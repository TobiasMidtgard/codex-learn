"""MA112 — Calculus II: Integration & Series."""

COURSE = {
    "id": "MA112",
    "title": "Calculus II — Integration & Series",
    "year": 1,
    "level": "Intermediate",
    "prereqs": ["MA111"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 110,
    "icon": "∑",
    "summary": (
        "Integration and infinite series, built numerically so that every theorem "
        "leaves a measurable trace. You implement the Newton-Cotes rules and watch "
        "their error orders appear in the data, drive an adaptive integrator to a "
        "requested tolerance, tame improper integrals by substitution, and turn "
        "Taylor's theorem and the convergence tests into code that reports how "
        "wrong it might be."
    ),
    "outcomes": [
        "Derive and implement the left, right, midpoint, trapezoid and Simpson rules",
        "Measure an observed error order and match it against the theoretical one",
        "Drive an adaptive quadrature to a caller-supplied tolerance with a depth guard",
        "Convert an improper integral into a proper one by a change of variable",
        "Construct Taylor coefficients and bound the truncation error with the Lagrange remainder",
        "Apply the ratio and integral tests, and estimate a radius of convergence numerically",
        "Report a numerical answer together with a defensible error bound",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone library (60%).",
    "reading": [
        "Stewart, *Calculus: Early Transcendentals*, 9th ed. — chapters 5-8 and 11",
        "Burden, Faires & Burden, *Numerical Analysis*, 10th ed. — chapter 4",
        "Spivak, *Calculus*, 4th ed. — chapters 13-14 and 22-24",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Riemann sums and the Newton-Cotes rules",
            "summary": "From the definition of the integral to the rules that make it computable.",
            "concepts": [
                "The Riemann integral as the common limit of left, right and midpoint sums",
                "The Fundamental Theorem of Calculus links antiderivatives to areas",
                "Trapezoid rule = average of the left and right sums; error term -(b-a)h^2 f''(c)/12",
                "Midpoint rule has the same order but half the constant, and the opposite sign",
                "Simpson's rule integrates the interpolating parabola exactly, and is exact for cubics",
                "Composite error orders: O(h) for left/right, O(h^2) for midpoint/trapezoid, O(h^4) for Simpson",
                "Observed order p = log2(E(n) / E(2n)) — halving h should divide the error by 2^p",
            ],
            "read": [
                {
                    "title": "What an integral is, before anyone mentions antiderivatives",
                    "minutes": 10,
                    "body": r'''
You can find the area of a rectangle by multiplying two lengths, and the area of any
polygon by cutting it into triangles. Neither move works on the region under
$y = x^2$ between $x = 0$ and $x = 1$. Its top edge curves everywhere, so no finite
collection of straight-sided pieces sits inside it exactly, and none contains it
exactly either. Before anyone can ask what that area *is*, somebody has to say what the
word means for a shape like this — and the answer is not a formula. It is a limit, and
everything else in this course is built on top of it.

## Trapping the region between staircases

Chop $[a,b]$ at points $a = x_0 < x_1 < \cdots < x_n = b$. That list is a
**partition**. On the $i$-th piece $[x_{i-1}, x_i]$, of width
$\Delta x_i = x_i - x_{i-1}$, choose any sample point $\xi_i$ inside it and raise a
rectangle of that width and of height $f(\xi_i)$. Add the rectangles up:

$$S = \sum_{i=1}^{n} f(\xi_i)\,\Delta x_i$$

That is a **Riemann sum**. Notice that it is not one number: it depends on where you
cut and on where you sampled. Three sampling choices come up often enough to have
names. On $n$ equal panels of width $h = (b-a)/n$ they are

$$L_n = h\sum_{i=0}^{n-1} f(a+ih), \qquad
  R_n = h\sum_{i=1}^{n} f(a+ih), \qquad
  M_n = h\sum_{i=0}^{n-1} f\left(a + \left(i + \frac{1}{2}\right)h\right)$$

the left, right and midpoint sums. The **mesh** of a partition is the width of its
widest piece. We say $f$ is **integrable** on $[a,b]$ with integral $I$ when every one
of these sums tends to the same $I$ as the mesh tends to zero — whatever the cuts,
whatever the sample points — and only then do we write

$$\int_a^b f(x)\,\mathrm{d}x = I$$

Two remarks before any arithmetic. First, the $\mathrm{d}x$ is not decoration and it is
not a factor you may cancel: it is what survives of $\Delta x_i$ after the limit, and
its job is to name the variable being summed over. Second, the definition insists that
*every* sampling choice agrees on the same limit. That demand is what makes the number
well defined, and it is also exactly the hypothesis that fails in the last section
below.

## Worked: $\int_0^1 x^2\,\mathrm{d}x$ from the definition alone

Equal panels, right-hand sample points. Every line is elementary; the only thing you
need from outside is the closed form for a sum of squares.

```
h    = (1 - 0)/n = 1/n
x_i  = 0 + i h   = i/n                       i = 1, 2, ..., n

R_n  = sum over i of  h * f(x_i)
     = sum over i of  (1/n) * (i/n)^2
     = (1/n^3) * sum(i^2, i = 1..n)

sum(i^2, i = 1..n) = n(n+1)(2n+1)/6          the standard identity

R_n  = (1/n^3) * n(n+1)(2n+1)/6
     = (n+1)(2n+1) / (6 n^2)
     = (2n^2 + 3n + 1) / (6 n^2)
     = 1/3 + 1/(2n) + 1/(6 n^2)
```

Let $n\to\infty$ and the last two terms vanish, so $R_n \to \frac{1}{3}$. The left sum
gives the same limit — replace $i$ running from $1$ to $n$ by $i$ running from $0$ to
$n-1$ and you get $\frac{1}{3} - \frac{1}{2n} + \frac{1}{6n^2}$ — and it can be shown
that every other sampling choice does too. So $\int_0^1 x^2\,\mathrm{d}x = \frac{1}{3}$,
and that is a statement about a limit of sums, not about anything differentiated.

Keep the error term, because it is the first quantitative fact in this module:

$$R_n - \frac{1}{3} = \frac{1}{2n} + \frac{1}{6n^2} \approx \frac{1}{2n}$$

Double $n$ and the error roughly halves. That is what "first order" means, and at
$n = 4$ it is $0.135$ — a 40% error from four rectangles.

## Worked: $\int_0^1 e^x\,\mathrm{d}x$, the one people give up on

Most people stop at the definition here, on the grounds that you cannot sum
$e^{h} + e^{2h} + \cdots$ in closed form. You can. It is a geometric series, and
missing that is the mistake this example exists for.

```
h    = 1/n,  x_i = i/n,  f(x_i) = e^(i h) = r^i   with r = e^h

R_n  = h * sum(r^i, i = 1..n)
     = h * r (r^n - 1)/(r - 1)                 sum of a geometric series

r^n  = (e^h)^n = e^(n h) = e^1 = e             because n h = 1

R_n  = h * e^h * (e - 1) / (e^h - 1)
     = (e - 1) * e^h * h/(e^h - 1)
```

Now take the limit. As $n\to\infty$ we have $h\to0$, so $e^h\to1$; and since
$e^h - 1 = h + \frac{h^2}{2} + \cdots$, the ratio $h/(e^h-1)\to 1$ as well. Both
correction factors go to one, and

$$\int_0^1 e^x\,\mathrm{d}x = e - 1 = 1.718281\ldots$$

Check it at $n = 4$, where $h = 0.25$ and $e^{0.25} = 1.284025$:

```
R_4 = 1.718282 * 1.284025 * (0.25 / 0.284025)
    = 1.718282 * 1.284025 * 0.880203
    = 1.942007
```

against the true $1.718282$ — an error of $0.223725$. Expand the two correction
factors one term further, $e^h \approx 1 + h + \frac{h^2}{2}$ and
$h/(e^h-1) \approx 1 - \frac h2 + \frac{h^2}{12}$, multiply, and the $h$ terms leave
$R_n \approx (e-1)\left(1 + \frac h2\right)$, so the error should be about
$\frac{h}{2}(e-1) = 0.2148$. Keeping the $h^2$ term as well gives $0.223734$, which
matches the measured $0.223725$ to five figures.

That leading term generalises: for any smooth $f$,

$$R_n - \int_a^b f \approx \frac{h}{2}\left(f(b) - f(a)\right)$$

Test it on the previous example: $f(b) - f(a) = 1 - 0 = 1$, so the predicted error is
$\frac{h}{2} = \frac{1}{2n}$, which is exactly the leading term we computed there. One
formula, two integrals, both right.

## The mistake worth naming

The tempting error is to read the definition as saying $\int f$ *is* an antiderivative,
because that is how integrals are used from the second week of a first course onwards.
It is not. On this page the integral is a number obtained by adding up rectangles, and
no derivative has appeared anywhere. That the two are connected is a **theorem** —
the next reading proves it — and treating it as a definition makes the theorem
invisible and its hypotheses unnoticeable. Every wrong answer in the second half of
this course comes from applying that theorem where its hypotheses fail.

A smaller cousin: people assume $L_n \le \int_a^b f \le R_n$ always. That is true only
when $f$ is increasing, because then the left endpoint of each panel is where $f$ is
smallest on it. For decreasing $f$ the inequality reverses, and for $f$ that goes up
and then down neither sum need bracket the integral at all.

## Where this stops working

Two hypotheses are doing real work.

**$f$ must be bounded.** If $f$ is unbounded on $[a,b]$ you can drive any Riemann sum
to any value you like by moving one sample point towards the blow-up, so no common
limit exists. $\int_0^1 \frac{1}{\sqrt x}\,\mathrm{d}x$ is therefore not a Riemann
integral at all as it stands; it is an *improper* one, defined by a further limit
$\lim_{c\to0^+}\int_c^1$, and module 2 is where that gets handled properly.

**The sums must all agree.** Take Dirichlet's function: $f(x) = 1$ when $x$ is
rational, $0$ when it is irrational, on $[0,1]$. It is bounded. But every panel,
however narrow, contains both rationals and irrationals, so sampling rationals gives
$S = 1$ and sampling irrationals gives $S = 0$, at every mesh, forever. There is no
common limit, so $f$ is not Riemann integrable — not because the answer is hard to
find, but because the definition awards it no answer. (The Lebesgue integral, built on
a different construction, does give it one: zero.)

Between those extremes, the good news is generous. Every continuous function on a
closed bounded interval is integrable, and so is every bounded function with only
finitely many discontinuities — a step function, a sawtooth, a signal that has been
switched. That covers essentially everything the rest of this course integrates.
''',
                },
                {
                    "title": "The Fundamental Theorem, and the two things it says",
                    "minutes": 10,
                    "body": r'''
The previous reading computed two integrals from the definition. One needed the closed
form for $\sum i^2$, the other needed a geometric series, and both took most of a page.
Now try $\int_1^2 \frac{1}{x}\,\mathrm{d}x$ by the same method. The right sum is
$\frac1n\sum_{i=1}^{n}\frac{1}{1 + i/n}$, and there is no elementary closed form for
that sum at all. The definition, taken literally, is unusable as a method of
calculation.

The way out is the single most useful theorem in the subject, and it is worth seeing
why it is startling. Differentiation is local: $f'(c)$ depends on $f$ in an arbitrarily
small neighbourhood of $c$. Integration is global: $\int_a^b f$ is built from every
value $f$ takes on the whole interval. There is no obvious reason those two operations
should have anything to do with each other. They do, and it is a theorem rather than a
definition.

## Part one: the area-so-far function

Fix $a$ and let the upper limit move. Define

$$F(x) = \int_a^x f(t)\,\mathrm{d}t$$

the signed area accumulated from $a$ up to $x$. The dummy variable has to be renamed —
writing $\int_a^x f(x)\,\mathrm{d}x$ uses $x$ for two different jobs in one expression
and is the commonest piece of sloppiness in the whole topic.

**Claim.** If $f$ is continuous on $[a,b]$, then $F$ is differentiable and $F' = f$.

*Proof.* Take the difference quotient. Because integrals over adjacent intervals add,

$$\frac{F(x+h) - F(x)}{h} = \frac{1}{h}\int_x^{x+h} f(t)\,\mathrm{d}t$$

On the closed interval $[x, x+h]$ the continuous function $f$ attains a minimum $m_h$
and a maximum $M_h$. Every Riemann sum for $\int_x^{x+h} f$ is then squeezed between
$m_h h$ and $M_h h$, so the integral is too, and dividing by $h$ gives

$$m_h \le \frac{F(x+h) - F(x)}{h} \le M_h$$

As $h\to0$ the interval $[x, x+h]$ shrinks to the point $x$, and continuity forces both
$m_h\to f(x)$ and $M_h\to f(x)$. The quotient is trapped between two things that both
approach $f(x)$, so it approaches $f(x)$. That is $F'(x) = f(x)$, and the proof is
complete.

Read what that says: **every continuous function has an antiderivative**, and here it
is, written as an integral. Nothing was assumed about $f$ having a formula.

## Part two: how to evaluate one

**Claim.** If $G$ is *any* function with $G' = f$ on $[a,b]$, and $f$ is integrable
there, then $\int_a^b f = G(b) - G(a)$.

*Proof.* Take any partition $a = x_0 < \cdots < x_n = b$. On each piece the mean value
theorem applies to $G$, so there is some $\xi_i$ in $[x_{i-1}, x_i]$ with

$$G(x_i) - G(x_{i-1}) = G'(\xi_i)\,(x_i - x_{i-1}) = f(\xi_i)\,\Delta x_i$$

Sum over $i$. The left side telescopes to $G(b) - G(a)$, and the right side is a
Riemann sum for $f$ with a particular set of sample points:

$$G(b) - G(a) = \sum_{i=1}^{n} f(\xi_i)\,\Delta x_i$$

This holds for *every* partition, however fine. But $f$ is integrable, so as the mesh
goes to zero the right-hand side converges to $\int_a^b f$, while the left-hand side
never changed. Hence $\int_a^b f = G(b) - G(a)$, which is the claim.

Two details fall straight out of that proof and are worth naming. The theorem holds for
*any* antiderivative, because two antiderivatives differ by a constant and the constant
cancels in $G(b) - G(a)$ — which is why the constant of integration is dropped in a
definite integral. And it does not require $f$ to be continuous, only integrable and
possessed of an antiderivative; that is a weaker hypothesis than part one needs.

## Worked: the routine case

$$\int_0^{\pi}\sin x\,\mathrm{d}x$$

```
G(x) = -cos x                  since G'(x) = sin x

integral = G(pi) - G(0)
         = -cos(pi) - (-cos 0)
         = -(-1) + 1
         = 2
```

Two, exactly, and the definition would have needed a trigonometric sum identity to get
there. Sanity-check it against the geometry: the arch has height 1 and base $\pi$, so a
rectangle around it holds $\pi \approx 3.14$ and the arch fills about 64% of it. That
is the right sort of number.

## Worked: the case people get wrong

$$\frac{\mathrm{d}}{\mathrm{d}x}\int_0^{x^2}\sin t\,\mathrm{d}t$$

The near-universal answer is $\sin(x^2)$, from applying part one and stopping. It is
wrong, because part one differentiates with respect to the *upper limit*, and here the
upper limit is $x^2$, not $x$. Set it up properly:

```
let F(u) = integral of sin t from 0 to u        so F'(u) = sin u    (part one)
the quantity wanted is F(x^2)

d/dx F(x^2) = F'(x^2) * d/dx (x^2)              chain rule
            = sin(x^2) * 2x
            = 2x sin(x^2)
```

Confirm it the long way, since $\sin$ has an elementary antiderivative here:
$\int_0^{u}\sin t\,\mathrm{d}t = 1 - \cos u$, so the quantity is
$\frac{\mathrm{d}}{\mathrm{d}x}\left(1 - \cos(x^2)\right) = 2x\sin(x^2)$. The two agree.

The same care handles a moving *lower* limit, by flipping it upstairs:
$\int_x^{5} f = -\int_5^{x} f$, and so
$\frac{\mathrm{d}}{\mathrm{d}x}\int_x^5 f = -f(x)$.
The minus sign is not a convention to memorise; it is what swapping the limits does.

## Two rules the proofs quietly used

Both proofs above leaned on facts that look like bookkeeping and are not.

**Additivity.** For $a \le b \le c$, $\int_a^c f = \int_a^b f + \int_b^c f$. This falls
straight out of the definition: partition $[a,c]$ with $b$ forced to be one of the cut
points, and the Riemann sum splits cleanly into a sum over $[a,b]$ plus a sum over
$[b,c]$. Refining both halves refines the whole. The step
$F(x+h) - F(x) = \int_x^{x+h} f$ in part one is nothing but this rule, rearranged.

**Orientation.** $\int_b^a f = -\int_a^b f$, by decree. Nothing in the definition covers
a backwards interval — every $\Delta x_i$ would be negative — so the convention has to
be chosen, and it is chosen to make additivity true for *every* ordering of $a$, $b$
and $c$ rather than only the increasing one. Two things follow at once. Setting $b = a$
gives $\int_a^a f = 0$, since a number equal to its own negative is zero. And part one
becomes true for $h < 0$ as well as $h > 0$, which matters, because a two-sided limit is
half of what the word *differentiable* means.

## Worked: reading a function you can only write as an integral

Part one is not merely a device for evaluating integrals. It is often the only way to
say anything at all about a function. The sine integral

$$\mathrm{Si}(x) = \int_0^x \frac{\sin t}{t}\,\mathrm{d}t$$

turns up in optics and in filter design and has no elementary closed form. Part one
nevertheless hands over its derivative immediately: $\mathrm{Si}'(x) = \frac{\sin x}{x}$
for $x \neq 0$. From that, ordinary calculus takes over.

```
Si'(x) = 0     where sin x = 0 and x is not 0
               so at x = pi, 2pi, 3pi, ...

Si'(x) > 0     on (0, pi),      since sin x > 0 and x > 0
Si'(x) < 0     on (pi, 2pi),    since sin x < 0 and x > 0

so x = pi is a maximum, x = 2pi a minimum, and so on alternately
```

The stationary points shrink in size as $1/x$ pulls the oscillation down, so the first
peak is the tallest: $\mathrm{Si}(\pi) \approx 1.8519$ is the global maximum of a
function nobody can write in closed form. That overshoot above the limiting value
$\pi/2 \approx 1.5708$ is a real physical effect — it is the Gibbs phenomenon, the
ringing you see at a step edge — and it was found by exactly this argument.

## Where this stops holding

Part two says $\int_a^b f = G(b) - G(a)$ whenever $G' = f$ **on the whole of
$[a,b]$**. Drop that and it produces nonsense:

$$\int_{-1}^{1}\frac{\mathrm{d}x}{x^2}
  = \left[-\frac1x\right]_{-1}^{1} = -1 - 1 = -2$$

A strictly positive integrand has returned a negative area. The fault is not in the
arithmetic: $-1/x$ really is an antiderivative of $1/x^2$ on $(0,1]$ and on $[-1,0)$.
It is that $1/x^2$ is unbounded at $x = 0$, which sits inside the interval, so $f$ is
not integrable on $[-1,1]$ and $G$ is not even defined there. The bracket notation
hides the hypothesis, which is exactly why the slip is so easy. The honest treatment
splits at the singularity and takes limits, and here both halves diverge: the integral
does not exist.

Part one has a boundary too. If $f$ is merely integrable rather than continuous, $F$ is
still continuous — indeed Lipschitz, since $|F(x+h)-F(x)|\le h\max|f|$ — but $F'$ need
not equal $f$ at a point where $f$ jumps. Take $f = 0$ on $[-1,0)$ and $f = 1$ on
$[0,1]$. Then $F(x) = 0$ for $x\le0$ and $F(x) = x$ for $x\ge0$: a corner at the
origin, where $F$ has no derivative at all, while $f(0) = 1$. Integration smooths, but
it cannot smooth a jump into differentiability.

Everywhere else, both parts hold, and for the rest of this course the practical
question is the one that opens the next reading: what do you do when $f$ is perfectly
continuous but $G$ cannot be written down?
''',
                },
                {
                    "title": "Why one rule beats another: the error terms",
                    "minutes": 11,
                    "body": r'''
The Fundamental Theorem converts an integral into a subtraction — provided you can
write the antiderivative down. Often you cannot. The function $e^{-x^2}$ is as smooth
as anything in mathematics and has no antiderivative expressible in elementary
functions; the same is true of $\frac{\sin x}{x}$, of $\sqrt{1 + x^3}$, and of most
integrands that arise from a real problem rather than from a textbook exercise. For
those you are back to adding up rectangles.

Except that plain rectangles are hopeless. The previous reading measured the right-sum
error as roughly $\frac{h}{2}(f(b) - f(a))$: first order in $h$, so to gain one decimal
place you multiply the work by ten, and six decimal places costs about a million
function evaluations. The Newton-Cotes rules exist because you can do enormously better
for the same number of samples, and the point of this reading is *how much* better, and
exactly what has to be true of $f$ for the improvement to appear.

## One panel at a time

Everything follows from what a rule does on a single panel of width $h$; the composite
rule is just $n$ copies of it. Take one panel running from $u$ to $u+h$, with midpoint
$m = u + \frac{h}{2}$. Expand $f$ in a Taylor series about $m$, integrate term by term,
and compare with what the rule returns. The module's derivation exercise does this in
full; the results are

$$\int_u^{u+h} f - h\,f(m) = +\frac{h^3}{24}f''(\xi),
\qquad
\int_u^{u+h} f - \frac{h}{2}\left(f(u) + f(u+h)\right) = -\frac{h^3}{12}f''(\xi)$$

for some $\xi$ in the panel. Three facts are packed in there, and each is worth
pulling out.

Both errors carry $h^3$, not $h^2$ — one power better than a plain rectangle, because
sampling at the middle (or averaging the two ends) makes the rule exact for straight
lines, and the first surviving term in the Taylor expansion is the quadratic one.

Both errors are proportional to $f''$. A rule that is exact for straight lines can only
be wrong to the extent that $f$ curves, so its error must be measured by curvature.
Where $f'' = 0$ these rules are exact.

The two constants are $\frac{1}{24}$ and $-\frac{1}{12}$. The midpoint rule is
typically **twice as accurate as the trapezoid rule, and wrong in the opposite
direction** — which is not what anyone guesses, since the trapezoid rule uses two
function values per panel and the midpoint rule uses one. Geometrically: for a convex
$f$ the chord lies above the curve, so the trapezoid overshoots; the midpoint tangent
line lies below it, and the tangent-line trapezoid — which has the same area as the
midpoint rectangle — undershoots by half as much.

## From one panel to $n$ of them

Add up $n$ panels of width $h = (b-a)/n$. Each contributes an error of order $h^3$, and
there are $n = (b-a)/h$ of them, so one power of $h$ is eaten by the panel count:

$$E_{\text{trap}} = -\frac{(b-a)h^2}{12}f''(\xi),
\qquad
E_{\text{mid}} = +\frac{(b-a)h^2}{24}f''(\xi),
\qquad
E_{\text{Simp}} = -\frac{(b-a)h^4}{180}f^{(4)}(\xi)$$

That last one is why Simpson's rule is the default. Halving $h$ divides a trapezoid
error by $2^2 = 4$ and a Simpson error by $2^4 = 16$. Over four halvings — sixteen
times the work — the trapezoid rule gains a factor of $256$ and Simpson a factor of
$65\,536$.

The practical handle on all of this is the **observed order**. Compute with $n$ panels
and with $2n$, and form

$$p = \log_2\frac{|E(n)|}{|E(2n)|}$$

If the theory holds, $p$ comes out at $1$ for the left and right sums, $2$ for midpoint
and trapezoid, and $4$ for Simpson. Measuring $p$ is how you find out whether your
implementation and your integrand are behaving, and it is what the lab in this module
asks you to build.

## Worked: the trapezoid rule, and does it obey its own bound?

Estimate $\int_1^2\frac{\mathrm{d}x}{x}$ with four panels, then check the error against
the bound.

```
h = 0.25;  nodes 1, 1.25, 1.5, 1.75, 2

T(4) = h * [ f(1)/2 + f(1.25) + f(1.5) + f(1.75) + f(2)/2 ]
     = 0.25 * [ 0.500000 + 0.800000 + 0.666667 + 0.571429 + 0.250000 ]
     = 0.25 * 2.788095
     = 0.697024

exact   = ln 2 = 0.693147
error   = 0.697024 - 0.693147 = +0.003877
```

Positive, as predicted for a convex integrand. Now the bound: $f(x) = 1/x$ gives
$f''(x) = 2/x^3$, which on $[1,2]$ is largest at $x = 1$, where it equals $2$. So

```
|E| <= (b - a) h^2 |f''|max / 12
     = 1 * 0.0625 * 2 / 12
     = 0.010417
```

and $0.003877 \le 0.010417$ holds. The bound is loose by a factor of about $2.7$, which
is normal: it used the worst curvature anywhere on the interval, while the true error
uses an average. A bound you can compute in two lines is worth having even when it is
pessimistic, and the numeric exercises in this module use exactly this one to size a
panel count in advance.

## Worked: the case people get wrong — Simpson on a cubic

Simpson's rule is derived by fitting a parabola through three equally spaced points and
integrating it. Everyone therefore expects it to be exact for polynomials up to degree
two and wrong from degree three onwards. It is exact for cubics as well, and the reason
is short enough to see in one line.

Put the middle node at the origin, so the panel pair is $[-h, h]$ and the rule reads
$\frac{h}{3}\left(f(-h) + 4f(0) + f(h)\right)$. Feed it $f(x) = x^3$:

```
rule  = (h/3) * [ (-h)^3 + 4*0 + h^3 ]
      = (h/3) * [ -h^3 + h^3 ]
      = 0

exact = integral of x^3 from -h to h
      = [x^4/4] from -h to h
      = h^4/4 - h^4/4
      = 0
```

Both zero, so the rule is exact on $x^3$; it is already exact on $1$, $x$ and $x^2$
because it integrates the interpolating parabola exactly, and every cubic is a
combination of those four. The cubic term is odd about the middle node, and both the
rule and the true integral kill odd terms by symmetry.

This is not a curiosity — it is the whole reason for the $h^4$. The first term Simpson
cannot handle is $x^4$, so the error is governed by $f^{(4)}$, and one free order of
accuracy has been picked up from symmetry. It is also the standard exam trap: asked for
the *degree of precision* of Simpson's rule, the answer is $3$, not $2$.

## Where the orders stop appearing

Every error term above contains a derivative of $f$ evaluated somewhere in the
interval, which quietly assumes that derivative exists and is bounded. When it is not,
the order collapses. Take $\int_0^1\sqrt x\,\mathrm{d}x = \frac{2}{3}$, where
$f'' = -\frac{1}{4}x^{-3/2}$ blows up at the left endpoint. Measured orders:

```
   n      trapezoid error      observed p        Simpson error     observed p
   16       3.085e-03             1.48             1.268e-03          1.500
   32       1.108e-03             1.48             4.485e-04          1.500
   64       3.959e-04             1.49             1.586e-04          1.500
  128       1.410e-04             1.49             ...
```

Both rules run at order $1.5$, not $2$ and certainly not $4$. Nothing is broken: the
singular endpoint contributes an error of its own that no amount of smooth-function
theory controls, and Simpson's extra samples buy nothing at all. The fix is not more
panels — it is a change of variable that removes the singularity, which is what module
2 does. Substituting $x = u^2$ turns this integral into $\int_0^1 2u^2\,\mathrm{d}u$,
a polynomial, on which Simpson is exact.

There is a floor at the other end too. The error terms fall as $h$ shrinks, but the
number of floating-point additions grows, and their rounding errors accumulate roughly
as $\sqrt n$ times the machine epsilon. Somewhere around $n\sim10^{6}$ for a trapezoid
rule in double precision, refinement stops helping and starts hurting. Simpson reaches
its floor at a few hundred panels — long before rounding matters — which is one more
argument for using a higher-order rule rather than a finer grid.
''',
                },
            ],
            "derive": [
                {
                    "title": "Adding up the rectangles: $\\int_0^1 x^2\\,\\mathrm{d}x$",
                    "minutes": 12,
                    "vars": ["n", "i", "h", "S"],
                    "brief": r'''
The integral $\int_0^1 x^2\,\mathrm{d}x$ is going to come out as $\frac{1}{3}$, and you
already know that from the Fundamental Theorem. The point of doing it from the
definition is that no theorem is used: only $n$ rectangles, one algebraic identity, and
a limit.

Split $[0,1]$ into $n$ equal panels and sample each one at its **right-hand** endpoint.
The identity you will need at the fourth step is
$\sum_{i=1}^{n} i^2 = \frac{n(n+1)(2n+1)}{6}$.
''',
                    "steps": [
                        {
                            "prompt": "Write the panel width $h$ in terms of $n$.",
                            "answer": "\\frac{1}{n}",
                            "placeholder": "1/n or similar",
                            "hint": "The interval $[0,1]$ has length $1$, cut into $n$ equal pieces.",
                        },
                        {
                            "prompt": "Write the right-hand endpoint $x_i$ of the $i$-th panel, in terms of $i$ and $n$.",
                            "answer": "\\frac{i}{n}",
                            "hint": "Start at $0$ and take $i$ steps of width $h$. The first panel ends at $h$, the second at $2h$.",
                        },
                        {
                            "prompt": "The $i$-th rectangle has width $h$ and height $f(x_i) = x_i^2$. Write its area in terms of $i$ and $n$.",
                            "answer": "\\frac{i^2}{n^3}",
                            "hint": "$\\left(\\frac{i}{n}\\right)^2$ times $\\frac{1}{n}$ — square the fraction first, then multiply.",
                        },
                        {
                            "prompt": "Sum those areas over $i = 1$ to $n$, using $\\sum i^2 = \\frac{n(n+1)(2n+1)}{6}$, and simplify. Write $S_n$ in terms of $n$ alone.",
                            "answer": "\\frac{(n+1)(2n+1)}{6n^2}",
                            "hint": "The $\\frac{1}{n^3}$ comes outside the sum because it does not depend on $i$. Then one factor of $n$ cancels from the top.",
                            "deconstruct": [
                                "$S_n = \\sum_{i=1}^{n}\\frac{i^2}{n^3} = \\frac{1}{n^3}\\sum_{i=1}^{n} i^2$.",
                                "Substitute the identity: $\\frac{1}{n^3}\\cdot\\frac{n(n+1)(2n+1)}{6}$.",
                                "One $n$ on the top cancels one of the three on the bottom, leaving $6n^2$ underneath.",
                            ],
                        },
                        {
                            "prompt": "Multiply out the top and split the fraction, so that the $n$-dependence is visible. Write $S_n$ as a constant plus two decaying terms.",
                            "answer": "\\frac{1}{3}+\\frac{1}{2n}+\\frac{1}{6n^2}",
                            "hint": "$(n+1)(2n+1) = 2n^2 + 3n + 1$. Divide each of those three terms by $6n^2$ separately.",
                        },
                        {
                            "prompt": "The limit as $n\\to\\infty$ is $\\frac{1}{3}$. Write the error $S_n - \\frac{1}{3}$ that the $n$-panel sum still carries.",
                            "answer": "\\frac{1}{2n}+\\frac{1}{6n^2}",
                            "hint": "Everything except the constant term survives.",
                        },
                    ],
                    "closing": r'''
Two things come out of that last line. The limit exists and equals $\frac{1}{3}$, so
$\int_0^1 x^2\,\mathrm{d}x = \frac{1}{3}$ by the definition alone — no antiderivative was
used anywhere.

And the error is dominated by $\frac{1}{2n}$: **first order**. Doubling the panel count
halves the error, so squeezing out one more decimal digit costs ten times the work, and
six digits would need about a million rectangles. At $n = 4$ the sum is
$\frac{1}{3} + 0.125 + 0.0104 = 0.4688$, a 40% overestimate. That number is the reason the
rest of this module exists.

Compare it with the general prediction from the reading,
$R_n - \int_a^b f \approx \frac{h}{2}(f(b) - f(a))$. Here $f(1) - f(0) = 1$ and
$h = \frac1n$, so the predicted error is $\frac{1}{2n}$ — exactly the leading term you
just derived.
''',
                },
                {
                    "title": "Simpson's rule, from the parabola through three points",
                    "minutes": 14,
                    "vars": ["A", "B", "C", "h", "x", "y_0", "y_1", "y_2"],
                    "brief": r'''
The trapezoid rule joins two samples with a straight line. The obvious next move is to
join three equally spaced samples with a parabola and integrate that instead — and that
is the whole content of Simpson's rule. Everything below is the fit, done once.

Put the middle sample at the origin, so the three nodes are at $x = -h$, $0$, $+h$ with
values $y_0$, $y_1$, $y_2$. Nothing is lost by that choice: shifting the origin shifts
both the parabola and the integral by the same amount. Fit
$p(x) = Ax^2 + Bx + C$ and integrate it over $[-h, h]$.
''',
                    "steps": [
                        {
                            "prompt": "Write $p(-h)$, in terms of $A$, $B$, $C$ and $h$.",
                            "answer": "A h^2 - B h + C",
                            "hint": "Substitute $x = -h$ into $Ax^2 + Bx + C$ and watch the sign on the middle term: $(-h)^2 = +h^2$ but $B(-h) = -Bh$.",
                        },
                        {
                            "prompt": "The middle node gives the easiest equation. Write $C$ in terms of the sample values.",
                            "answer": "y_1",
                            "hint": "Put $x = 0$ into the parabola; two of the three terms disappear.",
                        },
                        {
                            "prompt": "Add $p(-h)$ and $p(h)$, set the result equal to $y_0 + y_2$, and solve for $A$. Write $A$ in terms of $y_0$, $y_1$, $y_2$ and $h$.",
                            "answer": "\\frac{y_0 - 2y_1 + y_2}{2h^2}",
                            "hint": "The $B$ terms cancel when you add, leaving $2Ah^2 + 2C = y_0 + y_2$. Now put $C = y_1$ into that and isolate $A$.",
                            "deconstruct": [
                                "$p(-h) + p(h) = (Ah^2 - Bh + C) + (Ah^2 + Bh + C) = 2Ah^2 + 2C$.",
                                "Matching the data: $2Ah^2 + 2C = y_0 + y_2$, and $C = y_1$, so $2Ah^2 = y_0 - 2y_1 + y_2$.",
                                "Divide by $2h^2$. The numerator $y_0 - 2y_1 + y_2$ is the second difference — the discrete version of $f''$, which is what a parabola's leading coefficient has to be.",
                            ],
                        },
                        {
                            "prompt": "Integrate the general parabola over the panel pair: write $\\int_{-h}^{h}\\left(Ax^2 + Bx + C\\right)\\mathrm{d}x$ in terms of $A$, $C$ and $h$.",
                            "answer": "\\frac{2Ah^3}{3} + 2Ch",
                            "hint": "Antidifferentiate term by term. The $Bx$ term integrates to $\\frac{Bx^2}{2}$, which takes the same value at $-h$ and $+h$, so it contributes nothing.",
                            "deconstruct": [
                                "$\\int_{-h}^{h} Ax^2\\,\\mathrm{d}x = \\frac{A}{3}\\left(h^3 - (-h)^3\\right) = \\frac{2Ah^3}{3}$.",
                                "$\\int_{-h}^{h} Bx\\,\\mathrm{d}x = \\frac{B}{2}\\left(h^2 - h^2\\right) = 0$ — the odd term integrates away over a symmetric interval.",
                                "$\\int_{-h}^{h} C\\,\\mathrm{d}x = 2Ch$.",
                            ],
                        },
                        {
                            "prompt": "Substitute your $A$ and your $C$ into that integral, and simplify. Write the result in terms of $h$, $y_0$, $y_1$ and $y_2$.",
                            "answer": "\\frac{h(y_0 + 4y_1 + y_2)}{3}",
                            "hint": "The $h^3$ over $h^2$ leaves one $h$; the $2$s cancel against the $2$ in the denominator of $A$. Then collect the $y_1$ terms: you will have $-\\frac{2h}{3}y_1$ from the first piece and $2hy_1$ from the second.",
                            "deconstruct": [
                                "First piece: $\\frac{2h^3}{3}\\cdot\\frac{y_0 - 2y_1 + y_2}{2h^2} = \\frac{h}{3}(y_0 - 2y_1 + y_2)$.",
                                "Second piece: $2Ch = 2hy_1 = \\frac{h}{3}\\cdot 6y_1$.",
                                "Add them: $\\frac{h}{3}\\left(y_0 - 2y_1 + y_2 + 6y_1\\right) = \\frac{h}{3}(y_0 + 4y_1 + y_2)$.",
                            ],
                        },
                    ],
                    "closing": r'''
That is Simpson's rule: $\frac{h}{3}\left(y_0 + 4y_1 + y_2\right)$ over a *pair* of
panels of width $h$. Chain the pairs along $[a,b]$ and the shared nodes get counted
once from each side, which is where the $1,4,2,4,\ldots,4,1$ pattern of the composite
rule comes from — the $2$s are interior nodes that end one pair and begin the next.
This is also why the composite rule needs an even number of panels: the panels are
consumed two at a time.

Notice what the $B$ did. It never appeared in the answer, because an odd function
integrates to zero over a symmetric interval. That single cancellation is worth a whole
order of accuracy: the same argument applied to $f(x) = x^3$ shows the rule returns
$\frac{h}{3}\left(-h^3 + 0 + h^3\right) = 0$, which is exactly $\int_{-h}^{h}x^3 =0$.
So a rule built from parabolas integrates every cubic exactly, and its error term
involves $f^{(4)}$ rather than $f^{(3)}$ — the $h^4$ that makes it the workhorse.
''',
                },
                {
                    "title": "Midpoint, trapezoid, and the combination that beats both",
                    "minutes": 15,
                    "vars": ["F", "G", "P", "h", "t", "M", "T", "I", "y_0", "y_1", "y_2"],
                    "brief": r'''
Where do the constants $\frac{1}{12}$ and $\frac{1}{24}$ in the error terms come from,
and why does the midpoint rule beat the trapezoid rule despite using half as many
samples? Taylor's theorem answers both, and then hands over something better than
either rule for free.

Work on one panel of width $h$, running from $a = m - \frac h2$ to $b = m + \frac h2$
about its midpoint $m$. Write $t = x - m$, and abbreviate the derivatives at the
midpoint as $F = f(m)$, $G = f'(m)$, $P = f''(m)$, so that

$$f(m + t) = F + Gt + \frac{P}{2}t^2 + \cdots$$

Call the exact integral over the panel $I$, the midpoint estimate $M = hF$, and the
trapezoid estimate $T = \frac{h}{2}\left(f(a) + f(b)\right)$.
''',
                    "steps": [
                        {
                            "prompt": "Integrate the three written terms of the expansion over $t$ from $-\\frac h2$ to $\\frac h2$. Write $I$ in terms of $F$, $P$ and $h$.",
                            "answer": "F h + \\frac{P h^3}{24}",
                            "hint": "The constant gives $Fh$. The $Gt$ term is odd and integrates to zero over a symmetric interval. For the last one, $\\int_{-h/2}^{h/2} t^2\\,\\mathrm{d}t = \\frac{2}{3}\\left(\\frac h2\\right)^3 = \\frac{h^3}{12}$.",
                            "deconstruct": [
                                "$\\int_{-h/2}^{h/2} F\\,\\mathrm{d}t = Fh$.",
                                "$\\int_{-h/2}^{h/2} Gt\\,\\mathrm{d}t = 0$ by symmetry — this is why the midpoint is the right place to expand about.",
                                "$\\int_{-h/2}^{h/2}\\frac{P}{2}t^2\\,\\mathrm{d}t = \\frac{P}{2}\\cdot\\frac{h^3}{12} = \\frac{Ph^3}{24}$.",
                            ],
                        },
                        {
                            "prompt": "The midpoint rule returns $M = hF$. Write the midpoint error $I - M$.",
                            "answer": "\\frac{P h^3}{24}",
                            "hint": "Subtract $hF$ from what you just wrote; only one term is left.",
                        },
                        {
                            "prompt": "Now the trapezoid. Put $t = -\\frac h2$ and $t = +\\frac h2$ into the expansion and add the two results. Write $f(a) + f(b)$ in terms of $F$, $P$ and $h$.",
                            "answer": "2F + \\frac{P h^2}{4}",
                            "hint": "The $G$ terms are $\\pm G\\frac h2$ and cancel. Each quadratic term is $\\frac{P}{2}\\cdot\\frac{h^2}{4} = \\frac{Ph^2}{8}$, and there are two of them.",
                        },
                        {
                            "prompt": "The trapezoid rule is $\\frac h2$ times that sum. Write $T$ in terms of $F$, $P$ and $h$.",
                            "answer": "F h + \\frac{P h^3}{8}",
                            "hint": "Multiply both terms by $\\frac h2$: $\\frac h2\\cdot 2F = Fh$, and $\\frac h2\\cdot\\frac{Ph^2}{4} = \\frac{Ph^3}{8}$.",
                        },
                        {
                            "prompt": "Write the trapezoid error $I - T$, simplified to a single term.",
                            "answer": "-\\frac{P h^3}{12}",
                            "hint": "$\\frac{Ph^3}{24} - \\frac{Ph^3}{8}$. Put both over $24$: $\\frac{1}{8} = \\frac{3}{24}$.",
                            "deconstruct": [
                                "$I - T = \\left(Fh + \\frac{Ph^3}{24}\\right) - \\left(Fh + \\frac{Ph^3}{8}\\right)$.",
                                "The $Fh$ cancels, leaving $\\frac{Ph^3}{24} - \\frac{3Ph^3}{24} = -\\frac{2Ph^3}{24}$.",
                                "That reduces to $-\\frac{Ph^3}{12}$: twice the midpoint error in size, and opposite in sign.",
                            ],
                        },
                        {
                            "prompt": "Both errors are multiples of $Ph^3$, with opposite signs, so some weighted average of $M$ and $T$ has no $Ph^3$ error at all. Find the weights and write that combination in terms of $M$ and $T$.",
                            "answer": "\\frac{2M + T}{3}",
                            "hint": "Try $\\alpha M + (1-\\alpha)T$. Its error is $\\alpha(I-M) + (1-\\alpha)(I-T) = \\alpha\\frac{Ph^3}{24} - (1-\\alpha)\\frac{Ph^3}{12}$. Set that to zero and solve for $\\alpha$.",
                            "deconstruct": [
                                "Zero error needs $\\frac{\\alpha}{24} = \\frac{1-\\alpha}{12}$, so $\\alpha = 2(1-\\alpha)$.",
                                "That gives $3\\alpha = 2$, so $\\alpha = \\frac{2}{3}$ and the trapezoid weight is $\\frac{1}{3}$.",
                                "The trapezoid is wrong by twice as much, so it gets half the weight: the combination is $\\frac{2}{3}M + \\frac{1}{3} T$.",
                            ],
                        },
                        {
                            "prompt": "Substitute $M = h y_1$ and $T = \\frac h2\\left(y_0 + y_2\\right)$, where $y_0 = f(a)$, $y_1 = f(m)$, $y_2 = f(b)$. Write $\\frac{2M+T}{3}$ in terms of $h$, $y_0$, $y_1$ and $y_2$.",
                            "answer": "\\frac{h(y_0 + 4y_1 + y_2)}{6}",
                            "hint": "The numerator is $2hy_1 + \\frac h2(y_0 + y_2)$. Put it all over $2$, then divide by the $3$ outside.",
                            "deconstruct": [
                                "$2M + T = 2hy_1 + \\frac{h}{2}(y_0 + y_2) = \\frac{h}{2}\\left(4y_1 + y_0 + y_2\\right)$.",
                                "Dividing by $3$ gives $\\frac{h}{6}\\left(y_0 + 4y_1 + y_2\\right)$.",
                            ],
                        },
                    ],
                    "closing": r'''
The three nodes $a$, $m$, $b$ are spaced $\frac h2$ apart, so writing $H = \frac h2$
turns that last expression into $\frac{H}{3}\left(y_0 + 4y_1 + y_2\right)$ —
**Simpson's rule**, arrived at from a completely different direction than
the parabola fit. Two rules that are each wrong at order $h^3$ were combined so that
their leading errors cancelled, and the result is right to order $h^5$ per panel. That
manoeuvre is called **Richardson extrapolation**, and it is the engine of the adaptive
integrator in module 2.

Multiply the panel errors by $n = (b-a)/h$ panels to get the composite versions used
throughout the course:

$$E_{\text{mid}} = \frac{(b-a)h^2}{24}f''(\xi),
\qquad
E_{\text{trap}} = -\frac{(b-a)h^2}{12}f''(\xi)$$

Both are $O(h^2)$; the midpoint constant is half the trapezoid's and the sign is
reversed. That relation is easy to check on real numbers: for $\int_0^1 e^x\,\mathrm{d}x$
with four panels, the trapezoid rule gives $1.727222$ and the midpoint rule $1.713815$,
against an exact $1.718282$ — errors of $+0.008940$ and $-0.004467$. Their ratio is
$-2.0016$, which is the $-\frac{1}{12}$ against the $+\frac{1}{24}$, measured.

One warning. Everything above assumed $f''$ exists and stays bounded on the panel. If
it does not — a square root at an endpoint, a kink, a pole just outside the interval —
the $h^3$ term is not the leading behaviour, the cancellation does not happen, and the
combination has no advantage over either of its parts.
''',
                },
            ],
            "numeric": [
                {
                    "title": "One midpoint sum, by hand",
                    "minutes": 5,
                    "brief": r'''
The first rung: nothing to derive, nothing to rearrange. Take the rule as it is
written, work out where the samples go, and add them up.
''',
                    "prompt": "What does the composite midpoint rule with four panels give for this integral?",
                    "note": "Give the answer to six decimal places.",
                    "figure": "Estimate $\\int_1^2 \\frac{1}{x}\\,\\mathrm{d}x$ using the composite midpoint "
                              "rule on $n = 4$ equal panels. The rule is "
                              "$M_n = h\\sum f(\\text{panel midpoints})$, with $h = (b-a)/n$.",
                    "given": [
                        {"label": "Interval", "value": "$[1, 2]$"},
                        {"label": "Integrand", "value": "$f(x) = 1/x$"},
                        {"label": "Panels", "value": "4"},
                    ],
                    "aside": "The panels are $[1, 1.25]$, $[1.25, 1.5]$, $[1.5, 1.75]$, $[1.75, 2]$. Sample "
                             "each one at its centre, not at either end.",
                    "answer": 0.691220,
                    "tol": 0.0003,
                    "unit": "",
                    "hint": "$h = 0.25$, and the four midpoints are $1.125$, $1.375$, $1.625$ and $1.875$. "
                            "Add the four reciprocals, then multiply the total by $h$ once at the end.",
                    "wrong": "If you got $0.697024$ you used the panel *endpoints* with the trapezoid "
                             "weighting; if you got $0.759524$ you used the left endpoints, and if you got "
                             "$0.634524$ the right ones. All three are legitimate rules and none of them "
                             "is this one.",
                    "why": r'''
$h = (2-1)/4 = 0.25$, and the midpoints are $1.125, 1.375, 1.625, 1.875$:

```
1/1.125 = 0.888889
1/1.375 = 0.727273
1/1.625 = 0.615385
1/1.875 = 0.533333
                    ---------
sum               = 2.764880
times h = 0.25    = 0.691220
```

The exact value is $\ln 2 = 0.693147$, so the estimate is low by $0.001927$. Low is
what the theory predicts: $f'' = 2/x^3 > 0$ on this interval, so $f$ is convex, and the
midpoint error $I - M = +\frac{(b-a)h^2}{24}f''(\xi)$ is positive — the estimate sits
*below* the true value. Compare it with the trapezoid rule on the same four panels,
which gives $0.697024$, high by $0.003877$. The midpoint rule used four function
evaluations to the trapezoid's five and was twice as accurate, in the opposite
direction.
''',
                },
                {
                    "title": "Simpson, on an integral with no antiderivative",
                    "minutes": 8,
                    "brief": r'''
The second rung: the same mechanical process, on the rule that actually gets used, and
on an integrand where the Fundamental Theorem is no help at all. $e^{-x^2}$ has no
elementary antiderivative — this is the Gaussian whose integral defines the error
function — so quadrature is not a convenience here, it is the only route.
''',
                    "prompt": "What does composite Simpson's rule with four panels give for this integral?",
                    "note": "Give the answer to six decimal places. Carry at least six decimals through the "
                            "intermediate function values.",
                    "figure": "Estimate $\\int_0^1 e^{-x^2}\\,\\mathrm{d}x$ using composite Simpson's rule "
                              "on $n = 4$ equal panels, "
                              "$S = \\frac{h}{3}\\left(y_0 + 4y_1 + 2y_2 + 4y_3 + y_4\\right)$.",
                    "given": [
                        {"label": "Interval", "value": "$[0, 1]$"},
                        {"label": "Integrand", "value": "$f(x) = e^{-x^2}$"},
                        {"label": "Panels", "value": "4 (so $h = 0.25$)"},
                        {"label": "Weights", "value": "1, 4, 2, 4, 1"},
                    ],
                    "aside": "Five nodes, five weights. The interior node at $x = 0.5$ takes weight 2 "
                             "because it is where one panel pair ends and the next begins.",
                    "answer": 0.746855,
                    "tol": 0.00005,
                    "unit": "",
                    "hint": "$y_0 = e^0 = 1$, $y_1 = e^{-0.0625}$, $y_2 = e^{-0.25}$, $y_3 = e^{-0.5625}$, "
                            "$y_4 = e^{-1}$. Square the node first, then negate, then exponentiate.",
                    "wrong": "If you got $2.240566$ you multiplied by $h$ but never divided by 3, and if "
                             "you got $0.186714$ you divided by the panel count as well as by 3. If you "
                             "got $0.625123$ the weight 4 was parked on the middle node — the pattern is "
                             "$1, 4, 2, 4, 1$, with the 4s on the odd-indexed nodes. And if you got "
                             "$0.432478$ the integrand was read as $\\left(e^{-x}\\right)^2 = e^{-2x}$ "
                             "rather than $e^{-(x^2)}$, which is a different function entirely.",
                    "why": r'''
```
x      x^2       y = e^(-x^2)     weight    weight * y
0.00   0.0000      1.000000          1        1.000000
0.25   0.0625      0.939413          4        3.757652
0.50   0.2500      0.778801          2        1.557602
0.75   0.5625      0.569783          4        2.279132
1.00   1.0000      0.367879          1        0.367879
                                             ----------
                                              8.962265

S = (h/3) * 8.962265 = (0.25/3) * 8.962265 = 0.746855
```

The true value is $0.746824$, so Simpson is off by $3.1\times10^{-5}$ using five
function evaluations. For comparison, the trapezoid rule on the same five nodes gives
$0.742984$, off by $3.8\times10^{-3}$ — a hundred and twenty times worse for exactly
the same samples. That gap is the whole practical content of the $h^4$ against the
$h^2$: it costs nothing extra, it is purely a matter of which weights you attach to
the values you already have.
''',
                },
                {
                    "title": "How many panels for six digits?",
                    "minutes": 9,
                    "brief": r'''
The third rung reverses the question. Instead of computing an estimate and then asking
how wrong it is, you are told how wrong it may be and asked how much work that costs.
This is the calculation you do *before* running anything, and it is the reason the
error bounds are worth carrying around.
''',
                    "prompt": "What is the smallest number of equal panels for which the bound guarantees the required accuracy?",
                    "note": "Give a whole number of panels.",
                    "figure": "You need $\\int_0^1 e^{x}\\,\\mathrm{d}x$ to within $10^{-6}$ using the "
                              "composite trapezoid rule, and you intend to justify the claim with the "
                              "standard bound "
                              "$|E| \\le \\frac{(b-a)h^2}{12}\\max_{[a,b]}\\left|f''\\right|$, "
                              "where $h = (b-a)/n$.",
                    "given": [
                        {"label": "Interval", "value": "$[0, 1]$"},
                        {"label": "Integrand", "value": "$f(x) = e^x$"},
                        {"label": "Required", "value": "$|E| \\le 10^{-6}$"},
                    ],
                    "aside": "You have to find $\\max|f''|$ on the interval before you can use the bound. "
                             "For this integrand every derivative is the same function.",
                    "answer": 476,
                    "tol": 0.5,
                    "unit": "panels",
                    "hint": "$f'' = e^x$, which is increasing, so its maximum on $[0,1]$ is $e$. Put "
                            "$h = 1/n$ into the bound, set it equal to $10^{-6}$, and solve for $n$ — then "
                            "round the right way.",
                    "wrong": "If you got 475 you rounded to nearest instead of rounding up: $n = 475.94$ is "
                             "not enough, and the bound only holds at the next whole panel count. If you "
                             "got 289 the $\\max|f''|$ was taken as $1$ instead of $e$, and if you got "
                             "$226\\,524$ the square root was never taken.",
                    "why": r'''
```
f(x) = e^x  ->  f''(x) = e^x, increasing, so max on [0,1] is e = 2.718282

|E| <= (b - a) h^2 e / 12       with b - a = 1 and h = 1/n

    = e / (12 n^2)

require   e / (12 n^2)  <=  1e-6

          n^2  >=  e / (12 * 1e-6)  =  226 523.5

          n    >=  475.94...

          n    =  476            round UP; 475 fails the bound
```

That is 477 function evaluations for six decimal places, and it is worth seeing how
badly that compares. Simpson's bound is
$\frac{(b-a)h^4}{180}\max\left|f^{(4)}\right| = \frac{e}{180 n^4}$, and setting that
below $10^{-6}$ gives $n^4 \ge 15\,102$, so $n \ge 11.09$ — twelve panels, thirteen
evaluations. Forty times fewer samples for the same guarantee.

One honest caveat: the bound is not the error. At $n = 476$ the trapezoid rule is
actually off by $6.3\times10^{-7}$, not $10^{-6}$, because the bound used the largest
curvature anywhere on the interval while the true error responds to an average of it.
Bounds of this kind are always pessimistic, and that is the price of being certain in
advance rather than measuring afterwards.
''',
                },
                {
                    "title": "Two trapezoids, combined",
                    "minutes": 10,
                    "brief": r'''
The top rung. Nothing here can be looked up: you have to compute two estimates that
were not given to you, then combine them by a rule whose weights come out of the error
analysis rather than out of the table. The answer is worth more than the arithmetic
that produces it.
''',
                    "prompt": "What is the value of the combination $\\frac{4T(4) - T(2)}{3}$?",
                    "note": "Give the answer to six decimal places.",
                    "figure": "For $\\int_1^2\\frac{1}{x}\\,\\mathrm{d}x$, let $T(n)$ be the composite "
                              "trapezoid estimate on $n$ equal panels. Compute $T(2)$ and $T(4)$, then form "
                              "the Richardson combination $\\frac{4T(4) - T(2)}{3}$. "
                              "The weights come from the trapezoid error being $O(h^2)$: halving $h$ "
                              "divides the error by four, so four of the fine estimate minus one of the "
                              "coarse one cancels the leading error, and dividing by three restores the "
                              "scale.",
                    "given": [
                        {"label": "Interval", "value": "$[1, 2]$"},
                        {"label": "Integrand", "value": "$f(x) = 1/x$"},
                        {"label": "Coarse", "value": "$T(2)$, panels of width $0.5$"},
                        {"label": "Fine", "value": "$T(4)$, panels of width $0.25$"},
                    ],
                    "aside": "$T(4)$ reuses all three nodes of $T(2)$ and adds two more, so the whole "
                             "calculation needs five function values, not seven.",
                    "answer": 0.693254,
                    "tol": 0.00002,
                    "unit": "",
                    "hint": "$T(2) = 0.5\\left[\\frac{f(1)}{2} + f(1.5) + \\frac{f(2)}{2}\\right]$ and "
                            "$T(4) = 0.25\\left[\\frac{f(1)}{2} + f(1.25) + f(1.5) + f(1.75) + "
                            "\\frac{f(2)}{2}\\right]$. Carry six decimals through both before combining.",
                    "wrong": "If you got $0.702679$ you averaged the two estimates instead of extrapolating "
                             "— the whole point is that the fine one is four times better and should count "
                             "for far more than half. If you got $2.079762$ the division by 3 was dropped, "
                             "and if you got $0.712103$ the coarse and fine estimates were swapped, which "
                             "extrapolates away from the answer instead of towards it.",
                    "why": r'''
```
T(2):  h = 0.5,  nodes 1, 1.5, 2
       = 0.5 * [ 0.500000 + 0.666667 + 0.250000 ]
       = 0.5 * 1.416667
       = 0.708333                (exactly 17/24)

T(4):  h = 0.25, nodes 1, 1.25, 1.5, 1.75, 2
       = 0.25 * [ 0.500000 + 0.800000 + 0.666667 + 0.571429 + 0.250000 ]
       = 0.25 * 2.788095
       = 0.697024                (exactly 1171/1680)

combination = (4 * 0.697024 - 0.708333) / 3
            = (2.788095 - 0.708333) / 3
            = 2.079762 / 3
            = 0.693254                (exactly 1747/2520)
```

Compare the three against $\ln 2 = 0.693147$: the errors are $+0.015186$, $+0.003877$
and $+0.000107$. The two trapezoid errors are in the ratio $3.92$, close to the $4$ the
$h^2$ theory demands, which is exactly why the extrapolation works — the leading errors
were in a known ratio and could be cancelled.

Now the part worth keeping. Composite Simpson on those same four panels gives
$0.693254$: the *same number*, digit for digit, and $\frac{1747}{2520}$ is what both
produce exactly. That is not a coincidence of this integrand. Algebraically,
$\frac{4T(2n) - T(n)}{3} = S(2n)$ for every $f$ and every $n$ — Simpson's rule *is*
Richardson extrapolation applied to the trapezoid rule, which is the same statement as
the third derivation in this module reaching Simpson from a weighted midpoint and
trapezoid. Three routes, one rule.
''',
                },
            ],
            "blanks": {
                "title": "The same limit, one power up",
                "minutes": 9,
                "caption": "the right-hand sum for the integral of x^3, line by line",
                "lang": "text",
                "brief": r'''
The derivation in this module took $\int_0^1 x^2\,\mathrm{d}x$ from the definition to
$\frac{1}{3}$. Here is the same argument on $x^3$, written out with the working steps
removed. Everything you need is in the listing except one power-sum identity, and the
options will tell you which one.

The point of doing it twice is the last two lines: the answer changes, and the *shape*
of the error does not.
''',
                "listing": """integral of x^3 from 0 to 1, by right-hand rectangles
----------------------------------------------------

  panel width      h    = 1/n

  right endpoint   x_i  = ___                  for i = 1, 2, ..., n

  one rectangle    area = h * f(x_i)
                        = (1/n) * (i/n)^3
                        = i^3 / n^4

  all of them      S_n  = (1/n^4) * sum(i^3, i = 1..n)

  and the closed form for that power sum is

                   sum(i^3, i = 1..n) = ___

  substitute       S_n  = (1/n^4) * n^2 (n+1)^2 / 4
                        = ___                  cancel n^2 top and bottom

  expand it        S_n  = ___                  a constant plus two decaying terms

  let n -> infinity      S_n -> ___            the tails die, the constant survives
""",
                "blanks": [
                    {
                        "prompt": "The right-hand endpoint of the $i$-th panel.",
                        "hole": "?",
                        "opts": ["i/n", "(i-1)/n", "(2i-1)/(2n)", "i"],
                        "a": 0,
                        "why": "Starting at $0$ and taking $i$ steps of width $1/n$ lands on $i/n$, and "
                               "at $i = n$ that is the right end of the interval as it should be. "
                               "$(i-1)/n$ is the *left* endpoint of the same panel and would give the left "
                               "sum; $(2i-1)/(2n)$ is its midpoint. All three are valid Riemann sums with "
                               "the same limit — they differ only in how fast they get there.",
                    },
                    {
                        "prompt": "The closed form for a sum of cubes.",
                        "hole": "?",
                        "opts": ["n(n+1)/2", "n(n+1)(2n+1)/6", "n^2 (n+1)^2 / 4", "n^4 / 4"],
                        "a": 2,
                        "why": "$\\sum i^3 = \\left(\\frac{n(n+1)}{2}\\right)^2 = \\frac{n^2(n+1)^2}{4}$ "
                               "— the square of the sum of the first $n$ integers, which is a small "
                               "miracle worth remembering. $n(n+1)/2$ is that sum itself and belongs to "
                               "$\\int x\\,\\mathrm{d}x$; $n(n+1)(2n+1)/6$ is the sum of squares and "
                               "belongs to $\\int x^2\\,\\mathrm{d}x$. $n^4/4$ is only the leading term, "
                               "and dropping the rest would throw away exactly the error we are trying "
                               "to measure.",
                    },
                    {
                        "prompt": "After cancelling, $S_n$ in lowest terms.",
                        "hole": "?",
                        "opts": ["(n+1)^2 / (4 n^2)", "(n+1)^2 / 4", "(n+1) / (4n)", "n^2 / (4 (n+1)^2)"],
                        "a": 0,
                        "why": "$\\frac{1}{n^4}\\cdot\\frac{n^2(n+1)^2}{4} = \\frac{(n+1)^2}{4n^2}$: the "
                               "$n^2$ on the top cancels two of the four on the bottom, leaving two. "
                               "Cancelling all four would give $(n+1)^2/4$, which grows without bound and "
                               "cannot be an area under a bounded curve — a quick sanity check that "
                               "catches this slip immediately.",
                    },
                    {
                        "prompt": "The same expression, expanded so the $n$-dependence is visible.",
                        "hole": "?",
                        "opts": ["1/4 + 1/(2n) + 1/(4n^2)",
                                 "1/4 + 1/n + 1/(4n^2)",
                                 "1/4 + 1/(4n) + 1/(4n^2)",
                                 "1/4 + 1/(2n)"],
                        "a": 0,
                        "why": "$(n+1)^2 = n^2 + 2n + 1$, and dividing each term by $4n^2$ gives "
                               "$\\frac{1}{4} + \\frac{2n}{4n^2} + \\frac{1}{4n^2} = "
                               "\\frac{1}{4} + \\frac{1}{2n} + \\frac{1}{4n^2}$. The middle term is the one "
                               "that decides everything: $\\frac{2}{4} = \\frac{1}{2}$, not $\\frac{1}{4}$ and "
                               "not $1$. Check it at $n = 4$ — the expansion gives "
                               "$0.25 + 0.125 + 0.015625 = 0.390625$, and summing the four rectangles "
                               "directly gives $0.25(0.015625 + 0.125 + 0.421875 + 1) = 0.390625$.",
                    },
                    {
                        "prompt": "The limit, and therefore the integral.",
                        "hole": "?",
                        "opts": ["1/3", "1/4", "1/2", "0"],
                        "a": 1,
                        "why": "Both tails vanish and $\\frac{1}{4}$ is left, so "
                               "$\\int_0^1 x^3\\,\\mathrm{d}x = \\frac{1}{4}$ — which is what "
                               "$\\left[\\frac{x^4}{4}\\right]_0^1$ gives, as it must. $\\frac{1}{3}$ is the "
                               "answer to the $x^2$ version of this derivation. The error left at finite "
                               "$n$ is $\\frac{1}{2n} + \\frac{1}{4n^2}$, dominated by $\\frac{1}{2n}$: "
                               "first order again, and the same leading coefficient as the $x^2$ case, "
                               "because the general prediction "
                               "$R_n - I \\approx \\frac{h}{2}\\left(f(b) - f(a)\\right)$ depends only on "
                               "the endpoint values, and both functions run from $0$ to $1$.",
                    },
                ],
            },
            "quiz": {
                "title": "Sums, rules and the orders they achieve",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The definition of $\\int_a^b f$ as a limit of Riemann sums requires that:",
                        "opts": [
                            "every choice of partition and of sample points gives the same limit as the mesh goes to zero",
                            "the left sum and the right sum agree for some finite $n$",
                            "the panels all have the same width",
                            "$f$ has an antiderivative that can be written in elementary functions",
                        ],
                        "a": 0,
                        "why": r'''
The integral is defined as a *common* limit: all partitions, all sample points, one
answer. Insisting that the sums agree at a finite $n$ would be far too strong — the
left and right sums for $x^2$ never agree at any $n$, they differ by $\frac1n$, yet the
integral exists. Equal panels are a convenience for computation, not part of the
definition, and the whole point of quadrature is that integrals exist for functions
like $e^{-x^2}$ with no elementary antiderivative.
''',
                    },
                    {
                        "q": "$f$ is increasing on $[a,b]$. What can be said about the left and right sums on $n$ equal panels?",
                        "opts": [
                            "$L_n \\le \\int_a^b f \\le R_n$",
                            "$R_n \\le \\int_a^b f \\le L_n$",
                            "both sums lie above the integral",
                            "nothing, without knowing the sign of $f''$",
                        ],
                        "a": 0,
                        "why": r'''
On an increasing $f$ the left endpoint of each panel is where $f$ is smallest on that
panel, so every left rectangle sits under the curve and $L_n$ underestimates; the right
endpoint is the largest value, so $R_n$ overestimates. Reverse $f$ to decreasing and
the bracket reverses with it, which is why the ordering with $R_n$ below is not
generally wrong — it is right for decreasing $f$ and wrong here. Curvature is not what
decides this; monotonicity is. For an $f$ that rises and then falls, neither sum need
bracket the integral at all.
''',
                    },
                    {
                        "q": "Simpson's rule integrates the parabola through three equally spaced points, yet it is exact for every cubic. Why?",
                        "opts": [
                            "the cubic part is odd about the middle node, so both the rule and the true integral return zero for it",
                            "every cubic restricted to a closed interval is also a parabola",
                            "the rule secretly uses four sample points, which is enough to pin down a cubic",
                            "it is exact only for cubics that happen to be symmetric about the middle node",
                        ],
                        "a": 0,
                        "why": r'''
Put the middle node at the origin. Then $\int_{-h}^{h}x^3\,\mathrm{d}x = 0$ by
symmetry, and the rule gives $\frac{h}{3}\left(-h^3 + 0 + h^3\right) = 0$ too. Since
the rule is already exact on $1$, $x$ and $x^2$, and every cubic is a combination of
those four powers, it is exact on all of them. It really does use three points, and no
cubic is a parabola. The symmetry argument works for every cubic once the middle node
is taken as the origin — no extra assumption is needed. This free order is why the
error term involves $f^{(4)}$ and the composite rule is $O(h^4)$.
''',
                    },
                    {
                        "q": "The composite trapezoid rule has error $O(h^2)$ on a smooth integrand. Halving $h$ therefore:",
                        "opts": [
                            "divides the error by about 4",
                            "divides the error by about 2",
                            "divides the error by about 16",
                            "leaves the error unchanged, and only costs more work",
                        ],
                        "a": 0,
                        "why": r'''
Order $p$ means the error behaves like $Ch^p$, so scaling $h$ by $\frac{1}{2}$ scales the
error by $\left(\frac{1}{2}\right)^p$. With $p = 2$ that is a factor of $4$. A factor of
$2$ would be first order — the left and right Riemann sums. A factor of $16$ is $p=4$,
which is Simpson. Running this backwards is the standard diagnostic: measure
$p = \log_2\left(E(n)/E(2n)\right)$ and see whether the rule is achieving the order it
claims.
''',
                    },
                    {
                        "q": "Per panel, the midpoint error is $+\\frac{h^3}{24}f''(\\xi)$ and the trapezoid error is $-\\frac{h^3}{12}f''(\\xi)$. What follows?",
                        "opts": [
                            "the midpoint rule is typically about twice as accurate, and errs on the opposite side",
                            "the midpoint rule is about twice as accurate, and errs on the same side",
                            "they are equally accurate, since both errors carry $h^3$",
                            "the trapezoid rule is twice as accurate, since it uses two function values per panel",
                        ],
                        "a": 0,
                        "why": r'''
Same power of $h$, so the same order — but the constants are $\frac{1}{24}$ against
$\frac{1}{12}$, a factor of two in the midpoint rule's favour, and the signs are
opposite. Equal orders do not mean equal accuracy; the constant is half the
information. Using more samples per panel does not automatically help either: the
trapezoid rule spends two evaluations to be twice as wrong as the midpoint rule's one.
Geometrically, for convex $f$ the chord lies above the curve while the midpoint
rectangle matches the tangent line below it. Cancelling the two errors against each
other is where Simpson comes from.
''',
                    },
                    {
                        "q": "You measure $p \\approx 1.5$ for the composite trapezoid rule on $\\int_0^1\\sqrt{x}\\,\\mathrm{d}x$, not the expected 2. The most likely explanation is:",
                        "opts": [
                            "$f''$ is unbounded at $x = 0$, so the hypothesis behind the $h^2$ error term fails",
                            "the rule has been implemented incorrectly",
                            "$n$ is too small; the true order appears once $n$ is large enough",
                            "rounding error dominates at these panel counts",
                        ],
                        "a": 0,
                        "why": r'''
$f(x) = \sqrt x$ has $f'' = -\frac{1}{4} x^{-3/2}$, which blows up at the left endpoint. The
error term $-\frac{(b-a)h^2}{12}f''(\xi)$ presumes a bounded $f''$, and without it the
theory says nothing. The measured $1.5$ is real and stable — it does not drift towards
$2$ as $n$ grows, so a too-small $n$ is not the cause, and a broken implementation
would not produce a clean, repeatable non-integer order. Rounding error only matters at
enormous $n$ and would make the order worse erratically, not settle it at exactly
$1.5$. Simpson also degrades to $1.5$ here, which is the giveaway: the fault is in the
integrand, not the rule. The cure is a substitution that removes the singularity.
''',
                    },
                    {
                        "q": "Refining a composite rule indefinitely in double-precision floating point:",
                        "opts": [
                            "eventually stops helping, because rounding error accumulates while the truncation error shrinks",
                            "always improves the answer, since the truncation error tends to zero",
                            "helps for Simpson's rule but not for the trapezoid rule",
                            "has no effect on the total error either way",
                        ],
                        "a": 0,
                        "why": r'''
Two errors are in play and they move in opposite directions. Truncation error falls
like $h^p$, but each of the $n$ additions carries a rounding error, and those grow
roughly like $\sqrt n$ times the machine epsilon. Their sum has a minimum, typically
near $n\sim10^{6}$ for a trapezoid rule in double precision, after which more panels
make the answer worse. Nothing about this favours one rule over another — but a
higher-order rule reaches its accuracy target at a far smaller $n$, so it hits the
target long before the floor becomes relevant. That is the practical reason to raise
the order rather than the panel count.
''',
                    },
                ],
            },
            "lab": {
                "title": "Quadrature rules and their error orders",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Implement the five classical rules on `n` equal panels of width `h = (b - a) / n`,
then *measure* the error order each one actually achieves.

**`left_sum(f, a, b, n)`**, **`right_sum(f, a, b, n)`**, **`midpoint_sum(f, a, b, n)`**
— the three Riemann sums, sampling each panel at its left edge, right edge and
centre respectively.

**`trapezoid(f, a, b, n)`** — `h * (f(a)/2 + f(x_1) + ... + f(x_{n-1}) + f(b)/2)`.

**`simpson(f, a, b, n)`** — the 1-4-2-4-...-4-1 pattern, scaled by `h / 3`.

All five raise `ValueError` for `n < 1`; `simpson` additionally raises for odd `n`,
because it consumes panels in pairs.

```text
f(x) = x**2 on [0, 1] with n = 4
left_sum      -> 0.21875
right_sum     -> 0.46875
midpoint_sum  -> 0.328125
trapezoid     -> 0.34375
simpson       -> 0.3333333333333333
```

**`observed_order(rule, f, a, b, exact, n)`** — the empirical convergence order

```text
p = log2( |rule(f,a,b,n) - exact| / |rule(f,a,b,2n) - exact| )
```

Return `math.inf` when the finer error is exactly zero (the rule is exact for
that integrand, as Simpson is for any cubic).

Nothing here depends on the sign of `b - a`: with `b < a` the width `h` is
negative and every rule returns the negated integral automatically.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def left_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its left edge."""
    # your code here


def right_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its right edge."""
    # your code here


def midpoint_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its centre."""
    # your code here


def trapezoid(f, a, b, n):
    """Composite trapezoid rule on n panels."""
    # your code here


def simpson(f, a, b, n):
    """Composite Simpson rule; n must be even and at least 2."""
    # your code here


def observed_order(rule, f, a, b, exact, n):
    """log2 of the error ratio between n panels and 2n panels."""
    # your code here


print(trapezoid(lambda x: x * x, 0.0, 1.0, 4))
print(simpson(math.exp, 0.0, 1.0, 100))
print(observed_order(simpson, math.exp, 0.0, 1.0, math.e - 1.0, 32))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def left_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its left edge."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    return h * sum(f(a + i * h) for i in range(n))


def right_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its right edge."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    return h * sum(f(a + i * h) for i in range(1, n + 1))


def midpoint_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its centre."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    return h * sum(f(a + (i + 0.5) * h) for i in range(n))


def trapezoid(f, a, b, n):
    """Composite trapezoid rule on n panels."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return h * total


def simpson(f, a, b, n):
    """Composite Simpson rule; n must be even and at least 2."""
    if n < 2 or n % 2 != 0:
        raise ValueError("n must be an even integer of at least 2")
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 == 1 else 2) * f(a + i * h)
    return h * total / 3.0


def observed_order(rule, f, a, b, exact, n):
    """log2 of the error ratio between n panels and 2n panels."""
    coarse = abs(rule(f, a, b, n) - exact)
    fine = abs(rule(f, a, b, 2 * n) - exact)
    if fine == 0.0:
        return math.inf
    return math.log2(coarse / fine)


print(trapezoid(lambda x: x * x, 0.0, 1.0, 4))
print(simpson(math.exp, 0.0, 1.0, 100))
print(observed_order(simpson, math.exp, 0.0, 1.0, math.e - 1.0, 32))
'''}],
                "hints": [
                    "Compute `h = (b - a) / n` once, then the sample points are `a + i * h`. The left sum uses `i` from 0 to n-1, the right sum 1 to n, the midpoint `a + (i + 0.5) * h`.",
                    "Trapezoid: start the accumulator at `0.5 * (f(a) + f(b))`, add every interior point at full weight, and multiply by `h` at the end.",
                    "Simpson's weights alternate: interior index `i` gets 4 when `i` is odd and 2 when it is even. `(4 if i % 2 == 1 else 2)` inside the loop is the whole trick.",
                    "`observed_order` must guard against a zero denominator *before* calling `math.log2` — a rule that is exact at 2n panels has infinite observed order.",
                ],
                "tests": [
                    {"name": "The three Riemann sums on x^2", "code": r'''
_f = lambda x: x * x
for _name, _rule, _want in [("left_sum", left_sum, 0.21875),
                            ("right_sum", right_sum, 0.46875),
                            ("midpoint_sum", midpoint_sum, 0.328125)]:
    _got = _rule(_f, 0.0, 1.0, 4)
    assert abs(_got - _want) < 1e-12, f"{_name}(x^2, 0, 1, 4) gave {_got!r}, expected {_want}"
_got = left_sum(_f, 0.0, 1.0, 1)
assert abs(_got - 0.0) < 1e-12, f"left_sum with n=1 gave {_got!r}, expected 0.0"
_got = midpoint_sum(_f, 0.0, 1.0, 1)
assert abs(_got - 0.25) < 1e-12, f"midpoint_sum with n=1 gave {_got!r}, expected 0.25"
'''},
                    {"name": "Trapezoid is the mean of left and right", "code": r'''
_f = lambda x: math.exp(-x) + x ** 3
for _n in (1, 3, 7, 20):
    _mean = 0.5 * (left_sum(_f, 0.0, 2.0, _n) + right_sum(_f, 0.0, 2.0, _n))
    _got = trapezoid(_f, 0.0, 2.0, _n)
    assert abs(_got - _mean) < 1e-12, \
        f"trapezoid(n={_n}) gave {_got!r}, but (left+right)/2 is {_mean!r}"
_got = trapezoid(lambda x: 2.0 * x + 1.0, 0.0, 3.0, 3)
assert abs(_got - 12.0) < 1e-12, f"trapezoid is exact on straight lines; got {_got!r}, expected 12.0"
'''},
                    {"name": "Simpson is exact for cubics", "code": r'''
_got = simpson(lambda x: x ** 3, 0.0, 1.0, 2)
assert abs(_got - 0.25) < 1e-14, f"simpson(x^3, 0, 1, 2) gave {_got!r}, expected 0.25"
_got = simpson(lambda x: 4.0 * x ** 3 - 3.0 * x + 5.0, -1.0, 2.0, 4)
assert abs(_got - 25.5) < 1e-12, f"simpson on a cubic gave {_got!r}, expected 25.5"
_got = simpson(lambda x: x * x, 0.0, 1.0, 4)
assert abs(_got - 1.0 / 3.0) < 1e-14, f"simpson(x^2, 0, 1, 4) gave {_got!r}, expected 1/3"
'''},
                    {"name": "Bad panel counts are refused", "code": r'''
for _name, _rule in [("left_sum", left_sum), ("right_sum", right_sum),
                     ("midpoint_sum", midpoint_sum), ("trapezoid", trapezoid),
                     ("simpson", simpson)]:
    for _bad in (0, -1, -8):
        try:
            _rule(math.sin, 0.0, 1.0, _bad)
            assert False, f"{_name} with n={_bad} should raise ValueError"
        except ValueError:
            pass
for _odd in (1, 3, 15):
    try:
        simpson(math.sin, 0.0, 1.0, _odd)
        assert False, f"simpson with n={_odd} should raise ValueError (odd panel count)"
    except ValueError:
        pass
'''},
                    {"name": "Refinement really does converge", "code": r'''
_exact = math.e - 1.0
_e_trap = abs(trapezoid(math.exp, 0.0, 1.0, 1000) - _exact)
assert _e_trap < 1e-6, f"trapezoid with n=1000 was off by {_e_trap!r}, expected under 1e-6"
_e_mid = abs(midpoint_sum(math.exp, 0.0, 1.0, 1000) - _exact)
assert _e_mid < 1e-6, f"midpoint_sum with n=1000 was off by {_e_mid!r}, expected under 1e-6"
_e_simp = abs(simpson(math.exp, 0.0, 1.0, 100) - _exact)
assert _e_simp < 1e-9, f"simpson with n=100 was off by {_e_simp!r}, expected under 1e-9"
'''},
                    {"name": "Observed orders match the theory", "code": r'''
_exact = math.e - 1.0
for _name, _rule, _want in [("left_sum", left_sum, 1.0), ("right_sum", right_sum, 1.0),
                            ("midpoint_sum", midpoint_sum, 2.0), ("trapezoid", trapezoid, 2.0)]:
    _p = observed_order(_rule, math.exp, 0.0, 1.0, _exact, 64)
    assert abs(_p - _want) < 0.05, f"observed_order for {_name} gave {_p!r}, expected about {_want}"
_p = observed_order(simpson, math.exp, 0.0, 1.0, _exact, 32)
assert abs(_p - 4.0) < 0.05, f"observed_order for simpson gave {_p!r}, expected about 4.0"
'''},
                    {"name": "An exact rule has infinite order", "code": r'''
_p = observed_order(simpson, lambda x: x ** 3, 0.0, 1.0, 0.25, 4)
assert _p == math.inf, f"observed_order gave {_p!r}; a zero fine error should give math.inf"
'''},
                    {"name": "A reversed interval flips the sign", "code": r'''
for _name, _rule in [("trapezoid", trapezoid), ("midpoint_sum", midpoint_sum)]:
    _fwd = _rule(math.sin, 0.0, math.pi, 8)
    _bwd = _rule(math.sin, math.pi, 0.0, 8)
    assert abs(_fwd + _bwd) < 1e-12, \
        f"{_name} over [pi, 0] gave {_bwd!r}, expected the negation of {_fwd!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Adaptive quadrature and improper integrals",
            "summary": "Spending effort where the integrand is difficult, and taming infinite domains.",
            "concepts": [
                "A fixed panel count wastes work on smooth stretches and starves the hard ones",
                "Richardson extrapolation: comparing S(a,b) with S(a,c)+S(c,b) estimates the error",
                "The 1/15 factor comes from Simpson's h^4 order — halving h divides the error by 16",
                "Recursive bisection with a per-half tolerance of tol/2 keeps the global budget",
                "A depth limit is mandatory: a singularity would otherwise recurse forever",
                "Improper integrals of the first kind (infinite limit) yield to x = a + t/(1-t)",
                "Improper integrals of the second kind (endpoint blow-up) often yield to x = a + u^2",
            ],
            "lab": {
                "title": "Adaptive Simpson to a requested tolerance",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
## Adaptive Simpson

**`adaptive_simpson(f, a, b, tol, max_depth=30)`**

One Simpson panel over `[a, b]` is `(b - a) / 6 * (f(a) + 4 f(m) + f(b))` with
`m` the midpoint. Split the interval, compute the two half panels, and compare:

```text
delta = left + right - whole
```

Accept `left + right + delta / 15` when `abs(delta) <= 15 * tol` or the depth
budget is exhausted; otherwise recurse into each half with tolerance `tol / 2`.

`tol <= 0` raises `ValueError`. `a == b` returns `0.0`. `b < a` returns the
negation of the forward integral.

## Improper integrals

Each of the three below rewrites the integral as a proper one over a finite
interval and then calls `adaptive_simpson`. The substituted integrand is only
*removably* singular at the endpoint, so clamp the variable to `CLAMP = 1e-12`
away from it rather than evaluating the limit symbolically.

**`integrate_to_infinity(f, a, tol)`** — with `x = a + t/(1-t)` and
`dx = dt/(1-t)^2`,

```text
∫[a, ∞) f(x) dx  =  ∫[0, 1) f(a + t/(1-t)) / (1-t)^2 dt
```

**`integrate_real_line(f, tol)`** — split at 0 and reflect: the left half is
`integrate_to_infinity(lambda x: f(-x), 0, tol/2)`.

**`integrate_endpoint_singular(f, a, b, tol)`** — for an integrable blow-up at
`a`, substitute `x = a + u^2`, `dx = 2u du`:

```text
∫[a, b] f(x) dx  =  ∫[0, sqrt(b-a)] 2u f(a + u^2) du
```

The factor `2u` is exactly what kills a `1/sqrt(x - a)` singularity. Raise
`ValueError` unless `a < b`.

```text
integrate_to_infinity(lambda x: math.exp(-x), 0.0, 1e-10)      -> 1.0
integrate_real_line(lambda x: math.exp(-x*x), 1e-10)           -> sqrt(pi)
integrate_endpoint_singular(lambda x: 1/math.sqrt(x), 0, 1, 1e-10) -> 2.0
```
''',
                "files": [{"name": "main.py", "content": r'''
import math

CLAMP = 1e-12


def _panel(f, a, b):
    """One Simpson panel over [a, b]."""
    # your code here


def adaptive_simpson(f, a, b, tol, max_depth=30):
    """Recursive Simpson refinement to an absolute tolerance."""
    # your code here


def integrate_to_infinity(f, a, tol):
    """Integral of f from a to +infinity, via x = a + t/(1-t)."""
    # your code here


def integrate_real_line(f, tol):
    """Integral of f over the whole real line."""
    # your code here


def integrate_endpoint_singular(f, a, b, tol):
    """Integral of f over [a, b] with an integrable singularity at a."""
    # your code here


print(adaptive_simpson(math.sin, 0.0, math.pi, 1e-10))
print(integrate_real_line(lambda x: math.exp(-x * x), 1e-10))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

CLAMP = 1e-12


def _panel(f, a, b):
    """One Simpson panel over [a, b]."""
    c = 0.5 * (a + b)
    return (b - a) / 6.0 * (f(a) + 4.0 * f(c) + f(b))


def _refine(f, a, b, tol, whole, depth):
    """Bisect until the Richardson estimate of the panel error is small enough."""
    c = 0.5 * (a + b)
    left = _panel(f, a, c)
    right = _panel(f, c, b)
    delta = left + right - whole
    if depth <= 0 or abs(delta) <= 15.0 * tol:
        return left + right + delta / 15.0
    return (_refine(f, a, c, tol / 2.0, left, depth - 1)
            + _refine(f, c, b, tol / 2.0, right, depth - 1))


def adaptive_simpson(f, a, b, tol, max_depth=30):
    """Recursive Simpson refinement to an absolute tolerance."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    if a == b:
        return 0.0
    if b < a:
        return -adaptive_simpson(f, b, a, tol, max_depth)
    return _refine(f, a, b, tol, _panel(f, a, b), max_depth)


def integrate_to_infinity(f, a, tol):
    """Integral of f from a to +infinity, via x = a + t/(1-t)."""
    def g(t):
        u = 1.0 - t
        if u < CLAMP:
            u = CLAMP
        return f(a + (1.0 - u) / u) / (u * u)
    return adaptive_simpson(g, 0.0, 1.0, tol)


def integrate_real_line(f, tol):
    """Integral of f over the whole real line."""
    return (integrate_to_infinity(f, 0.0, tol / 2.0)
            + integrate_to_infinity(lambda x: f(-x), 0.0, tol / 2.0))


def integrate_endpoint_singular(f, a, b, tol):
    """Integral of f over [a, b] with an integrable singularity at a."""
    if b <= a:
        raise ValueError("need a < b")

    def g(u):
        if u < CLAMP:
            u = CLAMP
        return 2.0 * u * f(a + u * u)
    return adaptive_simpson(g, 0.0, math.sqrt(b - a), tol)


print(adaptive_simpson(math.sin, 0.0, math.pi, 1e-10))
print(integrate_real_line(lambda x: math.exp(-x * x), 1e-10))
'''}],
                "hints": [
                    "Put the recursion in a helper that already knows the value of the whole panel, so no point is ever evaluated twice for the same reason: `_refine(f, a, b, tol, whole, depth)`.",
                    "The accepted value is `left + right + delta / 15`, not `left + right` — that extra term is the Richardson correction and it buys you two extra orders for free.",
                    "For the infinite tail, work with `u = 1 - t` so the clamp is a single `if u < CLAMP: u = CLAMP`, and then `x = a + (1 - u) / u` and the Jacobian is `1 / u**2`.",
                    "`integrate_endpoint_singular` needs no clamp for `1/sqrt(x)` — `2u * f(u**2)` is the constant 2 — but `log` still needs one, so keep it.",
                ],
                "tests": [
                    {"name": "Proper integrals to ten digits", "code": r'''
for _name, _f, _a, _b, _want in [("sin on [0, pi]", math.sin, 0.0, math.pi, 2.0),
                                 ("exp on [0, 1]", math.exp, 0.0, 1.0, math.e - 1.0),
                                 ("x^3 on [0, 1]", lambda x: x ** 3, 0.0, 1.0, 0.25)]:
    _got = adaptive_simpson(_f, _a, _b, 1e-10)
    assert abs(_got - _want) < 1e-9, f"adaptive_simpson({_name}) gave {_got!r}, expected {_want!r}"
_got = adaptive_simpson(lambda x: 1.0 / (1.0 + 25.0 * x * x), -1.0, 1.0, 1e-10)
_want = 2.0 * math.atan(5.0) / 5.0
assert abs(_got - _want) < 1e-9, f"Runge integral gave {_got!r}, expected {_want!r}"
'''},
                    {"name": "Degenerate and reversed intervals", "code": r'''
_got = adaptive_simpson(math.sin, 1.0, 1.0, 1e-10)
assert _got == 0.0, f"adaptive_simpson over an empty interval gave {_got!r}, expected 0.0"
_fwd = adaptive_simpson(math.sin, 0.0, math.pi, 1e-10)
_bwd = adaptive_simpson(math.sin, math.pi, 0.0, 1e-10)
assert abs(_fwd + _bwd) < 1e-12, f"Reversed limits gave {_bwd!r}, expected the negation of {_fwd!r}"
'''},
                    {"name": "A non-positive tolerance is refused", "code": r'''
for _bad in (0.0, -1e-6, -3.0):
    try:
        adaptive_simpson(math.sin, 0.0, 1.0, _bad)
        assert False, f"adaptive_simpson with tol={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The tolerance is actually honoured", "code": r'''
_exact = math.e - 1.0
_loose = abs(adaptive_simpson(math.exp, 0.0, 1.0, 1e-3) - _exact)
_tight = abs(adaptive_simpson(math.exp, 0.0, 1.0, 1e-12) - _exact)
assert _loose < 1e-3, f"tol=1e-3 left an error of {_loose!r}"
assert _tight < 1e-11, f"tol=1e-12 left an error of {_tight!r}"
assert _tight <= _loose, f"Tightening the tolerance made things worse: {_tight!r} vs {_loose!r}"
'''},
                    {"name": "Infinite upper limit", "code": r'''
for _name, _f, _a, _want in [("exp(-x) from 0", lambda x: math.exp(-x), 0.0, 1.0),
                             ("1/(1+x^2) from 0", lambda x: 1.0 / (1.0 + x * x), 0.0, math.pi / 2.0),
                             ("x^2 exp(-x) from 0", lambda x: x * x * math.exp(-x), 0.0, 2.0),
                             ("x^-3 from 1", lambda x: x ** -3.0, 1.0, 0.5)]:
    _got = integrate_to_infinity(_f, _a, 1e-10)
    assert abs(_got - _want) < 1e-8, f"integrate_to_infinity({_name}) gave {_got!r}, expected {_want!r}"
'''},
                    {"name": "The whole real line", "code": r'''
_got = integrate_real_line(lambda x: math.exp(-x * x), 1e-10)
assert abs(_got - math.sqrt(math.pi)) < 1e-8, \
    f"Gaussian integral gave {_got!r}, expected {math.sqrt(math.pi)!r}"
_got = integrate_real_line(lambda x: 1.0 / (1.0 + x * x), 1e-10)
assert abs(_got - math.pi) < 1e-8, f"Cauchy integral gave {_got!r}, expected {math.pi!r}"
'''},
                    {"name": "Endpoint singularities", "code": r'''
_got = integrate_endpoint_singular(lambda x: 1.0 / math.sqrt(x), 0.0, 1.0, 1e-10)
assert abs(_got - 2.0) < 1e-9, f"Integral of x^-1/2 over [0, 1] gave {_got!r}, expected 2.0"
_got = integrate_endpoint_singular(math.log, 0.0, 1.0, 1e-10)
assert abs(_got + 1.0) < 1e-8, f"Integral of log over [0, 1] gave {_got!r}, expected -1.0"
_got = integrate_endpoint_singular(lambda x: x * x, 0.0, 1.0, 1e-10)
assert abs(_got - 1.0 / 3.0) < 1e-9, \
    f"The substitution must also work on smooth integrands; got {_got!r}, expected 1/3"
for _bad in [(1.0, 1.0), (2.0, 1.0)]:
    try:
        integrate_endpoint_singular(math.log, _bad[0], _bad[1], 1e-8)
        assert False, f"integrate_endpoint_singular{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Taylor and Maclaurin series",
            "summary": "Replacing a function by a polynomial, and knowing exactly what that costs.",
            "concepts": [
                "The Taylor coefficient c_k = f^(k)(a) / k!, and the Maclaurin case a = 0",
                "Maclaurin series for exp, sin and cos, and the parity that zeroes half their coefficients",
                "Horner evaluation costs n multiplications and is far better conditioned than powers",
                "Taylor's theorem with Lagrange remainder: R_n(x) = f^(n+1)(c) x^(n+1) / (n+1)!",
                "Bounding the remainder means bounding the derivative on the interval, not at a point",
                "Factorial growth beats any fixed power, so exp/sin/cos converge for every x",
                "Catastrophic cancellation: exp(-20) by Maclaurin series loses every significant digit",
            ],
            "lab": {
                "title": "Series coefficients and the Lagrange remainder",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Work with `kind` drawn from `"exp"`, `"sin"`, `"cos"`. Anything else raises
`ValueError`, as does a negative `n`.

**`taylor_coefficients(kind, n)`** — the Maclaurin coefficients `c_0 .. c_n`
as a list of `n + 1` floats.

```text
taylor_coefficients("exp", 4)  ->  [1.0, 1.0, 0.5, 1/6, 1/24]
taylor_coefficients("sin", 5)  ->  [0.0, 1.0, 0.0, -1/6, 0.0, 1/120]
taylor_coefficients("cos", 5)  ->  [1.0, 0.0, -0.5, 0.0, 1/24, 0.0]
```

**`evaluate(coeffs, x)`** — Horner's scheme: start from the last coefficient
and repeatedly multiply by `x` and add the next one down. An empty list raises
`ValueError`.

**`remainder_bound(kind, x, n)`** — the Lagrange bound on `|f(x) - P_n(x)|`:

```text
M * |x|^(n+1) / (n+1)!
```

where `M` bounds `|f^(n+1)|` between 0 and `x`. Every derivative of sin and cos
is bounded by 1; for exp the largest value on that interval is `exp(|x|)`.

```text
remainder_bound("sin", 0.5, 3)  ->  0.0026041666666666665
remainder_bound("exp", 1.0, 5)  ->  0.0037753914284153404
```

**`terms_for_tolerance(kind, x, tol, max_n=400)`** — the smallest `n` whose
remainder bound is `<= tol`. `tol <= 0` raises `ValueError`, and so does a
tolerance still unreached at `max_n`.

```text
terms_for_tolerance("sin", 1.0, 1e-6)   ->  9
terms_for_tolerance("cos", 0.5, 1e-12)  ->  11
```
''',
                "files": [{"name": "main.py", "content": r'''
import math

KINDS = ("exp", "sin", "cos")


def taylor_coefficients(kind, n):
    """Maclaurin coefficients c_0 .. c_n for exp, sin or cos."""
    # your code here


def evaluate(coeffs, x):
    """Evaluate the polynomial with these coefficients at x, by Horner."""
    # your code here


def remainder_bound(kind, x, n):
    """Lagrange bound on the error of the degree-n Maclaurin polynomial at x."""
    # your code here


def terms_for_tolerance(kind, x, tol, max_n=400):
    """Smallest n whose remainder bound at x is at most tol."""
    # your code here


print(taylor_coefficients("cos", 6))
print(evaluate(taylor_coefficients("exp", 20), 1.0), math.e)
print(terms_for_tolerance("sin", 1.0, 1e-6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

KINDS = ("exp", "sin", "cos")


def taylor_coefficients(kind, n):
    """Maclaurin coefficients c_0 .. c_n for exp, sin or cos."""
    if kind not in KINDS:
        raise ValueError("kind must be one of exp, sin, cos")
    if n < 0:
        raise ValueError("n must not be negative")
    coeffs = []
    for k in range(n + 1):
        if kind == "exp":
            coeffs.append(1.0 / math.factorial(k))
        elif kind == "sin":
            if k % 2 == 0:
                coeffs.append(0.0)
            else:
                coeffs.append((-1.0) ** ((k - 1) // 2) / math.factorial(k))
        else:
            if k % 2 == 1:
                coeffs.append(0.0)
            else:
                coeffs.append((-1.0) ** (k // 2) / math.factorial(k))
    return coeffs


def evaluate(coeffs, x):
    """Evaluate the polynomial with these coefficients at x, by Horner."""
    if not coeffs:
        raise ValueError("need at least one coefficient")
    total = 0.0
    for c in reversed(coeffs):
        total = total * x + c
    return total


def remainder_bound(kind, x, n):
    """Lagrange bound on the error of the degree-n Maclaurin polynomial at x."""
    if kind not in KINDS:
        raise ValueError("kind must be one of exp, sin, cos")
    if n < 0:
        raise ValueError("n must not be negative")
    m = math.exp(abs(x)) if kind == "exp" else 1.0
    return m * abs(x) ** (n + 1) / math.factorial(n + 1)


def terms_for_tolerance(kind, x, tol, max_n=400):
    """Smallest n whose remainder bound at x is at most tol."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    for n in range(max_n + 1):
        if remainder_bound(kind, x, n) <= tol:
            return n
    raise ValueError("tolerance not reachable below max_n")


print(taylor_coefficients("cos", 6))
print(evaluate(taylor_coefficients("exp", 20), 1.0), math.e)
print(terms_for_tolerance("sin", 1.0, 1e-6))
'''}],
                "hints": [
                    "Validate `kind` and `n` first; every one of these functions shares the same two guards.",
                    "For sin, only odd k survives and the sign alternates with `(k - 1) // 2`; for cos only even k survives, alternating with `k // 2`.",
                    "Horner is three lines: `total = 0.0`, then `for c in reversed(coeffs): total = total * x + c`, then return.",
                    "`terms_for_tolerance` is a linear search over n calling `remainder_bound` — do not re-derive the factorial by hand.",
                ],
                "tests": [
                    {"name": "Coefficients for the three kinds", "code": r'''
_got = taylor_coefficients("exp", 4)
_want = [1.0, 1.0, 0.5, 1.0 / 6.0, 1.0 / 24.0]
assert len(_got) == 5, f"taylor_coefficients('exp', 4) gave {len(_got)} entries, expected 5"
for _i, (_g, _w) in enumerate(zip(_got, _want)):
    assert abs(_g - _w) < 1e-15, f"exp coefficient {_i} is {_g!r}, expected {_w!r}"
_got = taylor_coefficients("sin", 5)
_want = [0.0, 1.0, 0.0, -1.0 / 6.0, 0.0, 1.0 / 120.0]
for _i, (_g, _w) in enumerate(zip(_got, _want)):
    assert abs(_g - _w) < 1e-15, f"sin coefficient {_i} is {_g!r}, expected {_w!r}"
_got = taylor_coefficients("cos", 5)
_want = [1.0, 0.0, -0.5, 0.0, 1.0 / 24.0, 0.0]
for _i, (_g, _w) in enumerate(zip(_got, _want)):
    assert abs(_g - _w) < 1e-15, f"cos coefficient {_i} is {_g!r}, expected {_w!r}"
'''},
                    {"name": "Degree zero and bad arguments", "code": r'''
assert taylor_coefficients("exp", 0) == [1.0], f"Got {taylor_coefficients('exp', 0)!r}, expected [1.0]"
assert taylor_coefficients("sin", 0) == [0.0], f"Got {taylor_coefficients('sin', 0)!r}, expected [0.0]"
for _args in [("tan", 3), ("EXP", 3), ("exp", -1), ("sin", -4)]:
    try:
        taylor_coefficients(*_args)
        assert False, f"taylor_coefficients{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Horner evaluation", "code": r'''
_got = evaluate([5.0], 12.0)
assert _got == 5.0, f"A constant polynomial gave {_got!r}, expected 5.0"
_got = evaluate([1.0, -2.0, 3.0], 2.0)
assert abs(_got - 9.0) < 1e-12, f"1 - 2x + 3x^2 at x=2 gave {_got!r}, expected 9.0"
_got = evaluate([1.0, 1.0, 0.5], 0.0)
assert _got == 1.0, f"Any polynomial at x=0 is its constant term; got {_got!r}"
try:
    evaluate([], 1.0)
    assert False, "evaluate([], 1.0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The polynomials really approximate", "code": r'''
for _kind, _fn, _n, _x in [("exp", math.exp, 20, 1.0), ("exp", math.exp, 25, -2.0),
                           ("sin", math.sin, 15, 0.7), ("sin", math.sin, 25, 3.0),
                           ("cos", math.cos, 25, 2.0), ("cos", math.cos, 10, -0.4)]:
    _got = evaluate(taylor_coefficients(_kind, _n), _x)
    _want = _fn(_x)
    assert abs(_got - _want) < 1e-10, \
        f"{_kind} series of degree {_n} at {_x} gave {_got!r}, expected {_want!r}"
'''},
                    {"name": "Known remainder bounds", "code": r'''
_got = remainder_bound("sin", 0.5, 3)
_want = 0.5 ** 4 / 24.0
assert abs(_got - _want) < 1e-18, f"remainder_bound('sin', 0.5, 3) gave {_got!r}, expected {_want!r}"
_got = remainder_bound("exp", 1.0, 5)
_want = math.e / 720.0
assert abs(_got - _want) < 1e-15, f"remainder_bound('exp', 1.0, 5) gave {_got!r}, expected {_want!r}"
assert remainder_bound("cos", 0.0, 0) == 0.0, "At x=0 the remainder bound is exactly 0"
for _args in [("tan", 1.0, 3), ("sin", 1.0, -1)]:
    try:
        remainder_bound(*_args)
        assert False, f"remainder_bound{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The bound is never violated", "code": r'''
for _kind, _fn in [("exp", math.exp), ("sin", math.sin), ("cos", math.cos)]:
    for _x in (-2.0, -0.3, 0.0, 0.75, 3.0):
        for _n in (2, 5, 9, 14):
            _err = abs(evaluate(taylor_coefficients(_kind, _n), _x) - _fn(_x))
            _bound = remainder_bound(_kind, _x, _n)
            assert _err <= _bound + 1e-14, \
                f"{_kind} at x={_x}, n={_n}: error {_err!r} exceeds the bound {_bound!r}"
'''},
                    {"name": "terms_for_tolerance is the smallest such n", "code": r'''
for _kind, _x, _tol, _want in [("sin", 1.0, 1e-6, 9), ("exp", 1.0, 1e-6, 9),
                               ("cos", 0.5, 1e-12, 11), ("exp", 0.0, 1e-12, 0)]:
    _got = terms_for_tolerance(_kind, _x, _tol)
    assert _got == _want, f"terms_for_tolerance({_kind!r}, {_x}, {_tol}) gave {_got!r}, expected {_want}"
    assert remainder_bound(_kind, _x, _got) <= _tol, "The returned n must satisfy the tolerance"
    if _got > 0:
        assert remainder_bound(_kind, _x, _got - 1) > _tol, "n-1 must NOT satisfy it"
for _bad in (0.0, -1e-9):
    try:
        terms_for_tolerance("sin", 1.0, _bad)
        assert False, f"terms_for_tolerance with tol={_bad} should raise ValueError"
    except ValueError:
        pass
try:
    terms_for_tolerance("exp", 5.0, 1e-9, max_n=3)
    assert False, "An unreachable tolerance within max_n should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Sequences, series and convergence tests",
            "summary": "Deciding whether an infinite sum exists, and pinning down its value.",
            "concepts": [
                "A series converges exactly when its sequence of partial sums converges",
                "The n-th term test is necessary, not sufficient — the harmonic series is the counterexample",
                "Ratio test: L < 1 converges absolutely, L > 1 diverges, L = 1 says nothing",
                "Numerically the ratio approaches its limit like L + c/n, so extrapolate with 2r(2n) - r(n)",
                "Integral test: for f positive and decreasing, the tail is squeezed between two integrals",
                "That squeeze is a computable error bar, which is what makes the test practically useful",
                "Radius of convergence R = 1/limsup |c_n|^(1/n), estimated from consecutive non-zero coefficients",
            ],
            "lab": {
                "title": "Convergence tests and the radius of convergence",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Throughout, `term(k)` supplies the k-th term of a series indexed from `k = 1`.

**`partial_sums(term, n)`** — the list `[S_1, S_2, ..., S_n]`. `n < 1` raises
`ValueError`.

```text
partial_sums(lambda k: 0.5 ** k, 3)  ->  [0.5, 0.75, 0.875]
```

**`ratio_test(term, n=200)`** — returns `(verdict, limit)`. Estimate the ratio
`r(m) = abs(term(m+1) / term(m))` at `m = n` and `m = 2n`, then extrapolate:

```text
limit = max(0.0, 2 * r(2n) - r(n))
```

`verdict` is `"converges"` below `1 - 1e-3`, `"diverges"` above `1 + 1e-3`, and
`"inconclusive"` in between. A zero term makes the ratio undefined — raise
`ValueError`. `n < 1` also raises.

```text
ratio_test(lambda k: 0.5 ** k)      ->  ("converges", 0.5)
ratio_test(lambda k: 1.0 / k ** 2)  ->  ("inconclusive", ~1.0)
ratio_test(lambda k: 2.0 ** k)      ->  ("diverges", 2.0)
```

**`estimate_sum(term, tail_integral, tol, max_terms=200000)`** — the integral
test turned into an answer with an error bar. `tail_integral(x)` supplies the
exact value of the improper integral of the underlying positive decreasing `f`
from `x` to infinity. After summing `n` terms,

```text
tail_integral(n+1)  <=  sum of the remaining terms  <=  tail_integral(n)
```

so take the midpoint of that bracket and half its width. Grow `n` until the
half-width is `<= tol`, then return `(estimate, half_width, n)`. `tol <= 0`
raises, and so does exhausting `max_terms`.

```text
estimate_sum(lambda k: 1/k**2, lambda x: 1/x, 1e-6)  ->  (~1.6449340678, ~1e-6, 707)
```

**`radius_of_convergence(coeff, n_max=60)`** — `coeff(k)` gives the k-th power
series coefficient. Define one estimate from the last two non-zero indices
`n < m` at or below a cut-off:

```text
rho = (abs(coeff(m)) / abs(coeff(n))) ** (1 / (m - n)),   R = 1 / rho
```

Compute `R_full` at `n_max` and `R_half` at `n_max // 2`. Return `math.inf`
when `R_full >= 1.9 * R_half` (shrinking faster than any geometric rate),
`0.0` when `R_full <= 0.55 * R_half`, and `R_full` otherwise. Fewer than two
non-zero coefficients at either cut-off raises `ValueError`.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def partial_sums(term, n):
    """[S_1, ..., S_n] for a series indexed from k = 1."""
    # your code here


def ratio_test(term, n=200):
    """(verdict, extrapolated ratio limit) for the ratio test."""
    # your code here


def estimate_sum(term, tail_integral, tol, max_terms=200000):
    """(estimate, half_width, terms_used) from the integral-test bracket."""
    # your code here


def radius_of_convergence(coeff, n_max=60):
    """Estimated radius of convergence of the power series with these coefficients."""
    # your code here


print(partial_sums(lambda k: 1.0 / k, 4))
print(ratio_test(lambda k: 0.5 ** k))
print(estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def partial_sums(term, n):
    """[S_1, ..., S_n] for a series indexed from k = 1."""
    if n < 1:
        raise ValueError("n must be at least 1")
    sums = []
    total = 0.0
    for k in range(1, n + 1):
        total += term(k)
        sums.append(total)
    return sums


def ratio_test(term, n=200):
    """(verdict, extrapolated ratio limit) for the ratio test."""
    if n < 1:
        raise ValueError("n must be at least 1")

    def ratio(m):
        below = term(m)
        if below == 0:
            raise ValueError("the ratio test needs non-zero terms")
        return abs(term(m + 1) / below)

    limit = 2.0 * ratio(2 * n) - ratio(n)
    if limit < 0.0:
        limit = 0.0
    if limit < 1.0 - 1e-3:
        return ("converges", limit)
    if limit > 1.0 + 1e-3:
        return ("diverges", limit)
    return ("inconclusive", limit)


def estimate_sum(term, tail_integral, tol, max_terms=200000):
    """(estimate, half_width, terms_used) from the integral-test bracket."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    total = 0.0
    for n in range(1, max_terms + 1):
        total += term(n)
        upper = tail_integral(n)
        lower = tail_integral(n + 1)
        half = 0.5 * (upper - lower)
        if half <= tol:
            return (total + 0.5 * (upper + lower), half, n)
    raise ValueError("tolerance not reached within max_terms")


def radius_of_convergence(coeff, n_max=60):
    """Estimated radius of convergence of the power series with these coefficients."""
    def estimate(top):
        live = [k for k in range(top + 1) if coeff(k) != 0]
        if len(live) < 2:
            raise ValueError("need at least two non-zero coefficients")
        n, m = live[-2], live[-1]
        rho = (abs(coeff(m)) / abs(coeff(n))) ** (1.0 / (m - n))
        if rho == 0.0:
            return math.inf
        return 1.0 / rho

    full = estimate(n_max)
    half = estimate(n_max // 2)
    if full == math.inf or full >= 1.9 * half:
        return math.inf
    if full <= 0.55 * half:
        return 0.0
    return full


print(partial_sums(lambda k: 1.0 / k, 4))
print(ratio_test(lambda k: 0.5 ** k))
print(estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-6))
'''}],
                "hints": [
                    "`partial_sums` is the running-total pattern: one accumulator, one append per step. Do not re-sum from k=1 for every entry.",
                    "Write the ratio as a small inner function `ratio(m)` so you can call it twice; check `term(m) == 0` inside it and raise there.",
                    "In `estimate_sum` the bracket is `[tail_integral(n+1), tail_integral(n)]`. The midpoint is the estimate and half the width is the guaranteed bound — return both.",
                    "For `radius_of_convergence`, build the list of indices with non-zero coefficients first, then work with its last two entries; the `1 / (m - n)` exponent is what handles series such as sin whose coefficients skip every other index.",
                ],
                "tests": [
                    {"name": "Partial sums accumulate", "code": r'''
_got = partial_sums(lambda k: 0.5 ** k, 3)
assert len(_got) == 3, f"partial_sums(..., 3) gave {len(_got)} entries, expected 3"
for _i, _w in enumerate([0.5, 0.75, 0.875]):
    assert abs(_got[_i] - _w) < 1e-12, f"S_{_i + 1} is {_got[_i]!r}, expected {_w}"
_got = partial_sums(lambda k: 1.0 / k, 4)
_want = [1.0, 1.5, 1.0 + 0.5 + 1.0 / 3.0, 1.0 + 0.5 + 1.0 / 3.0 + 0.25]
for _i in range(4):
    assert abs(_got[_i] - _want[_i]) < 1e-12, f"S_{_i + 1} is {_got[_i]!r}, expected {_want[_i]!r}"
assert partial_sums(lambda k: 7.0, 1) == [7.0], "A single-term run returns one entry"
for _bad in (0, -3):
    try:
        partial_sums(lambda k: 1.0, _bad)
        assert False, f"partial_sums with n={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Ratio test on geometric series", "code": r'''
_v, _L = ratio_test(lambda k: 0.5 ** k)
assert _v == "converges", f"Geometric with ratio 1/2 gave verdict {_v!r}"
assert abs(_L - 0.5) < 1e-6, f"Ratio limit was {_L!r}, expected 0.5"
_v, _L = ratio_test(lambda k: 2.0 ** k)
assert _v == "diverges", f"Geometric with ratio 2 gave verdict {_v!r}"
assert abs(_L - 2.0) < 1e-6, f"Ratio limit was {_L!r}, expected 2.0"
_v, _L = ratio_test(lambda k: (-1.0) ** k / 3.0 ** k)
assert _v == "converges", f"Alternating geometric gave verdict {_v!r}"
assert abs(_L - 1.0 / 3.0) < 1e-6, f"Ratio limit was {_L!r}, expected 1/3"
'''},
                    {"name": "Ratio test is honest about L = 1", "code": r'''
for _name, _term in [("1/k", lambda k: 1.0 / k), ("1/k^2", lambda k: 1.0 / k ** 2),
                     ("1/k^3", lambda k: 1.0 / k ** 3)]:
    _v, _L = ratio_test(_term)
    assert _v == "inconclusive", f"ratio_test on {_name} gave {_v!r}, expected 'inconclusive'"
    assert abs(_L - 1.0) < 1e-3, f"ratio_test on {_name} gave limit {_L!r}, expected about 1.0"
_v, _L = ratio_test(lambda k: 1.0 / math.factorial(k), 40)
assert _v == "converges" and _L < 1e-2, f"1/k! gave {(_v, _L)!r}, expected a ratio near 0"
'''},
                    {"name": "Ratio test refuses degenerate input", "code": r'''
try:
    ratio_test(lambda k: 0.0)
    assert False, "A series of zero terms should raise ValueError"
except ValueError:
    pass
for _bad in (0, -5):
    try:
        ratio_test(lambda k: 0.5 ** k, _bad)
        assert False, f"ratio_test with n={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "estimate_sum hits the Basel problem", "code": r'''
_est, _half, _n = estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-6)
assert _n == 707, f"estimate_sum used {_n} terms, expected 707"
assert _half <= 1e-6, f"Returned half-width {_half!r} exceeds the tolerance"
assert abs(_est - math.pi ** 2 / 6.0) <= _half, \
    f"Estimate {_est!r} is further than {_half!r} from pi^2/6 = {math.pi ** 2 / 6.0!r}"
_est, _half, _n = estimate_sum(lambda k: 1.0 / k ** 3, lambda x: 0.5 / x ** 2, 1e-8)
assert abs(_est - 1.2020569031595943) <= _half, \
    f"Apery estimate {_est!r} is outside its own bound {_half!r}"
'''},
                    {"name": "estimate_sum guards its arguments", "code": r'''
for _bad in (0.0, -1e-9):
    try:
        estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, _bad)
        assert False, f"estimate_sum with tol={_bad} should raise ValueError"
    except ValueError:
        pass
try:
    estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-9, max_terms=10)
    assert False, "Running out of terms before the tolerance should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Radius of convergence, finite cases", "code": r'''
_got = radius_of_convergence(lambda k: 2.0 ** k)
assert abs(_got - 0.5) < 1e-9, f"Coefficients 2^k give R = 0.5; got {_got!r}"
_got = radius_of_convergence(lambda k: 0.0 if k == 0 else 1.0 / k)
assert abs(_got - 1.0) < 0.05, f"Coefficients 1/k give R = 1; got {_got!r}"
_got = radius_of_convergence(lambda k: 0.0 if k == 0 else 1.0 / (3.0 ** k * k * k))
assert abs(_got - 3.0) < 0.2, f"Coefficients 1/(3^k k^2) give R = 3; got {_got!r}"
'''},
                    {"name": "Radius of convergence, degenerate cases", "code": r'''
_got = radius_of_convergence(lambda k: 1.0 / math.factorial(k))
assert _got == math.inf, f"The exp series has an infinite radius; got {_got!r}"
_sin = lambda k: 0.0 if k % 2 == 0 else (-1.0) ** ((k - 1) // 2) / math.factorial(k)
_got = radius_of_convergence(_sin)
assert _got == math.inf, f"The sin series has an infinite radius; got {_got!r}"
_got = radius_of_convergence(lambda k: float(math.factorial(k)))
assert _got == 0.0, f"Coefficients k! give R = 0; got {_got!r}"
try:
    radius_of_convergence(lambda k: 1.0 if k == 0 else 0.0)
    assert False, "A series with one non-zero coefficient should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Antiderivatives and the Fundamental Theorem",
            "summary": "Module 1 proved the theorem. This is the search it leaves open: obtaining an antiderivative, for which there is no algorithm.",
            "concepts": [
                r"An antiderivative is a family, not a function: if $F' = f$ then so is $F + C$, and the constant is what an initial condition exists to fix",
                r"Fundamental Theorem, first half: the accumulation function $A(x) = \int_a^x f(t)\,dt$ satisfies $A'(x) = f(x)$, so every continuous function has an antiderivative even when no formula for it exists",
                r"Fundamental Theorem, second half: $\int_a^b f = F(b) - F(a)$, which is why a closed form beats every quadrature rule in module 1 whenever you can find one",
                r"The standard table is the derivative table read backwards, with one exception: $\int x^n\,dx$ is $x^{n+1}/(n+1)$ for every $n$ except $-1$, where it is $\ln|x|$",
                r"Linearity, additivity over adjoining subintervals, and the convention $\int_b^a = -\int_a^b$ that keeps the theorem true whichever way the limits run",
                r"Module 1 proved the theorem; this module is about the search it leaves open. Obtaining a $G$ with $G' = f$ has no algorithm and no composition rule — nothing turns antiderivatives of $f_1$ and $f_2$ into one for $f_1 f_2$ — and modules 6 to 9 are the collected techniques for conducting it",
                r"On a domain in two pieces there are two constants, not one: the general antiderivative of $\frac{1}{x}$ carries an independent constant on $x < 0$ and on $x > 0$, because the mean value theorem argument behind $+C$ runs inside one interval at a time",
                r"$\ln$ is the antiderivative the power rule cannot reach, not an extra table entry. Define $L(x) = \int_1^x\frac{\mathrm{d}t}{t}$; part one gives $L' = \frac{1}{x}$, and $L(ab) = L(a) + L(b)$ falls out of the substitution $t = au$",
                r"Check an antiderivative by differentiating it, never by integrating again — and the discrepancy is usually the correction. Differentiating a guess of $x\ln x$ overshoots by exactly $1$, so $\int\ln x\,\mathrm{d}x = x\ln x - x$",
                r"Some continuous functions have no elementary antiderivative, and that is Liouville's theorem rather than a gap in anyone's technique. $e^{-x^2}$, $\frac{\sin x}{x}$ and $\frac{1}{\ln x}$ are all proved impossible, which is what module 2's quadrature and module 11's series exist to answer",
            ],
            "read": [
                {
                    "title": "The antiderivative as something you have to go and find",
                    "minutes": 12,
                    "body": r"""
Module 1 already proved the Fundamental Theorem, both halves, and used it. So this
module is not about the theorem. It is about the word inside it that the theorem never
explains.

$\int_a^b f = G(b) - G(a)$ is an instruction with a hole in it: *first obtain a $G$ with
$G' = f$*. Differentiation is an algorithm — the rules of Calculus I compose, so any
expression built out of the standard functions can be differentiated by a machine, in
one pass, with no cleverness anywhere. Going the other way is a search. There is no
composition rule for antiderivatives: nothing turns $G_1$ for $f_1$ and $G_2$ for $f_2$
into an antiderivative of $f_1 f_2$, and the next four modules are the collected
techniques for conducting that search. This module is the hinge between the numerical
half of the course and the algebraic half, and the first thing to establish is what an
antiderivative actually is.

## A family, and how many constants it really has

If $G' = f$ then $(G + C)' = f$ for every constant $C$, so an antiderivative is never a
function; it is a whole family. The usual statement — *any two antiderivatives of $f$
differ by a constant* — is a corollary of the mean value theorem from MA111's module 8,
and it needs a hypothesis that is almost always left out. If $H' = 0$ on an
**interval**, then for any two points $p < q$ in it the mean value theorem gives
$H(q) - H(p) = H'(c)(q - p) = 0$, so $H$ is constant. The argument needs $[p, q]$ to lie
inside the domain, and it says nothing at all when the domain is in two pieces.

That is not a technicality. Take $f(x) = \frac{1}{x}$, whose domain is
$(-\infty, 0) \cup (0, \infty)$, and build a function out of two different constants:

```
G(x) = ln|x| + 5      for x > 0
G(x) = ln|x| - 2      for x < 0
```

$G' = \frac{1}{x}$ at every point of the domain, and $G$ is not $\ln|x|$ plus any single
constant. The general
antiderivative of $\frac1x$ carries **two** independent constants, one per interval, and
software that reports `log(x) + C` is telling you about one of the two branches. The
same thing happens for $\tan x$, for $\frac{1}{x^2-1}$, and for every integrand with a
pole in the middle of the region of interest. Module 1 already showed what ignoring the
gap costs: $\int_{-1}^{1}\frac{\mathrm{d}x}{x^2}$ evaluates by bracket to $-2$, a
negative number for a positive integrand.

## The one exponent the power rule cannot reach

Read the power rule backwards. Since
$\frac{\mathrm{d}}{\mathrm{d}x}\frac{x^{n+1}}{n+1} = x^{n}$, the antiderivative of
$x^n$ is $\frac{x^{n+1}}{n+1} + C$ — for every $n$ except $-1$, where the construction
divides by zero. The gap is real rather than cosmetic: no power of $x$ has derivative
$\frac1x$, because differentiating $x^k$ always lowers the exponent by one and $k - 1 = -1$ forces $k = 0$, whose derivative is $0$ and not $\frac1x$.

So where does the missing function come from? Part one of the Fundamental Theorem
manufactures it. Define

$$L(x) = \int_1^{x}\frac{\mathrm{d}t}{t}, \qquad x > 0$$

Part one says immediately that $L'(x) = \frac1x$, and $L(1) = 0$ because the interval is
empty. That is an antiderivative of $\frac1x$ obtained without knowing any logarithm
exists. Its defining property arrives from a substitution — the technique of the next
module, used here one module early because this is the cleanest place it ever appears.
In $L(ab) = \int_1^{ab}\frac{\mathrm{d}t}{t}$ put $t = au$, so $\mathrm{d}t = a\, \mathrm{d}u$ and the integrand $\frac{\mathrm{d}t}{t} = \frac{a\,\mathrm{d}u}{au} = \frac{\mathrm{d}u}{u}$ — the $a$ cancels completely. The limits $t = a$ and $t = ab$
become $u = 1$ and $u = b$, so

$$L(ab) - L(a) = \int_{a}^{ab}\frac{\mathrm{d}t}{t} = \int_{1}^{b}\frac{\mathrm{d}u}{u}
= L(b)$$

which is $L(ab) = L(a) + L(b)$: the logarithm law, derived from an integral rather than
assumed from a table. Everything else follows. $L$ is strictly increasing because
$L' = \frac1x > 0$, so it has an inverse, and that inverse is $\exp$. For $x < 0$ the
chain rule gives $\frac{\mathrm{d}}{\mathrm{d}x}\ln(-x) = \frac{-1}{-x} = \frac1x$
again, which is what the modulus in $\ln|x|$ is doing — and, per the previous section,
the two branches keep separate constants.

## Checking an answer, and repairing it with the same move

Because differentiation is the algorithm and integration is the search, **every**
antiderivative you produce in the next four modules should be differentiated before it
is used. The check is cheap, it is complete, and it is the only one available.

It also repairs. Suppose you want $\int \ln x\,\mathrm{d}x$ and guess $x\ln x$, on the
grounds that a logarithm ought to come with an $x$ in front of it. Differentiate:

```
d/dx (x ln x) = ln x + x * (1/x)
              = ln x + 1
```

That is the integrand plus $1$, so the guess overshoots by exactly the antiderivative of
$1$. Subtract it: $x\ln x - x$. Differentiate again to confirm — $\ln x + 1 - 1 = \ln x$. The answer is $x\ln x - x + C$, obtained by guessing, checking, and correcting by
the size of the error, which is a method rather than a lucky guess. Module 7 turns the
same move into integration by parts.

## Worked: the constant is what the initial condition is for

A stone is thrown straight up at $20\,\mathrm{m/s}$ from ground level, with
$a(t) = -9.81\,\mathrm{m/s^2}$. Antidifferentiate twice, fixing each constant as it
appears.

```
a(t) = -9.81
v(t) = -9.81 t + C1          v(0) = 20   =>  C1 = 20
v(t) = 20 - 9.81 t

s(t) = 20 t - 4.905 t^2 + C2 s(0) = 0    =>  C2 = 0
s(t) = 20 t - 4.905 t^2

apex:  v = 0  =>  t = 20/9.81 = 2.0387 s
       s     =  20(2.0387) - 4.905(2.0387)^2
             =  40.7747 - 20.3874
             =  20.387 m
```

Cross-check by an argument that never integrates: kinetic energy $\frac{1}{2} v^2$ converts
to $g h$, so $h = \frac{v^2}{2g} = \frac{400}{19.62} = 20.387$ m. The two agree to five
figures, which they must, because the energy argument is the integral
$\int v\,\mathrm{d}v = \int -g\,\mathrm{d}s$ in disguise. Note where each constant was
pinned: $C_1$ from a condition on the velocity, $C_2$ from a condition on the position.
Two antidifferentiations need two conditions, and a family of curves becomes one curve
only when they are supplied.

## The mistake, and why it is tempting

The tempting move is to treat an integral sign as an operator that can be *applied*, the
way $\frac{\mathrm{d}}{\mathrm{d}x}$ can. It reads like one and it is written like one.
But $\frac{\mathrm{d}}{\mathrm{d}x}$ always terminates, and $\int$ may not terminate at
all. There is no product rule, no quotient rule and no chain rule for integrals; the
techniques ahead are each a *partial* inverse of one differentiation rule, which is why
each of them works on a shape rather than on everything. Substitution inverts the chain
rule and needs the inner derivative to be present. Parts inverts the product rule and
needs one factor to get simpler. Partial fractions is not the inverse of anything — it
is algebra applied before integrating at all.

## Where this stops holding

Some perfectly ordinary continuous functions have no elementary antiderivative, and
that is a theorem rather than an admission of ignorance. *Elementary* has a precise
meaning: built from rational functions by finitely many roots, exponentials and
logarithms. Liouville's theorem, and its algorithmic descendant, decides membership,
and it rules out $\int e^{-x^2}\,\mathrm{d}x$, $\int\frac{\sin x}{x}\,\mathrm{d}x$ and
$\int\frac{\mathrm{d}x}{\ln x}$. Nobody will find these by trying harder.

The antiderivatives still exist — module 1 built one, $\mathrm{Si}(x)$, and read its
graph off part one of the theorem without a formula. What is missing is a formula in
that particular vocabulary. Two routes remain and this course owns both: module 2's
adaptive quadrature evaluates such an integral to a requested tolerance, and module 11
expands the integrand as a series and integrates it term by term with a remainder bound.
Neither is a consolation prize. They are the reason the numerical half of this course
came first.
"""
                },
            ],
            "derive": [
                {
                    "title": "The exponent the power rule misses, and the function that fills the gap",
                    "minutes": 12,
                    "vars": ["x", "a", "b", "u", "n", "L"],
                    "brief": r"""
Reading the power rule backwards produces the antiderivative of $x^n$ for every
exponent but one. This derivation finds the exponent, then builds the missing
antiderivative out of the Fundamental Theorem instead of quoting it from a table — and
gets the logarithm law for free, out of a substitution.

Throughout, $L$ is the function defined by $L(x) = \int_1^{x}\frac{\mathrm{d}t}{t}$ for
$x > 0$.
""",
                    "steps": [
                        {
                            "prompt": "Differentiate $\\frac{x^{n+1}}{n+1}$, treating $n$ as a constant. Write the result in terms of $x$ and $n$.",
                            "answer": "x^{n}",
                            "placeholder": "a power of x",
                            "hint": "The power rule drops the exponent by one and multiplies by the old exponent; the $n+1$ underneath cancels the $n+1$ the rule brings down.",
                        },
                        {
                            "prompt": "That construction is an antiderivative of $x^n$ for every exponent except one. Which value of $n$ does it fail at?",
                            "answer": "-1",
                            "placeholder": "?",
                            "hint": "Look at the denominator, not the numerator. The expression has to be a function before it can be differentiated.",
                            "deconstruct": [
                                "The candidate antiderivative is $\\frac{x^{n+1}}{n+1}$.",
                                "It is undefined exactly when $n + 1 = 0$.",
                            ],
                        },
                        {
                            "prompt": "Part one of the Fundamental Theorem is applied to $L(x) = \\int_1^{x}\\frac{\\mathrm{d}t}{t}$ for $x > 0$. Write $L'(x)$.",
                            "answer": "\\frac{1}{x}",
                            "placeholder": "?",
                            "hint": "Part one hands back the integrand evaluated at the upper limit. No integration is performed anywhere.",
                        },
                        {
                            "prompt": "In $L(ab) - L(a) = \\int_{a}^{ab}\\frac{\\mathrm{d}t}{t}$, substitute $t = au$ with $a > 0$ fixed, so $\\mathrm{d}t = a\\,\\mathrm{d}u$. Write the integrand that is left, in terms of $u$.",
                            "answer": "\\frac{1}{u}",
                            "placeholder": "?",
                            "hint": "The $a$ appears once on the top from $\\mathrm{d}t$ and once on the bottom from $t = au$.",
                            "deconstruct": [
                                "$\\frac{\\mathrm{d}t}{t} = \\frac{a\\,\\mathrm{d}u}{au}$.",
                                "The factor $a$ cancels completely, which is the whole point of the substitution.",
                                "The limits move with it: $t = a$ gives $u = 1$, and $t = ab$ gives $u = b$.",
                            ],
                        },
                        {
                            "prompt": "Those new limits run from $1$ to $b$, so the right-hand side is $L(b)$ and therefore $L(ab) = L(a) + L(b)$. Put $a = b = 1$ in that identity and write the value of $L(1)$.",
                            "answer": "0",
                            "placeholder": "?",
                            "hint": "The identity gives $L(1) = 2L(1)$. Only one number satisfies that.",
                            "deconstruct": [
                                "$L(1 \\cdot 1) = L(1) + L(1)$.",
                                "So $L(1) = 2L(1)$, hence $L(1) = 0$ — which agrees with the integral running from $1$ to $1$.",
                            ],
                        },
                        {
                            "prompt": "$L$ only covers $x > 0$. For $x < 0$, differentiate $\\ln(-x)$ by the chain rule and write the result.",
                            "answer": "\\frac{1}{x}",
                            "placeholder": "?",
                            "hint": "The outer derivative is $\\frac{1}{-x}$ and the inner derivative is $-1$. The two minus signs cancel.",
                        },
                    ],
                    "closing": r"""
The two halves join into $\int\frac{\mathrm{d}x}{x} = \ln|x| + C$, and the modulus is
not decoration: it is the statement that the same formula covers both branches. What it
does **not** cover is a single constant. The domain $(-\infty,0)\cup(0,\infty)$ is two
intervals, the mean value theorem argument runs inside one interval at a time, and the
general antiderivative therefore carries one constant on each — a fact every computer
algebra system suppresses when it prints `log(x) + C`.

Steps three to five never mentioned the exponential, the number $e$, or any property of
$\ln$. They built a function with the right derivative and then derived its defining law
from a change of variable. The exponential can now be *defined* as the inverse of $L$,
which exists because $L' = \frac{1}{x} > 0$ makes $L$ strictly increasing, and $e$ can
be defined as the unique solution of $L(e) = 1$. That is the honest order: the
logarithm is an integral first and a table entry second.
"""
                },
            ],
            "quiz": {
                "title": "Antiderivatives and the two halves of the theorem",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Which of these is an antiderivative of $f(x) = 3x^2$?",
                        "opts": [r"$6x$", r"$x^3 - 7$", r"$x^3/3$", r"$3x^3$"],
                        "a": 1,
                        "why": (
                            r"Differentiate each candidate and keep whichever gives back $3x^2$. That is $x^3 - 7$ — and so "
                            r"would be $x^3$, or $x^3 + 100$, because the constant vanishes under differentiation. That is "
                            r"exactly why an antiderivative is a whole family and why the $+C$ is written. Of the others, "
                            r"$6x$ is the derivative of $3x^2$ rather than its antiderivative, $x^3/3$ differentiates to "
                            r"$x^2$, and $3x^3$ differentiates to $9x^2$."
                        ),
                    },
                    {
                        "q": r"What is $\int_1^e \frac{1}{x}\,dx$?",
                        "opts": [r"$1$", r"$e - 1$", r"$-1$", r"$e$"],
                        "a": 0,
                        "why": (
                            r"The antiderivative of $1/x$ is $\ln|x|$, so the value is $\ln e - \ln 1 = 1 - 0 = 1$. The power "
                            r"rule $x^{n+1}/(n+1)$ is the one place the table breaks, because at $n = -1$ it divides by zero; "
                            r"$1/x$ has to be handled separately and the logarithm is what fills the gap. The value $e - 1$ is "
                            r"what integrating $e^x$ over the same interval would give."
                        ),
                    },
                    {
                        "q": r"If $A(x) = \int_0^x \sin(t^2)\,dt$, what is $A'(x)$?",
                        "opts": [r"$\cos(x^2)$", r"$\sin(x^2)$", r"$2x\cos(x^2)$", r"$-\cos(x^2)/2$"],
                        "a": 1,
                        "why": (
                            r"The first half of the theorem says that differentiating an accumulation function hands back the "
                            r"integrand evaluated at the upper limit, so $A'(x) = \sin(x^2)$ and no integration is required. "
                            r"None is possible either: $\sin(t^2)$ has no elementary antiderivative, which is the whole point "
                            r"— $A$ still exists and is still differentiable. Answers built from $\cos$ come from integrating "
                            r"instead of differentiating, and the extra factor $2x$ belongs to the derivative of "
                            r"$\sin(x^2)$, a different question."
                        ),
                    },
                    {
                        "q": r"Given $\int_0^3 f = 7$ and $\int_0^5 f = 2$, what is $\int_5^3 f$?",
                        "opts": [r"$5$", r"$-5$", r"$9$", r"$-9$"],
                        "a": 0,
                        "why": (
                            r"Additivity gives $\int_0^3 f + \int_3^5 f = \int_0^5 f$, so $\int_3^5 f = 2 - 7 = -5$. The "
                            r"limits asked for run the other way, and reversing them flips the sign, so the value is $+5$. "
                            r"Stopping at $-5$ means the reversal was missed; adding the two given numbers instead of "
                            r"subtracting them gives $9$."
                        ),
                    },
                    {
                        "q": r"Simpson's rule converges as $O(h^4)$ on a smooth integrand. What does the Fundamental Theorem offer that no amount of refinement can?",
                        "opts": [
                            r"A faster algorithm for the same approximate answer",
                            r"The exact value, from one formula evaluated at just the two endpoints",
                            r"A guarantee that the integrand is continuous",
                            r"A way to integrate functions that have no antiderivative",
                        ],
                        "a": 1,
                        "why": (
                            r"When an antiderivative $F$ can be found, $F(b) - F(a)$ is the integral exactly, at the cost of "
                            r"two evaluations and no panels at all — a different kind of claim from an error that merely "
                            r"shrinks. It is not universal: most integrands have no elementary antiderivative, and that is "
                            r"precisely where quadrature earns its keep. Continuity is an assumption the theorem needs, not a "
                            r"conclusion it delivers."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M6
        {
            "title": "Substitution: the chain rule run backwards",
            "summary": "The technique that rewrites more integrals than all the others together, and the bookkeeping that keeps a definite integral honest.",
            "concepts": [
                r"Substitution is the chain rule integrated: with $u = g(x)$ and $du = g'(x)\,dx$, $\int f(g(x))\,g'(x)\,dx = \int f(u)\,du$",
                r"The whole skill is spotting a $g'$ already present in the integrand, up to a constant factor you are free to move outside",
                r"For a definite integral, push the limits through the substitution to $g(a)$ and $g(b)$ and never change back to $x$",
                r"Run the other way, writing $x = h(u)$, the map must be one-to-one on the interval — the requirement behind both trigonometric substitution and the infinite-domain maps of module 2",
                r"Symmetry falls out of the same move: over $[-a, a]$ an odd integrand gives $0$ and an even one gives twice the half-integral — both needing $f$ integrable across the whole of $[-a,a]$, which $\frac{1}{x}$ is not",
                r"The proof is two lines: the chain rule gives $\frac{\mathrm{d}}{\mathrm{d}x}F(g(x)) = f(g(x))\,g'(x)$, and part two of the Fundamental Theorem integrates both sides over $[a,b]$",
                r"That proof never assumes $g$ is one-to-one, so the forward direction survives a $g$ that folds: $\int_{-1}^{1}2x\cos(x^2)\,\mathrm{d}x$ substitutes to an integral from $1$ to $1$, and $0$ is the right answer",
                r"Forgetting to move the limits does not fail loudly — it returns a clean positive number answering a different question. On $\int_0^2 x e^{x^2}\,\mathrm{d}x$ that number is too small by a factor of $e^2 + 1 = 8.39$",
            ],
            "read": [
                {
                    "title": "One line of chain rule, and the hypothesis that appears only in one direction",
                    "minutes": 12,
                    "body": r"""
Every technique in this half of the course is one differentiation rule, run backwards,
with the conditions that survive the reversal written down. Substitution is the first
and the most used, and its entire proof is two lines. Seeing those two lines is worth
more than a page of practice, because they decide precisely what has to be checked and
what does not — and the answer is different for the two directions in which the
technique is used.

## The proof, in full

Let $F$ be an antiderivative of $f$, so $F' = f$. Apply the chain rule to the
composition:

$$\frac{\mathrm{d}}{\mathrm{d}x}F(g(x)) = F'(g(x))\,g'(x) = f(g(x))\,g'(x)$$

That is the chain rule and nothing else. Now integrate both sides over $[a,b]$ and use
part two of the Fundamental Theorem from module 1 on the left:

$$\int_a^b f(g(x))\,g'(x)\,\mathrm{d}x = F(g(b)) - F(g(a)) = \int_{g(a)}^{g(b)}
f(u)\,\mathrm{d}u$$

Done. The theorem needed $g$ differentiable with $g'$ integrable, and $f$ continuous on
the range of $g$. Read the list again and notice what is *not* on it: nothing requires
$g$ to be one-to-one, and nothing requires $g(a) < g(b)$.

## The case that looks broken and is not

Take $\int_{-1}^{1} 2x\cos(x^2)\,\mathrm{d}x$ with $u = x^2$. On $[-1,1]$ the map
$x \mapsto x^2$ is emphatically not one-to-one — it folds the interval in half. The
formula does not care:

```
u = x^2          du = 2x dx
lower  x = -1 -> u = 1
upper  x =  1 -> u = 1

integral = integral of cos u du from 1 to 1 = 0
```

Both limits land on $1$ and the answer is $0$. Check it independently: $2x\cos(x^2)$ is
an odd function integrated over an interval symmetric about the origin, so it is $0$ by
symmetry. The two agree. What the fold destroys is the *picture* of $u$ sweeping an
interval once — the substituted integral is not an area under $\cos u$ over any
interval — but the algebra was never about that picture. It was about a composition and
the chain rule, and both survive folding.

## The other direction, where injectivity is compulsory

Now run it backwards: write $x = h(u)$ and replace $\mathrm{d}x$ by $h'(u)\,\mathrm{d}u$.
Here you are choosing the new variable and *inventing* the old one from it, and the
requirement is real. To convert $\int_a^b\ldots\mathrm{d}x$ into an integral in $u$ you
must produce endpoints $\alpha,\beta$ with $h(\alpha) = a$ and $h(\beta) = b$, and the
formula then reports $\int_\alpha^\beta$. If $h$ doubles back, $[\alpha,\beta]$ covers
part of $[a,b]$ twice and part not at all, and the integral it computes is a different
one.

The concrete failure is a sign. Take $\int_0^1\sqrt{1-x^2}\,\mathrm{d}x$ with
$x = \sin\theta$. Then

$$\sqrt{1-x^2} = \sqrt{1-\sin^2\theta} = \sqrt{\cos^2\theta} = |\cos\theta|$$

and the modulus is the whole issue. Restricting $\theta$ to $[0,\frac{\pi}{2}]$ makes
$\cos\theta \ge 0$, the modulus disappears, and the integral becomes
$\int_0^{\pi/2}\cos^2\theta\,\mathrm{d}\theta = \frac{\pi}{4}$ — which is right, being a
quarter of the unit disc. Allow $\theta$ to reach $\pi$ and $\cos\theta$ turns negative
while $|\cos\theta|$ does not, so writing $\cos\theta$ for the root silently integrates
the wrong function over half the range. Module 2 chose $x = a + \frac{t}{1-t}$ for
infinite domains for exactly this reason: it increases strictly across $[0,1)$, so it is
one-to-one and the limits transfer.

## Worked: the error the arithmetic does not object to

$$\int_0^2 x e^{x^2}\,\mathrm{d}x$$

with $u = x^2$, so $\mathrm{d}u = 2x\,\mathrm{d}x$ and $x\,\mathrm{d}x = \frac{1}{2}\mathrm{d}u$. Push the limits: $x = 0$ gives $u = 0$, and $x = 2$ gives
$u = 4$.

```
correct     (1/2) * integral of e^u du from 0 to 4
          = (e^4 - 1)/2
          = 26.799

careless    (1/2) * integral of e^u du from 0 to 2      <- old limits, new variable
          = (e^2 - 1)/2
          = 3.1945
```

The wrong answer is not absurd. It is positive, it has the right units, it came out of
an expression that simplified cleanly, and it is too small by a factor of
$\frac{e^4-1}{e^2-1} = e^2 + 1 = 8.39$. Nothing in the working objects, because the
integral $\int_0^2 e^u\,\mathrm{d}u$ is a perfectly good integral. It is the
answer to a different question. This is the characteristic failure of substitution: it
does not crash, it answers something else.

Two habits close it off. Push the limits at the same moment you write $\mathrm{d}u$,
never afterwards. Or convert back to $x$ before evaluating, and then use the original
limits — which is slower and never wrong.

## Worked: three integrands that look alike and need three different moves

The technique is a pattern-matcher, so the skill it really trains is telling near-misses
apart. All three of these are a power of $x$ over $1 + x^{2}$ on $[0,1]$.

```
integral of x/(1+x^2) dx      numerator IS the derivative of the denominator,
                              up to a factor 2  ->  substitution, u = 1 + x^2

  = (1/2) ln(1+x^2) from 0 to 1  =  (1/2) ln 2  =  0.34657


integral of 1/(1+x^2) dx      no x on top at all, so nothing can be du
                              ->  no substitution exists; it is a standard form

  = arctan x from 0 to 1         =  pi/4        =  0.78540


integral of x^2/(1+x^2) dx    degree on top is not below degree underneath
                              ->  divide first, which is module 9's opening move

  x^2/(1+x^2) = 1 - 1/(1+x^2)
  = 1 - pi/4                     =  0.21460
```

One character of difference between the numerators, and three unrelated methods. The
first is the $\frac{f'}{f}$ pattern and takes one line. The second cannot be substituted
at all — there is no inner function whose derivative is present, because there is no
inner function — and has to be recognised. The third is not an integration problem until
a division has been done, and attempting a substitution on it wastes the effort before
discovering that.

Notice the arithmetic check available on the third without doing any of it: the
integrand $\frac{x^{2}}{1+x^{2}}$ is below $\frac{1}{2}$ everywhere on $[0,1]$ and below
$\frac{1}{2}$ at the right-hand end, so the answer must be under $0.5$. And the three
values must satisfy $0.78540 + 0.21460 = 1$, since the second and third integrands add to
$1$ identically. They do, which checks two of the three at once.

## The mistake, and why it is tempting

The other standard error is manufacturing the missing $g'$. Faced with
$\int\cos(x^2)\,\mathrm{d}x$, the inner function is $x^2$ and its derivative is $2x$,
which is nowhere in the integrand — so the temptation is to insert it and compensate,
claiming that

$$\int\cos(x^2)\,\mathrm{d}x = \frac{1}{2x}\int 2x\cos(x^2)\,\mathrm{d}x$$

This is tempting because it is a move that *is* legal when the missing factor is a
constant, and it has been used correctly a dozen times by the point it appears. It fails
here because $\frac{1}{2x}$ is not constant and cannot leave the integral sign;
$\int u\,v = u\int v$ is false for non-constant $u$. Test the claim with the crudest
possible check: at any single value of $x$ the right-hand side would have to have
derivative $\cos(x^2)$, and differentiating a product of $\frac{1}{2x}$ with an
integral produces an extra term from the product rule, which nothing cancels.

$\int\cos(x^2)\,\mathrm{d}x$ is in fact the Fresnel integral, one of the functions
module 5 named as having no elementary antiderivative at all. The manufacturing move is
attempting to prove a theorem false by notation.

## Where this stops holding

Substitution requires the inner derivative to be present *up to a constant factor*, and
that is a narrow condition. It reduces $\int\frac{2x+3}{x^2+3x+7}\,\mathrm{d}x$ to
$\int\frac{\mathrm{d}u}{u}$ in one step because the numerator is exactly the derivative
of the denominator — the $\frac{f'}{f}$ pattern, always a logarithm, and worth checking
for before anything else is tried. Change the numerator to $2x + 4$ and no substitution
touches it; the extra $1$ has to be split off and handled by module 9's machinery
instead.

The symmetry rules come from the same theorem and inherit its hypotheses. Over
$[-a,a]$, put $x = -t$: an odd integrand gives $\int_{-a}^{a}f = 0$ and an even one
gives $2\int_0^a f$. Both are proofs rather than estimates, and both need $f$ integrable
on the whole of $[-a,a]$ — which $\frac{1}{x}$, odd and unbounded at the origin, is not.
Its integral over $[-1,1]$ does not exist, and answering $0$ by symmetry is the same
error module 1 made with $\frac{1}{x^2}$, wearing a different hat.
"""
                },
            ],
            "derive": [
                {
                    "title": "One substitution, done twice: once with the limits moved and once without",
                    "minutes": 11,
                    "vars": ["x", "u", "e"],
                    "brief": r"""
$\int_0^2 x e^{x^2}\,\mathrm{d}x$ has no chance without a substitution — $e^{x^2}$ has
no elementary antiderivative on its own — and it falls in one line with $u = x^2$.

The point of the last two steps is that the commonest error in the technique produces a
clean, plausible, positive number, and this derivation prices it.
""",
                    "steps": [
                        {
                            "prompt": "With $u = x^2$, write $\\frac{\\mathrm{d}u}{\\mathrm{d}x}$.",
                            "answer": "2x",
                            "placeholder": "?",
                            "hint": "The power rule on $x^2$.",
                        },
                        {
                            "prompt": "The integrand carries $x\\,\\mathrm{d}x$, not $2x\\,\\mathrm{d}x$. Write the constant $c$ for which $x\\,\\mathrm{d}x = c\\,\\mathrm{d}u$.",
                            "answer": "\\frac{1}{2}",
                            "placeholder": "?",
                            "hint": "Divide $\\mathrm{d}u = 2x\\,\\mathrm{d}x$ through by $2$.",
                        },
                        {
                            "prompt": "The limits belong to the old variable and must be pushed through $u = x^2$. Write the new upper limit.",
                            "answer": "4",
                            "placeholder": "?",
                            "hint": "The old upper limit is $x = 2$.",
                        },
                        {
                            "prompt": "Evaluate $\\frac{1}{2}\\int_0^{4}e^{u}\\,\\mathrm{d}u$. Write the exact value in terms of $e$.",
                            "answer": "\\frac{e^4-1}{2}",
                            "placeholder": "?",
                            "hint": "The antiderivative of $e^u$ is $e^u$, so this is $\\frac{1}{2}\\left(e^4 - e^0\\right)$.",
                        },
                        {
                            "prompt": "Now the careless version: the same $\\frac{1}{2}$, but the limits left at $0$ and $2$. Write what that returns.",
                            "answer": "\\frac{e^2-1}{2}",
                            "placeholder": "?",
                            "hint": "Identical working, with $4$ replaced by $2$ in the upper limit.",
                        },
                        {
                            "prompt": "Divide the correct value by the careless one and simplify. Write the factor by which the error understates the answer.",
                            "answer": "e^2+1",
                            "placeholder": "?",
                            "hint": "$e^4 - 1$ is a difference of two squares: $\\left(e^2-1\\right)\\left(e^2+1\\right)$.",
                            "deconstruct": [
                                "$\\frac{e^4-1}{e^2-1}$, after the halves cancel.",
                                "Factor the top as $(e^2-1)(e^2+1)$ and cancel.",
                            ],
                        },
                    ],
                    "closing": r"""
The correct value is $\frac{e^4-1}{2} = 26.799$ and the careless one is
$\frac{e^2-1}{2} = 3.1945$, a factor of $e^2 + 1 = 8.39$ apart. Neither number looks
wrong. Both are positive, both are finite, and both came out of an expression that
simplified without complaint — which is why forgetting to move the limits is a mistake
that survives being checked over.

There is a check that does catch it, and it costs nothing. The integrand $x e^{x^2}$
exceeds $x$ on $[0,2]$ and $\int_0^2 x\,\mathrm{d}x = 2$; at $x = 2$ alone the
integrand is $2e^4 \approx 109$. An answer of $3.19$ for a function that reaches $109$
on the interval is not credible, and an order-of-magnitude bound of this kind is
available before any substitution is attempted. Module 1's staircase bounds are the same
idea used deliberately: any Riemann sum, however crude, brackets the answer.
"""
                },
            ],
            "quiz": {
                "title": "Substitution done carefully",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Which substitution turns $\int 2x\cos(x^2)\,dx$ into something elementary?",
                        "opts": [r"$u = 2x$", r"$u = \cos(x^2)$", r"$u = x^2$", r"$u = \sin(x^2)$"],
                        "a": 2,
                        "why": (
                            r"Take $u = x^2$; then $du = 2x\,dx$ and the $2x$ already sitting in the integrand is consumed "
                            r"exactly, leaving $\int\cos u\,du = \sin(x^2) + C$. The test for a usable substitution is always "
                            r"the same: is the derivative of the inner function already there, up to a constant? Setting $u$ "
                            r"to the whole $\cos(x^2)$ leaves a stray $\sin$ with nothing to cancel it, and $u = 2x$ does not "
                            r"simplify the argument of the cosine at all."
                        ),
                    },
                    {
                        "q": r"Evaluating $\int_0^2 x\,e^{x^2}\,dx$ with $u = x^2$, what does the integral become?",
                        "opts": [
                            r"$\frac{1}{2}\int_0^2 e^u\,du$",
                            r"$\frac{1}{2}\int_0^4 e^u\,du$",
                            r"$\int_0^4 e^u\,du$",
                            r"$2\int_0^4 e^u\,du$",
                        ],
                        "a": 1,
                        "why": (
                            r"$du = 2x\,dx$, so $x\,dx = \frac{1}{2}du$, which supplies the one half. The limits belong to the "
                            r"variable, so they must be pushed through as well: $x = 0$ gives $u = 0$ and $x = 2$ gives "
                            r"$u = 4$. Carrying the old limits over to the new variable is the commonest error here, and it "
                            r"fails quietly — the arithmetic still completes, it just answers a different question."
                        ),
                    },
                    {
                        "q": r"What is $\int_{-1}^{1} x^3\cos x\,dx$?",
                        "opts": [
                            r"$0$",
                            r"$2\int_0^1 x^3\cos x\,dx$",
                            r"$2\sin 1$",
                            r"It cannot be determined without integrating",
                        ],
                        "a": 0,
                        "why": (
                            r"$x^3$ is odd and $\cos x$ is even, so the product is odd, and an odd integrand over an interval "
                            r"symmetric about the origin contributes equal and opposite amounts on the two sides. Doubling the "
                            r"half-integral is the rule for an even integrand, not an odd one. The symmetry argument is a "
                            r"proof rather than an estimate, so nothing needs integrating — and integrating this directly "
                            r"would cost three rounds of parts."
                        ),
                    },
                    {
                        "q": r"$\int \frac{2x + 3}{x^2 + 3x + 7}\,dx$ equals",
                        "opts": [
                            r"$\ln|x^2 + 3x + 7| + C$",
                            r"$\frac{(2x+3)^2}{2(x^2+3x+7)} + C$",
                            r"$\arctan(x^2 + 3x + 7) + C$",
                            r"$\frac{1}{x^2 + 3x + 7} + C$",
                        ],
                        "a": 0,
                        "why": (
                            r"The numerator is exactly the derivative of the denominator, so with $u = x^2 + 3x + 7$ the whole "
                            r"thing collapses to $\int du/u = \ln|u| + C$. Recognising that pattern is worth more than any "
                            r"table, because it turns a quotient that looks like a partial-fractions job into one line. The "
                            r"absolute value is carried because in general the denominator can go negative, even though this "
                            r"particular quadratic never does."
                        ),
                    },
                    {
                        "q": r"Substituting $x = h(u)$ rather than $u = g(x)$ carries one extra requirement. What is it?",
                        "opts": [
                            r"$h$ must be one-to-one on the interval, so the new limits sweep the old one exactly once",
                            r"$h$ must be a polynomial",
                            r"$h$ must satisfy $h(0) = 0$",
                            r"$h$ must be bounded",
                        ],
                        "a": 0,
                        "why": (
                            r"Running the substitution backwards means every $x$ in the old interval has to come from exactly "
                            r"one $u$ in the new one. If the map doubles back, part of the interval is covered twice and part "
                            r"not at all. That is why $x = a\sin\theta$ is restricted to $-\pi/2 \le \theta \le \pi/2$, and "
                            r"why module 2 chose $x = a + t/(1-t)$, which increases strictly across $[0, 1)$. The forward "
                            r"direction $u = g(x)$ needs no such condition; it is only the chain rule read backwards."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M7
        {
            "title": "Integration by parts and reduction formulae",
            "summary": "The product rule integrated, including the trick of letting an integral appear on both sides of its own equation.",
            "concepts": [
                r"Integration by parts is the product rule integrated: $\int u\,dv = uv - \int v\,du$, trading one integral for another you hope is easier",
                r"Choose $u$ to be the factor that gets simpler when differentiated — logarithm, then inverse trigonometric, then algebraic, then trigonometric, then exponential",
                r"$\int\ln x\,dx$ and $\int\arctan x\,dx$ take $dv = dx$: there is only one factor, and differentiating it is the entire move",
                r"$\int e^{ax}\cos(bx)\,dx$ reproduces itself after two rounds, and the answer comes from solving the resulting equation for the unknown integral",
                r"A reduction formula expresses $\int\sin^n x\,dx$ through $\int\sin^{n-2}x\,dx$, turning an integral into a recurrence with a base case — the same recurrences that generate Fourier coefficients",
                r"The choice of $u$ is not a mnemonic. It is a search for the factor with a *terminating* derivative chain: a polynomial loses one degree per step and stops, an exponential or a sinusoid never changes difficulty in either direction, and one round of the formula shows which way the trade is running",
                r"Solving for a reproduced integral is legal exactly when it comes back with a coefficient other than $1$. The identical manoeuvre on $\int\frac{\mathrm{d}x}{x}$ gives $I = 1 + I$, and cancelling proves $0 = 1$; the sine recurrence is safe because collecting leaves a factor of $n$",
            ],
            "read": [
                {
                    "title": "The product rule backwards, and when solving for the integral is allowed",
                    "minutes": 13,
                    "body": r"""
Substitution inverts the chain rule. Integration by parts inverts the product rule, and
its derivation is the same two lines with a different starting identity. Start from the
product rule,

$$(uv)' = u'v + uv'$$

integrate both sides over $[a,b]$, and apply part two of the Fundamental Theorem to the
left-hand side, which is a derivative:

$$\left[uv\right]_a^b = \int_a^b u'v\,\mathrm{d}x + \int_a^b uv'\,\mathrm{d}x$$

Rearranged, $\int_a^b u\,\mathrm{d}v = \left[uv\right]_a^b - \int_a^b v\,\mathrm{d}u$.
The formula is a *trade*: it does not evaluate anything, it exchanges one integral for
another plus a boundary term you can read off. Whether that is progress depends entirely
on the choice of $u$, and the choice is not a matter of taste.

## LIATE, and the reason underneath it

The usual advice is a mnemonic — logarithmic, inverse trigonometric, algebraic,
trigonometric, exponential — and a mnemonic is a rule with the reason removed. The
reason is that the trade is worth making when $\int v\,\mathrm{d}u$ is a smaller problem
than $\int u\,\mathrm{d}v$, and "smaller" is measurable. Differentiating $x^n$ lowers
the degree by one, so repeated differentiation of a polynomial *terminates* in $n$
steps. Differentiating $e^{x}$ or $\sin x$ changes nothing about the difficulty.
Integrating $e^{x}$ or $\sin x$ also changes nothing about the difficulty. So in
$\int x^n e^{x}\,\mathrm{d}x$ the polynomial must be $u$: it is the only factor with a
terminating chain, and the exponential is the only factor that can be integrated
repeatedly at no cost.

The front of the list has a different reason. $\ln x$ and $\arctan x$ are there not
because they simplify pleasantly but because *nothing else can be done with them*:
neither has an antiderivative you already know, so neither can serve as $\mathrm{d}v$.
For $\int\ln x\,\mathrm{d}x$ the assignment is forced — $u = \ln x$, $\mathrm{d}v = \mathrm{d}x$ — and the technique's contribution is turning an unintegrable factor into
$\frac{1}{x}$, which is integrable against the $v = x$ it is now multiplied by.

## Worked: the wrong choice, carried far enough to see it fail

$\int x e^{x}\,\mathrm{d}x$ with the assignment backwards, $u = e^x$ and $\mathrm{d}v = x\,\mathrm{d}x$:

```
u  = e^x          du = e^x dx
dv = x dx         v  = x^2/2

integral = (x^2/2) e^x - integral of (x^2/2) e^x dx
```

The remaining integral has degree $2$ where the original had degree $1$. Push once more
and it is degree $3$, then $4$. The trade is running the wrong way and it is visible
after a single step, which is the practical test: **do parts once and compare the new
integral with the old one**. If it is worse, swap the assignment. With $u = x$ instead,
$\int x e^x = xe^x - \int e^x = (x-1)e^x + C$, and differentiating that returns
$e^x + (x-1)e^x = xe^x$.

## Solving for the integral, and the coefficient that makes it legal

Some integrands reproduce themselves. $\int e^{x}\sin x\,\mathrm{d}x$, called $I$, gives
after two rounds of parts

$$I = e^{x}\sin x - e^{x}\cos x - I$$

Collecting, $2I = e^{x}(\sin x - \cos x)$, so $I = \frac{1}{2}e^{x}(\sin x - \cos x) + C$. Differentiate to check: $\frac{1}{2}e^x(\sin x - \cos x) + \frac{1}{2}e^x(\cos x + \sin x) = e^x\sin x$.

Now the same move on a different integral. Let $I = \int\frac{\mathrm{d}x}{x}$ and take
$u = \frac{1}{x}$, $\mathrm{d}v = \mathrm{d}x$, so $v = x$ and $\mathrm{d}u = -\frac{\mathrm{d}x}{x^2}$:

$$I = \frac{1}{x}\cdot x - \int x\left(-\frac{1}{x^{2}}\right)\mathrm{d}x
    = 1 + \int\frac{\mathrm{d}x}{x} = 1 + I$$

Cancel $I$ from both sides and $0 = 1$. Every line of that is correct except the last
one, and the last one is the move the previous paragraph just endorsed. The difference
is the coefficient. In the first case the reproduced integral arrived with coefficient
$-1$, so collecting gave $2I$ and dividing by $2$ is legal. Here it arrives with
coefficient $+1$, collecting gives $0 \cdot I = 1$, and dividing by zero is what
produces the contradiction.

There is a second reading of the same fault, and it is worth having both.
$\int\frac{\mathrm{d}x}{x}$ denotes a *family* of functions differing by a constant, not
a number, and the two occurrences of $I$ in $I = 1 + I$ are not the same member of that
family — one is $\ln|x| + C_1$ and the other is $\ln|x| + C_2$, with $C_1 - C_2 = 1$.
Cancelling treats a family as a number. In the definite version the ambiguity is gone
and so is the contradiction: $\int_1^2\frac{\mathrm{d}x}{x} = \left[1\right]_1^2 + \int_1^2\frac{\mathrm{d}x}{x}$ reads $0 = 0$, true and useless.

So the rule is: solving for $I$ is valid exactly when the reproduced integral comes back
with a coefficient other than $1$. Reduction formulae satisfy that condition by
construction, which is the next section.

## A reduction formula, derived, and taken to a number

Let $W_n = \int_0^{\pi/2}\sin^{n}x\,\mathrm{d}x$. Split off one factor of sine to serve
as $\mathrm{d}v$:

```
u  = sin^(n-1) x      du = (n-1) sin^(n-2) x cos x dx
dv = sin x dx         v  = -cos x

W_n = [-sin^(n-1) x cos x] from 0 to pi/2
      + (n-1) * integral of sin^(n-2) x cos^2 x dx
```

The boundary term vanishes at both ends — $\cos\frac{\pi}{2} = 0$ at the top and
$\sin 0 = 0$ at the bottom for $n \ge 2$. Replace $\cos^2 x$ by $1 - \sin^2 x$ and the
remaining integral splits into $W_{n-2} - W_{n}$:

$$W_n = (n-1)\left(W_{n-2} - W_{n}\right) \quad\Rightarrow\quad
n\,W_n = (n-1)W_{n-2} \quad\Rightarrow\quad W_n = \frac{n-1}{n}W_{n-2}$$

The reproduced integral came back with coefficient $-(n-1)$, so collecting gave $n$, and
$n \neq 0$ is exactly the licence the previous section demanded. Two base cases finish
it: $W_0 = \frac{\pi}{2}$ and $W_1 = 1$. Then

```
W_2 = (1/2) W_0 = pi/4      = 0.785398
W_4 = (3/4) W_2 = 3 pi/16   = 0.589049
W_6 = (5/6) W_4 = 5 pi/32   = 0.490874
```

One derivation has answered infinitely many integrals, and it is structurally a
recursive function with a base case. The odd and even branches never mix, which is why
$\pi$ appears in every even $W_n$ and in no odd one.

## Worked: the factor that has no antiderivative of its own

The front of LIATE is where the technique does something no other technique can, and
$\int_0^1\arctan x\,\mathrm{d}x$ is the cleanest example. There is one factor. There is
nothing to substitute, no product to split, and no rational function to decompose —
$\arctan$ is not in the table of antiderivatives at all.

Parts creates the second factor out of nothing by taking $\mathrm{d}v = \mathrm{d}x$:

```
u  = arctan x        du = dx/(1+x^2)
dv = dx              v  = x

integral = [x arctan x] from 0 to 1  -  integral of x/(1+x^2) dx from 0 to 1
         = pi/4                      -  (1/2) ln 2
         = 0.78540 - 0.34657
         = 0.43882
```

The whole move is that differentiating $\arctan$ produces $\frac{1}{1+x^{2}}$, which is
rational — and multiplied by the $v = x$ that has just appeared, it becomes the
$\frac{f'}{f}$ pattern of module 6 and integrates in one step. An unintegrable factor
was converted into an integrable one by differentiating it, which is what parts is for
and what no amount of substitution would have achieved.

Check the size before believing the number: $\arctan x$ runs from $0$ to
$\frac{\pi}{4} = 0.7854$ across $[0,1]$ and is concave, so the answer must lie between
half of $0.7854$ and $0.7854$ itself. It does, at $0.4388$. And check it exactly by
differentiating the antiderivative: $\frac{\mathrm{d}}{\mathrm{d}x}\left(x\arctan x - \frac{1}{2}\ln(1+x^{2})\right) = \arctan x + \frac{x}{1+x^{2}} - \frac{x}{1+x^{2}} = \arctan x$.

$\int\ln x\,\mathrm{d}x = x\ln x - x$ is the same manoeuvre, and module 5 found it by
guessing and correcting instead. The two routes agree because they are the same
calculation: the correction module 5 subtracted is precisely the $\int v\,\mathrm{d}u$
that parts writes down in advance.

## Where this stops holding

Parts trades one integral for another and offers no guarantee the new one is easier. On
$\int e^{x^2}\,\mathrm{d}x$ every assignment produces something worse, and it must,
since module 5 recorded that no elementary antiderivative exists — a technique cannot
manufacture one. On $\int\sin(x^2)\,\mathrm{d}x$ the same. The useful reading of a
failed attempt is that it is evidence about the shape of the integrand, never a
conclusion about the integral.

The tabular short-cut, in which one column is differentiated to zero and the other
integrated repeatedly, is this same formula applied $n$ times with the signs alternating.
It works precisely when one factor's derivative chain terminates, which is the criterion
this reading started from — so it is a layout, not a new method, and it is silent on
every integrand where the polynomial is absent.
"""
                },
            ],
            "derive": [
                {
                    "title": "The sine reduction formula, and the coefficient that licences it",
                    "minutes": 13,
                    "vars": ["n", "x", "W"],
                    "brief": r"""
Write $W_n = \int_0^{\pi/2}\sin^{n}x\,\mathrm{d}x$. One application of integration by
parts turns this into a recurrence, and the recurrence answers every $n$ at once.

Take $u = \sin^{n-1}x$ and $\mathrm{d}v = \sin x\,\mathrm{d}x$. The last two steps are
the ones that matter: the reproduced integral has to come back with a coefficient other
than $1$, or solving for it is the step that proves $0 = 1$.

Write the trigonometric functions as `sin(x)` and `cos(x)`.
""",
                    "steps": [
                        {
                            "prompt": "With $\\mathrm{d}v = \\sin x\\,\\mathrm{d}x$, write $v$.",
                            "answer": "-cos(x)",
                            "placeholder": "?",
                            "hint": "An antiderivative of $\\sin$, and the sign is the whole of the answer.",
                        },
                        {
                            "prompt": "With $u = \\sin^{n-1}x$, write $\\frac{\\mathrm{d}u}{\\mathrm{d}x}$ using the chain rule.",
                            "answer": "(n-1)cos(x)sin(x)^{n-2}",
                            "placeholder": "(n-1) * ... * ...",
                            "hint": "Differentiate the outer power, then multiply by the derivative of $\\sin x$.",
                            "deconstruct": [
                                "The outer function is $t \\mapsto t^{n-1}$, whose derivative is $(n-1)t^{n-2}$.",
                                "The inner function is $\\sin x$, whose derivative is $\\cos x$.",
                            ],
                        },
                        {
                            "prompt": "The leftover integral is $(n-1)\\int_0^{\\pi/2}\\sin^{n-2}x\\,\\cos^{2}x\\,\\mathrm{d}x$, which is not yet a $W$. Rewrite $\\cos^{2}x$ so that it is.",
                            "answer": "1-sin(x)^2",
                            "placeholder": "?",
                            "hint": "The Pythagorean identity, arranged so that only sines are left.",
                        },
                        {
                            "prompt": "The boundary term vanishes at both ends, so $W_n = (n-1)\\left(W_{n-2} - W_n\\right)$. Collect the $W_n$ terms on the left and write the coefficient multiplying $W_n$ there.",
                            "answer": "n",
                            "placeholder": "?",
                            "hint": "One $W_n$ is already on the left and $(n-1)$ more come across from the right.",
                            "deconstruct": [
                                "$W_n + (n-1)W_n = (n-1)W_{n-2}$.",
                                "The left-hand side is $\\left(1 + n - 1\\right)W_n$.",
                            ],
                        },
                        {
                            "prompt": "Divide by that coefficient. Writing $W$ for $W_{n-2}$, write $W_n$.",
                            "answer": "\\frac{n-1}{n}W",
                            "placeholder": "? * W",
                            "hint": "The recurrence steps down by two, never by one, so the even and odd families never meet.",
                        },
                        {
                            "prompt": "Apply that recurrence three times starting from $W_0 = \\frac{\\pi}{2}$, and write $W_6$.",
                            "answer": "\\frac{5\\pi}{32}",
                            "placeholder": "?",
                            "hint": "$W_2 = \\frac{1}{2}W_0$, then $W_4 = \\frac{3}{4}W_2$, then $W_6 = \\frac{5}{6}W_4$.",
                            "deconstruct": [
                                "$W_2 = \\frac{1}{2}\\cdot\\frac{\\pi}{2} = \\frac{\\pi}{4}$.",
                                "$W_4 = \\frac{3}{4}\\cdot\\frac{\\pi}{4} = \\frac{3\\pi}{16}$.",
                                "$W_6 = \\frac{5}{6}\\cdot\\frac{3\\pi}{16} = \\frac{15\\pi}{96}$, which reduces.",
                            ],
                        },
                    ],
                    "closing": r"""
$W_6 = \frac{5\pi}{32} = 0.490874$. Check the size before believing it: $\sin^{6}x$ sits
below $1$ across $\left[0,\frac{\pi}{2}\right]$ and is small over most of it, so an
answer somewhere under $\frac{\pi}{2} = 1.5708$ and above zero is what to expect, and
$0.49$ is plausible where $4.9$ would not have been.

Step four is where the whole method rests. The reproduced integral came back with
coefficient $-(n-1)$, collecting produced $n$, and dividing by $n$ is legal for every
$n \ge 1$. Run the same manoeuvre on $\int\frac{\mathrm{d}x}{x}$ with $u = \frac1x$ and
$\mathrm{d}v = \mathrm{d}x$ and the integral comes back with coefficient $+1$: collecting
gives $0 \cdot I = 1$, and the division that looked identical is a division by zero. The
recurrence above is safe not because it is a reduction formula but because $n \neq 0$.

Odd $n$ runs down to $W_1 = 1$ and never meets a $\pi$; even $n$ runs down to
$W_0 = \frac{\pi}{2}$ and always carries one. Taking the ratio of the two families as
$n$ grows is how Wallis obtained his product for $\pi$ — from this recurrence and
nothing else.
"""
                },
            ],
            "quiz": {
                "title": "Choosing u, and knowing when to stop",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"For $\int x\,e^x\,dx$, which assignment leaves an easier integral behind?",
                        "opts": [
                            r"$u = x$ and $dv = e^x\,dx$",
                            r"$u = e^x$ and $dv = x\,dx$",
                            r"$u = x e^x$ and $dv = dx$",
                            r"Both of the first two work equally well",
                        ],
                        "a": 0,
                        "why": (
                            r"Differentiating $x$ gives $1$ and removes the algebraic factor entirely, leaving "
                            r"$xe^x - \int e^x\,dx$. Differentiating the exponential instead never simplifies anything, and "
                            r"integrating $x$ into $x^2/2$ makes the remaining integral worse than the original — a reliable "
                            r"sign that the assignment was backwards. Taking the whole product as $u$ simply reproduces the "
                            r"problem you started with."
                        ),
                    },
                    {
                        "q": r"$\int \ln x\,dx$ equals",
                        "opts": [
                            r"$\frac{1}{x} + C$",
                            r"$x\ln x - x + C$",
                            r"$x\ln x + C$",
                            r"$\frac{(\ln x)^2}{2} + C$",
                        ],
                        "a": 1,
                        "why": (
                            r"With $u = \ln x$ and $dv = dx$ the formula gives $x\ln x - \int x\cdot\frac{1}{x}\,dx = "
                            r"x\ln x - x + C$. Differentiating the result is the cheapest possible check: "
                            r"$\ln x + 1 - 1 = \ln x$. The answer $\frac{(\ln x)^2}{2}$ belongs to "
                            r"$\int\frac{\ln x}{x}\,dx$, which is a substitution rather than a parts problem, and $1/x$ is "
                            r"the derivative of the integrand instead of its integral."
                        ),
                    },
                    {
                        "q": r"In $\int e^x \sin x\,dx$, two rounds of parts bring the original integral back on the right-hand side. What now?",
                        "opts": [
                            r"Apply parts a third time",
                            r"Conclude that the integral does not exist",
                            r"Treat the integral as an unknown and solve the equation for it",
                            r"Abandon parts and use a substitution",
                        ],
                        "a": 2,
                        "why": (
                            r"Two rounds give $I = e^x\sin x - e^x\cos x - I$, an ordinary linear equation whose solution is "
                            r"$I = \frac{1}{2}e^x(\sin x - \cos x) + C$. A third round walks straight back to the starting "
                            r"point, because sine and cosine close under differentiation after two steps. The integral "
                            r"certainly exists — the integrand is continuous everywhere — and no substitution touches it, "
                            r"since neither factor is the derivative of the other. The cancellation is legal here because "
                            r"the integral returns with coefficient $-1$, so collecting leaves $2I$. Run the same "
                            r"manoeuvre on $\int\frac{\mathrm{d}x}{x}$ and it returns with coefficient $+1$: collecting "
                            r"gives $0\cdot I = 1$, and the identical-looking final step is a division by zero."
                        ),
                    },
                    {
                        "q": r"What is a reduction formula for?",
                        "opts": [
                            r"Reducing the number of significant figures the answer needs",
                            r"Expressing an integral through the same integral with a smaller exponent, applied repeatedly down to a base case",
                            r"Turning a definite integral into an indefinite one",
                            r"Rewriting a product of two functions as their quotient",
                        ],
                        "a": 1,
                        "why": (
                            r"It converts one integral into a recurrence: $\int\sin^n$ in terms of $\int\sin^{n-2}$, applied "
                            r"until the exponent reaches $0$ or $1$, where the answer is immediate. Structurally it is a "
                            r"recursive function with a base case, and it is how one derivation covers an infinite family of "
                            r"integrals instead of doing $n$ separate ones."
                        ),
                    },
                    {
                        "q": r"What is $\int_0^{\pi} x\sin x\,dx$?",
                        "opts": [r"$\pi$", r"$0$", r"$2$", r"$-\pi$"],
                        "a": 0,
                        "why": (
                            r"With $u = x$ and $dv = \sin x\,dx$ the boundary term $[-x\cos x]_0^{\pi}$ contributes $\pi$, and "
                            r"the leftover $\int_0^{\pi}\cos x\,dx$ contributes nothing, so the value is $\pi$. Both pieces "
                            r"have to be evaluated at the limits; dropping the boundary term is what produces $0$. A quick "
                            r"sanity check settles the sign: the integrand is non-negative across $[0, \pi]$, so a negative "
                            r"answer cannot be right."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M8
        {
            "title": "Trigonometric integrals and trigonometric substitution",
            "summary": "The identities that make squared and mixed sinusoids integrable, and the substitutions that clear a square root.",
            "concepts": [
                r"Power reduction: $\cos^2\theta = \frac{1 + \cos 2\theta}{2}$, so a squared sinusoid averages to $\frac{1}{2}$ over a period — the reason an RMS value is the peak divided by $\sqrt{2}$",
                r"An odd power of sine or cosine peels off one factor to serve as $du$; an even power has to go through the double-angle identities first",
                r"Orthogonality: over a full period $\int\sin(mx)\sin(nx)$ and $\int\sin(mx)\cos(nx)$ vanish unless the frequencies match, which is what every Fourier coefficient formula rests on",
                r"The three substitutions: $x = a\sin\theta$ for $\sqrt{a^2 - x^2}$, $x = a\tan\theta$ for $\sqrt{a^2 + x^2}$, $x = a\sec\theta$ for $\sqrt{x^2 - a^2}$",
                r"Complete the square first to reach one of those three forms, and come back through a right triangle rather than through nested inverse functions",
            ],
            "read": [
                {
                    "title": "Which products vanish, computed rather than remembered",
                    "minutes": 13,
                    "body": r"""
A signal is a sum of sinusoids and you want one of them out. Multiply the signal by
$\sin(3x)$, integrate over a full period, and the answer is the amount of $\sin(3x)$
that was in it — every other component contributes nothing. That procedure is the whole
of Fourier analysis, and it works only because of three definite integrals. This module
lists them; here they are computed, because one of the three behaves differently from
the way the list suggests and the difference is what makes the procedure work at all.

## Power reduction, derived from one identity

The addition formula gives $\cos(2\theta) = \cos^{2}\theta - \sin^{2}\theta$, and
$\cos^{2}\theta + \sin^{2}\theta = 1$. Add and subtract:

$$\cos^{2}\theta = \frac{1 + \cos 2\theta}{2}, \qquad
  \sin^{2}\theta = \frac{1 - \cos 2\theta}{2}$$

Nothing here is a new fact. Both are the addition formula rearranged, and both say the
same thing: a squared sinusoid is a constant $\frac{1}{2}$ plus a sinusoid at twice the
frequency. Over a whole number of periods the doubled sinusoid integrates to zero, so
the mean of $\sin^{2}$ is exactly $\frac{1}{2}$ — not approximately, and not because of
any symmetry argument about halves.

The engineering consequence follows in one line. The root mean square of $V\sin\omega t$
is $\sqrt{V^{2}\cdot\frac{1}{2}} = \frac{V}{\sqrt2}$, so a supply quoted at
$230\,\mathrm{V}$ RMS has a peak of $230\sqrt2 = 325.3\,\mathrm{V}$, and insulation is
specified against the peak while heating is computed from the RMS. Module 10 returns to
why squaring first is the right average for power.

## The three orthogonality integrals

Take $m$ and $n$ positive integers and integrate over $[0, 2\pi]$. Every one of these
comes from a product-to-sum identity followed by the observation that
$\int_0^{2\pi}\cos(kx)\,\mathrm{d}x = 0$ for every non-zero integer $k$, since $\cos(kx)$
completes $|k|$ whole cycles.

$$\sin(mx)\sin(nx) = \frac{\cos\left((m-n)x\right) - \cos\left((m+n)x\right)}{2}$$

For $m \neq n$ both cosines have non-zero frequency and both integrate to zero, so the
whole thing is $0$. For $m = n$ the first term becomes $\cos 0 = 1$, whose integral over
$[0,2\pi]$ is $2\pi$, and half of that is $\pi$. The cosine pair behaves identically:
$\int_0^{2\pi}\cos(mx)\cos(nx)\,\mathrm{d}x$ is $0$ when $m \neq n$ and $\pi$ when
$m = n$.

Now the mixed pair, which is the one worth doing carefully:

$$\sin(mx)\cos(nx) = \frac{\sin\left((m+n)x\right) + \sin\left((m-n)x\right)}{2}$$

For $m \neq n$ both sines integrate to zero over the period. And when $m = n$ the second
term is $\sin 0 = 0$ identically while the first is $\sin(2nx)$, which also integrates
to zero — so

$$\int_0^{2\pi}\sin(mx)\cos(nx)\,\mathrm{d}x = 0
\qquad\text{for every } m \text{ and } n \text{, including } m = n$$

This is not the same shape of result as the other two, and the difference is
load-bearing. A sine and a cosine at the *same* frequency are orthogonal. Nothing about
matching frequencies rescues them, because $\sin(nx)\cos(nx) = \frac{1}{2}\sin(2nx)$ is a
pure sinusoid at double the frequency and has mean zero like any other.

## Why that third integral is the one that matters

Suppose the mixed integral were $\pi$ at $m = n$, as the other two are. Then extracting
the sine coefficient at frequency $3$ would also pick up whatever cosine content sat at
frequency $3$, the two coefficients could not be separated, and the decomposition would
not be a decomposition. Watch it work on a signal where the answer is known:

$$f(x) = 2\sin 3x + 5\cos 3x - \sin 5x$$

```
b_3 = (1/pi) * integral of f(x) sin(3x) dx over [0, 2pi]

  from 2 sin3x  :  (1/pi) * 2 * pi        =  2     (m = n, sine-sine)
  from 5 cos3x  :  (1/pi) * 5 * 0         =  0     (m = n, sine-cosine)
  from -sin5x   :  (1/pi) * (-1) * 0      =  0     (m /= n, sine-sine)
                                          ------
                                             2
```

The $5\cos 3x$ term is at *exactly* the frequency being extracted, carries more than
twice the amplitude of the term being looked for, and contributes nothing. That is the
mixed integral doing its job.

## Odd powers, even powers, and which one is cheap

A single odd power is a substitution in disguise. In $\int\sin^{3}x\cos^{2}x\,\mathrm{d}x$
peel one sine off to be $\mathrm{d}u$ for $u = \cos x$, and convert what is left with the
Pythagorean identity, which is possible precisely because the remaining power is even:

```
sin^3 x cos^2 x dx = (1 - cos^2 x) cos^2 x * sin x dx
                   = -(1 - u^2) u^2 du            u = cos x, du = -sin x dx

integral = -(u^3/3 - u^5/5) + C
         = cos^5(x)/5 - cos^3(x)/3 + C
```

Differentiating that returns $-\cos^{4}x\sin x + \cos^{2}x\sin x = \cos^{2}x\sin x\left(1-\cos^{2}x\right) = \sin^{3}x\cos^{2}x$. When *both* powers are even no factor
can be peeled off, the substitution is unavailable, and the double-angle identities from
the first section have to reduce the powers instead — at roughly one identity per two
degrees, which is why an even-even integrand costs several times what an odd one does.

## Clearing a root, and the modulus that decides the sign

Three substitutions, one per shape, each turning a sum or difference of squares into a
single square by a Pythagorean identity:

```
sqrt(a^2 - x^2)     x = a sin(t)     gives a|cos t|
sqrt(a^2 + x^2)     x = a tan(t)     gives a|sec t|
sqrt(x^2 - a^2)     x = a sec(t)     gives a|tan t|
```

Every one produces a modulus, and every one is made harmless by restricting $t$ to the
range on which the inner function is non-negative — which is also the range on which the
substitution is one-to-one, the condition module 6 established for a reverse
substitution. The two requirements are the same requirement.

Worked, end to end:

$$\int_0^{3}\frac{\mathrm{d}x}{\sqrt{9+x^{2}}}$$

```
x = 3 tan t         dx = 3 sec^2 t dt
9 + x^2 = 9 sec^2 t     sqrt(...) = 3 sec t     for t in [0, pi/4]

limits  x = 0 -> t = 0        x = 3 -> t = pi/4

integral = integral of sec t dt from 0 to pi/4
         = [ln|sec t + tan t|] from 0 to pi/4
         = ln(sqrt2 + 1) - ln(1)
         = 0.8814
```

Sanity-check the magnitude without integrating: the integrand runs from $\frac{1}{3}$ at
$x=0$ down to $\frac{1}{3\sqrt2} = 0.2357$ at $x=3$, so the answer lies between
$3 \times 0.2357 = 0.707$ and $3 \times 0.333 = 1.0$. It does.

## The mistake, and why it is tempting

After $x = 3\tan t$ the answer has to come back to $x$, and the tempting route is to
invert the substitution literally: $t = \arctan\frac{x}{3}$, then write
$\sec\left(\arctan\frac{x}{3}\right)$ and stop. It is correct and it is unusable — no
further algebra will simplify it, and a second substitution downstream will not survive
it.

The right-triangle route is faster and produces something a later step can work with.
Draw the triangle in which $\tan t = \frac{x}{3}$: opposite $x$, adjacent $3$,
hypotenuse $\sqrt{9+x^{2}}$. Then $\sec t = \frac{\sqrt{9+x^{2}}}{3}$ and $\sin t = \frac{x}{\sqrt{9+x^{2}}}$, read straight off. The temptation exists because inverting a
function is the obvious thing to do to undo it; the triangle wins because it converts
the inverse into algebra rather than leaving it as a composition.

## Where this stops holding

The three substitutions match three shapes and nothing else, so the first move on a
general quadratic under a root is to complete the square and *make* one of the shapes
appear. $\sqrt{x^{2}-6x+13}$ has discriminant $36 - 52 = -16$, so it never factors over
the reals and no algebraic route is available — but completing the square gives
$\sqrt{(x-3)^{2}+4}$, the middle shape with $u = x - 3$ and $a = 2$.

Orthogonality itself is stated above over $[0,2\pi]$ with integer frequencies, and
neither condition is negotiable. Over a partial period the integrals are not zero, which
is why a finite record of a signal must be windowed before its spectrum means anything;
and for non-integer frequency ratios the components are not orthogonal at all, which is
the leakage that appears in every real spectrum. Module 4's convergence tests decide
whether the resulting Fourier series converges; these integrals only produce its
coefficients.
"""
                },
            ],
            "derive": [
                {
                    "title": "Three orthogonality integrals, and the one that is zero even at equal frequencies",
                    "minutes": 12,
                    "vars": ["m", "n", "x"],
                    "brief": r"""
Everything below is over $[0, 2\pi]$ with $m$ and $n$ positive integers, and everything
rests on one fact: $\int_0^{2\pi}\cos(kx)\,\mathrm{d}x = 0$ for every non-zero integer
$k$, because $\cos(kx)$ completes $|k|$ whole cycles.

Write the trigonometric functions as `sin(...)` and `cos(...)`. The last two steps
settle the mixed sine-cosine case, which does not behave like the other two.
""",
                    "steps": [
                        {
                            "prompt": "Use the product-to-sum identity to rewrite $\\sin(mx)\\sin(nx)$ as a combination of two cosines.",
                            "answer": "\\frac{cos((m-n)x)-cos((m+n)x)}{2}",
                            "placeholder": "(cos(...) - cos(...))/2",
                            "hint": "Subtract $\\cos(A+B) = \\cos A\\cos B - \\sin A\\sin B$ from $\\cos(A-B) = \\cos A\\cos B + \\sin A\\sin B$, then halve.",
                            "deconstruct": [
                                "$\\cos(A-B) - \\cos(A+B) = 2\\sin A\\sin B$.",
                                "Put $A = mx$ and $B = nx$, then divide by $2$.",
                            ],
                        },
                        {
                            "prompt": "Write the value of $\\int_0^{2\\pi}\\cos(kx)\\,\\mathrm{d}x$ for a non-zero integer $k$.",
                            "answer": "0",
                            "placeholder": "?",
                            "hint": "The antiderivative is $\\frac{\\sin(kx)}{k}$, and $\\sin$ takes the same value at $0$ and at $2k\\pi$.",
                        },
                        {
                            "prompt": "For $m \\neq n$, both frequencies $m-n$ and $m+n$ in step one are non-zero. Write $\\int_0^{2\\pi}\\sin(mx)\\sin(nx)\\,\\mathrm{d}x$.",
                            "answer": "0",
                            "placeholder": "?",
                            "hint": "Both terms are covered by step two.",
                        },
                        {
                            "prompt": "For $m = n$ the first cosine becomes $\\cos 0 = 1$ while the second still integrates to zero, so the integrand averages $\\frac{1}{2}$ over $[0, 2\\pi]$. Write the value of the integral.",
                            "answer": "\\pi",
                            "placeholder": "?",
                            "hint": "$\\int_0^{2\\pi}\\frac{1}{2}\\,\\mathrm{d}x$, and the second term contributes nothing.",
                        },
                        {
                            "prompt": "Now the mixed pair at equal frequencies. Write $\\sin(nx)\\cos(nx)$ as a single sinusoid.",
                            "answer": "\\frac{sin(2nx)}{2}",
                            "placeholder": "sin(...)/2",
                            "hint": "The double-angle formula $\\sin 2A = 2\\sin A\\cos A$, rearranged.",
                        },
                        {
                            "prompt": "Write $\\int_0^{2\\pi}\\sin(nx)\\cos(nx)\\,\\mathrm{d}x$.",
                            "answer": "0",
                            "placeholder": "?",
                            "hint": "It is a pure sinusoid at frequency $2n$, which is a non-zero integer, so step two applies to it unchanged.",
                        },
                    ],
                    "closing": r"""
Two of the three integrals are $\pi$ when the frequencies agree and $0$ otherwise. The
third — the mixed sine-cosine pair — is **zero for every $m$ and $n$, the equal case
included**, and steps five and six are the computation rather than an assertion. It does
not fit the pattern of the other two, and that is exactly what makes the Fourier
decomposition possible: the sine coefficient at frequency $n$ cannot be contaminated by
the cosine content at that same frequency, so the two families are extracted
independently.

Try it on $f(x) = 2\sin 3x + 5\cos 3x - \sin 5x$. Multiplying by $\sin 3x$ and
integrating over $[0,2\pi]$ picks up $2\pi$ from the first term, $0$ from the second by
step six, and $0$ from the third by step three. Dividing by $\pi$ returns $2$, the
coefficient that was there. The $5\cos 3x$ term is more than twice the size of the one
being measured, sits at precisely the frequency being measured, and contributes nothing
at all.
"""
                },
            ],
            "quiz": {
                "title": "Squares, products and square roots",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"What is the average value of $\sin^2(\omega t)$ over one full period?",
                        "opts": [r"$0$", r"$\frac{1}{2}$", r"$\frac{1}{\sqrt{2}}$", r"$1$"],
                        "a": 1,
                        "why": (
                            r"Rewrite it as $\frac{1 - \cos 2\omega t}{2}$. The cosine completes whole cycles over a period and "
                            r"averages to nothing, leaving $\frac{1}{2}$. Taking the square root of that mean is what produces "
                            r"the RMS value, so $\frac{1}{\sqrt{2}}$ is the RMS of the sinusoid rather than the mean of its "
                            r"square; and $0$ is the average of the raw $\sin$, not of $\sin^2$, which is never negative."
                        ),
                    },
                    {
                        "q": r"What is $\int_0^{2\pi}\sin(3x)\cos(5x)\,dx$?",
                        "opts": [r"$0$", r"$\pi$", r"$2\pi$", r"It depends on the phase"],
                        "a": 0,
                        "why": (
                            r"A product-to-sum identity turns it into $\frac{1}{2}\int[\sin(8x) - \sin(2x)]\,dx$, and both "
                            r"sinusoids complete a whole number of cycles across $[0, 2\pi]$, so both integrate to nothing. "
                            r"Sines and cosines at integer multiples of one frequency are orthogonal in exactly this sense, "
                            r"which is what lets a Fourier coefficient be extracted by multiplying the signal by one harmonic "
                            r"and integrating: every other harmonic contributes zero. The value $\pi$ is what appears when the "
                            r"frequencies do match and the two factors are the same kind of function — sine against sine, or "
                            r"cosine against cosine. The mixed pair never produces it: $\int_0^{2\pi}\sin(mx)\cos(nx)\,dx$ is "
                            r"zero for every $m$ and $n$ including $m = n$, since $\sin(nx)\cos(nx) = \frac{1}{2}\sin(2nx)$. "
                            r"That is the case the extraction actually depends on, because it is what stops the cosine content "
                            r"at the very frequency being measured from contaminating the sine coefficient."
                        ),
                    },
                    {
                        "q": r"What is the right first move for $\int\sin^3 x\cos^2 x\,dx$?",
                        "opts": [
                            r"Write $\sin^3 x = (1 - \cos^2 x)\sin x$ and substitute $u = \cos x$",
                            r"Substitute $u = \sin x$ directly",
                            r"Integrate by parts with $u = \sin^3 x$",
                            r"Apply the double-angle identity to both factors",
                        ],
                        "a": 0,
                        "why": (
                            r"The sine carries an odd power, so one factor of $\sin x$ can be set aside to become $du$ for "
                            r"$u = \cos x$, and the even remainder $\sin^2 x$ converts to $1 - \cos^2 x$ by the Pythagorean "
                            r"identity. What is left is a polynomial in $u$. Substituting $u = \sin x$ fails because "
                            r"$du = \cos x\,dx$ needs an odd power of cosine and this one is even. Double-angle identities are "
                            r"the tool when both powers are even, and they cost considerably more work."
                        ),
                    },
                    {
                        "q": r"Which substitution clears the root in $\int\frac{dx}{\sqrt{9 + x^2}}$?",
                        "opts": [r"$x = 3\sin\theta$", r"$x = 3\tan\theta$", r"$x = 3\sec\theta$", r"$u = 9 + x^2$"],
                        "a": 1,
                        "why": (
                            r"With $x = 3\tan\theta$, $9 + x^2 = 9(1 + \tan^2\theta) = 9\sec^2\theta$, and the square root "
                            r"comes out as $3\sec\theta$ with no root left. The sine substitution is built for "
                            r"$a^2 - x^2$ and here would leave $9 + 9\sin^2\theta$, which factors into nothing useful. A plain "
                            r"$u = 9 + x^2$ fails for a different reason: $du = 2x\,dx$ and there is no $x$ in the numerator to "
                            r"supply it."
                        ),
                    },
                    {
                        "q": r"What should you do to $\int\frac{dx}{\sqrt{x^2 - 6x + 13}}$ before choosing a substitution?",
                        "opts": [
                            r"Expand the bracket",
                            r"Complete the square to reach $\sqrt{(x - 3)^2 + 4}$",
                            r"Factor the quadratic into linear terms",
                            r"Split it into partial fractions",
                        ],
                        "a": 1,
                        "why": (
                            r"Completing the square turns the quadratic into $(x-3)^2 + 4$, which is the $a^2 + u^2$ pattern "
                            r"with $u = x - 3$ and $a = 2$, so $u = 2\tan\theta$ finishes the job. Factoring into real linear "
                            r"terms is impossible — the discriminant $36 - 52$ is negative — and partial fractions applies to "
                            r"rational functions, not to something sitting under a square root."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M9
        {
            "title": "Rational functions and partial fractions",
            "summary": "Breaking a quotient of polynomials into pieces small enough that each one is a logarithm or an arctangent.",
            "concepts": [
                r"Divide first: the decomposition only exists once the numerator's degree is below the denominator's, so a polynomial long division comes before anything else",
                r"Factor the denominator; each distinct linear factor $(x - r)$ contributes one term $A/(x - r)$, and the cover-up method reads $A$ off in a single step",
                r"A repeated factor $(x - r)^m$ needs one term for every power from $1$ to $m$, not only the highest",
                r"An irreducible quadratic contributes $(Ax + B)/(x^2 + bx + c)$, which after completing the square splits into a logarithm plus an arctangent",
                r"This is the same algebra that splits a transfer function into its poles before an inverse transform, so the decompositions written here reappear unchanged in later courses",
                r"The decomposition exists and is unique by a counting argument: over the reals every denominator factors into linear and irreducible quadratic pieces, those contribute exactly $\deg Q$ unknown coefficients, and clearing denominators gives exactly $\deg Q$ equations",
                r"Cover-up reads off only the *highest* power of a repeated factor, because the lower terms vanish at the root as well — so a repeated factor needs one comparison of coefficients after the two easy evaluations",
                r"Check the finished decomposition at a value of $x$ that was not used to build it. One substitution, and it catches every sign error, which is where the failures actually are",
                r"Near-equal roots make the coefficients enormous while the function stays smooth: $\frac{1}{(x-1)(x-1.001)}$ decomposes with $\pm 1000$, so every evaluation subtracts nearly equal numbers. That is module 3's catastrophic cancellation arriving by another route, and it is a defect of the parametrisation rather than of the integrand",
            ],
            "read": [
                {
                    "title": "Why the decomposition exists, and what its coefficients cost",
                    "minutes": 12,
                    "body": r"""
Partial fractions is the one technique in this half of the course that is not an
integration technique. It integrates nothing. It is an algebraic identity applied
*before* integrating, chosen because it converts a quotient that no rule handles into a
sum of pieces that two rules handle completely — every proper rational function
integrates to logarithms, arctangents and rational terms, and to nothing else. That is a
strong claim, and it deserves a reason.

## Why every proper rational function splits

Start from where the pieces come from. A real polynomial $Q$ of degree $d$ has $d$ roots
in the complex numbers, counted with multiplicity — the fundamental theorem of algebra —
and because $Q$ has real coefficients its non-real roots arrive in conjugate pairs. Each
pair $r, \bar r$ multiplies back into $(x-r)(x-\bar r) = x^{2} - 2\,\mathrm{Re}(r)\,x + |r|^{2}$, a real quadratic with negative discriminant. So over the reals every $Q$
factors into linear factors and irreducible quadratics, and the list of possible
denominators in the decomposition is fixed by that factorisation and by nothing else.

Now count. A factor $(x-r)^{m}$ contributes $m$ unknown numerators $A_1,\ldots,A_m$, one
per power; an irreducible $(x^{2}+bx+c)^{m}$ contributes $2m$, since each numerator is
linear. Adding over the whole factorisation gives exactly $\deg Q$ unknowns. Clearing
denominators turns the identity into an equality of two polynomials of degree less than
$\deg Q$, which is $\deg Q$ coefficient equations. A square system — and it is
non-singular, so the decomposition exists and is unique. That is the derivation behind
the rule "one term for every power from $1$ to $m$": leave out the lower powers and the
system has fewer unknowns than equations and generically no solution at all.

The properness condition enters before any of this. If $\deg P \ge \deg Q$ no sum of
terms with smaller numerators can produce the leading behaviour, so divide first:
$\frac{x^{3}}{x^{2}-1} = x + \frac{x}{x^{2}-1}$, and only the remainder is decomposed.

## Cover-up, derived, and the case it cannot reach

For a *simple* linear factor the coefficient is one evaluation. Write
$\frac{P(x)}{Q(x)} = \frac{A}{x-r} + \left(\text{the rest}\right)$ and multiply through
by $(x-r)$:

$$\frac{P(x)}{Q(x)}\,(x-r) = A + (x-r)\left(\text{the rest}\right)$$

Every other term still carries a factor $(x-r)$, so letting $x \to r$ annihilates all of
them and leaves $A$ alone. That is the whole justification, and it explains the
restriction as well: for a repeated factor $(x-r)^{m}$, multiplying by $(x-r)^{m}$ and
setting $x = r$ delivers only $A_m$, the top coefficient, because the lower terms
$A_{m-1}(x-r), A_{m-2}(x-r)^2,\ldots$ also vanish there. The lower coefficients need
either derivatives at $r$ or one round of matching.

Worked, all three coefficients, on $\frac{1}{x(x-2)^{2}}$:

```
A/x + B/(x-2) + C/(x-2)^2

A   cover x        : 1/(0-2)^2 = 1/4
C   cover (x-2)^2  : 1/2       = 1/2
B   match x^2      : A + B = 0  =>  B = -1/4
```

The $x^{2}$ coefficient is the cheapest of the remaining equations: clearing
denominators gives $1 = A(x-2)^{2} + Bx(x-2) + Cx$, and only $A$ and $B$ produce an
$x^{2}$ term, so $A + B = 0$ immediately. Check the whole decomposition at a value that
was never used to build it — $x = 1$:

```
left   1/(1 * (1-2)^2)                 = 1
right  (1/4)/1 + (-1/4)/(-1) + (1/2)/1 = 0.25 + 0.25 + 0.5 = 1
```

The check costs one substitution and catches every sign error, which is the most common
failure here by a distance.

## The shape of the answer, which the decomposition has already decided

Integrate the three pieces and notice that the *kind* of function each produces was
fixed the moment the denominator was factored:

```
A/x          -> A ln|x|                    simple linear   -> logarithm
B/(x-2)      -> B ln|x-2|                  simple linear   -> logarithm
C/(x-2)^2    -> -C/(x-2)                   repeated linear -> rational term
```

A repeated factor never produces a logarithm from its highest power; it produces a
rational function. So

$$\int_3^4\frac{\mathrm{d}x}{x(x-2)^{2}}
 = \left[\frac{1}{4}\ln|x| - \frac{1}{4}\ln|x-2| - \frac{1}{2(x-2)}\right]_3^4
 = \frac{1}{4}\ln\frac{2}{3} + \frac{1}{4} = 0.14863$$

The interval $[3,4]$ was chosen to avoid the poles at $0$ and $2$; over $[1,3]$ the same
bracket would produce a number and mean nothing, for module 1's reason.

The irreducible quadratic splits into one of each kind. In
$\int\frac{3x+5}{x^{2}+4x+13}\,\mathrm{d}x$, write the numerator as a multiple of the
denominator's derivative plus a remainder — $3x + 5 = \frac{3}{2}(2x+4) - 1$ — so the
first part is the $\frac{f'}{f}$ pattern of module 6 and the second is an arctangent
after completing the square, $x^{2}+4x+13 = (x+2)^{2}+9$:

$$\frac{3}{2}\ln\left(x^{2}+4x+13\right) - \frac{1}{3}\arctan\frac{x+2}{3} + C$$

Differentiating that returns $\frac{3x+5}{x^{2}+4x+13}$, which is the check that should
follow every one of these.

## Worked: the division that has to come first

$$\int_2^3\frac{x^{3}}{x^{2}-1}\,\mathrm{d}x$$

Degree three over degree two, so no decomposition of any shape can produce it — a sum of
terms $\frac{A}{x-1} + \frac{B}{x+1}$ tends to zero at infinity while $\frac{x^{3}}{x^{2}-1}$
grows without bound, so they cannot be equal for large $x$ and therefore cannot be equal
anywhere. That argument is worth having, because it says *why* properness is required
rather than treating it as a step in a procedure.

Divide, then decompose only what is left:

```
x^3 / (x^2 - 1)  =  x  +  x/(x^2 - 1)          quotient x, remainder x

x/(x^2-1) = x/((x-1)(x+1))
          = A/(x-1) + B/(x+1)

  A   cover (x-1) : 1/(1+1)  = 1/2
  B   cover (x+1) : -1/(-1-1) = 1/2

integral = x^2/2 + (1/2) ln|x-1| + (1/2) ln|x+1|
         = x^2/2 + (1/2) ln|x^2 - 1|

  at x = 3 :  4.5 + (1/2) ln 8  =  4.5 + 1.03972  =  5.53972
  at x = 2 :  2.0 + (1/2) ln 3  =  2.0 + 0.54931  =  2.54931
                                                     -------
                                                     2.99042
```

Both cover-up evaluations returned $\frac{1}{2}$, which looks like an error and is not:
the numerator $x$ takes the values $1$ and $-1$ at the two roots, and so does the
surviving factor, so the two quotients agree. Substituting $x = 0$ into the decomposition
checks it — $\frac{1/2}{-1} + \frac{1/2}{1} = 0$, and $\frac{0}{-1} = 0$.

The polynomial part carried most of the answer: $\frac{x^{2}}{2}$ contributes $2.5$ of
the $2.99$, and the two logarithms $0.49$ between them. Skipping the division does not
merely make the algebra harder; it discards the term that dominates.

## The mistake, and why it is tempting

Reaching for partial fractions on sight of a quotient. It is a general method, so it
always applies, and that is exactly what makes it the wrong first move:
$\int\frac{2x}{x^{2}+1}\,\mathrm{d}x$ is a one-line logarithm because the numerator is
the derivative of the denominator, and decomposing it instead means factoring $x^{2}+1$
over the complex numbers and recombining two complex logarithms into an answer that was
available immediately. The order that saves work is to check for $\frac{f'}{f}$ first, a
substitution second, and the decomposition only when both fail.

## Where this stops holding

The method needs the denominator **factored**, and the theory that guarantees a
factorisation exists does not supply one. Abel and Ruffini proved that the roots of a
general quintic cannot be written in radicals, so there are perfectly ordinary rational
integrands whose decomposition is not obtainable in closed form at all. The technique is
complete in principle and blocked in practice, and where it blocks, module 2's quadrature
answers the definite integral anyway.

It also degrades quietly when two roots are close. For $\frac{1}{(x-1)(x-1.001)}$ the
cover-up method gives $A = \frac{1}{1-1.001} = -1000$ and $B = +1000$: two huge
coefficients whose sum has to reproduce a small function, so every evaluation subtracts
nearly equal numbers and loses digits — module 3's catastrophic cancellation, arriving
by a different route. As the roots merge the coefficients diverge while the function
itself tends smoothly to $\frac{1}{(x-1)^{2}}$, which has a perfectly well-behaved
decomposition of its own. The instability is in the parametrisation, not in the
integrand, and that is worth recognising before trusting a decomposition computed in
floating point.
"""
                },
            ],
            "derive": [
                {
                    "title": "Three coefficients, one check, and the piece that is not a logarithm",
                    "minutes": 12,
                    "vars": ["A", "B", "C", "x"],
                    "brief": r"""
Decompose

$$\frac{1}{x(x-2)^{2}} = \frac{A}{x} + \frac{B}{x-2} + \frac{C}{(x-2)^{2}}$$

and then integrate it over $[3,4]$, which keeps clear of both poles.

The repeated factor needs a term at each power, so there are three unknowns for a
denominator of degree three. Two of them come from the cover-up rule and the third from
one coefficient comparison.
""",
                    "steps": [
                        {
                            "prompt": "Multiply both sides by $x$ and let $x \\to 0$, which annihilates the other two terms. Write $A$.",
                            "answer": "\\frac{1}{4}",
                            "placeholder": "?",
                            "hint": "What is left on the left-hand side is $\\frac{1}{(x-2)^{2}}$ evaluated at $x = 0$.",
                        },
                        {
                            "prompt": "Multiply both sides by $(x-2)^{2}$ and let $x \\to 2$. Write $C$.",
                            "answer": "\\frac{1}{2}",
                            "placeholder": "?",
                            "hint": "What is left is $\\frac{1}{x}$ at $x = 2$. The $B$ term keeps one factor of $(x-2)$ and dies.",
                        },
                        {
                            "prompt": "Clearing denominators gives $1 = A(x-2)^{2} + Bx(x-2) + Cx$. Only $A$ and $B$ contribute an $x^{2}$ term, and the left-hand side has none. Write $B$.",
                            "answer": "-\\frac{1}{4}",
                            "placeholder": "?",
                            "hint": "The $x^{2}$ coefficients give $A + B = 0$.",
                            "deconstruct": [
                                "$A(x-2)^2$ contributes $A x^2$ and $Bx(x-2)$ contributes $Bx^2$.",
                                "The left-hand side is the constant $1$, so the $x^2$ coefficient there is $0$.",
                            ],
                        },
                        {
                            "prompt": "Check the result at a value that was not used to build it. Evaluate $\\frac{A}{x} + \\frac{B}{x-2} + \\frac{C}{(x-2)^{2}}$ at $x = 1$ with the three numbers you have.",
                            "answer": "1",
                            "placeholder": "?",
                            "hint": "$\\frac{1/4}{1} + \\frac{-1/4}{-1} + \\frac{1/2}{1}$, and the original is $\\frac{1}{1 \\cdot 1} = 1$.",
                        },
                        {
                            "prompt": "Antidifferentiate the repeated-factor term $\\frac{C}{(x-2)^{2}}$ with $C = \\frac{1}{2}$. Write the result, without the constant.",
                            "answer": "-\\frac{1}{2(x-2)}",
                            "placeholder": "?",
                            "hint": "$(x-2)^{-2}$ antidifferentiates to $-(x-2)^{-1}$ by the power rule; there is no logarithm here.",
                        },
                        {
                            "prompt": "Assemble all three antiderivatives and evaluate between $3$ and $4$. Write the exact value, using `ln` for the natural logarithm.",
                            "answer": "\\frac{1}{4}ln(\\frac{2}{3})+\\frac{1}{4}",
                            "placeholder": "?",
                            "hint": "The two logarithms combine: $\\frac{1}{4}\\ln\\frac{x}{x-2}$ evaluated between $3$ and $4$ gives $\\frac{1}{4}\\ln\\frac{2}{3}$. The rational term contributes $-\\frac{1}{4} + \\frac{1}{2}$.",
                            "deconstruct": [
                                "$\\frac{1}{4}\\ln|x| - \\frac{1}{4}\\ln|x-2| = \\frac{1}{4}\\ln\\frac{x}{x-2}$ on $[3,4]$, where both are positive.",
                                "At $x = 4$ that is $\\frac{1}{4}\\ln 2$; at $x = 3$ it is $\\frac{1}{4}\\ln 3$.",
                                "The rational term is $-\\frac{1}{2(x-2)}$: $-\\frac{1}{4}$ at $x=4$ and $-\\frac{1}{2}$ at $x=3$.",
                            ],
                        },
                    ],
                    "closing": r"""
$\frac{1}{4}\ln\frac{2}{3} + \frac{1}{4} = 0.14863$. The integrand runs from
$\frac{1}{3}$ at $x = 3$ down to $\frac{1}{16}$ at $x = 4$, so any answer outside
$[0.0625, 0.333]$ would have been wrong on inspection, and $0.149$ sits where it should.

Two structural facts came out of the working rather than being quoted. The repeated
factor contributed a **rational** term and not a logarithm, because $(x-2)^{-2}$
antidifferentiates by the power rule — so the shape of the answer was decided when the
denominator was factored, before any integration happened. And step four is the check
that earns its keep: it uses a value of $x$ that appears in none of the three
derivations, so a sign error in any one of them fails it. Getting $A$, $B$ and $C$ is
routine; getting the sign of $B$ right is where the errors are.
"""
                },
            ],
            "quiz": {
                "title": "Splitting a quotient",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"What has to happen before $\frac{x^3}{x^2 - 1}$ can be decomposed into partial fractions?",
                        "opts": [
                            r"Nothing — it is already in a decomposable form",
                            r"A polynomial long division, because the numerator's degree is not below the denominator's",
                            r"Completing the square in the denominator",
                            r"Differentiating the numerator",
                        ],
                        "a": 1,
                        "why": (
                            r"Degree three over degree two is improper, and no sum of terms shaped like $A/(x - 1)$ can ever "
                            r"produce the leading $x$ that division pulls out. Dividing gives $x + \frac{x}{x^2 - 1}$, and only "
                            r"the remainder gets decomposed. Skipping the division produces a system of equations with no "
                            r"solution, which at least fails loudly rather than quietly."
                        ),
                    },
                    {
                        "q": r"In $\frac{5}{(x-1)(x+4)} = \frac{A}{x-1} + \frac{B}{x+4}$, what is the numerator $A$?",
                        "opts": [r"$1$", r"$5$", r"$-1$", r"$\frac{1}{5}$"],
                        "a": 0,
                        "why": (
                            r"Multiply both sides by $(x - 1)$ and set $x = 1$: the other term is annihilated by its own "
                            r"factor and what remains is $5/(1 + 4) = 1$. That is the cover-up method — hide the factor you "
                            r"are solving for and substitute its root into everything else. Expanding and matching "
                            r"coefficients reaches the same number through several more lines of algebra and several more "
                            r"chances to slip."
                        ),
                    },
                    {
                        "q": r"Which is the correct form for $\frac{1}{x(x-2)^2}$?",
                        "opts": [
                            r"$\frac{A}{x} + \frac{B}{(x-2)^2}$",
                            r"$\frac{A}{x} + \frac{B}{x-2} + \frac{C}{(x-2)^2}$",
                            r"$\frac{A}{x} + \frac{Bx + C}{(x-2)^2}$",
                            r"$\frac{A + B}{x(x-2)^2}$",
                        ],
                        "a": 1,
                        "why": (
                            r"A factor repeated twice needs a term at each power up to the repeat, so both $\frac{B}{x-2}$ and "
                            r"$\frac{C}{(x-2)^2}$ have to appear; leaving out the first-power term makes the system "
                            r"unsolvable in general. A linear numerator $Bx + C$ belongs over an irreducible quadratic, and "
                            r"$(x-2)^2$ is not irreducible — it is a linear factor squared."
                        ),
                    },
                    {
                        "q": r"$\int\frac{dx}{x^2 + 4}$ equals",
                        "opts": [
                            r"$\ln|x^2 + 4| + C$",
                            r"$\frac{1}{2}\arctan\frac{x}{2} + C$",
                            r"$\arctan(x^2 + 4) + C$",
                            r"$\frac{-1}{(x^2+4)^2} + C$",
                        ],
                        "a": 1,
                        "why": (
                            r"The standard form is $\int\frac{dx}{x^2 + a^2} = \frac{1}{a}\arctan\frac{x}{a} + C$, here with "
                            r"$a = 2$, so both the $\frac{1}{2}$ outside and the $\frac{x}{2}$ inside are needed. A logarithm "
                            r"appears only when the numerator is a multiple of $2x$, the derivative of the denominator, which "
                            r"it is not. A general $(Ax + B)$ numerator over an irreducible quadratic splits into one piece of "
                            r"each kind, one logarithm and one arctangent."
                        ),
                    },
                    {
                        "q": r"Which of these is genuinely a partial-fractions problem rather than a substitution?",
                        "opts": [
                            r"$\int\frac{2x}{x^2 + 1}\,dx$",
                            r"$\int\frac{dx}{(x-1)(x+3)}$",
                            r"$\int\frac{dx}{\sqrt{1 - x^2}}$",
                            r"$\int x\sqrt{x^2 + 1}\,dx$",
                        ],
                        "a": 1,
                        "why": (
                            r"A proper rational function whose denominator factors into distinct linear pieces is exactly what "
                            r"the method exists for. By contrast $\int\frac{2x}{x^2+1}\,dx$ carries the derivative of its own "
                            r"denominator on top and is a one-line logarithm; $\int\frac{dx}{\sqrt{1-x^2}}$ is the standard "
                            r"arcsine form; and $\int x\sqrt{x^2+1}\,dx$ yields to $u = x^2 + 1$. Reaching for partial "
                            r"fractions before checking for an $f'/f$ pattern is a good way to turn one line into a page."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M10
        {
            "title": "Applications of the definite integral",
            "summary": "Slice the quantity, approximate one slice by something you can already measure, and let the slice width go to zero.",
            "concepts": [
                r"Area between two curves is $\int(\text{upper} - \text{lower})\,dx$, split at every crossing, because a signed integral would cancel what you meant to add",
                r"Volumes of revolution: a disk or washer when the slice is perpendicular to the axis, a cylindrical shell $2\pi x f(x)\,dx$ when it runs parallel to it",
                r"Arc length $\int\sqrt{1 + f'(x)^2}\,dx$ and the surface of revolution $\int 2\pi f(x)\sqrt{1 + f'(x)^2}\,dx$ come from the same slice, measured two different ways",
                r"Average value $\bar f = \frac{1}{b-a}\int_a^b f$, attained somewhere by the mean value theorem for integrals; the root mean square $\sqrt{\frac{1}{T}\int_0^T f^2}$ is the average engineering quotes instead",
                r"Work is $\int F\,dx$ and stored energy is $\int v\,i\,dt$: whenever a product of two quantities is only valid for an instant, the total is an integral and not a multiplication",
                r"One template throughout — slice, approximate one slice, let the width go to zero — and the approximation is admissible only when its per-slice error carries one more power of $\Delta x$ than the slice contributes, so that the accumulated error still vanishes",
                r"That condition is not automatic. Slicing a cone into cylinders gets the volume right and the lateral area wrong by a factor of $\sqrt{2}$ — $29.3$ per cent short, at every panel count — because a cylinder's side misses the slant that arc length measures",
            ],
            "read": [
                {
                    "title": "One template, five formulas, and the slice that is not good enough",
                    "minutes": 13,
                    "body": r"""
This module looks like a list of formulas to memorise — area between curves, disks,
shells, arc length, work — and it is one procedure applied five times. The procedure has
three steps and the third one is the only place it can go wrong.

1. Cut the quantity into slices indexed by a variable, so the total is a sum of slice
   contributions.
2. Approximate one slice by something already measurable, keeping the error small
   compared with the slice.
3. Let the slice width go to zero, at which point the sum becomes an integral.

Step two is where the judgement lives, because a slice can be approximated in more than
one way and not every way survives step three. The rest of this reading is that
statement made precise, and then a case where the obvious approximation fails.

## Why a first-order approximation is enough — and what "enough" means

Suppose each slice of width $\Delta x$ is approximated with an error of order
$(\Delta x)^{2}$. There are about $\frac{b-a}{\Delta x}$ slices, so the total error is
about $\frac{b-a}{\Delta x}\cdot(\Delta x)^{2} = (b-a)\Delta x$, which goes to zero.
That is the licence to replace a curved slice by a straight one: the *per-slice* error
must be smaller than the slice width by at least one power, and then the accumulated
error still vanishes.

Now read the condition backwards. If the per-slice error is only of order $\Delta x$
itself, the total is of order $(b-a)$ — a fixed amount that never goes away, no matter
how fine the slicing. An approximation can be visibly, arbitrarily close to
the truth on each slice and still produce a wrong answer, and the next section is that
happening.

## Worked: the cone, where the obvious slice is wrong by 41 per cent

Rotate $y = x$ on $[0,1]$ about the $x$-axis. The result is a cone of radius $1$ and
height $1$.

Its **volume** comes out right with the obvious slice. A thin disc at $x$ has radius
$f(x)$ and thickness $\mathrm{d}x$:

$$V = \int_0^1 \pi f(x)^{2}\,\mathrm{d}x = \int_0^1 \pi x^{2}\,\mathrm{d}x =
\frac{\pi}{3}$$

which agrees with $\frac{1}{3}\pi r^{2}h$. Now its **lateral surface area**, by the same
slice: a thin cylinder at $x$ has circumference $2\pi f(x)$ and width $\mathrm{d}x$, so

$$A = \int_0^1 2\pi f(x)\,\mathrm{d}x = \int_0^1 2\pi x\,\mathrm{d}x
    = \pi = 3.1416 \qquad\text{(wrong)}$$

The true lateral area of a cone is $\pi r \ell$ with $\ell$ the slant height, here
$\sqrt{1^{2}+1^{2}} = \sqrt2$, giving $\pi\sqrt2 = 4.4429$. The cylinder slicing is
short by a factor of $\sqrt2$ — **29.3 per cent of the true area is missing** — and
refining the slicing does not help at all. Every finer version is short by the same
$\sqrt2$.

The reason is step two's error condition. A cylinder of width $\Delta x$ has slant
$\Delta x$; the actual surface element has slant $\sqrt{(\Delta x)^{2} + (\Delta y)^{2}}$.
The two differ by a *constant relative* amount whenever the surface is not horizontal, so
the per-slice error is of order $\Delta x$ and not $(\Delta x)^{2}$. It accumulates. The
correct element measures the slant:

$$A = \int_a^b 2\pi f(x)\sqrt{1 + f'(x)^{2}}\,\mathrm{d}x
    = \int_0^1 2\pi x\sqrt{2}\,\mathrm{d}x = \pi\sqrt2$$

For $f(x) = mx$ the factor is $\sqrt{1+m^{2}}$ — exactly $1$ when the surface is flat,
which is why nobody meets this failure on a cylinder, and why it is invisible until the
first cone.

Volume escapes because a disc and the true frustum differ in volume by order
$(\Delta x)^{2}$: the frustum's radius varies by $O(\Delta x)$ across the slice, and
volume depends on radius *squared* over a thickness, so the discrepancy carries the
extra power. Area depends on radius times slant, and the slant is where the missing
power went. Two integrals, the same slicing, and only one of them is entitled to it.

## Arc length, from the same triangle, taken to a number

The factor above is arc length in disguise. A short piece of curve is the hypotenuse of
a triangle with legs $\mathrm{d}x$ and $\mathrm{d}y$, so its length is
$\sqrt{\mathrm{d}x^{2} + \mathrm{d}y^{2}}$, and factoring $\mathrm{d}x$ out of the root
leaves

$$L = \int_a^b\sqrt{1 + f'(x)^{2}}\,\mathrm{d}x$$

The $1$ is the horizontal leg, squared. Worked on $y = x^{2}$ over $[0,1]$:

```
f'(x) = 2x

L = integral of sqrt(1 + 4x^2) dx from 0 to 1
  = (1/4)[ 2x sqrt(1+4x^2) + ln(2x + sqrt(1+4x^2)) ] from 0 to 1
  = (1/4)( 2 sqrt5 + ln(2 + sqrt5) )
  = 1.47894
```

Check it against the two lengths it must lie between: the straight chord from $(0,0)$ to
$(1,1)$ has length $\sqrt2 = 1.41421$, and the two-segment path through $(0.5, 0.25)$ has
length $0.5590 + 0.9014 = 1.46043$. The curve is longer than both and not by much, which
is right. Notice also that this integrand needed a trigonometric substitution from module
8 to produce a closed form at all; most arc-length integrands have none, which is where
module 2's adaptive quadrature stops being an exercise and becomes the only route.

## The averages, and why engineering quotes the second one

The mean value of $f$ over $[a,b]$ is $\bar f = \frac{1}{b-a}\int_a^b f$, and it is
attained. Apply the mean value theorem to $F(x) = \int_a^x f$, whose derivative is $f$ by
module 1: $F(b) - F(a) = F'(c)(b-a) = f(c)(b-a)$ for some $c$, so $f(c) = \bar f$. That
is the mean value theorem for integrals, and it is one line of the ordinary one applied
to the accumulation function.

For a sinusoid $\bar f = 0$, which says nothing about how much heating it does, because
power in a resistor goes as $v^{2}$ and not as $v$. The root mean square averages the
square first:

```
sinusoid   rms = V / sqrt2  = 0.7071 V      (module 8: mean of sin^2 is 1/2)
square     rms = V                          (the square of +-V is V^2 always)
triangle   rms = V / sqrt3  = 0.5774 V
```

Three waveforms with the same peak and the same zero mean, delivering three different
amounts of heat. The average that matters is decided by what the quantity is used for,
and that is a modelling choice rather than a mathematical one.

## The mistake, and why it is tempting

Integrating $\left(\text{upper} - \text{lower}\right)$ across a crossing without
splitting. Between $y = x$ and $y = x^{3}$ on $[-1,1]$ the curves cross at the origin and
swap places:

```
signed  integral of (x - x^3) dx from -1 to 1     = 0
area    2 * integral of (x - x^3) dx from 0 to 1  = 2(1/2 - 1/4) = 1/2
```

The signed integral is $0$ because the region left of the origin contributes exactly the
negative of the region right of it. It is tempting because the formula was applied
correctly and the answer is a number; the integral answered a different question,
which is the same failure mode module 6's unmoved limits produce. The habit that closes
it is to find the crossings before writing the integral, then integrate
$\left|\text{upper} - \text{lower}\right|$ piecewise.

The same slip in a different costume is choosing the wrong slice direction and then
fighting the algebra. Rotating the region under $y = f(x)$ about the $y$-axis with discs
requires inverting $f$; with shells it does not, because a shell at radius $x$ has volume
$2\pi x f(x)\,\mathrm{d}x$ and keeps the variable you already have a formula in. The two
give the same number, so the choice is about effort rather than correctness.

## Where this stops holding

The template needs each slice to be describable by a single quantity that varies
smoothly. Arc length needs $f'$ to exist and be integrable, and $y = |x|$ has a corner —
the integral must be split there, and $\sqrt{1+f'^{2}}$ has no value at the corner
itself. Surfaces of revolution need the curve not to cross the axis, or the "radius"
$f(x)$ goes negative and the area integral silently subtracts.

And the cone above is the small version of a genuine limit failure. Take a cylinder and
approximate it by a mesh of flat triangles chosen adversarially — the Schwarz lantern —
and the triangles can be made to converge pointwise to the cylinder while their total
area diverges to infinity. Slicing a length or an area is not a matter of getting close
to the shape; it is a matter of getting close *at the right order*, and that is the only
thing step two is ever asking.
"""
                },
            ],
            "derive": [
                {
                    "title": "One cone, two slicings, and the factor a cylinder leaves out",
                    "minutes": 11,
                    "vars": ["x", "m", "V", "A"],
                    "brief": r"""
Rotate $f(x) = x$ on $[0,1]$ about the $x$-axis: a cone of radius $1$ and height $1$.

The same slicing that gets the volume right gets the lateral area wrong, and this
derivation computes both so the discrepancy is a number rather than a warning. Take
$\pi$ as `\pi`.
""",
                    "steps": [
                        {
                            "prompt": "A disc at $x$ has radius $f(x) = x$ and thickness $\\mathrm{d}x$. Evaluate $\\int_0^1 \\pi x^{2}\\,\\mathrm{d}x$ and write the volume.",
                            "answer": "\\frac{\\pi}{3}",
                            "placeholder": "?",
                            "hint": "The antiderivative of $x^2$ is $\\frac{x^3}{3}$, and the limits are $0$ and $1$.",
                        },
                        {
                            "prompt": "With $f'(x) = 1$, write the arc-length factor $\\sqrt{1 + f'(x)^{2}}$.",
                            "answer": "\\sqrt{2}",
                            "placeholder": "?",
                            "hint": "It is a constant here, because the generating line has constant slope.",
                        },
                        {
                            "prompt": "The surface element is $2\\pi f(x)\\sqrt{1+f'(x)^{2}}\\,\\mathrm{d}x$. Evaluate $\\int_0^1 2\\pi x\\sqrt{2}\\,\\mathrm{d}x$ and write the lateral area.",
                            "answer": "\\pi\\sqrt{2}",
                            "placeholder": "?",
                            "hint": "$\\int_0^1 2x\\,\\mathrm{d}x = 1$, so the constants are all that survive.",
                        },
                        {
                            "prompt": "Now the same slicing with a plain cylinder of width $\\mathrm{d}x$, whose side area is $2\\pi f(x)\\,\\mathrm{d}x$. Evaluate $\\int_0^1 2\\pi x\\,\\mathrm{d}x$.",
                            "answer": "\\pi",
                            "placeholder": "?",
                            "hint": "The same integral as the previous step without the constant factor from step two.",
                        },
                        {
                            "prompt": "Divide the correct area by the cylinder answer. Write the factor the cylinder slicing loses.",
                            "answer": "\\sqrt{2}",
                            "placeholder": "?",
                            "hint": "It does not depend on the panel count, which is the point: refining the slicing never recovers it.",
                        },
                        {
                            "prompt": "Generalise. For $f(x) = mx$, write the factor by which the correct surface element exceeds the cylinder element.",
                            "answer": "\\sqrt{1+m^2}",
                            "placeholder": "?",
                            "hint": "It is the arc-length factor of step two with $f' = m$ in place of $1$.",
                        },
                    ],
                    "closing": r"""
The volume $\frac{\pi}{3} = 1.0472$ is right and agrees with $\frac{1}{3}\pi r^{2}h$.
The lateral area is $\pi\sqrt2 = 4.4429$, and the cylinder slicing returns $\pi = 3.1416$ — short by $29.3$ per cent, and short by the same $29.3$ per cent at every
panel count.

The discrepancy is a slice-error order, not an arithmetic slip. A disc differs from the
true frustum in volume by $O\left((\Delta x)^{2}\right)$, which vanishes when summed over
$\frac{1}{\Delta x}$ slices; a cylinder differs from it in *area* by $O(\Delta x)$, which
does not. Step six says where the boundary is: the factor is $\sqrt{1+m^{2}}$, equal to
$1$ exactly when $m = 0$. On a flat surface the cylinder slicing is correct, which is why
this failure is invisible until the first sloped one.

Whenever a slice is approximated, the question to ask is not whether the approximation
looks close. It is whether the error per slice carries one more power of $\Delta x$ than
the slice contributes.
"""
                },
            ],
            "quiz": {
                "title": "Setting up the integral",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"What is the area of the region between $y = x$ and $y = x^2$ for $0 \le x \le 1$?",
                        "opts": [r"$\frac{1}{6}$", r"$\frac{1}{2}$", r"$\frac{5}{6}$", r"$\frac{1}{3}$"],
                        "a": 0,
                        "why": (
                            r"On $[0, 1]$ the line lies above the parabola, so the area is "
                            r"$\int_0^1 (x - x^2)\,dx = \frac{1}{2} - \frac{1}{3} = \frac{1}{6}$. Integrating the two curves "
                            r"separately and adding gives $\frac{5}{6}$, which is the area under both rather than between "
                            r"them. Subtracting the other way round gives $-\frac{1}{6}$, and a negative area is the signal "
                            r"that the upper curve was misidentified."
                        ),
                    },
                    {
                        "q": r"Rotating the region under $y = f(x)$ from $x = a$ to $x = b$ about the $y$-axis, which integral is the shell method?",
                        "opts": [
                            r"$\int_a^b \pi f(x)^2\,dx$",
                            r"$\int_a^b 2\pi x\,f(x)\,dx$",
                            r"$\int_a^b 2\pi f(x)\,dx$",
                            r"$\int_a^b \pi x^2\,dx$",
                        ],
                        "a": 1,
                        "why": (
                            r"A shell at radius $x$ has circumference $2\pi x$, height $f(x)$ and thickness $dx$, so its "
                            r"volume is $2\pi x f(x)\,dx$. The form $\pi f(x)^2$ is the disk method, which is correct for "
                            r"rotation about the $x$-axis and answers a different question here. Choosing between them is "
                            r"choosing the direction of the slice, and shells usually win when they let you keep the variable "
                            r"you already have a formula in."
                        ),
                    },
                    {
                        "q": r"In the arc length formula $\int_a^b\sqrt{1 + f'(x)^2}\,dx$, where does the $1$ come from?",
                        "opts": [
                            r"A constant of integration",
                            r"The horizontal leg $dx$ of the small right triangle whose hypotenuse is the arc",
                            r"The requirement that a length be positive",
                            r"The average value of $f$ over the interval",
                        ],
                        "a": 1,
                        "why": (
                            r"A short piece of curve is the hypotenuse of a triangle with legs $dx$ and $dy$, so its length is "
                            r"$\sqrt{dx^2 + dy^2}$, and factoring $dx$ out leaves $\sqrt{1 + (dy/dx)^2}\,dx$. The $1$ is the "
                            r"horizontal leg, squared. Seeing that also explains why arc-length integrands are so often ugly: "
                            r"a square root of a polynomial rarely has an elementary antiderivative, which is exactly when the "
                            r"adaptive quadrature of module 2 gets used in earnest."
                        ),
                    },
                    {
                        "q": r"A voltage $v(t) = V\sin(\omega t)$ averages to zero over a full cycle. Why is its RMS value not zero as well?",
                        "opts": [
                            r"Because the RMS is taken over half a cycle only",
                            r"Because squaring first makes every contribution non-negative, so nothing cancels",
                            r"Because the RMS uses the absolute value of the integral",
                            r"Because the average is only zero for an ideal source",
                        ],
                        "a": 1,
                        "why": (
                            r"RMS squares before it averages, and a square is never negative, so the negative half-cycle "
                            r"contributes just as much as the positive one; the square root at the end returns the result to "
                            r"the original units. That is precisely the quantity that sets the heating in a resistor, because "
                            r"power goes as $v^2$ and not as $v$. Nothing about it involves halving the interval, and the mean "
                            r"of the raw sinusoid really is zero — which is why the plain mean is the wrong average for this "
                            r"job."
                        ),
                    },
                    {
                        "q": r"A spring obeying $F(x) = kx$ is stretched from $0$ to $L$. How much work is done?",
                        "opts": [r"$kL$", r"$\frac{1}{2}kL^2$", r"$kL^2$", r"$\frac{1}{2}kL$"],
                        "a": 1,
                        "why": (
                            r"Force times distance only holds while the force is constant, so the total is "
                            r"$\int_0^L kx\,dx = \frac{1}{2}kL^2$. Multiplying the final force $kL$ by the distance $L$ gives "
                            r"$kL^2$, twice the truth, because it charges the whole journey at the highest force. The same "
                            r"argument in a different costume produces $\frac{1}{2}CV^2$ for a charged capacitor and "
                            r"$\frac{1}{2}LI^2$ for an inductor."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M11
        {
            "title": "Power series as functions",
            "summary": "Once a function is a series it can be substituted into, differentiated and integrated like a polynomial — which is how the awkward integrals get done.",
            "concepts": [
                r"The geometric series $\frac{1}{1-x} = \sum_{n \ge 0} x^n$ for $|x| < 1$ is the one series that costs no differentiation at all, and most others are built from it",
                r"Substituting into and multiplying known series beats computing $n$ derivatives: $\frac{1}{1+x^2}$ is the geometric series evaluated at $-x^2$, in one line",
                r"Inside the radius of convergence a power series may be differentiated and integrated term by term, and the radius survives the operation — which turns geometric series into $\ln(1+x)$ and $\arctan x$",
                r"The binomial series extends $(1+x)^k$ to every real exponent $k$, and terminates into the ordinary binomial theorem exactly when $k$ is a non-negative integer",
                r"An integrand with no elementary antiderivative — $e^{-x^2}$, or $\frac{\sin x}{x}$ — is integrated by expanding it and integrating term by term, with the truncation sized by module 3's remainder bound",
                r"Term-by-term integration is licensed *strictly inside* the radius, so the classical $\frac{\pi}{4} = 1 - \frac{1}{3} + \frac{1}{5} - \cdots$ does not follow from evaluating the integrated series at $x = 1$. It follows from integrating the finite identity with its exact remainder and bounding that by $\frac{1}{2n+3}$ — which also prices it: $500$ terms for three digits",
                r"Convergent is not the same as convergent to the right function. $e^{-1/x^2}$ is infinitely differentiable with every derivative zero at the origin, so its Maclaurin series converges everywhere and agrees with the function at exactly one point",
                r"A radius of convergence can have no explanation on the real line at all: $\frac{1}{1+x^2}$ is smooth and bounded everywhere real and its radius is $1$, because the nearest singularities are the poles at $\pm i$",
            ],
            "read": [
                {
                    "title": "Term-by-term integration, with the remainder carried instead of assumed",
                    "minutes": 13,
                    "body": r"""
A power series inside its radius of convergence behaves like a polynomial: it can be
substituted into, differentiated and integrated term by term. That is the licence this
module runs on, and it turns the integrals module 5 declared elementary-antiderivative-free
into arithmetic. It also has an edge, and this course has already stepped over that edge
once without saying so.

## The geometric series, from an algebraic identity

Multiply out $(1-x)\left(1 + x + x^{2} + \cdots + x^{n}\right)$ and everything cancels
except the ends:

$$(1-x)\sum_{k=0}^{n}x^{k} = 1 - x^{n+1}
\qquad\text{so}\qquad
\sum_{k=0}^{n}x^{k} = \frac{1 - x^{n+1}}{1-x}$$

That is an identity, true for every $x \neq 1$ and every $n$, with no limit anywhere in
it. The infinite series is what happens when $x^{n+1}\to0$, which is exactly the
condition $|x| < 1$; outside it the terms do not even tend to zero and module 4's
$n$th-term test rules out convergence before anything subtler is required.

Everything else in this module is built from that one series by substitution.
$\frac{1}{1+x^{2}}$ is the geometric series evaluated at $-x^{2}$:

$$\frac{1}{1-(-x^{2})} = 1 - x^{2} + x^{4} - x^{6} + \cdots$$

in one line, with no derivatives computed. The alternative — Taylor's formula from
module 3, differentiating $\frac{1}{1+x^{2}}$ repeatedly at the origin — is correct and
costs an afternoon.

## The endpoint this course has already used

Integrating that series term by term from $0$ to $x$ gives

$$\arctan x = x - \frac{x^{3}}{3} + \frac{x^{5}}{5} - \cdots$$

and putting $x = 1$ produces the celebrated $\frac{\pi}{4} = 1 - \frac{1}{3} + \frac{1}{5} - \cdots$. Except that term-by-term integration was licensed *strictly inside* the radius,
and $x = 1$ is on the boundary. At $t = 1$ the series being integrated does not converge
at all: $1 - 1 + 1 - 1 + \cdots$ has no sum. So the standard derivation applies a theorem
outside its stated hypothesis and gets the right answer, which is worse than getting the
wrong one.

There is a route that needs no theorem about endpoints. Rearrange the finite identity
above with $x$ replaced by $-t^{2}$, and keep the remainder rather than discarding it:

$$\frac{1}{1+t^{2}} = \sum_{k=0}^{n}(-1)^{k}t^{2k}
  + \frac{(-1)^{n+1}t^{2n+2}}{1+t^{2}}$$

This is exact algebra — check it by multiplying through by $1+t^{2}$ — and it holds at
every real $t$, endpoint included, because it is a finite sum. Integrate all of it from
$0$ to $1$. The finite sum integrates term by term with no theorem required, giving
$\sum_{k=0}^{n}\frac{(-1)^{k}}{2k+1}$, and the remainder is a single honest integral:

$$\left|R_n\right| = \int_0^1\frac{t^{2n+2}}{1+t^{2}}\,\mathrm{d}t
 \le \int_0^1 t^{2n+2}\,\mathrm{d}t = \frac{1}{2n+3}$$

dropping the denominator because $1+t^{2}\ge1$. That bound goes to zero, so the series
converges to $\frac{\pi}{4}$, and — unlike the appeal to an endpoint theorem — it says
how fast.

## Worked: how fast, and what that costs

Take $n = 2$. The partial sum is $1 - \frac{1}{3} + \frac{1}{5} = \frac{13}{15} = 0.86667$, the
guaranteed bound is $\frac{1}{7} = 0.14286$, and the true error is
$\left|\frac{\pi}{4} - \frac{13}{15}\right| = 0.08127$. The bound holds and is within a
factor of two of the truth, which is about what a bound obtained by throwing away a
denominator deserves.

Now ask for three decimal places: $\frac{1}{2n+3}\le10^{-3}$ needs $2n+3\ge1000$, so
$n = 499$ — **five hundred terms for three digits**. That is the arithmetic behind the
remark that a series can be correct and useless at the same time. Module 2's adaptive
Simpson reaches $\int_0^1\frac{4\,\mathrm{d}x}{1+x^{2}} = \pi$ to nine digits from a
handful of panels, on the identical integrand. Convergence proved is not convergence
achieved, and the two halves of this course measure different things.

## Worked: an integral with no elementary antiderivative

$$\int_0^1 e^{-x^{2}}\,\mathrm{d}x$$

Module 5 recorded that this has no elementary antiderivative, by a theorem rather than
for want of trying. Substitute $-x^{2}$ into the exponential series and integrate:

```
e^(-x^2) = sum over n of (-1)^n x^(2n) / n!

integral from 0 to 1 = sum over n of (-1)^n / (n! (2n+1))

  n=0   +1.000000000
  n=1   -0.333333333
  n=2   +0.100000000
  n=3   -0.023809524
  n=4   +0.004629630
  n=5   -0.000757576
  n=6   +0.000106838
        -------------
         0.746836034      next term is 1/(7! * 15) = 1.3228e-5
```

The series alternates with terms decreasing in size, so the truncation error is smaller
than the first term omitted — module 4's alternating series bound. The true value is
$0.746824133$, so the actual error is $1.19\times10^{-5}$, under the promised
$1.32\times10^{-5}$. The answer arrives with an error bar, exactly as module 2's
quadrature does, reached from the other side.

## The binomial series, and where it terminates

For any real $k$,

$$(1+x)^{k} = 1 + kx + \frac{k(k-1)}{2!}x^{2} + \frac{k(k-1)(k-2)}{3!}x^{3} + \cdots$$

with radius $1$. When $k$ is a non-negative integer the factor $(k-n)$ eventually hits
zero and every later coefficient vanishes, so the series *is* the ordinary binomial
theorem and the radius question does not arise. For any other $k$ it never terminates.
Worked at $k = \frac{1}{2}$ and $x = 0.2$:

```
sqrt(1.2) ~ 1 + 0.1 - 0.005 + 0.0005 = 1.09550
true                                 = 1.09545
error                                = 5.5e-5
```

## Differentiating term by term, and a sum with no obvious value

The licence runs both ways, and differentiation is the direction that produces series
nobody would guess. Start again from the geometric series and differentiate both sides:

$$\frac{1}{1-x} = \sum_{n\ge0}x^{n}
\qquad\Rightarrow\qquad
\frac{1}{(1-x)^{2}} = \sum_{n\ge1}n\,x^{n-1}$$

The right-hand side is a series whose sum is not apparent from looking at it, and it has
now been evaluated in closed form without summing anything. Check it at $x = \frac{1}{2}$:

```
sum of n (1/2)^(n-1) for n = 1, 2, 3, ...

   1(1) + 2(0.5) + 3(0.25) + 4(0.125) + 5(0.0625) + ...
 = 1 + 1 + 0.75 + 0.5 + 0.3125 + 0.1875 + 0.109375 + ...

closed form   1/(1 - 1/2)^2  =  1/0.25  =  4
```

The partial sums above reach $3.86$ after seven terms and continue to $4$. At $x = \frac{1}{3}$ the same formula gives $\frac{1}{(2/3)^{2}} = \frac{9}{4} = 2.25$.

The radius survived the operation, as the module's bullet claims: both series converge
for $|x| < 1$ and neither at $x = 1$, where $\sum n$ diverges as loudly as $\sum 1$ does.
That invariance is the useful half of the theorem. It means a series may be
differentiated, integrated, differentiated again and substituted into, in any order,
without recomputing where it is valid — which is what makes a power series behave like a
polynomial rather than merely resemble one.

## The mistake, and why it is tempting

Expecting the radius of convergence to be set by where the function misbehaves on the
real line. $\frac{1}{1+x^{2}}$ is smooth and bounded on the whole of the real numbers,
with no singularity anywhere in sight, and its series has radius exactly $1$ — it
diverges at $x = 1.1$ for no reason visible on the real axis at all. The explanation is
not on the real axis: the function has poles at $x = \pm i$, at distance $1$ from the
origin, and a power series converges in a disc reaching the nearest singularity in the
*complex* plane. The temptation is to look for a real-line reason and conclude there is
none, and the honest position at this level is that the radius has an explanation and it
belongs to a later course.

## Where this stops holding

A function can be infinitely differentiable and still not equal its own Taylor series.
Take $f(x) = e^{-1/x^{2}}$ for $x \neq 0$ and $f(0) = 0$. Every derivative at the origin
is zero — the exponential decays faster than any power grows, so each derivative is a
rational function times $e^{-1/x^{2}}$ and each tends to $0$. The Maclaurin series is
therefore identically $0$, converges everywhere, and equals the function at exactly one
point.

So the chain module 3 built — compute coefficients, bound the remainder — has a link that
must be checked rather than assumed: the remainder has to go to zero, and *converging* is
not the same as *converging to the right function*. For $e^{x}$, $\sin$ and $\cos$ the
Lagrange remainder does go to zero for every $x$, because a factorial eventually beats
any fixed power, and module 3 proves it. It is proved there rather than assumed because
of the example above.
"""
                },
            ],
            "derive": [
                {
                    "title": "The arctangent series at the endpoint, with its remainder carried",
                    "minutes": 13,
                    "vars": ["n", "k", "t", "R"],
                    "brief": r"""
The usual derivation of $\frac{\pi}{4} = 1 - \frac{1}{3} + \frac{1}{5} - \cdots$
integrates a power series term by term and then evaluates at $x = 1$ — which is the one
place the licence to do that does not extend to, since the series being integrated
diverges there.

This derivation avoids the problem instead of stepping around it. Start from the **finite**
identity

$$\frac{1}{1+t^{2}} = \sum_{k=0}^{n}(-1)^{k}t^{2k} + R_n(t)$$

which is exact algebra, valid at every real $t$, and integrate all of it — remainder
included.
""",
                    "steps": [
                        {
                            "prompt": "Multiplying the finite geometric identity by $1+t^{2}$ and rearranging gives the exact remainder. Write $R_n(t)$.",
                            "answer": "\\frac{(-1)^{n+1}t^{2n+2}}{1+t^2}",
                            "placeholder": "?",
                            "hint": "The finite sum $\\sum_{k=0}^{n}(-1)^k t^{2k}$ is the geometric sum with ratio $-t^2$, so it equals $\\frac{1-(-t^{2})^{n+1}}{1+t^{2}}$.",
                            "deconstruct": [
                                "$\\sum_{k=0}^{n}(-1)^k t^{2k} = \\frac{1 - (-t^2)^{n+1}}{1 - (-t^2)}$.",
                                "Subtract that from $\\frac{1}{1+t^{2}}$; the two denominators are the same.",
                                "$-(-t^{2})^{n+1} = (-1)^{n}t^{2n+2}$ with a further sign from the subtraction.",
                            ],
                        },
                        {
                            "prompt": "Integrate the $k$-th term of the finite sum, $(-1)^{k}t^{2k}$, from $0$ to $1$. Write the result in terms of $k$.",
                            "answer": "\\frac{(-1)^k}{2k+1}",
                            "placeholder": "?",
                            "hint": "The power rule: $t^{2k}$ antidifferentiates to $\\frac{t^{2k+1}}{2k+1}$, evaluated at $1$ and $0$.",
                        },
                        {
                            "prompt": "Bound the size of the remainder's integrand by dropping the denominator, using $1 + t^{2} \\ge 1$. Write the bounding expression in $t$ and $n$.",
                            "answer": "t^{2n+2}",
                            "placeholder": "?",
                            "hint": "The numerator has magnitude $t^{2n+2}$, and dividing by something at least $1$ can only make it smaller.",
                        },
                        {
                            "prompt": "Integrate that bound from $0$ to $1$. Write the bound on $\\left|R_n\\right|$ after integration.",
                            "answer": "\\frac{1}{2n+3}",
                            "placeholder": "?",
                            "hint": "$\\int_0^1 t^{p}\\,\\mathrm{d}t = \\frac{1}{p+1}$, with $p = 2n+2$.",
                        },
                        {
                            "prompt": "Take $n = 2$ and write the partial sum $\\sum_{k=0}^{2}\\frac{(-1)^{k}}{2k+1}$ as a single fraction.",
                            "answer": "\\frac{13}{15}",
                            "placeholder": "?",
                            "hint": "$1 - \\frac{1}{3} + \\frac{1}{5}$, over a common denominator of $15$.",
                        },
                        {
                            "prompt": "Now demand three decimal places: find the smallest integer $n$ with $\\frac{1}{2n+3} \\le 10^{-3}$.",
                            "answer": "499",
                            "placeholder": "?",
                            "hint": "The condition is $2n + 3 \\ge 1000$.",
                            "deconstruct": [
                                "$2n + 3 \\ge 1000$ gives $n \\ge 498.5$.",
                                "$n$ counts terms and must be an integer, so round up.",
                            ],
                        },
                    ],
                    "closing": r"""
Nothing above needed a theorem about the endpoint. The identity in the brief is finite
and exact at every real $t$, the finite sum integrates term by term because it is a
polynomial, and the remainder was integrated rather than discarded. The bound
$\frac{1}{2n+3}$ tends to zero, so the series really does converge to $\frac{\pi}{4}$ —
established, not asserted.

Check step five against the truth. The partial sum is $\frac{13}{15} = 0.86667$, the
guaranteed bound is $\frac{1}{7} = 0.14286$, and $\left|\frac{\pi}{4} - \frac{13}{15}\right| = 0.08127$. The bound holds, and is loose by less than a factor of two — about what
dropping a denominator should cost.

Step six is the sting. Five hundred terms for three digits, on an integrand that module
2's adaptive Simpson takes to nine digits from a handful of panels. A series can be
correct, provably convergent, equipped with a rigorous error bound, and still the wrong
way to compute the number.
"""
                },
            ],
            "quiz": {
                "title": "Building series from series",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"For which $x$ does $\sum_{n=0}^{\infty} x^n$ converge, and to what?",
                        "opts": [
                            r"All $x$, to $\frac{1}{1-x}$",
                            r"$|x| < 1$, to $\frac{1}{1-x}$",
                            r"$|x| < 1$, to $\frac{1}{1+x}$",
                            r"$x > 0$, to $\frac{x}{1-x}$",
                        ],
                        "a": 1,
                        "why": (
                            r"The partial sum is $\frac{1 - x^{n+1}}{1 - x}$, and $x^{n+1} \to 0$ exactly when $|x| < 1$. "
                            r"Outside that the terms do not even tend to zero, so the $n$th-term test from module 4 rules "
                            r"convergence out before anything subtler is needed. Checking $x = \frac{1}{2}$, where the series "
                            r"sums to $2$, settles the sign in the denominator."
                        ),
                    },
                    {
                        "q": r"Using the geometric series, the expansion of $\frac{1}{1 + x^2}$ begins",
                        "opts": [
                            r"$1 + x^2 + x^4 + \cdots$",
                            r"$1 - x^2 + x^4 - \cdots$",
                            r"$1 - x + x^2 - \cdots$",
                            r"$x - \frac{x^3}{3} + \frac{x^5}{5} - \cdots$",
                        ],
                        "a": 1,
                        "why": (
                            r"Put $-x^2$ where the geometric series has its variable: "
                            r"$\frac{1}{1 - (-x^2)} = 1 + (-x^2) + (-x^2)^2 + \cdots = 1 - x^2 + x^4 - \cdots$. No derivatives "
                            r"are computed at any point. The all-plus version expands $\frac{1}{1 - x^2}$ instead, the "
                            r"alternating series in odd powers of $x$ is $\arctan x$, which is what you get after integrating "
                            r"this one term by term, and $1 - x + x^2 - \cdots$ expands $\frac{1}{1+x}$."
                        ),
                    },
                    {
                        "q": r"Integrating $1 - t^2 + t^4 - \cdots$ term by term from $0$ to $x$ gives",
                        "opts": [r"$\ln(1 + x)$", r"$\arctan x$", r"$e^{-x^2}$", r"$\frac{1}{1 + x^2}$"],
                        "a": 1,
                        "why": (
                            r"Term by term the integral is $x - \frac{x^3}{3} + \frac{x^5}{5} - \cdots$, and since the "
                            r"integrand sums to $\frac{1}{1 + t^2}$, the result is $\arctan x$. Putting $x = 1$ turns that into "
                            r"the classical $\pi/4$ series — though not by the theorem just used, since term-by-term "
                            r"integration is licensed strictly inside the radius and $x = 1$ is the boundary, where the "
                            r"integrand's series does not converge at all. The endpoint is reached instead by integrating the "
                            r"finite identity with its remainder, which also shows the series converges so slowly that it is a "
                            r"good reminder that a series being correct and a series being useful are separate claims. "
                            r"The logarithm comes from "
                            r"integrating the geometric series in $-t$ rather than in $-t^2$."
                        ),
                    },
                    {
                        "q": r"When is term-by-term differentiation and integration of a power series valid?",
                        "opts": [
                            r"Always",
                            r"Only for series with finitely many terms",
                            r"Strictly inside the radius of convergence, where the radius is unchanged by the operation",
                            r"Only when every coefficient is positive",
                        ],
                        "a": 2,
                        "why": (
                            r"Inside the radius the convergence is good enough — uniform on any closed subinterval — that both "
                            r"operations pass through the sum, and the differentiated and integrated series have the same "
                            r"radius as the original. The endpoints are the exception and must be checked separately, since "
                            r"convergence there can be gained or lost. Outside the radius there is nothing to differentiate, "
                            r"because the series represents no function at all."
                        ),
                    },
                    {
                        "q": r"$\int_0^1 e^{-x^2}\,dx$ has no elementary antiderivative. What is the series route to a value?",
                        "opts": [
                            r"Give up on calculus and read the answer from a table",
                            r"Substitute $-x^2$ into the exponential series, integrate term by term, and truncate with a remainder bound",
                            r"Differentiate under the integral sign",
                            r"Split the integrand into partial fractions",
                        ],
                        "a": 1,
                        "why": (
                            r"$e^{-x^2} = \sum\frac{(-x^2)^n}{n!}$ integrates term by term to "
                            r"$\sum\frac{(-1)^n}{n!\,(2n+1)}$, an alternating series whose truncation error is bounded by the "
                            r"first term left out. So the answer arrives with an error bar, exactly as the quadrature of "
                            r"module 2 does, but reached from the other side. Partial fractions needs a rational integrand and "
                            r"there is nothing rational here."
                        ),
                    },
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — quadrature and series library with error guarantees",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Fold the four labs into one library. `quadlib.py` holds every routine and is
what the checks import; `main.py` is a demo that integrates a handful of
awkward integrals, sums a series and prints an error report.

Every numerical routine returns the same record, so callers never have to guess
what a bare float means.

## `Result`

A dataclass with three fields, in this order:

- `value` — the number
- `error` — the routine's own estimate of how wrong it might be
- `evaluations` — how many times the integrand or term was called

## Integration

- `simpson(f, a, b, n)` — composite Simpson on `n` even panels; `ValueError`
  for odd `n` or `n < 2`. Returns a plain float, not a `Result`.
- `adaptive(f, a, b, tol, max_depth=30)` — the recursive Simpson of lab 2,
  returning a `Result`. `error` is the sum of `abs(delta) / 15` over the
  accepted panels; `evaluations` counts every call made to `f`. An empty
  interval gives `Result(0.0, 0.0, 0)`; a reversed one negates `value` only.
- `integrate(f, a, b, tol=1e-9)` — the front door. `a` or `b` may be
  `math.inf` / `-math.inf`, handled by the substitutions from lab 2 (split the
  doubly infinite case at 0 and give each half `tol / 2`). `tol <= 0` and any
  NaN bound raise `ValueError`.

## Series

- `taylor_coefficients(kind, n)`, `taylor_eval(coeffs, x)`,
  `taylor_bound(kind, x, n)` — exactly as in lab 3.
- `series_sum(term, tail_integral, tol, max_terms=200000)` — lab 4's
  `estimate_sum`, returning a `Result` whose `evaluations` is the number of
  terms used.

## Reporting

`error_report(entries)` takes a list of `(name, result, exact_or_None)` and
returns a string of exactly `len(entries) + 2` lines:

1. a header line beginning with `quantity`
2. one line per entry, starting with `name`, containing the value, the claimed
   bound and — when `exact` is given — the actual error
3. a final line starting with `TOTAL EVALUATIONS` and ending with the summed
   evaluation count

## Suggested order

`Result` and `simpson`, then `adaptive` with its counter, then `integrate`'s
dispatch on infinite bounds, then the series half, and `error_report` last.
''',
        "deliverables": [
            "`quadlib.py` — the whole library, importable with no output and no side effects",
            "`main.py` — a demo integrating a proper, an infinite and an oscillatory integral, then summing a series",
            "A `Result` record carrying value, error estimate and evaluation count from every routine",
            "`integrate` dispatching correctly on finite, semi-infinite and doubly infinite domains",
            "`series_sum` returning an integral-test bracket that provably contains the true sum",
            "`error_report` producing a table a marker can read without running anything",
        ],
        "constraints": [
            "Standard library only; `math` and `dataclasses` are all you need",
            "`quadlib.py` must define names only — importing it must print nothing",
            "No global mutable state: two concurrent integrations must not share an evaluation counter",
            "Every public routine validates its arguments and raises `ValueError` rather than returning nonsense",
            "The whole demo must finish in well under a second",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the infinite-domain, reversed-interval and empty-interval cases."},
            {"criterion": "Error control", "weight": 25,
             "evidence": "Reported error estimates actually bound the observed error on the tested integrals, and tightening tol tightens the answer."},
            {"criterion": "Argument validation", "weight": 15,
             "evidence": "Non-positive tolerances, odd Simpson panel counts and NaN bounds all raise ValueError."},
            {"criterion": "Design", "weight": 12,
             "evidence": "integrate dispatches onto shared helpers rather than duplicating the refinement loop, and the counter is per-call."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public routine, no dead code, no debug prints left in quadlib.py."},
        ],
        "hints": [
            "Wrap the integrand in a small closure that increments a list-of-one counter; returning `(wrapped, box)` from a helper keeps the state local to one call.",
            "Have `_refine` return the pair `(value, error)` and add the two halves' errors on the way back up — that is the whole error budget.",
            "`integrate` is a dispatch table, not an algorithm: empty interval, reversed interval, both infinite, upper infinite, lower infinite, otherwise `adaptive`. Reflect the lower-infinite case with `lambda x: f(-x)` and negated bounds.",
            "Merge sub-results with one helper that sums values, sums errors and sums evaluation counts, so every branch of `integrate` returns the same shape.",
        ],
        "files": [
            {"name": "quadlib.py", "content": r'''
import math
from dataclasses import dataclass

CLAMP = 1e-12
KINDS = ("exp", "sin", "cos")


@dataclass
class Result:
    value: float
    error: float
    evaluations: int


def simpson(f, a, b, n):
    """Composite Simpson rule on n even panels. Returns a float."""
    # your code here


def adaptive(f, a, b, tol, max_depth=30):
    """Adaptive Simpson to an absolute tolerance. Returns a Result."""
    # your code here


def integrate(f, a, b, tol=1e-9):
    """Integral of f over [a, b], where either bound may be infinite."""
    # your code here


def taylor_coefficients(kind, n):
    """Maclaurin coefficients c_0 .. c_n for exp, sin or cos."""
    # your code here


def taylor_eval(coeffs, x):
    """Horner evaluation of a coefficient list at x."""
    # your code here


def taylor_bound(kind, x, n):
    """Lagrange remainder bound for the degree-n Maclaurin polynomial."""
    # your code here


def series_sum(term, tail_integral, tol, max_terms=200000):
    """Sum a positive decreasing series to a tolerance. Returns a Result."""
    # your code here


def error_report(entries):
    """Table of (name, result, exact_or_None) rows plus a totals line."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
import math
from quadlib import integrate, series_sum, error_report

rows = [
    ("exp on [0,1]", integrate(math.exp, 0.0, 1.0, 1e-10), math.e - 1.0),
    ("exp(-x) to inf", integrate(lambda x: math.exp(-x), 0.0, math.inf, 1e-10), 1.0),
    ("gaussian", integrate(lambda x: math.exp(-x * x), -math.inf, math.inf, 1e-10), math.sqrt(math.pi)),
    ("basel series", series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-8), math.pi ** 2 / 6.0),
]

print(error_report(rows))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "quadlib.py", "content": r'''
import math
from dataclasses import dataclass

CLAMP = 1e-12
KINDS = ("exp", "sin", "cos")


@dataclass
class Result:
    value: float
    error: float
    evaluations: int


def _counted(f):
    """Wrap f so every call is tallied in a private one-element box."""
    box = [0]

    def wrapped(x):
        box[0] += 1
        return f(x)

    return wrapped, box


def _merge(parts):
    """Add up a list of Results field by field."""
    return Result(sum(p.value for p in parts),
                  sum(p.error for p in parts),
                  sum(p.evaluations for p in parts))


def simpson(f, a, b, n):
    """Composite Simpson rule on n even panels. Returns a float."""
    if n < 2 or n % 2 != 0:
        raise ValueError("n must be an even integer of at least 2")
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 == 1 else 2) * f(a + i * h)
    return h * total / 3.0


def _panel(f, a, b):
    """One Simpson panel over [a, b]."""
    c = 0.5 * (a + b)
    return (b - a) / 6.0 * (f(a) + 4.0 * f(c) + f(b))


def _refine(f, a, b, tol, whole, depth):
    """Return (value, error estimate) for the refined panel."""
    c = 0.5 * (a + b)
    left = _panel(f, a, c)
    right = _panel(f, c, b)
    delta = left + right - whole
    if depth <= 0 or abs(delta) <= 15.0 * tol:
        return (left + right + delta / 15.0, abs(delta) / 15.0)
    lv, le = _refine(f, a, c, tol / 2.0, left, depth - 1)
    rv, re = _refine(f, c, b, tol / 2.0, right, depth - 1)
    return (lv + rv, le + re)


def adaptive(f, a, b, tol, max_depth=30):
    """Adaptive Simpson to an absolute tolerance. Returns a Result."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    if a == b:
        return Result(0.0, 0.0, 0)
    sign = 1.0
    if b < a:
        a, b, sign = b, a, -1.0
    counted, box = _counted(f)
    value, error = _refine(counted, a, b, tol, _panel(counted, a, b), max_depth)
    return Result(sign * value, error, box[0])


def _tail(f, a, tol):
    """Integral of f from a to +infinity, via x = a + t/(1-t)."""
    def g(t):
        u = 1.0 - t
        if u < CLAMP:
            u = CLAMP
        return f(a + (1.0 - u) / u) / (u * u)
    return adaptive(g, 0.0, 1.0, tol)


def integrate(f, a, b, tol=1e-9):
    """Integral of f over [a, b], where either bound may be infinite."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    if math.isnan(a) or math.isnan(b):
        raise ValueError("bounds must not be nan")
    if a == b:
        return Result(0.0, 0.0, 0)
    if b < a:
        flipped = integrate(f, b, a, tol)
        return Result(-flipped.value, flipped.error, flipped.evaluations)
    if a == -math.inf and b == math.inf:
        return _merge([_tail(f, 0.0, tol / 2.0),
                       _tail(lambda x: f(-x), 0.0, tol / 2.0)])
    if b == math.inf:
        return _tail(f, a, tol)
    if a == -math.inf:
        return _tail(lambda x: f(-x), -b, tol)
    return adaptive(f, a, b, tol)


def taylor_coefficients(kind, n):
    """Maclaurin coefficients c_0 .. c_n for exp, sin or cos."""
    if kind not in KINDS:
        raise ValueError("kind must be one of exp, sin, cos")
    if n < 0:
        raise ValueError("n must not be negative")
    coeffs = []
    for k in range(n + 1):
        if kind == "exp":
            coeffs.append(1.0 / math.factorial(k))
        elif kind == "sin":
            if k % 2 == 0:
                coeffs.append(0.0)
            else:
                coeffs.append((-1.0) ** ((k - 1) // 2) / math.factorial(k))
        else:
            if k % 2 == 1:
                coeffs.append(0.0)
            else:
                coeffs.append((-1.0) ** (k // 2) / math.factorial(k))
    return coeffs


def taylor_eval(coeffs, x):
    """Horner evaluation of a coefficient list at x."""
    if not coeffs:
        raise ValueError("need at least one coefficient")
    total = 0.0
    for c in reversed(coeffs):
        total = total * x + c
    return total


def taylor_bound(kind, x, n):
    """Lagrange remainder bound for the degree-n Maclaurin polynomial."""
    if kind not in KINDS:
        raise ValueError("kind must be one of exp, sin, cos")
    if n < 0:
        raise ValueError("n must not be negative")
    m = math.exp(abs(x)) if kind == "exp" else 1.0
    return m * abs(x) ** (n + 1) / math.factorial(n + 1)


def series_sum(term, tail_integral, tol, max_terms=200000):
    """Sum a positive decreasing series to a tolerance. Returns a Result."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    total = 0.0
    for n in range(1, max_terms + 1):
        total += term(n)
        upper = tail_integral(n)
        lower = tail_integral(n + 1)
        half = 0.5 * (upper - lower)
        if half <= tol:
            return Result(total + 0.5 * (upper + lower), half, n)
    raise ValueError("tolerance not reached within max_terms")


def error_report(entries):
    """Table of (name, result, exact_or_None) rows plus a totals line."""
    lines = [f"{'quantity':<22}{'value':>18}{'bound':>12}{'actual':>12}"]
    for name, result, exact in entries:
        actual = "-" if exact is None else f"{abs(result.value - exact):.2e}"
        lines.append(f"{name:<22}{result.value:>18.12f}"
                     f"{result.error:>12.2e}{actual:>12}")
    total = sum(entry[1].evaluations for entry in entries)
    lines.append(f"{'TOTAL EVALUATIONS':<22}{total:>18d}")
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
import math
from quadlib import integrate, series_sum, error_report

rows = [
    ("exp on [0,1]", integrate(math.exp, 0.0, 1.0, 1e-10), math.e - 1.0),
    ("exp(-x) to inf", integrate(lambda x: math.exp(-x), 0.0, math.inf, 1e-10), 1.0),
    ("gaussian", integrate(lambda x: math.exp(-x * x), -math.inf, math.inf, 1e-10), math.sqrt(math.pi)),
    ("basel series", series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-8), math.pi ** 2 / 6.0),
]

print(error_report(rows))

runge = integrate(lambda x: 1.0 / (1.0 + 25.0 * x * x), -1.0, 1.0, 1e-10)
print("Runge integral:", runge.value, "in", runge.evaluations, "evaluations")
'''},
        ],
        "tests": [
            {"name": "Result carries value, error and evaluations", "code": r'''
import math as _m
from quadlib import Result, adaptive
_r = Result(1.5, 1e-9, 42)
assert (_r.value, _r.error, _r.evaluations) == (1.5, 1e-9, 42), f"Result fields came back as {_r!r}"
_got = adaptive(_m.sin, 0.0, _m.pi, 1e-10)
assert isinstance(_got, Result), f"adaptive returned {type(_got).__name__}, expected Result"
assert abs(_got.value - 2.0) < 1e-9, f"adaptive(sin, 0, pi) gave {_got.value!r}, expected 2.0"
assert _got.evaluations > 0, "adaptive must count its integrand calls"
'''},
            {"name": "Composite Simpson", "code": r'''
import math as _m
from quadlib import simpson
_got = simpson(lambda x: x ** 3, 0.0, 1.0, 2)
assert abs(_got - 0.25) < 1e-14, f"simpson(x^3, 0, 1, 2) gave {_got!r}, expected 0.25"
_got = simpson(_m.exp, 0.0, 1.0, 100)
assert abs(_got - (_m.e - 1.0)) < 1e-9, f"simpson(exp, 0, 1, 100) gave {_got!r}"
for _bad in (1, 3, 0, -2):
    try:
        simpson(_m.sin, 0.0, 1.0, _bad)
        assert False, f"simpson with n={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "adaptive hits proper integrals", "code": r'''
import math as _m
from quadlib import adaptive
for _name, _f, _a, _b, _want in [("sin", _m.sin, 0.0, _m.pi, 2.0),
                                 ("exp", _m.exp, 0.0, 1.0, _m.e - 1.0),
                                 ("runge", lambda x: 1.0 / (1.0 + 25.0 * x * x), -1.0, 1.0,
                                  2.0 * _m.atan(5.0) / 5.0)]:
    _r = adaptive(_f, _a, _b, 1e-10)
    assert abs(_r.value - _want) < 1e-9, f"adaptive on {_name} gave {_r.value!r}, expected {_want!r}"
    assert abs(_r.value - _want) <= _r.error + 1e-12, \
        f"On {_name} the actual error beat the claimed bound {_r.error!r}"
'''},
            {"name": "Empty, reversed and invalid intervals", "code": r'''
import math as _m
from quadlib import adaptive, integrate
_r = adaptive(_m.sin, 2.0, 2.0, 1e-9)
assert (_r.value, _r.error, _r.evaluations) == (0.0, 0.0, 0), f"Empty interval gave {_r!r}"
_f = adaptive(_m.sin, 0.0, _m.pi, 1e-10)
_b = adaptive(_m.sin, _m.pi, 0.0, 1e-10)
assert abs(_f.value + _b.value) < 1e-12, f"Reversed interval gave {_b.value!r}, expected -{_f.value!r}"
assert _b.error >= 0.0, "The error estimate must stay non-negative when the limits are swapped"
for _bad in (0.0, -1.0):
    try:
        integrate(_m.sin, 0.0, 1.0, _bad)
        assert False, f"integrate with tol={_bad} should raise ValueError"
    except ValueError:
        pass
try:
    integrate(_m.sin, float("nan"), 1.0)
    assert False, "A NaN bound should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Evaluation counters do not leak between calls", "code": r'''
import math as _m
from quadlib import adaptive
_one = adaptive(_m.sin, 0.0, _m.pi, 1e-10)
_two = adaptive(_m.sin, 0.0, _m.pi, 1e-10)
assert _one.evaluations == _two.evaluations, \
    f"Two identical calls counted {_one.evaluations} and {_two.evaluations} evaluations — the counter is shared"
'''},
            {"name": "integrate on semi-infinite domains", "code": r'''
import math as _m
from quadlib import integrate
for _name, _f, _a, _b, _want in [("exp(-x) from 0", lambda x: _m.exp(-x), 0.0, _m.inf, 1.0),
                                 ("x^-3 from 1", lambda x: x ** -3.0, 1.0, _m.inf, 0.5),
                                 ("lorentz to 0", lambda x: 1.0 / (1.0 + x * x), -_m.inf, 0.0, _m.pi / 2.0)]:
    _r = integrate(_f, _a, _b, 1e-10)
    assert abs(_r.value - _want) < 1e-8, f"integrate({_name}) gave {_r.value!r}, expected {_want!r}"
    assert _r.evaluations > 0, f"integrate({_name}) reported no evaluations"
'''},
            {"name": "integrate on the whole real line", "code": r'''
import math as _m
from quadlib import integrate
_r = integrate(lambda x: _m.exp(-x * x), -_m.inf, _m.inf, 1e-10)
assert abs(_r.value - _m.sqrt(_m.pi)) < 1e-8, \
    f"Gaussian integral gave {_r.value!r}, expected {_m.sqrt(_m.pi)!r}"
_r = integrate(lambda x: 1.0 / (1.0 + x * x), -_m.inf, _m.inf, 1e-10)
assert abs(_r.value - _m.pi) < 1e-8, f"Cauchy integral gave {_r.value!r}, expected {_m.pi!r}"
_r = integrate(_m.sin, 3.0, 3.0)
assert _r.value == 0.0 and _r.evaluations == 0, f"A degenerate interval gave {_r!r}"
'''},
            {"name": "Tightening the tolerance tightens the answer", "code": r'''
import math as _m
from quadlib import integrate
_exact = _m.e - 1.0
_loose = integrate(_m.exp, 0.0, 1.0, 1e-3)
_tight = integrate(_m.exp, 0.0, 1.0, 1e-12)
assert abs(_loose.value - _exact) < 1e-3, f"tol=1e-3 left an error of {abs(_loose.value - _exact)!r}"
assert abs(_tight.value - _exact) < 1e-11, f"tol=1e-12 left an error of {abs(_tight.value - _exact)!r}"
assert _tight.evaluations > _loose.evaluations, \
    f"A tighter tolerance used {_tight.evaluations} evaluations vs {_loose.evaluations} — it should cost more"
'''},
            {"name": "Taylor half of the library", "code": r'''
import math as _m
from quadlib import taylor_coefficients, taylor_eval, taylor_bound
assert taylor_coefficients("exp", 3) == [1.0, 1.0, 0.5, 1.0 / 6.0], \
    f"Got {taylor_coefficients('exp', 3)!r}"
assert taylor_coefficients("cos", 4)[1] == 0.0 and abs(taylor_coefficients("cos", 4)[2] + 0.5) < 1e-15, \
    f"cos coefficients came back as {taylor_coefficients('cos', 4)!r}"
_got = taylor_eval(taylor_coefficients("sin", 15), 0.7)
assert abs(_got - _m.sin(0.7)) < 1e-12, f"sin series at 0.7 gave {_got!r}, expected {_m.sin(0.7)!r}"
assert abs(taylor_bound("sin", 0.5, 3) - 0.5 ** 4 / 24.0) < 1e-18, \
    f"taylor_bound('sin', 0.5, 3) gave {taylor_bound('sin', 0.5, 3)!r}"
for _kind, _fn in [("exp", _m.exp), ("cos", _m.cos)]:
    for _x in (-1.5, 0.4, 2.0):
        _err = abs(taylor_eval(taylor_coefficients(_kind, 8), _x) - _fn(_x))
        assert _err <= taylor_bound(_kind, _x, 8) + 1e-14, \
            f"{_kind} at {_x}: error {_err!r} exceeds its bound"
for _args in [("tanh", 3), ("exp", -1)]:
    try:
        taylor_coefficients(*_args)
        assert False, f"taylor_coefficients{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "series_sum brackets the true sum", "code": r'''
import math as _m
from quadlib import series_sum, Result
_r = series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-6)
assert isinstance(_r, Result), f"series_sum returned {type(_r).__name__}, expected Result"
assert _r.evaluations == 707, f"series_sum used {_r.evaluations} terms, expected 707"
assert _r.error <= 1e-6, f"Claimed bound {_r.error!r} exceeds the tolerance"
assert abs(_r.value - _m.pi ** 2 / 6.0) <= _r.error, \
    f"Estimate {_r.value!r} lies outside its own bound of {_r.error!r} around pi^2/6"
_r = series_sum(lambda k: 1.0 / k ** 3, lambda x: 0.5 / x ** 2, 1e-8)
assert abs(_r.value - 1.2020569031595943) <= _r.error, f"Apery estimate {_r.value!r} is outside its bound"
for _bad in (0.0, -1e-9):
    try:
        series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, _bad)
        assert False, f"series_sum with tol={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "error_report shapes the table", "code": r'''
import math as _m
from quadlib import integrate, series_sum, error_report
_rows = [("exp on [0,1]", integrate(_m.exp, 0.0, 1.0, 1e-10), _m.e - 1.0),
         ("basel", series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-8), _m.pi ** 2 / 6.0),
         ("no exact", integrate(_m.sin, 0.0, 1.0, 1e-10), None)]
_rep = error_report(_rows)
assert isinstance(_rep, str), "error_report returns a string, it does not print"
_lines = _rep.split("\n")
assert len(_lines) == 5, f"Expected 1 header + 3 rows + 1 total = 5 lines, got {len(_lines)}"
assert _lines[0].startswith("quantity"), f"Header line was {_lines[0]!r}"
for _i, _row in enumerate(_rows):
    assert _lines[_i + 1].startswith(_row[0]), f"Line {_i + 1} was {_lines[_i + 1]!r}, expected to start with {_row[0]!r}"
assert _lines[3].rstrip().endswith("-"), f"A row with no exact value should end in a dash; got {_lines[3]!r}"
assert _lines[-1].startswith("TOTAL EVALUATIONS"), f"Last line was {_lines[-1]!r}"
_total = sum(_row[1].evaluations for _row in _rows)
assert _lines[-1].rstrip().endswith(str(_total)), \
    f"Totals line {_lines[-1]!r} should end with {_total}"
'''},
            {"name": "quadlib.py is import-clean and fast", "code": r'''
import time as _t
_src = open("quadlib.py").read()
assert "print(" not in _src, "quadlib.py defines routines; the printing belongs in main.py"
for _banned in ("numpy", "scipy"):
    assert _banned not in _src, f"quadlib.py must not reach for {_banned}"
import math as _m
from quadlib import integrate, series_sum
_start = _t.time()
integrate(lambda x: _m.exp(-x * x), -_m.inf, _m.inf, 1e-10)
series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-8)
_elapsed = _t.time() - _start
assert _elapsed < 5.0, f"The demo workload took {_elapsed:.2f}s, which is far too slow"
'''},
        ],
    },
}
