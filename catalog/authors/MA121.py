"""MA121 — Linear Algebra."""

COURSE = {
    "id": "MA121",
    "title": "Linear Algebra",
    "year": 1,
    "level": "Intermediate",
    "prereqs": ["MA101"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "▦",
    "summary": (
        "Linear algebra written from the ground up in plain Python: no library "
        "hides the arithmetic, so every theorem has to survive contact with "
        "floating point. You build a Matrix type, then Gaussian elimination with "
        "partial pivoting, then LU factorisation, then orthogonalisation and the "
        "power method — and finish with a least-squares engine that reports rank "
        "and conditioning alongside its answer."
    ),
    "outcomes": [
        "Implement matrix addition, scaling, multiplication and transposition from the definitions",
        "Explain why partial pivoting is a numerical necessity rather than a convenience",
        "Compute rank, determinant and solutions by elimination, and detect singular systems",
        "Factor a matrix as PA = LU and reuse the factors for determinants, solves and inverses",
        "Orthonormalise a basis with Gram-Schmidt and derive the QR factorisation from it",
        "Find a dominant eigenpair by power iteration and the smallest by inverse iteration",
        "Solve a least-squares problem and report its rank and condition number honestly",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone engine (60%).",
    "reading": [
        "Strang, *Introduction to Linear Algebra*, 6th ed. — chapters 1-6",
        "Trefethen & Bau, *Numerical Linear Algebra* — lectures 1-11 and 20-27",
        "Axler, *Linear Algebra Done Right*, 4th ed. — chapters 3, 5 and 6",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Vectors, matrices and the algebra of linear maps",
            "summary": "The objects themselves, and the operations that make them an algebra.",
            "concepts": [
                "A matrix is a linear map written in a chosen pair of bases",
                "Addition and scalar multiplication act entrywise; the m-by-n matrices form a vector space",
                "Matrix multiplication is composition of maps, hence associative but not commutative",
                "The (i, j) entry of AB is the dot product of row i of A with column j of B",
                "Shapes compose: (m x k)(k x n) -> (m x n), and nothing else is defined",
                "Transposition reverses products: (AB)^T = B^T A^T",
                "Floating-point equality needs a tolerance, so `equals` takes one and `==` picks a default",
            ],
            "lab": {
                "title": "A Matrix type over lists of lists",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Build a `Matrix` class storing rows as a list of lists of floats in
`self.rows`. Nothing else in the course is allowed to reach past that attribute.

## Construction

`Matrix(rows)` copies and converts to `float`. It raises `ValueError` for an
empty matrix, an empty row, rows of differing length, or a non-numeric entry
(booleans count as non-numeric here — `True` is not a number worth storing).

## The interface

- `shape` — a **property** giving `(number_of_rows, number_of_columns)`
- `Matrix.identity(n)` and `Matrix.zeros(rows, cols)` — **classmethods**;
  a non-positive dimension raises `ValueError`
- `m[i, j]` — entry access via a tuple index
- `a + b`, `a - b` — entrywise; mismatched shapes raise `ValueError`
- `a * b` — matrix product when `b` is a `Matrix`, scaling when it is a number;
  a shape mismatch raises `ValueError`
- `2 * a` — scaling from the left as well (`__rmul__`)
- `a.transpose()` — a new `Matrix`, rows and columns exchanged
- `a.equals(b, tol=1e-9)` — same shape and every entry within `tol`
- `a == b` — `equals` with the default tolerance; `False` against a non-Matrix
- `str(a)` — one line per row, entries formatted with `:g` and joined by two
  spaces, so `str(Matrix.identity(2))` is `"1  0\n0  1"`

```text
Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]])  ->  [[19, 22], [43, 50]]
Matrix([[1, 2, 3], [4, 5, 6]]).transpose().shape     ->  (3, 2)
```
''',
                "files": [{"name": "main.py", "content": r'''
class Matrix:
    """A dense matrix stored as a list of lists of floats."""

    def __init__(self, rows):
        # validate, convert to float, store in self.rows
        pass

    @property
    def shape(self):
        """(rows, columns)."""
        # your code here

    @classmethod
    def identity(cls, n):
        """The n-by-n identity."""
        # your code here

    @classmethod
    def zeros(cls, rows, cols):
        """An all-zero matrix of the given shape."""
        # your code here

    def __getitem__(self, index):
        """Entry access with a (row, column) tuple."""
        # your code here

    def __add__(self, other):
        # your code here
        pass

    def __sub__(self, other):
        # your code here
        pass

    def __mul__(self, other):
        """Matrix product with a Matrix, scaling with a number."""
        # your code here

    def __rmul__(self, scalar):
        # your code here
        pass

    def transpose(self):
        """A new Matrix with rows and columns exchanged."""
        # your code here

    def equals(self, other, tol=1e-9):
        """Same shape and every entry within tol."""
        # your code here

    def __eq__(self, other):
        # your code here
        pass

    def __repr__(self):
        return f"Matrix({self.rows!r})"

    def __str__(self):
        # your code here
        pass


a = Matrix([[1, 2], [3, 4]])
b = Matrix([[5, 6], [7, 8]])
print(a * b)
print(Matrix.identity(3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class Matrix:
    """A dense matrix stored as a list of lists of floats."""

    def __init__(self, rows):
        if not isinstance(rows, (list, tuple)) or len(rows) == 0:
            raise ValueError("a matrix needs at least one row")
        data = []
        width = None
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) == 0:
                raise ValueError("every row must be a non-empty sequence")
            if width is None:
                width = len(row)
            elif len(row) != width:
                raise ValueError("all rows must have the same length")
            converted = []
            for value in row:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError("entries must be numbers")
                converted.append(float(value))
            data.append(converted)
        self.rows = data

    @property
    def shape(self):
        """(rows, columns)."""
        return (len(self.rows), len(self.rows[0]))

    @classmethod
    def identity(cls, n):
        """The n-by-n identity."""
        if n < 1:
            raise ValueError("n must be positive")
        return cls([[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)])

    @classmethod
    def zeros(cls, rows, cols):
        """An all-zero matrix of the given shape."""
        if rows < 1 or cols < 1:
            raise ValueError("both dimensions must be positive")
        return cls([[0.0] * cols for _ in range(rows)])

    def __getitem__(self, index):
        """Entry access with a (row, column) tuple."""
        i, j = index
        return self.rows[i][j]

    def __add__(self, other):
        if not isinstance(other, Matrix) or other.shape != self.shape:
            raise ValueError("addition needs two matrices of the same shape")
        return Matrix([[x + y for x, y in zip(rx, ry)]
                       for rx, ry in zip(self.rows, other.rows)])

    def __sub__(self, other):
        if not isinstance(other, Matrix) or other.shape != self.shape:
            raise ValueError("subtraction needs two matrices of the same shape")
        return Matrix([[x - y for x, y in zip(rx, ry)]
                       for rx, ry in zip(self.rows, other.rows)])

    def __mul__(self, other):
        """Matrix product with a Matrix, scaling with a number."""
        if isinstance(other, Matrix):
            rows, inner = self.shape
            other_rows, cols = other.shape
            if inner != other_rows:
                raise ValueError("inner dimensions must agree")
            product = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    row.append(sum(self.rows[i][k] * other.rows[k][j]
                                   for k in range(inner)))
                product.append(row)
            return Matrix(product)
        if isinstance(other, bool) or not isinstance(other, (int, float)):
            raise ValueError("can only multiply by a Matrix or a number")
        return Matrix([[x * float(other) for x in row] for row in self.rows])

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def transpose(self):
        """A new Matrix with rows and columns exchanged."""
        rows, cols = self.shape
        return Matrix([[self.rows[i][j] for i in range(rows)] for j in range(cols)])

    def equals(self, other, tol=1e-9):
        """Same shape and every entry within tol."""
        if not isinstance(other, Matrix) or other.shape != self.shape:
            return False
        for rx, ry in zip(self.rows, other.rows):
            for x, y in zip(rx, ry):
                if abs(x - y) > tol:
                    return False
        return True

    def __eq__(self, other):
        return self.equals(other)

    def __repr__(self):
        return f"Matrix({self.rows!r})"

    def __str__(self):
        return "\n".join("  ".join(f"{value:g}" for value in row)
                         for row in self.rows)


a = Matrix([[1, 2], [3, 4]])
b = Matrix([[5, 6], [7, 8]])
print(a * b)
print(Matrix.identity(3))
'''}],
                "hints": [
                    "Do the validation in one pass in `__init__`: track the width of the first row, compare every later row against it, and convert entries with `float(value)` as you go.",
                    "`shape` is decorated with `@property`, so it is read as `m.shape` with no brackets; `identity` and `zeros` are `@classmethod` and build with `cls(...)` so subclasses keep working.",
                    "`__mul__` branches on `isinstance(other, Matrix)`. The product entry is `sum(self.rows[i][k] * other.rows[k][j] for k in range(inner))` — one loop over the shared inner dimension.",
                    "`__rmul__` only ever sees a scalar on the left, so it can simply delegate: `return self.__mul__(scalar)`.",
                ],
                "tests": [
                    {"name": "Construction, shape and entry access", "code": r'''
_m = Matrix([[1, 2, 3], [4, 5, 6]])
assert _m.shape == (2, 3), f"shape gave {_m.shape!r}, expected (2, 3)"
assert _m[0, 0] == 1.0 and _m[1, 2] == 6.0, f"Entry access gave {_m[0, 0]!r} and {_m[1, 2]!r}"
assert isinstance(_m[0, 0], float), "Entries should be stored as floats"
_src = [[1, 2], [3, 4]]
_copy = Matrix(_src)
_src[0][0] = 99
assert _copy[0, 0] == 1.0, "Matrix must copy its input, not alias it"
'''},
                    {"name": "Malformed input is refused", "code": r'''
for _bad in [[], [[]], [[1, 2], [3]], [[1, 2], []], "not a matrix", [[1, "a"]], [[1, None]]]:
    try:
        Matrix(_bad)
        assert False, f"Matrix({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "identity and zeros", "code": r'''
_i = Matrix.identity(3)
assert _i.shape == (3, 3), f"identity(3).shape is {_i.shape!r}"
for _r in range(3):
    for _c in range(3):
        _want = 1.0 if _r == _c else 0.0
        assert _i[_r, _c] == _want, f"identity(3)[{_r}, {_c}] is {_i[_r, _c]!r}, expected {_want}"
_z = Matrix.zeros(2, 4)
assert _z.shape == (2, 4), f"zeros(2, 4).shape is {_z.shape!r}"
assert all(_z[_r, _c] == 0.0 for _r in range(2) for _c in range(4)), "zeros must be all zero"
for _args in [(0,), (-2,)]:
    try:
        Matrix.identity(*_args)
        assert False, f"Matrix.identity{_args!r} should raise ValueError"
    except ValueError:
        pass
try:
    Matrix.zeros(2, 0)
    assert False, "Matrix.zeros(2, 0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Addition and subtraction", "code": r'''
_a = Matrix([[1, 2], [3, 4]])
_b = Matrix([[5, 6], [7, 8]])
assert (_a + _b).equals(Matrix([[6, 8], [10, 12]])), f"a + b gave {(_a + _b).rows!r}"
assert (_a - _b).equals(Matrix([[-4, -4], [-4, -4]])), f"a - b gave {(_a - _b).rows!r}"
assert _a.equals(Matrix([[1, 2], [3, 4]])), "Addition must not mutate its operands"
for _op in ("+", "-"):
    try:
        _a + Matrix([[1, 2, 3], [4, 5, 6]]) if _op == "+" else _a - Matrix([[1, 2, 3], [4, 5, 6]])
        assert False, f"Mismatched shapes under {_op} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Matrix and scalar multiplication", "code": r'''
_a = Matrix([[1, 2], [3, 4]])
_b = Matrix([[5, 6], [7, 8]])
assert (_a * _b).equals(Matrix([[19, 22], [43, 50]])), f"a * b gave {(_a * _b).rows!r}"
assert (_b * _a).equals(Matrix([[23, 34], [31, 46]])), \
    f"b * a gave {(_b * _a).rows!r}; the product is not commutative"
_c = Matrix([[1, 2, 3], [4, 5, 6]])
_d = Matrix([[7, 8], [9, 10], [11, 12]])
_p = _c * _d
assert _p.shape == (2, 2), f"(2x3)(3x2) should be 2x2, got {_p.shape!r}"
assert _p.equals(Matrix([[58, 64], [139, 154]])), f"Product gave {_p.rows!r}"
assert (_a * 2).equals(Matrix([[2, 4], [6, 8]])), f"a * 2 gave {(_a * 2).rows!r}"
assert (2 * _a).equals(Matrix([[2, 4], [6, 8]])), "2 * a needs __rmul__"
try:
    _c * _a
    assert False, "(2x3) * (2x2) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Identity acts as the unit", "code": r'''
_c = Matrix([[1, 2, 3], [4, 5, 6]])
assert (_c * Matrix.identity(3)).equals(_c), "A * I should be A"
assert (Matrix.identity(2) * _c).equals(_c), "I * A should be A"
_a = Matrix([[1, 2], [3, 4]])
_b = Matrix([[5, 6], [7, 8]])
_e = Matrix([[2, 0], [1, 3]])
assert ((_a * _b) * _e).equals(_a * (_b * _e)), "Matrix multiplication must be associative"
'''},
                    {"name": "Transpose and its product rule", "code": r'''
_c = Matrix([[1, 2, 3], [4, 5, 6]])
_t = _c.transpose()
assert _t.shape == (3, 2), f"transpose().shape is {_t.shape!r}, expected (3, 2)"
assert _t.equals(Matrix([[1, 4], [2, 5], [3, 6]])), f"transpose gave {_t.rows!r}"
assert _t.transpose().equals(_c), "Transposing twice returns the original"
_d = Matrix([[7, 8], [9, 10], [11, 12]])
assert (_c * _d).transpose().equals(_d.transpose() * _c.transpose()), \
    "(AB)^T should equal B^T A^T"
'''},
                    {"name": "Equality with a tolerance, and str", "code": r'''
_a = Matrix([[1.0, 2.0]])
_b = Matrix([[1.0 + 1e-12, 2.0]])
assert _a.equals(_b), "Entries within 1e-9 should compare equal"
assert not _a.equals(_b, tol=1e-15), "A tighter tolerance should reject them"
assert _a == _b, "== should use the default tolerance"
assert not (_a == Matrix([[1.0, 2.0, 3.0]])), "Different shapes are never equal"
assert not (_a == "not a matrix"), "Comparing against a non-Matrix must return False, not raise"
_s = str(Matrix.identity(2))
assert _s == "1  0\n0  1", f"str(identity(2)) gave {_s!r}, expected '1  0\\n0  1'"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Gaussian elimination, rank and determinant",
            "summary": "One algorithm that solves systems, measures rank and computes determinants.",
            "concepts": [
                "The three elementary row operations preserve the solution set",
                "Row echelon form: pivots move strictly right as you move down",
                "Partial pivoting picks the largest available pivot and bounds the growth of round-off",
                "Without pivoting a tiny pivot destroys accuracy even when the matrix is far from singular",
                "Rank is the number of pivots — equivalently the dimension of the column space",
                "The determinant is the product of the pivots, negated once per row interchange",
                "A square system is solvable for every right-hand side exactly when it has full rank",
            ],
            "lab": {
                "title": "Elimination with partial pivoting",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Work on plain lists of lists of numbers. Every function validates that its
argument is a non-empty rectangular matrix and raises `ValueError` otherwise.

**`forward_eliminate(a, tol=1e-12)`** — returns `(u, swaps)`: a *new* matrix in
row echelon form and the number of row interchanges performed. For each column
in turn, pick the row at or below the current pivot row with the largest
absolute entry in that column. If that entry is no bigger than `tol`, the column
carries no pivot — leave it and move on without advancing the pivot row.
Otherwise swap it into place, eliminate below it, and advance.

```text
forward_eliminate([[1, 2], [2, 4]])          ->  ([[2.0, 4.0], [0.0, 0.0]], 1)
forward_eliminate([[0, 0, 1], [0, 2, 3], [1, 4, 5]])
                                             ->  ([[1, 4, 5], [0, 2, 3], [0, 0, 1]], 1)
```

**`determinant(a)`** — square matrices only, otherwise `ValueError`. The product
of the diagonal of the echelon form, negated once per swap.

```text
determinant([[1, 2], [3, 4]])              ->  -2.0
determinant([[4, 3, 2], [1, 5, 7], [2, 2, 9]])  ->  123.0
determinant([[2, 0, 1], [1, 3, 2], [1, 1, 1]])  ->  0.0
```

**`rank(a, tol=1e-9)`** — how many rows of the echelon form are not entirely
zero (to within `tol`).

**`solve(a, b)`** — the unique solution of a square system, by eliminating on
the augmented matrix and then back-substituting. Raise `ValueError` when `a` is
not square, when `len(b)` does not match, or when any diagonal entry of the
reduced augmented matrix is at most `1e-12` in absolute value — that last case
is the singular system, and returning a wrong answer would be worse than
raising.

```text
solve([[2, 1], [1, 3]], [3, 5])  ->  [0.8, 1.4]
solve([[0, 1], [1, 0]], [1, 2])  ->  [2.0, 1.0]
```
''',
                "files": [{"name": "main.py", "content": r'''
def shape(a):
    """(rows, cols) after checking a is a non-empty rectangular matrix."""
    # your code here


def forward_eliminate(a, tol=1e-12):
    """(row echelon form, number of row swaps) with partial pivoting."""
    # your code here


def determinant(a):
    """Determinant of a square matrix, by elimination."""
    # your code here


def rank(a, tol=1e-9):
    """Number of non-zero rows in the row echelon form."""
    # your code here


def solve(a, b):
    """Unique solution of a square system; ValueError when singular."""
    # your code here


print(determinant([[4, 3, 2], [1, 5, 7], [2, 2, 9]]))
print(solve([[2, 1], [1, 3]], [3, 5]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def shape(a):
    """(rows, cols) after checking a is a non-empty rectangular matrix."""
    if not isinstance(a, list) or not a:
        raise ValueError("matrix must be a non-empty list of rows")
    cols = None
    for row in a:
        if not isinstance(row, list) or not row:
            raise ValueError("every row must be a non-empty list")
        if cols is None:
            cols = len(row)
        elif len(row) != cols:
            raise ValueError("all rows must have the same length")
    return (len(a), cols)


def forward_eliminate(a, tol=1e-12):
    """(row echelon form, number of row swaps) with partial pivoting."""
    rows, cols = shape(a)
    u = [[float(x) for x in row] for row in a]
    swaps = 0
    pivot = 0
    for col in range(cols):
        if pivot >= rows:
            break
        best = pivot
        for r in range(pivot + 1, rows):
            if abs(u[r][col]) > abs(u[best][col]):
                best = r
        if abs(u[best][col]) <= tol:
            continue
        if best != pivot:
            u[pivot], u[best] = u[best], u[pivot]
            swaps += 1
        for r in range(pivot + 1, rows):
            factor = u[r][col] / u[pivot][col]
            if factor != 0.0:
                for c in range(col, cols):
                    u[r][c] -= factor * u[pivot][c]
            u[r][col] = 0.0
        pivot += 1
    return (u, swaps)


def determinant(a):
    """Determinant of a square matrix, by elimination."""
    rows, cols = shape(a)
    if rows != cols:
        raise ValueError("determinant needs a square matrix")
    u, swaps = forward_eliminate(a)
    value = -1.0 if swaps % 2 else 1.0
    for i in range(rows):
        value *= u[i][i]
    return value


def rank(a, tol=1e-9):
    """Number of non-zero rows in the row echelon form."""
    u, _ = forward_eliminate(a)
    count = 0
    for row in u:
        if any(abs(x) > tol for x in row):
            count += 1
    return count


def solve(a, b):
    """Unique solution of a square system; ValueError when singular."""
    rows, cols = shape(a)
    if rows != cols:
        raise ValueError("solve needs a square matrix")
    if len(b) != rows:
        raise ValueError("b must have one entry per row")
    augmented = [[float(x) for x in a[i]] + [float(b[i])] for i in range(rows)]
    u, _ = forward_eliminate(augmented)
    for i in range(rows):
        if abs(u[i][i]) <= 1e-12:
            raise ValueError("matrix is singular")
    x = [0.0] * rows
    for i in range(rows - 1, -1, -1):
        total = u[i][cols]
        for j in range(i + 1, rows):
            total -= u[i][j] * x[j]
        x[i] = total / u[i][i]
    return x


print(determinant([[4, 3, 2], [1, 5, 7], [2, 2, 9]]))
print(solve([[2, 1], [1, 3]], [3, 5]))
'''}],
                "hints": [
                    "Copy the input before touching it: `u = [[float(x) for x in row] for row in a]`. Every one of these routines must leave its argument untouched.",
                    "Track the pivot row separately from the column index. A column with no usable pivot advances `col` but not `pivot` — that is exactly what makes the routine work on non-square and rank-deficient matrices.",
                    "After eliminating, assign `u[r][col] = 0.0` outright rather than trusting the subtraction to give a clean zero.",
                    "`solve` eliminates on the augmented matrix `A | b`, so the right-hand side rides along through the swaps for free; then back-substitute from the bottom row upwards.",
                ],
                "tests": [
                    {"name": "shape validates and reports", "code": r'''
assert shape([[1, 2, 3], [4, 5, 6]]) == (2, 3), f"Got {shape([[1, 2, 3], [4, 5, 6]])!r}"
assert shape([[7]]) == (1, 1), "A 1x1 matrix is still a matrix"
for _bad in [[], [[]], [[1, 2], [3]], "nope", [[1, 2], 3]]:
    try:
        shape(_bad)
        assert False, f"shape({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Echelon form and swap counting", "code": r'''
_u, _s = forward_eliminate([[1, 2], [2, 4]])
assert _s == 1, f"Partial pivoting should swap the larger row up; swaps was {_s}"
assert abs(_u[0][0] - 2.0) < 1e-12 and abs(_u[0][1] - 4.0) < 1e-12, f"First row is {_u[0]!r}"
assert all(abs(x) < 1e-12 for x in _u[1]), f"Second row should be zero, got {_u[1]!r}"
_a = [[0, 0, 1], [0, 2, 3], [1, 4, 5]]
_u, _s = forward_eliminate(_a)
assert _a == [[0, 0, 1], [0, 2, 3], [1, 4, 5]], "forward_eliminate must not mutate its argument"
for _i in range(3):
    for _j in range(_i):
        assert abs(_u[_i][_j]) < 1e-12, f"Entry ({_i}, {_j}) below the diagonal is {_u[_i][_j]!r}"
_u, _s = forward_eliminate([[0, 0], [0, 0]])
assert _s == 0 and all(abs(x) < 1e-12 for row in _u for x in row), f"Zero matrix gave {(_u, _s)!r}"
'''},
                    {"name": "Determinants", "code": r'''
for _name, _a, _want in [("2x2", [[1, 2], [3, 4]], -2.0),
                         ("3x3", [[4, 3, 2], [1, 5, 7], [2, 2, 9]], 123.0),
                         ("singular", [[2, 0, 1], [1, 3, 2], [1, 1, 1]], 0.0),
                         ("identity", [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1.0),
                         ("1x1", [[7]], 7.0),
                         ("swap", [[0, 1], [1, 0]], -1.0),
                         ("4x4", [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 13], [1, 0, 0, 1]], 4.0)]:
    _got = determinant(_a)
    assert abs(_got - _want) < 1e-9, f"determinant of the {_name} case gave {_got!r}, expected {_want}"
try:
    determinant([[1, 2, 3], [4, 5, 6]])
    assert False, "determinant of a non-square matrix should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Rank counts the pivots", "code": r'''
for _name, _a, _want in [("dependent rows", [[1, 2], [2, 4]], 1),
                         ("full 2x2", [[1, 2], [3, 4]], 2),
                         ("magic-ish 3x3", [[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2),
                         ("zero matrix", [[0, 0, 0], [0, 0, 0]], 0),
                         ("wide", [[1, 2, 3], [4, 5, 6]], 2),
                         ("tall", [[1, 2], [3, 4], [5, 6]], 2),
                         ("1x1 zero", [[0]], 0)]:
    _got = rank(_a)
    assert _got == _want, f"rank of the {_name} case gave {_got!r}, expected {_want}"
'''},
                    {"name": "Solving square systems", "code": r'''
_x = solve([[2, 1], [1, 3]], [3, 5])
assert abs(_x[0] - 0.8) < 1e-12 and abs(_x[1] - 1.4) < 1e-12, f"solve gave {_x!r}, expected [0.8, 1.4]"
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_x = solve(_a, [1, 2, 3])
for _row, _rhs in zip(_a, [1, 2, 3]):
    _lhs = sum(_c * _v for _c, _v in zip(_row, _x))
    assert abs(_lhs - _rhs) < 1e-9, f"Solution does not satisfy the system: {_lhs!r} vs {_rhs}"
assert abs(_x[0] - 6.0 / 41.0) < 1e-12, f"x[0] is {_x[0]!r}, expected 6/41"
_x = solve([[5]], [10])
assert abs(_x[0] - 2.0) < 1e-12, f"A 1x1 system gave {_x!r}, expected [2.0]"
'''},
                    {"name": "Pivoting handles a zero leading entry", "code": r'''
_x = solve([[0, 1], [1, 0]], [1, 2])
assert abs(_x[0] - 2.0) < 1e-12 and abs(_x[1] - 1.0) < 1e-12, \
    f"solve gave {_x!r}, expected [2.0, 1.0] — the first pivot must be swapped in"
_a = [[1e-14, 1.0], [1.0, 1.0]]
_x = solve(_a, [1.0, 2.0])
for _row, _rhs in zip(_a, [1.0, 2.0]):
    _lhs = _row[0] * _x[0] + _row[1] * _x[1]
    assert abs(_lhs - _rhs) < 1e-8, \
        f"A tiny leading pivot wrecked the accuracy: {_lhs!r} vs {_rhs} — pivot on the largest entry"
'''},
                    {"name": "Singular and malformed systems are refused", "code": r'''
try:
    solve([[1, 2], [2, 4]], [1, 2])
    assert False, "A singular system should raise ValueError, not return a wrong answer"
except ValueError:
    pass
try:
    solve([[1, 2, 3], [4, 5, 6]], [1, 2])
    assert False, "A non-square system should raise ValueError"
except ValueError:
    pass
try:
    solve([[1, 2], [3, 4]], [1, 2, 3])
    assert False, "A mismatched right-hand side should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "LU factorisation and reuse",
            "summary": "Doing the elimination once and spending the result many times.",
            "concepts": [
                "Elimination is a factorisation: PA = LU with L unit lower triangular",
                "The multipliers you would have discarded are exactly the entries of L",
                "Factorising costs O(n^3); each later solve costs only O(n^2)",
                "det(A) = det(P)^-1 * product of the diagonal of U, and det(P) is the swap parity",
                "Forward substitution on Pb, then back substitution on U, gives x",
                "The inverse is n solves against the columns of the identity — never how you should solve Ax = b",
                "A zero pivot in exact arithmetic means singular; in floating point it means a tolerance test",
            ],
            "lab": {
                "title": "PA = LU, and what the factors buy you",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
**`lu_decompose(a, tol=1e-12)`** — returns `(l, u, perm, sign)` for a square
`a`, where

- `l` is unit lower triangular (ones on the diagonal, multipliers below),
- `u` is upper triangular,
- `perm` is a list of the original row indices in their new order, so
  `[a[perm[i]] for i in range(n)] == l @ u`,
- `sign` is `1.0` or `-1.0`, the determinant of the permutation.

Choose each pivot by partial pivoting. When the best available pivot is no
bigger than `tol` the matrix is singular — raise `ValueError`. A non-square
argument also raises.

```text
lu_decompose([[4, 3, 2], [1, 5, 7], [2, 2, 9]])
  l -> [[1, 0, 0], [0.25, 1, 0], [0.5, 0.11764705882352941, 1]]
  u -> [[4, 3, 2], [0, 4.25, 6.5], [0, 0, 7.235294117647059]]
  perm -> [0, 1, 2],  sign -> 1.0
```

**`det_from_lu(u, sign)`** — `sign` times the product of the diagonal of `u`.

**`lu_solve(l, u, perm, b)`** — forward substitution for `y` (remembering that
row `i` of the permuted system uses `b[perm[i]]`), then back substitution for
`x`. A right-hand side of the wrong length raises `ValueError`.

**`inverse(a)`** — factor once, then solve against each column of the identity
and assemble the columns into the result.

```text
inverse([[4, 7], [2, 6]])  ->  [[0.6, -0.7], [-0.2, 0.4]]
```
''',
                "files": [{"name": "main.py", "content": r'''
def square_size(a):
    """n after checking a is a non-empty square matrix."""
    # your code here


def lu_decompose(a, tol=1e-12):
    """(l, u, perm, sign) with PA = LU and partial pivoting."""
    # your code here


def det_from_lu(u, sign):
    """Determinant read off an LU factorisation."""
    # your code here


def lu_solve(l, u, perm, b):
    """Solve A x = b from the factors of A."""
    # your code here


def inverse(a):
    """The inverse of a, one solve per column of the identity."""
    # your code here


print(lu_decompose([[4, 3, 2], [1, 5, 7], [2, 2, 9]]))
print(inverse([[4, 7], [2, 6]]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def square_size(a):
    """n after checking a is a non-empty square matrix."""
    if not isinstance(a, list) or not a:
        raise ValueError("matrix must be a non-empty list of rows")
    n = len(a)
    for row in a:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("matrix must be square")
    return n


def lu_decompose(a, tol=1e-12):
    """(l, u, perm, sign) with PA = LU and partial pivoting."""
    n = square_size(a)
    u = [[float(x) for x in row] for row in a]
    l = [[0.0] * n for _ in range(n)]
    perm = list(range(n))
    sign = 1.0
    for col in range(n):
        best = col
        for r in range(col + 1, n):
            if abs(u[r][col]) > abs(u[best][col]):
                best = r
        if abs(u[best][col]) <= tol:
            raise ValueError("matrix is singular")
        if best != col:
            u[col], u[best] = u[best], u[col]
            l[col], l[best] = l[best], l[col]
            perm[col], perm[best] = perm[best], perm[col]
            sign = -sign
        for r in range(col + 1, n):
            factor = u[r][col] / u[col][col]
            l[r][col] = factor
            for c in range(col, n):
                u[r][c] -= factor * u[col][c]
            u[r][col] = 0.0
    for i in range(n):
        l[i][i] = 1.0
    return (l, u, perm, sign)


def det_from_lu(u, sign):
    """Determinant read off an LU factorisation."""
    value = float(sign)
    for i in range(len(u)):
        value *= u[i][i]
    return value


def lu_solve(l, u, perm, b):
    """Solve A x = b from the factors of A."""
    n = len(l)
    if len(b) != n:
        raise ValueError("b must have one entry per row")
    y = [0.0] * n
    for i in range(n):
        total = float(b[perm[i]])
        for j in range(i):
            total -= l[i][j] * y[j]
        y[i] = total
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        total = y[i]
        for j in range(i + 1, n):
            total -= u[i][j] * x[j]
        x[i] = total / u[i][i]
    return x


def inverse(a):
    """The inverse of a, one solve per column of the identity."""
    n = square_size(a)
    l, u, perm, _ = lu_decompose(a)
    columns = []
    for j in range(n):
        unit = [1.0 if i == j else 0.0 for i in range(n)]
        columns.append(lu_solve(l, u, perm, unit))
    return [[columns[j][i] for j in range(n)] for i in range(n)]


print(lu_decompose([[4, 3, 2], [1, 5, 7], [2, 2, 9]]))
print(inverse([[4, 7], [2, 6]]))
'''}],
                "hints": [
                    "Swap rows of `l`, of `u` and of `perm` together, and flip `sign` each time. Filling the diagonal of `l` with ones at the very end keeps the swap logic simple.",
                    "The multiplier `factor = u[r][col] / u[col][col]` is stored in `l[r][col]` and then used to eliminate — nothing is thrown away, which is the whole point of LU.",
                    "In `lu_solve`, the permutation is applied to the right-hand side, not to the factors: row `i` starts from `b[perm[i]]`.",
                    "`inverse` calls `lu_decompose` exactly once and `lu_solve` n times. The solve for column j returns a *column* of the inverse, so transpose the collected list at the end.",
                ],
                "tests": [
                    {"name": "The factors have the right shape", "code": r'''
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_l, _u, _perm, _sign = lu_decompose(_a)
assert sorted(_perm) == [0, 1, 2], f"perm should be a permutation of 0..2, got {_perm!r}"
assert _sign in (1.0, -1.0), f"sign was {_sign!r}, expected 1.0 or -1.0"
for _i in range(3):
    assert abs(_l[_i][_i] - 1.0) < 1e-12, f"l[{_i}][{_i}] is {_l[_i][_i]!r}, expected 1.0 (unit diagonal)"
    for _j in range(_i + 1, 3):
        assert abs(_l[_i][_j]) < 1e-12, f"l[{_i}][{_j}] is {_l[_i][_j]!r}; l must be lower triangular"
        assert abs(_u[_j][_i]) < 1e-12, f"u[{_j}][{_i}] is {_u[_j][_i]!r}; u must be upper triangular"
assert _a == [[4, 3, 2], [1, 5, 7], [2, 2, 9]], "lu_decompose must not mutate its argument"
'''},
                    {"name": "L times U reproduces the permuted matrix", "code": r'''
def _mm(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(len(y))) for j in range(len(y[0]))]
            for i in range(len(x))]
for _a in [[[4, 3, 2], [1, 5, 7], [2, 2, 9]],
           [[0, 1], [1, 0]],
           [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
           [[2, 1, 1, 0], [4, 3, 3, 1], [8, 7, 9, 5], [6, 7, 9, 8]]]:
    _l, _u, _perm, _sign = lu_decompose(_a)
    _lu = _mm(_l, _u)
    for _i in range(len(_a)):
        for _j in range(len(_a)):
            _want = float(_a[_perm[_i]][_j])
            assert abs(_lu[_i][_j] - _want) < 1e-9, \
                f"(LU)[{_i}][{_j}] is {_lu[_i][_j]!r}, but row perm[{_i}] of A has {_want!r} there"
'''},
                    {"name": "Determinant from the factors", "code": r'''
for _name, _a, _want in [("3x3", [[4, 3, 2], [1, 5, 7], [2, 2, 9]], 123.0),
                         ("2x2", [[1, 2], [3, 4]], -2.0),
                         ("swap", [[0, 1], [1, 0]], -1.0),
                         ("identity", [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1.0),
                         ("1x1", [[7]], 7.0),
                         ("2x2 det 10", [[4, 7], [2, 6]], 10.0)]:
    _l, _u, _perm, _sign = lu_decompose(_a)
    _got = det_from_lu(_u, _sign)
    assert abs(_got - _want) < 1e-9, f"det of the {_name} case gave {_got!r}, expected {_want}"
'''},
                    {"name": "Singular and non-square input", "code": r'''
for _bad in [[[1, 2], [2, 4]], [[0, 0], [0, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]:
    try:
        lu_decompose(_bad)
        assert False, f"lu_decompose({_bad!r}) should raise ValueError — it is singular"
    except ValueError:
        pass
for _bad in [[[1, 2, 3], [4, 5, 6]], [], [[1, 2], [3]]]:
    try:
        lu_decompose(_bad)
        assert False, f"lu_decompose({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Solving from the factors", "code": r'''
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_l, _u, _perm, _sign = lu_decompose(_a)
_x = lu_solve(_l, _u, _perm, [1, 2, 3])
for _row, _rhs in zip(_a, [1, 2, 3]):
    _lhs = sum(_c * _v for _c, _v in zip(_row, _x))
    assert abs(_lhs - _rhs) < 1e-9, f"Solution does not satisfy the system: {_lhs!r} vs {_rhs}"
assert abs(_x[0] - 6.0 / 41.0) < 1e-12, f"x[0] is {_x[0]!r}, expected 6/41"
_l2, _u2, _p2, _s2 = lu_decompose([[0, 1], [1, 0]])
_x = lu_solve(_l2, _u2, _p2, [1, 2])
assert abs(_x[0] - 2.0) < 1e-12 and abs(_x[1] - 1.0) < 1e-12, \
    f"Got {_x!r}, expected [2.0, 1.0] — the permutation must be applied to b"
try:
    lu_solve(_l, _u, _perm, [1, 2])
    assert False, "A right-hand side of the wrong length should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The factors are reusable", "code": r'''
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_l, _u, _perm, _sign = lu_decompose(_a)
for _b in ([1, 0, 0], [0, 1, 0], [1, 2, 3], [-4, 7, 0.5]):
    _x = lu_solve(_l, _u, _perm, _b)
    for _row, _rhs in zip(_a, _b):
        _lhs = sum(_c * _v for _c, _v in zip(_row, _x))
        assert abs(_lhs - _rhs) < 1e-9, \
            f"Re-solving with b={_b!r} failed: {_lhs!r} vs {_rhs} — the factors must survive a solve"
'''},
                    {"name": "The inverse", "code": r'''
_inv = inverse([[4, 7], [2, 6]])
_want = [[0.6, -0.7], [-0.2, 0.4]]
for _i in range(2):
    for _j in range(2):
        assert abs(_inv[_i][_j] - _want[_i][_j]) < 1e-12, \
            f"inverse[{_i}][{_j}] is {_inv[_i][_j]!r}, expected {_want[_i][_j]!r}"
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_inv = inverse(_a)
_prod = [[sum(_a[i][k] * _inv[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
for _i in range(3):
    for _j in range(3):
        _target = 1.0 if _i == _j else 0.0
        assert abs(_prod[_i][_j] - _target) < 1e-9, \
            f"(A A^-1)[{_i}][{_j}] is {_prod[_i][_j]!r}, expected {_target}"
assert abs(inverse([[4]])[0][0] - 0.25) < 1e-12, f"inverse([[4]]) gave {inverse([[4]])!r}"
try:
    inverse([[1, 2], [2, 4]])
    assert False, "inverse of a singular matrix should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Orthogonality and eigenstructure",
            "summary": "Orthonormal bases, the QR factorisation, and iterating towards an eigenvector.",
            "concepts": [
                "The dot product measures both length and angle; orthogonal means dot product zero",
                "Gram-Schmidt subtracts the projection onto everything already accepted",
                "A residual that vanishes signals linear dependence, not bad luck",
                "QR: the orthonormalised columns form Q, and R[i][j] is the projection of column j onto q_i",
                "Q^T Q = I, so an orthogonal change of basis preserves lengths and cannot amplify error",
                "Power iteration converges to the dominant eigenvector at rate |lambda_2 / lambda_1|",
                "The Rayleigh quotient v^T A v is the best eigenvalue estimate for a given v",
            ],
            "lab": {
                "title": "Gram-Schmidt, QR and the power method",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
**`dot(u, v)`** and **`norm(v)`** — the usual definitions; mismatched lengths
raise `ValueError`.

**`matvec(a, v)`** — the matrix-vector product, `ValueError` on a shape
mismatch.

**`gram_schmidt(vectors, tol=1e-10)`** — orthonormalise a list of vectors, in
order. For each input vector, subtract its projection onto every basis vector
already accepted, then normalise what is left. A residual whose norm is at most
`tol` means the vector lay in the span of the earlier ones — raise `ValueError`.
An empty list also raises.

```text
gram_schmidt([[3.0, 0.0], [0.0, -2.0]])  ->  [[1.0, 0.0], [0.0, -1.0]]
gram_schmidt([[1, 2], [2, 4]])           ->  ValueError
```

**`qr(a)`** — for `a` with at least as many rows as columns and full column
rank, return `(q, r)` where `q` has the orthonormalised columns of `a` and
`r[i][j] = dot(q_i, a_j)` for `i <= j`, zero below. Because each `r[i][i]` is
the length of a residual, the diagonal of `R` comes out positive.

```text
qr([[12, -51], [6, 167], [-4, 24]])  ->  r = [[14, 21], [0, 175]]
```

**`power_method(a, tol=1e-10, max_iter=1000)`** — returns
`(eigenvalue, eigenvector, iterations)`. Start from the unit vector with every
component `1/sqrt(n)`. Each step forms `w = A v`, takes the Rayleigh quotient
`v . w` as the new eigenvalue estimate, and replaces `v` by `w / norm(w)`.
Stop once two consecutive estimates differ by at most `tol`. Return the
eigenvector scaled so its largest-magnitude component is positive. A non-square
matrix, a collapse to the zero vector, or exhausting `max_iter` all raise
`ValueError`.

```text
power_method([[4.0, 1.0], [2.0, 3.0]])  ->  (5.0, [0.7071..., 0.7071...], 2)
power_method([[3.0, 0.0], [0.0, -7.0]]) ->  (-7.0, [0.0, 1.0], ...)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def dot(u, v):
    """Dot product of two equal-length vectors."""
    # your code here


def norm(v):
    """Euclidean length."""
    # your code here


def matvec(a, v):
    """Matrix times vector."""
    # your code here


def gram_schmidt(vectors, tol=1e-10):
    """Orthonormalise a list of vectors; ValueError if they are dependent."""
    # your code here


def qr(a):
    """(q, r) with orthonormal columns in q and upper triangular r."""
    # your code here


def power_method(a, tol=1e-10, max_iter=1000):
    """(dominant eigenvalue, unit eigenvector, iterations used)."""
    # your code here


print(gram_schmidt([[1.0, 1.0], [1.0, 0.0]]))
print(qr([[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]])[1])
print(power_method([[4.0, 1.0], [2.0, 3.0]]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def dot(u, v):
    """Dot product of two equal-length vectors."""
    if len(u) != len(v):
        raise ValueError("vectors must have the same length")
    return sum(float(x) * float(y) for x, y in zip(u, v))


def norm(v):
    """Euclidean length."""
    return math.sqrt(dot(v, v))


def matvec(a, v):
    """Matrix times vector."""
    if not a or len(a[0]) != len(v):
        raise ValueError("column count must match the vector length")
    return [dot(row, v) for row in a]


def gram_schmidt(vectors, tol=1e-10):
    """Orthonormalise a list of vectors; ValueError if they are dependent."""
    if not vectors:
        raise ValueError("need at least one vector")
    basis = []
    for vector in vectors:
        residual = [float(x) for x in vector]
        for q in basis:
            projection = dot(q, residual)
            residual = [r - projection * qi for r, qi in zip(residual, q)]
        length = norm(residual)
        if length <= tol:
            raise ValueError("vectors are linearly dependent")
        basis.append([r / length for r in residual])
    return basis


def qr(a):
    """(q, r) with orthonormal columns in q and upper triangular r."""
    if not a or not a[0]:
        raise ValueError("matrix must be non-empty")
    rows = len(a)
    cols = len(a[0])
    if rows < cols:
        raise ValueError("need at least as many rows as columns")
    columns = [[float(a[i][j]) for i in range(rows)] for j in range(cols)]
    basis = gram_schmidt(columns)
    q = [[basis[j][i] for j in range(cols)] for i in range(rows)]
    r = [[0.0] * cols for _ in range(cols)]
    for i in range(cols):
        for j in range(i, cols):
            r[i][j] = dot(basis[i], columns[j])
    return (q, r)


def power_method(a, tol=1e-10, max_iter=1000):
    """(dominant eigenvalue, unit eigenvector, iterations used)."""
    if not a:
        raise ValueError("matrix must be non-empty")
    n = len(a)
    for row in a:
        if len(row) != n:
            raise ValueError("power_method needs a square matrix")
    v = [1.0 / math.sqrt(n)] * n
    value = 0.0
    used = 0
    converged = False
    for step in range(1, max_iter + 1):
        w = matvec(a, v)
        length = norm(w)
        if length <= 1e-300:
            raise ValueError("iteration collapsed to the zero vector")
        estimate = dot(v, w)
        v = [x / length for x in w]
        used = step
        if step > 1 and abs(estimate - value) <= tol:
            value = estimate
            converged = True
            break
        value = estimate
    if not converged:
        raise ValueError("power method did not converge")
    biggest = 0
    for i in range(n):
        if abs(v[i]) > abs(v[biggest]):
            biggest = i
    if v[biggest] < 0:
        v = [-x for x in v]
    return (value, v, used)


print(gram_schmidt([[1.0, 1.0], [1.0, 0.0]]))
print(qr([[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]])[1])
print(power_method([[4.0, 1.0], [2.0, 3.0]]))
'''}],
                "hints": [
                    "Gram-Schmidt is one loop with an inner loop: for every already-accepted `q`, compute `dot(q, residual)` and subtract that multiple of `q` from the residual.",
                    "Work with the *columns* of `a` in `qr`. Building the column list first, orthonormalising it, and only then stitching `q` back together as rows keeps the indices straight.",
                    "`r[i][j] = dot(basis[i], columns[j])` uses the ORIGINAL columns, not the orthonormalised ones — that is what makes `q @ r` reproduce `a`.",
                    "In `power_method`, compute the Rayleigh quotient with the *old* unit vector (`dot(v, w)`) before replacing `v`; compare consecutive estimates, and only fix the sign of the final eigenvector.",
                ],
                "tests": [
                    {"name": "dot, norm and matvec", "code": r'''
assert dot([1, 2, 3], [4, 5, 6]) == 32.0, f"dot gave {dot([1, 2, 3], [4, 5, 6])!r}, expected 32"
assert abs(norm([3, 4]) - 5.0) < 1e-12, f"norm([3, 4]) gave {norm([3, 4])!r}, expected 5.0"
assert norm([0.0, 0.0]) == 0.0, "The zero vector has length 0"
assert matvec([[1, 2], [3, 4]], [1, 1]) == [3.0, 7.0], \
    f"matvec gave {matvec([[1, 2], [3, 4]], [1, 1])!r}, expected [3.0, 7.0]"
assert matvec([[1, 2, 3], [4, 5, 6]], [1, 0, -1]) == [-2.0, -2.0], \
    f"matvec gave {matvec([[1, 2, 3], [4, 5, 6]], [1, 0, -1])!r}"
for _args in [([1, 2], [1, 2, 3]),]:
    try:
        dot(*_args)
        assert False, f"dot{_args!r} should raise ValueError"
    except ValueError:
        pass
try:
    matvec([[1, 2], [3, 4]], [1, 2, 3])
    assert False, "matvec with a mismatched vector should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Gram-Schmidt produces an orthonormal set", "code": r'''
_b = gram_schmidt([[3.0, 0.0], [0.0, -2.0]])
assert abs(_b[0][0] - 1.0) < 1e-12 and abs(_b[0][1]) < 1e-12, f"First vector is {_b[0]!r}"
assert abs(_b[1][1] + 1.0) < 1e-12, f"Second vector is {_b[1]!r}; normalising must not flip the sign"
_b = gram_schmidt([[1.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])
for _i in range(3):
    assert abs(norm(_b[_i]) - 1.0) < 1e-12, f"Vector {_i} has length {norm(_b[_i])!r}, expected 1"
    for _j in range(_i + 1, 3):
        assert abs(dot(_b[_i], _b[_j])) < 1e-12, \
            f"Vectors {_i} and {_j} have dot product {dot(_b[_i], _b[_j])!r}, expected 0"
'''},
                    {"name": "Gram-Schmidt detects dependence", "code": r'''
for _bad in [[[1.0, 2.0], [2.0, 4.0]],
             [[1.0, 0.0], [0.0, 1.0], [3.0, 4.0]],
             [[0.0, 0.0], [1.0, 0.0]]]:
    try:
        gram_schmidt(_bad)
        assert False, f"gram_schmidt({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    gram_schmidt([])
    assert False, "gram_schmidt([]) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "QR reproduces the matrix", "code": r'''
def _mm(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(len(y))) for j in range(len(y[0]))]
            for i in range(len(x))]
_a = [[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]]
_q, _r = qr(_a)
assert len(_q) == 3 and len(_q[0]) == 2, f"q has shape {(len(_q), len(_q[0]))!r}, expected (3, 2)"
assert len(_r) == 2 and len(_r[0]) == 2, f"r has shape {(len(_r), len(_r[0]))!r}, expected (2, 2)"
_prod = _mm(_q, _r)
for _i in range(3):
    for _j in range(2):
        assert abs(_prod[_i][_j] - _a[_i][_j]) < 1e-9, \
            f"(QR)[{_i}][{_j}] is {_prod[_i][_j]!r}, expected {_a[_i][_j]!r}"
assert abs(_r[0][0] - 14.0) < 1e-9 and abs(_r[0][1] - 21.0) < 1e-9 and abs(_r[1][1] - 175.0) < 1e-9, \
    f"r came out as {_r!r}, expected [[14, 21], [0, 175]]"
assert abs(_r[1][0]) < 1e-12, f"r[1][0] is {_r[1][0]!r}; R must be upper triangular"
'''},
                    {"name": "Q has orthonormal columns", "code": r'''
def _mm(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(len(y))) for j in range(len(y[0]))]
            for i in range(len(x))]
_a = [[1.0, 1.0], [1.0, 2.0], [1.0, 3.0], [1.0, 4.0]]
_q, _r = qr(_a)
_qt = [[_q[i][j] for i in range(4)] for j in range(2)]
_gram = _mm(_qt, _q)
for _i in range(2):
    for _j in range(2):
        _want = 1.0 if _i == _j else 0.0
        assert abs(_gram[_i][_j] - _want) < 1e-12, \
            f"(Q^T Q)[{_i}][{_j}] is {_gram[_i][_j]!r}, expected {_want}"
assert abs(_r[0][0] - 2.0) < 1e-12 and abs(_r[0][1] - 5.0) < 1e-12, f"r is {_r!r}"
assert abs(_r[1][1] - math.sqrt(5.0)) < 1e-12, f"r[1][1] is {_r[1][1]!r}, expected sqrt(5)"
assert all(_r[_i][_i] > 0 for _i in range(2)), "Gram-Schmidt gives a positive diagonal in R"
try:
    qr([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert False, "A wide matrix has dependent columns; qr should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Power method finds the dominant eigenpair", "code": r'''
_value, _vector, _steps = power_method([[4.0, 1.0], [2.0, 3.0]])
assert abs(_value - 5.0) < 1e-8, f"Dominant eigenvalue came out as {_value!r}, expected 5.0"
_r2 = math.sqrt(0.5)
assert abs(_vector[0] - _r2) < 1e-6 and abs(_vector[1] - _r2) < 1e-6, \
    f"Eigenvector is {_vector!r}, expected about [{_r2!r}, {_r2!r}]"
assert _steps >= 1, f"iterations came back as {_steps!r}"
_value, _vector, _ = power_method([[2.0, 1.0], [1.0, 2.0]])
assert abs(_value - 3.0) < 1e-8, f"Symmetric case gave {_value!r}, expected 3.0"
_value, _vector, _ = power_method([[6.0, 2.0, 1.0], [2.0, 3.0, 1.0], [1.0, 1.0, 1.0]])
assert abs(_value - 7.287992138960425) < 1e-6, f"3x3 case gave {_value!r}, expected 7.28799213896"
_residual = [x - _value * y for x, y in zip(matvec([[6.0, 2.0, 1.0], [2.0, 3.0, 1.0], [1.0, 1.0, 1.0]], _vector), _vector)]
assert norm(_residual) < 1e-5, f"A v - lambda v has norm {norm(_residual)!r}, expected about 0"
'''},
                    {"name": "Eigenvalue sign, scaling and refusal", "code": r'''
_value, _vector, _ = power_method([[3.0, 0.0], [0.0, -7.0]])
assert abs(_value + 7.0) < 1e-6, f"Dominance is by magnitude: got {_value!r}, expected -7.0"
assert abs(abs(_vector[1]) - 1.0) < 1e-5, f"Eigenvector is {_vector!r}, expected about [0, 1]"
_biggest = 0 if abs(_vector[0]) > abs(_vector[1]) else 1
assert _vector[_biggest] > 0, f"The largest component of {_vector!r} should be positive"
assert abs(norm(_vector) - 1.0) < 1e-9, f"The eigenvector should be a unit vector; norm is {norm(_vector)!r}"
_value, _vector, _ = power_method([[1.0, 0.0], [0.0, 1.0]])
assert abs(_value - 1.0) < 1e-9, f"The identity has eigenvalue 1; got {_value!r}"
try:
    power_method([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert False, "power_method on a non-square matrix should raise ValueError"
except ValueError:
    pass
try:
    power_method([[2.0, 1.0], [1.0, 2.0]], tol=1e-16, max_iter=1)
    assert False, "Exhausting max_iter without converging should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — least-squares engine with conditioning diagnostics",
        "runtime": "python",
        "minutes": 280,
        "brief": r'''
One library, `linalg.py`, that fits a model to data and tells you how much to
trust the fit. `main.py` is a demo that fits a polynomial and prints the report.

## Building blocks

- `shape(a)` — `(rows, cols)`, raising `ValueError` for anything that is not a
  non-empty rectangular list of lists
- `transpose(a)`, `dot(u, v)`, `norm(v)`, `matvec(a, v)`, `matmul(a, b)` —
  each validating its shapes
- `rank(a, tol=1e-9)` — by elimination with partial pivoting
- `qr(a, tol=1e-12)` — modified Gram-Schmidt; `ValueError` when the columns are
  dependent or when there are fewer rows than columns
- `solve_upper(r, y)` — back substitution; `ValueError` on a zero diagonal
- `lu_decompose(m, tol=1e-14)` and `lu_solve(l, u, perm, b)` — as in lab 3

## Eigenvalue diagnostics

- `power_method(m, tol=1e-12, max_iter=20000)` — the dominant eigenvalue of a
  symmetric `m` by Rayleigh-quotient iteration. Seed the start vector with
  `random.Random(7)` so runs are reproducible.
- `inverse_power(m, tol=1e-12, max_iter=500)` — the *smallest* eigenvalue, by
  running the same iteration against `lu_solve` on the factors of `m`. The
  convergence rate is `lambda_min / lambda_2`, which is fast precisely when the
  matrix is ill conditioned.
- `condition_number(a)` — `sqrt(lambda_max / lambda_min)` of `A^T A`, which is
  the ratio of the largest to the smallest singular value of `A`. Return
  `math.inf` when `A^T A` is singular.

## Fitting

- `vandermonde(xs, degree)` — the design matrix whose row for `x` is
  `[1, x, x^2, ..., x^degree]`. A negative degree, or fewer points than
  `degree + 1`, raises `ValueError`.
- `least_squares(a, b, tol=1e-9)` — returns a `Fit` dataclass with fields
  `coefficients`, `residual_norm`, `rank`, `condition`, in that order. Solve via
  `QR`: the normal equations squared the condition number, and you have just
  built the tool to measure that. Raise `ValueError` when `b` is the wrong
  length, when there are fewer rows than columns, or when the design matrix is
  rank deficient — a fit nobody can interpret is worse than no fit.
- `fit_report(fit)` — a string of `len(coefficients) + 4` lines: the header
  `coefficients:`, one `  cI = value` line per coefficient, then lines starting
  `rank`, `condition` and `residual norm`.

```text
xs = [0, 1, 2, 3, 4],  ys = 2 - 3x + x^2,  degree 2
  coefficients -> [2.0, -3.0, 1.0]
  residual_norm -> about 0
  rank -> 3,  condition -> 27.112831810
```
''',
        "deliverables": [
            "`linalg.py` — the whole engine, importable with no output and no side effects",
            "`main.py` — a demo fitting a polynomial to sample data and printing the report",
            "A QR-based `least_squares` that never forms the normal equations",
            "Rank detection that refuses a rank-deficient design matrix instead of returning noise",
            "A `condition_number` built from power and inverse-power iteration on `A^T A`",
            "`fit_report` — a fixed-shape summary of coefficients, rank, conditioning and residual",
        ],
        "constraints": [
            "Standard library only — `math`, `random` and `dataclasses` are enough",
            "`linalg.py` must define names only; importing it must print nothing",
            "Every RNG is seeded with `random.Random(7)`, so two runs agree exactly",
            "No routine may mutate the matrix or vector it is given",
            "The whole demo must finish in well under a second",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the exact-fit, over-determined and rank-deficient cases."},
            {"criterion": "Numerical judgement", "weight": 25,
             "evidence": "Least squares goes through QR rather than the normal equations, and pivoting is used wherever elimination is."},
            {"criterion": "Diagnostics", "weight": 15,
             "evidence": "Reported rank and condition number match independent references to at least six significant figures."},
            {"criterion": "Validation", "weight": 12,
             "evidence": "Ragged matrices, mismatched right-hand sides, singular systems and negative degrees all raise ValueError."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public routine, no dead code, no debug prints left in linalg.py."},
        ],
        "hints": [
            "Write `shape` first and call it from everywhere else — one validation routine, used seven times, is the difference between a library and a pile of functions.",
            "Modified Gram-Schmidt subtracts each projection from the working vector immediately, so later projections see the already-reduced residual. It costs the same as the classical version and is far more stable.",
            "`least_squares` reduces to `solve_upper(r, matvec(transpose(q), b))`: multiplying by Q^T is an orthogonal change of basis, so it cannot amplify the error.",
            "`inverse_power` is just `power_method` with `A^-1` in place of `A`, and `A^-1 v` is spelt `lu_solve(l, u, perm, v)` — factor once, outside the loop.",
        ],
        "files": [
            {"name": "linalg.py", "content": r'''
import math
import random
from dataclasses import dataclass


@dataclass
class Fit:
    coefficients: list
    residual_norm: float
    rank: int
    condition: float


def shape(a):
    """(rows, cols) after validating a is a non-empty rectangular matrix."""
    # your code here


def transpose(a):
    # your code here
    pass


def dot(u, v):
    # your code here
    pass


def norm(v):
    # your code here
    pass


def matvec(a, v):
    # your code here
    pass


def matmul(a, b):
    # your code here
    pass


def rank(a, tol=1e-9):
    """Number of pivots found by elimination with partial pivoting."""
    # your code here


def qr(a, tol=1e-12):
    """(q, r) by modified Gram-Schmidt on the columns of a."""
    # your code here


def solve_upper(r, y):
    """Back substitution against an upper triangular matrix."""
    # your code here


def lu_decompose(m, tol=1e-14):
    """(l, u, perm, sign) with PA = LU."""
    # your code here


def lu_solve(l, u, perm, b):
    """Solve from LU factors."""
    # your code here


def power_method(m, tol=1e-12, max_iter=20000):
    """Dominant eigenvalue of a symmetric matrix."""
    # your code here


def inverse_power(m, tol=1e-12, max_iter=500):
    """Smallest eigenvalue of a symmetric matrix."""
    # your code here


def condition_number(a):
    """Ratio of the largest to the smallest singular value of a."""
    # your code here


def vandermonde(xs, degree):
    """Polynomial design matrix with rows [1, x, ..., x**degree]."""
    # your code here


def least_squares(a, b, tol=1e-9):
    """Least-squares fit via QR, returned as a Fit."""
    # your code here


def fit_report(fit):
    """A fixed-shape textual summary of a Fit."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from linalg import vandermonde, least_squares, fit_report

xs = [0, 1, 2, 3, 4, 5, 6]
ys = [2.0, 0.1, -1.8, -1.9, 0.2, 4.1, 10.0]

fit = least_squares(vandermonde(xs, 2), ys)
print(fit_report(fit))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "linalg.py", "content": r'''
import math
import random
from dataclasses import dataclass


@dataclass
class Fit:
    coefficients: list
    residual_norm: float
    rank: int
    condition: float


def shape(a):
    """(rows, cols) after validating a is a non-empty rectangular matrix."""
    if not isinstance(a, list) or not a:
        raise ValueError("matrix must be a non-empty list of rows")
    cols = None
    for row in a:
        if not isinstance(row, list) or not row:
            raise ValueError("every row must be a non-empty list")
        if cols is None:
            cols = len(row)
        elif len(row) != cols:
            raise ValueError("all rows must have the same length")
    return (len(a), cols)


def transpose(a):
    """A new matrix with rows and columns exchanged."""
    rows, cols = shape(a)
    return [[float(a[i][j]) for i in range(rows)] for j in range(cols)]


def dot(u, v):
    """Dot product of two equal-length vectors."""
    if len(u) != len(v):
        raise ValueError("vectors must have the same length")
    return sum(float(x) * float(y) for x, y in zip(u, v))


def norm(v):
    """Euclidean length of a vector."""
    return math.sqrt(dot(v, v))


def matvec(a, v):
    """Matrix times vector."""
    rows, cols = shape(a)
    if len(v) != cols:
        raise ValueError("vector length must match the column count")
    return [dot(row, v) for row in a]


def matmul(a, b):
    """Matrix product."""
    ar, ac = shape(a)
    br, bc = shape(b)
    if ac != br:
        raise ValueError("inner dimensions must agree")
    bt = transpose(b)
    return [[dot(a[i], bt[j]) for j in range(bc)] for i in range(ar)]


def rank(a, tol=1e-9):
    """Number of pivots found by elimination with partial pivoting."""
    rows, cols = shape(a)
    u = [[float(x) for x in row] for row in a]
    pivot = 0
    for col in range(cols):
        if pivot >= rows:
            break
        best = pivot
        for r in range(pivot + 1, rows):
            if abs(u[r][col]) > abs(u[best][col]):
                best = r
        if abs(u[best][col]) <= tol:
            continue
        u[pivot], u[best] = u[best], u[pivot]
        for r in range(pivot + 1, rows):
            factor = u[r][col] / u[pivot][col]
            for c in range(col, cols):
                u[r][c] -= factor * u[pivot][c]
            u[r][col] = 0.0
        pivot += 1
    return pivot


def qr(a, tol=1e-12):
    """(q, r) by modified Gram-Schmidt on the columns of a."""
    rows, cols = shape(a)
    if rows < cols:
        raise ValueError("need at least as many rows as columns")
    columns = transpose(a)
    basis = []
    r = [[0.0] * cols for _ in range(cols)]
    for j in range(cols):
        residual = list(columns[j])
        for i, q in enumerate(basis):
            r[i][j] = dot(q, residual)
            residual = [x - r[i][j] * qi for x, qi in zip(residual, q)]
        length = norm(residual)
        if length <= tol:
            raise ValueError("columns are linearly dependent")
        r[j][j] = length
        basis.append([x / length for x in residual])
    q = [[basis[j][i] for j in range(cols)] for i in range(rows)]
    return (q, r)


def solve_upper(r, y):
    """Back substitution against an upper triangular matrix."""
    n, cols = shape(r)
    if n != cols:
        raise ValueError("solve_upper needs a square triangular matrix")
    if len(y) != n:
        raise ValueError("right-hand side length must match")
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if r[i][i] == 0.0:
            raise ValueError("triangular matrix is singular")
        total = float(y[i])
        for j in range(i + 1, n):
            total -= r[i][j] * x[j]
        x[i] = total / r[i][i]
    return x


def lu_decompose(m, tol=1e-14):
    """(l, u, perm, sign) with PA = LU."""
    n, cols = shape(m)
    if n != cols:
        raise ValueError("lu_decompose needs a square matrix")
    u = [[float(x) for x in row] for row in m]
    lower = [[0.0] * n for _ in range(n)]
    perm = list(range(n))
    sign = 1.0
    for col in range(n):
        best = col
        for r in range(col + 1, n):
            if abs(u[r][col]) > abs(u[best][col]):
                best = r
        if abs(u[best][col]) <= tol:
            raise ValueError("matrix is singular")
        if best != col:
            u[col], u[best] = u[best], u[col]
            lower[col], lower[best] = lower[best], lower[col]
            perm[col], perm[best] = perm[best], perm[col]
            sign = -sign
        for r in range(col + 1, n):
            factor = u[r][col] / u[col][col]
            lower[r][col] = factor
            for c in range(col, n):
                u[r][c] -= factor * u[col][c]
            u[r][col] = 0.0
    for i in range(n):
        lower[i][i] = 1.0
    return (lower, u, perm, sign)


def lu_solve(l, u, perm, b):
    """Solve from LU factors."""
    n = len(l)
    if len(b) != n:
        raise ValueError("b must have one entry per row")
    y = [0.0] * n
    for i in range(n):
        total = float(b[perm[i]])
        for j in range(i):
            total -= l[i][j] * y[j]
        y[i] = total
    return solve_upper(u, y)


def _seeded_unit(n):
    """A reproducible starting vector that is unlikely to be deficient."""
    rng = random.Random(7)
    v = [rng.random() + 0.5 for _ in range(n)]
    length = norm(v)
    return [x / length for x in v]


def power_method(m, tol=1e-12, max_iter=20000):
    """Dominant eigenvalue of a symmetric matrix."""
    n, cols = shape(m)
    if n != cols:
        raise ValueError("power_method needs a square matrix")
    v = _seeded_unit(n)
    value = 0.0
    for step in range(1, max_iter + 1):
        w = matvec(m, v)
        length = norm(w)
        if length <= 1e-300:
            return 0.0
        estimate = dot(v, w)
        v = [x / length for x in w]
        if step > 1 and abs(estimate - value) <= tol * (1.0 + abs(estimate)):
            return estimate
        value = estimate
    raise ValueError("power method did not converge")


def inverse_power(m, tol=1e-12, max_iter=500):
    """Smallest eigenvalue of a symmetric matrix."""
    n, cols = shape(m)
    lower, u, perm, _ = lu_decompose(m)
    v = _seeded_unit(n)
    value = 0.0
    for step in range(1, max_iter + 1):
        w = lu_solve(lower, u, perm, v)
        length = norm(w)
        if length <= 1e-300:
            raise ValueError("inverse iteration collapsed")
        v = [x / length for x in w]
        estimate = dot(v, matvec(m, v))
        if step > 1 and abs(estimate - value) <= tol * (1.0 + abs(estimate)):
            return estimate
        value = estimate
    raise ValueError("inverse power method did not converge")


def condition_number(a):
    """Ratio of the largest to the smallest singular value of a."""
    gram = matmul(transpose(a), a)
    top = power_method(gram)
    if top <= 0.0:
        return math.inf
    try:
        low = inverse_power(gram)
    except ValueError:
        return math.inf
    if low <= 0.0:
        return math.inf
    return math.sqrt(top / low)


def vandermonde(xs, degree):
    """Polynomial design matrix with rows [1, x, ..., x**degree]."""
    if degree < 0:
        raise ValueError("degree must not be negative")
    if len(xs) < degree + 1:
        raise ValueError("need at least degree + 1 sample points")
    return [[float(x) ** k for k in range(degree + 1)] for x in xs]


def least_squares(a, b, tol=1e-9):
    """Least-squares fit via QR, returned as a Fit."""
    rows, cols = shape(a)
    if len(b) != rows:
        raise ValueError("b must have one entry per row")
    if rows < cols:
        raise ValueError("an underdetermined system has no unique least-squares fit")
    found = rank(a, tol)
    if found < cols:
        raise ValueError("design matrix is rank deficient")
    q, r = qr(a)
    coefficients = solve_upper(r, matvec(transpose(q), b))
    predicted = matvec(a, coefficients)
    residual = [float(bi) - pi for bi, pi in zip(b, predicted)]
    return Fit(coefficients, norm(residual), found, condition_number(a))


def fit_report(fit):
    """A fixed-shape textual summary of a Fit."""
    lines = ["coefficients:"]
    for i, c in enumerate(fit.coefficients):
        lines.append(f"  c{i} = {c:.10g}")
    lines.append(f"rank          = {fit.rank}")
    lines.append(f"condition     = {fit.condition:.4e}")
    lines.append(f"residual norm = {fit.residual_norm:.4e}")
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from linalg import vandermonde, least_squares, fit_report

xs = [0, 1, 2, 3, 4, 5, 6]
ys = [2.0, 0.1, -1.8, -1.9, 0.2, 4.1, 10.0]

fit = least_squares(vandermonde(xs, 2), ys)
print(fit_report(fit))

exact = least_squares(vandermonde([0, 1, 2, 3, 4], 2), [2.0, 0.0, 0.0, 2.0, 6.0])
print()
print("exact quadratic:", [round(c, 12) for c in exact.coefficients])
'''},
        ],
        "tests": [
            {"name": "Shapes and products", "code": r'''
from linalg import shape, transpose, dot, norm, matvec, matmul
assert shape([[1, 2, 3], [4, 5, 6]]) == (2, 3), f"shape gave {shape([[1, 2, 3], [4, 5, 6]])!r}"
assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]], \
    f"transpose gave {transpose([[1, 2, 3], [4, 5, 6]])!r}"
assert dot([1, 2, 3], [4, 5, 6]) == 32.0, f"dot gave {dot([1, 2, 3], [4, 5, 6])!r}, expected 32"
assert abs(norm([3, 4]) - 5.0) < 1e-12, f"norm([3, 4]) gave {norm([3, 4])!r}"
assert matvec([[1, 2], [3, 4]], [1, 1]) == [3.0, 7.0], f"matvec gave {matvec([[1, 2], [3, 4]], [1, 1])!r}"
assert matmul([[1, 2, 3], [4, 5, 6]], [[7, 8], [9, 10], [11, 12]]) == [[58.0, 64.0], [139.0, 154.0]], \
    f"matmul gave {matmul([[1, 2, 3], [4, 5, 6]], [[7, 8], [9, 10], [11, 12]])!r}"
for _bad in [[], [[]], [[1, 2], [3]], "nope"]:
    try:
        shape(_bad)
        assert False, f"shape({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    matmul([[1, 2]], [[1, 2]])
    assert False, "matmul with mismatched inner dimensions should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Rank by elimination", "code": r'''
from linalg import rank
for _name, _a, _want in [("dependent", [[1, 2], [2, 4]], 1),
                         ("full", [[1, 2], [3, 4]], 2),
                         ("3x3 rank 2", [[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2),
                         ("zeros", [[0, 0, 0], [0, 0, 0]], 0),
                         ("tall dependent", [[1, 2], [2, 4], [3, 6]], 1),
                         ("vandermonde", [[1, 0, 0], [1, 1, 1], [1, 2, 4], [1, 3, 9], [1, 4, 16]], 3)]:
    _got = rank(_a)
    assert _got == _want, f"rank of the {_name} case gave {_got!r}, expected {_want}"
'''},
            {"name": "QR factorisation", "code": r'''
from linalg import qr, matmul, transpose
_a = [[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]]
_q, _r = qr(_a)
_prod = matmul(_q, _r)
for _i in range(3):
    for _j in range(2):
        assert abs(_prod[_i][_j] - _a[_i][_j]) < 1e-9, \
            f"(QR)[{_i}][{_j}] is {_prod[_i][_j]!r}, expected {_a[_i][_j]!r}"
assert abs(_r[0][0] - 14.0) < 1e-9 and abs(_r[0][1] - 21.0) < 1e-9 and abs(_r[1][1] - 175.0) < 1e-9, \
    f"R came out as {_r!r}, expected [[14, 21], [0, 175]]"
_gram = matmul(transpose(_q), _q)
for _i in range(2):
    for _j in range(2):
        _want = 1.0 if _i == _j else 0.0
        assert abs(_gram[_i][_j] - _want) < 1e-12, f"(Q^T Q)[{_i}][{_j}] is {_gram[_i][_j]!r}"
for _bad in [[[1.0, 2.0], [2.0, 4.0]], [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]]:
    try:
        qr(_bad)
        assert False, f"qr({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Triangular and LU solves", "code": r'''
from linalg import solve_upper, lu_decompose, lu_solve, matmul
_x = solve_upper([[2.0, 1.0], [0.0, 4.0]], [4.0, 8.0])
assert abs(_x[1] - 2.0) < 1e-12 and abs(_x[0] - 1.0) < 1e-12, f"solve_upper gave {_x!r}, expected [1.0, 2.0]"
try:
    solve_upper([[0.0, 1.0], [0.0, 1.0]], [1.0, 1.0])
    assert False, "A zero on the diagonal should raise ValueError"
except ValueError:
    pass
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_l, _u, _perm, _sign = lu_decompose(_a)
_lu = matmul(_l, _u)
for _i in range(3):
    for _j in range(3):
        assert abs(_lu[_i][_j] - float(_a[_perm[_i]][_j])) < 1e-9, \
            f"(LU)[{_i}][{_j}] is {_lu[_i][_j]!r}, expected {float(_a[_perm[_i]][_j])!r}"
_x = lu_solve(_l, _u, _perm, [1, 2, 3])
assert abs(_x[0] - 6.0 / 41.0) < 1e-12, f"lu_solve gave {_x!r}; x[0] should be 6/41"
try:
    lu_decompose([[1, 2], [2, 4]])
    assert False, "lu_decompose of a singular matrix should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Power and inverse-power iteration", "code": r'''
from linalg import power_method, inverse_power
assert abs(power_method([[2.0, 1.0], [1.0, 2.0]]) - 3.0) < 1e-8, \
    f"power_method gave {power_method([[2.0, 1.0], [1.0, 2.0]])!r}, expected 3.0"
assert abs(inverse_power([[2.0, 1.0], [1.0, 2.0]]) - 1.0) < 1e-8, \
    f"inverse_power gave {inverse_power([[2.0, 1.0], [1.0, 2.0]])!r}, expected 1.0"
_m = [[6.0, 2.0, 1.0], [2.0, 3.0, 1.0], [1.0, 1.0, 1.0]]
assert abs(power_method(_m) - 7.287992138960425) < 1e-7, \
    f"power_method on the 3x3 case gave {power_method(_m)!r}, expected 7.28799213896"
assert abs(inverse_power(_m) - 0.5789333856910526) < 1e-7, \
    f"inverse_power on the 3x3 case gave {inverse_power(_m)!r}, expected 0.57893338569"
try:
    power_method([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert False, "power_method on a non-square matrix should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Condition numbers", "code": r'''
import math as _m
from linalg import condition_number, vandermonde
assert abs(condition_number([[1.0, 0.0], [0.0, 1.0]]) - 1.0) < 1e-9, \
    f"The identity is perfectly conditioned; got {condition_number([[1.0, 0.0], [0.0, 1.0]])!r}"
_got = condition_number([[1.0, 0.0], [0.0, 2.0]])
assert abs(_got - 2.0) < 1e-8, f"diag(1, 2) has condition 2; got {_got!r}"
for _name, _a, _want in [("degree 1 on 1..4", vandermonde([1, 2, 3, 4], 1), 7.468739725928093),
                         ("degree 2 on 0..4", vandermonde([0, 1, 2, 3, 4], 2), 27.112831810234862),
                         ("degree 3 on 0..5", vandermonde([0, 1, 2, 3, 4, 5], 3), 324.4683163832041),
                         ("tall 3x2", [[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]], 12.681142753501145)]:
    _got = condition_number(_a)
    assert abs(_got - _want) / _want < 1e-6, \
        f"condition_number of the {_name} case gave {_got!r}, expected {_want!r}"
'''},
            {"name": "The Vandermonde design matrix", "code": r'''
from linalg import vandermonde
assert vandermonde([1, 2, 3], 2) == [[1.0, 1.0, 1.0], [1.0, 2.0, 4.0], [1.0, 3.0, 9.0]], \
    f"vandermonde gave {vandermonde([1, 2, 3], 2)!r}"
assert vandermonde([5, 6], 0) == [[1.0], [1.0]], f"Degree 0 gave {vandermonde([5, 6], 0)!r}"
for _args in [([1, 2, 3], -1), ([1, 2], 2)]:
    try:
        vandermonde(*_args)
        assert False, f"vandermonde{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "An exactly representable fit", "code": r'''
from linalg import vandermonde, least_squares, Fit
_xs = [0, 1, 2, 3, 4]
_ys = [2.0 - 3.0 * x + x * x for x in _xs]
_fit = least_squares(vandermonde(_xs, 2), _ys)
assert isinstance(_fit, Fit), f"least_squares returned {type(_fit).__name__}, expected Fit"
for _i, _want in enumerate([2.0, -3.0, 1.0]):
    assert abs(_fit.coefficients[_i] - _want) < 1e-9, \
        f"coefficient {_i} is {_fit.coefficients[_i]!r}, expected {_want}"
assert _fit.residual_norm < 1e-9, f"An exact fit should have residual ~0; got {_fit.residual_norm!r}"
assert _fit.rank == 3, f"rank came back as {_fit.rank!r}, expected 3"
assert abs(_fit.condition - 27.112831810234862) / 27.112831810234862 < 1e-6, \
    f"condition came back as {_fit.condition!r}, expected about 27.1128318102"
'''},
            {"name": "An over-determined fit against the closed form", "code": r'''
import math as _m
from linalg import vandermonde, least_squares
_fit = least_squares(vandermonde([1, 2, 3, 4], 1), [2, 4, 5, 8])
assert abs(_fit.coefficients[0] - 0.0) < 1e-9, \
    f"intercept is {_fit.coefficients[0]!r}, expected 0.0"
assert abs(_fit.coefficients[1] - 1.9) < 1e-9, \
    f"slope is {_fit.coefficients[1]!r}, expected 1.9"
assert abs(_fit.residual_norm - _m.sqrt(0.7)) < 1e-9, \
    f"residual norm is {_fit.residual_norm!r}, expected sqrt(0.7) = {_m.sqrt(0.7)!r}"
assert _fit.rank == 2, f"rank came back as {_fit.rank!r}, expected 2"
'''},
            {"name": "Bad fits are refused, not fudged", "code": r'''
from linalg import least_squares
try:
    least_squares([[1, 2], [2, 4], [3, 6]], [1, 2, 3])
    assert False, "A rank-deficient design matrix should raise ValueError"
except ValueError:
    pass
try:
    least_squares([[1, 0], [0, 1], [1, 1]], [1, 2])
    assert False, "A right-hand side of the wrong length should raise ValueError"
except ValueError:
    pass
try:
    least_squares([[1, 2, 3], [4, 5, 6]], [1, 2])
    assert False, "Fewer rows than columns should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The fit report", "code": r'''
from linalg import vandermonde, least_squares, fit_report
_fit = least_squares(vandermonde([1, 2, 3, 4], 1), [2, 4, 5, 8])
_rep = fit_report(_fit)
assert isinstance(_rep, str), "fit_report returns a string, it does not print"
_lines = _rep.split("\n")
assert len(_lines) == 6, f"Expected 6 lines for a 2-coefficient fit, got {len(_lines)}: {_lines!r}"
assert _lines[0].startswith("coefficients:"), f"First line was {_lines[0]!r}"
assert _lines[1].strip().startswith("c0 ="), f"Second line was {_lines[1]!r}"
assert _lines[2].strip().startswith("c1 ="), f"Third line was {_lines[2]!r}"
assert "1.9" in _lines[2], f"The slope should appear in {_lines[2]!r}"
assert _lines[3].startswith("rank"), f"Line 4 was {_lines[3]!r}"
assert _lines[3].rstrip().endswith("2"), f"The rank line should end with 2; got {_lines[3]!r}"
assert _lines[4].startswith("condition"), f"Line 5 was {_lines[4]!r}"
assert _lines[5].startswith("residual norm"), f"Line 6 was {_lines[5]!r}"
'''},
            {"name": "linalg.py is import-clean, pure and fast", "code": r'''
import time as _t
_src = open("linalg.py").read()
assert "print(" not in _src, "linalg.py defines routines; the printing belongs in main.py"
for _banned in ("numpy", "scipy"):
    assert _banned not in _src, f"linalg.py must not reach for {_banned}"
assert "random.Random(7)" in _src, "Seed the RNG with random.Random(7) so runs are reproducible"
from linalg import vandermonde, least_squares, rank, qr
_a = vandermonde([0, 1, 2, 3, 4], 2)
_before = [row[:] for row in _a]
least_squares(_a, [1.0, 2.0, 3.0, 4.0, 6.0])
rank(_a)
qr(_a)
assert _a == _before, "No routine may mutate the matrix it is given"
_start = _t.time()
for _ in range(5):
    least_squares(vandermonde([0, 1, 2, 3, 4, 5, 6], 3), [1.0, 2.0, 3.0, 4.0, 6.0, 9.0, 13.0])
_elapsed = _t.time() - _start
assert _elapsed < 5.0, f"Five fits took {_elapsed:.2f}s, which is far too slow"
'''},
        ],
    },
}
