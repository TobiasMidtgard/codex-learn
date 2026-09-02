"""MA301 — Optimisation."""

COURSE = {
    "id": "MA301",
    "title": "Optimisation",
    "year": 3,
    "level": "Advanced",
    "prereqs": ["MA121", "MA112", "CS201"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 130,
    "icon": "∇",
    "summary": (
        "The mathematics every later course quietly assumes: why a flat spot is a "
        "minimum, how far a descent step may go, what curvature buys, what a "
        "constraint costs, and what to do when the answer has to be a whole number. "
        "Everything is written in plain Python — a backtracking line search, a "
        "Cholesky factorisation, an active-set solver, a simplex tableau and a "
        "branch-and-bound tree — so no library hides the arithmetic that decides "
        "whether a method converges."
    ),
    "outcomes": [
        "Test convexity from the chord and tangent inequalities, and read a curvature bracket off a Hessian",
        "Derive the descent lemma and the step-size limit it implies, and implement backtracking line search",
        "Explain why the condition number, not the dimension, governs how many gradient steps a problem needs",
        "Implement a damped Newton method with a modified Hessian, and demonstrate quadratic convergence",
        "State and check the KKT conditions, and read a multiplier as the price of a constraint",
        "Solve a linear program by simplex, extract its dual prices and verify strong duality",
        "Find integer optima by branch and bound, and show why rounding the relaxation fails",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone solver (60%).",
    "reading": [
        "Boyd & Vandenberghe, *Convex Optimization*, CUP 2004 — chapters 2-5 and 9-11",
        "Nocedal & Wright, *Numerical Optimization*, 2nd ed. — chapters 2-3, 6, 12 and 13",
        "Chvatal, *Linear Programming*, Freeman 1983 — chapters 2-5 and 13",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Convexity, and why a flat spot is enough",
            "summary": "The one property that turns a local search into a global answer.",
            "concepts": [
                "The chord test: the graph of a convex function never rises above a chord",
                "The first-order condition f(y) >= f(x) + grad f(x) . (y - x): the tangent underestimates",
                "A stationary point of a convex function is a global minimiser",
                "Second-order test: convex on a region exactly when the Hessian is positive semidefinite there",
                "Curvature at one point says nothing about convexity, which is a statement about every point",
                "Convex sublevel sets are weaker than convexity (quasiconvexity), and the converse fails",
                "The bracket m I <= H <= L I and the condition number kappa = L / m, which the next module spends",
            ],
            "read": [
                {
                    "title": "The chord test, and why a flat spot is enough",
                    "minutes": 13,
                    "body": r'''
You are walking down a hillside in fog thick enough that you can see your boots and
nothing else. You have an altimeter and you can feel which way the ground tilts. The
rule you follow is the only one available: step in whatever direction the ground falls
away, and stop when it stops falling. After an hour the ground under you is level in
every direction, the altimeter has settled, and you announce that you have reached the
bottom of the valley.

You may be wrong. You may be standing in a small hollow two hundred metres up the side,
with the real floor invisible below and behind you. Nothing measurable from where you
stand tells the two apart: a hollow and a valley floor both feel level, and both make
the altimeter stop moving. Every method in this course is a version of that walk, so
the first question is not how to walk faster. It is what has to be true about the
landscape before "level" is allowed to mean "lowest".

## The taut rope

Pick two points on the terrain and stretch a rope between them, straight through the
air. Walk the ground beneath it. On a landscape with a single valley the ground stays
under the rope the whole way. On a landscape with two hollows separated by a ridge, the
ridge pokes through.

That picture is the definition. Write $x$ and $y$ for the two points and let $t$ run
from $0$ to $1$ along the segment between them. The ground at the point $t$ of the way
is $f(tx + (1-t)y)$, and the rope at that same place is the corresponding blend of the
two endpoint heights. A function is **convex** when the ground never rises above the
rope, for every pair of points and every $t$:

$$f(tx + (1-t)y) \le t f(x) + (1-t) f(y)$$

Take the double well $f(x) = x^4 - 3x^2 + 1$ and the two points $-1.5$ and $1.5$. Both
sit at height $-0.6875$, so the rope is level at $-0.6875$ all the way across, and the
ground at the midpoint is $f(0) = 1$. The ridge stands $1.6875$ above the rope.

```python
def well(x):
    return x ** 4 - 3.0 * x ** 2 + 1.0

left, right = -1.5, 1.5
rope = 0.5 * well(left) + 0.5 * well(right)
print("rope   at the midpoint:", rope)
print("ground at the midpoint:", well(0.0))
print("ground above rope by  :", well(0.0) - rope)
```

One violated chord is a complete refutation. The chord test is a claim about every pair
of points at once, which is why it cannot be checked by looking at any single place.

## From ropes to gradients

The chord inequality is about heights. Descent is about slopes, so the inequality has
to be turned into one. Fix $x$ and $y$, and rewrite the chord point as $x$ plus a
fraction of the way towards $y$, which is the same segment written from the other end:

$$f(x + t(y-x)) \le f(x) + t\left(f(y) - f(x)\right)$$

Subtract $f(x)$ from both sides and divide by $t$, which is positive, so the inequality
survives:

$$\frac{f(x + t(y-x)) - f(x)}{t} \le f(y) - f(x)$$

The left-hand side is a difference quotient in the direction $y - x$. Let $t$ shrink to
zero and it becomes the directional derivative $\nabla f(x) \cdot (y - x)$. The
right-hand side never moved. So

$$f(y) \ge f(x) + \nabla f(x) \cdot (y - x)$$

for every $x$ and $y$. Read it as a picture again: the tangent plane at $x$ lies below
the whole graph. Not below it near $x$, which is what a Taylor expansion would give
you, but below it everywhere.

Now set $\nabla f(x) = 0$. The right-hand side collapses to $f(x)$, and the inequality
says $f(y) \ge f(x)$ for every $y$ in the domain. That is the sentence the fog needed.
On a convex landscape, level means lowest, and the walk was allowed to stop.

## The curvature version, on real numbers

Checking chords is a poor way to test a function you have a formula for. Restrict $f$
to a line through $x$ in the direction $d$ and call it $g(t) = f(x + td)$. A function of
one variable is convex exactly when its second derivative is non-negative, and the
chain rule gives $g''(t) = d \cdot H(x + td)\, d$ where $H$ is the matrix of second
partial derivatives. Requiring that for every direction $d$ is exactly the statement
that $H$ is positive semidefinite — every eigenvalue at or above zero.

Take the bowl this course will keep coming back to:

$$f(x,y) = 2x^2 + 2xy + 2y^2 - 6x - 6y$$

Its gradient is $(4x + 2y - 6,\; 2x + 4y - 6)$ and its Hessian is the constant matrix
with rows $(4, 2)$ and $(2, 4)$. For a symmetric matrix with rows $(a, b)$ and $(b, d)$
the eigenvalues solve $\lambda^2 - (a + d)\lambda + (ad - b^2) = 0$; here that is
$\lambda^2 - 8\lambda + 12 = 0$, so $\lambda = (8 \pm \sqrt{64 - 48})/2$, giving $2$ and
$6$. Both positive, everywhere, so the bowl is convex and its stationary point is its
minimiser. Solving $4x + 2y = 6$ and $2x + 4y = 6$ gives $x = y = 1$ and
$f(1,1) = -6$.

```python
import math

def f(x, y):
    return 2 * x ** 2 + 2 * x * y + 2 * y ** 2 - 6 * x - 6 * y

def grad(x, y):
    return (4 * x + 2 * y - 6, 2 * x + 4 * y - 6)

gx, gy = grad(1.0, 1.0)
print("gradient at (1, 1):", (gx, gy))
print("f(1, 1) =", f(1.0, 1.0))
print("tangent gap at (3, 0):",
      f(3.0, 0.0) - f(1.0, 1.0) - (gx * (3.0 - 1.0) + gy * (0.0 - 1.0)))
disc = math.sqrt(8.0 ** 2 - 4.0 * 12.0)
print("eigenvalues:", ((8.0 - disc) / 2.0, (8.0 + disc) / 2.0))
```

The tangent gap at $(3,0)$ comes out at $6$: the graph is six units above the tangent
plane there, and the gradient term contributes nothing because the gradient is zero.
The two eigenvalues $2$ and $6$ are worth a name. Write $m = 2$ for the smallest and
$L = 6$ for the largest; the bowl curves at least like $\tfrac{1}{2} m t^2$ along every
direction and at most like $\tfrac{1}{2} L t^2$. Their ratio $\kappa = L/m = 3$ is the
**condition number**, and it is the number that decides how many steps the next module
needs. Convexity decides whether the answer exists. The bracket decides what it costs.

## The mistake

The tempting error is to compute the Hessian at the point you happen to be standing on,
find it positive definite, and conclude that the function is convex. It is tempting for
two reasons: a positive definite Hessian at a stationary point genuinely is the
second-order sufficient condition for a *local* minimum, and the point you are standing
on is the only place the fog lets you measure.

The double well answers it. Its second derivative is $12x^2 - 6$, and at the right-hand
minimum $x = \sqrt{1.5}$ that is $12$, comfortably positive — while the function has two
separate minima and a maximum between them.

```python
def well(x):
    return x ** 4 - 3.0 * x ** 2 + 1.0

def second_derivative(x):
    return 12.0 * x ** 2 - 6.0

root = 1.5 ** 0.5
print("second derivative at the right minimum:", round(second_derivative(root), 9))
print("height there:", round(well(root), 6))
print("height at the mirror minimum:", round(well(-root), 6))
print("height at the ridge:", well(0.0))
```

Positive curvature at a point buys a neighbourhood and nothing more. Convexity is
quantified over the whole domain, and no local measurement can establish it.

A second confusion is worth heading off. The set of points whose height is at or below
some ceiling $c$ — every $x$ with $f(x) \le c$ — is called a sublevel set, and for a
convex $f$ every sublevel set is convex. The converse is false. Take
$g(x) = \sqrt{|x|}$: every sublevel
set is an interval around the origin, so all of them are convex, yet the chord from $0$
to $1$ has its midpoint rope at $0.5$ while the ground is at $\sqrt{0.5} \approx
0.7071$.

```python
import math

def g(x):
    return math.sqrt(abs(x))

print("ground at 0.5:", round(g(0.5), 6))
print("rope   at 0.5:", 0.5 * g(0.0) + 0.5 * g(1.0))
```

Functions with convex sublevel sets are called quasiconvex, and for them a stationary
point may be nothing of the kind — $g$ has a kink at its minimum rather than a
stationary point, and a quasiconvex function can be flat at a place that is not a
minimum at all.

## Where it stops holding

Convexity guarantees that a stationary point is a global minimum. It does not guarantee
that one exists: $e^x$ is convex on the whole line and decreases forever. It does not
guarantee uniqueness either — a convex function can have a flat-bottomed valley, and
every point of that floor is a minimiser satisfying the same first-order condition. It
says nothing about smoothness: $|x|$ passes the chord test but has no gradient at its
minimum, so the tangent inequality has to be restated with subgradients before it means
anything there.

And most of what you will meet later is not convex. A network trained in ML401 and a
planner scored in ROB520 are both riddled with saddle points and separate basins. What
survives is smaller but still load-bearing: near a strict minimum a smooth function is
convex, so the methods built on convexity are the right methods once you are close, and
the honest description of a non-convex search is that it finds a hollow and cannot tell
you which one.

## The lab

**The chord test and the curvature bracket** asks you to write six routines:
`chord_gap` and `convex_on_grid` for the rope picture, `tangent_gap` for the
first-order inequality, `eig_sym2` and `curvature_bracket` for the second-order one,
and `bisect_min`.

`bisect_min` is where convexity stops being a description and starts being an
algorithm. For a differentiable convex function the derivative is non-decreasing, so if
it is negative at one end of an interval and positive at the other, it crosses zero once
and the crossing is the minimiser. Bisecting that sign change halves the bracket every
step without ever evaluating $f$ itself. Note also what `convex_on_grid` can and cannot
do: sampling finitely many chords can produce a counterexample, and can never produce a
proof.
''',
                },
            ],
            "quiz": {
                "title": "Chords, tangents and what curvature is worth",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A search walks downhill and stops where the ground is level. On which functions is that stopping point guaranteed to be a global minimum?",
                        "opts": [
                            "Any function whose Hessian comes out positive definite at the point where the search stopped",
                            "Any function whose graph never rises above a chord drawn between two of its points",
                            "Any function that is differentiable at every point of the region being searched",
                            "Any function all of whose sublevel sets turn out to be convex sets",
                        ],
                        "a": 1,
                        "whys": [
                            r"Positive definiteness where you stand is the second-order sufficient condition for a *local* minimum, and it is the only curvature the fog lets you measure — which is exactly why it is tempting. The double well has curvature $+12$ at each of its two minima.",
                            r"The chord condition is quantified over every pair of points, which is what makes the conclusion global.",
                            r"Differentiability lets you talk about slopes; it says nothing about what happens between two distant points. Every polynomial is differentiable everywhere, and most of them have several hollows.",
                            r"Convex sublevel sets define quasiconvexity, which is strictly weaker. $\sqrt{|x|}$ has interval sublevel sets and fails the chord test, and a quasiconvex function can be flat somewhere that is not a minimum.",
                        ],
                        "why": r'''
The chord test is the property that transfers a local measurement into a global claim,
because it is a statement about every pair of points at once. Rearranging it and letting
the fraction shrink to zero gives $f(y) \ge f(x) + \nabla f(x) \cdot (y - x)$, and at a
stationary point the gradient term vanishes and leaves $f(y) \ge f(x)$ for every $y$.
Curvature measured at one point cannot do that work: it is a statement about a
neighbourhood, and the double well has positive curvature at both of its minima.
''',
                    },
                    {
                        "q": "For a convex $f$, why does $\\nabla f(x) = 0$ force $f(y) \\ge f(x)$ at every other point $y$?",
                        "opts": [
                            "Because the whole graph lies above the tangent at $x$, and a tangent with zero slope is the constant $f(x)$",
                            "Because a convex function has exactly one stationary point, so the one that was found has to be it",
                            "Because the second derivative of a convex function is strictly positive, making every stationary point a minimum",
                            "Because the gradient of a convex function increases, so having reached zero it can never return there",
                        ],
                        "a": 0,
                        "whys": [
                            r"The tangent inequality holds for every $y$, and with $\nabla f(x) = 0$ its right-hand side is the number $f(x)$.",
                            r"Uniqueness is not on offer. A convex function may have a flat-bottomed valley, and every point of that floor is stationary and minimal — the conclusion still holds, but not for this reason.",
                            r"Convexity gives a Hessian that is positive *semi*definite, so the second derivative may be zero, as it is for $x^4$ at the origin. Strict positivity would also only argue locally.",
                            r"The gradient of a convex function is non-decreasing rather than increasing, so it may sit at zero along a whole interval. And monotonicity of the gradient on its own does not compare $f(y)$ with $f(x)$.",
                        ],
                        "why": r'''
The first-order condition $f(y) \ge f(x) + \nabla f(x) \cdot (y - x)$ is not a local
approximation; it is an inequality valid for every pair of points, obtained by dividing
the chord inequality by $t$ and letting $t$ shrink. Setting the gradient to zero
collapses the right-hand side to $f(x)$ and the statement becomes global minimality
directly. Arguments through second derivatives or through uniqueness are either weaker
or false: the flat-bottomed case shows there can be infinitely many minimisers, and
$x^4$ shows the second derivative can vanish at one.
''',
                    },
                    {
                        "q": "You compute the Hessian of $f$ at your current point and every eigenvalue is positive. What follows?",
                        "opts": [
                            "That $f$ curves upwards in every direction from this point, and nothing about any other point",
                            "That $f$ is convex on the whole region, since a positive definite Hessian is the second-order test",
                            "That this point is a global minimiser, because positive curvature rules out any lower point",
                            "That the sublevel sets of $f$ are convex, which is the same requirement written another way",
                        ],
                        "a": 0,
                        "whys": [
                            r"A Hessian is evaluated at a point, so a claim about its eigenvalues is a claim about that point.",
                            r"The second-order test asks for a positive semidefinite Hessian *at every point of the region*. Checking one point and quantifying over all of them is the single most common convexity error, and it is tempting because one point is all the fog lets you measure.",
                            r"Positive curvature does not even make the point a minimiser — the gradient could be large, in which case you are on a rising slope. Add a zero gradient and you have a *local* minimum, which is still not global: the double well has two.",
                            r"Convex sublevel sets are a weaker property, not the same one, and in any case that too is a statement about the whole function rather than about one point's curvature.",
                        ],
                        "why": r'''
The Hessian is a local object. Positive eigenvalues at one point say that every straight
line through that point curves upwards as it passes, which buys a neighbourhood and
stops there. Convexity requires positive semidefiniteness at every point of the region,
and the gap between the two is not a technicality: $x^4 - 3x^2 + 1$ has second
derivative $12$ at $x = \sqrt{1.5}$ and again at $x = -\sqrt{1.5}$, two positively
curved minima with a ridge between them. If you want a global statement you have to
establish it globally, which is what `convex_on_grid` samples for and what an algebraic
argument about the Hessian can actually prove.
''',
                    },
                    {
                        "q": "Every sublevel set of $g(x) = \\sqrt{|x|}$ is an interval, so all of them are convex sets. Is $g$ a convex function?",
                        "opts": [
                            "Yes — convex sublevel sets at every height is one of the standard equivalent definitions",
                            "No — the chord from $0$ to $1$ sits at $0.5$ at its midpoint while the graph is at about $0.707$",
                            "Yes, on any interval avoiding the origin, and convexity is only ever claimed where a function is smooth",
                            "No — a function with a kink in it cannot be convex, because the chord test needs a derivative",
                        ],
                        "a": 1,
                        "whys": [
                            r"Convexity implies convex sublevel sets, and the temptation is to run the implication backwards. It does not run: the family of functions with convex sublevel sets is called quasiconvex and is strictly larger.",
                            r"One chord below the graph settles it, and this one misses by about $0.207$.",
                            r"Smoothness is not required anywhere in the chord test, and restricting to an interval away from the origin is changing the question rather than answering it — on $[0.1, 1]$ this function really is concave, not convex.",
                            r"Kinks are perfectly compatible with convexity: $|x|$ has one at its minimum and passes the chord test at every pair of points. The chord test never mentions derivatives.",
                        ],
                        "why": r'''
Sublevel sets of $\sqrt{|x|}$ are intervals centred on the origin, so every one of them
is convex, and yet the midpoint of the chord from $0$ to $1$ has the rope at $0.5$ and
the ground at $\sqrt{0.5} \approx 0.7071$ — the graph pokes through. Convexity implies
convex sublevel sets; the reverse implication fails, and the weaker property has its own
name, quasiconvexity. The practical consequence is that a quasiconvex function can be
flat at a place that is not a minimum, so the whole argument of this module — level
means lowest — is unavailable for it.
''',
                    },
                    {
                        "q": "A convex quadratic has Hessian eigenvalues $2$ and $6$. What does the ratio $\\kappa = 3$ tell you?",
                        "opts": [
                            "How much steeper the bowl is in its worst direction than in its best, which sets the cost of the search",
                            "How many gradient steps the search will need, since that count is the condition number multiplied by the dimension",
                            "How far the minimiser sits from the origin, measured along the most strongly curved direction",
                            "How accurate the quadratic model is, since a ratio near one means the Taylor series was exact",
                        ],
                        "a": 0,
                        "whys": [
                            r"It compares the curvature of the steepest direction with that of the shallowest, and that shape is what a descent method has to fight.",
                            r"The count does depend on $\kappa$, and this is the closest of the wrong answers — but not by multiplying it by the dimension. A million-variable problem with $\kappa = 1$ is solved in one step, and a two-variable problem with $\kappa = 10^6$ is not.",
                            r"Distance to the minimiser depends on the gradient at your starting point, not on the eigenvalues. Shifting the linear term moves the minimiser anywhere you like while leaving the Hessian, and therefore $\kappa$, untouched.",
                            r"For a quadratic the second-order model is exact regardless of $\kappa$, which is precisely why Newton's method lands in one step on any of them, well conditioned or not.",
                        ],
                        "why": r'''
The eigenvalues bracket the curvature: along every direction the function rises at least
like $\tfrac{1}{2}(2)t^2$ and at most like $\tfrac{1}{2}(6)t^2$. Their ratio measures how
far from round the bowl is, and roundness is what steepest descent needs, because the
negative gradient points at the minimiser only when every direction curves alike. The
next module derives the contraction factor $(\kappa-1)/(\kappa+1)$ per step, which is
$0.5$ here and $0.98$ for $\kappa = 100$. Dimension does not enter it, and neither does
the location of the minimiser.
''',
                    },
                    {
                        "q": "`convex_on_grid` samples chords across a grid of points and returns True. What has that established?",
                        "opts": [
                            "That the function is convex on that interval, since the chord test was run and every sampled chord passed",
                            "That no sampled chord dipped below the graph, which leaves the space between grid points untested",
                            "That the function is convex everywhere, because convexity is decided point by point anyway",
                            "That the function has at most one minimiser on the interval it was given to sample",
                        ],
                        "a": 1,
                        "whys": [
                            r"The implication runs the wrong way. Every chord of a convex function passing is true, but passing on finitely many sampled chords does not distinguish a convex function from one whose only violation happens to sit between samples.",
                            r"A finite sample can refute and cannot certify, which is the honest reading of a True.",
                            r"Convexity is emphatically not decided point by point — that is the error this module is built around — and a routine that only ever looks inside `[lo, hi]` could say nothing about the rest of the line even if it were.",
                            r"Uniqueness needs strict convexity, and even a genuinely convex function can have a whole interval of minimisers, as $\max(0, |x| - 1)$ does. The routine also never evaluates a minimiser at all.",
                        ],
                        "why": r'''
The routine reports a search for a counterexample that failed. A returned False is
conclusive, because a single chord below the graph refutes convexity outright; a
returned True is evidence and not proof, since the violation may live between two grid
points or at a $t$ that was not sampled. That asymmetry is worth being explicit about in
the lab, because it is the same asymmetry that separates testing from verification
everywhere else in the degree: the sampled chords are a test suite, and the algebraic
argument about the Hessian is the proof.
''',
                    },
                ],
            },
            "blanks": {
                "title": "The chord test, line by line",
                "minutes": 8,
                "lang": "python",
                "caption": "chord_gap and convex_on_grid — five holes, and one sign that decides everything",
                "brief": r'''
Two routines. The first measures how far the rope sits above the ground at one point of
one chord; the second walks a grid of chords looking for a single violation.

Nothing runs here. Filled in correctly, `convex_on_grid` returns True for $x^2$ and
False for $x^4 - 3x^2 + 1$, and every value it returns is a Python bool rather than a
number.
''',
                "listing": r'''
def chord_gap(f, x, y, t):
    """The rope height at t, minus the ground height at the same place."""
    inside = ___
    rope = ___
    return rope - f(inside)


def convex_on_grid(f, lo, hi, n=9):
    """False as soon as one sampled chord dips below the graph."""
    xs = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    for i in range(n):
        for j in range(___, n):
            for t in (0.25, 0.5, 0.75):
                if chord_gap(f, xs[i], xs[j], t) < ___:
                    return False
    return ___
''',
                "blanks": [
                    {
                        "prompt": "The point on the segment that is a fraction t of the way from y towards x.",
                        "hole": "?",
                        "opts": ["t * x + (1 - t) * y", "t * x + t * y", "t * y + (1 - t) * x", "(x + y) / 2"],
                        "a": 0,
                        "why": "At t = 0 this is y and at t = 1 it is x, and the two weights add to one at every point in between — which is what makes it a point of the segment rather than somewhere else entirely.",
                        "whys": [
                            "At t = 0 this is y and at t = 1 it is x, and the two weights add to one at every point in between — which is what makes it a point of the segment rather than somewhere else entirely.",
                            "The weights add to 2t rather than to 1, so this is the midpoint scaled by 2t. At t = 0 it collapses to the origin no matter where x and y are, and the routine would report the height of a point on neither the chord nor the segment.",
                            "This walks the segment from the other end: at t = 0 it sits at x while the rope above it is weighted towards y. Ground and rope are then measured at mirror-image points, and the gap for f(z) = z squared between 0 and 1 at t = 0.75 comes out at -0.3125 — a report that the parabola is not convex.",
                            "The midpoint is one point of the segment, so this is right for t = 0.5 and wrong for every other t. The grid sweep then tests one chord position three times over and never sees a violation that only shows away from the middle.",
                        ],
                    },
                    {
                        "prompt": "The height of the taut rope directly above that point.",
                        "hole": "?",
                        "opts": ["t * f(x) + (1 - t) * f(y)", "f(t * x) + f((1 - t) * y)",
                                 "t * f(x) + t * f(y)", "(f(x) + f(y)) / 2"],
                        "a": 0,
                        "why": "The rope is straight, so its height is the same blend of the two endpoint heights that the point itself is of the two endpoints — the identical weights t and 1 - t, applied to f(x) and f(y).",
                        "whys": [
                            "The rope is straight, so its height is the same blend of the two endpoint heights that the point itself is of the two endpoints — the identical weights t and 1 - t, applied to f(x) and f(y).",
                            "This evaluates f at two scaled inputs and adds the results, which is the function applied to shrunken points rather than a straight line above the segment. For f(z) = z squared it gives a curve, so the test would compare the graph against another copy of itself.",
                            "Both endpoints get weight t, so the weights add to 2t instead of 1. At t = 0.5 it halves the true rope height and every chord looks violated; at t = 1 it doubles it and none ever does.",
                            "A straight midpoint average is correct at t = 0.5 and wrong elsewhere, so the rope stops tilting. The gap then comes out negative on a perfectly convex function whenever t is near an end, and the routine reports a counterexample that is not there.",
                        ],
                    },
                    {
                        "prompt": "Where the inner loop should start so that each unordered pair of grid points is tried once.",
                        "hole": "?",
                        "opts": ["i + 1", "0", "i", "1"],
                        "a": 0,
                        "why": "Starting one past i gives each pair exactly once and never pairs a point with itself. The chord test is symmetric in its two endpoints, so the other ordering would add work without adding information.",
                        "whys": [
                            "Starting one past i gives each pair exactly once and never pairs a point with itself. The chord test is symmetric in its two endpoints, so the other ordering would add work without adding information.",
                            "This tries every ordered pair, which doubles the work and includes the degenerate chords where both endpoints are the same point. Those contribute a gap of exactly zero, so they cost time without ever deciding anything.",
                            "This includes the case where the two endpoints coincide. The chord then has no length, the gap is zero, and with a strict comparison against a negative threshold it never fires — so the only effect is n wasted evaluations per outer step.",
                            "A fixed start skips no work at all when i is large and skips genuine pairs when i is 0, so the chord from the first grid point to the second is never tested. A violation living at the left-hand end goes unseen.",
                        ],
                    },
                    {
                        "prompt": "The threshold the gap has to fall below before the chord counts as violated.",
                        "hole": "?",
                        "opts": ["-1e-9", "0.0", "1e-9", "-1.0"],
                        "a": 0,
                        "why": "A small negative tolerance is what lets an exactly-linear stretch survive. For f(z) = |z| the gap is algebraically zero on chords that do not straddle the kink, and rounding makes it a few units in the last place either side of zero.",
                        "whys": [
                            "A small negative tolerance is what lets an exactly-linear stretch survive. For f(z) = |z| the gap is algebraically zero on chords that do not straddle the kink, and rounding makes it a few units in the last place either side of zero.",
                            "An exact comparison against zero condemns any function with a straight stretch in it. The absolute value is convex and its gap on a chord inside one arm is zero in exact arithmetic and about -1e-16 in floating point, so this reports it as not convex.",
                            "A positive threshold means the gap has to be genuinely positive before the chord passes, so every flat or linear region is reported as a violation — and the routine now also rejects chords that miss by less than a nanometre in the right direction.",
                            "A tolerance this loose swallows real violations. The double well's midpoint chord misses by 1.6875, which this still catches, but a shallower ridge of height 0.5 passes unnoticed and the function is reported convex.",
                        ],
                    },
                    {
                        "prompt": "What to return when the sweep finishes without finding a violation.",
                        "hole": "?",
                        "opts": ["True", "False", "None", "chord_gap(f, lo, hi, 0.5)"],
                        "a": 0,
                        "why": "Reaching the end means no sampled chord dipped below the graph, which is the most the routine can report — evidence rather than proof, but a genuine result and a bool.",
                        "whys": [
                            "Reaching the end means no sampled chord dipped below the graph, which is the most the routine can report — evidence rather than proof, but a genuine result and a bool.",
                            "This reports every function as non-convex, including the ones that passed every chord, so the early return above becomes dead code and the routine answers the same way whatever it is given.",
                            "A bare fall-off-the-end returns None, which is falsy, so the caller sees a rejection and no error was raised to say why. It is the failure that a test written as an equality against True catches and one written as a truthiness check does not.",
                            "One extra chord, from one end of the interval to the other, decides nothing that the sweep has not already decided, and returning a float where a bool is expected means the caller cannot tell a large positive gap from a verdict.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "The chord test and the curvature bracket",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Six routines in `main.py`, all working on plain floats and plain lists. Nothing here
imports anything except `math`.

## The rope picture

- `chord_gap(f, x, y, t)` — the rope height at the point $t$ of the way from `y` to
  `x`, minus the ground height there. Non-negative on a convex chord. A `t` outside
  $[0,1]$ raises `ValueError`, because there is no chord out there to measure.
- `convex_on_grid(f, lo, hi, n=9)` — `n` evenly spaced points across `[lo, hi]`, every
  unordered pair, `t` in `(0.25, 0.5, 0.75)`. Returns `False` on the first gap below
  `-1e-9`, and `True` if none is found. `n < 2` or `hi <= lo` raises `ValueError`.

## The tangent picture

- `tangent_gap(f, df, x, y)` — `f(y) - f(x) - df(x) * (y - x)`, which is non-negative
  for every pair exactly when `f` is convex.

## Curvature

- `eig_sym2(h)` — the two eigenvalues of a symmetric `2x2` given as a list of two
  rows, smallest first. Use the trace and determinant rather than a library. A matrix
  whose off-diagonal entries differ by more than `1e-12` is not a Hessian, and raises
  `ValueError`.
- `curvature_bracket(h)` — `(m, L, kappa)` with `kappa = L / m`, or `math.inf` when
  `m <= 0`, because an indefinite Hessian has no condition number worth quoting.

## And an algorithm

- `bisect_min(df, lo, hi, tol=1e-12)` — the minimiser of a convex differentiable
  function, found by bisecting the sign change of `df`. Requires `df(lo) <= 0 <=
  df(hi)`; anything else raises `ValueError`, as does `hi <= lo`. Halve until the
  bracket is no wider than `tol` and return its midpoint.

```text
chord_gap(lambda z: z*z, -1.0, 3.0, 0.5)  ->  4.0
eig_sym2([[4.0, 2.0], [2.0, 4.0]])        ->  (2.0, 6.0)
curvature_bracket([[4.0, 2.0], [2.0, 4.0]])  ->  (2.0, 6.0, 3.0)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def chord_gap(f, x, y, t):
    """Rope height at t, minus ground height at the same point of the chord."""
    # your code here


def convex_on_grid(f, lo, hi, n=9):
    """Sample chords across a grid; False on the first one that dips below."""
    # your code here


def tangent_gap(f, df, x, y):
    """f(y) - f(x) - df(x) * (y - x)."""
    # your code here


def eig_sym2(h):
    """The two eigenvalues of a symmetric 2x2, smallest first."""
    # your code here


def curvature_bracket(h):
    """(m, L, kappa) for a symmetric 2x2 Hessian."""
    # your code here


def bisect_min(df, lo, hi, tol=1e-12):
    """Bisect the sign change of a non-decreasing derivative."""
    # your code here


print("curvature bracket:", curvature_bracket([[4.0, 2.0], [2.0, 4.0]]))
print("minimiser of (x-2)^2:", bisect_min(lambda z: 2.0 * z - 4.0, -10.0, 10.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def chord_gap(f, x, y, t):
    """Rope height at t, minus ground height at the same point of the chord."""
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must lie in [0, 1] to name a point of the chord")
    inside = t * x + (1.0 - t) * y
    rope = t * f(x) + (1.0 - t) * f(y)
    return rope - f(inside)


def convex_on_grid(f, lo, hi, n=9):
    """Sample chords across a grid; False on the first one that dips below."""
    if n < 2:
        raise ValueError("need at least two grid points to have a chord")
    if hi <= lo:
        raise ValueError("hi must be greater than lo")
    xs = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            for t in (0.25, 0.5, 0.75):
                if chord_gap(f, xs[i], xs[j], t) < -1e-9:
                    return False
    return True


def tangent_gap(f, df, x, y):
    """f(y) - f(x) - df(x) * (y - x)."""
    return f(y) - f(x) - df(x) * (y - x)


def eig_sym2(h):
    """The two eigenvalues of a symmetric 2x2, smallest first."""
    a, b = float(h[0][0]), float(h[0][1])
    c, d = float(h[1][0]), float(h[1][1])
    if abs(b - c) > 1e-12:
        raise ValueError("a Hessian is symmetric; this matrix is not")
    trace = a + d
    spread = math.sqrt((a - d) ** 2 + 4.0 * b * c)
    return ((trace - spread) / 2.0, (trace + spread) / 2.0)


def curvature_bracket(h):
    """(m, L, kappa) for a symmetric 2x2 Hessian."""
    low, high = eig_sym2(h)
    kappa = high / low if low > 0.0 else math.inf
    return (low, high, kappa)


def bisect_min(df, lo, hi, tol=1e-12):
    """Bisect the sign change of a non-decreasing derivative."""
    if hi <= lo:
        raise ValueError("hi must be greater than lo")
    left, right = float(lo), float(hi)
    if df(left) > 0.0 or df(right) < 0.0:
        raise ValueError("the derivative does not change sign across the bracket")
    while right - left > tol:
        middle = 0.5 * (left + right)
        if df(middle) <= 0.0:
            left = middle
        else:
            right = middle
    return 0.5 * (left + right)


print("curvature bracket:", curvature_bracket([[4.0, 2.0], [2.0, 4.0]]))
print("minimiser of (x-2)^2:", bisect_min(lambda z: 2.0 * z - 4.0, -10.0, 10.0))
'''}],
                "hints": [
                    "`chord_gap` needs the same weights in two places: `t * x + (1 - t) * y` for the point and `t * f(x) + (1 - t) * f(y)` for the rope. Writing one line under the other makes the symmetry hard to get wrong.",
                    "For a symmetric 2x2 with rows (a, b) and (b, d), the eigenvalues are `(trace +/- sqrt((a - d)**2 + 4*b*b)) / 2`. The discriminant is a sum of squares, so it can never be negative and no complex case exists.",
                    "`curvature_bracket` should return `math.inf` rather than raising when the smallest eigenvalue is at or below zero — an indefinite Hessian is a fact about the function, not a caller error.",
                    "`bisect_min` never evaluates `f`. Convexity makes `df` non-decreasing, so `df(mid) <= 0` means the crossing is to the right of `mid` and the left end moves up to it.",
                ],
                "tests": [
                    {"name": "One chord, measured", "code": r'''
_sq = lambda z: z * z
_got = chord_gap(_sq, -1.0, 3.0, 0.5)
assert abs(_got - 4.0) < 1e-12, f"chord_gap on x^2 between -1 and 3 gave {_got!r}, expected 4.0"
_well = lambda z: z ** 4 - 3.0 * z ** 2 + 1.0
_got = chord_gap(_well, -1.5, 1.5, 0.5)
assert abs(_got + 1.6875) < 1e-12, f"chord_gap on the double well gave {_got!r}, expected -1.6875"
assert abs(chord_gap(_sq, -1.0, 3.0, 0.0)) < 1e-12, "at t = 0 the chord point is y, so the gap is 0"
assert abs(chord_gap(_sq, -1.0, 3.0, 1.0)) < 1e-12, "at t = 1 the chord point is x, so the gap is 0"
'''},
                    {"name": "A t off the chord is refused", "code": r'''
for _t in (-0.1, 1.5, 2.0):
    try:
        chord_gap(lambda z: z * z, 0.0, 1.0, _t)
        assert False, f"t = {_t} names no point of the chord; chord_gap should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The grid sweep finds the counterexample", "code": r'''
import math as _m
assert convex_on_grid(lambda z: z * z, -3.0, 3.0) is True, "x^2 is convex; the sweep should return True"
assert convex_on_grid(abs, -3.0, 3.0) is True, "|x| is convex despite the kink; the sweep should return True"
assert convex_on_grid(_m.exp, -2.0, 2.0) is True, "exp is convex; the sweep should return True"
assert convex_on_grid(lambda z: z ** 4 - 3.0 * z ** 2 + 1.0, -2.0, 2.0) is False, \
    "the double well has a ridge between two hollows and should be reported non-convex"
assert convex_on_grid(lambda z: _m.sqrt(abs(z)), -1.0, 1.0) is False, \
    "sqrt(|x|) is quasiconvex but not convex, and a sampled chord should catch it"
'''},
                    {"name": "A grid needs two points and a positive width", "code": r'''
for _args in [(0.0, 1.0, 1), (0.0, 1.0, 0), (1.0, 1.0, 5), (2.0, 1.0, 5)]:
    try:
        convex_on_grid(lambda z: z * z, *_args)
        assert False, f"convex_on_grid with (lo, hi, n) = {_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The tangent underestimates, and where it does not", "code": r'''
_sq = lambda z: z * z
_dsq = lambda z: 2.0 * z
_got = tangent_gap(_sq, _dsq, 1.0, 4.0)
assert abs(_got - 9.0) < 1e-12, f"tangent_gap on x^2 from 1 to 4 gave {_got!r}, expected 9.0"
assert abs(tangent_gap(_sq, _dsq, 2.0, 2.0)) < 1e-12, "the gap at y = x is exactly 0"
_well = lambda z: z ** 4 - 3.0 * z ** 2 + 1.0
_dwell = lambda z: 4.0 * z ** 3 - 6.0 * z
_got = tangent_gap(_well, _dwell, 0.0, 1.0)
assert abs(_got + 2.0) < 1e-12, \
    f"on the double well the tangent at 0 sits above the graph; gap gave {_got!r}, expected -2.0"
'''},
                    {"name": "Eigenvalues of a symmetric 2x2", "code": r'''
_lo, _hi = eig_sym2([[4.0, 2.0], [2.0, 4.0]])
assert abs(_lo - 2.0) < 1e-12 and abs(_hi - 6.0) < 1e-12, \
    f"eig_sym2 of [[4, 2], [2, 4]] gave {(_lo, _hi)!r}, expected (2.0, 6.0)"
_lo, _hi = eig_sym2([[1.0, 2.0], [2.0, 1.0]])
assert abs(_lo + 1.0) < 1e-12 and abs(_hi - 3.0) < 1e-12, \
    f"eig_sym2 of [[1, 2], [2, 1]] gave {(_lo, _hi)!r}, expected (-1.0, 3.0)"
_lo, _hi = eig_sym2([[5.0, 0.0], [0.0, 5.0]])
assert abs(_lo - 5.0) < 1e-12 and abs(_hi - 5.0) < 1e-12, \
    f"a multiple of the identity has a repeated eigenvalue; got {(_lo, _hi)!r}"
try:
    eig_sym2([[1.0, 2.0], [3.0, 4.0]])
    assert False, "a non-symmetric matrix is not a Hessian and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The curvature bracket and its condition number", "code": r'''
import math as _m
_low, _high, _kappa = curvature_bracket([[4.0, 2.0], [2.0, 4.0]])
assert abs(_low - 2.0) < 1e-12 and abs(_high - 6.0) < 1e-12 and abs(_kappa - 3.0) < 1e-12, \
    f"curvature_bracket of [[4, 2], [2, 4]] gave {(_low, _high, _kappa)!r}, expected (2.0, 6.0, 3.0)"
_low, _high, _kappa = curvature_bracket([[1.0, 2.0], [2.0, 1.0]])
assert _low < 0.0, f"[[1, 2], [2, 1]] is indefinite; smallest eigenvalue came out {_low!r}"
assert _kappa == _m.inf, f"an indefinite Hessian has no finite condition number; got {_kappa!r}"
_low, _high, _kappa = curvature_bracket([[3.0, 0.0], [0.0, 3.0]])
assert abs(_kappa - 1.0) < 1e-12, f"a round bowl has condition number 1; got {_kappa!r}"
'''},
                    {"name": "Bisecting a non-decreasing derivative", "code": r'''
import math as _m
_got = bisect_min(lambda z: 2.0 * z - 4.0, -10.0, 10.0)
assert abs(_got - 2.0) < 1e-9, f"the minimiser of (x-2)^2 is 2.0; bisect_min gave {_got!r}"
_got = bisect_min(lambda z: 4.0 * z ** 3, -1.0, 2.0)
assert abs(_got) < 1e-6, f"x^4 bottoms out at 0; bisect_min gave {_got!r}"
_got = bisect_min(lambda z: _m.exp(z) - 1.0, -5.0, 5.0)
assert abs(_got) < 1e-9, f"exp(x) - x is minimised at 0; bisect_min gave {_got!r}"
for _args in [(lambda z: 2.0 * z - 4.0, 3.0, 10.0),
              (lambda z: 2.0 * z - 4.0, -10.0, -3.0),
              (lambda z: 2.0 * z - 4.0, 5.0, 1.0)]:
    try:
        bisect_min(*_args)
        assert False, "a bracket with no sign change in it should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The script reports what it computed", "code": r'''
_lines = _out.strip().split("\n")
assert len(_lines) == 2, f"main.py should print two lines; it printed {len(_lines)}:\n{_out}"
assert _lines[0] == "curvature bracket: (2.0, 6.0, 3.0)", \
    f"the first line was {_lines[0]!r}, expected 'curvature bracket: (2.0, 6.0, 3.0)'"
assert _lines[1].startswith("minimiser of (x-2)^2: 2.0000000000"), \
    f"the second line was {_lines[1]!r}; bisection to 1e-12 should land on 2.0000000000..."
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Gradient descent, and the step that survives",
            "summary": "The steepest direction, how far you may walk along it, and what the shape of the bowl costs.",
            "concepts": [
                "The negative gradient is steepest descent in the Euclidean norm, and in no other",
                "The descent lemma f(x + p) <= f(x) + g . p + (L/2)|p|^2, and the guaranteed decrease it gives",
                "A fixed step converges on a quadratic exactly when t < 2 / L",
                "The best fixed step is 2 / (m + L), contracting by (kappa - 1) / (kappa + 1) per iteration",
                "Zig-zagging is what an ill-conditioned bowl does to a method that only knows slopes",
                "Backtracking line search: shrink t until the Armijo sufficient-decrease test passes",
                "A step size is a property of the problem's scaling, not of the algorithm",
            ],
            "read": [
                {
                    "title": "Downhill is a direction, not a distance",
                    "minutes": 13,
                    "body": r'''
A cost model with two knobs. The first is a clearance measured in centimetres; the
second is a clearance on a different part that somebody recorded in millimetres, and
nobody reconciled the units before the model was fitted. What came out was

$$f(x,y) = \tfrac{1}{2}\left(x^2 + 100 y^2\right)$$

with its minimum at the origin. Stand at $(1,1)$. The gradient is $(x, 100y) = (1,
100)$, a hundred times steeper in $y$ than in $x$, entirely because of the unit choice.
Steepest descent tells you to walk along $-(1,100)$, which is within a degree of
straight down the $y$ axis. The minimiser, from where you are standing, is in the
direction $(-1,-1)$. Those two directions are more than forty degrees apart.

```python
import math

gx, gy = 1.0, 100.0
tx, ty = -1.0, -1.0
cosine = (-gx * tx - gy * ty) / (math.hypot(gx, gy) * math.hypot(tx, ty))
print("angle between the descent direction and the way home:",
      round(math.degrees(math.acos(cosine)), 3), "degrees")
```

That gap is the subject of this module. The direction is not wrong — it is the best
direction available to anything that knows only slopes — but it is not the direction of
the answer, and the difference between the two is what every convergence rate here is
measuring.

## Why the negative gradient is the steepest direction

Walk a short distance $t$ in a direction $d$ of unit length. The first-order expansion
is $f(x + td) = f(x) + t\,\nabla f(x) \cdot d + o(t)$, so the initial rate of change is
the dot product. To fall as fast as possible you want that dot product as negative as
possible, and the Cauchy-Schwarz inequality says $\nabla f(x) \cdot d \ge
-|\nabla f(x)|\,|d|$, with equality exactly when $d$ points opposite to the gradient.

Read the derivation again and notice what it assumed: "unit length" and "as negative as
possible" were both measured in the ordinary Euclidean norm. Steepest descent is
steepest with respect to a ruler, and if you rescale $y$ the ruler changes and so does
the answer. The direction is a fact about the function and the units together, which is
already a warning about the paragraph on scaling below.

## How far along it you may walk

The direction says nothing about distance, and distance is where the method lives or
dies. Suppose the gradient does not change faster than some rate $L$ — the curvature is
bounded above by $L$ in every direction. Then the function sits below a quadratic:

$$f(x + p) \le f(x) + \nabla f(x) \cdot p + \frac{L}{2}|p|^2$$

Put in the step you are about to take, $p = -t g$ with $g = \nabla f(x)$:

$$f(x^{+}) \le f(x) - t|g|^2 + \frac{L t^2}{2}|g|^2 = f(x) - t\left(1 - \frac{Lt}{2}\right)|g|^2$$

The bracket is positive exactly while $t < 2/L$, and the right-hand side is smallest at
$t = 1/L$, where the guaranteed decrease is $|g|^2/(2L)$. So a step limit falls out of
the curvature bound, along with the observation that the guarantee is proportional to
the squared gradient — which is why progress collapses as the gradient does.

On a quadratic you can see the same limit exactly rather than as a bound. With
$f = \tfrac{1}{2}x \cdot Hx$ the gradient is $Hx$ and one step is
$x^{+} = (I - tH)x$. Along an eigenvector with eigenvalue $\lambda$ that multiplies the
coordinate by $1 - t\lambda$, so every coordinate shrinks exactly when
$|1 - t\lambda| < 1$ for every eigenvalue, which is $t < 2/L$. Here $L = 100$ and the
limit is $t < 0.02$. The steepest direction sets the speed limit; the shallowest sets
the distance still to travel.

```python
def f(x, y):
    return 0.5 * (x * x + 100.0 * y * y)

x, y = 1.0, 1.0
for k in range(5):
    print(f"k={k}  x={x:+.6f}  y={y:+.6f}  f={f(x, y):.6f}")
    x, y = x - 0.019 * x, y - 0.019 * 100.0 * y
```

At $t = 0.019$, safely under the limit, $y$ is multiplied by $1 - 1.9 = -0.9$ every
step: it flips sign and shrinks by a tenth. Meanwhile $x$ is multiplied by $0.981$ and
has moved from $1.0$ to $0.926$ after four steps. The path crosses and recrosses the
valley while creeping along it, and the coordinate that has to be waited for is the one
that was never the problem.

## What the best fixed step costs

Every eigenvalue lies in $[m, L]$, so the worst contraction over one step is the largest
$|1 - t\lambda|$ across that interval, and the largest is attained at one end or the
other. As $t$ grows, $1 - tm$ falls and $t L - 1$ rises, so the best $t$ is the one that
makes them equal: $1 - tm = tL - 1$ gives $t = 2/(m+L)$, and the common value is

$$\frac{L - m}{L + m} = \frac{\kappa - 1}{\kappa + 1}$$

For $\kappa = 100$ that factor is $0.980198$, and gaining one decimal digit takes
$\ln 10 / \ln(1/0.980198) \approx 115$ iterations. For the $\kappa = 3$ bowl of module 1
the factor is $0.5$ and a digit costs about $3.3$ iterations. Same code, same dimension,
same starting distance: thirty-five times the work, and the only thing that differs is
the shape of the bowl. This is why module 1 spent its last section on the curvature
bracket.

## When you do not know L

You almost never do. Backtracking replaces the constant with an experiment. Start at
$t = 1$, and accept the step when it delivers a decrease at least a fixed fraction $c$
of what the slope predicted:

$$f(x + td) \le f(x) + c\,t\,\nabla f(x) \cdot d$$

with $c$ small, $10^{-4}$ in this course. Otherwise halve $t$ and try again. That the
loop terminates is the same expansion as before: $f(x + td) - f(x) - c t\,g \cdot d =
(1 - c)\,t\,g \cdot d + o(t)$, and $g \cdot d$ is negative for a descent direction while
$1 - c$ is positive, so for small enough $t$ the whole expression is negative and the
test passes.

The function $x^4$ shows why this matters. Its curvature is $12x^2$, which has no upper
bound at all, so no fixed step is short enough everywhere. From $x = 10$ with a step of
$0.01$:

```python
x = 10.0
for k in range(4):
    print(f"k={k}  x={x:+.6g}  f={x ** 4:.6g}")
    x = x - 0.01 * 4.0 * x ** 3
```

Ten, then minus thirty, then one thousand and fifty, then minus forty-six million. Now
the same starting point with the ledger a backtracking search would write:

```python
base = 10.0 ** 4
slope = -(4.0 * 10.0 ** 3) ** 2
t = 1.0
while True:
    trial = 10.0 - t * 4.0 * 10.0 ** 3
    target = base + 1e-4 * t * slope
    ok = trial ** 4 <= target
    print(f"t={t:.8f}  x={trial:+.6g}  f={trial ** 4:.6g}  "
          f"target={target:.6g}  {'accept' if ok else 'reject'}")
    if ok:
        break
    t *= 0.5
```

Nine trials, each halving the overshoot, and the first accepted step is
$t = 0.00390625$. It lands at $x = -5.625$ with the objective down from $10000$ to
$1001$ — an overshoot past the minimum, and a perfectly good iteration, because Armijo
asks for sufficient decrease and not for monotone approach. From there the same run
reaches $x \approx 0.029$ in $147$ iterations at a gradient tolerance of $10^{-4}$: slow,
because $x^4$ is nearly flat at the bottom and a method that reads only the gradient has
almost nothing to read.

## The mistake

Two of them, and they are the same mistake seen from different sides.

The first is hearing "the gradient points at the minimum". It does not. It points across
the level set, which aims at the minimiser only when every direction curves alike — a
round bowl. The forty-four degree error computed at the top of this reading is what a
condition number of $100$ does to that intuition, and the intuition survives because
every hand-drawn example in every textbook is drawn round.

The second is treating the step size as a setting of the algorithm. Rescale $y$ by a
factor of a thousand and the same problem, the same code and the same starting point
need a step a million times smaller. A learning rate that worked on one dataset and
diverges on the next has usually not met a harder problem; it has met a differently
scaled one. That is the whole argument for standardising features before fitting, which
ML401 makes again from the other end.

## Where it stops holding

The descent lemma needs a finite curvature bound over everywhere the walk goes, and
$x^4$ has none. It needs a gradient at all, and $|x|$ has none at its minimum. And the
line search stops working some way before the mathematics does. Once $f(x)$ and
$f(x + td)$ round to the same double, the Armijo test is comparing a number against
itself minus a quantity below the resolution of that number, so every trial is rejected
until $t$ is small enough that the target rounds back up to $f(x)$ — at which point a
step that moves nothing is accepted. Ask the lab's `gradient_descent` for a gradient
tolerance of $10^{-9}$ on the module 1 bowl and it will spend thousands of iterations
doing exactly that, stalled at a gradient of about $10^{-8}$. A tolerance has to be one
the function values can still support.

Everything here also still runs on a landscape that is not convex, and still means only
what module 1 said it means: a descent method finds a hollow, and cannot tell you which.

## The lab

**Descent directions and the step that survives** asks for `dot`, `norm`,
`numeric_gradient`, `armijo_step` and `gradient_descent`. The last takes `step=None` for
backtracking or a float for a fixed step, so one routine produces both of the traces
above, and the divergence at $t = 0.021$ is a `ValueError` rather than a run of `nan`
values — a method that has lost control should say so rather than return a number.
`numeric_gradient` uses central differences, which will be the only gradient available
in the capstone when nobody has written the derivative down.
''',
                },
            ],
            "quiz": {
                "title": "Directions, step sizes and the shape of the bowl",
                "minutes": 9,
                "questions": [
                    {
                        "q": "Standing at $(1,1)$ on $f(x,y) = (x^2 + 100y^2)/2$, the negative gradient points more than forty degrees away from the minimiser at the origin. What has gone wrong?",
                        "opts": [
                            "Nothing — steepest descent is steepest under the Euclidean ruler, which is not the same as aiming at the answer",
                            "The gradient was computed with the wrong sign, since the true descent direction always aims at the minimiser",
                            "The starting point is too far out, and the two directions come back into agreement once the iterate is close enough",
                            "The function is not convex there, so the first-order expansion that defines the gradient does not apply",
                        ],
                        "a": 0,
                        "whys": [
                            r"Fastest initial decrease and shortest route are different questions, and they coincide only on a round bowl.",
                            r"The sign is right: $-(1,100)$ genuinely decreases $f$ faster than any other unit direction. What it does not do is point at the minimiser, and no sign change would fix that, since $(-1,-1)$ is not parallel to $(1,100)$ either way round.",
                            r"Distance is not the issue. At $(0.001, 0.001)$ the gradient is $(0.001, 0.1)$, which points in exactly the same direction as before — the angle is scale-invariant along a ray, so it survives all the way to the minimiser.",
                            r"This function is convex everywhere: its Hessian has eigenvalues $1$ and $100$, both positive. Convexity guarantees that a stationary point is the answer, and says nothing about the route taken to it.",
                        ],
                        "why": r'''
Steepest descent is the direction that minimises $\nabla f \cdot d$ over unit vectors
$d$, and Cauchy-Schwarz makes that the negative gradient. Both halves of that sentence
are measured in the Euclidean norm, which knows nothing about the fact that one
coordinate is in centimetres and the other effectively in millimetres. The route to the
minimiser is a different question, and the two answers agree only when every direction
curves at the same rate. That is what the condition number measures, and $\kappa = 100$
here buys a forty-four degree error that no amount of getting closer will reduce.
''',
                    },
                    {
                        "q": "On a quadratic with curvature bracket $m = 1$ and $L = 100$, why does a fixed step of $0.021$ diverge while $0.019$ converges?",
                        "opts": [
                            "Because the step has to be under $2/L$, and along the steepest eigendirection $|1 - 0.021 \\times 100| = 1.1$",
                            "Because the step has to be under $1/L$, so anything above $0.01$ overshoots and grows without bound",
                            "Because the step has to be under $2/\\kappa$, and the condition number here is $100$ rather than the curvature",
                            "Because the step has to be under $m/L$, which is the largest ratio the two curvatures will tolerate",
                        ],
                        "a": 0,
                        "whys": [
                            r"One step multiplies each eigencoordinate by $1 - t\lambda$, and a multiplier of magnitude above one grows forever.",
                            r"$1/L$ is the step that maximises the *guaranteed* decrease from the descent lemma, and it is safe — but it is not the boundary. Steps between $1/L$ and $2/L$ overshoot the minimum along the steep direction and still land closer than they started.",
                            r"The condition number is dimensionless and the step size is not, so a bound of $2/\kappa$ cannot even be right about units: rescale $f$ by a factor of a thousand and $\kappa$ is unchanged while every safe step shrinks by a thousand.",
                            r"$m/L$ is $0.01$ here, so this happens to forbid the diverging step, and that coincidence is what makes it tempting. It is also dimensionless, and it forbids $0.015$, which converges perfectly well.",
                        ],
                        "why": r'''
One gradient step on $f = \tfrac{1}{2}x \cdot Hx$ is $x^{+} = (I - tH)x$, so along an
eigenvector the coordinate is multiplied by $1 - t\lambda$ once per iteration. That
shrinks exactly when $|1 - t\lambda| < 1$, which is $0 < t < 2/\lambda$, and the binding
case is the largest eigenvalue. With $L = 100$ the limit is $0.02$: at $t = 0.019$ the
multiplier is $-0.9$, which flips sign and shrinks, and at $t = 0.021$ it is $-1.1$,
which flips sign and grows. Nothing about the shallow direction enters the limit, which
is why the direction that takes longest to travel is not the one that decides safety.
''',
                    },
                    {
                        "q": "Two problems, both convex quadratics: one has two variables and $\\kappa = 10^4$, the other has ten thousand variables and $\\kappa = 1$. Which needs more gradient steps?",
                        "opts": [
                            "The ten-thousand-variable one, because each iteration touches ten thousand coordinates",
                            "The two-variable one, because the contraction per step is set by $\\kappa$ and not by the count of variables",
                            "Neither — the number of steps is set by the starting distance, which is not given for either problem",
                            "The ten-thousand-variable one, because the step limit $2/L$ shrinks as more curving directions are added to it",
                        ],
                        "a": 1,
                        "whys": [
                            r"Work per iteration and number of iterations are different quantities, and the question asks for steps. A round bowl in any dimension is solved by a single step of $t = 1/L$, whether it has two coordinates or ten thousand.",
                            r"The contraction $(\kappa-1)/(\kappa+1)$ mentions the eigenvalue extremes and nothing else.",
                            r"The starting distance sets a constant inside a logarithm; the contraction factor sets the rate. Doubling the distance costs a single extra step at $\kappa = 3$, while raising $\kappa$ from $3$ to $10^4$ costs a factor of thousands however far away you start.",
                            r"The step limit is $2/L$, and $L$ is the largest eigenvalue of the Hessian — a curvature, not a count. Adding directions that all curve at rate $1$ leaves $L = 1$ exactly where it was.",
                        ],
                        "why": r'''
The contraction per step at the best fixed size is $(\kappa - 1)/(\kappa + 1)$, which
mentions the ratio of the largest curvature to the smallest and nothing else. At
$\kappa = 1$ that factor is zero: one step of $t = 1/L$ lands exactly on the minimiser
in any number of dimensions, because every coordinate is multiplied by $1 - t\lambda =
0$. At $\kappa = 10^4$ the factor is $0.9998$, and a decimal digit costs about eleven
thousand iterations. Dimension changes the cost of an iteration; conditioning changes
how many there are, and it is the second that decides whether a method is usable.
''',
                    },
                    {
                        "q": "A backtracking search accepts $t = 0.00390625$ at $x = 10$ on $f(x) = x^4$, landing at $x = -5.625$ — past the minimum and on the far side. Is that a defect?",
                        "opts": [
                            "No — the Armijo test asks for sufficient decrease, and $f$ fell from $10000$ to about $1001$",
                            "Yes — a line search must never step beyond the minimiser, which is what the halving is there to prevent",
                            "Yes — an accepted step should leave the iterate closer to the answer, and this one moved it further away",
                            "No — the objective is symmetric, so a mirror-image step is as good as staying put",
                        ],
                        "a": 0,
                        "whys": [
                            r"Sufficient decrease is a condition on the function value, and this step delivers a tenfold one.",
                            r"Halving exists to find *a* step that decreases the objective enough, not to bracket the minimiser. A search that insisted on never overshooting would be an exact line search — far more function evaluations per iteration for a guarantee the method does not need.",
                            r"Distance to the answer is not what any practical line search measures, and it usually cannot: the answer is what you are looking for. Here it is $x = 0$ and the step moved from $10$ to $-5.625$, closer in fact — but the acceptance had nothing to do with it.",
                            r"Symmetry is a red herring, and stepping to the exact mirror image would be worthless: it would give the identical function value, which fails sufficient decrease outright and would be rejected.",
                        ],
                        "why": r'''
Armijo asks one question: did the objective fall by at least the fraction $c$ of what
the slope promised? At $x = 10$ the slope promises a great deal, the test target is
$9993.75$, and the accepted step delivers $1001.13$ — an enormous decrease, on the far
side of the minimum. Insisting on monotone approach to the minimiser would mean an exact
line search, which costs many more function evaluations per iteration and buys a
guarantee the convergence proof never asked for. What the halving does buy is
termination: each rejection halves the overshoot, and after nine of them the step is
short enough for the first-order picture to hold.
''',
                    },
                    {
                        "q": "The same code, the same starting point and the same objective, but $y$ is now recorded in micrometres rather than millimetres. What happens to a step size that used to work?",
                        "opts": [
                            "It still works, because rescaling a variable rescales the gradient by the same factor and the two cancel",
                            "It diverges, because the curvature in that direction rose by a million and the safe limit is $2/L$",
                            "It converges more slowly, because the minimiser has moved a thousand times further away",
                            "It still works, because the step is applied to a normalised direction and the normalisation absorbs the change",
                        ],
                        "a": 1,
                        "whys": [
                            r"The gradient does scale, and so does the coordinate — which is exactly why they do not cancel. A step of $t$ moves the coordinate by $t$ times the gradient component, so the *product* is what changes, by the square of the rescaling.",
                            r"Curvature scales as the square of the coordinate rescaling, and the step limit is the reciprocal of it.",
                            r"The minimiser does move to a numerically larger value, and this is the closest of the wrong answers — but a slower, converging run is not what happens. The multiplier $1 - t\lambda$ leaves the unit interval altogether and the iterates grow without bound.",
                            r"Steepest descent as derived here scales the direction by the gradient's magnitude rather than normalising it. Normalising is a real variant, and it has its own failure: with a fixed step it circles the minimiser at a fixed radius forever instead of settling.",
                        ],
                        "why": r'''
Replacing $y$ by $1000y$ multiplies the second derivative in that direction by $10^6$,
so $L$ rises by $10^6$ and the safe step limit $2/L$ falls by the same factor. The
multiplier along that eigendirection becomes $1 - t\lambda$ with $\lambda$ a million
times larger, which leaves the interval $(-1, 1)$ immediately and the iterates grow. The
practical reading is that a step size is a statement about the units of the problem, not
a setting of the optimiser — which is why feature scaling and learning-rate tuning are
the same conversation, and why a backtracking search, which measures the curvature it
actually meets, is robust to a change that no fixed step survives.
''',
                    },
                    {
                        "q": "Asked for a gradient tolerance of $10^{-9}$ on a bowl whose minimum value is $-6$, a backtracking descent runs thousands of iterations without moving. Why?",
                        "opts": [
                            "The Armijo constant $c = 10^{-4}$ is too small to demand real progress, and raising it would fix the stall",
                            "The requested decrease is below the spacing of doubles near $-6$, so the test cannot tell the trial from the current point",
                            "The gradient has become exactly zero, and dividing by its norm inside the direction produces a step of length zero",
                            "The backtracking loop has run out of its sixty halvings, so it returns the shortest step it tried rather than raising an error",
                        ],
                        "a": 1,
                        "whys": [
                            r"Raising $c$ demands *more* decrease, so it makes the stall arrive sooner rather than later. The constant is small on purpose: it is meant to rule out steps that barely help, not to set the accuracy floor.",
                            r"Doubles near $-6$ are about $10^{-15}$ apart, and the decrease being asked for is smaller than that.",
                            r"The gradient is around $10^{-8}$, not zero, which is why the loop keeps going. Nothing in the method divides by the gradient norm either — the direction is the negative gradient itself, so a small gradient gives a small step rather than an undefined one.",
                            r"Running out of halvings raises, and that is not what is observed. What happens instead is that a very small $t$ makes the target round back up to exactly $f(x)$, so the test passes and a step that changes nothing is accepted.",
                        ],
                        "why": r'''
Near the minimum $f$ is flat, so with a gradient of about $10^{-8}$ the true decrease
available in one step is around $10^{-16}$ — smaller than the spacing between
neighbouring doubles at $-6$, which is about $10^{-15}$. The trial value and the current
value round to the same number, the sufficient-decrease target is that same number minus
something invisible, and the test fails until $t$ is small enough that the target rounds
back up, at which point a step that moves nothing is accepted. The lesson is not about
line searches: a stopping tolerance has to be one the arithmetic can still resolve, and
on a value of order one that puts a floor of roughly $\sqrt{\varepsilon}$ on any
tolerance stated in function values, and rather less on one stated in gradients.
''',
                    },
                ],
            },
            "blanks": {
                "title": "The line search and the loop around it, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "armijo_step and gradient_descent — five holes, one of which decides whether the method converges at all",
                "brief": r'''
The two routines the lab is built around. `dot` and `norm` are assumed to exist.

Nothing runs here. Filled in correctly, the search accepts $t = 0.25$ at the origin of
the module 1 bowl, and the loop reaches its minimiser in twenty-four iterations.
''',
                "listing": r'''
def armijo_step(f, x, d, g, t0=1.0, c=1e-4, shrink=0.5, max_halvings=60):
    """The first t along d that buys a fraction c of the promised decrease."""
    slope = ___
    if slope >= 0.0:
        raise ValueError("d is not a descent direction")
    base = f(x)
    t = float(t0)
    for _ in range(max_halvings + 1):
        trial = [xi + t * di for xi, di in zip(x, d)]
        if f(trial) <= ___:
            return t
        t *= ___
    raise ValueError("no step satisfied the Armijo condition")


def gradient_descent(f, grad, x0, step=None, tol=1e-6, max_iter=5000):
    x = [float(v) for v in x0]
    history = [f(x)]
    for _ in range(max_iter):
        g = grad(x)
        if ___ <= tol:
            return (x, history)
        d = ___
        t = armijo_step(f, x, d, g) if step is None else float(step)
        x = [xi + t * di for xi, di in zip(x, d)]
        history.append(f(x))
    return (x, history)
''',
                "blanks": [
                    {
                        "prompt": "The slope of f along d at the current point, which the sufficient-decrease target is a fraction of.",
                        "hole": "?",
                        "opts": ["dot(g, d)", "dot(g, g)", "dot(d, d)", "-dot(g, d)"],
                        "a": 0,
                        "why": "The directional derivative along d is the gradient dotted with d, and its sign is what makes d a descent direction at all. Negative slope, negative target offset, sufficient decrease.",
                        "whys": [
                            "The directional derivative along d is the gradient dotted with d, and its sign is what makes d a descent direction at all. Negative slope, negative target offset, sufficient decrease.",
                            "This is the squared gradient norm, which is never negative, so the guard above rejects every direction including the good ones and the routine raises on its first call.",
                            "The squared length of the direction carries no information about which way the function falls. It is also never negative, so like the squared gradient it trips the descent guard every time.",
                            "Flipping the sign turns a descent direction into one the guard rejects and an ascent direction into one it welcomes. Worse, the target then sits above the current value, so any step at all passes and the objective is free to rise.",
                        ],
                    },
                    {
                        "prompt": "The value the trial point has to come in at or below.",
                        "hole": "?",
                        "opts": ["base + c * t * slope", "base", "base + t * slope", "base * (1.0 - c * t)"],
                        "a": 0,
                        "why": "The slope predicts a fall of t times slope over a step of length t; asking for the fraction c of that is what makes the condition satisfiable for small t while still ruling out steps that barely help.",
                        "whys": [
                            "The slope predicts a fall of t times slope over a step of length t; asking for the fraction c of that is what makes the condition satisfiable for small t while still ruling out steps that barely help.",
                            "Any decrease at all now counts, however tiny. That is the classic failure the Armijo condition exists to rule out: a sequence of ever smaller improvements that converges to a point which is not a minimiser.",
                            "This demands the full first-order prediction, which the function only delivers in the limit. On any function with curvature the trial value exceeds it for every positive t, so the loop halves sixty times and raises.",
                            "This asks for a decrease proportional to the current value rather than to the slope, which is meaningless the moment the objective can be negative or zero. On the module 1 bowl the minimum value is -6, so multiplying by a number below one raises the target and every step is accepted however bad it is.",
                        ],
                    },
                    {
                        "prompt": "What t is multiplied by after a rejection.",
                        "hole": "?",
                        "opts": ["shrink", "c", "1.0 - shrink", "t"],
                        "a": 0,
                        "why": "Halving is what makes the sequence of trials geometric, so the search reaches any given step length in a number of trials proportional to the logarithm of the ratio rather than to the ratio itself.",
                        "whys": [
                            "Halving is what makes the sequence of trials geometric, so the search reaches any given step length in a number of trials proportional to the logarithm of the ratio rather than to the ratio itself.",
                            "The Armijo constant is a fraction of the promised decrease, not a step ratio. Multiplying by 1e-4 collapses t to 1e-24 in six trials, and the accepted step is then so short that the outer loop makes no measurable progress.",
                            "With the default this is also 0.5, so it looks identical until somebody passes a different shrink factor. Ask for a gentler 0.8 and this quietly shrinks by 0.2 instead, which is faster rather than gentler.",
                            "Squaring t looks like a shrink because t starts below one, and it is: 1.0 squared is 1.0, so the very first rejection leaves t exactly where it was and the loop retries the same failing step sixty times over.",
                        ],
                    },
                    {
                        "prompt": "The quantity that has to fall below tol before the loop reports success.",
                        "hole": "?",
                        "opts": ["norm(g)", "abs(f(x))", "dot(g, g)", "max(g)"],
                        "a": 0,
                        "why": "A stationary point is one where the gradient vanishes, so the gradient's length is the quantity that measures how far from stationary the current point is, in the same units whatever the dimension.",
                        "whys": [
                            "A stationary point is one where the gradient vanishes, so the gradient's length is the quantity that measures how far from stationary the current point is, in the same units whatever the dimension.",
                            "The size of the objective says nothing about whether it can still be reduced. On the module 1 bowl the minimum value is -6, so this test never fires and the loop always runs to max_iter; add a constant to f and the same code stops at a random moment.",
                            "The squared norm is a monotone function of the norm, so this stops at the right place, but at the square of the tolerance the caller asked for. A request for 1e-6 becomes a request for 1e-3, which on a slowly converging problem is a different answer.",
                            "The largest signed component is negative whenever every partial derivative is, so this test fires immediately at any point on a rising slope and the loop returns the starting point unchanged.",
                        ],
                    },
                    {
                        "prompt": "The search direction.",
                        "hole": "?",
                        "opts": ["[-gi for gi in g]", "g", "[abs(gi) for gi in g]",
                                 "[-gi / norm(g) for gi in g]"],
                        "a": 0,
                        "why": "Steepest descent under the Euclidean norm is the negative gradient itself, magnitude included: as the gradient shrinks near the minimiser the step shrinks with it, which is what lets a fixed step size settle rather than circle.",
                        "whys": [
                            "Steepest descent under the Euclidean norm is the negative gradient itself, magnitude included: as the gradient shrinks near the minimiser the step shrinks with it, which is what lets a fixed step size settle rather than circle.",
                            "This walks uphill. The descent guard inside the line search catches it immediately, which is the good outcome; with a fixed step there is no guard and the objective climbs until it overflows.",
                            "Taking absolute values makes every component non-negative, so the walk always heads into the positive quadrant regardless of where the minimiser is. It also destroys the descent property that the guard is checking for.",
                            "Normalising is a real variant and the most tempting wrong answer here. It removes exactly the information that lets the method stop: with a fixed step the iterate then orbits the minimiser at a constant radius forever, since the step length no longer shrinks as the gradient does.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Descent directions and the step that survives",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Five routines in `main.py`, on plain lists of floats. Only `math` is imported.

## Vectors

- `dot(u, v)` — the sum of products; different lengths raise `ValueError`.
- `norm(v)` — the Euclidean length, built from `dot`.

## A gradient without a derivative

- `numeric_gradient(f, x, h=1e-6)` — central differences, one coordinate at a time:
  the $i$th entry is `(f(x with x[i]+h) - f(x with x[i]-h)) / (2h)`. An empty `x`
  raises `ValueError`. Central differences are used rather than forward ones because
  their error falls as $h^2$ rather than as $h$.

## The line search

- `armijo_step(f, x, d, g, t0=1.0, c=1e-4, shrink=0.5, max_halvings=60)` — return the
  first `t` in `t0, t0*shrink, t0*shrink**2, ...` with

  `f(x + t*d) <= f(x) + c * t * dot(g, d)`

  A direction with `dot(g, d) >= 0` is not a descent direction and raises `ValueError`,
  as does running out of halvings. A trial value that is not finite counts as a
  rejection rather than as an error, and so does one that raises `OverflowError` —
  Python raises rather than returning infinity for `x ** 4`, and a line search that
  dies on a wild trial cannot recover from one.

## The loop

- `gradient_descent(f, grad, x0, step=None, tol=1e-6, max_iter=5000)` — returns
  `(x, history)`, where `history` holds `f` at the starting point and after every
  accepted step. Stop and return as soon as `norm(grad(x)) <= tol`, or after
  `max_iter` iterations. `step=None` means backtracking; a float means that fixed
  step. If `f(x)` stops being finite, or any evaluation raises `OverflowError`, raise
  `ValueError` — a run that has lost control should say so rather than return a page
  of `nan`.

```text
armijo_step(bowl, [0.0, 0.0], [6.0, 6.0], [-6.0, -6.0])   ->  0.25
gradient_descent(bowl, bowl_gradient, [0.0, 0.0])          ->  ([1.0, 1.0], 25 values)
gradient_descent(steep, steep_gradient, [1, 1], step=0.021)  ->  ValueError
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def dot(u, v):
    """Sum of products; ValueError when the lengths differ."""
    # your code here


def norm(v):
    """Euclidean length."""
    # your code here


def numeric_gradient(f, x, h=1e-6):
    """Central differences, one coordinate at a time."""
    # your code here


def armijo_step(f, x, d, g, t0=1.0, c=1e-4, shrink=0.5, max_halvings=60):
    """The first t that buys a fraction c of the decrease the slope promised."""
    # your code here


def gradient_descent(f, grad, x0, step=None, tol=1e-6, max_iter=5000):
    """(x, history) after descending until the gradient is small."""
    # your code here


def bowl(v):
    return 2 * v[0] ** 2 + 2 * v[0] * v[1] + 2 * v[1] ** 2 - 6 * v[0] - 6 * v[1]


def bowl_gradient(v):
    return [4 * v[0] + 2 * v[1] - 6, 2 * v[0] + 4 * v[1] - 6]


def stretched(kappa):
    return (lambda v: 0.5 * (v[0] ** 2 + kappa * v[1] ** 2),
            lambda v: [v[0], kappa * v[1]])


x, history = gradient_descent(bowl, bowl_gradient, [0.0, 0.0])
print("bowl minimiser:", [round(v, 5) for v in x], "after", len(history) - 1, "steps")
for kappa in (1.0, 100.0):
    f, g = stretched(kappa)
    _, trace = gradient_descent(f, g, [1.0, 1.0], step=1.0 / kappa,
                                tol=1e-8, max_iter=20000)
    print(f"kappa {kappa:.0f}: {len(trace) - 1} steps")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def dot(u, v):
    """Sum of products; ValueError when the lengths differ."""
    if len(u) != len(v):
        raise ValueError("vectors must have the same length")
    return sum(float(a) * float(b) for a, b in zip(u, v))


def norm(v):
    """Euclidean length."""
    return math.sqrt(dot(v, v))


def numeric_gradient(f, x, h=1e-6):
    """Central differences, one coordinate at a time."""
    if not x:
        raise ValueError("need at least one variable to differentiate in")
    out = []
    for i in range(len(x)):
        up = [float(v) for v in x]
        down = [float(v) for v in x]
        up[i] += h
        down[i] -= h
        out.append((f(up) - f(down)) / (2.0 * h))
    return out


def armijo_step(f, x, d, g, t0=1.0, c=1e-4, shrink=0.5, max_halvings=60):
    """The first t that buys a fraction c of the decrease the slope promised."""
    slope = dot(g, d)
    if slope >= 0.0:
        raise ValueError("d is not a descent direction")
    base = f(x)
    t = float(t0)
    for _ in range(max_halvings + 1):
        trial = [xi + t * di for xi, di in zip(x, d)]
        try:
            value = f(trial)
        except OverflowError:
            value = math.inf
        if math.isfinite(value) and value <= base + c * t * slope:
            return t
        t *= shrink
    raise ValueError("no step along d satisfied the Armijo condition")


def gradient_descent(f, grad, x0, step=None, tol=1e-6, max_iter=5000):
    """(x, history) after descending until the gradient is small."""
    x = [float(v) for v in x0]
    history = [f(x)]
    for _ in range(max_iter):
        try:
            g = grad(x)
            if norm(g) <= tol:
                return (x, history)
            d = [-gi for gi in g]
            t = armijo_step(f, x, d, g) if step is None else float(step)
            x = [xi + t * di for xi, di in zip(x, d)]
            value = f(x)
        except OverflowError:
            raise ValueError("an evaluation overflowed; the step is far too long")
        if not math.isfinite(value):
            raise ValueError("the objective stopped being finite; the step is too long")
        history.append(value)
    return (x, history)


def bowl(v):
    return 2 * v[0] ** 2 + 2 * v[0] * v[1] + 2 * v[1] ** 2 - 6 * v[0] - 6 * v[1]


def bowl_gradient(v):
    return [4 * v[0] + 2 * v[1] - 6, 2 * v[0] + 4 * v[1] - 6]


def stretched(kappa):
    return (lambda v: 0.5 * (v[0] ** 2 + kappa * v[1] ** 2),
            lambda v: [v[0], kappa * v[1]])


x, history = gradient_descent(bowl, bowl_gradient, [0.0, 0.0])
print("bowl minimiser:", [round(v, 5) for v in x], "after", len(history) - 1, "steps")
for kappa in (1.0, 100.0):
    f, g = stretched(kappa)
    _, trace = gradient_descent(f, g, [1.0, 1.0], step=1.0 / kappa,
                                tol=1e-8, max_iter=20000)
    print(f"kappa {kappa:.0f}: {len(trace) - 1} steps")
'''}],
                "hints": [
                    "Build `norm` out of `dot` rather than writing a second loop; the length check then happens in one place and a mismatched pair can never reach the square root.",
                    "`numeric_gradient` must not mutate the `x` it was handed. Copy it once per coordinate, nudge the one entry, and evaluate — the copy is cheaper than the confusion of a shared list.",
                    "In `armijo_step` compute `f(x)` once, before the loop. It does not change as `t` shrinks, and evaluating it sixty times is the sort of waste a line search cannot afford.",
                    "The divergence check belongs after the step, on the new value: `if not math.isfinite(value): raise ValueError(...)`. Wrap the evaluations in `try: ... except OverflowError:` as well, because `x ** 4` on a runaway iterate raises rather than returning infinity.",
                ],
                "tests": [
                    {"name": "Dot products, lengths and mismatches", "code": r'''
assert dot([1, 2, 3], [4, 5, 6]) == 32.0, f"dot gave {dot([1, 2, 3], [4, 5, 6])!r}, expected 32.0"
assert abs(norm([3, 4]) - 5.0) < 1e-12, f"norm([3, 4]) gave {norm([3, 4])!r}, expected 5.0"
assert norm([0.0, 0.0]) == 0.0, "the zero vector has length 0"
for _u, _v in [([1, 2], [1, 2, 3]), ([], [1])]:
    try:
        dot(_u, _v)
        assert False, f"dot({_u!r}, {_v!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "A gradient from function values alone", "code": r'''
_g = numeric_gradient(lambda v: v[0] ** 2 + 3.0 * v[1] ** 2, [1.0, 2.0])
assert abs(_g[0] - 2.0) < 1e-6 and abs(_g[1] - 12.0) < 1e-6, \
    f"numeric_gradient gave {_g!r}, expected about [2.0, 12.0]"
_g = numeric_gradient(lambda v: 5.0 * v[0] - 2.0 * v[1] + 7.0, [3.0, -1.0])
assert abs(_g[0] - 5.0) < 1e-8 and abs(_g[1] + 2.0) < 1e-8, \
    f"on a linear function the difference is exact; got {_g!r}, expected [5.0, -2.0]"
_x = [1.0, 2.0]
numeric_gradient(lambda v: v[0] * v[1], _x)
assert _x == [1.0, 2.0], "numeric_gradient must not mutate the point it was given"
try:
    numeric_gradient(lambda v: 0.0, [])
    assert False, "an empty point has no coordinates to differentiate in; expected ValueError"
except ValueError:
    pass
'''},
                    {"name": "The Armijo ledger stops where it should", "code": r'''
_t = armijo_step(bowl, [0.0, 0.0], [6.0, 6.0], [-6.0, -6.0])
assert _t == 0.25, f"the search should accept t = 0.25 at the origin of the bowl; got {_t!r}"
_steep = lambda v: 0.5 * (v[0] ** 2 + 100.0 * v[1] ** 2)
_t = armijo_step(_steep, [1.0, 1.0], [-1.0, -100.0], [1.0, 100.0])
assert _t == 0.015625, f"on the stretched bowl the first accepted step is 0.015625; got {_t!r}"
_quartic = lambda v: v[0] ** 4
_t = armijo_step(_quartic, [10.0], [-4000.0], [4000.0])
assert _t == 0.00390625, f"nine halvings from 1.0 gives 0.00390625; got {_t!r}"
'''},
                    {"name": "An uphill direction is refused", "code": r'''
try:
    armijo_step(bowl, [0.0, 0.0], [-6.0, -6.0], [-6.0, -6.0])
    assert False, "a direction with a non-negative slope should raise ValueError"
except ValueError:
    pass
try:
    armijo_step(bowl, [1.0, 1.0], [0.0, 0.0], [0.0, 0.0])
    assert False, "at a stationary point the slope is zero, which is not a descent direction"
except ValueError:
    pass
'''},
                    {"name": "A fixed step converges when it is short enough", "code": r'''
_f, _g = stretched(100.0)
_x, _h = gradient_descent(_f, _g, [1.0, 1.0], step=0.01, tol=1e-8, max_iter=5000)
assert 1700 <= len(_h) - 1 <= 1950, \
    f"a step of 0.01 needs about 1833 iterations here; got {len(_h) - 1}"
assert abs(_x[0]) < 1e-7 and abs(_x[1]) < 1e-12, f"the run ended at {_x!r}, expected about [0, 0]"
assert all(b <= a + 1e-15 for a, b in zip(_h, _h[1:])), "a step under 2/L never lets f rise"
'''},
                    {"name": "A step past 2/L is caught, not tolerated", "code": r'''
_f, _g = stretched(100.0)
try:
    gradient_descent(_f, _g, [1.0, 1.0], step=0.021, tol=1e-8, max_iter=10000)
    assert False, "0.021 is above 2/L = 0.02, so the run diverges and should raise ValueError"
except ValueError:
    pass
_x, _h = gradient_descent(_f, _g, [1.0, 1.0], step=0.019, tol=1e-8, max_iter=20000)
assert abs(_x[0]) < 1e-6 and abs(_x[1]) < 1e-6, \
    f"0.019 is under the limit and should converge; the run ended at {_x!r}"
'''},
                    {"name": "Backtracking needs no step size at all", "code": r'''
_x, _h = gradient_descent(bowl, bowl_gradient, [0.0, 0.0])
assert abs(_x[0] - 1.0) < 1e-6 and abs(_x[1] - 1.0) < 1e-6, \
    f"the bowl is minimised at [1, 1]; the run ended at {_x!r}"
assert len(_h) - 1 < 60, f"the bowl has kappa = 3 and should take a few dozen steps; took {len(_h) - 1}"
assert all(b <= a + 1e-12 for a, b in zip(_h, _h[1:])), \
    "every accepted step satisfies sufficient decrease, so the history never rises"
assert abs(_h[-1] + 6.0) < 1e-9, f"the minimum value is -6.0; the run ended at {_h[-1]!r}"
'''},
                    {"name": "A curvature with no upper bound", "code": r'''
_q = lambda v: v[0] ** 4
_dq = lambda v: [4.0 * v[0] ** 3]
try:
    gradient_descent(_q, _dq, [10.0], step=0.01, tol=1e-6, max_iter=200)
    assert False, "x^4 has no global curvature bound, so a fixed step from 10 diverges"
except ValueError:
    pass
_x, _h = gradient_descent(_q, _dq, [10.0], tol=1e-4, max_iter=2000)
assert abs(_x[0]) < 0.05, f"backtracking should reach the flat bottom; the run ended at {_x!r}"
assert _h[-1] < 1e-5, f"the objective should be near zero; it ended at {_h[-1]!r}"
'''},
                    {"name": "The report, and what it says about conditioning", "code": r'''
_lines = _out.strip().split("\n")
assert len(_lines) == 3, f"main.py should print three lines; it printed {len(_lines)}:\n{_out}"
assert _lines[0].startswith("bowl minimiser: [1.0, 1.0] after "), \
    f"the first line was {_lines[0]!r}, expected the minimiser [1.0, 1.0]"
assert _lines[1] == "kappa 1: 1 steps", \
    f"a round bowl is solved in one step of 1/L; the line read {_lines[1]!r}"
_n = int(_lines[2].split(":")[1].split()[0])
assert _n > 500, f"kappa = 100 should need many hundreds of steps; the line reported {_n}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Newton's method, and the damping that keeps it honest",
            "summary": "What the second derivative buys, what it costs, and the two repairs that make it usable.",
            "concepts": [
                "The Newton step solves H p = -g: the minimiser of the second-order model, not a scaled gradient",
                "On a quadratic the model is exact, so one step lands on the answer whatever the conditioning",
                "Newton is affine invariant: rescaling the variables leaves the iterates unchanged",
                "Quadratic convergence near a strict minimum, and only near it",
                "Newton solves grad f = 0, so it converges happily to a maximum or a saddle",
                "H p = -g is a descent direction exactly when H is positive definite",
                "Damping by line search and modification by H + tau I, with Cholesky as the positive-definiteness test",
            ],
            "read": [
                {
                    "title": "Curvature is the information a gradient does not carry",
                    "minutes": 13,
                    "body": r'''
Module 2 ended with a bill. On a bowl with condition number $100$, the best fixed
gradient step buys one decimal digit per $115$ iterations, and the reason is that a
gradient reports a slope and nothing else: it cannot distinguish a direction that falls
steeply for a centimetre from one that falls gently for a kilometre. Yet for that same
bowl the second derivatives are a constant matrix you could write down on the back of an
envelope. The question is what to do with them.

Here is the picture. You are standing somewhere on the surface. You can measure three
things without moving: the height, the slope, and how fast the slope is changing. Those
three numbers determine a parabola. Fit it, walk to the bottom of the parabola, and
repeat from there. A gradient method fits a straight line, which has no bottom, and so
has to be told separately how far to walk. A curvature method fits something with a
bottom, and the distance comes out of the fit.

## The step, derived

Write the second-order model of $f$ around the current point $x$, with $g$ the gradient
and $H$ the matrix of second derivatives:

$$m(p) = f(x) + g \cdot p + \frac{1}{2}\, p \cdot Hp$$

This is a quadratic in $p$. Its gradient is $g + Hp$, and module 1 established that a
convex quadratic is minimised where its gradient vanishes, so the step to the bottom of
the model is the solution of

$$Hp = -g$$

That is the Newton step. It is not the negative gradient scaled by anything: the two
agree only when $H$ is a multiple of the identity, which is the round bowl again.

Take the module 1 bowl, $f(x,y) = 2x^2 + 2xy + 2y^2 - 6x - 6y$, from the origin. There
$g = (-6,-6)$ and $H$ has rows $(4,2)$ and $(2,4)$, so the step solves
$4p_1 + 2p_2 = 6$ and $2p_1 + 4p_2 = 6$, giving $p = (1,1)$ and landing on $(1,1)$ — the
exact minimiser, in one step, from a point where gradient descent needed twenty-four.
Nothing special happened: for a quadratic the second-order model *is* the function, so
the bottom of the model is the bottom of the function.

That also settles a question module 2 left open. Rescale $y$ by a factor of a thousand
and the gradient method needs a step a million times smaller; the Newton step is
unchanged, because both $g$ and $H$ pick up matching factors and $H^{-1}g$ transforms
back exactly. Newton's method is affine invariant, which is the real reason the
condition number does not appear in its convergence rate.

```python
import math

def newton_steps(kappa):
    """f = (x^2 + kappa y^2) / 2, minimised by Newton from (1, 1)."""
    x, y = 1.0, 1.0
    steps = 0
    while math.hypot(x, kappa * y) > 1e-12:
        x = x - x / 1.0              # solve 1 * p = -x
        y = y - (kappa * y) / kappa  # solve kappa * p = -kappa*y
        steps += 1
    return steps

for kappa in (1.0, 100.0, 1000000.0):
    print(f"kappa={kappa:>10.0f}  Newton steps={newton_steps(kappa)}")
```

## How fast, on a function that is not a quadratic

Take $f(x) = x - \ln x$ on $x > 0$. Its derivative is $1 - 1/x$ and its second
derivative is $1/x^2$, so the Newton step is
$p = -(1 - 1/x)\,x^2 = -x^2 + x$ and the iteration is

$$x^{+} = x + p = 2x - x^2$$

Subtract both sides from $1$: $1 - x^{+} = 1 - 2x + x^2 = (1-x)^2$. The error at the
next step is the *square* of the error at this one, exactly, with no constant and no
approximation. Starting at $0.5$:

```python
x = 0.5
for k in range(6):
    print(f"k={k}  x={x:.16f}  error={1.0 - x:.4e}")
    x = 2.0 * x - x * x
```

The errors run $0.5$, $0.25$, $0.0625$, $0.0039$, $1.5 \times 10^{-5}$,
$2.3 \times 10^{-10}$: the number of correct digits doubles every iteration. That is
quadratic convergence, and it is why a Newton method that reaches the neighbourhood of
the answer is finished almost immediately.

## Three ways it goes wrong

**Far away, the model is a fantasy.** Run the same map from $x = 2.5$:
$2(2.5) - 2.5^2 = -1.25$, outside the domain, where $\ln x$ does not exist. The
quadratic fitted at $2.5$ is an excellent description of $f$ near $2.5$ and says nothing
useful about a point four units away. Quadratic convergence is a statement about a
neighbourhood, and outside it Newton has no claim at all.

**It is a root finder for the gradient.** Newton solves $\nabla f = 0$, and a maximum
satisfies that as comfortably as a minimum does. On $f(x) = -x^2$ the step is
$x - (-2x)/(-2) = 0$: from any starting point it lands on the maximum in one step and
reports convergence. Nothing in $Hp = -g$ mentions minimisation.

**The direction need not go downhill.** The slope of $f$ along the Newton direction is
$g \cdot p = -g \cdot H^{-1} g$, and that is negative for every non-zero $g$ exactly
when $H^{-1}$, and therefore $H$, is positive definite. Where the curvature is negative,
the Newton direction points uphill, and it does so for a reason: it is heading for the
nearest stationary point, which up there is a maximum.

## The two repairs

**Damping.** Do not take the whole step. Backtrack along $p$ with the same Armijo test
as module 2. Near the solution the full step $t = 1$ passes the test on the first try,
so the quadratic rate survives untouched; far away the step is cut and the iterate
still descends. From $x = 2.5$ on $x - \ln x$ the full step is rejected outright — it
lands where the objective is infinite — and $t = 0.5$ is accepted, arriving at $0.625$.

**Modification.** Where $H$ is not positive definite, replace it by $H + \tau I$ for the
smallest $\tau$ from $0, \beta, 2\beta, 4\beta, \dots$ that makes it so. Adding
$\tau$ to the diagonal adds $\tau$ to every eigenvalue, so a large enough $\tau$ always
works, and as $\tau$ grows the step turns continuously from the Newton direction towards
the negative gradient scaled by $1/\tau$. The test for positive definiteness is an
attempted Cholesky factorisation, which fails exactly when a diagonal entry it needs to
take a square root of comes out non-positive — so the test and the factorisation you
were going to need anyway are the same computation.

The double well makes both repairs visible at once. At $x = 0.1$ the second derivative
is $12(0.01) - 6 = -5.88$ and the gradient is $4(0.001) - 0.6 = -0.596$. The pure Newton
step is $-(-0.596)/(-5.88) = -0.101$, which moves *left*, towards the ridge at the
origin, because that is where the nearest stationary point is. Thirteen doublings of
$\beta = 10^{-3}$ give $\tau = 8.192$, the shifted curvature is $2.312$, and the step
becomes $+0.258$: downhill, to the right, towards the minimum at $\sqrt{1.5}$, which six
damped iterations then reach.

## The mistake

The one people actually make is saying that Newton's method finds minima. It finds
stationary points, and which kind it finds is decided by where it starts and by nothing
else. It is tempting because every worked example in every introduction is convex, where
the two coincide, and because the derivation above begins by *minimising* the model —
which it does, honestly, and then hands you a step that only minimises the real function
when the model curves the right way.

The second is computing $H^{-1}$ and multiplying by it. MA121 made the argument for
linear systems generally; here it is sharper, because the Hessian is often nearly
singular precisely where the step matters, and an explicit inverse both costs more and
loses more digits than a factorisation and a solve. `newton_direction` in the lab calls
`solve`, never an inverse.

## Where it stops holding

The cost. Assembling $H$ is $n^2$ second derivatives and factoring it is proportional to
$n^3$, per iteration. At a few hundred variables that is a bargain against the hundreds
of gradient steps it replaces; at a million it is unavailable, and that gap is the whole
reason quasi-Newton methods exist — BFGS and its limited-memory variant build an
approximate inverse Hessian out of successive gradient differences, keeping most of the
speed for the cost of a few vectors. It is also why the networks trained in ML401 are
trained with first-order methods.

Beyond cost: the Hessian has to exist, so a non-smooth objective is out; the quadratic
rate needs the Hessian at the solution to be non-singular, and $x^4$ at the origin fails
that and drops Newton back to a linear rate; and none of this makes a non-convex problem
convex. A damped, modified Newton method finds a hollow faster than gradient descent
does. It still cannot tell you which hollow.

## The lab

**The Newton step, and the damping that keeps it honest** builds the whole apparatus:
`solve` by Gaussian elimination with partial pivoting, `cholesky`,
`is_positive_definite` on top of it, `modified_hessian`, `newton_direction`, and
`damped_newton` with the Armijo test from module 2 folded in. The tests include the two
starting points above — $0.5$, where the full step is always accepted, and $2.5$, where
pure Newton leaves the domain on its first move — and the double well from $x = 0.1$,
where the unmodified direction climbs.
''',
                },
            ],
            "quiz": {
                "title": "What curvature buys and what it does not",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A convex quadratic in two variables has condition number $10^6$. How many Newton steps does it take from any starting point?",
                        "opts": [
                            "One, because the second-order model of a quadratic is the quadratic itself",
                            "About $10^6$, since the conditioning enters the Newton rate the same way it enters the gradient rate",
                            "Two, because the first step corrects the position and the second corrects the curvature estimate",
                            "It depends on the start, since a distant one makes the model unreliable",
                        ],
                        "a": 0,
                        "whys": [
                            r"Fitting a quadratic to a quadratic reproduces it exactly, so the bottom of the model is the bottom of the function.",
                            r"Conditioning appears nowhere in the Newton step. $Hp = -g$ divides by the curvature in each eigendirection, which is exactly the quantity that varies by $10^6$ — so the variation cancels rather than accumulating.",
                            r"There is no curvature estimate to correct: $H$ is evaluated exactly, and for a quadratic it is the same constant matrix everywhere. Two steps would be needed only if the first had been damped, and on a quadratic the full step always passes the Armijo test.",
                            r"For a general function that reservation is exactly right, and it is what damping exists for. For a quadratic the model is not an approximation at any distance, so a start a billion units away lands on the answer in the same single step.",
                        ],
                        "why": r'''
The Newton step minimises the second-order model $f(x) + g \cdot p + \tfrac{1}{2}p \cdot
Hp$, and for a quadratic that model is the function, not an approximation to it. So the
minimiser of the model is the minimiser of $f$, reached in one solve of $Hp = -g$ from
anywhere. The condition number does not appear because the step divides by the curvature
in every eigendirection — the same quantity whose spread defines $\kappa$ — which is the
computational content of Newton's affine invariance. That is the whole trade: the method
stops caring about scaling, and starts costing an $n \times n$ factorisation per
iteration.
''',
                    },
                    {
                        "q": "Applied to $f(x) = -x^2$ from $x = 3$, the Newton step lands on $x = 0$ and reports that the gradient is zero. What has it found?",
                        "opts": [
                            "The maximum — Newton solves $\\nabla f = 0$ and does not distinguish the kinds of stationary point",
                            "The minimum, which is at the origin because the parabola is symmetric about it",
                            "A saddle point, which is what a stationary point of a non-convex function always is",
                            "Nothing usable at all, because the Newton step is undefined whenever the second derivative comes out negative",
                        ],
                        "a": 0,
                        "whys": [
                            r"The equation being solved is stationarity, and a maximum satisfies it as well as a minimum does.",
                            r"This parabola opens downwards, so the origin is its highest point and $f$ has no minimum at all — it runs to minus infinity in both directions. A method that reports success here has answered a question nobody asked.",
                            r"A saddle needs at least two variables, with curvature of both signs. In one variable a stationary point is a maximum, a minimum, or an inflection, and this one is a maximum.",
                            r"The step is perfectly well defined: $-2$ is invertible, and $x - (-2x)/(-2) = 0$ has nothing wrong with the arithmetic. The trouble is what the arithmetic is aiming at.",
                        ],
                        "why": r'''
$Hp = -g$ is the stationarity condition of the second-order model, and the model here
opens downwards, so its stationary point is a maximum and Newton walks straight to it.
The gradient really is zero at the answer, so any stopping test written on the gradient
norm reports success. This is the practical reason a usable Newton method modifies $H$:
replacing $-2$ by $-2 + \tau$ for a large enough $\tau$ makes the model open upwards
again, and the step then heads downhill from wherever it is, which on this function
means heading away from the origin without bound — which is the honest answer, since
$-x^2$ has no minimum.
''',
                    },
                    {
                        "q": "Why is an attempted Cholesky factorisation a good test for positive definiteness?",
                        "opts": [
                            "It fails exactly when a diagonal entry it must take the root of is non-positive, and it leaves the factors you needed anyway",
                            "It computes all the eigenvalues on the way, so their signs can be inspected once the factorisation finishes",
                            "It is the only factorisation that exists for symmetric matrices, so no alternative test is available",
                            "It is numerically exact in a way that an eigenvalue computation is not, so the verdict never has to depend on a chosen tolerance",
                        ],
                        "a": 0,
                        "whys": [
                            r"The failure condition of the algorithm and the definition of the property coincide, and the work is not wasted when it succeeds.",
                            r"Cholesky computes no eigenvalues. The diagonal of $L$ holds the square roots of the pivots, which are related to the eigenvalues but are not them — a matrix with pivots $2$ and $2$ can have eigenvalues $1$ and $3$.",
                            r"Symmetric matrices have several factorisations, including the eigendecomposition and the symmetric indefinite one, and a plain LU exists for most of them. Cholesky is the cheapest *and* the one whose failure is informative, which is a different claim.",
                            r"No floating-point factorisation is exact, and a matrix that is positive definite by a margin of $10^{-18}$ can factor either way. The test still needs judgement about scale; what it does not need is a separate eigenvalue solver.",
                        ],
                        "why": r'''
The factorisation walks the diagonal computing $a_{ii}$ minus a sum of squares, and takes
the square root of the result. That quantity is positive for every $i$ exactly when the
matrix is positive definite, so the algorithm's failure condition is the definition of
the property rather than a proxy for it. It also costs about half of an LU
factorisation and leaves behind the factors the Newton solve wants, so the test is free
in the case where it passes — which is the common case. An eigenvalue routine would
answer the same question for several times the work and would then have to be followed
by a solve regardless.
''',
                    },
                    {
                        "q": "At $x = 0.1$ on $f(x) = x^4 - 3x^2 + 1$ the second derivative is $-5.88$ and the gradient is $-0.596$. The unmodified Newton step is $-0.101$. Why does it move left, towards the ridge?",
                        "opts": [
                            "Because dividing a negative gradient by a negative curvature gives a positive step that is then subtracted",
                            "Because the model fitted there opens downwards, so its stationary point is the top of the ridge",
                            "Because the ridge at the origin is closer than the minimum, and Newton always moves to the nearer of the two",
                            "Because the gradient is negative, which means the function decreases to the left",
                        ],
                        "a": 1,
                        "whys": [
                            r"The arithmetic is right and it is the same arithmetic, but stating it as a sign rule explains nothing about why the sign came out that way — and the rule as phrased predicts the same leftward move on a positively curved point with a negative gradient, where the step in fact goes right.",
                            r"A downward-opening parabola has one stationary point and it is its maximum, so the step aims at it.",
                            r"Distance plays no part in the step, which is computed from the gradient and curvature at one point and knows nothing about where any stationary point is. From $x = 0.2$, still closer to the ridge than to the minimum, a modified step goes right.",
                            r"A negative gradient means the function decreases to the *right*, since moving in the direction $-\nabla f$ is moving in the positive direction here. That is exactly what the modified step does.",
                        ],
                        "why": r'''
The Newton step solves $Hp = -g$, which is the stationarity condition of the fitted
quadratic. With $H = -5.88$ that quadratic opens downwards, so the only stationary point
it has is a maximum, and the step aims at it — leftwards, at the ridge. The gradient is
negative, so the honest descent direction is to the right, and the modification supplies
it: thirteen doublings of $10^{-3}$ give $\tau = 8.192$, the shifted curvature is
$2.312$, and the step becomes $+0.258$. Adding $\tau$ to the diagonal adds $\tau$ to
every eigenvalue, and as $\tau$ grows the direction turns smoothly from the Newton
direction towards a short step along the negative gradient.
''',
                    },
                    {
                        "q": "A damped Newton method takes full steps ($t = 1$) once it is near the solution. Why does that matter?",
                        "opts": [
                            "Because a shortened step costs an extra function evaluation, and those dominate the run near the answer",
                            "Because quadratic convergence is a property of the full step, and a permanently damped method converges only linearly",
                            "Because the Armijo test is not defined once the gradient is small, so the line search has to be switched off",
                            "Because the modification adds $\\tau I$ to the Hessian whenever a step is cut, which would keep on perturbing the curvature",
                        ],
                        "a": 1,
                        "whys": [
                            r"Function evaluations near the answer are the cheapest part of a Newton iteration — the factorisation dominates — and one extra halving would be a rounding error in the cost.",
                            r"The error-squaring argument is about $x + p$, so a method that always took $x + p/2$ would lose it.",
                            r"The Armijo test is defined wherever $f$ and the slope are, small gradient or not. It is not switched off near the solution; it passes on the first try, which is the point being made.",
                            r"The modification is decided by the curvature, not by whether a step was cut. Near a strict minimum the Hessian is positive definite, so $\tau = 0$ and the two mechanisms are independent.",
                        ],
                        "why": r'''
The error-squaring identity is about the undamped step: on $x - \ln x$ the map
$x^{+} = x + p$ satisfies $1 - x^{+} = (1-x)^2$ exactly, and the halved map
$x^{+} = x + p/2$ does not — its error contracts by a constant factor instead. So a
method that damped forever would be a linearly convergent method with a Hessian
factorisation in the inner loop, which is the worst of both. What makes damping safe is
that near a strict minimum the full step passes the sufficient-decrease test on its
first trial, so the line search stops interfering exactly when the fast rate becomes
available.
''',
                    },
                    {
                        "q": "Newton's method is affine invariant: rescaling the variables leaves its iterates unchanged. Why does that not make it the obvious default everywhere?",
                        "opts": [
                            "Because assembling and factoring the Hessian costs on the order of $n^3$ per iteration, which is unavailable at large $n$",
                            "Because affine invariance holds only for quadratics, and real objectives are not quadratic",
                            "Because gradient descent converges to a better minimum on a non-convex problem, being less willing to commit",
                            "Because the Hessian of a convex function can still turn out to be singular, and a singular system has no solution at all to offer",
                        ],
                        "a": 0,
                        "whys": [
                            r"An $n \times n$ factorisation every iteration is what buys the invariance, and it is the reason a million-parameter model is not trained this way.",
                            r"Affine invariance is a property of the step $Hp = -g$ under a change of variables and holds for any twice-differentiable $f$. What holds only for quadratics is exactness in a single step.",
                            r"Neither method has any claim on which hollow it finds, and there is no result saying either finds a better one. What is true is that Newton commits harder to the basin it is in, which is a fair intuition attached to a wrong conclusion.",
                            r"A singular Hessian is a real difficulty and the modification handles it: $H + \tau I$ is non-singular for any $\tau$ above the smallest eigenvalue's magnitude. It also cannot happen at a strict minimum, which is where the rate is claimed.",
                        ],
                        "why": r'''
The invariance is bought by solving a linear system in the curvature every iteration,
and that system costs roughly $n^3$ operations on an $n \times n$ matrix that itself
needs $n^2$ second derivatives. At a few hundred variables that is an excellent trade
against the hundreds of gradient iterations it replaces. At a million it is out of
reach, in time and in memory alike, which is why quasi-Newton methods approximate the
inverse Hessian from successive gradient differences and why large models are trained
with first-order methods. The mathematics does not stop being true at scale; the
arithmetic stops being affordable.
''',
                    },
                ],
            },
            "blanks": {
                "title": "Cholesky and the shift, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "the positive-definiteness test and the modification built on it — five holes",
                "brief": r'''
The factorisation whose failure is the test, and the loop that shifts a Hessian until it
passes.

Nothing runs here. Filled in correctly, the factor of the matrix with rows $(4,2)$ and
$(2,4)$ is lower-triangular with diagonal $2$ and $\sqrt{3}$, and a Hessian of $-5.88$
is shifted to $2.312$.
''',
                "listing": r'''
def cholesky(a):
    """Lower triangular L with L L^T = a; ValueError when a is not positive definite."""
    n = len(a)
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(___):
            total = a[i][j] - sum(lower[i][k] * lower[j][k] for k in range(___))
            if i == j:
                if total <= 0.0:
                    raise ValueError("matrix is not positive definite")
                lower[i][j] = ___
            else:
                lower[i][j] = total / ___
    return lower


def modified_hessian(h, beta=1e-3):
    """h itself when it is already positive definite, otherwise h + tau I."""
    n = len(h)
    if is_positive_definite(h):
        return [list(row) for row in h]
    tau = beta
    while True:
        shifted = [[h[i][j] + (tau if i == j else 0.0) for j in range(n)]
                   for i in range(n)]
        if is_positive_definite(shifted):
            return shifted
        tau *= ___
''',
                "blanks": [
                    {
                        "prompt": "How far along row i the inner loop runs.",
                        "hole": "?",
                        "opts": ["i + 1", "n", "i", "j + 1"],
                        "a": 0,
                        "why": "L is lower triangular, so row i has entries in columns 0 through i and the diagonal entry is the last one written. Stopping one past i is what makes the diagonal case reachable.",
                        "whys": [
                            "L is lower triangular, so row i has entries in columns 0 through i and the diagonal entry is the last one written. Stopping one past i is what makes the diagonal case reachable.",
                            "Running the full width writes entries above the diagonal, where L is supposed to be zero. Worse, the first of them divides by lower[j][j] for a j that has not been computed yet, which is still 0.0, so the routine raises ZeroDivisionError rather than returning a factor.",
                            "Stopping at i skips the diagonal entry of every row, so lower[i][i] stays 0.0 and the very next row divides by it. The positive-definiteness test never runs either, since the square root that would have failed is never taken.",
                            "j is the loop variable being defined here, so this is a NameError on the first iteration. The intent behind it is right — the loop should reach one past its last useful column — but the last useful column is named by i.",
                        ],
                    },
                    {
                        "prompt": "How many already-computed products are subtracted from a[i][j].",
                        "hole": "?",
                        "opts": ["j", "i", "n", "j + 1"],
                        "a": 0,
                        "why": "The entry being solved for is lower[i][j], and the identity says a[i][j] is the sum over k up to and including j of lower[i][k] times lower[j][k]. Every term before k = j is known; the term at k = j is the unknown, so the sum stops there.",
                        "whys": [
                            "The entry being solved for is lower[i][j], and the identity says a[i][j] is the sum over k up to and including j of lower[i][k] times lower[j][k]. Every term before k = j is known; the term at k = j is the unknown, so the sum stops there.",
                            "Row j has zeros beyond column j, so the extra terms from j to i contribute nothing and the answer happens to come out right for the strictly lower entries. On the diagonal, where i and j are equal, it is identical anyway. It is right by accident and reads as though the two indices were interchangeable.",
                            "Running k to the full width reads lower[j][k] for k beyond j, which is still 0.0 at that moment, so this also gives the right answer by accident — and stops doing so the moment the routine is adapted to factor in place, where those slots hold the original matrix.",
                            "Including k = j subtracts the unknown term as well, using whatever lower[i][j] happens to hold, which is 0.0 for the strictly lower entries and produces the correct value there. On the diagonal it subtracts nothing extra either, so this survives every square test and fails only once an entry is revisited.",
                        ],
                    },
                    {
                        "prompt": "The diagonal entry of L.",
                        "hole": "?",
                        "opts": ["math.sqrt(total)", "total", "total / lower[j][j]", "abs(total)"],
                        "a": 0,
                        "why": "The identity is a[i][i] equals the sum of the squares of row i of L, so the diagonal entry is the square root of what is left after the earlier squares are subtracted. That square root is also the step that refuses a non-positive-definite matrix.",
                        "whys": [
                            "The identity is a[i][i] equals the sum of the squares of row i of L, so the diagonal entry is the square root of what is left after the earlier squares are subtracted. That square root is also the step that refuses a non-positive-definite matrix.",
                            "Leaving the pivot unrooted produces a factorisation of a different matrix: for a 1x1 input of 4 it returns 4 rather than 2, and 4 times 4 is 16. This is the LDL decomposition's pivot, which is a real object, but it belongs in a factorisation that keeps D separate.",
                            "This is the off-diagonal formula applied to the diagonal, where j equals i and lower[j][j] is the very entry being computed — still 0.0 — so it raises ZeroDivisionError on the first row. The diagonal is special because it is the one place the identity gives a square rather than a product of two different entries.",
                            "The guard above has already rejected every non-positive total, so the absolute value can only ever be a no-op on a value that is already positive — and it leaves the same unrooted pivot as the option above.",
                        ],
                    },
                    {
                        "prompt": "What the off-diagonal entry is divided by.",
                        "hole": "?",
                        "opts": ["lower[j][j]", "lower[i][i]", "a[j][j]", "lower[i][j]"],
                        "a": 0,
                        "why": "Row j was finished on an earlier pass, so its diagonal entry is available and is the one multiplying the unknown in the identity for a[i][j].",
                        "whys": [
                            "Row j was finished on an earlier pass, so its diagonal entry is available and is the one multiplying the unknown in the identity for a[i][j].",
                            "Row i is the row currently being built, and its diagonal entry is written last, so this divides by 0.0 and raises ZeroDivisionError on the very first off-diagonal entry.",
                            "The original matrix entry is not the factor's diagonal: for a matrix with rows (4, 2) and (2, 4) this divides by 4 instead of by 2 and returns a lower triangle of 0.5 where 1.0 belongs, so L times L transposed no longer reproduces the input.",
                            "That is the entry being computed, so this divides by 0.0 on the first pass and by a stale value on any later one.",
                        ],
                    },
                    {
                        "prompt": "How tau grows after a rejected shift.",
                        "hole": "?",
                        "opts": ["2.0", "beta", "1.0", "0.5"],
                        "a": 0,
                        "why": "Doubling reaches any required shift in a number of attempts proportional to the logarithm of the ratio, so a Hessian needing tau near 8 is found in thirteen tries from a beta of a thousandth rather than in eight thousand.",
                        "whys": [
                            "Doubling reaches any required shift in a number of attempts proportional to the logarithm of the ratio, so a Hessian needing tau near 8 is found in thirteen tries from a beta of a thousandth rather than in eight thousand.",
                            "Multiplying by beta, which is a thousandth, makes tau smaller at every attempt, so it converges to zero and the loop never terminates on a matrix that needs any shift at all.",
                            "Leaving tau alone means the same failing shift is tested forever. Since the loop has no iteration cap, it hangs rather than raising, which is the worst of the failures here.",
                            "Halving also drives tau to zero, and it does so while looking plausible: a bisection is a reasonable thing to do once a working shift is known. Before one is known there is nothing to bisect between.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "The Newton step, and the damping that keeps it honest",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Six routines in `main.py`. Matrices are lists of rows; only `math` is imported.

## Linear algebra

- `solve(a, b)` — Gaussian elimination with partial pivoting, then back substitution.
  A non-square `a`, a mismatched `b`, or a pivot at or below `1e-12` in magnitude
  raises `ValueError`.
- `cholesky(a)` — the lower-triangular `L` with `L Lᵀ = a`. Raises `ValueError` when
  `a` is not square, when it is not symmetric to `1e-12`, or when it is not positive
  definite — which is exactly when a diagonal `total` comes out at or below zero.
- `is_positive_definite(a)` — `True` when `cholesky` succeeds, `False` when it refuses
  on positive-definiteness grounds. A non-square or non-symmetric `a` still raises,
  because that is a caller error rather than a fact about the curvature.

## Curvature, repaired

- `modified_hessian(h, beta=1e-3)` — a **new** matrix: `h` itself when it is already
  positive definite, otherwise `h + tau*I` for the first `tau` in
  `beta, 2*beta, 4*beta, ...` that is. Never mutate `h`.
- `newton_direction(h, g, beta=1e-3)` — `solve(modified_hessian(h, beta), -g)`. Use
  `solve`; do not form an inverse.

## The method

- `damped_newton(f, grad, hess, x0, tol=1e-8, max_iter=100)` — returns
  `(x, iterations)`. Each iteration: stop and return if `norm(grad(x)) <= tol`;
  otherwise take `p = newton_direction(hess(x), grad(x))`, raise `ValueError` if
  `dot(g, p) >= 0`, and backtrack `t = 1, 0.5, 0.25, ...` until

  `f(x + t*p) <= f(x) + 1e-4 * t * dot(g, p)`

  An objective may return `math.inf` where it is undefined, and such a trial is a
  rejection. Sixty-one failed halvings raise `ValueError`.

```text
newton_direction([[4.0, 2.0], [2.0, 4.0]], [-6.0, -6.0])  ->  [1.0, 1.0]
modified_hessian([[-5.88]])                               ->  [[2.312]]
damped_newton(bowl, bowl_gradient, bowl_hessian, [50.0, -30.0])  ->  ([1.0, 1.0], 1)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def solve(a, b):
    """Gaussian elimination with partial pivoting, then back substitution."""
    # your code here


def cholesky(a):
    """Lower triangular L with L L^T = a; ValueError when a is not positive definite."""
    # your code here


def is_positive_definite(a):
    """True when cholesky succeeds; a non-square or non-symmetric a still raises."""
    # your code here


def modified_hessian(h, beta=1e-3):
    """A new matrix: h, or h + tau*I for the first tau in beta, 2*beta, ... that is PD."""
    # your code here


def newton_direction(h, g, beta=1e-3):
    """The step p solving (h + tau*I) p = -g."""
    # your code here


def damped_newton(f, grad, hess, x0, tol=1e-8, max_iter=100):
    """(x, iterations) after Newton steps cut back by an Armijo line search."""
    # your code here


def bowl(v):
    return 2 * v[0] ** 2 + 2 * v[0] * v[1] + 2 * v[1] ** 2 - 6 * v[0] - 6 * v[1]


def bowl_gradient(v):
    return [4 * v[0] + 2 * v[1] - 6, 2 * v[0] + 4 * v[1] - 6]


def bowl_hessian(v):
    return [[4.0, 2.0], [2.0, 4.0]]


def well(v):
    return v[0] ** 4 - 3.0 * v[0] ** 2 + 1.0


def well_gradient(v):
    return [4.0 * v[0] ** 3 - 6.0 * v[0]]


def well_hessian(v):
    return [[12.0 * v[0] ** 2 - 6.0]]


x, steps = damped_newton(bowl, bowl_gradient, bowl_hessian, [50.0, -30.0])
print("bowl:", [round(v, 6) for v in x], "in", steps, "steps")
x, steps = damped_newton(well, well_gradient, well_hessian, [0.1])
print("double well from 0.1:", round(x[0], 6), "in", steps, "steps")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def _square_symmetric(a):
    """The order of a square symmetric matrix, or ValueError saying which it is not."""
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("expected a square matrix")
    for i in range(n):
        for j in range(i + 1, n):
            if abs(float(a[i][j]) - float(a[j][i])) > 1e-12:
                raise ValueError("expected a symmetric matrix")
    return n


def solve(a, b):
    """Gaussian elimination with partial pivoting, then back substitution."""
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("expected a square matrix")
    if len(b) != n:
        raise ValueError("b must have one entry per row")
    m = [[float(v) for v in row] + [float(b[i])] for i, row in enumerate(a)]
    for col in range(n):
        best = col
        for r in range(col + 1, n):
            if abs(m[r][col]) > abs(m[best][col]):
                best = r
        if abs(m[best][col]) <= 1e-12:
            raise ValueError("matrix is singular to working precision")
        m[col], m[best] = m[best], m[col]
        for r in range(col + 1, n):
            factor = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= factor * m[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        total = m[i][n]
        for j in range(i + 1, n):
            total -= m[i][j] * x[j]
        x[i] = total / m[i][i]
    return x


def cholesky(a):
    """Lower triangular L with L L^T = a; ValueError when a is not positive definite."""
    n = _square_symmetric(a)
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            total = float(a[i][j]) - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if total <= 0.0:
                    raise ValueError("matrix is not positive definite")
                lower[i][j] = math.sqrt(total)
            else:
                lower[i][j] = total / lower[j][j]
    return lower


def is_positive_definite(a):
    """True when cholesky succeeds; a non-square or non-symmetric a still raises."""
    _square_symmetric(a)
    try:
        cholesky(a)
    except ValueError:
        return False
    return True


def modified_hessian(h, beta=1e-3):
    """A new matrix: h, or h + tau*I for the first tau in beta, 2*beta, ... that is PD."""
    n = _square_symmetric(h)
    shifted = [[float(v) for v in row] for row in h]
    if is_positive_definite(shifted):
        return shifted
    tau = float(beta)
    for _ in range(200):
        shifted = [[float(h[i][j]) + (tau if i == j else 0.0) for j in range(n)]
                   for i in range(n)]
        if is_positive_definite(shifted):
            return shifted
        tau *= 2.0
    raise ValueError("could not shift the Hessian into positive definiteness")


def newton_direction(h, g, beta=1e-3):
    """The step p solving (h + tau*I) p = -g."""
    return solve(modified_hessian(h, beta), [-float(gi) for gi in g])


def damped_newton(f, grad, hess, x0, tol=1e-8, max_iter=100):
    """(x, iterations) after Newton steps cut back by an Armijo line search."""
    x = [float(v) for v in x0]
    for k in range(max_iter):
        g = grad(x)
        if math.sqrt(sum(gi * gi for gi in g)) <= tol:
            return (x, k)
        p = newton_direction(hess(x), g)
        slope = sum(gi * pi for gi, pi in zip(g, p))
        if slope >= 0.0:
            raise ValueError("the shifted Newton direction is not a descent direction")
        base = f(x)
        t = 1.0
        accepted = False
        for _ in range(61):
            trial = [xi + t * pi for xi, pi in zip(x, p)]
            try:
                value = f(trial)
            except OverflowError:
                value = math.inf
            if math.isfinite(value) and value <= base + 1e-4 * t * slope:
                accepted = True
                break
            t *= 0.5
        if not accepted:
            raise ValueError("no step along the Newton direction was accepted")
        x = [xi + t * pi for xi, pi in zip(x, p)]
    return (x, max_iter)


def bowl(v):
    return 2 * v[0] ** 2 + 2 * v[0] * v[1] + 2 * v[1] ** 2 - 6 * v[0] - 6 * v[1]


def bowl_gradient(v):
    return [4 * v[0] + 2 * v[1] - 6, 2 * v[0] + 4 * v[1] - 6]


def bowl_hessian(v):
    return [[4.0, 2.0], [2.0, 4.0]]


def well(v):
    return v[0] ** 4 - 3.0 * v[0] ** 2 + 1.0


def well_gradient(v):
    return [4.0 * v[0] ** 3 - 6.0 * v[0]]


def well_hessian(v):
    return [[12.0 * v[0] ** 2 - 6.0]]


x, steps = damped_newton(bowl, bowl_gradient, bowl_hessian, [50.0, -30.0])
print("bowl:", [round(v, 6) for v in x], "in", steps, "steps")
x, steps = damped_newton(well, well_gradient, well_hessian, [0.1])
print("double well from 0.1:", round(x[0], 6), "in", steps, "steps")
'''}],
                "hints": [
                    "Write the square-and-symmetric check once, as a helper returning the order, and call it from `cholesky`, `is_positive_definite` and `modified_hessian`. The three then agree about what they refuse.",
                    "`is_positive_definite` should validate the shape *before* the `try`, so a ragged matrix raises rather than quietly returning False — a caller error and a curvature fact should not arrive as the same answer.",
                    "`modified_hessian` must build a new matrix. `[[float(v) for v in row] for row in h]` copies; `list(h)` shares the rows, and a later `+= tau` would edit the caller's Hessian.",
                    "In `damped_newton`, evaluate `f(x)` and the slope once per iteration, outside the halving loop. The Armijo target changes with `t`, but the two quantities it is built from do not.",
                ],
                "tests": [
                    {"name": "Solving, with the pivot the naive order would miss", "code": r'''
_x = solve([[0.0, 1.0], [1.0, 0.0]], [2.0, 3.0])
assert abs(_x[0] - 3.0) < 1e-12 and abs(_x[1] - 2.0) < 1e-12, \
    f"the leading entry is 0, so the rows must be swapped; solve gave {_x!r}, expected [3.0, 2.0]"
_x = solve([[4, 3, 2], [1, 5, 7], [2, 2, 9]], [1, 2, 3])
assert abs(_x[0] - 6.0 / 41.0) < 1e-12, f"solve gave {_x!r}; x[0] should be 6/41"
_a = [[4.0, 3.0], [1.0, 5.0]]
solve(_a, [1.0, 2.0])
assert _a == [[4.0, 3.0], [1.0, 5.0]], "solve must not mutate the matrix it was given"
try:
    solve([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0])
    assert False, "a singular system should raise ValueError"
except ValueError:
    pass
try:
    solve([[1.0, 2.0], [3.0, 4.0]], [1.0])
    assert False, "a right-hand side of the wrong length should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Cholesky, and what it refuses", "code": r'''
import math as _m
_l = cholesky([[4.0, 2.0], [2.0, 4.0]])
assert abs(_l[0][0] - 2.0) < 1e-12 and _l[0][1] == 0.0, f"L came out {_l!r}"
assert abs(_l[1][0] - 1.0) < 1e-12 and abs(_l[1][1] - _m.sqrt(3.0)) < 1e-12, f"L came out {_l!r}"
_a = [[4.0, 12.0, -16.0], [12.0, 37.0, -43.0], [-16.0, -43.0, 98.0]]
_l = cholesky(_a)
for _i in range(3):
    for _j in range(3):
        _got = sum(_l[_i][_k] * _l[_j][_k] for _k in range(3))
        assert abs(_got - _a[_i][_j]) < 1e-9, \
            f"(L L^T)[{_i}][{_j}] is {_got!r}, expected {_a[_i][_j]!r}"
for _bad, _why in [([[1.0, 2.0], [2.0, 1.0]], "indefinite"),
                   ([[0.0, 0.0], [0.0, 0.0]], "only semidefinite"),
                   ([[1.0, 2.0], [3.0, 4.0]], "not symmetric"),
                   ([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], "not square")]:
    try:
        cholesky(_bad)
        assert False, f"cholesky of a matrix that is {_why} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The positive-definiteness verdict", "code": r'''
assert is_positive_definite([[4.0, 2.0], [2.0, 4.0]]) is True, "eigenvalues 2 and 6 are both positive"
assert is_positive_definite([[1.0, 0.0], [0.0, 1.0]]) is True, "the identity is positive definite"
assert is_positive_definite([[1.0, 2.0], [2.0, 1.0]]) is False, "eigenvalues -1 and 3"
assert is_positive_definite([[-5.88]]) is False, "a negative curvature is not positive definite"
assert is_positive_definite([[1.0, 1.0], [1.0, 1.0]]) is False, \
    "a singular semidefinite matrix has no Cholesky factor with a positive diagonal"
try:
    is_positive_definite([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert False, "a non-square matrix is a caller error and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Shifting a Hessian until it curves upwards", "code": r'''
_h = [[4.0, 2.0], [2.0, 4.0]]
_m1 = modified_hessian(_h)
assert _m1 == [[4.0, 2.0], [2.0, 4.0]], f"an already positive definite Hessian is returned as is; got {_m1!r}"
_m1[0][0] = 99.0
assert _h == [[4.0, 2.0], [2.0, 4.0]], "modified_hessian must return a copy, not the caller's matrix"
_m2 = modified_hessian([[-5.88]])
assert abs(_m2[0][0] - 2.312) < 1e-9, \
    f"thirteen doublings of 1e-3 give tau = 8.192, so the shift is 2.312; got {_m2[0][0]!r}"
_m3 = modified_hessian([[1.0, 2.0], [2.0, 1.0]])
assert abs(_m3[0][0] - 2.024) < 1e-9 and _m3[0][1] == 2.0, \
    f"only the diagonal is shifted; got {_m3!r}"
assert is_positive_definite(_m3) is True, "the point of the shift is that the result is positive definite"
'''},
                    {"name": "The Newton direction, and the one it repairs", "code": r'''
_p = newton_direction([[4.0, 2.0], [2.0, 4.0]], [-6.0, -6.0])
assert abs(_p[0] - 1.0) < 1e-12 and abs(_p[1] - 1.0) < 1e-12, \
    f"the step from the origin of the bowl is [1, 1]; got {_p!r}"
_g = [-0.596]
_p = newton_direction([[-5.88]], _g)
assert _p[0] > 0.0, f"the shifted step must go downhill, which here is to the right; got {_p!r}"
assert sum(a * b for a, b in zip(_g, _p)) < 0.0, "a descent direction has a negative slope"
_unshifted = [-(-0.596) / (-5.88)]
assert _unshifted[0] < 0.0, "the unmodified Newton step climbs towards the ridge, which is the point"
'''},
                    {"name": "One step on a quadratic, from anywhere", "code": r'''
for _start in ([0.0, 0.0], [50.0, -30.0], [-1000.0, 2000.0]):
    _x, _steps = damped_newton(bowl, bowl_gradient, bowl_hessian, _start)
    assert _steps == 1, f"a quadratic is solved in one Newton step; from {_start!r} it took {_steps}"
    assert abs(_x[0] - 1.0) < 1e-9 and abs(_x[1] - 1.0) < 1e-9, \
        f"from {_start!r} the run ended at {_x!r}, expected [1.0, 1.0]"
'''},
                    {"name": "Damping rescues a start the full step would ruin", "code": r'''
import math as _m


def _f(v):
    if v[0] <= 0.0:
        return _m.inf
    return v[0] - _m.log(v[0])


_grad = lambda v: [1.0 - 1.0 / v[0]]
_hess = lambda v: [[1.0 / (v[0] * v[0])]]
_p = newton_direction(_hess([2.5]), _grad([2.5]))
assert abs(_p[0] + 3.75) < 1e-9, f"the Newton step at 2.5 is -3.75; got {_p!r}"
assert _f([2.5 + _p[0]]) == _m.inf, "a full step from 2.5 lands outside the domain"
for _start, _limit in (([0.5], 8), ([2.5], 12)):
    _x, _steps = damped_newton(_f, _grad, _hess, _start)
    assert abs(_x[0] - 1.0) < 1e-8, f"from {_start!r} the run ended at {_x!r}, expected 1.0"
    assert _steps <= _limit, f"from {_start!r} it took {_steps} iterations, which is too many"
'''},
                    {"name": "A start where the curvature is wrong", "code": r'''
import math as _m
_x, _steps = damped_newton(well, well_gradient, well_hessian, [0.1])
assert abs(_x[0] - _m.sqrt(1.5)) < 1e-6, \
    f"from 0.1 the modified step goes right, to sqrt(1.5); the run ended at {_x!r}"
assert _steps <= 15, f"it should take a handful of iterations; it took {_steps}"
assert well(_x) < well([0.1]), "the run must end lower than it started"
_x, _steps = damped_newton(well, well_gradient, well_hessian, [-0.1])
assert abs(_x[0] + _m.sqrt(1.5)) < 1e-6, \
    f"the mirror start should reach the mirror minimum; the run ended at {_x!r}"
'''},
                    {"name": "What the script reports", "code": r'''
_lines = _out.strip().split("\n")
assert len(_lines) == 2, f"main.py should print two lines; it printed {len(_lines)}:\n{_out}"
assert _lines[0] == "bowl: [1.0, 1.0] in 1 steps", \
    f"the first line was {_lines[0]!r}, expected 'bowl: [1.0, 1.0] in 1 steps'"
assert _lines[1].startswith("double well from 0.1: 1.224745 in "), \
    f"the second line was {_lines[1]!r}; the run should land on sqrt(1.5) = 1.224745"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Constraints, multipliers and the KKT conditions",
            "summary": "What a constraint costs, why the price cannot be negative, and how to check an answer.",
            "concepts": [
                "At a constrained optimum the level set of f is tangent to the constraint, so their gradients are parallel",
                "The multiplier is the derivative of the optimal value with respect to the constraint's right-hand side",
                "An inequality is either slack, in which case its multiplier is zero, or tight, in which case it acts as an equality",
                "Dual feasibility lambda >= 0 comes from requiring that no feasible direction decreases f",
                "Complementary slackness lambda_i g_i(x) = 0 is the two cases written as one equation",
                "An equality-constrained quadratic program is one symmetric linear system, the KKT system",
                "KKT is necessary only under a constraint qualification, and sufficient only when the problem is convex",
            ],
            "read": [
                {
                    "title": "A multiplier is a price",
                    "minutes": 13,
                    "body": r'''
Twelve metres of fencing and a rectangular pen to enclose, all four sides fenced. Call
the sides $x$ and $y$. The area $xy$ has no maximum on its own — take $x$ and $y$ as
large as you like — so the interesting question exists only because the fence runs out:
maximise $xy$ subject to $2x + 2y = 12$.

Draw it. The constraint is a straight line in the $(x,y)$ plane. The level curves of the
area are hyperbolas $xy = k$, one for each area, further from the origin as $k$ grows.
Now walk along the line from one end towards the other and watch which hyperbola you are
standing on. Near the ends the area is small; in the middle it is larger. The walk stops
improving exactly where the line stops crossing to higher hyperbolas — which is where
the line touches one instead of cutting it.

Two curves that touch have the same tangent, so they have parallel normals, and the
normal to a level curve is the gradient of the function whose level curve it is. So at
the best point,

$$\nabla f = \lambda \nabla g$$

for some number $\lambda$, where $g$ is the constraint function. Here $\nabla f = (y,x)$
and $\nabla g = (2,2)$, so $y = 2\lambda$ and $x = 2\lambda$: the pen is a square,
$x = y = 3$, the area is $9$, and $\lambda = 1.5$.

The number $\lambda$ looks like a leftover of the algebra — the ratio between two
parallel vectors, of no interest in itself. It is the most useful thing in the
calculation.

## What the multiplier is worth

Suppose you can buy ten more centimetres of fence. What is that worth? The optimal pen
for a perimeter $b$ is a square of side $b/4$, so the best area is $b^2/16$, and its
derivative is $b/8$, which at $b = 12$ is $1.5$ — the multiplier, exactly.

```python
def best_area(perimeter):
    side = perimeter / 4.0
    return side * side

print("best area at 12.0 m:", best_area(12.0))
print("best area at 12.1 m:", best_area(12.1))
print("actual increase:", round(best_area(12.1) - best_area(12.0), 6))
print("multiplier times 0.1:", round(1.5 * 0.1, 6))
```

The extra ten centimetres are worth $0.150625$ square metres, against the multiplier's
prediction of $0.15$; the difference is the second-order term, and it shrinks with the
square of the increment. So $\lambda$ is the rate at which the best achievable objective
changes as the constraint is relaxed. It is a price, in units of objective per unit of
constraint, and that is the reading to carry into everything that follows. When the next
module reports that a carpentry hour is worth $5$ euros of profit, it is reporting this
number.

## One-sided constraints

Most real constraints are one-sided: *at most* twelve metres of fence, *at most* a
hundred hours of finishing. Write them as $g(x) \le 0$. The tangency argument does not
transfer unchanged, and taking two cases seriously is enough to derive everything that
is different.

**The constraint is slack**, $g(x^{*}) < 0$. Then a small ball around $x^{*}$ is
entirely feasible, so nothing about the constraint reaches the local problem, and
optimality is the ordinary $\nabla f = 0$. In the tangency equation that corresponds to
$\lambda = 0$: the price of a resource you have not used up is zero.

**The constraint is tight**, $g(x^{*}) = 0$. The tangency argument runs as before, so
$\nabla f = -\lambda \nabla g$ for some $\lambda$ — the minus sign is a convention that
makes the next paragraph read cleanly. But now there is a sign to settle that the
equality case did not have. From $x^{*}$, the directions $d$ that stay feasible to first
order are those with $\nabla g \cdot d \le 0$. For $x^{*}$ to be a minimum, none of them
may decrease $f$, so $\nabla f \cdot d \ge 0$ for every such $d$. Substituting,
$-\lambda\,\nabla g \cdot d \ge 0$ whenever $\nabla g \cdot d \le 0$, and that holds for
every such $d$ exactly when $\lambda \ge 0$.

A negative multiplier would say the objective improves in a direction the constraint
allows, which is a statement that the point is not optimal. So the sign is not a
convention; it is the optimality test.

The two cases can be written as one equation. Either $\lambda = 0$ or $g(x^{*}) = 0$,
which is $\lambda\, g(x^{*}) = 0$ — complementary slackness. Collecting everything, for
$\min f(x)$ subject to $g_i(x) \le 0$:

$$\nabla f(x) + \sum_i \lambda_i \nabla g_i(x) = 0, \qquad g_i(x) \le 0, \qquad
\lambda_i \ge 0, \qquad \lambda_i g_i(x) = 0$$

These are the Karush-Kuhn-Tucker conditions, and each of the four came out of the
picture rather than being posted on a wall.

## The worked example the lab checks

Minimise $(x-2)^2 + (y-1)^2$ subject to $x + y \le 2$, $x \ge 0$ and $y \ge 0$: the
nearest feasible point to $(2,1)$. The unconstrained minimiser is $(2,1)$ itself, whose
coordinates sum to $3$, so the first constraint is violated and must be tight at the
answer. On the line $x + y = 2$ the nearest point to $(2,1)$ is its perpendicular
projection: move $(3-2)/2 = 0.5$ along $(1,1)$ in the negative direction, arriving at
$(1.5, 0.5)$.

```python
x, y, lam = 1.5, 0.5, 1.0
gradient = (2.0 * (x - 2.0), 2.0 * (y - 1.0))
print("gradient of f:", gradient)
print("stationarity residual:", (gradient[0] + lam, gradient[1] + lam))
print("constraint x + y - 2:", x + y - 2.0)
print("complementary slackness:", lam * (x + y - 2.0))
print("objective:", (x - 2.0) ** 2 + (y - 1.0) ** 2)
```

Every one of the four conditions holds, with $\lambda = (1, 0, 0)$: stationarity is
exactly zero, the point is feasible, the multipliers are non-negative, and the two
inactive constraints carry zero prices. And the price means what it meant for the fence.
Relax the budget to $x + y \le b$ and the optimal value is $(3-b)^2/2$:

```python
def best(b):
    step = (3.0 - b) / 2.0
    return ((2.0 - step, 1.0 - step), 2.0 * step * step)

for b in (2.0, 2.1):
    point, value = best(b)
    print(f"b={b}: x={point[0]:.4f}  y={point[1]:.4f}  f={value:.6f}")
print("predicted change:", -1.0 * 0.1)
print("actual change:", round(best(2.1)[1] - best(2.0)[1], 6))
```

A tenth more budget buys $0.095$ of objective against the predicted $0.1$, and the sign
is negative because relaxing a constraint on a minimisation can only help.

## The mistake

The one people actually make is dropping the sign condition: deciding a constraint is
active and then treating it exactly like an equality. It is tempting because once you
have decided, the algebra genuinely is identical — the same linear system, the same
solve.

Minimise $(x-2)^2$ subject to $x \ge 1$, written as $g(x) = 1 - x \le 0$. Force the
constraint active. Then $x = 1$ and stationarity reads $2(x - 2) - \lambda = 0$, giving
$\lambda = -2$.

```python
x = 1.0
lam = 2.0 * (x - 2.0)          # from 2(x - 2) - lam = 0 at the forced-active point
print("multiplier at the forced-active point:", lam)
print("is it dual feasible:", lam >= 0.0)
print("value there:", (x - 2.0) ** 2, "against 0.0 at the unconstrained minimiser")
```

The negative multiplier is the entire message. It says the objective can be decreased by
moving in a direction the constraint permits, so this constraint should never have been
treated as binding. Release it and the answer is $x = 2$ with $\lambda = 0$. That is
precisely what the lab's `active_set_qp` does with the sign: it guesses which
constraints are active, solves the resulting equality problem, and discards the guess
the moment a multiplier comes out negative.

A smaller misreading is treating $\lambda_i = 0$ as "this constraint does not matter".
It says the constraint is not binding at the current data. Tighten the right-hand side
far enough and it will bind, and the price will stop being zero.

## Where it stops holding

The KKT conditions are necessary at an optimum only under a constraint qualification.
Minimise $x$ subject to $x^2 \le 0$. The feasible set is the single point $0$, so $0$ is
the optimum by default. But there $\nabla f = 1$ and $\nabla g = 2x = 0$, and
stationarity reads $1 + \lambda \cdot 0 = 0$, which no $\lambda$ satisfies. KKT fails at
the optimum, because a constraint gradient that vanishes cannot balance anything.
Conditions such as linear independence of the active constraint gradients, or Slater's
condition for a convex problem, exclude this; for the linear constraints in this module
and the next, they hold automatically.

Sufficiency is a separate question. For a general problem KKT is necessary and not
sufficient, and a KKT point may be a maximum or a saddle — the same complaint module 3
made about $\nabla f = 0$, now with constraints attached. When $f$ and the $g_i$ are all
convex, the conditions are both necessary and sufficient, which is what turns the lab's
enumeration into a proof rather than a search.

The enumeration is also exponential: with $m$ inequalities there are $2^m$ possible
active sets. That is fine for the handful here and hopeless at a thousand, which is why
real solvers move one constraint at a time rather than trying every subset. The simplex
method of the next module is exactly that idea, for the case where everything in sight
is linear.

## The lab

**KKT residuals and the price of a constraint** builds `matvec`, `transpose`,
`quad_value`, then `solve_eq_qp`, which assembles the symmetric KKT system

```text
[ Q   A^T ] [ x  ]   [ -c ]
[ A    0  ] [ nu ] = [  b ]
```

and solves it with module 3's `solve`; then `kkt_residuals`, which reports the four
conditions as four non-negative numbers; and `active_set_qp`, which enumerates the
subsets, keeps the candidates that are primal and dual feasible, and returns the best.
The tests include the projection above, a problem whose unconstrained optimum is already
feasible, one with two constraints active at once, and a duplicated constraint whose KKT
system is singular and has to be stepped over rather than crashed on.
''',
                },
            ],
            "quiz": {
                "title": "Prices, signs and what a KKT point proves",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A production plan is optimal and the multiplier on the machine-hours constraint is $12$. What does the $12$ mean?",
                        "opts": [
                            "Twelve more machine hours would be needed before the plan changes at all",
                            "One more machine hour is worth about twelve more units of objective at the optimum",
                            "The constraint is violated by twelve units, which is the amount to be corrected",
                            "Twelve of the decision variables are being held at their bounds by this one constraint",
                        ],
                        "a": 1,
                        "whys": [
                            r"How far the right-hand side can move before the *basis* changes is a real and different quantity — the range over which the price stays valid. The price itself is a rate, and it applies to the very first extra hour.",
                            r"The multiplier is the derivative of the optimal value with respect to the right-hand side.",
                            r"A multiplier is not a residual. At an optimum every constraint is satisfied, and a constraint carrying a positive price is satisfied with equality — its violation is exactly zero.",
                            r"The multiplier is one number attached to one constraint and says nothing about how many variables are at their bounds. Those variables have multipliers of their own, on their own constraints.",
                        ],
                        "why": r'''
The multiplier on a constraint is the derivative of the optimal objective value with
respect to that constraint's right-hand side. On the twelve-metre fence, relaxing the
perimeter by $0.1$ raised the best area by $0.150625$ against the multiplier's
prediction of $1.5 \times 0.1 = 0.15$, the gap being the second-order term. So a
multiplier of $12$ says the first extra machine hour buys about twelve units of
objective, which is exactly the number you compare against the price of renting one. How
far that rate stays valid is a separate question, and a genuinely important one, but it
is not what the multiplier reports.
''',
                    },
                    {
                        "q": "Solving a problem with an inequality forced to be active gives a multiplier of $-2$. What does that tell you?",
                        "opts": [
                            "That the problem is infeasible, since a feasible problem cannot produce a negative price",
                            "That the guess was wrong: the objective improves in a direction the constraint allows, so it is not active",
                            "That the sign convention was written the other way round, and the multiplier is really $+2$",
                            "That the constraint is active but redundant, since it is implied by the others already present in the system",
                        ],
                        "a": 1,
                        "whys": [
                            r"Infeasibility means no point satisfies the constraints, and the point that produced this multiplier satisfies all of them. Solving the equality problem always returns *some* point; the sign is what tells you whether to keep it.",
                            r"Dual feasibility is an optimality test, and this candidate fails it.",
                            r"A sign convention decides how $\lambda$ enters the Lagrangian, and once fixed it is fixed for every constraint. Re-reading the negative one as positive would silently accept a point where $f$ can still be reduced.",
                            r"Redundancy is a statement about the constraint set and has nothing to do with the sign of a multiplier. A redundant constraint that happens to be tight at the optimum carries a perfectly ordinary non-negative price, often zero.",
                        ],
                        "why": r'''
The sign condition came from requiring that no feasible direction decreases $f$. A
negative multiplier says the opposite: there is a direction the constraint permits along
which the objective falls, so the point is not a minimum and the assumption that this
constraint binds was wrong. On $\min (x-2)^2$ subject to $x \ge 1$, forcing the
constraint active gives $x = 1$ and $\lambda = -2$; releasing it gives $x = 2$ with
$\lambda = 0$ and a strictly better value. An active-set method depends on this: it
guesses a set, solves the equality problem, and throws the guess away the moment a
multiplier comes out negative.
''',
                    },
                    {
                        "q": "Why is complementary slackness written as $\\lambda_i g_i(x) = 0$ rather than as two separate rules?",
                        "opts": [
                            "Because it is one equation per constraint, and a solver needs equations rather than case distinctions",
                            "Because the product form also allows both factors to be non-zero, which the two cases forbid",
                            "Because $\\lambda_i$ and $g_i(x)$ always have opposite signs, so their product is the only thing that can vanish",
                            "Because it is the definition, and the two-case description is an informal gloss on it",
                        ],
                        "a": 0,
                        "whys": [
                            r"A product that has to vanish encodes an exclusive-or between two conditions in a form that can be solved rather than branched on.",
                            r"The product form allows nothing of the kind: a product of two real numbers is zero exactly when at least one factor is, which is precisely the two cases. If both could be non-zero the equation would be false.",
                            r"They do have opposite signs, since $\lambda_i \ge 0$ and $g_i(x) \le 0$ — but that makes the product non-positive, not zero. Requiring zero is a genuine extra condition beyond the two feasibility conditions.",
                            r"The two cases came first and the product came second; the derivation runs from the slack and tight cases to the equation, not the other way. Calling the derivation informal hides where the condition came from.",
                        ],
                        "why": r'''
Either the constraint is slack, in which case a whole neighbourhood is feasible and the
constraint has no local effect, so $\lambda_i = 0$; or it is tight, $g_i(x) = 0$, and it
acts as an equality with a non-negative price. The product $\lambda_i g_i(x)$ vanishes
exactly in those two situations, so the equation is the disjunction rather than a
consequence of it. Writing it as a product turns a case analysis into one more row of a
system of equations, which is what lets a solver treat all four KKT conditions
uniformly. It is also what `kkt_residuals` measures: the norm of the vector of products,
which is zero at a genuine optimum and grows the moment a price is charged for a
constraint with slack in it.
''',
                    },
                    {
                        "q": "Minimise $x$ subject to $x^2 \\le 0$. The optimum is $x = 0$, yet no multiplier satisfies stationarity there. What has gone wrong?",
                        "opts": [
                            "The feasible set is a single point, and KKT does not apply when the optimum is unique",
                            "The constraint gradient vanishes at the optimum, so it cannot balance the objective gradient",
                            "The constraint is not convex, and KKT requires convexity of every constraint function",
                            "The objective is linear, so its gradient is never zero and stationarity can never be satisfied",
                        ],
                        "a": 1,
                        "whys": [
                            r"Uniqueness is not the difficulty. Plenty of problems have a single feasible point described by constraints whose gradients are independent, and KKT holds at every one of them.",
                            r"Stationarity asks for $\nabla f$ to be a non-negative combination of the active constraint gradients, and the only one available here is the zero vector.",
                            r"$x^2$ is convex, so this problem is a convex objective over a convex feasible set. Convexity is what makes KKT *sufficient* once it holds; it is a constraint qualification that makes it necessary, and this problem fails the qualification while satisfying the convexity.",
                            r"A linear objective is the ordinary case in the next module, where every KKT condition holds and the multipliers are the dual prices. Stationarity does not require $\nabla f = 0$; it requires $\nabla f$ to be balanced by the constraint terms.",
                        ],
                        "why": r'''
Stationarity says $\nabla f$ must be expressible as a non-negative combination of the
gradients of the active constraints. Here $\nabla f = 1$ and the single active
constraint has $\nabla g = 2x = 0$ at the optimum, so the available combinations are all
zero and none of them is $-1$. The failure is not about convexity, which this problem
has, but about a constraint qualification: the active gradients have to be rich enough
to describe the feasible directions, and a vanishing gradient describes nothing.
Linear independence of the active gradients is the usual sufficient condition, and for
the linear constraints in this course it holds without being checked.
''',
                    },
                    {
                        "q": "`active_set_qp` enumerates subsets of the constraints. For a convex quadratic with linear constraints, why does the best surviving candidate have to be the global optimum?",
                        "opts": [
                            "Because the enumeration is exhaustive, and comparing objective values across all feasible points settles it",
                            "Because for a convex problem the KKT conditions are sufficient, and every surviving candidate satisfies all four",
                            "Because the objective is quadratic, so it has exactly one stationary point and the search cannot miss it",
                            "Because a linear constraint set is a polytope, and a quadratic is always minimised at one of that polytope's vertices",
                        ],
                        "a": 1,
                        "whys": [
                            r"The enumeration is exhaustive over active sets, not over feasible points — there are infinitely many of those. It is the sufficiency of KKT that lets a finite list of candidates settle an infinite question.",
                            r"Sufficiency is what turns a candidate that passes the tests into a proven optimum.",
                            r"The quadratic's own stationary point is the unconstrained minimiser, and here it is usually infeasible; the answer sits on the boundary where the objective is not stationary at all. A singular $Q$ would also give a whole flat of stationary points.",
                            r"That is true of a *linear* objective, and it is the fact the next module's simplex method runs on. A quadratic is minimised wherever its level sets first touch the polytope, which is generally in the middle of a face, as $(1.5, 0.5)$ is.",
                        ],
                        "why": r'''
Enumerating active sets produces a finite list of candidate points, each of which
satisfies stationarity by construction and is then filtered for primal feasibility and
for non-negative multipliers. So every survivor satisfies all four KKT conditions. For a
convex objective over a convex feasible set those conditions are sufficient, meaning any
point satisfying them is a global minimiser — so the first survivor is already the
answer and the comparison of objective values only settles ties. Drop convexity and the
whole argument collapses: the survivors would be stationary points of unknown character,
and the enumeration would be a heuristic. Drop the finiteness and it stops being an
algorithm, which is why $2^m$ is affordable at $m = 3$ and absurd at $m = 300$.
''',
                    },
                    {
                        "q": "The KKT system of an equality-constrained quadratic program is $Qx + A^{\\mathsf{T}}\\nu = -c$ together with $Ax = b$. Why is it solved as one system rather than by eliminating $\\nu$?",
                        "opts": [
                            "Because $\\nu$ cannot be eliminated: it appears in both blocks and no substitution removes it",
                            "Because eliminating it needs $Q^{-1}$, which is a worse-conditioned computation and fails when $Q$ is singular",
                            "Because the combined matrix is positive definite, so solving it in one piece is the more stable of the two routes",
                            "Because the multipliers are the answer being sought, and eliminating them would discard the prices",
                        ],
                        "a": 1,
                        "whys": [
                            r"It can be eliminated, and the resulting system in $\nu$ alone is the standard *Schur complement* form, $AQ^{-1}A^{\mathsf{T}}\nu = AQ^{-1}c + b$. That is a real method with real uses; what it costs is an inverse.",
                            r"Elimination goes through $Q^{-1}$, and module 3 already argued against forming inverses.",
                            r"The combined matrix is emphatically not positive definite — the zero block on its diagonal guarantees it has negative eigenvalues, which is why a Cholesky factorisation of it fails and the lab uses the general `solve` instead.",
                            r"The multipliers survive either route: the eliminated system solves for $\nu$ directly and recovers $x$ afterwards. Both orders produce both halves of the answer.",
                        ],
                        "why": r'''
Eliminating $\nu$ means solving the first block for $x$, which requires inverting $Q$,
and then substituting into $Ax = b$. That is the Schur complement form and it is a
perfectly real method — when $Q$ is well conditioned and easy to invert, such as a
diagonal matrix. In general it forms an inverse, which module 3 argued against on both
accuracy and cost, and it fails outright when $Q$ is singular even though the
constrained problem may still be perfectly well posed, because the constraints can pin
down the directions $Q$ says nothing about. Solving the whole indefinite system in one
elimination avoids both. Note that it *is* indefinite: the zero block makes a Cholesky
factorisation impossible, so this is the one place in the course where the general
pivoting solve is the right tool.
''',
                    },
                ],
            },
            "blanks": {
                "title": "The four residuals, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "kkt_residuals — five holes, and four conditions that each become one number",
                "brief": r'''
The whole of the KKT test, as four non-negative numbers that are all zero at an optimum.
`matvec`, `transpose` and `norm` are assumed to exist.

Nothing runs here. Filled in correctly, the point $(1.5, 0.5)$ with multipliers
$(1, 0, 0)$ returns four exact zeros for the projection problem of this module.
''',
                "listing": r'''
def kkt_residuals(q, c, g, h, x, lam):
    """The four KKT conditions of min (1/2) x.Qx + c.x subject to Gx <= h."""
    slack = [___ for row, hi in zip(matvec(g, x), h)]
    stationarity = norm([a + b + d for a, b, d in
                         zip(matvec(q, x), c, matvec(___, lam))])
    primal = norm([___ for s in slack])
    dual = norm([___ for li in lam])
    complementary = norm([___ for li, s in zip(lam, slack)])
    return (stationarity, primal, dual, complementary)
''',
                "blanks": [
                    {
                        "prompt": "The slack in one constraint, negative when there is room left.",
                        "hole": "?",
                        "opts": ["row - hi", "hi - row", "abs(row - hi)", "row"],
                        "a": 0,
                        "why": "The constraint is written Gx <= h, so the quantity that must be at or below zero is Gx minus h. Every later line reads its sign, so getting it backwards inverts three of the four residuals at once.",
                        "whys": [
                            "The constraint is written Gx <= h, so the quantity that must be at or below zero is Gx minus h. Every later line reads its sign, so getting it backwards inverts three of the four residuals at once.",
                            "This is the amount of room left rather than the violation, so it is positive at a feasible point. The primal residual then reports every satisfied constraint as violated, and a genuinely violated one as fine.",
                            "Taking the absolute value throws away the only thing the sign was carrying. A constraint with room to spare and one violated by the same amount become indistinguishable, and the primal residual is then non-zero at every point that is not exactly on the boundary.",
                            "Dropping the right-hand side measures the constraint's left side against zero, which is a different constraint. For x + y <= 2 this reports a slack of 2 at the feasible point (1.5, 0.5), so nothing downstream means anything.",
                        ],
                    },
                    {
                        "prompt": "What lam is multiplied by in the stationarity sum.",
                        "hole": "?",
                        "opts": ["transpose(g)", "g", "q", "transpose(q)"],
                        "a": 0,
                        "why": "Stationarity adds one copy of each constraint's gradient, weighted by its multiplier. The gradient of constraint i is row i of G, so the weighted sum over constraints is G transposed times lam, and the result has one entry per variable.",
                        "whys": [
                            "Stationarity adds one copy of each constraint's gradient, weighted by its multiplier. The gradient of constraint i is row i of G, so the weighted sum over constraints is G transposed times lam, and the result has one entry per variable.",
                            "G has one row per constraint and one column per variable, so this multiplies rows by a vector of multipliers whose length is the number of constraints — a shape error unless the two counts happen to match, and silently the wrong sum when they do.",
                            "Q is the curvature of the objective and has nothing to do with the constraint gradients. It is already used one term to the left, in matvec(q, x).",
                            "Q is symmetric, so transposing it changes nothing and this fails in exactly the same way as using it directly — while looking as though a shape had been fixed.",
                        ],
                    },
                    {
                        "prompt": "The contribution of one constraint to the primal-feasibility residual.",
                        "hole": "?",
                        "opts": ["max(0.0, s)", "s", "abs(s)", "min(0.0, s)"],
                        "a": 0,
                        "why": "Only a positive slack is a violation; a negative one is a satisfied constraint with room to spare and must contribute nothing. Clipping at zero is what makes the residual zero over the whole feasible region rather than only on its boundary.",
                        "whys": [
                            "Only a positive slack is a violation; a negative one is a satisfied constraint with room to spare and must contribute nothing. Clipping at zero is what makes the residual zero over the whole feasible region rather than only on its boundary.",
                            "Summing the raw slacks lets a comfortably satisfied constraint cancel a violated one, so a point outside the feasible set can report a residual of zero. It also reports a strictly feasible point as failing.",
                            "The absolute value counts room to spare as though it were violation, so the residual is zero only for points on every constraint boundary at once — usually no points at all, and never the interior optimum of an unconstrained-feasible problem.",
                            "This keeps exactly the satisfied constraints and discards the violated ones, which is the reverse of what a violation measure is for. An infeasible point comes out with a smaller residual than a feasible one.",
                        ],
                    },
                    {
                        "prompt": "The contribution of one multiplier to the dual-feasibility residual.",
                        "hole": "?",
                        "opts": ["max(0.0, -li)", "max(0.0, li)", "abs(li)", "li"],
                        "a": 0,
                        "why": "Dual feasibility asks for lam >= 0, so the failure to measure is how far below zero a multiplier has fallen. A price of 12 is perfectly legal and must contribute nothing.",
                        "whys": [
                            "Dual feasibility asks for lam >= 0, so the failure to measure is how far below zero a multiplier has fallen. A price of 12 is perfectly legal and must contribute nothing.",
                            "This penalises the legal multipliers and ignores the illegal ones, so a correct answer with a price of 12 reports a residual of 12 while a point with a price of -2 reports zero.",
                            "The magnitude treats a healthy positive price as a defect. Every problem with a binding constraint then fails its own optimality test, which is every interesting problem in the module.",
                            "The raw value is negative exactly when the condition fails, so the residual goes down as the violation gets worse and a norm built from it cannot distinguish the two directions at all.",
                        ],
                    },
                    {
                        "prompt": "The contribution of one constraint to the complementary-slackness residual.",
                        "hole": "?",
                        "opts": ["li * s", "li + s", "max(li, s)", "li * max(0.0, s)"],
                        "a": 0,
                        "why": "Complementary slackness is the statement that the product of the price and the slack vanishes for every constraint, so the product itself is the residual — non-zero exactly when a price is charged for a constraint that still has room.",
                        "whys": [
                            "Complementary slackness is the statement that the product of the price and the slack vanishes for every constraint, so the product itself is the residual — non-zero exactly when a price is charged for a constraint that still has room.",
                            "A sum is zero when the two terms cancel, so a price of 2 on a constraint with slack -2 would report perfect complementarity. That is the exact combination the condition exists to forbid.",
                            "The larger of the two is zero only when both are, which is far stricter than the condition: an active constraint with a positive price satisfies complementary slackness and fails this test.",
                            "Clipping the slack first means the residual only ever sees violated constraints, so a positive price on a strictly slack constraint — the whole failure mode being tested for — is silently reported as fine.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "KKT residuals and the price of a constraint",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
The problem throughout is

$$\min \tfrac{1}{2}\, x \cdot Qx + c \cdot x \quad \text{subject to} \quad Gx \le h$$

with `Q` symmetric positive definite. Six routines in `main.py`; only `math` and
`itertools.combinations` are imported.

## Helpers

- `transpose(a)`, `matvec(a, v)` — a row whose length does not match `v` raises
  `ValueError`.
- `norm(v)` — the Euclidean length; the empty vector has length `0.0`.
- `quad_value(q, c, x)` — the objective above.

## Equalities

- `solve_eq_qp(q, c, a, b)` — minimise the same objective subject to `a x = b`, by
  assembling and solving the KKT system

```text
[ Q   A^T ] [ x  ]   [ -c ]
[ A    0  ] [ nu ] = [  b ]
```

  Returns `(x, nu)`. Reuse module 3's `solve`: the matrix is symmetric but indefinite,
  so Cholesky is unavailable. A mismatched `c` or `b` raises `ValueError`, and so does
  a singular system — which is what a repeated constraint produces.

## Inequalities

- `kkt_residuals(q, c, g, h, x, lam)` — the tuple
  `(stationarity, primal, dual, complementary)`, each a norm and each zero exactly when
  its condition holds.
- `active_set_qp(q, c, g, h, tol=1e-9)` — enumerate every subset of the constraints of
  size at most the number of variables; for each, solve the equality problem with those
  rows as equalities, skipping a singular system; keep the result when every multiplier
  is at or above `-tol` and every constraint holds to `tol`; return the surviving
  `(x, lam)` of smallest objective. Multipliers of inactive constraints are exactly
  `0.0`. Raise `ValueError` when nothing survives, and when there are more than twelve
  constraints.

```text
active_set_qp([[2,0],[0,2]], [-4,-2], [[1,1],[-1,0],[0,-1]], [2,0,0])
    ->  ([1.5, 0.5], [1.0, 0.0, 0.0])
```
''',
                "files": [{"name": "main.py", "content": r'''
import math
from itertools import combinations


def transpose(a):
    """Rows become columns."""
    # your code here


def matvec(a, v):
    """Matrix times vector; a row of the wrong width raises ValueError."""
    # your code here


def norm(v):
    """Euclidean length; the empty vector has length 0.0."""
    # your code here


def quad_value(q, c, x):
    """0.5 * x.Qx + c.x."""
    # your code here


def solve(a, b):
    """Gaussian elimination with partial pivoting, as in module 3."""
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("expected a square matrix")
    if len(b) != n:
        raise ValueError("b must have one entry per row")
    m = [[float(v) for v in row] + [float(b[i])] for i, row in enumerate(a)]
    for col in range(n):
        best = col
        for r in range(col + 1, n):
            if abs(m[r][col]) > abs(m[best][col]):
                best = r
        if abs(m[best][col]) <= 1e-12:
            raise ValueError("matrix is singular to working precision")
        m[col], m[best] = m[best], m[col]
        for r in range(col + 1, n):
            factor = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= factor * m[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        total = m[i][n]
        for j in range(i + 1, n):
            total -= m[i][j] * x[j]
        x[i] = total / m[i][i]
    return x


def solve_eq_qp(q, c, a, b):
    """(x, nu) from the KKT system of the equality-constrained problem."""
    # your code here


def kkt_residuals(q, c, g, h, x, lam):
    """(stationarity, primal, dual, complementary), each zero when its condition holds."""
    # your code here


def active_set_qp(q, c, g, h, tol=1e-9):
    """(x, lam) by trying every active set and keeping the feasible ones."""
    # your code here


Q = [[2.0, 0.0], [0.0, 2.0]]
C = [-4.0, -2.0]
G = [[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
H = [2.0, 0.0, 0.0]

x, lam = active_set_qp(Q, C, G, H)
print("closest feasible point:", [round(v, 6) for v in x])
print("multipliers:", [round(v, 6) for v in lam])
print("residuals:", [round(r, 12) for r in kkt_residuals(Q, C, G, H, x, lam)])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
from itertools import combinations


def transpose(a):
    """Rows become columns."""
    if not a:
        raise ValueError("cannot transpose an empty matrix")
    return [[float(a[i][j]) for i in range(len(a))] for j in range(len(a[0]))]


def matvec(a, v):
    """Matrix times vector; a row of the wrong width raises ValueError."""
    if any(len(row) != len(v) for row in a):
        raise ValueError("each row must have one entry per variable")
    return [sum(float(x) * float(y) for x, y in zip(row, v)) for row in a]


def norm(v):
    """Euclidean length; the empty vector has length 0.0."""
    return math.sqrt(sum(float(x) * float(x) for x in v))


def quad_value(q, c, x):
    """0.5 * x.Qx + c.x."""
    return 0.5 * sum(xi * yi for xi, yi in zip(x, matvec(q, x))) + \
        sum(float(ci) * float(xi) for ci, xi in zip(c, x))


def solve(a, b):
    """Gaussian elimination with partial pivoting, as in module 3."""
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("expected a square matrix")
    if len(b) != n:
        raise ValueError("b must have one entry per row")
    m = [[float(v) for v in row] + [float(b[i])] for i, row in enumerate(a)]
    for col in range(n):
        best = col
        for r in range(col + 1, n):
            if abs(m[r][col]) > abs(m[best][col]):
                best = r
        if abs(m[best][col]) <= 1e-12:
            raise ValueError("matrix is singular to working precision")
        m[col], m[best] = m[best], m[col]
        for r in range(col + 1, n):
            factor = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= factor * m[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        total = m[i][n]
        for j in range(i + 1, n):
            total -= m[i][j] * x[j]
        x[i] = total / m[i][i]
    return x


def solve_eq_qp(q, c, a, b):
    """(x, nu) from the KKT system of the equality-constrained problem."""
    n = len(q)
    m = len(a)
    if len(c) != n:
        raise ValueError("c must have one entry per variable")
    if len(b) != m:
        raise ValueError("b must have one entry per constraint")
    at = transpose(a) if m else [[] for _ in range(n)]
    big = []
    for i in range(n):
        big.append([float(q[i][j]) for j in range(n)]
                   + [float(at[i][k]) for k in range(m)])
    for k in range(m):
        big.append([float(a[k][j]) for j in range(n)] + [0.0] * m)
    rhs = [-float(ci) for ci in c] + [float(bi) for bi in b]
    sol = solve(big, rhs)
    return (sol[:n], sol[n:])


def kkt_residuals(q, c, g, h, x, lam):
    """(stationarity, primal, dual, complementary), each zero when its condition holds."""
    slack = [row - float(hi) for row, hi in zip(matvec(g, x), h)]
    stationarity = norm([a + float(b) + d for a, b, d in
                         zip(matvec(q, x), c, matvec(transpose(g), lam))])
    primal = norm([max(0.0, s) for s in slack])
    dual = norm([max(0.0, -float(li)) for li in lam])
    complementary = norm([float(li) * s for li, s in zip(lam, slack)])
    return (stationarity, primal, dual, complementary)


def active_set_qp(q, c, g, h, tol=1e-9):
    """(x, lam) by trying every active set and keeping the feasible ones."""
    n = len(q)
    m = len(g)
    if m > 12:
        raise ValueError("enumeration is only sane for a dozen constraints or fewer")
    best = None
    for size in range(min(m, n) + 1):
        for active in combinations(range(m), size):
            try:
                x, nu = solve_eq_qp(q, c, [g[i] for i in active],
                                    [h[i] for i in active])
            except ValueError:
                continue
            lam = [0.0] * m
            for slot, i in enumerate(active):
                lam[i] = nu[slot]
            if any(li < -tol for li in lam):
                continue
            if any(row - float(hi) > tol for row, hi in zip(matvec(g, x), h)):
                continue
            value = quad_value(q, c, x)
            if best is None or value < best[0] - 1e-12:
                best = (value, x, lam)
    if best is None:
        raise ValueError("no feasible KKT point; the problem may be infeasible")
    return (best[1], best[2])


Q = [[2.0, 0.0], [0.0, 2.0]]
C = [-4.0, -2.0]
G = [[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
H = [2.0, 0.0, 0.0]

x, lam = active_set_qp(Q, C, G, H)
print("closest feasible point:", [round(v, 6) for v in x])
print("multipliers:", [round(v, 6) for v in lam])
print("residuals:", [round(r, 12) for r in kkt_residuals(Q, C, G, H, x, lam)])
'''}],
                "hints": [
                    "Build the KKT matrix row by row: the first `n` rows are a row of `Q` followed by a row of `A` transposed, and the last `m` rows are a row of `A` followed by `m` zeros. With no constraints at all the second block is empty and the system is `Qx = -c`.",
                    "`transpose` on an empty list would index row zero of nothing, so `solve_eq_qp` needs the empty active set handled separately — that case is the unconstrained solve, and skipping it loses the answer to any problem whose optimum is interior.",
                    "Inside `active_set_qp`, wrap the call in `try: ... except ValueError: continue`. A repeated or dependent constraint makes the KKT matrix singular, and such an active set is not a candidate at all rather than an error to report.",
                    "Enumerate sizes up to `min(m, n)` rather than up to `m`. More active constraints than variables makes the KKT block singular in every case, so the extra subsets cost time and produce nothing.",
                ],
                "tests": [
                    {"name": "Helpers, and the shapes they refuse", "code": r'''
assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]], \
    f"transpose gave {transpose([[1, 2, 3], [4, 5, 6]])!r}"
assert matvec([[1, 2], [3, 4]], [1, 1]) == [3.0, 7.0], \
    f"matvec gave {matvec([[1, 2], [3, 4]], [1, 1])!r}"
assert abs(norm([3, 4]) - 5.0) < 1e-12, f"norm([3, 4]) gave {norm([3, 4])!r}"
assert norm([]) == 0.0, "the empty vector has length 0.0"
assert abs(quad_value([[2.0, 0.0], [0.0, 2.0]], [-4.0, -2.0], [1.5, 0.5]) + 4.5) < 1e-12, \
    "the objective at (1.5, 0.5) is -4.5 before the dropped constant"
try:
    matvec([[1, 2, 3]], [1, 2])
    assert False, "a row wider than the vector should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "One equality constraint", "code": r'''
_x, _nu = solve_eq_qp([[1.0, 0.0], [0.0, 1.0]], [0.0, 0.0], [[1.0, 1.0]], [2.0])
assert abs(_x[0] - 1.0) < 1e-12 and abs(_x[1] - 1.0) < 1e-12, \
    f"the closest point of x + y = 2 to the origin is (1, 1); got {_x!r}"
assert abs(_nu[0] + 1.0) < 1e-12, f"the multiplier should be -1.0; got {_nu!r}"
_x, _nu = solve_eq_qp([[2.0, 0.0], [0.0, 2.0]], [-4.0, -2.0], [[1.0, 1.0]], [2.0])
assert abs(_x[0] - 1.5) < 1e-12 and abs(_x[1] - 0.5) < 1e-12, \
    f"the projection of (2, 1) onto x + y = 2 is (1.5, 0.5); got {_x!r}"
assert abs(_nu[0] - 1.0) < 1e-12, f"the price of the budget is 1.0; got {_nu!r}"
'''},
                    {"name": "No constraints, and constraints that repeat", "code": r'''
_x, _nu = solve_eq_qp([[2.0, 0.0], [0.0, 2.0]], [-4.0, -2.0], [], [])
assert abs(_x[0] - 2.0) < 1e-12 and abs(_x[1] - 1.0) < 1e-12, \
    f"with no constraints the answer is the unconstrained minimiser (2, 1); got {_x!r}"
assert _nu == [], f"no constraints means no multipliers; got {_nu!r}"
try:
    solve_eq_qp([[2.0, 0.0], [0.0, 2.0]], [-4.0, -2.0], [[1.0, 1.0], [1.0, 1.0]], [2.0, 2.0])
    assert False, "a repeated constraint makes the KKT matrix singular and should raise ValueError"
except ValueError:
    pass
try:
    solve_eq_qp([[2.0, 0.0], [0.0, 2.0]], [-4.0], [[1.0, 1.0]], [2.0])
    assert False, "a c of the wrong length should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The four residuals at a genuine optimum", "code": r'''
_q = [[2.0, 0.0], [0.0, 2.0]]
_c = [-4.0, -2.0]
_g = [[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
_h = [2.0, 0.0, 0.0]
_r = kkt_residuals(_q, _c, _g, _h, [1.5, 0.5], [1.0, 0.0, 0.0])
assert all(abs(v) < 1e-12 for v in _r), f"every residual should vanish at the optimum; got {_r!r}"
assert len(_r) == 4, f"kkt_residuals returns four numbers; got {len(_r)}"
'''},
                    {"name": "The residuals catch each way of being wrong", "code": r'''
_q = [[2.0, 0.0], [0.0, 2.0]]
_c = [-4.0, -2.0]
_g = [[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
_h = [2.0, 0.0, 0.0]
_r = kkt_residuals(_q, _c, _g, _h, [2.0, 1.0], [0.0, 0.0, 0.0])
assert _r[0] < 1e-12, "the unconstrained minimiser is stationary with zero multipliers"
assert abs(_r[1] - 1.0) < 1e-12, f"it violates x + y <= 2 by exactly 1; primal gave {_r[1]!r}"
_r = kkt_residuals(_q, _c, _g, _h, [1.5, 0.5], [-1.0, 0.0, 0.0])
assert _r[2] > 0.5, f"a multiplier of -1 is dual infeasible; dual residual gave {_r[2]!r}"
_r = kkt_residuals(_q, _c, _g, _h, [1.5, 0.5], [1.0, 1.0, 0.0])
assert _r[3] > 0.5, f"charging for a slack constraint breaks complementarity; got {_r[3]!r}"
'''},
                    {"name": "The projection problem, solved by enumeration", "code": r'''
_q = [[2.0, 0.0], [0.0, 2.0]]
_c = [-4.0, -2.0]
_g = [[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
_h = [2.0, 0.0, 0.0]
_x, _lam = active_set_qp(_q, _c, _g, _h)
assert abs(_x[0] - 1.5) < 1e-9 and abs(_x[1] - 0.5) < 1e-9, \
    f"the answer is (1.5, 0.5); got {_x!r}"
assert abs(_lam[0] - 1.0) < 1e-9, f"the budget carries a price of 1.0; got {_lam!r}"
assert _lam[1] == 0.0 and _lam[2] == 0.0, \
    f"the two slack constraints must carry exactly zero; got {_lam!r}"
assert all(abs(v) < 1e-9 for v in kkt_residuals(_q, _c, _g, _h, _x, _lam)), \
    "the returned pair must satisfy all four conditions"
'''},
                    {"name": "An interior optimum, and two constraints at once", "code": r'''
_g = [[1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
_h = [2.0, 0.0, 0.0]
_x, _lam = active_set_qp([[2.0, 0.0], [0.0, 2.0]], [-1.0, -1.0], _g, _h)
assert abs(_x[0] - 0.5) < 1e-9 and abs(_x[1] - 0.5) < 1e-9, \
    f"(0.5, 0.5) is feasible, so no constraint binds; got {_x!r}"
assert _lam == [0.0, 0.0, 0.0], f"every price should be zero; got {_lam!r}"
_x, _lam = active_set_qp([[2.0, 0.0], [0.0, 2.0]], [-4.0, -4.0],
                         [[1.0, 0.0], [0.0, 1.0]], [1.0, 1.0])
assert abs(_x[0] - 1.0) < 1e-9 and abs(_x[1] - 1.0) < 1e-9, \
    f"both bounds bind at (1, 1); got {_x!r}"
assert abs(_lam[0] - 2.0) < 1e-9 and abs(_lam[1] - 2.0) < 1e-9, \
    f"each bound carries a price of 2.0; got {_lam!r}"
'''},
                    {"name": "Singular active sets are stepped over, not crashed on", "code": r'''
_x, _lam = active_set_qp([[2.0, 0.0], [0.0, 2.0]], [-4.0, -2.0],
                         [[1.0, 1.0], [1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]],
                         [2.0, 2.0, 0.0, 0.0])
assert abs(_x[0] - 1.5) < 1e-9 and abs(_x[1] - 0.5) < 1e-9, \
    f"the duplicate constraint changes nothing about the answer; got {_x!r}"
try:
    active_set_qp([[2.0]], [0.0], [[1.0], [-1.0]], [1.0, -2.0])
    assert False, "x <= 1 and x >= 2 cannot both hold; expected ValueError"
except ValueError:
    pass
try:
    active_set_qp([[2.0]], [0.0], [[1.0]] * 13, [1.0] * 13)
    assert False, "more than twelve constraints should be refused rather than enumerated"
except ValueError:
    pass
'''},
                    {"name": "What the script reports", "code": r'''
_lines = _out.strip().split("\n")
assert len(_lines) == 3, f"main.py should print three lines; it printed {len(_lines)}:\n{_out}"
assert _lines[0] == "closest feasible point: [1.5, 0.5]", \
    f"the first line was {_lines[0]!r}, expected 'closest feasible point: [1.5, 0.5]'"
assert _lines[1] == "multipliers: [1.0, 0.0, 0.0]", \
    f"the second line was {_lines[1]!r}, expected 'multipliers: [1.0, 0.0, 0.0]'"
assert _lines[2] == "residuals: [0.0, 0.0, 0.0, 0.0]", \
    f"the third line was {_lines[2]!r}; every residual should print as an exact zero"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Linear programming, duality and discrete search",
            "summary": "Why the answer sits at a corner, what the dual prices are, and what to do when the answer must be a whole number.",
            "concepts": [
                "A linear objective over a polytope is optimised at a vertex, so the search is finite",
                "Slack variables turn inequalities into equalities and a vertex into a choice of basis",
                "The simplex tableau: reduced costs pick the entering column, the ratio test picks the leaving row",
                "Bland's rule terminates on degenerate problems that the steepest-reduced-cost rule can cycle on",
                "The dual: weak duality in two lines, strong duality at the optimum, dual prices in the objective row",
                "The LP relaxation of an integer program is an upper bound on every integer point below it",
                "Branch and bound: split on a fractional variable, prune any node whose bound cannot beat the incumbent",
            ],
            "read": [
                {
                    "title": "The corner you cannot see, and the price you can",
                    "minutes": 14,
                    "body": r'''
A workshop makes tables and chairs. A table takes 4 hours of carpentry and 2 of
finishing, and earns 30 euros. A chair takes 3 hours of carpentry and 1 of finishing,
and earns 20. This week there are 240 carpentry hours and 100 finishing hours, and
nothing else is scarce. How many of each?

$$\max\ 30t + 20c \quad \text{subject to} \quad 4t + 3c \le 240,\quad 2t + c \le 100,
\quad t \ge 0,\ c \ge 0$$

Draw the feasible region and it is a quadrilateral: the two axes and the two constraint
lines cut a polygon out of the first quadrant. Now draw the objective. The set of plans
earning exactly 1200 euros is a straight line, and so is the set earning 1500, and they
are parallel — the objective is linear, so its level sets are parallel lines that sweep
across the plane as the profit rises. Push the line as far as it will go while still
touching the polygon and it stops at a corner, because a straight line leaving a convex
polygon leaves through a vertex unless it happens to be parallel to an edge, in which
case it leaves through that whole edge — and the ends of that edge are vertices too.

So the optimum is at a vertex, and there are finitely many vertices. That single
observation converts an optimisation over a continuum into a search over a list.

```python
from itertools import combinations

lines = [(4.0, 3.0, 240.0), (2.0, 1.0, 100.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

def meet(p, q):
    det = p[0] * q[1] - p[1] * q[0]
    if abs(det) < 1e-12:
        return None
    return ((p[2] * q[1] - p[1] * q[2]) / det, (p[0] * q[2] - p[2] * q[0]) / det)

for p, q in combinations(lines, 2):
    point = meet(p, q)
    if point is None:
        continue
    t, c = point
    t, c = t + 0.0, c + 0.0            # a signed zero prints as -0.00 otherwise
    if t < -1e-9 or c < -1e-9:
        continue
    if 4 * t + 3 * c > 240 + 1e-9 or 2 * t + c > 100 + 1e-9:
        continue
    print(f"vertex ({t:6.2f}, {c:6.2f})   profit {30 * t + 20 * c:8.2f}")
```

Four feasible vertices, and the best of them is $t = 30$, $c = 40$, earning $1700$. Both
resources are exhausted there: $4(30) + 3(40) = 240$ and $2(30) + 40 = 100$.

Enumerating vertices is only sane in two dimensions. With $n$ variables and $m$
constraints a vertex is a choice of which $n$ of the $n+m$ inequalities hold with
equality, and the count grows like a binomial coefficient. The simplex method is the
repair: start at a vertex, look along each edge leaving it, and move to a neighbour that
improves the objective, stopping when no edge improves. Because the region is convex,
no local improvement being available means no improvement exists anywhere — module 1's
argument, applied to a polytope.

## What the tableau is doing

Introduce a slack variable per constraint, so $4t + 3c + s_1 = 240$ with $s_1 \ge 0$.
Now every constraint is an equation in $n + m$ non-negative variables, and a vertex is a
choice of $m$ of them to be *basic* — solved for — while the other $n$ are held at zero.
Sitting at the origin, the two slacks are basic and hold the unused hours.

The tableau carries those equations plus one more row for the objective. Each entry of
the objective row is a *reduced cost*: the net change in profit from raising that
variable by one, after the basic variables adjust to keep the equations true. A
negative entry (in the sign convention where the objective row starts as $-c$) names a
variable worth increasing. Raise it, and the basic variables move; the ratio test asks
which of them reaches zero first, and that one leaves the basis. One pivot later you are
at an adjacent vertex.

Two entering columns can look equally attractive, and on a degenerate problem — one
where a basic variable is already zero — a natural "most negative reduced cost" rule can
cycle forever between bases at the same vertex. Bland's rule fixes it: among the
candidates, always take the one with the lowest index, and break ties in the ratio test
the same way. It is provably finite, and it is what the lab uses.

## The dual, from a story

Someone offers to buy the workshop's whole capacity for the week rather than have it
make furniture. They will pay $y_1$ per carpentry hour and $y_2$ per finishing hour. What
prices would you accept?

You would refuse any offer that makes you worse off than building a table. A table
consumes 4 carpentry hours and 2 finishing hours, so selling that bundle must bring at
least the 30 euros the table would have earned: $4y_1 + 2y_2 \ge 30$. The same for a
chair: $3y_1 + y_2 \ge 20$. The buyer, wanting the capacity for as little as possible,
minimises the total bill $240y_1 + 100y_2$ subject to those two conditions and
$y \ge 0$.

That is the dual problem, and it was not posted as a definition; it is the same data
read from the other side of the table. The relationship between the two is two lines of
algebra. Take any feasible plan $x$ and any feasible price vector $y$. Then

$$c \cdot x \le (A^{\mathsf{T}}y) \cdot x = y \cdot (Ax) \le y \cdot b$$

The first step uses $A^{\mathsf{T}}y \ge c$ together with $x \ge 0$; the middle is the
associativity of a triple product; the last uses $Ax \le b$ together with $y \ge 0$.
Every feasible offer is at least as large as every feasible profit — weak duality — so
any dual-feasible $y$ you can produce is a certificate that no plan does better than
$y \cdot b$.

Strong duality is the statement that the two optima meet, and here they do:

```python
y1, y2 = 5.0, 5.0
print("acceptable for tables:", 4 * y1 + 2 * y2 >= 30)
print("acceptable for chairs:", 3 * y1 + y2 >= 20)
print("total bill  :", 240 * y1 + 100 * y2)
print("best profit :", 30 * 30 + 20 * 40)
```

Both dual constraints are tight, which is complementary slackness from module 4 wearing
different clothes: a product made in positive quantity has its dual constraint binding,
and a resource with slack left over has price zero. And $y_1 = 5$ is the multiplier of
module 4 — the derivative of the optimal value with respect to the right-hand side:

```python
def best_plan(carpentry_hours):
    """Both constraints tight: 4t + 3c = hours and 2t + c = 100."""
    tables = (300.0 - carpentry_hours) / 2.0
    chairs = carpentry_hours - 200.0
    return (tables, chairs, 30.0 * tables + 20.0 * chairs)

for hours in (240.0, 241.0):
    print(f"{hours:.0f} h: tables {best_plan(hours)[0]}, chairs {best_plan(hours)[1]}, "
          f"profit {best_plan(hours)[2]}")
print("the 241st carpentry hour is worth:",
      best_plan(241.0)[2] - best_plan(240.0)[2])
```

Five euros, exactly the dual price, and the number to compare against the cost of
overtime. A simplex tableau hands you these for free: when it stops, the objective-row
entries under the slack columns are the dual prices.

## When the answer has to be a whole number

The workshop cannot make 29.5 tables. Add integrality and the geometry changes
completely: the feasible set is no longer a polygon but a scatter of lattice points
inside one, and none of the vertex reasoning survives.

What does survive is a bound. Every integer feasible point is also a feasible point of
the *relaxation* — the same problem with the integrality dropped — so the relaxation's
optimum is at least as large as the best integer value. One line, and it is the entire
engine of the method.

With 241 carpentry hours the relaxation gives $t = 29.5$, $c = 41$ and $1705$. Branch on
the fractional variable: every integer plan has either $t \le 29$ or $t \ge 30$, and the
two cases together lose nothing. Solving the two children, $t \ge 30$ gives exactly
$(30, 40)$ with profit $1700$ — integral, so it becomes the incumbent — and $t \le 29$
gives $1703.33$, which is above $1700$, so that branch cannot be discarded and has to be
split again. Following it down produces $(28, 43)$, also worth $1700$. Nothing beats
$1700$, and the search stops with a proof rather than a hope.

Pruning is where the work is saved: a node whose relaxation is worth $1699$ can be
abandoned without exploring a single one of its descendants, because none of them can
exceed their own parent's bound.

## The mistake

Rounding the relaxation. It is the first thing anyone tries, it is often nearly right,
and "nearly right" is exactly the trap.

```python
for plan in [(30, 41), (29, 41), (30, 40), (28, 43)]:
    tables, chairs = plan
    carpentry = 4 * tables + 3 * chairs
    finishing = 2 * tables + chairs
    ok = carpentry <= 241 and finishing <= 100
    print(f"{plan}: carpentry {carpentry:3d}  finishing {finishing:3d}  "
          f"profit {30 * tables + 20 * chairs}  "
          f"{'feasible' if ok else 'INFEASIBLE'}")
```

Rounding $(29.5, 41)$ to the nearest integers gives $(30, 41)$, which overruns both
resources — it is not a plan at all, it is a wish. Rounding down gives $(29, 41)$, which
is feasible and earns $1690$: ten euros short of the true integer optimum, from a
starting point that was only half a table away. In higher dimensions the gap is not ten
euros; rounding a relaxation with a hundred fractional variables can miss the optimum by
any margin you like, and can be infeasible in a hundred ways at once.

The second misreading is treating a dual price of zero as "this resource is worthless".
It says there is slack in that resource *now*. Buy enough of everything else and it will
start to bind, and its price will stop being zero.

## Where it stops holding

A dual price is a derivative, so it describes a rate and not a policy. Add carpentry
hours one at a time and each is worth 5 euros until the finishing hours run out; past
that point the basis changes and so does the price. Every sensitivity number a solver
prints comes with a range of validity, and quoting the number without the range is the
most common way to misuse a solver's output.

Degeneracy costs more than pivots. When more constraints pass through a vertex than the
dimension requires, several bases describe the same point, the dual prices differ
between them, and the sensitivity becomes one-sided: relaxing a constraint may be worth
one number and tightening it another.

The lab's simplex assumes $b \ge 0$, so that the origin is feasible and can be used as a
starting vertex. Removing that assumption needs a phase-one problem that finds a vertex
before the real work starts. Its branch and bound assumes $A \ge 0$ as well, which is
what lets a lower bound on a variable be imposed by shifting the variable instead of
adding a constraint with a negative right-hand side.

And both methods are exponential in the worst case. Klee and Minty built linear programs
on which simplex visits every one of $2^n$ vertices, and branch and bound explores a tree
that can be as large as the lattice. What makes them usable is that the bounds are good
in practice, which is an empirical claim about the problems people actually have and not
a theorem.

## The lab

**A simplex tableau and a branch-and-bound tree** asks for four routines: `simplex_max`,
returning the plan, the value and the dual prices; `is_dual_feasible` and `duality_gap`,
which together let you check an answer against its own certificate rather than trusting
it; and `branch_and_bound`. The tests include the workshop at both 240 and 241 hours, a
three-variable program, a degenerate one with two identical constraints, and a knapsack
whose relaxation is worth 22 while no integer packing beats 21.
''',
                },
            ],
            "quiz": {
                "title": "Corners, prices and whole numbers",
                "minutes": 10,
                "questions": [
                    {
                        "q": "Why is a linear objective over a bounded polytope always optimised at a vertex?",
                        "opts": [
                            "Because the level sets are parallel hyperplanes, and the last one touching the region meets it at a face, which holds a corner",
                            "Because the gradient of a linear function is constant, so it points at the same vertex from every feasible point in the region",
                            "Because the interior of a polytope contains no stationary points at all, and an optimum has to be a stationary point of the objective",
                            "Because a polytope is convex, and every convex set attains the maximum of any function on its boundary",
                        ],
                        "a": 0,
                        "whys": [
                            r"Sweeping a family of parallel level sets across the region, the last contact is a face, and a face of a bounded polytope contains a vertex.",
                            r"The gradient is constant and does point in one fixed direction, which is why the sweep works — but a direction does not name a point, and which vertex is furthest along it depends on the region rather than on the gradient alone.",
                            r"A non-zero linear function has no stationary points anywhere, interior or not, and an optimum over a constrained set need not be stationary. That is the whole reason module 4 introduced multipliers.",
                            r"Convexity alone gives nothing of the kind: $-|x|^2$ on a disc is maximised at the centre. What is special here is the linearity of the objective, not the convexity of the set.",
                        ],
                        "why": r'''
The level sets of $c \cdot x$ are parallel hyperplanes, one per objective value, and
raising the value slides them in the direction $c$. The optimum is the last one that
still meets the region. That contact is a face of the polytope — possibly a single
vertex, possibly a whole edge or facet if $c$ is perpendicular to it — and every
non-empty face of a bounded polytope contains at least one vertex. So there is always a
vertex among the optimal points, which turns a search over a continuum into a search
over a finite list. Simplex is the method that walks that list along edges instead of
enumerating it.
''',
                    },
                    {
                        "q": "You have a feasible plan worth $1700$ and a set of dual prices, feasible for the dual, whose total bill is $1700$. What has been established?",
                        "opts": [
                            "That both are optimal, since weak duality puts every feasible profit at or below every feasible bill",
                            "That the plan is optimal, while the prices might still be improved on by a cheaper feasible set",
                            "That the problem is degenerate, because primal and dual values coincide only when a vertex is over-determined",
                            "Nothing yet — strong duality is needed, and it holds only after the simplex method has confirmed it",
                        ],
                        "a": 0,
                        "whys": [
                            r"Weak duality sandwiches every profit below every bill, so a matching pair pins both against the sandwich.",
                            r"The argument is symmetric. Any cheaper feasible bill would sit below a feasible profit of 1700, which weak duality forbids — so the prices are pinned exactly as tightly as the plan is.",
                            r"Equal values are the ordinary situation at an optimum, not a symptom of degeneracy. Degeneracy is about several bases describing one vertex, and it can occur whether or not you have a matching pair in hand.",
                            r"Strong duality guarantees that such a pair *exists*; it is not needed to interpret one you are holding. The matching pair is self-certifying, which is exactly what makes it useful.",
                        ],
                        "why": r'''
Weak duality is the chain $c \cdot x \le (A^{\mathsf{T}}y) \cdot x = y \cdot (Ax) \le y
\cdot b$, valid for every feasible pair. So every feasible profit lies at or below every
feasible bill. A plan worth $1700$ and prices billing $1700$ therefore squeeze the
optimum from both sides: no plan can exceed $1700$ because this $y$ forbids it, and no
prices can fall below $1700$ because this $x$ forbids it. That is a proof you can hand
to somebody who does not trust your solver, which is what a certificate means and why
`duality_gap` is worth writing.
''',
                    },
                    {
                        "q": "The relaxation of an integer program gives $t = 29.5$, $c = 41$, worth $1705$. Why is rounding to $(30, 41)$ not merely inaccurate but wrong in kind?",
                        "opts": [
                            "Because it lands outside the feasible region entirely, overrunning both resources rather than earning slightly less",
                            "Because rounding half-values up rather than down introduces a bias, which accumulates across the variables",
                            "Because the integer optimum can never be adjacent to the relaxed one, so any rounding is a step in a wrong direction",
                            "Because $1705$ is not attainable by integers, so the rounded plan cannot achieve the value the relaxation promised",
                            ],
                        "a": 0,
                        "whys": [
                            r"$(30, 41)$ needs 243 carpentry hours and 101 finishing hours, and only 241 and 100 exist.",
                            r"Rounding direction is a real question and rounding down does give a feasible plan here — worth $1690$, ten short. But a bias that costs value is a different failure from producing something that cannot be built at all.",
                            r"Adjacency is not forbidden: in this very problem the integer optimum $(30, 40)$ is one unit from the relaxed answer. It is not *reliably* adjacent, which is a much weaker and much more inconvenient statement.",
                            r"The unattainability of $1705$ is true and is the reason a gap exists, but it explains a shortfall rather than an infeasibility. A plan that missed $1705$ and earned $1690$ would still be a plan.",
                        ],
                        "why": r'''
$(30, 41)$ needs $4(30) + 3(41) = 243$ carpentry hours and $2(30) + 41 = 101$ finishing
hours, against 241 and 100 available. It is not a worse plan; it is not a plan. Rounding
down to $(29, 41)$ is feasible and earns $1690$, ten euros below the true integer
optimum of $1700$ — from a relaxation that was half a table away from integrality. With
two variables the damage is bounded by inspection. With a hundred fractional variables a
rounded point can violate a hundred constraints at once and can miss the optimum by any
margin at all, which is why the relaxation is used as a *bound* inside a search rather
than as an answer to be tidied up.
''',
                    },
                    {
                        "q": "In branch and bound, a node's relaxation is worth $1699$ and the best integer plan found so far is worth $1700$. What may be done with that node?",
                        "opts": [
                            "Discard it and its whole subtree, since no descendant can be worth more than the node's own bound",
                            "Discard the node but explore its children, because a child's relaxation can exceed its parent's",
                            "Keep it, since a node with a fractional relaxation may still contain a better integer point below it",
                            "Keep it, but explore it last, because a bound within one unit of the incumbent is too close to call",
                        ],
                        "a": 0,
                        "whys": [
                            r"A child's feasible set is a subset of its parent's, so its relaxation can only be worth the same or less.",
                            r"A child is the parent with one more constraint, so its feasible set is smaller and its optimum can never rise. If a child could beat its parent's bound the whole method would collapse.",
                            r"It may indeed contain integer points, and every one of them is worth at most $1699$ — the bound applies to every feasible point of the node, integral or not, which is the property that makes pruning sound.",
                            r"Ordering nodes is a real design choice and affects how quickly a good incumbent appears. It is not what is at issue here: this node is provably worthless and postponing it wastes the memory it sits in.",
                        ],
                        "why": r'''
Every feasible point of a node, integer or not, is feasible for that node's relaxation,
so its value is at most the relaxation's optimum — $1699$ here. Branching adds
constraints, so a child's feasible set is contained in its parent's and its bound can
only fall. The whole subtree is therefore capped at $1699$, and an integer plan worth
$1700$ is already in hand, so nothing down there can be used. That single deduction is
what separates branch and bound from enumerating the lattice: without pruning, the tree
is the lattice. The quality of the bound is what decides how much gets pruned, which is
why a tighter relaxation is worth real effort.
''',
                    },
                    {
                        "q": "A workshop's dual price for carpentry hours is $5$ euros. Its manager buys 200 extra hours at 4 euros each, expecting 1000 euros of extra profit. What is wrong with the reasoning?",
                        "opts": [
                            "The price is a derivative, valid until some other resource becomes binding, after which the basis and the price both change",
                            "The price applies to the constraint as a whole, so it has to be divided by the 240 hours already available",
                            "Dual prices are only meaningful for constraints that are slack, and this one is binding at the optimum",
                            "The price is measured in the dual problem's own units, so it has to be converted before it is compared with a cost in euros",
                        ],
                        "a": 0,
                        "whys": [
                            r"The finishing hours run out long before 200 extra carpentry hours have been used, and past that the marginal hour is worth nothing.",
                            r"The price is already per hour: relaxing the right-hand side by one raised the optimum by exactly 5. Dividing by 240 would make the whole capacity worth 5 euros, which contradicts the dual bill of 1700.",
                            r"It is the other way round. A slack constraint has price zero precisely because more of it changes nothing; a price is informative exactly when the constraint binds, as this one does.",
                            r"The dual variables of this problem are in euros per hour by construction — the dual constraints compare $4y_1 + 2y_2$ against a profit of 30 euros, so $y$ carries euros per hour and nothing needs converting.",
                        ],
                        "why": r'''
A multiplier is a derivative of the optimal value, so it describes the next hour, not the
next two hundred. Here the 241st carpentry hour genuinely is worth 5 euros, and the
optimal plan shifts from $(30, 40)$ towards more chairs to use it — but chairs consume
finishing hours, and there are only 100. Once finishing binds alone, further carpentry
hours are free capacity nobody can use and their price drops to zero. Every sensitivity
figure a solver prints comes with a range of right-hand sides over which it holds, and
using the number outside that range is the most common way to misread a solver's output.
The safe move is to re-solve with the proposed 440 hours and compare the two optima
directly.
''',
                    },
                    {
                        "q": "Why does the lab's simplex pick the lowest-indexed negative reduced cost rather than the most negative one?",
                        "opts": [
                            "Because Bland's rule provably terminates, while the most-negative rule can cycle between bases at a degenerate vertex",
                            "Because the most negative reduced cost is expensive to find, needing a scan of the whole objective row",
                            "Because the lowest index reaches the optimum in fewer pivots on the problems in the tests",
                            "Because the most-negative rule can pick a column with no positive entry, which would report a bounded problem as unbounded",
                        ],
                        "a": 0,
                        "whys": [
                            r"Termination is the guarantee being bought, and the price is usually a longer path to the same vertex.",
                            r"Both rules scan the objective row — the lowest-index rule can stop at the first negative entry, so it is marginally cheaper, but a scan of $n + m$ numbers is nothing beside the pivot that follows it.",
                            r"The opposite is the usual case: the most-negative rule normally takes fewer pivots, which is why it is the default in practice. Bland's rule is the safety net a solver falls back to when it detects stalling.",
                            r"A column with no positive entry means the objective really is unbounded along that edge, whichever rule chose the column. The report would be correct, not a false alarm.",
                        ],
                        "why": r'''
At a degenerate vertex a basic variable is already zero, so the ratio test can return a
step of length zero: the basis changes but the point does not. A sequence of such pivots
can return to a basis it has already visited, and then repeat forever — a genuine
infinite loop, first exhibited by Beale on a problem with three variables. Bland's rule,
taking the lowest index among the candidates for both entering and leaving, is provably
free of it. The cost is that it often takes more pivots than the steepest rule, so
production solvers use a fast rule and switch to Bland's when they detect stalling. A
teaching implementation that has to be correct on every input it is handed takes Bland's
rule from the start.
''',
                    },
                ],
            },
            "blanks": {
                "title": "One simplex pivot, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "the entering column, the ratio test and the elimination — five holes",
                "brief": r'''
One pivot of the tableau. The first `n` columns are the decision variables, the next `m`
are the slacks, the last is the right-hand side; row `m` is the objective, holding
$-c$ at the start.

Nothing runs here. Filled in correctly, the workshop problem reaches its optimum at
$(30, 40)$ in a handful of pivots and leaves the dual prices $5$ and $5$ in the
objective row under the slack columns.
''',
                "listing": r'''
def simplex_step(table, basis, n, m, tol=1e-9):
    """One pivot, or None when the objective row has no negative entry left."""
    entering = -1
    for j in range(n + m):                       # Bland: the lowest index wins
        if table[m][j] < ___:
            entering = j
            break
    if entering < 0:
        return None

    leaving = -1
    best = None
    for i in range(m):
        if table[i][entering] > tol:
            ratio = ___
            if best is None or ratio < best - 1e-12:
                best = ratio
                leaving = i
    if leaving < 0:
        raise ValueError("the objective is unbounded above on this feasible set")

    pivot = table[leaving][entering]
    table[leaving] = [v / ___ for v in table[leaving]]
    for i in range(m + 1):
        if i != leaving:
            factor = table[i][entering]
            table[i] = [v - ___ for v, w in zip(table[i], table[leaving])]
    basis[leaving] = ___
    return entering
''',
                "blanks": [
                    {
                        "prompt": "The threshold a reduced cost must fall below to count as an improving column.",
                        "hole": "?",
                        "opts": ["-tol", "0.0", "tol", "-1.0"],
                        "a": 0,
                        "why": "A reduced cost that is zero to within rounding buys nothing, and treating it as an improvement is how a degenerate problem stalls: the pivot happens, the objective does not move, and the same column can be chosen again.",
                        "whys": [
                            "A reduced cost that is zero to within rounding buys nothing, and treating it as an improvement is how a degenerate problem stalls: the pivot happens, the objective does not move, and the same column can be chosen again.",
                            "An exact comparison lets a reduced cost of -1e-17, which is rounding noise around zero, start another pivot. On a degenerate problem that is the difference between stopping and looping until max_pivots runs out.",
                            "A positive threshold accepts columns whose reduced cost is positive, which are the ones that make the objective worse. The method then walks downhill and stops at whatever vertex it happens to reach.",
                            "This waits for a reduced cost below -1.0 before pivoting, so a problem whose remaining improvements are all worth less than one unit is declared optimal while money is still on the table.",
                        ],
                    },
                    {
                        "prompt": "The ratio the test compares across rows.",
                        "hole": "?",
                        "opts": ["table[i][-1] / table[i][entering]",
                                 "table[i][entering] / table[i][-1]",
                                 "table[i][-1]",
                                 "table[i][-1] / table[m][entering]"],
                        "a": 0,
                        "why": "Raising the entering variable by one unit reduces basic variable i by table[i][entering], and it starts at table[i][-1]. The quotient is how far the entering variable can rise before that row hits zero, and the smallest such distance is the binding one.",
                        "whys": [
                            "Raising the entering variable by one unit reduces basic variable i by table[i][entering], and it starts at table[i][-1]. The quotient is how far the entering variable can rise before that row hits zero, and the smallest such distance is the binding one.",
                            "The reciprocal is minimised where the true ratio is maximised, so this picks the row that binds last rather than first. The pivot then drives another basic variable negative, and the tableau no longer describes a feasible point.",
                            "Comparing right-hand sides ignores how fast each row is being consumed. A row with 240 hours left that is used four at a time binds sooner than one with 100 left that is used one at a time, and this ranking gets that backwards.",
                            "Dividing by the objective row's entry uses the same number for every row, so the ranking is the ranking of the right-hand sides, with the additional hazard that the objective entry is negative and flips every comparison.",
                        ],
                    },
                    {
                        "prompt": "What the pivot row is divided through by.",
                        "hole": "?",
                        "opts": ["pivot", "table[leaving][-1]", "table[i][entering]", "1.0"],
                        "a": 0,
                        "why": "Dividing the row by its own pivot entry puts a 1 in the pivot position, which is what makes the entering variable basic and lets the elimination below clear the rest of the column.",
                        "whys": [
                            "Dividing the row by its own pivot entry puts a 1 in the pivot position, which is what makes the entering variable basic and lets the elimination below clear the rest of the column.",
                            "Dividing by the right-hand side normalises the wrong entry: the pivot position ends up holding a ratio rather than 1, so the elimination underneath leaves residue in the entering column and the basis is not what the bookkeeping says it is.",
                            "The loop variable i does not exist yet at this line, and even where it does it names some other row's entry in the entering column, which has no reason to be the pivot.",
                            "Dividing by one leaves the row exactly as it was, so the pivot position still holds the pivot value instead of a 1. The elimination underneath then subtracts the wrong multiple, the entering column is never cleared, and two variables end up claiming to be basic in the same row.",
                        ],
                    },
                    {
                        "prompt": "The multiple of the pivot row subtracted from every other row.",
                        "hole": "?",
                        "opts": ["factor * w", "w", "factor", "factor * v"],
                        "a": 0,
                        "why": "The aim is to leave a zero in the entering column of row i, and after the normalisation that column holds a 1 in the pivot row, so subtracting factor times the whole pivot row does it and keeps the equations equivalent.",
                        "whys": [
                            "The aim is to leave a zero in the entering column of row i, and after the normalisation that column holds a 1 in the pivot row, so subtracting factor times the whole pivot row does it and keeps the equations equivalent.",
                            "Subtracting one copy of the pivot row clears the entering column only when factor happens to be 1. For any other coefficient it leaves residue there, so the basic variables no longer read off the tableau.",
                            "Subtracting the same constant from every entry of the row is not a row operation at all: it changes the equation the row represents rather than adding a multiple of another equation to it.",
                            "This subtracts a multiple of the row from itself, which scales row i by 1 - factor and never touches the pivot row. The entering column is left exactly as it was, apart from the scaling.",
                        ],
                    },
                    {
                        "prompt": "The variable that is now basic in the pivot row.",
                        "hole": "?",
                        "opts": ["entering", "leaving", "n + leaving", "pivot"],
                        "a": 0,
                        "why": "The point of the pivot is that the entering variable takes over the row that the leaving variable held, so the basis entry for that row becomes the entering column's index.",
                        "whys": [
                            "The point of the pivot is that the entering variable takes over the row that the leaving variable held, so the basis entry for that row becomes the entering column's index.",
                            "That is the row number, not a column. The basis list holds one variable index per row, so writing a row number into it makes the solution read-off pick up whatever variable happens to share that index.",
                            "This is the slack variable of that row, which is the value the entry held before the very first pivot. Restoring it after every pivot means the basis list never changes and the reported solution stays at the origin however many pivots run.",
                            "The pivot is a coefficient, a float, and the basis holds integer column indices. Depending on the tableau it either indexes nonsense or raises a TypeError when the solution is read off.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "A simplex tableau and a branch-and-bound tree",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Four routines in `main.py`, on plain lists of floats. Only `math` is imported.

## The linear program

Throughout, the problem is

$$\max\ c \cdot x \quad \text{subject to} \quad Ax \le b,\quad x \ge 0$$

with every entry of `b` non-negative, so the origin is a feasible starting vertex and no
phase-one problem is needed.

- `simplex_max(c, a, b, tol=1e-9, max_pivots=5000)` — returns `(x, value, duals)`.
  Build the tableau with `m` slack columns and an objective row that starts at `-c`.
  Pivot by **Bland's rule**: entering column is the lowest index whose objective entry
  is below `-tol`; the ratio test takes the smallest `table[i][-1] / table[i][entering]`
  over rows with a positive entry there. When no entering column exists, read `x` off
  the basis, the value off the objective row's right-hand entry, and the duals off the
  objective row under the slack columns. An entering column with no positive entry means
  the objective is unbounded: raise `ValueError`. A negative entry of `b`, a ragged `a`,
  or a mismatched `b` also raises `ValueError`.

## Its certificate

- `is_dual_feasible(c, a, y, tol=1e-9)` — `True` when every `y_i >= -tol` and every
  column satisfies `sum_i a[i][j] * y[i] >= c[j] - tol`.
- `duality_gap(c, a, b, x, y)` — `dot(b, y) - dot(c, x)`. Zero at a matched optimal
  pair, and non-negative for any feasible pair by weak duality.

## Whole numbers

- `branch_and_bound(c, a, b, tol=1e-6, max_nodes=20000)` — returns
  `(x, value)` with every `x_j` an `int`. Depth-first over nodes; each node solves its
  relaxation with `simplex_max`, prunes when the bound cannot beat the incumbent,
  and otherwise branches on the first fractional variable.

  Both `a` and `b` must be non-negative, which raises `ValueError` otherwise, and it is
  what makes the branching work without a phase-one solve: an upper bound `x_j <= k` is
  a new row, and a lower bound `x_j >= k` is imposed by *substituting* `x_j = k + x'`,
  which subtracts `k` times column `j` from `b`. If that leaves any entry of `b`
  negative, the branch is infeasible and is dropped. Raise `ValueError` when no integer
  point is feasible.

```text
simplex_max([30, 20], [[4, 3], [2, 1]], [240, 100])
    ->  ([30.0, 40.0], 1700.0, [5.0, 5.0])
branch_and_bound([30, 20], [[4, 3], [2, 1]], [241, 100])   ->  value 1700.0
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def dot(u, v):
    return sum(float(a) * float(b) for a, b in zip(u, v))


def simplex_max(c, a, b, tol=1e-9, max_pivots=5000):
    """(x, value, duals) for max c.x subject to a x <= b, x >= 0, b >= 0."""
    # your code here


def is_dual_feasible(c, a, y, tol=1e-9):
    """True when y >= 0 and every column of a prices its variable at or above c."""
    # your code here


def duality_gap(c, a, b, x, y):
    """dot(b, y) - dot(c, x): zero at a matched optimal pair."""
    # your code here


def branch_and_bound(c, a, b, tol=1e-6, max_nodes=20000):
    """(x, value) with integer x, by depth-first search over LP relaxations."""
    # your code here


C = [30.0, 20.0]
A = [[4.0, 3.0], [2.0, 1.0]]
B = [240.0, 100.0]

x, value, duals = simplex_max(C, A, B)
print("plan:", [round(v, 6) for v in x], "profit:", round(value, 6))
print("prices:", [round(v, 6) for v in duals],
      "gap:", round(duality_gap(C, A, B, x, duals), 9))
xi, vi = branch_and_bound(C, A, [241.0, 100.0])
print("integer profit with 241 carpentry hours:", round(vi, 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def dot(u, v):
    return sum(float(a) * float(b) for a, b in zip(u, v))


def simplex_max(c, a, b, tol=1e-9, max_pivots=5000):
    """(x, value, duals) for max c.x subject to a x <= b, x >= 0, b >= 0."""
    m = len(a)
    if m == 0:
        raise ValueError("need at least one constraint")
    n = len(c)
    if any(len(row) != n for row in a):
        raise ValueError("each row of a needs one entry per variable")
    if len(b) != m:
        raise ValueError("b needs one entry per constraint")
    if any(float(bi) < -tol for bi in b):
        raise ValueError("every entry of b must be non-negative")

    table = []
    for i in range(m):
        row = [float(v) for v in a[i]] + [0.0] * m + [float(b[i])]
        row[n + i] = 1.0
        table.append(row)
    table.append([-float(v) for v in c] + [0.0] * (m + 1))
    basis = [n + i for i in range(m)]

    for _ in range(max_pivots):
        entering = -1
        for j in range(n + m):
            if table[m][j] < -tol:
                entering = j
                break
        if entering < 0:
            x = [0.0] * n
            for i in range(m):
                if basis[i] < n:
                    x[basis[i]] = table[i][-1]
            return (x, table[m][-1], [table[m][n + i] for i in range(m)])
        leaving = -1
        best = None
        for i in range(m):
            if table[i][entering] > tol:
                ratio = table[i][-1] / table[i][entering]
                if best is None or ratio < best - 1e-12 or \
                        (abs(ratio - best) <= 1e-12 and basis[i] < basis[leaving]):
                    best = ratio
                    leaving = i
        if leaving < 0:
            raise ValueError("the objective is unbounded above on this feasible set")
        pivot = table[leaving][entering]
        table[leaving] = [v / pivot for v in table[leaving]]
        for i in range(m + 1):
            if i != leaving:
                factor = table[i][entering]
                table[i] = [v - factor * w for v, w in zip(table[i], table[leaving])]
        basis[leaving] = entering
    raise ValueError("the simplex method did not terminate within max_pivots")


def is_dual_feasible(c, a, y, tol=1e-9):
    """True when y >= 0 and every column of a prices its variable at or above c."""
    if len(y) != len(a):
        raise ValueError("y needs one price per constraint")
    if any(float(yi) < -tol for yi in y):
        return False
    for j in range(len(c)):
        if sum(float(a[i][j]) * float(y[i]) for i in range(len(a))) < float(c[j]) - tol:
            return False
    return True


def duality_gap(c, a, b, x, y):
    """dot(b, y) - dot(c, x): zero at a matched optimal pair."""
    if len(b) != len(y) or len(c) != len(x):
        raise ValueError("the pair must match the problem")
    return dot(b, y) - dot(c, x)


def branch_and_bound(c, a, b, tol=1e-6, max_nodes=20000):
    """(x, value) with integer x, by depth-first search over LP relaxations."""
    n = len(c)
    if any(float(v) < 0.0 for row in a for v in row):
        raise ValueError("the shifting branch rule needs a non-negative a")
    if any(float(v) < 0.0 for v in b):
        raise ValueError("every entry of b must be non-negative")
    best_value = -math.inf
    best_x = None
    stack = [([[float(v) for v in row] for row in a], [float(v) for v in b],
              [0.0] * n, 0.0)]
    nodes = 0
    while stack:
        nodes += 1
        if nodes > max_nodes:
            raise ValueError("branch and bound ran out of nodes")
        rows, rhs, shift, offset = stack.pop()
        try:
            x, value, _ = simplex_max(c, rows, rhs)
        except ValueError as exc:
            if "unbounded" in str(exc):
                raise
            continue
        total = value + offset
        if total <= best_value + tol:
            continue
        fractional = -1
        for j in range(n):
            if abs(x[j] - round(x[j])) > tol:
                fractional = j
                break
        if fractional < 0:
            best_value = total
            best_x = [int(round(x[j] + shift[j])) for j in range(n)]
            continue
        floor_value = math.floor(x[fractional] + shift[fractional])
        step = floor_value + 1 - shift[fractional]
        if step >= 0:
            moved = [rhs[i] - step * rows[i][fractional] for i in range(len(rows))]
            if all(v >= -1e-9 for v in moved):
                lifted = list(shift)
                lifted[fractional] = float(floor_value + 1)
                stack.append(([row[:] for row in rows], moved, lifted,
                              offset + step * float(c[fractional])))
        cap = floor_value - shift[fractional]
        if cap >= 0:
            extra = [0.0] * n
            extra[fractional] = 1.0
            stack.append(([row[:] for row in rows] + [extra],
                          list(rhs) + [float(cap)], list(shift), offset))
    if best_x is None:
        raise ValueError("no integer point is feasible")
    return (best_x, best_value)


C = [30.0, 20.0]
A = [[4.0, 3.0], [2.0, 1.0]]
B = [240.0, 100.0]

x, value, duals = simplex_max(C, A, B)
print("plan:", [round(v, 6) for v in x], "profit:", round(value, 6))
print("prices:", [round(v, 6) for v in duals],
      "gap:", round(duality_gap(C, A, B, x, duals), 9))
xi, vi = branch_and_bound(C, A, [241.0, 100.0])
print("integer profit with 241 carpentry hours:", round(vi, 6))
'''}],
                "hints": [
                    "Build the tableau as `m + 1` rows of `n + m + 1` numbers: the constraint rows are `a[i]` then a one-hot slack then `b[i]`, and the objective row is `-c` followed by zeros. Keeping the right-hand side in the last column means the ratio test reads `table[i][-1]`.",
                    "After the pivot row has been divided by the pivot, the entering column holds a 1 there, so clearing every other row is `row - row[entering] * pivot_row`. Read `factor` before you start rewriting the row, or it changes underneath you.",
                    "The duals are the objective-row entries under the slack columns when the method stops. Nothing extra has to be computed: the same eliminations that solved the primal accumulated them.",
                    "For the lower-bound branch, subtract `step * rows[i][fractional]` from every `rhs[i]` and add `step * c[fractional]` to the node's objective offset. The reported solution is then the node's `x` plus the accumulated shift.",
                ],
                "tests": [
                    {"name": "The workshop, its plan and its prices", "code": r'''
_x, _v, _y = simplex_max([30.0, 20.0], [[4.0, 3.0], [2.0, 1.0]], [240.0, 100.0])
assert abs(_x[0] - 30.0) < 1e-9 and abs(_x[1] - 40.0) < 1e-9, \
    f"the optimal plan is 30 tables and 40 chairs; got {_x!r}"
assert abs(_v - 1700.0) < 1e-9, f"the profit is 1700; got {_v!r}"
assert abs(_y[0] - 5.0) < 1e-9 and abs(_y[1] - 5.0) < 1e-9, \
    f"both resources price at 5 euros an hour; got {_y!r}"
'''},
                    {"name": "The certificate closes", "code": r'''
_c, _a, _b = [30.0, 20.0], [[4.0, 3.0], [2.0, 1.0]], [240.0, 100.0]
_x, _v, _y = simplex_max(_c, _a, _b)
assert is_dual_feasible(_c, _a, _y) is True, f"the returned prices should be dual feasible; got {_y!r}"
assert abs(duality_gap(_c, _a, _b, _x, _y)) < 1e-9, \
    f"a matched optimal pair has gap 0; got {duality_gap(_c, _a, _b, _x, _y)!r}"
assert is_dual_feasible(_c, _a, [10.0, 10.0]) is True, "higher prices are still acceptable"
assert duality_gap(_c, _a, _b, _x, [10.0, 10.0]) > 0.0, \
    "weak duality makes any feasible bill at least the optimal profit"
assert is_dual_feasible(_c, _a, [1.0, 1.0]) is False, "6 euros does not cover a 30 euro table"
assert is_dual_feasible(_c, _a, [-1.0, 20.0]) is False, "a negative price is not dual feasible"
'''},
                    {"name": "Unbounded, infeasible shapes and negative right-hand sides", "code": r'''
try:
    simplex_max([1.0, 0.0], [[1.0, -1.0]], [1.0])
    assert False, "maximising x1 subject to x1 - x2 <= 1 is unbounded; expected ValueError"
except ValueError:
    pass
for _c, _a, _b, _why in [([1.0], [[1.0]], [-1.0], "a negative right-hand side"),
                         ([1.0, 2.0], [[1.0]], [1.0], "a row narrower than c"),
                         ([1.0], [[1.0]], [1.0, 2.0], "a b longer than a"),
                         ([1.0], [], [], "no constraints at all")]:
    try:
        simplex_max(_c, _a, _b)
        assert False, f"{_why} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Three variables, three constraints", "code": r'''
_c = [5.0, 4.0, 3.0]
_a = [[2.0, 3.0, 1.0], [4.0, 1.0, 2.0], [3.0, 4.0, 2.0]]
_b = [5.0, 11.0, 8.0]
_x, _v, _y = simplex_max(_c, _a, _b)
assert abs(_v - 13.0) < 1e-9, f"the optimum is 13; got {_v!r}"
assert abs(_x[0] - 2.0) < 1e-9 and abs(_x[1]) < 1e-9 and abs(_x[2] - 1.0) < 1e-9, \
    f"the optimal point is (2, 0, 1); got {_x!r}"
assert is_dual_feasible(_c, _a, _y) is True, f"the prices should be dual feasible; got {_y!r}"
assert abs(duality_gap(_c, _a, _b, _x, _y)) < 1e-9, "strong duality should close the gap"
'''},
                    {"name": "A degenerate problem terminates", "code": r'''
_x, _v, _y = simplex_max([1.0, 1.0], [[1.0, 1.0], [1.0, 1.0]], [4.0, 4.0])
assert abs(_v - 4.0) < 1e-9, f"two identical constraints still cap the objective at 4; got {_v!r}"
assert abs(_x[0] + _x[1] - 4.0) < 1e-9, f"any point on the edge is optimal; got {_x!r}"
assert abs(sum(_y) - 1.0) < 1e-9, \
    f"the two prices must add to 1, however the degenerate vertex splits them; got {_y!r}"
'''},
                    {"name": "Whole tables and whole chairs", "code": r'''
_c, _a, _b = [30.0, 20.0], [[4.0, 3.0], [2.0, 1.0]], [241.0, 100.0]
_, _relaxed, _ = simplex_max(_c, _a, _b)
assert abs(_relaxed - 1705.0) < 1e-9, f"the relaxation is worth 1705; got {_relaxed!r}"
_x, _v = branch_and_bound(_c, _a, _b)
assert abs(_v - 1700.0) < 1e-6, f"no integer plan beats 1700; got {_v!r}"
assert all(isinstance(v, int) for v in _x), f"the plan must be integers; got {_x!r}"
assert 4 * _x[0] + 3 * _x[1] <= 241 and 2 * _x[0] + _x[1] <= 100, \
    f"the returned plan {_x!r} does not fit in the available hours"
assert abs(30 * _x[0] + 20 * _x[1] - _v) < 1e-6, \
    f"the reported value {_v!r} does not match the plan {_x!r}"
'''},
                    {"name": "A knapsack the relaxation gets wrong", "code": r'''
_c = [8.0, 11.0, 6.0, 4.0]
_a = [[5.0, 7.0, 4.0, 3.0], [1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0],
      [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
_b = [14.0, 1.0, 1.0, 1.0, 1.0]
_, _relaxed, _ = simplex_max(_c, _a, _b)
assert abs(_relaxed - 22.0) < 1e-9, f"the relaxation takes half of item 3 and is worth 22; got {_relaxed!r}"
_x, _v = branch_and_bound(_c, _a, _b)
assert abs(_v - 21.0) < 1e-6, f"the best packing is worth 21; got {_v!r}"
assert all(v in (0, 1) for v in _x), f"every item is taken or left; got {_x!r}"
assert sum(w * v for w, v in zip([5, 7, 4, 3], _x)) <= 14, f"the pack {_x!r} is over weight"
'''},
                    {"name": "An already-integral optimum, and what is refused", "code": r'''
_x, _v = branch_and_bound([1.0, 1.0], [[1.0, 0.0], [0.0, 1.0]], [3.0, 4.0])
assert _x == [3, 4] and abs(_v - 7.0) < 1e-9, \
    f"the relaxation is already integral here; got {(_x, _v)!r}"
try:
    branch_and_bound([1.0, 1.0], [[1.0, -1.0]], [1.0])
    assert False, "a negative entry in a should be refused rather than silently mishandled"
except ValueError:
    pass
try:
    branch_and_bound([1.0], [[2.0]], [-1.0])
    assert False, "a negative right-hand side should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "What the script reports", "code": r'''
_lines = _out.strip().split("\n")
assert len(_lines) == 3, f"main.py should print three lines; it printed {len(_lines)}:\n{_out}"
assert _lines[0] == "plan: [30.0, 40.0] profit: 1700.0", \
    f"the first line was {_lines[0]!r}, expected 'plan: [30.0, 40.0] profit: 1700.0'"
assert _lines[1] == "prices: [5.0, 5.0] gap: 0.0", \
    f"the second line was {_lines[1]!r}, expected 'prices: [5.0, 5.0] gap: 0.0'"
assert _lines[2] == "integer profit with 241 carpentry hours: 1700.0", \
    f"the third line was {_lines[2]!r}; the integer optimum at 241 hours is 1700.0"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a production planner that proves its own answer",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
One library, `optlib.py`, that calibrates a model, plans against it, and hands back the
certificate that the plan is optimal. `main.py` is a demo: three weeks of production
records, a least-squares fit of the unit profits, and a plan for the coming week at two
different capacities.

Nothing is imported but `math` and `dataclasses`. No randomness anywhere: the search
orders are fixed, so two runs agree exactly.

## Vectors and linear systems

- `dot(u, v)`, `norm(v)`, `transpose(a)`, `matvec(a, v)` — each validating its shapes
  and raising `ValueError`.
- `solve(a, b)` — Gaussian elimination with partial pivoting, then back substitution;
  `ValueError` for a non-square `a`, a mismatched `b`, or a pivot at or below `1e-12`.

## The unconstrained half

- `cholesky(a)` and `is_positive_definite(a)` — as in module 3.
- `modified_hessian(h, beta=1e-3)` — a **new** matrix: `h` when it is already positive
  definite, otherwise `h + tau*I` for the first `tau` in `beta, 2*beta, 4*beta, ...`
  that is.
- `minimise(f, grad, hess, x0, tol=1e-8, max_iter=100)` — damped Newton, returning
  `(x, iterations)`. The direction is `solve(modified_hessian(hess(x)), -grad(x))`, never
  an inverse; the step is cut by an Armijo search with `c = 1e-4` and halving, and an
  objective may return `math.inf` where it is undefined.

## The constrained half

- `simplex_max(c, a, b, tol=1e-9, max_pivots=5000)` — `(x, value, duals)` for
  `max c.x` subject to `a x <= b`, `x >= 0`, `b >= 0`, pivoting by **Bland's rule**.
  `ValueError` for an unbounded objective, a negative entry of `b`, or a shape that does
  not line up.
- `is_dual_feasible(c, a, y, tol=1e-9)` and `duality_gap(c, a, b, x, y)`.
- `branch_and_bound(c, a, b, tol=1e-6, max_nodes=20000)` — `(x, value)` with integer
  `x`, depth-first with pruning against the incumbent. Both `a` and `b` must be
  non-negative; a lower bound is imposed by substituting `x_j = k + x'`, which keeps the
  right-hand side non-negative and avoids a phase-one solve.

## Putting it together

- `Plan` — a dataclass with fields `quantities`, `profit`, `prices`, `gap`, `bound`,
  `integral`, in that order.
- `plan(c, a, b, integral=False, tol=1e-6)` — solve the relaxation, take its dual
  prices, and **refuse to report a plan it cannot certify**: if the prices are not dual
  feasible, or the duality gap exceeds `tol`, raise `ValueError` rather than returning
  an unproved optimum. With `integral=True`, replace the quantities and the profit with
  the branch-and-bound answer, keeping the relaxation's prices and recording its value
  in `bound`.
- `plan_report(p)` — a string of exactly `len(p.quantities) + len(p.prices) + 6` lines:

```text
plan:
  x0 = 30
  x1 = 40
profit          = 1700
prices:
  y0 = 5
  y1 = 5
duality gap     = 0.000e+00
relaxation      = 1700
certificate     = integer plan, prices from the relaxation
```

  Quantities, the profit, the prices and the bound are formatted with `:.6g`; the gap
  with `:.3e`. The last line ends `integer plan, prices from the relaxation` when
  `p.integral` is true and `dual feasible, gap closed` when it is not.
''',
        "deliverables": [
            "`optlib.py` — the whole engine, importable with no output and no side effects",
            "`main.py` — a demo that calibrates unit profits from records, plans at two capacities, and prints both reports",
            "`simplex_max` pivoting by Bland's rule, returning the plan, its value and the dual prices in one pass",
            "A `plan` that refuses to report an answer whose prices do not certify it, rather than returning an unproved optimum",
            "`branch_and_bound` with LP bounding, pruning against the incumbent, and lower bounds imposed by substitution rather than by a negative right-hand side",
            "`minimise` — damped Newton with a modified Hessian and an Armijo line search, solving rather than inverting",
            "`plan_report` — a fixed-shape summary of quantities, profit, prices, gap, bound and certificate",
        ],
        "constraints": [
            "Standard library only — `math` and `dataclasses` are enough",
            "`optlib.py` must define names only; importing it must print nothing",
            "No randomness: the pivot rule and the branching order are fixed, so two runs agree exactly",
            "No routine may mutate a matrix or vector it is given",
            "The Newton direction goes through `solve`; no routine may form an inverse",
            "The whole demo must finish in well under a second",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 38,
             "evidence": "Every automated check passes, including the 241-hour case where rounding the relaxation is infeasible and the knapsack where it is merely wrong."},
            {"criterion": "Method discipline", "weight": 22,
             "evidence": "Bland's rule in the simplex, a modified Hessian and a line search in the Newton step, `solve` rather than an inverse, and no library doing the arithmetic."},
            {"criterion": "Certificates and diagnostics", "weight": 20,
             "evidence": "The returned prices are dual feasible, the duality gap is reported, and an uncertified plan raises instead of being returned."},
            {"criterion": "Validation", "weight": 12,
             "evidence": "Negative right-hand sides, ragged matrices, unbounded objectives, singular systems and infeasible integer problems all raise ValueError."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "A docstring on every public routine, no dead code, and no debug prints left behind in optlib.py."},
        ],
        "hints": [
            "Write `solve` first and build everything on it: the Newton direction, and nothing else — the simplex does its own elimination inside the tableau, which is a different algorithm wearing similar clothes.",
            "The dual prices are already in the tableau when the simplex stops: they are the objective-row entries under the `m` slack columns. Computing them a second way is both slower and a chance to disagree with yourself.",
            "`plan` should compute the relaxation once, check the certificate, and only then branch. Running branch and bound first wastes the whole search when the problem turns out to be unbounded.",
            "For the lower-bound branch, subtract `step * rows[i][j]` from every right-hand side and add `step * c[j]` to the node's offset. The reported quantities are the node's `x` plus the accumulated shift, which is why the shift has to travel with the node.",
        ],
        "files": [
            {"name": "optlib.py", "content": r'''
import math
from dataclasses import dataclass


@dataclass
class Plan:
    quantities: list
    profit: float
    prices: list
    gap: float
    bound: float
    integral: bool


def dot(u, v):
    """Sum of products; ValueError when the lengths differ."""
    # your code here


def norm(v):
    """Euclidean length."""
    # your code here


def transpose(a):
    """Rows become columns."""
    # your code here


def matvec(a, v):
    """Matrix times vector."""
    # your code here


def solve(a, b):
    """Gaussian elimination with partial pivoting, then back substitution."""
    # your code here


def cholesky(a):
    """Lower triangular L with L L^T = a; ValueError when a is not positive definite."""
    # your code here


def is_positive_definite(a):
    """True when cholesky succeeds."""
    # your code here


def modified_hessian(h, beta=1e-3):
    """A new matrix: h, or h + tau*I for the first tau in beta, 2*beta, ... that is PD."""
    # your code here


def minimise(f, grad, hess, x0, tol=1e-8, max_iter=100):
    """(x, iterations) by damped Newton with a modified Hessian."""
    # your code here


def simplex_max(c, a, b, tol=1e-9, max_pivots=5000):
    """(x, value, duals) for max c.x subject to a x <= b, x >= 0, b >= 0."""
    # your code here


def is_dual_feasible(c, a, y, tol=1e-9):
    """True when y >= 0 and every column prices its variable at or above c."""
    # your code here


def duality_gap(c, a, b, x, y):
    """dot(b, y) - dot(c, x)."""
    # your code here


def branch_and_bound(c, a, b, tol=1e-6, max_nodes=20000):
    """(x, value) with integer x, by depth-first search over LP relaxations."""
    # your code here


def plan(c, a, b, integral=False, tol=1e-6):
    """A certified Plan, or ValueError if the prices do not prove it optimal."""
    # your code here


def plan_report(p):
    """A fixed-shape textual summary of a Plan."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from optlib import minimise, plan, plan_report

# three weeks of records: tables made, chairs made, profit earned
RECORDS = [[10.0, 20.0], [20.0, 10.0], [30.0, 30.0]]
EARNED = [700.0, 800.0, 1500.0]


def sse(w):
    return sum((row[0] * w[0] + row[1] * w[1] - y) ** 2
               for row, y in zip(RECORDS, EARNED))


def sse_gradient(w):
    residual = [row[0] * w[0] + row[1] * w[1] - y for row, y in zip(RECORDS, EARNED)]
    return [2.0 * sum(row[j] * r for row, r in zip(RECORDS, residual))
            for j in range(2)]


def sse_hessian(w):
    return [[2.0 * sum(row[i] * row[j] for row in RECORDS) for j in range(2)]
            for i in range(2)]


unit_profit, steps = minimise(sse, sse_gradient, sse_hessian, [0.0, 0.0])
print("calibrated unit profits:", [round(v, 6) for v in unit_profit],
      "in", steps, "Newton step(s)")

CAPACITY = [[4.0, 3.0], [2.0, 1.0]]
for hours in ([240.0, 100.0], [241.0, 100.0]):
    print()
    print(f"--- carpentry {hours[0]:.0f} h, finishing {hours[1]:.0f} h")
    print(plan_report(plan(unit_profit, CAPACITY, hours, integral=True)))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "optlib.py", "content": r'''
import math
from dataclasses import dataclass


@dataclass
class Plan:
    quantities: list
    profit: float
    prices: list
    gap: float
    bound: float
    integral: bool


def dot(u, v):
    """Sum of products; ValueError when the lengths differ."""
    if len(u) != len(v):
        raise ValueError("vectors must have the same length")
    return sum(float(a) * float(b) for a, b in zip(u, v))


def norm(v):
    """Euclidean length."""
    return math.sqrt(dot(v, v))


def transpose(a):
    """Rows become columns."""
    if not a or not a[0]:
        raise ValueError("cannot transpose an empty matrix")
    width = len(a[0])
    if any(len(row) != width for row in a):
        raise ValueError("all rows must have the same length")
    return [[float(a[i][j]) for i in range(len(a))] for j in range(width)]


def matvec(a, v):
    """Matrix times vector."""
    if any(len(row) != len(v) for row in a):
        raise ValueError("each row must have one entry per variable")
    return [dot(row, v) for row in a]


def solve(a, b):
    """Gaussian elimination with partial pivoting, then back substitution."""
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("expected a square matrix")
    if len(b) != n:
        raise ValueError("b must have one entry per row")
    m = [[float(v) for v in row] + [float(b[i])] for i, row in enumerate(a)]
    for col in range(n):
        best = col
        for r in range(col + 1, n):
            if abs(m[r][col]) > abs(m[best][col]):
                best = r
        if abs(m[best][col]) <= 1e-12:
            raise ValueError("matrix is singular to working precision")
        m[col], m[best] = m[best], m[col]
        for r in range(col + 1, n):
            factor = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= factor * m[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        total = m[i][n]
        for j in range(i + 1, n):
            total -= m[i][j] * x[j]
        x[i] = total / m[i][i]
    return x


def _square_symmetric(a):
    """The order of a square symmetric matrix, or ValueError saying which it is not."""
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("expected a square matrix")
    for i in range(n):
        for j in range(i + 1, n):
            if abs(float(a[i][j]) - float(a[j][i])) > 1e-12:
                raise ValueError("expected a symmetric matrix")
    return n


def cholesky(a):
    """Lower triangular L with L L^T = a; ValueError when a is not positive definite."""
    n = _square_symmetric(a)
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            total = float(a[i][j]) - sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if total <= 0.0:
                    raise ValueError("matrix is not positive definite")
                lower[i][j] = math.sqrt(total)
            else:
                lower[i][j] = total / lower[j][j]
    return lower


def is_positive_definite(a):
    """True when cholesky succeeds."""
    _square_symmetric(a)
    try:
        cholesky(a)
    except ValueError:
        return False
    return True


def modified_hessian(h, beta=1e-3):
    """A new matrix: h, or h + tau*I for the first tau in beta, 2*beta, ... that is PD."""
    n = _square_symmetric(h)
    shifted = [[float(v) for v in row] for row in h]
    if is_positive_definite(shifted):
        return shifted
    tau = float(beta)
    for _ in range(200):
        shifted = [[float(h[i][j]) + (tau if i == j else 0.0) for j in range(n)]
                   for i in range(n)]
        if is_positive_definite(shifted):
            return shifted
        tau *= 2.0
    raise ValueError("could not shift the Hessian into positive definiteness")


def minimise(f, grad, hess, x0, tol=1e-8, max_iter=100):
    """(x, iterations) by damped Newton with a modified Hessian."""
    x = [float(v) for v in x0]
    for k in range(max_iter):
        g = grad(x)
        if norm(g) <= tol:
            return (x, k)
        p = solve(modified_hessian(hess(x)), [-float(gi) for gi in g])
        slope = dot(g, p)
        if slope >= 0.0:
            raise ValueError("the shifted Newton direction is not a descent direction")
        base = f(x)
        t = 1.0
        accepted = False
        for _ in range(61):
            trial = [xi + t * pi for xi, pi in zip(x, p)]
            try:
                value = f(trial)
            except OverflowError:
                value = math.inf
            if math.isfinite(value) and value <= base + 1e-4 * t * slope:
                accepted = True
                break
            t *= 0.5
        if not accepted:
            raise ValueError("no step along the Newton direction was accepted")
        x = [xi + t * pi for xi, pi in zip(x, p)]
    return (x, max_iter)


def simplex_max(c, a, b, tol=1e-9, max_pivots=5000):
    """(x, value, duals) for max c.x subject to a x <= b, x >= 0, b >= 0."""
    m = len(a)
    if m == 0:
        raise ValueError("need at least one constraint")
    n = len(c)
    if any(len(row) != n for row in a):
        raise ValueError("each row of a needs one entry per variable")
    if len(b) != m:
        raise ValueError("b needs one entry per constraint")
    if any(float(bi) < -tol for bi in b):
        raise ValueError("every entry of b must be non-negative")

    table = []
    for i in range(m):
        row = [float(v) for v in a[i]] + [0.0] * m + [float(b[i])]
        row[n + i] = 1.0
        table.append(row)
    table.append([-float(v) for v in c] + [0.0] * (m + 1))
    basis = [n + i for i in range(m)]

    for _ in range(max_pivots):
        entering = -1
        for j in range(n + m):
            if table[m][j] < -tol:
                entering = j
                break
        if entering < 0:
            x = [0.0] * n
            for i in range(m):
                if basis[i] < n:
                    x[basis[i]] = table[i][-1]
            return (x, table[m][-1], [table[m][n + i] for i in range(m)])
        leaving = -1
        best = None
        for i in range(m):
            if table[i][entering] > tol:
                ratio = table[i][-1] / table[i][entering]
                if best is None or ratio < best - 1e-12 or \
                        (abs(ratio - best) <= 1e-12 and basis[i] < basis[leaving]):
                    best = ratio
                    leaving = i
        if leaving < 0:
            raise ValueError("the objective is unbounded above on this feasible set")
        pivot = table[leaving][entering]
        table[leaving] = [v / pivot for v in table[leaving]]
        for i in range(m + 1):
            if i != leaving:
                factor = table[i][entering]
                table[i] = [v - factor * w for v, w in zip(table[i], table[leaving])]
        basis[leaving] = entering
    raise ValueError("the simplex method did not terminate within max_pivots")


def is_dual_feasible(c, a, y, tol=1e-9):
    """True when y >= 0 and every column prices its variable at or above c."""
    if len(y) != len(a):
        raise ValueError("y needs one price per constraint")
    if any(float(yi) < -tol for yi in y):
        return False
    for j in range(len(c)):
        if sum(float(a[i][j]) * float(y[i]) for i in range(len(a))) < float(c[j]) - tol:
            return False
    return True


def duality_gap(c, a, b, x, y):
    """dot(b, y) - dot(c, x)."""
    if len(b) != len(y) or len(c) != len(x):
        raise ValueError("the pair must match the problem")
    return dot(b, y) - dot(c, x)


def branch_and_bound(c, a, b, tol=1e-6, max_nodes=20000):
    """(x, value) with integer x, by depth-first search over LP relaxations."""
    n = len(c)
    if any(float(v) < 0.0 for row in a for v in row):
        raise ValueError("the shifting branch rule needs a non-negative a")
    if any(float(v) < 0.0 for v in b):
        raise ValueError("every entry of b must be non-negative")
    best_value = -math.inf
    best_x = None
    stack = [([[float(v) for v in row] for row in a], [float(v) for v in b],
              [0.0] * n, 0.0)]
    nodes = 0
    while stack:
        nodes += 1
        if nodes > max_nodes:
            raise ValueError("branch and bound ran out of nodes")
        rows, rhs, shift, offset = stack.pop()
        try:
            x, value, _ = simplex_max(c, rows, rhs)
        except ValueError as exc:
            if "unbounded" in str(exc):
                raise
            continue
        total = value + offset
        if total <= best_value + tol:
            continue
        fractional = -1
        for j in range(n):
            if abs(x[j] - round(x[j])) > tol:
                fractional = j
                break
        if fractional < 0:
            best_value = total
            best_x = [int(round(x[j] + shift[j])) for j in range(n)]
            continue
        floor_value = math.floor(x[fractional] + shift[fractional])
        step = floor_value + 1 - shift[fractional]
        if step >= 0:
            moved = [rhs[i] - step * rows[i][fractional] for i in range(len(rows))]
            if all(v >= -1e-9 for v in moved):
                lifted = list(shift)
                lifted[fractional] = float(floor_value + 1)
                stack.append(([row[:] for row in rows], moved, lifted,
                              offset + step * float(c[fractional])))
        cap = floor_value - shift[fractional]
        if cap >= 0:
            extra = [0.0] * n
            extra[fractional] = 1.0
            stack.append(([row[:] for row in rows] + [extra],
                          list(rhs) + [float(cap)], list(shift), offset))
    if best_x is None:
        raise ValueError("no integer point is feasible")
    return (best_x, best_value)


def plan(c, a, b, integral=False, tol=1e-6):
    """A certified Plan, or ValueError if the prices do not prove it optimal."""
    x, value, prices = simplex_max(c, a, b)
    gap = duality_gap(c, a, b, x, prices)
    if not is_dual_feasible(c, a, prices) or abs(gap) > tol:
        raise ValueError("the prices do not certify this plan; refusing to report "
                         "an unproved optimum")
    if not integral:
        return Plan(x, value, prices, gap, value, False)
    whole, whole_value = branch_and_bound(c, a, b)
    return Plan(whole, whole_value, prices, gap, value, True)


def plan_report(p):
    """A fixed-shape textual summary of a Plan."""
    lines = ["plan:"]
    for i, q in enumerate(p.quantities):
        lines.append(f"  x{i} = {q:.6g}")
    lines.append(f"profit          = {p.profit:.6g}")
    lines.append("prices:")
    for i, y in enumerate(p.prices):
        lines.append(f"  y{i} = {y:.6g}")
    lines.append(f"duality gap     = {p.gap:.3e}")
    lines.append(f"relaxation      = {p.bound:.6g}")
    lines.append("certificate     = " +
                 ("integer plan, prices from the relaxation" if p.integral
                  else "dual feasible, gap closed"))
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from optlib import minimise, plan, plan_report

# three weeks of records: tables made, chairs made, profit earned
RECORDS = [[10.0, 20.0], [20.0, 10.0], [30.0, 30.0]]
EARNED = [700.0, 800.0, 1500.0]


def sse(w):
    return sum((row[0] * w[0] + row[1] * w[1] - y) ** 2
               for row, y in zip(RECORDS, EARNED))


def sse_gradient(w):
    residual = [row[0] * w[0] + row[1] * w[1] - y for row, y in zip(RECORDS, EARNED)]
    return [2.0 * sum(row[j] * r for row, r in zip(RECORDS, residual))
            for j in range(2)]


def sse_hessian(w):
    return [[2.0 * sum(row[i] * row[j] for row in RECORDS) for j in range(2)]
            for i in range(2)]


unit_profit, steps = minimise(sse, sse_gradient, sse_hessian, [0.0, 0.0])
print("calibrated unit profits:", [round(v, 6) for v in unit_profit],
      "in", steps, "Newton step(s)")

CAPACITY = [[4.0, 3.0], [2.0, 1.0]]
for hours in ([240.0, 100.0], [241.0, 100.0]):
    print()
    print(f"--- carpentry {hours[0]:.0f} h, finishing {hours[1]:.0f} h")
    print(plan_report(plan(unit_profit, CAPACITY, hours, integral=True)))
'''},
        ],
        "tests": [
            {"name": "Vectors, matrices and one linear solve", "code": r'''
from optlib import dot, norm, transpose, matvec, solve
assert dot([1, 2, 3], [4, 5, 6]) == 32.0, f"dot gave {dot([1, 2, 3], [4, 5, 6])!r}"
assert abs(norm([3, 4]) - 5.0) < 1e-12, f"norm([3, 4]) gave {norm([3, 4])!r}"
assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]], \
    f"transpose gave {transpose([[1, 2, 3], [4, 5, 6]])!r}"
assert matvec([[1, 2], [3, 4]], [1, 1]) == [3.0, 7.0], f"matvec gave {matvec([[1, 2], [3, 4]], [1, 1])!r}"
_x = solve([[0.0, 1.0], [1.0, 0.0]], [2.0, 3.0])
assert abs(_x[0] - 3.0) < 1e-12 and abs(_x[1] - 2.0) < 1e-12, \
    f"the rows must be swapped before dividing; solve gave {_x!r}"
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
assert abs(solve(_a, [1, 2, 3])[0] - 6.0 / 41.0) < 1e-12, "x[0] should be 6/41"
assert _a == [[4, 3, 2], [1, 5, 7], [2, 2, 9]], "solve must not mutate its input"
for _args in [([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0]), ([[1.0, 2.0], [3.0, 4.0]], [1.0])]:
    try:
        solve(*_args)
        assert False, f"solve{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Curvature, repaired", "code": r'''
import math as _m
from optlib import cholesky, is_positive_definite, modified_hessian
_l = cholesky([[4.0, 2.0], [2.0, 4.0]])
assert abs(_l[0][0] - 2.0) < 1e-12 and abs(_l[1][1] - _m.sqrt(3.0)) < 1e-12, f"L gave {_l!r}"
assert is_positive_definite([[4.0, 2.0], [2.0, 4.0]]) is True, "eigenvalues 2 and 6"
assert is_positive_definite([[1.0, 2.0], [2.0, 1.0]]) is False, "eigenvalues -1 and 3"
_h = [[-5.88]]
_shifted = modified_hessian(_h)
assert abs(_shifted[0][0] - 2.312) < 1e-9, \
    f"thirteen doublings of 1e-3 give tau = 8.192, so the shift is 2.312; got {_shifted[0][0]!r}"
assert _h == [[-5.88]], "modified_hessian must not mutate the Hessian it is given"
assert modified_hessian([[4.0, 2.0], [2.0, 4.0]]) == [[4.0, 2.0], [2.0, 4.0]], \
    "an already positive definite Hessian is returned unchanged"
'''},
            {"name": "The Newton core", "code": r'''
import math as _m
from optlib import minimise
_bowl = lambda v: 2 * v[0] ** 2 + 2 * v[0] * v[1] + 2 * v[1] ** 2 - 6 * v[0] - 6 * v[1]
_bg = lambda v: [4 * v[0] + 2 * v[1] - 6, 2 * v[0] + 4 * v[1] - 6]
_bh = lambda v: [[4.0, 2.0], [2.0, 4.0]]
_x, _steps = minimise(_bowl, _bg, _bh, [50.0, -30.0])
assert _steps == 1, f"a quadratic takes one Newton step from anywhere; it took {_steps}"
assert abs(_x[0] - 1.0) < 1e-9 and abs(_x[1] - 1.0) < 1e-9, f"the run ended at {_x!r}"
_well = lambda v: v[0] ** 4 - 3.0 * v[0] ** 2 + 1.0
_wg = lambda v: [4.0 * v[0] ** 3 - 6.0 * v[0]]
_wh = lambda v: [[12.0 * v[0] ** 2 - 6.0]]
_x, _steps = minimise(_well, _wg, _wh, [0.1])
assert abs(_x[0] - _m.sqrt(1.5)) < 1e-6, \
    f"from 0.1 the curvature is negative and the shift must turn the step right; got {_x!r}"
'''},
            {"name": "Calibration against the closed form", "code": r'''
from optlib import minimise, solve, transpose, matvec


def _fit(rows, targets, start):
    def value(w):
        return sum((sum(a * b for a, b in zip(row, w)) - y) ** 2
                   for row, y in zip(rows, targets))

    def gradient(w):
        residual = [sum(a * b for a, b in zip(row, w)) - y
                    for row, y in zip(rows, targets)]
        return [2.0 * sum(row[j] * r for row, r in zip(rows, residual))
                for j in range(len(w))]

    def hessian(w):
        return [[2.0 * sum(row[i] * row[j] for row in rows) for j in range(len(w))]
                for i in range(len(w))]

    return minimise(value, gradient, hessian, start)


_w, _steps = _fit([[10.0, 20.0], [20.0, 10.0], [30.0, 30.0]], [700.0, 800.0, 1500.0], [0.0, 0.0])
assert _steps == 1, f"least squares is a quadratic and needs one step; it took {_steps}"
assert abs(_w[0] - 30.0) < 1e-9 and abs(_w[1] - 20.0) < 1e-9, \
    f"the records are consistent with unit profits of 30 and 20; got {_w!r}"
_rows = [[1.0, 1.0], [1.0, 2.0], [1.0, 3.0]]
_y = [1.0, 2.0, 2.0]
_w, _steps = _fit(_rows, _y, [0.0, 0.0])
_normal = solve([[3.0, 6.0], [6.0, 14.0]], [5.0, 11.0])
assert abs(_w[0] - _normal[0]) < 1e-9 and abs(_w[1] - _normal[1]) < 1e-9, \
    f"the fit {_w!r} disagrees with the normal equations {_normal!r}"
assert abs(_w[0] - 2.0 / 3.0) < 1e-9 and abs(_w[1] - 0.5) < 1e-9, \
    f"the closed form is (2/3, 1/2); got {_w!r}"
'''},
            {"name": "The linear program and the prices it certifies", "code": r'''
from optlib import simplex_max, is_dual_feasible, duality_gap
_c, _a, _b = [30.0, 20.0], [[4.0, 3.0], [2.0, 1.0]], [240.0, 100.0]
_x, _v, _y = simplex_max(_c, _a, _b)
assert abs(_x[0] - 30.0) < 1e-9 and abs(_x[1] - 40.0) < 1e-9, f"the plan is (30, 40); got {_x!r}"
assert abs(_v - 1700.0) < 1e-9, f"the profit is 1700; got {_v!r}"
assert abs(_y[0] - 5.0) < 1e-9 and abs(_y[1] - 5.0) < 1e-9, f"both prices are 5; got {_y!r}"
assert is_dual_feasible(_c, _a, _y) is True, "the returned prices must be dual feasible"
assert abs(duality_gap(_c, _a, _b, _x, _y)) < 1e-9, "strong duality closes the gap"
assert is_dual_feasible(_c, _a, [1.0, 1.0]) is False, "6 euros does not cover a 30 euro table"
_c3 = [5.0, 4.0, 3.0]
_a3 = [[2.0, 3.0, 1.0], [4.0, 1.0, 2.0], [3.0, 4.0, 2.0]]
_x3, _v3, _y3 = simplex_max(_c3, _a3, [5.0, 11.0, 8.0])
assert abs(_v3 - 13.0) < 1e-9, f"the three-variable optimum is 13; got {_v3!r}"
assert abs(duality_gap(_c3, _a3, [5.0, 11.0, 8.0], _x3, _y3)) < 1e-9, "the gap should close here too"
'''},
            {"name": "Refusals, not guesses", "code": r'''
from optlib import simplex_max, plan
try:
    simplex_max([1.0, 0.0], [[1.0, -1.0]], [1.0])
    assert False, "an unbounded objective should raise ValueError"
except ValueError:
    pass
for _args, _why in [(([1.0], [[1.0]], [-1.0]), "a negative right-hand side"),
                    (([1.0, 2.0], [[1.0]], [1.0]), "a row narrower than c"),
                    (([1.0], [[1.0]], [1.0, 2.0]), "a b longer than a")]:
    try:
        plan(*_args)
        assert False, f"{_why} should raise ValueError"
    except ValueError:
        pass
try:
    plan([1.0, 0.0], [[1.0, -1.0]], [1.0])
    assert False, "plan must not report an answer for an unbounded problem"
except ValueError:
    pass
'''},
            {"name": "Whole numbers, where rounding fails", "code": r'''
from optlib import plan, simplex_max, branch_and_bound
_c, _a, _b = [30.0, 20.0], [[4.0, 3.0], [2.0, 1.0]], [241.0, 100.0]
_relaxed = simplex_max(_c, _a, _b)[1]
assert abs(_relaxed - 1705.0) < 1e-9, f"the relaxation is worth 1705; got {_relaxed!r}"
_p = plan(_c, _a, _b, integral=True)
assert _p.integral is True and abs(_p.bound - 1705.0) < 1e-9, \
    f"the plan should record the relaxation as its bound; got {_p!r}"
assert abs(_p.profit - 1700.0) < 1e-6, f"no integer plan beats 1700; got {_p.profit!r}"
assert all(isinstance(q, int) for q in _p.quantities), f"quantities must be ints; got {_p.quantities!r}"
assert 4 * _p.quantities[0] + 3 * _p.quantities[1] <= 241, "the plan overruns the carpentry hours"
assert 2 * _p.quantities[0] + _p.quantities[1] <= 100, "the plan overruns the finishing hours"
assert 4 * 30 + 3 * 41 > 241, "rounding the relaxation to (30, 41) is infeasible, which is the point"
_kc = [8.0, 11.0, 6.0, 4.0]
_ka = [[5.0, 7.0, 4.0, 3.0], [1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0],
       [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
_kb = [14.0, 1.0, 1.0, 1.0, 1.0]
assert abs(simplex_max(_kc, _ka, _kb)[1] - 22.0) < 1e-9, "the knapsack relaxation is worth 22"
_kx, _kv = branch_and_bound(_kc, _ka, _kb)
assert abs(_kv - 21.0) < 1e-6, f"no integer packing beats 21; got {_kv!r}"
assert sum(w * v for w, v in zip([5, 7, 4, 3], _kx)) <= 14, f"the pack {_kx!r} is over weight"
'''},
            {"name": "The report has a fixed shape", "code": r'''
from optlib import plan, plan_report
_p = plan([30.0, 20.0], [[4.0, 3.0], [2.0, 1.0]], [240.0, 100.0])
_rep = plan_report(_p)
assert isinstance(_rep, str), "plan_report returns a string, it does not print"
_lines = _rep.split("\n")
assert len(_lines) == len(_p.quantities) + len(_p.prices) + 6, \
    f"expected {len(_p.quantities) + len(_p.prices) + 6} lines, got {len(_lines)}: {_lines!r}"
assert _lines[0] == "plan:", f"the first line was {_lines[0]!r}"
assert _lines[1].strip() == "x0 = 30", f"the first quantity line was {_lines[1]!r}"
assert _lines[2].strip() == "x1 = 40", f"the second quantity line was {_lines[2]!r}"
assert _lines[3].startswith("profit") and _lines[3].rstrip().endswith("1700"), \
    f"the profit line was {_lines[3]!r}"
assert _lines[4] == "prices:", f"line 5 was {_lines[4]!r}"
assert _lines[5].strip() == "y0 = 5" and _lines[6].strip() == "y1 = 5", \
    f"the price lines were {_lines[5]!r} and {_lines[6]!r}"
assert _lines[7].startswith("duality gap") and "e" in _lines[7], f"line 8 was {_lines[7]!r}"
assert _lines[8].startswith("relaxation"), f"line 9 was {_lines[8]!r}"
assert _lines[9].rstrip().endswith("dual feasible, gap closed"), f"line 10 was {_lines[9]!r}"
_q = plan([30.0, 20.0], [[4.0, 3.0], [2.0, 1.0]], [241.0, 100.0], integral=True)
assert plan_report(_q).split("\n")[-1].rstrip().endswith(
    "integer plan, prices from the relaxation"), "an integer plan must say so"
'''},
            {"name": "optlib.py is import-clean, pure and fast", "code": r'''
import time as _t
_src = open("optlib.py").read()
assert "print(" not in _src, "optlib.py defines routines; the printing belongs in main.py"
for _banned in ("numpy", "scipy", "random"):
    assert _banned not in _src, f"optlib.py must not reach for {_banned}"
from optlib import plan, simplex_max, branch_and_bound
_a = [[4.0, 3.0], [2.0, 1.0]]
_b = [241.0, 100.0]
_before_a = [row[:] for row in _a]
_before_b = _b[:]
plan([30.0, 20.0], _a, _b, integral=True)
assert _a == _before_a and _b == _before_b, "no routine may mutate the data it is given"
_start = _t.time()
for _ in range(5):
    plan([30.0, 20.0], _a, _b, integral=True)
_elapsed = _t.time() - _start
assert _elapsed < 5.0, f"five certified plans took {_elapsed:.2f}s, which is far too slow"
assert _out.strip().split("\n")[0].startswith("calibrated unit profits: [30.0, 20.0]"), \
    f"main.py should calibrate the unit profits first; its output began:\n{_out[:200]}"
'''},
        ],
    },
}
