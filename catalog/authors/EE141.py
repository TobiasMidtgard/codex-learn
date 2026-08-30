"""EE141 — Electricity and Magnetism.

A first-year course. It assumes school mathematics and EE111, the mathematics
course — complex numbers, derivatives, the exponential, and the first-order RC and
RL responses — and nothing else: no prior circuits beyond EE101, no field theory,
no vector calculus, no programming beyond arithmetic. Anything EE111 does not
supply is defined here where it first appears; the decibel is the one such term
and module 3 defines it.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number was produced by running the code, never assumed
"""

COURSE = {
    "id": "EE141",
    "title": "Electricity and Magnetism",
    "band": 1,
    "level": "Intermediate",
    "prereqs": ["EE111"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◎",
    "summary": (
        "Circuits treat a wire as a thing that carries current and a capacitor as a "
        "number in farads. This course asks where those numbers come from. It starts "
        "with the force between two charges, builds the electric field and the "
        "potential out of it, uses Gauss's law to get answers without integrating, "
        "and then does the same job on the magnetic side: Ampere's law, Faraday "
        "induction, and inductance read straight off a coil's dimensions. From there it "
        "takes both halves apart properly — what a conductor does to a field, what a "
        "resistance is made of, the sideways force that runs every motor, what an iron "
        "core buys and what it costs, and how two coils become a transformer — and "
        "ends where the halves join: the term missing from Ampere's law, Maxwell's four "
        "equations, and a wave that needs no charges at all."
    ),
    "outcomes": [
        "Compute the force and the field produced by a set of point charges, and say why superposition is allowed.",
        "Move between field, potential and energy, and use Gauss's law to get a field from symmetry alone.",
        "Work out a capacitance from the geometry of the conductors, and build an RC circuit with a specified time constant.",
        "Use Ampere's law and Faraday's law to explain what a coil does, and compute an inductance from its dimensions.",
        "Say what a conductor does to a field — screening, surface charge, the capacitance of a coaxial pair — and get a resistance out of a resistivity and a shape.",
        "Predict the path of a charge in a magnetic field and the torque on a current loop, and read a core, its gap and its saturation limit as a series of reluctances.",
        "Model a transformer as the ordinary components it behaves like, and state Maxwell's four equations, including why the displacement current had to be added and what speed and impedance follow from them.",
    ],
    "assessment": (
        "Ten quizzes that check the definitions landed, five circuits drawn and graded by "
        "measurement in the schematic editor, four guided derivations checked step by "
        "step, a filter design hit against two competing constraints, a numeric estimate, "
        "a fill-the-blanks on the transformer relations, seven short Python labs, and a "
        "capstone toolkit that designs a capacitor and a coil to a specification."
    ),
    "reading": [
        "*Electricity and Magnetism*, Purcell & Morin — chapters 1 to 3 for the electrostatics, 6 for the magnetic field.",
        "The MIT 8.02 course notes, freely available, for worked Gauss's law and Ampere's law examples.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Charge, force and the electric field",
            "summary": "Two charges push or pull. Divide that force by the charge you used to measure it and you have a field.",
            "concepts": [
                "Charge is a property of matter, measured in coulombs (C). It comes in two signs and is conserved.",
                "Coulomb's law: two point charges $q_1$ and $q_2$ a distance $r$ apart push each other apart with force $F = k q_1 q_2 / r^2$, where $k = 1/(4\\pi\\varepsilon_0) \\approx 8.99\\times10^9$ N m²/C². A negative product means they attract.",
                "The electric field $E$ at a point is the force a charge would feel there, divided by that charge: $E = F/q$. Its units are newtons per coulomb, which are the same thing as volts per metre.",
                "Superposition: the field of several charges is the vector sum of the fields each one would produce alone. Nothing interferes with anything.",
                "Field lines are curves you get by starting somewhere and always walking in the direction of the field. They start on positive charge and end on negative charge.",
            ],
            "read": [
                {
                    "title": "What charge is, and how hard two of them push",
                    "minutes": 12,
                    "body": r'''
Rub a balloon on a sleeve and it will hold itself flat against the ceiling. Nothing in
that is surprising until you count what is being held up: several grams of rubber, held
against the gravitational pull of the entire Earth, by a scuff. Whatever force did that
is not a weak one. It looks weak in ordinary life only because it is almost always
almost exactly cancelled, and electrostatics is the study of what goes on in the gap
left by *almost*.

## Charge is a property of matter, with one feature mass does not have

Mass comes in one sign. Everything attracts everything, there is no such thing as
negative mass, and no arrangement of matter can be made to pull on nothing.

Charge comes in two signs. Like signs push apart, unlike signs pull together, and — the
part with no gravitational analogue — an object carrying as much of one sign as of the
other exerts, from a distance, no force at all. Ordinary matter is exactly that
arrangement, which is why you can sit in a chair instead of being flung across the room
by the $10^{28}$ or so protons in it.

Three further facts are worth stating flatly, because everything after this rests on
them.

**Charge is conserved.** No process has ever been observed to change the net charge of
an isolated system. Rubbing the balloon manufactured nothing: it dragged electrons off
the sleeve, and the sleeve is left positive by precisely as much as the balloon is
negative.

**Charge is quantised.** Every isolated particle ever measured carries a whole multiple
of one elementary charge, $e = 1.602176634\times10^{-19}$ C. Since 2019 that value has
been exact by definition — the SI fixes $e$ and derives the ampere from it, rather than
the other way round. Quarks carry thirds of $e$, and have never been found on their own.

**Only the charge matters.** Two objects with the same charge feel the same electric
force in the same surroundings whether they are lead or hydrogen, hot or cold, large or
small. Nothing else about the object enters the law.

## A coulomb is an absurd amount of static charge

One coulomb is $1/e \approx 6.24\times10^{18}$ elementary charges. As an amount of
charge *flowing*, that is unremarkable — a torch bulb passes a coulomb through its
filament every couple of seconds. As an amount of charge *sitting still* on an object
it is preposterous. Two 1 C charges one metre apart would push each other apart with
about $9\times10^{9}$ N, which is the weight of nine hundred thousand tonnes. Real
static electricity deals in nanocoulombs and microcoulombs, and the second worked
example below shows why it could not be otherwise.

## Why the force should go as the inverse square

Coulomb measured the law in 1785 with a torsion balance: a light beam hung from a fine
fibre, a charged ball at each end, and the twist of the fibre read off as a force. It is
a beautiful experiment, and it is good to a few per cent — nowhere near good enough to
distinguish $r^{-2}$ from $r^{-2.01}$.

Two better arguments exist. The first is geometric. Whatever it is that reaches out from
a charge, suppose none of it is lost on the way. Then whatever crosses a sphere of
radius $r$ drawn around the charge also crosses a sphere of radius $2r$: the same total,
now shared over an area $4\pi r^2$ that has grown four times larger. The amount per unit
area therefore falls as $1/r^2$, for the same reason the brightness of a lamp does.
Module 2 turns that picture into Gauss's law and makes it exact. It is also why the
constant in the law is usually written $1/(4\pi\varepsilon_0)$ rather than as a single
letter: the $4\pi$ is the surface of the sphere, sitting in plain sight.

The second argument is an experiment that never measures a force at all. If the exponent
is exactly 2, the field everywhere inside a hollow charged conductor is exactly zero —
and if the exponent is not exactly 2, it is not zero. So instead of measuring a force to
a few per cent, put a detector inside a charged metal shell and look for nothing, which
can be done to extraordinary precision. Cavendish did it in 1773, Maxwell repeated it,
and modern versions pin the exponent to 2 within about $10^{-16}$. Module 5 explains why
the inside of a conductor is empty of field.

## The law itself

$$F = k\,\frac{q_1 q_2}{r^2}, \qquad
k = \frac{1}{4\pi\varepsilon_0} \approx 8.988\times10^{9}\ \mathrm{N\,m^2\,C^{-2}}$$

with $\varepsilon_0 = 8.854\times10^{-12}$ F/m, the permittivity of free space. Put the
charges in with their signs and the result carries its own meaning: a positive $F$ is a
repulsion along the line joining the two charges, a negative $F$ an attraction along
that same line. The force acts along that line and nowhere else.

Two features of the expression are easy to read straight past. The first is that it is
symmetric in $q_1$ and $q_2$, so the force on one is equal in size and opposite in
direction to the force on the other, whatever the two charges are: a 1 nC charge and a
1 µC charge a thousand times larger pull on each other exactly as hard. What differs is
what that force *does* to each, which depends on their masses and has nothing to do with
electricity. The second is that $r$ is the distance between them, in metres, squared.
Almost every wrong answer in this module comes from one of those two sentences.

## Worked: two small spheres

A sphere carrying $+2.0$ nC sits 3.0 cm from a sphere carrying $-5.0$ nC. Both are small
enough to treat as points. How hard do they pull on each other?

```text
q1 =  +2.0 nC = +2.0e-9 C
q2 =  -5.0 nC = -5.0e-9 C
r  =   3.0 cm =  0.030 m          r^2 = 9.0e-4 m^2

q1 * q2         = (2.0e-9) * (-5.0e-9)  = -1.0e-17 C^2
k * q1 * q2     = 8.988e9 * -1.0e-17    = -8.988e-8 N m^2
F = that / r^2  = -8.988e-8 / 9.0e-4    = -9.99e-5 N

                                        = 99.9 uN of attraction
```

A hundred micronewtons. If each sphere has a mass of a tenth of a gram, its weight is
$1.0\times10^{-4}\ \mathrm{kg} \times 9.81\ \mathrm{m/s^2} = 9.81\times10^{-4}$ N, so
the pull between them is about a tenth of that: obvious on a sensitive balance, nowhere
near enough to lift one sphere off the bench. Nanocoulombs at centimetre spacings live
in this range, and the scale is worth committing to memory, because it is the scale of
every electrostatics demonstration you will ever be shown.

## Worked: one electron in a billion

Now the other direction. Take two 1-gram spheres of copper a metre apart, and ask how
much charge is *present* inside them before any of it is unbalanced.

```text
copper: molar mass 63.55 g/mol, 29 protons per atom

atoms in 1 g       = 6.022e23 / 63.55         = 9.477e21
protons in 1 g     = 9.477e21 * 29            = 2.748e23
positive charge    = 2.748e23 * 1.602e-19 C   = 4.403e4 C    (44 kC)
```

Forty-four thousand coulombs in a gram of metal, matched to the last electron by an
equal negative charge, which is exactly why the sphere sits there doing nothing at all.
Now unbalance it by one part in a billion — strip one electron in $10^{9}$ off each
sphere:

```text
q = 4.403e4 C * 1e-9                 = 4.403e-5 C   (44 uC)

F = k q^2 / r^2
  = 8.988e9 * (4.403e-5)^2 / (1.0)^2
  = 8.988e9 * 1.939e-9                = 17.4 N
```

Seventeen newtons — the weight of a 1.8 kg object — between two gram-sized balls a metre
apart, from tampering with one electron in a billion. Each ball's own weight is
$9.8\times10^{-3}$ N, so the electric force is about 1800 times heavier than the thing
it acts on. That is what *almost* is doing in "almost exactly cancelled", and it is the
reason the world does not obviously look electrical: any imbalance big enough to notice
produces forces big enough to destroy the imbalance.

## The mistakes that actually get made

- **Leaving $r$ in centimetres.** The law is in SI and $r$ is squared, so 3 cm entered as
  3 gives an answer $10^4$ times too small. Convert first, every time.
- **Not squaring $r$.** The symptom is distinctive: the answer is too *large* by exactly
  the factor $r$, so it is out by a suspiciously round number.
- **Expecting the bigger charge to feel the bigger force.** Tempting, because the bigger
  charge visibly moves less — but that is its mass talking, not its charge.
- **Adding forces as numbers when there are more than two charges.** Coulomb's law gives
  one force per *pair*, and forces are vectors: three charges arranged in a triangle need
  components, not a total of magnitudes. The next reading unit deals with this at length.
- **Using the law on two spheres that are close together.** This one is a genuine physics
  error rather than an arithmetic one, and it is the first entry below.

## Where the law stops holding

**It is a law about point charges.** A sphere with its charge spread evenly over it acts,
from outside, exactly like a point charge at its centre — which is what licensed the two
worked examples above. But two *conductors* brought close together do not keep their
charge evenly spread. Each one's charge shifts in response to the other, positive drawn
towards a nearby negative, and the measured force is then larger than $kq_1q_2/r^2$
predicts. The rule of thumb is that the point-charge formula is safe when the separation
is several times the size of the objects. Module 5 is about what conductors do to
fields, and this is the first symptom of it.

**It is a law about charges in vacuum.** Immerse the same two charges in water and the
force falls by a factor of about 80, because the water molecules turn to screen them.
The repair is to replace $\varepsilon_0$ by $\varepsilon_r\varepsilon_0$, and module 3
does precisely that when it slides a dielectric between two capacitor plates.

**It is a law about charges at rest.** Two charges moving past one another exert forces
this expression does not give: there is a magnetic contribution as well (module 6), and
neither charge responds instantly to what the other is doing, because nothing does
(module 10). Coulomb's law is the static limit of something larger, and that larger
thing is where this course ends.

**It is a law about the electric force only.** Between two protons the electric
repulsion beats their gravitational attraction by a factor of $1.24\times10^{36}$, so
gravity is not what holds a nucleus together; the strong force is, and it takes over
below about $10^{-15}$ m. Above that scale, and outside the atom, Coulomb is what there
is.
''',
                },
                {
                    "title": "From a force to a field, and why fields simply add",
                    "minutes": 12,
                    "body": r'''
Coulomb's law describes a pair. Hand it two charges and it gives back the force between
them, and that is the whole of what it does. Ask what is going on at some empty point
near a single charge — no second charge there, nothing to feel a force — and the law has
nothing to say, because with one $q$ missing the expression is not about anything.

That is awkward for a practical reason as well as a philosophical one. Ten charges have
forty-five pairs. If the only thing you can compute is a pairwise force, then asking
what an eleventh charge would feel means starting the entire calculation again. Faraday's
move, which is the most useful single idea in this course, is to split the problem in
two: work out once what the source charges do *to the space*, and then ask separately
what any newcomer placed there would feel.

## The definition, and the division that makes it work

Put a small charge $q_0$ at the point of interest, measure the force $\mathbf{F}$ on it,
and divide:

$$\mathbf{E} = \frac{\mathbf{F}}{q_0}$$

The division is the whole idea. Double the test charge and the force on it doubles too,
so the ratio does not move — the number left over belongs to the point, not to the thing
you probed it with. Its units are newtons per coulomb.

Those units are also volts per metre, which is worth doing once rather than taking on
trust:

```text
1 N/C  =  1 N * m / (C * m)     multiply and divide by one metre
       =  1 J / (C * m)         a newton-metre is a joule
       =  1 V / m               a joule per coulomb is a volt
```

Both spellings are in use, sometimes in the same sentence. V/m is the practical one:
3 MV/m is the field at which dry air stops insulating, and it is quoted that way on
every datasheet you will ever read.

For a single point charge $Q$, put the test charge a distance $r$ away, apply Coulomb's
law, and divide $q_0$ back out:

$$E = \frac{1}{q_0}\cdot k\,\frac{Q q_0}{r^2} = k\,\frac{Q}{r^2}$$

pointing directly away from $Q$ if $Q$ is positive, and directly towards it if $Q$ is
negative. Notice what has disappeared: the field of a charge does not depend on there
being anything for it to push. It is what the charge does to its surroundings whether or
not anyone is there to check.

That sounds like bookkeeping, and in this module it is. It stops being bookkeeping in
module 10, where the field turns out to carry energy and momentum of its own and to
travel at a finite speed — at which point the field is unambiguously the thing that is
really there, and the force is what you get when something happens to be sitting in it.

## Why the fields simply add

Superposition is the claim that the field of several charges at a point is the vector
sum of what each charge alone would produce there:

$$\mathbf{E} = \mathbf{E}_1 + \mathbf{E}_2 + \cdots + \mathbf{E}_n$$

This reads like a triviality and is not. It says charge 1 makes the same contribution at
your point whether or not charge 2 is present: the two do not interfere, do not shield
one another, do not saturate the space between them. Plenty of physical influences fail
this test. Two loudspeakers driven hard produce distortion that neither produces alone;
iron in a magnetic field stops responding once it saturates, which module 8 has to
handle explicitly; light of two colours in the right crystal comes out as a third.
Superposition of the electric field in vacuum is a statement about the world, checked to
great precision, and formally it is the statement that the equations governing
$\mathbf{E}$ are linear.

What it buys is a method with no cleverness in it: one term per charge, resolved into
components, added.

## Worked: two charges on a line

Charges $q_1 = +4.0$ nC at the origin and $q_2 = +1.0$ nC at $x = 0.30$ m. What is the
field at $x = 0.10$ m, on the line between them?

Both are positive, so each pushes a positive test charge away from itself: the one at
the origin pushes it in $+x$, the one at 0.30 m pushes it in $-x$. Everything is
collinear, so the vector sum is a subtraction, and the only real work is keeping the two
distances straight.

```text
from q1:  r = 0.10 - 0     = 0.10 m        r^2 = 1.0e-2
          E1 = k q1 / r^2  = 8.988e9 * 4.0e-9 / 1.0e-2
                           = 35.95 / 1.0e-2       = 3595 V/m   (+x)

from q2:  r = 0.30 - 0.10  = 0.20 m        r^2 = 4.0e-2
          E2 = k q2 / r^2  = 8.988e9 * 1.0e-9 / 4.0e-2
                           = 8.988 / 4.0e-2       =  225 V/m   (-x)

net:      E = 3595 - 225                          = 3370 V/m, in +x
```

The nearer, larger charge dominates, and $1/r^2$ is unforgiving about it. Now move the
point to $x = 0.20$ m and run the same two lines again:

```text
from q1:  r = 0.20 m,   E1 = 35.95 / 4.0e-2   = 898.8 V/m   (+x)
from q2:  r = 0.10 m,   E2 =  8.988 / 1.0e-2  = 898.8 V/m   (-x)

net:      E = 0
```

There is a point between two like charges where the field is exactly zero, and it is not
the midpoint. It sits nearer the *smaller* charge, which needs the help of a shorter
distance to match its neighbour. Here the distances are 0.20 m and 0.10 m, in the ratio
$2:1$ — the square root of the charge ratio $4:1$. The guided derivation later in this
module works that out in general, and one of the numeric units makes you find such a
point from scratch.

## Worked: two charges not on a line

Two charges of $+5.0$ nC sit at $(0,\ +4.0\ \mathrm{cm})$ and $(0,\ -4.0\ \mathrm{cm})$.
What is the field at $(3.0\ \mathrm{cm},\ 0)$?

Now the two contributions point in different directions and the components have to be
taken seriously. The geometry is a 3–4–5 triangle, so the distances come out exactly:

```text
r = sqrt(0.030^2 + 0.040^2) = 0.050 m          r^2 = 2.5e-3 m^2

magnitude of each contribution:
   E = k Q / r^2 = 8.988e9 * 5.0e-9 / 2.5e-3
                 = 44.94 / 2.5e-3               = 17 976 V/m

direction cosines, off the same triangle:
   along x:  0.030 / 0.050 = 0.60
   along y:  0.040 / 0.050 = 0.80

upper charge:   Ex = +0.60 * 17 976 = +10 786    Ey = -0.80 * 17 976 = -14 381
lower charge:   Ex = +0.60 * 17 976 = +10 786    Ey = +0.80 * 17 976 = +14 381
                     -----------------------          ----------------------
                Ex = 21 571 V/m                  Ey = 0
```

So $2.16\times10^{4}$ V/m, pointing straight along $+x$. The $y$ components had to
cancel: the point sits on the perpendicular bisector of the two charges, and nothing in
the arrangement distinguishes up from down. Spotting that before doing any arithmetic
halves the work, and in module 2 the same habit — look for the symmetry first — is what
makes Gauss's law usable at all.

**Here is the mistake.** Adding the two magnitudes gives $2 \times 17\,976 = 35\,952$
V/m, which is 67 % too large. It is tempting because "superposition means the fields add"
is a true sentence, and because in the collinear example above the arithmetic really was
a plain subtraction of numbers. Fields add *as vectors*. The moment the contributions
stop being parallel, the sum is smaller than the total of the parts, and the factor 0.60
above is exactly where the difference went.

## Field lines, and what they are allowed to do

A field line is drawn by starting anywhere and repeatedly stepping in the direction of
the local field. The picture that results has three readable properties.

- **Direction.** The tangent at any point is the direction of $\mathbf{E}$ there, which
  is the direction a positive charge released there would initially accelerate. It is
  *not* the path the charge then follows: release a charge in a curved field and it
  picks up momentum, and momentum carries it across the lines.
- **Density.** Lines are drawn so that where they crowd together the field is strong.
  That is not a convention imposed by hand — it falls out of the same
  spreading-over-a-sphere argument that gave the inverse square, and module 2 makes it
  quantitative.
- **Ends.** Lines begin on positive charge and end on negative charge, and nowhere else.
  A line that appears to stop in empty space means the drawing ran out of room, not that
  the field ran out.

Two field lines can never cross, for a reason that is definitional rather than physical:
at the crossing point the field would need two directions at once, and it has one. The
single apparent exception is a point where the field is exactly zero — the null point
computed above — because there is no direction there at all, and several lines can run
into it. The sandbox in this module lets you watch that happen and then watch it stop
happening when you change the sign of the charge.

## Where the field picture stops

**The test charge has to be small.** Put a large charge at your point of interest and it
shoves the source charges around, so what you measure is the field of a different
arrangement from the one you meant. On a conductor the effect is dramatic, because the
sources are free to move. The definition should strictly read as a limit,
$\mathbf{E} = \lim_{q_0\to 0}\mathbf{F}/q_0$, with the awkwardness that charge is
quantised, so the limit cannot literally be taken.

**$E = kQ/r^2$ blows up at $r = 0$.** For a real object that never bites, because the
charge is spread over a surface and you cannot reach $r = 0$. For a genuine point
particle it is an unsolved problem in classical physics, and one of the clearer signs
that the classical picture is incomplete.

**Fields in matter superpose only while the matter behaves linearly.** In air above
about 3 MV/m the field tears electrons off molecules and the air conducts: a spark. That
number is a real design limit, not a curiosity. A 1 cm metal ball cannot hold more than
about 33 nC in open air — at that charge its surface field is
$kQ/R^2 = 8.988\times10^{9} \times 3.34\times10^{-8} / 10^{-4} = 3\times10^{6}$ V/m —
before the charge starts leaking away into the air. That is the practical reason
electrostatics deals in nanocoulombs. Module 8 meets the same kind of limit on the
magnetic side, where iron saturates and superposition fails outright.

**Everything here is static.** A field that does not change in time can be written as
the slope of a potential, which is what module 2 is about, and that fact is what makes
the entire apparatus of voltages work. Once the fields change, the electric field
acquires a circulating part that is not the slope of anything — Faraday induction,
module 4 — and the tidy picture of lines beginning and ending on charges is no longer
the whole story. Module 10 puts the two halves together.
''',
                },
            ],
            "sandbox": {
                "title": "Reading a field off its arrows",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": 1, "a12": 0, "a21": 0, "a22": 1},
                "brief": r'''
The panel draws a two-dimensional vector field. Read the axes as the two coordinates
of a flat region of space, the short strokes as the direction of the electric field
at each of those points, and the coloured curves as field lines: each one starts on
the rim and then follows the arrows wherever they lead.

The four sliders set how the field depends on position. That is a restriction — a
real point charge makes a field that falls off as $1/r^2$, which no slider here can
produce — but it is not a cheat. Inside a ball of uniformly spread charge the field
really does grow in direct proportion to the distance from the centre, which is
exactly what these sliders describe. The opening values, $a_{11} = a_{22} = 1$ with
the other two zero, are that case: the field at every point points straight away from
the black dot, and gets stronger the further out you go.
''',
                "notice": [
                    "As it opens, every stroke points away from the black dot and all eight curves run straight outwards. That is positive charge spread through the region: field lines begin here.",
                    "Set $a_{11}$ and $a_{22}$ both to $-1$. Every arrow reverses and the curves now run inwards to the dot. Nothing about the geometry changed — only the sign of the charge.",
                    "Set $a_{11} = 1$ and $a_{22} = -1$, leaving $a_{12}$ and $a_{21}$ at zero. Four of the eight curves sweep in from above and below, turn, and leave along the horizontal axis without going near the dot; two more, launched on the horizontal axis itself, simply run outwards. The last two are launched exactly on the vertical axis, and they run into the dot and stop — not because there is charge there, but because that one point is where the field is exactly zero and there is no direction left to follow. Everywhere else nothing begins or ends. This is what an electric field looks like where there is no charge, and module 2 turns that observation into Gauss's law.",
                    "Set $a_{11} = a_{22} = 0$, $a_{12} = 1$, $a_{21} = -1$. Every curve now wraps round the dot instead of running into it or out of it, and the readout calls the pattern a *centre*. (The drawn rings creep outward by about a tenth of their radius over the interval sketched; that is the forward-Euler step in the drawing code, not the field.) No electrostatic field can circulate like that. A magnetic field always does, and module 4 is about why.",
                ],
            },
            "derive": {
                "title": "Where the field of two like charges vanishes",
                "minutes": 12,
                "vars": ["Q", "q", "d", "x", "k"],
                "brief": r'''
A charge $Q$ sits at the origin and a charge $q$ sits at $x = d$. Both are positive.
Somewhere on the line between them the two contributions point in opposite directions
with equal magnitude, and the field is exactly zero.

The reading unit found that point for one particular pair of numbers by trying it. Here
you get it in general, and the answer is worth having: it says immediately which side of
the midpoint the null point falls on, and by how much.

Work with the Coulomb constant $k$ throughout. It cancels at the first opportunity, and
watching it go is half the point.
''',
                "steps": [
                    {
                        "prompt": "Take a point on the line between the charges, a distance $x$ from the origin. Write the magnitude of the field there due to $Q$ alone.",
                        "answer": "\\frac{k Q}{x^2}",
                        "hint": "The field of a point charge is $kQ/r^2$, and here the distance from $Q$ to your point is simply $x$.",
                        "deconstruct": [
                            "A point charge $Q$ makes a field of magnitude $kQ/r^2$ at distance $r$.",
                            "$Q$ is at the origin and the point is at $x$, so $r = x$.",
                        ],
                    },
                    {
                        "prompt": "Now the other one. Write the magnitude of the field at the same point due to $q$ alone.",
                        "answer": "\\frac{k q}{(d - x)^2}",
                        "placeholder": "k q over a squared distance",
                        "hint": "Same formula, different distance. The charge $q$ is at $x = d$ and the point is at $x$, so how far apart are they?",
                        "deconstruct": [
                            "The distance from $q$ to the point is $d - x$, which is positive because the point lies between the two charges.",
                            "Square it and put it under $kq$.",
                        ],
                    },
                    {
                        "prompt": "Between two positive charges the two contributions point in opposite directions, so the net field is zero where the magnitudes are equal. Set them equal and write the ratio $(d-x)^2 / x^2$.",
                        "answer": "\\frac{q}{Q}",
                        "hint": "Cross-multiply $kQ/x^2 = kq/(d-x)^2$. The $k$ goes first, and then collect the two distances on one side.",
                        "deconstruct": [
                            "$kQ/x^2 = kq/(d-x)^2$, and $k$ divides out of both sides at once.",
                            "Cross-multiplying gives $Q(d-x)^2 = q x^2$.",
                            "Divide both sides by $Q x^2$.",
                        ],
                    },
                    {
                        "prompt": "Take the positive square root of both sides and solve for $x$.",
                        "answer": "\\frac{d}{1 + \\sqrt{q/Q}}",
                        "placeholder": "d divided by something",
                        "hint": "The square root gives $(d-x)/x = \\sqrt{q/Q}$. Split the left side into $d/x - 1$ and the rest is one line.",
                        "deconstruct": [
                            "$(d-x)/x = \\sqrt{q/Q}$, taking the positive root because both distances are positive.",
                            "The left side is $d/x - 1$, so $d/x = 1 + \\sqrt{q/Q}$.",
                            "Invert and multiply through by $d$.",
                        ],
                    },
                    {
                        "prompt": "Check it on a case you can see. Put $Q = 9q$ into your expression: where is the null point?",
                        "answer": "\\frac{3 d}{4}",
                        "placeholder": "a fraction of d",
                        "hint": "$\\sqrt{q/Q} = \\sqrt{1/9} = 1/3$, so the denominator is $4/3$.",
                        "deconstruct": [
                            "With $Q = 9q$, the ratio $q/Q$ is $1/9$ and its square root is $1/3$.",
                            "$x = d/(1 + 1/3) = d/(4/3)$.",
                        ],
                    },
                ],
                "closing": r'''
$$x = \frac{d}{1 + \sqrt{q/Q}}$$

Read it as a ratio: the two distances $x$ and $d - x$ are in the ratio $\sqrt{Q}
: \sqrt{q}$. The null point is always nearer the *smaller* charge, and it moves as the
square root of the charge ratio, so it moves slowly — making $Q$ nine times $q$ shifts
the null point only from the midpoint out to three quarters of the way across.

Two things the algebra also tells you, both worth checking against the expression:

* Equal charges give $\sqrt{q/Q} = 1$ and $x = d/2$, the midpoint, which symmetry
  demanded before any of this was written down.
* Nothing here works for charges of *opposite* sign. Between $+Q$ and $-q$ both
  contributions point the same way — away from the positive one and towards the negative
  one — so they add everywhere in between and there is no null point there at all. Set
  the magnitudes equal anyway and the algebra hands you a solution outside the pair,
  beyond the smaller charge, which is where the null point genuinely is. And if the two
  are exactly equal and opposite, that solution runs off to infinity: a dipole has no
  point of zero field anywhere on its axis.
''',
            },
            "blanks": {
                "title": "Coulomb's law and the field, term by term",
                "minutes": 8,
                "caption": "the two laws of this module, with the load-bearing parts removed",
                "lang": "text",
                "brief": r'''
Nothing here is executed. These are the two expressions the rest of the module is built
on, and the holes are in the places where a slip changes the answer rather than the
spelling — the power on the distance, what the force is divided by, and how several
contributions combine.

If a choice looks obviously right, say why out loud before taking it. Two of these have
a distractor that is dimensionally sensible and still wrong.
''',
                "listing": """# Two point charges, q1 and q2, sitting r metres apart in vacuum.

F = k * q1 * q2 / ___             # Coulomb's law: the force each one feels

k = 1 / (4 * pi * ___)            # = 8.988e9 N m^2 / C^2

# The field is the force per unit charge on a small test charge q0 placed there.

E = F / ___                       # units of E: N/C, which is also ___

E_from_one_source = k * Q / ___   # the field a single charge Q makes, r away

# and with several source charges acting at the same point:

E_total = ___
""",
                "blanks": [
                    {
                        "prompt": "What sits under the product of the charges?",
                        "hole": "?",
                        "opts": ["r**2", "r", "r**3", "2*r"],
                        "a": 0,
                        "why": "The force falls as the *square* of the separation, so doubling the distance quarters the force. The picture behind the square is that whatever leaves the charge is shared over a sphere of area $4\\pi r^2$, and that area grows as $r^2$.",
                        "whys": [
                            "The force falls as the *square* of the separation, so doubling the distance quarters the force. The picture behind the square is that whatever leaves the charge is shared over a sphere of area $4\\pi r^2$, and that area grows as $r^2$.",
                            "A plain $r$ would make the force fall off far too slowly — halving at twice the distance instead of quartering. It is also the shape of the field around a long straight current-carrying wire, which is where the temptation comes from.",
                            "A cube is the falloff of a *dipole* field, where two opposite charges nearly cancel and what survives dies faster than either one alone. A single pair of charges is not a dipole.",
                            "Doubling $r$ is not the same as squaring it, and this choice would make the force fall off linearly with an extra factor of two attached — dimensionally wrong as well as physically wrong.",
                        ],
                    },
                    {
                        "prompt": "Which constant makes $k$ come out at $8.988\\times10^{9}$?",
                        "hole": "?",
                        "opts": ["epsilon_0", "mu_0", "c", "e"],
                        "a": 0,
                        "why": "$\\varepsilon_0 = 8.854\\times10^{-12}$ F/m, the permittivity of free space. Run it through: $4\\pi \\times 8.854\\times10^{-12} = 1.113\\times10^{-10}$, and one over that is $8.988\\times10^{9}$.",
                        "whys": [
                            "$\\varepsilon_0 = 8.854\\times10^{-12}$ F/m, the permittivity of free space. Run it through: $4\\pi \\times 8.854\\times10^{-12} = 1.113\\times10^{-10}$, and one over that is $8.988\\times10^{9}$.",
                            "$\\mu_0$ is the magnetic partner of this constant and belongs to module 4 onwards. The two do meet — their product fixes the speed of light — but $\\mu_0$ never appears in an electrostatic force.",
                            "The speed of light is not a constant of electrostatics, though module 10 shows it is built out of $\\varepsilon_0$ and $\\mu_0$ together. A speed under a $4\\pi$ would not even give the right units.",
                            "The elementary charge is the size of the charge on one electron, not a property of the space between charges. It is already accounted for in the values of $q_1$ and $q_2$.",
                        ],
                    },
                    {
                        "prompt": "The force is divided by what to give the field?",
                        "hole": "?",
                        "opts": ["q0", "Q", "r", "q0**2"],
                        "a": 0,
                        "why": "By the test charge, $q_0$ — the one you put there to do the measuring, not the source. That division is the entire idea: the force doubles when $q_0$ doubles, so the ratio is a property of the point rather than of the probe.",
                        "whys": [
                            "By the test charge, $q_0$ — the one you put there to do the measuring, not the source. That division is the entire idea: the force doubles when $q_0$ doubles, so the ratio is a property of the point rather than of the probe.",
                            "Dividing by the source charge would remove the very thing that is producing the field, and would leave a quantity that is the same near a big charge as near a small one.",
                            "Dividing a force by a distance gives a quantity in newtons per metre, which is a spring constant, not a field.",
                            "Squaring the test charge would break the cancellation: the force is proportional to $q_0$ to the first power, so only the first power divides out and the result would still depend on the probe.",
                        ],
                    },
                    {
                        "prompt": "N/C is the same unit as what?",
                        "hole": "?",
                        "opts": ["V/m", "J/C", "V*m", "N*m"],
                        "a": 0,
                        "why": "Multiply and divide by a metre: $\\mathrm{N/C} = \\mathrm{N\\,m/(C\\,m)} = \\mathrm{J/(C\\,m)} = \\mathrm{V/m}$. Both names are in use, and V/m is the one on datasheets — air breaks down at about 3 MV/m.",
                        "whys": [
                            "Multiply and divide by a metre: $\\mathrm{N/C} = \\mathrm{N\\,m/(C\\,m)} = \\mathrm{J/(C\\,m)} = \\mathrm{V/m}$. Both names are in use, and V/m is the one on datasheets — air breaks down at about 3 MV/m.",
                            "A joule per coulomb is one volt, which is a potential, not a field. This is the near miss to watch for: the field is a volt per *metre*, and the missing metre is exactly the difference between module 1 and module 2.",
                            "A volt-metre is the unit of electric flux, which arrives with Gauss's law in the next module. It is a field multiplied by an area divided by a length, not a field.",
                            "A newton-metre is a joule, an energy. It is what you get by multiplying a force by a distance rather than dividing a force by a charge.",
                        ],
                    },
                    {
                        "prompt": "And the field of one point charge, a distance r away?",
                        "hole": "?",
                        "opts": ["r**2", "4*pi*r**2", "r", "r**3"],
                        "a": 0,
                        "why": "The field inherits the inverse square from the force, because dividing by $q_0$ touches only the charges: $E = F/q_0 = kQ/r^2$.",
                        "whys": [
                            "The field inherits the inverse square from the force, because dividing by $q_0$ touches only the charges: $E = F/q_0 = kQ/r^2$.",
                            "The area of the sphere is already hidden inside $k = 1/(4\\pi\\varepsilon_0)$; putting it in again would divide the field by $4\\pi$ a second time. Write it as $Q/(4\\pi\\varepsilon_0 r^2)$ and the $4\\pi$ appears exactly once.",
                            "A first power would be the field of an infinite line of charge, not a point. A point's field must fall faster, because its influence spreads over a growing sphere rather than a growing cylinder.",
                            "A cube belongs to a dipole, where two nearby opposite charges very nearly cancel and what is left over dies away faster than either would alone.",
                        ],
                    },
                    {
                        "prompt": "Several charges, one point. What is the total field?",
                        "hole": "?",
                        "opts": [
                            "the vector sum E1 + E2 + ... + En",
                            "the sum of the magnitudes |E1| + |E2| + ... + |En|",
                            "the average of E1 ... En",
                            "whichever of E1 ... En is largest",
                        ],
                        "a": 0,
                        "why": "Superposition, and the word *vector* is the load-bearing one. Two contributions of 18.0 kV/m, each lying 53° away from their resultant, total 21.6 kV/m, not 36.0 kV/m: the components across the resultant cancel. Only when every contribution is parallel does the vector sum become a sum of numbers.",
                        "whys": [
                            "Superposition, and the word *vector* is the load-bearing one. Two contributions of 18.0 kV/m, each lying 53° away from their resultant, total 21.6 kV/m, not 36.0 kV/m: the components across the resultant cancel. Only when every contribution is parallel does the vector sum become a sum of numbers.",
                            "This is the single most common error in the module. It is right only in the special case where every contribution points the same way, and it can be wildly wrong otherwise — at the midpoint between two equal charges it predicts twice one charge's field where the true answer is zero.",
                            "Averaging would make the field of two identical charges the same as the field of one, so bringing a second charge up to join the first would change nothing at all. Adding charge has to add field.",
                            "Taking the largest would mean a distant second charge contributed nothing until it overtook the first, and the field would jump discontinuously at the crossover. Every contribution counts, all the time.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "Two spheres, one force",
                    "minutes": 5,
                    "brief": r'''
The mechanical case: one rule, one unknown, both charges given. The only thing this can
catch you on is the unit on the separation, which is why it is written in centimetres.
''',
                    "prompt": "How hard do the two spheres push each other apart?",
                    "note": "Give the answer in micronewtons, to one decimal place.",
                    "figure": r'''
```text
   two small charged spheres, held 4.0 cm apart on insulating stalks

       q1 = +3.0 nC                            q2 = +5.0 nC
            ( + ) <--------- 4.0 cm ---------> ( + )

   both small enough to count as points; nothing else is anywhere near
```
''',
                    "given": [
                        {"label": "First charge", "value": "+3.0 nC"},
                        {"label": "Second charge", "value": "+5.0 nC"},
                        {"label": "Separation", "value": "4.0 cm"},
                        {"label": "Coulomb constant", "value": "8.988 × 10⁹ N m² C⁻²"},
                    ],
                    "aside": "Put the separation into metres before squaring it. 4.0 cm is 0.040 m, and "
                             "$0.040^2 = 1.6\\times10^{-3}$ m².",
                    "answer": 84.3,
                    "tol": 0.5,
                    "unit": "µN",
                    "hint": "$F = kq_1q_2/r^2$. Multiply the two charges first — the product is "
                            "$1.5\\times10^{-17}$ C² — then multiply by $k$ and divide by $r^2$.",
                    "wrong": "If you got 3.37, the separation was not squared: $8.988\\times10^{9} \\times "
                             "1.5\\times10^{-17}/0.040$ is a division by a length, not by an area. If you "
                             "got 0.0084, the 4.0 went in as centimetres, and the factor $100^2$ between "
                             "them is why $r$ always goes into the formula in metres.",
                    "why": r'''
$q_1q_2 = 3.0\times10^{-9} \times 5.0\times10^{-9} = 1.5\times10^{-17}$ C², and
$k q_1 q_2 = 8.988\times10^{9} \times 1.5\times10^{-17} = 1.348\times10^{-7}$ N m².
Dividing by $r^2 = (0.040)^2 = 1.6\times10^{-3}$ m² gives
$F = 8.43\times10^{-5}$ N, which is 84.3 µN.

Both charges are positive, so the force is a repulsion along the line joining them, and
each sphere feels the same 84.3 µN — the 5.0 nC sphere no more than the 3.0 nC one.
Eighty micronewtons is roughly the weight of a large grain of sand, and it is a fair
sample of the scale of everything in this module: nanocoulombs at centimetre spacings
produce forces you need a sensitive balance to see.
''',
                },
                {
                    "title": "How far out is the field down to 500 V/m?",
                    "minutes": 6,
                    "brief": r'''
The same rule, run backwards, and asking for a distance rather than a force. The
distance is inside a square, so getting it out means taking a root — and that is where
the arithmetic goes wrong if it goes wrong at all.
''',
                    "prompt": "At what distance from the charge is the field 500 V/m?",
                    "note": "Give the answer in centimetres, to one decimal place.",
                    "figure": r'''
```text
   an isolated charged sphere in still, dry air, far from anything else

              ( +12.0 nC )  . . . . . . . . . . . .>  E = 500 V/m
                            |<-------- r = ? ------>|

   the sphere is small enough to treat as a point charge
```
''',
                    "given": [
                        {"label": "Charge on the sphere", "value": "+12.0 nC"},
                        {"label": "Field wanted", "value": "500 V/m"},
                        {"label": "Coulomb constant", "value": "8.988 × 10⁹ N m² C⁻²"},
                    ],
                    "aside": "Rearranging $E = kQ/r^2$ for $r$ gives $r = \\sqrt{kQ/E}$. Do the division "
                             "first, look at the units of what you have, and only then take the root.",
                    "answer": 46.4,
                    "tol": 0.4,
                    "unit": "cm",
                    "hint": "$kQ = 8.988\\times10^{9} \\times 12.0\\times10^{-9} = 107.9$ N m² C⁻¹. Divide "
                            "that by 500 V/m and you have $r^2$ in square metres.",
                    "wrong": "If you got 21.6 cm, the division was done and the square root was not: "
                             "$107.9/500 = 0.2157$, and that number is $r^2$ in m², not $r$ in m. The "
                             "give-away is the unit — square metres cannot be a distance.",
                    "why": r'''
$E = kQ/r^2$, so $r^2 = kQ/E$. Then
$kQ = 8.988\times10^{9} \times 12.0\times10^{-9} = 107.9$ N m² C⁻¹, and
$r^2 = 107.9/500 = 0.2157$ m². Taking the root, $r = 0.4644$ m, which is 46.4 cm.

Two things are worth noticing about that answer. The field of a fairly ordinary static
charge is still 500 V/m half a metre away — the inverse square falls off fast, but it
never stops, and there is no distance at which the field of a point charge is genuinely
zero. And the same 12 nC on a 1 cm sphere puts about 1.1 MV/m at its own surface, which
is within a factor of three of the field that makes air conduct. Between those two
numbers lies the whole practical difficulty of electrostatics: the field near the charge
is nearly unmanageable and the field a little way off is nearly undetectable.
''',
                },
                {
                    "title": "The point where the field is exactly zero",
                    "minutes": 8,
                    "brief": r'''
Two positive charges, and a question that asks for neither a force nor a field but a
*position*. Between two like charges the two contributions point in opposite directions,
so somewhere they must be equal in size — and that place is not the midpoint unless the
charges are equal.

Set the two magnitudes equal and solve. The Coulomb constant cancels before you need its
value, which is a good sign that you have set it up correctly.
''',
                    "prompt": "How far from the 9.0 nC charge is the point on the line between them where the total field is zero?",
                    "note": "Give the answer in centimetres from the 9.0 nC charge, to one decimal place.",
                    "figure": r'''
```text
   two positive point charges on a line, 50.0 cm apart

     +9.0 nC                    P                        +4.0 nC
       ( + )....................(?).......................( + )
       |<------- x = ? ------->|                            |
       |<---------------- 50.0 cm ------------------------->|

   P is the point where the two fields cancel exactly
```
''',
                    "given": [
                        {"label": "Left-hand charge", "value": "+9.0 nC"},
                        {"label": "Right-hand charge", "value": "+4.0 nC"},
                        {"label": "Separation", "value": "50.0 cm"},
                    ],
                    "aside": "At a point $x$ from the left charge, the distance to the right charge is "
                             "$0.500 - x$. Setting $kQ/x^2 = kq/(0.500-x)^2$ removes $k$ immediately, and "
                             "square-rooting both sides removes the squares.",
                    "answer": 30.0,
                    "tol": 0.3,
                    "unit": "cm",
                    "hint": "After cancelling $k$ and taking the square root, $(0.500 - x)/x = "
                            "\\sqrt{4/9} = 2/3$. That is a linear equation in $x$.",
                    "wrong": "If you got 25.0, that is the midpoint, which would only be right if the two "
                             "charges were equal. If you got 20.0, the distances are in the right ratio but "
                             "measured from the wrong end — check which side the null point has to be on by "
                             "asking which charge needs the help of a shorter distance.",
                    "why": r'''
Let $x$ be the distance from the 9.0 nC charge. The magnitudes are equal when

$$\frac{k(9.0\ \mathrm{nC})}{x^2} = \frac{k(4.0\ \mathrm{nC})}{(0.500 - x)^2}$$

The $k$ cancels and so does the common factor of $10^{-9}$, leaving
$9/x^2 = 4/(0.500-x)^2$. Taking the positive square root of both sides,
$3/x = 2/(0.500 - x)$, so $3(0.500 - x) = 2x$, so $1.500 = 5x$ and $x = 0.300$ m —
30.0 cm from the 9.0 nC charge, and 20.0 cm from the 4.0 nC one.

Check it: $E_9 = 8.988\times10^{9} \times 9.0\times10^{-9}/0.300^2 = 80.9/0.0900 =
899$ V/m, and $E_4 = 8.988\times10^{9} \times 4.0\times10^{-9}/0.200^2 = 35.95/0.0400 =
899$ V/m. They cancel.

The null point sits nearer the *smaller* charge, which is the part worth taking away:
the weaker source needs a shorter distance to make up the difference. The distances end
up in the ratio $3:2$, which is $\sqrt{9}:\sqrt{4}$ — a square root, so the null point
moves lazily. You would have to make one charge a hundred times the other to push it
nine tenths of the way across.
''',
                },
                {
                    "title": "A third charge, pulled two ways at once",
                    "minutes": 10,
                    "brief": r'''
Two source charges that are not on a line with the point of interest, so the two
contributions have to be added as vectors. They have been arranged at right angles to
each other to keep the geometry honest without making it fiddly: once you have the two
magnitudes, Pythagoras finishes the job.

The quantity asked for is a force on a charge that is itself negative, which changes the
direction of the answer but not its size.
''',
                    "prompt": "What is the magnitude of the net electric force on the −2.0 nC charge at the origin?",
                    "note": "Give the answer in micronewtons, to the nearest micronewton.",
                    "figure": r'''
```text
                      y (cm)
                        |
                   +4 --+  ( + ) q2 = +12.0 nC
                        |
                        |
   -----+---------------O---------------+-----> x (cm)
       -3               |
      ( + )             |
   q1 = +12.0 nC        O = the origin, where q3 = -2.0 nC sits

   q1 at (-3.0 cm, 0)      q2 at (0, +4.0 cm)      q3 at (0, 0)
```
''',
                    "given": [
                        {"label": "q1, at (−3.0 cm, 0)", "value": "+12.0 nC"},
                        {"label": "q2, at (0, +4.0 cm)", "value": "+12.0 nC"},
                        {"label": "q3, at the origin", "value": "−2.0 nC"},
                        {"label": "Coulomb constant", "value": "8.988 × 10⁹ N m² C⁻²"},
                    ],
                    "aside": "Find the field the two source charges make at the origin first, then multiply "
                             "by 2.0 nC at the very end. The two contributions are at right angles, so their "
                             "magnitudes combine as $\\sqrt{E_1^2 + E_2^2}$.",
                    "answer": 275.0,
                    "tol": 2.0,
                    "unit": "µN",
                    "hint": "$kq = 8.988\\times10^{9} \\times 12.0\\times10^{-9} = 107.9$. Divide by "
                            "$0.030^2$ for one contribution and by $0.040^2$ for the other, then combine "
                            "them with Pythagoras before multiplying by the 2.0 nC.",
                    "wrong": "If you got 374, the two contributions were added as numbers instead of as "
                             "vectors — that is the answer you would get if both pointed the same way, and "
                             "they are 90° apart. If you got 240, only the nearer charge was counted.",
                    "why": r'''
Work in fields first. Each source carries 12.0 nC, so $kq = 8.988\times10^{9} \times
12.0\times10^{-9} = 107.9$ N m² C⁻¹ for both.

```text
q1 is 0.030 m away:  E1 = 107.9 / 0.030^2 = 107.9 / 9.0e-4  = 1.198e5 V/m
q2 is 0.040 m away:  E2 = 107.9 / 0.040^2 = 107.9 / 1.6e-3  = 6.741e4 V/m
```

Both sources are positive, so both fields at the origin point *away* from their source:
$E_1$ along $+x$ and $E_2$ along $-y$. They are perpendicular, so

$$|\mathbf{E}| = \sqrt{(1.198\times10^{5})^2 + (6.741\times10^{4})^2}
= \sqrt{1.890\times10^{10}} = 1.375\times10^{5}\ \mathrm{V/m}$$

at $\arctan(6.741/11.98) = 29.4°$ below the $+x$ axis. The force on the third
charge is $F = |q_3| |\mathbf{E}| = 2.0\times10^{-9} \times 1.375\times10^{5} =
2.75\times10^{-4}$ N, which is **275 µN**.

Two remarks. The sign of $q_3$ does not change the size of that force, only its
direction: being negative, it is pulled *along* $-x$ and $+y$, back towards the two
positive charges, rather than pushed away. And notice that the two magnitudes add to
$1.872\times10^{5}$ V/m, which would give 374 µN. That is the answer to a different
question — the one where both fields point the same way — and it is 36 % too big here.
The right angle is doing real work.
''',
                },
                {
                    "title": "Two hanging spheres, and the charge that holds them apart",
                    "minutes": 12,
                    "brief": r'''
The hardest of these, and the one that looks least like the others: no charge is given,
no field is given, and the only measurement is a distance you could take with a ruler.
The source of the number is mechanical — a pair of threads that have found their
equilibrium — and the electrostatics is what you extract from it.

This is how Coulomb's own experiment worked and how a charge is still measured with
nothing but a balance, so it is worth working slowly. Resolve the forces on one sphere,
get the electric force out of the geometry, then use Coulomb's law backwards.
''',
                    "prompt": "What is the charge on each sphere?",
                    "note": "Give the answer in nanocoulombs, to one decimal place. Take g = 9.81 m/s².",
                    "figure": r'''
```text
                        o  <- both threads tied to the same point
                       / \
                      /   \      each thread 25.0 cm long
                     /     \
                    /       \
                   /         \
                 (q)         (q)   two identical spheres,
                  |<- 6.0 cm ->|   0.80 g each, equally charged

   they hang still, pushed apart by their own repulsion
   and pulled together by the threads
```
''',
                    "given": [
                        {"label": "Mass of each sphere", "value": "0.80 g"},
                        {"label": "Length of each thread", "value": "25.0 cm"},
                        {"label": "Separation at rest", "value": "6.0 cm"},
                        {"label": "Gravity", "value": "9.81 m/s²"},
                    ],
                    "aside": "One sphere feels three forces: its weight straight down, the thread tension "
                             "along the thread, and the Coulomb repulsion horizontally. Resolving vertically "
                             "and horizontally and dividing one by the other kills the tension and leaves "
                             "$F_e = mg\\tan\\theta$, where $\\theta$ is the angle of the thread from the "
                             "vertical.",
                    "answer": 19.5,
                    "tol": 0.2,
                    "unit": "nC",
                    "hint": "Each sphere hangs 3.0 cm sideways on a 25.0 cm thread, so $\\sin\\theta = "
                            "3.0/25.0 = 0.12$. Get $\\tan\\theta$ from that, then $F_e = mg\\tan\\theta$, "
                            "then $q = \\sqrt{F_e r^2/k}$ with $r$ the full 6.0 cm.",
                    "wrong": "If you got 27.9, the half-separation was used where the full one belongs: the "
                             "geometry uses 3.0 cm (each sphere's sideways displacement) but Coulomb's law "
                             "uses 6.0 cm (the distance between the two charges). If you got 81, the thread "
                             "length went into Coulomb's law instead of the separation.",
                    "why": r'''
Take one sphere. Its thread makes an angle $\theta$ with the vertical, and the sphere has
moved sideways by half the separation, 3.0 cm, on a 25.0 cm thread:

```text
sin(theta)  = 0.030 / 0.250                = 0.1200      (theta = 6.89 deg)
cos(theta)  = sqrt(1 - 0.1200^2)           = 0.99277
tan(theta)  = 0.1200 / 0.99277             = 0.12087
```

Vertically the thread tension holds the weight, $T\cos\theta = mg$; horizontally it
holds off the repulsion, $T\sin\theta = F_e$. Dividing the second by the first removes
the tension entirely, which is why the mass of the thread and the stiffness of the knot
never enter:

```text
F_e = m g tan(theta)
    = 0.80e-3 kg * 9.81 m/s^2 * 0.12087
    = 7.848e-3 N * 0.12087               = 9.486e-4 N   (0.95 mN)
```

Now Coulomb's law backwards, with $r$ the full 6.0 cm between the two charges and both
charges equal to $q$:

```text
F_e = k q^2 / r^2      ->      q = sqrt(F_e * r^2 / k)

q^2 = 9.486e-4 * (0.060)^2 / 8.988e9
    = 3.415e-6 / 8.988e9                 = 3.800e-16 C^2

q   = sqrt(3.800e-16)                    = 1.949e-8 C   = 19.5 nC
```

Nineteen and a half nanocoulombs on each sphere — about $1.2\times10^{11}$ excess
electrons, which sounds enormous until you weigh them: the mass of that many electrons
is $10^{-19}$ kg, roughly one part in $10^{16}$ of the sphere. The spheres are visibly
pushed apart by an imbalance far too small to weigh, which is the same point the copper
calculation in the reading made from the other direction.

One detail worth noting rather than hiding: at 6.89° the difference between
$\sin\theta$ and $\tan\theta$ is only 0.7 %, so the small-angle shortcut
$F_e \approx mg\sin\theta$ gives 19.4 nC here and would also be accepted. That is a
legitimate approximation at this angle and a bad habit at 30°, where the same shortcut
understates the force by 13 %.
''',
                },
            ],
            "quiz": {
                "title": "Charge and field, checked",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Two small charged spheres sit 10 cm apart and repel each other with a force of 4 mN. You move them to 20 cm apart. What is the force now?",
                        "opts": ["2 mN", "1 mN", "8 mN", "4 mN, unchanged"],
                        "a": 1,
                        "why": (
                            "Coulomb's law has $r^2$ in the denominator, so the force falls as the *square* "
                            "of the distance: doubling the separation divides the force by four, giving 1 mN. "
                            "Answering 2 mN is the common slip — that would be the answer if the law went as "
                            "$1/r$, which is the law for the magnetic field around a straight wire but not for "
                            "the force between charges."
                        ),
                    },
                    {
                        "q": "You measure the electric field at a point by placing a small charge there and dividing the force it feels by its charge. You then repeat the measurement with a charge twice as large. What do you get?",
                        "opts": [
                            "Twice the field, because the force is twice as big",
                            "Half the field",
                            "The same field",
                            "Nothing — a field can only be measured with a 1 C charge",
                        ],
                        "a": 2,
                        "why": (
                            "The force doubles and the charge you divide by doubles, so the ratio $E = F/q$ is "
                            "unchanged. That is the whole point of defining a field: it is a property of the "
                            "space, put there by the *source* charges, and it does not depend on what you use "
                            "to probe it. (A real probe charge does disturb the sources it is measuring, which "
                            "is why the definition says *small*.)"
                        ),
                    },
                    {
                        "q": "Two identical positive charges sit at $(-d, 0)$ and $(+d, 0)$. What is the electric field exactly halfway between them, at the origin?",
                        "opts": [
                            "Zero",
                            "Twice the field of one charge, pointing along the x-axis",
                            "Twice the field of one charge, pointing along the y-axis",
                            "Undefined, because two fields cannot occupy the same point",
                        ],
                        "a": 0,
                        "why": (
                            "Each charge pushes a positive test charge away from itself, so at the midpoint one "
                            "field points in $+x$ and the other in $-x$ with exactly equal magnitude. Vectors "
                            "add, and these cancel. Note that the fields do not somehow annihilate: move a "
                            "millimetre off the midpoint and the field is back. Note also that the *potential* "
                            "at that point is not zero — module 2 makes that distinction."
                        ),
                    },
                    {
                        "q": "Which way does the electric field point in the space around an isolated negative charge?",
                        "opts": [
                            "Radially outward, away from the charge",
                            "Radially inward, towards the charge",
                            "In circles around the charge",
                            "There is no field, because the charge is negative",
                        ],
                        "a": 1,
                        "why": (
                            "The field is defined as the force *per unit positive charge*. A positive test "
                            "charge is attracted to a negative source, so the field points inward. This is the "
                            "sign convention doing real work: the field of a negative charge is the field of a "
                            "positive one with every arrow reversed, which is what you saw in the sandbox when "
                            "you made both diagonal entries negative."
                        ),
                    },
                    {
                        "q": "A charge of $+1$ nC and a charge of $+1$ µC — a thousand times larger — are held a fixed distance apart. Compare the electric force on each.",
                        "opts": [
                            "The force on the small charge is a thousand times larger",
                            "The force on the large charge is a thousand times larger",
                            "The forces are equal in size and opposite in direction",
                            "There is no force on the small charge, only on the large one",
                        ],
                        "a": 2,
                        "why": (
                            "Coulomb's law is symmetric: the same expression $k q_1 q_2 / r^2$ gives the force "
                            "on each, so the magnitudes are identical and the directions opposite — Newton's "
                            "third law, exactly as for gravity. What differs is the *acceleration*, since the "
                            "two objects have different masses, and that is usually what makes people expect "
                            "the forces themselves to differ."
                        ),
                    },
                    {
                        "q": "Why can two electric field lines never cross?",
                        "opts": [
                            "They can, wherever two charges are close together",
                            "Because the field at the crossing point would have to have two different directions at once",
                            "Because field lines repel each other",
                            "Because crossing lines would mean infinite force",
                        ],
                        "a": 1,
                        "why": (
                            "A field line is drawn by following the field direction, and at any given point the "
                            "field is a single vector with one direction. Two lines crossing would mean two "
                            "directions at one point, which the definition forbids. The one exception is a point "
                            "where the field is exactly zero — there is no direction to follow there, and that "
                            "is why lines appear to meet at the null point between two like charges."
                        ),
                    },
                ],
            },
            "lab": {
                "title": "Coulomb's law and superposition",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
Two functions, both short.

`coulomb_force(q1, q2, r)` returns the **signed** force between two point charges
`r` metres apart, in newtons: positive when they push apart, negative when they pull
together. The constant `K` is already defined for you.

`field_at(charges, point)` returns the electric field at `point` as a NumPy array
`[Ex, Ey]`, in volts per metre. `charges` is a list of `(q, x, y)` triples. Add up
one contribution per charge: a charge $q$ sitting at $\mathbf{s}$ contributes

```text
E = K * q * (point - s) / |point - s|**3
```

That expression is worth a second look. Its magnitude is $Kq/r^2$, because one power
of $r$ in the cube is used up normalising the direction vector — so it is Coulomb's
law with the direction attached.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

EPS0 = 8.8541878128e-12          # permittivity of free space, in F/m
K = 1.0 / (4.0 * np.pi * EPS0)   # Coulomb constant, in N m^2 / C^2


def coulomb_force(q1, q2, r):
    """Signed force between two point charges r metres apart, in newtons.

    Positive means they repel; negative means they attract.
    """
    # TODO: Coulomb's law.
    return 0.0


def field_at(charges, point):
    """Electric field at `point`, in V/m, as a numpy array [Ex, Ey].

    `charges` is a list of (q, x, y) triples in SI units.
    """
    point = np.asarray(point, dtype=float)
    E = np.zeros(2)
    # TODO: add one contribution per charge.
    return E


if __name__ == "__main__":
    print("force between two 1 nC charges 10 cm apart:",
          coulomb_force(1e-9, 1e-9, 0.1), "N")
    print("field 10 cm from a 1 nC charge:",
          field_at([(1e-9, 0.0, 0.0)], (0.1, 0.0)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

EPS0 = 8.8541878128e-12          # permittivity of free space, in F/m
K = 1.0 / (4.0 * np.pi * EPS0)   # Coulomb constant, in N m^2 / C^2


def coulomb_force(q1, q2, r):
    """Signed force between two point charges r metres apart, in newtons.

    Positive means they repel; negative means they attract.
    """
    return K * q1 * q2 / (r * r)


def field_at(charges, point):
    """Electric field at `point`, in V/m, as a numpy array [Ex, Ey].

    `charges` is a list of (q, x, y) triples in SI units.
    """
    point = np.asarray(point, dtype=float)
    E = np.zeros(2)
    for q, sx, sy in charges:
        d = point - np.array([float(sx), float(sy)])
        r = float(np.hypot(d[0], d[1]))
        if r == 0.0:
            continue
        E = E + K * q * d / r ** 3
    return E


if __name__ == "__main__":
    print("force between two 1 nC charges 10 cm apart:",
          coulomb_force(1e-9, 1e-9, 0.1), "N")
    print("field 10 cm from a 1 nC charge:",
          field_at([(1e-9, 0.0, 0.0)], (0.1, 0.0)))
'''}],
                "hints": [
                    "`coulomb_force` is one line: `K * q1 * q2 / (r * r)`. Do not take an absolute value — the sign is carrying the physics.",
                    "In `field_at`, `d = point - np.array([sx, sy])` is the vector *from the charge to the point*, which is the direction a positive charge is pushed.",
                    "`np.hypot(d[0], d[1])` gives the distance. Dividing `d` by the cube of it normalises the direction and applies $1/r^2$ in one step.",
                ],
                "tests": [
                    {"name": "two like charges repel, with the right magnitude", "code": r'''
_f = coulomb_force(1e-9, 1e-9, 0.1)
assert _f > 0, "two positive charges push each other apart, so the force is positive"
assert abs(_f - 8.987551792261173e-07) < 1e-15, \
    f"expected K*1e-18/0.01 = 8.98755e-07 N, got {_f!r}"
'''},
                    {"name": "opposite charges attract", "code": r'''
_f = coulomb_force(1e-9, -1e-9, 0.1)
assert _f < 0, "a positive and a negative charge attract, which the sign should show"
assert abs(_f + 8.987551792261173e-07) < 1e-15, f"expected -8.98755e-07 N, got {_f!r}"
'''},
                    {"name": "the force falls as the square of the distance", "code": r'''
_near = coulomb_force(2e-9, 3e-9, 0.05)
_far = coulomb_force(2e-9, 3e-9, 0.10)
assert abs(_near / _far - 4.0) < 1e-9, \
    f"doubling the distance should divide the force by 4, got a ratio of {_near / _far}"
'''},
                    {"name": "the field of one positive charge points away from it", "code": r'''
import numpy as np
_E = np.asarray(field_at([(1e-9, 0.0, 0.0)], (0.1, 0.0)), dtype=float)
assert _E.shape == (2,), f"field_at should return two components, got shape {_E.shape}"
assert _E[0] > 0 and abs(_E[1]) < 1e-12, f"the field should point along +x, got {_E.tolist()}"
assert abs(_E[0] - 898.7551792261172) < 1e-9, \
    f"expected K*1e-9/0.01 = 898.755 V/m, got {_E[0]!r}"
'''},
                    {"name": "the field of one negative charge points towards it", "code": r'''
import numpy as np
_E = np.asarray(field_at([(-1e-9, 0.0, 0.0)], (0.1, 0.0)), dtype=float)
assert _E[0] < 0, f"a negative charge pulls a positive test charge inwards, got {_E.tolist()}"
assert abs(_E[0] + 898.7551792261172) < 1e-9, f"expected -898.755 V/m, got {_E[0]!r}"
'''},
                    {"name": "two equal charges cancel at the midpoint, and only there", "code": r'''
import numpy as np
_pair = [(3e-9, -0.1, 0.0), (3e-9, 0.1, 0.0)]
_E = np.asarray(field_at(_pair, (0.0, 0.0)), dtype=float)
assert float(np.hypot(_E[0], _E[1])) < 1e-9, \
    f"equal charges either side should cancel exactly at the midpoint, got {_E.tolist()}"
_off = np.asarray(field_at(_pair, (0.0, 0.05)), dtype=float)
assert abs(_off[0]) < 1e-9, f"by symmetry the x component is still zero here, got {_off[0]!r}"
assert abs(_off[1] - 1929.29056884442) < 1e-6, \
    f"5 cm off the midpoint the field is back: expected 1929.29 V/m along +y, got {_off[1]!r}"
'''},
                    {"name": "superposition adds, it does not average", "code": r'''
import numpy as np
_one = np.asarray(field_at([(2e-9, -0.05, 0.0)], (0.0, 0.0)), dtype=float)
_two = np.asarray(field_at([(2e-9, -0.05, 0.0), (-2e-9, 0.05, 0.0)], (0.0, 0.0)), dtype=float)
assert abs(_two[0] - 2.0 * _one[0]) < 1e-6, \
    "at the centre of a +q/-q pair both fields point the same way and add to twice one of them"
assert abs(_two[0] - 14380.082867617872) < 1e-6, \
    f"expected 14380.08 V/m along +x, got {_two[0]!r}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Potential, energy and Gauss's law",
            "summary": "One number per point instead of an arrow, and a way to get fields from symmetry without integrating anything.",
            "concepts": [
                "Electric potential $V$ at a point is the work per unit charge needed to bring a charge there from far away, measured in volts (joules per coulomb). It is a single number, not an arrow.",
                "For a point charge, $V = kq/r$ — note the single power of $r$, against $r^2$ for the field.",
                "Potentials add as ordinary numbers, so a potential sum is easier than a field sum. The field is recovered as the slope: $E = -\\mathrm{d}V/\\mathrm{d}x$ in one dimension.",
                "The work done by the field on a charge moving from A to B is $q(V_A - V_B)$, and depends only on the endpoints — never on the route.",
                "Electric flux through a surface counts the field lines crossing it. Gauss's law: the flux out of any *closed* surface equals the charge enclosed divided by $\\varepsilon_0$, whatever the shape of the surface.",
                "Gauss's law turns symmetry into answers: for a sphere, a long line or a large flat plate, one line of algebra gives the field with no integration at all.",
            ],
            "read": [
                {
                    "title": "Work, energy, and one number for each point",
                    "minutes": 13,
                    "body": r'''
A field map is a great many arrows. Module 1 showed what that costs: every point needs a
magnitude *and* a direction, contributions have to be resolved into components before
they can be added, and the second worked example spent most of its length on a direction
cosine of 0.60 and almost none of it on physics. Two charges were already tedious. Ten
would be unbearable.

There is an older piece of bookkeeping that avoids all of it, and it is the one every
voltmeter in the world reports. Instead of asking *which way would this point push a
charge*, ask *how much work does it take to bring a charge here*. Work is a single
number. Numbers add without any geometry at all.

## Work, and the one fact that makes it usable

Push a charge from A to B against an electric field and you do work on it: force times
distance, for a constant force along the direction of travel, and a sum of little
$F\,\mathrm{d}l$ contributions otherwise. That much is mechanics and holds for any force
whatever.

The fact that makes the electric case special is this: **the work is the same for every
route from A to B.** Not approximately, not usually — always, for charges at rest.

The reason is visible in the shape of Coulomb's law. The force from a point charge
points straight out along the radius and its size depends only on $r$. Take any path at
all and approximate it by a staircase of two kinds of step: little arcs at constant $r$,
and little radial moves in and out. On an arc you move perpendicular to the force, so
that step does no work at all — you can slide right around a source charge, all the way,
for free. On a radial step the work depends only on where the step started and where it
finished. Add up the staircase and everything cancels except the first radius and the
last one. Refine the staircase and the result does not change.

Superposition finishes the argument. If it holds for one source charge it holds for a
sum of them, because the total work is the sum of the works.

So: fix a reference point once, and every point in space acquires a definite number —
the work it takes to get a charge there from the reference. That is one number per
point, and it is the whole idea.

## Divide out the test charge, again

The work depends on how much charge you carried, and in exactly the trivial way: carry
twice the charge and you do twice the work. Divide it out, the same move that turned a
force into a field:

$$V_B - V_A = \frac{W_{A\to B}\ \text{done against the field}}{q_0}$$

The result is the **electric potential**, in joules per coulomb, which is given its own
name: the volt. A potential *difference* of 1 V between two points means it takes 1 J of
work to move 1 C between them.

Notice what the definition does and does not fix. Differences are physical; the zero is
a choice. For a finite clump of charge the convention is to put the zero infinitely far
away, which is what makes the expressions below come out clean. In a circuit the
convention is to put it on a particular piece of copper and call that piece ground. Both
are choices, and no measurement can tell them apart — which is exactly the point the
last quiz question in this module makes with a constant 12 V.

One sign to keep straight, because it is the commonest slip in the whole subject. The
work done *by the field* on a charge moving from A to B is

$$W_{\text{field}} = q(V_A - V_B)$$

and the work you must do to move it quasi-statically is the negative of that. A positive
charge released in a field runs *downhill* in potential, and the field does positive work
on it. A negative charge released in the same field runs uphill.

## The potential of a point charge

Now compute it once, for the case everything else is built out of. A source charge $Q$
sits at the origin; a test charge $q_0$ sits at distance $r$. The field pushes the test
charge outward with force $kQq_0/x^2$ when it is at $x$, so the work the field does
letting it escape all the way to infinity is

$$W = \int_r^{\infty} \frac{kQq_0}{x^2}\,\mathrm{d}x
    = kQq_0\left[-\frac{1}{x}\right]_r^{\infty} = \frac{kQq_0}{r}$$

That is the energy the pair had in reserve at separation $r$, so it is the potential
energy $U(r) = kQq_0/r$. Divide by the test charge and the potential is

$$V(r) = \frac{kQ}{r}$$

Look at the exponent. The field goes as $1/r^2$ and the potential goes as $1/r$: the
integration ate one power. Doubling the distance from a charge quarters the field and
halves the potential. Getting that wrong is worth an order of magnitude, so here is the
whole family in one place, worth committing to memory:

```text
quantity              for a point charge      falls as    adds as
----------------------------------------------------------------------
force      F          k q1 q2 / r^2            1/r^2      vectors
field      E          k Q / r^2                1/r^2      vectors
potential  V          k Q / r                  1/r        plain numbers
energy     U          k q1 q2 / r              1/r        plain numbers
```

And the signs take care of themselves. Near a negative charge the potential is negative,
full stop — there is no direction to reason about, only a minus sign to carry.

## Worked: two charges, one number, and what a third one costs

$q_1 = +5.0$ nC sits at the origin and $q_2 = -3.0$ nC sits at $x = 20.0$ cm. What is the
potential at the point $P = (0,\ 15.0\ \mathrm{cm})$, and how much work does it take to
bring a $+2.0$ nC charge to $P$ from far away?

The geometry first. $P$ is 15.0 cm from $q_1$ straight up the $y$ axis. From $q_2$ it is
the hypotenuse of a 20-by-15 triangle, which is a 3–4–5 scaled by five: 25.0 cm.

```text
r1 = 0.150 m                      r2 = sqrt(0.200^2 + 0.150^2) = 0.250 m

V1 = k q1 / r1 = 8.988e9 * 5.0e-9 / 0.150
   = 44.94 / 0.150                                    = +299.6 V

V2 = k q2 / r2 = 8.988e9 * (-3.0e-9) / 0.250
   = -26.964 / 0.250                                  = -107.9 V

V  = V1 + V2 = 299.6 - 107.9                          = +191.7 V
```

No components, no angles, no direction cosines — just two divisions and a subtraction,
and the 3–4–5 triangle was used only to get a distance rather than to resolve anything.
Compare with what the *field* at $P$ would have cost: two magnitudes, two direction
cosines, four components, and a Pythagoras at the end.

The work follows immediately. Bringing $q_3 = +2.0$ nC in from infinity, where the
potential is zero by our choice of reference, takes

```text
W = q3 * (V_P - V_infinity) = 2.0e-9 * (191.7 - 0)
  = 3.83e-7 J                                         = 383 nJ
```

against the field — positive, because $P$ sits at a positive potential and pushing a
positive charge to a positive potential is uphill. Had $q_3$ been negative the same
arithmetic would have given $-383$ nJ, meaning the field does the work for you and you
have to hold the charge back on the way in.

## Worked: an electron in a vacuum tube

Every cathode-ray tube, X-ray head and electron microscope in existence runs on one
line of this material. An electron starts at rest at a hot cathode and is pulled across
a gap to an anode held 500 V higher. How fast does it arrive?

The charge on the electron is $-e$, and it moves to a place 500 V *higher* in potential,
which for a negative charge is downhill. All the potential energy it loses turns into
kinetic energy:

```text
energy gained  = e * V = 1.602e-19 C * 500 V          = 8.011e-17 J

(1/2) m v^2    = 8.011e-17 J
v^2            = 2 * 8.011e-17 / 9.109e-31            = 1.759e14 m^2/s^2
v              = sqrt(1.759e14)                       = 1.33e7 m/s
```

Thirteen million metres per second, which is 4.4 % of the speed of light — fast, but
slow enough that ignoring relativity costs about a tenth of a per cent. Push the same
electron through 50 kV, as a dental X-ray head does, and it arrives at about 40 % of $c$
and the calculation above is genuinely wrong.

The joule is an absurd unit for that answer, which is why nobody uses it: an electron
crossing 500 V gains, by definition, 500 **electronvolts**. The electronvolt is not a
new physical quantity, it is the previous calculation with the $1.602\times10^{-19}$
left off, and one eV is $1.602\times10^{-19}$ J. Chemical bonds are a few eV, visible
light is 1.6 to 3.3 eV per photon, and stripping an electron off a nitrogen molecule
takes about 15.6 eV — which is why breaking air down needs a fierce *field* rather than a
fierce voltage: the energy has to be picked up over the very short distance between one
collision and the next.

## Getting the field back out

If the potential came from integrating the field, the field must come back out by
differentiating the potential. In one dimension:

$$E_x = -\frac{\mathrm{d}V}{\mathrm{d}x}$$

The field is the *slope* of the potential, and the minus sign says it points downhill.
This is the sense in which the potential picture loses nothing: the arrows are still
there, encoded as the steepness of a landscape, and one number per point is enough to
reconstruct all three components of a vector at every point because the three
derivatives are all you need.

The useful case is a uniform field, where the slope is constant and the calculus
collapses to a division. Between two parallel plates a distance $d$ apart with a voltage
$V$ across them,

$$E = \frac{V}{d}$$

Put 12 V across a gap of 0.10 mm and the field in the gap is
$12/1.0\times10^{-4} = 1.2\times10^{5}$ V/m — 120 kV/m out of a battery you would call
harmless, because the gap is small. This is why the gate oxide of a MOSFET, a few
nanometres thick, sits within a factor of two of destroying itself at 1 V, and why 12 V
across a 3 mm air gap does nothing at all.

One more consequence, free: surfaces of constant potential are everywhere perpendicular
to the field. Move along an equipotential and you do no work; do no work while moving,
and the force has no component along your motion. That is why field lines meet a
conductor's surface at right angles, which module 5 leans on heavily.

## The mistakes people actually make

- **Reading zero potential as zero field.** At the midpoint of a dipole the potential is
  exactly zero and the field is at its strongest. The potential is the height of a
  landscape and the field is its slope; a hillside crosses sea level at speed. One of the
  numeric units below lands on a point where $V = 0$ and $E = 2.4$ kV/m, for exactly this
  reason.
- **Carrying $r^2$ into the potential.** Tempting, because the field's $r^2$ was just
  drilled. The symptom is an answer that is too small by a factor of $r$ — at 20 cm, five
  times too small.
- **Dropping the sign of a negative source charge.** Potentials are signed numbers and
  the sign is the only thing distinguishing a hill from a valley. In the worked example
  above, keeping $q_2$ positive gives 407 V instead of 192 V.
- **Confusing the work the field does with the work you do.** They are equal and
  opposite. If an answer has the right size and the wrong sign, this is almost always
  why.
- **Treating the potential as a property of the charge you brought.** It is a property of
  the *point*, set up by the source charges, and it is there whether or not anyone probes
  it — exactly as the field is.
- **Saying "5 volts of energy".** A volt is a joule *per coulomb*. The energy depends on
  how much charge you move through it, which is why a 5 V USB supply and a 5 V signal
  line are utterly different things.

## Where this stops working

**The reference at infinity needs a finite clump of charge.** Put the zero at infinity
for an infinite line of charge and the potential is infinite everywhere: the correct
expression is $V = -2k\lambda \ln r + \text{constant}$, which has no limit as
$r \to \infty$. Nothing is broken — differences are still perfectly finite and
measurable — but you must nominate a reference radius by hand. The second reading unit
meets that line charge properly.

**$V = kQ/r$ diverges at $r = 0$.** The same limitation the field has, for the same
reason: a genuine point charge is an idealisation. Real charge sits on a surface with a
finite radius and you never reach the middle.

**All of this is static.** The path-independence argument used the fact that the force on
a charge depends only on where the charge is. Once magnetic fields change with time that
stops being true: the induced electric field circulates, and you can carry a charge round
a closed loop and come back with more energy than you started with — which is what a
transformer does for a living. A quantity that changes when you go round a loop and
return is not a function of position, so no potential exists for that part of the field.
Module 4 derives it and module 10 puts it in its final form. Until then, every "voltage"
in this course is a genuine difference of a genuine potential.

**A battery is not an electrostatic potential difference.** Chemistry, not the
electrostatic field, does the work of separating charge inside the cell. In the steady
state the terminal voltage does equal an electrostatic potential difference, so the
circuit arithmetic in EE101 was never wrong; but the thing driving it is not a hill that
charges roll down.
''',
                },
                {
                    "title": "Counting what crosses a surface: flux, and Gauss's law",
                    "minutes": 14,
                    "body": r'''
Hang a 100 W lamp in the middle of an empty room and draw an imaginary sphere of radius
1 m around it. A hundred watts crosses that sphere every second. Draw a sphere of radius
2 m instead: the light per square metre has dropped to a quarter, but the sphere has four
times the area, so a hundred watts still crosses it. Draw a lumpy potato-shaped surface
round the lamp — still a hundred watts. Draw one that does *not* contain the lamp and the
answer is zero: whatever light enters through one side leaves through the other.

That total-crossing-a-surface is a genuinely useful quantity precisely because it refuses
to change. Module 1 used the picture informally, to argue that the force between charges
ought to go as $1/r^2$. This unit turns it into an equation, and the equation turns out
to be one of the four that the whole of electromagnetism is written in.

## Flux, on one flat patch

Take a uniform field $\mathbf{E}$ and a flat patch of area $A$. Define the **electric
flux** through the patch as

$$\Phi = E A \cos\theta$$

where $\theta$ is the angle between the field and the *normal* to the patch — the
direction sticking out of it, not lying in it. The units are (V/m)(m²) = V·m.

The cosine is doing an obvious job. Hold a window frame square-on to falling rain and a
certain amount comes through per second. Tilt it and less comes through, because the
frame now presents a smaller shadow to the rain. Turn it edge-on and nothing comes
through at all, though the rain has not changed one bit. Only the component of the field
along the normal crosses the patch; the component lying in the surface slides along it.

For a curved surface or a non-uniform field, chop it into patches small enough that both
are effectively constant, and add:

$$\Phi = \oint \mathbf{E}\cdot \mathrm{d}\mathbf{A}$$

The circle on the integral is a reminder that the surface is closed, which is the case
that matters next.

## Why a closed surface is special

A closed surface has an inside and an outside, so the ambiguity about which way the
normal points goes away: by convention it points outward everywhere. That fixes signs,
and the signs are what make the whole thing work. Field entering the surface has
$\theta > 90°$, a negative cosine, and contributes negatively; field leaving contributes
positively.

Now take a field line that merely passes through — in one side, out the other. It
contributes once negatively and once positively, and the two cancel. The only way the
net flux can come out non-zero is if lines *begin* or *end* inside the surface. And from
module 1, field lines begin and end on exactly one thing: charge.

So the net flux out of a closed surface ought to be a measure of the charge inside it,
and nothing else. That is a statement about a picture. The next section makes it a
statement with a number in it.

## The sphere around a point charge, done properly

Put a charge $Q$ at the origin and take the closed surface to be a sphere of radius $r$
centred on it. Two facts make the integral trivial, and both come from the symmetry:
the magnitude of $\mathbf{E}$ is the same everywhere on the sphere, and the field is
everywhere parallel to the outward normal, so $\cos\theta = 1$ at every point.

```text
E on the sphere  = k Q / r^2         same value everywhere
area of sphere   = 4 pi r^2
theta            = 0 everywhere,  so cos(theta) = 1

Phi = E * A = (k Q / r^2) * (4 pi r^2)
            = 4 pi k Q                        the r^2 cancels exactly

and since k = 1 / (4 pi eps0):

Phi = 4 pi Q / (4 pi eps0)          = Q / eps0
```

Every trace of $r$ has gone. That cancellation is not luck: it is the inverse square law
meeting the area of a sphere, which is the same coincidence-that-is-not-a-coincidence
module 1 pointed at. It is also why the Coulomb constant is conventionally written
$1/(4\pi\varepsilon_0)$ instead of as a single letter — so that the $4\pi$ of the sphere
can cancel in plain sight and leave $Q/\varepsilon_0$ behind.

## Why any surface at all, and not just a sphere

Deform the sphere. Push one patch of it outward to a larger radius: its area grows as
$r^2$ while the field through it falls as $1/r^2$, so its contribution is unchanged.
Tilt a patch instead of moving it: it presents a larger area, but at an angle, and the
$\cos\theta$ takes back exactly what the extra area gave. Do that everywhere and you can
distort the sphere into any closed shape you like — a cube, a potato, a shape with dents
in it — without changing the total.

Superposition does the rest. Several charges inside contribute their fluxes
independently, and they simply add. A charge *outside* the surface contributes zero,
because its lines go in one side and out the other. What survives is

$$\oint \mathbf{E}\cdot \mathrm{d}\mathbf{A} = \frac{Q_{\text{enc}}}{\varepsilon_0}$$

**Gauss's law**, and it is exact, for any closed surface whatever, with $Q_{\text{enc}}$
the total charge inside the surface and no reference anywhere to the charge outside it.

## Always true, occasionally useful

Read that carefully before reaching for it. Gauss's law is one equation, and
$\mathbf{E}$ is a function of position with three components — an infinity of unknowns.
One equation cannot deliver them. Writing down the law never, by itself, gives you a
field.

What makes it a tool is a surface on which you can argue that $E$ has the same value
everywhere and points either straight along the normal or entirely across it. Then and
only then does $\oint \mathbf{E}\cdot\mathrm{d}\mathbf{A}$ collapse to $E \times A$, and
a division finishes the job. Exactly three geometries do this, and they are the sphere,
the infinite cylinder and the infinite plane. Everything below is one of those three.

## Worked: the long charged wire

A long straight wire carries charge uniformly along its length, $\lambda = 12$ nC per
metre. What is the field 4.0 cm from it?

By symmetry the field must point straight out from the wire — there is nothing in the
arrangement to make it lean one way along the wire rather than the other — and its
magnitude can depend only on the distance from the wire. So take the Gaussian surface to
be a cylinder of radius $r$ and length $L$, coaxial with the wire.

The two flat end caps contribute nothing: their normals point along the wire, the field
points across it, $\cos 90° = 0$. On the curved side the field is everywhere parallel to
the outward normal and everywhere the same size. So:

```text
curved area          = 2 pi r L
charge enclosed      = lambda * L

E * (2 pi r L)       = lambda L / eps0            the L cancels

E                    = lambda / (2 pi eps0 r)     =  2 k lambda / r
```

with the numbers,

```text
2 k lambda  = 2 * 8.988e9 * 12e-9                 = 215.7 N m^2 C^-1 / m
E           = 215.7 / 0.040                       = 5.39e3 V/m
```

5.39 kV/m at 4 cm. Two things are worth noticing. The first is the falloff: $1/r$, not
$1/r^2$. Backing away from a point charge, the sphere your influence spreads over grows
as $r^2$; backing away from a line, the cylinder grows only as $r$, because it gains no
length. The second is that $L$ cancelled, which is what "infinite" bought us — the answer
never had to know how long the wire was.

The potential of that line is worth a sentence, because it is where the previous reading
unit's caveat bites. Integrating $2k\lambda/r$ gives $V = -2k\lambda\ln r + C$, which
grows without limit as $r \to \infty$. There is no way to put the zero of potential at
infinity here. You nominate a reference radius, and only differences mean anything —
which was always true and is merely unavoidable in this case.

## Worked: the charged sheet, and where capacitors come from

Now a large flat sheet carrying charge $\sigma$ per square metre. By symmetry the field
must point straight away from the sheet on both sides, and can depend only on the
distance from it.

Take the Gaussian surface to be a short cylinder — a pillbox — poking through the sheet,
with faces of area $A$ parallel to it, one on each side. The curved side of the pillbox
contributes nothing: the field is parallel to it. Each flat face contributes $EA$, and
there are two of them.

```text
flux out        = E A  +  E A                   = 2 E A
charge enclosed = sigma * A

2 E A = sigma A / eps0                          the A cancels

E = sigma / (2 eps0)
```

The distance from the sheet is not in the answer. The field of an infinite charged plane
does not fall off at all, which sounds wrong until you notice that the pillbox never
mentioned the distance either: back away and you take in more sheet at exactly the rate
that the extra distance costs you.

Now put two such sheets facing each other, one at $+\sigma$ and one at $-\sigma$. Between
them the two fields point the same way and add to $\sigma/\varepsilon_0$; outside, they
point opposite ways and cancel to nothing. With $\sigma = 2.0\ \mu\mathrm{C/m^2}$:

```text
E between plates = sigma / eps0
                 = 2.0e-6 / 8.854e-12                = 2.26e5 V/m

with a gap of 0.50 mm, V = E d
                 = 2.26e5 * 5.0e-4                   = 113 V
```

That is a parallel-plate capacitor, computed with nothing but Gauss's law, and module 3
starts exactly here: divide the charge on a plate by that 113 V and you have a number in
farads.

## A third shape: inside a ball of charge

Spread a charge $Q$ uniformly through the *volume* of an insulating sphere of radius $R$
— not over its surface, right through it. Outside, a Gaussian sphere encloses all of $Q$
and the field is $kQ/r^2$, exactly as if the whole charge sat at the centre. Inside, at
radius $r < R$, the Gaussian sphere encloses only the fraction of the volume it contains:

$$Q_{\text{enc}} = Q\frac{r^3}{R^3}, \qquad
E = \frac{1}{4\pi\varepsilon_0}\frac{Q_{\text{enc}}}{r^2} = \frac{kQr}{R^3}$$

The field *rises linearly* from zero at the centre to $kQ/R^2$ at the surface, and falls
as $1/r^2$ beyond it. With $Q = 30$ nC and $R = 12.0$ cm, the surface field is
$8.988\times10^9 \times 30\times10^{-9}/0.0144 = 18.7$ kV/m, and halfway out, at 6.0 cm,
it is exactly half that: 9.36 kV/m. The last numeric unit in this module is this same
problem wearing cylindrical clothes.

## The mistakes people actually make

- **Pulling $E$ out of the integral where it is not constant.** Draw a cube round a point
  charge and Gauss's law still holds perfectly — the flux is still $Q/\varepsilon_0$ —
  but $E$ varies from face-centre to corner and is not perpendicular to the face, so
  $\Phi = EA$ is simply false and the "answer" you get is wrong. The law being true is
  not the same as the shortcut being available.
- **Thinking an outside charge makes no field on the surface.** It makes a perfectly
  good field at every point of the surface. What it makes no contribution to is the
  *net* flux, because its lines enter and leave. Those are different claims, and the
  quiz in this module asks you to separate them.
- **Using the total charge where the enclosed charge belongs.** Inside the ball above,
  using $Q$ rather than $Qr^3/R^3$ overstates the field by $R^3/r^3$ — a factor of eight
  at half the radius.
- **Losing the factor of two between $\sigma/2\varepsilon_0$ and $\sigma/\varepsilon_0$.**
  An isolated sheet sends field out both ways and gets the 2; the field just outside a
  charged conductor is $\sigma/\varepsilon_0$ because there is no field on the other side
  to share with. Module 5 does this properly, and the factor of two is the single most
  common slip in it.
- **Mishandling the end caps.** The habit that saves you is to ask, at each piece of the
  surface, whether $\mathbf{E}$ has any component along that piece's normal. If it does
  not, that piece contributes nothing and you can stop thinking about it.

## Where Gauss's law stops helping

**No symmetry, no shortcut.** Two point charges, a finite rod, a charged disc, anything
lumpy: the law is still exactly true and completely useless, because no surface exists on
which you can argue $E$ is constant. You are back to summing contributions, and in
practice to summing them numerically.

**"Infinite" means "much longer than your distance from it".** A real wire is finite, and
the cylinder argument leaks near its ends. At the midplane of a rod of length $L$, the
true field is smaller than the infinite-line answer by a factor
$1/\sqrt{1 + (2r/L)^2}$. Stand a tenth of the rod's length away and that is 0.98 — the
idealisation is 2 % high. Stand at half its length away and the factor is $1/\sqrt{2}$,
so the idealisation is 41 % high and you should be integrating instead.

**Matter changes the constant.** Fill the space with an insulator that polarises and
$\varepsilon_0$ becomes $\varepsilon_r\varepsilon_0$, with $\varepsilon_r$ around 4 for
glass and about 80 for water. Gauss's law survives in the same form; module 3 uses it in
that form to explain what a dielectric does to a capacitor.

**And a reversal worth knowing.** Almost every law in this course gets amended later:
Coulomb's law is the static limit of something larger, the potential stops existing when
fields change, Ampère's law needs an extra term that module 10 supplies. Gauss's law for
the electric field is the exception. It is written above in exactly the form it has in
Maxwell's four equations, it is true for charges in violent motion, and it never needed
repair. The only thing that changes is that its magnetic twin has a zero on the right
instead of a charge — because no one has ever found a magnetic charge for the lines to
begin on.
''',
                },
            ],
            "sandbox": {
                "title": "Where the field lines begin",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": 1, "a12": 0, "a21": 0, "a22": -1},
                "brief": r'''
The same vector-field panel as module 1, opened on a different field. Read the axes
as two coordinates in a flat region of space and the strokes as the direction of $E$.

The readout under the picture reports two numbers about the field you have set up.
The one that matters here is the **trace**, $a_{11} + a_{22}$. For a field written
this way the trace *is* the divergence — the amount by which lines begin at a point
rather than merely pass through it — and Gauss's law says that number is proportional
to the charge density sitting there. Zero trace means no charge.

The opening values have trace exactly zero, and the picture shows what that looks
like: lines that arrive, turn, and leave again, with nothing anywhere for one to
begin or end on.
''',
                "notice": [
                    "As it opens the readout says trace = 0.00, and the label calls it a saddle. Six of the eight curves pass through without touching the dot; the two launched exactly on the vertical axis run into it and stop, at the single point where the field is zero. No curve anywhere begins or ends on charge, because there is none: charge-free space, drawn.",
                    "Raise $a_{11}$ to 2 and leave $a_{22}$ at $-1$. The trace reads 1.00 and the curves now spread outward overall — positive charge is present, and Gauss's law says the enclosed charge is what the trace measures.",
                    "Set both $a_{11}$ and $a_{22}$ to $-1.5$. The trace reads $-3.00$ and every curve now ends on the black dot: a negative charge density, with the lines terminating on it.",
                    "Now move $a_{12}$ and $a_{21}$ around while leaving $a_{11}$ and $a_{22}$ alone. The picture distorts a great deal and the trace never budges. Charge is what makes lines start and stop; shearing the field sideways is not charge.",
                ],
            },
            "derive": {
                "title": "The potential of a point charge, and the field back out of it",
                "minutes": 14,
                "vars": ["k", "Q", "q", "x", "r", "a", "b"],
                "brief": r'''
The reading unit quoted $V = kQ/r$ and moved on. Here you produce it, from the only
thing this course has actually established — Coulomb's law — and then run the machinery
backwards to check that the field comes out again.

The arrangement is a source charge $Q$ fixed at the origin and a test charge $q$ out
along the positive axis. Distances measured from the origin are called $x$ while the
test charge is moving and $r$ when it has stopped somewhere definite.

The last step is the one that gets used: almost every potential question in practice is
a *difference* between two places, and the general expression for it is worth having in
front of you.
''',
                "steps": [
                    {
                        "prompt": "The test charge $q$ is at a distance $x$ from the source $Q$. Write the magnitude of the electric force on it.",
                        "answer": "\\frac{k Q q}{x^2}",
                        "hint": "This is Coulomb's law with nothing done to it: the product of the two charges over the square of their separation, times $k$.",
                        "deconstruct": [
                            "Coulomb's law gives the force between two point charges as $k q_1 q_2 / r^2$.",
                            "Here the two charges are $Q$ and $q$, and their separation is $x$.",
                        ],
                    },
                    {
                        "prompt": "Both charges positive, so the force pushes the test charge outward. Let it go from $x = r$ all the way out to infinity, and write the total work the field does on it: $\\int_r^{\\infty} kQq/x^2\\,\\mathrm{d}x$.",
                        "answer": "\\frac{k Q q}{r}",
                        "placeholder": "kQq over a distance",
                        "hint": "The antiderivative of $x^{-2}$ is $-1/x$. Evaluate $-kQq/x$ at the top limit, where it is zero, and subtract its value at $x = r$.",
                        "deconstruct": [
                            "$\\int x^{-2}\\,\\mathrm{d}x = -1/x$, so the integral is $kQq\\left[-1/x\\right]_r^{\\infty}$.",
                            "At $x \\to \\infty$ the bracket goes to zero; at $x = r$ it is $-1/r$.",
                            "Zero minus $(-1/r)$ is $+1/r$, and one power of $x$ has been eaten by the integration.",
                        ],
                    },
                    {
                        "prompt": "That work is the energy the pair had in reserve when they were $r$ apart, so it is the potential energy $U(r)$. Divide out the test charge to get the potential $V(r)$ — a property of the point rather than of the probe.",
                        "answer": "\\frac{k Q}{r}",
                        "hint": "The same division that turned a force into a field in module 1. Only $q$ leaves; nothing else in the expression mentions the test charge.",
                        "deconstruct": [
                            "$V = U/q$ by definition, in joules per coulomb.",
                            "$U = kQq/r$, and the $q$ cancels straight out.",
                        ],
                    },
                    {
                        "prompt": "Now go the other way as a check. The field is minus the slope of the potential, $E = -\\mathrm{d}V/\\mathrm{d}r$. Differentiate what you just wrote and give the magnitude of $E$.",
                        "answer": "\\frac{k Q}{r^2}",
                        "placeholder": "kQ over a power of r",
                        "hint": "$\\mathrm{d}(r^{-1})/\\mathrm{d}r = -r^{-2}$, and the minus sign in the definition cancels the one the derivative produces.",
                        "deconstruct": [
                            "Write $V = kQ\\,r^{-1}$, so $\\mathrm{d}V/\\mathrm{d}r = -kQ\\,r^{-2}$.",
                            "$E = -\\mathrm{d}V/\\mathrm{d}r$ flips that sign back to positive.",
                            "Getting Coulomb's law back is the point of the step: nothing was lost in going to one number per point.",
                        ],
                    },
                    {
                        "prompt": "Finally the useful form. A charge is carried from a distance $a$ from the source to a distance $b$. Write the potential difference $V(a) - V(b)$ it moves through.",
                        "answer": "k Q \\left( \\frac{1}{a} - \\frac{1}{b} \\right)",
                        "placeholder": "kQ times a difference of two reciprocals",
                        "hint": "Just evaluate your $V(r)$ at $r = a$ and at $r = b$ and subtract. Factor $kQ$ out of both terms.",
                        "deconstruct": [
                            "$V(a) = kQ/a$ and $V(b) = kQ/b$.",
                            "Subtract, then take the common factor $kQ$ outside the bracket.",
                        ],
                    },
                ],
                "closing": r'''
$$V(r) = \frac{kQ}{r}, \qquad V(a) - V(b) = kQ\left(\frac{1}{a} - \frac{1}{b}\right)$$

Four things fall out of those two lines, and all four get used later in the course.

* **The exponent.** One power of $r$ in the potential against two in the field. The
  integration ate exactly one, and it had to: energy is force times distance, so the
  energy expression carries one more power of distance than the force does.
* **Where the zero went.** Setting $V(\infty) = 0$ was a choice, made when the upper
  limit of the integral was taken to infinity and the bracket was allowed to vanish
  there. It is available only because the charge is confined to a point. Run the same
  integral on the field of an infinite line, $2k\lambda/r$, and you get
  $-2k\lambda\ln r$, which has no limit at infinity at all — so a line charge has a
  perfectly good potential *difference* between any two radii and no natural zero.
* **The difference is what survives.** Nothing measurable depends on the reference,
  because every physical quantity in this module is a difference: work is
  $q(V_A - V_B)$, field is a slope. Add ten volts to the potential everywhere and no
  experiment changes.
* **The far-field approximation you will meet constantly.** If $b \gg a$, the $1/b$ term
  is negligible and the difference is just $kQ/a$: bringing a charge in from anywhere
  sufficiently far away costs the same as bringing it in from infinity. At $b = 10a$ the
  error in that approximation is 10 %, and at $b = 100a$ it is 1 %.
''',
            },
            "blanks": {
                "title": "Potential, work and flux, term by term",
                "minutes": 9,
                "caption": "the six expressions this module runs on, with the load-bearing parts removed",
                "lang": "text",
                "brief": r'''
Nothing here is executed. These are the expressions the rest of the module is built on,
and the holes are in the places where a slip changes the answer rather than the spelling
— the power on the distance, the order of a subtraction, the trigonometric function on
a tilted surface, and what the enclosed charge is divided by.

Three of these have a distractor that is dimensionally sensible and still wrong, so
saying why a choice is right before taking it is worth the ten seconds.
''',
                "listing": """# A point charge Q sitting on its own in vacuum, and a field point r away.

V = k * Q / ___                # the potential there, in volts (= joules per coulomb)

# Several source charges acting at the same field point:

V_total = ___

# Carrying a charge q from point A to point B. The work done BY the field:

W = q * ___                    # the route taken does not appear anywhere

# Recovering the field from the potential, along one axis:

E_x = - dV / ___               # units V/m

# Flux of a uniform field E through a flat patch of area A, whose
# normal makes an angle theta with the field:

Phi = E * A * ___

# Gauss's law, for ANY closed surface, however lumpy:

Phi_closed = Q_enclosed / ___
""",
                "blanks": [
                    {
                        "prompt": "What sits under $kQ$ in the potential of a point charge?",
                        "hole": "?",
                        "opts": ["r", "r**2", "r**3", "sqrt(r)"],
                        "a": 0,
                        "why": "One power of $r$, not two. The field goes as $1/r^2$ and integrating it over distance to get an energy ate one power, so doubling your distance from a charge quarters the field and halves the potential.",
                        "whys": [
                            "One power of $r$, not two. The field goes as $1/r^2$ and integrating it over distance to get an energy ate one power, so doubling your distance from a charge quarters the field and halves the potential.",
                            "This is the field's falloff, freshly drilled in module 1, and it is the single commonest slip here. The symptom is an answer too small by a factor of $r$: at 20 cm from the charge, five times too small.",
                            "A cube is the falloff of a dipole *field*, where two opposite charges nearly cancel. No potential of a single point charge falls that fast.",
                            "A square root would make the potential fall off more slowly than the field does in every respect, and it never appears in electrostatics. It is also dimensionally wrong: $kQ$ divided by the square root of a length is not a voltage.",
                        ],
                    },
                    {
                        "prompt": "Several charges, one field point. What is the total potential there?",
                        "hole": "?",
                        "opts": [
                            "the plain sum V1 + V2 + ... + Vn, signs included",
                            "the vector sum of V1 ... Vn",
                            "the sum of the magnitudes |V1| + ... + |Vn|",
                            "whichever of V1 ... Vn is largest",
                        ],
                        "a": 0,
                        "why": "Potential is a single number with a sign, so superposition here is ordinary addition — no components, no angles, no geometry beyond getting each distance right. That is the entire reason the potential picture is worth having.",
                        "whys": [
                            "Potential is a single number with a sign, so superposition here is ordinary addition — no components, no angles, no geometry beyond getting each distance right. That is the entire reason the potential picture is worth having.",
                            "Fields are vectors and have to be summed as vectors; potentials are not and do not. A potential has no direction to sum, and asking which way a voltage points is not a question.",
                            "Dropping the signs turns every valley into a hill. At the midpoint of a dipole the true potential is exactly zero, and totalling magnitudes there gives twice one charge's contribution instead.",
                            "Taking the largest would mean a second charge contributed nothing until it overtook the first, so the potential would jump as the two crossed over. Every source contributes, always.",
                        ],
                    },
                    {
                        "prompt": "The work done *by the field* on a charge going from A to B — what does $q$ multiply?",
                        "hole": "?",
                        "opts": ["(V_A - V_B)", "(V_B - V_A)", "(V_A + V_B)", "V_A * V_B"],
                        "a": 0,
                        "why": "Start minus finish. A positive charge released in a field runs downhill in potential, so if $V_A > V_B$ the field does positive work on it — which this ordering gives. Note also what is absent: the path, the speed, and the time taken.",
                        "whys": [
                            "Start minus finish. A positive charge released in a field runs downhill in potential, so if $V_A > V_B$ the field does positive work on it — which this ordering gives. Note also what is absent: the path, the speed, and the time taken.",
                            "This is the work *you* do pushing the charge along, which is the negative of the work the field does. It is the near miss to watch for: right size, wrong sign, and the two are constantly confused because both are called 'the work'.",
                            "A sum instead of a difference would make the answer depend on where the zero of potential was put, and the zero is a free choice. Adding ten volts everywhere would change a measurable energy, which is impossible.",
                            "A product has units of volts squared, so it is not an energy per unit charge at all. It would also give zero work whenever either endpoint happened to sit at the zero of potential.",
                        ],
                    },
                    {
                        "prompt": "The field is minus the rate of change of the potential with respect to what?",
                        "hole": "?",
                        "opts": ["dx", "dt", "dq", "dA"],
                        "a": 0,
                        "why": "Position. The field is the *slope* of the potential across space, which is what makes V/m a unit of field: volts per metre is literally volts divided by metres of distance. The minus sign says the field points downhill.",
                        "whys": [
                            "Position. The field is the *slope* of the potential across space, which is what makes V/m a unit of field: volts per metre is literally volts divided by metres of distance. The minus sign says the field points downhill.",
                            "A rate of change with time would have units of volts per second, which is not a field. It is a real and important quantity — module 4 is largely about it — but it produces an induced voltage, not an electrostatic one.",
                            "Differentiating with respect to charge is meaningless here: the potential at a point does not depend on the charge you bring to probe it, which was the whole point of dividing that charge out.",
                            "Volts per square metre is not a unit of anything in this course. Area appears in flux, on the other side of the module.",
                        ],
                    },
                    {
                        "prompt": "The patch is tilted by an angle theta between the field and the patch's normal. What does that contribute to the flux?",
                        "hole": "?",
                        "opts": ["cos(theta)", "sin(theta)", "tan(theta)", "theta"],
                        "a": 0,
                        "why": "Only the component of the field along the normal crosses the patch, and that component is $E\\cos\\theta$. Square-on ($\\theta = 0$) gives the full $EA$; edge-on ($\\theta = 90°$) gives nothing, exactly as a window turned edge-on to falling rain catches none of it.",
                        "whys": [
                            "Only the component of the field along the normal crosses the patch, and that component is $E\\cos\\theta$. Square-on ($\\theta = 0$) gives the full $EA$; edge-on ($\\theta = 90°$) gives nothing, exactly as a window turned edge-on to falling rain catches none of it.",
                            "A sine gets the two extremes exactly backwards: it would give zero flux through a patch held square-on to the field, and maximum flux through one held edge-on. The temptation comes from measuring theta from the surface instead of from its normal, which is why the definition insists on the normal.",
                            "A tangent runs off to infinity at 90°, so an edge-on patch would carry infinite flux. Any expression that can exceed $EA$ is wrong, because $EA$ is what crosses when the patch faces the field squarely.",
                            "The bare angle is not dimensionless in the way this needs — the flux would depend on whether theta was measured in degrees or radians, and no physical quantity may do that.",
                        ],
                    },
                    {
                        "prompt": "In Gauss's law, what is the enclosed charge divided by?",
                        "hole": "?",
                        "opts": ["eps0", "4*pi*eps0", "mu0", "eps0 * A"],
                        "a": 0,
                        "why": "$\\varepsilon_0$ alone. The $4\\pi$ that lives inside the Coulomb constant is exactly cancelled by the $4\\pi r^2$ of the sphere used to derive the law, which is why $k = 1/(4\\pi\\varepsilon_0)$ is written that way in the first place.",
                        "whys": [
                            "$\\varepsilon_0$ alone. The $4\\pi$ that lives inside the Coulomb constant is exactly cancelled by the $4\\pi r^2$ of the sphere used to derive the law, which is why $k = 1/(4\\pi\\varepsilon_0)$ is written that way in the first place.",
                            "This is the $4\\pi$ being counted twice. It came in with $k$ and went out with the surface area of the sphere; putting it back leaves the flux out of a sphere around a 1 nC charge at 9.0 V·m instead of the correct 113 V·m.",
                            "$\\mu_0$ is the magnetic partner constant and belongs to module 4 onwards. Gauss's law for the electric field contains no magnetic quantity at all.",
                            "Dividing by an area as well would make the right-hand side a field rather than a flux, and would reintroduce the dependence on the size of the surface that the law exists to remove. The flux out of a closed surface does not care how big the surface is.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "The volts a nanocoulomb puts on a point",
                    "minutes": 5,
                    "brief": r'''
The mechanical case: one rule, one unknown, everything given. The only thing this can
catch you on is the exponent, and the exponent is the whole difference between this
module and the previous one.
''',
                    "prompt": "What is the electric potential at the point P, 30.0 cm from the sphere?",
                    "note": "Give the answer in volts, to the nearest volt. Take the potential to be zero infinitely far away.",
                    "figure": r'''
```text
   an isolated charged sphere in dry air, nothing else within metres

        ( +25.0 nC )  . . . . . . . . . . . . . . . .  P
                      |<--------- 30.0 cm --------->|

   the sphere is small enough to count as a point charge
```
''',
                    "given": [
                        {"label": "Charge on the sphere", "value": "+25.0 nC"},
                        {"label": "Distance to P", "value": "30.0 cm"},
                        {"label": "Coulomb constant", "value": "8.988 × 10⁹ N m² C⁻²"},
                    ],
                    "aside": "$V = kQ/r$ — a single power of $r$, against $r^2$ for the field. Convert the "
                             "30.0 cm to metres, then divide once.",
                    "answer": 749.0,
                    "tol": 5.0,
                    "unit": "V",
                    "hint": "$kQ = 8.988\\times10^{9} \\times 25.0\\times10^{-9} = 224.7$ V·m. Divide that "
                            "by 0.300 m.",
                    "wrong": "If you got 2497, the distance was squared — that is $kQ/r^2$, which is the "
                             "field in volts per metre, not the potential in volts. If you got 7.49, the "
                             "30.0 went in as centimetres.",
                    "why": r'''
$$V = \frac{kQ}{r} = \frac{8.988\times10^{9} \times 25.0\times10^{-9}}{0.300}
     = \frac{224.7}{0.300} = 749\ \mathrm{V}$$

Seven hundred and fifty volts, a third of a metre away from a charge far too small to
weigh. It is not a dangerous voltage in the way a mains socket is, and the reason is that
a voltage says nothing on its own about how much charge stands behind it. Here the whole
supply is 25 nC, and a socket delivering one amp moves that much charge every 25
nanoseconds, all day.

Two comparisons make the exponent concrete. The field at the same point is
$kQ/r^2 = 224.7/0.0900 = 2497$ V/m, and the ratio of the two is exactly the distance:
$V = Er$ holds for a point charge, though only because both fall as powers of the same
$r$. And move out to 60.0 cm: the field drops to a quarter, 624 V/m, while the potential
drops only to a half, 375 V. The potential reaches further, and that is the general rule.
''',
                },
                {
                    "title": "How fast does the proton arrive?",
                    "minutes": 7,
                    "brief": r'''
Two rules chained: the work a potential difference does on a charge, and what kinetic
energy that work becomes. Nothing about the geometry of the gap matters, which is the
part worth noticing — the answer would be identical for a gap of 1 mm or 1 m, straight
or curved, as long as the 1.20 kV is the same.
''',
                    "prompt": "How fast is the proton moving when it reaches the right-hand plate?",
                    "note": "Give the answer in kilometres per second, to three significant figures.",
                    "figure": r'''
```text
   a proton released from rest at the positive plate of an evacuated gap

     +1200 V                                              0 V
        |                                                  |
        |   (p+)  - - - - - - - - - - - - - - - ->         |
        |   at rest                          arrives here  |
        |                                                  |
      plate                                              plate

   vacuum between the plates; gravity and collisions both negligible
```
''',
                    "given": [
                        {"label": "Potential difference crossed", "value": "1.20 kV"},
                        {"label": "Charge on the proton", "value": "+1.602 × 10⁻¹⁹ C"},
                        {"label": "Mass of the proton", "value": "1.673 × 10⁻²⁷ kg"},
                        {"label": "Starting speed", "value": "0 (released from rest)"},
                    ],
                    "aside": "The work the field does is $qV$, and with nothing to lose it to, all of it "
                             "becomes $\\tfrac{1}{2}mv^2$. Solve for $v$, and keep the factor of 2.",
                    "answer": 479.5,
                    "tol": 4.0,
                    "unit": "km/s",
                    "hint": "$W = qV = 1.602\\times10^{-19} \\times 1200 = 1.923\\times10^{-16}$ J. Then "
                            "$v = \\sqrt{2W/m}$, and the answer is in metres per second before you convert.",
                    "wrong": "If you got 339, the factor of 2 was left out of $v = \\sqrt{2W/m}$. If you "
                             "got about 20 500, the electron mass was used instead of the proton's — and "
                             "that answer is also 7 % of the speed of light, which is a useful warning "
                             "sign in itself.",
                    "why": r'''
The proton starts at $+1200$ V and finishes at 0 V, so it moves *downhill* by 1200 V and
the field does positive work on it:

```text
W = q V = 1.602e-19 C * 1200 V                    = 1.923e-16 J

that all becomes kinetic energy:

(1/2) m v^2 = 1.923e-16
v^2 = 2 * 1.923e-16 / 1.673e-27                   = 2.299e11 m^2/s^2
v   = sqrt(2.299e11)                              = 4.795e5 m/s   = 479 km/s
```

Four hundred and eighty kilometres per second, and it is worth pausing on how ordinary
the input was: 1.2 kV is a small bench supply. The reason is the mass — a proton weighs
$1.7\times10^{-27}$ kg, so there is very little to accelerate.

Two remarks. The energy is more usefully quoted as 1.2 keV, which is the same statement
with the $1.602\times10^{-19}$ left off; particle physics is written in those units for
exactly this reason. And run the identical calculation for an electron, 1836 times
lighter, and it arrives at $2.05\times10^{7}$ m/s — nearly 7 % of the speed of light out
of the same 1.2 kV. That is why a cathode-ray tube runs at a few kilovolts and a proton
accelerator has to be a building.
''',
                },
                {
                    "title": "Carrying a charge across a two-source field",
                    "minutes": 9,
                    "brief": r'''
The potential picture doing the job it exists for. Two source charges, one of them
negative, and a charge carried between two points that are not specially placed. Four
terms of $kQ/r$, two subtractions, one multiplication — and no components anywhere.

Do it with fields instead and you would need the direction of the force at every point
along the path and an integral of the component along the motion. The route is not even
given here, and it does not need to be.
''',
                    "prompt": "How much work does the electric field do on the +3.0 nC charge as it is carried from A to B?",
                    "note": "Give the answer in microjoules, to three significant figures. A positive answer means the field does work on the charge.",
                    "figure": r'''
```text
   two fixed source charges on a line, and a third charge carried from A to B

    q1 = +6.0 nC          A                    B          q2 = -2.0 nC
       ( + )-------------(A)------------------(B)------------( - )
       |                  |                    |                |
       0                10.0 cm             30.0 cm          40.0 cm

   the carried charge is +3.0 nC; the path it takes from A to B is not specified
```
''',
                    "given": [
                        {"label": "q1, at x = 0", "value": "+6.0 nC"},
                        {"label": "q2, at x = 40.0 cm", "value": "−2.0 nC"},
                        {"label": "Charge carried", "value": "+3.0 nC"},
                        {"label": "A, B", "value": "x = 10.0 cm and x = 30.0 cm"},
                    ],
                    "aside": "$W_{\\text{field}} = q(V_A - V_B)$. Work out $V_A$ as $kq_1/r_1 + kq_2/r_2$ "
                             "with the distances measured from A, then $V_B$ the same way, then subtract "
                             "— in that order, start minus finish.",
                    "answer": 1.438,
                    "tol": 0.02,
                    "unit": "µJ",
                    "hint": "From A the two distances are 0.100 m and 0.300 m; from B they are 0.300 m and "
                            "0.100 m. Keep the minus sign on the 2.0 nC charge in both potentials.",
                    "wrong": "If you got 0.719, the minus sign on $q_2$ was dropped: a negative charge "
                             "lowers the potential around it, and the sign is the only thing distinguishing "
                             "a hill from a valley. If you got −1.44, the subtraction went the wrong way "
                             "round — $V_B - V_A$ is the work *you* would do, not the work the field does.",
                    "why": r'''
Potentials first, adding the two contributions as plain signed numbers.

```text
at A (x = 10.0 cm):   0.100 m from q1,  0.300 m from q2

  V_A = 8.988e9 * 6.0e-9 / 0.100  +  8.988e9 * (-2.0e-9) / 0.300
      =  53.928 / 0.100           +  (-17.976) / 0.300
      =  539.28 V                 +  (-59.92 V)             = 479.36 V

at B (x = 30.0 cm):   0.300 m from q1,  0.100 m from q2

  V_B = 53.928 / 0.300            +  (-17.976) / 0.100
      =  179.76 V                 +  (-179.76 V)            =   0.00 V
```

$V_B$ is exactly zero, and not by accident: $6.0/0.300$ and $2.0/0.100$ are both 20, so
the hill and the valley cancel there precisely. The work follows:

$$W = q(V_A - V_B) = 3.0\times10^{-9} \times (479.36 - 0) = 1.438\times10^{-6}\ \mathrm{J}$$

which is **1.44 µJ**, done *by* the field, because a positive charge has moved from a
higher potential to a lower one.

Now look again at point B. Its potential is zero and its field is emphatically not: the
6.0 nC charge pushes with $53.928/0.300^2 = 599$ V/m and the $-2.0$ nC charge pulls with
$17.976/0.100^2 = 1798$ V/m, both in the same direction, for a total of 2397 V/m. A
charge released at B would accelerate hard. Zero potential means the *work to get there*
is zero, not that nothing is happening there — and that distinction is the one this
module exists to install.
''',
                },
                {
                    "title": "The field beside a charged wire",
                    "minutes": 8,
                    "brief": r'''
The first question in this module you cannot answer by adding up point charges — not
without an integral, anyway. The wire is long, the charge on it is spread evenly, and
the symmetry is exactly the kind Gauss's law was built to exploit.

Draw a cylinder round the wire and ask what crosses each part of it. The two flat ends
are the part people get wrong, so decide about them before you compute anything.
''',
                    "prompt": "What is the magnitude of the electric field 8.0 cm from the axis of the wire?",
                    "note": "Give the answer in kilovolts per metre, to three significant figures.",
                    "figure": r'''
```text
   a long straight wire, charge spread evenly along it at 45 nC per metre

   ====================================================================>  wire
                              |
                              |  8.0 cm
                              |
                              *  the point where the field is wanted

   the Gaussian surface to use: a cylinder of radius r and length L,
   coaxial with the wire

              +-------------------------------+
   ===========|===============================|===========>
              +-------------------------------+
              |<------------ L -------------->|
```
''',
                    "given": [
                        {"label": "Charge per unit length", "value": "45 nC/m"},
                        {"label": "Distance from the axis", "value": "8.0 cm"},
                        {"label": "Permittivity of free space", "value": "8.854 × 10⁻¹² F/m"},
                        {"label": "Coulomb constant", "value": "8.988 × 10⁹ N m² C⁻²"},
                    ],
                    "aside": "On the end caps the field is parallel to the surface, so they carry no flux "
                             "at all. That leaves the curved side, area $2\\pi r L$, with the field "
                             "perpendicular to it and the same size everywhere: $E(2\\pi r L) = \\lambda "
                             "L/\\varepsilon_0$, and $L$ cancels.",
                    "answer": 10.11,
                    "tol": 0.15,
                    "unit": "kV/m",
                    "hint": "$E = \\lambda/(2\\pi\\varepsilon_0 r)$, which is the same as $2k\\lambda/r$. "
                            "$2k\\lambda = 2 \\times 8.988\\times10^{9} \\times 45\\times10^{-9} = 808.9$.",
                    "wrong": "If you got 126, the distance was squared: a line does not fall off as "
                             "$1/r^2$, because backing away from it gains you no extra length of wire. If "
                             "you got 5.06, the factor of two is missing — the cylinder's area is $2\\pi r "
                             "L$, and writing $\\lambda/(2\\pi\\varepsilon_0 r)$ in terms of $k$ gives "
                             "$2k\\lambda/r$, not $k\\lambda/r$.",
                    "why": r'''
Symmetry first, because it is what licenses everything else. The field can only point
straight out from the wire — nothing in the arrangement distinguishes one direction along
the wire from the other — and its size can depend only on the distance from the axis. So
on the curved side of a coaxial cylinder, $E$ is constant and perpendicular to the
surface; on the two end caps it lies flat in the surface and contributes nothing.

```text
flux out of the cylinder    = E * (2 pi r L)     ends contribute 0
charge enclosed             = lambda * L

E * 2 pi r L = lambda L / eps0                   L cancels from both sides

E = lambda / (2 pi eps0 r) = 2 k lambda / r

2 k lambda = 2 * 8.988e9 * 45e-9                 = 808.9
E          = 808.9 / 0.080                       = 1.011e4 V/m   = 10.1 kV/m
```

The $L$ cancelling is what "long" bought us: the answer never had to know the length of
the wire, only that it is much longer than 8 cm.

The falloff is the thing to take away. Move out to 16 cm and the field halves, to 5.06
kV/m — it does not quarter. A point charge spreads its influence over a sphere whose
area grows as $r^2$; a line spreads it over a cylinder whose area grows only as $r$,
because the cylinder gains no length as it widens. The same counting argument gives a
charged plane a field that does not fall off with distance at all.
''',
                },
                {
                    "title": "Inside a rod that is charged all the way through",
                    "minutes": 12,
                    "brief": r'''
The hardest of these, and the one where the given quantity is deliberately not the one
you want. Nobody hands you a charge here: the rod carries a charge *density*, spread
through its volume, and the field point is inside the material rather than outside it.

Two things have to be got right, and they are the same two every Gauss's law problem
turns on. Which surface, and — much more often the mistake — how much charge that
surface actually encloses.
''',
                    "prompt": "What is the magnitude of the electric field 1.5 mm from the axis, inside the material of the rod?",
                    "note": "Give the answer in kilovolts per metre, to the nearest kilovolt per metre.",
                    "figure": r'''
```text
   cross-section of a long plastic rod, charge spread uniformly
   through its whole volume at rho = 1.2 mC per cubic metre

                     . . . . . . . . . .
                 . '                     ' .
              .        + + + + + + + +        .
            .        + + + + + + + + + +        .
           .        + + + + * + + + + + +        .     * = the field point,
           .        + + + + | + + + + + +        .         1.5 mm from the axis
            .        + + +  |  + + + + +        .
              .         + + | + + + +        .
                 ' .        |          . '
                     . . . .|. . . . .
                       axis -+
                            |<-- 1.5 mm -->*
           |<---------------- 3.0 mm ------------>|   rod radius a

   the rod is metres long; treat it as infinite
```
''',
                    "given": [
                        {"label": "Volume charge density", "value": "1.2 mC/m³"},
                        {"label": "Radius of the rod", "value": "3.0 mm"},
                        {"label": "Distance of the point from the axis", "value": "1.5 mm"},
                        {"label": "Permittivity of free space", "value": "8.854 × 10⁻¹² F/m"},
                    ],
                    "aside": "Take a cylinder of radius 1.5 mm and length $L$, sitting entirely inside the "
                             "material. Its enclosed charge is $\\rho$ times *its own* volume, "
                             "$\\pi r^2 L$ — not $\\rho$ times the whole rod's volume. Then divide the "
                             "flux by the curved area $2\\pi r L$ as before.",
                    "answer": 101.6,
                    "tol": 1.5,
                    "unit": "kV/m",
                    "hint": "Per metre of rod, $Q_{\\text{enc}} = \\rho\\pi r^2 = 1.2\\times10^{-3} \\times "
                            "\\pi \\times (1.5\\times10^{-3})^2 = 8.48\\times10^{-9}$ C, and the curved "
                            "area is $2\\pi r = 9.42\\times10^{-3}$ m². $E = Q_{\\text{enc}}/(\\varepsilon_0 "
                            "\\times \\text{area})$.",
                    "wrong": "If you got 407, the whole rod's charge per metre was used — but a cylinder of "
                             "half the rod's radius contains only a quarter of its cross-section, so that "
                             "answer is four times too big. If you got 203, the field was evaluated at the "
                             "rod's surface rather than half-way in.",
                    "why": r'''
The Gaussian surface is a cylinder of radius $r = 1.5$ mm and length $L$, lying entirely
inside the plastic. As before the end caps carry no flux and the curved side carries all
of it. The one new step is the enclosed charge, which is the density times the volume of
the *Gaussian* cylinder, not of the rod:

```text
take L = 1.0 m for convenience; it cancels anyway

Q_enc = rho * pi * r^2 * L
      = 1.2e-3 * pi * (1.5e-3)^2 * 1.0
      = 1.2e-3 * 7.069e-6                         = 8.482e-9 C

curved area = 2 pi r L = 2 pi * 1.5e-3 * 1.0      = 9.425e-3 m^2

E = Q_enc / (eps0 * area)
  = 8.482e-9 / (8.854e-12 * 9.425e-3)
  = 8.482e-9 / 8.345e-14                          = 1.016e5 V/m  = 102 kV/m
```

Tidied up, the algebra says $E = \rho r/(2\varepsilon_0)$ — the field inside a uniformly
charged rod rises **linearly** from zero on the axis. The $r^2$ of the enclosed charge
beats the $r$ of the area by exactly one power, and that is the whole result.

The linearity gives you two free checks. At the surface, $r = a = 3.0$ mm, the same
expression gives 203 kV/m, exactly twice the answer — half the radius, half the field.
And that surface value has to agree with the outside formula: the whole rod carries
$\lambda = \rho\pi a^2 = 1.2\times10^{-3} \times \pi \times (3.0\times10^{-3})^2 =
33.9$ nC/m, and $2k\lambda/a = 2 \times 8.988\times10^{9} \times 33.9\times10^{-9}/0.0030
= 203$ kV/m. The two pictures meet at the boundary, as they must.

Using that $\lambda$ at $r = 1.5$ mm instead — $2k\lambda/r = 407$ kV/m — is the trap,
and it is worth naming why it is tempting: the formula is correct, and the number 33.9
nC/m is a real property of the rod. It is just that *outside* the enclosed charge is all
of $\lambda$ and *inside* it is only the fraction $r^2/a^2$ of it, which at half the
radius is a quarter. Gauss's law never mentions the charge that lies outside the
surface, and here three quarters of the rod does.
''',
                },
            ],
            "quiz": {
                "title": "Potential and Gauss's law, checked",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A charge $+q$ sits at $(-d, 0)$ and a charge $-q$ at $(+d, 0)$. What is true at the midpoint?",
                        "opts": [
                            "Both the potential and the field are zero",
                            "The potential is zero but the field is not",
                            "The field is zero but the potential is not",
                            "Neither is zero",
                        ],
                        "a": 1,
                        "why": (
                            "Potentials are plain numbers and add: $kq/d + k(-q)/d = 0$. Fields are vectors, and "
                            "here both point the same way — away from the positive charge and towards the "
                            "negative one — so they add up to twice one of them rather than cancelling. Zero "
                            "potential never implies zero field; it is the *slope* of the potential that gives "
                            "the field, and a function can pass through zero on a steep slope."
                        ),
                    },
                    {
                        "q": "You carry a charge from A to B through an electric field, once along a straight line and once by a long meandering path. Compare the work done by the field.",
                        "opts": [
                            "The straight path does less work",
                            "The long path does more work, because it is longer",
                            "The work is the same for both",
                            "It depends on how fast you move the charge",
                        ],
                        "a": 2,
                        "why": (
                            "The work done by the electrostatic field is $q(V_A - V_B)$ — endpoint values only, "
                            "with the path nowhere in the expression. That is precisely what makes a *potential* "
                            "definable at all. The intuition that a longer path costs more comes from friction, "
                            "which is not a conservative force; an electrostatic field is."
                        ),
                    },
                    {
                        "q": "A point charge $q$ sits at the centre of an imaginary sphere of radius $r$. You double the radius. What happens to the total electric flux out of the sphere?",
                        "opts": [
                            "It falls to a quarter",
                            "It halves",
                            "It stays the same",
                            "It quadruples",
                        ],
                        "a": 2,
                        "why": (
                            "The field weakens as $1/r^2$ but the surface area grows as $r^2$, and flux is field "
                            "times area, so the two changes cancel exactly. Gauss's law states the result "
                            "directly: the flux is $q/\\varepsilon_0$, which mentions only the enclosed charge. "
                            "Answering a quarter is reading the $1/r^2$ of the field and forgetting the area."
                        ),
                    },
                    {
                        "q": "A charged sphere sits just *outside* a closed imaginary surface. What is the net flux through that surface?",
                        "opts": [
                            "Zero",
                            "Non-zero, since the field from the sphere certainly passes through the surface",
                            "Zero only if the surface is a sphere too",
                            "Half of $q/\\varepsilon_0$",
                        ],
                        "a": 0,
                        "why": (
                            "Field lines from an outside charge enter the surface on one side and leave on the "
                            "other, so every line contributes once negatively and once positively and the *net* "
                            "flux is zero. The field is definitely non-zero everywhere on the surface — Gauss's "
                            "law is about the net count of lines crossing, not about whether a field is present."
                        ),
                    },
                    {
                        "q": "What is the electric field inside a hollow metal box that carries a static charge on its surface, with nothing inside it?",
                        "opts": [
                            "Zero everywhere inside",
                            "Uniform and equal to the field just outside",
                            "Strongest at the centre",
                            "It points from the walls towards the centre",
                        ],
                        "a": 0,
                        "why": (
                            "Take any closed surface inside the cavity: it encloses no charge, so the net flux is "
                            "zero, and since the charges on a conductor have arranged themselves so that no field "
                            "remains in the metal, there is nothing left to make a field in the cavity either. "
                            "This is the Faraday cage, and it is why a car is a reasonable place to be in a "
                            "thunderstorm."
                        ),
                    },
                    {
                        "q": "In a region the potential is a constant 12 V everywhere. What is the electric field there?",
                        "opts": [
                            "12 V/m, pointing in the direction of decreasing potential",
                            "Zero",
                            "12 V/m, pointing in the direction of increasing potential",
                            "Undefined without knowing the charges",
                        ],
                        "a": 1,
                        "why": (
                            "The field is the *rate of change* of potential with position, $E = -\\mathrm{d}V/"
                            "\\mathrm{d}x$, so a flat potential means no field. The number 12 is a red herring, "
                            "and a useful one: the zero of potential is a choice you make, and adding 12 V to "
                            "everything everywhere changes no measurable quantity at all."
                        ),
                    },
                ],
            },
            "lab": {
                "title": "Potential, work and flux",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Three short functions, on the same list-of-charges representation as module 1.

`potential_at(charges, point)` returns the potential in volts: add $kq/r$ for every
charge. One number out, not an array — no directions are involved.

`work_done(q, charges, start, end)` returns the work in joules that the field does on
a charge `q` carried from `start` to `end`. That is $q(V_{\text{start}} -
V_{\text{end}})$, and the path never enters into it.

`flux_through_sphere(charges, centre, radius)` returns the electric flux out of an
imaginary sphere, in V·m. Do **not** integrate anything. Gauss's law says the answer
is the enclosed charge divided by $\varepsilon_0$, so the entire job is deciding which
charges are inside — distance from the centre strictly less than the radius.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

EPS0 = 8.8541878128e-12
K = 1.0 / (4.0 * np.pi * EPS0)


def potential_at(charges, point):
    """Electric potential at `point`, in volts. A single number."""
    point = np.asarray(point, dtype=float)
    # TODO: add K*q/r for every charge.
    return 0.0


def work_done(q, charges, start, end):
    """Work in joules done by the field on charge `q` carried from `start` to `end`."""
    # TODO: endpoints only.
    return 0.0


def flux_through_sphere(charges, centre, radius):
    """Electric flux out of a sphere, in V*m, by Gauss's law."""
    centre = np.asarray(centre, dtype=float)
    # TODO: total the charge strictly inside, then divide by EPS0.
    return 0.0


if __name__ == "__main__":
    one = [(1e-9, 0.0, 0.0)]
    print("potential 10 cm from 1 nC:", potential_at(one, (0.1, 0.0)), "V")
    print("flux out of a 5 cm sphere around it:",
          flux_through_sphere(one, (0.0, 0.0), 0.05), "V m")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

EPS0 = 8.8541878128e-12
K = 1.0 / (4.0 * np.pi * EPS0)


def potential_at(charges, point):
    """Electric potential at `point`, in volts. A single number."""
    point = np.asarray(point, dtype=float)
    total = 0.0
    for q, sx, sy in charges:
        r = float(np.hypot(point[0] - sx, point[1] - sy))
        if r == 0.0:
            continue
        total += K * q / r
    return float(total)


def work_done(q, charges, start, end):
    """Work in joules done by the field on charge `q` carried from `start` to `end`."""
    return float(q * (potential_at(charges, start) - potential_at(charges, end)))


def flux_through_sphere(charges, centre, radius):
    """Electric flux out of a sphere, in V*m, by Gauss's law."""
    centre = np.asarray(centre, dtype=float)
    enclosed = 0.0
    for q, sx, sy in charges:
        r = float(np.hypot(sx - centre[0], sy - centre[1]))
        if r < radius:
            enclosed += q
    return float(enclosed / EPS0)


if __name__ == "__main__":
    one = [(1e-9, 0.0, 0.0)]
    print("potential 10 cm from 1 nC:", potential_at(one, (0.1, 0.0)), "V")
    print("flux out of a 5 cm sphere around it:",
          flux_through_sphere(one, (0.0, 0.0), 0.05), "V m")
'''}],
                "hints": [
                    "`potential_at` has no direction in it at all: accumulate a plain float, one `K * q / r` per charge.",
                    "`work_done` should call `potential_at` twice. If you find yourself writing a loop over a path, re-read the definition.",
                    "`flux_through_sphere` never touches the field. Total the charges whose distance from the centre is less than the radius, and divide by `EPS0`.",
                ],
                "tests": [
                    {"name": "the potential of a point charge falls as 1/r", "code": r'''
_v1 = potential_at([(1e-9, 0.0, 0.0)], (0.1, 0.0))
_v2 = potential_at([(1e-9, 0.0, 0.0)], (0.2, 0.0))
assert abs(_v1 - 89.87551792261172) < 1e-9, f"expected K*1e-9/0.1 = 89.8755 V, got {_v1!r}"
assert abs(_v1 / _v2 - 2.0) < 1e-9, \
    f"doubling the distance should halve the potential, got a ratio of {_v1 / _v2}"
'''},
                    {"name": "potentials add as numbers, so a dipole centre reads zero", "code": r'''
_v = potential_at([(2e-9, -0.05, 0.0), (-2e-9, 0.05, 0.0)], (0.0, 0.0))
assert abs(_v) < 1e-12, \
    f"equal and opposite charges give equal and opposite potentials at the midpoint, got {_v!r}"
_same = potential_at([(2e-9, -0.05, 0.0), (2e-9, 0.05, 0.0)], (0.0, 0.0))
assert abs(_same - 719.0041433808938) < 1e-9, \
    f"make both charges positive and the same sum gives 719.00 V, not zero, got {_same!r}"
'''},
                    {"name": "the potential of a negative charge is negative", "code": r'''
_v = potential_at([(-3e-9, 0.0, 0.0)], (0.15, 0.0))
assert _v < 0, f"a negative charge lowers the potential around it, got {_v!r}"
assert abs(_v + 179.75103584522343) < 1e-9, f"expected -179.751 V, got {_v!r}"
'''},
                    {"name": "the field does positive work pushing a charge away", "code": r'''
_w = work_done(1e-9, [(1e-9, 0.0, 0.0)], (0.1, 0.0), (0.2, 0.0))
assert _w > 0, "a positive charge moving away from a positive source is pushed, so the field does work on it"
assert abs(_w - 4.493775896130586e-08) < 1e-18, f"expected 4.4938e-08 J, got {_w!r}"
'''},
                    {"name": "work depends on the endpoints, not the direction of travel", "code": r'''
_there = work_done(2e-9, [(5e-9, 0.0, 0.0)], (0.1, 0.0), (0.3, 0.0))
_back = work_done(2e-9, [(5e-9, 0.0, 0.0)], (0.3, 0.0), (0.1, 0.0))
assert abs(_there - 5.991701194840781e-07) < 1e-17, \
    f"expected 5.9917e-07 J moving out from 10 cm to 30 cm, got {_there!r}"
assert abs(_there + _back) < 1e-20, \
    f"going and returning must cancel exactly, got {_there!r} and {_back!r}"
'''},
                    {"name": "flux counts the enclosed charge and nothing else", "code": r'''
_inside = flux_through_sphere([(1e-9, 0.0, 0.0)], (0.0, 0.0), 0.05)
assert abs(_inside - 112.94090673730192) < 1e-9, f"expected 1 nC / EPS0 = 112.94 V m, got {_inside!r}"
_outside = flux_through_sphere([(1e-9, 0.5, 0.0)], (0.0, 0.0), 0.05)
assert abs(_outside) < 1e-12, \
    f"a charge outside the surface contributes no net flux, got {_outside!r}"
'''},
                    {"name": "flux does not care about the size of the surface", "code": r'''
_small = flux_through_sphere([(4e-9, 0.0, 0.0), (-1e-9, 0.02, 0.0)], (0.0, 0.0), 0.05)
_big = flux_through_sphere([(4e-9, 0.0, 0.0), (-1e-9, 0.02, 0.0)], (0.0, 0.0), 0.40)
assert abs(_small - _big) < 1e-9, \
    "both spheres enclose the same 3 nC, so both must report the same flux"
assert abs(_small - 338.82272021190574) < 1e-9, f"expected 3 nC / EPS0 = 338.82 V m, got {_small!r}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Capacitance from geometry",
            "summary": "Two conductors, a gap, and a number in farads that you can compute from the dimensions alone.",
            "concepts": [
                "Put charge $+Q$ on one conductor and $-Q$ on another and a potential difference $V$ appears between them. The ratio $C = Q/V$ is the capacitance, in farads, and it depends only on the geometry and the material in the gap.",
                "Parallel plates of area $A$ separated by $d$: the field between them is uniform, $V = Ed$, and $C = \\varepsilon_0 A / d$. Wider plates hold more charge at the same voltage; a wider gap holds less.",
                "A dielectric — an insulator that polarises — multiplies the capacitance by its relative permittivity $\\varepsilon_r$, which is 1 for vacuum and around 4 for glass.",
                "Capacitors in parallel add ($C = C_1 + C_2$); in series their reciprocals add, so the total is smaller than the smallest one.",
                "The energy stored is $\\tfrac{1}{2}CV^2$, and it lives in the field in the gap, not on the plates.",
                "Charging a capacitor through a resistor takes time: $\\tau = RC$ seconds, after which the capacitor has reached 63% of the supply voltage, and about 95% after $3\\tau$.",
            ],
            "read": [
                {
                    "title": "Two conductors, a gap, and one number in farads",
                    "minutes": 15,
                    "body": r'''
Take two pieces of metal that do not touch — two plates, two strips of foil, a wire and
the ground plane underneath it — and connect a battery across them. Electrons leave one
piece and arrive on the other. Nothing crosses the gap: the electrons that leave the
first plate travel the long way round, out through the battery, and land on the second.
When the movement stops, one piece carries $+Q$ and the other carries $-Q$, and standing
between them is the battery's voltage.

That is the whole experiment, and on its own it is not very interesting. What makes it
worth a name is what happens when you change the battery.

## The ratio that does not move

Swap the 3 V cell for a 6 V one and the charge doubles. Use 1.5 V and it halves. Use 9 V
and the charge is exactly three times what the 3 V cell moved — not roughly, not over
some limited range, but to whatever precision you care to measure it, for two conductors
of any shapes whatever.

The reason is that every equation in the first two modules is *linear* in the charge.
Coulomb's law is linear in each charge. The field of a collection of charges is the plain
sum of the fields each would produce alone. The potential difference between two points
is an integral of that field along a path. Multiply every charge in a problem by three
and every field triples, and every potential difference triples with it. There is no step
in the chain that can bend.

So the ratio of the charge to the voltage it produces is fixed by the shapes of the two
conductors, their positions, and what is in the space between them — and by nothing else.
That ratio deserves a symbol:

$$C = \frac{Q}{V}$$

Read the two letters carefully, because both are easy to misread. $Q$ is the charge on
*one* of the conductors, the other carrying $-Q$; the pair together holds no net charge
at all. And $V$ is the potential difference *between them*, not the potential of either
one measured against infinity. Capacitance is a property of a pair. Asking for the
capacitance of a single plate is like asking for the distance of a single point.

## The farad, and why every real value is a millionth of one

The unit is the coulomb per volt, named the **farad**. It is an absurd unit, in the sense
that almost nothing you will meet is within six orders of magnitude of it. Module 1 gave
the reason: a coulomb is a colossal amount of charge. Two 1 C point charges a metre apart
repel each other with $9\times10^{9}$ N, which is the weight of about a million tonnes. A
one-farad capacitor charged to one volt is holding one of those coulombs on each plate.

Real components are quoted in picofarads ($10^{-12}$), nanofarads ($10^{-9}$) and
microfarads ($10^{-6}$). A ball of metal the size of a football — 0.22 m across, so a
radius of 0.11 m — floating alone in space has a capacitance of about 12 pF, and that is
the whole of it. Every practical capacitor gets a usable number by putting two conductors
very close together instead.

## Two plates: getting the number out of the geometry

Now compute one. Two parallel plates of area $A$, a gap $d$, and $d$ much smaller than
the width of the plates.

The charge spreads itself over the two facing surfaces. Between the plates the field is
uniform and points from the positive plate to the negative one; outside, the fields of
the two sheets very nearly cancel, which is why a capacitor does not push charges around
the rest of the room.

To get the field, put a Gaussian pillbox through the positive plate's inner surface, with
one face inside the metal and one face in the gap. Inside a conductor at equilibrium the
field is zero — if it were not, the free charges would still be moving and it would not be
equilibrium — so no flux comes out of the buried face. All of it leaves through the face
in the gap. Gauss's law from module 2 then says

$$E A_{\text{box}} = \frac{\sigma A_{\text{box}}}{\varepsilon_0}
\qquad\Longrightarrow\qquad E = \frac{\sigma}{\varepsilon_0} = \frac{Q}{\varepsilon_0 A}$$

The field is uniform, so the potential difference is just field times distance:
$V = Ed = Qd/(\varepsilon_0 A)$. Divide:

$$C = \frac{Q}{V} = \frac{\varepsilon_0 A}{d}$$

Nothing was announced. Two facts — the field of a charged sheet, and that a uniform field
integrates to $Ed$ — and one division.

Read the result before using it. More area means more room to park charge at the same
field strength. A smaller gap means the same charge produces the same field but over a
shorter climb, so a smaller voltage, so more charge per volt. And note the power: this is
$1/d$, not $1/d^2$. The inverse square belongs to a point charge in three dimensions.
Between two plates the field does not fall off at all, and the gap changes only how far
you have to walk across it.

```text
C = eps0 * A / d          A in m^2, d in m, C in farads

eps0 = 8.854e-12 F/m      read that unit: FARADS PER METRE.
                          A capacitor with A/d = 1 m has a capacitance
                          of exactly eps0, which is 8.854 pF.
```

## Worked: a pair of plates you could actually build

Two square plates 100 mm on a side, held 0.10 mm apart with air between them.

```text
A   = 0.100 * 0.100                             = 1.00e-2 m^2
d   = 0.10 mm                                   = 1.0e-4 m
A/d = 1.00e-2 / 1.0e-4                          = 100 m

C   = 8.854e-12 * 100                           = 8.854e-10 F   = 885 pF

now put 100 V across it:
Q   = C V = 8.854e-10 * 100                     = 8.854e-8 C    = 88.5 nC
    in electrons: 8.854e-8 / 1.602e-19          = 5.5e11

and the field in the gap:
E   = V/d = 100 / 1.0e-4                        = 1.0e6 V/m     = 1.0 MV/m
```

Three numbers, three different reactions. 885 pF is *small* — the plates are the size of a
postcard and the part is worth less than a fingernail-sized ceramic chip. 88.5 nC is
unremarkable; module 1 was throwing microcoulombs about. But 1.0 MV/m is a third of the
way to the roughly 3 MV/m at which dry air stops insulating and the gap flashes over. That
is the real design tension in every capacitor: the gap is what buys you capacitance and
the gap is what limits your voltage, and squeezing it improves one at the direct expense
of the other.

## Worked: what a one-microfarad capacitor has to look like

Turn the formula round. To get $C = 1.00$ µF out of an air gap of 0.10 mm:

```text
A = C d / eps0 = 1.00e-6 * 1.0e-4 / 8.854e-12
  = 1.0e-10 / 8.854e-12                         = 11.3 m^2
```

Eleven square metres — a pair of plates 3.4 m on a side, for one microfarad. Nobody builds
that. There are only two ways out, and every real capacitor uses both: make $d$ far
smaller than any air gap can be, and put something in the gap that multiplies the answer.

Take a 2 µm polypropylene film, whose relative permittivity is 2.2:

```text
A = C d / (eps0 * eps_r) = 1.00e-6 * 2.0e-6 / (8.854e-12 * 2.2)
  = 2.0e-12 / 1.948e-11                         = 0.1027 m^2  = 1027 cm^2
```

A strip 50 mm wide and about 2.05 m long. Wound into a cylinder — and in a real winding
both faces of each foil face a neighbour, so the actual roll is about half that length —
it is a part roughly the size of a thumb joint. That is what a 1 µF film capacitor *is*,
and the whole of its design is contained in the two factors you just used: get $d$ down to
microns, and pick a material with an $\varepsilon_r$ worth having.

## What the dielectric is doing

An insulator in the gap does not conduct, and yet it changes the answer. The mechanism is
polarisation. Every molecule of the material either has a permanent dipole that can rotate
into line, or an electron cloud that shifts slightly against its nucleus when a field is
applied. In the bulk of the material these little dipoles sit head to tail and cancel, but
at the two faces there is nothing to cancel against, so a thin layer of *bound* charge
appears on each surface — negative on the face touching the positive plate, positive on
the face touching the negative one.

Those bound layers make a field of their own, opposing the plates' field. The net field in
the gap is therefore smaller, by the factor $\varepsilon_r$. Smaller field, same distance,
so smaller voltage; same charge over a smaller voltage, so a larger $C = Q/V$:

$$C = \frac{\varepsilon_0 \varepsilon_r A}{d}$$

```text
vacuum                    1
dry air                   1.0006      (which is why we ignore it)
polypropylene             2.2
paper, oiled              3 to 4
window glass              4 to 7
aluminium oxide           ~9          (the film in an electrolytic)
class-2 ceramic (X7R)     2000 to 4000
```

## Where the formula stops

**When the gap is not small.** $\varepsilon_0 A/d$ assumes the field is uniform right out to
the rim, and it is not: near the edges the lines bulge outwards. The size of the error
scales roughly with the ratio of the gap to the plate width. For 100 mm plates 0.10 mm
apart that is a part in a thousand and you will never see it. For two plates as far apart
as they are wide, the fringing is not a correction to the answer, it *is* the answer, and
the formula is worthless. The parallel-plate result is a limit, not a law.

**At the breakdown field.** Every dielectric has a field it cannot survive: about 3 MV/m
for air, around 10 MV/m for glass, several hundred for thin polymer films. The capacitance
formula knows nothing about this, and it is what sets the voltage rating on the part. A
capacitor that fails this way usually fails short.

**When $\varepsilon_r$ is not a constant.** The class-2 ceramics that reach the thousands do
it with a ferroelectric mechanism, and it is not stable: a 10 µF X5R part biased at its
rated voltage can measure under 3 µF, and its value moves with temperature as well. The
class-1 ceramics (C0G/NP0) have an $\varepsilon_r$ of only a few tens, and are used
wherever the value has to be trusted. Permittivity also falls with frequency, once the
dipoles can no longer turn round fast enough to keep up.

## The mistake people make

The commonest is to believe that charging a capacitor harder raises its capacitance. It is
a tempting thought, because you never meet a capacitor on its own — there is always
something connected, and putting more voltage across it visibly puts more charge on it, so
it does "hold more". It holds *proportionally* more, and that proportionality is exactly
what leaves the ratio untouched. Capacitance is the constant of proportionality, not the
charge. The way to test yourself is to notice that $C = \varepsilon_0 A/d$ contains no $Q$
and no $V$ at all: it was derived from the geometry, and the charge cancelled on the way.

The second is $1/d^2$ for $1/d$, dealt with above; it is worth a factor of a thousand if
the gap is in millimetres.

The third is to assume an insulator can do nothing because no current flows through it.
Capacitance was never about current. The dielectric's entire job is to sit still and be
polarised.
''',
                },
                {
                    "title": "Combining them, and where the energy actually sits",
                    "minutes": 15,
                    "body": r'''
The last unit produced one capacitor from its dimensions. A real board has dozens, and
they are wired to each other. Two rules cover every combination that can be reduced at
all, and both of them fall out of simple bookkeeping about where charge is allowed to go.
Both are also the opposite way round from the resistor rules you already know, which is
where nearly all of the mistakes come from.

## Side by side: the plates just got bigger

Two capacitors connected between the same pair of nodes necessarily hold the same voltage
$V$ — that is what being connected to the same two nodes means. Each takes the charge its
own capacitance demands:

$$Q_1 = C_1 V, \qquad Q_2 = C_2 V$$

and the total charge the supply had to move is $Q = Q_1 + Q_2 = (C_1 + C_2)V$. Divide by
$V$:

$$C_{\text{parallel}} = C_1 + C_2$$

There is a picture that makes this obvious rather than algebraic. Two capacitors side by
side, with their top plates wired together and their bottom plates wired together, is one
capacitor whose plate area is the sum of the two areas. And $\varepsilon_0 A/d$ is linear
in $A$. The parallel rule is not a new fact; it is the area rule, restated.

## One after the other: the gap just got wider

Now put two in a single branch, one above the other. Look hard at what sits between them:
the bottom plate of the upper capacitor, the top plate of the lower one, and the wire
joining them. That island is connected to nothing else in the circuit. Whatever net charge
it started with — zero — it still has. So if $-Q$ is induced on one of its plates, exactly
$+Q$ must appear on the other.

**Series capacitors carry identical charge**, whatever their values are, and that single
sentence is the whole derivation. The voltages, on the other hand, add as you walk down
the branch:

$$V = V_1 + V_2 = \frac{Q}{C_1} + \frac{Q}{C_2} = Q\left(\frac{1}{C_1} + \frac{1}{C_2}\right)$$

and since $V/Q$ is $1/C$,

$$\frac{1}{C_{\text{series}}} = \frac{1}{C_1} + \frac{1}{C_2}
\qquad\text{or}\qquad C_{\text{series}} = \frac{C_1 C_2}{C_1 + C_2}$$

Again there is a picture. Two *identical* capacitors in series is one capacitor with twice
the gap, because the middle island contributes no thickness of its own that matters — and
doubling $d$ halves $\varepsilon_0 A/d$. The reciprocals are the gap rule, restated.

Two consequences worth memorising. A series combination is always smaller than its
smallest member, so adding a capacitor in series can only ever reduce the capacitance.
And a lone capacitor in series with a signal path blocks DC completely, which is what a
coupling capacitor is for.

Why do the rules feel backwards? Because a resistance is $\rho L/A$ — it grows with length
and shrinks with area — while a capacitance is $\varepsilon_0 A/d$, which shrinks with
"length" (the gap) and grows with area. Capacitance behaves like a *conductance*, not like
a resistance. If you insist on writing everything in terms of $1/C$, the rules become
letter-for-letter identical to the resistor rules. The reciprocals in the series formula
are telling you exactly that.

## Worked: a series pair, and which one takes the voltage

A 2.20 µF and a 4.70 µF capacitor in series across a 9.00 V supply.

```text
1/C = 1/2.20 + 1/4.70                  per microfarad
    = 0.454545 + 0.212766              = 0.667311  per uF
C   = 1 / 0.667311                     = 1.4986 uF

the charge — the SAME on both, by the island argument:
Q   = C V = 1.4986e-6 * 9.00           = 1.3487e-5 C   = 13.49 uC

and the voltage that charge produces on each:
V1  = Q/C1 = 13.49 uC / 2.20 uF        = 6.130 V
V2  = Q/C2 = 13.49 uC / 4.70 uF        = 2.870 V
                                         ---------
                                         9.000 V    checks
```

The *smaller* capacitor takes the *larger* share of the voltage — 68% of it here — because
the same charge sitting on a smaller capacitance is a bigger voltage. This is the exact
opposite of the resistive divider, where the larger resistor takes the larger share, and
it is worth stopping on: the two dividers you now know split in opposite directions.

It also has a consequence you can see on any mains power supply board. Two electrolytics
in series across a high-voltage rail will not share it evenly, because the sharing is
actually settled by their leakage currents rather than their capacitances, and those match
even more poorly. So each one gets a balancing resistor across it, which forces the split
by brute force.

## The energy it took to put the charge there

A capacitor holding $Q$ at $V$ has *not* stored $QV$ joules. Watch the charging happen.
At the instant the capacitor already holds $q$, its voltage is $q/C$, and moving the next
$\mathrm{d}q$ across that voltage costs $\mathrm{d}W = (q/C)\,\mathrm{d}q$. Add up the
whole journey from empty:

$$W = \int_0^{Q} \frac{q}{C}\,\mathrm{d}q = \frac{Q^2}{2C} = \tfrac{1}{2}CV^2 = \tfrac{1}{2}QV$$

The factor of one half is the entire content of the result. The first coulomb goes on
free, because the capacitor starts at 0 V; the last one has to be pushed against the full
final voltage; and because the voltage rises in exact proportion to the charge already
there, the average cost is half the final one.

So where did the other half go? Charge a 1.00 µF capacitor to 5.00 V from a 5.00 V supply,
through a resistor:

```text
the supply pushes out Q = C V = 5.00 uC, and every coulomb of it
leaves at the full 5.00 V, because that is what a fixed supply does:

    W_supply    = Q V   = 5.00e-6 * 5.00        = 25.0 uJ
    W_capacitor = 0.5 C V^2 = 0.5*1e-6*25.0     = 12.5 uJ
    difference                                  = 12.5 uJ
```

Exactly half is dissipated in the resistor — and notice that $R$ does not appear anywhere
in that calculation. Make it 1 Ω and the resistor takes 12.5 µJ in one very short, very hot
moment. Make it 1 MΩ and it takes 12.5 µJ slowly. You cannot charge a capacitor from a
fixed voltage through a resistance at better than 50% efficiency, ever. Switching
converters exist largely to dodge this, by putting an inductor where the resistor was.

## Worked: the two-capacitor puzzle

This one is worth doing carefully, because it looks like a paradox and is not.

A 1.00 µF capacitor is charged to 10.0 V and then, by closing a switch, connected in
parallel with an identical 1.00 µF capacitor that is completely uncharged. What happens?

```text
before:
    Q = C V     = 1.00e-6 * 10.0                 = 10.0 uC
    W = 0.5 C V^2 = 0.5 * 1.00e-6 * 100          = 50.0 uJ

charge cannot go anywhere except onto the two plates, so it is
conserved, and it now sits across the parallel pair:

after:
    C_total = 1.00 + 1.00                        = 2.00 uF
    V = Q / C_total = 10.0 uC / 2.00 uF          = 5.00 V
    W = 0.5 * 2.00e-6 * 25.0                     = 25.0 uJ
```

Half the energy has disappeared, and no resistor was mentioned anywhere in the problem.
It goes into whatever resistance the connecting wire actually has; and if you idealise the
wire to zero resistance, it goes into the ringing of the wire's own inductance against the
two capacitors, which then radiates it away. There is no version of this experiment in
which the energy is conserved. That is the cleanest demonstration in the subject that
$\tfrac{1}{2}CV^2$ is a real physical quantity and the one half is not decoration.

## The energy is in the gap, not on the plates

Say *where* the 12.5 µJ is. Substitute the parallel-plate results $C = \varepsilon_0 A/d$
and $V = Ed$ into $\tfrac{1}{2}CV^2$:

$$W = \tfrac{1}{2}\frac{\varepsilon_0 A}{d}(Ed)^2 = \tfrac{1}{2}\varepsilon_0 E^2 (Ad)$$

and $Ad$ is precisely the volume of the gap. So the energy per cubic metre is

$$u = \tfrac{1}{2}\varepsilon_0 E^2$$

which mentions no plates, no area, no charge and no gap — only the field. That is the point.
The energy is a property of the field wherever the field is, and the plates were only ever
the machinery for making one. The derivation unit in this module walks you through those
substitutions yourself.

It is worth one number. Air gives up at about 3 MV/m, so the very most you can store in a
cubic metre of air is

```text
u = 0.5 * 8.854e-12 * (3.0e6)^2                  = 39.8 J/m^3
```

A lithium 18650 cell holds about 3 A·h at 3.6 V, which is 38.9 kJ, in a volume of
$1.65\times10^{-5}$ m³ — some $2.4\times10^{9}$ J/m³. The battery wins by a factor of about
sixty million. No dielectric closes a gap that size, and that is the honest reason a
capacitor is not a battery: it is a device for storing small amounts of energy and giving
them back extremely fast, which is a different job.

## The mistakes, and where the rules stop

The most expensive slip is using $\tfrac{1}{2}CV^2$ with the supply voltage for one member
of a series pair. In the worked example above the 4.70 µF holds

```text
0.5 * 4.70e-6 * 2.870^2                          = 19.4 uJ      (correct)
0.5 * 4.70e-6 * 9.00^2                           = 190  uJ      (ten times too big)
```

and the check is that the parts must sum to the whole: $19.4 + 41.3 = 60.7$ µJ, and
$\tfrac{1}{2}\times1.4986\ \mu\text{F}\times9.00^2 = 60.7$ µJ. Each capacitor gets its own
voltage.

The second is applying the parallel rule to a series pair — writing $2.20 + 4.70 = 6.90$ µF.
The symptom is easy to catch: a series answer that is *larger* than either capacitor, when
it must be smaller than both.

And the rules themselves stop when the capacitors stop being capacitors. Every real part
has a leakage resistance in parallel with it and a small series resistance (ESR) and series
inductance (ESL) in the leads and plates. Above its self-resonant frequency — a few tens of
megahertz for a typical electrolytic, a few hundred for a small ceramic — a capacitor's
impedance rises with frequency, which is inductor behaviour, and "capacitors in parallel
add" quietly stops being true. That is why a fast digital board carries a 10 µF, a 100 nF
and a 1 nF part in parallel on the same rail instead of one 10.101 µF part: they are not
being added, they are covering different decades.
''',
                },
                {
                    "title": "What a resistor does to it: RC and the time constant",
                    "minutes": 15,
                    "body": r'''
Connect a capacitor straight across a battery and, in the idealised circuit, it charges
instantly: infinite current for zero time. Put a resistor in the way and it takes time,
and the shape of that charging curve is one of the two or three curves this whole subject
runs on.

Start with the picture rather than the equation. A tank is being filled through a narrow
pipe from a header tank held at a fixed level. The flow through the pipe is proportional
to the *difference* in levels. So as the tank fills, the difference shrinks, so the flow
slows, so the filling slows — and the closer it gets, the more slowly it approaches. It
never quite arrives. That is the whole of what follows; everything else is arithmetic.

## Writing down what the circuit says

A supply $V$, a resistor $R$ and a capacitor $C$ in one loop. Call the voltage across the
capacitor $v$, and let it start at zero.

Two statements, neither of them new. Around the loop, the supply voltage is shared between
the resistor and the capacitor, so the resistor holds $V - v$ and the current through it is
$(V - v)/R$. And that same current flows into the capacitor, where it piles up as charge:
$i = \mathrm{d}q/\mathrm{d}t$, and since $q = Cv$ with $C$ constant, $i = C\,\mathrm{d}v/\mathrm{d}t$.

Set the two expressions for the current equal:

$$C\frac{\mathrm{d}v}{\mathrm{d}t} = \frac{V - v}{R}$$

Read that before solving it. *The rate at which the capacitor's voltage rises is
proportional to how far it still has to go.* It is the tank, in symbols.

## Solving it

Separate the variables and integrate from $v = 0$ at $t = 0$:

$$\frac{\mathrm{d}v}{V - v} = \frac{\mathrm{d}t}{RC}
\qquad\Longrightarrow\qquad
\ln\frac{V}{V - v} = \frac{t}{RC}$$

Exponentiate and rearrange:

$$V - v = V e^{-t/RC}
\qquad\Longrightarrow\qquad
v(t) = V\left(1 - e^{-t/RC}\right)$$

The product $RC$ sits where a time has to sit, and it is one. Check the units once, by
hand, because it is the fastest way to catch a slip of a thousand:

```text
ohms * farads = (volts/amp) * (coulombs/volt) = coulombs/amp = seconds
```

Give it a name: $\tau = RC$, the **time constant**.

## Reading the curve

```text
t              v/V = 1 - exp(-t/tau)
------------------------------------------
0.693 tau      0.500        half way
1    tau       0.632
2    tau       0.865
3    tau       0.950
5    tau       0.993
```

Two things to take from that table. Half way is at $0.693\tau$, not at $\tau/2$ — nothing
about an exponential divides evenly, because it is not a straight line. And each further
$\tau$ removes 63.2% of *what is left*, so the shortfalls run 0.368, 0.135, 0.050, 0.018,
0.007. The curve approaches and never crosses; there is no time at which it is "finished",
only a time at which it is close enough for the job.

There is a neat geometric reading of $\tau$ as well. At $t = 0$ the slope is
$\mathrm{d}v/\mathrm{d}t = V/RC$, so if the capacitor kept charging at its initial rate it
would arrive at exactly $t = \tau$. The time constant is where the initial tangent cuts the
final value.

Discharging is the same curve upside down. With the supply removed and the capacitor left
to empty through $R$, $v(t) = V_0 e^{-t/\tau}$, which is down to 36.8% after one time
constant.

## Worked: forwards, and then backwards

$R = 2.20$ kΩ, $C = 470$ nF, supply 5.00 V, capacitor starting empty.

```text
tau = R C = 2200 * 470e-9                       = 1.034e-3 s = 1.034 ms

FORWARDS — what is v at t = 1.50 ms?
    t/tau     = 1.50 / 1.034                    = 1.4507
    exp(-1.4507)                                = 0.23441
    v         = 5.00 * (1 - 0.23441)            = 3.828 V

BACKWARDS — when does v first reach 3.00 V?
    1 - v/V   = 1 - 3.00/5.00                   = 0.400
    t/tau     = ln(1/0.400) = ln 2.5            = 0.91629
    t         = 0.91629 * 1.034 ms              = 0.9474 ms
```

The backwards direction always needs a logarithm, and it is always the natural logarithm,
because the natural exponential is what came out of the integration. Reaching for
$\log_{10}$ here gives an answer 2.303 times too small, which is a distinctive enough
error to recognise on sight.

## The resistance is usually not the one you can see

$\tau = RC$ is correct, but $R$ in it is not "the resistor in the drawing". It is the
resistance the capacitor sees when it looks back into the rest of the circuit **with every
independent source turned off** — voltage sources replaced by plain wire, current sources
by breaks. That is the Thévenin resistance at the capacitor's terminals.

The justification is the loop equation again: what governs the decay is the total
resistance in the path along which charge can move on or off the plates, and if the
surrounding network is more than a single resistor you have to reduce it first. Turning a
voltage source into a short is not a trick — a source that holds its terminals at a fixed
voltage offers no opposition at all to a *change*, which is what the transient is made of.

The final value has to be found separately, and it is the plain DC answer with the
capacitor removed, because once nothing is changing no current flows into it.

## Worked: a divider with a capacitor hanging on it

A 9.00 V rail, a 4.70 kΩ resistor from the rail to a node, a 10.0 kΩ resistor from that
node to ground, and a 220 nF capacitor from the node to ground. The rail is switched on at
$t = 0$. Where does the node end up, and how long does it take to get 90% of the way there?

```text
FINAL VALUE — the capacitor passes no steady current, so it is
simply out of the picture and this is a plain divider:

    V_f  = 9.00 * 10.0 / (4.70 + 10.0)           = 6.122 V

THE RESISTANCE the capacitor looks back into, with the 9 V rail
replaced by a short (which puts the two resistors in parallel):

    R_th = (4.70 * 10.0) / (4.70 + 10.0)  kohm   = 3.197 kohm

    tau  = 3.197e3 * 220e-9                      = 7.034e-4 s = 703.4 us

90% OF THE WAY:

    t    = tau * ln(10) = 703.4 us * 2.3026      = 1.620 ms
```

Compare the two wrong answers, because both are common and both are slow. Using the
4.70 kΩ alone gives $\tau = 1.034$ ms, 47% too long. Using the two added together gives
3.234 ms, four and a half times too long. The parallel combination is smaller than either
resistor, so the true circuit is *faster* than either mistake suggests — the extra resistor
to ground gives the charge a second route on and off the plate.

## The same circuit, described by frequency instead

Feed the same $R$ and $C$ a sine wave rather than a step. At low frequency the capacitor
has plenty of time to follow the input and the output tracks it. At high frequency the
input reverses before much charge has moved, and the output barely stirs. The crossover
happens where the capacitor's reactance $1/(2\pi f C)$ is equal to $R$:

$$f_c = \frac{1}{2\pi RC} = \frac{1}{2\pi\tau}$$

At $f_c$ the output is $1/\sqrt{2} = 0.707$ of the input. That ratio is normally quoted on a
logarithmic scale: a size ratio $g$ is $20\log_{10} g$ **decibels**, so $g = 1$ is 0 dB,
$g = 0.707$ is $-3.01$ dB, $g = 0.1$ is $-20$ dB and $g = 0.01$ is $-40$ dB. The decibel is
a change of units and nothing more, but it is the unit filters are quoted in, and $f_c$ is
universally called the $-3$ dB point, or the corner.

```text
tau = 1.034 ms   ->   f_c = 1/(2*pi*1.034e-3)    = 153.9 Hz
tau = 703.4 us   ->   f_c = 1/(2*pi*7.034e-4)    = 226.3 Hz
```

Above the corner the output falls by a factor of ten for every factor of ten in frequency —
$-20$ dB per decade, which is the steepest fall a circuit containing a single capacitor can
produce. And nothing new has been measured here: $\tau$ and $f_c$ are one fact wearing two
sets of units, related by $2\pi$. A circuit that takes a millisecond to settle cannot also
be quick in the frequency domain, and one designed to reject 50 Hz hum will unavoidably be
slow.

## Where this stops, and what people get wrong

**Real capacitors leak.** In parallel with every real capacitor is a large but finite
resistance, so a charged capacitor left completely alone does not stay charged. A good film
part will hold most of its voltage for weeks; a large electrolytic can be substantially
flat in an hour. The "isolated island" argument that gave the series rule is an idealisation
with a time limit on it.

**Real capacitors have series resistance.** The ESR is in the leads, foils and electrolyte,
and it matters as soon as the current is large or fast: it makes the initial jump in the
transient not quite zero and it is what heats a capacitor in a switching supply.

**Dielectric absorption.** Short out a large film or electrolytic capacitor, hold it
shorted, then remove the short and leave the terminals open. Over the next minute the
voltage climbs back to one or two per cent of what it started at, out of nowhere. Part of
the dielectric's polarisation relaxes on a much longer timescale than the main charge, and
it re-emerges. Sample-and-hold and integrator circuits have to be designed around this, and
it is why "the capacitor is discharged" is a statement that needs a tolerance attached.

**And the value may not be constant.** A class-2 ceramic loses capacitance as the DC voltage
across it rises, so $\tau$ changes during the transient and the curve is not truly
exponential at all.

Two errors to name, finally. The first is arithmetic: "63% in the first $\tau$, so it is
done in about $1.6\tau$." Nothing about the curve is linear and that reasoning gives 126%,
which is not a thing a charging capacitor can do. The second is structural: $\tau = RC$
describes a circuit with *one* capacitor and a purely resistive surround. Two capacitors
that cannot be combined into one give two time constants and a sum of two exponentials, and
that is the second-order territory EE111 set up — the coil in module 4 supplies the other
way of getting there.
''',
                },
            ],
            "derive": {
                "title": "Half a CV squared, and where it actually is",
                "minutes": 12,
                "vars": ["Q", "q", "C", "V", "W", "E", "A", "d", "u", "epsilon_0"],
                "brief": r'''
The reading unit asserted two things and sketched the second: that a charged capacitor
holds $\tfrac{1}{2}CV^2$ rather than $QV$, and that the energy is in the gap rather than on
the plates. Here you do both properly.

The route is: charge the capacitor one $\mathrm{d}q$ at a time, integrate, trade the charge
for the voltage, then substitute the parallel-plate geometry and divide by the volume. The
plates disappear at the last step, which is the whole point of doing it.

Write the permittivity of free space as `\epsilon_0`.
''',
                "steps": [
                    {
                        "prompt": "Charging is not instantaneous, and that matters. At the instant when the capacitor already holds a charge $q$, what is the voltage across it? Write it in terms of $q$ and $C$.",
                        "answer": "\\frac{q}{C}",
                        "hint": "The defining relation $C = Q/V$ holds at every instant during the charging, not only when it has finished.",
                        "deconstruct": [
                            "At any moment $C = q/v$, where $q$ and $v$ are the charge and voltage right now.",
                            "Rearrange that for $v$.",
                        ],
                    },
                    {
                        "prompt": "Moving the next $\\mathrm{d}q$ across that voltage costs $\\mathrm{d}W = v\\,\\mathrm{d}q$. Integrate from $q = 0$ up to the final charge $Q$, and write the total work $W$ in terms of $Q$ and $C$.",
                        "answer": "\\frac{Q^2}{2 C}",
                        "placeholder": "a square divided by a capacitance",
                        "hint": "$C$ is a constant, so it comes straight out of the integral, and $\\int_0^Q q\\,\\mathrm{d}q = Q^2/2$.",
                        "deconstruct": [
                            "$W = \\int_0^{Q} (q/C)\\,\\mathrm{d}q$.",
                            "Factor out the constant $1/C$; the remaining integral is $Q^2/2$.",
                        ],
                    },
                    {
                        "prompt": "Now trade the charge for the voltage. Using $Q = CV$, rewrite that same energy in terms of $C$ and $V$.",
                        "answer": "\\frac{C V^2}{2}",
                        "hint": "Substitute $Q = CV$ into $Q^2/(2C)$. Squaring gives $C^2$ on top, and one factor of $C$ cancels against the one underneath.",
                        "deconstruct": [
                            "$Q^2 = (CV)^2 = C^2V^2$.",
                            "Divide that by $2C$.",
                        ],
                    },
                    {
                        "prompt": "Now make it geometric. A parallel-plate capacitor has $C = \\epsilon_0 A/d$, and its field is uniform, so $V = Ed$. Substitute both, and write $W$ in terms of $\\epsilon_0$, $E$, $A$ and $d$ — with no $C$ and no $V$ left in it.",
                        "answer": "\\frac{\\epsilon_0 E^2 A d}{2}",
                        "placeholder": "no C and no V left",
                        "hint": "Put $\\epsilon_0 A/d$ where the $C$ was and $(Ed)^2$ where the $V^2$ was. The square brings a $d^2$, and dividing by the $d$ underneath leaves one power of $d$ surviving.",
                        "deconstruct": [
                            "$W = \\tfrac{1}{2}\\,(\\epsilon_0 A/d)\\,(Ed)^2$.",
                            "$(Ed)^2 = E^2 d^2$, and $d^2/d = d$.",
                        ],
                    },
                    {
                        "prompt": "The gap between the plates has volume $Ad$. Divide by it, and write the energy per unit volume $u$.",
                        "answer": "\\frac{\\epsilon_0 E^2}{2}",
                        "placeholder": "no area and no gap left",
                        "hint": "$A$ and $d$ each appear exactly once in the numerator, so both cancel outright against the volume.",
                        "deconstruct": [
                            "$u = W/(Ad)$.",
                            "Cancel the $A$ and the $d$; nothing about the shape survives.",
                        ],
                    },
                ],
                "closing": r'''
$$u = \tfrac{1}{2}\varepsilon_0 E^2$$

Look at what is *not* in that expression: no area, no gap, no charge, no plates, and no
capacitance. Every trace of the apparatus cancelled in the last step. What is left is a
statement about the electric field itself — wherever there is a field, there is this much
energy in every cubic metre of it — and it applies just as well to the field around a
thundercloud or a single point charge as it does between two plates. The capacitor was
only ever the most convenient place to derive it.

The number is small, and it is worth knowing how small. Dry air breaks down at about
3 MV/m, so the very most you can store in a cubic metre of air is
$\tfrac{1}{2}\times8.854\times10^{-12}\times(3\times10^{6})^2 = 39.8$ J/m³ — enough to lift
a bag of sugar four metres. The magnetic twin of this result, $u = B^2/2\mu_0$, arrives in
module 4 and is far more generous, which is one reason inductors store energy in situations
where capacitors cannot.

One warning about how far to push it. Applied to a point charge, $\tfrac{1}{2}\varepsilon_0
E^2$ integrated over all space diverges, because $E$ goes as $1/r^2$ and the integral runs
in to $r = 0$. That is not a flaw in the arithmetic you just did; it is the subject telling
you that a genuine point charge with a finite self-energy is not a consistent idea, and
that classical electromagnetism has an inner limit as well as the static one Coulomb's law
already had.
''',
            },
            "blanks": {
                "title": "Capacitance, energy and the time constant, term by term",
                "minutes": 9,
                "caption": "the six relations this module runs on, with the load-bearing parts removed",
                "lang": "text",
                "brief": r'''
Nothing here is executed. These are the six expressions the rest of the module stands on,
and the holes are in the places where a slip changes the answer rather than the spelling —
the power on the gap, the way up a ratio goes, the factor of one half, and which of the two
combination rules belongs to which wiring.

Two of the six have a distractor that is dimensionally perfectly sensible and still wrong,
so deciding *why* a choice is right before taking it is worth the ten seconds.
''',
                "listing": """# Two parallel plates of area A, a gap d, and a material of relative
# permittivity eps_r filling the gap.

C = eps0 * eps_r * A / ___          # farads

# The same capacitor described without mentioning its shape at all:
# it carries +Q on one plate and -Q on the other, and the potential
# difference between them is V.

C = ___

# The energy that had to be spent putting that charge there:

W = ___                             # joules

# Two capacitors wired between the SAME pair of nodes, so they are
# forced to hold the same voltage:

C_parallel = ___

# The same two, one after the other in a single branch, with the
# island between them connected to nothing else, so they are forced
# to hold the same charge:

C_series = ___                      # smaller than either of them

# Charging through a resistance R from a supply V, t seconds after
# the supply is applied:

v = V * (1 - exp(-t / ___))
""",
                "blanks": [
                    {
                        "prompt": "What does the plate area get divided by?",
                        "hole": "?",
                        "opts": ["d", "d**2", "sqrt(d)", "A * d"],
                        "a": 0,
                        "why": "One power of the gap. The field between two plates does not fall off with distance at all — it is uniform — so the gap changes nothing except how far you have to climb to cross it, and $V = Ed$ is linear in $d$.",
                        "whys": [
                            "One power of the gap. The field between two plates does not fall off with distance at all — it is uniform — so the gap changes nothing except how far you have to climb to cross it, and $V = Ed$ is linear in $d$.",
                            "This is the inverse square from module 1 turning up where it does not belong. It governs the field of a *point* charge spreading into three dimensions; between two plates the field is uniform. With a gap of 0.10 mm the error is a factor of ten thousand.",
                            "A square root would make a capacitor barely care about its gap, which is the opposite of the truth — the gap is the single hardest thing to manufacture and the reason a 1 µF part needs a 2 µm film rather than an air space.",
                            "Dividing by the volume leaves a capacitance per cubic metre, which is not what the symbol $C$ means. It would also make the area cancel out entirely, so a bigger plate would buy you nothing.",
                        ],
                    },
                    {
                        "prompt": "The definition itself: capacitance is which ratio?",
                        "hole": "?",
                        "opts": ["Q / V", "V / Q", "Q * V", "Q / V**2"],
                        "a": 0,
                        "why": "Charge per volt — how much charge one volt of persuasion puts on the plates. That is why the unit is the coulomb per volt, and why a large capacitance means a part that takes a lot of charge to move its voltage at all.",
                        "whys": [
                            "Charge per volt — how much charge one volt of persuasion puts on the plates. That is why the unit is the coulomb per volt, and why a large capacitance means a part that takes a lot of charge to move its voltage at all.",
                            "Upside down. Volts per coulomb is a real and occasionally useful quantity — it is called elastance, and it is what actually adds when capacitors are put in series — but it is not what the farad measures.",
                            "A product would mean that a capacitor with nothing connected, at zero volts and zero charge, had zero capacitance, and that charging it up would change the value of the component. Capacitance is fixed by the geometry and cannot depend on how hard you drive it.",
                            "This has the units of coulombs per volt squared, which is not a capacitance, and it would make the answer depend on the applied voltage. The whole content of the definition is that the ratio does *not* depend on the voltage.",
                        ],
                    },
                    {
                        "prompt": "The energy stored, in terms of C and V:",
                        "hole": "?",
                        "opts": ["0.5 * C * V**2", "C * V**2", "0.5 * C * V", "0.5 * Q**2 * C"],
                        "a": 0,
                        "why": "Half of $CV^2$. The half is there because the voltage climbs in step with the charge as you fill the capacitor: the first coulomb goes on at 0 V and the last one against the full voltage, so the average cost is half the final one.",
                        "whys": [
                            "Half of $CV^2$. The half is there because the voltage climbs in step with the charge as you fill the capacitor: the first coulomb goes on at 0 V and the last one against the full voltage, so the average cost is half the final one.",
                            "Dropping the half is the classic slip, and it is not a rounding error — it is exactly the energy the charging resistor dissipated, every time, whatever its value. $QV$ is what the *supply* delivered, and half of it never reached the capacitor.",
                            "$CV$ is the charge, in coulombs, not an energy. Multiplying by a half does not fix the units. A quick guard: any energy expression here must be quadratic in the voltage, because doubling the voltage doubles the charge *and* the price of each coulomb.",
                            "Multiplying $Q^2$ by $C$ rather than dividing gives units of coulombs squared per... nothing recognisable, and it gets the physics backwards: a bigger capacitor at a given charge holds *less* energy, because that charge sits at a lower voltage.",
                        ],
                    },
                    {
                        "prompt": "Two capacitors forced to the same voltage. What is the pair worth?",
                        "hole": "?",
                        "opts": ["C1 + C2", "C1 * C2 / (C1 + C2)", "1 / (C1 + C2)", "sqrt(C1**2 + C2**2)"],
                        "a": 0,
                        "why": "They add. Each takes its own charge $CV$ at the shared voltage, and the supply had to deliver the sum, so the total charge per volt is the sum of the two. Geometrically it is one capacitor with the two plate areas added together.",
                        "whys": [
                            "They add. Each takes its own charge $CV$ at the shared voltage, and the supply had to deliver the sum, so the total charge per volt is the sum of the two. Geometrically it is one capacitor with the two plate areas added together.",
                            "This is the *series* rule, applied to the wrong wiring. It is the one genuinely confusing thing about capacitors, because it is the reverse of the resistor rules — and the tell is that this expression is always smaller than either capacitor, whereas adding a second capacitor across the same two nodes can only give you more.",
                            "The reciprocal of a sum of capacitances is an elastance, not a capacitance, and its value would be tiny: two 1 µF parts would come out at 500 kilo-somethings rather than 2 µF.",
                            "A root-sum-square is how uncorrelated noise contributions combine, not how charge does. Charge is simply conserved and counted, so the arithmetic here is ordinary addition with no geometry in it at all.",
                        ],
                    },
                    {
                        "prompt": "The same two capacitors, forced instead to hold the same charge:",
                        "hole": "?",
                        "opts": ["C1 * C2 / (C1 + C2)", "C1 + C2", "(C1 + C2) / 2", "C1 * C2"],
                        "a": 0,
                        "why": "Product over sum, which is the same statement as $1/C = 1/C_1 + 1/C_2$. The charge is common and the voltages add, so it is the reciprocals that combine — and the answer is always smaller than the smaller of the two, exactly as two capacitors stacked make one capacitor with a wider gap.",
                        "whys": [
                            "Product over sum, which is the same statement as $1/C = 1/C_1 + 1/C_2$. The charge is common and the voltages add, so it is the reciprocals that combine — and the answer is always smaller than the smaller of the two, exactly as two capacitors stacked make one capacitor with a wider gap.",
                            "This is the parallel rule in the series position. Beyond being the wrong formula it fails the sanity check that costs nothing to apply: a series combination has to come out smaller than both of its members, and a sum never can.",
                            "An average would give 3.45 µF for a 2.2 µF and a 4.7 µF in series, when the true answer is 1.50 µF — smaller than either. Averages appear nowhere in circuit combination rules.",
                            "A bare product has units of farads squared, so it is not a capacitance at all. It is the numerator of the right answer with the sum underneath left off, which is exactly how the slip usually happens.",
                        ],
                    },
                    {
                        "prompt": "What goes in the denominator of the exponent — the time constant?",
                        "hole": "?",
                        "opts": ["R * C", "R / C", "C / R", "2 * pi * R * C"],
                        "a": 0,
                        "why": "The product, and it comes out in seconds: ohms times farads is (volts per amp) times (coulombs per volt), which is coulombs per amp, which is seconds. Checking that once by hand is the quickest way to catch a factor of a thousand.",
                        "whys": [
                            "The product, and it comes out in seconds: ohms times farads is (volts per amp) times (coulombs per volt), which is coulombs per amp, which is seconds. Checking that once by hand is the quickest way to catch a factor of a thousand.",
                            "A ratio has units of ohms per farad, which is not a time, and it gets the physics backwards twice over: a bigger capacitor would charge faster and a bigger resistor would slow it down only in one of those two ways.",
                            "Farads per ohm is not a time either, and it says a larger resistor makes the circuit quicker — which would mean an open circuit charged a capacitor instantly.",
                            "$2\\pi RC$ is a time, and it is the right order of magnitude, which is what makes this the dangerous one. But the $2\\pi$ belongs to the frequency-domain description: the corner is at $f_c = 1/(2\\pi RC)$, and the factor appears there because a radian frequency is $2\\pi$ times a cyclic one. It has no business in the transient.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "Two plates and a gap",
                    "minutes": 5,
                    "brief": r'''
The mechanical one, to get the formula under your fingers. One rule, one unknown, and the
only thing it can catch you out on is that both lengths have to be in metres before either
of them is used — and one of them is quoted in millimetres and the other in fractions of
one.
''',
                    "prompt": "What is the capacitance of the pair of plates?",
                    "note": "Give the answer in picofarads, to one decimal place.",
                    "figure": "Two flat square plates, each 50.0 mm along a side, are held parallel and "
                              "facing one another across a 0.200 mm air gap. Nothing else is near them. "
                              "Treat the air as vacuum, so the relative permittivity of the gap is 1.00.",
                    "given": [
                        {"label": "Plate side", "value": "50.0 mm"},
                        {"label": "Gap", "value": "0.200 mm"},
                        {"label": "Relative permittivity of the gap", "value": "1.00"},
                        {"label": "Permittivity of free space", "value": "8.854e-12 F/m"},
                    ],
                    "aside": "The area is a side times a side, not a side times four. And a picofarad is "
                             "$10^{-12}$ F, so the answer will be a small multiple of the 8.854 you started "
                             "with.",
                    "answer": 110.7,
                    "tol": 0.8,
                    "unit": "pF",
                    "hint": "$C = \\varepsilon_0 A/d$. Work out $A/d$ first, in metres, and note that it "
                            "comes out as a plain length; multiplying that by $\\varepsilon_0$ in farads "
                            "per metre leaves farads.",
                    "wrong": "If you got 2214, the plate's *side* went in where its area belongs — the "
                             "0.0500 m never got multiplied by itself. If you got 0.111, the gap went in "
                             "as 0.200 metres rather than 0.200 millimetres.",
                    "why": r'''
```
A   = 0.0500 * 0.0500                        = 2.50e-3 m^2
d   = 0.200 mm                               = 2.00e-4 m
A/d = 2.50e-3 / 2.00e-4                      = 12.5 m

C   = 8.854e-12 * 12.5                       = 1.1068e-10 F   = 110.7 pF
```

A hundred picofarads out of two plates the size of a beer mat, which is worth holding on
to as a sense of scale: the capacitance you can build in air, at any size you would
actually make, is *tiny*. Getting to a microfarad from here needs the gap down by a factor
of a hundred, to a couple of microns, and a dielectric in it — which is exactly how a real
film capacitor is built.

Note also what the arithmetic did: $A/d$ came out as a plain length in metres, 12.5 m, and
$\varepsilon_0$ is quoted in farads *per metre*. The units were never in doubt.
''',
                },
                {
                    "title": "Where the output has got to after a millisecond",
                    "minutes": 7,
                    "brief": r'''
A supply, one resistor, one capacitor to ground, and a probe on the node between them. The
supply is switched on at $t = 0$ with the capacitor completely empty.

One formula, used forwards. Work out the time constant first and keep it on the page — the
exponent is a ratio of two times, and it is a pure number.
''',
                    "prompt": "What is the voltage at the probe 1.00 ms after the supply is applied?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 3300},
                            {"id": "c1", "kind": "C", "x": 12, "y": 7, "rot": 1, "value": 220e-9},
                            {"id": "g1", "kind": "GND", "x": 12, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 16, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [12, 3], "b": [12, 6]},
                            {"a": [12, 8], "b": [12, 10]},
                            {"a": [12, 3], "b": [16, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "9.00 V"},
                        {"label": "Series resistor", "value": "3.30 kΩ"},
                        {"label": "Capacitor to ground", "value": "220 nF"},
                        {"label": "Time since the supply came on", "value": "1.00 ms"},
                    ],
                    "aside": "The time constant here is not a round number, and it is smaller than the "
                             "millisecond you are asked about — so the answer must be more than 63% of "
                             "the supply and less than all of it.",
                    "answer": 6.73,
                    "tol": 0.05,
                    # The prompt asks for a point on the transient, so the check runs the real
                    # transient and reads the last sample at exactly t = 1 ms rather than
                    # re-evaluating the closed form the answer came from.
                    "check": r'''
var s = c.step(1.0e-3);
return s.v[s.v.length - 1];
''',
                    "hint": "$\\tau = RC$, then $v = V(1 - e^{-t/\\tau})$. Both times must be in the same "
                            "unit before you divide them; milliseconds over milliseconds is fine.",
                    "wrong": "If you got 4.65, the exponent was inverted — it is $t/\\tau$, not $\\tau/t$. "
                             "If you got 2.27, the answer given was $Ve^{-t/\\tau}$, which is the *discharge* "
                             "curve, or equivalently the voltage left across the resistor rather than the "
                             "voltage reached by the capacitor. The two always add to 9.00 V.",
                    "why": r'''
```
tau     = R C = 3300 * 220e-9                  = 7.260e-4 s  = 0.7260 ms

t/tau   = 1.00 ms / 0.7260 ms                  = 1.3774
exp(-1.3774)                                   = 0.25223

v(1 ms) = 9.00 * (1 - 0.25223)
        = 9.00 * 0.74777                       = 6.730 V
```

A little under 1.4 time constants have gone by, so the capacitor is about three quarters of
the way there — comfortably past the 63.2% that one $\tau$ buys, nowhere near the 86.5% that
two would.

Two sanity checks that cost nothing. The answer has to lie strictly between 0 and 9.00 V,
because an exponential approaches its target and never passes it. And the resistor is
holding the difference, $9.00 - 6.73 = 2.27$ V, which means the current still flowing into
the capacitor is $2.27/3300 = 0.688$ mA — falling, and on its way to zero.
''',
                },
                {
                    "title": "Three capacitors and the energy in them",
                    "minutes": 9,
                    "brief": r'''
Now a network, and a quantity that is not a voltage. Two capacitors sit one after the other
in a branch; a third sits across that whole branch; and the lot is connected to a 24 V
supply and left until nothing is changing.

Reduce first, then ask the energy question of the single equivalent capacitor. Doing it the
other way round — energy of each part, then add — also works, but it needs the voltage on
each of the three separately and there are more places to slip.
''',
                    "prompt": "How much energy is stored in the whole network once it has settled?",
                    "note": "Give the answer in microjoules, to one decimal place.",
                    "figure": "A 1.00 µF capacitor and a 2.20 µF capacitor are wired in series to form one "
                              "branch. A 0.470 µF capacitor is wired directly across the ends of that "
                              "branch. The two ends are then connected to a 24.0 V supply and left until "
                              "nothing is changing.",
                    "given": [
                        {"label": "In series", "value": "1.00 µF and 2.20 µF"},
                        {"label": "Across the pair", "value": "0.470 µF"},
                        {"label": "Supply", "value": "24.0 V"},
                    ],
                    "aside": "Reduce the series pair first. It has to come out smaller than 1.00 µF; if it "
                             "does not, the two rules have been swapped.",
                    "answer": 333.4,
                    "tol": 3.0,
                    "unit": "µJ",
                    "hint": "Series first: $C_1C_2/(C_1+C_2)$. Then that result simply adds to the 0.470 µF, "
                            "because they lie between the same two nodes. Finish with "
                            "$W = \\tfrac{1}{2}CV^2$.",
                    "wrong": "If you got 1057, the series pair was added instead of combined — that gives "
                             "3.20 µF where it should give 0.688 µF, and the total comes out at 3.67 µF "
                             "instead of 1.16 µF. If you got 666.7, the factor of one half was dropped; "
                             "that is the energy the *supply* delivered, and half of it was lost in "
                             "whatever resistance the charging path had.",
                    "why": r'''
```
the series pair, product over sum:

    C_s   = (1.00 * 2.20) / (1.00 + 2.20)
          = 2.20 / 3.20                        = 0.6875 uF     (< 1.00, as it must be)

the third capacitor is across the same two nodes, so it adds:

    C_tot = 0.6875 + 0.470                     = 1.1575 uF

and the energy at 24.0 V:

    W     = 0.5 * 1.1575e-6 * 24.0^2
          = 0.5 * 1.1575e-6 * 576              = 3.3336e-4 J   = 333.4 uJ
```

Worth checking against the long route, because it exercises everything in the module at
once. The series branch holds $Q = 0.6875\ \mu\text{F} \times 24.0 = 16.5$ µC, the same
charge on both of its members, so the 1.00 µF sits at 16.5 V and the 2.20 µF at 7.50 V —
and they sum to 24.0 V. The energies are then
$\tfrac{1}{2}(1.00)(16.5)^2 = 136.1$ µJ, $\tfrac{1}{2}(2.20)(7.50)^2 = 61.9$ µJ and
$\tfrac{1}{2}(0.470)(24.0)^2 = 135.4$ µJ in microjoule units, and $136.1 + 61.9 + 135.4 =
333.4$ µJ. The same number, from three separate capacitors each at its own voltage.

Notice which capacitor holds most of it. The 0.470 µF is the smallest part in the circuit
and stores more than either member of the series branch, because it is the only one that
gets the full 24 V — and energy goes as the *square* of the voltage.
''',
                },
                {
                    "title": "The capacitor that has not been fitted",
                    "minutes": 12,
                    "brief": r'''
A board part-built. A 12.0 V rail feeds a 10.0 kΩ resistor into the probed node, and a
15.0 kΩ resistor runs from that node down to ground. Beside them is an empty pair of pads
for a capacitor from the node to ground, which is why the drawing shows no capacitor.

The specification says that when the rail is switched on, the probed node must be at
**5.00 V exactly 1.20 ms later**. Choose the capacitor.

Three things have to be established before the exponential can be inverted, and only one of
them is written on the drawing: what voltage the node ends up at, what resistance the
capacitor will actually see, and only then what value makes the timing come out. The
resistance is the part that catches people — it is neither 10 kΩ nor 25 kΩ.
''',
                    "prompt": "What value must the capacitor be?",
                    "note": "Give the answer in nanofarads, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 11, "y": 4, "rot": 1, "value": 10000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 15000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 6},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 6], "b": [15, 6]},
                            {"a": [11, 9], "b": [11, 11]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "12.0 V"},
                        {"label": "Series resistor", "value": "10.0 kΩ"},
                        {"label": "Resistor to ground", "value": "15.0 kΩ"},
                        {"label": "Node must reach", "value": "5.00 V"},
                        {"label": "By", "value": "1.20 ms after switch-on"},
                    ],
                    "aside": "The capacitor charges through everything that can move charge on and off it. "
                             "Turn the rail into a short — a fixed voltage cannot oppose a change — and "
                             "look back from the empty pads to see what is really there.",
                    "answer": 168.7,
                    "tol": 1.5,
                    "unit": "nF",
                    # The capacitor is not on the board, so there is nothing to read off directly.
                    # Everything except the two numbers in the specification comes out of the
                    # solve: the rail, its current and the probed node give both resistors, and
                    # their parallel combination is what the missing part will charge through.
                    "check": r'''
var d = c.dc();
var src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
var V = Math.abs(d.v[src.n1] - d.v[src.n2]);
var I = Math.abs(d.currents[src.id]);
var vf = d.v[c.outNode()];
var Rser = (V - vf) / I;
var Rsh = vf / I;
var Rth = 1 / (1 / Rser + 1 / Rsh);
var tau = 1.20e-3 / Math.log(1 / (1 - 5.00 / vf));
return tau / Rth * 1e9;
''',
                    "hint": "Final value first: with no current flowing into the capacitor at the end, the "
                            "node is a plain divider. Then the time constant uses the two resistors in "
                            "*parallel*. Then invert $v = V_f(1 - e^{-t/\\tau})$ for $\\tau$, and divide by "
                            "the resistance.",
                    "wrong": "If you got 101.2, the time constant was divided by 10.0 kΩ — the series "
                             "resistor alone, ignoring the second path the charge has to ground. If you "
                             "got 40.5, it was divided by the two in series, 25.0 kΩ, which is the "
                             "resistance the *rail* sees rather than the one the capacitor sees. And if "
                             "the exponential was inverted against 12.0 V instead of 7.20 V, the required "
                             "time constant comes out at 2.23 ms and the answer at 371 nF.",
                    "why": r'''
```
FINAL VALUE — at the end nothing is changing, so no current flows
into the capacitor and the node is a plain divider:

    V_f  = 12.0 * 15.0 / (10.0 + 15.0)          = 7.20 V

RESISTANCE the capacitor sees, with the 12 V rail shorted, which
puts the two resistors in parallel:

    R_th = (10.0 * 15.0) / (10.0 + 15.0) kohm   = 6.00 kohm

INVERT the exponential for the time constant it demands:

    v/V_f     = 5.00 / 7.20                     = 0.69444
    exp(-t/tau) = 1 - 0.69444                   = 0.30556
    t/tau     = ln(1/0.30556) = ln 3.2727       = 1.18562
    tau       = 1.20 ms / 1.18562               = 1.0121 ms

AND FINALLY the part:

    C    = tau / R_th = 1.0121e-3 / 6000        = 1.687e-7 F    = 168.7 nF
```

Every step of that is a thing the module has already said, but this is the first time all
three have had to be true at once, and the middle one is where the real content is. The
capacitor does not care which resistor is "the load" and which is "the source" — it sees
two resistances to ground in parallel, because from its point of view a 12 V rail that
never moves is indistinguishable from a piece of wire. Using 10.0 kΩ instead would have
called for 101 nF, and a board built with that part reaches 5.00 V at 0.72 ms — 40% early,
which for a power-on reset or a debounce is a failure rather than a rounding error.

The nearest standard part is 180 nF, or a 150 nF and a 22 nF in parallel; with 180 nF the
node reaches 5.00 V at 1.28 ms rather than 1.20 ms. That is the other thing this exercise
is quietly saying — the timing is only ever as good as the capacitor's tolerance, and a
±10% part makes the 1.20 ms a 1.08-to-1.32 ms specification whatever value you compute.
''',
                },
            ],
            "quiz": {
                "title": "Capacitance, checked",
                "minutes": 8,
                "questions": [
                    {
                        "q": "You pull the plates of a parallel-plate capacitor twice as far apart, changing nothing else. What happens to its capacitance?",
                        "opts": ["It doubles", "It halves", "It quadruples", "It is unchanged"],
                        "a": 1,
                        "why": (
                            "$C = \\varepsilon_0 A/d$ has the gap in the denominator, so doubling $d$ halves $C$. "
                            "Physically: at a given voltage the field $E = V/d$ is now weaker, so less charge is "
                            "needed on the plates to produce it. Note this is a $1/d$ law, not $1/d^2$ — the "
                            "inverse square belongs to the force between point charges, not to plate geometry."
                        ),
                    },
                    {
                        "q": "You slide a sheet of glass with $\\varepsilon_r = 4$ into the gap, filling it completely. The capacitance becomes:",
                        "opts": [
                            "Four times larger",
                            "Four times smaller",
                            "Unchanged, since glass is an insulator and carries no current",
                            "Twice as large",
                        ],
                        "a": 0,
                        "why": (
                            "The glass polarises: its molecules line up and their own field partly cancels the "
                            "field from the plates, so the same charge produces a smaller voltage — and $C = Q/V$ "
                            "goes up by the factor $\\varepsilon_r$, here four. The tempting wrong answer is that "
                            "an insulator can do nothing because no current flows through it, but capacitance was "
                            "never about current."
                        ),
                    },
                    {
                        "q": "Two 1 µF capacitors are connected in series. The combination behaves as:",
                        "opts": ["2 µF", "1 µF", "0.5 µF", "It depends on the applied voltage"],
                        "a": 2,
                        "why": (
                            "In series the reciprocals add: $1/C = 1/1 + 1/1$ per microfarad, giving 0.5 µF. The "
                            "geometric picture is the one to keep: two identical capacitors in series is the same "
                            "as one capacitor with twice the plate separation, and doubling $d$ halves $C$. "
                            "Answering 2 µF is applying the *parallel* rule, which is the rule that does add."
                        ),
                    },
                    {
                        "q": "A 1 µF and a 3 µF capacitor sit in series across a battery. Compare the charge stored on each.",
                        "opts": [
                            "The 3 µF holds three times the charge",
                            "The 1 µF holds three times the charge",
                            "They hold the same charge; the voltages differ instead",
                            "They hold the same charge and the same voltage",
                        ],
                        "a": 2,
                        "why": (
                            "The plates between the two capacitors are isolated, so whatever charge leaves one "
                            "must arrive on the other: series capacitors carry identical charge. With $Q$ fixed "
                            "and $V = Q/C$, the *smaller* capacitor takes the larger share of the voltage — here "
                            "the 1 µF takes three quarters of it. This is why series capacitors are used to split "
                            "a voltage that would break down a single one."
                        ),
                    },
                    {
                        "q": "You double the voltage across a capacitor. The stored energy:",
                        "opts": ["Doubles", "Halves", "Quadruples", "Stays the same"],
                        "a": 2,
                        "why": (
                            "The energy is $\\tfrac{1}{2}CV^2$, so it goes as the *square* of the voltage: doubling "
                            "$V$ multiplies the energy by four. The charge only doubles — the extra factor comes "
                            "from the fact that each additional coulomb has to be pushed onto a plate that is "
                            "already at a higher potential than the last one was."
                        ),
                    },
                    {
                        "q": "A 1 µF capacitor charges from a 5 V supply through a 1 kΩ resistor. After 1 ms — one time constant — the capacitor voltage is about:",
                        "opts": ["5 V, fully charged", "3.16 V", "2.5 V, exactly half", "1.84 V"],
                        "a": 1,
                        "why": (
                            "One time constant $\\tau = RC$ brings the capacitor to $1 - 1/e = 63.2\\%$ of the "
                            "supply, which is 3.16 V — not half, and not full. The charging curve is exponential, "
                            "so it never technically finishes; 95% is reached at $3\\tau$ and 99% at about "
                            "$4.6\\tau$. You will measure this exact number on a circuit you draw in the next "
                            "exercise."
                        ),
                    },
                ],
            },
            "build": {
                "title": "A one-millisecond RC",
                "minutes": 25,
                "brief": r'''
Draw a circuit that charges a capacitor from a **5 V source through a resistor**, so
that the voltage on the capacitor reaches 63% of the supply — 3.16 V — one
millisecond after the supply is applied.

The canvas opens with the source, a ground and a 1 kΩ resistor already wired, and a
probe on the node that will become the output. What is missing is a capacitor from
that node down to a ground of its own, and a value for it.

Only the **product** $RC$ is fixed by the specification, so you choose the split, and
you may change the resistor as well as add the capacitor. 1 kΩ with 1 µF works; so
does 10 kΩ with 100 nF, and the checks will accept either, because they measure the
circuit rather than compare it to a drawing.

Values are typed in engineering notation: `1k`, `100n`, `4.7u`.

The checks measure four things:

- the settled DC voltage at the probe,
- the time the transient takes to cross 3.16 V,
- the **corner frequency** $f_c = 1/(2\pi RC)$, which EE111 defined as the frequency
  where the output has fallen to $1/\sqrt{2} = 0.707$ of its low-frequency size,
- and that the output really is filtered rather than wired straight to the source.

That fall to $0.707$ is also written **−3 dB**. A *decibel* is a size ratio put on a
logarithmic scale: a ratio $g$ is $20\log_{10} g$ decibels, so $g = 1$ is 0 dB,
$g = 0.707$ is $-3.01$ dB, and $g = 0.1$ is $-20$ dB. It is a change of units and
nothing more, but it is the unit every filter is quoted in. Above the corner this
filter loses a further factor of ten — a further 20 dB — for every decade of
frequency, which is the fastest a circuit with one capacitor in it can fall.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1000},
                        {"id": "p2", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 4, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 4], "b": [11, 4]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1000},
                        {"id": "p2", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 4, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [9, 4], "b": [11, 4]},
                    ],
                },
                "checks": [
                    {"name": "the capacitor eventually charges to the full 5 V", "code": r'''
c.close(c.vout(), 5.0, 0.02, "the settled voltage at the probe");
'''},
                    {"name": "it reaches 63% of the supply after 1 ms", "code": r'''
var s = c.step(0.005);
var last = s.v[s.v.length - 1];
c.assert(last > 4.5, "after 5 ms the output has only reached " + c.fmt(last, "V") +
  " — the time constant is far longer than 1 ms");
var t63 = null;
for (var i = 1; i < s.t.length; i++) {
  if (s.v[i] >= 0.632 * 5.0) { t63 = s.t[i]; break; }
}
c.assert(t63 !== null, "the output never reaches 3.16 V within 5 ms");
c.close(t63, 1.0e-3, 0.08, "the time to reach 63% of 5 V");
'''},
                    {"name": "the same RC product puts the corner at 159 Hz", "code": r'''
var fc = c.corner(1, 1e5);
c.close(fc, 159.15, 0.06, "the -3 dB frequency (which is 1/(2*pi*R*C))");
'''},
                    {"name": "the output is filtered, not just wired to the source", "code": r'''
var low = c.gain(1);
var high = c.gain(1.5915e4);
c.assert(low > 4.5, "at 1 Hz the output should still follow the source, but it reads " +
  c.fmt(low, "V"));
c.assert(high < 0.15 * low, "a hundred times above the corner the output should be far " +
  "smaller than at DC, but it is " + (100 * high / low).toFixed(0) + "% of it");
'''},
                ],
                "hints": [
                    "The capacitor goes from the probe node down to a ground of its own — vertical, with its top pin meeting the wire that carries the resistor's right-hand end.",
                    "Pick the resistor first, then the capacitor: $C = \\tau / R$, and with $\\tau = 1$ ms a 1 kΩ resistor asks for 1 µF.",
                    "Type `1u` for a microfarad. If the transient check reports a time constant ten times too large, the capacitor is probably `10u`.",
                    "The corner check is not a second specification — $1/(2\\pi RC)$ with $RC = 1$ ms is 159.15 Hz automatically. If the time check passes and this one does not, look for a second resistor or capacitor loading the node.",
                ],
            },
            "lab": {
                "title": "Capacitance from dimensions",
                "runtime": "python",
                "minutes": 22,
                "brief": r'''
The circuit you just drew used a 1 µF part with no questions asked. This lab asks
where that number comes from, and closes the loop back to the time constant you
measured.

`plate_capacitance(area, gap, eps_r)` returns the capacitance of two parallel plates
in farads: $\varepsilon_0 \varepsilon_r A / d$.

`series_capacitance(caps)` and `parallel_capacitance(caps)` combine a list of values.
Reciprocals add in series; values add in parallel.

`charge_time(r, c, frac)` returns how long an RC circuit takes to reach the fraction
`frac` of its final voltage. Rearranging $v(t) = V(1 - e^{-t/RC})$ gives

```text
t = -R * C * log(1 - frac)
```

and putting `frac = 0.632` into it should return, to three figures, the millisecond
the schematic editor measured.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

EPS0 = 8.8541878128e-12   # F/m


def plate_capacitance(area, gap, eps_r=1.0):
    """Capacitance in farads of two parallel plates of `area` m^2, `gap` m apart."""
    # TODO: eps0 * eps_r * A / d
    return 0.0


def series_capacitance(caps):
    """Capacitance of a list of capacitors in series, in farads."""
    # TODO: the reciprocals add.
    return 0.0


def parallel_capacitance(caps):
    """Capacitance of a list of capacitors in parallel, in farads."""
    # TODO: the values add.
    return 0.0


def charge_time(r, c, frac):
    """Seconds for an RC circuit to reach `frac` of its final voltage."""
    # TODO: invert v(t) = V(1 - exp(-t/RC)).
    return 0.0


if __name__ == "__main__":
    small = plate_capacitance(1e-4, 1e-4)
    print("1 cm^2 plates 0.1 mm apart:", small, "F")
    print("with glass in the gap:", plate_capacitance(1e-4, 1e-4, 4.0), "F")
    print("1 kohm and 1 uF reach 63.2% after", charge_time(1000.0, 1e-6, 0.632), "s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

EPS0 = 8.8541878128e-12   # F/m


def plate_capacitance(area, gap, eps_r=1.0):
    """Capacitance in farads of two parallel plates of `area` m^2, `gap` m apart."""
    return float(EPS0 * eps_r * area / gap)


def series_capacitance(caps):
    """Capacitance of a list of capacitors in series, in farads."""
    total = 0.0
    for c in caps:
        total += 1.0 / c
    return float(1.0 / total)


def parallel_capacitance(caps):
    """Capacitance of a list of capacitors in parallel, in farads."""
    return float(sum(caps))


def charge_time(r, c, frac):
    """Seconds for an RC circuit to reach `frac` of its final voltage."""
    return float(-r * c * np.log(1.0 - frac))


if __name__ == "__main__":
    small = plate_capacitance(1e-4, 1e-4)
    print("1 cm^2 plates 0.1 mm apart:", small, "F")
    print("with glass in the gap:", plate_capacitance(1e-4, 1e-4, 4.0), "F")
    print("1 kohm and 1 uF reach 63.2% after", charge_time(1000.0, 1e-6, 0.632), "s")
'''}],
                "hints": [
                    "`plate_capacitance` is one expression. Keep the units straight: area in square metres, gap in metres.",
                    "For the series case accumulate `1/c` and take the reciprocal at the end. Returning the sum itself gives the parallel answer, which is the classic slip.",
                    "`charge_time` needs a natural logarithm: `np.log`, not `np.log10`.",
                ],
                "tests": [
                    {"name": "a square centimetre a tenth of a millimetre away", "code": r'''
_c = plate_capacitance(1e-4, 1e-4)
assert abs(_c - 8.8541878128e-12) < 1e-24, \
    f"with A/d = 1 the capacitance is just eps0 = 8.854 pF, got {_c!r}"
'''},
                    {"name": "wider gap, less capacitance; more area, more", "code": r'''
_base = plate_capacitance(1e-4, 1e-4)
_wide = plate_capacitance(1e-4, 2e-4)
_big = plate_capacitance(3e-4, 1e-4)
assert abs(_wide - 4.4270939064e-12) < 1e-24, \
    f"1 cm^2 plates 0.2 mm apart come to 4.427 pF, got {_wide!r}"
assert abs(_wide - _base / 2.0) < 1e-24, "doubling the gap should halve the capacitance"
assert abs(_big - 2.65625634384e-11) < 1e-23, \
    f"3 cm^2 plates 0.1 mm apart come to 26.56 pF, got {_big!r}"
assert abs(_big - 3.0 * _base) < 1e-24, "tripling the area should triple the capacitance"
'''},
                    {"name": "a dielectric multiplies the capacitance", "code": r'''
_vac = plate_capacitance(2e-4, 5e-5)
_glass = plate_capacitance(2e-4, 5e-5, 4.0)
assert abs(_vac - 3.54167512512e-11) < 1e-23, \
    f"A/d = 4 in vacuum gives 4*eps0 = 35.42 pF, got {_vac!r}"
assert abs(_glass - 4.0 * _vac) < 1e-22, \
    f"eps_r = 4 should give four times the vacuum value, got {_glass!r} against {_vac!r}"
'''},
                    {"name": "series is smaller than the smallest, parallel is the sum", "code": r'''
_s = series_capacitance([1e-6, 1e-6])
assert abs(_s - 5e-7) < 1e-16, f"two 1 uF in series is 0.5 uF, got {_s!r}"
_mixed = series_capacitance([1e-6, 2e-6])
assert _mixed < 1e-6, f"a series combination is smaller than its smallest member, got {_mixed!r}"
assert abs(_mixed - 6.666666666666667e-07) < 1e-16, f"expected 0.667 uF, got {_mixed!r}"
_p = parallel_capacitance([1e-6, 2e-6])
assert abs(_p - 3e-6) < 1e-16, f"in parallel they add to 3 uF, got {_p!r}"
'''},
                    {"name": "one time constant is 63.2% of the way there", "code": r'''
import math
_tau = charge_time(1000.0, 1e-6, 1.0 - 1.0 / math.e)
assert abs(_tau - 1e-3) < 1e-12, \
    f"reaching 1 - 1/e of the supply takes exactly RC = 1 ms, got {_tau!r}"
'''},
                    {"name": "the numbers match the circuit you drew", "code": r'''
_t63 = charge_time(1000.0, 1e-6, 0.632)
assert abs(_t63 - 1e-3) < 2e-6, \
    f"1 kohm with 1 uF should reach 63.2% at about 1 ms, got {_t63!r}"
_t95 = charge_time(1000.0, 1e-6, 0.95)
assert abs(_t95 - 0.00299573227355399) < 1e-12, \
    f"95% takes just under three time constants, got {_t95!r}"
assert _t95 > 2.5 * _t63, "the last few per cent take far longer than the first 63%"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Magnetic fields, induction and inductance",
            "summary": "Moving charge makes a field that curls, a changing field makes a voltage, and a coil's shape fixes how much.",
            "concepts": [
                "A current makes a magnetic field $B$, measured in tesla. Around a long straight wire the field circles the wire and falls off as $1/r$ — not $1/r^2$.",
                "Ampere's law: add up $B$ along any closed loop and the total is $\\mu_0$ times the current threaded through the loop. For a wire this gives $B = \\mu_0 I / (2\\pi r)$ in one line.",
                "Magnetic field lines always close on themselves. There is no magnetic charge for them to start on, so the net magnetic flux out of any closed surface is exactly zero.",
                "Magnetic flux through a loop is $\\Phi = BA\\cos\\theta$, in webers. Faraday's law: a *changing* flux drives a voltage, $\\mathcal{E} = -\\mathrm{d}\\Phi/\\mathrm{d}t$. A steady flux drives nothing.",
                "Lenz's law is the minus sign: the induced current flows the way that opposes the change that caused it. Energy conservation, wearing a different hat.",
                "A coil links its own flux, so changing its own current induces a voltage in itself: $v = L\\,\\mathrm{d}i/\\mathrm{d}t$. For a solenoid of $N$ turns, length $\\ell$ and cross-section $A$, $L = \\mu_0 N^2 A / \\ell$ — the turns count squared, because each turn both makes and links the flux.",
                "Through a resistor, an inductor's current settles with time constant $\\tau = L/R$, and a capacitor and an inductor together resonate at $\\omega_0 = 1/\\sqrt{LC}$.",
            ],
            "read": [
                {
                    "title": "A current makes a field, and the field goes round in circles",
                    "minutes": 18,
                    "body": r'''
In April 1820, lecturing in Copenhagen, Hans Christian Ørsted left a compass sitting on
the bench beside a wire. When he closed the circuit the needle moved. That alone was new
— nobody had made an electric current do anything to a magnet before — but the direction
it moved in was the real shock. The needle did not swing towards the wire, and it did not
swing away from it. It set itself *across* the wire, at right angles to the line joining
the two.

Everything in the first three modules was along the line joining. Coulomb's force between
two charges lies on the line between them. The field of a point charge points straight out
from it. Gauss's law works precisely because that field is radial, so a sphere drawn round
the charge meets it head-on everywhere. Ørsted's needle obeys none of this, and that is
why the magnetic half of the subject needs its own apparatus rather than the electric one
with the constants changed.

## What the needle is showing

Walk the compass round the wire at a fixed distance and the needle turns with you: it
always lies tangent to a circle drawn round the wire. Reverse the current and every needle
flips end for end. Move further out and the deflection weakens.

So the field of a straight current is a family of concentric circles, centred on the wire,
lying in planes at right angles to it. Grip the wire with your right hand, thumb pointing
along the conventional current, and your fingers curl the way the field runs. It is the
only mnemonic in this module and it is worth five minutes of deliberate practice, because
nearly every sign error later is this one made in a hurry.

Notice something about those circles that has no electrostatic counterpart: **they close**.
A field line round a wire is a loop with no beginning and no end. Electric field lines
start on positive charge and finish on negative charge, which is exactly what let module 2
count them through a closed surface and read the enclosed charge off the answer. Magnetic
field lines do neither, because there is nothing for them to start on.

## Defining B by what it does

The electric field was defined by dividing out the probe: put a small charge $q$ at a
point, measure the force on it, and $E = F/q$ is a property of the point rather than of
the probe. The magnetic field is defined the same way, with one large complication — a
*stationary* charge in a magnetic field feels nothing at all. Only a moving charge is
pushed; the push is at right angles both to the velocity and to the field; and its size
depends on the angle $\theta$ between them:

$$F = q v B \sin\theta$$

The direction comes from the right hand again: fingers along $\vec v$, curl them towards
$\vec B$, thumb gives the force on a positive charge. Compactly, $\vec F = q\,\vec v \times
\vec B$, and module 7 does the cross product properly. Here the magnitude and the phrase
*at right angles to both* are enough.

Rearranged, $B = F/(qv\sin\theta)$, so the unit is the newton per amp-metre, and it is
given the name **tesla**. It is a large unit, in the opposite way to the farad being an
absurdly small one:

```text
Earth's field at the surface           30 to 60 uT
a fridge magnet, at its face           about 5 mT
the gap of a loudspeaker motor         about 1 T
a clinical MRI bore                    1.5 to 3 T
the strongest continuous lab magnet    about 45 T
```

Almost everything you meet is a fraction of a tesla, and the microtesla is the working
unit for stray fields.

## Ampère's law: Gauss's law's loop-shaped cousin

Gauss's law took a closed *surface* and added up the electric field poking out through it.
The total came out proportional to the charge inside, and it was useful because in a
symmetric problem $E$ is constant over the surface and slides straight out of the sum.

The magnetic law has the same shape with two words changed. Take a closed *loop*, walk
round it, and at each step add the component of $\vec B$ that lies along your direction of
travel. The total is proportional to the current threading the loop:

$$\oint \vec B \cdot \mathrm{d}\vec\ell = \mu_0 I_{\text{enc}}$$

$I_{\text{enc}}$ is the net current passing through any surface the loop bounds, counted
with sign: currents one way add, currents the other way subtract. Two conductors carrying
5 A in opposite directions through the same loop enclose nothing, and contribute nothing
— which is why a two-core mains flex barely disturbs a compass while a single conductor
carrying the same current disturbs it a great deal.

The constant is the **permeability of free space**,

$$\mu_0 = 4\pi\times10^{-7}\ \mathrm{H/m} = 1.2566\times10^{-6}\ \mathrm{H/m}$$

Until the 2019 redefinition of the SI that value was exact by definition — the ampere was
*defined* through it — and it is now a measured quantity that agrees with
$4\pi\times10^{-7}$ to about ten digits. Either spelling is fine; the lab at the end of
this module uses $1.25663706212\times10^{-6}$.

## The straight wire, in one line

Symmetry does the work, exactly as it did for Gauss. The wire is long and looks the same
from every direction round it, so $B$ can depend only on the distance $r$; and the compass
told us it is tangential. Choose the Ampèrian loop to be a circle of radius $r$ centred on
the wire. Then $\vec B$ is parallel to $\mathrm{d}\vec\ell$ at every point of that circle,
and constant in magnitude along it, so the integral is simply $B$ times the circumference:

$$B\,(2\pi r) = \mu_0 I \qquad\Longrightarrow\qquad B = \frac{\mu_0 I}{2\pi r}$$

Read the power on $r$. It is **one**, not two. The pull towards $1/r^2$ is strong because
Coulomb's law is fresh, and it is wrong by a whole factor of $r$ — going from one
centimetre to ten, that is a factor of ten in the answer. The reason for the difference is
geometric and you have already met it: in module 2 an infinite *line* of charge also gave
$1/r$, because what spreads out from a line spreads over a cylinder, and a cylinder's area
grows in proportion to $r$ rather than to $r^2$. A point feeds a sphere; a line feeds a
cylinder. Same style of law, different geometry, different power.

## Worked: how strong, and how close

A wire carries 8.0 A. What is the field 5.0 cm away?

```text
mu0 / (2 pi) = 4 pi e-7 / (2 pi)              = 2.0e-7  T m / A

B = 2.0e-7 * I / r
  = 2.0e-7 * 8.0 / 0.050
  = 1.6e-6 / 0.050                            = 3.2e-5 T   = 32 uT
```

Thirty-two microtesla, against the Earth's 30–60 µT. A compass held five centimetres from
a wire carrying eight amps is fighting a field comparable to the one it is meant to be
reading, and it will settle somewhere between north and tangential. That is precisely what
Ørsted saw.

Now turn the formula round. How close would you have to get for that wire to make a
millitesla — still only a fifth of a fridge magnet?

```text
r = mu0 I / (2 pi B) = 2.0e-7 * 8.0 / 1.0e-3
  = 1.6e-6 / 1.0e-3                           = 1.6e-3 m   = 1.6 mm
```

Inside the insulation, in other words. A single straight wire is a hopeless magnet. To get
a useful field out of a modest current you have to arrange for the same current to pass the
same point many times over — which is a coil, and it is why every magnetic component in the
rest of this course is wound rather than straight.

## The solenoid: the same law, a different loop

Wind $N$ turns tightly into a cylinder of length $\ell$, with $\ell$ much greater than the
diameter. Inside such a coil the field is uniform and runs along the axis; outside, the
returning flux is spread through the whole of the surrounding space and is very nearly zero
close alongside the winding. Take those two facts as given for a moment — they are what the
picture of closed loops forces — and Ampère's law supplies the rest.

Choose a rectangular loop with one side of length $L$ running along the axis inside the
coil, the opposite side outside it, and the two short sides crossing the winding.

```text
inside side, length L, B parallel to the path   contributes   B * L
outside side                                    contributes   0      (B ~ 0 there)
the two crossing sides                          contribute    0      (B perpendicular)
                                                -----------------
total round the loop                            =  B * L

turns threaded by the loop = (N / l) * L = n L,  each carrying I
so  I_enc = n L I

B L = mu0 n L I     ->     B = mu0 n I
```

The length $L$ of the rectangle cancels, which is the sign that the answer belongs to the
winding rather than to the loop you happened to draw. With $n = N/\ell$ as the turns per
metre,

$$B = \mu_0 n I = \frac{\mu_0 N I}{\ell}$$

Note what is *not* in it: the cross-sectional area. A fat solenoid and a thin one with the
same turns per metre and the same current have the same field inside. The area matters
later, when we ask how much flux that field carries, which is the next reading unit.

## Worked: the coil this module ends with

The lab winds 500 turns over 20 cm on a former of cross-section 1.0 cm². Run 0.20 A through
it.

```text
n = N / l = 500 / 0.20                        = 2500 turns per metre

B = mu0 n I
  = 1.2566e-6 * 2500 * 0.20
  = 1.2566e-6 * 500                           = 6.283e-4 T  = 628 uT

flux through one turn, area A = 1.0 cm^2 = 1.0e-4 m^2:
Phi = B A = 6.283e-4 * 1.0e-4                 = 6.283e-8 Wb = 62.8 nWb
```

628 microtesla is roughly ten times the Earth's field and about an eighth of a fridge
magnet's: a coil holding some eighteen metres of wire, drawing a fifth of an amp, and
still feeble. Two things fix that in practice and this course does both — push the current
up, and count the heat that costs in module 6; or fill the middle with iron, which
multiplies $B$ by a relative permeability $\mu_r$ of a few thousand for a soft ferrite, and
module 8 is about what that buys and what it costs.

The 62.8 nWb per turn is the number the next reading unit picks up.

## The law with a zero on the right

Draw any closed surface you like — round one pole of a bar magnet, round a current-carrying
wire, round the whole apparatus — and add up the magnetic field poking through it. The
answer is always exactly zero:

$$\oint \vec B \cdot \mathrm{d}\vec A = 0$$

That is Gauss's law for magnetism, and it is a strong statement rather than a triviality.
The electric version has the enclosed charge on the right, and that is exactly what makes
charge measurable from outside without opening the box. Here the right-hand side is zero
because there is no magnetic charge to put there. Every line that enters the surface leaves
it again somewhere else.

The experimental face of this is that cutting a magnet in half does not leave you holding a
north pole in one hand and a south pole in the other. It leaves you holding two complete
magnets, and you can go on cutting down to the individual atom without ever isolating one
end. People have hunted an isolated pole — a magnetic monopole — for a century, in cosmic
rays, in moon rock and in accelerator debris, and nobody has produced one. Until somebody
does, the right-hand side stays zero, and this is one of the four equations module 10
assembles.

## The mistakes people make

**Writing $1/r^2$ for the wire.** The commonest slip in the module, and tempting because
three modules of inverse squares have just gone past. The test is to ask what the source
looks like: a point feeds a sphere and gives an inverse square, a line feeds a cylinder and
gives an inverse first power.

**Pointing the field at the wire.** Nearly everyone's first sketch has arrows radiating from
the conductor, because every field picture so far has looked like that. The magnetic field
circles. If your sketch has field lines that begin somewhere, you have drawn an electric
field.

**Using $B = \mu_0 n I$ where it does not apply.** The result is for the inside of a long
coil, well away from the ends. At the mouth of a solenoid the field is about *half* the
interior value, because the lines have already begun to spread; outside, alongside the
winding, it is small but not zero. A short, fat coil never reaches $\mu_0 n I$ anywhere at
all, and that is the reason a real short coil's measured inductance always comes out below
the formula the next units use.

## Where this stops

**Steady currents only.** Ampère's law as written above is exactly true only when nothing is
changing in time, and the failure is easy to stage. Charge a capacitor, and draw an Ampèrian
loop round the wire feeding it. Span that loop with a flat disc and the wire pierces it, so
$I_{\text{enc}} = I$. Span the same loop with a bag that dips down between the capacitor
plates and no current passes through it at all, so $I_{\text{enc}} = 0$. One loop cannot
have two answers. Maxwell's repair — an extra term on the right standing for the changing
electric field in the gap — is module 10, and it is the term that makes radio possible.

**Long, straight, and alone.** $B = \mu_0 I / 2\pi r$ assumes a wire much longer than $r$
with nothing else nearby. For a finite segment, a bend, or a single loop, the symmetry
argument has nothing to bite on and you must add up the contributions of the individual
current elements — the Biot–Savart law, which stands to Ampère's law roughly as Coulomb's
law stands to Gauss's.

**Vacuum, or something close to it.** $\mu_0$ belongs to empty space. Put iron in the way and
the material's own atomic currents add to the field, multiplying it by a factor that can
reach several thousand — and unlike a dielectric constant, that factor is not constant. It
collapses as the iron saturates. Superposition, which has held without a single exception
since module 1, genuinely fails there, and module 8 is about what to do instead.
''',
                },
                {
                    "title": "Flux, Faraday, and what the minus sign is for",
                    "minutes": 16,
                    "body": r'''
Connect a coil of wire to a sensitive meter and nothing else. Hold a bar magnet inside it
and the meter reads zero, however strong the magnet is. Move the magnet in and the needle
kicks; stop, and it falls back to zero; pull the magnet out and it kicks the other way.
Move it faster and the kick is bigger. Leave the magnet still and move the *coil* instead
and you get exactly the same readings.

Nothing about the size of the field appears anywhere in that. What the coil responds to is
the *change*. Faraday spent ten years chasing this, having reasoned from Ørsted that if a
current makes a field then a field ought to make a current, and finding — as everyone before
him had found — that a steady field placed near a steady coil does nothing whatever. The
effect is entirely in the derivative, and that single fact is the whole of electrical power
generation, every transformer ever wound, and the reason the mains alternates.

## Counting the lines: flux

To turn "the change" into a number we need a quantity to differentiate, and it is not the
field. It is the *flux* — the amount of field passing through the loop, which is the field
strength multiplied by the area it passes through:

$$\Phi = B A \cos\theta$$

for a flat loop of area $A$ in a uniform field $B$, where $\theta$ is the angle between the
field and the normal to the loop. In general it is $\Phi = \int \vec B \cdot \mathrm{d}\vec
A$, the same surface integral module 2 used for electric flux and for the same reason: it
counts field lines through a surface.

The $\cos\theta$ deserves a sentence rather than a memorisation. A loop face-on to the field
intercepts every line in its shadow, so $\theta = 0$ and the flux is $BA$. Turn the loop
edge-on and the lines slide past without crossing it at all: $\theta = 90°$ and the flux is
zero. In between, the loop's *projected* area — its shadow cast along the field — is
$A\cos\theta$, and that is what the lines actually see.

The unit is the tesla square metre, given the name **weber**. Fluxes in ordinary equipment
are small: the coil at the end of the last unit carried 62.8 nWb through each turn, and even
a transformer core running at a tesla through a 10 cm² window carries only 1 mWb.

## Faraday's law

$$\mathcal{E} = -\frac{\mathrm{d}\Phi}{\mathrm{d}t}$$

The voltage driven round the loop equals the rate at which the flux through it changes. This
is not a voltage *across* anything in the ordinary sense; it is an emf, a push distributed
round the whole loop, which is why a coil with no battery in it anywhere can drive a current
round itself.

For a coil of $N$ turns, each turn is its own loop and they are in series, so their emfs add:

$$\mathcal{E} = -N\frac{\mathrm{d}\Phi}{\mathrm{d}t}$$

where $\Phi$ is the flux through *one* turn. That factor of $N$ is the cheapest gain in
electrical engineering. It costs wire and nothing else, and it is why a 240-turn search coil
gives volts where a single loop gives millivolts.

There are exactly three ways to make $\Phi = BA\cos\theta$ change, and each one is a piece of
equipment:

* **change $B$** — a transformer, an induction hob, a wireless charger, a metal detector;
* **change $A$** — the sliding-rod experiment later in this unit, and every linear generator;
* **change $\theta$** — spin the loop, and you have built an alternator.

## Worked: a coil in a rising field

A 150-turn coil of area 8.0 cm² lies face-on in a field that is ramped from zero to 0.60 T
in 40 ms. What voltage appears across its ends while the ramp is running?

```text
A   = 8.0 cm^2 = 8.0e-4 m^2

flux through one turn at the end of the ramp:
Phi = B A     = 0.60 * 8.0e-4                 = 4.8e-4 Wb

the ramp is linear, so dPhi/dt is constant:
dPhi/dt       = 4.8e-4 / 0.040                = 1.2e-2 Wb/s

emf = N * dPhi/dt
    = 150 * 1.2e-2                            = 1.8 V
```

Three things to take from that. The 1.8 V lasts exactly as long as the ramp: at 40 ms it
stops dead, whatever the field is doing afterwards, because a field held at 0.60 T has no
rate of change. Reverse the ramp — collapse the field from 0.60 T back to zero in the same
40 ms — and you get 1.8 V of the opposite sign. And tilt the coil to 60° away from face-on,
and every number above is multiplied by $\cos 60° = 0.5$:

```text
Phi = B A cos(60 deg) = 0.60 * 8.0e-4 * 0.5   = 2.4e-4 Wb
emf = 150 * 2.4e-4 / 0.040                    = 0.90 V
```

## Worked: the alternator, and where 50 Hz comes from

Now spin a coil instead of ramping a field. A 200-turn coil of area 50 cm² sits in a 0.25 T
field and is turned at 3000 revolutions per minute about an axis across the field. The angle
is $\theta = \omega t$, so

$$\Phi = BA\cos\omega t \qquad\Longrightarrow\qquad
\mathcal{E} = -N\frac{\mathrm{d}\Phi}{\mathrm{d}t} = N B A \omega \sin\omega t$$

Differentiating the cosine brings out a factor of $\omega$ and turns it into a sine, so a
uniformly rotating loop produces a sinusoid whose amplitude is proportional to the speed.
Nobody chose that; it falls out of the geometry, and it is the reason the mains is a sine
wave rather than some other shape.

```text
omega = 3000 rev/min = 3000/60 rev/s = 50 rev/s
      = 50 * 2 pi                              = 314.16 rad/s
so the output frequency is                     = 50 Hz

peak emf = N B A omega
         = 200 * 0.25 * 5.0e-3 * 314.16
         = 0.25 * 314.16                       = 78.54 V peak

rms = peak / sqrt(2) = 78.54 / 1.4142          = 55.5 V rms
```

Fifty hertz out of a two-pole machine turning at 3000 rpm, which is exactly why that is the
standard speed for a European turbo-alternator. Double the speed and you double both the
frequency and the voltage, because the $\omega$ appears once — which is why a bicycle
dynamo's lamp brightens as you pedal harder.

## The minus sign, which is not decoration

Lenz's law is the statement that the sign is negative: *the induced current flows in the
direction that opposes the change which produced it.* Push a north pole towards a coil and
the coil presents a north face and pushes back. Pull it away and the coil presents a south
face and tries to hold on.

The argument for it is energy, and it is worth running to the end because it is the cleanest
"this had to be so" in the course. Suppose the sign were positive. Nudge a magnet towards a
coil. The induced current would attract it, so it accelerates inwards. Moving faster, it
induces more current, so it is attracted harder, so it accelerates more. The magnet arrives
at the coil with kinetic energy that came from nowhere, and the coil has been dissipating
heat in its own resistance the whole way. Energy conservation forbids that in one line, and
the minus sign is what enforces it.

You can feel Lenz's law directly. Drop a small neodymium magnet down a copper pipe and it
takes several seconds to fall a metre, drifting rather than dropping. The pipe is not
magnetic and the magnet never touches it. Circulating currents induced in the copper oppose
the magnet's arrival and then oppose its departure, and the gravitational energy that would
have become speed becomes heat in the pipe instead.

## Worked: the sliding rod, where the accounting closes exactly

The neatest quantitative version. Two horizontal rails 0.25 m apart, joined at one end by a
0.50 Ω resistor, standing in a vertical field of 0.40 T. A rod lies across the rails and is
pushed along them at a steady 3.0 m/s.

The circuit is a rectangle whose area grows as the rod advances: in a time $\mathrm{d}t$ the
rod moves $v\,\mathrm{d}t$ and the enclosed area grows by $\ell v\,\mathrm{d}t$. So

```text
dPhi/dt = B * l * v = 0.40 * 0.25 * 3.0         = 0.30 Wb/s
emf     = 0.30 V

current  I = emf / R = 0.30 / 0.50              = 0.60 A

the rod now carries 0.60 A across a 0.40 T field, so it feels a force
F = B I l = 0.40 * 0.60 * 0.25                  = 0.060 N
(pointing backwards - Lenz again - so you must push to hold the speed)

mechanical power you supply = F v = 0.060 * 3.0      = 0.18 W
electrical power dissipated = emf * I = 0.30 * 0.60  = 0.18 W
```

The two powers are equal, to the last digit, and nothing was arranged to make them so. That
identity *is* Lenz's law with numbers on it: the mechanical work done against the magnetic
drag is exactly the electrical energy that appears in the resistor. Take the resistor out —
make $R$ infinite — and no current flows, no force resists the rod, and it needs no pushing
at all. Short the rails with a thick wire instead and the rod becomes very hard to move.
Every generator on the grid is this experiment, and the "load" a power station feels is
precisely this force.

There is a second route to the same 0.30 V, and it is worth seeing because the two arguments
look nothing alike. Forget flux entirely. The rod is a piece of metal moving at $v$ through a
field $B$, so every free charge inside it is moving too and feels $F = qvB$ pushing it along
the rod's length. Divide by $q$ and that is an effective field of $vB$ inside the metal;
multiply by the rod's length and it is a potential difference of $B\ell v = 0.40 \times 0.25
\times 3.0 = 0.30$ V. One argument counts field lines through a growing loop; the other
pushes on individual electrons; they agree exactly. Einstein opens the 1905 relativity paper
by pointing out that this agreement looks like a coincidence and probably is not.

## The mistakes people make

**Confusing a large flux with a large emf.** Someone will always put the coil against the
strongest magnet available and be surprised the meter sits at zero. Faraday's law contains no
$\Phi$ at all, only $\mathrm{d}\Phi/\mathrm{d}t$. The quiz asks this and it is not a trick.

**Dropping the $N$.** The $\Phi$ in the formula is the flux through *one* turn, and without
the turn count the answer is $N$ times too small. For the 240-turn coil in the drills below
that is a factor of 240 — not a rounding error, a different answer entirely.

**Dropping the minus sign because only the magnitude was asked for.** You can get away with
that in a single-loop calculation. You cannot in the next unit, where the coil is driven by
its own current: there the sign is the difference between a component that opposes change and
one that runs away.

**Forgetting to convert the area.** A coil quoted in cm² is a factor of $10^{4}$ away from
m². A large share of all wrong answers to induction problems are exactly this.

## Where this stops

**When the circuit is not a well-defined loop.** "The flux through the loop" needs there to be
a loop that stays the same loop. In machines where the conducting path changes identity as
things move — a homopolar generator, a disc spinning on an axle with a brush pressed to its
rim — the flux rule can give the wrong answer while the underlying physics stays perfectly
consistent. The safe move is to fall back on the two things the flux rule stands in for: a
changing $B$ makes a circulating electric field, and a charge moving through a $B$ feels
$q\vec v \times \vec B$. Module 10 writes the first of those as one of Maxwell's equations.

**When the field is not quasi-static.** All of the above assumes that when the source current
changes, the field everywhere changes with it at the same instant. It does not — the news
travels at the speed of light — and once the apparatus is comparable in size to a wavelength,
"the flux through the loop" stops being a useful idea and radiation takes over. At 50 Hz a
wavelength is 6000 km and you may safely ignore all of this. At 2.4 GHz it is 12 cm, and a
loop of wire is an antenna whether you wanted one or not.

**When the emf has nowhere sensible to be measured.** Because the induced electric field
circulates, "the voltage between two points" inside a region of changing flux depends on which
way round the leads of your voltmeter go. Two meters clipped to the same two points, with
their leads routed on opposite sides of a changing-flux region, genuinely read different
numbers. Nothing is broken: the potential simply stops being single-valued once the field is
changing, and that is the first casualty of leaving electrostatics behind.
''',
                },
                {
                    "title": "A coil that fights its own change: inductance",
                    "minutes": 14,
                    "body": r'''
Wire a relay coil to a battery through a switch, and then open the switch. A blue spark snaps
across the contacts, and if you do it often enough the contacts burn away. The battery is
12 V; the spark needs several hundred. Nothing in the circuit can make several hundred volts
— and yet there it is, every time, and only ever at switch-off.

That spark is this whole unit in one observation. The coil has a current in it, the switch
tries to take that current to zero in a microsecond, and the coil produces whatever voltage
is required to argue about it.

## A coil links its own flux

The last unit had a coil sitting in somebody else's field. Now let it make its own. Push a
current $I$ through a coil and, by the unit before that, it produces a field; and that field
passes through the very turns that are making it. The coil links its own flux.

Everything in sight is linear — the field is proportional to the current, and the flux is
proportional to the field — so the total flux linkage, meaning the flux through one turn
multiplied by the number of turns that link it, is proportional to the current. Give the
constant of proportionality a name:

$$L = \frac{N\Phi}{I}$$

and then Faraday's law, applied to the coil's own flux, says

$$v = L\frac{\mathrm{d}i}{\mathrm{d}t}$$

Read that carefully, because it is the component's entire behaviour and it is easy to
misread. The voltage across an inductor is set by the *rate of change* of its current, not by
the current. Hold the current steady at ten amps and the voltage across the coil is zero. Let
the current move, and a voltage appears that opposes the movement — Lenz's law again, now
applied to a coil arguing with itself.

The unit of $L$ is the weber-turn per amp, named the **henry**. Like the farad it is a large
unit: practical parts run from nanohenries — a centimetre of straight wire is about 10 nH —
to tens of millihenries, with the henry itself reserved for mains chokes with iron in them.

## Where the square on the turns comes from

For a long solenoid the first reading unit gave $B = \mu_0 N I/\ell$ inside. The flux through
one turn is $\Phi = BA$, and all $N$ turns link it, so

$$L = \frac{N\Phi}{I} = \frac{N B A}{I} = \frac{\mu_0 N^2 A}{\ell}$$

and the derivation unit in this module walks that chain through one link at a time, then
keeps going. The turn count is *squared*, and the reason is worth holding on to, because it
is not arithmetic — it is bookkeeping done twice. Doubling the turns doubles the field the
coil makes for a given current, which is one factor of $N$; and it doubles the number of
turns sitting in that field to link it, which is the other. Every turn you add both makes
more flux and catches more of it.

## Worked: a real coil, and what a bigger one would cost

Take the coil the lab measures: 500 turns wound over 20 cm on a former of cross-section
1.0 cm², with air in the middle.

```text
N^2 = 500^2                                     = 2.5e5
A/l = 1.0e-4 / 0.20                             = 5.0e-4 m

L   = mu0 * N^2 * A / l
    = 1.2566e-6 * 2.5e5 * 5.0e-4
    = 1.2566e-6 * 125                           = 1.5708e-4 H  = 157 uH
```

157 microhenries. Now suppose the design calls for 10 mH — a common enough value, and the one
the build exercise uses. Since $L \propto N^2$:

```text
ratio needed = 10e-3 / 157.08e-6                = 63.66
turns needed = 500 * sqrt(63.66) = 500 * 7.979  = 3989   (call it 3990)

check: L = 1.2566e-6 * 3990^2 * 1.0e-4 / 0.20   = 1.0003e-2 H   ok
```

Four thousand turns in the same 20 cm — about 140 m of wire, in as many layers as it takes.
With wire fine enough to fit, the winding resistance alone would run into the hundreds of
ohms, and the part would be useless as an inductor and serviceable only as a heater. This is the moment iron earns its keep: filling the core multiplies $L$ by
$\mu_r$, so a ferrite with $\mu_r = 2000$ reaches 10 mH in about ninety turns rather than four
thousand. Module 8 presents the bill — saturation, hysteresis loss, and an inductance that is
no longer a constant.

## Energy: how much, and where

Charging a coil takes work, for the same reason charging a capacitor does. At the instant the
current is $i$, the voltage across the coil is $L\,\mathrm{d}i/\mathrm{d}t$, so the power
being delivered into it is $p = vi = L i\,\mathrm{d}i/\mathrm{d}t$, and the energy is the
integral of that:

$$W = \int_0^{I} L\,i\,\mathrm{d}i = \tfrac{1}{2}L I^2$$

The magnetic twin of $\tfrac{1}{2}CV^2$, with the current standing where the voltage stood.
And exactly as in module 3, the energy is not in the wire; it is in the field, at a density

$$u = \frac{B^2}{2\mu_0}$$

which the derivation unit gets out of the solenoid. Put numbers on both sides and the
comparison is startling:

```text
the 157 uH coil carrying 0.20 A:
W = 0.5 * 1.5708e-4 * 0.20^2                    = 3.14e-6 J   = 3.14 uJ

energy density in a 1 T field:
u = 1 / (2 * 1.2566e-6)                         = 3.98e5 J/m^3

energy density in air at its breakdown field of 3 MV/m (module 3):
u = 0.5 * 8.854e-12 * (3e6)^2                   = 39.8 J/m^3
```

Ten thousand times more energy per cubic metre in a one-tesla magnetic field than in the very
best electric field air can hold. That single ratio is why the world's motors, transformers
and switching converters are magnetic devices rather than electrostatic ones. The 3.14 µJ in
the little coil is not a counter-example; it is a statement about its volume and its field,
since 20 cm³ at 628 µT works out at 0.157 J/m³ — a very thin slice indeed of 3.98×10⁵.

## The RL circuit, and a time constant that divides

Put the coil in series with a resistor across a supply $V$ and close the switch. Kirchhoff's
voltage law round the loop gives $V = iR + L\,\mathrm{d}i/\mathrm{d}t$, whose solution — the
same first-order exponential EE111 solved for the RC circuit — is

$$i(t) = \frac{V}{R}\left(1 - e^{-t/\tau}\right), \qquad \tau = \frac{L}{R}$$

The time constant **divides** by the resistance. That is the opposite of $\tau = RC$, and it
is the most reliable mistake in the module. The reason is visible in the differential
equation: write it as $\mathrm{d}i/\mathrm{d}t = (V - iR)/L$ and the coefficient pulling $i$
towards its final value is $R/L$, so a bigger resistor is a stronger restoring term and the
circuit settles *faster*. In the capacitor case the resistor is what limits the charging
current, so a bigger one settles slower. Same word, opposite behaviour, because the resistor
is doing an opposite job.

## Worked: the circuit you are about to build

The build unit asks for $\tau = 159$ µs from a 5 V supply and suggests 10 mH with 62.8 Ω.

```text
tau = L / R = 0.010 / 62.8                      = 1.592e-4 s   = 159 us

final current  I = V / R = 5.0 / 62.8           = 79.6 mA
at t = tau,    i = 0.632 * 79.6 mA              = 50.3 mA
the probe sits across R, so v = iR:
               v(tau) = 0.632 * 5.0             = 3.16 V

as a filter corner:  fc = 1/(2 pi tau) = R/(2 pi L)
                        = 62.8 / (2 pi * 0.010) = 999.5 Hz  ~ 1 kHz
```

Now open the switch on that same circuit with 79.6 mA flowing, and suppose the contacts part
in a microsecond:

```text
v = L di/dt = 0.010 * 0.0796 / 1e-6             = 796 V
```

Eight hundred volts, from a five-volt supply. There is the spark from the opening paragraph,
with a number on it. It is also why every relay, solenoid valve and motor winding in a piece
of equipment has a diode across it: the diode gives the current somewhere to go while it
decays, and the coil never gets to demand a voltage the rest of the circuit cannot survive.

## Two limits worth memorising

**At DC an inductor is a piece of wire.** Once everything has settled,
$\mathrm{d}i/\mathrm{d}t = 0$, so the voltage across it is zero whatever current it happens
to be carrying. Both of the circuit drills below turn on this: the coil shorts out whatever
it is in parallel with, and its own branch current is decided by the resistance in series
with it.

**At high frequency an inductor is an open circuit.** $v = L\,\mathrm{d}i/\mathrm{d}t$ means
a rapidly alternating current needs a large voltage to drive it, so little current gets
through. A capacitor is exactly the other way round — a short at high frequency, an open at
DC — and that complementarity is what the sandbox at the top of this module is playing with.
Put the two in series and there is one frequency where their opposite behaviours cancel:

```text
L = 10 mH, C = 100 nF:
w0 = 1 / sqrt(L C) = 1 / sqrt(1.0e-2 * 1.0e-7)
   = 1 / sqrt(1.0e-9) = 1 / 3.162e-5             = 3.162e4 rad/s
f0 = w0 / (2 pi)                                 = 5.03 kHz
```

At that frequency energy sloshes between the coil's field and the capacitor's field twice per
cycle, and the source has only to make up what the resistance takes. That is why the sandbox
shows +20 dB across the capacitor at low damping without anything amplifying anything.

## The mistakes people make

**$\tau = LR$.** Covered above and worth repeating, because it is dimensionally plausible
until you check and it gives a confidently wrong answer. Henries per ohm are seconds;
henry-ohms are not.

**Believing an inductor resists current.** It resists *change* in current. The steady-state
current through an ideal inductor is limited by nothing at all, which is exactly why the DC
drills below work the way they do, and why an ideal inductor across a battery is a short
circuit that gets there slowly.

**Doubling the turns and doubling $L$.** Squared, not linear. It is also why a coil's
inductance is far more sensitive to how it is wound than to what you run through it.

## Where this stops

**Real inductors are not only inductors.** Every winding has resistance in series with it and
capacitance between its turns. Above the frequency where that turn-to-turn capacitance
resonates with the inductance — the self-resonant frequency — the part behaves as a
*capacitor*, and any data sheet that quotes 10 mH also quotes an SRF above which the number
is meaningless.

**The formula assumes a long coil.** $L = \mu_0 N^2 A/\ell$ came from $B = \mu_0 nI$, which
was derived for $\ell$ much greater than the diameter. For a coil as long as it is wide the
true inductance is some 30% lower, and handbooks supply a shape correction — Nagaoka's
coefficient — to patch it. The formula is a limit, exactly like the parallel-plate capacitor.

**With iron, $L$ is not a constant.** $\mu_r$ falls away as the core approaches saturation, so
a choke that measures 10 mH at 100 mA can be 3 mH at 2 A, and a converter designed as though
it were constant fails at exactly the moment it is worked hardest. Module 8 puts numbers on
that.

**One coil, one flux.** Everything here is about a coil linking its *own* flux. Put a second
coil nearby and it links some of the first one's flux as well, which is a mutual inductance —
and two coils sharing a core is a transformer, which is module 9.
''',
                },
            ],
            "sandbox": {
                "title": "A capacitor and an inductor in the same loop",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 0.5, "K": 1},
                "brief": r'''
Put a resistor, an inductor and a capacitor in series across a source and probe the
capacitor. The top panel is the size of the output as the source frequency is swept,
in decibels, as module 3 defined them: 0 dB means the output is the same size as the
source, $+20$ dB means ten times larger, $-20$ dB a tenth. The bottom panel is how far
the output lags the source, in degrees. Both are drawn for the response

$$\frac{1}{(1 - x^2) + j\,2\zeta x}, \qquad x = \frac{\omega}{\omega_n}$$

which is exactly what that circuit does, with $\omega_n = 1/\sqrt{LC}$ and
$\zeta = \tfrac{R}{2}\sqrt{C/L}$. So $\omega_n$ is the resonance set by the two energy
stores, and $\zeta$ is the damping the resistor adds. The third slider, $K$, is an
overall gain applied to the whole curve; leave it at 1 and the picture is the circuit
exactly.

The amber dot marks the response exactly at the resonant frequency.
''',
                "notice": [
                    "Pull $\\zeta$ down to 0.05 — a small series resistance. The amber dot climbs to +20 dB: the voltage across the capacitor is ten times the source voltage. Nothing is amplifying anything; energy is sloshing between the capacitor and the inductor and the source only tops it up.",
                    "Whatever you do to $\\zeta$, the lower curve crosses the dashed −90° line at exactly $\\omega_n$. Damping changes how sharp the transition is, never where it sits.",
                    "Above $\\omega_n$ the magnitude falls by 40 dB per decade — a factor of a hundred in size for every factor of ten in frequency. The RC filter you built in module 3 has one energy store and manages 20 dB per decade. Two energy stores, twice the roll-off.",
                    "Raise $\\omega_n$ and the whole picture slides right with its shape unchanged. Only the product $LC$ decides where the resonance is: halving $L$ and doubling $C$ leaves it exactly where it was.",
                ],
            },
            "derive": {
                "title": "A solenoid's inductance, and the energy in the field it makes",
                "minutes": 14,
                "vars": ["B", "I", "N", "A", "l", "L", "W", "u", "Phi", "mu_0"],
                "brief": r'''
The reading unit quoted $L = \mu_0 N^2 A / l$ and said in a sentence why the turn count is
squared. Here the whole chain is built, one link at a time, from Ampère's law to a statement
about the field that no longer mentions the coil at all.

The route is: field inside the winding, flux through one turn, flux linked by all $N$ turns,
inductance, energy, energy per unit volume. Two symbols cancel at the last step — the area
and the length — and watching them go is the point of doing it, exactly as it was for
$u = \tfrac{1}{2}\varepsilon_0 E^2$ in module 3.

Write the permeability of free space as `\mu_0`. Use $l$ for the length of the winding.
''',
                "steps": [
                    {
                        "prompt": "A long solenoid of $N$ turns over a length $l$ carries a current $I$. Ampère's law on a rectangle with one side inside the coil and one outside gives the field inside it. Write $B$ in terms of $\\mu_0$, $N$, $I$ and $l$.",
                        "answer": "\\frac{\\mu_0 N I}{l}",
                        "hint": "The turns per metre is $n = N/l$, and the field inside a long solenoid is $\\mu_0 n I$.",
                        "deconstruct": [
                            "Turns per metre: $n = N/l$.",
                            "Substitute that into $B = \\mu_0 n I$.",
                        ],
                    },
                    {
                        "prompt": "The winding sits on a former of cross-section $A$, and the field is uniform across it and along the axis. Write the flux $\\Phi$ through **one** turn, in terms of $\\mu_0$, $N$, $I$, $A$ and $l$.",
                        "answer": "\\frac{\\mu_0 N I A}{l}",
                        "placeholder": "the field, multiplied by an area",
                        "hint": "Flux is field times area when the field is uniform and the turn is face-on to it: $\\Phi = BA$.",
                        "deconstruct": [
                            "$\\Phi = B A$ with $B$ from the previous line.",
                            "Nothing cancels; the area simply multiplies in.",
                        ],
                    },
                    {
                        "prompt": "Every one of the $N$ turns is threaded by that same flux, and the turns are in series. Write the total flux linkage, $N\\Phi$.",
                        "answer": "\\frac{\\mu_0 N^2 I A}{l}",
                        "placeholder": "and here is where the square appears",
                        "hint": "Multiply by $N$. The $N$ already in the expression came from the field the coil makes; this second one counts the turns that link it.",
                        "deconstruct": [
                            "Multiply the flux through one turn by $N$.",
                            "$N \\times N = N^2$.",
                        ],
                    },
                    {
                        "prompt": "Inductance is the flux linkage per unit current: $L = N\\Phi / I$. Divide, and write $L$ in terms of $\\mu_0$, $N$, $A$ and $l$.",
                        "answer": "\\frac{\\mu_0 N^2 A}{l}",
                        "hint": "The current appears once in the numerator, so dividing by $I$ removes it entirely — which is the whole reason $L$ is a property of the coil and not of what you are doing with it.",
                        "deconstruct": [
                            "Divide the linkage by $I$.",
                            "The single factor of $I$ cancels outright.",
                        ],
                    },
                    {
                        "prompt": "Charging the coil to a current $I$ costs $W = \\tfrac{1}{2}LI^2$. Substitute the inductance you just found, and write $W$ in terms of $\\mu_0$, $N$, $A$, $I$ and $l$ — with no $L$ left in it.",
                        "answer": "\\frac{\\mu_0 N^2 A I^2}{2 l}",
                        "placeholder": "no L left",
                        "hint": "Put $\\mu_0 N^2 A / l$ where the $L$ was and keep the half and the $I^2$.",
                        "deconstruct": [
                            "$W = \\tfrac{1}{2}\\,(\\mu_0 N^2 A / l)\\,I^2$.",
                            "Collect it over a single denominator of $2l$.",
                        ],
                    },
                    {
                        "prompt": "That energy sits in the field, and the field fills the inside of the coil — a volume of $A l$. Divide by it, and write the energy per unit volume $u$ in terms of $\\mu_0$, $N$, $I$ and $l$.",
                        "answer": "\\frac{\\mu_0 N^2 I^2}{2 l^2}",
                        "placeholder": "no area left",
                        "hint": "$A$ appears exactly once in the numerator, so it cancels outright against the volume. The $l$ underneath meets the $l$ already there and becomes $l^2$.",
                        "deconstruct": [
                            "$u = W / (A l)$.",
                            "Cancel the $A$; the two factors of $l$ in the denominator combine.",
                        ],
                    },
                    {
                        "prompt": "The field inside the coil is $B = \\mu_0 N I / l$. Use it to eliminate $N$, $I$ and $l$ together, and write $u$ in terms of $B$ and $\\mu_0$ alone.",
                        "answer": "\\frac{B^2}{2 \\mu_0}",
                        "placeholder": "only B and mu_0 survive",
                        "hint": "$B^2 = \\mu_0^2 N^2 I^2 / l^2$, so $N^2 I^2 / l^2 = B^2/\\mu_0^2$. Substitute that and one power of $\\mu_0$ survives, in the denominator.",
                        "deconstruct": [
                            "Square the field: $B^2 = \\mu_0^2 N^2 I^2 / l^2$.",
                            "So $\\mu_0 N^2 I^2 / l^2 = B^2 / \\mu_0$.",
                            "Halve it.",
                        ],
                    },
                ],
                "closing": r'''
$$u = \frac{B^2}{2\mu_0}$$

No turns, no current, no area, no length, no coil. Every trace of the winding cancelled in the
last two lines, and what is left is a statement about the magnetic field itself: wherever there
is a field of strength $B$, there is this much energy in every cubic metre of it. It holds
inside a transformer core, in the gap of a motor, and in the field of a sunspot, none of which
is a solenoid.

Set it beside its electric twin from module 3 and compare the numbers rather than the shapes:

$$u_E = \tfrac{1}{2}\varepsilon_0 E^2, \qquad u_B = \frac{B^2}{2\mu_0}$$

Air gives up at about 3 MV/m, which caps $u_E$ at 39.8 J/m³. An ordinary iron-cored machine
works at about 1 T, giving $u_B = 1/(2 \times 1.2566\times10^{-6}) = 3.98\times10^{5}$ J/m³ —
ten thousand times more energy in the same cubic metre. That single ratio is the reason
electrical machines are magnetic devices. Nobody builds an electrostatic motor of any useful
size, and it is not for want of trying.

Two cautions about how far to push this. The volume $Al$ is the inside of the coil only, and
some field always leaks outside — for a long thin solenoid that is a small correction, and for
a short fat one it is not. And putting iron in the core replaces $\mu_0$ by $\mu_0\mu_r$
throughout, which *lowers* the energy density for a given $B$ rather than raising it: the iron
buys you a large $B$ for a small current, not extra storage. Where you actually want to store
magnetic energy — in a switching converter's choke — the energy piles up in the small air gap
deliberately cut in the core, for exactly this reason. Module 8 works that through.
''',
            },
            "blanks": {
                "title": "Ampère, Faraday and the coil, term by term",
                "minutes": 9,
                "caption": "the five relations this module runs on, with the load-bearing parts removed",
                "lang": "text",
                "brief": r'''
Nothing here is executed. These are the expressions the rest of the module is built on, and
the holes sit where a slip changes the answer rather than the spelling — the power on the
distance, the sign, and the two places where a quantity is squared.

Three of these have a distractor that is the *electric* version of the same idea. That is not
an accident: the two halves of the subject rhyme closely enough that reaching for the wrong
one is the standard failure, and it is better to meet it here than in the drills.
''',
                "listing": """# A long straight wire carrying a steady current I, at a distance r from it.

B = mu0 * I / ___             # Ampere's law, evaluated on a circle of radius r

# The flux through one flat turn of area A, tilted at theta to the field.

Phi = B * A * ___             # in webers

# Faraday's law for a coil of N turns. The sign is Lenz's law, and it is not optional.

emf = ___ * dPhi_dt           # dPhi_dt is the rate of change through ONE turn

# A solenoid: N turns wound over a length l, cross-section A, air in the middle.

L = mu0 * A * ___ / l         # in henries

# That coil switched onto a supply through a series resistance R:

tau = ___                     # seconds, to reach 63% of the final current

# and once the current has settled at I, the coil is holding

W = ___                       # joules, and they are in the field, not in the wire
""",
                "blanks": [
                    {
                        "prompt": "What goes under $\\mu_0 I$ for a straight wire?",
                        "hole": "?",
                        "opts": ["2*pi*r", "4*pi*r**2", "2*pi*r**2", "r"],
                        "a": 0,
                        "why": "The Ampèrian loop is a circle of radius $r$, and its circumference is $2\\pi r$. That is the only geometry in the derivation, so it is the only geometry in the answer — and it leaves a field falling off as $1/r$, not $1/r^2$.",
                        "whys": [
                            "The Ampèrian loop is a circle of radius $r$, and its circumference is $2\\pi r$. That is the only geometry in the derivation, so it is the only geometry in the answer — and it leaves a field falling off as $1/r$, not $1/r^2$.",
                            "This is the surface area of a sphere, and it belongs to the electric field of a point charge. Ampère's law integrates round a *loop*, so a length appears, never an area. A wire is a line of sources and its field spreads over a cylinder.",
                            "A tempting hybrid: the right $2\\pi$ with Coulomb's square attached. It gives a field that falls off as $1/r^2$, which is wrong by a whole factor of $r$ — a factor of ten between one centimetre and ten.",
                            "A bare $r$ has the right power but has lost the circumference of the loop, so every answer would come out $2\\pi = 6.28$ times too large. The $2\\pi$ is not a cosmetic constant; it is the length of the path you integrated along.",
                        ],
                    },
                    {
                        "prompt": "How does the tilt of the loop enter the flux?",
                        "hole": "?",
                        "opts": ["cos(theta)", "sin(theta)", "tan(theta)", "theta"],
                        "a": 0,
                        "why": "$\\theta$ is measured between the field and the *normal* to the loop, so face-on means $\\theta = 0$ and the full $BA$ passes through. Edge-on is $\\theta = 90°$ and nothing passes. The cosine is the loop's projected area — its shadow cast along the field — divided by its true area.",
                        "whys": [
                            "$\\theta$ is measured between the field and the *normal* to the loop, so face-on means $\\theta = 0$ and the full $BA$ passes through. Edge-on is $\\theta = 90°$ and nothing passes. The cosine is the loop's projected area — its shadow cast along the field — divided by its true area.",
                            "A sine is right only if you measure $\\theta$ from the plane of the loop rather than from its normal, and both conventions are in print. It is safer to fix the physics than the formula: face-on must give the maximum, edge-on must give zero, and then read off which function does that for your definition of the angle.",
                            "A tangent runs off to infinity at 90°, so an edge-on loop would carry unbounded flux. Nothing in the geometry can grow without limit — the flux can never exceed $BA$.",
                            "A bare angle is not even dimensionless in the right way: it would make the flux grow steadily as you turn the loop away from the field, which is the opposite of what happens.",
                        ],
                    },
                    {
                        "prompt": "What multiplies the rate of change of flux for an $N$-turn coil?",
                        "hole": "?",
                        "opts": ["-N", "N", "-1", "-1/N"],
                        "a": 0,
                        "why": "Each turn is a loop in its own right and they are wired in series, so their emfs add: that is the $N$. The minus sign is Lenz's law, and it is the part that stops the coil from being a free-energy machine — an induced current that reinforced its own cause would run away.",
                        "whys": [
                            "Each turn is a loop in its own right and they are wired in series, so their emfs add: that is the $N$. The minus sign is Lenz's law, and it is the part that stops the coil from being a free-energy machine — an induced current that reinforced its own cause would run away.",
                            "The magnitude is right and the sign is missing. You can get away with that on a single isolated loop where only the size was asked for; you cannot in the inductor of this module, where the sign is the difference between a component that opposes change and one that amplifies it without limit.",
                            "This is the single-turn law. Dropping the turn count is the commonest arithmetic error in induction problems, and for the 240-turn coil in the drills it is not a small error — it is a factor of 240.",
                            "Dividing by the turns has the relationship upside down. More turns give more voltage, not less; that is the entire reason coils are wound rather than left as single loops.",
                        ],
                    },
                    {
                        "prompt": "What power of the turn count sets the inductance?",
                        "hole": "?",
                        "opts": ["N**2", "N", "2*N", "sqrt(N)"],
                        "a": 0,
                        "why": "Squared, and the square is two separate pieces of counting. Doubling the turns doubles the field the coil produces for a given current — one factor — and then doubles the number of turns sitting in that field to link it — the other. Twice the turns is four times the inductance.",
                        "whys": [
                            "Squared, and the square is two separate pieces of counting. Doubling the turns doubles the field the coil produces for a given current — one factor — and then doubles the number of turns sitting in that field to link it — the other. Twice the turns is four times the inductance.",
                            "A single power would follow if the turns only linked an externally supplied field, which is the situation in Faraday's law. Here the coil is making the field it links, so the count enters twice.",
                            "Doubling is not squaring. This choice would make a 4000-turn coil only eight times the inductance of a 500-turn one, where the truth is sixty-four times — the difference between a workable design and an impossible one.",
                            "A square root would mean quadrupling the turns to double the inductance, so winding more wire would give steadily worse returns. It gives steadily better ones, which is why the practical limit on a coil is copper and space, not diminishing returns.",
                        ],
                    },
                    {
                        "prompt": "The RL time constant is:",
                        "hole": "?",
                        "opts": ["L/R", "L*R", "R/L", "L/R**2"],
                        "a": 0,
                        "why": "$\\tau = L/R$, in seconds. Rewrite the loop equation as $\\mathrm{d}i/\\mathrm{d}t = (V - iR)/L$ and the coefficient pulling the current towards its final value is $R/L$, so the time scale is its reciprocal. A bigger resistor makes an RL circuit settle *faster*.",
                        "whys": [
                            "$\\tau = L/R$, in seconds. Rewrite the loop equation as $\\mathrm{d}i/\\mathrm{d}t = (V - iR)/L$ and the coefficient pulling the current towards its final value is $R/L$, so the time scale is its reciprocal. A bigger resistor makes an RL circuit settle *faster*.",
                            "This is $\\tau = RC$ with an $L$ substituted for the $C$, and it is the most reliable mistake in the module because it is dimensionally plausible until you check. Henries per ohm are seconds; henry-ohms are not. For 10 mH and 100 Ω it gives 1 s where the truth is 100 µs — wrong by a factor of ten thousand.",
                            "This is the reciprocal, so it has units of inverse seconds. It is a perfectly good quantity — it is the rate constant in the exponential — but it is not the time constant.",
                            "The resistance appears once in the loop equation, not twice, so a second power cannot arise. The units give it away as well: henries per ohm squared is seconds per ohm.",
                        ],
                    },
                    {
                        "prompt": "And the energy the settled coil is holding?",
                        "hole": "?",
                        "opts": ["0.5 * L * I**2", "0.5 * L**2 * I", "L * I", "0.5 * C * V**2"],
                        "a": 0,
                        "why": "Integrate the power going in: $p = vi = L i \\,\\mathrm{d}i/\\mathrm{d}t$, so $W = \\int_0^I L i \\,\\mathrm{d}i = \\tfrac{1}{2}LI^2$. It is the magnetic twin of the capacitor's $\\tfrac{1}{2}CV^2$, with the current standing where the voltage stood.",
                        "whys": [
                            "Integrate the power going in: $p = vi = L i \\,\\mathrm{d}i/\\mathrm{d}t$, so $W = \\int_0^I L i \\,\\mathrm{d}i = \\tfrac{1}{2}LI^2$. It is the magnetic twin of the capacitor's $\\tfrac{1}{2}CV^2$, with the current standing where the voltage stood.",
                            "The square is on the wrong symbol. The integration was over the current, so it is the current that gets squared; the inductance was a constant and came straight out of the integral.",
                            "$LI$ is the flux linkage, in weber-turns — a real and useful quantity, but not an energy. Dropping the half and the square is what you get by assuming the voltage stayed at its final value throughout the charging, and it did not: it started at zero.",
                            "This is the capacitor's energy, which is the right shape for the wrong component. The pattern is worth fixing deliberately: a capacitor stores by voltage, an inductor stores by current, and each one's stored energy goes as the square of the quantity it cannot change abruptly.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "How strong is the field beside the wire?",
                    "minutes": 5,
                    "brief": r'''
The mechanical rung: one rule, one unknown, everything given. The only things it can catch
you on are the power on the distance and the centimetres, which is why it is written in
centimetres.
''',
                    "prompt": "How strong is the magnetic field at the point P?",
                    "note": "Give the answer in microtesla, to one decimal place.",
                    "figure": r'''
```text
   a long straight wire, seen end-on, carrying 8.0 A out of the page

              (x)  wire
               |
               |<----------- 5.0 cm ----------->|
               |                                |
                                                P

   the field at P is tangential - perpendicular, in the plane of the page,
   to the line drawn from the wire to P - and its size is what is asked for
```
''',
                    "given": [
                        {"label": "Current in the wire", "value": "8.0 A"},
                        {"label": "Distance from wire to P", "value": "5.0 cm"},
                        {"label": "Permeability of free space", "value": "4π × 10⁻⁷ H/m"},
                    ],
                    "aside": "$\\mu_0/2\\pi$ is exactly $2\\times10^{-7}$, which turns this into one "
                             "multiplication and one division. It is worth remembering as a number in "
                             "its own right.",
                    "answer": 32.0,
                    "tol": 0.4,
                    "unit": "µT",
                    "hint": "$B = \\mu_0 I / (2\\pi r)$, with $r$ in metres. Group the constants first: "
                            "$\\mu_0/(2\\pi) = 2.0\\times10^{-7}$.",
                    "wrong": "If you got 640, the distance was squared — that is Coulomb's law's power, "
                             "not this one. If you got 0.32, the 5.0 cm went in as 5.0 metres. If you "
                             "got 201, the $2\\pi$ was dropped and only $\\mu_0$ divided by $r$.",
                    "why": "Ampère's law on a circle of radius $r$ round the wire gives $B(2\\pi r) = "
                           "\\mu_0 I$, so $B = \\mu_0 I/(2\\pi r) = 2.0\\times10^{-7} \\times 8.0 / 0.050 "
                           "= 3.2\\times10^{-5}$ T, which is 32 µT. Two things are worth noticing about "
                           "that number. It is comparable to the Earth's own 30–60 µT, which is why a "
                           "compass near a wire is genuinely confused rather than slightly perturbed — "
                           "Ørsted's original observation. And it falls off as $1/r$, so at 10 cm it is "
                           "16 µT, not 8 µT: a wire is a line of sources and its field spreads over a "
                           "cylinder, whose area grows in proportion to $r$ rather than to $r^2$.",
                },
                {
                    "title": "The search coil in a rising field",
                    "minutes": 7,
                    "brief": r'''
Faraday's law, applied directly, with two unit conversions and one factor that people leave
out. A search coil like this is a real instrument: it is how the field in a magnet gap is
measured when a Hall probe would be in the way.

The field is ramped *linearly*, so the rate of change of flux is the same at every instant
during the ramp and there is no calculus to do — just a difference divided by a time.
''',
                    "prompt": "What voltage appears across the coil's ends while the field is ramping?",
                    "note": "Give the magnitude in volts, to two decimal places.",
                    "figure": r'''
```text
   a flat search coil lying face-on in a uniform field that is ramped up

        N = 240 turns, enclosed area 12 cm^2 each
        +-----------------------------+
        |   ) ) ) ) ) ) ) ) ) ) ) )   |      B is out of the page and the
        |   ) ) ) ) ) ) ) ) ) ) ) )   |      same everywhere across the coil
        +-----------------------------+
                  |       |
                  o       o   to the voltmeter

   the ramp:   B = 0  at t = 0     ->     B = 0.45 T  at t = 30 ms,
               and it rises in a straight line in between
```
''',
                    "given": [
                        {"label": "Turns", "value": "240"},
                        {"label": "Area of one turn", "value": "12 cm²"},
                        {"label": "Field at the end of the ramp", "value": "0.45 T"},
                        {"label": "Ramp duration", "value": "30 ms"},
                    ],
                    "aside": "Work out the flux through *one* turn first, then the rate at which it "
                             "changes, and only then bring in the turn count. Doing it in that order "
                             "makes the missing factor impossible to miss.",
                    "answer": 4.32,
                    "tol": 0.05,
                    "unit": "V",
                    "hint": "$\\Phi = BA$ for one turn, with $A$ in m². The ramp is linear, so "
                            "$\\mathrm{d}\\Phi/\\mathrm{d}t = \\Delta\\Phi/\\Delta t$. Then multiply by "
                            "$N$.",
                    "wrong": "If you got 0.018, the turn count was left out — that is the emf of a single "
                             "loop. If you got 43 200, the area went in as 12 rather than 12 cm² in m².",
                    "why": "One turn encloses $A = 12\\ \\text{cm}^2 = 1.2\\times10^{-3}$ m², so at the "
                           "end of the ramp the flux through it is $\\Phi = BA = 0.45 \\times 1.2\\times"
                           "10^{-3} = 5.4\\times10^{-4}$ Wb. The ramp is straight, so the rate of change "
                           "is constant at $5.4\\times10^{-4}/0.030 = 1.8\\times10^{-2}$ Wb/s. All 240 "
                           "turns link that flux and their emfs add in series, so $\\mathcal{E} = N\\,"
                           "\\mathrm{d}\\Phi/\\mathrm{d}t = 240 \\times 1.8\\times10^{-2} = 4.32$ V. The "
                           "sign is negative by Lenz's law, meaning the coil drives current the way that "
                           "would oppose the rise; the magnitude is what a meter reads. Note that the "
                           "4.32 V lasts exactly as long as the ramp and not one moment longer: hold the "
                           "field at 0.45 T and the reading falls to zero, however strong the field is.",
                },
                {
                    "title": "The current the coil settles at",
                    "minutes": 9,
                    "brief": r'''
A circuit now, and the first one where the inductor has to be *read* rather than calculated
with. Long after the switch closed, nothing is changing any more, so $\mathrm{d}i/\mathrm{d}t
= 0$ and the voltage across the coil is zero whatever current it carries. An inductor at DC is
a piece of wire.

That turns the picture into a resistor problem — but not the one it looks like, because the
coil's branch and the 60 Ω branch are then in parallel across the same two nodes, and only
part of the supply current goes down each.

The 25 mH is honest information about the part and plays no role whatever in the answer.
''',
                    "prompt": "Once everything has settled, how much current flows through the inductor?",
                    "note": "Give the answer in milliamps, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 40},
                            {"id": "r2", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 60},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "l1", "kind": "L", "x": 17, "y": 5, "rot": 1, "value": 0.025},
                            {"id": "r3", "kind": "R", "x": 17, "y": 8, "rot": 1, "value": 20},
                            {"id": "g2", "kind": "GND", "x": 17, "y": 11},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [17, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [17, 3], "b": [17, 4]},
                            {"a": [17, 6], "b": [17, 7]},
                            {"a": [17, 9], "b": [17, 11]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12 V"},
                        {"label": "Series resistor", "value": "40 Ω"},
                        {"label": "Shunt resistor", "value": "60 Ω"},
                        {"label": "In series with the coil", "value": "20 Ω"},
                        {"label": "Inductance", "value": "25 mH"},
                    ],
                    "aside": "Replace the coil with a plain wire on your sketch before doing any "
                             "arithmetic. What is left is a divider feeding two parallel branches, and "
                             "you have solved that shape since EE101.",
                    "answer": 163.6,
                    "tol": 1.0,
                    "unit": "mA",
                    "check": r'''
const d = c.dc();
const coil = c.net.parts.filter(function (p) { return p.kind === 'L'; })[0];
return Math.abs(d.currents[coil.id]) * 1000;
''',
                    "hint": "With the coil as a wire, the 60 Ω and the 20 Ω hang from the same node. "
                            "Find that node's voltage first, then divide it by 20 Ω.",
                    "wrong": "If you got 218.2, that is the total current out of the supply — all of it, "
                            "before the two branches split it. If you got 300, the 40 Ω was left out and "
                            "the supply was applied straight across the coil's branch.",
                    "why": "At DC the coil holds no voltage across it, so the 20 Ω branch and the 60 Ω "
                           "branch are simply in parallel: $60\\parallel20 = 1200/80 = 15\\ \\Omega$. "
                           "That 15 Ω is in series with the 40 Ω, so the supply sees 55 Ω and delivers "
                           "$12/55 = 218.2$ mA, and the junction sits at $12 \\times 15/55 = 3.273$ V. "
                           "The coil's branch takes $3.273/20 = 163.6$ mA of that, and the 60 Ω takes "
                           "the remaining $3.273/60 = 54.5$ mA — which do indeed add back to 218.2 mA. "
                           "The 25 mH decides how long the settling takes and nothing else: with a "
                           "Thévenin resistance of $20 + (40\\parallel60) = 44\\ \\Omega$ seen by the "
                           "coil, that is $\\tau = 0.025/44 = 568$ µs, so 'settled' here means a few "
                           "milliseconds.",
                },
                {
                    "title": "The energy left in the coil's field",
                    "minutes": 12,
                    "brief": r'''
The last rung, and the quantity asked for is not a voltage, not a current, and not anything the
solver reads off a node. There are three routes into the middle node — a supply through a
resistor, a resistor to ground, and a constant-current load pulling 50 mA out of it — and the
coil's branch hangs off the same node again.

The constant-current source is the piece to be careful with. It takes 50 mA out of the top
node no matter what the voltage there does, so it enters the node equation as a fixed current
rather than as a conductance, and it makes the node voltage *lower* than the resistors alone
would.

Once you have the coil's current, the energy is the magnetic twin of $\tfrac{1}{2}CV^2$.
''',
                    "prompt": "Once everything has settled, how much energy is stored in the inductor's field?",
                    "note": "Give the answer in microjoules, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 30},
                            {"id": "r2", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 60},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "i1", "kind": "I", "x": 15, "y": 6, "rot": 1, "value": 0.05},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "l1", "kind": "L", "x": 21, "y": 6, "rot": 1, "value": 0.04},
                            {"id": "r3", "kind": "R", "x": 21, "y": 9, "rot": 1, "value": 20},
                            {"id": "g3", "kind": "GND", "x": 21, "y": 12},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [21, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [15, 3], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [21, 3], "b": [21, 5]},
                            {"a": [21, 7], "b": [21, 8]},
                            {"a": [21, 10], "b": [21, 12]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "9.0 V"},
                        {"label": "Series resistor", "value": "30 Ω"},
                        {"label": "Shunt resistor", "value": "60 Ω"},
                        {"label": "Constant-current load", "value": "50 mA, drawn out of the top node"},
                        {"label": "In series with the coil", "value": "20 Ω"},
                        {"label": "Inductance", "value": "40 mH"},
                    ],
                    "aside": "Write one node equation for the rail: everything arriving equals everything "
                             "leaving. The coil is a wire, so its branch is just the 20 Ω to ground.",
                    "answer": 312.5,
                    "tol": 4.0,
                    "unit": "µJ",
                    "check": r'''
const coil = c.net.parts.filter(function (p) { return p.kind === 'L'; })[0];
const i = c.dc().currents[coil.id];
return 0.5 * coil.value * i * i * 1e6;
''',
                    "hint": "Let the rail be at $V$. Then $(V-9)/30 + V/60 + V/20 + 0.05 = 0$. Solve for "
                            "$V$, divide by 20 Ω for the coil's current, and finish with "
                            "$\\tfrac{1}{2}LI^2$.",
                    "wrong": "If you got 450, the current source was left out and the rail came out at "
                             "3.0 V. If you got 625, the half was dropped from $\\tfrac{1}{2}LI^2$.",
                    "why": "The coil is a short at DC, so the rail sees three conductances to ground and "
                           "one current being pulled out of it. Node equation, in siemens and amps: "
                           "$(V-9)/30 + V/60 + V/20 + 0.05 = 0$. The conductances total $1/30 + 1/60 + "
                           "1/20 = 2/60 + 1/60 + 3/60 = 0.100$ S, and the driving terms give $9/30 - "
                           "0.05 = 0.300 - 0.050 = 0.250$ A, so $V = 0.250/0.100 = 2.50$ V. The coil's "
                           "branch therefore carries $I = 2.50/20 = 125$ mA, and the field is holding "
                           "$W = \\tfrac{1}{2}LI^2 = 0.5 \\times 0.040 \\times 0.125^2 = 3.125\\times"
                           "10^{-4}$ J, which is 312.5 µJ. Two remarks. Without the 50 mA load the rail "
                           "would sit at 3.00 V and the stored energy would be 450 µJ — the energy goes "
                           "as the *square* of the current, so a 17% change in the rail is a 31% change "
                           "in the energy. And 312.5 µJ is a small number by any domestic standard, "
                           "about the work of lifting a one-gram paperclip three centimetres; but it has to go "
                           "somewhere when the circuit is switched off, and if the only path available "
                           "is an opening contact, it goes there as a spark.",
                },
            ],
            "quiz": {
                "title": "Magnetism and induction, checked",
                "minutes": 9,
                "questions": [
                    {
                        "q": "You measure the magnetic field 2 cm from a long straight wire, then move out to 6 cm. The field is now:",
                        "opts": ["A third as strong", "A ninth as strong", "A sixth as strong", "Unchanged"],
                        "a": 0,
                        "why": (
                            "Ampere's law gives $B = \\mu_0 I / (2\\pi r)$ for a long straight wire: a single power "
                            "of $r$, so tripling the distance divides the field by three. The instinct to answer "
                            "'a ninth' comes from Coulomb's law, but the geometry is different — a wire is a line "
                            "of sources, not a point, and its field falls off more slowly."
                        ),
                    },
                    {
                        "q": "What is the net magnetic flux out of a closed surface drawn around one end of a bar magnet?",
                        "opts": [
                            "Positive, since the north pole is inside",
                            "Zero",
                            "It depends on the shape of the surface",
                            "Equal to the pole strength divided by $\\mu_0$",
                        ],
                        "a": 1,
                        "why": (
                            "Magnetic field lines have no ends: every line that leaves the surface comes back in "
                            "somewhere else, because there is no magnetic charge for a line to start on. So the "
                            "net flux out of *any* closed surface is exactly zero — the magnetic counterpart of "
                            "Gauss's law, with a zero on the right-hand side. Cutting a magnet in half gives two "
                            "magnets, never an isolated pole."
                        ),
                    },
                    {
                        "q": "A coil of wire sits motionless in a strong, perfectly steady magnetic field. What voltage appears across its ends?",
                        "opts": [
                            "A large one, because the flux through it is large",
                            "None",
                            "One proportional to the field strength",
                            "One proportional to the coil's area",
                        ],
                        "a": 1,
                        "why": (
                            "Faraday's law is about the *rate of change* of flux, $\\mathcal{E} = -\\mathrm{d}\\Phi/"
                            "\\mathrm{d}t$. A steady flux, however large, has zero rate of change and induces "
                            "nothing. This is why transformers only work on alternating current, and why you have "
                            "to move a magnet past a coil rather than just holding it there."
                        ),
                    },
                    {
                        "q": "You push the north pole of a magnet towards a coil. Which way does the induced current flow?",
                        "opts": [
                            "The way that makes the coil's near face a north pole, pushing back",
                            "The way that makes the coil's near face a south pole, pulling the magnet in",
                            "It alternates as the magnet moves",
                            "No current flows until the magnet touches the coil",
                        ],
                        "a": 0,
                        "why": (
                            "Lenz's law: the induced current opposes the change that produced it, so the coil "
                            "presents a north face and repels the approaching magnet. It has to. If it attracted "
                            "the magnet instead, the magnet would accelerate in, inducing more current, "
                            "accelerating further — free energy from nothing. The minus sign in Faraday's law is "
                            "energy conservation written into the equation."
                        ),
                    },
                    {
                        "q": "You wind a solenoid with twice as many turns, keeping its length and cross-section the same. Its inductance:",
                        "opts": ["Doubles", "Quadruples", "Halves", "Is unchanged"],
                        "a": 1,
                        "why": (
                            "$L = \\mu_0 N^2 A / \\ell$ — the turn count is *squared*, so twice the turns is four "
                            "times the inductance. The reason it appears twice is worth holding on to: doubling "
                            "the turns doubles the field the coil makes for a given current, and then doubles "
                            "again the number of turns that link that field."
                        ),
                    },
                    {
                        "q": "A 10 mH inductor is switched onto a supply through a 100 Ω resistor. How long until the current has reached 63% of its final value?",
                        "opts": ["1 ms", "100 µs", "10 µs", "1 s"],
                        "a": 1,
                        "why": (
                            "For an inductor the time constant is $\\tau = L/R = 0.01/100 = 100$ µs. Note that the "
                            "resistance is in the *denominator*, the opposite of the capacitor case where "
                            "$\\tau = RC$: a bigger resistor makes an RL circuit faster and an RC circuit slower. "
                            "The 1 s option is the slip to watch for: it is $L$ multiplied by $R$, the "
                            "capacitor's rule applied to an inductor. The 1 ms option is the RC time "
                            "constant from module 3, which belongs to a different circuit entirely."
                        ),
                    },
                ],
            },
            "build": {
                "title": "An inductor that takes 159 microseconds",
                "minutes": 25,
                "brief": r'''
Draw the inductive twin of the RC you built in module 3: a **5 V source**, an
inductor in series, and a resistor from the inductor's far end down to ground, with
the probe on the junction between them.

At DC an inductor is simply a piece of wire, so the settled output is the full supply.
Immediately after switch-on it is the opposite — the inductor resists any sudden
change in its current, so the output starts at zero and climbs. The time constant is

$$\tau = \frac{L}{R}$$

and the specification is $\tau = 159$ µs, which puts the filter's corner at 1 kHz.

The canvas opens with the source wired straight to the resistor. Insert an inductor
into that path and choose the pair of values. As before, only the ratio is fixed:
10 mH with 62.8 Ω works, and so does 1 mH with 6.28 Ω.

Type inductances as `10m` for 10 millihenries.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 62.8},
                        {"id": "p2", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p3", "kind": "GND", "x": 9, "y": 9, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "OUT", "x": 11, "y": 4, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [9, 4], "b": [11, 4]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.01},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 62.8},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 4, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [9, 4], "b": [11, 4]},
                    ],
                },
                "checks": [
                    {"name": "at DC the inductor is just wire, so the output is the full 5 V", "code": r'''
c.close(c.vout(), 5.0, 0.02, "the settled voltage at the probe");
'''},
                    {"name": "the current takes 159 microseconds to reach 63%", "code": r'''
var s = c.step(0.001);
var last = s.v[s.v.length - 1];
c.assert(last > 4.5, "after 1 ms the output has only reached " + c.fmt(last, "V") +
  " — the L/R time constant is far longer than 159 us");
var t63 = null;
for (var i = 1; i < s.t.length; i++) {
  if (s.v[i] >= 0.632 * 5.0) { t63 = s.t[i]; break; }
}
c.assert(t63 !== null, "the output never reaches 3.16 V within 1 ms");
c.close(t63, 1.5915e-4, 0.10, "the time to reach 63% of 5 V");
'''},
                    {"name": "the corner sits at 1 kHz", "code": r'''
var fc = c.corner(10, 1e6);
c.close(fc, 1000.0, 0.06, "the -3 dB frequency (which is R/(2*pi*L))");
'''},
                    {"name": "one decade past the corner the output is down tenfold", "code": r'''
var low = c.gain(10);
var dec = c.gain(10000);
c.assert(low > 4.5, "at 10 Hz the output should still follow the source, but it reads " +
  c.fmt(low, "V"));
c.close(dec / low, 0.0995, 0.15, "the gain a decade above the corner, relative to DC");
'''},
                ],
                "hints": [
                    "The source is currently wired straight across to the resistor. Delete the long wire, drop the inductor into the gap, and rejoin both ends.",
                    "Choose the resistor first: with $\\tau = L/R$, a 10 mH coil needs $R = L/\\tau = 0.01/159\\,\\mu\\text{s} \\approx 62.8\\ \\Omega$.",
                    "If the DC check fails with an under-determined message, the probe node is floating — the resistor must reach ground.",
                    "A time constant ten times too *short* usually means the inductor was typed as `1m` rather than `10m`.",
                ],
            },
            "lab": {
                "title": "A coil, from its dimensions to its time constant",
                "runtime": "python",
                "minutes": 24,
                "brief": r'''
The same closing of the loop as module 3, on the magnetic side: from the shape of a
coil to the number you typed into the schematic.

`solenoid_inductance(turns, length, area, mu_r)` returns $\mu_0 \mu_r N^2 A / \ell$ in
henries. `MU0` is defined for you.

`emf_from_flux_change(flux_start, flux_end, dt)` returns the average induced voltage
over the interval, $-\Delta\Phi/\Delta t$. Keep the minus sign: it is Lenz's law, and
a rising flux must give a negative emf.

`rl_time_constant(inductance, resistance)` returns $L/R$ in seconds — the number the
circuit editor measured for you as 159 µs.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

MU0 = 1.25663706212e-6   # permeability of free space, in H/m


def solenoid_inductance(turns, length, area, mu_r=1.0):
    """Inductance in henries of a solenoid: mu0 * mu_r * N^2 * A / length."""
    # TODO: mind the square on the turn count.
    return 0.0


def emf_from_flux_change(flux_start, flux_end, dt):
    """Average induced emf in volts over `dt` seconds, from Faraday's law."""
    # TODO: minus the rate of change of flux.
    return 0.0


def rl_time_constant(inductance, resistance):
    """Time constant in seconds of an inductor discharging through a resistor."""
    # TODO: L over R, not L times R.
    return 0.0


if __name__ == "__main__":
    L = solenoid_inductance(500, 0.2, 1e-4)
    print("500 turns, 20 cm long, 1 cm^2 cross-section:", L, "H")
    print("with 62.8 ohm in series, tau =", rl_time_constant(L, 62.8), "s")
    print("flux rising 0 -> 2 mWb in 10 ms gives",
          emf_from_flux_change(0.0, 2e-3, 0.01), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

MU0 = 1.25663706212e-6   # permeability of free space, in H/m


def solenoid_inductance(turns, length, area, mu_r=1.0):
    """Inductance in henries of a solenoid: mu0 * mu_r * N^2 * A / length."""
    return float(MU0 * mu_r * turns * turns * area / length)


def emf_from_flux_change(flux_start, flux_end, dt):
    """Average induced emf in volts over `dt` seconds, from Faraday's law."""
    return float(-(flux_end - flux_start) / dt)


def rl_time_constant(inductance, resistance):
    """Time constant in seconds of an inductor discharging through a resistor."""
    return float(inductance / resistance)


if __name__ == "__main__":
    L = solenoid_inductance(500, 0.2, 1e-4)
    print("500 turns, 20 cm long, 1 cm^2 cross-section:", L, "H")
    print("with 62.8 ohm in series, tau =", rl_time_constant(L, 62.8), "s")
    print("flux rising 0 -> 2 mWb in 10 ms gives",
          emf_from_flux_change(0.0, 2e-3, 0.01), "V")
'''}],
                "hints": [
                    "`turns * turns` (or `turns ** 2`) — the squared turn count is the whole character of the formula.",
                    "The emf is *minus* the change in flux over the time taken, so a flux that grows gives a negative answer.",
                    "The RL time constant divides: a bigger resistor makes the circuit settle faster, which is the opposite of the RC case.",
                ],
                "tests": [
                    {"name": "a 500-turn solenoid", "code": r'''
_L = solenoid_inductance(500, 0.2, 1e-4)
assert abs(_L - 0.000157079632765) < 1e-15, \
    f"expected MU0*500^2*1e-4/0.2 = 157.08 uH, got {_L!r}"
'''},
                    {"name": "inductance goes as the square of the turns", "code": r'''
_one = solenoid_inductance(200, 0.1, 5e-4)
_two = solenoid_inductance(400, 0.1, 5e-4)
assert abs(_two / _one - 4.0) < 1e-9, \
    f"doubling the turns should quadruple the inductance, got a ratio of {_two / _one}"
'''},
                    {"name": "a longer coil of the same turns is weaker", "code": r'''
_short = solenoid_inductance(300, 0.05, 2e-4)
_long = solenoid_inductance(300, 0.10, 2e-4)
assert abs(_short / _long - 2.0) < 1e-9, "the length is in the denominator"
_core = solenoid_inductance(300, 0.05, 2e-4, 200.0)
assert abs(_core - 200.0 * _short) < 1e-12, "an iron core of mu_r = 200 multiplies L by 200"
'''},
                    {"name": "a rising flux induces a negative emf", "code": r'''
_e = emf_from_flux_change(0.0, 2e-3, 0.01)
assert _e < 0, "Lenz's law: the induced emf opposes the rise, so it comes out negative"
assert abs(_e + 0.2) < 1e-12, f"expected -0.2 V, got {_e!r}"
_back = emf_from_flux_change(2e-3, 0.0, 0.01)
assert abs(_back - 0.2) < 1e-12, f"reversing the change reverses the emf, got {_back!r}"
'''},
                    {"name": "a steady flux induces nothing, a changing one does", "code": r'''
_e = emf_from_flux_change(5e-3, 5e-3, 0.01)
assert abs(_e) < 1e-15, \
    f"Faraday's law responds to change, not to the size of the flux, got {_e!r}"
_drop = emf_from_flux_change(5e-3, 4e-3, 0.01)
assert abs(_drop - 0.1) < 1e-12, \
    f"the same 5 mWb falling by 1 mWb over 10 ms gives +0.1 V, got {_drop!r}"
'''},
                    {"name": "the time constant matches the circuit you drew", "code": r'''
_tau = rl_time_constant(0.01, 62.8)
assert abs(_tau - 0.00015923566878980894) < 1e-15, \
    f"10 mH with 62.8 ohm is 159 us, exactly as the editor measured, got {_tau!r}"
assert abs(rl_time_constant(0.01, 125.6) - _tau / 2.0) < 1e-15, \
    "doubling the resistance halves the RL time constant"
'''},
                ],
            },
        },
        # ---- M5 -----------------------------------------------------------
        {
            "title": "Conductors, screening and the coaxial pair",
            "summary": "A metal holds charges that are free to move, so it cannot keep a field inside itself — and everything else about conductors is a consequence of that one sentence.",
            "concepts": [
                "In a conductor at rest the field inside is zero. Any field would push the free charges, and they keep moving until the field they themselves make cancels it. In copper that rearrangement takes about $10^{-19}$ s, so \u2018at rest\u2019 means anything slower than that.",
                "Zero field inside forces two things by Gauss's law: no net charge anywhere in the bulk, so every excess charge sits on the surface; and no potential difference between any two points of the metal, so the whole conductor is one equipotential. Field lines therefore meet its surface at right angles \u2014 a sideways component would push surface charge along, and it would move.",
                "Just outside the surface the field is $E = \\sigma/\\varepsilon_0$, where $\\sigma$ is the local surface charge density. That is twice what an isolated sheet of the same $\\sigma$ would give, because on a conductor all the flux leaves from one face. Where the surface curves tightly, $\\sigma$ has to be large to hold the same potential, which is why charge crowds onto points and why lightning conductors are sharp.",
                "A closed conducting shell with nothing inside it has no field in the cavity, whatever charges sit outside and whether or not the shell is earthed. That is the screen round every instrument cable. Earthing does a different job: it holds the shell's own potential still, and it stops charge *inside* the cavity from producing a field outside.",
                "Coaxial geometry is the case worth having by heart. Gauss's law on a cylinder gives $E = \\lambda/(2\\pi\\varepsilon_0 r)$ between the conductors and zero outside the screen, and the capacitance per metre is $2\\pi\\varepsilon_0\\varepsilon_r/\\ln(b/a)$ \u2014 about 100 pF for every metre of ordinary cable. Screening is not free: you pay for it in capacitance.",
            ],
            "read": [
                {
                    "title": "Why a metal cannot hold a field, and what follows from that",
                    "minutes": 20,
                    "body": r'''
A cubic centimetre of copper holds about $8.5\times10^{22}$ atoms, and each of them
hands one of its outer electrons over to the metal as a whole. Those electrons stop
belonging to any particular atom. They move through the fixed lattice of positive ions
at something like $1.6\times10^6$ m/s, in every direction at once, and on average they
get nowhere — but they are free to go somewhere if anything asks them to.

That is the entire difference between a conductor and the dielectrics of module 3. A
dielectric's charges are bound: pull on them and they shift by a fraction of an atomic
diameter and stop, which is polarisation, and it weakens a field without abolishing it.
A conductor's charges are not bound at all. Push on them and they keep going until the
push stops.

Everything in this module is that sentence worked out patiently.

## The slab in a field

Take a rectangular block of copper and switch on a uniform field pointing left to right
across it. At the first instant the field inside the metal is whatever you applied. The
free electrons feel a force $-eE$, so they drift to the left; they pile up on the left
face and leave behind, on the right face, a layer of positive ions whose electrons have
gone.

Those two sheets of charge make a field of their own, pointing from the positive face to
the negative one — that is, from right to left. Inside the metal it opposes the field you
applied. So the total field in the metal is smaller than it was, which means the force
on the remaining electrons is smaller, which means they drift more slowly, which means
the sheets grow more slowly.

The process only stops when the sheets have grown to exactly the size that cancels the
applied field. Not approximately: exactly. Anything left over is a force on a charge that
is free to move, and it moves.

$$E_{\text{inside a conductor at rest}} = 0$$

The italic words are the whole of the physics. *Inside* — the field outside is not zero
and never was. *At rest* — nothing is moving any more, which needs a moment's attention,
because you are about to find out how short that moment is.

## How long the rearrangement takes

Suppose you could somehow deposit an excess charge $q$ deep inside the metal — a small
ball of it, radius $a$, far from any surface. It will not stay. Gauss's law on a sphere
of radius $a$ gives the field it makes at its own edge:

$$E = \frac{q}{4\pi\varepsilon_0 a^2}$$

That field is sitting inside a conductor, and a conductor answers a field with a current.
The local form of Ohm's law says a field $E$ drives a current density $J = E/\rho$, where
$\rho$ is the resistivity — module 6 builds that relation properly, and here we only need
it to exist. Charge therefore streams outward through the surface of our little ball at
a rate

$$\frac{\mathrm{d}q}{\mathrm{d}t} = -J \cdot 4\pi a^2 = -\frac{E}{\rho}\,4\pi a^2
= -\frac{1}{\rho}\cdot\frac{q}{4\pi\varepsilon_0 a^2}\cdot 4\pi a^2
= -\frac{q}{\varepsilon_0 \rho}$$

The radius cancels, which is the sign that the answer belongs to the material and not to
the ball you imagined. What is left is the equation of an exponential decay, $q(t) =
q_0 e^{-t/\tau}$, with

$$\tau = \varepsilon_0 \rho$$

```text
copper:   rho = 1.68e-8 ohm m,   eps0 = 8.854e-12 F/m

tau = 8.854e-12 * 1.68e-8      = 1.49e-19 s
```

Call it $10^{-19}$ s. Compare it with the fastest thing anywhere in this catalog — a
gigahertz clock edge, a nanosecond — and the conductor has finished ten orders of
magnitude before it was asked. When this course says
*electrostatics*, it is not asking you to hold still. It is telling you that for any
process a laboratory can arrange, the metal has already finished rearranging itself.

(The figure is honest about the answer and slightly dishonest about the route: $10^{-19}$ s
is shorter than the average time between one electron collision and the next, so the
Ohm's-law step is being used outside the range where it is exact. Do the calculation with
a model that survives that regime and you get a few times $10^{-16}$ s instead. It changes
nothing that matters.)

## Three things that follow immediately

**No charge anywhere in the bulk.** Draw any closed surface you like entirely inside the
metal. The field is zero at every point of it, so the flux through it is zero, so by
Gauss's law it encloses no net charge. That is true of *every* surface you can draw in
the bulk, however small, so there is no excess charge anywhere in there. Whatever charge
the object carries has been driven to the surface.

**The whole conductor is one equipotential.** Potential difference is the field integrated
along a path: $V_B - V_A = -\int_A^B \vec E\cdot\mathrm{d}\vec\ell$. Take a path from any
point of the metal to any other, staying inside. Every contribution to the integral is
zero. So every point of a conductor is at the same potential, including its surface, and
including the far end of a wire soldered to it. This is the licence you have been using
since EE101 without proof when you said "that node is at 5 V".

**Field lines meet the surface at right angles.** Suppose a field line arrived at the
surface at some other angle. Then it would have a component lying *along* the surface,
and that component would be a force on the surface charge — which is free to move, and
would. It moves until the sideways component is gone. What is left points straight out
(or straight in).

## The pillbox, and the factor of two

How strong is the field just outside? Put a tiny cylindrical box across the surface — the
standard Gaussian pillbox — with one flat face just inside the metal, one just outside,
and negligible height.

```text
       outside      ^ E                 flux out of the top face = E * A
    ---------------[ ]--------------    flux out of the sides     = 0  (E is
       surface, charge density sigma        parallel to them)
    ---------------[ ]--------------    flux out of the bottom    = 0  (E = 0
       inside the metal, E = 0                                     in the metal)

    enclosed charge = sigma * A

    Gauss:   E * A = sigma * A / eps0     ->     E = sigma / eps0
```

Nothing in that used the shape of the object. It is true at every point of every
conductor, with $\sigma$ the *local* surface charge density at that point.

The result people trip over is that an isolated sheet of charge with the same $\sigma$
gives only $\sigma/2\varepsilon_0$ on each side. The two answers differ by exactly two,
and the reason is the bottom face of the pillbox: an isolated sheet lets flux escape from
both faces and each gets half, while a conductor's surface charge has a field-free region
on one side and has to send everything out of the other.

## Worked: two spheres on a wire

A sphere of radius 2.0 cm and a sphere of radius 6.0 cm sit far apart, joined by a long
thin wire. Put 24 nC on the pair. Where does it go, and which surface has the stronger
field?

The wire makes the two spheres one conductor, so they are at one potential. Far apart
means each one's field is its own, so $V = kQ/R$ for each:

```text
k = 1 / (4 pi eps0) = 8.988e9 N m^2 / C^2

equal potentials:      k Q1 / R1  =  k Q2 / R2      ->   Q1 / Q2 = R1 / R2 = 1/3
total charge:          Q1 + Q2 = 24 nC

                       Q1 = 6.0 nC        Q2 = 18.0 nC

check the potential:   V = 8.988e9 * 6.0e-9 / 0.020   = 2696 V
                       V = 8.988e9 * 18.0e-9 / 0.060  = 2696 V     (same, as required)
```

Now the surface densities. Three times the charge, spread over nine times the area:

```text
sigma1 = Q1 / (4 pi R1^2) = 6.0e-9  / (4 pi * 4.0e-4) = 1.194e-6 C/m^2
sigma2 = Q2 / (4 pi R2^2) = 18.0e-9 / (4 pi * 3.6e-3) = 0.398e-6 C/m^2

E1 = sigma1 / eps0 = 1.194e-6 / 8.854e-12 = 1.348e5 V/m  = 135 kV/m
E2 = sigma2 / eps0 = 0.398e-6 / 8.854e-12 = 0.449e5 V/m  =  45 kV/m
```

Cross-check the first one the other way, as the field of a point charge evaluated at the
surface: $kQ_1/R_1^2 = 8.988\times10^9 \times 6.0\times10^{-9} / 4.0\times10^{-4} =
1.348\times10^5$ V/m. It agrees, and it must — for a sphere, $E = \sigma/\varepsilon_0$
and $E = kQ/R^2$ are the same statement wearing different clothes.

The small sphere carries a *third* of the charge and has *three times* the field. In
general, on one conductor at one potential, $\sigma \propto 1/R$: the tighter the
curvature, the more charge has to crowd in to hold the same potential, and the harder the
field just outside. Take that to its limit and you have a needle point, where the local
radius is a fraction of a millimetre and the field is enormous — which is why a lightning
conductor is sharpened, why high-voltage hardware is built out of fat smooth toroids with
no exposed corners, and why the 2 cm sphere in this example is the one that will spark
first. Air breaks down at about 3 MV/m, so:

```text
V at which the small sphere reaches 3 MV/m:   V = E * R = 3e6 * 0.020 = 60 kV
V at which the large one would:               V = 3e6 * 0.060 = 180 kV
```

Wire them together and the assembly is limited by the small sphere, at 60 kV. A chain is
as strong as its sharpest link.

## The cavity: why a box screens

Hollow the conductor out. Leave an empty cavity of any shape inside it, put whatever
charges you like *outside*, and ask what the field in the cavity is.

It is zero, and the argument is short. The metal is all at one potential, so the entire
wall of the cavity is at one potential. Now suppose there were a field line somewhere in
the cavity. A field line runs downhill in potential and it has to start and end
somewhere; with no charge in the cavity it cannot start or end in mid-air, so it must run
from one point of the wall to another. But those two points are at the same potential,
and a field line that runs from a place to another place at the same potential has
descended nothing — a contradiction. There are no field lines. There is no field.

This is the Faraday cage, and it is what the braid around an instrument cable is doing.
Note what the argument did *not* use: the shape of the cavity, the strength of the
outside field, and whether the shell is earthed. A sealed biscuit tin standing on a
wooden bench screens its contents from a charged rod exactly as well as a bolted-down
earthed enclosure does.

## Worked: a charge inside the cavity

Turn it round. A neutral spherical shell has inner radius 3.0 cm and outer radius 4.0 cm.
Suspend a $+2.5$ nC point charge at the centre of the cavity. Now what?

Take a closed surface inside the metal, surrounding the cavity. $E = 0$ on it, so it
encloses no net charge. It encloses the $+2.5$ nC and the inner wall, so the inner wall
must carry $-2.5$ nC. The shell was neutral to begin with and no charge has left it, so
the missing $+2.5$ nC is on the outer surface.

```text
inner wall:  sigma_in  = -2.5e-9 / (4 pi * 0.030^2) = -221 nC/m^2
outer wall:  sigma_out = +2.5e-9 / (4 pi * 0.040^2) = +124 nC/m^2

field in the cavity, at r = 2.0 cm:
    E = k q / r^2 = 8.988e9 * 2.5e-9 / 4.0e-4    = 5.62e4 V/m
field inside the metal, at r = 3.5 cm:            = 0
field outside, at r = 10 cm:
    E = 8.988e9 * 2.5e-9 / 1.0e-2                = 2.25e3 V/m
```

From outside, the assembly looks exactly like a bare $+2.5$ nC charge — the shell has
hidden nothing. Move the point charge off-centre in its cavity and the inner wall's
$\sigma$ redistributes, the cavity field changes shape, and the *outside* field does not
change at all: the outer surface has no way of knowing where in the cavity the charge is,
because the metal between them is field-free.

Now earth the shell. Charge flows in from the ground until the shell is at the potential
of the ground, and what leaves is precisely the $+2.5$ nC on the outer surface: the field
outside collapses to zero. The $-2.5$ nC on the inner wall stays exactly where it is,
because the point charge in the cavity is still demanding it. This is what earthing a
screen buys you — not protection of the inside from the outside, which you had already,
but protection of the outside from the inside.

## The mistakes people make

**"The cage works because it is earthed."** It does not, as the biscuit tin shows. The
belief is very hard to shake because every screened enclosure you will ever meet does
have an earth wire on it, and it is there for the two real reasons above: to stop the
enclosure floating to some arbitrary potential and coupling capacitively into what it
surrounds, and to give the inner charges' image somewhere to go. Screening against an
external electrostatic field is not one of them.

**"The field inside a conductor is always zero."** It is zero *in electrostatics*. Push a
current through a wire and there is certainly a field inside it — that field is what
drives the current. It is small, but it is the whole subject of module 6:

```text
10 A through 1 mm^2 of copper:  J = 10 / 1e-6      = 1.0e7 A/m^2
                                E = rho J = 1.68e-8 * 1.0e7
                                          = 0.168 V/m
```

which is 0.168 V along a metre of wire, and if you have ever measured the drop along a
long extension lead you have measured it.

**"A metal box screens everything."** It screens electric fields. A steady or slowly
varying *magnetic* field walks straight through a copper box as though it were not there
— there are no magnetic charges for the free electrons to arrange themselves into, so the
cancellation mechanism of this whole reading unit has nothing to work with. Screening a
magnetic field needs a high-permeability material to divert it, which is module 8.

## Where this stops

**Holes.** The cavity argument assumes a *closed* shell. A real screen has seams, a
connector at each end, and — if it is braided — thousands of small gaps. Field leaks
through an opening over a distance comparable to the opening's own size, so a joint a
millimetre wide is unimportant to a slow field and a serious matter at a wavelength of a
few millimetres. Microwave oven doors are perforated with holes a couple of millimetres
across, which is transparent to light and opaque at 12 cm.

**Speed.** $\tau = \varepsilon_0\rho$ was computed for charge relaxing inside the bulk. A
changing field arriving from outside is a different question, and the answer is the skin
depth $\delta = \sqrt{\rho/(\pi f \mu_0)}$: 9.2 mm in copper at 50 Hz, 65 µm at 1 MHz. A
25 µm foil screen is thinner than a skin depth at mains frequency, which is exactly why
foil-screened cable is poor at rejecting mains hum and good above a megahertz.

**Frequency, eventually.** The free-electron sea can only follow a field it has time to
follow. Above the plasma frequency — around $2.5\times10^{15}$ Hz for copper, in the
ultraviolet — the electrons can no longer keep up, the metal stops behaving as a
conductor, and it becomes transparent. Your copper box screens radio perfectly, visible
light perfectly, and X-rays not at all.

**Perfection.** Everything here treats the conductor as having some resistivity but no
other limits. A superconductor expels a magnetic field as well as an electric one, which
is a genuinely different phenomenon and not a limiting case of anything in this unit.
''',
                },
                {
                    "title": "The coaxial pair: a screen, and the price of it",
                    "minutes": 19,
                    "body": r'''
A single wire running across a laboratory is an antenna. It has capacitance to every
charged object in the room — a mains cable a metre away, a person walking past, a
fluorescent tube — and every one of those couples a current into it. Feed the wire from a
sensor with a source resistance of some tens of kilohms and the interference is not a
small correction. It is often larger than the signal.

The fix is the previous reading unit's cavity theorem, wrapped into a cable. Put the
signal wire inside a conducting tube. The tube is a closed conducting shell, so nothing
outside it produces a field inside it, so the wire hears nothing. Then connect the tube to
the circuit's reference node at one end so that it has a defined potential and so that the
signal's return current has somewhere to run.

That is coaxial cable: an inner conductor of radius $a$, a dielectric filling out to
radius $b$, a braided or foil screen at $b$, and a plastic jacket that is electrically
nothing. It is the most-used geometry in electronics and it is worth being able to
reconstruct from scratch.

## The field between the conductors

Put a charge $+\lambda$ on every metre of the inner conductor and $-\lambda$ on every
metre of the screen. Symmetry does the same work it did for Gauss's law in module 2: the
cable looks the same from every direction round its axis and the same at every point along
it, so the field can only point radially outward and can only depend on $r$.

Take a Gaussian cylinder of radius $r$ and length $L$, coaxial with the cable, with
$a < r < b$.

```text
flux out of the curved wall  = E(r) * 2 pi r L
flux out of the two flat ends = 0        (E is parallel to them)
charge enclosed               = lambda * L

Gauss:   E(r) * 2 pi r L = lambda L / eps0
```

$$E(r) = \frac{\lambda}{2\pi\varepsilon_0 r}, \qquad a < r < b$$

The length cancels, as it should. Note the power on $r$: **one**, not two. A cylinder's
area grows in proportion to $r$, so what spreads over a cylinder falls off as $1/r$; only
what spreads over a sphere falls off as $1/r^2$.

Now do the same sum for $r > b$, outside the screen. The cylinder now encloses the inner
conductor's $+\lambda L$ *and* the screen's $-\lambda L$, which add to nothing, so

$$E(r) = 0 \qquad \text{for } r > b$$

There is the screening, and it works in both directions: nothing outside gets in, and
nothing inside gets out. A coaxial cable carrying a kilovolt has no field on its jacket at
all.

For $r < a$ the enclosed charge is zero as well, because all of the inner conductor's
charge is on its own surface — which is the first reading unit's result, used without
comment.

## From the field to the capacitance

Capacitance is charge over voltage, so we need the voltage between the two conductors:
walk from the screen in to the inner wire, integrating the field.

$$V = \int_a^b E(r)\,\mathrm{d}r = \frac{\lambda}{2\pi\varepsilon_0}\int_a^b
\frac{\mathrm{d}r}{r} = \frac{\lambda}{2\pi\varepsilon_0}\ln\frac{b}{a}$$

The charge on a length $L$ is $\lambda L$, so the capacitance of that length is $\lambda
L / V$, and the capacitance **per metre** is

$$C' = \frac{\lambda}{V} = \frac{2\pi\varepsilon_0}{\ln(b/a)}$$

Fill the space with a dielectric — every real cable does, because the inner conductor has
to be held in the middle of the screen somehow — and module 3's rule applies: the
capacitance is multiplied by the relative permittivity $\varepsilon_r$ of whatever is in
there.

$$C' = \frac{2\pi\varepsilon_0\varepsilon_r}{\ln(b/a)}$$

Only the *ratio* $b/a$ appears, so a cable scaled up by a factor of ten in every dimension
has exactly the same capacitance per metre. That is worth a moment: capacitance normally
scales with size, and here it does not, because a coaxial pair grows its plate area and
its plate separation together.

## Worked: what a metre of RG-58 is worth

RG-58 is the thin black 50 Ω cable on every bench. Its inner conductor is 0.9 mm across,
its polyethylene dielectric is 2.95 mm across, and polyethylene has $\varepsilon_r = 2.25$.

```text
a = 0.45 mm      b = 1.475 mm       eps_r = 2.25

b / a = 1.475 / 0.45           = 3.278
ln(b/a)                        = 1.187

2 pi eps0 = 6.2832 * 8.854e-12 = 5.563e-11 F/m
numerator = 5.563e-11 * 2.25   = 1.252e-10
C' = 1.252e-10 / 1.187         = 1.054e-10 F/m   = 105 pF per metre
```

The datasheet says 101 pF/m, and the 4% is the braid not being a perfect cylinder. So the
rule of thumb in the concept list — about 100 pF for every metre — is not a coincidence of
this one cable; it is what the logarithm gives for any ratio near three with a plastic
dielectric, and almost every cable made is near three, because that is the ratio that gives
50 Ω.

Hold that number against the isolated sphere in this module's derivation, whose capacitance
is $4\pi\varepsilon_0 R$: a metal sphere the size of a grapefruit, radius 5 cm, comes to
5.6 pF — which at a hundred picofarads per metre is five and a half **centimetres** of
cable. A cable is an extremely efficient capacitor, and if you did not want a capacitor,
that is bad news.

## The logarithm is very slow, and that is the trap

Suppose you decide the cable's 100 pF/m is ruining your bandwidth and you will design it
away by making the screen bigger. The capacitance goes as $1/\ln(b/a)$, and a logarithm
barely moves:

```text
b/a =  3    ->  ln = 1.10     C' = 100 pF/m   (reference)
b/a =  6    ->  ln = 1.79     C' =  61 pF/m
b/a =  9    ->  ln = 2.20     C' =  50 pF/m
b/a = 20    ->  ln = 3.00     C' =  37 pF/m
b/a = 55    ->  ln = 4.01     C' =  27 pF/m
```

To halve the capacitance you must *square* the ratio. Going from a 3 mm cable to a 9 mm
one — three times the diameter, nine times the volume, a cable that no longer bends — buys
you a factor of two. This is the sentence at the end of the concept list made quantitative:
screening is not free, the price is capacitance, and you cannot buy your way out of it with
geometry. The only real levers are a lower-permittivity dielectric (foamed polyethylene
gets $\varepsilon_r$ down to about 1.5, worth a third) and using less cable.

## Where the field is strongest

The field between the conductors is $\lambda/2\pi\varepsilon_0 r$, which is largest at the
smallest $r$ — that is, at the surface of the inner conductor, $r = a$. Rewrite it in terms
of the applied voltage rather than the charge, by substituting $\lambda = 2\pi\varepsilon_0
V/\ln(b/a)$:

$$E_{\max} = E(a) = \frac{V}{a\,\ln(b/a)}$$

so the cable breaks down when the field at the *inner* conductor reaches the dielectric's
strength, however comfortable things are out near the screen.

Worked, for the RG-58 above with 1 kV between conductors:

```text
E_max = V / (a ln(b/a)) = 1000 / (0.45e-3 * 1.187)
      = 1000 / 5.342e-4                       = 1.87e6 V/m   = 1.87 MV/m
```

Polyethylene stands about 20 MV/m, so there is a factor of ten in hand, and RG-58 is in
fact rated at around 1.9 kV. Note where the danger is: at the screen the field is
$1.87\times10^6 \times (0.45/1.475) = 0.57$ MV/m, three times weaker. All the stress is on
the thin wire in the middle, and a nick or a whisker on that wire — a place where the local
radius of curvature is tiny — is where a cable fails.

## The ratio that gives the best cable

That formula pays a dividend. Suppose the outer radius $b$ is fixed by how fat a cable you
are willing to carry, and you may choose the inner radius $a$ freely. Which $a$ lets the
cable stand the most voltage — that is, which one *minimises* $E_{\max}$ for a given $V$?

Minimising $V/(a\ln(b/a))$ means maximising $f(a) = a\ln(b/a)$. Differentiate:

$$f'(a) = \ln\frac{b}{a} + a\cdot\left(-\frac{1}{a}\right) = \ln\frac{b}{a} - 1$$

Set it to zero and $\ln(b/a) = 1$, so

$$\frac{b}{a} = e = 2.718$$

A thicker inner conductor concentrates less field on itself but leaves less room for the
voltage to be dropped across; a thinner one has the opposite problem; and $e$ is where the
two effects balance. Power cables sit close to that ratio. Signal cables sit a little above
it, near 3.3, because they are optimised for a 50 Ω characteristic impedance rather than for
breakdown — which is a hint that the lumped capacitance of this unit is not the last word.

## Worked: what the cable does to a signal

A pressure sensor with a 10 kΩ output resistance sits at the end of 30 m of ordinary cable.

```text
C = 30 m * 100 pF/m                    = 3.0 nF

corner of the R-C low-pass it forms:
f_c = 1 / (2 pi R C) = 1 / (2 pi * 1.0e4 * 3.0e-9)
    = 1 / 1.885e-4                     = 5.3 kHz
```

Below 5.3 kHz the cable is invisible; above it, the signal is being thrown away at 20 dB
per decade. Whether that is a disaster or a gift depends on what you were sending — and
this module's tuning exercise is exactly that argument, with the interference you are
trying to reject on one side and the signal you are trying to keep on the other.

## The mistakes people make

**Radius and diameter.** $b/a$ is the same number whether you use radii or diameters, so
the capacitance formula forgives you and everyone gets lazy. Then they meet $E_{\max} =
V/(a\ln(b/a))$, put a diameter in for $a$, and get a field exactly half the true one — a
comfortable-looking factor of two on the safe-looking side. Fix the habit at the
capacitance, where it costs nothing, so that it is there when it matters.

**Expecting the capacitance to scale with the ratio.** People predict that doubling $b/a$
halves the capacitance. It does not; it multiplies it by $\ln(3)/\ln(6) = 0.61$. The
logarithm is the whole character of the coaxial geometry.

**Earthing the screen at both ends.** It sounds twice as good. It creates a loop of
conductor enclosing some area, threaded by whatever magnetic field is in the building, and
Faraday's law from module 4 then drives a current round it. The screen carries that current
and its resistance turns it back into a voltage in series with your signal — the classic
mains hum that appears the moment a second earth connection is made. Screens are earthed at
one end, at the amplifier.

**Believing the screen screens magnetism.** It does not, at low frequency, for the reason
given at the end of the last unit. What actually protects a coaxial cable against magnetic
pickup is that the signal current and its return current run through the same axis, so the
loop area between them is essentially zero and there is nothing for a changing flux to link.
That is a different mechanism from the electrostatic screening, and it is why a coaxial
cable beats a screened twisted pair at radio frequencies and roughly ties with it at 50 Hz.

## Where this stops

**Length, compared with a wavelength.** Treating the cable as a single lumped capacitor is
valid while the whole cable is much shorter than a wavelength at the frequency of interest,
or equivalently while the signal's rise time is much longer than the time light takes to
traverse it. Beyond that, the cable is a *transmission line* with a characteristic impedance

$$Z_0 = \frac{1}{2\pi}\sqrt{\frac{\mu_0}{\varepsilon_0\varepsilon_r}}\,\ln\frac{b}{a}
= \frac{60\,\Omega}{\sqrt{\varepsilon_r}}\ln\frac{b}{a}$$

```text
RG-58:  Z0 = (60 / sqrt(2.25)) * 1.187 = 40 * 1.187 = 47.5 ohm     (sold as 50)
signal speed  v = c / sqrt(eps_r) = 3.00e8 / 1.5 = 2.0e8 m/s
              which is 5.0 ns for every metre of cable
```

Notice that the same $\ln(b/a)$ appears, upside down: a cable with low capacitance per
metre has a high impedance, and the two facts are the same fact. Beyond the lumped regime a
cable must be *terminated* in $Z_0$ rather than merely loaded, and the 100 pF/m stops being
the thing you worry about. Module 10 gets as far as the wave; the transmission line itself
belongs to a later course.

**A perfectly concentric geometry.** Push the inner conductor off-centre — bend the cable
tightly, or crush it — and the gap on one side narrows, the field there rises, and both
$C'$ and $Z_0$ shift. It is the reason cables have a specified minimum bend radius and the
reason a crushed cable never fully recovers.

**A constant $\varepsilon_r$.** Polyethylene's 2.25 holds remarkably well from DC to
several gigahertz, which is why it is used. Other dielectrics do not: PVC is around 4 at
mains frequency and falls with frequency, and it is lossy, so PVC-insulated cable is a
mediocre signal cable however good its screen.

**A perfect screen.** A single foil screen has 100% coverage but a seam and a poor
connection at the connector; a braid has 85–95% coverage and small holes everywhere. Good
cable uses both. None of this appears in $2\pi\varepsilon_0\varepsilon_r/\ln(b/a)$, which
happily describes a cable with no screen holes at all.
''',
                },
            ],
            "tune": {
                "title": "How much screened cable can the sensor drive?",
                "minutes": 10,
                "brief": r'''
A sensor sits at the far end of a screened cable. The screen keeps interference out of
the signal wire, which is the whole reason for using it, and the price is the
capacitance between the wire and the screen — around 100 pF for every metre, from the
$2\pi\varepsilon_0\varepsilon_r/\ln(b/a)$ of this module.

That capacitance is not wasted. Together with the sensor's own output resistance it is
a first-order low-pass, and a low-pass is exactly what you want against the residue of
interference the screen did not stop. But the same filter attenuates the signal, and
those two facts pull in opposite directions:

- more capacitance (a longer cable, or one deliberately added at the amplifier) pushes
  the corner down and rejects more interference, and eventually eats the signal;
- a lower source resistance pushes the corner up and preserves the signal, and stops
  rejecting anything.

The panel reports the corner, what survives at the 100 Hz the sensor actually produces,
and what is left of a 10 kHz interferer.
''',
                "prompt": "Keep 99% of the signal at 100 Hz and get the 10 kHz interference at least 20 dB down.",
                "note": "It opens on a kilometre of cable: at 100 pF per metre, 100 nF is a thousand metres of it, and 10 k\u03a9 into that filters beautifully \u2014 it has already taken 15% of the signal with it. The slider spans 1 to 1000 nF, which is 10 m of cable at one end and 10 km at the other.",
                "model": "rc-lowpass",
                "initial": {"r": 10000, "c": 100},
                "constants": {"fsig": 100, "fnoise": 10000},
                "constraints": [
                    {"k": "keep", "label": "at least 0.99 of the signal survives at 100 Hz", "min": 0.99},
                    {"k": "reject", "label": "the 10 kHz interferer is 20 dB down or better", "max": -20.0},
                ],
            },
            "derive": {
                "title": "A sphere's capacitance, and the field at any conductor's surface",
                "minutes": 12,
                "vars": ["Q", "R", "V", "C", "E", "sigma", "k", "A"],
                "brief": r'''
An isolated metal sphere of radius $R$ carries a charge $Q$. All of it sits on the
surface, and outside the sphere the field is indistinguishable from that of a point
charge $Q$ at the centre — so everything you derived in module 2 applies unchanged.

Work with the Coulomb constant $k = 1/(4\pi\varepsilon_0)$ rather than $\varepsilon_0$
itself; the last step is where the two meet.
''',
                "steps": [
                    {
                        "prompt": "Take the potential to be zero far away. What is the potential $V$ at the surface of the sphere, in terms of $k$, $Q$ and $R$?",
                        "answer": "\\frac{k Q}{R}",
                        "hint": "Outside the sphere the field is a point charge's field, so the potential is a point charge's potential \u2014 evaluated at $r = R$, the nearest you can get.",
                        "deconstruct": [
                            "A point charge gives $V = kQ/r$.",
                            "The surface is at $r = R$, and everywhere inside is at that same potential because the metal is an equipotential.",
                        ],
                    },
                    {
                        "prompt": "Capacitance is charge divided by the potential it produces. Write $C$ for this sphere.",
                        "answer": "\\frac{R}{k}",
                        "hint": "Divide $Q$ by the $V$ you just wrote. The charge cancels, which it has to \u2014 capacitance is a property of the shape.",
                        "deconstruct": [
                            "$C = Q/V = Q \\div (kQ/R)$.",
                            "The $Q$ cancels top and bottom.",
                        ],
                    },
                    {
                        "prompt": "Now the surface. The charge is spread evenly over the sphere's area $4\\pi R^2$. Write the surface charge density $\\sigma$.",
                        "answer": "\\frac{Q}{4 \\pi R^2}",
                        "hint": "Charge divided by area, and the area of a sphere is $4\\pi R^2$.",
                        "deconstruct": [
                            "By symmetry there is no reason for any patch to hold more than any other, so the density is uniform.",
                            "Uniform means $\\sigma = Q/A$ with $A = 4\\pi R^2$.",
                        ],
                    },
                    {
                        "prompt": "Write the field $E$ just outside the surface, in terms of $k$, $Q$ and $R$.",
                        "answer": "\\frac{k Q}{R^2}",
                        "hint": "Again the outside field is a point charge's field, now evaluated at $r = R$ \u2014 and this time it is the field, not the potential, so the $R$ is squared.",
                        "deconstruct": [
                            "A point charge gives $E = kQ/r^2$.",
                            "Set $r = R$.",
                        ],
                    },
                    {
                        "prompt": "Divide that field by the density $\\sigma$. What is $E/\\sigma$?",
                        "answer": "4 \\pi k",
                        "placeholder": "a number times k",
                        "hint": "Both expressions contain $Q$ and a power of $R$. Write the division out and see what is left.",
                        "deconstruct": [
                            "$E/\\sigma = (kQ/R^2) \\times (4\\pi R^2/Q)$.",
                            "The $Q$ cancels and so does $R^2$.",
                        ],
                    },
                ],
                "closing": r'''
$4\pi k$ is $1/\varepsilon_0$ by the definition of $k$, so what you have proved is
$E = \sigma/\varepsilon_0$ — and although it came out of a sphere, nothing in the last
two steps used the radius except to cancel it. The pillbox argument in the quiz gets
the same answer for a surface of any shape.

The capacitance $R/k$ is worth a number. The Earth has $R = 6.37\times10^6$ m, so as a
lone conductor in space it is a 709 µF capacitor — a component you could hold in your
hand. That is how weak an isolated capacitance is, and why every practical capacitor is
two conductors close together rather than one on its own.
''',
            },
            "blanks": {
                "title": "The conductor relations, term by term",
                "minutes": 9,
                "caption": "six statements this module rests on, with the load-bearing part removed",
                "lang": "text",
                "brief": r'''
Nothing here is executed. These are the results the drills use, and each hole sits where
a slip changes the answer rather than the spelling — a factor of two, a power of a radius,
and the one logarithm.

Two of the distractors are the *electrostatic* result for a different geometry: the sheet
instead of the surface, the sphere instead of the cylinder. That is the standard failure in
this module. The formulae are close cousins and the geometry is the only thing that tells
them apart.
''',
                "listing": """# A lump of metal, any shape, sitting still with no current in it.

E_inside = ___

# An excess charge Q placed on it ends up

located_on = ___

# Just outside the surface, where the local surface charge density is sigma:

E_just_outside = ___

# An isolated sphere of radius R in vacuum, potential measured from infinity:

C = ___

# Coaxial cable: inner radius a, screen radius b, dielectric eps_r.

C_per_metre = 2*pi*eps0*eps_r / ___

# and between the two conductors, at a radius r from the axis, with lambda
# coulombs on every metre of the inner conductor:

E(r) = lambda / ___
""",
                "blanks": [
                    {
                        "prompt": "The field inside the metal is:",
                        "hole": "?",
                        "opts": ["0", "sigma/eps0", "rho*J", "V/d"],
                        "a": 0,
                        "why": "Exactly zero, because any field left over would be a force on charges that are free to move, and they would move until it was gone. The word doing the work is *still*: this is the electrostatic case.",
                        "whys": [
                            "Exactly zero, because any field left over would be a force on charges that are free to move, and they would move until it was gone. The word doing the work is *still*: this is the electrostatic case.",
                            "That is the field just *outside* the surface, on the other side of the pillbox. Inside there is none — which is precisely why the whole of $\\sigma$'s flux has to leave through the outer face and the outside field comes out twice an isolated sheet's.",
                            "This is the field inside a conductor that is carrying a current, and module 6 is about it. It is not zero, but it is small: 10 A in a square millimetre of copper gives 0.17 V/m. The condition stated here is no current, and then it collapses to zero.",
                            "$V/d$ is the uniform field in the gap of a parallel-plate capacitor — in the insulator between the plates, not in the plates themselves. Inside the plates it is zero, which is why the whole of $V$ is dropped across the gap.",
                        ],
                    },
                    {
                        "prompt": "The excess charge ends up:",
                        "hole": "?",
                        "opts": [
                            "the outer surface",
                            "the whole volume, spread evenly",
                            "the outer surface, but only if the lump is a sphere",
                            "the centre of the lump",
                        ],
                        "a": 0,
                        "why": "Draw any closed surface in the bulk. The field on it is zero, so the flux is zero, so it encloses no net charge — and that holds for every surface you can draw in there, however small. The only place left is the boundary.",
                        "whys": [
                            "Draw any closed surface in the bulk. The field on it is zero, so the flux is zero, so it encloses no net charge — and that holds for every surface you can draw in there, however small. The only place left is the boundary.",
                            "Spread evenly through the volume is what a charged *insulator* can do, because its charges cannot move. In a conductor a uniformly charged interior would make a field inside itself, and that field would immediately drive the charge apart.",
                            "The argument never mentioned the shape. Every closed surface drawn inside any conductor of any shape encloses zero net charge, so a cube, a wire and a crumpled sheet all keep their charge on the outside. The shape decides how the charge is *distributed* over the surface, not whether it is there.",
                            "A concentration at the centre is the one arrangement that maximises the field it makes inside the metal. It would fly apart in about $10^{-19}$ s, which is the relaxation time $\\varepsilon_0\\rho$ for copper.",
                        ],
                    },
                    {
                        "prompt": "Just outside the surface the field is:",
                        "hole": "?",
                        "opts": ["sigma/eps0", "sigma/(2*eps0)", "sigma*eps0", "0"],
                        "a": 0,
                        "why": "The Gaussian pillbox has one face inside the metal, where the field is zero, so the whole of the enclosed charge $\\sigma A$ must escape through the outer face alone: $EA = \\sigma A/\\varepsilon_0$.",
                        "whys": [
                            "The Gaussian pillbox has one face inside the metal, where the field is zero, so the whole of the enclosed charge $\\sigma A$ must escape through the outer face alone: $EA = \\sigma A/\\varepsilon_0$.",
                            "This is the field of an isolated charged sheet, which is the same law applied to a different geometry: a sheet sitting in vacuum lets flux out of both faces and each face gets half of it. A conductor's surface has a field-free region behind it, so it sends everything one way.",
                            "Multiplying by $\\varepsilon_0$ rather than dividing gives something around $10^{-23}$ times too small, and the units come out as coulombs per volt per metre cubed — nothing. When a constant can go either way, check what a big $\\varepsilon_0$ ought to mean: a medium that permits more flux for the same charge, hence a *smaller* field.",
                            "Zero is the field on the other side of that pillbox face, a few atoms away inside the metal. The field is discontinuous across a charged surface, and the size of the jump is exactly $\\sigma/\\varepsilon_0$.",
                        ],
                    },
                    {
                        "prompt": "The capacitance of an isolated sphere of radius $R$:",
                        "hole": "?",
                        "opts": ["4*pi*eps0*R", "4*pi*eps0*R**2", "eps0*A/d", "4*pi*eps0/R"],
                        "a": 0,
                        "why": "The surface sits at $V = kQ/R$, so $C = Q/V = R/k = 4\\pi\\varepsilon_0 R$. Capacitance is a length times a constant, which is why it scales with the size of a thing rather than with its area.",
                        "whys": [
                            "The surface sits at $V = kQ/R$, so $C = Q/V = R/k = 4\\pi\\varepsilon_0 R$. Capacitance is a length times a constant, which is why it scales with the size of a thing rather than with its area.",
                            "An $R^2$ is the sphere's area creeping in from $\\sigma = Q/4\\pi R^2$. The area is what fixes the charge *density*; the capacitance came from the potential, which carries a single power of $R$.",
                            "This is the parallel-plate result, and it needs two conductors and a gap between them. An isolated sphere has only one conductor — the second plate is infinity — so there is no $d$ to put anywhere.",
                            "Dividing by $R$ makes a small sphere a large capacitor, which is backwards: a small sphere reaches a high potential on very little charge, and that is what a *low* capacitance means. Test any candidate on the Earth, which at $R = 6.37\\times10^6$ m is 709 µF.",
                        ],
                    },
                    {
                        "prompt": "What divides $2\\pi\\varepsilon_0\\varepsilon_r$ for a coaxial cable?",
                        "hole": "?",
                        "opts": ["log(b/a)", "b/a", "log(a/b)", "b - a"],
                        "a": 0,
                        "why": "The potential between the conductors is $\\int_a^b \\lambda\\,\\mathrm{d}r/(2\\pi\\varepsilon_0 r)$, and integrating $1/r$ gives the logarithm. It is why the capacitance depends only on the *ratio* of the radii, and why it moves so little when you change that ratio.",
                        "whys": [
                            "The potential between the conductors is $\\int_a^b \\lambda\\,\\mathrm{d}r/(2\\pi\\varepsilon_0 r)$, and integrating $1/r$ gives the logarithm. It is why the capacitance depends only on the *ratio* of the radii, and why it moves so little when you change that ratio.",
                            "A bare ratio would make the capacitance fall in proportion to the screen radius, so doubling the screen would halve it. It does not: it multiplies it by $\\ln 3/\\ln 6 = 0.61$. The whole character of the coaxial geometry is that the logarithm resists you.",
                            "Upside down. Since $b > a$, $\\ln(a/b)$ is negative, and this would report a negative capacitance for every cable ever made. The integral runs from the inner radius outward, so the larger radius is on top.",
                            "$b - a$ is the thickness of the dielectric, and it is the answer to a parallel-plate question: field times gap. Here the field is not uniform across the gap — it falls off as $1/r$ — so the potential is not the field times the distance, and a plain subtraction cannot appear.",
                        ],
                    },
                    {
                        "prompt": "And the field between the conductors, at radius $r$:",
                        "hole": "?",
                        "opts": ["2*pi*eps0*r", "4*pi*eps0*r**2", "2*pi*eps0*r**2", "2*pi*eps0*a"],
                        "a": 0,
                        "why": "Gauss's law on a coaxial cylinder of radius $r$ and length $L$: the curved wall has area $2\\pi r L$ and encloses $\\lambda L$, so $E \\cdot 2\\pi r L = \\lambda L/\\varepsilon_0$ and the length cancels. A single power of $r$, because a line of charge feeds a cylinder.",
                        "whys": [
                            "Gauss's law on a coaxial cylinder of radius $r$ and length $L$: the curved wall has area $2\\pi r L$ and encloses $\\lambda L$, so $E \\cdot 2\\pi r L = \\lambda L/\\varepsilon_0$ and the length cancels. A single power of $r$, because a line of charge feeds a cylinder.",
                            "This is the point charge's denominator — the area of a sphere. A point feeds a sphere and gives an inverse square; a line feeds a cylinder and gives an inverse first power. The geometry of the source decides the power, every time.",
                            "A plausible-looking hybrid with the right $2\\pi$ and Coulomb's square attached. Check it against the capacitance: integrating this from $a$ to $b$ would give a potential going as $1/a - 1/b$, and no logarithm would ever appear in the capacitance. It does appear, so this cannot be the field.",
                            "Fixing the radius at $a$ would make the field the same everywhere in the dielectric. It is not — it is strongest at the inner conductor and weakest at the screen, which is why a cable always breaks down from the middle outwards. Setting $r = a$ gives the peak field, not the field.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "What a metre of that cable is worth",
                    "minutes": 5,
                    "brief": r'''
The mechanical rung: one formula, one unknown, every quantity given. The only thing it can
catch you on is that the dimensions are quoted the way a datasheet quotes them — as
diameters — and the formula wants radii.

That particular trap is harmless here, because $b/a$ is the same number either way. It is
worth noticing anyway, because two questions further down the ladder the same habit costs
a factor of two.
''',
                    "prompt": "What is the capacitance of one metre of this cable?",
                    "note": "Give the answer in picofarads per metre, to one decimal place.",
                    "figure": r'''
```text
   coaxial cable, seen end-on

          .-------------------.
         /   screen (braid)    \
        |    .-----------.      |
        |   /  dielectric \     |      inner conductor:  1.0 mm across
        |  |    ( . )      |    |      dielectric:       3.6 mm across
        |   \   inner     /     |      dielectric:       polyethylene,
        |    '-----------'      |                        eps_r = 2.3
         \                     /
          '-------------------'

   C' = 2 pi eps0 eps_r / ln(b/a)   farads per metre
```
''',
                    "given": [
                        {"label": "Inner conductor diameter", "value": "1.0 mm"},
                        {"label": "Dielectric outer diameter (= screen inner diameter)", "value": "3.6 mm"},
                        {"label": "Relative permittivity of the dielectric", "value": "2.3"},
                        {"label": "Permittivity of free space", "value": "8.854 × 10⁻¹² F/m"},
                    ],
                    "aside": "Work out $2\\pi\\varepsilon_0 = 5.563\\times10^{-11}$ F/m once and keep it. "
                             "It is the coaxial world's counterpart of $\\mu_0/2\\pi = 2\\times10^{-7}$, and "
                             "it turns this into one multiplication and one division.",
                    "answer": 99.9,
                    "tol": 1.5,
                    "unit": "pF/m",
                    "hint": "$b/a$ is a ratio, so the diameters can go straight in: $3.6/1.0 = 3.6$, and "
                            "$\\ln 3.6 = 1.281$.",
                    "wrong": "If you got 35.5, the ratio itself was used as the divisor instead of its "
                             "logarithm. If you got 128, the logarithm was left out altogether. If you "
                             "got 43.4, the dielectric was forgotten and the cable was treated as "
                             "air-filled — the difference between those two is exactly what "
                             "$\\varepsilon_r$ buys.",
                    "why": "$b/a = 3.6/1.0 = 3.6$ whether you read the numbers as diameters or halve them "
                           "first, and $\\ln 3.6 = 1.2809$. The numerator is $2\\pi\\varepsilon_0"
                           "\\varepsilon_r = 5.5631\\times10^{-11} \\times 2.3 = 1.2795\\times10^{-10}$, "
                           "so $C' = 1.2795\\times10^{-10}/1.2809 = 9.989\\times10^{-11}$ F/m, which is "
                           "99.9 pF per metre. That is the hundred-picofarads-a-metre of the concept list, "
                           "and it is not a coincidence of this cable: almost every coaxial cable made has "
                           "a radius ratio somewhere near three and a plastic dielectric near 2.3, because "
                           "that combination is what gives 50 Ω. Two consequences worth carrying away. A "
                           "10 m lead is 1 nF, which is a real capacitor by any standard — larger than "
                           "most of the ones deliberately fitted to a small-signal circuit. And the "
                           "capacitance is set by the *ratio* of the radii alone, so scaling the whole "
                           "cable up tenfold would leave this number exactly where it is.",
                },
                {
                    "title": "What appears on the outside of the shell",
                    "minutes": 7,
                    "brief": r'''
No formula is given for this one, because the arithmetic is trivial and the physics is not.
Two questions have to be answered before any number can be written down: how much charge
ends up on the outer surface, and why.

The shell is *neutral* and connected to nothing. It has not gained or lost any charge; it
has only rearranged what it already had.
''',
                    "prompt": "What is the surface charge density on the outer surface of the shell?",
                    "note": "Give the answer in nanocoulombs per square metre, to one decimal place.",
                    "figure": r'''
```text
   a neutral spherical metal shell, cut through the middle

              ,---------------------.
            ,'    metal shell         `.
           /   .-------------------.    \
          |   /                     \    |
          |  |     * +2.5 nC         |   |     cavity inner radius  3.0 cm
          |  |    (at the centre)    |   |     shell outer radius   4.0 cm
          |   \                     /    |
           \   '-------------------'    /      the shell carries no net
            `.                        ,'       charge of its own
              '---------------------'
```
''',
                    "given": [
                        {"label": "Point charge at the centre of the cavity", "value": "+2.5 nC"},
                        {"label": "Inner radius of the shell", "value": "3.0 cm"},
                        {"label": "Outer radius of the shell", "value": "4.0 cm"},
                        {"label": "Net charge on the shell itself", "value": "zero"},
                    ],
                    "aside": "Draw a closed surface that lies entirely within the metal and surrounds the "
                             "cavity. You know the field everywhere on it without calculating anything, so "
                             "you know the charge it encloses.",
                    "answer": 124.3,
                    "tol": 1.5,
                    "unit": "nC/m²",
                    "hint": "The inner wall must carry $-2.5$ nC. The shell was neutral, so the $+2.5$ nC it "
                            "is left with has nowhere to go but the outer surface — where it spreads over "
                            "$4\\pi R_{\\text{out}}^2$.",
                    "wrong": "If you got 221.0, the outer charge was spread over the *inner* radius. If you "
                             "got 62.2 the charge was halved somewhere, and if you got zero the shell was "
                             "assumed to hide the charge inside it — which is what earthing it would do, "
                             "and it is not earthed.",
                    "why": "A Gaussian surface drawn inside the metal has $E = 0$ everywhere on it, so it "
                           "encloses no net charge; it encloses the $+2.5$ nC and the inner wall, so the "
                           "inner wall holds $-2.5$ nC. The shell started neutral and nothing has flowed "
                           "in or out, so the matching $+2.5$ nC sits on the outer surface, over an area "
                           "$4\\pi R^2 = 4\\pi(0.040)^2 = 2.011\\times10^{-2}$ m². That gives $\\sigma = "
                           "2.5\\times10^{-9}/2.011\\times10^{-2} = 1.243\\times10^{-7}$ C/m², or 124.3 "
                           "nC/m². Check it against the surface field: $\\sigma/\\varepsilon_0 = 1.243"
                           "\\times10^{-7}/8.854\\times10^{-12} = 1.404\\times10^{4}$ V/m, and the field of "
                           "a bare 2.5 nC at 4 cm is $kQ/r^2 = 8.988\\times10^9 \\times 2.5\\times10^{-9}/"
                           "1.6\\times10^{-3} = 1.405\\times10^4$ V/m. They agree, and that agreement is the "
                           "real lesson: from outside, the shell has hidden nothing at all. Slide the point "
                           "charge off-centre and the inner wall's density redistributes wildly while this "
                           "number does not move, because the field-free metal between them means the outer "
                           "surface has no way of learning where the charge went.",
                },
                {
                    "title": "How much voltage before the cable arcs",
                    "minutes": 9,
                    "brief": r'''
Same cable as the first rung, now with a voltage across it. The field between the
conductors is not uniform — it falls off as $1/r$ — so there is a worst place, and the
cable fails there first while everywhere else is still comfortable.

You have $E(r) = \lambda/2\pi\varepsilon_0 r$ and $V = (\lambda/2\pi\varepsilon_0)\ln(b/a)$.
Eliminate $\lambda$ between them, decide which radius is the dangerous one, and invert.

This is the rung where reading a diameter as a radius costs you a factor of two, in the
direction that says the cable is safe when it is not.
''',
                    "prompt": "What voltage between the conductors brings the dielectric to its breakdown field?",
                    "note": "Give the answer in kilovolts, to one decimal place.",
                    "figure": r'''
```text
   the field in the dielectric, plotted against radius

   E |*
     | *
     |  *                E(r) = lambda / (2 pi eps0 r)
     |    *
     |       *  *
     |             *  *  *  *
     +----|--------------------|----------> r
        r = a                r = b
      inner conductor        screen

   inner conductor 1.0 mm across, dielectric 3.6 mm across,
   polyethylene: eps_r = 2.3, breakdown field 22 MV/m
```
''',
                    "given": [
                        {"label": "Inner conductor diameter", "value": "1.0 mm"},
                        {"label": "Dielectric outer diameter", "value": "3.6 mm"},
                        {"label": "Dielectric strength of polyethylene", "value": "22 MV/m"},
                    ],
                    "aside": "$\\varepsilon_r$ appears on the figure and is not needed here. It fixes how "
                             "much charge sits on the conductors for a given voltage; the relation between "
                             "the field and the voltage is the same whatever is in the gap.",
                    "answer": 14.1,
                    "tol": 0.3,
                    "unit": "kV",
                    "hint": "$E_{\\max} = V/(a\\ln(b/a))$, at $r = a$. Rearranged, $V = E_{\\max}\\,a"
                            "\\ln(b/a)$ — and $a$ is 0.5 mm, not 1.0 mm.",
                    "wrong": "If you got 28.2, the inner *diameter* went in where the radius belongs, and "
                             "the cable would arc at half the voltage you cleared it for. If you got 50.7, "
                             "the screen radius was used — the safest place in the cable rather than the "
                             "most dangerous. If you got 11.0, the logarithm was dropped and the answer "
                             "is just the breakdown field times the inner radius.",
                    "why": "Substituting $\\lambda = 2\\pi\\varepsilon_0 V/\\ln(b/a)$ into $E(r)$ gives "
                           "$E(r) = V/(r\\ln(b/a))$, which is largest at the smallest radius in the "
                           "dielectric — the surface of the inner conductor, $r = a = 0.50$ mm. So "
                           "$V_{\\max} = E_{\\text{break}}\\,a\\ln(b/a) = 22\\times10^6 \\times 0.50"
                           "\\times10^{-3} \\times 1.2809 = 1.409\\times10^4$ V, or 14.1 kV. At that point "
                           "the field out at the screen is only $22 \\times (0.5/1.8) = 6.1$ MV/m, well "
                           "within the material's limit: the whole failure is happening at the thin wire "
                           "in the middle while three quarters of the dielectric is untroubled. Two "
                           "practical corollaries. A real cable of this size is rated at perhaps 2 kV, not "
                           "14 — the margin covers voids in the extrusion, moisture, and the fact that a "
                           "nick or a stray whisker on the inner conductor is a place where the local "
                           "radius is microns rather than half a millimetre, and the field there is "
                           "correspondingly enormous. And if you were free to choose $a$ with $b$ fixed, "
                           "the best possible choice is $b/a = e = 2.718$, where $a\\ln(b/a)$ is at its "
                           "maximum; this cable's 3.6 is a little past it, because it was designed for "
                           "50 Ω rather than for breakdown.",
                },
                {
                    "title": "What the amplifier actually sees",
                    "minutes": 9,
                    "brief": r'''
A circuit now. A sensor with an output resistance of 33 kΩ drives 33 m of the cable from
the first rung — about 3.3 nF of it — into an amplifier whose input resistance is 470 kΩ,
with a 100 kΩ resistor at the far end holding the input defined when nothing is plugged in.

Long after switch-on nothing is changing, so no current flows into or out of the
capacitor and it can be lifted off the diagram entirely. What is left is a divider, but
not the two-resistor one it looks like: two resistors hang from the far node, and they
share the job of pulling it down.

The 3.3 nF is honest information about the cable and plays no part whatever in this
answer.
''',
                    "prompt": "Once everything has settled, what voltage appears at the probe?",
                    "note": "Give the answer in volts, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 33000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 100000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "c1", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 3.3e-9},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "r3", "kind": "R", "x": 19, "y": 6, "rot": 1, "value": 470000},
                            {"id": "g3", "kind": "GND", "x": 19, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 21, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [21, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [15, 3], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [19, 3], "b": [19, 5]},
                            {"a": [19, 7], "b": [19, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Sensor open-circuit output", "value": "5.0 V"},
                        {"label": "Sensor output resistance", "value": "33 kΩ"},
                        {"label": "Bias resistor at the amplifier", "value": "100 kΩ"},
                        {"label": "Amplifier input resistance", "value": "470 kΩ"},
                        {"label": "Cable capacitance (33 m at 100 pF/m)", "value": "3.3 nF"},
                    ],
                    "aside": "Rub the capacitor out of your sketch before doing any arithmetic. At DC it "
                             "carries no current, so it is not there.",
                    "answer": 3.571,
                    "tol": 0.02,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "Combine the 100 kΩ and the 470 kΩ into one resistance to ground, then divide "
                            "5 V between the 33 kΩ and that.",
                    "wrong": "If you got 4.672, the 100 kΩ bias resistor was left out and only the "
                             "amplifier's own input resistance loaded the cable. If you got 3.759, the "
                             "amplifier's 470 kΩ was left out instead and the bias resistor did all the "
                             "loading.",
                    "why": "The capacitor is an open circuit at DC, so the far node has two resistors to "
                           "ground: $100\\parallel470 = 47000/570 = 82.46$ kΩ. That sits in series with "
                           "the sensor's 33 kΩ, so the node is at $5.0 \\times 82.46/(33 + 82.46) = 5.0 "
                           "\\times 0.7142 = 3.571$ V. Two things are worth taking from that. The signal "
                           "has already lost 29% before any cable capacitance has been considered at all "
                           "— that loss is pure resistive division, it is the same at every frequency, "
                           "and it is caused by the 100 kΩ bias resistor far more than by the amplifier. "
                           "And the capacitance the cable contributes is not idle: with the 33 kΩ source "
                           "and the 82.5 kΩ load looking back at it, the capacitor sees a Thévenin "
                           "resistance of $33\\parallel82.46 = 23.6$ kΩ, so the corner is $1/(2\\pi "
                           "\\times 23.6\\times10^3 \\times 3.3\\times10^{-9}) = 2.0$ kHz. Below 2 kHz "
                           "the cable is invisible and the answer above is the whole story; above it, "
                           "this rung's arithmetic stops being the right question.",
                },
                {
                    "title": "How much charge is sitting on the cable",
                    "minutes": 13,
                    "brief": r'''
The last rung. The far end of the cable is no longer just loaded to ground: a 120 kΩ
resistor pulls it towards a 1.5 V reference rail, which is how a sensor that swings both
ways is given a mid-scale resting point. That rail is a second source, and it drives
current into the node exactly as the sensor does.

So the far node is set by three branches, not two, and no single division will give it to
you. Write one node equation instead: everything arriving equals everything leaving.

And the quantity asked for is not a voltage. Once you have the node, the charge standing
on the cable's inner conductor — mirrored by an equal and opposite charge on the screen,
which is what makes it a capacitor at all — is $Q = CV$.
''',
                    "prompt": "Once everything has settled, how much charge is stored on the cable capacitance?",
                    "note": "Give the answer in nanocoulombs, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 3.3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 82000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 330000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "c1", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 6.8e-9},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 17, "y": 1},
                            {"id": "r3", "kind": "R", "x": 21, "y": 6, "rot": 1, "value": 120000},
                            {"id": "v2", "kind": "V", "x": 21, "y": 9, "rot": 1, "value": 1.5},
                            {"id": "g3", "kind": "GND", "x": 21, "y": 12},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [21, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [15, 3], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [17, 3], "b": [17, 1]},
                            {"a": [21, 3], "b": [21, 5]},
                            {"a": [21, 7], "b": [21, 8]},
                            {"a": [21, 10], "b": [21, 12]},
                        ],
                    },
                    "given": [
                        {"label": "Sensor open-circuit output", "value": "3.3 V"},
                        {"label": "Sensor output resistance", "value": "82 kΩ"},
                        {"label": "Cable capacitance (68 m at 100 pF/m)", "value": "6.8 nF"},
                        {"label": "Bias resistor to ground", "value": "330 kΩ"},
                        {"label": "Resistor to the reference rail", "value": "120 kΩ"},
                        {"label": "Reference rail", "value": "1.5 V"},
                    ],
                    "aside": "Take the far node as $V$ and write the currents in siemens and volts: "
                             "$(V-3.3)/82\\text{k} + V/330\\text{k} + (V-1.5)/120\\text{k} = 0$. Collect "
                             "the conductances on one side and the two driving terms on the other.",
                    "answer": 15.22,
                    "tol": 0.2,
                    "unit": "nC",
                    "check": r'''
const cap = c.net.parts.filter(function (p) { return p.kind === 'C'; })[0];
const d = c.dc();
return cap.value * (d.v[cap.n1] - d.v[cap.n2]) * 1e9;
''',
                    "hint": "Solve $V \\times (1/82\\text{k} + 1/330\\text{k} + 1/120\\text{k}) = 3.3/82"
                            "\\text{k} + 1.5/120\\text{k}$, then multiply the answer by 6.8 nF.",
                    "wrong": "If you got 11.62, the 1.5 V rail was treated as a ground, so the 120 kΩ "
                             "became one more load pulling the node down rather than a source pushing it "
                             "up. If you got 17.97 the reference branch was left out of the node equation "
                             "altogether. If you got 22.44 the charge was taken as $C$ times the sensor's "
                             "open-circuit 3.3 V, ignoring everything the cable is connected to.",
                    "why": "The capacitor is open at DC, so only the three resistive branches decide the "
                           "node. The conductances are $1/82\\text{k} = 12.195\\,\\mu\\text{S}$, "
                           "$1/330\\text{k} = 3.030\\,\\mu\\text{S}$ and $1/120\\text{k} = 8.333\\,"
                           "\\mu\\text{S}$, totalling $23.559\\,\\mu\\text{S}$; the two sources push in "
                           "$3.3/82\\text{k} = 40.244\\,\\mu\\text{A}$ and $1.5/120\\text{k} = 12.500\\,"
                           "\\mu\\text{A}$, totalling $52.744\\,\\mu\\text{A}$. So $V = 52.744/23.559 = "
                           "2.2388$ V, and the cable holds $Q = CV = 6.8\\times10^{-9} \\times 2.2388 = "
                           "1.522\\times10^{-8}$ C, or 15.22 nC. Notice what the reference rail did: "
                           "without it the node would sit at $3.3 \\times 330/(82+330) = 2.643$ V, so "
                           "adding a 1.5 V bias *pulled the signal down*, which is the intended "
                           "behaviour — it is there to move the resting point, and it costs some gain to "
                           "do it. The 15.22 nC is the number to keep. It is the charge that has to be "
                           "physically moved onto and off the inner conductor every time the signal "
                           "changes, and it is the sensor's 82 kΩ that has to move it: swinging this "
                           "node by one volt means shifting 6.8 nC, and through 82 kΩ that takes about "
                           "$\\tau = [82\\text{k}\\parallel(330\\text{k}\\parallel120\\text{k})] \\times "
                           "6.8\\,\\text{nF} = 42.4\\,\\text{k}\\Omega \\times 6.8\\,\\text{nF} = 290$ µs. "
                           "Sixty-eight metres of screening has turned a "
                           "sensor into a slow one, and no amount of amplification at the far end gets "
                           "that back.",
                },
            ],
            "quiz": {
                "title": "What a conductor does to a field, checked",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A solid metal sphere is given a charge of $+6$ nC and left alone. Where does that charge end up?",
                        "opts": [
                            "Spread evenly through the volume of the metal",
                            "All of it on the outer surface",
                            "Concentrated at the centre",
                            "Half on the surface and half at the centre",
                        ],
                        "a": 1,
                        "why": (
                            "Draw any closed surface inside the metal. The field on it is zero, so the flux "
                            "through it is zero, so by Gauss's law it encloses no net charge \u2014 and that is "
                            "true of every surface you can draw in the bulk. The only place left is the "
                            "outside. Nothing about this argument used the sphere's shape: it holds for a "
                            "lump of any shape at all."
                        ),
                    },
                    {
                        "q": "A hollow, uncharged metal shell has a $+2$ nC point charge suspended at the centre of its cavity. What charge appears on the inner wall of the shell?",
                        "opts": ["$-2$ nC", "$+2$ nC", "None", "$-1$ nC"],
                        "a": 0,
                        "why": (
                            "Take a closed surface lying inside the metal itself and surrounding the cavity. "
                            "The field on it is zero, so it encloses no net charge \u2014 which means the $-2$ nC "
                            "drawn onto the inner wall exactly matches the charge inside. The shell was neutral "
                            "to begin with, so $+2$ nC is left on its outer surface, and from far away the whole "
                            "assembly still looks like $+2$ nC."
                        ),
                    },
                    {
                        "q": "Two isolated spheres of radius 2 cm and 6 cm are joined by a long thin wire and charged up. Which surface has the stronger electric field just outside it?",
                        "opts": [
                            "The large sphere, because it holds more charge",
                            "The small sphere, by a factor of three",
                            "They are equal, because the wire makes them one conductor",
                            "The small sphere, by a factor of nine",
                        ],
                        "a": 1,
                        "why": (
                            "The wire makes them one conductor, so they share a potential: $kQ/R$ is the same "
                            "for both, and the charge divides in proportion to the radius. The density "
                            "$\\sigma = Q/4\\pi R^2$ therefore goes as $1/R$, and so does the surface field "
                            "$\\sigma/\\varepsilon_0$. Three times the radius, one third of the field. The large "
                            "sphere does hold three times the charge \u2014 that is exactly why its field is weaker, "
                            "since it is spread over nine times the area."
                        ),
                    },
                    {
                        "q": "An isolated sheet of charge of density $\\sigma$ makes a field $\\sigma/2\\varepsilon_0$ on each side of it. At the surface of a charged conductor the field is $\\sigma/\\varepsilon_0$. Where does the factor of two come from?",
                        "opts": [
                            "The conductor holds twice as much charge",
                            "All the flux leaves on one side, because the field inside the metal is zero",
                            "A conductor's charge is negative, which doubles the field",
                            "It is a different constant; the two expressions describe unrelated situations",
                        ],
                        "a": 1,
                        "why": (
                            "Put a Gaussian pillbox across the surface with one face in the metal and one just "
                            "outside. The inner face contributes nothing, because $E = 0$ there. So the enclosed "
                            "charge $\\sigma A$ has to escape through the outer face alone, giving $EA = "
                            "\\sigma A/\\varepsilon_0$. An isolated sheet lets flux out of both faces and each "
                            "gets half. Same law, different geometry."
                        ),
                    },
                    {
                        "q": "You double the diameter of the outer screen of a coaxial cable from 3 mm to 6 mm, leaving the 1 mm inner conductor alone. What happens to the capacitance per metre?",
                        "opts": [
                            "It halves",
                            "It falls to about 61% of what it was",
                            "It is unchanged",
                            "It falls to a quarter",
                        ],
                        "a": 1,
                        "why": (
                            "The capacitance per metre goes as $1/\\ln(b/a)$, and a logarithm is a very slow "
                            "function. Here $\\ln 3 = 1.099$ becomes $\\ln 6 = 1.792$, so the capacitance falls "
                            "by the ratio $1.099/1.792 = 0.61$. Halving it would need $\\ln(b/a)$ to double, "
                            "which means squaring the radius ratio \u2014 an outer diameter of 9 mm. This is why "
                            "cable capacitance is so hard to design away: you cannot get much of it back "
                            "without a very fat cable."
                        ),
                    },
                    {
                        "q": "A closed metal box, connected to nothing, is brought near a strongly charged rod. What is the electric field inside the empty box?",
                        "opts": [
                            "Zero",
                            "The same as it would be with no box there",
                            "Reduced, but not to zero, unless the box is earthed",
                            "Reversed in direction",
                        ],
                        "a": 0,
                        "why": (
                            "The rod's field drives charge around on the outside of the box until the metal is "
                            "field-free, and once it is, the cavity has to be field-free too: it encloses no "
                            "charge, and its whole boundary is at one potential, so there is no potential "
                            "difference anywhere inside for a field to be the slope of. Earthing changes "
                            "nothing about *this* \u2014 it matters for holding the box's potential steady and for "
                            "keeping charges inside the box from being felt outside."
                        ),
                    },
                ],
            },
            "build": {
                "title": "Cancelling the cable: a 10:1 probe",
                "minutes": 25,
                "brief": r'''
An oscilloscope probe is a metre or so of miniature coaxial cable with a resistor in the
tip, and this module says what that cable costs: around 90 pF once its own capacitance and
the instrument's input capacitance are added up. The scope's input resistance is 1 MΩ, and
the tip resistor is 9 MΩ, so at DC the probe divides the signal by ten and the scope
multiplies its reading back by ten.

The trouble starts as soon as the signal moves. The 90 pF sits across the 1 MΩ, and

$$f_c = \frac{1}{2\pi (R_1\!\parallel\!R_2)C_2}
= \frac{1}{2\pi \times 0.9\,\mathrm{M}\Omega \times 90\,\mathrm{pF}} \approx 2\,\mathrm{kHz}$$

so above a couple of kilohertz the "divide by ten" quietly becomes divide by more than ten,
and by 100 kHz it is divide by five hundred. An instrument that lies by a factor of fifty
is worse than no instrument.

The cure is not to fight the cable capacitance but to give the *other* arm of the divider a
capacitance of its own, in exactly the right proportion. Put a capacitor $C_1$ across the
9 MΩ. Each arm is then a resistor in parallel with a capacitor, and the division ratio is
frequency-independent at all when

$$R_1 C_1 = R_2 C_2$$

because then each arm's impedance carries the same frequency dependence and it cancels in
the ratio. That is the small screw on the body of every scope probe: a trimmer, adjusted
against a square wave until the corners stop rounding over or overshooting.

The canvas opens with the 9 MΩ tip resistor, the 1 MΩ scope input, the 90 pF of cable and
instrument, a 1 V source standing for the signal, and the probe on the scope's input node.
Add the compensating capacitor and give it the right value.

Type capacitances as `10p` for ten picofarads.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 7, "y": 3, "rot": 0, "value": 9000000},
                        {"id": "p3", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 11, "y": 9, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "C", "x": 14, "y": 6, "rot": 1, "value": 9e-11},
                        {"id": "p6", "kind": "GND", "x": 14, "y": 9, "rot": 0, "value": 0},
                        {"id": "p7", "kind": "OUT", "x": 16, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [3, 3]},
                        {"a": [3, 3], "b": [6, 3]},
                        {"a": [8, 3], "b": [16, 3]},
                        {"a": [11, 3], "b": [11, 5]},
                        {"a": [11, 7], "b": [11, 9]},
                        {"a": [14, 3], "b": [14, 5]},
                        {"a": [14, 7], "b": [14, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 7, "y": 3, "rot": 0, "value": 9000000},
                        {"id": "p3", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 11, "y": 9, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "C", "x": 14, "y": 6, "rot": 1, "value": 9e-11},
                        {"id": "p6", "kind": "GND", "x": 14, "y": 9, "rot": 0, "value": 0},
                        {"id": "p7", "kind": "OUT", "x": 16, "y": 3, "rot": 0, "value": 0},
                        {"id": "p8", "kind": "C", "x": 7, "y": 1, "rot": 0, "value": 1e-11},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [3, 3]},
                        {"a": [3, 3], "b": [6, 3]},
                        {"a": [8, 3], "b": [16, 3]},
                        {"a": [11, 3], "b": [11, 5]},
                        {"a": [11, 7], "b": [11, 9]},
                        {"a": [14, 3], "b": [14, 5]},
                        {"a": [14, 7], "b": [14, 9]},
                        {"a": [6, 3], "b": [6, 1]},
                        {"a": [8, 3], "b": [8, 1]},
                    ],
                },
                "checks": [
                    {"name": "at DC it divides by ten", "code": r'''
c.close(c.vout(), 0.1, 0.02, "the settled output for a 1 V input");
'''},
                    {"name": "still a tenth at 10 kHz", "code": r'''
c.close(c.gain(1e4), 0.1, 0.03,
  "the output at 10 kHz — an uncompensated probe is already ten times low here");
'''},
                    {"name": "still a tenth at 1 MHz", "code": r'''
c.close(c.gain(1e6), 0.1, 0.05, "the output at 1 MHz");
'''},
                    {"name": "the ratio does not depend on frequency anywhere in between", "code": r'''
var lo = c.gain(10);
var fs = [100, 1e3, 1e4, 1e5, 1e6, 1e7];
for (var i = 0; i < fs.length; i++) {
  var g = c.gain(fs[i]);
  c.assert(Math.abs(g - lo) <= 0.05 * lo,
    "at " + c.fmt(fs[i], "Hz") + " the output is " + c.fmt(g, "V") +
    " but at 10 Hz it is " + c.fmt(lo, "V") + " — the division still depends on frequency");
}
'''},
                ],
                "hints": [
                    "The compensating capacitor goes *across the 9 MΩ*, from the source node to the probe node — not from either of them to ground. A capacitor to ground is one more piece of cable, and it makes things worse.",
                    "$R_1 C_1 = R_2 C_2$ with $R_1 = 9$ MΩ, $R_2 = 1$ MΩ and $C_2 = 90$ pF. Nine times the resistance needs a ninth of the capacitance.",
                    "If every check but the DC one fails, look at what value you typed: `10` is ten farads, `10p` is ten picofarads.",
                    "Well above the corner the resistors stop mattering and the two capacitors do the dividing on their own, at $C_1/(C_1+C_2)$. Get $C_1$ ten times too large and that is $100/190 = 0.53$ rather than 0.1, so a fast edge overshoots and the probe reads five times high; ten times too small and you are back where you started.",
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Current, resistivity and where the heat goes",
            "summary": "A resistor is a shape. The same move that turned a geometry into a capacitance turns one into a resistance — and tells you how fast the electrons are actually going.",
            "concepts": [
                "Current density $J = I/A$, in amps per square metre, is what a material feels. The current alone says nothing: 10 A through a busbar is idle and 10 A through a bond wire is a fuse.",
                "Charge carriers move slowly. With $n$ carriers per cubic metre each of charge $q$, $I = nAqv_d$, so a 1 mm² copper wire carrying 5 A has its electrons drifting at 0.37 mm/s — slower than a snail. The signal travels at nearly the speed of light because the field is established along the whole wire at once, not because anything is racing down it.",
                "Ohm's law as a statement about fields is $J = \\sigma E$: the current density at a point is proportional to the field at that point, with $\\sigma$ the conductivity of the material and $\\rho = 1/\\sigma$ its resistivity. Copper is $1.68\\times10^{-8}$ Ω·m at 20 °C.",
                "That local law gives the circuit law in one line. Over a uniform bar of length $\\ell$ and cross-section $A$: $V = E\\ell$ and $I = JA = \\sigma E A$, so $R = V/I = \\rho\\ell/A$. Material constant times geometry — exactly the shape of $C = \\varepsilon_0 A/d$, with the length and area the other way up.",
                "Power dissipates where the current is: $p = EJ$ watts per cubic metre, which integrates over a uniform bar to $I^2R$. And $\\rho$ for a metal climbs with temperature — copper by about 0.39% per kelvin — so a track that runs hot runs hotter, and a copper winding doubles as its own thermometer.",
            ],
            "quiz": {
                "title": "Current and resistance, checked",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A copper wire is drawn out until it is twice as long. The same metal is still there, so the cross-section has halved. What is its resistance now?",
                        "opts": ["Twice the old value", "Four times", "Unchanged", "Half"],
                        "a": 1,
                        "why": (
                            "$R = \\rho\\ell/A$ picks up a factor of two from the length and another factor of "
                            "two from the halved area, so it is four times what it was. Answering ‘twice’ is "
                            "reading the length and forgetting that stretching a fixed volume of metal must "
                            "thin it. This is why a wire that is stretched by a load has a measurable rise in "
                            "resistance, which is exactly what a strain gauge is for."
                        ),
                    },
                    {
                        "q": "Two wires of the same metal and the same length, one with twice the diameter of the other. Put the same voltage across each. Compare the currents.",
                        "opts": [
                            "The fat wire carries twice the current",
                            "The fat wire carries four times the current",
                            "They carry the same current",
                            "The fat wire carries eight times the current",
                        ],
                        "a": 1,
                        "why": (
                            "Resistance goes as $1/A$ and area goes as the square of the diameter, so twice the "
                            "diameter is four times the area and a quarter of the resistance — four times the "
                            "current. The current *density* is the same in both, which is the point: the fat "
                            "wire is not being worked any harder, there is simply more of it."
                        ),
                    },
                    {
                        "q": "Roughly how fast do individual electrons drift along a copper wire carrying an ordinary current?",
                        "opts": [
                            "About $3\\times10^{8}$ m/s",
                            "About $10^{5}$ m/s",
                            "About $10^{-4}$ m/s",
                            "They do not move at all; only the field does",
                        ],
                        "a": 2,
                        "why": (
                            "$v_d = I/(nAq)$, and copper's $n \\approx 8.5\\times10^{28}$ per cubic metre is an "
                            "enormous number, so a very slow drift carries a large current. Five amps in a "
                            "square millimetre comes to 0.37 mm/s — an electron takes the best part of an "
                            "hour to cross a "
                            "metre of cable. What travels quickly is the field, which is set up along the "
                            "whole wire in the time light takes to get there, and starts every electron moving "
                            "almost at once. The electrons are also moving *fast* between collisions, at around "
                            "$10^{6}$ m/s, but in random directions; the drift is the small bias on top of that."
                        ),
                    },
                    {
                        "q": "You double the current through a track. What happens to the heat it produces?",
                        "opts": ["It doubles", "It quadruples", "It is unchanged", "It halves"],
                        "a": 1,
                        "why": (
                            "$P = I^2R$, so twice the current is four times the power. Both factors are "
                            "physical: twice as much charge passes, and each coulomb falls through twice the "
                            "voltage, because the drop across a fixed resistance has doubled too. This square "
                            "law is why current ratings are so much less forgiving than voltage ratings."
                        ),
                    },
                    {
                        "q": "A conductor carrying a steady current has a field inside it — which seems to contradict the rule that a conductor has no internal field. Which statement resolves it?",
                        "opts": [
                            "There is genuinely no field; the current flows for no reason",
                            "The rule is about a conductor in equilibrium; a current is charge that has not finished moving, and it is sustained by a field $E = \\rho J$ along the wire",
                            "The internal field exists but points across the wire, not along it",
                            "The rule only applies to insulators",
                        ],
                        "a": 1,
                        "why": (
                            "The zero-field rule was derived from the assumption that nothing is moving. A "
                            "current is precisely the case where charges keep moving, and what keeps them "
                            "moving is a field along the wire of size $\\rho J$ — tiny in copper, which is why "
                            "we cheerfully treat wires as equipotentials, but not zero. Multiply it by the "
                            "length and you get $IR$, the voltage across the wire."
                        ),
                    },
                    {
                        "q": "A copper motor winding measures 20.0 Ω cold, at 20 °C. In service it reads 23.1 Ω. Roughly how hot is it?",
                        "opts": ["About 25 °C", "About 60 °C", "About 40 °C", "About 100 °C"],
                        "a": 1,
                        "why": (
                            "The resistance has risen by 15.5%, and copper changes by 0.393% per kelvin, so the "
                            "winding is $0.155/0.00393 \\approx 39$ K above the 20 °C it was measured at — "
                            "call it 59 °C. This is not a trick: measuring the resistance of a winding is the "
                            "standard way of finding its average temperature, because you cannot get a probe "
                            "into the middle of it."
                        ),
                    },
                ],
            },
            "build": {
                "title": "A sense resistor that does not spoil what it measures",
                "minutes": 22,
                "brief": r'''
Measuring a current means turning it into a voltage, and the only honest way to do that
is to make it flow through a known resistance and read the drop. The canvas opens with
a 5 V rail feeding a 4.7 Ω load, with the bottom of the load wired straight to ground
and a probe on that junction — which currently reads nothing at all, because there is
nothing between it and ground.

Cut that return path and put a **sense resistor** in it, so the probe reads the voltage
across the sense resistor and nothing else. Then choose its value, against two
requirements that pull in opposite directions:

- the amplifier that follows needs at least **90 mV** to work with, so the resistor
  cannot be too small;
- the load must keep at least **4.875 V** of the 5 V rail — the sense resistor is not
  allowed to steal more than 2.5% of the supply — so it cannot be too large.

Values are typed in engineering notation: `100m` is a hundred milliohms.

The third check measures the reading at 100 kHz and compares it with DC. A real shunt
has a little inductance in it, and the fast currents you most want to see are exactly
the ones that inductance lies about; here it is a way of insisting that what you put in
the return path is a resistance and nothing else.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4.7},
                        {"id": "p2", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p3", "kind": "GND", "x": 9, "y": 13, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "OUT", "x": 12, "y": 9, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [9, 9], "b": [9, 13]},
                        {"a": [9, 9], "b": [12, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4.7},
                        {"id": "p2", "kind": "R", "x": 9, "y": 10, "rot": 1, "value": 0.1},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 13, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "OUT", "x": 12, "y": 9, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [9, 11], "b": [9, 13]},
                        {"a": [9, 9], "b": [12, 9]},
                    ],
                },
                "checks": [
                    {"name": "the sense resistor gives the amplifier something to read", "code": r'''
var v = c.vout();
c.assert(v >= 0.090, "the probe reads " + c.fmt(v, "V") + " across the sense resistor, and the " +
  "amplifier after it needs at least 90 mV");
'''},
                    {"name": "the load still gets its share of the rail", "code": r'''
var load = 5.0 - c.vout();
c.assert(load >= 4.875, "the load is left with " + c.fmt(load, "V") + " of the 5 V rail — the " +
  "sense resistor is taking more than the 2.5% it is allowed");
'''},
                    {"name": "what is in the return path is a resistance and nothing else", "code": r'''
var lo = c.gain(1), hi = c.gain(1e5);
c.close(hi / lo, 1.0, 0.02, "the reading at 100 kHz relative to the reading at DC");
'''},
                ],
                "hints": [
                    "Delete the wire running from the bottom of the load down to the ground symbol, drop a resistor into the gap, and rejoin both ends. The probe stays where it is, on the junction between the load and the new resistor.",
                    "Work the two requirements into a range before choosing anything. The load current is roughly $5/4.7 \\approx 1.06$ A, so 90 mV needs about 86 mΩ and a 125 mV budget allows about 120 mΩ.",
                    "`100m` types a hundred milliohms, and the two ways of getting it wrong look quite different. If the load check fails with the load down near 4.1 V, the sense resistor is at 1 Ω. If the load is down at a few tens of millivolts instead, it is still at the editor's 1 kΩ default and the prefix never took.",
                    "The 100 kHz check has nothing to do with the value you chose — it passes for any resistor. It fails if you reached for a capacitor or an inductor to satisfy one of the other two.",
                ],
            },
            "numeric": {
                "title": "How fast is an electron actually going?",
                "minutes": 7,
                "brief": r'''
Every intuition about current is built on water in pipes, and this is the number that
breaks it. Copper has roughly one free electron per atom, which is an enormous carrier
density, and an enormous carrier density means an ordinary current needs almost no
speed at all.
''',
                "prompt": "What is the drift velocity of the electrons, in millimetres per second?",
                "figure": r'''
```text
   a copper conductor of cross-section 1.0 mm², carrying 5.0 A

         +---------------------------------------------+
  5 A -> |    n = 8.5 x 10^28 free electrons per m^3    | -> 5 A
         +---------------------------------------------+

   A = 1.0 mm^2 = 1.0 x 10^-6 m^2        q = 1.602 x 10^-19 C
```
''',
                "given": [
                    {"label": "Current", "value": "5.0 A"},
                    {"label": "Cross-section", "value": "1.0 mm²"},
                    {"label": "Carrier density", "value": "8.5 × 10²⁸ m⁻³"},
                    {"label": "Charge per electron", "value": "1.602 × 10⁻¹⁹ C"},
                ],
                "note": "Answer in mm/s, to three figures.",
                "aside": "Count the charge that crosses one cross-section per second: it is the charge in a "
                         "slab of wire one drift-length long, which is $n A v_d q$ coulombs.",
                "answer": 0.367,
                "tol": 0.01,
                "unit": "mm/s",
                "hint": "Rearrange $I = nAqv_d$ for $v_d$. Everything is already in SI units except the answer, "
                        "which is asked for in mm/s — so multiply the metres per second by 1000 at the end.",
                "wrong": "Check the powers of ten. $nA$ is $8.5\\times10^{28} \\times 1.0\\times10^{-6} = "
                         "8.5\\times10^{22}$ carriers per metre of wire, and multiplying that by the electronic "
                         "charge gives about $1.36\\times10^{4}$ coulombs per metre.",
                "why": "$v_d = I/(nAq) = 5.0/(8.5\\times10^{28} \\times 1.0\\times10^{-6} \\times "
                       "1.602\\times10^{-19}) = 3.67\\times10^{-4}$ m/s, which is 0.367 mm/s. An electron that "
                       "sets off from the battery when you close the switch arrives a metre down the cable "
                       "about three quarters of an hour later. Nothing about the lamp lighting instantly "
                       "required it to get there: the field that pushes the electrons already in the filament "
                       "was established in nanoseconds.",
            },
            "lab": {
                "title": "A resistor, from its dimensions",
                "runtime": "python",
                "minutes": 24,
                "brief": r'''
Four functions. The first is the resistive twin of `plate_capacitance` from module 3 —
a material constant times a geometry — and the rest are what you do with it.

`track_resistance(rho, length, width, thickness)` returns the resistance in ohms of a
rectangular conductor of that resistivity and those dimensions, all in metres. The
cross-section is `width * thickness`.

`drift_velocity(current, area, carriers_per_m3)` returns the drift speed in metres per
second, from $I = nAqv_d$. `ELEMENTARY_CHARGE` is defined for you.

`power_lost(current, resistance)` returns the watts turned into heat.

`resistance_at(r20, temp_c, alpha)` returns what a resistance measured as `r20` at
20 °C becomes at `temp_c`, using the linear law $R = R_{20}(1 + \alpha(T - 20))$ with
`alpha` in per-kelvin. The default is copper's 0.00393.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

RHO_COPPER = 1.68e-8            # resistivity of copper at 20 C, in ohm metres
ELEMENTARY_CHARGE = 1.602176634e-19


def track_resistance(rho, length, width, thickness):
    """Resistance in ohms of a rectangular conductor, all dimensions in metres."""
    # TODO: rho * length / cross-sectional area.
    return 0.0


def drift_velocity(current, area, carriers_per_m3):
    """Drift speed in m/s of the carriers in a conductor of that cross-section."""
    # TODO: invert I = n A q v.
    return 0.0


def power_lost(current, resistance):
    """Heat produced, in watts."""
    # TODO
    return 0.0


def resistance_at(r20, temp_c, alpha=0.00393):
    """A resistance measured at 20 C, corrected to temp_c."""
    # TODO: R20 * (1 + alpha * (T - 20)).
    return 0.0


if __name__ == "__main__":
    r = track_resistance(RHO_COPPER, 0.120, 2.0e-3, 35e-6)
    print("120 mm of 2 mm wide, 35 um thick copper:", r, "ohm")
    print("carrying 3 A, it drops", 3.0 * r, "V and dissipates", power_lost(3.0, r), "W")
    print("5 A in 1 mm^2 drifts at",
          drift_velocity(5.0, 1.0e-6, 8.5e28), "m/s")
    print("a 20 ohm winding at 60 C reads", resistance_at(20.0, 60.0), "ohm")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

RHO_COPPER = 1.68e-8            # resistivity of copper at 20 C, in ohm metres
ELEMENTARY_CHARGE = 1.602176634e-19


def track_resistance(rho, length, width, thickness):
    """Resistance in ohms of a rectangular conductor, all dimensions in metres."""
    return float(rho * length / (width * thickness))


def drift_velocity(current, area, carriers_per_m3):
    """Drift speed in m/s of the carriers in a conductor of that cross-section."""
    return float(current / (carriers_per_m3 * area * ELEMENTARY_CHARGE))


def power_lost(current, resistance):
    """Heat produced, in watts."""
    return float(current * current * resistance)


def resistance_at(r20, temp_c, alpha=0.00393):
    """A resistance measured at 20 C, corrected to temp_c."""
    return float(r20 * (1.0 + alpha * (temp_c - 20.0)))


if __name__ == "__main__":
    r = track_resistance(RHO_COPPER, 0.120, 2.0e-3, 35e-6)
    print("120 mm of 2 mm wide, 35 um thick copper:", r, "ohm")
    print("carrying 3 A, it drops", 3.0 * r, "V and dissipates", power_lost(3.0, r), "W")
    print("5 A in 1 mm^2 drifts at",
          drift_velocity(5.0, 1.0e-6, 8.5e28), "m/s")
    print("a 20 ohm winding at 60 C reads", resistance_at(20.0, 60.0), "ohm")
'''}],
                "hints": [
                    "`track_resistance` is one expression, and the only trap is the area: `width * thickness`, both in metres, so 35 µm is `35e-6` and not `35`.",
                    "`drift_velocity` divides by the product of three things. If your answer comes out enormous, check that the carrier density is multiplying rather than dividing.",
                    "`power_lost` squares the current. `current * resistance` is the voltage across it, not the power.",
                    "`resistance_at` must return exactly `r20` when `temp_c` is 20, which is a quick way to check the sign of the bracket.",
                ],
                "tests": [
                    {"name": "a length of ordinary printed-circuit copper", "code": r'''
_r = track_resistance(1.68e-8, 0.120, 2.0e-3, 35e-6)
assert abs(_r - 0.028800000000000006) < 1e-12, \
    f"120 mm of 2 mm wide, 35 um copper is 28.8 mohm, got {_r!r}"
'''},
                    {"name": "resistance goes up with length and down with area", "code": r'''
_base = track_resistance(1.68e-8, 0.120, 2.0e-3, 35e-6)
_wide = track_resistance(1.68e-8, 0.120, 4.0e-3, 35e-6)
_long = track_resistance(1.68e-8, 0.240, 2.0e-3, 35e-6)
assert abs(_wide - 0.014400000000000003) < 1e-12, \
    f"doubling the width should halve the resistance, got {_wide!r}"
assert abs(_long - 2.0 * _base) < 1e-15, "doubling the length should double the resistance"
_thick = track_resistance(1.68e-8, 0.120, 2.0e-3, 70e-6)
assert abs(_thick - _wide) < 1e-15, \
    "width and thickness enter only as their product, so doubling either does the same thing"
'''},
                    {"name": "the electrons crawl", "code": r'''
_v = drift_velocity(5.0, 1.0e-6, 8.5e28)
assert abs(_v - 0.000367147592615339) < 1e-15, \
    f"5 A in 1 mm^2 of copper drifts at 0.367 mm/s, got {_v!r} m/s"
_fat = drift_velocity(5.0, 2.0e-6, 8.5e28)
assert abs(_fat - _v / 2.0) < 1e-18, \
    "the same current in twice the area needs half the speed"
_semi = drift_velocity(5.0, 1.0e-6, 8.5e22)
assert _semi > 100.0 * _v, \
    "a material with a million times fewer carriers needs a far faster drift for the same current"
'''},
                    {"name": "heat goes as the square of the current", "code": r'''
_r = track_resistance(1.68e-8, 0.120, 2.0e-3, 35e-6)
_p = power_lost(3.0, _r)
assert abs(_p - 0.25920000000000004) < 1e-12, \
    f"3 A through 28.8 mohm is 259 mW, got {_p!r}"
assert abs(power_lost(6.0, _r) - 4.0 * _p) < 1e-12, \
    "doubling the current should quadruple the heat"
'''},
                    {"name": "a copper winding is its own thermometer", "code": r'''
assert abs(resistance_at(20.0, 20.0) - 20.0) < 1e-12, \
    "at 20 C the correction must do nothing at all"
_hot = resistance_at(20.0, 60.0)
assert abs(_hot - 23.144) < 1e-9, \
    f"20 ohm of copper at 60 C reads 23.144 ohm, got {_hot!r}"
_alu = resistance_at(20.0, 60.0, 0.00403)
assert _alu > _hot, "aluminium has the larger temperature coefficient, so it should rise further"
'''},
                    {"name": "the track from the schematic exercise, end to end", "code": r'''
_r = track_resistance(1.68e-8, 0.120, 2.0e-3, 35e-6)
_drop = 3.0 * _r
assert abs(_drop - 0.08640000000000002) < 1e-12, \
    f"at 3 A that track drops 86.4 mV, got {_drop!r} V"
_hot = resistance_at(_r, 85.0)
assert _hot > _r, "the track gets hotter and therefore worse"
assert abs(_hot - 0.03615696000000001) < 1e-9, \
    f"at 85 C the same track is 36.2 mohm, got {_hot!r}"
'''},
                ],
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "The force on a moving charge, and the current loop",
            "summary": "A magnetic field never pushes a charge forwards. It pushes it sideways, and motors, mass spectrometers and the Hall probe are all that one fact used differently.",
            "concepts": [
                "$\\mathbf{F} = q\\mathbf{v}\\times\\mathbf{B}$: the magnitude is $qvB\\sin\\theta$ and the direction is perpendicular to both $\\mathbf{v}$ and $\\mathbf{B}$. A charge at rest feels nothing, and a charge moving straight along the field feels nothing either — which is why the magnetic force is so easy to overlook and so hard to reason about by analogy with the electric one.",
                "Because that force is always at right angles to the velocity, it does no work: a magnetic field can change where a charge is going but never how fast. The energy a motor delivers comes from the electric field driving the current round the loop; the magnetic field only decides which way the push points.",
                "A charge fired across a uniform field goes in a circle: $qvB = mv^2/r$ gives a radius $r = mv/(qB)$, and a period $T = 2\\pi m/(qB)$ that contains no $v$ at all. Faster particles run bigger circles in the same time, which is the whole design principle of a cyclotron.",
                "A current is moving charge, so a wire of length $L$ in the field feels $F = BIL\\sin\\theta$. A flat coil of $N$ turns and area $A$ feels no net force in a uniform field but does feel a torque $\\tau = NIAB\\sin\\theta$. Write $m = NIA$ for the magnetic moment and it reads $\\tau = mB\\sin\\theta$ — the same expression that turns a compass needle.",
                "The Hall effect is this force acting on the carriers *inside* a conductor. They pile up on one edge until the transverse electric field they build balances the magnetic push, leaving a steady voltage $V_H = IB/(nqt)$ across the strip. It measures the field, it measures the carrier density, and the sign of it tells you the sign of the carriers — which is how it was discovered that in some materials the moving charge is effectively positive.",
            ],
            "sandbox": {
                "title": "A charge in a magnetic field, drawn in velocity space",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "initial": {"a11": 0, "a12": 1, "a21": -1, "a22": 0},
                "brief": r'''
The same panel as modules 1 and 2, reading two different axes. Take the horizontal axis
as $v_x$ and the vertical as $v_y$: each point is a possible *velocity*, and a curve is
the history of one particle's velocity as the field acts on it.

For a charge in a uniform field pointing out of the page, $m\,\mathrm{d}\mathbf{v}/
\mathrm{d}t = q\mathbf{v}\times\mathbf{B}$ works out as

$$\dot{v_x} = \omega v_y, \qquad \dot{v_y} = -\omega v_x, \qquad \omega = \frac{qB}{m}$$

which is exactly what these four sliders describe, with $a_{12} = \omega$ and
$a_{21} = -\omega$. The opening values are $\omega = 1$.

One thing to keep hold of: the distance of a point from the centre of this picture is
the particle's **speed**. So a curve that stays at a fixed distance is a particle whose
speed is not changing.
''',
                "notice": [
                    "As it opens, the readout says trace = 0.00, det = 1.00 and calls the pattern a *centre*. Every trajectory closes on itself at a fixed distance from the middle: the direction of the velocity goes round and round, the speed never moves. That is the whole content of ‘a magnetic force does no work’, drawn. (The rings creep outward by about a tenth of their radius over the interval sketched, which is the forward-Euler step in the drawing code and not the physics — the same artefact module 1 pointed out.)",
                    "Look at the short strokes rather than the curves. At every grid point the stroke is at right angles to the line joining that point to the centre — which is to say the force is always perpendicular to the velocity. Nothing else in this course behaves like that; an electric field points along the line to the charge that made it.",
                    "Set $a_{12} = -1$ and $a_{21} = 1$. The readout is unchanged — trace 0.00, det 1.00, still a centre — but every curve now runs the other way round. That is what reversing the sign of the charge does, and also what reversing the field does: same speed, same size of circle, opposite sense. It is why an electron and a proton entering the same field separate rather than following each other.",
                    "Put $a_{12}$ and $a_{21}$ back to $1$ and $-1$, then set $a_{11}$ and $a_{22}$ both to $-0.30$. The readout reads trace $= -0.60$, det $= 1.09$, and calls it a stable spiral: the velocity still turns, but now it decays. That is a charge colliding with the lattice, and in a real metal an electric field keeps topping the velocity back up. Where the two balance is the drift velocity of the previous module — and the fact that the turning term is *still there*, pushing the drifting carriers sideways, is the Hall effect.",
                    "Back to a clean centre, and now set $a_{12} = 0.5$ with $a_{21} = -0.5$. Trace 0.00, det 0.25: still a centre, but the curves are traced out at half the rate. Halving the field halves the cyclotron frequency. Note what has *not* changed — the size of the orbits in this picture, because the speed was never the field's to alter. In real space the circle has doubled in radius, since $r = v/\\omega$.",
                ],
            },
            "quiz": {
                "title": "The magnetic force, checked",
                "minutes": 9,
                "questions": [
                    {
                        "q": "An electron travels exactly parallel to a strong uniform magnetic field. What magnetic force does it feel?",
                        "opts": [
                            "A large force, along the field",
                            "None",
                            "A force perpendicular to the field, proportional to its speed",
                            "A force opposing its motion",
                        ],
                        "a": 1,
                        "why": (
                            "The magnitude is $qvB\\sin\\theta$ and $\\theta$ is zero here, so the force is zero "
                            "no matter how fast the electron goes or how strong the field is. Only the "
                            "component of velocity *across* the field produces any force at all, which is why "
                            "a charge released at a general angle spirals: the along-field part sails on "
                            "untouched while the across-field part goes in a circle."
                        ),
                    },
                    {
                        "q": "A proton is fired into a uniform magnetic field at right angles to it. What is its speed after a quarter of a turn?",
                        "opts": [
                            "Higher, because the field accelerated it",
                            "Lower, because it lost energy turning",
                            "Exactly what it was",
                            "Zero, because it is at the top of the circle",
                        ],
                        "a": 2,
                        "why": (
                            "Work is force times distance *along the direction of motion*, and the magnetic "
                            "force is always at right angles to the motion, so it does no work at all: the "
                            "kinetic energy, and therefore the speed, cannot change. The proton is certainly "
                            "accelerating, in the sense that its velocity is changing direction — acceleration "
                            "and speeding up are not the same thing."
                        ),
                    },
                    {
                        "q": "You double the speed of a charged particle circling in a fixed magnetic field. What happens to the radius of its path and to the time it takes to go round?",
                        "opts": [
                            "Both double",
                            "The radius doubles; the period is unchanged",
                            "The radius is unchanged; the period halves",
                            "The radius halves; the period doubles",
                        ],
                        "a": 1,
                        "why": (
                            "$r = mv/(qB)$ is proportional to the speed, so the circle doubles. But "
                            "$T = 2\\pi m/(qB)$ has no $v$ in it: the particle has twice as far to go and is "
                            "going twice as fast, and the two cancel exactly. That cancellation is not a "
                            "coincidence of algebra — it is what makes a fixed-frequency accelerator possible."
                        ),
                    },
                    {
                        "q": "A rectangular current loop sits in a uniform magnetic field. In which orientation is the torque on it zero?",
                        "opts": [
                            "When the plane of the loop contains the field direction",
                            "When the field is perpendicular to the plane of the loop, so the flux through it is greatest",
                            "When the loop is at 45° to the field",
                            "The torque is never zero while current flows",
                        ],
                        "a": 1,
                        "why": (
                            "The torque is $mB\\sin\\theta$ with $\\theta$ measured between the magnetic moment "
                            "— which points along the loop's normal — and the field. It vanishes when the "
                            "moment lines up with the field, which is when the field is normal to the loop and "
                            "the flux through it is at its maximum. That is the position the loop turns "
                            "towards, and a DC motor exists to reverse the current just before it gets there, "
                            "so the torque never runs out."
                        ),
                    },
                    {
                        "q": "You measure the Hall voltage across a strip of an unfamiliar material and find its sign is the opposite of what copper gives. What does that tell you?",
                        "opts": [
                            "The magnetic field was applied backwards",
                            "The charge carriers behave as though they are positive",
                            "The material has no free carriers",
                            "The measurement is faulty; the Hall voltage has only one sign",
                        ],
                        "a": 1,
                        "why": (
                            "Reverse the sign of the carriers and they pile up on the opposite edge for the "
                            "same current and the same field, so the Hall voltage flips. This is the one "
                            "measurement that distinguishes charge flowing one way from the opposite charge "
                            "flowing the other way — the current is identical, and everything else about the "
                            "conductor is blind to the difference. It is how p-type semiconductors were "
                            "identified."
                        ),
                    },
                    {
                        "q": "In a cyclotron a particle is given a small push twice per revolution by a voltage that reverses at a fixed frequency. Why does a fixed frequency go on working as the particle speeds up?",
                        "opts": [
                            "Because the speed does not actually increase",
                            "Because the period $2\\pi m/(qB)$ does not depend on the speed, so a faster particle simply runs a larger circle in the same time",
                            "Because the magnetic field is raised in step with the speed",
                            "It does not — the drive frequency has to be swept from the very start",
                        ],
                        "a": 1,
                        "why": (
                            "Everything in $T = 2\\pi m/(qB)$ is a constant of the particle or the machine, so "
                            "the revolutions stay in step with a fixed drive while the orbit spirals outward. "
                            "It stops working eventually, and for a reason worth knowing: as the speed "
                            "approaches that of light the effective mass rises, the period lengthens, and the "
                            "particle falls out of step. Machines that push past that point sweep the "
                            "frequency, and are called synchrocyclotrons for exactly that reason."
                        ),
                    },
                ],
            },
            "derive": {
                "title": "The radius and the period of a circling charge",
                "minutes": 11,
                "vars": ["q", "v", "B", "m", "r", "T"],
                "brief": r'''
A particle of charge $q$ and mass $m$ enters a uniform field $B$ at speed $v$, moving at
right angles to the field. It goes in a circle. Four steps get you the radius and the
time it takes to go round, and the second of those is worth the trip on its own.
''',
                "steps": [
                    {
                        "prompt": "Write the magnitude of the magnetic force on the particle. It is moving at right angles to the field, so the angle factor is 1.",
                        "answer": "q v B",
                        "hint": "The general form is $qvB\\sin\\theta$, and $\\sin 90° = 1$.",
                        "deconstruct": [
                            "The force is $q\\mathbf{v}\\times\\mathbf{B}$.",
                            "At right angles the cross product has magnitude $vB$.",
                        ],
                    },
                    {
                        "prompt": "Anything going round a circle of radius $r$ at speed $v$ needs a force towards the centre. Write that centripetal force in terms of $m$, $v$ and $r$.",
                        "answer": "\\frac{m v^2}{r}",
                        "hint": "Mass times centripetal acceleration, and the acceleration is $v^2/r$.",
                        "deconstruct": [
                            "Centripetal acceleration is $v^2/r$.",
                            "Newton's second law multiplies it by the mass.",
                        ],
                    },
                    {
                        "prompt": "The magnetic force is the only one acting, so it *is* the centripetal force. Equate the two expressions and solve for $r$.",
                        "answer": "\\frac{m v}{q B}",
                        "hint": "Set $qvB = mv^2/r$, multiply both sides by $r$, then divide by $qvB$. One power of $v$ cancels.",
                        "deconstruct": [
                            "$qvB = mv^2/r$ rearranges to $r = mv^2/(qvB)$.",
                            "Cancel the common $v$.",
                        ],
                    },
                    {
                        "prompt": "One lap is a distance $2\\pi r$ at speed $v$. Write the period $T$, substituting the radius you just found.",
                        "answer": "\\frac{2 \\pi m}{q B}",
                        "placeholder": "something over q B",
                        "hint": "$T = 2\\pi r / v$. Put your expression for $r$ in and see which symbol disappears.",
                        "deconstruct": [
                            "$T = 2\\pi r/v$ with $r = mv/(qB)$ gives $T = 2\\pi mv/(qBv)$.",
                            "The $v$ cancels top and bottom.",
                        ],
                    },
                ],
                "closing": r'''
The speed has gone. Two particles of the same charge and mass entering the same field at
wildly different speeds go round wildly different circles in precisely the same time, and
that is why a fixed radio frequency can accelerate a whole bunch of them at once.

The two results are also a measuring instrument in disguise. Fix $B$ and measure $r$ for
a beam accelerated through a known voltage, and you have $m/q$ — which is what a mass
spectrometer reports, and how the electron's charge-to-mass ratio was first pinned down.
''',
            },
            "lab": {
                "title": "Cross products, circles and a Hall probe",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
Five functions. The first is the only one where the vectors matter; the rest are the
scalar results that fall out of it.

`lorentz_force(q, v, B)` returns the force in newtons as a three-element NumPy array,
$q\,\mathbf{v}\times\mathbf{B}$. `np.cross` does the cross product; the job is to get the
order right, because $\mathbf{B}\times\mathbf{v}$ is the same size and the wrong sign.

`cyclotron_radius(mass, speed, charge, b_field)` and `cyclotron_period(mass, charge,
b_field)` are the two results you just derived.

`hall_voltage(current, b_field, carriers_per_m3, thickness)` returns $IB/(nqt)$ in volts,
where `thickness` is the dimension of the strip measured along the field.

`loop_torque(turns, current, area, b_field, angle_rad)` returns $NIAB\sin\theta$, with the
angle measured between the loop's normal and the field.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

ELEMENTARY_CHARGE = 1.602176634e-19   # C
ELECTRON_MASS = 9.1093837015e-31      # kg
PROTON_MASS = 1.67262192369e-27       # kg


def lorentz_force(q, v, B):
    """Magnetic force in newtons on a charge q moving at v through field B."""
    v = np.asarray(v, dtype=float)
    B = np.asarray(B, dtype=float)
    # TODO: q times the cross product, in the right order.
    return np.zeros(3)


def cyclotron_radius(mass, speed, charge, b_field):
    """Radius in metres of the circular path."""
    # TODO
    return 0.0


def cyclotron_period(mass, charge, b_field):
    """Seconds for one complete revolution."""
    # TODO: no speed appears in this one.
    return 0.0


def hall_voltage(current, b_field, carriers_per_m3, thickness):
    """Hall voltage in volts across a strip of that thickness."""
    # TODO
    return 0.0


def loop_torque(turns, current, area, b_field, angle_rad):
    """Torque in newton metres on a flat coil in a uniform field."""
    # TODO
    return 0.0


if __name__ == "__main__":
    print("force on an electron at 1e6 m/s across 0.5 T:",
          lorentz_force(-ELEMENTARY_CHARGE, [1e6, 0.0, 0.0], [0.0, 0.0, 0.5]))
    print("its orbit radius:",
          cyclotron_radius(ELECTRON_MASS, 1e6, ELEMENTARY_CHARGE, 0.5), "m")
    print("its period:", cyclotron_period(ELECTRON_MASS, ELEMENTARY_CHARGE, 0.5), "s")
    print("Hall voltage, copper foil 0.1 mm thick, 1 A, 0.5 T:",
          hall_voltage(1.0, 0.5, 8.5e28, 1e-4), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

ELEMENTARY_CHARGE = 1.602176634e-19   # C
ELECTRON_MASS = 9.1093837015e-31      # kg
PROTON_MASS = 1.67262192369e-27       # kg


def lorentz_force(q, v, B):
    """Magnetic force in newtons on a charge q moving at v through field B."""
    v = np.asarray(v, dtype=float)
    B = np.asarray(B, dtype=float)
    return q * np.cross(v, B)


def cyclotron_radius(mass, speed, charge, b_field):
    """Radius in metres of the circular path."""
    return float(mass * speed / (charge * b_field))


def cyclotron_period(mass, charge, b_field):
    """Seconds for one complete revolution."""
    return float(2.0 * np.pi * mass / (charge * b_field))


def hall_voltage(current, b_field, carriers_per_m3, thickness):
    """Hall voltage in volts across a strip of that thickness."""
    return float(current * b_field
                 / (carriers_per_m3 * ELEMENTARY_CHARGE * thickness))


def loop_torque(turns, current, area, b_field, angle_rad):
    """Torque in newton metres on a flat coil in a uniform field."""
    return float(turns * current * area * b_field * np.sin(angle_rad))


if __name__ == "__main__":
    print("force on an electron at 1e6 m/s across 0.5 T:",
          lorentz_force(-ELEMENTARY_CHARGE, [1e6, 0.0, 0.0], [0.0, 0.0, 0.5]))
    print("its orbit radius:",
          cyclotron_radius(ELECTRON_MASS, 1e6, ELEMENTARY_CHARGE, 0.5), "m")
    print("its period:", cyclotron_period(ELECTRON_MASS, ELEMENTARY_CHARGE, 0.5), "s")
    print("Hall voltage, copper foil 0.1 mm thick, 1 A, 0.5 T:",
          hall_voltage(1.0, 0.5, 8.5e28, 1e-4), "V")
'''}],
                "hints": [
                    "`np.cross(v, B)` and then multiply by `q`. Writing `np.cross(B, v)` gives every component the wrong sign, and no test of magnitude alone would catch it.",
                    "`cyclotron_radius` is $mv/(qB)$ and `cyclotron_period` is $2\\pi m/(qB)$ — note that the speed appears in one and not the other.",
                    "In `hall_voltage` the electronic charge is the module-level constant, not an argument. Watch the thickness: it divides, so a thinner strip gives a bigger reading.",
                    "`np.sin` takes radians, and the argument is already in radians.",
                ],
                "tests": [
                    {"name": "the cross product points the right way", "code": r'''
import numpy as np
_F = np.asarray(lorentz_force(1.602176634e-19, [1e6, 0.0, 0.0], [0.0, 0.0, 0.5]), dtype=float)
assert _F.shape == (3,), f"lorentz_force should return three components, got shape {_F.shape}"
assert abs(_F[0]) < 1e-24 and abs(_F[2]) < 1e-24, \
    f"a velocity along x crossed with a field along z leaves only a y component, got {_F.tolist()}"
assert _F[1] < 0, "x cross z points along minus y, so a positive charge is pushed that way"
assert abs(_F[1] + 8.010883169999999e-14) < 1e-26, \
    f"expected -8.0109e-14 N along y, got {_F[1]!r}"
'''},
                    {"name": "reversing the charge reverses the force", "code": r'''
import numpy as np
_p = np.asarray(lorentz_force(1.602176634e-19, [1e6, 0.0, 0.0], [0.0, 0.0, 0.5]), dtype=float)
_e = np.asarray(lorentz_force(-1.602176634e-19, [1e6, 0.0, 0.0], [0.0, 0.0, 0.5]), dtype=float)
assert float(np.max(np.abs(_p))) > 1e-20, \
    f"there should be a force here at all, and it comes to 8.0e-14 N; got {_p.tolist()}"
assert float(np.max(np.abs(_p + _e))) < 1e-26, \
    "the same motion with the opposite charge must give exactly the opposite force"
'''},
                    {"name": "motion along the field produces nothing", "code": r'''
import numpy as np
_along = np.asarray(lorentz_force(1.602176634e-19, [0.0, 0.0, 3e6], [0.0, 0.0, 0.5]), dtype=float)
assert float(np.max(np.abs(_along))) < 1e-30, \
    f"a charge moving along the field feels no force at all, got {_along.tolist()}"
_across = np.asarray(lorentz_force(1.602176634e-19, [0.0, 3e6, 0.0], [0.0, 0.0, 0.5]), dtype=float)
assert abs(_across[0] - 2.403264951e-13) < 1e-25, \
    f"the same speed across the field gives 2.403e-13 N along x, got {_across.tolist()}"
'''},
                    {"name": "an electron's orbit in half a tesla", "code": r'''
_r = cyclotron_radius(9.1093837015e-31, 1e6, 1.602176634e-19, 0.5)
assert abs(_r - 1.1371260207131446e-05) < 1e-17, \
    f"expected 11.4 um, got {_r!r} m"
_fast = cyclotron_radius(9.1093837015e-31, 2e6, 1.602176634e-19, 0.5)
assert abs(_fast - 2.0 * _r) < 1e-17, "twice the speed is twice the radius"
_strong = cyclotron_radius(9.1093837015e-31, 1e6, 1.602176634e-19, 1.0)
assert abs(_strong - _r / 2.0) < 1e-17, "twice the field is half the radius"
'''},
                    {"name": "the period does not know about the speed", "code": r'''
_T = cyclotron_period(9.1093837015e-31, 1.602176634e-19, 0.5)
assert abs(_T - 7.14477350575642e-11) < 1e-23, \
    f"an electron in 0.5 T goes round in 71.4 ps, got {_T!r} s"
_p = cyclotron_period(1.67262192369e-27, 1.602176634e-19, 0.8)
assert abs(_p - 8.199309358573712e-08) < 1e-20, \
    f"a proton in 0.8 T takes 82.0 ns, got {_p!r} s"
assert _p > 1000.0 * _T, "the proton is far heavier, so its orbit is far slower"
'''},
                    {"name": "the two cyclotron results agree with each other", "code": r'''
import numpy as np
_m, _q, _B, _v = 1.67262192369e-27, 1.602176634e-19, 0.8, 2e6
_r = cyclotron_radius(_m, _v, _q, _B)
_T = cyclotron_period(_m, _q, _B)
assert abs(_r - 0.02609921228713288) < 1e-14, f"expected a 2.61 cm circle, got {_r!r} m"
assert abs(2.0 * np.pi * _r / _v - _T) < 1e-18, \
    "one circumference at that speed must take exactly one period"
'''},
                    {"name": "a Hall probe, and why it is made thin", "code": r'''
_cu = hall_voltage(1.0, 0.5, 8.5e28, 1e-4)
assert abs(_cu - 3.67147592615339e-07) < 1e-18, \
    f"copper gives a useless 0.367 uV here, got {_cu!r} V"
_semi = hall_voltage(1e-3, 0.5, 1e22, 1e-4)
assert abs(_semi - 0.0031207545372303816) < 1e-14, \
    f"a semiconductor with a millionth of the carriers gives 3.12 mV on a thousandth of the current, got {_semi!r} V"
assert abs(hall_voltage(1.0, 0.5, 8.5e28, 5e-5) - 2.0 * _cu) < 1e-18, \
    "halving the thickness doubles the reading"
'''},
                    {"name": "the torque on a coil, and where it vanishes", "code": r'''
import numpy as np
_t = loop_torque(200, 0.5, 4e-4, 0.3, np.pi / 2)
assert abs(_t - 0.012) < 1e-12, f"expected 12 mN m at right angles, got {_t!r}"
assert abs(loop_torque(200, 0.5, 4e-4, 0.3, 0.0)) < 1e-15, \
    "with the normal along the field there is no torque left"
assert abs(loop_torque(200, 0.5, 4e-4, 0.3, np.pi / 6) - 0.006) < 1e-12, \
    "at 30 degrees the torque is half its maximum"
assert abs(loop_torque(400, 0.5, 4e-4, 0.3, np.pi / 2) - 2.0 * _t) < 1e-12, \
    "twice the turns is twice the torque - and unlike inductance, it is not squared"
'''},
                ],
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Magnetic materials, saturation and the magnetic circuit",
            "summary": "Iron multiplies a coil's field by thousands, up to a hard ceiling — and once you accept the ceiling, designing an inductor becomes a circuit problem with a resistor analogy.",
            "concepts": [
                "Two fields, not one. $H = NI/\\ell$ is what the winding *imposes*, in amps per metre, and it depends only on the current and the geometry. $B = \\mu_0\\mu_r H$ is what the material *delivers*. In vacuum $\\mu_r = 1$; in silicon steel it is a few thousand, in a power ferrite one to ten thousand.",
                "The multiplication has a ceiling. The material's response comes from magnetic domains lining up, and once they all have there is nothing left to recruit: past saturation — around 1.5 to 2 T for iron, 0.3 to 0.4 T for common ferrites — extra current adds field as if the core were not there, and the inductance collapses to its air value.",
                "Ferromagnets remember. Take the current away and some flux remains; reversing it takes a coercive field to undo. Traced round a full cycle, $B$ against $H$ is a loop rather than a line, and the area inside that loop is energy turned into heat, per cycle and per cubic metre. That is why a transformer hums warm at 50 Hz and why core materials are chosen by frequency.",
                "Ampère's law round a closed core reads $NI = \\sum H\\ell$, which is Kirchhoff's voltage law wearing a hat: the magnetomotive force $NI$ plays the part of a voltage, the flux $\\Phi$ that of a current, and the reluctance $\\mathcal{R} = \\ell/(\\mu_0\\mu_r A)$ that of a resistance. Reluctances in series add, and $\\Phi = NI/\\mathcal{R}$ is Ohm's law.",
                "An air gap has $\\mu_r = 1$, so half a millimetre of it can outweigh ten centimetres of ferrite ten times over. Gapping a core throws away most of the inductance — and buys back a value fixed by a measurable length instead of by a material property that drifts with temperature, drive level and batch, and buys headroom before saturation. Nearly every power inductor is gapped for exactly those reasons.",
            ],
            "quiz": {
                "title": "Cores, gaps and saturation, checked",
                "minutes": 9,
                "questions": [
                    {
                        "q": "You wind a coil on a closed ferrite ring with $\\mu_r = 2000$, in place of an otherwise identical air-cored winding of the same turns, area and path length. What happens to the inductance, while the current stays small?",
                        "opts": [
                            "It is multiplied by about 2000",
                            "It is divided by about 2000",
                            "It is multiplied by about $\\sqrt{2000}$",
                            "It is unchanged; $\\mu_r$ affects only the field, not the inductance",
                        ],
                        "a": 0,
                        "why": (
                            "$L = \\mu_0\\mu_r N^2 A/\\ell$ carries $\\mu_r$ as a straight multiplier, so a "
                            "closed core of $\\mu_r = 2000$ gives roughly two thousand times the inductance "
                            "for the same winding. The closed path is what earns the full factor, and it is "
                            "worth knowing what happens without one: slide the same ferrite into the coil as "
                            "a *rod* and the flux has to return through air, whose reluctance then dominates "
                            "the loop. A rod five diameters long multiplies the inductance by about eighteen, "
                            "and one ten diameters long by about fifty — not by two thousand."
                        ),
                    },
                    {
                        "q": "The current in a cored inductor is raised until the core saturates. What does the inductance do?",
                        "opts": [
                            "It rises sharply",
                            "It falls sharply, towards what the same winding would have with no core at all",
                            "It stays where it was; saturation affects only the losses",
                            "It becomes negative",
                        ],
                        "a": 1,
                        "why": (
                            "Inductance is how much flux a further amp buys, and past saturation a further amp "
                            "buys only what it would in air. The failure mode is nasty because it feeds "
                            "itself: $\\mathrm{d}i/\\mathrm{d}t = v/L$, so as $L$ collapses the current rises "
                            "faster, which saturates the core harder. A switching converter whose inductor "
                            "saturates does not degrade gracefully; it destroys the transistor."
                        ),
                    },
                    {
                        "q": "A magnetic circuit has a gap whose reluctance is ten times that of the core around it. What fraction of the winding's $NI$ is spent across the gap?",
                        "opts": ["About 50%", "About 91%", "About 10%", "About 99%"],
                        "a": 1,
                        "why": (
                            "Reluctances in series carry the same flux and divide the mmf in proportion, "
                            "exactly as series resistors divide a voltage: $10/11 = 0.91$. Almost the whole "
                            "of the winding's effort is spent driving flux across half a millimetre of air, "
                            "and almost none on the ten centimetres of ferrite — which is why the gap, not "
                            "the ferrite, is what sets the inductance of a gapped part."
                        ),
                    },
                    {
                        "q": "Why is an air gap deliberately cut into the core of most power inductors?",
                        "opts": [
                            "To increase the inductance",
                            "To set the inductance by a machined length instead of by the core's permeability, and to allow more current before saturation",
                            "To let the heat escape",
                            "To reduce the resistance of the winding",
                        ],
                        "a": 1,
                        "why": (
                            "Once the gap dominates the reluctance, $L$ depends on the gap length and the core "
                            "area and hardly at all on $\\mu_r$ — which is fortunate, because $\\mu_r$ can "
                            "change by a factor of two over the temperature range a converter runs at. The "
                            "second reason is saturation: for a given current the gap holds $B$ in the core "
                            "down, so the part takes more current before the domains run out. Both benefits "
                            "are paid for in inductance, which is why the winding then needs more turns."
                        ),
                    },
                    {
                        "q": "What does the area enclosed by a material's B–H loop represent?",
                        "opts": [
                            "The energy stored in the core",
                            "The energy lost as heat, per cycle and per unit volume",
                            "The saturation flux density",
                            "The permeability",
                        ],
                        "a": 1,
                        "why": (
                            "Going once round the loop returns the material to where it started, so nothing is "
                            "left stored — yet the integral $\\oint H\\,\\mathrm{d}B$ is not zero, and what "
                            "went in came out as heat. Because it is energy *per cycle*, the power lost rises "
                            "with frequency, which is the first thing that limits how fast a magnetic "
                            "component can be driven, and why 50 Hz uses laminated steel and 500 kHz uses "
                            "ferrite."
                        ),
                    },
                    {
                        "q": "A coil is wound on a closed ferrite ring and measures 275 mH. The same coil on the same ring, now with a 0.5 mm gap cut in it, measures 25 mH. Which statement about the two parts is right?",
                        "opts": [
                            "The gapped one stores less energy before it saturates",
                            "The gapped one holds its value far better against temperature and drive, and saturates at a higher current",
                            "The gapped one has more turns",
                            "They behave identically below saturation",
                        ],
                        "a": 1,
                        "why": (
                            "The eleven-fold drop is the gap taking over the reluctance, and everything good "
                            "about the gapped part follows from that: the value now depends on a length "
                            "someone machined rather than on $\\mu_r$, and for a given current the flux "
                            "density in the core is eleven times lower, so the current can go far higher "
                            "before the domains run out. The turns did not change — that was the premise."
                        ),
                    },
                ],
            },
            "build": {
                "title": "Measuring the coil you designed, by resonating it",
                "minutes": 24,
                "brief": r'''
The core: a ferrite ring, magnetic path 100 mm, cross-section 100 mm², $\mu_r = 2000$,
with a 0.5 mm gap cut in it. Wind 331 turns and the reluctance sum in this module's
derivation gives **25 mH** — of which the gap is responsible for about ten elevenths.

Now check it. There is no instrument on this bench that reads henries directly, and the
standard way to measure an inductance has always been to resonate it against a
capacitor you already know and find the frequency where the response peaks.

Draw that measurement: the **5 V source**, the inductor and a resistor in series, and a
capacitor from the far end down to ground with the probe on it. Then choose the
capacitor and the resistor so that

- the response peaks at **1.00 kHz**, within 3%, and
- the peak is at least **five times** the source — a resonance you cannot see is a
  resonance you cannot measure.

The canvas opens with the resistor and capacitor wired as a plain RC, and no inductor.

Type inductances as `25m` and capacitances as `1u`.

Only the product $LC$ fixes the frequency, so the checks will accept any pair that
resonates in the right place — they measure the circuit rather than compare it with a
drawing. What the resistor decides on its own is how sharp the peak is: it is the
damping, and too much of it flattens the very thing you are trying to find.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "R", "x": 10, "y": 4, "rot": 0, "value": 22},
                        {"id": "p2", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "GND", "x": 13, "y": 9, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "OUT", "x": 15, "y": 4, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [9, 4]},
                        {"a": [11, 4], "b": [13, 4]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.025},
                        {"id": "p2", "kind": "R", "x": 10, "y": 4, "rot": 0, "value": 22},
                        {"id": "p3", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p4", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "GND", "x": 13, "y": 9, "rot": 0, "value": 0},
                        {"id": "p6", "kind": "OUT", "x": 15, "y": 4, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [11, 4], "b": [13, 4]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                    ],
                },
                "checks": [
                    {"name": "at DC the capacitor simply sits at the supply", "code": r'''
c.close(c.vout(), 5.0, 0.02, "the settled DC voltage on the capacitor");
'''},
                    {"name": "the resonance is big enough to see", "code": r'''
var best = 0;
for (var f = 300; f <= 3000; f *= 1.01) { var g = c.gain(f); if (g > best) best = g; }
c.assert(best >= 25.0, "the largest reading anywhere near 1 kHz is " + c.fmt(best, "V") +
  ", and five times a 5 V source means 25 V — the damping resistor is too large, or " +
  "there is no resonance here at all");
'''},
                    {"name": "and it sits at 1 kHz", "code": r'''
var best = 0, at = 0;
for (var f = 300; f <= 3000; f *= 1.01) { var g = c.gain(f); if (g > best) { best = g; at = f; } }
c.close(at, 1000.0, 0.03, "the frequency at which the capacitor voltage peaks");
'''},
                    {"name": "two energy stores, so 40 dB per decade above it", "code": r'''
c.close(c.gain(1e4) / c.gain(100), 0.0101, 0.25,
  "the response a decade above resonance, as a fraction of the response well below it");
'''},
                ],
                "hints": [
                    "The source is wired straight across to the resistor. Delete that long wire, drop the inductor into the gap, and rejoin both ends — the same edit as the RL exercise in module 4.",
                    "Resonance is at $f_0 = 1/(2\\pi\\sqrt{LC})$. With $L = 25$ mH, $C = 1/((2\\pi \\times 1000)^2 \\times 0.025) \\approx 1\\ \\mu$F.",
                    "If the frequency is right but the peak is too small, the resistor is doing it. The peak height is roughly $1/(2\\zeta)$ with $\\zeta = \\tfrac{R}{2}\\sqrt{C/L}$, so a peak of five wants $\\zeta \\approx 0.1$, which for these values is a resistor of a few tens of ohms.",
                    "A peak an order of magnitude away in frequency usually means a prefix: `25m` is 25 millihenries and `25u` is a thousand times less.",
                ],
            },
            "derive": {
                "title": "Where the mmf goes in a gapped core",
                "minutes": 13,
                "vars": ["N", "I", "Phi", "A", "g", "L_c", "mu_0", "mu_r", "B", "H"],
                "brief": r'''
A closed ferrite ring of cross-section $A$ and magnetic path length $L_c$, with a narrow
gap of length $g$ cut across it, wound with $N$ turns carrying $I$.

The flux $\Phi$ that goes round the ring has nowhere else to be, so the *same* $\Phi$
crosses the core and the gap — which is the magnetic version of the same current
flowing through two series resistors. What differs between them is $\mu_r$, and this
derivation is about how much that difference is worth.

Take the gap narrow enough that the flux does not spread out crossing it.
''',
                "steps": [
                    {
                        "prompt": "Both regions have cross-section $A$ and carry the same flux $\\Phi$. Write the flux density $B$.",
                        "answer": "\\frac{\\Phi}{A}",
                        "hint": "Flux density is flux per unit area — the definition, nothing more.",
                        "deconstruct": [
                            "$\\Phi = BA$ for a uniform field crossing an area squarely.",
                            "Solve that for $B$.",
                        ],
                    },
                    {
                        "prompt": "In the gap the material is air, so $B = \\mu_0 H$. Write the mmf the gap consumes, which is $H$ there times the gap length $g$.",
                        "answer": "\\frac{\\Phi g}{\\mu_0 A}",
                        "hint": "Take the $B$ from the previous step, divide by $\\mu_0$ to get $H$, then multiply by $g$.",
                        "deconstruct": [
                            "$H_{gap} = B/\\mu_0 = \\Phi/(\\mu_0 A)$.",
                            "The mmf spent is $H_{gap}\\,g$.",
                        ],
                    },
                    {
                        "prompt": "In the ferrite $B = \\mu_0\\mu_r H$, so the same $B$ needs a factor $\\mu_r$ less $H$. Write the mmf the core consumes over its path length $L_c$.",
                        "answer": "\\frac{\\Phi L_c}{\\mu_0 \\mu_r A}",
                        "hint": "The same expression as the gap, with $\\mu_0$ replaced by $\\mu_0\\mu_r$ and $g$ replaced by $L_c$.",
                        "deconstruct": [
                            "$H_{core} = B/(\\mu_0\\mu_r) = \\Phi/(\\mu_0\\mu_r A)$.",
                            "The mmf spent is $H_{core}L_c$.",
                        ],
                    },
                    {
                        "prompt": "Ampère's law round the whole path says $NI$ equals the sum of those two. Solve for the flux $\\Phi$.",
                        "answer": "\\frac{N I \\mu_0 A}{g + \\frac{L_c}{\\mu_r}}",
                        "placeholder": "N I over something",
                        "hint": "Add the two mmf terms, take out the common factor $\\Phi/(\\mu_0 A)$, then divide.",
                        "deconstruct": [
                            "$NI = \\dfrac{\\Phi}{\\mu_0 A}\\left(g + \\dfrac{L_c}{\\mu_r}\\right)$.",
                            "Multiply both sides by $\\mu_0 A$ and divide by the bracket.",
                        ],
                    },
                ],
                "closing": r'''
Read the denominator: the core contributes $L_c/\mu_r$ and the gap contributes $g$, and
those are the two reluctances $\mathcal{R} = \ell/(\mu_0\mu_r A)$ sitting in series with
the $\mu_0 A$ factored out.

Numbers make the point better than the algebra does. With $L_c = 100$ mm and
$\mu_r = 2000$, the core term is $100/2000 = 0.05$ mm. A 0.5 mm gap is ten times that.
So the *equivalent* path is 0.55 mm long, of which ten elevenths is air and the ferrite
is worth one twentieth of a millimetre, and a part designed this way barely notices if
$\mu_r$ falls by half when it gets hot.

The inductance follows in one more line, since $L = N\Phi/I$: with those dimensions and
$A = 100$ mm², 331 turns give 25 mH, against 275 mH for the same winding on the same
ring with no gap.
''',
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "Mutual inductance, coupling and the transformer",
            "summary": "Two coils sharing a core are one component with four terminals — and what it does to the circuit around it is three ordinary parts you can draw.",
            "concepts": [
                "Mutual inductance: current in coil 1 makes flux, some of which threads coil 2, so a changing $I_1$ induces $V_2 = M\\,\\mathrm{d}I_1/\\mathrm{d}t$. The same $M$ works in the other direction — $M_{12} = M_{21}$ always, whatever the shapes and however lopsided they look, which is a genuine theorem and not a definition.",
                "$M = k\\sqrt{L_1 L_2}$, where the coupling coefficient $k$ runs from 0 to 1 and says what fraction of one coil's flux the other one catches. Two windings on a shared closed ferrite core reach $k > 0.99$; two coils a centimetre apart in air might manage 0.1.",
                "The ideal transformer is the limit $k = 1$ with a core good enough that no current is needed to make the flux. Both windings then link the same $\\mathrm{d}\\Phi/\\mathrm{d}t$, so $V_2/V_1 = N_2/N_1$; and since nothing stores or dissipates anything, $V_1I_1 = V_2I_2$ forces $I_2/I_1 = N_1/N_2$.",
                "Put those two together and a load $Z$ on the secondary looks like $(N_1/N_2)^2 Z$ from the primary. Changing an impedance is often the *reason* for the transformer rather than a side effect: it is how a 4 Ω loudspeaker was matched to a valve amplifier that wanted to see thousands of ohms.",
                "Three departures from the ideal are worth drawing. Winding resistance sits in series. Leakage inductance — the $(1-k)$ part of the flux that misses the other winding — also sits in series, and limits the top of the band. And the magnetising inductance sits *across* the primary: a real core needs some current to make flux, and that current is what a transformer draws with its secondary open. It is also why a transformer passes no DC and droops at the bottom of its band.",
            ],
            "quiz": {
                "title": "Transformers, checked",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A transformer has 1000 primary turns and 100 secondary turns and is fed from 230 V AC. Ignoring losses, what does the secondary produce, and what current does it deliver when the primary draws 0.10 A?",
                        "opts": ["23 V at 1.0 A", "23 V at 0.010 A", "2300 V at 1.0 A", "23 V at 0.10 A"],
                        "a": 0,
                        "why": (
                            "The voltage follows the turns: $230 \\times 100/1000 = 23$ V. The current goes the "
                            "other way, so it is multiplied by ten: 1.0 A. Check it with power — 230 V at "
                            "0.10 A is 23 W in, 23 V at 1.0 A is 23 W out. Any answer where those two "
                            "disagree is asking a piece of iron to create energy."
                        ),
                    },
                    {
                        "q": "You connect a 12 V battery across the primary of a transformer and wait. What appears at the secondary?",
                        "opts": [
                            "12 V, scaled by the turns ratio",
                            "Nothing, once the initial switch-on transient has died away",
                            "12 V exactly, whatever the turns ratio",
                            "A steadily rising voltage",
                        ],
                        "a": 1,
                        "why": (
                            "Faraday's law responds to $\\mathrm{d}\\Phi/\\mathrm{d}t$, and a steady current "
                            "makes a steady flux, whose rate of change is zero. There is a pulse at the moment "
                            "of connection, while the current is still building — and that pulse is exactly "
                            "what an ignition coil is for — but nothing after it. Meanwhile the primary "
                            "current keeps rising until only the winding resistance limits it, which is how "
                            "transformers are destroyed by DC."
                        ),
                    },
                    {
                        "q": "An 8 Ω loudspeaker is connected to the secondary of a transformer with ten times as many primary turns as secondary turns. What impedance does the amplifier driving the primary see?",
                        "opts": ["800 Ω", "80 Ω", "8 Ω", "0.08 Ω"],
                        "a": 0,
                        "why": (
                            "Impedance reflects as the *square* of the turns ratio: $10^2 \\times 8 = 800$ Ω. "
                            "The square is not arbitrary — the primary voltage is ten times larger and the "
                            "primary current ten times smaller, and impedance is their ratio. Answering 80 Ω "
                            "is applying the turns ratio once, which is what the voltage does but not what "
                            "the impedance does."
                        ),
                    },
                    {
                        "q": "Two coils of 100 mH and 400 mH are coupled with $k = 0.5$. What is the mutual inductance?",
                        "opts": ["100 mH", "250 mH", "200 mH", "50 mH"],
                        "a": 0,
                        "why": (
                            "$M = k\\sqrt{L_1L_2} = 0.5\\sqrt{0.1 \\times 0.4} = 0.5 \\times 0.2 = 0.1$ H. The "
                            "geometric mean, not the average: 250 mH is the arithmetic mean of the two "
                            "inductances and has no role here. Note that even perfect coupling would only "
                            "give 200 mH — $\\sqrt{L_1L_2}$ is a hard ceiling on $M$, and it is what $k \\le "
                            "1$ means."
                        ),
                    },
                    {
                        "q": "A step-up transformer delivers a higher voltage than it is given. Where does the extra energy come from?",
                        "opts": [
                            "From the core, which stores it between cycles",
                            "Nowhere — the current falls in the same ratio the voltage rises, so the power is unchanged",
                            "From the extra turns on the secondary",
                            "From the mains, which supplies whatever is needed",
                        ],
                        "a": 1,
                        "why": (
                            "A transformer is not a source. Ten times the voltage comes with a tenth of the "
                            "current available, and the product — the power — is the same on both sides, less "
                            "a few per cent of losses. The core does store energy within a cycle and give it "
                            "back, which is what the magnetising inductance describes, but the average of "
                            "that over a cycle is zero."
                        ),
                    },
                    {
                        "q": "With nothing at all connected to its secondary, a real transformer plugged into the mains still draws a small current. What is that current doing?",
                        "opts": [
                            "Leaking through the insulation",
                            "Flowing in the magnetising inductance to establish the core flux — largely reactive, returned each cycle",
                            "Charging the winding capacitance, and nothing else",
                            "Nothing; a well-made transformer draws no current with the secondary open",
                        ],
                        "a": 1,
                        "why": (
                            "A real core has finite permeability, so it takes some mmf — some current — to "
                            "drive flux round it. That current lags the voltage by nearly 90°, so it carries "
                            "almost no real power: energy goes into the field on one part of the cycle and "
                            "comes back on the next. It is the current through the magnetising inductance, "
                            "and it is the same current that makes the flux the secondary will link once you "
                            "load it."
                        ),
                    },
                ],
            },
            "build": {
                "title": "A transformer, drawn as the three parts it behaves like",
                "minutes": 22,
                "brief": r'''
There is no transformer symbol on this canvas, which is convenient, because what a
transformer does to the circuit on its primary side is captured entirely by ordinary
components — and drawing them is a better way of understanding it than drawing two
coils and a pair of bars.

The situation: an amplifier with a **100 Ω** output resistance drives the primary of a
10:1 transformer, and a 9 Ω load hangs on the secondary. Reflected through the square of
the turns ratio, that load appears at the primary as $10^2 \times 9 = 900\ \Omega$, and
the canvas already has both of those drawn, with the probe on the primary terminal.

What is missing is the **magnetising inductance**: the primary current a real core needs
in order to have any flux in it at all. It goes from the primary node down to ground,
in parallel with the reflected load, and choosing it is choosing how low in frequency
this transformer still works.

Add it, and pick a value big enough that

- with a **steady** source the probe reads exactly zero — a transformer passes no DC, and
  in this model it is the inductance shorting the primary out that says so;
- at **50 Hz** the primary still reaches at least **4.2 V**;
- and well above the droop, at 5 kHz, the probe settles at the plain resistive answer
  $5 \times 900/1000 = 4.5$ V.

Type inductances as `1` for a henry, `500m` for half of one.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 100},
                        {"id": "p2", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 900},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "GND", "x": 13, "y": 9, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "OUT", "x": 15, "y": 4, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [13, 4]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 100},
                        {"id": "p2", "kind": "L", "x": 9, "y": 6, "rot": 1, "value": 1},
                        {"id": "p3", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 900},
                        {"id": "p4", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "GND", "x": 9, "y": 9, "rot": 0, "value": 0},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 9, "rot": 0, "value": 0},
                        {"id": "p7", "kind": "OUT", "x": 15, "y": 4, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 4], "b": [13, 4]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                    ],
                },
                "checks": [
                    {"name": "nothing gets through on DC", "code": r'''
var v = c.vout();
c.assert(Math.abs(v) < 1e-6, "with a steady source the probe still reads " + c.fmt(v, "V") +
  " — there is no path pulling the primary to ground, so this circuit would happily " +
  "pass direct current, and a transformer does not");
'''},
                    {"name": "well above the droop it is just the two resistors", "code": r'''
c.close(c.gain(5000), 4.5, 0.02,
  "the primary voltage at 5 kHz, which should be the plain 900/1000 of the source");
'''},
                    {"name": "at 50 Hz the magnetising inductance has not stolen too much", "code": r'''
var g = c.gain(50);
c.assert(g >= 4.2, "at 50 Hz the primary only reaches " + c.fmt(g, "V") + " of the 4.5 V " +
  "it manages higher up; the magnetising inductance is small enough to be shunting the " +
  "source away");
'''},
                    {"name": "the part that blocks the DC is an inductance", "code": r'''
c.assert(c.count("L") >= 1, "there is no inductor in this circuit. A series capacitor would " +
  "measure much the same at the probe, which is worth knowing — but the thing that stops a " +
  "real transformer passing DC is the magnetising inductance across the primary, and that " +
  "is what this model has to contain");
c.assert(c.count("C") === 0, "there is a capacitor here, and nothing in the primary model of " +
  "a transformer is a capacitor");
'''},
                ],
                "hints": [
                    "The inductor is vertical, from the wire joining the 100 Ω to the 900 Ω, down to a ground of its own — in parallel with the 900 Ω, not in series with it.",
                    "Any inductor at all makes the DC check pass, because at DC an inductor is a piece of wire and it shorts the probe to ground. The 50 Hz check is the one that sets the value.",
                    "Work out the reactance you need before choosing, and note which resistance sets the target. The inductor is in parallel with the 900 Ω but is fed through the 100 Ω, so the droop corner sits where $\\omega L$ equals the two in parallel, $100 \\parallel 900 = 90\\ \\Omega$ — not where it equals 900 Ω. At 50 Hz, $2\\pi \\times 50 \\times 1\\ \\mathrm{H} = 314\\ \\Omega$, three and a half times that, which is already enough here. Anything below about three quarters of a henry is not.",
                    "This model leaves out the leakage inductance, which would sit in series and roll the response off at the *top* of the band. Adding it is a good thing to try afterwards; it is not what the checks are asking for.",
                ],
            },
            "blanks": {
                "title": "The four transformer relations",
                "minutes": 9,
                "caption": "the ideal transformer, with N1 primary turns and N2 secondary",
                "lang": "text",
                "brief": r'''
Every one of these follows from a single premise — that both windings are threaded by
the same flux, so both see the same $\mathrm{d}\Phi/\mathrm{d}t$ — plus the fact that an
ideal transformer neither stores nor dissipates energy.

Nothing here is executed. You are choosing symbols, and the point is to be able to
reconstruct all four from the premise rather than remembering which way up each ratio
goes.
''',
                "listing": """# An ideal transformer. N1 turns on the primary, N2 on the secondary,
# both wound on the same core, so both link the same flux Phi:
#
#     V1 = N1 * dPhi/dt          V2 = N2 * dPhi/dt
#     and no energy is stored or lost, so   V1 * I1 = V2 * I2

V2 / V1                    = ___

I2 / I1                    = ___

Z_seen_from_the_primary    = ___ * Z_load

# with a steady primary current, dPhi/dt = 0, and so
V2                         = ___
""",
                "blanks": [
                    {
                        "prompt": "Divide the two Faraday expressions above. What is left?",
                        "hole": "?",
                        "opts": ["N2 / N1", "N1 / N2", "(N2 / N1)**2", "N1 * N2"],
                        "a": 0,
                        "why": "Both windings share $\\mathrm{d}\\Phi/\\mathrm{d}t$, so dividing $V_2 = N_2\\,\\mathrm{d}\\Phi/\\mathrm{d}t$ by $V_1 = N_1\\,\\mathrm{d}\\Phi/\\mathrm{d}t$ cancels it completely and leaves the turns. More turns on the secondary, more volts out.",
                        "whys": [
                            "Both windings share $\\mathrm{d}\\Phi/\\mathrm{d}t$, so dividing $V_2 = N_2\\,\\mathrm{d}\\Phi/\\mathrm{d}t$ by $V_1 = N_1\\,\\mathrm{d}\\Phi/\\mathrm{d}t$ cancels it completely and leaves the turns. More turns on the secondary, more volts out.",
                            "That is the ratio upside down. It would say a secondary with more turns than the primary produces *less* voltage, which would make a step-up transformer impossible to wind.",
                            "The square belongs to impedance, which is a ratio of a voltage to a current and therefore picks up the turns ratio twice. A voltage picks it up once.",
                            "A product cannot be right on units alone: doubling both windings would then quadruple the output voltage, when in fact it changes nothing.",
                        ],
                    },
                    {
                        "prompt": "Now use $V_1I_1 = V_2I_2$ together with the ratio you just wrote.",
                        "hole": "?",
                        "opts": ["N1 / N2", "N2 / N1", "(N1 / N2)**2", "1"],
                        "a": 0,
                        "why": "Conservation of power says $I_2/I_1 = V_1/V_2$, and $V_1/V_2$ is $N_1/N_2$ — so the current ratio is the inverse of the voltage ratio. A transformer that multiplies volts divides amps by the same factor, which is the whole reason the grid runs at high voltage.",
                        "whys": [
                            "Conservation of power says $I_2/I_1 = V_1/V_2$, and $V_1/V_2$ is $N_1/N_2$ — so the current ratio is the inverse of the voltage ratio. A transformer that multiplies volts divides amps by the same factor, which is the whole reason the grid runs at high voltage.",
                            "This makes the current follow the turns the same way the voltage does, so a step-up transformer would deliver more volts *and* more amps. That is more power out than in.",
                            "Squaring appears when a voltage ratio and a current ratio are combined into an impedance. Here only one of the two is involved.",
                            "Equal currents on both sides would break the power balance unless the voltages were equal too, which is the one case where the transformer is doing nothing.",
                        ],
                    },
                    {
                        "prompt": "Impedance at the primary is $V_1/I_1$. Write both in terms of the secondary.",
                        "hole": "?",
                        "opts": ["(N1 / N2)**2", "N2 / N1", "N1 / N2", "(N2 / N1)**2"],
                        "a": 0,
                        "why": "$V_1 = V_2 N_1/N_2$ and $I_1 = I_2 N_2/N_1$, so the ratio picks up $N_1/N_2$ twice: $Z_1 = (N_1/N_2)^2 Z_2$. With ten times the primary turns, an 8 Ω speaker looks like 800 Ω — and that transformation, not the voltage, is often the reason the transformer is there.",
                        "whys": [
                            "$V_1 = V_2 N_1/N_2$ and $I_1 = I_2 N_2/N_1$, so the ratio picks up $N_1/N_2$ twice: $Z_1 = (N_1/N_2)^2 Z_2$. With ten times the primary turns, an 8 Ω speaker looks like 800 Ω — and that transformation, not the voltage, is often the reason the transformer is there.",
                            "This scales the impedance the way the *secondary voltage* scales, and in the wrong direction as well: a step-down transformer has $N_1 > N_2$, so it makes a load look *larger* from the primary — 800 Ω for an 8 Ω speaker at 10:1 — while $N_2/N_1$ is less than one there and would shrink it to 0.8 Ω.",
                            "Applying the turns ratio once is what a voltage does. An impedance is a voltage divided by a current, and both of those changed, so the factor appears twice.",
                            "This has the square, which is right, but inverted — it would make a 10:1 step-down transformer present 8 Ω as 0.08 Ω rather than 800 Ω.",
                        ],
                    },
                    {
                        "prompt": "What does the secondary produce when the primary current is steady?",
                        "hole": "?",
                        "opts": ["0", "V1", "V1 * N2 / N1", "as large as you like"],
                        "a": 0,
                        "why": "The premise of every line above is $\\mathrm{d}\\Phi/\\mathrm{d}t$, and a steady current makes a steady flux whose rate of change is zero. So the secondary produces nothing at all, however large the primary voltage or the flux itself. This is the single most useful thing to remember about transformers: they are blind to DC.",
                        "whys": [
                            "The premise of every line above is $\\mathrm{d}\\Phi/\\mathrm{d}t$, and a steady current makes a steady flux whose rate of change is zero. So the secondary produces nothing at all, however large the primary voltage or the flux itself. This is the single most useful thing to remember about transformers: they are blind to DC.",
                            "Equal voltages would need equal turns, and even then Faraday's law gives nothing while the flux is not changing — the windings are not connected to each other, only coupled through a field that is standing still.",
                            "That is the correct answer for an alternating primary voltage, and it is exactly the mistake to watch for: the turns ratio scales $\\mathrm{d}\\Phi/\\mathrm{d}t$, and scaling zero gives zero.",
                            "Nothing here can produce an unbounded voltage. There is a large transient at the instant the primary current changes — which is what an ignition coil exploits — but with the current steady there is no output at all.",
                        ],
                    },
                ],
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "Displacement current, Maxwell's equations and the wave",
            "summary": "One term was missing from Ampere's law. Putting it back closes the subject: the fields stop needing charges and start carrying themselves, at a speed you can compute from two laboratory constants.",
            "concepts": [
                "Ampere's law as module 4 states it is not consistent. Take a charging capacitor and a loop round the wire feeding it: one surface spanning that loop is pierced by the wire and reports a current, another bulges out and passes between the plates, where no charge crosses at all. Same loop, same law, two answers.",
                "Maxwell's repair: a changing electric flux counts as a current too, $I_d = \\varepsilon_0\\,\\mathrm{d}\\Phi_E/\\mathrm{d}t$. Between the plates the field is growing at exactly the rate that makes $I_d$ equal to the wire current, and the contradiction disappears. Nothing is flowing there; the name is historical and slightly unhelpful.",
                "The four equations, in words. Electric field lines begin and end on charge. Magnetic field lines do neither. A changing magnetic flux drives an electric field round a loop. A current *or* a changing electric flux drives a magnetic field round a loop. The first two are the Gauss laws of modules 2 and 4, the third is Faraday, and the fourth is the one that was just repaired.",
                "The last two now feed each other, and away from all charge they admit a solution with no sources anywhere: a disturbance in which each field's change sustains the other, travelling at $1/\\sqrt{\\mu_0\\varepsilon_0}$. Put in the two constants measured on a bench with capacitors and coils and that comes to $3.00\\times10^8$ m/s, which was already the measured speed of light — the strongest circumstantial evidence in the history of physics.",
                "In such a wave $\\mathbf{E}$ and $\\mathbf{B}$ are perpendicular to each other and to the direction of travel, in step, with $E = cB$. The ratio $E/H$ is the same everywhere and is a property of the vacuum: $\\eta_0 = \\sqrt{\\mu_0/\\varepsilon_0} = 376.7\\ \\Omega$. Power flows as $\\mathbf{S} = \\mathbf{E}\\times\\mathbf{H}$, which for a sinusoid averages $E_0^2/(2\\eta_0)$ watts per square metre.",
            ],
            "sandbox": {
                "title": "The two fields, sloshing",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "initial": {"a11": 0, "a12": 2, "a21": -0.5, "a22": 0},
                "brief": r'''
The same panel again, and now the two axes are the two fields. Fix a spatial pattern —
a sine wave of wavenumber $k$ frozen in place — and let $x_1$ be the amplitude of the
electric field in it and $x_2$ the amplitude of the magnetic field strength $H$.
Faraday's law and the repaired Ampere law then say

$$\dot{x_1} = \frac{k}{\varepsilon_0}\,x_2, \qquad
  \dot{x_2} = -\frac{k}{\mu_0}\,x_1$$

which is these sliders with $a_{12} = k/\varepsilon_0$ and $a_{21} = -k/\mu_0$. Each
field's rate of change is set by how much of the *other* one there is, and by nothing
else. There is no charge anywhere in this picture and no current.

Two numbers fall out of the two entries. Their product is $k^2/(\mu_0\varepsilon_0)$, so
$\sqrt{a_{12}\,|a_{21}|}$ is the frequency $ck$. Their ratio is $\mu_0/\varepsilon_0$,
so $\sqrt{a_{12}/|a_{21}|}$ is the ratio of the two field amplitudes — the impedance.
The real one is 377, which would draw as a flat line; the opening values use 2 instead,
so that both axes are visible.
''',
                "notice": [
                    "As it opens the readout says trace = 0.00, det = 1.00 and calls it a centre. Nothing decays and nothing grows: the disturbance goes round and round forever with no charge sustaining it. Energy is passing between the electric term and the magnetic term and back, and the closed curve is the statement that the total does not change.",
                    "The orbits are ellipses twice as wide as they are tall. The electric amplitude is twice the magnetic one, because $\\sqrt{a_{12}/|a_{21}|} = \\sqrt{2/0.5} = 2$ — and that is the impedance of this pretend vacuum. In the real one the same square root gives 377 Ω, which is why the electric field of a radio wave is easy to measure and the magnetic field is not.",
                    "Set $a_{12} = 0.5$ and $a_{21} = -2$. The readout is unchanged — trace 0.00, det 1.00, a centre at the same rate — but the ellipses are now taller than they are wide. The determinant fixes the speed and the *ratio* of the two entries fixes the impedance, and they are genuinely independent: two different media can carry waves at the same speed with different field ratios.",
                    "Now set $a_{12} = 1$ and $a_{21} = -0.25$. The det falls to 0.25, so the orbits are traced at half the rate, while the shape of the ellipse is untouched. Both entries were divided by two, which is a material with twice the permittivity and twice the permeability of the vacuum: $c = 1/\\sqrt{\\mu\\varepsilon}$ halves and $\\eta = \\sqrt{\\mu/\\varepsilon}$ does not move. That is exactly what those two formulas say, drawn.",
                    "Put $a_{12}$ and $a_{21}$ back to 2 and $-0.5$, then pull $a_{11}$ down to $-0.20$. Trace $-0.20$, det 1.00, and it becomes a stable spiral: the wave still oscillates but dies away. A loss term on the electric equation is a conduction current $\\sigma E$ — a medium with some conductivity in it — and this is why seawater is opaque to radio and why a metal box keeps a wave out as effectively as it keeps a static field out.",
                ],
            },
            "quiz": {
                "title": "Maxwell and the wave, checked",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A capacitor is charging at 2 A. What is the displacement current between its plates?",
                        "opts": ["Zero — no charge crosses the gap", "2 A", "It depends on the plate separation", "Half of 2 A, since the current splits between the plates"],
                        "a": 1,
                        "why": (
                            "Exactly 2 A, and it has to be: the whole reason for inventing the term was to make "
                            "Ampere's law give the same answer whichever surface you span the loop with. "
                            "Charge really does not cross the gap, and nothing is flowing there — what is "
                            "happening is that $\\varepsilon_0\\,\\mathrm{d}\\Phi_E/\\mathrm{d}t$ between the "
                            "plates comes out numerically equal to the current in the wire, because the "
                            "arriving charge is precisely what is raising the field."
                        ),
                    },
                    {
                        "q": "Which of Maxwell's four equations has zero on its right-hand side, always and everywhere?",
                        "opts": [
                            "The one for the flux of E out of a closed surface",
                            "The one for the flux of B out of a closed surface",
                            "Faraday's law",
                            "The Ampere–Maxwell law",
                        ],
                        "a": 1,
                        "why": (
                            "The magnetic flux out of any closed surface is zero, because there is no magnetic "
                            "charge for a field line to start on: every line that leaves comes back. Its "
                            "electric counterpart has the enclosed charge on the right, and that is the "
                            "deepest asymmetry in the whole set. If an isolated magnetic pole were ever found, "
                            "this is the equation that would have to change."
                        ),
                    },
                    {
                        "q": "Why was it significant that $1/\\sqrt{\\mu_0\\varepsilon_0}$ comes to $3.00\\times10^8$ m/s?",
                        "opts": [
                            "Because it proved that light must be a wave rather than a stream of particles",
                            "Because two constants measured with capacitors and coils reproduced the independently measured speed of light",
                            "Because it fixed the value of the metre",
                            "Because it showed that the speed of light depends on the medium",
                        ],
                        "a": 1,
                        "why": (
                            "$\\varepsilon_0$ came out of electrostatic force measurements and $\\mu_0$ out of "
                            "the force between current-carrying wires. Neither experiment involves light in "
                            "any way, and their combination reproduced a number astronomers and opticians had "
                            "measured by completely different means. That coincidence is what identified light "
                            "as an electromagnetic wave — and it is why this course, which began with two "
                            "charged spheres, is allowed to end here."
                        ),
                    },
                    {
                        "q": "A plane wave in vacuum has an electric field amplitude of 100 V/m. What is its magnetic field amplitude?",
                        "opts": ["$3.3\\times10^{-7}$ T", "$1.3\\times10^{-6}$ T", "$3.0\\times10^{10}$ T", "100 T"],
                        "a": 0,
                        "why": (
                            "$E = cB$, so $B = 100/(3.00\\times10^8) = 3.3\\times10^{-7}$ T. The magnetic part "
                            "of an electromagnetic wave always looks negligible written in tesla and is not: "
                            "the two carry equal energy density. The units are simply scaled by a factor of "
                            "$c$, which is a large number that has nothing to do with the physics being "
                            "lopsided."
                        ),
                    },
                    {
                        "q": "The impedance of free space is 377 Ω. What is it the ratio of?",
                        "opts": [
                            "The voltage across a metre of vacuum to the current through it",
                            "The electric field to the magnetic field strength in a plane wave",
                            "The resistance an antenna presents to its feeder",
                            "The energy in the electric field to the energy in the magnetic field",
                        ],
                        "a": 1,
                        "why": (
                            "$\\eta_0 = E/H$ in a travelling wave, and it comes out in ohms because volts per "
                            "metre divided by amps per metre is volts per amp. Nothing conducts and nothing "
                            "dissipates — a vacuum is not a resistor. An antenna's feed impedance is a related "
                            "but different quantity, set by the antenna's geometry, and the two field energies "
                            "in a plane wave are equal rather than in the ratio 377."
                        ),
                    },
                    {
                        "q": "Sunlight at the ground delivers roughly 1000 W/m². Roughly how large is the peak electric field in it?",
                        "opts": ["About 2.7 V/m", "About 87 V/m", "About 870 V/m", "About 8.7 kV/m"],
                        "a": 2,
                        "why": (
                            "Invert $S = E_0^2/(2\\eta_0)$: $E_0 = \\sqrt{2 \\times 376.7 \\times 1000} = 868$ "
                            "V/m. It is a startling number — comparable to the field a few centimetres from a "
                            "charged balloon — and the accompanying magnetic amplitude is 2.9 µT, which is a "
                            "twentieth of the Earth's own field. Sunlight is not a feeble thing; it is just "
                            "spread thinly and oscillating far too fast for anything mechanical to follow."
                        ),
                    },
                ],
            },
            "derive": {
                "title": "The speed of light, and the impedance of free space",
                "minutes": 12,
                "vars": ["E", "B", "H", "c", "mu_0", "epsilon_0", "eta_0"],
                "brief": r'''
Take the wave for granted — a disturbance travelling through empty space, with $E$ and
$H$ perpendicular to each other and to the direction of travel — and extract its two
constants.

Write the permeability as `\mu_0` and the permittivity as `\epsilon_0`.
''',
                "steps": [
                    {
                        "prompt": "Combining Faraday's law with the Ampere–Maxwell law in empty space gives a wave equation, and every wave equation carries a speed. Write it in terms of $\\mu_0$ and $\\varepsilon_0$.",
                        "answer": "\\frac{1}{\\sqrt{\\mu_0 \\epsilon_0}}",
                        "hint": "The two constants appear as a product, under a square root, in the denominator. Check the units if you are unsure which way up it goes: $\\mu_0\\varepsilon_0$ has units of s²/m².",
                        "deconstruct": [
                            "The wave equation reads $\\partial^2 E/\\partial x^2 = \\mu_0\\varepsilon_0\\,\\partial^2 E/\\partial t^2$.",
                            "Comparing with the standard form, which has $1/c^2$ in that place, gives $c^2 = 1/(\\mu_0\\varepsilon_0)$.",
                        ],
                    },
                    {
                        "prompt": "In a plane wave the two fields are locked together by $E = cB$. Write $B$ in terms of $E$, $\\mu_0$ and $\\varepsilon_0$ — with no $c$ left in it.",
                        "answer": "E \\sqrt{\\mu_0 \\epsilon_0}",
                        "hint": "$B = E/c$, and dividing by $1/\\sqrt{\\mu_0\\varepsilon_0}$ is multiplying by $\\sqrt{\\mu_0\\varepsilon_0}$.",
                        "deconstruct": [
                            "$B = E/c$.",
                            "Substitute the $c$ from the previous step and turn the division into a multiplication.",
                        ],
                    },
                    {
                        "prompt": "The magnetic field strength is $H = B/\\mu_0$. Write $H$ in terms of $E$ and the two constants.",
                        "answer": "E \\sqrt{\\frac{\\epsilon_0}{\\mu_0}}",
                        "hint": "Divide the previous answer by $\\mu_0$ and pull the $\\mu_0$ inside the root, where it cancels one of the two factors already there.",
                        "deconstruct": [
                            "$H = E\\sqrt{\\mu_0\\varepsilon_0}/\\mu_0$.",
                            "Write $\\mu_0$ as $\\sqrt{\\mu_0^2}$ and cancel inside the root.",
                        ],
                    },
                    {
                        "prompt": "The impedance of free space is $\\eta_0 = E/H$. Write it.",
                        "answer": "\\sqrt{\\frac{\\mu_0}{\\epsilon_0}}",
                        "placeholder": "a root of a ratio",
                        "hint": "Divide $E$ by the previous answer. The $E$ cancels, and dividing by a square root inverts what is inside it.",
                        "deconstruct": [
                            "$E/H = E \\div (E\\sqrt{\\varepsilon_0/\\mu_0})$.",
                            "The $E$ cancels and the reciprocal turns the fraction inside the root upside down.",
                        ],
                    },
                ],
                "closing": r'''
Two numbers, and both of them are only constants of the vacuum:

$$c = \frac{1}{\sqrt{\mu_0\varepsilon_0}} = 2.998\times10^8\ \mathrm{m/s},
\qquad \eta_0 = \sqrt{\frac{\mu_0}{\varepsilon_0}} = 376.7\ \Omega$$

The first identified light. The second is what every antenna is matched against, and it
is why a resistive film of 377 ohms per square, hung a quarter of a wavelength in front
of a metal backing, absorbs a normally incident wave instead of reflecting it — the
Salisbury screen, and the ancestor of every radar-absorbing coating.

Notice also that the two between them hold nothing new. Multiply them and you get
$c\,\eta_0 = 1/\varepsilon_0$; divide the impedance by the speed and you get
$\eta_0/c = \mu_0$. There were only ever two constants in this course, and every result
in it has been one or the other wearing different units.
''',
            },
            "lab": {
                "title": "The two constants, and what they predict",
                "runtime": "python",
                "minutes": 22,
                "brief": r'''
Six one-line functions, and the point of all of them is the numbers that come out.

`speed_of_light()` returns $1/\sqrt{\mu_0\varepsilon_0}$ in m/s, and
`impedance_of_free_space()` returns $\sqrt{\mu_0/\varepsilon_0}$ in ohms. Both take no
arguments: they are properties of empty space, and `MU0` and `EPS0` are defined for you.

`wavelength(frequency)` returns $c/f$ in metres.

`b_from_e(e_field)` returns the magnetic amplitude that accompanies an electric
amplitude in a plane wave, from $E = cB$.

`intensity(e_peak)` returns the average power per square metre, $E_0^2/(2\eta_0)$, and
`peak_field(intensity)` inverts it. Feed one into the other and you must get back what
you started with.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

EPS0 = 8.8541878128e-12   # F/m
MU0 = 1.25663706212e-6    # H/m


def speed_of_light():
    """The speed of an electromagnetic wave in vacuum, in m/s."""
    # TODO: 1 / sqrt(MU0 * EPS0)
    return 0.0


def impedance_of_free_space():
    """The ratio E/H in a plane wave, in ohms."""
    # TODO: sqrt(MU0 / EPS0)
    return 0.0


def wavelength(frequency):
    """Wavelength in metres of a wave of that frequency in vacuum."""
    # TODO
    return 0.0


def b_from_e(e_field):
    """Magnetic amplitude in tesla accompanying an electric amplitude in V/m."""
    # TODO
    return 0.0


def intensity(e_peak):
    """Average power per square metre carried by a wave of that peak field."""
    # TODO
    return 0.0


def peak_field(power_per_m2):
    """Peak electric field in V/m of a wave carrying that intensity."""
    # TODO: invert `intensity`.
    return 0.0


if __name__ == "__main__":
    print("c =", speed_of_light(), "m/s")
    print("eta_0 =", impedance_of_free_space(), "ohm")
    print("100 MHz has a wavelength of", wavelength(100e6), "m")
    print("sunlight at 1000 W/m^2 peaks at", peak_field(1000.0), "V/m")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

EPS0 = 8.8541878128e-12   # F/m
MU0 = 1.25663706212e-6    # H/m


def speed_of_light():
    """The speed of an electromagnetic wave in vacuum, in m/s."""
    return float(1.0 / np.sqrt(MU0 * EPS0))


def impedance_of_free_space():
    """The ratio E/H in a plane wave, in ohms."""
    return float(np.sqrt(MU0 / EPS0))


def wavelength(frequency):
    """Wavelength in metres of a wave of that frequency in vacuum."""
    return float(speed_of_light() / frequency)


def b_from_e(e_field):
    """Magnetic amplitude in tesla accompanying an electric amplitude in V/m."""
    return float(e_field / speed_of_light())


def intensity(e_peak):
    """Average power per square metre carried by a wave of that peak field."""
    return float(e_peak * e_peak / (2.0 * impedance_of_free_space()))


def peak_field(power_per_m2):
    """Peak electric field in V/m of a wave carrying that intensity."""
    return float(np.sqrt(2.0 * impedance_of_free_space() * power_per_m2))


if __name__ == "__main__":
    print("c =", speed_of_light(), "m/s")
    print("eta_0 =", impedance_of_free_space(), "ohm")
    print("100 MHz has a wavelength of", wavelength(100e6), "m")
    print("sunlight at 1000 W/m^2 peaks at", peak_field(1000.0), "V/m")
'''}],
                "hints": [
                    "`np.sqrt` for both constants. The product goes under the root for the speed and the quotient goes under it for the impedance — swapping them gives a number with the wrong units and no meaning.",
                    "Build the later functions out of the earlier ones rather than retyping the constants, so there is one place where the physics lives.",
                    "`intensity` has the *peak* field in it and the factor of two is the average of $\\sin^2$ over a cycle. Leaving it out overstates the power by a factor of two.",
                    "`peak_field` is `intensity` solved for the field: multiply by $2\\eta_0$ and take the root.",
                ],
                "tests": [
                    {"name": "two bench constants give the speed of light", "code": r'''
_c = speed_of_light()
assert abs(_c - 299792458.0000065) < 1.0, \
    f"expected 2.998e8 m/s, got {_c!r}"
assert abs(_c / 299792458.0 - 1.0) < 1e-9, \
    "this should agree with the defined speed of light to nine figures, and it does"
'''},
                    {"name": "and the impedance of free space", "code": r'''
_e = impedance_of_free_space()
assert abs(_e - 376.73031366686166) < 1e-9, f"expected 376.73 ohm, got {_e!r}"
assert abs(_e * _e * 8.8541878128e-12 - 1.25663706212e-6) < 1e-18, \
    "squaring the impedance and multiplying by EPS0 must give MU0 back"
'''},
                    {"name": "wavelengths of things you have heard of", "code": r'''
assert abs(wavelength(100e6) - 2.997924580000065) < 1e-9, \
    f"an FM broadcast at 100 MHz is about 3 m long, got {wavelength(100e6)!r} m"
assert abs(wavelength(2.4e9) - 0.12491352416666937) < 1e-12, \
    f"a 2.4 GHz wireless link is 12.5 cm, got {wavelength(2.4e9)!r} m"
assert abs(wavelength(50.0) - 5995849.16000013) < 1e-3, \
    f"a 50 Hz mains cycle is six thousand kilometres long, got {wavelength(50.0)!r} m"
'''},
                    {"name": "the magnetic half of the wave", "code": r'''
_b = b_from_e(100.0)
assert abs(_b - 3.3356409519814484e-07) < 1e-18, \
    f"100 V/m comes with 334 nT, got {_b!r} T"
assert abs(b_from_e(200.0) - 2.0 * _b) < 1e-18, "the two amplitudes are strictly proportional"
assert abs(b_from_e(0.0)) < 1e-30, "no electric field means no magnetic field either"
'''},
                    {"name": "sunlight, both ways round", "code": r'''
_e = peak_field(1000.0)
assert abs(_e - 868.0210984381217) < 1e-6, \
    f"1 kW per square metre peaks at 868 V/m, got {_e!r}"
assert abs(intensity(_e) - 1000.0) < 1e-9, \
    "feeding the peak field back into `intensity` must return the 1000 W/m^2 it came from"
assert abs(intensity(100.0) - 13.27209363996507) < 1e-9, \
    f"100 V/m carries 13.3 W/m^2, got {intensity(100.0)!r}"
'''},
                    {"name": "intensity goes as the square of the field", "code": r'''
_one = intensity(50.0)
_two = intensity(100.0)
assert abs(_two / _one - 4.0) < 1e-9, \
    f"doubling the field should quadruple the power, got a ratio of {_two / _one}"
assert abs(peak_field(1.0) - 27.4492372814569) < 1e-9, \
    f"one watt per square metre peaks at 27.4 V/m, got {peak_field(1.0)!r}"
assert peak_field(4.0) > 2.0 * peak_field(1.0) - 1e-9, \
    "four times the power needs twice the field"
'''},
                ],
            },
        },

    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "An electromagnetics toolkit, and two components designed with it",
        "runtime": "python",
        "minutes": 100,
        "brief": r'''
Everything in this course has been the same move made twice: start from a force or a
geometry, and end with a number you can put into a circuit. This capstone assembles
the pieces into one small toolkit and then uses it backwards — not "what does this
shape do", but "what shape do I need".

`emconst.py` holds the constants and is read-only. Work in `main.py`.

## What to build

1. **Fields and potentials.** `field_at(charges, point)` and
   `potential_at(charges, point)`, as in modules 1 and 2: a vector sum and a scalar
   sum over a list of `(q, x, y)` charges.
2. **Gauss's law.** `flux_out_of_sphere(charges, centre, radius)`, using enclosed
   charge only.
3. **Geometry, forwards.** `plate_capacitance(area, gap, eps_r)` and
   `solenoid_inductance(turns, length, area, mu_r)`.
4. **Geometry, backwards.** `design_capacitor(target_c, gap, eps_r)` returns the plate
   area in m² that hits the target, and `design_solenoid(target_l, length, area)`
   returns the turn count. Each must be an exact inverse of the forward function —
   feed the answer back in and the target must come out. Leave the turn count as a
   real number; rounding it to a whole number of turns is a manufacturing decision,
   not a physics one.
5. **Transients.** `rc_voltage(v_source, r, c, t)` gives the capacitor voltage at time
   `t` when charging from rest, and `rl_voltage(v_source, l, r, t)` gives the voltage
   across the resistor of a series RL from switch-on. Both are the same shape,
   $V(1 - e^{-t/\tau})$, with $\tau = RC$ in one case and $L/R$ in the other — which is
   the tidiest evidence you have that the electric and magnetic sides of this course
   are two halves of one subject.

Then put a comment at the top of `main.py` recording the plate area your
`design_capacitor` returned for a 1 nF capacitor with a 0.5 mm gap and $\varepsilon_r
= 4$, and the turn count `design_solenoid` returned for a 10 mH coil 10 cm long with a
2 cm² cross-section — with a sentence on whether either is a component you would
actually build.
''',
        "deliverables": [
            "`field_at` and `potential_at`, both by superposition over a list of point charges, with the field returned as a two-element NumPy array and the potential as a plain float.",
            "`flux_out_of_sphere`, computed from the enclosed charge by Gauss's law and not by integrating a field over a surface.",
            "`plate_capacitance` and `solenoid_inductance`, each straight from the geometry, and the two inverse functions `design_capacitor` and `design_solenoid` that hit a target exactly.",
            "`rc_voltage` and `rl_voltage`, the charging curves of the two circuits built in modules 3 and 4, agreeing with the time constants those exercises measured.",
            "A comment at the top of `main.py` giving the designed plate area and turn count, and a sentence on whether each is physically sensible.",
        ],
        "constraints": [
            "NumPy and the standard library only.",
            "`emconst.py` is read-only; import the constants from it rather than retyping them, so every function is using the same numbers.",
            "`flux_out_of_sphere` must not call `field_at`. The point of Gauss's law is that the field never has to be computed.",
            "The design functions must invert the forward functions algebraically. A search loop that gets close is not the same thing and will fail the round-trip checks.",
        ],
        "rubric": [
            {"criterion": "Fields and potentials", "weight": 30,
             "evidence": "Superposition is correct in both direction and magnitude: a single charge gives the textbook value, two equal charges cancel at their midpoint, and a dipole centre gives zero potential with a non-zero field."},
            {"criterion": "Gauss's law", "weight": 20,
             "evidence": "The flux depends only on the charge enclosed: it is unchanged by the radius of the surface, and a charge just outside contributes nothing."},
            {"criterion": "Geometry both ways", "weight": 30,
             "evidence": "Forward formulas scale correctly with area, gap, turns and length, and each design function is an exact inverse — its output fed back into the forward function reproduces the target to floating-point precision."},
            {"criterion": "Transients", "weight": 20,
             "evidence": "Both charging curves start at zero, reach 63.2% at one time constant and 95% at three, and reproduce the 1 ms and 159 µs measured in the two circuit exercises."},
        ],
        "hints": [
            "Every function here already exists in one of the four labs. The capstone is mostly assembly, so bring them across and make them agree on their constants.",
            "`design_capacitor` is `plate_capacitance` solved for the area: $A = C d / (\\varepsilon_0 \\varepsilon_r)$.",
            "`design_solenoid` needs a square root: $N = \\sqrt{L \\ell / (\\mu_0 A)}$.",
            "`rc_voltage` and `rl_voltage` differ only in how they build $\\tau$. Write one helper that takes a time constant and call it twice.",
            "At $t = 0$ both curves must return exactly zero — a capacitor cannot change its voltage instantly, and an inductor cannot change its current instantly.",
        ],
        "files": [
            {"name": "emconst.py", "ro": True, "content": r'''
"""Physical constants. Do not edit — the checks rely on these exact values."""

EPS0 = 8.8541878128e-12      # permittivity of free space, F/m
MU0 = 1.25663706212e-6       # permeability of free space, H/m
K = 8987551792.261171        # 1 / (4 pi eps0), N m^2 / C^2
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from emconst import EPS0, MU0, K

# Designed components:
#   1 nF capacitor, 0.5 mm gap, eps_r = 4  ->  plate area TODO m^2, and whether that is sensible
#   10 mH coil, 10 cm long, 2 cm^2 section ->  TODO turns, and whether that is sensible


def field_at(charges, point):
    """Electric field at `point` in V/m, as a numpy array [Ex, Ey]."""
    point = np.asarray(point, dtype=float)
    # TODO
    return np.zeros(2)


def potential_at(charges, point):
    """Electric potential at `point`, in volts."""
    # TODO
    return 0.0


def flux_out_of_sphere(charges, centre, radius):
    """Electric flux out of a sphere in V*m, by Gauss's law."""
    # TODO: enclosed charge only.
    return 0.0


def plate_capacitance(area, gap, eps_r=1.0):
    """Capacitance in farads of two parallel plates."""
    # TODO
    return 0.0


def solenoid_inductance(turns, length, area, mu_r=1.0):
    """Inductance in henries of a solenoid."""
    # TODO
    return 0.0


def design_capacitor(target_c, gap, eps_r=1.0):
    """Plate area in m^2 that gives `target_c` farads at this gap."""
    # TODO: invert plate_capacitance.
    return 0.0


def design_solenoid(target_l, length, area, mu_r=1.0):
    """Turn count that gives `target_l` henries for this coil shape."""
    # TODO: invert solenoid_inductance.
    return 0.0


def rc_voltage(v_source, r, c, t):
    """Capacitor voltage at time `t`, charging from rest through `r`."""
    # TODO
    return 0.0


def rl_voltage(v_source, l, r, t):
    """Resistor voltage at time `t` in a series RL, from switch-on."""
    # TODO
    return 0.0


if __name__ == "__main__":
    print("area for 1 nF:", design_capacitor(1e-9, 0.5e-3, 4.0), "m^2")
    print("turns for 10 mH:", design_solenoid(0.01, 0.1, 2e-4))
    print("RC at one time constant:", rc_voltage(5.0, 1000.0, 1e-6, 1e-3), "V")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from emconst import EPS0, MU0, K

# Designed components:
#   1 nF capacitor, 0.5 mm gap, eps_r = 4  ->  0.01412 m^2 of plate, about 12 cm square.
#       Buildable, but only just: this is why real 1 nF parts are rolled or stacked
#       rather than left as two flat plates in air.
#   10 mH coil, 10 cm long, 2 cm^2 section ->  1994.7 turns.
#       Perfectly ordinary for a wound air-cored coil, though the wire resistance that
#       comes with two thousand turns is what actually limits such a design.


def field_at(charges, point):
    """Electric field at `point` in V/m, as a numpy array [Ex, Ey]."""
    point = np.asarray(point, dtype=float)
    E = np.zeros(2)
    for q, sx, sy in charges:
        d = point - np.array([float(sx), float(sy)])
        r = float(np.hypot(d[0], d[1]))
        if r == 0.0:
            continue
        E = E + K * q * d / r ** 3
    return E


def potential_at(charges, point):
    """Electric potential at `point`, in volts."""
    point = np.asarray(point, dtype=float)
    total = 0.0
    for q, sx, sy in charges:
        r = float(np.hypot(point[0] - sx, point[1] - sy))
        if r == 0.0:
            continue
        total += K * q / r
    return float(total)


def flux_out_of_sphere(charges, centre, radius):
    """Electric flux out of a sphere in V*m, by Gauss's law."""
    centre = np.asarray(centre, dtype=float)
    enclosed = 0.0
    for q, sx, sy in charges:
        if float(np.hypot(sx - centre[0], sy - centre[1])) < radius:
            enclosed += q
    return float(enclosed / EPS0)


def plate_capacitance(area, gap, eps_r=1.0):
    """Capacitance in farads of two parallel plates."""
    return float(EPS0 * eps_r * area / gap)


def solenoid_inductance(turns, length, area, mu_r=1.0):
    """Inductance in henries of a solenoid."""
    return float(MU0 * mu_r * turns * turns * area / length)


def design_capacitor(target_c, gap, eps_r=1.0):
    """Plate area in m^2 that gives `target_c` farads at this gap."""
    return float(target_c * gap / (EPS0 * eps_r))


def design_solenoid(target_l, length, area, mu_r=1.0):
    """Turn count that gives `target_l` henries for this coil shape."""
    return float(np.sqrt(target_l * length / (MU0 * mu_r * area)))


def _rise(v_source, tau, t):
    """The shared charging curve: V(1 - exp(-t/tau))."""
    return float(v_source * (1.0 - np.exp(-t / tau)))


def rc_voltage(v_source, r, c, t):
    """Capacitor voltage at time `t`, charging from rest through `r`."""
    return _rise(v_source, r * c, t)


def rl_voltage(v_source, l, r, t):
    """Resistor voltage at time `t` in a series RL, from switch-on."""
    return _rise(v_source, l / r, t)


if __name__ == "__main__":
    print("area for 1 nF:", design_capacitor(1e-9, 0.5e-3, 4.0), "m^2")
    print("turns for 10 mH:", design_solenoid(0.01, 0.1, 2e-4))
    print("RC at one time constant:", rc_voltage(5.0, 1000.0, 1e-6, 1e-3), "V")
'''},
        ],
        "tests": [
            {"name": "the field superposes, in direction and in size", "code": r'''
import numpy as np
_E = np.asarray(field_at([(1e-9, 0.0, 0.0)], (0.1, 0.0)), dtype=float)
assert _E.shape == (2,), f"field_at should return two components, got shape {_E.shape}"
assert abs(_E[0] - 898.7551792261172) < 1e-6 and abs(_E[1]) < 1e-9, \
    f"expected 898.755 V/m along +x, got {_E.tolist()}"
_pair = np.asarray(field_at([(3e-9, -0.1, 0.0), (3e-9, 0.1, 0.0)], (0.0, 0.0)), dtype=float)
assert float(np.hypot(_pair[0], _pair[1])) < 1e-9, \
    f"two equal charges cancel at their midpoint, got {_pair.tolist()}"
'''},
            {"name": "potential is a scalar sum, and disagrees with the field", "code": r'''
import numpy as np
_v = potential_at([(2e-9, -0.05, 0.0), (-2e-9, 0.05, 0.0)], (0.0, 0.0))
assert abs(_v) < 1e-12, f"a dipole centre sits at zero potential, got {_v!r}"
_E = np.asarray(field_at([(2e-9, -0.05, 0.0), (-2e-9, 0.05, 0.0)], (0.0, 0.0)), dtype=float)
assert abs(_E[0] - 14380.082867617872) < 1e-6, \
    f"the field there is emphatically not zero: expected 14380.08 V/m, got {_E[0]!r}"
assert abs(potential_at([(1e-9, 0.0, 0.0)], (0.1, 0.0)) - 89.87551792261172) < 1e-9
'''},
            {"name": "flux sees only the enclosed charge", "code": r'''
_inside = flux_out_of_sphere([(1e-9, 0.0, 0.0)], (0.0, 0.0), 0.05)
assert abs(_inside - 112.94090673730192) < 1e-9, f"expected 1 nC / EPS0, got {_inside!r}"
_outside = flux_out_of_sphere([(1e-9, 0.5, 0.0)], (0.0, 0.0), 0.05)
assert abs(_outside) < 1e-12, f"a charge outside contributes no net flux, got {_outside!r}"
_wide = flux_out_of_sphere([(1e-9, 0.0, 0.0)], (0.0, 0.0), 0.40)
assert abs(_wide - _inside) < 1e-9, "growing the surface changes nothing while the charge stays inside"
'''},
            {"name": "the geometry formulas scale as they should", "code": r'''
_c = plate_capacitance(1e-4, 1e-4)
assert abs(_c - 8.8541878128e-12) < 1e-24, f"A/d = 1 gives eps0 exactly, got {_c!r}"
assert abs(plate_capacitance(1e-4, 2e-4) - _c / 2.0) < 1e-24, "doubling the gap halves C"
assert abs(plate_capacitance(1e-4, 1e-4, 4.0) - 4.0 * _c) < 1e-23, "eps_r = 4 quadruples C"
_l = solenoid_inductance(500, 0.2, 1e-4)
assert abs(_l - 0.000157079632765) < 1e-15, f"expected 157.08 uH, got {_l!r}"
assert abs(solenoid_inductance(1000, 0.2, 1e-4) - 4.0 * _l) < 1e-14, \
    "twice the turns is four times the inductance"
'''},
            {"name": "the design functions invert the geometry exactly", "code": r'''
_area = design_capacitor(1e-9, 0.5e-3, 4.0)
assert abs(_area - 0.01411761334216274) < 1e-12, f"expected 0.01412 m^2, got {_area!r}"
assert abs(plate_capacitance(_area, 0.5e-3, 4.0) - 1e-9) < 1e-21, \
    "feeding the designed area back in must return the 1 nF target"
_n = design_solenoid(0.01, 0.1, 2e-4)
assert abs(_n - 1994.7114014642273) < 1e-6, f"expected 1994.7 turns, got {_n!r}"
assert abs(solenoid_inductance(_n, 0.1, 2e-4) - 0.01) < 1e-15, \
    "feeding the designed turn count back in must return the 10 mH target"
'''},
            {"name": "the design functions are not hard-coded to those two targets", "code": r'''
_a2 = design_capacitor(4.7e-9, 1e-4, 1.0)
assert abs(plate_capacitance(_a2, 1e-4, 1.0) - 4.7e-9) < 1e-20, \
    "a different target must still round-trip"
_n2 = design_solenoid(2.2e-3, 0.05, 8e-4)
assert abs(solenoid_inductance(_n2, 0.05, 8e-4) - 2.2e-3) < 1e-15, \
    "a different coil must still round-trip"
assert _n2 < 1994.7114014642273, \
    "a smaller inductance on a fatter core needs fewer turns, not more"
'''},
            {"name": "both transients start at zero and hit 63.2% at one tau", "code": r'''
assert abs(rc_voltage(5.0, 1000.0, 1e-6, 0.0)) < 1e-15, \
    "a capacitor cannot change its voltage instantly, so v(0) is exactly 0"
assert abs(rl_voltage(5.0, 0.01, 62.8, 0.0)) < 1e-15, \
    "an inductor cannot change its current instantly, so the resistor starts at 0 V"
assert abs(rc_voltage(5.0, 1000.0, 1e-6, 1e-3) - 3.1606027941427883) < 1e-9, \
    "1 kohm and 1 uF reach 63.2% of 5 V at t = 1 ms"
assert abs(rl_voltage(5.0, 0.01, 62.8, 0.01 / 62.8) - 3.1606027941427883) < 1e-9, \
    "10 mH and 62.8 ohm reach the same 63.2% at t = L/R"
'''},
            {"name": "the two circuits from modules 3 and 4 agree with the toolkit", "code": r'''
_rc95 = rc_voltage(5.0, 1000.0, 1e-6, 3e-3)
assert abs(_rc95 / 5.0 - 0.950212931632136) < 1e-9, \
    f"three time constants is 95.02% of the way there, got {_rc95 / 5.0!r}"
_tau_rl = 0.01 / 62.8
assert abs(_tau_rl - 0.00015923566878980894) < 1e-15
_late = rl_voltage(5.0, 0.01, 62.8, 5.0 * _tau_rl)
assert _late > 4.9, f"after five time constants the RL is within 1% of the supply, got {_late!r}"
assert rl_voltage(5.0, 0.01, 62.8, 1e-6) < rl_voltage(5.0, 0.01, 62.8, 1e-5), \
    "the curve must be rising, not falling"
'''},
        ],
    },
}
