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
that every other sampling choice does too. So $\int_0^1 x^2\,\mathrm{d}x = \frac13$,
and that is a statement about a limit of sums, not about anything differentiated.

Keep the error term, because it is the first quantitative fact in this module:

$$R_n - \frac13 = \frac{1}{2n} + \frac{1}{6n^2} \approx \frac{1}{2n}$$

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
the order collapses. Take $\int_0^1\sqrt x\,\mathrm{d}x = \frac23$, where
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
The integral $\int_0^1 x^2\,\mathrm{d}x$ is going to come out as $\frac13$, and you
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
                            "prompt": "The limit as $n\\to\\infty$ is $\\frac13$. Write the error $S_n - \\frac13$ that the $n$-panel sum still carries.",
                            "answer": "\\frac{1}{2n}+\\frac{1}{6n^2}",
                            "hint": "Everything except the constant term survives.",
                        },
                    ],
                    "closing": r'''
Two things come out of that last line. The limit exists and equals $\frac13$, so
$\int_0^1 x^2\,\mathrm{d}x = \frac13$ by the definition alone — no antiderivative was
used anywhere.

And the error is dominated by $\frac{1}{2n}$: **first order**. Doubling the panel count
halves the error, so squeezing out one more decimal digit costs ten times the work, and
six digits would need about a million rectangles. At $n = 4$ the sum is
$\frac13 + 0.125 + 0.0104 = 0.4688$, a 40% overestimate. That number is the reason the
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
                                "That gives $3\\alpha = 2$, so $\\alpha = \\frac23$ and the trapezoid weight is $\\frac13$.",
                                "The trapezoid is wrong by twice as much, so it gets half the weight: the combination is $\\frac{2}{3}M + \\frac13 T$.",
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
$\frac13$. Here is the same argument on $x^3$, written out with the working steps
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
                               "$\\frac14 + \\frac{2n}{4n^2} + \\frac{1}{4n^2} = "
                               "\\frac14 + \\frac{1}{2n} + \\frac{1}{4n^2}$. The middle term is the one "
                               "that decides everything: $\\frac{2}{4} = \\frac12$, not $\\frac14$ and "
                               "not $1$. Check it at $n = 4$ — the expansion gives "
                               "$0.25 + 0.125 + 0.015625 = 0.390625$, and summing the four rectangles "
                               "directly gives $0.25(0.015625 + 0.125 + 0.421875 + 1) = 0.390625$.",
                    },
                    {
                        "prompt": "The limit, and therefore the integral.",
                        "hole": "?",
                        "opts": ["1/3", "1/4", "1/2", "0"],
                        "a": 1,
                        "why": "Both tails vanish and $\\frac14$ is left, so "
                               "$\\int_0^1 x^3\\,\\mathrm{d}x = \\frac14$ — which is what "
                               "$\\left[\\frac{x^4}{4}\\right]_0^1$ gives, as it must. $\\frac13$ is the "
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
Order $p$ means the error behaves like $Ch^p$, so scaling $h$ by $\frac12$ scales the
error by $\left(\frac12\right)^p$. With $p = 2$ that is a factor of $4$. A factor of
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
$f(x) = \sqrt x$ has $f'' = -\frac14 x^{-3/2}$, which blows up at the left endpoint. The
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
            "summary": "The theorem that turns an area problem into an algebra problem, and the table of antiderivatives that makes it pay.",
            "concepts": [
                r"An antiderivative is a family, not a function: if $F' = f$ then so is $F + C$, and the constant is what an initial condition exists to fix",
                r"Fundamental Theorem, first half: the accumulation function $A(x) = \int_a^x f(t)\,dt$ satisfies $A'(x) = f(x)$, so every continuous function has an antiderivative even when no formula for it exists",
                r"Fundamental Theorem, second half: $\int_a^b f = F(b) - F(a)$, which is why a closed form beats every quadrature rule in module 1 whenever you can find one",
                r"The standard table is the derivative table read backwards, with one exception: $\int x^n\,dx$ is $x^{n+1}/(n+1)$ for every $n$ except $-1$, where it is $\ln|x|$",
                r"Linearity, additivity over adjoining subintervals, and the convention $\int_b^a = -\int_a^b$ that keeps the theorem true whichever way the limits run",
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
                r"Symmetry falls out of the same move: over $[-a, a]$ an odd integrand gives $0$ and an even one gives twice the half-integral",
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
                            r"since neither factor is the derivative of the other."
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
                            r"frequencies do match and the two factors are the same kind of function."
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
                            r"the classical $\pi/4$ series, which converges so slowly that it is a good reminder that a series "
                            r"being correct and a series being useful are separate claims. The logarithm comes from "
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
