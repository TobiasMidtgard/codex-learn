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
