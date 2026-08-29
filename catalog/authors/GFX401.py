"""GFX401 — Computer Graphics & Visualization. Author module."""

COURSE = {
    "id": "GFX401",
    "title": "Computer Graphics & Visualization",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["MA121", "CS201"],
    "stack": ["GLSL (reference)", "Python", "Canvas"],
    "credits": 10,
    "hours": 150,
    "icon": "◩",
    "summary": (
        "The pipeline built from the bottom up, with no graphics library underneath. "
        "You compose 4x4 homogeneous transforms and project a cube, rasterise lines and "
        "triangles with a z-buffer and a watertight fill rule, evaluate Lambert and "
        "Blinn-Phong under gamma-correct encoding, and finish with a recursive ray "
        "tracer that writes a PPM of a lit, shadowed, reflective scene."
    ),
    "outcomes": [
        "Compose model, view and projection as 4x4 matrices and predict the effect of their order",
        "Derive the perspective matrix and explain what the divide by w does to depth",
        "Rasterise lines with integer arithmetic and triangles with barycentric edge functions",
        "Apply a top-left fill rule and prove a shared edge is neither dropped nor drawn twice",
        "Evaluate Lambert diffuse and Blinn-Phong specular terms and encode them for a display",
        "Intersect rays with spheres and planes, and use the results for shadow and reflection rays",
        "Assess a rendered image against pixel statistics rather than a golden byte comparison",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone software renderer (60%).",
    "reading": [
        "Marschner & Shirley, *Fundamentals of Computer Graphics*, 5th ed. — chapters 6-8 and 13",
        "Pharr, Jakob & Humphreys, *Physically Based Rendering*, 4th ed. — chapters 3 and 5",
        "Blinn, 'Models of Light Reflection for Computer Synthesized Pictures', *SIGGRAPH* 1977",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "The transform stack",
            "summary": "Homogeneous coordinates, composition order, and the perspective divide.",
            "concepts": [
                "A point is (x, y, z, 1) and a direction is (x, y, z, 0); the fourth slot is what makes translation linear",
                "Column-vector convention: v' = M v, so the matrix written last is applied first",
                "Rotations are orthogonal with determinant +1; their inverse is their transpose",
                "Matrix multiplication is associative but not commutative — translate-then-rotate is a different object",
                "The projection matrix does not project; the divide by w does",
                "Perspective maps the near plane to -1 and the far plane to +1, non-linearly in between",
                "Depth precision is worst far from the eye, which is why the near plane must not be tiny",
            ],
            "lab": {
                "title": "4x4 transforms and a projected cube",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Matrices are lists of four rows of four floats, row-major, applied to column
vectors. `identity()` and the `CUBE` corner list are given.

**`translate(tx, ty, tz)`**, **`scale(sx, sy, sz)`** — identity with the fourth
column, respectively the diagonal, filled in.

**`rotate_x(theta)`**, **`rotate_y(theta)`**, **`rotate_z(theta)`** — right-handed
rotations by `theta` radians. For `rotate_z`, row 0 is `(cos, -sin, 0, 0)` and
row 1 is `(sin, cos, 0, 0)`; `rotate_x` acts on rows 1 and 2 the same way, and
`rotate_y` puts `+sin` at `[0][2]` and `-sin` at `[2][0]`.

**`matmul(a, b)`** — the 4x4 product. Anything that is not 4x4 raises `ValueError`.

**`compose(*matrices)`** — left-to-right product, so `compose(A, B, C)` is
`A @ B @ C` and `C` is applied to the point first.

**`apply(m, point)`** — transform a 3-tuple, then divide by `w`. A point that is
not three numbers raises `ValueError`, and so does a `w` whose magnitude is below
`1e-12` — that point sits on the plane of the eye and has no image.

**`transform_points(m, points)`** — `apply` over a list.

**`perspective(fovy_deg, aspect, near, far)`** — the standard OpenGL frustum with
`f = 1 / tan(radians(fovy) / 2)`:

```text
[ f/aspect   0        0                   0                 ]
[ 0          f        0                   0                 ]
[ 0          0        (far+near)/(near-far)  2*far*near/(near-far) ]
[ 0          0       -1                   0                 ]
```

Raise `ValueError` unless `0 < fovy_deg < 180`, `aspect > 0` and `0 < near < far`.

## Checks worth knowing before you start

```text
apply(rotate_z(pi/2), (1, 0, 0))              ->  (0, 1, 0)
apply(compose(translate(1,0,0), rotate_z(pi/2)), (1,0,0)) -> (1, 1, 0)
apply(compose(rotate_z(pi/2), translate(1,0,0)), (1,0,0)) -> (0, 2, 0)
apply(perspective(90, 1, 1, 100), (0, 0, -1))   ->  z = -1
apply(perspective(90, 1, 1, 100), (0, 0, -100)) ->  z = +1
apply(perspective(90, 1, 1, 100), (1, 1, -2))   ->  (0.5, 0.5, ...)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math

CUBE = [(x, y, z) for x in (-1.0, 1.0) for y in (-1.0, 1.0) for z in (-1.0, 1.0)]


def identity():
    """The 4x4 identity."""
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def translate(tx, ty, tz):
    """Translation by (tx, ty, tz)."""
    # your code here


def scale(sx, sy, sz):
    """Non-uniform scale."""
    # your code here


def rotate_x(theta):
    """Right-handed rotation about the x axis, theta in radians."""
    # your code here


def rotate_y(theta):
    """Right-handed rotation about the y axis, theta in radians."""
    # your code here


def rotate_z(theta):
    """Right-handed rotation about the z axis, theta in radians."""
    # your code here


def matmul(a, b):
    """The 4x4 matrix product a @ b."""
    # your code here


def compose(*matrices):
    """Left-to-right product; the last matrix is applied to the point first."""
    # your code here


def apply(m, point):
    """Transform a 3-tuple and divide by w."""
    # your code here


def transform_points(m, points):
    """apply over a list of points."""
    # your code here


def perspective(fovy_deg, aspect, near, far):
    """The OpenGL perspective frustum matrix."""
    # your code here


mvp = compose(perspective(60.0, 1.0, 0.1, 50.0), translate(0.0, 0.0, -5.0))
corners = transform_points(mvp, CUBE)
print("projected corners:", len(corners))
print(f"near-face x: {corners[1][0]:.6f}   far-face x: {corners[0][0]:.6f}")
print(f"near-face z: {corners[1][2]:.6f}   far-face z: {corners[0][2]:.6f}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

CUBE = [(x, y, z) for x in (-1.0, 1.0) for y in (-1.0, 1.0) for z in (-1.0, 1.0)]


def identity():
    """The 4x4 identity."""
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def translate(tx, ty, tz):
    """Translation by (tx, ty, tz)."""
    m = identity()
    m[0][3] = float(tx)
    m[1][3] = float(ty)
    m[2][3] = float(tz)
    return m


def scale(sx, sy, sz):
    """Non-uniform scale."""
    m = identity()
    m[0][0] = float(sx)
    m[1][1] = float(sy)
    m[2][2] = float(sz)
    return m


def rotate_x(theta):
    """Right-handed rotation about the x axis, theta in radians."""
    c, s = math.cos(theta), math.sin(theta)
    m = identity()
    m[1][1] = c
    m[1][2] = -s
    m[2][1] = s
    m[2][2] = c
    return m


def rotate_y(theta):
    """Right-handed rotation about the y axis, theta in radians."""
    c, s = math.cos(theta), math.sin(theta)
    m = identity()
    m[0][0] = c
    m[0][2] = s
    m[2][0] = -s
    m[2][2] = c
    return m


def rotate_z(theta):
    """Right-handed rotation about the z axis, theta in radians."""
    c, s = math.cos(theta), math.sin(theta)
    m = identity()
    m[0][0] = c
    m[0][1] = -s
    m[1][0] = s
    m[1][1] = c
    return m


def matmul(a, b):
    """The 4x4 matrix product a @ b."""
    if len(a) != 4 or len(b) != 4:
        raise ValueError("both operands must be 4x4")
    if any(len(row) != 4 for row in a) or any(len(row) != 4 for row in b):
        raise ValueError("both operands must be 4x4")
    out = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            total = 0.0
            for k in range(4):
                total += a[i][k] * b[k][j]
            out[i][j] = total
    return out


def compose(*matrices):
    """Left-to-right product; the last matrix is applied to the point first."""
    result = identity()
    for m in matrices:
        result = matmul(result, m)
    return result


def apply(m, point):
    """Transform a 3-tuple and divide by w."""
    if len(point) != 3:
        raise ValueError("a point has three coordinates")
    x, y, z = point
    out = [m[i][0] * x + m[i][1] * y + m[i][2] * z + m[i][3] for i in range(4)]
    w = out[3]
    if abs(w) < 1e-12:
        raise ValueError("point projects to w = 0 and has no image")
    return (out[0] / w, out[1] / w, out[2] / w)


def transform_points(m, points):
    """apply over a list of points."""
    return [apply(m, p) for p in points]


def perspective(fovy_deg, aspect, near, far):
    """The OpenGL perspective frustum matrix."""
    if not 0.0 < fovy_deg < 180.0:
        raise ValueError("fovy must lie strictly between 0 and 180 degrees")
    if aspect <= 0.0:
        raise ValueError("aspect must be positive")
    if near <= 0.0 or far <= near:
        raise ValueError("need 0 < near < far")
    f = 1.0 / math.tan(math.radians(fovy_deg) / 2.0)
    m = [[0.0] * 4 for _ in range(4)]
    m[0][0] = f / aspect
    m[1][1] = f
    m[2][2] = (far + near) / (near - far)
    m[2][3] = 2.0 * far * near / (near - far)
    m[3][2] = -1.0
    return m


mvp = compose(perspective(60.0, 1.0, 0.1, 50.0), translate(0.0, 0.0, -5.0))
corners = transform_points(mvp, CUBE)
print("projected corners:", len(corners))
print(f"near-face x: {corners[1][0]:.6f}   far-face x: {corners[0][0]:.6f}")
print(f"near-face z: {corners[1][2]:.6f}   far-face z: {corners[0][2]:.6f}")
'''}],
                "hints": [
                    "Build every transform by starting from `identity()` and overwriting the few entries that differ — it keeps the bottom row correct for free.",
                    "`compose` folds left: start from `identity()` and repeatedly `result = matmul(result, m)`. Composition order is the whole point of the lab, so check it against the worked example before moving on.",
                    "`apply` needs all four components. Compute `out[i] = m[i][0]*x + m[i][1]*y + m[i][2]*z + m[i][3]` for i in 0..3, then divide the first three by `out[3]`.",
                    "The two interesting entries of the projection matrix are `m[2][3] = 2*far*near/(near-far)` and `m[3][2] = -1`. That -1 is what makes w equal -z.",
                ],
                "tests": [
                    {"name": "identity and matmul", "code": r'''
_i = identity()
assert _i == [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0],
              [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], f"identity() gave {_i!r}"
_t = translate(1.0, 2.0, 3.0)
assert matmul(_t, _i) == _t and matmul(_i, _t) == _t, "the identity must be a two-sided unit"
_a = [[float(4 * i + j) for j in range(4)] for i in range(4)]
_b = [[float(j - i) for j in range(4)] for i in range(4)]
_got = matmul(_a, _b)
assert _got[0][0] == sum(_a[0][k] * _b[k][0] for k in range(4)), f"matmul row 0 col 0 is wrong: {_got[0][0]!r}"
assert _got[3][2] == sum(_a[3][k] * _b[k][2] for k in range(4)), "matmul row 3 col 2 is wrong"
for _bad in ([[0.0] * 4] * 3, [[0.0] * 3] * 4):
    try:
        matmul(_bad, _i)
        assert False, "matmul should raise ValueError for a matrix that is not 4x4"
    except ValueError:
        pass
'''},
                    {"name": "translate and scale act on points", "code": r'''
assert apply(translate(1, 2, 3), (1.0, 2.0, 3.0)) == (2.0, 4.0, 6.0), \
    f"translate gave {apply(translate(1, 2, 3), (1.0, 2.0, 3.0))!r}, expected (2.0, 4.0, 6.0)"
assert apply(scale(2, 3, 4), (1.0, 1.0, 1.0)) == (2.0, 3.0, 4.0), \
    f"scale gave {apply(scale(2, 3, 4), (1.0, 1.0, 1.0))!r}, expected (2.0, 3.0, 4.0)"
assert apply(translate(0, 0, 0), (5.0, -1.0, 0.0)) == (5.0, -1.0, 0.0), "a zero translation is the identity"
assert apply(scale(1, 1, 1), (5.0, -1.0, 0.0)) == (5.0, -1.0, 0.0), "a unit scale is the identity"
'''},
                    {"name": "The three rotations", "code": r'''
_cases = [(rotate_z(math.pi / 2), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
          (rotate_x(math.pi / 2), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
          (rotate_y(math.pi / 2), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))]
for _m, _p, _want in _cases:
    _got = apply(_m, _p)
    for _g, _w in zip(_got, _want):
        assert abs(_g - _w) < 1e-12, f"rotating {_p} gave {_got!r}, expected {_want}"
for _rot in (rotate_x, rotate_y, rotate_z):
    _round = apply(compose(_rot(-0.7), _rot(0.7)), (1.0, -2.0, 3.0))
    for _g, _w in zip(_round, (1.0, -2.0, 3.0)):
        assert abs(_g - _w) < 1e-12, f"{_rot.__name__} then its inverse moved the point to {_round!r}"
'''},
                    {"name": "Composition order is not commutative", "code": r'''
_t = translate(1.0, 0.0, 0.0)
_r = rotate_z(math.pi / 2)
_tr = apply(compose(_t, _r), (1.0, 0.0, 0.0))
_rt = apply(compose(_r, _t), (1.0, 0.0, 0.0))
for _g, _w in zip(_tr, (1.0, 1.0, 0.0)):
    assert abs(_g - _w) < 1e-12, f"compose(T, R) gave {_tr!r}, expected (1.0, 1.0, 0.0) — R runs first"
for _g, _w in zip(_rt, (0.0, 2.0, 0.0)):
    assert abs(_g - _w) < 1e-12, f"compose(R, T) gave {_rt!r}, expected (0.0, 2.0, 0.0) — T runs first"
assert compose() == identity(), "composing nothing gives the identity"
'''},
                    {"name": "perspective maps the frustum to the cube", "code": r'''
_p = perspective(90.0, 1.0, 1.0, 100.0)
assert abs(apply(_p, (0.0, 0.0, -1.0))[2] + 1.0) < 1e-9, \
    f"the near plane should map to z = -1, got {apply(_p, (0.0, 0.0, -1.0))[2]!r}"
assert abs(apply(_p, (0.0, 0.0, -100.0))[2] - 1.0) < 1e-9, \
    f"the far plane should map to z = +1, got {apply(_p, (0.0, 0.0, -100.0))[2]!r}"
_q = apply(_p, (1.0, 1.0, -2.0))
assert abs(_q[0] - 0.5) < 1e-9 and abs(_q[1] - 0.5) < 1e-9, \
    f"(1, 1, -2) should land at (0.5, 0.5) under a 90 degree square frustum, got {_q!r}"
_w = apply(perspective(90.0, 2.0, 1.0, 100.0), (1.0, 1.0, -2.0))
assert abs(_w[0] - 0.25) < 1e-9 and abs(_w[1] - 0.5) < 1e-9, \
    f"a 2:1 aspect halves the x coordinate only, got {_w!r}"
'''},
                    {"name": "The projected cube keeps its symmetry and depth order", "code": r'''
_mvp = compose(perspective(60.0, 1.0, 0.1, 50.0), translate(0.0, 0.0, -5.0))
_pts = transform_points(_mvp, CUBE)
assert len(_pts) == 8, f"the cube has 8 corners, got {len(_pts)}"
_f = 1.0 / math.tan(math.radians(30.0))
assert abs(_pts[0][0] - (-_f / 6.0)) < 1e-12, \
    f"corner (-1,-1,-1) sits at world z = -6, so x should be {-_f / 6.0!r}, got {_pts[0][0]!r}"
assert abs(_pts[4][0] - (_f / 6.0)) < 1e-12, "corner (1,-1,-1) must mirror it exactly"
assert _pts[1][2] < _pts[0][2], \
    f"the near face should have the smaller depth: near {_pts[1][2]!r} vs far {_pts[0][2]!r}"
assert all(-1.0 < _p[2] < 1.0 for _p in _pts), "the whole cube lies inside the frustum"
assert "projected corners: 8" in _out, "main.py should report how many corners it projected"
'''},
                    {"name": "The error paths", "code": r'''
try:
    apply(perspective(90.0, 1.0, 1.0, 100.0), (0.0, 0.0, 0.0))
    assert False, "a point at the eye has w = 0 and should raise ValueError"
except ValueError:
    pass
try:
    apply(identity(), (1.0, 2.0))
    assert False, "apply should raise ValueError for a point that is not 3 numbers"
except ValueError:
    pass
for _bad in [(0.0, 1.0, 1.0, 10.0), (180.0, 1.0, 1.0, 10.0), (60.0, 0.0, 1.0, 10.0),
             (60.0, 1.0, 0.0, 10.0), (60.0, 1.0, 10.0, 10.0), (60.0, 1.0, 20.0, 10.0)]:
    try:
        perspective(*_bad)
        assert False, f"perspective{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Rasterisation",
            "summary": "Lines by integer error terms, triangles by edge functions and a z-buffer.",
            "concepts": [
                "Bresenham replaces division and rounding with an integer error accumulator",
                "The edge function is a 2-D cross product: its sign says which side of a directed edge a point lies on",
                "The three edge functions at a point are proportional to the barycentric coordinates",
                "Twice the signed area is the edge function of the third vertex; a zero means a degenerate triangle",
                "Sampling at pixel centres (x+0.5, y+0.5) keeps the geometry symmetric about the pixel grid",
                "A fill rule makes shared edges watertight: a boundary sample belongs to exactly one triangle",
                "The z-buffer resolves visibility per sample, so triangles may be submitted in any order",
            ],
            "lab": {
                "title": "Lines, triangles and the z-buffer",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Screen space has y growing downwards. Pixel `(x, y)` is sampled at its centre
`(x + 0.5, y + 0.5)`. `Raster.__init__`, `Raster.inside` and `Raster.count` are
given.

## `Raster.put(x, y, z, colour)`

Depth test and write in one call: return `False` and change nothing when the
pixel is off-screen or when `z >= self.depth[y][x]`; otherwise store both the
depth and the colour and return `True`. Smaller z is nearer.

## `bresenham(x0, y0, x1, y1)`

The integer line, from the first endpoint to the second, both included, in
order. Use the all-octant error form: `dx = abs(x1-x0)`, `dy = -abs(y1-y0)`,
`err = dx + dy`, and at each step `e2 = 2*err`; step x when `e2 >= dy`, step y
when `e2 <= dx`. No floats anywhere.

```text
bresenham(0, 0, 5, 2)  ->  [(0,0), (1,0), (2,1), (3,1), (4,2), (5,2)]
bresenham(2, 2, 2, 2)  ->  [(2,2)]
```

**`draw_line(raster, x0, y0, x1, y1, colour, z=0.0)`** puts every point of that
line and returns how many actually landed.

## The triangle

**`edge(a, b, p)`** — `(b.x-a.x)*(p.y-a.y) - (b.y-a.y)*(p.x-a.x)`.

**`is_top_left(a, b)`** — the fill rule for the directed edge `a -> b`, with the
winding normalised so the signed area is positive: an edge is a *left* edge when
`dy < 0`, and a *top* edge when `dy == 0 and dx > 0`.

**`bounding_box(tri, width, height)`** — `(x0, y0, x1, y1)` inclusive integer
bounds, floor/ceil of the vertex extents, clipped to the raster.

**`fill_triangle(raster, tri, colour)`** — `tri` is three `(x, y, z)` vertices.
Compute the signed area; return 0 when it is exactly zero. When it is negative,
swap the last two vertices so it is positive. Then, for every pixel centre in
the bounding box, evaluate the three edge functions; reject a sample when any is
negative, and when one is exactly zero reject it unless that edge is top-left.
Interpolate z with the normalised edge functions as barycentric weights and hand
it to `put`. Return how many pixels were written.

```text
fill_triangle over ((0,0,0), (4,0,0), (0,4,0)) covers exactly
    (0,0) (1,0) (2,0) (0,1) (1,1) (0,2)  -- 6 pixels
and gives the same 6 for either winding.
```

The fill rule is not decoration. Split the square `(0,0)-(4,4)` along its
diagonal into two triangles and the two must cover 10 and 6 pixels: sixteen
pixels, each drawn exactly once.
''',
                "files": [{"name": "main.py", "content": r'''
import math


class Raster:
    """A colour buffer and a depth buffer of the same size."""

    def __init__(self, width, height, background=(0, 0, 0)):
        if width < 1 or height < 1:
            raise ValueError("a raster needs a positive width and height")
        self.width = width
        self.height = height
        self.background = background
        self.colour = [[background for _ in range(width)] for _ in range(height)]
        self.depth = [[float("inf")] * width for _ in range(height)]

    def inside(self, x, y):
        """True when (x, y) is a valid pixel index."""
        return 0 <= x < self.width and 0 <= y < self.height

    def count(self, colour):
        """How many pixels currently hold this colour."""
        return sum(row.count(colour) for row in self.colour)

    def put(self, x, y, z, colour):
        """Depth-test and write; True when the pixel was updated."""
        # your code here


def bresenham(x0, y0, x1, y1):
    """Integer line points from the first endpoint to the second, inclusive."""
    # your code here


def draw_line(raster, x0, y0, x1, y1, colour, z=0.0):
    """Put every point of the line; returns how many pixels were written."""
    # your code here


def edge(a, b, p):
    """Twice the signed area of the triangle a, b, p."""
    # your code here


def is_top_left(a, b):
    """True when the directed edge a -> b is a top or a left edge."""
    # your code here


def bounding_box(tri, width, height):
    """Inclusive integer (x0, y0, x1, y1) clipped to the raster."""
    # your code here


def fill_triangle(raster, tri, colour):
    """Rasterise one (x, y, z) triangle; returns how many pixels were written."""
    # your code here


screen = Raster(16, 16)
near = fill_triangle(screen, ((1.0, 1.0, 5.0), (14.0, 2.0, 5.0), (3.0, 13.0, 5.0)), (200, 60, 60))
far = fill_triangle(screen, ((2.0, 2.0, 9.0), (13.0, 3.0, 9.0), (4.0, 12.0, 9.0)), (60, 60, 200))
drawn = draw_line(screen, 0, 15, 15, 0, (255, 255, 255), 1.0)
print(f"near: {near}  far: {far}  line: {drawn}")
print("blue pixels behind red:", screen.count((60, 60, 200)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


class Raster:
    """A colour buffer and a depth buffer of the same size."""

    def __init__(self, width, height, background=(0, 0, 0)):
        if width < 1 or height < 1:
            raise ValueError("a raster needs a positive width and height")
        self.width = width
        self.height = height
        self.background = background
        self.colour = [[background for _ in range(width)] for _ in range(height)]
        self.depth = [[float("inf")] * width for _ in range(height)]

    def inside(self, x, y):
        """True when (x, y) is a valid pixel index."""
        return 0 <= x < self.width and 0 <= y < self.height

    def count(self, colour):
        """How many pixels currently hold this colour."""
        return sum(row.count(colour) for row in self.colour)

    def put(self, x, y, z, colour):
        """Depth-test and write; True when the pixel was updated."""
        if not self.inside(x, y):
            return False
        if z >= self.depth[y][x]:
            return False
        self.depth[y][x] = z
        self.colour[y][x] = colour
        return True


def bresenham(x0, y0, x1, y1):
    """Integer line points from the first endpoint to the second, inclusive."""
    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            return points
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def draw_line(raster, x0, y0, x1, y1, colour, z=0.0):
    """Put every point of the line; returns how many pixels were written."""
    drawn = 0
    for x, y in bresenham(x0, y0, x1, y1):
        if raster.put(x, y, z, colour):
            drawn += 1
    return drawn


def edge(a, b, p):
    """Twice the signed area of the triangle a, b, p."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def is_top_left(a, b):
    """True when the directed edge a -> b is a top or a left edge."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return dy < 0 or (dy == 0 and dx > 0)


def bounding_box(tri, width, height):
    """Inclusive integer (x0, y0, x1, y1) clipped to the raster."""
    xs = [v[0] for v in tri]
    ys = [v[1] for v in tri]
    x0 = max(0, int(math.floor(min(xs))))
    x1 = min(width - 1, int(math.ceil(max(xs))))
    y0 = max(0, int(math.floor(min(ys))))
    y1 = min(height - 1, int(math.ceil(max(ys))))
    return (x0, y0, x1, y1)


def fill_triangle(raster, tri, colour):
    """Rasterise one (x, y, z) triangle; returns how many pixels were written."""
    v0, v1, v2 = tri
    area = edge(v0, v1, v2)
    if area == 0:
        return 0
    if area < 0:
        v1, v2 = v2, v1
        area = -area
    x0, y0, x1, y1 = bounding_box(tri, raster.width, raster.height)
    drawn = 0
    for py in range(y0, y1 + 1):
        for px in range(x0, x1 + 1):
            p = (px + 0.5, py + 0.5)
            w0 = edge(v1, v2, p)
            w1 = edge(v2, v0, p)
            w2 = edge(v0, v1, p)
            if w0 < 0 or w1 < 0 or w2 < 0:
                continue
            if w0 == 0 and not is_top_left(v1, v2):
                continue
            if w1 == 0 and not is_top_left(v2, v0):
                continue
            if w2 == 0 and not is_top_left(v0, v1):
                continue
            z = (w0 * v0[2] + w1 * v1[2] + w2 * v2[2]) / area
            if raster.put(px, py, z, colour):
                drawn += 1
    return drawn


screen = Raster(16, 16)
near = fill_triangle(screen, ((1.0, 1.0, 5.0), (14.0, 2.0, 5.0), (3.0, 13.0, 5.0)), (200, 60, 60))
far = fill_triangle(screen, ((2.0, 2.0, 9.0), (13.0, 3.0, 9.0), (4.0, 12.0, 9.0)), (60, 60, 200))
drawn = draw_line(screen, 0, 15, 15, 0, (255, 255, 255), 1.0)
print(f"near: {near}  far: {far}  line: {drawn}")
print("blue pixels behind red:", screen.count((60, 60, 200)))
'''}],
                "hints": [
                    "`put` must test before it writes: `if z >= self.depth[y][x]: return False`. Using `>` instead of `>=` lets a coplanar triangle overwrite its neighbour and makes the result submission-order dependent.",
                    "Bresenham's two `if`s are independent — a diagonal step happens when both fire in the same iteration. Do not turn the second into an `elif`.",
                    "In `fill_triangle`, `w0` belongs to the edge opposite `v0`, which is `edge(v1, v2, p)`. Get that pairing wrong and the z interpolation is a shuffled version of the right answer.",
                    "The barycentric weights are `w0/area, w1/area, w2/area`. Because they sum to one you can interpolate z as `(w0*z0 + w1*z1 + w2*z2) / area`.",
                ],
                "tests": [
                    {"name": "The raster and its depth test", "code": r'''
for _bad in [(0, 4), (4, 0), (-1, 4)]:
    try:
        Raster(*_bad)
        assert False, f"Raster{_bad!r} should raise ValueError"
    except ValueError:
        pass
_r = Raster(3, 2)
assert _r.count((0, 0, 0)) == 6, f"a fresh 3x2 raster has 6 background pixels, count gave {_r.count((0, 0, 0))}"
assert _r.put(1, 1, 5.0, (9, 9, 9)) is True, "the first write to an empty pixel must succeed"
assert _r.put(1, 1, 9.0, (1, 1, 1)) is False, "a farther sample must be rejected"
assert _r.put(1, 1, 5.0, (1, 1, 1)) is False, "an equal depth must be rejected, not tie-broken"
assert _r.put(1, 1, 2.0, (7, 7, 7)) is True, "a nearer sample must win"
assert _r.colour[1][1] == (7, 7, 7) and _r.depth[1][1] == 2.0, \
    f"the pixel holds {_r.colour[1][1]!r} at depth {_r.depth[1][1]!r}"
assert _r.put(9, 9, 0.0, (5, 5, 5)) is False, "an off-screen write must be refused, not crash"
'''},
                    {"name": "bresenham in every octant", "code": r'''
_cases = {
    (0, 0, 5, 2): [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)],
    (0, 0, 2, 5): [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (2, 5)],
    (0, 0, 3, 3): [(0, 0), (1, 1), (2, 2), (3, 3)],
    (5, 2, 0, 0): [(5, 2), (4, 2), (3, 1), (2, 1), (1, 0), (0, 0)],
    (0, 0, 0, 4): [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
    (4, 0, 0, 0): [(4, 0), (3, 0), (2, 0), (1, 0), (0, 0)],
    (0, 0, -3, 2): [(0, 0), (-1, 1), (-2, 1), (-3, 2)],
    (2, 2, 2, 2): [(2, 2)],
}
for _args, _want in _cases.items():
    _got = bresenham(*_args)
    assert _got == _want, f"bresenham{_args!r} gave {_got!r}, expected {_want!r}"
_r = Raster(8, 8)
assert draw_line(_r, 0, 0, 7, 3, (5, 5, 5)) == 8, "the line from (0,0) to (7,3) covers 8 pixels"
assert _r.count((5, 5, 5)) == 8, f"the raster holds {_r.count((5, 5, 5))} line pixels"
assert draw_line(_r, -5, -5, -1, -1, (6, 6, 6)) == 0, "an entirely off-screen line writes nothing"
'''},
                    {"name": "The edge function and the bounding box", "code": r'''
assert edge((0.0, 0.0), (4.0, 0.0), (0.0, 4.0)) == 16.0, \
    f"edge gave {edge((0.0, 0.0), (4.0, 0.0), (0.0, 4.0))!r}, expected 16.0"
assert edge((0.0, 0.0), (0.0, 4.0), (4.0, 0.0)) == -16.0, "reversing the winding flips the sign"
assert edge((0.0, 0.0), (4.0, 4.0), (2.0, 2.0)) == 0.0, "a collinear point sits exactly on the edge"
assert bounding_box(((-3.0, -3.0, 0.0), (2.5, 1.2, 0.0), (1.0, 9.0, 0.0)), 4, 4) == (0, 0, 3, 3), \
    "the box must be clipped to the raster on all four sides"
assert bounding_box(((1.2, 2.7, 0.0), (3.4, 2.7, 0.0), (1.2, 5.1, 0.0)), 16, 16) == (1, 2, 4, 6), \
    f"got {bounding_box(((1.2, 2.7, 0.0), (3.4, 2.7, 0.0), (1.2, 5.1, 0.0)), 16, 16)!r}"
'''},
                    {"name": "fill_triangle covers the right pixels", "code": r'''
def _covered(tri):
    _r = Raster(8, 8)
    _n = fill_triangle(_r, tri, (9, 9, 9))
    _px = sorted((x, y) for y in range(8) for x in range(8) if _r.colour[y][x] == (9, 9, 9))
    return _n, _px
_want = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0)]
_n, _px = _covered(((0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (0.0, 4.0, 0.0)))
assert _n == 6 and _px == _want, f"the right triangle covered {_n} pixels: {_px!r}"
_n2, _px2 = _covered(((0.0, 0.0, 0.0), (0.0, 4.0, 0.0), (4.0, 0.0, 0.0)))
assert _px2 == _want, f"the reversed winding covered {_px2!r} — the coverage must not depend on winding"
assert _covered(((0.0, 0.0, 0.0), (2.0, 2.0, 0.0), (4.0, 4.0, 0.0)))[0] == 0, \
    "a degenerate triangle covers nothing"
assert _covered(((10.0, 10.0, 0.0), (14.0, 10.0, 0.0), (10.0, 14.0, 0.0)))[0] == 0, \
    "an entirely off-screen triangle covers nothing and must not crash"
'''},
                    {"name": "The fill rule makes shared edges watertight", "code": r'''
def _cover_set(tri):
    _r = Raster(8, 8)
    _n = fill_triangle(_r, tri, (9, 9, 9))
    return _n, {(x, y) for y in range(8) for x in range(8) if _r.colour[y][x] == (9, 9, 9)}
_n1, _s1 = _cover_set(((0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (4.0, 4.0, 0.0)))
_n2, _s2 = _cover_set(((0.0, 0.0, 0.0), (4.0, 4.0, 0.0), (0.0, 4.0, 0.0)))
assert (_n1, _n2) == (10, 6), f"the two halves covered {_n1} and {_n2} pixels, expected 10 and 6"
assert not (_s1 & _s2), f"these pixels were drawn twice: {sorted(_s1 & _s2)!r}"
assert len(_s1 | _s2) == 16, f"the split square covers {len(_s1 | _s2)} pixels, expected 16"
_nu, _su = _cover_set(((0.0, 2.5, 0.0), (4.0, 2.5, 0.0), (2.0, 0.5, 0.0)))
_nd, _sd = _cover_set(((4.0, 2.5, 0.0), (0.0, 2.5, 0.0), (2.0, 4.5, 0.0)))
assert not (_su & _sd), f"a shared horizontal edge was drawn twice at {sorted(_su & _sd)!r}"
assert (_nu, _nd) == (2, 6), f"the horizontal-edge pair covered {_nu} and {_nd} pixels, expected 2 and 6"
'''},
                    {"name": "Depth is interpolated, not constant", "code": r'''
_r = Raster(8, 8)
fill_triangle(_r, ((0.0, 0.0, 0.0), (4.0, 0.0, 4.0), (0.0, 4.0, 8.0)), (1, 1, 1))
_row = [_r.depth[0][x] for x in range(3)]
for _got, _want in zip(_row, [1.5, 2.5, 3.5]):
    assert abs(_got - _want) < 1e-9, f"row 0 depths were {_row!r}, expected [1.5, 2.5, 3.5]"
'''},
                    {"name": "The z-buffer resolves visibility in any order", "code": r'''
_tri = lambda z: ((0.0, 0.0, z), (4.0, 0.0, z), (0.0, 4.0, z))
_r = Raster(4, 4)
assert fill_triangle(_r, _tri(5.0), (9, 9, 9)) == 6, "the first triangle writes all six pixels"
assert fill_triangle(_r, _tri(2.0), (7, 7, 7)) == 6, "a nearer triangle replaces all six"
assert fill_triangle(_r, _tri(8.0), (3, 3, 3)) == 0, "a farther triangle writes nothing at all"
assert _r.colour[0][0] == (7, 7, 7) and _r.depth[0][0] == 2.0, \
    f"the visible pixel is {_r.colour[0][0]!r} at depth {_r.depth[0][0]!r}"
assert "blue pixels behind red:" in _out, "main.py should report how much of the far triangle survived"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Shading and colour",
            "summary": "Normals, the two reflection terms, and getting the numbers onto a display.",
            "concepts": [
                "The geometric normal is the normalised cross product of two edges; vertex order fixes its sign",
                "Lambert's cosine law: irradiance falls with cos(theta) = n . l, clamped at zero",
                "The clamp is not cosmetic — a negative cosine means the light is behind the surface",
                "Blinn's halfway vector h = normalise(l + v) replaces Phong's reflection vector and stays cheaper",
                "The specular exponent controls highlight tightness; energy conservation ties it to the specular weight",
                "Shading is linear-light arithmetic; a display expects roughly sRGB, so encode last",
                "Clamp before the gamma encode, never after, or you raise a negative number to a fractional power",
            ],
            "lab": {
                "title": "Lambert, Blinn-Phong and gamma",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Vectors are 3-tuples of floats. `sub`, `add`, `mul`, `dot`, `cross` and `length`
are given.

**`normalise(v)`** — the unit vector. A length below `1e-12` raises `ValueError`.

**`face_normal(a, b, c)`** — `normalise(cross(b - a, c - a))`. Reversing two
vertices must flip it.

**`lambert(n, l)`** — `max(0, n . l)` for unit `n` and unit `l` pointing *at* the
light.

**`blinn_phong(n, l, v, shininess)`** — `0.0` when `n . l <= 0` (a highlight
cannot appear on a face the light does not reach); otherwise
`max(0, n . h) ** shininess` with `h = normalise(l + v)`. A `shininess` that is
not positive raises `ValueError`.

**`shade(n, l, v, base, light, ambient, shininess, ks)`** — per channel `i`:

```text
base[i] * (ambient + light[i] * lambert(n, l))  +  ks * light[i] * blinn_phong(...)
```

**`clamp(x, lo=0.0, hi=1.0)`**, then
**`to_srgb_byte(linear, gamma=2.2)`** — clamp first, raise to `1/gamma`, scale by
255 and round to an `int`. **`encode(colour, gamma=2.2)`** does all three
channels.

## Numbers to steer by

```text
face_normal((0,0,0), (1,0,0), (0,1,0))            ->  (0, 0, 1)
lambert((0,0,1), normalise((1,0,1)))              ->  0.70710678...
blinn_phong((0,0,1), (0,0,1), (0,0,1), 32)        ->  1.0
blinn_phong((0,0,1), (1,0,0), (0,0,1), 32)        ->  0.0    (light on the horizon)
blinn_phong((0,0,1), normalise((1,0,1)), (0,0,1), 32) -> cos(pi/8)**32 = 0.0793763...
to_srgb_byte(0.0), (0.25), (0.5), (1.0)           ->  0, 136, 186, 255
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def sub(a, b):
    """a - b."""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    """a + b."""
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    """a scaled by s."""
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    """The scalar product."""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    """The vector product."""
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def length(a):
    """The Euclidean length."""
    return math.sqrt(dot(a, a))


def normalise(a):
    """The unit vector; ValueError for a zero-length input."""
    # your code here


def face_normal(a, b, c):
    """The unit normal of the triangle a, b, c."""
    # your code here


def lambert(n, l):
    """The clamped diffuse cosine term."""
    # your code here


def blinn_phong(n, l, v, shininess):
    """The clamped Blinn-Phong specular term."""
    # your code here


def shade(n, l, v, base, light, ambient, shininess, ks):
    """Ambient plus diffuse plus specular, in linear light."""
    # your code here


def clamp(x, lo=0.0, hi=1.0):
    """x confined to [lo, hi]."""
    # your code here


def to_srgb_byte(linear, gamma=2.2):
    """One linear channel as a display byte."""
    # your code here


def encode(colour, gamma=2.2):
    """A linear RGB triple as three display bytes."""
    # your code here


N = face_normal((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
L = normalise((1.0, 1.0, 1.0))
V = (0.0, 0.0, 1.0)
lit = shade(N, L, V, (0.8, 0.3, 0.3), (1.0, 1.0, 1.0), 0.1, 32, 0.4)
print("normal:", N)
print(f"diffuse: {lambert(N, L):.6f}  specular: {blinn_phong(N, L, V, 32):.6f}")
print("encoded:", encode(lit))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def sub(a, b):
    """a - b."""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    """a + b."""
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    """a scaled by s."""
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    """The scalar product."""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    """The vector product."""
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def length(a):
    """The Euclidean length."""
    return math.sqrt(dot(a, a))


def normalise(a):
    """The unit vector; ValueError for a zero-length input."""
    n = length(a)
    if n < 1e-12:
        raise ValueError("cannot normalise a zero-length vector")
    return (a[0] / n, a[1] / n, a[2] / n)


def face_normal(a, b, c):
    """The unit normal of the triangle a, b, c."""
    return normalise(cross(sub(b, a), sub(c, a)))


def lambert(n, l):
    """The clamped diffuse cosine term."""
    return max(0.0, dot(n, l))


def blinn_phong(n, l, v, shininess):
    """The clamped Blinn-Phong specular term."""
    if shininess <= 0:
        raise ValueError("shininess must be positive")
    if dot(n, l) <= 0.0:
        return 0.0
    h = normalise(add(l, v))
    return max(0.0, dot(n, h)) ** shininess


def shade(n, l, v, base, light, ambient, shininess, ks):
    """Ambient plus diffuse plus specular, in linear light."""
    diffuse = lambert(n, l)
    specular = blinn_phong(n, l, v, shininess)
    return tuple(base[i] * (ambient + light[i] * diffuse) + ks * light[i] * specular
                 for i in range(3))


def clamp(x, lo=0.0, hi=1.0):
    """x confined to [lo, hi]."""
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def to_srgb_byte(linear, gamma=2.2):
    """One linear channel as a display byte."""
    return int(round(clamp(linear) ** (1.0 / gamma) * 255))


def encode(colour, gamma=2.2):
    """A linear RGB triple as three display bytes."""
    return tuple(to_srgb_byte(c, gamma) for c in colour)


N = face_normal((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
L = normalise((1.0, 1.0, 1.0))
V = (0.0, 0.0, 1.0)
lit = shade(N, L, V, (0.8, 0.3, 0.3), (1.0, 1.0, 1.0), 0.1, 32, 0.4)
print("normal:", N)
print(f"diffuse: {lambert(N, L):.6f}  specular: {blinn_phong(N, L, V, 32):.6f}")
print("encoded:", encode(lit))
'''}],
                "hints": [
                    "`face_normal` is `normalise(cross(sub(b, a), sub(c, a)))` — one line, but the order of the two edge vectors decides which way the normal points.",
                    "Guard the specular term with `if dot(n, l) <= 0.0: return 0.0` before you build the halfway vector, or you will paint highlights on unlit faces.",
                    "`shade` should call `lambert` and `blinn_phong` rather than recomputing the dot products, so the clamping rules stay in one place.",
                    "In `to_srgb_byte` the clamp comes first: `clamp(linear) ** (1.0 / gamma) * 255`. Raising a negative number to a fractional power raises an exception in Python, not a warning.",
                ],
                "tests": [
                    {"name": "normalise and its failure mode", "code": r'''
_u = normalise((3.0, 0.0, 4.0))
assert abs(length(_u) - 1.0) < 1e-12, f"normalise gave a vector of length {length(_u)!r}"
for _g, _w in zip(_u, (0.6, 0.0, 0.8)):
    assert abs(_g - _w) < 1e-12, f"normalise((3,0,4)) gave {_u!r}, expected (0.6, 0.0, 0.8)"
try:
    normalise((0.0, 0.0, 0.0))
    assert False, "normalising the zero vector should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "face_normal points where the winding says", "code": r'''
_n = face_normal((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
assert _n == (0.0, 0.0, 1.0), f"face_normal gave {_n!r}, expected (0.0, 0.0, 1.0)"
_flipped = face_normal((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0))
assert _flipped == (0.0, 0.0, -1.0), f"swapping two vertices should flip the normal, got {_flipped!r}"
_skew = face_normal((1.0, 1.0, 1.0), (2.0, 1.0, 1.0), (1.0, 3.0, 1.0))
assert abs(length(_skew) - 1.0) < 1e-12, "the normal must be unit length wherever the triangle sits"
try:
    face_normal((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0))
    assert False, "a collinear triangle has no normal and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The diffuse term obeys the cosine law", "code": r'''
assert lambert((0.0, 0.0, 1.0), (0.0, 0.0, 1.0)) == 1.0, "a head-on light gives the full cosine"
assert lambert((0.0, 0.0, 1.0), (0.0, 0.0, -1.0)) == 0.0, "a light behind the surface contributes nothing"
assert lambert((0.0, 0.0, 1.0), (1.0, 0.0, 0.0)) == 0.0, "a light on the horizon contributes nothing"
_got = lambert((0.0, 0.0, 1.0), normalise((1.0, 0.0, 1.0)))
assert abs(_got - 1.0 / math.sqrt(2.0)) < 1e-12, f"a 45 degree light gave {_got!r}, expected 0.7071067811865476"
'''},
                    {"name": "The specular term and the halfway vector", "code": r'''
assert blinn_phong((0.0, 0.0, 1.0), (0.0, 0.0, 1.0), (0.0, 0.0, 1.0), 32) == 1.0, \
    "light, view and normal aligned gives a full highlight"
assert blinn_phong((0.0, 0.0, 1.0), (0.0, 0.0, -1.0), (0.0, 0.0, 1.0), 32) == 0.0, \
    "no highlight on a face the light cannot reach"
assert blinn_phong((0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 32) == 0.0, \
    "a light exactly on the horizon gives no highlight"
_got = blinn_phong((0.0, 0.0, 1.0), normalise((1.0, 0.0, 1.0)), (0.0, 0.0, 1.0), 32)
_want = math.cos(math.pi / 8.0) ** 32
assert abs(_got - _want) < 1e-12, f"the 45 degree case gave {_got!r}, expected cos(pi/8)**32 = {_want!r}"
_tight = blinn_phong((0.0, 0.0, 1.0), normalise((1.0, 0.0, 1.0)), (0.0, 0.0, 1.0), 128)
assert _tight < _got, "a larger exponent must give a tighter, dimmer highlight off-axis"
for _bad in (0, -8):
    try:
        blinn_phong((0.0, 0.0, 1.0), (0.0, 0.0, 1.0), (0.0, 0.0, 1.0), _bad)
        assert False, f"shininess={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "shade combines the three terms", "code": r'''
_n = (0.0, 0.0, 1.0)
_dark = shade(_n, (0.0, 0.0, -1.0), _n, (0.8, 0.2, 0.2), (1.0, 1.0, 1.0), 0.1, 32, 0.5)
for _g, _w in zip(_dark, (0.08, 0.02, 0.02)):
    assert abs(_g - _w) < 1e-12, f"an unlit face should be ambient only, got {_dark!r}"
_lit = shade(_n, _n, _n, (0.8, 0.2, 0.2), (1.0, 1.0, 1.0), 0.1, 32, 0.5)
for _g, _w in zip(_lit, (1.38, 0.72, 0.72)):
    assert abs(_g - _w) < 1e-12, f"the head-on case gave {_lit!r}, expected (1.38, 0.72, 0.72)"
_tinted = shade(_n, _n, _n, (1.0, 1.0, 1.0), (1.0, 0.0, 0.0), 0.0, 32, 0.0)
assert _tinted == (1.0, 0.0, 0.0), f"a red light on white gives red, got {_tinted!r}"
'''},
                    {"name": "Clamping and the gamma encode", "code": r'''
assert clamp(-1.0) == 0.0 and clamp(2.0) == 1.0 and clamp(0.3) == 0.3, "clamp confines to [0, 1]"
assert clamp(7.0, 2.0, 5.0) == 5.0 and clamp(1.0, 2.0, 5.0) == 2.0, "clamp honours its bounds"
_want = {0.0: 0, 0.25: 136, 0.5: 186, 1.0: 255, -1.0: 0, 2.0: 255}
for _v, _b in _want.items():
    _got = to_srgb_byte(_v)
    assert _got == _b, f"to_srgb_byte({_v}) gave {_got!r}, expected {_b}"
    assert isinstance(_got, int), f"to_srgb_byte({_v}) returned {type(_got).__name__}, expected an int"
assert encode((1.0, 0.5, 0.0)) == (255, 186, 0), f"encode gave {encode((1.0, 0.5, 0.0))!r}"
assert encode((0.5, 0.5, 0.5), gamma=1.0) == (128, 128, 128), \
    f"with gamma 1 the encode is linear, got {encode((0.5, 0.5, 0.5), gamma=1.0)!r}"
assert "normal: (0.0, 0.0, 1.0)" in _out, "main.py should print the computed face normal"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Ray tracing",
            "summary": "Intersections, the epsilon that stops self-hits, and one bounce.",
            "concepts": [
                "A ray is origin + t * direction with t > 0; rendering is a visibility query along it",
                "Ray/sphere is a quadratic in t; the discriminant's sign classifies miss, tangent and pierce",
                "Take the smaller positive root, so a ray starting inside a sphere still hits its far wall",
                "Ray/plane is one division; a denominator near zero means the ray runs parallel to the plane",
                "Shadow acne is a floating-point artefact: offset the shadow ray origin along the normal",
                "A shadow ray must be occluded *before* the light, not merely occluded somewhere",
                "Recursion depth bounds the reflection series; each bounce contributes geometrically less",
            ],
            "lab": {
                "title": "Spheres, planes, shadows and one bounce",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
The vector helpers, `shade`, `EPS` and the `SCENE` dictionary are given. Objects
are dicts with a `kind` of `"sphere"` or `"plane"`.

**`intersect_sphere(origin, direction, centre, radius)`** — solve
`a*t^2 + b*t + c = 0` with `a = d.d`, `b = 2 * (o-c).d`, `c = (o-c).(o-c) - r^2`.
Return the smaller root greater than `EPS`, then the larger, then `None`.

```text
from (0,0,0) along (0,0,-1) at the sphere (0,0,-5) r=1  ->  4.0
starting inside it at (0,0,-5)                          ->  1.0
grazing it from (1,0,0)                                 ->  5.0
pointing away from (0,0,-10)                            ->  None
```

**`intersect_plane(origin, direction, point, normal)`** — `None` when
`abs(d . n) < EPS`, else `t = ((p - o) . n) / (d . n)`, and `None` again unless
`t > EPS`.

**`reflect(d, n)`** — `d - 2*(d.n)*n`.

**`hit_distance(obj, origin, direction)`** and **`normal_at(obj, point)`**
dispatch on `obj["kind"]`; an unknown kind raises `ValueError`. A sphere's normal
is `normalise(point - centre)`; a plane's is its own normal, normalised.

**`nearest_hit(objects, origin, direction)`** — `(t, obj)` for the smallest `t`,
or `None`.

**`in_shadow(objects, point, light, normal)`** — fire a ray from
`point + 1e-4 * normal` towards `light`; shadowed when something is hit at a
distance less than the distance to the light.

**`trace(scene, origin, direction, depth)`**:

1. No hit -> `scene["background"]`.
2. Otherwise take the hit point and its normal, flipping the normal if it faces
   the same way as the ray.
3. In shadow -> `scene["ambient"] * obj["colour"]`, channel by channel.
   Otherwise `shade(...)` with the object's `shininess` and `ks`.
4. If `obj["reflectivity"] > 0` and `depth > 0`, trace the reflected ray from
   `point + 1e-4 * normal` and mix: `colour*(1-k) + bounce*k`.

## Values to check against

```text
trace(SCENE, (0,0,0), (0,1,0), 1)        ->  the background, unchanged
trace(SCENE, (0,0,0), (0,0,-1), 1)       ->  a red-dominant colour
trace(SCENE, (-1,3,-6), (0,-1,0), 1)     ->  (0.08, 0.08, 0.08): plain ambient, in shadow
```
''',
                "files": [{"name": "main.py", "content": r'''
import math

EPS = 1e-6


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def normalise(a):
    n = math.sqrt(dot(a, a))
    if n < 1e-12:
        raise ValueError("cannot normalise a zero-length vector")
    return (a[0] / n, a[1] / n, a[2] / n)


def shade(n, l, v, base, light, ambient, shininess, ks):
    """Ambient plus Lambert diffuse plus Blinn-Phong specular."""
    diffuse = max(0.0, dot(n, l))
    specular = 0.0
    if diffuse > 0.0:
        h = normalise(add(l, v))
        specular = max(0.0, dot(n, h)) ** shininess
    return tuple(base[i] * (ambient + light[i] * diffuse) + ks * light[i] * specular
                 for i in range(3))


SCENE = {
    "objects": [
        {"kind": "sphere", "centre": (0.0, 0.0, -5.0), "radius": 1.0,
         "colour": (0.9, 0.3, 0.3), "reflectivity": 0.0, "shininess": 32, "ks": 0.4},
        {"kind": "sphere", "centre": (1.6, 0.0, -4.0), "radius": 0.5,
         "colour": (0.3, 0.9, 0.4), "reflectivity": 0.6, "shininess": 64, "ks": 0.5},
        {"kind": "plane", "point": (0.0, -1.0, 0.0), "normal": (0.0, 1.0, 0.0),
         "colour": (0.8, 0.8, 0.8), "reflectivity": 0.0, "shininess": 8, "ks": 0.1},
    ],
    "light": (5.0, 5.0, 0.0),
    "light_colour": (1.0, 1.0, 1.0),
    "ambient": 0.1,
    "background": (0.02, 0.03, 0.06),
}


def intersect_sphere(origin, direction, centre, radius):
    """Smallest t > EPS at which the ray meets the sphere, or None."""
    # your code here


def intersect_plane(origin, direction, point, normal):
    """t > EPS at which the ray meets the plane, or None."""
    # your code here


def reflect(d, n):
    """d mirrored in the plane with normal n."""
    # your code here


def hit_distance(obj, origin, direction):
    """Dispatch to the right intersection routine."""
    # your code here


def normal_at(obj, point):
    """The unit surface normal of obj at point."""
    # your code here


def nearest_hit(objects, origin, direction):
    """(t, obj) for the closest hit, or None."""
    # your code here


def in_shadow(objects, point, light, normal):
    """True when something blocks the straight line from point to light."""
    # your code here


def trace(scene, origin, direction, depth):
    """The colour seen along this ray."""
    # your code here


print("straight ahead:", trace(SCENE, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), 1))
print("into the sky:", trace(SCENE, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1))
print("shadowed floor:", trace(SCENE, (-1.0, 3.0, -6.0), (0.0, -1.0, 0.0), 1))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

EPS = 1e-6


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def normalise(a):
    n = math.sqrt(dot(a, a))
    if n < 1e-12:
        raise ValueError("cannot normalise a zero-length vector")
    return (a[0] / n, a[1] / n, a[2] / n)


def shade(n, l, v, base, light, ambient, shininess, ks):
    """Ambient plus Lambert diffuse plus Blinn-Phong specular."""
    diffuse = max(0.0, dot(n, l))
    specular = 0.0
    if diffuse > 0.0:
        h = normalise(add(l, v))
        specular = max(0.0, dot(n, h)) ** shininess
    return tuple(base[i] * (ambient + light[i] * diffuse) + ks * light[i] * specular
                 for i in range(3))


SCENE = {
    "objects": [
        {"kind": "sphere", "centre": (0.0, 0.0, -5.0), "radius": 1.0,
         "colour": (0.9, 0.3, 0.3), "reflectivity": 0.0, "shininess": 32, "ks": 0.4},
        {"kind": "sphere", "centre": (1.6, 0.0, -4.0), "radius": 0.5,
         "colour": (0.3, 0.9, 0.4), "reflectivity": 0.6, "shininess": 64, "ks": 0.5},
        {"kind": "plane", "point": (0.0, -1.0, 0.0), "normal": (0.0, 1.0, 0.0),
         "colour": (0.8, 0.8, 0.8), "reflectivity": 0.0, "shininess": 8, "ks": 0.1},
    ],
    "light": (5.0, 5.0, 0.0),
    "light_colour": (1.0, 1.0, 1.0),
    "ambient": 0.1,
    "background": (0.02, 0.03, 0.06),
}


def intersect_sphere(origin, direction, centre, radius):
    """Smallest t > EPS at which the ray meets the sphere, or None."""
    oc = sub(origin, centre)
    a = dot(direction, direction)
    b = 2.0 * dot(oc, direction)
    c = dot(oc, oc) - radius * radius
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return None
    root = math.sqrt(disc)
    for t in ((-b - root) / (2.0 * a), (-b + root) / (2.0 * a)):
        if t > EPS:
            return t
    return None


def intersect_plane(origin, direction, point, normal):
    """t > EPS at which the ray meets the plane, or None."""
    denom = dot(direction, normal)
    if abs(denom) < EPS:
        return None
    t = dot(sub(point, origin), normal) / denom
    return t if t > EPS else None


def reflect(d, n):
    """d mirrored in the plane with normal n."""
    return sub(d, mul(n, 2.0 * dot(d, n)))


def hit_distance(obj, origin, direction):
    """Dispatch to the right intersection routine."""
    if obj["kind"] == "sphere":
        return intersect_sphere(origin, direction, obj["centre"], obj["radius"])
    if obj["kind"] == "plane":
        return intersect_plane(origin, direction, obj["point"], obj["normal"])
    raise ValueError(f"unknown object kind {obj['kind']!r}")


def normal_at(obj, point):
    """The unit surface normal of obj at point."""
    if obj["kind"] == "sphere":
        return normalise(sub(point, obj["centre"]))
    if obj["kind"] == "plane":
        return normalise(obj["normal"])
    raise ValueError(f"unknown object kind {obj['kind']!r}")


def nearest_hit(objects, origin, direction):
    """(t, obj) for the closest hit, or None."""
    best = None
    for obj in objects:
        t = hit_distance(obj, origin, direction)
        if t is not None and (best is None or t < best[0]):
            best = (t, obj)
    return best


def in_shadow(objects, point, light, normal):
    """True when something blocks the straight line from point to light."""
    to_light = sub(light, point)
    distance = math.sqrt(dot(to_light, to_light))
    direction = mul(to_light, 1.0 / distance)
    hit = nearest_hit(objects, add(point, mul(normal, 1e-4)), direction)
    return hit is not None and hit[0] < distance


def trace(scene, origin, direction, depth):
    """The colour seen along this ray."""
    hit = nearest_hit(scene["objects"], origin, direction)
    if hit is None:
        return scene["background"]
    t, obj = hit
    point = add(origin, mul(direction, t))
    n = normal_at(obj, point)
    if dot(n, direction) > 0.0:
        n = mul(n, -1.0)
    if in_shadow(scene["objects"], point, scene["light"], n):
        colour = tuple(c * scene["ambient"] for c in obj["colour"])
    else:
        to_light = normalise(sub(scene["light"], point))
        view = mul(direction, -1.0)
        colour = shade(n, to_light, view, obj["colour"], scene["light_colour"],
                       scene["ambient"], obj["shininess"], obj["ks"])
    k = obj["reflectivity"]
    if k > 0.0 and depth > 0:
        r = normalise(reflect(direction, n))
        bounce = trace(scene, add(point, mul(n, 1e-4)), r, depth - 1)
        colour = tuple(colour[i] * (1.0 - k) + bounce[i] * k for i in range(3))
    return colour


print("straight ahead:", trace(SCENE, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), 1))
print("into the sky:", trace(SCENE, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1))
print("shadowed floor:", trace(SCENE, (-1.0, 3.0, -6.0), (0.0, -1.0, 0.0), 1))
'''}],
                "hints": [
                    "Test the roots in order — `(-b - root) / (2a)` first — and return the first one greater than `EPS`. Returning the smaller root unconditionally breaks every ray that starts inside a sphere.",
                    "`abs(denom) < EPS` is the parallel test for the plane. Comparing to exactly zero lets a nearly-parallel ray produce an enormous t and a hit that should not exist.",
                    "`in_shadow` needs the distance to the light as well as the direction: an object beyond the light does not cast a shadow onto the point.",
                    "In `trace`, flip the normal with `if dot(n, direction) > 0.0: n = mul(n, -1.0)` before shading, otherwise a ray that enters a sphere from inside shades against the wrong hemisphere.",
                ],
                "tests": [
                    {"name": "Ray/sphere in all its cases", "code": r'''
_c, _r = (0.0, 0.0, -5.0), 1.0
assert intersect_sphere((0.0, 0.0, 0.0), (0.0, 0.0, -1.0), _c, _r) == 4.0, \
    f"the near hit is at t=4.0, got {intersect_sphere((0.0, 0.0, 0.0), (0.0, 0.0, -1.0), _c, _r)!r}"
assert intersect_sphere((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), _c, _r) is None, "a ray pointing up misses"
assert intersect_sphere((0.0, 0.0, -5.0), (0.0, 0.0, -1.0), _c, _r) == 1.0, \
    "starting inside, the only positive root is the far wall at t=1.0"
assert intersect_sphere((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), _c, _r) == 5.0, \
    "a grazing ray has a zero discriminant and a single root at t=5.0"
assert intersect_sphere((0.0, 0.0, -10.0), (0.0, 0.0, -1.0), _c, _r) is None, \
    "a sphere entirely behind the ray is not a hit"
'''},
                    {"name": "Ray/plane and reflection", "code": r'''
_p, _n = (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)
assert intersect_plane((0.0, 1.0, 0.0), (0.0, -1.0, 0.0), _p, _n) == 1.0, \
    f"got {intersect_plane((0.0, 1.0, 0.0), (0.0, -1.0, 0.0), _p, _n)!r}, expected 1.0"
assert intersect_plane((0.0, 1.0, 0.0), (1.0, 0.0, 0.0), _p, _n) is None, "a parallel ray never meets it"
assert intersect_plane((0.0, 1.0, 0.0), (0.0, 1.0, 0.0), _p, _n) is None, "the plane is behind this ray"
assert reflect((0.0, -1.0, 0.0), (0.0, 1.0, 0.0)) == (0.0, 1.0, 0.0), "a head-on ray comes straight back"
assert reflect((1.0, -1.0, 0.0), (0.0, 1.0, 0.0)) == (1.0, 1.0, 0.0), "only the normal component flips"
_d = normalise((0.3, -0.8, 0.5))
_twice = reflect(reflect(_d, (0.0, 1.0, 0.0)), (0.0, 1.0, 0.0))
for _g, _w in zip(_twice, _d):
    assert abs(_g - _w) < 1e-12, f"reflecting twice should restore the direction, got {_twice!r}"
'''},
                    {"name": "Dispatch, normals and the unknown kind", "code": r'''
_sphere = SCENE["objects"][0]
_plane = SCENE["objects"][2]
assert hit_distance(_sphere, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0)) == 4.0, "sphere dispatch"
assert hit_distance(_plane, (0.0, 1.0, 0.0), (0.0, -1.0, 0.0)) == 2.0, "plane dispatch"
assert normal_at(_sphere, (0.0, 0.0, -4.0)) == (0.0, 0.0, 1.0), \
    f"the front of the sphere faces the camera, got {normal_at(_sphere, (0.0, 0.0, -4.0))!r}"
assert normal_at(_plane, (3.0, -1.0, 2.0)) == (0.0, 1.0, 0.0), "the plane normal is the same everywhere"
for _fn, _args in ((hit_distance, ((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))), (normal_at, ((0.0, 0.0, 0.0),))):
    try:
        _fn({"kind": "torus"}, *_args)
        assert False, f"{_fn.__name__} should raise ValueError for an unknown kind"
    except ValueError:
        pass
'''},
                    {"name": "nearest_hit takes the closest", "code": r'''
_hit = nearest_hit(SCENE["objects"], (0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
assert _hit is not None and _hit[0] == 4.0, f"nearest_hit gave {_hit!r}, expected t=4.0"
assert _hit[1] is SCENE["objects"][0], "the red sphere is the nearest thing straight ahead"
assert nearest_hit(SCENE["objects"], (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)) is None, \
    "nothing lies above the camera"
assert nearest_hit([], (0.0, 0.0, 0.0), (0.0, 0.0, -1.0)) is None, "an empty scene has no hits"
_far = [{"kind": "sphere", "centre": (0.0, 0.0, -20.0), "radius": 1.0,
         "colour": (1.0, 1.0, 1.0), "reflectivity": 0.0, "shininess": 8, "ks": 0.1}]
_both = nearest_hit(SCENE["objects"] + _far, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
assert _both[0] == 4.0, f"adding a farther sphere must not change the answer, got {_both[0]!r}"
'''},
                    {"name": "Shadow rays", "code": r'''
assert in_shadow(SCENE["objects"], (-1.0, -1.0, -6.0), SCENE["light"], (0.0, 1.0, 0.0)) is True, \
    "the floor behind the red sphere is in shadow"
assert in_shadow(SCENE["objects"], (-3.0, -1.0, -2.0), SCENE["light"], (0.0, 1.0, 0.0)) is False, \
    "this patch of floor sees the light directly"
assert in_shadow(SCENE["objects"], (0.0, 0.0, -4.0), SCENE["light"], (0.0, 0.0, 1.0)) is False, \
    "the lit face of the sphere must not shadow itself — offset the ray origin along the normal"
assert in_shadow([], (0.0, 0.0, 0.0), SCENE["light"], (0.0, 1.0, 0.0)) is False, \
    "nothing can block the light in an empty scene"
'''},
                    {"name": "trace: background, light and shadow", "code": r'''
assert trace(SCENE, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1) == SCENE["background"], \
    "a ray that hits nothing returns the background unchanged"
_red = trace(SCENE, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), 1)
assert _red[0] > _red[1] and _red[0] > _red[2], f"the red sphere should read red, got {_red!r}"
assert _red[0] > 0.3, f"the lit face should be well above ambient, got {_red!r}"
_shadow = trace(SCENE, (-1.0, 3.0, -6.0), (0.0, -1.0, 0.0), 1)
for _g in _shadow:
    assert abs(_g - 0.08) < 1e-9, f"shadowed floor should be ambient * 0.8 = 0.08, got {_shadow!r}"
'''},
                    {"name": "The reflection bounce", "code": r'''
_d = normalise((1.6, 0.0, -4.0))
_flat = trace(SCENE, (0.0, 0.0, 0.0), _d, 0)
_bounced = trace(SCENE, (0.0, 0.0, 0.0), _d, 1)
assert _flat != _bounced, "the mirrored sphere must look different once a bounce is allowed"
_mix = tuple(_flat[i] * 0.4 for i in range(3))
assert all(_bounced[i] >= _mix[i] - 1e-9 for i in range(3)), \
    f"the bounce should mix in, not replace: direct {_flat!r} became {_bounced!r}"
assert trace(SCENE, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), 0) == trace(SCENE, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), 1), \
    "a matt object is unaffected by the recursion depth"
assert "into the sky: (0.02, 0.03, 0.06)" in _out, "main.py should show the background colour for a miss"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a software renderer that writes a PPM",
        "runtime": "python",
        "minutes": 240,
        "brief": r'''
Everything from the four modules, assembled into a renderer that turns a scene
description into an image file. `renderer.py` holds the logic and is what the
checks import; `main.py` renders the picture, writes `scene.ppm` and prints its
statistics.

The vector helpers, `EPS`, `clamp` and `make_scene()` are given. The scene is
four objects — three spheres and an infinite ground plane — one point light, an
ambient term, a background colour and `max_depth = 1`.

## Camera

**`camera_ray(scene, x, y, width, height)`** returns `(origin, direction)` for
pixel `(x, y)`, sampled at its centre. The camera sits at `scene["camera"]` and
looks down -z, y upwards on screen:

```text
scale  = tan(radians(fov_deg) / 2)
aspect = width / height
px = (2 * ((x + 0.5) / width)  - 1) * scale * aspect
py = (1 - 2 * ((y + 0.5) / height))     * scale
direction = normalise((px, py, -1))
```

A non-positive width or height raises `ValueError`.

## Geometry, shading, tracing

`intersect_sphere`, `intersect_plane`, `hit_distance`, `normal_at`,
`nearest_hit`, `in_shadow` and `trace` behave exactly as in module 4 — smaller
positive root, `EPS` guards, a shadow ray offset by `1e-4` along the normal that
only counts occluders nearer than the light, a normal flipped to face the ray,
plain `ambient * colour` in shadow, and one mixed reflection bounce while
`depth > 0`.

`shade` is the module 3 model: `base * (ambient + light * diffuse) + ks * light *
specular`, with Blinn-Phong specular suppressed when the diffuse term is zero.

## Output

**`to_srgb_byte(linear, gamma=2.2)`** and **`encode(colour)`** — clamp, gamma,
scale, round to `int`.

**`render(scene, width, height)`** — a list of `height` rows of `width`
`(r, g, b)` byte triples. Row 0 is the top of the image.

**`write_ppm(path, pixels)`** — plain-text P3: the magic number, `width height`,
`255`, then the samples. An empty image raises `ValueError`.

**`read_ppm(path)`** — `(width, height, pixels)` back from such a file. A file
that does not start with `P3`, or whose sample count is not `width*height*3`,
raises `ValueError`.

**`image_stats(pixels)`** — a dict with `width`, `height`, `pixels`,
`mean_luma`, `min_luma`, `max_luma` and `unique_colours`, where the luma of a
pixel is `(r + g + b) / 3`. An empty image raises `ValueError`.

## How this is marked

Not by a byte comparison — a legitimate renderer can differ in the last bit. The
checks look at structure and statistics: every pixel is a byte triple, the image
is reproducible, a sky pixel equals the encoded background, a shadowed floor
pixel is darker than a lit one, and the 64x48 render of `make_scene()` has a mean
luma near 135, a darkest pixel below the background, a brightest pixel above 200
from the specular highlights, and several hundred distinct colours.
''',
        "deliverables": [
            "`renderer.py` — camera, intersections, shading, shadow and reflection rays, importable with no side effects",
            "`renderer.py` — `render`, `write_ppm`, `read_ppm` and `image_stats`",
            "`main.py` — renders `make_scene()` at 64x48, writes `scene.ppm` and prints the statistics",
            "A P3 file that reads back byte-identical through your own `read_ppm`",
            "Validation: empty images, malformed PPMs and non-positive image sizes all raise `ValueError`",
            "Gamma-correct output: linear shading throughout, encoded to bytes exactly once, at the end",
        ],
        "constraints": [
            "Standard library only — `math` is the only import the renderer needs",
            "`renderer.py` must define names only; importing it must print nothing and write no files",
            "The renderer must be deterministic: two runs of `render` on the same scene are identical",
            "No supersampling and no random jitter — every sample is the pixel centre",
            "A 64x48 render must complete in well under a second, so no per-pixel scene rebuilding",
        ],
        "rubric": [
            {"criterion": "Geometry", "weight": 25,
             "evidence": "Sphere and plane intersections return the correct roots for the outside, inside, grazing and behind cases."},
            {"criterion": "Shading and colour", "weight": 25,
             "evidence": "Diffuse, specular, ambient and the gamma encode produce the documented byte values; shadowed surfaces read as plain ambient."},
            {"criterion": "Image pipeline", "weight": 20,
             "evidence": "render returns a correctly shaped grid of byte triples; write_ppm and read_ppm round-trip without loss."},
            {"criterion": "Statistical fidelity", "weight": 20,
             "evidence": "The reference render's mean, extremes and colour count fall inside the published bands."},
            {"criterion": "Robustness", "weight": 10,
             "evidence": "Every documented ValueError is raised, renderer.py is import-clean, and the render is reproducible."},
        ],
        "hints": [
            "Build it bottom-up and print as you go: intersections first, then a flat-colour render, then shading, then shadows, then the bounce. A wrong image is far easier to diagnose one layer at a time.",
            "If the picture comes out upside down, the sign of `py` is wrong — screen y grows downwards while world y grows upwards, which is what the `1 - 2*(...)` does.",
            "Black speckles across a lit surface are shadow acne: the shadow ray is hitting the surface it started on. Offset its origin by `1e-4` along the normal.",
            "`write_ppm` can join the samples however you like — whitespace is whitespace in P3 — but `read_ppm` should tokenise with `split()` rather than assume one row per line.",
            "For `image_stats`, collect the pixels into a `set` to count distinct colours; a flat image means your shading is not varying and the bands will catch it.",
        ],
        "files": [
            {"name": "renderer.py", "content": r'''
import math

EPS = 1e-6


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def normalise(a):
    n = math.sqrt(dot(a, a))
    if n < 1e-12:
        raise ValueError("cannot normalise a zero-length vector")
    return (a[0] / n, a[1] / n, a[2] / n)


def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else (hi if x > hi else x)


def make_scene():
    """Three spheres on an infinite floor, one light, one bounce."""
    return {
        "objects": [
            {"kind": "sphere", "centre": (0.0, 0.0, -5.0), "radius": 1.0,
             "colour": (0.90, 0.25, 0.25), "reflectivity": 0.25,
             "shininess": 64, "ks": 0.5},
            {"kind": "sphere", "centre": (2.2, 0.3, -6.5), "radius": 1.3,
             "colour": (0.25, 0.45, 0.90), "reflectivity": 0.50,
             "shininess": 128, "ks": 0.6},
            {"kind": "sphere", "centre": (-2.0, -0.4, -4.5), "radius": 0.6,
             "colour": (0.95, 0.80, 0.20), "reflectivity": 0.0,
             "shininess": 16, "ks": 0.3},
            {"kind": "plane", "point": (0.0, -1.0, 0.0), "normal": (0.0, 1.0, 0.0),
             "colour": (0.75, 0.75, 0.78), "reflectivity": 0.15,
             "shininess": 8, "ks": 0.1},
        ],
        "camera": (0.0, 0.0, 0.0),
        "fov_deg": 60.0,
        "light": (5.0, 6.0, 1.0),
        "light_colour": (1.0, 1.0, 1.0),
        "ambient": 0.12,
        "background": (0.05, 0.07, 0.12),
        "max_depth": 1,
    }


def reflect(d, n):
    """d mirrored in the plane with normal n."""
    # your code here


def camera_ray(scene, x, y, width, height):
    """(origin, direction) for the centre of pixel (x, y)."""
    # your code here


def intersect_sphere(origin, direction, centre, radius):
    """Smallest t > EPS at which the ray meets the sphere, or None."""
    # your code here


def intersect_plane(origin, direction, point, normal):
    """t > EPS at which the ray meets the plane, or None."""
    # your code here


def hit_distance(obj, origin, direction):
    """Dispatch on obj["kind"]."""
    # your code here


def normal_at(obj, point):
    """The unit surface normal of obj at point."""
    # your code here


def nearest_hit(objects, origin, direction):
    """(t, obj) for the closest hit, or None."""
    # your code here


def in_shadow(objects, point, light, normal):
    """True when an object lies between point and light."""
    # your code here


def shade(n, l, v, base, light, ambient, shininess, ks):
    """Ambient plus Lambert diffuse plus Blinn-Phong specular."""
    # your code here


def trace(scene, origin, direction, depth):
    """The linear colour seen along this ray."""
    # your code here


def to_srgb_byte(linear, gamma=2.2):
    """One linear channel as a display byte."""
    # your code here


def encode(colour, gamma=2.2):
    """A linear RGB triple as three display bytes."""
    # your code here


def render(scene, width, height):
    """Rows of (r, g, b) byte triples, row 0 at the top."""
    # your code here


def write_ppm(path, pixels):
    """Write a plain P3 PPM."""
    # your code here


def read_ppm(path):
    """(width, height, pixels) read back from a P3 PPM."""
    # your code here


def image_stats(pixels):
    """Summary statistics for a rendered image."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from renderer import make_scene, render, write_ppm, read_ppm, image_stats, encode

WIDTH, HEIGHT = 64, 48
scene = make_scene()

# 1. render the scene
# 2. write scene.ppm and read it back to prove the round trip
# 3. print the image statistics
print("renderer not finished yet")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "renderer.py", "content": r'''
import math

EPS = 1e-6


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def normalise(a):
    n = math.sqrt(dot(a, a))
    if n < 1e-12:
        raise ValueError("cannot normalise a zero-length vector")
    return (a[0] / n, a[1] / n, a[2] / n)


def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else (hi if x > hi else x)


def make_scene():
    """Three spheres on an infinite floor, one light, one bounce."""
    return {
        "objects": [
            {"kind": "sphere", "centre": (0.0, 0.0, -5.0), "radius": 1.0,
             "colour": (0.90, 0.25, 0.25), "reflectivity": 0.25,
             "shininess": 64, "ks": 0.5},
            {"kind": "sphere", "centre": (2.2, 0.3, -6.5), "radius": 1.3,
             "colour": (0.25, 0.45, 0.90), "reflectivity": 0.50,
             "shininess": 128, "ks": 0.6},
            {"kind": "sphere", "centre": (-2.0, -0.4, -4.5), "radius": 0.6,
             "colour": (0.95, 0.80, 0.20), "reflectivity": 0.0,
             "shininess": 16, "ks": 0.3},
            {"kind": "plane", "point": (0.0, -1.0, 0.0), "normal": (0.0, 1.0, 0.0),
             "colour": (0.75, 0.75, 0.78), "reflectivity": 0.15,
             "shininess": 8, "ks": 0.1},
        ],
        "camera": (0.0, 0.0, 0.0),
        "fov_deg": 60.0,
        "light": (5.0, 6.0, 1.0),
        "light_colour": (1.0, 1.0, 1.0),
        "ambient": 0.12,
        "background": (0.05, 0.07, 0.12),
        "max_depth": 1,
    }


def reflect(d, n):
    """d mirrored in the plane with normal n."""
    return sub(d, mul(n, 2.0 * dot(d, n)))


def camera_ray(scene, x, y, width, height):
    """(origin, direction) for the centre of pixel (x, y)."""
    if width < 1 or height < 1:
        raise ValueError("the image needs a positive width and height")
    scale = math.tan(math.radians(scene["fov_deg"]) / 2.0)
    aspect = width / height
    px = (2.0 * ((x + 0.5) / width) - 1.0) * scale * aspect
    py = (1.0 - 2.0 * ((y + 0.5) / height)) * scale
    return scene["camera"], normalise((px, py, -1.0))


def intersect_sphere(origin, direction, centre, radius):
    """Smallest t > EPS at which the ray meets the sphere, or None."""
    oc = sub(origin, centre)
    a = dot(direction, direction)
    b = 2.0 * dot(oc, direction)
    c = dot(oc, oc) - radius * radius
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return None
    root = math.sqrt(disc)
    for t in ((-b - root) / (2.0 * a), (-b + root) / (2.0 * a)):
        if t > EPS:
            return t
    return None


def intersect_plane(origin, direction, point, normal):
    """t > EPS at which the ray meets the plane, or None."""
    denom = dot(direction, normal)
    if abs(denom) < EPS:
        return None
    t = dot(sub(point, origin), normal) / denom
    return t if t > EPS else None


def hit_distance(obj, origin, direction):
    """Dispatch on obj["kind"]."""
    if obj["kind"] == "sphere":
        return intersect_sphere(origin, direction, obj["centre"], obj["radius"])
    if obj["kind"] == "plane":
        return intersect_plane(origin, direction, obj["point"], obj["normal"])
    raise ValueError(f"unknown object kind {obj['kind']!r}")


def normal_at(obj, point):
    """The unit surface normal of obj at point."""
    if obj["kind"] == "sphere":
        return normalise(sub(point, obj["centre"]))
    if obj["kind"] == "plane":
        return normalise(obj["normal"])
    raise ValueError(f"unknown object kind {obj['kind']!r}")


def nearest_hit(objects, origin, direction):
    """(t, obj) for the closest hit, or None."""
    best = None
    for obj in objects:
        t = hit_distance(obj, origin, direction)
        if t is not None and (best is None or t < best[0]):
            best = (t, obj)
    return best


def in_shadow(objects, point, light, normal):
    """True when an object lies between point and light."""
    to_light = sub(light, point)
    distance = math.sqrt(dot(to_light, to_light))
    direction = mul(to_light, 1.0 / distance)
    hit = nearest_hit(objects, add(point, mul(normal, 1e-4)), direction)
    return hit is not None and hit[0] < distance


def shade(n, l, v, base, light, ambient, shininess, ks):
    """Ambient plus Lambert diffuse plus Blinn-Phong specular."""
    diffuse = max(0.0, dot(n, l))
    specular = 0.0
    if diffuse > 0.0:
        h = normalise(add(l, v))
        specular = max(0.0, dot(n, h)) ** shininess
    return tuple(base[i] * (ambient + light[i] * diffuse) + ks * light[i] * specular
                 for i in range(3))


def trace(scene, origin, direction, depth):
    """The linear colour seen along this ray."""
    hit = nearest_hit(scene["objects"], origin, direction)
    if hit is None:
        return scene["background"]
    t, obj = hit
    point = add(origin, mul(direction, t))
    n = normal_at(obj, point)
    if dot(n, direction) > 0.0:
        n = mul(n, -1.0)
    if in_shadow(scene["objects"], point, scene["light"], n):
        colour = tuple(c * scene["ambient"] for c in obj["colour"])
    else:
        to_light = normalise(sub(scene["light"], point))
        view = mul(direction, -1.0)
        colour = shade(n, to_light, view, obj["colour"], scene["light_colour"],
                       scene["ambient"], obj["shininess"], obj["ks"])
    k = obj["reflectivity"]
    if k > 0.0 and depth > 0:
        r = normalise(reflect(direction, n))
        bounce = trace(scene, add(point, mul(n, 1e-4)), r, depth - 1)
        colour = tuple(colour[i] * (1.0 - k) + bounce[i] * k for i in range(3))
    return colour


def to_srgb_byte(linear, gamma=2.2):
    """One linear channel as a display byte."""
    return int(round(clamp(linear) ** (1.0 / gamma) * 255))


def encode(colour, gamma=2.2):
    """A linear RGB triple as three display bytes."""
    return tuple(to_srgb_byte(c, gamma) for c in colour)


def render(scene, width, height):
    """Rows of (r, g, b) byte triples, row 0 at the top."""
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            origin, direction = camera_ray(scene, x, y, width, height)
            row.append(encode(trace(scene, origin, direction, scene["max_depth"])))
        rows.append(row)
    return rows


def write_ppm(path, pixels):
    """Write a plain P3 PPM."""
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    if width == 0 or height == 0:
        raise ValueError("cannot write an empty image")
    parts = ["P3", f"{width} {height}", "255"]
    for row in pixels:
        parts.append(" ".join(f"{r} {g} {b}" for r, g, b in row))
    with open(path, "w") as fh:
        fh.write("\n".join(parts) + "\n")


def read_ppm(path):
    """(width, height, pixels) read back from a P3 PPM."""
    with open(path) as fh:
        tokens = fh.read().split()
    if not tokens or tokens[0] != "P3":
        raise ValueError("not a plain P3 PPM file")
    width = int(tokens[1])
    height = int(tokens[2])
    values = [int(v) for v in tokens[4:]]
    if len(values) != width * height * 3:
        raise ValueError("the file does not hold width * height * 3 samples")
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            i = (y * width + x) * 3
            row.append((values[i], values[i + 1], values[i + 2]))
        rows.append(row)
    return width, height, rows


def image_stats(pixels):
    """Summary statistics for a rendered image."""
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    if width == 0 or height == 0:
        raise ValueError("cannot summarise an empty image")
    total = 0.0
    lo = 255.0
    hi = 0.0
    seen = set()
    for row in pixels:
        for px in row:
            luma = (px[0] + px[1] + px[2]) / 3.0
            total += luma
            if luma < lo:
                lo = luma
            if luma > hi:
                hi = luma
            seen.add(px)
    count = width * height
    return {"width": width, "height": height, "pixels": count,
            "mean_luma": total / count, "min_luma": lo, "max_luma": hi,
            "unique_colours": len(seen)}
'''},
            {"name": "main.py", "content": r'''
from renderer import make_scene, render, write_ppm, read_ppm, image_stats, encode

WIDTH, HEIGHT = 64, 48
scene = make_scene()

pixels = render(scene, WIDTH, HEIGHT)
write_ppm("scene.ppm", pixels)
width, height, again = read_ppm("scene.ppm")

print(f"rendered {WIDTH}x{HEIGHT}, round trip: {(width, height) == (WIDTH, HEIGHT) and again == pixels}")
print("sky pixel:", pixels[0][0], "== encoded background:", encode(scene["background"]))

stats = image_stats(pixels)
print(f"mean luma: {stats['mean_luma']:.3f}")
print(f"darkest: {stats['min_luma']:.3f}   brightest: {stats['max_luma']:.3f}")
print(f"distinct colours: {stats['unique_colours']}")
'''},
        ],
        "tests": [
            {"name": "Camera rays are unit length and symmetric", "code": r'''
import renderer as _r
_s = _r.make_scene()
_o, _d = _r.camera_ray(_s, 32, 24, 64, 48)
assert _o == _s["camera"], f"every primary ray starts at the camera, got {_o!r}"
assert abs(_r.dot(_d, _d) - 1.0) < 1e-12, f"the direction must be normalised, got {_d!r}"
_left = _r.camera_ray(_s, 0, 24, 64, 48)[1]
_right = _r.camera_ray(_s, 63, 24, 64, 48)[1]
assert abs(_left[0] + _right[0]) < 1e-12, f"the two edges should mirror: {_left!r} vs {_right!r}"
assert abs(_left[1] - _right[1]) < 1e-12, "pixels in the same row share a y component"
_top = _r.camera_ray(_s, 32, 0, 64, 48)[1]
_bottom = _r.camera_ray(_s, 32, 47, 64, 48)[1]
assert _top[1] > 0.0 > _bottom[1], f"row 0 must look upwards: top {_top!r}, bottom {_bottom!r}"
assert _left[2] < 0.0, "the camera looks down -z"
for _bad in [(0, 48), (64, 0), (-1, 48)]:
    try:
        _r.camera_ray(_s, 0, 0, *_bad)
        assert False, f"camera_ray with size {_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "The aspect ratio widens x only", "code": r'''
import renderer as _r
_s = _r.make_scene()
_square = _r.camera_ray(_s, 0, 0, 48, 48)[1]
_wide = _r.camera_ray(_s, 0, 0, 96, 48)[1]
assert abs(_wide[0] / _wide[2]) > abs(_square[0] / _square[2]) + 1e-9, \
    "a wider image must open the horizontal field of view, not the vertical one"
assert abs(_wide[1] / _wide[2] - _square[1] / _square[2]) < 1e-12, \
    "the vertical field of view is fixed by fov_deg alone"
_scale = __import__("math").tan(__import__("math").radians(_s["fov_deg"]) / 2.0)
_edge = _r.camera_ray(_s, 47, 0, 48, 48)[1]
assert abs(_edge[0] / -_edge[2] - _scale * (2 * (47.5 / 48) - 1)) < 1e-12, \
    "the last column should sit at the documented offset from the axis"
'''},
            {"name": "Intersections", "code": r'''
import renderer as _r
_c, _rad = (0.0, 0.0, -5.0), 1.0
assert _r.intersect_sphere((0.0, 0.0, 0.0), (0.0, 0.0, -1.0), _c, _rad) == 4.0, "the front wall is at t=4"
assert _r.intersect_sphere((0.0, 0.0, -5.0), (0.0, 0.0, -1.0), _c, _rad) == 1.0, "from inside, the far wall"
assert _r.intersect_sphere((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), _c, _rad) == 5.0, "the grazing ray"
assert _r.intersect_sphere((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), _c, _rad) is None, "a clean miss"
assert _r.intersect_plane((0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)) == 1.0
assert _r.intersect_plane((0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)) is None
assert _r.reflect((1.0, -1.0, 0.0), (0.0, 1.0, 0.0)) == (1.0, 1.0, 0.0), "only the normal component flips"
try:
    _r.hit_distance({"kind": "torus"}, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    assert False, "an unknown object kind should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "nearest_hit and shadow rays", "code": r'''
import renderer as _r
_s = _r.make_scene()
_hit = _r.nearest_hit(_s["objects"], (0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
assert _hit is not None and _hit[0] == 4.0, f"nearest_hit gave {_hit!r}, expected t=4.0"
assert _hit[1] is _s["objects"][0], "the red sphere is nearest along the axis"
assert _r.nearest_hit(_s["objects"], (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)) is None, "nothing overhead"
assert _r.in_shadow(_s["objects"], (-5.0 / 6.0, -1.0, -6.0), _s["light"], (0.0, 1.0, 0.0)) is True, \
    "the floor directly behind the red sphere is in its shadow"
assert _r.in_shadow(_s["objects"], (-4.0, -1.0, -2.0), _s["light"], (0.0, 1.0, 0.0)) is False, \
    "this patch of floor sees the light"
assert _r.in_shadow(_s["objects"], (0.0, 0.0, -4.0), _s["light"], (0.0, 0.0, 1.0)) is False, \
    "a lit surface must not shadow itself — offset the shadow ray along the normal"
'''},
            {"name": "shade and the gamma encode", "code": r'''
import renderer as _r
_n = (0.0, 0.0, 1.0)
_dark = _r.shade(_n, (0.0, 0.0, -1.0), _n, (0.8, 0.2, 0.2), (1.0, 1.0, 1.0), 0.1, 32, 0.5)
for _g, _w in zip(_dark, (0.08, 0.02, 0.02)):
    assert abs(_g - _w) < 1e-12, f"an unlit face is ambient only, got {_dark!r}"
_lit = _r.shade(_n, _n, _n, (0.8, 0.2, 0.2), (1.0, 1.0, 1.0), 0.1, 32, 0.5)
for _g, _w in zip(_lit, (1.38, 0.72, 0.72)):
    assert abs(_g - _w) < 1e-12, f"the head-on case gave {_lit!r}, expected (1.38, 0.72, 0.72)"
for _v, _b in {0.0: 0, 0.25: 136, 0.5: 186, 1.0: 255, -1.0: 0, 2.0: 255}.items():
    assert _r.to_srgb_byte(_v) == _b, f"to_srgb_byte({_v}) gave {_r.to_srgb_byte(_v)!r}, expected {_b}"
assert _r.encode((0.05, 0.07, 0.12)) == (65, 76, 97), \
    f"the background encodes to (65, 76, 97), got {_r.encode((0.05, 0.07, 0.12))!r}"
'''},
            {"name": "trace: sky, light, shadow and bounce", "code": r'''
import renderer as _r
_s = _r.make_scene()
assert _r.trace(_s, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 1) == _s["background"], \
    "a ray into the sky returns the background unchanged"
_red = _r.trace(_s, (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), 1)
assert _red[0] > _red[1] and _red[0] > _red[2], f"the red sphere should read red, got {_red!r}"
_shadowed = _r.trace(_s, (-5.0 / 6.0, 3.0, -6.0), (0.0, -1.0, 0.0), 1)
_litfloor = _r.trace(_s, (-4.0, 3.0, -2.0), (0.0, -1.0, 0.0), 1)
assert sum(_shadowed) < sum(_litfloor) * 0.5, \
    f"the shadowed floor {_shadowed!r} should be far darker than the lit floor {_litfloor!r}"
_dir = _r.normalise((2.2, 0.3, -6.5))
assert _r.trace(_s, (0.0, 0.0, 0.0), _dir, 0) != _r.trace(_s, (0.0, 0.0, 0.0), _dir, 1), \
    "the mirrored sphere must change once a bounce is allowed"
'''},
            {"name": "render produces a well-formed image", "code": r'''
import renderer as _r
_s = _r.make_scene()
_img = _r.render(_s, 16, 12)
assert len(_img) == 12 and all(len(row) == 16 for row in _img), \
    f"render(scene, 16, 12) returned {len(_img)} rows of {len(_img[0]) if _img else 0}"
for _row in _img:
    for _px in _row:
        assert len(_px) == 3, f"each pixel is an (r, g, b) triple, got {_px!r}"
        assert all(isinstance(_c, int) and 0 <= _c <= 255 for _c in _px), \
            f"pixel {_px!r} is not three bytes in 0..255"
assert _img[0][0] == _r.encode(_s["background"]), \
    f"the top-left pixel looks at empty sky, expected {_r.encode(_s['background'])!r}, got {_img[0][0]!r}"
assert _r.render(_s, 16, 12) == _img, "rendering the same scene twice must give the same image"
'''},
            {"name": "The PPM round trip", "code": r'''
import renderer as _r
_img = [[(0, 0, 0), (255, 128, 64)], [(1, 2, 3), (250, 251, 252)]]
_r.write_ppm("cap_tiny.ppm", _img)
with open("cap_tiny.ppm") as _fh:
    _tokens = _fh.read().split()
assert _tokens[:4] == ["P3", "2", "2", "255"], f"the header reads {_tokens[:4]!r}, expected P3 2 2 255"
assert len(_tokens) == 4 + 12, f"a 2x2 image needs 12 samples, the file has {len(_tokens) - 4}"
assert _r.read_ppm("cap_tiny.ppm") == (2, 2, _img), "write_ppm and read_ppm must round-trip exactly"
try:
    _r.write_ppm("cap_empty.ppm", [])
    assert False, "writing an empty image should raise ValueError"
except ValueError:
    pass
with open("cap_bad.ppm", "w") as _fh:
    _fh.write("P6 2 2 255 1 2 3\n")
try:
    _r.read_ppm("cap_bad.ppm")
    assert False, "a file that is not P3 should raise ValueError"
except ValueError:
    pass
with open("cap_short.ppm", "w") as _fh:
    _fh.write("P3\n2 2\n255\n1 2 3 4 5 6\n")
try:
    _r.read_ppm("cap_short.ppm")
    assert False, "a truncated sample list should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "image_stats reports the shape and the extremes", "code": r'''
import renderer as _r
_flat = [[(10, 20, 30)] * 4 for _ in range(3)]
_st = _r.image_stats(_flat)
assert (_st["width"], _st["height"], _st["pixels"]) == (4, 3, 12), f"shape came back as {_st!r}"
assert abs(_st["mean_luma"] - 20.0) < 1e-12, f"mean_luma gave {_st['mean_luma']!r}, expected 20.0"
assert _st["min_luma"] == 20.0 and _st["max_luma"] == 20.0, "a flat image has no spread"
assert _st["unique_colours"] == 1, f"a flat image has one colour, got {_st['unique_colours']!r}"
_mixed = [[(0, 0, 0), (255, 255, 255)]]
_st2 = _r.image_stats(_mixed)
assert (_st2["min_luma"], _st2["max_luma"], _st2["unique_colours"]) == (0.0, 255.0, 2), f"got {_st2!r}"
assert abs(_st2["mean_luma"] - 127.5) < 1e-12, f"mean_luma gave {_st2['mean_luma']!r}, expected 127.5"
try:
    _r.image_stats([])
    assert False, "summarising an empty image should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The reference render sits inside the published bands", "code": r'''
import renderer as _r
_s = _r.make_scene()
_img = _r.render(_s, 64, 48)
_st = _r.image_stats(_img)
assert _st["pixels"] == 3072, f"a 64x48 image has 3072 pixels, got {_st['pixels']!r}"
assert 125.0 < _st["mean_luma"] < 145.0, \
    f"mean luma {_st['mean_luma']:.3f} is outside the reference band 125-145"
_bg_luma = sum(_r.encode(_s["background"])) / 3.0
assert _st["min_luma"] < _bg_luma, \
    f"the darkest pixel {_st['min_luma']:.3f} should be a shadow, below the background {_bg_luma:.3f}"
assert _st["max_luma"] > 200.0, \
    f"the brightest pixel is {_st['max_luma']:.3f}; the specular highlights should exceed 200"
assert _st["unique_colours"] > 300, \
    f"only {_st['unique_colours']} distinct colours — the shading is not varying enough"
'''},
            {"name": "The study runs and the module stays clean", "code": r'''
assert "round trip: True" in _out, "main.py should prove the PPM round-trips"
assert "mean luma" in _out and "distinct colours" in _out, \
    "main.py should print the image statistics"
_src = open("renderer.py").read()
assert "print(" not in _src, "renderer.py holds the logic; the printing belongs in main.py"
import os as _os
assert _os.path.exists("scene.ppm"), "main.py should write scene.ppm"
_w, _h, _back = __import__("renderer").read_ppm("scene.ppm")
assert (_w, _h) == (64, 48), f"scene.ppm is {_w}x{_h}, expected 64x48"
'''},
        ],
    },
}
