"""MA211 — Numerical Methods & Scientific Computing."""

COURSE = {
    "id": "MA211",
    "title": "Numerical Methods & Scientific Computing",
    "year": 2,
    "level": "Intermediate",
    "prereqs": ["MA112", "MA121", "CS101"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 130,
    "icon": "≈",
    "summary": (
        "The methods every simulation, renderer and training loop is built out of, "
        "written in plain Python with nothing hidden behind a library call. You "
        "measure what a double can hold, watch one subtraction destroy ten digits, "
        "and then build the tools that survive it: root finders that report how they "
        "converged, elimination with partial pivoting, quadrature that refines itself "
        "where the integrand is hard, and Runge-Kutta steppers you push until they go "
        "unstable — finishing with a trajectory engine that uses all five."
    ),
    "outcomes": [
        "Predict and measure the rounding error of a floating-point computation, and rewrite an expression to avoid catastrophic cancellation",
        "Choose between bisection, Newton and the secant method by what each one costs and what each one can promise",
        "Solve a linear system by LU factorisation with partial pivoting, and say why the pivot is a necessity rather than a tidiness",
        "Separate a small residual from a small error, and estimate a condition number to tell them apart",
        "Derive the trapezoid and Simpson rules from the shapes they fit, and predict how their error falls with the step",
        "Implement Euler, Heun and RK4, measure their orders empirically, and locate the step size at which an explicit method goes unstable",
        "Recognise a stiff problem from its time constants and explain why an implicit step is the answer",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone engine (60%).",
    "reading": [
        "Heath, *Scientific Computing: An Introductory Survey*, revised 2nd ed. — chapters 1-2, 5-6, 8-9",
        "Trefethen & Bau, *Numerical Linear Algebra* — lectures 12-17 and 20-23",
        "Higham, *Accuracy and Stability of Numerical Algorithms*, 2nd ed. — chapters 1-4",
        "Goldberg, *What Every Computer Scientist Should Know About Floating-Point Arithmetic* (1991)",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Floating point, error, and conditioning",
            "summary": "What a double can hold, what every operation costs you, and which rearrangement wins the digits back.",
            "concepts": [
                "A double is a sign, an 11-bit exponent and a 52-bit fraction: the reals are sampled, not stored",
                "Machine epsilon is the gap next to 1.0, and the *relative* spacing everywhere else",
                "Every rounded operation satisfies fl(a op b) = (a op b)(1 + delta) with |delta| <= eps/2",
                "Cancellation does not create error — it promotes an existing error to the front of the answer",
                "The quadratic formula loses digits when b*b is much larger than 4ac, and one rearrangement wins them back",
                "Naive summation drifts with the number of terms; compensated summation carries the dropped bits forward",
                "A small residual is not a small error: conditioning is the factor between them",
                "Comparing computed floats needs a relative tolerance and an absolute one",
            ],
            "read": [
                {
                    "title": "The gap next to one",
                    "minutes": 13,
                    "body": r'''
A billing system holds money in dollars and adds ten deductions of ten cents each.
Before it writes the row it checks the total against a dollar.

```python
total = 0.0
for _ in range(10):
    total += 0.1
print(total)
print(total == 1.0)
```

It prints `0.9999999999999999`, and then `False`. No addition in that loop was
performed incorrectly. Every one of them returned the closest available answer.
The nine at the end is not a bug in Python or in the processor, and hunting for the
faulty line is a way to lose an afternoon. What is wrong is the expectation, and
this module is about replacing it with one that predicts what the machine will do.

## What a double can hold

A `float` in Python is an IEEE-754 binary64: 64 bits, split into one sign bit,
eleven bits of exponent, and fifty-two bits of fraction. The value stored is
$\pm(1.f) \cdot 2^{e}$, where $1.f$ is a binary fraction with 52 bits after the
point. Fix the exponent and you have $2^{52}$ evenly spaced values covering the
interval from $2^{e}$ to $2^{e+1}$. Move the exponent up by one and the same
$2^{52}$ values cover twice as much ground, so the spacing doubles.

That is the whole structure, and one measurement pins it down. Halve a trial gap
until adding half of it to 1.0 changes nothing:

```python
gap = 1.0
while 1.0 + gap / 2 != 1.0:
    gap /= 2
print(gap)
print(gap == 2.0 ** -52)
```

It prints `2.220446049250313e-16` and `True`. That number is **machine epsilon**,
written $\epsilon$: the distance from 1.0 to the next double above it. Because the
spacing scales with the exponent, the gap near any $x$ is about $\epsilon|x|$, and
rounding a real number to the nearest double therefore costs at most half a gap:

$$|\mathrm{fl}(x) - x| \leq \frac{\epsilon}{2}|x|$$

Call that half-epsilon the unit roundoff, $u = 1.1102230246251565 \cdot 10^{-16}$.
IEEE-754 requires each of the four arithmetic operations to return the correctly
rounded value of the exact result, so for any two doubles

$$\mathrm{fl}(a \circ b) = (a \circ b)(1 + \delta), \qquad |\delta| \leq u$$

Every claim in this course about accuracy is built from that one line.

It also explains the opening. A tenth is a repeating fraction in binary exactly as
a third is in decimal:

```python
print((0.1).hex())
print(f"{0.1:.20f}")
```

`0x1.999999999999ap-4` — the nine-nine-nine goes on forever and the last digit is
rounded up to `a`. Written out in decimal, the double called `0.1` is
`0.10000000000000000555`. Ten of those, added left to right with a rounding after
each, land next door to 1.0 rather than on it.

The relative spacing has a consequence people meet late and painfully:

```python
print(1e16 + 1.0 == 1e16)
print(1e16 + 2.0 == 1e16)
```

`True`, then `False`. At $10^{16}$ consecutive doubles are 2 apart, so adding 1 asks
for a value that does not exist and the result rounds back to where it started. A
counter kept in a double stops counting near $2^{53}$. Nothing overflowed, nothing
warned, and a loop written to run a quadrillion times will run forever.

## Cancellation moves an error, it does not make one

Here is the operation that ruins numerical code, and the surprise is that it is the
one operation that never rounds at all.

```python
import math

x = 1e-8
print(math.cos(x) == 1.0)
print((1 - math.cos(x)) / x**2)
print(2 * math.sin(x / 2)**2 / x**2)
```

The three lines print `True`, `0.0` and `0.5`. The limit of
$(1 - \cos x)/x^{2}$ as $x \to 0$ is $\tfrac{1}{2}$, so the second answer is not
inaccurate — it has no correct digits at all, while the third is right to every
digit shown.

Trace where the digits went. Mathematically $\cos(10^{-8}) = 1 - 5 \cdot 10^{-17}$.
The gap below 1.0 is $1.11 \cdot 10^{-16}$, so that value is nearer to 1.0 than to
any other double and `cos` returns exactly 1.0. The rounding happened inside `cos`,
before any subtraction: the returned value carries an absolute error of
$5 \cdot 10^{-17}$, which against its own size of 1 is a relative error of
$5 \cdot 10^{-17}$ — beneath notice. Now subtract 1. The subtraction itself is
exact: when two numbers lie within a factor of two of each other their difference
is representable, so nothing is rounded here at all. What the subtraction does is
remove the 1 and leave behind a result whose true size is $5 \cdot 10^{-17}$ with
that same absolute error still attached to it. The error was in the sixteenth digit
of the operand; it is now the whole of the answer.

That is catastrophic cancellation, and the name misleads. The subtraction is
innocent. The damage is done earlier, by whatever rounded the operands, and the
subtraction merely rescales it. The second spelling avoids the trap by never
forming a small number out of large ones: $\sin(x/2)$ is computed with a small
relative error and is squared, not subtracted.

## The quadratic formula, all the way through

Solve $x^{2} - 100000x + 1 = 0$. The roots are $99999.99999$ and, to eleven digits,
$1.0000000001 \cdot 10^{-5}$.

```python
import math

a, b, c = 1.0, -100000.0, 1.0
disc = math.sqrt(b * b - 4 * a * c)
naive = (-b - disc) / (2 * a)

q = -0.5 * (b + math.copysign(disc, b))
stable = c / q

print(naive)
print(stable)
```

The first prints `1.0000003385357559e-05` and the second
`1.0000000001000001e-05`. The naive answer is wrong from its seventh digit; the
rearranged one is right to the last bit but one.

Follow the arithmetic. `b * b - 4 * a * c` is $10^{10} - 4$, held exactly. Its
square root is $99999.999979999999998$, and the nearest double to that is
`99999.99998`, so `disc` arrives with an absolute error under
$7.3 \cdot 10^{-12}$ — half of the $1.46 \cdot 10^{-11}$ spacing at $10^{5}$, and a
relative error of $10^{-16}$, which is the best any function can do. Then
`-b - disc` subtracts two numbers that agree in their first ten digits. The
difference should be $2.0000000002 \cdot 10^{-5}$; the computed one is
$2.0000006771 \cdot 10^{-5}$. The absolute error did not change — it is
$6.77 \cdot 10^{-12}$, the error `disc` was already carrying — but the answer it
sits on is ten million times smaller than the numbers it came from, so the relative
error grew by that same factor, from $10^{-16}$ to $3.4 \cdot 10^{-7}$.

The repair is to compute the root where the two terms have the same sign and add
instead of cancelling. With $b < 0$, $-b + \sqrt{b^{2}-4ac}$ adds two positives, so
that root is safe. The other one comes from the product of the roots,
$x_{1}x_{2} = c/a$, which needs no subtraction whatever. `math.copysign` picks the
safe sign automatically, so one line covers both signs of $b$.

Push the coefficients further and the naive formula stops being merely inaccurate.
For $x^{2} - 10^{8}x + 1$ it returns $7.45 \cdot 10^{-9}$ where the answer is
$10^{-8}$: a quarter of the value gone, from a formula that is algebraically
correct and that every one of us was taught.

## The mistake, and why it is tempting

The mistake is to check the answer by putting it back. Substitute the bad root into
$x^{2} - 100000x + 1$ and the residual comes to $-3.4 \cdot 10^{-7}$, which looks
like nothing at all beside a coefficient of one hundred thousand. The root passes
the test people actually apply and is wrong in its seventh digit.

It is tempting because for most problems it works, and because the underlying
reasoning sounds airtight: every operation is accurate to a relative $10^{-16}$, so
an answer built from a handful of them should be accurate to something like
$10^{-16}$. What the argument omits is that error is carried in absolute terms and
judged in relative ones. An operation that shrinks the result without shrinking the
error attached to it multiplies the relative error by the ratio, and no amount of
care in the individual operations prevents that. The factor by which a problem
magnifies input error into output error is its **condition number**, and it belongs
to the problem, not to the code. Ill-conditioned problems are the ones where a
small residual and a small error part company; the rest of this course keeps
running into them, in linear systems and again in stiff differential equations.

## Where the model stops holding

Three places, all of which the lab pokes at. Epsilon bounds the *relative* error, so
it says nothing about the absolute one: at $10^{16}$ the gap between neighbours is
2, and code that tests `abs(a - b) < 1e-12` on values that size is testing `a == b`
with extra steps. Below about $10^{-308}$ the exponent runs out and the spacing
stops shrinking, so the $(1+\delta)$ model fails: a product of two nonzero numbers
can underflow to zero. And "avoid subtraction" is the wrong lesson to take from the
section above. Subtraction of near-equals is the one operation guaranteed to be
exact. What you avoid is *manufacturing* a small number out of large ones that are
carrying error.

## Adding a great many numbers

```python
values = [0.1] * 1000000

total = 0.0
for v in values:
    total += v
print(total)

running = 0.0
lost = 0.0
for v in values:
    y = v - lost
    t = running + y
    lost = (t - running) - y
    running = t
print(running)
```

The first loop prints `100000.00000133288`; the second prints `100000.0`. Each
addition in the first rounds by at most $u$ times the running total, and there are
$n$ of them, so the error can reach $n u \sum|x_i|$ — here $1.1 \cdot 10^{-5}$. The
observed $1.3 \cdot 10^{-6}$ is inside that because the roundings partly cancel, but
the growth with $n$ is real and it is why a long simulation drifts.

The second loop is compensated summation. After `t = running + y` the two values
`t` and `running` are within a factor of two of each other, so `t - running` is
computed exactly: it is the portion of `y` that survived the addition. Subtract `y`
from it and what remains is precisely the portion that did not, with its sign
flipped. Carry that into the next term and the bits come back. The whole method is
four lines and it turns a million-term sum from six correct digits into all of them.

## What the lab asks

**Floating point survival kit** is this module's lab. You write `machine_epsilon`
by the halving loop above, `relative_error`, a `close` that takes both a relative
and an absolute tolerance and so behaves near zero as well as at $10^{12}$,
`naive_sum` and `kahan_sum` side by side, `stable_quadratic`, and `horner` for
evaluating a polynomial without forming its powers. One check adds a hundred
thousand tenths and demands the answer `10000.0` exactly: the naive loop returns
`10000.000000018848` and cannot pass it, and the compensated one returns the
integer.
''',
                },
            ],
            "quiz": {
                "title": "What the arithmetic actually promises",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Adding `0.1` to a running total ten times leaves `0.9999999999999999`. What went wrong?",
                        "opts": [
                            "Nothing rounded wrongly: `0.1` is not representable, so each addition rounds its exact result",
                            "Floating point carries about 15 decimal digits, and ten additions of `0.1` exhaust the budget",
                            "Addition rounds towards zero on every step, so a sum of positives always ends up short",
                            "The two values are the same double and the printing differs; the comparison is the faulty part",
                        ],
                        "a": 0,
                        "whys": [
                            "The stored `0.1` is `0.10000000000000000555`, and each of the ten additions returns the nearest double to a slightly wrong exact sum. Every step is correctly rounded and the total still misses.",
                            "The digit count is roughly right and the conclusion does not follow from it. Ten additions of exactly-stored values would land exactly on the answer; the trouble starts before the first addition, in the value `0.1` itself.",
                            "IEEE-754 rounds to nearest with ties to even, not towards zero, so the errors go both ways. Truncation would show as a steady one-sided drift, and the last addition here in fact rounds up.",
                            "They are different doubles, `1.0` and the one below it, separated by the full gap of $1.11 \\cdot 10^{-16}$. Printing is honest here; `repr` shows the shortest text that reads back as that exact value.",
                        ],
                        "why": r"""
A tenth is a repeating fraction in binary the way a third is in decimal, so the
double named `0.1` is `0.10000000000000000555`. Each addition then returns the
nearest double to an exact sum that was already off, and the roundings do not
happen to cancel. What is worth taking from this is that "correctly rounded" is a
promise about one operation and never about a sequence of them: the operations were
faultless and the total is still wrong in the last digit.
""",
                    },
                    {
                        "q": "At $x = 10^{-8}$, `(1 - math.cos(x)) / x**2` returns `0.0` where the answer is `0.5`. Which step destroyed the digits?",
                        "opts": [
                            "The subtraction rounded badly, because subtracting nearly equal numbers is the least accurate operation",
                            "`math.cos` rounded to 1.0, and the subtraction then rescaled that error to be the whole answer",
                            "Dividing by $x^{2} = 10^{-16}$ underflowed, since the numerator is below the smallest normal double",
                            "`math.cos` loses accuracy near zero, so its answer was wrong before any subtraction",
                        ],
                        "a": 1,
                        "whys": [
                            "It is the reverse: when two numbers lie within a factor of two of each other, their difference is exactly representable and the subtraction rounds by nothing at all. The subtraction here is the only faultless step in the line.",
                            "The true cosine is $1 - 5 \\cdot 10^{-17}$, which is nearer 1.0 than any other double, so the error is already there when the subtraction starts. Removing the 1 leaves that error as the entire result.",
                            "Nothing underflows. The numerator is exactly zero, and $10^{-16}$ is fifteen orders of magnitude above the smallest normal double, so the division is ordinary and returns `0.0` honestly.",
                            "`math.cos` is correctly rounded to within an ulp, which near zero is a relative error of about $10^{-16}$ — it is one of the most accurate things in the library. Its answer was right to every bit it could hold.",
                        ],
                        "why": r"""
Cancellation moves error rather than making it. `math.cos(1e-8)` is the closest
double to $1 - 5 \cdot 10^{-17}$, which is 1.0 itself, so an absolute error of
$5 \cdot 10^{-17}$ is present before the subtraction runs. Against an operand of
size 1 that is invisible; after the 1 is subtracted away the result should be
$5 \cdot 10^{-17}$ and the error is the same size as the answer. Rewriting as
$2\sin^{2}(x/2)/x^{2}$ never builds a small number out of large ones and returns
`0.5` exactly.
""",
                    },
                    {
                        "q": "Machine epsilon is $2.22 \\cdot 10^{-16}$. Which statement does that licence?",
                        "opts": [
                            "Two doubles differing by less than $10^{-16}$ in absolute value are the same double",
                            "A computed double is within $2.22 \\cdot 10^{-16}$ of the value it was meant to hold",
                            "Rounding one real to the nearest double costs at most $1.11 \\cdot 10^{-16}$ times its size",
                            "Any sum of $n$ doubles carries an absolute error no larger than $n$ times $2.22 \\cdot 10^{-16}$",
                        ],
                        "a": 2,
                        "whys": [
                            "True only near 1.0. At $10^{16}$ the neighbouring doubles are 2 apart, so two values a whole unit apart are indeed the same double; at $10^{-300}$ billions of distinct doubles fit inside $10^{-16}$.",
                            "This is the absolute reading of a relative bound, and it is the usual way the number gets misused. The bound on the error of a rounded value is $u|x|$, which at $x = 10^{6}$ is $10^{-10}$ and at $x = 10^{16}$ is a full unit.",
                            "Epsilon is the spacing at 1.0, spacing scales with the exponent, and rounding to nearest costs at most half a spacing — which is $u|x|$ with $u = \\epsilon/2$.",
                            "The error of a sum scales with the magnitudes being added, not with epsilon alone: adding $n$ terms each near $10^{6}$ can drift by $n u \\cdot 10^{6}$. This bound is also blind to cancellation, which can make the relative error unbounded.",
                        ],
                        "why": r"""
Epsilon is a *relative* quantity: it is the gap next to 1.0, and because the
exponent scales the whole mantissa the gap near any $x$ is about $\epsilon|x|$.
Rounding to nearest therefore costs at most half a gap, $u|x|$ with
$u = \epsilon/2$. Reading it as an absolute bound is the mistake that produces
tolerances like `abs(a - b) < 1e-12` on values of size $10^{16}$, where the gap
between neighbouring doubles is 2 and the test has become an equality check.
""",
                    },
                    {
                        "q": "For $x^{2} - 100000x + 1 = 0$, the small root from `(-b - sqrt(disc)) / (2*a)` is wrong in its seventh digit. Why does `c / q` with $q = -(b + \\sqrt{disc})/2$ fix it?",
                        "opts": [
                            "It computes the large root by addition, then gets the small one from $x_1 x_2 = c/a$ without subtracting",
                            "Dividing by $q$ is a more accurate operation than subtracting, so the rounding error stays smaller",
                            "It evaluates the discriminant to a higher working precision, so the square root arrives carrying fewer bad digits",
                            "It rescales the coefficients before solving, which brings the two roots closer together in size",
                        ],
                        "a": 0,
                        "whys": [
                            "With $b$ negative, $-b + \\sqrt{b^2-4ac}$ adds two positives and cancels nothing, and the product of the roots hands over the other one for the price of a division.",
                            "Division and subtraction are both correctly rounded to within $u$, so neither is inherently more accurate. What differs is the *problem*: this route never forms a small number from two large ones.",
                            "The discriminant is identical in both routes, computed in the same binary64 and carrying the same relative error of about $10^{-16}$. What changes is what happens to it afterwards.",
                            "Nothing is rescaled and the roots stay ten orders of magnitude apart — that separation is the reason the naive formula cancels, and no rearrangement of the algebra can remove it.",
                        ],
                        "why": r"""
Both routes use the same discriminant with the same relative error of about
$10^{-16}$. The naive route then subtracts two numbers agreeing in ten digits,
which leaves the absolute error untouched while shrinking the result by $10^{7}$ —
so the relative error grows by $10^{7}$, to $3.4 \cdot 10^{-7}$. The rearrangement
computes the root whose two terms have the same sign, so nothing cancels, and
recovers the other from $x_1 x_2 = c/a$. `math.copysign` picks the safe sign, which
is why the fix is one line rather than a branch on the sign of $b$.
""",
                    },
                    {
                        "q": "In compensated summation, after `t = total + y` the code stores `lost = (t - total) - y`. What is in `lost`?",
                        "opts": [
                            "The running total's accumulated drift over every term so far, subtracted off at the end",
                            "An estimate of the next term's rounding error, used to pre-correct the addition",
                            "The part of `y` the addition dropped, negated, ready to be added back to the next term",
                            "The difference between the compensated total and the naive one, kept for reporting",
                        ],
                        "a": 2,
                        "whys": [
                            "It holds one step's worth, not the history: `lost` is overwritten every iteration and never accumulates. The correction is applied at the top of the next term rather than saved for the end.",
                            "There is no estimating anywhere in the method, and nothing is predicted about a term that has not been read. Every quantity here is computed exactly from an addition that has already happened.",
                            "`t` and `total` are within a factor of two, so `t - total` is exact and equals the portion of `y` that survived; subtracting `y` leaves the portion that did not, with the sign the next `y - lost` needs.",
                            "The naive total is never computed, so no such difference exists to store. The two loops in the reading are separate demonstrations, not two halves of one algorithm.",
                        ],
                        "why": r"""
`t` and `total` lie within a factor of two of one another, so `t - total` is
computed exactly and equals the part of `y` that actually made it into the total.
Subtracting `y` from that leaves exactly the part that was dropped, carrying the
sign that makes `y = v - lost` on the next iteration add it back. Nothing here is an
estimate: each quantity is exact, which is why a million-term sum comes out to the
last bit rather than merely closer.
""",
                    },
                    {
                        "q": "Two routines return roots of the same polynomial. One leaves a residual of $10^{-7}$, the other $10^{-9}$. Which is nearer the true root?",
                        "opts": [
                            "The one with the smaller residual, since the residual is the error scaled by the polynomial",
                            "Neither can be ranked from the residuals alone without knowing how the problem magnifies error",
                            "The one with the larger residual, because a suspiciously small residual indicates an overfitted root",
                            "The smaller residual wins whenever the polynomial's coefficients are all of comparable size",
                        ],
                        "a": 1,
                        "whys": [
                            "This is the check almost everyone applies, and it measures how well the answer satisfies the equation rather than how near it is. The reading's bad root has a residual of $3.4 \\cdot 10^{-7}$ against coefficients of $10^{5}$ and is wrong in its seventh digit.",
                            "Residual and error are related by the conditioning of the root: a flat polynomial near its root has a tiny residual over a wide interval, and the same residual then covers a much larger error.",
                            "There is no such thing as an overfitted root, and a small residual is genuinely evidence — it is weak evidence rather than none. Reversing the test replaces one unjustified ranking with another.",
                            "Comparable coefficients are not the relevant condition, and the reading's example has them: $1$, $-10^{5}$ and $1$ span five orders and still produce a misleading residual. What matters is the slope of the polynomial at the root.",
                        ],
                        "why": r"""
The residual answers "does this value nearly satisfy the equation" and the error
answers "is this value near the root". They agree only when the problem is well
conditioned. Near a root where the polynomial is flat, a whole interval of candidates
produces a tiny residual, so a small residual buys very little. The condition number
is the factor between the two, and the honest procedure is to report the residual
together with an estimate of that factor — which is what the capstone's fit report
does, and what a bare residual can never do on its own.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Compensated summation and the safe root, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "fpkit.py — five holes; get them right and a million tenths add to exactly 100000.0",
                "brief": r"""
Both routines below are four lines longer than the version everybody writes first,
and every extra line is buying back digits. Nothing runs here. Filled in correctly,
`kahan_sum([0.1] * 1000000)` returns `100000.0` exactly, and
`stable_quadratic(1, -1e5, 1)` returns a small root correct to the last bit but one.
""",
                "listing": r'''
import math


def kahan_sum(values):
    """Left-to-right addition that carries the dropped bits forward."""
    total = 0.0
    lost = 0.0
    for v in values:
        y = v - ___
        t = total + y
        lost = ___ - y
        total = t
    return total


def stable_quadratic(a, b, c):
    """The root that would cancel is never formed by subtraction."""
    disc = math.sqrt(b * b - ___)
    q = -0.5 * (b + math.copysign(disc, ___))
    big = q / a
    small = ___ / q
    return (min(big, small), max(big, small))
''',
                "blanks": [
                    {
                        "prompt": "The correction from the previous term is applied to this one before it is added.",
                        "hole": "?",
                        "opts": ["lost", "0.0", "total", "-lost"],
                        "a": 0,
                        "why": "`lost` holds the part of the previous term the addition dropped, with its sign already flipped by the way it was computed, so subtracting it here puts those bits back into the value about to be added.",
                        "whys": [
                            "This is the whole compensation: the bits dropped last time are restored to the front of this term, so they get a second chance to survive the rounding.",
                            "Zeroing the correction turns the routine back into the naive loop it was written to replace. Every value it returns would match the plain running total, bit for bit.",
                            "Subtracting the running total from each term computes something with no meaning at all — after two terms the total is already large and each subsequent term arrives hugely negative.",
                            "The sign is already handled. `lost` was formed as (t - total) - y, which is the negative of what was dropped, so flipping it here adds the error a second time instead of cancelling it.",
                        ],
                    },
                    {
                        "prompt": "This difference is exact, and it is the part of the term that survived the addition.",
                        "hole": "?",
                        "opts": ["(total - t)", "(t - total)", "(t - y)", "(total + y)"],
                        "a": 1,
                        "why": "`t` and `total` are within a factor of two of each other, so their difference is representable and no rounding occurs; that difference is exactly how much of `y` reached the total, and subtracting `y` leaves what did not.",
                        "whys": [
                            "The magnitude is right and the sign is inverted, so the correction is added on the next iteration instead of removed. The error then grows at roughly twice the naive rate rather than vanishing.",
                            "Both operands are near each other in size, so this subtraction is exact, and what it isolates is the portion of the term the addition managed to keep.",
                            "`t` is the new total and `y` a single term, so this is roughly the old total back again — a large number where the correction should be a few times $10^{-17}$.",
                            "That is the value `t` was supposed to be before rounding, and recomputing it in floating point rounds it identically. The difference from `y` is then the whole total, not the lost bits.",
                        ],
                    },
                    {
                        "prompt": "Complete the discriminant under the square root.",
                        "hole": "?",
                        "opts": ["4 * a * c", "4 * a", "2 * a * c", "4 * c"],
                        "a": 0,
                        "why": "The discriminant of a quadratic is b squared minus four a c, and each of the three coefficients has to appear or the formula stops solving the equation it was derived from.",
                        "whys": [
                            "The standard discriminant, and note that it is the only place c enters before the last line — which is why the small root can be recovered from it later.",
                            "Dropping c makes the roots depend on only two of the three coefficients, so every equation with the same a and b would come out with the same answer.",
                            "The 2 belongs in the denominator of the formula, not under the root. Using it here returns roots that satisfy no quadratic in particular.",
                            "Losing a breaks every equation whose leading coefficient is not 1, and the tests use one with a equal to 2 for exactly that reason.",
                        ],
                    },
                    {
                        "prompt": "copysign takes the sign from this, so that the two terms of q add rather than cancel.",
                        "hole": "?",
                        "opts": ["a", "b", "disc", "-b"],
                        "a": 1,
                        "why": "Giving the square root the same sign as b makes b + copysign(disc, b) a sum of two like-signed quantities, which is the one arrangement in which nothing cancels whatever the sign of b happens to be.",
                        "whys": [
                            "The leading coefficient has nothing to do with which of the two terms would cancel; with a positive and b negative this reproduces the naive formula and loses the same digits.",
                            "Matching the root's sign to b is what guarantees the addition never cancels, and it removes the need to branch on whether b is positive or negative.",
                            "disc is a square root and already non-negative, so copying its own sign onto it changes nothing at all and leaves the cancelling arrangement exactly as it was.",
                            "This flips the sign to the one that guarantees cancellation rather than prevents it, so the routine loses digits precisely on the inputs it was written to survive.",
                        ],
                    },
                    {
                        "prompt": "The second root comes from the product of the roots, without any subtraction.",
                        "hole": "?",
                        "opts": ["c", "a", "-c", "b"],
                        "a": 0,
                        "why": "The two roots multiply to c over a, so once the safe root q/a is known the other is c/q — a division, which is correctly rounded and cannot amplify anything.",
                        "whys": [
                            "Expanding a(x - r1)(x - r2) shows the constant term is a r1 r2, so r1 r2 = c/a; with big = q/a in hand, the other root is c/q and no subtraction is involved.",
                            "The sum of the roots is -b/a and the product is c/a; using a here returns 1/(r1) scaled wrongly and fails on every equation whose a and c differ.",
                            "The sign belongs to the coefficients as written; negating c returns roots of the wrong sign for every equation with a positive constant term, including the tests.",
                            "b determines the sum of the roots, not their product, so this returns a number related to the wrong symmetric function and matches the true root only by coincidence.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Floating point survival kit",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Seven routines in `main.py`. Together they are the toolbox the rest of the course
uses to decide whether an answer is any good.

## Measuring the arithmetic

- `machine_epsilon()` — the gap from 1.0 to the next double up, found by halving a
  trial gap while `1.0 + gap / 2 != 1.0`. No constants: measure it.
- `relative_error(approx, exact)` — `abs(approx - exact) / abs(exact)`, falling back
  to `abs(approx)` when `exact` is 0.0, because a relative error against zero has no
  meaning.
- `close(a, b, rel_tol=1e-9, abs_tol=0.0)` — `True` when
  `abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)`. Equal values are
  always close (which covers the infinities); a NaN is close to nothing, itself
  included.

## Summing

- `naive_sum(values)` — the honest left-to-right loop, written out. Do not reach for
  the builtin: recent CPython compensates inside `sum` and this routine is the
  control the next one is measured against.
- `kahan_sum(values)` — compensated summation. `kahan_sum([0.1] * 100000)` must
  return exactly `10000.0`, where the naive loop returns `10000.000000018848`.

## Polynomials

- `horner(coeffs, x)` — evaluate $c_0 + c_1x + c_2x^2 + \dots$ with coefficients in
  *increasing* order of power, walking from the top down so no power of `x` is ever
  formed. An empty coefficient list raises `ValueError`.
- `stable_quadratic(a, b, c)` — the two real roots as a tuple, smaller first.
  `ValueError` when `a` is 0.0 or the discriminant is negative. The small root must
  not come from a subtraction of near-equal numbers: for `(1, -1e8, 1)` the naive
  formula returns `7.45e-09` where the answer is `1e-08`, and the check demands a
  relative error under `1e-12`.

```text
machine_epsilon()                  ->  2.220446049250313e-16
close(1.0, 1.0 + 1e-12)            ->  True
close(0.0, 1e-12)                  ->  False        (relative, against zero)
close(0.0, 1e-12, abs_tol=1e-9)    ->  True
horner([1, -100000, 1], 3.0)       ->  -299990.0
stable_quadratic(1, -1e5, 1)       ->  (1.0000000001000001e-05, 99999.99999)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def machine_epsilon():
    """The gap from 1.0 to the next representable double, measured by halving."""
    # your code here


def relative_error(approx, exact):
    """|approx - exact| / |exact|, or |approx| when exact is zero."""
    # your code here


def close(a, b, rel_tol=1e-9, abs_tol=0.0):
    """True when a and b agree to within a relative or an absolute tolerance."""
    # your code here


def naive_sum(values):
    """Left to right, one rounding per addition. The control, not the goal."""
    # your code here


def kahan_sum(values):
    """Compensated summation: carry the bits each addition drops."""
    # your code here


def horner(coeffs, x):
    """Evaluate a polynomial given coefficients in increasing order of power."""
    # your code here


def stable_quadratic(a, b, c):
    """Both real roots, smaller first, without cancelling."""
    # your code here


print("epsilon:", machine_epsilon())
print("100000 tenths, naive:", naive_sum([0.1] * 100000))
print("100000 tenths, kahan:", kahan_sum([0.1] * 100000))
print("roots:", stable_quadratic(1.0, -1e5, 1.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def machine_epsilon():
    """The gap from 1.0 to the next representable double, measured by halving."""
    gap = 1.0
    while 1.0 + gap / 2 != 1.0:
        gap /= 2
    return gap


def relative_error(approx, exact):
    """|approx - exact| / |exact|, or |approx| when exact is zero."""
    if exact == 0.0:
        return abs(approx)
    return abs(approx - exact) / abs(exact)


def close(a, b, rel_tol=1e-9, abs_tol=0.0):
    """True when a and b agree to within a relative or an absolute tolerance."""
    if math.isnan(a) or math.isnan(b):
        return False
    if a == b:
        return True
    if math.isinf(a) or math.isinf(b):
        return False
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def naive_sum(values):
    """Left to right, one rounding per addition. The control, not the goal."""
    total = 0.0
    for v in values:
        total += v
    return total


def kahan_sum(values):
    """Compensated summation: carry the bits each addition drops."""
    total = 0.0
    lost = 0.0
    for v in values:
        y = v - lost
        t = total + y
        lost = (t - total) - y
        total = t
    return total


def horner(coeffs, x):
    """Evaluate a polynomial given coefficients in increasing order of power."""
    if not coeffs:
        raise ValueError("a polynomial needs at least one coefficient")
    acc = 0.0
    for c in reversed(coeffs):
        acc = acc * x + c
    return acc


def stable_quadratic(a, b, c):
    """Both real roots, smaller first, without cancelling."""
    if a == 0.0:
        raise ValueError("not a quadratic: a is zero")
    d = b * b - 4.0 * a * c
    if d < 0.0:
        raise ValueError("the roots are not real")
    disc = math.sqrt(d)
    q = -0.5 * (b + math.copysign(disc, b))
    if q == 0.0:
        return (0.0, 0.0)
    big = q / a
    small = c / q
    return (min(big, small), max(big, small))


print("epsilon:", machine_epsilon())
print("100000 tenths, naive:", naive_sum([0.1] * 100000))
print("100000 tenths, kahan:", kahan_sum([0.1] * 100000))
print("roots:", stable_quadratic(1.0, -1e5, 1.0))
'''}],
                "hints": [
                    "`machine_epsilon` is the loop from the reading: start `gap` at 1.0 and halve it while `1.0 + gap / 2 != 1.0`, then return `gap`. Do not write the constant down — measuring it is the point.",
                    "`close` needs three early exits before the tolerance test: a NaN on either side is never close, equal values always are (which is what makes two infinities compare equal), and a lone infinity never is.",
                    "In `kahan_sum` the order of the four lines matters. Compute `y = v - lost` first, then `t = total + y`, then recover the dropped part as `(t - total) - y`, and only then move `total` on to `t`.",
                    "`stable_quadratic` builds `q = -0.5 * (b + math.copysign(disc, b))`. That is the root that adds rather than cancels; the other one is `c / q`, from the fact that the roots multiply to `c / a`.",
                ],
                "tests": [
                    {"name": "Machine epsilon is measured, not quoted", "code": r'''
_eps = machine_epsilon()
assert _eps == 2.0 ** -52, f"machine_epsilon() gave {_eps!r}, expected 2**-52"
assert 1.0 + _eps != 1.0, "1.0 + eps must be a different double"
assert 1.0 + _eps / 2 == 1.0, "1.0 + eps/2 must round back to 1.0"
'''},
                    {"name": "Relative error, including against zero", "code": r'''
assert abs(relative_error(1.01, 1.0) - 0.01) < 1e-12, \
    f"relative_error(1.01, 1.0) gave {relative_error(1.01, 1.0)!r}, expected 0.01"
assert abs(relative_error(99.0, 100.0) - 0.01) < 1e-12, \
    f"relative_error(99.0, 100.0) gave {relative_error(99.0, 100.0)!r}"
assert relative_error(5.0, 5.0) == 0.0, "An exact answer has zero relative error"
assert relative_error(1e-9, 0.0) == 1e-9, \
    f"With exact 0.0 the fallback is the absolute value; got {relative_error(1e-9, 0.0)!r}"
assert relative_error(-2.0, 1.0) == 3.0, \
    f"relative_error(-2.0, 1.0) gave {relative_error(-2.0, 1.0)!r}, expected 3.0"
'''},
                    {"name": "close mixes a relative and an absolute tolerance", "code": r'''
assert close(1.0, 1.0 + 1e-12), "1.0 and 1.0 + 1e-12 agree to 1e-9 relative"
assert not close(1.0, 1.0 + 1e-12, rel_tol=1e-15), "A tighter tolerance must reject them"
assert not close(0.0, 1e-12), "A purely relative test can never accept anything against 0.0"
assert close(0.0, 1e-12, abs_tol=1e-9), "The absolute tolerance is what rescues values near zero"
assert close(1e12, 1e12 + 1.0), "1.0 apart at 1e12 is 1e-12 relative, well inside 1e-9"
assert not close(float("nan"), float("nan")), "A NaN is close to nothing, itself included"
assert close(float("inf"), float("inf")), "Equal values are close, which covers the infinities"
assert not close(float("inf"), 1e308), "An infinity is not close to any finite value"
'''},
                    {"name": "naive_sum is the honest control", "code": r'''
assert naive_sum([]) == 0.0, "The empty sum is 0.0"
assert naive_sum([1.0, 2.0, 3.0]) == 6.0, f"naive_sum([1,2,3]) gave {naive_sum([1.0, 2.0, 3.0])!r}"
_got = naive_sum([0.1] * 100000)
assert _got == 10000.000000018848, \
    f"A left-to-right loop over 100000 tenths gives 10000.000000018848; got {_got!r}. " \
    "Write the loop out rather than calling the builtin, which compensates."
'''},
                    {"name": "kahan_sum wins the digits back", "code": r'''
assert kahan_sum([]) == 0.0, "The empty sum is 0.0"
assert kahan_sum([1.0, 2.0, 3.0]) == 6.0, f"kahan_sum([1,2,3]) gave {kahan_sum([1.0, 2.0, 3.0])!r}"
_got = kahan_sum([0.1] * 100000)
assert _got == 10000.0, f"kahan_sum of 100000 tenths gave {_got!r}, expected exactly 10000.0"
_mixed = [1.0] + [1e-10] * 100000
assert kahan_sum(_mixed) == 1.00001, \
    f"kahan_sum of 1.0 plus 100000 copies of 1e-10 gave {kahan_sum(_mixed)!r}, expected 1.00001"
assert naive_sum(_mixed) != kahan_sum(_mixed), \
    "The two routines must differ on this input, or one of them is not doing its job"
'''},
                    {"name": "Horner evaluates without forming powers", "code": r'''
assert horner([7.0], 3.0) == 7.0, "A single coefficient is a constant polynomial"
assert horner([1.0, -100000.0, 1.0], 3.0) == -299990.0, \
    f"horner([1, -100000, 1], 3.0) gave {horner([1.0, -100000.0, 1.0], 3.0)!r}, expected -299990.0"
assert horner([2.0, -3.0, 0.0, 1.0], 2.0) == 4.0, \
    f"horner([2, -3, 0, 1], 2.0) gave {horner([2.0, -3.0, 0.0, 1.0], 2.0)!r}, expected 4.0"
assert horner([1.0, 1.0, 1.0], 0.0) == 1.0, "At x = 0 only the constant term survives"
for _x in (0.5, -1.5, 12.0):
    _direct = sum(c * _x ** i for i, c in enumerate([3.0, -1.0, 2.0, 0.5]))
    assert abs(horner([3.0, -1.0, 2.0, 0.5], _x) - _direct) < 1e-9, \
        f"horner disagrees with the direct sum at x = {_x}"
try:
    horner([], 1.0)
    assert False, "horner([], x) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The quadratic that breaks the textbook formula", "code": r'''
_lo, _hi = stable_quadratic(1.0, -1e5, 1.0)
assert abs(_hi - 99999.99999) < 1e-6, f"The large root came out as {_hi!r}"
assert abs(_lo - 1.0000000001e-05) / 1.0000000001e-05 < 1e-12, \
    f"The small root came out as {_lo!r}, expected about 1.0000000001e-05 — " \
    "the naive formula gives 1.0000003385357559e-05"
_lo8, _hi8 = stable_quadratic(1.0, -1e8, 1.0)
assert abs(_lo8 - 1e-08) / 1e-08 < 1e-12, \
    f"For x^2 - 1e8 x + 1 the small root is 1e-08; got {_lo8!r} " \
    "(the naive formula returns 7.450580596923828e-09)"
assert abs(_hi8 - 1e8) / 1e8 < 1e-12, f"The large root came out as {_hi8!r}"
'''},
                    {"name": "Ordinary roots, and inputs that are refused", "code": r'''
assert stable_quadratic(1.0, -3.0, 2.0) == (1.0, 2.0), \
    f"x^2 - 3x + 2 has roots 1 and 2; got {stable_quadratic(1.0, -3.0, 2.0)!r}"
_r = stable_quadratic(2.0, 5.0, -3.0)
assert abs(_r[0] + 3.0) < 1e-12 and abs(_r[1] - 0.5) < 1e-12, \
    f"2x^2 + 5x - 3 has roots -3 and 0.5; got {_r!r}"
_p = stable_quadratic(1.0, 1e5, 1.0)
assert abs(_p[1] - -1.0000000001e-05) / 1.0000000001e-05 < 1e-12, \
    f"With b positive the small root is negative and near -1e-5; got {_p!r}"
for _args in [(0.0, 2.0, 1.0), (1.0, 1.0, 1.0), (1.0, 0.0, 4.0)]:
    try:
        stable_quadratic(*_args)
        assert False, f"stable_quadratic{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Root finding: bracketing, tangents and secants",
            "summary": "Three ways to solve f(x) = 0, what each one guarantees, and what each one charges for it.",
            "concepts": [
                "A sign change on a continuous function traps a root; halving the bracket wins one bit per step",
                "Bisection's step count is predictable in advance: log2 of the interval over twice the tolerance",
                "Newton replaces f by its tangent line and solves that, so the error squares each step near a simple root",
                "The squaring constant is |f''| / (2|f'|) at the root, and it can be measured from the trace",
                "The secant method drops the derivative for a difference quotient and converges at order 1.618",
                "Stopping on |f(x)| tests the equation; stopping on the step tests the answer",
                "At a multiple root Newton falls back to halving the error, and the derivative guard can fire first",
                "Newton can cycle, and a bracketing scan is blind to a root of even multiplicity",
            ],
            "read": [
                {
                    "title": "Halving, tangents, and the price of each",
                    "minutes": 13,
                    "body": r'''
Before any method is chosen, look at what five evaluations already tell you.

```python
def f(x):
    return x**3 - 2*x - 5

for x in (1.0, 1.5, 2.0, 2.5, 3.0):
    print(x, f(x))
```

The values run `-6.0`, `-4.625`, `-1.0`, `5.625`, `16.0`. Between 2.0 and 2.5 the
sign flips, and a continuous function cannot get from $-1$ to $5.625$ without
passing through zero on the way. Nothing has been solved, no formula has been
applied, and the answer is already trapped in an interval of width 0.5. That
trapping is the only unconditional guarantee any root finder in this module offers,
and the first method is built out of nothing else.

## One bit per step

Take the midpoint, evaluate there, and keep whichever half still shows a sign
change.

```python
def f(x):
    return x**3 - 2*x - 5

a, b = 2.0, 3.0
for step in range(1, 6):
    m = (a + b) / 2
    print(step, a, b, m, f(m))
    if f(a) * f(m) < 0:
        b = m
    else:
        a = m
```

The bracket goes $[2, 3]$, $[2, 2.5]$, $[2, 2.25]$, $[2, 2.125]$, $[2.0625, 2.125]$.
Each line costs one evaluation of $f$ and halves the width, so after $k$ steps the
bracket is $(b-a)/2^{k}$ wide. Report the midpoint and the answer is off by at most
half of that, which gives an error bound before the code has been run:

$$\frac{b-a}{2^{k+1}} \leq \text{tol} \quad\text{when}\quad
k \geq \log_2\frac{b-a}{2\,\text{tol}}$$

For $[2,3]$ and a tolerance of $10^{-12}$ that is $\log_2(5 \cdot 10^{11}) = 38.86$,
so 39 steps, and the count is not an estimate — it is arithmetic done in advance.

```python
import math

def f(x):
    return x**3 - 2*x - 5

a, b, tol = 2.0, 3.0, 1e-12
fa = f(a)
steps = 0
while (b - a) / 2 > tol:
    m = (a + b) / 2
    fm = f(m)
    steps += 1
    if fa * fm < 0:
        b = m
    else:
        a, fa = m, fm
print(steps, (a + b) / 2)
print(math.ceil(math.log2((3.0 - 2.0) / (2 * tol))))
```

`39 2.094551481542112`, then `39`. Bisection converges *linearly*: the error is
multiplied by $\tfrac{1}{2}$ every step, so the digits arrive at a fixed rate of
about one every three and a third steps and no starting point can hurry them.

## Replacing the curve with its tangent

Sampling ignores everything except the sign. The function also has a slope, and near
a root the tangent line is a good stand-in for the curve. Write the first two terms
of the Taylor expansion at the current guess and set them to zero:

$$f(x_n) + f'(x_n)(x - x_n) = 0 \qquad\text{gives}\qquad
x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$

That is Newton's method, and on this equation — his own, from 1669 — it does the
following:

```python
def f(x):
    return x**3 - 2*x - 5

def df(x):
    return 3*x*x - 2

root = 2.0945514815423265
x = 2.0
for n in range(5):
    print(n, x, abs(x - root))
    x = x - f(x) / df(x)
```

The errors are $9.46 \cdot 10^{-2}$, $5.45 \cdot 10^{-3}$, $1.66 \cdot 10^{-5}$,
$1.56 \cdot 10^{-10}$, and then zero to the last bit. Correct digits go 1, 2, 5, 10,
16: each step roughly doubles them. Expanding $f$ about the root explains the
doubling exactly. With $e_n = x_n - r$, the Taylor series gives

$$e_{n+1} \approx \frac{f''(r)}{2f'(r)}\,e_n^{2}$$

so the error is squared and then scaled by a constant belonging to the function. The
trace lets that constant be read off and checked:

```python
root = 2.0945514815423265
errs = [9.455148e-02, 5.448518e-03, 1.663956e-05, 1.558726e-10]
for n in range(3):
    print(errs[n + 1] / errs[n]**2)
print(abs(6 * root) / (2 * abs(3 * root * root - 2)))
```

The measured ratios are `0.6094...`, `0.5605...`, `0.5629...` and the predicted
constant is `0.5630...`. The last two agree to three digits, which is what
"quadratic convergence" means in practice: not a promise of speed in the abstract
but a specific number you can measure from your own iterates.

## Dropping the derivative

Newton needs $f'$, and for a function that is itself the output of a simulation
there may be no derivative to hand. Replace the tangent's slope with the slope
through the last two points:

$$x_{n+1} = x_n - f(x_n)\,\frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}$$

Started from 2.0 and 3.0, that reaches the root in 7 steps against Newton's 5 and
bisection's 39. Its convergence order is the golden ratio, $\varphi \approx 1.618$:
slower than squaring, far faster than halving. The comparison that matters is per
*evaluation* rather than per step. Newton spends two calls a step, one on $f$ and
one on $f'$, so it earns $\sqrt{2} \approx 1.414$ per call, while the secant method
reuses the previous value and spends one, earning 1.618. When $f$ is expensive — and
in this course $f$ is often an entire ODE solve — the secant method is the better
buy, and it is what the capstone's launch-angle search uses.

## The mistake: stopping when the residual is small

The tempting stopping test is `abs(f(x)) < tol`. It is the quantity already in hand,
it costs nothing extra, and it reads like a statement that the equation has been
solved. It fails in both directions, and the failures are worth seeing as numbers.

```python
def flat(x):
    return (x - 1)**3

print(flat(1.0001))
print(1e8 * ((1.0 + 2.0**-52) - 1.0))
```

The first prints `9.999999999996696e-13`. So for a flat root the test
`abs(f(x)) < 1e-12` accepts $x = 1.0001$, an answer wrong in the fourth decimal
place. The second prints `2.220446049250313e-08`: for the steep function
$10^{8}(x-1)$, the closest double to the root that is not the root itself already
has a residual of $2 \cdot 10^{-8}$, so no representable number satisfies
`abs(f(x)) < 1e-12` and a loop with that test runs until `max_iter` and reports
failure on a problem it solved perfectly at the first step.

The residual measures the equation; the step $|x_{n+1} - x_n|$ measures the answer.
Even the step is an estimate, and it is honest only when convergence is fast. If the
error shrinks by a factor $r$ each time, then $x_{n+1} - x_n = e_n - e_{n+1} =
e_n(1 - r)$, so $e_n = \text{step}/(1-r)$. For Newton near a simple root $r$ is on its
way to zero and the step is essentially the error. For an iteration crawling along at
$r = 0.9$ the true error is ten times the last step, and a step-based tolerance
overstates its accuracy by that factor.

## Where these methods stop holding

Newton's guarantee is local and it is about *simple* roots. At a double root the
squaring is gone: for $f(x) = (x-1)^{2}$ the iteration reduces to
$x_{n+1} = x_n - (x_n - 1)/2$, which halves the error exactly as bisection does. From
$x_0 = 2$ it needs 34 steps to reach $10^{-10}$, where the simple root took 5, and
$f'$ is heading for zero the whole way, so a guard against a vanishing derivative can
fire before the answer arrives. Worse, Newton can fail to converge at all: on
$x^{3} - 2x + 2$ from $x_0 = 0$ the tangent sends it to 1, and the tangent at 1 sends
it back to 0, forever. Nothing has gone wrong in the code; the tangent line really
does point there.

Bracketing has its own blind spot, and it is not the one people expect. A root of
even multiplicity has no sign change around it, so no amount of sampling will trap
it. Sample $x^{2}-1$ at $-2, -1, 0, 1, 2$ and there is no sign change anywhere on the
grid at all, because both roots sit exactly on sample points and contribute a zero to
each product rather than a negative. The scan reports nothing found on a function
with two perfectly ordinary roots.

## What the lab asks

**Three root finders and what they cost** has you write `bisect` returning the root
*and* its iteration count, `bisection_steps` predicting that count from the interval
and the tolerance, `newton` with a guard on a vanishing derivative and a limit on the
iterations, `secant`, and `bracket_scan` for locating sign changes on a grid. The
checks compare the predicted step count against the measured one on $[2,3]$, watch
Newton take five steps on the simple root and more than twenty-five on the double
one, and require `bracket_scan` to return an empty list for $x^{2}-1$ on the grid its
roots sit on.
''',
                },
            ],
            "quiz": {
                "title": "What each method promises and what it charges",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Bisection on $[2, 3]$ to a tolerance of $10^{-12}$ takes 39 steps. What would starting from $[2, 2.1]$ instead change?",
                        "opts": [
                            "Nothing: the count depends on the function's slope near the root, not on the bracket",
                            "About 3 steps fewer: the count falls with the logarithm of the width, and the width fell by 10",
                            "Roughly ten times fewer steps, since each step removes a fixed proportion of the bracket's width",
                            "It would converge in a handful of steps, because the starting bracket is already inside the tolerance",
                        ],
                        "a": 1,
                        "whys": [
                            "Bisection never looks at a slope — it looks at a sign. The count depends on the starting width and the tolerance and on nothing else about the function, which is exactly what makes it predictable in advance.",
                            "The count is $\\log_2$ of the width over twice the tolerance, so dividing the width by 10 subtracts $\\log_2 10 = 3.32$, giving 36 steps rather than 39.",
                            "Each step does remove a fixed proportion, which is why the count is logarithmic rather than linear: ten times narrower is $\\log_2 10$ steps saved, about 3, not a tenth of 39.",
                            "The bracket is 0.1 wide and the tolerance is $10^{-12}$, so there are eleven orders of magnitude still to cross. Narrowing the start helps, but by a logarithm rather than by a factor.",
                        ],
                        "why": r"""
The whole cost model is $k \geq \log_2\frac{b-a}{2\,\text{tol}}$, and the only
inputs are the starting width and the tolerance. Ten times narrower buys
$\log_2 10 = 3.32$ steps, so 39 becomes 36. This is the trade bisection offers:
the count is knowable before the run and completely insensitive to what the function
does, which is the same insensitivity that stops a good starting guess from helping
very much.
""",
                    },
                    {
                        "q": "Newton's errors on $x^3 - 2x - 5$ run $9.5 \\cdot 10^{-2}$, $5.4 \\cdot 10^{-3}$, $1.7 \\cdot 10^{-5}$, $1.6 \\cdot 10^{-10}$. What does the pattern rest on?",
                        "opts": [
                            "The function being a polynomial, so its tangent line agrees with it to second order everywhere",
                            "The step size falling below the tolerance, which forces the reported error down with it",
                            "The root being simple, so $f'$ is nonzero there and the leftover Taylor term is quadratic",
                            "The starting point being close, which is enough on its own to make any iteration square its error",
                        ],
                        "a": 2,
                        "whys": [
                            "Being a polynomial is neither needed nor sufficient: $\\sin$ and $\\exp$ square their errors under Newton too, and the polynomial $(x-1)^2$ does not, because its root is double.",
                            "The tolerance decides when to stop, not how fast the error falls. These errors are measured against the true root and would follow the same pattern with the test removed entirely.",
                            "Dividing by $f'(x_n)$ removes the linear term, so what is left over is the quadratic one, giving $e_{n+1} \\approx |f''/2f'|\\,e_n^2$ — which the trace confirms as 0.563.",
                            "Closeness is necessary and not sufficient. Start next to the double root of $(x-1)^2$ and Newton halves the error each step, which is bisection's rate with none of bisection's guarantee.",
                        ],
                        "why": r"""
Newton subtracts $f(x_n)/f'(x_n)$, which cancels the linear term of the Taylor
expansion exactly and leaves the quadratic one, so
$e_{n+1} \approx \frac{f''(r)}{2f'(r)}e_n^2$. That argument needs $f'(r) \neq 0$: at
a multiple root the denominator vanishes along with the numerator and the iteration
degrades to halving the error. The constant is not folklore either — the trace gives
0.5605 and 0.5629 for the last two ratios, and $|f''/2f'|$ at the root is 0.5630.
""",
                    },
                    {
                        "q": "A root finder stops when `abs(f(x)) < 1e-12`. On which function does that test do the most damage?",
                        "opts": [
                            "$f(x) = (x-1)^3$, where the residual is $10^{-12}$ while $x$ is still wrong in the fourth decimal",
                            "$f(x) = x - 1$, where the residual and the error are exactly equal, so the test has no margin left at all",
                            "$f(x) = 10^{8}(x-1)$, where the loop stops immediately and reports far more accuracy than it has",
                            "$f(x) = x^2 - 2$, where the residual is twice the error, so the test is off by a factor of two",
                            ],
                        "a": 0,
                        "whys": [
                            "Cubing shrinks the residual far faster than the error: at $x = 1.0001$ the residual is already $10^{-12}$, so the test accepts a value wrong in its fourth decimal place.",
                            "Here the test is exactly right — residual and error coincide — which is why the identity function is the one case the naive test handles perfectly and why it looks safe to people who try it there.",
                            "The steep function is a genuine failure and it goes the other way: no double other than the root itself has a residual below $10^{-12}$, so the loop cannot stop and reports failure on a solved problem.",
                            "A factor of two is not damage, it is a constant, and near $\\sqrt 2$ the slope is $2\\sqrt 2$, so the residual overstates the error by 2.8. Nothing is lost that a tolerance cannot absorb.",
                        ],
                        "why": r"""
The residual and the error are related by the slope: $|f(x)| \approx |f'(r)||x - r|$
near a simple root. When the slope is tiny, a small residual permits a large error —
$(x-1)^3$ has slope zero at the root, so `flat(1.0001)` is $10^{-12}$ and the test
accepts four correct digits as sixteen. When the slope is huge the same test cannot
be satisfied at all: for $10^8(x-1)$ the double next to the root already has a
residual of $2 \cdot 10^{-8}$. Testing the step instead measures the answer rather
than the equation.
""",
                    },
                    {
                        "q": "The secant method converges at order 1.618 and Newton at order 2. When is the secant method the better choice?",
                        "opts": [
                            "When $f$ is costly, since Newton spends two evaluations a step and the secant method reuses one",
                            "When the root is a multiple one, since a difference quotient stays finite as $f'$ vanishes",
                            "When a bracket is available, because unlike Newton the secant method keeps the root trapped throughout",
                            "When high accuracy is wanted, as an order below 2 avoids the overshoot that squaring the error causes",
                        ],
                        "a": 0,
                        "whys": [
                            "Per evaluation Newton earns $\\sqrt2 = 1.414$ and the secant method 1.618, so whenever an evaluation is the expensive thing — an ODE solve, a rendered frame — the cheaper step wins.",
                            "Both degrade at a multiple root, and for the same reason: the difference quotient is an estimate of the same vanishing derivative, so it goes to zero as well.",
                            "The secant method does not bracket. Its next iterate is an extrapolation as readily as an interpolation and can land outside the interval entirely, which is precisely what bisection refuses to do.",
                            "Nothing overshoots because of a high order. Squaring the error is what makes Newton reach the last bit sooner, and both methods finish at the same accuracy once the step falls under the tolerance.",
                        ],
                        "why": r"""
Convergence order per *step* is the wrong comparison when steps have different
prices. Newton calls $f$ and $f'$ each step, so its order-2 step costs two
evaluations and earns $2^{1/2} = 1.414$ per call; the secant method reuses the
previous value, so its order-1.618 step costs one and earns 1.618. When $f$ is an
entire simulation the difference is the whole decision, which is why the capstone
searches for a launch angle with secant steps rather than by differentiating a
trajectory.
""",
                    },
                    {
                        "q": "Newton on $f(x) = (x-1)^2$ from $x_0 = 2$ needs 34 steps to reach $10^{-10}$. What is happening?",
                        "opts": [
                            "The tolerance is being applied to the residual, which for a squared term is the error squared",
                            "The iteration becomes $x - (x-1)/2$, so the error halves rather than squaring at a double root",
                            "Round-off dominates once the derivative is small, so the last iterates wander instead of converging",
                            "The starting point is outside the basin of attraction, so early steps are spent travelling towards it",
                        ],
                        "a": 1,
                        "whys": [
                            "The stopping test is on the step, not the residual, and the count would be the same with the residual removed. What is slow here is the iteration itself, before any test is applied.",
                            "Substituting $f = (x-1)^2$ and $f' = 2(x-1)$ into the Newton step cancels one factor of $(x-1)$ and leaves half of it, so each step halves the distance to 1 exactly.",
                            "Round-off is not the issue at $10^{-10}$, which is six orders above the spacing there, and the iterates do not wander — they march down by a factor of two with complete regularity.",
                            "There is nothing to travel to: every starting point converges here, because the halving iteration is contracting everywhere. Slowness and non-convergence are different failures and this is the first.",
                        ],
                        "why": r"""
Put $f = (x-1)^2$ and $f' = 2(x-1)$ into $x - f/f'$ and one factor cancels, leaving
$x_{n+1} = x_n - (x_n - 1)/2$: the error is halved, not squared. The quadratic
argument assumed $f'(r) \neq 0$ and a double root breaks that assumption. The practical
signal is the pair of quantities heading to zero together — $f$ and $f'$ both vanish
at the root — which is also why a guard on a small derivative can fire before a
multiple root is reached, and why the lab has you write that guard and then meet it.
""",
                    },
                    {
                        "q": "`bracket_scan` samples $x^2 - 1$ at $-2, -1, 0, 1, 2$ and returns no brackets at all. Why?",
                        "opts": [
                            "The function is even, and a scan cannot separate a root from its mirror image on the far side",
                            "Its roots are irrational, so no sampled point can land near enough to either of them to register",
                            "Both roots sit on sample points, so every adjacent pair multiplies to zero rather than to a negative",
                            "The grid is too coarse, and refining it far enough would eventually make both of the sign changes appear",
                        ],
                        "a": 2,
                        "whys": [
                            "Evenness is a red herring: shift to $(x-0.5)^2 - 1$, which is not even, and the same grid finds both sign changes without difficulty. What matters is where the sample points fall.",
                            "The roots are $-1$ and $1$, both exactly representable and both exactly on the grid — which is the trouble here, rather than any inability to get close to them.",
                            "The test is a strictly negative product, and $f(-1)$ and $f(1)$ are exactly 0.0, so the pairs around them give zero and the scan passes over both roots.",
                            "Refining does help here, because these are simple roots that a shifted grid would straddle. It would not help for $x^2$, where no grid finds a sign change at all, since the function never changes sign.",
                        ],
                        "why": r"""
The scan keeps a subinterval when `f(a) * f(b) < 0`, and $f(-1)$ and $f(1)$ are
exactly zero, so the products around them are zero rather than negative. Two
perfectly ordinary simple roots vanish from the report. Move the grid and they come
back — but the deeper version of this blind spot does not: a root of even
multiplicity, such as the one $x^2$ has at the origin, produces no sign change
anywhere, so no bracketing method can find it however fine the sampling. That is the
price of the guarantee, and it is why the lab checks for the empty list rather than
pretending the case does not arise.
""",
                    },
                ],
            },
            "blanks": {
                "title": "A bracket and a tangent, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "roots.py — five holes; the comparisons decide which half survives and when to stop",
                "brief": r"""
Every line below is one of two decisions: which half of the bracket still contains a
root, and when the iteration has earned the right to stop. Nothing runs here. Filled
in correctly, `bisect` on the interval from 2 to 3 reports 39 steps and `newton`
reports 5 on the same equation.
""",
                "listing": r'''
def bisect(f, a, b, tol=1e-12, max_iter=200):
    """Halve the bracket until it is narrow enough. Returns (root, steps)."""
    fa, fb = f(a), f(b)
    if fa * fb ___ 0:
        raise ValueError("f(a) and f(b) must have opposite signs")
    steps = 0
    while (b - a) / 2 > tol and steps < max_iter:
        m = (a + b) / 2
        fm = f(m)
        steps += 1
        if fa * fm ___ 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return (a + b) / 2, steps


def newton(f, df, x0, tol=1e-12, max_iter=100):
    """Solve the tangent line instead of the curve. Returns (root, steps)."""
    x = float(x0)
    for k in range(1, max_iter + 1):
        slope = df(x)
        if abs(slope) < ___:
            raise ValueError("the derivative vanished")
        step = f(x) / ___
        x -= step
        if abs(___) <= tol:
            return x, k
    raise ValueError("did not converge")
''',
                "blanks": [
                    {
                        "prompt": "Refuse the interval when the two endpoint values share a sign.",
                        "hole": "?",
                        "opts": [">=", "==", ">", "<"],
                        "a": 2,
                        "why": "Two values of the same sign multiply to something strictly positive, and that is the one case with no trapped root; a product of exactly zero means an endpoint is itself a root, which is worth returning rather than refusing.",
                        "whys": [
                            "This refuses an interval whose endpoint is exactly a root, because the product is then zero. The caller is handed an exception for the one input on which the answer was already known.",
                            "A zero product is an endpoint sitting on a root, which is a success rather than an error, and every ordinary bracket has a strictly negative product and would sail past this test unrefused.",
                            "A strictly positive product is exactly the no-sign-change case, and it leaves a zero product free to be treated as the endpoint root it is.",
                            "This refuses precisely the intervals that do bracket a root and accepts the ones that do not, so every well-posed call raises and every hopeless one runs to max_iter.",
                        ],
                    },
                    {
                        "prompt": "Keep the left half when the sign change lies between a and the midpoint.",
                        "hole": "?",
                        "opts": ["> 0", "< 0", "== 0", "!= 0"],
                        "a": 1,
                        "why": "A negative product between f(a) and f(m) means the sign flips somewhere inside the left half, so the right endpoint moves down to the midpoint and the trapped root stays trapped.",
                        "whys": [
                            "This keeps the half that has no sign change in it and throws away the half that does, so the bracket loses the root on the first step and converges to whatever endpoint it drifts towards.",
                            "The sign change is inside the left half exactly when the product of the two values there is negative, which is the condition for moving b down to the midpoint.",
                            "A product of exactly zero happens only when the midpoint lands on the root, which is a rare and lucky event rather than the ordinary case, so the bracket would almost always take the other branch and never narrow from the right.",
                            "Every product that is not zero satisfies this, so the right endpoint moves down whether or not the root is in that half, and half the time the method discards the root it was holding.",
                        ],
                    },
                    {
                        "prompt": "The floor below which the slope counts as vanished.",
                        "hole": "?",
                        "opts": ["tol", "1e-14", "1e-300", "1.0"],
                        "a": 1,
                        "why": "A small fixed floor catches a derivative heading for zero before the division turns a finite step into an enormous one, and it is kept well below any sensible tolerance so that ordinary iterations never touch it.",
                        "whys": [
                            "The tolerance measures the answer, not the slope, and the two have unrelated scales. With tol at 1e-12 a perfectly usable slope of 1e-13 would be refused, and the method would give up on a solvable problem.",
                            "Small enough that no healthy iteration meets it, large enough to catch a division that is about to produce a meaningless step. The guard is what turns a silent numerical explosion into a message.",
                            "This is a guard in name only: a slope of 1e-200 sails past it and the division returns a step of order 1e200, so the next iterate is an infinity and no later test can recover from it.",
                            "A slope of 1.0 is entirely ordinary, so this refuses almost every real problem on the first iteration, including the cubic whose slope at the root is above 11.",
                        ],
                    },
                    {
                        "prompt": "The Newton step divides the function value by this.",
                        "hole": "?",
                        "opts": ["abs(slope)", "step", "tol", "slope"],
                        "a": 3,
                        "why": "The tangent at the current point has that slope, and solving the tangent line for zero gives the horizontal distance f(x) divided by it — which is the whole of Newton's method in one expression.",
                        "whys": [
                            "Discarding the sign sends the iterate the wrong way whenever the slope is negative, so on a decreasing function every step climbs away from the root instead of towards it.",
                            "The step is what this line computes, so it holds the previous iteration's value here and the first pass has nothing at all to divide by.",
                            "The tolerance is a stopping threshold, and dividing by it turns every step into a huge multiple of the function value, throwing the iterate far away on the first pass.",
                            "The tangent through the current point drops to zero after a horizontal distance of f(x) over its slope, and subtracting that distance is exactly the Newton update.",
                        ],
                    },
                    {
                        "prompt": "Stop when this has become smaller than the tolerance.",
                        "hole": "?",
                        "opts": ["step", "f(x)", "slope", "x"],
                        "a": 0,
                        "why": "The step is the distance the iterate moved, and near a simple root it is an estimate of the distance still to go; testing it measures the answer rather than the equation.",
                        "whys": [
                            "Once the iterate stops moving by more than the tolerance there is nothing left to gain, and near a simple root that step is a fair estimate of the remaining error.",
                            "This is the residual test, and it measures how well the equation is satisfied rather than how near the root is. On a flat root it accepts four correct digits; on a steep one it can never be satisfied at all.",
                            "The derivative has no reason to be small at a root, and for the cubic here it is above 11 at the answer, so this test would never fire and every call would run to max_iter.",
                            "The iterate itself is near 2.09 for this equation and never becomes small, so the loop would exhaust its iterations regardless of how well converged the answer is.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Three root finders and what they cost",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Five routines in `main.py`. Each root finder reports the root **and** the number of
iterations it took, because the count is the thing being compared.

## Bracketing

- `bracket_scan(f, lo, hi, n)` — split $[lo, hi]$ into `n` equal subintervals and
  return the list of `(a, b)` pairs on which `f(a) * f(b) < 0`, in order. Raises
  `ValueError` when `n < 1` or `hi <= lo`. A root that lands exactly on a sample
  point produces a zero product rather than a negative one and is not reported;
  that is the method's blind spot and one check pins it down.
- `bisect(f, a, b, tol=1e-12, max_iter=200)` — returns `(root, steps)`. If `f(a)` or
  `f(b)` is exactly zero, return that endpoint with 0 steps. Raise `ValueError` when
  `f(a) * f(b) > 0`. Otherwise halve while `(b - a) / 2 > tol`, counting each pass,
  and return the midpoint.
- `bisection_steps(a, b, tol)` — the step count predicted in advance:
  `ceil(log2((b - a) / (2 * tol)))`, never below 0. `ValueError` when `b <= a` or
  `tol <= 0`. On $[2, 3]$ this must agree with what `bisect` actually does.

## Iterating

- `newton(f, df, x0, tol=1e-12, max_iter=100)` — returns `(root, steps)`. Each pass
  computes the slope, raises `ValueError` when `abs(slope) < 1e-14`, takes the step
  `f(x) / slope`, and returns as soon as `abs(step) <= tol`. Raise `ValueError` if
  `max_iter` passes go by without that happening.
- `secant(f, x0, x1, tol=1e-12, max_iter=100)` — the same contract without `df`,
  using the slope through the last two points. Raise `ValueError` when the two
  function values are equal, since the secant is then horizontal.

```text
f(x) = x**3 - 2*x - 5,  root 2.0945514815423265

bisect(f, 2, 3)            ->  (2.094551481542112, 39)
bisection_steps(2, 3, 1e-12)  ->  39
newton(f, df, 2.0)         ->  (2.0945514815423265, 5)
secant(f, 2.0, 3.0)        ->  (2.0945514815423265, 7)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def bracket_scan(f, lo, hi, n):
    """Subintervals of [lo, hi] on which f changes sign."""
    # your code here


def bisect(f, a, b, tol=1e-12, max_iter=200):
    """Halve the bracket until it is narrow enough. Returns (root, steps)."""
    # your code here


def bisection_steps(a, b, tol):
    """How many halvings the tolerance needs, worked out in advance."""
    # your code here


def newton(f, df, x0, tol=1e-12, max_iter=100):
    """Solve the tangent line instead of the curve. Returns (root, steps)."""
    # your code here


def secant(f, x0, x1, tol=1e-12, max_iter=100):
    """Newton with the derivative replaced by a difference quotient."""
    # your code here


def f(x):
    return x**3 - 2*x - 5


def df(x):
    return 3*x*x - 2


print("brackets:", bracket_scan(f, 0.0, 4.0, 8))
print("bisect:  ", bisect(f, 2.0, 3.0))
print("newton:  ", newton(f, df, 2.0))
print("secant:  ", secant(f, 2.0, 3.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def bracket_scan(f, lo, hi, n):
    """Subintervals of [lo, hi] on which f changes sign."""
    if n < 1:
        raise ValueError("n must be at least 1")
    if hi <= lo:
        raise ValueError("hi must be above lo")
    width = (hi - lo) / n
    out = []
    left = lo
    fleft = f(lo)
    for i in range(1, n + 1):
        right = lo + i * width
        fright = f(right)
        if fleft * fright < 0:
            out.append((left, right))
        left, fleft = right, fright
    return out


def bisect(f, a, b, tol=1e-12, max_iter=200):
    """Halve the bracket until it is narrow enough. Returns (root, steps)."""
    a, b = float(a), float(b)
    fa, fb = f(a), f(b)
    if fa == 0.0:
        return a, 0
    if fb == 0.0:
        return b, 0
    if fa * fb > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")
    steps = 0
    while (b - a) / 2 > tol and steps < max_iter:
        m = (a + b) / 2
        fm = f(m)
        steps += 1
        if fm == 0.0:
            return m, steps
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return (a + b) / 2, steps


def bisection_steps(a, b, tol):
    """How many halvings the tolerance needs, worked out in advance."""
    if b <= a:
        raise ValueError("b must be above a")
    if tol <= 0:
        raise ValueError("the tolerance must be positive")
    return max(0, math.ceil(math.log2((b - a) / (2 * tol))))


def newton(f, df, x0, tol=1e-12, max_iter=100):
    """Solve the tangent line instead of the curve. Returns (root, steps)."""
    x = float(x0)
    for k in range(1, max_iter + 1):
        slope = df(x)
        if abs(slope) < 1e-14:
            raise ValueError("the derivative vanished")
        step = f(x) / slope
        x -= step
        if abs(step) <= tol:
            return x, k
    raise ValueError("did not converge")


def secant(f, x0, x1, tol=1e-12, max_iter=100):
    """Newton with the derivative replaced by a difference quotient."""
    x0, x1 = float(x0), float(x1)
    f0, f1 = f(x0), f(x1)
    for k in range(1, max_iter + 1):
        if f1 == f0:
            raise ValueError("the secant is horizontal")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        step = x2 - x1
        x0, f0 = x1, f1
        x1, f1 = x2, f(x2)
        if abs(step) <= tol:
            return x1, k
    raise ValueError("did not converge")


def f(x):
    return x**3 - 2*x - 5


def df(x):
    return 3*x*x - 2


print("brackets:", bracket_scan(f, 0.0, 4.0, 8))
print("bisect:  ", bisect(f, 2.0, 3.0))
print("newton:  ", newton(f, df, 2.0))
print("secant:  ", secant(f, 2.0, 3.0))
'''}],
                "hints": [
                    "`bracket_scan` should evaluate `f` once per grid point, not twice: carry the previous value forward in a variable and compare it against the new one, the way the bisection loop carries `fa`.",
                    "In `bisect`, keep `fa` alongside `a` and update them together. Recomputing `f(a)` inside the loop doubles the evaluation count, which is the quantity the whole lab is about.",
                    "`bisection_steps` is `ceil(log2((b - a) / (2 * tol)))` clamped at zero. The 2 is there because reporting the midpoint of the final bracket halves the width one more time.",
                    "`newton` and `secant` share a shape: compute a step, apply it, then test `abs(step) <= tol` *after* applying it, so the returned root is the improved one rather than the value that was tested.",
                ],
                "tests": [
                    {"name": "Bisection halves an interval and counts its steps", "code": r'''
def _f(x):
    return x**3 - 2*x - 5
_root, _steps = bisect(_f, 2.0, 3.0)
assert abs(_root - 2.0945514815423265) < 1e-12, f"bisect returned the root {_root!r}"
assert _steps == 39, f"bisect took {_steps} steps on [2, 3] to 1e-12, expected 39"
_root3, _steps3 = bisect(_f, 2.0, 3.0, tol=1e-3)
assert _steps3 == 9, f"At a tolerance of 1e-3 the count is 9, got {_steps3}"
assert abs(_root3 - 2.0945514815423265) < 1e-3, f"bisect to 1e-3 returned {_root3!r}"
'''},
                    {"name": "Bisection refuses what it cannot trap", "code": r'''
def _f(x):
    return x**3 - 2*x - 5
for _a, _b in [(0.0, 2.0), (3.0, 4.0), (-1.0, 1.0)]:
    try:
        bisect(_f, _a, _b)
        assert False, f"bisect over ({_a}, {_b}) has no sign change and should raise ValueError"
    except ValueError:
        pass
_r, _s = bisect(lambda x: x*x - 4.0, 2.0, 5.0)
assert _r == 2.0 and _s == 0, f"An endpoint that is already a root returns (2.0, 0); got {(_r, _s)!r}"
_r, _s = bisect(lambda x: x*x - 25.0, 2.0, 5.0)
assert _r == 5.0 and _s == 0, f"The right endpoint case gave {(_r, _s)!r}"
'''},
                    {"name": "The predicted step count matches the measured one", "code": r'''
def _f(x):
    return x**3 - 2*x - 5
assert bisection_steps(2.0, 3.0, 1e-12) == 39, \
    f"bisection_steps(2, 3, 1e-12) gave {bisection_steps(2.0, 3.0, 1e-12)!r}, expected 39"
assert bisection_steps(2.0, 3.0, 1e-3) == 9, \
    f"bisection_steps(2, 3, 1e-3) gave {bisection_steps(2.0, 3.0, 1e-3)!r}, expected 9"
assert bisection_steps(0.0, 1.0, 1.0) == 0, "A tolerance wider than the bracket needs no steps"
for _tol in (1e-3, 1e-6, 1e-9, 1e-12):
    assert bisect(_f, 2.0, 3.0, tol=_tol)[1] == bisection_steps(2.0, 3.0, _tol), \
        f"prediction and measurement disagree at tol = {_tol}"
for _args in [(3.0, 2.0, 1e-6), (1.0, 1.0, 1e-6), (0.0, 1.0, 0.0), (0.0, 1.0, -1e-6)]:
    try:
        bisection_steps(*_args)
        assert False, f"bisection_steps{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Newton squares the error at a simple root", "code": r'''
def _f(x):
    return x**3 - 2*x - 5
def _df(x):
    return 3*x*x - 2
_root, _steps = newton(_f, _df, 2.0)
assert abs(_root - 2.0945514815423265) < 1e-14, f"newton returned {_root!r}"
assert _steps == 5, f"newton took {_steps} steps from 2.0, expected 5"
assert newton(_f, _df, 10.0)[1] <= 12, "From 10.0 it should still finish well inside 12 steps"
_r, _s = newton(lambda x: math.cos(x) - x, lambda x: -math.sin(x) - 1.0, 1.0)
assert abs(_r - 0.7390851332151607) < 1e-14, f"cos(x) = x has the root 0.739085...; got {_r!r}"
assert _s <= 6, f"That root should take at most 6 steps, took {_s}"
'''},
                    {"name": "Newton reports the ways it can fail", "code": r'''
try:
    newton(lambda x: x*x + 1.0, lambda x: 2.0*x, 0.0)
    assert False, "A zero derivative at the start should raise ValueError"
except ValueError:
    pass
try:
    newton(lambda x: x**3 - 2*x + 2, lambda x: 3*x*x - 2, 0.0, max_iter=50)
    assert False, "x^3 - 2x + 2 from 0.0 cycles between 0 and 1 and should raise ValueError"
except ValueError:
    pass
try:
    newton(lambda x: x**3 - 2*x - 5, lambda x: 3*x*x - 2, 2.0, max_iter=1)
    assert False, "One iteration is not enough to reach 1e-12 and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "A double root costs Newton its speed", "code": r'''
_simple, _s1 = newton(lambda x: x*x - 1.0, lambda x: 2.0*x, 2.0, tol=1e-10)
assert abs(_simple - 1.0) < 1e-9 and _s1 <= 7, \
    f"The simple root of x^2 - 1 took {_s1} steps to {_simple!r}"
_double, _s2 = newton(lambda x: (x - 1.0)**2, lambda x: 2.0*(x - 1.0), 2.0, tol=1e-10)
assert abs(_double - 1.0) < 1e-9, f"The double root came out at {_double!r}"
assert _s2 >= 25, f"At a double root the error only halves, so this should take 25 steps or " \
    f"more; it took {_s2}"
assert _s2 > 3 * _s1, "The double root must cost several times what the simple one did"
'''},
                    {"name": "The secant method, without a derivative", "code": r'''
def _f(x):
    return x**3 - 2*x - 5
_root, _steps = secant(_f, 2.0, 3.0)
assert abs(_root - 2.0945514815423265) < 1e-12, f"secant returned {_root!r}"
assert _steps == 7, f"secant took {_steps} steps from (2, 3), expected 7"
assert _steps < bisect(_f, 2.0, 3.0)[1], "The secant method should beat bisection on step count"
_r, _s = secant(lambda x: math.exp(x) - 3.0, 0.5, 2.0)
assert abs(_r - math.log(3.0)) < 1e-12, f"exp(x) = 3 has the root log 3; got {_r!r}"
try:
    secant(lambda x: 4.0, 0.0, 1.0)
    assert False, "Equal function values leave a horizontal secant and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Scanning for sign changes, and the roots it cannot see", "code": r'''
_cubic = lambda x: (x - 0.3) * (x - 1.7) * (x - 2.9)
_found = bracket_scan(_cubic, 0.0, 4.0, 8)
assert _found == [(0.0, 0.5), (1.5, 2.0), (2.5, 3.0)], f"bracket_scan gave {_found!r}"
for _a, _b in _found:
    assert _cubic(_a) * _cubic(_b) < 0, "every reported pair must actually change sign"
assert bracket_scan(_cubic, 0.0, 4.0, 1) == [(0.0, 4.0)], \
    "With one subinterval the ends still differ in sign, so a single bracket holding " \
    "all three roots is reported — a sign change means an odd number of roots, not one"
assert bracket_scan(lambda x: x*x - 1.0, -2.0, 2.0, 4) == [], \
    "Both roots sit on sample points, so every product is zero rather than negative"
assert bracket_scan(lambda x: x*x, -2.0, 2.0, 8) == [], \
    "A double root has no sign change anywhere, at any resolution"
for _args in [(0.0, 4.0, 0), (0.0, 4.0, -3), (4.0, 0.0, 8), (1.0, 1.0, 8)]:
    try:
        bracket_scan(_cubic, *_args)
        assert False, f"bracket_scan with {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Linear systems, pivoting and conditioning",
            "summary": "Elimination written so that a small pivot cannot destroy it, and a number that says how much to trust the answer.",
            "concepts": [
                "The three elementary row operations leave the solution set alone, which is what licenses elimination",
                "The multiplier a[i][k] / a[k][k] is enormous when the pivot is small, and it swamps the row it acts on",
                "Partial pivoting takes the largest available pivot, so every multiplier has magnitude at most 1",
                "The multipliers are L, the eliminated matrix is U, the swaps are P, and PA = LU records the whole elimination",
                "Factorising costs about n^3/3 operations and each extra right-hand side then costs only n^2",
                "The determinant is the product of the pivots, negated once per row interchange",
                "A small residual is not a small error: the condition number is the factor between them",
                "A relative residual of 10^-6 on a matrix conditioned at 10^6 guarantees nothing at all",
            ],
            "read": [
                {
                    "title": "The pivot decides the answer",
                    "minutes": 13,
                    "body": r'''
Two equations, and their answer is $x = y = 1$ to sixteen digits:

$$10^{-17}x + y = 1, \qquad x + y = 2$$

Solve them by the elimination everyone is taught. Subtract $m$ copies of the first
row from the second, where $m$ is chosen to knock out the $x$ term:

```python
a = [[1e-17, 1.0], [1.0, 1.0]]
b = [1.0, 2.0]

m = a[1][0] / a[0][0]
row = [a[1][0] - m * a[0][0], a[1][1] - m * a[0][1]]
rhs = b[1] - m * b[0]
print(m, row, rhs)

y = rhs / row[1]
x = (b[0] - a[0][1] * y) / a[0][0]
print(x, y)
```

The multiplier is `1e+17`, the eliminated row is `[0.0, -1e+17]` with a right-hand
side of `-1e+17`, and the answer comes out as `0.0 1.0`. The $y$ is right and the
$x$ has no correct digits whatever — not a rounding in the last place, a wrong
answer, from a matrix that is nowhere near singular.

## Where the digits went

The second equation says $x + y = 2$. After the elimination step its coefficient of
$y$ is $1 - 10^{17} \cdot 1$, and its right-hand side is $2 - 10^{17} \cdot 1$. Both
of those subtract a modest number from an enormous one, and at $10^{17}$ the spacing
between neighbouring doubles is 16, so the 1 and the 2 fall off the end. Both round
to $-10^{17}$, and the $y$ they produce is 1 — accidentally right, because the two
discarded numbers were of similar size. Then the back substitution divides by the
pivot: $x = (1 - y)/10^{-17}$. The numerator is a subtraction of near-equals whose
error is the whole of what is left, and dividing by $10^{-17}$ multiplies that error
by $10^{17}$.

The row operations themselves are sound. Adding a multiple of one equation to
another does not change which pairs $(x, y)$ satisfy the system, and neither does
swapping two equations or scaling one — that is what licenses elimination in the
first place. What the arithmetic destroyed is the *information* in the second row.
Multiplying row 1 by $10^{17}$ made its entries so large that row 2's own numbers had
nothing left to say.

## Choose the pivot rather than accepting it

Since exchanging two equations is one of the legal operations, use it. Look down the
column for the entry of largest magnitude, bring it up, and eliminate with that.

```python
a = [[1.0, 1.0], [1e-17, 1.0]]
b = [2.0, 1.0]

m = a[1][0] / a[0][0]
row = [a[1][0] - m * a[0][0], a[1][1] - m * a[0][1]]
rhs = b[1] - m * b[0]
print(m, row, rhs)

y = rhs / row[1]
x = (b[0] - a[0][1] * y) / a[0][0]
print(x, y)
```

Now the multiplier is `1e-17`, the eliminated row is `[0.0, 1.0]`, and the answer is
`1.0 1.0`. Same system, same operations, different order — and every digit is
correct.

The rule generalises to one line: at step $k$, pick the row $p \geq k$ with the
largest $|a_{pk}|$ and swap it into position. Then every multiplier
$m_{ik} = a_{ik}/a_{kk}$ has $|m_{ik}| \leq 1$ by construction, so no elimination
step can inflate an entry by more than a factor of two. That is **partial pivoting**,
and it is not a tidiness or a convention. It is the difference between the two runs
above.

## The factorisation is the record of the elimination

Nothing about the elimination depends on the right-hand side, so it is worth keeping.
The multipliers $m_{ik}$, stored where the zeros they created went, form a unit lower
triangular $L$; what is left of the matrix is upper triangular $U$; and the row swaps
are a permutation $P$. Together

$$PA = LU$$

For $A = \begin{bmatrix} 4 & 3 & 2 \\ 1 & 5 & 7 \\ 2 & 2 & 9 \end{bmatrix}$ no swaps
are needed and the factors are $L$ with multipliers $0.25$, $0.5$ and
$0.1176470588$, and $U$ with diagonal $4$, $4.25$, $7.2352941176$. Solving is then
two triangular sweeps: forward substitution through $L$, back substitution through
$U$.

The point of keeping the factors is arithmetic. The elimination is about $n^{3}/3$
multiply-adds; each triangular sweep is about $n^{2}/2$. For $n = 1000$ that is 333
million against a million, so a second right-hand side against the same matrix costs
a third of a percent of the first. Any code that calls a general solver in a loop
over right-hand sides is paying the $n^3$ three hundred times over.

The determinant falls out of the same factors: $\det(A) = \pm\prod_k U_{kk}$, with the
sign flipped once per row interchange. For the matrix above,
$4 \cdot 4.25 \cdot 7.2352941176 = 123$, exactly the determinant, and it costs
nothing beyond the factorisation that was going to happen anyway.

## The mistake: reading the residual as the error

Given a computed $\tilde{x}$, the residual $r = b - A\tilde{x}$ is available for the
price of one matrix-vector product, and it is the natural thing to check. Watch it
mislead.

```python
A = [[0.780, 0.563], [0.913, 0.659]]
b = [0.217, 0.254]

for name, x in [("near", [0.999, -1.001]), ("far", [0.341, -0.087])]:
    ax = [A[i][0]*x[0] + A[i][1]*x[1] for i in (0, 1)]
    r = [b[i] - ax[i] for i in (0, 1)]
    print(name, max(abs(v) for v in r))
```

The true solution is $x = (1, -1)$. The candidate `near` is wrong by $10^{-3}$ in
each component and has a residual of $1.57 \cdot 10^{-3}$. The candidate `far` is
wrong by $0.913$ — it is not in the same neighbourhood as the answer — and its
residual is $10^{-6}$, more than a thousand times *smaller*. Anyone ranking answers
by residual would take the useless one.

The tempting part is that the reasoning behind the check is nearly right. A small
residual does mean the candidate nearly satisfies the equations. What it does not
mean is that the candidate is near the solution, and the factor between the two is a
property of the matrix:

$$\frac{\|\Delta x\|}{\|x\|} \leq \kappa(A)\,\frac{\|r\|}{\|b\|}, \qquad
\kappa(A) = \|A\|\,\|A^{-1}\|$$

```python
A = [[0.780, 0.563], [0.913, 0.659]]
det = A[0][0]*A[1][1] - A[0][1]*A[1][0]
inv = [[A[1][1]/det, -A[0][1]/det], [-A[1][0]/det, A[0][0]/det]]
rows = lambda m: max(sum(abs(v) for v in row) for row in m)
print(det)
print(rows(A) * rows(inv))
```

The determinant is $10^{-6}$ and the condition number is $2661396$. The relative
residual of the `far` candidate is about $4 \cdot 10^{-6}$; multiply by $\kappa$ and
the bound on the relative error is 10.5, which is to say no accuracy is promised at
all. The bound is not being pessimistic. It is describing a matrix whose two rows are
very nearly parallel, so that a whole ridge of candidates satisfies the equations to
six digits.

## Where this stops holding

Partial pivoting bounds every multiplier by 1, but it bounds the *growth* of the
matrix entries only by $2^{n-1}$, and matrices attaining that bound can be
constructed. In fifty years of practice they have essentially never arisen from a
real problem, which is why partial pivoting is the default everywhere while complete
pivoting, which is safe and costs a column search as well, is not.

The deeper limit is that pivoting cannot rescue an ill-conditioned matrix, because
the difficulty is in the problem rather than the algorithm. The Hilbert matrices
$H_{ij} = 1/(i+j+1)$ make the point:

```text
 n   condition number     error in the computed solution
 2       27                6.7e-16
 3      748                2.2e-16
 4    2.8e4                2.4e-13
 5    9.4e5                7.1e-13
 6    2.9e7                6.8e-11
```

Every one of those was solved with full partial pivoting. The error tracks the
condition number, and the working rule of thumb is that you lose
$\log_{10}\kappa$ decimal digits no matter how careful the code is. Reporting
$\kappa$ beside the answer is the honest thing to do, and it is what the capstone's
report does.

## What the lab asks

**Elimination that survives a small pivot** has you write `lu_decompose` returning
`(l, u, perm, sign)`, `lu_solve` for the two triangular sweeps, `solve`,
`determinant` from the pivots, `inverse` by solving against each column of the
identity, `residual`, `norm_inf`, and `condition_inf`. Two checks are the ones to
watch: solving the $10^{-17}$ system above must give $(1, 1)$, which no unpivoted
elimination can do, and a check reproduces the residual paradox by asserting that the
far-away candidate really does have the smaller residual.
''',
                },
            ],
            "quiz": {
                "title": "Pivots, factors and how much to trust an answer",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Eliminating with the pivot $10^{-17}$ returned $x = 0$ where the answer is $x = 1$. Which step lost the information?",
                        "opts": [
                            "The division by a pivot of $10^{-17}$, which overflowed the exponent range",
                            "Subtracting $10^{17}$ times row 1 from row 2, which rounded row 2's own entries away",
                            "The back substitution, since dividing by a small pivot magnifies whatever error reaches it",
                            "The matrix is nearly singular, so no ordering of the operations could have recovered $x$",
                        ],
                        "a": 1,
                        "whys": [
                            "Nothing overflows: $10^{17}$ is fifteen orders below the largest double, and the division is exact. The damage is in an addition, not in the range of the exponent.",
                            "At $10^{17}$ the gap between doubles is 16, so the 1 and the 2 that row 2 contributed fall off the end and both entries round to $-10^{17}$ — the second equation is gone.",
                            "The back substitution does magnify the error, by the full $10^{17}$, but it magnifies an error that arrived already made. Swap the rows and the same division happens with no trouble at all.",
                            "The determinant is about $-1$ and the condition number is near 2, so this matrix is about as well behaved as a matrix gets. Swapping the rows recovers every digit, which settles it.",
                        ],
                        "why": r"""
The multiplier is $10^{17}$, so the elimination computes $1 - 10^{17}$ and
$2 - 10^{17}$. Doubles near $10^{17}$ are 16 apart, so both subtractions return
$-10^{17}$ and everything the second equation knew has been rounded away. The later
division by the small pivot then scales the resulting error up by $10^{17}$, which is
why the wrongness is total rather than slight — but the loss happened in the
subtraction, and swapping the rows first avoids it entirely.
""",
                    },
                    {
                        "q": "Partial pivoting takes the largest available entry in the column. What does that actually buy?",
                        "opts": [
                            "Every multiplier then has magnitude at most 1, so an elimination step cannot inflate a row",
                            "The pivot is then never zero, which is what makes the factorisation exist for any matrix at all",
                            "The condition number falls, so the computed solution has a smaller error bound",
                            "It orders the rows by size, which keeps the diagonal dominant and the back substitution stable",
                        ],
                        "a": 0,
                        "whys": [
                            "The multiplier is the column entry over the pivot, and choosing the largest entry as the pivot makes that ratio at most 1, so no row can be scaled up by the elimination.",
                            "A column that is entirely zero has no nonzero pivot to find, and that is exactly the singular case the routine has to refuse. Pivoting chooses the best available entry; it cannot manufacture one.",
                            "The condition number belongs to the matrix and no reordering changes it. Pivoting protects the algorithm from making things worse than the matrix already is, which is a different guarantee.",
                            "Only the current column is examined, and later steps re-order what is below them, so nothing global about the diagonal is established. Diagonal dominance is a property some matrices have and pivoting does not create it.",
                        ],
                        "why": r"""
The multiplier is $a_{ik}/a_{kk}$, and taking the largest available $|a_{kk}|$ makes
every one of them at most 1 in magnitude. An entry updated as
$a_{ij} - m\,a_{kj}$ with $|m| \leq 1$ cannot more than double, so nothing in the
matrix can grow explosively and swamp the numbers around it. That is the whole
mechanism, and it is worth being clear about what it does not do: the condition
number is a property of the matrix, and pivoting leaves it exactly where it was.
""",
                    },
                    {
                        "q": "Why keep $L$, $U$ and the permutation rather than calling a general solver again for a second right-hand side?",
                        "opts": [
                            "The factors are more accurate than a fresh elimination would be",
                            "A fresh solve would pick different pivots and could return a different answer for the same input",
                            "The elimination costs about $n^3/3$ and a pair of triangular sweeps costs about $n^2$",
                            "The factors compress the matrix, so a large system needs far less memory once it is factored",
                        ],
                        "a": 2,
                        "whys": [
                            "Both routes do the same arithmetic in the same order and produce the same factors, so accuracy is identical. What differs is how many times that arithmetic is performed.",
                            "The pivot choice depends only on the matrix, not on the right-hand side, so a second elimination reproduces the same factors exactly. Determinism is not the reason to keep them.",
                            "At $n = 1000$ that is 333 million operations against a million, so the second right-hand side costs a third of a percent of the first once the factors are in hand.",
                            "L and U together hold $n^2$ numbers, the same as the matrix they came from — they are usually stored in its place rather than beside it. Nothing is compressed.",
                        ],
                        "why": r"""
The factorisation is cubic and the two triangular sweeps are quadratic, so once the
elimination is paid for, extra right-hand sides are nearly free. That is why a
library exposes a factor step and a solve step separately, and why computing an
inverse by solving against each column of the identity is one factorisation and $n$
sweeps rather than $n$ eliminations. It is also the reason the capstone factors its
normal-equation matrix once and reuses it.
""",
                    },
                    {
                        "q": "For $A = [[0.780, 0.563], [0.913, 0.659]]$ and $b = (0.217, 0.254)$, the candidate $(0.341, -0.087)$ has residual $10^{-6}$ and the candidate $(0.999, -1.001)$ has residual $1.6 \\cdot 10^{-3}$. The true solution is $(1, -1)$. What follows?",
                        "opts": [
                            "One of the residuals must be wrong, since a nearer answer fits better",
                            "The residual ranks how well each candidate satisfies the equations, not how near it is",
                            "The system has more than one solution, and the far candidate satisfies a different one of them",
                            "The residual should have been measured relative to $b$, which reverses the ranking of the two",
                        ],
                        "a": 1,
                        "whys": [
                            "Both are arithmetic anyone can repeat, and both are correct. The instinct that a nearer answer must fit better is the thing this example exists to break.",
                            "The rows are nearly parallel, so a long thin ridge of candidates satisfies the equations to six digits, and being on that ridge says nothing about being near the corner where it crosses.",
                            "The determinant is $10^{-6}$, small but not zero, so the solution is unique. Near-singular and singular are different, and the whole difficulty lives in the gap between them.",
                            "Dividing both residuals by the same $\\|b\\|$ scales them equally and cannot change which is larger. The relative residual is the right quantity for the error bound, and it preserves the ordering.",
                        ],
                        "why": r"""
The residual answers "does this nearly satisfy the equations" and the error answers
"is this near the solution". The bound linking them,
$\|\Delta x\|/\|x\| \leq \kappa(A)\|r\|/\|b\|$, has a factor of
$\kappa(A) = 2661396$ in it here, so a relative residual of $4 \cdot 10^{-6}$ permits
a relative error above 10. The two rows of this matrix are nearly parallel, and the
pair of lines they describe cross at such a shallow angle that a whole ridge of
points lies within $10^{-6}$ of both.
""",
                    },
                    {
                        "q": "A solver reports a condition number of $2.9 \\cdot 10^{7}$ for a $6 \\times 6$ system. What should you expect of the answer?",
                        "opts": [
                            "About seven decimal digits lost, leaving roughly nine of the sixteen a double can hold",
                            "The solve is unreliable and the whole system should be re-solved at a much tighter tolerance",
                            "About seven digits lost, and a better pivoting rule would recover most of them",
                            "Nothing about accuracy: a condition number describes the matrix, not the solution",
                        ],
                        "a": 0,
                        "whys": [
                            "The working rule is that $\\log_{10}\\kappa$ digits go, and $\\log_{10}(2.9 \\cdot 10^{7})$ is 7.5 — which matches the Hilbert table, where a condition of $2.9 \\cdot 10^{7}$ came with an error of $7 \\cdot 10^{-11}$.",
                            "There is no tolerance to tighten. A direct solve is not an iteration and does the same fixed sequence of operations however unhappy you are with the answer.",
                            "Partial pivoting is already keeping the algorithm from adding error of its own, and the loss described here is the problem's, not the algorithm's. Complete pivoting would change essentially nothing.",
                            "It describes the matrix and that is precisely why it predicts the solution's accuracy: it is the factor by which the matrix magnifies any perturbation, including the rounding of the inputs.",
                        ],
                        "why": r"""
The condition number is the factor by which relative perturbations of the data are
magnified in the answer. The inputs are already perturbed by rounding, at a relative
$10^{-16}$, so the output can be off by $\kappa \cdot 10^{-16}$ — here about
$3 \cdot 10^{-9}$, which is a loss of roughly seven and a half digits. The Hilbert
table bears it out. None of that is a fault to fix: it is the honest reading, and the
reason a numerical routine that returns a bare vector is telling you less than it
knows.
""",
                    },
                    {
                        "q": "`lu_decompose` raises `ValueError` when the largest remaining entry in a column is below $10^{-14}$. What is that test really deciding?",
                        "opts": [
                            "Whether the matrix is singular exactly, which for a floating-point matrix is decidable",
                            "Whether that column has been fully eliminated already, which is the normal end of the factorisation",
                            "Whether the remaining column is small enough that its content is round-off rather than data",
                            "Whether the pivot search failed, which happens when two rows of the matrix are identical",
                        ],
                        "a": 2,
                        "whys": [
                            "Exact singularity is not decidable from a rounded matrix: a genuinely singular one usually leaves a pivot of $10^{-17}$ rather than 0.0, and a well-conditioned one can carry a small entry honestly. The test is a judgement, not a proof.",
                            "Elimination clears the entries *below* the pivot, never the pivot itself, so a healthy factorisation ends with every diagonal entry nonzero. A whole column of zeros at and below the diagonal is the failure case, not the finish.",
                            "After elimination the surviving entries are differences of larger numbers, so a value at the $10^{-14}$ level is what cancellation leaves behind rather than a coefficient anyone supplied.",
                            "Two identical rows do produce a singular matrix, and the search does not fail — it returns a pivot, and the entry it finds is a cancelled zero. The test is about the magnitude found, not about the search.",
                        ],
                        "why": r"""
By the time a column is reached its entries are differences of numbers that were
larger, so what a truly singular matrix leaves at the pivot is not 0.0 but something
at the level of the round-off, perhaps $10^{-17}$. A tolerance is the only workable
test, and choosing it is a judgement about scale: for a matrix whose entries are all
around $10^{-15}$ the threshold would refuse a perfectly good system. That is the
argument for scaling a problem before solving it, and for reporting the condition
number rather than a yes-or-no verdict on singularity.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Elimination with partial pivoting, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "linsolve.py — five holes; get them right and the 1e-17 system returns (1.0, 1.0)",
                "brief": r"""
The pivot search is three lines and it is the whole difference between an answer and
a wrong answer. Nothing runs here. Filled in correctly, this factorisation reproduces
PA = LU to the last bit, and the determinant it implies for the 3 by 3 in the reading
is exactly 123.
""",
                "listing": r'''
def lu_decompose(a, tol=1e-14):
    """PA = LU by elimination with partial pivoting."""
    n = len(a)
    u = [[float(v) for v in row] for row in a]
    l = [[0.0] * n for _ in range(n)]
    perm = list(range(n))
    sign = 1
    for k in range(n):
        p = max(range(___, n), key=lambda i: abs(u[i][k]))
        if abs(u[p][k]) ___ tol:
            raise ValueError("the matrix is singular to working precision")
        if p != k:
            u[k], u[p] = u[p], u[k]
            l[k], l[p] = l[p], l[k]
            perm[k], perm[p] = perm[p], perm[k]
            sign = ___
        l[k][k] = 1.0
        for i in range(k + 1, n):
            factor = u[i][k] / ___
            l[i][k] = factor
            for j in range(k, n):
                u[i][j] -= factor * ___
    return l, u, perm, sign
''',
                "blanks": [
                    {
                        "prompt": "The pivot search starts at this row.",
                        "hole": "?",
                        "opts": ["0", "k", "k + 1", "n - 1"],
                        "a": 1,
                        "why": "Rows above k have already been used as pivots and their eliminated entries are finished work; the search runs over the rows still in play, which begins at the diagonal itself.",
                        "whys": [
                            "Searching from the top can select a row that has already served as a pivot, and swapping it down undoes the elimination that row was the record of.",
                            "The rows from k downwards are the ones not yet used, and the diagonal entry is a candidate like any other — often the winner, in which case no swap happens at all.",
                            "Skipping the diagonal means the current row can never be its own pivot, so a matrix that is already in perfect order gets shuffled at every step, and for the last column there is nothing left to search.",
                            "This looks at the bottom row alone, so the pivot is whatever happens to be there and the search that gives the method its name never takes place.",
                        ],
                    },
                    {
                        "prompt": "Refuse the matrix when the best pivot available is this small.",
                        "hole": "?",
                        "opts": ["<=", ">=", "==", "!="],
                        "a": 0,
                        "why": "A pivot at or below the tolerance means the largest entry left in that column is at the level of round-off, so there is no real coefficient to divide by and the factorisation cannot continue honestly.",
                        "whys": [
                            "At or below the threshold there is nothing but cancellation residue left in the column, and dividing by it would manufacture enormous multipliers out of noise.",
                            "This refuses every healthy matrix, since an ordinary pivot is far above 1e-14, and accepts exactly the singular ones it was written to catch.",
                            "Testing for equality catches only a pivot that is exactly 0.0, and a singular matrix rarely leaves that — after elimination it leaves something around 1e-17, which sails through and divides.",
                            "Any pivot other than exactly the tolerance raises, which is every matrix ever passed in, so the routine never factors anything.",
                        ],
                    },
                    {
                        "prompt": "A row interchange does this to the sign that the determinant carries.",
                        "hole": "?",
                        "opts": ["sign", "-sign", "1", "abs(sign)"],
                        "a": 1,
                        "why": "Exchanging two rows of a matrix negates its determinant, so the running sign flips once per swap and the product of the pivots has to be multiplied by it at the end.",
                        "whys": [
                            "Leaving the sign alone loses one fact per swap, and the determinant then comes out with the wrong sign whenever an odd number of interchanges happened.",
                            "One interchange negates the determinant, so tracking the parity of the swaps is all that is needed to recover it from the product of the pivots.",
                            "Resetting to 1 discards every swap made so far rather than the one being made now, so two interchanges followed by a third report a positive determinant instead of a negative one.",
                            "The absolute value throws the parity away permanently, which is the one piece of information this variable exists to carry.",
                        ],
                    },
                    {
                        "prompt": "The multiplier divides the entry below the pivot by the pivot itself.",
                        "hole": "?",
                        "opts": ["u[i][i]", "u[k][k]", "u[i][k]", "a[k][k]"],
                        "a": 1,
                        "why": "After the swap the pivot sits at row k, column k, and the multiplier is the entry being cleared divided by it — which with partial pivoting makes the ratio at most 1 in magnitude.",
                        "whys": [
                            "This is the diagonal entry of the row being eliminated, which has nothing to do with the column being cleared and has not been computed yet for rows below k.",
                            "The pivot is at row k and column k after the swap, and dividing by it is what makes the entry below cancel exactly when the row is subtracted.",
                            "Dividing an entry by itself gives 1 for every row, so each row below has the whole pivot row subtracted from it once, and nothing is eliminated except by accident.",
                            "The original matrix still holds its unmodified entries and the swap was applied to u rather than to a, so this divides by a number belonging to a different row than the pivot.",
                        ],
                    },
                    {
                        "prompt": "Each entry of the row has this much subtracted, scaled by the multiplier.",
                        "hole": "?",
                        "opts": ["u[i][j]", "u[k][j]", "u[j][k]", "l[k][j]"],
                        "a": 1,
                        "why": "The operation is row i minus the multiplier times the pivot row, so the value subtracted comes from row k in the same column j that is being updated.",
                        "whys": [
                            "Subtracting a multiple of the row from itself scales it towards zero and destroys the equation, rather than combining it with the pivot row.",
                            "The pivot row supplies the values, one column at a time, and the multiplier was chosen precisely so that the column-k entry cancels when this runs.",
                            "The indices are transposed, so this walks down a column of the matrix while j walks across a row, and the arithmetic mixes entries that belong to different equations.",
                            "L holds the multipliers already used rather than any part of the pivot row, and above the diagonal it is all zeros, so this subtracts nothing at all from most of the row.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Elimination that survives a small pivot",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Eight routines in `main.py`, over plain lists of lists of floats. Nothing may mutate
the matrix or the vector it is handed.

## Factorising and solving

- `lu_decompose(a, tol=1e-14)` — returns `(l, u, perm, sign)` with $PA = LU$. `l` is
  unit lower triangular, `u` upper triangular, `perm` a list of the original row
  indices in their new order, and `sign` is `1` or `-1` according to the number of
  interchanges. Raise `ValueError` for a matrix that is empty, ragged or not square,
  and when the best pivot in a column is `<= tol`.
- `lu_solve(l, u, perm, b)` — forward substitution through `l`, then back
  substitution through `u`. `ValueError` when `b` is the wrong length.
- `solve(a, b)` — the two together.
- `determinant(a)` — the product of `u`'s diagonal times `sign`; `0.0` for a singular
  matrix rather than an exception, since a determinant of zero is the answer.
- `inverse(a)` — solve against each column of the identity. One factorisation, `n`
  substitutions.

## Judging the answer

- `residual(a, x, b)` — the vector $b - Ax$.
- `norm_inf(v)` — the largest absolute entry of a vector; `ValueError` on an empty
  one.
- `condition_inf(a)` — $\|A\|_\infty \|A^{-1}\|_\infty$, where the matrix norm is the
  largest absolute row sum.

```text
solve([[1e-17, 1], [1, 1]], [1, 2])  ->  [1.0, 1.0]    (0.0 without pivoting)
determinant([[4, 3, 2], [1, 5, 7], [2, 2, 9]])  ->  123.0
condition_inf([[0.780, 0.563], [0.913, 0.659]])  ->  2661396.0
```
''',
                "files": [{"name": "main.py", "content": r'''
def lu_decompose(a, tol=1e-14):
    """PA = LU by elimination with partial pivoting. Returns (l, u, perm, sign)."""
    # your code here


def lu_solve(l, u, perm, b):
    """Forward substitution through l, then back substitution through u."""
    # your code here


def solve(a, b):
    """Factor and substitute."""
    # your code here


def determinant(a):
    """The product of the pivots, signed by the number of interchanges."""
    # your code here


def inverse(a):
    """Solve against each column of the identity."""
    # your code here


def residual(a, x, b):
    """The vector b - A x."""
    # your code here


def norm_inf(v):
    """The largest absolute entry of a vector."""
    # your code here


def condition_inf(a):
    """The infinity-norm condition number of a."""
    # your code here


print(solve([[1e-17, 1.0], [1.0, 1.0]], [1.0, 2.0]))
print(determinant([[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]]))
print(condition_inf([[0.780, 0.563], [0.913, 0.659]]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def _shape(a):
    """(rows, cols) after checking a is a non-empty rectangular matrix."""
    if not isinstance(a, (list, tuple)) or len(a) == 0:
        raise ValueError("a matrix needs at least one row")
    width = None
    for row in a:
        if not isinstance(row, (list, tuple)) or len(row) == 0:
            raise ValueError("every row must be a non-empty sequence")
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ValueError("the rows must all have the same length")
    return len(a), width


def lu_decompose(a, tol=1e-14):
    """PA = LU by elimination with partial pivoting. Returns (l, u, perm, sign)."""
    n, cols = _shape(a)
    if n != cols:
        raise ValueError("the matrix must be square")
    u = [[float(v) for v in row] for row in a]
    l = [[0.0] * n for _ in range(n)]
    perm = list(range(n))
    sign = 1
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(u[i][k]))
        if abs(u[p][k]) <= tol:
            raise ValueError("the matrix is singular to working precision")
        if p != k:
            u[k], u[p] = u[p], u[k]
            l[k], l[p] = l[p], l[k]
            perm[k], perm[p] = perm[p], perm[k]
            sign = -sign
        l[k][k] = 1.0
        for i in range(k + 1, n):
            factor = u[i][k] / u[k][k]
            l[i][k] = factor
            for j in range(k, n):
                u[i][j] -= factor * u[k][j]
    return l, u, perm, sign


def lu_solve(l, u, perm, b):
    """Forward substitution through l, then back substitution through u."""
    n = len(l)
    if len(b) != n:
        raise ValueError("the right-hand side is the wrong length")
    y = [0.0] * n
    for i in range(n):
        y[i] = float(b[perm[i]]) - sum(l[i][j] * y[j] for j in range(i))
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - sum(u[i][j] * x[j] for j in range(i + 1, n))) / u[i][i]
    return x


def solve(a, b):
    """Factor and substitute."""
    n, cols = _shape(a)
    if len(b) != n:
        raise ValueError("the right-hand side is the wrong length")
    l, u, perm, sign = lu_decompose(a)
    return lu_solve(l, u, perm, b)


def determinant(a):
    """The product of the pivots, signed by the number of interchanges."""
    n, cols = _shape(a)
    if n != cols:
        raise ValueError("the matrix must be square")
    try:
        l, u, perm, sign = lu_decompose(a)
    except ValueError:
        return 0.0
    total = float(sign)
    for i in range(n):
        total *= u[i][i]
    return total


def inverse(a):
    """Solve against each column of the identity."""
    n, cols = _shape(a)
    if n != cols:
        raise ValueError("the matrix must be square")
    l, u, perm, sign = lu_decompose(a)
    columns = []
    for j in range(n):
        e = [1.0 if i == j else 0.0 for i in range(n)]
        columns.append(lu_solve(l, u, perm, e))
    return [[columns[j][i] for j in range(n)] for i in range(n)]


def residual(a, x, b):
    """The vector b - A x."""
    n, cols = _shape(a)
    if len(x) != cols or len(b) != n:
        raise ValueError("the shapes do not agree")
    out = []
    for i in range(n):
        total = 0.0
        for j in range(cols):
            total += a[i][j] * x[j]
        out.append(float(b[i]) - total)
    return out


def norm_inf(v):
    """The largest absolute entry of a vector."""
    if len(v) == 0:
        raise ValueError("an empty vector has no norm")
    return max(abs(float(t)) for t in v)


def condition_inf(a):
    """The infinity-norm condition number of a."""
    rows = lambda m: max(sum(abs(t) for t in row) for row in m)
    return rows(a) * rows(inverse(a))


print(solve([[1e-17, 1.0], [1.0, 1.0]], [1.0, 2.0]))
print(determinant([[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]]))
print(condition_inf([[0.780, 0.563], [0.913, 0.659]]))
'''}],
                "hints": [
                    "Write the shape check once and call it from everywhere. Every routine here has the same three ways of being handed rubbish, and one place to refuse it is the difference between a library and a pile of functions.",
                    "`max(range(k, n), key=lambda i: abs(u[i][k]))` is the pivot search in one line. The range starts at `k`, not at 0: rows above have already been used and swapping one down would undo its elimination.",
                    "`lu_solve` reads the right-hand side through the permutation — `b[perm[i]]` — rather than permuting a copy of `b`. That is what keeps the routine from mutating the vector it was given.",
                    "`determinant` should return 0.0 rather than raising when `lu_decompose` refuses the matrix: a singular matrix has a determinant, and it is zero.",
                ],
                "tests": [
                    {"name": "PA = LU, with the swaps recorded", "code": r'''
_a = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 10.0]]
_l, _u, _perm, _sign = lu_decompose(_a)
assert sorted(_perm) == [0, 1, 2], f"perm must be a permutation of the rows; got {_perm!r}"
for _i in range(3):
    assert _l[_i][_i] == 1.0, f"l must be unit lower triangular; l[{_i}][{_i}] is {_l[_i][_i]!r}"
    for _j in range(_i + 1, 3):
        assert _l[_i][_j] == 0.0, f"l[{_i}][{_j}] should be 0.0, got {_l[_i][_j]!r}"
        assert abs(_u[_j][_i]) < 1e-15, f"u[{_j}][{_i}] should be 0.0, got {_u[_j][_i]!r}"
    for _j in range(_i):
        assert abs(_l[_i][_j]) <= 1.0 + 1e-12, \
            f"partial pivoting bounds every multiplier by 1; l[{_i}][{_j}] is {_l[_i][_j]!r}"
for _i in range(3):
    for _j in range(3):
        _lu = sum(_l[_i][_k] * _u[_k][_j] for _k in range(3))
        assert abs(_lu - _a[_perm[_i]][_j]) < 1e-9, \
            f"(LU)[{_i}][{_j}] is {_lu!r}, expected {_a[_perm[_i]][_j]!r}"
assert _sign in (1, -1), f"sign must be 1 or -1, got {_sign!r}"
'''},
                    {"name": "Solving a system, without disturbing it", "code": r'''
_a = [[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]]
_b = [1.0, 2.0, 3.0]
_before = [row[:] for row in _a]
_x = solve(_a, _b)
assert _a == _before, "solve must not mutate the matrix it is given"
assert _b == [1.0, 2.0, 3.0], "solve must not mutate the right-hand side"
for _i, _want in enumerate([6.0 / 41.0, -3.0 / 41.0, 13.0 / 41.0]):
    assert abs(_x[_i] - _want) < 1e-12, f"x[{_i}] is {_x[_i]!r}, expected {_want!r}"
assert norm_inf(residual(_a, _x, _b)) < 1e-12, \
    f"the residual should be at round-off; it is {norm_inf(residual(_a, _x, _b))!r}"
_l, _u, _p, _s = lu_decompose(_a)
assert max(abs(_x[_i] - lu_solve(_l, _u, _p, _b)[_i]) for _i in range(3)) < 1e-15, \
    "solve and lu_solve on the same factors must agree"
'''},
                    {"name": "The system an unpivoted elimination gets wrong", "code": r'''
_x = solve([[1e-17, 1.0], [1.0, 1.0]], [1.0, 2.0])
assert abs(_x[0] - 1.0) < 1e-9 and abs(_x[1] - 1.0) < 1e-9, \
    f"solve returned {_x!r}, expected about [1.0, 1.0] — without a row swap this " \
    "comes out as [0.0, 1.0]"
_y = solve([[1.0, 1.0], [1e-17, 1.0]], [2.0, 1.0])
assert abs(_y[0] - 1.0) < 1e-9 and abs(_y[1] - 1.0) < 1e-9, \
    f"the same system with the rows already in order gave {_y!r}"
_z = solve([[0.0, 2.0, 1.0], [1.0, 1.0, 1.0], [3.0, 1.0, 4.0]], [3.0, 3.0, 8.0])
for _i in range(3):
    assert abs(_z[_i] - 1.0) < 1e-12, f"a zero in the top-left forces a swap; got {_z!r}"
'''},
                    {"name": "Determinants from the pivots", "code": r'''
assert abs(determinant([[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]]) - 123.0) < 1e-9, \
    f"got {determinant([[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]])!r}, expected 123.0"
assert abs(determinant([[1.0, 2.0], [3.0, 4.0]]) + 2.0) < 1e-12, \
    f"det [[1,2],[3,4]] is -2; got {determinant([[1.0, 2.0], [3.0, 4.0]])!r}"
assert abs(determinant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 10.0]]) + 3.0) < 1e-9, \
    "det of that 3x3 is -3"
_swapped = determinant([[3.0, 4.0], [1.0, 2.0]])
assert abs(_swapped - 2.0) < 1e-12, \
    f"exchanging two rows negates the determinant; got {_swapped!r}, expected 2.0"
assert determinant([[1.0, 2.0], [2.0, 4.0]]) == 0.0, \
    "a singular matrix has a determinant, and it is zero"
assert abs(determinant([[7.0]]) - 7.0) < 1e-12, "a 1x1 determinant is its only entry"
'''},
                    {"name": "Malformed input is refused", "code": r'''
for _bad in [[], [[]], [[1.0, 2.0], [3.0]], [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], "nope"]:
    try:
        lu_decompose(_bad)
        assert False, f"lu_decompose({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    lu_decompose([[1.0, 2.0], [2.0, 4.0]])
    assert False, "a singular matrix should raise ValueError"
except ValueError:
    pass
try:
    solve([[1.0, 2.0], [3.0, 4.0]], [1.0])
    assert False, "a right-hand side of the wrong length should raise ValueError"
except ValueError:
    pass
try:
    norm_inf([])
    assert False, "norm_inf([]) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The residual paradox, reproduced", "code": r'''
_a = [[0.780, 0.563], [0.913, 0.659]]
_b = [0.217, 0.254]
_near = residual(_a, [0.999, -1.001], _b)
_far = residual(_a, [0.341, -0.087], _b)
assert norm_inf(_far) < norm_inf(_near) / 100.0, \
    f"the far candidate has the smaller residual: {norm_inf(_far)!r} against {norm_inf(_near)!r}"
assert abs(norm_inf(_far) - 1e-06) < 1e-12, f"its residual is 1e-6; got {norm_inf(_far)!r}"
assert abs(norm_inf(_near) - 0.001572) < 1e-12, \
    f"the near candidate's residual is 0.001572; got {norm_inf(_near)!r}"
_true = solve(_a, _b)
assert abs(_true[0] - 1.0) < 1e-6 and abs(_true[1] + 1.0) < 1e-6, \
    f"the true solution is (1, -1); solve gave {_true!r}"
assert norm_inf(residual(_a, _true, _b)) < 1e-15, "the true solution's residual is at round-off"
'''},
                    {"name": "Inverses, one factorisation and n substitutions", "code": r'''
_a = [[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]]
_inv = inverse(_a)
for _i in range(3):
    for _j in range(3):
        _p = sum(_a[_i][_k] * _inv[_k][_j] for _k in range(3))
        _want = 1.0 if _i == _j else 0.0
        assert abs(_p - _want) < 1e-12, f"(A A^-1)[{_i}][{_j}] is {_p!r}, expected {_want}"
_i2 = inverse([[1.0, 0.0], [0.0, 1.0]])
assert abs(_i2[0][0] - 1.0) < 1e-15 and abs(_i2[0][1]) < 1e-15, \
    f"the identity is its own inverse; got {_i2!r}"
try:
    inverse([[1.0, 2.0], [2.0, 4.0]])
    assert False, "a singular matrix has no inverse and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Condition numbers, well and badly behaved", "code": r'''
assert abs(condition_inf([[1.0, 0.0], [0.0, 1.0]]) - 1.0) < 1e-12, \
    "the identity is perfectly conditioned"
assert abs(condition_inf([[1.0, 0.0], [0.0, 2.0]]) - 2.0) < 1e-12, \
    f"diag(1, 2) has condition 2; got {condition_inf([[1.0, 0.0], [0.0, 2.0]])!r}"
_c3 = condition_inf([[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]])
assert abs(_c3 - 6.869918699186992) / 6.869918699186992 < 1e-9, \
    f"that 3x3 is conditioned at 6.8699187; got {_c3!r}"
_bad = condition_inf([[0.780, 0.563], [0.913, 0.659]])
assert abs(_bad - 2661396.0) / 2661396.0 < 1e-6, \
    f"the near-parallel pair is conditioned at 2661396; got {_bad!r}"
assert _bad > 1e6 > _c3, "the ill-conditioned matrix must dwarf the well-conditioned one"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Quadrature: trapezoids, parabolas and adaptivity",
            "summary": "Approximate the curve by a shape you can integrate, then use the error's own law to improve it.",
            "concepts": [
                "The trapezoid rule is the area of the trapezium through the two endpoints, summed over panels",
                "Its error is proportional to h^2, so halving the step divides the error by four",
                "Simpson's rule fits a parabola through three points, giving weights 1, 4, 1 over h/3",
                "Simpson integrates cubics exactly, because its error term involves the fourth derivative",
                "Halving the step divides Simpson's error by sixteen, which a run can confirm",
                "Richardson extrapolation turns two estimates into a better one and an error estimate",
                "Romberg is Richardson applied repeatedly to the trapezoid rule; adaptive Simpson refines only where it must",
                "Both error laws assume bounded derivatives, and a square root at an endpoint breaks them",
            ],
            "read": [
                {
                    "title": "Fitting shapes under a curve",
                    "minutes": 14,
                    "body": r'''
Integrate $e^{x}$ from 0 to 1, and pretend for the moment that the answer
$e - 1 = 1.718281828459045$ is unknown. The only thing a program can do with $f$ is
evaluate it at points, so every method in this module is the same manoeuvre:
replace the curve between the sample points by a shape whose area is known, and add
those areas up.

The simplest such shape is the straight line through the two ends, which makes a
trapezium of width $h$ and parallel sides $f(a)$ and $f(b)$. Its area is the width
times the average of the sides, and that is the whole rule. Chop $[a,b]$ into $n$
panels of width $h = (b-a)/n$ and add:

$$T_n = h\left(\frac{f_0}{2} + f_1 + f_2 + \dots + f_{n-1} + \frac{f_n}{2}\right)$$

The interior points appear once at full weight because each is the right end of one
panel and the left end of the next.

```python
import math

def trapezoid(f, a, b, n):
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return total * h

exact = math.e - 1.0
previous = None
for n in (1, 2, 4, 8, 16):
    err = abs(trapezoid(math.exp, 0.0, 1.0, n) - exact)
    print(n, err, "ratio" if previous is None else previous / err)
    previous = err
```

The errors are $0.1409$, $0.0356$, $0.00894$, $0.00224$, $0.000559$, and the ratios
between consecutive rows are `3.951`, `3.988`, `3.997`, `3.999`. Halving the step
divides the error by four, so the error is proportional to $h^{2}$, and the run
settles onto that law from the second refinement onwards.

The four is not a coincidence to be observed and shrugged at. Over one panel the gap
between the curve and the chord is governed by the curvature, and integrating the
Taylor remainder gives $-h^{3}f''(\xi)/12$ per panel. There are $(b-a)/h$ panels, so
the total is

$$E_n = -\frac{(b-a)h^{2}}{12}f''(\xi)$$

For $e^{x}$ on $[0,1]$ that predicts an error of $-0.1432h^{2}$, which at $h = 1$ is
$-0.1432$ against the measured $-0.1409$, and at $h = 0.5$ is $-0.0358$ against
$-0.0356$.

## A parabola through three points

A chord uses two values. Use three — the two ends and the middle — and the shape that
fits them is a parabola, which can also be integrated in closed form. Put the three
points at $-h$, $0$ and $h$ and integrate the quadratic through them; the result is

$$\int_{-h}^{h} p(x)\,dx = \frac{h}{3}\left(f_{-1} + 4f_{0} + f_{1}\right)$$

The middle point carries four times the weight of the ends, and the composite rule
alternates 4 and 2 across the interior because every second point is the middle of
its own pair of panels. That alternation is why $n$ has to be even: the panels are
consumed two at a time.

```python
import math

def simpson(f, a, b, n):
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * f(a + i * h)
    return total * h / 3.0

exact = math.e - 1.0
previous = None
for n in (2, 4, 8, 16):
    err = abs(simpson(math.exp, 0.0, 1.0, n) - exact)
    print(n, err, "ratio" if previous is None else previous / err)
    previous = err
```

The errors run $5.79 \cdot 10^{-4}$, $3.70 \cdot 10^{-5}$, $2.33 \cdot 10^{-6}$,
$1.46 \cdot 10^{-7}$, and the ratios are `15.65`, `15.91`, `15.98`. Sixteen, so the
error goes like $h^{4}$: one extra evaluation per pair of panels has bought two extra
orders of convergence.

There is a bonus hiding in that exponent. Fitting a parabola should integrate
quadratics exactly and nothing more, and yet:

```python
def simpson(f, a, b, n):
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * f(a + i * h)
    return total * h / 3.0

print(simpson(lambda x: x**3, 0.0, 1.0, 2))
print(simpson(lambda x: x**3 - 2*x, -1.0, 2.0, 2))
```

`0.25` and `0.75`, both exact. The cubic term of the error integrates to zero by
symmetry about the midpoint, so the leading error involves $f^{(4)}$ and Simpson's
rule is exact for every cubic. That is the reason for the fourth-order behaviour and
it is worth knowing when choosing a rule: Simpson is not "a bit better than
trapezoid", it is two orders better.

## Two estimates are worth more than one

If the error goes like $h^{4}$, then halving the step should divide it by 16 —
which means the *difference* between the two estimates is measurable evidence about
the error of the finer one. Writing $I$ for the true value, $S_1$ for the coarse
estimate and $S_2$ for the fine one, $I - S_1 \approx 16(I - S_2)$, and rearranging:

$$I - S_2 \approx \frac{S_2 - S_1}{15}$$

The right-hand side costs nothing beyond estimates already computed, and it can be
used twice over: as an error bar, and as a correction.

```python
import math

def simpson(f, a, b, n):
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * f(a + i * h)
    return total * h / 3.0

s1 = simpson(math.exp, 0.0, 1.0, 2)
s2 = simpson(math.exp, 0.0, 1.0, 4)
print((s2 - s1) / 15)
print(abs(s2 - (math.e - 1.0)))
print(abs(s2 + (s2 - s1) / 15 - (math.e - 1.0)))
```

The estimated error is `-3.615e-05` and the true error of $S_2$ is `3.701e-05`, so
the estimate is right to two digits. Adding the correction gives an error of
`8.59e-07`, forty times better than $S_2$ and free. That is **Richardson
extrapolation**, and applying it repeatedly to the trapezoid rule is the Romberg
method: six levels, using 33 evaluations in total, integrates $e^{x}$ to
$6.7 \cdot 10^{-16}$, which is the last bit. The plain trapezoid rule needs about
$10^{5}$ evaluations to reach $1.4 \cdot 10^{-11}$.

The same difference, used as a local error bar rather than a global one, is adaptive
quadrature: estimate an interval, estimate its two halves, and if the difference is
too large, recurse into each half with half the tolerance. Points end up where the
function is difficult and nowhere else. On $1/(1+25x^{2})$ over $[-1,1]$ — a function
with a sharp peak at the origin and long flat tails — adaptive Simpson reaches an
error of $5 \cdot 10^{-14}$ in 625 evaluations, where the uniform rule needs about a
thousand for $1.4 \cdot 10^{-13}$.

## The mistake: more points must mean less error

Every table above rewards refinement, so the natural conclusion is that $n$ should be
as large as patience allows. Watch what the $h^{2}$ law does when it is pushed.

```python
import math

def trapezoid(f, a, b, n):
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return total * h

exact = math.e - 1.0
for n in (1000, 10000, 100000, 1000000):
    print(n, abs(trapezoid(math.exp, 0.0, 1.0, n) - exact))
```

The errors are $1.432 \cdot 10^{-7}$, $1.432 \cdot 10^{-9}$, $1.432 \cdot 10^{-11}$,
and then $8.6 \cdot 10^{-14}$ where the law predicts $1.432 \cdot 10^{-13}$. The last
row has left the line, because a sum of a million terms carries its own round-off of
about $nu\sum|f| \approx 10^{-10}$ in the worst case and something like $10^{-13}$
in practice. Below that level the discretisation error being chased is smaller than
the arithmetic error being added, and refining further moves the answer around
without improving it. The right response is not more points; it is a better rule, or
compensated summation of the terms — both of which cost far less than the factor of
ten in evaluations that bought nothing here.

## Where the error laws stop holding

Both error formulas contain a derivative of $f$ at an unknown interior point, and both
are worthless if that derivative is unbounded. Integrate $\sqrt{x}$ from 0 to 1, whose
answer is $2/3$:

```python
import math

def trapezoid(f, a, b, n):
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return total * h

previous = None
for n in (8, 16, 32, 64):
    err = abs(trapezoid(math.sqrt, 0.0, 1.0, n) - 2.0/3.0)
    print(n, err, "ratio" if previous is None else previous / err)
    previous = err
```

The ratios are `2.739`, `2.767`, `2.785`, `2.798` — not 4, and heading towards
$2^{1.5} = 2.828$. The error is falling like $h^{1.5}$ rather than $h^{2}$, because
$f''(x) = -\tfrac{1}{4}x^{-3/2}$ blows up at the left endpoint. Nothing warns you:
the numbers keep improving, at a rate that only a ratio column reveals as wrong.
Simpson does no better on the same function, since its error term needs four bounded
derivatives where the trapezoid rule needed two. The cures are a substitution that
removes the singularity, a rule with points clustered at the ends, or splitting the
integral at the awkward point — and choosing between them requires knowing the
singularity is there, which is why the ratio column belongs in your toolbox.

## What the lab asks

**Quadrature that refines where it needs to** has you write `trapezoid` and
`simpson` as composite rules with their validation, `romberg` building the
extrapolation table, `adaptive_simpson` recursing on the difference test above, and
`halving_ratio`, which measures the observed order of a rule by comparing the errors
at $n$ and $2n$. The checks require the ratio to come out at 4 for the trapezoid rule
and 16 for Simpson on a smooth integrand — and at about 2.8 for $\sqrt{x}$, so that
the failure is pinned down as firmly as the success.
''',
                },
            ],
            "quiz": {
                "title": "Which rule, how many points, and when to stop",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Doubling the panel count on a smooth integrand divides the trapezoid error by four. Where does the four come from?",
                        "opts": [
                            "From averaging the two endpoints, which halves the error twice over per panel",
                            "From the panel count doubling while each panel's own error halves alongside it",
                            "From the per-panel error going like $h^3$, with one power spent on the panel count",
                            "From the rule being exact for linear functions, which removes the first two Taylor terms",
                        ],
                        "a": 2,
                        "whys": [
                            "Averaging the endpoints is what the rule computes and it says nothing about the rate. A rule that averaged three points the same way would still have to be analysed by its Taylor remainder.",
                            "This gets a factor of 2 from each of two places and the second one is wrong: an individual panel's error falls by $2^3$ when its width halves, not by 2. The arithmetic then lands on 4 by accident.",
                            "One panel contributes $-h^3f''/12$, and there are $(b-a)/h$ panels, so the total carries $h^2$: halve $h$ and the error falls by 4.",
                            "Exactness for linear functions is why the leading term involves $f''$ at all, but it fixes which derivative appears rather than which power of $h$ survives the summation.",
                        ],
                        "why": r"""
Over one panel the trapezium misses by $-h^{3}f''(\xi)/12$, and there are $(b-a)/h$
panels to add up, so one factor of $h$ is consumed by the panel count and the total
error is proportional to $h^{2}$. That is the general shape of every composite rule's
analysis: work out the error on one panel, then multiply by how many panels there
are. Simpson's per-pair error is $h^{5}$, the pair count is $(b-a)/2h$, and $h^{4}$
survives — which is the sixteen the run confirms.
""",
                    },
                    {
                        "q": "Simpson's rule fits a parabola through three points, yet it integrates $x^3$ exactly. Why?",
                        "opts": [
                            "The cubic term is antisymmetric about the midpoint, so its contribution integrates away",
                            "Any cubic can be written as a parabola plus a linear function, both of which the rule handles",
                            "The weights 1, 4, 1 come from fitting a cubic rather than a parabola",
                            "It is exact only for $x^3$ specifically, because that cubic happens to vanish at the midpoint",
                        ],
                        "a": 0,
                        "whys": [
                            "Write the interval symmetrically about its midpoint and the cubic part of the error is an odd function, whose integral over a symmetric interval is zero — so the error term jumps straight to $f^{(4)}$.",
                            "That decomposition is false: $x^3$ is not a parabola plus a line, which is exactly why its exact integration is surprising and worth an explanation.",
                            "The weights come from integrating the quadratic through the three points, and one can check that directly. The cubic exactness is a consequence rather than a design goal.",
                            "It is exact for every cubic, shifted or not — the reading's second example is $x^3 - 2x$ over $[-1, 2]$, which is neither centred nor vanishing at the midpoint, and it comes out at 0.75 exactly.",
                        ],
                        "why": r"""
Set the three points at $-h$, $0$, $h$ and expand $f$ about the middle. The rule is
exact for $1$, $x$ and $x^{2}$ by construction, and the $x^{3}$ term is odd about the
midpoint, so both the true integral and the rule's estimate of it are zero. The
leading error therefore starts at the quartic term, giving $h^5 f^{(4)}/90$ per pair
and an $h^{4}$ composite law. This is why every rule is quoted by its *degree of
exactness*: Simpson is exact to degree 3 on 3 points, which is one better than the
counting argument suggests.
""",
                    },
                    {
                        "q": "Two Simpson estimates give $S_1$ on $n$ panels and $S_2$ on $2n$. What is $(S_2 - S_1)/15$?",
                        "opts": [
                            "The difference between the two rules, scaled so it can be compared against a tolerance",
                            "An estimate of the error remaining in $S_2$, which can also be added to $S_2$ as a correction",
                            "The error of $S_1$, which the finer estimate is being used to measure after the fact",
                            "A rigorous bound on the error of $S_2$, valid whatever the integrand does between the sample points",
                        ],
                        "a": 1,
                        "whys": [
                            "Scaling by 15 is not cosmetic: the number comes from $16 - 1$ in the $h^4$ law, and what it produces is a quantity on the scale of the remaining error rather than of the difference.",
                            "From $I - S_1 \\approx 16(I - S_2)$ it follows that $I - S_2 \\approx (S_2 - S_1)/15$, which for the reading's numbers gives $-3.6 \\cdot 10^{-5}$ against a true error of $3.7 \\cdot 10^{-5}$.",
                            "The error of $S_1$ is about sixteen times larger, so this quantity is roughly $S_1$'s error divided by 16. Using it as $S_1$'s error would overstate the accuracy by that factor.",
                            "It is an estimate rather than a bound, and it rests on the $h^4$ law holding across the interval. On $\\sqrt{x}$ near zero the law does not hold and the estimate is wrong along with it.",
                        ],
                        "why": r"""
The $h^{4}$ law says the coarse error is about sixteen times the fine one, so
$I - S_1 \approx 16(I - S_2)$. Subtracting gives $S_2 - S_1 \approx 15(I - S_2)$, and
dividing by 15 turns two numbers already computed into an estimate of what is still
wrong. It is used both ways in this course: as the stopping test inside
`adaptive_simpson`, and as a correction added straight onto $S_2$, which is
Richardson extrapolation and is the engine of the Romberg table.
""",
                    },
                    {
                        "q": "The trapezoid error on $e^x$ falls as $h^2$ until $n = 10^6$, where it stops following the law. What has happened?",
                        "opts": [
                            "The panels are narrower than the spacing of the doubles, so the sample points repeat",
                            "The evaluations of `exp` have become the dominant error, since each carries a half-ulp",
                            "The accumulated round-off of summing a million terms is now the size of the error being chased",
                            "The step $h$ is no longer representable, so the panels are unequal and the rule is no longer valid",
                        ],
                        "a": 2,
                        "whys": [
                            "At $n = 10^6$ the panels are $10^{-6}$ wide and the spacing of doubles near 1 is $10^{-16}$, so there are ten orders of magnitude to spare. Sample points repeating is a real failure mode, at $n$ near $10^{16}$.",
                            "Each evaluation is correctly rounded to a relative $10^{-16}$ and those errors are averaged by the sum rather than accumulated, so they contribute around $10^{-16}$ — a thousand times below what is observed.",
                            "A million additions each round by up to $u$ times the running total, and that noise is around $10^{-13}$ — the same size as the discretisation error the refinement was chasing.",
                            "The step is $10^{-6}$, which is a perfectly ordinary double, and unequal panels are not the issue: the same rule with the same spacing works at $n = 10^5$ exactly as the law predicts.",
                        ],
                        "why": r"""
There are two errors in play and they move in opposite directions as $n$ grows. The
discretisation error falls like $h^{2}$; the round-off of the sum grows with the
number of terms, at up to $nu\sum|f|$. They cross, and past the crossing more points
buy nothing — at $n = 10^{6}$ the measured error is $8.6 \cdot 10^{-14}$ where the law
predicts $1.4 \cdot 10^{-13}$, so it is already off the line. The response is a better
rule rather than more points: Romberg reaches the last bit on 33 evaluations, which
never gives the round-off a chance to accumulate.
""",
                    },
                    {
                        "q": "On $\\sqrt{x}$ over $[0, 1]$ the trapezoid error ratios come out at 2.74, 2.77, 2.80 rather than 4. What does that indicate?",
                        "opts": [
                            "A bug in the rule, since a correct implementation gives 4 on any integrand",
                            "The integral is divergent at the origin, so no fixed-step rule can converge to it at all",
                            "The error law needs a bounded $f''$, and here it is unbounded at the left endpoint",
                            "Round-off has taken over early, because $\\sqrt{x}$ loses precision for small arguments",
                        ],
                        "a": 2,
                        "whys": [
                            "The same code gives 4.00 on $e^x$ and exactly 4 on $x^2$, so it is doing its arithmetic correctly. What changed is the integrand, and specifically its second derivative.",
                            "The integral is perfectly finite at $2/3$, and the rule does converge — at $h^{1.5}$ rather than $h^{2}$. Divergence and slow convergence are different diagnoses with different cures.",
                            "$f'' = -x^{-3/2}/4$ is unbounded as $x \\to 0$, so the remainder term the $h^2$ law rests on does not exist and the observed rate settles at $2^{1.5} = 2.83$.",
                            "`math.sqrt` is correctly rounded everywhere, including near zero, and the errors here are around $10^{-4}$ — twelve orders above anything round-off is doing.",
                        ],
                        "why": r"""
The $h^{2}$ law comes from a Taylor remainder containing $f''(\xi)$, and at the origin
$f''$ is infinite for the square root, so the derivation has nothing to stand on. The
observed rate settles at $2^{1.5} = 2.828$, which is the true convergence rate for
this singularity. What makes it dangerous is that the numbers still improve on every
refinement: only the ratio column shows that they improve at the wrong rate. A ratio
column costs one extra run of the rule and turns a silent loss of accuracy into a
visible one.
""",
                    },
                    {
                        "q": "Adaptive Simpson reaches $5 \\cdot 10^{-14}$ on $1/(1+25x^2)$ in 625 evaluations. Where did it put them?",
                        "opts": [
                            "Spread evenly, but each one is reused several times by the recursion's error estimates",
                            "Concentrated near the peak, where the halved estimates disagreed and the recursion continued",
                            "Concentrated at the endpoints, where a rule of this kind is always at its least accurate",
                            "Chosen at the roots of an orthogonal polynomial, which is what makes the rule better than a uniform one",
                        ],
                        "a": 1,
                        "whys": [
                            "Reuse is real and worth implementing — the endpoints and midpoint of a parent are the points of its children — but it saves a constant factor rather than deciding where the points go.",
                            "The test is whether the two half-interval estimates agree with the whole-interval one, and disagreement means curvature, so the recursion drives itself into the peak and leaves the flat tails alone.",
                            "Endpoints are where a rule struggles when the integrand is singular there, which this one is not: it is smooth on the whole interval and merely has all its curvature in the middle.",
                            "Choosing points at the roots of an orthogonal polynomial is Gaussian quadrature, a different method with fixed points, and adaptivity is precisely the alternative to fixing them in advance.",
                        ],
                        "why": r"""
The recursion asks one local question — do the two halves agree with the whole to
within the tolerance — and that question is a curvature detector. Where $f$ is nearly
a parabola the answer is yes and the interval is accepted with three points. Where the
peak is, the answer is no and both halves are subdivided again. The result is a mesh
that is fine near the origin and coarse on the tails, which is what buys the accuracy
per evaluation over a uniform rule. It also explains the failure mode: a spike thin
enough to fall between the first few sample points is never detected, and the routine
returns a confident wrong answer.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Weights and the extrapolation, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "quad.py — five holes; the weights decide whether the rule is second order or fourth",
                "brief": r"""
Two composite rules and the correction that turns a pair of estimates into a better
one. Nothing runs here. Filled in correctly, the trapezoid rule on a straight line is
exact for every panel count, and `refine` improves a Simpson estimate by a factor of
forty at no cost in evaluations.
""",
                "listing": r'''
def trapezoid(f, a, b, n):
    """The composite trapezoid rule over n panels."""
    h = (b - a) / n
    total = ___ * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + ___)
    return total * h


def simpson(f, a, b, n):
    """The composite Simpson rule; n must be even."""
    if n < 2 or n % 2:
        raise ValueError("n must be even and at least 2")
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (___ if i % 2 else 2.0) * f(a + i * h)
    return total * h / ___


def refine(coarse, fine):
    """Richardson: the finer Simpson estimate, corrected by its own error estimate."""
    return fine + (fine - coarse) / ___
''',
                "blanks": [
                    {
                        "prompt": "The two endpoints carry this share of an interior point's weight.",
                        "hole": "?",
                        "opts": ["0.5", "1.0", "h", "2.0"],
                        "a": 0,
                        "why": "An interior point is the right end of one panel and the left end of the next, so it is counted twice at half weight; the two outer points belong to one panel each and keep a single half.",
                        "whys": [
                            "Every panel contributes half of each of its two ends, and only the outer points fail to be shared, which is what leaves them at half while the interior points reach a full 1.",
                            "Giving the ends full weight adds an extra half of each to the total, so the answer is too large by h times the average of the endpoint values — visible immediately on any straight line.",
                            "The step is already applied to the whole sum on the last line, so using it here multiplies the endpoint terms by h twice and the result scales wrongly with the panel count.",
                            "This doubles the endpoints instead of halving them, so a rule that should be exact for straight lines overestimates every integral by one and a half panels' worth of the ends.",
                        ],
                    },
                    {
                        "prompt": "The offset of the i-th interior sample point from a.",
                        "hole": "?",
                        "opts": ["i * h", "h", "i / h", "i * n"],
                        "a": 0,
                        "why": "The points are equally spaced h apart starting at a, so the i-th of them sits at a plus i steps of h — the expression that makes the loop walk across the interval exactly once.",
                        "whys": [
                            "Multiplying the index by the step is what advances the sample point, so the loop visits every interior node once and finishes one step short of b.",
                            "Without the index every iteration evaluates at the same point a + h, so the sum is n - 1 copies of one value and the answer is unrelated to the function elsewhere.",
                            "Dividing by a step of 0.001 sends the sample points to a + 1000i, thousands of intervals away, and the rule reports the behaviour of f far outside the region asked about.",
                            "The panel count is not a distance. This walks in strides of n, so for any n above 1 the loop leaves the interval on its first iteration and the samples have nothing to do with the integral.",
                        ],
                    },
                    {
                        "prompt": "The weight on an odd-indexed interior point.",
                        "hole": "?",
                        "opts": ["1.0", "4.0", "3.0", "2.0"],
                        "a": 1,
                        "why": "Odd-indexed points are the midpoints of the parabola-fitting triples, and integrating the quadratic through three equally spaced points gives the middle one four times the weight of the ends.",
                        "whys": [
                            "Equal weights on every point make this the rectangle-ish sum rather than Simpson's rule; the estimate is then second order at best and the halving ratio comes out near 4 instead of 16.",
                            "Integrating the interpolating parabola over the pair of panels produces the pattern 1, 4, 1 over h/3, and the 4 is what makes the rule exact for cubics.",
                            "Weights of 3 and 2 sum to the wrong total: the coefficients over each pair of panels must add to 6 for the h/3 out front to reproduce the width of the pair, and 1 + 3 + 1 gives 5.",
                            "Using the same weight as the even points turns the alternation into a constant, and the rule collapses into two-thirds of the trapezoid rule — wrong by a third on every integral.",
                        ],
                    },
                    {
                        "prompt": "The whole Simpson sum is divided by this.",
                        "hole": "?",
                        "opts": ["6.0", "3.0", "2.0", "n"],
                        "a": 1,
                        "why": "The weights over one pair of panels add to 6 while the pair is 2h wide, so the sum has to be scaled by h/3 for a constant function to integrate to its own value times the width.",
                        "whys": [
                            "This halves every answer. The check is a constant function: with weights summing to 6 over a width of 2h, dividing by 6 gives the width as h rather than 2h.",
                            "Take f identically 1 over one pair of panels: the weighted sum is 6, the width is 2h, and h/3 is the only scaling that returns 2h.",
                            "This is the trapezoid rule's scaling applied to Simpson's weights, and it overstates every integral by half, so even a constant function comes out fifty per cent too large.",
                            "The panel count is already inside h, which is the interval divided by n, so dividing again shrinks the answer by a further factor of n and the estimate falls to zero as the rule is refined.",
                        ],
                    },
                    {
                        "prompt": "The Richardson correction divides the difference by this.",
                        "hole": "?",
                        "opts": ["3.0", "15.0", "4.0", "16.0"],
                        "a": 1,
                        "why": "Simpson's error falls by 16 per halving, so the coarse error is about sixteen times the fine one and their difference is about fifteen times the fine error — which is what has to be divided out.",
                        "whys": [
                            "Three is the divisor for a second-order rule, where the errors differ by a factor of 4 and their difference is 3 times the finer error. Used here it overcorrects by a factor of five.",
                            "From $I - S_1 = 16(I - S_2)$ the difference $S_2 - S_1$ is $15(I - S_2)$, so dividing by 15 recovers the remaining error and adding it lands far closer to $I$.",
                            "Four is the ratio of the errors for the trapezoid rule rather than a difference for Simpson, and it belongs to neither role here: it neither matches the 16 nor the 15 derived from it.",
                            "Sixteen is the ratio between the two errors, not the ratio between their difference and the finer one. Using it undercorrects by one part in fifteen, which leaves seven per cent of the error behind.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Quadrature that refines where it needs to",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Five routines in `main.py`. Every one of them takes the integrand as a callable and
must work for any callable, so nothing may be hard-coded about $f$.

## The fixed rules

- `trapezoid(f, a, b, n)` — the composite trapezoid rule over `n` equal panels.
  `ValueError` when `n < 1` or `b <= a`.
- `simpson(f, a, b, n)` — the composite Simpson rule. `ValueError` when `n < 2`, when
  `n` is odd, or when `b <= a`.
- `romberg(f, a, b, levels)` — the extrapolation table. Row `k` starts with the
  trapezoid rule on $2^{k}$ panels, and entry `j` of that row is
  `r[k][j-1] + (r[k][j-1] - r[k-1][j-1]) / (4**j - 1)`. Return the last entry of the
  last row. `ValueError` when `levels < 1` or `b <= a`.

## Refining where it matters

- `adaptive_simpson(f, a, b, tol=1e-10, max_depth=50)` — estimate the whole interval
  with the three-point rule, estimate each half, and accept
  `left + right + (left + right - whole) / 15` when
  `abs(left + right - whole) <= 15 * tol`; otherwise recurse into each half with half
  the tolerance and one less depth. Pass the function values you already have into
  the recursion rather than recomputing them: on the peaked integrand in the checks
  that is the difference between about six hundred evaluations and several thousand.
  `ValueError` when `tol <= 0` or `b <= a`.
- `halving_ratio(rule, f, a, b, exact, n)` — the observed order of a rule, as
  `abs(rule(f, a, b, n) - exact) / abs(rule(f, a, b, 2 * n) - exact)`. `ValueError`
  when the finer estimate is exact, since the ratio is then undefined.

```text
trapezoid(exp, 0, 1, 1)                      ->  1.8591409142295225
simpson(lambda x: x**3, 0, 1, 2)             ->  0.25            (exact)
romberg(exp, 0, 1, 6)                        ->  e - 1 to the last bit
halving_ratio(trapezoid, exp, 0, 1, e-1, 8)  ->  3.999
halving_ratio(simpson,   exp, 0, 1, e-1, 8)  ->  15.98
halving_ratio(trapezoid, sqrt, 0, 1, 2/3, 32) -> 2.798   (not 4)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def trapezoid(f, a, b, n):
    """The composite trapezoid rule over n equal panels."""
    # your code here


def simpson(f, a, b, n):
    """The composite Simpson rule; n must be even."""
    # your code here


def romberg(f, a, b, levels):
    """Repeated Richardson extrapolation of the trapezoid rule."""
    # your code here


def adaptive_simpson(f, a, b, tol=1e-10, max_depth=50):
    """Subdivide only where the halved estimates disagree."""
    # your code here


def halving_ratio(rule, f, a, b, exact, n):
    """The factor by which doubling the panel count reduces the error."""
    # your code here


print("trapezoid:", trapezoid(math.exp, 0.0, 1.0, 8))
print("simpson:  ", simpson(math.exp, 0.0, 1.0, 8))
print("romberg:  ", romberg(math.exp, 0.0, 1.0, 6))
print("adaptive: ", adaptive_simpson(math.exp, 0.0, 1.0))
print("ratio:    ", halving_ratio(trapezoid, math.exp, 0.0, 1.0, math.e - 1.0, 8))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def trapezoid(f, a, b, n):
    """The composite trapezoid rule over n equal panels."""
    if n < 1:
        raise ValueError("n must be at least 1")
    if b <= a:
        raise ValueError("b must be above a")
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return total * h


def simpson(f, a, b, n):
    """The composite Simpson rule; n must be even."""
    if n < 2 or n % 2:
        raise ValueError("n must be even and at least 2")
    if b <= a:
        raise ValueError("b must be above a")
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * f(a + i * h)
    return total * h / 3.0


def romberg(f, a, b, levels):
    """Repeated Richardson extrapolation of the trapezoid rule."""
    if levels < 1:
        raise ValueError("levels must be at least 1")
    if b <= a:
        raise ValueError("b must be above a")
    rows = []
    for k in range(levels):
        row = [trapezoid(f, a, b, 2 ** k)]
        for j in range(1, k + 1):
            row.append(row[j - 1] + (row[j - 1] - rows[k - 1][j - 1]) / (4 ** j - 1))
        rows.append(row)
    return rows[-1][-1]


def adaptive_simpson(f, a, b, tol=1e-10, max_depth=50):
    """Subdivide only where the halved estimates disagree."""
    if tol <= 0:
        raise ValueError("the tolerance must be positive")
    if b <= a:
        raise ValueError("b must be above a")

    def panel(fa, fm, fb, lo, hi):
        return (hi - lo) * (fa + 4.0 * fm + fb) / 6.0

    def step(lo, hi, fa, fm, fb, whole, tol, depth):
        mid = 0.5 * (lo + hi)
        lmid = 0.5 * (lo + mid)
        rmid = 0.5 * (mid + hi)
        flm = f(lmid)
        frm = f(rmid)
        left = panel(fa, flm, fm, lo, mid)
        right = panel(fm, frm, fb, mid, hi)
        if depth <= 0 or abs(left + right - whole) <= 15.0 * tol:
            return left + right + (left + right - whole) / 15.0
        return (step(lo, mid, fa, flm, fm, left, tol / 2, depth - 1) +
                step(mid, hi, fm, frm, fb, right, tol / 2, depth - 1))

    fa = f(a)
    fb = f(b)
    mid = 0.5 * (a + b)
    fm = f(mid)
    return step(a, b, fa, fm, fb, panel(fa, fm, fb, a, b), tol, max_depth)


def halving_ratio(rule, f, a, b, exact, n):
    """The factor by which doubling the panel count reduces the error."""
    coarse = abs(rule(f, a, b, n) - exact)
    fine = abs(rule(f, a, b, 2 * n) - exact)
    if fine == 0.0:
        raise ValueError("the finer estimate is exact, so the ratio is undefined")
    return coarse / fine


print("trapezoid:", trapezoid(math.exp, 0.0, 1.0, 8))
print("simpson:  ", simpson(math.exp, 0.0, 1.0, 8))
print("romberg:  ", romberg(math.exp, 0.0, 1.0, 6))
print("adaptive: ", adaptive_simpson(math.exp, 0.0, 1.0))
print("ratio:    ", halving_ratio(trapezoid, math.exp, 0.0, 1.0, math.e - 1.0, 8))
'''}],
                "hints": [
                    "Both fixed rules have the same shape: seed the total with the endpoint terms, loop over the interior indices adding the weighted values, and scale once at the end. Scaling inside the loop is where the round-off comes from.",
                    "In `romberg`, build the table row by row and keep the previous row to hand. Entry `j` of row `k` needs entry `j-1` of the row above it, which is why the whole triangle is stored rather than a single running value.",
                    "`adaptive_simpson` wants an inner function taking the interval, the three function values already computed, the whole-interval estimate and the remaining depth. Passing those values down is what stops the evaluation count exploding.",
                    "The tolerance halves on the way down because the two halves both contribute to the total error; if each is allowed the full tolerance, the sum can be off by twice what was asked for.",
                ],
                "tests": [
                    {"name": "The trapezoid rule, and what it is exact for", "code": r'''
for _n in (1, 2, 7, 20):
    _got = trapezoid(lambda x: 3.0 * x + 1.0, 0.0, 2.0, _n)
    assert abs(_got - 8.0) < 1e-12, f"a straight line is exact for any n; n={_n} gave {_got!r}"
assert abs(trapezoid(math.exp, 0.0, 1.0, 1) - 1.8591409142295225) < 1e-12, \
    f"one panel on exp gives 1.8591409142295225; got {trapezoid(math.exp, 0.0, 1.0, 1)!r}"
assert abs(trapezoid(math.exp, 0.0, 1.0, 8) - 1.7205185921643018) < 1e-12, \
    f"eight panels gave {trapezoid(math.exp, 0.0, 1.0, 8)!r}"
for _args in [(0, 1, 0), (0, 1, -2), (1, 1, 4), (2, 1, 4)]:
    try:
        trapezoid(math.exp, float(_args[0]), float(_args[1]), _args[2])
        assert False, f"trapezoid with (a, b, n) = {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Halving the step divides the trapezoid error by four", "code": r'''
_r = halving_ratio(trapezoid, lambda x: x * x, 0.0, 1.0, 1.0 / 3.0, 4)
assert abs(_r - 4.0) < 1e-6, f"on a quadratic the ratio is exactly 4; got {_r!r}"
_re = halving_ratio(trapezoid, math.exp, 0.0, 1.0, math.e - 1.0, 8)
assert 3.9 < _re < 4.05, f"on exp the ratio should be about 4; got {_re!r}"
try:
    halving_ratio(trapezoid, lambda x: 2.0 * x, 0.0, 1.0, 1.0, 4)
    assert False, "an exact finer estimate leaves the ratio undefined and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Simpson is exact for every cubic", "code": r'''
assert abs(simpson(lambda x: x**3, 0.0, 1.0, 2) - 0.25) < 1e-15, \
    f"simpson of x^3 over [0,1] is 0.25; got {simpson(lambda x: x**3, 0.0, 1.0, 2)!r}"
assert abs(simpson(lambda x: x**3 - 2.0 * x, -1.0, 2.0, 2) - 0.75) < 1e-14, \
    f"got {simpson(lambda x: x**3 - 2.0*x, -1.0, 2.0, 2)!r}, expected 0.75"
assert abs(simpson(lambda x: 5.0, 0.0, 3.0, 6) - 15.0) < 1e-12, "a constant integrates to its area"
assert abs(simpson(math.exp, 0.0, 1.0, 2) - 1.7188611518765928) < 1e-12, \
    f"two panels on exp gave {simpson(math.exp, 0.0, 1.0, 2)!r}"
for _n in (0, 1, 3, -2):
    try:
        simpson(math.exp, 0.0, 1.0, _n)
        assert False, f"simpson with n = {_n} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Halving the step divides Simpson's error by sixteen", "code": r'''
_r = halving_ratio(simpson, math.exp, 0.0, 1.0, math.e - 1.0, 8)
assert 15.5 < _r < 16.5, f"Simpson's ratio should be about 16; got {_r!r}"
_r4 = halving_ratio(simpson, math.exp, 0.0, 1.0, math.e - 1.0, 4)
assert 15.0 < _r4 < 16.5, f"at n = 4 the ratio is 15.91; got {_r4!r}"
_rt = halving_ratio(trapezoid, math.exp, 0.0, 1.0, math.e - 1.0, 8)
assert _r > 3 * _rt, "Simpson must converge two orders faster than the trapezoid rule"
'''},
                    {"name": "Romberg reaches the last bit on very few points", "code": r'''
_got = romberg(math.exp, 0.0, 1.0, 6)
assert abs(_got - (math.e - 1.0)) < 1e-14, \
    f"six levels on exp should reach the last bit; got {_got!r}, off by " \
    f"{abs(_got - (math.e - 1.0))!r}"
assert abs(romberg(math.sin, 0.0, math.pi, 8) - 2.0) < 1e-12, \
    f"the integral of sin over [0, pi] is 2; got {romberg(math.sin, 0.0, math.pi, 8)!r}"
assert abs(romberg(lambda x: 3.0 * x + 1.0, 0.0, 2.0, 1) - 8.0) < 1e-12, \
    "one level is the trapezoid rule on a single panel, which is exact for a line"
assert abs(romberg(math.exp, 0.0, 1.0, 3) - 1.7182826879247575) < 1e-12, \
    f"three levels gave {romberg(math.exp, 0.0, 1.0, 3)!r}"
for _args in [(0.0, 1.0, 0), (0.0, 1.0, -1), (1.0, 1.0, 4)]:
    try:
        romberg(math.exp, _args[0], _args[1], _args[2])
        assert False, f"romberg with {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Adaptive Simpson on a peaked integrand", "code": r'''
_exact = 0.4 * math.atan(5.0)
_calls = [0]
def _runge(x):
    _calls[0] += 1
    return 1.0 / (1.0 + 25.0 * x * x)
_got = adaptive_simpson(_runge, -1.0, 1.0, 1e-9)
assert abs(_got - _exact) < 1e-9, f"adaptive_simpson gave {_got!r}, expected {_exact!r}"
assert _calls[0] < 3000, \
    f"that took {_calls[0]} evaluations; pass the values you already have into the " \
    "recursion instead of recomputing them"
assert abs(adaptive_simpson(math.exp, 0.0, 1.0, 1e-12) - (math.e - 1.0)) < 1e-12, \
    "exp over [0, 1] should come out to the tolerance asked for"
assert abs(adaptive_simpson(math.sin, 0.0, math.pi, 1e-12) - 2.0) < 1e-11, \
    f"sin over [0, pi] gave {adaptive_simpson(math.sin, 0.0, math.pi, 1e-12)!r}"
for _args in [(0.0, 1.0, 0.0), (0.0, 1.0, -1e-6), (1.0, 1.0, 1e-6)]:
    try:
        adaptive_simpson(math.exp, _args[0], _args[1], _args[2])
        assert False, f"adaptive_simpson with {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Where adaptivity earns its keep", "code": r'''
_exact = 200.0 * math.atan(100.0)
_calls = [0]
def _spike(x):
    _calls[0] += 1
    return 1.0 / (1e-4 + x * x)
_got = adaptive_simpson(_spike, -1.0, 1.0, 1e-6)
assert abs(_got - _exact) / _exact < 1e-9, \
    f"adaptive_simpson on the spike gave {_got!r}, expected {_exact!r}"
assert _calls[0] < 8000, f"that took {_calls[0]} evaluations, which is far too many"
_uniform = simpson(_spike, -1.0, 1.0, 1000)
assert abs(_uniform - _exact) / _exact > 1e-8, \
    "a uniform rule on a thousand panels should still be far less accurate here"
assert abs(_got - _exact) < abs(_uniform - _exact) / 100.0, \
    "the adaptive estimate must beat the uniform one by orders of magnitude"
'''},
                    {"name": "The rate a singular integrand actually gives", "code": r'''
_r = halving_ratio(trapezoid, math.sqrt, 0.0, 1.0, 2.0 / 3.0, 32)
assert 2.7 < _r < 2.9, \
    f"the trapezoid rule on sqrt converges at h^1.5, so the ratio is about 2.83; got {_r!r}"
assert _r < 3.5, "it is emphatically not 4 — the error law needs a bounded second derivative"
_rs = halving_ratio(simpson, math.sqrt, 0.0, 1.0, 2.0 / 3.0, 32)
assert 2.7 < _rs < 2.9, \
    f"Simpson does no better on the same singularity; got {_rs!r}"
_smooth = halving_ratio(trapezoid, math.exp, 0.0, 1.0, math.e - 1.0, 32)
assert _smooth > 3.9, "the same code on a smooth integrand must still give 4"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Ordinary differential equations: order and stability",
            "summary": "Walking a solution forward one step at a time, and the two different things that can go wrong.",
            "concepts": [
                "Euler's method follows the tangent line for one step, exactly as Newton's method does for one guess",
                "Local error per step goes like h^2, and the step count is T/h, so the global error goes like h",
                "Heun averages the slopes at the two ends of the step, which is the trapezoid rule applied to y'",
                "RK4 weights four slopes 1, 2, 2, 1 over 6, and for y' = g(t) it reduces to Simpson's rule",
                "Order is measured, not asserted: the error ratio under halving comes out at 2, 4 and 16",
                "For y' = lambda*y an explicit step multiplies by a growth factor, and stability needs its magnitude below 1",
                "Forward Euler is stable only for h <= 2/|lambda|; a higher order does not enlarge the region much",
                "A stiff problem has a fast transient that is long dead and still dictates the step for every explicit method",
                "Backward Euler solves for the end-of-step slope and is stable at every step size",
            ],
            "read": [
                {
                    "title": "The tangent line, taken one step at a time",
                    "minutes": 14,
                    "body": r'''
A capacitor discharges through a resistor. Nobody handed you the charge as a
function of time; what you have is the rule that at every instant the current is
proportional to the charge remaining, which in scaled units is

$$y' = -y, \qquad y(0) = 1$$

The answer is $e^{-t}$, and $y(1) = 0.36787944117144233$, which will let every method
below be marked. What a program has is the same thing the physics gave: a value at
one point, and a rule for the slope anywhere.

## Follow the tangent, then look again

The slope at $(t_n, y_n)$ is $f(t_n, y_n)$. Follow that line for a distance $h$ and
land at

$$y_{n+1} = y_n + h\,f(t_n, y_n)$$

This is Euler's method, and it is the same move Newton's method made in module 2:
replace a curve by its tangent, act as though the tangent were the truth, then
re-measure at the new point.

```python
import math

def euler(f, t0, y0, t1, n):
    h = (t1 - t0) / n
    t, y = float(t0), float(y0)
    for i in range(n):
        y = y + h * f(t, y)
        t = t0 + (i + 1) * h
    return y

exact = math.exp(-1.0)
previous = None
for n in (4, 8, 16, 32, 64):
    err = abs(euler(lambda t, y: -y, 0.0, 1.0, 1.0, n) - exact)
    print(n, err, "ratio" if previous is None else previous / err)
    previous = err
```

With four steps the answer is $0.31640625$, which is $0.75^{4}$ — the method
multiplies by $(1 + h\lambda)$ each step, and here that is $0.75$. The errors are
$0.0515$, $0.0243$, $0.0118$, $0.00582$, $0.00289$, and the ratios are `2.12`,
`2.06`, `2.03`, `2.01`. Halving the step halves the error: first order.

That one is worth deriving, because the exponent is not what a single step suggests.
Taylor's theorem says one step is wrong by $\tfrac{1}{2}h^{2}y''(\xi)$, which is
*second* order. But reaching a fixed time $T$ takes $T/h$ steps, and each contributes
its own local error, so the errors accumulate:

$$\text{global error} \approx \frac{T}{h} \cdot \frac{h^{2}}{2}|y''|
= \frac{T h}{2}|y''|$$

One power of $h$ is spent on the number of steps. Every method in this module loses
an order the same way, which is why a rule with a local error of $h^{5}$ is called
fourth order.

## Averaging the two slopes

The tangent at the start of the step is the right slope only at the start. By the end
of the step the true slope has moved on, and Euler never notices. So take a
provisional step, look at the slope where it lands, and average:

$$k_1 = f(t_n, y_n), \qquad k_2 = f(t_n + h,\; y_n + hk_1), \qquad
y_{n+1} = y_n + \frac{h}{2}(k_1 + k_2)$$

That is Heun's method, and the shape of it should be familiar: averaging the values
at the two ends of an interval is the trapezoid rule from module 4, applied here to
$y'$ rather than to a fixed integrand.

```python
import math

def heun(f, t0, y0, t1, n):
    h = (t1 - t0) / n
    t, y = float(t0), float(y0)
    for i in range(n):
        k1 = f(t, y)
        k2 = f(t + h, y + h * k1)
        y = y + 0.5 * h * (k1 + k2)
        t = t0 + (i + 1) * h
    return y

exact = math.exp(-1.0)
previous = None
for n in (4, 8, 16, 32):
    err = abs(heun(lambda t, y: -y, 0.0, 1.0, 1.0, n) - exact)
    print(n, err, "ratio" if previous is None else previous / err)
    previous = err
```

Errors of $0.00465$, $0.00105$, $0.000251$, $0.0000613$, with ratios `4.41`, `4.20`,
`4.10`. Second order, for two slope evaluations per step instead of one.

Push the same idea to four slopes — one at the start, two in the middle, one at the
provisional end — and weight them $1, 2, 2, 1$ over 6:

```python
import math

def rk4(f, t0, y0, t1, n):
    h = (t1 - t0) / n
    t, y = float(t0), float(y0)
    for i in range(n):
        k1 = f(t, y)
        k2 = f(t + 0.5*h, y + 0.5*h*k1)
        k3 = f(t + 0.5*h, y + 0.5*h*k2)
        k4 = f(t + h, y + h*k3)
        y = y + h * (k1 + 2*k2 + 2*k3 + k4) / 6.0
        t = t0 + (i + 1) * h
    return y

exact = math.exp(-1.0)
previous = None
for n in (4, 8, 16, 32):
    err = abs(rk4(lambda t, y: -y, 0.0, 1.0, 1.0, n) - exact)
    print(n, err, "ratio" if previous is None else previous / err)
    previous = err
```

The errors are $1.48 \cdot 10^{-5}$, $8.31 \cdot 10^{-7}$, $4.93 \cdot 10^{-8}$,
$3.00 \cdot 10^{-9}$, and the ratios are `17.8`, `16.9`, `16.4`, settling towards 16.
Fourth order. Those weights are not arbitrary either: when $f$ depends on $t$ alone,
$k_2$ and $k_3$ are the same value at the midpoint and the formula collapses to
$\tfrac{h}{6}(f_0 + 4f_{1/2} + f_1)$, which is Simpson's rule. RK4 is Simpson's rule
taught to cope with an integrand that depends on the answer.

Count the cost honestly. RK4 with four steps spends 16 evaluations of $f$ and is
wrong by $1.5 \cdot 10^{-5}$; Euler with sixteen steps spends the same 16 evaluations
and is wrong by $0.0118$. Eight hundred times the accuracy for the same money, and
the gap widens with every refinement.

## The mistake: treating a blow-up as an accuracy problem

Now change the physics. A stiffer circuit gives $y' = -50y$, still decaying, still
harmless. Integrate it to $t = 1$ with ten steps.

```python
def euler(f, t0, y0, t1, n):
    h = (t1 - t0) / n
    t, y = float(t0), float(y0)
    out = []
    for i in range(n):
        y = y + h * f(t, y)
        t = t0 + (i + 1) * h
        out.append(y)
    return out

print(euler(lambda t, y: -50*y, 0.0, 1.0, 1.0, 10)[:5])
```

The values are `-4.0, 16.0, -64.0, 256.0, -1024.0`, ending at $1.05 \cdot 10^{6}$
where the true answer is $1.9 \cdot 10^{-22}$. The sign alternates and the magnitude
quadruples every step.

The instinct is to reach for a better method, and it is a good instinct that fails
here. RK4 on the same problem with the same step reaches $2.3 \cdot 10^{11}$ — five
orders *worse* than Euler. Order and stability are different axes, and no amount of
the first buys the second.

What is happening is visible in one line of algebra. For $y' = \lambda y$, Euler's
step is $y_{n+1} = (1 + h\lambda)y_n$: a multiplication by a fixed number. After $n$
steps the answer is $(1 + h\lambda)^{n}y_0$, so the computed solution decays only if

$$|1 + h\lambda| \leq 1 \qquad\text{that is}\qquad h \leq \frac{2}{|\lambda|}
\;\;\text{for real } \lambda < 0$$

With $\lambda = -50$ that limit is $h = 0.04$, and the run above used $h = 0.1$, giving
a growth factor of $-4$. RK4 has its own growth factor,
$1 + z + z^{2}/2 + z^{3}/6 + z^{4}/24$ with $z = h\lambda$, which at $z = -5$ is
$13.7$ — a larger stability region than Euler's, but not five times larger, and $-5$
is outside it too.

## Taking the slope at the other end

Nothing forces the slope to be sampled at the start of the step. Evaluate it at the
end instead:

$$y_{n+1} = y_n + h\,f(t_{n+1},\, y_{n+1})$$

The unknown is now on both sides, which is what makes the method implicit. For the
test equation it can be solved by hand: $y_{n+1}(1 - h\lambda) = y_n$, so
$y_{n+1} = y_n/(1 - h\lambda)$.

```python
lam = -50.0
h = 0.1
y = 1.0
for i in range(10):
    y = y / (1.0 - h * lam)
print(y)
```

It prints `1.6538171687920194e-08`, decaying monotonically at a factor of six per
step, and it would decay for any $h$ whatever, since $|1 - h\lambda| > 1$ for every
positive $h$ when $\lambda$ is negative. Backward Euler is stable without condition,
and the price is that each step needs an equation solved — for a nonlinear $f$, a
Newton iteration, which is why module 2 came first.

A problem is called **stiff** when its fastest time constant is far shorter than the
interval you care about. Here the transient $e^{-50t}$ is finished by $t = 0.2$, and
it still dictates the step size for the whole run, because an explicit method's
stability depends on the fastest mode present rather than on the one you are watching.
Real systems are full of them: a chemical mechanism with one fast reaction, a circuit
with one small capacitor, a mesh with one small cell.

## Where this stops holding

Stability is not accuracy, and it is a mistake to read a bounded answer as a good one.
Take $\lambda = -50$ with 26 steps, so that $h = 0.0385$ is inside the limit. The run
is stable and every step shrinks, and it finishes at $0.125$ where the true value is
$2 \cdot 10^{-22}$. Every step is multiplying by $-0.923$ when it ought to be
multiplying by $e^{-50h} = 0.146$ — so the answer also alternates in sign, on a
problem whose solution never changes sign at all. Nothing has blown up and nothing is
right. Only below $h = 1/|\lambda| = 0.02$ does the growth factor become positive and
the computed solution start to resemble a decay.

The second limit is the fixed step itself. A trajectory that is placid for most of its
length and violent for a moment is badly served by one step size, exactly as a
peaked integrand was badly served by one panel width in module 4, and the answer is
the same: estimate the local error by comparing two steps, and let the estimate choose
the step.

## What the lab asks

**Steppers, orders and the stability limit** has you write `euler`, `heun` and `rk4`
returning the whole trajectory as a list of `(t, y)` pairs, `backward_euler_linear`
for the test equation, `order_estimate` for measuring the order from two runs, and
`stability_limit`. The checks confirm the orders as 2, 4 and 16 rather than taking
them on trust, confirm that RK4 integrates a cubic $y'$ exactly because it is Simpson
underneath, and require both the blow-up at $h$ above $2/|\lambda|$ and the monotone
decay at a step below it.
''',
                },
            ],
            "quiz": {
                "title": "Order, cost and the step you are allowed",
                "minutes": 8,
                "questions": [
                    {
                        "q": "One Euler step is wrong by about $h^2 y''/2$, and yet the method is called first order. Why the difference?",
                        "opts": [
                            "The local estimate is optimistic: the true per-step error is proportional to $h$",
                            "Reaching a fixed time takes $T/h$ steps, so one power of $h$ is spent on the step count",
                            "Round-off adds a term proportional to $h$, and it dominates the truncation error at every step",
                            "The order counts evaluations of $f$ rather than powers of $h$, and Euler uses one per step",
                        ],
                        "a": 1,
                        "whys": [
                            "The local estimate is right and can be checked directly: take a single step of size $h$ from an exact value and the error falls by 4 when $h$ is halved.",
                            "Each of the $T/h$ steps contributes about $h^2y''/2$, and multiplying the count by the per-step error leaves $Th|y''|/2$ — first order in $h$.",
                            "Round-off does add a term, and it grows as $h$ *shrinks* rather than with $h$, since more steps mean more roundings. It is invisible until $h$ is far smaller than anything used here.",
                            "Order is defined by the power of $h$ in the global error. Evaluation count is the cost, a separate axis, and the two are traded against each other when a method is chosen.",
                        ],
                        "why": r"""
The distinction is between local and global error. One step from an exact value costs
$\tfrac{1}{2}h^{2}y''$; reaching $T$ takes $T/h$ of them; multiply and one power of
$h$ cancels, leaving a global error proportional to $h$. Every method here loses an
order the same way, which is why RK4, whose local error is $h^{5}$, is called fourth
order. The measured ratios settle at 2 for Euler and 16 for RK4, which is the global
order and the one that matters when a step size is chosen.
""",
                    },
                    {
                        "q": "RK4 with 4 steps and Euler with 16 both cost 16 evaluations of $f$. RK4's error is $1.5 \\cdot 10^{-5}$ and Euler's is $0.0118$. What generalises here?",
                        "opts": [
                            "A higher order wins once the step is small enough for its error term to dominate",
                            "RK4 is always better, because averaging four slopes cancels errors that one slope cannot",
                            "Nothing generalises: on a different equation the same comparison could come out either way",
                            "It only holds for a linear $f$, where RK4's extra slopes coincide",
                        ],
                        "a": 0,
                        "whys": [
                            "The constants in front of $h^4$ and $h$ differ, so at a large enough step the low-order method can win; below the crossover the exponent decides, and the gap then widens with every refinement.",
                            "Not always: at a step size near the stability limit RK4 can be worse, and on the stiff problem in the reading it is five orders worse than Euler at the same step.",
                            "The exponents are properties of the methods rather than of the equation, so once the step is inside the asymptotic regime the fourth-order method pulls away on any smooth problem.",
                            "The four slopes coincide for $f$ depending on $t$ alone, not for a linear $f$, and the reading's comparison is on $y' = -y$, which is linear and shows the full gap.",
                        ],
                        "why": r"""
Two error curves, $Ch$ against $Dh^{4}$, with different constants. For a large step the
constants can put the low-order method ahead, which is why the ratio columns in the
reading only settle after a refinement or two. Once the step is small enough for the
exponent to dominate, the higher-order method wins by more at every subsequent
halving. The one thing this reasoning cannot tell you is whether either method is
stable at that step, which is a separate question and the subject of the rest of the
module.
""",
                    },
                    {
                        "q": "Forward Euler on $y' = -50y$ with $h = 0.1$ gives $-4, 16, -64, 256$. What is the growth factor telling you?",
                        "opts": [
                            "The problem is ill conditioned, so the true solution is as sensitive as the computed one",
                            "The step multiplies by $1 + h\\lambda = -4$, and any factor beyond 1 in magnitude grows",
                            "The tangent line is a poor approximation here, so the truncation error is enormous",
                            "Round-off is being amplified by the large coefficient, which is what the alternating sign shows",
                        ],
                        "a": 1,
                        "whys": [
                            "The true solution is $e^{-50t}$, which is about as insensitive as a solution can be: perturb the initial value and the difference decays. The instability belongs to the method, not the problem.",
                            "Euler on $y' = \\lambda y$ is a multiplication by $1 + h\\lambda$ each step, and at $h\\lambda = -5$ that number is $-4$: the sign flips and the magnitude quadruples, forever.",
                            "The local truncation error is about $h^2 y''/2$, which for the first step is a few percent. What makes the run diverge is that the error is multiplied by 4 at every subsequent step rather than that it started large.",
                            "The run would do exactly this in exact arithmetic, starting from the exact value 1.0. Round-off contributes nothing here; the recurrence itself is divergent.",
                        ],
                        "why": r"""
For the test equation the method is a recurrence $y_{n+1} = (1 + h\lambda)y_n$, so the
whole of its behaviour is one number. With $\lambda = -50$ and $h = 0.1$ that number is
$-4$: the computed solution alternates in sign and grows by a factor of four each step,
and it would do so in exact arithmetic. Stability is a property of the recurrence, and
the fix is a step below $2/|\lambda| = 0.04$ — or a method whose growth factor stays
below 1 for every step, which is what an implicit method buys.
""",
                    },
                    {
                        "q": "On that same stiff problem, RK4 with $h = 0.1$ reaches $2.3 \\cdot 10^{11}$ where Euler reached $10^{6}$. What does that show?",
                        "opts": [
                            "RK4 was implemented wrongly: a fourth-order method cannot do worse than a first-order one",
                            "RK4 amplifies round-off through its four stages, and each stage compounds the previous one's error",
                            "Stability is a separate axis from order, and RK4's growth factor at $h\\lambda = -5$ is 13.7",
                            "The problem needs a smaller tolerance, and RK4 is more sensitive to the tolerance than Euler is",
                        ],
                        "a": 2,
                        "whys": [
                            "It can and does. Order describes how the error shrinks as $h \\to 0$; it says nothing at a step size where the recurrence itself is divergent, and this step is well outside both stability regions.",
                            "The stages are not compounding round-off — the same divergence appears in exact arithmetic. What compounds is the growth factor, applied once per step to whatever the solution currently is.",
                            "Its growth factor is $1 + z + z^2/2 + z^3/6 + z^4/24$, which at $z = -5$ is 13.7, so each step multiplies by 13.7 where Euler multiplied by 4.",
                            "Neither method here has a tolerance: both take a fixed step. Adaptive step control would in fact rescue this run, by refusing steps whose error estimate is large, which is a different mechanism.",
                        ],
                        "why": r"""
Every explicit method applied to $y' = \lambda y$ becomes a multiplication by some
polynomial in $z = h\lambda$: $1 + z$ for Euler, and the first five terms of $e^{z}$ for
RK4. RK4's stability region is larger — it reaches to about $z = -2.79$ on the real
axis where Euler stops at $-2$ — but $z = -5$ is outside both, and outside it RK4's
polynomial is the bigger number. Raising the order improves accuracy inside the
stability region and does almost nothing to enlarge it.
""",
                    },
                    {
                        "q": "Backward Euler gives $y_{n+1} = y_n/(1 - h\\lambda)$. What is the cost of its unconditional stability?",
                        "opts": [
                            "Its order drops to a half, since the implicit step is only accurate at the end point",
                            "It cannot be used with a variable step, because the factor is fixed once the step is chosen",
                            "It needs the derivative of $f$, which for a system means forming and factoring a Jacobian",
                            "The unknown appears on both sides, so a general $f$ needs an equation solved every step",
                        ],
                        "a": 3,
                        "whys": [
                            "It is first order, the same as forward Euler, and the reading's closed form is exact for the test equation rather than approximate. Nothing about being implicit costs accuracy.",
                            "Variable steps are as available as they are for any method — the factor is recomputed from whatever $h$ the step controller chose, which is one division.",
                            "A Jacobian is what a practical Newton solve for a system uses, and it is a consequence of the real cost rather than the cost itself: the root-finding is required whether or not it uses derivatives.",
                            "$y_{n+1}$ appears inside $f$, so each step is a root-finding problem — trivial for the linear test equation, a Newton iteration for anything else.",
                        ],
                        "why": r"""
Taking the slope at the end of the step puts the unknown on both sides, and only for a
linear $f$ can it be rearranged by hand into $y_n/(1 - h\lambda)$. For a general $f$
each step is $y_{n+1} - y_n - hf(t_{n+1}, y_{n+1}) = 0$, a root-finding problem in
$y_{n+1}$ — which is where module 2 comes back, usually as a Newton iteration with the
previous step's value as the starting guess. That is the trade a stiff solver makes:
several evaluations and a linear solve per step, against a step size that is limited
by accuracy rather than by the fastest mode in the system.
""",
                    },
                    {
                        "q": "With $\\lambda = -50$ and 26 steps, every Euler step shrinks and the run ends at 0.125. The true value is $2 \\cdot 10^{-22}$. What should be concluded?",
                        "opts": [
                            "Stability was the wrong question: 26 steps is inside the limit and nowhere near accurate",
                            "The method has converged, and the remaining difference is the accumulated round-off of 26 steps",
                            "The true value is below the smallest normal double, so no method could represent it",
                            "The step is only barely inside the limit, and any step inside it gives a usable answer",
                        ],
                        "a": 0,
                        "whys": [
                            "Being inside the stability region means the recurrence does not diverge, and that is all it means. Each step multiplies by -0.923 where the true solution multiplies by 0.146.",
                            "Round-off over 26 steps is at the $10^{-15}$ level; the discrepancy here is twenty-one orders of magnitude larger and comes entirely from the size of the step.",
                            "$2 \\cdot 10^{-22}$ is a perfectly ordinary double, nearly three hundred orders above the underflow threshold, and RK4 with a hundred steps returns it to two digits.",
                            "Inside the limit only guarantees a bounded answer. Accuracy needs $h$ small compared with $1/|\\lambda|$, which is $0.02$ here, not merely below $2/|\\lambda|$.",
                        ],
                        "why": r"""
The stability limit and the accuracy requirement are different thresholds, and the
first is far weaker. At $h = 0.0385$ the growth factor is $-0.923$, so the run is
stable — shrinking, bounded, entirely plausible on a plot of magnitudes — while the
true factor per step is $e^{-50h} = 0.146$. Accuracy needs $h$ small compared with the time constant
$1/|\lambda| = 0.02$, where stability only asked for $h$ below $2/|\lambda| = 0.04$.
A stable run that nobody checks against a refinement is a picture, not a result.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Four slopes and an implicit step, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "steppers.py — five holes; the weights are what make the method fourth order",
                "brief": r"""
The four stages of RK4 are worth reading slowly: two of them are evaluated at the
midpoint of the step, and the second of those uses the first one's answer. Nothing
runs here. Filled in correctly, `rk4` on the decaying exponential is wrong by
$1.5 \cdot 10^{-5}$ after four steps, and the implicit step decays for any step size
at all.
""",
                "listing": r'''
def rk4(f, t0, y0, t1, n):
    """Four slopes per step, weighted 1, 2, 2, 1."""
    h = (t1 - t0) / n
    out = [(float(t0), float(y0))]
    t, y = float(t0), float(y0)
    for i in range(n):
        k1 = f(t, y)
        k2 = f(t + 0.5 * h, y + ___ * k1)
        k3 = f(t + 0.5 * h, y + 0.5 * h * ___)
        k4 = f(t + h, y + h * k3)
        y = y + h * (k1 + ___ * (k2 + k3) + k4) / ___
        t = t0 + (i + 1) * h
        out.append((t, y))
    return out


def backward_euler_linear(lam, y0, t1, n):
    """y' = lam * y, with the slope taken at the END of the step."""
    h = t1 / n
    y = float(y0)
    out = [(0.0, y)]
    for i in range(n):
        y = y / (1.0 ___ h * lam)
        out.append((h * (i + 1), y))
    return out
''',
                "blanks": [
                    {
                        "prompt": "The second slope is sampled after moving this far along the first one.",
                        "hole": "?",
                        "opts": ["0.5 * h", "h", "0.5", "h * h"],
                        "a": 0,
                        "why": "The stage is evaluated at the midpoint of the step, so the state it is evaluated at has to be advanced by half a step along the slope already computed.",
                        "whys": [
                            "The time argument moved half a step, so the state argument has to move half a step too, or the slope is being sampled at a point that is on no trajectory at all.",
                            "Advancing a whole step in y while advancing half a step in t samples the slope at an inconsistent point, and the method drops from fourth order to first.",
                            "Without the step size this adds half of a slope to a state, which is a units error: the term has to be a rate multiplied by a time.",
                            "Squaring the step makes the correction vanish far too quickly as the step shrinks, so the stage collapses towards the value already held and the method reduces to Euler.",
                        ],
                    },
                    {
                        "prompt": "The third slope refines the midpoint estimate using this one.",
                        "hole": "?",
                        "opts": ["k1", "k2", "k3", "y"],
                        "a": 1,
                        "why": "The third stage is at the same midpoint as the second, but starting from a state built with the second slope instead of the first, which is what makes the pair of midpoint estimates better than either alone.",
                        "whys": [
                            "Reusing the first slope makes the third stage identical to the second, so two of the four evaluations return the same number and the extra work buys nothing.",
                            "Each stage is built from the one before it, so the midpoint is visited twice with a better state the second time, and the two estimates are averaged by the equal weights.",
                            "A stage cannot be defined in terms of itself, and the name does not exist yet at this point in the step.",
                            "The state is already the base of the expression; adding a multiple of it to itself scales the solution rather than advancing it along a slope.",
                        ],
                    },
                    {
                        "prompt": "The two midpoint slopes carry this weight relative to the end ones.",
                        "hole": "?",
                        "opts": ["2.0", "4.0", "0.5", "1.0"],
                        "a": 0,
                        "why": "The weights are 1, 2, 2, 1 and they add to 6, which matches the divisor; the midpoint is worth twice an endpoint for the same reason it is in Simpson's rule.",
                        "whys": [
                            "Doubling the middle pair against single weights on the ends gives 1, 2, 2, 1 summing to 6, and when the two midpoint slopes coincide it becomes Simpson's 1, 4, 1 over 6.",
                            "Four apiece makes the weights sum to 10 against a divisor of 6, so even a constant slope advances the solution by nearly twice the step it should.",
                            "Halving the midpoint slopes puts more trust in the two end estimates, which are the least accurate of the four, and the weights then sum to 3 rather than 6.",
                            "Equal weights on all four stages is a valid-looking average that is only second order, and the halving ratio comes out at 4 rather than 16.",
                        ],
                    },
                    {
                        "prompt": "The weighted sum of slopes is divided by this.",
                        "hole": "?",
                        "opts": ["3.0", "6.0", "4.0", "2.0"],
                        "a": 1,
                        "why": "The four weights add to 6, so dividing by 6 turns the sum into an average slope; a constant slope then advances the solution by exactly that slope times the step.",
                        "whys": [
                            "Dividing by 3 doubles every step, so an equation whose solution is a straight line comes out with twice the gradient it should have.",
                            "Test it on a constant slope: the four stages all return the same number, the weighted sum is six times it, and only a divisor of 6 returns the slope itself.",
                            "Four is the number of stages rather than the sum of their weights, and using it overstates the step by half.",
                            "Two would be the divisor if the weights were 1 and 1, which is Heun's method; here the weights add to 6 and this triples every step.",
                        ],
                    },
                    {
                        "prompt": "The implicit step divides by this combination.",
                        "hole": "?",
                        "opts": ["-", "+", "*", "/"],
                        "a": 0,
                        "why": "Rearranging y_new = y + h*lam*y_new collects the unknown on the left as y_new*(1 - h*lam), so the update divides by one minus the product.",
                        "whys": [
                            "Moving the h*lam*y_new term across the equals sign subtracts it, which is what makes the factor exceed 1 in magnitude for a decaying problem and the method stable at any step.",
                            "Adding gives the growth factor of the forward method dressed up as a division, and for a step beyond the stability limit it produces a divisor below 1 in magnitude, which grows the solution.",
                            "Multiplying gives a divisor of h times lam, so the answer scales with the step in a way that has no limit as the step shrinks, and a step of zero divides by zero.",
                            "Dividing one by the product inverts the step size, so halving the step changes the update by a factor of two in the wrong direction and the method converges to nothing.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Steppers, orders and the stability limit",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Six routines in `main.py`. The three steppers share one signature and return the
whole trajectory, so the checks can look at every point rather than only the last.

## The steppers

Each of `euler(f, t0, y0, t1, n)`, `heun(...)` and `rk4(...)` returns a list of
`(t, y)` pairs of length `n + 1`, starting with `(t0, y0)`. Compute the time as
`t0 + (i + 1) * h` rather than by repeated addition, so the last entry lands exactly
on `t1`. Raise `ValueError` when `n < 1` or `t1 <= t0`.

- `euler` — one slope: `y + h * f(t, y)`.
- `heun` — two: the slope now and the slope at the provisional end, averaged.
- `rk4` — four, weighted 1, 2, 2, 1 over 6.

## The implicit one, and the diagnostics

- `backward_euler_linear(lam, y0, t1, n)` — the test equation $y' = \lambda y$ with
  the slope taken at the end of the step, so each update is `y / (1 - h * lam)`.
  Starts at $t = 0$ and returns `(t, y)` pairs like the others. `ValueError` when
  `n < 1`, `t1 <= 0`, or `1 - h * lam` is zero.
- `order_estimate(method, f, t0, y0, t1, exact, n)` — the ratio of the final error at
  `n` steps to the final error at `2 * n` steps. `ValueError` when the finer run is
  exact.
- `stability_limit(lam)` — the largest step for which forward Euler does not grow on
  $y' = \lambda y$, which is `2 / abs(lam)`. `ValueError` when `lam >= 0`, since a
  growing solution has no such limit.

```text
euler(lambda t, y: -y, 0, 1, 1, 4)[-1]   ->  (1.0, 0.31640625)      = 0.75**4
order_estimate(euler, ..., 16)           ->  about 2
order_estimate(heun,  ..., 16)           ->  about 4
order_estimate(rk4,   ..., 8)            ->  about 16
stability_limit(-50.0)                   ->  0.04
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def euler(f, t0, y0, t1, n):
    """One slope per step. Returns [(t, y), ...] of length n + 1."""
    # your code here


def heun(f, t0, y0, t1, n):
    """The average of the slope now and the slope at the provisional end."""
    # your code here


def rk4(f, t0, y0, t1, n):
    """Four slopes per step, weighted 1, 2, 2, 1 over 6."""
    # your code here


def backward_euler_linear(lam, y0, t1, n):
    """y' = lam * y with the slope taken at the end of the step."""
    # your code here


def order_estimate(method, f, t0, y0, t1, exact, n):
    """The factor by which halving the step reduces the final error."""
    # your code here


def stability_limit(lam):
    """The largest step for which forward Euler does not grow."""
    # your code here


_decay = lambda t, y: -y
print("euler: ", euler(_decay, 0.0, 1.0, 1.0, 4)[-1])
print("heun:  ", heun(_decay, 0.0, 1.0, 1.0, 4)[-1])
print("rk4:   ", rk4(_decay, 0.0, 1.0, 1.0, 4)[-1])
print("order: ", order_estimate(rk4, _decay, 0.0, 1.0, 1.0, math.exp(-1.0), 8))
print("limit: ", stability_limit(-50.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def _check(t0, t1, n):
    if n < 1:
        raise ValueError("n must be at least 1")
    if t1 <= t0:
        raise ValueError("t1 must be above t0")
    return (t1 - t0) / n


def euler(f, t0, y0, t1, n):
    """One slope per step. Returns [(t, y), ...] of length n + 1."""
    h = _check(t0, t1, n)
    t, y = float(t0), float(y0)
    out = [(t, y)]
    for i in range(n):
        y = y + h * f(t, y)
        t = t0 + (i + 1) * h
        out.append((t, y))
    return out


def heun(f, t0, y0, t1, n):
    """The average of the slope now and the slope at the provisional end."""
    h = _check(t0, t1, n)
    t, y = float(t0), float(y0)
    out = [(t, y)]
    for i in range(n):
        k1 = f(t, y)
        k2 = f(t + h, y + h * k1)
        y = y + 0.5 * h * (k1 + k2)
        t = t0 + (i + 1) * h
        out.append((t, y))
    return out


def rk4(f, t0, y0, t1, n):
    """Four slopes per step, weighted 1, 2, 2, 1 over 6."""
    h = _check(t0, t1, n)
    t, y = float(t0), float(y0)
    out = [(t, y)]
    for i in range(n):
        k1 = f(t, y)
        k2 = f(t + 0.5 * h, y + 0.5 * h * k1)
        k3 = f(t + 0.5 * h, y + 0.5 * h * k2)
        k4 = f(t + h, y + h * k3)
        y = y + h * (k1 + 2.0 * (k2 + k3) + k4) / 6.0
        t = t0 + (i + 1) * h
        out.append((t, y))
    return out


def backward_euler_linear(lam, y0, t1, n):
    """y' = lam * y with the slope taken at the end of the step."""
    h = _check(0.0, t1, n)
    denominator = 1.0 - h * lam
    if denominator == 0.0:
        raise ValueError("the implicit step is singular for this lam and h")
    y = float(y0)
    out = [(0.0, y)]
    for i in range(n):
        y = y / denominator
        out.append((h * (i + 1), y))
    return out


def order_estimate(method, f, t0, y0, t1, exact, n):
    """The factor by which halving the step reduces the final error."""
    coarse = abs(method(f, t0, y0, t1, n)[-1][1] - exact)
    fine = abs(method(f, t0, y0, t1, 2 * n)[-1][1] - exact)
    if fine == 0.0:
        raise ValueError("the finer run is exact, so the ratio is undefined")
    return coarse / fine


def stability_limit(lam):
    """The largest step for which forward Euler does not grow."""
    if lam >= 0:
        raise ValueError("a growing solution has no stability limit")
    return 2.0 / abs(lam)


_decay = lambda t, y: -y
print("euler: ", euler(_decay, 0.0, 1.0, 1.0, 4)[-1])
print("heun:  ", heun(_decay, 0.0, 1.0, 1.0, 4)[-1])
print("rk4:   ", rk4(_decay, 0.0, 1.0, 1.0, 4)[-1])
print("order: ", order_estimate(rk4, _decay, 0.0, 1.0, 1.0, math.exp(-1.0), 8))
print("limit: ", stability_limit(-50.0))
'''}],
                "hints": [
                    "All three steppers share a skeleton: validate, compute `h`, seed the output with `(t0, y0)`, then loop `n` times appending. Write that once and change only the line that advances `y`.",
                    "Set the time as `t0 + (i + 1) * h` rather than `t += h`. Repeated addition accumulates round-off, and one check compares the last time value against `t1` exactly.",
                    "In `rk4` the third stage is evaluated at the same time as the second — `t + 0.5 * h` — but from a state built with `k2` rather than `k1`. Getting that wrong leaves the method looking correct and only second order, which `order_estimate` catches.",
                    "`backward_euler_linear` has no `f` because the equation is solved by hand: `y * (1 - h * lam) = y_previous`. Compute the divisor once outside the loop.",
                ],
                "tests": [
                    {"name": "Euler's shape, and the growth factor it applies", "code": r'''
_path = euler(lambda t, y: y, 0.0, 1.0, 1.0, 4)
assert len(_path) == 5, f"n = 4 gives 5 points, got {len(_path)}"
assert _path[0] == (0.0, 1.0), f"the path starts at (t0, y0); got {_path[0]!r}"
assert _path[-1][0] == 1.0, f"the last time must land exactly on t1; got {_path[-1][0]!r}"
for _i in range(5):
    assert abs(_path[_i][0] - 0.25 * _i) < 1e-15, f"time {_i} is {_path[_i][0]!r}"
assert abs(_path[-1][1] - 1.25 ** 4) < 1e-15, \
    f"on y' = y each step multiplies by 1 + h; expected {1.25 ** 4!r}, got {_path[-1][1]!r}"
for _args in [(0.0, 1.0, 0), (0.0, 1.0, -3), (1.0, 1.0, 4), (2.0, 1.0, 4)]:
    try:
        euler(lambda t, y: y, _args[0], 1.0, _args[1], _args[2])
        assert False, f"euler with (t0, t1, n) = {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Euler is first order, measured rather than assumed", "code": r'''
_decay = lambda t, y: -y
_exact = math.exp(-1.0)
assert abs(euler(_decay, 0.0, 1.0, 1.0, 4)[-1][1] - 0.31640625) < 1e-15, \
    f"four steps give 0.75**4 = 0.31640625; got {euler(_decay, 0.0, 1.0, 1.0, 4)[-1][1]!r}"
_r = order_estimate(euler, _decay, 0.0, 1.0, 1.0, _exact, 16)
assert 1.9 < _r < 2.1, f"halving the step should halve the error; the ratio is {_r!r}"
assert abs(euler(_decay, 0.0, 1.0, 1.0, 1000)[-1][1] - _exact) < 2e-4, \
    "a thousand steps should be within 2e-4"
try:
    order_estimate(euler, lambda t, y: 1.0, 0.0, 0.0, 1.0, 1.0, 4)
    assert False, "an exact finer run leaves the ratio undefined and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Heun is second order, and exact where the trapezoid rule is", "code": r'''
_decay = lambda t, y: -y
_exact = math.exp(-1.0)
_r = order_estimate(heun, _decay, 0.0, 1.0, 1.0, _exact, 16)
assert 3.8 < _r < 4.3, f"Heun should divide the error by about 4; the ratio is {_r!r}"
assert abs(heun(_decay, 0.0, 1.0, 1.0, 4)[-1][1] - 0.3725290298461914) < 1e-12, \
    f"four steps gave {heun(_decay, 0.0, 1.0, 1.0, 4)[-1][1]!r}"
_line = heun(lambda t, y: 2.0 * t, 0.0, 0.0, 1.0, 3)[-1][1]
assert abs(_line - 1.0) < 1e-14, \
    f"the average of the two end slopes is the trapezoid rule, which is exact for a " \
    f"linear y'; got {_line!r} where the answer is 1.0"
assert abs(heun(_decay, 0.0, 1.0, 1.0, 64)[-1][1] - _exact) < 2e-5, \
    "sixty-four steps should be inside 2e-5"
'''},
                    {"name": "RK4 is fourth order", "code": r'''
_decay = lambda t, y: -y
_exact = math.exp(-1.0)
_r = order_estimate(rk4, _decay, 0.0, 1.0, 1.0, _exact, 8)
assert 15.0 < _r < 18.0, f"RK4 should divide the error by about 16; the ratio is {_r!r}"
assert abs(rk4(_decay, 0.0, 1.0, 1.0, 4)[-1][1] - _exact) < 2e-5, \
    f"four steps should be inside 2e-5; got an error of " \
    f"{abs(rk4(_decay, 0.0, 1.0, 1.0, 4)[-1][1] - _exact)!r}"
assert abs(rk4(_decay, 0.0, 1.0, 1.0, 20)[-1][1] - _exact) < 1e-7, \
    "twenty steps should be inside 1e-7"
_logistic = rk4(lambda t, y: y * (1.0 - y), 0.0, 0.5, 1.0, 20)[-1][1]
_want = 1.0 / (1.0 + math.exp(-1.0))
assert abs(_logistic - _want) < 1e-8, \
    f"the logistic equation from y(0) = 0.5 reaches {_want!r}; got {_logistic!r}"
'''},
                    {"name": "RK4 is Simpson's rule underneath", "code": r'''
_cubic = rk4(lambda t, y: 4.0 * t**3, 0.0, 0.0, 1.0, 2)[-1][1]
assert abs(_cubic - 1.0) < 1e-14, \
    f"with y' a cubic in t the stages become Simpson's rule, which is exact; got {_cubic!r}"
assert abs(rk4(lambda t, y: 3.0 * t * t, 0.0, 0.0, 1.0, 5)[-1][1] - 1.0) < 1e-14, \
    "and it stays exact at any step count"
_quartic = rk4(lambda t, y: 5.0 * t**4, 0.0, 0.0, 1.0, 2)[-1][1]
assert abs(_quartic - 1.0) > 1e-6, \
    f"a quartic y' is past Simpson's degree of exactness, so this should NOT be exact; " \
    f"got {_quartic!r}"
assert abs(_quartic - 1.0) < 1e-2, f"it should still be close; got {_quartic!r}"
'''},
                    {"name": "The step that makes an explicit method explode", "code": r'''
_stiff = lambda t, y: -50.0 * y
_path = [y for _, y in euler(_stiff, 0.0, 1.0, 1.0, 10)]
assert abs(_path[-1]) > 1e5, \
    f"h = 0.1 is beyond the limit of 0.04, so this must diverge; it ended at {_path[-1]!r}"
for _i in range(1, len(_path)):
    assert _path[_i] * _path[_i - 1] < 0, "the growth factor is negative, so the sign alternates"
    assert abs(_path[_i]) > abs(_path[_i - 1]), "and the magnitude grows every step"
_r4 = rk4(_stiff, 0.0, 1.0, 1.0, 10)[-1][1]
assert abs(_r4) > abs(_path[-1]), \
    f"RK4 at the same step is worse, not better: {_r4!r} against {_path[-1]!r}"
assert abs(rk4(_stiff, 0.0, 1.0, 1.0, 100)[-1][1]) < 1e-20, \
    "with h = 0.01 RK4 is inside its stability region and decays"
'''},
                    {"name": "The implicit step decays whatever the step size", "code": r'''
_path = backward_euler_linear(-50.0, 1.0, 1.0, 10)
assert len(_path) == 11 and _path[0] == (0.0, 1.0), f"the path starts at (0.0, 1.0); got {_path[0]!r}"
assert abs(_path[1][1] - 1.0 / 6.0) < 1e-15, \
    f"one step of h = 0.1 divides by 1 - 0.1*(-50) = 6; got {_path[1][1]!r}"
for _i in range(1, 11):
    assert 0.0 < _path[_i][1] < _path[_i - 1][1], "every step must decrease, and stay positive"
assert abs(_path[-1][1] - 6.0 ** -10) < 1e-15, f"ten steps give 6**-10; got {_path[-1][1]!r}"
_huge = backward_euler_linear(-50.0, 1.0, 1.0, 1)
assert 0.0 < _huge[-1][1] < 0.03, \
    f"even one enormous step stays bounded and positive; got {_huge[-1][1]!r}"
for _args in [(-50.0, 1.0, 0), (-50.0, 0.0, 4), (-50.0, -1.0, 4)]:
    try:
        backward_euler_linear(_args[0], 1.0, _args[1], _args[2])
        assert False, f"backward_euler_linear with {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The stability limit, either side of it", "code": r'''
assert abs(stability_limit(-50.0) - 0.04) < 1e-15, \
    f"stability_limit(-50) is 2/50 = 0.04; got {stability_limit(-50.0)!r}"
assert abs(stability_limit(-2.0) - 1.0) < 1e-15, "stability_limit(-2) is 1.0"
for _lam in (0.0, 1.0, 50.0):
    try:
        stability_limit(_lam)
        assert False, f"stability_limit({_lam}) should raise ValueError"
    except ValueError:
        pass
_stiff = lambda t, y: -50.0 * y
_inside = [y for _, y in euler(_stiff, 0.0, 1.0, 1.0, 26)]
assert 1.0 / 26 < stability_limit(-50.0), "26 steps puts h inside the limit"
for _i in range(1, len(_inside)):
    assert abs(_inside[_i]) < abs(_inside[_i - 1]), \
        "inside the limit every step shrinks in magnitude"
_outside = [y for _, y in euler(_stiff, 0.0, 1.0, 1.0, 24)]
assert 1.0 / 24 > stability_limit(-50.0), "24 steps puts h outside the limit"
assert abs(_outside[-1]) > 1.0, f"outside it the run grows; it ended at {_outside[-1]!r}"
_positive = [y for _, y in euler(_stiff, 0.0, 1.0, 1.0, 60)]
for _i in range(1, len(_positive)):
    assert 0.0 < _positive[_i] < _positive[_i - 1], \
        "with h below 1/50 the growth factor is positive and the decay is monotone"
assert abs(_inside[-1]) > 0.1, \
    "and note that the stable run is nowhere near the true value of 2e-22 — stability is not accuracy"
'''},
                ],
            },
        },
    ],
    "capstone": {
        "title": "Capstone — a trajectory engine built from all five methods",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
One library, `numkit.py`, that fires a projectile through quadratic drag and answers
questions about where it went. `main.py` is a demo that finds the launch angle for a
target and prints the report. Every method in the course appears, and each one does a
job that the others cannot.

## The toolbox, carried forward

- `kahan_sum(values)` — compensated summation, from module 1. The normal equations
  below add powers of $x$ up to the fourth, and those sums are long and badly scaled.
- `secant(f, x0, x1, tol=1e-10, max_iter=100)` — module 2, returning the root only.
  `ValueError` when the two function values are equal, and when `max_iter` passes go
  by without the step falling under `tol`.
- `solve(a, b, tol=1e-14)` — module 3: elimination with **partial pivoting**, then
  back substitution. `ValueError` for a matrix that is not square or non-empty, a
  right-hand side of the wrong length, or a pivot at or below `tol`.
- `adaptive_simpson(f, a, b, tol=1e-10, max_depth=40)` — module 4, with the same
  `(left + right - whole) / 15` test.
- `rk4_system(f, t0, y0, t1, n)` — module 5, promoted to vectors. `f(t, y)` takes a
  list and returns a list of the same length; the result is a list of
  `(t, [state...])` pairs of length `n + 1`. `ValueError` when `n < 1` or
  `t1 <= t0`.

## The projectile

Take `GRAVITY = 9.81`, a state of `[x, y, vx, vy]`, and a drag force opposing the
motion with magnitude proportional to the *square* of the speed:

$$\dot v_x = -k\,|v|\,v_x, \qquad \dot v_y = -g - k\,|v|\,v_y$$

- `derivative(drag)` — returns the function `f(t, state)` above. `ValueError` for a
  negative `drag`.
- `state_at(t, angle, speed, drag=0.0, steps=200)` — the state at time `t`, from a
  launch at the origin. `ValueError` unless `0 < angle < pi/2` and `speed > 0`.
- `flight_time(angle, speed, drag=0.0, steps=200)` — when the height returns to zero.
  The height at time `t` is an entire ODE solve, so there is no derivative to
  differentiate: bracket it around the drag-free flight time
  $2v\sin\theta/g$ and finish with `secant`.
- `range_of(...)`, and `arc_length(angle, speed, drag=0.0, steps=200, tol=1e-8)` —
  the distance flown, which is the integral of the speed over the flight and needs
  `adaptive_simpson` because each evaluation of the speed costs a solve.
- `launch_angle(target, speed, drag=0.0, steps=200)` — the angle below 45 degrees
  whose range is `target`. `ValueError` when `target <= 0`, and when it exceeds the
  range at 45 degrees, because a target nobody can hit deserves an exception rather
  than a plausible angle.

## Fitting and reporting

- `fit_quadratic(xs, ys)` — least squares $c_0 + c_1x + c_2x^2$ through the normal
  equations $\sum x^{i+j}c_j = \sum x^{i}y$, a 3 by 3 system solved with `solve`.
  `ValueError` for mismatched lengths, fewer than three points, or a singular system.
  Note what this costs: forming the normal equations squares the condition number of
  the design matrix, which is the price of the shortcut.
- `report(angle, speed, drag=0.0, steps=200)` — a **string** of exactly five lines:

```text
angle = 45.0000 deg
range = 40.7747 m
flight time = 2.8832 s
path length = 46.8010 m
apex = 10.1937 m
```

Every number is formatted with `:.4f`, the apex is the largest height in a sampled
trajectory, and the whole thing is returned rather than printed.

## The checks worth reading before you start

With `drag = 0` the answers are known in closed form, and the checks use all three:
flight time $2v\sin\theta/g$, range $v^{2}\sin 2\theta/g$, and path length
$\frac{v^{2}}{g}\left(\sin\theta + \cos^{2}\theta\,\ln\frac{1+\sin\theta}{\cos\theta}\right)$.
Your engine has to match them to eight digits, and then keep working when the drag is
switched on and no closed form exists.
''',
        "deliverables": [
            "`numkit.py` — the whole engine, importable with no output and no side effects",
            "`main.py` — a demo that solves for a launch angle and prints the report",
            "A vector RK4 that carries the four-component state through quadratic drag",
            "A flight time and range found by secant steps on the height, which is itself an ODE solve",
            "A path length from adaptive Simpson over the speed, refining where the speed changes fastest",
            "A least-squares quadratic fit whose 3 by 3 system goes through the pivoting solver",
        ],
        "constraints": [
            "Standard library only — `math` is enough, and nothing may import numpy or scipy",
            "`numkit.py` must define names only; importing it must print nothing",
            "No routine may mutate a list it was given, including the state passed to a derivative",
            "Every elimination uses partial pivoting; an unpivoted solve fails the checks outright",
            "The whole demo must finish in well under a second",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the three drag-free closed forms and the launch-angle round trip."},
            {"criterion": "Numerical judgement", "weight": 25,
             "evidence": "Pivoting in the solve, compensated summation in the normal equations, and a bracket around the flight time before the secant steps."},
            {"criterion": "Validation", "weight": 20,
             "evidence": "Negative drag, angles outside the open interval, unreachable targets, singular fits and short point lists all raise ValueError."},
            {"criterion": "Readability", "weight": 15,
             "evidence": "A docstring on every public routine, the launch state built in one place, and no debug prints left in numkit.py."},
        ],
        "hints": [
            "Build the launch state in one small helper and validate the angle and speed there. Four routines need it, and one place to refuse a bad angle is what stops the error message depending on which one was called.",
            "`flight_time` needs a bracket before it needs a root finder. The drag-free flight time is an upper bound whenever there is drag, so starting the secant iteration from half of it and just above it lands on the right crossing rather than on the launch.",
            "In `rk4_system` build each stage as a fresh list comprehension over the components. Updating the state in place would corrupt `k1` while `k2` is being computed, and the symptom is a method that looks right and measures as first order.",
            "`fit_quadratic` needs the sums of $x^0$ through $x^4$ and of $x^0y$ through $x^2y$. Compute the five power sums once into a list and index it as `powers[i + j]` — the normal matrix is then three lines.",
        ],
        "files": [
            {"name": "numkit.py", "content": r'''
import math

GRAVITY = 9.81


def kahan_sum(values):
    """Compensated summation: carry the bits each addition drops."""
    # your code here


def secant(f, x0, x1, tol=1e-10, max_iter=100):
    """The root of f, from two starting points and no derivative."""
    # your code here


def solve(a, b, tol=1e-14):
    """Ax = b by elimination with partial pivoting."""
    # your code here


def adaptive_simpson(f, a, b, tol=1e-10, max_depth=40):
    """Subdivide only where the halved estimates disagree."""
    # your code here


def rk4_system(f, t0, y0, t1, n):
    """Vector RK4. Returns [(t, [state...]), ...] of length n + 1."""
    # your code here


def derivative(drag):
    """f(t, [x, y, vx, vy]) for a projectile with quadratic drag."""
    # your code here


def state_at(t, angle, speed, drag=0.0, steps=200):
    """The state [x, y, vx, vy] at time t, launched from the origin."""
    # your code here


def flight_time(angle, speed, drag=0.0, steps=200):
    """When the height comes back to zero."""
    # your code here


def range_of(angle, speed, drag=0.0, steps=200):
    """How far downrange it lands."""
    # your code here


def launch_angle(target, speed, drag=0.0, steps=200):
    """The angle below 45 degrees whose range is the target."""
    # your code here


def arc_length(angle, speed, drag=0.0, steps=200, tol=1e-8):
    """The length of the path flown."""
    # your code here


def fit_quadratic(xs, ys):
    """Least squares c0 + c1 x + c2 x^2, through the normal equations."""
    # your code here


def report(angle, speed, drag=0.0, steps=200):
    """A five-line summary of one shot."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from numkit import launch_angle, report

speed = 20.0
drag = 0.02
target = 20.0

angle = launch_angle(target, speed, drag)
print(report(angle, speed, drag))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "numkit.py", "content": r'''
import math

GRAVITY = 9.81


def kahan_sum(values):
    """Compensated summation: carry the bits each addition drops."""
    total = 0.0
    lost = 0.0
    for v in values:
        y = v - lost
        t = total + y
        lost = (t - total) - y
        total = t
    return total


def secant(f, x0, x1, tol=1e-10, max_iter=100):
    """The root of f, from two starting points and no derivative."""
    x0, x1 = float(x0), float(x1)
    f0, f1 = f(x0), f(x1)
    for k in range(1, max_iter + 1):
        if f1 == f0:
            raise ValueError("the secant is horizontal")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        step = x2 - x1
        x0, f0 = x1, f1
        x1, f1 = x2, f(x2)
        if abs(step) <= tol:
            return x1
    raise ValueError("the secant iteration did not converge")


def solve(a, b, tol=1e-14):
    """Ax = b by elimination with partial pivoting."""
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("the matrix must be square and non-empty")
    if len(b) != n:
        raise ValueError("the right-hand side is the wrong length")
    u = [[float(v) for v in row] for row in a]
    rhs = [float(v) for v in b]
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(u[i][k]))
        if abs(u[p][k]) <= tol:
            raise ValueError("the matrix is singular to working precision")
        if p != k:
            u[k], u[p] = u[p], u[k]
            rhs[k], rhs[p] = rhs[p], rhs[k]
        for i in range(k + 1, n):
            factor = u[i][k] / u[k][k]
            for j in range(k, n):
                u[i][j] -= factor * u[k][j]
            rhs[i] -= factor * rhs[k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (rhs[i] - sum(u[i][j] * x[j] for j in range(i + 1, n))) / u[i][i]
    return x


def adaptive_simpson(f, a, b, tol=1e-10, max_depth=40):
    """Subdivide only where the halved estimates disagree."""
    if tol <= 0:
        raise ValueError("the tolerance must be positive")
    if b <= a:
        raise ValueError("b must be above a")

    def panel(fa, fm, fb, lo, hi):
        return (hi - lo) * (fa + 4.0 * fm + fb) / 6.0

    def step(lo, hi, fa, fm, fb, whole, tol, depth):
        mid = 0.5 * (lo + hi)
        lmid = 0.5 * (lo + mid)
        rmid = 0.5 * (mid + hi)
        flm = f(lmid)
        frm = f(rmid)
        left = panel(fa, flm, fm, lo, mid)
        right = panel(fm, frm, fb, mid, hi)
        if depth <= 0 or abs(left + right - whole) <= 15.0 * tol:
            return left + right + (left + right - whole) / 15.0
        return (step(lo, mid, fa, flm, fm, left, tol / 2, depth - 1) +
                step(mid, hi, fm, frm, fb, right, tol / 2, depth - 1))

    fa = f(a)
    fb = f(b)
    mid = 0.5 * (a + b)
    fm = f(mid)
    return step(a, b, fa, fm, fb, panel(fa, fm, fb, a, b), tol, max_depth)


def rk4_system(f, t0, y0, t1, n):
    """Vector RK4. Returns [(t, [state...]), ...] of length n + 1."""
    if n < 1:
        raise ValueError("n must be at least 1")
    if t1 <= t0:
        raise ValueError("t1 must be above t0")
    h = (t1 - t0) / n
    t = float(t0)
    y = [float(v) for v in y0]
    out = [(t, list(y))]
    for i in range(n):
        k1 = f(t, y)
        k2 = f(t + 0.5 * h, [y[j] + 0.5 * h * k1[j] for j in range(len(y))])
        k3 = f(t + 0.5 * h, [y[j] + 0.5 * h * k2[j] for j in range(len(y))])
        k4 = f(t + h, [y[j] + h * k3[j] for j in range(len(y))])
        y = [y[j] + h * (k1[j] + 2.0 * (k2[j] + k3[j]) + k4[j]) / 6.0
             for j in range(len(y))]
        t = t0 + (i + 1) * h
        out.append((t, list(y)))
    return out


def derivative(drag):
    """f(t, [x, y, vx, vy]) for a projectile with quadratic drag."""
    if drag < 0:
        raise ValueError("the drag coefficient cannot be negative")

    def f(t, s):
        vx, vy = s[2], s[3]
        speed = math.hypot(vx, vy)
        return [vx, vy, -drag * speed * vx, -GRAVITY - drag * speed * vy]

    return f


def _launch_state(angle, speed):
    """The state at t = 0, and the one place a bad shot is refused."""
    if not 0.0 < angle < 0.5 * math.pi:
        raise ValueError("the angle must be between 0 and pi/2")
    if speed <= 0:
        raise ValueError("the speed must be positive")
    return [0.0, 0.0, speed * math.cos(angle), speed * math.sin(angle)]


def state_at(t, angle, speed, drag=0.0, steps=200):
    """The state [x, y, vx, vy] at time t, launched from the origin."""
    start = _launch_state(angle, speed)
    if t <= 0.0:
        return list(start)
    return rk4_system(derivative(drag), 0.0, start, t, steps)[-1][1]


def flight_time(angle, speed, drag=0.0, steps=200):
    """When the height comes back to zero."""
    guess = 2.0 * speed * math.sin(angle) / GRAVITY
    height = lambda t: state_at(t, angle, speed, drag, steps)[1]
    return secant(height, 0.5 * guess, 1.05 * guess, tol=1e-12)


def range_of(angle, speed, drag=0.0, steps=200):
    """How far downrange it lands."""
    end = flight_time(angle, speed, drag, steps)
    return state_at(end, angle, speed, drag, steps)[0]


def launch_angle(target, speed, drag=0.0, steps=200):
    """The angle below 45 degrees whose range is the target."""
    if target <= 0:
        raise ValueError("the target must be downrange")
    best = range_of(0.25 * math.pi, speed, drag, steps)
    if target > best:
        raise ValueError("no angle reaches that target at this speed")
    miss = lambda a: range_of(a, speed, drag, steps) - target
    return secant(miss, 0.05, 0.7, tol=1e-12)


def arc_length(angle, speed, drag=0.0, steps=200, tol=1e-8):
    """The length of the path flown."""
    end = flight_time(angle, speed, drag, steps)

    def rate(t):
        s = state_at(t, angle, speed, drag, steps)
        return math.hypot(s[2], s[3])

    return adaptive_simpson(rate, 0.0, end, tol)


def fit_quadratic(xs, ys):
    """Least squares c0 + c1 x + c2 x^2, through the normal equations."""
    if len(xs) != len(ys):
        raise ValueError("xs and ys must be the same length")
    if len(xs) < 3:
        raise ValueError("a quadratic fit needs at least three points")
    powers = [kahan_sum([float(x) ** k for x in xs]) for k in range(5)]
    matrix = [[powers[i + j] for j in range(3)] for i in range(3)]
    rhs = [kahan_sum([float(ys[i]) * float(xs[i]) ** k for i in range(len(xs))])
           for k in range(3)]
    return solve(matrix, rhs)


def report(angle, speed, drag=0.0, steps=200):
    """A five-line summary of one shot."""
    end = flight_time(angle, speed, drag, steps)
    landing = state_at(end, angle, speed, drag, steps)
    samples = rk4_system(derivative(drag), 0.0, _launch_state(angle, speed), end, steps)
    apex = max(s[1] for _, s in samples)
    return "\n".join([
        "angle = {0:.4f} deg".format(math.degrees(angle)),
        "range = {0:.4f} m".format(landing[0]),
        "flight time = {0:.4f} s".format(end),
        "path length = {0:.4f} m".format(arc_length(angle, speed, drag, steps, tol=1e-8)),
        "apex = {0:.4f} m".format(apex),
    ])
'''},
        ],
        "tests": [
            {"name": "Compensated summation and the secant iteration", "code": r'''
import math as _m
from numkit import kahan_sum, secant
assert kahan_sum([]) == 0.0, "the empty sum is 0.0"
assert kahan_sum([0.1] * 100000) == 10000.0, \
    f"a hundred thousand tenths must come out exactly; got {kahan_sum([0.1] * 100000)!r}"
_naive = 0.0
for _v in [0.1] * 100000:
    _naive += _v
assert _naive != kahan_sum([0.1] * 100000), "the compensation has to change the answer"
assert abs(secant(lambda x: x * x - 2.0, 1.0, 2.0) - _m.sqrt(2.0)) < 1e-12, \
    "secant should find the square root of 2"
assert abs(secant(lambda x: _m.cos(x) - x, 0.0, 1.0) - 0.7390851332151607) < 1e-10, \
    "cos(x) = x has the root 0.739085..."
try:
    secant(lambda x: 3.0, 0.0, 1.0)
    assert False, "equal function values leave a horizontal secant and should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The solver pivots", "code": r'''
from numkit import solve
_x = solve([[1e-17, 1.0], [1.0, 1.0]], [1.0, 2.0])
assert abs(_x[0] - 1.0) < 1e-9 and abs(_x[1] - 1.0) < 1e-9, \
    f"solve gave {_x!r}; without a row swap this system returns [0.0, 1.0]"
_y = solve([[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]], [1.0, 2.0, 3.0])
for _i, _want in enumerate([6.0 / 41.0, -3.0 / 41.0, 13.0 / 41.0]):
    assert abs(_y[_i] - _want) < 1e-12, f"x[{_i}] is {_y[_i]!r}, expected {_want!r}"
_a = [[4.0, 3.0, 2.0], [1.0, 5.0, 7.0], [2.0, 2.0, 9.0]]
_before = [row[:] for row in _a]
solve(_a, [1.0, 2.0, 3.0])
assert _a == _before, "solve must not mutate the matrix it is given"
for _args in [([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0]), ([[1.0, 2.0], [3.0, 4.0]], [1.0]),
              ([[1.0, 2.0, 3.0]], [1.0]), ([], [])]:
    try:
        solve(*_args)
        assert False, f"solve{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Adaptive quadrature", "code": r'''
import math as _m
from numkit import adaptive_simpson
assert abs(adaptive_simpson(_m.exp, 0.0, 1.0, 1e-12) - (_m.e - 1.0)) < 1e-12, \
    "exp over [0, 1] should come out to the tolerance asked for"
assert abs(adaptive_simpson(_m.sin, 0.0, _m.pi, 1e-12) - 2.0) < 1e-11, \
    "sin over [0, pi] is 2"
_calls = [0]
def _runge(x):
    _calls[0] += 1
    return 1.0 / (1.0 + 25.0 * x * x)
assert abs(adaptive_simpson(_runge, -1.0, 1.0, 1e-9) - 0.4 * _m.atan(5.0)) < 1e-9, \
    "the peaked integrand should still reach the tolerance"
assert _calls[0] < 3000, f"that took {_calls[0]} evaluations; reuse the ones you have"
for _args in [(0.0, 1.0, 0.0), (1.0, 1.0, 1e-6), (2.0, 1.0, 1e-6)]:
    try:
        adaptive_simpson(_m.exp, _args[0], _args[1], _args[2])
        assert False, f"adaptive_simpson with {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Vector RK4 on a system with a known solution", "code": r'''
import math as _m
from numkit import rk4_system
_circle = lambda t, y: [y[1], -y[0]]
_path = rk4_system(_circle, 0.0, [1.0, 0.0], 2.0 * _m.pi, 400)
assert len(_path) == 401, f"n = 400 gives 401 points, got {len(_path)}"
assert _path[0][0] == 0.0 and _path[0][1] == [1.0, 0.0], f"the path starts at {_path[0]!r}"
assert abs(_path[-1][0] - 2.0 * _m.pi) < 1e-12, "the last time lands on t1"
assert abs(_path[-1][1][0] - 1.0) < 1e-8 and abs(_path[-1][1][1]) < 1e-8, \
    f"a full turn should return to [1, 0]; got {_path[-1][1]!r}"
_quarter = rk4_system(_circle, 0.0, [1.0, 0.0], 0.5 * _m.pi, 100)[-1][1]
assert abs(_quarter[0]) < 1e-8 and abs(_quarter[1] + 1.0) < 1e-8, \
    f"a quarter turn should reach [0, -1]; got {_quarter!r}"
_y0 = [1.0, 0.0]
rk4_system(_circle, 0.0, _y0, 1.0, 10)
assert _y0 == [1.0, 0.0], "rk4_system must not mutate the initial state"
for _args in [(0.0, 1.0, 0), (0.0, 1.0, -4), (1.0, 1.0, 10), (2.0, 1.0, 10)]:
    try:
        rk4_system(_circle, _args[0], [1.0, 0.0], _args[1], _args[2])
        assert False, f"rk4_system with (t0, t1, n) = {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Drag-free flight against the closed forms", "code": r'''
import math as _m
from numkit import flight_time, range_of
_g = 9.81
for _deg in (15.0, 30.0, 45.0, 60.0, 75.0):
    _a = _m.radians(_deg)
    _v = 20.0
    _t_want = 2.0 * _v * _m.sin(_a) / _g
    _r_want = _v * _v * _m.sin(2.0 * _a) / _g
    _t = flight_time(_a, _v)
    _r = range_of(_a, _v)
    assert abs(_t - _t_want) / _t_want < 1e-8, \
        f"at {_deg} degrees the flight time is {_t_want!r}; got {_t!r}"
    assert abs(_r - _r_want) / _r_want < 1e-8, \
        f"at {_deg} degrees the range is {_r_want!r}; got {_r!r}"
assert abs(range_of(_m.radians(45.0), 20.0) - 40.77471967380224) / 40.77471967380224 < 1e-9, \
    "the 45 degree range at 20 m/s is 40.7747196738"
for _args in [(0.0, 20.0), (0.5 * _m.pi, 20.0), (-0.3, 20.0), (0.5, 0.0), (0.5, -20.0)]:
    try:
        range_of(_args[0], _args[1])
        assert False, f"range_of{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Drag shortens the flight", "code": r'''
import math as _m
from numkit import range_of, derivative
_a = _m.radians(45.0)
_ranges = [range_of(_a, 20.0, _k) for _k in (0.0, 0.005, 0.01, 0.02, 0.05)]
for _i in range(1, len(_ranges)):
    assert _ranges[_i] < _ranges[_i - 1], \
        f"more drag must mean less range; got {_ranges!r}"
assert abs(_ranges[0] - 40.77471967380224) < 1e-6, "the first entry is the drag-free case"
assert 25.0 < _ranges[3] < 26.5, \
    f"at a drag of 0.02 the range is about 25.83; got {_ranges[3]!r}"
_f = derivative(0.0)
_s = [0.0, 0.0, 3.0, 4.0]
assert _f(0.0, _s) == [3.0, 4.0, 0.0, -9.81], \
    f"with no drag the accelerations are 0 and -g; got {_f(0.0, _s)!r}"
assert _s == [0.0, 0.0, 3.0, 4.0], "the derivative must not mutate the state"
_fd = derivative(0.1)
_got = _fd(0.0, [0.0, 0.0, 3.0, 4.0])
assert abs(_got[2] + 0.1 * 5.0 * 3.0) < 1e-12 and abs(_got[3] + 9.81 + 0.1 * 5.0 * 4.0) < 1e-12, \
    f"the drag term is -k|v|v componentwise; got {_got!r}"
try:
    derivative(-0.5)
    assert False, "a negative drag coefficient should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The launch angle round trip", "code": r'''
import math as _m
from numkit import launch_angle, range_of
_a = launch_angle(30.0, 20.0)
assert abs(_m.degrees(_a) - 23.68531408476106) < 1e-6, \
    f"the angle reaching 30 m at 20 m/s is 23.6853 degrees; got {_m.degrees(_a)!r}"
assert abs(range_of(_a, 20.0) - 30.0) < 1e-6, \
    f"and its range must come back as 30.0; got {range_of(_a, 20.0)!r}"
_b = launch_angle(20.0, 20.0, 0.02)
assert abs(range_of(_b, 20.0, 0.02) - 20.0) < 1e-6, \
    f"the round trip must hold with drag too; got {range_of(_b, 20.0, 0.02)!r}"
assert 0.0 < _b < 0.25 * _m.pi, f"the shallow solution is below 45 degrees; got {_b!r}"
for _args in [(100.0, 20.0), (0.0, 20.0), (-5.0, 20.0), (45.0, 20.0, 0.05)]:
    try:
        launch_angle(*_args)
        assert False, f"launch_angle{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Path length against the closed form", "code": r'''
import math as _m
from numkit import arc_length, range_of
_g = 9.81
for _deg in (30.0, 45.0, 60.0):
    _a = _m.radians(_deg)
    _v = 20.0
    _want = (_v * _v / _g) * (_m.sin(_a) +
                              _m.cos(_a) ** 2 * _m.log((1.0 + _m.sin(_a)) / _m.cos(_a)))
    _got = arc_length(_a, _v)
    assert abs(_got - _want) / _want < 1e-8, \
        f"at {_deg} degrees the path length is {_want!r}; got {_got!r}"
    assert _got > range_of(_a, _v), "the path flown is always longer than the ground covered"
assert abs(arc_length(_m.radians(45.0), 20.0) - 46.8009612516338) < 1e-6, \
    "the 45 degree path length at 20 m/s is 46.80096125"
assert arc_length(_m.radians(45.0), 20.0, 0.02) < arc_length(_m.radians(45.0), 20.0), \
    "drag shortens the path as well as the range"
'''},
            {"name": "The fit recovers a parabola exactly", "code": r'''
import math as _m
from numkit import fit_quadratic, rk4_system, derivative, flight_time
_a = _m.radians(45.0)
_v = 20.0
_c2 = -9.81 / (2.0 * _v * _v * _m.cos(_a) ** 2)
_c1 = _m.tan(_a)
_xs = [4.0 * _i for _i in range(11)]
_ys = [_c1 * _x + _c2 * _x * _x for _x in _xs]
_fit = fit_quadratic(_xs, _ys)
assert abs(_fit[0]) < 1e-9, f"the intercept should be 0; got {_fit[0]!r}"
assert abs(_fit[1] - _c1) < 1e-9, f"the slope should be {_c1!r}; got {_fit[1]!r}"
assert abs(_fit[2] - _c2) / abs(_c2) < 1e-9, f"the curvature should be {_c2!r}; got {_fit[2]!r}"
_end = flight_time(_a, _v)
_path = rk4_system(derivative(0.0), 0.0, [0.0, 0.0, _v * _m.cos(_a), _v * _m.sin(_a)], _end, 20)
_ft = fit_quadratic([_s[0] for _, _s in _path], [_s[1] for _, _s in _path])
assert abs(_ft[2] - _c2) / abs(_c2) < 1e-6, \
    f"a drag-free trajectory is a parabola, so the fit must recover {_c2!r}; got {_ft[2]!r}"
assert fit_quadratic([0.0, 1.0, 2.0], [1.0, 3.0, 5.0])[2] < 1e-9, \
    "three points on a line have no curvature"
for _args in [([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]), ([1.0, 2.0], [1.0, 2.0]),
              ([1.0, 2.0, 3.0], [1.0, 2.0])]:
    try:
        fit_quadratic(*_args)
        assert False, f"fit_quadratic{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "The report, and a library that stays a library", "code": r'''
import math as _m
import time as _t
from numkit import report
_src = open("numkit.py").read()
assert "print(" not in _src, "numkit.py defines routines; the printing belongs in main.py"
for _banned in ("numpy", "scipy"):
    assert _banned not in _src, f"numkit.py must not reach for {_banned}"
_rep = report(_m.radians(45.0), 20.0)
assert isinstance(_rep, str), "report returns a string, it does not print"
_lines = _rep.split("\n")
assert len(_lines) == 5, f"the report has five lines, got {len(_lines)}: {_lines!r}"
for _i, _prefix in enumerate(["angle = ", "range = ", "flight time = ",
                              "path length = ", "apex = "]):
    assert _lines[_i].startswith(_prefix), \
        f"line {_i + 1} should start with {_prefix!r}; got {_lines[_i]!r}"
assert _lines[0] == "angle = 45.0000 deg", f"got {_lines[0]!r}"
assert _lines[1] == "range = 40.7747 m", f"got {_lines[1]!r}"
assert _lines[2] == "flight time = 2.8832 s", f"got {_lines[2]!r}"
assert _lines[3] == "path length = 46.8010 m", f"got {_lines[3]!r}"
assert abs(float(_lines[4].split(" = ")[1].split()[0]) - 10.19367991845056) < 1e-2, \
    f"the apex should be about 10.1937; got {_lines[4]!r}"
_start = _t.time()
report(_m.radians(35.0), 25.0, 0.01)
assert _t.time() - _start < 5.0, "one report should take a small fraction of a second"
'''},
        ],
    },
}
