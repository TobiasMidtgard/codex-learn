"""MA111 — Calculus I: Limits & Derivatives. Author module."""

COURSE = {
    "id": "MA111",
    "title": "Calculus I — Limits & Derivatives",
    "year": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python"],
    "credits": 10,
    "hours": 110,
    "icon": "∫",
    "summary": (
        "Limits, derivatives and their numerical shadows. Every definition in the "
        "course is turned into a procedure that a machine can run, so you see where "
        "the epsilon-delta bookkeeping actually bites and where floating point "
        "quietly ruins an otherwise correct formula."
    ),
    "outcomes": [
        "Estimate a limit numerically and recognise when no limit exists",
        "Produce a delta witness for a given epsilon and check it by sampling",
        "Derive and implement forward and central difference quotients",
        "Measure the observed convergence order of a numerical rule and match it to theory",
        "Implement Newton-Raphson with derivative, divergence and iteration guards",
        "Locate critical points by a sign change of the derivative and classify them",
        "Report the global extrema of a function on a closed interval",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Stewart, *Calculus: Early Transcendentals*, 8th ed. — chapters 1-4",
        "Spivak, *Calculus*, 4th ed. — chapters 5-11",
        "Burden & Faires, *Numerical Analysis*, 10th ed. — sections 2.3 and 4.1",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Limits and continuity",
            "summary": "What a limit asserts, and how to probe one with a finite machine.",
            "concepts": [
                "The limit of f at a describes the punctured neighbourhood, never f(a) itself",
                "One-sided limits; a two-sided limit exists only when both agree",
                "The epsilon-delta definition: for every eps > 0 there is a delta > 0",
                "Failure modes: a jump, an unbounded blow-up, and endless oscillation",
                "Continuity at a means the limit exists and equals f(a)",
                "Numerical probing is evidence, not proof — catastrophic cancellation lies",
            ],
            "read": [
                {
                    "title": "The value the function never takes",
                    "minutes": 11,
                    "body": r'''
Take the function

$$f(x) = \frac{x^{2}-1}{x-1}.$$

At $x = 1$ the denominator is zero. So is the numerator, so the expression reads
$0/0$ and there is no number to report. Everywhere else it is completely ordinary.
Evaluate it just to the left, $f(0.999) = 1.999$, and just to the right,
$f(1.001) = 2.001$, and the answers close in on $2$ from both sides without ever
arriving — because arriving is the one thing the formula forbids.

So $f$ has no value at $1$ and an unmistakable *tendency* at $1$. Making that word
precise is the business of this module, and it is worth doing slowly, because every
derivative in the rest of the course is a quantity of exactly this shape: an
expression that reads $0/0$ at the point you care about and behaves perfectly well
everywhere around it. A derivative is not an awkward special case of a limit. It is
the reason limits were invented.

## What the notation claims

The sentence

$$\lim_{x \to a} f(x) = L$$

is read "the limit of $f(x)$, as $x$ tends to $a$, is $L$", and it asserts this: you
can force $f(x)$ to be as close to $L$ as anyone demands, by requiring $x$ to be close
enough to $a$ — close enough, but not equal.

Three things are settled by that sentence, and each is somewhere people go wrong.

**It never looks at $x = a$.** The set of points the claim is about is the *punctured*
neighbourhood of $a$: everything within some distance of $a$, except $a$ itself. That
is not a technicality bolted on to cope with $0/0$. It is what makes the idea useful.
The value $f(a)$ may be undefined, or defined and equal to $L$, or defined and equal
to something absurd like $-40$, and the limit is the same in all three cases, because
none of them is consulted.

**It is about every way of approaching, not one of them.** "Close to $a$" means close
on either side, along any sequence of points, in any order. A limit that only holds
for the particular values you happened to try is not a limit at all, and the second
reading in this module exists because that distinction cannot be made with a finite
table of numbers.

**It is a claim about the function, not about a procedure.** There is no step in the
definition that says "substitute". Substitution is a method that happens to work for a
large and important class of functions, and the name of that class is *continuous* —
the third reading.

## Worked: a hole you can factor out

Evaluate $\displaystyle\lim_{x \to 1}\frac{x^{2}-1}{x-1}$.

For every $x$ other than $1$:

$$\frac{x^{2}-1}{x-1} \;=\; \frac{(x-1)(x+1)}{x-1} \;=\; x+1 .$$

Line by line. The numerator factors as a difference of two squares,
$x^{2}-1 = (x-1)(x+1)$. Cancelling the common factor requires $x - 1 \neq 0$, that is
$x \neq 1$ — and $x \neq 1$ is precisely what the limit grants us. Say that sentence
out loud once, because it is the load-bearing step: *we may divide by $x-1$ because
$x-1$ is never zero anywhere the limit is looking.*

So on a punctured neighbourhood of $1$, $f$ and the polynomial $g(x) = x+1$ are the
same function. Two functions that agree on a punctured neighbourhood of $a$ have the
same limit at $a$ — the definition cannot tell them apart, since the only values it
reads are the ones on which they agree. And $g$ is a polynomial, so its limit at $1$
is its value there: $g(1) = 2$.

$$\lim_{x \to 1}\frac{x^{2}-1}{x-1} = 2 .$$

The function still has no value at $1$. Nothing in the working repaired the hole; it
found out what value would fill it.

## Worked: a hole you cannot factor out

Evaluate $\displaystyle\lim_{x \to 0}\frac{\sqrt{4+x}-2}{x}$.

Substituting gives $\sqrt{4}-2 = 0$ over $0$: the same shape as before. But this time
there is no factor to spot, because $\sqrt{4+x}-2$ is a difference, not a product.

Multiply top and bottom by the conjugate $\sqrt{4+x}+2$. That quantity is close to $4$
near $x = 0$ and in particular is never zero there, so the multiplication is legal:

$$\frac{\sqrt{4+x}-2}{x}\cdot\frac{\sqrt{4+x}+2}{\sqrt{4+x}+2}
 \;=\; \frac{\left(\sqrt{4+x}\right)^{2}-2^{2}}{x\left(\sqrt{4+x}+2\right)} .$$

The numerator is now a difference of two squares, and the root disappears from it:

$$\frac{(4+x)-4}{x\left(\sqrt{4+x}+2\right)} \;=\; \frac{x}{x\left(\sqrt{4+x}+2\right)} .$$

Cancel the $x$ — legal for the same reason as before, since $x \neq 0$ on the
punctured neighbourhood:

$$\frac{1}{\sqrt{4+x}+2} .$$

This last expression has no difficulty at $x = 0$ at all: the root of a positive
number, plus $2$, in a denominator that is nowhere near zero. Its limit is its value,

$$\lim_{x \to 0}\frac{\sqrt{4+x}-2}{x} \;=\; \frac{1}{\sqrt{4}+2} \;=\; \frac{1}{4} .$$

A quick numerical check: the original quotient at $x = 10^{-3}$ reads $0.2499843\ldots$,
closing on $0.25$ from below.

The conjugate did not remove a difficulty, it moved one. The zero of the numerator was
hidden inside a difference of roots; multiplying by the conjugate turned that into a
difference of squares, where the zero is visible as a factor of $x$ and can be
cancelled. Nearly every $0/0$ in this course is handled the same way — find the hidden
factor of $(x-a)$ upstairs, by factorising, by rationalising, or by expanding.

## One side at a time

Sometimes the two directions of approach disagree. Take

$$s(x) = \frac{|x-2|}{x-2} .$$

For $x > 2$ the quantity $x - 2$ is positive, so $|x-2| = x-2$ and $s(x) = +1$. For
$x < 2$ it is negative, so $|x-2| = -(x-2)$ and $s(x) = -1$. Writing
$\lim_{x\to 2^{+}}$ for the approach from above and $\lim_{x\to 2^{-}}$ for the
approach from below,

$$\lim_{x\to 2^{+}} s(x) = 1, \qquad \lim_{x\to 2^{-}} s(x) = -1 .$$

The two-sided limit exists exactly when both one-sided limits exist and are equal. Here
they are not, so $\lim_{x\to 2} s(x)$ **does not exist**. Not "is zero", not "is both":
there is no number $L$ at all. To see why, suppose someone nominates one. Every
punctured neighbourhood of $2$ contains points where $s = 1$ and points where
$s = -1$, so it contains points at distance $|1-L|$ from $L$ and points at distance
$|-1-L|$. Those two distances add to at least $2$, by the triangle inequality, so at
least one of them is at least $1$ — and a tolerance of, say, $0.5$ can never be met.

## Three ways to have no limit

**A jump.** The two sides converge, to different values. $s$ above is the model case.

**A blow-up.** The values leave every bound: $1/x^{2}$ as $x \to 0$. It is standard to
write $\lim_{x\to 0} 1/x^{2} = \infty$, and it is important to know what that sentence
is not. There is no number $\infty$, and the sentence is not an existence claim; it is
shorthand recording *how* the limit fails to exist — the values eventually exceed any
bound you name.

**Oscillation.** The values neither settle nor run away. $\sin(\pi/x)$ as $x \to 0$
sweeps the whole of $[-1, 1]$ infinitely often inside every punctured neighbourhood of
zero, however small. There is no $L$, and the failure is not visible in any finite
amount of evidence: sample it at $x = 1, \tfrac12, \tfrac13, \ldots, \tfrac1n$ and
every single reading is $\sin(n\pi) = 0$. A table of exact zeros is exactly what a
function tending to zero looks like. This one is not.

## The mistake

The commonest error is to compute $f(a)$ and report it as the limit. For most
functions you meet it gives the right answer — every polynomial, every exponential,
every sine — and that is what makes it dangerous: it is a habit reinforced by hundreds
of correct results before it fails. It works when $f$ is continuous at $a$, which is a
theorem about a class of functions, not the meaning of the notation. In the one case
that matters, $0/0$, substitution returns nothing at all — and $0/0$ is the shape of
every derivative in this course.

The second commonest is to see $0/0$ and conclude the limit does not exist. $0/0$ is
not a value; it is a report that this particular method has not settled the question.
At $x = 1$, all three of

$$\frac{x^{2}-1}{x-1}, \qquad \frac{x-1}{x^{2}-1}, \qquad \frac{x-1}{(x-1)^{3}}$$

read $0/0$, and their limits are $2$, $\tfrac12$ and nonexistent respectively — the
last because it reduces to $1/(x-1)^{2}$, which blows up. The symbol tells you nothing
about which of those you are in. The algebra does.

## Where this stops

A limit at $a$ requires points to approach $a$ through. For $f(x) = \sqrt{x}$ no
punctured neighbourhood of $0$ lies inside the domain, so the two-sided statement
$\lim_{x\to 0}\sqrt{x}$ has nothing to quantify over and is not asked; the honest
statement is the one-sided $\lim_{x\to 0^{+}}\sqrt{x} = 0$. The same caution applies
at any endpoint of a domain, and it is why one-sided limits are part of the basic
vocabulary rather than a refinement.

And none of the arithmetic above is a proof yet. Factoring and cancelling rests on the
claim that two functions agreeing on a punctured neighbourhood have the same limit,
and "the limit of a polynomial is its value" is itself something to be established.
Both follow from a definition sharp enough to be argued with, which is the next
reading. What the algebra genuinely gives you is the candidate $L$ — and you cannot
verify a limit you have not first guessed.
''',
                },
                {
                    "title": "Epsilon, delta, and the order of the words",
                    "minutes": 12,
                    "body": r'''
Everything in the previous reading rests on the phrase *as close as you like*. That is
a promise about an unlimited supply of demands, and no finite amount of checking can
keep it. The oscillating example makes the point brutally: $\sin(\pi/x)$ sampled at
$x = 1/n$ returns exactly zero for every $n$ you have the patience to try, and yet
there is no limit at all. A table can never separate "tends to $L$" from "happens to
pass through $L$ at the points I chose to look".

So the definition has to quantify over every possible demand at once, and it has to do
it in a way that a person can actually discharge in a few lines. Weierstrass's
arrangement does both, and it has not been improved on in a hundred and fifty years.

## A game with two players

An adversary picks a tolerance $\epsilon > 0$ and says: *get $f(x)$ within $\epsilon$
of $L$, and I may pick $\epsilon$ as small as I like.*

You reply with a distance $\delta > 0$ and a claim: *every $x$ within $\delta$ of $a$,
other than $a$ itself, has $f(x)$ within $\epsilon$ of $L$.*

You have proved the limit if you have a reply to every possible challenge. The point
of the arrangement is that you almost never have to answer them one at a time: if you
can produce $\delta$ as a *formula in $\epsilon$*, you have answered infinitely many
challenges in one line.

Everything hangs on the order. The adversary moves first. Your $\delta$ is allowed to
depend on their $\epsilon$; their $\epsilon$ is not allowed to depend on your $\delta$.
Swapping the two produces a different statement, and almost always a false one.

## The definition

$$\lim_{x\to a} f(x) = L
\quad\text{means}\quad
\forall \epsilon > 0 \;\; \exists\, \delta > 0 \;:\;
0 < |x - a| < \delta \;\Longrightarrow\; |f(x) - L| < \epsilon .$$

Read it in pieces.

- $|f(x) - L| < \epsilon$ — the output is inside the tolerance.
- $|x - a| < \delta$ — the input is inside your window.
- $0 < |x - a|$ — the puncture. This is the character that excludes $x = a$, and it is
  the entire reason an expression that is $0/0$ at $a$ can still have a limit there.
- $\forall \epsilon\, \exists \delta$ — every challenge, some reply.

Nothing in the statement mentions $f(a)$, and nothing requires $f$ to be defined at
$a$ at all.

## Worked: a straight line

Claim: $\displaystyle\lim_{x\to 2}(3x+1) = 7$.

Start where the definition ends, with the quantity it controls, and simplify it until
$|x-2|$ appears:

$$|f(x) - L| = |(3x+1) - 7| = |3x - 6| = |3(x-2)| = 3\,|x-2| .$$

The constant comes out of the modulus as $3$, not $\pm 3$, because $3$ is positive.
Now the requirement $|f(x)-7| < \epsilon$ is the requirement $3|x-2| < \epsilon$, which
is the requirement

$$|x - 2| < \frac{\epsilon}{3} .$$

That is a statement of exactly the form the definition wants, so take
$\delta = \epsilon/3$. It is positive, because $\epsilon$ is, and that is the one
property a $\delta$ must have.

*Verification, written forwards.* Let $\epsilon > 0$ and put $\delta = \epsilon/3 > 0$.
Suppose $0 < |x - 2| < \delta$. Then

$$|f(x) - 7| = 3|x-2| < 3\delta = 3\cdot\frac{\epsilon}{3} = \epsilon .$$

Since $\epsilon$ was arbitrary, the limit is $7$. $\blacksquare$

A number, to see it move: $\epsilon = 0.06$ gives $\delta = 0.02$. At $x = 2.019$,
which is inside that window, $f(x) = 3(2.019)+1 = 7.057$, and the error $0.057$ is
indeed under $0.06$.

Notice how the proof was found: by working *backwards* from the target inequality
until $\delta$ fell out, and then written *forwards* from the assumption. That is the
standard shape and it is not cheating. The backwards work is discovery; the paragraph
beginning "let $\epsilon > 0$" is the proof.

## Worked: a curve, where the constant will not come out

Claim: $\displaystyle\lim_{x\to 3} x^{2} = 9$.

Same opening move:

$$|x^{2} - 9| = |(x-3)(x+3)| = |x-3|\,|x+3| .$$

The first factor is the one the definition lets you make small. The second is the
problem: $|x+3|$ is not a constant, so you cannot simply divide the target by it and
call the result $\delta$. A $\delta$ containing $x$ is not a $\delta$ at all — more on
that below.

The way out is to restrict $\delta$ in advance. Nothing stops you promising to be more
careful than necessary, so **insist that $\delta \le 1$**. Then $|x-3| < \delta \le 1$
gives $2 < x < 4$, hence $5 < x+3 < 7$, hence

$$|x+3| < 7 \qquad\text{whenever } |x-3| < 1 .$$

The nuisance factor is now bounded by a constant, and the rest is the linear argument:

$$|x^{2}-9| = |x-3|\,|x+3| < 7\,|x-3| ,$$

so forcing $7|x-3| < \epsilon$, that is $|x-3| < \epsilon/7$, is enough. Two
restrictions have to hold at once, so take

$$\delta = \min\!\left(1, \frac{\epsilon}{7}\right) .$$

*Verification.* Let $\epsilon > 0$ and let $\delta$ be that minimum, which is positive
because both entries are. Suppose $0 < |x-3| < \delta$. Because $\delta \le 1$ we have
$|x+3| < 7$; because $\delta \le \epsilon/7$ we have $|x-3| < \epsilon/7$. Multiplying,

$$|x^{2}-9| = |x-3|\,|x+3| < \frac{\epsilon}{7}\cdot 7 = \epsilon . \qquad\blacksquare$$

Numbers again: $\epsilon = 0.35$ gives $\epsilon/7 = 0.05$, which is less than $1$, so
$\delta = 0.05$. At the right-hand edge, $x = 3.05$ and $x^{2} = 9.3025$, an error of
$0.3025$; at the left-hand edge, $x = 2.95$ and $x^{2} = 8.7025$, an error of $0.2975$.
Both are under $0.35$, and the right-hand edge is the tighter of the two — which is
worth noticing, because it is the side on which $|x+3|$ is larger.

That $\delta$ is *sufficient*, not largest. The largest $\delta$ that actually works
here is $\min\left(\sqrt{9.35}-3,\; 3-\sqrt{8.65}\right) = \min(0.0578, 0.0589)
= 0.0578$, and nobody wants to carry that formula around. The definition never asks
for the best $\delta$: any working one proves the claim, and anything smaller than a
working $\delta$ also works. That last fact is why taking a minimum is safe, and why a
crude bound like $|x+3| < 7$ costs nothing.

## The mistake: a delta that mentions x

The tempting move at the awkward step is to write

$$\delta = \frac{\epsilon}{|x+3|} ,$$

because if you substitute it the algebra closes beautifully. It is not a legal answer.
The definition says *there exists a $\delta$ such that for all $x$*: $\delta$ is chosen
before $x$ is, and one $\delta$ has to serve the whole window at once. An expression
containing $x$ is a different $\delta$ at every point, which is not a window.

It is tempting because the backwards scratch work leads there naturally — you divide by
$|x+3|$ because that is what you would do with any other factor — and because
recognising that the nuisance factor must be *bounded by a constant* rather than
divided out is the only genuinely new idea in the whole business. Once seen, it works
everywhere: pre-restrict $\delta$, bound the extra factor on that restricted window,
then take a minimum.

A second mistake is quieter: reversing the quantifiers to "there is a $\delta > 0$
such that for every $\epsilon > 0$ ...". That sentence says one window works for every
tolerance however small, which forces $f$ to be constant and equal to $L$ near $a$. It
is a much stronger claim, it is false for almost every function, and it is easy to
write by accident because English tolerates the reordering and logic does not.

## Where the definition stops

It says nothing whatever about $f(a)$. A function can have a limit at a point where it
is undefined, at a point where it takes an unrelated value, or at a point where it
behaves itself; the definition reads none of those.

It needs points to approach through. If no punctured neighbourhood of $a$ lies inside
the domain — $a = 0$ for $\sqrt{x}$, or an isolated point of a domain — the two-sided
statement has nothing to quantify over, and the one-sided version is what to use.

It defines a *finite* limit only. The sentence $\lim_{x\to 0} 1/x^{2} = \infty$ is a
different definition with a different shape — for every $M$ there is a $\delta$ making
$f(x) > M$ — and it is not an instance of this one. Treating $\infty$ as a value of
$L$ and putting it inside $|f(x)-L| < \epsilon$ produces nonsense.

And it verifies; it does not discover. Producing $\delta$ confirms a value of $L$ you
already had. Where $L$ comes from is the algebra of the previous reading.
''',
                },
                {
                    "title": "Continuity, and why the machine cannot check it",
                    "minutes": 11,
                    "body": r'''
Almost every limit you will ever evaluate, you will evaluate by substituting. The two
readings before this one have been at pains to insist that substitution is not what a
limit means. Both statements are true, and the word that reconciles them is
*continuity*.

Continuity is not a further topic that follows limits. It is the name for the case in
which the whole apparatus collapses into arithmetic — and knowing exactly which
functions are in that case is what lets you stop thinking about $\epsilon$ and $\delta$
for the rest of the course.

## Three conditions, written as one

A function $f$ is continuous at $a$ when all three of these hold.

1. $f(a)$ exists — that is, $a$ is in the domain.
2. $\lim_{x\to a} f(x)$ exists.
3. The two are equal.

Which is why the whole definition is normally written in a single line,

$$\lim_{x\to a} f(x) = f(a) ,$$

a sentence that quietly asserts all three: both sides have to mean something before
they can be compared. Read as a statement about notation, it says the limit sign and
the function symbol may be exchanged, $\lim f(x) = f(\lim x)$ — and that exchange,
harmless-looking and false in general, is exactly the property being named.

The functions with the property are the ones you already trust. Polynomials are
continuous everywhere. Rational functions are continuous everywhere their denominator
is non-zero. So are $\sin$, $\cos$ and $\exp$; $\sqrt{\cdot}$ on $[0,\infty)$, one-sidedly
at the endpoint; $\log$ on $(0,\infty)$. And sums, differences, products, quotients
with non-zero denominator, and compositions of continuous functions are continuous. It
is that closure property, rather than any individual entry on the list, that makes
substitution work so often: almost anything you can write down is built out of
continuous pieces by continuous operations, and is therefore continuous wherever the
pieces are defined.

## Worked: where a rational function fails, and how

$$r(x) = \frac{x^{2}-5x+6}{x^{2}-4} .$$

The denominator vanishes at $x = 2$ and $x = -2$, and nowhere else. Away from those two
points $r$ is a quotient of polynomials with non-zero denominator, hence continuous, so
those are the only two places anything can go wrong. Factor both halves:

$$r(x) = \frac{(x-2)(x-3)}{(x-2)(x+2)} .$$

**At $x = 2$.** For every $x$ other than $2$ and $-2$ the common factor cancels, leaving
$r(x) = \dfrac{x-3}{x+2}$. That reduced expression is continuous at $2$, so

$$\lim_{x\to 2} r(x) = \frac{2-3}{2+2} = -\frac{1}{4} .$$

The limit exists; $r(2)$ does not. Condition 2 holds and condition 1 fails, which is a
**removable** discontinuity — define $r(2) = -\tfrac14$ and the repaired function is
continuous there.

**At $x = -2$.** The reduced expression $\dfrac{x-3}{x+2}$ has numerator tending to
$-5$, which is not zero, over a denominator tending to $0$. The quotient leaves every
bound. Approaching from the right, $x+2 \to 0^{+}$ and $r(x) \to -\infty$; from the
left, $x + 2 \to 0^{-}$ and $r(x) \to +\infty$. This is an **infinite** discontinuity,
and no value assigned to $r(-2)$ can repair it: condition 2 fails, and condition 2 is
not about the point.

Both points made the denominator vanish, and only one of them was a genuine break. The
whole test is whether the numerator vanishes there too.

## Worked: patching a hole, and the trap in it

$$g(x) = \begin{cases}
\dfrac{x^{2}+cx-6}{x-2}, & x \neq 2, \\[6pt]
d, & x = 2 .
\end{cases}$$

Find the constants $c$ and $d$ that make $g$ continuous at $2$.

The trap is to go straight for $d$ — to reason that $d$ is whatever the fraction tends
to, and start computing. But for *any* $c$ the denominator vanishes at $2$, and unless
the numerator vanishes there too the quotient is a non-zero number over something
going to zero, the limit does not exist, and no choice of $d$ can help. So the first
condition constrains $c$, not $d$.

Numerator at $x = 2$:

$$2^{2} + 2c - 6 = 4 + 2c - 6 = 2c - 2 ,$$

which is zero exactly when $c = 1$. With $c = 1$ the numerator is $x^{2}+x-6$, and

$$x^{2}+x-6 = (x+3)(x-2) ,$$

so for $x \neq 2$ we have $g(x) = x+3$, whose limit at $2$ is $5$. Hence $c = 1$ and
$d = 5$.

Test the trap by taking a wrong $c$, say $c = 0$. Then $g(x) = \dfrac{x^{2}-6}{x-2}$,
whose numerator at $2$ is $-2$. Approaching from above, $x-2 \to 0^{+}$ and
$g \to -\infty$; from below, $g \to +\infty$. There is no $d$ at all, and any answer
of the form "$d$ = something" would have been wrong before it was computed.

## What continuity buys, and what it does not

It buys substitution, which is most of the practical value. It buys composition, so
$\lim_{x\to a} \sin(p(x)) = \sin(p(a))$ for a polynomial $p$ with no further thought.
And on a **closed, bounded** interval it buys the theorems the next module runs on: a
continuous function on $[a,b]$ attains a greatest and a least value, and takes every
value between $f(a)$ and $f(b)$.

Both of those need the interval closed, and both fail the moment it is not. The
function $h(x) = x$ on the open interval $(0,1)$ is continuous and attains neither a
maximum nor a minimum, because the candidates $0$ and $1$ are not in the interval. The
function $1/x$ on $(0,1]$ is continuous and unbounded. Neither is a pathology; both are
one missing endpoint.

What continuity does not buy is smoothness. $|x|$ is continuous at $0$ — its limit
there is $0$ and its value there is $0$ — and it has no derivative at $0$, because the
two one-sided difference quotients are $+1$ and $-1$ and disagree. Continuity is a
statement about values; differentiability, from the next module on, is a statement
about a limit of slopes, and it is strictly stronger.

## Why the machine cannot check any of this

The lab in this module builds a numerical limit-prober, so it is worth knowing in
advance what such a thing cannot do.

Take $g(x) = \dfrac{\sqrt{1+x}-1}{x}$, whose limit at $0$ is $\tfrac12$ by the
conjugate argument of the first reading. Evaluated in ordinary double precision:

```text
x = 1e-6     0.4999998750587764
x = 1e-10    0.5000000413701855
x = 1e-13    0.49960036108132044
x = 1e-15    0.44408920985006256
x = 1e-16    0.0
```

The early rows converge on $0.5$, as they should. Then the sequence turns round and
walks away, and at $x = 10^{-16}$ it returns exactly zero. No mathematics went wrong.
A double carries about $16$ significant decimal digits, so $1 + 10^{-16}$ rounds to
exactly $1.0$; then $\sqrt{1+x}$ is exactly $1$, the numerator is exactly $0$, and
zero divided by $10^{-16}$ is zero. Subtracting two nearly equal numbers threw away
every significant digit of their difference. This is **catastrophic cancellation**, and
it is the normal behaviour of the normal $0/0$ expression evaluated too near the point
of interest — which is to say, exactly where a naive prober would want to look.

So three warnings, all of which the lab will make you handle. A table that settles down
is evidence and not proof. A table that walks away may be a real failure or may be
arithmetic noise, and the two look identical. And a table of clean zeros — the
$\sin(\pi/x)$ case from the first reading — can be entirely consistent and entirely
misleading.

Rationalising the expression by hand first turns $g$ into $1/(\sqrt{1+x}+1)$, which is
numerically harmless at every $x$ and returns $0.5$ steadily however small the step.
That is a good habit in its own right, and it is a concrete reason why the algebra of
the first reading is worth having: the form of an expression does not change its
mathematics and completely changes its arithmetic.

## Where continuity stops

Continuity at a point is a statement about a whole neighbourhood of that point, so it
is not something you can inspect by evaluating anywhere finite. At an endpoint of a
domain only the one-sided version is available, and $\sqrt{x}$ at $0$ is continuous
from the right and nothing at all from the left. And a function continuous at every
point of an interval can still be very badly behaved by the standards of the next
module — continuous everywhere and differentiable nowhere is possible, and the fact
that no such function is in this course does not make the implication run backwards.
''',
                },
            ],
            "derive": [
                {
                    "title": "A delta for a straight line",
                    "minutes": 11,
                    "vars": ["x", "a", "c", "m", "L", "epsilon", "delta"],
                    "brief": r'''
The claim is $\displaystyle\lim_{x\to 2}(3x+1) = 7$, and the job is to produce a
$\delta$ for an arbitrary $\epsilon$ rather than for one lucky value of it.

The method is the same every time: start from $|f(x)-L|$, the quantity the definition
controls, and rewrite it until $|x-a|$ appears as a factor. Nothing here needs an
inequality yet — the first move is pure algebra.
''',
                    "steps": [
                        {
                            "prompt": "Write $f(x) - L$ for $f(x) = 3x+1$ and $L = 7$, with the constant factored out so that $(x-2)$ appears explicitly.",
                            "answer": "3(x-2)",
                            "placeholder": "3(x - \\ldots)",
                            "hint": "$(3x+1)-7 = 3x-6$, and $6$ is $3$ times something.",
                        },
                        {
                            "prompt": "Taking moduli gives $|f(x)-7| = 3\\,|x-2|$, since $3 > 0$. The definition wants that under $\\epsilon$. What must $|x-2|$ be under? Give the bound in terms of $\\epsilon$.",
                            "answer": "\\frac{\\epsilon}{3}",
                            "hint": "Divide both sides of $3|x-2| < \\epsilon$ by the positive constant $3$.",
                            "deconstruct": [
                                "$3|x-2| < \\epsilon$ is an inequality between two positive quantities.",
                                "Dividing an inequality by a positive number preserves it, so $|x-2| < \\epsilon/3$.",
                            ],
                        },
                        {
                            "prompt": "Run the same argument on a general line. For $f(x) = mx + c$ with $m > 0$, at any point $a$, with $L = ma + c$, write the $\\delta$ the argument produces in terms of $\\epsilon$ and $m$.",
                            "answer": "\\frac{\\epsilon}{m}",
                            "hint": "$|f(x) - L| = |mx + c - ma - c| = m|x-a|$ because $m$ is positive. Then repeat the division.",
                            "deconstruct": [
                                "$f(x) - L = (mx+c) - (ma+c) = m(x-a)$; the constant $c$ cancels.",
                                "So $|f(x)-L| = m\\,|x-a|$, and requiring that under $\\epsilon$ requires $|x-a| < \\epsilon/m$.",
                                "The slope is the only feature of the line that survives: steeper means smaller $\\delta$.",
                            ],
                        },
                        {
                            "prompt": "Back to $f(x) = 3x+1$ at $a = 2$. An adversary offers $\\epsilon = 0.06$. Write the largest $\\delta$ this argument produces.",
                            "answer": "0.02",
                            "hint": "Put $\\epsilon = 0.06$ into the formula you found two steps ago.",
                        },
                    ],
                    "closing": r'''
Written out forwards, that is a complete proof. Let $\epsilon > 0$, put
$\delta = \epsilon/3 > 0$, and suppose $0 < |x-2| < \delta$; then
$|f(x)-7| = 3|x-2| < 3\delta = \epsilon$. Since $\epsilon$ was arbitrary, the limit is
$7$.

Two things generalise. The $\delta$ came out as a formula in $\epsilon$, which is what
answers infinitely many challenges at once; and it came out proportional to
$1/m$, so a steeper line needs a narrower window for the same tolerance. That ratio
$\epsilon/\delta$ is the slope, and three modules from now it will be the derivative —
which is one reason the linear case is the case worth being fluent in.

What does *not* generalise is the ease. The step "$|f(x)-L| = m|x-a|$" worked because
the factor multiplying $|x-a|$ was a constant. For anything curved it is not, and that
single difficulty is the whole content of the next derivation.
''',
                },
                {
                    "title": "Rationalising a zero over zero",
                    "minutes": 11,
                    "vars": ["x", "L"],
                    "brief": r'''
Evaluate $\displaystyle\lim_{x\to 0}\frac{\sqrt{1+x}-1}{x}$.

Substituting $0$ gives $0/0$, and there is no factor of $x$ to be seen: the numerator
is a difference of two things, not a product. The move that exposes one is to multiply
top and bottom by the conjugate $\sqrt{1+x}+1$, which is near $2$ around $x = 0$ and in
particular never zero there, so nothing illegal happens.
''',
                    "steps": [
                        {
                            "prompt": "Multiply the numerator $\\sqrt{1+x}-1$ by the conjugate $\\sqrt{1+x}+1$ and simplify completely. Write the result.",
                            "answer": "x",
                            "placeholder": "a polynomial in x",
                            "hint": "$(A-B)(A+B) = A^2 - B^2$ with $A = \\sqrt{1+x}$ and $B = 1$.",
                            "deconstruct": [
                                "$\\left(\\sqrt{1+x}\\right)^{2} = 1+x$, because squaring undoes the root of a non-negative quantity.",
                                "$1^{2} = 1$, so the difference is $(1+x) - 1$.",
                            ],
                        },
                        {
                            "prompt": "The denominator was multiplied by the same factor. Write the whole fraction as it now stands, before anything is cancelled.",
                            "answer": "\\frac{x}{x(\\sqrt{1+x}+1)}",
                            "hint": "Numerator: what you just found. Denominator: the original $x$, times the conjugate.",
                        },
                        {
                            "prompt": "On a punctured neighbourhood of $0$ the variable $x$ is never zero, so the common factor may be cancelled. Write what is left.",
                            "answer": "\\frac{1}{\\sqrt{1+x}+1}",
                            "hint": "Divide top and bottom by $x$. The justification is the puncture in the definition, not luck.",
                        },
                        {
                            "prompt": "That expression is continuous at $x = 0$ — a root of a positive number, in a denominator that is not zero — so its limit is its value there. Write the limit.",
                            "answer": "\\frac{1}{2}",
                            "hint": "Put $x = 0$ into $1/(\\sqrt{1+x}+1)$.",
                        },
                    ],
                    "closing": r'''
So $\displaystyle\lim_{x\to 0}\frac{\sqrt{1+x}-1}{x} = \frac{1}{2}$, and the original
expression, which had no value at $0$ and no obvious tendency either, turns out to be a
disguise worn by $1/(\sqrt{1+x}+1)$ — a function with no difficulty at $0$ whatsoever.

Two things to take from it. First, the conjugate did not remove the zero of the
numerator; it made it visible. Every $0/0$ with a finite limit hides a factor of
$(x-a)$ upstairs, and the technique — factorise, rationalise, expand — is whatever
exposes it in the case at hand.

Second, the two forms are equal as functions everywhere except at $x=0$, and they are
wildly different as *computations*. Ask a computer for the left-hand form at
$x = 10^{-16}$ and it answers $0$, because $1 + 10^{-16}$ rounds to $1$ and the
numerator dies. Ask it for $1/(\sqrt{1+x}+1)$ at the same point and it answers $0.5$.
The algebra you have just done is also the fix for that, which is the subject of the
last reading in this module.
''',
                },
                {
                    "title": "A delta for a curve: bounding the nuisance factor",
                    "minutes": 14,
                    "vars": ["x", "L", "epsilon", "delta"],
                    "brief": r'''
Claim: $\displaystyle\lim_{x\to 3} x^{2} = 9$.

The opening move is the same as for a line — rewrite $|f(x)-L|$ so that $|x-3|$ appears
as a factor. What is different is what multiplies it. For a line that was a constant
and could be divided out. Here it is another function of $x$, and dividing by it would
produce a $\delta$ that depends on $x$, which is not a legal answer.

The fix is to promise in advance to be more careful than necessary, and use that
promise to replace the nuisance factor by a constant.
''',
                    "steps": [
                        {
                            "prompt": "Factor $x^{2}-9$ so that $(x-3)$ appears explicitly.",
                            "answer": "(x-3)(x+3)",
                            "placeholder": "(x - 3)(\\ldots)",
                            "hint": "A difference of two squares, $A^{2}-B^{2} = (A-B)(A+B)$.",
                        },
                        {
                            "prompt": "Agree in advance never to take $\\delta$ larger than $1$. Then $|x-3| < 1$, so $2 < x < 4$ and hence $5 < x+3 < 7$. Under that restriction, write the constant that bounds $x+3$ from above.",
                            "answer": "7",
                            "hint": "The largest $x$ can be is just under $4$, so the largest $x+3$ can be is just under that plus $3$.",
                            "deconstruct": [
                                "$|x-3| < 1$ means $-1 < x - 3 < 1$, i.e. $2 < x < 4$.",
                                "Adding $3$ throughout gives $5 < x+3 < 7$.",
                                "Since $x+3$ is positive on that window, $|x+3| < 7$ as well.",
                            ],
                        },
                        {
                            "prompt": "So $|x^{2}-9| = |x-3|\\,|x+3| < 7\\,|x-3|$ whenever $|x-3| < 1$. To force $7|x-3| < \\epsilon$, what must $|x-3|$ be under? Give the bound in terms of $\\epsilon$.",
                            "answer": "\\frac{\\epsilon}{7}",
                            "hint": "Divide the inequality by the positive constant $7$ — exactly the step that worked for a straight line.",
                        },
                        {
                            "prompt": "Both restrictions have to hold at once, so $\\delta = \\min(1, \\epsilon/7)$. Take $\\epsilon = 0.35$; here the second entry is the smaller. Write the $\\delta$ this proof produces.",
                            "answer": "0.05",
                            "hint": "$0.35$ divided by $7$, and check it against $1$.",
                        },
                        {
                            "prompt": "Check the claim at the far edge of that window, which is the worse of the two sides because $|x+3|$ is larger there. With $x = 3.05$, write $x^{2} - 9$ as an exact decimal.",
                            "answer": "0.3025",
                            "hint": "$3.05^{2} = 9.3025$; subtract $9$.",
                            "deconstruct": [
                                "$3.05^{2} = (3 + 0.05)^{2} = 9 + 2(3)(0.05) + 0.05^{2}$.",
                                "$= 9 + 0.3 + 0.0025 = 9.3025$.",
                                "Subtracting $9$ leaves $0.3025$, and the tolerance was $0.35$.",
                            ],
                        },
                    ],
                    "closing": r'''
$0.3025 < 0.35$, so the window holds — and at the other edge, $2.95^{2} = 8.7025$,
an error of $0.2975$, comfortably inside as well. The right-hand side is the tighter
one, exactly as the bound $|x+3| < 7$ predicted.

The $\delta$ produced here is sufficient, not maximal. The largest window that actually
works is $\min(\sqrt{9.35}-3,\; 3-\sqrt{8.65}) = \min(0.0578, 0.0589) = 0.0578$, and
nothing is gained by finding it. The definition asks only that *some* positive $\delta$
work, and anything smaller than a working $\delta$ works too — which is precisely what
makes the crude bound $|x+3| < 7$ and the $\min$ legitimate rather than sloppy.

The mistake to avoid is writing $\delta = \epsilon/|x+3|$. Substituted back it appears
to close the argument, and it is not an answer: the definition chooses $\delta$ before
$x$, so one number must serve the whole window. Whenever a factor of $x$ is left over,
the move is not to divide by it but to pre-restrict $\delta$, bound it by a constant on
that restricted window, and take a minimum at the end. That recipe handles every
polynomial in this course.
''',
                },
                {
                    "title": "Choosing the constants that remove a discontinuity",
                    "minutes": 12,
                    "vars": ["x", "c", "d", "L"],
                    "brief": r'''
A function is defined in two pieces:

$$g(x) = \begin{cases}
\dfrac{x^{2}+cx-6}{x-2}, & x \neq 2, \\[6pt]
d, & x = 2 .
\end{cases}$$

Find $c$ and $d$ making $g$ continuous at $2$. The order matters and it is not the
order most people start in: $d$ can only be chosen once the limit exists, and whether
the limit exists at all is decided by $c$.
''',
                    "steps": [
                        {
                            "prompt": "The denominator vanishes at $x=2$ for every $c$. For the quotient to have a finite limit there, the numerator must vanish too. Substitute $x = 2$ into $x^{2}+cx-6$ and write the resulting expression in $c$.",
                            "answer": "4+2c-6",
                            "placeholder": "an expression in c",
                            "hint": "$2^{2} = 4$ and $c \\times 2 = 2c$.",
                        },
                        {
                            "prompt": "Set that expression to zero and solve. Write $c$.",
                            "answer": "1",
                            "hint": "$2c - 2 = 0$.",
                        },
                        {
                            "prompt": "With $c = 1$ the numerator is $x^{2}+x-6$. Factor it so that $(x-2)$ appears explicitly.",
                            "answer": "(x-2)(x+3)",
                            "hint": "Two numbers multiplying to $-6$ and adding to $+1$.",
                            "deconstruct": [
                                "Look for $(x-2)(x+k)$; expanding gives $x^{2} + (k-2)x - 2k$.",
                                "Matching the constant term, $-2k = -6$, so $k = 3$.",
                                "Check the middle term: $k - 2 = 1$, which is the coefficient wanted.",
                            ],
                        },
                        {
                            "prompt": "Cancel the common factor — legal because $x \\neq 2$ on a punctured neighbourhood — and evaluate the limit at $x = 2$. Write the value $d$ must take.",
                            "answer": "5",
                            "hint": "After cancelling, the function agrees with $x+3$ everywhere except at $2$ itself.",
                        },
                    ],
                    "closing": r'''
So $c = 1$ and $d = 5$, and with those the repaired $g$ is just $x+3$ in disguise.

The reason to do it in this order is that the other order fails silently. Take $c = 0$:
the numerator at $2$ is $-2$, so $g(x) = (x^{2}-6)/(x-2)$ runs to $-\infty$ from above
and $+\infty$ from below, and *no* value of $d$ makes $g$ continuous. Anyone who
started by computing $d$ would still produce a number — the arithmetic does not
complain — and it would be a number for a limit that does not exist.

That is the general shape of a removable discontinuity. A vanishing denominator is not
by itself a break in the graph; it is a break only when the numerator does not vanish
with it. The test is one substitution, and it is worth making before any other work.
''',
                },
            ],
            "blanks": {
                "title": "An epsilon-delta proof, line by line",
                "minutes": 9,
                "caption": "the standard shape of the argument, with four steps removed",
                "lang": "text",
                "brief": r'''
Below is a complete proof that $\displaystyle\lim_{x\to 3}(4x-5) = 7$, written the way
one is normally written: the scratch work that *finds* $\delta$ comes first, then the
verification that runs forwards from the assumption.

Four steps have been taken out. Three are algebra; one is the condition that makes a
$\delta$ legal at all, and is where most wrong proofs go wrong.
''',
                "listing": """Claim:   lim (4x - 5) = 7    as  x -> 3
         ----------------------

Proof.   Let eps > 0 be given.  We must produce a delta > 0.

  Scratch work.  Start from the quantity the definition controls
  and make |x - 3| appear:

     |f(x) - L|  =  |(4x - 5) - 7|
                 =  |4x - 12|
                 =  ___ |x - 3|            constant out of the modulus

  The definition demands |f(x) - L| < eps, so it is enough to have

     4 |x - 3|  <  eps        i.e.        |x - 3|  <  ___

  Choose  delta = eps/4.  It is positive whenever eps is, and it
  depends on ___ alone -- which is what makes it a legal choice.

  Verification, forwards.  Suppose  0 < |x - 3| < delta.  Then

     |f(x) - 7|  =  4 |x - 3|
                 <  4 * delta
                 =  4 * (eps/4)
                 =  eps

  eps was arbitrary, so the limit is 7.                          []

  A number, to watch it work:  eps = 0.02 forces  delta = ___ ,
  and x = 3.004 lies inside that window:  f(3.004) = 7.016, whose
  distance from 7 is 0.016 -- under the 0.02 demanded.
""",
                "blanks": [
                    {
                        "prompt": "$|4x - 12|$, rewritten as a multiple of $|x-3|$. What is the constant?",
                        "hole": "?",
                        "opts": ["4", "12", "1/4", "3"],
                        "a": 0,
                        "why": "$4x - 12 = 4(x-3)$, and $|4(x-3)| = |4|\\,|x-3| = 4|x-3|$ because $4$ is "
                               "positive. Taking $12$ mistakes the constant term for the factor; taking "
                               "$1/4$ inverts it, which is the reciprocal that appears later in $\\delta$, "
                               "not here; and $3$ is the point being approached, not a coefficient.",
                    },
                    {
                        "prompt": "Divide $4|x-3| < \\epsilon$ through by the coefficient. What must $|x-3|$ be under?",
                        "hole": "?",
                        "opts": ["eps/4", "4 eps", "eps", "eps - 4"],
                        "a": 0,
                        "why": "Dividing an inequality between positive quantities by the positive number "
                               "$4$ preserves it, giving $|x-3| < \\epsilon/4$. Multiplying by $4$ instead "
                               "goes the wrong way and would let $x$ range four times too far; leaving "
                               "$\\epsilon$ alone ignores the slope entirely; and subtracting is not a "
                               "legal move on a product at all, besides going negative for small "
                               "$\\epsilon$ and so failing to be a $\\delta$.",
                    },
                    {
                        "prompt": "A $\\delta$ is only legal if it depends on which of these?",
                        "hole": "?",
                        "opts": ["eps", "x", "both eps and x", "f(x)"],
                        "a": 0,
                        "why": "The definition reads *for every $\\epsilon$ there exists a $\\delta$ such "
                               "that for all $x$*, so $\\delta$ is fixed before any $x$ is looked at and "
                               "one value of it must serve the entire window. A formula containing $x$ "
                               "gives a different window at every point, which is not a window; the same "
                               "objection rules out anything depending on $f(x)$. Depending on $\\epsilon$ "
                               "is not merely allowed, it is the whole point \u2014 a smaller tolerance is "
                               "what buys a narrower window.",
                    },
                    {
                        "prompt": "$\\epsilon = 0.02$. What is $\\delta = \\epsilon/4$?",
                        "hole": "?",
                        "opts": ["0.005", "0.08", "0.02", "0.0005"],
                        "a": 0,
                        "why": "$0.02/4 = 0.005$. Getting $0.08$ multiplies where the algebra divides; "
                               "$0.02$ forgets the slope, and at $x = 3.019$ \u2014 inside a window of that "
                               "width \u2014 the function reads $7.076$, missing the target by nearly four "
                               "times the tolerance; $0.0005$ divides by $40$ and would still be a valid "
                               "$\\delta$, just not the one this proof produces, since anything smaller "
                               "than a working $\\delta$ also works.",
                    },
                ],
            },
            "numeric": [
                {
                    "title": "A hole that factors out",
                    "minutes": 5,
                    "brief": r'''
The routine case, and the one to be fluent in before anything else: substitution gives
$0/0$, the numerator hides a factor of $(x-a)$, and cancelling it is legal because the
limit never visits $x = a$.
''',
                    "prompt": "What is $\\lim_{x\\to 2} f(x)$?",
                    "note": "A pure number, to three decimal places. Mind the sign.",
                    "figure": "The function is $f(x) = \\dfrac{x^{2}-5x+6}{x-2}$, defined for every real "
                              "$x$ except $x = 2$. At $x = 2$ the numerator and the denominator are both "
                              "zero, so the formula returns nothing there. Everywhere else it is an "
                              "ordinary quotient of polynomials.",
                    "given": [
                        {"label": "Numerator", "value": "$x^{2}-5x+6$"},
                        {"label": "Denominator", "value": "$x-2$"},
                        {"label": "Point of interest", "value": "$x = 2$"},
                    ],
                    "aside": "Two numbers that multiply to $+6$ and add to $-5$ are both negative.",
                    "answer": -1.0,
                    "tol": 0.005,
                    "unit": "",
                    "hint": "Factor the numerator, cancel, and then substitute into what is left.",
                    "wrong": "If you answered $0$, that is the numerator's value at $x=2$ being read as "
                             "the limit \u2014 but the denominator is zero there too, and $0/0$ is not $0$. "
                             "If you answered $+1$, one of the two factors lost its minus sign.",
                    "why": "$x^{2}-5x+6 = (x-2)(x-3)$, so for every $x \\neq 2$ the quotient equals "
                           "$x-3$. That reduced function is a polynomial, hence continuous, so its "
                           "limit at $2$ is its value there: $2 - 3 = -1$. The original function still "
                           "has no value at $2$; what the working found is the value that *would* fill "
                           "the hole. Sampling agrees \u2014 at $x = 1.999$ the quotient reads $-1.001$ and "
                           "at $x = 2.001$ it reads $-0.999$ \u2014 but sampling is evidence and the "
                           "cancellation is the proof.",
                },
                {
                    "title": "A hole that has to be rationalised first",
                    "minutes": 7,
                    "brief": r'''
Same $0/0$, but the factor of $x$ is hidden inside a difference of square roots and no
amount of staring will factor it out. One multiplication by the conjugate turns that
difference into a difference of squares, where the factor is in plain sight.
''',
                    "prompt": "What is $\\lim_{x\\to 0} g(x)$?",
                    "note": "A pure number, to four decimal places.",
                    "figure": "The function is $g(x) = \\dfrac{\\sqrt{9+x}-3}{x}$, defined for every "
                              "$x > -9$ except $x = 0$. At $x = 0$ the numerator is $\\sqrt{9}-3 = 0$ and "
                              "the denominator is $0$, so the formula returns nothing there.",
                    "given": [
                        {"label": "Numerator", "value": "$\\sqrt{9+x}-3$"},
                        {"label": "Denominator", "value": "$x$"},
                        {"label": "Point of interest", "value": "$x = 0$"},
                    ],
                    "aside": "The conjugate of $\\sqrt{9+x}-3$ is $\\sqrt{9+x}+3$, and it is close to $6$ "
                             "near $x = 0$, so multiplying by it over itself is legal.",
                    "answer": 0.16667,
                    "tol": 0.0005,
                    "unit": "",
                    "hint": "Multiply top and bottom by $\\sqrt{9+x}+3$, simplify the numerator, cancel "
                            "the $x$, then substitute.",
                    "wrong": "If you answered $0$, that is what a naive machine reports: evaluate the "
                             "original expression at $x = 10^{-18}$ in double precision and $9 + x$ "
                             "rounds to exactly $9$, so the numerator is exactly zero. The mathematics "
                             "is fine; the arithmetic threw the answer away.",
                    "why": "Multiplying by the conjugate gives numerator $(9+x) - 9 = x$, so the "
                           "quotient becomes $\\dfrac{x}{x\\left(\\sqrt{9+x}+3\\right)}$, and cancelling "
                           "the $x$ \u2014 legal on a punctured neighbourhood \u2014 leaves "
                           "$\\dfrac{1}{\\sqrt{9+x}+3}$. That expression is continuous at $0$, so the "
                           "limit is its value there, $\\dfrac{1}{3+3} = \\dfrac{1}{6} = 0.16667$. Notice "
                           "that the rationalised form is also the numerically safe one: it returns "
                           "$0.1666\\ldots$ at every step size, while the original starts drifting below "
                           "$x = 10^{-12}$ and collapses to zero below $10^{-16}$.",
                },
                {
                    "title": "The window a curve allows",
                    "minutes": 9,
                    "brief": r'''
The top of the ladder: the number asked for does not exist until you have derived it.
Nothing here can be evaluated directly, because the factor multiplying $|x-4|$ is not a
constant and has to be bounded before it can be used.

Use the standard recipe. Restrict $\delta$ to at most $1$ first, find what that
restriction forces on the nuisance factor, and take the minimum at the end.
''',
                    "prompt": "What $\\delta$ does the standard argument produce for this $\\epsilon$?",
                    "note": "A pure number, to three decimal places.",
                    "figure": "Prove that $\\lim_{x\\to 4} x^{2} = 16$. Follow the usual recipe: agree in "
                              "advance that $\\delta$ will never exceed $1$; use that restriction to "
                              "bound $|x+4|$ by a constant; then take $\\delta$ to be the smaller of $1$ "
                              "and whatever the $\\epsilon$ condition demands. The tolerance offered is "
                              "$\\epsilon = 0.36$.",
                    "given": [
                        {"label": "Function and point", "value": "$f(x) = x^{2}$, $a = 4$, $L = 16$"},
                        {"label": "Tolerance offered", "value": "$\\epsilon = 0.36$"},
                        {"label": "Standing restriction", "value": "$\\delta \\le 1$"},
                    ],
                    "aside": "$|x^{2}-16| = |x-4|\\,|x+4|$, and $|x-4| < 1$ pins $x$ between $3$ and $5$.",
                    "answer": 0.04,
                    "tol": 0.0005,
                    "unit": "",
                    "hint": "With $|x-4| < 1$ you get $3 < x < 5$, hence $7 < x+4 < 9$. Use the upper "
                            "bound, then divide $\\epsilon$ by it.",
                    "wrong": "If you answered $0.36$, the factor $|x+4|$ was dropped \u2014 that is the "
                             "answer for a line of slope $1$, and $x^{2}$ near $4$ is roughly eight times "
                             "steeper than that. If you answered $0.045$, the bound used was $8$ (the "
                             "value of $x+4$ at the centre) rather than $9$ (its supremum over the "
                             "window), and a bound has to hold across the whole window, not at its "
                             "midpoint.",
                    "why": "$|x^{2}-16| = |x-4|\\,|x+4|$. The restriction $\\delta \\le 1$ gives "
                           "$|x-4| < 1$, hence $3 < x < 5$ and $7 < x+4 < 9$, so $|x+4| < 9$ throughout "
                           "the window. Then $|x^{2}-16| < 9\\,|x-4|$, and forcing that under "
                           "$\\epsilon = 0.36$ needs $|x-4| < 0.36/9 = 0.04$. Since $0.04 < 1$, the "
                           "minimum of the two restrictions is $\\delta = 0.04$. Check it at the worse "
                           "edge: $4.04^{2} = 16.3216$, an error of $0.3216$, inside the $0.36$ "
                           "demanded. The $\\delta$ is sufficient rather than largest \u2014 the exact "
                           "largest is $\\sqrt{16.36}-4 \\approx 0.0448$ \u2014 and the definition asks "
                           "only for one that works.",
                },
            ],
            "quiz": {
                "title": "What a limit asserts, and what it does not",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The statement $\\lim_{x\\to a} f(x) = L$ is a claim about:",
                        "opts": [
                            "the values of $f$ at points near $a$, never at $a$ itself",
                            "the value $f(a)$",
                            "the value $f(a)$ together with the values around it",
                            "the values of $f$ across its whole domain",
                        ],
                        "a": 0,
                        "why": r'''
The definition quantifies over $x$ satisfying $0 < |x-a| < \delta$, and the strict
$0 <$ on the left is the puncture: $x = a$ is excluded by construction. That exclusion
is not a technicality — it is what allows an expression that reads $0/0$ at $a$ to have
a limit there, which is the entire reason the notion exists, since every derivative in
this course has that shape. The value $f(a)$ may be undefined, or equal to $L$, or
equal to something unrelated, and the limit is unchanged in all three cases. Nor is it
a global claim: what happens far from $a$ is irrelevant.
''',
                    },
                    {
                        "q": "For $f(x) = \\dfrac{|x-2|}{x-2}$, what is $\\lim_{x\\to 2} f(x)$?",
                        "opts": ["$1$", "$-1$", "$0$", "It does not exist"],
                        "a": 3,
                        "why": r'''
For $x > 2$ the quantity $x-2$ is positive so $f(x) = +1$; for $x < 2$ it is negative
so $f(x) = -1$. The one-sided limits are $+1$ and $-1$, they disagree, and a two-sided
limit exists only when both one-sided limits exist and are equal. Answering $+1$ or
$-1$ takes one side for the whole story. Answering $0$ averages them, which the
definition never licenses: every punctured neighbourhood of $2$ contains points at
distance $1$ from $0$, so a tolerance of $0.5$ around $0$ can never be met.
''',
                    },
                    {
                        "q": "Which ordering of the quantifiers is the definition of a limit?",
                        "opts": [
                            "for every $\\epsilon>0$ there exists $\\delta>0$ such that $0<|x-a|<\\delta$ implies $|f(x)-L|<\\epsilon$",
                            "for every $\\delta>0$ there exists $\\epsilon>0$ such that $0<|x-a|<\\delta$ implies $|f(x)-L|<\\epsilon$",
                            "there exists $\\epsilon>0$ such that for every $\\delta>0$, $0<|x-a|<\\delta$ implies $|f(x)-L|<\\epsilon$",
                            "there exists $\\delta>0$ such that for every $\\epsilon>0$, $0<|x-a|<\\delta$ implies $|f(x)-L|<\\epsilon$",
                        ],
                        "a": 0,
                        "why": r'''
The tolerance is the challenge and the window is the reply, so $\epsilon$ is
quantified first and $\delta$ may depend on it. Leading with $\delta$ instead makes the
tolerance depend on the window, which is satisfied by any bounded function and asserts
nothing. Fixing a single $\delta$ that works for *every* $\epsilon$ is far stronger
than intended: it forces $f$ to equal $L$ identically on a punctured neighbourhood of
$a$. And beginning with "there exists $\epsilon$" asks only that some one tolerance be
met, which is not a statement about closing in on anything.
''',
                    },
                    {
                        "q": "$f(x) = \\dfrac{x^{2}-9}{x-3}$ for $x \\neq 3$, and $f(3) = 0$. At $x=3$:",
                        "opts": [
                            "$f$ is continuous, because it has a value there",
                            "the limit is $6$, but $f$ is not continuous at $3$",
                            "the limit does not exist, because the denominator vanishes",
                            "the limit is $0$, because that is the value assigned",
                        ],
                        "a": 1,
                        "why": r'''
For $x \neq 3$ the quotient equals $x+3$, so the limit at $3$ is $6$. The function is
defined at $3$, with value $0$. Continuity needs the limit and the value to agree, and
$6 \neq 0$, so this is a removable discontinuity that has been repaired with the wrong
number. Having a value at the point is only one of the three conditions. And a
vanishing denominator does not by itself destroy a limit — it destroys it only when the
numerator fails to vanish with it, which here it does not.
''',
                    },
                    {
                        "q": "Sampling $f(x)=\\sin(\\pi/x)$ at $x = 1, \\tfrac12, \\tfrac13, \\ldots, \\tfrac1n$ returns exactly $0$ every time. This shows:",
                        "opts": [
                            "$\\lim_{x\\to 0} f(x) = 0$",
                            "$f$ is continuous at $0$",
                            "nothing about the limit: those samples were taken where $f$ vanishes, and $f$ reaches $\\pm 1$ between them",
                            "the limit fails to exist because $0$ is outside the domain",
                        ],
                        "a": 2,
                        "why": r'''
At $x = 1/n$ the argument is $n\pi$ and $\sin(n\pi) = 0$ for every integer $n$, so the
table is a list of exact zeros — and it is exactly what a function tending to zero
would produce. But between consecutive samples, at $x = 2/(2k+1)$, the function reads
$\pm 1$, and every punctured neighbourhood of $0$ contains infinitely many of both. No
limit exists. A finite table can never distinguish "tends to $L$" from "passes through
$L$ at the points I sampled", which is why the $\epsilon$-$\delta$ definition is
needed. Note also that being outside the domain is not itself a reason for a limit to
fail: $(x^{2}-1)/(x-1)$ is undefined at $1$ and has a perfectly good limit there.
''',
                    },
                    {
                        "q": "In double precision, $g(x) = \\dfrac{\\sqrt{1+x}-1}{x}$ evaluated at $x = 10^{-16}$ returns exactly $0$. Why?",
                        "opts": [
                            "the true limit is $0$",
                            "$1+x$ rounds to exactly $1$, so the numerator is exactly zero — cancellation, not mathematics",
                            "$x$ underflows to zero, so the division is $0/0$",
                            "the square root is inaccurate near $1$",
                        ],
                        "a": 1,
                        "why": r'''
A double holds about $16$ significant decimal digits, so $1 + 10^{-16}$ is not
representable as anything other than $1.0$. Then $\sqrt{1+x}$ is exactly $1$, the
numerator is exactly $0$, and $0/10^{-16} = 0$. The true limit is $\tfrac12$, by the
conjugate argument. Underflow is not involved: $10^{-16}$ is an entirely ordinary
double, far above the underflow threshold near $10^{-308}$, and it is the *addition*
that loses it, not the storage. The square root itself is accurate to within a rounding
step — it faithfully returns the root of the number it was handed, which is $1$.
Rationalising to $1/(\sqrt{1+x}+1)$ removes the subtraction and returns $0.5$ at every
step size.
''',
                    },
                    {
                        "q": "What does $\\lim_{x\\to 0} \\dfrac{1}{x^{2}} = \\infty$ mean?",
                        "opts": [
                            "the limit exists, and its value is the number $\\infty$",
                            "the limit does not exist; the notation records how it fails, the values exceeding every bound",
                            "the limit is undefined and nothing further can be said",
                            "$1/x^{2}$ is continuous at $0$ with value $\\infty$",
                        ],
                        "a": 1,
                        "why": r'''
There is no real number $\infty$, so it cannot be an $L$: substituting it into
$|f(x)-L| < \epsilon$ is meaningless. The notation is shorthand for a separate
definition — for every $M$ there is a $\delta$ such that $0 < |x| < \delta$ forces
$f(x) > M$ — which is a statement about escaping every bound rather than approaching a
value. It is more informative than "no limit": compare $\sin(\pi/x)$, which also has
no limit at $0$ but stays inside $[-1,1]$ forever. And continuity is out of the
question, since the function is not even defined at $0$.
''',
                    },
                ],
            },
            "lab": {
                "title": "Numerical limits and an epsilon-delta witness",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Three functions that turn the definition of a limit into something executable.

## `limit_table(f, a, hs)`

For each step `h` in `hs`, record the pair of values either side of `a`.
Return a list of triples `(h, f(a - h), f(a + h))`, in the order `hs` gives.
Raise `ValueError` if any `h` is zero or negative — a step must shrink towards
`a` from somewhere.

```text
limit_table(lambda x: x * x, 3, [0.1]) -> [(0.1, 8.41, 9.61)]
```

## `estimate_limit(f, a, tol=1e-4, hs=HS)`

Take the **smallest** step in `hs`, evaluate `left = f(a - h)` and
`right = f(a + h)`, and then decide:

- if calling `f` raises `ArithmeticError` or `ValueError`, return `None`
- if either value is not finite, or exceeds `HUGE` in magnitude, return `None`
- if `abs(left - right) > tol * max(1.0, abs(left), abs(right))`, return `None`
- otherwise return `(left + right) / 2`

The third rule is *relative*: a steep but continuous function has a genuinely
large gap between the two sides, and must not be mistaken for a jump.

```text
estimate_limit(lambda x: math.sin(x) / x, 0.0)  ->  0.9999999999998333
estimate_limit(lambda x: abs(x) / x, 0.0)       ->  None
estimate_limit(lambda x: 1 / (x * x), 0.0)      ->  None
```

## `delta_for(f, a, L, eps, deltas)`

The witness checker. Return the **largest** `delta` in `deltas` for which every
sampled point of the punctured interval satisfies `abs(f(x) - L) < eps`, or
`None` when no candidate works. `deltas` may arrive in any order.

Sample `x = a + delta * k / SAMPLES` and `x = a - delta * k / SAMPLES` for
`k = 1 .. SAMPLES`; `k` never reaches 0, so `a` itself is never evaluated.
Raise `ValueError` when `eps` is zero or negative.
''',
                "files": [{"name": "main.py", "content": r'''
import math

HS = (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6)
HUGE = 1e8
SAMPLES = 50


def limit_table(f, a, hs):
    """[(h, f(a - h), f(a + h)) for h in hs]. ValueError if any h <= 0."""
    # your code here


def estimate_limit(f, a, tol=1e-4, hs=HS):
    """Two-sided estimate at the smallest step, or None when no limit is seen."""
    # your code here


def delta_for(f, a, L, eps, deltas):
    """Largest delta in deltas that witnesses the eps claim, else None."""
    # your code here


print(estimate_limit(lambda x: math.sin(x) / x, 0.0))
print(delta_for(lambda x: 3 * x + 1, 2.0, 7.0, 0.1, [1.0, 0.5, 0.05, 0.01]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

HS = (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6)
HUGE = 1e8
SAMPLES = 50


def limit_table(f, a, hs):
    """[(h, f(a - h), f(a + h)) for h in hs]. ValueError if any h <= 0."""
    rows = []
    for h in hs:
        if h <= 0:
            raise ValueError("every step h must be strictly positive")
        rows.append((h, f(a - h), f(a + h)))
    return rows


def estimate_limit(f, a, tol=1e-4, hs=HS):
    """Two-sided estimate at the smallest step, or None when no limit is seen."""
    h = min(hs)
    try:
        left = f(a - h)
        right = f(a + h)
    except (ArithmeticError, ValueError):
        # f is not even defined on one side of a, so nothing two-sided exists.
        return None
    if not (math.isfinite(left) and math.isfinite(right)):
        return None
    if abs(left) > HUGE or abs(right) > HUGE:
        return None
    # Relative gap: a steep continuous function must not read as a jump.
    scale = max(1.0, abs(left), abs(right))
    if abs(left - right) > tol * scale:
        return None
    return (left + right) / 2


def delta_for(f, a, L, eps, deltas):
    """Largest delta in deltas that witnesses the eps claim, else None."""
    if eps <= 0:
        raise ValueError("eps must be strictly positive")
    for delta in sorted(deltas, reverse=True):
        ok = True
        for k in range(1, SAMPLES + 1):
            offset = delta * k / SAMPLES
            for x in (a - offset, a + offset):
                if abs(f(x) - L) >= eps:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return delta
    return None


print(estimate_limit(lambda x: math.sin(x) / x, 0.0))
print(delta_for(lambda x: 3 * x + 1, 2.0, 7.0, 0.1, [1.0, 0.5, 0.05, 0.01]))
'''}],
                "hints": [
                    "Validate before you compute: loop over `hs` once, raise on the first bad step.",
                    "`min(hs)` picks the smallest step; the table order does not matter for the estimate.",
                    "`math.isfinite(v)` is False for both `inf` and `nan`, which is exactly the blow-up test.",
                    "`sorted(deltas, reverse=True)` gives you the candidates largest-first, so the first success is the answer.",
                ],
                "tests": [
                    {"name": "limit_table records both sides", "code": r'''
_rows = limit_table(lambda x: x * x, 3, [0.1, 0.01])
assert len(_rows) == 2, f"limit_table gave {len(_rows)} rows, expected 2"
assert abs(_rows[0][0] - 0.1) < 1e-12, f"first row step is {_rows[0][0]!r}, expected 0.1"
assert abs(_rows[0][1] - 8.41) < 1e-9, f"f(a-h) is {_rows[0][1]!r}, expected 8.41"
assert abs(_rows[0][2] - 9.61) < 1e-9, f"f(a+h) is {_rows[0][2]!r}, expected 9.61"
assert abs(_rows[1][1] - 8.9401) < 1e-9, f"second row f(a-h) is {_rows[1][1]!r}"
'''},
                    {"name": "limit_table refuses a non-positive step", "code": r'''
for _bad in ([0.1, 0.0], [-0.5], [0.0]):
    try:
        limit_table(lambda x: x, 1.0, _bad)
        assert False, f"limit_table with hs={_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "estimate_limit finds removable and ordinary limits", "code": r'''
import math as _math
_got = estimate_limit(lambda x: _math.sin(x) / x, 0.0)
assert _got is not None and abs(_got - 1.0) < 1e-9, f"sin(x)/x at 0 gave {_got!r}, expected ~1"
_got = estimate_limit(lambda x: (x * x - 1) / (x - 1), 1.0)
assert _got is not None and abs(_got - 2.0) < 1e-5, f"(x^2-1)/(x-1) at 1 gave {_got!r}, expected ~2"
_got = estimate_limit(lambda x: x * x + 3 * x, 2.0)
assert _got is not None and abs(_got - 10.0) < 1e-6, f"x^2+3x at 2 gave {_got!r}, expected ~10"
'''},
                    {"name": "A steep continuous function still has a limit", "code": r'''
_got = estimate_limit(lambda x: 1000.0 * x, 1.0)
assert _got is not None, "1000x is continuous — the gap test must be relative, not absolute"
assert abs(_got - 1000.0) < 1e-6, f"1000x at 1 gave {_got!r}, expected ~1000"
'''},
                    {"name": "estimate_limit rejects jumps, blow-ups and undefined sides", "code": r'''
import math as _math
assert estimate_limit(lambda x: abs(x) / x, 0.0) is None, "|x|/x jumps at 0 — expected None"
assert estimate_limit(lambda x: 1.0 / x, 0.0) is None, "1/x is unbounded at 0 — expected None"
assert estimate_limit(lambda x: 1.0 / (x * x), 0.0) is None, "1/x^2 blows up at 0 — expected None"
assert estimate_limit(_math.log, 0.0) is None, "log is undefined left of 0 — expected None"
'''},
                    {"name": "delta_for returns the largest witness", "code": r'''
_f = lambda x: 3 * x + 1
assert delta_for(_f, 2.0, 7.0, 0.1, [0.01, 1.0, 0.05, 0.5]) == 0.01, \
    f"Got {delta_for(_f, 2.0, 7.0, 0.1, [0.01, 1.0, 0.05, 0.5])!r}, expected 0.01"
assert delta_for(_f, 2.0, 7.0, 10.0, [0.01, 1.0, 0.05, 0.5]) == 1.0, \
    "With eps=10 even delta=1 works, and it is the largest candidate"
_g = lambda x: (x * x - 1) / (x - 1)
assert delta_for(_g, 1.0, 2.0, 0.01, [0.1, 0.02, 0.005]) == 0.005, \
    "The punctured neighbourhood must never evaluate f at a itself"
'''},
                    {"name": "delta_for gives up, and refuses a non-positive eps", "code": r'''
_f = lambda x: 3 * x + 1
assert delta_for(_f, 2.0, 7.0, 1e-9, [0.01, 1.0, 0.05]) is None, \
    "No candidate delta is small enough, so the answer is None"
assert delta_for(_f, 2.0, 7.0, 1.0, []) is None, "No candidates at all means None"
for _bad in (0.0, -1.0):
    try:
        delta_for(_f, 2.0, 7.0, _bad, [1.0])
        assert False, f"eps={_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Limit laws, asymptotes and the intermediate value theorem",
            "summary": "Evaluating a limit on paper instead of sampling it, and the two theorems continuity pays for.",
            "concepts": [
                "The limit laws: sums, products and quotients pass through a limit, provided every piece has one and no denominator tends to zero",
                "`0/0` and `inf/inf` are questions, not answers — factor and cancel, or rationalise the conjugate, before substituting",
                "The squeeze theorem reaches limits the laws cannot: `-|x| <= x*sin(1/x) <= |x|` forces the middle to `0`",
                "Limits at infinity: divide by the dominant power to read off a horizontal asymptote; a vertical asymptote is a one-sided infinite limit",
                "The intermediate value theorem turns a sign change into a guaranteed root, which is the licence bisection runs on",
            ],
            "quiz": {
                "title": "Evaluating a limit without sampling it",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is `lim x->3 of (x*x - 9)/(x - 3)`?",
                        "opts": [
                            "`0`, because substituting `x = 3` gives `0/0`",
                            "`6`",
                            "It does not exist, because the function is undefined at `x = 3`",
                            "`3`",
                        ],
                        "a": 1,
                        "why": r"""
Factor the numerator first: `(x - 3)(x + 3)/(x - 3)` is `x + 3` at every point except
`x = 3` itself, and a limit only ever looks at the punctured neighbourhood, so the
value is `3 + 3 = 6`. Substituting before cancelling gives `0/0`, which is not the
number zero — it is the signal that the quotient law does not apply yet and that some
algebra is owed. Being undefined at the point is no obstacle either: `sin(x)/x` is
undefined at `0` and still has the limit `1`, which is the whole reason the definition
punctures the neighbourhood.
""",
                    },
                    {
                        "q": "The quotient law `lim f/g = (lim f)/(lim g)` carries one condition. Which?",
                        "opts": [
                            "`lim g` is not zero",
                            "`f` and `g` are both continuous at the point",
                            "`g` is nowhere zero on the whole interval",
                            "`lim f` is not zero",
                        ],
                        "a": 0,
                        "why": r"""
Only the denominator's limit matters, and it must be non-zero — that alone keeps `g`
away from zero close enough to the point for the quotient to make sense. Continuity is
not required, because a limit ignores the value at the point: both `f` and `g` may be
undefined there. `g` is allowed to vanish elsewhere on the interval, far from the point
being approached. And a numerator limit of zero is perfectly fine: it simply makes the
quotient's limit zero, which is a determinate answer rather than the `0/0` form.
""",
                    },
                    {
                        "q": "What is `lim x->inf of (3*x*x - x)/(2*x*x + 5)`?",
                        "opts": [
                            "`+inf`, because the numerator grows without bound",
                            "`-1/5`, from the terms left over when the squares cancel",
                            "`1.5`",
                            "`0`",
                        ],
                        "a": 2,
                        "why": r"""
Divide top and bottom by the dominant power `x*x`: the quotient becomes
`(3 - 1/x)/(2 + 5/x*x)`, and both small terms vanish, leaving `3/2`. Both halves do grow
without bound, which is exactly why the form `inf/inf` decides nothing on its own — the
race is settled by the leading coefficients. The lower-order terms do not survive as a
ratio of their own; they are the parts that die. A limit of `0` would need the
denominator to carry the higher degree.
""",
                    },
                    {
                        "q": "Why does the product law fail to give `lim x->0 of x*sin(1/x)`, and what is the limit?",
                        "opts": [
                            "It does not fail: one factor tends to `0`, so the product does too",
                            "`sin(1/x)` has no limit at `0`, so the law says nothing; the squeeze `-|x| <= x*sin(1/x) <= |x|` gives `0`",
                            "`sin(1/x)` has no limit at `0`, so the product has none either",
                            "The limit is `1`, by the standard `sin(t)/t` result",
                        ],
                        "a": 1,
                        "why": r"""
The product law needs each factor to have a limit of its own, and `sin(1/x)` takes every
value in `[-1, 1]` arbitrarily close to the origin, so it has none. The law being silent
is not the same as the limit failing to exist: bound the product instead. Since
`|sin(1/x)| <= 1`, the whole expression is trapped between `-|x|` and `|x|`, and both
bounds go to `0`, so the middle has nowhere else to go. The `sin(t)/t` result is about a
different expression — here the reciprocal is inside the sine, not dividing it.
""",
                    },
                    {
                        "q": "`f` is continuous on `[1, 2]` with `f(1) = -3` and `f(2) = 5`. What does the intermediate value theorem guarantee?",
                        "opts": [
                            "`f` is increasing on `[1, 2]`",
                            "`f` has exactly one zero in `(1, 2)`",
                            "`f(c) = 0` for at least one `c` in `(1, 2)`",
                            "`f'(c) = 8` for some `c` in `(1, 2)`",
                        ],
                        "a": 2,
                        "why": r"""
A continuous function takes every value between its endpoint values, and `0` lies
between `-3` and `5`, so at least one root exists. The theorem counts nothing: a
continuous function can cross zero three times on the way, so uniqueness is a separate
claim needing a separate argument, usually monotonicity. Nor does it force `f` to rise
steadily — it may wander as long as it does not tear. The claim about an interior slope
is the mean value theorem, which needs differentiability rather than mere continuity.
This existence guarantee is precisely what makes bisection legitimate: a sign change
across a bracket means the root is genuinely inside it.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "The derivative as a limit",
            "summary": "Difference quotients, their truncation error, and the order that error obeys.",
            "concepts": [
                "The derivative is the limit of a difference quotient, not a formula to memorise",
                "Forward difference: f'(x) = (f(x+h) - f(x))/h + O(h)",
                "Central difference: f'(x) = (f(x+h) - f(x-h))/(2h) + O(h^2)",
                "Taylor expansion is where both error terms come from",
                "Observed order p from a pair of steps: p = log(e1/e2) / log(h1/h2)",
                "Richardson extrapolation cancels the leading error term and buys two orders",
                "Roundoff sets a floor: shrinking h forever makes the answer worse",
            ],
            "lab": {
                "title": "Finite differences and their error order",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Four functions. The last two measure how fast the first two converge.

## `forward_diff(f, x, h)` and `central_diff(f, x, h)`

The two standard quotients. Both raise `ValueError` when `h <= 0`.

```text
f(x) = x*x + 3x,  x = 2,  h = 0.5
forward_diff -> 7.5     central_diff -> 7.0     exact f'(2) = 7
```

Central difference is exact for any quadratic; forward difference is off by
roughly `f''(x) * h / 2`. That is the whole point of the module.

## `richardson(f, x, h)`

Combine two central differences to cancel the `h^2` term:

```text
richardson(f, x, h) = (4 * central_diff(f, x, h/2) - central_diff(f, x, h)) / 3
```

The remaining error is `O(h^4)`.

## `errors_for(rule, f, x, exact, hs)` and `error_order(errors, hs)`

`errors_for` returns `[abs(rule(f, x, h) - exact) for h in hs]`.

`error_order` turns that list into a single observed order: the **mean** of

```text
log(e_i / e_{i+1}) / log(h_i / h_{i+1})
```

over every consecutive pair. Raise `ValueError` if the two lists differ in
length, hold fewer than two points, contain an error that is not strictly
positive, or contain two equal steps.

With `hs = (0.4, 0.2, 0.1, 0.05)` and `f = sin` at `x = 1` you should observe
about `1.03` for forward, `2.00` for central and `4.00` for Richardson.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def forward_diff(f, x, h):
    """(f(x+h) - f(x)) / h. ValueError when h <= 0."""
    # your code here


def central_diff(f, x, h):
    """(f(x+h) - f(x-h)) / (2h). ValueError when h <= 0."""
    # your code here


def richardson(f, x, h):
    """(4 * central_diff(f, x, h/2) - central_diff(f, x, h)) / 3."""
    # your code here


def errors_for(rule, f, x, exact, hs):
    """Absolute error of rule at each step in hs."""
    # your code here


def error_order(errors, hs):
    """Mean observed convergence order over consecutive (h, error) pairs."""
    # your code here


HS = (0.4, 0.2, 0.1, 0.05)
for name, rule in [("forward", forward_diff), ("central", central_diff),
                   ("richardson", richardson)]:
    errs = errors_for(rule, math.sin, 1.0, math.cos(1.0), HS)
    print(name, round(error_order(errs, HS), 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def forward_diff(f, x, h):
    """(f(x+h) - f(x)) / h. ValueError when h <= 0."""
    if h <= 0:
        raise ValueError("h must be strictly positive")
    return (f(x + h) - f(x)) / h


def central_diff(f, x, h):
    """(f(x+h) - f(x-h)) / (2h). ValueError when h <= 0."""
    if h <= 0:
        raise ValueError("h must be strictly positive")
    return (f(x + h) - f(x - h)) / (2 * h)


def richardson(f, x, h):
    """(4 * central_diff(f, x, h/2) - central_diff(f, x, h)) / 3."""
    # The h^2 terms of the two central differences cancel exactly, leaving O(h^4).
    return (4 * central_diff(f, x, h / 2) - central_diff(f, x, h)) / 3


def errors_for(rule, f, x, exact, hs):
    """Absolute error of rule at each step in hs."""
    return [abs(rule(f, x, h) - exact) for h in hs]


def error_order(errors, hs):
    """Mean observed convergence order over consecutive (h, error) pairs."""
    errors = list(errors)
    hs = list(hs)
    if len(errors) != len(hs):
        raise ValueError("errors and hs must have the same length")
    if len(hs) < 2:
        raise ValueError("need at least two points to observe an order")
    if any(e <= 0 for e in errors):
        raise ValueError("an error of zero has no order — the rule is exact here")
    if any(h <= 0 for h in hs):
        raise ValueError("every step h must be strictly positive")
    orders = []
    for i in range(len(hs) - 1):
        if hs[i] == hs[i + 1]:
            raise ValueError("two equal steps give no information")
        orders.append(math.log(errors[i] / errors[i + 1])
                      / math.log(hs[i] / hs[i + 1]))
    return sum(orders) / len(orders)


HS = (0.4, 0.2, 0.1, 0.05)
for name, rule in [("forward", forward_diff), ("central", central_diff),
                   ("richardson", richardson)]:
    errs = errors_for(rule, math.sin, 1.0, math.cos(1.0), HS)
    print(name, round(error_order(errs, HS), 3))
'''}],
                "hints": [
                    "Guard `h` first in both quotients, then return the one-line expression.",
                    "`richardson` must call `central_diff`, not re-derive it: `(4 * central_diff(f, x, h/2) - central_diff(f, x, h)) / 3`.",
                    "`errors_for` is a single list comprehension over `hs`.",
                    "Do every validation in `error_order` before the loop, so a bad input never reaches `math.log`.",
                ],
                "tests": [
                    {"name": "Both quotients on a quadratic", "code": r'''
_f = lambda x: x * x + 3 * x
assert abs(forward_diff(_f, 2.0, 0.5) - 7.5) < 1e-12, \
    f"forward_diff gave {forward_diff(_f, 2.0, 0.5)!r}, expected 7.5"
assert abs(central_diff(_f, 2.0, 0.5) - 7.0) < 1e-12, \
    f"central_diff gave {central_diff(_f, 2.0, 0.5)!r}, expected 7.0 exactly"
assert abs(central_diff(_f, 2.0, 1e-3) - 7.0) < 1e-9, \
    "central difference is exact for quadratics at every step size"
'''},
                    {"name": "Both quotients refuse a non-positive step", "code": r'''
for _rule in (forward_diff, central_diff):
    for _bad in (0.0, -0.1):
        try:
            _rule(lambda x: x, 1.0, _bad)
            assert False, f"{_rule.__name__} with h={_bad!r} should raise ValueError"
        except ValueError:
            pass
'''},
                    {"name": "richardson is far sharper than central", "code": r'''
import math as _math
_exact = _math.cos(1.0)
_c = abs(central_diff(_math.sin, 1.0, 0.1) - _exact)
_r = abs(richardson(_math.sin, 1.0, 0.1) - _exact)
assert _r < _c / 1000, f"richardson error {_r!r} should be far below central error {_c!r}"
assert _r < 1e-6, f"richardson error at h=0.1 is {_r!r}, expected below 1e-6"
'''},
                    {"name": "errors_for lines the errors up with the steps", "code": r'''
import math as _math
_hs = (0.4, 0.2, 0.1, 0.05)
_e = errors_for(central_diff, _math.sin, 1.0, _math.cos(1.0), _hs)
assert len(_e) == 4, f"errors_for gave {len(_e)} entries, expected 4"
assert all(_e[i] > _e[i + 1] for i in range(3)), f"Errors should shrink with h: {_e!r}"
assert abs(_e[0] - 0.0142932) < 1e-4, f"error at h=0.4 is {_e[0]!r}, expected about 0.014293"
'''},
                    {"name": "Observed orders match the theory", "code": r'''
import math as _math
_hs = (0.4, 0.2, 0.1, 0.05)
_p = error_order(errors_for(forward_diff, _math.sin, 1.0, _math.cos(1.0), _hs), _hs)
assert abs(_p - 1.0) < 0.1, f"forward difference observed order {_p!r}, expected about 1"
_p = error_order(errors_for(central_diff, _math.sin, 1.0, _math.cos(1.0), _hs), _hs)
assert abs(_p - 2.0) < 0.05, f"central difference observed order {_p!r}, expected about 2"
_p = error_order(errors_for(richardson, _math.sin, 1.0, _math.cos(1.0), _hs), _hs)
assert abs(_p - 4.0) < 0.1, f"richardson observed order {_p!r}, expected about 4"
'''},
                    {"name": "error_order on a clean synthetic sequence", "code": r'''
_hs = [0.1, 0.05, 0.025]
_errs = [3.0 * h ** 2 for h in _hs]
assert abs(error_order(_errs, _hs) - 2.0) < 1e-9, \
    f"A pure h^2 sequence must read exactly 2, got {error_order(_errs, _hs)!r}"
'''},
                    {"name": "error_order rejects unusable input", "code": r'''
for _errs, _hs in [([1.0], [0.1]),
                   ([1.0, 0.5], [0.1]),
                   ([1.0, 0.0], [0.1, 0.05]),
                   ([1.0, -0.5], [0.1, 0.05]),
                   ([1.0, 0.5], [0.1, 0.1]),
                   ([1.0, 0.5], [0.1, 0.0])]:
    try:
        error_order(_errs, _hs)
        assert False, f"error_order({_errs!r}, {_hs!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Differentiation rules: power, product and quotient",
            "summary": "The rules that retire the difference quotient, and the derivation standing behind each one.",
            "concepts": [
                "The derivative is a function in its own right, so it can be differentiated again: `f'`, `f''`, written `dy/dx` and `d2y/dx2` in the other notation",
                "Linearity plus the power rule `d/dx x^n = n*x^(n-1)`, which falls straight out of the binomial expansion of `(x + h)^n`",
                "The product rule `(f*g)' = f'*g + f*g'`; the tempting `f'*g'` fails on the first example anyone tries",
                "The quotient rule `(f/g)' = (f'*g - f*g')/(g*g)`, where the order in the numerator is the entire sign",
                "Differentiability implies continuity, but not the reverse: `|x|` is continuous at `0` and has a corner there",
            ],
            "quiz": {
                "title": "The three rules, and what they are not",
                "minutes": 8,
                "questions": [
                    {
                        "q": "For `f(x) = (x^3)*(x^2)`, what does the product rule give, and does it agree with the power rule on `x^5`?",
                        "opts": [
                            "`6*x^3` from the product rule; the power rule disagrees and the product rule wins",
                            "`5*x^4` from both",
                            "`6*x^4` from both",
                            "`5*x^4` from the power rule but `6*x^3` from the product rule; the two rules genuinely disagree",
                        ],
                        "a": 1,
                        "why": r"""
The product rule gives `3*x^2 * x^2 + x^3 * 2*x`, which is `3*x^4 + 2*x^4 = 5*x^4`, and
the power rule on `x^5` gives `5*x^4` as well. Multiplying the derivatives together
instead gives `3*x^2 * 2*x = 6*x^3`, which is not even the right degree — the cheapest
demonstration that the derivative of a product is not the product of the derivatives.
Two correct rules never disagree; when they seem to, the arithmetic is wrong, and this
particular product is the standard place to check yourself.
""",
                    },
                    {
                        "q": "For `f(x) = (x*x + 1)/x` with `x` non-zero, what is `f'(x)`?",
                        "opts": [
                            "`2*x`",
                            "`1 + 1/(x*x)`",
                            "`1 - 1/(x*x)`",
                            "`(x*x + 1)/(x*x)`",
                        ],
                        "a": 2,
                        "why": r"""
The quotient rule gives `(2*x * x - (x*x + 1) * 1)/(x*x)`, which simplifies to
`(x*x - 1)/(x*x) = 1 - 1/(x*x)`. Split the fraction first and you get the same thing
with no rule at all: `f(x) = x + 1/x`, so `f'(x) = 1 - 1/(x*x)`. Reversing the order of
the numerator flips that minus to a plus, which is the single most common slip in the
rule. Differentiating the numerator alone gives `2*x` and quietly pretends the
denominator is a constant.
""",
                    },
                    {
                        "q": "For `x > 0`, what is `d/dx sqrt(x)`?",
                        "opts": [
                            "`1/(2*sqrt(x))`",
                            "`(1/2)*sqrt(x)`",
                            "`1/sqrt(x)`",
                            "`2*sqrt(x)`",
                        ],
                        "a": 0,
                        "why": r"""
The power rule works for any real exponent, so with `n = 1/2` the derivative is
`(1/2)*x^(-1/2)`, i.e. `1/(2*sqrt(x))`. The exponent drops by one; it does not stay put,
which is what `(1/2)*sqrt(x)` assumes. Two checks confirm the shape: `sqrt` is
increasing and flattening, so the derivative must be positive and shrinking, and the
tangent goes vertical as `x` approaches `0`, which is why the expression grows without
bound there. Dropping the `2` costs a factor of two everywhere.
""",
                    },
                    {
                        "q": "At `x = 2`, the function `f(x) = |x - 2|` is:",
                        "opts": [
                            "differentiable but not continuous",
                            "neither continuous nor differentiable",
                            "continuous and differentiable, with `f'(2) = 0`",
                            "continuous but not differentiable",
                        ],
                        "a": 3,
                        "why": r"""
The difference quotient approaches `-1` from the left and `+1` from the right, so the
two-sided limit does not exist and there is no derivative — while the graph itself has
no gap, so continuity holds. That is the one-way implication in this module:
differentiable forces continuous, and continuity buys nothing back. The claim of a zero
derivative is worth knowing as a trap, because it is exactly what an unguarded central
difference reports: it averages the two sides and hides the corner completely, which is
why numerical evidence needs a continuity argument standing behind it.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "The chain rule and the derivative of an inverse",
            "summary": "Differentiating a composition one layer at a time, and reading a slope backwards through an inverse.",
            "concepts": [
                "A composition differentiates outside-in: `(f(g(x)))' = f'(g(x)) * g'(x)`, and the inner factor is the part that gets dropped",
                "Leibniz form `dy/dx = (dy/du)*(du/dx)`: it looks like cancellation, but it is the limit of a product of two quotients",
                "Nested compositions peel one layer at a time; `d/dx [g(x)]^n = n*[g(x)]^(n-1)*g'(x)` is the case worth memorising",
                "The inverse rule `(f_inv)'(y) = 1/f'(f_inv(y))`: reflecting a graph in the line `y = x` reciprocates its slope",
                "A scale factor inside the function comes back out as a multiplier, which is why every rate a circuit produces carries its frequency with it",
            ],
            "quiz": {
                "title": "Peeling a composition",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is `d/dx (3*x + 1)^5`?",
                        "opts": [
                            "`5*(3*x + 1)^4`",
                            "`15*(3*x + 1)^4`",
                            "`15*(3*x + 1)^5`",
                            "`5*(3*x + 1)^4 * 3*x`",
                        ],
                        "a": 1,
                        "why": r"""
The outer power rule gives `5*(3*x + 1)^4` and the inner derivative of `3*x + 1` is `3`,
so the two multiply to `15*(3*x + 1)^4`. Losing that inner `3` is the classic omission,
and the binomial expansion catches it: `(1 + 3*x)^5 = 1 + 15*x + ...`, so the slope at
`x = 0` is `15`, not `5`. Leaving the exponent at `5` forgets the outer rule instead, and
differentiating the inside to `3*x` rather than `3` differentiates it one step too few.
""",
                    },
                    {
                        "q": "What is `d/dx sqrt(1 + x*x)`?",
                        "opts": [
                            "`1/(2*sqrt(1 + x*x))`",
                            "`2*x/sqrt(1 + x*x)`",
                            "`x/sqrt(1 + x*x)`",
                            "`x/(2*sqrt(1 + x*x))`",
                        ],
                        "a": 2,
                        "why": r"""
Outer layer: `1/(2*sqrt(u))`. Inner layer: `2*x`. Their product is
`2*x/(2*sqrt(1 + x*x))`, and the twos cancel to leave `x/sqrt(1 + x*x)`. Forgetting the
inner factor leaves the bare `1/(2*sqrt(...))`; cancelling only one of the two twos
leaves either the doubled or the halved version. A symmetry check settles it in one
line: the function is even, so its derivative must be odd and must vanish at `x = 0`.
Only `x/sqrt(1 + x*x)` does.
""",
                    },
                    {
                        "q": "`y` depends on `u` and `u` on `x`. At `x = 1` you measure `u = 5` and `du/dx = 0.5`, and at `u = 5` you measure `dy/du = -2`. What is `dy/dx` at `x = 1`?",
                        "opts": [
                            "`-4`",
                            "`-1.5`",
                            "`-2`",
                            "`-1`",
                        ],
                        "a": 3,
                        "why": r"""
Multiply the two rates: `-2 * 0.5 = -1`. The units say why it has to be a product —
`dy/du` is `y` per `u` and `du/dx` is `u` per `x`, so the `u` cancels and what is left is
`y` per `x`. Dividing gives `-4` and treats the rates as if they were being compared
rather than chained. Reporting `-2` uses only the outer rate and ignores that `x` moves
`u` at half speed, so the effect on `y` is halved too. Note also that `dy/du` must be
read at `u = 5`, not at `u = 1`.
""",
                    },
                    {
                        "q": "`f(x) = x^3 + x`, so `f(1) = 2` and `f'(x) = 3*x*x + 1`. What is `(f_inv)'(2)`?",
                        "opts": [
                            "`1/4`",
                            "`4`",
                            "`1/13`",
                            "`13`",
                        ],
                        "a": 0,
                        "why": r"""
The inverse rule evaluates `f'` at the point that maps to `2`, which is `x = 1`:
`f'(1) = 4`, so the inverse has slope `1/4` there. Using `f'(2) = 13` reads the
derivative at the wrong place — it is the input of `f` that matters, not the input of the
inverse. Dropping the reciprocal leaves `4`, but reflecting a graph in `y = x` swaps rise
and run, so a steep `f` must have a shallow inverse. The rule is safe here because
`f'` is positive everywhere, so `f` is strictly increasing and the inverse exists.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M6
        {
            "title": "Derivatives of the exponential, logarithm and trigonometric functions",
            "summary": "The functions engineering actually runs on, and where each of their derivatives comes from.",
            "concepts": [
                "`e` is the base whose exponential is its own derivative: `d/dx e^x = e^x`, and `d/dx a^x = a^x * ln(a)`",
                "`d/dx ln(x) = 1/x`, whether you take it from the inverse rule or from the limit that defines `e`",
                "`sin' = cos` and `cos' = -sin`, both built from `lim h->0 sin(h)/h = 1` and `lim h->0 (cos(h) - 1)/h = 0`",
                "The inverse trigonometric derivatives are algebraic: `d/dx arctan(x) = 1/(1 + x*x)` and `d/dx arcsin(x) = 1/sqrt(1 - x*x)`",
                "Logarithmic differentiation: take `ln` of both sides first, and a product becomes a sum while a variable exponent becomes a coefficient",
            ],
            "quiz": {
                "title": "Growth, decay and the two that go round",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A capacitor discharges as `v(t) = V0 * exp(-t/T)`, with `V0` and the time constant `T` constant. What is `dv/dt`?",
                        "opts": [
                            "`-V0 * exp(-t/T)`",
                            "`-(V0/T) * exp(-t/T)`",
                            "`(V0/T) * exp(-t/T)`",
                            "`-(t/T) * V0 * exp(-t/T)`",
                        ],
                        "a": 1,
                        "why": r"""
The exponential reproduces itself and the chain rule supplies the inner derivative of
`-t/T`, which is `-1/T`, giving `-(V0/T)*exp(-t/T)`. Dropping that `1/T` loses the time
constant and with it the units: `dv/dt` has to come out in volts per second, and only the
version carrying `1/T` does. The sign is negative because the capacitor is emptying. At
`t = 0` the rate is `-V0/T`, which is the tangent behind the familiar picture of a
capacitor that would be flat in exactly one time constant if it kept its initial slope.
""",
                    },
                    {
                        "q": "What is `d/dx 2^x`?",
                        "opts": [
                            "`x * 2^(x-1)`",
                            "`2^x`",
                            "`2^x * ln(2)`",
                            "`2^x / ln(2)`",
                        ],
                        "a": 2,
                        "why": r"""
Rewrite the base in terms of `e`: `2^x = exp(x*ln(2))`, and the chain rule leaves the
constant `ln(2)`, about `0.693`, as a factor. The power rule does not apply at all here —
the variable is in the exponent, not the base — so `x * 2^(x-1)` is a category error worth
naming rather than merely marking wrong. The plain `2^x` is the answer only for base `e`,
which is the property that singles `e` out. Dividing by `ln(2)` is the change-of-base
rule for logarithms, a different formula entirely.
""",
                    },
                    {
                        "q": "With `f` constant, what is `d/dt sin(2*pi*f*t)`?",
                        "opts": [
                            "`cos(2*pi*f*t)`",
                            "`2*pi*f * cos(2*pi*f*t)`",
                            "`2*pi*f*t * cos(2*pi*f*t)`",
                            "`-2*pi*f * cos(2*pi*f*t)`",
                        ],
                        "a": 1,
                        "why": r"""
`sin` differentiates to `cos`, and the chain rule multiplies by the inner derivative,
the angular frequency `2*pi*f`. That factor is why differentiation amplifies high
frequencies: at the same amplitude, a 1 kHz tone comes back a thousand times larger than
a 1 Hz one, which is the whole behaviour of a differentiating circuit. Differentiating
the inside to `2*pi*f*t` stops one step short, dropping the factor altogether keeps only
the outer rule, and the minus sign belongs to `cos`, not to `sin`.
""",
                    },
                    {
                        "q": "Why is `lim h->0 sin(h)/h = 1` proved geometrically rather than with L'Hopital's rule?",
                        "opts": [
                            "L'Hopital's rule does not apply, because the form is `0/0`",
                            "It is not a limit at all, only a small-angle approximation",
                            "That limit is the derivative of `sin` at `0`, so using `sin' = cos` to prove it assumes what is being proved",
                            "L'Hopital's rule gives the wrong value here",
                        ],
                        "a": 2,
                        "why": r"""
The quotient `sin(h)/h` is exactly the difference quotient of `sin` at `0`. Applying
L'Hopital's rule means differentiating `sin`, which is the very fact the limit is being
used to establish, so the argument would be circular. It is settled first by squeezing
`sin(h)` between two areas on the unit circle. The rule does apply to `0/0` forms — that
is precisely its home ground — and it does return `1`; the objection is not that the
value is wrong but that the derivation is not allowed to be the proof.
""",
                    },
                    {
                        "q": "For `x > 0`, what is `d/dx x^x`?",
                        "opts": [
                            "`x * x^(x-1)`",
                            "`x^x * ln(x)`",
                            "`x^x`",
                            "`x^x * (1 + ln(x))`",
                        ],
                        "a": 3,
                        "why": r"""
Neither standard rule applies on its own, because the variable sits in the base and in
the exponent at once. Take logs: `ln(y) = x*ln(x)`, differentiate both sides — the chain
rule turns the left into `y'/y` — and get `y'/y = ln(x) + 1`, so `y' = x^x * (1 + ln(x))`.
Freezing the exponent and using the power rule gives `x * x^(x-1) = x^x`; freezing the
base and using the exponential rule gives `x^x * ln(x)`. The true derivative is their sum,
which is what logarithmic differentiation quietly encodes.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M7
        {
            "title": "Implicit differentiation and related rates",
            "summary": "Differentiating a relation nobody solved for y, and turning one measured rate into another.",
            "concepts": [
                "A curve need not be a graph: differentiate the equation term by term with `y` treated as a function of `x`, then solve for `dy/dx`",
                "Every `y` term contributes a `dy/dx` factor by the chain rule, and that factor is the entire method",
                "Related rates: differentiate the relation with respect to `t`, and each variable brings its own rate along",
                "Substitute the instantaneous values only after differentiating; a number fixed too early has its rate quietly set to zero",
                "Signs and units carry the physics: `i = C*dv/dt` is a related rate, and so is the falling level in a tank that is emptying",
            ],
            "quiz": {
                "title": "The factor everyone drops",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Differentiating `x*x + y*y = 25` with respect to `x`, where `y` is a function of `x`, gives:",
                        "opts": [
                            "`2*x + 2*y = 0`",
                            "`2*x + 2*y*(dy/dx) = 0`",
                            "`2*x + (dy/dx) = 0`",
                            "`0 = 0`, since 25 is a constant",
                        ],
                        "a": 1,
                        "why": r"""
Along the curve `y` is a function of `x`, so `d/dx` of `y*y` is `2*y*(dy/dx)` by the
chain rule. The right-hand side really does differentiate to zero, but that does not make
the left-hand side vanish term by term. Solving gives `dy/dx = -x/y`, which at the point
`(3, 4)` is `-3/4` — perpendicular to the radius, exactly as a circle requires, and a
useful check that the method was applied correctly. Dropping the `dy/dx` factor is the
one mistake this technique exists to prevent, and losing the `2*y` as well makes it worse.
""",
                    },
                    {
                        "q": "If `y` is a function of `x`, what is `d/dx (y^3)`?",
                        "opts": [
                            "`3*y*y`",
                            "`3*y*y*(dy/dx)`",
                            "`3*x*x*(dy/dx)`",
                            "`y^3*(dy/dx)`",
                        ],
                        "a": 1,
                        "why": r"""
The outer power rule gives `3*y*y` and the chain rule multiplies by the inner derivative
`dy/dx`. Without that factor the expression would be the derivative with respect to `y`,
not with respect to `x`. Differentiating the wrong letter produces the version in `x`,
which has nothing to do with the relation. Compare `d/dx x^3 = 3*x*x`, where the inner
derivative is `dx/dx = 1` and the factor is invisible — which is precisely why it is so
easy to forget the moment the letter changes.
""",
                    },
                    {
                        "q": "A spherical balloon has `V = (4/3)*pi*r^3`. At the instant when `r = 5 cm` and `dr/dt = 2 cm/s`, what is `dV/dt`?",
                        "opts": [
                            "`200*pi cm^3/s`",
                            "`100*pi cm^3/s`",
                            "`(4/3)*pi*125 cm^3/s`",
                            "`4*pi*25 cm^3`",
                        ],
                        "a": 0,
                        "why": r"""
Differentiate with respect to `t` first: `dV/dt = 4*pi*r*r*(dr/dt)`, then substitute, to
get `4*pi*25*2 = 200*pi`, about `628 cm^3/s`. The factor `4*pi*r*r` is the surface area,
so the volume grows at the area times the speed the surface moves outward — a check that
costs nothing. Substituting `r = 5` into `V` before differentiating turns the volume into
a constant with rate zero, which is why the instantaneous numbers go in last. The volume
itself is not a rate at all, and its units say so.
""",
                    },
                    {
                        "q": "A `10 uF` capacitor has a voltage rising at `3 V/ms`. Since `i = C*(dv/dt)`, the current is:",
                        "opts": [
                            "`30 uA`",
                            "`3 mA`",
                            "`30 mA`",
                            "`0.03 mA`",
                        ],
                        "a": 2,
                        "why": r"""
Put the rate into volts per second before multiplying: `3 V/ms` is `3000 V/s`, so
`i = 10e-6 * 3000 = 0.03 A`, which is `30 mA`. Multiplying by the bare `3` without
converting the milliseconds gives `30 uA`, a thousand times too small, and that single
conversion is what the question is really testing. This is a related rate in disguise:
the capacitor relation ties charge to voltage, and differentiating it in time is where
the current comes from.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M8
        {
            "title": "The mean value theorem and the shape of a graph",
            "summary": "The theorem that connects a derivative back to the function it came from, and everything it licenses.",
            "concepts": [
                "Rolle's theorem: equal values at the ends of a differentiable arc force a horizontal tangent somewhere between them",
                "The mean value theorem: some interior slope equals the average slope `(f(b) - f(a))/(b - a)` — the speed-camera argument",
                "Its corollaries do the real work: `f' = 0` on an interval means constant, `f' > 0` means increasing, and two functions with the same derivative differ by a constant",
                "Concavity is the sign of `f''`; an inflection is where that sign changes, not merely where `f''` is zero",
                "L'Hopital's rule is a two-function mean value theorem in disguise, and it applies only to `0/0` and `inf/inf` — check the form before using it",
            ],
            "quiz": {
                "title": "What the mean value theorem licenses",
                "minutes": 9,
                "questions": [
                    {
                        "q": "For `f(x) = x*x` on `[0, 3]`, the mean value theorem promises a `c` where `f'(c)` equals the average slope. Which `c`?",
                        "opts": [
                            "`c = 3`",
                            "`c = 2.25`",
                            "`c = 1.5`",
                            "There is none, because `f(0)` and `f(3)` are different",
                        ],
                        "a": 2,
                        "why": r"""
The average slope is `(9 - 0)/(3 - 0) = 3`, and `f'(c) = 2*c = 3` gives `c = 1.5` — the
midpoint, as it always is for a parabola. Equal endpoint values are Rolle's extra
hypothesis, not this theorem's: the mean value theorem asks only for continuity on the
closed interval and differentiability inside, which a parabola has everywhere. The value
`2.25` is `f(1.5)`, a height rather than a location, and confusing the two is the usual
way this question goes wrong.
""",
                    },
                    {
                        "q": "`f(x) = |x|` on `[-1, 1]` has `f(-1) = f(1)` yet no interior point where `f' = 0`. Why is Rolle's theorem not violated?",
                        "opts": [
                            "Rolle's theorem needs differentiability at every interior point, and `|x|` has no derivative at `0`",
                            "Rolle's theorem applies only to polynomials",
                            "It is violated; the theorem holds for most functions but not all",
                            "`f'(0) = 0`, because `|x|` has a minimum there",
                        ],
                        "a": 0,
                        "why": r"""
The function is continuous on the closed interval but fails differentiability at exactly
one interior point, and one failure is enough to release the conclusion. The minimum at
the origin is genuine, but turning a minimum into a zero derivative is Fermat's theorem,
which also needs a derivative to exist — at a corner there is no tangent line to be
horizontal. Theorems are never violated by examples; an example only shows which
hypothesis was load-bearing, and here it is differentiability rather than the shape of
the function.
""",
                    },
                    {
                        "q": "L'Hopital's rule may legitimately be applied to which of these?",
                        "opts": [
                            "`lim x->0 of (x + 1)/(x + 2)`",
                            "`lim x->0 of (exp(x) - 1)/x`",
                            "`lim x->0 of cos(x)/(1 + x)`",
                            "`lim x->2 of (x*x + 1)/(x - 1)`",
                        ],
                        "a": 1,
                        "why": r"""
Substituting into `(exp(x) - 1)/x` gives `0/0`, the indeterminate form the rule exists
for, and differentiating top and bottom gives `exp(x)/1`, which tends to `1`. The others
substitute cleanly to `1/2`, `1` and `5`, so there is nothing to resolve — and applying
the rule anyway produces confident nonsense: the cosine quotient would come out as `0`
instead of `1`. Checking the form is not a formality before the method, it is the
hypothesis of the theorem.
""",
                    },
                    {
                        "q": "`f(x) = x^4` has `f''(0) = 0`. Is `x = 0` an inflection point?",
                        "opts": [
                            "Yes — `f'' = 0` is what an inflection point means",
                            "Yes, and `f'(0) = 0` confirms it",
                            "No: `f'' = 12*x*x` is positive on both sides, so the concavity never changes",
                            "No, because `f` is not twice differentiable at `0`",
                        ],
                        "a": 2,
                        "why": r"""
The second derivative touches zero at the origin without crossing it, so the curve is
concave up on both sides and its shape never changes — the point is a minimum, not an
inflection. A vanishing second derivative is necessary but not sufficient; the sign has
to change. The function is differentiable to every order everywhere, so smoothness is
not the issue. This is exactly the check the capstone's inflection method is required to
perform rather than trusting a root of `f''` on its own.
""",
                    },
                    {
                        "q": "`f'(x) = g'(x)` at every point of an interval. What follows?",
                        "opts": [
                            "`f = g` on the interval",
                            "`f - g` is constant on the interval",
                            "`f - g` is linear on the interval",
                            "Nothing, without knowing the two functions",
                        ],
                        "a": 1,
                        "why": r"""
Apply the mean value theorem to `h = f - g`. Its derivative is zero everywhere, so for
any two points `h(b) - h(a) = h'(c)*(b - a) = 0`, and `h` never changes value. It is a
constant, not necessarily zero: `x*x` and `x*x + 7` have identical derivatives without
being the same function. A non-zero slope would make the difference linear, which is
what a constant difference in the derivatives would give instead. This corollary is why
an antiderivative comes with an arbitrary constant and why one initial condition pins it
down.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M9
        {
            "title": "Linear approximation, differentials and error propagation",
            "summary": "Using the tangent line as a stand-in for the curve, and knowing how far that is safe.",
            "concepts": [
                "`L(x) = f(a) + f'(a)*(x - a)` is the tangent line, and the best linear model of `f` near `a`",
                "The differential `dy = f'(x)*dx` is the same statement written for small changes rather than for points",
                "The error is second order, about `f''(a)*(x - a)^2/2`, so halving the step quarters it",
                "Relative error travels through a sensitivity factor: `dy/y = (x*f'(x)/f(x)) * (dx/x)`, which is what a tolerance budget is made of",
                "The approximations worth knowing cold: `(1 + x)^k ~ 1 + k*x`, `sin(x) ~ x`, `exp(x) ~ 1 + x`, `ln(1 + x) ~ x`",
            ],
            "quiz": {
                "title": "How far a tangent line can be trusted",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Linearising `sqrt(x)` at `a = 4` to estimate `sqrt(4.02)` gives:",
                        "opts": [
                            "`2.02`",
                            "`2.005`",
                            "`2.0025`",
                            "`2.05`",
                        ],
                        "a": 1,
                        "why": r"""
`f(4) = 2` and `f'(4) = 1/(2*2) = 0.25`, so the tangent line gives
`2 + 0.25*0.02 = 2.005`. The true value is `2.0049938...`, so the estimate is high by
about `6e-6` — the second-order term `f''(4)*(0.02)^2/2` with `f''(4) = -1/32`, which is
where that number comes from. Adding the whole `0.02` ignores the slope entirely, and
`2.0025` uses a slope of `1/8` rather than `1/4`, the commonest arithmetic slip in the
power rule for a square root.
""",
                    },
                    {
                        "q": "You linearise at `a` and evaluate at distance `d`, then halve `d`. The error of the approximation:",
                        "opts": [
                            "falls by about a factor of 4",
                            "halves",
                            "is unchanged",
                            "falls by about a factor of 8",
                        ],
                        "a": 0,
                        "why": r"""
The first term the tangent line omits is `f''(a)*d*d/2`, so the error scales like `d*d`
and halving `d` divides it by four. This is the same convergence-order arithmetic as the
difference quotients earlier in the course: an order-2 error responds to a halved step by
a factor of four, and measuring that ratio is how you confirm you implemented what you
think you did. An error that merely halved would be first order, and a factor of eight
would mean the quadratic term had cancelled too.
""",
                    },
                    {
                        "q": "`P = V*V/R` with `V` held fixed. A resistor arrives 1% above its nominal value. The power is about:",
                        "opts": [
                            "1% low",
                            "1% high",
                            "2% low",
                            "unchanged, since `V` did not move",
                        ],
                        "a": 0,
                        "why": r"""
Differentiate and divide by `P`: `dP/P = -dR/R`, so the sensitivity to `R` is exactly
`-1` and a resistor 1% high gives a power 1% low. The factor of two belongs to the
voltage, where the square doubles the contribution and `dP/P = 2*dV/V` — keeping those
two sensitivities apart is most of what a tolerance budget does. Nothing here is
unaffected: holding `V` fixed is what makes the dependence on `R` the only one left.
""",
                    },
                    {
                        "q": "For small `x`, `1/(1 + x)` is approximately:",
                        "opts": [
                            "`1 + x`",
                            "`1 - x`",
                            "`1 - x*x`",
                            "`1/x`",
                        ],
                        "a": 1,
                        "why": r"""
Use `(1 + x)^k ~ 1 + k*x` with `k = -1`. Numerically, `1/1.02 = 0.98039...` against the
estimate `0.98`, a slip of `4e-4`, which is the second-order term `x*x` doing its work.
This is the approximation behind the rule that a 2% error in a denominator becomes a 2%
error the other way in the result, and behind every quick estimate of a divider whose
load is large enough to ignore. Getting the sign backwards inverts the whole conclusion,
and a purely quadratic correction drops the first-order term, which is the only one that
matters at this size.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M10
        {
            "title": "Newton-Raphson and the failure modes of iteration",
            "summary": "Tangent-line root finding, and the three ways it goes wrong.",
            "concepts": [
                "Newton's step is the root of the tangent line: x - f(x)/f'(x)",
                "Quadratic convergence near a simple root, and what breaks it",
                "A vanishing derivative leaves the tangent horizontal — no next point exists",
                "Divergence: iterates can run away, as they do for arctan from a large start",
                "Attracting cycles: x^3 - 2x + 2 from 0 alternates between 0 and 1 forever",
                "A relative step h * max(1, |x|) keeps the numerical derivative usable at large x",
                "Every iteration needs a cap; a browser tab has no Ctrl-C",
            ],
            "lab": {
                "title": "Newton's method with guards",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
The two exception classes at the top of `main.py` are given. Use them.

## `numeric_derivative(f, x, h=1e-6)`

A central difference with a **relative** step: `step = h * max(1.0, abs(x))`.
At `x = 120000` an absolute step of `1e-6` is smaller than one unit in the last
place of `x`, so `f(x+h)` and `f(x-h)` become the same number and the quotient
collapses to zero. Scaling the step with `x` avoids that.

## `newton(f, x0, tol=1e-12, max_iter=50, h=1e-6)`

Return `(root, iterations)`, where `iterations` counts the Newton steps taken.

The loop, in order:

1. `fx = f(x)`. If `abs(fx) <= tol`, return `(x, iterations)`.
2. If the cap is reached, raise `Diverged`.
3. `d = numeric_derivative(f, x, h)`. If `abs(d) < DERIV_FLOOR`, raise
   `ZeroDerivative`.
4. `x = x - fx / d`.
5. If `x` is not finite, or `abs(x) > DIVERGE_LIMIT`, raise `Diverged`.

Raise `ValueError` for `tol <= 0` or `max_iter < 1` — those are caller mistakes,
not iteration failures.

```text
newton(lambda x: x*x - 2, 1.0)          -> (1.4142135623730951, 5)
newton(lambda x: x*x + 1, 0.0)          -> ZeroDerivative   f'(0) = 0
newton(lambda x: x**3 - 2*x + 2, 0.0)   -> Diverged         a 2-cycle: 0, 1, 0, 1, ...
newton(math.atan, 2.0)                  -> Diverged         the iterates run away
```
''',
                "files": [{"name": "main.py", "content": r'''
import math

DERIV_FLOOR = 1e-14
DIVERGE_LIMIT = 1e9


class ZeroDerivative(RuntimeError):
    """The tangent is horizontal, so Newton has no next point."""


class Diverged(RuntimeError):
    """The iterates ran away, or the iteration cap was reached."""


def numeric_derivative(f, x, h=1e-6):
    """Central difference with a step scaled by max(1, |x|)."""
    # your code here


def newton(f, x0, tol=1e-12, max_iter=50, h=1e-6):
    """(root, iterations). ZeroDerivative / Diverged on failure."""
    # your code here


print(newton(lambda x: x * x - 2, 1.0))
print(newton(lambda x: math.cos(x) - x, 1.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

DERIV_FLOOR = 1e-14
DIVERGE_LIMIT = 1e9


class ZeroDerivative(RuntimeError):
    """The tangent is horizontal, so Newton has no next point."""


class Diverged(RuntimeError):
    """The iterates ran away, or the iteration cap was reached."""


def numeric_derivative(f, x, h=1e-6):
    """Central difference with a step scaled by max(1, |x|)."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - f(x - step)) / (2 * step)


def newton(f, x0, tol=1e-12, max_iter=50, h=1e-6):
    """(root, iterations). ZeroDerivative / Diverged on failure."""
    if tol <= 0:
        raise ValueError("tol must be strictly positive")
    if max_iter < 1:
        raise ValueError("max_iter must be at least 1")

    x = float(x0)
    for taken in range(max_iter + 1):
        fx = f(x)
        if abs(fx) <= tol:
            return (x, taken)
        if taken == max_iter:
            raise Diverged(f"no convergence in {max_iter} iterations")
        d = numeric_derivative(f, x, h)
        if abs(d) < DERIV_FLOOR:
            raise ZeroDerivative(f"derivative vanished at x={x!r}")
        x = x - fx / d
        # Check the magnitude before the next derivative: a runaway iterate
        # makes the difference quotient meaningless as well as useless.
        if not math.isfinite(x) or abs(x) > DIVERGE_LIMIT:
            raise Diverged(f"iterates left the useful range at x={x!r}")
    raise Diverged("unreachable")


print(newton(lambda x: x * x - 2, 1.0))
print(newton(lambda x: math.cos(x) - x, 1.0))
'''}],
                "hints": [
                    "`step = h * max(1.0, abs(x))` — then divide by `2 * step`, not by `2 * h`.",
                    "Validate `tol` and `max_iter` before the loop starts; those are argument errors, not iteration failures.",
                    "Use `for taken in range(max_iter + 1)` so the convergence test gets one look at the final iterate before the cap fires.",
                    "Raise `Diverged` immediately after updating `x`, before the next derivative is taken.",
                ],
                "tests": [
                    {"name": "numeric_derivative is accurate", "code": r'''
import math as _math
assert abs(numeric_derivative(_math.sin, 1.0) - _math.cos(1.0)) < 1e-8, \
    f"d/dx sin at 1 gave {numeric_derivative(_math.sin, 1.0)!r}, expected {_math.cos(1.0)!r}"
assert abs(numeric_derivative(_math.exp, 2.0) - _math.exp(2.0)) < 1e-6, \
    f"d/dx exp at 2 gave {numeric_derivative(_math.exp, 2.0)!r}"
assert abs(numeric_derivative(lambda x: x * x, 3.0) - 6.0) < 1e-8, "d/dx x^2 at 3 is 6"
'''},
                    {"name": "The relative step survives a large x", "code": r'''
import math as _math
_d = numeric_derivative(_math.atan, 121977.0)
assert _d != 0.0, "An absolute step of 1e-6 vanishes at x=121977 — scale it by |x|"
assert abs(_d - 1.0 / (1.0 + 121977.0 ** 2)) < 1e-14, f"Got {_d!r}"
'''},
                    {"name": "newton finds simple roots quickly", "code": r'''
import math as _math
_r, _n = newton(lambda x: x * x - 2, 1.0)
assert abs(_r - _math.sqrt(2)) < 1e-10, f"sqrt(2) came out as {_r!r}"
assert _n <= 10, f"Newton took {_n} iterations for sqrt(2), expected under 10"
_r, _n = newton(lambda x: _math.cos(x) - x, 1.0)
assert abs(_r - 0.7390851332151607) < 1e-9, f"cos(x)=x root came out as {_r!r}"
_r, _n = newton(lambda x: x ** 3 - 2 * x - 5, 2.0)
assert abs(_r - 2.0945514815423265) < 1e-9, f"cubic root came out as {_r!r}"
'''},
                    {"name": "The starting point decides which root you get", "code": r'''
import math as _math
_r, _n = newton(lambda x: x * x - 2, -1.0)
assert abs(_r + _math.sqrt(2)) < 1e-10, f"From x0=-1 the root should be -sqrt(2), got {_r!r}"
'''},
                    {"name": "Starting on the root costs no iterations", "code": r'''
import math as _math
_r, _n = newton(lambda x: x * x - 2, _math.sqrt(2))
assert _n == 0, f"Already at the root, so 0 steps — got {_n}"
assert abs(_r - _math.sqrt(2)) < 1e-15, f"Got {_r!r}"
'''},
                    {"name": "A horizontal tangent raises ZeroDerivative", "code": r'''
try:
    newton(lambda x: x * x + 1, 0.0)
    assert False, "f'(0) = 0 for x^2 + 1, so this must raise ZeroDerivative"
except ZeroDerivative:
    pass
'''},
                    {"name": "Cycles and runaways raise Diverged", "code": r'''
import math as _math
try:
    newton(lambda x: x ** 3 - 2 * x + 2, 0.0)
    assert False, "x^3 - 2x + 2 from 0 cycles forever, so this must raise Diverged"
except Diverged:
    pass
try:
    newton(_math.atan, 2.0)
    assert False, "arctan from x0=2 runs away, so this must raise Diverged"
except Diverged:
    pass
try:
    newton(lambda x: x ** 3 - 2 * x - 5, 2.0, max_iter=1)
    assert False, "One iteration is not enough here, so this must raise Diverged"
except Diverged:
    pass
'''},
                    {"name": "Bad arguments raise ValueError, not Diverged", "code": r'''
for _kw in ({"tol": 0.0}, {"tol": -1e-9}, {"max_iter": 0}, {"max_iter": -3}):
    try:
        newton(lambda x: x * x - 2, 1.0, **_kw)
        assert False, f"newton(..., {_kw!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M11
        {
            "title": "Critical points and optimisation",
            "summary": "Finding where the derivative changes sign, and deciding what happens there.",
            "concepts": [
                "Fermat's theorem: an interior extremum forces f'(x) = 0",
                "A sign change of f' brackets a critical point; bisection then locates it",
                "The second derivative test, and the cases where it is silent",
                "The first derivative test as the fallback when f''(x) is zero",
                "The extreme value theorem: on a closed interval the candidates are the critical points plus the two endpoints",
                "Grid-based search misses anything narrower than the grid — state the limitation",
                "A sample that lands exactly on a root produces no sign change and must be handled separately",
            ],
            "lab": {
                "title": "Locating and classifying critical points",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
`derivative` and `second_derivative` are given at the top of `main.py`. You
write the four functions below.

## `bracket_sign_changes(g, a, b, n)`

Evaluate `g` at the `n + 1` points `x_k = a + k * (b - a) / n`. Walk the
samples in order and emit:

- `(x_k, x_k)` — a *degenerate* bracket — whenever `g(x_k)` is exactly `0.0`
- `(x_k, x_{k+1})` when `g(x_k) * g(x_{k+1}) < 0`

Check every index once, including the last point. Raise `ValueError` when
`n < 1` or `a >= b`.

The degenerate case is not pedantry: for `f(x) = x^4 - 2x^2` on `[-2, 2]` with
`n = 400` the grid lands exactly on `-1`, `0` and `1`, where `f'` is zero and
never changes sign across a pair.

## `bisect(g, lo, hi, tol=1e-12, max_iter=200)`

Bisection. Return `lo` immediately when `lo == hi`. Raise `ValueError` when
`g(lo) * g(hi) > 0`. Otherwise halve until the bracket is no wider than `tol`
or the cap is reached, then return the midpoint.

## `critical_points(f, a, b, n=400)`

Bracket the sign changes of `derivative(f, ·)`, bisect each one, round the
roots to 9 decimal places, drop duplicates, and return a list of `(x, kind)`
sorted by `x`. Classify with the second derivative test, threshold `1e-5`:

```text
f''(x) >  1e-5   -> "minimum"
f''(x) < -1e-5   -> "maximum"
otherwise        -> first derivative test one grid step either side:
                    negative then positive -> "minimum"
                    positive then negative -> "maximum"
                    anything else          -> "inflection"
```

## `optimise(f, a, b, n=400)`

The extreme value theorem, mechanised. Consider the endpoints and every
critical point, and return `{"min": (x, f(x)), "max": (x, f(x))}`. Ties in the
value are broken by the smaller `x`.
''',
                "files": [{"name": "main.py", "content": r'''
import math

CLASSIFY_TOL = 1e-5


def derivative(f, x, h=1e-6):
    """Given. Central difference with a step scaled by max(1, |x|)."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - f(x - step)) / (2 * step)


def second_derivative(f, x, h=1e-4):
    """Given. Second-order central difference."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - 2 * f(x) + f(x - step)) / (step * step)


def bracket_sign_changes(g, a, b, n):
    """Brackets where g changes sign, plus degenerate (x, x) for exact zeros."""
    # your code here


def bisect(g, lo, hi, tol=1e-12, max_iter=200):
    """Bisect a bracket down to width tol. ValueError if the signs agree."""
    # your code here


def critical_points(f, a, b, n=400):
    """Sorted [(x, kind)] with kind in minimum / maximum / inflection."""
    # your code here


def optimise(f, a, b, n=400):
    """{"min": (x, f(x)), "max": (x, f(x))} over endpoints and critical points."""
    # your code here


print(critical_points(lambda x: x ** 3 - 3 * x, -3.0, 3.0))
print(optimise(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

CLASSIFY_TOL = 1e-5


def derivative(f, x, h=1e-6):
    """Given. Central difference with a step scaled by max(1, |x|)."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - f(x - step)) / (2 * step)


def second_derivative(f, x, h=1e-4):
    """Given. Second-order central difference."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - 2 * f(x) + f(x - step)) / (step * step)


def bracket_sign_changes(g, a, b, n):
    """Brackets where g changes sign, plus degenerate (x, x) for exact zeros."""
    if n < 1:
        raise ValueError("n must be at least 1")
    if a >= b:
        raise ValueError("need a < b")
    step = (b - a) / n
    xs = [a + step * k for k in range(n + 1)]
    vals = [g(x) for x in xs]
    out = []
    for i in range(n):
        if vals[i] == 0.0:
            out.append((xs[i], xs[i]))
        elif vals[i] * vals[i + 1] < 0.0:
            out.append((xs[i], xs[i + 1]))
    if vals[n] == 0.0:
        out.append((xs[n], xs[n]))
    return out


def bisect(g, lo, hi, tol=1e-12, max_iter=200):
    """Bisect a bracket down to width tol. ValueError if the signs agree."""
    if lo == hi:
        return lo
    g_lo, g_hi = g(lo), g(hi)
    if g_lo * g_hi > 0.0:
        raise ValueError("g does not change sign across the bracket")
    for _ in range(max_iter):
        if hi - lo <= tol:
            break
        mid = 0.5 * (lo + hi)
        g_mid = g(mid)
        if g_mid == 0.0:
            return mid
        if g_lo * g_mid < 0.0:
            hi, g_hi = mid, g_mid
        else:
            lo, g_lo = mid, g_mid
    return 0.5 * (lo + hi)


def critical_points(f, a, b, n=400):
    """Sorted [(x, kind)] with kind in minimum / maximum / inflection."""
    slope = lambda x: derivative(f, x)
    step = (b - a) / n
    roots = []
    for lo, hi in bracket_sign_changes(slope, a, b, n):
        roots.append(round(bisect(slope, lo, hi), 9) + 0.0)
    out = []
    for x in sorted(set(roots)):
        out.append((x, _classify(f, x, step)))
    return out


def _classify(f, x, step):
    """Second derivative test, falling back to the first derivative test."""
    d2 = second_derivative(f, x)
    if d2 > CLASSIFY_TOL:
        return "minimum"
    if d2 < -CLASSIFY_TOL:
        return "maximum"
    left = derivative(f, x - step)
    right = derivative(f, x + step)
    if left < 0.0 < right:
        return "minimum"
    if left > 0.0 > right:
        return "maximum"
    return "inflection"


def optimise(f, a, b, n=400):
    """Endpoints plus critical points; ties in the value keep the smaller x."""
    xs = sorted(set([a, b] + [x for x, _ in critical_points(f, a, b, n)]))
    pairs = [(x, f(x)) for x in xs]
    lowest = min(pairs, key=lambda pair: (pair[1], pair[0]))
    highest = max(pairs, key=lambda pair: (pair[1], -pair[0]))
    return {"min": lowest, "max": highest}


print(critical_points(lambda x: x ** 3 - 3 * x, -3.0, 3.0))
print(optimise(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0))
'''}],
                "hints": [
                    "Evaluate `g` once per grid point into a list; calling it again inside the loop doubles the work and invites inconsistency.",
                    "In `bisect`, keep the sign of `g(lo)` in a variable and update it with the bracket — one evaluation per halving.",
                    "`round(x, 9) + 0.0` both deduplicates near-identical roots and turns `-0.0` into `0.0`.",
                    "`min(pairs, key=lambda p: (p[1], p[0]))` and `max(pairs, key=lambda p: (p[1], -p[0]))` give the tie rule in one line each.",
                ],
                "tests": [
                    {"name": "bracket_sign_changes finds ordinary crossings", "code": r'''
_b = bracket_sign_changes(lambda x: x * x - 2, 0.0, 3.0, 30)
assert len(_b) == 1, f"x^2-2 crosses once on [0,3], got {_b!r}"
_lo, _hi = _b[0]
assert _lo < 1.4142135623730951 < _hi, f"Bracket {_b[0]!r} should straddle sqrt(2)"
assert bracket_sign_changes(lambda x: x * x + 1, -1.0, 1.0, 20) == [], \
    "x^2+1 has no zero, so there is nothing to bracket"
'''},
                    {"name": "An exact zero on the grid gives a degenerate bracket", "code": r'''
_b = bracket_sign_changes(lambda x: x * (x - 1), -1.0, 2.0, 30)
assert (0.0, 0.0) in _b, f"g(0) is exactly 0 on this grid, expected (0.0, 0.0) in {_b!r}"
_deg = [p for p in _b if p[0] == p[1]]
assert len(_deg) == 2, f"Both 0 and 1 sit on the grid, expected 2 degenerate brackets, got {_deg!r}"
'''},
                    {"name": "bracket_sign_changes validates its interval", "code": r'''
for _args in [(0.0, 1.0, 0), (0.0, 1.0, -5), (1.0, 1.0, 10), (2.0, 1.0, 10)]:
    try:
        bracket_sign_changes(lambda x: x, *_args)
        assert False, f"bracket_sign_changes(g, {_args!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "bisect converges, and refuses a bad bracket", "code": r'''
import math as _math
_g = lambda x: x * x - 2
assert abs(bisect(_g, 1.0, 2.0) - _math.sqrt(2)) < 1e-10, \
    f"bisect gave {bisect(_g, 1.0, 2.0)!r}, expected sqrt(2)"
assert bisect(_g, 1.5, 1.5) == 1.5, "A degenerate bracket returns its own point"
try:
    bisect(_g, 2.0, 3.0)
    assert False, "g has the same sign at both ends, so this must raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "critical_points of x^3 - 3x", "code": r'''
_cp = critical_points(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
assert len(_cp) == 2, f"Expected two critical points, got {_cp!r}"
assert abs(_cp[0][0] + 1.0) < 1e-6 and _cp[0][1] == "maximum", f"Got {_cp[0]!r}, expected (-1, maximum)"
assert abs(_cp[1][0] - 1.0) < 1e-6 and _cp[1][1] == "minimum", f"Got {_cp[1]!r}, expected (1, minimum)"
'''},
                    {"name": "critical_points of the double well, grid points and all", "code": r'''
_cp = critical_points(lambda x: x ** 4 - 2 * x * x, -2.0, 2.0)
assert len(_cp) == 3, f"x^4-2x^2 has three critical points on [-2,2], got {_cp!r}"
_kinds = [k for _, k in _cp]
assert _kinds == ["minimum", "maximum", "minimum"], f"Got {_kinds!r}"
assert abs(_cp[0][0] + 1.0) < 1e-6 and abs(_cp[1][0]) < 1e-6 and abs(_cp[2][0] - 1.0) < 1e-6, \
    f"Critical points should sit at -1, 0, 1 — got {[x for x, _ in _cp]!r}"
'''},
                    {"name": "The first derivative fallback catches a flat minimum", "code": r'''
_cp = critical_points(lambda x: x ** 4, -1.0, 1.0)
assert len(_cp) == 1, f"x^4 has one critical point on [-1,1], got {_cp!r}"
assert abs(_cp[0][0]) < 1e-6, f"It sits at 0, got {_cp[0][0]!r}"
assert _cp[0][1] == "minimum", \
    "f''(0) is zero for x^4, so the first derivative test must decide — expected minimum"
'''},
                    {"name": "optimise solves the open-box problem", "code": r'''
_V = lambda x: x * (30 - 2 * x) * (16 - 2 * x)
_r = optimise(_V, 0.0, 8.0)
_x, _y = _r["max"]
assert abs(_x - 10.0 / 3.0) < 1e-6, f"The box is largest at x=10/3, got {_x!r}"
assert abs(_y - 19600.0 / 27.0) < 1e-4, f"Maximum volume is 19600/27, got {_y!r}"
assert _r["min"] == (0.0, 0.0), f"Both endpoints give volume 0; ties keep the smaller x — got {_r['min']!r}"
'''},
                    {"name": "optimise weighs endpoints against interior points", "code": r'''
_r = optimise(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
assert abs(_r["min"][0] + 3.0) < 1e-9 and abs(_r["min"][1] + 18.0) < 1e-6, \
    f"Global minimum is the left endpoint (-3, -18), got {_r['min']!r}"
assert abs(_r["max"][0] - 3.0) < 1e-9 and abs(_r["max"][1] - 18.0) < 1e-6, \
    f"Global maximum is the right endpoint (3, 18), got {_r['max']!r}"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — single-variable function analyser",
        "runtime": "python",
        "minutes": 240,
        "brief": r'''
Everything in the course, assembled into one reusable object. `analyser.py`
holds the class and is what the checks import; `main.py` is a demo that
analyses two functions and prints their reports.

## `FunctionAnalyser(f, a, b, samples=400)`

Stores `f`, the closed interval `[a, b]` as floats, the sample count, and the
grid step `(b - a) / samples`. It refuses bad input at construction time with
`ValueError`: a non-callable `f`, an interval where `a >= b`, or fewer than two
samples.

## Numerical primitives

- `derivative(x, h=1e-6)` — central difference, step `h * max(1, abs(x))`
- `second_derivative(x, h=1e-4)` — `(f(x+s) - 2f(x) + f(x-s)) / s^2`, same
  relative step

## Structure

- `roots()` — sorted `x` values in `[a, b]` where `f` crosses zero, or where a
  grid sample lands exactly on a zero. Round each to 9 decimals and deduplicate.
- `critical_points()` — sorted `(x, kind)` pairs from the zeros of the
  derivative, `kind` in `"minimum"`, `"maximum"`, `"inflection"`. Classify with
  the second derivative test at threshold `1e-5`, falling back to the sign of
  the derivative one grid step either side.
- `inflection_points()` — zeros of the second derivative, kept **only** when
  the second derivative genuinely changes sign one grid step either side. A
  touch that does not cross is not an inflection.
- `monotonic_intervals()` — cut `[a, b]` at the critical points and label each
  piece `"increasing"`, `"decreasing"` or `"constant"` by the sign of the
  derivative at its midpoint. Returns `(lo, hi, label)` triples.
- `extrema()` — `{"min": (x, f(x)), "max": (x, f(x))}` over the endpoints and
  the critical points, ties broken by the smaller `x`.

## `report()`

A nine-line string, in this order, values formatted to six decimals and an
empty list written as `none`:

```text
interval: [-3.000000, 3.000000]
roots: -1.732051, 0.000000, 1.732051
minima: 1.000000
maxima: -1.000000
inflections: 0.000000
increasing: [-3.000000, -1.000000], [1.000000, 3.000000]
decreasing: [-1.000000, 1.000000]
global min: f(-3.000000) = -18.000000
global max: f(3.000000) = 18.000000
```

## Known limitations, which you should state in a docstring

A grid search cannot see a feature narrower than one grid step, and a double
root where `f` touches zero without crossing is only found when a sample lands
on it exactly. Say so rather than pretending otherwise.
''',
        "deliverables": [
            "`analyser.py` — the `FunctionAnalyser` class, importable with no side effects",
            "`main.py` — a demo that builds two analysers and prints both reports",
            "Constructor validation that raises `ValueError` instead of storing a broken interval",
            "A shared bracket-and-bisect helper reused by roots, critical points and inflections",
            "Classification that falls back to the first derivative test when the second is silent",
            "A `report()` string a human can read in a terminal",
        ],
        "constraints": [
            "Standard library only; `math` is the only import you need",
            "`analyser.py` must define the class only — importing it must print nothing",
            "No global mutable state: two analysers must not share any cached result",
            "Every public method returns a value; none of them print",
            "Bisection must be capped, so no input can hang the browser tab",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the empty-result and validation cases."},
            {"criterion": "Numerical robustness", "weight": 25,
             "evidence": "Relative step sizes, exact-zero grid samples handled, bisection capped, inflections confirmed by an actual sign change."},
            {"criterion": "Decomposition and reuse", "weight": 20,
             "evidence": "One bracketing helper and one bisection helper serve roots, critical points and inflections; nothing is copied three times."},
            {"criterion": "Readability and documentation", "weight": 15,
             "evidence": "Docstrings on every public method, the grid limitation stated honestly, no dead code or debug prints."},
        ],
        "hints": [
            "Write `_brackets(g)` and `_bisect(g, lo, hi)` first — every structural method is then three lines on top of `_roots_of(g)`.",
            "`self.derivative` and `self.second_derivative` are bound methods, so you can pass them straight into `_roots_of` as the callable `g`.",
            "`round(x, 9) + 0.0` deduplicates and kills `-0.0`; `sorted(set(...))` then finishes the job.",
            "Format with a helper that snaps anything below `5e-10` to `0.0`, otherwise a root at zero prints as `-0.000000`.",
        ],
        "files": [
            {"name": "analyser.py", "content": r'''
import math

CLASSIFY_TOL = 1e-5


class FunctionAnalyser:
    """Numerical shape analysis of one real function on a closed interval."""

    def __init__(self, f, a, b, samples=400):
        # validate, then store f, a, b, samples and the grid step
        pass

    def derivative(self, x, h=1e-6):
        pass

    def second_derivative(self, x, h=1e-4):
        pass

    def roots(self):
        pass

    def critical_points(self):
        pass

    def inflection_points(self):
        pass

    def monotonic_intervals(self):
        pass

    def extrema(self):
        pass

    def report(self):
        pass
'''},
            {"name": "main.py", "content": r'''
from analyser import FunctionAnalyser

cubic = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
print(cubic.report())
print()

box = FunctionAnalyser(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0)
print(box.report())
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "analyser.py", "content": r'''
import math

CLASSIFY_TOL = 1e-5


def _fmt(value):
    """Six decimals, with anything within half an ulp of zero snapped to 0.0."""
    return f"{0.0 if abs(value) < 5e-10 else value:.6f}"


def _join(values):
    return ", ".join(_fmt(v) for v in values) if values else "none"


def _join_intervals(items):
    if not items:
        return "none"
    return ", ".join(f"[{_fmt(lo)}, {_fmt(hi)}]" for lo, hi, _ in items)


class FunctionAnalyser:
    """Numerical shape analysis of one real function on a closed interval.

    The search is grid based: features narrower than one grid step are
    invisible, and a double root where f touches zero without crossing is only
    reported when a sample happens to land on it exactly. Raise the sample
    count when that matters.
    """

    def __init__(self, f, a, b, samples=400):
        if not callable(f):
            raise ValueError("f must be callable")
        if not a < b:
            raise ValueError("need a < b")
        if samples < 2:
            raise ValueError("samples must be at least 2")
        self.f = f
        self.a = float(a)
        self.b = float(b)
        self.samples = int(samples)
        self.step = (self.b - self.a) / self.samples

    # ------------------------------------------------------------- primitives
    def derivative(self, x, h=1e-6):
        """Central difference with a step scaled by max(1, |x|)."""
        step = h * max(1.0, abs(x))
        return (self.f(x + step) - self.f(x - step)) / (2 * step)

    def second_derivative(self, x, h=1e-4):
        """Second-order central difference, same relative step."""
        step = h * max(1.0, abs(x))
        return (self.f(x + step) - 2 * self.f(x) + self.f(x - step)) / (step * step)

    # ------------------------------------------------------------- machinery
    def _brackets(self, g):
        """Sign-change brackets of g on the grid; exact zeros give (x, x)."""
        xs = [self.a + self.step * k for k in range(self.samples + 1)]
        vals = [g(x) for x in xs]
        out = []
        for i in range(self.samples):
            if vals[i] == 0.0:
                out.append((xs[i], xs[i]))
            elif vals[i] * vals[i + 1] < 0.0:
                out.append((xs[i], xs[i + 1]))
        if vals[self.samples] == 0.0:
            out.append((xs[self.samples], xs[self.samples]))
        return out

    @staticmethod
    def _bisect(g, lo, hi, tol=1e-12, max_iter=200):
        """Capped bisection. A degenerate bracket returns its own point."""
        if lo == hi:
            return lo
        g_lo, g_hi = g(lo), g(hi)
        if g_lo * g_hi > 0.0:
            raise ValueError("g does not change sign across the bracket")
        for _ in range(max_iter):
            if hi - lo <= tol:
                break
            mid = 0.5 * (lo + hi)
            g_mid = g(mid)
            if g_mid == 0.0:
                return mid
            if g_lo * g_mid < 0.0:
                hi, g_hi = mid, g_mid
            else:
                lo, g_lo = mid, g_mid
        return 0.5 * (lo + hi)

    def _roots_of(self, g):
        """Every zero of g on the grid, rounded to 9 decimals and deduplicated."""
        found = [round(self._bisect(g, lo, hi), 9) + 0.0
                 for lo, hi in self._brackets(g)]
        return sorted(set(found))

    # ------------------------------------------------------------- structure
    def roots(self):
        """Sorted zeros of f on [a, b]."""
        return self._roots_of(self.f)

    def critical_points(self):
        """Sorted (x, kind) pairs from the zeros of the derivative."""
        return [(x, self._classify(x)) for x in self._roots_of(self.derivative)]

    def _classify(self, x):
        """Second derivative test, falling back to the first derivative test."""
        d2 = self.second_derivative(x)
        if d2 > CLASSIFY_TOL:
            return "minimum"
        if d2 < -CLASSIFY_TOL:
            return "maximum"
        left = self.derivative(x - self.step)
        right = self.derivative(x + self.step)
        if left < 0.0 < right:
            return "minimum"
        if left > 0.0 > right:
            return "maximum"
        return "inflection"

    def inflection_points(self):
        """Zeros of f'' that are genuine sign changes, not mere touches."""
        keep = []
        for x in self._roots_of(self.second_derivative):
            left = self.second_derivative(x - self.step)
            right = self.second_derivative(x + self.step)
            if left * right < 0.0:
                keep.append(x)
        return keep

    def monotonic_intervals(self):
        """(lo, hi, label) pieces cut at the critical points."""
        cuts = sorted(set([self.a, self.b]
                          + [x for x, _ in self.critical_points()]))
        out = []
        for lo, hi in zip(cuts, cuts[1:]):
            slope = self.derivative(0.5 * (lo + hi))
            if slope > 0.0:
                label = "increasing"
            elif slope < 0.0:
                label = "decreasing"
            else:
                label = "constant"
            out.append((lo, hi, label))
        return out

    def extrema(self):
        """Global min and max over endpoints and critical points."""
        xs = sorted(set([self.a, self.b]
                        + [x for x, _ in self.critical_points()]))
        pairs = [(x, self.f(x)) for x in xs]
        lowest = min(pairs, key=lambda pair: (pair[1], pair[0]))
        highest = max(pairs, key=lambda pair: (pair[1], -pair[0]))
        return {"min": lowest, "max": highest}

    # ------------------------------------------------------------- reporting
    def report(self):
        """A nine-line human-readable summary of everything above."""
        crit = self.critical_points()
        mono = self.monotonic_intervals()
        ext = self.extrema()
        lines = [
            f"interval: [{_fmt(self.a)}, {_fmt(self.b)}]",
            "roots: " + _join(self.roots()),
            "minima: " + _join([x for x, kind in crit if kind == "minimum"]),
            "maxima: " + _join([x for x, kind in crit if kind == "maximum"]),
            "inflections: " + _join(self.inflection_points()),
            "increasing: " + _join_intervals([i for i in mono if i[2] == "increasing"]),
            "decreasing: " + _join_intervals([i for i in mono if i[2] == "decreasing"]),
            f"global min: f({_fmt(ext['min'][0])}) = {_fmt(ext['min'][1])}",
            f"global max: f({_fmt(ext['max'][0])}) = {_fmt(ext['max'][1])}",
        ]
        return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from analyser import FunctionAnalyser

cubic = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
print(cubic.report())
print()

box = FunctionAnalyser(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0)
print(box.report())
print()
print("largest box:", box.extrema()["max"])
'''},
        ],
        "tests": [
            {"name": "The constructor validates its interval", "code": r'''
from analyser import FunctionAnalyser
for _args in [(None, 0.0, 1.0), (lambda x: x, 1.0, 1.0), (lambda x: x, 2.0, 1.0),
              (lambda x: x, 0.0, 1.0, 1), (lambda x: x, 0.0, 1.0, 0)]:
    try:
        FunctionAnalyser(*_args)
        assert False, f"FunctionAnalyser{_args!r} should raise ValueError"
    except ValueError:
        pass
_fa = FunctionAnalyser(lambda x: x, 0.0, 4.0, samples=8)
assert abs(_fa.step - 0.5) < 1e-12, f"step is {_fa.step!r}, expected 0.5"
'''},
            {"name": "The numerical primitives are accurate", "code": r'''
import math as _math
from analyser import FunctionAnalyser
_fa = FunctionAnalyser(_math.sin, 0.0, 6.0)
assert abs(_fa.derivative(1.0) - _math.cos(1.0)) < 1e-8, f"f'(1) gave {_fa.derivative(1.0)!r}"
assert abs(_fa.second_derivative(1.0) + _math.sin(1.0)) < 1e-6, \
    f"f''(1) gave {_fa.second_derivative(1.0)!r}, expected {-_math.sin(1.0)!r}"
_q = FunctionAnalyser(lambda x: 5 * x * x, -1.0, 1.0)
assert abs(_q.second_derivative(0.3) - 10.0) < 1e-5, f"f'' of 5x^2 is 10, got {_q.second_derivative(0.3)!r}"
'''},
            {"name": "roots of a cubic, and a function with none", "code": r'''
import math as _math
from analyser import FunctionAnalyser
_r = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).roots()
assert len(_r) == 3, f"x^3-3x has three roots on [-3,3], got {_r!r}"
for _got, _want in zip(_r, [-_math.sqrt(3), 0.0, _math.sqrt(3)]):
    assert abs(_got - _want) < 1e-6, f"root {_got!r}, expected {_want!r}"
assert FunctionAnalyser(lambda x: x * x + 1, -2.0, 2.0).roots() == [], \
    "x^2+1 has no real root, so the list is empty"
'''},
            {"name": "critical_points classifies a cubic and a double well", "code": r'''
from analyser import FunctionAnalyser
_cp = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).critical_points()
assert len(_cp) == 2, f"Expected two critical points, got {_cp!r}"
assert abs(_cp[0][0] + 1.0) < 1e-6 and _cp[0][1] == "maximum", f"Got {_cp[0]!r}"
assert abs(_cp[1][0] - 1.0) < 1e-6 and _cp[1][1] == "minimum", f"Got {_cp[1]!r}"
_cp = FunctionAnalyser(lambda x: x ** 4 - 2 * x * x, -2.0, 2.0).critical_points()
assert [k for _, k in _cp] == ["minimum", "maximum", "minimum"], f"Got {_cp!r}"
'''},
            {"name": "The first derivative fallback still decides", "code": r'''
from analyser import FunctionAnalyser
_cp = FunctionAnalyser(lambda x: x ** 4, -1.0, 1.0).critical_points()
assert len(_cp) == 1 and abs(_cp[0][0]) < 1e-6, f"Got {_cp!r}"
assert _cp[0][1] == "minimum", \
    "f''(0) is zero for x^4, so the first derivative test must call it a minimum"
'''},
            {"name": "inflection_points needs a real sign change", "code": r'''
from analyser import FunctionAnalyser
_i = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).inflection_points()
assert len(_i) == 1 and abs(_i[0]) < 1e-6, f"x^3-3x inflects only at 0, got {_i!r}"
assert FunctionAnalyser(lambda x: x ** 4, -1.0, 1.0).inflection_points() == [], \
    "f'' of x^4 touches zero at 0 without crossing, so it is not an inflection"
assert FunctionAnalyser(lambda x: x * x, -2.0, 2.0).inflection_points() == [], \
    "A parabola has no inflection point"
'''},
            {"name": "monotonic_intervals cuts at the critical points", "code": r'''
from analyser import FunctionAnalyser
_m = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).monotonic_intervals()
assert len(_m) == 3, f"Two critical points cut [-3,3] into three pieces, got {_m!r}"
assert [t[2] for t in _m] == ["increasing", "decreasing", "increasing"], f"Got {_m!r}"
assert abs(_m[0][0] + 3.0) < 1e-9 and abs(_m[-1][1] - 3.0) < 1e-9, \
    f"The pieces must span the whole interval, got {_m!r}"
assert abs(_m[0][1] + 1.0) < 1e-6 and abs(_m[1][1] - 1.0) < 1e-6, f"Got {_m!r}"
'''},
            {"name": "monotonic_intervals on a function with no critical point", "code": r'''
from analyser import FunctionAnalyser
_m = FunctionAnalyser(lambda x: 2 * x + 1, 0.0, 1.0).monotonic_intervals()
assert len(_m) == 1, f"A straight line gives one piece, got {_m!r}"
assert _m[0][2] == "increasing", f"Got {_m[0]!r}"
'''},
            {"name": "extrema weighs endpoints against interior points", "code": r'''
from analyser import FunctionAnalyser
_e = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).extrema()
assert abs(_e["min"][0] + 3.0) < 1e-9 and abs(_e["min"][1] + 18.0) < 1e-6, f"Got {_e['min']!r}"
assert abs(_e["max"][0] - 3.0) < 1e-9 and abs(_e["max"][1] - 18.0) < 1e-6, f"Got {_e['max']!r}"
_box = FunctionAnalyser(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0)
_e = _box.extrema()
assert abs(_e["max"][0] - 10.0 / 3.0) < 1e-6, f"The box is largest at 10/3, got {_e['max'][0]!r}"
assert abs(_e["max"][1] - 19600.0 / 27.0) < 1e-4, f"Got {_e['max'][1]!r}"
assert _e["min"] == (0.0, 0.0), f"Ties keep the smaller x, so (0.0, 0.0) — got {_e['min']!r}"
'''},
            {"name": "Two analysers share nothing", "code": r'''
from analyser import FunctionAnalyser
_a = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
_b = FunctionAnalyser(lambda x: x * x + 1, -2.0, 2.0)
_a.roots()
assert _b.roots() == [], "The second analyser must not see the first one's results"
assert len(_a.roots()) == 3, "And the first must be unchanged by the second"
'''},
            {"name": "report has nine labelled lines", "code": r'''
from analyser import FunctionAnalyser
_rep = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).report()
assert isinstance(_rep, str), "report() returns a string, it does not print"
_lines = _rep.strip().split("\n")
assert len(_lines) == 9, f"Expected nine lines, got {len(_lines)}: {_lines!r}"
_labels = ["interval:", "roots:", "minima:", "maxima:", "inflections:",
           "increasing:", "decreasing:", "global min:", "global max:"]
for _line, _label in zip(_lines, _labels):
    assert _line.startswith(_label), f"Expected a line starting {_label!r}, got {_line!r}"
assert "-18.000000" in _lines[7], f"Global minimum line was {_lines[7]!r}"
assert "18.000000" in _lines[8], f"Global maximum line was {_lines[8]!r}"
'''},
            {"name": "An empty list is written as none", "code": r'''
from analyser import FunctionAnalyser
_rep = FunctionAnalyser(lambda x: x * x + 1, -2.0, 2.0).report()
_lines = _rep.strip().split("\n")
assert _lines[1] == "roots: none", f"No roots, so the line reads 'roots: none' — got {_lines[1]!r}"
assert _lines[4] == "inflections: none", f"Got {_lines[4]!r}"
'''},
            {"name": "analyser.py is import-clean", "code": r'''
_src = open("analyser.py").read()
assert "print(" not in _src, "analyser.py defines the class; the printing belongs in main.py"
assert "class FunctionAnalyser" in _src, "The class must live in analyser.py"
'''},
        ],
    },
}
