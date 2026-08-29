"""ML401 — Machine Learning & Statistical Modeling."""

COURSE = {
    "id": "ML401",
    "title": "Machine Learning & Statistical Modeling",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["MA121", "MA201", "CS301"],
    "stack": ["Python"],
    "credits": 15,
    "hours": 170,
    "icon": "∴",
    "summary": (
        "Every estimator in this course is built from arithmetic you write yourself: "
        "the normal equation solved by Gaussian elimination, logistic regression driven "
        "by its own gradient, impurity-based tree splits, k-means++ and PCA by power "
        "iteration. Nothing is imported that would hide the mathematics. The result is "
        "an honest pipeline — split, scale, train, tune, evaluate — and metrics you can "
        "derive on paper before you trust them on screen."
    ),
    "outcomes": [
        "Derive and implement the normal equation, and contrast it with batch gradient descent",
        "Explain why feature scaling changes the conditioning of a gradient-descent problem",
        "Implement logistic regression from the cross-entropy gradient and read its coefficients",
        "Compute precision, recall, F1, a confusion matrix and ROC-AUC without a library",
        "Grow decision trees from gini or entropy gain and bag them into a random forest",
        "Implement k-means++ and PCA by power iteration, and interpret inertia and explained variance",
        "Select a model with k-fold cross-validation and demonstrate the bias-variance trade-off",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone build (60%).",
    "reading": [
        "Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning*, 2nd ed. — chapters 3, 4, 7, 9, 14",
        "Bishop, *Pattern Recognition and Machine Learning* — chapters 3, 4, 12",
        "James, Witten, Hastie & Tibshirani, *An Introduction to Statistical Learning*, 2nd ed. — chapters 5-6",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Linear regression two ways",
            "summary": "The normal equation by elimination, then the same fit by gradient descent.",
            "concepts": [
                "The design matrix, the bias column, and least squares as a projection",
                "The normal equation X^T X w = X^T y, and when X^T X is singular",
                "Gaussian elimination with partial pivoting; O(d^3) versus O(nd) per step",
                "Mean squared error, its gradient (2/n) X^T (Xw - y), and why the 2 matters",
                "Feature scaling changes the condition number, and therefore the usable step size",
                "A convergence trace is the cheapest diagnostic you will ever write",
                "Divergence, oscillation and crawling are three distinct learning-rate failures",
            ],
            "lab": {
                "title": "Normal equation versus gradient descent",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Fit `y = w0 + w1*x1 + w2*x2` twice, exactly and iteratively, and compare.

Data comes from `make_dataset(n, seed)`, already written for you: it returns
`(X, y)` where `y = 3 + 2*x1 - x2` with **no noise**, so the exact fit is
`[3, 2, -1]` and you can check your work to machine precision.

Implement:

**`solve_linear_system(A, b)`** — Gauss-Jordan elimination with partial
pivoting. Returns the solution list. Raise `ValueError` when the pivot column is
numerically zero (treat `abs(pivot) < 1e-12` as singular).

**`transpose(A)`, `matmul(A, B)`, `matvec(A, v)`** — the three products you need.

**`add_bias(X)`** — prepend a `1.0` to every row.

**`standardise(X)`** — returns `(Z, means, stds)`, each column centred on its
mean and divided by its **population** standard deviation (divide by `n`). A
column with zero spread keeps `std = 1.0`, so it maps to all zeros rather than
to `nan`.

**`normal_equation(X, y)`** — solve `X^T X w = X^T y`. Raise `ValueError` when
`X` is empty or `len(X) != len(y)`.

**`predict(X, w)`** and **`mse(actual, predicted)`**.

**`gradient_descent(X, y, lr, epochs)`** — start from all-zero weights and
return `(w, history)`. `history` holds the MSE **before** each update, so it has
exactly `epochs` entries and `history[0]` is the error of the zero model.

```text
standardise([[1.0], [3.0]])  ->  ([[-1.0], [1.0]], [2.0], [1.0])
solve_linear_system([[2, 1], [1, 3]], [5, 10])  ->  [1.0, 3.0]
mse([0.0, 0.0], [1.0, 3.0])  ->  5.0
```

On standardised features with `lr=0.1` and 500 epochs the trace should fall to
machine zero; on the raw features the same rate diverges. That contrast is the
point of the lab.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def make_dataset(n=60, seed=7):
    """Noiseless data from y = 3 + 2*x1 - x2."""
    rng = random.Random(seed)
    X = [[rng.uniform(0, 10), rng.uniform(-5, 5)] for _ in range(n)]
    y = [3.0 + 2.0 * a - 1.0 * b for a, b in X]
    return X, y


def transpose(A):
    """Rows become columns."""
    # your code here


def matmul(A, B):
    """Matrix product A @ B."""
    # your code here


def matvec(A, v):
    """Matrix-vector product A @ v."""
    # your code here


def solve_linear_system(A, b):
    """Gauss-Jordan with partial pivoting. ValueError when A is singular."""
    # your code here


def add_bias(X):
    """Prepend a 1.0 column."""
    # your code here


def standardise(X):
    """(Z, means, stds) using the population standard deviation."""
    # your code here


def normal_equation(X, y):
    """Least-squares weights from X^T X w = X^T y."""
    # your code here


def predict(X, w):
    """Model predictions for every row of X."""
    # your code here


def mse(actual, predicted):
    """Mean squared error."""
    # your code here


def gradient_descent(X, y, lr, epochs):
    """(w, history) — history holds the MSE before each update."""
    # your code here


X, y = make_dataset()
print("closed form:", normal_equation(add_bias(X), y))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def make_dataset(n=60, seed=7):
    """Noiseless data from y = 3 + 2*x1 - x2."""
    rng = random.Random(seed)
    X = [[rng.uniform(0, 10), rng.uniform(-5, 5)] for _ in range(n)]
    y = [3.0 + 2.0 * a - 1.0 * b for a, b in X]
    return X, y


def transpose(A):
    """Rows become columns."""
    return [list(col) for col in zip(*A)]


def matmul(A, B):
    """Matrix product A @ B."""
    Bt = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


def matvec(A, v):
    """Matrix-vector product A @ v."""
    return [sum(a * b for a, b in zip(row, v)) for row in A]


def solve_linear_system(A, b):
    """Gauss-Jordan with partial pivoting. ValueError when A is singular."""
    n = len(A)
    if n == 0 or len(b) != n:
        raise ValueError("A must be square and match b")
    M = [list(map(float, row)) + [float(b[i])] for i, row in enumerate(A)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-12:
            raise ValueError("matrix is singular to working precision")
        M[col], M[pivot] = M[pivot], M[col]
        scale = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= scale
        for r in range(n):
            if r != col and M[r][col] != 0.0:
                factor = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= factor * M[col][j]
    return [M[i][n] for i in range(n)]


def add_bias(X):
    """Prepend a 1.0 column."""
    return [[1.0] + [float(v) for v in row] for row in X]


def standardise(X):
    """(Z, means, stds) using the population standard deviation."""
    if not X:
        raise ValueError("X is empty")
    cols = transpose(X)
    means = [sum(c) / len(c) for c in cols]
    stds = []
    for c, m in zip(cols, means):
        spread = math.sqrt(sum((v - m) ** 2 for v in c) / len(c))
        stds.append(spread if spread > 1e-12 else 1.0)
    Z = [[(v - m) / s for v, m, s in zip(row, means, stds)] for row in X]
    return Z, means, stds


def normal_equation(X, y):
    """Least-squares weights from X^T X w = X^T y."""
    if not X or not y:
        raise ValueError("X and y must be non-empty")
    if len(X) != len(y):
        raise ValueError("X and y disagree on the number of rows")
    Xt = transpose(X)
    return solve_linear_system(matmul(Xt, X), matvec(Xt, y))


def predict(X, w):
    """Model predictions for every row of X."""
    return matvec(X, w)


def mse(actual, predicted):
    """Mean squared error."""
    if len(actual) != len(predicted):
        raise ValueError("actual and predicted differ in length")
    if not actual:
        raise ValueError("nothing to score")
    return sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)


def gradient_descent(X, y, lr, epochs):
    """(w, history) — history holds the MSE before each update."""
    if len(X) != len(y):
        raise ValueError("X and y disagree on the number of rows")
    n = len(X)
    d = len(X[0])
    w = [0.0] * d
    history = []
    for _ in range(epochs):
        residual = [p - t for p, t in zip(matvec(X, w), y)]
        history.append(sum(r * r for r in residual) / n)
        grad = [(2.0 / n) * sum(X[i][j] * residual[i] for i in range(n)) for j in range(d)]
        w = [wj - lr * gj for wj, gj in zip(w, grad)]
    return w, history


X, y = make_dataset()
print("closed form:", [round(v, 10) for v in normal_equation(add_bias(X), y)])

Z, means, stds = standardise(X)
w_gd, history = gradient_descent(add_bias(Z), y, 0.1, 500)
print("gd first / last MSE:", history[0], history[-1])
'''}],
                "hints": [
                    "Build the augmented matrix `[A | b]` once, then work on it in place: pick the pivot row by largest absolute value in the column, swap it up, divide it through, and eliminate that column from every other row.",
                    "`normal_equation` is three lines once the products exist: transpose, `matmul(Xt, X)`, `matvec(Xt, y)`, then `solve_linear_system`.",
                    "In `standardise` compute the mean first and the variance from it in a second pass; guard `spread > 1e-12` before dividing, or a constant column produces `nan` and poisons every later matrix.",
                    "Append the MSE to `history` at the top of the loop body, before the weight update — that is what makes `history[0]` the error of the zero model and `len(history) == epochs`.",
                ],
                "tests": [
                    {"name": "Elimination solves and detects singularity", "code": r'''
_got = solve_linear_system([[2, 1], [1, 3]], [5, 10])
assert all(abs(a - b) < 1e-9 for a, b in zip(_got, [1.0, 3.0])), \
    f"solve_linear_system([[2,1],[1,3]], [5,10]) gave {_got!r}, expected [1.0, 3.0]"
_got = solve_linear_system([[0.0, 1.0], [1.0, 0.0]], [2.0, 3.0])
assert all(abs(a - b) < 1e-9 for a, b in zip(_got, [3.0, 2.0])), \
    f"A zero leading pivot must be handled by swapping rows; got {_got!r}, expected [3.0, 2.0]"
try:
    solve_linear_system([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0])
    assert False, "A singular matrix should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The three products", "code": r'''
assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]], \
    f"transpose gave {transpose([[1, 2, 3], [4, 5, 6]])!r}"
_p = matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]])
assert _p == [[19, 22], [43, 50]], f"matmul gave {_p!r}, expected [[19, 22], [43, 50]]"
_v = matvec([[1, 2], [3, 4]], [1, 1])
assert _v == [3, 7], f"matvec gave {_v!r}, expected [3, 7]"
'''},
                    {"name": "add_bias and standardise", "code": r'''
assert add_bias([[2.0, 3.0]]) == [[1.0, 2.0, 3.0]], f"add_bias gave {add_bias([[2.0, 3.0]])!r}"
_Z, _m, _s = standardise([[1.0], [3.0]])
assert _m == [2.0], f"means came out {_m!r}, expected [2.0]"
assert abs(_s[0] - 1.0) < 1e-12, f"population std came out {_s!r}, expected [1.0]"
assert abs(_Z[0][0] + 1.0) < 1e-12 and abs(_Z[1][0] - 1.0) < 1e-12, \
    f"standardised column is {_Z!r}, expected [[-1.0], [1.0]]"
_Zc, _mc, _sc = standardise([[5.0, 1.0], [5.0, 3.0]])
assert _sc[0] == 1.0, f"A constant column must keep std 1.0, got {_sc[0]!r}"
assert _Zc[0][0] == 0.0 and _Zc[1][0] == 0.0, \
    f"A constant column standardises to zeros, got {[r[0] for r in _Zc]!r}"
'''},
                    {"name": "The normal equation recovers the exact model", "code": r'''
_X = [[1.0, 2.0], [2.0, 1.0], [3.0, 4.0], [4.0, 3.0], [5.0, 7.0]]
_y = [3.0 + 2.0 * a - b for a, b in _X]
_w = normal_equation(add_bias(_X), _y)
for _got, _want, _name in zip(_w, [3.0, 2.0, -1.0], ["w0", "w1", "w2"]):
    assert abs(_got - _want) < 1e-9, f"{_name} came out {_got!r}, expected {_want}"
_Xbig, _ybig = make_dataset(60, 7)
_wbig = normal_equation(add_bias(_Xbig), _ybig)
for _got, _want in zip(_wbig, [3.0, 2.0, -1.0]):
    assert abs(_got - _want) < 1e-7, f"On the 60-row set the weights are {_wbig!r}, expected [3, 2, -1]"
'''},
                    {"name": "predict and mse", "code": r'''
assert predict([[1.0, 2.0]], [3.0, 4.0]) == [11.0], f"predict gave {predict([[1.0, 2.0]], [3.0, 4.0])!r}"
assert mse([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 0.0, "A perfect fit has zero error"
assert abs(mse([0.0, 0.0], [1.0, 3.0]) - 5.0) < 1e-12, \
    f"mse([0,0], [1,3]) gave {mse([0.0, 0.0], [1.0, 3.0])!r}, expected 5.0"
'''},
                    {"name": "Gradient descent converges to the closed form", "code": r'''
_X, _y = make_dataset(60, 7)
_Z, _, _ = standardise(_X)
_Zb = add_bias(_Z)
_closed = normal_equation(_Zb, _y)
_w, _hist = gradient_descent(_Zb, _y, 0.1, 500)
assert len(_hist) == 500, f"history should hold one MSE per epoch, got {len(_hist)}"
assert abs(_hist[0] - mse(_y, predict(_Zb, [0.0, 0.0, 0.0]))) < 1e-9, \
    f"history[0] should be the MSE of the zero model, got {_hist[0]!r}"
assert all(_hist[i + 1] <= _hist[i] + 1e-12 for i in range(len(_hist) - 1)), \
    "The trace must not rise — with lr=0.1 on standardised features it decreases every epoch"
assert _hist[-1] < 1e-6, f"After 500 epochs the MSE is {_hist[-1]!r}, expected under 1e-6"
for _got, _want in zip(_w, _closed):
    assert abs(_got - _want) < 1e-4, f"Gradient descent gave {_w!r}, closed form is {_closed!r}"
'''},
                    {"name": "Bad shapes are refused", "code": r'''
try:
    normal_equation([[1.0, 2.0]], [1.0, 2.0])
    assert False, "normal_equation should reject len(X) != len(y) with ValueError"
except ValueError:
    pass
try:
    normal_equation([], [])
    assert False, "normal_equation should reject an empty design matrix with ValueError"
except ValueError:
    pass
try:
    gradient_descent([[1.0, 1.0]], [1.0, 2.0], 0.1, 5)
    assert False, "gradient_descent should reject len(X) != len(y) with ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Classification and honest metrics",
            "summary": "Logistic regression from the cross-entropy gradient, then the numbers that judge it.",
            "concepts": [
                "The logistic link, the log-odds, and why squared error is the wrong loss here",
                "Cross-entropy as the negative log-likelihood of a Bernoulli model",
                "The gradient (1/n) X^T (sigma(Xw) - y): the same shape as least squares, a different sigma",
                "Numerically safe sigmoid and clipped logs; `exp(800)` is an OverflowError, not a large number",
                "The confusion matrix, and precision and recall as two different questions",
                "F1 as the harmonic mean, and what a zero denominator should mean",
                "ROC-AUC as the probability a random positive outscores a random negative",
            ],
            "lab": {
                "title": "Logistic regression and the metrics that judge it",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Build a binary classifier and then the evidence that it works.

**`sigmoid(z)`** — must not overflow. For `z >= 0` use `1 / (1 + exp(-z))`; for
`z < 0` use `exp(z) / (1 + exp(z))`. `sigmoid(-800)` returns `0.0`, it does not
raise.

**`cross_entropy(y, p)`** — mean of `-(y*log(p) + (1-y)*log(1-p))`, with `p`
clipped into `[1e-12, 1 - 1e-12]` so a confident mistake costs a large number
rather than infinity. `ValueError` when the lists differ in length.

```text
cross_entropy([1, 0], [0.9, 0.2])  ->  0.16425203348601802
```

**`fit_logistic(X, y, lr, epochs, l2=0.0)`** — batch gradient descent from
all-zero weights. `X` already carries its bias column, and the penalty must
**not** touch `w[0]`. The update uses `grad[j] = (1/n) * sum_i X[i][j] * (p_i -
y_i)`, plus `l2 * w[j] / n` for `j >= 1`.

**`predict_proba(X, w)`** and **`predict_label(X, w, threshold=0.5)`**.

**`confusion_matrix(y_true, y_pred)`** — returns `(tp, fp, fn, tn)`.

**`precision`, `recall`, `f1_score`** — each takes `(y_true, y_pred)` and
returns `0.0` when its denominator is zero rather than raising.

**`roc_auc(y_true, scores)`** — count pairs: every positive scored above a
negative contributes 1, every tie contributes 0.5, divided by the number of
pairs. Return `0.5` when one class is missing entirely.

```text
roc_auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8])  ->  0.75
```

`make_blobs(n, seed)` is supplied: two Gaussian clouds at (-2, -2) and (2, 2),
which a correct fit separates perfectly.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def make_blobs(n=120, seed=7):
    """Two Gaussian clouds, labels 0 and 1, linearly separable in practice."""
    rng = random.Random(seed)
    X, y = [], []
    for _ in range(n):
        label = rng.randrange(2)
        centre = 2.0 if label else -2.0
        X.append([rng.gauss(centre, 1.0), rng.gauss(centre, 1.0)])
        y.append(label)
    return X, y


def add_bias(X):
    """Prepend a 1.0 column."""
    return [[1.0] + [float(v) for v in row] for row in X]


def sigmoid(z):
    """Overflow-safe logistic function."""
    # your code here


def cross_entropy(y, p):
    """Mean binary cross-entropy, with p clipped away from 0 and 1."""
    # your code here


def fit_logistic(X, y, lr=0.5, epochs=2000, l2=0.0):
    """Batch gradient descent on the cross-entropy. X already has its bias column."""
    # your code here


def predict_proba(X, w):
    """P(y = 1) for every row."""
    # your code here


def predict_label(X, w, threshold=0.5):
    """Hard 0/1 predictions."""
    # your code here


def confusion_matrix(y_true, y_pred):
    """(tp, fp, fn, tn)."""
    # your code here


def precision(y_true, y_pred):
    """tp / (tp + fp), or 0.0 when nothing was predicted positive."""
    # your code here


def recall(y_true, y_pred):
    """tp / (tp + fn), or 0.0 when there are no positives."""
    # your code here


def f1_score(y_true, y_pred):
    """Harmonic mean of precision and recall, or 0.0 when both are zero."""
    # your code here


def roc_auc(y_true, scores):
    """Pairwise ranking estimate of the area under the ROC curve."""
    # your code here


X, y = make_blobs()
Xb = add_bias(X)
w = fit_logistic(Xb, y)
print("weights:", w)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def make_blobs(n=120, seed=7):
    """Two Gaussian clouds, labels 0 and 1, linearly separable in practice."""
    rng = random.Random(seed)
    X, y = [], []
    for _ in range(n):
        label = rng.randrange(2)
        centre = 2.0 if label else -2.0
        X.append([rng.gauss(centre, 1.0), rng.gauss(centre, 1.0)])
        y.append(label)
    return X, y


def add_bias(X):
    """Prepend a 1.0 column."""
    return [[1.0] + [float(v) for v in row] for row in X]


def sigmoid(z):
    """Overflow-safe logistic function."""
    if z >= 0.0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def cross_entropy(y, p):
    """Mean binary cross-entropy, with p clipped away from 0 and 1."""
    if len(y) != len(p):
        raise ValueError("y and p differ in length")
    if not y:
        raise ValueError("nothing to score")
    total = 0.0
    for target, prob in zip(y, p):
        q = min(max(prob, 1e-12), 1.0 - 1e-12)
        total -= target * math.log(q) + (1.0 - target) * math.log(1.0 - q)
    return total / len(y)


def fit_logistic(X, y, lr=0.5, epochs=2000, l2=0.0):
    """Batch gradient descent on the cross-entropy. X already has its bias column."""
    if len(X) != len(y):
        raise ValueError("X and y disagree on the number of rows")
    n = len(X)
    d = len(X[0])
    w = [0.0] * d
    for _ in range(epochs):
        residual = [sigmoid(sum(wj * xj for wj, xj in zip(w, row))) - target
                    for row, target in zip(X, y)]
        grad = [sum(X[i][j] * residual[i] for i in range(n)) / n for j in range(d)]
        for j in range(1, d):
            grad[j] += l2 * w[j] / n
        w = [wj - lr * gj for wj, gj in zip(w, grad)]
    return w


def predict_proba(X, w):
    """P(y = 1) for every row."""
    return [sigmoid(sum(wj * xj for wj, xj in zip(w, row))) for row in X]


def predict_label(X, w, threshold=0.5):
    """Hard 0/1 predictions."""
    return [1 if p >= threshold else 0 for p in predict_proba(X, w)]


def confusion_matrix(y_true, y_pred):
    """(tp, fp, fn, tn)."""
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred differ in length")
    tp = fp = fn = tn = 0
    for t, p in zip(y_true, y_pred):
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 1:
            fp += 1
        elif t == 1 and p == 0:
            fn += 1
        else:
            tn += 1
    return tp, fp, fn, tn


def precision(y_true, y_pred):
    """tp / (tp + fp), or 0.0 when nothing was predicted positive."""
    tp, fp, _, _ = confusion_matrix(y_true, y_pred)
    return tp / (tp + fp) if tp + fp else 0.0


def recall(y_true, y_pred):
    """tp / (tp + fn), or 0.0 when there are no positives."""
    tp, _, fn, _ = confusion_matrix(y_true, y_pred)
    return tp / (tp + fn) if tp + fn else 0.0


def f1_score(y_true, y_pred):
    """Harmonic mean of precision and recall, or 0.0 when both are zero."""
    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    return 2.0 * p * r / (p + r) if p + r else 0.0


def roc_auc(y_true, scores):
    """Pairwise ranking estimate of the area under the ROC curve."""
    if len(y_true) != len(scores):
        raise ValueError("y_true and scores differ in length")
    positives = [s for s, t in zip(scores, y_true) if t == 1]
    negatives = [s for s, t in zip(scores, y_true) if t == 0]
    if not positives or not negatives:
        return 0.5
    wins = 0.0
    for p in positives:
        for q in negatives:
            if p > q:
                wins += 1.0
            elif p == q:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


X, y = make_blobs()
Xb = add_bias(X)
w = fit_logistic(Xb, y)
labels = predict_label(Xb, w)
print("weights:", [round(v, 4) for v in w])
print("f1:", round(f1_score(y, labels), 4), "auc:", round(roc_auc(y, predict_proba(Xb, w)), 4))
'''}],
                "hints": [
                    "Write `sigmoid` with the branch on the sign of `z` first — every later function depends on it never raising OverflowError.",
                    "`confusion_matrix` is the single source of truth: build `precision`, `recall` and `f1_score` on top of it rather than counting three more times.",
                    "The regularised gradient is the plain gradient plus `l2 * w[j] / n`, and only for `j >= 1`. Penalising the intercept quietly biases every prediction towards 0.5.",
                    "For `roc_auc`, split the scores into the positive and negative lists first, then compare every pair: `>` scores 1, `==` scores 0.5, and divide by `len(pos) * len(neg)`.",
                ],
                "tests": [
                    {"name": "sigmoid is safe at both extremes", "code": r'''
assert sigmoid(0.0) == 0.5, f"sigmoid(0) gave {sigmoid(0.0)!r}, expected 0.5"
assert abs(sigmoid(2.0) - 0.8807970779778823) < 1e-12, f"sigmoid(2) gave {sigmoid(2.0)!r}"
assert abs(sigmoid(-2.0) - 0.11920292202211755) < 1e-12, f"sigmoid(-2) gave {sigmoid(-2.0)!r}"
assert sigmoid(800.0) == 1.0, f"sigmoid(800) gave {sigmoid(800.0)!r}, expected 1.0"
assert sigmoid(-800.0) == 0.0, f"sigmoid(-800) gave {sigmoid(-800.0)!r} — branch on the sign of z"
'''},
                    {"name": "cross_entropy, including the clipped extreme", "code": r'''
_got = cross_entropy([1, 0], [0.9, 0.2])
assert abs(_got - 0.16425203348601802) < 1e-12, \
    f"cross_entropy([1,0], [0.9,0.2]) gave {_got!r}, expected 0.16425203348601802"
assert cross_entropy([1, 0], [1.0, 0.0]) < 1e-9, \
    f"A perfect confident fit should score ~0, got {cross_entropy([1, 0], [1.0, 0.0])!r}"
_bad = cross_entropy([1], [0.0])
assert 20.0 < _bad < 40.0, f"A confident mistake should cost about 27.6 (the clip), got {_bad!r}"
try:
    cross_entropy([1, 0], [0.5])
    assert False, "Mismatched lengths should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The confusion matrix and the three rates", "code": r'''
_t = [1, 1, 1, 0, 0, 0, 0, 1]
_p = [1, 0, 1, 0, 1, 0, 0, 1]
_cm = confusion_matrix(_t, _p)
assert _cm == (3, 1, 1, 3), f"confusion_matrix gave {_cm!r}, expected (tp, fp, fn, tn) = (3, 1, 1, 3)"
assert abs(precision(_t, _p) - 0.75) < 1e-12, f"precision gave {precision(_t, _p)!r}, expected 0.75"
assert abs(recall(_t, _p) - 0.75) < 1e-12, f"recall gave {recall(_t, _p)!r}, expected 0.75"
assert abs(f1_score(_t, _p) - 0.75) < 1e-12, f"f1_score gave {f1_score(_t, _p)!r}, expected 0.75"
'''},
                    {"name": "Degenerate metric cases return 0.0", "code": r'''
assert precision([1, 1], [0, 0]) == 0.0, "Nothing predicted positive: precision is 0.0, not a crash"
assert recall([0, 0], [1, 1]) == 0.0, "No true positives: recall is 0.0, not a crash"
assert f1_score([0, 0], [0, 0]) == 0.0, "No positives anywhere: f1 is 0.0, not a crash"
assert confusion_matrix([0, 0], [0, 0]) == (0, 0, 0, 2), \
    f"confusion_matrix gave {confusion_matrix([0, 0], [0, 0])!r}, expected (0, 0, 0, 2)"
'''},
                    {"name": "ROC-AUC ranks, ties and degenerates", "code": r'''
_got = roc_auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8])
assert abs(_got - 0.75) < 1e-12, f"roc_auc gave {_got!r}, expected 0.75"
assert abs(roc_auc([0, 1], [0.2, 0.9]) - 1.0) < 1e-12, "A perfect ranking scores 1.0"
assert abs(roc_auc([0, 1], [0.9, 0.2]) - 0.0) < 1e-12, "A perfectly wrong ranking scores 0.0"
assert abs(roc_auc([0, 1], [0.5, 0.5]) - 0.5) < 1e-12, "A tie is worth half a win"
assert roc_auc([1, 1, 1], [0.1, 0.2, 0.3]) == 0.5, "With one class present AUC is undefined — return 0.5"
'''},
                    {"name": "The fit separates the blobs", "code": r'''
_X, _y = make_blobs(120, 7)
_Xb = add_bias(_X)
_w = fit_logistic(_Xb, _y, 0.5, 2000)
assert len(_w) == 3, f"With a bias column the weight vector has 3 entries, got {len(_w)}"
_probs = predict_proba(_Xb, _w)
assert all(0.0 <= p <= 1.0 for p in _probs), "Probabilities must stay inside [0, 1]"
_labels = predict_label(_Xb, _w)
_acc = sum(1 for a, b in zip(_labels, _y) if a == b) / len(_y)
assert _acc == 1.0, f"The two clouds are separable — training accuracy was {_acc!r}, expected 1.0"
assert abs(roc_auc(_y, _probs) - 1.0) < 1e-12, f"AUC was {roc_auc(_y, _probs)!r}, expected 1.0"
assert _w[1] > 0 and _w[2] > 0, f"Both features push towards class 1, so both weights are positive; got {_w!r}"
'''},
                    {"name": "L2 shrinks the coefficients but not the intercept", "code": r'''
_X, _y = make_blobs(120, 7)
_Xb = add_bias(_X)
_plain = fit_logistic(_Xb, _y, 0.5, 2000, 0.0)
_ridged = fit_logistic(_Xb, _y, 0.5, 2000, 50.0)
_np = sum(v * v for v in _plain[1:]) ** 0.5
_nr = sum(v * v for v in _ridged[1:]) ** 0.5
assert _nr < _np, f"L2 should shrink the slope norm: got {_nr!r} with penalty, {_np!r} without"
_loss_plain = cross_entropy(_y, predict_proba(_Xb, _plain))
_loss_ridged = cross_entropy(_y, predict_proba(_Xb, _ridged))
assert _loss_plain <= _loss_ridged + 1e-12, \
    f"The unpenalised fit must reach the lower training loss: {_loss_plain!r} vs {_loss_ridged!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Trees, bagging and the variance they trade away",
            "summary": "Impurity-driven splits, depth control, then bootstrap aggregation into a forest.",
            "concepts": [
                "Gini impurity and Shannon entropy as two measures of node disorder",
                "Information gain: parent impurity minus the size-weighted child impurity",
                "Candidate thresholds are midpoints between consecutive sorted feature values",
                "Depth, minimum split size and zero-gain nodes are the three stopping rules",
                "An unpruned tree memorises: perfect training accuracy, mediocre test accuracy",
                "Bootstrap aggregation averages away variance without touching bias",
                "Random feature subsets at each split decorrelate the trees, which is why forests beat bagging",
            ],
            "lab": {
                "title": "A decision tree, then a forest around it",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
`make_ring_data(n, seed)` is supplied: points in a square, labelled 1 outside a
circle of radius^2 = 3.2 and 0 inside, with 10% of the labels flipped. No single
straight line fits it, and the noise punishes anything that memorises.

**`gini(labels)`** and **`entropy(labels)`** — entropy in bits (`log2`). Both
return `0.0` for an empty list.

```text
gini([0, 0, 1, 1])     -> 0.5        entropy([0, 0, 1, 1]) -> 1.0
gini([0, 0, 0, 1])     -> 0.375      entropy([0, 0, 0, 1]) -> 0.8112781244591328
```

**`best_split(X, y, criterion="gini", features=None)`** — try every candidate
threshold on every allowed feature and return `(index, threshold, gain)` for the
best, or `None` when fewer than two samples are given. Candidates are the
midpoints of consecutive **sorted distinct** values; `left` is `x <= threshold`.
`features` restricts the search to a list of column indices.

```text
best_split([[1], [2], [3], [4]], [0, 0, 1, 1])  ->  (0, 2.5, 0.5)
```

**`DecisionTree(max_depth=3, min_samples_split=2, criterion="gini",
max_features=None, rng=None)`** with `.fit(X, y)`, `.predict(X)` and `.depth()`.
A node becomes a leaf when the depth limit is reached, when fewer than
`min_samples_split` samples remain, when the labels are pure, or when the best
gain is not positive. A leaf predicts the majority label, **ties broken by the
smaller label**. When `max_features` and `rng` are both given, each node searches
`rng.sample(range(d), min(max_features, d))` instead of every column.

**`RandomForest(n_trees=25, max_depth=6, max_features=1, seed=7)`** with `.fit`
and `.predict`. Build one `random.Random(seed)` for the whole forest, and per
tree draw `n` bootstrap indices with `rng.randrange(n)` before fitting a
`DecisionTree` that shares that same `rng`. Predictions are a majority vote,
ties again broken by the smaller label.

Split the 220 rows as the first 150 for training and the last 70 for testing.
A depth-8 tree memorises the training set exactly; the forest should beat it on
the held-out rows by a wide margin.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random
from collections import Counter


def make_ring_data(n=220, seed=11):
    """Points labelled 1 outside a circle, with 10% label noise."""
    rng = random.Random(seed)
    X, y = [], []
    for _ in range(n):
        a = rng.uniform(-3, 3)
        b = rng.uniform(-3, 3)
        label = 1 if (a * a + b * b) > 3.2 else 0
        if rng.random() < 0.10:
            label = 1 - label
        X.append([a, b])
        y.append(label)
    return X, y


def accuracy(y_true, y_pred):
    """Fraction of labels predicted correctly."""
    return sum(1 for a, b in zip(y_true, y_pred) if a == b) / len(y_true)


def gini(labels):
    """1 - sum(p^2)."""
    # your code here


def entropy(labels):
    """-sum(p log2 p)."""
    # your code here


def majority_label(labels):
    """Most common label; ties go to the smaller label."""
    # your code here


def best_split(X, y, criterion="gini", features=None):
    """(feature_index, threshold, gain) for the best split, or None."""
    # your code here


class DecisionTree:
    def __init__(self, max_depth=3, min_samples_split=2, criterion="gini",
                 max_features=None, rng=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion = criterion
        self.max_features = max_features
        self.rng = rng
        self.root = None

    def fit(self, X, y):
        """Grow the tree and return self."""
        # your code here

    def predict(self, X):
        """One label per row."""
        # your code here

    def depth(self):
        """Number of edges on the longest root-to-leaf path."""
        # your code here


class RandomForest:
    def __init__(self, n_trees=25, max_depth=6, max_features=1, seed=7):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.max_features = max_features
        self.seed = seed
        self.trees = []

    def fit(self, X, y):
        """Bootstrap n_trees trees and return self."""
        # your code here

    def predict(self, X):
        """Majority vote across the trees."""
        # your code here


X, y = make_ring_data()
print("class balance:", Counter(y))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random
from collections import Counter


def make_ring_data(n=220, seed=11):
    """Points labelled 1 outside a circle, with 10% label noise."""
    rng = random.Random(seed)
    X, y = [], []
    for _ in range(n):
        a = rng.uniform(-3, 3)
        b = rng.uniform(-3, 3)
        label = 1 if (a * a + b * b) > 3.2 else 0
        if rng.random() < 0.10:
            label = 1 - label
        X.append([a, b])
        y.append(label)
    return X, y


def accuracy(y_true, y_pred):
    """Fraction of labels predicted correctly."""
    return sum(1 for a, b in zip(y_true, y_pred) if a == b) / len(y_true)


def gini(labels):
    """1 - sum(p^2)."""
    n = len(labels)
    if n == 0:
        return 0.0
    return 1.0 - sum((c / n) ** 2 for c in Counter(labels).values())


def entropy(labels):
    """-sum(p log2 p)."""
    n = len(labels)
    if n == 0:
        return 0.0
    total = 0.0
    for count in Counter(labels).values():
        p = count / n
        total -= p * math.log2(p)
    return total


IMPURITY = {"gini": gini, "entropy": entropy}


def majority_label(labels):
    """Most common label; ties go to the smaller label."""
    counts = Counter(labels)
    best = max(counts.values())
    return min(label for label, count in counts.items() if count == best)


def best_split(X, y, criterion="gini", features=None):
    """(feature_index, threshold, gain) for the best split, or None."""
    n = len(y)
    if n < 2:
        return None
    impurity = IMPURITY[criterion]
    parent = impurity(y)
    columns = range(len(X[0])) if features is None else features
    best = None
    for j in columns:
        values = sorted(set(row[j] for row in X))
        for low, high in zip(values, values[1:]):
            threshold = (low + high) / 2.0
            left = [y[i] for i in range(n) if X[i][j] <= threshold]
            right = [y[i] for i in range(n) if X[i][j] > threshold]
            if not left or not right:
                continue
            child = (len(left) / n) * impurity(left) + (len(right) / n) * impurity(right)
            gain = parent - child
            if best is None or gain > best[2] + 1e-15:
                best = (j, threshold, gain)
    return best


class DecisionTree:
    """A binary CART-style tree over numeric features."""

    def __init__(self, max_depth=3, min_samples_split=2, criterion="gini",
                 max_features=None, rng=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion = criterion
        self.max_features = max_features
        self.rng = rng
        self.root = None

    def _grow(self, X, y, depth):
        if (depth >= self.max_depth or len(y) < self.min_samples_split
                or len(set(y)) == 1):
            return {"leaf": True, "label": majority_label(y)}
        features = None
        if self.max_features is not None and self.rng is not None:
            k = min(self.max_features, len(X[0]))
            features = sorted(self.rng.sample(range(len(X[0])), k))
        split = best_split(X, y, self.criterion, features)
        if split is None or split[2] <= 1e-12:
            return {"leaf": True, "label": majority_label(y)}
        j, threshold, _ = split
        left = [i for i in range(len(y)) if X[i][j] <= threshold]
        right = [i for i in range(len(y)) if X[i][j] > threshold]
        return {
            "leaf": False,
            "feature": j,
            "threshold": threshold,
            "left": self._grow([X[i] for i in left], [y[i] for i in left], depth + 1),
            "right": self._grow([X[i] for i in right], [y[i] for i in right], depth + 1),
        }

    def fit(self, X, y):
        """Grow the tree and return self."""
        if len(X) != len(y) or not X:
            raise ValueError("X and y must be non-empty and the same length")
        self.root = self._grow(X, y, 0)
        return self

    def _decide(self, row):
        node = self.root
        while not node["leaf"]:
            node = node["left"] if row[node["feature"]] <= node["threshold"] else node["right"]
        return node["label"]

    def predict(self, X):
        """One label per row."""
        return [self._decide(row) for row in X]

    def _depth(self, node):
        if node["leaf"]:
            return 0
        return 1 + max(self._depth(node["left"]), self._depth(node["right"]))

    def depth(self):
        """Number of edges on the longest root-to-leaf path."""
        return self._depth(self.root)


class RandomForest:
    """Bootstrap aggregation over decision trees with random feature subsets."""

    def __init__(self, n_trees=25, max_depth=6, max_features=1, seed=7):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.max_features = max_features
        self.seed = seed
        self.trees = []

    def fit(self, X, y):
        """Bootstrap n_trees trees and return self."""
        rng = random.Random(self.seed)
        n = len(y)
        self.trees = []
        for _ in range(self.n_trees):
            picks = [rng.randrange(n) for _ in range(n)]
            tree = DecisionTree(self.max_depth, 2, "gini", self.max_features, rng)
            tree.fit([X[i] for i in picks], [y[i] for i in picks])
            self.trees.append(tree)
        return self

    def predict(self, X):
        """Majority vote across the trees."""
        votes = [tree.predict(X) for tree in self.trees]
        return [majority_label([vote[i] for vote in votes]) for i in range(len(X))]


X, y = make_ring_data()
X_train, y_train = X[:150], y[:150]
X_test, y_test = X[150:], y[150:]

deep = DecisionTree(max_depth=8).fit(X_train, y_train)
forest = RandomForest().fit(X_train, y_train)
print("deep tree  train/test:", accuracy(y_train, deep.predict(X_train)),
      round(accuracy(y_test, deep.predict(X_test)), 4))
print("forest         test:", round(accuracy(y_test, forest.predict(X_test)), 4))
'''}],
                "hints": [
                    "Write `gini` and `entropy` from a `Counter`, and keep the empty-list guard — `best_split` calls them on child nodes that a bad threshold can leave empty.",
                    "For candidate thresholds take `sorted(set(column))` and pair consecutive values with `zip(values, values[1:])`; the midpoint of each pair is the only threshold worth trying.",
                    "Grow the tree recursively into plain dicts: `{\"leaf\": True, \"label\": ...}` or `{\"leaf\": False, \"feature\": j, \"threshold\": t, \"left\": ..., \"right\": ...}`. Prediction is then a `while not node[\"leaf\"]` loop.",
                    "The forest owns one `random.Random(seed)`. Pass that same object to every tree so the bootstrap draws and the per-node feature samples come from one reproducible stream.",
                ],
                "tests": [
                    {"name": "Impurity measures on known nodes", "code": r'''
assert abs(gini([0, 0, 1, 1]) - 0.5) < 1e-12, f"gini([0,0,1,1]) gave {gini([0, 0, 1, 1])!r}, expected 0.5"
assert abs(gini([0, 0, 0, 1]) - 0.375) < 1e-12, f"gini([0,0,0,1]) gave {gini([0, 0, 0, 1])!r}, expected 0.375"
assert gini([1, 1, 1]) == 0.0, f"A pure node has gini 0, got {gini([1, 1, 1])!r}"
assert gini([]) == 0.0 and entropy([]) == 0.0, "An empty node has zero impurity, not a crash"
assert abs(entropy([0, 0, 1, 1]) - 1.0) < 1e-12, f"entropy([0,0,1,1]) gave {entropy([0, 0, 1, 1])!r}, expected 1.0"
assert abs(entropy([0, 0, 0, 1]) - 0.8112781244591328) < 1e-12, \
    f"entropy([0,0,0,1]) gave {entropy([0, 0, 0, 1])!r}, expected 0.8112781244591328"
'''},
                    {"name": "best_split finds the midpoint and the gain", "code": r'''
_got = best_split([[1], [2], [3], [4]], [0, 0, 1, 1])
assert _got is not None, "best_split returned None on a perfectly splittable set"
assert _got[0] == 0, f"The only feature is index 0, got {_got[0]!r}"
assert abs(_got[1] - 2.5) < 1e-12, f"The threshold should be the midpoint 2.5, got {_got[1]!r}"
assert abs(_got[2] - 0.5) < 1e-12, f"Gain should be 0.5 - 0.0 = 0.5, got {_got[2]!r}"
assert best_split([[1]], [0]) is None, "Fewer than two samples cannot be split"
_pure = best_split([[1], [2], [3], [4]], [1, 1, 1, 1])
assert _pure is None or _pure[2] < 1e-12, f"A pure node offers no gain, got {_pure!r}"
_restricted = best_split([[9, 1], [9, 2], [9, 3], [9, 4]], [0, 0, 1, 1], "gini", [0])
assert _restricted is None or _restricted[2] < 1e-12, \
    f"Restricted to the constant feature there is no useful split, got {_restricted!r}"
'''},
                    {"name": "Depth limits and leaf predictions", "code": r'''
_X = [[1.0], [2.0], [3.0], [4.0]]
_y = [0, 0, 1, 1]
_stump = DecisionTree(max_depth=1).fit(_X, _y)
assert _stump.predict(_X) == [0, 0, 1, 1], f"A depth-1 stump separates this set; got {_stump.predict(_X)!r}"
assert _stump.depth() == 1, f"The stump has depth 1, got {_stump.depth()!r}"
_root_only = DecisionTree(max_depth=0).fit(_X, [0, 1, 1, 1])
assert _root_only.depth() == 0, f"max_depth=0 leaves a single leaf, got depth {_root_only.depth()!r}"
assert _root_only.predict(_X) == [1, 1, 1, 1], \
    f"A root-only tree predicts the majority label everywhere, got {_root_only.predict(_X)!r}"
assert majority_label([1, 1, 0, 0]) == 0, f"Ties go to the smaller label, got {majority_label([1, 1, 0, 0])!r}"
_pure_tree = DecisionTree(max_depth=5).fit(_X, [1, 1, 1, 1])
assert _pure_tree.depth() == 0, f"Pure labels stop the recursion at once, got depth {_pure_tree.depth()!r}"
'''},
                    {"name": "Entropy and gini both grow usable trees", "code": r'''
_X, _y = make_ring_data(220, 11)
_Xtr, _ytr, _Xte, _yte = _X[:150], _y[:150], _X[150:], _y[150:]
for _crit in ("gini", "entropy"):
    _t = DecisionTree(max_depth=4, criterion=_crit).fit(_Xtr, _ytr)
    _a = accuracy(_yte, _t.predict(_Xte))
    assert _a > 0.6, f"A depth-4 {_crit} tree scored {_a!r} on the held-out rows, expected over 0.6"
    assert _t.depth() <= 4, f"max_depth=4 was exceeded: depth is {_t.depth()!r}"
'''},
                    {"name": "An unpruned tree memorises the training set", "code": r'''
_X, _y = make_ring_data(220, 11)
_Xtr, _ytr, _Xte, _yte = _X[:150], _y[:150], _X[150:], _y[150:]
_deep = DecisionTree(max_depth=8).fit(_Xtr, _ytr)
_train_acc = accuracy(_ytr, _deep.predict(_Xtr))
_test_acc = accuracy(_yte, _deep.predict(_Xte))
assert _train_acc == 1.0, f"A depth-8 tree fits these 150 rows exactly; training accuracy was {_train_acc!r}"
assert _test_acc < _train_acc, \
    f"10% of the labels are noise, so held-out accuracy ({_test_acc!r}) must fall short of {_train_acc!r}"
'''},
                    {"name": "The forest beats the single deep tree", "code": r'''
_X, _y = make_ring_data(220, 11)
_Xtr, _ytr, _Xte, _yte = _X[:150], _y[:150], _X[150:], _y[150:]
_deep = DecisionTree(max_depth=8).fit(_Xtr, _ytr)
_forest = RandomForest(25, 6, 1, 7).fit(_Xtr, _ytr)
assert len(_forest.trees) == 25, f"Expected 25 fitted trees, found {len(_forest.trees)}"
_tree_acc = accuracy(_yte, _deep.predict(_Xte))
_forest_acc = accuracy(_yte, _forest.predict(_Xte))
assert _forest_acc >= 0.82, f"The forest scored {_forest_acc!r} on the held-out rows, expected at least 0.82"
assert _forest_acc > _tree_acc, \
    f"Bagging should beat the single deep tree: forest {_forest_acc!r} vs tree {_tree_acc!r}"
'''},
                    {"name": "The same seed gives the same forest", "code": r'''
_X, _y = make_ring_data(220, 11)
_a = RandomForest(10, 5, 1, 3).fit(_X[:150], _y[:150]).predict(_X[150:])
_b = RandomForest(10, 5, 1, 3).fit(_X[:150], _y[:150]).predict(_X[150:])
assert _a == _b, "Two forests built with seed 3 must predict identically"
_c = RandomForest(10, 5, 1, 4).fit(_X[:150], _y[:150]).predict(_X[150:])
assert _c != _a, "A different seed should draw different bootstrap samples and change some predictions"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Unsupervised structure",
            "summary": "k-means++ with inertia, and principal components by power iteration.",
            "concepts": [
                "k-means minimises within-cluster sum of squares; Lloyd's algorithm alternates two steps",
                "Inertia never rises across an iteration, but it is not comparable across different k",
                "Naive random seeding can land two centres in one cluster; k-means++ samples proportionally to D^2",
                "The sample covariance matrix, and why the n-1 denominator is the unbiased choice",
                "Power iteration converges to the dominant eigenvector at a rate set by the eigenvalue gap",
                "Hotelling deflation, A - lambda v v^T, exposes the next component",
                "Explained variance ratio is an eigenvalue divided by the trace",
            ],
            "lab": {
                "title": "k-means++ and PCA from first principles",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
Two unsupervised workhorses, both from arithmetic.

## Clustering

**`euclidean(a, b)`** — the usual distance.

**`kmeans_plus_plus_init(X, k, rng)`** — pick the first centre with
`rng.randrange(len(X))`, then repeatedly pick a point with probability
proportional to its squared distance to the nearest chosen centre. Draw with
`rng.random() * total` and walk a running sum. Return `k` lists.

**`assign_clusters(X, centres)`** — index of the nearest centre for every point,
ties going to the lower index.

**`inertia(X, labels, centres)`** — the summed squared distance of each point to
its own centre.

```text
inertia([[0.0], [2.0]], [0, 0], [[1.0]])  ->  2.0
```

**`kmeans(X, k, seed=7, max_iter=100)`** — k-means++ then Lloyd iterations until
the assignment stops changing. Return `(centres, labels, inertia)`. An empty
cluster keeps its previous centre.

## PCA

**`covariance_matrix(X)`** — the **sample** covariance, dividing by `n - 1`.

```text
covariance_matrix([[1, 2], [3, 6], [5, 10]])  ->  [[4.0, 8.0], [8.0, 16.0]]
```

**`power_iteration(A, iters=500, tol=1e-12, seed=0)`** — draw a start vector with
`random.Random(seed).gauss(0, 1)` per component and normalise it, then repeat
`v <- Av / ||Av||`, stop when `v` settles, and return `(v^T A v, v)`. A zero
matrix returns eigenvalue `0.0` rather than dividing by zero. The random start
matters: an all-equal vector such as `(1, 1)/sqrt(2)` can sit *exactly* in the
null space of a deflated matrix, and the iteration then converges to nothing.

**`deflate(A, value, vector)`** — `A - value * v v^T`.

**`pca(X, n_components)`** — covariance, then power iteration and deflation
`n_components` times. Return `(components, eigenvalues)`.

**`project(X, components)`** — centre each row on the column means, then take the
dot product with each component.

`make_blobs3()` gives three tight, widely separated clusters; `make_line_data()`
gives 25 points lying exactly on the line through direction `(0.6, 0.8)`, so its
first eigenvalue is `3.3854166666666665` and the second is zero.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def make_blobs3(seed=3):
    """Three tight clusters at (0,0), (10,0) and (5,9), plus their true labels."""
    rng = random.Random(seed)
    X, truth = [], []
    for index, (cx, cy) in enumerate([(0.0, 0.0), (10.0, 0.0), (5.0, 9.0)]):
        for _ in range(40):
            X.append([cx + rng.gauss(0, 0.5), cy + rng.gauss(0, 0.5)])
            truth.append(index)
    return X, truth


def make_line_data():
    """25 points on the line (0.6t + 1, 0.8t - 2) for t from -3 to 3."""
    ts = [-3.0 + 0.25 * i for i in range(25)]
    return [[0.6 * t + 1.0, 0.8 * t - 2.0] for t in ts]


def euclidean(a, b):
    """Straight-line distance."""
    # your code here


def kmeans_plus_plus_init(X, k, rng):
    """k starting centres, sampled proportionally to squared distance."""
    # your code here


def assign_clusters(X, centres):
    """Index of the nearest centre for every point."""
    # your code here


def inertia(X, labels, centres):
    """Summed squared distance to the assigned centre."""
    # your code here


def kmeans(X, k, seed=7, max_iter=100):
    """(centres, labels, inertia) after Lloyd's algorithm."""
    # your code here


def covariance_matrix(X):
    """Sample covariance, dividing by n - 1."""
    # your code here


def matvec(A, v):
    """Matrix-vector product."""
    # your code here


def power_iteration(A, iters=500, tol=1e-12, seed=0):
    """(dominant eigenvalue, unit eigenvector) from a seeded random start."""
    # your code here


def deflate(A, value, vector):
    """A - value * v v^T."""
    # your code here


def pca(X, n_components):
    """(components, eigenvalues) by repeated power iteration and deflation."""
    # your code here


def project(X, components):
    """Centred rows projected onto each component."""
    # your code here


X, truth = make_blobs3()
print("points:", len(X))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def make_blobs3(seed=3):
    """Three tight clusters at (0,0), (10,0) and (5,9), plus their true labels."""
    rng = random.Random(seed)
    X, truth = [], []
    for index, (cx, cy) in enumerate([(0.0, 0.0), (10.0, 0.0), (5.0, 9.0)]):
        for _ in range(40):
            X.append([cx + rng.gauss(0, 0.5), cy + rng.gauss(0, 0.5)])
            truth.append(index)
    return X, truth


def make_line_data():
    """25 points on the line (0.6t + 1, 0.8t - 2) for t from -3 to 3."""
    ts = [-3.0 + 0.25 * i for i in range(25)]
    return [[0.6 * t + 1.0, 0.8 * t - 2.0] for t in ts]


def euclidean(a, b):
    """Straight-line distance."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def kmeans_plus_plus_init(X, k, rng):
    """k starting centres, sampled proportionally to squared distance."""
    if k < 1 or k > len(X):
        raise ValueError("k must be between 1 and len(X)")
    centres = [list(X[rng.randrange(len(X))])]
    while len(centres) < k:
        weights = [min(euclidean(point, c) ** 2 for c in centres) for point in X]
        total = sum(weights)
        if total <= 0.0:
            centres.append(list(X[rng.randrange(len(X))]))
            continue
        target = rng.random() * total
        running = 0.0
        for point, weight in zip(X, weights):
            running += weight
            if running >= target:
                centres.append(list(point))
                break
    return centres


def assign_clusters(X, centres):
    """Index of the nearest centre for every point."""
    labels = []
    for point in X:
        best_index = 0
        best_distance = euclidean(point, centres[0])
        for index in range(1, len(centres)):
            distance = euclidean(point, centres[index])
            if distance < best_distance - 1e-15:
                best_index, best_distance = index, distance
        labels.append(best_index)
    return labels


def inertia(X, labels, centres):
    """Summed squared distance to the assigned centre."""
    return sum(euclidean(point, centres[label]) ** 2 for point, label in zip(X, labels))


def kmeans(X, k, seed=7, max_iter=100):
    """(centres, labels, inertia) after Lloyd's algorithm."""
    rng = random.Random(seed)
    centres = kmeans_plus_plus_init(X, k, rng)
    labels = assign_clusters(X, centres)
    for _ in range(max_iter):
        moved = []
        for index in range(k):
            members = [p for p, l in zip(X, labels) if l == index]
            if not members:
                moved.append(list(centres[index]))
            else:
                moved.append([sum(col) / len(members) for col in zip(*members)])
        centres = moved
        relabelled = assign_clusters(X, centres)
        if relabelled == labels:
            break
        labels = relabelled
    return centres, labels, inertia(X, labels, centres)


def covariance_matrix(X):
    """Sample covariance, dividing by n - 1."""
    n = len(X)
    if n < 2:
        raise ValueError("covariance needs at least two rows")
    d = len(X[0])
    means = [sum(row[j] for row in X) / n for j in range(d)]
    C = [[0.0] * d for _ in range(d)]
    for row in X:
        for i in range(d):
            for j in range(d):
                C[i][j] += (row[i] - means[i]) * (row[j] - means[j])
    return [[value / (n - 1) for value in row] for row in C]


def matvec(A, v):
    """Matrix-vector product."""
    return [sum(a * b for a, b in zip(row, v)) for row in A]


def power_iteration(A, iters=500, tol=1e-12, seed=0):
    """(dominant eigenvalue, unit eigenvector) from a seeded random start."""
    d = len(A)
    rng = random.Random(seed)
    v = [rng.gauss(0.0, 1.0) for _ in range(d)]
    scale = math.sqrt(sum(x * x for x in v))
    v = [x / scale for x in v]
    for _ in range(iters):
        w = matvec(A, v)
        norm = math.sqrt(sum(x * x for x in w))
        if norm < 1e-300:
            return 0.0, v
        nxt = [x / norm for x in w]
        if sum(abs(a - b) for a, b in zip(nxt, v)) < tol:
            v = nxt
            break
        v = nxt
    Av = matvec(A, v)
    return sum(a * b for a, b in zip(v, Av)), v


def deflate(A, value, vector):
    """A - value * v v^T."""
    d = len(A)
    return [[A[i][j] - value * vector[i] * vector[j] for j in range(d)] for i in range(d)]


def pca(X, n_components):
    """(components, eigenvalues) by repeated power iteration and deflation."""
    C = covariance_matrix(X)
    components, eigenvalues = [], []
    for _ in range(n_components):
        value, vector = power_iteration(C)
        components.append(vector)
        eigenvalues.append(value)
        C = deflate(C, value, vector)
    return components, eigenvalues


def project(X, components):
    """Centred rows projected onto each component."""
    n = len(X)
    d = len(X[0])
    means = [sum(row[j] for row in X) / n for j in range(d)]
    out = []
    for row in X:
        centred = [row[j] - means[j] for j in range(d)]
        out.append([sum(c * w for c, w in zip(centred, comp)) for comp in components])
    return out


X, truth = make_blobs3()
centres, labels, cost = kmeans(X, 3)
print("k=3 inertia:", round(cost, 4))
components, values = pca(make_line_data(), 2)
print("first component:", [round(v, 6) for v in components[0]], "eigenvalues:", values)
'''}],
                "hints": [
                    "For k-means++, the sampling step is a weighted draw: compute `weights[i] = min squared distance to a chosen centre`, take `target = rng.random() * sum(weights)`, then walk the list accumulating until the running total reaches the target.",
                    "Lloyd's loop is assign, recompute means, assign again. Stop as soon as the new labels equal the old ones — that is the fixed point, and iterating further changes nothing.",
                    "Build the covariance matrix from the column means with two nested loops over the dimensions; divide by `n - 1` at the end, not inside the accumulation.",
                    "After `power_iteration` returns `(value, v)`, deflate with `A - value * v v^T` and run it again — the dominant eigenvector of the deflated matrix is the second principal component. Start the iteration from a seeded random vector, not from `(1, 1, ...)/sqrt(d)`: on a deflated matrix that particular start can be orthogonal to the answer.",
                ],
                "tests": [
                    {"name": "Distance and inertia", "code": r'''
assert abs(euclidean([0.0, 0.0], [3.0, 4.0]) - 5.0) < 1e-12, \
    f"euclidean((0,0), (3,4)) gave {euclidean([0.0, 0.0], [3.0, 4.0])!r}, expected 5.0"
assert euclidean([1.0], [1.0]) == 0.0, "A point is zero distance from itself"
assert abs(inertia([[0.0], [2.0]], [0, 0], [[1.0]]) - 2.0) < 1e-12, \
    f"inertia gave {inertia([[0.0], [2.0]], [0, 0], [[1.0]])!r}, expected 2.0"
assert inertia([[5.0], [5.0]], [0, 0], [[5.0]]) == 0.0, "Identical points on their centre cost nothing"
assert assign_clusters([[0.0], [9.0]], [[0.0], [10.0]]) == [0, 1], \
    f"assign_clusters gave {assign_clusters([[0.0], [9.0]], [[0.0], [10.0]])!r}, expected [0, 1]"
'''},
                    {"name": "k-means++ seeds k distinct points of X", "code": r'''
import random as _random
_X, _truth = make_blobs3(3)
_centres = kmeans_plus_plus_init(_X, 3, _random.Random(7))
assert len(_centres) == 3, f"Expected 3 centres, got {len(_centres)}"
_as_points = [list(c) for c in _centres]
for _c in _as_points:
    assert _c in [list(p) for p in _X], f"Every k-means++ centre is a data point; {_c!r} is not"
assert len({tuple(c) for c in _as_points}) == 3, f"The three centres must be distinct, got {_as_points!r}"
'''},
                    {"name": "k-means recovers the three blobs", "code": r'''
_X, _truth = make_blobs3(3)
_centres, _labels, _cost = kmeans(_X, 3, 7)
assert len(set(_labels)) == 3, f"Expected three non-empty clusters, got {len(set(_labels))}"
for _cluster in set(_labels):
    _members = {_truth[i] for i in range(len(_truth)) if _labels[i] == _cluster}
    assert len(_members) == 1, f"Cluster {_cluster} mixes true blobs {_members!r} — the blobs are far apart"
assert _cost < 100.0, f"With three tight blobs the inertia should be well under 100, got {_cost!r}"
_, _, _cost2 = kmeans(_X, 2, 7)
assert _cost2 > _cost, f"Fewer clusters cannot fit better: k=2 gave {_cost2!r}, k=3 gave {_cost!r}"
_, _labels_again, _ = kmeans(_X, 3, 7)
assert _labels_again == _labels, "The same seed must reproduce the same clustering"
'''},
                    {"name": "The sample covariance matrix", "code": r'''
_C = covariance_matrix([[1.0, 2.0], [3.0, 6.0], [5.0, 10.0]])
_want = [[4.0, 8.0], [8.0, 16.0]]
for _i in range(2):
    for _j in range(2):
        assert abs(_C[_i][_j] - _want[_i][_j]) < 1e-9, \
            f"covariance_matrix gave {_C!r}, expected {_want!r} (divide by n - 1)"
assert abs(_C[0][1] - _C[1][0]) < 1e-12, "A covariance matrix is symmetric"
'''},
                    {"name": "Power iteration finds the dominant eigenpair", "code": r'''
_value, _vector = power_iteration([[2.0, 1.0], [1.0, 2.0]])
assert abs(_value - 3.0) < 1e-8, f"The dominant eigenvalue of [[2,1],[1,2]] is 3, got {_value!r}"
assert abs(sum(x * x for x in _vector) - 1.0) < 1e-9, f"The eigenvector must be a unit vector, got {_vector!r}"
_align = abs(_vector[0] * 0.7071067811865476 + _vector[1] * 0.7071067811865476)
assert abs(_align - 1.0) < 1e-6, f"The eigenvector should lie along (1,1)/sqrt(2), got {_vector!r}"
_value2, _vector2 = power_iteration([[4.0, 8.0], [8.0, 16.0]])
assert abs(_value2 - 20.0) < 1e-7, f"The dominant eigenvalue of [[4,8],[8,16]] is 20, got {_value2!r}"
_align2 = abs(_vector2[0] * 0.4472135954999579 + _vector2[1] * 0.8944271909999159)
assert abs(_align2 - 1.0) < 1e-6, f"The eigenvector should lie along (1,2)/sqrt(5), got {_vector2!r}"
_zero_value, _ = power_iteration([[0.0, 0.0], [0.0, 0.0]])
assert _zero_value == 0.0, f"A zero matrix has eigenvalue 0 and must not divide by zero, got {_zero_value!r}"
'''},
                    {"name": "Deflation removes the component just found", "code": r'''
_A = [[2.0, 1.0], [1.0, 2.0]]
_value, _vector = power_iteration(_A)
_B = deflate(_A, _value, _vector)
_value2, _ = power_iteration(_B)
assert abs(_value2 - 1.0) < 1e-6, \
    f"After deflating away 3, the remaining eigenvalue of [[2,1],[1,2]] is 1, got {_value2!r}"
'''},
                    {"name": "PCA on data that lies exactly on a line", "code": r'''
_X = make_line_data()
_components, _values = pca(_X, 2)
assert abs(_values[0] - 3.3854166666666665) < 1e-7, \
    f"The first eigenvalue should be 3.3854166666666665, got {_values[0]!r}"
assert abs(_values[1]) < 1e-7, f"The data has no spread off the line, so the second eigenvalue is 0, got {_values[1]!r}"
_align = abs(_components[0][0] * 0.6 + _components[0][1] * 0.8)
assert abs(_align - 1.0) < 1e-6, \
    f"The first component should lie along (0.6, 0.8), got {_components[0]!r}"
_scores = project(_X, _components[:1])
_mean = sum(s[0] for s in _scores) / len(_scores)
assert abs(_mean) < 1e-9, f"Projections of centred data have mean 0, got {_mean!r}"
_var = sum((s[0] - _mean) ** 2 for s in _scores) / (len(_scores) - 1)
assert abs(_var - _values[0]) < 1e-7, \
    f"The variance along the first component is its eigenvalue: got {_var!r} against {_values[0]!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Model selection and the bias-variance trade-off",
            "summary": "k-fold cross-validation, L2 shrinkage, and a decomposition you can check to machine precision.",
            "concepts": [
                "Training error is not an estimate of anything; a held-out fold is",
                "k-fold cross-validation reuses every row for training and for testing exactly once",
                "Ridge regression solves (X^T X + alpha I) w = X^T y, leaving the intercept unpenalised",
                "Collinearity inflates least-squares variance; shrinkage trades a little bias for a lot of it",
                "The decomposition E[(f_hat - f)^2] = bias^2 + variance is an identity, not an approximation",
                "Model capacity moves bias down and variance up; the sum has an interior minimum",
                "Selecting on the test set is the most common way to fool yourself",
            ],
            "lab": {
                "title": "Cross-validation, ridge, and a bias-variance decomposition",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
Three tools that decide which model you should actually ship.

**`k_folds(n, k, seed=7)`** — shuffle `list(range(n))` with
`random.Random(seed).shuffle`, then let fold `i` be `shuffled[i::k]`. Return a
list of `(train_indices, test_indices)` pairs, both **sorted ascending**, with
fold `i` as the test set.

```text
k_folds(10, 5, 7) test folds  ->  [0, 8], [3, 9], [1, 6], [2, 4], [5, 7]
```

**`ridge_fit(X, y, alpha)`** — solve `(X^T X + alpha I) w = X^T y`, but do
**not** add `alpha` to the top-left entry: `X` carries a bias column and the
intercept is not shrunk. `ValueError` for a negative `alpha`.

**`cross_val_mse(X, y, alpha, k=5, seed=7)`** — mean test MSE across the folds.

**`select_alpha(X, y, alphas, k=5, seed=7)`** — the candidate with the lowest
cross-validated MSE, earlier candidates winning ties.

**`poly_features(xs, degree)`** — rows `[x, x^2, ..., x^degree]`.

**`bias_variance(degree, n_sets=80, n_train=20, noise=0.3, seed=7)`** — the
demonstration. The truth is `f(x) = sin(3x)` on the grid
`[-1.0, -0.9, ..., 1.0]`. Draw `n_sets` independent training sets of `n_train`
points with `rng.uniform(-1, 1)` and Gaussian noise, fit
`ridge_fit(add_bias(poly_features(xs, degree)), ys, 1e-8)` to each, and predict
on the grid. Return `(bias_squared, variance, expected_error)` where, averaged
over the grid:

- `bias_squared` is `(mean prediction - f(x))^2`
- `variance` is the mean squared deviation of each prediction from the mean prediction
- `expected_error` is the mean squared deviation of each prediction from `f(x)`

Those three satisfy `bias_squared + variance == expected_error` exactly, so the
checks hold you to `1e-9`. Degree 1 is nearly all bias; degree 5 is nearly all
variance.

`make_collinear_data()` supplies 30 rows in which `x2` is a near-copy of `x1`,
the case where ridge earns its keep.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def make_collinear_data(n=30, seed=7):
    """x2 is x1 plus a whisper of jitter; y depends on x1 and x3 only."""
    rng = random.Random(seed)
    X, y = [], []
    for _ in range(n):
        a = rng.gauss(0, 1)
        b = a + rng.gauss(0, 0.001)
        c = rng.gauss(0, 1)
        X.append([a, b, c])
        y.append(2.0 * a + 0.5 * c + rng.gauss(0, 0.5))
    return X, y


def transpose(A):
    """Rows become columns."""
    return [list(col) for col in zip(*A)]


def matmul(A, B):
    """Matrix product."""
    Bt = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


def matvec(A, v):
    """Matrix-vector product."""
    return [sum(a * b for a, b in zip(row, v)) for row in A]


def solve_linear_system(A, b):
    """Gauss-Jordan with partial pivoting."""
    n = len(A)
    M = [list(map(float, row)) + [float(b[i])] for i, row in enumerate(A)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-12:
            raise ValueError("matrix is singular to working precision")
        M[col], M[pivot] = M[pivot], M[col]
        scale = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= scale
        for r in range(n):
            if r != col and M[r][col] != 0.0:
                factor = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= factor * M[col][j]
    return [M[i][n] for i in range(n)]


def add_bias(X):
    """Prepend a 1.0 column."""
    return [[1.0] + [float(v) for v in row] for row in X]


def predict(X, w):
    """Model predictions."""
    return matvec(X, w)


def mse(actual, predicted):
    """Mean squared error."""
    return sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)


def k_folds(n, k, seed=7):
    """[(train_indices, test_indices)] for each of the k folds."""
    # your code here


def ridge_fit(X, y, alpha):
    """Solve (X^T X + alpha I) w = X^T y, leaving the intercept unpenalised."""
    # your code here


def cross_val_mse(X, y, alpha, k=5, seed=7):
    """Mean held-out MSE across the folds."""
    # your code here


def select_alpha(X, y, alphas, k=5, seed=7):
    """The candidate alpha with the lowest cross-validated MSE."""
    # your code here


def poly_features(xs, degree):
    """Rows [x, x^2, ..., x^degree]."""
    # your code here


def bias_variance(degree, n_sets=80, n_train=20, noise=0.3, seed=7):
    """(bias_squared, variance, expected_error) over independent training sets."""
    # your code here


X, y = make_collinear_data()
print("rows:", len(X))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def make_collinear_data(n=30, seed=7):
    """x2 is x1 plus a whisper of jitter; y depends on x1 and x3 only."""
    rng = random.Random(seed)
    X, y = [], []
    for _ in range(n):
        a = rng.gauss(0, 1)
        b = a + rng.gauss(0, 0.001)
        c = rng.gauss(0, 1)
        X.append([a, b, c])
        y.append(2.0 * a + 0.5 * c + rng.gauss(0, 0.5))
    return X, y


def transpose(A):
    """Rows become columns."""
    return [list(col) for col in zip(*A)]


def matmul(A, B):
    """Matrix product."""
    Bt = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]


def matvec(A, v):
    """Matrix-vector product."""
    return [sum(a * b for a, b in zip(row, v)) for row in A]


def solve_linear_system(A, b):
    """Gauss-Jordan with partial pivoting."""
    n = len(A)
    M = [list(map(float, row)) + [float(b[i])] for i, row in enumerate(A)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-12:
            raise ValueError("matrix is singular to working precision")
        M[col], M[pivot] = M[pivot], M[col]
        scale = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= scale
        for r in range(n):
            if r != col and M[r][col] != 0.0:
                factor = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= factor * M[col][j]
    return [M[i][n] for i in range(n)]


def add_bias(X):
    """Prepend a 1.0 column."""
    return [[1.0] + [float(v) for v in row] for row in X]


def predict(X, w):
    """Model predictions."""
    return matvec(X, w)


def mse(actual, predicted):
    """Mean squared error."""
    return sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)


def k_folds(n, k, seed=7):
    """[(train_indices, test_indices)] for each of the k folds."""
    if k < 2 or k > n:
        raise ValueError("k must be between 2 and n")
    order = list(range(n))
    random.Random(seed).shuffle(order)
    folds = [order[i::k] for i in range(k)]
    splits = []
    for i in range(k):
        test = sorted(folds[i])
        train = sorted(index for f in range(k) if f != i for index in folds[f])
        splits.append((train, test))
    return splits


def ridge_fit(X, y, alpha):
    """Solve (X^T X + alpha I) w = X^T y, leaving the intercept unpenalised."""
    if alpha < 0:
        raise ValueError("alpha must not be negative")
    Xt = transpose(X)
    A = matmul(Xt, X)
    for i in range(1, len(A)):
        A[i][i] += alpha
    return solve_linear_system(A, matvec(Xt, y))


def cross_val_mse(X, y, alpha, k=5, seed=7):
    """Mean held-out MSE across the folds."""
    total = 0.0
    splits = k_folds(len(y), k, seed)
    for train, test in splits:
        w = ridge_fit([X[i] for i in train], [y[i] for i in train], alpha)
        total += mse([y[i] for i in test], predict([X[i] for i in test], w))
    return total / len(splits)


def select_alpha(X, y, alphas, k=5, seed=7):
    """The candidate alpha with the lowest cross-validated MSE."""
    best_alpha, best_score = None, None
    for alpha in alphas:
        score = cross_val_mse(X, y, alpha, k, seed)
        if best_score is None or score < best_score - 1e-15:
            best_alpha, best_score = alpha, score
    return best_alpha


def poly_features(xs, degree):
    """Rows [x, x^2, ..., x^degree]."""
    return [[x ** d for d in range(1, degree + 1)] for x in xs]


def bias_variance(degree, n_sets=80, n_train=20, noise=0.3, seed=7):
    """(bias_squared, variance, expected_error) over independent training sets."""
    rng = random.Random(seed)
    grid = [-1.0 + 0.1 * i for i in range(21)]
    truth = [math.sin(3.0 * x) for x in grid]
    grid_design = add_bias(poly_features(grid, degree))
    runs = []
    for _ in range(n_sets):
        xs = [rng.uniform(-1, 1) for _ in range(n_train)]
        ys = [math.sin(3.0 * x) + rng.gauss(0, noise) for x in xs]
        w = ridge_fit(add_bias(poly_features(xs, degree)), ys, 1e-8)
        runs.append(predict(grid_design, w))
    m = len(grid)
    mean_prediction = [sum(run[j] for run in runs) / n_sets for j in range(m)]
    bias_squared = sum((mean_prediction[j] - truth[j]) ** 2 for j in range(m)) / m
    variance = sum(sum((run[j] - mean_prediction[j]) ** 2 for run in runs) / n_sets
                   for j in range(m)) / m
    expected_error = sum(sum((run[j] - truth[j]) ** 2 for run in runs) / n_sets
                         for j in range(m)) / m
    return bias_squared, variance, expected_error


X, y = make_collinear_data()
Xb = add_bias(X)
ALPHAS = [0.0, 0.01, 0.1, 1.0, 10.0, 100.0]
print("chosen alpha:", select_alpha(Xb, y, ALPHAS))
for degree in (1, 5):
    print("degree", degree, "->", [round(v, 5) for v in bias_variance(degree)])
'''}],
                "hints": [
                    "`order[i::k]` is the whole fold construction — every index lands in exactly one stride, and the strides differ in size by at most one.",
                    "`ridge_fit` is the normal equation with a loop over `range(1, len(A))` adding alpha to the diagonal. Starting that loop at 1 is what keeps the intercept unpenalised.",
                    "`cross_val_mse` refits on each fold's training rows and scores the held-out rows. Never fit on rows you are about to score — that is the whole point of the split.",
                    "In `bias_variance`, accumulate the predictions of every training set on the fixed grid first. `bias^2`, `variance` and `expected_error` are then three different averages over that same table, and the first two must sum to the third.",
                ],
                "tests": [
                    {"name": "k_folds partitions the indices exactly once", "code": r'''
_splits = k_folds(10, 5, 7)
assert len(_splits) == 5, f"Expected 5 folds, got {len(_splits)}"
_test_sets = [test for _, test in _splits]
assert _test_sets == [[0, 8], [3, 9], [1, 6], [2, 4], [5, 7]], \
    f"With seed 7 the test folds are [[0,8],[3,9],[1,6],[2,4],[5,7]], got {_test_sets!r}"
_seen = sorted(i for fold in _test_sets for i in fold)
assert _seen == list(range(10)), f"Every index is tested exactly once, got {_seen!r}"
for _train, _test in _splits:
    assert sorted(_train + _test) == list(range(10)), "train and test must together cover every row"
    assert not set(_train) & set(_test), "A row must not appear in both halves of a fold"
    assert _train == sorted(_train) and _test == sorted(_test), "Both index lists come back sorted"
_uneven = [len(test) for _, test in k_folds(17, 4, 3)]
assert sorted(_uneven) == [4, 4, 4, 5], f"17 rows over 4 folds gives sizes 4,4,4,5; got {sorted(_uneven)!r}"
'''},
                    {"name": "Ridge with alpha = 0 is ordinary least squares", "code": r'''
_X = [[1.0, 2.0], [2.0, 1.0], [3.0, 4.0], [4.0, 3.0], [5.0, 7.0]]
_y = [3.0 + 2.0 * a - b for a, b in _X]
_w = ridge_fit(add_bias(_X), _y, 0.0)
for _got, _want in zip(_w, [3.0, 2.0, -1.0]):
    assert abs(_got - _want) < 1e-8, f"alpha=0 must reproduce least squares [3, 2, -1], got {_w!r}"
try:
    ridge_fit(add_bias(_X), _y, -1.0)
    assert False, "A negative alpha should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Ridge shrinks the slopes, not the intercept", "code": r'''
_X, _y = make_collinear_data()
_Xb = add_bias(_X)
_w0 = ridge_fit(_Xb, _y, 0.0)
_w1 = ridge_fit(_Xb, _y, 1.0)
_w2 = ridge_fit(_Xb, _y, 100.0)
_n0 = sum(v * v for v in _w0[1:]) ** 0.5
_n1 = sum(v * v for v in _w1[1:]) ** 0.5
_n2 = sum(v * v for v in _w2[1:]) ** 0.5
assert _n2 < _n1 < _n0, f"Slope norms should shrink as alpha grows, got {_n0!r}, {_n1!r}, {_n2!r}"
assert abs(_w0[1] + _w0[2]) > 1.0, \
    f"Near-collinear columns split the signal between w1 and w2; their sum was {_w0[1] + _w0[2]!r}"
assert _n2 > 0.0, "Shrinkage pulls towards zero, it does not reach it"
'''},
                    {"name": "Cross-validation prefers a positive alpha here", "code": r'''
_X, _y = make_collinear_data()
_Xb = add_bias(_X)
_alphas = [0.0, 0.01, 0.1, 1.0, 10.0, 100.0]
_scores = [cross_val_mse(_Xb, _y, a) for a in _alphas]
assert all(s > 0 for s in _scores), f"Cross-validated errors must be positive, got {_scores!r}"
_chosen = select_alpha(_Xb, _y, _alphas)
assert _chosen in _alphas, f"select_alpha must return one of the candidates, got {_chosen!r}"
_best = _alphas[_scores.index(min(_scores))]
assert _chosen == _best, f"select_alpha chose {_chosen!r} but the lowest CV error is at {_best!r}"
assert _chosen > 0.0, \
    f"On near-collinear data regularisation should win; select_alpha chose {_chosen!r} with scores {[round(s, 4) for s in _scores]!r}"
assert min(_scores) < _scores[0], \
    f"The best alpha should beat alpha=0: {min(_scores)!r} vs {_scores[0]!r}"
'''},
                    {"name": "poly_features builds the design columns", "code": r'''
assert poly_features([2.0], 3) == [[2.0, 4.0, 8.0]], f"poly_features gave {poly_features([2.0], 3)!r}"
assert poly_features([0.0, 1.0], 1) == [[0.0], [1.0]], f"poly_features gave {poly_features([0.0, 1.0], 1)!r}"
assert len(poly_features([1.0, 2.0, 3.0], 4)) == 3, "One row per input value"
assert len(poly_features([1.0], 4)[0]) == 4, "Degree 4 gives four columns, x through x^4"
'''},
                    {"name": "The decomposition is an exact identity", "code": r'''
for _degree in (1, 5):
    _b2, _var, _total = bias_variance(_degree)
    assert _b2 >= 0.0 and _var >= 0.0, f"Both terms are non-negative, got {(_b2, _var)!r}"
    assert abs(_b2 + _var - _total) < 1e-9, \
        f"degree {_degree}: bias^2 {_b2!r} + variance {_var!r} should equal {_total!r}"
'''},
                    {"name": "Capacity trades bias for variance", "code": r'''
_b1, _v1, _t1 = bias_variance(1)
_b5, _v5, _t5 = bias_variance(5)
assert _b1 > _b5, f"A straight line cannot follow sin(3x): bias^2 was {_b1!r} at degree 1 and {_b5!r} at degree 5"
assert _b1 > 0.05, f"The degree-1 bias^2 should be substantial, got {_b1!r}"
assert _v5 > _v1, f"The flexible model must wobble more: variance {_v5!r} at degree 5 against {_v1!r} at degree 1"
assert _v5 > 5.0 * _v1, f"The variance gap should be large, got {_v5!r} against {_v1!r}"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an honest end-to-end credit-default pipeline",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
`data.py` hands you `RAW_CSV`: 200 rows of a loan book, one header line and
these columns.

```text
age,income,years_employed,region,defaulted
44,43400,8,south,1
57,66300,29,north,1
```

`region` is categorical (`north`, `south`, `east`), `defaulted` is the target,
and **five income cells are blank**. About 40% of the rows defaulted, so a
majority-class classifier scores around 0.60 — that is the bar to beat.

`pipeline.py` holds the logic and is what the checks import. `main.py` is the
demonstration run. `data.py` is read-only.

## Loading and encoding

- `load_csv(text)` — `(header, rows)`, header as a list of names, rows as lists
  of strings. Blank lines are skipped.
- `median(values)` — the middle value, the mean of the middle two when even.
- `to_features(header, rows)` — `(X, y)`. Each row becomes exactly five numbers,
  in this order: `age`, `income`, `years_employed`, `is_north`, `is_south`.
  `east` is the baseline category, encoded as two zeros. A blank income is
  replaced by the **median of the incomes that are present**. `y` is `0`/`1`.

## Splitting, scaling, fitting

- `train_test_split(X, y, test_size=0.3, seed=7)` — shuffle `list(range(n))`
  with `random.Random(seed).shuffle`, take `cut = int(round(n * (1 - test_size)))`,
  and return `(X_train, y_train, X_test, y_test)` from `sorted(order[:cut])` and
  `sorted(order[cut:])`.
- `Scaler` — `fit(X)` records `means` and `stds` (population standard deviation,
  a zero-spread column keeping `1.0`); `transform(X)` applies them. Fit on the
  training rows **only**, then transform both halves. That is the whole of
  leakage control and the checks test for it.
- `LogisticModel(lr=0.8, epochs=250, l2=0.0)` — `fit(X, y)` runs batch gradient
  descent on the cross-entropy with an explicit intercept `w[0]` that the L2
  penalty never touches; `predict_proba(X)`; `predict(X, threshold=0.5)`.

## Metrics and selection

- `confusion_matrix`, `accuracy`, `precision`, `recall`, `f1_score`, `roc_auc` —
  the degenerate cases return `0.0` (or `0.5` for a one-class AUC), never a
  `ZeroDivisionError`.
- `k_fold_indices(n, k, seed=7)` — the same construction as the cross-validation
  lab: shuffle, then fold `i` is `order[i::k]`; both index lists sorted.
- `cross_val_score(X, y, config, k=4, seed=7)` — mean held-out **accuracy**.
  A fresh `Scaler` is fitted inside every fold on that fold's training rows.
- `tune(X, y, grid, k=4, seed=7)` — `(best_config, best_score)` over a list of
  keyword dicts, earlier entries winning ties.
- `evaluate(model, X, y)` — a dict with keys `accuracy`, `precision`, `recall`,
  `f1` and `auc`, computed on already-scaled features.

## The run in `main.py`

Load, encode, split, tune on the training half only, fit the winning
configuration on all of the training rows, and report the metrics on the test
rows that no fitting step has ever seen. Print the majority-class baseline
alongside, because a number without its baseline is not a result.
''',
        "deliverables": [
            "`pipeline.py` — loading, encoding, splitting, scaling, the model, the metrics and the tuner, importable with no side effects",
            "`main.py` — one reproducible run: split, tune, fit, evaluate, report against the baseline",
            "Median imputation for the missing incomes and a baseline-coded one-hot for `region`",
            "A `Scaler` fitted on training rows only, inside each cross-validation fold as well as for the final fit",
            "Held-out precision, recall, F1 and ROC-AUC alongside accuracy and the majority-class baseline",
            "Deterministic behaviour: the same seed reproduces the same split, the same folds and the same metrics",
        ],
        "constraints": [
            "Standard library only — `math` and `random` are all this needs",
            "`pipeline.py` must define functions and classes only; importing it must print nothing",
            "`data.py` is read-only; treat `RAW_CSV` as a file you were handed",
            "No statistic computed from the test rows may reach any fitting step",
            "Every random draw goes through a seeded `random.Random`, never the module-level functions",
        ],
        "rubric": [
            {"criterion": "Correctness of the pipeline", "weight": 35,
             "evidence": "All automated checks pass, including the imputation, the encoding and the degenerate metric cases."},
            {"criterion": "Leakage control", "weight": 25,
             "evidence": "Scaling statistics come from training rows only, both for the final fit and inside every cross-validation fold."},
            {"criterion": "Honest evaluation", "weight": 20,
             "evidence": "Held-out accuracy beats the majority baseline, and precision, recall, F1 and AUC are reported beside it."},
            {"criterion": "Reproducibility", "weight": 10,
             "evidence": "Seeded splits and folds; two runs of main.py produce identical numbers."},
            {"criterion": "Readability", "weight": 10,
             "evidence": "Small documented functions, no duplicated metric arithmetic, no dead code or debug prints."},
        ],
        "hints": [
            "Do the imputation in `to_features`: collect the incomes that parse, take their `median`, then build the rows in a second pass. Computing it inside the loop would use a different median for every row.",
            "One-hot with a baseline: three regions become two columns. `east` is all zeros, and the intercept absorbs it — encoding all three columns makes `X^T X` singular.",
            "`cross_val_score` must build a new `Scaler` inside the fold loop. Scaling once outside it leaks the held-out rows' means into training and quietly inflates every score.",
            "Keep `w[0]` as the intercept and store the slopes in `w[1:]`. The gradient of the L2 term is `l2 * w[j] / n` for `j >= 1` only.",
        ],
        "files": [
            {"name": "data.py", "ro": True, "content": r'''
"""The dataset you were handed. Treat RAW_CSV as a file that arrived by email."""

import math
import random

_REGIONS = ["north", "south", "east"]
_REGION_EFFECT = {"north": 0.0, "south": 1.1, "east": -1.1}


def _build():
    rng = random.Random(20260828)
    rows = []
    for _ in range(200):
        age = rng.randrange(21, 66)
        income = round(rng.uniform(18000, 95000), -2)
        years = rng.randrange(0, 31)
        region = _REGIONS[rng.randrange(3)]
        z = (-0.35
             + 0.045 * (age - 43)
             - 0.000075 * (income - 56500)
             - 0.16 * (years - 15)
             + _REGION_EFFECT[region])
        label = 1 if rng.random() < 1.0 / (1.0 + math.exp(-z)) else 0
        rows.append([str(age), str(int(income)), str(years), region, str(label)])
    for index in (11, 47, 83, 128, 176):
        rows[index][1] = ""
    header = "age,income,years_employed,region,defaulted"
    return header + "\n" + "\n".join(",".join(row) for row in rows) + "\n"


RAW_CSV = _build()
'''},
            {"name": "pipeline.py", "content": r'''
import math
import random

REGIONS = ("east", "north", "south")


def load_csv(text):
    """(header, rows) from CSV text; blank lines are skipped."""
    # your code here


def median(values):
    """Middle value, or the mean of the middle two."""
    # your code here


def to_features(header, rows):
    """(X, y) with median-imputed income and east-baseline one-hot regions."""
    # your code here


def train_test_split(X, y, test_size=0.3, seed=7):
    """(X_train, y_train, X_test, y_test) from a seeded shuffle."""
    # your code here


class Scaler:
    def fit(self, X):
        """Record column means and population standard deviations."""
        # your code here

    def transform(self, X):
        """Apply the recorded statistics."""
        # your code here


def sigmoid(z):
    """Overflow-safe logistic function."""
    # your code here


class LogisticModel:
    def __init__(self, lr=0.8, epochs=250, l2=0.0):
        self.lr = lr
        self.epochs = epochs
        self.l2 = l2
        self.w = None

    def fit(self, X, y):
        """Batch gradient descent; w[0] is the unpenalised intercept."""
        # your code here

    def predict_proba(self, X):
        """P(default) per row."""
        # your code here

    def predict(self, X, threshold=0.5):
        """Hard 0/1 predictions."""
        # your code here


def confusion_matrix(y_true, y_pred):
    """(tp, fp, fn, tn)."""
    # your code here


def accuracy(y_true, y_pred):
    """Fraction correct."""
    # your code here


def precision(y_true, y_pred):
    """tp / (tp + fp), or 0.0."""
    # your code here


def recall(y_true, y_pred):
    """tp / (tp + fn), or 0.0."""
    # your code here


def f1_score(y_true, y_pred):
    """Harmonic mean of precision and recall, or 0.0."""
    # your code here


def roc_auc(y_true, scores):
    """Pairwise ranking estimate; 0.5 when only one class is present."""
    # your code here


def k_fold_indices(n, k, seed=7):
    """[(train_indices, test_indices)] with fold i = shuffled[i::k]."""
    # your code here


def cross_val_score(X, y, config, k=4, seed=7):
    """Mean held-out accuracy, scaling inside each fold."""
    # your code here


def tune(X, y, grid, k=4, seed=7):
    """(best_config, best_score) over a list of keyword dicts."""
    # your code here


def evaluate(model, X, y):
    """Metric dict for already-scaled features."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from data import RAW_CSV
from pipeline import (load_csv, to_features, train_test_split, Scaler,
                      LogisticModel, tune, evaluate)

GRID = [
    {"lr": 0.8, "epochs": 250, "l2": 0.0},
    {"lr": 0.8, "epochs": 250, "l2": 1.0},
    {"lr": 0.8, "epochs": 250, "l2": 10.0},
]

header, rows = load_csv(RAW_CSV)
X, y = to_features(header, rows)
print("rows:", len(X), "features:", len(X[0]) if X else 0)
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "pipeline.py", "content": r'''
import math
import random

REGIONS = ("east", "north", "south")


def load_csv(text):
    """(header, rows) from CSV text; blank lines are skipped."""
    lines = [line for line in text.replace("\r\n", "\n").split("\n") if line.strip()]
    if not lines:
        raise ValueError("no data in the CSV text")
    header = [name.strip() for name in lines[0].split(",")]
    rows = [[field.strip() for field in line.split(",")] for line in lines[1:]]
    return header, rows


def median(values):
    """Middle value, or the mean of the middle two."""
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        raise ValueError("median of an empty sequence")
    middle = n // 2
    if n % 2:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def to_features(header, rows):
    """(X, y) with median-imputed income and east-baseline one-hot regions."""
    column = {name: index for index, name in enumerate(header)}
    known = [float(row[column["income"]]) for row in rows if row[column["income"]]]
    fallback = median(known)
    X, y = [], []
    for row in rows:
        raw_income = row[column["income"]]
        income = float(raw_income) if raw_income else fallback
        region = row[column["region"]].lower()
        X.append([
            float(row[column["age"]]),
            income,
            float(row[column["years_employed"]]),
            1.0 if region == "north" else 0.0,
            1.0 if region == "south" else 0.0,
        ])
        y.append(int(row[column["defaulted"]]))
    return X, y


def train_test_split(X, y, test_size=0.3, seed=7):
    """(X_train, y_train, X_test, y_test) from a seeded shuffle."""
    if len(X) != len(y):
        raise ValueError("X and y disagree on the number of rows")
    n = len(y)
    order = list(range(n))
    random.Random(seed).shuffle(order)
    cut = int(round(n * (1.0 - test_size)))
    train = sorted(order[:cut])
    test = sorted(order[cut:])
    return ([X[i] for i in train], [y[i] for i in train],
            [X[i] for i in test], [y[i] for i in test])


class Scaler:
    """Column-wise standardisation with statistics learned from one set of rows."""

    def fit(self, X):
        """Record column means and population standard deviations."""
        if not X:
            raise ValueError("nothing to fit")
        columns = list(zip(*X))
        self.means = [sum(col) / len(col) for col in columns]
        self.stds = []
        for col, mean in zip(columns, self.means):
            spread = math.sqrt(sum((v - mean) ** 2 for v in col) / len(col))
            self.stds.append(spread if spread > 1e-12 else 1.0)
        return self

    def transform(self, X):
        """Apply the recorded statistics."""
        return [[(v - m) / s for v, m, s in zip(row, self.means, self.stds)] for row in X]


def sigmoid(z):
    """Overflow-safe logistic function."""
    if z >= 0.0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


class LogisticModel:
    """Binary logistic regression trained by batch gradient descent."""

    def __init__(self, lr=0.8, epochs=250, l2=0.0):
        self.lr = lr
        self.epochs = epochs
        self.l2 = l2
        self.w = None

    def _score(self, row):
        return self.w[0] + sum(wj * xj for wj, xj in zip(self.w[1:], row))

    def fit(self, X, y):
        """Batch gradient descent; w[0] is the unpenalised intercept."""
        if len(X) != len(y):
            raise ValueError("X and y disagree on the number of rows")
        n = len(X)
        d = len(X[0]) + 1
        self.w = [0.0] * d
        for _ in range(self.epochs):
            residual = [sigmoid(self._score(row)) - target for row, target in zip(X, y)]
            grad = [sum(residual) / n]
            for j in range(d - 1):
                g = sum(X[i][j] * residual[i] for i in range(n)) / n
                grad.append(g + self.l2 * self.w[j + 1] / n)
            self.w = [wj - self.lr * gj for wj, gj in zip(self.w, grad)]
        return self

    def predict_proba(self, X):
        """P(default) per row."""
        return [sigmoid(self._score(row)) for row in X]

    def predict(self, X, threshold=0.5):
        """Hard 0/1 predictions."""
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


def confusion_matrix(y_true, y_pred):
    """(tp, fp, fn, tn)."""
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred differ in length")
    tp = fp = fn = tn = 0
    for t, p in zip(y_true, y_pred):
        if t == 1 and p == 1:
            tp += 1
        elif t == 0 and p == 1:
            fp += 1
        elif t == 1 and p == 0:
            fn += 1
        else:
            tn += 1
    return tp, fp, fn, tn


def accuracy(y_true, y_pred):
    """Fraction correct."""
    if not y_true:
        return 0.0
    return sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)


def precision(y_true, y_pred):
    """tp / (tp + fp), or 0.0."""
    tp, fp, _, _ = confusion_matrix(y_true, y_pred)
    return tp / (tp + fp) if tp + fp else 0.0


def recall(y_true, y_pred):
    """tp / (tp + fn), or 0.0."""
    tp, _, fn, _ = confusion_matrix(y_true, y_pred)
    return tp / (tp + fn) if tp + fn else 0.0


def f1_score(y_true, y_pred):
    """Harmonic mean of precision and recall, or 0.0."""
    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    return 2.0 * p * r / (p + r) if p + r else 0.0


def roc_auc(y_true, scores):
    """Pairwise ranking estimate; 0.5 when only one class is present."""
    if len(y_true) != len(scores):
        raise ValueError("y_true and scores differ in length")
    positives = [s for s, t in zip(scores, y_true) if t == 1]
    negatives = [s for s, t in zip(scores, y_true) if t == 0]
    if not positives or not negatives:
        return 0.5
    wins = 0.0
    for p in positives:
        for q in negatives:
            if p > q:
                wins += 1.0
            elif p == q:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


def k_fold_indices(n, k, seed=7):
    """[(train_indices, test_indices)] with fold i = shuffled[i::k]."""
    if k < 2 or k > n:
        raise ValueError("k must be between 2 and n")
    order = list(range(n))
    random.Random(seed).shuffle(order)
    folds = [order[i::k] for i in range(k)]
    splits = []
    for i in range(k):
        test = sorted(folds[i])
        train = sorted(index for f in range(k) if f != i for index in folds[f])
        splits.append((train, test))
    return splits


def cross_val_score(X, y, config, k=4, seed=7):
    """Mean held-out accuracy, scaling inside each fold."""
    splits = k_fold_indices(len(y), k, seed)
    total = 0.0
    for train, test in splits:
        scaler = Scaler().fit([X[i] for i in train])
        model = LogisticModel(**config).fit(scaler.transform([X[i] for i in train]),
                                            [y[i] for i in train])
        predicted = model.predict(scaler.transform([X[i] for i in test]))
        total += accuracy([y[i] for i in test], predicted)
    return total / len(splits)


def tune(X, y, grid, k=4, seed=7):
    """(best_config, best_score) over a list of keyword dicts."""
    best_config, best_score = None, None
    for config in grid:
        score = cross_val_score(X, y, config, k, seed)
        if best_score is None or score > best_score + 1e-15:
            best_config, best_score = config, score
    return best_config, best_score


def evaluate(model, X, y):
    """Metric dict for already-scaled features."""
    predicted = model.predict(X)
    return {
        "accuracy": accuracy(y, predicted),
        "precision": precision(y, predicted),
        "recall": recall(y, predicted),
        "f1": f1_score(y, predicted),
        "auc": roc_auc(y, model.predict_proba(X)),
    }
'''},
            {"name": "main.py", "content": r'''
from data import RAW_CSV
from pipeline import (load_csv, to_features, train_test_split, Scaler,
                      LogisticModel, tune, evaluate)

GRID = [
    {"lr": 0.8, "epochs": 250, "l2": 0.0},
    {"lr": 0.8, "epochs": 250, "l2": 1.0},
    {"lr": 0.8, "epochs": 250, "l2": 10.0},
]

header, rows = load_csv(RAW_CSV)
X, y = to_features(header, rows)
X_train, y_train, X_test, y_test = train_test_split(X, y, 0.3, 7)

best_config, best_score = tune(X_train, y_train, GRID)

scaler = Scaler().fit(X_train)
model = LogisticModel(**best_config).fit(scaler.transform(X_train), y_train)
report = evaluate(model, scaler.transform(X_test), y_test)

positives = sum(y_test)
baseline = max(positives, len(y_test) - positives) / len(y_test)

print("rows:", len(X), "features:", len(X[0]))
print("train / test:", len(y_train), "/", len(y_test))
print("chosen config:", best_config, "cv accuracy:", round(best_score, 4))
print("majority baseline:", round(baseline, 4))
for name in ("accuracy", "precision", "recall", "f1", "auc"):
    print(f"  {name:<10}{report[name]:.4f}")
'''},
        ],
        "tests": [
            {"name": "The CSV loads with its header and 200 rows", "code": r'''
from data import RAW_CSV
from pipeline import load_csv
_header, _rows = load_csv(RAW_CSV)
assert _header == ["age", "income", "years_employed", "region", "defaulted"], \
    f"header came back as {_header!r}"
assert len(_rows) == 200, f"Expected 200 data rows, got {len(_rows)}"
assert all(len(r) == 5 for r in _rows), "Every row should split into five fields"
_blank = [i for i, r in enumerate(_rows) if r[1] == ""]
assert len(_blank) == 5, f"Five income cells are blank in this file, found {len(_blank)}"
assert load_csv("a,b\n\n1,2\n")[1] == [["1", "2"]], "Blank lines must be skipped"
'''},
            {"name": "median handles odd and even counts", "code": r'''
from pipeline import median
assert median([3, 1, 2]) == 2, f"median([3,1,2]) gave {median([3, 1, 2])!r}, expected 2"
assert median([4, 1, 3, 2]) == 2.5, f"median([4,1,3,2]) gave {median([4, 1, 3, 2])!r}, expected 2.5"
assert median([7]) == 7, f"median([7]) gave {median([7])!r}"
assert median([2, 1]) == 1.5, f"median([2,1]) gave {median([2, 1])!r}, expected 1.5"
'''},
            {"name": "Encoding imputes income and codes region against a baseline", "code": r'''
from data import RAW_CSV
from pipeline import load_csv, to_features, median
_header, _rows = load_csv(RAW_CSV)
_X, _y = to_features(_header, _rows)
assert len(_X) == 200 and len(_y) == 200, f"Expected 200 rows, got {len(_X)} and {len(_y)}"
assert all(len(row) == 5 for row in _X), \
    f"Each row is age, income, years, is_north, is_south — got widths {sorted({len(r) for r in _X})!r}"
assert set(_y) == {0, 1}, f"The target should be 0/1, got {sorted(set(_y))!r}"
assert sum(_y) == 81, f"This file holds 81 defaults, got {sum(_y)}"
_known = [float(r[1]) for r in _rows if r[1]]
_want = median(_known)
for _i, _r in enumerate(_rows):
    if _r[1] == "":
        assert abs(_X[_i][1] - _want) < 1e-9, \
            f"Row {_i} has no income and should take the median {_want!r}, got {_X[_i][1]!r}"
for _i, _r in enumerate(_rows):
    _flags = (_X[_i][3], _X[_i][4])
    if _r[3] == "east":
        assert _flags == (0.0, 0.0), f"east is the baseline and encodes as (0, 0), got {_flags!r}"
    elif _r[3] == "north":
        assert _flags == (1.0, 0.0), f"north should encode as (1, 0), got {_flags!r}"
    else:
        assert _flags == (0.0, 1.0), f"south should encode as (0, 1), got {_flags!r}"
'''},
            {"name": "The split is disjoint, complete and reproducible", "code": r'''
from data import RAW_CSV
from pipeline import load_csv, to_features, train_test_split
_header, _rows = load_csv(RAW_CSV)
_X, _y = to_features(_header, _rows)
_Xtr, _ytr, _Xte, _yte = train_test_split(_X, _y, 0.3, 7)
assert len(_ytr) == 140, f"70% of 200 rows is 140 training rows, got {len(_ytr)}"
assert len(_yte) == 60, f"and 60 test rows, got {len(_yte)}"
assert len(_Xtr) == len(_ytr) and len(_Xte) == len(_yte), "Features and labels must stay aligned"
_seen = [tuple(r) for r in _Xtr] + [tuple(r) for r in _Xte]
assert sorted(_seen) == sorted(tuple(r) for r in _X), "Every row must land in exactly one half"
assert 0.25 < sum(_yte) / len(_yte) < 0.6, \
    f"The test half should keep a similar class balance, got {sum(_yte) / len(_yte)!r}"
_again = train_test_split(_X, _y, 0.3, 7)
assert _again[1] == _ytr and _again[3] == _yte, "The same seed must give the same split"
_other = train_test_split(_X, _y, 0.3, 8)
assert _other[1] != _ytr, "A different seed should give a different split"
'''},
            {"name": "The scaler learns from one set of rows and applies to another", "code": r'''
from pipeline import Scaler
_s = Scaler().fit([[1.0, 5.0], [3.0, 5.0]])
assert _s.means == [2.0, 5.0], f"means came out {_s.means!r}, expected [2.0, 5.0]"
assert abs(_s.stds[0] - 1.0) < 1e-12, f"population std of [1, 3] is 1.0, got {_s.stds[0]!r}"
assert _s.stds[1] == 1.0, f"A constant column keeps std 1.0, got {_s.stds[1]!r}"
_z = _s.transform([[1.0, 5.0], [3.0, 5.0]])
assert abs(_z[0][0] + 1.0) < 1e-12 and abs(_z[1][0] - 1.0) < 1e-12, f"transform gave {_z!r}"
assert _z[0][1] == 0.0 and _z[1][1] == 0.0, "A constant column standardises to zeros"
_new = _s.transform([[5.0, 5.0]])
assert abs(_new[0][0] - 3.0) < 1e-12, \
    f"Unseen rows use the *training* mean and std: expected 3.0, got {_new[0][0]!r}"
'''},
            {"name": "Metrics, including the degenerate cases", "code": r'''
from pipeline import confusion_matrix, accuracy, precision, recall, f1_score, roc_auc
_t = [1, 1, 1, 0, 0, 0, 0, 1]
_p = [1, 0, 1, 0, 1, 0, 0, 1]
assert confusion_matrix(_t, _p) == (3, 1, 1, 3), \
    f"confusion_matrix gave {confusion_matrix(_t, _p)!r}, expected (3, 1, 1, 3)"
assert abs(accuracy(_t, _p) - 0.75) < 1e-12, f"accuracy gave {accuracy(_t, _p)!r}, expected 0.75"
assert abs(precision(_t, _p) - 0.75) < 1e-12, f"precision gave {precision(_t, _p)!r}, expected 0.75"
assert abs(recall(_t, _p) - 0.75) < 1e-12, f"recall gave {recall(_t, _p)!r}, expected 0.75"
assert abs(f1_score(_t, _p) - 0.75) < 1e-12, f"f1_score gave {f1_score(_t, _p)!r}, expected 0.75"
assert precision([1, 1], [0, 0]) == 0.0, "Nothing predicted positive gives precision 0.0"
assert recall([0, 0], [1, 1]) == 0.0, "No positives gives recall 0.0"
assert f1_score([0, 0], [0, 0]) == 0.0, "No positives anywhere gives F1 0.0"
assert abs(roc_auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]) - 0.75) < 1e-12, \
    f"roc_auc gave {roc_auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8])!r}, expected 0.75"
assert roc_auc([1, 1], [0.2, 0.9]) == 0.5, "One class present: AUC is undefined, return 0.5"
'''},
            {"name": "k_fold_indices reproduces the documented split", "code": r'''
from pipeline import k_fold_indices
_splits = k_fold_indices(10, 5, 7)
assert [test for _, test in _splits] == [[0, 8], [3, 9], [1, 6], [2, 4], [5, 7]], \
    f"With seed 7 the folds are [[0,8],[3,9],[1,6],[2,4],[5,7]], got {[t for _, t in _splits]!r}"
for _train, _test in _splits:
    assert sorted(_train + _test) == list(range(10)), "Each fold must cover every index once"
    assert not set(_train) & set(_test), "A row cannot be trained and tested in the same fold"
assert sorted(len(t) for _, t in k_fold_indices(17, 4, 3)) == [4, 4, 4, 5], \
    "17 rows over 4 folds gives sizes 4, 4, 4, 5"
'''},
            {"name": "The model learns the training half", "code": r'''
from data import RAW_CSV
from pipeline import load_csv, to_features, train_test_split, Scaler, LogisticModel, accuracy
_header, _rows = load_csv(RAW_CSV)
_X, _y = to_features(_header, _rows)
_Xtr, _ytr, _Xte, _yte = train_test_split(_X, _y, 0.3, 7)
_scaler = Scaler().fit(_Xtr)
_model = LogisticModel().fit(_scaler.transform(_Xtr), _ytr)
assert _model.w is not None and len(_model.w) == 6, \
    f"Five features plus an intercept is six weights, got {None if _model.w is None else len(_model.w)}"
_probs = _model.predict_proba(_scaler.transform(_Xtr))
assert all(0.0 <= p <= 1.0 for p in _probs), "Probabilities must stay inside [0, 1]"
_train_acc = accuracy(_ytr, _model.predict(_scaler.transform(_Xtr)))
assert _train_acc > 0.80, f"Training accuracy was {_train_acc!r}, expected over 0.80"
_flat = LogisticModel(lr=0.8, epochs=0).fit(_scaler.transform(_Xtr), _ytr)
assert all(w == 0.0 for w in _flat.w), "With no epochs the weights stay where they started"
'''},
            {"name": "L2 shrinks the slopes and leaves the intercept alone", "code": r'''
from data import RAW_CSV
from pipeline import load_csv, to_features, train_test_split, Scaler, LogisticModel
_header, _rows = load_csv(RAW_CSV)
_X, _y = to_features(_header, _rows)
_Xtr, _ytr, _, _ = train_test_split(_X, _y, 0.3, 7)
_Z = Scaler().fit(_Xtr).transform(_Xtr)
_plain = LogisticModel(0.8, 250, 0.0).fit(_Z, _ytr)
_ridged = LogisticModel(0.8, 250, 200.0).fit(_Z, _ytr)
_np = sum(v * v for v in _plain.w[1:]) ** 0.5
_nr = sum(v * v for v in _ridged.w[1:]) ** 0.5
assert _nr < _np, f"The penalised slopes should be smaller: {_nr!r} against {_np!r}"
assert _nr > 0.0, "Shrinkage pulls towards zero without reaching it"
'''},
            {"name": "Cross-validation and tuning agree with each other", "code": r'''
from data import RAW_CSV
from pipeline import load_csv, to_features, train_test_split, cross_val_score, tune
_header, _rows = load_csv(RAW_CSV)
_X, _y = to_features(_header, _rows)
_Xtr, _ytr, _, _ = train_test_split(_X, _y, 0.3, 7)
_grid = [{"lr": 0.8, "epochs": 250, "l2": 0.0},
         {"lr": 0.8, "epochs": 250, "l2": 1.0},
         {"lr": 0.8, "epochs": 250, "l2": 10.0}]
_scores = [cross_val_score(_Xtr, _ytr, c) for c in _grid]
assert all(0.0 <= s <= 1.0 for s in _scores), f"Accuracies must lie in [0, 1], got {_scores!r}"
assert max(_scores) > 0.72, f"Cross-validated accuracy should clear 0.72, best was {max(_scores)!r}"
_best_config, _best_score = tune(_Xtr, _ytr, _grid)
assert _best_config in _grid, f"tune must return one of the grid entries, got {_best_config!r}"
assert abs(_best_score - max(_scores)) < 1e-12, \
    f"tune reported {_best_score!r} but the best cross_val_score is {max(_scores)!r}"
_untrained = cross_val_score(_Xtr, _ytr, {"lr": 0.8, "epochs": 0, "l2": 0.0})
assert _best_score > _untrained, \
    f"A trained model must beat the zero-epoch model: {_best_score!r} against {_untrained!r}"
'''},
            {"name": "The held-out numbers beat the baseline", "code": r'''
from data import RAW_CSV
from pipeline import (load_csv, to_features, train_test_split, Scaler,
                      LogisticModel, tune, evaluate)
_header, _rows = load_csv(RAW_CSV)
_X, _y = to_features(_header, _rows)
_Xtr, _ytr, _Xte, _yte = train_test_split(_X, _y, 0.3, 7)
_grid = [{"lr": 0.8, "epochs": 250, "l2": 0.0},
         {"lr": 0.8, "epochs": 250, "l2": 1.0}]
_config, _ = tune(_Xtr, _ytr, _grid)
_scaler = Scaler().fit(_Xtr)
_model = LogisticModel(**_config).fit(_scaler.transform(_Xtr), _ytr)
_report = evaluate(_model, _scaler.transform(_Xte), _yte)
for _key in ("accuracy", "precision", "recall", "f1", "auc"):
    assert _key in _report, f"evaluate() should report {_key!r}; got keys {sorted(_report)!r}"
_baseline = max(sum(_yte), len(_yte) - sum(_yte)) / len(_yte)
assert _report["accuracy"] > _baseline, \
    f"Held-out accuracy {_report['accuracy']!r} must beat the majority baseline {_baseline!r}"
assert _report["accuracy"] >= 0.70, f"Held-out accuracy was {_report['accuracy']!r}, expected at least 0.70"
assert _report["auc"] >= 0.80, f"Held-out ROC-AUC was {_report['auc']!r}, expected at least 0.80"
assert 0.0 < _report["f1"] <= 1.0, f"F1 came out {_report['f1']!r}"
_repeat = evaluate(_model, _scaler.transform(_Xte), _yte)
assert _repeat == _report, "Evaluation must be deterministic"
'''},
            {"name": "Scaling statistics never come from the test rows", "code": r'''
from data import RAW_CSV
from pipeline import load_csv, to_features, train_test_split, Scaler
_header, _rows = load_csv(RAW_CSV)
_X, _y = to_features(_header, _rows)
_Xtr, _ytr, _Xte, _yte = train_test_split(_X, _y, 0.3, 7)
_scaler = Scaler().fit(_Xtr)
_train_means = [sum(col) / len(col) for col in zip(*_Xtr)]
for _got, _want in zip(_scaler.means, _train_means):
    assert abs(_got - _want) < 1e-9, \
        f"The scaler means are {_scaler.means!r}, but the training means are {_train_means!r}"
_all_means = [sum(col) / len(col) for col in zip(*_X)]
assert any(abs(a - b) > 1e-9 for a, b in zip(_train_means, _all_means)), \
    "The training and full-dataset means differ here, which is exactly why fitting on all rows leaks"
_src = open("pipeline.py").read()
assert "print(" not in _src, "pipeline.py defines the logic; the printing belongs in main.py"
'''},
        ],
    },
}
