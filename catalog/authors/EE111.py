"""EE111 — Mathematics for Electrical Engineering.

A first-year course. It assumes school mathematics and nothing else: no prior
circuits, no prior programming beyond arithmetic. Every term is defined where it
first appears.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed; scipy is not
  * every expected number here was produced by running the code or the solver
"""

COURSE = {
    "id": "EE111",
    "title": "Mathematics for Electrical Engineering",
    "band": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python", "SymPy"],
    "credits": 10,
    "hours": 120,
    "icon": "◈",
    "summary": (
        "Electrical engineering is written in five pieces of mathematics: complex "
        "numbers, the exponential function, differentiation, integration, and "
        "simultaneous equations. This course teaches those five from the beginning "
        "and shows, in a working circuit simulator, what each one is for. Nothing is "
        "assumed beyond school algebra and trigonometry."
    ),
    "outcomes": [
        "Add, multiply, conjugate and divide complex numbers, and place them on the Argand plane.",
        "State Euler's identity and use a phasor to add sinusoids of the same frequency.",
        "Differentiate and integrate the exponentials and sinusoids that circuits produce, and apply i = C dv/dt.",
        "Solve a first-order differential equation, and recognise the time constant in a measured response.",
        "Write a set of simultaneous equations as a matrix and solve it.",
        "Convert a gain into decibels and back, and read a slope in decibels per decade off a response.",
        "Reduce a second-order circuit to $\\omega_n$ and $\\zeta$, and say from the components alone whether it will ring.",
        "Replace a curve by its tangent, estimate what that approximation costs, and iterate to an answer where algebra cannot reach one.",
        "Add, project and turn vectors in three dimensions with the dot and cross products.",
        "Use partial derivatives as sensitivities, and combine component tolerances both in the worst case and in quadrature.",
    ],
    "assessment": (
        "Ten quizzes; three circuits drawn and measured in the schematic editor; three "
        "design targets hit against a live model; four guided derivations, a symbol "
        "drill, a numeric question and a listing with holes in it; eight small Python "
        "labs; and a capstone that computes an RC network four different ways."
    ),
    "reading": [
        "*Engineering Mathematics*, Stroud — parts 1 and 2, for the algebra at exactly this level.",
        "*Mathematical Methods for Physics and Engineering*, Riley, Hobson & Bence — chapter 3 for complex numbers.",
        "*The Art of Electronics*, Horowitz & Hill — chapter 1, where complex impedance is put to work, once module 2 is done.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Complex numbers and the Argand plane",
            "summary": "A number with two parts, drawn as a point on a plane. Multiplying by j turns that point a quarter of the way round.",
            "concepts": [
                "The symbol $j$ is defined by one rule and one rule only: $j^2 = -1$. Engineers write $j$ rather than $i$ because $i$ is already the current.",
                "A complex number is $a + jb$: $a$ is the **real part**, $b$ is the **imaginary part**. Both are ordinary real numbers.",
                "The **Argand plane** draws $a + jb$ as the point $(a, b)$ — real part across, imaginary part up. Addition is then exactly vector addition.",
                "The **modulus** $|a + jb| = \\sqrt{a^2 + b^2}$ is the distance from the origin; the **argument** is the angle from the positive real axis, found with $\\arctan$ of $b/a$ in the right quadrant.",
                "The **conjugate** of $a + jb$ is $a - jb$: the same point reflected in the real axis. Multiplying a number by its own conjugate gives $a^2 + b^2$, a real number — which is how division is done.",
                "Multiplying by $j$ rotates a point a quarter turn anticlockwise and changes nothing else. That single fact is why complex numbers describe alternating current.",
            ],
            "read": [
                {
                    "title": "The number the real line has no room for",
                    "minutes": 12,
                    "body": r'''
A real number is a point on a line, and multiplying by a real number does exactly two
things to that point. It changes how far from zero the point sits, and it either
leaves it on the side it was already on or throws it across to the other side.
Multiplying by 3 stretches. Multiplying by $1/2$ pulls in. Multiplying by $-1$ moves
nothing at all except the side. There is no third move available, because a line has
only two directions.

Now ask a question that sounds like idle algebra and is not. Multiplying by $-1$ twice
returns you to where you started, so a flip is *half* of doing nothing. What, then, is
half of a flip? What could you multiply by twice, so that the two operations together
add up to one flip?

No point on the line will do it. Whatever the number is, if it is positive then
multiplying by it twice leaves you on the side you began on; if it is negative then
multiplying by it twice throws you across and back, and again you end up on the side
you began on. A flip does not. The operation being asked for cannot be multiplication
by any point of the line, because the line has nowhere to put it.

The way out is to stop insisting that it must be on the line. Give the operation a
name, state exactly what it does, and then check whether ordinary algebra survives
having it around.

## One rule, and everything after it is bookkeeping

$$j^2 = -1$$

That is the entire definition. $j$ is not a real number in disguise and it is not an
abbreviation for something you already had. It is a new object, introduced precisely
because no real number squares to a negative, carrying one rule that says what its
square is.

Engineers write $j$ where mathematicians write $i$, for the flattest of reasons: $i$
was already taken. It is the current, it appears in nearly every equation in this
course, and one letter cannot hold down both jobs.

A **complex number** is anything of the form $a + jb$, where $a$ and $b$ are ordinary
real numbers. $a$ is the **real part** and $b$ is the **imaginary part** — and note
carefully that the imaginary part is $b$, a real number, not $jb$. Both halves are
perfectly concrete quantities. The adjective is a seventeenth-century insult that
stuck.

From here on, treat $j$ as an algebraic symbol, exactly as you would treat $x$. Expand
brackets the way you always did. Collect like terms the way you always did. Apply the
one rule wherever a $j^2$ appears. That is the whole method, and there is nothing else
to learn about complex arithmetic — the rest of this unit is four consequences of it.

## Adding: two accounts kept separately

$$(a + jb) + (c + jd) = (a + c) + j(b + d)$$

Real parts with real parts, imaginary with imaginary. No $j^2$ can arise, because
nothing is multiplied, so addition never leaves the form $a + jb$ and never surprises
anybody. Subtraction is the same with the other sign.

It is worth stating explicitly for one reason: it makes complex numbers *closed* under
addition. Add two of them and what comes out is another one, not some third kind of
object needing its own rules. The same will turn out to be true of multiplication and
of division, and that closure is what makes it possible to build the rest of the
subject — impedance, transfer functions, the whole of frequency response — on top
without ever needing a fourth kind of number.

## Multiplying: expand in full, then use the rule once

Nothing new is required here, which is exactly the point. Multiply the brackets out
completely — all four products — and then go looking for $j^2$.

$$(a + jb)(c + jd) = ac + jad + jbc + j^2bd = (ac - bd) + j(ad + bc)$$

The minus sign in the real part is not a convention somebody chose. It is $j^2$ being
replaced by $-1$, and that substitution is the only place the rule was used.

### Worked: $(2 + 5j)(4 - 3j)$

```
first  :   2  *   4    =   8
outer  :   2  * (-3j)  =  -6j
inner  :  5j  *   4    = +20j
last   :  5j  * (-3j)  = -15 j^2   and   j^2 = -1,   so  = +15

real part      :    8 + 15  =  23
imaginary part :   -6 + 20  =  14

(2 + 5j)(4 - 3j) = 23 + 14j
```

Two features of that are worth staring at. The last product was $-15j^2$ and came back
*positive*: two sign changes, one from the $-3$ and one from the rule. And the real
part of the answer, 23, is larger than the product of the two real parts, which was 8.
That is not an arithmetic slip. It is the $j^2$ term feeding into the real column, and
it is the reason the next section exists.

## The mistake almost everybody makes once

The tempting move is to multiply part by part, the way addition works: $2 \times 4 = 8$
for the real part, $5 \times (-3) = -15$ for the imaginary part, giving $8 - 15j$.

It is tempting for two good reasons. Addition genuinely does work that way, so the
pattern has just been reinforced. And component-by-component multiplication is what
happens when you multiply two arrays in a program, which is the mental model most
people arrive with.

It is wrong because under multiplication the two parts are not separate accounts. $j$
times $j$ lands in the *real* column, so the imaginary parts of the inputs contribute
to the real part of the answer, and the real parts contribute to the imaginary part.
The four-product expansion is not a longer route to the same place; it is a different
operation. Compare the two results — $23 + 14j$ against $8 - 15j$ — and note that they
agree in neither part, not even in sign. If you take one habit away from this unit,
take this one: **multiplication mixes the parts; addition does not.**

## The conjugate, and the trick it makes possible

The **conjugate** of $z = a + jb$, written $\bar{z}$, is $a - jb$: the same real part,
the imaginary part negated.

On its own that looks like notation with no job to do. Multiply a number by its own
conjugate and the job appears:

$$(a + jb)(a - jb) = a^2 - jab + jab - j^2b^2 = a^2 + b^2$$

The two middle terms cancel exactly — they must, since they differ only in sign — and
the final term changes sign as it crosses into the real column. What is left contains
no $j$ at all. **A number times its own conjugate is always real, and always positive
unless the number was zero.** That single fact is the whole of complex division.

## Dividing: manufacture a real denominator

Nobody has any idea what it means to divide by $1 - 2j$ directly. But everybody knows
how to divide by a real number, and you have just seen how to turn any complex number
into a real one. So multiply the top and the bottom of the fraction by the conjugate of
the *bottom*. That is multiplying by 1, so it changes nothing about the value; what it
changes is the form.

### Worked: $\dfrac{3 + 4j}{1 - 2j}$

```
conjugate of the bottom :  1 + 2j

bottom :  (1 - 2j)(1 + 2j)  =  1^2 + 2^2   =  5      real, as promised

top    :  (3 + 4j)(1 + 2j)
          first  :   3 *  1   =   3
          outer  :   3 * 2j   =  +6j
          inner  :  4j *  1   =  +4j
          last   :  4j * 2j   =  +8 j^2  =  -8

          real       :   3 - 8   =  -5
          imaginary  :   6 + 4   = +10          top  =  -5 + 10j

result :  (-5 + 10j) / 5  =  -1 + 2j
```

Check it the way you would check any division — by multiplying the answer back by the
divisor and seeing whether the dividend reappears:

```
(-1 + 2j)(1 - 2j) =  -1 + 2j + 2j - 4 j^2
                  =  -1 + 4 + 4j
                  =   3 + 4j          the numerator we started from
```

### Worked: $\dfrac{1}{j}$

Small enough to do in your head once you have seen it done once, and it turns up
constantly.

```
conjugate of the bottom :  -j

1 / j  =  (1 * -j) / (j * -j)  =  -j / (-j^2)  =  -j / 1  =  -j
```

So $1/j = -j$. Dividing by $j$ and multiplying by $j$ do opposite things — which, after
the next unit, will read as *a quarter turn one way and a quarter turn the other*. It
also means that a $j$ in a denominator is never a reason to panic: move it upstairs and
change its sign.

## Where this stops working

**There is no "greater than".** $3 + 4j$ is neither larger nor smaller than $5 - 2j$.
Any attempt to order complex numbers consistently with their own arithmetic collapses
immediately: whichever side of zero you decide to put $j$ on, the usual rules force
$j^2$ to come out positive, and $j^2$ is $-1$. What gets compared instead is the
modulus, a real number and the subject of the next unit. Every time an engineer says
one complex quantity is bigger than another, that is what is meant.

**"The square root of $-1$" is a phrase to handle with care.** Both $j$ and $-j$ square
to $-1$, so the radical has no single value here, and the school rule
$\sqrt{a}\sqrt{b} = \sqrt{ab}$ stops holding: it would give
$\sqrt{-1}\,\sqrt{-1} = \sqrt{1} = 1$ when the answer is $-1$. Define $j$ by $j^2 = -1$
and use that definition; do not carry the radical sign around and expect it to behave.

**It does not extend to triples.** The obvious next move — invent a second symbol and
work with $a + jb + kc$ — cannot be made to work. There is no way to multiply triples
of real numbers that keeps all the ordinary rules of algebra. The next system that does
exist needs *four* components, and buys them by giving up something you have relied on
since primary school: for quaternions, $pq$ and $qp$ are different numbers.
Two-dimensional is not an arbitrary stopping point, it is the last place where
arithmetic still works the way you expect.

**And none of this yet says why a circuit should care.** Everything above is algebra:
a symbol, one rule, and its consequences. Nothing so far explains why an object with
two parts should have anything to do with a capacitor. That connection is geometric,
it is the subject of the next unit, and it rests entirely on what multiplication turns
out to do to a *picture*.
''',
                },
                {
                    "title": "The plane, and why multiplying turns things",
                    "minutes": 13,
                    "body": r'''
A complex number holds two independent real numbers, and anything holding two
independent real numbers can be drawn on a plane. Put the real part along the
horizontal axis and the imaginary part up the vertical one, and $a + jb$ becomes the
point $(a, b)$. Drawn that way the plane is called the **Argand plane**, and from this
point on it is worth thinking of a complex number as a point — or better, as the arrow
from the origin to that point — rather than as a piece of notation.

The picture immediately earns its keep. Addition, which was defined as separate
bookkeeping on the two parts, is exactly arrow addition: go along the first arrow, then
along the second, and where you end up is the sum. The parallelogram rule you may have
met for forces is the same rule, because it is the same arithmetic.

## Two numbers that describe the arrow instead of the point

Every arrow can be described in a second way: by how long it is and which way it
points.

The **modulus** $|z|$ is the length of the arrow, so it is Pythagoras and nothing else:

$$|a + jb| = \sqrt{a^2 + b^2}$$

It is a real number, it is never negative, and it is the answer to "how big is this
quantity" for something that has two parts. Note that squaring destroys the signs, so
$3 + 4j$, $3 - 4j$, $-3 + 4j$ and $-3 - 4j$ all have modulus 5.

The **argument** $\arg z$ is the angle from the positive real axis, measured
anticlockwise. Since $\tan(\text{angle}) = b/a$, it is tempting to write
$\arg z = \arctan(b/a)$ and move on. Do not: that formula throws away the information
you most need.

### Worked: putting $-3 + 4j$ into modulus-and-angle form

```
modulus  :  sqrt((-3)^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5

arctan(b/a) = arctan(4 / -3) = arctan(-1.3333) = -53.13 degrees      <-- wrong
```

That answer is wrong, and the picture says why in a second. The point $(-3, 4)$ is up
and to the left: second quadrant, so its angle must be somewhere between $90^\circ$ and
$180^\circ$. What $\arctan$ returned is the angle of $3 - 4j$, which is down and to the
right. The ratio $b/a$ is $-1.3333$ for both points, because a minus sign on the top and
a minus sign on the bottom give the same quotient, and $\arctan$ has no way to tell
which of the two it was handed.

```
the point is in the second quadrant, so add 180 degrees:

arg(-3 + 4j) = -53.13 + 180 = 126.87 degrees

check :  5 * cos(126.87 deg) = 5 * (-0.6) = -3     the real part
         5 * sin(126.87 deg) = 5 * ( 0.8) =  4     the imaginary part
```

This is why every programming language provides `atan2(b, a)`, which takes the two
parts separately and gets the quadrant right, and why the lab at the end of this module
insists on it. `atan(b / a)` cannot be fixed by care; it can only be patched afterwards
by looking at the signs, which is what `atan2` does for you.

Going the other way is easier and has no traps:

$$a = |z|\cos\theta \qquad b = |z|\sin\theta$$

so that any complex number can be written $z = |z|(\cos\theta + j\sin\theta)$. That form
is about to do all the work.

## What multiplication does to the picture

Take two numbers in that form, with moduli $r$ and $s$ and arguments $\theta$ and
$\phi$, and multiply them the only way you know how — expand, and use $j^2 = -1$:

$$r(\cos\theta + j\sin\theta)\cdot s(\cos\phi + j\sin\phi)$$

$$= rs\left[(\cos\theta\cos\phi - \sin\theta\sin\phi) + j(\cos\theta\sin\phi + \sin\theta\cos\phi)\right]$$

Look hard at the two brackets. They are the compound-angle formulas from school
trigonometry, sitting there fully assembled:
$\cos(\theta + \phi)$ in the first and $\sin(\theta + \phi)$ in the second. So

$$zw = rs\left[\cos(\theta + \phi) + j\sin(\theta + \phi)\right]$$

**Multiplying two complex numbers multiplies their lengths and adds their angles.**
Nothing was assumed to get there; it fell out of the four-product expansion and the
one rule. Division is the same statement backwards: divide the lengths, subtract the
angles.

That is the sentence the whole of alternating-current analysis is built on, and it is
worth pausing on how strange it is. An operation defined purely as symbol-pushing turns
out, when drawn, to be a rotation combined with a stretch. Two quite different kinds of
thing — turning and scaling — have been packed into a single multiplication.

### Worked: the same division, done both ways

In the previous unit, $\dfrac{3 + 4j}{1 - 2j}$ came out as $-1 + 2j$ by multiplying top
and bottom by the conjugate. Here it is again in lengths and angles.

```
3 + 4j :  modulus  sqrt(9 + 16)  = 5
          argument arctan(4/3)   = +53.130 deg    (first quadrant, arctan is safe here)

1 - 2j :  modulus  sqrt(1 + 4)   = sqrt(5) = 2.2361
          argument arctan(-2/1)  = -63.435 deg    (fourth quadrant, arctan is safe here)

divide  :  modulus  5 / 2.2361             = 2.2361  = sqrt(5)
           argument 53.130 - (-63.435)     = 116.565 deg

back to parts :  2.2361 * cos(116.565 deg) = 2.2361 * (-0.4472) = -1.000
                 2.2361 * sin(116.565 deg) = 2.2361 * ( 0.8944) = +2.000
```

$-1 + 2j$, the same answer. And as a check on the check, $|-1 + 2j| = \sqrt{1 + 4} =
\sqrt{5}$, which is what the length rule predicted, and its argument is
$180^\circ - 63.435^\circ = 116.565^\circ$, which is what the angle rule predicted.

Rectangular form is the one to use when adding. Modulus-and-angle form is the one to
use when multiplying, dividing, or raising to a power. Neither is more correct; they
are the same number, described for different jobs.

### Worked: $(1 + j)^8$

Try this by repeated expansion and you will be there for a while. In lengths and angles
it is two lines.

```
1 + j  :  modulus  sqrt(1 + 1) = sqrt(2) = 1.41421
          argument arctan(1/1) = 45 degrees

eighth power :  modulus   (sqrt(2))^8 = 2^4        = 16
                argument  8 * 45                   = 360 degrees

360 degrees is a whole turn, which is the same direction as 0 degrees:

(1 + j)^8 = 16 * (cos 0 + j sin 0) = 16          a real number
```

Worth confirming by hand, since the shortcut is the sort of thing that feels too easy:

```
(1 + j)^2 = 1 + 2j + j^2 = 2j
(2j)^2    = 4 j^2        = -4
(-4)^2    =                16
```

## Multiplying by $j$, which is the point of the whole exercise

$j$ itself is the point $(0, 1)$: modulus 1, argument $90^\circ$. By the rule just
derived, multiplying anything by $j$ leaves its length untouched and adds a quarter turn
anticlockwise. Check it against the algebra: $j(a + jb) = ja + j^2b = -b + ja$, so
$(a, b)$ becomes $(-b, a)$. Take $3 + j$, at $18.43^\circ$; multiplying by $j$ gives
$-1 + 3j$, at $108.43^\circ$. Exactly $90^\circ$ more, and both have modulus
$\sqrt{10}$.

Here is why that matters, two modules early. A sinusoid at a fixed frequency is
described entirely by an amplitude and a phase — a length and an angle. Differentiating
a sinusoid leaves the frequency alone, scales the amplitude, and shifts the phase by
exactly a quarter cycle. So does multiplying by $j$. Calculus on sinusoids and
multiplication by a complex number are the same operation wearing different clothes,
and that identification is what turns the differential equations of a circuit into
arithmetic. Module 2 makes it precise.

## Where this stops working

**Lengths and angles are useless for addition.** There is no rule that gets $|z + w|$
from $|z|$ and $|w|$. Concretely: $|3 + 4j| = 5$ and $|1 - 2j| = 2.236$, but their sum
is $4 + 2j$, whose modulus is $\sqrt{20} = 4.472$ — not $7.236$, and not any other
combination of the two. Moduli only add when the two arrows point the same way; the
general statement is the triangle inequality, $|z + w| \le |z| + |w|$. To add, convert
back to real and imaginary parts.

**The argument is only defined up to whole turns.** $126.87^\circ$ and $486.87^\circ$
name the same direction, and both are correct. Mostly this is harmless, but it bites in
one place: the power rule $\arg(z^n) = n\arg z$ is only true modulo a full turn, and its
inverse genuinely has several answers. $(1 + j)^8 = 16$ above, but $1 + j$ is not the
only eighth root of 16 — there are eight of them, spaced $45^\circ$ apart around a
circle of radius $\sqrt{2}$. A calculator's square-root key hands you one of two and
says nothing about the other.

**Zero has no argument at all.** $|0| = 0$, which is fine, but an arrow of zero length
points nowhere, so $\arg 0$ is undefined. Most languages have `atan2(0, 0)` return 0,
which is a convenience rather than a fact; if a phase comes back as exactly zero from a
signal that was not there, that is what happened.

**And a phase is only meaningful against a reference.** The argument of a single
complex number in isolation depends on where you started measuring, in the same way
that the voltage at a node depends on where you put ground. What is physically real is
the *difference* between two arguments — which is why the answer to the build unit in
module 2 is quoted as a lag of $45^\circ$ relative to the input, and never as an angle
on its own.
''',
                },
            ],
            "sandbox": {
                "title": "Multiplying by j, drawn as motion",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": 0, "a12": -1, "a21": 1, "a22": 0},
                "brief": r'''
Take the horizontal axis to be the real part of a complex number and the vertical
axis to be the imaginary part. That is the Argand plane.

The four sliders set a matrix that turns a point into a velocity. The short strokes
point along that velocity — they are all drawn the same length, so they show the
direction and not the speed — and the coloured curves are the paths that follow it
from eight starting points around a circle.

The matrix it opens with is $\begin{bmatrix} 0 & -1 \\ 1 & 0\end{bmatrix}$, which
sends the point $(a, b)$ to $(-b, a)$ — and $(-b, a)$ is exactly $j$ times $a + jb$.
So the picture on screen is what "multiply by $j$" does, applied over and over.
''',
                "notice": [
                    "The eight curves are circles about the origin. Multiplying by $j$ never changes the modulus, only the angle — so a point can only ever go round. (The drawing steps forward in small jumps, so the circles creep outwards by about a tenth of their radius over the run; that is the drawing's arithmetic, not the mathematics.)",
                    "Set $a_{11}$ and $a_{22}$ both to $-0.3$ and leave the other two alone. The circles become inward spirals, and the readout under the plot changes to *stable spiral*. Rotation plus shrinking is what a decaying oscillation looks like — hold on to this picture, it returns in module 2.",
                    "Now set $a_{11}$ and $a_{22}$ both to $+0.3$. The spirals run outwards instead, past the edge of the plot and off the panel, where the drawing gives up on each curve in turn. Same rotation, opposite growth.",
                    "Set $a_{12}$ to $+1$ so both off-diagonal entries are $+1$. The readout says *saddle*: the paths no longer go round at all. Rotation needed that minus sign — one entry, and the whole character of the picture changes.",
                ],
            },
            "quiz": {
                "title": "Does the definition hold up",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is $j^2$?",
                        "opts": ["$1$", "$j$", "$-1$", "$0$"],
                        "a": 2,
                        "why": (
                            "This is the definition, not a result: $j$ is *introduced* as a thing whose square is $-1$, "
                            "because no real number has that property. Everything else about complex numbers follows "
                            "from ordinary algebra plus this one substitution. A common slip is $j^2 = j$, which would "
                            "make $j$ equal to 0 or 1 and leave nothing new."
                        ),
                    },
                    {
                        "q": "What is $(3 + 4j) + (1 - 2j)$?",
                        "opts": ["$4 + 6j$", "$4 + 2j$", "$4 - 8j$", "$3 - 8j$"],
                        "a": 1,
                        "why": (
                            "Add the real parts and add the imaginary parts, separately: $3 + 1 = 4$ and $4 + (-2) = 2$. "
                            "Nothing multiplies, so $j^2$ never appears. On the Argand plane this is the parallelogram "
                            "rule — the same addition you would do with two arrows."
                        ),
                    },
                    {
                        "q": "What is $|3 + 4j|$, the modulus?",
                        "opts": ["$7$", "$25$", "$12$", "$5$"],
                        "a": 3,
                        "why": (
                            "The modulus is the distance from the origin to the point $(3, 4)$, so it is Pythagoras: "
                            "$\\sqrt{3^2 + 4^2} = \\sqrt{25} = 5$. Two frequent errors are adding the parts to get 7, "
                            "and stopping at $3^2 + 4^2 = 25$ without taking the square root."
                        ),
                    },
                    {
                        "q": "What is the conjugate of $2 - 5j$?",
                        "opts": ["$-2 + 5j$", "$2 + 5j$", "$-2 - 5j$", "$5 - 2j$"],
                        "a": 1,
                        "why": (
                            "Conjugating flips the sign of the imaginary part and leaves the real part alone: the point "
                            "is reflected in the horizontal axis. It does not negate the whole number, and it does not "
                            "swap the two parts over."
                        ),
                    },
                    {
                        "q": "On the Argand plane, what does multiplying a number by $j$ do to it?",
                        "opts": [
                            "Doubles its distance from the origin",
                            "Reflects it in the real axis",
                            "Turns it a quarter turn anticlockwise about the origin",
                            "Moves it one unit upwards",
                        ],
                        "a": 2,
                        "why": (
                            "Check it on a case: $j(a + jb) = ja + j^2 b = -b + ja$, so $(a, b)$ becomes $(-b, a)$. "
                            "Draw those two points and the angle between them is 90 degrees, with the distance from the "
                            "origin unchanged. Reflection in the real axis is conjugation, a different operation; and "
                            "*adding* $j$, not multiplying, is what moves a point one unit up."
                        ),
                    },
                    {
                        "q": "What is $(2 + 3j)(2 - 3j)$?",
                        "opts": ["$4 - 9j$", "$4 + 9j$", "$13j$", "$13$"],
                        "a": 3,
                        "why": (
                            "Expand: $4 - 6j + 6j - 9j^2$. The two middle terms cancel, and $-9j^2 = +9$, leaving $13$ "
                            "with no imaginary part at all. A number times its own conjugate is always real and equal "
                            "to the modulus squared — which is exactly why you multiply top and bottom by the "
                            "conjugate when dividing."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "The seven lines the rest of the course rests on",
                "minutes": 9,
                "caption": "a and b, c and d are ordinary real numbers throughout",
                "lang": "text",
                "brief": r'''
Nothing is executed here. Each line is one of the rules from the reading, with the
right-hand side removed — and every one of them is a consequence of $j^2 = -1$ and
ordinary algebra, so if you can reconstruct the expansion you can reconstruct the line.

`conj` means the conjugate, `*` is multiplication, `**` is a power and `sqrt` is a
square root, as in Python.
''',
                "listing": """j * j                      =  ___

(a + jb) + (c + jd)        =  (a + c) + j___

(a + jb) * (c + jd)        =  ___ + j(a*d + b*c)

conj(a + jb)               =  ___

(a + jb) * conj(a + jb)    =  ___

|a + jb|                   =  ___

1 / j                      =  ___
""",
                "blanks": [
                    {
                        "prompt": "The definition itself.",
                        "hole": "?",
                        "opts": ["-1", "1", "j", "0"],
                        "a": 0,
                        "why": "This is not derived from anything — it is the rule $j$ was introduced to obey, because no real number squares to a negative. Every other line below is this one plus ordinary algebra.",
                        "whys": [
                            "This is not derived from anything — it is the rule $j$ was introduced to obey, because no real number squares to a negative. Every other line below is this one plus ordinary algebra.",
                            "If $j^2$ were $+1$ then $j$ would be $\\pm 1$, an ordinary real number, and nothing new would have been introduced at all.",
                            "$j^2 = j$ forces $j$ to be 0 or 1 — divide both sides by $j$ — so again nothing new. A squaring must produce something that is not the thing you squared.",
                            "$j^2 = 0$ would make $j$ zero. There would then be no second dimension to draw anything on.",
                        ],
                    },
                    {
                        "prompt": "The imaginary part of a sum.",
                        "hole": "?",
                        "opts": ["(b * d)", "(a + c)", "(b + d)", "(b - d)"],
                        "a": 2,
                        "why": "Addition keeps the two parts in separate accounts: real with real, imaginary with imaginary. Nothing is multiplied, so no $j^2$ can appear and nothing crosses over.",
                        "whys": [
                            "Multiplying the imaginary parts is what happens inside a *product*, and even there the result lands in the real column, not this one.",
                            "That is the real part of the sum, already written to the left of the $j$. Reusing it here would drop the imaginary information entirely.",
                            "Addition keeps the two parts in separate accounts: real with real, imaginary with imaginary. Nothing is multiplied, so no $j^2$ can appear and nothing crosses over.",
                            "Subtraction is a different operation. $(a + jb) - (c + jd)$ would give $b - d$; the line as written is a sum.",
                        ],
                    },
                    {
                        "prompt": "The real part of a product.",
                        "hole": "?",
                        "opts": ["a*c + b*d", "a*c - b*d", "a*c", "(a + b)*(c + d)"],
                        "a": 1,
                        "why": "Expanding gives $ac + jad + jbc + j^2bd$, and the last term is where the rule bites: $j^2bd$ becomes $-bd$ and lands in the real column. The minus sign is $j^2 = -1$ and nothing else.",
                        "whys": [
                            "This is the expansion with $j^2$ left as $+1$. The whole point of the definition is that it is $-1$, which is what puts the minus sign there.",
                            "Expanding gives $ac + jad + jbc + j^2bd$, and the last term is where the rule bites: $j^2bd$ becomes $-bd$ and lands in the real column. The minus sign is $j^2 = -1$ and nothing else.",
                            "This is multiplication done part by part — the most common error with complex numbers. It ignores that $j$ times $j$ produces a real contribution, so the imaginary parts must appear in the real answer.",
                            "That would be the product of the sums of the parts, which mixes real and imaginary quantities that are not comparable. Expand the original brackets instead and keep track of which column each term lands in.",
                        ],
                    },
                    {
                        "prompt": "The conjugate.",
                        "hole": "?",
                        "opts": ["a - jb", "-a + jb", "-a - jb", "b + ja"],
                        "a": 0,
                        "why": "Conjugating negates the imaginary part and leaves the real part alone: on the Argand plane it reflects the point in the horizontal axis. The modulus is therefore unchanged, and the argument changes sign.",
                        "whys": [
                            "Conjugating negates the imaginary part and leaves the real part alone: on the Argand plane it reflects the point in the horizontal axis. The modulus is therefore unchanged, and the argument changes sign.",
                            "This negates the wrong half. It is a reflection in the *vertical* axis, which is a different operation and does not make $z\\bar{z}$ real.",
                            "Negating both parts is multiplying by $-1$ — a half turn, not a reflection. It would leave $z \\times (-z) = -(a^2 - b^2 + 2jab)$, still complex.",
                            "Swapping the parts over is reflection in the diagonal line $b = a$. Nothing in this course wants that, and it would not produce a real product either.",
                        ],
                    },
                    {
                        "prompt": "A number times its own conjugate.",
                        "hole": "?",
                        "opts": ["a**2 - b**2", "a**2 + b**2", "a + b", "0"],
                        "a": 1,
                        "why": "$(a + jb)(a - jb) = a^2 - jab + jab - j^2b^2$. The middle terms cancel exactly and the last one changes sign, leaving $a^2 + b^2$ — real, non-negative, and equal to $|z|^2$. This is the fact that makes division possible.",
                        "whys": [
                            "That is the difference of two squares as it would be for real numbers, but $-j^2b^2$ is $+b^2$, not $-b^2$. The sign flip is exactly what the definition supplies.",
                            "$(a + jb)(a - jb) = a^2 - jab + jab - j^2b^2$. The middle terms cancel exactly and the last one changes sign, leaving $a^2 + b^2$ — real, non-negative, and equal to $|z|^2$. This is the fact that makes division possible.",
                            "Both parts are squared by this product, so a sum of the parts themselves cannot be right — try $a = 3$, $b = 4$ and the product is 25, not 7.",
                            "The product is zero only when $z$ itself is zero. For anything else it is a positive real number, which is precisely why it can be used as a denominator.",
                        ],
                    },
                    {
                        "prompt": "The modulus — the distance from the origin.",
                        "hole": "?",
                        "opts": ["a**2 + b**2", "sqrt(a**2 - b**2)", "a + b", "sqrt(a**2 + b**2)"],
                        "a": 3,
                        "why": "The point sits at $(a, b)$, so its distance from the origin is Pythagoras. Note the relationship to the line above: $|z|^2 = z\\bar{z}$, which is often the more useful form because it has no square root in it.",
                        "whys": [
                            "That is the modulus *squared*. It is a useful quantity in its own right — it is $z\\bar{z}$ — but it is not a distance; $|3 + 4j|$ is 5, not 25.",
                            "A minus sign under the root would make the modulus of $3 + 4j$ imaginary. Distances are added in quadrature, never subtracted.",
                            "Adding the parts gives 7 for $3 + 4j$, which is the distance you would travel going along and then up rather than straight there.",
                            "The point sits at $(a, b)$, so its distance from the origin is Pythagoras. Note the relationship to the line above: $|z|^2 = z\\bar{z}$, which is often the more useful form because it has no square root in it.",
                        ],
                    },
                    {
                        "prompt": "One over j.",
                        "hole": "?",
                        "opts": ["j", "-j", "1", "-1"],
                        "a": 1,
                        "why": "Multiply top and bottom by the conjugate of $j$, which is $-j$: $\\frac{1}{j} = \\frac{-j}{-j^2} = \\frac{-j}{1} = -j$. Geometrically, multiplying by $j$ is a quarter turn one way, so dividing by it must be a quarter turn the other.",
                        "whys": [
                            "That would say $j$ is its own reciprocal, so $j \\times j = 1$. It is $-1$. This is the sign slip to watch for whenever a $j$ moves out of a denominator.",
                            "Multiply top and bottom by the conjugate of $j$, which is $-j$: $\\frac{1}{j} = \\frac{-j}{-j^2} = \\frac{-j}{1} = -j$. Geometrically, multiplying by $j$ is a quarter turn one way, so dividing by it must be a quarter turn the other.",
                            "A reciprocal that came out real would mean $j$ was real. Check it: $j \\times 1 = j$, not 1.",
                            "$-1$ is $j^2$, not $1/j$. Multiply your answer by $j$ and see whether you get 1 back — that is the test for any reciprocal.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "How big is it",
                    "minutes": 4,
                    "brief": r'''
The modulus is the distance from the origin to the point on the Argand plane, so it is
Pythagoras and nothing else. It is a real number, it is never negative, and it is what
"how big" means for a quantity that arrives in two parts.
''',
                    "prompt": r"What is $|z|$?",
                    "note": "One rule, one step. Give a plain number: the modulus carries no $j$.",
                    "figure": r"""
$$z = 7 - 24j$$

The imaginary part is negative, so the point sits below the real axis, at $(7, -24)$
on the Argand plane — a long way down and a little to the right.
""",
                    "given": [
                        {"label": "Real part", "value": "7"},
                        {"label": "Imaginary part", "value": "-24"},
                    ],
                    "answer": 25,
                    "tol": 0.05,
                    "hint": r"$|a + jb| = \sqrt{a^2 + b^2}$. Both parts are squared, so the sign of the imaginary part cannot survive into the answer.",
                    "wrong": r"If the answer came out negative, the $-24$ was carried through as a negative: squaring destroys the sign, since $(-24)^2 = +576$, and a distance can never be negative. If it came out as 625, the square root was left off — $a^2 + b^2$ is the modulus *squared*, not the modulus.",
                    "why": r"$\sqrt{7^2 + 24^2} = \sqrt{49 + 576} = \sqrt{625} = 25$. The point $(7, -24)$ lies 25 units from the origin, in the fourth quadrant. It comes out whole because 7, 24, 25 is a Pythagorean triple; most moduli are not so obliging, and $|1 + j| = \sqrt{2}$ is the more typical case.",
                    "aside": "The conjugate $7 + 24j$, and $-7 \\pm 24j$ too, all have exactly this modulus. Four points, one distance.",
                },
                {
                    "title": "One part of a product",
                    "minutes": 6,
                    "brief": r'''
Multiplication is the four-product expansion followed by one substitution. The question
asks for the real part only, but there is no shortcut to it: the real part of the answer
depends on the imaginary parts of both inputs.
''',
                    "prompt": r"What is the real part of $z_1 z_2$?",
                    "note": "Expand all four products before collecting anything. Give a plain number.",
                    "figure": r"""
$$z_1 = 2 + 5j \qquad z_2 = 4 - 3j$$

Neither number is real and neither is purely imaginary, so all four products in the
expansion are non-zero and every one of them matters.
""",
                    "given": [
                        {"label": "z1", "value": "2 + 5j"},
                        {"label": "z2", "value": "4 - 3j"},
                        {"label": "Asked for", "value": "the real part only"},
                    ],
                    "answer": 23,
                    "tol": 0.05,
                    "hint": r"$(a + jb)(c + jd) = (ac - bd) + j(ad + bc)$. Here $b = 5$ and $d = -3$, so watch what happens to the sign of $bd$.",
                    "wrong": r"If you got $-7$, the last product went in as $-15$: $5j \times (-3j) = -15j^2$, and replacing $j^2$ by $-1$ turns that into $+15$. If you got 8, only the real parts were multiplied — that is the part-by-part error, and it ignores the fact that $j$ times $j$ contributes to the real column.",
                    "why": r"The four products are $2\times4 = 8$, $2\times(-3j) = -6j$, $5j\times4 = 20j$ and $5j\times(-3j) = -15j^2 = +15$. Collecting: real $8 + 15 = 23$, imaginary $-6 + 20 = 14$, so $z_1z_2 = 23 + 14j$. The real part, 23, is nearly three times the product of the two real parts, which is the clearest possible demonstration that the parts do not multiply separately.",
                    "aside": "As a check on the size, $|z_1| = \\sqrt{29} = 5.385$ and $|z_2| = 5$, so $|z_1z_2|$ must be $26.93$ — and $\\sqrt{23^2 + 14^2} = \\sqrt{725} = 26.93$.",
                },
                {
                    "title": "The angle of a quotient",
                    "minutes": 8,
                    "brief": r'''
Two routes lead to the same place. You can divide first — multiply top and bottom by the
conjugate of the bottom — and then take the argument of what comes out; or you can take
both arguments and subtract, since dividing subtracts angles. Doing it both ways is a
good use of five minutes.
''',
                    "prompt": r"What is $\arg(z_1/z_2)$, in degrees, measured anticlockwise from the positive real axis?",
                    "note": "Answer in degrees, in the range $0^\\circ$ to $360^\\circ$. Two decimal places is ample.",
                    "figure": r"""
$$z_1 = 3 + 4j \qquad z_2 = 1 - 2j$$

$z_1$ is in the first quadrant and $z_2$ is in the fourth. Sketching both arrows before
starting is worth the ten seconds it costs — the quadrant of the answer is the thing
most easily got wrong here.
""",
                    "given": [
                        {"label": "z1", "value": "3 + 4j"},
                        {"label": "z2", "value": "1 - 2j"},
                        {"label": "Answer in", "value": "degrees, 0 to 360"},
                    ],
                    "answer": 116.57,
                    "tol": 0.2,
                    "unit": "degrees",
                    "hint": r"Multiplying top and bottom by $1 + 2j$ makes the denominator $1^2 + 2^2 = 5$. Once you have the quotient as $a + jb$, look at the signs of $a$ and $b$ to decide the quadrant before reaching for $\arctan$.",
                    "wrong": r"$-63.4^\circ$ is what $\arctan(b/a)$ reports for the quotient $-1 + 2j$, because $2/(-1)$ and $(-2)/1$ are the same ratio and $\arctan$ cannot tell them apart. The point is up and to the left, so the angle is in the second quadrant: add $180^\circ$.",
                    "why": r"Dividing: $\dfrac{(3+4j)(1+2j)}{(1-2j)(1+2j)} = \dfrac{-5 + 10j}{5} = -1 + 2j$. That point is in the second quadrant, so $\arg = 180^\circ - \arctan(2/1) = 180^\circ - 63.435^\circ = 116.565^\circ$. By the other route, $\arg z_1 = 53.130^\circ$ and $\arg z_2 = -63.435^\circ$, and $53.130 - (-63.435) = 116.565^\circ$ — the same number, reached without ever forming the quotient.",
                    "aside": "The moduli confirm it too: $5/\\sqrt{5} = \\sqrt{5}$, and $|-1 + 2j| = \\sqrt{5}$.",
                },
                {
                    "title": "Three operations, one modulus",
                    "minutes": 10,
                    "brief": r'''
Now several steps with nothing signposted. There is a division that needs a conjugate, a
reciprocal of $j$ that does not, an addition that must be done in rectangular form, and
a modulus at the end. Do them in that order and each step is one you have already done.
''',
                    "prompt": r"What is $|z|$?",
                    "note": "Give the answer to three decimal places.",
                    "figure": r"""
$$z = \frac{2 + j}{1 - j} + \frac{3}{j}$$

The two terms have to be brought to $a + jb$ form separately before they can be added —
there is no rule that combines moduli under addition.
""",
                    "given": [
                        {"label": "First term", "value": "(2 + j) / (1 - j)"},
                        {"label": "Second term", "value": "3 / j"},
                        {"label": "Asked for", "value": "the modulus of the sum"},
                    ],
                    "answer": 1.581,
                    "tol": 0.005,
                    "hint": r"For the first term multiply top and bottom by $1 + j$, which makes the denominator $1^2 + 1^2 = 2$. For the second, use $1/j = -j$ from the reading rather than a conjugate — it is quicker and it is the same result.",
                    "wrong": r"If you got 4.528, the second term came out as $+3j$. $1/j$ is $-j$, not $+j$: multiply $j$ by each candidate and see which gives 1. If you got 4.581, the two moduli were taken separately and added — $|z + w|$ is never $|z| + |w|$ unless the two point the same way, and here they very much do not.",
                    "why": r"First term: $\dfrac{(2+j)(1+j)}{(1-j)(1+j)} = \dfrac{1 + 3j}{2} = 0.5 + 1.5j$, since $(2+j)(1+j) = 2 + 2j + j - 1$. Second term: $3/j = 3 \times (-j) = -3j$. Adding, $z = 0.5 + 1.5j - 3j = 0.5 - 1.5j$. Then $|z| = \sqrt{0.25 + 2.25} = \sqrt{2.5} = 1.5811$. Notice that the two terms nearly cancelled in the imaginary direction and the real part survived untouched — which is why the parts had to be recovered before adding.",
                    "aside": "Worth noticing why the first term also has modulus 1.581: subtracting $3j$ took its imaginary part from $+1.5$ to $-1.5$, so the sum is the first term's own conjugate. A reflection in the real axis cannot change a distance.",
                },
                {
                    "title": "Choosing a value to kill the real part",
                    "minutes": 10,
                    "brief": r'''
Everything so far has been evaluation: numbers in, number out. This one runs the other
way. A condition on the *answer* is stated, and the question is what the input must have
been — which is the shape almost every design problem in engineering takes.

"Purely imaginary" means the real part is zero and the imaginary part is not.
''',
                    "prompt": r"For what real value of $k$ is the product $(3 + kj)(2 - j)$ purely imaginary?",
                    "note": "$k$ is a real number and may be negative. Give it to two decimal places.",
                    "figure": r"""
$$(3 + kj)(2 - j) = \text{something purely imaginary}$$

$k$ is unknown, so carry it through the expansion as an ordinary algebraic symbol. It
sits on an imaginary part, so wherever it meets the $-j$ it will cross into the real
column and bring a sign change with it.
""",
                    "given": [
                        {"label": "First factor", "value": "3 + kj"},
                        {"label": "Second factor", "value": "2 - j"},
                        {"label": "Condition", "value": "the product has zero real part"},
                    ],
                    "answer": -6,
                    "tol": 0.02,
                    "hint": r"Expand into the form $(\text{real}) + j(\text{imaginary})$ with $k$ inside both brackets, then set the real bracket to zero. It is one linear equation.",
                    "wrong": r"If you got 1.5, the wrong bracket was set to zero: $2k - 3 = 0$ kills the *imaginary* part and leaves the product purely real, at $7.5$. Read the condition again — it is the real part that must vanish.",
                    "why": r"Expanding: $3\times2 = 6$, $3\times(-j) = -3j$, $kj\times2 = 2kj$, and $kj\times(-j) = -kj^2 = +k$. So the product is $(6 + k) + j(2k - 3)$. Purely imaginary means $6 + k = 0$, hence $k = -6$. Checking: $(3 - 6j)(2 - j) = 6 - 3j - 12j + 6j^2 = 6 - 6 - 15j = -15j$, which has no real part and a non-zero imaginary one. Note where the $k$ entered the real bracket — it arrived from the product of the two *imaginary* parts, which is the whole reason a purely imaginary factor can cancel a real one.",
                    "aside": "Geometrically it is an angle statement. Multiplication adds arguments, $\\arg(2 - j) = -26.57^\\circ$, and a purely imaginary number sits at $\\pm 90^\\circ$ — so $3 + kj$ has to be at $-63.43^\\circ$, which is exactly $\\arctan(-6/3)$.",
                },
            ],
            "derive": {
                "title": "The division rule, built from the conjugate",
                "minutes": 14,
                "vars": ["a", "b", "c", "d", "j"],
                "brief": r'''
Dividing by $c + jd$ has no meaning on its own. The way through is to turn the
denominator into a real number, which the conjugate does for free, and then divide the
two parts by it separately.

$$\frac{a + jb}{c + jd} \times \frac{c - jd}{c - jd}$$

Multiplying by that second fraction is multiplying by 1, so nothing about the value
changes — only the form. Work out what the two ends of it come to. Assume $c$ and $d$
are not both zero.
''',
                "steps": [
                    {
                        "prompt": r"Multiply out the new denominator, $(c + jd)(c - jd)$, and write what is left. It should contain no $j$.",
                        "answer": r"c^2 + d^2",
                        "placeholder": r"a sum of two squares",
                        "hint": r"The two cross terms are $-jcd$ and $+jcd$, which cancel. The remaining term is $-j^2d^2$, and $j^2 = -1$.",
                        "deconstruct": [
                            r"$(c + jd)(c - jd) = c^2 - jcd + jcd - j^2d^2$.",
                            r"The middle terms differ only in sign, so they cancel exactly.",
                            r"$-j^2d^2 = +d^2$, leaving a real, non-negative number.",
                        ],
                    },
                    {
                        "prompt": r"Now expand the numerator $(a + jb)(c - jd)$ and write its real part, in terms of $a$, $b$, $c$ and $d$.",
                        "answer": r"a c + b d",
                        "hint": r"Two of the four products are real: the one with no $j$ in it, and the one with $j$ twice.",
                        "deconstruct": [
                            r"The four products are $ac$, $-jad$, $+jbc$ and $-j^2bd$.",
                            r"$-j^2bd = +bd$, which joins $ac$ in the real column.",
                        ],
                    },
                    {
                        "prompt": r"Write the imaginary part of that same numerator — the coefficient of $j$, without the $j$ itself.",
                        "answer": r"b c - a d",
                        "hint": r"The two terms carrying a single $j$ are $-jad$ and $+jbc$. Collect them.",
                        "deconstruct": [
                            r"$-jad + jbc = j(bc - ad)$.",
                            r"The coefficient asked for is what sits inside that bracket.",
                        ],
                    },
                    {
                        "prompt": r"Put $a = 1$ and $b = 0$, so the fraction is $1/(c + jd)$. Write the imaginary part of the result — remember the denominator from the first step.",
                        "answer": r"\frac{-d}{c^2 + d^2}",
                        "placeholder": r"a fraction with a minus sign on top",
                        "hint": r"Substitute into $\dfrac{bc - ad}{c^2 + d^2}$. With $b = 0$ the first term of the numerator disappears.",
                        "deconstruct": [
                            r"The imaginary part in general is $\dfrac{bc - ad}{c^2 + d^2}$.",
                            r"With $a = 1$ and $b = 0$ the numerator becomes $0 \times c - 1 \times d = -d$.",
                        ],
                    },
                    {
                        "prompt": r"Finally, the modulus. Write $\left|\dfrac{a + jb}{c + jd}\right|^2$ — the modulus squared — in terms of $a$, $b$, $c$ and $d$.",
                        "answer": r"\frac{a^2 + b^2}{c^2 + d^2}",
                        "placeholder": r"one sum of squares over another",
                        "hint": r"Square and add the two parts you found, over the squared denominator. The numerator collapses: $(ac + bd)^2 + (bc - ad)^2 = (a^2 + b^2)(c^2 + d^2)$.",
                        "deconstruct": [
                            r"$|z|^2$ is the sum of the squares of the two parts, so it is $\dfrac{(ac+bd)^2 + (bc-ad)^2}{(c^2+d^2)^2}$.",
                            r"Expanding the top, the $2abcd$ terms cancel and what remains is $a^2c^2 + a^2d^2 + b^2c^2 + b^2d^2 = (a^2+b^2)(c^2+d^2)$.",
                            r"One factor of $c^2 + d^2$ then cancels against the denominator.",
                        ],
                    },
                ],
                "closing": r'''
The general rule, assembled:

$$\frac{a + jb}{c + jd} = \frac{ac + bd}{c^2 + d^2} + j\,\frac{bc - ad}{c^2 + d^2}$$

Nobody memorises that, and nobody needs to — the conjugate trick reproduces it in three
lines whenever it is wanted. What is worth keeping is the two things it tells you.

First, the special cases fall straight out. Put $a = 1$, $b = 0$, $c = 0$, $d = 1$ and
you get $1/j = 0 - j$, the result from the reading. Put $a = 3$, $b = 4$, $c = 1$,
$d = -2$ and you get $\frac{3 - 8}{5} + j\frac{4 + 6}{5} = -1 + 2j$, which is the worked
example, arrived at without expanding anything.

Second, the last step is the more useful half. $|z/w|^2 = |z|^2/|w|^2$, so moduli simply
divide — and that is the statement doing the work every time a gain is computed in
module 5, where a transfer function is a ratio of two complex numbers and only its size
is wanted. The parts can be left alone entirely.
''',
            },
            "lab": {
                "title": "Complex arithmetic, built from nothing",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Python has complex numbers built in. You are going to write them yourself once, so
that nothing about them is magic afterwards.

A complex number here is an ordinary pair of floats: the tuple `(a, b)` means
$a + jb$. Fill in the six functions in `main.py`:

- `add(x, y)` and `mul(x, y)` — the arithmetic. For `mul`, expand the brackets and
  replace $j^2$ with $-1$.
- `conj(x)` — flip the sign of the imaginary part.
- `modulus(x)` — the distance from the origin.
- `argument(x)` — the angle from the positive real axis, in radians. Use
  `math.atan2(b, a)`, which gets the quadrant right; `math.atan(b / a)` does not.
- `divide(x, y)` — multiply top and bottom by the conjugate of the bottom, so the
  bottom becomes the real number $|y|^2$, then divide both parts by it. Raise
  `ZeroDivisionError` if the bottom is $0 + 0j$.

`main.py` prints a few results when you run it; the checks call your functions.
''',
                "files": [{"name": "main.py", "content": r'''
import math

# A complex number is the tuple (real_part, imaginary_part).
# So (3.0, 4.0) means 3 + 4j.


def add(x, y):
    """(a + jb) + (c + jd). Add the two parts separately."""
    # TODO
    return (0.0, 0.0)


def mul(x, y):
    """(a + jb)(c + jd). Expand, then replace j*j with -1."""
    # TODO
    return (0.0, 0.0)


def conj(x):
    """a + jb  ->  a - jb."""
    # TODO
    return (0.0, 0.0)


def modulus(x):
    """The distance from the origin to the point (a, b)."""
    # TODO
    return 0.0


def argument(x):
    """The angle in radians from the positive real axis. Use math.atan2."""
    # TODO
    return 0.0


def divide(x, y):
    """x / y, by multiplying top and bottom by the conjugate of y."""
    # TODO
    return (0.0, 0.0)


if __name__ == "__main__":
    print("j * j        =", mul((0.0, 1.0), (0.0, 1.0)))
    print("(3+4j) sum   =", add((3.0, 4.0), (1.0, -2.0)))
    print("|3+4j|       =", modulus((3.0, 4.0)))
    print("arg(0+2j)    =", round(argument((0.0, 2.0)), 6), "rad")
    print("1 / j        =", divide((1.0, 0.0), (0.0, 1.0)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

# A complex number is the tuple (real_part, imaginary_part).
# So (3.0, 4.0) means 3 + 4j.


def add(x, y):
    """(a + jb) + (c + jd). Add the two parts separately."""
    return (x[0] + y[0], x[1] + y[1])


def mul(x, y):
    """(a + jb)(c + jd). Expand, then replace j*j with -1."""
    a, b = x
    c, d = y
    return (a * c - b * d, a * d + b * c)


def conj(x):
    """a + jb  ->  a - jb."""
    return (x[0], -x[1])


def modulus(x):
    """The distance from the origin to the point (a, b)."""
    return math.hypot(x[0], x[1])


def argument(x):
    """The angle in radians from the positive real axis. Use math.atan2."""
    return math.atan2(x[1], x[0])


def divide(x, y):
    """x / y, by multiplying top and bottom by the conjugate of y."""
    bottom = y[0] * y[0] + y[1] * y[1]
    if bottom == 0.0:
        raise ZeroDivisionError("cannot divide by 0 + 0j")
    top = mul(x, conj(y))
    return (top[0] / bottom, top[1] / bottom)


if __name__ == "__main__":
    print("j * j        =", mul((0.0, 1.0), (0.0, 1.0)))
    print("(3+4j) sum   =", add((3.0, 4.0), (1.0, -2.0)))
    print("|3+4j|       =", modulus((3.0, 4.0)))
    print("arg(0+2j)    =", round(argument((0.0, 2.0)), 6), "rad")
    print("1 / j        =", divide((1.0, 0.0), (0.0, 1.0)))
'''}],
                "hints": [
                    "For `mul`, write the four products out on paper first: $ac + jad + jbc + j^2bd$. Only the last one changes sign.",
                    "`math.hypot(a, b)` is $\\sqrt{a^2 + b^2}$ and avoids overflow; `math.atan2(b, a)` takes the parts in that order — imaginary first.",
                    "For `divide`, you already have `mul` and `conj`. Multiply the top by `conj(y)`, work out $|y|^2$ as `y[0]**2 + y[1]**2`, and divide each part of the result by it.",
                ],
                "tests": [
                    {"name": "j squared is minus one", "code": r'''
_r = mul((0.0, 1.0), (0.0, 1.0))
assert abs(_r[0] - (-1.0)) < 1e-12 and abs(_r[1]) < 1e-12, \
    f"j*j should be (-1, 0), got {_r}"
'''},
                    {"name": "addition works part by part", "code": r'''
_r = add((3.0, 4.0), (1.0, -2.0))
assert abs(_r[0] - 4.0) < 1e-12 and abs(_r[1] - 2.0) < 1e-12, \
    f"(3+4j) + (1-2j) should be (4, 2), got {_r}"
'''},
                    {"name": "multiplication is not part by part", "code": r'''
_r = mul((3.0, 4.0), (1.0, -2.0))
assert abs(_r[0] - 11.0) < 1e-12 and abs(_r[1] - (-2.0)) < 1e-12, \
    f"(3+4j)(1-2j) should be (11, -2), got {_r} — expand all four products"
'''},
                    {"name": "modulus is Pythagoras", "code": r'''
assert abs(modulus((3.0, 4.0)) - 5.0) < 1e-12, \
    f"|3+4j| should be 5, got {modulus((3.0, 4.0))}"
assert abs(modulus((-3.0, -4.0)) - 5.0) < 1e-12, \
    "the modulus is a distance and can never be negative"
'''},
                    {"name": "argument gets the quadrant right", "code": r'''
import math
assert abs(argument((0.0, 2.0)) - math.pi / 2) < 1e-12, \
    "0 + 2j sits straight up, at pi/2"
_a = argument((-1.0, 1.0))
assert abs(_a - 3 * math.pi / 4) < 1e-12, \
    f"-1 + j is in the second quadrant, at 3pi/4, got {_a} — atan alone cannot see this"
'''},
                    {"name": "a number times its conjugate is real", "code": r'''
_r = mul((3.0, 4.0), conj((3.0, 4.0)))
assert abs(_r[1]) < 1e-12, f"the imaginary part should vanish, got {_r}"
assert abs(_r[0] - 25.0) < 1e-12, f"it should equal |3+4j|^2 = 25, got {_r[0]}"
'''},
                    {"name": "division by j turns the other way", "code": r'''
_r = divide((1.0, 0.0), (0.0, 1.0))
assert abs(_r[0]) < 1e-12 and abs(_r[1] - (-1.0)) < 1e-12, \
    f"1/j should be (0, -1), got {_r} — dividing by j is a quarter turn clockwise"
'''},
                    {"name": "dividing by zero is refused", "code": r'''
try:
    divide((1.0, 2.0), (0.0, 0.0))
except ZeroDivisionError:
    pass
else:
    raise AssertionError("dividing by 0 + 0j should raise ZeroDivisionError")
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Euler's identity and the phasor",
            "summary": "One equation ties the exponential to the sine and cosine, and turns trigonometry into arithmetic.",
            "concepts": [
                "**Euler's identity**: $e^{j\\theta} = \\cos\\theta + j\\sin\\theta$. Read it as a point on the unit circle at angle $\\theta$.",
                "It follows that $|e^{j\\theta}| = 1$ for every real $\\theta$: a pure imaginary exponent rotates and never stretches.",
                "Running it backwards gives $\\cos\\theta = \\frac{e^{j\\theta} + e^{-j\\theta}}{2}$ and $\\sin\\theta = \\frac{e^{j\\theta} - e^{-j\\theta}}{2j}$.",
                "A **phasor** is a complex number carrying the amplitude and the phase of a sinusoid: $A\\cos(\\omega t + \\phi)$ is written $A e^{j\\phi}$, and the $\\omega t$ is left implied because every signal in the circuit shares it.",
                "Two sinusoids of the *same frequency* add by adding their phasors — ordinary complex addition, no trigonometric identities.",
                "A general exponent $\\sigma + j\\omega$ gives $e^{\\sigma t}e^{j\\omega t}$: a rotation at rate $\\omega$ scaled by a growth or decay $e^{\\sigma t}$. Negative $\\sigma$ means the oscillation dies away.",
            ],
            "read": [
                {
                    "title": "The exponential that goes round in circles",
                    "minutes": 13,
                    "body": r'''
Ask where exponentials come from and the answer is always the same sentence: something
whose rate of change is proportional to how much of it there is. A capacitor
discharging through a resistor pushes current out in proportion to the voltage still
across it, and that voltage is in proportion to the charge still on it — so the charge
leaves fastest when there is most of it left, and the emptying slows down as it goes. A
hot object loses heat fastest when it is furthest above room temperature. Written down,
that sentence is

$$\frac{dy}{dt} = ky$$

and the function that satisfies it is $y = y_0e^{kt}$. That is the *only* reason the
number $e$ is in this subject. It is not a mystical constant; it is the base that makes
an exponential its own derivative, which is exactly what the sentence above demands.

Now look at what $k$ does to the picture rather than to the formula. $y$ is a point on
a line, and $dy/dt = ky$ says: at every instant, move along the direction of $y$
itself, at a speed proportional to how far out you already are. With $k$ positive you
run away from the origin, faster and faster. With $k$ negative you fall towards it and
never quite arrive. Either way you stay on the line, because the only direction
available to move in is the one you are already pointing along.

## What happens if the constant is $j$

Module 1 handed us a number that is not on the line and an operation the line cannot
perform: multiplying by $j$ is a quarter turn. So write the same differential equation
with $k = j$, let $z$ be a point on the Argand plane, and call the independent variable
$\theta$, because it is about to turn out to be an angle:

$$\frac{dz}{d\theta} = jz, \qquad z(0) = 1$$

Read that as a rule for motion. *At every instant, move at right angles to the arrow
you are currently at, at a speed equal to that arrow's length.* That is the whole
content of the equation, and two consequences follow with no calculation at all.

First, **the length cannot change.** A velocity at right angles to the radius has no
component along the radius, and only a component along the radius could carry the point
closer to or further from the origin. So $|z|$ stays at 1 for ever. The point is stuck
on the unit circle.

Second, **the speed is fixed.** It is $|z|$, which we have just established is 1. A
point going round a circle of radius 1 at a speed of 1 sweeps out angle at one radian
per unit of $\theta$ — because on the unit circle, arc length *is* angle in radians. So
when $\theta$ has advanced by $\theta$, the point sits at angle $\theta$, having started
at angle zero.

A point on the unit circle at angle $\theta$ has horizontal coordinate $\cos\theta$ and
vertical coordinate $\sin\theta$. That is what cosine and sine *are*; it is a
definition, not a result. So

$$e^{j\theta} = \cos\theta + j\sin\theta$$

This is Euler's identity, and it did not fall out of an algebraic accident. It is what
"grow in the direction of $j$ times yourself" looks like when you draw it.

## The same thing from the series, if you would rather have arithmetic

The geometric argument is the one to keep, but the result also drops out of the power
series, which appeals to no picture at all.

$$e^{x} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \frac{x^4}{4!} + \cdots$$

Put $x = j\theta$ and use the fact that powers of $j$ cycle with period four:

```
j^0 =  1     j^1 =  j     j^2 = -1     j^3 = -j
j^4 =  1     j^5 =  j     j^6 = -1     j^7 = -j
```

Term by term, writing $t$ for the angle to keep the lines short:

```
e^(jt) = 1 + jt + (jt)^2/2! + (jt)^3/3! + (jt)^4/4! + (jt)^5/5! + ...
       = 1 + jt -   t^2/2!  - j t^3/3!  +   t^4/4!  + j t^5/5!  - ...

real terms      :    1 - t^2/2! + t^4/4! - ...    =   cos t
imaginary terms :  j(t - t^3/3! + t^5/5! - ...)   = j sin t
```

The even powers of $j$ are real and alternate in sign, which is precisely the cosine
series. The odd powers each carry a single $j$, and what is left is precisely the sine
series. Nothing was assumed and nothing was arranged: the three series were written
down separately, and two of them turn out to be the halves of the third.

## Polar form, and why it makes multiplication easy

Any complex number is a distance and a direction: $r$ out from the origin, at angle
$\theta$. In rectangular form that is $r\cos\theta + jr\sin\theta$; with Euler's
identity it is

$$z = re^{j\theta}$$

and here is where the identity begins to earn its keep. Multiply two of them:

$$r_1e^{j\theta_1} \cdot r_2e^{j\theta_2} = r_1r_2\,e^{j(\theta_1 + \theta_2)}$$

Nothing has been used except the ordinary index law $e^ae^b = e^{a+b}$, which held for
real exponents and holds here. But read what it says: **multiplying complex numbers
multiplies their lengths and adds their angles.** Module 1 established that multiplying
by $j$ is a quarter turn; that is now simply $j = e^{j\pi/2}$, and adding $\pi/2$ to an
angle is what a quarter turn is. A geometric fact and an algebraic rule have become the
same statement. Powers follow at once, a power being repeated multiplication:
$(re^{j\theta})^n = r^ne^{jn\theta}$.

### Worked: $(-3 + 4j)^3$, both ways

Rectangular first, so that there is something to check against.

```
(-3 + 4j)^2 =  9 - 12j - 12j + 16 j^2
            =  9 - 24j - 16
            = -7 - 24j

(-7 - 24j)(-3 + 4j) = 21 - 28j + 72j - 96 j^2
                    = 21 + 44j + 96
                    = 117 + 44j
```

Now polar. The modulus is $\sqrt{(-3)^2 + 4^2} = 5$, and the point is up and to the
left, so the argument is in the second quadrant.

```
r     = 5
theta = 180 - arctan(4/3) = 180 - 53.130 = 126.870 deg

cube :  r^3     = 5^3 = 125
        3 theta = 380.610 deg  ->  20.610 deg     (one whole turn removed)

125 * cos(20.610 deg) = 125 * 0.93600 = 117.00
125 * sin(20.610 deg) = 125 * 0.35200 =  44.00

(-3 + 4j)^3 = 117 + 44j             the same answer
```

Two things came free. The modulus of the result is $125 = 5^3$, so you knew how big the
answer would be before doing any of it. And the argument advanced by exactly three
times $126.87^\circ$, which overshoots a full turn — angles wrap, and $380.61^\circ$
and $20.61^\circ$ are the same direction. For a cube the rectangular route is about as
quick; for a tenth power it is no contest; and for a *fractional* power the polar route
is the only one that works at all.

## Running Euler backwards

$e^{j\theta}$ and $e^{-j\theta}$ are conjugates — the same point reflected in the real
axis — so adding them destroys the imaginary part and subtracting them destroys the
real one:

$$e^{j\theta} + e^{-j\theta} = 2\cos\theta \qquad
  e^{j\theta} - e^{-j\theta} = 2j\sin\theta$$

which rearranges to

$$\cos\theta = \frac{e^{j\theta} + e^{-j\theta}}{2} \qquad
  \sin\theta = \frac{e^{j\theta} - e^{-j\theta}}{2j}$$

Note where the $2j$ sits and why: the subtraction leaves $2j\sin\theta$, so the $j$ has
to be divided out along with the 2. Get that wrong and every sine in your working is a
quarter turn out.

These two lines turn trigonometric identities into index laws. The double-angle result,
for instance, needs no identity at all — only the squaring of a bracket:

```
cos^2 t = [ (e^(jt) + e^(-jt)) / 2 ]^2
        = ( e^(2jt) + 2 e^(jt) e^(-jt) + e^(-2jt) ) / 4
        = ( e^(2jt) + 2 + e^(-2jt) ) / 4        since e^(jt) e^(-jt) = e^0 = 1
        = ( 2 cos 2t + 2 ) / 4
        = ( 1 + cos 2t ) / 2
```

That identity is what every average-power calculation in electrical engineering rests
on, and it has just been produced by expanding a bracket.

### Worked: an exponent with both parts, in amperes

An exponent need not be purely real or purely imaginary. Split a general one:

$$e^{(\sigma + j\omega)t} = e^{\sigma t}\,e^{j\omega t}$$

The second factor has modulus 1 and does nothing but rotate, at $\omega$ radians per
second. The first is real, and is the whole of the growing or the shrinking. **The real
part of the exponent decides whether it dies; the imaginary part decides only how fast
it goes round.** That is the sentence to carry out of this unit, and it is exactly what
the sandbox at the top of the module draws.

Take a current in a ringing circuit, $i(t) = \mathrm{Re}\{2e^{(-40 + 300j)t}\}$
amperes, and ask what it is doing 10 ms after the start.

```
sigma * t = -40 * 0.010 = -0.400
omega * t = 300 * 0.010 =  3.000 rad  = 171.887 deg

e^(-0.400)      =  0.67032
cos(3.000 rad)  = -0.98999
sin(3.000 rad)  =  0.14112

2 e^(-0.400) e^(3.000 j) = 2 * 0.67032 * (-0.98999 + 0.14112 j)
                         = 1.34064 * (-0.98999 + 0.14112 j)
                         = -1.3272 + 0.1892 j          amperes

i(10 ms)  = Re{...} = -1.327 A
envelope  = |...|   =  1.341 A
```

The envelope, $2e^{\sigma t} = 1.341$ A, is what a peak detector would report; the
$-1.327$ A is what an oscilloscope shows at that instant, and it is negative because
3 radians is a little past half a turn. The decay has a time constant of
$1/40 = 25$ ms, so at 25 ms the envelope is down to $2/e = 0.736$ A whatever the
oscillation happens to be doing at the time.

## The mistake people actually make

**$e^{j30}$ is not thirty degrees.** The exponent of an exponential is a pure number,
and when Euler's identity turns it into an angle, that angle is in radians. Always.
Thirty radians is four and three-quarter turns:

```
30 rad = 30 * 180/pi      = 1718.873 deg
       = 1718.873 - 4*360 =  278.873 deg

e^(30j)       = cos(30 rad) + j sin(30 rad) =  0.1543 - 0.9880 j
e^(j 30 deg)  = cos(30 deg) + j sin(30 deg) =  0.8660 + 0.5000 j
```

Those two are not close. They are not even in the same quadrant. The error is tempting
because engineers write angles in degrees everywhere else — $5e^{j30^\circ}$ is
standard notation on a phasor diagram and nobody objects to it. The degree sign in that
expression is doing real work; drop it and the expression means something else
entirely. Write the sign, or convert to radians, and never let a bare number in an
exponent stand for degrees.

Two smaller ones are worth naming. $e^{a + jb}$ is $e^ae^{jb}$, a *product*: the index
law says exponents add when the powers multiply, and $e^a + e^{jb}$ is not an
exponential of anything. And $|e^{j\theta}| = 1$ for every real $\theta$, so no amount
of increasing $\theta$ makes $e^{j\theta}$ bigger. If the modulus of your answer depends
on $\theta$, a real part has crept into the exponent somewhere.

## Where this stops holding

**Angles wrap, so the complex exponential is not one-to-one.** $e^{j\theta}$ has period
$2\pi$: $e^{j0} = e^{j2\pi} = e^{j4\pi} = 1$. For real exponents you can cancel — $e^a
= e^b$ forces $a = b$ — and here you cannot. All that $e^{j\theta_1} = e^{j\theta_2}$
permits is that $\theta_1$ and $\theta_2$ differ by a whole number of turns. This bites
the first time you measure a phase: an instrument reporting $-270^\circ$ and one
reporting $+90^\circ$ are describing the same phasor, and deciding which you meant is a
question about the circuit rather than about the arithmetic.

**Fractional powers stop having one answer.** $(e^{j\theta})^n = e^{jn\theta}$ is safe
for whole-number $n$. Put $n = 1/3$ and the wrapping bites: $1$ is $e^{j0}$ and
$e^{j2\pi}$ and $e^{j4\pi}$, so the cube roots of 1 are $e^{j0}$, $e^{j2\pi/3}$ and
$e^{j4\pi/3}$ — three of them, evenly spaced round the unit circle, and only one is the
1 you were expecting. Every complex number has $n$ distinct $n$th roots for the same
reason. It is a feature rather than a nuisance, since those evenly spaced points are
what the poles of a filter are made of, but it does mean that "the" square root is a
phrase needing a convention behind it.

**And the circle is only the special case.** A purely imaginary exponent gives a circle
because the modulus never changes. The moment $\sigma$ is not zero the path is a
spiral: inward if $\sigma < 0$, outward if $\sigma > 0$, and the sign of that one real
number is the difference between a filter that settles and an oscillator that runs
away. Module 6 turns it into a design rule. What the next unit does is narrower and
more immediately useful — it takes the case where $\sigma$ is exactly zero and every
signal in the circuit shares one $\omega$, and works out how much of the notation can
be thrown away.
''',
                },
                {
                    "title": "Everything shares the $\\omega t$, so stop writing it",
                    "minutes": 14,
                    "body": r'''
Put two probes on a circuit that is being driven by a signal generator, and look at the
screen. Both traces are sinusoids. They rise and fall at exactly the same rate — the
same number of cycles per second as the generator — and the only ways they differ from
each other are how tall they are and where along the horizontal axis they sit. That is
the whole observation this unit is built on, and it is worth taking seriously before
any algebra starts, because it is a fact about circuits rather than a fact about
mathematics.

Now suppose you want the sum of those two traces, which is what Kirchhoff's voltage law
asks for the moment you go round a loop. In trigonometry that is a slog. Take
$v_1 = A_1\cos(\omega t + \phi_1)$ and $v_2 = A_2\cos(\omega t + \phi_2)$, expand both
with the compound-angle formula, and collect:

```
v1 + v2 = A1 cos(wt) cos(f1) - A1 sin(wt) sin(f1)
        + A2 cos(wt) cos(f2) - A2 sin(wt) sin(f2)

        = [A1 cos f1 + A2 cos f2] cos(wt) - [A1 sin f1 + A2 sin f2] sin(wt)
             \________  ________/               \________  ________/
                      P                                  Q
```

and then, to get back to the single-cosine form $A\cos(\omega t + \phi)$, you need
$A = \sqrt{P^2 + Q^2}$ and $\phi = \arctan(Q/P)$ with a quadrant check on the arctan.
It works. It is also half a page for the sum of two signals, and a node with four
branches would be four pages of it.

Look at what actually survived the slog. Two numbers, $P$ and $Q$. Everything else was
$\cos\omega t$ and $\sin\omega t$ being carried from line to line and coming out at the
end exactly as they went in.

## Why the $\omega t$ can be left behind

A linear circuit does only four things to a signal. It multiplies it by a constant (a
resistor, a divider ratio). It adds signals together (a node, a loop). It
differentiates — $i = C\,dv/dt$ is the capacitor's own law, and module 3 takes it
apart properly. And it integrates, which is what an inductor's current does to its
voltage. Not one of those four can change the *frequency* of a sinusoid: the derivative
of $\cos\omega t$ is $-\omega\sin\omega t$, still at $\omega$; the sum of two signals at
$\omega$ is at $\omega$; a constant times a sinusoid is the same sinusoid, taller.

So once the switch-on transient has died away, every voltage and every current
everywhere in the circuit is a sinusoid at the frequency of the source. The only things
that differ from one node to the next are the amplitude and the phase. The $\omega t$ is
not information. It is a bill that every signal in the circuit pays equally.

## The definition

Combine that observation with Euler's identity. Any sinusoid is the real part of a
rotating complex number:

$$A\cos(\omega t + \phi) = \mathrm{Re}\{Ae^{j(\omega t + \phi)}\}
  = \mathrm{Re}\{\,Ae^{j\phi}\cdot e^{j\omega t}\,\}$$

The exponential has split into the part that differs from signal to signal and the part
that does not. The **phasor** is the first part:

$$V = Ae^{j\phi}$$

an ordinary complex number carrying the amplitude as its modulus and the phase as its
argument. Write it however is convenient — $Ae^{j\phi}$, or $A\angle\phi$, or as
$a + jb$ — since all three name the same point on the Argand plane.

Two conventions have to be fixed once and then never moved. The reference is the
**cosine**: a plain $\cos\omega t$ has phase zero. And the frequency travels separately,
written at the top of the page or held in your head, because the phasor does not
contain it. A phasor without a stated frequency is half an answer.

```
signal                            phasor
--------------------------------------------------------------
5 cos(wt)                         5
5 cos(wt + 90 deg)                5j
5 cos(wt - 90 deg)               -5j
5 sin(wt)                        -5j        since sin(x) = cos(x - 90 deg)
a cos(wt) + b sin(wt)             a - jb
```

The last line is the one to check for yourself, because it is what you need when a
signal arrives written as a sum rather than as a single shifted cosine:

$$\mathrm{Re}\{(a - jb)(\cos\omega t + j\sin\omega t)\} = a\cos\omega t + b\sin\omega t$$

The sine's coefficient arrives on the imaginary axis *with a minus sign*, and that is
the one sign in this unit worth writing on the back of your hand.

## Why adding phasors is the same as adding signals

Taking a real part is a linear operation over real coefficients: the real part of a sum
is the sum of the real parts, and a real constant slides in and out of it freely. So

$$\mathrm{Re}\{V_1e^{j\omega t}\} + \mathrm{Re}\{V_2e^{j\omega t}\}
  = \mathrm{Re}\{(V_1 + V_2)e^{j\omega t}\}$$

and the sum of two sinusoids at the same frequency is the sinusoid whose phasor is the
sum of the two phasors. One line, and it is the entire method. It is also, word for
word, the small print: *the same frequency*, and *real coefficients*. Both are tested
at the end of this unit.

### Worked: 6 V at $+30^\circ$ plus 8 V at $-60^\circ$

$v_1(t) = 6\cos(\omega t + 30^\circ)$ V and $v_2(t) = 8\cos(\omega t - 60^\circ)$ V, at
the same frequency. What is $v_1 + v_2$?

```
V1 = 6 e^(j30 deg)  = 6(cos 30    + j sin 30)    =  5.1962 + 3.0000 j
V2 = 8 e^(-j60 deg) = 8(cos(-60)  + j sin(-60))  =  4.0000 - 6.9282 j
                                                    ----------------
V1 + V2                                          =  9.1962 - 3.9282 j

|V1 + V2| = sqrt(9.1962^2 + 3.9282^2)
          = sqrt(84.569 + 15.431)
          = sqrt(100.000)  =  10.000            volts

arg       = arctan(-3.9282 / 9.1962) = -23.130 deg    (first quadrant across,
                                                       below the axis: no 180 to add)

v1 + v2 = 10.000 cos(wt - 23.130 deg)   volts
```

The amplitude comes out at exactly 10 V, and not by luck. The two phasors are
$90^\circ$ apart — $+30^\circ$ and $-60^\circ$ — so they sit at right angles on the
plane, and 6 and 8 at right angles have given 10 since school. Note what the answer is
*not*. It is not 14 V, which is what adding the amplitudes would give, and it is not
2 V. Two signals of 6 V and 8 V at one frequency can sum to anything from 2 V to 14 V
depending only on where they sit relative to each other, and the phasor is the object
that knows which.

Spot-check it at one instant, $\omega t = 0$:

```
v1(0) = 6 cos(30 deg)  = 5.1962
v2(0) = 8 cos(-60 deg) = 4.0000
                         ------
sum                    = 9.1962

10.000 * cos(-23.130 deg) = 10.000 * 0.91962 = 9.1962      the same number
```

## What a circuit does to a phasor

One more consequence of Euler, and it is the one that puts phasors to work. If
$v(t) = \mathrm{Re}\{Ve^{j\omega t}\}$ then

$$\frac{dv}{dt} = \mathrm{Re}\{j\omega Ve^{j\omega t}\}$$

because differentiating $e^{j\omega t}$ brings down a factor $j\omega$ and nothing else.
**Differentiating in time multiplies the phasor by $j\omega$.** Calculus has become
multiplication.

Apply that to the capacitor's law $i = C\,dv/dt$ and it becomes $I = j\omega C\,V$, or

$$V = \frac{1}{j\omega C}\,I$$

which is Ohm's law with a complex constant where the resistance used to be. That
constant is the **impedance**, and the whole of frequency response is built on it. For
now the only thing that matters is that it is a complex number, so every rule from
module 1 applies to it untouched.

In the filter you drew in the build, a resistor and a capacitor sit in series across
the source and the output is taken across the capacitor, so the output is the ordinary
divider ratio of the two impedances:

$$V_{out} = V_{in}\,\frac{1/(j\omega C)}{R + 1/(j\omega C)}
          = V_{in}\,\frac{1}{1 + j\omega RC}$$

Multiply top and bottom by $j\omega C$ to get from the first form to the second.

### Worked: 5 V into 2 kΩ and 100 nF at 5000 rad/s

```
R C     = 2000 * 100e-9   = 2.0000e-4 s
w R C   = 5000 * 2.0000e-4 = 1.0000        a pure number, as it has to be

Vout = 5 / (1 + 1j)
     = 5 (1 - 1j) / ((1 + 1j)(1 - 1j))
     = 5 (1 - 1j) / 2
     = 2.5000 - 2.5000 j        volts

|Vout|    = sqrt(2.5^2 + 2.5^2)  = 3.5355 V
arg Vout  = arctan(-2.5 / 2.5)   = -45.000 deg

vout(t) = 3.5355 cos(5000 t - 45 deg)   volts
```

In time, $45^\circ$ at $\omega = 5000$ rad/s is a delay of
$(\pi/4)/5000 = 157.1\ \mu\mathrm{s}$, against a period of $2\pi/5000 = 1.2566$ ms.
One eighth of a cycle, which is what a $45^\circ$ lag is.

Now do the resistor. Kirchhoff's voltage law holds for phasors exactly as it holds for
instantaneous voltages, because the phasors were built by a linear operation:

```
VR = Vin - Vout = 5 - (2.5 - 2.5j) = 2.5 + 2.5j   volts

|VR| = sqrt(2.5^2 + 2.5^2) = 3.5355 V   at  +45.000 deg
```

And there is the point of the entire unit. The resistor has 3.5355 V across it and the
capacitor has 3.5355 V across it, and $3.5355 + 3.5355 = 7.071$ V, which is not 5 V and
never was going to be. The two voltages are $90^\circ$ apart, so what adds to the
source is $\sqrt{3.5355^2 + 3.5355^2} = 5.000$ V. **Kirchhoff adds phasors, not
amplitudes.** Put a voltmeter across each component and the two readings sum to more
than the supply, and no law has been broken: the two voltages peak at different
moments, so they are never both at their maximum together.

## The mistake people actually make

Adding the amplitudes, exactly as above. It is worth being precise about why it is
tempting. For direct current, amplitudes *do* add — two 1.5 V cells in series give 3 V
and nobody thinks twice — and that habit is a decade old by the time anyone meets a
capacitor. Nothing in the appearance of an AC circuit warns you that it has stopped
applying. It stops applying because a sinusoid carries two numbers rather than one, and
a meter reporting a single number has thrown one of them away before you got to it.

The second mistake is subtler and catches people who have understood the first. A
phasor is referenced to the cosine. If one signal in a problem is written as a sine and
the rest as cosines, and the sine goes onto the diagram at face value, every angle in
the answer is $90^\circ$ out and nothing about the arithmetic looks wrong. Convert
first: $\sin\theta = \cos(\theta - 90^\circ)$.

## Where the phasor stops working

**Two different frequencies.** A 50 Hz signal and a 60 Hz signal have no combined
phasor. Their arrows rotate at different rates, so the angle between them is not a
number but a function of time, and the sum is not a sinusoid at all. What you do
instead is superposition: solve the circuit at 50 Hz, solve it again at 60 Hz, and add
the two *time* functions at the end. Never the phasors.

**Anything nonlinear.** A diode, a transistor being driven hard, a multiplier — these
produce frequencies that were not in the input, and a phasor has nowhere to put them.
Every step of the derivation above leaned on linearity, pulling $\mathrm{Re}\{\cdot\}$
through sums and real constants. Squaring breaks it immediately, and one example
settles it: with $z = j$, $(\mathrm{Re}\{z\})^2 = 0$ while $\mathrm{Re}\{z^2\} = -1$.

**Power, for exactly that reason.** $p = vi$ is a product of two signals, so it is not
linear and the phasors cannot simply be multiplied through it. The correct statement,
which EE102 derives, is that the average power is $\frac{1}{2}\mathrm{Re}\{VI^*\}$ —
with a conjugate in it and a factor of one half, neither of which you would have
guessed from the phasor rules alone.

**Before the steady state.** A phasor describes what a circuit settles into, not how it
gets there. Close the switch and there is a transient governed by exponents with a real
part — $e^{(\sigma + j\omega)t}$, the spiral from the previous unit and the two dots in
the sandbox at the top of this module. For a stable circuit that transient dies away
and the phasor answer is what remains, which is why the method is worth anything at
all. For a circuit whose $\sigma$ is positive, it never dies, the steady state never
arrives, and the phasor answer describes a state the circuit will never be observed in.
Module 4 puts numbers on how long the waiting takes.
''',
                },
            ],
            "sandbox": {
                "title": "A complex exponent, seen as a response",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 0.2, "wn": 4},
                "brief": r'''
The left panel is the complex plane again, and the two dots are the exponents that
this system's response is built from. The right panel is that response: what the
output does after the input is switched on at time zero, with the dashed line
marking where it eventually settles.

The two sliders move the dots. $\zeta$ (zeta) controls how far to the left they sit
— that is the real part $\sigma$, the decay. $\omega_n$ controls how far they are
from the origin overall.
''',
                "notice": [
                    "Drag $\\zeta$ down to 0. The dots land exactly on the vertical axis, so the exponent is purely imaginary, and the response oscillates between 0 and 2 forever without ever settling. A purely imaginary exponent rotates and never decays — that is $|e^{j\\theta}| = 1$, drawn.",
                    "Put $\\zeta$ back to about 0.2 and watch the response wobble in and stop. The dots are now at $\\sigma \\approx -0.8$ with an imaginary part near $\\pm 3.9$: the rotation is still there, but it is multiplied by a shrinking $e^{\\sigma t}$.",
                    "Push $\\zeta$ up to 1. The caption under the left panel changes from $\\omega_d$ to *both poles real*, the two dots meet on the horizontal axis, and the response climbs to the dashed line without crossing it. No imaginary part means no rotation, so nothing can overshoot.",
                    "Hold $\\zeta$ and double $\\omega_n$ from 4 to 8. The shape of the response is identical; only the numbers on the time axis halve. The angle of the dots, not their distance, sets the character.",
                ],
            },
            "quiz": {
                "title": "Euler, phase and amplitude",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is $e^{j\\pi}$?",
                        "opts": ["$1$", "$-1$", "$j$", "$\\pi$"],
                        "a": 1,
                        "why": (
                            "Put $\\theta = \\pi$ into $e^{j\\theta} = \\cos\\theta + j\\sin\\theta$: "
                            "$\\cos\\pi = -1$ and $\\sin\\pi = 0$, so the answer is $-1 + 0j$. Geometrically you have "
                            "gone half way round the unit circle from $+1$, which lands you on $-1$."
                        ),
                    },
                    {
                        "q": "For a real angle $\\theta$, what is $|e^{j\\theta}|$?",
                        "opts": ["$e^{\\theta}$", "$\\theta$", "$1$, always", "It depends on $\\theta$ in a complicated way"],
                        "a": 2,
                        "why": (
                            "$|e^{j\\theta}|^2 = \\cos^2\\theta + \\sin^2\\theta = 1$, for every $\\theta$. The "
                            "tempting wrong answer is $e^{\\theta}$ — that is the size of $e^{\\theta}$ with a *real* "
                            "exponent. A real exponent stretches; an imaginary one rotates. Keeping those two apart is "
                            "most of what this module is for."
                        ),
                    },
                    {
                        "q": "Which expression equals $\\cos\\theta$?",
                        "opts": [
                            "$\\frac{e^{j\\theta} - e^{-j\\theta}}{2}$",
                            "$\\frac{e^{j\\theta} + e^{-j\\theta}}{2}$",
                            "$\\frac{e^{j\\theta} + e^{-j\\theta}}{2j}$",
                            "$\\frac{e^{j\\theta}}{2}$",
                        ],
                        "a": 1,
                        "why": (
                            "Write $e^{j\\theta} = \\cos\\theta + j\\sin\\theta$ and $e^{-j\\theta} = \\cos\\theta - j\\sin\\theta$, "
                            "then add them: the sines cancel and you get $2\\cos\\theta$. Subtracting instead leaves "
                            "$2j\\sin\\theta$, which is why the *sine* formula is the one carrying the $2j$ on the bottom."
                        ),
                    },
                    {
                        "q": "The signal $5\\cos(\\omega t + 30^\\circ)$ is written as a phasor. What is it?",
                        "opts": [
                            "Amplitude 30, angle $5^\\circ$",
                            "Amplitude 5, angle $-30^\\circ$",
                            "Amplitude 5, angle $30^\\circ$",
                            "Amplitude $5\\omega$, angle $30^\\circ$",
                        ],
                        "a": 2,
                        "why": (
                            "A phasor keeps the two things that vary from signal to signal — the amplitude and the "
                            "phase — and drops the $\\omega t$, because every signal in a circuit driven at one "
                            "frequency shares it. So $5\\cos(\\omega t + 30^\\circ)$ becomes $5e^{j30^\\circ}$. The "
                            "sign is kept as written: a *positive* angle inside the cosine means the signal leads."
                        ),
                    },
                    {
                        "q": "A quantity behaves as $e^{(-2 + 10j)t}$. What does it do as $t$ increases?",
                        "opts": [
                            "Oscillates while growing without limit",
                            "Oscillates forever at constant amplitude",
                            "Falls straight to zero without oscillating",
                            "Oscillates while shrinking towards zero",
                        ],
                        "a": 3,
                        "why": (
                            "Split it: $e^{-2t} \\cdot e^{j10t}$. The second factor has modulus 1 and only rotates, "
                            "at 10 radians per second. The first is a real decaying exponential, and it is the whole "
                            "of the shrinking. Sign of the real part decides shrink or grow; the imaginary part "
                            "decides only how fast it goes round."
                        ),
                    },
                    {
                        "q": "Two sinusoids of the same frequency, amplitudes 3 and 4, with the second lagging the first by exactly $90^\\circ$. What is the amplitude of their sum?",
                        "opts": ["7", "5", "1", "12"],
                        "a": 1,
                        "why": (
                            "As phasors they are $3$ and $-4j$, which are at right angles on the Argand plane, so the "
                            "sum has modulus $\\sqrt{3^2 + 4^2} = 5$. Amplitudes only add to 7 when the two signals are "
                            "exactly in phase, and only subtract to 1 when they are exactly opposed. This is the whole "
                            "reason for phasors: the geometry does the trigonometry for you."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "Eight lines that turn a signal into a number",
                "minutes": 10,
                "caption": "theta and phi are angles in radians; w is the frequency in radians per second",
                "lang": "text",
                "brief": r'''
Nothing is executed here. The first five lines are Euler's identity and its immediate
consequences; the last three convert a signal in the time domain into its phasor, with
the cosine as the reference in every case.

`e^(x)` is the exponential, `*` is multiplication and `deg` marks an angle written in
degrees rather than radians. A phasor is written as a plain complex number.
''',
                "listing": r'''
e^(j theta)                          =  cos(theta) + j ___

|e^(j theta)|                        =  ___

e^(j pi)                             =  ___

e^(j theta) * e^(j phi)              =  e^(j ___)

d/dt [ e^(j w t) ]                   =  ___ * e^(j w t)

5 cos(w t + 90 deg)   as a phasor    =  ___

5 sin(w t)            as a phasor    =  ___

2 cos(w t) - 2 sin(w t)  as a phasor =  ___
''',
                "blanks": [
                    {
                        "prompt": "Euler's identity itself.",
                        "hole": "?",
                        "opts": ["sin(theta)", "cos(theta)", "tan(theta)", "sin(theta)/2"],
                        "a": 0,
                        "why": "The point sits on the unit circle at angle $\\theta$, so its horizontal coordinate is $\\cos\\theta$ and its vertical one is $\\sin\\theta$. The vertical coordinate is the one that gets the $j$.",
                        "whys": [
                            "The point sits on the unit circle at angle $\\theta$, so its horizontal coordinate is $\\cos\\theta$ and its vertical one is $\\sin\\theta$. The vertical coordinate is the one that gets the $j$.",
                            "That would make the whole thing $\\cos\\theta(1 + j)$, which has modulus $\\sqrt{2}\\,|\\cos\\theta|$ — not 1, and zero at a quarter turn, where $e^{j\\pi/2}$ is very much not zero.",
                            "A tangent runs off to infinity at a quarter turn. Nothing on the unit circle can do that; both coordinates of a point on it stay between $-1$ and $+1$.",
                            "The halving has no source. Put $\\theta = \\pi/2$: the identity has to give exactly $j$, and a half would give $j/2$, a point inside the circle rather than on it.",
                        ],
                    },
                    {
                        "prompt": "The size of a pure rotation.",
                        "hole": "?",
                        "opts": ["e^theta", "1", "theta", "sqrt(2)"],
                        "a": 1,
                        "why": "$|e^{j\\theta}|^2 = \\cos^2\\theta + \\sin^2\\theta = 1$ for every real $\\theta$. An imaginary exponent rotates and never stretches, which is the single property that makes the whole of phasor analysis work.",
                        "whys": [
                            "$e^{\\theta}$ is the size of an exponential with a *real* exponent. Keeping the real and the imaginary exponent apart is most of what this module is for: one stretches, the other turns.",
                            "$|e^{j\\theta}|^2 = \\cos^2\\theta + \\sin^2\\theta = 1$ for every real $\\theta$. An imaginary exponent rotates and never stretches, which is the single property that makes the whole of phasor analysis work.",
                            "The angle is not the length. Going twice as far round a circle does not take you further from the middle of it.",
                            "$\\sqrt{2}$ is the modulus of $1 + j$, which is a point on the *corner* of the unit square rather than on the unit circle. $e^{j\\pi/4}$ is that direction shrunk back onto the circle: $0.707 + 0.707j$.",
                        ],
                    },
                    {
                        "prompt": "Half a turn.",
                        "hole": "?",
                        "opts": ["1", "j", "-1", "0"],
                        "a": 2,
                        "why": "$\\cos\\pi = -1$ and $\\sin\\pi = 0$, so $e^{j\\pi} = -1$. Half a turn anticlockwise from $+1$ lands on $-1$, which is also why multiplying by $-1$ was called a flip in module 1: it is two quarter turns.",
                        "whys": [
                            "A full turn, $e^{j2\\pi}$, gives 1. Half of one gives the point diametrically opposite, which is $-1$.",
                            "$j$ is a quarter turn, $e^{j\\pi/2}$. The exponent here is twice that.",
                            "$\\cos\\pi = -1$ and $\\sin\\pi = 0$, so $e^{j\\pi} = -1$. Half a turn anticlockwise from $+1$ lands on $-1$, which is also why multiplying by $-1$ was called a flip in module 1: it is two quarter turns.",
                            "Nothing of the form $e^{j\\theta}$ is ever zero — every one of them has modulus exactly 1.",
                        ],
                    },
                    {
                        "prompt": "Multiplying two rotations.",
                        "hole": "?",
                        "opts": ["theta * phi", "theta + phi", "theta - phi", "theta / phi"],
                        "a": 1,
                        "why": "This is the ordinary index law $e^ae^b = e^{a+b}$, and it is the reason polar form is worth having: multiplying complex numbers adds their angles. Dividing subtracts them.",
                        "whys": [
                            "Exponents add under multiplication; they do not multiply. $e^2e^3$ is $e^5$, not $e^6$, and nothing about an imaginary exponent changes that.",
                            "This is the ordinary index law $e^ae^b = e^{a+b}$, and it is the reason polar form is worth having: multiplying complex numbers adds their angles. Dividing subtracts them.",
                            "Subtraction is what *division* does to the angles. Turning twice in the same sense cannot leave you at zero when the two angles are equal.",
                            "Division of the exponents has no meaning here at all — check it against real exponents, where $e^2e^3$ is plainly not $e^{2/3}$.",
                        ],
                    },
                    {
                        "prompt": "Differentiating a rotation with respect to time.",
                        "hole": "?",
                        "opts": ["w", "j w", "1 / (j w)", "j"],
                        "a": 1,
                        "why": "The chain rule brings down the whole coefficient of $t$ in the exponent, and that coefficient is $j\\omega$. This is the line that turns calculus into multiplication: differentiating a phasor multiplies it by $j\\omega$, and integrating divides by it.",
                        "whys": [
                            "The $\\omega$ is right but the $j$ has been dropped, and the $j$ is the whole content of the result — it says the derivative leads the signal by a quarter turn, which is why a capacitor's current peaks where its voltage is steepest rather than where it is largest.",
                            "The chain rule brings down the whole coefficient of $t$ in the exponent, and that coefficient is $j\\omega$. This is the line that turns calculus into multiplication: differentiating a phasor multiplies it by $j\\omega$, and integrating divides by it.",
                            "That is the factor for *integration*, which is the inverse operation. Differentiating a fast signal produces a bigger result, not a smaller one, so the $\\omega$ must end up on top.",
                            "A bare $j$ has no units and no frequency in it. Differentiate with respect to time and the answer has to scale with how fast the signal is going.",
                        ],
                    },
                    {
                        "prompt": "A cosine shifted a quarter turn early.",
                        "hole": "?",
                        "opts": ["5", "5j", "-5j", "90"],
                        "a": 1,
                        "why": "The phasor is $5e^{j90^\\circ} = 5(\\cos 90^\\circ + j\\sin 90^\\circ) = 5j$. A positive angle inside the cosine means the signal leads, and leading by a quarter turn is multiplication by $j$ — the same quarter turn as in module 1.",
                        "whys": [
                            "That is the phasor of a plain $5\\cos\\omega t$. The shift has been dropped, and with it everything that distinguishes this signal from the reference.",
                            "The phasor is $5e^{j90^\\circ} = 5(\\cos 90^\\circ + j\\sin 90^\\circ) = 5j$. A positive angle inside the cosine means the signal leads, and leading by a quarter turn is multiplication by $j$ — the same quarter turn as in module 1.",
                            "That is a quarter turn the other way, a *lag* of $90^\\circ$. The sign inside the cosine is kept as written: $+90^\\circ$ inside means $+90^\\circ$ on the phasor.",
                            "90 is the angle, not the phasor. A phasor has to carry the amplitude as well, and this one is nowhere near 5 units from the origin.",
                        ],
                    },
                    {
                        "prompt": "A sine, converted to the cosine reference.",
                        "hole": "?",
                        "opts": ["5", "5j", "-5j", "-5"],
                        "a": 2,
                        "why": "$\\sin\\theta = \\cos(\\theta - 90^\\circ)$, so the phasor is $5e^{-j90^\\circ} = -5j$. A sine reaches its peak a quarter cycle after the cosine does, so it lags, and a lag is a negative angle.",
                        "whys": [
                            "That is $5\\cos\\omega t$, the reference itself. A sine is zero when the cosine is at its peak, so the two cannot share a phasor.",
                            "This is the sine put on the diagram a quarter turn the wrong way. The check is at $t = 0$: $5\\sin 0 = 0$, and the real part of $5j$ is also 0 — so far so good — but a moment later the sine is *rising* from zero while $5j$ describes a signal that is falling through it.",
                            "$\\sin\\theta = \\cos(\\theta - 90^\\circ)$, so the phasor is $5e^{-j90^\\circ} = -5j$. A sine reaches its peak a quarter cycle after the cosine does, so it lags, and a lag is a negative angle.",
                            "$-5$ is a phase of $180^\\circ$, an inverted cosine. That is $-5\\cos\\omega t$, half a turn from the reference rather than a quarter.",
                        ],
                    },
                    {
                        "prompt": "A cosine and a sine added together.",
                        "hole": "?",
                        "opts": ["2 + 2j", "2 - 2j", "-2 + 2j", "4"],
                        "a": 0,
                        "why": "$a\\cos\\omega t + b\\sin\\omega t$ has phasor $a - jb$, and here $b = -2$, so the phasor is $2 + 2j$: amplitude $2\\sqrt{2} = 2.828$ at $+45^\\circ$. Check it at $t = 0$, where the signal is 2 and $2.828\\cos 45^\\circ$ is also 2.",
                        "whys": [
                            "$a\\cos\\omega t + b\\sin\\omega t$ has phasor $a - jb$, and here $b = -2$, so the phasor is $2 + 2j$: amplitude $2\\sqrt{2} = 2.828$ at $+45^\\circ$. Check it at $t = 0$, where the signal is 2 and $2.828\\cos 45^\\circ$ is also 2.",
                            "This is the phasor of $2\\cos\\omega t + 2\\sin\\omega t$ — the sign of the sine term has been copied across instead of reversed. The rule is $a\\cos + b\\sin \\to a - jb$, and the minus sign is the whole of the conversion.",
                            "Both signs have gone the wrong way. At $t = 0$ this describes a signal of $-2$, and the one written down is $+2$ there.",
                            "Adding the two amplitudes is the error this module exists to kill. The two terms are a quarter turn apart, so they combine in quadrature: $\\sqrt{2^2 + 2^2} = 2.828$, not 4.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "The value at the instant the clock starts",
                    "minutes": 4,
                    "brief": r'''
One rule, one step. A phasor is a complex number carrying an amplitude and a phase, and
the signal it stands for is $v(t) = \mathrm{Re}\{Ve^{j\omega t}\}$. At $t = 0$ the
rotating factor is $e^0 = 1$ and gets out of the way entirely.
''',
                    "prompt": r"What is $v(t)$ at $t = 0$?",
                    "note": "Answer in volts, to three decimal places.",
                    "figure": r"""
$$V = 12e^{j30^\circ}\ \text{V}, \qquad f = 60\ \text{Hz}$$

A voltage given as a phasor, together with the frequency it belongs to. The signal
itself is $v(t) = \mathrm{Re}\{Ve^{j\omega t}\}$ with $\omega = 2\pi f$.
""",
                    "given": [
                        {"label": "Phasor", "value": "12 V at 30 degrees"},
                        {"label": "Frequency", "value": "60 Hz"},
                        {"label": "Asked for", "value": "the signal at t = 0"},
                    ],
                    "answer": 10.392,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": r"At $t = 0$ the factor $e^{j\omega t}$ is 1, so $v(0)$ is just the real part of the phasor: $12\cos 30^\circ$.",
                    "wrong": r"If you got 6.000, the imaginary part was taken instead of the real one — $12\sin 30^\circ$. If you got 1.851, the 30 went into the cosine as 30 *radians*: $\cos(30\ \text{rad}) = 0.1543$, which is a completely different direction. The degree sign in $e^{j30^\circ}$ is not decoration.",
                    "why": r"$v(0) = \mathrm{Re}\{12e^{j30^\circ}\} = 12\cos 30^\circ = 12 \times 0.86603 = 10.392$ V. The frequency was never needed: it tells you how fast the phasor turns, and at $t = 0$ nothing has turned yet. That is worth noticing, because it is the first sign of what a phasor is for — the amplitude and the phase are the circuit's business, and the frequency is the source's.",
                    "aside": "The imaginary part is not wasted information. $12\\sin 30^\\circ = 6$ V is the coefficient that would sit on the $-\\sin\\omega t$ term if you expanded the cosine out, and it is the value $v$ would have a quarter cycle earlier.",
                },
                {
                    "title": "Two sources on one node",
                    "minutes": 7,
                    "brief": r'''
Two sinusoids of the same frequency, added. The amplitudes do not add, because the two
signals do not peak at the same moment — what adds is the pair of phasors, as ordinary
complex numbers, and the amplitude of the answer is the modulus of that sum.
''',
                    "prompt": r"What is the amplitude of $v_1(t) + v_2(t)$?",
                    "note": "Answer in volts, to three decimal places.",
                    "figure": r"""
$$v_1(t) = 5\cos(\omega t)\ \text{V} \qquad
  v_2(t) = 3\cos(\omega t + 120^\circ)\ \text{V}$$

Both at the same frequency $\omega$, so both can be put on one phasor diagram and left
there.
""",
                    "given": [
                        {"label": "First signal", "value": "5 V at 0 degrees"},
                        {"label": "Second signal", "value": "3 V at 120 degrees"},
                        {"label": "Asked for", "value": "the amplitude of the sum"},
                    ],
                    "answer": 4.359,
                    "tol": 0.01,
                    "unit": "V",
                    "hint": r"The phasors are $5$ and $3e^{j120^\circ}$. Put the second into rectangular form — $3\cos 120^\circ = -1.5$ and $3\sin 120^\circ = +2.598$ — then add and take the modulus.",
                    "wrong": r"If you got 8, the amplitudes were added; that is the answer only when the two signals are exactly in phase. If you got 2, they were subtracted, which is the answer only when they are exactly opposed. If you got 5.831, the two were treated as being at right angles — $\sqrt{5^2 + 3^2}$ — which would need $90^\circ$ between them, not $120^\circ$.",
                    "why": r"As phasors, $V_1 = 5$ and $V_2 = 3e^{j120^\circ} = -1.5 + 2.598j$. Adding: $V_1 + V_2 = 3.5 + 2.598j$. The modulus is $\sqrt{3.5^2 + 2.598^2} = \sqrt{12.25 + 6.75} = \sqrt{19} = 4.3589$ V, and the argument is $\arctan(2.598/3.5) = 36.59^\circ$. Note that the second phasor has *reduced* the real part while adding to the imaginary one, which is exactly what a $120^\circ$ shift should do: past a quarter turn, part of the second signal is working against the first. The answer must lie between $5 - 3 = 2$ V and $5 + 3 = 8$ V, and 4.36 V does.",
                    "aside": "Three equal phasors at $0^\\circ$, $120^\\circ$ and $240^\\circ$ sum to exactly zero, which is why three-phase power distribution needs no return conductor. Here the amplitudes are unequal, so nothing cancels.",
                },
                {
                    "title": "A signal that is not written as a phasor yet",
                    "minutes": 8,
                    "brief": r'''
Circuits do not hand you signals in the form $A\cos(\omega t + \phi)$. A differential
equation or a Kirchhoff sum produces a cosine term and a sine term side by side, and the
first job is to collapse them into one shifted cosine.

Nothing new is needed: $\sin$ is a $\cos$ a quarter turn late, so both terms are already
phasors and they only have to be added.
''',
                    "prompt": r"Written in the form $A\cos(\omega t + \phi)$, what is $\phi$ in degrees?",
                    "note": "Answer in degrees, between $-180^\\circ$ and $+180^\\circ$, to two decimal places.",
                    "figure": r"""
$$v(t) = 3\cos\omega t - 4\sin\omega t \quad \text{volts}$$

One frequency, two terms, and a minus sign that is doing more work than it looks like it
is doing.
""",
                    "given": [
                        {"label": "Cosine coefficient", "value": "3"},
                        {"label": "Sine coefficient", "value": "-4"},
                        {"label": "Asked for", "value": "the phase of the single cosine"},
                    ],
                    "answer": 53.13,
                    "tol": 0.1,
                    "unit": "degrees",
                    "hint": r"$a\cos\omega t + b\sin\omega t$ has phasor $a - jb$. Here $a = 3$ and $b = -4$, so the phasor is $3 + 4j$, and $\phi$ is its argument.",
                    "wrong": r"If you got $-53.13$, the sine's coefficient went onto the imaginary axis with the sign it was written with. It has to be reversed: the phasor of $b\sin\omega t$ is $-jb$, so a *negative* sine term gives a *positive* imaginary part. If you got 36.87, the arctangent was taken the other way up — $\arctan(3/4)$ rather than $\arctan(4/3)$.",
                    "why": r"Rewrite the sine as a cosine: $-4\sin\omega t = 4\cos(\omega t + 90^\circ)$, so the two phasors are $3$ and $4j$, and the total is $3 + 4j$. Its modulus is 5 and its argument is $\arctan(4/3) = 53.13^\circ$, so $v(t) = 5\cos(\omega t + 53.13^\circ)$ V. Check it at two instants. At $\omega t = 0$ the original reads $3 - 0 = 3$, and $5\cos 53.13^\circ = 5 \times 0.6 = 3$. At $\omega t = 90^\circ$ the original reads $0 - 4 = -4$, and $5\cos(143.13^\circ) = 5 \times (-0.8) = -4$. Both agree, which is as much confirmation as two points can give for a sinusoid of known frequency.",
                    "aside": "The amplitude, 5 V, is larger than either coefficient and smaller than their sum — the same quadrature addition as the previous question, with the two terms exactly $90^\\circ$ apart because sine and cosine always are.",
                },
                {
                    "title": "How far behind the input is the output",
                    "minutes": 9,
                    "brief": r'''
A drawn circuit, and the quantity this module exists for. The source drives a resistor
and a capacitor in series, and the probe sits on the capacitor. The output is the input
multiplied by the complex number

$$G = \frac{1}{1 + j\omega RC}$$

so the phase shift the output picks up is the argument of that number. Work in ordinary
frequency and remember that $\omega = 2\pi f$.
''',
                    "prompt": r"What is the phase of the output relative to the input at 2.00 kHz?",
                    "note": "Answer in degrees, to two decimal places. A lagging output has a negative phase.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 2},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "2.00 V amplitude, at 0 degrees"},
                        {"label": "R", "value": "4.70 k\u03a9"},
                        {"label": "C", "value": "10.0 nF"},
                        {"label": "Frequency", "value": "2.00 kHz"},
                    ],
                    # The prompt asks for the argument of the probed node, which is exactly what
                    # the solver's own AC analysis reports — no arithmetic is repeated here.
                    "check": r'''
return c.phase(2000);
''',
                    "answer": -30.567,
                    "tol": 0.05,
                    "unit": "degrees",
                    "hint": r"Form the dimensionless product $x = 2\pi fRC$ first, then the phase is $-\arctan x$. Keep the resistance in ohms and the capacitance in farads.",
                    "wrong": r"If you got $-45$, the frequency was assumed to be the corner; it is not, and the corner of this circuit is 3.39 kHz. If you got $-59.43$, the arctangent was taken of $1/x$ instead of $x$. If you got $-0.53$, the answer is in radians — multiply by $180/\pi$.",
                    "why": r"$RC = 4700 \times 10^{-8} = 4.70\times10^{-5}$ s, so $x = 2\pi fRC = 2\pi \times 2000 \times 4.70\times10^{-5} = 0.5906$. Then $\phi = -\arctan(0.5906) = -30.57^\circ$. The sanity check is the corner frequency, $f_c = 1/(2\pi RC) = 3386$ Hz: 2 kHz is *below* the corner, so the lag must be less than the $45^\circ$ the corner gives, and $30.6^\circ$ is. The amplitude at the same point is $2/\sqrt{1 + 0.5906^2} = 1.722$ V, still most of the way to the full 2 V — below the corner a low-pass filter shifts the phase noticeably before it has taken much amplitude away, which is what makes phase the more sensitive measurement of the two.",
                    "aside": "In time rather than in angle: $30.57^\\circ$ of a 2 kHz cycle is $30.57/360 \\times 500\\ \\mu s = 42.5\\ \\mu s$ of delay.",
                },
                {
                    "title": "The voltage the probe is not on",
                    "minutes": 12,
                    "brief": r'''
The same shape of circuit, larger parts, and a question about the resistor rather than
about the probed node. Kirchhoff's voltage law says the source voltage is the sum of the
two component voltages — but it says so about the *phasors*, which are complex, and not
about the amplitudes, which are not.

So there are three steps: find the output phasor, subtract it from the source phasor,
and take the modulus of what is left.
''',
                    "prompt": r"What is the amplitude of the voltage across the resistor at 1.00 kHz?",
                    "note": "Answer in volts, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 3300},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 47e-9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "10.0 V amplitude, at 0 degrees"},
                        {"label": "R", "value": "3.30 k\u03a9"},
                        {"label": "C", "value": "47.0 nF"},
                        {"label": "Frequency", "value": "1.00 kHz"},
                    ],
                    # The resistor's voltage is not a node voltage, so it cannot be read straight
                    # out of the solve. Both the size and the angle of the probed node are taken
                    # from the AC analysis, the source amplitude is read off the netlist rather
                    # than repeated here, and the subtraction is done in the complex plane.
                    "check": r'''
const f = 1000;
const g = c.gain(f);
const ph = c.phase(f) * Math.PI / 180;
const vin = c.values('V')[0];
const dx = vin - g * Math.cos(ph);
const dy = -g * Math.sin(ph);
return Math.sqrt(dx * dx + dy * dy);
''',
                    "answer": 6.979,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": r"With $x = 2\pi fRC$, the output phasor is $10/(1 + jx)$. Get it into $a + jb$ form with the conjugate trick, subtract it from 10, and take the modulus of the difference. There is a shortcut worth spotting afterwards.",
                    "wrong": r"If you got 2.838, the amplitudes were subtracted: $10 - 7.162$. That is the error this question exists to catch. The two voltages are $90^\circ$ apart, so they do not subtract any more than they add — they combine in quadrature, and quadrature is a Pythagoras, not a subtraction.",
                    "why": r"$RC = 3300 \times 47\times10^{-9} = 1.551\times10^{-4}$ s, so $x = 2\pi \times 1000 \times 1.551\times10^{-4} = 0.9745$. The output phasor is $\dfrac{10}{1 + 0.9745j} = \dfrac{10(1 - 0.9745j)}{1 + 0.9497} = 5.129 - 4.998j$ V, whose modulus is 7.162 V. The resistor takes what is left: $V_R = 10 - (5.129 - 4.998j) = 4.871 + 4.998j$ V, and $|V_R| = \sqrt{23.73 + 24.98} = \sqrt{48.71} = 6.979$ V. Check the whole thing with Pythagoras: $6.979^2 + 7.162^2 = 48.71 + 51.29 = 100.0 = 10^2$. That is not a coincidence — the resistor's voltage is in phase with the current and the capacitor's lags it by exactly $90^\circ$, so the two are always at right angles and always add in quadrature to the source.",
                    "aside": "The shortcut: $|V_R|/|V_C| = x$ exactly, for any first-order RC. Here $x = 0.9745$, so the resistor takes slightly less than the capacitor and the corner — where they are equal — must be slightly above 1 kHz. It is 1026 Hz.",
                },
            ],
            "build": {
                "title": "A filter that lags by 45 degrees",
                "minutes": 22,
                "brief": r'''
Time to draw a circuit.

A **resistor** (R) resists current: the current through it is the voltage across it
divided by its resistance, at every instant. A **capacitor** (C) does not pass a
steady current at all, but it does pass a changing one, and the faster the change
the more easily it passes. That difference is enough to make a *filter*: something
that lets slow signals through and holds fast ones back.

Build a circuit with these properties, driven by the voltage source that is already
on the canvas, and put the probe on the output:

1. It passes low frequencies and blocks high ones.
2. Its **corner frequency** — the frequency at which the output has fallen to
   $1/\sqrt{2}$ of its low-frequency size — is **1 kHz**.
3. At that corner frequency the output **lags the input by 45 degrees**.

The third property is the one that needs module 2. The output is the input
multiplied by a complex number, and at the corner that complex number has an angle
of $-45^\circ$. You are drawing Euler's identity.

Any pair of values with the right product will pass: the checks measure the circuit,
they do not compare it with a drawing.

**How to use the editor.** Pick a part from the toolbar and click the grid to place
it; pick *Wire* and click twice to run a wire; pick *Probe* and click the node you
are calling the output. *Select* a part to change its value. The corner frequency
of a resistor and a capacitor together is $f_c = \dfrac{1}{2\pi RC}$.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 5, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1592},
                        {"id": "p2", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 9, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                    ],
                },
                "checks": [
                    {"name": "low frequencies get through and high ones do not", "code": r'''
const low = c.gain(10);
const high = c.gain(100000);
c.assert(low > 1e-6, "nothing at all reaches the probe at 10 Hz — check the wiring and where the probe sits");
c.assert(high < low / 10, "at 100 kHz the output is " + c.fmt(high, "V") + " against " +
  c.fmt(low, "V") + " at 10 Hz; a low-pass filter should have cut it by far more than that");
'''},
                    {"name": "the corner frequency is 1 kHz", "code": r'''
c.close(c.corner(10, 1e6), 1000, 0.05, "the frequency where the output is 1/sqrt(2) of its low-frequency value");
'''},
                    {"name": "the output lags the input by 45 degrees at the corner", "code": r'''
c.close(c.phase(1000), -45, 0.15, "the phase of the output at 1 kHz");
'''},
                    {"name": "ten times past the corner it is ten times smaller", "code": r'''
const ratio = c.gain(10000) / c.gain(10);
c.close(ratio, 0.0995, 0.2, "the size at 10 kHz relative to the flat region");
'''},
                ],
                "hints": [
                    "Two parts are enough. The source drives the first one, the two of them meet at a node, and the second goes on down to ground. The probe belongs on the node between them.",
                    "Rearrange $f_c = 1/(2\\pi RC)$ to get the product you need: $RC = 1/(2\\pi \\times 1000) \\approx 1.59\\times10^{-4}$. Pick a round capacitor value first — 100 nF, say — and let the resistor take whatever value that forces.",
                    "You can type values as `100n`, `1.6k` or `1e-7`; the editor understands all three.",
                    "Nothing is measurable until there is a ground and a probe. Ground is what all the voltages are measured against, and the probe says which node the checks should look at.",
                ],
            },
            "derive": {
                "title": "The size and the angle of one over one plus jx",
                "minutes": 14,
                "vars": ["x", "j", "R", "C", "omega"],
                "brief": r'''
Every first-order filter in the rest of this degree has the same complex number sitting
at the middle of it:

$$G = \frac{1}{1 + jx}$$

where $x$ is a pure number that grows with frequency. For the resistor-and-capacitor
filter you drew in the build, $x = \omega RC$.

$G$ multiplies the input phasor, so its **modulus** is the factor the amplitude is
multiplied by and its **argument** is the phase the output picks up. Both of those are
real numbers, and neither can be read off the expression while the $j$ is downstairs.
Get it upstairs first, with the conjugate trick from module 1, and the rest is
bookkeeping. Take $x$ to be real and positive throughout.
''',
                "steps": [
                    {
                        "prompt": r"Multiply top and bottom by the conjugate of the denominator. Write the new denominator — it should contain no $j$.",
                        "answer": r"1 + x^2",
                        "placeholder": r"1 plus something",
                        "hint": r"The conjugate of $1 + jx$ is $1 - jx$, and $(1 + jx)(1 - jx) = 1 - (jx)^2$. Then use $j^2 = -1$.",
                        "deconstruct": [
                            r"$(1 + jx)(1 - jx) = 1 - jx + jx - j^2x^2$.",
                            r"The two middle terms differ only in sign, so they cancel exactly.",
                            r"$-j^2x^2 = +x^2$, leaving a real, positive number — which is the whole point of multiplying by the conjugate.",
                        ],
                    },
                    {
                        "prompt": r"The numerator is now $1 \times (1 - jx) = 1 - jx$. Write the real part of $G$, as a fraction in $x$.",
                        "answer": r"\frac{1}{1 + x^2}",
                        "placeholder": r"1 over something",
                        "hint": r"$G = \dfrac{1 - jx}{1 + x^2}$. Split it into two terms over the same denominator; the one without a $j$ is the real part.",
                        "deconstruct": [
                            r"$G = \dfrac{1 - jx}{1 + x^2} = \dfrac{1}{1 + x^2} - j\dfrac{x}{1 + x^2}$.",
                            r"The real part is the term carrying no $j$.",
                            r"Sanity check: at $x = 0$ it is 1, and a filter at zero frequency passes everything.",
                        ],
                    },
                    {
                        "prompt": r"Write the imaginary part of $G$ — the coefficient of $j$, without the $j$ itself.",
                        "answer": r"\frac{-x}{1 + x^2}",
                        "placeholder": r"a fraction carrying a minus sign",
                        "hint": r"From $\dfrac{1}{1 + x^2} - j\dfrac{x}{1 + x^2}$, the coefficient of $j$ is the whole of the second fraction, minus sign included.",
                        "deconstruct": [
                            r"The second term is $-j\dfrac{x}{1 + x^2}$.",
                            r"Stripping the $j$ leaves $-\dfrac{x}{1 + x^2}$, which is negative for every positive $x$.",
                            r"That sign is the lag: the output of this filter is never ahead of its input.",
                        ],
                    },
                    {
                        "prompt": r"Now the modulus. Write $|G|$ as a single expression in $x$.",
                        "answer": r"\frac{1}{\sqrt{1 + x^2}}",
                        "placeholder": r"1 over a square root",
                        "hint": r"$|G|^2$ is the sum of the squares of the two parts: $\dfrac{1 + x^2}{(1 + x^2)^2}$. One factor cancels, and then take the square root.",
                        "deconstruct": [
                            r"$|G|^2 = \dfrac{1^2 + x^2}{(1 + x^2)^2}$, since both parts share the denominator $1 + x^2$.",
                            r"The numerator is $1 + x^2$, so one factor cancels against the denominator, leaving $|G|^2 = \dfrac{1}{1 + x^2}$.",
                            r"Take the positive square root; a modulus is never negative.",
                        ],
                    },
                    {
                        "prompt": r"Write $\tan(\arg G)$ — the imaginary part divided by the real part.",
                        "answer": r"-x",
                        "placeholder": r"something very short",
                        "hint": r"Divide $-\dfrac{x}{1 + x^2}$ by $\dfrac{1}{1 + x^2}$. The denominators are identical and cancel completely.",
                        "deconstruct": [
                            r"$\tan(\arg G) = \dfrac{\text{imaginary part}}{\text{real part}}$.",
                            r"Both parts carry $1 + x^2$ underneath, so it divides out.",
                            r"What is left is $-x$, which means $\arg G = -\arctan x$.",
                        ],
                    },
                    {
                        "prompt": r"For the filter, $x = \omega RC$. Write the frequency $\omega$ at which the argument of $G$ is exactly $-45^\circ$.",
                        "answer": r"\frac{1}{R C}",
                        "placeholder": r"a reciprocal of a product",
                        "hint": r"$\tan(-45^\circ) = -1$, so you need $-x = -1$, that is $\omega RC = 1$. Rearrange for $\omega$.",
                        "deconstruct": [
                            r"$\arg G = -45^\circ$ requires $\tan(\arg G) = -1$.",
                            r"From the previous step that means $x = 1$, and $x = \omega RC$.",
                            r"So $\omega RC = 1$, giving $\omega = 1/(RC)$ radians per second.",
                        ],
                    },
                ],
                "closing": r'''
Collect the three results:

$$|G| = \frac{1}{\sqrt{1 + x^2}} \qquad \arg G = -\arctan x \qquad x = \omega RC$$

and read the two ends off them.

At low frequency $x \ll 1$, so $|G| \to 1$ and $\arg G \to 0$: the filter passes the
signal through unchanged. At high frequency $x \gg 1$, the 1 under the root is
negligible and $|G| \approx 1/x$ — the output falls in inverse proportion to frequency,
which is ten times smaller for every ten times higher, and that is where the *20 dB per
decade* of module 5 comes from. The argument heads for $-\arctan(\infty) = -90^\circ$
and stops there; a first-order filter cannot shift the phase further than a quarter
turn however hard it is driven.

Between the two, $x = 1$ is the crossing point, and it is the one every datasheet
quotes. There $|G| = 1/\sqrt{2} = 0.7071$ and $\arg G = -45^\circ$ exactly — the two
numbers the build measured your circuit against. In ordinary frequency the last step
reads

$$f_c = \frac{\omega}{2\pi} = \frac{1}{2\pi RC}$$

which is the formula the build handed you with no explanation attached. It has one now:
it is the frequency at which the resistor's impedance and the capacitor's are the same
size, so the divider splits the phasor evenly between them — evenly in *length*, at
right angles in *direction*, which is why the output is $0.707$ rather than $0.5$ of the
input there.
''',
            },
            "lab": {
                "title": "Adding sinusoids without trigonometry",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
The circuit you just drew multiplies its input by a complex number. This lab
computes that number, and uses phasors to add sinusoids.

Python writes the imaginary unit as `j` attached to a number: `3+4j` is a complex
number, `abs(z)` is its modulus, and `cmath.phase(z)` is its argument in radians.

Fill in four functions:

- `phasor(amp, phase_deg)` — return the complex number of amplitude `amp` at angle
  `phase_deg` degrees.
- `to_polar(z)` — return the pair `(amplitude, phase_in_degrees)`.
- `add_sinusoids(a1, p1, a2, p2)` — add two sinusoids *of the same frequency* given
  as amplitude and phase in degrees, and return the sum in the same form.
- `rc_gain(R, C, f)` — return the complex number the resistor–capacitor filter
  multiplies its input by at frequency `f` hertz:

$$G = \frac{1}{1 + j\,2\pi f R C}$$

At the corner frequency $f_c = 1/(2\pi RC)$ the bottom becomes $1 + j$, and you
should find that `abs(rc_gain(...))` is $1/\sqrt{2}$ and the phase is exactly
$-45^\circ$ — the two numbers your circuit was measured against.
''',
                "files": [{"name": "main.py", "content": r'''
import cmath
import math


def phasor(amp, phase_deg):
    """The complex number with this amplitude and this phase (in degrees)."""
    # TODO: amp * e^(j * angle in radians)
    return 0j


def to_polar(z):
    """Return (amplitude, phase in degrees) for the complex number z."""
    # TODO: abs(z) and cmath.phase(z), converted to degrees
    return (0.0, 0.0)


def add_sinusoids(a1, p1, a2, p2):
    """Add two same-frequency sinusoids given as amplitude and phase in degrees."""
    # TODO: turn both into phasors, add, convert back
    return (0.0, 0.0)


def rc_gain(R, C, f):
    """The complex gain 1 / (1 + j*2*pi*f*R*C) of a resistor-capacitor filter."""
    # TODO
    return 0j


if __name__ == "__main__":
    print("3 at 0 deg plus 4 at 90 deg ->", add_sinusoids(3.0, 0.0, 4.0, 90.0))
    R, C = 1592.0, 1e-7
    fc = 1.0 / (2.0 * math.pi * R * C)
    print("corner frequency:", round(fc, 2), "Hz")
    print("gain at the corner:", to_polar(rc_gain(R, C, fc)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import cmath
import math


def phasor(amp, phase_deg):
    """The complex number with this amplitude and this phase (in degrees)."""
    return amp * cmath.exp(1j * math.radians(phase_deg))


def to_polar(z):
    """Return (amplitude, phase in degrees) for the complex number z."""
    return (abs(z), math.degrees(cmath.phase(z)))


def add_sinusoids(a1, p1, a2, p2):
    """Add two same-frequency sinusoids given as amplitude and phase in degrees."""
    return to_polar(phasor(a1, p1) + phasor(a2, p2))


def rc_gain(R, C, f):
    """The complex gain 1 / (1 + j*2*pi*f*R*C) of a resistor-capacitor filter."""
    return 1.0 / (1.0 + 1j * 2.0 * math.pi * f * R * C)


if __name__ == "__main__":
    print("3 at 0 deg plus 4 at 90 deg ->", add_sinusoids(3.0, 0.0, 4.0, 90.0))
    R, C = 1592.0, 1e-7
    fc = 1.0 / (2.0 * math.pi * R * C)
    print("corner frequency:", round(fc, 2), "Hz")
    print("gain at the corner:", to_polar(rc_gain(R, C, fc)))
'''}],
                "hints": [
                    "`cmath.exp(1j * x)` is $e^{jx}$ with `x` in radians, and `math.radians` converts degrees for you.",
                    "`to_polar` and `phasor` are inverses of each other. Write them first and check that `to_polar(phasor(2, 30))` gives back `(2, 30)`.",
                    "In `rc_gain` the whole of $2\\pi f R C$ multiplies `1j`, so the bottom is `1 + 1j * 2 * math.pi * f * R * C`. Bracket the whole of that before dividing: `1 / (1 + ...)`. Writing `1 / 1 + 1j * ...` divides by the 1 alone and leaves the rest untouched.",
                ],
                "tests": [
                    {"name": "a phasor at 90 degrees is j", "code": r'''
_z = phasor(1.0, 90.0)
assert abs(_z - 1j) < 1e-12, f"1 at 90 degrees should be j, got {_z}"
_z2 = phasor(2.0, 0.0)
assert abs(_z2 - 2.0) < 1e-12, f"2 at 0 degrees should be 2, got {_z2}"
'''},
                    {"name": "polar and back is the identity", "code": r'''
_a, _p = to_polar(phasor(3.0, -37.0))
assert abs(_a - 3.0) < 1e-9, f"amplitude should come back as 3, got {_a}"
assert abs(_p - (-37.0)) < 1e-9, f"phase should come back as -37 degrees, got {_p}"
'''},
                    {"name": "3 and 4 at right angles make 5", "code": r'''
_a, _p = add_sinusoids(3.0, 0.0, 4.0, 90.0)
assert abs(_a - 5.0) < 1e-9, f"the amplitude should be 5, not 7, got {_a}"
assert abs(_p - 53.13010235415598) < 1e-6, f"the phase should be 53.13 degrees, got {_p}"
'''},
                    {"name": "in phase they add, opposed they cancel", "code": r'''
_a, _p = add_sinusoids(1.0, 0.0, 1.0, 0.0)
assert abs(_a - 2.0) < 1e-9, f"two equal signals in phase add to amplitude 2, got {_a}"
_a, _p = add_sinusoids(1.0, 0.0, 1.0, 180.0)
assert _a < 1e-9, f"two equal signals half a cycle apart cancel exactly, got amplitude {_a}"
'''},
                    {"name": "the gain is 1 at zero frequency", "code": r'''
_g = rc_gain(1000.0, 1e-6, 0.0)
assert abs(_g - 1.0) < 1e-12, f"with nothing changing the filter passes everything, got {_g}"
'''},
                    {"name": "at the corner the gain is 1/sqrt(2) at -45 degrees", "code": r'''
import math
_R, _C = 1592.0, 1e-7
_fc = 1.0 / (2.0 * math.pi * _R * _C)
_amp, _ph = to_polar(rc_gain(_R, _C, _fc))
assert abs(_amp - 0.7071067811865475) < 1e-9, f"the amplitude should be 1/sqrt(2), got {_amp}"
assert abs(_ph - (-45.0)) < 1e-9, f"the phase should be exactly -45 degrees, got {_ph}"
'''},
                    {"name": "ten times past the corner the gain is a tenth", "code": r'''
import math
_R, _C = 1592.0, 1e-7
_fc = 1.0 / (2.0 * math.pi * _R * _C)
_amp, _ph = to_polar(rc_gain(_R, _C, 10.0 * _fc))
assert abs(_amp - 0.09950371902099893) < 1e-9, f"expected about 0.0995, got {_amp}"
assert _ph < -80.0, f"the phase should be heading for -90 degrees, got {_ph}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Differentiating and integrating what circuits produce",
            "summary": "Two operations, and only a handful of functions to apply them to — because circuits only make exponentials and sinusoids.",
            "concepts": [
                "A **derivative** $\\frac{dv}{dt}$ is the slope of a graph of $v$ against $t$: how fast the quantity is changing right now, in volts per second.",
                "An **integral** $\\int i\\,dt$ is the area under the graph so far: how much has accumulated, in this case charge in coulombs.",
                "The exponential is the one function that reproduces itself when differentiated: $\\frac{d}{dt}e^{at} = a\\,e^{at}$, the same function again times a constant. Nothing but a multiple of $e^{at}$ behaves this way, which is why it is everywhere in circuits.",
                "$\\frac{d}{dt}\\sin(\\omega t) = \\omega\\cos(\\omega t)$ and $\\frac{d}{dt}\\cos(\\omega t) = -\\omega\\sin(\\omega t)$. The $\\omega$ appearing out front is the chain rule, and it is the reason fast signals produce big currents.",
                "The **capacitor law** is $i = C\\frac{dv}{dt}$: the current into a capacitor is proportional to how fast its voltage is changing, not to the voltage itself.",
                "Turn that around and the capacitor is an integrator: $v = \\frac{1}{C}\\int i\\,dt$. Push a constant current in and the voltage climbs in a straight line.",
                "The **inductor law** is the mirror image: $v = L\\frac{di}{dt}$. A sudden change of current through an inductor would need an infinite voltage, so current through an inductor cannot jump.",
            ],
            "read": [
                {
                    "title": "The slope of a graph, and the only two shapes that have one worth knowing",
                    "minutes": 14,
                    "body": r'''
Put a probe on a node and watch the trace go past. At every instant the screen is
telling you two different things about that voltage, and separating them is the whole
of this unit.

It tells you **where the trace is**: 3.2 volts above the ground line. And it tells you
**which way it is going and how steeply**: climbing, and climbing hard enough that it
will be at 4 volts forty microseconds from now if nothing interrupts it.

Those two numbers are independent. A trace can sit at 100 V and be perfectly flat. It
can pass through 0 V while rising faster than anything else on the screen. In a circuit
that distinction is not a fine point, because different components read different
numbers off the same trace: a resistor responds to the first — the voltage across it —
and a capacitor responds only to the second. Hold a capacitor at a huge steady voltage
and nothing whatever flows into it.

The second number is the **derivative**, written $\frac{dv}{dt}$, and its unit is volts
per second. The rest of this unit is about how to get one, and about the fact that a
circuit only ever makes two shapes you need it for.

## Rise over run, and then shrinking the run

Start with a straight line, where the answer is obvious. If a trace climbs from 1 V to
4 V over 200 µs, it is climbing at

```
(4 - 1) V / 200e-6 s = 3 / 0.0002 = 15000 V/s
```

and it is climbing at that rate everywhere along the line, because a straight line has
only one slope.

A curve does not. Take the voltage on a 47 nF capacitor discharging through 10 kΩ from
5 V — the commonest curve in the subject, and one we will meet properly in module 4:

$$v(t) = 5\,e^{-t/\tau}, \qquad \tau = RC = 10^4 \times 47\times10^{-9} = 4.70\times10^{-4}\ \text{s}$$

Ask how fast it is falling *at the instant it starts*. Rise over run needs two points,
so pick a second one a little later and see what comes out. Then move that second point
closer and watch what happens to the answer:

```
window       v at end of window      (v_end - 5) / window
------------------------------------------------------------
100 us       4.041727 V              -9582.73  V/s
 10 us       4.894741 V             -10525.92  V/s
  1 us       4.989373 V             -10626.99  V/s
100 ns       4.998936 V             -10637.17  V/s
```

The numbers are not wandering. They are converging, and the thing they converge on is
$-10638.30$ V/s. That limit is the derivative at $t = 0$: the slope of the straight line
that touches the curve there and matches its direction. Every rule of differentiation
you will ever use is a shortcut for that shrinking process, worked out once so nobody
has to do the table again.

One school result is worth having in your hand, because everything else is built from
it: $\frac{d}{dt}t^n = n\,t^{n-1}$. For $n = 2$ you can see where it comes from in one
line — expand $(t + h)^2 = t^2 + 2th + h^2$, subtract $t^2$, divide by $h$ to get
$2t + h$, and let $h$ shrink to nothing. The $h^2$ was the only term that could have
survived and it did not.

## The function that is its own slope

Circuits do not produce arbitrary curves. They produce the solutions of
$\frac{dy}{dt} = ky$ — *the rate of change is proportional to how much is left* — for
the reason module 2 gave: a capacitor pushes current out in proportion to the voltage
still on it. So the function we need is the one that survives being differentiated.

Look for it as a power series, $y = a_0 + a_1t + a_2t^2 + a_3t^3 + \cdots$, and demand
that differentiating gives the same series back. Differentiating shifts everything down
one place and multiplies by the old power:

```
y      = a0 + a1 t + a2 t^2 + a3 t^3 + a4 t^4 + ...
dy/dt  =      a1   + 2 a2 t + 3 a3 t^2 + 4 a4 t^3 + ...

matching:   a1 = a0        a2 = a1/2       a3 = a2/3       a4 = a3/4
```

Starting from $a_0 = 1$ that forces $a_1 = 1$, $a_2 = 1/2$, $a_3 = 1/6$, $a_4 = 1/24$ —
the reciprocals of the factorials, and the series

$$e^{t} = 1 + t + \frac{t^2}{2!} + \frac{t^3}{3!} + \cdots$$

that module 2 already used to get Euler's identity. So $\frac{d}{dt}e^t = e^t$ is not a
curiosity about a particular number; $e$ is *defined* as the base for which it holds,
and that is the only reason the constant is in this subject at all.

For a general exponent the chain rule supplies a factor. Substitute $u = at$: the inner
function contributes $\frac{du}{dt} = a$, so

$$\frac{d}{dt}e^{at} = a\,e^{at}$$

That factor of $a$ is the whole content of the rule, and dropping it is the standard
slip. It says something physical: a fast exponential is also a steep one. Halve the time
constant and the slope at any given voltage doubles.

### Worked: how hard is that capacitor discharging?

Same curve as above: $v(t) = 5e^{-t/\tau}$ with $\tau = 4.70\times10^{-4}$ s. Here
$a = -1/\tau = -2127.66\ \text{s}^{-1}$, so $\frac{dv}{dt} = -\frac{5}{\tau}e^{-t/\tau}$.

```
at t = 0:
    e^0        = 1
    dv/dt      = -5 / 4.70e-4 = -10638.30 V/s
    i = C dv/dt = 47e-9 * (-10638.30) = -5.000e-4 A = -0.500 mA

at t = tau = 470 us:
    e^-1       = 0.367879
    v          = 5 * 0.367879 = 1.8394 V
    dv/dt      = -10638.30 * 0.367879 = -3913.61 V/s

at t = 1.00 ms:
    t/tau      = 1.00e-3 / 4.70e-4 = 2.12766
    e^-2.12766 = 0.1191157
    v          = 5 * 0.1191157 = 0.59558 V
    dv/dt      = -10638.30 * 0.1191157 = -1267.19 V/s
    i          = 47e-9 * (-1267.19) = -59.56 uA
```

The $-10638.30$ V/s matches the table, which is the first check. The second is better:
at $t = 0$ the capacitor holds 5 V and it is connected to a 10 kΩ resistor, so Ohm's law
says 0.5 mA must be leaving it — and $C\frac{dv}{dt}$ gives exactly 0.5 mA without
being told about the resistor at all. Two different laws agreeing on one number is how
you know neither has been misremembered.

Notice one more thing in that column: $\frac{dv/dt}{v}$ is $-2127.66$ at all three
times. The slope is always the same *fraction* of what is left. That sentence is the
differential equation, read backwards off its own solution.

## The circle again: sine and cosine

Module 2 put a point on the unit circle and let it go round at one radian per second, so
that at time $t$ it sits at $(\cos t,\ \sin t)$. It also established the rule of motion:
the velocity is at right angles to the radius, and on the unit circle its length is 1.

That is enough to differentiate both functions with no limits at all. Turning the radius
vector $(\cos t,\ \sin t)$ a quarter turn anticlockwise gives $(-\sin t,\ \cos t)$ — the
same quarter turn that multiplication by $j$ performs. The velocity *is* that vector, and
the velocity is the derivative of the position, component by component:

$$\frac{d}{dt}\cos t = -\sin t \qquad \frac{d}{dt}\sin t = \cos t$$

The minus sign is not a convention to memorise. It is there because a point on the
right-hand side of the circle, moving anticlockwise, is moving *leftwards*: its
horizontal coordinate is decreasing while its vertical one increases.

Now let the point go round $\omega$ times faster. Its position at time $t$ is
$(\cos\omega t,\ \sin\omega t)$, its speed is $\omega$ rather than 1, and its velocity
vector points the same way but is $\omega$ times as long:

$$\frac{d}{dt}\sin(\omega t) = \omega\cos(\omega t) \qquad
  \frac{d}{dt}\cos(\omega t) = -\omega\sin(\omega t)$$

That leading $\omega$ is the chain rule again, and it is the most consequential factor
in this module. It says the steepness of a sinusoid is set by its frequency as much as
by its height.

### Worked: the steepest a mains socket ever gets

A 230 V rms, 50 Hz supply. The amplitude is the rms value times $\sqrt2$, and the
steepest point of a sinusoid is where it crosses zero, since that is where the cosine
factor is at its own peak.

```
amplitude   A = 230 * sqrt(2)   = 325.269 V
omega       w = 2 pi * 50       = 314.159 rad/s
max slope   = w A = 314.159 * 325.269 = 102186 V/s   (about 102 kV/s)

current into a 100 nF capacitor at that instant:
    i = C * w A = 100e-9 * 102186 = 1.0219e-2 A = 10.2 mA
```

Now compare it with a signal a hundredth of a volt of which would be lost in the noise:
1 V amplitude at 1 MHz.

```
omega     = 2 pi * 1e6 = 6.2832e6 rad/s
max slope = 6.2832e6 * 1 = 6.28 MV/s

ratio to the mains: 6.2832e6 / 102186 = 61.5
```

The small signal is sixty-one times steeper than the one that can kill you, because it
is twenty thousand times faster and only three hundred times smaller. This is why a
capacitance of a few picofarads between two tracks is irrelevant at audio and a serious
problem at radio frequency, and why every high-speed layout rule is really a rule about
$\omega$.

## The mistakes people actually make

**Dropping the $\omega$.** Writing $\frac{d}{dt}\sin(\omega t) = \cos(\omega t)$ is
tempting because that is exactly what the rule looked like at school, where the variable
was $x$ and its coefficient was 1. It is not a small error. At 1 MHz it is wrong by a
factor of 6.28 million, and it amounts to claiming that a signal at 1 MHz changes no
faster than one at 1 Hz.

**Claiming the exponential is its own derivative.** The slogan is true of $e^t$ and of
nothing else. $\frac{d}{dt}e^{-t/\tau}$ is $-\frac{1}{\tau}e^{-t/\tau}$, and with
$\tau = 470\ \mu$s that missing factor is 2127, not a rounding matter.

**Reading the rate off the value.** A sinusoid's derivative is *largest where the
sinusoid is zero* and *zero where the sinusoid is largest*, which is the opposite of the
intuition that big signals do big things. It is also the reason a capacitor's current
peaks a quarter cycle before its voltage does — module 2 called that a multiplication by
$j$, and this is the same statement in the time domain.

## Where this stops holding

**At a corner there is no slope.** Everything above assumed you could shrink the window
and get one answer. Approach the apex of a triangle wave from the left and the table
converges on $+4000$ V/s; approach from the right and it converges on $-4000$ V/s. There
is no single number, and $\frac{dv}{dt}$ simply does not exist at that instant. Ideal
square waves are worse: the edge is vertical, so the slope is infinite and $i = C
\frac{dv}{dt}$ predicts an infinite current. Real edges are finite, and the finite
number is alarming enough — a 3.3 V logic signal with a 1 ns edge is moving at
$3.3\times10^9$ V/s, and 10 pF of stray capacitance on that node draws
$10^{-11} \times 3.3\times10^9 = 33$ mA out of the driver for the duration of the edge.
That current is where most of a digital circuit's supply noise comes from.

**On measured data you never have the limit.** An oscilloscope hands you samples, not a
function, so the smallest window available is one sample interval and the table cannot
be continued. Worse, differentiation multiplies by $\omega$, so it multiplies
high-frequency noise more than it multiplies the signal — the same fact that made the
1 MHz trace steep makes the hash riding on your measurement steeper still. The lab at
the end of this module uses a central difference, which is the standard compromise:
better than a one-sided difference, and still no substitute for having a formula. Module
5 turns "multiplies by $\omega$" into a slope on a graph and makes the trade quantitative.

**And two shapes is not all of mathematics.** Nothing here differentiates a product, a
quotient or a composition of anything more elaborate. The reason the module can get away
with it is that a linear circuit driven by a source only ever produces exponentials,
sinusoids, and sums of the two — which is what $e^{(\sigma + j\omega)t}$ was in module 2.
Feed it a diode or a transistor and that guarantee is gone, and so is most of this unit.
''',
                },
                {
                    "title": "Area under the curve, and the two components that do calculus for you",
                    "minutes": 15,
                    "body": r'''
A current of 2 amperes is a flow of 2 coulombs of charge every second. Let it run for
3 seconds and 6 coulombs have gone past. Nobody needs calculus for that: it is one
multiplication, and if you draw the current against time it is the area of a rectangle
2 high and 3 wide.

The whole of integration is what to do when the current is not steady, and the answer is
the same picture. Chop the time axis into strips narrow enough that the current barely
changes across each one, treat every strip as a rectangle, add the rectangles, and then
make the strips narrower until the total stops moving. That total is the **integral**,
written $\int i\,dt$, and for current against time it is the accumulated charge in
coulombs. Amperes times seconds are coulombs; the units come out right because the
picture was right.

Two things about that definition are worth saying out loud before any component appears.

First, **the integral is a running total, not a single number.** Ask for the charge
delivered *so far* and you get a function of time, one value for every instant you might
stop counting.

Second, **the total has to start somewhere.** Integration recovers changes, and changes
alone never tell you where you are. That is the constant of integration, and in a
circuit it is never a formality: it is the charge that was already on the capacitor when
you started watching.

### Worked: a current that will not sit still

Suppose a current is sampled every 10 ms and reads 0, 120, 200, 240, 250 µA. The
trapezoid rule joins consecutive samples with straight lines and adds the areas, each of
width 10 ms and height equal to the average of its two ends:

```
strip 1:  0.010 * (0   + 120)/2 uA.s =  0.600 uC
strip 2:  0.010 * (120 + 200)/2 uA.s =  1.600 uC
strip 3:  0.010 * (200 + 240)/2 uA.s =  2.200 uC
strip 4:  0.010 * (240 + 250)/2 uA.s =  2.450 uC
                                total =  6.850 uC
```

6.85 microcoulombs in 40 ms. It is an estimate, because the true curve between samples
is not straight, but it is the estimate every simulator and every scope's maths channel
actually computes, and the lab at the end of this module has you write it.

## Where $i = C\frac{dv}{dt}$ comes from

A capacitor is two conductors with an insulator between them. Push charge onto one plate
and an equal charge leaves the other, and the voltage between them grows in proportion
to the charge you have moved. That proportionality is the *definition* of capacitance:

$$q = Cv$$

with $q$ in coulombs, $v$ in volts and $C$ in farads. A 1 F capacitor at 1 V is holding
1 C, which is an enormous amount of charge — hence the microfarads and nanofarads that
real parts are made in.

Now differentiate both sides with respect to time. $C$ is a constant, and the rate at
which charge arrives at the plate is precisely what we mean by the current into the
capacitor:

$$i = \frac{dq}{dt} = C\frac{dv}{dt}$$

That is the capacitor law, and it was not announced — it is $q = Cv$ with the clock
started. Everything strange about capacitors follows from it. A steady voltage, however
large, has $\frac{dv}{dt} = 0$ and draws no current at all; that is what "blocks DC"
means. A voltage that jumps instantaneously would need an infinite current, so a
capacitor's voltage is continuous no matter what you do to the rest of the circuit.

Run it the other way and the capacitor is an integrator:

$$v(t) = v(0) + \frac{1}{C}\int_0^t i\,dt'$$

Read the $v(0)$: the integral supplies the *change* in voltage, and the capacitor
supplies the starting point out of the charge it was already holding.

### Worked: a triangle in, a square out

A 470 nF capacitor is driven by a triangle wave at 1 kHz that climbs from 0 V to 2 V in
the first half of each cycle and falls back in the second. Each half lasts 500 µs.

```
rising half:   dv/dt = +2.0 V / 500e-6 s = +4000 V/s
               i = C dv/dt = 470e-9 * 4000 = +1.88e-3 A = +1.88 mA

falling half:  dv/dt = -4000 V/s
               i = -1.88 mA
```

The current is a **square wave** of ±1.88 mA. Nothing about it is triangular, because
the capacitor never sees the voltage — only its slope, and the slope of a triangle wave
is piecewise constant. This is worth carrying around as a picture: differentiating turns
triangles into squares, and integrating turns squares back into triangles.

Check the charge two ways, which is the habit to build:

```
from the current:  q = i * t = 1.88e-3 * 500e-6 = 9.40e-7 C
from the voltage:  q = C dv = 470e-9 * 2.0     = 9.40e-7 C
```

0.94 µC either way.

### Worked: starting from somewhere

A 10 µF capacitor already sits at 2.00 V. A steady 250 µA is pushed into it for 60 ms.
What is the voltage at the end?

```
charge delivered  q  = I t = 250e-6 * 0.060 = 1.50e-5 C
change in voltage dv = q / C = 1.50e-5 / 10e-6 = 1.50 V
final voltage        = 2.00 + 1.50 = 3.50 V
```

The 2.00 V is not decoration. Leave it out and you get 1.50 V, which is a perfectly
correct answer to a question nobody asked. Note also the shape of the middle line: the
same charge into a *bigger* capacitor produces a *smaller* voltage change, because $C$
is downstairs. A big capacitor is a large bucket, not a full one.

## The inductor is the same statement with the words swapped

An inductor stores energy in a magnetic field instead of an electric one, and its law is
the mirror image of the capacitor's:

$$v = L\frac{di}{dt} \qquad\Longleftrightarrow\qquad
  i(t) = i(0) + \frac{1}{L}\int_0^t v\,dt'$$

Voltage and current have exchanged places, and so has everything that follows. The
current through an inductor cannot jump, because a jump would need an infinite voltage.
An inductor with a steady current through it has no voltage across it at all — it is
just a piece of wire, which is exactly how the DC solver treats it.

The integral form is worth reading carefully, because it says that what sets an
inductor's current is the **volt-seconds** applied to it: the area under the voltage
curve, not the voltage itself. Power electronics is largely bookkeeping in volt-seconds.

### Worked: volt-seconds into a coil

A 100 mH inductor starts with no current. 5 V is applied across it for 3 ms, then the
polarity is reversed to $-5$ V for 1 ms.

```
first interval:   area = +5 * 3e-3 = +0.0150 V.s
                  di   = 0.0150 / 0.1 = +0.150 A
                  i after 3 ms = 0.150 A

second interval:  area = -5 * 1e-3 = -0.0050 V.s
                  di   = -0.0050 / 0.1 = -0.050 A
                  i after 4 ms = 0.150 - 0.050 = 0.100 A

net:              0.0150 - 0.0050 = 0.0100 V.s, and 0.0100/0.1 = 0.100 A  (same answer)
```

The current did not care in which order the volt-seconds arrived, only about the total —
which is what "the integral is the area" means when the area comes in pieces of both
signs. That last line is also the design rule for a transformer: apply equal and
opposite volt-seconds every cycle, or the current walks away and the core saturates.

## The mistakes people actually make

**Treating a capacitor as though it had a resistance.** Module 2 gave a capacitor an
impedance of $1/(\omega C)$, in ohms, and it behaves like a resistance in a divider — so
it is very tempting to write $i = v/(1/\omega C)$ and be done. That number is real, but
it exists only for a *steady sinusoid at one frequency*: it is what
$i = C\frac{dv}{dt}$ collapses to once you have agreed that everything in the circuit is
$Ae^{j\omega t}$. Ask it about a step, a triangle wave, or the instant a switch closes
and it has no answer, because there is no $\omega$. When something is not a sinusoid,
$i = C\frac{dv}{dt}$ is the only statement that still holds.

**Losing the constant of integration.** An integral tells you the change. Every
capacitor question that starts "the capacitor is initially charged to..." is testing
this one line, and it is the single commonest source of an answer that is right by a
constant offset.

## Where this stops holding

**$C$ is not actually constant.** $q = Cv$ was written as if capacitance were a property
of a part, and for film and NP0 ceramic parts it nearly is. Class-2 ceramics — the X7R
and X5R capacitors that make up most of what is on a board — lose capacitance under DC
bias, and the loss is not marginal: a 10 µF 6.3 V part in an 0805 package can be down
near 3 µF with 5 V across it. Every equation above still holds instant by instant, but
the $C$ in it is the one at the voltage you are actually at, which is a different
question from the one printed on the reel.

**Real capacitors leak and real inductors have resistance.** An ideal capacitor holds its
charge for ever, so "it blocks DC" is exact. A real one has a leakage resistance across
it, and a sample-and-hold circuit that has to keep a voltage for a second is designed
around that number rather than around $C$. Symmetrically, an inductor's winding
resistance means a steady current does need a voltage after all.

**And the ideal laws break at the extremes they seem to forbid.** Connect a 1 µF
capacitor charged to 10 V directly across an identical uncharged one. Charge is
conserved, so the 10 µC spreads over 2 µF and both settle at 5 V. But count the energy:
$\frac12 \times 1\ \mu\text{F} \times 10^2 = 50\ \mu$J before, and
$\frac12 \times 2\ \mu\text{F} \times 5^2 = 25\ \mu$J after. Half of it has gone, and it
goes no matter how thick the wire is — the thinner the wire, the bigger the current and
the shorter the time, with the product unchanged. An ideal, resistance-free connection is
not a limit the equations can take.

The inductor's version of that is louder. Open a switch on a 100 mH relay coil carrying
150 mA and the current is being forced to zero in whatever time the contacts take to
part, perhaps a microsecond:

```
di/dt = -0.150 / 1e-6 = -1.5e5 A/s
v     = L di/dt = 0.1 * (-1.5e5) = -15000 V
```

Fifteen kilovolts across a relay driver, which is why the contacts arc and why every
inductive load in a real design has a diode across it. The equation did not fail; it
told you exactly what would happen if you insisted on the impossible, and the arc is the
circuit's way of declining.

The next module takes these two laws, puts a resistor next to them, and asks what
happens when the current that charges a capacitor is itself set by the voltage the
capacitor has reached — which is a differential equation, and the reason the exponential
in the previous unit was worth so much attention.
''',
                },
            ],
            "sandbox": {
                "title": "Exponentials, added together",
                "visualiser": "pole-step",
                "minutes": 7,
                "initial": {"zeta": 1.4, "wn": 3},
                "brief": r'''
The same two panels as in module 2, but this time both dots sit on the horizontal
axis, so both exponents are ordinary real numbers and there is no rotation at all.
The response on the right is a sum of two decaying exponentials, and it is the
commonest shape in the whole subject.
''',
                "notice": [
                    "The caption under the left panel reads *both poles real*, and the two dots are far apart: one close to the origin, near $-1.3$, and one much further left, near $-7.1$. The far one has died away almost immediately; the near one is what you are watching for the rest of the plot.",
                    "The curve rises towards the dashed line and never crosses it. With no imaginary part there is nothing to rotate, so nothing can overshoot — a sum of decaying exponentials can only approach its final value from one side.",
                    "Push $\\zeta$ up to 1.6. The near dot creeps closer to the origin, from about $-1.26$ to about $-1.05$, and the curve now ends further short of the dashed line than it did — about 92% of the way up instead of 97%. The slowest exponential always sets the pace.",
                    "Now drag $\\zeta$ down to 0.7. The two dots change colour, lift off the horizontal axis, and the caption becomes $\\omega_d$; the response overshoots the dashed line by about 5% before settling back on it. That is the moment the exponents become complex and module 2's rotation comes back.",
                ],
            },
            "quiz": {
                "title": "Slopes, areas, and what a capacitor does",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is $\\frac{d}{dt}e^{at}$, where $a$ is a constant?",
                        "opts": ["$e^{at}$", "$t\\,e^{at}$", "$a\\,e^{at}$", "$a\\,e^{a}$"],
                        "a": 2,
                        "why": (
                            "The exponential comes back unchanged apart from a factor of $a$ from the chain rule. "
                            "Answering $e^{at}$ is the standard slip — that is only right when $a = 1$. The factor "
                            "matters: it is what makes a fast-decaying exponential also a steeply-sloping one."
                        ),
                    },
                    {
                        "q": "A capacitor has a perfectly steady voltage across it. What current flows into it?",
                        "opts": ["A steady current proportional to the voltage", "None", "An infinite current", "A current proportional to $C$ alone"],
                        "a": 1,
                        "why": (
                            "$i = C\\frac{dv}{dt}$, and a steady voltage has $\\frac{dv}{dt} = 0$, so the current is "
                            "zero however large the voltage is. This is what people mean when they say a capacitor "
                            "*blocks DC*. Confusing it with a resistor, where current is proportional to voltage, is "
                            "the mistake to avoid: for a capacitor it is proportional to the *rate of change*."
                        ),
                    },
                    {
                        "q": "What is $\\frac{d}{dt}\\sin(\\omega t)$?",
                        "opts": ["$\\cos(\\omega t)$", "$-\\omega\\cos(\\omega t)$", "$\\omega\\sin(\\omega t)$", "$\\omega\\cos(\\omega t)$"],
                        "a": 3,
                        "why": (
                            "The sine differentiates to the cosine, and the chain rule brings out the $\\omega$ from "
                            "inside the bracket. Dropping that $\\omega$ is the usual error, and it is not a small "
                            "one: it says a signal at 1 MHz changes no faster than a signal at 1 Hz. The minus sign "
                            "belongs to the derivative of the *cosine*, not the sine."
                        ),
                    },
                    {
                        "q": "A steady current $I$ flows into a capacitor $C$ for a time $T$, starting from zero volts. What is the final voltage?",
                        "opts": [
                            "$ICT$",
                            "$IT$",
                            "$\\frac{IT}{C}$",
                            "$\\frac{I}{CT}$",
                        ],
                        "a": 2,
                        "why": (
                            "Integrating the capacitor law: $v = \\frac{1}{C}\\int_0^T I\\,dt = \\frac{IT}{C}$. The "
                            "integral of a constant is the constant times the elapsed time — the area of a rectangle. "
                            "Note the shape of the answer: bigger capacitor, *smaller* voltage for the same charge, "
                            "because $C$ is on the bottom."
                        ),
                    },
                    {
                        "q": "Why can the current through an inductor not change instantly?",
                        "opts": [
                            "Because inductors have resistance",
                            "Because $v = L\\frac{di}{dt}$, and an instant change would demand an infinite voltage",
                            "Because the current has to go somewhere first",
                            "It can — inductors respond instantly",
                        ],
                        "a": 1,
                        "why": (
                            "An instantaneous jump in current means $\\frac{di}{dt}$ is infinite, and $v = L\\frac{di}{dt}$ "
                            "then demands an infinite voltage, which no real source can supply. So inductor current is "
                            "continuous. The mirror statement holds for capacitors: their *voltage* cannot jump, because "
                            "that would need infinite current."
                        ),
                    },
                    {
                        "q": "You plot current against time and measure the area under the curve. What physical quantity have you measured?",
                        "opts": ["Charge, in coulombs", "Energy, in joules", "Power, in watts", "Voltage, in volts"],
                        "a": 0,
                        "why": (
                            "Current is charge per second, so current multiplied by time is charge — and the area under "
                            "the curve is exactly that product, accumulated over an interval where the current varies. "
                            "Energy would need the area under a *power* curve, and power is voltage times current, not "
                            "current alone."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "Seven lines that cover the whole module",
                "minutes": 9,
                "caption": "a is a constant, w is a frequency in radians per second, I is a constant current",
                "lang": "text",
                "brief": r'''
Nothing is executed here. The first three lines are the derivatives this module needs;
the next two are the component laws; the last two are what integration gives back.

`e^(x)` is the exponential, `*` is multiplication, and `v(0)` is the capacitor voltage
at the moment the clock starts.
''',
                "listing": r'''
d/dt [ e^(a t) ]                       =  ___ * e^(a t)

d/dt [ cos(w t) ]                      =  ___

d/dt [ t^3 ]                           =  ___

i into a capacitor C                   =  C * ___

v across an inductor L                 =  L * ___

v on capacitor C after time T, given   =  v(0) + (1/C) * ___
a constant current I from t = 0

energy stored in C at voltage V        =  ___
''',
                "blanks": [
                    {
                        "prompt": "The chain rule on an exponential.",
                        "hole": "?",
                        "opts": ["a", "1", "t", "a t"],
                        "a": 0,
                        "why": "The coefficient of $t$ in the exponent comes down out front: $\\frac{d}{dt}e^{at} = a\\,e^{at}$. It is the factor that makes a fast exponential a steep one, and with $a = -1/\\tau$ and $\\tau = 470\\ \\mu$s it is $-2128$, not something to leave out.",
                        "whys": [
                            "The coefficient of $t$ in the exponent comes down out front: $\\frac{d}{dt}e^{at} = a\\,e^{at}$. It is the factor that makes a fast exponential a steep one, and with $a = -1/\\tau$ and $\\tau = 470\\ \\mu$s it is $-2128$, not something to leave out.",
                            "That is the slogan *the exponential is its own derivative* applied where it does not belong. It holds for $e^t$ and for nothing else; the moment the exponent has a coefficient, so does the derivative.",
                            "A factor of $t$ would mean the slope kept growing even for a decaying exponential, which is the opposite of what a discharging capacitor does. Powers of $t$ appear when you differentiate powers of $t$, not exponentials.",
                            "Only one factor of $a$ comes down, from the inner function $at$. Differentiating a second time would bring down another and give $a^2e^{at}$.",
                        ],
                    },
                    {
                        "prompt": "Differentiating a cosine, frequency included.",
                        "hole": "?",
                        "opts": ["sin(w t)", "-sin(w t)", "-w sin(w t)", "w sin(w t)"],
                        "a": 2,
                        "why": "Two things happen at once: the cosine becomes a sine with a minus sign, and the chain rule brings out the $\\omega$. Picture the point going round the circle — on the right-hand side, moving anticlockwise, it is heading leftwards, so the horizontal coordinate is falling.",
                        "whys": [
                            "Both the sign and the $\\omega$ have gone. This says a cosine's slope is largest where the cosine is largest, and it is in fact zero there.",
                            "The sign is right and the frequency is missing. Dropping $\\omega$ claims a 1 MHz signal changes no faster than a 1 Hz one — wrong by a factor of a million.",
                            "Two things happen at once: the cosine becomes a sine with a minus sign, and the chain rule brings out the $\\omega$. Picture the point going round the circle — on the right-hand side, moving anticlockwise, it is heading leftwards, so the horizontal coordinate is falling.",
                            "The magnitude is right but the sign is not. A cosine starts at its maximum, so it can only go down from there; a positive slope at $t = 0$ would take it above 1.",
                        ],
                    },
                    {
                        "prompt": "The school rule, still needed.",
                        "hole": "?",
                        "opts": ["3 t", "3 t^2", "t^2", "t^4 / 4"],
                        "a": 1,
                        "why": "$\\frac{d}{dt}t^n = n\\,t^{n-1}$: the old power comes down as a factor and the new power is one lower. This is the rule the exponential's power series was differentiated with in the reading.",
                        "whys": [
                            "The factor of 3 is right and the power has fallen too far. Differentiating drops the exponent by exactly one, from 3 to 2.",
                            "$\\frac{d}{dt}t^n = n\\,t^{n-1}$: the old power comes down as a factor and the new power is one lower. This is the rule the exponential's power series was differentiated with in the reading.",
                            "The power is right and the factor of 3 has been lost. Check it at $t = 1$: $t^3$ is passing 1 and climbing three times as fast as $t$ itself is.",
                            "That is the *integral* of $t^3$, not its derivative. Integration raises the power and divides by the new one; differentiation does the reverse.",
                        ],
                    },
                    {
                        "prompt": "The capacitor law.",
                        "hole": "?",
                        "opts": ["v", "dv/dt", "integral of v dt", "1/v"],
                        "a": 1,
                        "why": "$i = C\\frac{dv}{dt}$, which is $q = Cv$ with the clock running. The current depends on how fast the voltage is moving, not on where it is — which is why a capacitor with a steady 100 V across it draws nothing at all.",
                        "whys": [
                            "$i = Cv$ would make a capacitor a resistor of conductance $C$, and it would draw a steady current from a steady voltage for ever. What it actually does with a steady voltage is nothing.",
                            "$i = C\\frac{dv}{dt}$, which is $q = Cv$ with the clock running. The current depends on how fast the voltage is moving, not on where it is — which is why a capacitor with a steady 100 V across it draws nothing at all.",
                            "That has the operation the wrong way round. Integrating the voltage would mean the current kept growing while a steady voltage was applied, when in fact it falls to zero.",
                            "Nothing in a linear component divides by the signal. This would also blow up at every zero crossing, where a real capacitor's current is at its most ordinary.",
                        ],
                    },
                    {
                        "prompt": "The inductor law — the same statement with the words swapped.",
                        "hole": "?",
                        "opts": ["i", "di/dt", "integral of i dt", "i / t"],
                        "a": 1,
                        "why": "$v = L\\frac{di}{dt}$. Voltage and current have exchanged roles compared with the capacitor, and every consequence swaps with them: an inductor carrying a steady current has no voltage across it, and its current cannot jump because a jump would demand an infinite voltage.",
                        "whys": [
                            "$v = Li$ is Ohm's law with $L$ playing the part of a resistance, and an inductor is not a resistor — a steady current through an ideal one produces no voltage whatever.",
                            "$v = L\\frac{di}{dt}$. Voltage and current have exchanged roles compared with the capacitor, and every consequence swaps with them: an inductor carrying a steady current has no voltage across it, and its current cannot jump because a jump would demand an infinite voltage.",
                            "Integrating is what the inductor does to *voltage* in order to produce current. Written this way round it is the capacitor's relation with the letters changed, which is exactly one swap too many.",
                            "An average rate is not the instantaneous one. $i/t$ happens to agree with $di/dt$ for a current that ramps from zero, and disagrees with it for everything else.",
                        ],
                    },
                    {
                        "prompt": "The area under a constant current.",
                        "hole": "?",
                        "opts": ["I T", "I / T", "I T^2 / 2", "I"],
                        "a": 0,
                        "why": "The integral of a constant is the area of a rectangle: height $I$, width $T$, so $IT$ coulombs of charge, and dividing by $C$ turns that into volts. Straight in, straight up — the build in this module is exactly this line, watched on a plot.",
                        "whys": [
                            "The integral of a constant is the area of a rectangle: height $I$, width $T$, so $IT$ coulombs of charge, and dividing by $C$ turns that into volts. Straight in, straight up — the build in this module is exactly this line, watched on a plot.",
                            "Dividing by the time would mean that leaving the current running longer charged the capacitor *less*. Charge accumulates; it does not get diluted.",
                            "$T^2/2$ is the area under a current that *ramps* from zero, which is a triangle. A constant current gives a rectangle, and the area of a rectangle carries no half.",
                            "The current alone has the wrong units — amperes where coulombs are needed. However briefly you leave a current running you get some charge, and how briefly has to appear in the answer.",
                        ],
                    },
                    {
                        "prompt": "What the capacitor has swallowed.",
                        "hole": "?",
                        "opts": ["C V", "(1/2) C V^2", "C V^2", "(1/2) C V"],
                        "a": 1,
                        "why": "$W = \\frac12 CV^2$, in joules. The derivation in this module gets it by integrating the power $vi = Cv\\frac{dv}{dt}$, where the $dt$ cancels and what is left is the area under a straight line of height $Cv$ — a triangle, hence the half.",
                        "whys": [
                            "$CV$ is the stored *charge* in coulombs, not the stored energy in joules. It is the number you need for the last line but one; squaring and halving it turns it into this one.",
                            "$W = \\frac12 CV^2$, in joules. The derivation in this module gets it by integrating the power $vi = Cv\\frac{dv}{dt}$, where the $dt$ cancels and what is left is the area under a straight line of height $Cv$ — a triangle, hence the half.",
                            "$CV^2$ is what the *source* had to give up to charge the capacitor through a resistor, and exactly half of it was burnt in the resistor on the way. The capacitor keeps the other half.",
                            "This has the half but not the square, so it is half the charge rather than any energy. Energy has to grow faster than linearly with voltage, because each extra coulomb is being pushed across a bigger gap than the one before it.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "A ramp, a capacitor, and one multiplication",
                    "minutes": 5,
                    "brief": r'''
One rule, one unknown. The only thing to be careful about is the time unit, which is why
it is written in microseconds.
''',
                    "prompt": "What current flows into the capacitor while the voltage is climbing?",
                    "note": "Give the answer in milliamperes, to one decimal place.",
                    "figure": "A 220 nF capacitor has the voltage across it driven in a perfectly straight line "
                              "from 0 V up to 12.0 V, taking 300 µs to get there. Nothing else is connected "
                              "to it.",
                    "given": [
                        {"label": "Capacitance", "value": "220 nF"},
                        {"label": "Voltage change", "value": "0 V to 12.0 V"},
                        {"label": "Time taken", "value": "300 µs"},
                    ],
                    "aside": "Work the slope out in volts per *second* before multiplying by anything. "
                             "300 µs is $3.00\\times10^{-4}$ s.",
                    "answer": 8.8,
                    "tol": 0.05,
                    "unit": "mA",
                    "hint": "$i = C\\dfrac{dv}{dt}$, and a straight climb has the same slope at every instant, "
                            "so there is only one current to find.",
                    "wrong": "If you got 2.64, that is $CV = 2.64\\ \\mu$C — the charge the capacitor ends up "
                             "holding, not the current that put it there. If you got 0.0088, the 300 went in "
                             "as seconds rather than microseconds.",
                    "why": "The slope is $\\dfrac{12.0}{3.00\\times10^{-4}} = 4.00\\times10^{4}$ V/s, and "
                           "$i = C\\dfrac{dv}{dt} = 220\\times10^{-9} \\times 4.00\\times10^{4} = "
                           "8.80\\times10^{-3}$ A $= 8.80$ mA. Check it the other way round, which is the "
                           "habit worth building: the capacitor ends up holding $q = CV = 220\\times10^{-9} "
                           "\\times 12.0 = 2.64\\ \\mu$C, and delivering 2.64 µC in 300 µs is "
                           "$2.64\\times10^{-6}/3.00\\times10^{-4} = 8.80$ mA. Same number from the "
                           "derivative and from the charge, because they are the same statement.",
                },
                {
                    "title": "The peak current a sinusoid asks for",
                    "minutes": 7,
                    "brief": r'''
Two steps rather than one. The frequency is given in hertz and the derivative wants
radians per second, so there is a $2\pi$ to insert before the chain rule can be applied.

The peak of the current is not at the same instant as the peak of the voltage, and the
question only asks how big it gets.
''',
                    "prompt": r"What is the peak current into the capacitor?",
                    "note": "Give the answer in milliamperes, to two decimal places.",
                    "figure": "A 68.0 nF capacitor has $v(t) = 4.50\\cos(2\\pi \\times 1200\\,t)$ volts across "
                              "it, with $t$ in seconds. It has been running long enough that the start-up is "
                              "forgotten.",
                    "given": [
                        {"label": "Capacitance", "value": "68.0 nF"},
                        {"label": "Voltage amplitude", "value": "4.50 V"},
                        {"label": "Frequency", "value": "1.20 kHz"},
                    ],
                    "aside": "$\\omega = 2\\pi f$, in radians per second. A sine never exceeds 1, so the peak "
                             "of the current is whatever multiplies it.",
                    "answer": 2.31,
                    "tol": 0.02,
                    "unit": "mA",
                    "hint": "Differentiate: $\\dfrac{dv}{dt} = -4.50\\,\\omega\\sin(\\omega t)$. Multiply by "
                            "$C$ and take the largest size that expression reaches.",
                    "wrong": "If you got 0.367, the frequency went in as 1200 instead of "
                             "$\\omega = 2\\pi \\times 1200$; the $2\\pi$ is the whole difference between "
                             "cycles per second and radians per second. If you got 0.000306, the $\\omega$ "
                             "was dropped altogether.",
                    "why": "$\\omega = 2\\pi \\times 1200 = 7539.82$ rad/s. Differentiating, "
                           "$\\dfrac{dv}{dt} = -4.50 \\times 7539.82\\sin(\\omega t) = "
                           "-3.393\\times10^{4}\\sin(\\omega t)$ V/s, so the steepest the voltage ever gets "
                           "is $3.393\\times10^{4}$ V/s. Then $i_{\\text{peak}} = C \\times 3.393\\times10^{4} "
                           "= 68.0\\times10^{-9} \\times 3.393\\times10^{4} = 2.307\\times10^{-3}$ A "
                           "$= 2.31$ mA. The sine is at its own peak where the cosine is zero, so the "
                           "current is largest at the instants the voltage passes through zero — a quarter "
                           "cycle, 208 µs, before the voltage peaks.",
                },
                {
                    "title": "Integrating a current that changes its mind",
                    "minutes": 9,
                    "brief": r'''
Now the other direction, and with a starting value that is not zero. The current is a
ramp followed by a flat run, so the area under it is a triangle followed by a rectangle
— two pieces of school geometry, added.

The capacitor turns that area into a voltage, and then remembers where it began.
''',
                    "prompt": r"What is the voltage across the capacitor at $t = 5.00$ ms?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "figure": "A 4.70 µF capacitor is already sitting at 3.00 V when the clock starts. "
                              "From $t = 0$ the current into it rises in a straight line from 0 to 12.0 mA "
                              "over 2.00 ms, and then holds steady at 12.0 mA until $t = 5.00$ ms.",
                    "given": [
                        {"label": "Capacitance", "value": "4.70 µF"},
                        {"label": "Voltage at $t = 0$", "value": "3.00 V"},
                        {"label": "Current, 0 to 2.00 ms", "value": "0 rising to 12.0 mA"},
                        {"label": "Current, 2.00 to 5.00 ms", "value": "steady 12.0 mA"},
                        {"label": "Read the voltage at", "value": "5.00 ms"},
                    ],
                    "aside": "The area of a triangle is half base times height. Keep everything in coulombs "
                             "until the very last division.",
                    "answer": 13.21,
                    "tol": 0.05,
                    "unit": "V",
                    "hint": "Total the charge first: triangle plus rectangle. Then $\\Delta v = q/C$, and the "
                            "answer is $3.00 + \\Delta v$, not $\\Delta v$.",
                    "wrong": "If you got 10.21, the 3.00 V head start was dropped — the integral gives the "
                             "*change*, never the value. If you got 15.77, the whole 5 ms was treated as a "
                             "rectangle at 12.0 mA, which counts charge the ramp never delivered.",
                    "why": "The triangle contributes $\\tfrac12 \\times 2.00\\times10^{-3} \\times "
                           "12.0\\times10^{-3} = 1.20\\times10^{-5}$ C and the rectangle contributes "
                           "$3.00\\times10^{-3} \\times 12.0\\times10^{-3} = 3.60\\times10^{-5}$ C, so "
                           "$q = 4.80\\times10^{-5}$ C in total. Then $\\Delta v = q/C = "
                           "4.80\\times10^{-5}/4.70\\times10^{-6} = 10.21$ V, and the capacitor finishes at "
                           "$3.00 + 10.21 = 13.21$ V. Worth picturing the voltage as well as the number: for "
                           "the first 2 ms the current is a ramp, so the voltage is a *parabola* curving "
                           "upwards; after that the current is constant, so the voltage is a straight line. "
                           "Integration always produces a shape one degree smoother than the thing it "
                           "integrates.",
                },
                {
                    "title": "The instant the switch closes",
                    "minutes": 10,
                    "brief": r'''
A drawn circuit, and a question about the very first moment. The inductor has no current
in it before the supply is connected, and $v = L\frac{di}{dt}$ says its current cannot
jump — so an instant later the current is still zero.

Work out what that fact does to the resistor, and the inductor law will tell you the
rest. The question asks for a rate, not a current.
''',
                    "prompt": r"How fast is the current through the inductor rising at the instant the supply is connected?",
                    "note": "Give the answer in amperes per second, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                            {"id": "l1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 47e-3},
                            {"id": "r1", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 180},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V, connected at $t = 0$"},
                        {"label": "Inductance", "value": "47.0 mH"},
                        {"label": "Series resistance", "value": "180 Ω"},
                        {"label": "Inductor current before $t = 0$", "value": "0"},
                    ],
                    # The prompt asks for a slope, which is no node of this circuit. The transient is
                    # run, the probe voltage one step in is turned back into a current through the
                    # resistor the netlist actually contains, and that current is divided by the step
                    # — so a re-drawn schematic is re-measured rather than compared to a memory of it.
                    "check": r'''
const s = c.step(2.6e-5);
const r = c.net.parts.filter(function (p) { return p.kind === 'R'; })[0];
return (s.v[1] / r.value) / s.t[1];
''',
                    "answer": 255.3,
                    "tol": 1.0,
                    "unit": "A/s",
                    "hint": "Zero current through the resistor means zero volts across it. Kirchhoff's "
                            "voltage law then leaves the whole supply across the inductor, and "
                            "$\\frac{di}{dt} = v/L$.",
                    "wrong": "If you got 1.42, the *final* current was divided by the inductance: "
                             "$12/180 = 66.7$ mA is where the current ends up, not how fast it starts. "
                             "If you got 0.255, the inductance went in as 47 H rather than 47 mH.",
                    "why": "The inductor's current is continuous, so it is still 0 A the instant after the "
                           "switch closes. A resistor carrying no current has no voltage across it, so at "
                           "that instant the resistor might as well not be there and the full 12.0 V "
                           "appears across the inductor. Then $\\frac{di}{dt} = \\frac{v}{L} = "
                           "\\frac{12.0}{47.0\\times10^{-3}} = 255.3$ A/s. The resistor decides where the "
                           "current *ends up*, at $12/180 = 66.7$ mA, and the inductor decides how fast it "
                           "sets off. Divide one by the other and you get $0.0667/255.3 = 2.61\\times10^{-4}$ "
                           "s, which is $L/R$ — the time constant, and the time the current would take to "
                           "arrive if it kept that initial slope instead of easing off. Module 4 is about "
                           "what it does instead.",
                    "aside": "The same reasoning run backwards is why the resistor is invisible at $t = 0$ "
                             "and the inductor is invisible at $t = \\infty$: at the start the current is "
                             "fixed and at the end the slope is.",
                },
                {
                    "title": "How much energy is sitting on the board",
                    "minutes": 12,
                    "brief": r'''
The hardest of the set, and nothing in it is a node voltage. Once everything has settled
the capacitors have stopped taking current — $\frac{dv}{dt} = 0$, so $i = 0$ — which
means they are open circuits and the three resistors are simply a chain from the supply
to ground.

Find the two node voltages, then use $W = \frac12 CV^2$ on each capacitor and add. The
derivation elsewhere in this module is where that formula comes from; here it is just
being used.
''',
                    "prompt": r"How much energy is stored in the two capacitors once everything has settled?",
                    "note": "Give the answer in microjoules, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 15},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "r2", "kind": "R", "x": 12, "y": 4, "rot": 0, "value": 10000},
                            {"id": "c2", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 2.2e-7},
                            {"id": "r3", "kind": "R", "x": 18, "y": 6, "rot": 1, "value": 6800},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "g3", "kind": "GND", "x": 18, "y": 9},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 4], "b": [11, 4]},
                            {"a": [13, 4], "b": [15, 4]},
                            {"a": [15, 4], "b": [15, 5]},
                            {"a": [15, 4], "b": [18, 4]},
                            {"a": [18, 4], "b": [18, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [18, 7], "b": [18, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "15.0 V"},
                        {"label": "R1, top of the chain", "value": "4.70 kΩ"},
                        {"label": "R2, middle", "value": "10.0 kΩ"},
                        {"label": "R3, to ground", "value": "6.80 kΩ"},
                        {"label": "C1, at the R1–R2 node", "value": "100 nF"},
                        {"label": "C2, at the R2–R3 node", "value": "220 nF"},
                    ],
                    # Neither the node voltages nor the energy are repeated as constants here: the
                    # DC operating point is solved, every capacitor in the netlist is asked what
                    # voltage it ended up with, and the energies are summed and converted to
                    # microjoules. Redraw the chain differently and the check follows it.
                    "check": r'''
const d = c.dc();
let e = 0;
c.net.parts.filter(function (p) { return p.kind === 'C'; }).forEach(function (p) {
  const u = d.v[p.n1] - d.v[p.n2];
  e += 0.5 * p.value * u * u;
});
return e * 1e6;
''',
                    "answer": 9.345,
                    "tol": 0.03,
                    "unit": "µJ",
                    "hint": "One current flows through all three resistors. Get it from the supply and the "
                            "total resistance, then each node voltage is that current times whatever "
                            "resistance lies between the node and ground.",
                    "wrong": "If you got 36.0, both capacitors were put at the full 15 V; neither of them is "
                             "anywhere near it. If you got 18.7, the factor of $\\tfrac12$ was left out of "
                             "$W = \\tfrac12 CV^2$.",
                    "why": "With the capacitors open, the chain carries $I = 15.0/(4700 + 10000 + 6800) = "
                           "15.0/21500 = 697.7\\ \\mu$A. The R2–R3 node sits at "
                           "$I \\times 6800 = 4.744$ V and the R1–R2 node at "
                           "$I \\times (10000 + 6800) = 11.721$ V. Then "
                           "$W_1 = \\tfrac12 \\times 100\\times10^{-9} \\times 11.721^2 = 6.869\\ \\mu$J and "
                           "$W_2 = \\tfrac12 \\times 220\\times10^{-9} \\times 4.744^2 = 2.476\\ \\mu$J, "
                           "totalling $9.345\\ \\mu$J. Notice that the smaller capacitor holds the larger "
                           "share, by nearly three to one: energy goes as the *square* of the voltage and "
                           "only linearly with capacitance, so a factor of 2.47 in voltage beats a factor "
                           "of 2.2 in capacitance comfortably.",
                    "aside": "Nine microjoules is not much — a circuit drawing one watt gets through it in "
                             "9.3 µs. That is exactly the calculation behind every *hold-up time* figure: "
                             "how long the stored energy can feed the load once the supply disappears.",
                },
            ],
            "derive": {
                "title": "Where the half in $\\tfrac12 CV^2$ comes from",
                "minutes": 14,
                "vars": ["C", "L", "V", "v", "i", "p", "q", "t", "W"],
                "brief": r'''
Charging a capacitor takes work, because every extra coulomb has to be pushed onto a
plate that is already repelling it. The last coulomb is pushed across the full $V$; the
first one is pushed across nothing at all. So the answer cannot be $qV$, and the whole
question is what it is instead.

The tool is the one this module supplies. Energy is the integral of power,
$W = \int p\,dt$, power is $p = vi$, and the capacitor law $i = C\frac{dv}{dt}$ turns
that integral over time into an integral over voltage: substituting gives
$\int Cv\frac{dv}{dt}\,dt$, and the $dt$ cancels against the $dt$ in the derivative,
leaving an integral in $v$ alone.

Take $C$ and $L$ to be constants throughout, and start from an uncharged capacitor.
''',
                "steps": [
                    {
                        "prompt": r"Write the instantaneous power flowing into the capacitor, in terms of the voltage $v$ across it and the current $i$ into it.",
                        "answer": r"v i",
                        "placeholder": r"a product of two symbols",
                        "hint": r"A volt is a joule per coulomb and an amp is a coulomb per second, so their product is joules per second — which is a watt.",
                        "deconstruct": [
                            r"Power is energy per unit time.",
                            r"Each coulomb arriving at the plate carries $v$ joules with it, because that is what a volt means.",
                            r"Coulombs arrive at $i$ per second, so joules arrive at $vi$ per second.",
                        ],
                    },
                    {
                        "prompt": r"Substitute $i = C\frac{dv}{dt}$ and cancel the $dt$. Write the integrand that is now being integrated with respect to $v$.",
                        "answer": r"C v",
                        "placeholder": r"a constant times a variable",
                        "hint": r"$p\,dt = v \cdot C\frac{dv}{dt} \cdot dt$. The $dt$ on the outside cancels the one underneath the derivative, leaving something times $dv$.",
                        "deconstruct": [
                            r"$W = \int vi\,dt$ and $i = C\frac{dv}{dt}$, so $W = \int v\,C\frac{dv}{dt}\,dt$.",
                            r"The $dt$ cancels: $W = \int Cv\,dv$.",
                            r"What multiplies $dv$ is the integrand, and here that is $Cv$.",
                        ],
                    },
                    {
                        "prompt": r"Integrate that from $v = 0$ up to $v = V$. Write the stored energy $W$.",
                        "answer": r"\frac{1}{2} C V^2",
                        "placeholder": r"a fraction times C times a square",
                        "hint": r"$\int_0^V Cv\,dv$ is the area under a straight line of slope $C$, from 0 to $V$ — a triangle of base $V$ and height $CV$.",
                        "deconstruct": [
                            r"$\int v\,dv = \tfrac12 v^2$, by the power rule run backwards.",
                            r"Evaluated between 0 and $V$ that is $\tfrac12 V^2 - 0$.",
                            r"The constant $C$ comes outside the integral untouched.",
                        ],
                    },
                    {
                        "prompt": r"The charge delivered was $q = CV$. Had every coulomb of it been pushed across the full $V$, the work would have been $qV = CV^2$. Write the ratio of the true stored energy to that.",
                        "answer": r"\frac{1}{2}",
                        "placeholder": r"a pure number",
                        "hint": r"Divide the answer to the previous step by $CV^2$. Everything with a letter in it cancels.",
                        "deconstruct": [
                            r"$\dfrac{\tfrac12 CV^2}{CV^2}$.",
                            r"The $C$ cancels and the $V^2$ cancels.",
                            r"What is left is a pure number, and it is the same number for every capacitor and every voltage.",
                        ],
                    },
                    {
                        "prompt": r"Eliminate $V$ using $q = CV$, and write the same stored energy in terms of $q$ and $C$ only.",
                        "answer": r"\frac{q^2}{2 C}",
                        "placeholder": r"a square over something",
                        "hint": r"$V = q/C$. Put that into $\tfrac12 CV^2$ and simplify — one factor of $C$ survives, downstairs.",
                        "deconstruct": [
                            r"$\tfrac12 C\left(\dfrac{q}{C}\right)^2 = \tfrac12 C \dfrac{q^2}{C^2}$.",
                            r"One factor of $C$ cancels against one of the two underneath.",
                            r"That leaves $\dfrac{q^2}{2C}$ — the same energy, counted in charge instead of voltage.",
                        ],
                    },
                    {
                        "prompt": r"An inductor obeys $v = L\frac{di}{dt}$, which is the same statement with voltage and current exchanged. Run the identical argument and write the energy stored in an inductor carrying a current $i$.",
                        "answer": r"\frac{1}{2} L i^2",
                        "placeholder": r"the same shape with different letters",
                        "hint": r"$W = \int vi\,dt = \int L\frac{di}{dt}\,i\,dt = \int Li\,di$. Nothing else changes.",
                        "deconstruct": [
                            r"Power is still $vi$; this time it is the *voltage* that gets substituted.",
                            r"$\int Li\,di$ has exactly the shape of $\int Cv\,dv$.",
                            r"So the answer has exactly the shape of $\tfrac12 CV^2$, with $L$ for $C$ and current for voltage.",
                        ],
                    },
                ],
                "closing": r'''
Two formulas, one argument:

$$W_C = \tfrac12 CV^2 = \frac{q^2}{2C} \qquad W_L = \tfrac12 Li^2$$

Put numbers on the first. A 100 µF capacitor charged to 12 V is holding

```
W = 0.5 * 100e-6 * 12^2 = 0.5 * 100e-6 * 144 = 7.20e-3 J = 7.2 mJ
```

Now use the fourth step for something the arithmetic alone does not give you. Charge that
same capacitor from a 12 V supply through a resistor. The supply pushes
$q = CV = 1.2\times10^{-3}$ C out at 12 V throughout, so it gives up
$qV = CV^2 = 14.4$ mJ. The capacitor keeps 7.2 mJ. The other **7.2 mJ is dissipated in
the resistor** — and the resistance is nowhere in that sentence. Make it 1 Ω and the
current is enormous and brief; make it 1 MΩ and it is tiny and long; the heat is 7.2 mJ
either way. Exactly half of what the supply provides is thrown away, whatever you do,
which is why charging a capacitor through a resistor is never how a serious power supply
is built, and why switching converters — which use the *inductor* formula instead — exist
at all.

The inductor result is the one to keep in mind for the other reason. An inductor carrying
150 mA with $L = 100$ mH is sitting on $\tfrac12 \times 0.1 \times 0.15^2 = 1.125$ mJ, and
that energy has to go somewhere the instant you open the switch. If you give it nowhere
to go it makes its own arc, at whatever voltage that takes.
''',
            },
            "build": {
                "title": "Integration you can watch",
                "minutes": 20,
                "brief": r'''
There is a capacitor on the canvas already, with a probe on its top plate and its
bottom plate grounded. Nothing is driving it, so the probe reads a flat zero.

Add a **current source** — the part marked `I` — and wire it so that a steady
current flows into that capacitor. A current source pushes a fixed number of amps
around the loop regardless of what voltage that takes, which is the electrical way
of saying "the input is a constant".

The capacitor then integrates that constant. Get the values right and the probe
voltage must **climb in a straight line at exactly 1 volt per millisecond**, so it
reads 1 V after 1 ms, 2 V after 2 ms, and is still climbing at the same rate at
3 ms. Straight, not curved: this is the integral of a constant.

From $i = C\dfrac{dv}{dt}$, a constant current $I$ gives a slope of
$\dfrac{dv}{dt} = \dfrac{I}{C}$, so it is the *ratio* you have to get right. Any
current and capacitance with that ratio will pass.

To run it yourself, choose **Transient** in the analysis panel, set *Stop after* to
`3m`, and press Solve.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "C", "x": 3, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 3, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 3], "b": [3, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "C", "x": 3, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 3, "y": 3},
                        {"id": "p3", "kind": "I", "x": 4, "y": 4, "rot": 0, "value": 1e-3},
                        {"id": "p4", "kind": "GND", "x": 5, "y": 6},
                    ],
                    "wires": [
                        {"a": [3, 3], "b": [3, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [5, 4], "b": [5, 6]},
                    ],
                },
                "checks": [
                    {"name": "the probe starts at zero and rises", "code": r'''
const s = c.step(3e-3);
c.assert(Math.abs(s.v[0]) < 0.02, "an uncharged capacitor starts at 0 V, but the probe begins at " +
  c.fmt(s.v[0], "V"));
c.assert(s.v[s.v.length - 1] > 0.5, "after 3 ms the probe reads " + c.fmt(s.v[s.v.length - 1], "V") +
  "; it should have climbed to about 3 V. If it went downwards, the current is flowing the wrong way.");
'''},
                    {"name": "one millisecond in, it reads 1 volt", "code": r'''
const s = c.step(3e-3);
let k = 0;
for (let i = 1; i < s.t.length; i++) {
  if (Math.abs(s.t[i] - 1e-3) < Math.abs(s.t[k] - 1e-3)) k = i;
}
c.close(s.v[k], 1.0, 0.05, "the probe voltage after 1 ms");
'''},
                    {"name": "two milliseconds in, it reads 2 volts", "code": r'''
const s = c.step(3e-3);
let k = 0;
for (let i = 1; i < s.t.length; i++) {
  if (Math.abs(s.t[i] - 2e-3) < Math.abs(s.t[k] - 2e-3)) k = i;
}
c.close(s.v[k], 2.0, 0.05, "the probe voltage after 2 ms — twice the time, twice the voltage");
'''},
                    {"name": "the climb does not flatten off", "code": r'''
const s = c.step(3e-3);
const n = s.t.length - 1;
const m = Math.round(n * 2 / 3);
const slope = (s.v[n] - s.v[m]) / (s.t[n] - s.t[m]);
c.close(slope, 1000, 0.05, "the slope over the last millisecond, in volts per second");
'''},
                ],
                "hints": [
                    "One millisecond is $10^{-3}$ s, so 1 volt per millisecond is a slope of 1000 volts per second. You need $I/C = 1000$.",
                    "With the capacitor left at 1 µF, that means a current of 1 mA. Type it as `1m` in the value box.",
                    "The current source needs a complete loop: one end on the capacitor's top node, the other end down to a ground of its own.",
                    "If the voltage ramps downwards instead of upwards, the source is pushing current the other way round. Rotate it, or swap which of its two ends you grounded.",
                ],
            },
            "lab": {
                "title": "Slopes and areas from samples",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
The circuit you just built did the integration in hardware. Now do both operations
in software, on lists of measured samples — which is what an oscilloscope, or any
simulator, actually has to work with.

`cap_current(times, volts, C)` returns the current into a capacitor at each sample,
using $i = C\frac{dv}{dt}$. Estimate the slope with a **central difference**: at
sample $k$ in the middle of the list,

$$\frac{dv}{dt} \approx \frac{v_{k+1} - v_{k-1}}{t_{k+1} - t_{k-1}}$$

At the two ends there is no neighbour on one side, so use the one-sided difference
with the sample that does exist.

`cap_voltage(times, currents, C)` goes the other way: $v = \frac{1}{C}\int i\,dt$,
starting from 0 V, using the **trapezoid rule**. Each step adds the area of a
trapezoid of width $t_k - t_{k-1}$ and average height $(i_k + i_{k-1})/2$, then
divides by $C$. Return a list the same length as `times`, beginning with `0.0`.

Both rules are exact when the thing they are applied to is a straight line, which
is why the checks start there.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def cap_current(times, volts, C):
    """Return i = C dv/dt at every sample: central differences inside, one-sided at the ends."""
    # TODO: build a list the same length as `times`.
    return []


def cap_voltage(times, currents, C):
    """Return v = (1/C) * integral of i dt at every sample, starting from 0 V."""
    # TODO: trapezoid rule, accumulating as you go. First entry is 0.0.
    return []


if __name__ == "__main__":
    ts = [k * 1e-5 for k in range(101)]
    vs = [1000.0 * t for t in ts]          # a 1 V per ms ramp, as in the circuit
    C = 1e-6
    i = cap_current(ts, vs, C)
    print("current into the capacitor:", i[:3], "...")
    back = cap_voltage(ts, i, C)
    print("integrated back to:", round(back[-1], 6), "V after", ts[-1], "s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def cap_current(times, volts, C):
    """Return i = C dv/dt at every sample: central differences inside, one-sided at the ends."""
    n = len(times)
    out = []
    for k in range(n):
        if k == 0:
            slope = (volts[1] - volts[0]) / (times[1] - times[0])
        elif k == n - 1:
            slope = (volts[n - 1] - volts[n - 2]) / (times[n - 1] - times[n - 2])
        else:
            slope = (volts[k + 1] - volts[k - 1]) / (times[k + 1] - times[k - 1])
        out.append(C * slope)
    return out


def cap_voltage(times, currents, C):
    """Return v = (1/C) * integral of i dt at every sample, starting from 0 V."""
    out = [0.0]
    for k in range(1, len(times)):
        h = times[k] - times[k - 1]
        area = h * (currents[k] + currents[k - 1]) / 2.0
        out.append(out[-1] + area / C)
    return out


if __name__ == "__main__":
    ts = [k * 1e-5 for k in range(101)]
    vs = [1000.0 * t for t in ts]          # a 1 V per ms ramp, as in the circuit
    C = 1e-6
    i = cap_current(ts, vs, C)
    print("current into the capacitor:", i[:3], "...")
    back = cap_voltage(ts, i, C)
    print("integrated back to:", round(back[-1], 6), "V after", ts[-1], "s")
'''}],
                "hints": [
                    "Handle the three cases in order: `k == 0`, `k == n - 1`, and everything in between. The central difference spans *two* steps, so its denominator is `times[k+1] - times[k-1]`, not one step.",
                    "Do not forget to multiply the slope by `C`. The units only work out as amps if you do.",
                    "In `cap_voltage`, start the output list as `[0.0]` and append one entry per gap between samples. The list then ends up the same length as `times`.",
                    "Check yourself on the ramp before running anything else: a straight line of slope 1000 V/s through a 1 µF capacitor must give exactly 1 mA at every single sample, ends included.",
                ],
                "tests": [
                    {"name": "a straight ramp gives a constant current", "code": r'''
_ts = [k * 1e-5 for k in range(101)]
_vs = [1000.0 * t for t in _ts]
_i = cap_current(_ts, _vs, 1e-6)
assert len(_i) == len(_ts), f"expected {len(_ts)} samples of current, got {len(_i)}"
for _k, _val in enumerate(_i):
    assert abs(_val - 1e-3) < 1e-12, \
        f"sample {_k} should be 1 mA everywhere on a straight ramp, got {_val}"
'''},
                    {"name": "the ends are handled too", "code": r'''
_ts = [0.0, 1e-5, 2e-5, 3e-5]
_vs = [0.0, 2.0, 4.0, 6.0]
_i = cap_current(_ts, _vs, 2e-6)
assert abs(_i[0] - 0.4) < 1e-12, f"first sample should use a one-sided slope: 2e-6 * 2e5 = 0.4 A, got {_i[0]}"
assert abs(_i[-1] - 0.4) < 1e-12, f"last sample should do the same, got {_i[-1]}"
'''},
                    {"name": "a sinusoid gives the chain rule back", "code": r'''
import math
_w = 2.0 * math.pi * 50.0
_ts = [k * 1e-5 for k in range(2001)]
_vs = [math.sin(_w * t) for t in _ts]
_i = cap_current(_ts, _vs, 1e-6)
_want = 1e-6 * _w
assert abs(_i[0] - _want) < 1e-9, \
    f"at t=0 the slope is w*cos(0) = {_w:.4f}, so i should be {_want:.6e}, got {_i[0]:.6e}"
assert abs(max(_i) - _want) < 1e-9, \
    f"the peak current should be C*w = {_want:.6e}, got {max(_i):.6e}"
'''},
                    {"name": "a constant current integrates to a ramp", "code": r'''
_ts = [k * 1e-5 for k in range(101)]
_is = [1e-3] * len(_ts)
_v = cap_voltage(_ts, _is, 1e-6)
assert len(_v) == len(_ts), f"expected {len(_ts)} samples of voltage, got {len(_v)}"
assert abs(_v[0]) < 1e-15, f"it must start from 0 V, got {_v[0]}"
assert abs(_v[-1] - 1.0) < 1e-12, \
    f"1 mA into 1 uF for 1 ms is exactly 1 V, got {_v[-1]}"
assert abs(_v[50] - 0.5) < 1e-12, f"halfway through it should be at 0.5 V, got {_v[50]}"
'''},
                    {"name": "a rising current integrates to a curve", "code": r'''
_ts = [k * 1e-5 for k in range(101)]
_is = [1.0 * t for t in _ts]
_v = cap_voltage(_ts, _is, 1e-6)
assert abs(_v[-1] - 0.5) < 1e-12, \
    f"the area under a triangle of height 1e-3 and width 1e-3 is 5e-7 C, so 0.5 V, got {_v[-1]}"
'''},
                    {"name": "differentiating then integrating returns the original", "code": r'''
import math
_ts = [k * 1e-5 for k in range(501)]
_vs = [3.0 * math.sin(2.0 * math.pi * 50.0 * t) for t in _ts]
_back = cap_voltage(_ts, cap_current(_ts, _vs, 1e-6), 1e-6)
for _k in range(0, len(_ts), 25):
    assert abs(_back[_k] - _vs[_k]) < 2e-3, \
        f"at sample {_k} the round trip gave {_back[_k]:.6f} against the original {_vs[_k]:.6f}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "First-order equations, and equations solved all at once",
            "summary": "One equation that involves a rate of change, and several equations that must hold simultaneously. Circuits produce both.",
            "concepts": [
                "A **differential equation** is an equation containing a derivative. A resistor and a capacitor in series across a source obey $\\frac{dv}{dt} = \\frac{V_s - v}{RC}$: the rate of change depends on how far you still have to go.",
                "Its solution, starting from $v(0) = 0$, is $v(t) = V_s\\left(1 - e^{-t/RC}\\right)$. You do not have to take that on trust: differentiate it, put both sides of the equation side by side, and they agree.",
                "The product $RC$ has units of seconds and is called the **time constant**, written $\\tau$. After one $\\tau$ the response has covered $1 - e^{-1} = 63.2\\%$ of the distance; after five, 99.3%.",
                "An inductor and a resistor give the same equation with $\\tau = L/R$. One resistor and one energy store always produce a first-order equation, whichever store it is.",
                "A network of resistors instead gives **simultaneous equations**: one current-balance equation per node, all of which must hold at once.",
                "Those equations are written as a matrix: $G\\mathbf{v} = \\mathbf{i}$, where each diagonal entry of $G$ is the sum of the conductances at that node and each off-diagonal entry is minus the conductance joining two nodes.",
                "A 2×2 system is solved by the **determinant**: $\\det = a_{11}a_{22} - a_{12}a_{21}$, and there is a single answer exactly when that determinant is not zero.",
            ],
            "read": [
                {
                    "title": "Nothing is instant, and one product says how slow",
                    "minutes": 15,
                    "body": r'''
Wire a lamp to a battery through a switch. Close the switch and the lamp is lit — not
lit a moment later, lit. Every equation module 1 and module 2 needed was of that kind:
you put a voltage somewhere, and the currents that follow are settled before you can
look at them.

Now put a capacitor across the far end of a resistor and close the switch again. The
voltage on the capacitor does something the resistor on its own never does. It starts
at zero, climbs steeply, bends over, and creeps towards the supply without ever quite
arriving. Nothing about the switch has changed. What has changed is that the circuit
now contains something that **stores** — and a store cannot be filled instantly, because
filling it takes charge and charge arrives at a finite rate.

This unit is about the curve that comes out, the single number that describes it, and
how to answer both questions you will ever be asked about it: what the voltage is at a
stated time, and at what time it reaches a stated voltage.

## Two laws, pointing at the same current

Draw the circuit as a loop: a source of $V_s$ volts, a resistor $R$, and a capacitor
$C$ whose lower plate is grounded. Call the voltage on the capacitor $v$. It is the
only thing in the circuit that is not already known.

There is exactly one current in this loop, and two different laws describe it.

The resistor's law is Ohm's. The voltage across the resistor is what the source has
minus what the capacitor has already taken, so

$$i = \frac{V_s - v}{R}$$

The capacitor's law is module 3's: current is charge per second, and charge on a
capacitor is $Cv$, so

$$i = C\frac{dv}{dt}$$

Those are the same current, because there is nowhere else for it to go. Setting them
equal and dividing through by $C$:

$$\frac{dv}{dt} = \frac{V_s - v}{RC}$$

That is a **differential equation** — an equation with a derivative in it — and it is
the first one in this course. Read it in words before you solve it, because the words
are the physics: *the speed at which the voltage rises is proportional to how far it
still has to go.* Start at zero and the gap is the whole supply, so the climb is at its
steepest. Get half way and the gap has halved, so the climb has halved with it. Arrive
and the gap is nothing, so the climb stops. Nothing forces the curve to bend over; the
bending is the only behaviour that sentence permits.

## Solving it without guessing

Let $u = V_s - v$ — the gap still to be crossed. Since $V_s$ is a constant,
$\frac{du}{dt} = -\frac{dv}{dt}$, and the equation becomes

$$\frac{du}{dt} = -\frac{u}{RC}$$

which is the equation module 3 already answered: the rate of change is proportional to
what is left, and the only function with that property is the exponential. So
$u = u_0e^{-t/RC}$. If the capacitor starts empty then $v(0) = 0$, the initial gap is
$u_0 = V_s$, and putting $v$ back:

$$V_s - v = V_se^{-t/RC} \qquad\Longrightarrow\qquad v(t) = V_s\left(1 - e^{-t/RC}\right)$$

You never have to take that on trust. Differentiate it — the chain rule gives a factor
of $-1/RC$ — and you get $\frac{dv}{dt} = \frac{V_s}{RC}e^{-t/RC}$, while the right-hand
side of the original equation, $\frac{V_s - v}{RC}$, is $\frac{V_s}{RC}e^{-t/RC}$ as
well. They agree everywhere, which is what it means to be a solution.

## Why the product is a time

The exponent $t/RC$ has to be a pure number — you cannot raise $e$ to a power measured
in seconds — so $RC$ must be a time. Check it the long way once:

```
an ohm    = volt / amp
a farad   = coulomb / volt
ohm*farad = (volt/amp) * (coulomb/volt) = coulomb / amp
an amp    = coulomb / second
so        coulomb / (coulomb/second) = second
```

That product is the **time constant**, written $\tau$. Two consequences follow
immediately and both are worth memorising:

* After one $\tau$, the response has covered $1 - e^{-1} = 0.632$, or 63.2%, of the
  distance from where it started to where it is going. After two, 86.5%; after three,
  95.0%; after five, 99.3%.
* $\tau$ depends on the **product** only. A 1 kΩ with a 1 µF and a 10 kΩ with a 100 nF
  behave identically. The circuit does not know which pair you picked.

For arithmetic, learn the pairing that avoids powers of ten: **kilohms times microfarads
gives milliseconds**, and megohms times microfarads gives seconds. A 4.7 kΩ with a
2.2 µF is $4.7 \times 2.2 = 10.34$ ms and no exponent has to be written down at all.

### Worked: 9 volts, 10 kΩ, 47 nF

```
tau = R C = 1.0e4 * 47e-9 = 4.70e-4 s = 470 us

v(t) = 9 * (1 - e^(-t/470us))

t =    0 us   e^0       = 1          v = 0        V
t =  100 us   e^-0.2128 = 0.808345   v = 1.7249   V
t =  200 us   e^-0.4255 = 0.653422   v = 3.1192   V
t =  470 us   e^-1      = 0.367879   v = 5.6891   V   <- one tau, 63.2%
t = 1000 us   e^-2.1277 = 0.119116   v = 7.9280   V
t = 2350 us   e^-5      = 0.006738   v = 8.9394   V   <- five tau, 99.3%
```

Two independent checks on that table. First, the slope at $t = 0$ should be
$V_s/\tau = 9/4.70\times10^{-4} = 19149$ V/s; the first hundred microseconds cover
1.7249 V, which at a constant 19149 V/s would have been 1.9149 V, so the curve has
already bent over slightly — as it must. Second, and better, at $t = 0$ the capacitor
holds nothing, so the whole 9 V is across the resistor and Ohm's law gives
$i = 9/10^4 = 0.900$ mA. Feed that to the capacitor law:
$\frac{dv}{dt} = i/C = 9.00\times10^{-4}/47\times10^{-9} = 19149$ V/s. Two laws that
were never told about each other agree to five figures.

### Worked backwards: when does it pass 5 V?

The same formula, rearranged. This is where module 5's logarithm earns its place, and
the rearrangement is worth doing once slowly:

```
v  = Vs (1 - e^(-t/tau))
v / Vs         = 1 - e^(-t/tau)
e^(-t/tau)     = 1 - v/Vs = (Vs - v)/Vs
-t/tau         = ln((Vs - v)/Vs)
t              = tau * ln(Vs / (Vs - v))

Vs = 9, v = 5:   Vs - v = 4
t = 470us * ln(9/4) = 470us * ln(2.25) = 470us * 0.81093 = 381.1 us
```

381 µs, which sits sensibly below the 470 µs that reaches 5.69 V. The same line gives
the half-way time for any first-order circuit at all: put $v = V_s/2$ and the ratio is
2, so $t_{1/2} = \tau\ln 2 = 0.693\tau$ — here 326 µs. Note that the *half* way point
comes before the *63%* point, which is the sanity check most likely to catch a
rearrangement done in a hurry.

## The same equation, with the other kind of store

Swap the capacitor for an inductor and put the resistor in series with it. Module 3's
inductor law is $v_L = L\frac{di}{dt}$, and Kirchhoff round the loop says
$V_s = L\frac{di}{dt} + iR$, so

$$\frac{di}{dt} = \frac{V_s - iR}{L} = \frac{V_s/R - i}{L/R}$$

which is the identical shape with $i$ in place of $v$, a final value of $V_s/R$ in place
of $V_s$, and

$$\tau = \frac{L}{R}$$

Note that the resistor is now **downstairs**. A bigger resistor makes an RC circuit
slower and an RL circuit *faster*, and getting that backwards is a genuinely common
slip.

### Worked: 12 V into 100 mH and 220 Ω

```
tau = L/R = 0.100 / 220 = 4.5455e-4 s = 454.5 us
final current = Vs/R = 12/220 = 54.545 mA

i(t) = 54.545 mA * (1 - e^(-t/454.5us))

t =    0 us    i =  0        mA     v across R =  0.000 V
t =  200 us    i = 19.416    mA     v across R =  4.272 V
t =  455 us    i = 34.479    mA     v across R =  7.585 V
t = 1000 us    i = 48.502    mA     v across R = 10.670 V
```

Check the start: at $t = 0$ the inductor carries no current, so the resistor drops
nothing and the whole 12 V is across the inductor, giving
$\frac{di}{dt} = V_s/L = 12/0.1 = 120$ A/s. Over the first 200 µs that rate alone would
build $120 \times 2\times10^{-4} = 24.0$ mA, and the real answer is 19.4 mA — bent over,
again, and by about the amount the exponential predicts. Check the finish: after several
$\tau$ the current stops changing, so the inductor drops nothing and the resistor has
the lot, 12 V across 220 Ω, 54.5 mA. At 1 ms the resistor has 10.670 V of that and the
inductor still holds the remaining 1.330 V, because 1 ms is only 2.2 time constants and
the current is still climbing.

## The mistakes people actually make

**63% and 37% are the same fact, and get swapped.** $e^{-1} = 0.368$ is the fraction
*remaining*; $1 - e^{-1} = 0.632$ is the fraction *covered*. A rising response is at 63%
after one $\tau$; a falling one is at 37%. Both numbers are correct and each is the
wrong answer to the other question.

**Treating $\tau$ as "how long it takes".** It never takes $\tau$; it never finishes at
all. What $\tau$ buys you is a scale: below one $\tau$ nothing much has happened, past
five $\tau$ nothing much is left to happen, and every first-order circuit ever built
looks the same on a horizontal axis marked in $\tau$. When a datasheet says a signal
settles in 3 µs it means five time constants of something.

**Assuming the capacitor started empty.** $V_s(1 - e^{-t/\tau})$ is one special case of
a general rule that costs nothing extra:

$$v(t) = v_\infty + (v_0 - v_\infty)e^{-t/\tau}$$

*where it ends up, plus the initial error, decaying.* Set $v_0 = 0$ and you recover the
charging formula; set $v_\infty = 0$ and you get the discharge, $v_0e^{-t/\tau}$. One
formula, three questions.

**Believing a bigger capacitor charges to a bigger voltage.** It does not. The final
voltage is $V_s$ whatever $C$ is — the source decides that, and $C$ decides only how
long the journey takes and how much charge is required to complete it.

## Where this stops holding

**Two stores, and the curve can overshoot.** Everything above needed exactly one energy
store. Put a capacitor *and* an inductor in the same loop and the equation acquires a
second derivative, its solution can ring past the target and come back, and one time
constant is no longer enough to describe it. That is module 6, where $\tau$ is replaced
by a natural frequency $\omega_n$ and a damping ratio $\zeta$.

**A resistor that is not a resistor.** The derivation used $i = (V_s - v)/R$ with $R$
constant. A diode's current is exponential in its voltage, so the equation stops being
linear, the exponential solution stops being right, and there is no formula to
rearrange at all. Module 8 gets those answers by iterating instead.

**A source that is not a step.** $v = V_s(1 - e^{-t/\tau})$ assumed $V_s$ was switched
on once and left alone. Drive the same circuit with a sinusoid instead and the answer is
module 2's: after the initial transient dies away, the output is the input multiplied by
$1/(1 + j\omega RC)$, and the same $RC$ reappears as a corner frequency
$f_c = 1/(2\pi RC)$. It is the same circuit and the same number, seen in the frequency
domain instead of the time domain, and $\tau$ and $f_c$ are reciprocals up to that
$2\pi$.

**Real parts have more than one number on them.** An inductor's winding has resistance,
and it is in series with everything, so a 100 mH coil with 8 Ω of wire in a circuit with
a 220 Ω resistor actually runs at $\tau = 0.1/228 = 439$ µs, not 455. A capacitor leaks,
so a genuinely long time constant — say a 100 µF across 1 MΩ, nominally
$\tau = 100$ s — is set as much by the part's own leakage as by the resistor you chose.
And that same slow circuit is why a charged capacitor is worth respecting: starting at
12 V, after a full minute it is still at $12e^{-0.6} = 6.59$ V, and it takes
$100\ln 12 = 248$ s to fall below a volt.
''',
                },
                {
                    "title": "One equation per node, and no way to take them one at a time",
                    "minutes": 15,
                    "body": r'''
Here is a voltage divider: 12 V, a 1 kΩ from the supply down to a middle node, a 3.3 kΩ
from that node down to ground. The middle node sits at

$$12 \times \frac{3300}{1000 + 3300} = 9.209\ \text{V}$$

and you can do that in your head because the two resistors carry the *same current*.
One current, one unknown, one division.

Now hang something off that middle node: a 2.2 kΩ going sideways to a second node, and
a 4.7 kΩ from that second node down to ground. Try to repeat the trick and it comes
apart. The current through the 1 kΩ is no longer the current through the 3.3 kΩ, because
some of it now turns off at the middle. How much turns off depends on the voltage at the
middle node. And the voltage at the middle node depends on how much current went through
the 1 kΩ. You cannot start, because whichever end you start from, the thing you need is
the thing you are trying to find.

That circularity is not a failure of cleverness. It is the signature of a problem whose
answer is fixed by several conditions holding **at once**, and the way out is to stop
trying to compute the unknowns one at a time and instead write down every condition,
then solve them together.

## Ground first, then one balance per node

The recipe has four steps and never changes.

1. **Pick a ground.** Voltages are differences, so one node has to be called zero. Then
   every other node has a number, and there are $n - 1$ unknowns for $n$ nodes.
2. **Cross off the nodes you already know.** A node wired straight to a voltage source
   is not an unknown; it is $V_s$.
3. **Write one current balance at each remaining node.** Kirchhoff's current law: charge
   does not pile up anywhere, so the currents leaving a node sum to zero. The current
   leaving node $a$ through a resistor $R$ towards node $b$ is $(v_a - v_b)/R$, always,
   with no thought required about which way it really flows — if the algebra comes out
   negative, it flows the other way.
4. **Solve the set.**

Apply that to the circuit above. Call the middle node $v_1$ and the far node $v_2$, with
$R_1 = 1\ \text{k}\Omega$ from the 12 V supply, $R_2 = 3.3\ \text{k}\Omega$ from $v_1$
to ground, $R_3 = 2.2\ \text{k}\Omega$ between the two nodes, and
$R_4 = 4.7\ \text{k}\Omega$ from $v_2$ to ground.

$$\text{node 1:}\quad \frac{v_1 - 12}{1000} + \frac{v_1}{3300} + \frac{v_1 - v_2}{2200} = 0$$

$$\text{node 2:}\quad \frac{v_2 - v_1}{2200} + \frac{v_2}{4700} = 0$$

Three terms in the first, because three components touch node 1; two in the second.
Every term has the same form and the same sign, which is the whole reason for insisting
on *leaving* rather than *arriving*.

### Worked: the loaded divider, all the way through

Collect the coefficients of $v_1$ and $v_2$, and move the known source term to the
right:

```
node 1:  (1/1000 + 1/3300 + 1/2200) v1 - (1/2200) v2 = 12/1000

         1/1000 = 1.000000e-3
         1/3300 = 3.030303e-4
         1/2200 = 4.545455e-4          sum = 1.757576e-3

node 2:  -(1/2200) v1 + (1/2200 + 1/4700) v2 = 0

         1/2200 = 4.545455e-4
         1/4700 = 2.127660e-4          sum = 6.673114e-4
```

The second equation is the easier one, so use it to get $v_1$ in terms of $v_2$:

```
v1 = v2 * 6.673114e-4 / 4.545455e-4 = 1.468085 * v2
```

Substitute into the first:

```
1.757576e-3 * 1.468085 * v2 - 4.545455e-4 * v2 = 0.012
(2.580271e-3 - 4.545455e-4) v2 = 0.012
2.125725e-3 * v2 = 0.012
v2 = 5.64513 V
v1 = 1.468085 * 5.64513 = 8.28753 V
```

Now check it, because a solved system that satisfies nothing is worthless. Currents:

```
through R1:  (12 - 8.28753)/1000 = 3.71247 mA
through R2:   8.28753/3300        = 2.51137 mA
through R3:  (8.28753 - 5.64513)/2200 = 1.20109 mA
through R4:   5.64513/4700        = 1.20109 mA

node 1:  3.71247 = 2.51137 + 1.20109 = 3.71246   ok
node 2:  R3 and R4 carry the same current        ok
```

And look at what the answer says. The unloaded divider sat at 9.209 V; loaded, its
middle node has sagged to 8.288 V. The load did not merely take a little current, it
moved the very voltage it was measuring — which is the single most important practical
fact in this module, and the reason a voltmeter is built with a 10 MΩ input.

## The same two equations, written as a matrix

Look again at the two lines of coefficients. There is a pattern in them, and it is
worth naming because it means you can write the equations down without deriving them
each time.

$$\begin{bmatrix} \frac{1}{R_1} + \frac{1}{R_2} + \frac{1}{R_3} & -\frac{1}{R_3} \\[4pt]
-\frac{1}{R_3} & \frac{1}{R_3} + \frac{1}{R_4}\end{bmatrix}
\begin{bmatrix} v_1 \\ v_2 \end{bmatrix} =
\begin{bmatrix} \frac{V_s}{R_1} \\ 0 \end{bmatrix}$$

* Every entry is a **conductance**, $1/R$, in siemens. Not a resistance. Currents add at
  a node, and current per volt is $1/R$, so $1/R$ is what adds.
* The **diagonal** entry of row $k$ is the sum of every conductance touching node $k$ —
  including the ones that go to ground and the ones that go to a source.
* The **off-diagonal** entry joining nodes $j$ and $k$ is *minus* the conductance between
  them, and it appears twice, symmetrically. The minus sign is there because raising a
  neighbour's voltage pushes current *into* your node, which is the opposite of your own
  voltage pushing it out.
* The **right-hand side** is the current injected into each node by sources. A current
  source of $I$ amps into node $k$ puts $I$ there directly, which is why current sources
  are the easy case. A voltage source $V_s$ feeding node $k$ through $R$ contributes
  $V_s/R$ — the current that would flow if the node were at zero.

That matrix is called $G$, and $G\mathbf{v} = \mathbf{i}$ is the whole of resistive
circuit analysis. It is also, almost line for line, what the analysis panel in this
course assembles before it solves anything.

## Determinants, and the answer in closed form

For a 2×2 system

$$a_{11}x_1 + a_{12}x_2 = b_1, \qquad a_{21}x_1 + a_{22}x_2 = b_2$$

eliminating $x_2$ by hand gives $x_1(a_{11}a_{22} - a_{12}a_{21}) = b_1a_{22} - a_{12}b_2$,
and the bracket that appears is the **determinant**:

$$\det = a_{11}a_{22} - a_{12}a_{21}, \qquad
x_1 = \frac{b_1a_{22} - a_{12}b_2}{\det}, \qquad
x_2 = \frac{a_{11}b_2 - b_1a_{21}}{\det}$$

Each numerator is the determinant of the same matrix with one column replaced by the
right-hand side; that is Cramer's rule. On the numbers above:

```
det = 1.757576e-3 * 6.673114e-4 - (4.545455e-4)^2
    = 1.172850e-6 - 2.066116e-7
    = 9.662388e-7

v1 = (0.012 * 6.673114e-4 - 0) / 9.662388e-7 = 8.007737e-6 / 9.662388e-7 = 8.28753 V
v2 = (0 + 0.012 * 4.545455e-4) / 9.662388e-7 = 5.454545e-6 / 9.662388e-7 = 5.64513 V
```

The same two numbers, from a route that needed no rearranging and no judgement about
which equation to start with. That is what makes it mechanical enough to hand to a
computer — and mechanical enough that the lab at the end of this module is six lines
long.

### Worked: a current source, where the right-hand side is obvious

Take 1.50 mA pushed into node 1, a 10 kΩ from node 1 to ground, a 22 kΩ from node 1 to
node 2, and a 47 kΩ from node 2 to ground. No voltage source anywhere, so the
right-hand side is just the injected current.

```
g11 = 1/10k + 1/22k  = 1.000000e-4 + 4.545455e-5 = 1.454545e-4
g12 = g21 = -1/22k                               = -4.545455e-5
g22 = 1/22k + 1/47k  = 4.545455e-5 + 2.127660e-5 = 6.673114e-5
b   = (1.5e-3, 0)

det = 1.454545e-4 * 6.673114e-5 - (4.545455e-5)^2
    = 9.706348e-9 - 2.066116e-9 = 7.640232e-9

v1 = 1.5e-3 * 6.673114e-5 / 7.640232e-9 = 1.000967e-7 / 7.640232e-9 = 13.1013 V
v2 = 1.5e-3 * 4.545455e-5 / 7.640232e-9 = 6.818182e-8 / 7.640232e-9 =  8.9241 V
```

Check it against something simpler. With no source in the way, the 22 k and 47 k are in
series — 69 kΩ — and that sits in parallel with the 10 kΩ:
$10 \times 69 / 79 = 8.7342$ kΩ. All 1.50 mA goes through that, so
$v_1 = 1.5\ \text{mA} \times 8.7342\ \text{k}\Omega = 13.101$ V, and $v_2$ is $v_1$
divided down by $47/69 = 0.68116$, giving 8.924 V. Both agree to five figures.

## The mistakes people actually make

**Resistances in the matrix instead of conductances.** This is the error, and it
produces answers wrong by orders of magnitude rather than a little. The rule to hold on
to is that KCL adds *currents*, so whatever multiplies a voltage in these equations must
turn volts into amps, and that is $1/R$.

**Losing a minus sign off the diagonal.** With all-positive off-diagonals, the two
equations describe a circuit where raising one node raises its neighbour's current
outward, and you will get an answer above the supply rail. If a node voltage comes out
larger than every source in the circuit, this is the first thing to check.

**Giving ground an off-diagonal partner.** A resistor from node 1 to ground contributes
to $G_{11}$ and to nothing else, because ground is not an unknown — its voltage is
zero, so its column was struck out. Every resistor contributes to the diagonal; only the
ones spanning *two unknowns* contribute off it.

**Writing an equation for the source node.** A node wired to a voltage source has a
known voltage. Writing KCL there adds an unknown — the current in the source — for no
gain. Leave it out, and let it appear on the right-hand side as $V_s/R$.

## Where this stops holding

**The determinant is zero.** Then there is no single answer, and the circuit is telling
you something real: two equations that are secretly the same one. It happens when part
of a network has no resistive path to ground at all — the app says *under-determined* and
refuses — and it happens with two ideal voltage sources wired in parallel with different
values, which is a contradiction rather than a circuit. A determinant that is merely
*small* is a warning of its own: the answer exists but is extremely sensitive to the
component values, which is exactly the situation a precision bridge is deliberately
built into.

**Cramer's rule does not scale.** It is unbeatable at 2×2, tolerable at 3×3, and beyond
that the work grows like $n!$ while Gaussian elimination — the same eliminating you did
by hand above, done systematically — grows like $n^3$. A simulator with ten thousand
nodes does elimination, and it never forms a determinant at all.

**A voltage source between two ungrounded nodes.** It has no conductance to write down —
its current is whatever it needs to be — so it cannot be stamped into $G$. The repair is
to add that current as an extra unknown with an extra row saying $v_a - v_b = V_s$, which
is what *modified* nodal analysis means and what the solver behind this course's
schematic editor actually does.

**Components that are not resistors.** Put a capacitor in and the entry is no longer a
real number: at frequency $\omega$ it is $j\omega C$, module 2's complex conductance, and
the whole matrix becomes complex while every rule above survives unchanged. Put one in
and ask about *time* instead of frequency, and the entries acquire derivatives — at which
point $G\mathbf{v} = \mathbf{i}$ has turned into the coupled first-order equations of the
first half of this module, which is exactly what the sandbox's phase portrait draws.
''',
                },
            ],
            "sandbox": {
                "title": "Two equations at once, coupled or not",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": -1, "a12": 0, "a21": 0, "a22": -2},
                "brief": r'''
The four sliders are the four entries of a 2×2 matrix, and the matrix says how fast
each of two quantities changes in terms of both of them. Take $x_1$ to be a voltage
somewhere in a circuit and $x_2$ to be a voltage somewhere else.

It opens with both off-diagonal entries at zero, which means the two quantities do
not affect each other at all: $\dot{x_1} = -x_1$ and $\dot{x_2} = -2x_2$, two
separate first-order equations, each with the exponential solution from this
module.
''',
                "notice": [
                    "Every arrow points inwards and every curve ends at the origin: both exponentials decay. The readout underneath says *stable node*, and gives $\\text{trace} = -3$, $\\det = 2$.",
                    "The curves flatten onto the horizontal axis before they arrive. $x_2$ decays twice as fast as $x_1$, so the vertical part of the motion is over first and the slow coordinate finishes the journey alone. The slowest time constant always wins in the end.",
                    "Set $a_{12}$ to 1. The two equations are now coupled — $x_2$ feeds into $\\dot{x_1}$ — and the curves visibly lean over. But the trace and determinant in the readout do not move at all, and it is still a stable node: coupling changed the paths without changing the two decay rates.",
                    "Put $a_{12}$ back to 0 and raise $a_{11}$ to $+0.5$. The determinant goes negative, the readout changes to *saddle*, and the curves run away along the horizontal axis. One positive rate is enough to ruin the whole system, however well behaved the other one is.",
                ],
            },
            "derive": {
                "title": "A loaded divider, solved once for every set of values",
                "minutes": 16,
                "vars": ["V_s", "R_1", "R_2", "R_3", "R_4", "v_1", "v_2"],
                "brief": r'''
The reading solved one loaded divider with one set of numbers. Do it with letters
instead and you get a formula that answers every loaded divider there will ever be —
and, more usefully, a formula whose *shape* tells you which resistor matters.

The circuit is the one from the reading. A source $V_s$ feeds node 1 through $R_1$;
$R_2$ goes from node 1 down to ground; $R_3$ carries on sideways from node 1 to node 2;
and $R_4$ goes from node 2 down to ground. Node 2 is the output.

Node analysis gives $G\mathbf{v} = \mathbf{i}$ with

$$G = \begin{bmatrix} G_{11} & -\frac{1}{R_3} \\[4pt] -\frac{1}{R_3} & G_{22}\end{bmatrix},
\qquad \mathbf{i} = \begin{bmatrix} \frac{V_s}{R_1} \\ 0 \end{bmatrix}$$

and the two diagonal entries are the first things to write down. Every resistance is a
positive constant; nothing here is a function of time.
''',
                "steps": [
                    {
                        "prompt": r"Write $G_{11}$: the sum of every conductance touching node 1.",
                        "answer": r"\frac{1}{R_1} + \frac{1}{R_2} + \frac{1}{R_3}",
                        "placeholder": r"a sum of reciprocals",
                        "hint": r"Three components touch node 1 — the one from the source, the one to ground, and the one across to node 2. Each contributes $1/R$, and conductances at a node add.",
                        "deconstruct": [
                            r"List what touches node 1: $R_1$, $R_2$, $R_3$.",
                            r"Each contributes its conductance, $1/R$, never its resistance.",
                            r"They add, because the node's own voltage pushes current out through all three at once.",
                        ],
                    },
                    {
                        "prompt": r"Write $G_{22}$: the sum of every conductance touching node 2.",
                        "answer": r"\frac{1}{R_3} + \frac{1}{R_4}",
                        "placeholder": r"a sum of two reciprocals",
                        "hint": r"Only two components reach node 2. $R_1$ and $R_2$ are nowhere near it, so neither appears.",
                        "deconstruct": [
                            r"$R_3$ joins node 2 to node 1, so it touches node 2.",
                            r"$R_4$ joins node 2 to ground, so it touches node 2.",
                            r"Nothing else does, and a conductance that is not attached does not appear in the row.",
                        ],
                    },
                    {
                        "prompt": r"The off-diagonal entries are both $-\frac{1}{R_3}$. Write $\det = G_{11}G_{22} - \left(\frac{1}{R_3}\right)^2$, multiplied out and simplified so that no $1/R_3^2$ term is left.",
                        "answer": r"\frac{1}{R_1 R_3} + \frac{1}{R_1 R_4} + \frac{1}{R_2 R_3} + \frac{1}{R_2 R_4} + \frac{1}{R_3 R_4}",
                        "placeholder": r"a sum of five reciprocal products",
                        "hint": r"Multiplying the two diagonals gives six terms, and exactly one of them is $1/R_3^2$. That is the one the subtraction removes.",
                        "deconstruct": [
                            r"$G_{11}G_{22} = \left(\frac{1}{R_1} + \frac{1}{R_2} + \frac{1}{R_3}\right)\left(\frac{1}{R_3} + \frac{1}{R_4}\right)$: three terms times two terms, so six products.",
                            r"Written out: $\frac{1}{R_1R_3} + \frac{1}{R_1R_4} + \frac{1}{R_2R_3} + \frac{1}{R_2R_4} + \frac{1}{R_3^2} + \frac{1}{R_3R_4}$.",
                            r"Subtracting $1/R_3^2$ cancels the fifth term exactly, and five survive.",
                        ],
                    },
                    {
                        "prompt": r"Cramer's rule gives $v_2 = \dfrac{G_{11}b_2 - b_1G_{21}}{\det}$, with $b_1 = \frac{V_s}{R_1}$, $b_2 = 0$ and $G_{21} = -\frac{1}{R_3}$. Write that numerator.",
                        "answer": r"\frac{V_s}{R_1 R_3}",
                        "placeholder": r"a source over a product",
                        "hint": r"The first term vanishes because $b_2 = 0$. What is left is minus $b_1$ times a negative, so the two minus signs cancel.",
                        "deconstruct": [
                            r"$G_{11}b_2 = G_{11} \times 0 = 0$: nothing is injected at node 2.",
                            r"$-b_1G_{21} = -\dfrac{V_s}{R_1}\times\left(-\dfrac{1}{R_3}\right)$.",
                            r"Two minus signs make a plus, and the two denominators multiply.",
                        ],
                    },
                    {
                        "prompt": r"Divide that numerator by the determinant, then clear every fraction by multiplying top and bottom by $R_1R_2R_3R_4$. Write $v_2$.",
                        "answer": r"\frac{V_s R_2 R_4}{R_1 R_2 + R_1 R_3 + R_1 R_4 + R_2 R_3 + R_2 R_4}",
                        "placeholder": r"a product on top, five products underneath",
                        "hint": r"On top, $\frac{V_s}{R_1R_3} \times R_1R_2R_3R_4$ leaves $V_sR_2R_4$. Underneath, each of the five terms loses its own two factors and keeps the other two.",
                        "deconstruct": [
                            r"$\dfrac{1}{R_1R_3}\times R_1R_2R_3R_4 = R_2R_4$, and the same cancellation happens in every term.",
                            r"The five denominator terms become $R_2R_4$, $R_2R_3$, $R_1R_4$, $R_1R_3$, $R_1R_2$.",
                            r"That is every pair of the four resistances except $R_3R_4$ — the one pair that does not include a path back to the source.",
                        ],
                    },
                    {
                        "prompt": r"Short out $R_3$ — set $R_3 = 0$, so node 2 becomes node 1 and $R_4$ hangs directly on the divider. Write $v_2$ for that case.",
                        "answer": r"\frac{V_s R_2 R_4}{R_1 R_2 + R_1 R_4 + R_2 R_4}",
                        "placeholder": r"the same shape with one term gone",
                        "hint": r"Two of the five denominator terms carry a factor of $R_3$, and both go to zero. Nothing on top involves $R_3$ at all.",
                        "deconstruct": [
                            r"$R_1R_3 \to 0$ and $R_2R_3 \to 0$.",
                            r"The numerator $V_sR_2R_4$ has no $R_3$ in it, so it is untouched.",
                            r"Three terms are left, and they are symmetric in a way the general answer is not.",
                        ],
                    },
                ],
                "closing": r'''
$$v_2 = \frac{V_sR_2R_4}{R_1R_2 + R_1R_3 + R_1R_4 + R_2R_3 + R_2R_4}$$

Put the reading's numbers in — $V_s = 12$ V, $R_1 = 1$ kΩ, $R_2 = 3.3$ kΩ,
$R_3 = 2.2$ kΩ, $R_4 = 4.7$ kΩ — and every product is in units of $\text{k}\Omega^2$:

```
top:   12 * 3.3 * 4.7 = 186.12

R1R2 =  1   * 3.3 =  3.30
R1R3 =  1   * 2.2 =  2.20
R1R4 =  1   * 4.7 =  4.70
R2R3 =  3.3 * 2.2 =  7.26
R2R4 =  3.3 * 4.7 = 15.51
                    ------
                     32.97

v2 = 186.12 / 32.97 = 5.6451 V
```

which is the number the elimination in the reading produced, from an entirely different
route. Two disagreeing methods would mean one of them was wrong; two agreeing to five
figures is as much confirmation as algebra offers.

Now read the formula rather than evaluating it, because that is what it is for.

**Disconnect the load.** Let $R_4 \to \infty$. Divide top and bottom by $R_4$ and every
term without an $R_4$ in it disappears, leaving $v_2 \to \dfrac{V_sR_2}{R_1 + R_2}$ — the
plain unloaded divider, 9.209 V here. So the general formula contains the easy one, which
is the first thing you should check of any result with letters in it.

**Disconnect the output instead.** Let $R_3 \to \infty$ and the numerator's single $R_3$-free
product is swamped by two denominator terms that grow with $R_3$, so $v_2 \to 0$. Also
correct: with nothing bridging across, node 2 is left with only $R_4$ to ground and sits
at zero.

**And notice which pair is missing.** Four resistances make six pairs, and $R_3R_4$ is
the one absent from the denominator. That is not a coincidence: $R_3$ and $R_4$ are the
only two that do not lie on a path from the source, so the one term they would have
contributed has nothing to drive it.
''',
            },
            "blanks": {
                "title": "Seven lines, one from each half of the module",
                "minutes": 9,
                "caption": "Vs is a constant supply, tau is a time constant, and a_jk are the entries of a 2x2 matrix",
                "lang": "text",
                "brief": r'''
Nothing is executed here. The first three lines are the first-order half of this module
and the last four are the simultaneous-equations half.

`e^(x)` is the exponential, `*` is multiplication, and *node k* means one particular
node of a resistor network whose equations you are assembling.
''',
                "listing": r'''
time constant of R and C in series          tau  =  ___

time constant of L and R in series          tau  =  ___

capacitor voltage, starting from empty      v(t) =  Vs * (1 - ___)

diagonal entry of G for node k              ___

entry of G joining node j to node k         ___

right-hand side for a node fed from Vs      ___
through a resistor R

determinant of [ [a11, a12], [a21, a22] ]   ___
''',
                "blanks": [
                    {
                        "prompt": "One resistor, one capacitor.",
                        "hole": "?",
                        "opts": ["R / C", "R * C", "C / R", "R + C"],
                        "a": 1,
                        "why": "$\\tau = RC$. Ohms times farads is seconds, and only the *product* matters — 1 kΩ with 1 µF behaves exactly like 10 kΩ with 100 nF.",
                        "whys": [
                            "Dividing gives ohms per farad, which is not a time; check the units before anything else. It would also say that a bigger capacitor charges *faster*, and a bigger capacitor is precisely more charge to move.",
                            "$\\tau = RC$. Ohms times farads is seconds, and only the *product* matters — 1 kΩ with 1 µF behaves exactly like 10 kΩ with 100 nF.",
                            "This has both parts the wrong way up: it makes the circuit slower as the resistor gets smaller, when a smaller resistor lets more current through and fills the capacitor sooner.",
                            "Adding an ohm to a farad is adding two quantities that are not the same kind of thing. Nothing in this subject ever adds a resistance to a capacitance.",
                        ],
                    },
                    {
                        "prompt": "One resistor, one inductor — and the resistor has changed sides.",
                        "hole": "?",
                        "opts": ["L * R", "R / L", "L / R", "1 / (L * R)"],
                        "a": 2,
                        "why": "$\\tau = L/R$. This is the one place where a bigger resistor makes the circuit *faster*, and it catches people who have just learned $\\tau = RC$. Physically: the resistor is what stops the current, and a bigger one stops it sooner.",
                        "whys": [
                            "Henries times ohms is not a time — it is volt-seconds per amp times volts per amp, which is nothing useful. Only $L/R$ has the units of a second.",
                            "This is $L/R$ upside down, so it is a rate rather than a time. With 100 mH and 220 Ω it gives 2200, and the real time constant is 455 µs.",
                            "$\\tau = L/R$. This is the one place where a bigger resistor makes the circuit *faster*, and it catches people who have just learned $\\tau = RC$. Physically: the resistor is what stops the current, and a bigger one stops it sooner.",
                            "A reciprocal of a product appears nowhere in a first-order response. Check the extreme case: with no resistance at all the current would rise for ever, so $\\tau$ must grow without limit as $R \\to 0$, and only $L/R$ does that.",
                        ],
                    },
                    {
                        "prompt": "The rising exponential, written so it starts at zero.",
                        "hole": "?",
                        "opts": ["e^(-t/tau)", "1 - e^(-t/tau)", "e^(t/tau)", "t/tau"],
                        "a": 0,
                        "why": "$v = V_s(1 - e^{-t/\\tau})$, so the blank holds the decaying exponential itself. Test it at both ends: at $t = 0$ the bracket is $1 - 1 = 0$, and after a long time it is $1 - 0 = 1$, giving $V_s$.",
                        "whys": [
                            "$v = V_s(1 - e^{-t/\\tau})$, so the blank holds the decaying exponential itself. Test it at both ends: at $t = 0$ the bracket is $1 - 1 = 0$, and after a long time it is $1 - 0 = 1$, giving $V_s$.",
                            "That double-counts the subtraction. The whole bracket is already $1 - e^{-t/\\tau}$, so putting the same thing inside it gives $V_se^{-t/\\tau}$ — the *discharge*, which starts full and empties.",
                            "A positive exponent grows without limit, so this predicts a capacitor charging past its supply and on to infinity. Every decaying quantity in this course carries a minus sign in the exponent.",
                            "A straight ramp is what a *constant current* into a capacitor produces, not a resistor. A resistor delivers less current as the capacitor fills, which is exactly why the line bends over.",
                        ],
                    },
                    {
                        "prompt": "Building the conductance matrix: what goes on the diagonal.",
                        "hole": "?",
                        "opts": [
                            "the sum of R over everything touching node k",
                            "1 / (the sum of R touching node k)",
                            "the sum of 1/R over everything touching node k",
                            "the largest 1/R touching node k",
                        ],
                        "a": 2,
                        "why": "Each row is a current balance, and every component attached to node $k$ carries current out of it in proportion to that node's own voltage. Those coefficients add, so the diagonal is $\\sum 1/R$ over everything touching the node — resistors to ground and resistors to a source included.",
                        "whys": [
                            "Resistances do not add at a node; conductances do. Currents are what balance, and current per volt is $1/R$, so $1/R$ is what has to be summed.",
                            "This is the parallel-resistance formula, which is the reciprocal of the answer. It is a resistance, and the matrix multiplies voltages to make currents, so its entries must be conductances.",
                            "Each row is a current balance, and every component attached to node $k$ carries current out of it in proportion to that node's own voltage. Those coefficients add, so the diagonal is $\\sum 1/R$ over everything touching the node — resistors to ground and resistors to a source included.",
                            "Every attached component contributes, not just the strongest one. Dropping the small conductances is an approximation you might make deliberately later; it is not the rule.",
                        ],
                    },
                    {
                        "prompt": "And what goes off the diagonal, where two nodes share a resistor.",
                        "hole": "?",
                        "opts": ["+1 / R", "-1 / R", "-R", "0"],
                        "a": 1,
                        "why": "Minus the conductance joining them, and it appears twice, symmetrically. The sign is not a convention: raising a neighbour's voltage pushes current *into* your node, which is the opposite of what your own voltage does, so its coefficient must carry the opposite sign.",
                        "whys": [
                            "With a positive off-diagonal the two nodes would help each other rise, and the solve returns voltages above the supply rail. A node voltage larger than every source in the circuit is the symptom of this exact slip.",
                            "Minus the conductance joining them, and it appears twice, symmetrically. The sign is not a convention: raising a neighbour's voltage pushes current *into* your node, which is the opposite of what your own voltage does, so its coefficient must carry the opposite sign.",
                            "The sign is right and the quantity is not. Everything in $G$ is a conductance in siemens, because $G$ multiplies volts and has to produce amps.",
                            "Zero would mean the two nodes do not affect each other at all, which is true only when no component joins them — and if that is the case there is no off-diagonal entry to write.",
                        ],
                    },
                    {
                        "prompt": "A voltage source, entering a set of equations whose unknowns are all node voltages.",
                        "hole": "?",
                        "opts": ["Vs * R", "Vs", "Vs / R", "R / Vs"],
                        "a": 2,
                        "why": "$V_s/R$ — the current that would flow in through that resistor if the node itself were sitting at zero. The right-hand side of $G\\mathbf{v} = \\mathbf{i}$ is a column of *currents*, so anything landing there has to be one.",
                        "whys": [
                            "Volts times ohms is neither a current nor a voltage. The quick way to catch it: the left-hand side is a conductance times a voltage, which is amps, so the right-hand side must be amps too.",
                            "A voltage cannot sit in a column of currents. This is also the entry you would write if you were trying to say *this node equals $V_s$*, which is a different kind of equation and belongs to a different method.",
                            "$V_s/R$ — the current that would flow in through that resistor if the node itself were sitting at zero. The right-hand side of $G\\mathbf{v} = \\mathbf{i}$ is a column of *currents*, so anything landing there has to be one.",
                            "Upside down, so it grows when the source shrinks. A source of zero volts should inject no current at all, and this would inject an infinite amount.",
                        ],
                    },
                    {
                        "prompt": "The number that decides whether there is an answer at all.",
                        "hole": "?",
                        "opts": [
                            "a11 a22 + a12 a21",
                            "a11 a12 - a21 a22",
                            "a11 + a22 - a12 - a21",
                            "a11 a22 - a12 a21",
                        ],
                        "a": 3,
                        "why": "$\\det = a_{11}a_{22} - a_{12}a_{21}$: the leading diagonal's product minus the other one's. It is what appears when you eliminate one unknown by hand, and it is what divides both answers — so a determinant of zero leaves nothing to divide by, and the two equations do not pin down a single answer.",
                        "whys": [
                            "The minus sign is the whole content of a determinant. With a plus, a matrix of all ones would come out as 2 rather than 0, and a matrix of all ones is the clearest example there is of two equations saying the same thing twice.",
                            "The products are taken along the rows rather than across the diagonals. Try it on the identity matrix: the diagonals give $1 \\times 1 - 0 \\times 0 = 1$, and this gives $1 \\times 0 - 0 \\times 1 = 0$, which would claim the simplest system of all has no answer.",
                            "The sum of the diagonal is the *trace*, a different and also useful number — the sandbox in this module shows the trace and the determinant side by side. The trace tells you about decay rates; only the determinant decides solvability.",
                            "$\\det = a_{11}a_{22} - a_{12}a_{21}$: the leading diagonal's product minus the other one's. It is what appears when you eliminate one unknown by hand, and it is what divides both answers — so a determinant of zero leaves nothing to divide by, and the two equations do not pin down a single answer.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "How long before anything happens",
                    "minutes": 4,
                    "brief": r'''
One rule, one multiplication. A resistor and a capacitor in series have a time constant
$\tau = RC$, and every question about how fast that circuit responds is answered by that
one number.

Read both values off the schematic and keep them in base units — ohms and farads — or use
the shortcut worth knowing: kilohms times microfarads gives milliseconds directly.
''',
                    "prompt": r"What is the time constant of this circuit?",
                    "note": "Answer in milliseconds, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 22000},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "5.00 V, switched on at t = 0"},
                        {"label": "R1", "value": "22.0 k\u03a9"},
                        {"label": "C1", "value": "100 nF"},
                        {"label": "Asked for", "value": "the time constant"},
                    ],
                    # The solver measures this circuit's own -3 dB corner by bisecting its AC
                    # response, and tau is 1/(2*pi*fc). Nothing about R or C is repeated here:
                    # if the drawn parts change, the measured corner changes with them.
                    "check": r'''
return 1000 / (2 * Math.PI * c.corner(1, 1e6));
''',
                    "answer": 2.2,
                    "tol": 0.01,
                    "unit": "ms",
                    "hint": r"$\tau = RC$ with $R$ in ohms and $C$ in farads: $22\,000 \times 100\times10^{-9}$. Then convert the answer from seconds to milliseconds.",
                    "wrong": r"If you got 0.0022, that is the right time in seconds rather than milliseconds. If you got 2200, the 100 nF went in as 100 µF — a factor of a thousand, and the commonest slip in the subject. If you got 72.3, that is the circuit's corner frequency in hertz, which is the same fact seen in the frequency domain: $f_c = 1/(2\pi\tau)$.",
                    "why": r"$\tau = RC = 2.20\times10^4 \times 1.00\times10^{-7} = 2.20\times10^{-3}$ s, which is 2.20 ms. The shortcut agrees without any exponents: 22 kΩ times 0.1 µF is $22 \times 0.1 = 2.2$ ms. What that number buys you is the whole shape of the response — the output passes 63.2% of 5 V, which is 3.16 V, at 2.20 ms; it is at 4.32 V by 4.40 ms; and it is within a percent of the supply after five time constants, at 11.0 ms. Nothing else about the circuit needs to be known to say all of that.",
                    "aside": "The same $RC$ is the corner frequency of this circuit read as a filter: $f_c = 1/(2\\pi \\times 2.20\\ \\text{ms}) = 72.3$ Hz. One circuit, one number, two languages — module 5 works in the second of them.",
                },
                {
                    "title": "The other kind of store, part way up",
                    "minutes": 7,
                    "brief": r'''
Same equation, different components. An inductor and a resistor in series produce the
identical first-order response, with

$$\tau = \frac{L}{R}$$

Note where the resistor has gone. In an RC circuit a bigger resistor is slower; here it
is *faster*, because the resistor is what limits the final current and a bigger one
limits it sooner.

The probe sits on the resistor, so it reads $iR$ — and since the current climbs from
zero towards $V_s/R$, the probe climbs from zero towards $V_s$.
''',
                    "prompt": r"What does the probe read 1.00 ms after the supply is switched on?",
                    "note": "Answer in volts, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                            {"id": "l1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.1},
                            {"id": "r1", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 220},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "12.0 V, switched on at t = 0"},
                        {"label": "L1", "value": "100 mH"},
                        {"label": "R1", "value": "220 \u03a9"},
                        {"label": "Asked for", "value": "the probe voltage at t = 1.00 ms"},
                    ],
                    # Every constant is read off the drawn parts rather than restated, so an edit
                    # to the schematic cannot leave this answer behind: the time constant, the
                    # final value and the exponent all come out of the netlist the solver built.
                    "check": r'''
const R = c.values('R')[0];
const L = c.values('L')[0];
const Vs = c.values('V')[0];
return Vs * (1 - Math.exp(-1e-3 * R / L));
''',
                    "answer": 10.670,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": r"Get $\tau = L/R$ in seconds first, then form the pure number $t/\tau$, and only then reach for the exponential. The probe voltage is $V_s(1 - e^{-t/\tau})$.",
                    "wrong": r"If you got 1.330, that is the *inductor's* share, $V_se^{-t/\tau}$ — the two add to 12 V, and the question asked for the other one. If you got 12.000, the response was assumed to be over; at 1 ms it is 2.2 time constants in, which is close but not finished. If you got 7.585, the formula was evaluated at $t = \tau$ instead of at 1 ms. If you got essentially zero, $\tau$ was taken as $R/L = 2200$ rather than $L/R$.",
                    "why": r"$\tau = L/R = 0.100/220 = 4.545\times10^{-4}$ s, or 454.5 µs. One millisecond is therefore $t/\tau = 1.00\times10^{-3}/4.545\times10^{-4} = 2.200$ time constants, and $e^{-2.200} = 0.110803$. So the probe reads $12 \times (1 - 0.110803) = 12 \times 0.889197 = 10.670$ V. Two checks. The current at that instant is $10.670/220 = 48.50$ mA, on its way to a final $12/220 = 54.55$ mA — 88.9% of the way, the same fraction, as it must be. And the inductor is holding the remaining $12 - 10.670 = 1.330$ V, which it can only do while the current is still changing: $v_L = L\,di/dt$ gives $di/dt = 1.330/0.100 = 13.3$ A/s, against 120 A/s at the very start.",
                    "aside": "Swap the inductor for a capacitor of $C = \\tau/R = 454.5\\ \\mu\\text{s}/220 = 2.07\\ \\mu$F and the trace is identical. The mathematics cannot tell the two circuits apart, which is the point of putting them in the same module.",
                },
                {
                    "title": "Two nodes that will not come apart",
                    "minutes": 9,
                    "brief": r'''
A divider with something hanging off it. The current through R1 is no longer the current
through R2, because part of it turns off at the middle node and goes through R3 and R4
instead — and how much turns off depends on the voltage you are trying to find.

Two unknowns, then: the middle node and the probed node. Write one current balance at
each, and solve the pair together. The closed form derived earlier in this module will
also do it in one line, if you would rather check than derive.
''',
                    "prompt": r"What voltage does the probe read?",
                    "note": "Answer in volts, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 12},
                            {"id": "r1", "kind": "R", "x": 5, "y": 4, "rot": 0, "value": 1500},
                            {"id": "r2", "kind": "R", "x": 8, "y": 6, "rot": 1, "value": 2200},
                            {"id": "r3", "kind": "R", "x": 10, "y": 4, "rot": 0, "value": 1000},
                            {"id": "r4", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 3300},
                            {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 8, "y": 9},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 13, "y": 4},
                        ],
                        "wires": [
                            {"a": [2, 5], "b": [2, 4]},
                            {"a": [2, 4], "b": [4, 4]},
                            {"a": [6, 4], "b": [8, 4]},
                            {"a": [8, 4], "b": [8, 5]},
                            {"a": [8, 4], "b": [9, 4]},
                            {"a": [11, 4], "b": [13, 4]},
                            {"a": [13, 4], "b": [13, 5]},
                            {"a": [2, 7], "b": [2, 9]},
                            {"a": [8, 7], "b": [8, 9]},
                            {"a": [13, 7], "b": [13, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "12.0 V"},
                        {"label": "R1 (supply to node 1)", "value": "1.50 k\u03a9"},
                        {"label": "R2 (node 1 to ground)", "value": "2.20 k\u03a9"},
                        {"label": "R3 (node 1 to node 2)", "value": "1.00 k\u03a9"},
                        {"label": "R4 (node 2 to ground)", "value": "3.30 k\u03a9"},
                    ],
                    # The probed node is one of the two unknowns of the 2x2 system, so the
                    # solver's own DC operating point is the answer with nothing added to it.
                    "check": r'''
return c.vout();
''',
                    "answer": 4.535,
                    "tol": 0.01,
                    "unit": "V",
                    "hint": r"At node 1 three resistors meet, at node 2 only two. Write $\sum$ (current leaving) $= 0$ at each, in conductances, and solve the pair. Or use $v_2 = V_sR_2R_4/(R_1R_2 + R_1R_3 + R_1R_4 + R_2R_3 + R_2R_4)$.",
                    "wrong": r"If you got 7.135, that is the unloaded divider $12 \times 2.2/3.7$ — the load was ignored, which is the error this question exists for. If you got 5.909, that is node 1; the probe is on node 2, one resistor further along. If you got 5.476, the unloaded 7.135 V was divided down by R3 and R4, which treats the divider as a perfect source; it is not, and its own output resistance is what makes the difference.",
                    "why": r'''
Two equations, in conductances:

```
node 1:  (1/1500 + 1/2200 + 1/1000) v1 - (1/1000) v2 = 12/1500
         6.666667e-4 + 4.545455e-4 + 1.000000e-3 = 2.1212121e-3        b1 = 8.000e-3

node 2:  -(1/1000) v1 + (1/1000 + 1/3300) v2 = 0
         1.000000e-3 + 3.030303e-4 = 1.3030303e-3                      b2 = 0

det = 2.1212121e-3 * 1.3030303e-3 - (1.000000e-3)^2
    = 2.7640037e-6 - 1.0000000e-6 = 1.7640037e-6

v2 = (0 - 8.000e-3 * (-1.000e-3)) / det = 8.0000e-6 / 1.7640037e-6 = 4.5351 V
v1 = (8.000e-3 * 1.3030303e-3 - 0) / det = 1.0424e-5 / 1.7640037e-6 = 5.9094 V
```

Check it with the currents, which is the only check that matters: R1 carries
$(12 - 5.9094)/1500 = 4.0604$ mA, R2 carries $5.9094/2200 = 2.6861$ mA, and R3 carries
$(5.9094 - 4.5351)/1000 = 1.3743$ mA. The last two add to 4.0604 mA, which is the
first — Kirchhoff at node 1, satisfied. R4 carries $4.5351/3300 = 1.3743$ mA, the same
as R3, as it must since nothing else touches node 2.

Now the point. Without R3 and R4 the middle node would sit at $12 \times 2200/3700 =
7.135$ V. Loaded, it sits at 5.909 V — the load has pulled it down by 1.23 V, or 17%.
The reason is the divider's own output resistance, $R_1 \parallel R_2 = 1500 \times
2200/3700 = 892\ \Omega$, which is not small against the 4.3 kΩ it is being asked to
drive. Thevenin says $v_2 = 7.135 \times 3300/(892 + 1000 + 3300) = 4.535$ V, and it
agrees, which is worth noticing: node analysis and Thevenin are two descriptions of the
same two equations.
''',
                    "aside": "Make R3 and R4 a hundred times larger — 100 kΩ and 330 kΩ — and the same arithmetic gives 7.120 V at node 1 instead of 5.909 V, within 0.2% of the unloaded 7.135 V. That is the whole design rule for instrumentation: load a divider with something much larger than the divider itself, or measure what you have actually built rather than what you drew.",
                },
                {
                    "title": "A bridge, and the current across the middle of it",
                    "minutes": 12,
                    "brief": r'''
This one cannot be reduced. There is no pair of resistors in series and no pair in
parallel anywhere in it, because R5 spans the two halves and spoils every grouping you
might try. Series and parallel arithmetic has run out, and the only way in is the one
this module is about: name the unknowns, write a balance at each, and solve them
together.

The top node is wired to the source, so it is not an unknown — it is 10 V. That leaves
two: the node between R1 and R3, and the node between R2 and R4. Three resistors touch
each of them.

The quantity asked for is not a node voltage. Find the two node voltages first, then get
the current from the difference between them.
''',
                    "prompt": r"What current flows through R5, from the left-hand middle node to the right-hand one?",
                    "note": "Answer in microamps, to one decimal place. A negative answer would mean it flows the other way.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 2, "y": 5, "rot": 1, "value": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 1, "value": 1000},
                            {"id": "r3", "kind": "R", "x": 6, "y": 7, "rot": 1, "value": 2200},
                            {"id": "r2", "kind": "R", "x": 12, "y": 3, "rot": 1, "value": 2200},
                            {"id": "r4", "kind": "R", "x": 12, "y": 7, "rot": 1, "value": 3300},
                            {"id": "r5", "kind": "R", "x": 9, "y": 5, "rot": 0, "value": 4700},
                            {"id": "g0", "kind": "GND", "x": 2, "y": 8},
                            {"id": "g1", "kind": "GND", "x": 6, "y": 10},
                            {"id": "g2", "kind": "GND", "x": 12, "y": 10},
                            {"id": "o1", "kind": "OUT", "x": 8, "y": 4},
                        ],
                        "wires": [
                            {"a": [2, 4], "b": [2, 2]},
                            {"a": [2, 2], "b": [6, 2]},
                            {"a": [6, 2], "b": [12, 2]},
                            {"a": [2, 6], "b": [2, 8]},
                            {"a": [6, 4], "b": [6, 6]},
                            {"a": [6, 8], "b": [6, 10]},
                            {"a": [12, 4], "b": [12, 6]},
                            {"a": [12, 8], "b": [12, 10]},
                            {"a": [6, 5], "b": [8, 5]},
                            {"a": [10, 5], "b": [12, 5]},
                            {"a": [6, 4], "b": [8, 4]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "10.0 V"},
                        {"label": "R1 (supply to left node)", "value": "1.00 k\u03a9"},
                        {"label": "R3 (left node to ground)", "value": "2.20 k\u03a9"},
                        {"label": "R2 (supply to right node)", "value": "2.20 k\u03a9"},
                        {"label": "R4 (right node to ground)", "value": "3.30 k\u03a9"},
                        {"label": "R5 (across the middle)", "value": "4.70 k\u03a9"},
                    ],
                    # A branch current is no node of the circuit, so it is taken out of the DC
                    # solve as the drop across R5 over R5's own value. Reading both off the
                    # netlist keeps the check honest if the schematic is ever redrawn.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r5'; })[0];
return (d.v[r.n1] - d.v[r.n2]) / r.value * 1e6;
''',
                    "answer": 130.5,
                    "tol": 0.6,
                    "unit": "\u00b5A",
                    "hint": r"Call the left node $v_B$ and the right one $v_C$. At $v_B$: $(v_B - 10)/1000 + v_B/2200 + (v_B - v_C)/4700 = 0$. Write the matching line at $v_C$, then solve the 2×2. Both rows have a source term on the right, because both middle nodes are fed from the supply.",
                    "wrong": r"If you got 0, the bridge was assumed to be balanced. It balances only when $R_1/R_3 = R_2/R_4$, and here that is $0.455$ against $0.667$. If you got 186.2, R5 was removed to find the open-circuit difference — $6.875 - 6.000 = 0.875$ V — and that was divided by 4.70 kΩ; the difference collapses as soon as current actually flows, because both halves have output resistance of their own. If you got 613, that is the voltage across R5 in millivolts, one division short of the answer.",
                    "why": r'''
Two nodes, three conductances each:

```
gBB = 1/1000 + 1/2200 + 1/4700 = 1.6673114e-3      bB = 10/1000 = 1.0000000e-2
gCC = 1/2200 + 1/3300 + 1/4700 = 9.7034172e-4      bC = 10/2200 = 4.5454545e-3
gBC = gCB = -1/4700            = -2.1276596e-4

det = 1.6673114e-3 * 9.7034172e-4 - (2.1276596e-4)^2
    = 1.6178618e-6 - 4.5269353e-8 = 1.5725925e-6

vB = (1.0000000e-2 * 9.7034172e-4 + 2.1276596e-4 * 4.5454545e-3) / det
   = (9.7034172e-6 + 9.6711800e-7) / det = 1.0670535e-5 / 1.5725925e-6 = 6.7853 V

vC = (1.6673114e-3 * 4.5454545e-3 + 1.0000000e-2 * 2.1276596e-4) / det
   = (7.5786882e-6 + 2.1276596e-6) / det = 9.7063478e-6 / 1.5725925e-6 = 6.1722 V

i(R5) = (6.7853 - 6.1722) / 4700 = 0.61312 / 4700 = 1.3045e-4 A = 130.5 uA
```

The probe is on the left-hand node, so 6.785 V is there to check the first half against
before you go on.

Then check both balances, which is what makes a simultaneous solve trustworthy. Into the
left node through R1: $(10 - 6.7853)/1000 = 3.2147$ mA. Out of it through R3:
$6.7853/2200 = 3.0842$ mA. Out through R5: 0.1305 mA. The two outgoing add to 3.2147 mA.
At the right node: $(10 - 6.1722)/2200 = 1.7399$ mA arrives through R2 and 0.1305 mA
arrives through R5, together 1.8704 mA, and R4 carries $6.1722/3300 = 1.8704$ mA away.
Both nodes balance to five figures.

Notice what the sign says. The left node sits higher, so current crosses from left to
right — the left-hand half of the bridge is the more lightly loaded one, since
$R_1/R_3 = 0.455$ is smaller than $R_2/R_4 = 0.667$. Swap R1 and R3 over and the
left-hand node drops to 3.13 V open-circuit against the right-hand node's 6.00 V, so the
current reverses — a bridge reading tells you which way the imbalance went as well as
how big it was.
''',
                    "aside": "A bridge is balanced when $R_1/R_3 = R_2/R_4$, which here would need $R_4 = R_2R_3/R_1 = 2200 \\times 2200/1000 = 4840\\ \\Omega$. At that value no current crosses the middle at all, whatever R5 is and whatever the supply is — which is why a bridge is the classic way to measure a resistance precisely. You never have to measure a small current accurately; you only have to see it reach zero.",
                },
            ],
            "quiz": {
                "title": "Time constants and determinants",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A resistor and capacitor charge a node from a step of $V_s$ volts. After exactly one time constant, how far has the output got?",
                        "opts": ["Exactly half way", "About 37% of the way", "About 63% of the way to $V_s$", "All the way"],
                        "a": 2,
                        "why": (
                            "$v(\\tau) = V_s(1 - e^{-1}) = 0.632\\,V_s$. The 37% figure is the very same number seen "
                            "from the other side — it is the fraction *remaining*, $e^{-1}$ — and mixing the two up "
                            "is the classic error. Half way happens a little earlier, at $0.693\\tau$."
                        ),
                    },
                    {
                        "q": "You double the resistance and halve the capacitance. What happens to the time constant $\\tau = RC$?",
                        "opts": ["It doubles", "It stays the same", "It halves", "It is quartered"],
                        "a": 1,
                        "why": (
                            "$\\tau$ depends only on the *product*: $(2R)(C/2) = RC$. This is why a build check on a "
                            "time constant cannot ask for particular values of $R$ and $C$ — infinitely many pairs "
                            "give the same behaviour, and the circuit does not know which pair you chose."
                        ),
                    },
                    {
                        "q": "Which function solves $\\frac{dv}{dt} = \\frac{V_s - v}{\\tau}$ with $v(0) = 0$?",
                        "opts": [
                            "$V_s e^{-t/\\tau}$",
                            "$V_s\\frac{t}{\\tau}$",
                            "$V_s\\left(1 - e^{-t/\\tau}\\right)$",
                            "$V_s\\left(1 + e^{-t/\\tau}\\right)$",
                        ],
                        "a": 2,
                        "why": (
                            "Test the candidates at $t = 0$ and at $t = \\infty$: the answer must start at 0 and finish "
                            "at $V_s$. Only $V_s(1 - e^{-t/\\tau})$ does both. $V_s e^{-t/\\tau}$ is the *decaying* solution, which "
                            "answers a different question — a charged capacitor emptying itself — and the straight "
                            "line would need a constant current, not a resistor."
                        ),
                    },
                    {
                        "q": "You write the node equations of a resistor network as $G\\mathbf{v} = \\mathbf{i}$. What sits on the diagonal of $G$?",
                        "opts": [
                            "The resistance of the largest resistor at that node",
                            "The voltage at that node",
                            "Always 1",
                            "The sum of all the conductances touching that node",
                        ],
                        "a": 3,
                        "why": (
                            "Each row is a current balance at one node. The node's own voltage appears once for every "
                            "component attached to it, so the coefficients add up: the diagonal entry is $\\sum 1/R$ "
                            "over everything touching the node. Conductances, not resistances — that is why the "
                            "matrix is built from $1/R$ throughout, and why the off-diagonal entries are negative."
                        ),
                    },
                    {
                        "q": "A 2×2 system of simultaneous equations has no single answer when the determinant is:",
                        "opts": ["Zero", "One", "Negative", "Very large"],
                        "a": 0,
                        "why": (
                            "The determinant divides the answer, so a determinant of zero means there is no single "
                            "answer to divide out — the two equations are either the same equation twice, or they "
                            "contradict each other. A negative determinant is perfectly ordinary and just means the "
                            "solution comes out with the signs the algebra gives it."
                        ),
                    },
                    {
                        "q": "Multiply an ohm by a farad. What unit do you get?",
                        "opts": ["A hertz", "A second", "A volt", "An amp"],
                        "a": 1,
                        "why": (
                            "Ohms times farads is seconds, which is why $\\tau = RC$ is a time at all. It is worth "
                            "checking this the long way once: an ohm is volts per amp and a farad is coulombs per "
                            "volt, so the product is coulombs per amp, and an amp is coulombs per second. A useful "
                            "habit — if the units of a formula are wrong, the formula is wrong."
                        ),
                    },
                ],
            },
            "build": {
                "title": "A circuit with a time constant of one millisecond",
                "minutes": 22,
                "brief": r'''
The canvas has a 5 V source, a ground, and a probe sitting straight on the source,
so the probe jumps to 5 V the instant the supply appears. Put something between them
that makes the rise take time.

Build a circuit driven by that 5 V source whose probe voltage:

1. starts at **0 V**,
2. rises to **5 V** and stays there,
3. passes 63% of the way — that is 3.16 V — after exactly **1 millisecond**,
4. and is 95% of the way there at 3 ms, because the rise is exponential rather than
   a straight climb.

You need one resistor and one energy store. It can be a capacitor, with
$\tau = RC$; it can equally be an **inductor** (the part marked `L`), with
$\tau = L/R$. Either gives the same differential equation and the same curve, which
is the point of the module — and only one of the two is drawn in the reference
answer, so pick whichever you can reason about.

To see the response, choose **Transient**, set *Stop after* to `5m` and press Solve.

An inductor resists changes in current, so with an inductor in series the current
starts at zero and builds up; put the probe where the growing current shows as a
growing voltage.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 5, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.1},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 100},
                        {"id": "p3", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 9, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                    ],
                },
                "checks": [
                    {"name": "the output starts at zero, not at the supply", "code": r'''
const s = c.step(6e-3);
c.assert(Math.abs(s.v[0]) < 0.05, "at the instant the supply appears the probe already reads " +
  c.fmt(s.v[0], "V") + "; there is nothing between the source and the probe to slow it down");
'''},
                    {"name": "it settles at the full 5 volts", "code": r'''
const s = c.step(2e-2);
c.close(s.v[s.v.length - 1], 5.0, 0.02, "the settled output voltage");
'''},
                    {"name": "it is 63% of the way there after 1 ms", "code": r'''
const s = c.step(6e-3);
let k = -1;
for (let i = 0; i < s.v.length; i++) {
  if (s.v[i] >= 0.632 * 5.0) { k = i; break; }
}
c.assert(k >= 0, "the output never reaches 3.16 V within 6 ms — the time constant is far too long");
c.close(s.t[k], 1e-3, 0.1, "the time taken to reach 63% of the supply");
'''},
                    {"name": "the rise is exponential, not a straight line", "code": r'''
const s = c.step(6e-3);
let k = 0;
for (let i = 1; i < s.t.length; i++) {
  if (Math.abs(s.t[i] - 3e-3) < Math.abs(s.t[k] - 3e-3)) k = i;
}
c.close(s.v[k], 4.7515, 0.04, "the output at 3 ms, which should be 95% of the way there");
'''},
                ],
                "hints": [
                    "For the inductor route: $\\tau = L/R$, and you need $\\tau = 1$ ms. Choose the resistor first — 100 Ω, say — and the inductance follows as $L = \\tau R$. Type it as `100m`.",
                    "For the capacitor route: $\\tau = RC$, so a 1 kΩ resistor with a 1 µF capacitor gives exactly 1 ms.",
                    "The probe must go on the node between the two parts, not on the source. On the source there is nothing to measure.",
                    "Both parts need somewhere to send their current: the second one should end at a ground.",
                    "If the response is over almost instantly, your time constant is too small by a factor you can read straight off the plot — the time axis is labelled.",
                ],
            },
            "lab": {
                "title": "Solving a network all at once",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
A resistor network does not have one equation with one unknown; it has one equation
per node, and they all have to hold at the same time. This lab writes and solves
such a pair.

`solve2(a11, a12, a21, a22, b1, b2)` solves

$$a_{11}x_1 + a_{12}x_2 = b_1, \qquad a_{21}x_1 + a_{22}x_2 = b_2$$

by determinants. Work out $\det = a_{11}a_{22} - a_{12}a_{21}$ first. If it is zero
there is no single answer, so raise `ValueError`. Otherwise

$$x_1 = \frac{b_1 a_{22} - a_{12} b_2}{\det}, \qquad x_2 = \frac{a_{11} b_2 - b_1 a_{21}}{\det}$$

`ladder(vs, r1, r2, r3)` uses it on a real circuit: a source `vs` feeds `r1` into
node 1, `r2` joins node 1 to node 2, and `r3` takes node 2 down to ground. Balancing
the currents at each node gives

$$\begin{bmatrix} \frac{1}{r_1} + \frac{1}{r_2} & -\frac{1}{r_2} \\ -\frac{1}{r_2} & \frac{1}{r_2} + \frac{1}{r_3} \end{bmatrix}\begin{bmatrix} v_1 \\ v_2 \end{bmatrix} = \begin{bmatrix} \frac{v_s}{r_1} \\ 0 \end{bmatrix}$$

Build those six numbers and hand them to `solve2`. Notice the pattern: the sum of
the conductances on the diagonal, minus the shared conductance off it, and the
source appearing only in the row of the node it feeds.
''',
                "files": [{"name": "main.py", "content": r'''
def solve2(a11, a12, a21, a22, b1, b2):
    """Solve two simultaneous equations by determinants.

    Raise ValueError when the determinant is zero.
    """
    # TODO: determinant first, then the two answers.
    return (0.0, 0.0)


def ladder(vs, r1, r2, r3):
    """Node voltages of  vs -[r1]- node1 -[r2]- node2 -[r3]- ground."""
    # TODO: build the four matrix entries and the two right-hand sides,
    # then call solve2.
    return (0.0, 0.0)


if __name__ == "__main__":
    print("solve2:", solve2(2.0, 1.0, 1.0, 3.0, 5.0, 10.0))
    print("ladder, three equal resistors:", ladder(3.0, 1000.0, 1000.0, 1000.0))
    print("ladder, 1k 2k 3k from 9 V:", ladder(9.0, 1000.0, 2000.0, 3000.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def solve2(a11, a12, a21, a22, b1, b2):
    """Solve two simultaneous equations by determinants.

    Raise ValueError when the determinant is zero.
    """
    det = a11 * a22 - a12 * a21
    if abs(det) < 1e-15:
        raise ValueError("the determinant is zero: these two equations do not fix a single answer")
    x1 = (b1 * a22 - a12 * b2) / det
    x2 = (a11 * b2 - b1 * a21) / det
    return (x1, x2)


def ladder(vs, r1, r2, r3):
    """Node voltages of  vs -[r1]- node1 -[r2]- node2 -[r3]- ground."""
    g11 = 1.0 / r1 + 1.0 / r2
    g12 = -1.0 / r2
    g21 = -1.0 / r2
    g22 = 1.0 / r2 + 1.0 / r3
    return solve2(g11, g12, g21, g22, vs / r1, 0.0)


if __name__ == "__main__":
    print("solve2:", solve2(2.0, 1.0, 1.0, 3.0, 5.0, 10.0))
    print("ladder, three equal resistors:", ladder(3.0, 1000.0, 1000.0, 1000.0))
    print("ladder, 1k 2k 3k from 9 V:", ladder(9.0, 1000.0, 2000.0, 3000.0))
'''}],
                "hints": [
                    "Compute the determinant once and store it. You need it twice, and testing it for zero before dividing is what stops the function crashing on a badly posed network.",
                    "Compare floating-point numbers against a small tolerance rather than exactly: `abs(det) < 1e-15`.",
                    "In `ladder`, everything is a conductance — $1/r$ — never a resistance. If your answers come out enormous, that is the reason.",
                    "Sanity-check the three-equal-resistor case by hand: the same current flows through all three, so the voltages must be two thirds and one third of the source.",
                ],
                "tests": [
                    {"name": "a small system comes out right", "code": r'''
_x1, _x2 = solve2(2.0, 1.0, 1.0, 3.0, 5.0, 10.0)
assert abs(_x1 - 1.0) < 1e-12 and abs(_x2 - 3.0) < 1e-12, \
    f"expected (1, 3), got ({_x1}, {_x2})"
'''},
                    {"name": "the answers really satisfy both equations", "code": r'''
_a = (3.0, -2.0, 4.0, 5.0)
_b = (7.0, -1.0)
_x1, _x2 = solve2(_a[0], _a[1], _a[2], _a[3], _b[0], _b[1])
assert abs(_a[0] * _x1 + _a[1] * _x2 - _b[0]) < 1e-9, "the first equation is not satisfied"
assert abs(_a[2] * _x1 + _a[3] * _x2 - _b[1]) < 1e-9, "the second equation is not satisfied"
'''},
                    {"name": "a zero determinant is refused", "code": r'''
try:
    solve2(1.0, 2.0, 2.0, 4.0, 1.0, 2.0)
except ValueError:
    pass
else:
    raise AssertionError("the second equation is just twice the first, so ValueError was expected")
'''},
                    {"name": "three equal resistors divide evenly", "code": r'''
_v1, _v2 = ladder(3.0, 1000.0, 1000.0, 1000.0)
assert abs(_v1 - 2.0) < 1e-9, f"node 1 should sit at two thirds of 3 V, got {_v1}"
assert abs(_v2 - 1.0) < 1e-9, f"node 2 should sit at one third of 3 V, got {_v2}"
'''},
                    {"name": "unequal resistors divide in proportion", "code": r'''
_v1, _v2 = ladder(9.0, 1000.0, 2000.0, 3000.0)
assert abs(_v1 - 7.5) < 1e-9, f"expected 7.5 V at node 1, got {_v1}"
assert abs(_v2 - 4.5) < 1e-9, f"expected 4.5 V at node 2, got {_v2}"
'''},
                    {"name": "a big resistor to ground draws almost nothing", "code": r'''
_v1, _v2 = ladder(10.0, 1000.0, 1000.0, 1e9)
assert abs(_v1 - 10.0) < 1e-3, f"with almost no current there is almost no drop across r1, got {_v1}"
assert abs(_v2 - 10.0) < 1e-3, f"and none across r2 either, got {_v2}"
'''},
                ],
            },
        },

        # ---- M5 -----------------------------------------------------------
        {
            "title": "Exponentials, logarithms and the decibel",
            "summary": "The exponential read backwards, and the unit engineers actually quote a gain in. Both exist because electronics spans factors of a million and paper does not.",
            "concepts": [
                r"A **logarithm** is an exponent read backwards. $\log_{10}x$ is the power of ten that gives $x$; $\ln x$ is the power of $e$ that gives $x$. So $10^{\log_{10}x} = x$ and $e^{\ln x} = x$ for every positive $x$ — and no logarithm of zero or of a negative number exists, because no power of ten lands there.",
                r"Because exponents add when powers multiply, a logarithm turns multiplication into addition: $\log(ab) = \log a + \log b$, $\log(a/b) = \log a - \log b$, $\log(a^n) = n\log a$. Every use of a logarithm in this course is one of those three lines.",
                r"The natural logarithm is the one that undoes a circuit. From $v = V_0e^{-t/\tau}$, taking logs of both sides gives $t = \tau\ln(V_0/v)$: measuring how long a decay takes to fall to a stated fraction *is* taking a logarithm.",
                r"A **decibel** is a logarithm of a ratio, and it always compares two quantities. For powers it is $10\log_{10}(P_2/P_1)$; for voltages, currents or any other amplitude it is $20\log_{10}(A_2/A_1)$. The 20 is not a second rule — power goes as amplitude squared, and $\log(A^2) = 2\log A$.",
                r"Four landmarks are worth knowing without a calculator: $\times 1$ is 0 dB, $\times\sqrt{2}$ in amplitude is 3.01 dB, $\times 2$ in amplitude is 6.02 dB, and $\times 10$ in amplitude is exactly 20 dB. The half-power point, where amplitude has fallen to $1/\sqrt{2}$, is $-3.01$ dB, which everybody writes as $-3$ dB.",
                r"Decibels add where gains multiply. A 20 dB stage followed by a 14 dB stage is 34 dB, and nothing was multiplied — which is the entire reason a cascade is quoted this way.",
                r"A **decade** is a factor of ten in frequency; an **octave** is a factor of two. A first-order roll-off loses 20 dB per decade, which is the same slope as 6.02 dB per octave: one physical fact, two units.",
            ],
            "read": [
                {
                    "title": "The exponent, read backwards",
                    "minutes": 16,
                    "body": r'''
Open a drawer of resistors and the values run from about 10 Ω to about 10 MΩ — a factor
of a million. Look at the signals inside a radio receiver and they run from two
microvolts at the antenna to thirty volts at the loudspeaker — a factor of fifteen
million. Draw those signal levels to scale on an axis tall enough to show the 30 V and
the antenna signal is thinner than the ink you drew it with.

That is the first problem. The second is worse. Almost everything this subject does to a
quantity **multiplies** it. A gain of 200 followed by a loss of 30 is a multiplication
and a division. Doubling a frequency and then doubling it again moves you two equal steps
along a scale that are 1 kHz and 2 kHz wide in hertz. A capacitor discharging loses the
same *fraction* of what is left every millisecond, not the same number of volts.
Multiplication is the natural operation here, and multiplication is the one arithmetic is
worst at.

A logarithm converts the second problem into addition and the first into something that
fits on a page. This unit is about what it is, the three lines it is for, and the one
question in circuits that cannot be answered without it.

## The definition, from counting

Start with something you can count. Ten multiplied by itself three times is a thousand,
so we write $10^3 = 1000$. Now ask the same fact backwards: *how many tens were
multiplied to get a thousand?* Three. That number — the exponent, recovered from the
result — is the logarithm:

$$\log_{10} 1000 = 3 \qquad \text{because} \qquad 10^3 = 1000$$

Nothing more is going on. $\log_{10}x$ is the power of ten that gives $x$, so the two
operations undo each other exactly:

$$10^{\log_{10}x} = x \qquad\text{and}\qquad \log_{10}(10^y) = y$$

The interesting part is what happens between the whole numbers. $\log_{10} 500$ is not
a count of anything, because 500 is not a product of whole tens; it is 2.69897, meaning
$10^{2.69897} = 500$. The exponent function was extended to fractional powers long before
anyone needed it here, and the logarithm inherits that extension. So every positive number
has a logarithm, and the counting picture is only the anchor.

Two consequences are immediate and both matter. Numbers **below one** have negative
logarithms: $\log_{10}0.001 = -3$, because $10^{-3} = 0.001$. And **zero has no
logarithm at all**, because no power of ten is ever zero; $10^{-6}$ is small, $10^{-100}$
is very small, and neither is zero. Nor does any negative number, for the same reason.
That is not a gap to be patched later — it is the reason a decibel figure for a signal
that is genuinely absent does not exist.

## Two bases, and why the subject keeps both

Base ten is the one that matches how we write numbers, so it is the one used whenever a
human has to read the answer: decades, decibels, log-scaled axes on a datasheet.

Base $e$ is the one the physics produces. Module 3 showed why: a quantity whose rate of
change is proportional to itself decays as $e^{-t/\tau}$ and nothing else, and $e$ appears
there because it is the number whose exponential is its own derivative. Nobody chose it.
So when a circuit answer has to be undone, the natural logarithm $\ln$ is what undoes it:

$$e^{\ln x} = x$$

The two are the same function with a constant in front. Since $x = 10^{\log_{10}x}$ and
$10 = e^{\ln 10}$,

$$x = \left(e^{\ln 10}\right)^{\log_{10}x} = e^{\,\ln 10\,\cdot\,\log_{10}x}
\qquad\Longrightarrow\qquad \ln x = 2.302585 \times \log_{10}x$$

Keep that factor of 2.3026 in mind. It is the size of the error you make by reaching for
the wrong button, and it is small enough that a wrong answer still looks plausible.

## The three lines

Everything a logarithm is used for in this course comes from the exponent rules you
already know, read backwards. Take $a = 10^p$ and $b = 10^q$, so $p = \log a$ and
$q = \log b$. Then $ab = 10^{p}10^{q} = 10^{p+q}$, and reading *that* backwards:

$$\log(ab) = p + q = \log a + \log b$$

The same move on $a/b = 10^{p-q}$ and on $a^n = 10^{np}$ gives the other two:

$$\log\frac{a}{b} = \log a - \log b \qquad\qquad \log(a^n) = n\log a$$

Those three lines are the whole toolkit, and they hold in any base. Products become sums,
quotients become differences, powers become multipliers. Notice what is *not* on the list:
there is no rule for $\log(a + b)$. Addition survives the transformation as nothing at
all, which is exactly why two signals added together are awkward to handle in decibels and
two signals multiplied together are trivial.

## Worked: a capacitor that is still worth respecting

A 100 µF capacitor sits charged to 12.0 V across a 220 kΩ bleed resistor. Module 4's
result applies: $v = V_0e^{-t/\tau}$ with $\tau = RC$.

```
tau = R C = 2.20e5 * 1.00e-4 = 22.0 s
```

Question one: when does it fall to half, 6.00 V?

```
6.00 = 12.0 e^(-t/22)
0.5  = e^(-t/22)
ln 0.5 = -t/22                 <- take ln of both sides; ln undoes e
-0.693147 = -t/22
t = 22 * 0.693147 = 15.25 s
```

Question two: when is it below 1.00 V — a level you could touch without noticing?

```
1.00 / 12.0 = e^(-t/22)
t = 22 * ln(12.0/1.00) = 22 * 2.484907 = 54.67 s
```

Question three: below 0.100 V?

```
t = 22 * ln(120) = 22 * 4.787492 = 105.3 s
```

Three things are worth reading off that. First, the ratio is what enters, never the
voltages themselves: $\ln(12/1) $ and $\ln(1.2/0.1)$ are the same number and give the same
time. Second, each further factor of ten costs the same 50.7 s, because
$\ln 10 = 2.302585$ and $22 \times 2.302585 = 50.66$ s — equal factors, equal times, which
is the whole character of exponential decay. Third, the answers are not proportional to
the voltage: getting from 12 V to 6 V took 15.2 s, and getting from 6 V to 1 V took
another 39.4 s even though it is a smaller drop in volts. If you find yourself scaling a
decay time linearly, that is the check that catches it.

The general form, worth writing once and keeping:

$$t = \tau\ln\frac{v_{\text{start}}}{v_{\text{end}}}$$

## Worked: what "settled" means on a datasheet

A converter samples a signal through a switch with 500 Ω of on-resistance into a 2.0 nF
sampling capacitor. The manufacturer says the input must settle to 12-bit accuracy before
the conversion starts. How long is that?

Twelve-bit accuracy means the remaining error must be under half of one least significant
bit — half of $1/2^{12}$ of full scale, so $1/2^{13} = 1/8192$.

```
tau = R C = 500 * 2.0e-9 = 1.00e-6 s = 1.00 us

remaining fraction = e^(-t/tau) = 1/8192
t/tau = ln 8192 = 13 * ln 2 = 13 * 0.693147 = 9.011
t = 9.011 * 1.00 us = 9.01 us
```

The general result is prettier than the number, and it is the reason to have done it
symbolically: $n$-bit settling costs

$$\frac{t}{\tau} = \ln 2^{\,n+1} = (n+1)\ln 2 \approx 0.693(n+1)$$

time constants. Eight bits costs 6.24 τ, twelve costs 9.01 τ, sixteen costs 11.78 τ.
Every extra bit costs 0.693 τ — a *fixed* amount, not a doubling — because each bit is a
factor of two in accuracy and the logarithm turns that factor into a constant addition.
That is the single most useful thing a logarithm does in this subject, seen on a real
specification: an exponential requirement became a straight line.

## Reading a logarithmic axis

A frequency axis drawn logarithmically puts $\log_{10}f$, not $f$, at equal distances.
Between the gridlines marked 100 and 1000 there is one decade of paper, and the point
half way across is **not** 550. It is the frequency whose logarithm is half way, so

$$\log_{10}f = \tfrac{1}{2}(2 + 3) = 2.5 \qquad\Longrightarrow\qquad
f = 10^{2.5} = 316.2\ \text{Hz}$$

Half way along in distance is the *geometric* mean, $\sqrt{100 \times 1000} = 316.2$, and
the same is true anywhere on the axis. This is worth ten seconds of practice because
every plot in the next five modules is drawn this way, and reading 550 off one of them
is an error of 74%.

## The mistakes people actually make

**Splitting the logarithm of a sum.** $\log(a + b)$ is not $\log a + \log b$ — the second
expression is $\log(ab)$, which is a different number entirely. Try it: $\log_{10}(2 + 8)
= \log_{10}10 = 1$, while $\log_{10}2 + \log_{10}8 = 0.301 + 0.903 = 1.204$, which is
$\log_{10}16$. The reason this is tempting is that the three real rules all *look* like
distributing, and the sum rule is the one that would be most useful if it existed.

**Reaching for the wrong base.** `log` on a calculator is usually base ten and `log` in a
programming language is usually natural — Python, C and JavaScript all mean $\ln$ by
`log`. The two differ by 2.3026, which turns a $-20$ dB/decade slope into $-8.7$ and a
54.7 s bleed time into 23.7 s. Both wrong answers are the right order of magnitude, which
is precisely what makes the slip survive.

**Using the wrong voltage in a decay.** $t = \tau\ln(v_{\text{start}}/v_{\text{end}})$ is
about the quantity that is *decaying*. For a capacitor charging up, what decays is the gap
still to be crossed, $V_s - v$, so the time to reach 7.5 V of a 9 V supply is
$\tau\ln(9/1.5)$ and not $\tau\ln(9/7.5)$. Those are 1.792 and 0.182 time constants — a
factor of nearly ten — and the wrong one is the one with the target voltage visibly in it,
which is why it looks right.

**Treating a logarithm as roughly linear.** $\log_{10}$ of 100 is 2 and of 200 is 2.301.
Doubling a number adds 0.301 to its logarithm *wherever you start*: from 5 to 10, from
5 million to 10 million, always 0.301. The function grows so slowly that intuition built
on linear quantities gives no useful estimate at all — $\log_{10}$ of a billion is only 9.

## Where the logarithm stops

**No logarithm of zero, and none of a negative number.** Not "it is very negative" — for
zero the limit runs off to $-\infty$ and never arrives, and for a negative number there is
no real answer at all. In practice this means a formula that takes the logarithm of a
measured quantity has to be guarded: a ratio of zero, which is what a disconnected probe
produces, will crash it rather than return a large number. The lab in this module makes
that check explicit for exactly this reason.

**Unless the number is allowed to be complex.** Module 1's polar form does define one.
Since $-1 = e^{j\pi}$, it is consistent to write $\ln(-1) = j\pi$, and generally
$\ln(re^{j\theta}) = \ln r + j\theta$: the modulus goes to the real part and the angle to
the imaginary part. But $\theta$ and $\theta + 2\pi$ are the same point, so the complex
logarithm has infinitely many values differing by $2\pi j$, and it stops being a function
until you pick a branch. That is a real subject and not a first-year one; the useful
takeaway is that the modulus and the angle separate, which is what a Bode plot draws in
two panels.

**Ratios very close to one lose their digits.** Computing $\ln(1 + x)$ for $x = 10^{-9}$
by forming $1 + x$ first throws away the answer, because $1 + 10^{-9}$ rounds to something
whose logarithm is not accurately $10^{-9}$. Every serious library carries a separate
`log1p` for this. It matters here whenever you take the logarithm of a gain that is almost
exactly unity — the flat part of a filter response, where a genuine 0.01 dB of droop can
be swamped by the arithmetic used to find it.

**A logarithm needs a pure number.** You cannot take the logarithm of 5 volts. $\log$ of
a quantity with units is meaningless, because the exponent rules that defined it assume
you can multiply the thing by itself. Every logarithm in this subject is therefore of a
**ratio** — output over input, voltage over some reference voltage, frequency over some
reference frequency. When a figure looks like the logarithm of a bare quantity, as
"$-107$ dBm" does, a reference has been agreed and hidden. The next unit is about the
system of units built on exactly that trick.
''',
                },
                {
                    "title": "One over ten, in a unit that adds",
                    "minutes": 16,
                    "body": r'''
Here is a receiver, drawn as four boxes in a row. An antenna delivers 2.00 µV. A low-noise
amplifier multiplies it by 7.9433. A length of cable between the amplifier and the rest
multiplies by 0.59566 — it loses signal, so its multiplier is below one. A filter
multiplies by 0.79433. A final amplifier multiplies by 39.811.

To find what comes out you multiply five numbers together, and the answer is 299 µV. Now
change the cable and do it again. Now ask which stage costs you the most. Now ask what
happens if you put two of the filters in. Every one of those questions is a fresh chain of
multiplications, and none of them can be done in your head.

The decibel exists to turn that chain into a sum. It is not a different physics and it is
not an approximation; it is the previous unit's logarithm, applied to the one thing this
subject does most, with a scale factor chosen by convention.

## Why a logarithm, and why base ten

The chain multiplies. Logarithms turn multiplication into addition. So take the logarithm
of every stage's multiplier, add them, and take the exponential at the end. Base ten,
because the numbers involved span decades and a human has to read them.

That alone would give a workable unit — call it the *bel*, and a gain of 100 is 2 bels.
The problem is granularity. The interesting range of a real circuit is roughly $10^{-6}$
to $10^{6}$, which in bels is $-6$ to $+6$: twelve units to cover everything, so useful
figures come out as 1.7 bels and 0.3 bels and every quantity needs decimals. Multiply by
ten and the whole range becomes $-60$ to $+60$, one unit is a difference you can just
about measure, and most figures are whole numbers. That is the **deci**bel, and the 10 in
front of the logarithm is that decision and nothing more:

$$\text{gain in dB} = 10\log_{10}\frac{P_2}{P_1}$$

for a ratio of **powers**.

## Where the 20 comes from

Most of what you measure is not a power. It is a voltage, or a current, or an amplitude of
some kind. Those relate to power through a square: a voltage $V$ across a resistance $R$
delivers $P = V^2/R$.

So if two voltages sit across the same resistance, their power ratio is the square of
their voltage ratio, and the third of the previous unit's three lines does the rest:

$$10\log_{10}\frac{P_2}{P_1} = 10\log_{10}\left(\frac{V_2}{V_1}\right)^{2}
= 10 \times 2 \times \log_{10}\frac{V_2}{V_1} = 20\log_{10}\frac{V_2}{V_1}$$

The 20 is not a second convention to memorise alongside the 10. It is the 10, with the
$\log(a^n) = n\log a$ rule applied to the squaring that turns amplitude into power. Every
time you write 20 you are asserting that the quantity you have is an amplitude; every time
you write 10 you are asserting it is a power. Choosing correctly is the entire skill, and
choosing wrongly halves or doubles every figure you will ever quote.

Note what this means: **a factor of two in power and a factor of two in amplitude are
different decibel figures**, 3.01 dB and 6.02 dB. They describe different physical
situations and both are right.

## The landmarks

Six numbers cover most of what anyone needs without a calculator.

```
amplitude ratio    dB           power ratio      dB
--------------------------------------------------------
   x1            0.00             x1            0.00
   x sqrt(2)     3.01             x2            3.01
   x2            6.02             x4            6.02
   x10          20.00             x10          10.00
   x100         40.00             x100         20.00
   /2           -6.02             /2           -3.01
```

And three consequences worth internalising:

* **Decibels add where gains multiply.** 20 dB then 14 dB is 34 dB. Nothing was
  multiplied. In plain ratios that is $10 \times 5 = 50$, and $20\log_{10}50 = 33.98$ dB —
  the same answer, reached by doing the arithmetic the unit was invented to avoid.
* **A sign is a direction, not an error.** $-6$ dB is a loss of half the amplitude,
  $+6$ dB is a gain of double. A chain with more loss than gain has a negative total, and
  that is a perfectly ordinary circuit.
* **0 dB means times one**, not "no signal". A plot that sits at 0 dB across most of its
  width is describing a circuit that passes its input through unchanged.

## Worked: the receiver chain, forwards and backwards

Take the four boxes from the opening and quote each in decibels. Amplitudes, so the 20:

```
LNA        20 log10(7.9433)  = 20 *  0.90000 = +18.0 dB
cable      20 log10(0.59566) = 20 * -0.22500 =  -4.5 dB
filter     20 log10(0.79433) = 20 * -0.10000 =  -2.0 dB
final amp  20 log10(39.811)  = 20 *  1.60000 = +32.0 dB
                                               --------
total                                          +43.5 dB
```

Convert the total back to a plain ratio to find the output:

```
ratio = 10^(43.5/20) = 10^2.175 = 149.62
out   = 2.00 uV * 149.62 = 299.2 uV
```

Now do it the other way, multiplying the four ratios and never leaving them:

```
7.9433 * 0.59566 = 4.73151
4.73151 * 0.79433 = 3.75838
3.75838 * 39.811  = 149.62
```

The same 149.62, to five figures. That agreement is the point: the decibel version added
four numbers, and the direct version needed three multiplications and gave no insight
about which stage mattered. From the decibel column you can see instantly that the final
amplifier dominates, that cable and filter together cost 6.5 dB — a factor of about 2.1 —
and that removing the filter would lift the output to 45.5 dB, or 376 µV, without
recomputing anything.

One more move, because it is how the figure is actually quoted. Suppose the antenna
delivers $-107$ dBm, which means 107 dB below one milliwatt. The chain has 43.5 dB of gain
in it, so the output is $-107 + 43.5 = -63.5$ dBm. The addition is identical; only the
reference has changed, and the next section is about that.

## Worked: measuring a slope off a response that has not settled

Take the RC low-pass of module 2 with $R = 10.0$ kΩ and $C = 10.0$ nF. Its corner sits at

$$f_c = \frac{1}{2\pi RC} = \frac{1}{2\pi \times 10^{4} \times 10^{-8}} = 1591.5\ \text{Hz}$$

and its exact amplitude response is $|G| = 1/\sqrt{1 + (f/f_c)^2}$. Measure it at 5.00 kHz
and again at 50.0 kHz, a decade apart, and take the difference in decibels.

```
f = 5.00 kHz:   f/fc = 3.14159      (f/fc)^2 = 9.8696
                |G| = 1/sqrt(10.8696) = 1/3.29691 = 0.303314
                dB  = 20 log10(0.303314) = -10.362

f = 50.0 kHz:   f/fc = 31.4159      (f/fc)^2 = 986.96
                |G| = 1/sqrt(987.96) = 1/31.4318 = 0.0318149
                dB  = 20 log10(0.0318149) = -29.947

slope = -29.947 - (-10.362) = -19.585 dB per decade
```

Nineteen and a half, not twenty. The textbook figure is 20 dB per decade, and the
measurement is 0.42 dB short of it. Nothing is wrong with either. The 20 dB figure is the
**asymptote** — what the slope approaches far above the corner — and 5 kHz is only 3.14
times the corner, close enough that the 1 under the square root has not yet become
negligible. Move both readings a decade further out:

```
f = 50.0 kHz:   dB = -29.947
f = 500  kHz:   f/fc = 314.159, |G| = 1/314.161 = 0.00318308
                dB = -49.943

slope = -49.943 - (-29.947) = -19.996 dB per decade
```

Four thousandths of a decibel from 20. The lesson is not that the rule is unreliable; it
is that a straight-line rule about *asymptotes* is quoted for the region where the
asymptote holds, and one decade above the corner is the usual boundary. In the same
circuit, the octave figure from 50 kHz to 100 kHz comes to $-6.017$ dB against the
$20\log_{10}2 = 6.021$ dB the rule predicts — same fact, smaller step.

## Decibels of what?

A decibel is a ratio, so a bare decibel figure with nothing to compare against is
incomplete. Two ways out are in use.

The first is that the comparison is obvious from context: a filter's response is output
over input, an amplifier's gain is out over in, and nobody writes it down.

The second is a **suffixed unit**, where a reference is agreed once and attached to the
name:

```
dBm    reference 1 mW               0 dBm = 1 mW,  +30 dBm = 1 W
dBW    reference 1 W                0 dBW = 1 W  = +30 dBm
dBV    reference 1 V (amplitude)    0 dBV = 1 V,   -60 dBV = 1 mV
dBuV   reference 1 uV (amplitude)   0 dBuV = 1 uV
```

These *are* absolute quantities, because the ratio has been completed for you. And they
mix with plain decibels the obvious way, which is what makes them worth the trouble: dBm
plus dB is dBm, as the receiver chain showed. What you must not do is add two dBm figures
together — that is a power times a power, which is not a thing.

## The mistakes people actually make

**Using 10 on an amplitude.** A voltage gain of 100 is 40 dB, not 20 dB. This is the
single commonest error in the subject and it is tempting because 10 is the definition and
20 feels like a special case, when in fact almost every measurement you make is an
amplitude and 20 is what you will use nine times out of ten.

**Adding decibels when the signals add.** Decibels add when *gains cascade*, because gains
multiply. Two signals arriving at the same node do not multiply; they add. Two equal
signals in phase give twice the amplitude, which is +6.02 dB. Two equal uncorrelated
signals — two noise sources, say — add in power instead, giving +3.01 dB. Neither is
"3 dB plus 3 dB". The previous unit is why: there is no rule for $\log(a + b)$.

**Thinking $-3$ dB means half.** It means half the *power* and $1/\sqrt{2} = 0.707$ of the
amplitude. Half the amplitude is $-6.02$ dB, which is a noticeably different point on a
curve. A filter's stated bandwidth is the $-3$ dB one, so at the edge of the band your
signal still has 71% of its amplitude, and if you were expecting 50% you will mis-size
everything downstream.

**Treating a decibel figure as a quantity.** "The output is 43.5 dB" says nothing until
you know 43.5 dB relative to what. If the answer is "relative to the input", it is a gain,
and it does not tell you whether anything came out at all — a 43.5 dB amplifier fed
nothing still delivers nothing.

## Where the decibel stops

**It says nothing about phase.** $20\log_{10}|G|$ throws away the argument of a complex
gain deliberately. Two circuits with identical magnitude responses can behave completely
differently in time, and one of them can be unstable when you close a loop round it. That
is why every Bode plot has a second panel, and why module 6's damping ratio is not
recoverable from the magnitude alone until you look at what happens near the peak.

**The 10-versus-20 equivalence needs equal impedances.** The derivation used $P = V^2/R$
twice with the *same* $R$. Compare voltages measured across a 50 Ω load and a 600 Ω load
and the amplitude ratio in decibels is no longer the power ratio in decibels — they differ
by $10\log_{10}(600/50) = 10.8$ dB. In radio work, where everything is 50 Ω, the two
coincide and people stop distinguishing them; the habit then travels into circuits where
the impedances are not equal and quietly stops being true.

**Corner frequencies do not simply add.** Two identical first-order stages, buffered so
they do not load each other, each $-3$ dB at $f_c$, are $-6$ dB at $f_c$ together — so the
*pair's* $-3$ dB point is lower, at $f_c\sqrt{\sqrt{2}-1} = 0.644f_c$. Cascading
narrows the band. The general figure for $n$ identical buffered stages is
$f_c\sqrt{2^{1/n}-1}$, and if the stages actually load each other, as two RC sections wired
directly together do, the answer is different again and has to come from solving the whole
network at once.

**A ratio of zero has no decibel value.** A response with a true null in it — a notch
filter at its notch, an ideal bridge at balance — goes to $-\infty$ dB and the plot cannot
draw it. Real circuits never quite reach zero, so what you actually see is a very deep
finite notch whose depth is set by component tolerance rather than by the design, which is
the honest reason a datasheet quotes "typically $-60$ dB" and not a formula.
''',
                },
            ],
            "sandbox": {
                "title": "Decibels, decades, and a slope you can read off",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 1.5, "K": 1},
                "brief": r'''
The top panel is the size of a circuit's output relative to its input, in decibels.
The bottom panel is the phase shift in degrees. Both are drawn against frequency in
radians per second, and the frequency axis is **logarithmic** — equal distances along
it are equal *multiplications*, not equal additions.

The slider $K$ is a plain gain, the number the circuit multiplies by when the
frequency is low enough not to matter. It opens at 1. The other two sliders set where
the response starts to fall away; with $\zeta$ at 1.5 the fall happens in two separate
stages, at about 7.6 and 52 rad/s, which is what makes the slope worth reading.
''',
                "notice": [
                    r"With $K = 1$ the flat left-hand part of the top panel sits at **0 dB**. 0 dB does not mean no output; it means times one. That is worth fixing now, because a plot that spends most of its time near zero is describing a circuit that mostly passes its input through.",
                    r"Take $K$ up to 10. Every point of the magnitude curve lifts by exactly 20 dB — the flat part moves from 0 to +20 — and the phase panel does not move at all. Multiplying a gain shifts a decibel curve bodily; it never changes its shape, and it never touches the phase.",
                    r"Read the top panel at $\omega = 100$ and again at $\omega = 1000$, which is one decade apart. It falls from about $-29$ dB to about $-68$ dB: 39 dB in a factor of ten. Two first-order corners together give 40 dB per decade, and the missing decibel is the upper corner at 52 rad/s: it is less than a factor of two below the left-hand reading, so at $\omega = 100$ it is still bending into its asymptote rather than yet contributing its full 20 dB per decade. Read the decade from 200 to 2000 instead, with both corners further behind, and the fall is 39.7 dB.",
                    r"Look at the five gridlines along the bottom: 0.1, 1, 14, 168, 2000 (rounded to fit). They are equally spaced on the page, and each is 11.9 times the one before. Equal distance means equal ratio — which is why a fixed slope in dB per decade draws as a straight line here and as a curve on any other axis.",
                ],
            },
            "quiz": {
                "title": "Ratios, in the unit they are usually quoted in",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"An amplifier makes its output 100 times the amplitude of its input. What is its gain in decibels?",
                        "opts": ["20 dB", "40 dB", "100 dB", "2 dB"],
                        "a": 1,
                        "why": (
                            r"Amplitude ratios take the 20: $20\log_{10}100 = 20 \times 2 = 40$ dB. Answering 20 dB is "
                            r"using the power rule on an amplitude, which halves every figure you will ever quote; "
                            r"answering 2 dB is the bare logarithm with the multiplier forgotten."
                        ),
                    },
                    {
                        "q": r"A stage delivers twice the *power* it is given. How many decibels is that?",
                        "opts": ["3.01 dB", "6.02 dB", "2 dB", "0.30 dB"],
                        "a": 0,
                        "why": (
                            r"Power ratios take the 10: $10\log_{10}2 = 3.01$ dB. The 6.02 dB figure is the same "
                            r"factor of two applied to an *amplitude*, and the two differ by exactly the factor of "
                            r"2 that squaring an amplitude introduces. Getting 0.30 means the multiplier was left off "
                            r"entirely — that is $\log_{10}2$ on its own."
                        ),
                    },
                    {
                        "q": r"At its corner frequency a filter's output amplitude is $1/\sqrt{2}$ of its input. In decibels that is:",
                        "opts": [r"$-1.5$ dB", r"$-3.01$ dB", r"$-6.02$ dB", r"$-0.71$ dB"],
                        "a": 1,
                        "why": (
                            r"$20\log_{10}(1/\sqrt{2}) = 20 \times (-0.1505) = -3.01$ dB. Half the *power* is passing, "
                            r"so it is the same $-3$ dB whichever of the two rules you use, provided you feed each one "
                            r"the quantity it expects. $-6$ dB would be a fall to one half in amplitude, which is "
                            r"further down than the corner."
                        ),
                    },
                    {
                        "q": r"Two stages in cascade: the first has a gain of 20 dB, the second 14 dB. What is the gain of the pair?",
                        "opts": ["34 dB", "280 dB", "17 dB", "6 dB"],
                        "a": 0,
                        "why": (
                            r"Gains multiply, so their logarithms add: $20 + 14 = 34$ dB. In plain ratios that is "
                            r"$10 \times 5 = 50$, and $20\log_{10}50 = 34.0$ dB — the same answer with more arithmetic. "
                            r"Multiplying the decibel figures together, or averaging them, corresponds to nothing "
                            r"physical at all."
                        ),
                    },
                    {
                        "q": r"A first-order roll-off falls at 20 dB per decade. How much does it fall in one octave, where the frequency merely doubles?",
                        "opts": ["10 dB", "6.02 dB", "2 dB", "20 dB"],
                        "a": 1,
                        "why": (
                            r"A decade is a factor of ten and an octave a factor of two, so the octave figure is "
                            r"$20\log_{10}2 = 6.02$ dB. Both describe exactly the same line; only the size of the step "
                            r"along the frequency axis differs. Halving the decade figure to 10 dB assumes the slope "
                            r"is linear in frequency, and it is linear in the *logarithm* of frequency."
                        ),
                    },
                    {
                        "q": r"A capacitor discharges as $v = 5e^{-t/\tau}$ with $\tau = 2$ ms. When does it reach 1 V?",
                        "opts": ["0.4 ms", "1.6 ms", "3.22 ms", "10 ms"],
                        "a": 2,
                        "why": (
                            r"Rearranging: $e^{-t/\tau} = 1/5$, so $t = \tau\ln 5 = 2\,\text{ms} \times 1.609 = 3.22$ ms. "
                            r"The tempting 0.4 ms comes from treating the decay as a straight line — dividing the "
                            r"voltages and multiplying by $\tau$ — which would be right for a ramp and is wrong here by "
                            r"a factor of eight."
                        ),
                    },
                ],
            },
            "derive": {
                "title": "Where 20 dB per decade comes from",
                "minutes": 12,
                "vars": ["f", "f_c", "G"],
                "brief": r'''
The amplitude response of the resistor–capacitor filter from module 2, written in
terms of the corner frequency $f_c = 1/(2\pi RC)$, is

$$|G| = \frac{1}{\sqrt{1 + (f/f_c)^2}}$$

Everything the Bode sketch does with a straight edge comes out of this one
expression and two approximations.
''',
                "steps": [
                    {
                        "prompt": r"Put $f = f_c$ into the expression. Write $|G|$ at the corner.",
                        "answer": r"1/\sqrt{2}",
                        "hint": r"At $f = f_c$ the ratio $f/f_c$ is 1, so the bottom is $\sqrt{1+1}$.",
                        "deconstruct": [
                            r"$(f/f_c)^2 = 1$.",
                            r"So the whole bottom is $\sqrt{2}$, and the top is 1.",
                        ],
                    },
                    {
                        "prompt": r"Far above the corner the 1 under the root is swamped by $(f/f_c)^2$. Drop it and write the approximate $|G|$ for $f \gg f_c$, in terms of $f$ and $f_c$.",
                        "answer": r"f_c/f",
                        "placeholder": r"a ratio of the two frequencies",
                        "hint": r"With the 1 gone, the bottom is $\sqrt{(f/f_c)^2}$, which is just $f/f_c$. One over that is the answer.",
                        "deconstruct": [
                            r"$\sqrt{1 + (f/f_c)^2} \approx \sqrt{(f/f_c)^2} = f/f_c$ when $f/f_c$ is large.",
                            r"$|G|$ is one divided by that.",
                        ],
                    },
                    {
                        "prompt": r"Take two frequencies a decade apart, $f$ and $10f$, both far above the corner, so the approximation holds at each. Write the ratio $|G(10f)|/|G(f)|$.",
                        "answer": r"1/10",
                        "hint": r"Both are $f_c$ over the frequency, so $f_c$ and $f$ both cancel out of the ratio.",
                        "deconstruct": [
                            r"$|G(10f)| \approx f_c/(10f)$ and $|G(f)| \approx f_c/f$.",
                            r"Dividing one by the other leaves only the 10.",
                        ],
                    },
                    {
                        "prompt": r"An amplitude ratio in decibels is $20\log_{10}$ of it, and $\log_{10}(1/10) = -1$. Write the *change* in the response over that decade, in decibels, as a signed number.",
                        "answer": r"-20",
                        "hint": r"Multiply the two numbers you have been handed.",
                        "deconstruct": [
                            r"The ratio is $1/10$.",
                            r"$20 \times (-1)$.",
                        ],
                    },
                    {
                        "prompt": r"Now go back to the exact expression and put $f = 10f_c$ into it. Write the exact $|G|$ there.",
                        "answer": r"1/\sqrt{101}",
                        "hint": r"$(10f_c/f_c)^2 = 100$, and the 1 is still there.",
                        "deconstruct": [
                            r"$f/f_c = 10$, so $(f/f_c)^2 = 100$.",
                            r"The bottom is $\sqrt{1 + 100}$.",
                        ],
                    },
                ],
                "closing": r'''
The exact value one decade out is $1/\sqrt{101} = 0.09950$, and the approximation
said $0.1$. In decibels that is $-20.04$ against $-20$: the straight line is wrong by
four hundredths of a decibel, which no instrument in a first-year lab can see. That
is why the sketch is drawn with a ruler and why nobody apologises for it.
''',
            },
            "blanks": [
                {
                    "title": "The three lines a logarithm is for, and two rearrangements",
                    "minutes": 8,
                    "caption": "log is base ten, ln is natural, and tau is a time constant",
                    "lang": "text",
                    "brief": r'''
Nothing is executed here. The first three lines are the identities every use of a
logarithm in this course comes from; the last three are the places you will actually
reach for them.

`e^(x)` is the exponential, `*` is multiplication, and `V0` is a starting voltage that
decays.
''',
                    "listing": r'''
log(a * b)                                 =  ___

log(a / b)                                 =  ___

log(a^n)                                   =  ___

ln x, written with a base-ten logarithm    =  ___

v = V0 * e^(-t/tau), solved for t      t   =  ___

x, given that log10(x) = -3            x   =  ___
''',
                    "blanks": [
                        {
                            "prompt": "A product, taken apart.",
                            "hole": "?",
                            "opts": ["log a * log b", "log a + log b", "log(a + b)", "(log a)^b"],
                            "a": 1,
                            "why": r"$\log(ab) = \log a + \log b$. Exponents add when powers multiply, and a logarithm *is* an exponent, so the rule is that fact read backwards. Check it: $\log_{10}(2 \times 5) = \log_{10}10 = 1$, and $0.30103 + 0.69897 = 1$.",
                            "whys": [
                                r"Multiplying the two logarithms corresponds to nothing. Test it on $2 \times 5$: the true answer is $\log_{10}10 = 1$, and $0.30103 \times 0.69897 = 0.2104$.",
                                r"$\log(ab) = \log a + \log b$. Exponents add when powers multiply, and a logarithm *is* an exponent, so the rule is that fact read backwards. Check it: $\log_{10}(2 \times 5) = \log_{10}10 = 1$, and $0.30103 + 0.69897 = 1$.",
                                r"This turns a product into a sum *inside* the logarithm, which changes the number. $\log_{10}(2 \times 5) = 1$ and $\log_{10}(2 + 5) = 0.845$. There is no rule for the logarithm of a sum, and its absence is exactly why two signals added together are awkward in decibels.",
                                r"A power outside the logarithm is not what the third identity says either — that one moves an exponent from inside to a multiplier in front, giving $n\log a$, not a logarithm raised to a power.",
                            ],
                        },
                        {
                            "prompt": "A quotient. Same idea, opposite sign.",
                            "hole": "?",
                            "opts": ["log a / log b", "log a - log b", "log a + log b", "log(a - b)"],
                            "a": 1,
                            "why": r"$\log(a/b) = \log a - \log b$. This is the line the decibel runs on: every decibel figure is the logarithm of a ratio, and it can always be split into the output's logarithm minus the input's. In the divider question of this module, $20\log_{10}(1000/4300) = 60 - 72.67 = -12.67$ dB with no division done at all.",
                            "whys": [
                                r"Dividing the logarithms is the change-of-base formula, which answers a different question: $\log a/\log b$ is $\log_b a$. Useful, but not this.",
                                r"$\log(a/b) = \log a - \log b$. This is the line the decibel runs on: every decibel figure is the logarithm of a ratio, and it can always be split into the output's logarithm minus the input's. In the divider question of this module, $20\log_{10}(1000/4300) = 60 - 72.67 = -12.67$ dB with no division done at all.",
                                r"That is the product rule. A ratio smaller than one must give a negative logarithm, and adding two positive logarithms can never produce one.",
                                r"A difference inside the logarithm is a different number, and it is undefined the moment $b$ exceeds $a$ — whereas $\log(a/b)$ is perfectly well behaved there and simply comes out negative.",
                            ],
                        },
                        {
                            "prompt": "A power. This one is why an amplitude decibel carries a 20.",
                            "hole": "?",
                            "opts": ["(log a)^n", "n * log a", "log a / n", "log n + log a"],
                            "a": 1,
                            "why": r"$\log(a^n) = n\log a$, because $a^n$ is $a$ multiplied by itself $n$ times and the product rule turns that into $n$ copies of $\log a$. Power goes as amplitude squared, so $10\log(V^2/\!R\text{-stuff})$ becomes $20\log V$ — the 20 in the amplitude rule is this identity with $n = 2$.",
                            "whys": [
                                r"Raising the logarithm to the power is a different operation and gives a different number: $\log_{10}(100^2) = 4$, while $(\log_{10}100)^2 = 2^2 = 4$ agrees here by accident and fails everywhere else — try $a = 1000$, where the true answer is 6 and this gives 9.",
                                r"$\log(a^n) = n\log a$, because $a^n$ is $a$ multiplied by itself $n$ times and the product rule turns that into $n$ copies of $\log a$. Power goes as amplitude squared, so $10\log(V^2/\!R\text{-stuff})$ becomes $20\log V$ — the 20 in the amplitude rule is this identity with $n = 2$.",
                                r"Dividing by $n$ is what a *root* does: $\log(a^{1/n}) = (\log a)/n$. Right family, wrong direction, and it would make the amplitude rule a 5 rather than a 20.",
                                r"This treats $a^n$ as though it were $na$. Squaring 100 gives 10 000, and doubling it gives 200; the logarithms of those two are 4 and 2.301, which are not close.",
                            ],
                        },
                        {
                            "prompt": "Changing base, in the direction you need when a calculator has one button and the physics wants the other.",
                            "hole": "?",
                            "opts": ["log10(x) / 2.302585", "2.302585 * log10(x)", "log10(x) - 2.302585", "log10(x)"],
                            "a": 1,
                            "why": r"$\ln x = 2.302585\,\log_{10}x$, where $2.302585 = \ln 10$. Sanity check on a number you know: $\ln 10$ must be 2.3026, and $\log_{10}10 = 1$, so the multiplier is the right way up. Getting this backwards scales every time constant answer by 5.3.",
                            "whys": [
                                r"That is the conversion the other way, $\log_{10}x = \ln x/2.302585$. Check with $x = 10$: the natural logarithm of 10 is 2.3026, and this gives $1/2.3026 = 0.434$.",
                                r"$\ln x = 2.302585\,\log_{10}x$, where $2.302585 = \ln 10$. Sanity check on a number you know: $\ln 10$ must be 2.3026, and $\log_{10}10 = 1$, so the multiplier is the right way up. Getting this backwards scales every time constant answer by 5.3.",
                                r"Base change is a scaling, never a shift. A shift would fail immediately at $x = 1$, where both logarithms are zero and any constant added to one of them is not.",
                                r"The two logarithms agree only at $x = 1$. Everywhere else they differ by the factor 2.3026, which is small enough that a wrong answer keeps a believable order of magnitude — the reason this slip survives.",
                            ],
                        },
                        {
                            "prompt": "The decay, run backwards to find a time.",
                            "hole": "?",
                            "opts": ["tau * ln(v / V0)", "tau * ln(V0 / v)", "tau * log10(V0 / v)", "tau * (V0 / v)"],
                            "a": 1,
                            "why": r"$t = \tau\ln(V_0/v)$. Take logs of $v/V_0 = e^{-t/\tau}$ to get $-t/\tau = \ln(v/V_0)$, then flip the ratio to absorb the minus sign. The bigger ratio goes on top so the answer is positive, which is the check to run every time.",
                            "whys": [
                                r"This is the same expression before the minus sign was dealt with, so it returns a negative time for any decay that has actually decayed. The fix is $\ln(v/V_0) = -\ln(V_0/v)$.",
                                r"$t = \tau\ln(V_0/v)$. Take logs of $v/V_0 = e^{-t/\tau}$ to get $-t/\tau = \ln(v/V_0)$, then flip the ratio to absorb the minus sign. The bigger ratio goes on top so the answer is positive, which is the check to run every time.",
                                r"The exponential is base $e$, so only $\ln$ undoes it. This answer is too small by 2.3026 — a 54.7 s bleed time comes out as 23.7 s, which is wrong and not obviously so.",
                                r"No logarithm at all here, so a factor of ten in voltage becomes a factor of ten in time. It does not: each factor of ten costs a further $\tau\ln 10 = 2.303\tau$, the same amount every time.",
                            ],
                        },
                        {
                            "prompt": "A logarithm undone.",
                            "hole": "?",
                            "opts": ["-1000", "-0.001", "0.001", "-30"],
                            "a": 2,
                            "why": r"$\log_{10}x = -3$ means $x = 10^{-3} = 0.001$. A negative logarithm describes a positive number *smaller than one* — the sign lives in the exponent, not in the value. Every quantity with a logarithm is positive, by definition.",
                            "whys": [
                                r"The minus sign belongs in the exponent, not in front of the number. There is no $x$ at all whose base-ten logarithm is $-3$ and which is itself negative, because negative numbers have no real logarithm.",
                                r"Same slip, one step further on: this has both the reciprocal and the sign, and $\log_{10}$ of a negative number does not exist to be $-3$.",
                                r"$\log_{10}x = -3$ means $x = 10^{-3} = 0.001$. A negative logarithm describes a positive number *smaller than one* — the sign lives in the exponent, not in the value. Every quantity with a logarithm is positive, by definition.",
                                r"That is the decibel figure this ratio would produce as an amplitude, $20 \times (-3) = -60$, or as a power, $10 \times (-3) = -30$ — a related and genuinely useful number, but not $x$.",
                            ],
                        },
                    ],
                },
                {
                    "title": "Decibels: what goes in front of the logarithm, and what comes out",
                    "minutes": 9,
                    "caption": "A2/A1 is a ratio of amplitudes, P2/P1 a ratio of powers, D a figure already in decibels",
                    "lang": "text",
                    "brief": r'''
Nothing is executed here either. Each line is a definition or a landmark you will use
without looking it up within a week.

A **decade** is a factor of ten in frequency and an **octave** a factor of two.
''',
                    "listing": r'''
an amplitude ratio A2/A1, in decibels            ___

a power ratio P2/P1, in decibels                 ___

the amplitude ratio that D decibels describes    ___

two stages in cascade, both quoted in decibels   ___

a first-order roll-off, per decade               ___

the same slope, quoted per octave                ___

the half-power point, in decibels                ___
''',
                    "blanks": [
                        {
                            "prompt": "The one you will use nine times out of ten.",
                            "hole": "?",
                            "opts": [
                                "10 log10(A2/A1)",
                                "20 log10(A2/A1)",
                                "20 ln(A2/A1)",
                                "10 log10((A2/A1)^2) / 2",
                            ],
                            "a": 1,
                            "why": r"$20\log_{10}(A_2/A_1)$. Amplitudes take the 20 because power goes as amplitude squared and $\log(A^2) = 2\log A$. A voltage gain of 100 is 40 dB, and calling it 20 dB is the commonest error in the subject.",
                            "whys": [
                                r"That is the power rule applied to an amplitude, which halves every figure you will ever quote. It is tempting because 10 is the definition, but almost everything you measure is an amplitude.",
                                r"$20\log_{10}(A_2/A_1)$. Amplitudes take the 20 because power goes as amplitude squared and $\log(A^2) = 2\log A$. A voltage gain of 100 is 40 dB, and calling it 20 dB is the commonest error in the subject.",
                                r"The decibel is defined on the base-ten logarithm. Using the natural one multiplies every answer by 2.3026, so a factor of ten in amplitude would come out as 46.05 dB rather than exactly 20.",
                                r"Squaring inside and halving outside cancel exactly, leaving the power rule again — $10\log_{10}(A_2/A_1)$, which is half of what an amplitude needs.",
                            ],
                        },
                        {
                            "prompt": "The definition the other one is derived from.",
                            "hole": "?",
                            "opts": ["10 log10(P2/P1)", "20 log10(P2/P1)", "log10(P2/P1)", "10 log10(P2 - P1)"],
                            "a": 0,
                            "why": r"$10\log_{10}(P_2/P_1)$. Doubling a power is $10\log_{10}2 = 3.01$ dB, and doubling an amplitude is 6.02 dB; both are correct, and they describe different situations. The 10 is the *deci* in decibel — the bel itself is the bare logarithm.",
                            "whys": [
                                r"$10\log_{10}(P_2/P_1)$. Doubling a power is $10\log_{10}2 = 3.01$ dB, and doubling an amplitude is 6.02 dB; both are correct, and they describe different situations. The 10 is the *deci* in decibel — the bel itself is the bare logarithm.",
                                r"The 20 belongs to amplitudes. Applying it to a power double-counts the squaring that produced the 20 in the first place, and a doubling of power would be quoted as 6.02 dB rather than 3.01.",
                                r"That is the bel, not the decibel. It is off by the factor of ten the unit is named after, and it puts every interesting circuit into a range of about twelve units, which is why nobody uses it.",
                                r"Decibels compare quantities by division, never by subtraction. A difference of powers is not dimensionless and has no logarithm.",
                            ],
                        },
                        {
                            "prompt": "Back the other way, from a decibel figure to a plain multiplier.",
                            "hole": "?",
                            "opts": ["10^(D/20)", "10^(D/10)", "20^(D/10)", "D/20"],
                            "a": 0,
                            "why": r"$10^{D/20}$. It has to undo $20\log_{10}$, so divide by 20 first and then raise ten to it. Check on a landmark: $D = 40$ gives $10^{2} = 100$, and a gain of 100 in amplitude is indeed 40 dB. For a *power* figure the same reasoning gives $10^{D/10}$.",
                            "whys": [
                                r"$10^{D/20}$. It has to undo $20\log_{10}$, so divide by 20 first and then raise ten to it. Check on a landmark: $D = 40$ gives $10^{2} = 100$, and a gain of 100 in amplitude is indeed 40 dB. For a *power* figure the same reasoning gives $10^{D/10}$.",
                                r"That is the inverse of the power rule, so it returns a power ratio. Fed 40 dB it gives 10 000, which is the *power* ratio that an amplitude ratio of 100 produces — right number, wrong quantity.",
                                r"The base is ten, not twenty. The 20 is a multiplier applied to a base-ten logarithm; it never becomes a base of its own.",
                                r"Dividing is what you do to the exponent, not to the whole thing. This makes the conversion linear, so 40 dB would be a gain of 2 and 80 dB a gain of 4, when in fact each 20 dB is a further factor of ten.",
                            ],
                        },
                        {
                            "prompt": "Two boxes in a row, each with its gain already in decibels.",
                            "hole": "?",
                            "opts": ["D1 * D2", "D1 + D2", "(D1 + D2) / 2", "10^(D1 + D2)"],
                            "a": 1,
                            "why": r"$D_1 + D_2$. Gains multiply, so their logarithms add — that is the entire reason a cascade is quoted this way. 20 dB then 14 dB is 34 dB; in plain ratios $10 \times 5 = 50$ and $20\log_{10}50 = 33.98$ dB, the same answer with more arithmetic.",
                            "whys": [
                                r"Multiplying decibel figures corresponds to nothing physical, and the units give it away: a decibel is already a logarithm, and logarithms are added, never multiplied together.",
                                r"$D_1 + D_2$. Gains multiply, so their logarithms add — that is the entire reason a cascade is quoted this way. 20 dB then 14 dB is 34 dB; in plain ratios $10 \times 5 = 50$ and $20\log_{10}50 = 33.98$ dB, the same answer with more arithmetic.",
                                r"Averaging would say that a 20 dB amplifier followed by a 20 dB amplifier still gives 20 dB, which cannot be right — the signal passed through two of them.",
                                r"This exponentiates a figure that is already in decibels. The sum is the answer; taking a power of ten of it converts to a plain ratio and then quotes it as though it were still in decibels.",
                            ],
                        },
                        {
                            "prompt": "The slope every single-pole filter falls at, far above its corner.",
                            "hole": "?",
                            "opts": ["-10 dB", "-20 dB", "-6.02 dB", "-3.01 dB"],
                            "a": 1,
                            "why": r"$-20$ dB per decade. Far above the corner $|G| \approx f_c/f$, so ten times the frequency is a tenth of the amplitude, and $20\log_{10}(1/10) = -20$ dB. It is an asymptote: measured only three times above the corner it comes out nearer $-19.6$, and a decade further out it is $-19.996$.",
                            "whys": [
                                r"That is the same physical roll-off quoted as a *power* ratio, and a Bode magnitude plot is an amplitude plot. Mixing the two halves every slope on the page.",
                                r"$-20$ dB per decade. Far above the corner $|G| \approx f_c/f$, so ten times the frequency is a tenth of the amplitude, and $20\log_{10}(1/10) = -20$ dB. It is an asymptote: measured only three times above the corner it comes out nearer $-19.6$, and a decade further out it is $-19.996$.",
                                r"That is the fall over one *octave* — a factor of two in frequency, not ten. Same line, smaller step along it.",
                                r"That is the depth of the corner itself, where the response has fallen to $1/\sqrt{2}$. It is a single point on the curve, not a rate of change.",
                            ],
                        },
                        {
                            "prompt": "The same line, walked in factors of two instead of factors of ten.",
                            "hole": "?",
                            "opts": ["-10 dB", "-2 dB", "-6.02 dB", "-20 dB"],
                            "a": 2,
                            "why": r"$-6.02$ dB per octave, because an octave is a factor of two and $20\log_{10}2 = 6.02$. The two figures describe the identical slope; only the size of the step along the frequency axis differs, and $\log_{10}2 = 0.301$ of a decade is what an octave is worth.",
                            "whys": [
                                r"Halving the decade figure assumes the slope is linear in frequency. It is linear in the *logarithm* of frequency, and an octave is 0.301 of a decade, not half of one.",
                                r"This looks like a tenth of the decade figure, which would be right if an octave were a tenth of a decade. It is 0.301 of one.",
                                r"$-6.02$ dB per octave, because an octave is a factor of two and $20\log_{10}2 = 6.02$. The two figures describe the identical slope; only the size of the step along the frequency axis differs, and $\log_{10}2 = 0.301$ of a decade is what an octave is worth.",
                                r"That is the decade figure unchanged. A smaller step along the frequency axis has to give a smaller fall, so the octave number must be below 20 whatever else is true.",
                            ],
                        },
                        {
                            "prompt": "Where a filter's stated bandwidth is measured.",
                            "hole": "?",
                            "opts": ["-3.01 dB", "-6.02 dB", "-1.5 dB", "-0.5 dB"],
                            "a": 0,
                            "why": r"$-3.01$ dB, universally written $-3$ dB. Half the power is getting through, and $10\log_{10}(1/2) = -3.01$; the amplitude there is $1/\sqrt{2} = 0.707$ of the input, and $20\log_{10}(0.707) = -3.01$ as well. The two rules agree because each was fed the quantity it expects.",
                            "whys": [
                                r"$-3.01$ dB, universally written $-3$ dB. Half the power is getting through, and $10\log_{10}(1/2) = -3.01$; the amplitude there is $1/\sqrt{2} = 0.707$ of the input, and $20\log_{10}(0.707) = -3.01$ as well. The two rules agree because each was fed the quantity it expects.",
                                r"That is where the *amplitude* has fallen to a half, which is further down the curve — for a first-order filter it is at $\sqrt{3} = 1.73$ times the corner frequency, not at the corner.",
                                r"Half of the right answer, which is what applying the amplitude rule to a power ratio gives. Both rules must land on the same $-3.01$ dB here; if yours do not, one of them was handed the wrong quantity.",
                                r"Too shallow to be any standard landmark. $-0.5$ dB is a ratio of 0.944 in amplitude, which is inside the flat part of the band rather than at its edge.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "A divider, quoted the way a gain is quoted",
                    "minutes": 4,
                    "brief": r'''
The first step of every decibel question is to get a **ratio**, and the ratio here is the
one module 2 already gives you: a divider's output over its input.

A gain is an amplitude ratio, so it takes the 20:

$$D = 20\log_{10}\frac{V_{\text{out}}}{V_{\text{in}}}$$

Read the two resistors off the schematic. The source value is on the schematic too, and
you will not need it — but work out why before you decide that.
''',
                    "prompt": r"What is the gain of this divider, expressed in decibels?",
                    "note": "Answer in decibels, to two decimal places. A circuit that loses signal has a negative gain in decibels.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 3300},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 1000},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "5.00 V"},
                        {"label": "R1 (supply to the probed node)", "value": "3.30 kΩ"},
                        {"label": "R2 (probed node to ground)", "value": "1.00 kΩ"},
                        {"label": "Asked for", "value": "the gain in decibels"},
                    ],
                    # The gain is the solved node voltage over the source's own value, both read
                    # from the netlist, so the check follows the schematic if the schematic
                    # changes and repeats no constant that is already drawn.
                    "check": r'''
return 20 * Math.log10(c.vout() / c.values('V')[0]);
''',
                    "answer": -12.67,
                    "tol": 0.03,
                    "unit": "dB",
                    "hint": r"Get the ratio first — $R_2/(R_1 + R_2)$ — and only then take $20\log_{10}$ of it. The source cancels out of the ratio, which is why its value never enters.",
                    "wrong": r"If you got $+12.67$, the ratio went in upside down: 4300/1000 rather than 1000/4300, and a divider cannot have gain. If you got $-6.33$, the power rule was used on an amplitude, which halves every decibel figure. If you got $-2.30$, the divider was read the wrong way round as $3300/4300$. If you got $1.16$, that is the output voltage in volts, one step short of the question.",
                    "why": r'''
Two steps, and the second one is the whole module.

```
ratio = R2 / (R1 + R2) = 1000 / 4300 = 0.2325581
D     = 20 log10(0.2325581) = 20 * (-0.6334685) = -12.669 dB
```

The source never appears. With 5.00 V in, the probe reads $5.00 \times 0.2325581 = 1.1628$
V, and $1.1628/5.00$ is the same 0.2325581 — the divider multiplies by a fixed number
whatever you feed it, and that number is what a gain is.

Now do the logarithm the other way, using $\log(a/b) = \log a - \log b$, because this is
the arithmetic the unit exists for:

```
20 log10(1000) = 20 * 3.000000 = 60.000 dB
20 log10(4300) = 20 * 3.633469 = 72.669 dB
                                --------
                                -12.669 dB
```

No division was performed. That is a small saving here and an enormous one in a chain of
eight stages, which is the situation the decibel was invented for.

One sanity check worth building the habit of: 1000/4300 is a bit under a quarter, and a
quarter in amplitude is $-12.04$ dB. The answer must therefore sit slightly below $-12$,
and $-12.67$ does.
''',
                    "aside": "Swap R1 and R2 and the gain becomes $20\\log_{10}(3300/4300) = -2.30$ dB — a much gentler loss, because most of the voltage now survives. A divider's decibel figure is always negative, and it approaches 0 dB as R1 shrinks towards nothing, which is the same statement as \"a wire has no loss\".",
                },
                {
                    "title": "How far down is the filter here",
                    "minutes": 7,
                    "brief": r'''
Same question, one rule further along. The gain of an RC low-pass depends on frequency,
and module 2 gave its size:

$$|G| = \frac{1}{\sqrt{1 + (f/f_c)^2}} \qquad\text{with}\qquad f_c = \frac{1}{2\pi RC}$$

So there are three steps now: the corner from the components, the ratio at the frequency
asked about, and the decibels from the ratio. The source is a sinusoid of 1.00 V, so the
probe reads $|G|$ directly.

Do not use the 20 dB per decade shortcut for this one. The frequency asked about is close
enough to the corner that the asymptote is visibly wrong, and finding out by how much is
half the point of the question.
''',
                    "prompt": r"What is the gain of this filter at 1.00 kHz, in decibels?",
                    "note": "Answer in decibels, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V sinusoid at 1.00 kHz"},
                        {"label": "R1", "value": "4.70 kΩ"},
                        {"label": "C1", "value": "100 nF"},
                        {"label": "Asked for", "value": "the gain at that frequency, in decibels"},
                    ],
                    # The solver's own AC magnitude at 1 kHz, divided by the source amplitude it
                    # was driven with. Both come out of the netlist, so neither R nor C is
                    # restated here and a redrawn schematic cannot leave this answer stale.
                    "check": r'''
return 20 * Math.log10(c.gain(1000) / c.values('V')[0]);
''',
                    "answer": -9.88,
                    "tol": 0.04,
                    "unit": "dB",
                    "hint": r"$f_c = 1/(2\pi \times 4700 \times 10^{-7})$. Then $f/f_c$, then square it, then add one, then the square root, then invert, and only then $20\log_{10}$. Doing it in that order keeps every intermediate a number you can check.",
                    "wrong": r"If you got $-9.41$, that is the asymptote $-20\log_{10}(f/f_c)$, which ignores the 1 under the root; at only 2.95 times the corner it is 0.47 dB optimistic. If you got $-4.94$, the power rule was used on an amplitude. If you got $-3.01$, the frequency was taken to be the corner itself, and 1 kHz is well past it. If you got $-11.94$, the ratio $f/f_c$ was not squared before the 1 was added.",
                    "why": r'''
Three steps, in order.

```
fc  = 1 / (2 pi R C) = 1 / (2 pi * 4700 * 1.00e-7)
    = 1 / 2.953097e-3 = 338.63 Hz

f/fc      = 1000 / 338.63 = 2.953097
(f/fc)^2  = 8.720782
1 + that  = 9.720782
sqrt      = 3.117817
|G|       = 1 / 3.117817 = 0.3207372

D = 20 log10(0.3207372) = 20 * (-0.4938506) = -9.877 dB
```

Two things are worth reading off that arithmetic.

First, $f/f_c$ came out as 2.953097, and $2\pi f R C = 2\pi \times 1000 \times 4700 \times
10^{-7}$ is 2.953097 as well. That is not a coincidence — $f/f_c = 2\pi fRC$ identically,
because $f_c$ was defined as $1/(2\pi RC)$. Forming $\omega RC$ directly saves you a
division and a chance to slip.

Second, compare with the straight-line rule. The asymptote says the response is
$-20\log_{10}(2.953097) = -9.406$ dB, and the truth is $-9.877$ dB: the sketch is 0.47 dB
optimistic here. It has to be, because the asymptote drops the 1 in $1 + (f/f_c)^2$ and at
$f/f_c = 2.95$ that 1 is still more than a tenth of the 8.72 beside it. Go to 10 kHz,
where $f/f_c = 29.53$, and the discrepancy falls to 0.005 dB. One decade above the corner
is the usual line between "sketch it" and "compute it".
''',
                    "aside": "In plain terms the filter is passing 0.321 of what it is given at 1 kHz — about a third of the amplitude, and $0.321^2 = 0.103$, about a tenth of the power. That the power figure is a tenth while the amplitude figure is a third is the whole content of the 10-versus-20 distinction, seen once on real numbers.",
                },
                {
                    "title": "When does it get there",
                    "minutes": 8,
                    "brief": r'''
This one asks for a time rather than a level, so the exponential has to be run backwards —
and running an exponential backwards is what a logarithm is.

Module 4's charging curve is $v(t) = V_s(1 - e^{-t/\tau})$ with $\tau = RC$. Rearranged
for the time at which a stated voltage is reached:

$$t = \tau\ln\frac{V_s}{V_s - v}$$

Note what sits underneath: the voltage still **to go**, not the voltage reached. The
quantity decaying in a charging circuit is the gap.
''',
                    "prompt": r"How long after the supply is switched on does the capacitor voltage reach 7.50 V?",
                    "note": "Answer in milliseconds, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 47000},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 2.2e-7},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "9.00 V, switched on at t = 0"},
                        {"label": "R1", "value": "47.0 kΩ"},
                        {"label": "C1", "value": "220 nF"},
                        {"label": "Capacitor at t = 0", "value": "empty"},
                        {"label": "Asked for", "value": "the time at which v reaches 7.50 V"},
                    ],
                    # tau is not restated: it is recovered from the circuit's own measured -3 dB
                    # corner, since tau = 1/(2 pi fc) for a first-order network. The supply comes
                    # off the netlist too, so only the 7.50 V target — which is in the prompt and
                    # nowhere on the schematic — is written down here.
                    "check": r'''
const tau = 1 / (2 * Math.PI * c.corner(0.01, 1e5));
const Vs = c.values('V')[0];
return 1000 * tau * Math.log(Vs / (Vs - 7.5));
''',
                    "answer": 18.53,
                    "tol": 0.06,
                    "unit": "ms",
                    "hint": r"$\tau = RC$ in seconds first — or use kilohms times microfarads for milliseconds directly. Then the ratio is $V_s$ over what is *left*, which is $9.00 - 7.50 = 1.50$ V.",
                    "wrong": r"If you got 1.885 ms, the ratio was $9/7.5$ instead of $9/1.5$ — the voltage reached rather than the voltage still to go, and it is the error this question exists for. If you got 8.05 ms, $\log_{10}$ was used where $\ln$ was needed, a factor of 2.3026. If you got 10.3 ms, that is one time constant, which only takes the capacitor to 5.69 V. If you got 8.62 ms, the charge was treated as a straight ramp and scaled by $7.5/9$.",
                    "why": r'''
```
tau = R C = 4.70e4 * 2.20e-7 = 1.034e-2 s = 10.34 ms
     (or, with no exponents: 47 kohm * 0.22 uF = 10.34 ms)

still to go = Vs - v = 9.00 - 7.50 = 1.50 V

t = tau * ln(9.00 / 1.50) = 10.34 ms * ln 6
  = 10.34 ms * 1.7917595 = 18.527 ms
```

Check it forwards, which is always the safer direction. At $t = 18.527$ ms the exponent is
$t/\tau = 1.79176$, and $e^{-1.79176} = 0.166667$ — exactly one sixth, because
$\ln 6 = 1.79176$ was constructed to make it so. The capacitor has therefore covered
$1 - 1/6 = 5/6$ of the way, and $9.00 \times 5/6 = 7.50$ V. It lands on the number asked
for, so the rearrangement was done correctly.

Two bearings on the answer. One time constant, 10.34 ms, gets you to
$9(1 - e^{-1}) = 5.689$ V, so 7.50 V must come later — and 18.53 ms is 1.79 time
constants. Five time constants, 51.7 ms, gets you to 8.94 V, so 7.50 V must come well
before that. The answer sits sensibly between the two landmarks.

And the shape of the formula is worth keeping. Each further factor of ten in the remaining
gap costs another $\tau\ln 10 = 2.303\tau = 23.8$ ms, no matter where you start: from 7.50
V the capacitor reaches 8.85 V at 42.3 ms and 8.985 V at 66.1 ms, equal steps in time for
equal *factors* in what is left. That is the signature of an exponential, and it is why
the answers come out of a logarithm rather than out of a proportion.
''',
                    "aside": "The check on this question does not use $R$ and $C$ at all. It measures the circuit's own $-3$ dB corner, 15.392 Hz, and takes $\\tau = 1/(2\\pi f_c) = 10.340$ ms from it. Time constant and corner frequency are the same fact in two languages, and the agreement to five figures is the solver confirming it.",
                },
                {
                    "title": "A slope, measured rather than assumed",
                    "minutes": 12,
                    "brief": r'''
Two RC sections, wired straight together with nothing between them. Each on its own would
roll off at 20 dB per decade, so the pair "should" give 40 — and the question is what it
actually gives, one decade of real measurement at a time.

Two warnings before you start. First, the second section **loads** the first: the current
that leaves C1's node through R2 is current that never charged C1, so you cannot multiply
two independent divider responses together. Write the two node equations of module 4 and
solve them at once. Second, the quantity asked for is not a voltage. It is a *difference*
of two decibel figures, which is a ratio of two gains, and it is what an instrument means
when it reports a slope.
''',
                    "prompt": r"By how many decibels does the output fall between 10.0 kHz and 100 kHz?",
                    "note": "Answer in decibels as a signed number, to two decimal places. A response that falls has a negative change.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 10000},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "r2", "kind": "R", "x": 12, "y": 4, "rot": 0, "value": 10000},
                            {"id": "c2", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 15, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 4], "b": [11, 4]},
                            {"a": [13, 4], "b": [15, 4]},
                            {"a": [15, 4], "b": [15, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [15, 7], "b": [15, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V sinusoid"},
                        {"label": "R1, R2", "value": "10.0 kΩ each"},
                        {"label": "C1, C2", "value": "10.0 nF each"},
                        {"label": "Asked for", "value": "the change in output, in dB, from 10.0 kHz to 100 kHz"},
                    ],
                    # A slope is no node of the circuit, so it is taken as the ratio of two AC
                    # magnitudes. The source amplitude cancels out of the ratio, which is why
                    # nothing but the two frequencies appears here.
                    "check": r'''
return 20 * Math.log10(c.gain(1e5) / c.gain(1e4));
''',
                    "answer": -39.30,
                    "tol": 0.12,
                    "unit": "dB",
                    "hint": r"Write $x = \omega RC$ and the loaded pair has $|G| = 1/\sqrt{(1 - x^2)^2 + 9x^2}$. Evaluate at both frequencies, convert each to decibels, and subtract. The 9 is where the loading lives — two independent sections would give a 4 there.",
                    "wrong": r"If you got exactly $-40.00$, that is the asymptote both corners head for, and neither reading is far enough out to have reached it. If you got $-39.78$, the two sections were treated as independent and multiplied together, which ignores the loading. If you got $-19.90$, only one section was counted. If you got $-39.30$ with the sign the other way, the two frequencies were subtracted in the other order — the output falls, so the change is negative.",
                    "why": r'''
The two node equations, with $s = j\omega$ and both sections identical. Call the middle
node $v_A$ and the output $v_B$.

```
at B:  (vB - vA)/R + vB sC = 0            ->  vA = vB (1 + sRC)
at A:  (vA - vin)/R + vA sC + (vA - vB)/R = 0
       vin = vA (2 + sRC) - vB
           = vB (1 + sRC)(2 + sRC) - vB
           = vB [ 1 + 3 sRC + (sRC)^2 ]
```

So the loaded pair is

$$G = \frac{1}{1 + 3sRC + (sRC)^2}, \qquad
|G| = \frac{1}{\sqrt{(1-x^2)^2 + 9x^2}}, \qquad x = \omega RC$$

and the **3** in the middle is the loading. Two buffered sections would have given a 2
there, and $(1 + sRC)^2$ instead.

With $RC = 10^4 \times 10^{-8} = 1.00\times10^{-4}$ s:

```
f = 10.0 kHz:  x = 2 pi * 1e4 * 1e-4 = 6.283185
               x^2 = 39.47842      (1 - x^2) = -38.47842
               (1-x^2)^2 = 1480.589      9x^2 = 355.3058
               sum = 1835.894      sqrt = 42.84734
               |G| = 0.02333867    dB = -32.638

f = 100 kHz:   x = 62.83185
               x^2 = 3947.842     (1 - x^2) = -3946.842
               (1-x^2)^2 = 1.557756e7    9x^2 = 35530.58
               sum = 1.561309e7   sqrt = 3951.340
               |G| = 2.530787e-4  dB = -71.935

fall = -71.935 - (-32.638) = -39.296 dB
```

Just under 39.3 dB, where the rule of thumb says 40. Both corners are already behind: the
denominator factorises into poles at 607.9 Hz and 4166.7 Hz, so at 10 kHz the upper one is
only 2.4 times below the measurement and has not finished bending into its asymptote. Take
the next decade instead, 100 kHz to 1 MHz, and the fall is 39.99 dB. Same circuit, same
rule, and the rule is only true where it claims to be.

The loading is worth one more line, because it is the reason the two sections cannot be
handled separately. Buffered, the pair would fall 39.78 dB over the same decade — close to
the measured 39.30 in *slope*, but the two circuits differ by 0.49 dB at 10 kHz and their
corner frequencies are not the same at all: the loaded ladder's poles are 607.9 Hz and
4166.7 Hz, while the buffered pair has both at 1591.5 Hz. Slopes far out are forgiving;
everything near the corner is not.
''',
                    "aside": "The $-3$ dB point of this ladder measures 595.6 Hz, close to but not equal to the lower pole at 607.9 Hz — the upper pole is still contributing a little attenuation down there. Two buffered sections of the same values would be $-3$ dB at $1591.5\\sqrt{\\sqrt{2}-1} = 1024$ Hz. Cascading always narrows the band, and loading narrows it further.",
                },
            ],
            "lab": {
                "title": "Decibels, and a slope measured from data",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Two small conversions and one measurement.

The conversions are the two decibel rules. `db_amplitude(ratio)` returns
$20\log_{10}$ of the ratio and `db_power(ratio)` returns $10\log_{10}$ of it; both must
refuse a ratio that is zero or negative, because no such logarithm exists — raise
`ValueError`. `from_db_amplitude(db)` goes back the other way.

The measurement is the one an instrument makes for you and you should be able to
make yourself. `slope_per_decade(freqs, dbs)` is handed a frequency sweep and the
response in decibels at each frequency, and returns the slope in **decibels per
decade**. A slope per decade is a slope against $\log_{10}f$, so fit a straight line
to `dbs` against `log10(freqs)` by least squares:

$$\text{slope} = \frac{\sum (x_k - \bar{x})(y_k - \bar{y})}{\sum (x_k - \bar{x})^2},
\qquad x_k = \log_{10}f_k, \quad y_k = \text{dbs}_k$$

Fitting rather than taking the two end points is the point: real sweeps have noise in
them, and every point should get a vote.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def db_amplitude(ratio):
    """20*log10(ratio). Raise ValueError unless the ratio is positive."""
    # TODO
    return 0.0


def db_power(ratio):
    """10*log10(ratio). Raise ValueError unless the ratio is positive."""
    # TODO
    return 0.0


def from_db_amplitude(db):
    """The amplitude ratio that this many decibels describes."""
    # TODO
    return 0.0


def slope_per_decade(freqs, dbs):
    """Least-squares slope of dbs against log10(freqs), in dB per decade."""
    # TODO
    return 0.0


if __name__ == "__main__":
    print("x10 in amplitude :", db_amplitude(10.0), "dB")
    print("x2  in power     :", round(db_power(2.0), 4), "dB")
    print("-3 dB is a ratio of", round(from_db_amplitude(-3.0103), 6))
    fc = 100.0
    fs = [10.0 ** (3.0 + k / 20.0 * 2.0) for k in range(21)]
    mags = [db_amplitude(1.0 / math.sqrt(1.0 + (f / fc) ** 2)) for f in fs]
    print("measured slope   :", round(slope_per_decade(fs, mags), 3), "dB/decade")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def db_amplitude(ratio):
    """20*log10(ratio). Raise ValueError unless the ratio is positive."""
    if ratio <= 0.0:
        raise ValueError("a decibel figure needs a positive ratio")
    return 20.0 * math.log10(ratio)


def db_power(ratio):
    """10*log10(ratio). Raise ValueError unless the ratio is positive."""
    if ratio <= 0.0:
        raise ValueError("a decibel figure needs a positive ratio")
    return 10.0 * math.log10(ratio)


def from_db_amplitude(db):
    """The amplitude ratio that this many decibels describes."""
    return 10.0 ** (db / 20.0)


def slope_per_decade(freqs, dbs):
    """Least-squares slope of dbs against log10(freqs), in dB per decade."""
    xs = [math.log10(f) for f in freqs]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(dbs) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, dbs))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den


if __name__ == "__main__":
    print("x10 in amplitude :", db_amplitude(10.0), "dB")
    print("x2  in power     :", round(db_power(2.0), 4), "dB")
    print("-3 dB is a ratio of", round(from_db_amplitude(-3.0103), 6))
    fc = 100.0
    fs = [10.0 ** (3.0 + k / 20.0 * 2.0) for k in range(21)]
    mags = [db_amplitude(1.0 / math.sqrt(1.0 + (f / fc) ** 2)) for f in fs]
    print("measured slope   :", round(slope_per_decade(fs, mags), 3), "dB/decade")
'''}],
                "hints": [
                    r"`math.log10` is the base-ten logarithm and `math.log` is the natural one. Using the wrong one scales every answer by 2.303, which is close enough to look plausible and far enough to be wrong.",
                    r"Check the sign of the test before computing: `if ratio <= 0.0: raise ValueError(...)`. Doing it afterwards means `math.log10` has already raised its own less helpful error.",
                    r"For the fit, build the list of $x_k = \log_{10}f_k$ first, then the two means, then the two sums. Written that way it is five short lines and no bookkeeping.",
                    r"If your slope comes out around $-8.7$ instead of $-20$, you fitted against $\ln f$ rather than $\log_{10}f$.",
                ],
                "tests": [
                    {"name": "the amplitude landmarks are where they should be", "code": r'''
assert abs(db_amplitude(1.0)) < 1e-12, "a ratio of one is 0 dB"
assert abs(db_amplitude(10.0) - 20.0) < 1e-9, f"x10 in amplitude is exactly 20 dB, got {db_amplitude(10.0)}"
assert abs(db_amplitude(2.0) - 6.020599913279624) < 1e-9, f"x2 in amplitude is 6.02 dB, got {db_amplitude(2.0)}"
import math
assert abs(db_amplitude(1.0 / math.sqrt(2.0)) - (-3.0102999566398125)) < 1e-9, \
    "the half-power point is -3.01 dB"
'''},
                    {"name": "power uses ten, not twenty", "code": r'''
assert abs(db_power(2.0) - 3.010299956639812) < 1e-9, f"x2 in power is 3.01 dB, got {db_power(2.0)}"
assert abs(db_power(10.0) - 10.0) < 1e-9, f"x10 in power is 10 dB, got {db_power(10.0)}"
assert abs(db_power(9.0) - db_amplitude(3.0)) < 1e-9, \
    "tripling an amplitude multiplies the power by nine, so the two figures must agree"
'''},
                    {"name": "a ratio that is not positive has no decibel value", "code": r'''
for _bad in (0.0, -2.0):
    for _fn in (db_amplitude, db_power):
        try:
            _fn(_bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{_fn.__name__}({_bad}) should raise ValueError")
'''},
                    {"name": "decibels add where gains multiply", "code": r'''
_a, _b = 10.0, 5.0
assert abs(db_amplitude(_a * _b) - 33.979400086720375) < 1e-9, \
    f"a gain of 50 is 33.98 dB, got {db_amplitude(_a * _b)}"
assert abs(db_amplitude(_a * _b) - (db_amplitude(_a) + db_amplitude(_b))) < 1e-9, \
    "20 dB followed by 13.98 dB must come to the same as a single gain of 50"
'''},
                    {"name": "the conversion goes both ways", "code": r'''
for _r in (0.001, 0.5, 1.0, 7.3, 1000.0):
    assert abs(from_db_amplitude(db_amplitude(_r)) - _r) < 1e-9 * max(1.0, _r), \
        f"the round trip lost {_r}"
assert abs(from_db_amplitude(-20.0) - 0.1) < 1e-12, "-20 dB is a tenth"
'''},
                    {"name": "a first-order roll-off measures 20 dB per decade", "code": r'''
import math
_fc = 100.0
_fs = [10.0 ** (3.0 + _k / 20.0 * 2.0) for _k in range(21)]
_db = [20.0 * math.log10(1.0 / math.sqrt(1.0 + (_f / _fc) ** 2)) for _f in _fs]
_s = slope_per_decade(_fs, _db)
assert -20.1 < _s < -19.9, f"expected about -20 dB/decade well above the corner, got {_s}"
'''},
                    {"name": "two corners double the slope", "code": r'''
import math
_wn, _zeta = 100.0, 1.5
_fs = [10.0 ** (3.0 + _k / 20.0 * 2.0) for _k in range(21)]
_db = []
for _f in _fs:
    _x = _f / _wn
    _db.append(20.0 * math.log10(1.0 / math.hypot(1.0 - _x * _x, 2.0 * _zeta * _x)))
_s = slope_per_decade(_fs, _db)
assert -40.2 < _s < -39.6, f"two first-order corners give about -40 dB/decade, got {_s}"
'''},
                    {"name": "the fit is a fit, not two end points", "code": r'''
_fs = [10.0, 100.0, 1000.0]
_db = [0.0, -20.0, -40.0]
assert abs(slope_per_decade(_fs, _db) - (-20.0)) < 1e-9, "a clean line must come back exactly"
_db_noisy = [1.0, -20.0, -41.0]
_s = slope_per_decade(_fs, _db_noisy)
assert abs(_s - (-21.0)) < 1e-9, \
    f"least squares on this data gives exactly -21; got {_s} — check the two means"
'''},
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Second-order equations: the quadratic that decides everything",
            "summary": "Two energy stores make a second derivative, a quadratic, and three responses that look nothing alike but are the same equation with a different discriminant.",
            "concepts": [
                r"One resistor and one energy store gave a first-order equation. A capacitor **and** an inductor give a second derivative: a series $R$, $L$, $C$ driven by $V_s$, with the output taken across the capacitor, obeys $LC\ddot{v} + RC\dot{v} + v = V_s$.",
                r"Substituting $v = Ae^{st}$ turns each derivative into a multiplication by $s$ — the only property of the exponential being used — and the common factor $Ae^{st}$ divides out. What is left is the **characteristic equation** $LCs^2 + RCs + 1 = 0$: a problem in calculus has become a quadratic.",
                r"Divided through by $LC$ and matched against the standard form $s^2 + 2\zeta\omega_n s + \omega_n^2 = 0$, the **natural frequency** is $\omega_n = 1/\sqrt{LC}$ in radians per second and the **damping ratio** is $\zeta = \frac{R}{2}\sqrt{C/L}$, a pure number carrying no units at all.",
                r"The roots are $s = \omega_n\left(-\zeta \pm \sqrt{\zeta^2-1}\right)$, and the discriminant decides their character. $\zeta > 1$: two real roots, no overshoot, **overdamped**. $\zeta = 1$: a repeated root, **critically damped**, the fastest arrival with no overshoot. $\zeta < 1$: a complex pair $-\zeta\omega_n \pm j\omega_d$ with $\omega_d = \omega_n\sqrt{1-\zeta^2}$, **underdamped** — module 2's rotation multiplied by a decay.",
                r"$\zeta < 1$ is the same statement as $R^2 < 4L/C$. Whether a circuit rings is settled by the resistance compared against $\sqrt{L/C}$, and by nothing else.",
                r"Driven by a sinusoid rather than a step, the same circuit peaks near $\omega_n$ whenever $\zeta < 1/\sqrt{2}$, reaching $1/\left(2\zeta\sqrt{1-\zeta^2}\right)$ times its low-frequency size. Above $\zeta = 1/\sqrt{2} \approx 0.707$ there is no peak at all.",
                r"The two numbers are set separately: $\omega_n$ by the product $LC$, $\zeta$ by $R$ against $\sqrt{L/C}$. Changing $R$ alone moves the damping and leaves the frequency exactly where it was — which is why $R$ is the knob a designer reaches for.",
            ],
            "read": [
                {
                    "title": "Two energy stores in one loop",
                    "minutes": 18,
                    "body": r'''
A resistor has nothing to remember. Put 5 V across it and the current is there at once;
take the 5 V away and the current is gone at once. Nothing that happened a microsecond ago
survives anywhere inside it, which is why a circuit made only of resistors is solved with
algebra and never with calculus. There is no state to carry forward.

An energy store is the opposite kind of object. A capacitor holds energy in the electric
field between its plates, and the size of that field is what we call its voltage; to change
the voltage you have to move charge onto or off the plates, and moving charge takes current
and takes time. That is the whole content of

$$i = C\frac{dv}{dt}$$

An inductor holds energy in the magnetic field around its winding, and the size of that
field is what we call its current; to change the current you have to push against the
induced voltage, which again takes time:

$$v = L\frac{di}{dt}$$

Read those two laws as refusals and they are easier to keep straight. **A capacitor refuses
a jump in voltage. An inductor refuses a jump in current.** A jump would need infinite
current in the first case and infinite voltage in the second, and the circuit has neither
to give.

## Why two stores is not just more of the same

Module 4 put one store in a loop with a resistor. One state variable, one first-order
equation, one exponential, one time constant, and a response that goes one way and stops.
Nothing in that circuit can overshoot, because there is only one quantity being remembered
and it is being driven straight at its final value.

Now put a capacitor **and** an inductor in the same loop, in series with a resistor, and
connect a supply. Follow what has to happen. The supply pushes current through the
inductor into the capacitor, and the capacitor's voltage climbs. It reaches the supply
voltage. At that instant the net voltage driving the loop is zero, so the current has
stopped *growing* — but it has not stopped. It cannot: the inductor refuses a jump in
current, and there is a substantial current flowing. That current has nowhere to go except
into the capacitor, so the capacitor keeps charging, past the supply voltage.

Now the capacitor is at a higher voltage than the supply. The voltage across the inductor
has reversed, so the current is being braked, and eventually it reaches zero and reverses.
The energy stored in the magnetic field has been handed to the electric field, and now it
starts coming back. The two stores trade. The resistor, meanwhile, is the only part of the
loop that can lose any of it, and it takes a share on every pass.

That sloshing is the physical fact this whole module is about, and every formula below is
bookkeeping for it. A single store has one number to remember; two stores have two, and two
numbers that can trade can oscillate.

If the mechanics helps, the correspondence is exact rather than poetic. A mass on a spring
with a dashpot obeys the same equation: the mass, which resists a change in velocity, is
the inductor; the spring, which stores energy in displacement, is the capacitor; the
dashpot, which converts motion to heat and never gives it back, is the resistor. Velocity
is current, force is voltage. Everything derived here is also true of a car suspension,
which is why suspensions are described as underdamped or overdamped in the same words.

## Getting the equation

Take the series loop: supply $V_s$, then $L$, then $R$, then $C$, with the output taken
across the capacitor. One current $i$ flows through all four, because there is nowhere for
it to branch. Kirchhoff's voltage law round the loop says the three component voltages add
up to the supply:

$$L\frac{di}{dt} + Ri + v = V_s$$

There are two unknowns in that, $i$ and $v$, so it is not yet solvable. But the current in
the loop is the current *into the capacitor*, and the capacitor law relates them:
$i = C\,dv/dt$. Substituting, and using $di/dt = C\,d^2v/dt^2$:

$$LC\frac{d^2v}{dt^2} + RC\frac{dv}{dt} + v = V_s$$

which is usually written $LC\ddot{v} + RC\dot{v} + v = V_s$. The second derivative is not a
mathematical flourish; it arrived because the inductor's law differentiates a current which
was already itself the derivative of the capacitor's voltage. Two stores in a chain, two
differentiations.

## The exponential is the only function that fits

To find what the circuit does *on its own* — the part of the response that is the circuit's
own character rather than the supply's — set $V_s = 0$ and look for a function that can
satisfy

$$LC\ddot{v} + RC\dot{v} + v = 0$$

A sum of a function, its derivative and its second derivative can only cancel to nothing if
all three have the same shape. That is a strong requirement, and exactly one family of
functions meets it: $v = Ae^{st}$, whose derivative is $sAe^{st}$ and whose second
derivative is $s^2Ae^{st}$ — the same function each time, only rescaled. Nothing else will
do, and this is the sole property of the exponential being used.

Substitute it:

$$LCs^2Ae^{st} + RCsAe^{st} + Ae^{st} = 0$$

$Ae^{st}$ is a common factor, and an exponential is never zero, so it divides out and takes
the calculus with it:

$$LCs^2 + RCs + 1 = 0$$

That is the **characteristic equation**, and the trade just made is the most valuable one in
the subject: a differential equation has become a quadratic. Everything from here is
school algebra.

## Two numbers instead of three components

Divide through by $LC$ so the leading coefficient is 1:

$$s^2 + \frac{R}{L}s + \frac{1}{LC} = 0$$

and set it beside the form that every second-order system in engineering is written in:

$$s^2 + 2\zeta\omega_n s + \omega_n^2 = 0$$

Matching the constant terms gives $\omega_n^2 = 1/(LC)$, so

$$\omega_n = \frac{1}{\sqrt{LC}}$$

and matching the coefficients of $s$ gives $2\zeta\omega_n = R/L$, so
$\zeta = R/(2L\omega_n)$. Dividing by $\omega_n$ is multiplying by $\sqrt{LC}$, and
$\sqrt{LC}/L = \sqrt{C/L}$, which leaves

$$\zeta = \frac{R}{2}\sqrt{\frac{C}{L}}$$

$\omega_n$ is the **natural frequency**, in radians per second. $\zeta$ is the **damping
ratio**, and it has no units at all — check it if you like: $R$ is in ohms and
$\sqrt{L/C}$ is also in ohms, so their ratio is a bare number.

That last fact is worth a line of its own, because it is what $\zeta$ actually *means*.
Write the damping ratio as

$$\zeta = \frac{R}{2Z_0} \qquad\text{with}\qquad Z_0 = \sqrt{\frac{L}{C}}$$

$Z_0$ is in ohms and is built from the two energy stores alone; it is called the
characteristic impedance of the pair. Damping is not "how much resistance there is". It is
**how the resistance compares with $Z_0$**. A 50 Ω resistor is heavy damping in a circuit
whose $Z_0$ is 10 Ω and almost none at all in one whose $Z_0$ is 1000 Ω.

Solving the quadratic gives the two roots, and it is convenient to factor $\omega_n$ out:

$$s = \omega_n\left(-\zeta \pm \sqrt{\zeta^2 - 1}\right)$$

The discriminant $\zeta^2 - 1$ decides everything. Above $\zeta = 1$ it is positive and the
roots are two real negative numbers: two decaying exponentials, no oscillation,
**overdamped**. At $\zeta = 1$ the roots meet, **critically damped**. Below $\zeta = 1$ the
square root is imaginary and the roots are a complex conjugate pair, which by module 2 means
a rotation multiplied by a decay: **underdamped**, and the circuit rings.

## Worked: reading a circuit

A series circuit with $L = 100$ mH, $C = 100$ nF and $R = 220\,\Omega$.

```
LC        = 0.100 * 100e-9   = 1.00e-8 s^2
sqrt(LC)  = 1.00e-4 s
wn        = 1 / 1.00e-4      = 10 000 rad/s
fn        = 10 000 / (2 pi)  = 1591.5 Hz

L/C       = 0.100 / 100e-9   = 1.00e6 ohm^2
Z0        = sqrt(L/C)        = 1000 ohm
zeta      = R / (2 Z0) = 220 / 2000 = 0.110
```

$\zeta = 0.110$ is well below 1, so this rings. Put numbers on the ringing:

```
sigma = zeta * wn = 0.110 * 10 000 = 1100 /s
wd    = wn sqrt(1 - zeta^2) = 10 000 * sqrt(1 - 0.0121)
      = 10 000 * 0.993932 = 9939.3 rad/s
roots = -1100 +/- j 9939.3
```

The ringing period is $2\pi/\omega_d = 6.2832/9939.3 = 6.322\times10^{-4}$ s, or 632 µs. The
amplitude of the ring falls by a factor $e$ every $1/\sigma = 1/1100 = 909$ µs. Dividing,
the ring loses a factor of $e$ every 1.44 cycles, and reaching a hundredth of its starting
size takes $\ln(100) \times 909$ µs, or 4.19 ms — about six and a half visible cycles on
a scope.

Notice how close $\omega_d$ is to $\omega_n$: 9939 against 10 000, a difference of 0.6%. At
light damping the frequency you would *count* on the screen and the $\omega_n$ you compute
from $L$ and $C$ are the same number for any practical purpose. They separate only when
$\zeta$ gets large, and by then there is nothing left to count.

## Worked: choosing the resistor

Now the design direction. $L = 20$ mH and $C = 2$ µF are fixed; the question is what $R$
to fit.

```
LC   = 0.020 * 2.00e-6 = 4.00e-8 s^2
wn   = 1 / 2.00e-4     = 5000 rad/s      fn = 795.77 Hz
L/C  = 0.020 / 2.00e-6 = 1.00e4 ohm^2
Z0   = 100 ohm
```

$\omega_n$ contains no $R$, so no choice made below moves it. Only $\zeta = R/200$ moves.

```
R =  33 ohm  ->  zeta = 0.165   rings hard
R = 100 ohm  ->  zeta = 0.500   one visible overshoot
R = 200 ohm  ->  zeta = 1.000   critical, no overshoot at all
R = 500 ohm  ->  zeta = 2.500   overdamped
```

The overdamped case is the one worth working out, because it is the one people mispredict.
With $\zeta = 2.5$:

```
zeta^2 - 1     = 5.25          sqrt = 2.291288
s = 5000 * (-2.5 +/- 2.291288)
s1 = 5000 * (-0.208712) = -1043.6 /s   ->  tau1 = 958 us
s2 = 5000 * (-4.791288) = -23956  /s   ->  tau2 =  41.7 us
```

Two exponentials, one fast and one slow, and the slow one is what you actually see. Compare
it against critical damping, where both roots sit at $-\omega_n = -5000$ and the time
constant is 200 µs. Piling on resistance made the circuit **almost five times slower**. It
did not damp the circuit into submission; it made one of the two exponentials lazy. As
$R \to \infty$ the slow root creeps towards the origin like $-1/(RC)$ and the circuit
degenerates into the plain $RC$ charge of module 4, with the inductor doing nothing.

## The two mistakes

**Radians against hertz.** $\omega_n = 1/\sqrt{LC}$ has no $2\pi$ anywhere in it, and every
other formula in this module — $\zeta$, the roots, $\omega_d$ — is written in $\omega$ as
well. So the $2\pi$ is due exactly once, at the very last step, converting to a frequency
you could measure, and by then you have been working happily in radians for ten minutes and
have stopped thinking about it. The circuit above has $\omega_n = 10\,000$ rad/s and
$f_n = 1591.5$ Hz; those are the same physical fact, and quoting one when the question asked
for the other is the single commonest error in this material. Read the units of the answer
before you write it down.

**"More resistance means more ringing."** Resistance feels like the active ingredient,
because it is the component whose value you usually choose. But $R$ is the only part of the
loop that *removes* energy — $L$ and $C$ only pass it back and forth, neither of them
consuming anything. Ringing is not something the resistor causes; it is what happens when
the resistor is too small to stop it. Every formula agrees: $\zeta$ is proportional to $R$,
and the circuit rings when $\zeta < 1$, which is $R < 2\sqrt{L/C}$.

## Where this stops holding

**It needs exactly two independent energy stores.** Add a third that is not simply in
parallel with one of the others — a second capacitor further down the chain, say — and the
characteristic equation is a cubic. It has three roots, and no pair $(\omega_n, \zeta)$
describes it. What engineers do then is find the two roots nearest the origin, call them the
dominant pair, and use $\omega_n$ and $\zeta$ as an approximation whose error you have to
estimate separately. That is a different skill and it is honest about being an
approximation.

**It needs the components to be ideal.** A real inductor is a long piece of wire, and that
wire has resistance in series with the inductance. It adds to $R$ and it is frequently the
dominant damping in a design where you deliberately chose a small $R$. Build the 20 mH,
2 µF circuit above with a 200 Ω resistor expecting $\zeta$ to be exactly 1 and, if the coil
carries 30 Ω of winding resistance, you will measure $\zeta = 230/200 = 1.15$ instead. A
real capacitor likewise has a small series resistance of its own. Neither is a defect in the
theory; they are components you forgot to put in the model.

**It needs linearity.** An inductor wound on a ferrite core has a roughly constant $L$ only
while the core is unsaturated. Drive it hard enough and $L$ falls, which raises $\omega_n$
and — since $\zeta \propto \sqrt{C/L}$ — *lowers* $\zeta$, so the circuit rings harder the
harder you drive it. Nothing in this module predicts that, and no choice of $\omega_n$ and
$\zeta$ can describe a circuit whose behaviour depends on the size of the signal.

**It needs the circuit to be small.** Everything here treats a wire as a point at one
voltage. Once the physical loop approaches a tenth of a wavelength at the frequencies
involved, that stops being true, and the loop starts behaving like an antenna and a
transmission line rather than three lumped components.

Within those limits, two numbers now stand in for three components, and any $R$, $L$, $C$
sharing an $\omega_n$ and a $\zeta$ behave identically. The next reading unit takes those
two numbers as given and works out what they predict.
''',
                },
                {
                    "title": "What the damping ratio predicts",
                    "minutes": 19,
                    "body": r'''
The previous unit turned three components into two numbers. This one spends them. Given
$\omega_n$ and $\zeta$, what does the circuit actually do — first when you hit it with a
step, and then when you drive it with a sinusoid and sweep the frequency? The two answers
look unrelated on a screen and come from the same quadratic.

## Three kinds of root, three shapes

The roots are $s = \omega_n(-\zeta \pm \sqrt{\zeta^2-1})$, and the natural response is built
from $e^{st}$ with each root in turn.

**Overdamped, $\zeta > 1$.** Two real negative roots, so the response is a sum of two
decaying exponentials, $Ae^{s_1t} + Be^{s_2t}$. A sum of decaying exponentials starting from
rest can approach its final value but never cross it, so there is no overshoot at all. The
root nearer the origin has the longer time constant and dominates everything after the first
instant.

**Critically damped, $\zeta = 1$.** The discriminant is zero and the two roots collide at
$s = -\omega_n$. That is a problem: a second-order equation needs two independent solutions
and there is now only one exponential. The missing one is $te^{-\omega_n t}$, and you can
see where it comes from by watching the two roots merge. Any multiple of
$(e^{s_1t} - e^{s_2t})/(s_1 - s_2)$ is a solution while the roots are distinct, and as
$s_2 \to s_1$ that expression is exactly the definition of the derivative of $e^{st}$ with
respect to $s$, which is $te^{st}$. So the response is $(A + Bt)e^{-\omega_n t}$ — a
straight line multiplied by a decay.

**Underdamped, $\zeta < 1$.** The square root is imaginary. Write $\sigma = \zeta\omega_n$
and $\omega_d = \omega_n\sqrt{1-\zeta^2}$; then the roots are $-\sigma \pm j\omega_d$ and

$$e^{(-\sigma + j\omega_d)t} = e^{-\sigma t}\left(\cos\omega_d t + j\sin\omega_d t\right)$$

by module 2's identity. A real voltage cannot be complex, and it does not have to be: the
two roots are conjugates, and combining their contributions with conjugate coefficients
cancels every imaginary part and leaves

$$e^{-\sigma t}\left(B\cos\omega_d t + D\sin\omega_d t\right)$$

A rotation multiplied by a decay. $\sigma$ sets how fast the envelope shrinks; $\omega_d$ —
the **damped** natural frequency, always a little below $\omega_n$ — sets the pitch.

## The step response, and how far it overshoots

Drive the circuit with a step of size $V_s$, starting from rest, and the underdamped
capacitor voltage works out to

$$v(t) = V_s\left[1 - \frac{e^{-\zeta\omega_n t}}{\sqrt{1-\zeta^2}}\sin(\omega_d t + \phi)\right]
\qquad \cos\phi = \zeta$$

The bracket contains a 1, which is where it ends up, minus a decaying sinusoid, which is the
transient. Differentiate and set to zero and the extrema fall at $t = k\pi/\omega_d$ — evenly
spaced at half a ringing period. Evaluating at those instants, the distance from the final
value at the $k$-th extremum is

$$\left|\frac{v - V_s}{V_s}\right| = M_p^{\,k} \qquad\text{where}\qquad
M_p = \exp\!\left(\frac{-\pi\zeta}{\sqrt{1-\zeta^2}}\right)$$

So the first peak overshoots by the fraction $M_p$, the first undershoot is $M_p^2$ below,
the second peak is $M_p^3$ above, and so on: a geometric sequence with ratio $M_p$. And
notice what is *not* in that formula. $\omega_n$ does not appear. **How far a second-order
circuit overshoots depends on $\zeta$ alone** — $\omega_n$ only sets how quickly the whole
picture plays out.

## Worked: a 2 V step into an underdamped circuit

$L = 100$ mH, $C = 10$ µF, $R = 50\,\Omega$, stepped from 0 to 2.00 V.

```
LC    = 0.100 * 1.00e-5 = 1.00e-6 s^2
wn    = 1 / 1.00e-3 = 1000 rad/s          fn = 159.15 Hz
Z0    = sqrt(0.100 / 1.00e-5) = sqrt(1.00e4) = 100 ohm
zeta  = R / (2 Z0) = 50 / 200 = 0.250

sigma = zeta wn = 250 /s
wd    = 1000 * sqrt(1 - 0.0625) = 1000 * 0.9682458 = 968.25 rad/s

t_p   = pi / wd = 3.141593 / 968.25 = 3.2446e-3 s = 3.244 ms
Mp    = exp(-pi * 0.250 / 0.9682458)
      = exp(-0.785398 / 0.9682458) = exp(-0.811158) = 0.44434
```

The first peak reaches $2.00 \times 1.44434 = 2.889$ V, at 3.24 ms. Read that twice: a 2.00 V
supply has put 2.89 V on the capacitor. No part of the circuit generates the extra 0.89 V —
it is the energy the inductor was carrying at the moment the capacitor reached 2 V, dumped
into the capacitor because the current had nowhere else to go. That is not a curiosity, it
is the reason a relay coil switched carelessly destroys the transistor next to it.

The rest of the sequence follows from the ratio:

```
1st peak      2.000 * (1 + 0.44434) = 2.889 V   at 3.24 ms
1st trough    2.000 * (1 - 0.19744) = 1.605 V   at 6.49 ms
2nd peak      2.000 * (1 + 0.08773) = 2.175 V   at 9.73 ms
```

with $0.44434^2 = 0.19744$ and $0.44434^3 = 0.08773$.

## Worked: which damping settles fastest

Take $L = 20$ mH and $C = 2$ µF again, so $\omega_n = 5000$ rad/s and $Z_0 = 100\,\Omega$,
and ask a question a designer actually asks: how long before the output is within 1% of its
final value and stays there?

```
R =  33 ohm   zeta = 0.165   settles in 5.27 ms
R = 200 ohm   zeta = 1.000   settles in 1.33 ms
R = 500 ohm   zeta = 2.500   settles in 4.46 ms
```

There is a minimum in the middle, and it is not an accident. Too little damping and the
circuit spends milliseconds ringing its way down inside the band; too much and the slow
root drags. Critical damping is the fastest arrival that never crosses the final value at
all, and that is the sentence worth remembering.

One honest wrinkle, since the numbers are in front of you. If you are willing to tolerate a
*little* overshoot, you can beat $\zeta = 1$ slightly: $\zeta = 0.9$ settles into the same
1% band in 1.03 ms, because its overshoot is only 0.15% — smaller than the band itself, so
the crossing costs nothing. This is why real designs sit near $\zeta = 0.7$ to $1.0$ rather
than exactly at 1: the settling penalty is small and the extra bandwidth is worth having.

## Now drive it with a sinusoid

Same circuit, different question. Instead of a step, apply $V_s\cos\omega t$ and let it run
until the transient has died, then ask how big the capacitor voltage is. Module 2 supplies
the shortcut: for a steady sinusoid, $d/dt$ becomes multiplication by $j\omega$. Applying
that to $LC\ddot{v} + RC\dot{v} + v = V_s$:

$$\left(-\omega^2LC + j\omega RC + 1\right)V = V_s
\qquad\Rightarrow\qquad
H(j\omega) = \frac{V}{V_s} = \frac{1}{1 - \omega^2LC + j\omega RC}$$

Write $u = \omega/\omega_n$ and use $\omega_n^2 = 1/(LC)$ and $RC = 2\zeta/\omega_n$ to get
the standard form, which contains no $L$, $C$ or $R$ at all:

$$H = \frac{1}{1 - u^2 + j2\zeta u}
\qquad\qquad
|H| = \frac{1}{\sqrt{(1-u^2)^2 + (2\zeta u)^2}}$$

$|H|$ is largest where the quantity under the root is smallest, so differentiate that with
respect to $u$ and set it to zero:

$$\frac{d}{du}\left[(1-u^2)^2 + 4\zeta^2u^2\right] = -4u(1-u^2) + 8\zeta^2u
= 4u\left(u^2 - 1 + 2\zeta^2\right) = 0$$

Two solutions: $u = 0$, and

$$u_r = \sqrt{1 - 2\zeta^2}$$

The second one only exists as a real number when $1 - 2\zeta^2 > 0$, that is when
$\zeta < 1/\sqrt{2} \approx 0.707$. Above that damping there is no interior peak: $u = 0$ is
the maximum and the response simply falls away from its low-frequency value. Below it, the
peak sits at $u_r$, and substituting $u_r$ back into $|H|$ gives its height:

$$|H|_{\max} = \frac{1}{2\zeta\sqrt{1-\zeta^2}}$$

## Worked: the peak of the same circuit

The $\zeta = 0.25$, $\omega_n = 1000$ rad/s circuit from before, driven with 2.00 V:

```
u_r = sqrt(1 - 2 * 0.0625) = sqrt(0.875) = 0.935414
f_r = 0.935414 * 159.155 = 148.88 Hz

|H|max = 1 / (2 * 0.250 * sqrt(1 - 0.0625))
       = 1 / (0.500 * 0.9682458) = 1 / 0.4841229 = 2.06559

peak output = 2.00 * 2.06559 = 4.131 V   at 148.88 Hz
```

and for comparison, at $\omega_n$ exactly, where $u = 1$ and the two reactances cancel:

```
|H| at u = 1  =  1 / (2 zeta)  =  1 / 0.500  =  2.000
output        =  4.000 V   at 159.15 Hz
```

Do the same for a more heavily damped version, $R = 100\,\Omega$ with $L = 20$ mH and
$C = 2$ µF, which is $\zeta = 0.500$ and $f_n = 795.77$ Hz:

```
u_r    = sqrt(1 - 0.500) = 0.707107   ->  f_r = 562.70 Hz
|H|max = 1 / (2 * 0.500 * sqrt(0.750)) = 1 / 0.866025 = 1.15470
|H| at u = 1 = 1 / (2 * 0.500) = 1.000
```

At $\zeta = 0.25$ the peak sits 6.5% below $f_n$ and is 3% higher than the value at $f_n$.
At $\zeta = 0.5$ it sits 29% below and is 15% higher. The gap between "the peak" and "the
value at $\omega_n$" opens up exactly as the damping rises, which is inconvenient, because
that is precisely the region where people reach for the approximation.

## The mistakes

**"The resonance is at $\omega_n$."** Three different frequencies live in this circuit and
all three get called the resonant frequency by somebody:

| symbol | value | what it is |
|---|---|---|
| $\omega_n$ | $1/\sqrt{LC}$ | where the reactances cancel; where the phase is exactly $-90°$ |
| $\omega_d$ | $\omega_n\sqrt{1-\zeta^2}$ | the frequency you would count watching it ring |
| $\omega_r$ | $\omega_n\sqrt{1-2\zeta^2}$ | where the driven response is biggest |

They obey $\omega_r < \omega_d < \omega_n$ whenever a peak exists at all. In the 100 mH,
100 nF, 220 Ω circuit of the previous unit, where $\zeta = 0.11$, the three come out as
1591.5, 1581.9 and 1572.2 Hz — a spread of 1.2%, and insisting on the distinction there is
pedantry. In the 20 mH, 2 µF circuit with $R = 100\,\Omega$, where $\zeta = 0.5$, they are
795.8, 689.2 and 562.7 Hz, and it is not pedantry at all.

**"The peak height is $1/(2\zeta)$."** That is the height *at* $\omega_n$, which is a
different place from the peak. The two agree when $\zeta$ is small and separate as it grows:
3% apart at $\zeta = 0.25$, 15% apart at $\zeta = 0.5$, and at $\zeta = 0.707$ the formula
$1/(2\zeta)$ confidently returns 0.707 for a response whose actual maximum is 1. The
approximation is tempting because $1/(2\zeta)$ is the quantity called $Q$, which appears
everywhere, and because at the light damping of a radio filter it really is exact enough.

## Where this stops holding

**It depends on where you probe.** $\omega_n$ and $\zeta$ are properties of the loop, but
the peaking formulas above are properties of the loop *and* the choice to measure across the
capacitor. Take the output across the resistor instead, from exactly the same three
components, and the transfer function becomes $2\zeta ju/(1 - u^2 + j2\zeta u)$: a
band-pass, whose maximum is at $u = 1$ exactly for every $\zeta$, and whose height there is
exactly 1 no matter how lightly damped the circuit is. Same roots, same $\omega_n$, same
$\zeta$, completely different picture. Nothing above applies to it.

**The parallel circuit inverts the resistance.** Put $R$, $L$ and $C$ all in parallel and
drive the combination with a current source. Kirchhoff's current law gives
$C\dot{v} + v/R + \frac{1}{L}\int v\,dt = I$; differentiate and divide by $C$:

$$\ddot{v} + \frac{1}{RC}\dot{v} + \frac{1}{LC}v = \frac{\dot{I}}{C}$$

The natural frequency is unchanged, $\omega_n = 1/\sqrt{LC}$, but now
$2\zeta\omega_n = 1/(RC)$, which gives

$$\zeta = \frac{1}{2R}\sqrt{\frac{L}{C}} = \frac{Z_0}{2R}$$

$R$ has moved to the bottom. In the parallel circuit a **larger** resistor rings more, and
the reason is not mysterious: in series the resistor is in the path the energy must take, so
a big one blocks the sloshing; in parallel the resistor is the escape route by which energy
leaves, and a big resistor is a poor escape route. The equation is the same, the algebra is
the same, and the knob turns the other way. Reaching for $\zeta = \frac{R}{2}\sqrt{C/L}$ on
a parallel circuit is the mistake this paragraph exists to prevent.

**Everything here is linear, and small.** The transfer function $|H|$ assumes the circuit
does the same thing to a 10 mV signal as to a 10 V one. A saturating inductor core or a
diode anywhere in the loop breaks that, and once it is broken the response depends on the
amplitude and no single pair $(\omega_n, \zeta)$ describes the circuit any more.
''',
                },
            ],
            "numeric": [
                {
                    "title": "The frequency the two stores set between them",
                    "minutes": 5,
                    "brief": r'''
The most mechanical question this module has: one rule, one unknown, and a resistor on the
schematic that plays no part in the answer.

$$\omega_n = \frac{1}{\sqrt{LC}}$$

That $\omega_n$ is in radians per second. The question asks for hertz, so there is a $2\pi$
waiting at the end — and $\omega_n = 1/\sqrt{LC}$ is the one formula in this module with no
$2\pi$ already inside it.

Work in base units. 100 mH is 0.100 H and 100 nF is $1.00\times10^{-7}$ F; a millihenry
left in as a whole number is off by a thousand and a nanofarad by a billion.
''',
                    "prompt": r"What is this circuit's natural frequency $\omega_n$, expressed in hertz?",
                    "note": "Answer in hertz, to one decimal place. The resistor is not needed.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "l1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.1},
                            {"id": "r1", "kind": "R", "x": 9, "y": 4, "rot": 0, "value": 220},
                            {"id": "c1", "kind": "C", "x": 12, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 12, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 12, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [8, 4]},
                            {"a": [10, 4], "b": [12, 4]},
                            {"a": [12, 4], "b": [12, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [12, 7], "b": [12, 9]},
                        ],
                    },
                    "given": [
                        {"label": "L1", "value": "100 mH"},
                        {"label": "R1", "value": "220 Ω"},
                        {"label": "C1, the probed node to ground", "value": "100 nF"},
                        {"label": "Asked for", "value": "$f_n = \\omega_n/2\\pi$, in hertz"},
                    ],
                    # No constant from the schematic is repeated here. omega_n is the frequency at
                    # which the capacitor voltage lags the source by exactly 90 degrees — the two
                    # reactances cancelling is the same statement — so the solver's own phase is
                    # bisected to find it, and the answer follows a redrawn schematic.
                    "check": r'''
let lo = 1, hi = 1e7;
for (let i = 0; i < 200; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
return Math.sqrt(lo * hi);
''',
                    "answer": 1591.5,
                    "tol": 2.0,
                    "unit": "Hz",
                    "hint": r"$LC = 0.100 \times 1.00\times10^{-7}$. Take the square root of that product, invert it for $\omega_n$ in rad/s, and divide by $2\pi$ last.",
                    "wrong": r"If you got 10 000, that is $\omega_n$ in radians per second and the question asked for hertz. If you got 15.9 million, the square root was never taken and $1/(LC) = 10^8$ was used as $\omega_n$. If you got 50.3, the inductance went in as 100 rather than 0.100 H. If you got 1581.9, that is $f_d$, the frequency the circuit would actually ring at — correct arithmetic, and the answer to a different question.",
                    "why": r'''
```
LC       = 0.100 H * 1.00e-7 F = 1.00e-8 s^2
sqrt(LC) = 1.00e-4 s
wn       = 1 / 1.00e-4 = 10 000 rad/s
fn       = 10 000 / 6.283185 = 1591.5 Hz
```

The resistor never appears, and that is the point of the standard form: $\omega_n$ depends
on $L$ and $C$ through their product alone. Change the 220 Ω to 1 Ω or to 1 kΩ and this
answer does not move by a hertz — what moves is $\zeta$, and with it how long the circuit
rings and how far it overshoots.

Worth checking the size by hand before believing it. $\sqrt{10^{-8}}$ is $10^{-4}$ because
the exponent halves; the reciprocal of $10^{-4}$ is $10^{4}$; and $10^4/2\pi$ is a bit over
1500. An answer of 15.9 kHz or 159 Hz would be a decade out and this check catches it.

The two frequencies to keep apart: $\omega_n = 10\,000$ rad/s and $f_n = 1591.5$ Hz are the
same physical fact in different units, and there is no third quantity hiding between them.
''',
                    "aside": "With $R = 220\\,\\Omega$ this circuit has $\\zeta = 0.11$, so it rings — and it rings at $\\omega_d = \\omega_n\\sqrt{1-\\zeta^2} = 9939$ rad/s, or 1581.9 Hz. That is 0.6% below $f_n$, which is why light damping lets people use the two words interchangeably and get away with it.",
                },
                {
                    "title": "How much damping does this resistor buy",
                    "minutes": 7,
                    "brief": r'''
Now all three components matter. The damping ratio is

$$\zeta = \frac{R}{2}\sqrt{\frac{C}{L}} = \frac{R}{2Z_0}
\qquad\text{with}\qquad Z_0 = \sqrt{\frac{L}{C}}$$

Two ways to compute the same thing, and the second is easier to check: work out $Z_0$ in
ohms first, then compare the resistor against it. If $Z_0$ comes out to something that is
not a sensible resistance — a millionth of an ohm, or a megohm — the exponents went in
wrong.

$\zeta$ is a pure number. If your answer has units, something has gone wrong upstream.
''',
                    "prompt": r"What is the damping ratio $\zeta$ of this circuit?",
                    "note": "Answer as a plain number, to three decimal places. It carries no units.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "l1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.02},
                            {"id": "r1", "kind": "R", "x": 9, "y": 4, "rot": 0, "value": 33},
                            {"id": "c1", "kind": "C", "x": 12, "y": 6, "rot": 1, "value": 2e-6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 12, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 12, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [8, 4]},
                            {"a": [10, 4], "b": [12, 4]},
                            {"a": [12, 4], "b": [12, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [12, 7], "b": [12, 9]},
                        ],
                    },
                    "given": [
                        {"label": "L1", "value": "20.0 mH"},
                        {"label": "R1", "value": "33.0 Ω"},
                        {"label": "C1", "value": "2.00 µF"},
                        {"label": "Asked for", "value": "the damping ratio ζ"},
                    ],
                    # zeta is measured rather than recomputed: at omega_n the capacitor voltage is
                    # 1/(2 zeta) times the drive, so the phase is bisected to locate omega_n and the
                    # solver's own magnitude there is inverted. No component value is restated.
                    "check": r'''
let lo = 1, hi = 1e7;
for (let i = 0; i < 200; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
const fn = Math.sqrt(lo * hi);
return c.values('V')[0] / (2 * c.gain(fn));
''',
                    "answer": 0.165,
                    "tol": 0.003,
                    "unit": "",
                    "hint": r"$L/C = 0.0200/2.00\times10^{-6}$ comes out to a round number of ohms squared. Take its square root to get $Z_0$, then $\zeta = R/(2Z_0)$.",
                    "wrong": r"If you got 1650, $\sqrt{L/C}$ was used where $\sqrt{C/L}$ belongs — the ratio is upside down, and the giveaway is a damping ratio in the thousands. If you got 0.330, the factor of 2 was dropped. If you got 165, the microfarads went in as a bare 2. If you got 1.65, $Z_0$ was taken as 10 rather than 100, which is one square root too many.",
                    "why": r'''
```
L/C   = 0.0200 / 2.00e-6 = 1.00e4 ohm^2
Z0    = sqrt(1.00e4)     = 100 ohm
zeta  = R / (2 Z0) = 33.0 / 200 = 0.165
```

Or in one line,
$\zeta = \frac{R}{2}\sqrt{C/L} = 16.5 \times \sqrt{1.00\times10^{-4}} = 16.5 \times 0.0100 = 0.165$
— the same arithmetic with the square root taken of the reciprocal instead.

$\zeta = 0.165$ is a long way below 1, so this circuit rings, and the formulas of the second
reading unit say how much. The first overshoot is
$\exp(-\pi \times 0.165/\sqrt{1-0.0272}) = \exp(-0.5254) = 0.591$, so a step drives the
capacitor 59% past its final value before it comes back. That is a circuit nobody would
ship as a power supply and exactly what you would want in a tuned radio stage.

The useful reading of the number is the comparison it hides. $Z_0 = 100\,\Omega$ is what this
$L$ and $C$ pair amount to as an impedance, and the resistor is a third of it. Damping is
always that comparison — never the resistance on its own. Put the same 33 Ω resistor with a
20 mH inductor and a 200 nF capacitor and $Z_0$ becomes 316 Ω, so $\zeta$ falls to 0.052 and
the same resistor now barely damps anything.
''',
                    "aside": "To make this circuit critically damped you would need $\\zeta = 1$, which is $R = 2Z_0 = 200\\,\\Omega$. Note how large that is compared with 33 Ω: getting from a hard ring to no overshoot at all takes a six-fold increase in resistance, not a nudge.",
                },
                {
                    "title": "The voltage the capacitor reaches that the supply never had",
                    "minutes": 9,
                    "brief": r'''
This circuit is driven by a sinusoid whose amplitude is fixed and whose frequency is swept
from very low to very high. Somewhere in the sweep the capacitor voltage is at its largest.
How large?

Three steps, and the middle one is the module's own result:

1. $\zeta$ from the components, as in the previous question.
2. The peak of $|H|$, which is $\dfrac{1}{2\zeta\sqrt{1-\zeta^2}}$ — not $1/(2\zeta)$, which
   is the height at $\omega_n$ and a slightly different place.
3. Multiply by the source amplitude, because $|H|$ is a ratio.

The frequency at which it happens is not asked for here, only the height.
''',
                    "prompt": r"Swept across all frequencies, what is the largest amplitude the capacitor voltage reaches?",
                    "note": "Answer in volts, to three decimal places. The source amplitude is on the schematic.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 2},
                            {"id": "l1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.1},
                            {"id": "r1", "kind": "R", "x": 9, "y": 4, "rot": 0, "value": 50},
                            {"id": "c1", "kind": "C", "x": 12, "y": 6, "rot": 1, "value": 1e-5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 12, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 12, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [8, 4]},
                            {"a": [10, 4], "b": [12, 4]},
                            {"a": [12, 4], "b": [12, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [12, 7], "b": [12, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "2.00 V sinusoid, frequency swept"},
                        {"label": "L1", "value": "100 mH"},
                        {"label": "R1", "value": "50.0 Ω"},
                        {"label": "C1", "value": "10.0 µF"},
                        {"label": "Asked for", "value": "the largest capacitor amplitude, in volts"},
                    ],
                    # The peak is found rather than asserted: a coarse logarithmic scan of the
                    # solver's own magnitude locates it, a golden-section search refines the
                    # bracket, and the magnitude at the refined frequency is returned.
                    "check": r'''
let bf = 1, best = 0;
for (let i = 0; i <= 3000; i++) {
  const f = Math.pow(10, i * 7 / 3000 - 1);
  const g = c.gain(f);
  if (g > best) { best = g; bf = f; }
}
let a = bf / 1.03, b = bf * 1.03;
for (let i = 0; i < 160; i++) {
  const m1 = a * Math.pow(b / a, 0.382), m2 = a * Math.pow(b / a, 0.618);
  if (c.gain(m1) > c.gain(m2)) b = m2; else a = m1;
}
return c.gain(Math.sqrt(a * b));
''',
                    "answer": 4.131,
                    "tol": 0.01,
                    "unit": "V",
                    "hint": r"$Z_0 = \sqrt{0.100/1.00\times10^{-5}}$ is a round 100 Ω, so $\zeta = 50/200$. Then the peak of $|H|$ is $1/(2\zeta\sqrt{1-\zeta^2})$, and the answer is that times 2.00 V.",
                    "wrong": r"If you got 4.000, the height at $\omega_n$ was used — $1/(2\zeta) = 2.000$ — which is the commonest slip here and is 3% low. If you got 2.066, the source amplitude was never applied; $|H|$ is a ratio, not a voltage. If you got 2.309, the factor of 2 in $\zeta$ was dropped, making $\zeta = 0.5$ and the peak 1.1547. If you got 2.000, the conclusion was that there is no peak — which would be right if $\zeta$ were above 0.707, and it is not.",
                    "why": r'''
```
Z0     = sqrt(0.100 / 1.00e-5) = sqrt(1.00e4) = 100 ohm
zeta   = 50.0 / (2 * 100) = 0.250

1 - zeta^2   = 0.937500
sqrt         = 0.9682458
2 zeta * that= 0.500 * 0.9682458 = 0.4841229
|H|max       = 1 / 0.4841229 = 2.065591

output       = 2.00 V * 2.065591 = 4.131 V
```

A 2.00 V source has produced 4.13 V across a capacitor, using three passive components and
nothing that could be called an amplifier. Where the energy comes from is not mysterious —
it is delivered by the source over many cycles and stored, because at this frequency the
inductor's and capacitor's reactances very nearly cancel and the only thing limiting the
loop current is the 50 Ω resistor. The current is therefore large, and a large current
through a capacitor's reactance is a large voltage. In a filter this is called peaking; in
a power converter it is called the reason the output capacitor failed.

Two things worth pinning down. First, why not $1/(2\zeta) = 2.000$? That is the height at
$\omega_n = 1000$ rad/s exactly, which is 159.15 Hz. The true maximum is at
$\omega_n\sqrt{1-2\zeta^2} = 935.4$ rad/s, or 148.88 Hz, and is 2.0656. The gap is small at
$\zeta = 0.25$ and grows fast: at $\zeta = 0.5$ it is 15%.

Second, why is there a maximum at all? Because $\zeta = 0.25$ is below $1/\sqrt{2}$. Raise
the resistor to 142 Ω and $\zeta$ passes 0.707, the interior peak vanishes, and the largest
output over the whole sweep becomes the 2.00 V the circuit passes at DC.
''',
                    "aside": "Hit the same circuit with a 2.00 V *step* instead of a swept sinusoid and the capacitor reaches $2.00 \\times (1 + e^{-\\pi\\zeta/\\sqrt{1-\\zeta^2}}) = 2.889$ V once, at 3.24 ms, and then settles. Driven at the right frequency it holds 4.13 V indefinitely. Same $\\zeta$, two different numbers, two different questions.",
                },
                {
                    "title": "Where the peak actually sits",
                    "minutes": 9,
                    "brief": r'''
Same three components as the damping-ratio question, with one change: the resistor has gone
from 33 Ω to 100 Ω. So $\omega_n$ has not moved at all — it never depends on $R$ — but the
damping has tripled, and this question is about what that does to the *frequency* at which
the response peaks.

$$\omega_r = \omega_n\sqrt{1 - 2\zeta^2}$$

Note the 2 under the root, which is what distinguishes this from $\omega_d$. Getting
$\zeta$ first is unavoidable; after that it is one substitution and a division by $2\pi$.

Before computing, predict the sign of the effect: is the peak above or below $f_n$?
''',
                    "prompt": r"At what frequency, in hertz, is the capacitor voltage largest?",
                    "note": "Answer in hertz, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "l1", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.02},
                            {"id": "r1", "kind": "R", "x": 9, "y": 4, "rot": 0, "value": 100},
                            {"id": "c1", "kind": "C", "x": 12, "y": 6, "rot": 1, "value": 2e-6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 12, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 12, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [8, 4]},
                            {"a": [10, 4], "b": [12, 4]},
                            {"a": [12, 4], "b": [12, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [12, 7], "b": [12, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V sinusoid, frequency swept"},
                        {"label": "L1", "value": "20.0 mH"},
                        {"label": "R1", "value": "100 Ω"},
                        {"label": "C1", "value": "2.00 µF"},
                        {"label": "Asked for", "value": "the frequency of the maximum, in hertz"},
                    ],
                    # Same measurement as the previous question, but the frequency is returned rather
                    # than the magnitude: coarse logarithmic scan for the bracket, golden-section
                    # search to refine it.
                    "check": r'''
let bf = 1, best = 0;
for (let i = 0; i <= 3000; i++) {
  const f = Math.pow(10, i * 7 / 3000 - 1);
  const g = c.gain(f);
  if (g > best) { best = g; bf = f; }
}
let a = bf / 1.03, b = bf * 1.03;
for (let i = 0; i < 160; i++) {
  const m1 = a * Math.pow(b / a, 0.382), m2 = a * Math.pow(b / a, 0.618);
  if (c.gain(m1) > c.gain(m2)) b = m2; else a = m1;
}
return Math.sqrt(a * b);
''',
                    "answer": 562.7,
                    "tol": 1.5,
                    "unit": "Hz",
                    "hint": r"$Z_0$ is still 100 Ω, so $\zeta = 100/200$. Then $1 - 2\zeta^2$ is a very round number, and $f_r = f_n\sqrt{1-2\zeta^2}$ with $f_n = 795.77$ Hz.",
                    "wrong": r"If you got 795.8, that is $f_n$ — the answer you get by assuming the peak sits at the natural frequency, and at this damping it is 41% too high. If you got 689.2, the root was $\sqrt{1-\zeta^2}$, giving $f_d$, the ringing frequency, which is a different quantity again. If you got 3536, that is $\omega_r$ in radians per second — the right quantity, still owed its division by $2\pi$.",
                    "why": r'''
```
Z0    = sqrt(0.0200 / 2.00e-6) = sqrt(1.00e4) = 100 ohm
zeta  = 100 / (2 * 100) = 0.500

wn    = 1 / sqrt(0.0200 * 2.00e-6) = 1 / 2.00e-4 = 5000 rad/s
fn    = 5000 / 6.283185 = 795.775 Hz

1 - 2 zeta^2 = 1 - 0.500 = 0.500
sqrt         = 0.7071068
fr           = 795.775 * 0.7071068 = 562.70 Hz
```

Below $f_n$, and by a lot: 29% below. The peak of a second-order low-pass always sits below
the natural frequency, and the heavier the damping the further below it slides, until at
$\zeta = 1/\sqrt{2} = 0.7071$ it reaches zero and there is no interior peak left at all.
That is the same statement as $1 - 2\zeta^2 = 0$.

Three frequencies are in play in this one circuit and it is worth writing all three out,
because at $\zeta = 0.5$ they are not close:

```
fn = 795.8 Hz   where the reactances cancel, phase exactly -90 deg
fd = fn sqrt(1 - zeta^2)  = 795.8 * 0.866025 = 689.2 Hz   the ringing frequency
fr = fn sqrt(1 - 2 zeta^2) = 795.8 * 0.707107 = 562.7 Hz   the driven peak
```

Compare with the first question of this ladder, where $\zeta$ was 0.11 and the same three
frequencies were 1591.5, 1581.9 and 1572.2 Hz — all within 1.3% of each other. That is why
the distinction can be ignored in a lightly damped tuned circuit and cannot be ignored here.

The peak is also barely a peak. Its height is
$1/(2\zeta\sqrt{1-\zeta^2}) = 1/0.866025 = 1.1547$, so the response bulges 15% above its
low-frequency value and no more. Halve the
resistor to 50 Ω and $\zeta$ becomes 0.25, the peak climbs to 2.07, and it moves back up to
$0.9354 f_n = 744.4$ Hz.
''',
                    "aside": "The 2 under the root is doing real work, and it is easy to justify. $\\omega_d$ comes from the *roots* of the quadratic, which is a question about the natural response. $\\omega_r$ comes from minimising $(1-u^2)^2 + (2\\zeta u)^2$, which is a question about the driven response. Different questions, different answers, and only the algebra tells you which root belongs to which.",
                },
                {
                    "title": "Current magnification in the parallel circuit",
                    "minutes": 12,
                    "brief": r'''
The hardest question here, and everything about it is a step away from the four before it:
the components are in parallel rather than in series, the source pushes a fixed **current**
rather than a fixed voltage, and the quantity asked for is not a node voltage.

The parallel circuit has the same $\omega_n = 1/\sqrt{LC}$ but a damping ratio in which the
resistance appears the other way up:

$$\zeta = \frac{1}{2R}\sqrt{\frac{L}{C}} = \frac{Z_0}{2R}$$

Two more facts you will need, both derived in the second reading unit or immediately from
it. Driven by a current, the impedance of the parallel combination is largest at $\omega_n$
exactly — not below it — and its value there is exactly $R$, because at $\omega_n$ the
inductor's and capacitor's currents are equal and opposite and cancel completely, leaving
the resistor to take the whole of the source current.

So: find $\omega_n$, find the voltage across the network there, and then ask the inductor
what current that voltage drives through it. The inductor's reactance is $\omega_n L$.
''',
                    "prompt": r"With the source at the frequency that maximises the voltage across the network, what is the amplitude of the current in the inductor?",
                    "note": "Answer in milliamps, to two decimal places. The source supplies 1.00 mA.",
                    "diagram": {
                        "parts": [
                            {"id": "i1", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 1e-3},
                            {"id": "r1", "kind": "R", "x": 7, "y": 6, "rot": 1, "value": 2000},
                            {"id": "l1", "kind": "L", "x": 11, "y": 6, "rot": 1, "value": 0.04},
                            {"id": "c1", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 2.5e-7},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 7, "y": 9},
                            {"id": "g2", "kind": "GND", "x": 11, "y": 9},
                            {"id": "g3", "kind": "GND", "x": 15, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 7, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [7, 4]},
                            {"a": [7, 4], "b": [7, 5]},
                            {"a": [7, 4], "b": [11, 4]},
                            {"a": [11, 4], "b": [11, 5]},
                            {"a": [11, 4], "b": [15, 4]},
                            {"a": [15, 4], "b": [15, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [7, 7], "b": [7, 9]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [15, 7], "b": [15, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 mA sinusoid, at the frequency of maximum response"},
                        {"label": "R1", "value": "2.00 kΩ"},
                        {"label": "L1", "value": "40.0 mH"},
                        {"label": "C1", "value": "250 nF"},
                        {"label": "Asked for", "value": "the inductor current amplitude, in milliamps"},
                    ],
                    # Nothing is assumed about where the maximum sits: the solver's own magnitude is
                    # scanned and refined to find it, and the inductor current is then computed from
                    # the measured node voltage and the inductance in the netlist.
                    "check": r'''
let bf = 1, best = 0;
for (let i = 0; i <= 3000; i++) {
  const f = Math.pow(10, i * 7 / 3000 - 1);
  const g = c.gain(f);
  if (g > best) { best = g; bf = f; }
}
let a = bf / 1.03, b = bf * 1.03;
for (let i = 0; i < 160; i++) {
  const m1 = a * Math.pow(b / a, 0.382), m2 = a * Math.pow(b / a, 0.618);
  if (c.gain(m1) > c.gain(m2)) b = m2; else a = m1;
}
const fr = Math.sqrt(a * b);
return 1000 * c.gain(fr) / (2 * Math.PI * fr * c.values('L')[0]);
''',
                    "answer": 5.0,
                    "tol": 0.05,
                    "unit": "mA",
                    "hint": r"$\omega_n = 1/\sqrt{0.0400 \times 2.50\times10^{-7}}$ is a round 10 000 rad/s. The voltage across the network at that frequency is $I \times R$. Then $|I_L| = V/(\omega_n L)$.",
                    "wrong": r"If you got 1.00, the current was divided by $R$ rather than by the inductor's reactance, which returns the source current unchanged — right for a resistor on its own and for nothing else here. If you got 31.4, $f_n = 1591.5$ Hz was used where $\omega_n = 10\,000$ rad/s belongs, so the reactance came out $2\pi$ times too small. If you got 0.200, the *series* damping formula was used: it gives $\zeta = 2.5$, hence $Q = 0.2$, and the circuit would be attenuating rather than magnifying. If you got 5000, the amps were never converted to milliamps.",
                    "why": r'''
```
LC     = 0.0400 * 2.50e-7 = 1.00e-8 s^2
wn     = 1 / 1.00e-4 = 10 000 rad/s        fn = 1591.5 Hz

Z0     = sqrt(0.0400 / 2.50e-7) = sqrt(1.60e5) = 400 ohm
zeta   = Z0 / (2 R) = 400 / 4000 = 0.100

V at wn = I * R = 1.00e-3 * 2000 = 2.00 V
XL      = wn L = 10 000 * 0.0400 = 400 ohm
|IL|    = 2.00 / 400 = 5.00e-3 A = 5.00 mA
```

The source supplies 1.00 mA and the inductor carries 5.00 mA. That is not an error and no
energy has been created: the capacitor is carrying 5.00 mA as well, in exact antiphase, so
the two of them are passing 5 mA back and forth between themselves every cycle and only the
1 mA difference ever reaches the source. This is **current magnification**, and the factor
is

$$Q = \frac{1}{2\zeta} = \frac{R}{Z_0} = \frac{2000}{400} = 5$$

the same $Q$ that in the series circuit magnified a *voltage*. Same quadratic, dual
circuit, dual quantity.

Check the capacitor to see the cancellation directly:

```
XC   = 1 / (wn C) = 1 / (10 000 * 2.50e-7) = 1 / 2.50e-3 = 400 ohm
|IC| = 2.00 / 400 = 5.00 mA
```

Equal, because $\omega_n$ is by definition where $\omega L = 1/(\omega C)$; opposite in sign,
because one current leads the voltage by 90° and the other lags by 90°. They cancel exactly,
which is why the source sees only the resistor and why the peak of $|Z|$ is at $\omega_n$
precisely, with no $\sqrt{1-2\zeta^2}$ correction anywhere in sight.

The trap in this question is the damping ratio, and it is worth stating plainly. Using the
series formula $\zeta = \frac{R}{2}\sqrt{C/L} = 1000 \times 0.0025 = 2.5$ would say this
circuit is heavily overdamped and cannot resonate at all, when in fact $\zeta = 0.100$ and
it has a $Q$ of 5. The two formulas are reciprocals of each other, so getting them the wrong
way round does not produce a small error — it produces the opposite answer.
''',
                    "aside": "Where the 5 mA actually hurts: the inductor and the capacitor have to be rated for it, and the wire in the coil dissipates $I^2R_{\\text{wire}}$ at 25 times the rate the 1 mA source current would suggest. A tuned circuit with a $Q$ of 100 circulates 100 times its input current, and the components have to survive that.",
                },
            ],
            "blanks": [
                {
                    "title": "From components to the standard form",
                    "minutes": 8,
                    "caption": "v'' is the second derivative, wn is omega_n, and Z0 is the characteristic impedance",
                    "lang": "text",
                    "brief": r'''
Nothing runs here. The first four lines are the route from a series $R$, $L$, $C$ to the
quadratic every second-order system is written in; the six holes are the results you will
reach for.

`sqrt` is a square root, `^` is a power, and `Vs` is the supply.
''',
                    "listing": r'''
series R, L, C, output across C     LC v'' + RC v' + v = Vs

try v = A e^(s t), set Vs = 0       LC s^2 + RC s + 1 = 0

divide through by LC                s^2 + (R/L) s + 1/(LC) = 0

the standard form                   s^2 + 2 zeta wn s + wn^2 = 0


matching the constant term          wn    =  ___

matching the coefficient of s       zeta  =  ___

the impedance zeta compares R with  Z0    =  ___

the two roots of the quadratic      s     =  ___

the ringing frequency, zeta < 1     wd    =  ___

the R that makes it critical        R     =  ___
''',
                    "blanks": [
                        {
                            "prompt": "The natural frequency, in radians per second.",
                            "hole": "?",
                            "opts": ["sqrt(L C)", "1 / sqrt(L C)", "1 / (L C)", "1 / (2 pi sqrt(L C))"],
                            "a": 1,
                            "why": r"$\omega_n^2 = 1/(LC)$ from matching the constant term, so $\omega_n = 1/\sqrt{LC}$. Check the units: $LC$ has units of seconds squared, so its square root is a time and the reciprocal is a rate. With $L = 100$ mH and $C = 100$ nF that is $1/10^{-4} = 10\,000$ rad/s.",
                            "whys": [
                                r"$\sqrt{LC}$ is a *time*, not a frequency — it is $1/\omega_n$, and for a 100 mH, 100 nF pair it is 100 µs. Inverting it is the step that is missing.",
                                r"$\omega_n^2 = 1/(LC)$ from matching the constant term, so $\omega_n = 1/\sqrt{LC}$. Check the units: $LC$ has units of seconds squared, so its square root is a time and the reciprocal is a rate. With $L = 100$ mH and $C = 100$ nF that is $1/10^{-4} = 10\,000$ rad/s.",
                                r"That is $\omega_n^2$, the constant term itself, with the square root never taken. It is off by a factor of $\omega_n$, which for a typical circuit is four orders of magnitude.",
                                r"This is $f_n$ in hertz, not $\omega_n$ in radians per second. Both are useful and they differ by $2\pi$, but every other formula in this module — the roots, $\zeta$, $\omega_d$ — is written in $\omega$, so mixing the two in mid-calculation is the error the module warns about most.",
                            ],
                        },
                        {
                            "prompt": "The damping ratio. A pure number.",
                            "hole": "?",
                            "opts": ["(R/2) sqrt(L/C)", "R sqrt(L C)", "(R/2) sqrt(C/L)", "2 R sqrt(C/L)"],
                            "a": 2,
                            "why": r"Matching the $s$ terms gives $2\zeta\omega_n = R/L$, so $\zeta = R/(2L\omega_n) = R\sqrt{LC}/(2L)$, and $\sqrt{LC}/L = \sqrt{C/L}$. The $C$ is on top. Sanity check with $R = 33\,\Omega$, $L = 20$ mH, $C = 2$ µF: $\sqrt{C/L} = 0.01$, so $\zeta = 16.5 \times 0.01 = 0.165$, a lightly damped circuit — which is what a small resistor should give.",
                            "whys": [
                                r"The ratio is upside down. With $\sqrt{L/C}$ a 33 Ω resistor in a 20 mH, 2 µF circuit would come out at $\zeta = 1.65$ and be called overdamped, when in fact it rings hard. Remember that a *small* resistance means *light* damping, and check any candidate formula against that.",
                                r"There is no factor of 2, and the dimensions do not work either: $R\sqrt{LC}$ is ohms times seconds, which is not a pure number.",
                                r"Matching the $s$ terms gives $2\zeta\omega_n = R/L$, so $\zeta = R/(2L\omega_n) = R\sqrt{LC}/(2L)$, and $\sqrt{LC}/L = \sqrt{C/L}$. The $C$ is on top. Sanity check with $R = 33\,\Omega$, $L = 20$ mH, $C = 2$ µF: $\sqrt{C/L} = 0.01$, so $\zeta = 16.5 \times 0.01 = 0.165$, a lightly damped circuit — which is what a small resistor should give.",
                                r"The 2 belongs underneath, not on top. It arrives from the $2\zeta\omega_n$ in the standard form, and putting it the other way multiplies every damping ratio by four — enough to turn a ringing circuit into an apparently overdamped one.",
                            ],
                        },
                        {
                            "prompt": "The resistance that the damping ratio is really a comparison against.",
                            "hole": "?",
                            "opts": ["sqrt(L/C)", "sqrt(L C)", "L / C", "R / 2"],
                            "a": 0,
                            "why": r"$\zeta = \frac{R}{2}\sqrt{C/L}$ can be written $R/(2Z_0)$ with $Z_0 = \sqrt{L/C}$, which is measured in ohms: $L$ is in V·s/A and $C$ is in A·s/V, so $L/C$ is in $\text{V}^2/\text{A}^2$ and its root is a resistance. Damping is never the resistance alone, it is the resistance compared with this. For 20 mH and 2 µF, $Z_0 = 100\,\Omega$.",
                            "whys": [
                                r"$\zeta = \frac{R}{2}\sqrt{C/L}$ can be written $R/(2Z_0)$ with $Z_0 = \sqrt{L/C}$, which is measured in ohms: $L$ is in V·s/A and $C$ is in A·s/V, so $L/C$ is in $\text{V}^2/\text{A}^2$ and its root is a resistance. Damping is never the resistance alone, it is the resistance compared with this. For 20 mH and 2 µF, $Z_0 = 100\,\Omega$.",
                                r"$\sqrt{LC}$ is a time — it is $1/\omega_n$. It sets how fast the circuit is, not how heavily it is damped, and it is not measured in ohms.",
                                r"$L/C$ has units of ohms *squared*, so it is $Z_0^2$. For 20 mH and 2 µF it is 10 000, and calling that an impedance would put the damping out by a factor of 100.",
                                r"$R/2$ is half of the thing being compared, not the thing it is compared against. A formula for $\zeta$ has to contain both $L$ and $C$, because the same resistor damps differently in different circuits.",
                            ],
                        },
                        {
                            "prompt": "Solving the quadratic. Both roots at once.",
                            "hole": "?",
                            "opts": [
                                "wn(-zeta +/- sqrt(1 - zeta^2))",
                                "wn(-zeta +/- sqrt(zeta^2 - 1))",
                                "-zeta +/- sqrt(zeta^2 - 1)",
                                "wn(zeta +/- sqrt(zeta^2 - 1))",
                            ],
                            "a": 1,
                            "why": r"The quadratic formula on $s^2 + 2\zeta\omega_n s + \omega_n^2 = 0$ gives $s = \frac{-2\zeta\omega_n \pm \sqrt{4\zeta^2\omega_n^2 - 4\omega_n^2}}{2} = \omega_n(-\zeta \pm \sqrt{\zeta^2-1})$. Everything the module says follows from the sign of what is under that root: positive gives two real roots and no overshoot, negative gives a complex pair and ringing.",
                            "whys": [
                                r"The discriminant is $\zeta^2 - 1$, not $1 - \zeta^2$. Written this way the roots would be complex when $\zeta > 1$ — heavy damping producing oscillation — which is backwards. The $1 - \zeta^2$ form does appear in this module, but under $\omega_d$, after the $j$ has been factored out.",
                                r"The quadratic formula on $s^2 + 2\zeta\omega_n s + \omega_n^2 = 0$ gives $s = \frac{-2\zeta\omega_n \pm \sqrt{4\zeta^2\omega_n^2 - 4\omega_n^2}}{2} = \omega_n(-\zeta \pm \sqrt{\zeta^2-1})$. Everything the module says follows from the sign of what is under that root: positive gives two real roots and no overshoot, negative gives a complex pair and ringing.",
                                r"The $\omega_n$ has been dropped. Without it the answer is a pure number, and a root of the characteristic equation must have units of 1/s — it is the $s$ in $e^{st}$.",
                                r"The leading sign is wrong. A root with a positive real part means $e^{st}$ *grows*, so the circuit would oscillate ever harder on its own, which no arrangement of a resistor, a capacitor and an inductor can do.",
                            ],
                        },
                        {
                            "prompt": "The frequency of the ringing, when there is any.",
                            "hole": "?",
                            "opts": ["wn sqrt(zeta^2 - 1)", "wn (1 - zeta)", "wn sqrt(1 - 2 zeta^2)", "wn sqrt(1 - zeta^2)"],
                            "a": 3,
                            "why": r"When $\zeta < 1$ the discriminant is negative, so write $\sqrt{\zeta^2-1} = j\sqrt{1-\zeta^2}$ and the roots become $-\zeta\omega_n \pm j\omega_n\sqrt{1-\zeta^2}$. The imaginary part is the rotation rate, so $\omega_d = \omega_n\sqrt{1-\zeta^2}$: always a little below $\omega_n$, and equal to it only when there is no damping at all.",
                            "whys": [
                                r"That is the real discriminant, which is what you use when $\zeta > 1$ — and in that case there is no ringing to have a frequency. Below 1 the quantity under this root is negative.",
                                r"Damping does slow the ringing, but not linearly. At $\zeta = 0.5$ this would give $0.5\omega_n$ where the true answer is $0.866\omega_n$, and at $\zeta = 0.1$ it gives $0.9\omega_n$ where the true answer is $0.995\omega_n$.",
                                r"The 2 under the root belongs to $\omega_r$, the frequency at which the *driven* response peaks. That is a different question — one about a sinusoid being applied, not about what the circuit does on its own — and it gives a lower frequency still.",
                                r"When $\zeta < 1$ the discriminant is negative, so write $\sqrt{\zeta^2-1} = j\sqrt{1-\zeta^2}$ and the roots become $-\zeta\omega_n \pm j\omega_n\sqrt{1-\zeta^2}$. The imaginary part is the rotation rate, so $\omega_d = \omega_n\sqrt{1-\zeta^2}$: always a little below $\omega_n$, and equal to it only when there is no damping at all.",
                            ],
                        },
                        {
                            "prompt": "The resistance that puts the circuit exactly on the boundary.",
                            "hole": "?",
                            "opts": ["(1/2) sqrt(L/C)", "2 sqrt(L C)", "2 sqrt(L/C)", "sqrt(L/C)"],
                            "a": 2,
                            "why": r"Critical damping is $\zeta = 1$, and $\zeta = R/(2Z_0)$, so $R = 2Z_0 = 2\sqrt{L/C}$. For 20 mH and 2 µF that is 200 Ω. It is the same statement as $R^2 = 4L/C$, which is the form the quiz uses, and below it the circuit rings.",
                            "whys": [
                                r"This is $Z_0/2$, which is $\zeta = 0.25$ — a circuit that still overshoots by 44%. The factor is out by four.",
                                r"$\sqrt{LC}$ is a time, so this would set a resistance equal to a number of seconds. Any candidate formula for a resistance has to reduce to ohms, and $\sqrt{L/C}$ is the only combination of $L$ and $C$ that does.",
                                r"Critical damping is $\zeta = 1$, and $\zeta = R/(2Z_0)$, so $R = 2Z_0 = 2\sqrt{L/C}$. For 20 mH and 2 µF that is 200 Ω. It is the same statement as $R^2 = 4L/C$, which is the form the quiz uses, and below it the circuit rings.",
                                r"$R = Z_0$ gives $\zeta = 0.5$, not 1 — a circuit with a visible 16% overshoot. The 2 is not decoration; it comes from the $2\zeta\omega_n$ in the standard form.",
                            ],
                        },
                    ],
                },
                {
                    "title": "What the two numbers predict",
                    "minutes": 9,
                    "caption": "wn and zeta are given; every line below is a consequence of them",
                    "lang": "text",
                    "brief": r'''
The same circuit asked two different questions — hit with a step, then driven with a
sinusoid and swept — plus one line about what changes when the three components are put in
parallel instead of in series.

`exp(x)` is the exponential, `pi` is 3.14159, and `wd` is $\omega_n\sqrt{1-\zeta^2}$.
''',
                    "listing": r'''
given                          wn  and  zeta < 1


STEP INPUT

  the error |v - Vs| decays as     exp(- ___ * t)

  the first peak overshoots by     ___

  and it gets there at time  t_p = ___


SINE INPUT, frequency swept

  the response peaks at      w_r = ___

  and its height there is          ___    times the low-frequency value


THE SAME PARTS IN PARALLEL, driven by a current source

  wn is unchanged, but      zeta = ___
''',
                    "blanks": [
                        {
                            "prompt": "The rate at which the envelope shrinks.",
                            "hole": "?",
                            "opts": ["zeta", "wd", "zeta * wn", "wn"],
                            "a": 2,
                            "why": r"The roots are $-\zeta\omega_n \pm j\omega_d$, and the real part is what multiplies $t$ in the decaying exponential. So the envelope is $e^{-\zeta\omega_n t}$ and the decay time constant is $1/(\zeta\omega_n)$. With $\zeta = 0.25$ and $\omega_n = 1000$ rad/s the envelope falls by a factor of $e$ every 4 ms.",
                            "whys": [
                                r"$\zeta$ is a pure number, so $e^{-\zeta t}$ would have a time in the exponent with nothing to cancel it. An exponent must be dimensionless, and that requires a rate multiplying $t$.",
                                r"$\omega_d$ is the imaginary part of the root — how fast the response rotates, not how fast it decays. It sets the pitch of the ringing; this blank is about the envelope.",
                                r"The roots are $-\zeta\omega_n \pm j\omega_d$, and the real part is what multiplies $t$ in the decaying exponential. So the envelope is $e^{-\zeta\omega_n t}$ and the decay time constant is $1/(\zeta\omega_n)$. With $\zeta = 0.25$ and $\omega_n = 1000$ rad/s the envelope falls by a factor of $e$ every 4 ms.",
                                r"$\omega_n$ alone is the decay rate only in the one case $\zeta = 1$. For a lightly damped circuit it would predict a response that vanishes almost immediately, when the whole difficulty with light damping is that it does not.",
                            ],
                        },
                        {
                            "prompt": "How far past the final value the first peak goes, as a fraction of the step.",
                            "hole": "?",
                            "opts": [
                                "exp(-pi zeta / sqrt(1 - zeta^2))",
                                "exp(-2 pi zeta)",
                                "exp(-pi / (zeta wn))",
                                "1 - zeta",
                            ],
                            "a": 0,
                            "why": r"The extrema fall at $t = k\pi/\omega_d$, and evaluating the response there gives $M_p^k$ with $M_p = \exp(-\pi\zeta/\sqrt{1-\zeta^2})$. Note what is missing: $\omega_n$ is not in it. Overshoot depends on $\zeta$ alone — $\omega_n$ only decides how quickly it all happens. At $\zeta = 0.25$, $M_p = 0.444$, so a 2 V step reaches 2.89 V.",
                            "whys": [
                                r"The extrema fall at $t = k\pi/\omega_d$, and evaluating the response there gives $M_p^k$ with $M_p = \exp(-\pi\zeta/\sqrt{1-\zeta^2})$. Note what is missing: $\omega_n$ is not in it. Overshoot depends on $\zeta$ alone — $\omega_n$ only decides how quickly it all happens. At $\zeta = 0.25$, $M_p = 0.444$, so a 2 V step reaches 2.89 V.",
                                r"This is the same shape but with the $\sqrt{1-\zeta^2}$ missing and the $\pi$ doubled — it is the ratio between *successive* peaks on the same side, which is $M_p^2$ only when $\zeta$ is small enough for the root to be near 1.",
                                r"An overshoot is a pure fraction, and this expression is not dimensionless: $\zeta\omega_n$ is a rate, so $\pi/(\zeta\omega_n)$ is a time. It is in fact roughly a decay time constant, which is a different kind of answer altogether.",
                                r"A straight line in $\zeta$ has the right rough behaviour — less overshoot as damping rises — but it is wrong everywhere and badly wrong at the ends. At $\zeta = 0.5$ it claims 50% where the true figure is 16%, and it reaches zero at $\zeta = 1$ only by coincidence of shape.",
                            ],
                        },
                        {
                            "prompt": "The time at which that first peak happens.",
                            "hole": "?",
                            "opts": ["2 pi / wd", "pi / wn", "1 / (zeta wn)", "pi / wd"],
                            "a": 3,
                            "why": r"Differentiating the step response and setting it to zero puts the extrema at $t = k\pi/\omega_d$ — every half cycle of the ringing. The first of them, $k = 1$, is the overshoot peak. For $\omega_d = 968$ rad/s that is $3.1416/968 = 3.24$ ms.",
                            "whys": [
                                r"That is a full ringing period, which lands on the *second* extremum — the trough after the first peak, not the peak itself. The extrema are half a period apart.",
                                r"Close, but the ringing happens at $\omega_d$, not $\omega_n$. The two are within a per cent of each other at light damping and diverge as $\zeta$ grows; at $\zeta = 0.5$ this would be 13% early.",
                                r"$1/(\zeta\omega_n)$ is the decay time constant of the envelope — how long the ringing lasts, not when the first peak occurs. The two are unrelated: a circuit can peak early and ring for a long time afterwards.",
                                r"Differentiating the step response and setting it to zero puts the extrema at $t = k\pi/\omega_d$ — every half cycle of the ringing. The first of them, $k = 1$, is the overshoot peak. For $\omega_d = 968$ rad/s that is $3.1416/968 = 3.24$ ms.",
                            ],
                        },
                        {
                            "prompt": "Now a sinusoid. Where the output is biggest.",
                            "hole": "?",
                            "opts": ["wn sqrt(1 - zeta^2)", "wn", "wn sqrt(1 - 2 zeta^2)", "wn sqrt(1 + 2 zeta^2)"],
                            "a": 2,
                            "why": r"Minimising $(1-u^2)^2 + (2\zeta u)^2$ over $u = \omega/\omega_n$ gives $u(u^2 - 1 + 2\zeta^2) = 0$, so the interior maximum is at $u = \sqrt{1-2\zeta^2}$. It exists only while $1 - 2\zeta^2 > 0$, that is $\zeta < 1/\sqrt{2} \approx 0.707$; above that the response has no peak and falls away from DC.",
                            "whys": [
                                r"That is $\omega_d$, which came from the roots and describes the circuit ringing on its own. This blank is about a sinusoid being applied, which is a different question and gives a lower frequency.",
                                r"$\omega_n$ is where the reactances cancel and the phase is exactly $-90°$, and it is where people expect the peak to be — but the maximum of the magnitude sits below it whenever there is any damping at all. At $\zeta = 0.5$ it is 29% below.",
                                r"Minimising $(1-u^2)^2 + (2\zeta u)^2$ over $u = \omega/\omega_n$ gives $u(u^2 - 1 + 2\zeta^2) = 0$, so the interior maximum is at $u = \sqrt{1-2\zeta^2}$. It exists only while $1 - 2\zeta^2 > 0$, that is $\zeta < 1/\sqrt{2} \approx 0.707$; above that the response has no peak and falls away from DC.",
                                r"A plus sign would put the peak *above* $\omega_n$ and would never let it vanish, no matter how heavy the damping. Both of those contradict what a heavily damped low-pass visibly does.",
                            ],
                        },
                        {
                            "prompt": "And how tall that peak is.",
                            "hole": "?",
                            "opts": [
                                "1 / (2 zeta)",
                                "1 / (2 zeta sqrt(1 - zeta^2))",
                                "1 / sqrt(1 - 2 zeta^2)",
                                "1 / (2 zeta sqrt(1 - 2 zeta^2))",
                            ],
                            "a": 1,
                            "why": r"Substituting $u^2 = 1-2\zeta^2$ back into $|H| = 1/\sqrt{(1-u^2)^2 + (2\zeta u)^2}$ leaves $1/(2\zeta\sqrt{1-\zeta^2})$. At $\zeta = 0.25$ that is 2.066 against 2.000 for the height at $\omega_n$ — a 3% gap that grows to 15% by $\zeta = 0.5$.",
                            "whys": [
                                r"$1/(2\zeta)$ is the height *at* $\omega_n$, which is not where the maximum is. It is the quantity called $Q$, it is exact enough for a lightly damped tuned circuit, and it is 15% low by $\zeta = 0.5$ — where you are most likely to be relying on it.",
                                r"Substituting $u^2 = 1-2\zeta^2$ back into $|H| = 1/\sqrt{(1-u^2)^2 + (2\zeta u)^2}$ leaves $1/(2\zeta\sqrt{1-\zeta^2})$. At $\zeta = 0.25$ that is 2.066 against 2.000 for the height at $\omega_n$ — a 3% gap that grows to 15% by $\zeta = 0.5$.",
                                r"This has no $2\zeta$ in front, so it stays near 1 for small $\zeta$ instead of growing without bound. A very lightly damped circuit peaks enormously; any formula that does not blow up as $\zeta \to 0$ is describing something else.",
                                r"The $\sqrt{1-2\zeta^2}$ is the expression for *where* the peak sits, reused by mistake as part of its height. It also misbehaves at $\zeta = 1/\sqrt{2}$, where it divides by zero, while the true peak height there is a perfectly finite 1.",
                            ],
                        },
                        {
                            "prompt": "The same three components in parallel, driven by a current source.",
                            "hole": "?",
                            "opts": [
                                "(R/2) sqrt(C/L)",
                                "(1/(2R)) sqrt(L/C)",
                                "(1/(2R)) sqrt(C/L)",
                                "R sqrt(C/L)",
                            ],
                            "a": 1,
                            "why": r"Kirchhoff's current law on the single node gives $C\ddot{v} + \dot{v}/R + v/L = \dot{I}$, so dividing by $C$ makes $2\zeta\omega_n = 1/(RC)$ and $\zeta = \frac{1}{2RC\omega_n} = \frac{1}{2R}\sqrt{L/C} = Z_0/(2R)$. The resistance has moved to the bottom: a *bigger* parallel resistor rings more, because in parallel the resistor is the route by which energy escapes, and a large resistor is a poor route.",
                            "whys": [
                                r"That is the series formula, and using it on a parallel circuit does not give a slightly wrong answer — it gives the reciprocal. A parallel circuit with $R = 2$ kΩ, $L = 40$ mH and $C = 250$ nF has $\zeta = 0.1$; this formula would report 2.5 and call it overdamped.",
                                r"Kirchhoff's current law on the single node gives $C\ddot{v} + \dot{v}/R + v/L = \dot{I}$, so dividing by $C$ makes $2\zeta\omega_n = 1/(RC)$ and $\zeta = \frac{1}{2RC\omega_n} = \frac{1}{2R}\sqrt{L/C} = Z_0/(2R)$. The resistance has moved to the bottom: a *bigger* parallel resistor rings more, because in parallel the resistor is the route by which energy escapes, and a large resistor is a poor route.",
                                r"The $R$ is correctly underneath but the $L$ and $C$ have been swapped, which breaks the units: $\zeta$ has to be dimensionless, and $\frac{1}{R}\sqrt{C/L}$ is one over an ohm times one over an ohm.",
                                r"The factor of 2 is missing and the $R$ is on top. Both halves of the parallel result have gone: it should be $1/(2R)$, not $R$.",
                            ],
                        },
                    ],
                },
            ],
            "tune": {
                "title": "A 1 kHz resonance, damped to order",
                "minutes": 10,
                "brief": r'''
Three sliders, two requirements, and they do not line up one-to-one with each other.

The resonant frequency depends on $L$ and $C$ only, through their product. The
damping depends on all three, through $\frac{R}{2}\sqrt{C/L}$. So $L$ and $C$ can be
traded against one another at constant frequency — double one and halve the other —
and doing so changes $\sqrt{L/C}$, which moves the damping even though $R$ has not
been touched.

Work out the product $LC$ you need first, from $f_n = 1/(2\pi\sqrt{LC})$. Then pick
a pair with that product, and let $R$ take whatever value the damping demands.
''',
                "prompt": r"Resonate at 1.00 kHz with a damping ratio of 0.20.",
                "note": "Both numbers are read from the panel beside the plot; both have to be right at once.",
                "model": "rlc",
                "initial": {"r": 100, "l": 100, "c": 2.5},
                "plotKey": "fn",
                "constraints": [
                    {"k": "fn", "label": "resonant frequency 1.00 kHz ± 20 Hz", "eq": 1000.0, "tol": 20.0},
                    {"k": "zeta", "label": "damping ζ = 0.20 ± 0.02", "eq": 0.20, "tol": 0.02},
                ],
            },
            "quiz": {
                "title": "Reading a second-order circuit off its components",
                "minutes": 9,
                "questions": [
                    {
                        "q": r"A series circuit has $L = 100$ mH and $C = 2.5$ µF. What is $\omega_n$?",
                        "opts": ["500 rad/s", "2000 rad/s", "4000 rad/s", "318 rad/s"],
                        "a": 1,
                        "why": (
                            r"$\omega_n = 1/\sqrt{LC} = 1/\sqrt{0.1 \times 2.5\times10^{-6}} = 1/\sqrt{2.5\times10^{-7}} "
                            r"= 1/(5\times10^{-4}) = 2000$ rad/s. The 318 is the same circuit in hertz — "
                            r"$2000/2\pi = 318.3$ Hz — and mixing the two units up is the commonest error in the "
                            r"whole subject. Read the units of the answer before choosing it."
                        ),
                    },
                    {
                        "q": r"Same circuit, with $R = 100\,\Omega$, giving $\zeta = 0.25$. What does the step response do?",
                        "opts": [
                            "Rises to the final value and stops, without ever crossing it",
                            "Overshoots, rings, and settles",
                            "Oscillates for ever at constant amplitude",
                            "Falls towards zero instead of rising",
                        ],
                        "a": 1,
                        "why": (
                            r"$\zeta = 0.25$ is below 1, so the roots are a complex pair: a rotation multiplied by "
                            r"$e^{-\zeta\omega_n t}$. The rotation is what carries the response past its final value; "
                            r"the decay is what brings it back. Constant oscillation would need $\zeta$ to be exactly "
                            r"zero, which means no resistance at all."
                        ),
                    },
                    {
                        "q": r"Which value of $\zeta$ gives the fastest arrival at the final value with no overshoot whatever?",
                        "opts": ["0", "0.5", "1", "2"],
                        "a": 2,
                        "why": (
                            r"$\zeta = 1$ is critical damping: the discriminant is exactly zero, the two roots meet, "
                            r"and the response arrives without crossing. Below 1 it overshoots; above 1 it is slower, "
                            r"because one of the two real roots creeps towards the origin and that slow exponential "
                            r"then sets the pace."
                        ),
                    },
                    {
                        "q": r"In terms of the components, the circuit rings exactly when:",
                        "opts": [r"$R^2 < 4L/C$", r"$R^2 > 4L/C$", r"$R > L/C$", r"$R^2 < LC$"],
                        "a": 0,
                        "why": (
                            r"Ringing means $\zeta < 1$, and $\zeta = \frac{R}{2}\sqrt{C/L}$, so the condition is "
                            r"$\frac{R^2C}{4L} < 1$, which rearranges to $R^2 < 4L/C$. Note what it says: a *smaller* "
                            r"resistance is what makes a circuit ring, because the resistor is the only part that "
                            r"removes energy. $R^2 < LC$ is not even dimensionally possible."
                        ),
                    },
                    {
                        "q": r"You double $R$ and change nothing else. What happens to $\omega_n$?",
                        "opts": ["It doubles", "It halves", "It is unchanged", "It quadruples"],
                        "a": 2,
                        "why": (
                            r"$\omega_n = 1/\sqrt{LC}$ contains no $R$ at all, so the natural frequency does not move. "
                            r"What doubles is $\zeta$, since $\zeta = \frac{R}{2}\sqrt{C/L}$ is proportional to $R$. "
                            r"That separation is the useful part of the standard form: one knob for the pitch, "
                            r"another for how long it rings."
                        ),
                    },
                    {
                        "q": r"Driven by a sinusoid, a second-order low-pass with $\zeta = 0.25$ peaks at how many times its low-frequency size?",
                        "opts": ["Exactly 2", "About 2.07", "About 4", "1 — there is no peak"],
                        "a": 1,
                        "why": (
                            r"$1/\left(2\zeta\sqrt{1-\zeta^2}\right) = 1/(0.5 \times 0.968) = 2.07$. The tempting "
                            r"$1/(2\zeta) = 2$ is the height at $\omega = \omega_n$ exactly, and the true peak sits "
                            r"slightly below that frequency and slightly above that height. There is no peak at all "
                            r"once $\zeta$ passes $1/\sqrt{2}$."
                        ),
                    },
                ],
            },
            "derive": {
                "title": "From two energy stores to $\\omega_n$ and $\\zeta$",
                "minutes": 14,
                "vars": ["s", "R", "L", "C", "omega_n", "zeta", "A", "t"],
                "brief": r'''
A series $R$, $L$, $C$ with the output across the capacitor obeys

$$LC\ddot{v} + RC\dot{v} + v = V_s$$

To find how it behaves on its own — the part of the response that dies away — set
$V_s = 0$ and try $v = Ae^{st}$. Each derivative brings down one factor of $s$, and
the common factor $Ae^{st}$ is never zero, so it divides out of every term.
''',
                "steps": [
                    {
                        "prompt": r"Write what is left after dividing by $Ae^{st}$: the polynomial in $s$ that must equal zero.",
                        "answer": r"L C s^2 + R C s + 1",
                        "hint": r"$\ddot{v}$ contributes $s^2$, $\dot{v}$ contributes $s$, and $v$ contributes 1 — each keeping the coefficient it already had.",
                        "deconstruct": [
                            r"$LC\ddot{v} \to LCs^2Ae^{st}$, $RC\dot{v} \to RCsAe^{st}$, $v \to Ae^{st}$.",
                            r"Divide every term by $Ae^{st}$ and set the sum to zero.",
                        ],
                    },
                    {
                        "prompt": r"Divide through by $LC$ so that $s^2$ stands alone. Write the constant term — the one with no $s$ in it.",
                        "answer": r"1/(L C)",
                        "hint": r"The constant was 1; dividing it by $LC$ is the whole step.",
                        "deconstruct": [
                            r"The three terms become $s^2$, $\frac{R}{L}s$ and $\frac{1}{LC}$.",
                            r"You are asked for the last of them.",
                        ],
                    },
                    {
                        "prompt": r"The standard form is $s^2 + 2\zeta\omega_n s + \omega_n^2$. Its constant term is $\omega_n^2$, so match it against yours and write $\omega_n$.",
                        "answer": r"1/\sqrt{L C}",
                        "placeholder": r"one over a square root",
                        "hint": r"$\omega_n^2 = 1/(LC)$. Take the positive square root of both sides.",
                        "deconstruct": [
                            r"$\omega_n^2 = \frac{1}{LC}$.",
                            r"$\omega_n = \sqrt{\frac{1}{LC}}$, which is $1/\sqrt{LC}$.",
                        ],
                    },
                    {
                        "prompt": r"Now match the coefficient of $s$: $2\zeta\omega_n = R/L$. Substitute the $\omega_n$ you just found and write $\zeta$ in terms of $R$, $L$ and $C$.",
                        "answer": r"(R/2)\sqrt{C/L}",
                        "hint": r"$\zeta = \dfrac{R}{2L\omega_n}$, and dividing by $\omega_n$ is multiplying by $\sqrt{LC}$.",
                        "deconstruct": [
                            r"$\zeta = \frac{R}{2L\omega_n}$.",
                            r"$\frac{1}{\omega_n} = \sqrt{LC}$, so $\zeta = \frac{R\sqrt{LC}}{2L}$.",
                            r"$\frac{\sqrt{LC}}{L} = \sqrt{\frac{C}{L}}$.",
                        ],
                    },
                    {
                        "prompt": r"The roots are $s = \omega_n\left(-\zeta \pm \sqrt{\zeta^2-1}\right)$. Write the condition on $\zeta$ that makes them a complex pair, so that the circuit rings.",
                        "answer": r"\zeta < 1",
                        "hint": r"A square root is imaginary exactly when what is under it is negative.",
                        "deconstruct": [
                            r"The roots are complex when $\zeta^2 - 1 < 0$.",
                            r"$\zeta$ is never negative for a real resistance, so that is $\zeta < 1$.",
                        ],
                    },
                ],
                "closing": r'''
Two numbers now stand in for three components. $\omega_n$ says how fast, $\zeta$ says
how long it rings, and any $R$, $L$, $C$ with the same pair behaves identically —
which is why the rest of engineering talks about $\zeta$ and $\omega_n$ and not about
millihenries.

Written out, $\zeta = \frac{R}{2}\sqrt{C/L}$ says the resistance is being compared
against $\sqrt{L/C}$, a quantity in ohms built from the two energy stores. For the
100 mH and 2.5 µF used in the quiz that is 200 Ω, so a 100 Ω resistor gives
$\zeta = 0.25$ and rings, while 400 Ω would not.
''',
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "Approximation: the straight line that stands in for the curve",
            "summary": "Every formula in engineering gets used near some operating point, and near a point a smooth curve is a straight line. What matters is knowing how far 'near' extends.",
            "concepts": [
                r"**Taylor's approximation** rebuilds a function near a point $a$ out of its derivatives there: $f(x) \approx f(a) + f'(a)(x-a) + \frac{f''(a)}{2}(x-a)^2 + \cdots$. Keep one term and you have a constant; keep two and you have the tangent line; each further term buys accuracy further from $a$.",
                r"Expanded about zero, the three functions this course keeps meeting are $e^x = 1 + x + \frac{x^2}{2} + \frac{x^3}{6} + \cdots$, $\sin x = x - \frac{x^3}{6} + \cdots$ and $\cos x = 1 - \frac{x^2}{2} + \cdots$. The first two terms of each are the ones used in practice.",
                r"The **binomial approximation** $(1+x)^n \approx 1 + nx$ for $|x| \ll 1$ covers a whole family at once: $1/(1+x) \approx 1 - x$ with $n = -1$, and $\sqrt{1+x} \approx 1 + \frac{x}{2}$ with $n = \frac{1}{2}$.",
                r"The size of the first term you dropped is the size of the error. Dropping the $x^2/2$ term costs about $x^2/2$ — so halving $x$ quarters the error, and an approximation quoted without that estimate is a guess rather than an approximation.",
                r"First engineering use: **asymptotes**. The response $|G| = 1/\sqrt{1+(f/f_c)^2}$ is close to 1 well below the corner and close to $f_c/f$ well above it. Sketching those two straight lines and joining them near the corner is the whole of a Bode sketch.",
                r"Second engineering use: **small signals**. A device with a curved characteristic, wiggled slightly about an operating point, behaves like the tangent there — and a straight line through an operating point on a current-against-voltage plot is a resistance. A diode passing 4.4 mA looks like 5.8 Ω to a signal small enough not to leave the tangent.",
                r"Both uses share one caution: an approximation is a claim about a region, not about a point. Quote the region — *below a tenth of the corner*, *for swings under a millivolt* — or the next person will use it where it is wrong.",
            ],
            "read": [
                {
                    "title": "Zoom in far enough and the curve is a straight line",
                    "minutes": 16,
                    "body": r'''
Take any smooth curve — the voltage climbing on a charging capacitor, a diode's current
against its voltage, the gain of a filter against frequency — put it on a screen, and zoom
in on one point of it. Not a little: keep going. The curve straightens. Somewhere on the way
in, the bend stops being visible, and what is left on the screen is a straight line that no
amount of squinting will find a kink in. Zoom back out and the bend is obviously still
there. Nothing about the function changed. What changed is how much of it you were looking
at.

That is the whole idea of this module. It is a claim about **smooth** functions inside
**small** windows, and both halves of that matter: a square wave does not straighten when
you zoom in on its edge, and a sine does not look straight if the window is a whole cycle
wide. Everything below is about turning "small enough" from a feeling into a number.

## Building the straight line, and then the next one

Say you want a polynomial that behaves like $f$ near the point $x = a$. Write it in powers
of $(x-a)$ rather than powers of $x$, because $(x-a)$ is the thing that is small:

$$p(x) = c_0 + c_1(x-a) + c_2(x-a)^2 + c_3(x-a)^3 + \cdots$$

Now demand that $p$ agrees with $f$ at $a$ — not just in value, but in slope, in curvature,
in everything you can measure at that one point. Each demand pins down exactly one
coefficient, and it does so because setting $x = a$ annihilates every term that still has a
factor of $(x-a)$ in it.

Put $x = a$ straight away. Every term dies except the first, so $p(a) = c_0$, and matching
values forces $c_0 = f(a)$.

Differentiate once: $p'(x) = c_1 + 2c_2(x-a) + 3c_3(x-a)^2 + \cdots$. Put $x = a$ again and
only $c_1$ survives, so matching slopes forces $c_1 = f'(a)$.

Differentiate again: $p''(x) = 2c_2 + 6c_3(x-a) + \cdots$, so $p''(a) = 2c_2$ and
$c_2 = f''(a)/2$. Once more gives $p^{(3)}(a) = 6c_3$, so $c_3 = f^{(3)}(a)/6$. The factors
1, 2, 6, 24 are the factorials, arriving because differentiating $(x-a)^k$ $k$ times brings
down $k$, then $k-1$, and so on. The general coefficient is $c_k = f^{(k)}(a)/k!$, and what
you have is **Taylor's approximation**:

$$f(x) \approx f(a) + f'(a)(x-a) + \frac{f''(a)}{2}(x-a)^2 + \frac{f^{(3)}(a)}{6}(x-a)^3 + \cdots$$

Notice that nothing was guessed. The coefficients were *forced* by the demand that the
polynomial and the function agree at one point to as many derivatives as you care to name.
Keep one term and you have a constant. Keep two and you have the tangent line — the straight
line the screen showed when you zoomed in. Keep three and you have a parabola that also
bends the right way.

## The three expansions this course keeps meeting

Expand about $a = 0$, which is where the algebra is tidiest. The exponential is its own
derivative, so every derivative at zero is $e^0 = 1$ and every coefficient is $1/k!$:

$$e^x = 1 + x + \frac{x^2}{2} + \frac{x^3}{6} + \frac{x^4}{24} + \cdots$$

The sine's derivatives cycle $\sin, \cos, -\sin, -\cos$, which at zero are $0, 1, 0, -1$, so
the even coefficients all vanish:

$$\sin x = x - \frac{x^3}{6} + \frac{x^5}{120} - \cdots$$

The cosine's cycle starts one step along, $1, 0, -1, 0$, so the odd coefficients vanish
instead:

$$\cos x = 1 - \frac{x^2}{2} + \frac{x^4}{24} - \cdots$$

That the sine has only odd powers and the cosine only even ones is not a coincidence to
memorise; it is $\sin(-x) = -\sin x$ and $\cos(-x) = \cos x$ written in another alphabet.

## Worked example: a charging capacitor is a ramp to begin with

A 3.3 V supply is switched onto 2.2 kΩ in series with 100 nF, and the output is taken across
the capacitor. The exact answer, from module 4, is $v(t) = 3.3\left(1 - e^{-t/\tau}\right)$
with $\tau = RC$. What is the voltage 11 µs after the switch closes?

Use $e^{-x} \approx 1 - x$, so $1 - e^{-x} \approx x$: for a short enough time the capacitor
charges along a straight ramp.

```
tau            = 2.2e3 ohm * 100e-9 F        = 220 us
x = t / tau    = 11 us / 220 us              = 0.0500
ramp estimate  = 3.3 V * 0.0500              = 0.16500 V
exact          = 3.3 * (1 - e^-0.05)
               = 3.3 * 0.0487706             = 0.16094 V
error          = 0.16500 - 0.16094           = 0.00406 V
first term dropped: 3.3 * x^2/2              = 0.00413 V
```

The ramp is 0.004 V high, and the term thrown away predicted 0.004 V. They agree to within
2% of themselves, which is what "the error is the first term you dropped" means in practice.

The relative version is worth keeping in your head. The exact series is
$1 - e^{-x} = x - x^2/2 + \cdots$, so the ramp overstates the voltage by a fraction of about
$x/2$: **half the elapsed fraction of a time constant**. At 5% of a time constant the ramp
is 2.5% high, and indeed $0.00406/0.16094 = 2.52\%$. At 1% of a time constant it is 0.5%
high. That single sentence is why an oscilloscope trace of the first tenth of an RC charge
looks like a straight line, and why timing circuits that use only the first stretch of the
curve are the easy ones to design.

## Worked example: why a small phase error costs almost no amplitude

Two signals meant to be aligned are 5° apart, and the useful output is the projection of one
on the other — the cosine of the angle. How much amplitude is lost?

```
x         = 5 deg = 5*pi/180                 = 0.0872665 rad
x^2/2                                        = 0.0038077
1 - x^2/2                                    = 0.9961923
cos(5 deg), exactly                          = 0.9961947
shortfall 1 - cos                            = 0.0038053
```

The loss is 0.38% — 0.033 dB, which no instrument in a first-year lab will resolve. Compare
that with a 5% amplitude error, which costs, unsurprisingly, 5%. The difference is the shape
of the two functions at the point in question: amplitude enters linearly, but the cosine is
**flat** at its peak, so its leading correction is quadratic and a small angle is squared
before it can do any damage.

The quadratic dependence is testable. Double the misalignment to 10° and the loss should go
up by four, not by two: $1 - \cos 10° = 0.015192$, against $4 \times 0.0038053 = 0.015221$.
It does. And the same flatness works against you when you try to *measure* an angle near
zero by looking at a cosine, because a quantity that barely changes is a quantity you cannot
read.

## The error is the size of the first term you dropped

That claim has now been used twice, so here it is on its own, on the exponential:

```
x = 0.10 :  e^x = 1.1051709,  1+x = 1.10,  error = 0.0051709,  x^2/2 = 0.00500
x = 0.05 :  e^x = 1.0512711,  1+x = 1.05,  error = 0.0012711,  x^2/2 = 0.00125
ratio of the two errors = 0.0051709 / 0.0012711 = 4.07
```

Halving $x$ divided the error by four, because the leading dropped term is quadratic. Keep
three terms instead and the leading dropped term is cubic, and halving $x$ would divide the
error by about eight. This is the difference between an approximation and a guess: an
approximation comes with an estimate of its own error, and that estimate tells you what to
do if it is too big.

## The mistake people actually make

The first one is degrees. $\sin x \approx x$ is simply false if $x$ is in degrees:
$\sin 5° = 0.0872$, and 5 is not 0.0872. The reason is buried in the derivation — the
coefficients came from differentiating, and $\frac{d}{dx}\sin x = \cos x$ only holds when
$x$ is measured in radians. In degrees the derivative carries a factor of $\pi/180$ and
every coefficient changes. It is tempting to forget because the calculator will happily
work in either, and the formula does not carry its units on its face.

The second, and the more damaging, is quoting an approximation with no region attached.
"$\sin x = x$" written on a whiteboard with nothing beside it is not a true statement; it is
a true statement with its most important half deleted. An approximation is a claim about a
neighbourhood, and the neighbourhood is part of the claim. Write *for $x$ below about 0.2
rad, where the error stays under 1%* and the next person can use it safely. Write the bare
identity and they will use it at 1.5 rad, because you gave them no reason not to.

## Where it stops holding, and what replaces it

**The window gets too wide.** At $x = 1.5$ rad the small-angle rule says 1.5 and the sine is
0.99749: an error of 50%. The fix is not to abandon Taylor but to expand about a point near
where you are actually working. Build the approximation about $a = \pi/2$, where
$\sin a = 1$ and $\sin' a = 0$, so the first surviving correction is quadratic:
$\sin x \approx 1 - \frac{(x - \pi/2)^2}{2}$.

```
a          = pi/2                            = 1.5707963
x - a      = 1.5 - 1.5707963                 = -0.0707963
(x-a)^2/2                                    =  0.0025061
1 - (x-a)^2/2                                =  0.9974939
sin(1.5), exactly                            =  0.9974950
error                                        =  1.0e-6
```

One part in a million, from two terms, for the same function that a moment ago was 50%
wrong. The lesson is that "approximation" is never a property of a function alone; it is a
property of a function *and a point*.

**The function is not smooth.** A rectifier at its crossing, a comparator at its threshold,
$|x|$ at the origin: no tangent exists, so there is nothing to keep the first two terms of.
What replaces the tangent there is a piecewise description — one straight line on each side —
and the crossing itself has to be handled as an event rather than as a value.

**The series only converges nearby.** $\frac{1}{1-x} = 1 + x + x^2 + \cdots$ is exact for
$|x| < 1$ and meaningless at $x = 1$, where the function itself blows up. A series can carry
a radius beyond which adding terms makes things worse, not better, and the pole in the
function is what sets it.

**The operating point moves.** Everything here was built at one point. When the supply sags,
the temperature rises or the bias current changes, the tangent you fitted is a tangent
somewhere else, and its slope has changed with it. That is not a failure of the method; it
is the reason the third unit of this module insists that a small-signal answer is quoted
with the operating current it was taken at.
''',
                },
                {
                    "title": "One term of the binomial, and what a tolerance costs",
                    "minutes": 15,
                    "body": r'''
Open a bag of 1% resistors marked 10 kΩ and you have a bag of parts somewhere between
9.90 kΩ and 10.10 kΩ. Nothing in the design is going to be built from the marked value,
because no such resistor exists. So the practical question is never "what does the circuit
do at 10.000 kΩ" but "how far does the answer move when the resistor moves by 1%", and that
question is answered by one term of a series.

You could of course just recompute the whole formula with 9.9 kΩ and again with 10.1 kΩ.
People do, and for one component it is fine. It stops being fine the moment there are six
components, each of which can go either way, because that is 64 recomputations to find a
worst case and none of them tells you *which* component was to blame. The first-order rule
tells you that in one line per component, and it is the sensitivity — not the recomputed
number — that tells you where to spend money on a tighter part.

## The rule

Apply the machinery of the previous unit to $f(x) = (1+x)^n$, about $x = 0$. The value there
is $f(0) = 1$. The derivative is $f'(x) = n(1+x)^{n-1}$, so $f'(0) = n$. Two terms:

$$(1+x)^n \approx 1 + nx \qquad \text{for } |x| \ll 1$$

The next derivative is $f''(x) = n(n-1)(1+x)^{n-2}$, so $f''(0) = n(n-1)$ and the first term
dropped is $\frac{n(n-1)}{2}x^2$. Keep that expression; it is the error estimate, and it is
the thing that decides later whether one term was enough.

The rule is worth more than it looks, because $n$ is unrestricted. Whole, fractional,
negative — the same line covers a whole family:

```
n =  2   (1+x)^2      ~  1 + 2x        a squared quantity doubles the change
n =  3   (1+x)^3      ~  1 + 3x        a cubed one triples it
n = 1/2  sqrt(1+x)    ~  1 + x/2       a square root halves it
n = -1   1/(1+x)      ~  1 - x         a denominator reverses it
n = -1/2 1/sqrt(1+x)  ~  1 - x/2       reverses and halves
```

Read the right-hand column and the rule stops being algebra and becomes a sentence:
**a fractional change is multiplied by the exponent it sits under.**

## Fractional changes add

That sentence extends to a whole formula. Suppose $y = AB$ and both factors move: $A$ by a
fraction $\alpha$, $B$ by a fraction $\beta$. Then

$$y(1 + \delta) = A(1+\alpha)\,B(1+\beta) = AB\left(1 + \alpha + \beta + \alpha\beta\right)$$

so $\delta = \alpha + \beta + \alpha\beta$. If $\alpha$ and $\beta$ are each around a
percent, $\alpha\beta$ is around a hundredth of a percent, and dropping it costs nothing.
Fractional changes **add** across a product. A quotient subtracts, being a product with
$n = -1$, and a power multiplies. Putting the three together, for
$y = A^p B^q$,

$$\frac{\delta y}{y} \approx p\,\frac{\delta A}{A} + q\,\frac{\delta B}{B}$$

This is the single most-used piece of mathematics in a component-tolerance calculation, and
it is one line of binomial expansion.

## Worked example: the corner of an RC filter

$f_c = \dfrac{1}{2\pi RC}$, so $f_c \propto R^{-1}C^{-1}$: both exponents are $-1$. Suppose
the resistor comes in 1% high and the capacitor 2% low.

```
exponent of R is -1 :  (-1) * (+0.01)  = -0.01
exponent of C is -1 :  (-1) * (-0.02)  = +0.02
sum                                    = +0.01   ->  fc is 1% high

exact:  1 / (1.01 * 0.98) = 1 / 0.9898 = 1.010305  ->  1.031% high
```

Read the two contributions physically before believing the arithmetic. A resistor that is
too big slows the charging, so it pulls the corner **down**. A capacitor that is too small
speeds it up, so it pushes the corner **up**. The capacitor is further out of tolerance than
the resistor, so up wins, and the corner lands about 1% high. Getting that sign right by
thinking is worth more than getting it right by symbol-pushing, because the thinking also
catches a mis-copied exponent.

The exact answer is 1.031% and the rule said 1.000%. The gap of 3 parts in $10^4$ is the
size of the dropped terms, which are quadratic in changes of order $10^{-2}$ — exactly as
advertised.

## Worked example: a square root, and a change too big for one term

$f_n = \dfrac{1}{2\pi\sqrt{LC}}$, so $f_n \propto L^{-1/2}C^{-1/2}$. Take an inductor 5% high
and a capacitor 10% low — plausible numbers, since 10% capacitors are ordinary.

```
exponent of L is -1/2 :  (-0.5) * (+0.05)  = -0.025
exponent of C is -1/2 :  (-0.5) * (-0.10)  = +0.050
sum                                        = +0.025  ->  2.5% high

exact:  1 / sqrt(1.05 * 0.90) = 1 / 0.9721111 = 1.028690  ->  2.87% high
```

Now the rule is out by 0.37 percentage points, and on a 2.5% prediction that is a seventh of
the answer. Nothing has gone wrong; the error estimate said this would happen. The largest
term dropped is $\frac{n(n-1)}{2}x^2$ with $n = -\frac12$ and $x = -0.10$, which is
$\frac{3}{8}(0.10)^2 = 0.375\%$ — and the observed discrepancy is 0.369%. The first-order
rule has told you both the answer and the fact that the answer is not quite good enough.

Shrink the changes and it recovers immediately. With the inductor 2% high and the capacitor
3% low the rule predicts $-0.5(0.02) - 0.5(-0.03) = +0.5\%$, and the exact value is
$1/\sqrt{1.02 \times 0.97} = 1.005343$, or 0.534%. A gap of three parts in $10^4$ again.

## Worked example: what a load does to a divider

A 10 V supply feeds two 10 kΩ resistors in series, and the output is the junction. Unloaded
it sits at 5.000 V. Now hang a 1 MΩ load on it — a voltmeter, or the input of the next
stage. How much does the output drop?

Do the algebra once, in conductances, at the output node. Current in through $R_1$ equals
current out through $R_2$ and $R_L$:

$$\frac{V - v}{R_1} = \frac{v}{R_2} + \frac{v}{R_L}
\qquad\Longrightarrow\qquad
v = \frac{V/R_1}{\frac{1}{R_1} + \frac{1}{R_2} + \frac{1}{R_L}}$$

Delete the load, and the same expression gives the unloaded output $v_0$. Dividing one by
the other, everything cancels except one ratio:

$$\frac{v}{v_0} = \frac{\frac{1}{R_1}+\frac{1}{R_2}}{\frac{1}{R_1}+\frac{1}{R_2}+\frac{1}{R_L}}
= \frac{1}{1 + R_{\text{th}}/R_L}
\qquad\text{where } R_{\text{th}} = R_1 \parallel R_2$$

That is exact, and it is already the shape the binomial rule wants: $1/(1+x)$ with
$x = R_{\text{th}}/R_L$. So for a load much larger than the source resistance,

$$v \approx v_0\left(1 - \frac{R_{\text{th}}}{R_L}\right)$$

```
v0    = 10 * 10k / (10k + 10k)     = 5.0000 V
Rth   = 10k || 10k                 = 5.000 kohm
x     = Rth / RL = 5k / 1M         = 0.00500
droop = v0 * x                     = 0.0250 V
v     ~ 5.0000 - 0.0250            = 4.9750 V
exact = 5 / 1.005                  = 4.97512 V
```

The rule is out by 0.12 mV. And it has left behind something better than a number: the
**fractional droop is the ratio of the source resistance to the load**. A divider built from
10 kΩ parts loses a part in 200 into a 1 MΩ load and a part in 20 into a 100 kΩ one. You can
now size a divider without solving it again — which is what an approximation is for.

Push it too far and it degrades on schedule. With a 100 kΩ load, $x = 0.05$, the rule gives
4.750 V and the exact answer is 4.7619 V: 0.25% out, which is $x^2$, as promised.

## The mistake people actually make

The sign, and it is tempting for a good reason. Everybody knows that a bigger resistor makes
a slower filter, and everybody can also see the $R$ sitting in $f_c = 1/(2\pi RC)$. Under
time pressure the second observation wins and the sentence "the resistor is 1% high so the
corner is 1% high" gets written down. It is the exponent that carries the sign, and in a
denominator it is $-1$. Say the physical sentence out loud before you write the number.

The second is subtler and does real damage: applying the rule to a **difference of two
nearly equal quantities**. Two nodes each sitting at 10.00 V, each uncertain by 1%, are each
known to $\pm 0.1$ V — a fine relative accuracy. Their difference is nominally zero and
uncertain by up to $\pm 0.2$ V, which is an infinite relative error. Nothing was done wrong
to either term; it is the subtraction that destroyed the precision. This is why a bridge is
specified by the absolute stability of its arms and not by their percentage tolerance, and
why a first-order sensitivity analysis has to be done on the quantity you actually care
about rather than on the pieces it was built from.

## Where it stops holding

**The change is not small.** The 10% capacitor above. When $\left|\frac{n-1}{2}x\right|$ is
not small compared with 1, keep the quadratic term or compute exactly.

**The first-order sensitivity is zero.** At a maximum — the peak of a tuned response, or the
flat passband of a filter, where the next unit will find $|H| \approx 1 - \frac12 u^2$ — the
derivative vanishes and the rule predicts no change at all. That prediction is right and
useless: the real dependence is quadratic, so you have to keep the next term to see
anything. A sensitivity of zero is a signal to expand further, not a licence to stop.

**Tolerances that are not independent.** All of the above concerns worst cases, where every
part is assumed to go wrong in the same direction at once. Real parts from one reel are
correlated, and parts from different reels are not, and the arithmetic for combining
independent tolerances is different again. That is a question about statistics rather than
about approximation, and it is the subject of module 10.
''',
                },
                {
                    "title": "Two places the tangent earns its living",
                    "minutes": 15,
                    "body": r'''
The last two units built the machinery. This one spends it, on the two approximations a
practising engineer uses most often: the straight lines that a frequency response is drawn
with, and the straight line that turns a curved device into a resistor.

## A response drawn with a ruler

A first-order low-pass filter has magnitude

$$|H| = \frac{1}{\sqrt{1 + u^2}}, \qquad u = \frac{f}{f_c}$$

which is a perfectly good formula and a nuisance to sketch. So look at what it does in two
places where one of the two terms under the root dominates.

**Well below the corner**, $u \ll 1$, so $u^2$ is very small indeed and the binomial rule
applies with $n = -\frac12$ and $x = u^2$:

$$|H| = (1 + u^2)^{-1/2} \approx 1 - \tfrac12 u^2$$

At a tenth of the corner that correction is $\frac12(0.1)^2 = 0.5\%$. The response is flat,
and flat to better than the tolerance of the parts that built it.

**Well above the corner**, $u \gg 1$, the same expansion is useless, because $u^2$ is now
enormous. The move that rescues it is to take the large quantity out of the root first:

$$\sqrt{1+u^2} = u\sqrt{1 + \frac{1}{u^2}}
\qquad\Longrightarrow\qquad
|H| = \frac{1}{u}\left(1 + \frac{1}{u^2}\right)^{-1/2} \approx \frac{1}{u}\left(1 - \frac{1}{2u^2}\right)$$

Now the small quantity is $1/u^2$, and the leading term is simply $|H| \approx 1/u$. On
logarithmic axes that is a straight line of slope $-1$: every factor of ten in frequency
costs a factor of ten in amplitude, which is $-20$ dB per decade. Two straight lines — one
flat, one falling — meeting where $1 = 1/u$, that is, at $u = 1$: the corner.

How wrong are they? The ratio of asymptote to exact value is $\sqrt{1+u^2}$ below the corner
and $\sqrt{1+u^2}/u$ above it, and those two are the same number under $u \to 1/u$, so the
picture is symmetric about the corner on a log axis:

```
u = f/fc     exact |H|     asymptote     asymptote too high by
  0.1        0.99504        1            0.043 dB
  0.5        0.89443        1            0.969 dB
  1.0        0.70711        1            3.010 dB
  2.0        0.44721        0.5          0.969 dB
 10          0.09950        0.1          0.043 dB
```

The worst error in the whole sketch is 3 dB, and it happens at one known place. That is why
a Bode magnitude sketch is drawn with a ruler and then corrected by hand at exactly one
point, and why the corner frequency is *defined* at $-3$ dB rather than at some rounder
number: the definition is chosen so that the correction to the ruler is the same 3 dB for
every first-order corner there has ever been.

### Worked example

A filter corners at 2.00 kHz and is driven with 1.00 V.

```
at 6 kHz:   u = 6.00/2.00 = 3.00
  asymptote  |H| = 1/3      = 0.3333   ->  -9.54 dB   ->  333.3 mV
  exact      1/sqrt(1+9)    = 0.31623  -> -10.00 dB   ->  316.2 mV
  the ruler is 0.46 dB optimistic: 17 mV in 316

at 20 kHz:  u = 20.0/2.00 = 10.0
  asymptote  1/10           = 0.1000   -> -20.00 dB   ->  100.0 mV
  exact      1/sqrt(101)    = 0.09950  -> -20.04 dB   ->   99.5 mV
  the ruler is 0.04 dB optimistic: 0.5 mV in 100
```

Whether either error matters is a question about the job, not about the mathematics. Half a
millivolt in a hundred is nothing at all if you are budgeting how much of a switching spur
survives to the output. It is a great deal if the filter sits in front of a calibration
reference, where a decade of margin is being traded for a tenth of a percent of accuracy.
Say which you are doing, and the tolerance answers itself.

## The tangent as a resistance

The second use is the one that makes the rest of electronics possible.

A resistor obeys $i = v/R$: a straight line through the origin, and the slope is the whole
story. A diode does not. Its current is

$$i = I_S\left(e^{v/V_T} - 1\right)$$

with $V_T = kT/q = 25.7$ mV at 25 °C, and that curve is nothing like a straight line — over
a swing of 60 mV the current changes by a factor of ten. Yet a diode in a working circuit is
routinely replaced by a resistor of a few ohms, and the answers come out right. The reason
is the picture from the first unit: pick an operating point on the curve, zoom in far
enough, and what is left is a straight line.

Differentiate the diode equation:

$$\frac{di}{dv} = \frac{I_S}{V_T}e^{v/V_T} = \frac{i + I_S}{V_T} \approx \frac{I}{V_T}$$

the last step because a forward-conducting diode carries a current enormously larger than
$I_S$. The slope of the tangent is a current divided by a voltage, which is a conductance,
so its reciprocal is a resistance:

$$r = \frac{dv}{di} = \frac{V_T}{I}$$

Note carefully which way that runs: $r$ is **inversely** proportional to the operating
current. More current, less resistance.

```
I = 1.00 mA :  r = 25.7 mV / 1.00 mA = 25.7 ohm
I = 4.40 mA :  r = 25.7 mV / 4.40 mA =  5.84 ohm
I = 0.10 mA :  r = 25.7 mV / 0.10 mA =  257  ohm
```

### How small does the signal have to be

Ride a swing $\Delta v$ on top of the operating point and write $\delta = \Delta v/V_T$ —
the swing measured in units of $V_T$, which is the only yardstick the exponential has. The
true change in current is $I\left(e^{\delta} - 1\right)$; the tangent predicts $I\delta$.
Their ratio is $\left(e^{\delta} - 1\right)/\delta$, which expands to
$1 + \delta/2 + \delta^2/6 + \cdots$:

```
   dv       d = dv/VT     true swing / linear swing
 1.00 mV      0.039              1.020     2.0% high
 2.57 mV      0.100              1.052     5.2% high
 5.14 mV      0.200              1.107    10.7% high
25.7  mV      1.000              1.718      72% high
```

So "small signal" across a diode junction means *a few millivolts*, and $V_T$ is the
yardstick that says how few. That is not a vague caution; it is the reason a bipolar
transistor stage's input is kept to a few millivolts if you want low distortion, and the
reason the same stage works beautifully as a mixer if you do not.

### The mistake people actually make

Having computed 5.84 Ω, it is very tempting to use it to find the voltage across the diode:
$4.4\text{ mA} \times 5.84\,\Omega = 25.7$ mV. That is wrong by a factor of nearly thirty —
the diode is sitting at something like 0.7 V. The small-signal resistance describes how the
voltage *changes* when the current changes; it says nothing whatever about where the
operating point is. Geometrically, the tangent has an intercept, and the intercept is the
part that got thrown away: extending the tangent back to $i = 0$ lands at $V_0 - V_T$,
about 0.67 V for a diode operating at 0.7 V. That intercept is exactly the "0.7 V in series
with a small resistance" model, and it is the same approximation written out honestly.

The temptation is structural rather than careless. Everywhere else in a first course,
"resistance" means $v/i$ — the ratio — and here it means $dv/di$ — the slope. For a straight
line through the origin those are the same number, which is why nobody has had to
distinguish them before, and why the habit of not distinguishing them survives until it
meets a curve.

## Where both of these stop

The asymptote fails near the corner, by a known and bounded 3 dB, and it fails completely
for anything of second order or higher, where the corner region can peak instead of sagging
and the two straight lines miss by however much the resonance says.

The small-signal resistance fails as soon as the swing is comparable to $V_T$. What appears
first is the quadratic term, which produces a component at twice the input frequency and a
shift in the average current — distortion in an amplifier, and the entire operating
principle of a detector. It also fails whenever the operating point drifts, and $V_T$ itself
is proportional to absolute temperature, so a stage whose gain depends on $r$ has a gain
that depends on how warm it is. What replaces it in all three cases is the exponential
itself, solved numerically — which is the business of the next module, because
$i = I_S(e^{v/V_T}-1)$ with a resistor in series is an equation that will not rearrange.

There is a closing joke in this course's own simulator worth noticing. The solver behind
every schematic here handles resistors, capacitors, inductors and sources, and refuses
diodes and transistors outright, because it has no iteration in it. What a small-signal
model does is convert a circuit full of curved devices into precisely the class of circuit
this solver *can* do. That is not a limitation being worked around; it is the reason linear
circuit analysis is worth learning at all.
''',
                },
            ],
            "tune": {
                "title": "A corner chosen with two approximations",
                "minutes": 10,
                "brief": r'''
A sensor gives you a 100 Hz signal you must not spoil, sitting under a 10 kHz
interferer you must remove. One resistor and one capacitor is all you get, so there
is one number to choose: the corner frequency.

Do not solve the exact expression. Use the two approximations from this module:

* well **below** the corner, $|H| = (1 + (f/f_c)^2)^{-1/2} \approx 1 - \frac{1}{2}(f/f_c)^2$
  by the binomial rule — near enough to 1 to call it 1 for most purposes, but it is
  that small shortfall the 99% requirement bites on, so it is the first-order term,
  not the flat 1, that gives you a lowest corner at all;
* well **above** the corner, $|H| \approx f_c/f$ — the rejection is the ratio of
  frequencies.

Those give you the lowest corner that keeps the signal and the highest corner that
kills the interferer. If the two overlap, any corner inside the window works, and the
panel measures your circuit with the exact expression to check that the approximation
did not mislead you.
''',
                "prompt": r"Keep at least 99% of the 100 Hz signal, and put the 10 kHz interferer at least 21 dB down.",
                "note": "The two constraints pull the corner in opposite directions. Both are read from the panel, and both must hold at once.",
                "model": "rc-lowpass",
                "initial": {"r": 1000, "c": 100},
                "plotKey": "fc",
                "constraints": [
                    {"k": "keep", "label": "at least 0.99 of the 100 Hz signal survives", "min": 0.99},
                    {"k": "reject", "label": "10 kHz interferer at −21 dB or lower", "max": -21.0},
                ],
            },
            "quiz": {
                "title": "How wrong is the first term",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"The small-angle rule says $\sin x \approx x$. At $x = 0.1$ radians, roughly how big is the error?",
                        "opts": ["About 0.00017", "About 0.005", "About 0.1", "Exactly zero"],
                        "a": 0,
                        "why": (
                            r"The first dropped term is $x^3/6 = 0.001/6 = 0.000167$, and the true error is 0.000167. "
                            r"The error of an approximation is the first term you threw away — which is why the rule is "
                            r"quoted with a range of validity rather than as an identity. The 0.005 figure is $x^2/2$, "
                            r"the error of the *cosine* approximation at the same angle."
                        ),
                    },
                    {
                        "q": r"Use $(1+x)^n \approx 1 + nx$ to estimate $1.02^3$.",
                        "opts": ["1.02", "1.06", "1.08", "3.06"],
                        "a": 1,
                        "why": (
                            r"$n = 3$ and $x = 0.02$, so the estimate is $1 + 0.06 = 1.06$. The exact value is 1.06121, "
                            r"so the approximation is 0.11% low — near enough for any resistor tolerance calculation "
                            r"and reached without a calculator. Multiplying the percentage by the power is the whole "
                            r"content of the rule."
                        ),
                    },
                    {
                        "q": r"You halve $x$. What happens to the error of the two-term approximation $e^x \approx 1 + x$?",
                        "opts": ["It halves", "It falls by about four", "It is unchanged", "It falls by about eight"],
                        "a": 1,
                        "why": (
                            r"The first dropped term is $x^2/2$, which is quadratic in $x$, so halving $x$ divides the "
                            r"error by about four. Measured: at $x = 0.1$ the error is 0.00517 and at $x = 0.05$ it is "
                            r"0.00127, a ratio of 4.07. A factor of eight would be the behaviour of the *three*-term "
                            r"approximation, whose first dropped term is cubic."
                        ),
                    },
                    {
                        "q": r"For small $x$, $\dfrac{1}{1+x}$ is approximately:",
                        "opts": [r"$1 + x$", r"$1 - x$", r"$1 - x^2$", r"$x - 1$"],
                        "a": 1,
                        "why": (
                            r"It is the binomial rule with $n = -1$: $1 + (-1)x = 1 - x$. Check it at $x = 0.05$: the "
                            r"exact value is 0.95238 and the approximation gives 0.95, low by a quarter of a percent. "
                            r"$1 + x$ has the sign backwards, and would say that loading a divider *raises* its output."
                        ),
                    },
                    {
                        "q": r"Why can a diode be replaced by a resistance when the signal riding on it is small?",
                        "opts": [
                            "Because a diode is really a resistor with a threshold",
                            "Because the exponential is nearly straight everywhere",
                            "Because over a small enough swing the curve is its own tangent, and a straight line through the operating point is a resistance",
                            "Because the current is small, so the voltage across it is negligible",
                        ],
                        "a": 2,
                        "why": (
                            r"The tangent at the operating point is $i \approx I + \frac{di}{dv}\Delta v$, and a fixed "
                            r"ratio of current change to voltage change is exactly what a resistance is. Nothing is "
                            r"being claimed about the exponential away from that point — it is emphatically not "
                            r"straight, which is why the replacement is valid only for small swings and why the "
                            r"resistance changes the moment the operating current does."
                        ),
                    },
                    {
                        "q": r"One decade above its corner a first-order filter has $|G| = 1/\sqrt{101} = 0.09950$, and the asymptote says 0.1. How wrong is the asymptote there?",
                        "opts": ["About 0.5%", "About 5%", "About 10%", "About 0.05%"],
                        "a": 0,
                        "why": (
                            r"$0.1/0.09950 = 1.00499$, so the straight line is half a percent high — 0.04 dB, which no "
                            r"first-year instrument resolves. That is why Bode sketches are drawn with a ruler and "
                            r"corrected only at the corner itself, where the error reaches its largest value of 3 dB."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "The six approximations worth memorising",
                "minutes": 9,
                "caption": "each line keeps the first two terms of a series about x = 0",
                "lang": "text",
                "brief": r'''
These six lines cover most of the approximating anybody does with a circuit in front
of them. Every one of them is the same move — keep the constant term and the term in
$x$, throw the rest away — so the answers are shorter than they look.

Nothing is executed here. The symbol `~` means *approximately equal to for small*
$|x|$, and `**` is a power, as in Python.
''',
                "listing": """exp(x)         ~   1 + ___

sin(x)         ~   ___

cos(x)         ~   1 - ___

(1 + x)**n     ~   1 + ___

1 / (1 + x)    ~   1 - ___

sqrt(1 + x)    ~   1 + ___
""",
                "blanks": [
                    {
                        "prompt": "The exponential, to two terms.",
                        "hole": "?",
                        "opts": ["x**2", "x", "x/2", "2*x"],
                        "a": 1,
                        "why": "The series is $1 + x + x^2/2 + \\cdots$, so the second term is $x$ itself: the slope of $e^x$ at zero is 1. Everything else in this list is a consequence of that one fact.",
                        "whys": [
                            "That is the *third* term without its $1/2$. Including it would be a better approximation, but the line asks for the two-term form, and the term in $x$ has to come first.",
                            "The series is $1 + x + x^2/2 + \\cdots$, so the second term is $x$ itself: the slope of $e^x$ at zero is 1. Everything else in this list is a consequence of that one fact.",
                            "A half belongs with the *square* term, not the linear one. With $x/2$ here the approximation would have slope $1/2$ at the origin, and $e^x$ has slope 1.",
                            "This would make the slope 2. The defining property of $e^x$ is that its own slope equals its own value, which at $x = 0$ is 1.",
                        ],
                    },
                    {
                        "prompt": "The sine, to the first term that is not zero.",
                        "hole": "?",
                        "opts": ["1", "x**2/2", "x", "1 - x"],
                        "a": 2,
                        "why": "$\\sin x = x - x^3/6 + \\cdots$: the constant term is zero because $\\sin 0 = 0$, and the first surviving term is $x$. This is the small-angle rule, and its error at 0.1 rad is $0.1^3/6 = 0.00017$.",
                        "whys": [
                            "$\\sin 0 = 0$, so there is no constant term at all. A constant of 1 here is the cosine's opening, not the sine's.",
                            "There is no square term in the sine — the series runs in odd powers only, which is another way of saying $\\sin(-x) = -\\sin x$.",
                            "$\\sin x = x - x^3/6 + \\cdots$: the constant term is zero because $\\sin 0 = 0$, and the first surviving term is $x$. This is the small-angle rule, and its error at 0.1 rad is $0.1^3/6 = 0.00017$.",
                            "This mixes the two: a constant that does not belong and a slope with the wrong sign. The sine climbs away from the origin, it does not fall from 1.",
                        ],
                    },
                    {
                        "prompt": "The cosine, whose leading correction is subtracted.",
                        "hole": "?",
                        "opts": ["x**2/2", "x", "x/2", "x**3/6"],
                        "a": 0,
                        "why": "$\\cos x = 1 - x^2/2 + \\cdots$. The cosine is flat at the origin — its slope there is zero — so there is no term in $x$, and the first correction is quadratic. That flatness is why a small phase error costs so little amplitude.",
                        "whys": [
                            "$\\cos x = 1 - x^2/2 + \\cdots$. The cosine is flat at the origin — its slope there is zero — so there is no term in $x$, and the first correction is quadratic. That flatness is why a small phase error costs so little amplitude.",
                            "A linear term would mean the cosine leaves 1 at a finite slope. It does not: $\\frac{d}{dx}\\cos x = -\\sin x$, which is zero at the origin.",
                            "Same objection, with half the slope: any term in $x$ at all contradicts the cosine being flat at zero.",
                            "That is the sine's first correction. The cosine's series runs in even powers, the sine's in odd ones.",
                        ],
                    },
                    {
                        "prompt": "The binomial, for any power n — whole, fractional or negative.",
                        "hole": "?",
                        "opts": ["x**n", "n + x", "n*x", "n*x**2"],
                        "a": 2,
                        "why": "$(1+x)^n \\approx 1 + nx$: a small fractional change $x$ comes out multiplied by the power. A resistor 1% high, cubed, is 3% high. The whole of the next two lines is this one with $n = -1$ and $n = 1/2$.",
                        "whys": [
                            "This says $(1+x)^n \\approx 1 + x^n$, which fails immediately at $n = 2$: $(1+x)^2 = 1 + 2x + x^2$, and there is no $x^2$ in $1 + x^2$'s linear behaviour to match the $2x$.",
                            "Adding $n$ makes the value wrong even at $x = 0$, where every power of 1 is 1 and the answer must be exactly 1.",
                            "$(1+x)^n \\approx 1 + nx$: a small fractional change $x$ comes out multiplied by the power. A resistor 1% high, cubed, is 3% high. The whole of the next two lines is this one with $n = -1$ and $n = 1/2$.",
                            "A quadratic term cannot be the leading correction: the derivative of $(1+x)^n$ at the origin is $n$, which is not zero, so the first correction is linear.",
                        ],
                    },
                    {
                        "prompt": "The reciprocal — the binomial rule with n = -1.",
                        "hole": "?",
                        "opts": ["x**2", "1/x", "x/2", "x"],
                        "a": 3,
                        "why": "$1/(1+x) \\approx 1 - x$. At $x = 0.05$ the exact value is 0.95238 against the approximation's 0.95: a quarter of a percent low. This is the line behind every statement of the form *a 1% larger load costs 1% of the output*.",
                        "whys": [
                            "A quadratic correction would mean the reciprocal is flat at the origin. Its slope there is $-1$, which is as far from flat as the exponential's.",
                            "$1/x$ blows up at $x = 0$, where the expression is a perfectly well-behaved 1. An approximation must at least agree with the function at the point it is built around.",
                            "Half the correction. This is what you would get from $n = -1/2$, which is $1/\\sqrt{1+x}$, not $1/(1+x)$.",
                            "$1/(1+x) \\approx 1 - x$. At $x = 0.05$ the exact value is 0.95238 against the approximation's 0.95: a quarter of a percent low. This is the line behind every statement of the form *a 1% larger load costs 1% of the output*.",
                        ],
                    },
                    {
                        "prompt": "The square root — the binomial rule with n = 1/2.",
                        "hole": "?",
                        "opts": ["x/2", "x", "x**2/2", "2*x"],
                        "a": 0,
                        "why": "$\\sqrt{1+x} \\approx 1 + x/2$: a 2% change under a square root emerges as 1%. At $x = 0.02$ the exact root is 1.00995 against 1.01, an error of five parts in a hundred thousand — which is why nobody reaches for a calculator to work out how a tolerance passes through $\\sqrt{LC}$.",
                        "whys": [
                            "$\\sqrt{1+x} \\approx 1 + x/2$: a 2% change under a square root emerges as 1%. At $x = 0.02$ the exact root is 1.00995 against 1.01, an error of five parts in a hundred thousand — which is why nobody reaches for a calculator to work out how a tolerance passes through $\\sqrt{LC}$.",
                            "That is the rule for $n = 1$, which is no root at all. A square root always moves less than the thing under it, so the coefficient has to be smaller than 1.",
                            "A quadratic leading term would make the root flat at the origin, and its slope there is $1/2$.",
                            "This doubles the change instead of halving it — the rule for $n = 2$, which is squaring, the opposite operation.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "One decade past the corner, with a ruler",
                    "minutes": 5,
                    "brief": r'''
The most mechanical question this module has: one rule, one unknown, and no exact
expression needed anywhere.

Well above its corner a first-order low-pass has

$$|H| \approx \frac{f_c}{f}$$

so the attenuation is nothing more than a ratio of two frequencies, turned into decibels
with $20\log_{10}$.

The resistor has been chosen to put the corner at $f_c = 1/(2\pi RC) = 999.7$ Hz, so 10 kHz
sits one decade above it to four figures. Work out the ratio first and take the logarithm
last.
''',
                    "prompt": r"Using the high-frequency asymptote, how far below the source is the probed node at 10.0 kHz?",
                    "note": "Answer in decibels, to one decimal place. A signal that has been attenuated is a negative number of decibels. The tolerance is wide enough that the asymptote is an acceptable answer here — part of the exercise is finding out that it is.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1592},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V"},
                        {"label": "R1", "value": "1.592 kΩ"},
                        {"label": "C1, the probed node to ground", "value": "100 nF"},
                        {"label": "Corner", "value": "$f_c = 999.7$ Hz"},
                        {"label": "Asked at", "value": "10.0 kHz"},
                    ],
                    # The solver's own AC magnitude at 10 kHz, divided by the source amplitude the
                    # netlist carries, so the answer follows the schematic rather than a remembered
                    # corner frequency. Nothing on the diagram is restated here.
                    "check": r'''
return 20 * Math.log10(c.gain(1e4) / c.values('V')[0]);
''',
                    "answer": -20.0,
                    "tol": 0.1,
                    "unit": "dB",
                    "hint": r"$f_c/f = 999.7/10\,000$. Take $20\log_{10}$ of that, not $10\log_{10}$ — this is an amplitude ratio, not a power ratio.",
                    "wrong": r"If you got $-3.0$, that is the attenuation at the corner itself, not a decade above it. If you got $-40$, the ratio was squared, or $20\log_{10}$ was applied to $(f_c/f)^2$. If you got $-6.0$, the frequency was taken one *octave* above the corner rather than one decade. If you got $+20$, the ratio was written the other way up: the output is smaller than the input, so the decibel figure is negative.",
                    "why": r'''
```
fc / f       = 999.7 / 10 000            = 0.09997
20 log10     = 20 * (-1.0000)            = -20.00 dB
```

The asymptote says $-20.00$ dB. The exact expression says

```
u        = f/fc = 10 000 / 999.7         = 10.003
|H|      = 1/sqrt(1 + 100.06)            = 0.09948
20 log10                                 = -20.05 dB
```

so the straight line is 0.05 dB optimistic — a part in 200 of amplitude, at a frequency
where the signal has already been cut to a tenth. That is the payoff of the whole module:
a two-symbol calculation you can do in your head, wrong by less than the tolerance of the
capacitor that set the corner in the first place.

Both numbers are inside the stated tolerance, deliberately. An approximation that has to
be quoted with the region it holds in also has to be quoted with the accuracy it holds to,
and a tolerance is where that accuracy gets written down.
''',
                    "aside": "The $-20$ dB is not a coincidence of these components. A first-order response falls at 20 dB per decade forever, so *any* first-order low-pass is 20 dB down one decade above its corner, 40 dB down two decades above, and so on. That is what makes the asymptote worth drawing: it is the same line every time, and only its corner moves.",
                },
                {
                    "title": "What the load costs the divider",
                    "minutes": 8,
                    "brief": r'''
The divider on its own would sit at $V\dfrac{R_2}{R_1+R_2}$. The 470 kΩ load pulls it down,
and rather than re-solving the three-resistor network you can use the exact result from the
second reading unit:

$$\frac{v}{v_0} = \frac{1}{1 + R_{\text{th}}/R_L}
\qquad\text{with}\qquad
R_{\text{th}} = R_1 \parallel R_2$$

and then the binomial rule with $n = -1$, since $R_{\text{th}}/R_L$ here is well under a
percent:

$$v \approx v_0\left(1 - \frac{R_{\text{th}}}{R_L}\right)$$

Three steps: the unloaded output, the source resistance seen looking back into the junction,
and the fractional droop.
''',
                    "prompt": r"What voltage does the probed node actually sit at?",
                    "note": "Answer in volts, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 10000},
                            {"id": "rl", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 470000},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "g2", "kind": "GND", "x": 12, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 4], "b": [12, 4]},
                            {"a": [12, 4], "b": [12, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [12, 7], "b": [12, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "9.00 V"},
                        {"label": "R1 (supply to the probed node)", "value": "4.70 kΩ"},
                        {"label": "R2 (probed node to ground)", "value": "10.0 kΩ"},
                        {"label": "RL, the load (probed node to ground)", "value": "470 kΩ"},
                    ],
                    # The probed node is the one unknown of the network, so the solver's own DC
                    # operating point is the answer with nothing added to it — and it is computed
                    # from the three resistors as drawn, not from the approximation the brief
                    # recommends, which is the point of comparing them.
                    "check": r'''
return c.vout();
''',
                    "answer": 6.081,
                    "tol": 0.005,
                    "unit": "V",
                    "hint": r"$R_{\text{th}} = 4.70\parallel10.0$ kΩ is a little over 3.1 kΩ, and dividing that by 470 kΩ gives a droop of well under a percent. Apply that fraction to the unloaded 6.122 V.",
                    "wrong": r"If you got 6.122, the load was ignored — that is the unloaded divider, and it is the answer this question exists to rule out. If you got 5.992, the droop was computed against $R_2$ alone, and if you got 6.061, against $R_1$ alone; the source resistance seen by the load is the *parallel* combination of the two, because an ideal supply is a short circuit as far as the load can tell. If you got 8.913, the load was put in series with $R_2$ instead of across it.",
                    "why": r'''
```
v0    = 9.00 * 10.0k / (4.70k + 10.0k)      = 6.1224 V
Rth   = 4.70k || 10.0k = 47.0/14.7 kohm     = 3.1973 kohm
x     = Rth / RL = 3197.3 / 470 000         = 0.006803
droop = v0 * x = 6.1224 * 0.006803          = 0.04165 V
v     ~ 6.1224 - 0.0417                     = 6.0808 V
```

The exact answer, from the three-resistor network solved properly, is 6.0811 V. The
approximation is 0.3 mV low, which is 0.005% — far inside the 1% tolerance of any resistor
you would build this from.

What the calculation gives you beyond the number is the *shape* of the dependence. The
droop is $R_{\text{th}}/R_L$, a ratio of resistances, and it does not care about the supply
or about which of $R_1$ and $R_2$ is larger. A 15 kΩ divider loaded by 470 kΩ droops by
0.7%, and it would droop by 0.7% at 9 V or at 90 V. That is a rule you can apply at a bench
without a calculator; the exact expression is not.

The reason $R_{\text{th}}$ is the *parallel* combination and not $R_2$ is worth being sure
of. Looking back into the junction from the load, the ideal 9 V supply has no resistance of
its own, so $R_1$ appears to be connected to ground just as $R_2$ is. The load therefore
sees the two of them in parallel, and that is the resistance that turns the load current
into a voltage drop.
''',
                    "aside": "Turn the rule around and it becomes a design rule: to keep loading under a chosen fraction $\\varepsilon$, make $R_L > R_{\\text{th}}/\\varepsilon$. A 0.1% budget needs a load a thousand times the divider's source resistance — which is why a 10 MΩ oscilloscope probe is still not good enough for a divider built from megohms.",
                },
                {
                    "title": "How long the capacitor takes to reach a tenth",
                    "minutes": 9,
                    "brief": r'''
The supply is connected at $t = 0$ and the capacitor charges as
$v(t) = V\left(1 - e^{-t/\tau}\right)$ with $\tau = RC$.

The question runs the other way: given the voltage, find the time. Write $y = v/V$ for the
fraction of the way there, so that $e^{-t/\tau} = 1 - y$ and

$$\frac{t}{\tau} = \ln\frac{1}{1-y} = y + \frac{y^2}{2} + \frac{y^3}{3} + \cdots$$

which is the series for $-\ln(1-y)$. The first term alone is the straight-line ramp of the
first reading unit, and at $y = 0.1$ it is **not** good enough here — the correction
$y^2/2$ is 5% of the answer, and the tolerance on this question is tighter than that. Keep
terms until the next one no longer moves your third digit.
''',
                    "prompt": r"How long after the supply is connected does the probed node reach 0.500 V — one tenth of the supply?",
                    "note": "Answer in microseconds, to one decimal place. The capacitor starts empty.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 10000},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "5.00 V, connected at $t = 0$"},
                        {"label": "R1", "value": "10.0 kΩ"},
                        {"label": "C1", "value": "100 nF"},
                        {"label": "Target", "value": "0.500 V, a tenth of the supply"},
                    ],
                    # The transient is run and the crossing is found by walking the samples and
                    # interpolating between the two that straddle it. The threshold is a tenth of
                    # the source value the netlist carries, so a redrawn supply moves the target
                    # with it and no constant from the schematic is repeated here.
                    "check": r'''
const s = c.step(2e-4);
const target = c.values('V')[0] / 10;
let i = 1;
while (i < s.v.length && s.v[i] < target) i++;
const t0 = s.t[i - 1], t1 = s.t[i], v0 = s.v[i - 1], v1 = s.v[i];
return 1e6 * (t0 + (target - v0) * (t1 - t0) / (v1 - v0));
''',
                    "answer": 105.4,
                    "tol": 1.0,
                    "unit": "µs",
                    "hint": r"$\tau = 10.0\text{ k}\Omega \times 100\text{ nF} = 1.00$ ms, and $y = 0.500/5.00 = 0.100$. Then $t/\tau = y + y^2/2 + y^3/3$, and everything after that is below the third digit.",
                    "wrong": r"If you got 100.0, only the ramp term was kept: that is the answer the straight line gives, and it is 5% early, which is exactly the error the series predicted. If you got 1000, that is one whole time constant in microseconds — the time to reach 63% of the supply, not 10% of it. If you got 105.4 ms or 0.105 µs, the time constant went in as 1 s or 1 µs — $10^4 \times 10^{-7}$ is $10^{-3}$.",
                    "why": r'''
```
tau      = 10.0e3 * 100e-9                    = 1.000 ms
y        = 0.500 / 5.00                       = 0.1000
t/tau    = y + y^2/2 + y^3/3 + ...
         = 0.1000 + 0.005000 + 0.000333       = 0.105333
t        = 0.105333 * 1.000 ms                = 105.33 us
exact    = tau * ln(1/0.9) = 1.000 ms * 0.1053605  = 105.36 us
```

Three terms land within 0.03 µs of the truth. One term lands 5.4 µs early, and a 5% timing
error is the difference between a circuit that works and one that does not.

The point of the question is the discipline, not the arithmetic. The straight-line ramp was
introduced in the first reading unit with its error attached: it is high on voltage by about
$x/2$, so inverted it is early on time by about $y/2$ — half of 10% is 5%, and the observed
5.4/105.4 is 5.1%. Nothing here was a surprise, because the size of the first dropped term
was known before the exact answer was.

Notice also which way the correction goes. Charging *slows down* as the capacitor fills, so
reaching any given voltage always takes longer than the initial straight line suggests. If
your correction had made the answer smaller, the sign was wrong and the physics would have
said so before the algebra did.
''',
                    "aside": "The same series is behind the rule of thumb that a capacitor is 63% charged after one time constant and 95% after three. Those are $1 - e^{-1}$ and $1 - e^{-3}$, and no series is any use there: at $y$ near 1 the expansion of $-\\ln(1-y)$ is on the edge of its region, which is another way of saying that the far end of a charging curve has to be handled with the logarithm itself.",
                },
                {
                    "title": "The power a load takes from a divider it is spoiling",
                    "minutes": 12,
                    "brief": r'''
The last rung, and it chains four things together. The quantity asked for is not a node
voltage and not any current the solver would hand you directly: it is the power in the load
resistor, which you can only get after working out what the loading has done to the voltage.

The route:

1. the unloaded output $v_0 = V\dfrac{R_2}{R_1+R_2}$;
2. the source resistance seen by the load, $R_{\text{th}} = R_1\parallel R_2$;
3. the loaded output, $v \approx v_0\left(1 - R_{\text{th}}/R_L\right)$;
4. the power, $P = v^2/R_L$.

Step 4 is where the binomial rule earns its keep a second time. Power goes as the *square*
of the voltage, so a fractional error $\varepsilon$ in $v$ becomes $2\varepsilon$ in $P$ —
that is $(1+x)^n$ with $n = 2$. Decide before you start whether your $v$ is good enough to
survive being doubled.
''',
                    "prompt": r"How much power does the 220 kΩ load dissipate?",
                    "note": "Answer in microwatts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 8200},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3300},
                            {"id": "rl", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 220000},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "g2", "kind": "GND", "x": 12, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 4], "b": [12, 4]},
                            {"a": [12, 4], "b": [12, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [12, 7], "b": [12, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "12.0 V"},
                        {"label": "R1 (supply to the probed node)", "value": "8.20 kΩ"},
                        {"label": "R2 (probed node to ground)", "value": "3.30 kΩ"},
                        {"label": "RL, the load", "value": "220 kΩ"},
                        {"label": "Asked for", "value": "the power in RL, in µW"},
                    ],
                    # The load's power is not a node voltage, so it is assembled from two things the
                    # netlist holds: the solved probe voltage, and the load's own value looked up by
                    # id. Redraw either and the check follows.
                    "check": r'''
const v = c.vout();
const rl = c.net.parts.filter(function (p) { return p.id === 'rl'; })[0];
return 1e6 * v * v / rl.value;
''',
                    "answer": 52.76,
                    "tol": 0.3,
                    "unit": "µW",
                    "hint": r"$R_{\text{th}} = 8.20\parallel3.30$ kΩ is a little over 2.3 kΩ, so the droop is about 1%. Work the voltage to four figures before squaring it, because squaring doubles whatever error is in it.",
                    "wrong": r"If you got 53.9, the loading was ignored and the unloaded 3.443 V was squared; that is 2.2% high, which is twice the 1.1% error in the voltage — the squaring at work. If you got 0.0528, the answer is in watts and the question asked for microwatts. If you got 15.5, that is the load *current* in microamps, not the power. If you got 3520, the power was taken as $v^2/R_2$ — the wrong resistor, and the one carrying nearly seventy times the current.",
                    "why": r'''
```
v0    = 12.0 * 3.30k / (8.20k + 3.30k)      = 3.4435 V
Rth   = 8.20k || 3.30k = 27.06/11.5 kohm    = 2.3530 kohm
x     = Rth / RL = 2353.0 / 220 000         = 0.010696
v     ~ 3.4435 * (1 - 0.010696)             = 3.4066 V
P     = v^2 / RL = 11.605 / 220 000         = 5.275e-5 W
                                            = 52.75 uW
```

The exact value is 52.76 µW, from the loaded voltage of 3.4070 V. The first-order rule was
0.4 mV low on the voltage, and squaring turned that into 0.01 µW — still nothing, because
$x = 1.07\%$ and the dropped term is $x^2 = 0.011\%$.

Compare with the answer you get by ignoring the load altogether. That gives 3.4435 V and
53.90 µW, which is 2.2% high. The voltage was only 1.1% wrong; the power is out by twice
that, because $P \propto v^2$ and the exponent multiplies the fractional error. This is the
binomial rule being used not to *get* an answer but to decide how carefully the previous
step had to be done — which is the more valuable of its two jobs.

One sanity check before believing any of it. The load draws $3.41/220\text{k} = 15.5$ µA,
while the divider chain itself carries $12/11.5\text{k} = 1.04$ mA. The load current is
1.5% of the chain current, so the disturbance ought to be of that order, and a 1% droop is.
A first-order correction that came out at 20% would be telling you that the load is not a
perturbation at all and the network has to be solved properly.
''',
                    "aside": "There is a second approximation hiding in the phrase *the source resistance seen by the load*. It treats the 12 V supply as ideal — zero resistance of its own. A real supply with 0.5 Ω of output resistance adds that in series with $R_1$, changing $R_{\\text{th}}$ from 2353.0 Ω to 2353.1 Ω, which moves nothing here. It would move a great deal in a divider built from ohms rather than kilohms, and that is the check to make before assuming it away.",
                },
            ],
            "derive": {
                "title": "The two straight lines a first-order response is drawn with",
                "minutes": 13,
                "vars": ["u", "n", "x", "H"],
                "brief": r'''
A first-order low-pass has magnitude

$$|H| = \frac{1}{\sqrt{1 + u^2}}, \qquad u = \frac{f}{f_c}$$

Nobody sketches that. What gets sketched is two straight lines — one flat, one falling at
20 dB per decade — and a note of how wrong they are near the corner. This derivation
produces both lines and the error, from the binomial rule and nothing else.

Throughout, $(1+x)^n \approx 1 + nx$ for $|x| \ll 1$, and the whole art is choosing which
quantity is playing the part of $x$.
''',
                "steps": [
                    {
                        "prompt": r"Below the corner $u$ is small, so $u^2$ is very small. Apply the binomial rule to $(1+u^2)^{-1/2}$, taking $x = u^2$ and $n = -\frac{1}{2}$, and write the two-term approximation.",
                        "answer": r"1 - u^2/2",
                        "placeholder": r"1 - something",
                        "hint": r"$nx$ is $\left(-\frac12\right)\left(u^2\right)$. Add 1 to it and you are done.",
                        "deconstruct": [
                            r"$|H| = (1+u^2)^{-1/2}$, so $x = u^2$ and $n = -\frac12$.",
                            r"$1 + nx = 1 - \frac{1}{2}u^2$.",
                        ],
                    },
                    {
                        "prompt": r"Above the corner that expansion is worthless, because $u^2$ is now enormous rather than small. Fix it by taking the large factor out of the root: for $u > 0$, rewrite $|H|$ with $u$ pulled outside the square root.",
                        "answer": r"\frac{1}{u\sqrt{1 + 1/u^2}}",
                        "placeholder": r"a factor of 1/u times a root",
                        "hint": r"$1 + u^2 = u^2\left(1 + \frac{1}{u^2}\right)$, and the square root of a product is the product of the square roots.",
                        "deconstruct": [
                            r"Factor $u^2$ out: $1 + u^2 = u^2\left(1 + 1/u^2\right)$.",
                            r"$\sqrt{u^2\left(1+1/u^2\right)} = u\sqrt{1 + 1/u^2}$ for positive $u$.",
                            r"$|H|$ is one over that.",
                        ],
                    },
                    {
                        "prompt": r"Now the small quantity is $1/u^2$. Drop it entirely and write what is left: the high-frequency asymptote.",
                        "answer": r"1/u",
                        "hint": r"With $1/u^2$ set to zero the root becomes $\sqrt{1} = 1$.",
                        "deconstruct": [
                            r"$\sqrt{1 + 1/u^2} \to \sqrt{1} = 1$.",
                            r"What remains is $1/u$ — on log axes, a straight line of slope $-1$.",
                        ],
                    },
                    {
                        "prompt": r"Put one term back. Expand $\left(1 + 1/u^2\right)^{-1/2}$ by the binomial rule and multiply through by the $1/u$ in front.",
                        "answer": r"1/u - 1/(2 u^3)",
                        "placeholder": r"1/u minus a correction",
                        "hint": r"With $x = 1/u^2$ and $n = -\frac12$, the two-term factor is $1 - \frac{1}{2u^2}$. Multiply that by $1/u$.",
                        "deconstruct": [
                            r"$\left(1 + 1/u^2\right)^{-1/2} \approx 1 - \frac{1}{2u^2}$.",
                            r"$\frac{1}{u}\left(1 - \frac{1}{2u^2}\right) = \frac{1}{u} - \frac{1}{2u^3}$.",
                        ],
                    },
                    {
                        "prompt": r"To say how wrong the ruler is, compare the two. Write the ratio of the high-frequency asymptote to the exact magnitude, as a function of $u$.",
                        "answer": r"\sqrt{1+u^2}/u",
                        "placeholder": r"a root over u",
                        "hint": r"Dividing by $|H| = 1/\sqrt{1+u^2}$ is multiplying by $\sqrt{1+u^2}$.",
                        "deconstruct": [
                            r"The ratio is $\dfrac{1/u}{1/\sqrt{1+u^2}}$.",
                            r"Dividing by a fraction inverts it: $\dfrac{\sqrt{1+u^2}}{u}$.",
                        ],
                    },
                    {
                        "prompt": r"Evaluate that ratio one decade above the corner, at $u = 10$.",
                        "answer": r"\sqrt{101}/10",
                        "hint": r"Substitute $u = 10$: the numerator becomes $\sqrt{1 + 100}$.",
                        "deconstruct": [
                            r"$\sqrt{1 + 10^2} = \sqrt{101}$.",
                            r"Divide by $u = 10$.",
                        ],
                    },
                ],
                "closing": r'''
$\sqrt{101}/10 = 1.004988$, so a decade above the corner the ruler is high by half a percent
of amplitude — $20\log_{10}(1.004988) = 0.043$ dB. Nobody's sketch is that good, and no
first-year instrument would show the difference.

Put $u = 1$ into the same ratio and it becomes $\sqrt{2} = 1.414$, which is 3.01 dB. That is
the worst the two straight lines are ever wrong, it happens at exactly one place, and it is
the only correction a hand-drawn magnitude sketch needs.

The last step also explains the symmetry of the picture. Replacing $u$ by $1/u$ in
$\sqrt{1+u^2}/u$ gives $\sqrt{1+u^2}$, which is the error of the *low*-frequency asymptote —
so the two straight lines are wrong by the same amount an octave below the corner as an
octave above it, and the sketch is symmetric about the corner on a logarithmic axis.
''',
            },
            "lab": {
                "title": "Measuring the error of an approximation",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
An approximation is only worth using if you can say how wrong it is. This lab
computes a series, measures its error, and watches that error behave the way the
first dropped term says it should.

Write four functions.

`exp_series(x, n)` returns the sum of the **first n terms** of

$$e^x = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots$$

so `exp_series(x, 1)` is 1 and `exp_series(x, 2)` is $1 + x$. Build each term from
the previous one — the $k$-th term is the $(k-1)$-th multiplied by $x/k$ — rather
than calling a factorial. It is faster, it never overflows, and it is how every
library on earth does it.

`abs_error(x, n)` returns the absolute difference between that sum and `math.exp(x)`.

`linear_binomial(x, n)` returns the two-term binomial approximation $1 + nx$.

`terms_needed(x, tol)` returns the smallest number of terms whose error is at or
below `tol`. Start at one term and add more until it is.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def exp_series(x, n):
    """The sum of the first n terms of the Maclaurin series for e**x."""
    # TODO: run a term along, multiplying by x/k each time.
    return 0.0


def abs_error(x, n):
    """How far exp_series(x, n) is from math.exp(x)."""
    # TODO
    return 0.0


def linear_binomial(x, n):
    """The two-term binomial approximation to (1 + x)**n."""
    # TODO
    return 0.0


def terms_needed(x, tol):
    """The smallest number of terms whose error is <= tol."""
    # TODO
    return 0


if __name__ == "__main__":
    print("e to five terms :", exp_series(1.0, 5), "against", math.e)
    print("error at x=0.1, two terms:", abs_error(0.1, 2), " x*x/2 =", 0.1 * 0.1 / 2)
    print("error at x=0.05, two terms:", abs_error(0.05, 2))
    print("1.02**3 ~", linear_binomial(0.02, 3), " exact", 1.02 ** 3)
    print("terms needed for 1e-6 at x=1:", terms_needed(1.0, 1e-6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def exp_series(x, n):
    """The sum of the first n terms of the Maclaurin series for e**x."""
    total = 0.0
    term = 1.0
    for k in range(n):
        if k:
            term *= x / k
        total += term
    return total


def abs_error(x, n):
    """How far exp_series(x, n) is from math.exp(x)."""
    return abs(exp_series(x, n) - math.exp(x))


def linear_binomial(x, n):
    """The two-term binomial approximation to (1 + x)**n."""
    return 1.0 + n * x


def terms_needed(x, tol):
    """The smallest number of terms whose error is <= tol."""
    n = 1
    while abs_error(x, n) > tol:
        n += 1
    return n


if __name__ == "__main__":
    print("e to five terms :", exp_series(1.0, 5), "against", math.e)
    print("error at x=0.1, two terms:", abs_error(0.1, 2), " x*x/2 =", 0.1 * 0.1 / 2)
    print("error at x=0.05, two terms:", abs_error(0.05, 2))
    print("1.02**3 ~", linear_binomial(0.02, 3), " exact", 1.02 ** 3)
    print("terms needed for 1e-6 at x=1:", terms_needed(1.0, 1e-6))
'''}],
                "hints": [
                    r"Start `term` at 1.0 and `total` at 0.0. On the first pass add the term as it is; on every later pass multiply it by `x / k` first, where `k` is the loop index.",
                    r"`exp_series(x, 1)` must return exactly 1.0 for every `x`, including a huge one — the first term does not contain `x` at all. If yours returns `1 + x`, your loop is running one step too far.",
                    r"`terms_needed` is a `while` loop over `abs_error`, not a formula. Guard nothing: the error falls to zero eventually for any finite `x`, so the loop always ends.",
                    r"A negative `x` is not a special case. The terms alternate in sign and the same loop handles it.",
                ],
                "tests": [
                    {"name": "the first few partial sums are exact", "code": r'''
assert abs(exp_series(1.0, 1) - 1.0) < 1e-15, f"one term is just 1, got {exp_series(1.0, 1)}"
assert abs(exp_series(1.0, 2) - 2.0) < 1e-15, f"two terms at x=1 give 1+1=2, got {exp_series(1.0, 2)}"
assert abs(exp_series(1.0, 5) - 2.708333333333333) < 1e-12, \
    f"five terms at x=1 give 1+1+1/2+1/6+1/24 = 2.7083333, got {exp_series(1.0, 5)}"
assert abs(exp_series(3.7, 1) - 1.0) < 1e-15, "the first term never contains x"
'''},
                    {"name": "enough terms reproduce the exponential", "code": r'''
import math
for _x in (0.5, 2.0, -1.0, -3.0):
    assert abs(exp_series(_x, 40) - math.exp(_x)) < 1e-12, \
        f"40 terms should nail e**{_x}: got {exp_series(_x, 40)} against {math.exp(_x)}"
'''},
                    {"name": "the error is the first term thrown away", "code": r'''
_e = abs_error(0.1, 2)
assert abs(_e - 0.005170918075647624) < 1e-12, f"expected 0.0051709 at x=0.1, got {_e}"
assert 0.9 < _e / (0.1 * 0.1 / 2) < 1.1, \
    "the error should be within 10% of x*x/2, the first term left out"
'''},
                    {"name": "halving x quarters the error", "code": r'''
_ratio = abs_error(0.1, 2) / abs_error(0.05, 2)
assert 3.8 < _ratio < 4.3, \
    f"a quadratic error term should fall by about four when x halves, got a ratio of {_ratio}"
_ratio3 = abs_error(0.1, 3) / abs_error(0.05, 3)
assert 7.4 < _ratio3 < 8.6, \
    f"with three terms the leading error is cubic, so expect about eight, got {_ratio3}"
'''},
                    {"name": "the binomial rule multiplies the percentage by the power", "code": r'''
assert abs(linear_binomial(0.02, 3) - 1.06) < 1e-12, f"1 + 3*0.02 = 1.06, got {linear_binomial(0.02, 3)}"
assert abs(linear_binomial(0.02, 0.5) - 1.01) < 1e-12, "a square root halves the change"
assert abs(linear_binomial(0.05, -1) - 0.95) < 1e-12, "a reciprocal reverses it"
assert abs(linear_binomial(0.02, 3) - 1.02 ** 3) < 2e-3, \
    "and it should land within a fifth of a percent of the exact value"
'''},
                    {"name": "counting the terms a tolerance costs", "code": r'''
assert terms_needed(0.0, 1e-12) == 1, "at x=0 one term is already exact"
_n = terms_needed(1.0, 1e-6)
assert _n == 10, f"e to a millionth needs 10 terms, got {_n}"
assert abs_error(1.0, _n) <= 1e-6, "the count returned must actually meet the tolerance"
assert abs_error(1.0, _n - 1) > 1e-6, "and one fewer term must not"
'''},
                    {"name": "a smaller x is cheaper", "code": r'''
assert terms_needed(0.1, 1e-6) < terms_needed(1.0, 1e-6), \
    "the series converges faster close to the point it was built around"
assert terms_needed(0.1, 1e-6) == 5, f"expected 5 terms at x=0.1, got {terms_needed(0.1, 1e-6)}"
'''},
                ],
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Equations that will not rearrange: iteration and Newton's method",
            "summary": "The moment a circuit contains a diode, algebra stops being able to isolate the answer. Iteration is what replaces it, and Newton's method is the tangent line from module 7, used over and over.",
            "concepts": [
                r"A resistor and a diode in series across a supply obey $I_s\left(e^{v/V_T} - 1\right) = (V_s - v)/R$. The unknown $v$ appears inside an exponential on one side and outside it on the other, and no rearrangement separates them: the answer exists, is unique, and has no formula.",
                r"**Iteration** replaces a formula with a sequence of guesses that improves, plus a rule for when to stop. The rule matters as much as the sequence.",
                r"**Bisection** needs only a sign change. Evaluate at the midpoint of a bracket, keep whichever half still has the sign change across it, repeat. Each step halves the interval, so 30 steps take a 5 V bracket down to 5 nV. It cannot fail, and it is slow.",
                r"**Newton–Raphson** replaces the curve by its tangent at the current guess and jumps to where that tangent crosses zero: $x_{n+1} = x_n - f(x_n)/f'(x_n)$. That is module 7's linearisation, applied again and again.",
                r"Near a simple root Newton roughly squares the error each step — the number of correct digits doubles — but far from one it can throw the guess anywhere. A diode at 0 V has an almost flat slope, so the very first step from there lands several volts away; every circuit simulator therefore limits how far one step may move.",
                r"Stop on the **change**, not on the residual alone. When the step is smaller than the accuracy you actually need and $f$ is small, you have an answer; a tolerance far below what you can measure just spends iterations.",
                r"The two methods are complementary, not rivals: bracket with bisection until you are near, then let Newton finish. Every serious solver is some version of that pairing.",
                r"EE131 module 10, *Finding a root you cannot solve for*, writes both of these as code. The two courses run alongside each other and neither assumes the other, so the methods are stated in full in both places; the division is that the mathematics is this module's — why a sign change guarantees a root, why Newton doubles the digits, why the pair is used together — while what EE131 adds is the engineering of a solver somebody else can call: the function passed in as an argument instead of baked in, a raised error rather than a plausible-looking number when the bracket has no sign change, and a stopping rule the caller chooses. If you meet that module first, nothing here will be new mathematics; if you meet this one first, nothing there will be new mathematics either.",
            ],
            "read": [
                {
                    "title": "Two curves, and the place where they cross",
                    "minutes": 15,
                    "body": r'''
Put three things in a loop: a 5 V supply, a 1 kΩ resistor, and a small-signal diode.
Call $v$ the voltage at the node between the resistor and the diode, with the diode's
other end tied to ground. One current goes round the loop, because there is nowhere
else for it to go, and one voltage is unknown. On the face of it this is the simplest
circuit in the course.

Build it and a meter says 0.574 V across the diode and 4.43 mA round the loop. Now try
to get those two numbers out of the component values on paper. You will not manage it
— not by rearranging harder, not by being cleverer with logarithms, not ever. There is
no formula. The answer exists, it is a single definite number, and no finite
combination of the usual operations produces it from $V_s$, $R$, $I_s$ and $V_T$.

That is not a gap in your algebra. It is a property of the equation, and the response
to it is the subject of this module. It is also, quietly, what every circuit simulator
in the world does a few hundred thousand times every time somebody presses Run.

## The two demands

Forget equations for a moment and think about what each component wants.

The **resistor** is a straight-line device. Whatever voltage $v$ ends up at the node,
the resistor has $V_s - v$ across it and therefore carries

$$i_R = \frac{V_s - v}{R}$$

Plot that against $v$ and you get a falling straight line: 5 mA when $v = 0$, zero when
$v = 5$ V, and a slope of $-1/R$ all the way across. It is called the **load line**, and
it is the whole of what the rest of the circuit has to say about the diode. Nothing
about the diode enters it.

The **diode** is not a straight-line device at all. It carries

$$i_D = I_s\left(e^{v/V_T} - 1\right)$$

with $I_s$ around $10^{-12}$ A for a small-signal part and $V_T = 25.85$ mV at room
temperature. That is an extremely violent curve. At 0.30 V it passes 110 nanoamps; at
0.50 V, 251 microamps; at 0.60 V, 12.0 milliamps; at 0.65 V, 83 milliamps. Every extra
59.5 mV multiplies the current by ten, because $V_T \ln 10 = 59.5$ mV — that constant
is worth memorising, and it is the reason diode voltages are always quoted as *about*
something.

Both currents are the same current, because the parts are in series. So the answer is
wherever the falling line meets the rising curve. There is a real picture here and it
is worth holding on to: two curves on the same axes, one from the linear part of the
circuit and one from the non-linear part, crossing at a single point. That point is
called the **operating point**, and finding it is the problem.

## Writing it down, and watching the algebra fail

Setting the two demands equal:

$$I_s\left(e^{v/V_T} - 1\right) = \frac{V_s - v}{R}$$

One unknown, one equation. Try to isolate $v$.

The obvious move is to take logarithms, since the offending operation is an
exponential. Rearranged for that:

$$e^{v/V_T} = 1 + \frac{V_s - v}{R I_s}
\qquad\Longrightarrow\qquad
v = V_T \ln\!\left(1 + \frac{V_s - v}{R I_s}\right)$$

Look carefully at what happened. The logarithm did exactly what it was asked: it
released the $v$ that was inside the exponential. But the *other* $v$, the one that
came from the resistor, is now sitting inside the logarithm, and there is no operation
that will bring it out. Push the other way — multiply out, collect terms — and you get
$v$ trapped inside an exponential again. The unknown appears in two places of
incompatible kinds, and the standard toolkit has nothing that separates them.

This is not a rare pathology. $v e^{v} = a$, $x + \sin x = a$, $x = \cos x$: all the
same shape of failure, and all common. Mathematicians handle the first of those by
inventing a name for its solution — the Lambert W function — and tabulating it, which is
honest but is not a formula in any useful sense. It is a promise that somebody else has
already done the iteration for you.

## There is an answer, and there is exactly one

Before hunting for a number it is worth knowing that there is one to find, and that
you will not have to choose between several.

Look at the two sides as functions of $v$ on the interval $0 \le v \le V_s$.

The diode side starts at exactly zero when $v = 0$ — that is what the $-1$ in the law
is for — and increases, strictly, without ever levelling off. The resistor side starts
at $V_s/R = 5$ mA and decreases, strictly, reaching zero at $v = V_s$.

So at the left end the diode side is *below* the resistor side, and at the right end it
is *above* it. Both sides are continuous. A continuous function that is negative
somewhere and positive somewhere else must be zero in between — that is the
intermediate value theorem, and it is the entire mathematical content of "the curves
have to cross". And because one side only ever rises while the other only ever falls,
their difference only ever rises, so it can pass through zero once and once only.

Define the **residual**

$$f(v) = i_D(v) - \frac{V_s - v}{R}$$

and the statement is: $f(0) < 0$, $f(V_s) > 0$, $f$ is continuous and strictly
increasing, so $f$ has exactly one zero in between. Everything that follows is a way of
finding it.

## First response: turn the failed rearrangement into a recipe

Go back to

$$v = V_T \ln\!\left(1 + \frac{V_s - v}{R I_s}\right)$$

It is not a solution, because $v$ is on both sides. But it *is* a machine: put a number
in on the right, get a number out on the left, put that back in. Take a 10 V supply
through 1 kΩ and start from a guess of 0.600 V.

```
guess v = 0.600000000 V
pass 1   i = (10 - 0.600000000)/1000             = 9.400000 mA
         v = 0.02585 * ln(9.400000e-3 / 1e-12)   = 0.593618767 V
pass 2   i = (10 - 0.593618767)/1000             = 9.406381 mA
         v = 0.02585 * ln(9.406381e-3 / 1e-12)   = 0.593636310 V
pass 3   i = (10 - 0.593636310)/1000             = 9.406364 mA
         v = 0.02585 * ln(9.406364e-3 / 1e-12)   = 0.593636262 V
```

The answer is 0.593636262 V, so three passes have taken a guess that was 6.4 mV out and
settled it to a tenth of a nanovolt. The reason it behaves so well is the logarithm: an
error of 1% in the current becomes an error of only $V_T \ln(1.01) = 0.26$ mV in the
voltage. Differentiate the right-hand side and the factor by which each pass shrinks the
error comes out as

$$\left|\frac{V_T}{V_s - v}\right| = \frac{0.02585}{9.406} = \frac{1}{364}$$

which is exactly what the table does: 6.4 mV of error becomes 17.5 µV, then 48 nV, then
0.13 nV. The starting guess barely matters — begin at 0.3 V or 0.9 V and you land in the
same place in the same three passes.

That is **fixed-point iteration**, and the warning that belongs with it is that the
crushing factor is a property of this particular rearrangement, not of iteration in
general. Write the same equation the other way round —

$$v = V_s - R\,I_s\left(e^{v/V_T} - 1\right)$$

— and the same differentiation gives a factor of $R I_s e^{v/V_T}/V_T = R i/V_T = 364$:
the exact reciprocal, so each pass now *multiplies* the error by 364 instead of dividing
by it. Two passes from a guess that was a millivolt out and you are past 100 V. The same
equation, rearranged two ways, gives one recipe that converges in three steps and one
that diverges in two, and nothing in the algebra tells you in advance which one you have
written. That is exactly why the next two methods are worth having: they do not depend on
finding a lucky rearrangement.

## Second response: stop rearranging and hunt by sign

You know $f(0) < 0$ and $f(5) > 0$. You do not need a formula to exploit that. Evaluate
$f$ at the midpoint of the interval; whichever half still has opposite signs at its
ends must contain the crossing, so keep that half and throw the other away. Repeat.

That is **bisection**, and on the 5 V, 1 kΩ loop the first six steps run like this:

```
bracket [0.000000, 5.000000]   f(0) = -5.000 mA,  f(5) > 0
 1  mid 2.500000   f = +1.0e+33 mA   ->  [0.000000, 2.500000]
 2  mid 1.250000   f = +1.0e+12 mA   ->  [0.000000, 1.250000]
 3  mid 0.625000   f = +27.273  mA   ->  [0.000000, 0.625000]
 4  mid 0.312500   f =  -4.687  mA   ->  [0.312500, 0.625000]
 5  mid 0.468750   f =  -4.456  mA   ->  [0.468750, 0.625000]
 6  mid 0.546875   f =  -2.912  mA   ->  [0.546875, 0.625000]
```

Six steps have taken a 5 V interval down to 78 mV, and the answer 0.574147 is inside
it. Nothing about the diode was used except the ability to evaluate it and read off a
sign.

Notice the first two residuals. A diode at 2.5 V would pass $10^{30}$ amps, and the
arithmetic reports it without complaint. That is fine here, but it is a real limit:
widen the starting bracket to 50 V and $e^{50/0.02585}$ overflows a double-precision
float before the first step finishes. A bracket is a claim about where the answer is,
and it should be as tight as you can honestly make it.

## What bisection costs

Each step multiplies the width of the bracket by exactly one half, so after $n$ steps a
starting width $W$ has become $W/2^n$. To get below a tolerance $\varepsilon$ you need

$$n \ge \log_2\!\frac{W}{\varepsilon}$$

For $W = 5$ V and $\varepsilon = 1$ nV that is $\log_2(5\times10^9) = 32.2$, so 33
steps. And because the cost is a logarithm, extra accuracy is bought at a *fixed price
per factor*: three more decimal places is $\log_2 1000 = 9.97$, call it ten more steps,
whether you are going from volts to millivolts or from nanovolts to picovolts.

That is bisection's whole character. It is completely reliable and completely
indifferent to how nice the function is, and it will never do better than one bit of
the answer per evaluation. Newton, in the next unit, will do better than that — and
will occasionally fail outright, which is the trade.

## The mistake: "a diode drops 0.7 volts"

This is the thing people actually do, and it is tempting for a good reason: it is
*nearly* right, it takes no work, and the person who taught it to you was not lying.
Assume 0.7 V, subtract it from the supply, divide by $R$, and you have a current in
five seconds.

Here is what it costs. Solve the loop properly at four different currents:

```
Vs = 1.5 V, R = 10 kΩ    ->  0.4768 V   at   0.102 mA
Vs = 5.0 V, R =  1 kΩ    ->  0.5741 V   at   4.426 mA
Vs = 5.0 V, R =  330 Ω   ->  0.6026 V   at  13.33  mA
Vs = 5.0 V, R =   47 Ω   ->  0.6527 V   at  92.50  mA
```

The drop is not 0.7 V at any of them, and it moves 176 mV across the range — because
the drop is a *logarithm* of the current, and the current here spans three decades, and
three decades is $3 \times 59.5 = 179$ mV. The rule of thumb is not a fact about diodes;
it is a fact about the one current, somewhere around an amp for a rectifier, where
somebody first quoted it.

When does it not matter? When the diode is in series with something much larger. At
$V_s = 5$ V through 1 kΩ, being wrong about the drop by 126 mV changes the current by
$0.126/1000 = 126$ µA out of 4.4 mA — under 3%, and less than the resistor's own
tolerance. When does it matter? When the supply is small: on the 1.5 V rail through
10 kΩ the true drop is 0.477 V, so assuming 0.7 V predicts $(1.5 - 0.7)/10\,000 = 80$ µA
where the circuit actually delivers 102 µA — an error of 22%, because what the assumption
is wrong about is a large fraction of the 1.5 V there is to go round. It also matters
when the diode is the thing you are measuring, and when it sits in a feedback loop that
amplifies the discrepancy rather than diluting it. Knowing which case you are in is the
actual skill; assuming 0.7 V and never checking is the mistake.

## Where bisection stops holding

Bisection rests on one thing only: a sign change across a bracket. Take that away and
it has nothing.

**A root the function touches but does not cross.** $f(v) = (v - a)^2$ is zero at $a$
and positive either side. There is no bracket with opposite signs anywhere, so
bisection cannot start. This is not exotic — it is what a tangency looks like, and it
happens at exactly the parameter values where two operating points are about to merge
and vanish.

**A sign change with no root.** $f(v) = 1/(v - a)$ changes sign across $a$ because it
blows up there. Bisection will converge, confidently and to full precision, on a pole.
The method never evaluates whether the thing it is closing in on is a solution; it
only ever compares signs.

**More than one unknown.** Two nodes and two diodes give two residuals in two
variables, and "the sign of $f$" is no longer one bit — there is no way to bisect a
region of the plane, because there is no ordering to bisect along. Every real circuit
is in this case: a schematic with $n$ nodes gives $n$ simultaneous non-linear
equations. This is where bisection simply stops being available, and it is the reason
the next unit matters. Newton's method generalises to $n$ dimensions without changing
shape — the derivative becomes a matrix, the division becomes the matrix solve of
module 4, and everything else reads the same.
''',
                },
                {
                    "title": "The tangent, used again and again",
                    "minutes": 18,
                    "body": r'''
Bisection throws away almost everything it learns. It computes $f$ at a point, keeps
one bit of the result — the sign — and discards the magnitude, the steepness, and
every other thing that evaluation cost it. Standing at $v = 0.60$ V on the 5 V loop it
would note "positive" and move on, when what it actually had in its hands was: the
residual is 7.63 mA, and the curve is climbing at 0.466 amps per volt just here. Two
numbers like that are enough to make a *guess about where zero is*, and a guess is
worth more than a bit.

That is Newton's method. It is module 7's idea — replace a curve by its tangent — used
not once but over and over, each time from wherever the last one landed.

## The update, from a straight line

At the current guess $v_n$ you can evaluate two things: the height $f(v_n)$ and the
slope $f'(v_n)$. The straight line through that point with that slope is

$$y = f(v_n) + f'(v_n)\,(v - v_n)$$

It is the best straight-line description of $f$ near $v_n$ — it agrees with $f$ in
value and in slope, and no other line does both. If you had to bet on where $f$ hits
zero knowing nothing but those two numbers, you would bet on where the line hits zero.
Set $y = 0$:

$$0 = f(v_n) + f'(v_n)(v - v_n)
\qquad\Longrightarrow\qquad
v = v_n - \frac{f(v_n)}{f'(v_n)}$$

and that is the whole method:

$$v_{n+1} = v_n - \frac{f(v_n)}{f'(v_n)}$$

For the diode loop the two pieces are worth writing out. The residual is
$f(v) = i_D(v) - (V_s - v)/R$, so

$$f'(v) = \underbrace{\frac{I_s}{V_T}e^{v/V_T}}_{g(v)} + \frac{1}{R}$$

where $g$ is the slope of the diode's own curve — its **conductance** at that voltage,
in amps per volt. Both terms are positive, which is the algebraic version of "the
residual only ever rises", and it means the denominator can never be zero. That is a
guarantee this particular problem hands you and most problems do not.

## Worked: five steps on the 5 V loop

$V_s = 5$ V, $R = 1$ kΩ, $I_s = 1$ pA, $V_T = 25.85$ mV. Start at $v_0 = 0.600$ V,
which is a plausible eyeball guess for a conducting silicon diode.

```
n = 0   v = 0.600000000
        i_D  = 1e-12*(e^(0.600/0.02585) - 1)     = 12.031953 mA
        line = (5 - 0.600)/1000                  =  4.400000 mA
        f    = 12.031953 - 4.400000              =  7.631953 mA
        g    = 12.031953e-3 / 0.02585            =  0.4654527 S
        f'   = 0.4654527 + 1/1000                =  0.4664527 S
        step = 7.631953e-3 / 0.4664527           =  0.0163617 V
        v    = 0.6000000 - 0.0163617             =  0.5836383 V
```

The remaining four steps, with the error against the true answer 0.5741473392:

```
n     v (volts)        step (V)     error (V)
0     0.6000000000                  2.585e-02
1     0.5836383139     1.636e-02    9.491e-03
2     0.5756884201     7.950e-03    1.541e-03
3     0.5741921301     1.496e-03    4.479e-05
4     0.5741473777     4.475e-05    3.856e-08
5     0.5741473392     3.856e-08    2.864e-14
```

Read the error column as a count of correct significant figures: about 2, then 3, then
4, then 7, then 13 — at which point it has run out of double-precision float to be
correct in. The first two steps are still finding their feet; from the third onwards
each one roughly doubles the count.

Bisection, starting from the same 5 V bracket, would have needed
$\log_2(5/5.8\times10^{-14}) = 46.3$, so 47 steps to get to the same place. This is what
people mean when they say Newton is fast.

Notice also the last column against the one before it: **the step you just took is very
nearly the error you had before taking it**, and it is a much better estimate of that
error than the residual is. Hold on to that; the third unit builds a stopping rule out
of it.

## Why the digits double

The pattern in that table is not luck. Write $e_n = v_n - v^*$ for the error, where
$v^*$ is the true root, and expand $f$ about $v_n$ with Taylor's theorem from module 7:

$$0 = f(v^*) = f(v_n) - f'(v_n)e_n + \tfrac12 f''(\xi)e_n^2$$

for some $\xi$ between the two. Divide through by $f'(v_n)$ and rearrange:

$$e_n - \frac{f(v_n)}{f'(v_n)} = \frac{f''(\xi)}{2f'(v_n)}e_n^2$$

The left-hand side is exactly $v_n - v^* - (v_n - v_{n+1}) = e_{n+1}$. So

$$e_{n+1} \approx \frac{f''(v^*)}{2f'(v^*)}\,e_n^2$$

The error is squared each step, times a constant fixed by the shape of $f$ at the root.
Squaring a small number doubles the number of leading zeros, which is the same thing as
doubling the number of correct digits. That is what **quadratic convergence** means, and
you can check the constant on the table above. At the root,
$f' = 0.17221$ S and $f'' = 6.6233$ A/V², so the constant is $6.6233/(2 \times 0.17221)
= 19.23$ per volt:

```
e = 9.491e-03  ->  19.23 * (9.491e-3)^2 = 1.732e-03   (observed 1.541e-03)
e = 1.541e-03  ->  19.23 * (1.541e-3)^2 = 4.567e-05   (observed 4.479e-05)
e = 4.479e-05  ->  19.23 * (4.479e-5)^2 = 3.858e-08   (observed 3.856e-08)
```

The prediction is loose at the top of the table, where $e$ is large enough that
"approximately" is doing some work, and exact by the bottom.

Two conditions are hiding in that derivation, and both matter. $f'$ must not be near
zero at the root, or the constant blows up and the squaring is worthless. And $e_n$
must already be small enough that $\frac{f''}{2f'}e_n^2 < e_n$, i.e. $e_n < 2f'/f''$ —
here about 52 mV. Outside that radius the argument says nothing at all, and the next
section is what "nothing at all" looks like.

## Worked: the same method, started at zero

Zero is the natural place to start: it assumes nothing, it is what you would type if you
had no idea, and for every *linear* circuit in this course it is not even a guess —
Newton on a linear problem lands on the exact answer in one step from anywhere, because
the tangent to a straight line is the line.

```
n = 0   v = 0.000000
        i_D  = 1e-12*(e^0 - 1)                   =  0.000000 mA
        line = (5 - 0)/1000                      =  5.000000 mA
        f    = 0 - 5.000000                      = -5.000000 mA
        g    = 1e-12/0.02585                     =  3.868e-11 S
        f'   = 3.868e-11 + 1/1000                =  0.001000 S
        step = -5.000e-3 / 1.000e-3              = -5.000 V
        v    = 0 - (-5.000)                      =  5.000 V
```

The first step is five volts, and it lands the guess on the supply rail — a voltage at
which this diode would be passing $10^{72}$ amps.

The reason is not that the residual was large. It was 5 mA, which is small. It is that
the **denominator** was tiny: at 0 V the diode contributes 39 picosiemens of slope, so
the only conductance in the circuit is the resistor's 1 mS, and a line that flat travels
five volts before it reaches zero. Newton did nothing wrong. It answered the question it
was asked — *where does the tangent cross?* — and the tangent crosses a long way away,
because $f$ near the origin looks nothing like $f$ near the root.

What happens next is worth following, because it is not what people expect. High up the
exponential the residual is essentially the diode current, $f \approx i_D$, and the
slope is essentially the diode conductance, $f' \approx i_D/V_T$. The step is the ratio
of those, so it is $V_T$ — 25.85 mV — and it stays 25.85 mV no matter how far out you
are:

```
n      v (volts)      step (V)
1      4.99999981     -5.000000
2      4.97414981     +0.025850
3      4.94829981     +0.025850
4      4.92244981     +0.025850
...
```

Newton crawls back down the exponential at one thermal voltage per iteration, and needs
$(5 - 0.574)/0.02585 = 171$ of them before it re-enters the region where it is any good.
One bad step has cost more evaluations than bisection would have taken for the whole
problem.

Raise the supply and the crawl becomes a crash. `exp` gives up on a double-precision
argument beyond 709.8, which is $709.8 \times 0.02585 = 18.35$ V — so on any supply above
about 18 volts the first step lands somewhere the second evaluation cannot even be
computed, and the program stops with an overflow rather than a wrong answer.

This is the failure mode that matters in practice, and it has siblings. If $f'$ is
small the step is huge. If $f'$ changes sign between the guess and the root, the step
points the wrong way. On a function with an inflection between guess and root, Newton
can settle into a two-cycle, bouncing between two points for ever, converging to
nothing and never raising an error.

## The limiter, and why every simulator has one

The fix is blunt and universal: never let a single step move more than some fixed
amount. In code that is three lines,

```
step = f / fprime
if step >  max_step: step =  max_step
if step < -max_step: step = -max_step
v = v - step
```

and with `max_step = 0.1` V the run from zero goes:

```
n     raw step      taken       v
1     -5.000e+00    -1.0e-01    0.100000000
2     -4.900e+00    -1.0e-01    0.200000000
3     -4.800e+00    -1.0e-01    0.300000000
4     -4.680e+00    -1.0e-01    0.400000000
5     -3.819e+00    -1.0e-01    0.500000000
6     -3.962e-01    -1.0e-01    0.600000000
7     +1.636e-02    +1.6e-02    0.583638314
8     +7.950e-03    +8.0e-03    0.575688420
9     +1.496e-03    +1.5e-03    0.574192130
10    +4.475e-05    +4.5e-05    0.574147378
11    +3.856e-08    +3.9e-08    0.574147339
12    +2.866e-14    +2.9e-14    0.574147339
```

Six crawling steps to walk into the neighbourhood, and then the limiter stops binding
and the quadratic behaviour of the previous table takes over unchanged. Twelve
evaluations, against bisection's forty-seven for the same accuracy, and against 178 for
the unlimited version of this same method.

Two details in those three lines are worth saying out loud. The clamp goes on the
**step**, not on the voltage: clamping $v$ into a range would let a bad step arrive and
then hold it, and the loop would stop converging rather than converge slowly. And the
limiter is not an approximation — it changes the *route*, never the destination,
because once the steps are smaller than the limit it is not doing anything at all.
SPICE calls its version of this *damping*, and applies it per junction rather than per
node; the reason your simulator does not fall over on a circuit full of transistors is
that somebody wrote these three lines into it.

## What one step is, as a circuit

Return to the update with the pieces spelled out:

$$v_{n+1} = v_n - \frac{f(v_n)}{g_n + 1/R}$$

The denominator is a sum of two conductances: the diode's at the present guess, and the
resistor's. That is not a coincidence of notation. It is the conductance you would see
looking into that node if the diode really were a resistor of $1/g_n$ — so Newton's
step is the answer to a *linear* circuit problem, and each iteration solves a linear
circuit built from the non-linear one.

You can make that literal. The tangent to the diode's curve at $v_n$ is a straight line
in the $i$–$v$ plane, and a straight line in the $i$–$v$ plane is a resistor in series
with a battery. Its slope gives the resistance,

$$r_d = \frac{1}{g_n} = \frac{V_T}{i_D(v_n) + I_s} \approx \frac{V_T}{i_D(v_n)}$$

and the voltage at which it crosses zero current gives the battery,

$$V_{eq} = v_n - \frac{i_D(v_n)}{g_n} = v_n - V_T\left(1 - e^{-v_n/V_T}\right) \approx v_n - V_T$$

At $v_n = 0.600$ V those come to $r_d = 2.148$ Ω and $V_{eq} = 0.574150$ V. So one
Newton step from 0.6 V is: rub out the diode, draw a 0.574 V battery in series with a
2.15 Ω resistor, solve the resulting divider, and read the node voltage. Which gives

```
(5 - v)/1000 = (v - 0.57415)/2.1484
10.742 - 2.1484 v = 1000 v - 574.15
v = 584.892 / 1002.148 = 0.583638 V
```

— the same 0.583638 the arithmetic above produced, because it is the same arithmetic
wearing a schematic.

That model should look familiar. "A diode is a 0.7 V battery in series with a few ohms"
is the standard hand-analysis model, and what has just fallen out is that it is
precisely one Newton step, from a guess of about 0.7 V, with $r_d = V_T/I$. The rule of
thumb was never a separate thing; it was this method, stopped after one iteration and
not labelled as such.

## The mistake: reading a large step as progress

Here is the one people make. Newton reports a step of 5 V, and the instinct is that a
big step means a big correction — a lot getting done. It is the opposite. A large step
means the tangent is nearly flat, so the local model is nearly useless and the step is
nearly meaningless; in a well-behaved late iteration the steps are *tiny*, and tiny is
what confidence looks like here.

The misreading is tempting because in almost every other numerical setting a big number
in the update means the algorithm found something. It has a practical consequence too:
if the steps a solver reports are not shrinking, do not wait for it to settle — it is
not going to.

## Where Newton stops holding

**At a repeated root.** If $f'(v^*) = 0$ the Taylor argument collapses, and the error
merely halves each step instead of squaring — Newton degrades to something slower than
bisection, and gives no sign that it has.

**Where the tangent points away.** Nothing in the derivation says the step goes towards
the root; it says the step goes to where the tangent crosses. Start Newton on
$\arctan x$ far from the origin and each step lands further out than the last, for ever.
The remedy is not a cleverer step but a *test*: only accept a step that reduces $|f|$,
and halve it until it does. That is a **line search**, and it is what turns Newton from
a fast method into a fast method you can rely on.

**Where the function is not smooth.** An ideal switch, a comparator, a table with kinks:
all have derivatives that are zero, undefined or wrong. It is why device models are
written to be continuously differentiable even where the physics is not — the model is
chosen to keep Newton alive.

**Where the derivative is expensive or unavailable.** If $f$ is a measurement or a
simulation you cannot differentiate, replace the tangent by the line through the last
two points. That is the **secant method**; it converges at a rate of about 1.62 rather
than 2, which is nearly as good for half the work per step.

And the practical arrangement, which is neither method on its own: bracket with
bisection until you are inside the region where the quadratic argument holds, then let
Newton finish, and fall back to a bisection step any time Newton proposes something
that leaves the bracket. That hybrid is Brent's method, it is what `scipy.optimize` and
MATLAB's `fzero` do, and it is the honest answer to "which one should I use".
''',
                },
                {
                    "title": "Knowing when to stop, and what the answer is worth",
                    "minutes": 14,
                    "body": r'''
Every method in this module produces an endless sequence. Bisection will happily go on
halving a bracket for ever; Newton will keep proposing steps of $10^{-18}$ V long after
the answer stopped changing. Neither of them terminates on its own. The stopping rule
is not an implementation detail bolted on at the end — it is the part of the method
that decides what number you actually get, and it is where most of the real mistakes
live.

There are two things you could plausibly measure, and only one of them is the thing you
care about.

## What you want, and what you can see

What you want is the **error**, $|v_n - v^*|$. You cannot have it: $v^*$ is precisely
the number you do not know.

What you can see is the **residual**, $|f(v_n)|$ — how badly the circuit equation fails
at your present guess. It is tempting to treat a small residual as a small error, and
in a linear problem with a well-conditioned matrix that is roughly fair. On this
problem it is badly wrong, and it is worth seeing exactly how wrong.

## Worked: the residual lies about the error

The 5 V, 1 kΩ loop again, true answer $v^* = 0.5741473$ V. Evaluate the residual at
four guesses:

```
v (V)      residual (mA)      error (mV)
0.500        -4.249            -74.15
0.550        -2.711            -24.15
0.600        +7.632            +25.85
0.650       +78.896            +75.85
```

Look at the top two rows against the bottom two. At 0.550 V the residual is 2.7 mA and
the guess is 24 mV low. At 0.600 V the residual is nearly three times bigger, 7.6 mA,
and the guess is 26 mV out — essentially the same distance from the answer, on the
other side. And at 0.650 V, a residual thirty times larger than at 0.550 V corresponds
to an error only three times larger.

The residual is not a distorted picture of the error; it is a picture of something else
entirely. It is the error multiplied by a slope taken somewhere between the guess and
the root, and on an exponential that slope changes by a factor of ten every 59.5 mV.
The residual's slope here is 10.7 mS at 0.500 V and 3.22 S at 0.650 V, a factor of 300
across a range of 150 mV — so a fixed residual threshold that stands for a millivolt of
error at 0.500 V stands for three microvolts of it at 0.650 V.

There is a second problem with the residual, which is that it has *units*. It is a
current. "Stop when $|f| < 10^{-9}$" is a nanoamp, and whether a nanoamp is negligible
depends entirely on whether the circuit runs at 4 mA or at 4 nA. Any threshold you
write against a residual is a claim about the scale of the problem, and it will be
wrong on the next circuit.

## The step is the error, near the end

The quantity that does work is the **step**, $|v_{n+1} - v_n|$. From the previous unit,
once Newton is converging quadratically the error after a step is the square of the
error before it, times a constant — so the error after is negligible against the error
before, and

$$|v_{n+1} - v_n| = |e_n - e_{n+1}| \approx |e_n|$$

The step you just took is an estimate of the error you just removed. It is in volts,
the same units as the answer, it needs no knowledge of $f'$, and it is available for
free.

The catch is that it estimates the error you *had*, not the one you have left — it is
one step out of date, which is why it is a conservative rule and not an exact one. And
it can be small for the wrong reason: a limiter that is clamping, or a nearly flat
region, produces small steps with a large error still outstanding. So the rule people
actually use is both together — the step is small **and** the residual is small — with
the step doing the work of measuring and the residual doing the work of confirming that
you are near a root rather than merely stuck.

## Absolute and relative, in the same test

A single threshold cannot serve both a 5 V node and a 5 µV one. The standard form is

$$|v_{n+1} - v_n| < \varepsilon_{abs} + \varepsilon_{rel}\,|v_{n+1}|$$

The relative term does the work at ordinary signal levels; the absolute term stops the
test becoming impossible near zero, where a relative tolerance would demand infinite
precision from a node that is meant to be at ground. SPICE ships with `reltol` = $10^{-3}$,
`vntol` = 1 µV for voltages and `abstol` = 1 pA for currents, and those three numbers
between them are why a simulation converges in a few iterations rather than a few
hundred.

## Worked: what the answer is actually worth

Before choosing a tolerance, ask what the answer means. The diode's operating point
depends on $I_s$, which is set by the doping and the geometry of the junction and
varies by a factor of two or more between two parts out of the same bag. Push that
through:

$$v = V_T \ln\!\frac{I}{I_s}
\qquad\Longrightarrow\qquad
\Delta v = -V_T \ln 2 = -25.85 \times 0.6931 = -17.92\ \text{mV}$$

Doubling $I_s$ moves the operating point 17.9 mV. Now the resistor, a 5% part:

```
R =  950 Ω   ->  v = 0.5754656 V
R = 1000 Ω   ->  v = 0.5741473 V
R = 1050 Ω   ->  v = 0.5728934 V
```

a spread of 2.6 mV across the tolerance band. And temperature: $V_T = kT/q$ moves with
$T$, and $I_s$ moves far faster, with the net effect that a silicon junction's forward
voltage falls about 2 mV for every degree. Ten degrees of ambient is 20 mV.

So the operating point of this circuit is a number known to perhaps $\pm 20$ mV in the
physical world. Solving it to $10^{-12}$ V is solving it ten orders of magnitude past
the point where the answer means anything, and each of those orders costs iterations.

And yet simulators do converge tightly, for a reason worth understanding: the DC solve
is not the deliverable. It is one step inside a transient loop that will run it fifty
thousand times, and a residual left behind at each step accumulates. Converging to a
thousand times better than you need is cheap when the cost is quadratic — it is one
extra iteration — and it is what stops a slow drift from swamping the answer. The rule
is: **choose the tolerance from what the result feeds, not from what the result means.**
A single number for a datasheet needs three digits. The same number inside a loop that
integrates it needs ten.

## The floor you cannot go below

Ask for too much and the loop never ends. Doubles carry about 16 significant decimal
digits, so near $v = 0.574$ the spacing between representable numbers is

$$\text{ulp}(0.574) \approx 1.11\times10^{-16}\ \text{V}$$

No step smaller than that can be represented; subtracting one changes nothing. A
tolerance of $10^{-18}$ V is therefore a request that can never be satisfied, and the
loop runs until the iteration cap saves it — reporting failure on a problem it solved
perfectly at iteration eleven. The same trap catches a residual tolerance set below the
noise of the arithmetic that computes $f$: subtracting two numbers around 12 mA to get
a residual leaves about $10^{-18}$ A of rounding, and asking for less than that is
asking for a number that is not there.

Always cap the iteration count, and always treat hitting the cap as an error rather
than as a result. The alternative is a function that returns a plausible-looking number
having quietly failed, which is the worst possible outcome — worse than a crash,
because nothing downstream can tell.

## The mistake: turning the tolerance down until it "looks converged"

The mistake is to watch a printed answer wobble in the sixth decimal place, tighten
`tol` by a factor of a thousand, see it stop wobbling, and ship that. It is tempting
because it works — the wobble does stop — and because it feels like rigour.

What it usually buys is nothing. If the wobble came from a genuine convergence problem,
a tighter tolerance makes the loop run longer and fail in the same place. If it came
from the sixth decimal place being meaningless, as it was above, then you have paid
iterations for digits that describe the model rather than the circuit. And in a
transient simulation the same reflex is actively harmful: tightening `reltol` past the
error of the integration method makes every timestep slower without making the waveform
one bit more accurate, because the accuracy is set by the timestep, not the solve.

The habit that replaces it: decide what the answer is worth *before* choosing the
tolerance, then set the tolerance a couple of decades below that, then cap the
iterations and treat the cap as a failure.

## Where "the answer" stops being a single number

Everything in this module has rested on the uniqueness argument from the first unit:
one side strictly rising, the other strictly falling, therefore exactly one crossing.
Plenty of real circuits break it.

Put a resistor from the output of an inverter back to its input and you have a Schmitt
trigger; add positive feedback around an amplifier and you have a latch; use a tunnel
diode, whose $i$–$v$ curve genuinely falls over part of its range, and the load line
can cross it three times. In each case there are *several* operating points, two of them
stable and one not, and asking "what voltage does it sit at" has no single answer. It
depends on what happened before.

Newton does not report this. It converges, quickly and cleanly, to whichever solution
lies in the basin of the initial guess — so the initial guess stops being a
computational convenience and becomes part of the question. Change it and you get a
different answer, both of them correct.

What replaces the simple loop there is **continuation**: solve an easy problem you know
the answer to, then deform it towards the hard one in small steps, carrying the solution
along as the starting guess for each. SPICE does exactly this when a circuit will not
converge — `gmin` stepping hangs a large conductance from every node to ground so that
the circuit is nearly linear, solves that, then shrinks the conductance back to nothing
a decade at a time; source stepping ramps every supply up from zero. And when even that
fails, the honest answer is to stop asking for a DC operating point at all and run a
transient from a known initial state, because a circuit with two stable states does not
have *an* operating point — it has a history.
''',
                },
            ],
            "match": {
                "title": "Which laws you can rearrange, and which you cannot",
                "minutes": 7,
                "brief": r'''
Before deciding how to solve a circuit, you have to know what kind of equations it
is made of. Every symbol on a schematic stands for a relationship between the voltage
across a part and the current through it — and only some of those relationships can
be rearranged to put the unknown on its own.

Two of these five are the reason this module exists.
''',
                "prompt": "Pick a law, then tap the symbol that obeys it.",
                "labels": [
                    "Current proportional to voltage — one straight line, and the unknown comes out by rearranging",
                    "Current proportional to the rate of change of voltage",
                    "Voltage proportional to the rate of change of current",
                    "Current an exponential of voltage — no rearrangement puts the voltage on its own",
                    "Either no voltage across it or no current through it — a case split rather than a formula",
                ],
                "items": [
                    {"sym": "R", "a": 0, "why": "A resistor: $i = v/R$ at every instant. The graph of current against "
                     "voltage is a straight line through the origin, and its slope is the same wherever you stand on "
                     "it — which is exactly why a network of resistors becomes a set of linear equations and a matrix."},
                    {"sym": "C", "a": 1, "why": "A capacitor: $i = C\\,dv/dt$. Linear, but in a derivative — so it "
                     "contributes to a differential equation rather than to an algebraic one. At a single frequency "
                     "module 2 turned that derivative into a multiplication, which is what made phasors worth having."},
                    {"sym": "L", "a": 2, "why": "An inductor: $v = L\\,di/dt$, the capacitor's mirror image. Also "
                     "linear, also a derivative, and the second energy store that made module 6's equation "
                     "second-order."},
                    {"sym": "D", "a": 3, "why": "A diode: $i = I_s(e^{v/V_T} - 1)$. Take logs to isolate $v$ and the "
                     "$v$ on the other side of the circuit equation is still there, untouched. This is the law that "
                     "forces iteration, and the reason every simulator has a Newton loop at its heart."},
                    {"sym": "SW", "a": 4, "why": "A switch: open means zero current whatever the voltage, closed "
                     "means zero voltage whatever the current. Each state is perfectly linear on its own, and "
                     "choosing between them is not — which is why a circuit with switches is solved state by state."},
                ],
            },
            "quiz": {
                "title": "Guessing well, and knowing when to stop",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Why can the diode-and-resistor loop not be solved by rearranging?",
                        "opts": [
                            "Because the exponential has no inverse",
                            "Because the unknown voltage appears both inside the exponential and outside it",
                            "Because $I_s$ is too small to work with",
                            "Because the equation has no solution",
                        ],
                        "a": 1,
                        "why": (
                            r"Taking a logarithm isolates the $v$ inside the exponential and leaves the other $v$ — the "
                            r"one in $(V_s - v)/R$ — exactly where it was. The exponential does have an inverse, and the "
                            r"equation does have a solution: a single one, since one side rises steeply with $v$ while "
                            r"the other falls, so the two curves cross exactly once."
                        ),
                    },
                    {
                        "q": r"Bisection halves its bracket at every step. Starting from a bracket 1 V wide, how many steps take it below 1 mV?",
                        "opts": ["3", "10", "100", "1000"],
                        "a": 1,
                        "why": (
                            r"$2^{10} = 1024$, so ten halvings take 1 V to 0.98 mV. Each step buys a fixed *factor*, "
                            r"which means the cost of an extra three decimal places is about ten more steps whatever "
                            r"you started from. The 1000 comes from thinking the interval falls by one thousandth per "
                            r"step rather than by half."
                        ),
                    },
                    {
                        "q": r"The update $x - f(x)/f'(x)$ is the root of what?",
                        "opts": [
                            "The tangent line to $f$ at the current guess",
                            "The chord between the two ends of the bracket",
                            "The second-order Taylor polynomial at the current guess",
                            "The function itself, computed exactly",
                        ],
                        "a": 0,
                        "why": (
                            r"The tangent at $x$ is $y = f(x) + f'(x)(X - x)$; setting $y = 0$ and solving for $X$ gives "
                            r"precisely $x - f(x)/f'(x)$. Using the chord instead is a different and slightly slower "
                            r"method (the secant method), and using the quadratic is a different one again. Newton is "
                            r"the linear one — which is why module 7 comes first."
                        ),
                    },
                    {
                        "q": r"Newton is started at 0 V on a diode-and-resistor loop and the first step lands near the supply voltage. Why?",
                        "opts": [
                            "Because the residual at 0 V is enormous",
                            "Because the diode's slope at 0 V is almost zero, so the tangent is nearly flat and crosses zero far away",
                            "Because the method always overshoots on its first step",
                            "Because the supply voltage is the correct answer",
                        ],
                        "a": 1,
                        "why": (
                            r"The step is $f/f'$, and it is the *denominator* that is tiny: a diode conducts almost "
                            r"nothing at 0 V, so the only slope left is the resistor's $1/R$. A nearly flat line "
                            r"crosses zero a long way off. The residual at 0 V is only a few milliamps — small, not "
                            r"enormous — which is precisely why the ratio is large."
                        ),
                    },
                    {
                        "q": r"Near a simple root, how does Newton's error behave from one step to the next?",
                        "opts": [
                            "It halves",
                            "It falls by a fixed number of digits per step, set by the function",
                            "It is roughly squared, so the number of correct digits doubles",
                            "It falls linearly with the step number",
                        ],
                        "a": 2,
                        "why": (
                            r"Squaring the error is what quadratic convergence means: $10^{-2}$ becomes $10^{-4}$, then "
                            r"$10^{-8}$. Started at 0.6 V, this module's lab runs an error of $9\times10^{-3}$, then $1.5\times10^{-3}$, "
                            r"$4.5\times10^{-5}$, $3.9\times10^{-8}$ — visibly faster than any fixed factor. Halving is "
                            r"bisection's behaviour, and it is the price bisection pays for never failing."
                        ),
                    },
                    {
                        "q": r"What is the honest reason to keep bisection in the toolbox at all?",
                        "opts": [
                            "It is faster once the bracket is small",
                            "It needs no derivative and cannot diverge once a sign change is bracketed",
                            "It is more accurate at the same number of steps",
                            "It works on equations that have no solution",
                        ],
                        "a": 1,
                        "why": (
                            r"Bisection asks only for the sign of $f$, so it works where the derivative is unavailable, "
                            r"unreliable or expensive — and once a sign change is bracketed the answer cannot escape. "
                            r"It is slower at every stage, not faster, and no method finds a solution that does not "
                            r"exist. The usual arrangement is bisection to get close, Newton to finish."
                        ),
                    },
                ],
            },
            "derive": {
                "title": "Newton's step, and the diode loop it is aimed at",
                "minutes": 12,
                "vars": ["x", "x_n", "y_n", "m_n", "v", "v_n", "f_n", "g_n", "g", "R", "V_s"],
                "brief": r'''
Newton's method is one line of algebra about a straight line. Derive it once here and
the rest of the module is arithmetic.

At the current guess $x_n$ the function has the value $y_n$ and the slope $m_n$. The
tangent there is the straight line through the point $(x_n, y_n)$ with that slope.
''',
                "steps": [
                    {
                        "prompt": r"Write the height of that tangent line at a general $x$, in terms of $y_n$, $m_n$, $x$ and $x_n$.",
                        "answer": r"y_n + m_n (x - x_n)",
                        "hint": r"Start at the known point and travel: the height changes by the slope times the distance travelled.",
                        "deconstruct": [
                            r"A straight line through $(x_n, y_n)$ with slope $m_n$ has the form $y = y_n + m_n \times (\text{how far you have moved in } x)$.",
                            r"You have moved $x - x_n$.",
                        ],
                    },
                    {
                        "prompt": r"Set that height to zero and solve for $x$ — the next guess. Write it in terms of $x_n$, $y_n$ and $m_n$.",
                        "answer": r"x_n - y_n/m_n",
                        "placeholder": r"the guess, corrected by a ratio",
                        "hint": r"Move $y_n$ across, then divide both sides by $m_n$.",
                        "deconstruct": [
                            r"$0 = y_n + m_n(x - x_n)$.",
                            r"$x - x_n = -y_n/m_n$.",
                        ],
                    },
                    {
                        "prompt": r"Now the circuit. The equation to solve is $f(v) = i(v) - (V_s - v)/R = 0$, where $i(v)$ is the diode's current. Write $df/dv$ in terms of $g$, the slope $di/dv$ of the diode's own curve, and $R$.",
                        "answer": r"g + 1/R",
                        "hint": r"Differentiate the two pieces separately. The second one is $-(V_s - v)/R$, and only the $v$ in it survives differentiation.",
                        "deconstruct": [
                            r"$\frac{d}{dv}i(v) = g$, by the definition of $g$.",
                            r"$\frac{d}{dv}\left(-\frac{V_s - v}{R}\right) = +\frac{1}{R}$, since $V_s$ and $R$ are constants.",
                        ],
                    },
                    {
                        "prompt": r"Put the two together. With the residual $f_n$ and the diode slope $g_n$ at the current guess, write the next voltage in terms of $v_n$, $f_n$, $g_n$ and $R$.",
                        "answer": r"v_n - f_n/(g_n + 1/R)",
                        "hint": r"Take the update you derived and substitute the slope you just worked out.",
                        "deconstruct": [
                            r"The update is $v_{n+1} = v_n - f_n/m_n$.",
                            r"Here $m_n$ is $g_n + 1/R$.",
                        ],
                    },
                ],
                "closing": r'''
Look at what the denominator is. $g_n$ is the diode's slope in amps per volt — its
*conductance* at the present guess — and $1/R$ is the resistor's. Newton's step is
the residual divided by the total conductance seen at that node, which is exactly the
linear circuit you would solve if the diode really were a resistor of $1/g_n$.

That is the whole trick, and the reason it is called linearisation: each iteration
replaces the non-linear part by the resistance it looks like at the current guess,
solves the linear circuit that results, and asks again.
''',
            },
            "numeric": [
                {
                    "title": "The easy direction of the diode law",
                    "minutes": 4,
                    "brief": r'''
The equation that will not rearrange is only stuck in one direction. Given the current
you cannot get the voltage without iterating; given the *voltage* the current comes out
in one line, because that is the way the law is written.

$$i = I_s\left(e^{v/V_T} - 1\right)$$

One rule, one substitution, nothing else. The only place to slip is the exponent, which
is a ratio of two voltages and therefore has no units — so both of them have to be in
the same one before you divide.
''',
                    "prompt": "What current does the diode pass?",
                    "note": "Answer in milliamps, to two decimal places.",
                    "figure": "A single silicon diode with 0.600 V held across it, forward biased. Its "
                              "saturation current is I_s = 1.00 pA and the thermal voltage is "
                              "V_T = 25.85 mV. Nothing else is connected to it.",
                    "given": [
                        {"label": "Voltage across the diode", "value": "0.600 V"},
                        {"label": "Saturation current $I_s$", "value": "1.00 pA"},
                        {"label": "Thermal voltage $V_T$", "value": "25.85 mV"},
                    ],
                    "aside": "25.85 mV is 0.02585 V. A picoamp is $10^{-12}$ A.",
                    "answer": 12.03,
                    "tol": 0.06,
                    "unit": "mA",
                    "hint": r"Work out the exponent $v/V_T$ first and look at it before going on: it should be a plain number in the low twenties. Then exponentiate, subtract one, and multiply by $I_s$.",
                    "wrong": r"If you got something around $2\times10^{-14}$ A, the exponent was computed as $0.600/25.85$ — millivolts against volts. If you got 23.2, that is the exponent itself and not a current. If you got 12.03 A rather than mA, the picoamp went in as $10^{-9}$.",
                    "why": r'''
```
exponent   v / VT   = 0.600 / 0.02585        = 23.2108
e^23.2108                                    = 1.20320e10
minus 1                                      = 1.20320e10
times Is   1e-12 * 1.20320e10                = 1.20320e-2 A
                                             = 12.03 mA
```

The $-1$ changed nothing at all here, and it will change nothing at any forward voltage
worth talking about — at 0.6 V the exponential is $10^{10}$, so subtracting one is a
correction in the eleventh significant figure. It is not decoration, though: it is what
makes the law give exactly zero current at exactly zero volts, and a model that leaked a
picoamp with nothing across it would be wrong in a way that shows up the moment you put
two diodes back to back.

Hold on to the size of that exponent. Twenty-three is what makes this device so
uncomfortable to compute with: 20 mV either way multiplies or divides the answer by
$e^{20/25.85} = 2.17$, and the whole of the rest of this module exists because a
quantity that doubles every 18 mV cannot be solved for by rearranging.
''',
                },
                {
                    "title": "Choosing the resistor, which needs no iteration at all",
                    "minutes": 7,
                    "brief": r'''
Here is the asymmetry that is easy to miss. *Analysing* the loop — supply and resistor
given, find the voltage — has no closed form and needs the whole of this module.
*Designing* it — pick the voltage you want and find the resistor that produces it — is
two lines of school algebra.

The reason is that the unknown has moved. With $v$ chosen, the diode's current follows
immediately, that same current has to come through the resistor, and Ohm's law gives $R$
with nothing on both sides of anything.

You are designing a bias circuit: a 9.00 V supply, one resistor, one diode, in series.
''',
                    "prompt": r"What series resistance puts exactly 0.620 V across the diode?",
                    "note": "Answer in ohms, to the nearest ohm.",
                    "figure": "A 9.00 V supply, a resistor, and a diode in one series loop, the diode's "
                              "far end at ground. The diode has I_s = 1.00 pA and V_T = 25.85 mV. You "
                              "get to choose the resistor; the target is 0.620 V across the diode.",
                    "given": [
                        {"label": "Supply", "value": "9.00 V"},
                        {"label": "Target diode voltage", "value": "0.620 V"},
                        {"label": "Saturation current $I_s$", "value": "1.00 pA"},
                        {"label": "Thermal voltage $V_T$", "value": "25.85 mV"},
                    ],
                    "aside": "The resistor and the diode carry the same current, and the voltage across "
                             "the resistor is what the supply has left after the diode has taken its share.",
                    "answer": 321.0,
                    "tol": 3.0,
                    "unit": "Ω",
                    "hint": r"Get the diode's current at 0.620 V first, exactly as in the previous question. The resistor then has $9.00 - 0.620$ volts across it and that same current through it.",
                    "wrong": r"If you got 345 Ω, the whole 9.00 V was put across the resistor instead of the 8.38 V that is left after the diode. If you got about 696 Ω, the current used was the one at 0.600 V rather than at 0.620 V — 20 mV of diode voltage is a factor of 2.17 in current, and 2.17 is exactly the ratio between those two answers.",
                    "why": r'''
```
diode current at 0.620 V
  exponent  0.620 / 0.02585                 = 23.9845
  e^23.9845                                 = 2.60824e10
  times Is                                  = 2.60824e-2 A  = 26.0824 mA

resistor
  volts across it   9.00 - 0.620            = 8.380 V
  R = 8.380 / 0.0260824                     = 321.29 Ω
```

So 321 Ω, and the nearest standard value is 330 Ω, which lands the diode at 0.6193 V
instead — 0.7 mV low, and nobody would ever notice.

The thing worth taking from this is not the number but the direction. The equation
$I_s(e^{v/V_T} - 1) = (V_s - v)/R$ has four symbols in it besides $v$, and it is
solvable in closed form for *every one of them* — $R$, $V_s$, $I_s$, $V_T$ — and not
for $v$. Whether a problem needs iteration is a question about which symbol you are
asking for, not about how hard the equation looks.

It also shows why nobody biases a circuit like this on purpose. Compare the two
questions: 20 mV of diode voltage moved the current by a factor of 2.17, so read
backwards, a resistor that is 10% off moves the diode's voltage by only
$V_T \ln(1.1) = 2.5$ mV. A diode is an excellent voltage reference driven from a current
source and a terrible current source driven from a voltage.
''',
                },
                {
                    "title": "One Newton step, drawn as the circuit it really is",
                    "minutes": 9,
                    "brief": r'''
The tangent to the diode's curve at a guess $v_n$ is a straight line in the $i$–$v$
plane, and a straight line in the $i$–$v$ plane is a resistor in series with a battery.
So one iteration of Newton's method is not an abstract update — it is a *linear circuit*
you can draw and solve with module 4's methods.

Starting from a guess of $v_0 = 0.600$ V on a 5.00 V supply through 1.00 kΩ, the tangent
has slope

$$g_0 = \frac{i_D(v_0)}{V_T} = \frac{12.032\ \text{mA}}{25.85\ \text{mV}} = 0.4655\ \text{S}
\qquad\Longrightarrow\qquad r_d = \frac{1}{g_0} = 2.15\ \Omega$$

and crosses zero current at $V_{eq} = v_0 - V_T = 0.574$ V. Those two numbers are the
2.15 Ω resistor and the 574 mV source drawn below, in place of the diode.

Solve the circuit as drawn. What comes out is $v_1$, the next Newton iterate — no
exponentials required, because the exponential has already been used up in working out
the two component values.
''',
                    "prompt": r"What voltage does the probed node sit at?",
                    "note": "Answer in volts, to four decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1000},
                            {"id": "rd", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 2.15},
                            {"id": "veq", "kind": "V", "x": 9, "y": 9, "rot": 1, "value": 0.574},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 12},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 8]},
                            {"a": [9, 10], "b": [9, 12]},
                            {"a": [3, 7], "b": [3, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "5.00 V"},
                        {"label": "R1, supply to the probed node", "value": "1.00 kΩ"},
                        {"label": "$r_d$, the tangent's slope resistance", "value": "2.15 Ω"},
                        {"label": "$V_{eq}$, where the tangent meets zero current", "value": "574 mV"},
                        {"label": "The guess this tangent was taken at", "value": "0.600 V"},
                    ],
                    # Nothing about the tangent is restated here: the probed node is the single
                    # unknown of the drawn network, so the solver's own operating point IS the
                    # Newton iterate. Redraw the schematic with different tangent values and this
                    # check follows them.
                    "check": r'''
return c.vout();
''',
                    "answer": 0.5835,
                    "tol": 0.0008,
                    "unit": "V",
                    "hint": r"It is a loop with two sources in it. Either sum the currents at the probed node — $(5 - v)/1000 = (v - 0.574)/2.15$ — or notice that 4.426 V is dropped across 1002.15 Ω in series.",
                    "wrong": r"If you got 10.7 mV, the 574 mV source was left out and the answer is just the divider $5 \times 2.15/1002.15$. If you got 4.99 V, the two resistors were used the wrong way round. If you got 0.600, the tangent was solved at the guess instead of being followed to where it crosses.",
                    "why": r'''
```
node equation   (5 - v)/1000 = (v - 0.574)/2.15
cross-multiply  2.15(5 - v)  = 1000(v - 0.574)
                10.750 - 2.15 v = 1000 v - 574.000
                584.750      = 1002.15 v
                v            = 0.58350 V
```

The true operating point is 0.5741473 V. The guess was 25.9 mV out; one step has brought
it to 9.3 mV out, and the next three steps take it to 1.5 mV, 45 µV and 39 nV. This is
the first rung of the quadratic ladder from the reading unit.

Two things are worth noticing about the drawn circuit. First, the 2.15 Ω is absurdly
small next to the 1 kΩ — the diode at 12 mA is a very stiff device — which is why the
answer sits so close to $V_{eq}$ and why the correction from a guess is small even when
the guess is poor. Second, this schematic is exactly the "0.6 V battery plus a couple of
ohms" model of a diode that gets taught as a rule of thumb. It is not a rule of thumb.
It is Newton's method, drawn, stopped after one iteration, and the two numbers in it are
$v_0 - V_T$ and $V_T/I$.

Solve the same circuit with a tangent taken at 0.583638 V instead and it hands you
0.575688 V, and so on: a simulator's DC analysis is this drawing, redrawn with new
component values, ten or twelve times.
''',
                    "aside": r"$V_{eq} = v_0 - V_T$ is not an approximation picked to make the arithmetic tidy: the exact intercept is $v_0 - V_T\left(1 - e^{-v_0/V_T}\right)$, and the term dropped is 2 picovolts at a guess of 0.6 V. The tangent to an exponential always meets the axis one $V_T$ back, which is a fact about exponentials rather than about diodes — the tangent to $e^x$ at $x_0$ crosses zero at $x_0 - 1$.",
                },
                {
                    "title": "A diode on a divider, and the heat in the feed resistor",
                    "minutes": 12,
                    "brief": r'''
Now three unknown currents instead of one, a quantity that is not a node voltage, and a
source you have to work out rather than read off the supply.

A 12.0 V rail feeds a 470 Ω resistor into node A. From node A, a 2.20 kΩ resistor goes
to ground and a diode goes to ground alongside it. The loop has already been iterated to
convergence, and at the operating point the diode is passing 23.94 mA, which makes its
tangent

$$r_d = \frac{V_T}{I_D} = \frac{25.85\ \text{mV}}{23.94\ \text{mA}} = 1.08\ \Omega,
\qquad V_{eq} = v_A - V_T = 0.592\ \text{V}$$

Those are the 1.08 Ω and the 592 mV in the schematic. Because the tangent was taken *at*
the answer rather than at a guess, this linear circuit does not merely take you one step
closer — it reproduces the non-linear circuit's operating point exactly, which is what
"converged" means.

The question is not about the diode. It is about how much heat the 470 Ω feed resistor
has to get rid of, which decides whether it can be a quarter-watt part.
''',
                    "prompt": r"What power is dissipated in the 470 Ω feed resistor?",
                    "note": "Answer in milliwatts, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 12},
                            {"id": "r1", "kind": "R", "x": 5, "y": 4, "rot": 0, "value": 470},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 2200},
                            {"id": "rd", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 1.08},
                            {"id": "veq", "kind": "V", "x": 13, "y": 9, "rot": 1, "value": 0.592},
                            {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 11},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [2, 5], "b": [2, 4]},
                            {"a": [2, 4], "b": [4, 4]},
                            {"a": [6, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 4], "b": [13, 4]},
                            {"a": [13, 4], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 8]},
                            {"a": [13, 10], "b": [13, 11]},
                            {"a": [2, 7], "b": [2, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "R1, the feed resistor", "value": "470 Ω"},
                        {"label": "R2, node A to ground", "value": "2.20 kΩ"},
                        {"label": "$r_d$, the converged diode tangent", "value": "1.08 Ω"},
                        {"label": "$V_{eq}$, the tangent's zero-current intercept", "value": "592 mV"},
                    ],
                    # Read from the solve, not restated: the drop across whichever resistor is r1
                    # and that part's own value. A redrawn schematic is re-measured.
                    "check": r'''
const d = c.dc();
const r1 = c.net.parts.filter(function (p) { return p.id === 'r1'; })[0];
const drop = d.v[r1.n1] - d.v[r1.n2];
return drop * drop / r1.value * 1000;
''',
                    "answer": 275.6,
                    "tol": 0.8,
                    "unit": "mW",
                    "hint": r"Find node A first. Three branches meet there: $(12 - v)/470$ arrives, $v/2200$ leaves through R2, and $(v - 0.592)/1.08$ leaves through the diode's tangent. Then the feed resistor has $12 - v$ across it.",
                    "wrong": r"If you got 306 mW, the whole 12 V was put across the feed resistor — the node is not at ground, so the drop is $12 - v_A$. If you got 0.812 mW, $(12 - v_A)^2$ was replaced by $v_A^2$: the power in a resistor uses the drop across *it*, not the voltage at one end of it. If you got 0.174 mW, the sum was done for R2 instead.",
                    "why": r'''
Node A, by summing conductances — the matrix method of module 4 with a single unknown:

```
G = 1/470 + 1/2200 + 1/1.08
  = 0.00212766 + 0.00045455 + 0.9259259     = 0.9285081 S
I = 12/470 + 0.592/1.08
  = 0.0255319 + 0.5481481                   = 0.5736800 A
v = 0.5736800 / 0.9285081                   = 0.617851 V
```

Then the feed resistor:

```
drop  = 12 - 0.617851                       = 11.382149 V
P     = 11.382149^2 / 470 = 129.5533 / 470  = 0.2756453 W
                                            = 275.6 mW
```

A quarter-watt resistor will not do; this needs a half-watt part, or a different design.
And look where the power went. The three currents are 24.22 mA in, 0.28 mA through R2
and 23.94 mA through the diode, so 99% of the current is going through a device dropping
0.62 V, while the resistor that delivers it drops 11.4 V. The diode is burning 14.8 mW
and the feed resistor 276 mW — the circuit is 95% heater. That is the real answer to
"why not bias a reference this way from a 12 V rail", and no amount of care over the
fourth decimal place of the operating point changes it.

One last thing about the arithmetic. The 1.08 Ω branch carries almost all the current
and is a thousand times smaller than everything else in the network, so the conductance
sum is dominated by one term. That is a **stiff** matrix, and it is what makes
non-linear circuit solving numerically awkward in general: the Jacobian of a real
circuit routinely has entries spanning ten orders of magnitude, which is why simulators
pivot carefully and why the module 4 machinery is not optional.
''',
                    "aside": r"The check reads the drop across R1 out of the solved circuit and squares it, rather than trusting the 0.617851 V above — so if the schematic is ever edited, the stated answer has to move with it or the gate fails.",
                },
            ],
            "blanks": {
                "title": "Newton's loop, with five decisions taken out of it",
                "minutes": 10,
                "caption": "Is, VT, vs and R are already in scope, and math is imported",
                "lang": "python",
                "brief": r'''
This is the loop from the lab, reduced to the five lines that carry a decision. Each
blank has one right answer and three that are recognisably a real mistake — the
resistor's demand written without the node voltage, a slope missing a term, a one-sided
limiter, a stopping test on the wrong quantity.

The circuit is the usual one: `vs` through `R` into a diode, and `v` is the diode's
voltage.
''',
                "listing": r'''
def newton(v0, tol=1e-9, max_step=0.1, cap=100):
    v = v0
    for n in range(1, cap + 1):
        i_diode = Is * (math.exp(v / VT) - 1.0)
        f       = i_diode - ___
        g       = ___
        step    = ___
        step    = ___
        v       = v - step
        if abs(___) < tol:
            return v, n
    raise RuntimeError("no convergence in %d steps" % cap)
''',
                "blanks": [
                    {
                        "prompt": "The residual is the diode's current minus the resistor's. What does the resistor demand?",
                        "hole": "?",
                        "opts": ["vs / R", "(vs - v) / R", "v / R", "(vs - v) * R"],
                        "a": 1,
                        "why": "The resistor has whatever the supply has left after the diode's share, so $(V_s - v)/R$. It is the load line, and it has to fall as $v$ rises — that falling line crossing the rising exponential is the entire picture the module is built on.",
                        "whys": [
                            "This is the current that would flow if the diode were a short — the load line's value at $v = 0$, with the slope thrown away. The loop still converges, and that is the danger: on the 5 V, 1 kΩ circuit it settles at 0.5773 V, the voltage at which the diode passes the full 5 mA rather than the 4.43 mA the resistor can actually supply. Wrong by 3.2 mV and entirely plausible-looking.",
                            "The resistor has whatever the supply has left after the diode's share, so $(V_s - v)/R$. It is the load line, and it has to fall as $v$ rises — that falling line crossing the rising exponential is the entire picture the module is built on.",
                            "This is the current through a resistor from the node to *ground*, which is a different circuit — that is the divider of the last numeric question, not the series loop. Here the resistor goes to the supply.",
                            "Volts times ohms is not a current. Multiplying instead of dividing also gets the direction of the dependence backwards: a bigger series resistor must let *less* current through, and this makes it more.",
                        ],
                    },
                    {
                        "prompt": "The slope of the whole residual with respect to v.",
                        "hole": "?",
                        "opts": [
                            "(i_diode + Is) / VT",
                            "(i_diode + Is) / VT + 1.0 / R",
                            "(i_diode + Is) / VT - 1.0 / R",
                            "VT / (i_diode + Is) + R",
                        ],
                        "a": 1,
                        "why": r"Differentiate both terms. The diode gives $I_se^{v/V_T}/V_T$, which is $(i + I_s)/V_T$; the term $-(V_s - v)/R$ gives $+1/R$. Both are positive, which is why this particular residual is strictly increasing and the root is unique.",
                        "whys": [
                            "This is only the diode's contribution. Leaving the resistor out still converges — the step is just slightly too big every time — but it stops being Newton's method, and it is exactly the piece that keeps the denominator away from zero when the diode is off.",
                            r"Differentiate both terms. The diode gives $I_se^{v/V_T}/V_T$, which is $(i + I_s)/V_T$; the term $-(V_s - v)/R$ gives $+1/R$. Both are positive, which is why this particular residual is strictly increasing and the root is unique.",
                            "The sign is wrong. The residual contains $-(V_s - v)/R$, and the only $v$ in it carries a plus, so differentiating gives $+1/R$. With a minus, the two conductances would cancel near where the diode is as stiff as the resistor and the step would blow up at the worst possible moment.",
                            "Both terms have been turned upside down, so this is a resistance in ohms where a conductance in siemens belongs. Dividing a current by it would give volts per ohm squared, which is nothing.",
                        ],
                    },
                    {
                        "prompt": "The correction: where the tangent crosses zero, relative to here.",
                        "hole": "?",
                        "opts": ["g / f", "f * g", "f / g", "-f / g"],
                        "a": 2,
                        "why": "The tangent at $v$ is $y = f + g(x - v)$, and setting $y = 0$ gives $x = v - f/g$. The subtraction happens two lines further down, so what belongs here is $f/g$ on its own.",
                        "whys": [
                            "Upside down. This has units of siemens per amp, and it would grow when the residual shrinks — so the closer the loop got to the answer, the further it would jump.",
                            "A product of a current and a conductance is amps times siemens, which is not a voltage. The tangent construction divides: the height, divided by the slope, is the horizontal distance to the crossing.",
                            "The tangent at $v$ is $y = f + g(x - v)$, and setting $y = 0$ gives $x = v - f/g$. The subtraction happens two lines further down, so what belongs here is $f/g$ on its own.",
                            "The sign is already carried by `v = v - step` below, so putting a minus here as well would double it and send every step in the wrong direction — the guess would run away from the root at exactly the rate it should be running towards it.",
                        ],
                    },
                    {
                        "prompt": "Limit the move, so that a nearly flat tangent cannot throw the guess across the room.",
                        "hole": "?",
                        "opts": [
                            "min(max_step, step)",
                            "max(-max_step, min(max_step, step))",
                            "max(-max_step, min(max_step, v))",
                            "abs(step)",
                        ],
                        "a": 1,
                        "why": "Clamp on both sides, and clamp the *step*. A one-sided clamp leaves the other direction free, and a two-sided clamp applied to the voltage instead of the move is not a limiter at all.",
                        "whys": [
                            "`min` caps `step` from above only, so a large *negative* step passes through untouched — and a large negative step is exactly what a guess below the root produces. From 0 V the first step is $-5$ V, it sails through this test unaltered, and the limiter has done nothing.",
                            "Clamp on both sides, and clamp the *step*. A one-sided clamp leaves the other direction free, and a two-sided clamp applied to the voltage instead of the move is not a limiter at all.",
                            "This puts the *voltage* through the limiter and then subtracts the result as though it were a step. From 0.6 V it computes `min(0.1, 0.6) = 0.1`, subtracts that, and goes on marching down 0.1 V at a time whatever the residual says — finally returning 0 V, which satisfies the stopping test perfectly and is not the answer.",
                            "Throwing away the sign makes every step positive, and since the update *subtracts* it the guess can then only ever fall. From 0 V the first move takes it to $-5$ V and the next to $-15$ V, and it never comes back.",
                        ],
                    },
                    {
                        "prompt": "What has to be small before you can say you have arrived?",
                        "hole": "?",
                        "opts": ["f", "step", "i_diode", "v - v0"],
                        "a": 1,
                        "why": "The step. Once the method is converging quadratically the step you have just taken is very nearly the error you have just removed, it is in volts like the answer, and it needs no knowledge of the scale of the currents.",
                        "whys": [
                            "The residual is in amps, and on an exponential its size says almost nothing about the distance to the root — 2.7 mA of residual is 24 mV of error at 0.55 V, while 79 mA is 76 mV at 0.65 V. It is a useful *confirmation* alongside the step, and a bad measurement on its own.",
                            "The step. Once the method is converging quadratically the step you have just taken is very nearly the error you have just removed, it is in volts like the answer, and it needs no knowledge of the scale of the currents.",
                            "The diode's current is not small at the answer — it is 4.4 mA — so this test would never pass, and if it did it would mean the diode had switched off rather than that the loop had converged.",
                            "The total distance travelled since the start is not a convergence test: it is large precisely when the loop has done the most work. It would also be satisfied immediately by a guess that happened to start at the answer, which is right for the wrong reason.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "The operating point of a diode, found by iteration",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
One supply, one resistor, one diode, in a loop. The diode passes
$i = I_s\left(e^{v/V_T} - 1\right)$ and the resistor demands $i = (V_s - v)/R$; the
operating point is the single voltage where those agree. You are going to find it
twice.

Write four functions.

`diode_current(v, Is, VT)` — the diode law.

`residual(v, vs, R, Is, VT)` — the diode's current minus the resistor's, which is
zero at the answer and has opposite signs either side of it.

`bisect(vs, R, lo, hi, tol, Is, VT)` — halve the bracket until it is narrower than
`tol`, and return the pair `(voltage, steps)`. Keep whichever half still has the sign
change across it: compare the sign at the midpoint with the sign at `lo`.

`newton(vs, R, v0, tol, max_step, Is, VT)` — the update from the derivation,
$v \leftarrow v - f/(g + 1/R)$ with $g = \frac{I_s}{V_T}e^{v/V_T}$, returning
`(voltage, steps)`. Stop when the step is smaller than `tol`.

**The limiter is not optional.** At $v = 0$ the diode's slope is essentially zero, so
the first Newton step is about $V_s$ and lands the guess on the supply rail. From up
there every further step is worth only one $V_T$ — 25.85 mV — so the unlimited method
needs about 170 iterations to crawl back down; and on any supply past 18.3 V it does
not crawl at all, because $e^{v/V_T}$ overflows a float and the run stops. Clamp every
step to at most `max_step` volts in either direction. Every SPICE ever written does
this, for this reason.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def diode_current(v, Is=1e-12, VT=0.02585):
    """Is * (exp(v / VT) - 1)."""
    # TODO
    return 0.0


def residual(v, vs, R, Is=1e-12, VT=0.02585):
    """The diode's current minus the resistor's. Zero at the operating point."""
    # TODO
    return 0.0


def bisect(vs, R, lo, hi, tol=1e-9, Is=1e-12, VT=0.02585):
    """Halve the bracket until it is narrower than tol. Return (voltage, steps)."""
    # TODO
    return (0.0, 0)


def newton(vs, R, v0=0.0, tol=1e-12, max_step=0.1, Is=1e-12, VT=0.02585):
    """Newton's method with a step limiter. Return (voltage, steps)."""
    # TODO
    return (0.0, 0)


if __name__ == "__main__":
    vb, nb = bisect(5.0, 1000.0, 0.0, 5.0)
    vn, nn = newton(5.0, 1000.0, 0.0)
    print("bisection:", round(vb, 9), "V in", nb, "steps")
    print("newton   :", round(vn, 9), "V in", nn, "steps")
    print("current  :", round(diode_current(vn) * 1000, 6), "mA")
    print("residual :", residual(vn, 5.0, 1000.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def diode_current(v, Is=1e-12, VT=0.02585):
    """Is * (exp(v / VT) - 1)."""
    return Is * (math.exp(v / VT) - 1.0)


def residual(v, vs, R, Is=1e-12, VT=0.02585):
    """The diode's current minus the resistor's. Zero at the operating point."""
    return diode_current(v, Is, VT) - (vs - v) / R


def bisect(vs, R, lo, hi, tol=1e-9, Is=1e-12, VT=0.02585):
    """Halve the bracket until it is narrower than tol. Return (voltage, steps)."""
    flo = residual(lo, vs, R, Is, VT)
    steps = 0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        fmid = residual(mid, vs, R, Is, VT)
        steps += 1
        if (fmid > 0.0) == (flo > 0.0):
            lo, flo = mid, fmid
        else:
            hi = mid
    return (0.5 * (lo + hi), steps)


def newton(vs, R, v0=0.0, tol=1e-12, max_step=0.1, Is=1e-12, VT=0.02585):
    """Newton's method with a step limiter. Return (voltage, steps)."""
    v = v0
    for steps in range(1, 201):
        f = residual(v, vs, R, Is, VT)
        g = Is / VT * math.exp(v / VT) + 1.0 / R
        step = f / g
        if step > max_step:
            step = max_step
        elif step < -max_step:
            step = -max_step
        v -= step
        if abs(step) < tol:
            return (v, steps)
    raise RuntimeError("no convergence in 200 steps")


if __name__ == "__main__":
    vb, nb = bisect(5.0, 1000.0, 0.0, 5.0)
    vn, nn = newton(5.0, 1000.0, 0.0)
    print("bisection:", round(vb, 9), "V in", nb, "steps")
    print("newton   :", round(vn, 9), "V in", nn, "steps")
    print("current  :", round(diode_current(vn) * 1000, 6), "mA")
    print("residual :", residual(vn, 5.0, 1000.0))
'''}],
                "hints": [
                    r"`diode_current(0)` must be exactly 0: the $-1$ in the law is there so that no current flows with no voltage across it.",
                    r"In `bisect`, compute the residual at `lo` once before the loop and carry it along. Recomputing it every pass works too, but the sign test is the only thing it is for.",
                    r"In `newton`, apply the limiter to the *step*, not to the voltage: `if step > max_step: step = max_step`, and the mirror image for the negative direction. Clamping the voltage instead would stop it converging at all.",
                    r"Count a step every time you move, and return as soon as the move is smaller than `tol`. Testing the residual instead is legitimate but harder to scale: the residual is in amps, and a milliamp of it means something very different at 1 mA than at 1 A.",
                    r"If `newton` returns the right voltage but takes 170-odd steps rather than a dozen, the limiter is missing rather than wrong: from 0 V the first unlimited step reaches the supply rail, and from there the method walks back down at one $V_T$ per iteration.",
                ],
                "tests": [
                    {"name": "the diode law itself", "code": r'''
import math
assert abs(diode_current(0.0)) < 1e-18, f"no voltage, no current — got {diode_current(0.0)}"
_i = diode_current(0.6)
assert abs(_i - 0.012031953282638291) < 1e-9, f"expected 12.03 mA at 0.6 V, got {_i * 1000} mA"
_i2 = diode_current(0.6 + 0.02585 * math.log(10.0))
assert abs(_i2 / _i - 10.0) < 1e-6, \
    "one decade of current should cost VT*ln(10) = 59.5 mV, and does not here"
'''},
                    {"name": "the residual changes sign across the answer", "code": r'''
assert residual(0.0, 5.0, 1000.0) < 0, "at 0 V the resistor wants to push more current than the diode takes"
assert residual(0.8, 5.0, 1000.0) > 0, "at 0.8 V the diode would take far more than the resistor can supply"
'''},
                    {"name": "bisection finds the operating point", "code": r'''
_v, _n = bisect(5.0, 1000.0, 0.0, 5.0)
assert abs(_v - 0.5741473389) < 1e-6, f"expected 0.574147 V, got {_v}"
assert 25 <= _n <= 60, f"halving a 5 V bracket to a nanovolt takes about 33 steps, got {_n}"
assert abs(residual(_v, 5.0, 1000.0)) < 1e-9, "the residual at the answer should be tiny"
'''},
                    {"name": "newton finds the same point from a standing start", "code": r'''
try:
    _v, _n = newton(5.0, 1000.0, 0.0)
except OverflowError:
    raise AssertionError("the first step from 0 V ran away and the exponential overflowed — "
                         "clamp each step to max_step volts")
assert abs(_v - 0.5741473392) < 1e-8, f"expected 0.574147 V, got {_v}"
assert _n <= 25, f"with a 0.1 V limiter this takes about 12 steps, got {_n}"
'''},
                    {"name": "newton is the faster of the two", "code": r'''
_vb, _nb = bisect(5.0, 1000.0, 0.0, 5.0)
_vn, _nn = newton(5.0, 1000.0, 0.0)
assert abs(_vb - _vn) < 1e-6, f"the two methods disagree: {_vb} against {_vn}"
assert _nn < _nb, f"newton took {_nn} steps and bisection {_nb} — newton should need fewer"
'''},
                    {"name": "a different supply and resistor", "code": r'''
_v, _n = newton(3.3, 220.0, 0.0)
assert abs(_v - 0.6005073) < 1e-6, f"expected 0.600507 V for 3.3 V through 220 ohms, got {_v}"
_i = diode_current(_v)
assert abs(_i - 0.01227042) < 1e-7, f"that is 12.27 mA, got {_i * 1000} mA"
_v2, _n2 = newton(1.5, 10000.0, 0.0)
assert abs(_v2 - 0.4767683) < 1e-6, f"expected 0.476768 V at 0.1 mA, got {_v2}"
'''},
                    {"name": "doubling the saturation current costs one VT ln 2", "code": r'''
import math
_v1, _ = newton(5.0, 1000.0, 0.0)
_v2, _ = newton(5.0, 1000.0, 0.0, Is=2e-12)
_shift = _v1 - _v2
assert 0.0 < _shift, "a leakier diode should sit at a lower voltage for nearly the same current"
assert abs(_shift - 0.02585 * math.log(2.0)) < 5e-4, \
    f"expected a shift of about 17.9 mV, got {_shift * 1000:.3f} mV"
'''},
                    {"name": "starting from a good guess needs fewer steps", "code": r'''
_v0, _n0 = newton(5.0, 1000.0, 0.0)
_v6, _n6 = newton(5.0, 1000.0, 0.6)
assert abs(_v0 - _v6) < 1e-8, "the answer must not depend on where you started"
assert _n6 < _n0, f"from 0.6 V it should take fewer steps than from 0 V, got {_n6} against {_n0}"
'''},
                ],
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "Vectors: adding, projecting and turning",
            "summary": "Three numbers where there was one, and two different products that answer two different questions. Fields and forces do not fit on a number line.",
            "concepts": [
                r"A **vector** carries a magnitude and a direction. Written in components, $\mathbf{a} = (a_x, a_y, a_z)$, and its magnitude is $|\mathbf{a}| = \sqrt{a_x^2 + a_y^2 + a_z^2}$ — Pythagoras, applied twice.",
                r"Addition and scaling work one component at a time. Multiplying by a positive number keeps the direction and changes the length; by a negative number, reverses the direction. A **unit vector** $\hat{\mathbf{a}} = \mathbf{a}/|\mathbf{a}|$ has length 1 and carries the direction alone.",
                r"The **dot product** $\mathbf{a}\cdot\mathbf{b} = a_xb_x + a_yb_y + a_zb_z = |\mathbf{a}||\mathbf{b}|\cos\theta$ produces a plain *number*. It is zero exactly when the two are perpendicular, and it measures how much of one lies along the other.",
                r"The **cross product** $\mathbf{a}\times\mathbf{b}$ produces a *vector*, perpendicular to both, of magnitude $|\mathbf{a}||\mathbf{b}|\sin\theta$, pointing the way the right-hand rule says. It is zero exactly when the two are parallel, and swapping the order reverses it: $\mathbf{b}\times\mathbf{a} = -\mathbf{a}\times\mathbf{b}$.",
                r"Which product to reach for is decided by what comes out. Work is $\mathbf{F}\cdot\mathbf{d}$ and the flux through a flat loop is $\mathbf{B}\cdot\mathbf{A}$ — both numbers, both carrying the $\cos\theta$. The force on a charge moving through a magnetic field is $q\,\mathbf{v}\times\mathbf{B}$, a vector, and that is why the force comes out sideways to both.",
                r"Adding several fields at a point is vector addition, component by component. *Superposition*, when EE141 says it, means exactly this and nothing more.",
                r"The two products between the same pair are not independent: $(\mathbf{a}\cdot\mathbf{b})^2 + |\mathbf{a}\times\mathbf{b}|^2 = |\mathbf{a}|^2|\mathbf{b}|^2$, which is $\cos^2\theta + \sin^2\theta = 1$ wearing components.",
            ],
            "read": [
                {
                    "title": "Three numbers where one will not do",
                    "minutes": 13,
                    "body": r'''
Two people push a stalled car, each with a steady 400 newtons. How hard is the car
being pushed?

The question has no answer yet. If both are behind the boot, the car feels 800 N. If
one of them has walked round to the front, it feels nothing at all. If one pushes from
behind and the other from the driver's door, it feels $400\sqrt{2} = 566$ N and sets
off diagonally across the road. Three different answers out of the same two numbers,
and the reason is that "400 N" was never the whole of what either person contributed.
The other half of it — *which way* — was left out, and in this problem it matters more
than the size does.

A quantity that needs a direction as well as a size is a **vector**. Force is one; so
are velocity, acceleration, the electric field, the magnetic field, and the position
of one point relative to another. A quantity that needs no direction is a **scalar**:
temperature, charge, resistance, energy, time. The distinction is not a matter of
taste or notation. Two 400 N pushes can between them produce anything from 0 N to
800 N. Two 5 Ω resistors in series produce 10 Ω, always, and there is no further
information anyone could supply that would change it.

## Three questions with fixed answers

Direction is awkward to write down. "North-east and a bit up" is not something you can
put in an equation. The trick that makes vectors calculable is to stop describing the
direction and start asking three fixed questions instead.

Choose three directions at right angles to one another once and for all — call them
$x$, $y$ and $z$ — and then ask of any vector: *how much of you points along $x$? along
$y$? along $z$?* The three answers are ordinary signed real numbers, and they pin the
vector down completely. Write them as a triple:

$$\mathbf{a} = (a_x,\,a_y,\,a_z)$$

These are the **components**. A component can be negative, and that is not a defect —
it means "along that axis, but the other way". The bold letter is the vector itself,
the thing in the world; the triple is what you get when you interrogate it with a
particular set of axes. Those are not the same kind of object, and the difference
becomes important at the end of this unit.

Two vectors are equal when all three components match. There is no partial credit and
no ordering: you cannot ask whether $\mathbf{a} > \mathbf{b}$, because "bigger" would
have to mean bigger in every direction at once, and usually it is bigger in one and
smaller in another.

## Adding: why one component at a time is allowed

Put both people back behind the car. What the car does is decided by a single effective
force, and the experimental fact — it is a fact about the world, not a definition — is
that the effective force is found by laying the two arrows nose to tail and drawing the
arrow that closes the gap. Nothing about the two pushes is lost and nothing extra
appears. This is **superposition**, and when EE141 uses the word about circuits it means
exactly this and nothing more.

Once that is granted, components add one at a time, and the reason is worth being clear
about. The $x$ question — *how much of you points along $x$?* — is answered by each
force separately, and laying arrows nose to tail moves you along $x$ by the first
answer and then by the second. The $y$ and $z$ questions never enter into it. So

$$\mathbf{a} + \mathbf{b} = (a_x + b_x,\,a_y + b_y,\,a_z + b_z)$$

and subtraction is the same with minus signs. Scaling is the same idea again:
$3\mathbf{a} = (3a_x,\,3a_y,\,3a_z)$ is three times as long in the same direction, and
$-\mathbf{a}$ is the same length pointing the opposite way. Multiplying by a number
never turns a vector; it only stretches it, or reverses it, or both.

## The length, from Pythagoras used twice

The **magnitude** $|\mathbf{a}|$ is how long the arrow is. Getting it from components is
Pythagoras applied twice, and the second application is the one people forget they are
doing.

Start on the floor. The $x$ and $y$ components lay out a right-angled triangle whose
hypotenuse is the shadow of the arrow on the floor, of length
$\sqrt{a_x^2 + a_y^2}$. Now stand that shadow up: the shadow and the vertical component
$a_z$ are themselves the two short sides of a right-angled triangle, because $z$ is
perpendicular to the whole floor. So the arrow itself has length

$$|\mathbf{a}| = \sqrt{\left(\sqrt{a_x^2 + a_y^2}\right)^2 + a_z^2} = \sqrt{a_x^2 + a_y^2 + a_z^2}$$

The inner square root cancels against the outer square, which is why the finished
formula shows no sign of having been built in two stages. It is the same calculation as
the modulus of a complex number in module 1, with one more term.

Dividing a vector by its own length gives a vector of length 1 pointing the same way,
written $\hat{\mathbf{a}} = \mathbf{a}/|\mathbf{a}|$ and called a **unit vector**. It
carries the direction and nothing else, which makes it the natural way to say "along
the rail" or "towards the antenna" without also saying how far. Any vector can then be
split into its two halves of information: $\mathbf{a} = |\mathbf{a}|\,\hat{\mathbf{a}}$,
a size times a direction.

### Worked: the load on a bracket

A bracket on a wall carries two struts. Strut 1 pulls with
$\mathbf{F}_1 = (60,\,25,\,0)$ N and strut 2 with $\mathbf{F}_2 = (-20,\,45,\,30)$ N.
What single force is the bracket actually holding, and how big is it?

```
|F1| = sqrt(60^2 + 25^2 + 0)      = sqrt(3600 + 625)        = sqrt(4225)  = 65.00 N
|F2| = sqrt(20^2 + 45^2 + 30^2)   = sqrt(400 + 2025 + 900)   = sqrt(3325)  = 57.66 N

R = F1 + F2 = (60 - 20, 25 + 45, 0 + 30) = (40, 70, 30) N

|R| = sqrt(40^2 + 70^2 + 30^2) = sqrt(1600 + 4900 + 900) = sqrt(7400) = 86.02 N
```

Note what did *not* happen: $65.00 + 57.66 = 122.66$ N, and the bracket is not carrying
122.66 N. It is carrying 86.02 N, because the two struts are pulling partly against
each other — strut 1 pulls in the $+x$ direction and strut 2 partly back the other way.

The direction of the resultant is its unit vector:

```
R_hat = (40, 70, 30) / 86.02 = (0.4650, 0.8137, 0.3487)

angle to x:  arccos(0.4650) = 62.29 deg
angle to y:  arccos(0.8137) = 35.54 deg
angle to z:  arccos(0.3487) = 69.59 deg

check:  0.4650^2 + 0.8137^2 + 0.3487^2 = 0.2162 + 0.6622 + 0.1216 = 1.0000
```

Those three cosines are the **direction cosines**, and the check at the bottom is not
decoration: the components of any unit vector must square to 1, so if they do not, an
arithmetic slip happened somewhere above and it is cheaper to find it here than in the
next question. Note also that the three angles do not add to anything meaningful —
$62.29 + 35.54 + 69.59 = 167.4°$ is not a quantity. Angles to three different axes are
not angles in a triangle.

### Worked: three sources, one point

Three charges each set up an electric field at the same point in space. Measured
against the same axes, their contributions are

$$\mathbf{E}_1 = (1200,\,0,\,0), \quad \mathbf{E}_2 = (-300,\,800,\,0), \quad
\mathbf{E}_3 = (0,\,-500,\,900)\,\text{V/m}$$

The field at that point is their vector sum, and nothing else — this is the whole
content of superposition for fields.

```
E = (1200 - 300 + 0,  0 + 800 - 500,  0 + 0 + 900) = (900, 300, 900) V/m

|E| = sqrt(900^2 + 300^2 + 900^2)
    = sqrt(810000 + 90000 + 810000)
    = sqrt(1710000) = 1307.7 V/m

E_hat = (900, 300, 900) / 1307.7 = (0.6882, 0.2294, 0.6882)
```

Individually the three fields have magnitudes 1200, 854.4 and 1029.6 V/m, adding to
3084.0 V/m. The actual field is 1307.7 V/m, well under half of that, and a voltmeter at
that point would agree with 1307.7. The scalar sum is not a bound anybody uses, an
estimate anybody uses, or a number with a physical meaning; it is simply the wrong
calculation.

## The mistake, and why it is tempting

The mistake is adding the magnitudes. It is tempting for two good reasons. The first is
ten years of practice: for everything school arithmetic offered — money, mass, litres —
adding the sizes was not merely allowed, it was the definition of combining. The second
is that it is *sometimes right*, so it survives the first few encounters. Hang two
weights on one string and the tensions really do add as numbers, because the two forces
point the same way and $\cos 0 = 1$. Every case where the vectors are parallel and
agree in direction is a case where the shortcut works, which is exactly the set of
cases a first example is likely to be drawn from.

The way to keep it straight is to remember what the sum has to be able to do. It has to
be able to come out as *zero* when two equal pushes oppose each other, and no sum of
positive magnitudes can ever be zero. So magnitudes cannot be the things being added.

A second, quieter mistake is treating a component as though it were a length. Lengths
are never negative; components frequently are, and the sign is carrying the direction.
Writing $|(-20,\,45,\,30)| = -20 + 45 + 30$ produces 55, which is neither the magnitude
(57.66) nor anything else.

## Where this stops holding

**Components belong to axes, the vector does not.** Turn your axes by 30° and every
component of every vector changes, while the struts on the wall pull exactly as they
did. So a claim about components alone is only half a claim; it needs the axes named.
The magnitude, by contrast, is unchanged by any rotation of the axes, which is why it
is worth computing as a check whenever you change frames.

**Not every triple of numbers is a vector.** The three resistor values in a divider,
$(R_1, R_2, R_3)$, form a perfectly good list, but adding two such lists componentwise
describes nothing, and there is no sense in which rotating your axes ought to mix $R_1$
into $R_2$. What makes a triple a vector is that its components change together, in the
one specific way, when the axes turn. A list of unrelated numbers does not.

**Even some quantities with a size and a direction are not vectors.** A rotation of a
rigid body has a magnitude (the angle) and a direction (the axis), and it is still not a
vector, because vector addition is commutative and rotations are not. Turn a matchbox
90° about $x$ and then 90° about $y$, then do the same two turns in the other order: the
matchbox ends up in two different orientations. Anything that fails
$\mathbf{a} + \mathbf{b} = \mathbf{b} + \mathbf{a}$ is not in this subject.

**A vector says nothing about where it acts.** $\mathbf{F}_1 + \mathbf{F}_2$ gives the
resultant force on the bracket, and if the two struts meet at a point that is the whole
story. If they do not, the bracket may also be twisted, and the twist is invisible to
this sum. Recovering it needs a second kind of product and a position vector, which is
the third unit of this module.
''',
                },
                {
                    "title": "The dot product: how much of one lies along the other",
                    "minutes": 14,
                    "body": r'''
Drag a sledge across a field with a rope. The rope is not horizontal — it comes off the
sledge and up to your shoulder — so the pull has an upward part and a forward part. The
sledge goes forward. The upward part of the pull does not push it forward at all; all
it does is take some weight off the runners.

Now ask how much energy you spent. Energy is a scalar: joules, no direction. But the
two things it depends on, the pull and the movement, are both vectors, and only the
part of the pull that lies *along* the movement contributed anything. There has to be a
way of combining two vectors that throws away everything except the part they have in
common and hands back a plain number. That is the **dot product**, and this unit is
about where its two faces come from and why they agree.

## The shadow

Stand a vector $\mathbf{a}$ up against a second vector $\mathbf{b}$ and shine a light
straight down onto $\mathbf{b}$'s line. The shadow $\mathbf{a}$ casts along that line
has length $|\mathbf{a}|\cos\theta$, where $\theta$ is the angle between them: the
shadow is the adjacent side of a right-angled triangle whose hypotenuse is $\mathbf{a}$.

That length is the **projection** of $\mathbf{a}$ onto $\mathbf{b}$, and it is signed.
If $\theta$ is more than 90° the cosine is negative and the shadow falls on the far side
of the origin — the vector is leaning away rather than along. If $\theta$ is exactly 90°
there is no shadow at all.

Multiply that shadow by the length of $\mathbf{b}$ and you have the dot product:

$$\mathbf{a}\cdot\mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$$

Why multiply by $|\mathbf{b}|$ as well, rather than stopping at the shadow? Because the
quantities the definition is built for are products of two sizes. Work is a force times
a distance, not a force times a direction; flux is a field times an area. Building
$|\mathbf{b}|$ into the definition means work is simply $\mathbf{F}\cdot\mathbf{d}$ with
nothing left over. The plain shadow is still available when you want it — it is
$\mathbf{a}\cdot\hat{\mathbf{b}}$, the dot product with the *unit* vector along
$\mathbf{b}$ — and forgetting that division by $|\mathbf{b}|$ is the standard slip.

## From geometry to components

The geometric definition cannot be computed: you rarely know $\theta$. What you know is
components. So the two forms have to be connected, and the connection is the law of
cosines.

Draw the triangle with sides $\mathbf{a}$ and $\mathbf{b}$ from a common point; the
third side is $\mathbf{a} - \mathbf{b}$. The law of cosines says

$$|\mathbf{a} - \mathbf{b}|^2 = |\mathbf{a}|^2 + |\mathbf{b}|^2 - 2|\mathbf{a}||\mathbf{b}|\cos\theta$$

Now work out the left-hand side in components, using nothing but Pythagoras and
ordinary algebra:

```
|a - b|^2 = (ax - bx)^2 + (ay - by)^2 + (az - bz)^2

          = ax^2 - 2 ax bx + bx^2
          + ay^2 - 2 ay by + by^2
          + az^2 - 2 az bz + bz^2

          = (ax^2 + ay^2 + az^2) + (bx^2 + by^2 + bz^2) - 2(ax bx + ay by + az bz)

          = |a|^2 + |b|^2 - 2(ax bx + ay by + az bz)
```

Set the two expressions side by side. The $|\mathbf{a}|^2$ and $|\mathbf{b}|^2$ cancel,
the factor of $-2$ cancels, and what is left is

$$a_xb_x + a_yb_y + a_zb_z = |\mathbf{a}||\mathbf{b}|\cos\theta$$

Both sides are the dot product. The left is arithmetic anyone can do; the right contains
the angle. Every use of this product is one of the two sides being swapped for the
other.

One consequence falls out immediately: $\mathbf{a}\cdot\mathbf{a} = |\mathbf{a}|^2$,
since $\theta = 0$. A vector dotted with itself is its length squared, which is often
more convenient than the length because it has no square root in it.

## The sign, before any arithmetic

Because $|\mathbf{a}|$ and $|\mathbf{b}|$ are never negative, the sign of the dot
product is the sign of $\cos\theta$ alone:

```
a . b  >  0      the angle is under 90 deg   -- they broadly agree
a . b  =  0      the angle is exactly 90 deg -- perpendicular
a . b  <  0      the angle is over 90 deg    -- they broadly oppose
```

Three multiplications and two additions tell you which side of a right angle two
directions are on, with no square roots and no inverse cosine. That is worth having on
its own, and the middle line is worth more still: *perpendicular* is the same statement
as *dot product zero*, and that is how perpendicularity is imposed in practice — not by
measuring an angle but by writing an equation that says a dot product vanishes.

### Worked: the rope on the sledge

You pull with 250 N along a rope at 35° above the horizontal, and the sledge moves 12 m
horizontally. How much work did you do?

Geometric form first, because here the angle is the thing you were given:

```
W = |F| |d| cos(theta) = 250 * 12 * cos(35 deg)
                       = 3000 * 0.81915
                       = 2457.5 J
```

Now the same thing in components, to see the two forms meet. Put $x$ along the ground
and $y$ up:

```
F = (250 cos35, 250 sin35, 0) = (204.79, 143.39, 0) N
d = (12, 0, 0) m

F . d = 204.79*12 + 143.39*0 + 0*0 = 2457.5 J
```

The vertical 143.39 N was multiplied by zero displacement and dropped out of its own
accord. Nobody had to decide to ignore it. That is the dot product doing the job it was
built for: the geometry decides what is relevant, not the person doing the sum.

### Worked: splitting a force into along and across

A force $\mathbf{a} = (5,\,2,\,-4)$ N acts on a carriage that can only move along a rail
whose direction is $\mathbf{b} = (2,\,3,\,6)$. How much of the force drives the carriage,
and how much is wasted pressing it into the rail?

```
a . b  =  5*2 + 2*3 + (-4)*6  =  10 + 6 - 24  =  -8

|b| = sqrt(4 + 9 + 36) = sqrt(49) = 7
|a| = sqrt(25 + 4 + 16) = sqrt(45) = 6.7082
```

The dot product is negative before anything else is worked out, so the force is pushing
the carriage *backwards* along the rail. The along-the-rail component is the shadow —
the dot product with the unit vector, not with $\mathbf{b}$ itself:

```
along = a . b_hat = (a . b) / |b| = -8 / 7 = -1.1429 N
```

To get the along-the-rail piece as a vector, multiply that length by the unit vector
again, which divides by $|\mathbf{b}|$ a second time:

```
a_par = ((a . b) / |b|^2) b = (-8/49)(2, 3, 6) = (-0.3265, -0.4898, -0.9796) N

a_perp = a - a_par = (5.3265, 2.4898, -3.0204) N
```

Two checks, and both are worth doing every time. First, the leftover really is
perpendicular to the rail:

```
a_perp . b = 5.3265*2 + 2.4898*3 + (-3.0204)*6
           = 10.6531 + 7.4694 - 18.1224 = 0.0000
```

Second, the two pieces are at right angles, so their lengths satisfy Pythagoras against
the original:

```
|a_perp| = sqrt(45 - 1.1429^2) = sqrt(45 - 1.3061) = sqrt(43.6939) = 6.6101 N

check: sqrt(1.1429^2 + 6.6101^2) = sqrt(1.3061 + 43.6939) = sqrt(45) = 6.7082 = |a|
```

So of a 6.71 N force, 1.14 N drives the carriage (backwards) and 6.61 N is absorbed by
the rail. And the angle, if you want it:

```
cos(theta) = -8 / (6.7082 * 7) = -8 / 46.9574 = -0.17037
theta      = 99.81 deg
```

Just over a right angle, which agrees with the sign of the dot product having been
barely negative.

## The mistakes

**Expecting a vector back.** The commonest error is multiplying component by component
and keeping three numbers: $(1,2,3)\cdot(4,-5,6) = (4,-10,18)$. That triple is a
perfectly computable thing, but it is not a product of vectors, it depends on the axes
in a way no physical quantity does, and it is not what any formula in the subject means.
The dot product is the sum $4 - 10 + 18 = 12$. Adding the three is the entire point:
it is what makes the answer independent of which axes you chose.

**Dividing by the wrong thing.** To project $\mathbf{a}$ onto $\mathbf{b}$ you divide by
$|\mathbf{b}|$, the vector you are projecting *onto*. Dividing by $|\mathbf{a}|$ gives
$|\mathbf{b}|\cos\theta$, the shadow the other way round, and the two are only equal
when the magnitudes happen to be equal. When in doubt, check the units: a force
projected on a direction must come out in newtons.

**Reading zero as "one of them is zero".** $\mathbf{a}\cdot\mathbf{b} = 0$ with both
non-zero is the ordinary and useful case, not a degenerate one. Real multiplication has
no such thing, which is why it is unfamiliar.

## Where this stops holding

**The component formula assumes the axes are at right angles and one unit long.** If
they are not — skewed crystal axes, a coordinate system stretched along one direction —
then $\mathbf{a}\cdot\mathbf{b}$ is *not* $\sum a_ib_i$, and recovering it needs a
matrix of correction factors between the axes, called the metric. The geometric
definition $|\mathbf{a}||\mathbf{b}|\cos\theta$ survives untouched, because it never
mentioned axes. Whenever a formula in components disagrees with a formula in geometry,
it is the one that names axes that has extra conditions attached.

**Complex components need a conjugate.** Module 2 turned every sinusoid into a phasor,
a complex number, and a three-phase system or a two-port network is naturally a vector
of them. For such a vector $\sum a_i^2$ is a disaster: $(1, j)$ would have
$1 + j^2 = 0$ for its length squared while being a perfectly ordinary non-zero object.
The repair is to conjugate one side, $\sum a_i b_i^{*}$, which makes
$\mathbf{a}\cdot\mathbf{a}^{*} = \sum|a_i|^2$ real and positive again. This is not an
exotic case in electrical engineering: it is why average power is
$P = \tfrac12\,\mathrm{Re}(V I^{*})$ and not $\tfrac12 VI$, and the conjugate in that
formula is there for exactly this reason.

**It cannot tell clockwise from anticlockwise.** $\mathbf{a}\cdot\mathbf{b}$ and
$\mathbf{b}\cdot\mathbf{a}$ are the same number, so no dot product can ever distinguish
turning one way from turning the other. Every question about twisting, circulation or
handedness is invisible to it, and needs the other product.
''',
                },
                {
                    "title": "The cross product: the answer that comes out sideways",
                    "minutes": 14,
                    "body": r'''
Put a spanner on a nut and push the end of it. The nut turns. Push twice as hard and it
turns twice as insistently; use a spanner twice as long and the same push does the same
job again. But push along the spanner, straight towards the nut, and nothing turns at
all, however hard you push.

So the effect depends on two vectors — where you push (the position of your hand
relative to the nut) and how you push — and it vanishes when they are parallel, which is
precisely when the dot product is largest. Worse, the answer is not a plain number.
"The nut turns" is incomplete until you say which way, and *which way* here means an
axis to turn about and a sense of rotation around it. The result of this combination has
to be a vector, and it has to point along the spanner's axis of rotation, which is
perpendicular to both the things that went in.

That is the **cross product**, written $\mathbf{a}\times\mathbf{b}$. It is the second of
the two products, it is unrelated to the first, and it exists because a whole family of
physical effects come out sideways to their causes.

## The size: an area

Take two vectors from a common point. They span a parallelogram. Its base is
$|\mathbf{b}|$ and its perpendicular height is $|\mathbf{a}|\sin\theta$ — the part of
$\mathbf{a}$ that stands *across* $\mathbf{b}$, the leftover from the last unit — so its
area is

$$|\mathbf{a}\times\mathbf{b}| = |\mathbf{a}||\mathbf{b}|\sin\theta$$

That is the magnitude of the cross product, and the $\sin$ against the dot product's
$\cos$ is the whole difference between them in one symbol. It is largest when the two
are perpendicular and zero when they are parallel, which is the spanner's behaviour
exactly: a push straight at the nut spans no area and turns nothing.

The direction is the normal to that parallelogram. There are two of those, one on each
face, and no amount of geometry picks between them — the choice is a convention. The
convention is the **right-hand rule**: point the fingers of your right hand along
$\mathbf{a}$, curl them towards $\mathbf{b}$, and your thumb points along
$\mathbf{a}\times\mathbf{b}$. Swap the two vectors and your hand has to turn over, so

$$\mathbf{b}\times\mathbf{a} = -\,\mathbf{a}\times\mathbf{b}$$

The cross product is the one product in this course where order matters. It also
follows that $\mathbf{a}\times\mathbf{a} = \mathbf{0}$, both because $\sin 0 = 0$ and
because anything equal to minus itself is zero.

## Building the components

Three rules and the ordinary distributive law generate the whole formula. Let
$\hat{\mathbf{x}}, \hat{\mathbf{y}}, \hat{\mathbf{z}}$ be unit vectors along the axes,
chosen right-handed, so that

$$\hat{\mathbf{x}}\times\hat{\mathbf{y}} = \hat{\mathbf{z}}, \qquad
\hat{\mathbf{y}}\times\hat{\mathbf{z}} = \hat{\mathbf{x}}, \qquad
\hat{\mathbf{z}}\times\hat{\mathbf{x}} = \hat{\mathbf{y}}$$

Each of these is two perpendicular unit vectors, so the magnitude is $1\times1\times1$,
and the direction is whichever axis is left over. Reversing any one of them puts a minus
sign in front, and each axis crossed with itself is zero.

Now expand. Nine terms, of which three are zero:

```
a x b = (ax x^ + ay y^ + az z^) x (bx x^ + by y^ + bz z^)

  ax bx (x^ x x^) = 0                ax by (x^ x y^) = + ax by z^
  ay by (y^ x y^) = 0                ax bz (x^ x z^) = - ax bz y^
  az bz (z^ x z^) = 0                ay bx (y^ x x^) = - ay bx z^
                                     ay bz (y^ x z^) = + ay bz x^
                                     az bx (z^ x x^) = + az bx y^
                                     az by (z^ x y^) = - az by x^

collect x^ :  ay bz - az by
collect y^ :  az bx - ax bz
collect z^ :  ax by - ay bx
```

$$\mathbf{a}\times\mathbf{b} = (a_yb_z - a_zb_y,\,\,a_zb_x - a_xb_z,\,\,a_xb_y - a_yb_x)$$

Each component is built from the two axes that are *not* it, in cyclic order
$x \to y \to z \to x$, minus the same pair the other way round. Written as a determinant
it is easier to remember and easier to get wrong:

$$\mathbf{a}\times\mathbf{b} = \begin{vmatrix} \hat{\mathbf{x}} & \hat{\mathbf{y}} & \hat{\mathbf{z}} \\,a_x & a_y & a_z \\,b_x & b_y & b_z \end{vmatrix}$$

because expanding a determinant along its top row alternates the signs, and the middle
term therefore carries a minus that the cyclic form has already absorbed. Written out,
the $\hat{\mathbf{y}}$ term is $-(a_xb_z - a_zb_x)$, which is the same as
$a_zb_x - a_xb_z$. Two ways to write one thing, and mixing them is where sign errors
come from.

That the result really is perpendicular to both is now a two-line check rather than an
assertion:

```
a . (a x b) = ax(ay bz - az by) + ay(az bx - ax bz) + az(ax by - ay bx)

            = ax ay bz - ax az by + ay az bx - ay ax bz + az ax by - az ay bx
            = 0
```

Every term appears twice with opposite signs. The same cancellation happens with
$\mathbf{b}$.

### Worked: a spanner

A spanner lies in the horizontal plane. Your hand is at
$\mathbf{r} = (0.24,\,0.10,\,0)$ m from the nut and pushes with
$\mathbf{F} = (-90,\,210,\,0)$ N. The torque is the cross product $\mathbf{r}\times\mathbf{F}$, written `tau` below.

```
tau_x = ry Fz - rz Fy = 0.10*0    - 0*210    = 0
tau_y = rz Fx - rx Fz = 0*(-90)   - 0.24*0   = 0
tau_z = rx Fy - ry Fx = 0.24*210  - 0.10*(-90)
                      = 50.4 + 9.0 = 59.4

tau = (0, 0, 59.4) N m
```

Everything is in the $xy$ plane, so the torque is purely along $z$ — the nut turns about
the vertical, which is the only axis available to it. The sign is positive, meaning
anticlockwise seen from above.

Check it against the geometric form:

```
|r| = sqrt(0.24^2 + 0.10^2) = sqrt(0.0676) = 0.26 m
|F| = sqrt(90^2 + 210^2)    = sqrt(52200)  = 228.47 N

r . F = 0.24*(-90) + 0.10*210 = -21.6 + 21.0 = -0.6
cos(theta) = -0.6 / (0.26 * 228.47) = -0.010100
theta      = 90.579 deg,  sin(theta) = 0.999949

|r||F| sin(theta) = 0.26 * 228.47 * 0.999949 = 59.40 N m
```

The push is almost exactly at right angles to the spanner, which is why nearly all of it
is doing useful work — and why the small negative dot product, $-0.6$, tells you the
hand is very slightly pulling back along the shaft rather than pushing along it.

### Worked: a charge crossing a field

A charge $q = 5.0\,\mu\mathrm{C}$ moves with $\mathbf{v} = (3.0,\,-1.0,\,2.0)\times10^{5}$ m/s
through a magnetic field $\mathbf{B} = (0,\,0.40,\,0.30)$ T. The force is
$q\,\mathbf{v}\times\mathbf{B}$.

```
(v x B)_x = vy Bz - vz By = (-1.0e5)(0.30) - (2.0e5)(0.40) = -3.0e4 - 8.0e4 = -1.10e5
(v x B)_y = vz Bx - vx Bz = (2.0e5)(0)     - (3.0e5)(0.30) =      0 - 9.0e4 = -0.90e5
(v x B)_z = vx By - vy Bx = (3.0e5)(0.40)  - (-1.0e5)(0)   =  1.2e5 - 0     =  1.20e5

F = q (v x B) = 5.0e-6 * (-1.10e5, -0.90e5, 1.20e5)
              = (-0.550, -0.450, 0.600) N

|F| = sqrt(0.3025 + 0.2025 + 0.3600) = sqrt(0.8650) = 0.9301 N
```

Now the check that makes this product worth trusting:

```
F . v = (-0.550)(3.0e5) + (-0.450)(-1.0e5) + (0.600)(2.0e5)
      = -165000 + 45000 + 120000 = 0

F . B = (-0.550)(0) + (-0.450)(0.40) + (0.600)(0.30)
      = 0 - 0.180 + 0.180 = 0
```

Both zero, as the algebra above promised. The first of those is a physical statement of
some weight: a force perpendicular to the velocity does no work, so a magnetic field can
bend a charged particle's path but can never speed it up or slow it down. All the energy
in a motor arrives through some other route.

And the geometric form agrees:

```
|v| = sqrt(1.4e11) = 3.7417e5 m/s      |B| = sqrt(0.16 + 0.09) = 0.50 T
v . B = (-1.0e5)(0.40) + (2.0e5)(0.30) = -4.0e4 + 6.0e4 = 2.0e4
cos(theta) = 2.0e4 / (3.7417e5 * 0.50) = 0.10690,  sin(theta) = 0.99427

q |v| |B| sin(theta) = 5.0e-6 * 3.7417e5 * 0.50 * 0.99427 = 0.9301 N
```

## The mistakes

**The middle sign.** Far and away the most common error is writing the $y$ component as
$a_xb_z - a_zb_x$ instead of $a_zb_x - a_xb_z$. It is tempting because the $x$ and $z$
components both read "first index times second, minus the swap" in the obvious order,
and the $y$ one does not. The cure is to trust the cycle $x \to y \to z \to x$ rather
than the pattern: the $y$ component uses $z$ then $x$, in that order, because $z$ is
what follows $y$ round the loop. If you have made this mistake, the result comes out
perpendicular to nothing, so the $\mathbf{a}\cdot(\mathbf{a}\times\mathbf{b}) = 0$ check
catches it every time — which is why it is worth doing.

**Assuming order does not matter.** It does, and physically. $q\,\mathbf{v}\times\mathbf{B}$
written the other way round points the force at the opposite side of the track.

**Reaching for the wrong product.** The question to ask is what kind of answer the
quantity is. Work, energy and flux are numbers, so they are dot products; torque, the
magnetic force and the Poynting vector are directed, so they are cross products.

## Where this stops holding

**Three dimensions, and no others.** In two dimensions there is no room for a vector
perpendicular to the plane, so the plane's cross product is really just the single
number $a_xb_y - a_yb_x$ — which is why a torque in a plane problem is treated as a
signed scalar with no axis attached. In four dimensions there is too much room: given
two vectors, a whole plane of directions is perpendicular to both, and no single one of
them is picked out. The object that generalises properly is not a vector at all but an
antisymmetric array, and in electromagnetism it turns up as the field tensor. The cross
product is a piece of luck peculiar to three dimensions, where "the perpendicular
direction" happens to be unique.

**It is not associative.** $\mathbf{a}\times(\mathbf{b}\times\mathbf{c})$ and
$(\mathbf{a}\times\mathbf{b})\times\mathbf{c}$ are different vectors, so the brackets are
never optional. One line settles it:
$\hat{\mathbf{x}}\times(\hat{\mathbf{x}}\times\hat{\mathbf{y}}) =
\hat{\mathbf{x}}\times\hat{\mathbf{z}} = -\hat{\mathbf{y}}$, while
$(\hat{\mathbf{x}}\times\hat{\mathbf{x}})\times\hat{\mathbf{y}} =
\mathbf{0}\times\hat{\mathbf{y}} = \mathbf{0}$.

**The result is not quite an arrow.** Reflect the whole world in a mirror and an
ordinary vector — a velocity, a force — reflects with it. A cross product does not: both
inputs reflect, and the right-hand rule then hands back a vector pointing the *wrong*
way compared with the mirrored picture. Quantities built this way are called
pseudovectors, and the magnetic field is one, which is why mirror-image arguments about
magnetism so often come out backwards.

## The two products, taken together

They are not independent. The dot product keeps $\cos\theta$, the cross product keeps
$\sin\theta$, and those two are tied by the identity that has held since school:

$$(\mathbf{a}\cdot\mathbf{b})^2 + |\mathbf{a}\times\mathbf{b}|^2 = |\mathbf{a}|^2|\mathbf{b}|^2$$

which is $\cos^2\theta + \sin^2\theta = 1$ multiplied through by
$|\mathbf{a}|^2|\mathbf{b}|^2$. Take the pair from the previous unit,
$\mathbf{a} = (5, 2, -4)$ and $\mathbf{b} = (2, 3, 6)$:

```
a . b = -8                            (a . b)^2 = 64

a x b = (2*6 - (-4)*3, (-4)*2 - 5*6, 5*3 - 2*2)
      = (12 + 12, -8 - 30, 15 - 4)
      = (24, -38, 11)                 |a x b|^2 = 576 + 1444 + 121 = 2141

64 + 2141 = 2205        and        |a|^2 |b|^2 = 45 * 49 = 2205
```

That is a complete check on both products at once, from two vectors and no angle. It
also gives the across-the-rail length of the previous unit for free:
$|\mathbf{a}\times\mathbf{b}|/|\mathbf{b}| = \sqrt{2141}/7 = 46.271/7 = 6.6101$ N,
which is the 6.6101 N worked out there by an entirely different route.
''',
                },
            ],
            "sandbox": {
                "title": "A vector attached to every point",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": -1, "a12": 0, "a21": 0, "a22": -1},
                "brief": r'''
Forget the differential equations this picture was drawn for and read it as geometry.

Each short stroke sits at a point $\mathbf{x} = (x_1, x_2)$ of a 7 × 7 grid and points
along the vector $A\mathbf{x}$ — the matrix applied to that point's own position
vector. (At the origin $A\mathbf{x}$ is the zero vector, which has no direction, so
no stroke is drawn there — the filled dot at the centre is a fixed marker for the
origin itself, and it is drawn whatever the matrix is.) The strokes are all the same
length, so what you can read off them is direction and nothing else. The coloured curves join the strokes up, following the
directions from eight starting points around a circle.

Four settings of the matrix are worth working through, and each one is a statement
about vectors rather than about circuits.
''',
                "notice": [
                    r"It opens at $A = -I$: $a_{11} = a_{22} = -1$ with both off-diagonal entries zero, so $A\mathbf{x} = -\mathbf{x}$. Every stroke lies along the line from the origin to its own point and faces inwards. Multiplying a vector by a negative number keeps its line and reverses its direction; the length is unchanged here, though the drawing normalises it away.",
                    r"Set $a_{11}$ and $a_{22}$ both to $+1$, so $A\mathbf{x} = +\mathbf{x}$. Every stroke reverses and now points directly away from the origin, still along the same lines. The readout underneath changes from *stable node* to *unstable node*, and the eight curves become short outward stubs that leave the plot almost at once.",
                    r"Now set $a_{11} = a_{22} = 0$, $a_{12} = -1$, $a_{21} = 1$. Then $A\mathbf{x} = (-x_2, x_1)$, and its dot product with $\mathbf{x}$ is $x_1(-x_2) + x_2x_1 = 0$ at *every* point. Look along any radius: the stroke is at right angles to it. A dot product of zero, drawn at every point of the grid at once. (The curves creep outwards by about a tenth of their radius over the run — that is the drawing stepping forward in finite jumps, not the geometry.)",
                    r"Finally set $a_{12}$ to $+1$, so both off-diagonal entries are $+1$ and $A\mathbf{x} = (x_2, x_1)$ — the mirror image of $\mathbf{x}$ in the 45° line. Now $\mathbf{x}\cdot A\mathbf{x} = 2x_1x_2$, which vanishes only where $x_1$ or $x_2$ is zero: the strokes stand at right angles to the radius on the two axes and nowhere else. The readout says *saddle*, because the determinant has gone negative.",
                ],
            },
            "quiz": {
                "title": "Two products, and what each one is for",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"What is the magnitude of $(3, 4, 12)$?",
                        "opts": ["19", "13", "169", "7"],
                        "a": 1,
                        "why": (
                            r"$\sqrt{9 + 16 + 144} = \sqrt{169} = 13$. Adding the components gives 19 and stopping "
                            r"before the square root gives 169; both are the same two slips that turn up with the "
                            r"modulus of a complex number, because it is the same calculation with a third component "
                            r"added."
                        ),
                    },
                    {
                        "q": r"What is $(1, 2, 3)\cdot(4, -5, 6)$?",
                        "opts": ["12", r"$(4, -10, 18)$", "32", "$-30$"],
                        "a": 0,
                        "why": (
                            r"$4 - 10 + 18 = 12$: multiply the matching components and add the three results. The "
                            r"answer is a single number — a triple of numbers is what you get if you multiply "
                            r"component by component and forget to add, which is not a product of vectors at all."
                        ),
                    },
                    {
                        "q": r"Two non-zero vectors have a dot product of exactly zero. What does that tell you?",
                        "opts": [
                            "They point the same way",
                            "They are perpendicular",
                            "They have the same magnitude",
                            "One of them is a unit vector",
                        ],
                        "a": 1,
                        "why": (
                            r"$\mathbf{a}\cdot\mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$, and with neither "
                            r"magnitude zero the only way to get zero is $\cos\theta = 0$, so $\theta = 90°$. It is "
                            r"the *cross* product that vanishes when two vectors point the same way — the two "
                            r"products fail in opposite circumstances, which is what makes them worth having both."
                        ),
                    },
                    {
                        "q": r"$\mathbf{a}$ and $\mathbf{b}$ are parallel. What is $|\mathbf{a}\times\mathbf{b}|$?",
                        "opts": [r"$|\mathbf{a}||\mathbf{b}|$", "Zero", r"$|\mathbf{a}| + |\mathbf{b}|$", "It cannot be determined"],
                        "a": 1,
                        "why": (
                            r"$|\mathbf{a}\times\mathbf{b}| = |\mathbf{a}||\mathbf{b}|\sin\theta$, and $\sin 0 = 0$. "
                            r"Geometrically the cross product's magnitude is the area of the parallelogram the two "
                            r"vectors span, and two parallel vectors span nothing. The product $|\mathbf{a}||\mathbf{b}|$ "
                            r"is what you get when they are perpendicular, which is the other extreme."
                        ),
                    },
                    {
                        "q": r"How does $\mathbf{b}\times\mathbf{a}$ compare with $\mathbf{a}\times\mathbf{b}$?",
                        "opts": [
                            "They are the same vector",
                            "Same magnitude, opposite direction",
                            "Same direction, opposite magnitude",
                            "They are perpendicular to each other",
                        ],
                        "a": 1,
                        "why": (
                            r"Swapping the order flips the cross product: $\mathbf{b}\times\mathbf{a} = "
                            r"-\mathbf{a}\times\mathbf{b}$. The right-hand rule is what encodes the sign, and it is "
                            r"why the order in $q\,\mathbf{v}\times\mathbf{B}$ must be written down carefully — "
                            r"reversing it points the force the other way. A magnitude cannot be negative, so "
                            r"'opposite magnitude' describes nothing."
                        ),
                    },
                    {
                        "q": r"A charge moves exactly along a magnetic field line. What magnetic force does it feel?",
                        "opts": [
                            "None",
                            "The maximum possible, $qvB$",
                            r"$qvB$ along the direction of travel",
                            "It depends on the sign of the charge",
                        ],
                        "a": 0,
                        "why": (
                            r"The force is $q\,\mathbf{v}\times\mathbf{B}$, and a cross product of parallel vectors is "
                            r"zero. The maximum $qvB$ arrives at the opposite extreme, when the motion is at right "
                            r"angles to the field. The sign of the charge decides which way the force points when "
                            r"there is one, and cannot conjure a force out of a zero cross product."
                        ),
                    },
                ],
            },
            "blanks": [
                {
                    "title": "The seven rules, with the right-hand sides taken off",
                    "minutes": 9,
                    "caption": "a = (a1, a2, a3) and b = (b1, b2, b3); theta is the angle between them",
                    "lang": "text",
                    "brief": r'''
Nothing is executed here. Each line is one of the rules from the reading with its
answer removed, and every one of them can be rebuilt from the two definitions —
$\mathbf{a}\cdot\mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$ and
$|\mathbf{a}\times\mathbf{b}| = |\mathbf{a}||\mathbf{b}|\sin\theta$ — plus the
right-hand rule.

`sqrt` is a square root, `**` is a power, `.` is the dot product and `x` is the cross
product, as in the reading.
''',
                    "listing": """|a|                        =  ___

a + b                      =  (a1 + b1, a2 + b2, ___)

3 * a                      =  ___

a . b                      =  a1*b1 + a2*b2 + ___

a . b                      =  |a| * |b| * ___

|a x b|                    =  |a| * |b| * ___

b x a                      =  ___
""",
                    "blanks": [
                        {
                            "prompt": "The magnitude, from the components.",
                            "hole": "?",
                            "opts": ["a1 + a2 + a3", "sqrt(a1**2 + a2**2 + a3**2)",
                                     "a1**2 + a2**2 + a3**2", "sqrt(a1 + a2 + a3)"],
                            "a": 1,
                            "why": "Pythagoras twice: once across the floor to get the shadow, once more to stand the shadow up against the vertical component. The two square roots collapse into one because the inner root is immediately squared.",
                            "whys": [
                                "Adding the components gives the distance you would walk going along, then across, then up — the taxi route rather than the straight line. For $(3, 4, 12)$ it gives 19 instead of 13.",
                                "Pythagoras twice: once across the floor to get the shadow, once more to stand the shadow up against the vertical component. The two square roots collapse into one because the inner root is immediately squared.",
                                "That is the magnitude *squared*, which is $\\mathbf{a}\\cdot\\mathbf{a}$ and often the more convenient quantity — but it is not a length, and its units are the square of the vector's.",
                                "Squaring is what removes the signs, so it has to happen before the sum, not after. With a negative component this can even ask for the root of a negative number.",
                            ],
                        },
                        {
                            "prompt": "The third component of a sum.",
                            "hole": "?",
                            "opts": ["a3 + b3", "a3 * b3", "a3 - b3", "sqrt(a3**2 + b3**2)"],
                            "a": 0,
                            "why": "Each axis is answered on its own: how far along $z$ the first vector goes, then how far along $z$ the second one goes. Nothing from $x$ or $y$ can reach this column, because the axes are at right angles.",
                            "whys": [
                                "Each axis is answered on its own: how far along $z$ the first vector goes, then how far along $z$ the second one goes. Nothing from $x$ or $y$ can reach this column, because the axes are at right angles.",
                                "Multiplying components belongs to the dot product, and even there the three results are added into a single number rather than kept as a component.",
                                "That is the third component of $\\mathbf{a} - \\mathbf{b}$. The line as written is a sum, and getting the sign wrong here reverses one of the two vectors.",
                                "Adding in quadrature is how *lengths* of perpendicular pieces combine, not how components along the same axis combine. Two vectors each reaching $z = 3$ reach $z = 6$ between them, not 4.24.",
                            ],
                        },
                        {
                            "prompt": "Scaling by a positive number.",
                            "hole": "?",
                            "opts": ["(3*a1, a2, a3)", "(3*a1, 3*a2, 3*a3)",
                                     "3*a1 + 3*a2 + 3*a3", "(a1**3, a2**3, a3**3)"],
                            "a": 1,
                            "why": "Every component is multiplied, so the arrow gets three times longer and does not turn at all — the ratios between the components, which are what fix the direction, are unchanged.",
                            "whys": [
                                "Stretching one axis only would swing the arrow round towards that axis. Scaling a vector must not change its direction, and this does.",
                                "Every component is multiplied, so the arrow gets three times longer and does not turn at all — the ratios between the components, which are what fix the direction, are unchanged.",
                                "That collapses a vector to a single number. Multiplying by a scalar takes a vector in and must give a vector back.",
                                "Cubing each component is not multiplying by 3; for the component 2 it gives 8. It also has the wrong units — metres cubed where metres were wanted.",
                            ],
                        },
                        {
                            "prompt": "The last term of the dot product.",
                            "hole": "?",
                            "opts": ["a3*b3", "a3 + b3", "(a3, b3)", "a3*b3 + a1*b2"],
                            "a": 0,
                            "why": "Matching components are multiplied and the three results are added. Doing the sum at the end is what makes the answer independent of which axes were chosen — a triple of products would not be.",
                            "whys": [
                                "Matching components are multiplied and the three results are added. Doing the sum at the end is what makes the answer independent of which axes were chosen — a triple of products would not be.",
                                "The other two terms on this line are products, so this one must be too. Mixing an addition in among them would also break the rule that doubling $\\mathbf{a}$ doubles the dot product.",
                                "A pair of numbers is not a term in a sum. This is the shape of the error that keeps three separate results instead of adding them.",
                                "Cross terms between different axes appear in the *cross* product, not this one. Here each component of $\\mathbf{a}$ meets only the matching component of $\\mathbf{b}$.",
                            ],
                        },
                        {
                            "prompt": "The geometric form of the dot product.",
                            "hole": "?",
                            "opts": ["sin(theta)", "cos(theta)", "tan(theta)", "1 - cos(theta)"],
                            "a": 1,
                            "why": "The dot product keeps the part of one vector that lies *along* the other, and that shadow is the adjacent side of a right-angled triangle: $|\\mathbf{a}|\\cos\\theta$. So it is largest when the two agree and zero when they are perpendicular.",
                            "whys": [
                                "This would make the dot product vanish for two parallel vectors, which is backwards: two forces pushing the same way have the largest possible dot product. The sine belongs to the cross product.",
                                "The dot product keeps the part of one vector that lies *along* the other, and that shadow is the adjacent side of a right-angled triangle: $|\\mathbf{a}|\\cos\\theta$. So it is largest when the two agree and zero when they are perpendicular.",
                                "A tangent runs off to infinity at 90°, and no product of two finite vectors does that. The dot product is bounded by $|\\mathbf{a}||\\mathbf{b}|$.",
                                "This is never negative, so it could not tell you that two vectors broadly oppose each other — and it is 0 at $\\theta = 0$, where the dot product is at its largest.",
                            ],
                        },
                        {
                            "prompt": "The magnitude of the cross product.",
                            "hole": "?",
                            "opts": ["cos(theta)", "sin(theta)", "tan(theta)", "1 + cos(theta)"],
                            "a": 1,
                            "why": "The magnitude is the area of the parallelogram the two vectors span: base $|\\mathbf{b}|$ times perpendicular height $|\\mathbf{a}|\\sin\\theta$. Parallel vectors span no area, and perpendicular ones span the most.",
                            "whys": [
                                "That is the dot product's factor. It would make the cross product largest for parallel vectors, when in fact two parallel vectors have a cross product of exactly zero — a push straight along the spanner turns nothing.",
                                "The magnitude is the area of the parallelogram the two vectors span: base $|\\mathbf{b}|$ times perpendicular height $|\\mathbf{a}|\\sin\\theta$. Parallel vectors span no area, and perpendicular ones span the most.",
                                "Unbounded, so it cannot be the size of a product of two finite vectors. It is also the ratio of the two products, $|\\mathbf{a}\\times\\mathbf{b}|/(\\mathbf{a}\\cdot\\mathbf{b})$, which is a different quantity.",
                                "This is 2 for parallel vectors, where the cross product must be zero. Reversing one vector should also leave the magnitude alone, and this changes it from 2 to 0.",
                            ],
                        },
                        {
                            "prompt": "Swapping the order of a cross product.",
                            "hole": "?",
                            "opts": ["a x b", "-(a x b)", "0", "|a| * |b|"],
                            "a": 1,
                            "why": "The magnitude is unchanged — the parallelogram is the same one — but the right-hand rule turns your hand over, so the answer points the other way. This is the only product in the course where order matters, and it is also why $\\mathbf{a}\\times\\mathbf{a} = \\mathbf{0}$: only zero equals its own negative.",
                            "whys": [
                                "That is the rule for the dot product, where swapping changes nothing. If the cross product behaved this way, reversing the current in a motor winding would not reverse the force on it.",
                                "The magnitude is unchanged — the parallelogram is the same one — but the right-hand rule turns your hand over, so the answer points the other way. This is the only product in the course where order matters, and it is also why $\\mathbf{a}\\times\\mathbf{a} = \\mathbf{0}$: only zero equals its own negative.",
                                "Zero only when the two are parallel. For anything else the swapped product has exactly the same length as the original, so it cannot be the zero vector.",
                                "A cross product is a vector; this is a number. It is also the *largest* the magnitude can be, reached only when the two are perpendicular.",
                            ],
                        },
                    ],
                },
                {
                    "title": "Five lines of NumPy that do the whole module",
                    "minutes": 9,
                    "caption": "the same a and b as the worked example in the reading: a = (5, 2, -4) N along a rail b = (2, 3, 6)",
                    "lang": "python",
                    "brief": r'''
This is the force-on-a-rail example from the second reading unit, written out so the
answers can be checked against the ones worked by hand: $|\mathbf{b}| = 7$,
$\mathbf{a}\cdot\mathbf{b} = -8$, an along-the-rail component of $-1.1429$ N and an
across-the-rail component of $6.6101$ N.

Each blank has one right answer and three that are a real mistake — a norm where a sum
belongs, a projection divided by the wrong length, lengths subtracted that should have
been combined in quadrature, an array where a float is wanted.
''',
                    "listing": """import numpy as np

a = np.array([5.0, 2.0, -4.0])          # the force, in newtons
b = np.array([2.0, 3.0, 6.0])           # the direction of the rail

mag_b  = ___                            # 7.0
b_hat  = ___                            # the rail's direction, length 1
p      = ___                            # the dot product: one float, here -8.0
along  = ___                            # signed length along the rail: -1.1429 N
across = ___                            # length across the rail: 6.6101 N

theta  = np.degrees(np.arccos(p / (np.linalg.norm(a) * mag_b)))    # 99.809 deg
""",
                    "blanks": [
                        {
                            "prompt": "The length of b.",
                            "hole": "?",
                            "opts": ["np.linalg.norm(b)", "np.sum(b)", "np.abs(b)", "np.dot(b, b)"],
                            "a": 0,
                            "why": "`np.linalg.norm` is the square root of the sum of the squares, which is 7.0 here. Everything below divides by it, so getting it wrong scales two answers at once and neither looks obviously wrong.",
                            "whys": [
                                "`np.linalg.norm` is the square root of the sum of the squares, which is 7.0 here. Everything below divides by it, so getting it wrong scales two answers at once and neither looks obviously wrong.",
                                "That adds the components: $2 + 3 + 6 = 11$, the taxi route rather than the straight-line distance. It happens to be positive here, which is why it survives a glance.",
                                "`np.abs` works element by element and returns an array of three numbers, so `b / mag_b` would then divide component by component and give `(1, 1, 1)`.",
                                "$\\mathbf{b}\\cdot\\mathbf{b} = 49$ is the length *squared*. It is the more convenient quantity in the vector projection formula, but here a length is wanted and 49 is not it.",
                            ],
                        },
                        {
                            "prompt": "The unit vector along the rail.",
                            "hole": "?",
                            "opts": ["b / mag_b", "b * mag_b", "mag_b / b", "b / np.sum(b)"],
                            "a": 0,
                            "why": "Dividing every component by the length leaves the direction alone and makes the length 1: $(2, 3, 6)/7 = (0.2857, 0.4286, 0.8571)$, whose squares add to 1.",
                            "whys": [
                                "Dividing every component by the length leaves the direction alone and makes the length 1: $(2, 3, 6)/7 = (0.2857, 0.4286, 0.8571)$, whose squares add to 1.",
                                "Multiplying makes it 49 long rather than 1. Dividing is the only operation that can normalise, because the result has to be independent of how long $\\mathbf{b}$ started out.",
                                "This divides a number by an array, giving $(3.5, 2.333, 1.167)$ — a vector pointing a different way from $\\mathbf{b}$ entirely, since the biggest component has become the smallest.",
                                "Dividing by 11 gives a vector of length $7/11 = 0.636$, not 1. Only the true length normalises.",
                            ],
                        },
                        {
                            "prompt": "The dot product.",
                            "hole": "?",
                            "opts": ["np.dot(a, b)", "a * b", "np.cross(a, b)", "np.sum(a) * np.sum(b)"],
                            "a": 0,
                            "why": "`np.dot` multiplies matching components and adds the three results: $10 + 6 - 24 = -8$. The sign is already telling you the force pushes the carriage backwards along the rail, before any further arithmetic.",
                            "whys": [
                                "`np.dot` multiplies matching components and adds the three results: $10 + 6 - 24 = -8$. The sign is already telling you the force pushes the carriage backwards along the rail, before any further arithmetic.",
                                "In NumPy `*` is element by element, so this gives the array $(10, 6, -24)$ — the three products with the addition left out. That is the commonest wrong idea about the dot product, and here Python will not complain until something further down expects a number.",
                                "The cross product returns a vector, and the line below divides `p` by a length expecting a number. It is also answering a different question: how much of $\\mathbf{a}$ lies *across* $\\mathbf{b}$, not along it.",
                                "Summing each vector first throws the direction information away: $3 \\times 11 = 33$, which would be unchanged if the components of $\\mathbf{a}$ were shuffled into a completely different direction.",
                            ],
                        },
                        {
                            "prompt": "The signed length of the force's shadow on the rail.",
                            "hole": "?",
                            "opts": ["np.dot(a, b_hat)", "np.dot(a, b)",
                                     "np.linalg.norm(a) / mag_b", "np.dot(a, b) / np.linalg.norm(a)"],
                            "a": 0,
                            "why": "The projection is the dot product with the *unit* vector: $-8/7 = -1.1429$ N. Because `b_hat` has length 1, the units come out as newtons, which is what a component of a force has to be.",
                            "whys": [
                                "The projection is the dot product with the *unit* vector: $-8/7 = -1.1429$ N. Because `b_hat` has length 1, the units come out as newtons, which is what a component of a force has to be.",
                                "This is $-8$, the projection multiplied by the length of the rail vector. It would change if $\\mathbf{b}$ were written as $(4, 6, 12)$ instead, and a component of a force cannot depend on how long someone chose to draw the direction.",
                                "This is $6.7082/7 = 0.958$: the ratio of the two lengths, with the angle between them nowhere in it. It is positive even when the force points backwards.",
                                "Dividing by $|\\mathbf{a}|$ instead of $|\\mathbf{b}|$ projects the rail onto the force rather than the force onto the rail. Here it gives $-1.1926$, close enough to the right answer to pass unnoticed.",
                            ],
                        },
                        {
                            "prompt": "The length of what is left over, across the rail.",
                            "hole": "?",
                            "opts": ["np.linalg.norm(np.cross(a, b_hat))",
                                     "np.linalg.norm(a) - along",
                                     "np.linalg.norm(np.cross(a, b))",
                                     "np.cross(a, b_hat)"],
                            "a": 0,
                            "why": "The cross product with the unit vector has magnitude $|\\mathbf{a}|\\sin\\theta$, which is exactly the across-the-rail length: 6.6101 N. Check it against Pythagoras — $\\sqrt{1.1429^2 + 6.6101^2} = \\sqrt{45} = 6.7082 = |\\mathbf{a}|$.",
                            "whys": [
                                "The cross product with the unit vector has magnitude $|\\mathbf{a}|\\sin\\theta$, which is exactly the across-the-rail length: 6.6101 N. Check it against Pythagoras — $\\sqrt{1.1429^2 + 6.6101^2} = \\sqrt{45} = 6.7082 = |\\mathbf{a}|$.",
                                "Subtracting lengths would only be right if the two pieces pointed the same way, and they are at right angles by construction. It gives 7.851 N here — larger than the force it came from, which is impossible.",
                                "Crossing with $\\mathbf{b}$ rather than `b_hat` leaves a factor of $|\\mathbf{b}| = 7$ in: 46.271 instead of 6.6101. The units give it away, since this is newton-metres.",
                                "`np.cross` returns a vector where a single number was asked for — and not the across-the-rail vector either, since it points perpendicular to $\\mathbf{a}$ as well as to the rail. Only its magnitude is the quantity wanted, which is what the norm around it is for.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "What the bracket actually carries",
                    "minutes": 5,
                    "brief": r'''
Two forces act at the same point. The single force that would do the same job is their
vector sum, found one component at a time, and its size is Pythagoras across the three
components of that sum:

$$|\mathbf{F}_1 + \mathbf{F}_2| = \sqrt{(F_{1x}+F_{2x})^2 + (F_{1y}+F_{2y})^2 + (F_{1z}+F_{2z})^2}$$

Add first, then take the length. Doing it the other way round answers a different
question, and one nothing in the subject asks.
''',
                    "prompt": r"How large is the resultant force on the bracket?",
                    "note": "Give the answer in newtons, to two decimal places. Both forces act at the same point, so the resultant is simply their sum.",
                    "figure": r"""
A bracket is pulled by two struts at the same point:

    F1 = ( 14, -8,  5) N
    F2 = ( -6, 20,  7) N

Neither is a multiple of the other, and neither lies along an axis.
""",
                    "given": [
                        {"label": "F1", "value": "(14, -8, 5) N"},
                        {"label": "F2", "value": "(-6, 20, 7) N"},
                        {"label": "Answer in", "value": "newtons"},
                    ],
                    "aside": "Two of the six components are negative, and both of them matter — one shortens the sum, the other lengthens it.",
                    "answer": 18.76,
                    "tol": 0.03,
                    "unit": "N",
                    "hint": r"Add the two vectors component by component first. The sum has all three components positive, which makes the square root that follows straightforward.",
                    "wrong": r"If you got about 38.9 N, you found $|\mathbf{F}_1| + |\mathbf{F}_2| = 16.88 + 22.02$. That is the answer to a question about two forces pulling in the *same* direction, and these two do not: $\mathbf{F}_1$ pulls towards $+x$ and $\mathbf{F}_2$ towards $-x$, so part of each is spent cancelling the other.",
                    "why": r"$\mathbf{F}_1 + \mathbf{F}_2 = (14-6,\,-8+20,\,5+7) = (8, 12, 12)$ N, so the magnitude is $\sqrt{64 + 144 + 144} = \sqrt{352} = 18.76$ N. The individual magnitudes are $\sqrt{285} = 16.88$ N and $\sqrt{485} = 22.02$ N; the resultant is smaller than their sum and larger than their difference, which is the range every resultant of two vectors lies in.",
                },
                {
                    "title": "The angle between two vectors",
                    "minutes": 7,
                    "brief": r'''
    The dot product is the only practical way to get an angle out of components. Written
    both ways,

    $$\mathbf{a}\cdot\mathbf{b} = a_xb_x + a_yb_y + a_zb_z = |\mathbf{a}||\mathbf{b}|\cos\theta$$

    the left-hand form is arithmetic you can do and the right-hand form contains the
    angle. Equate them and $\theta$ falls out.
    ''',
                    "prompt": r"What is the angle between $\mathbf{a}$ and $\mathbf{b}$?",
                    "note": "Give the answer in degrees, to one decimal place. Both vectors happen to have the same magnitude, which is a convenience, not a hint.",
                    "figure": r"""
    $\mathbf{a} = (2, 3, 6)$ and $\mathbf{b} = (6, -2, 3)$, both in the same units.
    Neither lies along an axis and neither is a multiple of the other, so nothing here
    can be read off by inspection — the components are the only information there is.
    """,
                    "given": [
                        {"label": "a", "value": "(2, 3, 6)"},
                        {"label": "b", "value": "(6, -2, 3)"},
                        {"label": "Answer in", "value": "degrees"},
                    ],
                    "aside": "A dot product is one multiplication per component and then a single addition — "
                             "no square roots until the magnitudes are needed.",
                    "answer": 60.7,
                    "tol": 0.3,
                    "unit": "degrees",
                    "hint": r"$\cos\theta = \dfrac{\mathbf{a}\cdot\mathbf{b}}{|\mathbf{a}||\mathbf{b}|}$. Work out the three pieces separately, then take the inverse cosine.",
                    "wrong": r"Check what you divided by. It is the *product* of the two magnitudes, $7 \times 7 = 49$, not their sum: dividing by 14 gives $\cos\theta = 1.71$, an answer no angle has, which is a useful sign that the denominator went in wrong.",
                    "why": r"$\mathbf{a}\cdot\mathbf{b} = 12 - 6 + 18 = 24$. Both magnitudes are 7, since $4+9+36 = 49$ and $36+4+9 = 49$. So $\cos\theta = 24/49 = 0.4898$ and $\theta = 60.7°$. Notice that the middle term was negative and the answer still came out under 90° — the sign of the dot product alone tells you which side of a right angle you are on, before any arithmetic with square roots.",
                },
                {
                    "title": "The energy a shove is worth",
                    "minutes": 7,
                    "brief": r'''
Work is the dot product of the force with the displacement:

$$W = \mathbf{F}\cdot\mathbf{d} = F_xd_x + F_yd_y + F_zd_z$$

and it is a scalar — joules, with no direction attached. Only the part of the force that
lies along the movement contributes, and the dot product performs that selection on its
own: no component has to be discarded by hand.
''',
                    "prompt": r"How much work does the force do over that displacement?",
                    "note": "Give the answer in joules. The force is constant over the whole movement, so no integration is needed.",
                    "figure": r"""
A constant force acts on a carriage while it moves:

    F = ( 85, -40, 30) N
    d = (1.2, 0.5, -0.8) m

The force and the displacement are not parallel and not perpendicular; two of the three
products are negative.
""",
                    "given": [
                        {"label": "F", "value": "(85, -40, 30) N"},
                        {"label": "d", "value": "(1.2, 0.5, -0.8) m"},
                        {"label": "Answer in", "value": "joules"},
                    ],
                    "aside": "A newton times a metre is a joule, so the three products can be added directly — no conversion, and no square roots anywhere in this one.",
                    "answer": 58.0,
                    "tol": 0.4,
                    "unit": "J",
                    "hint": r"Three multiplications and two additions. Watch the signs: $(-40)(0.5)$ and $(30)(-0.8)$ both come out negative.",
                    "wrong": r"About 150 J means $|\mathbf{F}||\mathbf{d}| = 98.62 \times 1.5264$ was used — the work that *would* be done if the force pointed exactly along the movement. That is the maximum available, not the amount delivered; here the angle is $67.3°$ and only $\cos 67.3° = 0.385$ of it arrives.",
                    "why": r"$\mathbf{F}\cdot\mathbf{d} = (85)(1.2) + (-40)(0.5) + (30)(-0.8) = 102 - 20 - 24 = 58$ J. The result is positive, so the force is broadly helping the carriage along rather than resisting it, and you knew that from the sign of the sum before working out either magnitude. As a check on the geometry: $|\mathbf{F}| = \sqrt{9725} = 98.62$ N and $|\mathbf{d}| = \sqrt{2.33} = 1.5264$ m, so $\cos\theta = 58/150.53 = 0.3853$ and $\theta = 67.3°$ — under a right angle, as the positive answer requires.",
                },
                {
                    "title": "One component of a force that comes out sideways",
                    "minutes": 9,
                    "brief": r'''
A straight wire of length and direction $\mathbf{L}$, carrying current $I$ through a
uniform field $\mathbf{B}$, feels a force

$$\mathbf{F} = I\,\mathbf{L}\times\mathbf{B}$$

perpendicular to both the wire and the field. The components of a cross product run in
the cycle $x \to y \to z \to x$: each one is built from the *other* two axes, in that
order, minus the same pair reversed.

$$\mathbf{L}\times\mathbf{B} = (L_yB_z - L_zB_y,\;\; L_zB_x - L_xB_z,\;\; L_xB_y - L_yB_x)$$

The question asks for one component of the answer, not its size, so the signs have to
survive to the end.
''',
                    "prompt": r"What is the $y$ component of the force on the wire?",
                    "note": "Give the answer in newtons, with its sign, to three decimal places. Only the y component is wanted.",
                    "figure": r"""
A straight segment of wire in a uniform magnetic field:

    L = (0.25, 0.00, 0.10) m      the segment, pointing the way the current flows
    I = 8.0 A
    B = (0.12, 0.30, -0.20) T

The wire has no y component, but the force does.
""",
                    "given": [
                        {"label": "L", "value": "(0.25, 0, 0.10) m"},
                        {"label": "I", "value": "8.0 A"},
                        {"label": "B", "value": "(0.12, 0.30, -0.20) T"},
                        {"label": "Answer in", "value": "newtons"},
                    ],
                    "aside": "An ampere times a metre times a tesla is a newton, so nothing needs converting — but the current multiplies the whole cross product, not one component of it.",
                    "answer": 0.496,
                    "tol": 0.004,
                    "unit": "N",
                    "hint": r"The $y$ component of $\mathbf{L}\times\mathbf{B}$ is $L_zB_x - L_xB_z$ — $z$ first, then $x$, because $z$ is what follows $y$ round the cycle. Then multiply by $I$.",
                    "wrong": r"If you got $-0.496$ N, the two products in the $y$ component were taken in the order $L_xB_z - L_zB_x$. That is the order the $x$ and $z$ components use, and the $y$ one is the exception — writing the cross product as a determinant makes the reason visible, because expanding along the top row alternates the signs and the middle term is the one that picks up the minus.",
                    "why": r"$L_zB_x - L_xB_z = (0.10)(0.12) - (0.25)(-0.20) = 0.012 + 0.050 = 0.062$, and $F_y = I \times 0.062 = 8.0 \times 0.062 = 0.496$ N. For the record the whole force is $\mathbf{F} = (-0.240,\,0.496,\,0.600)$ N, of magnitude 0.8146 N. Two checks worth making: $\mathbf{F}\cdot\mathbf{L} = -0.060 + 0 + 0.060 = 0$ and $\mathbf{F}\cdot\mathbf{B} = -0.0288 + 0.1488 - 0.1200 = 0$, so the force really is perpendicular to both, which is the fastest way to catch a sign error in any cross product.",
                },
                {
                    "title": "How far the sensor sits from the busbar",
                    "minutes": 12,
                    "brief": r'''
A straight line in space is fixed by one point on it, $\mathbf{P}_0$, and a direction
$\mathbf{u}$. The perpendicular distance from some other point $\mathbf{Q}$ is not one
of the numbers you were given, and it is not a component of anything: it has to be
built.

Let $\mathbf{r} = \mathbf{Q} - \mathbf{P}_0$ be the displacement from the line's known
point to the sensor. Split it into the part along the line and the part across it. The
part across is what is wanted, and its length is available two ways:

$$q = \frac{|\mathbf{r}\times\mathbf{u}|}{|\mathbf{u}|}
   \qquad\text{or}\qquad
   q = \sqrt{|\mathbf{r}|^2 - \left(\frac{\mathbf{r}\cdot\mathbf{u}}{|\mathbf{u}|}\right)^2}$$

Both come from the same right-angled triangle. Doing it one way and checking with the
other costs very little and catches almost everything.
''',
                    "prompt": r"How far is the sensor from the busbar, measured perpendicular to it?",
                    "note": "Give the answer in metres, to three decimal places. The busbar is straight and long enough that the distance to the line, not to its ends, is what matters.",
                    "figure": r"""
A straight busbar runs through the point P0 in the direction u; a field sensor sits
at Q:

    P0 = (1, 0, 2) m        a point the busbar passes through
    u  = (2, 3, 6)          the busbar's direction (not a unit vector)
    Q  = (4, 2, 1) m        the sensor

u is a direction only, so its own length is not a distance in the problem.
""",
                    "given": [
                        {"label": "P0", "value": "(1, 0, 2) m"},
                        {"label": "u", "value": "(2, 3, 6)"},
                        {"label": "Q", "value": "(4, 2, 1) m"},
                        {"label": "Answer in", "value": "metres"},
                    ],
                    "aside": "The length of u is 7, and it appears in the answer as a divisor. A direction vector of any other length would have to give the same distance, which is a good way to test a formula you are unsure of.",
                    "answer": 3.642,
                    "tol": 0.01,
                    "unit": "m",
                    "hint": r"First find $\mathbf{r} = \mathbf{Q} - \mathbf{P}_0$. Then cross it with $\mathbf{u}$, take the magnitude, and divide by $|\mathbf{u}|$ — the division is what makes the answer independent of how long $\mathbf{u}$ was written.",
                    "wrong": r"About 3.742 m is $|\mathbf{r}|$ itself — the distance from the sensor to the point $\mathbf{P}_0$, not to the line. Those differ by however far along the busbar the nearest point lies, which here is only 0.857 m, so the two answers are close enough that the mistake survives a sanity check. About 25.5 m is $|\mathbf{r}\times\mathbf{u}|$ with the division by $|\mathbf{u}|$ left out; the units give that one away, since a cross product of a length with a bare direction is not a length.",
                    "why": r"$\mathbf{r} = (4-1,\,2-0,\,1-2) = (3, 2, -1)$ m. Then $\mathbf{r}\times\mathbf{u} = (2\cdot6 - (-1)\cdot3,\; (-1)\cdot2 - 3\cdot6,\; 3\cdot3 - 2\cdot2) = (15, -20, 5)$, whose magnitude is $\sqrt{225+400+25} = \sqrt{650} = 25.495$. Dividing by $|\mathbf{u}| = 7$ gives $q = 3.642$ m. The other route: $\mathbf{r}\cdot\mathbf{u} = 6 + 6 - 6 = 6$, so the along-the-bar part is $6/7 = 0.857$ m, and $|\mathbf{r}|^2 = 14$, giving $q = \sqrt{14 - 0.857^2} = \sqrt{13.265} = 3.642$ m. Two independent calculations agreeing is what makes an answer like this one safe to use — and the distance is the quantity a field measurement actually depends on, since a long straight conductor's field falls off as $1/q$.",
                },
            ],
            "derive": {
                "title": "Splitting a vector into the part along another and the part across it",
                "minutes": 13,
                "vars": ["a", "b", "p", "k", "q"],
                "brief": r'''
Almost every use of vectors in engineering is this one operation: take a quantity and
ask how much of it lies along some direction that matters — a rail, a wire, a normal to
a surface — and how much is left over pointing elsewhere. This derivation builds both
pieces from the dot product alone, and then discovers the cross product waiting at the
end of it.

To keep the algebra scalar, name the four numbers involved and work with those:

$$a = |\mathbf{a}|, \qquad b = |\mathbf{b}|, \qquad p = \mathbf{a}\cdot\mathbf{b},
\qquad \hat{\mathbf{b}} = \frac{\mathbf{b}}{b}$$

and let $k$ be the (signed) length of the part of $\mathbf{a}$ along $\mathbf{b}$, and
$q$ the length of the part across it. Every answer below is an expression in
$a$, $b$, $p$, $k$ and $q$ — no vectors, no angles.
''',
                "steps": [
                    {
                        "prompt": r"Write the along-the-direction piece as $k\hat{\mathbf{b}}$ and demand that the remainder $\mathbf{a} - k\hat{\mathbf{b}}$ be perpendicular to $\mathbf{b}$ — that is, that its dot product with $\mathbf{b}$ be zero. Expanding gives $\mathbf{a}\cdot\mathbf{b} - k\,(\mathbf{b}\cdot\mathbf{b})/b = 0$. Solve for $k$ in terms of $p$ and $b$.",
                        "given": r"$\mathbf{b}\cdot\mathbf{b} = b^2$",
                        "answer": r"\frac{p}{b}",
                        "placeholder": "p over something",
                        "hint": r"With $\mathbf{b}\cdot\mathbf{b} = b^2$, the second term is $kb^2/b = kb$. The equation is then $p - kb = 0$.",
                        "deconstruct": [
                            r"$\mathbf{a}\cdot\mathbf{b} = p$ by definition.",
                            r"$k\,(\mathbf{b}\cdot\mathbf{b})/b = k b^2 / b = kb$.",
                            r"So $p - kb = 0$, and $k = p/b$.",
                        ],
                    },
                    {
                        "prompt": r"That $k$ is a length, so the along-the-direction piece as a *vector* is $k\hat{\mathbf{b}} = (k/b)\,\mathbf{b}$. Write the scalar that multiplies $\mathbf{b}$, in terms of $p$ and $b$.",
                        "answer": r"\frac{p}{b^2}",
                        "placeholder": "p over a square",
                        "hint": r"Substitute $k = p/b$ into $k/b$.",
                        "deconstruct": [
                            r"$k/b = (p/b)/b$.",
                            r"Dividing twice by $b$ is dividing once by $b^2$.",
                        ],
                    },
                    {
                        "prompt": r"The two pieces are perpendicular by construction, so their lengths obey Pythagoras against the original: $a^2 = k^2 + q^2$. Write $q^2$ in terms of $a$, $p$ and $b$.",
                        "answer": r"a^2 - \frac{p^2}{b^2}",
                        "placeholder": "a squared minus something",
                        "hint": r"Rearrange to $q^2 = a^2 - k^2$, then put $k = p/b$ in and square it.",
                        "deconstruct": [
                            r"$q^2 = a^2 - k^2$.",
                            r"$k^2 = (p/b)^2 = p^2/b^2$.",
                        ],
                    },
                    {
                        "prompt": r"Fractions inside a square root are awkward, so clear the denominator. Multiply that expression through by $b^2$ and write $(qb)^2$ in terms of $a$, $b$ and $p$.",
                        "answer": r"a^2b^2 - p^2",
                        "placeholder": "a product of squares minus a square",
                        "hint": r"$b^2\left(a^2 - \dfrac{p^2}{b^2}\right)$ — the second term's denominator cancels outright.",
                        "deconstruct": [
                            r"$(qb)^2 = q^2b^2$.",
                            r"$b^2 \cdot a^2 = a^2b^2$, and $b^2 \cdot p^2/b^2 = p^2$.",
                        ],
                    },
                    {
                        "prompt": r"Finally, take the square root and divide by $b$ to recover $q$ itself. Write $q$ in terms of $a$, $b$ and $p$.",
                        "answer": r"\frac{\sqrt{a^2b^2 - p^2}}{b}",
                        "placeholder": "a root, over b",
                        "hint": r"$qb = \sqrt{a^2b^2 - p^2}$ since $q$ and $b$ are both lengths and cannot be negative. Now divide.",
                        "deconstruct": [
                            r"From the last step, $qb = \sqrt{a^2b^2 - p^2}$.",
                            r"Divide both sides by $b$.",
                        ],
                    },
                ],
                "closing": r'''
Look at what the last two steps produced. Step 4 says $(qb)^2 = a^2b^2 - p^2$, and $qb$
is $|\mathbf{a}|\sin\theta$ multiplied by $|\mathbf{b}|$ — which is exactly
$|\mathbf{a}\times\mathbf{b}|$. Rearranged, that line reads

$$(\mathbf{a}\cdot\mathbf{b})^2 + |\mathbf{a}\times\mathbf{b}|^2 = |\mathbf{a}|^2|\mathbf{b}|^2$$

The identity that ties the two products together was never a separate fact. It is
Pythagoras applied to the two pieces a single vector splits into, with the dot product
measuring one piece and the cross product measuring the other. That is also why the two
products are the only two there are: a pair of vectors offers exactly one number about
how much they agree and one about how much they do not, and $\cos^2 + \sin^2 = 1$ says
those two exhaust the information.

Step 5 is the formula for the perpendicular distance from a point to a line, and it is
worth keeping. Put $\mathbf{a} = \mathbf{Q} - \mathbf{P}_0$, the displacement from a
point on the line to the point of interest, and $\mathbf{b} = \mathbf{u}$, the line's
direction, and $q$ is the distance. The equivalent form
$q = |\mathbf{a}\times\mathbf{b}|/b$ is the one usually quoted; the two are the same
statement, as the identity above shows.

One caution. Every step here divided by $b$, so the whole construction fails when
$\mathbf{b}$ is the zero vector — and rightly so, since "the part of $\mathbf{a}$ along
nothing in particular" is not a question with an answer. It also assumed $b > 0$ when
the square root was taken, which is safe for a magnitude and is not safe in general.
''',
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "Partial derivatives, sensitivity and how errors add",
            "summary": "Differentiate with respect to one thing at a time, and you can say what every component's tolerance is worth in volts before anything is built.",
            "concepts": [
                r"A **partial derivative** $\partial f/\partial x$ differentiates with respect to $x$ while every other variable is held still. No new rules are needed: treat the others as constants and differentiate as usual. The curly $\partial$ only announces that there were others to hold.",
                r"For small changes in several variables at once, $\Delta f \approx \frac{\partial f}{\partial x_1}\Delta x_1 + \frac{\partial f}{\partial x_2}\Delta x_2 + \cdots$ — module 7's tangent line with one term per variable.",
                r"Each partial derivative is a **sensitivity**. For the unloaded divider, $\partial V_{out}/\partial R_2 = V_{in}R_1/(R_1+R_2)^2$, in volts per ohm; multiply it by a resistor's tolerance in ohms and you have what that tolerance is worth in volts.",
                r"**Worst case** adds the magnitudes: $|\Delta f|_{\max} = \sum \left|\partial f/\partial x_i\right|\delta_i$, assuming every part is off in the direction that hurts. It always holds, and it is always pessimistic.",
                r"Independent random errors instead add **in quadrature**: $\sigma_f = \sqrt{\sum \left(\partial f/\partial x_i\,\sigma_i\right)^2}$, because a part that is high usually meets one that is low. For two equal contributions that is $\sqrt{2}$ smaller than the worst case, not 2 — and for ten equal ones it is $\sqrt{10}$, which is where the saving becomes worth having.",
                r"Signs matter, and they can cancel exactly. A divider whose two resistors are both 1% high delivers precisely the voltage it was designed for: the two sensitivities are equal and opposite, because only the *ratio* is doing any work. Matched parts on one chip are built to exploit this.",
                r"The vector of all the partial derivatives is the **gradient** $\nabla f$. It points the direction in which $f$ increases fastest, and EE141's $\mathbf{E} = -\nabla V$ is that sentence about electric potential.",
            ],
            "read": [
                {
                    "title": "One knob at a time",
                    "minutes": 13,
                    "body": r'''
Two trimmers on a board and a voltmeter across the output. Turn the left one and the
reading climbs; turn the right one and it falls. Somebody asks how many millivolts a
turn is worth, and the only honest first answer is a question back: *which trimmer, and
where is the other one standing?*

That exchange is the whole of this unit. A quantity that depends on one variable has
one slope. A quantity that depends on four has four slopes — one per variable — and
none of them means anything until you have said what the other three are doing. Say it,
and a four-variable problem becomes four one-variable problems, each of which is
module 3 again with nothing added.

## Holding the others still

Take the unloaded divider, which is the circuit this module keeps returning to because
it is the smallest one where two components fight over the same output:

$$V_{out}(V_{in}, R_1, R_2) = V_{in}\frac{R_2}{R_1 + R_2}$$

Freeze $V_{in}$ at 10 V and $R_1$ at 15 kΩ. What is left is a function of $R_2$ alone —
an ordinary curve you could plot on ordinary axes, rising from 0 V when $R_2 = 0$ and
flattening towards 10 V as $R_2$ grows without limit. That curve has an ordinary
derivative at every point, and that derivative is the **partial derivative** of
$V_{out}$ with respect to $R_2$:

$$\frac{\partial V_{out}}{\partial R_2} = \lim_{h\to 0}\frac{V_{out}(V_{in},\,R_1,\,R_2+h) - V_{out}(V_{in},\,R_1,\,R_2)}{h}$$

Look at what moved between the two evaluations on top: $R_2$ and nothing else. That is
the entire content of the curly $\partial$. It is not a new operation, it is a *label*
— a reminder that there were other variables in the room and that they were told to
stand still. If there had only ever been one variable the two symbols would mean the
same thing, which is why nobody writes $\partial$ in module 3.

## There is nothing new to differentiate

Because the others are constants for the duration, every rule from module 3 applies
unchanged. The only thing that takes practice is noticing when a variable appears in
more than one place, because then all of its appearances move together.

```
f = Vin * R2 / (R1 + R2)          differentiate with respect to R2

  R2 appears TWICE -- on the top, and inside the bottom. Quotient rule:

  d/dR2 [ R2 / (R1 + R2) ] = [ (R1 + R2)*1 - R2*1 ] / (R1 + R2)^2
                           = R1 / (R1 + R2)^2

  so  df/dR2 = Vin * R1 / (R1 + R2)^2


f = Vin * R2 / (R1 + R2)          differentiate with respect to R1

  R1 appears ONCE, in the bottom. Vin*R2 is now a constant multiplier:

  d/dR1 (R1 + R2)^-1 = -(R1 + R2)^-2

  so  df/dR1 = -Vin * R2 / (R1 + R2)^2
```

The two results are not mirror images of each other. They differ in sign, and they
differ in which resistor sits on top. That asymmetry is real: raising the bottom
resistor of a divider raises the output, raising the top resistor lowers it, and the
two effects are not the same size unless the two resistors are equal.

## Adding up several small changes

One partial derivative tells you the effect of moving one variable. Real components are
all wrong at once. To get from one to the other, move them one at a time and add up
what each move cost:

$$\Delta f = \underbrace{\big[f(x+\Delta x,\,y) - f(x,\,y)\big]}_{\text{move }x\text{ first}}
           + \underbrace{\big[f(x+\Delta x,\,y+\Delta y) - f(x+\Delta x,\,y)\big]}_{\text{then move }y}$$

The first bracket is a change in $x$ alone, so it is $\frac{\partial f}{\partial x}\Delta x$
to the accuracy of module 7's tangent line. The second is a change in $y$ alone — but
taken at $x + \Delta x$ rather than at $x$, so the slope it uses is very slightly the
wrong one. How wrong? By however much $\partial f/\partial y$ itself changes over a step
$\Delta x$, which is a small correction multiplied by an already small $\Delta y$. It is
a product of two small things, and it is dropped for the same reason module 7 drops
$\Delta x^2$:

$$\Delta f \approx \frac{\partial f}{\partial x}\Delta x + \frac{\partial f}{\partial y}\Delta y + \cdots$$

One term per variable, each of them a rate times a displacement. Check the units on any
term and they are the units of $f$: volts per ohm times ohms is volts. That check catches
more mistakes than any other single habit in this module.

Each partial derivative, used this way, is called a **sensitivity**. The word is not
decoration — it says what the number is for. Hand $\partial V_{out}/\partial R_2$ a
tolerance in ohms and it hands back an error in volts, which is the question the person
choosing the resistor actually has.

### Worked: what one resistor is worth

A 10 V rail, $R_1 = 15$ kΩ on top, $R_2 = 5$ kΩ to ground, output taken across $R_2$.

```
Vout       = 10 * 5000 / 20000                      = 2.5000 V

dVout/dR2  = Vin * R1 / (R1 + R2)^2
           = 10 * 15000 / 20000^2
           = 150000 / 4.000e8    = 3.750e-4 V/ohm   = 375.0 uV/ohm

dVout/dR1  = -Vin * R2 / (R1 + R2)^2
           = -10 * 5000 / 4.000e8 = -1.250e-4 V/ohm = -125.0 uV/ohm
```

Now put a tolerance on it. $R_2$ is a 1% part, so it may be up to 50 Ω away from 5 kΩ.
The prediction is $375.0\ \mu\text{V}/\Omega \times 50\ \Omega = 18.75$ mV.

Test the prediction against the exact answer, because the whole method rests on the
tangent line being close enough:

```
exact:   10 * 5050 / (15000 + 5050) = 10 * 5050 / 20050 = 2.518703 V
         shift = 2.518703 - 2.500000 = 18.703 mV

linear:  18.750 mV        high by 0.047 mV, which is 0.25% of the shift
```

Forty-seven microvolts of error on an eighteen-millivolt prediction. And the size of
that error is not mysterious — for this function it is exactly the fraction
$\Delta R_2/(R_1+R_2)$, here $50/20000 = 0.25\%$, because the exact shift carries
$(R_1+R_2+\Delta R_2)$ in its denominator where the linear one carries $(R_1+R_2)$:

```
  dR2 = 1% of R2      linear 18.750 mV   exact 18.703 mV   high by  0.25%
  dR2 = 5% of R2      linear 93.750 mV   exact 92.593 mV   high by  1.25%
  dR2 = 10% of R2     linear 187.50 mV   exact 182.93 mV   high by  2.50%
  dR2 = 50% of R2     linear 937.50 mV   exact 833.33 mV   high by 12.50%
```

At the tolerances components actually come in, the linear estimate is good to a fraction
of a percent *of an already small quantity*, and its error is far below anything you
could measure. At 50% it is a different tool being used for a different job, badly.

### Worked: the corner frequency, where logarithms are easier

An RC low-pass has $f_c = 1/(2\pi RC)$, with $R = 4.7$ kΩ and $C = 100$ nF.

```
fc      = 1 / (2 pi * 4700 * 100e-9)
        = 1 / (2 pi * 4.700e-4)
        = 1 / 2.95310e-3        = 338.63 Hz

dfc/dR  = -1 / (2 pi R^2 C) = -fc / R = -338.63 / 4700   = -0.07205 Hz/ohm
dfc/dC  = -1 / (2 pi R C^2) = -fc / C = -338.63 / 1e-7   = -3.386e9 Hz/F
```

Both are correct and the pair is useless. One is per ohm and one is per farad, and
"3.4 gigahertz per farad" tells you nothing until you also remember that a farad is an
absurd amount of capacitance. Quantities in wildly different units cannot be compared,
so scale them: divide by the size of the output and multiply by the size of the input.
That gives the **relative sensitivity**, a pure number:

$$S^{f}_{x} = \frac{x}{f}\frac{\partial f}{\partial x} = \frac{\partial \ln f}{\partial \ln x}$$

```
S(fc, R) = (4700 / 338.63) * (-0.07205) = -1.000
S(fc, C) = (1e-7  / 338.63) * (-3.386e9) = -1.000
```

Both exactly $-1$: one percent up on either part is one percent down on the corner. The
logarithm form says why in one line, with no arithmetic at all —
$\ln f_c = -\ln 2\pi - \ln R - \ln C$, and the derivative of a logarithm with respect to
a logarithm is just the exponent. For any expression built only from products, quotients
and powers, the relative sensitivities *are the exponents*, and you can read them off
without differentiating anything.

## The mistake, and why it is tempting

The common error is to differentiate $V_{in}R_2/(R_1+R_2)$ with respect to $R_2$ and
write $V_{in}/(R_1+R_2)$ — treating the bottom as a constant because "the other
variables are held fixed". For the divider above that gives
$10/20000 = 500\ \mu\text{V}/\Omega$ against the true 375, a third too big.

It is tempting because the instruction really is *hold the others fixed*, and the
denominator is where the other one lives, so the denominator feels like it should be
held fixed too. It is not: $R_2$ is in there as well, and every appearance of the
variable you are differentiating has to move.

Nothing about units catches it — both answers come out in volts per ohm. What catches
it is asking what the wrong answer claims. A constant $500\ \mu\text{V}/\Omega$ says the
output climbs at a steady rate for ever, so at $R_2 = 100$ kΩ it would read 50 V from a
10 V rail. The real slope must fade to zero as $R_2$ grows, because the output is
creeping up on $V_{in}$ and cannot pass it — and
$V_{in}R_1/(R_1+R_2)^2$, with its squared denominator, does exactly that.

A second, quieter slip is assuming the partials are similar in size. Here they are 375
and $-125$: a factor of three apart, and opposite in sign. Which resistor deserves the
expensive tolerance is decided by that factor, and guessing gets it wrong half the time.

## Where this stops holding

**The steps must be small compared with the curvature.** The table above puts a number
on "small" for one function; in general the neglected term is
$\frac{1}{2}\frac{\partial^2 f}{\partial x^2}\Delta x^2$ and its friends, so the
approximation degrades as the square. When it matters, either keep the second-order
terms or stop approximating and evaluate the exact function at the corners.

**The variables must be free to move independently.** Partials assume you can hold $R$
still while $C$ moves. Warm the board and both change at once, so the drift of $f_c$
with temperature is not either partial but the chain rule through the shared variable:
$\frac{df_c}{dT} = \frac{\partial f_c}{\partial R}\frac{dR}{dT} + \frac{\partial f_c}{\partial C}\frac{dC}{dT}$.
That is why a $+100$ ppm/°C resistor paired with a $-100$ ppm/°C capacitor gives a
corner frequency that barely moves at all — a cancellation the independent analysis
cannot see, because it never asked whether the two errors were related.

**The function must be smooth where you are standing.** A comparator flipping at a
threshold, an amplifier hitting its rail, a part leaving its rated range: at the kink
there is no single slope, and a sensitivity computed on one side of it is silent about
the other. There the honest method is to evaluate both cases.

**A sensitivity is local.** $375\ \mu\text{V}/\Omega$ is the figure at $R_2 = 5$ kΩ and
nowhere else; at 50 kΩ, with the same $R_1$, it is
$10 \times 15000/65000^2 = 35.5\ \mu\text{V}/\Omega$. Quoting a sensitivity without the
operating point it was taken at is quoting half a number.

Collect all the partials of one function into a list and you have the **gradient**,
$\nabla f$ — the vector that points the way $f$ climbs fastest. That object is the
subject of the next course but one; here, the list is a tolerance budget, and adding
the terms up is the next unit.
''',
                },
                {
                    "title": "Adding up what the tolerances are worth",
                    "minutes": 14,
                    "body": r'''
Take a bag of 1% resistors, build two hundred copies of the same divider, and measure
every output. You get a pile of readings clustered around the nominal value. Two
different questions can be asked of that pile, they have two different answers, and
confusing them is the most common failure in this subject.

The first question is *how far out could a board possibly be?* The second is *how far
out are the boards actually?* The first has a hard answer that no board will ever
reach. The second has a soft answer that describes almost all of them. Both are worth
computing, and each is the wrong answer to the other question.

## Worst case, and where it comes from

Start from the total change of the previous unit, writing $s_i$ for the sensitivity
$\partial f/\partial x_i$ and $\delta_i$ for the largest error part $i$ is allowed:

$$\Delta f = \sum_i s_i \Delta x_i, \qquad |\Delta x_i| \le \delta_i$$

Take the magnitude of both sides. The triangle inequality — the size of a sum is never
more than the sum of the sizes — gives

$$|\Delta f| = \left|\sum_i s_i \Delta x_i\right| \;\le\; \sum_i |s_i|\,|\Delta x_i| \;\le\; \sum_i |s_i|\,\delta_i$$

That last expression is the **worst case**. Two things about it are worth being explicit
about, because both get forgotten. It is a genuine bound: nothing inside the tolerances
can exceed it, which is what makes it the right tool when a limit must not be crossed.
And equality needs every single term to be at its full size *and* pointing the same way
— which is a coincidence of $n$ separate coincidences.

### Worked: a divider budget

A 9 V rail, $R_1 = 22$ kΩ on top, $R_2 = 10$ kΩ to ground, both 1% parts.

```
S      = R1 + R2 = 32.0 k
Vout   = 9 * 10000 / 32000                       = 2.8125 V

s1 = dVout/dR1 = -9 * 10000 / 32000^2  = -8.7891e-5 V/ohm  = -87.89 uV/ohm
s2 = dVout/dR2 = +9 * 22000 / 32000^2  = +1.9336e-4 V/ohm  = +193.36 uV/ohm

d1 = 1% of 22.0 k = 220 ohm            d2 = 1% of 10.0 k = 100 ohm

|s1| d1 = 87.89e-6 * 220 = 19.336 mV
|s2| d2 = 193.36e-6 * 100 = 19.336 mV
                            ----------
worst case                   38.672 mV        (1.375% of 2.8125 V)
```

The two contributions came out exactly equal, and that is not luck. Both are
$V_{in}R_1R_2/(R_1+R_2)^2$ divided by a hundred — the expression is symmetric in the two
resistors once each tolerance is written as a percentage of its own part. Any divider
built from two parts of the same percentage tolerance splits its error budget exactly in
half, whatever the ratio.

The bound can be tested, because the exact endpoints are computable:

```
lowest  Vout: R1 1% high, R2 1% low   9 * 9900 / (22220 + 9900)  = 2.77397 V   (-38.53 mV)
highest Vout: R1 1% low,  R2 1% high  9 * 10100 / (21780 + 10100) = 2.85132 V   (+38.82 mV)
```

The linear budget said $\pm 38.67$ mV and the truth is $-38.53$ / $+38.82$ mV. The real
interval is slightly lopsided, because the function is curved, and the linear figure
sits between the two — close enough to be the number you design with, and worth knowing
is not exact.

## Why nobody ever measures the worst case

Every part has to be at the end of its band, and at the correct end. With two parts
there are four corners of the tolerance box and one of them is worst. With $n$ parts
there are $2^n$ corners.

Put a number on it. Suppose a part's actual value is spread evenly across its band. The
chance it lands in the outermost tenth of that band, at the harmful end, is one in ten.
For six such parts to do it at once is one in a million boards — and that is only the
outermost tenth, not the corner itself, whose probability is zero for a continuous
spread. Meanwhile the *typical* board has some parts high, some low, and most of them
near the middle, so the errors partly cancel before they ever reach the output.

This is why a worst-case budget quoted as the expected performance is not merely
pessimistic, it is misleading: it describes a board that will not be built.

## Quadrature, and where that comes from

For the typical board, model each error as an independent random variable $X_i$ with
mean zero and standard deviation $\sigma_i$. Then $\Delta f = \sum s_i X_i$ is itself
random, and the useful fact about variance is that it adds:

$$\operatorname{Var}\!\left(\sum_i s_i X_i\right) = \sum_i s_i^2\sigma_i^2 + 2\sum_{i<j} s_is_j\operatorname{Cov}(X_i, X_j)$$

The cross terms are what the assumption of independence kills: independent variables
have zero covariance, so everything after the first sum vanishes and

$$\sigma_f = \sqrt{\sum_i \left(s_i\sigma_i\right)^2}$$

This is **adding in quadrature**, or the root-sum-square. Notice that squaring destroys
the signs. Quadrature cannot tell a sensitivity of $+193$ from one of $-193$, which
means it cannot see cancellation — and cancellation is exactly what happens when errors
are *not* independent. The formula does not merely assume independence as a convenience;
its answer is wrong in a specific, knowable direction without it.

### Worked: the same divider, in quadrature

```
|s1| d1 = 19.336 mV        |s2| d2 = 19.336 mV

rss = sqrt(19.336^2 + 19.336^2) = 19.336 * sqrt(2) = 27.345 mV

worst case  38.672 mV
quadrature  27.345 mV        smaller by a factor of sqrt(2) = 1.414
```

Two equal contributions give a saving of $\sqrt2$, which is 29% — real but not
dramatic. The saving grows as the square root of the number of contributions, and that
is where it becomes worth having. Ten equal 5 mV contributions:

```
worst case  10 * 5.00 =  50.00 mV
quadrature  sqrt(10) * 5.00 = 15.81 mV        a factor of 3.16
```

A word about what goes into $\sigma_i$, because this is where the arithmetic gets
quietly dishonest. A 1% tolerance is a *bound*, not a standard deviation. If the parts
really were spread evenly across the band then $\sigma = \delta/\sqrt3 = 0.577\delta$,
and the quadrature figure above would be 15.8 mV rather than 27.3. Feeding the bounds
$\delta_i$ into the root-sum-square instead, as everyone does and as the lab in this
module does, produces a useful, comparable, conventional number — but it is a
convention, not a theorem, and it should be labelled "RSS of tolerances" rather than
"one sigma". Quadrature of genuine standard deviations is a theorem. Quadrature of
tolerances is a habit.

## Products and quotients: work in fractions

When $f$ is built only from products, quotients and powers, dividing through by $f$ is
much less work than differentiating. For $f = x^ay^b$, take logarithms first:

$$\ln f = a\ln x + b\ln y \quad\Longrightarrow\quad \frac{\Delta f}{f} = a\frac{\Delta x}{x} + b\frac{\Delta y}{y}$$

The exponents are the relative sensitivities. No quotient rule, no algebra, and the
answer arrives as a percentage, which is the unit tolerances are quoted in anyway.

### Worked: how far the corner can move

$f_c = 1/(2\pi RC) = R^{-1}C^{-1}/2\pi$, so both exponents are $-1$. Take a 1% resistor
and a 10% capacitor, which is the usual pairing — film capacitors are far looser parts
than resistors.

```
worst case   |-1|*1% + |-1|*10%          = 11.00%     -> 0.1100 * 338.63 = 37.25 Hz
quadrature   sqrt(1^2 + 10^2)            = 10.05%     -> 0.1005 * 338.63 = 34.03 Hz
```

Look at what the resistor bought. In quadrature the 1% part moved the total from 10.00%
to 10.05%. Replacing it with a 0.1% part would move it to 10.0005%. That is the single
most useful thing quadrature tells you, and worst case never will: when one contribution
dominates, the others cost nothing and buying them down is money set on fire. Spend it
on the capacitor.

And here the linearisation is starting to creak, because 10% is not small:

```
highest corner: R 1% low, C 10% low     1 / (0.99 * 0.90) = 1.1223  ->  +41.43 Hz
lowest  corner: R 1% high, C 10% high   1 / (1.01 * 1.10) = 0.9001  ->  -33.83 Hz
```

The linear budget said $\pm 37.25$ Hz. The true interval runs from $-33.8$ to $+41.4$ Hz
— visibly asymmetric, and 11% wider on the high side than predicted, because $1/x$
curves upwards. At 1% tolerances this effect was invisible; at 10% it is the difference
between passing and failing a specification written at the edge.

## The mistakes, and why they are tempting

**Quoting quadrature when the errors are correlated.** Temperature is the usual culprit:
every part on a board sits at the same temperature, so their drifts are not independent,
they are nearly identical. Sometimes that helps enormously — the derivation later in
this module shows a divider whose common drift cancels exactly — and sometimes it hurts,
because a sum of ten identically drifting parts drifts ten times as much, with no
$\sqrt{10}$ relief anywhere. Quadrature is neither of those answers. It is tempting
because it is always the smaller number, and there is always pressure for the number to
be smaller.

**Assuming the tolerance is the answer.** Ten percent on $C$ does not mean ten percent
on everything downstream of $C$; it means ten percent multiplied by the relative
sensitivity, and that is not always 1. In module 6, $\omega_n = 1/\sqrt{LC}$ has
exponents of $-\tfrac12$, so 10% on $L$ and 10% on $C$ together give
$\tfrac12(10) + \tfrac12(10) = 10\%$ on $\omega_n$ in the worst case, not 20%. The
square root halves both contributions. Read the exponent before adding anything.

## Where this stops holding

**Correlated errors need the covariance term.** Keeping it, and writing $\rho$ for the
correlation between two errors, gives
$\sigma_f^2 = (s_1\sigma_1)^2 + (s_2\sigma_2)^2 + 2\rho\,(s_1\sigma_1)(s_2\sigma_2)$.
For the divider above, $s_1\sigma_1 = -19.34$ mV and $s_2\sigma_2 = +19.34$ mV. With
$\rho = 0$ that returns 27.3 mV. With $\rho = 1$ — both resistors drifting the same way
together, as they do on one chip — it collapses to
$|{-19.34} + 19.34| = 0$. One formula, both extremes, and the independent case sitting
between them.

**Large tolerances need the exact corners or a simulation.** The 10% capacitor above
already bends the answer. Past that, evaluate the function at the corners, or draw
random samples and measure the spread of the results, which is what `spread` does in
this module's lab and why it is worth having next to the two formulas.

**A hard limit is a worst-case question, always.** If exceeding a value damages
something — a rating, a breakdown voltage, a regulator dropping out — quadrature is the
wrong tool no matter how many parts are involved, because it answers a question about
typical boards and the question asked is about every board.

**The distribution may not be what you assumed.** Parts from one reel come from one
production lot and track each other; a value that has been sorted, with the close ones
sold as a tighter grade, leaves a bin that is emptiest in the middle. Neither is the
even spread the $\delta/\sqrt3$ figure assumed, and neither is a bell curve.
''',
                },
            ],
            "tune": {
                "title": "A divider ratio, and what one notch of the slider is worth",
                "minutes": 10,
                "brief": r'''
The panel reports the divider ratio $R_2/(R_1+R_2)$ to three decimal places, and the
total current the pair draws from the rail. Hit a ratio of 0.360 — the window of
±0.004 around it is about what a pair of 1% resistors would hold — while keeping the
current under half a milliamp.

Then do the part this module is actually about. Before you move anything, work out

$$\frac{\partial}{\partial R_2}\frac{R_2}{R_1+R_2} = \frac{R_1}{(R_1+R_2)^2}$$

at the position you have landed on, multiply it by 100 Ω — one notch of the slider —
and predict the change in the third decimal place of the ratio. Then move it one
notch and see whether you were right.
''',
                "prompt": r"Set a divider ratio of 0.360 ± 0.004, drawing under 0.50 mA from the 5 V rail.",
                "note": "The ratio does not fix the current: it is the size of the pair that does, and the two constraints therefore pull in different directions.",
                "model": "divider",
                "initial": {"r1": 2200, "r2": 2200},
                "constants": {"vin": 5},
                "plotKey": "vout",
                "constraints": [
                    {"k": "ratio", "label": "divider ratio 0.360 ± 0.004", "eq": 0.360, "tol": 0.004},
                    {"k": "i", "label": "total current ≤ 0.50 mA", "max": 0.5},
                ],
            },
            "quiz": {
                "title": "What a tolerance is worth",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"For the unloaded divider $V_{out} = V_{in}R_2/(R_1+R_2)$, what is $\partial V_{out}/\partial R_2$?",
                        "opts": [
                            r"$\dfrac{V_{in}}{R_1+R_2}$",
                            r"$\dfrac{V_{in}R_1}{(R_1+R_2)^2}$",
                            r"$-\dfrac{V_{in}R_2}{(R_1+R_2)^2}$",
                            r"$\dfrac{V_{in}R_2}{(R_1+R_2)^2}$",
                        ],
                        "a": 1,
                        "why": (
                            r"Quotient rule, with $R_1$ held fixed: the top differentiates to 1 and the bottom to 1, "
                            r"leaving $\frac{(R_1+R_2) - R_2}{(R_1+R_2)^2} = \frac{R_1}{(R_1+R_2)^2}$, all times "
                            r"$V_{in}$. The expression with $R_2$ on top and a minus sign is the derivative with "
                            r"respect to $R_1$ — the other partial, and the reason the two can cancel."
                        ),
                    },
                    {
                        "q": r"Both resistors of a divider turn out to be exactly 1% high. What happens to the output voltage?",
                        "opts": [
                            "It rises by 1%",
                            "It rises by 2%",
                            "It does not move",
                            "It falls by 1%",
                        ],
                        "a": 2,
                        "why": (
                            r"$V_{out}$ depends only on the ratio $R_2/(R_1+R_2)$, and multiplying both resistors by "
                            r"1.01 leaves that ratio untouched. Through the sensitivities: the two terms are "
                            r"$-\frac{V_{in}R_2}{(R_1+R_2)^2}\times 0.01R_1$ and "
                            r"$+\frac{V_{in}R_1}{(R_1+R_2)^2}\times 0.01R_2$, which are equal and opposite. What does "
                            r"change is the current, by about 1% downwards."
                        ),
                    },
                    {
                        "q": r"Two independent error sources each contribute 10 mV. What are the worst-case and root-sum-square totals?",
                        "opts": [
                            "20 mV and 14 mV",
                            "20 mV and 20 mV",
                            "14 mV and 20 mV",
                            "10 mV and 10 mV",
                        ],
                        "a": 0,
                        "why": (
                            r"Worst case assumes both go the same way: $10 + 10 = 20$ mV. In quadrature: "
                            r"$\sqrt{10^2+10^2} = 14.1$ mV. The quadrature figure is always the smaller of the two, "
                            r"and quoting it commits you to the claim that the sources really are independent — which "
                            r"is a statement about the circuit, not about the arithmetic."
                        ),
                    },
                    {
                        "q": r"A quantity is the product of two measurements, one 2% uncertain and the other 3%. In the worst case, how uncertain is the product?",
                        "opts": ["1%", "5%", "6%", "3.6%"],
                        "a": 1,
                        "why": (
                            r"For a product the *fractional* errors add: $(1.02)(1.03) = 1.0506$, so about 5%. "
                            r"Multiplying the percentages gives 0.06%, which is the size of the term everyone "
                            r"correctly neglects; 3.6% is the quadrature answer, right only if the two are "
                            r"independent random errors rather than a worst case."
                        ),
                    },
                    {
                        "q": r"Why is a partial derivative called a sensitivity in this context?",
                        "opts": [
                            "Because it says how accurately the variable must be measured",
                            "Because multiplying it by a component's tolerance gives the resulting change in the output",
                            "Because it is always the largest of the derivatives",
                            "Because it is dimensionless",
                        ],
                        "a": 1,
                        "why": (
                            r"$\partial V_{out}/\partial R_2$ comes out in volts per ohm; hand it a tolerance in ohms "
                            r"and it hands back volts. That is the whole of tolerance analysis. It is emphatically "
                            r"not dimensionless — the *relative* sensitivity, "
                            r"$\frac{x}{f}\frac{\partial f}{\partial x}$, is the dimensionless cousin, and it is the "
                            r"one quoted as a percentage per percentage."
                        ),
                    },
                    {
                        "q": r"What is the gradient of a scalar function of several variables?",
                        "opts": [
                            "The largest of its partial derivatives",
                            "The sum of its partial derivatives",
                            "The vector of all its partial derivatives, pointing the way the function increases fastest",
                            "The rate of change along the x axis",
                        ],
                        "a": 2,
                        "why": (
                            r"$\nabla f = (\partial f/\partial x, \partial f/\partial y, \partial f/\partial z)$ — one "
                            r"component per variable, assembled into a vector. Its direction is the direction of "
                            r"steepest increase and its magnitude is that steepest rate. Adding the partials together "
                            r"would throw away the directions, which are the entire point."
                        ),
                    },
                ],
            },
            "blanks": [
                {
                    "title": "The five lines a tolerance budget is made of",
                    "minutes": 9,
                    "caption": "s_i is the sensitivity of f to x_i, delta_i is a bound on the error, sigma_i a standard deviation",
                    "lang": "text",
                    "brief": r'''
Nothing runs here. Each line is one of the rules from the reading with its right-hand
side removed, and they are in the order you would use them: differentiate, combine,
bound, estimate, and finally rescale into percentages.

`sum` is a sum over every variable, `sqrt` is a square root, `^` is a power, and
`|...|` is a magnitude.
''',
                    "listing": r'''
f depends on x_1 ... x_n, none of them known exactly


the sensitivity of f to x_i          s_i      =  ___

the change from all of them at once  df       =  ___

every part off in the direction
that hurts, with |dx_i| <= delta_i   |df|max  =  ___

independent random errors, each
with standard deviation sigma_i      sigma_f  =  ___

the dimensionless version of s_i,
a percent of f per percent of x      S_x      =  ___
''',
                    "blanks": [
                        {
                            "prompt": "The rate itself.",
                            "hole": "?",
                            "opts": [
                                "df/dx_i with every other variable held still",
                                "df/dx_i with every other variable also moving",
                                "f / x_i",
                                "the total change in f divided by the total change in x_i",
                            ],
                            "a": 0,
                            "why": r"A partial derivative is the ordinary derivative of a function that has had all but one of its variables frozen. That freezing is the only thing the curly $\partial$ announces, and it is what makes the $n$ rates separable in the first place.",
                            "whys": [
                                r"A partial derivative is the ordinary derivative of a function that has had all but one of its variables frozen. That freezing is the only thing the curly $\partial$ announces, and it is what makes the $n$ rates separable in the first place.",
                                r"If the others move too you have a *total* derivative, which needs to be told how they move — the chain rule through a shared variable such as temperature. That is a different and later question; the budget below is built from the frozen ones.",
                                r"$f/x_i$ is an average, not a rate. For the divider it would give $V_{out}/R_2 = V_{in}/(R_1+R_2)$, which is a real quantity but not the slope at the point — and it is exactly the wrong answer the reading warns about.",
                                r"That is a secant over the whole range rather than a tangent at the operating point, and it needs both endpoints to exist. Sensitivities are local: they are quoted with the operating point they were taken at.",
                            ],
                        },
                        {
                            "prompt": "One term per variable.",
                            "hole": "?",
                            "opts": [
                                "sum of |s_i| dx_i",
                                "sum of s_i dx_i",
                                "product of s_i dx_i over all i",
                                "sum of s_i",
                            ],
                            "a": 1,
                            "why": r"Move one variable at a time and add up what each move cost: $\Delta f \approx \sum_i s_i\Delta x_i$. The signs stay, because they are what allows one part's error to cancel another's. Each term is a rate times a displacement, so each has the units of $f$.",
                            "whys": [
                                r"Taking magnitudes here throws the signs away before they have done any work, and the signs are the whole reason a divider with two matched errors holds its output. Magnitudes belong in the worst-case line below, not in this one.",
                                r"Move one variable at a time and add up what each move cost: $\Delta f \approx \sum_i s_i\Delta x_i$. The signs stay, because they are what allows one part's error to cancel another's. Each term is a rate times a displacement, so each has the units of $f$.",
                                r"A product of $n$ small quantities is vanishingly smaller than any one of them — it is the second-order term that gets *dropped*, not the answer. Two errors of 1% would multiply to 0.01%.",
                                r"Without the $\Delta x_i$ this is a sum of rates, which does not even have the units of $f$: volts per ohm added to volts per volt is not volts. Every term needs the displacement that turns a rate into a change.",
                            ],
                        },
                        {
                            "prompt": "The bound nothing inside the tolerances can beat.",
                            "hole": "?",
                            "opts": [
                                "|sum of s_i delta_i|",
                                "max over i of |s_i| delta_i",
                                "sum of |s_i| delta_i",
                                "sqrt of the sum of (s_i delta_i)^2",
                            ],
                            "a": 2,
                            "why": r"The triangle inequality: $\left|\sum s_i\Delta x_i\right| \le \sum|s_i||\Delta x_i| \le \sum|s_i|\delta_i$. Taking the magnitude of each term separately is what assumes every part is off in the direction that hurts, and it is the step that makes the result a bound rather than an estimate.",
                            "whys": [
                                r"Taking the magnitude at the end rather than term by term lets opposite signs cancel, which is the *best* case, not the worst. For the divider it would return zero — a perfect output from imperfect parts, guaranteed, which is plainly not a bound on anything.",
                                r"The largest single contribution is a lower bound on the worst case, not the worst case. It is right only when one term dominates so heavily that the others round away, and knowing that is true requires computing them.",
                                r"The triangle inequality: $\left|\sum s_i\Delta x_i\right| \le \sum|s_i||\Delta x_i| \le \sum|s_i|\delta_i$. Taking the magnitude of each term separately is what assumes every part is off in the direction that hurts, and it is the step that makes the result a bound rather than an estimate.",
                                r"That is the quadrature figure, and it is always the smaller of the two. It estimates the spread of the boards you will actually build; it does not bound anything, and quoting it where a rating must not be exceeded is the standard way to ship a design that fails one board in a thousand.",
                            ],
                        },
                        {
                            "prompt": "What the spread of real boards looks like.",
                            "hole": "?",
                            "opts": [
                                "sum of s_i sigma_i",
                                "sqrt of the sum of s_i sigma_i",
                                "(sum of s_i sigma_i)^2",
                                "sqrt of the sum of (s_i sigma_i)^2",
                            ],
                            "a": 3,
                            "why": r"Variances add for independent variables, and the variance of $s_iX_i$ is $s_i^2\sigma_i^2$. Add the squares, then take the root once at the end. Squaring is also what destroys the signs, which is why this formula cannot see the cancellation that matched parts give you.",
                            "whys": [
                                r"Standard deviations do not add; variances do. Two equal contributions combine to $c\sqrt2$, not $2c$ — and written this way the sensitivities keep their signs, so for a divider made of two 1% resistors the formula would predict no spread at all, which no bench measurement would agree with.",
                                r"The square root has to be taken of a sum of *squares*. As written the units are wrong too — the root of a voltage is not a voltage.",
                                r"This is the variance, not the standard deviation: one square root short, and in the wrong units. For 19.3 mV and 19.3 mV it would return 0.0015 V², a number with no reading on any meter.",
                                r"Variances add for independent variables, and the variance of $s_iX_i$ is $s_i^2\sigma_i^2$. Add the squares, then take the root once at the end. Squaring is also what destroys the signs, which is why this formula cannot see the cancellation that matched parts give you.",
                            ],
                        },
                        {
                            "prompt": "The one you can compare across different kinds of quantity.",
                            "hole": "?",
                            "opts": [
                                "(f / x) df/dx",
                                "(x / f) df/dx",
                                "x f df/dx",
                                "df/dx with x measured as a percentage",
                            ],
                            "a": 1,
                            "why": r"$S_x = \frac{x}{f}\frac{\partial f}{\partial x}$ divides out the units of both, leaving a pure number: a percent of $f$ per percent of $x$. It is the only way to say that a corner frequency cares equally about its resistor and its capacitor, when one sensitivity is in Hz/Ω and the other in Hz/F. For $f = x^ay^b$ these numbers are simply $a$ and $b$.",
                            "whys": [
                                r"This is upside down, and it does not come out dimensionless: for the corner frequency it gives $(f_c/R)(-f_c/R) = -f_c^2/R^2$, in hertz squared per ohm squared. Check any candidate by asking whether the units cancel — only the arrangement that divides by $f$ and multiplies by $x$ does.",
                                r"$S_x = \frac{x}{f}\frac{\partial f}{\partial x}$ divides out the units of both, leaving a pure number: a percent of $f$ per percent of $x$. It is the only way to say that a corner frequency cares equally about its resistor and its capacitor, when one sensitivity is in Hz/Ω and the other in Hz/F. For $f = x^ay^b$ these numbers are simply $a$ and $b$.",
                                r"Multiplying by both makes the units worse rather than better, and it grows without limit as either quantity grows. A dimensionless sensitivity has to divide by $f$, not multiply by it.",
                                r"Rescaling the input alone is half the job: it clears the ohms but leaves the answer in the units of $f$. Both ends have to be made relative, which is what dividing by $f$ does.",
                            ],
                        },
                    ],
                },
                {
                    "title": "A tolerance budget, filled in",
                    "minutes": 10,
                    "caption": "a 9.00 V rail, a 22.0 k / 10.0 k divider, both resistors 1% parts",
                    "lang": "text",
                    "brief": r'''
This is the same divider the numeric ladder uses, worked through line by line. Two of
the numbers are given so the pattern is visible; fill in the rest.

Everything is to first order, so a 1% resistor contributes its sensitivity multiplied by
1% of its own nominal value — 220 Ω for the 22.0 kΩ part, 100 Ω for the 10.0 kΩ one.
''',
                    "listing": r'''
Vin = 9.00 V     R1 = 22.0 k (1%)     R2 = 10.0 k (1%)     Vout across R2

R1 + R2 = 32.0 k


nominal output      Vin R2 / (R1 + R2)          =  ___ V

sensitivity to R1   -Vin R2 / (R1 + R2)^2       =  -87.89 uV/ohm
sensitivity to R2   +Vin R1 / (R1 + R2)^2       =  ___ uV/ohm

R1 is out by 220 ohm    220 x  87.89 uV/ohm     =  ___ mV
R2 is out by 100 ohm    100 x 193.36 uV/ohm     =  19.34 mV

worst case          the two magnitudes added    =  ___ mV
independent random  the two added in quadrature =  ___ mV
both parts 1% HIGH  the two added WITH signs    =  ___ mV
''',
                    "blanks": [
                        {
                            "prompt": "The output the divider is designed to give.",
                            "hole": "?",
                            "opts": ["4.5000", "2.8125", "0.3125", "6.1875"],
                            "a": 1,
                            "why": r"$9.00 \times 10000/32000 = 9.00 \times 0.3125 = 2.8125$ V. The output is taken across the *lower* resistor, so the ratio has $R_2$ on top.",
                            "whys": [
                                r"Half the supply is what an equal pair would give. These are 22 k and 10 k, so the lower resistor takes less than a third.",
                                r"$9.00 \times 10000/32000 = 9.00 \times 0.3125 = 2.8125$ V. The output is taken across the *lower* resistor, so the ratio has $R_2$ on top.",
                                r"That is the ratio $R_2/(R_1+R_2)$ itself, which is dimensionless. It still needs multiplying by the 9.00 V rail.",
                                r"That is the drop across $R_1$, the other resistor: $9.00 - 2.8125 = 6.1875$ V. The two do add to the supply, which is a useful check once you have the right one.",
                            ],
                        },
                        {
                            "prompt": "Volts per ohm, at the lower resistor.",
                            "hole": "?",
                            "opts": ["281.25", "193.36", "87.89", "618.75"],
                            "a": 1,
                            "why": r"$V_{in}R_1/(R_1+R_2)^2 = 9 \times 22000/32000^2 = 198000/1.024\times10^9 = 1.9336\times10^{-4}$ V/Ω, or 193.36 µV/Ω. It is larger than the sensitivity to $R_1$ by the ratio $R_1/R_2 = 2.2$, because $R_1$ is the resistor that sits on top of the fraction.",
                            "whys": [
                                r"This is $V_{in}/(R_1+R_2) = 9/32000$, the answer you get by treating the denominator as a constant. $R_2$ appears in the denominator too, and differentiating it there is what turns $V_{in}$ on the top into $V_{in}R_1$ and squares the bottom.",
                                r"$V_{in}R_1/(R_1+R_2)^2 = 9 \times 22000/32000^2 = 198000/1.024\times10^9 = 1.9336\times10^{-4}$ V/Ω, or 193.36 µV/Ω. It is larger than the sensitivity to $R_1$ by the ratio $R_1/R_2 = 2.2$, because $R_1$ is the resistor that sits on top of the fraction.",
                                r"That is the sensitivity to $R_1$, already given on the line above. The two are not equal: they carry $R_2$ and $R_1$ respectively on the top, so they differ by a factor of 2.2 here.",
                                r"That is $V_{in}R_1/\big((R_1+R_2)R_2\big)$ — a denominator built from two different factors instead of the sum squared. The quotient rule leaves $(R_1+R_2)^2 = 1.024\times10^9$ underneath, and $R_2$ does not appear there on its own at all.",
                            ],
                        },
                        {
                            "prompt": "What the top resistor's 1% is worth at the output.",
                            "hole": "?",
                            "opts": ["19.34", "8.79", "38.67", "1.93"],
                            "a": 0,
                            "why": r"$87.89\ \mu\text{V}/\Omega \times 220\ \Omega = 19.34$ mV. It matches the lower resistor's contribution exactly, and that is structural rather than lucky: both terms equal $V_{in}R_1R_2/(R_1+R_2)^2$ divided by 100, so any divider made of two parts of equal percentage tolerance splits its budget in half.",
                            "whys": [
                                r"$87.89\ \mu\text{V}/\Omega \times 220\ \Omega = 19.34$ mV. It matches the lower resistor's contribution exactly, and that is structural rather than lucky: both terms equal $V_{in}R_1R_2/(R_1+R_2)^2$ divided by 100, so any divider made of two parts of equal percentage tolerance splits its budget in half.",
                                r"That is $87.89\ \mu\text{V}/\Omega \times 100\ \Omega$ — the other resistor's tolerance applied to this resistor's sensitivity. One percent of 22.0 kΩ is 220 Ω, not 100 Ω.",
                                r"That is both contributions together, which is the worst-case line further down. This line is one of the two.",
                                r"Out by a factor of ten. $87.89\times10^{-6} \times 220$ is $1.934\times10^{-2}$ V, and a volt is a thousand millivolts.",
                            ],
                        },
                        {
                            "prompt": "Both parts off in the direction that hurts.",
                            "hole": "?",
                            "opts": ["27.35", "19.34", "38.67", "0.00"],
                            "a": 2,
                            "why": r"$19.34 + 19.34 = 38.67$ mV, which is 1.375% of the 2.8125 V nominal. The exact endpoints are $-38.53$ mV and $+38.82$ mV, so the linear budget sits between them: close enough to design with, and not exact, because the function is curved.",
                            "whys": [
                                r"That is the quadrature figure, $19.34\sqrt2$. It is an estimate of the spread of real boards, not a bound, and it belongs on the line below.",
                                r"That is one contribution. The worst case has both parts off at once, in the directions that push the output the same way.",
                                r"$19.34 + 19.34 = 38.67$ mV, which is 1.375% of the 2.8125 V nominal. The exact endpoints are $-38.53$ mV and $+38.82$ mV, so the linear budget sits between them: close enough to design with, and not exact, because the function is curved.",
                                r"Zero is what the two terms give when added *with* their signs and with both parts off the same way — the last line of this table. The worst case is the opposite assumption: the parts off in opposite directions, so that nothing cancels.",
                            ],
                        },
                        {
                            "prompt": "Two independent errors, combined the way independent errors combine.",
                            "hole": "?",
                            "opts": ["38.67", "27.35", "13.67", "19.34"],
                            "a": 1,
                            "why": r"$\sqrt{19.34^2 + 19.34^2} = 19.34\sqrt2 = 27.35$ mV. Two equal contributions always give exactly $\sqrt2$ times one of them, so the saving over the worst case is 29% — real, but small enough that it only becomes worth arguing about when there are many terms: ten equal ones give a factor of $\sqrt{10} = 3.16$.",
                            "whys": [
                                r"That is the worst case, on the line above. Quadrature is always the smaller of the two.",
                                r"$\sqrt{19.34^2 + 19.34^2} = 19.34\sqrt2 = 27.35$ mV. Two equal contributions always give exactly $\sqrt2$ times one of them, so the saving over the worst case is 29% — real, but small enough that it only becomes worth arguing about when there are many terms: ten equal ones give a factor of $\sqrt{10} = 3.16$.",
                                r"This is $19.34/\sqrt2$: the root two went underneath instead of on top. Combining two error sources can never give less than either one of them alone.",
                                r"That is one contribution unchanged, which would be the answer only if the other source did not exist.",
                            ],
                        },
                        {
                            "prompt": "Both resistors 1% HIGH, so the two terms keep their own signs.",
                            "hole": "?",
                            "opts": ["38.67", "19.34", "0.00", "-19.34"],
                            "a": 2,
                            "why": r"The sensitivities are $-87.89$ and $+193.36$ µV/Ω, so the two terms are $-19.34$ mV and $+19.34$ mV and they cancel exactly. Check it without any calculus: $9 \times 10100/(22220+10100) = 90900/32320 = 2.8125$ V, the nominal value to every digit. Only the *ratio* does any work, and multiplying both resistors by 1.01 leaves the ratio alone. The current does not get off so lightly — it is $V_{in}/(R_1+R_2)$, and it falls by very nearly the full 1%.",
                            "whys": [
                                r"That is the worst case, which assumes the errors are in *opposite* directions. Here they are both high, which is the case that cancels.",
                                r"Neither term survives alone. They are equal in size and opposite in sign, so they annihilate rather than leaving one behind.",
                                r"The sensitivities are $-87.89$ and $+193.36$ µV/Ω, so the two terms are $-19.34$ mV and $+19.34$ mV and they cancel exactly. Check it without any calculus: $9 \times 10100/(22220+10100) = 90900/32320 = 2.8125$ V, the nominal value to every digit. Only the *ratio* does any work, and multiplying both resistors by 1.01 leaves the ratio alone. The current does not get off so lightly — it is $V_{in}/(R_1+R_2)$, and it falls by very nearly the full 1%.",
                                r"The sign would have to come from somewhere. The two terms are $-19.34$ and $+19.34$ mV; there is no third term left over to make the total negative.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "What one ohm is worth",
                    "minutes": 5,
                    "brief": r'''
One sensitivity, one rule, and nothing else. The output of an unloaded divider is

$$V_{out} = V_{in}\frac{R_2}{R_1+R_2}$$

and $R_2$ appears twice in it — on the top, and inside the bottom. Differentiating with
respect to $R_2$ while $V_{in}$ and $R_1$ stand still therefore needs the quotient rule,
not just the reciprocal of the denominator.

Read the three values off the schematic. The answer is a rate, and its units are volts
per ohm, asked for here in microvolts per ohm because that is the size a real divider
comes out at.
''',
                    "prompt": r"What is $\partial V_{out}/\partial R_2$ for this divider?",
                    "note": "Answer in microvolts per ohm, to one decimal place. The answer is a slope, not a voltage.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 15000},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 5000},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "10.0 V"},
                        {"label": "R1 (supply to the probed node)", "value": "15.0 kΩ"},
                        {"label": "R2 (probed node to ground)", "value": "5.00 kΩ"},
                        {"label": "Asked for", "value": "µV per ohm"},
                    ],
                    # The closed form is checked against the solver's own operating point before it
                    # is differentiated, so a rewired schematic cannot quietly keep the old answer.
                    "check": r'''
const p = {};
c.net.parts.forEach(function (x) { p[x.id] = x.value; });
c.close(p.v1 * p.r2 / (p.r1 + p.r2), c.vout(), 1e-9,
        'the closed form must describe the circuit as drawn');
return 1e6 * p.v1 * p.r1 / Math.pow(p.r1 + p.r2, 2);
''',
                    "answer": 375.0,
                    "tol": 2.0,
                    "unit": "µV/Ω",
                    "aside": "A microvolt per ohm is a millivolt per kilohm — the same number, and often the easier way to picture it.",
                    "hint": r"Quotient rule on $R_2/(R_1+R_2)$: the top differentiates to 1 and the bottom to 1, leaving $R_1/(R_1+R_2)^2$. Multiply by $V_{in}$, and remember the denominator is squared.",
                    "wrong": r"If you got 500.0, the bottom was treated as a constant: that is $V_{in}/(R_1+R_2) = 10/20000$. Check what it claims — a fixed 500 µV/Ω would have the output passing 10 V and climbing, when a divider can never reach its own supply. If you got 125.0, that is the magnitude of the *other* partial, $\partial V_{out}/\partial R_1$, which carries $R_2$ on the top instead of $R_1$.",
                    "why": r'''
```
Vout      = 10 * 5000 / 20000                    = 2.5000 V

dVout/dR2 = Vin * R1 / (R1 + R2)^2
          = 10 * 15000 / 20000^2
          = 150000 / 4.000e8  = 3.750e-4 V/ohm   = 375.0 uV/ohm
```

Test it. $R_2$ is a 1% part, so it may be 50 Ω high, and the prediction is
$375.0 \times 50 = 18.75$ mV. Exactly:
$10 \times 5050/20050 = 2.518703$ V, a shift of 18.703 mV. The tangent line is high by
47 µV, or 0.25% of the shift — and that 0.25% is precisely
$\Delta R_2/(R_1+R_2) = 50/20000$, because the exact answer carries the enlarged sum in
its denominator and the linear one does not.

For the record the other partial is $-V_{in}R_2/(R_1+R_2)^2 = -125.0$ µV/Ω. Raising the
top resistor lowers the output, and it does so three times less strongly here, because
the two sensitivities are in the ratio $R_1 : R_2$.
''',
                },
                {
                    "title": "What a pair of 1% resistors costs at the output",
                    "minutes": 7,
                    "brief": r'''
Both resistors are 1% parts, so each may be anywhere in a band around its marked value.
The worst case adds the magnitudes of the two contributions, on the assumption that both
parts are off in whichever direction pushes the output the same way:

$$|\Delta V_{out}|_{\max} = \left|\frac{\partial V_{out}}{\partial R_1}\right|\delta_1
                          + \left|\frac{\partial V_{out}}{\partial R_2}\right|\delta_2$$

Each $\delta$ is 1% of that resistor's own nominal value, so the two are different
numbers of ohms. Work out both sensitivities, multiply each by its own tolerance, and
add the sizes.
''',
                    "prompt": r"In the worst case, how far can the output be from its nominal 2.8125 V?",
                    "note": "Answer in millivolts, to two decimal places. Give the size of the deviation, not a voltage.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 22000},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 10000},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "9.00 V"},
                        {"label": "R1 (supply to the probed node)", "value": "22.0 kΩ, ±1%"},
                        {"label": "R2 (probed node to ground)", "value": "10.0 kΩ, ±1%"},
                        {"label": "Asked for", "value": "the worst-case deviation, in mV"},
                    ],
                    # Both sensitivities are differentiated from the closed form, and the closed form
                    # is pinned to the solver's own operating point first. The two tolerances are
                    # 1% of whatever the schematic says each resistor is.
                    "check": r'''
const p = {};
c.net.parts.forEach(function (x) { p[x.id] = x.value; });
const S = p.r1 + p.r2;
c.close(p.v1 * p.r2 / S, c.vout(), 1e-9,
        'the closed form must describe the circuit as drawn');
const s1 = -p.v1 * p.r2 / (S * S);
const s2 = p.v1 * p.r1 / (S * S);
return 1000 * (Math.abs(s1) * 0.01 * p.r1 + Math.abs(s2) * 0.01 * p.r2);
''',
                    "answer": 38.67,
                    "tol": 0.2,
                    "unit": "mV",
                    "aside": "One percent of 22.0 kΩ is 220 Ω and one percent of 10.0 kΩ is 100 Ω — the same percentage, and not the same number of ohms.",
                    "hint": r"$\partial V_{out}/\partial R_1 = -V_{in}R_2/(R_1+R_2)^2$ and $\partial V_{out}/\partial R_2 = +V_{in}R_1/(R_1+R_2)^2$, with $(R_1+R_2)^2 = 1.024\times10^9$. Take the size of each, multiply by that resistor's own 1%, and add.",
                    "wrong": r"If you got 27.35, the two contributions were added in quadrature — the right answer to a different question, and always the smaller one. If you got 19.34, only one of the two resistors was counted; the other happens to contribute exactly the same, so half the budget is missing. If you got 0, the two terms were added with their signs while both parts moved the same way, which is the special case the derivation in this module is about, not the worst case.",
                    "why": r'''
```
S  = 32.0 k                Vout = 9 * 10000 / 32000 = 2.8125 V

s1 = -9 * 10000 / 32000^2  = -8.7891e-5 V/ohm = -87.89 uV/ohm
s2 = +9 * 22000 / 32000^2  = +1.9336e-4 V/ohm = +193.36 uV/ohm

|s1| * 220 = 19.336 mV
|s2| * 100 = 19.336 mV
             ----------
worst case    38.672 mV      = 1.375% of 2.8125 V
```

The two contributions are exactly equal, and that is structural: both come out as
$V_{in}R_1R_2/(R_1+R_2)^2$ divided by 100. Any divider built from two parts of the same
percentage tolerance splits its error budget precisely in half, whatever the ratio of
the resistors — the larger sensitivity always meets the smaller tolerance.

Against the exact endpoints: $R_1$ high and $R_2$ low gives
$9 \times 9900/32120 = 2.77397$ V, and $R_1$ low with $R_2$ high gives
$9 \times 10100/31880 = 2.85132$ V. That is $-38.53$ mV and $+38.82$ mV, so the true
interval is slightly lopsided and the linear figure sits between the two ends. Curvature
is what makes it lopsided, and at 1% it is worth 0.3 mV.
''',
                },
                {
                    "title": "The same two resistors, and a quantity that does not cancel",
                    "minutes": 7,
                    "brief": r'''
Identical circuit, identical parts, different question. The current the divider draws
from the rail is

$$I = \frac{V_{in}}{R_1 + R_2}$$

and both resistors now sit in the same place in the expression, so both partial
derivatives have the *same* sign. Nothing cancels here. Find both, multiply each by its
own 1%, and add the magnitudes.
''',
                    "prompt": r"In the worst case, how far can the current drawn from the rail be from its nominal value?",
                    "note": "Answer in microamps, to two decimal places. Give the size of the deviation, not the current itself.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 22000},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 10000},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "9.00 V"},
                        {"label": "R1", "value": "22.0 kΩ, ±1%"},
                        {"label": "R2", "value": "10.0 kΩ, ±1%"},
                        {"label": "Nominal current", "value": "281.25 µA"},
                        {"label": "Asked for", "value": "the worst-case deviation, in µA"},
                    ],
                    # The nominal current is taken from the solver's own source current before the
                    # closed form is trusted to differentiate.
                    "check": r'''
const p = {};
c.net.parts.forEach(function (x) { p[x.id] = x.value; });
const S = p.r1 + p.r2;
c.close(p.v1 / S, Math.abs(c.dc().currents.v1), 1e-9,
        'the closed form must give the current the solver measures');
const s = -p.v1 / (S * S);
return 1e6 * (Math.abs(s) * 0.01 * p.r1 + Math.abs(s) * 0.01 * p.r2);
''',
                    "answer": 2.81,
                    "tol": 0.03,
                    "unit": "µA",
                    "aside": "Both resistors have the same sensitivity here, because the current sees only their sum — but they do not have the same tolerance in ohms.",
                    "hint": r"$\partial I/\partial R_1 = \partial I/\partial R_2 = -V_{in}/(R_1+R_2)^2$, the same number for both. The two tolerances differ: 220 Ω and 100 Ω.",
                    "wrong": r"If you got 0, the cancellation from the output-voltage question was carried over — but that cancellation came from the two sensitivities having opposite signs, and here they have the same sign. If you got 1.93, only $R_1$ was counted; if you got 0.88, only $R_2$.",
                    "why": r'''
```
I  = 9 / 32000                                = 281.25 uA

dI/dR1 = dI/dR2 = -Vin / (R1+R2)^2
                = -9 / 1.024e9  = -8.7891e-9 A/ohm

|dI/dR1| * 220 = 1.9336 uA
|dI/dR2| * 100 = 0.8789 uA
                 ---------
worst case        2.8125 uA
```

That is exactly 1% of 281.25 µA, and it has to be: $I$ depends on the two resistors only
through their sum, and 1% of $R_1$ plus 1% of $R_2$ is 1% of $R_1+R_2$. Both parts 1%
high together gives $9/32320 = 278.47$ µA, a fall of 2.78 µA — the full worst case
almost exactly, where the same common error left the output voltage completely
untouched.

That is the point of asking the two questions about one circuit. Matching does not make
a divider immune to its tolerances; it makes the *ratio* immune, and the impedance level
is left carrying all of it. Voltage is safe, current is not.
''',
                },
                {
                    "title": "How far a corner frequency can wander",
                    "minutes": 9,
                    "brief": r'''
The corner of an RC low-pass is $f_c = 1/(2\pi RC)$ — nothing but a product of powers,
so take logarithms rather than derivatives:

$$\ln f_c = -\ln 2\pi - \ln R - \ln C \quad\Longrightarrow\quad
\frac{\Delta f_c}{f_c} = -\frac{\Delta R}{R} - \frac{\Delta C}{C}$$

Both relative sensitivities are $-1$. The resistor is a 1% part and the capacitor a 10%
part, which is the usual pairing: film capacitors are much looser than film resistors.

This question asks for the two combined **in quadrature**, not the worst case — the two
errors are independent, so their variances add and the deviations do not.
''',
                    "prompt": r"Combining the two tolerances in quadrature, what is the standard spread of the corner frequency?",
                    "note": "Answer in hertz, to one decimal place. Quadrature, not worst case.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "R", "value": "4.70 kΩ, ±1%"},
                        {"label": "C", "value": "100 nF, ±10%"},
                        {"label": "Nominal corner", "value": "338.63 Hz"},
                        {"label": "Asked for", "value": "the quadrature spread, in Hz"},
                    ],
                    # The corner is measured off the drawn circuit by bisecting its own response,
                    # then compared with 1/(2 pi R C) before the tolerances are applied to it.
                    "check": r'''
const p = {};
c.net.parts.forEach(function (x) { p[x.id] = x.value; });
const fc = 1 / (2 * Math.PI * p.r1 * p.c1);
c.close(c.corner(1, 1e6), fc, 1e-4,
        'the drawn RC must have the corner the algebra predicts');
return Math.sqrt(0.01 * 0.01 + 0.10 * 0.10) * fc;
''',
                    "answer": 34.03,
                    "tol": 0.3,
                    "unit": "Hz",
                    "aside": "The two tolerances are on parts measured in different units entirely, which is exactly why the calculation is done in percentages.",
                    "hint": r"Get the fractional spread first — $\sqrt{0.01^2 + 0.10^2}$ — and only then multiply by the nominal 338.63 Hz. Both relative sensitivities are 1 in size, so the tolerances go in unweighted.",
                    "wrong": r"If you got 37.25, that is the worst case, $0.11 \times 338.63$, which assumes both parts are off the same way at full tolerance. If you got 33.86, only the capacitor was counted — which is very nearly right, and that is the finding, not the error. If you got 3.39, only the resistor was counted.",
                    "why": r'''
```
fc   = 1 / (2 pi * 4700 * 100e-9) = 1 / 2.95310e-3     = 338.63 Hz

quadrature fraction = sqrt(0.01^2 + 0.10^2)
                    = sqrt(0.0001 + 0.0100)
                    = sqrt(0.0101) = 0.100499

spread = 0.100499 * 338.63                             = 34.03 Hz
```

Now look at what the resistor bought. On its own the capacitor gives 10.0000%; adding
the resistor takes the total to 10.0499%. Replacing the 1% resistor with a 0.1% part
would take it to 10.0005%. When one contribution dominates, buying the others down is
money set on fire, and quadrature is the calculation that says so — the worst-case
figure of 11% never will, because in a sum of magnitudes every term looks like it is
pulling its weight.

Where this starts to creak: 10% is not a small perturbation. The exact endpoints are
$1/(0.99 \times 0.90) = 1.1223$, or $+41.43$ Hz, and
$1/(1.01 \times 1.10) = 0.9001$, or $-33.83$ Hz. The true interval is visibly
asymmetric and reaches 11% further up than the linear worst case predicted, because
$1/x$ curves upwards. At 1% tolerances that effect is invisible; at 10% it is the
difference between passing and failing a limit written at the edge.
''',
                },
                {
                    "title": "The power in a resistor that appears twice",
                    "minutes": 12,
                    "brief": r'''
The power dissipated in the lower resistor of an unloaded divider is $V_{out}^2/R_2$,
and substituting the divider formula gives

$$P_2 = \frac{V_{in}^2R_2}{(R_1+R_2)^2}$$

Look at where $R_2$ appears: on the top, where raising it raises the power, and inside
the squared bottom, where raising it lowers the power. The two effects partly cancel,
and getting the size of that cancellation right is the whole of this question.

Take logarithms, because $P_2$ is a product of powers:

$$\ln P_2 = 2\ln V_{in} + \ln R_2 - 2\ln(R_1+R_2)$$

Differentiating a logarithm gives the *fractional* change directly, which is what a
tolerance is quoted in. Both resistors are 1% parts; the supply is exact.
''',
                    "prompt": r"In the worst case, by what percentage can the power dissipated in $R_2$ differ from its nominal value?",
                    "note": "Answer as a percentage, to two decimal places. Both resistors are 1% parts and the 12 V rail is exact.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 10000},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 5000},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "o1", "kind": "OUT", "x": 9, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "12.0 V, exact"},
                        {"label": "R1", "value": "10.0 kΩ, ±1%"},
                        {"label": "R2", "value": "5.00 kΩ, ±1%"},
                        {"label": "Nominal power in R2", "value": "3.20 mW"},
                        {"label": "Asked for", "value": "the worst-case deviation, as a %"},
                    ],
                    # The power is measured from the solver's own node voltages and pinned to the
                    # closed form before that closed form is differentiated logarithmically.
                    "check": r'''
const p = {};
c.net.parts.forEach(function (x) { p[x.id] = x.value; });
const S = p.r1 + p.r2;
const d = c.dc();
const r2 = c.net.parts.filter(function (x) { return x.id === 'r2'; })[0];
const drop = d.v[r2.n1] - d.v[r2.n2];
c.close(drop * drop / r2.value, p.v1 * p.v1 * p.r2 / (S * S), 1e-9,
        'the measured power must match the closed form being differentiated');
const f1 = -2 / S;
const f2 = 1 / p.r2 - 2 / S;
return 100 * (Math.abs(f1) * 0.01 * p.r1 + Math.abs(f2) * 0.01 * p.r2);
''',
                    "answer": 1.67,
                    "tol": 0.03,
                    "unit": "%",
                    "aside": "The nominal power is $4.00^2/5000 = 3.20$ mW, so a percent of it is 32 µW — small in absolute terms, and the question is about the percentage.",
                    "hint": r"$\frac{1}{P}\frac{\partial P}{\partial R_1} = -\frac{2}{R_1+R_2}$, and $\frac{1}{P}\frac{\partial P}{\partial R_2} = \frac{1}{R_2} - \frac{2}{R_1+R_2}$. Multiply each by that resistor's own 1% in ohms — 100 Ω and 50 Ω — and add the magnitudes.",
                    "wrong": r"If you got 2.00, the $R_2$ term was taken as $-2/(R_1+R_2)$ alone: $R_2$ was differentiated in the denominator but not on the numerator, so the partial cancellation was missed. If you got 1.33, only $R_1$ was counted. If you got 1.00, the two terms were subtracted rather than having their magnitudes added — which is the *best* case, not the worst. If you got 1.37, that is the quadrature figure.",
                    "why": r'''
```
S = 15.0 k        Vout = 12 * 5000/15000 = 4.00 V        P2 = 16.0/5000 = 3.20 mW

(1/P) dP/dR1 = -2 / S            = -2/15000     = -1.3333e-4 per ohm
(1/P) dP/dR2 = 1/R2 - 2/S        = 2.0000e-4 - 1.3333e-4
                                                = +6.6667e-5 per ohm

R1 term: 1.3333e-4 * 100 ohm  = 1.3333e-2  = 1.3333%
R2 term: 6.6667e-5 *  50 ohm  = 3.3333e-3  = 0.3333%
                                 ----------------------
worst case                                     1.6667%
```

The two terms are a factor of four apart, and the reason is the cancellation. Written
out, $1/R_2 = 2\times10^{-4}$ pulls the power up and $-2/(R_1+R_2) = -1.333\times10^{-4}$
pushes it down, leaving only a third of the larger effect. A one percent error in the
lower resistor is worth a third of a percent in its own dissipation. A one percent error
in the *upper* resistor, which does nothing but throttle the current, is worth four times
as much.

Two checks. The exact endpoints: $R_1$ 1% low with $R_2$ 1% high gives
$144 \times 5050/14950^2 = 3.2537$ mW, up 1.677%, and the opposite corner gives
3.1470 mW, down 1.657%. The linear 1.667% sits between them, as it should.

And the common-mode case again, for contrast: both resistors 1% high leaves the *ratio*
alone, so $V_{out}$ is unchanged at 4.00 V — but the power is $V_{out}^2/R_2$ with a
larger $R_2$, so it falls by 1/1.01, which is 0.990%. The output voltage survives a
common error and the dissipation does not, for the same reason the supply current does
not: only the ratio is protected, never the impedance level.
''',
                },
            ],
            "derive": {
                "title": "Why a divider does not care about a common error",
                "minutes": 12,
                "vars": ["V_in", "V_out", "R_1", "R_2"],
                "brief": r'''
A divider is built from two resistors that are each allowed to be a percent or so
away from their marked value. This derivation works out what that costs — and finds
that half of it costs nothing at all.

Take the divider unloaded, so that the same current flows through both resistors.
''',
                "steps": [
                    {
                        "prompt": r"Write $V_{out}$ in terms of $V_{in}$, $R_1$ and $R_2$, with $R_2$ the resistor the output is measured across.",
                        "answer": r"V_in R_2/(R_1 + R_2)",
                        "hint": r"The current through the pair is $V_{in}/(R_1+R_2)$, and $V_{out}$ is that current through $R_2$.",
                        "deconstruct": [
                            r"$I = V_{in}/(R_1+R_2)$.",
                            r"$V_{out} = IR_2$.",
                        ],
                    },
                    {
                        "prompt": r"Differentiate with respect to $R_2$, holding $R_1$ and $V_{in}$ fixed. Write $\partial V_{out}/\partial R_2$.",
                        "answer": r"V_in R_1/(R_1 + R_2)^2",
                        "placeholder": r"something over the sum, squared",
                        "hint": r"Quotient rule on $R_2/(R_1+R_2)$: top differentiates to 1, bottom differentiates to 1.",
                        "deconstruct": [
                            r"$\frac{d}{dR_2}\frac{R_2}{R_1+R_2} = \frac{(R_1+R_2)\cdot 1 - R_2 \cdot 1}{(R_1+R_2)^2}$.",
                            r"The top simplifies to $R_1$.",
                        ],
                    },
                    {
                        "prompt": r"Now differentiate with respect to $R_1$ instead, holding $R_2$ and $V_{in}$ fixed. Write $\partial V_{out}/\partial R_1$.",
                        "answer": r"-V_in R_2/(R_1 + R_2)^2",
                        "hint": r"Only the bottom depends on $R_1$ now, so it is the chain rule on $(R_1+R_2)^{-1}$ — and the sign comes out negative.",
                        "deconstruct": [
                            r"$V_{out} = V_{in}R_2(R_1+R_2)^{-1}$ with $R_2$ constant.",
                            r"Differentiating gives $-V_{in}R_2(R_1+R_2)^{-2}$.",
                        ],
                    },
                    {
                        "prompt": r"Both resistors are 1% high, so $\Delta R_1 = R_1/100$ and $\Delta R_2 = R_2/100$. Substitute into $\Delta V_{out} = \frac{\partial V_{out}}{\partial R_1}\Delta R_1 + \frac{\partial V_{out}}{\partial R_2}\Delta R_2$ and write the result.",
                        "answer": r"0",
                        "hint": r"Write both terms out over the common bottom $(R_1+R_2)^2$ and compare their tops.",
                        "deconstruct": [
                            r"The first term is $-\frac{V_{in}R_2}{(R_1+R_2)^2}\cdot\frac{R_1}{100}$.",
                            r"The second is $+\frac{V_{in}R_1}{(R_1+R_2)^2}\cdot\frac{R_2}{100}$.",
                            r"They contain the same product $V_{in}R_1R_2/100$ and carry opposite signs.",
                        ],
                    },
                ],
                "closing": r'''
Exactly zero, to first order, for any pair of resistors and any common percentage.
Only the *mismatch* between the two errors reaches the output — which is why resistors
made side by side on the same chip, from the same film, at the same temperature, give
a divider far better than either resistor's absolute accuracy would suggest.

The current is not so lucky: it is $V_{in}/(R_1+R_2)$, both errors push it the same
way, and 1% high on both parts is 1% low on the current.
''',
            },
            "lab": {
                "title": "Worst case, quadrature, and a simulation to settle it",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Two formulas and one experiment that decides between them.

`partial(f, xs, i, h)` estimates $\partial f/\partial x_i$ at the point `xs` by a
central difference, taking the step *relative* to the size of the variable —
`step = h * max(1.0, abs(xs[i]))` — because a fixed step of $10^{-6}$ stops working
once the variable itself is large. The test that catches this differentiates
$\sqrt{x}$ at $x = 10^{6}$: a fixed $10^{-6}$ puts the two evaluations at
1000.0000000005 and 999.9999999995, which agree to twelve significant figures, so the
difference that survives the subtraction is good to only about five, and the slope
comes back as $4.99995\times10^{-4}$ against the exact $5\times10^{-4}$ — outside the
$10^{-9}$ the test allows. Scaling the step makes it 1.0 there, and the same
subtraction returns the slope right to ten figures.

The divider in `__main__` is nowhere near that regime, so do not expect the change to
show there: at 12.8 kΩ even a fixed $10^{-6}$ gives $-9.0000007\times10^{-5}$
against the exact $-9\times10^{-5}$. The relative step costs nothing on a point like
that and is what keeps the same routine usable on the large ones.

Read the floor of 1.0 carefully: it only ever scales the step *up*, never down. A
variable much smaller than 1 — a capacitance of 1 µF, written in farads — still gets
the bare $10^{-6}$, which is the whole of its own value; for a point like that you
must rescale the variable (work in µF) or lower `h` yourself.

`worst_case(f, xs, deltas)` returns $\sum |\partial f/\partial x_i|\,\delta_i$.

`rss(f, xs, deltas)` returns $\sqrt{\sum (\partial f/\partial x_i\,\delta_i)^2}$.

`spread(f, xs, sigmas, n, seed)` settles the argument by experiment: draw `n` samples
in which each variable is displaced by `random.Random(seed).gauss(0, sigma)`, evaluate
`f` at each, and return the **sample standard deviation** of the results — the one
with $n-1$ on the bottom. If the quadrature formula is right, `spread` should land on
top of `rss` for independent gaussian errors, and well below `worst_case`.

`f` takes a single list of values, so a divider is written
`lambda xs: 5.0 * xs[1] / (xs[0] + xs[1])`.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def partial(f, xs, i, h=1e-6):
    """Central-difference estimate of df/dx_i at xs, with a relative step."""
    # TODO: step = h * max(1.0, abs(xs[i])), then (f(up) - f(down)) / (2 * step)
    return 0.0


def worst_case(f, xs, deltas):
    """Sum of |partial| * delta over every variable."""
    # TODO
    return 0.0


def rss(f, xs, deltas):
    """Root of the sum of the squares of partial * delta."""
    # TODO
    return 0.0


def spread(f, xs, sigmas, n, seed):
    """Sample standard deviation of f over n gaussian draws about xs."""
    # TODO: one random.Random(seed), then n samples, then mean and sd with n-1.
    return 0.0


if __name__ == "__main__":
    divider = lambda xs: 5.0 * xs[1] / (xs[0] + xs[1])
    point = [12800.0, 7200.0]
    tol = [128.0, 72.0]              # 1% of each
    print("nominal    :", divider(point), "V")
    print("d/dR1      :", partial(divider, point, 0))
    print("d/dR2      :", partial(divider, point, 1))
    print("worst case :", worst_case(divider, point, tol), "V")
    print("quadrature :", rss(divider, point, tol), "V")
    print("simulated  :", spread(divider, point, tol, 20000, 12345), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def partial(f, xs, i, h=1e-6):
    """Central-difference estimate of df/dx_i at xs, with a relative step."""
    step = h * max(1.0, abs(xs[i]))
    up = list(xs)
    down = list(xs)
    up[i] += step
    down[i] -= step
    return (f(up) - f(down)) / (2.0 * step)


def worst_case(f, xs, deltas):
    """Sum of |partial| * delta over every variable."""
    return sum(abs(partial(f, xs, i)) * deltas[i] for i in range(len(xs)))


def rss(f, xs, deltas):
    """Root of the sum of the squares of partial * delta."""
    total = 0.0
    for i in range(len(xs)):
        term = partial(f, xs, i) * deltas[i]
        total += term * term
    return math.sqrt(total)


def spread(f, xs, sigmas, n, seed):
    """Sample standard deviation of f over n gaussian draws about xs."""
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        pt = [xs[i] + (rng.gauss(0.0, sigmas[i]) if sigmas[i] else 0.0)
              for i in range(len(xs))]
        vals.append(f(pt))
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)
    return math.sqrt(var)


if __name__ == "__main__":
    divider = lambda xs: 5.0 * xs[1] / (xs[0] + xs[1])
    point = [12800.0, 7200.0]
    tol = [128.0, 72.0]              # 1% of each
    print("nominal    :", divider(point), "V")
    print("d/dR1      :", partial(divider, point, 0))
    print("d/dR2      :", partial(divider, point, 1))
    print("worst case :", worst_case(divider, point, tol), "V")
    print("quadrature :", rss(divider, point, tol), "V")
    print("simulated  :", spread(divider, point, tol, 20000, 12345), "V")
'''}],
                "hints": [
                    r"Copy the point before moving it: `up = list(xs)` and then `up[i] += step`. Mutating `xs` itself leaves the caller's point displaced and every later partial derivative wrong.",
                    r"The denominator of a central difference is `2 * step`, not `step`. Getting that wrong doubles every sensitivity and every answer downstream of it.",
                    r"`worst_case` needs the absolute value and `rss` does not, because squaring removes the sign for you. That difference is the whole distinction between the two formulas.",
                    r"Make one `random.Random(seed)` outside the loop. A fresh generator inside it, seeded the same way each pass, produces the same sample `n` times and a standard deviation of zero.",
                ],
                "tests": [
                    {"name": "the partial derivatives match the algebra", "code": r'''
_div = lambda xs: 5.0 * xs[1] / (xs[0] + xs[1])
_pt = [12800.0, 7200.0]
_p0 = partial(_div, _pt, 0)
_p1 = partial(_div, _pt, 1)
assert abs(_p0 - (-9e-05)) < 1e-9, f"d/dR1 should be -V*R2/(R1+R2)^2 = -9e-05, got {_p0}"
assert abs(_p1 - 1.6e-04) < 1e-9, f"d/dR2 should be V*R1/(R1+R2)^2 = 1.6e-04, got {_p1}"
assert abs(_div(_pt) - 1.8) < 1e-12, "the point itself must not have been moved"
'''},
                    {"name": "the step keeps up with the size of the variable", "code": r'''
import math
_e = lambda xs: math.exp(xs[0])
assert abs(partial(_e, [0.0], 0) - 1.0) < 1e-6, \
    f"the exponential has slope 1 at the origin, got {partial(_e, [0.0], 0)}"
_root = lambda xs: xs[0] ** 0.5
_d = partial(_root, [1e6], 0)
assert abs(_d - 5e-4) < 1e-9, \
    f"d(sqrt(x))/dx at x=1e6 is 0.5/1000 = 5e-4, got {_d} — at this size a fixed tiny step is eaten by rounding"
'''},
                    {"name": "worst case and quadrature on the divider", "code": r'''
import math
_div = lambda xs: 5.0 * xs[1] / (xs[0] + xs[1])
_pt = [12800.0, 7200.0]
_tol = [128.0, 72.0]
_w = worst_case(_div, _pt, _tol)
_r = rss(_div, _pt, _tol)
assert abs(_w - 0.02304) < 1e-6, f"expected 23.04 mV worst case, got {_w * 1000} mV"
assert abs(_r - 0.016291744) < 1e-6, f"expected 16.29 mV in quadrature, got {_r * 1000} mV"
assert abs(_w / _r - math.sqrt(2.0)) < 1e-6, \
    "the two contributions here are equal, so the ratio must be exactly root two"
'''},
                    {"name": "a second circuit, checked by hand", "code": r'''
import math
_pwr = lambda xs: xs[0] ** 2 / xs[1]
_pt = [5.0, 1000.0]
_tol = [0.05, 10.0]
assert abs(worst_case(_pwr, _pt, _tol) - 7.5e-4) < 1e-9, \
    "dP/dV = 2V/R = 0.01 and dP/dR = -V^2/R^2 = -2.5e-5, so the worst case is 0.75 mW"
assert abs(rss(_pwr, _pt, _tol) - math.sqrt(2.5e-7 + 6.25e-8)) < 1e-9, \
    "in quadrature that is 0.559 mW"
'''},
                    {"name": "equal and opposite sensitivities cancel", "code": r'''
_div = lambda xs: 5.0 * xs[1] / (xs[0] + xs[1])
_pt = [12800.0, 7200.0]
_shift = partial(_div, _pt, 0) * 128.0 + partial(_div, _pt, 1) * 72.0
assert abs(_shift) < 1e-6, \
    f"both resistors 1% high should move the output by nothing, got {_shift}"
assert worst_case(_div, _pt, [128.0, 72.0]) > 0.02, \
    "but the worst case, which ignores the signs, must still be sizeable"
'''},
                    {"name": "the simulation lands on the quadrature figure", "code": r'''
_div = lambda xs: 5.0 * xs[1] / (xs[0] + xs[1])
_pt = [12800.0, 7200.0]
_tol = [128.0, 72.0]
_r = rss(_div, _pt, _tol)
_s = spread(_div, _pt, _tol, 20000, 12345)
assert abs(_s - _r) / _r < 0.08, \
    f"20000 gaussian draws gave a spread of {_s:.6f} against the formula's {_r:.6f}"
assert _s < worst_case(_div, _pt, _tol), "and it must sit well below the worst case"
'''},
                    {"name": "the simulation is reproducible and honest about zero", "code": r'''
_div = lambda xs: 5.0 * xs[1] / (xs[0] + xs[1])
_pt = [12800.0, 7200.0]
_a = spread(_div, _pt, [128.0, 72.0], 500, 7)
_b = spread(_div, _pt, [128.0, 72.0], 500, 7)
assert _a == _b, "the same seed must give the same answer"
_c = spread(_div, _pt, [128.0, 72.0], 500, 8)
assert _c != _a, "a different seed must give a different one"
assert spread(_div, _pt, [0.0, 0.0], 200, 1) == 0.0, "no uncertainty in, no spread out"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "One RC network, computed four ways",
        "runtime": "python",
        "minutes": 130,
        "brief": r'''
Everything in this course points at the same small circuit: a source, a resistor,
and a capacitor. You now know four different ways to say what it does, one from
each module, and they must all agree.

Build a single file that computes all four and checks them against each other.

## The circuit

A source $V_s$ drives a resistor $R$, which feeds a node; a capacitor $C$ takes that
node down to ground. The node is the output.

## The four descriptions

1. **As simultaneous equations.** At DC the capacitor passes nothing, so the circuit
   is resistive and a network of resistors becomes a matrix. Write a general solver
   `solve_nodes(G, b)` for an $n \times n$ system, by Gaussian elimination with
   partial pivoting — that is, at each column, swap the row with the largest entry
   into place before dividing, so you never divide by something tiny.

2. **As a complex number.** At a frequency $f$ the output is the input multiplied by
   $G(f) = 1/(1 + j2\pi fRC)$. Its modulus is the size of the output and its
   argument is the phase shift.

3. **As a differential equation, solved numerically.** $\frac{dv}{dt} = (V_s - v)/RC$
   stepped forward in small increments of `dt` from $v = 0$.

4. **As a differential equation, solved on paper.** $v(t) = V_s(1 - e^{-t/RC})$ —
   and confirmed with SymPy, by substituting it back into the equation and asking
   whether what is left over is zero.

## Suggested order

`solve_nodes` first, because it is the only one with any real bookkeeping in it, and
the checks for it do not depend on anything else. Then the two one-line functions in
the frequency domain. Then the two step responses, which is where the numbers have
to start agreeing with each other.

The last function, `satisfies_ode`, is where SymPy earns its place: it does the
differentiation symbolically, so you find out whether your closed form is right
rather than whether it happens to match at the points you sampled.
''',
        "deliverables": [
            "`solve_nodes(G, b)` — Gaussian elimination with partial pivoting on an n x n system, returning the list of node voltages, and raising `ValueError` on a singular matrix.",
            "`lowpass_gain(R, C, f)` and `corner_frequency(R, C)` — the complex gain at a frequency, and the frequency at which its modulus falls to $1/\\sqrt{2}$.",
            "`step_euler(vs, R, C, dt, steps)` — the differential equation stepped forward numerically from 0 V, returning `steps + 1` samples.",
            "`analytic_step(vs, R, C, t)` — the closed-form solution at a single time.",
            "`satisfies_ode(vs, R, C)` — substitute the closed form back into the differential equation with SymPy and return whether the remainder is exactly zero.",
        ],
        "constraints": [
            "The standard library, NumPy and SymPy only. No SciPy, and no circuit-simulation library.",
            "`solve_nodes` must work for any size of system, not just 2 x 2 — the checks use a three-node ladder as well as a two-node one.",
            "Use partial pivoting, not plain elimination: a zero in a pivot position must be swapped away rather than divided by.",
            "`step_euler` must start from 0 V and return a list of length `steps + 1`, so that sample `k` is the voltage at time `k * dt`.",
            "`satisfies_ode` must do the differentiation symbolically. Sampling the two sides at a few times and comparing is not the same claim.",
        ],
        "rubric": [
            {"criterion": "The linear solver", "weight": 30,
             "evidence": "solve_nodes returns the correct node voltages for both a two-node and a three-node resistive ladder, pivots rather than dividing by a zero, and raises ValueError when the matrix is singular."},
            {"criterion": "The frequency description", "weight": 25,
             "evidence": "lowpass_gain has modulus 1 at zero frequency and modulus 1/sqrt(2) with a phase of exactly -45 degrees at the frequency returned by corner_frequency."},
            {"criterion": "The two step responses agree", "weight": 25,
             "evidence": "step_euler starts at zero, has the right length, and tracks analytic_step to within a fraction of a percent once the step size is small; both settle at the supply voltage."},
            {"criterion": "The symbolic confirmation", "weight": 20,
             "evidence": "satisfies_ode returns True for several different values of vs, R and C, and gets there by differentiating the closed form symbolically and simplifying the remainder to zero, rather than by sampling both sides at a few times and comparing."},
        ],
        "hints": [
            "For `solve_nodes`, copy `G` into a working matrix with `b` appended as an extra column. Reduce that one array and the answers are left in the last column.",
            "Partial pivoting is one line: before dividing by `M[col][col]`, find the row at or below `col` whose entry in that column has the largest absolute value, and swap it up.",
            "`corner_frequency` is $1/(2\\pi RC)$. Do not compute it by searching the response — you know it in closed form.",
            "For `step_euler`, one step is `v = v + dt * (vs - v) / (R * C)`. Append after stepping, and put the initial `0.0` in before the loop starts.",
            "In `satisfies_ode`, build the symbol with `t = sympy.symbols('t', positive=True)`, form the expression, and test `sympy.simplify(sympy.diff(v, t) - (vs - v) / (R * C)) == 0`.",
        ],
        "files": [
            {"name": "main.py", "content": r'''
import math
import sympy as sp


def solve_nodes(G, b):
    """Solve G x = b by Gaussian elimination with partial pivoting.

    G is a list of n rows, each a list of n floats; b is a list of n floats.
    Return the list of n answers. Raise ValueError if G is singular.
    """
    # TODO
    return []


def lowpass_gain(R, C, f):
    """The complex gain 1 / (1 + j*2*pi*f*R*C)."""
    # TODO
    return 0j


def corner_frequency(R, C):
    """The frequency at which the modulus of the gain is 1/sqrt(2)."""
    # TODO
    return 0.0


def step_euler(vs, R, C, dt, steps):
    """Step dv/dt = (vs - v) / (R*C) forward from 0 V. Return steps + 1 samples."""
    # TODO
    return []


def analytic_step(vs, R, C, t):
    """The closed-form solution at time t, starting from 0 V."""
    # TODO
    return 0.0


def satisfies_ode(vs, R, C):
    """True if the closed form satisfies dv/dt = (vs - v)/(R*C), checked symbolically."""
    # TODO
    return False


if __name__ == "__main__":
    G = [[0.0015, -0.0005], [-0.0005, 0.0008333333333333334]]
    b = [0.009, 0.0]
    print("node voltages:", solve_nodes(G, b))
    R, C = 1000.0, 1e-6
    print("corner frequency:", round(corner_frequency(R, C), 3), "Hz")
    print("gain there:", lowpass_gain(R, C, corner_frequency(R, C)))
    tau = R * C
    ys = step_euler(5.0, R, C, tau / 2000.0, 6000)
    print("numerical at 3 tau:", round(ys[-1], 6))
    print("analytic  at 3 tau:", round(analytic_step(5.0, R, C, 3.0 * tau), 6))
    print("closed form satisfies the equation:", satisfies_ode(5.0, R, C))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import math
import sympy as sp


def solve_nodes(G, b):
    """Solve G x = b by Gaussian elimination with partial pivoting.

    G is a list of n rows, each a list of n floats; b is a list of n floats.
    Return the list of n answers. Raise ValueError if G is singular.
    """
    n = len(b)
    M = [list(G[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        piv = col
        for r in range(col + 1, n):
            if abs(M[r][col]) > abs(M[piv][col]):
                piv = r
        if abs(M[piv][col]) < 1e-15:
            raise ValueError("the network does not fix a single set of voltages")
        M[col], M[piv] = M[piv], M[col]
        d = M[col][col]
        for cc in range(col, n + 1):
            M[col][cc] /= d
        for r in range(n):
            if r == col:
                continue
            f = M[r][col]
            if f == 0.0:
                continue
            for cc in range(col, n + 1):
                M[r][cc] -= f * M[col][cc]
    return [M[i][n] for i in range(n)]


def lowpass_gain(R, C, f):
    """The complex gain 1 / (1 + j*2*pi*f*R*C)."""
    return 1.0 / (1.0 + 1j * 2.0 * math.pi * f * R * C)


def corner_frequency(R, C):
    """The frequency at which the modulus of the gain is 1/sqrt(2)."""
    return 1.0 / (2.0 * math.pi * R * C)


def step_euler(vs, R, C, dt, steps):
    """Step dv/dt = (vs - v) / (R*C) forward from 0 V. Return steps + 1 samples."""
    tau = R * C
    v = 0.0
    out = [0.0]
    for _ in range(steps):
        v = v + dt * (vs - v) / tau
        out.append(v)
    return out


def analytic_step(vs, R, C, t):
    """The closed-form solution at time t, starting from 0 V."""
    return vs * (1.0 - math.exp(-t / (R * C)))


def satisfies_ode(vs, R, C):
    """True if the closed form satisfies dv/dt = (vs - v)/(R*C), checked symbolically."""
    t = sp.symbols("t", positive=True)
    v = vs * (1 - sp.exp(-t / (R * C)))
    remainder = sp.simplify(sp.diff(v, t) - (vs - v) / (R * C))
    return remainder == 0


if __name__ == "__main__":
    G = [[0.0015, -0.0005], [-0.0005, 0.0008333333333333334]]
    b = [0.009, 0.0]
    print("node voltages:", solve_nodes(G, b))
    R, C = 1000.0, 1e-6
    print("corner frequency:", round(corner_frequency(R, C), 3), "Hz")
    print("gain there:", lowpass_gain(R, C, corner_frequency(R, C)))
    tau = R * C
    ys = step_euler(5.0, R, C, tau / 2000.0, 6000)
    print("numerical at 3 tau:", round(ys[-1], 6))
    print("analytic  at 3 tau:", round(analytic_step(5.0, R, C, 3.0 * tau), 6))
    print("closed form satisfies the equation:", satisfies_ode(5.0, R, C))
'''},
        ],
        "tests": [
            {"name": "a two-node ladder solves correctly", "code": r'''
_G = [[0.0015, -0.0005], [-0.0005, 1.0 / 2000.0 + 1.0 / 3000.0]]
_b = [0.009, 0.0]
_v = solve_nodes(_G, _b)
assert len(_v) == 2, f"expected 2 node voltages, got {len(_v)}"
assert abs(_v[0] - 7.5) < 1e-9, f"node 1 should be 7.5 V, got {_v[0]}"
assert abs(_v[1] - 4.5) < 1e-9, f"node 2 should be 4.5 V, got {_v[1]}"
'''},
            {"name": "a three-node ladder solves correctly", "code": r'''
_g = 1.0 / 1000.0
_G = [[2 * _g, -_g, 0.0], [-_g, 2 * _g, -_g], [0.0, -_g, 2 * _g]]
_b = [4.0 * _g, 0.0, 0.0]
_v = solve_nodes(_G, _b)
for _k, _want in enumerate([3.0, 2.0, 1.0]):
    assert abs(_v[_k] - _want) < 1e-9, f"node {_k + 1} should be {_want} V, got {_v[_k]}"
'''},
            {"name": "pivoting handles a zero in the way", "code": r'''
_G = [[0.0, 2.0], [1.0, 1.0]]
_b = [4.0, 3.0]
_v = solve_nodes(_G, _b)
assert abs(_v[0] - 1.0) < 1e-9 and abs(_v[1] - 2.0) < 1e-9, \
    f"expected (1, 2), got {_v} — the first pivot is zero and must be swapped away"
'''},
            {"name": "a singular matrix is refused", "code": r'''
try:
    solve_nodes([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0])
except ValueError:
    pass
else:
    raise AssertionError("the second row is twice the first, so ValueError was expected")
'''},
            {"name": "the gain is right at zero frequency and at the corner", "code": r'''
import math
_R, _C = 1000.0, 1e-6
assert abs(lowpass_gain(_R, _C, 0.0) - 1.0) < 1e-12, "at DC the filter passes everything"
_fc = corner_frequency(_R, _C)
assert abs(_fc - 159.15494309189535) < 1e-6, f"expected about 159.15 Hz, got {_fc}"
_g = lowpass_gain(_R, _C, _fc)
assert abs(abs(_g) - 0.7071067811865475) < 1e-9, f"the modulus should be 1/sqrt(2), got {abs(_g)}"
assert abs(math.degrees(math.atan2(_g.imag, _g.real)) - (-45.0)) < 1e-9, \
    "the phase at the corner should be exactly -45 degrees"
'''},
            {"name": "the numerical and analytic step responses agree", "code": r'''
_R, _C, _vs = 1000.0, 1e-6, 5.0
_tau = _R * _C
_dt = _tau / 2000.0
_ys = step_euler(_vs, _R, _C, _dt, 6000)
assert len(_ys) == 6001, f"expected 6001 samples, got {len(_ys)}"
assert abs(_ys[0]) < 1e-15, f"it must start from 0 V, got {_ys[0]}"
_want = analytic_step(_vs, _R, _C, 3.0 * _tau)
assert abs(_want - 4.751064658160680) < 1e-9, \
    f"the closed form at 3 tau should be 4.7510647, got {_want}"
assert abs(_ys[-1] - _want) < 1e-3, \
    f"numerical {_ys[-1]:.6f} against analytic {_want:.6f} — these should agree closely"
'''},
            {"name": "the response settles at the supply", "code": r'''
_R, _C, _vs = 1000.0, 1e-6, 5.0
_tau = _R * _C
_ys = step_euler(_vs, _R, _C, _tau / 1000.0, 20000)
assert abs(_ys[-1] - _vs) < 1e-6, f"after 20 time constants it should be at {_vs} V, got {_ys[-1]}"
assert abs(analytic_step(_vs, _R, _C, 0.0)) < 1e-15, "the closed form must give 0 at t = 0"
'''},
            {"name": "SymPy confirms the closed form", "code": r'''
assert satisfies_ode(5.0, 1000.0, 1e-6) is True, \
    "substituting the closed form into the equation should leave exactly zero"
assert satisfies_ode(2.0, 4700.0, 2.2e-7) is True, \
    "it should hold for any values, not just the ones you tried first"
'''},
        ],
    },
}
