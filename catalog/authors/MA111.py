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
            "read": [
                {
                    "title": "Substitution is a theorem, and it has hypotheses",
                    "minutes": 11,
                    "body": r'''
The last module produced exactly two ways of finding a limit, and both are far too
expensive to use twice. Sampling $f$ near $a$ gives a number that looks convincing and
proves nothing — a table of values cannot tell a limit of $2$ from a limit of
$2.000001$, and catastrophic cancellation can make it lie outright. An
$\epsilon$–$\delta$ argument does prove something, but it takes half a page for a
straight line.

Meanwhile everybody writes

$$\lim_{x\to 2}\left(x^{2}+1\right) = 5$$

without comment, by putting $2$ where the $x$ was. That step is not the definition of a
limit — the definition deliberately refuses to look at $f(2)$ — so something has to
license it. What licenses it is a small family of theorems, and the useful thing about
them is not the statements, which are what you would guess, but the hypotheses, which
are not.

## The laws

Suppose $\lim_{x\to a} f(x) = F$ and $\lim_{x\to a} g(x) = G$,
both existing and both finite. Then

$$\lim_{x\to a}\left(f(x)+g(x)\right) = F+G, \qquad
\lim_{x\to a}\left(f(x)\,g(x)\right) = F\,G, \qquad
\lim_{x\to a}\, c\,f(x) = c\,F,$$

and, **provided $G \neq 0$**,

$$\lim_{x\to a}\frac{f(x)}{g(x)} = \frac{F}{G}.$$

Read the shape rather than the content. Each law begins by *assuming* that every piece
already has a limit of its own, and concludes something about the combination. That
direction matters, and it is the source of most of the trouble later in this reading:
when a hypothesis fails, a law does not say the limit fails to exist. It says nothing
at all.

## Why the sum law is true

The proof is worth seeing once, because it is the only place the number $\epsilon/2$
ever looks mysterious, and it stops looking mysterious immediately.

Let $\epsilon > 0$ be given. We must produce a $\delta$ that forces
$\left|(f+g)(x) - (F+G)\right| < \epsilon$.

The definition of $\lim f = F$ holds for *every* positive tolerance, so we may apply it
to the tolerance $\epsilon/2$ rather than to $\epsilon$: there is a $\delta_{1} > 0$
with

$$0 < |x-a| < \delta_{1} \;\Rightarrow\; |f(x)-F| < \frac{\epsilon}{2}.$$

Apply it to $g$ as well, getting a $\delta_{2}$ with $|g(x)-G| < \epsilon/2$ on its own
window. Now take $\delta = \min(\delta_{1},\delta_{2})$, so that both statements hold at
once, and compute:

$$\left|(f(x)+g(x)) - (F+G)\right| = \left|\,(f(x)-F) + (g(x)-G)\,\right|
\;\le\; |f(x)-F| + |g(x)-G| \;<\; \frac{\epsilon}{2} + \frac{\epsilon}{2} = \epsilon.$$

The middle step is the triangle inequality; everything else is bookkeeping. The halves
were chosen at the start precisely so that they would add to $\epsilon$ at the end.
Nothing about $2$ is special — a sum of five functions would use $\epsilon/5$.

The product law needs one extra idea (a function with a limit is bounded near the
point, so the cross terms can be controlled) and the quotient law needs one more still,
which is the hypothesis worth dwelling on.

## The one condition in the quotient law

The quotient law asks for $G \neq 0$ and asks nothing about $F$. Both halves of that
are worth saying out loud.

$F = 0$ is fine: it just makes the answer $0$. There is nothing indeterminate about
$0/7$.

$G = 0$ is fatal, and not merely as a technicality about dividing by zero. If $G \neq
0$, then close enough to $a$ the function $g$ is bounded away from zero — it cannot
sneak arbitrarily close to $0$ near $a$, because it is busy staying near $G$ — and that
is what keeps $1/g$ from blowing up. Lose the hypothesis and every behaviour becomes
possible at once: with $f(x) = x$ and $g(x) = x^{2}$ at $a = 0$ the quotient
$1/x$ blows up, with $f = x^{2}$ and $g = x$ the quotient $x$ tends to $0$, and with
$f = 3x$ and $g = x$ it sits at $3$ throughout. Same form, three different answers, so
the form itself cannot be the answer.

## What the laws actually buy

Chain the sum and product laws finitely many times, starting from the two limits that
are true by inspection, $\lim_{x\to a} c = c$ and $\lim_{x\to a} x = a$, and you get:
for any polynomial $p$,

$$\lim_{x\to a} p(x) = p(a),$$

and for a quotient of polynomials $p/q$ with $q(a) \neq 0$, the limit is $p(a)/q(a)$.

That is the licence. Substituting is legal for polynomials and for rational functions
away from the zeros of the denominator, and it is legal because of a theorem, not
because a limit means "the value". The class of functions for which substitution works
has a name — the continuous ones — and this reading has just proved that every rational
function is continuous wherever it is defined.

## When substitution returns $0/0$

If $q(a) = 0$ the licence lapses and there is algebra to do. Two examples, one routine
and one that catches people.

### A routine one

$$\lim_{x\to -1}\frac{x^{2}+3x+2}{x^{2}-1}.$$

Substitute first, to find out which case you are in. Numerator: $(-1)^{2} + 3(-1) + 2 =
1 - 3 + 2 = 0$. Denominator: $(-1)^{2} - 1 = 0$. So the form is $0/0$ and the quotient
law does not apply.

Both vanish at $-1$, so both carry a factor of $(x+1)$:

$$x^{2}+3x+2 = (x+1)(x+2), \qquad x^{2}-1 = (x-1)(x+1).$$

Hence for every $x \neq -1$,

$$\frac{x^{2}+3x+2}{x^{2}-1} = \frac{(x+1)(x+2)}{(x-1)(x+1)} = \frac{x+2}{x-1}.$$

The cancellation is legal exactly because a limit only ever inspects the punctured
neighbourhood, where $x + 1 \neq 0$. What is left is a rational function whose
denominator at $-1$ is $-2 \neq 0$, so the licence is back and we substitute:

$$\lim_{x\to -1}\frac{x+2}{x-1} = \frac{-1+2}{-1-1} = \frac{1}{-2} = -\frac{1}{2}.$$

Sampling agrees: at $x = -1.001$ the original quotient reads $-0.4993$.

### The one people get wrong

$$\lim_{x\to 1}\left(\frac{1}{x-1} - \frac{2}{x^{2}-1}\right).$$

Look at the two pieces separately. Neither has a limit at $1$: $1/(x-1)$ runs to
$+\infty$ from the right and $-\infty$ from the left, and $2/(x^{2}-1)$ does the same.
The difference law therefore has nothing to say, since its hypothesis — both pieces
have limits — fails on both counts.

At this point two wrong conclusions are available, and both get drawn. The first is
"neither piece has a limit, so the difference has none". The second is
"$\infty - \infty = 0$". Combine the fractions instead:

$$\frac{1}{x-1} - \frac{2}{(x-1)(x+1)}
= \frac{(x+1) - 2}{(x-1)(x+1)}
= \frac{x-1}{(x-1)(x+1)}
= \frac{1}{x+1} \qquad (x \neq \pm 1),$$

and the last expression is rational with denominator $2 \neq 0$ at the point, so

$$\lim_{x\to 1}\left(\frac{1}{x-1} - \frac{2}{x^{2}-1}\right) = \frac{1}{2}.$$

Check it numerically at $x = 1.001$: the first term is $1000$, the second is
$2/0.002001 = 999.50$, and the difference is $0.4998$. Two quantities of size a
thousand, differing by a half. The blow-ups were real and they cancelled exactly.

## The mistake, and why it is tempting

Writing $0/0 = 0$ is tempting because the numerator really is zero, and zero over
anything *is* zero — for anything except zero. Writing $\infty - \infty = 0$ is
tempting for the same shape of reason: equal things cancel. What both forget is that
$0/0$ and $\infty-\infty$ are not values of an expression; they are reports about a
*form*, and the form is compatible with every answer there is. The $0/0$ examples above
gave $-1/2$ and $1/2$; $\frac{3x}{x}$ gives $3$; $\frac{x}{x^{2}}$ gives no finite
limit at all. An indeterminate form is a question, and the algebra is how it gets
answered.

The subtler mistake is treating a law's silence as a verdict. "The product law does not
apply, therefore no limit" is a non-sequitur, and the standard counterexample is
$x\sin(1/x)$ at $0$: the second factor has no limit, the law is mute, and the limit is
$0$ all the same. Establishing that needs a different tool, which is the next reading.

## Where the laws stop

Three boundaries, all of them live.

**Every piece needs its own limit.** Not "the combination looks fine" — each piece,
separately, finite. When that fails, combine, factor, or rationalise until it holds.

**The denominator's limit must be non-zero.** $F = 0$ is harmless; $G = 0$ voids the
law, and $F = G = 0$ signals that a common factor is waiting to be found.

**"Finitely many" is a hypothesis too.** The sum law extends to any fixed number of
terms by induction, and to no more than that. Take $n$ copies of $1/n$ and add them:
each term tends to $0$ as $n$ grows, and the sum is $1$ at every $n$. Nothing is wrong
with the sum law there; it was simply never a statement about a number of terms that
moves.

One last piece of hygiene. After cancelling, $\frac{x^{2}+3x+2}{x^{2}-1}$ and
$\frac{x+2}{x-1}$ are the same function *except at $x=-1$*, where the first is
undefined and the second equals $-1/2$. The limit does not care about that difference,
which is exactly why the manoeuvre is allowed — but the two expressions are not
interchangeable in every context, and saying they are is how a genuine discontinuity
occasionally gets cancelled away and forgotten.
''',
                },
                {
                    "title": "Squeezing a limit the laws cannot reach",
                    "minutes": 10,
                    "body": r'''
Here is a limit the previous reading cannot touch:

$$\lim_{x\to 0} x\sin\!\left(\frac{1}{x}\right).$$

The product law wants both factors to have limits. The first does; the second does not,
and not by a small margin. As $x \to 0$ the quantity $1/x$ runs off to infinity, so
$\sin(1/x)$ runs through the whole of $[-1,1]$ infinitely often in every interval
around the origin, however short. There is no number it approaches. So the law is
silent — which, as the last reading insisted, is not the same as saying the limit fails
to exist.

What is still true, and true everywhere, is an *inequality*: $\sin$ of anything is
between $-1$ and $1$. The tool that turns an inequality into a limit is the squeeze
theorem, and it is the only theorem in this module that reaches limits the algebraic
laws cannot.

## The statement

Suppose that on some punctured neighbourhood of $a$ — every $x$ with
$0 < |x - a| < r$, for some $r > 0$ — the three functions satisfy

$$g(x) \le f(x) \le h(x),$$

and suppose

$$\lim_{x\to a} g(x) = \lim_{x\to a} h(x) = L.$$

Then $\lim_{x\to a} f(x) = L$.

Three features are worth noticing before any use is made of it. The two outer limits
must be *equal*; nothing is claimed if they merely both exist. The inequality is only
required near $a$, and not at $a$ itself, which is what makes the theorem usable on
functions with a hole. And $f$ is required to have no property of its own — no
continuity, no formula, no limit assumed in advance. Its limit is a conclusion, forced
on it by the neighbours.

## Why it is true

Let $\epsilon > 0$. Since $g \to L$, there is $\delta_{1}$ such that
$L - \epsilon < g(x)$ whenever $0 < |x-a| < \delta_{1}$; that is one half of
$|g(x) - L| < \epsilon$, and it is the half we need. Since $h \to L$, there is
$\delta_{2}$ with $h(x) < L + \epsilon$ on its window.

Take $\delta = \min(\delta_{1}, \delta_{2}, r)$, so that all three facts hold together.
Then for $0 < |x - a| < \delta$,

$$L - \epsilon < g(x) \le f(x) \le h(x) < L + \epsilon,$$

so $L - \epsilon < f(x) < L + \epsilon$, which is $|f(x) - L| < \epsilon$. That is the
definition, and $\epsilon$ was arbitrary.

The whole proof is one chain of inequalities. There is no cleverness in it, and that is
the point: the theorem is a way of transferring a definition from functions you
understand onto one you do not.

## The routine case, worked

$$\lim_{x\to 0} x^{2}\cos\!\left(\frac{1}{x}\right).$$

Start from the fact that holds everywhere the expression is defined, that is, for every
$x \neq 0$:

$$-1 \le \cos\!\left(\frac{1}{x}\right) \le 1.$$

Multiply through by $x^{2}$. This is legal without flipping anything because $x^{2} > 0$
for $x \neq 0$ — and *that* is the step to be careful about, since multiplying an
inequality by a negative quantity reverses it:

$$-x^{2} \le x^{2}\cos\!\left(\frac{1}{x}\right) \le x^{2}.$$

Both outer functions are polynomials, so their limits at $0$ are their values there:
$\lim_{x\to 0}(-x^{2}) = 0$ and $\lim_{x\to 0} x^{2} = 0$. The outer limits agree, so
the squeeze applies and

$$\lim_{x\to 0} x^{2}\cos\!\left(\frac{1}{x}\right) = 0.$$

## Closing the opening example

The same argument settles $x\sin(1/x)$, with one wrinkle worth making explicit, because
it is exactly where a careless copy of the working above goes wrong. Start from the
bound that holds for every $x \neq 0$:

$$-1 \le \sin\!\left(\frac{1}{x}\right) \le 1 .$$

Multiplying through by $x$ is *not* safe this time: for $x < 0$ the inequalities
reverse, and the chain as written would be false on the whole left half of every
neighbourhood of the origin. Two ways round it. One is to handle the two sides
separately. The shorter one is to multiply by $|x|$, which is positive on both sides,
and read the result off $\left|x\sin(1/x)\right| = |x|\left|\sin(1/x)\right| \le |x|$:

$$-|x| \;\le\; x\sin\!\left(\frac{1}{x}\right) \;\le\; |x| .$$

Both bounds are continuous with the value $0$ at the origin, so
$\lim_{x\to 0}\left(-|x|\right) = \lim_{x\to 0}|x| = 0$, the outer limits agree, and

$$\lim_{x\to 0} x\sin\!\left(\frac{1}{x}\right) = 0 .$$

Look at what has been established, and about what. The function oscillates infinitely
often in every neighbourhood of the origin, crosses zero at $x = 1/(n\pi)$ for every
non-zero integer $n$, and has no value at $0$ at all. None of that had to be dealt
with. The two bounds did the entire job and the unruly factor was never evaluated,
estimated or sampled — which is the characteristic move of this theorem, and the reason
it reaches where the laws are silent.

## The case worth being fluent in

$$\lim_{x\to 0}\frac{\sin x}{x}.$$

This one is $0/0$, no factoring will help, and it is the limit the whole of
trigonometric calculus rests on: it is the derivative of $\sin$ at $0$, and every
derivative of a trigonometric function in Module 6 comes back to it. It cannot be
proved by the limit laws, and it cannot honestly be proved by sampling. The squeeze
does it, given one geometric fact.

Take $0 < x < \pi/2$ and work in the unit circle, with $x$ measured in radians so that
the arc it cuts has length $x$. Compare three areas: the triangle with vertices at the
centre, at $(1,0)$ and at the point on the circle at angle $x$; the circular sector
between the same two radii; and the right triangle formed by the tangent at $(1,0)$.
The first sits inside the second, which sits inside the third, so

$$\frac{1}{2}\sin x \;\le\; \frac{1}{2}x \;\le\; \frac{1}{2}\tan x .$$

Multiply by $2$ and divide by $\sin x$, which is strictly positive on this interval, so
the inequalities keep their direction:

$$1 \;\le\; \frac{x}{\sin x} \;\le\; \frac{1}{\cos x}.$$

All three quantities are positive, and taking reciprocals of positive quantities
reverses the order:

$$\cos x \;\le\; \frac{\sin x}{x} \;\le\; 1 .$$

Now $\cos x \to 1$ as $x \to 0$, and the constant $1$ does too. Equal outer limits, so

$$\lim_{x\to 0^{+}}\frac{\sin x}{x} = 1.$$

The restriction $x > 0$ was needed to divide by $\sin x$ without flipping. For the left
side, note that $\frac{\sin(-x)}{-x} = \frac{-\sin x}{-x} = \frac{\sin x}{x}$: the
function is even, so the left-hand limit equals the right-hand one, and the two-sided
limit is $1$.

Two consequences follow immediately and get used constantly. First, for any constant
$k \neq 0$, substituting $t = kx$ gives

$$\lim_{x\to 0}\frac{\sin (kx)}{x} = \lim_{x \to 0} k\cdot\frac{\sin (kx)}{kx} = k .$$

Second, radians are not a convention here but a hypothesis: the sector area is
$\frac{1}{2}x$ only when $x$ is in radians. In degrees the same limit comes out
$\pi/180$, and every derivative formula for $\sin$ and $\cos$ picks up that factor.
That is the real reason calculus uses radians.

## The mistake

The classic misuse is to squeeze with bounds that do not meet. From
$-1 \le \sin(1/x) \le 1$ one may write

$$-1 \le \sin\!\left(\frac{1}{x}\right) \le 1$$

and conclude precisely nothing about $\lim_{x\to 0}\sin(1/x)$, because the outer limits
are $-1$ and $1$ and the theorem requires them to be the same number. The bound is
correct; it is just not a squeeze. What made the opening example work was not the
boundedness of the sine on its own, but the factor of $x$ multiplying it, which dragged
both bounds to the same place.

The second misuse is to assume boundedness is enough regardless of what multiplies it.
Consider

$$\frac{\sin(1/x)}{x}.$$

The numerator is bounded, exactly as before. The limit at $0$ does not exist, and not
because of the oscillation alone: the expression is unbounded, taking values of size
$1/x$ whenever $\sin(1/x)$ happens to be near $1$. Bounded times *small* is small;
bounded divided by small is anything at all.

## Where it stops

The theorem needs the two outer limits to be equal, needs the inequality only near the
point, and gives back nothing more than the value $L$. In particular it says nothing
about *how fast* $f$ approaches $L$, and nothing about $f$ being continuous, monotone
or even defined at $a$.

It also transfers verbatim to limits at infinity — replace "for $0 < |x - a| < \delta$"
by "for $x > X$" throughout the proof and nothing else changes — which is how
$\lim_{x\to\infty}\frac{\sin x}{x} = 0$ is established, with the bounds $-1/x$ and
$1/x$. That limit is the subject of the next reading, where infinity gets a definition
of its own.
''',
                },
                {
                    "title": "Both ends of the line, and a sign change you can trust",
                    "minutes": 14,
                    "body": r'''
Two questions are left over, and they are the two that a graph answers at a glance and
algebra has to work for. What does a function settle down to far out along the axis?
And what happens at a point where a denominator vanishes but no cancellation rescues
it? Both are called limits, both are written with $\infty$, and in neither case is
$\infty$ a number that has been reached.

The third question in this reading is different in kind. Granted a function is
continuous, what can be deduced from two of its values? The answer is the theorem that
makes root-finding by bracketing legitimate, and it is the one result in this module
that is genuinely deeper than it looks.

## What $x \to \infty$ means

There is no point at infinity to be near, so the definition of Module 1 cannot be
recycled. The replacement keeps the tolerance and changes what is required of $x$:

$$\lim_{x\to\infty} f(x) = L$$

means that for every $\epsilon > 0$ there is a number $X$ such that $|f(x) - L| <
\epsilon$ for every $x > X$. "Close enough to $a$" has become "far enough out". The
graph of $y = L$ is then a **horizontal asymptote** of $f$.

The other use of the symbol runs the other way:

$$\lim_{x\to a} f(x) = \infty$$

means that for every $M$ there is a $\delta > 0$ with $f(x) > M$ whenever
$0 < |x - a| < \delta$. This is a statement that the limit *fails to exist*, written in
a form that says how it fails. No arithmetic may be done with the symbol: $\infty$ is
not available as a value of $F$ or $G$ in any of the limit laws.

## Reading a rational function far out

The technique is one line: divide the numerator and the denominator by the highest
power of $x$ that appears anywhere in the fraction, then use $\lim_{x\to\infty} 1/x^{k}
= 0$ for every $k \ge 1$.

$$\lim_{x\to\infty}\frac{5x^{2}-3x+1}{2x^{2}+7}.$$

Both halves grow without bound, so the form is $\infty/\infty$ and the quotient law
does not apply — for the same reason $0/0$ did not, namely that the hypotheses require
finite limits. Divide top and bottom by $x^{2}$, which is legal for every $x \neq 0$
and so in particular throughout the region the limit inspects:

$$\frac{5x^{2}-3x+1}{2x^{2}+7}
= \frac{5 - \dfrac{3}{x} + \dfrac{1}{x^{2}}}{2 + \dfrac{7}{x^{2}}}.$$

Now every piece has a limit of its own — $5$, $0$, $0$, $2$, $0$ — and the denominator's
limit is $2 \neq 0$, so the laws finally apply:

$$\lim_{x\to\infty}\frac{5x^{2}-3x+1}{2x^{2}+7} = \frac{5-0+0}{2+0} = \frac{5}{2}.$$

The general rule falls out of the same working: for a quotient of polynomials, compare
degrees. Equal degrees give the ratio of the leading coefficients; a smaller numerator
degree gives $0$; a larger numerator degree gives no finite limit. Note what the rule
throws away — the lower-order terms decide nothing at infinity, which is exactly the
opposite of the situation at a finite point, where they decide everything.

## The case people get wrong: a root at the far left

$$\lim_{x\to-\infty}\frac{\sqrt{4x^{2}+1}}{3x-2}.$$

The same instinct applies — divide by $x$ — and the trap is inside the root. To take
$x$ under a square root sign one must write it as $\sqrt{x^{2}}$, and

$$\sqrt{x^{2}} = |x|,$$

which is $x$ when $x \ge 0$ and $-x$ when $x < 0$, because the radical sign denotes the
*non-negative* root. As $x \to -\infty$ we are firmly in the second case, so dividing
the numerator by $x$ means dividing it by $-\sqrt{x^{2}}$:

$$\frac{\sqrt{4x^{2}+1}}{x} = \frac{\sqrt{4x^{2}+1}}{-\sqrt{x^{2}}}
= -\sqrt{\frac{4x^{2}+1}{x^{2}}} = -\sqrt{4 + \frac{1}{x^{2}}}.$$

Dividing the denominator by $x$ is ordinary: $(3x-2)/x = 3 - 2/x$. So

$$\frac{\sqrt{4x^{2}+1}}{3x-2} = \frac{-\sqrt{4 + \dfrac{1}{x^{2}}}}{3 - \dfrac{2}{x}}
\;\to\; \frac{-\sqrt{4}}{3} = -\frac{2}{3}.$$

Sampling confirms the sign: at $x = -1000$ the numerator is $\sqrt{4{,}000{,}001}
\approx 2000.0003$ and the denominator is $-3002$, giving $-0.6662$. The answer at the
other end is $+2/3$, and a function with two different horizontal asymptotes is
completely ordinary — this one has them.

The error to name: writing $\sqrt{4x^{2}+1} \approx 2x$ for large negative $x$. It is
false, because the left side is positive and the right side is negative, and it is
tempting because it is true at the other end of the axis and the algebra looks
identical. Any time a root is divided by a variable heading to $-\infty$, a minus sign
is owed.

## A myth about asymptotes

An asymptote is often described as a line the graph approaches but never touches. The
first half is the definition; the second half is false. Take

$$f(x) = \frac{\sin x}{x}, \qquad x > 0 .$$

Since $-1/x \le f(x) \le 1/x$ and both bounds tend to $0$, the squeeze gives
$\lim_{x\to\infty} f(x) = 0$, so $y = 0$ is a horizontal asymptote. And $f$ hits that
asymptote at $x = \pi, 2\pi, 3\pi, \ldots$ — infinitely many times, out to arbitrarily
large $x$. Nothing in the definition forbids it. Crossing the asymptote is only
forbidden for the limit's *final* approach in the sense of $\epsilon$: the graph must
eventually stay within every band around $y = L$, and staying within a band is not the
same as staying on one side of the line.

## Vertical asymptotes, one side at a time

At a finite point, an infinite limit comes from a denominator that goes to zero over a
numerator that does not. The test is one substitution:

$$f(x) = \frac{x+4}{x^{2}-4} = \frac{x+4}{(x-2)(x+2)} .$$

At $x = 2$ the denominator is $0$ and the numerator is $6 \neq 0$, so there is no
common factor to cancel and no hole: this is a genuine blow-up. But *which* infinity
depends on the side, and the only way to know is to track the signs of the factors.

From the right, at $x = 2.001$: the numerator is near $6 > 0$; the factor $x+2$ is near
$4 > 0$; the factor $x-2$ is $+0.001$, positive and tiny. A positive number divided by
a tiny positive number is huge and positive, so

$$\lim_{x\to 2^{+}} \frac{x+4}{x^{2}-4} = +\infty .$$

From the left, at $x = 1.999$, only one sign changes: $x - 2 = -0.001$. So the quotient
is huge and negative, and $\lim_{x\to 2^{-}} f(x) = -\infty$. The two-sided limit
therefore does not exist — not even "as an infinity", because the two sides disagree,
and writing $\lim_{x\to 2} f(x) = \infty$ here would be a false statement rather than a
loose one.

Contrast $x = -2$, where the numerator is $2 \neq 0$: another asymptote, with the signs
working out the other way round, since $x-2$ is now negative. And contrast both with a
point where the numerator vanishes too, such as $x = 2$ in $\frac{x^{2}-4}{x-2}$: there
the factor cancels, the graph has a hole rather than a pole, and the limit is finite.
Zero denominator alone decides nothing.

## A sign change is a root

Now the theorem. Let $f$ be continuous on the closed interval $[a,b]$, and let $N$ be
any number between $f(a)$ and $f(b)$. Then there is at least one $c$ in $(a,b)$ with
$f(c) = N$. The case that gets used is $N = 0$: **if $f$ is continuous on $[a,b]$ and
$f(a)$ and $f(b)$ have opposite signs, then $f$ has a root in $(a,b)$.**

It looks obvious. It is not, and the quickest way to see that is to run the same
sentence over the rational numbers. Let $f(x) = x^{2}-2$, and let $x$ range over
rationals only. Then $f(1) = -1 < 0$ and $f(2) = 2 > 0$, the function is continuous in
every sense a rational-valued world can express, and there is no rational $c$ with
$f(c) = 0$, because $\sqrt{2}$ is irrational. The theorem is false over $\mathbf{Q}$.
So whatever proves it must use a property the rationals lack, and the property is
completeness — the reals have no gaps.

Here is the argument, which doubles as an algorithm. Suppose $f(a) < 0 < f(b)$. Look at
the midpoint $m = (a+b)/2$ and evaluate $f(m)$. If $f(m) = 0$ we are finished. If
$f(m) > 0$, the sign change now sits in $[a,m]$; if $f(m) < 0$, it sits in $[m,b]$.
Either way we have a new interval, half as long, whose endpoints still straddle a sign
change. Repeat forever. The intervals are nested and their lengths $(b-a)/2^{n}$ tend
to $0$, so by completeness they close down on exactly one point $c$. At every stage the
left endpoint has $f \le 0$ and the right endpoint has $f \ge 0$; the endpoints both
converge to $c$, and continuity says $f$ of the limit is the limit of $f$. So $f(c)
\le 0$ and $f(c) \ge 0$ at once, which leaves $f(c) = 0$.

That procedure is **bisection**, and the proof is also its error bound: after $n$ steps
the bracket has width $(b-a)/2^{n}$, so the number of steps needed for a given accuracy
is known in advance, before the function is looked at. Starting from a bracket of width
$1$, ten steps give $2^{-10} < 10^{-3}$. The method is slow — one binary digit per
evaluation — and it cannot fail, which is a trade Module 9 will revisit when Newton's
method offers the opposite bargain.

## Where the theorem stops

**Continuity on the whole closed interval is the hypothesis, and dropping it drops the
conclusion.** Take $f(x) = 1/x$ on $[-1,1]$. Then $f(-1) = -1$ and $f(1) = 1$, values
of opposite sign, and $f$ is never zero anywhere. Nothing has gone wrong with the
theorem: $f$ is not continuous on $[-1,1]$, because it is not even defined at $0$. This
is also the practical failure mode of bisection — bracket a pole instead of a root and
the algorithm converges obediently to the pole, reporting a sign change that never was
a crossing.

**It gives existence, never uniqueness.** A continuous function may cross zero three
times between the endpoints, and the theorem counts nothing. Getting a count needs a
separate argument, usually that $f$ is monotone on the interval.

**It has no converse.** No sign change does not mean no root: $f(x) = x^{2}$ on
$[-1,1]$ has $f(-1) = f(1) = 1$, no sign change at all, and a root sitting at the
origin. A bracketing method is blind to roots of even multiplicity, which is worth
remembering the next time a solver reports that no root exists.
''',
                },
            ],
            "derive": [
                {
                    "title": "Infinity minus infinity, made finite",
                    "minutes": 13,
                    "vars": ["x", "L"],
                    "brief": r'''
Evaluate $\lim_{x\to\infty}\left(\sqrt{x^{2}+3x}-x\right)$.

Both terms run off to infinity, so the difference law says nothing, and dividing by the
dominant power gets nowhere because there is no fraction to divide. The form is
$\infty-\infty$, which is indeterminate: the two terms could separate without bound,
could settle on any finite gap, or could close up entirely.

The move that decides it is the one used on $0/0$ with a root in it, run in reverse.
Manufacture a fraction by multiplying by the conjugate over itself, then divide by the
dominant power in the ordinary way.
''',
                    "steps": [
                        {
                            "prompt": "Multiply $\\sqrt{x^{2}+3x}-x$ by its conjugate $\\sqrt{x^{2}+3x}+x$ and simplify the product completely. Write the result.",
                            "answer": "3x",
                            "placeholder": "a polynomial in x",
                            "hint": "$(A-B)(A+B) = A^{2}-B^{2}$, with $A = \\sqrt{x^{2}+3x}$ and $B = x$.",
                            "deconstruct": [
                                "$\\left(\\sqrt{x^{2}+3x}\\right)^{2} = x^{2}+3x$, since the quantity under the root is positive for large $x$.",
                                "$B^{2} = x^{2}$, so the difference is $(x^{2}+3x) - x^{2}$.",
                                "The $x^{2}$ terms cancel, which is the entire point of the manoeuvre.",
                            ],
                        },
                        {
                            "prompt": "The conjugate cannot be introduced for free, so divide by it as well. Write the original expression as the single fraction this produces.",
                            "answer": "\\frac{3x}{\\sqrt{x^{2}+3x}+x}",
                            "hint": "Numerator: the product you just simplified. Denominator: the conjugate itself.",
                            "deconstruct": [
                                "Multiplying by $\\dfrac{\\sqrt{x^{2}+3x}+x}{\\sqrt{x^{2}+3x}+x}$ multiplies by $1$, so nothing has changed.",
                                "That factor is legal for large $x$ because the denominator is then strictly positive, never zero.",
                            ],
                        },
                        {
                            "prompt": "Now divide numerator and denominator by $x$. Inside the root, $x$ must enter as $\\sqrt{x^{2}}$, which equals $x$ here because $x$ is heading to $+\\infty$. Write the resulting fraction.",
                            "answer": "\\frac{3}{\\sqrt{1+3/x}+1}",
                            "placeholder": "\\frac{3}{\\sqrt{\\ldots}+1}",
                            "hint": "$\\dfrac{\\sqrt{x^{2}+3x}}{x} = \\sqrt{\\dfrac{x^{2}+3x}{x^{2}}} = \\sqrt{1+\\dfrac{3}{x}}$, and $\\dfrac{x}{x} = 1$.",
                            "deconstruct": [
                                "Top: $3x/x = 3$.",
                                "Bottom, first term: bring the $x$ under the root as $\\sqrt{x^{2}}$ and combine, giving $\\sqrt{1+3/x}$.",
                                "Bottom, second term: $x/x = 1$.",
                            ],
                        },
                        {
                            "prompt": "The term $3/x$ tends to $0$ and every remaining piece has a limit of its own, so the laws finally apply. Write the value of the limit.",
                            "answer": "\\frac{3}{2}",
                            "hint": "The root tends to $\\sqrt{1+0} = 1$, so the denominator tends to $1+1$.",
                        },
                        {
                            "prompt": "Now the other end of the axis. For $x < 0$, write $\\sqrt{x^{2}}$ in terms of $x$ without using a modulus sign.",
                            "answer": "-x",
                            "hint": "The radical denotes the non-negative root, and when $x$ itself is negative it is $-x$ that is positive.",
                            "deconstruct": [
                                "$\\sqrt{x^{2}} = |x|$ for every real $x$; the square destroys the sign and the root cannot restore it.",
                                "For $x < 0$ the non-negative one of $x$ and $-x$ is $-x$.",
                                "Test it: at $x = -5$, $\\sqrt{25} = 5 = -(-5)$.",
                            ],
                        },
                    ],
                    "closing": r'''
So $\lim_{x\to\infty}\left(\sqrt{x^{2}+3x}-x\right) = \frac{3}{2}$: the
curve $y = \sqrt{x^{2}+3x}$ and the line $y = x$ separate for a while and then run
parallel at a fixed gap of $1.5$. Sampling agrees — at $x = 10^{6}$ the difference is
$1.49999\ldots$ — but sampling could never have distinguished a gap of $1.5$ from a gap
that closes very slowly, and the algebra does.

Nothing about $3$ was special. The same three lines give
$\lim_{x\to\infty}\left(\sqrt{x^{2}+kx}-x\right) = k/2$ for any constant $k$, which is
a formula worth recognising: the linear term inside the root becomes half of itself
outside it.

The last step is the guard on the other end. As $x \to -\infty$ the quantity $-x$ is
large and positive, so $\sqrt{x^{2}+3x} - x$ is a sum of two large positive things and
runs off to $+\infty$. The limit at $-\infty$ is not $-3/2$, and it is not $3/2$; there
is no finite limit at all. Every step of the working above assumed $\sqrt{x^{2}} = x$,
which is true at one end of the axis and false at the other, and forgetting that is the
single most common way this calculation goes wrong.
''',
                },
                {
                    "title": "Trapping sin(x)/x between two things that meet",
                    "minutes": 14,
                    "vars": ["x", "k", "L"],
                    "brief": r'''
The limit $\lim_{x\to 0}\frac{\sin x}{x}$ is $0/0$, and no factoring,
cancelling or rationalising touches it — there is no polynomial structure to exploit.
It is also not optional: it is the derivative of $\sin$ at the origin, and every
trigonometric derivative later in the course is built on it.

The route in is the squeeze, and the inequality it squeezes with comes from geometry.
In the unit circle, with $x$ in radians and $0 < x < \pi/2$, a triangle sits inside a
sector which sits inside a larger triangle, and comparing the three areas gives

$$\tfrac{1}{2}\sin x \;\le\; \tfrac{1}{2}x \;\le\; \tfrac{1}{2}\tan x,
\qquad\text{that is}\qquad \sin x \le x \le \tan x .$$

Take that inequality as given and turn it into the limit.

One note on typing, since several answers below contain a trigonometric function: the
checker reads plain function names, so enter them as `sin(x)`, `cos(x)` and `tan(x)`,
with the brackets and without a backslash.
''',
                    "steps": [
                        {
                            "prompt": "Before anything can be divided, write $\\tan(x)$ in terms of $\\sin(x)$ and $\\cos(x)$.",
                            "answer": "\\frac{sin(x)}{cos(x)}",
                            "hint": "The definition of the tangent, not an identity to be derived.",
                        },
                        {
                            "prompt": "Divide the chain $\\sin(x) \\le x \\le \\tan(x)$ through by $\\sin(x)$, which is strictly positive for $0 < x < \\pi/2$, so no inequality flips. The middle term becomes $x/\\sin(x)$ and the left becomes $1$. Write the right-hand bound.",
                            "answer": "\\frac{1}{cos(x)}",
                            "hint": "$\\dfrac{\\tan x}{\\sin x} = \\dfrac{\\sin x}{\\cos x}\\cdot\\dfrac{1}{\\sin x}$, and the sines cancel.",
                            "deconstruct": [
                                "Write the right-hand term as $\\dfrac{\\sin x}{\\cos x} \\div \\sin x$.",
                                "Dividing by $\\sin x$ is multiplying by $1/\\sin x$, so the $\\sin x$ factors cancel.",
                                "Only $1/\\cos x$ survives.",
                            ],
                        },
                        {
                            "prompt": "All three quantities in $1 \\le \\dfrac{x}{\\sin(x)} \\le \\dfrac{1}{\\cos(x)}$ are positive, and taking reciprocals of positive quantities reverses a chain. The reversed chain reads (lower bound) $\\le \\dfrac{\\sin(x)}{x} \\le 1$. Write that lower bound.",
                            "answer": "cos(x)",
                            "hint": "The reciprocal of $1/\\cos x$ is $\\cos x$, and it moves from the right-hand end to the left-hand end.",
                        },
                        {
                            "prompt": "Both outer bounds have limits as $x \\to 0$, and the squeeze theorem needs them to agree. Write the common value, which is therefore $\\lim_{x\\to 0}\\frac{\\sin(x)}{x}$.",
                            "answer": "1",
                            "hint": "$\\cos$ is continuous with $\\cos 0 = 1$, and the constant bound is $1$ already.",
                        },
                        {
                            "prompt": "Use it. Rewrite $\\dfrac{\\sin(5x)}{3x}$ as a constant multiplied by $\\dfrac{\\sin(5x)}{5x}$, then take the limit as $x \\to 0$. Write the limit.",
                            "answer": "\\frac{5}{3}",
                            "hint": "$\\dfrac{\\sin 5x}{3x} = \\dfrac{5}{3}\\cdot\\dfrac{\\sin 5x}{5x}$, and the second factor tends to $1$ because $5x \\to 0$.",
                            "deconstruct": [
                                "Multiply numerator and denominator by $5$: $\\dfrac{\\sin 5x}{3x} = \\dfrac{5\\sin 5x}{15x}$.",
                                "Regroup as $\\dfrac{5}{3}\\cdot\\dfrac{\\sin 5x}{5x}$.",
                                "As $x \\to 0$ the quantity $t = 5x$ also tends to $0$, so $\\dfrac{\\sin t}{t} \\to 1$.",
                            ],
                        },
                        {
                            "prompt": "A harder use. Multiply $\\dfrac{1-\\cos(x)}{x^{2}}$ top and bottom by $1+\\cos(x)$, and simplify the numerator with $1-\\cos^{2} = \\sin^{2}$. Write the whole fraction.",
                            "answer": "\\frac{sin(x)^{2}}{x^{2}(1+cos(x))}",
                            "placeholder": "\\frac{\\ldots}{x^{2}(1+cos(x))}",
                            "hint": "The numerator becomes $(1-\\cos x)(1+\\cos x) = 1-\\cos^{2}x$; the denominator picks up the same conjugate factor.",
                        },
                        {
                            "prompt": "Split that into $\\left(\\dfrac{\\sin(x)}{x}\\right)^{2}\\cdot\\dfrac{1}{1+\\cos(x)}$ — now every factor has a limit — and write $\\lim_{x\\to 0}\\dfrac{1-\\cos(x)}{x^{2}}$.",
                            "answer": "\\frac{1}{2}",
                            "hint": "The squared factor tends to $1^{2}$, and $1+\\cos 0 = 2$.",
                        },
                    ],
                    "closing": r'''
Three results have come out of one inequality:

$$\lim_{x\to 0}\frac{\sin x}{x} = 1, \qquad
\lim_{x\to 0}\frac{\sin (kx)}{x} = k, \qquad
\lim_{x\to 0}\frac{1-\cos x}{x^{2}} = \frac{1}{2}.$$

The middle one says the sine is indistinguishable from its argument near $0$ up to a
first-order factor, and the last says the cosine differs from $1$ by about
$\tfrac{1}{2}x^{2}$ — which is the first hint of Taylor's theorem, and the reason
$\cos x \approx 1 - x^{2}/2$ is worth memorising.

Two hypotheses were spent and both matter. **Radians**: the sector area is
$\tfrac{1}{2}x$ only in radians, and in degrees the first limit is $\pi/180$, not $1$.
**Positivity**: dividing the chain by $\sin x$ kept its direction only because $\sin x >
0$ on $(0,\pi/2)$, which is why the argument establishes the right-hand limit first.
The two-sided result follows because $\frac{\sin x}{x}$ is an even function, so the
left-hand side is a mirror image and gives the same value.

Where it stops: none of this survives being applied at a point other than $0$.
$\lim_{x\to\pi}\frac{\sin x}{x}$ is not $1$ — it is $0/\pi = 0$, by plain substitution,
because there is nothing indeterminate about it. The result is about the *coincidence*
of a zero in the numerator with a zero in the denominator, and that only happens at
the origin.
''',
                },
                {
                    "title": "From a sign change to a bracket you can shrink",
                    "minutes": 12,
                    "vars": ["x", "n", "f", "c"],
                    "brief": r'''
The cubic $f(x) = x^{3}-x-2$ has no rational root and no formula anyone wants to use.
The intermediate value theorem does not care: continuity plus two values of opposite
sign is enough to guarantee that a root exists, and the proof of the theorem is itself
an algorithm for finding it.

This derivation runs that algorithm by hand for two steps, then reads off the guarantee
it comes with — a bound on the error that is known before any function value is
computed.
''',
                    "steps": [
                        {
                            "prompt": "Take the bracket $[1,2]$. The bracketing test is a statement about the sign of one product. Compute $f(1)\\,f(2)$ for $f(x) = x^{3}-x-2$.",
                            "answer": "-8",
                            "hint": "$f(1) = 1-1-2$ and $f(2) = 8-2-2$; multiply them.",
                            "deconstruct": [
                                "$f(1) = 1^{3}-1-2 = -2$.",
                                "$f(2) = 2^{3}-2-2 = 4$.",
                                "$(-2)(4) = -8$, and a negative product is precisely what 'opposite signs' means.",
                            ],
                        },
                        {
                            "prompt": "The product is negative and $f$ is a polynomial, hence continuous on $[1,2]$, so a root exists inside. Write the midpoint of the bracket, which is where bisection looks next.",
                            "answer": "\\frac{3}{2}",
                            "hint": "Halfway between $1$ and $2$.",
                        },
                        {
                            "prompt": "Evaluate $f$ at that midpoint. Write $f(3/2)$ exactly, as a fraction.",
                            "answer": "-\\frac{1}{8}",
                            "hint": "$\\left(\\frac{3}{2}\\right)^{3} = \\frac{27}{8}$, then subtract $\\frac{3}{2}$ and $2$ over a common denominator of $8$.",
                            "deconstruct": [
                                "$\\left(\\frac{3}{2}\\right)^{3} = \\frac{27}{8}$.",
                                "$\\frac{3}{2} = \\frac{12}{8}$ and $2 = \\frac{16}{8}$.",
                                "$\\frac{27}{8}-\\frac{12}{8}-\\frac{16}{8} = -\\frac{1}{8}$, so the value is negative — small, but negative.",
                            ],
                        },
                        {
                            "prompt": "That value has the same sign as $f(1)$, so the sign change lies in the other half, $[3/2,\\,2]$. Write the width of this new bracket.",
                            "answer": "\\frac{1}{2}",
                            "hint": "The old bracket had width $1$ and the midpoint cut it in two.",
                        },
                        {
                            "prompt": "Each step halves the bracket, and the starting width here is $1$. Write the width after $n$ steps, as a function of $n$.",
                            "answer": "\\frac{1}{2^{n}}",
                            "placeholder": "a power of 2",
                            "hint": "One halving is $1/2$, two halvings are $1/4$; the pattern is a power.",
                        },
                        {
                            "prompt": "Ten decimal places are not needed; three are. Write the smallest whole number $n$ for which the bracket width $2^{-n}$ is at most $10^{-3}$.",
                            "answer": "10",
                            "hint": "$2^{9} = 512$ and $2^{10} = 1024$. Which is the first to exceed $1000$?",
                            "deconstruct": [
                                "The condition $2^{-n} \\le 10^{-3}$ is the same as $2^{n} \\ge 1000$.",
                                "$2^{9} = 512 < 1000$, so nine steps are not enough.",
                                "$2^{10} = 1024 \\ge 1000$, so ten steps suffice and nine do not.",
                            ],
                        },
                    ],
                    "closing": r'''
Two bisections have cut the root down to $[1.5, 1.75]$ — the second midpoint is
$1.75$, where $f = \frac{103}{64} \approx 1.609 > 0$, so the bracket becomes
$[1.5,\,1.75]$ — and the true root is $c \approx 1.52138$.

What makes this worth doing is the last two steps rather than the first four. The
error bound $2^{-n}$ does not depend on $f$: it is fixed by the geometry of halving, so
the cost of a given accuracy is known before the first evaluation, and the method
cannot diverge, stall or oscillate. That is a rare guarantee, and it is bought entirely
with the intermediate value theorem.

The price is speed. One binary digit per function evaluation means about $3.3$ steps
per decimal digit, and no amount of smoothness in $f$ makes it faster — bisection never
looks at how big $f$ is, only at its sign, so it throws away almost all the information
it collects. Newton's method in Module 9 uses that information and roughly doubles the
number of correct digits per step, in exchange for giving up the guarantee entirely.

Where the argument stops: the sign test detects a *crossing*, not a root. On
$f(x) = 1/x$ over $[-1,1]$ the endpoint values are $-1$ and $1$, the product is
negative, and bisection converges neatly to $0$ — which is a pole, not a root, and the
hypothesis that failed is continuity on the closed interval. And a root of even
multiplicity, such as the one $x^{2}$ has at the origin, produces no sign change at all
and is invisible to any bracketing method.
''',
                },
            ],
            "blanks": [
                {
                    "title": "A zero over zero, evaluated line by line",
                    "minutes": 9,
                    "caption": "the standard evaluation, with five steps removed",
                    "lang": "text",
                    "brief": r'''
A $0/0$ with a square root in the *denominator* rather than the numerator. The strategy
is unchanged — expose the common factor, cancel it on the punctured neighbourhood, then
substitute into what is left — but the conjugate now has to be applied downstairs.

Four of the missing pieces are algebra. One is the reason the cancellation is allowed
at all, which is the step that is usually performed silently and is the only step that
could be wrong.
''',
                    "listing": """Evaluate      lim  (x^2 - 9) / (sqrt(x + 1) - 2)      as  x -> 3
              ---


Step 0.  Substitute first, to find out which case this is.

     numerator      3^2 - 9          =  0
     denominator    sqrt(3 + 1) - 2  =  0

     so the form is ___ , and the quotient law does not apply.


Step 1.  The obstruction is the root downstairs.  Multiply top and
         bottom by C, the conjugate of the denominator:

     C  =  ___

              (x^2 - 9) * C
     ---------------------------------
          (sqrt(x+1) - 2) * C


Step 2.  The denominator is now a difference of two squares:

     (sqrt(x+1))^2 - 2^2  =  (x + 1) - 4  =  ___


Step 3.  Factor the numerator so that the same factor is visible
         on top:

     x^2 - 9  =  (x - 3)(x + 3)

     giving       (x - 3)(x + 3) * C
                  ---------------------
                        (x - 3)


Step 4.  Cancel the common factor (x - 3).  This is legal because
         ___ .

     leaving      (x + 3) * C


Step 5.  What is left is continuous at x = 3, so substitute x = 3,
         where C = sqrt(3 + 1) + 2 = 4:

     (3 + 3) * 4  =  ___
""",
                    "blanks": [
                        {
                            "prompt": "Both halves came out zero. Name the form.",
                            "hole": "?",
                            "opts": ["0", "0/0", "inf/inf", "undefined, so no limit exists"],
                            "a": 1,
                            "why": r"""
$0/0$ is a report about the shape of the expression, not a value: it says the quotient
law's hypotheses have failed and algebra is owed. Reading it as the number $0$ takes the
numerator's value for the quotient's, which would make every limit of this shape zero —
and this one is $24$. $\infty/\infty$ is the form for two pieces that grow without
bound, which is not what happened here. And being undefined at the point is no
obstruction whatsoever: a limit inspects only the punctured neighbourhood, so a hole is
the normal case rather than a failure.
""",
                        },
                        {
                            "prompt": "The conjugate of $\\sqrt{x+1}-2$.",
                            "hole": "?",
                            "opts": ["sqrt(x-1) + 2", "x + 1 - 4", "sqrt(x+1) + 2", "sqrt(x+1) - 2"],
                            "a": 2,
                            "why": r"""
A conjugate flips the sign between the two terms and changes nothing else, so
$\sqrt{x+1}-2$ pairs with $\sqrt{x+1}+2$; the product is
$\left(\sqrt{x+1}\right)^{2}-2^{2}$, which is what kills the root. Repeating the
expression unchanged squares it instead and leaves the root firmly in place. Moving the
sign inside the radical, as $\sqrt{x-1}$, changes the function rather than multiplying
by $1$. Writing $x+1-4$ is the *result* of the multiplication, not the thing multiplied
by.
""",
                        },
                        {
                            "prompt": "$(x+1)-4$, simplified.",
                            "hole": "?",
                            "opts": ["x - 3", "x + 5", "x - 4", "x + 3"],
                            "a": 0,
                            "why": r"""
$(x+1)-4 = x-3$, and the appearance of exactly the factor that the numerator also
carries is the whole reason the conjugate was worth introducing. Getting $x+5$ adds
where the algebra subtracts; $x-4$ forgets the $+1$ that came out of the root; $x+3$ is
the *other* factor of $x^{2}-9$, which survives the cancellation rather than performing
it.
""",
                        },
                        {
                            "prompt": "Why may $(x-3)$ be cancelled here?",
                            "hole": "?",
                            "opts": [
                                "a common factor may always be cancelled from a fraction",
                                "the numerator and the denominator both vanish at x = 3",
                                "x is never equal to 3 on the punctured neighbourhood a limit inspects",
                                "the limit is already known to exist",
                            ],
                            "a": 2,
                            "why": r"""
Cancelling divides by $x-3$, and division is legal only when that quantity is non-zero
— which is guaranteed here not by luck but by the definition of a limit, which examines
$0 < |x-3| < \delta$ and never $x = 3$ itself. The blanket claim that common factors
always cancel is false precisely at the point in question, and it is the belief that
turns this manoeuvre into a habit that occasionally destroys a genuine discontinuity.
Both halves vanishing is the reason a common factor *exists*, not the reason it may be
divided out. And the existence of the limit is the conclusion of the argument, so
assuming it here would be circular.
""",
                        },
                        {
                            "prompt": "$6 \\times 4$.",
                            "hole": "?",
                            "opts": ["12", "24", "0", "6"],
                            "a": 1,
                            "why": r"""
$(3+3)(\sqrt{4}+2) = 6 \times 4 = 24$, so the limit is $24$ — a perfectly ordinary
number produced by an expression that has no value at all at $x = 3$. Answering $12$
drops the $\sqrt{4} = 2$ and multiplies $6$ by the leftover $2$; answering $6$ keeps
only the polynomial factor and throws away the conjugate that the rationalisation put
there; answering $0$ reports the numerator's value at the point, which is the original
mistake the whole calculation exists to avoid.
""",
                        },
                    ],
                },
                {
                    "title": "Which side of the asymptote",
                    "minutes": 9,
                    "caption": "a sign analysis of a pole, one factor at a time",
                    "lang": "text",
                    "brief": r'''
A vanishing denominator is not by itself an asymptote, and an asymptote is not by itself
an answer: the two sides can run to opposite infinities. Both facts are settled by the
same routine — check the numerator, then track the sign of every factor as the point is
approached from one side.

The analysis below is written out for $f(x) = \dfrac{x+4}{x^{2}-4}$ at both of its bad
points. Five entries are missing.
''',
                    "listing": """f(x) = (x + 4) / (x^2 - 4) = (x + 4) / ((x - 2)(x + 2))

A zero denominator is not by itself an asymptote, so look at the
numerator at each bad point before deciding anything.

     at x =  2 :   numerator = 6 , nonzero   ->  vertical asymptote
     at x = -2 :   numerator = 2 , nonzero   ->  vertical asymptote

Contrast:  g(x) = (x^2 - 4) / (x - 2).  Its denominator vanishes at
x = 2 as well -- but so does its numerator, the factor (x - 2)
cancels, and what the graph of g has at x = 2 is instead ___ .


Back to f.  Approach x = 2 from the RIGHT   (test point x = 2.001):

     x + 4    ->    6.001       positive
     x + 2    ->    4.001       positive
     x - 2    ->   +0.001       positive and tiny
     f(x)     ->    6 / (tiny positive)     ->  ___
     f(2.001) =  1499.9 ...


Approach x = 2 from the LEFT    (test point x = 1.999):

     x + 4    ->    5.999       positive
     x + 2    ->    3.999       positive
     x - 2    ->   -0.001       ___ and tiny
     f(x)     ->    6 / (tiny negative)     ->  -inf
     f(1.999) = -1500.1 ...


Approach x = -2 from the RIGHT  (test point x = -1.999):

     x + 4    ->    2.001       positive
     x - 2    ->   -3.999       negative
     x + 2    ->   +0.001       positive and tiny
     f(x)     ->    2 / (tiny negative)     ->  ___
     f(-1.999) = -500.4 ...


Conclusion at x = 2:  the two sides disagree, so the two-sided
limit ___ .
""",
                    "blanks": [
                        {
                            "prompt": "For $g(x) = \\dfrac{x^{2}-4}{x-2}$, both halves vanish at $x=2$ and the factor cancels. What does the graph of $g$ have there?",
                            "hole": "?",
                            "opts": [
                                "a vertical asymptote, as for f",
                                "a hole, with the limit 4",
                                "a jump, with different one-sided limits",
                                "an ordinary point, with g(2) = 4",
                            ],
                            "a": 1,
                            "why": r"""
Cancelling gives $g(x) = x+2$ for every $x \neq 2$, so $g$ approaches $4$ from both
sides and the discontinuity is removable — a hole, not a pole. The difference from $f$
is entirely in the numerator: $f$ has $6 \neq 0$ over a vanishing denominator, which is
unbounded, while $g$ has $0/0$, which the cancellation resolves to a finite value. It is
not a jump, since the two one-sided limits agree. And it is not an ordinary point:
$g(2)$ is still $0/0$ and therefore undefined, which is exactly why the word
*removable* is doing work — the hole can be filled by defining $g(2) = 4$, but nobody
has filled it yet.
""",
                        },
                        {
                            "prompt": "A positive number over a tiny positive number.",
                            "hole": "?",
                            "opts": ["+inf", "-inf", "0", "6"],
                            "a": 0,
                            "why": r"""
Every factor is positive just to the right of $2$, so the quotient is positive and grows
without bound as the denominator shrinks: the one-sided limit is $+\infty$. The negative
infinity is what the *other* side gives, which is exactly why the side has to be tracked.
A limit of $0$ would need the denominator to grow, not shrink. And $6$ is the numerator's
value, which would be the answer only if the denominator tended to $1$.
""",
                        },
                        {
                            "prompt": "Just to the left of $2$, the factor $x-2$ is what?",
                            "hole": "?",
                            "opts": ["positive", "zero", "negative", "undefined"],
                            "a": 2,
                            "why": r"""
At $x = 1.999$ the quantity $x-2$ is $-0.001$: small in size but negative in sign, and it
is the sign that decides which infinity the quotient runs to. Calling it positive is the
single most common slip in this analysis, because "close to zero" gets read as "close to
zero from above". It is not zero — the limit never reaches the point — and it is
perfectly well defined; only the quotient is undefined at $x=2$.
""",
                        },
                        {
                            "prompt": "At $x = -1.999$: a positive numerator over a tiny negative denominator.",
                            "hole": "?",
                            "opts": ["+inf", "0", "-2", "-inf"],
                            "a": 3,
                            "why": r"""
Two of the three factors decide it: $x-2$ is near $-4$, negative, and $x+2$ is tiny and
positive, so the denominator is tiny and negative while the numerator is near $+2$. The
quotient is large and negative, so the limit is $-\infty$, and the sample value
$f(-1.999) = -500.4$ agrees. Answering $+\infty$ drops the sign of $x-2$, which is the
factor that is easy to ignore because it is nowhere near zero. There is nothing here
that tends to a finite value.
""",
                        },
                        {
                            "prompt": "The two sides at $x = 2$ give $+\\infty$ and $-\\infty$. So the two-sided limit...",
                            "hole": "?",
                            "opts": ["is +inf", "does not exist", "is 0", "is -inf"],
                            "a": 1,
                            "why": r"""
A two-sided limit exists only when both one-sided limits exist and agree, and here they
disagree as loudly as possible. Writing $\lim_{x\to 2} f(x) = +\infty$ would be a false
statement rather than a loose one: it claims $f$ exceeds every bound near $2$, and just
to the left $f$ is large and *negative*. Averaging the two sides to $0$ is not a
definition of anything — the function takes no values near $0$ anywhere close to $x=2$.
Both infinities are genuine, and each belongs to its own side.
""",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Reading a horizontal asymptote off the coefficients",
                    "minutes": 5,
                    "brief": r'''
The bottom of the ladder: one division by the dominant power and every term either
survives or dies. Nothing has to be derived first.
''',
                    "prompt": "What is $\\lim_{x\\to\\infty} f(x)$?",
                    "note": "A pure number, to three decimal places.",
                    "figure": "The function is $f(x) = \\dfrac{7x^{3}+2x}{2x^{3}-x^{2}+9}$. Both the "
                              "numerator and the denominator grow without bound as $x$ increases, so "
                              "the form is $\\infty/\\infty$ and the quotient law does not apply until "
                              "the expression has been rewritten.",
                    "given": [
                        {"label": "Numerator", "value": "$7x^{3}+2x$"},
                        {"label": "Denominator", "value": "$2x^{3}-x^{2}+9$"},
                        {"label": "Direction", "value": "$x \\to +\\infty$"},
                    ],
                    "aside": "Divide every term, top and bottom, by $x^{3}$.",
                    "answer": 3.5,
                    "tol": 0.005,
                    "unit": "",
                    "hint": "After dividing by $x^{3}$ the numerator reads $7 + 2/x^{2}$ and the "
                            "denominator reads $2 - 1/x + 9/x^{3}$. Every term with an $x$ underneath "
                            "goes to zero.",
                    "wrong": "If you answered $0$, the numerator's lower-order terms were kept and its "
                             "leading term dropped. If you answered $0.286$, the leading coefficients "
                             "were divided the wrong way round: it is numerator over denominator, "
                             "$7/2$, not $2/7$. At infinity only the highest power in each half "
                             "survives, so the $-x^{2}$ and the $+9$ contribute nothing.",
                    "why": "Dividing numerator and denominator by $x^{3}$ gives "
                           "$\\dfrac{7 + 2/x^{2}}{2 - 1/x + 9/x^{3}}$. Each of $2/x^{2}$, $1/x$ and "
                           "$9/x^{3}$ tends to $0$, and the denominator's limit is $2 \\neq 0$, so the "
                           "quotient law finally applies and the value is $7/2 = 3.5$. The general "
                           "rule is visible in the working: for equal degrees the limit is the ratio "
                           "of the leading coefficients, and the lower-order terms — which decide "
                           "everything at a finite point — decide nothing at infinity. Sampling "
                           "agrees slowly: at $x = 100$ the quotient is $3.5177$, still drifting down "
                           "towards $3.5$ like $1/x$.",
                },
                {
                    "title": "A trigonometric zero over zero",
                    "minutes": 7,
                    "brief": r'''
One rung up: the form is $0/0$, but there is no polynomial factor to cancel. The only
tool that reaches it is $\lim_{t\to 0}\frac{\sin t}{t} = 1$, applied twice — once to
each sine, with the argument arranged to match the denominator underneath it.
''',
                    "prompt": "What is $\\lim_{x\\to 0} g(x)$?",
                    "note": "A pure number, to four decimal places.",
                    "figure": "The function is $g(x) = \\dfrac{\\sin(7x)}{\\sin(3x)}$, defined for every "
                              "$x$ near $0$ except $x = 0$ itself, where both the numerator and the "
                              "denominator vanish. Angles are in radians.",
                    "given": [
                        {"label": "Numerator", "value": "$\\sin(7x)$"},
                        {"label": "Denominator", "value": "$\\sin(3x)$"},
                        {"label": "Known result", "value": "$\\lim_{t\\to 0} \\dfrac{\\sin t}{t} = 1$"},
                    ],
                    "aside": "Multiply the fraction above and below by $x$, then arrange each sine over "
                             "its own argument.",
                    "answer": 2.33333,
                    "tol": 0.0005,
                    "unit": "",
                    "hint": "Write $\\dfrac{\\sin 7x}{\\sin 3x} = \\dfrac{7}{3}\\cdot"
                            "\\dfrac{\\sin 7x}{7x}\\cdot\\dfrac{3x}{\\sin 3x}$ and take the three "
                            "limits separately.",
                    "wrong": "If you answered $1$, the two sines were cancelled against each other as "
                             "though $\\sin$ were a factor rather than a function — $\\sin(7x)$ is "
                             "not $7\\sin(x)$. If you answered $0.4286$, the ratio came out upside "
                             "down: $3/7$ rather than $7/3$.",
                    "why": "Insert the arguments each sine needs: "
                           "$\\dfrac{\\sin 7x}{\\sin 3x} = \\dfrac{7x}{3x}\\cdot"
                           "\\dfrac{\\sin 7x}{7x}\\cdot\\dfrac{3x}{\\sin 3x}$. As $x \\to 0$ both "
                           "$7x$ and $3x$ tend to $0$, so the second factor tends to $1$ and the third "
                           "to $1/1 = 1$, while the first is the constant $7/3$ for every $x \\neq 0$. "
                           "Every piece now has a limit and no denominator's limit is zero, so the "
                           "laws apply and the answer is $7/3 = 2.3333$. Sampling confirms it: at "
                           "$x = 0.001$ the quotient reads $2.33332$. The result also says something "
                           "worth remembering — near the origin a sine is indistinguishable from "
                           "its argument, so a ratio of sines behaves like the ratio of the arguments.",
                },
                {
                    "title": "The end of the axis where the sign flips",
                    "minutes": 8,
                    "brief": r'''
The same division by the dominant power as the first rung, at the other end of the axis
and with a square root in the way. The arithmetic is easy and the sign is not: this is
the case that catches people who have done fifty of these at $+\infty$.
''',
                    "prompt": "What is $\\lim_{x\\to-\\infty} h(x)$?",
                    "note": "A pure number, to three decimal places. Mind the sign.",
                    "figure": "The function is $h(x) = \\dfrac{\\sqrt{9x^{2}+4}}{2x+1}$. The numerator is "
                              "a square root, so it is positive for every $x$; the denominator is "
                              "negative once $x < -1/2$. The limit is taken as $x$ runs off to the "
                              "left.",
                    "given": [
                        {"label": "Numerator", "value": "$\\sqrt{9x^{2}+4}$"},
                        {"label": "Denominator", "value": "$2x+1$"},
                        {"label": "Direction", "value": "$x \\to -\\infty$"},
                    ],
                    "aside": "To take $x$ inside a square root it must be written as $\\sqrt{x^{2}}$, "
                             "and $\\sqrt{x^{2}} = -x$ when $x$ is negative.",
                    "answer": -1.5,
                    "tol": 0.005,
                    "unit": "",
                    "hint": "Divide top and bottom by $x$. Dividing the root by $x$ means dividing by "
                            "$-\\sqrt{x^{2}}$, which leaves a minus sign outside the radical.",
                    "wrong": "If you answered $+1.5$, the numerator was divided by $x$ as though "
                             "$\\sqrt{x^{2}} = x$. That identity holds at the right-hand end of the "
                             "axis and fails at this one, and the failure is easy to see without any "
                             "algebra: the numerator is positive and the denominator is negative for "
                             "large negative $x$, so the quotient cannot be positive.",
                    "why": "For $x < 0$ we have $x = -\\sqrt{x^{2}}$, so "
                           "$\\dfrac{\\sqrt{9x^{2}+4}}{x} = -\\sqrt{\\dfrac{9x^{2}+4}{x^{2}}} = "
                           "-\\sqrt{9 + \\dfrac{4}{x^{2}}}$, while $\\dfrac{2x+1}{x} = 2 + "
                           "\\dfrac{1}{x}$. The quotient is therefore "
                           "$\\dfrac{-\\sqrt{9+4/x^{2}}}{2+1/x}$, and letting $x \\to -\\infty$ sends "
                           "both small terms to zero, leaving $-\\sqrt{9}/2 = -3/2 = -1.5$. Sampling "
                           "agrees: at $x = -1000$ the numerator is $3000.0007$, the denominator is "
                           "$-1999$, and the quotient is $-1.50075$. At the other end the same "
                           "function tends to $+1.5$, so its graph has two different horizontal "
                           "asymptotes.",
                },
                {
                    "title": "Choosing the constant that fixes the gap",
                    "minutes": 10,
                    "brief": r'''
The top of the ladder: the number asked for cannot be evaluated, because it is not the
value of anything yet. Derive the limit as a formula in the unknown constant first,
then solve the equation that formula produces.

The expression is an $\infty-\infty$, so the conjugate has to come out before any
division by the dominant power is possible.
''',
                    "prompt": "For which value of $k$ does the limit equal $5$?",
                    "note": "A pure number, to two decimal places.",
                    "figure": "Let $k > 0$ and consider $\\lim_{x\\to\\infty}\\left(\\sqrt{4x^{2}+kx} "
                              "- 2x\\right)$. Both terms grow without bound, so the form is "
                              "$\\infty-\\infty$, which settles nothing on its own: depending on $k$ "
                              "the gap between the curve and the line could close, stay fixed, or "
                              "grow. Find the $k$ that makes the gap settle at exactly $5$.",
                    "given": [
                        {"label": "Expression", "value": "$\\sqrt{4x^{2}+kx}-2x$"},
                        {"label": "Direction", "value": "$x \\to +\\infty$"},
                        {"label": "Required limit", "value": "$5$"},
                    ],
                    "aside": "Multiply by $\\dfrac{\\sqrt{4x^{2}+kx}+2x}{\\sqrt{4x^{2}+kx}+2x}$, then "
                             "divide numerator and denominator by $x$.",
                    "answer": 20.0,
                    "tol": 0.05,
                    "unit": "",
                    "hint": "The conjugate leaves $\\dfrac{kx}{\\sqrt{4x^{2}+kx}+2x}$. Dividing by $x$ "
                            "turns that into $\\dfrac{k}{\\sqrt{4+k/x}+2}$, whose limit is a simple "
                            "multiple of $k$. Set it equal to $5$.",
                    "wrong": "If you answered $10$, the limit was taken to be $k/2$ — that is the "
                             "answer for $\\sqrt{x^{2}+kx}-x$, where the leading coefficient inside "
                             "the root is $1$. Here it is $4$, so the root contributes $2$ rather than "
                             "$1$ to the denominator and the limit is $k/4$. If you answered $5$, the "
                             "conjugate step was skipped and the constant read straight off the "
                             "target.",
                    "why": "Multiplying by the conjugate over itself gives "
                           "$\\dfrac{(4x^{2}+kx)-4x^{2}}{\\sqrt{4x^{2}+kx}+2x} = "
                           "\\dfrac{kx}{\\sqrt{4x^{2}+kx}+2x}$. Dividing top and bottom by $x$, and "
                           "taking $x = \\sqrt{x^{2}}$ inside the root as is legal for $x > 0$, gives "
                           "$\\dfrac{k}{\\sqrt{4+k/x}+2}$. As $x \\to \\infty$ the term $k/x$ vanishes, "
                           "the root tends to $2$, and the limit is $\\dfrac{k}{4}$. Setting "
                           "$\\dfrac{k}{4} = 5$ gives $k = 20$. Check it numerically: with $k = 20$ "
                           "and $x = 10^{6}$, $\\sqrt{4\\times 10^{12}+2\\times 10^{7}} - 2\\times "
                           "10^{6} = 4.99999\\ldots$, and the convergence is from below like $1/x$.",
                },
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
                "A two-sided limit is required: one-sided quotients that disagree mean no derivative, as at the corner of `|x|`",
                "Differentiability implies continuity; the converse is false",
                "Forward difference: f'(x) = (f(x+h) - f(x))/h + O(h)",
                "Central difference: f'(x) = (f(x+h) - f(x-h))/(2h) + O(h^2)",
                "Taylor expansion is where both error terms come from",
                "Observed order p from a pair of steps: p = log(e1/e2) / log(h1/h2)",
                "Richardson extrapolation cancels the leading error term and buys two orders",
                "Roundoff sets a floor: shrinking h forever makes the answer worse",
                "A difference formula returns a number whether or not the derivative exists",
            ],
            "read": [
                {
                    "title": "A slope for something that is not straight",
                    "minutes": 11,
                    "body": r"""
A car covers $120$ kilometres in two hours. Its average speed over the journey is
$60$ km/h, and that number came out of an ordinary division: distance over time. Now
ask what the speedometer read at the instant $t = 1$. The same division gives nothing,
because the distance covered in an instant is zero and the time taken is zero, and
$0/0$ is not a number. It is the report, from Module 2, that a quotient law has been
applied where its hypotheses fail, and that some algebra is owed.

That gap is the whole problem this module solves. Every rate anyone can actually
measure is an average over an interval. Every rate anyone actually wants is at a
point. The bridge between them is a limit, and it holds precisely because the $0/0$
form is a question rather than a dead end.

## Secants, and the one that cannot be drawn

Fix a function $f$ and a point $a$ where $f$ is defined. Pick a second point at
distance $h$, namely $a+h$. The straight line through $(a, f(a))$ and
$(a+h, f(a+h))$ is a *secant*, and its slope is an honest division of a rise by a run:

$$Q(h) \;=\; \frac{f(a+h) - f(a)}{h}.$$

This is the **difference quotient**, and it is the average rate of change of $f$
across the interval between $a$ and $a+h$. It is defined for every $h$ except $h = 0$
— which is exactly the value we want.

Watch the geometry as $h$ shrinks. The second point slides along the curve towards the
first, and the secant pivots about $(a, f(a))$. If the curve is smooth there, the
secants settle down onto one particular line: the tangent. If the curve has a kink
there, they do not settle onto anything, because the secants coming from the left
approach one line and those from the right approach another.

So the object of interest, $Q$, is a perfectly ordinary function of $h$ with a hole at
the origin. Module 1 said what to do with those. Do not evaluate at the hole. Take a
limit into it.

## The definition

$$f'(a) \;=\; \lim_{h \to 0} \frac{f(a+h) - f(a)}{h},$$

when that limit exists. If it does, $f$ is **differentiable** at $a$ and the number
$f'(a)$ is its derivative there. Substituting $x = a + h$ gives the same statement in
the other common form,

$$f'(a) \;=\; \lim_{x \to a} \frac{f(x) - f(a)}{x - a},$$

which is sometimes more convenient and never says anything different.

Three features are worth reading off before any use is made of it. The limit is
**two-sided**: $h$ approaches zero through positive and negative values alike, and both
must give the same answer. Unlike a general limit, this one **does care about the value
at the point**, because $f(a)$ sits inside the quotient — so $f$ must at least be
defined at $a$. And the limit **may fail**; differentiability is a property a function
can lack, not a guarantee that comes free with being a function.

## Worked: a quadratic, at every point at once

Take $f(x) = x^{2} - 3x$ and compute $f'(x)$ at a general point $x$, so that one
calculation serves every point.

First expand the shifted value:

$$f(x+h) = (x+h)^{2} - 3(x+h) = x^{2} + 2xh + h^{2} - 3x - 3h.$$

Subtract $f(x) = x^{2} - 3x$. The $x^{2}$ and the $-3x$ cancel, leaving

$$f(x+h) - f(x) = 2xh + h^{2} - 3h.$$

Every term carries a factor of $h$, which is not luck: the numerator vanishes at
$h = 0$, so by the factor theorem $h$ divides it. Divide by $h$, which is legal because
the limit examines only $0 < |h| < \delta$ and never $h = 0$:

$$\frac{f(x+h) - f(x)}{h} = 2x + h - 3 \qquad (h \neq 0).$$

What is left is a polynomial in $h$, continuous everywhere, so its limit is its value:

$$f'(x) = \lim_{h \to 0}\,(2x + h - 3) = 2x - 3.$$

Check the machinery against arithmetic at $x = 2$, where the formula claims $f'(2) = 1$.
We have $f(2) = 4 - 6 = -2$ and $f(2.001) = 4.004001 - 6.003 = -1.998999$, so the
difference quotient at $h = 0.001$ is $0.001001/0.001 = 1.001$. The formula
$2x + h - 3$ predicts $4 + 0.001 - 3 = 1.001$ exactly, and the excess over $1$ is the
$h$ that has not yet been sent to zero. That excess is the entire subject of the next
reading.

One more thing falls out for free. Setting $2x - 3 = 0$ gives $x = 1.5$, and that is
the vertex of the parabola. A derivative of zero at a point where the graph turns is
not a coincidence; it is Module 10.

## Worked: the corner that has no slope

Now the case people get wrong. Take $f(x) = |x|$ at $a = 0$:

$$Q(h) = \frac{|0 + h| - |0|}{h} = \frac{|h|}{h}.$$

For $h > 0$ we have $|h| = h$, so $Q(h) = 1$. For $h < 0$ we have $|h| = -h$, so
$Q(h) = -1$. Therefore

$$\lim_{h \to 0^{+}} Q(h) = 1, \qquad \lim_{h \to 0^{-}} Q(h) = -1,$$

the two one-sided limits disagree, the two-sided limit does not exist, and $f'(0)$ does
not exist.

Nothing has gone wrong with the arithmetic. Every line is exact, and $Q$ is not even
close to being badly behaved: it takes only the two values $\pm 1$. What fails is the
agreement of the sides, which Module 1 made the price of a two-sided limit.

This is the case that catches people, and it is worth saying why it is tempting. The
function $|x|$ looks harmless. It is continuous everywhere. Its graph is drawn without
lifting the pen. Away from the origin its slope is perfectly well defined, $-1$ on the
left and $+1$ on the right. So the instinct is to split the difference and answer $0$,
or to note that the graph is fine 'almost everywhere' and wave the point through. Worse,
a machine asked for the symmetric quotient $(|h| - |-h|)/(2h)$ returns
$(h - h)/(2h) = 0$ at every step size, confidently and forever. None of that makes
$f'(0)$ exist. Zero is simply what a symmetric formula returns when it cannot tell.

## Two mistakes worth naming

The first is substituting $h = 0$ too early. In the quadratic above, doing it at the
second line gives $0/0$, and the calculation stops. The definition explicitly excludes
$h = 0$; the point of the limit is to reach that value without ever evaluating there.

The second is the mirror image: cancelling the $h$ and then worrying about whether that
was allowed. It was, and for the reason Module 2 gave for cancelling $(x-3)$ from a
$0/0$ quotient — not because common factors always cancel, which is false exactly at
the point in question, but because a limit inspects a punctured neighbourhood on which
$h$ is guaranteed non-zero. Getting the licence right matters, because the same
manoeuvre performed without it destroys genuine discontinuities.

There is a third, and it is the reason this module has three more readings. Writing

$$f'(a) \;\approx\; \frac{f(a+h) - f(a)}{h} \quad\text{with } h \text{ small}$$

and stopping there is not a derivative. It is a difference quotient with the limit left
out, and how far apart those two numbers are is a question with a precise answer.

## Differentiable implies continuous, and not the other way

**Theorem.** If $f'(a)$ exists then $f$ is continuous at $a$.

*Proof.* For $x \neq a$ write the identity

$$f(x) - f(a) \;=\; \frac{f(x) - f(a)}{x - a}\cdot (x - a),$$

which is true because the $(x-a)$ cancels. As $x \to a$ the first factor tends to
$f'(a)$ — that is the definition, in its $x$-form — and the second tends to $0$. Both
factors have limits, so the product law applies:

$$\lim_{x \to a}\,(f(x) - f(a)) = f'(a) \cdot 0 = 0,$$

that is, $\lim_{x \to a} f(x) = f(a)$, which is continuity at $a$.

Note where the hypothesis was spent: the product law needed the first factor to have a
limit, and that is precisely the assumption that $f'(a)$ exists.

The converse is false, and $|x|$ at $0$ is the counterexample: continuous, not
differentiable. Continuity says the graph does not tear. Differentiability says it also
does not kink. The second is strictly stronger.

## Where it stops

The limit defining $f'(a)$ can fail in three distinct ways, and they look different on
a graph.

A **corner**, as at $|x|$ at the origin: both one-sided limits exist, are finite, and
disagree. A **vertical tangent**, as at $f(x) = x^{1/3}$ at the origin, where

$$Q(h) = \frac{h^{1/3} - 0}{h} = h^{-2/3},$$

which is $100$ at $h = 10^{-3}$ and $10^{4}$ at $h = 10^{-6}$: the two sides agree, but
they agree on $+\infty$, which is not a number, so there is no derivative even though
the picture has a perfectly good vertical tangent line. And a **discontinuity** of any
kind, which the theorem above rules out immediately: no continuity, no derivative, and
no amount of smoothness elsewhere repairs it.

One last caution about what the definition does *not* say. It is a statement about a
single point. A function can be differentiable at exactly one point and nowhere else —
take $f(x) = x^{2}$ for rational $x$ and $f(x) = 0$ for irrational $x$, which is
differentiable at the origin, with $f'(0) = 0$, and is not even continuous anywhere
else. Every convenient theorem later in the course, from the mean value theorem to
Newton's method, therefore asks for differentiability on an *interval*, not at a point,
and says so in its hypotheses.

The definition is the honest object. It is also, as an instrument, useless: no machine
can take $h \to 0$. It can only choose an $h$ and divide. What that choice costs is the
next reading.
""",
                },
                {
                    "title": "The error you pay for choosing an h",
                    "minutes": 12,
                    "body": r"""
The definition says to send $h$ to zero. A machine cannot do that. It can pick one
value of $h$, evaluate $f$ twice and divide, giving

$$D_{+}(h) \;=\; \frac{f(x+h) - f(x)}{h},$$

the **forward difference**. The question this reading answers is how wrong that number
is, and the answer is not 'a bit'. It is a formula — and the formula is far more useful
than any single number, because it says how the wrongness responds to $h$, which is the
only lever available.

## Taylor's theorem, in the form actually used

Suppose $f$ is twice continuously differentiable on an interval containing $x$ and
$x+h$. Then there is a point $\xi$ strictly between them with

$$f(x+h) \;=\; f(x) + h\,f'(x) + \frac{h^{2}}{2}f''(\xi).$$

The location of $\xi$ is unknown and does not need to be known: all that is used is
that $f''(\xi)$ is no larger than whatever bounds $f''$ on the interval. When more
derivatives exist, more terms can be taken, and it is convenient to write the version
with everything evaluated at $x$:

$$f(x+h) \;=\; f(x) + h f'(x) + \frac{h^{2}}{2}f''(x) + \frac{h^{3}}{6}f'''(x) + \frac{h^{4}}{24}f''''(x) + \cdots$$

The coefficient of $h^{k}$ is the $k$th derivative over $k!$.

## The forward difference and its error

Take the two-term version, subtract $f(x)$ and divide by $h$:

$$\frac{f(x+h) - f(x)}{h} \;=\; f'(x) + \frac{h}{2}f''(\xi).$$

That is an equation, not an approximation. The forward difference is the derivative
plus a term that is exactly $\tfrac{h}{2}f''(\xi)$ for some interior $\xi$. Writing
$M_{2}$ for a bound on $|f''|$ near $x$,

$$|D_{+}(h) - f'(x)| \;\le\; \frac{M_{2}}{2}\,h .$$

The error is proportional to the first power of $h$: the rule is **first order**, and
halving $h$ halves the error. The bound is also a prediction with a sign, because
$f''(\xi) \approx f''(x)$ for small $h$: the leading error is about
$\tfrac{h}{2}f''(x)$, so a forward difference overestimates the derivative where the
curve is convex and underestimates it where it is concave.

## Checking that against arithmetic

Take $f = \sin$ at $x = 1$, where the exact derivative is $\cos 1 = 0.5403023059$.

| $h$ | $D_{+}(h)$ | error |
| --- | --- | --- |
| $0.4$ | $0.3599468630$ | $-0.1803554429$ |
| $0.2$ | $0.4528405058$ | $-0.0874618001$ |
| $0.1$ | $0.4973637525$ | $-0.0429385533$ |
| $0.05$ | $0.5190448157$ | $-0.0212574901$ |

Successive error ratios are $2.062$, $2.037$, $2.020$: each halving of $h$ halves the
error, converging on a factor of exactly $2$. That is first order, observed.

The theory does better than the trend. At $x = 1$ the second derivative is
$f''(1) = -\sin 1 = -0.8414710$, so the leading term predicts an error of
$-0.04207355$ at $h = 0.1$, while the measured error is $-0.04293855$ — a gap of about
two per cent. The gap is the next term. Adding
$\tfrac{h^{2}}{6}f'''(1) = \tfrac{0.01}{6}(-0.5403023) = -0.00090050$
gives $-0.04297405$, and adding
$\tfrac{h^{3}}{24}f''''(1) = \tfrac{0.001}{24}(0.8414710) = +0.00003506$
gives $-0.04293899$. The measured error is $-0.04293855$. Six digits, from
three terms of an expansion, before the calculation was run.

## The central difference: cancelling the $h$ term

The expansion is available in the other direction too. Replacing $h$ by $-h$ flips the
sign of every odd power:

$$f(x-h) \;=\; f(x) - h f'(x) + \frac{h^{2}}{2}f''(x) - \frac{h^{3}}{6}f'''(x) + \cdots$$

Subtract this from the forward expansion. The $f(x)$ terms cancel, the $f''$ terms
cancel because they are identical in both, and the odd terms double:

$$f(x+h) - f(x-h) \;=\; 2h f'(x) + \frac{h^{3}}{3}f'''(x) + \cdots$$

Divide by $2h$ to get the **central difference**:

$$D_{0}(h) \;=\; \frac{f(x+h) - f(x-h)}{2h} \;=\; f'(x) + \frac{h^{2}}{6}f'''(x) + O(h^{4}).$$

The $f''$ term did not get smaller. It was *annihilated*, by the symmetry of the two
sample points about $x$. That is the whole reason the central difference is better, and
it costs nothing extra in theory — though it does cost in practice, since it needs two
fresh evaluations while the forward difference needs one fresh evaluation plus an
$f(x)$ you may already have from somewhere else.

The error bound is now $|D_{0}(h) - f'(x)| \le \tfrac{M_{3}}{6}h^{2}$ with
$M_{3}$ a bound on $|f'''|$. Second order: halve $h$ and the error falls by four.

| $h$ | $D_{0}(h)$ | error |
| --- | --- | --- |
| $0.4$ | $0.5260090707$ | $-0.0142932351$ |
| $0.2$ | $0.5367074877$ | $-0.0035948182$ |
| $0.1$ | $0.5394022522$ | $-0.0009000537$ |
| $0.05$ | $0.5400772080$ | $-0.0002250978$ |

Ratios $3.976$, $3.994$, $3.999$. And the leading term predicts
$\tfrac{h^{2}}{6}f'''(1) = -0.09005\,h^{2}$, which at $h = 0.1$ is $-0.00090050$
against a measured $-0.00090005$.

Notice how much the order buys. At $h = 0.05$ the forward difference is wrong in the
second decimal place and the central difference in the fourth, from the same
$f$ and comparable work.

## Measuring the order instead of trusting it

Suppose the error obeys $e(h) = C h^{p}$ for some unknown constant $C$ and unknown
order $p$. Run the rule at two steps and form both errors. Then

$$\frac{e_{1}}{e_{2}} = \left(\frac{h_{1}}{h_{2}}\right)^{p}
\quad\Rightarrow\quad
p = \frac{\log(e_{1}/e_{2})}{\log(h_{1}/h_{2})}.$$

The unknown $C$ divides out, which is what makes the measurement possible; and the base
of the logarithm cancels, because it appears twice.

Apply it to the central-difference table at $h_{1} = 0.2$ and $h_{2} = 0.1$:
$e_{1}/e_{2} = 0.0035948182/0.0009000537 = 3.99400$ and $h_{1}/h_{2} = 2$, so

$$p = \frac{\log 3.99400}{\log 2} = 1.9978.$$

The same two steps applied to the forward-difference table give $p = 1.026$. The
numbers are not exactly $2$ and $1$ because the neglected terms are not exactly zero at
these step sizes; the reading is a diagnosis, not a proof.

One thing the calculation quietly requires: the *exact* answer, to form the errors at
all. So the observed order is a check you run on a problem whose answer you already
know, in order to earn the right to trust the rule on one whose answer you do not.

## The mistake

Two of them, and the second is expensive.

The first is reading $O(h^{2})$ as a promise about a particular $h$. It is a statement
about a limit — about how the error *changes* — not about how big the error is. At
$h = 0.4$ the second-order central difference on $\sin$ is wrong in the second decimal
place. Second order is not a synonym for accurate.

The second is assuming an order without checking the smoothness that paid for it. The
$h^{3}$ term in the subtraction was written down only because $f'''$ exists and is
bounded near $x$. Remove that hypothesis and the cancellation of the $f''$ terms still
happens, but nothing at all can be said about what is left.

## Where it stops

Take $f(x) = x|x|$, which is $x^{2}$ for $x \ge 0$ and $-x^{2}$ for $x < 0$, and
differentiate it at the origin. It is smoother than it looks: $f'(x) = 2|x|$ exists
everywhere and is continuous, so $f$ is continuously differentiable, and $f'(0) = 0$.
But $f''(x) = 2$ for $x > 0$ and $-2$ for $x < 0$, so $f''(0)$ does not exist, and
$f'''$ certainly does not.

Now run the central difference at $x = 0$. Here $f(h) = h^{2}$ and $f(-h) = -h^{2}$, so

$$D_{0}(h) = \frac{h^{2} - (-h^{2})}{2h} = \frac{2h^{2}}{2h} = h .$$

The error is $|h - 0| = h$, exactly, at every step size. Halving $h$ halves the error
and never quarters it, and the observed order comes out at exactly $1$. There is no
rounding involved here and no asymptotic regime still to be reached: the second-order
claim is simply false at this point, and the hypothesis that failed is the existence of
$f'''$ — indeed of $f''$.

The sharper failure is the one from the previous reading. At $f(x) = |x|$ and $x = 0$,

$$D_{0}(h) = \frac{|h| - |-h|}{2h} = \frac{h - h}{2h} = 0$$

for every $h > 0$. The rule returns $0$, at every step size, with no wobble to suggest
anything is wrong, and the observed order is not even computable because the error
never changes. Yet $f'(0)$ does not exist. A difference formula cannot detect its own
hypotheses. It will always return a number, and the number means nothing unless the
smoothness is there to be had. That is why the derivative was defined as a limit first
and computed second, and it is the single most important sentence in this module.

Both error terms shrink without limit as $h$ shrinks, which suggests taking $h$ as
small as the machine will allow. The next reading is about why that is the worst thing
you can do.
""",
                },
                {
                    "title": "The floor that arithmetic puts under h",
                    "minutes": 12,
                    "body": r"""
Everything in the last reading pushed one way: the truncation error of a forward
difference is bounded by $M_{2}h/2$, so shrink $h$. Here is what actually happens when
you do. The rule is the forward difference on $f = \sin$ at $x = 1$, in ordinary
double-precision arithmetic, against the exact $\cos 1 = 0.5403023059$.

| $h$ | $D_{+}(h)$ | error |
| --- | --- | --- |
| $10^{-1}$ | $0.497363752535$ | $4.29 \times 10^{-2}$ |
| $10^{-2}$ | $0.536085981012$ | $4.22 \times 10^{-3}$ |
| $10^{-3}$ | $0.539881480360$ | $4.21 \times 10^{-4}$ |
| $10^{-4}$ | $0.540260231419$ | $4.21 \times 10^{-5}$ |
| $10^{-5}$ | $0.540298098506$ | $4.21 \times 10^{-6}$ |
| $10^{-6}$ | $0.540301885121$ | $4.21 \times 10^{-7}$ |
| $10^{-7}$ | $0.540302264040$ | $4.18 \times 10^{-8}$ |
| $10^{-8}$ | $0.540302302898$ | $2.97 \times 10^{-9}$ |
| $10^{-9}$ | $0.540302358409$ | $5.25 \times 10^{-8}$ |
| $10^{-10}$ | $0.540302247387$ | $5.85 \times 10^{-8}$ |
| $10^{-11}$ | $0.540301137164$ | $1.17 \times 10^{-6}$ |
| $10^{-12}$ | $0.540345546085$ | $4.32 \times 10^{-5}$ |
| $10^{-14}$ | $0.544009282066$ | $3.71 \times 10^{-3}$ |
| $10^{-16}$ | $0.000000000000$ | $5.40 \times 10^{-1}$ |

Read down the error column. It falls by a factor of ten per row, exactly as first order
predicts, all the way to about $h = 10^{-8}$. Then it turns round and climbs, and by
$h = 10^{-16}$ the rule returns $0$ and the answer is wrong in the first digit. Taking
$h$ towards zero, which is what the definition instructs, destroys the calculation.

The truncation theory is not wrong. It is incomplete, because it assumed the arithmetic
was exact.

## Subtractive cancellation

A double-precision number carries about $16$ significant decimal digits. The spacing
between $1$ and its neighbour is the machine epsilon,
$\epsilon \approx 2.22\times10^{-16}$, and the stored value of $f(x)$ differs from the
true one by up to roughly $\epsilon|f(x)|$ — plus whatever error the routine computing
$f$ has of its own.

Now look at the numerator $f(x+h) - f(x)$ when $h$ is small. At $h = 10^{-8}$ the
numbers $\sin(1.00000001)$ and $\sin(1)$ agree in their first eight digits. Those eight
digits cancel in the subtraction. What survives is carried entirely by the last eight
digits of each operand — which are the digits the representation is least sure of. The
subtraction itself is exact; what it does is throw away the trustworthy digits and
promote the doubtful ones. That is **subtractive cancellation**.

Quantitatively: write $\delta$ for the absolute error in a stored function value, so
$\delta \approx \epsilon|f|$ here. The numerator inherits up to $2\delta$, and the
division by $h$ multiplies that by $1/h$. So the rounding contribution to the answer is
up to $2\delta/h$, which grows without bound as $h$ shrinks.

## The total error curve, and its minimum

Add the two effects:

$$E(h) \;\le\; \frac{M_{2}}{2}h \;+\; \frac{2\delta}{h}.$$

One term falls linearly and one rises like $1/h$, so the sum has a minimum. Find it:

$$E'(h) = \frac{M_{2}}{2} - \frac{2\delta}{h^{2}} = 0
\quad\Rightarrow\quad
h^{2} = \frac{4\delta}{M_{2}}
\quad\Rightarrow\quad
h_{*} = 2\sqrt{\frac{\delta}{M_{2}}},$$

and substituting back gives
$E(h_{*}) = \sqrt{M_{2}\delta} + \sqrt{M_{2}\delta} = 2\sqrt{M_{2}\delta}$.
The two contributions are equal at the optimum, which is a
useful check on any such calculation.

Two facts are worth carrying away. The best step is the **square root** of the accuracy
of the function values, not the accuracy you want. And the best error attainable is also
about the square root of $\delta$ — so a forward difference on double-precision data
buys about eight correct digits out of sixteen, and no choice of $h$ buys more.

Test it on the table. Here $\delta \approx \epsilon \sin 1 \approx 1.87\times10^{-16}$
and $M_{2} = |{-\sin 1}| = 0.8415$, so

$$h_{*} = 2\sqrt{\frac{1.87\times10^{-16}}{0.8415}} = 2\sqrt{2.22\times10^{-16}}
\approx 3.0\times10^{-8},
\qquad E(h_{*}) \approx 2.5\times10^{-8}.$$

The table's best row is $h = 10^{-8}$, one grid step below the predicted $3\times10^{-8}$,
with an error of $3.0\times10^{-9}$, about eight times better than the bound. Both
discrepancies are expected: the table only samples powers of ten, and the bound assumes
every rounding error takes its worst value with the worst sign simultaneously, which
they do not.

## The central difference has a different floor

The same accounting, with the numerator error still $2\delta$ but the divisor now $2h$,
gives a rounding term of $\delta/h$, against a truncation term of $M_{3}h^{2}/6$:

$$E(h) \;\le\; \frac{M_{3}}{6}h^{2} + \frac{\delta}{h},
\qquad
E'(h) = \frac{M_{3}}{3}h - \frac{\delta}{h^{2}} = 0
\quad\Rightarrow\quad
h_{*} = \left(\frac{3\delta}{M_{3}}\right)^{1/3}.$$

For $\sin$ at $1$, with $M_{3} = |{-\cos 1}| = 0.5403$, that is
$(1.04\times10^{-15})^{1/3} \approx 1.0\times10^{-5}$. And here is the
central-difference column of the same experiment:

| $h$ | error |
| --- | --- |
| $10^{-3}$ | $9.00 \times 10^{-8}$ |
| $10^{-4}$ | $9.00 \times 10^{-10}$ |
| $10^{-5}$ | $1.11 \times 10^{-11}$ |
| $10^{-6}$ | $2.77 \times 10^{-11}$ |
| $10^{-7}$ | $1.94 \times 10^{-10}$ |
| $10^{-8}$ | $2.58 \times 10^{-9}$ |

The minimum sits at $h = 10^{-5}$, exactly where the formula said, with an error near
$10^{-11}$ — three or four digits better than the forward difference can ever reach.
The rules of thumb worth memorising are $h \approx \sqrt{\epsilon} \approx 10^{-8}$ for
a forward difference and $h \approx \epsilon^{1/3} \approx 6\times10^{-6}$ for a central
one.

## The same curve with measured data

Nothing above used the fact that $\delta$ came from floating point. Replace it by the
accuracy of an instrument and every line stands.

Suppose readings of $f$ are good to $\delta = 10^{-6}$ and $|f''| \le 2$ near the point.
Then

$$h_{*} = 2\sqrt{\frac{10^{-6}}{2}} = 2 \times 7.07\times10^{-4} \approx 1.41\times10^{-3},
\qquad E(h_{*}) = 2\sqrt{2 \times 10^{-6}} \approx 2.83\times10^{-3}.$$

Six good digits in the data support about three in the derivative. That is the honest
exchange rate, and it is why differentiating noisy measurements is a disaster done
naively and a smoothing problem done properly.

## Buying two orders back

The central difference has an expansion in even powers only,
$D_{0}(h) = A + Kh^{2} + Lh^{4} + \cdots$, where $A = f'(x)$ is what we want. Write the
same thing at half the step:

$$D_{0}(h/2) = A + \frac{K}{4}h^{2} + \frac{L}{16}h^{4} + \cdots$$

Multiply by $4$ and subtract the first line. The $h^{2}$ terms are now identical and go:

$$4D_{0}(h/2) - D_{0}(h) = 3A - \frac{3}{4}Lh^{4} + \cdots
\quad\Rightarrow\quad
R(h) = \frac{4D_{0}(h/2) - D_{0}(h)}{3} = A - \frac{L}{4}h^{4} + \cdots$$

This is **Richardson extrapolation**. The $h^{2}$ term was not made smaller; it was
cancelled, by an algebraic identity, at the cost of one arithmetic line and no new
theory.

On the running example, $D_{0}(0.2) = 0.5367074877$ and $D_{0}(0.1) = 0.5394022522$
combine to

$$R = \frac{4(0.5394022522) - 0.5367074877}{3} = \frac{1.6209015211}{3} = 0.5403005070,$$

with an error of $1.80\times10^{-6}$ against $9.0\times10^{-4}$ for the better of its
two inputs: a factor of $500$ for one line of arithmetic. Halving again gives
$R = 0.5403021933$ with an error of $1.13\times10^{-7}$, and $1.80\times10^{-6}$ over
$1.13\times10^{-7}$ is $16 = 2^{4}$, confirming fourth order.

## The mistake

'Shrink $h$ until the answer stops changing.' In the table above the answer settles down
around $h = 10^{-8}$ to $10^{-9}$ — three or four digits *after* the last correct one —
and then starts changing again for entirely the wrong reason. What the values do near
the floor is wander, not converge, and the size of the wandering is the size of the
error. Stability is not accuracy.

The second mistake is measuring the observed order in the roundoff regime. Take the
central-difference rows at $h = 10^{-6}$ and $h = 10^{-7}$, with errors
$2.77\times10^{-11}$ and $1.94\times10^{-10}$. The error *grew*, so

$$p = \frac{\log(2.77\times10^{-11} / 1.94\times10^{-10})}{\log(10^{-6}/10^{-7})}
= \frac{-0.846}{1} = -0.846 .$$

A negative order is not a broken rule; it is a correct measurement of the wrong regime.
Order must be measured where truncation dominates, which means at the *large* end of the
step sizes, not the small.

## Where it stops

Three hypotheses are doing work here, and each fails in practice.

The first is that $\delta \approx \epsilon|f|$ — proportional to the *size* of $f$, and
nothing to do with the size of its derivative. Take $g(x) = 10^{6} + \sin x$. Its
derivative is $\cos x$, unchanged, but $\delta$ is a million times larger, so
$h_{*}$ rises by a factor of about a thousand, to $3\times10^{-5}$, and the attainable
accuracy falls by the same thousand, to about $3\times10^{-5}$. Adding a constant
changes nothing mathematically and ruins the numerics.

The second is that rounding the final value is the only error in $f$. A function
delivered by an iteration, a quadrature or a simulation carries its own error, usually
far larger than $\epsilon|f|$, and $\delta$ must be set to *that* instead — which is
what pushes $h_{*}$ up into the region where the truncation analysis of the last reading
is doing real work.

The third is that there is a truncation analysis at all. On $f(x) = x|x|$ at the origin
the central difference is first order at every $h$, so there is no second-order regime
to cross over from, and the optimum computed from $M_{3}$ is meaningless because
$M_{3}$ does not exist. The floor is real, but it only becomes the binding constraint
once the smoothness above it has been earned.
""",
                },
            ],
            "derive": [
                {
                    "title": "1/x, from nothing but the definition",
                    "minutes": 12,
                    "vars": ["x", "h"],
                    "brief": r"""
No differentiation rules exist yet — this module has the definition and nothing else,
and the point of working a reciprocal by hand is that it is the first case where the
$h$ in the numerator does not fall out on its own. It has to be manufactured, and the
tool is a common denominator.

Two conventions for the answer boxes. Write fractions as `\frac{a}{b}`, and give every
answer as an expression in $x$ and $h$ — no limit signs, no $f$, no equals sign.
""",
                    "steps": [
                        {
                            "prompt": "Let $f(x) = \\dfrac{1}{x}$ with $x \\neq 0$. Put $f(x+h) - f(x)$ over the common denominator $x(x+h)$ and simplify the numerator completely. Write the result.",
                            "answer": "\\frac{-h}{x(x+h)}",
                            "placeholder": "a single fraction in x and h",
                            "hint": "The numerator is $x - (x+h)$, and the two $x$ terms cancel.",
                            "deconstruct": [
                                "$\\dfrac{1}{x+h} = \\dfrac{x}{x(x+h)}$, multiplying top and bottom by $x$.",
                                "$\\dfrac{1}{x} = \\dfrac{x+h}{x(x+h)}$, multiplying top and bottom by $x+h$.",
                                "Subtracting the numerators gives $x - (x+h) = -h$, so the difference is $\\dfrac{-h}{x(x+h)}$ — and that factor of $h$ is the one that will cancel the $h$ underneath.",
                            ],
                        },
                        {
                            "prompt": "The difference quotient divides that by $h$. On the punctured neighbourhood a limit inspects, $h$ is never zero, so the division is legal. Write the difference quotient in lowest terms.",
                            "answer": "\\frac{-1}{x(x+h)}",
                            "hint": "Dividing by $h$ multiplies the denominator by $h$; the two factors of $h$ then cancel.",
                            "deconstruct": [
                                "$\\dfrac{-h}{x(x+h)} \\div h = \\dfrac{-h}{h\\,x(x+h)}$.",
                                "Cancel the $h$, which is allowed because $h \\neq 0$ throughout the neighbourhood being examined.",
                                "What is left is $\\dfrac{-1}{x(x+h)}$, and nothing in it is singular at $h = 0$.",
                            ],
                        },
                        {
                            "prompt": "That expression is continuous at $h = 0$ as long as $x \\neq 0$, so its limit is its value there. Write $f'(x)$.",
                            "answer": "-\\frac{1}{x^{2}}",
                            "hint": "Put $h = 0$ in the denominator $x(x+h)$.",
                        },
                        {
                            "prompt": "Read off a number. Write $f'(2)$.",
                            "answer": "-\\frac{1}{4}",
                            "hint": "Evaluate $-1/x^{2}$ at $x = 2$.",
                        },
                        {
                            "prompt": "The same three lines survive a higher power. For $g(x) = \\dfrac{1}{x^{2}}$, put $g(x+h) - g(x)$ over the common denominator $x^{2}(x+h)^{2}$ and expand the numerator fully. Write the result.",
                            "answer": "\\frac{-2xh-h^{2}}{x^{2}(x+h)^{2}}",
                            "placeholder": "a single fraction, numerator expanded",
                            "hint": "The numerator is $x^{2} - (x+h)^{2}$; expand the square, then cancel the $x^{2}$ terms.",
                            "deconstruct": [
                                "The numerator is $x^{2} - (x+h)^{2}$.",
                                "$(x+h)^{2} = x^{2} + 2xh + h^{2}$.",
                                "So $x^{2} - (x^{2} + 2xh + h^{2}) = -2xh - h^{2}$, which again carries a factor of $h$ in every term.",
                            ],
                        },
                        {
                            "prompt": "Divide by $h$, cancel, then let $h \\to 0$. Write $g'(x)$.",
                            "answer": "-\\frac{2}{x^{3}}",
                            "hint": "After the division the quotient is $\\dfrac{-2x-h}{x^{2}(x+h)^{2}}$; now put $h = 0$.",
                            "deconstruct": [
                                "Dividing $-2xh - h^{2}$ by $h$ gives $-2x - h$.",
                                "At $h = 0$ the numerator is $-2x$ and the denominator is $x^{2}\\cdot x^{2} = x^{4}$.",
                                "$\\dfrac{-2x}{x^{4}} = \\dfrac{-2}{x^{3}}$.",
                            ],
                        },
                    ],
                    "closing": r"""
Two derivatives, and a pattern already visible. Writing the functions as powers,
$x^{-1}$ has derivative $-x^{-2}$ and $x^{-2}$ has derivative $-2x^{-3}$: in both cases
the exponent has come down as a factor and then dropped by one. That is the power rule,
and Module 4 proves it for every exponent rather than checking it one case at a time.
The point of doing these two by hand is that the rule is a shortcut for the calculation
above, not a substitute for knowing what it is a shortcut for.

Two things worth pausing on. The first is that neither numerator produced its factor of
$h$ by luck. In both cases the numerator vanishes at $h = 0$ — it has to, since it is
$g(x+h) - g(x)$ — so $h$ divides it, and the cancellation was guaranteed before any
algebra was done. That is a useful thing to know when a first-principles calculation
looks stuck: the factor is there, and the job is to expose it.

The second is a sanity check that costs nothing. Both derivatives are negative wherever
they are defined, which matches the picture: $1/x$ falls as $x$ increases, on each side
of the origin. But do not upgrade that to 'so $1/x$ is a decreasing function'. Its
domain is two disconnected pieces, and $f(-1) = -1$ is *less* than $f(1) = 1$, so the
function is not decreasing across the gap. A statement about a derivative on an
interval says nothing across a hole in the domain, and that distinction returns with
force in Module 8.

Where the working stops: everything above assumed $x \neq 0$, and at $x = 0$ there is
nothing to discuss. The formula $-1/x^{2}$ is not 'infinite at the origin'; it is
undefined there, because $f$ itself is undefined there, and a function that has no value
at a point cannot have a rate of change at it either.
""",
                },
                {
                    "title": "Where the h/2 and the h-squared/6 come from",
                    "minutes": 14,
                    "vars": ["h", "F", "A", "B", "C"],
                    "brief": r"""
The truncation error of a difference formula is not measured, it is *derived*, and the
derivation is four lines of Taylor expansion. Doing it once explains why the forward
difference is first order, why the central difference is second, and — more usefully —
exactly which hypothesis each of those claims is resting on.

The checker reads expressions, not primes, so fix the point $x$ and write

$$F = f(x), \qquad A = f'(x), \qquad B = f''(x), \qquad C = f'''(x),$$

all of which are constants once $x$ is fixed. Every answer below is a polynomial in $h$
with those four letters as coefficients. Write $Ah$ for $A$ times $h$, and fractions as
`\frac{a}{b}`.
""",
                    "steps": [
                        {
                            "prompt": "Taylor's expansion about $x$, kept as far as the $h^{3}$ term, writes $f(x+h)$ as a polynomial in $h$. Write it in the letters above.",
                            "answer": "F + Ah + \\frac{B}{2}h^{2} + \\frac{C}{6}h^{3}",
                            "placeholder": "a cubic in h",
                            "hint": "The coefficient of $h^{k}$ is the $k$th derivative divided by $k!$, and $2! = 2$, $3! = 6$.",
                            "deconstruct": [
                                "The constant term is the value itself, $F$.",
                                "The linear term is $f'(x)h/1! = Ah$.",
                                "Then $f''(x)h^{2}/2! = \\dfrac{B}{2}h^{2}$ and $f'''(x)h^{3}/3! = \\dfrac{C}{6}h^{3}$.",
                            ],
                        },
                        {
                            "prompt": "Form the forward difference from that: subtract $F$, then divide the whole thing by $h$. Write the result.",
                            "answer": "A + \\frac{B}{2}h + \\frac{C}{6}h^{2}",
                            "hint": "Subtracting $F$ removes the constant term; dividing by $h$ drops every remaining power by one.",
                        },
                        {
                            "prompt": "The quantity actually wanted is $A$. Write the leading term of the error — the largest of the terms left over.",
                            "answer": "\\frac{B}{2}h",
                            "hint": "The first term after $A$, the one carrying the lowest power of $h$.",
                        },
                        {
                            "prompt": "Now the other direction. Write the expansion of $f(x-h)$ to the $h^{3}$ term, in the same letters.",
                            "answer": "F - Ah + \\frac{B}{2}h^{2} - \\frac{C}{6}h^{3}",
                            "hint": "Replace $h$ by $-h$ in the first expansion: odd powers change sign, even powers do not.",
                            "deconstruct": [
                                "$(-h)^{1} = -h$, so the $A$ term changes sign.",
                                "$(-h)^{2} = h^{2}$, so the $B$ term is unchanged — this is the fact the whole derivation turns on.",
                                "$(-h)^{3} = -h^{3}$, so the $C$ term changes sign.",
                            ],
                        },
                        {
                            "prompt": "Subtract the backward expansion from the forward one. Write $f(x+h) - f(x-h)$, simplified.",
                            "answer": "2Ah + \\frac{C}{3}h^{3}",
                            "placeholder": "two terms, in odd powers of h",
                            "hint": "The even-power terms are identical in both expansions and cancel; the odd-power terms double.",
                            "deconstruct": [
                                "$F - F = 0$.",
                                "$Ah - (-Ah) = 2Ah$.",
                                "$\\dfrac{B}{2}h^{2} - \\dfrac{B}{2}h^{2} = 0$, and that cancellation is the entire purpose of the manoeuvre.",
                                "$\\dfrac{C}{6}h^{3} - \\left(-\\dfrac{C}{6}h^{3}\\right) = \\dfrac{C}{3}h^{3}$.",
                            ],
                        },
                        {
                            "prompt": "Divide by $2h$ to get the central difference. Write the result.",
                            "answer": "A + \\frac{C}{6}h^{2}",
                            "hint": "$\\dfrac{2Ah}{2h} = A$, and $\\dfrac{Ch^{3}/3}{2h} = \\dfrac{C}{6}h^{2}$.",
                        },
                        {
                            "prompt": "Write the leading error term of the central difference.",
                            "answer": "\\frac{C}{6}h^{2}",
                            "hint": "Whatever is left once $A$ has been removed.",
                        },
                    ],
                    "closing": r"""
Both error terms are now derived rather than asserted:

$$D_{+}(h) - f'(x) = \frac{h}{2}f''(x) + O(h^{2}), \qquad
D_{0}(h) - f'(x) = \frac{h^{2}}{6}f'''(x) + O(h^{4}).$$

With Taylor's theorem in Lagrange form the leading terms are exact rather than
approximate: the forward error is $\frac{h}{2}f''(\xi)$ for some $\xi$ between $x$ and
$x+h$, and the central error is $\frac{h^{2}}{6}f'''(\eta)$ for some $\eta$ in
$(x-h, x+h)$. That is what turns them into bounds.

The step to look at again is the fourth. The $B$ term survived the sign flip because
$h^{2}$ is even, and that is the only reason it cancelled in the subtraction. Symmetry
did the work; no extra function evaluations, no cleverer algebra. The same observation
run the other way — *adding* the two expansions instead of subtracting — kills the odd
terms and gives the second-derivative formula

$$\frac{f(x+h) - 2f(x) + f(x-h)}{h^{2}} = f''(x) + O(h^{2}),$$

which is the workhorse of every numerical solution of a differential equation.

Where it stops. Every line above used a Taylor expansion, and a Taylor expansion to the
$h^{3}$ term requires $f'''$ to exist and be bounded near $x$. If it does not, the
subtraction still happens and the algebra is still valid, but there is nothing left to
say about the size of the remainder. The concrete failure is $f(x) = x|x|$ at the
origin, where $f''$ already fails to exist: the central difference there returns exactly
$h$, so its error is first order at every step size, and no amount of shrinking $h$
recovers the second order the formula appears to promise.
""",
                },
                {
                    "title": "One model, two uses",
                    "minutes": 13,
                    "vars": ["h", "A", "K", "p", "D_1", "D_2", "e_1", "e_2", "h_1", "h_2"],
                    "brief": r"""
Everything in this module rests on one model for what a differencing rule returns:

$$D(h) = A + Kh^{p},$$

where $A$ is the exact answer, $p$ is the order and $K$ is an unknown constant nobody
ever computes. Two quite different things can be done with it. If $p$ is known, the
error term can be *cancelled* by combining two runs. If $p$ is unknown, it can be
*measured* from two errors. This derivation does both, in that order.

Notation for the boxes: subscripts as `D_1`, `e_2`, `h_1`; powers as `2^{p}`;
logarithms as `log(...)`, with brackets and no backslash.
""",
                    "steps": [
                        {
                            "prompt": "Start with the central difference, whose model is $D(h) = A + Kh^{2}$. Write $D(h/2)$.",
                            "answer": "A + \\frac{K}{4}h^{2}",
                            "hint": "Substitute $h/2$ for $h$; squaring the half makes it a quarter.",
                        },
                        {
                            "prompt": "Write $4D(h/2)$.",
                            "answer": "4A + Kh^{2}",
                            "hint": "Multiply both terms of the previous line by $4$.",
                            "deconstruct": [
                                "$4 \\times A = 4A$.",
                                "$4 \\times \\dfrac{K}{4}h^{2} = Kh^{2}$ — the error term has been restored to exactly the size it has in $D(h)$.",
                            ],
                        },
                        {
                            "prompt": "Now subtract $D(h) = A + Kh^{2}$ from that. Write $4D(h/2) - D(h)$.",
                            "answer": "3A",
                            "hint": "The two $h^{2}$ terms are now identical, so they cancel; only multiples of $A$ remain.",
                        },
                        {
                            "prompt": "Name the two computed numbers $D_{1} = D(h)$ and $D_{2} = D(h/2)$. Write the combination of them that equals $A$ under this model.",
                            "answer": "\\frac{4D_{2}-D_{1}}{3}",
                            "placeholder": "a weighted combination over 3",
                            "hint": "Divide the previous line by $3$, and remember it is the *smaller* step that carries the weight $4$.",
                        },
                        {
                            "prompt": "Generalise to an unknown order. For $D(h) = A + Kh^{p}$, write the multiplier $m$ that makes the $h^{p}$ term cancel in $m\\,D(h/2) - D(h)$.",
                            "answer": "2^{p}",
                            "hint": "$D(h/2)$ carries $Kh^{p}/2^{p}$, so it must be scaled up by $2^{p}$ to match the $Kh^{p}$ in $D(h)$.",
                            "deconstruct": [
                                "$(h/2)^{p} = h^{p}/2^{p}$, so the error term of $D(h/2)$ is $Kh^{p}/2^{p}$.",
                                "Multiplying by $m$ makes it $mKh^{p}/2^{p}$.",
                                "For that to equal $Kh^{p}$ and cancel on subtraction, $m = 2^{p}$. Checking against the case just done, $p = 2$ gives $m = 4$.",
                            ],
                        },
                        {
                            "prompt": "The second use of the same model. Errors $e_{1}$ at step $h_{1}$ and $e_{2}$ at step $h_{2}$ obey $e = Kh^{p}$, so $e_{1}/e_{2} = (h_{1}/h_{2})^{p}$ with $K$ divided out. Solve for $p$.",
                            "answer": "\\frac{log(e_{1}/e_{2})}{log(h_{1}/h_{2})}",
                            "placeholder": "a ratio of two logarithms",
                            "hint": "Take logarithms of both sides: $\\log(e_{1}/e_{2}) = p\\,\\log(h_{1}/h_{2})$, then divide.",
                        },
                    ],
                    "closing": r"""
The general extrapolation formula follows from the fifth step: since
$2^{p}D(h/2) - D(h)$ has no $h^{p}$ term and equals $(2^{p}-1)A$ plus smaller terms,

$$R(h) = \frac{2^{p}D(h/2) - D(h)}{2^{p}-1},$$

which for $p = 2$ is the $\dfrac{4D_{2}-D_{1}}{3}$ derived above and for $p = 1$ is the
simpler $2D_{2} - D_{1}$.

How much this buys depends on what the next term is. In general, killing the $h^{p}$
term leaves an $h^{p+1}$ term and the extrapolated rule is one order better. The central
difference is a special case worth knowing, because its expansion contains only even
powers, so killing $h^{2}$ exposes $h^{4}$ and the rule gains *two* orders. On $\sin$ at
$x = 1$, combining the central differences at $h = 0.2$ and $h = 0.1$ gives an error of
$1.80\times10^{-6}$ where the better input was wrong by $9.0\times10^{-4}$, and halving
the pair again divides the error by $16$ rather than $4$.

Where each half of this stops.

Richardson assumes the error really is $Kh^{p}$ with $K$ constant over the two steps.
Once the roundoff floor of the previous reading has been reached, the discrepancy is not
of that form at all, and the combination makes matters worse rather than better: its
coefficients are $4/3$ and $-1/3$, whose magnitudes sum to $5/3$, so rounding noise is
amplified by $5/3$ while nothing is cancelled. Extrapolation is for the truncation
regime only.

The measurement of $p$ has the mirror-image restriction, and needs one thing more: the
exact answer, in order to form $e_{1}$ and $e_{2}$ at all. So it is a diagnostic run on
a test problem whose solution is known, and both steps must be taken from the large end
of the range, where truncation dominates. Two steps from below the floor give a
meaningless number — often negative, since down there the error grows as $h$ shrinks.
""",
                },
            ],
            "blanks": [
                {
                    "title": "A square root from first principles, line by line",
                    "minutes": 10,
                    "caption": "the definition applied to sqrt(x), with six steps removed",
                    "lang": "text",
                    "brief": r"""
The reciprocal exposed its factor of $h$ with a common denominator. A square root will
not: there is nothing to put over a common denominator and nothing to factor. The move
that works is the one Module 2 used on a $0/0$ with a root in it — multiply by the
conjugate — and it is worth seeing that the *same* manoeuvre appears here for the same
reason.

Four of the missing pieces are algebra. One is the reason the cancellation is allowed,
which is the step usually performed in silence and the only one that could be wrong.
One is a number.
""",
                    "listing": """Differentiate  f(x) = sqrt(x)  from the definition, at a point x > 0.


Step 0.  Write down the difference quotient.

     f(x + h) - f(x)          sqrt(x + h) - sqrt(x)
     ---------------    =     ---------------------
            h                           h


Step 1.  Substituting h = 0 makes the numerator sqrt(x) - sqrt(x) = 0
         and the denominator 0, so the form is ___ and the quotient
         law does not apply yet.


Step 2.  There is no factor of h anywhere to cancel.  Manufacture one:
         multiply top and bottom by C, the conjugate of the numerator.

     C  =  ___


Step 3.  The numerator becomes a difference of two squares:

     (sqrt(x + h))^2 - (sqrt(x))^2  =  (x + h) - x  =  ___


Step 4.  So the quotient now reads

                     h                                1
         ---------------------------    =    ---------------------
          h * (sqrt(x+h) + sqrt(x))           sqrt(x+h) + sqrt(x)

         and cancelling the h is legal because ___ .


Step 5.  What is left is continuous at h = 0, so substitute h = 0:

     1 / (sqrt(x + 0) + sqrt(x))  =  ___


Step 6.  Read off a number.  At x = 9, the derivative f'(9) is ___ .
""",
                    "blanks": [
                        {
                            "prompt": "Both halves of the quotient came out zero. Name the form.",
                            "hole": "?",
                            "opts": ["0", "0/0", "1", "undefined, so f has no derivative at x"],
                            "a": 1,
                            "why": r"""
$0/0$ is a report about the shape of the expression, not a value: it says the quotient
law's hypotheses have failed and that algebra is owed. Every difference quotient has
this form at $h = 0$, which is exactly why the derivative had to be defined as a limit
in the first place. Reading it as the number $0$ would make every derivative zero.
Reading it as $1$ treats the two zeros as cancelling, which they do not — the answer
here turns out to depend on $x$. And being undefined at $h = 0$ is no obstruction
whatsoever: a limit inspects only the punctured neighbourhood, so a hole at the point
is the normal case rather than a failure.
""",
                        },
                        {
                            "prompt": "The conjugate of $\\sqrt{x+h}-\\sqrt{x}$.",
                            "hole": "?",
                            "opts": [
                                "sqrt(x+h) + sqrt(x)",
                                "sqrt(x+h) - sqrt(x)",
                                "sqrt(x-h) + sqrt(x)",
                                "sqrt(x+h) * sqrt(x)",
                            ],
                            "a": 0,
                            "why": r"""
A conjugate flips the sign between the two terms and changes nothing else, so
$\sqrt{x+h}-\sqrt{x}$ pairs with $\sqrt{x+h}+\sqrt{x}$, and the product is
$(\sqrt{x+h})^{2}-(\sqrt{x})^{2}$, which is what removes the roots. Repeating the
expression unchanged squares it and leaves both roots firmly in place. Moving the sign
inside the radical, as $\sqrt{x-h}$, changes the function rather than multiplying by
$1$. And a product of the two roots is not a conjugate at all — it gives
$\sqrt{x(x+h)}$, a single root and no cancellation.
""",
                        },
                        {
                            "prompt": "Simplify $(x+h)-x$.",
                            "hole": "?",
                            "opts": ["h", "0", "2x + h", "x"],
                            "a": 0,
                            "why": r"""
$(x+h)-x = h$, and the appearance of exactly the factor sitting in the denominator is
the whole reason the conjugate was worth introducing: it converts a difference of roots
into the single factor that will cancel. Answering $0$ substitutes $h = 0$ a step early,
which is the mistake the entire limit construction exists to avoid. $2x+h$ is what
$(x+h)+x$ gives, from adding instead of subtracting. And $x$ is what survives if the
$h$ is dropped, which is precisely the term that does not survive.
""",
                        },
                        {
                            "prompt": "Why may the factor $h$ be cancelled here?",
                            "hole": "?",
                            "opts": [
                                "a common factor may always be cancelled from a fraction",
                                "h is never 0 on the punctured neighbourhood a limit inspects",
                                "the numerator and the denominator both vanish at h = 0",
                                "x is strictly positive, so the roots are defined",
                            ],
                            "a": 1,
                            "why": r"""
Cancelling divides by $h$, and division is legal only when that quantity is non-zero —
which is guaranteed here not by luck but by the definition of a limit, which examines
$0 < |h| < \delta$ and never $h = 0$ itself. The blanket claim that common factors
always cancel is false at exactly the point in question, and believing it turns this
step into a habit that will one day destroy a genuine discontinuity. Both halves
vanishing is the reason a common factor *exists*, not the reason it may be divided out.
And $x > 0$ is a real hypothesis, but it is the one that keeps $\sqrt{x}$ defined and
the denominator non-zero at the end; it says nothing about $h$.
""",
                        },
                        {
                            "prompt": "Simplify $\\dfrac{1}{\\sqrt{x}+\\sqrt{x}}$.",
                            "hole": "?",
                            "opts": ["1 / (2*sqrt(x))", "2*sqrt(x)", "1 / sqrt(2*x)", "sqrt(x) / 2"],
                            "a": 0,
                            "why": r"""
Two identical roots add to $2\sqrt{x}$, so the reciprocal is $\dfrac{1}{2\sqrt{x}}$ —
the standard derivative of the square root, now derived rather than quoted. Answering
$2\sqrt{x}$ inverts the fraction. Answering $1/\sqrt{2x}$ takes the $2$ inside the
radical, which is a different number: at $x = 9$ that would give $1/\sqrt{18} = 0.2357$
rather than $1/6 = 0.1667$. And $\sqrt{x}/2$ inverts only part of the expression.
Notice what the answer says about the shape of the curve: the derivative grows without
bound as $x \to 0^{+}$, which is the vertical tangent the graph of $\sqrt{x}$ has at the
origin, and the reason the hypothesis $x > 0$ could not be dropped.
""",
                        },
                        {
                            "prompt": "Evaluate $\\dfrac{1}{2\\sqrt{x}}$ at $x = 9$.",
                            "hole": "?",
                            "opts": ["1/6", "3", "1/3", "6"],
                            "a": 0,
                            "why": r"""
$\sqrt{9} = 3$, so $\dfrac{1}{2\sqrt{9}} = \dfrac{1}{6} \approx 0.1667$. Check it against
the quotient it came from: $\sqrt{9.01} = 3.0016662$, so the difference quotient at
$h = 0.01$ is $0.0016662/0.01 = 0.16662$, already within $5\times10^{-5}$ of
$1/6 = 0.16667$. Answering $3$
reports $f(9)$ rather than $f'(9)$; answering $1/3$ forgets the factor of $2$ that came
from adding two equal roots; answering $6$ inverts the result. The number is also a
reminder of how flat the square root is out here — nine units along, the curve is rising
at one sixth of a unit per unit.
""",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One forward difference, by hand",
                    "minutes": 5,
                    "brief": r"""
The bottom of the ladder. Nothing has to be derived: two evaluations, one subtraction,
one division. The only trap is answering the question that was not asked.
""",
                    "prompt": "What does the forward difference return?",
                    "note": "A pure number, to three decimal places.",
                    "figure": "Estimate the derivative of $f(x) = x^{3}$ at $x = 2$ with the forward "
                              "difference $\\dfrac{f(x+h)-f(x)}{h}$ at step $h = 0.1$. Report the value "
                              "the formula returns, not the value of the derivative.",
                    "given": [
                        {"label": "Function", "value": "$f(x) = x^{3}$"},
                        {"label": "Point", "value": "$x = 2$"},
                        {"label": "Step", "value": "$h = 0.1$"},
                        {"label": "Rule", "value": "$\\dfrac{f(x+h)-f(x)}{h}$"},
                    ],
                    "aside": "$2.1^{3} = 9.261$ exactly.",
                    "answer": 12.61,
                    "tol": 0.005,
                    "unit": "",
                    "hint": "$f(2.1) = 9.261$ and $f(2) = 8$. Subtract, then divide by $0.1$ — which "
                            "is the same as multiplying by $10$.",
                    "wrong": "If you answered $12$, you reported the exact derivative "
                             "$f'(2) = 3 \\times 2^{2}$ rather than what the formula returns, and the "
                             "gap between those two numbers is the whole subject of this module. If "
                             "you answered $1.261$, the division by $h$ was left out. If you answered "
                             "$12.01$, that is the *central* difference, "
                             "$(f(2.1)-f(1.9))/0.2$, which is a different and better rule.",
                    "why": "$\\dfrac{9.261 - 8}{0.1} = \\dfrac{1.261}{0.1} = 12.61$. The exact "
                           "derivative is $f'(2) = 12$, so the rule is wrong by $0.61$ at this step "
                           "size — about five per cent, from an $h$ that looks small. For a cubic the "
                           "Taylor expansion terminates, so the error can be accounted for to the last "
                           "digit: the forward difference equals "
                           "$f' + \\tfrac{h}{2}f'' + \\tfrac{h^{2}}{6}f'''$ exactly, and with "
                           "$f''(2) = 12$ and $f''' = 6$ that is "
                           "$12 + 0.05 \\times 12 + \\tfrac{0.01}{6}\\times 6 = 12 + 0.6 + 0.01 = "
                           "12.61$. Nothing was approximated anywhere. The leading term $0.6$ is the "
                           "one that halves when $h$ halves, which is what first order means.",
                },
                {
                    "title": "How fast is it converging?",
                    "minutes": 7,
                    "brief": r"""
One rung up: a formula applied to two measurements rather than to a function. The order
of a rule is not something to be taken on trust from a textbook — it can be read off
two runs, and when the reading disagrees with the textbook it is the textbook's
hypotheses that have failed.
""",
                    "prompt": "What is the observed order $p$?",
                    "note": "A pure number, to two decimal places.",
                    "figure": "A differencing rule was run twice on the same test problem, whose exact "
                              "answer is known, so both errors could be formed: $e_{1} = 3.5948 \\times "
                              "10^{-3}$ at step $h_{1} = 0.2$, and $e_{2} = 9.0005 \\times 10^{-4}$ at "
                              "step $h_{2} = 0.1$. Assume the model $e = Kh^{p}$ and report $p$.",
                    "given": [
                        {"label": "First run", "value": "$h_{1} = 0.2$, $e_{1} = 3.5948 \\times 10^{-3}$"},
                        {"label": "Second run", "value": "$h_{2} = 0.1$, $e_{2} = 9.0005 \\times 10^{-4}$"},
                        {"label": "Model", "value": "$e = Kh^{p}$"},
                    ],
                    "aside": "$p = \\dfrac{\\log(e_{1}/e_{2})}{\\log(h_{1}/h_{2})}$, and the base of "
                             "the logarithm does not matter because it appears twice.",
                    "answer": 1.998,
                    "tol": 0.02,
                    "unit": "",
                    "hint": "$e_{1}/e_{2} = 3.994$ and $h_{1}/h_{2} = 2$, so $p$ is $\\log 3.994$ "
                            "divided by $\\log 2$.",
                    "wrong": "If you answered $3.99$, that is the error ratio itself rather than its "
                             "logarithm to base $2$ — the ratio answers 'by how much', the order "
                             "answers 'to what power'. If you answered $0.50$, the fraction is upside "
                             "down: it is the logarithm of the *error* ratio on top. If you answered "
                             "$2$ exactly, that is the right conclusion but not the measurement; the "
                             "measured value is slightly below $2$ and the gap is informative.",
                    "why": "The unknown constant $K$ divides out of $e_{1}/e_{2} = "
                           "(h_{1}/h_{2})^{p}$, leaving $p = \\log(3.99400)/\\log 2 = 1.9978$. So the "
                           "rule is second order, and this is a central difference: the model has been "
                           "confirmed, not assumed. The reading is not exactly $2$ because the "
                           "neglected $h^{4}$ term is not exactly zero at $h = 0.2$; running the same "
                           "test at $h = 0.1$ and $h = 0.05$ gives $1.9995$, closer still. For "
                           "contrast, the forward difference on the same problem and the same two "
                           "steps reads $1.026$. Note what the calculation required: the exact answer, "
                           "in order to form the errors at all. Observed order is therefore a "
                           "diagnostic you run on a problem you have already solved, to earn the right "
                           "to trust the rule on one you have not.",
                },
                {
                    "title": "Two estimates, one better answer",
                    "minutes": 8,
                    "brief": r"""
The number asked for is neither of the numbers given, and it is not their average. It is
the one combination of them whose leading error term is zero — which is worth more than
either input and costs one line of arithmetic.
""",
                    "prompt": "What does Richardson extrapolation give?",
                    "note": "A pure number, to six decimal places. Keep the sign.",
                    "figure": "A second-order accurate differencing rule was applied to a quantity "
                              "available only through an expensive simulation, so the exact derivative "
                              "is not known in closed form and a third run is not on offer. At "
                              "$h = 0.2$ the rule returned $D_{1} = -0.83485679$; at $h = 0.1$ it "
                              "returned $D_{2} = -0.85191951$. Combine the two.",
                    "given": [
                        {"label": "Order of the rule", "value": "$p = 2$"},
                        {"label": "Coarse run", "value": "$D_{1} = D(0.2) = -0.83485679$"},
                        {"label": "Fine run", "value": "$D_{2} = D(0.1) = -0.85191951$"},
                    ],
                    "aside": "For a second-order rule the combination is "
                             "$\\dfrac{4D_{2}-D_{1}}{3}$.",
                    "answer": -0.857607,
                    "tol": 5e-06,
                    "unit": "",
                    "hint": "$4 \\times (-0.85191951) = -3.40767804$. Subtracting $D_{1}$, which is "
                            "itself negative, adds $0.83485679$. Then divide by $3$.",
                    "wrong": "If you answered $-0.829169$, the two values were swapped: it is the "
                             "*finer* step that carries the weight $4$, because it is the more nearly "
                             "correct of the two. If you answered $-0.843388$, you averaged them, "
                             "which cancels nothing — an average of two estimates with the same-sign "
                             "error is still wrong in that direction. If you answered $-0.851920$, "
                             "you reported the better input rather than the combination.",
                    "why": "$\\dfrac{4(-0.85191951) - (-0.83485679)}{3} = \\dfrac{-2.57282125}{3} = "
                           "-0.85760708$. The simulation was in fact $e^{-x^{2}}$ at $x = 0.7$, whose "
                           "derivative is $-1.4e^{-0.49} = -0.85767695$, so the extrapolated value is "
                           "wrong by $7.0 \\times 10^{-5}$ where the better of its two inputs was "
                           "wrong by $5.8 \\times 10^{-3}$: a factor of $82$, bought with one "
                           "subtraction and one division. The mechanism is the model $D(h) = A + "
                           "Kh^{2}$: quartering the step term means $4D(h/2)$ carries the same "
                           "$Kh^{2}$ as $D(h)$, so the subtraction annihilates it and leaves $3A$. "
                           "Nothing here needed the value of $K$, which is why the trick works on a "
                           "function nobody can differentiate.",
                },
                {
                    "title": "The step size the noise chooses for you",
                    "minutes": 10,
                    "brief": r"""
The top of the ladder. There is no number to look up and nothing to evaluate: the
quantity asked for is the minimiser of a total-error model, so the model has to be
written down and differentiated before any arithmetic can start.

This is also the case that matters in practice, because real function values are never
exact — they come from an instrument, a simulation or a floating-point routine, and all
three carry a floor.
""",
                    "prompt": "Which step size $h$ minimises the error bound?",
                    "note": "A pure number, in the same units as $x$. Three significant figures.",
                    "figure": "A quantity $f$ is read off an instrument, and every reading carries an "
                              "absolute error of at most $\\delta = 10^{-8}$. Near the point of "
                              "interest $|f''| \\le M = 4$. The derivative is to be estimated by the "
                              "forward difference $\\dfrac{f(x+h)-f(x)}{h}$, whose truncation "
                              "contributes at most $Mh/2$ and whose two noisy readings contribute at "
                              "most $2\\delta/h$ once the division has magnified them. Choose $h$.",
                    "given": [
                        {"label": "Reading error", "value": "$\\delta = 10^{-8}$"},
                        {"label": "Curvature bound", "value": "$M = 4$"},
                        {"label": "Truncation term", "value": "$Mh/2$"},
                        {"label": "Noise term", "value": "$2\\delta/h$"},
                    ],
                    "aside": "Add the two contributions, differentiate the sum with respect to $h$, "
                             "and set the derivative to zero.",
                    "answer": 0.0001,
                    "tol": 5e-06,
                    "unit": "",
                    "hint": "$E(h) = \\dfrac{M}{2}h + \\dfrac{2\\delta}{h}$, so "
                            "$E'(h) = \\dfrac{M}{2} - \\dfrac{2\\delta}{h^{2}}$. Set that to zero and "
                            "solve for $h$.",
                    "wrong": "If you answered $5 \\times 10^{-5}$, the factor of $2$ on the noise term "
                             "was dropped — both readings are uncertain, so their difference carries "
                             "twice the error of one. If you answered $10^{-8}$, the step was set "
                             "equal to the noise itself, which is the natural guess and the worst "
                             "possible choice: at $h = \\delta$ the noise term alone is $2$. If you "
                             "answered $4 \\times 10^{-4}$, that is the minimum error $2\\sqrt{M\\delta}$ "
                             "rather than the step that achieves it.",
                    "why": "Setting $\\dfrac{M}{2} = \\dfrac{2\\delta}{h^{2}}$ gives "
                           "$h^{2} = \\dfrac{4\\delta}{M}$ and hence $h_{*} = 2\\sqrt{\\delta/M} = "
                           "2\\sqrt{2.5 \\times 10^{-9}} = 2 \\times 5 \\times 10^{-5} = 10^{-4}$. "
                           "Substituting back, the two contributions come out equal — "
                           "$Mh_{*}/2 = 2\\times10^{-4}$ and $2\\delta/h_{*} = 2\\times10^{-4}$ — "
                           "which is a free check on any calculation of this shape, and the total "
                           "bound is $2\\sqrt{M\\delta} = 4\\times10^{-4}$. Two consequences are worth "
                           "keeping. Data good to eight digits supports a derivative good to about "
                           "three and a half, because the attainable error goes like $\\sqrt{\\delta}$ "
                           "rather than $\\delta$. And overshooting downwards is punished hard: at "
                           "$h = 10^{-5}$, ten times smaller, the bound is "
                           "$2\\times10^{-5} + 2\\times10^{-3} = 2.02\\times10^{-3}$, five times worse "
                           "than at the optimum, because the noise term is now doing all the damage.",
                },
            ],
            "quiz": {
                "title": "Difference quotients and what they cost",
                "minutes": 9,
                "questions": [
                    {
                        "q": "Before any limit is taken, what does $\\dfrac{f(a+h)-f(a)}{h}$ measure?",
                        "opts": [
                            "the slope of the tangent to $y = f(x)$ at $x = a$",
                            "the slope of the secant through $(a, f(a))$ and $(a+h, f(a+h))$",
                            "the derivative $f'(a)$, provided $h$ is small enough",
                            "nothing — it has the form $0/0$",
                        ],
                        "a": 1,
                        "why": r"""
It is a rise divided by a run between two points that both lie on the curve, which is
exactly the slope of the secant joining them, and equivalently the average rate of change
of $f$ across that interval. The tangent slope is the *limit* of this quantity as
$h \to 0$, not the quantity itself, and the gap between them is what the rest of the
module measures. Calling it the derivative 'provided $h$ is small' is the same error
with a hedge attached: at $h = 0.1$ on $f(x) = x^{3}$ at $x = 2$ the quotient is $12.61$
and the derivative is $12$. And the $0/0$ form arises only at $h = 0$, which the
definition explicitly excludes.
""",
                    },
                    {
                        "q": "For $f(x) = |x|$, what is $f'(0)$?",
                        "opts": [
                            "$0$, by symmetry",
                            "$1$, since $|x| = x$ for $x > 0$",
                            "it does not exist: the quotient is $+1$ for $h > 0$ and $-1$ for $h < 0$",
                            "it does not exist, because $f$ is not continuous at $0$",
                        ],
                        "a": 2,
                        "why": r"""
The quotient is $|h|/h$, which is $+1$ on one side and $-1$ on the other, so the
one-sided limits are $1$ and $-1$, they disagree, and the two-sided limit required by the
definition does not exist. Symmetry is a real feature of the picture but it is not a
theorem: the symmetric formula $(|h|-|-h|)/(2h)$ returns $0$ at every step size, which
shows only that a difference formula will answer a question that has no answer. Taking
the right-hand slope alone answers a different question, the one-sided derivative.
And $f$ is perfectly continuous at $0$ — continuity is not what fails here, which is
precisely why this example matters: it separates the two properties.
""",
                    },
                    {
                        "q": "Halving $h$ multiplies the error of a forward difference by about $1/2$. For a central difference, by about what?",
                        "opts": ["$1/2$", "$1/4$", "$1/8$", "$1/16$"],
                        "a": 1,
                        "why": r"""
The central difference has error $\frac{h^{2}}{6}f'''(\xi)$, so the error is proportional
to $h^{2}$ and halving $h$ divides it by $2^{2} = 4$. Dividing by $2$ would be first
order, which is what the forward difference does and what the symmetric arrangement was
designed to improve on. Factors of $8$ and $16$ belong to third- and fourth-order rules;
$1/16$ is what Richardson extrapolation of a central difference achieves, but that takes
an extra combination step rather than merely halving.
""",
                    },
                    {
                        "q": "The central difference applied to $f(x) = x|x|$ at $x = 0$ returns exactly $h$ at every step size, while $f'(0) = 0$. What does that show?",
                        "opts": [
                            "the rule was implemented wrongly; the correct central difference gives $0$ here",
                            "the second-order claim requires $f'''$ to exist near the point, and here not even $f''$ does",
                            "nothing surprising — the estimate still tends to $0$, so the order claim is unaffected",
                            "the derivative $f'(0)$ does not actually exist",
                        ],
                        "a": 1,
                        "why": r"""
Here $f(h) = h^{2}$ and $f(-h) = -h^{2}$, so the rule returns $2h^{2}/(2h) = h$: the
implementation is correct and the arithmetic is exact. The error is $h$, so the rule is
first order at every step size, and the $O(h^{2})$ derivation fails because it expanded
$f$ to the $h^{3}$ term — which needs $f'''$, and this $f$ has no second derivative at
the origin at all. It is true that the estimate still converges, but converging was never
the disputed claim; the claim was the *rate*, and that is false here, so halving $h$ buys
one bit rather than two. And $f'(0)$ does exist and equals $0$, since
$(h|h| - 0)/h = |h| \to 0$ from both sides.
""",
                    },
                    {
                        "q": "The error of a forward difference in double precision falls as $h$ shrinks until roughly $h = 10^{-8}$, then grows. Why?",
                        "opts": [
                            "the truncation term $\\frac{h}{2}f''$ changes sign there",
                            "the subtraction $f(x+h)-f(x)$ loses its leading digits to cancellation, and dividing by $h$ magnifies what is left",
                            "the machine cannot represent numbers below $10^{-8}$",
                            "$f''$ grows without bound as $h \\to 0$",
                        ],
                        "a": 1,
                        "why": r"""
The two stored values agree in more and more leading digits as $h$ shrinks; those digits
cancel exactly in the subtraction, leaving a result carried by the least reliable digits
of each operand, and the division by $h$ then multiplies that inherited error by $1/h$.
The rounding contribution is about $2\delta/h$ with $\delta \approx \epsilon|f|$, so it
grows without bound. The truncation term does not change sign — it falls steadily, and it
is still falling when the roundoff term overtakes it. Doubles represent numbers far below
$10^{-8}$ perfectly well; the trouble is with the *difference*, not the step. And $f''$
is a property of $f$ at the point and does not depend on $h$ at all.
""",
                    },
                    {
                        "q": "Two runs of a rule give errors $2.77\\times10^{-11}$ at $h = 10^{-6}$ and $1.94\\times10^{-10}$ at $h = 10^{-7}$, so the observed order comes out $-0.85$. What should you conclude?",
                        "opts": [
                            "the rule diverges",
                            "both steps sit below the roundoff floor, so the measurement is of noise rather than truncation — measure the order at larger $h$",
                            "the rule has order $-0.85$",
                            "the exact answer used to form the errors must be wrong",
                        ],
                        "a": 1,
                        "why": r"""
A negative order says the error *grew* when the step shrank, and that is exactly what
happens below the crossover, where the $1/h$ rounding term dominates the $h^{2}$
truncation term. The measurement is correct and is telling you which regime you are in.
The rule does not diverge: at $h = 10^{-3}$ the same rule is converging cleanly at order
$2$. A negative order is not a property a differencing rule can have, since the model
$e = Kh^{p}$ describes only the truncation term. And there is no reason to doubt the
reference answer — the errors are around $10^{-11}$, which is exactly the size the floor
predicts.
""",
                    },
                    {
                        "q": "Richardson extrapolation combines two runs of a second-order rule as $\\dfrac{4D_{2}-D_{1}}{3}$, where $D_{2}$ used the halved step. What is the $3$ doing?",
                        "opts": [
                            "it cancels the leading error term",
                            "the numerator has already lost its $h^{2}$ term but equals $3$ times the true value, so dividing restores the scale",
                            "it counts the function evaluations the two runs used",
                            "it keeps the rounding error from being amplified",
                        ],
                        "a": 1,
                        "why": r"""
With $D(h) = A + Kh^{2}$, the combination $4D(h/2) - D(h)$ equals
$(4A + Kh^{2}) - (A + Kh^{2}) = 3A$: the cancellation of the error is done by the $4$,
which restores the quartered $h^{2}$ term to full size, and the $3$ is merely the
leftover coefficient $4 - 1$ on $A$. For a rule of order $p$ the same argument gives
$2^{p}$ on top and $2^{p}-1$ underneath. The evaluation count has nothing to do with it.
And far from protecting against rounding, the combination *amplifies* it: the weights
$4/3$ and $-1/3$ have magnitudes summing to $5/3$, so extrapolating below the roundoff
floor makes the answer worse.
""",
                    },
                ],
            },
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
                "Linearity plus the power rule `d/dx x^n = n*x^(n-1)`. The binomial expansion of `(x + h)^n` proves it for whole-number `n` and for nothing else; negative exponents come from the quotient rule, rational ones from squaring the relation first, and irrational ones have to wait for `exp` and `ln` in Module 6",
                "The product rule `(f*g)' = f'*g + f*g'`; the tempting `f'*g'` fails on the first example anyone tries",
                "The quotient rule `(f/g)' = (f'*g - f*g')/(g*g)`, where the order in the numerator is the entire sign",
                "Differentiability implies continuity, but not the reverse: `|x|` is continuous at `0` and has a corner there",
            ],
            "read": [
                {
                    "title": "Three rules, and the two lines behind each one",
                    "minutes": 12,
                    "body": r"""
Module 3 differentiated $x^{2} - 3x$ from the definition. It took half a page, and the
answer was $2x - 3$. Now try the same thing on

$$f(x) = \frac{x^{2}+1}{x^{3}-x}.$$

Form $f(x+h)$, put it over a common denominator with $f(x)$, expand two cubics and a
square, cancel whatever cancels, divide by $h$, and take a limit. It can be done. It is
also the last time anyone would want to do it, and the answer — $-31/36$ at $x = 2$ —
does not look like it cost that much.

The rules in this module are not a new idea. They are the observation that the same
cancellations happen every time, so they can be done once, in general, and then quoted.
What follows is each rule with the derivation standing behind it, because a rule you
have seen proved is a rule you can repair when you misremember it, and a rule you have
only seen stated is a formula you either recall or do not.

## Linearity, straight from the limit laws

If $f$ and $g$ are both differentiable at $x$, then

$$\frac{(f+g)(x+h) - (f+g)(x)}{h} = \frac{f(x+h)-f(x)}{h} + \frac{g(x+h)-g(x)}{h},$$

which is ordinary algebra, not analysis. Now take $h \to 0$. Module 2's sum law says
the limit of a sum is the sum of the limits **provided both limits exist**, and they do
by hypothesis. So $(f+g)' = f' + g'$. The same two lines with a constant $c$ give
$(cf)' = cf'$.

That hypothesis is worth noticing rather than skipping. The sum law is what fails when
one of the two pieces is not differentiable, and it is the reason none of these rules
can be applied to a function you have not first checked.

## The power rule, from the binomial theorem

Take $n$ a positive whole number and expand:

$$(x+h)^{n} = x^{n} + nx^{n-1}h + \binom{n}{2}x^{n-2}h^{2} + \cdots + h^{n}.$$

Subtract $x^{n}$ and the first term goes. Every remaining term carries at least one
factor of $h$, so dividing by $h$ is legal on the punctured neighbourhood a limit
inspects:

$$\frac{(x+h)^{n} - x^{n}}{h} = nx^{n-1} + \binom{n}{2}x^{n-2}h + \cdots + h^{n-1}.$$

Every term after the first still carries an $h$. Letting $h \to 0$ kills all of them at
once and leaves

$$\frac{d}{dx}x^{n} = nx^{n-1}.$$

**Read the scope of that argument carefully, because the course will use the rule well
outside it.** The binomial theorem in the form used above expands $(x+h)^{n}$ into
$n+1$ terms, which requires $n$ to be a positive whole number. The derivation above
therefore proves the power rule for $n = 1, 2, 3, \ldots$ and for nothing else.

The rule is nevertheless true for every real exponent, and each remaining case is a
separate argument:

- **Negative integers.** $x^{-m} = 1/x^{m}$, and the quotient rule below turns the
  positive case into the negative one.
- **Rational exponents.** $y = x^{1/2}$ satisfies $y^{2} = x$. Differentiating that
  relation gives the answer without expanding anything — the derivation is at the end of
  this reading, and Module 7 makes the technique general.
- **Irrational exponents.** $x^{\pi}$ is *defined* as $\exp(\pi \ln x)$, so its
  derivative has to wait for Module 6, where the exponential and the logarithm get
  theirs.

None of that changes how you use the rule. It changes what you are entitled to say
about why it holds, which is a different thing and the one people skip.

## The product rule, and the rectangle it comes from

Picture $f(x)$ and $g(x)$ as the sides of a rectangle, so $f(x)g(x)$ is its area.
Increase $x$ by $h$: one side grows by $\Delta f = f(x+h) - f(x)$, the other by
$\Delta g$. The new area exceeds the old by three pieces — a strip $g\,\Delta f$ along
one side, a strip $f\,\Delta g$ along the other, and the small corner square
$\Delta f\,\Delta g$ where they meet.

Algebraically, that decomposition is the add-and-subtract:

$$f(x+h)g(x+h) - f(x)g(x) = \underbrace{[f(x+h)-f(x)]g(x+h)}_{\text{one strip}} +
\underbrace{f(x)[g(x+h)-g(x)]}_{\text{the other}}.$$

Divide by $h$ and let $h \to 0$. The first bracket over $h$ tends to $f'(x)$. The
factor $g(x+h)$ tends to $g(x)$ — and it does so because $g$ is differentiable, hence
continuous, which is the one place that implication is load-bearing. The second term
tends to $f(x)g'(x)$. So

$$(fg)' = f'g + fg'.$$

The corner square is where the missing term went. It is $\Delta f\,\Delta g$, a product
of two quantities both heading to zero, so divided by $h$ it still carries a factor
tending to zero and contributes nothing in the limit. That is the honest reason the
product rule has two terms rather than three.

## Why $f'g'$ is tempting, and how fast it fails

Every other rule so far has distributed: the derivative of a sum is the sum of the
derivatives, and constants pull out. It is a reasonable guess that products behave the
same way. They do not, and the cheapest demonstration takes one line. Let
$f(x) = x^{3}$ and $g(x) = x^{2}$, so $fg = x^{5}$ and the power rule gives $5x^{4}$.
The product rule agrees: $3x^{2}\cdot x^{2} + x^{3}\cdot 2x = 3x^{4} + 2x^{4} = 5x^{4}$.
Multiplying the derivatives gives $3x^{2}\cdot 2x = 6x^{3}$, which is not even the right
power of $x$.

The rectangle says why. The area does not grow by the product of the two growths; it
grows by two strips, and each strip is one side's growth times *the other side's whole
length*.

## The quotient rule, which nobody needs to memorise

Let $q = f/g$ at a point where $g \neq 0$. Then $f = qg$, and the product rule applies
to the right-hand side:

$$f' = q'g + qg'.$$

Solve for $q'$, then substitute $q = f/g$:

$$q' = \frac{f' - qg'}{g} = \frac{f' - (f/g)g'}{g} = \frac{f'g - fg'}{g^{2}}.$$

The order in the numerator is not a convention to be memorised. It arrives that way
because $q'g$ was the term isolated and $qg'$ the term moved across, and moving it
across is what makes it negative. If you write the numerator backwards you get $-q'$,
and one test at $f = x$, $g = 1$ — where the answer must be $1$ — catches it
immediately. This is worth doing rather than trusting memory: the reversed numerator is
the single most common error in the rule.

The derivation also needs one thing the statement hides. It assumed $q$ is
differentiable in order to apply the product rule to $qg$. That is provable, but it is
not free, and the argument above is a way of *computing* $q'$ on the assumption it
exists rather than a proof that it does.

## Worked, end to end

Return to $f(x) = \dfrac{x^{2}+1}{x^{3}-x}$ and evaluate $f'(2)$.

The numerator has derivative $2x$; the denominator has derivative $3x^{2}-1$. At
$x = 2$: the numerator is $5$ and its derivative is $4$; the denominator is
$8 - 2 = 6$ and its derivative is $12 - 1 = 11$. So

$$f'(2) = \frac{4\cdot 6 - 5\cdot 11}{6^{2}} = \frac{24 - 55}{36} = -\frac{31}{36}
\approx -0.8611.$$

Check it the way Module 3 taught. $f(2) = 5/6 = 0.8333\ldots$, and a central difference
with $h = 10^{-4}$ gives $-0.86111112$, against $-31/36 = -0.86111111$. The agreement
to seven figures is not a proof, but a disagreement in the second figure would have been
a sign error, and this is the cheapest way to catch one.

Sanity on the sign: at $x = 2$ the denominator $x^{3}-x$ is growing much faster than the
numerator $x^{2}+1$, so the ratio should be falling. It is.

## Differentiable implies continuous

One more consequence, used above and worth stating on its own. If $f'(a)$ exists then

$$f(x) - f(a) = \frac{f(x)-f(a)}{x-a}\cdot(x-a) \longrightarrow f'(a)\cdot 0 = 0,$$

so $f(x) \to f(a)$ and $f$ is continuous at $a$. The product law is legal here because
both factors have limits.

The converse is false, and Module 3's $|x|$ is the standing counterexample: continuous
everywhere, no derivative at the origin. Continuity is necessary for differentiability
and buys nothing back.

## Where these rules stop

Every rule above has the same hypothesis: **both derivatives exist at the point in
question.** When one does not, the rule does not apply — and, importantly, that is not
the same as the conclusion being false.

Take $f(x) = |x|$ and $g(x) = |x|$ at the origin. Neither is differentiable there, so
the product rule says nothing. But $f(x)g(x) = x^{2}$, which is differentiable at $0$
with derivative $0$. A failed hypothesis releases the theorem; it does not reverse it.
Deciding that a product is non-differentiable *because* a factor is, is the same
category of error as concluding a limit fails to exist because substitution gave $0/0$.
""",
                },
            ],
            "derive": [
                {
                    "title": "The three rules, proved rather than quoted",
                    "minutes": 14,
                    "vars": ["x", "h", "n", "F", "G", "A", "B"],
                    "brief": r"""
Each rule below is two or three lines of algebra and one limit. Doing them in order
also shows how they lean on one another: the quotient rule is the product rule
rearranged, and the square root is the power rule proved by an argument the binomial
theorem cannot reach.

For the general rules, fix the point $x$ and write

$$F = f(x), \qquad G = g(x), \qquad A = f'(x), \qquad B = g'(x),$$

which are four constants once $x$ is fixed. Write fractions as `\frac{a}{b}`, and give
each answer as an expression — no primes, no limit signs, no equals sign.
""",
                    "steps": [
                        {
                            "prompt": "Start concrete. Expand $(x+h)^{3} - x^{3}$ completely and collect it in powers of $h$. Write the result.",
                            "answer": "3x^{2}h + 3xh^{2} + h^{3}",
                            "placeholder": "three terms, each carrying an h",
                            "hint": "$(x+h)^{3} = x^{3} + 3x^{2}h + 3xh^{2} + h^{3}$, and the $x^{3}$ cancels.",
                            "deconstruct": [
                                "The binomial coefficients for the cube are $1, 3, 3, 1$.",
                                "So $(x+h)^{3} = x^{3} + 3x^{2}h + 3xh^{2} + h^{3}$.",
                                "Subtracting $x^{3}$ removes the only term without an $h$, which is why the division by $h$ that comes next is going to work.",
                            ],
                        },
                        {
                            "prompt": "Divide that by $h$ — legal, since a limit never evaluates at $h = 0$ — and then let $h \\to 0$. Write the derivative of $x^{3}$.",
                            "answer": "3x^{2}",
                            "hint": "After dividing you have $3x^{2} + 3xh + h^{2}$; every term but the first still carries an $h$.",
                        },
                        {
                            "prompt": "Now the general case for a positive whole number $n$. In $(x+h)^{n} - x^{n}$, every term beyond the second carries $h^{2}$ or higher and dies in the limit, so only the coefficient of $h^{1}$ survives the division. Write the derivative of $x^{n}$.",
                            "answer": "nx^{n-1}",
                            "placeholder": "a coefficient times a power of x",
                            "hint": "The $h^{1}$ term of the binomial expansion is $\\binom{n}{1}x^{n-1}h$, and $\\binom{n}{1} = n$.",
                            "deconstruct": [
                                "$(x+h)^{n} = x^{n} + \\binom{n}{1}x^{n-1}h + \\binom{n}{2}x^{n-2}h^{2} + \\cdots$",
                                "Subtract $x^{n}$, then divide every remaining term by $h$.",
                                "The $h^{1}$ term becomes $\\binom{n}{1}x^{n-1} = nx^{n-1}$ with no $h$ left in it; everything after it keeps at least one $h$ and vanishes.",
                            ],
                        },
                        {
                            "prompt": "The product rule. Split $f(x+h)g(x+h) - f(x)g(x)$ as $[f(x+h)-f(x)]\\,g(x+h) + f(x)[g(x+h)-g(x)]$, divide by $h$, and let $h \\to 0$, using the continuity of $g$ to send $g(x+h)$ to $G$. Write $(fg)'$ in the letters above.",
                            "answer": "AG + FB",
                            "placeholder": "two terms",
                            "hint": "Each bracket over $h$ becomes a derivative; each surviving factor becomes a value.",
                            "deconstruct": [
                                "$\\dfrac{f(x+h)-f(x)}{h} \\to A$, and the factor $g(x+h) \\to G$.",
                                "$\\dfrac{g(x+h)-g(x)}{h} \\to B$, and the factor $f(x)$ is already $F$.",
                                "Adding the two limits gives $AG + FB$ — one term per side of the rectangle, and nothing for the corner.",
                            ],
                        },
                        {
                            "prompt": "The quotient rule, without memorising it. Let $q = F/G$. Since $f = qg$, the product rule gives $A = q'G + qB$. Solve that for $q'$ and substitute $q = F/G$. Write $q'$ as a single fraction.",
                            "answer": "\\frac{AG - FB}{G^{2}}",
                            "placeholder": "one fraction over G squared",
                            "hint": "$q' = \\dfrac{A - qB}{G}$; now put $q = F/G$ and clear the inner fraction.",
                            "deconstruct": [
                                "From $A = q'G + qB$, isolate: $q' = \\dfrac{A - qB}{G}$.",
                                "Substitute $q = F/G$: $q' = \\dfrac{A - (F/G)B}{G}$.",
                                "Multiply top and bottom by $G$: $q' = \\dfrac{AG - FB}{G^{2}}$ — and the minus sign is there because $qB$ was moved across, not because of a convention.",
                            ],
                        },
                        {
                            "prompt": "Finally, an exponent the binomial theorem cannot reach. Let $y = \\sqrt{x}$ for $x > 0$, so $y^{2} = x$. Differentiating both sides with respect to $x$ gives $2y\\,y' = 1$. Solve for $y'$ and write it in terms of $x$.",
                            "answer": "\\frac{1}{2\\sqrt{x}}",
                            "placeholder": "a fraction with a root underneath",
                            "hint": "$y' = 1/(2y)$, and $y$ is $\\sqrt{x}$.",
                            "deconstruct": [
                                "$2y\\,y' = 1$ gives $y' = \\dfrac{1}{2y}$.",
                                "Replace $y$ by $\\sqrt{x}$: $y' = \\dfrac{1}{2\\sqrt{x}}$.",
                                "Compare with the power rule at $n = 1/2$: $\\tfrac{1}{2}x^{-1/2}$ is the same number, reached by an argument that never expanded a binomial.",
                            ],
                        },
                    ],
                    "closing": r"""
Five rules, and not one of them was asserted. That matters more than it looks: the
quotient rule is the rule most often misremembered, and the derivation above is short
enough to redo on the spot when the numerator's order is in doubt.

The last step is the one to keep. The power rule was proved by the binomial theorem for
$n = 1, 2, 3, \ldots$, and the binomial theorem has nothing to say about $n = 1/2$ —
there is no expansion of $(x+h)^{1/2}$ into finitely many terms. Squaring the relation
first, and differentiating what results, is a completely different argument that happens
to give an answer matching the same formula. Module 7 names that technique and makes it
general, which is where every rational exponent is finally covered.

Where the working stops: the square-root argument assumed $y' $ exists before solving
for it, and at $x = 0$ it does not. The graph of $\sqrt{x}$ has a vertical tangent at
the origin, $1/(2\sqrt{x})$ grows without bound as $x \to 0^{+}$, and the function is
not differentiable there at all — a reminder that solving for a derivative presumes you
already know there is one to solve for.
""",
                },
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
                "The inverse rule `(f_inv)'(y) = 1/f'(f_inv(y))`, which is the chain rule applied to `f(f_inv(y)) = y`: reflecting a graph in the line `y = x` reciprocates its slope, so it needs `f'` non-zero there — a horizontal tangent reflects into a vertical one",
                "A scale factor inside the function comes back out as a multiplier, which is why every rate a circuit produces carries its frequency with it",
            ],
            "read": [
                {
                    "title": "One rate feeding another",
                    "minutes": 11,
                    "body": r"""
A tank is filling, and a float rides on the surface. The water level rises at
$0.4$ cm per second. A pointer attached to the float moves $3$ cm across a dial for
every centimetre the float rises. How fast does the pointer move?

Nobody needs calculus for this: $3 \times 0.4 = 1.2$ cm per second. The two rates
multiply, and the units say why they must. Centimetres of pointer *per centimetre of
water*, times centimetres of water *per second*, leaves centimetres of pointer per
second. The middle quantity cancels the way a unit cancels, and the chain rule is that
observation made exact for rates that are not constant.

## The statement, and what each part is evaluated at

If $y = f(u)$ and $u = g(x)$, then $y = f(g(x))$ and

$$\frac{d}{dx}f(g(x)) = f'(g(x)) \cdot g'(x).$$

Read the first factor carefully. It is $f'$ **evaluated at $g(x)$**, not at $x$. The
float example makes the reason concrete: the dial's gearing might vary with height, in
which case the gearing that matters is the one at *the height the float is currently
at*, not at some number that happens to be the clock reading. Evaluating the outer
derivative at the wrong point is the second most common error in this rule, and it is
invisible when the inner function happens to be the identity.

The second factor is the one that gets dropped. In Leibniz notation the rule reads

$$\frac{dy}{dx} = \frac{dy}{du}\cdot\frac{du}{dx},$$

which looks like the $du$ cancelling. It is a good mnemonic and a bad proof, because
$dy/du$ is not a fraction — it is a limit of fractions, and the numerators and
denominators inside it are all heading to zero.

## Deriving it, and being honest about the gap

The natural argument writes the difference quotient in two pieces:

$$\frac{\Delta y}{\Delta x} = \frac{\Delta y}{\Delta u}\cdot\frac{\Delta u}{\Delta x},$$

then sends $\Delta x \to 0$, notes that $\Delta u \to 0$ because $g$ is continuous, and
concludes that the two factors tend to $f'(u)$ and $g'(x)$.

There is a hole in it, and it is worth seeing rather than being protected from. The
first factor divides by $\Delta u$, which requires $\Delta u \neq 0$. For most functions
that is fine for all small enough $\Delta x$. It is not always fine. Take

$$g(x) = x^{2}\sin(1/x) \quad (x \neq 0), \qquad g(0) = 0.$$

This $g$ is differentiable at $0$ with $g'(0) = 0$, yet $g(x) = 0$ at $x = 1/(k\pi)$
for every whole $k$ — points arbitrarily close to the origin. So $\Delta u$ is exactly
zero infinitely often on the way in, and the division is illegal infinitely often.

The conclusion survives. The repair replaces the quotient $\Delta y/\Delta u$ by a
function that equals it when $\Delta u \neq 0$ and equals $f'(u)$ when $\Delta u = 0$;
that function is continuous at zero precisely because $f$ is differentiable, and the
product argument then goes through with no division at all. The rule is true. The
one-line proof of it is not, and knowing which is which is the difference between using
a theorem and reciting one.

## Peeling, with numbers at the end

Compositions come in layers, and the rule applies one layer at a time from the outside
in. Take

$$p(x) = (2x^{3}-5)^{4}.$$

Outer layer: a fourth power, whose derivative is $4(\;\cdot\;)^{3}$ evaluated at the
inside, giving $4(2x^{3}-5)^{3}$. Inner layer: the derivative of $2x^{3}-5$, which is
$6x^{2}$. Multiply:

$$p'(x) = 4(2x^{3}-5)^{3}\cdot 6x^{2} = 24x^{2}(2x^{3}-5)^{3}.$$

Now put a number through it. At $x = 1$ the inside is $2 - 5 = -3$, so
$p'(1) = 24 \cdot 1 \cdot (-27) = -648$, and $p(1) = (-3)^{4} = 81$.

Check it numerically, as Module 3 insisted. $p(1.001) = 80.35329708$, so the forward
difference is

$$\frac{80.35329708 - 81}{0.001} = -646.70.$$

That is $-648$ to within about $0.2\%$ — and the discrepancy is not sloppiness, it is
the first-order truncation error of a forward difference, which Module 3 showed is
proportional to $h$. Halving $h$ would halve it. Had the answer been $-162$ (the inner
factor dropped) or $-2$ (the outer power forgotten), no step size would have rescued it.

Three layers work the same way. For $q(x) = (1 + \sqrt{x})^{5}$, the outer fifth power
gives $5(1+\sqrt{x})^{4}$, the middle layer contributes the derivative of $1 + \sqrt{x}$,
which is $1/(2\sqrt{x})$ from Module 4, and there is no third layer. So

$$q'(x) = \frac{5(1+\sqrt{x})^{4}}{2\sqrt{x}}.$$

## The mistake, and why it is tempting

The inner factor is dropped more often than any other error in differentiation, and the
reason is that it is invisible in every example used to introduce the rules. For
$d/dx\,x^{5}$ the inner function is $x$ itself, its derivative is $1$, and the chain
rule multiplies by $1$. The whole of Module 4 can be worked without ever noticing the
factor exists. Then the inside becomes $3x+1$, the factor becomes $3$, and the habit
formed on a hundred correct answers produces a wrong one.

The test that catches it costs nothing: **substitute a number into both the function and
the claimed derivative, and compare against a difference quotient.** A missing constant
factor is a factor-of-three error, which no rounding can disguise.

## The inverse rule, in one line

An inverse function undoes $f$: $f(f^{-1}(y)) = y$ for every $y$ in range. That is an
identity, so both sides can be differentiated with respect to $y$. The left side is a
composition, so the chain rule applies; the right side has derivative $1$:

$$f'\big(f^{-1}(y)\big)\cdot \big(f^{-1}\big)'(y) = 1,
\qquad\text{hence}\qquad
\big(f^{-1}\big)'(y) = \frac{1}{f'\big(f^{-1}(y)\big)}.$$

No new idea was needed — the inverse rule is the chain rule applied to a statement that
was true by definition. Geometrically it says that reflecting a graph in the line
$y = x$ swaps rise with run, so slopes turn into their reciprocals.

Worked: $f(x) = x^{3}+x$ has $f'(x) = 3x^{2}+1$, which is positive everywhere, so $f$ is
strictly increasing and an inverse exists. Since $f(1) = 2$, the point that maps to $2$
is $x = 1$, and $f'(1) = 4$. Therefore $(f^{-1})'(2) = 1/4$. Notice what was *not* done:
$f'(2) = 13$ never entered, because the rule evaluates $f'$ at the input of $f$, and the
input of $f$ here is $1$.

## Where it stops

The inverse rule divides by $f'(f^{-1}(y))$, so it says nothing wherever that derivative
is zero — and the geometry explains what goes wrong rather than merely forbidding it.

Take $f(x) = x^{3}$, whose inverse is $y^{1/3}$. At the origin $f'(0) = 0$: the graph of
$x^{3}$ has a horizontal tangent there. Reflect a horizontal line in $y = x$ and you get
a vertical one, so the inverse has a vertical tangent at $y = 0$ and no finite
derivative. The formula reports this honestly, since $(y^{1/3})' = 1/(3y^{2/3})$ grows
without bound as $y \to 0$. The inverse function still exists and is continuous
everywhere; it is differentiability, not invertibility, that fails.

The chain rule itself has the milder hypothesis you would expect: $g$ differentiable at
$x$, and $f$ differentiable at $g(x)$ — again *at $g(x)$*, not at $x$. A composition
whose inner function lands exactly on the outer function's corner is not covered, which
is why $\big||x| - 1\big|$ needs care at $x = \pm 1$ and at $0$.
""",
                },
            ],
            "derive": [
                {
                    "title": "Peeling layers, and reading a slope backwards",
                    "minutes": 12,
                    "vars": ["x", "y", "u"],
                    "brief": r"""
The first three steps are the chain rule used forwards, on compositions that get one
layer deeper each time. The last two turn it round: the inverse rule is not a new
theorem, it is this one applied to $f(f^{-1}(y)) = y$.

Write fractions as `\frac{a}{b}` and roots as `\sqrt{x}`, and give every answer as an
expression with no primes and no equals sign.
""",
                    "steps": [
                        {
                            "prompt": "Differentiate $p(x) = (2x^{3}-5)^{4}$. Take the outer power first, leave the inside alone, then multiply by the derivative of the inside. Write $p'(x)$.",
                            "answer": "24x^{2}(2x^{3}-5)^{3}",
                            "placeholder": "a coefficient, a power of x, and the bracket to a power",
                            "hint": "The outer layer gives $4(2x^{3}-5)^{3}$; the inside differentiates to $6x^{2}$.",
                            "deconstruct": [
                                "Outer: $\\dfrac{d}{du}u^{4} = 4u^{3}$, evaluated at $u = 2x^{3}-5$.",
                                "Inner: $\\dfrac{d}{dx}(2x^{3}-5) = 6x^{2}$.",
                                "Their product is $4(2x^{3}-5)^{3}\\cdot 6x^{2} = 24x^{2}(2x^{3}-5)^{3}$.",
                            ],
                        },
                        {
                            "prompt": "Put a number through it: at $x = 1$ the inside is $-3$. Write $p'(1)$ as a single number.",
                            "answer": "-648",
                            "hint": "$24 \\cdot 1 \\cdot (-3)^{3}$, and an odd power keeps the sign.",
                        },
                        {
                            "prompt": "A negative outer exponent, so the inside cannot be ignored either. Differentiate $r(x) = \\dfrac{1}{(3x+2)^{2}}$, that is $(3x+2)^{-2}$. Write $r'(x)$.",
                            "answer": "\\frac{-6}{(3x+2)^{3}}",
                            "placeholder": "a fraction with a cube underneath",
                            "hint": "The outer rule gives $-2(3x+2)^{-3}$ and the inner derivative is $3$.",
                            "deconstruct": [
                                "Write it as a power: $r(x) = (3x+2)^{-2}$.",
                                "Outer: $-2(3x+2)^{-3}$. Inner: $3$.",
                                "Multiplying gives $-6(3x+2)^{-3}$, which is $\\dfrac{-6}{(3x+2)^{3}}$.",
                            ],
                        },
                        {
                            "prompt": "Three layers now. Differentiate $q(x) = (1 + \\sqrt{x})^{5}$ for $x > 0$, using $\\dfrac{d}{dx}\\sqrt{x} = \\dfrac{1}{2\\sqrt{x}}$ from Module 4. Write $q'(x)$.",
                            "answer": "\\frac{5(1+\\sqrt{x})^{4}}{2\\sqrt{x}}",
                            "placeholder": "a bracket to the fourth over a root",
                            "hint": "Outer gives $5(1+\\sqrt{x})^{4}$; the inside $1 + \\sqrt{x}$ differentiates to $1/(2\\sqrt{x})$.",
                            "deconstruct": [
                                "Outer: $5(1+\\sqrt{x})^{4}$, evaluated at the whole inside.",
                                "Inner: the $1$ contributes nothing, and $\\sqrt{x}$ contributes $\\dfrac{1}{2\\sqrt{x}}$.",
                                "The product is $\\dfrac{5(1+\\sqrt{x})^{4}}{2\\sqrt{x}}$.",
                            ],
                        },
                        {
                            "prompt": "Turn it round. $f(x) = x^{3}+x$ has $f'(x) = 3x^{2}+1$, and $f(1) = 2$. Differentiating $f(f^{-1}(y)) = y$ gives $f'(f^{-1}(y))\\cdot (f^{-1})'(y) = 1$. Write $(f^{-1})'(2)$ as a number.",
                            "answer": "\\frac{1}{4}",
                            "hint": "The point that maps to $2$ is $x = 1$, so the rule needs $f'(1)$, not $f'(2)$.",
                            "deconstruct": [
                                "$f^{-1}(2) = 1$, because $f(1) = 1 + 1 = 2$.",
                                "$f'(1) = 3 + 1 = 4$.",
                                "The rule reciprocates it: $(f^{-1})'(2) = \\dfrac{1}{4}$.",
                            ],
                        },
                        {
                            "prompt": "The same rule where it is about to break. $f(x) = x^{3}$ has inverse $f^{-1}(y) = y^{1/3}$, and $f'(x) = 3x^{2}$. Write $(f^{-1})'(y)$ as an expression in $y$.",
                            "answer": "\\frac{1}{3y^{2/3}}",
                            "placeholder": "a fraction with a fractional power of y underneath",
                            "hint": "Evaluate $f'$ at $f^{-1}(y) = y^{1/3}$, then reciprocate: $3(y^{1/3})^{2} = 3y^{2/3}$.",
                            "deconstruct": [
                                "$f^{-1}(y) = y^{1/3}$, so $f'(f^{-1}(y)) = 3(y^{1/3})^{2}$.",
                                "$(y^{1/3})^{2} = y^{2/3}$, so the denominator is $3y^{2/3}$.",
                                "Reciprocating gives $\\dfrac{1}{3y^{2/3}}$.",
                            ],
                        },
                    ],
                    "closing": r"""
The last two steps are the same rule and they end very differently, which is the point of
putting them next to each other.

For $x^{3}+x$ the derivative $3x^{2}+1$ is never zero, the function is strictly
increasing, and the inverse is differentiable everywhere. For $x^{3}$ the derivative
vanishes at the origin, and the formula $1/(3y^{2/3})$ grows without bound as
$y \to 0$ — correctly, because the graph of $y^{1/3}$ has a vertical tangent there. The
inverse still exists; every real number has exactly one cube root, and the function is
continuous. What fails is differentiability, and only at that one point.

That is the general picture. A horizontal tangent on $f$ reflects into a vertical tangent
on $f^{-1}$, and a vertical tangent is not a slope. So the inverse rule carries the
hypothesis $f'(f^{-1}(y)) \neq 0$, and when the hypothesis fails the right conclusion is
not "the inverse does not exist" but "the inverse is not differentiable here".

Where the working stops: every step above assumed the composition's inner value lands
somewhere the outer function is differentiable. Step 4 needs $x > 0$ for that reason —
at $x = 0$ the inner $\sqrt{x}$ has no derivative, and no amount of care with the outer
fifth power repairs it.
""",
                },
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
            "read": [
                {
                    "title": "Where these derivatives actually come from",
                    "minutes": 14,
                    "body": r"""
Every derivative so far was earned. The power rule came out of a binomial expansion, the
product rule out of a rectangle, the quotient rule out of the product rule. This module
is where a course usually stops earning them and starts issuing a table: $\sin$ goes to
$\cos$, $e^{x}$ goes to itself, $\ln$ goes to $1/x$. Memorise these.

Two of those are worth deriving in full, because the derivations explain things the table
cannot. One of them is also the place where a course can be caught being circular, and
this one nearly is: the quiz for this module asks why $\lim_{h\to 0}\sin(h)/h = 1$ must
be proved geometrically — a limit the course has been using and has never proved. So it
gets proved here first.

## The limit everything trigonometric rests on

Draw a unit circle and an angle $h$ with $0 < h < \pi/2$, measured **in radians**. Three
regions sit inside one another:

- the triangle with vertices at the centre, at $(1,0)$, and at the point on the circle,
  whose area is $\tfrac{1}{2}\sin h$;
- the circular sector between the two radii, whose area is $\tfrac{1}{2}h$;
- the triangle with vertices at the centre, at $(1,0)$, and at the point vertically
  above $(1,0)$ on the tangent line, whose area is $\tfrac{1}{2}\tan h$.

Each contains the one before it, so

$$\tfrac{1}{2}\sin h \;<\; \tfrac{1}{2}h \;<\; \tfrac{1}{2}\tan h.$$

Multiply by $2$ and divide by $\sin h$, which is positive on this range:

$$1 \;<\; \frac{h}{\sin h} \;<\; \frac{1}{\cos h}.$$

Take reciprocals, which reverses the inequalities:

$$\cos h \;<\; \frac{\sin h}{h} \;<\; 1.$$

Both ends tend to $1$ as $h \to 0$, so Module 2's squeeze theorem forces the middle to as
well. The function $\sin(h)/h$ is even, so the same bound covers negative $h$, and

$$\lim_{h\to 0}\frac{\sin h}{h} = 1.$$

Numerically, at $h = 0.01$ the quotient is $0.99998333$ and $\cos h = 0.99995$, so the
squeeze is doing visible work rather than being a formality.

**Where the sector area came from is the hypothesis to watch.** A sector of angle $h$ in
a unit circle has area $h/2$ *only when $h$ is in radians* — that is what the radian is
defined to make true. In degrees the sector has area $\pi h/360$, the squeeze produces
$\pi/180$ instead of $1$, and every derivative below changes. This is not pedantry:
$\frac{d}{dx}\sin(x^{\circ}) = \frac{\pi}{180}\cos(x^{\circ}) \approx
0.01745\cos(x^{\circ})$, and a program that feeds degrees to a routine expecting radians
is wrong by that factor of $57.3$ with no error message.

The companion limit follows from the first by an algebraic trick rather than a new
picture. Multiply by the conjugate:

$$\frac{\cos h - 1}{h} = \frac{\cos^{2}h - 1}{h(\cos h + 1)}
= \frac{-\sin^{2}h}{h(\cos h + 1)}
= -\frac{\sin h}{h}\cdot\frac{\sin h}{\cos h + 1}
\longrightarrow -1 \cdot \frac{0}{2} = 0.$$

At $h = 0.01$ the true value is $-0.005$, small and heading to zero, as promised.

## Sine, in three lines

With both limits in hand, the derivative is the addition formula and nothing else. Using
$\sin(x+h) = \sin x\cos h + \cos x\sin h$:

$$\frac{\sin(x+h)-\sin x}{h}
= \sin x\cdot\frac{\cos h - 1}{h} + \cos x\cdot\frac{\sin h}{h}.$$

Both fractions have known limits, and $\sin x$ and $\cos x$ are constants as far as $h$
is concerned. So the whole thing tends to $\sin x\cdot 0 + \cos x\cdot 1$, giving

$$\frac{d}{dx}\sin x = \cos x.$$

The same three lines with $\cos(x+h) = \cos x\cos h - \sin x\sin h$ give
$\frac{d}{dx}\cos x = -\sin x$, and the minus sign is the one that came from the
addition formula, not from a convention.

Everything else trigonometric is now the quotient rule. For $\tan x = \sin x/\cos x$:

$$\frac{d}{dx}\tan x = \frac{\cos x\cos x - \sin x(-\sin x)}{\cos^{2}x}
= \frac{1}{\cos^{2}x},$$

using $\sin^{2}+\cos^{2} = 1$ at the last step.

## Why $e$ is not an arbitrary number

For any positive base $a$,

$$\frac{a^{x+h}-a^{x}}{h} = a^{x}\cdot\frac{a^{h}-1}{h},$$

because $a^{x+h} = a^{x}a^{h}$ — the variable factors straight out. So

$$\frac{d}{dx}a^{x} = a^{x}\cdot L(a), \qquad L(a) = \lim_{h\to 0}\frac{a^{h}-1}{h},$$

and $L(a)$ is a constant depending only on the base. Note what this already says: **every
exponential is proportional to its own derivative.** The only question left is the
constant of proportionality.

$L(a)$ is the slope of $a^{x}$ where it crosses the vertical axis. For $a = 2$ it is
about $0.693$; for $a = 3$ about $1.099$. Somewhere between $2$ and $3$ is the base where
that slope is exactly $1$, and **that is the definition of $e$** — not $2.71828\ldots$
learned as a decimal, but the base singled out by making its own exponential its own
derivative.

Once $e$ exists, every other base is reached through it. Since $a = e^{\ln a}$, we have
$a^{x} = e^{x\ln a}$, and the chain rule gives

$$\frac{d}{dx}a^{x} = e^{x\ln a}\cdot\ln a = a^{x}\ln a,$$

which also identifies the mystery constant: $L(a) = \ln a$. Checking the arithmetic,
$L(2)$ should be $\ln 2 = 0.6931472$, and the difference quotient at $h = 10^{-6}$ gives
$0.6931474$ — agreeing to six figures, with the discrepancy in the seventh being the
first-order truncation error Module 3 predicted.

## The logarithm, from the inverse rule

No new limit is required. Let $y = \ln x$ for $x > 0$, so $e^{y} = x$. Differentiate both
sides with respect to $x$; the left is a composition, so the chain rule applies:

$$e^{y}\frac{dy}{dx} = 1 \quad\Longrightarrow\quad \frac{dy}{dx} = \frac{1}{e^{y}}
= \frac{1}{x}.$$

That is Module 5's inverse rule doing exactly what it was built for, and it explains a
fact that looks like a coincidence in the table: the derivative of a transcendental
function turns out to be algebraic. Reflecting a graph reciprocates its slopes, and the
reciprocal of $e^{y}$ is $1/x$ once you remember what $e^{y}$ is.

The inverse trigonometric functions go the same way. For $y = \arctan x$ we have
$\tan y = x$, so $\frac{1}{\cos^{2}y}\cdot y' = 1$ and $y' = \cos^{2}y$. Now use
$1 + \tan^{2}y = 1/\cos^{2}y$, which with $\tan y = x$ says $1/\cos^{2}y = 1 + x^{2}$.
Hence

$$\frac{d}{dx}\arctan x = \frac{1}{1+x^{2}},$$

algebraic again, and finite everywhere. At $x = 1$ it equals $1/2$.

For $y = \arcsin x$: $\sin y = x$, so $\cos y\cdot y' = 1$ and $y' = 1/\cos y$. The
principal branch has $y \in (-\pi/2, \pi/2)$, where $\cos y > 0$, so
$\cos y = +\sqrt{1-\sin^{2}y} = \sqrt{1-x^{2}}$ and

$$\frac{d}{dx}\arcsin x = \frac{1}{\sqrt{1-x^{2}}}.$$

The choice of the positive root is the branch choice, not an algebraic step, and it is
where a sign error hides if the branch is left unstated.

## Logarithmic differentiation, worked

When the variable sits in the base *and* the exponent, no single rule applies. Take
$y = x^{x}$ for $x > 0$. Take logarithms first:

$$\ln y = x\ln x.$$

Differentiate both sides with respect to $x$. The left side is a composition, giving
$y'/y$; the right side is a product, giving $\ln x + 1$:

$$\frac{y'}{y} = \ln x + 1
\quad\Longrightarrow\quad
y' = x^{x}\big(1 + \ln x\big).$$

Put a number through it. At $x = 2$: $y = 4$ and $y' = 4(1 + 0.693147) = 6.7726$. A
forward difference with $h = 0.001$ gives $(4.00677933 - 4)/0.001 = 6.7793$, about
$0.1\%$ high — again first-order truncation error, not a mistake in the algebra.

The two wrong answers are instructive because each is *half* right. Freezing the exponent
and using the power rule gives $x\cdot x^{x-1} = x^{x}$. Freezing the base and using the
exponential rule gives $x^{x}\ln x$. Their sum is $x^{x}(1+\ln x)$, the true answer —
which is not a coincidence but the multivariable chain rule showing through: the function
depends on $x$ through two routes, and the total rate is the sum of the two partial
contributions.

## Where these stop

$\ln x$ and its derivative $1/x$ require $x > 0$; the function has no values to the left
of the origin, so it has no rate of change there either. (The identity
$\frac{d}{dx}\ln|x| = 1/x$ covers negative $x$, and it is a different function.)

$\arcsin$ is defined on $[-1,1]$ but its derivative formula only works on the open
interval: at $x = \pm 1$ the denominator $\sqrt{1-x^{2}}$ is zero. That is not a defect
in the algebra — $\sin$ has horizontal tangents at $\pm\pi/2$, and Module 5 showed that a
horizontal tangent reflects into a vertical one.

And $\sin' = \cos$ is a statement about radians. Every derivative in this reading inherits
that, which makes the units of an angle a correctness question rather than a preference.
""",
                },
            ],
            "derive": [
                {
                    "title": "Sine from a squeeze, and the rest from inverses",
                    "minutes": 15,
                    "vars": ["x", "h", "a", "y"],
                    "brief": r"""
Two facts are granted, both proved in the reading by squeezing areas on the unit circle:

$$\lim_{h\to 0}\frac{\sin h}{h} = 1, \qquad \lim_{h\to 0}\frac{\cos h - 1}{h} = 0.$$

Everything below is built from those two and from rules already proved. Write function
names without backslashes — `sin(x)`, `cos(x)`, `ln(x)` — write fractions as
`\frac{a}{b}`, and give each answer as an expression.
""",
                    "steps": [
                        {
                            "prompt": "Expand $\\sin(x+h)$ with the addition formula. Write the result in terms of $\\sin$ and $\\cos$ of $x$ and of $h$.",
                            "answer": "sin(x)cos(h) + cos(x)sin(h)",
                            "placeholder": "two products",
                            "hint": "The formula is sine-cosine plus cosine-sine, in that order.",
                        },
                        {
                            "prompt": "Subtract $\\sin x$ from that and regroup so the two granted limits are visible: collect the terms containing $\\cos(h)$ and $1$ into one bracket. Write $\\sin(x+h) - \\sin(x)$ in that grouped form.",
                            "answer": "sin(x)(cos(h)-1) + cos(x)sin(h)",
                            "placeholder": "a bracket times sin(x), plus a second term",
                            "hint": "$\\sin(x)\\cos(h) - \\sin(x)$ factors as $\\sin(x)(\\cos(h)-1)$.",
                            "deconstruct": [
                                "From the previous step, $\\sin(x+h) - \\sin(x) = \\sin(x)\\cos(h) + \\cos(x)\\sin(h) - \\sin(x)$.",
                                "The first and last terms share a factor of $\\sin(x)$: together they are $\\sin(x)(\\cos(h)-1)$.",
                                "So the difference is $\\sin(x)(\\cos(h)-1) + \\cos(x)\\sin(h)$, and dividing by $h$ now produces exactly the two granted limits.",
                            ],
                        },
                        {
                            "prompt": "Divide by $h$ and take $h \\to 0$. The first bracket over $h$ tends to $0$, the second fraction to $1$, and $\\sin(x)$ and $\\cos(x)$ are constants here. Write the derivative of $\\sin(x)$.",
                            "answer": "cos(x)",
                            "hint": "One term is killed by the limit that goes to zero; the other survives with its coefficient.",
                        },
                        {
                            "prompt": "Now the quotient rule on $\\tan(x) = \\sin(x)/\\cos(x)$, using $\\sin^{2}+\\cos^{2}=1$ to simplify the numerator. Write the derivative of $\\tan(x)$ as a single fraction over a squared cosine.",
                            "answer": "\\frac{1}{cos(x)^{2}}",
                            "placeholder": "one over a squared trig function",
                            "hint": "The numerator is $\\cos(x)\\cos(x) - \\sin(x)(-\\sin(x))$, which is $\\cos^{2}+\\sin^{2}$.",
                            "deconstruct": [
                                "Quotient rule: $\\dfrac{\\cos(x)\\cdot\\cos(x) - \\sin(x)\\cdot(-\\sin(x))}{\\cos(x)^{2}}$.",
                                "The numerator is $\\cos^{2}(x) + \\sin^{2}(x)$, which is $1$.",
                                "So the derivative is $\\dfrac{1}{\\cos(x)^{2}}$.",
                            ],
                        },
                        {
                            "prompt": "Read a slope backwards. For $y = \\arctan(x)$ we have $\\tan(y) = x$, so differentiating gives $\\dfrac{1}{\\cos(y)^{2}}\\cdot y' = 1$, and $1/\\cos^{2}(y) = 1 + \\tan^{2}(y) = 1 + x^{2}$. Write the derivative of $\\arctan(x)$ as an expression in $x$.",
                            "answer": "\\frac{1}{1+x^{2}}",
                            "placeholder": "one over something in x",
                            "hint": "$y' = \\cos^{2}(y)$, and $\\cos^{2}(y)$ is the reciprocal of $1+x^{2}$.",
                            "deconstruct": [
                                "$\\tan(y) = x$ differentiates to $\\dfrac{y'}{\\cos(y)^{2}} = 1$, so $y' = \\cos(y)^{2}$.",
                                "The identity $1 + \\tan^{2}(y) = 1/\\cos(y)^{2}$ with $\\tan(y) = x$ gives $1/\\cos(y)^{2} = 1+x^{2}$.",
                                "Reciprocating, $\\cos(y)^{2} = \\dfrac{1}{1+x^{2}}$, and that is $y'$ — algebraic, with no trigonometry left in it.",
                            ],
                        },
                        {
                            "prompt": "A general base. Rewrite $a^{x}$ as $e^{x\\,ln(a)}$ and apply the chain rule, remembering that $ln(a)$ is a constant. Write the derivative of $a^{x}$.",
                            "answer": "a^{x}ln(a)",
                            "placeholder": "the function itself times a constant",
                            "hint": "The exponential reproduces itself; the inner derivative of $x\\,\\ln(a)$ is $\\ln(a)$.",
                            "deconstruct": [
                                "$a = e^{\\ln(a)}$, so $a^{x} = e^{x\\ln(a)}$.",
                                "The chain rule gives $e^{x\\ln(a)}\\cdot\\ln(a)$.",
                                "Rewriting $e^{x\\ln(a)}$ back as $a^{x}$ leaves $a^{x}\\ln(a)$ — and at $a = e$ the factor is $1$, which is the property that defines $e$.",
                            ],
                        },
                        {
                            "prompt": "The variable in the base and the exponent at once. For $y = x^{x}$ with $x > 0$, take logarithms to get $ln(y) = x\\,ln(x)$, differentiate both sides, then solve. Write the derivative of $x^{x}$.",
                            "answer": "x^{x}(1+ln(x))",
                            "placeholder": "the function itself times a bracket",
                            "hint": "The left side differentiates to $y'/y$; the right side is a product.",
                            "deconstruct": [
                                "Left side: $\\dfrac{d}{dx}\\ln(y) = \\dfrac{y'}{y}$ by the chain rule.",
                                "Right side: $\\dfrac{d}{dx}\\,x\\ln(x) = \\ln(x) + x\\cdot\\dfrac{1}{x} = \\ln(x) + 1$.",
                                "So $y' = y(1+\\ln(x)) = x^{x}(1+\\ln(x))$.",
                            ],
                        },
                    ],
                    "closing": r"""
Nothing above was quoted from a table. Two limits were established by squeezing areas,
and every derivative in the module followed from them together with rules already proved:
the addition formula for sine, the quotient rule for tangent, the inverse rule for
arctangent, the chain rule for a general base, and logarithms for the case where no
single rule applies.

Check the last one numerically, because it is the one that looks like a trick. At
$x = 2$ the formula gives $4(1 + \ln 2) = 6.7726$, and a forward difference with
$h = 0.001$ gives $6.7793$. The gap is $0.1\%$, first order in $h$, exactly as Module 3
said a forward difference behaves.

Where the working stops: the whole chain rests on the sector area being $h/2$, which is
true for radians and for nothing else. In degrees the first limit becomes $\pi/180$, and
step 3 would read $\frac{\pi}{180}\cos(x)$ — a factor of $57.3$, silently, in any program
that mixes the two conventions. The last step also assumed $x > 0$, since $\ln(x)$ is
undefined otherwise; $x^{x}$ does have values at some negative $x$, but not on an
interval, and a derivative needs an interval to live on.
""",
                },
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
            "read": [
                {
                    "title": "Differentiating an equation nobody solved",
                    "minutes": 12,
                    "body": r"""
Every function differentiated so far arrived as $y = \text{something in } x$. Plenty of
curves do not. The circle

$$x^{2} + y^{2} = 25$$

fails the vertical line test — above $x = 3$ there are two points, $y = 4$ and
$y = -4$ — so it is not the graph of any function at all. It still has a tangent at
every point except two, and that tangent still has a slope. Something has to compute it.

You could solve for $y$. The circle splits into $y = \sqrt{25-x^{2}}$ and
$y = -\sqrt{25-x^{2}}$, and you differentiate whichever branch you are standing on. That
works, and it is already annoying: two cases, a sign to keep straight, and a chain rule
either way. Now try it on

$$x^{3} + y^{3} = 3xy,$$

the folium of Descartes. Solving for $y$ means solving a cubic. Nobody does this.

## The method is the chain rule with the outer function left unnamed

Suppose that near the point of interest the curve *is* traced by some differentiable
function $y(x)$ — we will return to when that is safe. Then every appearance of $y$ in
the equation is a function of $x$, and can be differentiated as one.

The only fact needed is Module 5's chain rule. For any power,

$$\frac{d}{dx}\big[y(x)\big]^{3} = 3\big[y(x)\big]^{2}\cdot\frac{dy}{dx},$$

because the outer function is the cube and the inner function is $y$. The factor
$dy/dx$ is the inner derivative — the same factor dropped a hundred times in Module 5,
except that here it cannot be computed away, so it stays in the expression as an unknown
and gets solved for at the end.

That is the whole technique. Differentiate both sides with respect to $x$, treat $y$ as
a function, collect the $dy/dx$ terms, divide.

Compare $\frac{d}{dx}x^{3} = 3x^{2}$. The chain rule applies there too; the inner
derivative is $dx/dx = 1$, and multiplying by $1$ is invisible. That invisibility is
exactly why the factor is so easy to forget the moment the letter changes.

## The circle, worked end to end

Differentiate both sides of $x^{2}+y^{2} = 25$ with respect to $x$:

$$2x + 2y\frac{dy}{dx} = 0.$$

The right-hand side really is a constant and really does differentiate to zero. That does
not make the left-hand side vanish term by term — it makes the two terms cancel each
other. Solve:

$$\frac{dy}{dx} = -\frac{x}{y}.$$

One formula, both branches, no cases. At $(3,4)$ it gives $-3/4$.

**Check it twice, in ways that could have disagreed.** First, the explicit branch: at
$(3,4)$ we are on $y = \sqrt{25-x^{2}}$, whose derivative is $-x/\sqrt{25-x^{2}}$, which
at $x = 3$ is $-3/4$. Second, the geometry: the radius from the origin to $(3,4)$ has
slope $4/3$, and a tangent to a circle is perpendicular to its radius, so the tangent
slope must be the negative reciprocal $-3/4$. Three routes, one answer.

Notice also what $-x/y$ says about the lower branch. At $(3,-4)$ it gives $+3/4$, which
is right: the bottom of the circle rises where the top falls.

## The second derivative, implicitly

The same machinery differentiates again. Starting from $y' = -x/y$ and using the quotient
rule, remembering that $y$ is a function of $x$:

$$y'' = -\frac{y - x y'}{y^{2}}.$$

Substitute $y' = -x/y$:

$$y'' = -\frac{y + x^{2}/y}{y^{2}} = -\frac{y^{2}+x^{2}}{y^{3}} = -\frac{25}{y^{3}},$$

where the last step used the original equation, which is legal because every point under
discussion lies on it. At $(3,4)$ this is $-25/64 = -0.3906$, negative — the upper
branch is concave down, which is what the top of a circle looks like. On the lower branch
$y^{3}$ is negative and $y''$ is positive, concave up, which is what the bottom looks
like. The formula got both without being told which branch it was on.

## The folium, where there is no alternative

For $x^{3}+y^{3} = 3xy$, differentiate term by term. The left gives $3x^{2}+3y^{2}y'$;
the right is a product, so it gives $3y + 3xy'$:

$$3x^{2}+3y^{2}y' = 3y + 3xy'.$$

Collect the $y'$ terms on one side and divide by $3$:

$$y'(y^{2}-x) = y - x^{2}, \qquad \frac{dy}{dx} = \frac{y-x^{2}}{y^{2}-x}.$$

The point $(4/3,\,2/3)$ is on the curve — $\frac{64}{27}+\frac{8}{27} = \frac{72}{27}$
and $3\cdot\frac{4}{3}\cdot\frac{2}{3} = \frac{8}{3} = \frac{72}{27}$ — and there

$$\frac{dy}{dx} = \frac{2/3 - 16/9}{4/9 - 4/3} = \frac{-10/9}{-8/9} = \frac{5}{4}.$$

At $(3/2,\,3/2)$, which is also on the curve, the slope is $-1$ — as symmetry demands,
since the equation is unchanged when $x$ and $y$ are swapped, so the curve is symmetric
about the line $y = x$ and must cross it perpendicularly.

## Related rates: the same rule, with $t$ underneath

Nothing changes if the independent variable is time. Differentiate the relation with
respect to $t$, and every variable brings its own rate along.

Take two resistors in parallel:

$$\frac{1}{R} = \frac{1}{R_{1}} + \frac{1}{R_{2}}.$$

Suppose $R_{1} = 1.00\ \text{k}\Omega$ with a temperature coefficient of
$+200$ ppm/$^{\circ}$C, $R_{2} = 2.20\ \text{k}\Omega$ and stable, and the board is
warming at $2.5\ ^{\circ}$C/s. How fast is the parallel combination drifting?

First the rate of $R_{1}$ itself: $200$ ppm/$^{\circ}$C of $1000\ \Omega$ is
$0.2\ \Omega/^{\circ}$C, and at $2.5\ ^{\circ}$C/s that is
$dR_{1}/dt = 0.5\ \Omega/\text{s}$.

Now differentiate the relation with respect to $t$. Each term is a reciprocal, so each
picks up a $-1/(\;\cdot\;)^{2}$ from the chain rule, and $R_{2}$ is constant so its term
dies:

$$-\frac{1}{R^{2}}\frac{dR}{dt} = -\frac{1}{R_{1}^{2}}\frac{dR_{1}}{dt}
\quad\Longrightarrow\quad
\frac{dR}{dt} = \left(\frac{R}{R_{1}}\right)^{2}\frac{dR_{1}}{dt}.$$

That result is worth keeping: **the parallel combination drifts by the square of the
divider ratio.** Numerically, $R = (1000)(2200)/3200 = 687.5\ \Omega$, so
$R/R_{1} = 0.6875$, its square is $0.4727$, and

$$\frac{dR}{dt} = 0.4727 \times 0.5 = 0.236\ \Omega/\text{s}.$$

The sensitivity factor being well under $1$ is the point of the exercise: paralleling a
drifting resistor with a stable one does not merely dilute the drift, it attenuates it
quadratically.

## The mistake this technique exists to prevent

Substituting the instantaneous numbers before differentiating. It is tempting because the
numbers are known and the expression is shorter afterwards, and it is always wrong, in a
way that is worth seeing rather than being warned about.

In the balloon problem, $V = \frac{4}{3}\pi r^{3}$ with $r = 5$: substitute first and you
have $V = \frac{500\pi}{3}$, a constant. Its derivative is zero. The volume is not
changing — except that it obviously is, and what was actually computed was the rate of
change of a number, which is always zero.

The same trap in the circle: fix $y = 4$ first and the equation becomes $x^{2} = 9$,
which has no $y$ left in it to differentiate. **A value is a snapshot; a relation is what
holds while things move.** Differentiate the relation, then take the snapshot.

## Where it stops

Everything above assumed a differentiable $y(x)$ exists near the point. That assumption
has a name — the implicit function theorem — and it can fail, in two ways that both show
up as the formula misbehaving rather than as a silent wrong answer.

**Vertical tangents.** On the circle at $(5,0)$, the formula $-x/y$ divides by zero.
Nothing is broken: the curve genuinely has a vertical tangent there, no interval around
$x = 5$ contains two branches to choose between, and no function $y(x)$ describes the
curve near that point. The undefined expression is the honest report.

**Self-intersections.** The folium passes through the origin twice, along two different
tangent lines. There is no single slope, and the formula returns $\frac{0-0}{0-0}$,
refusing to name one. Again the arithmetic is telling the truth.

In both cases the rule is the same: when the denominator of an implicit derivative
vanishes, look at the curve before looking for an algebra mistake.
""",
                },
            ],
            "derive": [
                {
                    "title": "A curve that is not a graph, and a rate that follows",
                    "minutes": 13,
                    "vars": ["x", "y", "R", "R_1", "R_2", "k"],
                    "brief": r"""
The rule throughout: $y$ is a function of $x$, so every $y$ term contributes a $dy/dx$
factor by the chain rule, and $dy/dx$ is then solved for like any other unknown.

Answers are expressions in the letters shown — no $dy/dx$, no primes, no equals sign.
Write fractions as `\frac{a}{b}`.
""",
                    "steps": [
                        {
                            "prompt": "Differentiate $x^{2}+y^{2} = 25$ with respect to $x$, which gives $2x + 2y\\,y' = 0$, and solve for $y'$. Write it as an expression in $x$ and $y$.",
                            "answer": "-\\frac{x}{y}",
                            "placeholder": "a ratio of the two coordinates",
                            "hint": "Move the $2x$ across and divide by $2y$.",
                            "deconstruct": [
                                "$2y\\,y' = -2x$.",
                                "Divide both sides by $2y$, legal wherever $y \\neq 0$.",
                                "$y' = -\\dfrac{x}{y}$ — one formula covering both branches of the circle.",
                            ],
                        },
                        {
                            "prompt": "Evaluate that at the point $(3, 4)$. Write the number.",
                            "answer": "-\\frac{3}{4}",
                            "hint": "Substitute $x = 3$ and $y = 4$.",
                        },
                        {
                            "prompt": "Differentiate again. The quotient rule on $y' = -x/y$ gives $y'' = -\\dfrac{y - x y'}{y^{2}}$; substitute $y' = -x/y$ and then use $x^{2}+y^{2} = 25$ to simplify. Write $y''$ as an expression in $y$ alone.",
                            "answer": "-\\frac{25}{y^{3}}",
                            "placeholder": "a constant over a power of y",
                            "hint": "After substituting you have $-\\dfrac{y + x^{2}/y}{y^{2}}$; combine the numerator over $y$.",
                            "deconstruct": [
                                "Substituting $y' = -x/y$ turns $y - xy'$ into $y + \\dfrac{x^{2}}{y}$.",
                                "Over the common denominator $y$, that is $\\dfrac{y^{2}+x^{2}}{y}$, so $y'' = -\\dfrac{y^{2}+x^{2}}{y^{3}}$.",
                                "Every point on the curve satisfies $x^{2}+y^{2} = 25$, so the numerator is $25$ and $y'' = -\\dfrac{25}{y^{3}}$.",
                            ],
                        },
                        {
                            "prompt": "A curve with no solved form. Differentiate $x^{3}+y^{3} = 3xy$ with respect to $x$ — the right-hand side needs the product rule — then collect the $y'$ terms and solve. Write $y'$ as a single fraction in $x$ and $y$.",
                            "answer": "\\frac{y-x^{2}}{y^{2}-x}",
                            "placeholder": "one fraction, both letters in each part",
                            "hint": "You get $3x^{2}+3y^{2}y' = 3y + 3xy'$; gather the $y'$ terms on one side.",
                            "deconstruct": [
                                "Left: $3x^{2} + 3y^{2}y'$. Right: $3y + 3xy'$ by the product rule on $3xy$.",
                                "Gather: $3y^{2}y' - 3xy' = 3y - 3x^{2}$, so $y'(y^{2}-x) = y - x^{2}$ after dividing by $3$.",
                                "Hence $y' = \\dfrac{y-x^{2}}{y^{2}-x}$.",
                            ],
                        },
                        {
                            "prompt": "The point $(4/3,\\, 2/3)$ lies on that curve. Evaluate the slope there. Write the number.",
                            "answer": "\\frac{5}{4}",
                            "placeholder": "a fraction in lowest terms",
                            "hint": "The numerator is $\\tfrac{2}{3}-\\tfrac{16}{9}$ and the denominator is $\\tfrac{4}{9}-\\tfrac{4}{3}$; both are negative.",
                            "deconstruct": [
                                "Numerator: $\\dfrac{2}{3} - \\left(\\dfrac{4}{3}\\right)^{2} = \\dfrac{6}{9} - \\dfrac{16}{9} = -\\dfrac{10}{9}$.",
                                "Denominator: $\\left(\\dfrac{2}{3}\\right)^{2} - \\dfrac{4}{3} = \\dfrac{4}{9} - \\dfrac{12}{9} = -\\dfrac{8}{9}$.",
                                "The two minus signs cancel: $\\dfrac{10}{8} = \\dfrac{5}{4}$.",
                            ],
                        },
                        {
                            "prompt": "Now a rate. Two resistors in parallel satisfy $\\dfrac{1}{R} = \\dfrac{1}{R_1} + \\dfrac{1}{R_2}$ with $R_2$ constant. Differentiating with respect to time gives $-\\dfrac{1}{R^{2}}\\dfrac{dR}{dt} = -\\dfrac{1}{R_1^{2}}k$, where $k$ is $dR_1/dt$. Solve for $dR/dt$ and write it in terms of $R$, $R_1$ and $k$.",
                            "answer": "\\frac{R^{2}}{R_1^{2}}k",
                            "placeholder": "a squared ratio times k",
                            "hint": "Multiply both sides by $-R^{2}$; the minus signs cancel.",
                            "deconstruct": [
                                "Both sides carry a minus sign, so they cancel: $\\dfrac{1}{R^{2}}\\dfrac{dR}{dt} = \\dfrac{k}{R_1^{2}}$.",
                                "Multiply through by $R^{2}$.",
                                "$\\dfrac{dR}{dt} = \\dfrac{R^{2}}{R_1^{2}}k$, which is the square of the ratio $R/R_1$ times the driving rate.",
                            ],
                        },
                    ],
                    "closing": r"""
The last step is worth a number. With $R_1 = 1.00\ \text{k}\Omega$ and
$R_2 = 2.20\ \text{k}\Omega$, the parallel value is $687.5\ \Omega$, so
$R/R_1 = 0.6875$ and the sensitivity factor $(R/R_1)^{2}$ is $0.4727$. A drift of
$0.5\ \Omega/\text{s}$ in $R_1$ therefore shows up as $0.236\ \Omega/\text{s}$ in the
combination. Paralleling a drifting resistor with a stable one attenuates the drift
quadratically, not merely proportionally — a conclusion no amount of staring at the
formula for $R$ would have produced, and three lines of implicit differentiation did.

Two habits are worth carrying out of this. **Differentiate the relation, then substitute
the instantaneous values**, never the other way round: a number fixed early has its rate
silently set to zero, and the calculation returns a confident $0$. And **read the
denominator**. Step 1's answer divides by $y$, step 4's by $y^{2}-x$, step 6's by
nothing at all — and where those denominators vanish, the method is not failing, it is
reporting that no differentiable branch $y(x)$ exists there.

Where the working stops: on the circle at $(5,0)$ the tangent is vertical and $-x/y$ is
undefined, correctly. On the folium at the origin the curve crosses itself, the formula
gives $\frac{0}{0}$, and there are genuinely two tangent lines to choose between. Both
are cases of the implicit function theorem's hypothesis failing, and in both the
arithmetic tells the truth rather than producing a plausible wrong number.
""",
                },
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
                "It also implies in one direction only: if the derivative quotient has a limit the original has the same one, but a derivative quotient with no limit proves nothing — `(x + sin(x))/x` tends to 1 while `(1 + cos(x))/1` oscillates forever",
            ],
            "read": [
                {
                    "title": "The theorem that lets a derivative speak about the function",
                    "minutes": 13,
                    "body": r"""
Two gantries stand $12$ km apart on a motorway. A car passes the first at 10:00:00 and
the second at 10:08:00, so its average speed was $90$ km/h in a $100$ km/h limit. The
driver was never photographed exceeding anything. Was the car ever doing exactly
$90$ km/h?

Yes, and the reason is a theorem rather than an intuition. Speed is continuous, the
journey took a positive amount of time, and a continuous quantity that averages $90$ must
have equalled $90$ at some instant. That is the mean value theorem, and it is the
statement this module exists to prove and then spend.

## Why it is needed at all

Every derivative computed so far is **local**: $f'(a)$ describes the function in an
arbitrarily small neighbourhood of $a$ and, on its own, says nothing about what happens a
finite distance away. Almost every statement anyone wants is **global**: *this function is
increasing on the interval*, *these two functions differ by a constant*, *this
approximation is accurate to within so much across that range*.

Nothing so far connects the two. The mean value theorem is the bridge, and it is the only
bridge — every result in this module is a corollary of it, including several that look so
obvious they seem not to need proving.

## Rolle's theorem first

Suppose $f$ is continuous on $[a,b]$, differentiable on $(a,b)$, and $f(a) = f(b)$. Then
$f'(c) = 0$ for some $c$ strictly between $a$ and $b$.

The proof rests on two theorems. The first is the **extreme value theorem**: a function
continuous on a closed bounded interval attains a maximum and a minimum somewhere on it.
That is a companion to Module 2's intermediate value theorem — both are properties
continuity buys on a closed interval — and it is stated rather than proved here; Module
11 takes it up again as the reason a search for global extrema only ever has to check
the critical points and the two endpoints. If both are attained at the endpoints, then
since
$f(a) = f(b)$ the maximum equals the minimum and $f$ is constant, so $f' = 0$ everywhere
inside. Otherwise one of them is attained at an interior point $c$, and Fermat's theorem
says an interior extremum of a differentiable function has $f'(c) = 0$: the difference
quotient is $\le 0$ approaching from one side and $\ge 0$ from the other, so the
two-sided limit must be zero.

Both hypotheses earn their place. Drop differentiability at one interior point and
$|x|$ on $[-1,1]$ is a counterexample: equal endpoint values, no interior zero
derivative, and a corner where the tangent should have been. Drop continuity at an
endpoint and a function that leaps back to its starting value at the last instant is
another.

## Tilting it into the mean value theorem

Rolle's theorem is the flat case. The general case is the same picture with the axes
tilted, and the proof is to subtract the tilt.

Given $f$ continuous on $[a,b]$ and differentiable on $(a,b)$, define

$$h(x) = f(x) - f(a) - \frac{f(b)-f(a)}{b-a}\,(x-a),$$

which is $f$ minus the straight chord through its endpoints. Check the ends:
$h(a) = 0$, and

$$h(b) = f(b) - f(a) - \frac{f(b)-f(a)}{b-a}(b-a) = 0.$$

So $h$ satisfies Rolle's hypotheses, and there is a $c$ in $(a,b)$ with $h'(c) = 0$.
Since $h'(x) = f'(x) - \frac{f(b)-f(a)}{b-a}$, that says

$$f'(c) = \frac{f(b)-f(a)}{b-a}.$$

Some interior slope equals the average slope. The car was doing exactly $90$.

## What it gives back

Three corollaries, each proved in a line or two, each used constantly.

**If $f' = 0$ throughout an interval, $f$ is constant there.** For any two points $u < v$
in the interval, $f(v)-f(u) = f'(c)(v-u) = 0$. Not obvious, and not provable from the
definition of the derivative alone: the derivative is local, "constant" is global.

**If $f' > 0$ throughout an interval, $f$ is increasing there.** Same line, with the sign
kept: $f(v)-f(u) = f'(c)(v-u) > 0$.

**If $f' = g'$ throughout an interval, then $f - g$ is constant.** Apply the first
corollary to $h = f-g$. Constant, not necessarily zero — $x^{2}$ and $x^{2}+7$ have the
same derivative everywhere. This is why an antiderivative carries an arbitrary constant
and why one initial condition determines it.

Every one of those says *interval*, and the restriction is real. Module 3's $1/x$ has a
negative derivative on each side of the origin but is not decreasing across the gap:
$f(-1) = -1$ is less than $f(1) = 1$. The mean value theorem needs $[u,v]$ inside the
domain, and there is no such interval spanning a hole.

## Worked: finding the $c$, and one inequality

For $f(x) = x^{2}$ on $[0,3]$: the average slope is $(9-0)/(3-0) = 3$, and $f'(c) = 2c$,
so $c = 3/2$. That is the midpoint, and it is the midpoint for a parabola on *any*
interval: the average slope on $[a,b]$ is $\frac{b^{2}-a^{2}}{b-a} = a+b$, and
$2c = a+b$ gives $c = \frac{a+b}{2}$.

The midpoint is a parabola's special property, not the theorem's. For $f(x) = x^{3}$ on
$[0,3]$ the average slope is $27/3 = 9$, and $3c^{2} = 9$ gives $c = \sqrt{3} \approx
1.732$, well right of the midpoint $1.5$. For $f(x) = 1/x$ on $[1,2]$ the average slope
is $(\tfrac{1}{2}-1)/1 = -\tfrac{1}{2}$, and $-1/c^{2} = -\tfrac{1}{2}$ gives
$c = \sqrt{2} \approx 1.414$.

The theorem is also how inequalities get proved. Claim: $e^{x} > 1+x$ for every $x > 0$.
Apply the mean value theorem to $e^{x}$ on $[0,x]$: there is a $c$ in $(0,x)$ with

$$e^{x} - 1 = e^{c}\,x.$$

Since $c > 0$ we have $e^{c} > 1$, so $e^{x}-1 > x$. At $x = 0.1$ that predicts
$e^{0.1} > 1.1$, and indeed $e^{0.1} = 1.10517$. The inequality is the statement that the
exponential lies above its own tangent line at the origin, which Module 9 will use to
bound a linearisation error.

## Concavity, and the check people skip

The second derivative describes how the first is changing. Where $f'' > 0$ the slope is
increasing and the curve is concave up; where $f'' < 0$ it is concave down. An
**inflection point** is where that concavity changes.

The mistake is to define an inflection as a zero of $f''$. Vanishing is necessary but not
sufficient — the sign has to actually change. For $f(x) = x^{4}$, $f'' = 12x^{2}$ is zero
at the origin and positive on both sides, so the curve is concave up throughout and the
origin is a minimum, not an inflection. Any method that reports roots of $f''$ without
testing the sign on both sides will report it as one, which is exactly the check the
capstone is required to perform.

## L'Hôpital's rule, and its one-way street

L'Hôpital's rule is the mean value theorem applied to two functions at once — Cauchy's
form, which gives a $c$ with $\big(f(b)-f(a)\big)g'(c) = \big(g(b)-g(a)\big)f'(c)$.
Taking $a$ to the point of interest and applying it to a $0/0$ quotient turns
$\frac{f(x)}{g(x)}$ into $\frac{f'(c)}{g'(c)}$ with $c$ trapped between, and the trapping
is what forces the two limits to agree.

Two failure modes are worth naming, because the rule is applied far more often than its
hypotheses are checked.

**The form must be indeterminate.** Applied to $\cos x/(1+x)$ at $x = 0$, which
substitutes cleanly to $1$, the rule produces $-\sin x/1 \to 0$. It is not that the
answer is hard to get; it is that a confident wrong answer is produced by a method that
was never entitled to run.

**The implication only goes one way.** If the derivative quotient has a limit, the
original has the same one. If the derivative quotient has *no* limit, nothing follows.
Consider

$$\lim_{x\to\infty}\frac{x + \sin x}{x}.$$

This is an $\infty/\infty$ form, and the true value is $1$, since $\sin x$ is bounded
while $x$ is not. But the derivative quotient is $\frac{1+\cos x}{1}$, which oscillates
between $0$ and $2$ forever and has no limit at all. The rule is silent here, and reading
its silence as "therefore the original limit does not exist" is the error. That is why a
failed application is a reason to try something else, never a conclusion.

## Where it stops

The mean value theorem is a theorem about real-valued functions, and it is false for
functions with more than one output. Take $f(t) = (\cos t,\, \sin t)$ on $[0, 2\pi]$: the
start and end points are identical, so the average velocity is the zero vector, yet the
speed is $1$ at every instant and the derivative is never zero. Rolle's conclusion fails
outright.

Nothing is wrong with the proof; the proof used the extreme value theorem to find a
largest value, and a pair of numbers has no largest. The theorem holds for exactly the
functions the argument covers, which is a good reminder that its hypotheses are load
bearing rather than decorative.
""",
                },
            ],
            "derive": [
                {
                    "title": "Rolle, tilted, and the numbers it produces",
                    "minutes": 12,
                    "vars": ["x", "a", "b", "c", "A", "B"],
                    "brief": r"""
The mean value theorem promises a point $c$ in $(a,b)$ where the instantaneous slope
equals the average slope. Steps 2 to 5 find that point for four specific functions,
which is the fastest way to see that it is a real number and not a formality.

Write $A = f(a)$ and $B = f(b)$. Fractions as `\frac{a}{b}`, roots as `\sqrt{x}`, and
each answer an expression with no equals sign.
""",
                    "steps": [
                        {
                            "prompt": "The theorem sets $f'(c)$ equal to the slope of the chord joining the two endpoints. Write that chord slope in terms of $A$, $B$, $a$ and $b$.",
                            "answer": "\\frac{B-A}{b-a}",
                            "placeholder": "rise over run",
                            "hint": "Rise over run, with the endpoint values on top and the endpoint positions underneath.",
                        },
                        {
                            "prompt": "Apply it to $f(x) = x^{2}$ on $[0,3]$. The chord slope is $3$ and $f'(c) = 2c$. Write $c$.",
                            "answer": "\\frac{3}{2}",
                            "hint": "$(9-0)/(3-0) = 3$, so solve $2c = 3$.",
                        },
                        {
                            "prompt": "Same function, general interval $[a,b]$. The chord slope is $\\dfrac{b^{2}-a^{2}}{b-a}$, which factors. Write $c$ in terms of $a$ and $b$.",
                            "answer": "\\frac{a+b}{2}",
                            "placeholder": "something built from a and b",
                            "hint": "$b^{2}-a^{2} = (b-a)(b+a)$, so the chord slope is $a+b$; now solve $2c = a+b$.",
                            "deconstruct": [
                                "The difference of two squares factors: $\\dfrac{b^{2}-a^{2}}{b-a} = a+b$.",
                                "Set that equal to $f'(c) = 2c$.",
                                "$c = \\dfrac{a+b}{2}$ — the midpoint, every time, for a parabola.",
                            ],
                        },
                        {
                            "prompt": "Now $f(x) = x^{3}$ on $[0,3]$, where the answer is no longer the midpoint. The chord slope is $9$ and $f'(c) = 3c^{2}$. Write the $c$ that lies in the interval.",
                            "answer": "\\sqrt{3}",
                            "placeholder": "a root",
                            "hint": "$3c^{2} = 9$ gives $c^{2} = 3$; the theorem promises a $c$ inside $(0,3)$, so take the positive root.",
                            "deconstruct": [
                                "Chord slope: $\\dfrac{27-0}{3-0} = 9$.",
                                "Solve $3c^{2} = 9$, so $c^{2} = 3$ and $c = \\pm\\sqrt{3}$.",
                                "Only $+\\sqrt{3} \\approx 1.732$ lies in $(0,3)$ — and it sits right of the midpoint $1.5$, unlike the parabola's.",
                            ],
                        },
                        {
                            "prompt": "And $f(x) = 1/x$ on $[1,2]$, where $f'(x) = -1/x^{2}$. The chord slope is $-\\tfrac{1}{2}$. Write the $c$ that lies in the interval.",
                            "answer": "\\sqrt{2}",
                            "placeholder": "a root",
                            "hint": "Solve $-1/c^{2} = -\\tfrac{1}{2}$, so $c^{2} = 2$.",
                            "deconstruct": [
                                "Chord slope: $\\dfrac{\\tfrac{1}{2}-1}{2-1} = -\\dfrac{1}{2}$.",
                                "Set $-\\dfrac{1}{c^{2}} = -\\dfrac{1}{2}$, so $c^{2} = 2$.",
                                "$c = \\sqrt{2} \\approx 1.414$, which is inside $(1,2)$ as promised.",
                            ],
                        },
                        {
                            "prompt": "The theorem also proves inequalities. To show $exp(x) > 1+x$ for $x > 0$, set $h(x) = exp(x) - 1 - x$ and study its derivative. Write $h'(x)$.",
                            "answer": "exp(x)-1",
                            "placeholder": "an exponential and a constant",
                            "hint": "Differentiate term by term; the exponential reproduces itself and the derivative of $-x$ is $-1$.",
                            "deconstruct": [
                                "$\\dfrac{d}{dx}\\exp(x) = \\exp(x)$.",
                                "$\\dfrac{d}{dx}(-1-x) = -1$.",
                                "So $h'(x) = \\exp(x)-1$, which is positive for every $x > 0$ — and by the mean value theorem a positive derivative on an interval forces $h$ to increase, so $h(x) > h(0) = 0$.",
                            ],
                        },
                    ],
                    "closing": r"""
The last step is the pattern worth keeping, because it is how most inequalities in
analysis are actually proved: build the difference, differentiate it, show the derivative
has one sign, and let the mean value theorem convert that local fact into a global one.
At $x = 0.1$ the conclusion says $e^{0.1} > 1.1$, and the true value is $1.10517$.

Steps 2 to 5 are there to make one thing concrete. The theorem does not say the point is
the midpoint — that is a parabola's private habit. For $x^{3}$ on $[0,3]$ the point is
$\sqrt{3} \approx 1.732$; for $1/x$ on $[1,2]$ it is $\sqrt{2} \approx 1.414$. What the
theorem promises is existence, and existence is enough for every corollary that matters:
constant derivative implies constant function, positive derivative implies increasing
function, equal derivatives imply a constant difference.

Where the working stops: each of those corollaries says **on an interval**, and the word
is load bearing. The function $1/x$ has $f'(x) = -1/x^{2} < 0$ everywhere it is defined,
yet $f(-1) = -1$ is smaller than $f(1) = 1$, so it is not a decreasing function. Its
domain is two disconnected pieces and there is no interval joining them, so there is no
$c$ to apply the theorem at. A statement about a derivative never crosses a hole in the
domain.
""",
                },
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
            "read": [
                {
                    "title": "The tangent line as a stand-in, and how far it can be trusted",
                    "minutes": 12,
                    "body": r"""
What is $\sqrt{4.02}$, without a calculator? You know $\sqrt{4} = 2$, and $4.02$ is only
a little further along. The square root is a smooth curve, and over a short enough
stretch a smooth curve is indistinguishable from its tangent line. So walk along the
tangent instead: its slope at $x = 4$ is $\frac{1}{2\sqrt{4}} = 0.25$, and $0.02$ of
horizontal travel buys $0.005$ of height. The answer is about $2.005$.

The true value is $2.0049938$. The estimate is high by $6.2\times 10^{-6}$ — six parts in
a million, from arithmetic done in your head. This module is about why that works, and
about how to know in advance how big that error will be.

## The tangent line, and why it is the *best* line

The linearisation of $f$ at $a$ is

$$L(x) = f(a) + f'(a)\,(x-a),$$

the line through $(a, f(a))$ with slope $f'(a)$. Nothing so far says it is a good
approximation, only that it touches at one point and has the right slope there. Both
facts come straight out of the definition of the derivative, and so does the third, which
is the one that matters.

Rearrange the definition. Since $f'(a) = \lim_{x\to a}\frac{f(x)-f(a)}{x-a}$,

$$\frac{f(x) - L(x)}{x-a} = \frac{f(x)-f(a)}{x-a} - f'(a) \longrightarrow 0
\quad\text{as } x \to a.$$

So the error $f(x)-L(x)$ does not merely go to zero — it goes to zero *faster than
$x-a$ does*. That is a much stronger statement, and it is what distinguishes the tangent
from every other line through the same point. Take any other line
$\tilde{L}(x) = f(a) + m(x-a)$ with $m \neq f'(a)$. Its error over $x-a$ tends to
$f'(a) - m$, a non-zero constant, so its error is proportional to $x-a$ rather than
smaller than it. **The tangent line is not one linear approximation among many; it is the
only one whose error is negligible compared with the step.**

The same statement in the language of small changes: writing $dx$ for a change in the
input and $dy = f'(x)\,dx$ for the corresponding change along the tangent, the true
change in $f$ differs from $dy$ by something smaller than $dx$ itself. That is the
**differential**, and it is the same theorem written for engineers rather than for
points.

## How big is the error, exactly

"Smaller than $x-a$" is qualitative. The quantitative version is Taylor's theorem with
remainder, which is Module 8's mean value theorem applied one order up: for some $\xi$
between $a$ and $x$,

$$f(x) - L(x) = \frac{f''(\xi)}{2}(x-a)^{2}.$$

Two things follow immediately. The error is **second order** in the step, so halving the
distance quarters the error — the same order arithmetic Module 3 used to distinguish a
forward difference from a central one. And the constant is controlled by $f''$, so a
function that is bending hard near $a$ is one whose tangent goes wrong quickly.

Back to the square root. Here $f''(x) = -\frac{1}{4}x^{-3/2}$, so
$f''(4) = -\frac{1}{4}\cdot\frac{1}{8} = -\frac{1}{32}$, and with $x-a = 0.02$ the
predicted error is

$$\left|\frac{-1/32}{2}\right|(0.02)^{2} = \frac{0.0004}{64} = 6.25\times 10^{-6}.$$

The measured error was $6.234\times 10^{-6}$. The prediction is not a bound that happened
to be loose; it is the right number to three figures, because $f''$ barely moves between
$4$ and $4.02$. The sign is right too — $f''$ is negative, the curve is concave down, and
the tangent lies above it, which is why the estimate came out high.

## Relative error, and the factor that carries it

Absolute error is rarely what an engineer has. Components come with percentages, so the
useful question is how a *relative* error travels. Divide the differential by the value:

$$\frac{dy}{y} = \frac{f'(x)\,dx}{f(x)}
= \underbrace{\frac{x f'(x)}{f(x)}}_{\text{sensitivity}}\cdot\frac{dx}{x}.$$

The bracketed factor is dimensionless, and it is the number that matters. For a power
$f(x) = x^{k}$ it is exactly $k$:

$$\frac{x\cdot kx^{k-1}}{x^{k}} = k.$$

So a $1\%$ error in $x$ becomes a $k\%$ error in $x^{k}$. Squaring doubles a percentage;
a square root halves it; a reciprocal flips its sign and keeps its size.

**Worked: a power budget.** $P = V^{2}/R$, with $V$ known to $\pm 2\%$ and $R$ to
$\pm 1\%$. Sensitivities: $+2$ for $V$, $-1$ for $R$. So

$$\frac{dP}{P} = 2\frac{dV}{V} - \frac{dR}{R}.$$

Worst case is both errors pushing the same way — $V$ high and $R$ low —
giving $2(2\%) + 1\% = 5\%$. Checking against the exact arithmetic,
$\frac{1.02^{2}}{0.99} - 1 = 5.09\%$, so the linear estimate is right to within a tenth
of a percent, and the $0.09$ it missed is the second-order term.

If instead the two tolerances are independent random errors rather than worst cases, they
combine in quadrature: $\sqrt{(2\times 2)^{2} + 1^{2}} = 4.12\%$. Which of $5\%$ and
$4.12\%$ to quote is an engineering question about what the tolerances mean, not a
mathematical one — but both are computed from the same two sensitivities.

## The approximations worth knowing cold

All of them are the tangent line at $x = 0$, and each is one line of work:

$$(1+x)^{k} \approx 1+kx, \qquad \sin x \approx x, \qquad
e^{x} \approx 1+x, \qquad \ln(1+x) \approx x.$$

The first with $k = -1$ gives $\frac{1}{1+x} \approx 1-x$, the workhorse behind every
quick estimate of a lightly loaded divider. Check it: $1/1.02 = 0.980392$ against the
estimate $0.98$, off by $3.9\times 10^{-4}$, which is the $x^{2}$ term doing its work.

The accuracy varies more than the uniform look of the list suggests. At $x = 0.1$,
$\sin x \approx x$ is off by $1.7\times 10^{-4}$, while $e^{x} \approx 1+x$ is off by
$5.2\times 10^{-3}$ — thirty times worse. The reason is in the second derivative:
$\sin''(0) = 0$, so the sine's quadratic term vanishes and its first error is cubic,
while the exponential's is quadratic. The second-order formula predicts this before any
of it is measured.

## The mistake, and why it is tempting

The tangent line is exact at one point and good near it, and nothing in the formula says
how near. So it gets used at a distance.

Linearise $\sqrt{x}$ at $a = 4$ and evaluate at $x = 9$: the estimate is
$2 + 0.25(5) = 3.25$, against a true value of $3$. That is an $8.3\%$ error, from the
same formula that was accurate to six parts in a million at $x = 4.02$. Nothing changed
except the step, and the error grew by the square of it: $(5/0.02)^{2}$ is a factor of
$62\,500$, which turns six parts per million into most of a tenth.

The habit that prevents it is to state the step alongside the answer. "The tangent at
$4$ gives $3.25$" is a claim nobody would trust; "$\sqrt{9} \approx 3.25$" reads like a
result.

The second mistake is quieter: adding relative errors without their sensitivities. In the
power budget above, $2\%$ and $1\%$ give $5\%$, not $3\%$, and the difference is entirely
the factor of $2$ carried by the square.

## Where it stops

The error formula needs $f''$ to exist and be bounded on the interval between $a$ and
$x$. When it is not, the second-order estimate says nothing, even though the tangent line
still exists.

$\sqrt{x}$ near $a = 0$ is the standing example. The function is defined at $0$ and
continuous there, but $f'(x) = 1/(2\sqrt{x})$ grows without bound as $x \to 0^{+}$, so
there is no tangent line to linearise along and no finite $f''$ to bound the error with.
Any tolerance analysis of a square root near zero is invalid, which matters wherever an
instrument computes an RMS value of something that may be nearly silent.

More generally, the whole apparatus is local. The sensitivity $xf'(x)/f(x)$ is evaluated
at the operating point, and a device moved to a different operating point has different
sensitivities. A budget computed at one bias current is not a budget at another.
""",
                },
            ],
            "derive": [
                {
                    "title": "The tangent line, the error it leaves, and a tolerance budget",
                    "minutes": 12,
                    "vars": ["x", "a", "h", "k", "V", "R", "P"],
                    "brief": r"""
The linearisation of $f$ at $a$ is $L(x) = f(a) + f'(a)(x-a)$, and the error it leaves is
$\frac{f''(\xi)}{2}(x-a)^{2}$ for some $\xi$ between the two points — Taylor's remainder,
which is Module 8's mean value theorem one order up.

Steps 1 to 3 take one function all the way through, prediction and error together. Write
fractions as `\frac{a}{b}`, and give decimals plainly where a decimal is asked for.
""",
                    "steps": [
                        {
                            "prompt": "Linearise $f(x) = \\sqrt{x}$ at $a = 4$, where $f(4) = 2$ and $f'(4) = \\dfrac{1}{2\\sqrt{4}} = \\dfrac{1}{4}$. Write $L(x)$.",
                            "answer": "2+\\frac{x-4}{4}",
                            "placeholder": "a value plus a slope times a displacement",
                            "hint": "$L(x) = f(a) + f'(a)(x-a)$ with $a = 4$.",
                            "deconstruct": [
                                "$f(4) = 2$ is the constant term.",
                                "$f'(4) = \\dfrac{1}{4}$ is the slope.",
                                "The displacement from the base point is $x-4$, so $L(x) = 2 + \\dfrac{x-4}{4}$.",
                            ],
                        },
                        {
                            "prompt": "Evaluate that at $x = 4.02$ to estimate $\\sqrt{4.02}$. Write the number as a decimal.",
                            "answer": "2.005",
                            "hint": "The displacement is $0.02$, and a quarter of $0.02$ is $0.005$.",
                        },
                        {
                            "prompt": "Now predict the error before comparing. With $f''(x) = -\\dfrac{1}{4}x^{-3/2}$ we have $f''(4) = -\\dfrac{1}{32}$, and the remainder is $\\dfrac{|f''(4)|}{2}(0.02)^{2}$. Write that size as an exact fraction.",
                            "answer": "\\frac{1}{160000}",
                            "placeholder": "one over a large whole number",
                            "hint": "$\\dfrac{1/32}{2} = \\dfrac{1}{64}$, and $(0.02)^{2} = \\dfrac{1}{2500}$.",
                            "deconstruct": [
                                "$\\dfrac{|f''(4)|}{2} = \\dfrac{1}{64}$.",
                                "$(0.02)^{2} = 0.0004 = \\dfrac{1}{2500}$.",
                                "Multiplying, $\\dfrac{1}{64}\\cdot\\dfrac{1}{2500} = \\dfrac{1}{160000} = 6.25\\times 10^{-6}$ — and the measured error is $6.23\\times 10^{-6}$.",
                            ],
                        },
                        {
                            "prompt": "The general small-quantity approximation. Linearise $f(x) = (1+x)^{k}$ at $x = 0$, where $f(0) = 1$ and $f'(x) = k(1+x)^{k-1}$. Write $L(x)$.",
                            "answer": "1+kx",
                            "placeholder": "a constant plus a term in x",
                            "hint": "$f'(0) = k$, so the tangent at the origin has slope $k$.",
                            "deconstruct": [
                                "$f(0) = 1^{k} = 1$.",
                                "$f'(0) = k\\cdot 1^{k-1} = k$.",
                                "So $L(x) = 1 + kx$ — the one approximation the other three on the list are special cases of.",
                            ],
                        },
                        {
                            "prompt": "Use that with the exponent that turns it into the divider rule: take $k = -1$ to approximate $\\dfrac{1}{1+x}$ for small $x$. Write the approximation.",
                            "answer": "1-x",
                            "hint": "Put $k = -1$ into the previous answer.",
                        },
                        {
                            "prompt": "A tolerance budget. For $P = V^{2}/R$ the sensitivities are $+2$ for $V$ and $-1$ for $R$, so $\\dfrac{dP}{P} = 2\\dfrac{dV}{V} - \\dfrac{dR}{R}$. Take the worst case, $V$ high by $2\\%$ and $R$ low by $1\\%$. Write the resulting relative change in $P$ as a decimal fraction.",
                            "answer": "0.05",
                            "placeholder": "a decimal, not a percentage sign",
                            "hint": "$2(0.02) - (-0.01)$, and both contributions push the same way.",
                            "deconstruct": [
                                "$dV/V = +0.02$, so the first term is $2(0.02) = 0.04$.",
                                "$dR/R = -0.01$, so the second term is $-(-0.01) = +0.01$.",
                                "The two add rather than cancel: $0.04 + 0.01 = 0.05$, a $5\\%$ swing from tolerances of $2\\%$ and $1\\%$.",
                            ],
                        },
                    ],
                    "closing": r"""
Step 3 is the one to keep. The error was predicted at $6.25\times 10^{-6}$ before the
true value was looked at, and the true error is $6.23\times 10^{-6}$ — so the
second-order term is not a vague bound but the actual size of what the tangent line
misses. That is what makes a linearisation usable in engineering rather than merely
suggestive: you can state in advance how far you are allowed to walk.

Step 6 is worth checking against exact arithmetic, since the whole method is an
approximation. The linear estimate says $5\%$; the exact value is
$\frac{1.02^{2}}{0.99} - 1 = 5.09\%$. The missing $0.09$ is second order in the
tolerances, which is why a linear budget is trustworthy at $1$–$2\%$ and starts to drift
somewhere above $10\%$.

Where the working stops: every error statement above needs $f''$ to exist and stay bounded
between the base point and the point of use. At $a = 0$ the square root has neither a
finite $f'$ nor a finite $f''$ — its tangent is vertical — so no linearisation exists
there at all, and a tolerance analysis of $\sqrt{x}$ near zero is not merely inaccurate
but undefined. The second limit is distance: the same tangent that was right to six parts
in a million at $x = 4.02$ returns $3.25$ for $\sqrt{9}$, an error of $8.3\%$, because the
remainder grows with the *square* of the step and the step grew by a factor of $250$.
""",
                },
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
            "read": [
                {
                    "title": "The tangent line used backwards, and the three ways it fails",
                    "minutes": 13,
                    "body": r'''
You want $\sqrt{2}$ to every digit a double can hold, and all you have is arithmetic.
Start from $x_0 = 1$ — a guess wrong in the first decimal place — and apply the map
$x \mapsto \tfrac{1}{2}(x + 2/x)$ five times.

| $k$ | $x_k$ | $x_k - \sqrt{2}$ |
| --- | --- | --- |
| $0$ | $1.0000000000000000$ | $-4.142136\times 10^{-1}$ |
| $1$ | $1.5000000000000000$ | $+8.578644\times 10^{-2}$ |
| $2$ | $1.4166666666666667$ | $+2.453104\times 10^{-3}$ |
| $3$ | $1.4142156862745099$ | $+2.123901\times 10^{-6}$ |
| $4$ | $1.4142135623746899$ | $+1.594724\times 10^{-12}$ |
| $5$ | $1.4142135623730951$ | $0$ |

Count the correct digits down that last column: one, two, five, eleven, and then all of
them. Each step roughly doubles the tally. Five multiplications and five divisions have
produced a number that is correct in every bit.

Three questions follow, and this module is the three answers. Where does that map come
from? Why do the digits double? And what does the same procedure do on a function that
does not cooperate?

## The step is a tangent line, solved for zero

Module 9 built the linearisation $L(x) = f(a) + f'(a)(x-a)$ and used it to *evaluate* $f$
a short way from $a$. Read it in the other direction. A line is the one shape whose root
can be written down, so if $L$ stands in for $f$ near $a$, the root of $L$ should stand
in for the root of $f$. Set $L(x) = 0$ at $a = x_k$:

$$0 = f(x_k) + f'(x_k)\,(x - x_k),$$

which rearranges to

$$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}.$$

That is the whole method. Put $f(x) = x^2 - 2$ into it and

$$x_{k+1} = x_k - \frac{x_k^2 - 2}{2x_k} = \frac{1}{2}\left(x_k + \frac{2}{x_k}\right),$$

the average of a guess and $2$ divided by that guess. The rule the table used is not a
trick handed down from Babylon; it is the tangent line to a parabola, written out.

Notice what the derivation did not promise. $x_{k+1}$ is the exact root of an approximate
function. Whether that is progress depends entirely on how good the approximation was —
which is the quantity Module 9 spent its length measuring.

## Why the digits double

Take Taylor with remainder at $x_k$ and evaluate it at the true root $r$, where $f$ is
zero. For some $\xi$ between $x_k$ and $r$,

$$0 = f(r) = f(x_k) + f'(x_k)(r - x_k) + \frac{f''(\xi)}{2}(r - x_k)^2.$$

Write $e_k = x_k - r$ for the error, so $r - x_k = -e_k$, and divide through by
$f'(x_k)$:

$$0 = \frac{f(x_k)}{f'(x_k)} - e_k + \frac{f''(\xi)}{2f'(x_k)}\,e_k^2.$$

The next error is $e_{k+1} = x_{k+1} - r = e_k - f(x_k)/f'(x_k)$, and the line above says
exactly what $f(x_k)/f'(x_k)$ is. Substituting it, the $e_k$ terms cancel and

$$e_{k+1} = \frac{f''(\xi)}{2f'(x_k)}\,e_k^2.$$

The error is *squared* each step, times a constant. For $f = x^2 - 2$ that constant tends
to $2/(2\cdot 2\sqrt{2}) = 1/(2\sqrt{2}) = 0.3535534$, and the table can be used to check
it rather than to illustrate it. From $e_2 = 2.453104\times 10^{-3}$ the formula predicts
$e_3 = 0.3535534 \times (2.453104\times 10^{-3})^2 = 2.127586\times 10^{-6}$, against a
measured $2.123901\times 10^{-6}$. From that, it predicts
$e_4 = 1.594864\times 10^{-12}$ against a measured $1.594724\times 10^{-12}$ — four
significant figures, out of an expression containing an unknown $\xi$.

Squaring an error of $10^{-6}$ gives $10^{-12}$, and that is the doubling of digits, with
no separate explanation needed. But look at where $f'(x_k)$ ended up: in the denominator.
Everything that goes wrong below is that denominator misbehaving.

## The three ways it fails

**The derivative vanishes.** For $f(x) = x^2 + 1$ started at $x_0 = 0$, $f'(0) = 0$. The
tangent there is horizontal, a horizontal line has no root, and there is no next point to
compute. The iteration has not converged and has not diverged; it has stopped existing,
which is why the lab gives it an exception of its own rather than a return value.

**The iterates run away.** Newton on $\arctan$ from $x_0 = 2$ steps by
$-(1 + x^2)\arctan x$. Because $\arctan$ flattens, $f'$ shrinks like $1/x^2$ while $f$
stays near $\pi/2$, so the correction is enormous and lands further out than it started:

| $k$ | $0$ | $1$ | $2$ | $3$ | $4$ | $5$ |
| --- | --- | --- | --- | --- | --- | --- |
| $x_k$ | $2.00$ | $-3.54$ | $13.95$ | $-279.34$ | $122017$ | $-2.34\times 10^{10}$ |

The root at $0$ is crossed on the first step and never approached again. This is not a
rounding effect; the same thing happens in exact arithmetic, and the boundary is sharp —
$x_0 = 1.3917$ converges and $x_0 = 1.3918$ does not.

**The iterates cycle.** For $f(x) = x^3 - 2x + 2$ from $x_0 = 0$: $f(0) = 2$ and
$f'(0) = -2$, so $x_1 = 0 - 2/(-2) = 1$. Then $f(1) = 1$ and $f'(1) = 1$, so
$x_2 = 1 - 1 = 0$. The sequence is $0, 1, 0, 1, \dots$ for as long as anyone is willing
to run it. Every value is finite, every step is legal, and the residual never falls.

That third one is the argument for a cap. Two of these failures announce themselves — a
division by zero, a number that overflows — and the third produces perfectly ordinary
output forever. `newton` in **Newton's method with guards** therefore counts its steps
and raises rather than trusting the problem, because the tab it runs in has no Ctrl-C.

## Worked: the step under the difference quotient

When $f'$ is estimated rather than supplied, one more failure joins the list, and it is
the reason the lab's `numeric_derivative` scales its step.

At $x = 121977$, $\arctan x = 1.5707881$, and one unit in the last place of a number that
size is $2.22\times 10^{-16}$. The true change in $\arctan$ across $h = 10^{-6}$ either
side is $2h/(1+x^2) = 1.34\times 10^{-16}$ — smaller than the last place of the values
being subtracted. So the subtraction cannot return the right answer: it returns zero, or
it returns one unit in the last place. Here it returns one, $2.22\times 10^{-16}$, and
the central difference reports $1.11\times 10^{-10}$ where the truth is
$6.72\times 10^{-11}$. Sixty-five per cent high, with nothing raised and nothing printed.

Scale the step with the point instead — `step = h * max(1.0, abs(x))`, which is $0.122$
here — and the same expression returns $6.7211195\times 10^{-11}$ against an exact
$6.7211580\times 10^{-11}$, wrong in the sixth significant figure. The difference matters
downstream: a derivative 65 per cent too large makes every Newton step three-fifths of
the length it should be, which turns quadratic convergence into a crawl.

## The mistake

A loop can measure $|f(x_k)|$ and cannot measure $|x_k - r|$, so the stopping test is
written on the residual. It is then very easy to read a small residual as a small error.

The two agree only when $f'$ at the root is not small, and at a **double** root they part
company entirely. Take $f(x) = (x-1)^2$. The step collapses to
$x_{k+1} = x_k - (x_k-1)^2/(2(x_k-1)) = \tfrac{1}{2}(x_k + 1)$, so the error *halves*
each time rather than squaring — linear convergence, from the same formula that gave
sixteen digits in five steps. From $x_0 = 2$ the errors are
$1, \tfrac12, \tfrac14, \tfrac18, \tfrac{1}{16}, \tfrac{1}{32}$: after five steps $x$ is
still wrong in the second decimal place, while the residual has fallen to
$9.77\times 10^{-4}$ and looks convincing. Carry on to a residual of $10^{-12}$ and the
root is located to about $10^{-6}$ — the square root of the tolerance asked for.

It is tempting because on every well-behaved example the two quantities agree to within a
factor of $f'(r)$, and the well-behaved examples are the ones people test with. The habit
that catches it costs one line: watch $|x_{k+1} - x_k|$ as well. On a simple root that
step collapses as fast as the residual; on a double root it settles into halving, and
three iterations are enough to see it.

## Where it stops

Every claim above assumed four things at once: a simple root, a starting point near it, a
derivative that stays away from zero along the whole path, and a bounded second
derivative. None of the four is checkable from inside the loop, and none implies another.

Convergence is local, and "near" carries no radius you can compute in advance. The set of
starting points that reach a given root can be an interval, as it is for $x^2 - 2$; for
$z^3 - 1$ in the complex plane the three sets interleave at every scale, so two starts a
millionth apart reach different roots. A guard that gives up at $|x| > 10^9$ is therefore
a policy rather than a theorem: it correctly stops the $\arctan$ runaway, and it would
also stop a search that was going to succeed after wandering.

Quadratic convergence is a statement about a limit, too, and says nothing about the first
few steps. The opening table spent two steps merely arriving in the neighbourhood and
three collecting all sixteen digits — which is the usual division of labour, and the
reason a method with a cap of fifty is not being generous.
''',
                },
            ],
            "quiz": {
                "title": "What the iteration does when it is not converging",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The Newton step `x - f(x)/f'(x)` is, geometrically:",
                        "opts": [
                            "the root of the tangent line to `f` drawn at `x`",
                            "the point nearest `x` at which `f` is smallest",
                            "the midpoint of a bracket known to hold the root",
                            "the average of `x` and the estimate before it",
                        ],
                        "a": 0,
                        "why": r"""
Write the tangent at `x` as `L(t) = f(x) + f'(x)*(t - x)` and solve `L(t) = 0`: the
answer is `t = x - f(x)/f'(x)`, which is the step. Nothing in that derivation minimises
anything — a minimum of `f` is where the derivative vanishes, which is a different
question and often a different point. Bisection is the method that halves a bracket, and
it needs a sign change Newton never asks for; the resemblance to averaging comes from
`x^2 - 2` alone, where the step happens to collapse to the mean of `x` and `2/x`.
""",
                    },
                    {
                        "q": "At a simple root, an iterate is wrong by about `1e-4`. The next one is wrong by about:",
                        "opts": [
                            "`5e-5`, because each step halves the distance to the root",
                            "`1e-8`, because each step squares the current error",
                            "`1e-2`, because rounding takes over at that size",
                            "`1e-16`, since a double carries sixteen digits",
                        ],
                        "a": 1,
                        "why": r"""
The error recurrence is `e_next = f''(xi)/(2*f'(x)) * e*e`, so the error is squared and
`1e-4` becomes about `1e-8` — the count of correct digits doubles, which is what
quadratic convergence means. Halving is what bisection does, and what Newton itself does
at a double root, where `f'` vanishes with the error and the squaring is lost. Rounding
does eventually put a floor under the process, but it sits near `1e-16`, and no single
step jumps straight to it from `1e-4`.
""",
                    },
                    {
                        "q": "`newton(lambda x: x*x + 1, 0.0)` is run. What stops it, and why?",
                        "opts": [
                            "`f` has no real root, so the iterates wander until the cap fires",
                            "`f(0)` is 1, which is over the tolerance, so it returns at once",
                            "`f'(0)` is zero, so the flat tangent has no root to step to",
                            "the iterates settle into a two-cycle and never leave it",
                        ],
                        "a": 2,
                        "why": r"""
`f'(x) = 2x` vanishes at exactly the point the run starts from, so the first step has
nothing to compute: a horizontal line crosses zero nowhere. That is why the lab raises
`ZeroDerivative` rather than `Diverged` — the iteration has not gone wrong, it has failed
to exist. It is true that `x*x + 1` has no real root, and from a start away from the
origin the iterates would indeed run until the cap stopped them; from `0` the derivative
check fires first. A residual above the tolerance is a reason to keep going, not to stop,
and the two-cycle belongs to `x**3 - 2*x + 2`.
""",
                    },
                    {
                        "q": "From `x0 = 0`, iterating on `x**3 - 2*x + 2` gives `0, 1, 0, 1, ...`. Why must the loop count its steps?",
                        "opts": [
                            "because the derivative reaches zero once a cycle has set in",
                            "because nothing in the sequence itself ever signals failure",
                            "because rounding error accumulates a little on every step",
                            "because the iterates overflow if the cycle is left running",
                        ],
                        "a": 1,
                        "why": r"""
Every value in that sequence is finite, every derivative is non-zero, and every step is
legal arithmetic; the residual is 2, then 1, then 2, then 1, and it never falls below any
tolerance. There is no state the loop could inspect that distinguishes this from slow
progress, so the only defence is a count. The other two Newton failures do announce
themselves — a zero derivative divides, a runaway overflows — and it is precisely the
quiet one that needs `max_iter`.
""",
                    },
                    {
                        "q": "Why does the lab scale the difference step as `h * max(1, abs(x))` instead of using `h`?",
                        "opts": [
                            "because `x + h` rounds back to `x` at large `x`, so the quotient divides by zero",
                            "because the truncation error grows without bound as `x` grows",
                            "because the two values of `f` come out too close to be told apart",
                            "because a larger step is more accurate, so it should grow with `x`",
                        ],
                        "a": 2,
                        "why": r"""
At `x = 121977`, `atan(x)` is about 1.5707881 and one unit in its last place is `2.2e-16`,
while the true change in `atan` across `h = 1e-6` either side is only `1.3e-16`. The
subtraction therefore cannot resolve it: the computed difference comes out as zero or as
one unit in the last place, and the quotient here reports `1.11e-10` against a true
`6.72e-11`. Note what does *not* happen: `x + 1e-6` is perfectly distinct from `x` at
that size, since one unit in the last place of `x` is only `1.5e-11`. Truncation error
shrinks with `h` rather than growing with `x`, and a larger step buys accuracy only until
its own `h^2` term takes over.
""",
                    },
                    {
                        "q": "`newton` stops when `abs(f(x)) <= tol`. On a double root with `tol = 1e-12`, the root is located to about:",
                        "opts": [
                            "`1e-12`, the tolerance itself",
                            "`1e-24`, the tolerance squared",
                            "`1e-6`, the square root of the tolerance",
                            "`1e-12` still, since the residual test is unaffected by a double root",
                        ],
                        "a": 2,
                        "why": r"""
Near a double root `f` behaves like `C*(x - r)^2`, so a residual of `1e-12` corresponds to
a distance of about `1e-6` — six digits, not twelve. The residual is the only thing a loop
can measure and it is a proxy for the error, with the flatness of `f` at the root setting
the exchange rate; the flatter the root, the worse the deal. The same flatness costs the
convergence rate as well: `x_next = (x + 1)/2` for `(x-1)^2`, which halves the error
rather than squaring it. Watching `abs(x_next - x)` alongside the residual is what makes
this visible within three iterations.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Flat is not the same as best, and a grid does not see everything",
                    "minutes": 13,
                    "body": r'''
A sheet of card measures 30 cm by 16 cm. Cut a square of side $x$ from each corner, fold
the four flaps up, and tape the seams: you have an open box $x$ deep, with a base
$(30-2x)$ by $(16-2x)$. Its volume is

$$V(x) = x\,(30-2x)(16-2x).$$

Cut nothing and there is no box; cut $x = 8$ and the short side has closed up entirely.
Between those two the volume is positive, so somewhere in between it is largest. Try a
few values: $V(2) = 624$, $V(3) = 720$, $V(4) = 704$. The best cut is somewhere near 3,
and guessing more finely is not a method.

## Why a maximum must have a horizontal tangent

Suppose $c$ is an interior point of the interval where $f$ takes its largest value, and
suppose $f'(c)$ exists and is positive. The definition of the derivative says the
quotient $(f(c+h) - f(c))/h$ is close to $f'(c)$ for small $h$, so for small
enough positive $h$ that quotient is positive, and multiplying by $h > 0$ makes
$f(c+h) > f(c)$. That contradicts $c$ being the largest value. If instead $f'(c) < 0$,
take $h$ small and negative and the same line gives $f(c+h) > f(c)$ again. The only
survivor is $f'(c) = 0$.

That is Fermat's theorem, and it is worth being exact about what it does and does not
say. It is a **necessary** condition: every interior extremum is a critical point.
It is not sufficient — $f(x) = x^3$ has $f'(0) = 0$ and no extremum there at all. And it
says nothing about endpoints, where the argument breaks because $h$ cannot be taken in
both directions.

## Worked: the open box

Multiply $V$ out to $4x^3 - 92x^2 + 480x$ and differentiate:

$$V'(x) = 12x^2 - 184x + 480 = 4\,(3x^2 - 46x + 120).$$

The quadratic formula gives $x = \dfrac{46 \pm \sqrt{2116 - 1440}}{6} = \dfrac{46 \pm 26}{6}$,
so $x = 12$ or $x = \tfrac{10}{3}$.

Only one of those is a cut you can make. At $x = 12$ the flaps have long since overlapped
and $V(12) = -576$, a number the algebra is happy to produce and the card is not. The
domain is $[0, 8]$, and the candidate list has to be intersected with it before anything
else happens.

So the interior candidate is $x = \tfrac{10}{3} = 3.3333$ cm, where

$$V\left(\tfrac{10}{3}\right) = \tfrac{10}{3}\cdot\tfrac{70}{3}\cdot\tfrac{28}{3}
= \tfrac{19600}{27} = 725.9259\,\text{cm}^{3},$$

which beats the 720 found by guessing $x = 3$ by about six cubic centimetres.

## Deciding what kind of point it is

A critical point is a place where the tangent is flat, and flat is compatible with a
peak, a trough and a shelf. To tell them apart, look at the term the tangent line left
out. Taylor at $c$, with $f'(c) = 0$, gives

$$f(c+h) = f(c) + \frac{f''(c)}{2}h^2 + \cdots$$

Since $h^2 > 0$ on both sides, the sign of $f''(c)$ decides the sign of the change.
Positive: $f(c+h) > f(c)$ either way, a minimum. Negative: a maximum. For the box,
$V''(x) = 24x - 184$, and $V''(10/3) = 80 - 184 = -104$, comfortably negative — a maximum,
confirmed rather than assumed.

The test is silent when $f''(c) = 0$, and the reason is visible in the same expansion:
the $h^2$ term has vanished and the sign is decided by whatever comes next. All three
outcomes occur. For $x^4$ the next term is $h^4$, positive on both sides, a minimum. For
$-x^4$, a maximum. For $x^3$ the next term is $h^3$, which changes sign with $h$, so the
point is neither. That is why `critical_points` in **Locating and classifying critical
points** falls back to the first derivative test — the sign of $f'$ one grid step either
side — whenever $|f''(c)|$ is below $10^{-5}$. Negative then positive is a minimum,
positive then negative a maximum, and no change at all is a shelf.

## The candidates are a finite list

A continuous function on a closed, bounded interval attains a largest and a smallest
value somewhere. Wherever the largest value sits, it is either interior — and then
Fermat forces a critical point — or it is one of the two endpoints. There is no third
possibility, so the search is over a finite list: the critical points, plus $a$, plus
$b$. Evaluate $f$ at each and compare.

That list is what `optimise` builds, and the box shows why the endpoints have to be in
it: $V(0) = V(8) = 0$, both minima, and neither is a critical point of anything.

## The mistake

Set the derivative to zero, solve, report the answer. It works on almost every problem
anyone is first shown, which is exactly what makes it dangerous.

Take $f(x) = x^3 - 3x$ on $[-3, 3]$. The critical points are $x = \pm 1$, with $f(-1) = 2$
and $f(1) = -2$, and the second derivative test labels them cleanly: $f'' = 6x$, so $-1$
is a maximum and $+1$ is a minimum. Both labels are correct, and both answers are wrong.
The endpoints give $f(-3) = -18$ and $f(3) = 18$, so the largest value on the interval is
$18$ and the smallest is $-18$ — and neither is at a critical point. The interior
"maximum" at $-1$ is not even in the top half of the range.

The word doing the damage is *local*. The second derivative test is a statement about a
neighbourhood, and it stays true: $f(-1) = 2$ really is bigger than everything nearby.
Asking which value is largest on the whole interval is a different question, and the only
thing that answers it is the comparison across the whole candidate list. It is tempting
because in the problems used to teach the technique the domain is usually unbounded, or
the endpoints are hopeless on sight, so the extra comparison never changes the answer and
quietly stops being made.

## What a grid can and cannot see

Roots of $f'$ are found numerically by sampling. `bracket_sign_changes` walks $n+1$
samples and keeps a pair whenever the product of the two slopes is negative: a sign
change means a root somewhere between, by the intermediate value theorem of Module 2, and
bisection then squeezes the bracket down.

A sign change is sufficient evidence of a root. It is not necessary, and both ways of
failing are real. A feature narrower than one grid step is invisible — with $n = 400$ on
$[-2,2]$ the step is $0.01$, and a pair of critical points $0.003$ apart falls between two
samples with no sign change to show for it.

The other failure is stranger, and it is why the lab has a degenerate case. Take
$f(x) = x^4 - 2x^2$ on $[-2, 2]$ with $n = 400$. The samples land exactly on $-1$, $0$
and $1$, which are precisely the three critical points. At $\pm 1$ the numerical
derivative comes back as $\pm 5.55\times 10^{-11}$ rather than zero — rounding in the
difference quotient — which is enough to keep a sign change alive on one side of each.
At $0$ it comes back as exactly $0.0$, and a product with zero in it is never negative,
so neither the pair to its left nor the pair to its right registers a change. A search
that tests only for sign changes reports two critical points where there are three, and
reports them with complete confidence. Emitting a degenerate bracket $(x_k, x_k)$
whenever a sample is exactly zero is what closes that hole.

## Where it stops

Every guarantee here needs the interval closed and bounded and the function continuous on
it, and each hypothesis fails on its own. On the open interval $(0,1)$ the function
$f(x) = x$ has a least upper bound of 1 and never attains it; on $(0,1]$, $1/x$ is
unbounded. In both cases the candidate list is complete and the answer is still not on
it, because there is no answer.

Fermat's theorem needs $f'(c)$ to exist. It does not for $f(x) = |x|$ at $0$, which is a
genuine minimum with no horizontal tangent, so a search that hunts only for zeros of the
derivative walks straight past it — and the numerical derivative makes matters worse by
returning $0$ there, from a symmetric difference of two equal values.

Bisection needs the sign change it is handed to be real. A double root of $f'$, as at
$x = 0$ for $f(x) = x^4$, touches zero without crossing, so nothing brackets it unless a
sample lands on it exactly. And the second derivative test decides between a peak and a
trough; it never decides whether the point is worth having, which stays a question about
the whole candidate list.
''',
                },
            ],
            "quiz": {
                "title": "Candidates, classification and the limits of a grid",
                "minutes": 8,
                "questions": [
                    {
                        "q": "At an interior point `c` of the interval, `f'(c) = 0`. What has that established?",
                        "opts": [
                            "that `c` is either a local minimum or a local maximum",
                            "that `c` is the largest or smallest value on the interval",
                            "that `c` is a candidate, which may turn out to be neither",
                            "that `f` fails to be differentiable somewhere near `c`",
                        ],
                        "a": 2,
                        "why": r"""
Fermat's theorem runs one way only: an interior extremum forces the derivative to vanish,
so every interior extremum appears on the list of critical points. The converse is false,
and `x**3` at `0` is the standing counterexample — flat tangent, no extremum. Being the
largest value on the whole interval is a stronger claim again, and it needs the endpoints
compared as well. A vanishing derivative is evidence that `f` is differentiable at `c`,
not that it fails to be.
""",
                    },
                    {
                        "q": "Where does `f(x) = x**3 - 3*x` take its largest value on `[-3, 3]`?",
                        "opts": [
                            "at `x = -1`, the local maximum the derivative finds",
                            "at `x = 1`, where the second derivative is positive",
                            "at `x = 3`, an endpoint, where the value reaches 18",
                            "nowhere: `x**3 - 3*x` is unbounded above",
                        ],
                        "a": 2,
                        "why": r"""
The critical points are `-1` and `1`, with values `2` and `-2`; the endpoints give `-18`
and `18`. The largest of those four numbers is 18, at the right endpoint, and the interior
"maximum" at `-1` is not close to it. That is the whole reason the extreme value theorem
puts the endpoints on the candidate list: `local` maximum means larger than its
neighbours and nothing more. `x**3 - 3*x` is indeed unbounded on the whole real line, but
a continuous function on a closed bounded interval always attains a largest value on it.
""",
                    },
                    {
                        "q": "At a critical point `c`, the second derivative comes out as zero. What follows?",
                        "opts": [
                            "`c` is a point of inflection rather than a real extremum",
                            "the test decides nothing; the sign of `f'` either side does",
                            "`c` is a minimum, since the curvature is not negative there",
                            "`f` has no extremum anywhere on the interval at all",
                        ],
                        "a": 1,
                        "why": r"""
With `f'(c) = 0`, the expansion reads `f(c+h) = f(c) + f''(c)*h*h/2 + ...`, and when the
`f''` term vanishes the sign of the change is settled by whatever comes after it. All
three outcomes really occur: `x**4` has a minimum at `0`, `-x**4` a maximum, and `x**3`
neither, and every one of them has both derivatives zero there. So the fallback is to
look at the sign of `f'` a step either side — negative then positive is a minimum,
positive then negative a maximum, no change a shelf.
""",
                    },
                    {
                        "q": "A grid sample lands exactly on a root of `f'`, so the sampled slope is `0.0`. A search testing only `g(x_k)*g(x_k+1) < 0` will:",
                        "opts": [
                            "bracket it twice, once from each side of the exact hit",
                            "miss it, since a product with a zero is never negative",
                            "bracket it, since a zero counts as a change of sign",
                            "raise a `ValueError` that the caller then has to handle",
                        ],
                        "a": 1,
                        "why": r"""
The pair to the left multiplies to `something * 0.0`, which is zero and not negative, and
the pair to the right does the same. So the exact hit is passed over by both tests and the
critical point is reported as absent. `x**4 - 2*x**2` on `[-2, 2]` with `n = 400` is the
case the lab checks: the grid lands on `-1`, `0` and `1`, rounding leaves the outer two
just off zero so their brackets survive, and the one at the origin comes back as exactly
`0.0` and vanishes from the answer. Emitting a degenerate bracket `(x_k, x_k)` is what
recovers it.
""",
                    },
                    {
                        "q": "Why must `critical_points` state a limitation about its grid?",
                        "opts": [
                            "because bisection cannot converge on fewer than 400 samples",
                            "because two critical points inside one step leave no sign change",
                            "because the second derivative test needs a finer grid to be reliable",
                            "because no grid of rationals can land on an irrational root",
                        ],
                        "a": 1,
                        "why": r"""
A sign change is sufficient evidence of a root and not necessary evidence of one. With
`n = 400` on `[-2, 2]` the step is `0.01`, and a pair of critical points `0.003` apart
sits between two samples with the slope having the same sign at both — the feature is
narrower than the sampling and leaves no trace. Bisection is not the limitation; it
converges on any bracket it is handed. Nor is exactness: bisection locates an irrational
root to whatever tolerance is asked, provided the bracket reached it in the first place.
""",
                    },
                    {
                        "q": "`f(x) = 1/x` on `(0, 1]` has no largest value. Which hypothesis has failed?",
                        "opts": [
                            "continuity, since `1/x` is discontinuous inside the interval",
                            "differentiability, since `1/x` has no derivative at an endpoint",
                            "closedness: the end where the trouble sits is left out",
                            "none of them; the candidate list was built incorrectly",
                        ],
                        "a": 2,
                        "why": r"""
The extreme value theorem asks for a continuous function on a closed bounded interval, and
`1/x` is continuous and differentiable at every point of `(0, 1]` — there is nothing wrong
with the function on the set where it is defined. What is missing is the left end. The
values climb without bound as `x` approaches `0`, and because `0` is not in the interval
there is no point at which the climb is realised. Adding a candidate would not help: the
supremum is not attained anywhere, so no list of points can contain it.
""",
                    },
                ],
            },
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
