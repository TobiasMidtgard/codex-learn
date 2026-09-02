"""ROB520 — Advanced Elective: Robotics & Autonomy. Author module."""

COURSE = {
    "id": "ROB520",
    "title": "Advanced Elective — Robotics & Autonomy",
    "year": 5,
    "level": "Expert",
    "prereqs": ["ML401", "MA121"],
    "stack": ["Python", "ROS 2 (reference)"],
    "credits": 10,
    "hours": 150,
    "icon": "☸",
    "summary": (
        "The four pillars an autonomous machine stands on: where its body is, where "
        "it is in the world, where it should go, and how it drives the actuators to "
        "get there. You write the analytic inverse kinematics of a planar arm, a "
        "Kalman and a particle filter, A* on an inflated occupancy grid and an RRT in "
        "continuous space, and a PID loop with anti-windup — then bolt all four "
        "together into a delivery agent scored over seeded trials."
    ),
    "outcomes": [
        "Derive and implement forward and inverse kinematics for a planar manipulator, including reachability and elbow branches",
        "Identify kinematic singularities from the Jacobian determinant rather than from symptoms",
        "Implement the predict/update recursion of a Kalman filter and explain why the covariance shrinks",
        "Apply a particle filter where the posterior is multimodal and a Gaussian assumption fails",
        "Search an occupancy grid with A* under an admissible octile heuristic and obstacle inflation",
        "Build a sampling-based planner and compare it against a grid search on path length and node count",
        "Tune a PID controller and quantify rise time, overshoot, settling time and steady-state error",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone autonomy stack (60%).",
    "reading": [
        "Siciliano, Sciavicco, Villani & Oriolo, *Robotics: Modelling, Planning and Control*, Springer 2009 — chapters 2, 3 and 12",
        "Thrun, Burgard & Fox, *Probabilistic Robotics*, MIT Press 2005 — chapters 3, 4 and 8",
        "LaValle, *Planning Algorithms*, Cambridge University Press 2006 — chapters 5 and 14",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Kinematics of a planar manipulator",
            "summary": "Joint angles to end-effector pose, and the harder journey back.",
            "concepts": [
                "Configuration space vs task space; the map between them is the forward kinematics",
                "Forward kinematics of a planar 2R arm by composing two planar rotations",
                "The reachable workspace is an annulus of radii |l1 - l2| and l1 + l2",
                "Analytic inverse kinematics via the law of cosines; two elbow branches per reachable point",
                "The manipulator Jacobian maps joint rates to end-effector velocity",
                "det J = l1 l2 sin(theta2): the arm is singular fully stretched and fully folded",
                "Manipulability |det J| as a scalar score for how well-conditioned a pose is",
            ],
            "read": [
                {
                    "title": "Two angles in, one point out, and the way back",
                    "minutes": 14,
                    "body": r'''
A two-link arm is bolted to a bench. The shoulder joint sits at the origin, the upper
arm is 1.3 m long, the forearm is 0.7 m, and somebody has put a bolt on the bench at
(1.2, 0.9) and asked you to put the tip of the arm on it. You can command two things:
the shoulder angle and the elbow angle. Everything in this module is the question
"what angles?" and the two or three surprises hiding inside it.

## Forward: where the tip ends up

Start with the direction that is easy. Turn the shoulder by $\theta_1$ from the x-axis.
The elbow is then at the end of a rod of length $l_1$ pointing in that direction, so it
sits at $(l_1\cos\theta_1,\ l_1\sin\theta_1)$. The forearm is another rod, of length
$l_2$, and the elbow angle $\theta_2$ is measured *relative to the upper arm*, which is
how the motor at the elbow experiences it. In world terms, then, the forearm points at
absolute angle $\theta_1 + \theta_2$, and the tip is the elbow plus that second rod:

$$x = l_1\cos\theta_1 + l_2\cos(\theta_1+\theta_2), \qquad
  y = l_1\sin\theta_1 + l_2\sin(\theta_1+\theta_2).$$

That is the forward kinematics. It is two vector additions and it never fails: any pair
of angles gives exactly one tip position.

```python
import math


def forward(t1, t2, l1=1.0, l2=1.0):
    return (l1 * math.cos(t1) + l2 * math.cos(t1 + t2),
            l1 * math.sin(t1) + l2 * math.sin(t1 + t2))


print(forward(0.0, 0.0))                 # stretched along x: (2.0, 0.0)
x, y = forward(0.0, math.pi / 2)
print(round(x, 6), round(y, 6))          # elbow bent square: 1.0 1.0
```

The second call is worth holding in your head, because it comes back later as the
worked example for the reverse direction: upper arm along x, forearm turned a quarter
turn, tip at (1, 1).

## Where the tip can be at all

Before asking for the angles that reach a point, ask whether any do. Hold the shoulder
still and swing only the elbow. The tip's distance from the shoulder, $r$, is the third
side of a triangle whose other two sides are $l_1$ and $l_2$. A triangle's third side
can be no longer than the other two added together and no shorter than their
difference, so

$$|l_1 - l_2| \le r \le l_1 + l_2 .$$

The reachable set is an annulus: a disc of radius $l_1 + l_2$ with a hole of radius
$|l_1 - l_2|$ punched out of the middle. For the bench arm that is 0.6 m to 2.0 m, and
the bolt is at $r = \sqrt{1.2^2 + 0.9^2} = 1.5$ m, so it is reachable. With two equal
links the hole has radius zero and the arm can fold back onto its own shoulder.

One practical note that the lab turns into a test: a point that `forward` produced can
land a rounding error outside the annulus, at 2.0000000000000004 when the edge is 2.0.
A reachability test with no tolerance would refuse the arm's own pose.

## Back from the point: the law of cosines

Now the direction that is not easy. You are given $(x, y)$ and want $\theta_1, \theta_2$.
The triangle from the previous section is the whole trick. Its sides are $l_1$, $l_2$
and $r$, and the law of cosines relates the side $r$ to the interior angle $\phi$
opposite it, the angle at the elbow *inside* the triangle:

$$r^2 = l_1^2 + l_2^2 - 2 l_1 l_2 \cos\phi .$$

But $\theta_2$ is not $\phi$. The elbow motor measures how far the forearm has turned
away from the line of the upper arm, and that is the exterior angle, $\theta_2 = \pi -
\phi$. Since $\cos(\pi - \phi) = -\cos\phi$, the sign flips and

$$\cos\theta_2 = \frac{r^2 - l_1^2 - l_2^2}{2 l_1 l_2}.$$

Put the bench numbers in. $r^2 = 2.25$, $l_1^2 = 1.69$, $l_2^2 = 0.49$, $2 l_1 l_2 = 1.82$,
so $\cos\theta_2 = 0.07 / 1.82 = 0.0385$ and $\theta_2 = \pm 87.8^\circ$. Two signs, and
the next section is about why. Take the positive one for now: $\sin\theta_2 =
\sqrt{1 - 0.0385^2} = 0.9993$.

For $\theta_1$, look at the tip from the shoulder. Its direction is
$\operatorname{atan2}(y, x) = \operatorname{atan2}(0.9, 1.2) = 36.87^\circ$. That
direction is the upper arm's direction $\theta_1$ plus the angle by which the tip is
offset from the upper arm's line, and that offset comes from the same triangle: in a
frame aligned with the upper arm the tip sits at $(l_1 + l_2\cos\theta_2,\
l_2\sin\theta_2) = (1.3269, 0.6995)$, at angle $\operatorname{atan2}(0.6995, 1.3269) =
27.80^\circ$. So

$$\theta_1 = \operatorname{atan2}(y, x) - \operatorname{atan2}(l_2\sin\theta_2,\
l_1 + l_2\cos\theta_2) = 36.87^\circ - 27.80^\circ = 9.07^\circ .$$

```python
import math


def forward(t1, t2, l1=1.0, l2=1.0):
    return (l1 * math.cos(t1) + l2 * math.cos(t1 + t2),
            l1 * math.sin(t1) + l2 * math.sin(t1 + t2))


def inverse(x, y, l1=1.0, l2=1.0, elbow="up"):
    c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)
    c2 = max(-1.0, min(1.0, c2))
    s2 = math.sqrt(1.0 - c2 * c2)
    if elbow == "down":
        s2 = -s2
    t2 = math.atan2(s2, c2)
    t1 = math.atan2(y, x) - math.atan2(l2 * s2, l1 + l2 * c2)
    return (t1, t2)


for branch in ("up", "down"):
    t1, t2 = inverse(1.2, 0.9, 1.3, 0.7, branch)
    x, y = forward(t1, t2, 1.3, 0.7)
    print(branch, round(math.degrees(t1), 2), round(math.degrees(t2), 2),
          "->", round(x, 6), round(y, 6))
```

This prints `up 9.07 87.8 -> 1.2 0.9` and `down 64.67 -87.8 -> 1.2 0.9`: both answers
put the tip on the bolt. Run the same function on the earlier example, `inverse(1, 1)`
with unit links, and the up branch gives $(0, \pi/2)$, the pose that `forward` started
from.

## Two answers, and why exactly two

Taking the square root threw away a sign, and the sign is real: $\sin\theta_2 > 0$ is
the elbow bent one way, $\sin\theta_2 < 0$ the other. Both elbows put the tip on the
same point, because both come from the same triangle reflected across the line from
shoulder to tip. The lab calls them `"up"` and `"down"`, and the only thing that
differs in the code is the sign of `s2`; `atan2(s2, c2)` then carries that sign into
$\theta_2$, and the $\theta_1$ formula absorbs it.

There are never three answers, because the law of cosines fixes $\cos\theta_2$ to one
value and a cosine has at most two angles in a full turn. There is one answer, not two,
only on the boundary of the annulus, where $\cos\theta_2 = \pm 1$, $\sin\theta_2 = 0$,
and the two branches meet.

## The mistake that raises

The clamp on `c2` in the code above looks like paranoia. It is not. Take a pose on the
outer boundary, feed it through `forward`, and hand the point back:

```python
# raises ValueError
import math

x = math.cos(math.radians(105)) + math.cos(math.radians(105))
y = math.sin(math.radians(105)) + math.sin(math.radians(105))
c2 = (x * x + y * y - 1.0 - 1.0) / 2.0
print(repr(c2))                 # 1.0000000000000004
print(math.sqrt(1.0 - c2 * c2)) # the square root of a negative number
```

The arm is fully stretched, so $\cos\theta_2$ should be exactly 1, and in floating
point it comes out four parts in $10^{16}$ above it. `1 - c2*c2` is then negative and
`math.sqrt` raises. The temptation is to reason that a point produced by the arm must
be reachable, so no guard is needed; the guard is needed precisely because the point is
on the edge. Clamp `c2` into $[-1, 1]$ before the root, and treat the reachability test
with the same tolerance.

The other mistake is quieter. Writing $\theta_1$ with `atan(y / x)` instead of
`atan2(y, x)` gives the right answer for every target in the right half-plane and an
answer $180^\circ$ off for every target in the left. It is tempting because the two
functions agree on every example anyone tries first.

## Velocities: the Jacobian

Positions are half the story. A controller commands joint *rates*, and wants to know
what tip velocity results. Differentiate the forward kinematics with respect to time,
using the chain rule on each term:

$$\dot{x} = -l_1\sin\theta_1\,\dot\theta_1 - l_2\sin(\theta_1+\theta_2)(\dot\theta_1 +
\dot\theta_2), \qquad
\dot{y} = l_1\cos\theta_1\,\dot\theta_1 + l_2\cos(\theta_1+\theta_2)(\dot\theta_1 +
\dot\theta_2).$$

Collect the coefficients of $\dot\theta_1$ and $\dot\theta_2$ into a matrix and the
relation is $\dot{\mathbf p} = J\dot{\boldsymbol\theta}$ with

$$J = \begin{pmatrix} -l_1 s_1 - l_2 s_{12} & -l_2 s_{12} \\ l_1 c_1 + l_2 c_{12} &
l_2 c_{12} \end{pmatrix},$$

writing $s_{12}$ for $\sin(\theta_1 + \theta_2)$ and so on. Its determinant is worth
expanding by hand once, because the answer collapses. The two $l_2^2 s_{12} c_{12}$
terms cancel and what is left is $l_1 l_2 (s_{12} c_1 - c_{12} s_1) = l_1 l_2
\sin\theta_2$, by the angle-difference identity. At the pose $(0, \pi/2)$ with unit
links, $J = \begin{pmatrix} -1 & -1 \\ 1 & 0 \end{pmatrix}$ and $\det J = 1$.

## Singularities are where the answer gets huge

$\det J = l_1 l_2 \sin\theta_2$ is zero at $\theta_2 = 0$ and $\theta_2 = \pi$: the arm
stretched straight and the arm folded double. At those poses $J$ cannot be inverted,
which means there is a tip velocity no joint rates can produce — pushing the tip
further out when the arm is already straight. Near those poses the inverse exists but
the rates it asks for climb without limit:

```python
import math


def jacobian(t1, t2, l1=1.0, l2=1.0):
    s1, c1 = math.sin(t1), math.cos(t1)
    s12, c12 = math.sin(t1 + t2), math.cos(t1 + t2)
    return ((-l1 * s1 - l2 * s12, -l2 * s12),
            (l1 * c1 + l2 * c12, l2 * c12))


def rates_for(J, vx, vy):
    (a, b), (c, d) = J
    det = a * d - b * c
    return ((d * vx - b * vy) / det, (-c * vx + a * vy) / det)


for t2 in (math.pi / 2, 0.5, 0.1, 0.01):
    J = jacobian(0.0, t2)
    det = J[0][0] * J[1][1] - J[0][1] * J[1][0]
    q1, q2 = rates_for(J, 0.1, 0.0)
    print(round(t2, 2), "det", round(det, 4), "rates", round(q1, 3), round(q2, 3))
```

The tip is asked to move at 0.1 m/s along x in every case. At $\theta_2 = \pi/2$ the
rates are 0 and −0.1 rad/s. At $\theta_2 = 0.01$ they are 10 and −20 rad/s: two
hundred times larger, for the same tip motion, with the two joints fighting each other
in opposite directions. $|\det J|$ is the *manipulability*, and this is why it is worth
computing as a number rather than checking for zero: a pose with manipulability 0.01 is
not singular, but it is a pose you do not want to be commanding fine motion from.

## Where it stops holding

Everything above is planar and has two joints, which is exactly why it has a closed
form. A six-joint industrial arm has an analytic inverse only when its geometry is
special — three wrist axes meeting at a point is the usual condition — and a
seven-joint arm has infinitely many inverses for most targets, so a numerical scheme
built on the Jacobian takes over from the law of cosines. Joint limits, which this
model ignores, often remove one elbow branch in practice. And nothing here knows about
gravity, inertia or motor torque: this is the geometry of the arm, not its dynamics.

## What you are about to build

The lab *Forward and inverse kinematics of a 2R arm* asks for five functions:
`forward`, `reachable` with the tolerance discussed above, `inverse` with both elbow
branches and a `ValueError` for an unreachable target, `jacobian` as two row tuples,
and `manipulability` as the absolute determinant. Its tests run `inverse` and
`forward` back to back over a 13-by-13 lattice of poses with links of 1.3 and 0.7,
which is where the clamp earns its keep, and check that the determinant you compute
from the matrix agrees with $l_1 l_2 |\sin\theta_2|$ to twelve decimals.
''',
                },
            ],
            "quiz": {
                "title": "Reaching, and failing to reach, with two joints",
                "minutes": 8,
                "questions": [
                    {
                        "q": "An arm has links of 2.0 and 1.0. Which target is *unreachable*, and why?",
                        "opts": [
                            "(0.5, 0) — it lies inside the hole of radius $|l_1 - l_2| = 1$ the arm cannot fold into",
                            "(3, 0) — the arm can reach the outer edge of its workspace only with the elbow bent, never straight",
                            "(−2, 0) — negative coordinates lie behind the shoulder, outside the annulus",
                            "(1, 0) — the inverse kinematics has a division by zero at the inner edge",
                        ],
                        "a": 0,
                        "whys": [
                            r"Fold the forearm back along the upper arm and the tip sits at 2 − 1 = 1 from the shoulder; nothing brings it closer. A point at $r = 0.5$ is inside that hole.",
                            r"(3, 0) is at $r = 3 = l_1 + l_2$, reachable with the arm dead straight — a bent elbow is what brings the tip *closer*, not further.",
                            r"The annulus is centred on the shoulder and has no favoured direction. (−2, 0) is at $r = 2$, comfortably between 1 and 3, reached by pointing the whole arm left.",
                            r"$r = 1$ is exactly the inner edge, where $\cos\theta_2 = -1$ and the arm is folded double. The formulas evaluate fine there; the only division is by $2 l_1 l_2$.",
                        ],
                        "why": r"""
The reachable set is the annulus $|l_1 - l_2| \le r \le l_1 + l_2$, here $1 \le r
\le 3$. Which direction the target lies in never matters, because the shoulder can
turn a full circle. The hole in the middle is the surprise: an arm with unequal links
cannot touch its own shoulder, or anything within $|l_1 - l_2|$ of it, because the
forearm folded straight back still leaves the tip $l_1 - l_2$ away.
""",
                    },
                    {
                        "q": "The law of cosines gives $\\cos\\theta_2$ for a target inside the workspace. Why does the inverse then have exactly two solutions?",
                        "opts": [
                            "The square root that recovers $\\sin\\theta_2$ has two signs, and each sign is a real elbow configuration",
                            "$\\theta_1$ can be measured from either the x-axis or the y-axis, and each convention gives a solution",
                            "The shoulder can turn either clockwise or anticlockwise to reach the same direction, and each way of turning counts",
                            "A cosine repeats every $2\\pi$, so $\\theta_2$ and $\\theta_2 + 2\\pi$ are distinct solutions",
                        ],
                        "a": 0,
                        "whys": [
                            r"One value of the cosine, two angles with that cosine: the elbow bent one way or the other, mirror images across the shoulder-to-tip line.",
                            r"A convention for measuring an angle does not create a second physical pose. Whatever axis you measure from, the arm is in one of two shapes.",
                            r"The direction of rotation is a story about how the joint got there, not where it is. A shoulder at $9^\circ$ is one pose however it was reached.",
                            r"$\theta_2 + 2\pi$ is the same angle, and puts every link in the same place. Adding a full turn does not give a different configuration of the arm.",
                        ],
                        "why": r"""
The law of cosines pins $\cos\theta_2$ to one number, and a cosine has two angles per
turn: $\theta_2$ and $-\theta_2$. The sign is the sign of $\sin\theta_2$, which is
exactly what the square root discards. Physically the two are the elbow-up and
elbow-down poses, reflections of the same triangle. There is one solution rather than
two only on the boundary of the annulus, where $\sin\theta_2 = 0$ and the branches
coincide.
""",
                    },
                    {
                        "q": "Reading `inverse` code, you see `c2 = max(-1.0, min(1.0, c2))` before the square root. What is that line for?",
                        "opts": [
                            "It rejects unreachable targets by folding their cosine back into the valid range, so that the function never has to raise",
                            "It keeps a boundary target, which rounding can push to $\\cos\\theta_2$ a hair above 1, from making the square root fail",
                            "It selects the elbow branch, since values above 1 correspond to elbow-up and below −1 to elbow-down",
                            "It is a speed optimisation, avoiding a slow trigonometric call when the elbow is nearly straight",
                        ],
                        "a": 1,
                        "whys": [
                            r"Silencing unreachable targets is the *danger* of that line if reachability is not checked first — a target at $r = 2.5$ would quietly be reported as the stretched pose. The lab checks reachability separately, before the clamp, for that reason.",
                            r"A point on the edge of the workspace can arrive with $\cos\theta_2 = 1.0000000000000004$, and $\sqrt{1 - c_2^2}$ of that is the root of a negative number.",
                            r"The branch is chosen by the sign of $\sin\theta_2$, after the root. A cosine above 1 or below −1 is not a configuration of anything; it is rounding noise.",
                            r"No trigonometric call is skipped: `atan2` runs either way. The clamp costs two comparisons and exists for correctness on the boundary, not for speed.",
                        ],
                        "why": r"""
On the boundary of the annulus $\cos\theta_2$ is exactly $\pm 1$ in exact arithmetic
and often $\pm 1$ plus a few ulps in floating point. The very next line takes
$\sqrt{1 - c_2^2}$, which is undefined for $|c_2| > 1$ and raises `ValueError`. The
clamp lets a pose the arm itself produced be inverted. It is not a substitute for the
reachability test, which must run first: a genuinely unreachable target would
otherwise be clamped into a wrong but plausible answer.
""",
                    },
                    {
                        "q": "For the 2R arm, $\\det J = l_1 l_2 \\sin\\theta_2$. What does a determinant of exactly zero mean for the controller?",
                        "opts": [
                            "The tip is at rest, since zero determinant means zero tip velocity for any joint rates",
                            "The arm is at the workspace boundary and both elbow branches give the same joint angles",
                            "There is a tip velocity no joint rates can produce, so some motions cannot be commanded from this pose",
                            "The forward kinematics is undefined at this pose, and the tip position cannot be computed until the joints move away",
                        ],
                        "a": 2,
                        "whys": [
                            r"Joint rates still move the tip — swinging the shoulder sweeps the straight arm round in an arc. What is lost is one *direction* of tip motion, not all motion.",
                            r"Half right: $\sin\theta_2 = 0$ does put the arm on the boundary and does merge the branches. But the question asks what it means for control, and the answer is about which velocities $J$ can produce.",
                            r"A singular matrix maps the two joint rates onto a line in the plane; the perpendicular direction, radially outward when stretched, is unreachable at any rate.",
                            r"Forward kinematics is two sums of sines and cosines and is defined everywhere. It is the *inverse* of the Jacobian that fails, not the position map.",
                        ],
                        "why": r"""
$J$ maps joint rates to tip velocity. When its determinant is zero its two columns are
parallel, so every achievable tip velocity lies along one line and the perpendicular
direction is unreachable however fast the joints turn. Stretched straight, that
missing direction is radially outward. Near the singularity the inverse exists but
demands enormous rates, which is why the lab measures $|\det J|$ as a continuous
manipulability score rather than testing it for zero.
""",
                    },
                    {
                        "q": "A colleague computes $\\theta_1$ as `atan(y / x) - atan2(l2*s2, l1 + l2*c2)`. Every test target they tried works. What will go wrong?",
                        "opts": [
                            "Targets with $x < 0$ come back $180^\\circ$ off, because `atan` cannot tell $(-1, -1)$ from $(1, 1)$",
                            "Targets with $y = 0$ come back as `nan`, because the division inside `atan` is undefined when the numerator is zero",
                            "Nothing: `atan(y / x)` and `atan2(y, x)` are the same function written two ways",
                            "The elbow-down branch is lost, because `atan` always returns a positive angle",
                        ],
                        "a": 0,
                        "whys": [
                            r"$y/x$ is the same number for $(1, 1)$ and $(-1, -1)$, so `atan` gives $45^\circ$ for both. The second target is at $225^\circ$, and the arm reaches for the wrong side of the bench.",
                            r"$y = 0$ makes $y/x$ zero, not undefined, and `atan(0)` is 0. The division fails only at $x = 0$, and even there the real defect is the lost quadrant, not a `nan`.",
                            r"They agree on the right half-plane, which is where every first example lives. `atan2` takes two arguments precisely so that it can recover the quadrant the ratio destroys.",
                            r"The branch lives in the sign of `s2`, which is still there. `atan` returns angles in $(-\pi/2, \pi/2)$, negative included; what it cannot do is reach the left half-plane.",
                        ],
                        "why": r"""
`atan` sees only the ratio $y/x$ and returns an angle between $-90^\circ$ and
$90^\circ$; `atan2` sees $x$ and $y$ separately and returns the full-circle direction.
The two agree whenever $x > 0$, which is why testing with a few targets in front of the
arm never catches it. The first target behind the shoulder gets a $\theta_1$ off by
$180^\circ$, and `forward` of that pose lands on the mirror-image point.
""",
                    },
                ],
            },
            "lab": {
                "title": "Forward and inverse kinematics of a 2R arm",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
A planar arm has two revolute joints. Link 1 has length `l1` and turns by
`theta1` from the x-axis; link 2 has length `l2` and turns by `theta2`
*relative to link 1*. The tool tip therefore sits at

```text
x = l1*cos(t1) + l2*cos(t1 + t2)
y = l1*sin(t1) + l2*sin(t1 + t2)
```

Implement five functions.

**`forward(t1, t2, l1=1.0, l2=1.0)`** — the pair `(x, y)` above.

**`reachable(x, y, l1=1.0, l2=1.0, tol=1e-9)`** — the workspace is the annulus
`|l1 - l2| <= r <= l1 + l2` where `r = hypot(x, y)`. Allow `tol` slack at both
edges so a point produced by `forward` never falls out through rounding.

**`inverse(x, y, l1=1.0, l2=1.0, elbow="up")`** — the analytic solution. From
the law of cosines,

```text
c2 = (x*x + y*y - l1*l1 - l2*l2) / (2*l1*l2)
s2 = +sqrt(1 - c2*c2)   for elbow "up",  -sqrt(...) for "down"
t2 = atan2(s2, c2)
t1 = atan2(y, x) - atan2(l2*s2, l1 + l2*c2)
```

Raise `ValueError` for an unreachable target, and `ValueError` for any `elbow`
that is neither `"up"` nor `"down"`. Clamp `c2` into `[-1, 1]` before the square
root — a point on the workspace boundary can land at 1 + 1e-16.

**`jacobian(t1, t2, l1=1.0, l2=1.0)`** — the 2x2 matrix as a tuple of two rows:

```text
[ -l1*sin(t1) - l2*sin(t1+t2)   -l2*sin(t1+t2) ]
[  l1*cos(t1) + l2*cos(t1+t2)    l2*cos(t1+t2) ]
```

**`manipulability(t1, t2, l1=1.0, l2=1.0)`** — `abs(det J)`. Work it out from
the matrix you just built; it should agree with `l1*l2*abs(sin(t2))`.

Worked values to check yourself against:

```text
forward(0, 0)                  -> (2.0, 0.0)
forward(0, pi/2)               -> (1.0, 1.0)
inverse(1, 1, elbow="up")      -> (0.0, pi/2)
inverse(1, 1, elbow="down")    -> (pi/2, -pi/2)
manipulability(0, 0)           -> 0.0        (fully stretched: singular)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def forward(t1, t2, l1=1.0, l2=1.0):
    """(x, y) of the tool tip for joint angles t1, t2 in radians."""
    # your code here


def reachable(x, y, l1=1.0, l2=1.0, tol=1e-9):
    """True when (x, y) lies in the annulus the arm can touch."""
    # your code here


def inverse(x, y, l1=1.0, l2=1.0, elbow="up"):
    """(t1, t2) reaching (x, y). ValueError if unreachable or elbow is unknown."""
    # your code here


def jacobian(t1, t2, l1=1.0, l2=1.0):
    """The 2x2 manipulator Jacobian, as a tuple of two row tuples."""
    # your code here


def manipulability(t1, t2, l1=1.0, l2=1.0):
    """abs(det J) — zero exactly at a kinematic singularity."""
    # your code here


print("tip at (0, 0):", forward(0.0, 0.0))
print("ik for (1, 1):", inverse(1.0, 1.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def forward(t1, t2, l1=1.0, l2=1.0):
    """(x, y) of the tool tip for joint angles t1, t2 in radians."""
    x = l1 * math.cos(t1) + l2 * math.cos(t1 + t2)
    y = l1 * math.sin(t1) + l2 * math.sin(t1 + t2)
    return (x, y)


def reachable(x, y, l1=1.0, l2=1.0, tol=1e-9):
    """True when (x, y) lies in the annulus the arm can touch."""
    r = math.hypot(x, y)
    return abs(l1 - l2) - tol <= r <= l1 + l2 + tol


def inverse(x, y, l1=1.0, l2=1.0, elbow="up"):
    """(t1, t2) reaching (x, y). ValueError if unreachable or elbow is unknown."""
    if elbow not in ("up", "down"):
        raise ValueError(f"elbow must be 'up' or 'down', got {elbow!r}")
    if not reachable(x, y, l1, l2):
        raise ValueError(f"({x}, {y}) is outside the workspace of a {l1}/{l2} arm")
    c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)
    c2 = max(-1.0, min(1.0, c2))
    s2 = math.sqrt(1.0 - c2 * c2)
    if elbow == "down":
        s2 = -s2
    t2 = math.atan2(s2, c2)
    t1 = math.atan2(y, x) - math.atan2(l2 * s2, l1 + l2 * c2)
    return (t1, t2)


def jacobian(t1, t2, l1=1.0, l2=1.0):
    """The 2x2 manipulator Jacobian, as a tuple of two row tuples."""
    s1, c1 = math.sin(t1), math.cos(t1)
    s12, c12 = math.sin(t1 + t2), math.cos(t1 + t2)
    return (
        (-l1 * s1 - l2 * s12, -l2 * s12),
        (l1 * c1 + l2 * c12, l2 * c12),
    )


def manipulability(t1, t2, l1=1.0, l2=1.0):
    """abs(det J) — zero exactly at a kinematic singularity."""
    (a, b), (c, d) = jacobian(t1, t2, l1, l2)
    return abs(a * d - b * c)


print("tip at (0, 0):", forward(0.0, 0.0))
print("ik for (1, 1):", inverse(1.0, 1.0))
'''}],
                "hints": [
                    "`forward` is two cosines and two sines — note the second link uses the *sum* `t1 + t2`.",
                    "Validate `elbow` before you validate reachability, so a typo is reported as a typo.",
                    "The elbow branch is only the sign of `s2`; `t2 = atan2(s2, c2)` then carries that sign.",
                    "det of `((a, b), (c, d))` is `a*d - b*c`; expand it symbolically and the arm's `l1*l2*sin(t2)` falls out.",
                ],
                "tests": [
                    {"name": "forward kinematics at known poses", "code": r'''
import math
_got = forward(0.0, 0.0)
assert abs(_got[0] - 2.0) < 1e-12 and abs(_got[1]) < 1e-12, f"forward(0,0) gave {_got!r}, expected (2.0, 0.0)"
_got = forward(0.0, math.pi / 2)
assert abs(_got[0] - 1.0) < 1e-12 and abs(_got[1] - 1.0) < 1e-12, f"forward(0,pi/2) gave {_got!r}, expected (1.0, 1.0)"
_got = forward(math.pi / 2, math.pi / 2, 2.0, 1.0)
assert abs(_got[0] + 1.0) < 1e-12 and abs(_got[1] - 2.0) < 1e-12, f"forward(pi/2,pi/2,2,1) gave {_got!r}, expected (-1.0, 2.0)"
'''},
                    {"name": "the workspace is an annulus", "code": r'''
assert reachable(2.0, 0.0) is True, "the fully stretched pose (2, 0) is reachable with l1 = l2 = 1"
assert reachable(0.0, 0.0) is True, "with equal links the arm can fold back onto the origin"
assert reachable(2.5, 0.0) is False, "r = 2.5 is beyond l1 + l2 = 2"
assert reachable(0.5, 0.0, 2.0, 1.0) is False, "r = 0.5 is inside the hole of radius |2 - 1| = 1"
assert reachable(1.0, 0.0, 2.0, 1.0) is True, "r = 1.0 is exactly the inner edge of the annulus"
'''},
                    {"name": "inverse kinematics: both elbow branches", "code": r'''
import math
_up = inverse(1.0, 1.0)
assert abs(_up[0]) < 1e-12 and abs(_up[1] - math.pi / 2) < 1e-12, f"inverse(1,1,elbow='up') gave {_up!r}, expected (0.0, pi/2)"
_dn = inverse(1.0, 1.0, elbow="down")
assert abs(_dn[0] - math.pi / 2) < 1e-12 and abs(_dn[1] + math.pi / 2) < 1e-12, f"inverse(1,1,elbow='down') gave {_dn!r}, expected (pi/2, -pi/2)"
assert _up[1] > 0 > _dn[1], f"the two branches must differ in the sign of t2, got {_up[1]!r} and {_dn[1]!r}"
'''},
                    {"name": "inverse undoes forward across the workspace", "code": r'''
import math
_worst = 0.0
for _i in range(-6, 7):
    for _j in range(-6, 7):
        _t1 = _i * math.pi / 6.0
        _t2 = _j * math.pi / 6.0
        _x, _y = forward(_t1, _t2, 1.3, 0.7)
        for _branch in ("up", "down"):
            _a, _b = inverse(_x, _y, 1.3, 0.7, _branch)
            _rx, _ry = forward(_a, _b, 1.3, 0.7)
            _worst = max(_worst, abs(_rx - _x), abs(_ry - _y))
assert _worst < 1e-9, f"forward(inverse(p)) drifted from p by {_worst!r}, expected under 1e-9"
'''},
                    {"name": "inverse refuses the impossible", "code": r'''
try:
    inverse(2.5, 0.0)
    assert False, "inverse(2.5, 0.0) is outside the workspace and must raise ValueError"
except ValueError:
    pass
try:
    inverse(0.5, 0.0, 2.0, 1.0)
    assert False, "inverse(0.5, 0.0, 2, 1) is inside the workspace hole and must raise ValueError"
except ValueError:
    pass
try:
    inverse(1.0, 1.0, elbow="sideways")
    assert False, "an unknown elbow branch must raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "the Jacobian and its determinant", "code": r'''
import math
_j = jacobian(0.0, math.pi / 2)
assert len(_j) == 2 and len(_j[0]) == 2, f"jacobian should be 2 rows of 2, got {_j!r}"
_want = ((-1.0, -1.0), (1.0, 0.0))
for _r in range(2):
    for _c in range(2):
        assert abs(_j[_r][_c] - _want[_r][_c]) < 1e-12, f"jacobian(0, pi/2)[{_r}][{_c}] is {_j[_r][_c]!r}, expected {_want[_r][_c]}"
for _t1 in (0.0, 0.4, -1.1):
    for _t2 in (0.3, 1.0, -2.0, 2.9):
        _m = manipulability(_t1, _t2, 1.3, 0.7)
        _want_m = 1.3 * 0.7 * abs(math.sin(_t2))
        assert abs(_m - _want_m) < 1e-12, f"manipulability({_t1},{_t2},1.3,0.7) is {_m!r}, expected {_want_m!r}"
'''},
                    {"name": "singular fully stretched and fully folded", "code": r'''
import math
assert manipulability(0.7, 0.0) < 1e-12, f"t2 = 0 is the stretched singularity, got {manipulability(0.7, 0.0)!r}"
assert manipulability(0.7, math.pi) < 1e-12, f"t2 = pi is the folded singularity, got {manipulability(0.7, math.pi)!r}"
assert manipulability(0.7, math.pi / 2) > 0.9, f"t2 = pi/2 is the best-conditioned pose, got {manipulability(0.7, math.pi / 2)!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "State estimation under noise",
            "summary": "Kalman recursion for linear-Gaussian problems, particles for the rest.",
            "concepts": [
                "Belief as a distribution, not a point; estimation is Bayes' rule applied recursively",
                "The Kalman predict step grows covariance by the process noise Q",
                "The update step shrinks it: the gain K trades prior variance against measurement variance R",
                "With no process noise, information adds — the posterior variance falls as 1/n",
                "A constant-velocity model estimates a state that is never directly measured",
                "Particle filters represent an arbitrary posterior by weighted samples",
                "Systematic resampling and the effective sample size 1/sum(w^2) fight particle depletion",
            ],
            "read": [
                {
                    "title": "Believing a noisy sensor by exactly the right amount",
                    "minutes": 15,
                    "body": r'''
A robot is stopped in a corridor and has two rangefinders pointed at the same wall. The
cheap one says the wall is 3.0 m away, and its datasheet gives it a standard deviation
of 0.4 m. The better one says 3.5 m, with a standard deviation of 0.2 m. Where is the
wall? Not at 3.25 m, the plain average: that treats the two sensors as equally
trustworthy, and one of them is four times noisier in variance than the other. Not at
3.5 m either, because throwing the cheap sensor away wastes real information. The
answer is in between, closer to the good sensor, and the whole of this module is
working out exactly how much closer, and then doing it again every tenth of a second
as the robot drives.

## Two readings, one belief

Call the readings $x_a = 3.0$ with variance $p_a = 0.16$ and $x_b = 3.5$ with variance
$p_b = 0.04$. Take a weighted average, $\hat x = w x_a + (1-w) x_b$, and ask what $w$
makes the result least uncertain. The variance of the weighted sum, for independent
errors, is $w^2 p_a + (1-w)^2 p_b$. Differentiate with respect to $w$ and set to zero:
$2 w p_a - 2(1-w) p_b = 0$, so $w = p_b / (p_a + p_b)$. Each reading is weighted by the
*other* one's variance, which is the same as weighting each by its own precision $1/p$.

With the numbers: $w = 0.04/0.20 = 0.2$ on the cheap sensor, $0.8$ on the good one, and
$\hat x = 0.2 \times 3.0 + 0.8 \times 3.5 = 3.4$ m. Rewrite that as $\hat x = x_a +
K(x_b - x_a)$ with $K = p_a/(p_a + p_b) = 0.8$: start from one reading and move a
fraction $K$ of the way toward the other. Substitute $w$ back into the variance and it
comes to $p_a p_b/(p_a + p_b) = 0.032$, or in precision terms $1/0.032 = 31.25 = 1/0.16
+ 1/0.04$. Precisions add. A second reading, however bad, can only sharpen a belief.

```python
xa, pa = 3.0, 0.16
xb, pb = 3.5, 0.04
K = pa / (pa + pb)
fused = xa + K * (xb - xa)
var = (1.0 - K) * pa
print("K", round(K, 4), "fused", round(fused, 4), "variance", round(var, 4))
```

This prints `K 0.8 fused 3.4 variance 0.032`. That line, $K = p/(p + r)$, $x
\leftarrow x + K(z - x)$, $p \leftarrow (1-K)p$, is the Kalman update. Everything else
is bookkeeping.

## Doing it again, and again

Now treat the first reading as a *prior* belief $(x, p)$ and every later reading $z$
with variance $r$ as a new sensor. The same three lines apply each time. Start with
$x_0 = 0$, $p_0 = 1$ and feed in readings of $1.0$ with $r = 1$:

```python
x, p = 0.0, 1.0
for n, z in enumerate([1.0, 1.0, 1.0, 1.0], 1):
    K = p / (p + 1.0)
    x = x + K * (z - x)
    p = (1.0 - K) * p
    print(n, round(x, 4), round(p, 4))
```

The variances print as 0.5, 0.3333, 0.25, 0.2 and the means as 0.5, 0.6667, 0.75, 0.8.
Both follow from precisions adding: after $n$ readings the precision is $1/p_0 + n/r =
1 + n$, so $p_n = 1/(n+1)$, and the mean is the precision-weighted average of the prior
0 and the $n$ readings of 1, which is $n/(n+1)$. This is the lab's `kalman_1d` with `q =
0`, and its first test checks these exact fractions.

## Motion adds doubt

Between readings the robot drives. If it commands a displacement $u$, the belief's mean
moves by $u$ and its variance grows by $q$, the variance of how far it *actually* moved
given that command: $x \leftarrow x + u$, $p \leftarrow p + q$. That is the predict step,
and it is the reason the variance in a real filter never reaches zero. With $q > 0$
each cycle adds $q$ and each update removes some; the two balance at a steady-state
variance that depends on $q$ and $r$ together. The lab's test that "process noise $q >
0$ must leave more residual variance than $q = 0$" is checking exactly that balance.

## Several numbers at once

A state is rarely one number. Stack them into a vector $\mathbf x$ with covariance
matrix $P$, and let the motion be linear, $\mathbf x \leftarrow F\mathbf x$. The
covariance of a linear map of a random vector is $F P F^\top$ — the same rule as $\text{Var}(a
X) = a^2 \text{Var}(X)$, written for matrices — so predict becomes

$$\mathbf x \leftarrow F\mathbf x, \qquad P \leftarrow F P F^\top + Q.$$

For one scalar measurement $z = H\mathbf x + \text{noise}$, with $H$ a row vector picking
out what the sensor sees, the same derivation as the corridor gives

$$S = H P H^\top + r, \qquad K = P H^\top / S, \qquad \mathbf x \leftarrow \mathbf x +
K(z - H\mathbf x), \qquad P \leftarrow P - K H P.$$

Set every matrix to $1 \times 1$ and $H = 1$ and these are the three lines from the
corridor: $S = p + r$, $K = p/(p+r)$, $P \leftarrow p - Kp$.

## The velocity you never measured

Here is where the matrix form earns its keep. Track a robot with state $[\text{position},
\text{velocity}]$ under a constant-velocity model: $F = \begin{pmatrix} 1 & \Delta t \\
0 & 1 \end{pmatrix}$. Only the position is measured, so $H = (1, 0)$. Start from $P =
I$, take $\Delta t = 0.5$ and $Q = 0.1 I$, and run one predict:

$$F P F^\top = \begin{pmatrix} 1 + \Delta t^2 & \Delta t \\ \Delta t & 1 \end{pmatrix} =
\begin{pmatrix} 1.25 & 0.5 \\ 0.5 & 1 \end{pmatrix}, \qquad P = \begin{pmatrix} 1.35 & 0.5
\\ 0.5 & 1.1 \end{pmatrix}.$$

An off-diagonal 0.5 has appeared from nothing. It says position and velocity are now
correlated: if the position turns out further along than expected, the velocity was
probably higher than expected too. Now update with a position reading, $r = 1$:

```python
P = [[1.35, 0.5], [0.5, 1.1]]
H = [1.0, 0.0]
r = 1.0
PHt = [sum(P[i][j] * H[j] for j in range(2)) for i in range(2)]
S = sum(H[i] * PHt[i] for i in range(2)) + r
K = [PHt[i] / S for i in range(2)]
P_new = [[P[i][j] - K[i] * PHt[j] for j in range(2)] for i in range(2)]
print("K", [round(k, 4) for k in K])
print("position variance", round(P_new[0][0], 4))
print("velocity variance", round(P_new[1][1], 4))
```

The gain prints as `[0.5745, 0.2128]`: the position reading moves the *velocity*
estimate too, by a fifth of the innovation. The position variance falls from 1.35 to
0.5745, and the velocity variance falls from 1.1 to 0.9936 — a quantity no sensor ever
looked at has become more certain, purely because the motion model tied it to one that
was. The lab's `kalman_cv` runs this for sixty steps and recovers a velocity of 2.0 to
within a tenth from position readings with noise of 0.5.

## When the bell curve is the wrong shape

Everything so far assumed the belief is a Gaussian: one hump, described by a mean and a
variance. Now put the robot in a circular corridor of circumference 20 with landmarks
at 0, 5 and 12, and give it a sensor that reports only its distance to the *nearest*
landmark. A reading of 2.0 is consistent with being at 2, at 3, at 7, at 10, at 14 and
at 18: six places, and no single hump covers them. A Kalman filter would report the
mean of those, somewhere near 9, and be confidently wrong.

A particle filter keeps a crowd of guesses instead. Each particle is a candidate
position with a weight; the update multiplies each weight by how likely the reading
would be from there, $\exp(-\tfrac12 ((z - \text{sensor}(p))/\sigma)^2)$, and
normalises; the predict moves every particle by the command plus its own noise.

```python
import math
import random

rng = random.Random(7)
L, landmarks = 20.0, [0.0, 5.0, 12.0]


def ring(a, b):
    d = abs(a - b) % L
    return min(d, L - d)


def sensor(x):
    return min(ring(x, m) for m in landmarks)


n = 2000
particles = [rng.uniform(0.0, L) for _ in range(n)]
weights = [1.0 / n] * n


def update(z, sigma):
    global weights
    raw = [w * math.exp(-0.5 * ((z - sensor(p)) / sigma) ** 2) + 1e-300
           for p, w in zip(particles, weights)]
    total = sum(raw)
    weights = [w / total for w in raw]


def crowded():
    mass = [0.0] * 20
    for p, w in zip(particles, weights):
        mass[int(p)] += w
    return [i for i, m in enumerate(mass) if m > 0.05]


update(2.0, 0.3)
print("after z=2:", crowded(), "ESS", round(1.0 / sum(w * w for w in weights)))
particles = [(p + 3.0 + rng.gauss(0.0, 0.1)) % L for p in particles]
update(1.0, 0.3)
print("after moving 3 and z=1:", crowded(), "ESS", round(1.0 / sum(w * w for w in weights)))
```

After the first reading the unit-wide bins holding more than 5% of the weight are
`[1, 2, 3, 6, 7, 9, 10, 13, 14, 17, 18]`: the six places, each smeared across two bins.
The robot then drives three units and reads a distance of 1, and the crowd thins to
`[0, 1, 5, 6, 12, 13]`. Three of the six hypotheses were killed by the second reading
and three survived, because a robot starting at 3, at 10 or at 18 would have seen
exactly that sequence. The filter is honestly reporting three-way ambiguity. A
Gaussian would have had to pick one.

## Depletion, and the effective sample size

The ESS printed above falls from about 611 to about 268 out of 2000. It is $1/\sum
w_i^2$: with uniform weights it equals $n$, and with all the weight on one particle it
equals 1. It measures how many particles are doing any work. Left alone, a few
particles come to hold nearly all the weight and the rest are dead cargo, so when the
ESS drops below $n/2$ the filter *resamples*: draws $n$ new particles from the old ones
in proportion to weight and resets every weight to $1/n$. Systematic resampling does
this with one random number: a comb of $n$ evenly spaced teeth, offset by a single
uniform draw, swept once across the cumulative weights.

The mistake here is resampling at every step whether the ESS asks for it or not. It is
tempting because it looks tidier, and it slowly destroys the crowd: each resample
copies some particles and deletes others, and with nothing to replenish diversity the
filter ends up with a few hundred copies of the same three positions. The threshold is
the cure.

There is a second trap, in the estimate itself:

```python
import math

particles = [0.1, 19.9, 0.2, 19.8]
L = 20.0
print("arithmetic mean", sum(particles) / 4)
cx = sum(math.cos(2 * math.pi * p / L) for p in particles) / 4
cy = sum(math.sin(2 * math.pi * p / L) for p in particles) / 4
print("circular mean", round((math.atan2(cy, cx) % (2 * math.pi)) * L / (2 * math.pi), 6))
```

Four particles huddled around the join of the ring average, arithmetically, to 10.0 —
the far side of the corridor. Average their unit vectors instead and the circular mean
prints as 0.0 to six decimals. The lab's `estimate` must do the second thing, and one
of its tests places particles on both sides of the wrap to make sure.

## Where it stops holding

The Kalman filter is optimal when the motion and the sensor are linear and the noise is
Gaussian, and it is a reasonable approximation when they are nearly so: the extended
Kalman filter linearises a curved model around the current estimate and carries on.
It has no way at all to represent two hypotheses, which is what the ring showed. The
particle filter can represent anything, and pays for it in particles: in one dimension
two thousand is lavish, in a six-dimensional pose it is barely enough, and in fifty
dimensions no affordable number of samples covers the space. Between the two sit
most real localisation systems.

## What you are about to build

The lab *Kalman and particle filters* has you write `kf_predict` and `kf_update` on
plain lists of lists, then `kalman_1d` and `kalman_cv` on top of them, with tests that
pin the $1/(n+1)$ variances and the recovered velocity. The second half is the
`ParticleFilter` class on the ring: `sensor`, `predict`, `update`, `ess`, a systematic
`resample`, and the circular `estimate`. The tests seed the generator and specify the
order in which random numbers are drawn, so the draw order in the brief is part of the
contract.
''',
                },
            ],
            "quiz": {
                "title": "How much to believe a reading",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Two sensors read the same wall: 3.0 m with variance 0.16 and 3.5 m with variance 0.04. What estimate is least uncertain?",
                        "opts": [
                            "3.25 m, the average, since each sensor contributes one independent reading",
                            "3.33 m, weighting each by $1/\\sigma$ rather than by $1/\\sigma^2$",
                            "3.4 m, weighting each reading by the inverse of its own variance",
                            "3.5 m, since the better sensor's reading dominates the worse one entirely",
                        ],
                        "a": 2,
                        "whys": [
                            r"The plain average is the right answer only when the variances are equal. Here one sensor is four times noisier in variance, and treating it as an equal costs accuracy.",
                            r"Weights of $1/0.4$ and $1/0.2$ give 3.33, and it feels natural to weight by the number on the datasheet. But minimising the variance of the combination puts the weights at $1/\sigma^2$, not $1/\sigma$.",
                            r"$K = 0.16/(0.16 + 0.04) = 0.8$ of the way from 3.0 toward 3.5 is 3.4, with variance 0.032.",
                            r"Discarding the cheap sensor leaves the variance at 0.04. Folding it in, even at a weight of 0.2, brings the variance down to 0.032: a worse sensor still carries information.",
                        ],
                        "why": r"""
Minimising the variance of $w x_a + (1-w) x_b$ gives $w = p_b/(p_a + p_b)$, so the
weights are proportional to precision, $1/p$. That is 0.2 on the 3.0 m reading and 0.8
on the 3.5 m reading, giving 3.4 m with variance $p_a p_b/(p_a + p_b) = 0.032$, lower
than either sensor alone. Weighting by $1/\sigma$ is the common near-miss; it points
the right way but under-trusts the good sensor.
""",
                    },
                    {
                        "q": "A scalar Kalman filter with $p_0 = 1$, $r = 1$ and no process noise sees readings one after another. Its variance goes $1/2, 1/3, 1/4, \\dots$ Why that sequence?",
                        "opts": [
                            "Each update halves the remaining uncertainty, and the sequence approximates that halving",
                            "Precisions add: each reading contributes $1/r$, so after $n$ readings the precision is $1 + n$",
                            "The variance converges toward $r$, the measurement variance, which is the floor a sensor can reach",
                            "The gain $K$ is fixed at $1/2$, so the variance is scaled by a constant fraction every step",
                        ],
                        "a": 1,
                        "whys": [
                            r"Halving would give $1/2, 1/4, 1/8$. The actual sequence falls much more slowly, because each new reading is worth less against an ever-sharper prior.",
                            r"$1/p_n = 1/p_0 + n/r = 1 + n$, so $p_n = 1/(n+1)$, which is the sequence.",
                            r"The variance passes straight through $r = 1$ on the first step and keeps falling. Repeated readings beat a single sensor's variance; that is the point of averaging.",
                            r"$K = p/(p + r)$ changes every step: $1/2$, then $1/3$, then $1/4$. It shrinks as the prior sharpens, which is exactly why later readings move the estimate less.",
                        ],
                        "why": r"""
The update's variance is $p r/(p + r)$, and in precision form that is $1/p' = 1/p +
1/r$: every reading adds its own precision to the belief's. Starting at precision 1 and
adding 1 per reading gives $1/(n+1)$. With process noise $q > 0$ the predict step would
add back $q$ each cycle and the sequence would level off; with $q = 0$ it runs to zero,
because there is nothing left to be uncertain about.
""",
                    },
                    {
                        "q": "In the constant-velocity tracker only position is measured, yet the velocity estimate converges. What carries the information from position to velocity?",
                        "opts": [
                            "The filter differences consecutive position estimates internally, dividing by $\\Delta t$ to form a velocity",
                            "The measurement row $H$ includes a small velocity component that the sensor picks up",
                            "The predict step's $F P F^\\top$ correlates position with velocity, so a position innovation updates both",
                            "The velocity is assumed constant, so it is known in advance and needs no estimation",
                        ],
                        "a": 2,
                        "whys": [
                            r"No differencing happens anywhere in the recursion. Differencing two noisy positions would give a very noisy velocity; the filter does better than that precisely by not doing it.",
                            r"$H = (1, 0)$: the velocity component is exactly zero. The sensor sees position and nothing else.",
                            r"After one predict $P$ gains an off-diagonal $\Delta t$, and $K = P H^\top/S$ inherits it, so the velocity gets a share of every position surprise.",
                            r"Constant in the *model* means the velocity does not change; it says nothing about what value it has. The whole exercise is finding that value from readings that never mention it.",
                        ],
                        "why": r"""
$F P F^\top$ with $F = \begin{pmatrix} 1 & \Delta t \\ 0 & 1 \end{pmatrix}$ produces an
off-diagonal covariance term, because a position further along than expected is
evidence of a higher velocity. The gain $K = P H^\top / S$ then has a non-zero velocity
row, so each position reading nudges the velocity estimate, and $P - K H P$ shrinks
the velocity variance too. Nothing in the filter ever differences positions.
""",
                    },
                    {
                        "q": "Why does the ring-corridor robot with a nearest-landmark sensor need a particle filter rather than a Kalman filter?",
                        "opts": [
                            "Its motion is nonlinear, and the Kalman filter can only propagate a linear model",
                            "Its posterior has several separated peaks, and a Gaussian can represent only one",
                            "The corridor wraps around, and a Kalman filter has no way to take a modulo",
                            "A particle filter is more accurate than a Kalman filter on every problem, given enough particles",
                        ],
                        "a": 1,
                        "whys": [
                            r"The motion is a plain shift with noise, which is as linear as it gets. Nonlinearity would call for an extended Kalman filter; it is not the problem here.",
                            r"A reading of 2 fits six places on the ring at once. One mean and one variance cannot describe six humps, and their average lands somewhere the robot is not.",
                            r"Wrapping the mean is one line of arithmetic and would not help: the trouble is not the topology but the six-way ambiguity, which survives any wrapping.",
                            r"On a linear-Gaussian problem the Kalman filter is exactly optimal and a particle filter is a noisy approximation of it. Particles win only where the Gaussian shape is wrong.",
                        ],
                        "why": r"""
The nearest-landmark sensor maps many positions to the same reading, so after one
reading the belief is a set of well-separated peaks — multimodal. A Kalman filter's
belief is a single Gaussian, and the best single Gaussian over six peaks is a wide hump
centred between them, which is confidently wrong. Particles represent the peaks
directly, and the second reading in the reading's example prunes six hypotheses to
three rather than to a spurious average.
""",
                    },
                    {
                        "q": "After one update, a filter of 100 particles reports an effective sample size of 8. What does that say, and what should happen next?",
                        "opts": [
                            "The filter has converged: eight particles agree on the position, and the remaining ninety-two can be dropped",
                            "The reading was probably faulty, since a good reading would keep the ESS near 100",
                            "The weight now sits on a handful of particles and the rest carry almost none, so it is time to resample",
                            "92 particles fell outside the sensor's range and were removed, leaving 8 active ones",
                        ],
                        "a": 2,
                        "whys": [
                            r"A low ESS is a statement about *weights*, not about agreement. The eight heavy particles may sit in three different clusters, and dropping the rest by hand is what resampling does properly.",
                            r"A sharp, correct reading is exactly what collapses the ESS: it makes most particles implausible. Faulty readings tend to do the opposite, spreading weight thinly.",
                            r"$1/\sum w^2 = 8$ means the weights behave as if only eight particles were drawn. Resampling redistributes the crowd onto the plausible ones and resets the weights to $1/n$.",
                            r"Nothing is removed by an update; every particle keeps its position and receives a weight, however tiny. The count stays at 100 throughout.",
                        ],
                        "why": r"""
The effective sample size $1/\sum w_i^2$ is 100 with uniform weights and 1 when one
particle holds everything. A value of 8 says the update concentrated nearly all the
weight on a few particles, and the others are dead cargo. The remedy is to resample —
redraw 100 particles in proportion to weight and reset the weights — which the lab does
whenever the ESS falls below half the particle count. Resampling every step regardless
would slowly erase the diversity the filter depends on.
""",
                    },
                    {
                        "q": "Four particles at 0.1, 19.9, 0.2 and 19.8 on a ring of length 20 carry equal weight. What position estimate should the filter report?",
                        "opts": [
                            "10.0, the arithmetic mean of the four positions taken as plain numbers",
                            "About 0, the circular mean, since the particles straddle the join of the ring",
                            "19.9, the median of the four positions once they are sorted",
                            "The estimate is undefined, since the particles are split into two groups on opposite sides of the wrap",
                        ],
                        "a": 1,
                        "whys": [
                            r"10.0 is the far side of the corridor from every particle. The arithmetic mean treats 0.1 and 19.9 as twenty units apart when on the ring they are 0.2 apart.",
                            r"Averaging the unit vectors $(\cos, \sin)$ of $2\pi p/L$ and taking `atan2` gives an angle near 0, which maps back to a position near 0.",
                            r"A median on a ring inherits the same problem as the mean: the sorted order puts 0.1 and 19.9 at opposite ends of the list, though they are neighbours.",
                            r"The particles are one tight group that happens to sit across the point where the coordinate wraps. A ring has no ends, and the group has a perfectly good centre.",
                        ],
                        "why": r"""
On a ring, 0.1 and 19.9 are 0.2 apart, not 19.8. Any estimate that averages the raw
numbers gets the answer 10.0, which is the one place the robot is certainly not. The
circular mean maps each particle to a point on the unit circle, averages those, and
reads the angle back — which gives 0.0 to six decimals here. The lab's `estimate` must
work this way, and one of its tests puts particles on both sides of the join to check.
""",
                    },
                ],
            },
            "lab": {
                "title": "Kalman and particle filters",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
The 2x2 matrix helpers at the top of `main.py` are given. Build on them.

### Part 1 — the linear-Gaussian recursion

**`kf_predict(x, P, F, Q)`** returns `(F x, F P F^T + Q)`, with `x` a list of n
floats and `P`, `F`, `Q` n-by-n lists of lists.

**`kf_update(x, P, z, H, r)`** folds in one *scalar* measurement `z` with row
vector `H` (a list of n floats) and variance `r`:

```text
S = H P H^T + r          (a scalar)
K = P H^T / S            (an n-vector)
x' = x + K (z - H x)
P' = P - K (H P)
```

**`kalman_1d(measurements, x0, p0, q, r)`** — the n = 1 special case. Return a
list of `(x, p)` posteriors, one per measurement. With `q = 0`, `p0 = 1`,
`r = 1` the variances must come out exactly `1/2, 1/3, 1/4, ...`: information
adds, so after n readings the variance is `1 / (1/p0 + n/r)`.

**`kalman_cv(measurements, dt, q, r, x0, p0)`** — a constant-velocity tracker.
State is `[position, velocity]`, `F = [[1, dt], [0, 1]]`, `Q = q*I`, and only
the position is measured, so `H = [1, 0]`. Return a list of
`((x, v), ((p00, p01), (p10, p11)))`. Velocity is never measured yet is
estimated well — that is the whole point of the model.

### Part 2 — when Gaussian is the wrong shape

A robot drives round a circular corridor of circumference `length`. It only
ever reports its distance to the *nearest* landmark, so the same reading fits
several places at once: the posterior is multimodal and no Gaussian describes
it. Complete `ParticleFilter`:

- `ring_distance(a, b, length)` — shortest way round, so `ring_distance(1, 19, 20)` is `2.0`
- `sensor(x)` — `min` ring distance from `x` to any landmark
- `predict(u, sigma_u)` — move every particle by `u` plus `rng.gauss(0, sigma_u)`, modulo `length`
- `update(z, sigma_z)` — multiply each weight by `exp(-0.5*((z - sensor(p))/sigma_z)**2)`, add `1e-300` to keep it non-zero, then normalise so the weights sum to 1
- `ess()` — `1 / sum(w*w)`
- `resample()` — systematic resampling from one uniform draw `rng.random()/n`, then reset the weights to `1/n`
- `estimate()` — the *circular* weighted mean: average the unit vectors `(cos, sin)` of `2*pi*p/length`, take `atan2`, map back. A plain arithmetic mean of particles at 0.1 and 19.9 would answer 10.0, which is as wrong as an answer can be.

Draw every random number from `self.rng` in the order given: the tests pin a seed.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


# ---- given: small dense-matrix helpers -------------------------------------
def mat_vec(A, v):
    """A @ v for a matrix of lists and a vector of floats."""
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]


def mat_mul(A, B):
    """A @ B."""
    n, k, m = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]


def mat_t(A):
    """Transpose."""
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def mat_add(A, B):
    """Elementwise sum."""
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


# ---- your work -------------------------------------------------------------
def kf_predict(x, P, F, Q):
    """Propagate the belief through the motion model. Returns (x, P)."""
    # your code here


def kf_update(x, P, z, H, r):
    """Fold in one scalar measurement z. Returns (x, P)."""
    # your code here


def kalman_1d(measurements, x0, p0, q, r):
    """List of (x, p) posteriors for a scalar random walk."""
    # your code here


def kalman_cv(measurements, dt, q, r, x0=(0.0, 0.0), p0=((1.0, 0.0), (0.0, 1.0))):
    """List of ((x, v), ((p00, p01), (p10, p11))) for a constant-velocity model."""
    # your code here


def ring_distance(a, b, length):
    """Shortest distance between a and b around a loop of circumference length."""
    # your code here


class ParticleFilter:
    def __init__(self, n, length, landmarks, seed=7):
        self.rng = random.Random(seed)
        self.length = float(length)
        self.landmarks = [float(m) for m in landmarks]
        self.particles = [self.rng.uniform(0.0, self.length) for _ in range(n)]
        self.weights = [1.0 / n] * n

    def sensor(self, x):
        """Distance from x to the nearest landmark, measured round the loop."""
        # your code here

    def predict(self, u, sigma_u):
        """Push every particle through the noisy motion model."""
        # your code here

    def update(self, z, sigma_z):
        """Reweight by the Gaussian likelihood of z, then normalise."""
        # your code here

    def ess(self):
        """Effective sample size 1 / sum(w^2)."""
        # your code here

    def resample(self):
        """Systematic resampling; weights become uniform again."""
        # your code here

    def estimate(self):
        """Circular weighted mean of the particles."""
        # your code here


print("1d variances:", [round(p, 4) for _, p in kalman_1d([1.0] * 4, 0.0, 1.0, 0.0, 1.0)])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


# ---- given: small dense-matrix helpers -------------------------------------
def mat_vec(A, v):
    """A @ v for a matrix of lists and a vector of floats."""
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]


def mat_mul(A, B):
    """A @ B."""
    n, k, m = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]


def mat_t(A):
    """Transpose."""
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def mat_add(A, B):
    """Elementwise sum."""
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


# ---- your work -------------------------------------------------------------
def kf_predict(x, P, F, Q):
    """Propagate the belief through the motion model. Returns (x, P)."""
    return mat_vec(F, x), mat_add(mat_mul(mat_mul(F, P), mat_t(F)), Q)


def kf_update(x, P, z, H, r):
    """Fold in one scalar measurement z. Returns (x, P)."""
    n = len(x)
    PHt = [sum(P[i][j] * H[j] for j in range(n)) for i in range(n)]
    s = sum(H[i] * PHt[i] for i in range(n)) + r
    K = [PHt[i] / s for i in range(n)]
    innovation = z - sum(H[i] * x[i] for i in range(n))
    x_new = [x[i] + K[i] * innovation for i in range(n)]
    P_new = [[P[i][j] - K[i] * PHt[j] for j in range(n)] for i in range(n)]
    return x_new, P_new


def kalman_1d(measurements, x0, p0, q, r):
    """List of (x, p) posteriors for a scalar random walk."""
    x, P = [float(x0)], [[float(p0)]]
    out = []
    for z in measurements:
        x, P = kf_predict(x, P, [[1.0]], [[float(q)]])
        x, P = kf_update(x, P, float(z), [1.0], float(r))
        out.append((x[0], P[0][0]))
    return out


def kalman_cv(measurements, dt, q, r, x0=(0.0, 0.0), p0=((1.0, 0.0), (0.0, 1.0))):
    """List of ((x, v), ((p00, p01), (p10, p11))) for a constant-velocity model."""
    x = [float(x0[0]), float(x0[1])]
    P = [[float(p0[0][0]), float(p0[0][1])], [float(p0[1][0]), float(p0[1][1])]]
    F = [[1.0, float(dt)], [0.0, 1.0]]
    Q = [[float(q), 0.0], [0.0, float(q)]]
    out = []
    for z in measurements:
        x, P = kf_predict(x, P, F, Q)
        x, P = kf_update(x, P, float(z), [1.0, 0.0], float(r))
        out.append(((x[0], x[1]), ((P[0][0], P[0][1]), (P[1][0], P[1][1]))))
    return out


def ring_distance(a, b, length):
    """Shortest distance between a and b around a loop of circumference length."""
    d = abs(a - b) % length
    return min(d, length - d)


class ParticleFilter:
    def __init__(self, n, length, landmarks, seed=7):
        self.rng = random.Random(seed)
        self.length = float(length)
        self.landmarks = [float(m) for m in landmarks]
        self.particles = [self.rng.uniform(0.0, self.length) for _ in range(n)]
        self.weights = [1.0 / n] * n

    def sensor(self, x):
        """Distance from x to the nearest landmark, measured round the loop."""
        return min(ring_distance(x, m, self.length) for m in self.landmarks)

    def predict(self, u, sigma_u):
        """Push every particle through the noisy motion model."""
        self.particles = [(p + u + self.rng.gauss(0.0, sigma_u)) % self.length
                          for p in self.particles]

    def update(self, z, sigma_z):
        """Reweight by the Gaussian likelihood of z, then normalise."""
        raw = []
        for p, w in zip(self.particles, self.weights):
            residual = (z - self.sensor(p)) / sigma_z
            raw.append(w * math.exp(-0.5 * residual * residual) + 1e-300)
        total = sum(raw)
        self.weights = [w / total for w in raw]

    def ess(self):
        """Effective sample size 1 / sum(w^2)."""
        return 1.0 / sum(w * w for w in self.weights)

    def resample(self):
        """Systematic resampling; weights become uniform again."""
        n = len(self.particles)
        step = 1.0 / n
        start = self.rng.random() * step
        cumulative = self.weights[0]
        i = 0
        drawn = []
        for j in range(n):
            target = start + j * step
            while target > cumulative and i < n - 1:
                i += 1
                cumulative += self.weights[i]
            drawn.append(self.particles[i])
        self.particles = drawn
        self.weights = [step] * n

    def estimate(self):
        """Circular weighted mean of the particles."""
        two_pi = 2.0 * math.pi
        cx = sum(w * math.cos(two_pi * p / self.length)
                 for p, w in zip(self.particles, self.weights))
        cy = sum(w * math.sin(two_pi * p / self.length)
                 for p, w in zip(self.particles, self.weights))
        return (math.atan2(cy, cx) % two_pi) * self.length / two_pi


print("1d variances:", [round(p, 4) for _, p in kalman_1d([1.0] * 4, 0.0, 1.0, 0.0, 1.0)])
'''}],
                "hints": [
                    "`kf_predict` is one line if you let the given helpers do the work: `mat_add(mat_mul(mat_mul(F, P), mat_t(F)), Q)`.",
                    "In `kf_update`, compute the n-vector `P H^T` once and reuse it for both `S` and `K`; `P' = P - K (P H^T)^T`.",
                    "`kalman_1d` is `kf_predict`/`kf_update` with n = 1: `x = [x0]`, `P = [[p0]]`, `F = [[1.0]]`, `H = [1.0]`.",
                    "For systematic resampling walk one index pointer forward as the targets `start + j/n` increase — never restart the scan, or the method degenerates to O(n^2).",
                ],
                "tests": [
                    {"name": "the scalar recursion: information adds", "code": r'''
_r1 = kalman_1d([1.0] * 5, 0.0, 1.0, 0.0, 1.0)
assert len(_r1) == 5, f"kalman_1d returned {len(_r1)} rows, expected one per measurement (5)"
for _n, (_x, _p) in enumerate(_r1, 1):
    assert abs(_p - 1.0 / (_n + 1)) < 1e-12, f"variance after {_n} readings is {_p!r}, expected {1.0 / (_n + 1)!r}"
    assert abs(_x - _n / (_n + 1.0)) < 1e-12, f"mean after {_n} readings is {_x!r}, expected {_n / (_n + 1.0)!r}"
_walk = kalman_1d([1.0] * 5, 0.0, 1.0, 0.5, 1.0)
assert _walk[-1][1] > _r1[-1][1], "process noise q > 0 must leave more residual variance than q = 0"
'''},
                    {"name": "predict grows the covariance, update shrinks it", "code": r'''
_x, _P = kf_predict([0.0, 1.0], [[1.0, 0.0], [0.0, 1.0]], [[1.0, 0.5], [0.0, 1.0]], [[0.1, 0.0], [0.0, 0.1]])
assert abs(_x[0] - 0.5) < 1e-12 and abs(_x[1] - 1.0) < 1e-12, f"predicted state {_x!r}, expected [0.5, 1.0]"
assert abs(_P[0][0] - 1.35) < 1e-12, f"P[0][0] after predict is {_P[0][0]!r}, expected 1.35"
assert abs(_P[0][1] - 0.5) < 1e-12 and abs(_P[1][0] - 0.5) < 1e-12, f"P off-diagonals are {_P[0][1]!r}/{_P[1][0]!r}, expected 0.5"
assert abs(_P[1][1] - 1.1) < 1e-12, f"P[1][1] after predict is {_P[1][1]!r}, expected 1.1"
_x2, _P2 = kf_update(_x, _P, 2.0, [1.0, 0.0], 1.0)
assert _P2[0][0] < _P[0][0], "measuring the position must reduce the position variance"
assert _P2[1][1] < _P[1][1], "correlation means a position reading also sharpens the velocity"
'''},
                    {"name": "constant velocity recovers an unmeasured state", "code": r'''
import random as _random
_rng = _random.Random(7)
_dt = 0.1
_truth = [2.0 * _k * _dt for _k in range(1, 61)]
_meas = [_t + _rng.gauss(0.0, 0.5) for _t in _truth]
_res = kalman_cv(_meas, _dt, 1e-4, 0.25, (0.0, 0.0), ((1.0, 0.0), (0.0, 1.0)))
assert len(_res) == 60, f"kalman_cv returned {len(_res)} rows, expected 60"
(_pos, _vel), _P = _res[-1]
assert abs(_vel - 2.0) < 0.1, f"final velocity estimate is {_vel!r}, expected within 0.1 of the true 2.0"
assert abs(_pos - _truth[-1]) < 0.2, f"final position estimate is {_pos!r}, expected within 0.2 of {_truth[-1]!r}"
_first_trace = _res[0][1][0][0] + _res[0][1][1][1]
_last_trace = _P[0][0] + _P[1][1]
assert _last_trace < _first_trace / 10.0, f"trace(P) only fell from {_first_trace!r} to {_last_trace!r}; evidence should shrink it far more"
_raw = sum((_m - _t) ** 2 for _m, _t in zip(_meas, _truth)) / 60
_filt = sum((_r[0][0] - _t) ** 2 for _r, _t in zip(_res, _truth)) / 60
assert _filt < _raw / 3.0, f"filtered MSE {_filt!r} should be far below the raw measurement MSE {_raw!r}"
'''},
                    {"name": "ring geometry and the nearest-landmark sensor", "code": r'''
assert abs(ring_distance(1.0, 19.0, 20.0) - 2.0) < 1e-12, f"ring_distance(1, 19, 20) gave {ring_distance(1.0, 19.0, 20.0)!r}, expected 2.0"
assert abs(ring_distance(3.0, 3.0, 20.0)) < 1e-12, "a point is zero distance from itself"
assert abs(ring_distance(0.0, 10.0, 20.0) - 10.0) < 1e-12, "antipodal points are length/2 apart"
_pf = ParticleFilter(200, 20.0, [0.0, 5.0, 12.0], seed=7)
assert abs(_pf.sensor(2.0) - 2.0) < 1e-12, f"sensor(2.0) gave {_pf.sensor(2.0)!r}, expected 2.0 (landmark at 0)"
assert abs(_pf.sensor(19.0) - 1.0) < 1e-12, f"sensor(19.0) gave {_pf.sensor(19.0)!r}, expected 1.0 (wrapping to the landmark at 0)"
assert abs(_pf.sensor(8.5) - 3.5) < 1e-12, f"sensor(8.5) gave {_pf.sensor(8.5)!r}, expected 3.5"
'''},
                    {"name": "weights normalise and the ESS reacts", "code": r'''
_pf = ParticleFilter(100, 20.0, [0.0, 5.0, 12.0], seed=7)
assert len(_pf.particles) == 100, f"expected 100 particles, got {len(_pf.particles)}"
assert abs(_pf.ess() - 100.0) < 1e-9, f"uniform weights give ESS = n = 100, got {_pf.ess()!r}"
_pf.update(0.5, 0.3)
assert abs(sum(_pf.weights) - 1.0) < 1e-9, f"weights sum to {sum(_pf.weights)!r}, expected 1.0"
assert all(w >= 0.0 for w in _pf.weights), "weights may not go negative"
_after = _pf.ess()
assert _after < 100.0, f"a sharp measurement must lower the ESS below 100, got {_after!r}"
_pf.resample()
assert abs(_pf.ess() - 100.0) < 1e-9, f"resampling resets the weights to uniform, ESS should be 100 again but is {_pf.ess()!r}"
assert all(abs(w - 0.01) < 1e-12 for w in _pf.weights), "every weight should be 1/n after resampling"
'''},
                    {"name": "systematic resampling keeps the survivors", "code": r'''
_pf = ParticleFilter(4, 20.0, [0.0], seed=3)
_pf.particles = [0.0, 1.0, 2.0, 3.0]
_pf.weights = [0.0, 0.0, 1.0, 0.0]
_pf.resample()
assert _pf.particles == [2.0, 2.0, 2.0, 2.0], f"all the weight sat on particle 2.0, so resampling must give four copies of it, got {_pf.particles!r}"
_pf2 = ParticleFilter(4, 20.0, [0.0], seed=3)
_pf2.particles = [0.1, 19.9, 0.2, 19.8]
_pf2.weights = [0.25] * 4
_est = _pf2.estimate()
assert min(_est, 20.0 - _est) < 0.05, f"the circular mean of particles either side of the wrap should be near 0, got {_est!r}"
'''},
                    {"name": "the particle filter localises a multimodal robot", "code": r'''
import random as _random
_L = 20.0
_lms = [0.0, 5.0, 12.0]
_pf = ParticleFilter(600, _L, _lms, seed=7)
_sim = _random.Random(11)
_truth = 3.0
for _step in range(25):
    _truth = (_truth + 1.0 + _sim.gauss(0.0, 0.05)) % _L
    _pf.predict(1.0, 0.1)
    _z = min(ring_distance(_truth, _m, _L) for _m in _lms) + _sim.gauss(0.0, 0.2)
    _pf.update(_z, 0.3)
    if _pf.ess() < len(_pf.particles) / 2:
        _pf.resample()
_err = ring_distance(_pf.estimate(), _truth, _L)
assert _err < 1.0, f"after 25 steps the estimate is {_pf.estimate()!r} against a truth of {_truth!r} — an error of {_err!r}, expected under 1.0"
_spread = ring_distance(max(_pf.particles), min(_pf.particles), _L)
assert len(_pf.particles) == 600, "the particle count must stay constant"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Motion planning",
            "summary": "Optimal search on a grid, and sampling when the grid is hopeless.",
            "concepts": [
                "Occupancy grids; obstacle inflation by the robot radius turns a body into a point",
                "A* expands by f = g + h; an admissible, consistent h keeps the result optimal",
                "The octile distance is the tight admissible heuristic for 8-connected grids",
                "No-corner-cutting: a diagonal move needs both orthogonal neighbours free",
                "Nodes expanded is the honest measure of search effort, not path length",
                "RRT trades optimality for probabilistic completeness in continuous space",
                "Goal biasing and step size govern how fast an RRT finds anything at all",
            ],
            "read": [
                {
                    "title": "Finding a way through, and knowing what it cost",
                    "minutes": 15,
                    "body": r'''
A delivery robot 40 cm across is parked at one corner of a warehouse whose floor has
been mapped as a grid of half-metre cells, each marked free or occupied. The shelving
runs in long rows with gaps in it. The robot has to get to the far corner, and it has
to decide two things before it moves: which cells it may enter at all, given that it
has a body and not a point, and in what order to cross them so that the trip is as
short as it can be. The second question has a beautiful answer. The first has to be
settled before the second is even well posed.

## The body becomes a point

Planning for a body is hard; planning for a point is a solved problem. The trick is to
move the body's size out of the robot and into the map. If the robot is a disc of
radius one cell, then any cell within one cell of an obstacle is a cell whose *centre*
the robot cannot occupy without overlapping the obstacle. Paint every such cell
occupied — a square of Chebyshev radius 1 around each original obstacle — and the
robot may thereafter be treated as a point on the inflated map. A gap one cell wide
closes; a gap three cells wide keeps a one-cell channel down its middle.

The mistake here is to paint into the same grid you are reading from:

```python
narrow = [[0] * 7 for _ in range(3)] + [[1, 1, 1, 0, 1, 1, 1]] + [[0] * 7 for _ in range(3)]


def inflate_in_place(grid, radius):
    out = [list(row) for row in grid]
    rows, cols = len(out), len(out[0])
    for r in range(rows):
        for c in range(cols):
            if out[r][c]:                      # reads the grid it is painting
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < rows and 0 <= cc < cols:
                            out[rr][cc] = 1
    return out


grown = inflate_in_place(narrow, 1)
print("occupied per row:", [sum(row) for row in grown])
print("total:", sum(map(sum, grown)))
```

The wall has six obstacle cells and a radius of one should paint 21 cells: the three
rows either side of and including the wall, full width. This prints `[0, 0, 7, 7, 7,
7, 7]` and a total of 35. The scan reaches row 4, finds the cells it painted a moment
ago, treats them as obstacles, and paints row 5 from them, and so on to the bottom of
the map. It is tempting because copying the grid *looks* like the safeguard, and it is
not: the safeguard is reading only from the input and writing only to the output.

## Cost, and a promise about what remains

On the inflated grid the robot is a point that can step to any of eight neighbours.
Orthogonal steps cost 1 and diagonal steps cost $\sqrt 2$, because that is how far the
centre moves. Dijkstra's algorithm finds the cheapest path by always expanding the
frontier cell with the smallest cost-so-far $g$, and it is correct because a cell is
never settled before every cheaper cell has been. It is also blind: it expands in
every direction equally, including straight away from the goal.

A* keeps the guarantee and loses the blindness by expanding on $f = g + h$, where $h$
is an estimate of the cost still to go. The guarantee survives if and only if $h$
*never overestimates*. Here is why. Suppose A* pops the goal with $f = g_{\text{goal}}$
while some cheaper path of true cost $C < g_{\text{goal}}$ exists. Some cell on that
cheaper path is on the frontier; call it $n$, with $g(n)$ its true cost along the cheap
path. Since $h$ never overestimates, $f(n) = g(n) + h(n) \le g(n) + (\text{true cost
from } n) = C < g_{\text{goal}}$. So $n$ would have been popped before the goal. The
goal was popped first, so no such path exists.

What is the largest $h$ that never overestimates on an 8-connected grid? On an empty
grid, crossing $d_r$ rows and $d_c$ columns is done fastest by taking $\min(d_r, d_c)$
diagonals and then the remaining $|d_r - d_c|$ orthogonal steps, so

$$h_{\text{octile}} = \sqrt 2 \min(d_r, d_c) + \big(\max(d_r, d_c) - \min(d_r, d_c)\big) =
(d_r + d_c) + (\sqrt 2 - 2)\min(d_r, d_c).$$

Obstacles can only make the true cost larger, so this is admissible, and on an empty
grid it is exact. From (0, 0) to (3, 5) it is $3\sqrt 2 + 2 = 6.243$.

## The search, with the numbers on

```python
import heapq
import math

SQRT2 = math.sqrt(2.0)


def octile(a, b):
    dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dr + dc) + (SQRT2 - 2.0) * min(dr, dc)


def astar(grid, start, goal, h=octile):
    rows, cols = len(grid), len(grid[0])
    frontier = [(h(start, goal), 0, start)]
    came, cost, settled, tie, expanded = {}, {start: 0.0}, set(), 0, 0
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node in settled:
            continue
        settled.add(node)
        expanded += 1
        if node == goal:
            path = [node]
            while path[-1] in came:
                path.append(came[path[-1]])
            return path[::-1], expanded
        r, c = node
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if not (0 <= rr < rows and 0 <= cc < cols) or grid[rr][cc]:
                    continue
                if dr and dc and (grid[r][cc] or grid[rr][c]):
                    continue                   # no corner cutting
                g = cost[node] + (SQRT2 if dr and dc else 1.0)
                if g < cost.get((rr, cc), float("inf")) - 1e-12:
                    cost[(rr, cc)] = g
                    came[(rr, cc)] = node
                    tie += 1
                    heapq.heappush(frontier, (g + h((rr, cc), goal), tie, (rr, cc)))
    return None, expanded


def length(path):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))


empty = [[0] * 6 for _ in range(6)]
path, expanded = astar(empty, (0, 0), (5, 5))
print("octile:  length", round(length(path), 4), "settled", expanded)
path, expanded = astar(empty, (0, 0), (5, 5), h=lambda a, b: 0.0)
print("h = 0:   length", round(length(path), 4), "settled", expanded)

wall = [[0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]]
path, expanded = astar(wall, (0, 0), (3, 5))
print("wall:    length", round(length(path), 4), "settled", expanded)
```

On the empty 6-by-6 grid the diagonal costs $5\sqrt 2 = 7.0711$ and A* settles exactly
6 cells: the diagonal itself. Every other cell has $f$ strictly greater — the cell (1,
0), for instance, has $g = 1$ and $h = 4\sqrt 2 + 1 = 6.657$, so $f = 7.657$, and it is
never popped. Set $h$ to zero and the same path is found after settling all 36 cells,
because without a guess about what remains the search has to sweep the whole board.
That is the honest measure of what the heuristic bought: the path is identical, and it
is a property of the world; the count of settled cells is a property of the search.

On the wall grid, which is the one in the lab's starter file, the goal at (3, 5) sits
inside an alcove and the search has to go round the top: the path is $8 + \sqrt 2 =
9.4142$ long and 22 cells are settled. Notice that the heap entries carry a strictly
increasing `tie` counter between $f$ and the cell. Two cells with equal $f$ are then
ordered by insertion, never by comparing tuples of coordinates, and the same grid
always gives the same path.

## Corners

The `no corner cutting` line deserves its own paragraph. A diagonal step from $(r, c)$
to $(r+1, c+1)$ passes through the shared corner of the cells $(r, c+1)$ and $(r+1,
c)$. If either of those is occupied, a robot with any width at all clips it; the
inflated grid has made the robot a point, but the *path* between cell centres still has
to be clear. So the diagonal is allowed only when both orthogonal neighbours are free.
On the two-by-two grid `[[0, 1], [1, 0]]` the corners touch and there is no legal
move: the lab expects `None`.

## When the guess is too big

The Manhattan distance $d_r + d_c$ is the obvious heuristic and it is wrong for this
grid: it charges 2 for a diagonal that costs $1.414$, so it overestimates, and the
proof above no longer goes through.

```python
import heapq
import math

SQRT2 = math.sqrt(2.0)


def octile(a, b):
    dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dr + dc) + (SQRT2 - 2.0) * min(dr, dc)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, goal, h):
    rows, cols = len(grid), len(grid[0])
    frontier = [(h(start, goal), 0, start)]
    came, cost, settled, tie, expanded = {}, {start: 0.0}, set(), 0, 0
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node in settled:
            continue
        settled.add(node)
        expanded += 1
        if node == goal:
            path = [node]
            while path[-1] in came:
                path.append(came[path[-1]])
            return path[::-1], expanded
        r, c = node
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if not (0 <= rr < rows and 0 <= cc < cols) or grid[rr][cc]:
                    continue
                if dr and dc and (grid[r][cc] or grid[rr][c]):
                    continue
                g = cost[node] + (SQRT2 if dr and dc else 1.0)
                if g < cost.get((rr, cc), float("inf")) - 1e-12:
                    cost[(rr, cc)] = g
                    came[(rr, cc)] = node
                    tie += 1
                    heapq.heappush(frontier, (g + h((rr, cc), goal), tie, (rr, cc)))
    return None, expanded


def length(path):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))


grid = [[0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0]]
for name, h in (("octile", octile), ("manhattan", manhattan)):
    path, expanded = astar(grid, (0, 0), (5, 5), h)
    print(name, "length", round(length(path), 4), "settled", expanded)
```

Octile settles 12 cells and returns a path of length $8.2426$. Manhattan settles 10
cells and returns a path of length $8.8284$: fewer expansions, and a route that is
0.59 longer than the best one. That is the trap. An inflated heuristic is *faster*,
because it drives the search harder toward the goal, and a benchmark that counts
expansions and never checks path length will report it as an improvement. Consistency
is the slightly stronger property the lab's tests assume — $h(n) \le c(n, m) + h(m)$
for every edge — and octile has it, which is what lets the search settle a cell the
first time it is popped and ignore stale heap entries afterwards.

## When the grid is hopeless

A grid is a fine model of a warehouse floor and a terrible model of a six-joint arm.
Its configuration space has six dimensions, and at one-degree resolution that is
$360^6 \approx 2 \times 10^{15}$ cells, before inflation. No search that visits cells
can live there. A rapidly-exploring random tree gives up on visiting cells and grows a
tree by sampling: draw a random point in the space, find the tree node nearest to it,
step a fixed distance from that node toward the sample, keep the new node if the
segment to it is collision-free, and stop when a node lands within tolerance of the
goal.

The nearest-node rule is what makes it *rapidly exploring*. A node on the edge of the
tree next to a large empty region is the nearest node for every sample in that region,
so it gets extended far more often than a node buried in the middle: the tree is
pulled toward the space it has not seen. Sampling the goal itself with a small
probability, the goal bias, adds a steady tug in the right direction. In the lab's
world of two disc obstacles between (0, 0) and (5, 5), seed 7 with a 5% bias builds a
tree of 36 nodes and returns a 19-waypoint path of length 8.8 against a straight line
of 7.07; with the bias at zero the same seed needs 48 nodes, and at 30% it needs 27.
Those numbers move with the seed, which is the point: the RRT trades the grid's
determinism and optimality for the ability to find *something* in a space the grid
cannot represent. It is probabilistically complete — the chance of missing an
existing path goes to zero as the node count grows — and its paths are wandering, as
8.8 against 7.07 shows.

## Where it stops holding

A* is optimal and its expansion count is honest, and both stop meaning much once the
grid is too big to hold or the space is continuous. The RRT finds paths in spaces the
grid cannot touch, and never the shortest one; RRT\* rewires the tree as it grows and
recovers optimality in the limit, at a cost per node. Both planners assume a static
map. A planner on a live robot replans as the map changes, which is where the
inflation radius earns a safety margin beyond the robot's true size.

## What you are about to build

The lab *A\* on an occupancy grid, then an RRT* asks for `inflate` into a fresh grid,
`octile`, `astar` returning both the path and the count of settled cells, with the
corner rule, the `tie` counter, `ValueError` for an off-grid endpoint and `(None, 0)`
for an occupied one, `path_length`, and `rrt` over disc obstacles with every random
number drawn from one seeded generator. Its tests check the $5\sqrt 2$ diagonal, the
$8 + \sqrt 2$ detour round the wall, the closed one-cell gap after inflation, and that
two runs of the RRT on the same seed give the same tree.
''',
                },
            ],
            "quiz": {
                "title": "Optimal, admissible and rapidly exploring",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Why must obstacles be inflated by the robot's radius *before* planning, rather than checking the robot's footprint at every step of the search?",
                        "opts": [
                            "Inflation turns the robot into a point on a modified map, so a plain grid search stays correct and cheap",
                            "Inflation is needed because A* can only handle grids where every free cell is at least two cells from an obstacle",
                            "Inflation makes the search find shorter paths, since the obstacles' inflated shapes are simpler to route around",
                            "Inflation is optional on a grid; it matters only for continuous planners like the RRT",
                        ],
                        "a": 0,
                        "whys": [
                            r"A cell whose centre is within the radius of an obstacle is a cell the body cannot occupy. Marking those once moves the body's size into the map, and the search never has to think about it again.",
                            r"A* has no such requirement; it searches whatever grid it is given. The inflation is about what the *robot* can occupy, not about what the algorithm can handle.",
                            r"Inflation removes cells, so paths can only get longer or vanish. What it buys is that the paths that remain are ones the body can actually follow.",
                            r"It is the grid planner that needs it most: A* treats the robot as a point at a cell centre, and without inflation a point path runs a wide robot straight into shelving.",
                        ],
                        "why": r"""
A grid search moves a point between cell centres. A robot has a body, so a point path
that hugs an obstacle is a collision. Painting every cell within the robot's radius of
an obstacle as occupied makes the point path correct for the body, once, before the
search starts; the search itself is unchanged. The lab checks the consequence directly:
a one-cell gap that a point passes through is closed for a robot of radius one.
""",
                    },
                    {
                        "q": "On an 8-connected grid where diagonals cost $\\sqrt 2$, what goes wrong if A* uses the Manhattan distance $d_r + d_c$ as its heuristic?",
                        "opts": [
                            "Nothing: any distance-like heuristic gives an optimal path, and Manhattan expands fewer cells",
                            "The search may return a path that is not the shortest, because the heuristic can overestimate the remaining cost",
                            "The search never terminates on grids with obstacles, because the heuristic can equal zero at cells far away from the goal",
                            "The search expands more cells than Dijkstra, because Manhattan underestimates the diagonal moves",
                        ],
                        "a": 1,
                        "whys": [
                            r"Fewer expansions is precisely the symptom, and it is bought at the wrong price. The reading's 6-by-6 example settles 10 cells instead of 12 and hands back a path 0.59 longer than the best one.",
                            r"Manhattan charges 2 for a diagonal that costs 1.414, so it overestimates, and the argument that the goal is popped only after every cheaper path no longer holds.",
                            r"A heuristic that is zero somewhere is fine; Dijkstra is A* with $h = 0$ everywhere and terminates. Termination is not the issue; optimality is.",
                            r"Manhattan *over*estimates diagonals, not under. Over-estimation makes the search greedier and faster, which is why it looks like a win until the path length is checked.",
                        ],
                        "why": r"""
A* is optimal only when $h$ never overestimates the true remaining cost. Manhattan
counts a diagonal as two unit steps, so it overestimates wherever a diagonal is
possible, and the guarantee is lost. The failure is quiet: the search finishes sooner
and returns a plausible path that is not the shortest. Octile is the largest
heuristic that is still admissible on this grid, which is why it is both safe and
tight.
""",
                    },
                    {
                        "q": "On an empty 6-by-6 grid A* with the octile heuristic settles 6 cells for the corner-to-corner path; with $h = 0$ it settles 36. What is the right conclusion?",
                        "opts": [
                            "The heuristic found a shorter path, so the octile run is the better planner on both counts",
                            "The heuristic pruned the search without changing the path, so expansions measure the search, not the world",
                            "The $h = 0$ run is more reliable, since it examined every cell before answering",
                            "The two runs found different paths of equal length, and settling more cells reveals more of those alternatives",
                        ],
                        "a": 1,
                        "whys": [
                            r"Both runs return the same diagonal of length $5\sqrt 2$. An admissible heuristic never changes the answer; it changes how much work is done to reach it.",
                            r"The path is a property of the grid; the count of settled cells is a property of the search. Only the second moved.",
                            r"Examining every cell is not extra reliability, it is wasted work. Dijkstra and A* with an admissible heuristic are both exact; one of them knows which cells cannot matter.",
                            r"The tie counter makes both runs deterministic and they pop the same cells in the same order along the diagonal; the difference is the 30 cells the heuristic never had to pop.",
                        ],
                        "why": r"""
With an admissible heuristic the path is the same as Dijkstra's — that is what
admissibility guarantees. What differs is effort: every off-diagonal cell has $f$
above $5\sqrt 2$ under octile and is never popped, whereas with $h = 0$ nothing rules
them out. That is why the lab returns `expanded` alongside the path: length tells you
about the map, the count tells you about the planner.
""",
                    },
                    {
                        "q": "What does the no-corner-cutting rule forbid, and why does it exist even after obstacles have been inflated?",
                        "opts": [
                            "A diagonal step when either cell at the shared corner is occupied, since the segment between centres would clip it",
                            "Any diagonal step next to an obstacle, because inflation accounts only for orthogonal clearance and not diagonal clearance",
                            "A diagonal step when the destination cell is occupied, because the search must not enter obstacles",
                            "Two consecutive diagonal steps, because the path would then leave the 8-connected neighbourhood",
                        ],
                        "a": 0,
                        "whys": [
                            r"The segment from $(r, c)$ to $(r+1, c+1)$ passes through the corner shared with $(r, c+1)$ and $(r+1, c)$. If either is a wall, the move brushes it.",
                            r"Inflation is symmetric in all directions and clears diagonals as well as it clears anything. The corner rule is about the *segment* between two free centres, which can still touch an obstacle's corner.",
                            r"Entering an occupied cell is refused for every step, diagonal or not, by the ordinary free-cell check. The corner rule is an extra condition on diagonals whose destination is free.",
                            r"Consecutive diagonals are fine; the empty-grid solution is five of them in a row. The neighbourhood is checked one step at a time.",
                        ],
                        "why": r"""
On the inflated grid the robot is a point, but the point moves along a straight
segment between cell centres, and a diagonal segment passes through the corner where
two other cells meet. If one of those is occupied the segment grazes it. So a diagonal
from $(r, c)$ is allowed only when both $(r, c + d_c)$ and $(r + d_r, c)$ are free. The
lab's `[[0, 1], [1, 0]]` grid has two free cells that touch only at such a corner,
and the correct answer is that there is no path.
""",
                    },
                    {
                        "q": "An RRT is run on a world with a clear route between start and goal. Which statement about its result is correct?",
                        "opts": [
                            "It returns the shortest collision-free path once the tree contains enough nodes",
                            "It finds *a* collision-free path with probability approaching 1 as nodes are added, with no claim about length",
                            "It fails whenever the goal is not sampled directly, so the goal bias must be set well above zero for it to work at all",
                            "It returns the same path as A* on a fine enough grid, since both are complete planners",
                        ],
                        "a": 1,
                        "whys": [
                            r"An RRT's path is a chain of random steps and is never the shortest; the reading's example is 8.8 long against a straight line of 7.07. RRT* adds rewiring to converge on the optimum.",
                            r"Probabilistic completeness is the whole promise: a path that exists will be found with probability tending to 1. Nothing is said about how good it is.",
                            r"Goal bias speeds the search up — 48 nodes at zero bias against 36 at 5% in the reading — but with bias zero the tree still reaches the goal region by ordinary sampling.",
                            r"A* is optimal and deterministic on its grid; an RRT is neither. They agree on whether a path exists, given enough effort, and on almost nothing else.",
                        ],
                        "why": r"""
The RRT's guarantee is probabilistic completeness: if a path exists, the probability of
finding one tends to 1 as the tree grows. Its paths are whatever chain of random steps
reached the goal first, and the lab's own test bounds their length only loosely, at
less than three times the straight line. Goal bias and step size change how fast a
path is found, not whether one is found. The trade is deliberate: optimality and
determinism in exchange for working in spaces no grid can hold.
""",
                    },
                ],
            },
            "lab": {
                "title": "A* on an occupancy grid, then an RRT",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Grids are lists of rows of `0` (free) and `1` (occupied); a cell is a
`(row, col)` tuple.

**`inflate(grid, radius)`** — a *new* grid where every occupied cell has
painted a square of Chebyshev radius `radius` around itself. Do not mutate the
input, and do not let a freshly painted cell seed further growth.

**`octile(a, b)`** — `(dr + dc) + (sqrt(2) - 2) * min(dr, dc)`, the exact
cost of crossing `dr`, `dc` cells on an empty 8-connected grid.

**`astar(grid, start, goal)`** — return `(path, expanded)`:

- `path` is the list of cells from `start` to `goal`, or `None` when there is none
- `expanded` counts cells popped from the frontier and settled
- orthogonal steps cost 1, diagonal steps cost `sqrt(2)`
- a diagonal step from `(r, c)` to `(r+dr, c+dc)` is forbidden when either
  `(r, c+dc)` or `(r+dr, c)` is occupied — robots do not squeeze through seams
- an occupied start or goal yields `(None, 0)`
- a start or goal outside the grid raises `ValueError`
- push `(f, tie, cell)` with a strictly increasing `tie` counter so ties break deterministically

**`path_length(path)`** — the summed Euclidean length; `0.0` for `None`, an
empty path or a single cell.

**`rrt(start, goal, obstacles, bounds, step, goal_tol, goal_bias, max_nodes, seed)`**
— a rapidly-exploring random tree in the plane. `obstacles` is a list of
`(cx, cy, radius)` discs, `bounds` is `(xmin, xmax, ymin, ymax)`. Each iteration:

1. with probability `goal_bias` sample the goal itself, else sample uniformly in `bounds`
2. find the nearest existing node
3. step at most `step` from it towards the sample
4. discard the candidate if it leaves `bounds` or if the segment to it clips a disc
5. otherwise add it; if it lands within `goal_tol` of the goal, walk the parents back and return

Return `(path, nodes)` — `path` a list of `(x, y)` or `None`, `nodes` the size
of the tree. Draw every random number from one `random.Random(seed)`.

Reference results on an empty 6x6 grid: `astar(grid, (0,0), (5,5))` returns a
6-cell path of length `5*sqrt(2)` and settles 6 cells.
''',
                "files": [{"name": "main.py", "content": r'''
import heapq
import math
import random

SQRT2 = math.sqrt(2.0)


def inflate(grid, radius):
    """A new grid with every obstacle grown by radius cells in Chebyshev distance."""
    # your code here


def octile(a, b):
    """Admissible 8-connected heuristic between two (row, col) cells."""
    # your code here


def astar(grid, start, goal):
    """(path, expanded) — path is None when the goal is unreachable."""
    # your code here


def path_length(path):
    """Summed Euclidean length of a cell path; 0.0 for None or a single cell."""
    # your code here


def point_free(p, obstacles):
    """True when the point misses every disc obstacle."""
    # your code here


def segment_free(a, b, obstacles, resolution=0.05):
    """True when the whole segment a-b misses every disc obstacle."""
    # your code here


def rrt(start, goal, obstacles, bounds, step=0.5, goal_tol=0.5,
        goal_bias=0.05, max_nodes=3000, seed=7):
    """(path, nodes) for a seeded rapidly-exploring random tree."""
    # your code here


GRID = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

print("A*:", astar(GRID, (0, 0), (3, 5)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import heapq
import math
import random

SQRT2 = math.sqrt(2.0)


def inflate(grid, radius):
    """A new grid with every obstacle grown by radius cells in Chebyshev distance."""
    rows, cols = len(grid), len(grid[0])
    out = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if not grid[r][c]:
                continue
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        out[rr][cc] = 1
    return out


def octile(a, b):
    """Admissible 8-connected heuristic between two (row, col) cells."""
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return (dr + dc) + (SQRT2 - 2.0) * min(dr, dc)


def _neighbours(grid, node):
    rows, cols = len(grid), len(grid[0])
    r, c = node
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if not (0 <= rr < rows and 0 <= cc < cols) or grid[rr][cc]:
                continue
            if dr and dc:
                if grid[r][cc] or grid[rr][c]:
                    continue
                yield (rr, cc), SQRT2
            else:
                yield (rr, cc), 1.0


def astar(grid, start, goal):
    """(path, expanded) — path is None when the goal is unreachable."""
    rows, cols = len(grid), len(grid[0])
    for node in (start, goal):
        if not (0 <= node[0] < rows and 0 <= node[1] < cols):
            raise ValueError(f"cell {node!r} is outside the {rows}x{cols} grid")
    if grid[start[0]][start[1]] or grid[goal[0]][goal[1]]:
        return None, 0
    frontier = [(octile(start, goal), 0, start)]
    came = {}
    cost = {start: 0.0}
    settled = set()
    tie = 0
    expanded = 0
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node in settled:
            continue
        settled.add(node)
        expanded += 1
        if node == goal:
            path = [node]
            while path[-1] in came:
                path.append(came[path[-1]])
            path.reverse()
            return path, expanded
        for nb, step_cost in _neighbours(grid, node):
            if nb in settled:
                continue
            g = cost[node] + step_cost
            if g < cost.get(nb, float("inf")) - 1e-12:
                cost[nb] = g
                came[nb] = node
                tie += 1
                heapq.heappush(frontier, (g + octile(nb, goal), tie, nb))
    return None, expanded


def path_length(path):
    """Summed Euclidean length of a cell path; 0.0 for None or a single cell."""
    if not path or len(path) < 2:
        return 0.0
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))


def point_free(p, obstacles):
    """True when the point misses every disc obstacle."""
    return all(math.hypot(p[0] - o[0], p[1] - o[1]) > o[2] for o in obstacles)


def segment_free(a, b, obstacles, resolution=0.05):
    """True when the whole segment a-b misses every disc obstacle."""
    span = math.hypot(b[0] - a[0], b[1] - a[1])
    steps = max(2, int(span / resolution) + 1)
    for i in range(steps + 1):
        t = i / steps
        if not point_free((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), obstacles):
            return False
    return True


def rrt(start, goal, obstacles, bounds, step=0.5, goal_tol=0.5,
        goal_bias=0.05, max_nodes=3000, seed=7):
    """(path, nodes) for a seeded rapidly-exploring random tree."""
    rng = random.Random(seed)
    xmin, xmax, ymin, ymax = bounds
    nodes = [(float(start[0]), float(start[1]))]
    parent = {0: None}
    for _ in range(max_nodes - 1):
        if rng.random() < goal_bias:
            sample = (float(goal[0]), float(goal[1]))
        else:
            sample = (rng.uniform(xmin, xmax), rng.uniform(ymin, ymax))
        best = min(range(len(nodes)),
                   key=lambda i: (nodes[i][0] - sample[0]) ** 2 + (nodes[i][1] - sample[1]) ** 2)
        near = nodes[best]
        span = math.hypot(sample[0] - near[0], sample[1] - near[1])
        if span < 1e-12:
            continue
        t = min(step, span) / span
        new = (near[0] + t * (sample[0] - near[0]), near[1] + t * (sample[1] - near[1]))
        if not (xmin <= new[0] <= xmax and ymin <= new[1] <= ymax):
            continue
        if not segment_free(near, new, obstacles):
            continue
        nodes.append(new)
        parent[len(nodes) - 1] = best
        if math.hypot(new[0] - goal[0], new[1] - goal[1]) <= goal_tol:
            path = []
            i = len(nodes) - 1
            while i is not None:
                path.append(nodes[i])
                i = parent[i]
            path.reverse()
            return path, len(nodes)
    return None, len(nodes)


GRID = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

print("A*:", astar(GRID, (0, 0), (3, 5)))
'''}],
                "hints": [
                    "Write `inflate` into a fresh output grid and read only from the input — painting in place makes obstacles grow without limit.",
                    "Settle a node the moment you pop it, and skip anything already settled; that is how you tolerate stale heap entries instead of trying to decrease keys.",
                    "The no-corner-cutting rule is two lookups: `grid[r][c+dc]` and `grid[r+dr][c]` must both be free before a diagonal is allowed.",
                    "For the RRT, reconstruct the path by walking `parent[i]` back to `None` and reversing — store parents by index, not by coordinate, since two nodes can coincide.",
                ],
                "tests": [
                    {"name": "octile, and A* achieving it on an empty grid", "code": r'''
import math
_want = 2.0 + 3.0 * math.sqrt(2.0)
assert abs(octile((0, 0), (3, 5)) - _want) < 1e-12, f"octile((0,0),(3,5)) gave {octile((0, 0), (3, 5))!r}, expected {_want!r}"
assert abs(octile((2, 2), (2, 2))) < 1e-12, "octile of a cell with itself is 0"
assert abs(octile((0, 0), (0, 4)) - 4.0) < 1e-12, f"a pure sideways run of 4 costs 4, got {octile((0, 0), (0, 4))!r}"
_empty = [[0] * 6 for _ in range(6)]
_p, _e = astar(_empty, (0, 0), (5, 5))
assert _p == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], f"expected the straight diagonal, got {_p!r}"
assert abs(path_length(_p) - 5 * math.sqrt(2.0)) < 1e-12, f"path_length gave {path_length(_p)!r}, expected {5 * math.sqrt(2.0)!r}"
assert _e <= 12, f"a consistent heuristic should settle about 6 cells here, not {_e}"
_p2, _e2 = astar(_empty, (0, 0), (0, 5))
assert abs(path_length(_p2) - 5.0) < 1e-12, f"a straight run of 5 has length 5.0, got {path_length(_p2)!r}"
'''},
                    {"name": "obstacles, boundaries and the empty path", "code": r'''
import math
_p, _e = astar(GRID, (0, 0), (3, 5))
assert _p is not None, "the goal is reachable round the top of the wall"
assert _p[0] == (0, 0) and _p[-1] == (3, 5), f"path must run start to goal, got {_p[0]!r}..{_p[-1]!r}"
assert abs(path_length(_p) - (8.0 + math.sqrt(2.0))) < 1e-9, f"optimal detour is 8 + sqrt(2) = {8.0 + math.sqrt(2.0)!r}, got {path_length(_p)!r}"
assert _e >= len(_p), f"A* settled {_e} cells for a {len(_p)}-cell path — it must settle at least the path"
_same, _es = astar(GRID, (2, 2), (2, 2))
assert _same == [(2, 2)] and _es == 1, f"start == goal should give ([(2, 2)], 1), got ({_same!r}, {_es!r})"
assert path_length(_same) == 0.0 and path_length(None) == 0.0, "a one-cell path and None both have length 0.0"
'''},
                    {"name": "unreachable, occupied and off-grid", "code": r'''
_walled = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
_p, _e = astar(_walled, (0, 0), (0, 2))
assert _p is None, f"a full-height wall makes the goal unreachable, got {_p!r}"
assert _e >= 1, "the search should still have settled the reachable side"
assert astar(_walled, (0, 1), (0, 2)) == (None, 0), "an occupied start returns (None, 0) without searching"
assert astar(_walled, (0, 0), (1, 1)) == (None, 0), "an occupied goal returns (None, 0) without searching"
try:
    astar(_walled, (0, 0), (9, 9))
    assert False, "a goal outside the grid must raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "no corner cutting through a diagonal seam", "code": r'''
_seam = [[0, 1], [1, 0]]
_p, _e = astar(_seam, (0, 0), (1, 1))
assert _p is None, f"(0,0) and (1,1) touch only at a corner between two obstacles — no legal move, got {_p!r}"
_open = [[0, 0], [0, 0]]
_p2, _e2 = astar(_open, (0, 0), (1, 1))
assert _p2 == [(0, 0), (1, 1)], f"with both seams free the diagonal is legal, got {_p2!r}"
'''},
                    {"name": "inflation closes a corridor the robot cannot fit", "code": r'''
_narrow = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
]
assert astar(_narrow, (0, 0), (6, 6))[0] is not None, "a point robot fits through the one-cell gap"
_grown = inflate(_narrow, 1)
assert _narrow[3][3] == 0, "inflate must not mutate the grid it was given"
assert _grown[3][3] == 1 and _grown[2][3] == 1, "radius 1 closes a single-cell gap"
assert _grown[0][0] == 0 and _grown[6][6] == 0, "the far corners are more than one cell from any obstacle"
assert astar(_grown, (0, 0), (6, 6))[0] is None, "a robot of radius 1 cannot pass, so the inflated search must fail"
_wide = [list(_r) for _r in _narrow]
_wide[3] = [1, 1, 0, 0, 0, 1, 1]
_wide_grown = inflate(_wide, 1)
assert _wide_grown[3][3] == 0, "a three-cell gap keeps a one-cell channel after inflation"
assert astar(_wide_grown, (0, 0), (6, 6))[0] is not None, "the widened gap must still admit the inflated robot"
'''},
                    {"name": "the RRT finds a collision-free path", "code": r'''
import math
_obs = [(2.0, 2.0, 1.0), (4.0, 3.0, 0.8)]
_path, _nodes = rrt((0.0, 0.0), (5.0, 5.0), _obs, (0.0, 6.0, 0.0, 6.0),
                    0.5, 0.5, 0.05, 3000, 7)
assert _path is not None, "an RRT with 3000 nodes must solve this easy world"
assert 1 < _nodes <= 3000, f"tree size {_nodes} is out of range"
assert abs(_path[0][0]) < 1e-12 and abs(_path[0][1]) < 1e-12, f"the path must begin at the start, got {_path[0]!r}"
assert math.hypot(_path[-1][0] - 5.0, _path[-1][1] - 5.0) <= 0.5, f"the path must end within goal_tol of (5, 5), got {_path[-1]!r}"
for _a, _b in zip(_path, _path[1:]):
    assert math.hypot(_b[0] - _a[0], _b[1] - _a[1]) <= 0.5 + 1e-9, f"segment {_a!r}->{_b!r} is longer than the step size"
    assert segment_free(_a, _b, _obs), f"segment {_a!r}->{_b!r} clips an obstacle"
_len = path_length(_path)
assert _len >= math.hypot(5.0, 5.0) - 1e-9, f"an RRT path of {_len!r} cannot be shorter than the straight line {math.hypot(5.0, 5.0)!r}"
assert _len < 3 * math.hypot(5.0, 5.0), f"path length {_len!r} is implausibly wandering for this world"
'''},
                    {"name": "the RRT gives up honestly, and is deterministic", "code": r'''
_walled_in = [(2.5, 2.5, 20.0)]
_path, _nodes = rrt((0.0, 0.0), (5.0, 5.0), _walled_in, (0.0, 6.0, 0.0, 6.0),
                    0.5, 0.5, 0.05, 200, 7)
assert _path is None, f"every sample is inside the obstacle, so no path exists — got {_path!r}"
assert _nodes == 1, f"no candidate can be added, so the tree stays at the start node; got {_nodes}"
_obs = [(2.0, 2.0, 1.0), (4.0, 3.0, 0.8)]
_a = rrt((0.0, 0.0), (5.0, 5.0), _obs, (0.0, 6.0, 0.0, 6.0), 0.5, 0.5, 0.05, 3000, 7)
_b = rrt((0.0, 0.0), (5.0, 5.0), _obs, (0.0, 6.0, 0.0, 6.0), 0.5, 0.5, 0.05, 3000, 7)
assert _a == _b, "the same seed must give the same tree — draw every random number from self-contained random.Random(seed)"
_c = rrt((0.0, 0.0), (5.0, 5.0), _obs, (0.0, 6.0, 0.0, 6.0), 0.5, 0.5, 0.05, 3000, 11)
assert _c[0] is not None and _c != _a, "a different seed should explore differently"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Feedback control",
            "summary": "PID on a first-order plant: tuning, saturation and honest metrics.",
            "concepts": [
                "A first-order plant tau*y' = -y + K*u, discretised by forward Euler",
                "Proportional action alone leaves a steady-state offset of 1/(1 + K*kp)",
                "Integral action removes that offset by accumulating error over time",
                "Derivative action anticipates, and amplifies measurement noise while doing so",
                "Actuator saturation breaks the loop: the integral keeps growing while the plant cannot respond",
                "Conditional integration (anti-windup): only commit the integral when the output is unsaturated",
                "Step-response metrics: rise time, overshoot, settling time, steady-state error",
            ],
            "read": [
                {
                    "title": "Closing the loop on a plant that lags",
                    "minutes": 15,
                    "body": r'''
A wheel motor on the delivery robot is told to spin. Command it with $u = 0.5$ and the
wheel does not leap to speed: it climbs, fast at first and then slower, toward a speed
of $1.0$, taking about a second to get most of the way there. Push on the wheel and
it slows; let go and it climbs back. Every actuator you will ever control behaves a
little like this, and the simplest model that captures it is one line:

$$\tau\,\dot y = -y + K u .$$

$y$ is the speed, $u$ the command, $K = 2$ the gain (steady speed per unit command) and
$\tau = 1$ s the time constant. With $u$ held fixed, $\dot y = 0$ when $y = K u$, and
the further $y$ is from that the faster it moves toward it. To simulate it, replace
the derivative by a step of $\Delta t$: $y \leftarrow y + \Delta t\,(K u - y)/\tau$,
which is forward Euler and is exactly what the lab's `FirstOrderPlant.step` does, with
a `disturbance` added straight onto $y$ to model the push.

## Proportional: the offset it cannot remove

Ask for a setpoint $r = 1$. The obvious controller commands in proportion to the error,
$u = k_p (r - y)$. What speed does the wheel settle at? At rest $\dot y = 0$, so $y = K
u = K k_p (r - y)$. Solve for $y$:

$$y_\infty = \frac{K k_p}{1 + K k_p}\, r, \qquad r - y_\infty = \frac{r}{1 + K k_p}.$$

With $K = 2$ and $k_p = 1$ the wheel settles at $2/3$ and the error is $1/3$. This is
not a tuning accident. A proportional controller produces a command *only* from error,
and holding the wheel at any speed above zero needs a non-zero command, so the error
can never reach zero while the command is needed. A bigger $k_p$ shrinks the offset —
$k_p = 10$ leaves $1/21$ — and never removes it.

## Integral: the term that refuses to rest

Add a term that accumulates the error over time: $u = k_p e + k_i \int e\,dt$. Now ask
again what the loop can settle to. At rest everything is constant, including the
integral, and an integral is constant only when what it is integrating is zero. So
$e = 0$: the integrator keeps pushing the command up for as long as any error remains,
and stops exactly when there is none. The price is momentum. The integral is still
large when $y$ first reaches the setpoint, so the wheel overshoots and has to unwind.

```python
class Plant:
    def __init__(self, gain, tau, dt, y0=0.0):
        self.gain, self.tau, self.dt, self.y = gain, tau, dt, y0

    def step(self, u, disturbance=0.0):
        self.y += (self.gain * u - self.y) / self.tau * self.dt + disturbance
        return self.y


class PID:
    def __init__(self, kp, ki, kd, dt, out_min=-1e30, out_max=1e30):
        self.kp, self.ki, self.kd, self.dt = kp, ki, kd, dt
        self.out_min, self.out_max = out_min, out_max
        self.integral, self.prev_error = 0.0, None

    def update(self, setpoint, y):
        error = setpoint - y
        derivative = 0.0 if self.prev_error is None else (error - self.prev_error) / self.dt
        trial = self.integral + error * self.dt
        u = self.kp * error + self.ki * trial + self.kd * derivative
        if self.out_min <= u <= self.out_max:
            self.integral = trial
        else:
            u = max(self.out_min, min(self.out_max, u))
        self.prev_error = error
        return u


def simulate(plant, pid, setpoint, steps):
    ys = [plant.y]
    for _ in range(steps):
        ys.append(plant.step(pid.update(setpoint, plant.y)))
    return ys


ys = simulate(Plant(2.0, 1.0, 0.01), PID(1.0, 0.0, 0.0, 0.01), 1.0, 2000)
print("P only, final:", round(ys[-1], 4))

ys = simulate(Plant(2.0, 1.0, 0.01), PID(2.0, 5.0, 0.0, 0.01), 1.0, 2000)
peak = max(ys)
print("PI, final:", round(ys[-1], 4), "overshoot %:", round((peak - 1.0) * 100, 2),
      "at t =", ys.index(peak) * 0.01)
low = next(i for i, y in enumerate(ys) if y >= 0.1)
high = next(i for i, y in enumerate(ys) if y >= 0.9)
print("PI, rise time:", round((high - low) * 0.01, 2))
```

The proportional loop prints a final value of 0.6667, the $2/3$ from the algebra. The
PI loop with $k_p = 2$, $k_i = 5$ prints a final value of 1.0, an overshoot of 10.19%
peaking at $t = 0.79$ s, and a rise time — first sample at 10% to first sample at 90%
— of 0.33 s. Those are the anchors the lab brief quotes, and the four metric functions
you will write are what produced them: `rise_time`, `overshoot` as a percentage of the
setpoint, `steady_state_error` as the gap to the mean of the final tenth, and
`settling_time`, the time after which the response never again leaves a 2% band,
which for this run is 1.57 s.

## Derivative, and the kick

The third term, $k_d\,\dot e$, reacts to how fast the error is changing, so it brakes
the loop as it approaches the setpoint and softens the overshoot. It also multiplies
measurement noise by $k_d/\Delta t$, which with $\Delta t = 0.01$ is a hundred times
$k_d$, and that is why it is used sparingly on anything measured by a real sensor.

It has a trap on the very first call. There is no previous error yet, and the tempting
sentinel is `prev_error = 0.0`:

```python
class PID:
    def __init__(self, kp, kd, dt, prev_error):
        self.kp, self.kd, self.dt, self.prev_error = kp, kd, dt, prev_error

    def update(self, setpoint, y):
        error = setpoint - y
        derivative = 0.0 if self.prev_error is None else (error - self.prev_error) / self.dt
        self.prev_error = error
        return self.kp * error + self.kd * derivative


print("prev_error = None:", PID(1.0, 0.1, 0.01, None).update(1.0, 0.0))
print("prev_error = 0.0: ", PID(1.0, 0.1, 0.01, 0.0).update(1.0, 0.0))
```

With `None` the first command is 1.0, the proportional term alone. With `0.0` it is
11.0: the controller sees the error jump from 0 to 1 in one tick, computes a derivative
of $100$, multiplies by $k_d = 0.1$, and slams the actuator with ten times the intended
command on the first sample. Use `None` as the flag, as the lab's `reset` does, and
report zero derivative on the first call.

## Saturation, and the integral that keeps counting

Real actuators have limits. Give the motor a command range of $[0, 1]$ and ask for a
setpoint of 5: the wheel tops out at $K \times 1 = 2$, the error never falls below 3,
and the integrator does what integrators do. At $k_i = 4$ it accumulates about $4
\times 3 \times \Delta t$ of command per tick, and after five seconds it holds a
command contribution of nearly 70, all of it clamped away and none of it doing
anything. Now drop the setpoint to 1. The wheel is at 2, the error is $-1$, and the
integral unwinds at $k_i \times 1 \times \Delta t = 0.04$ per tick. Unwinding 70 takes
about 1700 ticks: seventeen seconds during which the command stays pinned at its
maximum and the wheel sits at twice the setpoint. That is windup.

The fix in the lab is conditional integration. Compute the trial integral, use it to
compute $u$, and *then* decide: if $u$ is inside the limits, commit the trial;
otherwise leave the integral where it was and clamp $u$. The integrator is allowed to
count only while counting can change the output.

```python
class Plant:
    def __init__(self, gain, tau, dt, y0=0.0):
        self.gain, self.tau, self.dt, self.y = gain, tau, dt, y0

    def step(self, u, disturbance=0.0):
        self.y += (self.gain * u - self.y) / self.tau * self.dt + disturbance
        return self.y


class PID:
    def __init__(self, kp, ki, dt, out_min, out_max, conditional):
        self.kp, self.ki, self.dt = kp, ki, dt
        self.out_min, self.out_max, self.conditional = out_min, out_max, conditional
        self.integral = 0.0

    def update(self, setpoint, y):
        error = setpoint - y
        trial = self.integral + error * self.dt
        u = self.kp * error + self.ki * trial
        if self.out_min <= u <= self.out_max or not self.conditional:
            self.integral = trial
        u = max(self.out_min, min(self.out_max, u))
        return u


def simulate(plant, pid, setpoint, steps):
    ys = [plant.y]
    for _ in range(steps):
        ys.append(plant.step(pid.update(setpoint, plant.y)))
    return ys


for conditional in (True, False):
    plant = Plant(2.0, 1.0, 0.01)
    pid = PID(1.0, 4.0, 0.01, 0.0, 1.0, conditional)
    simulate(plant, pid, 5.0, 500)
    wound = pid.integral
    after = simulate(plant, pid, 1.0, 500)
    print("conditional" if conditional else "always     ",
          "integral after 5 s:", round(wound, 3),
          "y 5 s after the drop:", round(after[-1], 4))
```

With conditional integration the integral after five saturated seconds is 0.0 — the
command was clamped on every tick, so the trial was never committed — and five seconds
after the setpoint drops the wheel is at 1.0005. With the integral always committed it
is 16.987, and five seconds after the drop the wheel is still at 1.9999. The lab's
test for this is the sharpest one in the module: after 500 saturated steps it asserts
`abs(controller.integral) < 1e-9`.

The mistake people make is to clamp first and commit afterwards, or to commit the trial
unconditionally and then clamp. Both look like anti-windup, because there is a clamp in
the code. Neither is, because the integral still grows while the clamp holds.

## Rejecting a push

The integral term does one more thing for you. Apply a steady disturbance — a constant
$0.002$ added to $y$ every tick from $t = 10$ s — to the PI loop above. The wheel jumps
to about 1.024, the error goes negative, the integral winds *down* until the command
has fallen by exactly enough to cancel the push, and the wheel returns to 1.0. An open
loop under the same push drifts to 1.2 and stays there. The disturbance never appears
in the controller's inputs; it is inferred from its effect on the error and cancelled.

## Where it stops holding

Two boundaries matter here. The first is the simulation itself. Forward Euler on the
closed loop with proportional control updates $y$ by a factor of $1 - \Delta t (1 + K
k_p)/\tau$ each tick, and that factor must stay inside $(-1, 1)$, so

$$\Delta t < \frac{2\tau}{1 + K k_p}.$$

For $K = 2$, $k_p = 1$, $\tau = 1$ the bound is $2/3$ s:

```python
class Plant:
    def __init__(self, gain, tau, dt, y0=0.0):
        self.gain, self.tau, self.dt, self.y = gain, tau, dt, y0

    def step(self, u):
        self.y += (self.gain * u - self.y) / self.tau * self.dt
        return self.y


for dt in (0.5, 1.0):
    plant = Plant(2.0, 1.0, dt)
    ys = [plant.y]
    for _ in range(int(20 / dt)):
        ys.append(plant.step(1.0 * (1.0 - plant.y)))
    print("dt", dt, "final", round(ys[-1], 4), "peak", round(max(ys), 4))
```

At $\Delta t = 0.5$ the loop oscillates on its way in (a peak of 1.0) and settles at
0.6667. At $\Delta t = 1.0$ it prints a final value of $-699050$: the plant is stable,
the controller is stable, and the *simulation* has blown up. When a tuned loop goes
wild, check the step size before the gains.

The second boundary is the plant. A first-order lag can never overshoot under
proportional control, and PID on it is nearly always tameable. Add a second lag, a
transport delay, or a nonlinearity — a robot arm's gravity load, a motor's friction —
and the same three gains can produce oscillation that no amount of $k_d$ removes.
PID is the right first controller for almost everything and the right last controller
for rather less.

## What you are about to build

The lab *A PID loop with anti-windup* asks for `FirstOrderPlant`, the `PID` class
with `reset` and the conditional-integration `update`, `simulate` returning `steps +
1` samples, and the four metrics. Its tests pin the $2/3$ offset, the 10.2% overshoot
and 0.33 s rise time, the zero integral after 500 saturated steps, the recovery after
the setpoint drops, and the rejection of the sustained disturbance. The same `PID`
class, with the same anti-windup rule, is the one the capstone's delivery agent drives
its wheels with, clamped at $\pm v_{\max}$.
''',
                },
            ],
            "quiz": {
                "title": "Three gains and one clamp",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A proportional controller with $k_p = 1$ drives a plant with gain $K = 2$ toward a setpoint of 1. It settles at $2/3$. Why not at 1?",
                        "opts": [
                            "At rest the command must be non-zero to hold the plant up, and a proportional command is non-zero only while error remains",
                            "Forward Euler with $\\Delta t = 0.01$ accumulates truncation error over the 2000 steps, and the error shows up as a $1/3$ shortfall at the end",
                            "The plant's gain of 2 halves the effective setpoint, and $k_p$ would need to be doubled to compensate exactly",
                            "The controller has not finished converging; a longer simulation would carry the output the rest of the way",
                        ],
                        "a": 0,
                        "whys": [
                            r"Solve $y = K k_p (r - y)$ at rest: $y = 2/3$. Zero error would mean zero command, and zero command lets the plant fall back to zero.",
                            r"Euler's error here is a few parts in $10^{6}$, not a third. The offset is in the algebra of the equilibrium, and no step size removes it.",
                            r"A higher gain shrinks the offset — $k_p = 2$ gives $4/5$ — and never removes it, because $K k_p/(1 + K k_p)$ is below 1 for every finite gain.",
                            r"The output is within $10^{-6}$ of $2/3$ at the end of the run and is not moving. The equilibrium of the proportional loop *is* $2/3$; there is nowhere else to go.",
                        ],
                        "why": r"""
At equilibrium $\dot y = 0$ so $y = K u = K k_p (r - y)$, giving $y = K k_p r/(1 + K
k_p) = 2/3$. Holding the plant anywhere above zero needs a standing command, and a
proportional controller makes its command out of error alone, so a standing command
means a standing error. Raising $k_p$ shrinks the gap toward zero without reaching it;
removing it takes a term that keeps pushing while any error remains — the integral.
""",
                    },
                    {
                        "q": "Why does adding an integral term remove the steady-state offset that proportional control leaves behind?",
                        "opts": [
                            "The integral averages out the measurement noise, so the controller sees the true error and can cancel it",
                            "The loop can only come to rest when the integral stops changing, and it stops changing only when the error is zero",
                            "The integral raises the effective gain to $k_p + k_i$, which pushes the equilibrium closer to the setpoint",
                            "The integral makes the plant respond faster, so it reaches the setpoint before the proportional term stops pushing",
                        ],
                        "a": 1,
                        "whys": [
                            r"There is no noise in the lab's simulation and the offset is still there under P alone. The integral's job is not smoothing; it is providing a standing command with no standing error.",
                            r"An integral is constant only while its integrand is zero. At rest everything is constant, so the error must be zero: the integrator supplies whatever command holds the plant there.",
                            r"$k_i$ multiplies a different quantity from $k_p$ and the two do not add. A higher proportional gain would shrink the offset without removing it; the integral removes it at any $k_i > 0$.",
                            r"The integral usually makes the loop *slower* to settle, with overshoot. It wins on the final value, not on speed.",
                        ],
                        "why": r"""
With $u = k_p e + k_i \int e$, equilibrium requires every term to stop changing. The
integral stops changing only when $e = 0$, so the loop cannot rest anywhere except on
the setpoint — the integrator holds the standing command that the proportional term
could only produce from a standing error. The cost is momentum: the integral is still
large when the output first arrives, which is the 10% overshoot in the lab's PI run.
""",
                    },
                    {
                        "q": "A PID with output limits $[0, 1]$ and $k_i = 4$ spends five seconds at an unreachable setpoint of 5, then the setpoint drops to 1. Without anti-windup, what happens?",
                        "opts": [
                            "The output falls to 1 within a second, since the clamp kept the command bounded throughout",
                            "The command stays pinned at its maximum for many seconds while the wound-up integral unwinds, and the plant sits at 2",
                            "The loop oscillates between 0 and 2, because the clamp introduces a hard nonlinearity",
                            "The plant overshoots the original setpoint of 5, since the integral accumulated during saturation is finally released all at once",
                        ],
                        "a": 1,
                        "whys": [
                            r"The clamp bounds the *command*, not the integral. The integral kept counting the whole time, and with $k_i = 4$ it holds nearly 70 units of command that must unwind at 0.04 per tick.",
                            r"Error of $-1$ drains the integral at $k_i \times 1 \times \Delta t = 0.04$ per tick; unwinding about 70 takes about 1700 ticks, with the plant at $K \times 1 = 2$ throughout.",
                            r"Nothing oscillates. The command is saturated at 1 for as long as the integral term exceeds the limit, and the plant sits quietly at the ceiling that command allows.",
                            r"The plant cannot exceed $K \times u_{\max} = 2$ whatever the integral holds; the limit is on the actuator. The damage is the long delay, not a burst above 5.",
                        ],
                        "why": r"""
While the command is saturated the integrator keeps accumulating error it can do
nothing about. When the setpoint drops, that stored integral still demands a command
far above the limit, so the clamp holds at the maximum until the negative error has
drained the store — about seventeen seconds in the reading's numbers, with the plant
parked at 2. Conditional integration prevents the store from growing in the first
place: after the same five seconds the integral is exactly zero and the loop is within
2% of the new setpoint in under a second.
""",
                    },
                    {
                        "q": "Which implementation of `update` is the conditional-integration anti-windup the lab asks for?",
                        "opts": [
                            "Form $u$ from a trial integral; commit the trial only if $u$ is within limits, else clamp $u$ and keep the old integral",
                            "Commit the new integral on every call, form $u$ from it, and then clamp $u$ into the actuator limits before returning it to the caller",
                            "Clamp $u$ into the limits, and whenever the clamp was needed reset the integral to zero",
                            "Form $u$ from the committed integral, and skip the clamp entirely when the integral is small",
                        ],
                        "a": 0,
                        "whys": [
                            r"The integral counts only on ticks where counting could have changed the output. On a saturated tick the trial is discarded, so the store never grows while the clamp holds.",
                            r"This is the windup case with a clamp attached. The integral grows on every saturated tick exactly as it would with no limits; the clamp hides the symptom and stores the problem.",
                            r"Resetting throws away the correct standing command as well as the excess. Every time the loop brushes a limit it forgets what it had learned and has to start over, which is its own oscillation.",
                            r"Skipping the clamp sends the actuator a command it cannot honour. The limits are a fact about the hardware and apply to every tick.",
                        ],
                        "why": r"""
The rule in the brief is one `if`: compute `trial = integral + error*dt`, use it to
compute `u`, and commit `integral = trial` only when `out_min <= u <= out_max`;
otherwise leave the integral alone and clamp `u`. Committing before clamping is
windup with extra steps, and resetting on saturation discards the standing command the
integral exists to hold. The lab checks the rule by asserting the integral is still
zero after 500 saturated ticks.
""",
                    },
                    {
                        "q": "A colleague initialises `prev_error = 0.0` instead of `None`. With $k_d = 0.1$ and $\\Delta t = 0.01$, what does the first call for a unit step do?",
                        "opts": [
                            "Nothing unusual: the derivative of a constant error is zero, so the first command is the proportional term alone, as intended",
                            "It adds a derivative term of $0.1 \\times (1 - 0)/0.01 = 10$ to the command, a kick ten times the intended proportional action",
                            "It raises a `ZeroDivisionError`, because there is no time interval yet over which to take a derivative",
                            "It halves the first command, because the derivative term opposes the proportional term on the first sample",
                        ],
                        "a": 1,
                        "whys": [
                            r"The error is not constant on the first call; it appears from nowhere. Compared with a sentinel of 0.0 it has changed by 1 in one tick, and the derivative term sees that as a slope of 100.",
                            r"$(1 - 0)/0.01 = 100$, times $k_d = 0.1$, is 10, added to a proportional term of 1. The reading's example prints 11.0 against 1.0.",
                            r"$\Delta t$ is a fixed constructor argument and never zero; nothing divides by elapsed time. The failure is a wrong number, not an exception.",
                            r"The derivative term has the same sign as the error's change, which on a rising step is positive: it adds to the command rather than opposing it.",
                        ],
                        "why": r"""
A sentinel of `0.0` is a claim that the error was zero one tick ago. On a step from 0
to 1 that makes the measured slope $1/\Delta t = 100$, and $k_d = 0.1$ turns it into a
command of 10 on top of the proportional 1. Using `None` as the flag, as the lab's
`reset` does, lets `update` report zero derivative on the first call and the command
comes out as 1.0. The same kick recurs whenever the setpoint changes suddenly, which
is why many controllers differentiate the measurement rather than the error.
""",
                    },
                    {
                        "q": "A proportional loop on the plant $\\tau = 1$, $K = 2$, $k_p = 1$ is simulated by forward Euler with $\\Delta t = 1.0$ and diverges to enormous values. What is wrong?",
                        "opts": [
                            "The gain $k_p$ is too high for this plant, and the closed loop is genuinely unstable at any step size, however small",
                            "The step exceeds $2\\tau/(1 + K k_p) = 2/3$, so the discretised loop is unstable although the continuous one is not",
                            "The plant model is unstable because $\\tau = 1$ equals $\\Delta t$, which makes the lag term vanish",
                            "Floating-point rounding accumulates over the run and eventually dominates the small step updates",
                        ],
                        "a": 1,
                        "whys": [
                            r"The continuous loop is a first-order lag under proportional control and is stable for every positive $k_p$. The same gains at $\Delta t = 0.01$ settle calmly at $2/3$.",
                            r"Each Euler tick multiplies the error by $1 - \Delta t(1 + K k_p)/\tau$, which at $\Delta t = 1$ is $-2$: the error doubles and flips sign every step.",
                            r"$\tau = \Delta t$ makes the open-loop step land exactly on $K u$ in one tick, which is coarse but not unstable. It is the closed-loop factor that goes past $-1$.",
                            r"Rounding is at the $10^{-16}$ level; a value of $-699050$ after twenty steps is not rounding. It is a geometric growth with ratio $-2$.",
                        ],
                        "why": r"""
Forward Euler on the closed loop gives $e_{k+1} = \big(1 - \Delta t (1 + K
k_p)/\tau\big) e_k$, which is stable only while that factor lies in $(-1, 1)$, i.e.
$\Delta t < 2\tau/(1 + K k_p) = 2/3$ here. At $\Delta t = 0.5$ the factor is $-0.5$
and the loop rings its way in; at $\Delta t = 1.0$ it is $-2$ and every tick doubles
the error. The physical loop is fine. When a simulated controller goes wild, the step
size is the first thing to check, before the gains.
""",
                    },
                ],
            },
            "lab": {
                "title": "A PID loop with anti-windup",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
**`FirstOrderPlant(gain, tau, dt, y0=0.0)`** — one state `y`. `step(u, disturbance=0.0)`
advances by forward Euler and returns the new `y`:

```text
y += (gain*u - y) / tau * dt + disturbance
```

**`PID(kp, ki, kd, dt, out_min=-1e30, out_max=1e30)`** — `reset()` clears
`integral`, `prev_error` (to `None`) and `last_output`. `update(setpoint, measurement)`
returns the command:

```text
error      = setpoint - measurement
derivative = 0 on the very first call, else (error - prev_error) / dt
trial      = integral + error*dt
u          = kp*error + ki*trial + kd*derivative
```

Then the anti-windup rule: if `out_min <= u <= out_max`, commit `integral = trial`;
otherwise **leave `integral` untouched** and clamp `u` into the limits. That one
`if` is the difference between a loop that recovers from saturation in a second
and one that sails past its setpoint for a minute.

**`simulate(plant, controller, setpoint, steps, disturbance=None)`** — returns
`[y0, y1, ..., y_steps]`, i.e. `steps + 1` samples. `disturbance`, when given,
is called as `disturbance(k)` for step index `k` starting at 0.

Four metrics over such a list:

- **`rise_time(ys, dt, setpoint)`** — from the first sample at or above `0.1*setpoint`
  to the first at or above `0.9*setpoint`, in seconds. `None` if either is never reached.
- **`overshoot(ys, setpoint)`** — `(max(ys) - setpoint)/setpoint * 100`, or `0.0` if the peak never exceeds the setpoint.
- **`steady_state_error(ys, setpoint)`** — `abs(setpoint - mean_of_last_tenth)`, the tail being `max(1, len(ys)//10)` samples.
- **`settling_time(ys, dt, setpoint, band=0.02)`** — the time of the first sample after
  which the response never again leaves `+/- band*|setpoint|`. `None` if it is
  still outside at the end.

Sanity anchors with `gain=2, tau=1, dt=0.01, setpoint=1`:

```text
kp=1, ki=0, kd=0, 2000 steps  ->  y settles at 2/3; steady_state_error 1/3; rise_time None
kp=2, ki=5, kd=0, 2000 steps  ->  steady_state_error under 1e-9; overshoot about 10.2%
```
''',
                "files": [{"name": "main.py", "content": r'''
class FirstOrderPlant:
    """tau * dy/dt = -y + gain*u, stepped by forward Euler."""

    def __init__(self, gain, tau, dt, y0=0.0):
        self.gain = float(gain)
        self.tau = float(tau)
        self.dt = float(dt)
        self.y = float(y0)

    def step(self, u, disturbance=0.0):
        """Advance one tick and return the new output."""
        # your code here


class PID:
    """A discrete PID controller with output limits and conditional integration."""

    def __init__(self, kp, ki, kd, dt, out_min=-1e30, out_max=1e30):
        self.kp, self.ki, self.kd = float(kp), float(ki), float(kd)
        self.dt = float(dt)
        self.out_min, self.out_max = float(out_min), float(out_max)
        self.reset()

    def reset(self):
        """Clear the integral, the previous error and the last output."""
        # your code here

    def update(self, setpoint, measurement):
        """Return the (clamped) command, honouring the anti-windup rule."""
        # your code here


def simulate(plant, controller, setpoint, steps, disturbance=None):
    """Closed-loop run; returns steps + 1 samples starting from the initial y."""
    # your code here


def rise_time(ys, dt, setpoint):
    """Seconds from 10% to 90% of setpoint, or None."""
    # your code here


def overshoot(ys, setpoint):
    """Peak excess over setpoint, as a percentage; 0.0 when there is none."""
    # your code here


def steady_state_error(ys, setpoint):
    """abs(setpoint - mean of the final tenth of the samples)."""
    # your code here


def settling_time(ys, dt, setpoint, band=0.02):
    """Time after which the response stays inside the band, or None."""
    # your code here


plant = FirstOrderPlant(2.0, 1.0, 0.01)
pid = PID(2.0, 5.0, 0.0, 0.01)
ys = simulate(plant, pid, 1.0, 2000)
print("final:", ys[-1])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class FirstOrderPlant:
    """tau * dy/dt = -y + gain*u, stepped by forward Euler."""

    def __init__(self, gain, tau, dt, y0=0.0):
        self.gain = float(gain)
        self.tau = float(tau)
        self.dt = float(dt)
        self.y = float(y0)

    def step(self, u, disturbance=0.0):
        """Advance one tick and return the new output."""
        self.y += (self.gain * float(u) - self.y) / self.tau * self.dt + float(disturbance)
        return self.y


class PID:
    """A discrete PID controller with output limits and conditional integration."""

    def __init__(self, kp, ki, kd, dt, out_min=-1e30, out_max=1e30):
        self.kp, self.ki, self.kd = float(kp), float(ki), float(kd)
        self.dt = float(dt)
        self.out_min, self.out_max = float(out_min), float(out_max)
        self.reset()

    def reset(self):
        """Clear the integral, the previous error and the last output."""
        self.integral = 0.0
        self.prev_error = None
        self.last_output = 0.0

    def update(self, setpoint, measurement):
        """Return the (clamped) command, honouring the anti-windup rule."""
        error = float(setpoint) - float(measurement)
        if self.prev_error is None:
            derivative = 0.0
        else:
            derivative = (error - self.prev_error) / self.dt
        trial = self.integral + error * self.dt
        u = self.kp * error + self.ki * trial + self.kd * derivative
        if self.out_min <= u <= self.out_max:
            self.integral = trial
        else:
            u = max(self.out_min, min(self.out_max, u))
        self.prev_error = error
        self.last_output = u
        return u


def simulate(plant, controller, setpoint, steps, disturbance=None):
    """Closed-loop run; returns steps + 1 samples starting from the initial y."""
    ys = [plant.y]
    for k in range(steps):
        u = controller.update(setpoint, plant.y)
        kick = 0.0 if disturbance is None else float(disturbance(k))
        ys.append(plant.step(u, kick))
    return ys


def rise_time(ys, dt, setpoint):
    """Seconds from 10% to 90% of setpoint, or None."""
    low = next((i for i, y in enumerate(ys) if y >= 0.1 * setpoint), None)
    high = next((i for i, y in enumerate(ys) if y >= 0.9 * setpoint), None)
    if low is None or high is None:
        return None
    return (high - low) * dt


def overshoot(ys, setpoint):
    """Peak excess over setpoint, as a percentage; 0.0 when there is none."""
    peak = max(ys)
    if peak <= setpoint:
        return 0.0
    return (peak - setpoint) / setpoint * 100.0


def steady_state_error(ys, setpoint):
    """abs(setpoint - mean of the final tenth of the samples)."""
    tail = ys[-max(1, len(ys) // 10):]
    return abs(setpoint - sum(tail) / len(tail))


def settling_time(ys, dt, setpoint, band=0.02):
    """Time after which the response stays inside the band, or None."""
    tol = band * abs(setpoint)
    index = 0
    for i in range(len(ys) - 1, -1, -1):
        if abs(ys[i] - setpoint) > tol:
            index = i + 1
            break
    if index >= len(ys):
        return None
    return index * dt


plant = FirstOrderPlant(2.0, 1.0, 0.01)
pid = PID(2.0, 5.0, 0.0, 0.01)
ys = simulate(plant, pid, 1.0, 2000)
print("final:", ys[-1])
'''}],
                "hints": [
                    "`update` must compute the *trial* integral, use it in `u`, and only then decide whether to keep it — deciding afterwards is the classic bug.",
                    "`prev_error is None` is the flag for the first call; a `0.0` sentinel would inject a spurious derivative kick of `setpoint/dt`.",
                    "`simulate` returns `steps + 1` values because the initial `plant.y` counts as sample zero.",
                    "For `settling_time`, scan backwards for the last sample outside the band; the answer is the index just after it, or `None` if that runs off the end.",
                ],
                "tests": [
                    {"name": "the plant is a first-order lag", "code": r'''
_p = FirstOrderPlant(2.0, 1.0, 0.01)
_y = _p.step(1.0)
assert abs(_y - 0.02) < 1e-12, f"one step from 0 with u = 1 gives (2*1 - 0)/1*0.01 = 0.02, got {_y!r}"
assert abs(_p.y - 0.02) < 1e-12, "step must also store the new output on the plant"
_y = _p.step(1.0, 0.5)
assert abs(_y - (0.02 + (2.0 - 0.02) * 0.01 + 0.5)) < 1e-12, f"a disturbance adds straight onto y, got {_y!r}"
_settled = FirstOrderPlant(2.0, 1.0, 0.01, 2.0)
assert abs(_settled.step(1.0) - 2.0) < 1e-12, "y = gain*u is the equilibrium: the plant should not move"
'''},
                    {"name": "proportional action leaves an offset", "code": r'''
_p = FirstOrderPlant(2.0, 1.0, 0.01)
_c = PID(1.0, 0.0, 0.0, 0.01)
_ys = simulate(_p, _c, 1.0, 2000)
assert len(_ys) == 2001, f"simulate should return steps + 1 = 2001 samples, got {len(_ys)}"
assert abs(_ys[0]) < 1e-12, "the first sample is the plant's initial output"
assert abs(_ys[-1] - 2.0 / 3.0) < 1e-6, f"K*kp/(1 + K*kp) = 2/3 is the P-only equilibrium, got {_ys[-1]!r}"
assert abs(steady_state_error(_ys, 1.0) - 1.0 / 3.0) < 1e-6, f"steady_state_error gave {steady_state_error(_ys, 1.0)!r}, expected 1/3"
assert overshoot(_ys, 1.0) == 0.0, f"a first-order lag under pure P cannot overshoot, got {overshoot(_ys, 1.0)!r}"
assert rise_time(_ys, 0.01, 1.0) is None, "the response never reaches 90% of the setpoint, so rise_time is None"
'''},
                    {"name": "integral action removes the offset", "code": r'''
_p = FirstOrderPlant(2.0, 1.0, 0.01)
_c = PID(2.0, 5.0, 0.0, 0.01)
_ys = simulate(_p, _c, 1.0, 2000)
assert steady_state_error(_ys, 1.0) < 1e-9, f"with integral action the offset must vanish, got {steady_state_error(_ys, 1.0)!r}"
_os = overshoot(_ys, 1.0)
assert 8.0 < _os < 13.0, f"this tuning overshoots by about 10.2%, got {_os!r}"
_rt = rise_time(_ys, 0.01, 1.0)
assert _rt is not None and 0.2 < _rt < 0.5, f"rise time should be about 0.33 s, got {_rt!r}"
_st = settling_time(_ys, 0.01, 1.0)
assert _st is not None and _rt < _st < 4.0, f"settling time should follow the rise time and be about 1.6 s, got {_st!r}"
'''},
                    {"name": "metrics on hand-built responses", "code": r'''
assert rise_time([0.0, 0.25, 0.5, 0.75, 1.0], 1.0, 1.0) == 3.0, f"10% first at index 1, 90% first at index 4, so 3.0 s; got {rise_time([0.0, 0.25, 0.5, 0.75, 1.0], 1.0, 1.0)!r}"
assert rise_time([0.0, 0.1, 0.2], 1.0, 1.0) is None, "never reaching 90% means None"
assert abs(overshoot([0.0, 0.5, 1.2, 1.0, 1.0], 1.0) - 20.0) < 1e-9, f"a peak of 1.2 against a setpoint of 1 is 20% overshoot, got {overshoot([0.0, 0.5, 1.2, 1.0, 1.0], 1.0)!r}"
assert overshoot([0.0, 0.5, 1.0], 1.0) == 0.0, "touching the setpoint exactly is not overshoot"
assert abs(settling_time([0.0, 0.5, 0.99, 1.0, 1.0], 0.5, 1.0) - 1.0) < 1e-9, f"the last sample outside the 2% band is index 1, so settling time is 1.0 s; got {settling_time([0.0, 0.5, 0.99, 1.0, 1.0], 0.5, 1.0)!r}"
assert settling_time([0.0, 0.5, 0.7], 0.5, 1.0) is None, "still outside the band at the end means None"
assert abs(steady_state_error([0.0] * 9 + [0.8], 1.0) - 0.2) < 1e-9, f"the tail is the last max(1, n//10) = 1 sample, got {steady_state_error([0.0] * 9 + [0.8], 1.0)!r}"
'''},
                    {"name": "anti-windup keeps the integral bounded", "code": r'''
_p = FirstOrderPlant(2.0, 1.0, 0.01)
_c = PID(1.0, 4.0, 0.0, 0.01, 0.0, 1.0)
_ys = simulate(_p, _c, 5.0, 500)
assert max(_ys) <= 2.0 + 1e-9, f"with u clamped at 1 the plant can never exceed gain*u = 2, got a peak of {max(_ys)!r}"
assert abs(_c.integral) < 1e-9, f"the command was saturated at every step, so the integral must never have been committed; it is {_c.integral!r}"
assert abs(_c.last_output - 1.0) < 1e-9, f"the clamped command should sit on out_max = 1.0, got {_c.last_output!r}"
'''},
                    {"name": "and lets the loop recover when the setpoint drops", "code": r'''
_p = FirstOrderPlant(2.0, 1.0, 0.01)
_c = PID(1.0, 4.0, 0.0, 0.01, 0.0, 1.0)
simulate(_p, _c, 5.0, 500)
_after = simulate(_p, _c, 1.0, 1500)
assert abs(_after[-1] - 1.0) < 1e-3, f"after the setpoint drops the loop must settle back on 1.0, got {_after[-1]!r}"
assert steady_state_error(_after, 1.0) < 1e-3, f"a wound-up integral would hold the output at 2.0; steady-state error is {steady_state_error(_after, 1.0)!r}"
'''},
                    {"name": "the loop rejects a sustained disturbance", "code": r'''
_p = FirstOrderPlant(2.0, 1.0, 0.01)
_c = PID(2.0, 5.0, 0.0, 0.01)
_ys = simulate(_p, _c, 1.0, 3000, lambda k: 0.002 if k >= 1000 else 0.0)
assert steady_state_error(_ys, 1.0) < 5e-3, f"integral action must absorb a constant push; residual error {steady_state_error(_ys, 1.0)!r}"
_open = FirstOrderPlant(2.0, 1.0, 0.01)
_drift = [_open.step(0.5, 0.002) for _ in range(3000)]
assert _drift[-1] > 1.19, f"without feedback the same push drags the plant to its own equilibrium of 1.2; it reached {_drift[-1]!r}"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- CAP
    "capstone": {
        "title": "Autonomous delivery agent",
        "brief": r'''
Put the four pillars together. `agent.py` holds the stack; `main.py` runs a
demonstration delivery across a warehouse aisle grid and prints a report.

The world is an occupancy grid of `0`/`1` cells. Cell `(row, col)` has its
centre at the continuous point `x = col`, `y = row`. The robot has a body, so
plan on `inflate(grid, 1)`, but judge collisions against the *raw* grid, using
the cell nearest the robot's true position.

Implement in `agent.py`:

- `inflate(grid, radius)` and `octile(a, b)` as in the planning lab
- `plan(grid, start, goal)` — A*, 8-connected, no corner cutting; returns the
  cell path or `None`. Occupied endpoints give `None`.
- `Localiser(x, y, var, q, r)` — two decoupled scalar Kalman filters, one per
  axis. `predict(dx, dy)` shifts the mean by the commanded displacement and adds
  `q` to each variance; `update(zx, zy)` folds in a noisy position fix;
  `estimate()` returns `(x, y)`; `uncertainty()` returns `px + py`.
- `PID(kp, ki, kd, dt, out_min, out_max)` — as in the control lab, with the same
  conditional-integration anti-windup.
- `run_trial(grid, start, goal, seed=7, **overrides)` — one seeded delivery.
- `run_trials(grid, start, goal, trials=20, seed=7, **overrides)` — the summary.

`DEFAULTS` (override any of them through `**overrides`):

```text
dt 0.1   v_max 1.5   sensor_sigma 0.25   disturbance_sigma 0.03
waypoint_tol 0.35   goal_tol 0.25   max_steps 900   kp 2.0   ki 0.3   kd 0.05
```

One tick of `run_trial`, in this exact order — the RNG draw order is part of
the contract:

1. `loc.update(true_x + rng.gauss(0, sensor_sigma), true_y + rng.gauss(0, sensor_sigma))`
2. read the estimate; advance the waypoint index while the *current* waypoint is
   nearer than `waypoint_tol` to the estimate and it is not the last one
3. `vx = pid_x.update(target_x, est_x)`, `vy = pid_y.update(target_y, est_y)`;
   if `hypot(vx, vy) > v_max`, scale both down so the speed is exactly `v_max`
4. move the truth: `true += v*dt + rng.gauss(0, disturbance_sigma)` per axis,
   accumulating `travelled`
5. `loc.predict(vx*dt, vy*dt)`
6. collide-check the nearest raw-grid cell (`round(true_y)`, `round(true_x)`);
   off-grid counts as a collision
7. succeed when the true position is within `goal_tol` of the final waypoint

`run_trial` returns a dict with keys `success`, `reason`, `steps`, `travelled`,
`final_error`, `waypoints`. `reason` is one of `"delivered"`, `"collision"`,
`"timeout"`, `"no-path"`. `run_trials` runs seeds `seed, seed+1, ...` and
returns `trials`, `successes`, `success_rate`, `mean_steps`, `mean_travelled`
(the means over *successful* trials only, or `None` when there are none) and
`failures`, the sorted set of distinct failure reasons.
''',
        "deliverables": [
            "`agent.py` — the full stack: inflation, A*, the Kalman localiser, the PID controller and the trial harness",
            "`main.py` — plans one delivery, runs it, and prints the route length, the outcome and a 12-trial success rate",
            "A working `run_trial` that reports every one of the four failure reasons on the appropriate world",
            "Deterministic behaviour: the same seed reproduces the same trial exactly, every time",
            "Feedback taken from the *estimate*, never from the true position — the controller may not read ground truth",
            "A 12-trial sweep on the supplied `WAREHOUSE` grid that delivers on every seed",
        ],
        "constraints": [
            "`agent.py` must define names only — importing it prints nothing and runs no simulation",
            "Standard library only; every random draw comes from a `random.Random(seed)` created inside the trial",
            "The controller sees `Localiser.estimate()` alone; reading the true pose in the control path is a fail",
            "Plan on the inflated grid, collide against the raw grid — mixing the two hides the bug that inflation exists to prevent",
            "A 20-trial sweep must complete in well under a second: no per-step allocation of the whole grid",
        ],
        "rubric": [
            {"criterion": "Autonomy stack correctness", "weight": 40,
             "evidence": "Planner, filter and controller each pass their own checks, and the assembled agent delivers on every seed of the sweep."},
            {"criterion": "Estimation discipline", "weight": 20,
             "evidence": "Localiser variance shrinks under measurement and grows under prediction; the control path touches only the estimate."},
            {"criterion": "Failure handling", "weight": 20,
             "evidence": "no-path, collision and timeout are each reported distinctly, with the step and travel figures that go with them."},
            {"criterion": "Determinism and cost", "weight": 10,
             "evidence": "Identical seeds give byte-identical dicts; twenty trials finish in a fraction of a second."},
            {"criterion": "Structure and clarity", "weight": 10,
             "evidence": "agent.py is import-clean and documented; main.py is a thin demonstration over it."},
        ],
        "runtime": "python",
        "minutes": 240,
        "hints": [
            "Build it in the order the tick runs: get `plan` right on the inflated grid first, then drive the robot with the *true* pose to prove the waypoint logic, and only then insert the localiser between sensor and controller.",
            "Waypoint advance is a `while`, not an `if` — a fast robot can retire two waypoints in one tick, and stopping early makes it chase a point it has already passed.",
            "Scale the velocity vector, never each axis independently: clamping `vx` and `vy` separately bends the heading and walks the robot into shelves on diagonals.",
            "`Localiser.predict` must add the *commanded* displacement `vx*dt`, not the realised one — the realised one includes the disturbance the filter is supposed to discover.",
            "If trials time out, check the goal test: it compares the true position to the last waypoint, and `goal_tol` is smaller than `waypoint_tol` on purpose.",
        ],
        "files": [
            {"name": "agent.py", "content": r'''
import heapq
import math
import random

SQRT2 = math.sqrt(2.0)

DEFAULTS = {
    "dt": 0.1,
    "v_max": 1.5,
    "sensor_sigma": 0.25,
    "disturbance_sigma": 0.03,
    "waypoint_tol": 0.35,
    "goal_tol": 0.25,
    "max_steps": 900,
    "kp": 2.0,
    "ki": 0.3,
    "kd": 0.05,
}


def inflate(grid, radius):
    """A new grid with every obstacle grown by radius cells."""
    # your code here


def octile(a, b):
    """Admissible 8-connected heuristic between two (row, col) cells."""
    # your code here


def plan(grid, start, goal):
    """A* cell path from start to goal, or None."""
    # your code here


class Localiser:
    """Two decoupled scalar Kalman filters, one per axis."""

    def __init__(self, x, y, var=1.0, q=0.01, r=0.25):
        self.x, self.y = float(x), float(y)
        self.px = self.py = float(var)
        self.q, self.r = float(q), float(r)

    def predict(self, dx, dy):
        """Shift the mean by a commanded displacement and grow the variance."""
        # your code here

    def update(self, zx, zy):
        """Fold in a noisy position fix on each axis."""
        # your code here

    def estimate(self):
        """The current (x, y) mean."""
        # your code here

    def uncertainty(self):
        """px + py — one scalar summary of the belief's width."""
        # your code here


class PID:
    """Discrete PID with output limits and conditional-integration anti-windup."""

    def __init__(self, kp, ki, kd, dt, out_min=-1e30, out_max=1e30):
        self.kp, self.ki, self.kd = float(kp), float(ki), float(kd)
        self.dt = float(dt)
        self.out_min, self.out_max = float(out_min), float(out_max)
        self.integral = 0.0
        self.prev_error = None

    def update(self, setpoint, measurement):
        """Return the clamped command."""
        # your code here


def run_trial(grid, start, goal, seed=7, **overrides):
    """One seeded delivery. See the brief for the tick order and the result keys."""
    # your code here


def run_trials(grid, start, goal, trials=20, seed=7, **overrides):
    """Summary over consecutive seeds."""
    # your code here


WAREHOUSE = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
'''},
            {"name": "main.py", "content": r'''
from agent import WAREHOUSE, inflate, plan, run_trial, run_trials

route = plan(inflate(WAREHOUSE, 1), (0, 0), (12, 14))
print("waypoints:", len(route) if route else None)

trial = run_trial(WAREHOUSE, (0, 0), (12, 14), seed=7)
print("outcome:", trial["reason"], "in", trial["steps"], "ticks")

summary = run_trials(WAREHOUSE, (0, 0), (12, 14), 12, 7)
print("success rate:", summary["success_rate"])
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "agent.py", "content": r'''
import heapq
import math
import random

SQRT2 = math.sqrt(2.0)

DEFAULTS = {
    "dt": 0.1,
    "v_max": 1.5,
    "sensor_sigma": 0.25,
    "disturbance_sigma": 0.03,
    "waypoint_tol": 0.35,
    "goal_tol": 0.25,
    "max_steps": 900,
    "kp": 2.0,
    "ki": 0.3,
    "kd": 0.05,
}


def inflate(grid, radius):
    """A new grid with every obstacle grown by radius cells."""
    rows, cols = len(grid), len(grid[0])
    out = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if not grid[r][c]:
                continue
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        out[rr][cc] = 1
    return out


def octile(a, b):
    """Admissible 8-connected heuristic between two (row, col) cells."""
    dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dr + dc) + (SQRT2 - 2.0) * min(dr, dc)


def plan(grid, start, goal):
    """A* cell path from start to goal, or None."""
    rows, cols = len(grid), len(grid[0])
    start, goal = tuple(start), tuple(goal)
    for cell in (start, goal):
        if not (0 <= cell[0] < rows and 0 <= cell[1] < cols):
            raise ValueError(f"cell {cell!r} is outside the {rows}x{cols} grid")
    if grid[start[0]][start[1]] or grid[goal[0]][goal[1]]:
        return None
    frontier = [(octile(start, goal), 0, start)]
    came, cost, settled, tie = {}, {start: 0.0}, set(), 0
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node in settled:
            continue
        settled.add(node)
        if node == goal:
            path = [node]
            while path[-1] in came:
                path.append(came[path[-1]])
            path.reverse()
            return path
        r, c = node
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if not (0 <= rr < rows and 0 <= cc < cols) or grid[rr][cc]:
                    continue
                if dr and dc and (grid[r][cc] or grid[rr][c]):
                    continue
                g = cost[node] + (SQRT2 if dr and dc else 1.0)
                if g < cost.get((rr, cc), float("inf")) - 1e-12:
                    cost[(rr, cc)] = g
                    came[(rr, cc)] = node
                    tie += 1
                    heapq.heappush(frontier, (g + octile((rr, cc), goal), tie, (rr, cc)))
    return None


class Localiser:
    """Two decoupled scalar Kalman filters, one per axis."""

    def __init__(self, x, y, var=1.0, q=0.01, r=0.25):
        self.x, self.y = float(x), float(y)
        self.px = self.py = float(var)
        self.q, self.r = float(q), float(r)

    def predict(self, dx, dy):
        """Shift the mean by a commanded displacement and grow the variance."""
        self.x += dx
        self.y += dy
        self.px += self.q
        self.py += self.q

    def update(self, zx, zy):
        """Fold in a noisy position fix on each axis."""
        kx = self.px / (self.px + self.r)
        self.x += kx * (zx - self.x)
        self.px = (1.0 - kx) * self.px
        ky = self.py / (self.py + self.r)
        self.y += ky * (zy - self.y)
        self.py = (1.0 - ky) * self.py

    def estimate(self):
        """The current (x, y) mean."""
        return (self.x, self.y)

    def uncertainty(self):
        """px + py — one scalar summary of the belief's width."""
        return self.px + self.py


class PID:
    """Discrete PID with output limits and conditional-integration anti-windup."""

    def __init__(self, kp, ki, kd, dt, out_min=-1e30, out_max=1e30):
        self.kp, self.ki, self.kd = float(kp), float(ki), float(kd)
        self.dt = float(dt)
        self.out_min, self.out_max = float(out_min), float(out_max)
        self.integral = 0.0
        self.prev_error = None

    def update(self, setpoint, measurement):
        """Return the clamped command."""
        error = float(setpoint) - float(measurement)
        if self.prev_error is None:
            derivative = 0.0
        else:
            derivative = (error - self.prev_error) / self.dt
        trial = self.integral + error * self.dt
        u = self.kp * error + self.ki * trial + self.kd * derivative
        if self.out_min <= u <= self.out_max:
            self.integral = trial
        else:
            u = max(self.out_min, min(self.out_max, u))
        self.prev_error = error
        return u


def _result(success, reason, steps, travelled, final_error, waypoints):
    return {"success": success, "reason": reason, "steps": steps,
            "travelled": travelled, "final_error": final_error,
            "waypoints": waypoints}


def run_trial(grid, start, goal, seed=7, **overrides):
    """One seeded delivery. See the brief for the tick order and the result keys."""
    cfg = dict(DEFAULTS)
    cfg.update(overrides)
    rng = random.Random(seed)
    cells = plan(inflate(grid, 1), tuple(start), tuple(goal))
    if cells is None:
        return _result(False, "no-path", 0, 0.0, float("inf"), 0)

    route = [(float(c), float(r)) for r, c in cells]
    dt = cfg["dt"]
    true_x, true_y = route[0]
    loc = Localiser(true_x, true_y, 0.5, 0.02, cfg["sensor_sigma"] ** 2)
    pid_x = PID(cfg["kp"], cfg["ki"], cfg["kd"], dt, -cfg["v_max"], cfg["v_max"])
    pid_y = PID(cfg["kp"], cfg["ki"], cfg["kd"], dt, -cfg["v_max"], cfg["v_max"])
    rows, cols = len(grid), len(grid[0])
    index = 0
    travelled = 0.0

    for step in range(1, cfg["max_steps"] + 1):
        loc.update(true_x + rng.gauss(0.0, cfg["sensor_sigma"]),
                   true_y + rng.gauss(0.0, cfg["sensor_sigma"]))
        est_x, est_y = loc.estimate()
        while (index < len(route) - 1
               and math.hypot(route[index][0] - est_x,
                              route[index][1] - est_y) < cfg["waypoint_tol"]):
            index += 1
        target_x, target_y = route[index]

        vx = pid_x.update(target_x, est_x)
        vy = pid_y.update(target_y, est_y)
        speed = math.hypot(vx, vy)
        if speed > cfg["v_max"]:
            scale = cfg["v_max"] / speed
            vx *= scale
            vy *= scale

        next_x = true_x + vx * dt + rng.gauss(0.0, cfg["disturbance_sigma"])
        next_y = true_y + vy * dt + rng.gauss(0.0, cfg["disturbance_sigma"])
        travelled += math.hypot(next_x - true_x, next_y - true_y)
        true_x, true_y = next_x, next_y
        loc.predict(vx * dt, vy * dt)

        cell_r, cell_c = int(round(true_y)), int(round(true_x))
        error = math.hypot(true_x - route[-1][0], true_y - route[-1][1])
        if not (0 <= cell_r < rows and 0 <= cell_c < cols) or grid[cell_r][cell_c]:
            return _result(False, "collision", step, travelled, error, len(route))
        if error <= cfg["goal_tol"]:
            return _result(True, "delivered", step, travelled, error, len(route))

    error = math.hypot(true_x - route[-1][0], true_y - route[-1][1])
    return _result(False, "timeout", cfg["max_steps"], travelled, error, len(route))


def run_trials(grid, start, goal, trials=20, seed=7, **overrides):
    """Summary over consecutive seeds."""
    results = [run_trial(grid, start, goal, seed=seed + i, **overrides)
               for i in range(trials)]
    good = [r for r in results if r["success"]]
    return {
        "trials": trials,
        "successes": len(good),
        "success_rate": len(good) / trials,
        "mean_steps": (sum(r["steps"] for r in good) / len(good)) if good else None,
        "mean_travelled": (sum(r["travelled"] for r in good) / len(good)) if good else None,
        "failures": sorted({r["reason"] for r in results if not r["success"]}),
    }


WAREHOUSE = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
'''},
            {"name": "main.py", "content": r'''
from agent import WAREHOUSE, inflate, plan, run_trial, run_trials

route = plan(inflate(WAREHOUSE, 1), (0, 0), (12, 14))
print("waypoints:", len(route) if route else None)

trial = run_trial(WAREHOUSE, (0, 0), (12, 14), seed=7)
print("outcome:", trial["reason"], "in", trial["steps"], "ticks")
print("travelled:", round(trial["travelled"], 2))

summary = run_trials(WAREHOUSE, (0, 0), (12, 14), 12, 7)
print("success rate:", summary["success_rate"])
print("mean ticks:", round(summary["mean_steps"], 1))
'''},
        ],
        "tests": [
            {"name": "the planner respects inflation", "code": r'''
from agent import WAREHOUSE, inflate, octile, plan
import math
_grown = inflate(WAREHOUSE, 1)
assert WAREHOUSE[2][2] == 1 and WAREHOUSE[1][2] == 0, "inflate must not mutate the grid it was given"
assert _grown[1][2] == 1 and _grown[3][5] == 1, "shelves must grow by one cell in every direction"
assert _grown[4][7] == 0, "the central aisle at column 7 must survive inflation"
_route = plan(_grown, (0, 0), (12, 14))
assert _route is not None, "the warehouse has a route from (0, 0) to (12, 14) on the inflated grid"
assert _route[0] == (0, 0) and _route[-1] == (12, 14), f"route runs {_route[0]!r}..{_route[-1]!r}"
for _r, _c in _route:
    assert _grown[_r][_c] == 0, f"cell {(_r, _c)!r} on the route is occupied after inflation"
for _a, _b in zip(_route, _route[1:]):
    assert max(abs(_a[0] - _b[0]), abs(_a[1] - _b[1])) == 1, f"{_a!r} and {_b!r} are not adjacent"
assert abs(octile((0, 0), (12, 14)) - (26.0 - 12.0 * (2.0 - math.sqrt(2.0)))) < 1e-9, "octile disagrees with (dr+dc) + (sqrt2-2)*min(dr,dc)"
'''},
            {"name": "the planner refuses the impossible", "code": r'''
from agent import plan, inflate
_wall = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
assert plan(_wall, (0, 0), (0, 2)) is None, "a full-height wall blocks the crossing"
assert plan(_wall, (0, 1), (0, 2)) is None, "an occupied start has no route"
assert plan(_wall, (0, 0), (1, 1)) is None, "an occupied goal has no route"
assert plan([[0, 0], [0, 0]], (1, 1), (1, 1)) == [(1, 1)], "start == goal is a one-cell route"
_seam = [[0, 1], [1, 0]]
assert plan(_seam, (0, 0), (1, 1)) is None, "a diagonal seam between two obstacles is not passable"
'''},
            {"name": "the localiser sharpens on evidence and blurs on motion", "code": r'''
from agent import Localiser
_loc = Localiser(0.0, 0.0, var=1.0, q=0.01, r=0.25)
_before = _loc.uncertainty()
assert abs(_before - 2.0) < 1e-12, f"two axes at variance 1.0 give uncertainty 2.0, got {_before!r}"
_loc.update(1.0, 2.0)
_after = _loc.uncertainty()
assert _after < _before, f"a measurement must reduce uncertainty: {_before!r} -> {_after!r}"
assert abs(_loc.px - 0.2) < 1e-12, f"1*(1/(1+0.25))... px should be 1 - 1/1.25 = 0.2, got {_loc.px!r}"
_ex, _ey = _loc.estimate()
assert abs(_ex - 0.8) < 1e-12 and abs(_ey - 1.6) < 1e-12, f"gain 0.8 on a measurement of (1, 2) gives (0.8, 1.6), got {(_ex, _ey)!r}"
_loc.predict(0.5, -0.5)
_ex, _ey = _loc.estimate()
assert abs(_ex - 1.3) < 1e-12 and abs(_ey - 1.1) < 1e-12, f"predict shifts the mean by the commanded step, got {(_ex, _ey)!r}"
assert abs(_loc.uncertainty() - (_after + 0.02)) < 1e-12, "predict adds q to each axis variance"
_steady = Localiser(0.0, 0.0, 1.0, 0.0, 1.0)
for _i in range(50):
    _steady.update(1.0, 1.0)
assert abs(_steady.px - 1.0 / 51.0) < 1e-12, f"with q = 0 the variance falls as 1/(1+n); after 50 fixes expected {1.0 / 51.0!r}, got {_steady.px!r}"
'''},
            {"name": "the controller clamps and does not wind up", "code": r'''
from agent import PID
_pid = PID(2.0, 0.0, 0.0, 0.1, -1.5, 1.5)
assert abs(_pid.update(1.0, 0.0) - 1.5) < 1e-12, f"kp*error = 2.0 exceeds out_max, so the command clamps to 1.5; got {_pid.update(1.0, 0.0)!r}"
_pid2 = PID(2.0, 0.3, 0.05, 0.1, -1.5, 1.5)
assert abs(_pid2.update(0.1, 0.0) - (2.0 * 0.1 + 0.3 * 0.01)) < 1e-12, "the first call has no derivative term"
_wind = PID(1.0, 4.0, 0.0, 0.1, -1.0, 1.0)
for _i in range(50):
    _wind.update(5.0, 0.0)
assert abs(_wind.integral) < 1e-12, f"every command saturated, so the integral must never be committed; it is {_wind.integral!r}"
'''},
            {"name": "one delivery, start to finish", "code": r'''
from agent import WAREHOUSE, run_trial
_t = run_trial(WAREHOUSE, (0, 0), (12, 14), seed=7)
assert set(_t) == {"success", "reason", "steps", "travelled", "final_error", "waypoints"}, f"unexpected result keys: {sorted(_t)!r}"
assert _t["success"] is True and _t["reason"] == "delivered", f"seed 7 should deliver, got {_t!r}"
assert _t["final_error"] <= 0.25 + 1e-9, f"a delivery ends within goal_tol; final_error is {_t['final_error']!r}"
assert 50 < _t["steps"] < 500, f"the run should take a couple of hundred ticks, got {_t['steps']!r}"
assert 20.0 < _t["travelled"] < 45.0, f"the route is about 26 units long; travelled {_t['travelled']!r}"
assert _t["waypoints"] > 20, f"the planned route has more than 20 cells, got {_t['waypoints']!r}"
'''},
            {"name": "the trial is deterministic in its seed", "code": r'''
from agent import WAREHOUSE, run_trial
_a = run_trial(WAREHOUSE, (0, 0), (12, 14), seed=7)
_b = run_trial(WAREHOUSE, (0, 0), (12, 14), seed=7)
assert _a == _b, "the same seed must reproduce the trial exactly — build the RNG inside run_trial"
_c = run_trial(WAREHOUSE, (0, 0), (12, 14), seed=8)
assert _c["success"] is True, f"seed 8 should also deliver, got {_c!r}"
assert _c != _a, "a different seed must give a different realisation of the noise"
'''},
            {"name": "every failure mode reports itself", "code": r'''
from agent import WAREHOUSE, run_trial
_wall = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
_np = run_trial(_wall, (0, 0), (0, 2), seed=7)
assert _np["reason"] == "no-path" and _np["success"] is False, f"expected a no-path result, got {_np!r}"
assert _np["steps"] == 0 and _np["travelled"] == 0.0 and _np["waypoints"] == 0, f"nothing was driven, so the counters stay at zero: {_np!r}"
_to = run_trial(WAREHOUSE, (0, 0), (12, 14), seed=7, max_steps=20)
assert _to["reason"] == "timeout" and _to["steps"] == 20, f"a 20-tick budget cannot reach the far corner: {_to!r}"
assert _to["final_error"] > 0.25, "a timeout ends short of the goal"
_crash = run_trial(WAREHOUSE, (0, 0), (12, 14), seed=3, disturbance_sigma=3.0)
assert _crash["success"] is False and _crash["reason"] in ("collision", "timeout"), f"a violent disturbance must not be reported as a delivery: {_crash!r}"
'''},
            {"name": "the sweep delivers on every seed", "code": r'''
from agent import WAREHOUSE, run_trials
_s = run_trials(WAREHOUSE, (0, 0), (12, 14), 12, 7)
assert _s["trials"] == 12 and _s["successes"] == 12, f"all twelve seeds should deliver, got {_s!r}"
assert _s["success_rate"] == 1.0, f"success_rate is {_s['success_rate']!r}, expected 1.0"
assert _s["failures"] == [], f"no failures expected, got {_s['failures']!r}"
assert 100.0 < _s["mean_steps"] < 400.0, f"mean_steps of {_s['mean_steps']!r} is outside the plausible band"
assert 20.0 < _s["mean_travelled"] < 45.0, f"mean_travelled of {_s['mean_travelled']!r} is outside the plausible band"
'''},
            {"name": "the summary survives a world with no route", "code": r'''
from agent import run_trials
_wall = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
_s = run_trials(_wall, (0, 0), (0, 2), 4, 7)
assert _s["successes"] == 0 and _s["success_rate"] == 0.0, f"nothing can succeed here, got {_s!r}"
assert _s["mean_steps"] is None and _s["mean_travelled"] is None, "means over an empty set are None, not 0 and not a ZeroDivisionError"
assert _s["failures"] == ["no-path"], f"expected exactly ['no-path'], got {_s['failures']!r}"
'''},
            {"name": "twenty trials cost almost nothing", "code": r'''
import time
from agent import WAREHOUSE, run_trials
_t0 = time.time()
_s = run_trials(WAREHOUSE, (0, 0), (12, 14), 20, 100)
_elapsed = time.time() - _t0
assert _s["success_rate"] == 1.0, f"seeds 100..119 should all deliver, got {_s['success_rate']!r}"
assert _elapsed < 5.0, f"twenty trials took {_elapsed!r}s — well over the budget"
'''},
            {"name": "agent.py is a library, main.py is the demonstration", "code": r'''
_src = open("agent.py").read()
assert "print(" not in _src, "agent.py must define names only; the printing belongs in main.py"
assert "waypoints:" in _out, f"main.py should report the route size; stdout was {_out!r}"
assert "success rate:" in _out, f"main.py should report the sweep; stdout was {_out!r}"
assert "delivered" in _out, f"the demonstration delivery should succeed; stdout was {_out!r}"
'''},
        ],
    },
}
