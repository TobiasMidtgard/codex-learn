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
            "read": [
                {
                    "title": "One fit, found two ways",
                    "minutes": 12,
                    "body": r'''
Three readings from a thermometer taped to a kettle, taken a minute apart as it warms: 1 degree above the starting temperature after one minute, 2 after two, and 2 again after three, because the sensor reports whole degrees only. You want the straight line $y = w_0 + w_1 x$ that describes the warming, and there is no such line: any line through the first two points passes through 3 at minute three, not 2. So the question is not which line fits, but which line fits *least badly*, and that needs a number for badly.

Draw the three points and any candidate line, and drop a vertical segment from each point to the line. Those segments are the residuals, $r_i = (w_0 + w_1 x_i) - y_i$, positive above a point and negative below. Adding them is useless, because a line far above one point and far below another has residuals that cancel and looks perfect. Absolute values are honest but leave a kink at zero that no derivative can get through. Squares have neither problem: every miss counts, a miss of 2 counts four times as much as a miss of 1, and the result is a smooth bowl in $w$. Divide by the number of points and you have the mean squared error:

$$J(w) = \frac{1}{n}\sum_{i=1}^{n}\left(x_i \cdot w - y_i\right)^2$$

Here $x_i$ is the $i$th row of the design matrix $X$ with a $1$ prepended, so that $x_i \cdot w = w_0 + w_1 x_{i1} + \dots$ and the intercept is a weight like every other; that column is what `add_bias` builds. Leave it out and the model is $y = w_1 x$, a line nailed to the origin, and no amount of fitting will move it off.

## The gradient, and what setting it to zero buys

$J$ is a sum of squares of things that are linear in $w$, so its derivative with respect to any one weight $w_j$ comes from the chain rule: bring the 2 down, keep the inside, multiply by the inside's derivative, which is $x_{ij}$.

$$\frac{\partial J}{\partial w_j} = \frac{2}{n}\sum_{i=1}^{n}\left(x_i \cdot w - y_i\right)x_{ij}$$

Stacked into a vector, the sum over $i$ is a matrix product: $\nabla J = \frac{2}{n}X^T(Xw - y)$. The $2$ is not decoration. It came out of the square, and every learning-rate limit later in this reading is stated for a gradient that keeps it. Drop it and your descent takes steps half as long as you think.

The bottom of a bowl is where the slope is zero in every direction, so the best $w$ satisfies $\frac{2}{n}X^T(Xw - y) = 0$. Multiply out, move the $y$ term across, and the constant falls away:

$$X^T X\, w = X^T y$$

That is the normal equation, and it was not announced; it is the statement that the gradient of the mean squared error vanishes. Read it a second way, $X^T(Xw - y) = 0$, and it says the residual is perpendicular to every column of $X$: the fitted values $Xw$ are the shadow $y$ casts on the space the columns span, and the residual is the part no combination of columns can reach. That is the projection in the concept list, and it gives a hand check: the residuals of a correct fit sum to zero, because the column of ones is one of the columns.

## Working it through on the kettle

With $x = 1, 2, 3$ and $y = 1, 2, 2$, the design matrix and its products are

$$X = \begin{pmatrix}1 & 1\\ 1 & 2\\ 1 & 3\end{pmatrix},\qquad X^T X = \begin{pmatrix}3 & 6\\ 6 & 14\end{pmatrix},\qquad X^T y = \begin{pmatrix}5\\ 11\end{pmatrix}$$

In $X^T X$ the top-left entry counts the rows, the off-diagonal is the sum of the $x$ values and the bottom-right the sum of their squares; $X^T y$ holds the sums of $y$ and of $xy$. Two equations, two unknowns: $3w_0 + 6w_1 = 5$ and $6w_0 + 14w_1 = 11$. Gauss-Jordan elimination does what you would do on paper, on an augmented matrix $[A | b]$, and this version prints its state after each column:

```python
def solve_linear_system(A, b):
    n = len(A)
    M = [list(map(float, row)) + [float(b[i])] for i, row in enumerate(A)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-12:
            raise ValueError("matrix is singular to working precision")
        M[col], M[pivot] = M[pivot], M[col]
        scale = M[col][col]
        M[col] = [v / scale for v in M[col]]
        for r in range(n):
            if r != col:
                factor = M[r][col]
                M[r] = [a - factor * p for a, p in zip(M[r], M[col])]
        print(f"after column {col}:", [[round(v, 4) for v in row] for row in M])
    return [row[n] for row in M]

print("w =", [round(v, 4) for v in solve_linear_system([[3, 6], [6, 14]], [5, 11])])
```

The largest entry in column 0 is the 6 in the second row, not the 3 in the first, so the rows are swapped before anything is divided: that is partial pivoting. On the lab's test `[[0, 1], [1, 0]]` it is the difference between an answer and a division by zero, because the entry the naive algorithm would divide by is exactly $0$, and a zero there does not mean the system is singular; it means the rows are in an unhelpful order. A tiny pivot amplifies every rounding error beneath it, and taking the largest available one keeps the multipliers at most $1$ in size.

The answer is $w_0 = 2/3$ and $w_1 = 1/2$: the line $y = 0.667 + 0.5x$. Its predictions at $x = 1, 2, 3$ are $1.167, 1.667, 2.167$, the residuals are $0.167, -0.333, 0.167$, they sum to zero as promised, and the mean squared error is $(0.0278 + 0.1111 + 0.0278)/3 = 0.0556$.

## When the pivot is not there

Elimination fails in one way that is not a bug. If a feature is an exact multiple of another, the columns of $X^T X$ built from the pair are the same multiple of each other, the first sweep wipes out the second row, and the pivot search then finds nothing above $10^{-12}$:

```python
# raises ValueError
# x2 is exactly twice x1, so the second column of X^T X is twice the first
A = [[5.0, 10.0], [10.0, 20.0]]
for col in range(2):
    pivot = max(range(col, 2), key=lambda r: abs(A[r][col]))
    if abs(A[pivot][col]) < 1e-12:
        raise ValueError(f"column {col}: nothing above 1e-12 to pivot on")
    A[col], A[pivot] = A[pivot], A[col]
    A[col] = [v / A[col][col] for v in A[col]]
    for r in range(2):
        if r != col:
            A[r] = [a - A[r][col] * p for a, p in zip(A[r], A[col])]
    print(f"after column {col}:", A)
```

The `ValueError` is right, because the question has no single answer: if $x_2 = 2x_1$ then $w_1 x_1 + w_2 x_2 = (w_1 + 2w_2)x_1$, and every pair of weights with the same $w_1 + 2w_2$ fits identically. The threshold is a judgement. Columns that are nearly proportional give a pivot of $10^{-9}$ rather than $0$, elimination goes through, and the weights come back enormous and opposite in sign; module 5 returns to that case.

Cost is the other limit. Forming $X^T X$ is $O(nd^2)$ and eliminating a $d \times d$ system is $O(d^3)$: nothing for $d$ in the hundreds, out of reach for $d$ in the hundreds of thousands, where one step of the method below costs $O(nd)$ instead.

## The same answer by walking downhill

Gradient descent never sets the gradient to zero. It points uphill, so step the other way, scaled by a learning rate $\eta$:

$$w \leftarrow w - \eta\,\nabla J(w)$$

Start the kettle problem from $w = (0, 0)$. The predictions are all $0$, the residuals are $-1, -2, -2$, and the mean squared error is $(1 + 4 + 4)/3 = 3$. The gradient is $\frac{2}{3}X^T r = \frac{2}{3}(-5, -11) = (-3.333, -7.333)$, so with $\eta = 0.1$ the first step lands on $w = (0.333, 0.733)$. The lab records the error *before* each update, which is why `history[0]` is the error of the zero model and `history` has exactly `epochs` entries:

```python
def gradient_descent(X, y, lr, epochs):
    n, d = len(X), len(X[0])
    w = [0.0] * d
    history = []
    for _ in range(epochs):
        residual = [sum(wj * xj for wj, xj in zip(w, row)) - t for row, t in zip(X, y)]
        history.append(sum(r * r for r in residual) / n)
        grad = [(2.0 / n) * sum(X[i][j] * residual[i] for i in range(n)) for j in range(d)]
        w = [wj - lr * gj for wj, gj in zip(w, grad)]
    return w, history

X = [[1.0, 1.0], [1.0, 2.0], [1.0, 3.0]]
y = [1.0, 2.0, 2.0]
w, history = gradient_descent(X, y, 0.1, 3)
print("MSE before each of the first three steps:", [round(h, 4) for h in history])
print("weights after three steps:", [round(v, 4) for v in w])
w, history = gradient_descent(X, y, 0.1, 2000)
print("after 2000 steps:", [round(v, 6) for v in w], "MSE", round(history[-1], 9))
```

Two thousand steps later the weights are $0.666667$ and $0.5$ and the error is $0.0555556$: the numbers elimination produced in two column sweeps. That agreement is the lab's central check; the closed form is the answer, and descent is a slower road to the same place.

## Why the raw features blow up

The lab's data set has $x_1$ in $[0, 10]$ and $x_2$ in $[-5, 5]$, and at $\eta = 0.1$ descent on those columns explodes. To see why, look at one direction of the bowl at a time. Along a direction in which $J$ has curvature $\lambda$, the error is $J = \frac{\lambda}{2}(w - w^*)^2$ with gradient $\lambda(w - w^*)$, and one step gives

$$w - w^* \leftarrow (1 - \eta\lambda)(w - w^*)$$

The distance to the optimum is multiplied by $(1 - \eta\lambda)$ every step, which shrinks only when $|1 - \eta\lambda| < 1$, that is, when $\eta < 2/\lambda$. The curvatures are the eigenvalues of the Hessian $\frac{2}{n}X^T X$: the largest sets the ceiling on $\eta$, the smallest sets how slowly the flattest direction is crossed, and their ratio is the condition number.

On the raw lab data the diagonal of $\frac{2}{n}X^T X$ is about $2$ for the column of ones, $60$ for $x_1$ and $15$ for $x_2$, and the largest eigenvalue is $61.9$. The ceiling is $2/61.9 = 0.032$, and $\eta = 0.1$ is three times over it: along the $x_1$ direction each step multiplies the error by $1 - 6.19 = -5.19$. Standardising each column, subtracting its mean and dividing by its spread, makes every diagonal entry $2$ and the largest eigenvalue $2.10$, so the ceiling becomes $0.95$. The block runs both, then runs the standardised problem at four rates, printing only the intercept weight, whose direction has curvature exactly $2$ once the other columns are centred:

```python
import math
import random

def make_dataset(n=60, seed=7):
    rng = random.Random(seed)
    X = [[rng.uniform(0, 10), rng.uniform(-5, 5)] for _ in range(n)]
    return X, [3.0 + 2.0 * a - 1.0 * b for a, b in X]

def standardise(X):
    cols = list(zip(*X))
    means = [sum(c) / len(c) for c in cols]
    stds = [math.sqrt(sum((v - m) ** 2 for v in c) / len(c)) or 1.0 for c, m in zip(cols, means)]
    return [[(v - m) / s for v, m, s in zip(row, means, stds)] for row in X]

def gradient_descent(X, y, lr, epochs):
    X = [[1.0] + list(row) for row in X]
    n, d = len(X), len(X[0])
    w = [0.0] * d
    history, intercepts = [], []
    for _ in range(epochs):
        residual = [sum(wj * xj for wj, xj in zip(w, row)) - t for row, t in zip(X, y)]
        history.append(sum(r * r for r in residual) / n)
        grad = [(2.0 / n) * sum(X[i][j] * residual[i] for i in range(n)) for j in range(d)]
        w = [wj - lr * gj for wj, gj in zip(w, grad)]
        intercepts.append(round(w[0], 2))
    return history, intercepts

X, y = make_dataset()
Z = standardise(X)
print("raw, lr=0.1:            ", [f"{h:.3g}" for h in gradient_descent(X, y, 0.1, 6)[0]])
print("standardised, lr=0.1:   ", [f"{h:.3g}" for h in gradient_descent(Z, y, 0.1, 6)[0]])
print("standardised, epoch 500:", f"{gradient_descent(Z, y, 0.1, 500)[0][-1]:.3g}")
print("target intercept, the mean of y:", round(sum(y) / len(y), 2))
for lr in (0.01, 0.1, 0.9, 1.05):
    print(f"intercept at lr={lr:<5}", gradient_descent(Z, y, lr, 8)[1])
```

Same data, same rate, same code, and the raw trace multiplies by about $27$ every step while the standardised one reaches $10^{-29}$. The lab's `standardise` uses the population standard deviation, dividing by $n$, and keeps a constant column at spread $1.0$ rather than $0$, because dividing by a zero spread produces `nan`, and one `nan` poisons every product made from it afterwards.

## Three ways a learning rate fails

The factor $(1 - \eta\lambda)$ tells you what a bad rate looks like before you see it, and the four intercept traces show each case. At $\eta = 0.01$ the factor is $0.98$: after eight steps the intercept has crawled to $1.84$ of its $12.32$, and it needs a couple of hundred more. At $0.1$ the factor is $0.8$ and the approach is steady. At $0.9$ it is $-0.8$: the intercept leaps to $22$, drops to $4$, rises to $19$, and the swings shrink by a fifth each time, so it converges, slowly and by oscillation. At $1.05$ the factor is $-1.1$, the sign still flips, and the swings grow without bound. Those are three different numbers, and a printed `history` tells them apart in its first ten entries. It is the cheapest diagnostic in the course.

## The mistake, and where the idea stops

The mistake is to see an error of $10^{9}$ after six epochs and go looking for a bug in `matvec`. It is tempting because a number that large looks like nonsense, and nonsense usually means a wrong index. But the products are fine; the step is too long for the curvature, and either the rate or the scaling has to change. The tell is the shape of the trace: a bug produces wrong numbers, a bad rate produces numbers that grow by the same factor each step.

Monotone descent needs $\eta < 2/\lambda_{\max}$, and it needs $J$ to be a bowl, which it is here because the model is linear in $w$; the logistic loss in the next module is still convex but has no closed form, so descent is the only road. The normal equation needs $X^T X$ invertible, which a duplicated column, or a constant feature sitting beside the bias column, denies it. And the lab's data is noiseless, which is why both methods can be checked to machine precision; on real data the error floors at the noise, and $10^{-29}$ would mean something had gone wrong.

In the lab, *Normal equation versus gradient descent*, you will build the three products, the pivoting solver, `standardise` and `gradient_descent` with its history, and see the two methods meet at $[3, 2, -1]$ on standardised features while the raw features diverge at the rate this reading predicts.
''',
                },
            ],
            "quiz": {
                "title": "Two roads to one set of weights",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"The lab's `add_bias` prepends a `1.0` to every row before either fit. What does that column of ones do?",
                        "opts": [
                            r"It guarantees $X^T X$ is invertible, because a constant column can never be proportional to any of the feature columns",
                            r"It centres the features, so the intercept direction of the bowl decouples from the rest and descent converges faster",
                            r"It gives the intercept a coordinate, so $w_0$ is fitted like any other weight and the line is able to miss the origin",
                            r"It lets `standardise` skip the first column, so the intercept is never divided by a zero spread and turned to `nan`",
                        ],
                        "a": 2,
                        "whys": [
                            r"A constant column can be proportional to a feature: a feature that is itself constant makes the two columns identical and $X^T X$ singular. The ones column brings no promise about invertibility.",
                            r"Centring is what `standardise` does, and it does it to the feature columns; the ones column is never centred. The decoupling happens only after the other columns have been centred, and is a side effect, not the purpose.",
                            r"The model is $x \cdot w$, and without a coordinate that is always $1$ there is no term in it that can be a constant.",
                            r"`standardise` runs on the features before the bias is added, and its zero-spread guard is what handles a constant column. The ones column is not there to be skipped.",
                        ],
                        "why": r'''
The model is a dot product, $x \cdot w$. Every term in it is a weight times a coordinate, so the only way to get a constant term is a coordinate that is constant: the column of ones. Leave it out and the fitted line passes through the origin whatever the data says. The column brings no promise about invertibility, it is not centred, and it is added after standardisation rather than protected from it.
''',
                    },
                    {
                        "q": r"During elimination a $0$ turns up in the pivot position of a matrix that is not singular. Why is that zero not evidence of singularity?",
                        "opts": [
                            r"Rows can be reordered without changing the solution, and another row may hold a usable entry in that column",
                            r"Singularity is decided by the determinant, which elimination never computes, so no single entry can show it",
                            r"The zero is a rounding artefact, and scaling that row by a large enough constant restores a usable pivot",
                            r"It is evidence: a zero on the diagonal means the column carries no information, and `ValueError` is the right response",
                        ],
                        "a": 0,
                        "whys": [
                            r"Swapping two equations changes nothing about their solution, and the lab's test `[[0, 1], [1, 0]]` has a perfectly good $1$ waiting in the row below.",
                            r"Elimination is one of the standard ways of computing a determinant, since the product of the pivots is the determinant up to sign. And the determinant of `[[0, 1], [1, 0]]` is $-1$, not $0$: the matrix is not singular, whatever the diagonal shows.",
                            r"Scaling a row scales every entry in it, including the zero, which stays zero. Rounding is not the issue when the entry is exactly $0$; the row order is.",
                            r"A zero on the diagonal says nothing about the column, which may be full of useful entries in other rows. Singularity is the case where the whole remainder of the column is zero, and that is what the pivot search, taken over every row below, actually tests.",
                        ],
                        "why": r'''
The solution of a linear system does not depend on the order the equations are written in, so a zero in the pivot position can be swapped away whenever some lower row has a nonzero entry in that column. Partial pivoting always picks the largest such entry, which handles the exact zero and also keeps rounding error from being amplified by a tiny divisor. Only when every remaining entry in the column is below the threshold is the matrix singular to working precision, and only then does the lab's solver raise.
''',
                    },
                    {
                        "q": r"With `lr=0.1`, gradient descent diverges on the raw lab features and converges on the standardised ones. What did standardising change?",
                        "opts": [
                            r"The location of the minimum, which moved to the origin, where the lab's all-zero starting weights were already sitting",
                            r"The size of the gradient's $2/n$ factor, which the division by each column's own standard deviation exactly cancels out",
                            r"The need for a bias column, since centred features have mean zero and there is no longer any intercept left to fit",
                            r"The bowl's curvature: the largest eigenvalue fell from about $62$ to about $2$, so $2/\lambda_{\max}$ rose above $0.1$",
                        ],
                        "a": 3,
                        "whys": [
                            r"The minimum is wherever the data puts it, and on standardised features the intercept is the mean of $y$, about $12.3$, not $0$. Descent from zero still has to get there; what changed is that it can.",
                            r"The $2/n$ is a constant in front of the whole gradient and has nothing to do with the columns. Standardising changes the columns' scale, which changes $X^T X$, which changes the curvature.",
                            r"Centred features still need an intercept, because $y$ is not centred; the fitted $w_0$ is the mean of $y$. The bias column stays, and the lab adds it after standardising.",
                            r"Each step multiplies the error along a direction by $1 - \eta\lambda$, and at $\lambda = 62$ with $\eta = 0.1$ that is $-5.2$.",
                        ],
                        "why": r'''
Along a direction of curvature $\lambda$ one step multiplies the distance to the optimum by $1 - \eta\lambda$, which shrinks only when $\eta < 2/\lambda$. On the raw features the $x_1$ column runs from $0$ to $10$, the Hessian's largest eigenvalue is about $62$, and the ceiling is $0.032$; at $0.1$ that direction blows up. Dividing each column by its spread makes every diagonal entry of the Hessian $2$, the largest eigenvalue about $2.1$, and the ceiling about $0.95$. The minimum, the gradient's constant and the need for a bias are all unchanged.
''',
                    },
                    {
                        "q": r"A trace of the intercept weight reads $22.2, 4.4, 18.6, 7.3, 16.4, 9.1$, and the target is $12.3$. Which learning-rate regime produced it?",
                        "opts": [
                            r"A rate above the ceiling, so the per-step factor $1 - \eta\lambda$ is below $-1$ and the swings are about to keep growing",
                            r"A rate below the ceiling but past half of it, so the factor $1 - \eta\lambda$ is negative and each overshoot is smaller than the last",
                            r"A rate far too small, so the intercept is crawling and the alternation is the noise in the training data showing through",
                            r"A rate that is fine, since the values are converging on the target; the alternation is only a rounding artefact of printing to one decimal",
                        ],
                        "a": 1,
                        "whys": [
                            r"Above the ceiling the swings grow: $22$ would be followed by something further from $12.3$, not nearer. Here each swing is about four fifths of the one before, which is a factor of $-0.8$.",
                            r"The distance from $12.3$ goes $9.9, 7.9, 6.3, 5.0, 4.1, 3.2$, shrinking by a fifth each step with the sign flipping: the signature of $1 - \eta\lambda = -0.8$.",
                            r"A crawl moves in one direction by tiny amounts, and the lab's data has no noise at all. Leaping from $22$ to $4$ is not crawling, and it is not noise.",
                            r"Rounding to one decimal cannot turn a smooth approach into swings of ten units. The alternation is real, and it means the step is long enough to overshoot on every single update.",
                        ],
                        "why": r'''
The distance from the target is $9.9$, then $7.9$, $6.3$, $5.0$, $4.1$, $3.2$: it shrinks by a fifth each step and changes sign each step, so the per-step factor is $-0.8$, which is $1 - \eta\lambda$ at $\eta = 0.9$ on a direction of curvature $2$. That is inside the stable range, so the trace converges, but it does so by overshooting on every update. The same rate a little higher, at $1.05$, gives a factor of $-1.1$ and the swings grow instead. Oscillation that shrinks and oscillation that grows sit either side of the ceiling, and a printed trace tells them apart at once.
''',
                    },
                    {
                        "q": r"You drop the $2$ from the gradient and use $\frac{1}{n}X^T(Xw - y)$, keeping `lr=0.1` and 500 epochs. What changes?",
                        "opts": [
                            r"The destination: the weights converge to half of the least-squares solution, because every gradient along the way was halved",
                            r"Convergence fails, since the update no longer follows the true gradient of the mean squared error and wanders off",
                            r"Nothing about the destination: each step is half as long, so the run behaves like `lr=0.05` and reaches the same weights later",
                            r"The stability ceiling halves, so `lr=0.1` now diverges on the standardised features where the full gradient converged comfortably",
                        ],
                        "a": 2,
                        "whys": [
                            r"The zero of the gradient is unchanged by scaling it, so the minimum is where it was. Halving the gradient changes how fast you walk, not where the bottom of the bowl is.",
                            r"Half the true gradient still points downhill, and descent along any positive multiple of the gradient converges, given a small enough step. It is a slower run, not a failed one.",
                            r"$\eta \cdot \frac{1}{n}X^T r$ is the same vector as $\frac{\eta}{2} \cdot \frac{2}{n}X^T r$, step for step.",
                            r"Halving the gradient halves the effective step, which makes the run more stable, not less; the ceiling on `lr` doubles. The reading's rates were computed for the gradient that keeps the $2$.",
                        ],
                        "why": r'''
Descent with a halved gradient at rate $\eta$ takes exactly the steps that the full gradient takes at rate $\eta/2$, so the run behaves like `lr=0.05`: same bowl, same bottom, half the speed. After 500 epochs the weights are a little further from the closed form than they would have been, and the lab's `1e-4` tolerance may or may not still be met. The trap is that every rate quoted in the reading, and every ceiling of the form $2/\lambda_{\max}$, assumed the $2$ is there; drop it and those numbers are all off by a factor of two.
''',
                    },
                    {
                        "q": r"A data set has a million rows and five features. Which method fits it more cheaply, and why?",
                        "opts": [
                            r"The normal equation: forming $X^T X$ is one pass over the data, and the $6 \times 6$ solve after it costs nothing",
                            r"Gradient descent: each step is $O(nd)$, which is a smaller number than the $O(d^3)$ that elimination has to pay",
                            r"Gradient descent: the normal equation needs an $n \times n$ matrix, which cannot possibly fit in memory at that size",
                            r"Neither: with that many rows $X^T X$ becomes singular, so only a regularised solve can proceed at all",
                        ],
                        "a": 0,
                        "whys": [
                            r"$O(nd^2)$ to form the products is six million multiplications per column, and $O(d^3)$ on a $6 \times 6$ system is a few hundred more.",
                            r"$O(d^3)$ with $d = 6$ is about two hundred operations, and one descent step at $O(nd)$ is six million. Descent needs hundreds of steps; the comparison runs the other way at this shape.",
                            r"The normal equation never forms an $n \times n$ matrix. $X^T X$ is $d \times d$, six by six here, and forming it streams through the rows without holding anything of size $n^2$.",
                            r"More rows make $X^T X$ better conditioned, not worse; singularity comes from dependent columns, and there are only five of them. Regularisation has a place, but not because of $n$.",
                        ],
                        "why": r'''
Cost is set by the shape. Forming $X^T X$ and $X^T y$ is $O(nd^2)$, a single streaming pass through the million rows accumulating a $6 \times 6$ matrix and a vector of length $6$, and the elimination that follows is $O(d^3)$ on six unknowns, which is trivial. Gradient descent also pays $O(nd)$ per step but needs hundreds of steps to match. The closed form loses only when $d$ is large, where $d^3$ and the $d \times d$ matrix itself become the problem; at five features it wins outright.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "A probability, the loss that belongs to it, and four cells",
                    "minutes": 12,
                    "body": r'''
A blood test returns a number, and the question is whether the patient has the condition: yes or no, $1$ or $0$. You have two hundred past results with the answer known, and the obvious move is the last module's: fit $y = w_0 + w_1 x$ to the labels and call anything above $0.5$ a yes. Draw it and the trouble is visible. The line runs past $1$ for high readings and below $0$ for low ones, so it cannot be read as the chance of anything; and one healthy patient with a wildly high reading pulls the whole line down, moving the threshold for everyone else, although that patient was already on the correct side of it and could not be classified any better.

What the picture wants is a score that can run from $-\infty$ to $\infty$, because a linear function of the features does that whether you like it or not, and a probability that stays inside $(0, 1)$. The bridge between them is the odds. A probability $p$ has odds $p/(1-p)$, which run from $0$ to $\infty$, and the log of the odds runs over the whole real line. So let the linear score *be* the log-odds:

$$\log\frac{p}{1-p} = x \cdot w = z$$

and solve for $p$: $p = e^z/(1 + e^z) = 1/(1 + e^{-z})$. That is the logistic function $\sigma(z)$, and its shape follows from the derivation. At $z = 0$ the odds are even and $p = 0.5$. Far above $0$ it saturates near $1$, far below near $0$, and a patient with an absurd reading contributes an absurdly confident probability rather than dragging a line about. Adding $1$ to $z$ multiplies the odds by $e$ whatever they were, which is what a weight means here: the change in log-odds per unit of its feature.

## A loss that belongs to the model

Squared error was the natural loss for a line, because the line's residuals were the picture. Here the model claims something more specific: each label is a coin toss that comes up $1$ with probability $p_i = \sigma(x_i \cdot w)$. If that is the claim, the natural question is how likely the observed labels were under it. For one row that is $p_i$ if $y_i = 1$ and $1 - p_i$ if $y_i = 0$, which one expression covers, $p_i^{y_i}(1 - p_i)^{1 - y_i}$, and for independent rows the probabilities multiply. A product of two hundred numbers below $1$ underflows, so take the log, which turns the product into a sum, and negate it so that better is smaller. Divide by $n$ and you have the mean cross-entropy:

$$L(w) = -\frac{1}{n}\sum_{i=1}^{n}\left[y_i\log p_i + (1 - y_i)\log(1 - p_i)\right]$$

Each row pays $-\log$ of the probability the model gave to what actually happened. A confident correct prediction pays almost nothing; a confident wrong one pays without limit, because $-\log p \to \infty$ as $p \to 0$. Here is the lab's own example:

```python
import math

y = [1, 0]
p = [0.9, 0.2]
terms = []
for target, prob in zip(y, p):
    q = min(max(prob, 1e-12), 1.0 - 1e-12)
    term = -(target * math.log(q) + (1 - target) * math.log(1 - q))
    terms.append(term)
    print(f"y={target}, p={prob}: costs {term:.5f}")
print("mean:", sum(terms) / len(terms))
print("a confident miss, y=1 with p=0.0, costs", -math.log(1e-12))
```

The clip at $10^{-12}$ is not cosmetic. Python's `math.log(0.0)` raises `ValueError`, and a model that assigns probability exactly $0$ to a label that occurred has, in strict likelihood terms, an infinite loss. Capping it at $27.6$ keeps the number finite and keeps the gradient finite with it.

## The gradient, and why squared error is the wrong loss here

Two facts about $\sigma$ make the derivative short. First, $1 - \sigma(z) = \sigma(-z)$. Second, differentiating $\sigma(z) = (1 + e^{-z})^{-1}$ gives $e^{-z}/(1 + e^{-z})^2$, which is $\sigma(z)\,\sigma(-z) = \sigma(z)(1 - \sigma(z))$. Now differentiate one row's loss $\ell = -[y\log p + (1 - y)\log(1 - p)]$ with respect to $z$, writing $p = \sigma(z)$:

$$\frac{d\ell}{dz} = \left(-\frac{y}{p} + \frac{1 - y}{1 - p}\right)p(1 - p) = -y(1 - p) + (1 - y)p = p - y$$

The $p(1-p)$ from the sigmoid cancels the denominators from the logs exactly, and what is left is the plain residual. Since $\partial z/\partial w_j = x_j$, the gradient of the mean loss is

$$\nabla L = \frac{1}{n}X^T\left(\sigma(Xw) - y\right)$$

Set this beside the last module's $\frac{2}{n}X^T(Xw - y)$. Same shape: the transposed design matrix times a residual. The differences are the $\sigma$ wrapped around the prediction and the missing $2$, which belonged to the square and has no counterpart here.

This is also the answer to why not squared error. Had you minimised $\frac{1}{n}\sum(\sigma(z_i) - y_i)^2$ instead, the chain rule would have left the factor $\sigma(z)(1 - \sigma(z))$ in the gradient uncancelled. That factor is largest at $p = 0.5$ and tends to $0$ at either end. A row the model is confidently wrong about, $y = 1$ with $p = 0.001$, would then contribute a gradient near $0$: the worse the mistake, the less the model learns from it. The cross-entropy gradient for the same row is $p - y = -0.999$, the largest it can be. Squared error on a sigmoid is also not convex in $w$, so descent can settle in a side valley; cross-entropy is convex, and the bowl has one bottom.

## Keeping the arithmetic finite

Before any of this can run, the sigmoid has to survive its inputs. A weight vector a few epochs into training can produce $z = -800$ for an outlying row, and the textbook formula then asks for $e^{800}$:

```python
# raises OverflowError
import math
print(math.exp(800))
```

A float holds about $10^{308}$ and $e^{800}$ is about $10^{347}$, and `math.exp` raises rather than returning `inf`. The fix is algebra, not clipping: multiply the numerator and denominator of $1/(1 + e^{-z})$ by $e^z$ to get $e^z/(1 + e^z)$, the same number, whose only exponential has a negative argument when $z$ is negative. Use whichever form keeps the exponent non-positive:

```python
import math

def sigmoid(z):
    if z >= 0.0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)

for z in (-800.0, -2.0, 0.0, 2.0, 800.0):
    print(f"sigmoid({z:>6}) = {sigmoid(z)}")
```

$\sigma(-800)$ comes out as $0.0$ and $\sigma(800)$ as $1.0$, by underflow to within $10^{-300}$ of the true value, and neither raises.

## One step by hand, then two thousand

Four patients in one dimension, readings $-2, -1, 1, 2$, labels $0, 0, 1, 1$, and a bias column. From $w = (0, 0)$ every score is $0$ and every probability is $0.5$. The residuals are $0.5, 0.5, -0.5, -0.5$. The intercept gradient is their mean, $0$, because the classes are balanced; the slope gradient is $\frac{1}{4}\sum x_i r_i = \frac{1}{4}(-1 - 0.5 - 0.5 - 1) = -0.75$. At $\eta = 0.5$ the slope moves to $0.375$:

```python
import math

def sigmoid(z):
    if z >= 0.0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)

X = [[1.0, -2.0], [1.0, -1.0], [1.0, 1.0], [1.0, 2.0]]
y = [0, 0, 1, 1]
w = [0.0, 0.0]
for step in range(2000):
    p = [sigmoid(w[0] * row[0] + w[1] * row[1]) for row in X]
    residual = [pi - yi for pi, yi in zip(p, y)]
    grad = [sum(row[j] * r for row, r in zip(X, residual)) / 4 for j in range(2)]
    w = [wj - 0.5 * gj for wj, gj in zip(w, grad)]
    if step < 2:
        print(f"step {step}: p={[round(v, 3) for v in p]} grad={[round(g, 3) + 0.0 for g in grad]} w={[round(v, 3) for v in w]}")
print("after 2000 steps w =", [round(v, 3) for v in w])
print("probabilities:", [round(sigmoid(w[0] + w[1] * row[1]), 3) for row in X])
```

The intercept never moves, which is right for a symmetric problem. The slope keeps growing: $6.2$ after two thousand steps, and larger after ten thousand. Those four points are perfectly separable, and for separable data the cross-entropy has no minimum: every doubling of $w$ pushes the probabilities closer to $0$ and $1$ and the loss closer to $0$, without arriving. The lab's blobs are separable in practice, which is why its fit reaches training accuracy $1.0$ and why the L2 term exists. Adding $\frac{\lambda}{2n}\sum_{j \ge 1} w_j^2$ to the loss adds $\lambda w_j / n$ to each slope's gradient, a pull back towards $0$ that grows with the weight, and the tug of war then has a finite winner. The intercept is left out of the sum on purpose. It encodes the base rate, the log-odds of the positive class when every feature is at zero, and shrinking it towards $0$ drags every probability towards $0.5$ whatever the class balance actually is.

## Four numbers from one table

Once probabilities become labels at a threshold, every prediction lands in one of four cells: true positive, false positive, false negative, true negative. The lab's example gives $(3, 1, 1, 3)$:

```python
def confusion_matrix(y_true, y_pred):
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

y_true = [1, 1, 1, 0, 0, 0, 0, 1]
y_pred = [1, 0, 1, 0, 1, 0, 0, 1]
tp, fp, fn, tn = confusion_matrix(y_true, y_pred)
print("tp, fp, fn, tn =", (tp, fp, fn, tn))
precision = tp / (tp + fp)
recall = tp / (tp + fn)
print("precision", precision, "recall", recall, "F1", 2 * precision * recall / (precision + recall))

p, r = 1.0, 0.01
print("arithmetic mean of 1.0 and 0.01:", (p + r) / 2)
print("harmonic mean of 1.0 and 0.01:  ", round(2 * p * r / (p + r), 4))
```

Precision, $tp/(tp + fp)$, answers a question about the predictions: of the rows I flagged, how many were right? Recall, $tp/(tp + fn)$, answers a question about the truth: of the rows that were positive, how many did I catch? They are different questions, and which matters depends on what a mistake costs. A screening test wants recall, because a missed case is the expensive error; a filter that deletes messages wants precision, because a wrongly deleted one is. Accuracy answers neither. On a condition that one patient in a hundred has, a model that says no to everyone scores $0.99$ and catches nobody.

F1 is meant to reward both at once, and it uses the harmonic mean because the arithmetic mean can be gamed. The harmonic mean of two rates is $2/(1/P + 1/R)$, which rearranges to $2PR/(P + R)$, and it sits close to the smaller of the two. A model with precision $1.0$ and recall $0.01$ has an arithmetic mean of $0.505$, which looks like a coin toss, and an F1 of $0.0198$, which looks like what it is. When nothing is predicted positive, precision is $0/0$; when there are no positives, recall is. The lab returns $0.0$ for both rather than raising, and that is a convention: the honest answer is *undefined*, and a library that returns $0$ with a warning has chosen the same convenience.

## A metric with no threshold in it

Everything above depends on the $0.5$. Move it and the cells shift. ROC-AUC asks a threshold-free question: pick a random positive and a random negative, and how often does the positive get the higher score?

```python
y_true = [0, 0, 1, 1]
scores = [0.1, 0.4, 0.35, 0.8]
positives = [s for s, t in zip(scores, y_true) if t == 1]
negatives = [s for s, t in zip(scores, y_true) if t == 0]
wins = 0.0
for p in positives:
    for q in negatives:
        verdict = 1.0 if p > q else 0.5 if p == q else 0.0
        wins += verdict
        print(f"positive {p} against negative {q}: {verdict}")
print("AUC =", wins / (len(positives) * len(negatives)))
```

Three of the four pairs are ordered correctly, and the tie rule, half a win when the scores are equal, is what a coin toss between the two would give. The name comes from the ROC curve, which plots true-positive rate against false-positive rate as the threshold slides from top to bottom, and the pair count is that curve's area. To see why, sort the rows by score and walk down. Each negative you pass moves the curve one cell right, each positive one cell up, on a grid of $P \times N$ cells, and a cell sits under the curve exactly when its positive was passed, scored higher, before its negative. The area is the fraction of correctly ordered pairs.

When one class is absent there are no pairs and no curve, and the lab returns $0.5$, the value of a model that knows nothing, as its convention. Two things AUC ignores are worth holding on to. It does not care whether the scores are calibrated, only how they rank: multiply every score by $0.001$ and the AUC does not move. And it does not say where to put the threshold; it says whether any threshold could do well.

## Where it stops, and the mistake in between

Logistic regression draws one straight boundary, $x \cdot w = 0$. The two clouds in the lab sit on either side of such a line, which is why the fit separates them; the ring-shaped data in the next module does not, and no weight vector will help. F1 ignores true negatives, so it changes when you swap which class is called positive. AUC computed on hard labels rather than scores collapses the curve to a single corner and is not the number you wanted.

The mistake to name is reporting accuracy alone and calling it done. It is tempting because accuracy is one number whose meaning seems plain, and on balanced data it is even fine. But the data that matters is rarely balanced, and $0.99$ on a one-in-a-hundred problem is the score of the model that does nothing.

In the lab, *Logistic regression and the metrics that judge it*, you will write the safe sigmoid, the clipped cross-entropy, the gradient with the intercept left out of the penalty, and the four metrics, and check that the fit separates the blobs at accuracy $1.0$ and AUC $1.0$ while L2 pulls the slopes in without touching $w_0$.
''',
                },
            ],
            "quiz": {
                "title": "Odds, losses and four cells",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Cross-entropy is paired with the sigmoid rather than squared error. What does that choice do to the gradient of one row's loss with respect to its score $z$?",
                        "opts": [
                            r"It leaves $(p - y)\,p(1 - p)$: the sigmoid's slope stays in, so a confident miss contributes almost nothing to the update at all",
                            r"It leaves $p - y$: the sigmoid's slope cancels the logs' denominators, so a confident miss gives the largest possible update",
                            r"It leaves $\log p - \log(1 - p)$: the two log terms separate and the sigmoid drops out of the derivative entirely",
                            r"It leaves $2(p - y)$: the same as squared error up to its constant, which is why the two losses train almost alike",
                        ],
                        "a": 1,
                        "whys": [
                            r"That is the squared-error gradient, with the sigmoid's slope left uncancelled, and it is the defect cross-entropy removes: at $p = 0.001$ against $y = 1$ the factor $p(1-p)$ is near zero and the model barely learns from its worst row.",
                            r"The derivative of $-[y\log p + (1-y)\log(1-p)]$ with respect to $p$ has $p$ and $1-p$ in its denominators, and $dp/dz = p(1-p)$ cancels both.",
                            r"The sigmoid cannot drop out, since $p$ is a function of $z$ and the derivative goes through it. The two log terms are weighted by $y$ and $1-y$, so only one of them is active for any given row.",
                            r"There is no $2$; it belonged to the square. And the losses do not train alike, because squared error on a sigmoid is not convex and its gradient vanishes exactly where the model is most wrong.",
                        ],
                        "why": r'''
Write $p = \sigma(z)$. The loss's derivative with respect to $p$ is $-y/p + (1-y)/(1-p)$, and the sigmoid's derivative is $p(1-p)$. Multiply and the denominators cancel, leaving $-y(1-p) + (1-y)p = p - y$. That residual is largest when the model is most wrong, which is where the biggest correction belongs. With squared error the factor $p(1-p)$ survives, and it tends to zero at exactly the confident mistakes.
''',
                    },
                    {
                        "q": r"The naive `1 / (1 + math.exp(-z))` is called with `z = -800`. What happens, and what is the fix?",
                        "opts": [
                            r"It returns `0.0`, since `exp(800)` is infinite and one over infinity is zero, so nothing at all needs fixing",
                            r"It returns `nan`, because infinity divided by infinity is undefined; clip $z$ into $[-1, 1]$ before every call to be safe",
                            r"It returns a tiny negative number from rounding; take the absolute value so that probabilities stay inside range",
                            r"`math.exp(800)` raises `OverflowError`; use $e^{z}/(1 + e^{z})$ for negative $z$, the same value with a safe exponent",
                        ],
                        "a": 3,
                        "whys": [
                            r"That is what a float `inf` would give, but `math.exp` does not return `inf` for a finite argument that is too large; it raises, and the lab's tests call `sigmoid(-800)` to prove the branch exists.",
                            r"There is no infinity to divide by, because the exception fires first. And clipping $z$ to $[-1, 1]$ would cap every probability between $0.27$ and $0.73$, wrecking the model to save the arithmetic.",
                            r"Rounding never makes $1/(1 + e^{-z})$ negative, since every quantity in it is positive. The problem is an exception, and the absolute value of an exception is still an exception.",
                            r"A float tops out near $10^{308}$ and $e^{800}$ is near $10^{347}$; the rewritten form asks for $e^{-800}$ instead, which underflows harmlessly to $0$.",
                        ],
                        "why": r'''
`math.exp(800)` cannot be represented as a float, and Python raises `OverflowError` rather than returning `inf`. Multiplying the top and bottom of $1/(1 + e^{-z})$ by $e^{z}$ gives $e^{z}/(1 + e^{z})$, algebraically identical, and for negative $z$ its only exponential has a negative argument, which underflows to $0$ without complaint. Branch on the sign of $z$ and use whichever form keeps the exponent non-positive.
''',
                    },
                    {
                        "q": r"A classifier's threshold is raised from $0.5$ to $0.9$, so it flags fewer rows. What happens to precision and recall, in the usual case?",
                        "opts": [
                            r"Precision tends to rise and recall to fall: the rows still flagged are the surest ones, but positives under $0.9$ are now missed",
                            r"Both rise: fewer flagged rows means fewer false positives, and a stricter threshold means fewer false negatives as well",
                            r"Recall tends to rise and precision to fall: a stricter threshold catches more of the true positives at the cost of extra false alarms",
                            r"Neither moves: precision and recall are properties of the scores, and only the ROC-AUC depends on where the threshold sits",
                        ],
                        "a": 0,
                        "whys": [
                            r"The flagged set shrinks to the highest-scoring rows, so the false positives among them thin out, while every true positive scoring between $0.5$ and $0.9$ becomes a false negative.",
                            r"Fewer flagged rows cannot mean fewer false negatives. A false negative is a positive that was not flagged, and raising the threshold can only add to that set, never remove from it.",
                            r"This is the two metrics with their directions swapped. Recall counts positives caught, and a stricter threshold catches fewer; precision counts flags that were right, and the surviving flags are the most confident ones.",
                            r"It is the other way round: precision and recall are computed from hard labels, which the threshold creates, while AUC is computed from the ranking of the scores and is the one that does not move.",
                        ],
                        "why": r'''
Precision is $tp/(tp+fp)$ and recall is $tp/(tp+fn)$. Raising the threshold moves rows out of the flagged set. Every true positive that leaves becomes a false negative, so recall can only fall; the rows that remain are the highest-scoring, so the false positives among them are typically a smaller share and precision rises. The trade-off is why neither number is enough on its own, and why AUC, which looks at the ranking rather than any one cut, is reported beside them.
''',
                    },
                    {
                        "q": r"A model has precision $1.0$ and recall $0.01$. Its F1 is $0.0198$, not $0.505$. Why does F1 use the harmonic mean?",
                        "opts": [
                            r"The harmonic mean is the only average that stays between the two rates, which is what keeps the score inside $[0, 1]$",
                            r"Precision and recall are rates, and rates combine by adding their reciprocals, in the way parallel resistances do",
                            r"The harmonic mean sits near the smaller rate, so a model cannot buy a high score by maxing one rate at the other's cost",
                            r"The harmonic mean equals accuracy whenever the two classes are balanced, which makes F1 directly comparable with accuracy",
                        ],
                        "a": 2,
                        "whys": [
                            r"The arithmetic mean also lies between the two rates and so also lands in $[0, 1]$; staying in range does not distinguish them. What distinguishes them is where in the range they land.",
                            r"The reciprocal rule for resistors comes from currents adding through parallel paths; nothing in a confusion matrix adds that way. The harmonic mean was chosen for how it behaves, not because rates demand it.",
                            r"$2/(1/P + 1/R)$ is dominated by whichever reciprocal is large, and $1/0.01 = 100$ swamps $1/1.0 = 1$.",
                            r"F1 and accuracy are computed from different cells, since F1 never sees the true negatives, and they disagree even on balanced data. No identity ties them together.",
                        ],
                        "why": r'''
The harmonic mean of $P$ and $R$ is $2/(1/P + 1/R) = 2PR/(P+R)$. Reciprocals of small numbers are large, so a tiny recall makes $1/R$ enormous and the mean collapses towards it. The arithmetic mean would let a model that flags one sure row and nothing else score $0.505$, which reads like a coin toss for a model that catches one positive in a hundred.
''',
                    },
                    {
                        "q": r"Every score a model produces is multiplied by $0.001$, so none exceeds the $0.5$ threshold any more. What happens to its ROC-AUC?",
                        "opts": [
                            r"It drops to $0.5$: with no score above the threshold nothing is flagged, so positives and negatives are indistinguishable",
                            r"Nothing: AUC depends only on how positives rank against negatives, and a positive scaling preserves every such order",
                            r"It drops to $0.0$: every positive now scores below the cut, and that counts as a loss against every negative in the set",
                            r"It becomes undefined: the ROC curve needs at least one threshold at which something is predicted positive",
                        ],
                        "a": 1,
                        "whys": [
                            r"That would be true of accuracy or F1 at a fixed threshold. AUC has no fixed threshold in it; it walks every possible cut, and the cut at $0.0004$ separates these scores as well as $0.4$ did the originals.",
                            r"For every positive-negative pair, $0.001p > 0.001q$ exactly when $p > q$, so every win, loss and tie is unchanged.",
                            r"A pair is scored by comparing the positive's score to the negative's, not to $0.5$. Both may sit below the threshold, and the positive can still be the higher of the two.",
                            r"The curve is drawn by sliding the threshold through every score value, and there is always a value low enough to flag everything. Nothing about $0.5$ enters it.",
                        ],
                        "why": r'''
AUC is the fraction of positive-negative pairs in which the positive scores higher, with ties at a half. Multiplying by a positive constant changes no comparison, so the count is untouched and the AUC is the same number. That invariance is the point: AUC judges the ranking, not the calibration or the threshold, which is also why it cannot tell you where to cut.
''',
                    },
                    {
                        "q": r"In `fit_logistic`, a learner adds `l2 * w[j] / n` to the gradient for every `j`, the intercept included. What goes wrong?",
                        "opts": [
                            r"Nothing: the intercept is a weight like any other, and shrinking it makes the model more robust to outlying training rows",
                            r"Descent stops converging, because the penalty on $w_0$ and the data gradient on $w_0$ never agree on a sign",
                            r"The slopes are no longer shrunk, since the penalty's budget is spent on the intercept instead of the features",
                            r"The intercept is dragged towards $0$, pulling every probability towards $0.5$ whatever the share of positives actually is",
                        ],
                        "a": 3,
                        "whys": [
                            r"It is not like any other: it carries the class balance rather than a feature's effect. And shrinking it does nothing about outliers, which act through the slopes.",
                            r"Descent converges fine; a penalised intercept is a convex problem like the rest. The trouble is the answer it converges to, which is biased towards even odds.",
                            r"There is no budget: each weight's penalty is its own term, and adding one for $w_0$ leaves the slopes' terms untouched. The slopes shrink exactly as before.",
                            r"$w_0$ is the log-odds of the positive class when every feature is at $0$, and pulling it to $0$ says the base rate is even whether or not it is.",
                        ],
                        "why": r'''
The intercept sets where the boundary sits when the features contribute nothing, which is the log-odds of the base rate. Penalising it pulls that rate towards $0.5$ with no evidence from the data, so on a one-in-ten problem every probability is biased upwards. The lab's hint says it plainly: penalising the intercept quietly biases every prediction towards 0.5. Its L2 test checks that the slope norm shrinks and says nothing about $w_0$, because $w_0$ is meant to be left alone.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Twenty questions with thresholds, and why a crowd of trees beats one",
                    "minutes": 12,
                    "body": r'''
Spread the lab's data on a table: 220 points in a square six units across, each labelled $1$ if it lies outside a circle of radius about $1.8$ and $0$ if inside, with one label in ten flipped at random. The last module's classifier draws one straight line, and no straight line separates a disc from its surroundings. But you can play twenty questions. Is $a$ greater than $1.8$? Then the point is outside, whatever $b$ is. Is $a$ less than $-1.8$? Outside again. Otherwise, is $b$ above $1.8$, or below $-1.8$? Four questions have carved off the outer band, and a few more inside what is left carve the corners. Each question splits a rectangle into two rectangles along one axis, and a stack of them can approximate any shape, a circle included, to whatever resolution you have patience for. The question is how to choose the questions.

## A number for mixed

A good question is one whose answers leave the two groups purer than the group they came from, so we need a number for how mixed a group is. Take the labels at a node and imagine drawing two of them at random, with replacement. The probability that the two agree is $\sum_k p_k^2$, where $p_k$ is the share of label $k$, and the probability that they disagree is

$$G = 1 - \sum_k p_k^2$$

That is the Gini impurity, and its behaviour follows from the picture. A pure node has one label with share $1$, the draws always agree, and $G = 0$. A node split evenly between two labels has $G = 1 - (0.25 + 0.25) = 0.5$, the most mixed two labels can be. Entropy measures the same thing with a different question: how many bits, on average, does it take to say which label a random draw was? A label with share $p$ carries $-\log_2 p$ bits of surprise, and the average surprise is

$$H = -\sum_k p_k \log_2 p_k$$

A pure node needs zero bits, a fair fifty-fifty needs one, and the lab's second example, three of one label and one of the other, needs $0.75 \times 0.415 + 0.25 \times 2 = 0.811$:

```python
import math
from collections import Counter

def gini(labels):
    n = len(labels)
    if n == 0:
        return 0.0
    return 1.0 - sum((c / n) ** 2 for c in Counter(labels).values())

def entropy(labels):
    n = len(labels)
    if n == 0:
        return 0.0
    total = 0.0
    for count in Counter(labels).values():
        p = count / n
        total -= p * math.log2(p)
    return total

for node in ([0, 0, 1, 1], [0, 0, 0, 1], [1, 1, 1, 1]):
    print(f"{node}: gini {gini(node):.4f}  entropy {entropy(node):.4f}")
```

Both are zero exactly when the node is pure and largest when the labels are evenly split, and on most data they choose the same splits. The lab has you write both so that `criterion` is a real choice, and its tests check that trees grown under either one work.

## What a question is worth

A split takes a node with impurity $G_{\text{parent}}$ and produces a left child holding $n_L$ of the $n$ samples and a right child holding $n_R$. Its gain is what it removed:

$$\text{gain} = G_{\text{parent}} - \left(\frac{n_L}{n}G_L + \frac{n_R}{n}G_R\right)$$

The weights are the point. Without them, a split that peels one sample into a pure leaf of its own scores $G_L = 0$ and looks as good as a split that sorts the whole node, when it has done almost nothing. Weighting by size charges each child for the share of the data it holds, so the lone leaf's zero counts for $1/n$ of the total and the large, still-mixed sibling counts for the rest.

Which thresholds are worth trying? For one feature, sort its distinct values. Any threshold strictly between two neighbours produces the same left and right sets as any other threshold in that gap, so there is exactly one partition per gap, and the midpoint is its canonical representative, the cut that sits furthest from both values it separates. Here is the lab's own example, four points at $1, 2, 3, 4$ with labels $0, 0, 1, 1$:

```python
from collections import Counter

def gini(labels):
    n = len(labels)
    if n == 0:
        return 0.0
    return 1.0 - sum((c / n) ** 2 for c in Counter(labels).values())

X = [[1], [2], [3], [4]]
y = [0, 0, 1, 1]
parent = gini(y)
values = sorted(set(row[0] for row in X))
for low, high in zip(values, values[1:]):
    threshold = (low + high) / 2
    left = [y[i] for i in range(len(y)) if X[i][0] <= threshold]
    right = [y[i] for i in range(len(y)) if X[i][0] > threshold]
    child = len(left) / len(y) * gini(left) + len(right) / len(y) * gini(right)
    print(f"threshold {threshold}: left {left} right {right} weighted child {child:.4f} gain {parent - child:.4f}")
```

The middle cut sorts the node completely and its gain is the whole parent impurity, $0.5$. The outer two each isolate one point, and the size weighting prices that at a third of the value. `best_split` returns `(0, 2.5, 0.5)`: the feature, the threshold and the gain, with `left` meaning $x \le 2.5$.

## Growing, and stopping

A tree is that search applied recursively. Find the best split of the node, send the rows each way, and repeat on each child until a stopping rule fires. The lab has four. A depth limit, because each level can double the number of leaves; a minimum number of samples to split, because a node of two rows has nothing to say about a third; purity, because a pure node cannot be improved; and a gain that is not positive, because a split that removes no impurity is noise made permanent. A leaf predicts the majority label of the rows that reached it, with ties going to the smaller label so that the prediction depends on the data and not on dictionary order.

## What a tree that is allowed to keep going does

Let the depth reach $8$ on the lab's 150 training rows and the tree reproduces every label, the seventeen flipped ones included, for a training accuracy of exactly $1.0$. On the 70 rows it did not see, it scores about $0.76$. The mechanism is visible if you picture it. A flipped label is a point marked $1$ sitting inside the disc among points marked $0$. A deep tree, asked to fit it, adds cuts until that one point has a rectangle of its own, and then predicts $1$ for that whole rectangle. New points that land in it are almost all genuine $0$s, and the rectangle mislabels every one. The tree has not learned the circle better; it has learned the noise, at the cost of the region around each noisy point. This is variance in the sense the module's title means: grow the same tree on a different sample of 150 rows and the noisy points move, their rectangles move with them, and the two trees disagree wherever a rectangle was.

## Averaging the disagreement away

If the trees disagree where the noise is and agree where the signal is, a vote among many of them keeps the signal and cancels the noise. Bagging manufactures the many trees from one data set by resampling it: draw $n$ rows with replacement, fit a tree, repeat. Each bootstrap sample leaves some rows out. A given row is missed by one draw with probability $1 - 1/n$, and by all $n$ draws with probability $(1 - 1/n)^n$, which tends to $1/e \approx 0.368$:

```python
import random

rng = random.Random(7)
n = 150
coverage = []
for _ in range(200):
    picks = [rng.randrange(n) for _ in range(n)]
    coverage.append(len(set(picks)) / n)
print("mean fraction of distinct rows in a bootstrap:", round(sum(coverage) / len(coverage), 4))
print("1 - (1 - 1/n)^n =", round(1 - (1 - 1 / n) ** n, 4))
```

So each tree sees about $63\%$ of the rows, some repeated, and the trees differ because their samples do. The vote is a majority, ties again going to the smaller label.

How much does averaging buy? Suppose each tree's error at a point has variance $\sigma^2$ and any two trees' errors have correlation $\rho$. The average of $B$ of them has variance

$$\text{Var} = \frac{1}{B^2}\left(B\sigma^2 + B(B-1)\rho\sigma^2\right) = \rho\sigma^2 + \frac{1 - \rho}{B}\sigma^2$$

The first term inside the bracket is the $B$ variances on the diagonal of the covariance, the second is the $B(B-1)$ pairs off it. As $B$ grows the second term of the result vanishes and the first does not: no number of trees gets below $\rho\sigma^2$. And $\rho$ is not small, because the bootstraps overlap by about two thirds and the trees all reach for the same strong split first:

```python
import random

rng = random.Random(3)
n_models, trials = 25, 20000

def variance_of_average(rho):
    averages = []
    for _ in range(trials):
        shared = rng.gauss(0, rho ** 0.5)
        errors = [shared + rng.gauss(0, (1 - rho) ** 0.5) for _ in range(n_models)]
        averages.append(sum(errors) / n_models)
    mean = sum(averages) / trials
    return sum((a - mean) ** 2 for a in averages) / trials

for rho in (0.0, 0.5, 0.9):
    print(f"rho={rho}: simulated {variance_of_average(rho):.4f}, formula {rho + (1 - rho) / n_models:.4f}")
```

With $\rho = 0.5$, twenty-five trees reduce a variance of $1$ to $0.52$, nearly all of which is the floor. That floor is why a random forest is not merely bagging. At every node, instead of searching all $d$ features, the tree searches a random subset of them, `max_features` in size. Trees are then forced to build from different features in different places, their mistakes are less alike, $\rho$ falls, and the floor falls with it. The lab's forest uses one feature per node on two-dimensional data, which sounds crippling for a single tree and is the point for twenty-five of them.

What averaging does not touch is bias. If every tree in the forest misses the circle in the same way, because each is too shallow to bend around it, the average misses it the same way. Bagging deep trees works because deep trees have low bias and high variance, and variance is the thing a vote can spend.

## Where the search stops holding

The split search is greedy: it picks the single best cut now, with no view of what the cuts beneath it might achieve. On some data that is fatal. Four points at the corners of a square, labelled by whether the two coordinates differ, the exclusive-or:

```python
from collections import Counter

def gini(labels):
    n = len(labels)
    if n == 0:
        return 0.0
    return 1.0 - sum((c / n) ** 2 for c in Counter(labels).values())

X = [[0, 0], [0, 1], [1, 0], [1, 1]]
y = [0, 1, 1, 0]
parent = gini(y)
for j in range(2):
    left = [y[i] for i in range(4) if X[i][j] <= 0.5]
    right = [y[i] for i in range(4) if X[i][j] > 0.5]
    child = 0.5 * gini(left) + 0.5 * gini(right)
    print(f"split on feature {j} at 0.5: left {left} right {right} gain {parent - child}")
```

Every candidate split leaves both children exactly as mixed as the parent, the gain is $0$ everywhere, and the zero-gain rule makes the root a leaf. A depth-2 tree fits this data perfectly, but no depth-1 tree makes any progress towards it, and the greedy search cannot see two moves ahead. Axis-aligned cuts are the other limit: a boundary that runs diagonally costs a staircase of many splits where a rotated feature would cost one.

## The mistake

The mistake that spoils a forest silently is seeding. Build each tree with a fresh `random.Random(seed)` using the same seed and every tree draws the same bootstrap rows and the same feature subsets, so the forest is one tree copied twenty-five times, and its vote is that tree's opinion. Nothing crashes, and the forest still scores something, which is why it is tempting: reseeding per tree looks like reproducibility. The lab has you build one `random.Random(seed)` for the whole forest and hand that single object to every tree, so the draws form one reproducible stream that differs from tree to tree. Its last test builds two forests from the same seed and expects identical predictions, and a third from a different seed and expects them to change.

In the lab, *A decision tree, then a forest around it*, you will write `gini`, `entropy` and `best_split`, grow a `DecisionTree` under the four stopping rules, watch a depth-8 tree memorise the training rows and lose on the held-out ones, and then bag twenty-five feature-restricted trees into a `RandomForest` that beats it by a wide margin on the same seventy rows.
''',
                },
            ],
            "quiz": {
                "title": "Splits, leaves and the vote",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"`gini([0, 0, 0, 1])` is $0.375$. What does that number measure?",
                        "opts": [
                            r"The share of the node held by its minority label, which is the error a majority leaf would make on it",
                            r"The number of bits needed to encode one label drawn from the node, which is the same thing as its entropy",
                            r"One minus the accuracy that a leaf predicting the majority label would reach on the node's own rows",
                            r"The chance that two labels drawn from the node at random, with replacement, disagree with each other",
                        ],
                        "a": 3,
                        "whys": [
                            r"The minority share here is $0.25$, not $0.375$. Gini does track the minority share, but through squares, so it is not the same number.",
                            r"That is entropy, and for this node it is $0.811$ bits. The two measures agree on which nodes are pure and which are evenly split, and disagree on the numbers between.",
                            r"One minus the majority accuracy is $0.25$ again, the minority share. Gini is larger here because a random draw is wrong more often than a majority guess is.",
                            r"$1 - (0.75^2 + 0.25^2) = 1 - 0.625 = 0.375$, the disagreement probability for two independent draws.",
                        ],
                        "why": r'''
Gini is $1 - \sum_k p_k^2$, the probability that two labels drawn independently from the node differ. With shares $0.75$ and $0.25$ the draws agree with probability $0.5625 + 0.0625 = 0.625$ and disagree with probability $0.375$. It is not the minority share, which is $0.25$ and which the majority leaf's error would equal, and it is not the entropy, which is $0.811$ bits for the same node.
''',
                    },
                    {
                        "q": r"Why is the children's impurity weighted by their sizes before it is subtracted from the parent's?",
                        "opts": [
                            r"So that isolating one sample in a pure leaf earns a small gain, in proportion to the share of the data it sorted",
                            r"So that the gain always falls between $0$ and $1$, which lets gini gains and entropy gains be compared directly",
                            r"So that a child with more rows counts for more, because a larger node gives a more reliable estimate of impurity",
                            r"So that unbalanced splits are penalised outright, since the tree should prefer cuts that fall near the median",
                        ],
                        "a": 0,
                        "whys": [
                            r"An unweighted average would let $G_L = 0$ from a single peeled-off row count as much as a child holding the other $n - 1$.",
                            r"Weighting does not bound the gain by $1$; an entropy gain can exceed $1$ with more than two labels. And the two criteria are on different scales regardless of weighting.",
                            r"Reliability is a real concern, but the weights are not there to express it: they make the weighted child impurity equal the impurity of the whole partition, so the gain is a true before-and-after comparison.",
                            r"The weights do not penalise unbalanced splits as such. A lopsided cut that leaves both children pure has gain equal to the whole parent impurity, and is exactly what the tree should choose.",
                        ],
                        "why": r'''
The weighted sum $\frac{n_L}{n}G_L + \frac{n_R}{n}G_R$ is the impurity of the data after the cut, counted row by row, so subtracting it from the parent's impurity measures what the cut removed. In the reading's example the cut at $1.5$ makes a pure leaf of one row, and the weighting prices it at a third of the gain of the cut at $2.5$, which sorts all four. Without the weights the three cuts would look far closer than they are.
''',
                    },
                    {
                        "q": r"A depth-8 tree scores $1.0$ on the 150 training rows and about $0.76$ on the 70 held-out ones. What mechanism produces the gap?",
                        "opts": [
                            r"The tree is not deep enough to trace the circle, so its boxes cut across the boundary and misclassify the points near it",
                            r"The held-out rows come from a different region of the square than the training rows, which the tree never saw during growth",
                            r"Each flipped label got a rectangle of its own, and on new data that rectangle mislabels the genuine points that land in it",
                            r"Gini favours the majority class, so the tree under-predicts the minority label wherever the two classes are unbalanced",
                        ],
                        "a": 2,
                        "whys": [
                            r"Too shallow would show up as training error, and the training accuracy is exactly $1.0$. The tree has more than enough depth; that is the problem, not the cure.",
                            r"Both halves come from the same uniform square, the lab's `make_ring_data`; the split is by row order, not by region. There is no region the training rows failed to cover.",
                            r"That is what fitting every training label means when a tenth of them are noise: the noise gets a region, and the region is wrong for everyone else.",
                            r"Gini has no preference for either class; it is symmetric in the label shares. And the gap appears with entropy too, because it is caused by capacity, not by the criterion.",
                        ],
                        "why": r'''
A tree with enough depth can give any single training point a leaf to itself, and a leaf predicts its label for the whole rectangle it covers. The lab flips one label in ten, so seventeen of the training rows are marked wrongly, each ends up alone in a rectangle that says the wrong thing, and every held-out point that lands in one of those rectangles is misclassified. The training set cannot show this, because on the training set the rectangles are right by construction.
''',
                    },
                    {
                        "q": r"Bagging already grows each tree on a different bootstrap sample. What does restricting each split to a random subset of the features add?",
                        "opts": [
                            r"It is what makes the trees differ at all, since a tree grown on the same rows is deterministic and bootstraps mostly overlap",
                            r"It lowers the correlation between the trees' errors, which is the floor that averaging on its own can never get beneath",
                            r"It lowers each tree's bias, since a tree that sees fewer features at a time has fewer ways to overfit its own sample",
                            r"It stops the vote from tying, because trees built from different features cannot all return the same label at once",
                        ],
                        "a": 1,
                        "whys": [
                            r"Bootstraps differ in about a third of their rows, which is plenty to make the trees differ; they do not differ enough. The feature restriction is about how alike their mistakes are, not whether they are identical.",
                            r"With correlation $\rho$ the average of $B$ trees has variance $\rho\sigma^2 + (1-\rho)\sigma^2/B$, and only the first term is left when $B$ is large.",
                            r"Restricting features raises each tree's bias, if anything: a node that cannot see the best feature makes a worse cut. The forest accepts that for the drop in correlation, and the vote recovers what the single tree lost.",
                            r"Ties are broken by the smaller label and have nothing to do with feature choice; twenty-five trees can agree unanimously whatever they were built from. The restriction changes how often they agree wrongly together.",
                        ],
                        "why": r'''
The average of $B$ estimates with pairwise correlation $\rho$ has variance $\rho\sigma^2 + (1-\rho)\sigma^2/B$. More trees shrink the second term and leave the first alone, so the correlation is the floor. Trees grown on overlapping bootstraps all reach for the same strong split first and make the same mistakes. Forcing each node to choose among a random subset of features makes the trees build differently, lowers $\rho$, and lowers the floor with it.
''',
                    },
                    {
                        "q": r"Four points at the corners of a square are labelled by whether their two coordinates differ. What does the lab's tree do with them?",
                        "opts": [
                            r"Every candidate split has gain $0$, so the zero-gain rule makes the root a leaf, though a depth-2 tree would fit them exactly",
                            r"It grows to depth $2$ and fits them, because the gain at the second level is positive even though the first level's gain is not",
                            r"It raises, because a node whose labels are not pure and whose best split has no gain has no stopping rule to fall back on",
                            r"It picks the split whose children have the highest entropy, since with no gain to compare, that is the next criterion in the line",
                        ],
                        "a": 0,
                        "whys": [
                            r"Both children of either cut hold one $0$ and one $1$, as mixed as the parent, and the greedy search cannot see that the next cut would finish the job.",
                            r"The second level is never reached: the search is greedy and stops when the best single cut removes no impurity, whatever the cuts beneath it might have done.",
                            r"Zero gain is itself a stopping rule in the lab's tree, alongside depth, sample count and purity, and the node becomes a leaf predicting its tie-broken majority. Nothing raises.",
                            r"There is no secondary criterion; high child entropy is the opposite of what a split is for, and a search that preferred it would be choosing the worst cut rather than the least bad.",
                        ],
                        "why": r'''
This is the exclusive-or, and it exposes the greedy search. Any single axis-aligned cut sends one $0$ and one $1$ each way, so the weighted child impurity equals the parent's and the gain is exactly zero for every candidate. The lab's tree treats a non-positive gain as a reason to stop, so the root becomes a leaf, and the tie between two $0$s and two $1$s goes to the smaller label. A tree that cut twice would separate all four points; the search never looks two moves ahead.
''',
                    },
                    {
                        "q": r"A learner builds each of the forest's 25 trees with its own `random.Random(self.seed)`, freshly constructed inside the loop. Every accuracy test passes. What has gone wrong?",
                        "opts": [
                            r"Nothing: seeding each tree the same way is what makes the forest reproducible, and the reproducibility tests pass",
                            r"The trees are decorrelated too well, so the vote averages away the signal along with the noise it was meant to remove",
                            r"All 25 trees draw the same rows and the same feature subsets, so the forest is one tree repeated and the vote is its opinion",
                            r"The bootstraps overlap completely, but the feature subsets still differ, so the forest loses only part of its variance reduction",
                        ],
                        "a": 2,
                        "whys": [
                            r"Reproducibility needs the whole forest to be a function of the seed, which one shared generator provides. Identical trees are reproducible and useless, and the accuracy tests passing is why the defect hides.",
                            r"Identical trees are the opposite of decorrelated: their errors have correlation $1$, the variance floor is the full $\sigma^2$, and the average buys nothing at all.",
                            r"A `random.Random` built from the same seed produces the same stream every time, so each tree's `randrange` and `sample` calls return identical answers.",
                            r"The feature subsets are drawn from the same stream as the bootstrap, so they are identical too. Nothing differs between the trees, not the rows and not the features.",
                        ],
                        "why": r'''
A generator seeded with the same number replays the same sequence, so every tree's bootstrap indices and per-node feature draws come out identical, and the forest is a single tree voting 25 times. Its accuracy is that tree's accuracy, which can still clear a threshold, so the failure is silent. The lab builds one `random.Random(seed)` for the forest and passes that object to each tree, so the draws form one stream that differs from tree to tree and is still fixed by the seed.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Groups nobody labelled, and the direction that holds the most",
                    "minutes": 12,
                    "body": r'''
A hundred and twenty measurements of something, two numbers each, and no labels at all. Plotted, they fall into three clumps, and you would like a program to see the three clumps too: to pick three centres and say which points belong to which. What makes one choice of centres better than another? Look at a candidate: three centres, every point joined by a line to the nearest of them. A good choice has short lines, so the natural score is the sum of their squared lengths, the within-cluster sum of squares, which the lab calls inertia:

$$W = \sum_{i=1}^{n}|x_i - c_{\ell(i)}|^2$$

where $\ell(i)$ is the index of the centre point $i$ is assigned to. Minimising $W$ over centres and assignments together is hard, because there are $k^n$ assignments. But each half on its own is easy, and that is the algorithm.

## Two easy halves

Fix the centres and ask for the best assignment. Each point's term in $W$ depends only on which centre it is assigned to, so give it the nearest one; nothing else can lower its term. Fix the assignment and ask for the best centres. Cluster $j$'s contribution is $\sum_{i \in j}|x_i - c_j|^2$, and differentiating with respect to $c_j$ gives $-2\sum_{i \in j}(x_i - c_j)$, which is zero when $c_j$ is the mean of its points. So Lloyd's algorithm alternates: assign to nearest, move each centre to the mean, repeat. Neither step can raise $W$, because each is the exact minimiser of its own half with the other half held still. And since there are finitely many assignments and $W$ never rises, an assignment must eventually repeat, at which point nothing moves and the loop stops. Four points on a line, with two centres that both start at the left end:

```python
X = [[0.0], [2.0], [10.0], [12.0]]
centres = [[0.0], [2.0]]
labels = None
for step in range(10):
    new_labels = [min(range(2), key=lambda k: (p[0] - centres[k][0]) ** 2) for p in X]
    if new_labels == labels:
        break
    labels = new_labels
    centres = [[sum(X[i][0] for i in range(4) if labels[i] == k) / labels.count(k)] for k in range(2)]
    print(f"step {step}: labels {labels} -> centres {[c[0] for c in centres]}")
inertia = sum((X[i][0] - centres[labels[i]][0]) ** 2 for i in range(4))
print("inertia:", inertia)
```

The first assignment gives the left centre one point and the right centre three, the means move to $0$ and $8$, the reassignment hands $2$ across to the left, the means settle at $1$ and $11$, and the next assignment changes nothing. The inertia is $4$, one unit from each point. The lab's `kmeans` stops on exactly that signal, an assignment equal to the previous one, and keeps a centre where it was if its cluster empties rather than dividing by zero.

## Why the start matters

Lloyd's algorithm finds a local minimum, and which one depends on where it began. Put two of the three centres inside one clump and the third between the other two, and the algorithm will split the first clump in half, merge the other two, and stop, because no single step improves on that. Uniform random starts do this more often than you would expect: with three equal clumps, the chance that three uniform picks land one in each is $6/27$, under a quarter.

k-means++ fixes the start by making later centres prefer points far from earlier ones. Pick the first centre uniformly. Then, for every point, compute $D^2$, the squared distance to its nearest chosen centre, and pick the next centre with probability proportional to $D^2$:

```python
X = [[0.0], [2.0], [10.0], [12.0]]
centres = [X[0]]
weights = [min((p[0] - c[0]) ** 2 for c in centres) for p in X]
total = sum(weights)
print("squared distances to the nearest centre:", weights)
print("probability of each point being the next centre:", [round(w / total, 3) for w in weights])
```

With $0$ chosen, the point $2$ has $D^2 = 4$ against $100$ and $144$ for the far pair, so the next centre comes from the far pair with probability $0.98$. The squaring is what makes it decisive: a point twice as far is four times as likely. To draw with those weights, take `rng.random() * total` as a target and walk the list accumulating weights until the running sum reaches it, which is what the lab asks for so that a seed reproduces a start.

Inertia is a score for comparing runs at the same $k$ and nothing else. Add a centre and every point's nearest centre is at least as near, so $W$ falls, and at $k = n$ it is zero. The lab's test that $k = 2$ costs more than $k = 3$ is a check on the arithmetic, not a way of choosing $k$.

## One number per point, chosen well

The second problem is different. Twenty-five points lie exactly on a line through the plane, tilted along the direction $(0.6, 0.8)$. Two numbers describe each point, but one would do: its position along the line. The line is the direction of the data's spread, and principal component analysis is the search for that direction when it is not visible. Centre the data first, subtracting each column's mean, so that directions are measured from the middle of the cloud. The projection of a centred point $x$ onto a unit vector $v$ is the number $v \cdot x$, and the spread of those numbers over the data is their variance:

$$\text{Var}(v \cdot x) = \frac{1}{n-1}\sum_i (v \cdot x_i)^2 = v^T\left(\frac{1}{n-1}\sum_i x_i x_i^T\right)v = v^T C v$$

The matrix in the middle is the covariance matrix, and $v^T C v$ is the variance of the data seen along $v$. We want the unit $v$ that makes it largest. At a maximum on the unit sphere the gradient of the objective, $2Cv$, must point along the gradient of the constraint $|v|^2 = 1$, which is $2v$; so $Cv = \lambda v$ for some number $\lambda$. The best direction is an eigenvector of $C$, and the variance it achieves is $v^T C v = v^T \lambda v = \lambda$: its eigenvalue. The first principal component is the eigenvector with the largest eigenvalue, the second is the largest among directions perpendicular to it, and so on. Since the trace of $C$ is the sum of the per-column variances and also the sum of the eigenvalues, $\lambda_j / \text{trace}(C)$ is the share of the total variance the $j$th component explains.

The $n - 1$ is deliberate. The deviations are measured from the sample mean, which sits closer to these particular points than the true mean does, so $\sum(x - \bar{x})^2$ comes out short by a factor of $(n-1)/n$ on average; dividing by $n - 1$ instead of $n$ corrects it. Here is the lab's example by hand:

```python
X = [[1.0, 2.0], [3.0, 6.0], [5.0, 10.0]]
n = len(X)
means = [sum(row[j] for row in X) / n for j in range(2)]
print("means:", means)
deviations = [[row[j] - means[j] for j in range(2)] for row in X]
print("deviations:", deviations)
C = [[sum(d[i] * d[j] for d in deviations) / (n - 1) for j in range(2)] for i in range(2)]
print("sample covariance:", C)
```

The second column is twice the first, the deviations say so, and the covariance matrix has a second row twice its first: rank one. Its eigenvalues are $20$ and $0$, its top eigenvector is $(1, 2)/\sqrt{5}$, and a single number per point, the projection onto that direction, loses nothing.

## Finding the eigenvector by repetition

There is no elimination for eigenvectors; the standard tools are iterative, and the simplest is to multiply by $C$ over and over. Write a start vector in the eigenvector basis, $v_0 = a u_1 + b u_2$, with $\lambda_1 > \lambda_2$. Then

$$C^k v_0 = a\lambda_1^k u_1 + b\lambda_2^k u_2 = \lambda_1^k\left(a u_1 + b\left(\frac{\lambda_2}{\lambda_1}\right)^k u_2\right)$$

Normalise after each multiplication and the $\lambda_1^k$ is scaled away, leaving a vector whose $u_2$ part shrinks by the factor $\lambda_2/\lambda_1$ every step. On $\begin{pmatrix}2 & 1\\ 1 & 2\end{pmatrix}$, whose eigenvalues are $3$ along $(1, 1)$ and $1$ along $(1, -1)$, the error should fall by a third per step, and it does:

```python
import math

A = [[2.0, 1.0], [1.0, 2.0]]
v = [1.0, 0.0]
target = [1 / math.sqrt(2), 1 / math.sqrt(2)]
for step in range(6):
    w = [sum(a * x for a, x in zip(row, v)) for row in A]
    norm = math.sqrt(sum(x * x for x in w))
    v = [x / norm for x in w]
    error = math.sqrt(sum((a - b) ** 2 for a, b in zip(v, target)))
    print(f"step {step}: v = ({v[0]:.4f}, {v[1]:.4f})  distance to target {error:.5f}")
Av = [sum(a * x for a, x in zip(row, v)) for row in A]
print("Rayleigh quotient v^T A v =", round(sum(a * b for a, b in zip(v, Av)), 6))
```

The eigenvalue comes from the Rayleigh quotient $v^T C v$ at the end, which is the variance along $v$, the same expression as before. Two things the derivation warns about. The rate is the gap: with eigenvalues $3$ and $2.9$ the error shrinks by $0.967$ per step, and reaching $10^{-6}$ takes about four hundred steps rather than thirteen. And the start must contain some $u_1$, $a \ne 0$, or there is nothing for the iteration to amplify. On a zero matrix every product is zero, the norm is zero, and the lab returns eigenvalue $0.0$ rather than dividing by it.

## The next component, and a trap

Having found $\lambda_1$ and $u_1$, subtract them out: $B = C - \lambda_1 u_1 u_1^T$. Then $B u_1 = \lambda_1 u_1 - \lambda_1 u_1 (u_1 \cdot u_1) = 0$ and $B u_2 = \lambda_2 u_2 - 0$, because $u_1 \cdot u_2 = 0$. The first component has been flattened to nothing and the second is now dominant, so the same iteration on $B$ finds it. That is Hotelling deflation:

```python
import math
import random

A = [[2.0, 1.0], [1.0, 2.0]]
u1 = [1 / math.sqrt(2), 1 / math.sqrt(2)]
B = [[A[i][j] - 3.0 * u1[i] * u1[j] for j in range(2)] for i in range(2)]
print("deflated matrix:", [[round(x, 4) for x in row] for row in B])
print("B times (1,1)/sqrt(2):", [round(sum(b * x for b, x in zip(row, u1)), 12) for row in B])

rng = random.Random(0)
v = [rng.gauss(0, 1) for _ in range(2)]
for _ in range(50):
    w = [sum(b * x for b, x in zip(row, v)) for row in B]
    norm = math.sqrt(sum(x * x for x in w))
    v = [x / norm for x in w]
Bv = [sum(b * x for b, x in zip(row, v)) for row in B]
print("from a random start: v =", [round(x, 4) for x in v], "eigenvalue", round(sum(a * b for a, b in zip(v, Bv)), 6))
```

The trap is on the second printed line. Start the iteration on $B$ from $(1, 1)/\sqrt{2}$, a tidy-looking choice, and the product is the zero vector, because that start is $u_1$ itself and $B$ annihilates it. The all-equal start has $a = 0$ in the deflated basis, with nothing to amplify, and the lab's zero-norm guard would report an eigenvalue of $0$ where the answer is $1$; its deflation test would fail. The lab draws the start from a seeded Gaussian, which is orthogonal to the answer with probability zero. Projection finishes the job: centre each row on the column means, dot it with each component, and the variance of the scores along component $j$ is $\lambda_j$, which the lab checks on the line data.

## The mistake, and where the ideas stop

The mistake with k-means is trusting one run. It converges every time and to a local minimum every time, and the printed inertia is a number, so it looks like an answer. k-means++ makes the bad minima rarer, not impossible; the honest practice is several seeds and the lowest inertia among them at the same $k$. The mistake with PCA is skipping the centring, or the scaling: a column measured in millimetres has a variance a million times that of the same column in metres, and PCA, which sees variance and nothing else, will hand it the first component regardless of whether it means anything.

Both methods have shapes they cannot see. k-means partitions space into cells around the centres, each convex, so the ring data from the last module is carved into wedges rather than a disc and a band, and clusters of very different sizes or spreads are mis-cut at the boundary. PCA is linear: a curved sheet of data gets a flat plane through it. And power iteration is only as fast as the eigenvalue gap; when two components hold nearly equal variance it crawls, and when they hold exactly equal variance the direction it reports is whichever the start favoured.

In the lab, *k-means++ and PCA from first principles*, you will write the $D^2$ seeding, Lloyd's loop with its stopping rule, the sample covariance, power iteration from a seeded start, deflation and projection, and recover the three blobs at $k = 3$ and the line direction $(0.6, 0.8)$ with eigenvalues $3.385$ and $0$.
''',
                },
            ],
            "quiz": {
                "title": "Centres, means and eigen-directions",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Why can an iteration of Lloyd's algorithm never raise the inertia?",
                        "opts": [
                            r"Because k-means++ places the starting centres well enough that every later move is an improvement on the last",
                            r"Because each half-step exactly minimises its own variable with the other held fixed: nearest centre, then the mean",
                            r"Because each centre moves only a short distance per iteration, so the assignment can drift but never jump",
                            r"Because there are finitely many assignments, so the algorithm must revisit one and stop before the score can ever rise",
                        ],
                        "a": 1,
                        "whys": [
                            r"Monotone descent holds from any start, good or bad; the seeding decides which minimum is reached, not whether the path down is monotone.",
                            r"Reassigning a point to its nearest centre cannot increase its own term, and the mean minimises the summed squared distance of a fixed set of points.",
                            r"A centre moves all the way to the mean of its cluster in one step, which can be far. The guarantee comes from where it moves to, not how far.",
                            r"Finiteness is why the loop terminates, given that inertia never rises; it does not on its own stop the score from rising. The order of the argument matters.",
                        ],
                        "why": r'''
With centres fixed, giving each point its nearest centre minimises that point's term and touches no other. With assignments fixed, the derivative of $\sum|x_i - c|^2$ is zero at the mean, which is therefore the best centre for those points. Each half-step is exact for its half, so $W$ cannot rise. Since $W$ never rises and there are finitely many assignments, an assignment must repeat, and the loop stops there.
''',
                    },
                    {
                        "q": r"A run at $k = 3$ reports inertia $45$; a run on the same data at $k = 6$ reports $20$. What does the comparison tell you?",
                        "opts": [
                            r"That $k = 6$ describes the data better, because its centres sit less than half as far from their points on average",
                            r"That $k = 6$ is overfitting, so the smaller inertia is a warning sign and $k = 3$ should be preferred",
                            r"That the data has three real clusters, because the drop from $45$ to $20$ is smaller than a halving would be",
                            r"Nothing about which $k$ is right: extra centres can only lower the inertia, and at $k = n$ it reaches exactly zero",
                        ],
                        "a": 3,
                        "whys": [
                            r"Lower inertia at a larger $k$ is guaranteed by the arithmetic, not earned by the fit; six centres on three clumps split clumps, and the score still drops.",
                            r"Overfitting is a reasonable worry, but inertia cannot diagnose it, because a smaller inertia is what any larger $k$ produces, right or wrong.",
                            r"The size of the drop is the elbow heuristic, and it needs the whole curve of inertia against $k$, not two points; two numbers cannot show a bend.",
                            r"Each point's nearest centre at $k = 6$ is at least as near as at $k = 3$, so the total cannot be higher whatever the structure.",
                        ],
                        "why": r'''
Adding a centre gives every point a nearest centre at least as close as before, so inertia falls monotonically in $k$ and is zero when every point is its own centre. That makes it a score for comparing runs at the same $k$, where a lower value means a better local minimum, and not for comparing across $k$. Choosing $k$ needs something else: an elbow in the curve, a held-out criterion, or knowledge of the problem.
''',
                    },
                    {
                        "q": r"The sample covariance divides by $n - 1$ rather than $n$. What is the reason?",
                        "opts": [
                            r"The deviations are from the sample mean, which sits nearer the data than the true mean, so their squared sum runs short",
                            r"One of the $n$ rows is used up in computing the mean and has to be dropped from the count of independent rows",
                            r"Between $n$ sorted values there are only $n - 1$ gaps, and the variance is a measure of the gaps between neighbouring values",
                            r"With $n = 1$ a division by $n - 1$ would fail, which forces the caller to supply at least two rows before asking",
                        ],
                        "a": 0,
                        "whys": [
                            r"The sample mean is the point that minimises $\sum(x - m)^2$, so the sum around it is at most the sum around the true mean, and the shortfall averages one $\sigma^2$.",
                            r"This is the degrees-of-freedom slogan, and it points at the right number for the wrong reason: no row is dropped, all $n$ deviations are summed, and the correction is to the divisor because of the mean's position.",
                            r"Variance is not about gaps between neighbours; two data sets with identical gaps but different spreads about the mean have different variances. The $n - 1$ is not a count of anything in the sorted order.",
                            r"The lab does refuse fewer than two rows, but that is a consequence of the divisor, not its purpose; a divisor chosen to make one-row data fail would be a strange reason to pick a formula.",
                        ],
                        "why": r'''
The sample mean $\bar{x}$ is the value of $m$ that minimises $\sum(x_i - m)^2$, so the sum of squared deviations about $\bar{x}$ is never larger than about the true mean $\mu$, and it is smaller by $n(\bar{x} - \mu)^2$, which averages $\sigma^2$. Dividing by $n$ therefore underestimates $\sigma^2$ by the factor $(n-1)/n$; dividing by $n - 1$ makes the estimate unbiased. The lab's expected eigenvalue $3.385$ depends on this choice, since dividing by $n$ would scale it by $24/25$.
''',
                    },
                    {
                        "q": r"Power iteration on a matrix with eigenvalues $3$ and $1$ cuts its error by a third each step. What happens on a matrix with eigenvalues $3$ and $2.9$?",
                        "opts": [
                            r"It converges faster, because the eigenvalues are larger and each multiplication stretches the vector further along them",
                            r"It converges at the same rate, because the rate depends on the dimension of the matrix and not on its eigenvalues",
                            r"The error shrinks by only $2.9/3$ per step, so reaching the same accuracy now takes about thirty times as many steps",
                            r"It converges to the average of the two eigenvectors, because the iteration cannot tell eigenvalues that close apart",
                        ],
                        "a": 2,
                        "whys": [
                            r"The stretch is normalised away every step; only the ratio of the eigenvalues survives, and a ratio near $1$ is slow whatever the absolute sizes.",
                            r"The dimension sets the cost of each multiplication, not the number of them. The number of steps is set by the eigenvalue gap alone.",
                            r"The $u_2$ component is multiplied by $\lambda_2/\lambda_1$ each step; $(1/3)^k$ and $(0.967)^k$ reach $10^{-6}$ at $k \approx 13$ and $k \approx 410$.",
                            r"Given enough steps it still converges to $u_1$, because $0.967^k$ does tend to zero. Only with exactly equal eigenvalues is the limit direction undetermined.",
                        ],
                        "why": r'''
Expanding the start in the eigenbasis, after $k$ multiplications and normalisations the unwanted component is scaled by $(\lambda_2/\lambda_1)^k$. At $1/3$ that is $10^{-6}$ after thirteen steps; at $2.9/3 = 0.967$ it takes about four hundred and ten. The gap between the top two eigenvalues, not their size or the matrix's dimension, is the whole of the rate, and the lab's `iters=500` default is chosen with such gaps in mind.
''',
                    },
                    {
                        "q": r"After deflating $\begin{pmatrix}2 & 1\\ 1 & 2\end{pmatrix}$ by its top eigenpair, a learner starts power iteration from $(1, 1)/\sqrt{2}$. What is reported?",
                        "opts": [
                            r"Eigenvalue $3$ along $(1, 1)/\sqrt{2}$ again, because the start is already an eigenvector and the iteration leaves it exactly where it is",
                            r"Eigenvalue $1$ along $(1, -1)/\sqrt{2}$ after one step, because the start is orthogonal to the second component",
                            r"An `OverflowError`, because the deflated matrix has a negative entry and the iterates grow without any bound at all",
                            r"Eigenvalue $0.0$: the start is the removed eigenvector, the deflated matrix maps it to zero, and nothing is left to normalise",
                        ],
                        "a": 3,
                        "whys": [
                            r"It was an eigenvector of $C$; deflation is designed so that its eigenvalue under $B$ is exactly $0$, which is what the removal means.",
                            r"The start is $u_1$, which is orthogonal to $u_2$, not the other way about; a start with no $u_2$ component in it cannot be amplified towards $u_2$.",
                            r"The deflated matrix is $\begin{pmatrix}0.5 & -0.5\\ -0.5 & 0.5\end{pmatrix}$, with eigenvalues $1$ and $0$; nothing grows, and normalising each step rules out overflow in any case.",
                            r"$B = C - 3u_1u_1^T$ has $Bu_1 = 3u_1 - 3u_1 = 0$, so the first product is the zero vector and the lab's zero-norm guard returns $0.0$.",
                        ],
                        "why": r'''
Deflation subtracts $\lambda_1 u_1 u_1^T$, so $u_1$ is sent to zero and $u_2$ keeps its eigenvalue. A start equal to $u_1$ has no $u_2$ component to amplify, the first product is the zero vector, and the lab's guard returns eigenvalue $0.0$ where the answer is $1$; the deflation test then fails. This is why the lab seeds the start from a Gaussian rather than an all-equal vector: a random direction has a nonzero $u_2$ component with probability one.
''',
                    },
                    {
                        "q": r"PCA on two columns gives eigenvalues $3.385$ and $0$. Why is the first said to explain $100\%$ of the variance, with the trace as the denominator?",
                        "opts": [
                            r"The eigenvalues of a covariance matrix are normalised to sum to $1$, so each one is already a share of the total on its own",
                            r"The trace is the sum of the per-column variances, and rotating to the eigenbasis keeps that sum, so it equals the eigenvalues' sum",
                            r"The determinant of the covariance matrix is the total variance, and here it equals the first eigenvalue because the second eigenvalue is $0$",
                            r"The components are unit vectors, so the variance along each is a fraction of one, and those fractions add up to the trace",
                        ],
                        "a": 1,
                        "whys": [
                            r"Eigenvalues are variances in the data's own units; here they sum to $3.385$, not $1$. The division by the trace is what turns them into shares.",
                            r"$\text{trace}(C) = \sum_j C_{jj} = \sum_j \text{Var}(x_j)$, and the trace is invariant under the orthogonal change of basis to the eigenvectors, where it is $\sum_j \lambda_j$.",
                            r"The determinant is the product of the eigenvalues, which is $0$ here, and a total variance of $0$ for data that plainly varies is the wrong number.",
                            r"A unit vector fixes the scale of the direction, not of the variance along it; the variance along a unit vector can be any non-negative number, and $3.385$ is one.",
                        ],
                        "why": r'''
The diagonal of the covariance matrix holds each column's variance, so its trace is the total variance in the data. The trace of a matrix equals the sum of its eigenvalues, and for a symmetric matrix that is the statement that an orthogonal rotation preserves total variance. So $\lambda_j/\text{trace}(C)$ is the share of the total that the $j$th component carries, and with the second eigenvalue at $0$ the first carries all of it: the data lies on a line.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Which model to ship, and why the training error cannot say",
                    "minutes": 12,
                    "body": r'''
Twenty points, each an $x$ between $-1$ and $1$ and a $y$ that is $\sin 3x$ plus a little noise. Fit a straight line to them and it misses the wave in the middle; the error on the twenty points is large. Fit a degree-5 polynomial and it follows the wave, with an error several times smaller. Fit a degree-15 polynomial and it threads every point, with an error near zero. By training error the ranking is settled, and it is wrong: the degree-15 fit swings wildly between the points, and on fresh $x$ values it does far worse than the degree 5. Training error cannot rank these, because the same twenty rows chose the weights. More capacity always fits the rows that chose it better; the question is what it does on rows that did not.

## Holding rows out

The obvious repair is to keep some rows back: fit on most, score on the rest, and the score estimates the error on rows the fit never saw. It is an honest estimate and a noisy one. Hold out five rows and the score is an average of five squared errors, which swings with which five they were. Hold out ten and the fit has only ten rows to learn from and is worse than the one you will ship. $k$-fold cross-validation spends the rows more carefully. Shuffle them once, deal them into $k$ folds, and for each fold in turn fit on the other $k - 1$ and score on it. Every row is scored exactly once, by a model that never saw it, and trained on $k - 1$ times; the $k$ scores are averaged. The construction in the lab is a stride over the shuffled order:

```python
import random

n, k = 10, 5
order = list(range(n))
random.Random(7).shuffle(order)
print("shuffled order:", order)
for i in range(k):
    test = sorted(order[i::k])
    train = sorted(index for index in order if index not in test)
    print(f"fold {i}: test {test}  train {train}")
```

Fold $i$ takes positions $i, i + k, i + 2k, \dots$ of the shuffled list, so the folds partition the indices and differ in size by at most one; seventeen rows over four folds come out as $5, 4, 4, 4$. Sorting both index lists afterwards is housekeeping that makes the tests deterministic. With $k = 5$ each fit sees $80\%$ of the rows, close to the full-data model, and the average over five folds is steadier than any one of them.

## Two columns that say the same thing

The lab's data has a second trap. It supplies thirty rows in which $x_2$ is $x_1$ plus noise of size $0.001$, and $y$ depends on $x_1$ and $x_3$ only. Least squares on it returns something like $w_1 = -62$ and $w_2 = 64$. The sum is about $2$, which is the truth, but the split between them is absurd, and it changes completely if a single row is perturbed. The reason is in $X^T X$. Two nearly identical columns make it nearly singular: in the direction $(1, -1)$, where the two coefficients move opposite ways, the matrix has an eigenvalue near zero, because $w_1 x_1 + w_2 x_2$ barely changes when $w_1$ goes up and $w_2$ goes down by the same amount. Solving the normal equation inverts those eigenvalues, so noise in $y$ that projects onto that direction is amplified by a factor near $1/\lambda_{\min}$, which here is in the tens of thousands. The fit is not wrong, in the sense that it minimises the training error; it is unstable, which is variance by another name.

Ridge regression changes the objective. Add a penalty on the size of the weights:

$$\min_w |Xw - y|^2 + \alpha\sum_{j \ge 1} w_j^2$$

Differentiate as in the first module: the first term gives $2X^T(Xw - y)$, the penalty gives $2\alpha w_j$ for each penalised coordinate, and setting the sum to zero gives

$$\left(X^T X + \alpha \tilde{I}\right)w = X^T y$$

where $\tilde{I}$ is the identity with its top-left entry zeroed, so that the intercept is left alone. That is the lab's `ridge_fit`: the normal equation with $\alpha$ added down the diagonal from the second entry on. Adding $\alpha$ to the diagonal adds $\alpha$ to every eigenvalue, so the near-zero one becomes about $\alpha$ and the amplification becomes $1/\alpha$ instead of $1/\lambda_{\min}$:

```python
import random

def solve(A, b):
    n = len(A)
    M = [list(map(float, row)) + [float(b[i])] for i, row in enumerate(A)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[pivot] = M[pivot], M[col]
        M[col] = [v / M[col][col] for v in M[col]]
        for r in range(n):
            if r != col:
                M[r] = [a - M[r][col] * p for a, p in zip(M[r], M[col])]
    return [row[n] for row in M]

def ridge_fit(X, y, alpha):
    Xt = list(zip(*X))
    A = [[sum(a * b for a, b in zip(r, c)) for c in Xt] for r in Xt]
    for i in range(1, len(A)):
        A[i][i] += alpha
    return solve(A, [sum(a * b for a, b in zip(r, y)) for r in Xt])

rng = random.Random(7)
X, y = [], []
for _ in range(30):
    a = rng.gauss(0, 1)
    X.append([1.0, a, a + rng.gauss(0, 0.001)])
    y.append(2.0 * a + rng.gauss(0, 0.5))
for alpha in (0.0, 0.01, 1.0):
    w = ridge_fit(X, y, alpha)
    print(f"alpha={alpha:<5} w1={w[1]:>9.3f}  w2={w[2]:>9.3f}  w1+w2={w[1] + w[2]:.3f}")
```

At $\alpha = 0$ the split is $-118$ against $120$. At $\alpha = 0.01$, a penalty too small to notice on any well-behaved coefficient, it is $0.8$ against $1.2$. At $\alpha = 1$ the two are within a hundredth of each other, which is what two near-identical columns deserve, and the sum has moved from $1.96$ to $1.95$. That last number is the bias: shrinkage pulls every weight a little towards zero, so the sum lands a little short of $2$. A little bias, bought with an enormous drop in variance, which is the trade the module is named for.

The intercept is excluded because it is not a coefficient on anything. It is the level of $y$ when the features are at zero, and shrinking it towards $0$ says the level should be $0$, a claim the data was never asked about. Feature scale matters too: $\alpha$ penalises $w_j^2$ in whatever units $w_j$ happens to have, so a feature measured in kilometres gets a coefficient a thousand times larger than the same feature in metres, and a thousand-times harsher penalty. Standardise before ridge, or the penalty falls unevenly.

Choosing $\alpha$ is what cross-validation is for. The lab's `select_alpha` scores a list of candidates by `cross_val_mse` and takes the lowest, earlier candidates winning ties. On the collinear data the curve dips from $0.290$ at $\alpha = 0$ to $0.260$ at $\alpha = 1$ and climbs to $2.15$ at $\alpha = 100$, where the shrinkage has flattened a real signal; the minimum is interior, and that is the general shape.

## An identity, not an approximation

Why does a flexible model do worse on new data when it does better on the old? Fix one input $x$ where the truth is $f$, and imagine drawing a training set, fitting, and predicting at $x$, over and over. The predictions $\hat f$ scatter; call their mean $\bar f$. Insert and subtract that mean inside the squared error:

$$\mathrm{E}\left[(\hat f - f)^2\right] = \mathrm{E}\left[(\hat f - \bar f)^2\right] + (\bar f - f)^2 + 2(\bar f - f)\,\mathrm{E}\left[\hat f - \bar f\right]$$

The last expectation is zero by the definition of $\bar f$, so the cross term dies, and what remains is the variance, how much the prediction wobbles from one training set to the next, plus the squared bias, how far the average prediction sits from the truth. Bias is the systematic miss a straight line makes against a wave; variance is the wildness of the degree-15 fit. The identity is algebra, and it holds exactly for a finite collection of predictions as long as the same mean is used in all three terms, which is why the lab can hold you to $10^{-9}$. Two predictions, $1$ and $3$, against a truth of $1$: the mean is $2$, the bias squared is $1$, the variance is $1$, and the expected error is $(0 + 4)/2 = 2$.

Three toy predictors at one point, where the truth is $0.8$, show the two terms trading:

```python
import random

rng = random.Random(7)
truth = 0.8
n_sets = 4000

def decompose(predictions):
    mean = sum(predictions) / len(predictions)
    bias2 = (mean - truth) ** 2
    variance = sum((p - mean) ** 2 for p in predictions) / len(predictions)
    expected = sum((p - truth) ** 2 for p in predictions) / len(predictions)
    return bias2, variance, expected

rigid = [0.5 for _ in range(n_sets)]
one_point = [truth + rng.gauss(0, 0.3) for _ in range(n_sets)]
four_points = [truth + sum(rng.gauss(0, 0.3) for _ in range(4)) / 4 for _ in range(n_sets)]
for name, preds in (("rigid", rigid), ("one point", one_point), ("four points", four_points)):
    b2, var, total = decompose(preds)
    print(f"{name:<12} bias^2 {b2:.4f}  variance {var:.4f}  expected error {total:.4f}  sum {b2 + var:.4f}")
```

The rigid predictor always says $0.5$: no variance, all bias. The predictor that reports one noisy observation is unbiased and carries the whole noise variance, $0.09$. Averaging four observations keeps it unbiased and quarters the variance. Capacity moves along the same axis: a more flexible model chases the training set more closely, lowering bias and raising variance, and the total has a minimum somewhere between. In the lab, on the noisy sine, degree 1 comes out as bias squared $0.20$ and variance $0.03$, nearly all systematic miss, and degree 5 as $0.007$ and $1.31$, nearly all wobble. Degree 3 sits between at $0.005$ and $0.033$, and it is the one to ship.

## The way people fool themselves

You have a test set. You try twenty configurations, score each on it, and report the best score. Here are twenty models that cannot possibly know anything, each a coin flip per row:

```python
import random

rng = random.Random(99)
n_test = 50
labels = [rng.randrange(2) for _ in range(n_test)]
fresh_labels = [rng.randrange(2) for _ in range(n_test)]

def coin_flip_model(seed):
    model_rng = random.Random(seed)
    return [model_rng.randrange(2) for _ in range(n_test)]

def accuracy(y_true, y_pred):
    return sum(1 for a, b in zip(y_true, y_pred) if a == b) / len(y_true)

scores = [(accuracy(labels, coin_flip_model(seed)), seed) for seed in range(1000, 1020)]
best_score, best_seed = max(scores)
print(f"best of 20 coin-flip models on the test set: {best_score:.2f} (seed {best_seed})")
print(f"the same model on fresh data:                 {accuracy(fresh_labels, coin_flip_model(best_seed)):.2f}")
```

The best of twenty coin flips scores $0.64$ on the fifty test rows and $0.52$ on fifty fresh ones, because the maximum of twenty noisy estimates is biased upwards, and the estimate you reported was the maximum. The moment the test set is used to choose, it is no longer held out; the choice was fitted to it, and its score is a training score for that choice. The remedy is the structure the capstone enforces: split once, tune by cross-validation inside the training half only, fit the winner on all of the training half, and touch the test rows exactly once, for the number you report. The same discipline applies to scaling. A `Scaler` fitted on all rows before the split has seen the test rows' means, and inside a cross-validation loop it has to be refitted per fold, on that fold's training rows, or the held-out fold has leaked into the fit.

## Where it stops holding

Cross-validation assumes the rows are exchangeable: any row is as good a stand-in for the future as any other. For a time series that is false, because a random fold puts next week in the training set and last week in the test; for data with groups, several rows per patient, it is false too, and a patient split across train and test is a leak. The estimate also has variance of its own, and $k$ trades it off: larger $k$ means each fit is closer to the final model and the folds are smaller and noisier. The decomposition above is for squared loss against the true function; against noisy targets an irreducible term, the noise variance, is added, and for a $0$-$1$ loss the split is not clean at all. And ridge assumes that a shrinkage target of zero is sensible, which it is for standardised features and not for raw ones.

In the lab, *Cross-validation, ridge, and a bias-variance decomposition*, you will build `k_folds` by the stride, `ridge_fit` with the intercept unpenalised, `cross_val_mse` and `select_alpha`, and `bias_variance`, which fits eighty independent training sets and returns three numbers of which the first two must sum to the third to nine decimal places.
''',
                },
            ],
            "quiz": {
                "title": "Held out, shrunk, and decomposed",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Training error falls as the polynomial degree rises, at every degree. Why is it unable to choose between the degrees?",
                        "opts": [
                            r"Training error is biased low by exactly the noise variance, so subtracting that constant would restore it as a selection criterion",
                            r"Training error is too noisy to rank models, and only averaging it over many training sets brings it down to a usable estimate",
                            r"The rows being scored are the rows that chose the weights, so the score measures memorisation, and more capacity memorises better",
                            r"Training error uses squared loss, which rewards the interpolating fit; an absolute loss would rank the degrees correctly",
                        ],
                        "a": 2,
                        "whys": [
                            r"The gap between training and true error is not a constant; it grows with capacity, which is exactly why it cannot be corrected by subtraction. It is smallest for the line and largest for the interpolant.",
                            r"Averaging training error over training sets would still average a number that falls with degree. The noise is not the problem; the optimism is, and it is systematic.",
                            r"A degree-15 polynomial can pass through twenty points exactly, so its training error is near zero however badly it behaves between them.",
                            r"An absolute loss on the training rows is also zero for a fit that passes through every point. The loss function does not change who chose the weights.",
                        ],
                        "why": r'''
The weights were chosen to minimise error on these rows, so their error on these rows is the smallest any model of that capacity can reach, and a larger capacity reaches smaller still. That optimism grows with capacity rather than staying constant, so it cannot be corrected away; it can only be avoided, by scoring on rows that had no hand in the fit. That is what a held-out fold provides.
''',
                    },
                    {
                        "q": r"Compared with a single train/test split, what does $k$-fold cross-validation gain?",
                        "opts": [
                            r"Every row is scored once by a model that did not train on it, and the $k$ scores are averaged, so all rows inform the estimate",
                            r"The model is trained on every row at once while still being scored, because each fold's model sees the rows of all the other folds",
                            r"The best fold's score can be reported, which is a fairer number than the score of one arbitrary split would have been",
                            r"It produces $k$ different models, and shipping the one with the lowest fold error gives a better final model than a single fit",
                        ],
                        "a": 0,
                        "whys": [
                            r"Each fold's model is fitted on $k - 1$ folds and scored on the $k$th, so no row is scored by a model that trained on it, yet every row is scored.",
                            r"No row is ever both trained on and scored by the same model; that would be the leak the method exists to prevent. Every model still sees only $k - 1$ folds.",
                            r"Reporting the best fold is the same selection-on-the-test error in miniature; the maximum of $k$ noisy scores is biased upwards. The average is the estimate.",
                            r"The $k$ models are scaffolding for the estimate, not candidates; each saw fewer rows than the final model, which is fitted on everything once the choice is made.",
                        ],
                        "why": r'''
A single split scores only the held-out rows and fits on only the rest, so the estimate rests on a fraction of the data and swings with which rows were held out. $k$-fold rotates the held-out role through every fold, so every row is scored exactly once by a model that never saw it, and the average of the $k$ scores uses all the data without a single leak. The models themselves are discarded; the estimate is what they were for.
''',
                    },
                    {
                        "q": r"On the collinear data least squares returns $w_1 = -62$ and $w_2 = 64$. How should the pair be read?",
                        "opts": [
                            r"As evidence of a solver bug, since the generating process used $2$ and $0$ and a correct least squares would recover them",
                            r"As a fit that has failed, because coefficients that large cannot minimise the training error on targets near $2$",
                            r"As two strong effects that happen to oppose, which is a real finding that the penalised fit would wrongly hide",
                            r"The data pins down only $w_1 + w_2$; the split between them is noise amplified by a near-zero eigenvalue of $X^T X$",
                        ],
                        "a": 3,
                        "whys": [
                            r"Least squares cannot recover $2$ and $0$ from columns it cannot tell apart; any pair summing to about $2$ fits equally well, and the solver is correctly reporting one of them.",
                            r"It does minimise the training error, which is why it is dangerous; the huge opposite coefficients cancel on the training rows and only misbehave on rows where $x_2 - x_1$ differs.",
                            r"Opposite effects of that size on two near-identical columns are not a finding; they are the fingerprint of an ill-conditioned system, and perturbing one row would flip their signs.",
                            r"With $x_2 \approx x_1$, moving $w_1$ up and $w_2$ down by the same amount leaves $w_1x_1 + w_2x_2$ almost unchanged, so the direction $(1, -1)$ costs nothing and is set by noise.",
                        ],
                        "why": r'''
Two nearly identical columns give $X^T X$ an eigenvalue near zero along $(1, -1)$, the direction in which the two coefficients trade against each other. The normal equation divides by that eigenvalue, so whatever noise in $y$ points that way is amplified enormously. The sum $w_1 + w_2$ lives along the well-determined direction and comes out near the true $2$; the difference is arbitrary. Ridge adds $\alpha$ to the small eigenvalue and the difference settles, at $\alpha = 1$ to two coefficients of about $0.96$ each.
''',
                    },
                    {
                        "q": r"The lab holds $\text{bias}^2 + \text{variance} = \text{expected error}$ to $10^{-9}$. What makes the cross term in the expansion vanish exactly?",
                        "opts": [
                            r"The noise added to the training targets has mean zero, so its contribution to the cross term averages out over the sets",
                            r"Variance and bias are both measured against the same mean prediction, so the deviations from it sum to zero by construction",
                            r"The eighty training sets are drawn independently of each other, so the covariance between any two of their predictions is zero",
                            r"The predictions are evaluated on a grid, and summing over the grid cancels the positive and negative errors",
                        ],
                        "a": 1,
                        "whys": [
                            r"The noise being centred matters for whether the fits are unbiased, not for the identity; the cross term is $2(\bar f - f)$ times the mean of $\hat f - \bar f$ and vanishes for any set of predictions, noisy or not.",
                            r"$\bar f$ is defined as the mean of the $\hat f$ values, so the deviations $\hat f - \bar f$ sum to exactly zero, whatever the values are.",
                            r"Independence of the training sets is not used anywhere in the identity, which is a statement about one list of numbers and its mean. It would hold for eighty identical training sets too.",
                            r"The identity holds at every single grid point separately, before any summing; the lab's averaging over the grid is done to each of the three terms alike.",
                        ],
                        "why": r'''
Insert and subtract the mean prediction: $(\hat f - f)^2 = ((\hat f - \bar f) + (\bar f - f))^2$. The square expands into the variance term, the bias term, and $2(\bar f - f)(\hat f - \bar f)$. Averaged over the training sets, $\bar f - f$ is a constant and $\hat f - \bar f$ averages to zero because $\bar f$ is that average. That is pure algebra on a finite list of numbers, which is why the lab can demand equality to nine decimal places rather than approximate agreement.
''',
                    },
                    {
                        "q": r"Degree 1 gives bias squared $0.20$ and variance $0.03$; degree 5 gives $0.007$ and $1.31$; degree 3 gives $0.005$ and $0.033$. Which to ship, and on what basis?",
                        "opts": [
                            r"Degree 5, because its bias is the smallest, and bias is the systematic error that no amount of data can ever remove",
                            r"Degree 1, because its variance is nearly as low as degree 3's, and a simpler model is preferable at equal variance",
                            r"Degree 3, because the expected error is the sum of the two terms, and its sum of $0.038$ is the lowest of the three",
                            r"Degree 3, because it is the median of the three candidates, and the bias-variance curve is symmetric about its minimum",
                        ],
                        "a": 2,
                        "whys": [
                            r"Bias is one term of two. Degree 5 buys its tiny bias with a variance of $1.31$, and its expected error of $1.32$ is the worst of the three.",
                            r"The variances are close but the biases are not: $0.20$ against $0.005$. Simplicity is a tie-breaker, and this is not a tie; the total for the line is $0.23$.",
                            r"Expected squared error is exactly bias squared plus variance, and $0.038$ beats both $0.23$ and $1.32$.",
                            r"Nothing about the curve is symmetric, and the median of three arbitrary candidates is not a criterion. Degree 3 wins on its total, and would still win if the candidates had been $1$, $3$ and $4$.",
                        ],
                        "why": r'''
The decomposition exists so that the two terms can be added: the expected squared error at a point is bias squared plus variance, exactly. Degree 1 totals $0.23$, degree 5 totals $1.32$, and degree 3 totals $0.038$. The straight line cannot bend to the wave and the quintic bends to the noise; the cubic bends enough for the wave and not enough for the noise, and that is the interior minimum the module is about.
''',
                    },
                    {
                        "q": r"Twenty configurations are scored on the test set and the best scores $0.64$. Fresh data gives $0.52$. Which number is honest, and what went wrong?",
                        "opts": [
                            r"The $0.52$: picking the best of twenty on the test set fitted the choice to it, and the maximum of twenty noisy scores is biased up",
                            r"The $0.64$: the test rows were never used to fit any weights, so their score is a held-out score whatever was chosen on them",
                            r"The average of the twenty test scores, since the best one is an outlier and the mean is the unbiased summary of the run",
                            r"Neither: fifty rows is too few for any accuracy to mean anything, and the difference between the two numbers is pure sampling noise",
                        ],
                        "a": 0,
                        "whys": [
                            r"A selection is a fit. Twenty scores on the same fifty rows scatter, the largest scatters upwards, and reporting it reports the scatter.",
                            r"Weights are not the only thing that can be fitted. Picking the configuration with the highest test score is a decision made using the test rows, and the score of that decision is no longer held out.",
                            r"The mean of the twenty is an honest estimate of the average configuration, which is not what is being shipped. The question is the score of the one chosen, and for that only fresh rows are honest.",
                            r"Fifty rows give a noisy estimate, which is precisely why the maximum of twenty of them is biased; the noise is the mechanism, not an excuse to ignore the result. The fresh score is still the one to report.",
                        ],
                        "why": r'''
Each test score is the true accuracy plus noise, and the maximum of twenty such numbers is pulled upwards by the noise alone; the models in the reading were coin flips, and the best of them scored $0.64$. Once the test set has been used to choose, the choice has been fitted to it and its score is a training score for that choice. The honest number is the one from rows that played no part in either fitting or choosing, which is why the capstone tunes by cross-validation inside the training half and touches the test rows once.
''',
                    },
                ],
            },
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
