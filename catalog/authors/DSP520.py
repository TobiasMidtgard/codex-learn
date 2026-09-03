"""DSP520 — Adaptive Filters.

Same authoring rules as CTRL510, which is the model for this file:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

Every number asserted in a lab below was produced by running the reference
solution, not by reading it off a textbook.
"""

COURSE = {
    "id": "DSP520",
    "title": "Adaptive Filters",
    "band": 3,
    "level": "Advanced",
    "prereqs": ["DSP510"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◊",
    "summary": (
        "A fixed filter needs you to know the signal in advance. An adaptive filter "
        "works it out from the data while it runs, and every practical one is a cheap "
        "approximation to the same optimal answer. This course starts at that answer — "
        "the Wiener solution — then descends towards it by gradient, replaces the "
        "gradient with a one-sample guess to get LMS, normalises the step so it stops "
        "depending on how loud the input is, and finally pays for exact least squares "
        "with RLS. The recurring question is the honest one: how fast, and how much "
        "excess error is that speed costing you."
    ),
    "outcomes": [
        "Form the correlation matrix and cross-correlation vector from data, and solve the normal equations for the Wiener filter.",
        "Predict the convergence of steepest descent mode by mode, and derive the step-size bound from the largest eigenvalue.",
        "Implement LMS and normalised LMS, and say precisely what normalisation buys and what it does not.",
        "Implement RLS with a forgetting factor, and trade convergence speed against misadjustment with numbers rather than adjectives.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that cancels an acoustic echo through a room that changes halfway through the call.",
    "reading": [
        "*Adaptive Filter Theory*, Haykin — chapters 2, 5, 6 and 9 cover this course almost exactly.",
        "*Statistical Digital Signal Processing and Modeling*, Hayes — chapter 9, for a gentler route to the same equations.",
        "*Fundamentals of Adaptive Filtering*, Sayed — for the least-squares view of RLS.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Correlation and the Wiener solution",
            "summary": "The optimal filter is the solution of one linear system. Everything later is a way of solving it without ever forming it.",
            "concepts": [
                "The mean-square error $J(w) = \\sigma_d^2 - 2w^\\top p + w^\\top R w$ is a quadratic bowl — one minimum, no local traps.",
                "$R = E[xx^\\top]$ is symmetric, positive semi-definite and Toeplitz for a stationary input; $p = E[dx]$ is the cross-correlation.",
                "The normal equations $Rw = p$, and the Wiener solution $w_o = R^{-1}p$.",
                "The orthogonality principle: at the optimum the residual is uncorrelated with every input sample the filter can see.",
                "Eigenvalue spread $\\chi = \\lambda_{max}/\\lambda_{min}$ measures how badly conditioned the bowl is, and it is set by the input spectrum, not by the filter.",
            ],
            "read": [
                {
                    "title": "Three numbers that were already in the recording",
                    "minutes": 16,
                    "body": r'''
A hands-free unit on a desk. The far-end voice leaves the loudspeaker as $x(n)$, bounces
off the desk and the wall behind it, and comes back into the microphone. What the
microphone hands you is $d(n)$: that echo, plus a little sensor noise. Four thousand
samples of each are on disk. Nobody measured the room, and nobody is going to.

The far end hears $d(n)$ unless something is subtracted from it, and the only material
available to build the subtrahend out of is $x$ itself. Three taps, then:
$y(n) = w_0x(n) + w_1x(n-1) + w_2x(n-2)$. The number that decides whether the call is
bearable is the mean square of what is left, $J(w) = \frac{1}{N}\sum_n (d(n) - y(n))^2$.

The first move most people make is to try some values.

```python
import random


def session(N=4000):
    """4000 samples of far-end signal and the microphone signal it echoes into."""
    far = random.Random(7)
    mic = random.Random(8)
    room = [1.0, -0.5, 0.25]
    x = [far.gauss(0.0, 1.0) for _ in range(N)]
    d = []
    for n in range(N):
        echo = sum(room[k] * x[n - k] for k in range(3) if n - k >= 0)
        d.append(echo + 0.01 * mic.gauss(0.0, 1.0))
    return x, d


def cost(x, d, w):
    """J(w): the mean square of what the far end still hears."""
    total = 0.0
    for n in range(len(x)):
        y = sum(w[k] * x[n - k] for k in range(len(w)) if n - k >= 0)
        total += (d[n] - y) ** 2
    return total / len(x)


x, d = session()
for w in ([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, -0.5, 0.0],
          [0.8, -0.5, 0.25], [1.0, -0.5, 0.25], [1.2, -0.5, 0.25]):
    print(f"w = {str(w):22} J = {cost(x, d, w):.6f}")
```

Switched off, $J$ is `1.323851`. Cancel the direct path alone and it falls to `0.314970`;
add the first reflection and it reaches `0.062948`; the third tap takes it to `0.000099`,
which is the noise the microphone was going to add anyway. Perturbing the leading tap by
$\pm 0.2$ from there costs `0.040349` one way and `0.040531` the other — near enough the
same rise on both sides, and both close to $0.2^2 \times 1.0085 = 0.0403$.

That last coincidence is the whole subject. The cost went up by (the size of the error)
squared, times the input power. It is a parabola, and the three-tap version of a parabola
is a bowl.

## The bowl has an equation, and the equation has a solution

Expand $J$ without deciding anything about $w$ first:

$$J(w) = E\big[(d - w^\top x)^2\big] = E[d^2] - 2w^\top E[dx] + w^\top E[xx^\top]w$$

Three expectations came out of that, and only three. Name them:
$\sigma_d^2 = E[d^2]$, the cross-correlation $p = E[dx]$, and the correlation matrix
$R = E[xx^\top]$. So

$$J(w) = \sigma_d^2 - 2w^\top p + w^\top R w$$

and nothing else about the signals survives. Not their distributions, not their
waveforms, not what anybody was saying — second-order statistics and no more. The optimal
echo canceller for a call cannot depend on anything a correlation cannot see.

The gradient of that expression is $\nabla J = 2Rw - 2p$, and it vanishes where

$$Rw = p$$

These are the normal equations, and $w_o = R^{-1}p$ is the Wiener solution. The derive
unit *The Wiener solution, one tap at a time* walks the same two lines with scalars, so
that the algebra is visible before the matrices arrive.

For the recording above, $R$ and $p$ have to be estimated from the samples, which means
replacing each expectation by an average over the record. The matrix has a shape worth
exploiting: $E[x(n-i)x(n-j)]$ depends on $i - j$ alone when the statistics do not drift,
so an $M \times M$ matrix is described by $M$ numbers, $r(0) \dots r(M-1)$.

```python
import random


def session(N=4000):
    far = random.Random(7)
    mic = random.Random(8)
    room = [1.0, -0.5, 0.25]
    x = [far.gauss(0.0, 1.0) for _ in range(N)]
    d = []
    for n in range(N):
        echo = sum(room[k] * x[n - k] for k in range(3) if n - k >= 0)
        d.append(echo + 0.01 * mic.gauss(0.0, 1.0))
    return x, d


def solve(A, b):
    """Gaussian elimination with partial pivoting, in plain lists."""
    n = len(b)
    aug = [list(row) + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        piv = max(range(i, n), key=lambda t: abs(aug[t][i]))
        aug[i], aug[piv] = aug[piv], aug[i]
        for j in range(i + 1, n):
            f = aug[j][i] / aug[i][i]
            for c in range(i, n + 1):
                aug[j][c] -= f * aug[i][c]
    w = [0.0] * n
    for i in range(n - 1, -1, -1):
        w[i] = (aug[i][n] - sum(aug[i][c] * w[c] for c in range(i + 1, n))) / aug[i][i]
    return w


x, d = session()
N, M = len(x), 3
r = [sum(x[n] * x[n - k] for n in range(k, N)) / N for k in range(M)]
p = [sum(d[n] * x[n - k] for n in range(k, N)) / N for k in range(M)]
R = [[r[abs(i - j)] for j in range(M)] for i in range(M)]
w = solve(R, p)
print("r =", [round(v, 6) for v in r])
print("p =", [round(v, 6) for v in p])
print("w =", [round(v, 6) for v in w])

e = [d[n] - sum(w[k] * x[n - k] for k in range(M) if n - k >= 0) for n in range(N)]
bad = [1.0, 0.0, 0.0]
eb = [d[n] - sum(bad[k] * x[n - k] for k in range(M) if n - k >= 0) for n in range(N)]
for k in range(M):
    good = sum(e[n] * x[n - k] for n in range(k, N)) / N
    poor = sum(eb[n] * x[n - k] for n in range(k, N)) / N
    print(f"lag {k}:  solved {good:+.6f}   w = [1, 0, 0] {poor:+.6f}")
```

The estimates come out as $r = [1.008508, -0.00153, -0.001404]$ and
$p = [1.008694, -0.505133, 0.251074]$, and one elimination on a $3 \times 3$ system
returns $w = [0.999775, -0.498977, 0.249591]$. No search, no iteration, no tuning
parameter. The room was $[1.0, -0.5, 0.25]$, and three lags of correlation were enough
to name it to three decimal places.

## How the answer knows it is the answer

The second half of that listing measures something the first half never asked for. At
$w = [1, 0, 0]$ the residual still correlates with the input at lag 1 at $-0.503604$ and
at lag 2 at $+0.252478$. At the solved weights those correlations read $+0.000000$,
$-0.000971$ and $+0.000333$.

This is the normal equations read backwards. Write out row $k$ of $Rw = p$ and it says
$E[dx(n-k)] = \sum_j w_j E[x(n-j)x(n-k)]$, which rearranges to
$E[e(n)x(n-k)] = 0$ for every lag the filter can reach. A leftover correlation at lag 1
is the filter announcing that $x(n-1)$ still carries information about $d(n)$ that it has
not used — and a tap it could turn to use it. When every such correlation is zero there
is nothing left to gain, and that is the orthogonality principle.

The three numbers are not machine zero, and the reason is worth knowing rather than
rounding away: $r$ and $p$ were estimated with sums that start at $n = k$, while the
residual correlation runs over a slightly different set of edge samples. The mismatch is
a handful of terms out of four thousand, so it lands at $10^{-3}$ — three orders below
the wrong filter, and shrinking as $1/N$.

## The mistake: the cross-correlation is not the filter

Look again at the white-input numbers. $p = [1.008694, -0.505133, 0.251074]$, and dividing
by $r(0) = 1.008508$ gives almost exactly the room. It is very tempting to conclude that
the cross-correlation *is* the answer, and skip the matrix — an instinct reinforced by
every matched-filter argument ever made, and by the fact that it works perfectly here.

It works here because the far end was white noise, which makes $R$ a multiple of the
identity and $R^{-1}$ a division by a scalar. Speech is not white. Drive the same room
with an AR(1) process at $\rho = 0.8$, which is far closer to what a voice channel
carries:

```python
import math
import random


def ar1_session(N=4000, rho=0.8):
    """The same room, driven by a correlated far-end signal instead of white noise."""
    far = random.Random(7)
    mic = random.Random(8)
    room = [1.0, -0.5, 0.25]
    scale = math.sqrt(1.0 - rho * rho)
    x = [0.0] * N
    for n in range(1, N):
        x[n] = rho * x[n - 1] + scale * far.gauss(0.0, 1.0)
    d = []
    for n in range(N):
        echo = sum(room[k] * x[n - k] for k in range(3) if n - k >= 0)
        d.append(echo + 0.01 * mic.gauss(0.0, 1.0))
    return x, d


def solve(A, b):
    n = len(b)
    aug = [list(row) + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        piv = max(range(i, n), key=lambda t: abs(aug[t][i]))
        aug[i], aug[piv] = aug[piv], aug[i]
        for j in range(i + 1, n):
            f = aug[j][i] / aug[i][i]
            for c in range(i, n + 1):
                aug[j][c] -= f * aug[i][c]
    w = [0.0] * n
    for i in range(n - 1, -1, -1):
        w[i] = (aug[i][n] - sum(aug[i][c] * w[c] for c in range(i + 1, n))) / aug[i][i]
    return w


def cost(x, d, w):
    total = 0.0
    for n in range(len(x)):
        y = sum(w[k] * x[n - k] for k in range(len(w)) if n - k >= 0)
        total += (d[n] - y) ** 2
    return total / len(x)


x, d = ar1_session()
N, M = len(x), 3
r = [sum(x[n] * x[n - k] for n in range(k, N)) / N for k in range(M)]
p = [sum(d[n] * x[n - k] for n in range(k, N)) / N for k in range(M)]
matched = [v / r[0] for v in p]
wiener = solve([[r[abs(i - j)] for j in range(M)] for i in range(M)], p)
print("r =", [round(v, 4) for v in r])
print("p / r(0) =", [round(v, 4) for v in matched], " J =", round(cost(x, d, matched), 4))
print("R^-1 p   =", [round(v, 4) for v in wiener], " J =", round(cost(x, d, wiener), 6))
print("do nothing                              J =", round(cost(x, d, [0.0] * 3), 4))
```

The correlation vector, scaled, gives $[0.7604, 0.5118, 0.5055]$ — the middle tap has the
wrong sign — and a residual of `1.1467`. Doing nothing at all scores `0.6628`. The
matched-filter answer is not merely worse than optimal; it is worse than leaving the
canceller switched off, and it would put more echo on the line than the room did.
Solving the system gives $[1.0001, -0.5002, 0.2501]$ and a residual of `9.9e-05`.

What $R^{-1}$ contributes is exactly the correction for the input's own correlation. The
input at lag 1 already resembles the input at lag 0, so a raw correlation credits the
second tap for work the first tap has done. The normal equations say: undo the input's
internal structure, then keep what the input shares with the target.

## Estimating $R$ without breaking it

The lab asks for the **biased** estimate $r(k) = \frac{1}{N}\sum_{n=k}^{N-1}x(n)x(n-k)$,
dividing by $N$ even though only $N - k$ products were added. Dividing by $N - k$ instead
gives an unbiased estimate, and unbiased sounds better, which is why people reach for it.

```python
import math
import random


def is_a_bowl(r):
    """Cholesky by hand: it completes when the Toeplitz matrix is positive definite."""
    M = len(r)
    A = [[r[abs(i - j)] for j in range(M)] for i in range(M)]
    L = [[0.0] * M for _ in range(M)]
    for i in range(M):
        for j in range(i + 1):
            s = A[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                if s <= 0.0:
                    return False
                L[i][i] = math.sqrt(s)
            else:
                L[i][j] = s / L[j][j]
    return True


N, M = 12, 8
biased_bad = unbiased_bad = 0
for seed in range(200):
    q = random.Random(seed)
    x = [q.gauss(0.0, 1.0) for _ in range(N)]
    lag = [sum(x[n] * x[n - k] for n in range(k, N)) for k in range(M)]
    biased_bad += not is_a_bowl([s / N for s in lag])
    unbiased_bad += not is_a_bowl([s / (N - k) for k, s in enumerate(lag)])
print("records where the biased estimate is not a bowl:  ", biased_bad, "of 200")
print("records where the unbiased estimate is not a bowl:", unbiased_bad, "of 200")
```

Across 200 twelve-sample records with eight taps, the biased estimate produced a positive
definite $R$ every time — `0 of 200` failures — and the unbiased estimate failed `51 of
200`. A failed Cholesky means the surface is not a bowl: it has a direction of negative
curvature, so "the minimum" is a saddle and there are weights with arbitrarily negative
predicted error. The biased estimate is the autocorrelation of a real finite sequence, so
it is positive semi-definite by construction; scaling each lag by a different factor
destroys that guarantee. Bias is a small, known, shrinking error; an indefinite $R$ is a
different kind of object.

## Where this stops holding

$R$ and $p$ are constants only if the statistics are. The moment somebody moves, or the
far-end talker changes, the bowl moves and $w_o$ with it — which is why the capstone
switches the room halfway through the call and why nothing in this module can cope with
that on its own.

$R$ can also be singular. If the far-end signal is a single tone, a three-tap filter sees
an input that lives in a two-dimensional subspace, and there is a whole line of weight
vectors with identical error. The sandbox *How fast you sample decides how correlated the
input looks* puts that at $f_{sig} = f_s/2$, where $r(1)/r(0) = \cos\pi = -1$ and the
two-tap matrix collapses. Every algorithm later in this course will drift along that flat
direction without the error changing.

And the model is linear and finite. If the loudspeaker is driven into compression, part of
$d$ is a nonlinear function of $x$ and no choice of $w$ reaches it: the residual has a
floor set by the distortion rather than by the microphone. A room with a 200-sample
reverberation tail is no better served by three taps, and the missing tail appears as
excess error that looks exactly like noise.

## What you are about to build

The lab *Solve the normal equations from a block of data* is the listing above, split into
the pieces that will be reused for the rest of the course: `autocorr(x, M)` for the biased
lags, `toeplitz_R(r)` for the $r[|i-j|]$ matrix, `cross_corr(x, d, M)` for $p$, `wiener`
to put them together and solve, and `predict(x, w)` to run the resulting filter. One check
recovers $[1.0, -0.5, 0.25]$ from white input; another measures the residual correlation
at each lag and insists it has fallen below $10^{-3}$, which is the orthogonality
principle used as a test rather than as a slogan. The last one computes the eigenvalue
spread of $R$ for white and for AR(1) input — around 1 against around 115 — and that
single ratio is what the next three modules are all fighting.
''',
                },
            ],
            "sandbox": {
                "title": "How fast you sample decides how correlated the input looks",
                "visualiser": "spectrum",
                "minutes": 8,
                "initial": {"fsig": 30, "fs": 200},
                "brief": r'''
An adaptive filter never sees a waveform. It sees a sequence of numbers, and the
only thing it can exploit is how those numbers are correlated with each other.

For a sinusoid sampled at $f_s$, the normalised one-lag correlation is exactly
$r(1)/r(0) = \cos(2\pi f_{sig}/f_s)$. That single number is what decides whether
the correlation matrix is well conditioned or nearly singular — so move the two
sliders and watch the sample dots, not the underlying curve.
''',
                "notice": [
                    "Drop $f_{sig}$ to 5 Hz with $f_s$ at 200. Consecutive dots are almost identical: $r(1)/r(0) \\approx 0.99$, which is exactly the strongly correlated input that gives a large eigenvalue spread.",
                    "Set $f_{sig}$ to 100 Hz, exactly half the sample rate. Every sampling instant now falls on a zero crossing, so the dots lie flat on the axis while the curve behind them keeps swinging. The statistic behind that picture is $r(1)/r(0) = \\cos(\\pi) = -1$: whatever the sampling phase, the two-tap correlation matrix is singular and the Wiener solution stops being unique.",
                    "Set $f_{sig} = 50$ with $f_s = 200$: a quarter cycle per sample, so $r(1)/r(0) = 0$. To a two-tap filter this input is white, and its bowl is a perfect circle.",
                ],
            },
            "derive": {
                "title": "The Wiener solution, one tap at a time",
                "minutes": 14,
                "vars": ["J", "w", "w_o", "r", "p", "sigma_d", "rho", "chi", "d", "x"],
                "brief": r'''
Take the smallest possible adaptive filter: a single tap $w$, forming $y = wx$ and
trying to match a desired signal $d$. Write

$$r = E[x^2], \qquad p = E[dx], \qquad \sigma_d^2 = E[d^2]$$

Everything the general case does, this case does with scalars.
''',
                "steps": [
                    {
                        "prompt": "Expand the mean-square error $J(w) = E[(d - wx)^2]$ in terms of $\\sigma_d$, $p$, $r$ and $w$.",
                        "answer": "\\sigma_d^2 - 2 w p + w^2 r",
                        "hint": "Square the bracket first, then take the expectation term by term. $w$ is a constant, so it comes outside.",
                        "deconstruct": [
                            "$(d - wx)^2 = d^2 - 2wdx + w^2x^2$.",
                            "Take expectations: $E[d^2] = \\sigma_d^2$, $E[dx] = p$, $E[x^2] = r$.",
                        ],
                    },
                    {
                        "prompt": "Differentiate $J$ with respect to $w$.",
                        "answer": "2 w r - 2 p",
                        "hint": "It is a quadratic in one variable; $\\sigma_d^2$ does not depend on $w$ at all.",
                        "deconstruct": [
                            "The constant term differentiates to zero.",
                            "$-2wp$ gives $-2p$, and $w^2 r$ gives $2wr$.",
                        ],
                    },
                    {
                        "prompt": "Set the derivative to zero and write the optimal tap $w_o$.",
                        "answer": "\\frac{p}{r}",
                        "hint": "This is the one-dimensional version of $w_o = R^{-1}p$.",
                        "deconstruct": [
                            "$2wr - 2p$ vanishes when $wr = p$.",
                            "Divide by $r$, which is a power and so is strictly positive for any real input.",
                        ],
                    },
                    {
                        "prompt": "Substitute $w_o$ back into $J$ and write the minimum mean-square error.",
                        "answer": "\\sigma_d^2 - \\frac{p^2}{r}",
                        "hint": "Put $p/r$ in place of $w$ in $\\sigma_d^2 - 2wp + w^2r$ and collect the two $p^2/r$ terms.",
                        "deconstruct": [
                            "$-2wp$ becomes $-2p^2/r$ and $w^2 r$ becomes $p^2/r$.",
                            "Those two sum to $-p^2/r$, which is the part of the desired signal the filter managed to explain.",
                        ],
                    },
                    {
                        "prompt": "Now two taps, with a unit-power input whose one-lag correlation is $\\rho$: $R$ has $1$ on the diagonal and $\\rho$ off it, so its eigenvalues are $1 + \\rho$ and $1 - \\rho$. Write the eigenvalue spread $\\chi$ for $0 < \\rho < 1$.",
                        "answer": "\\frac{1+\\rho}{1-\\rho}",
                        "hint": "Spread is the largest eigenvalue divided by the smallest, and for $0 < \\rho < 1$ the larger one is $1 + \\rho$.",
                        "deconstruct": [
                            "The eigenvectors are $[1, 1]$ and $[1, -1]$, giving eigenvalues $1 + \\rho$ and $1 - \\rho$.",
                            "Divide the larger by the smaller.",
                        ],
                    },
                ],
                "closing": r'''
Two things to carry forward. First, the optimum needs only second-order statistics —
no distribution, no model of the signal, just $R$ and $p$. Second, that spread
$\chi$ heads for infinity as $\rho \to 1$, and every gradient method in this course
slows down in direct proportion to it.
''',
            },
            "quiz": {
                "title": "One linear system, and every later algorithm solving it",
                "minutes": 7,
                "questions": [
                    {
                        "q": "$J(w) = \\sigma_d^2 - 2w^\\top p + w^\\top Rw$. What shape is it?",
                        "opts": [
                            "A bowl with a single minimum",
                            "A surface with many local minima",
                            "A saddle",
                            "A plane",
                        ],
                        "a": 0,
                        "why": r"""
Quadratic with $R \succeq 0$, so it is convex: one minimum, no local traps, and gradient
descent cannot get stuck. This is why adaptive filtering works as reliably as it does,
and it is exactly what is lost the moment the filter becomes non-linear. The bowl's
*shape* still matters enormously — an elongated one is what makes convergence slow, which
is module 2.
""",
                    },
                    {
                        "q": "For a stationary input, what structure does $R = E[xx^\\top]$ have?",
                        "opts": [
                            "Symmetric, positive semi-definite and Toeplitz",
                            "Diagonal",
                            "Skew-symmetric",
                            "Upper triangular",
                        ],
                        "a": 0,
                        "why": r"""
Toeplitz because $E[x(n-i)x(n-j)]$ depends only on $i-j$ when the input is stationary —
constant along every diagonal, so the whole matrix is described by one autocorrelation
sequence rather than $M^2$ numbers. That structure is what makes fast solvers such as
Levinson–Durbin possible. It is diagonal only for white input, which is the special case
where every eigenvalue is equal and convergence is fastest.
""",
                    },
                    {
                        "q": "Setting the gradient to zero gives which equations?",
                        "opts": ["$Rw = p$", "$Rp = w$", "$w = R + p$", "$R^\\top R w = p$"],
                        "a": 0,
                        "why": r"""
The normal equations, and $w_o = R^{-1}p$ is the Wiener solution. Everything later in
this course is a way of reaching that same $w_o$ *without* forming $R$, inverting it, or
even knowing it — because in practice the statistics are unknown and non-stationary, and
an $M \times M$ inverse per sample is not affordable.
""",
                    },
                    {
                        "q": "What is $p = E[d\\,x]$?",
                        "opts": [
                            "The cross-correlation between the desired signal and the input",
                            "The autocorrelation of the input",
                            "The power of the desired signal",
                            "The prediction error",
                        ],
                        "a": 0,
                        "why": r"""
It is the only place the *desired* signal enters the problem, and it is what makes the
solution a solution to your problem rather than a generic property of the input. Read the
normal equations that way and they say something plain: undo the input's own correlation
structure ($R^{-1}$) and keep what the input shares with the target ($p$).
""",
                    },
                    {
                        "q": "Why is the Wiener solution unique when $R \\succ 0$?",
                        "opts": [
                            "The cost is strictly convex, so there is exactly one stationary point",
                            "Because $R$ is Toeplitz",
                            "Because the filter is FIR",
                            "It is not — any $w$ with $J(w)$ small enough will do",
                        ],
                        "a": 0,
                        "why": r"""
Strict positive definiteness makes the bowl curve upward in *every* direction, so there
is one stationary point and it is the minimum. If $R$ is merely semi-definite — which
happens when the input does not excite every direction, a narrowband tone into a long
filter, say — there is a flat valley of equally optimal solutions, and the algorithms
will wander along it without the error getting any worse.
""",
                    },
                ],
            },
            "lab": {
                "title": "Solve the normal equations from a block of data",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Estimate $R$ and $p$ from data and solve $Rw = p$.

- `autocorr(x, M)` returns `[r(0), r(1), ..., r(M-1)]` using the **biased**
  estimate $r(k) = \frac{1}{N}\sum_{n=k}^{N-1} x(n)x(n-k)$. Divide by `N` every
  time, not by `N - k`: the biased estimate is the one that keeps $R$ positive
  semi-definite.
- `toeplitz_R(r)` builds the $M \times M$ symmetric matrix whose $(i, j)$ entry is
  `r[abs(i - j)]`.
- `cross_corr(x, d, M)` returns `p`, with $p(k) = \frac{1}{N}\sum_{n=k}^{N-1} d(n)x(n-k)$.
- `wiener(x, d, M)` puts those together and solves the system with
  `np.linalg.solve`.
- `predict(x, w)` runs the FIR filter: $y(n) = \sum_k w_k x(n-k)$, returning an
  array the same length as `x` and treating samples before the start as zero.

`main.py` prints a summary; run it, and the checks read your functions directly.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def autocorr(x, M):
    """Biased autocorrelation estimate: r(k) = (1/N) * sum x(n) x(n-k), k = 0..M-1."""
    x = np.asarray(x, dtype=float)
    r = np.zeros(M)
    # TODO: fill r[k] with the lag-k product sum divided by N.
    return r


def toeplitz_R(r):
    """Build the MxM symmetric Toeplitz matrix whose (i, j) entry is r[|i - j|]."""
    r = np.asarray(r, dtype=float)
    M = r.size
    # TODO: build the matrix.
    return np.zeros((M, M))


def cross_corr(x, d, M):
    """p(k) = (1/N) * sum d(n) x(n-k), for k = 0..M-1."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    p = np.zeros(M)
    # TODO
    return p


def wiener(x, d, M):
    """Solve R w = p for the M-tap Wiener filter."""
    # TODO: build R and p, then np.linalg.solve.
    return np.zeros(M)


def predict(x, w):
    """FIR output y(n) = sum_k w[k] x(n-k), zero before the start of the record."""
    x = np.asarray(x, dtype=float)
    w = np.asarray(w, dtype=float)
    y = np.zeros(x.size)
    # TODO
    return y


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    x = rng.standard_normal(20000)
    h = np.array([1.0, -0.5, 0.25])
    d = np.convolve(x, h)[:20000] + 0.01 * rng.standard_normal(20000)
    w = wiener(x, d, 3)
    print("estimated taps:", np.round(w, 4).tolist())
    print("residual power:", round(float(np.mean((d - predict(x, w)) ** 2)), 8))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def autocorr(x, M):
    """Biased autocorrelation estimate: r(k) = (1/N) * sum x(n) x(n-k), k = 0..M-1."""
    x = np.asarray(x, dtype=float)
    N = x.size
    r = np.zeros(M)
    for k in range(M):
        r[k] = float(np.dot(x[k:], x[:N - k]) / N)
    return r


def toeplitz_R(r):
    """Build the MxM symmetric Toeplitz matrix whose (i, j) entry is r[|i - j|]."""
    r = np.asarray(r, dtype=float)
    M = r.size
    idx = np.abs(np.subtract.outer(np.arange(M), np.arange(M)))
    return r[idx]


def cross_corr(x, d, M):
    """p(k) = (1/N) * sum d(n) x(n-k), for k = 0..M-1."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    N = x.size
    p = np.zeros(M)
    for k in range(M):
        p[k] = float(np.dot(d[k:], x[:N - k]) / N)
    return p


def wiener(x, d, M):
    """Solve R w = p for the M-tap Wiener filter."""
    R = toeplitz_R(autocorr(x, M))
    p = cross_corr(x, d, M)
    return np.linalg.solve(R, p)


def predict(x, w):
    """FIR output y(n) = sum_k w[k] x(n-k), zero before the start of the record."""
    x = np.asarray(x, dtype=float)
    w = np.asarray(w, dtype=float)
    N = x.size
    y = np.zeros(N)
    for k in range(w.size):
        y[k:] += w[k] * x[:N - k]
    return y


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    x = rng.standard_normal(20000)
    h = np.array([1.0, -0.5, 0.25])
    d = np.convolve(x, h)[:20000] + 0.01 * rng.standard_normal(20000)
    w = wiener(x, d, 3)
    print("estimated taps:", np.round(w, 4).tolist())
    print("residual power:", round(float(np.mean((d - predict(x, w)) ** 2)), 8))
'''}],
                "hints": [
                    "`np.dot(x[k:], x[:N - k])` is the whole lag-$k$ sum; no Python loop over samples is needed.",
                    "For the Toeplitz matrix, `np.abs(np.subtract.outer(np.arange(M), np.arange(M)))` is the matrix of $|i - j|$, and indexing `r` with it does the rest.",
                    "In `predict`, adding `w[k] * x[:N - k]` into `y[k:]` shifts by $k$ and pads the front with zeros in one line.",
                ],
                "tests": [
                    {"name": "white noise has no correlation beyond lag zero", "code": r'''
import numpy as np
_rng = np.random.default_rng(7)
_x = _rng.standard_normal(20000)
_r = autocorr(_x, 4)
assert _r.shape == (4,), f"autocorr should return M values, got shape {_r.shape}"
assert abs(_r[0] - 1.0) < 0.05, \
    f"r(0) is the signal power, which is 1 for this input; got {_r[0]:.4f}"
assert abs(_r[1]) < 0.03 and abs(_r[2]) < 0.03, \
    f"white noise is uncorrelated, so r(1) and r(2) should be near zero; got {_r[1]:.4f}, {_r[2]:.4f}"
'''},
                    {"name": "the correlation matrix is symmetric and Toeplitz", "code": r'''
import numpy as np
_R = toeplitz_R(np.array([2.0, 1.0, 0.5]))
assert _R.shape == (3, 3), f"expected a 3x3 matrix, got {_R.shape}"
assert np.allclose(_R, _R.T), "R is symmetric by construction — check your index expression"
assert abs(_R[0, 0] - 2.0) < 1e-12 and abs(_R[0, 1] - 1.0) < 1e-12 and abs(_R[0, 2] - 0.5) < 1e-12, \
    f"the first row should be r(0), r(1), r(2); got {_R[0].tolist()}"
assert abs(_R[2, 0] - 0.5) < 1e-12, \
    f"entry (2,0) is lag 2, so r(2) = 0.5; got {_R[2,0]} — the entry depends on |i-j| only"
'''},
                    {"name": "the Wiener filter recovers a known channel", "code": r'''
import numpy as np
_rng = np.random.default_rng(7)
_x = _rng.standard_normal(20000)
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:20000] + 0.01 * _rng.standard_normal(20000)
_w = wiener(_x, _d, 3)
assert np.max(np.abs(_w - _h)) < 0.01, \
    f"with white input the Wiener taps are the channel taps; expected {_h.tolist()}, got {np.round(_w, 4).tolist()}"
'''},
                    {"name": "the residual is orthogonal to the input", "code": r'''
import numpy as np
_rng = np.random.default_rng(7)
_x = _rng.standard_normal(20000)
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:20000] + 0.01 * _rng.standard_normal(20000)
_w = wiener(_x, _d, 3)
_e = _d - predict(_x, _w)
_N = _x.size
for _k in range(3):
    _c = float(np.dot(_e[_k:], _x[:_N - _k]) / _N)
    assert abs(_c) < 1e-3, \
        f"at the optimum the residual carries no information the filter could still use, so the lag-{_k} correlation should vanish; got {_c:.6f}"
'''},
                    {"name": "correlated input is badly conditioned and white input is not", "code": r'''
import numpy as np
_rng = np.random.default_rng(3)
_v = _rng.standard_normal(40000)
_xa = np.zeros(40000)
for _n in range(1, 40000):
    _xa[_n] = 0.9 * _xa[_n - 1] + _v[_n]
_Ra = toeplitz_R(autocorr(_xa, 8))
_ea = np.linalg.eigvalsh(_Ra)
_spread_ar = float(_ea[-1] / _ea[0])
_rng2 = np.random.default_rng(7)
_Rw = toeplitz_R(autocorr(_rng2.standard_normal(20000), 8))
_ew = np.linalg.eigvalsh(_Rw)
_spread_w = float(_ew[-1] / _ew[0])
assert _spread_ar > 20.0, \
    f"an AR(1) input with rho=0.9 should give a spread near 115; got {_spread_ar:.2f}"
assert _spread_w < 2.0, \
    f"white input should give a spread near 1; got {_spread_w:.2f}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Steepest descent and the step-size bound",
            "summary": "Walk downhill on the error surface. The eigenvalues of R decide both how far you may step and how long the walk takes.",
            "concepts": [
                "The gradient $\\nabla J = 2(Rw - p)$, and the update $w(n+1) = w(n) + \\mu(p - Rw(n))$.",
                "In the eigenvector coordinates the update decouples into scalar recursions with factor $1 - \\mu\\lambda_i$.",
                "Convergence needs $|1 - \\mu\\lambda_i| < 1$ for every mode, so $0 < \\mu < 2/\\lambda_{max}$.",
                "The slowest mode belongs to $\\lambda_{min}$, so the time to converge scales with the eigenvalue spread.",
                "Steepest descent is deterministic: it needs $R$ and $p$, which is exactly what a real system does not have.",
            ],
            "read": [
                {
                    "title": "Two hundred iterations, and the one number that set them",
                    "minutes": 16,
                    "body": r'''
Two taps this time, and the correlation measured off a voice channel rather than off
white noise: neighbouring samples correlate at 0.9, so

$$R = \begin{bmatrix} 1 & 0.9 \\ 0.9 & 1 \end{bmatrix}, \qquad
  p = \begin{bmatrix} 0.5 \\ 0.25 \end{bmatrix}, \qquad \sigma_d^2 = 1$$

Module 1 would finish this in one elimination: $w_o = R^{-1}p = [1.447368, -1.052632]$
and $J_{min} = 0.539474$. Refuse to form the inverse — a 512-tap canceller would be
inverting a $512\times512$ matrix, and later modules will not have $R$ at all — and walk
downhill instead. The gradient of $J(w) = \sigma_d^2 - 2w^\top p + w^\top Rw$ is
$2(Rw - p)$, so a step against half of it is $w \leftarrow w + \mu(p - Rw)$.

Set $\mu$ to half of $2/\lambda_{max} = 2/1.9$, which is what the lab does, and start at
the origin.

```python
R = [[1.0, 0.9], [0.9, 1.0]]
p = [0.5, 0.25]
var_d = 1.0


def step(w, mu):
    """One steepest-descent update: w <- w + mu (p - R w)."""
    Rw = [R[i][0] * w[0] + R[i][1] * w[1] for i in (0, 1)]
    return [w[i] + mu * (p[i] - Rw[i]) for i in (0, 1)]


def J(w):
    Rw = [R[i][0] * w[0] + R[i][1] * w[1] for i in (0, 1)]
    return var_d - 2 * (p[0] * w[0] + p[1] * w[1]) + w[0] * Rw[0] + w[1] * Rw[1]


mu = 0.5 * (2.0 / 1.9)
w = [0.0, 0.0]
print(f"mu = {mu:.6f}")
for n in range(201):
    if n in (0, 1, 2, 5, 10, 25, 50, 100, 200):
        print(f"n = {n:3d}   w = [{w[0]:+.6f}, {w[1]:+.6f}]   J = {J(w):.6f}")
    w = step(w, mu)
```

$J$ falls from `1.000000` to `0.819945` on the first iteration, then to `0.791198`,
`0.721460`, `0.645455` — and by iteration 200 it has reached `0.539474`, which is
$J_{min}$ to six places. Two hundred iterations to do what one elimination did.

## The trace is telling you the answer

Read the weights themselves rather than the cost. At $n = 1$, $w = [0.263158,
0.131579]$, so $w - w_o = [-1.184211, +1.184211]$. At $n = 2$ the difference is
$[-1.121884, +1.121884]$, at $n = 3$, $[-1.062837, +1.062837]$. The two components are
exact negatives of each other from the first iteration onwards, and their magnitude
shrinks by the same factor every time.

```python
R = [[1.0, 0.9], [0.9, 1.0]]
p = [0.5, 0.25]
wo = [1.4473684210526314, -1.0526315789473681]     # R^-1 p, worked out by hand
mu = 0.5 * (2.0 / 1.9)

w = [0.0, 0.0]
print("  n      w0 - wo0     w1 - wo1     sum        along [1,-1]   shrink")
prev = None
for n in range(7):
    v = [w[0] - wo[0], w[1] - wo[1]]
    along = (v[0] - v[1]) / 2
    ratio = "      --" if prev is None else f"{along / prev:+.6f}"
    print(f"{n:3d}  {v[0]:+.6f}   {v[1]:+.6f}   {v[0] + v[1]:+.6f}   "
          f"{along:+.6f}   {ratio}")
    prev = along
    Rw = [R[i][0] * w[0] + R[i][1] * w[1] for i in (0, 1)]
    w = [w[i] + mu * (p[i] - Rw[i]) for i in (0, 1)]
print()
print("1 - mu * 1.9 =", round(1 - mu * 1.9, 12))
print("1 - mu * 0.1 =", round(1 - mu * 0.1, 6))
```

The `sum` column starts at `-0.394737` and is `-0.000000` from iteration 1 onwards. The
`shrink` column reads `+0.947368` at every single step. Two constants have appeared out
of a recursion that was written with no constants in it, and the last two lines print
`0.0` and `0.947368`.

Here is where they come from. Put $v = w - w_o$ into the update and use $Rw_o = p$:

$$v(n+1) = v(n) + \mu\big(p - R(w_o + v(n))\big) = v(n) - \mu Rv(n) = (I - \mu R)\,v(n)$$

So the error is multiplied by the fixed matrix $I - \mu R$ each iteration, and the
directions in which that multiplication is a plain scaling are the eigenvectors of $R$.
For this $R$ they can be read off: $R[1, 1]^\top = [1.9, 1.9]^\top$ and
$R[1, -1]^\top = [0.1, -0.1]^\top$, so the eigenvalues are $\lambda_1 = 1.9$ along
$[1, 1]$ and $\lambda_2 = 0.1$ along $[1, -1]$. Along either one,

$$v(n+1) = (1 - \mu\lambda)\,v(n), \qquad v(n) = (1 - \mu\lambda)^n v(0)$$

which is a one-pole recursion with the pole at $1 - \mu\lambda$. That is the whole of the
sandbox *One mode of the descent as a single pole*: set the radius to $|1-\mu\lambda|$ and
the impulse response you see is a column of the table above.

Now both constants are forced. $\mu$ was set to $1/1.9$, so $1 - \mu\lambda_1$ is exactly
zero and the $[1,1]$ component is annihilated on the first update and can never come back
— which is what the `sum` column is showing. And $1 - \mu\lambda_2 = 1 - 0.1/1.9 =
0.947368$, which is the `shrink` column to six places. The derive unit *Why the step size
is bounded by the largest eigenvalue* builds the same two lines with $R$, $\mu$ and
$\lambda$ left as symbols.

Two hundred iterations, then, were never about the algorithm. They were $\lambda_2 = 0.1$
being nineteen times smaller than $\lambda_1$: $0.947368^{200} = 1.9\times10^{-5}$.

## The bound falls straight out of the same line

Every mode must shrink, so $|1 - \mu\lambda_i| < 1$ for every eigenvalue, which is
$0 < \mu\lambda_i < 2$. All of those have to hold at once, so the largest eigenvalue wins
and

$$0 < \mu < \frac{2}{\lambda_{max}}$$

Nothing about the smallest eigenvalue appears in the bound. It appears in the wait
instead: with $|1-\mu\lambda|^n = e^{n\ln|1-\mu\lambda|} \approx e^{-n\mu\lambda}$ for
small $\mu\lambda$, the mode belonging to $\lambda_{min}$ has time constant
$\tau = 1/(\mu\lambda_{min})$ iterations. The blanks unit *How far you may step, and how
long it takes* is these two facts, one hole each.

## The mistake: turning $\mu$ up towards the bound

The bound is stated as the point at which the algorithm breaks, so it reads like a
throttle: more $\mu$, more speed, right up to the edge. It is tempting because it is true
over the first half of the range, and because $\tau = 1/(\mu\lambda_{min})$ appears to say
so in symbols. Count the iterations instead.

```python
R = [[1.0, 0.9], [0.9, 1.0]]
p = [0.5, 0.25]
wo = [1.4473684210526314, -1.0526315789473681]
bound = 2.0 / 1.9


def outcome(mu, tol=1e-3, cap=20000):
    """Updates needed to come within tol of the Wiener solution, or why not."""
    w = [0.0, 0.0]
    target = tol * (wo[0] ** 2 + wo[1] ** 2) ** 0.5
    for n in range(cap):
        gap = ((w[0] - wo[0]) ** 2 + (w[1] - wo[1]) ** 2) ** 0.5
        if gap < target:
            return str(n)
        if gap > 1e12:
            return "diverges"
        Rw = [R[i][0] * w[0] + R[i][1] * w[1] for i in (0, 1)]
        w = [w[i] + mu * (p[i] - Rw[i]) for i in (0, 1)]
    return "never"


print("mu/bound     mu      |1-mu*1.9|  |1-mu*0.1|  iterations")
for frac in (0.2, 0.5, 0.8, 0.95, 0.99, 1.0, 1.02):
    mu = frac * bound
    print(f"  {frac:4.2f}    {mu:.6f}    {abs(1 - mu * 1.9):.4f}      "
          f"{abs(1 - mu * 0.1):.4f}     {outcome(mu)}")
```

At a fifth of the bound it takes 325 iterations; at half, 128; at 0.8, 79; at 0.95, 66.
Then at 0.99 it takes **250** — worse than half the bound — and at the bound itself,
`never`.

The `|1-mu*1.9|` column explains it and nothing else does. That factor falls to zero at
$\mu = 1/\lambda_{max}$ and then climbs back, negative, reaching $-1$ exactly at the
bound: the fast mode stops decaying and flips sign forever, overshooting the solution by
the same amount every iteration. Past the bound its magnitude exceeds one and the walk
runs away — the sandbox draws that as a pole pushed outside the unit circle, and
$\theta = \pi$ is what the negative sign looks like there. Convergence is governed by
$\max_i|1 - \mu\lambda_i|$, and the best step is the one that equalises the two ends of
the spectrum, $\mu = 2/(\lambda_{max} + \lambda_{min}) = 1.0$ here, giving $\pm 0.9$ and
the 66-iteration row.

Note also that the `|1-mu*0.1|` column barely moves across the whole table: 0.9789 down
to 0.8926. The slow mode is nearly indifferent to $\mu$, which is the honest version of
"turning the step size up does not help".

## Where this stops holding

The exactness of all of this rests on $J$ being a quadratic with a constant $R$. That is
true for a linear filter under a mean-square criterion and stops being true the moment
either assumption goes: a nonlinear filter, or a cost such as mean absolute error, has a
surface with a different shape and the mode decomposition does not exist.

The analysis is also for a *fixed* $R$. If the far-end talker changes, $R$ changes, its
eigenvectors rotate, and the modes you were tracking are no longer modes. Nothing here
diverges, but the trajectory stops matching the geometric prediction.

Most importantly, this algorithm cannot be built. Every update contains $R$ and $p$, and
if you had those you would have solved $Rw = p$ and gone home. Even the step size is
unusable as stated: $\lambda_{max}$ requires an eigendecomposition of a matrix you do not
have. Module 3's answer is to bound it by $\text{trace}(R) = M\sigma_x^2$, which is at
least $\lambda_{max}$ and is measurable as the input power with a running average.

## What you are about to build

The lab *Descend a known error surface* hands you $R$ and $p$ so that the recursion is
all there is to write: `max_step(R)` returning $2/\lambda_{max}$, `mse(R, p, var_d, w)`
returning $J$, and `descend(R, p, mu, iters, w0=None)` returning the whole trajectory
rather than the final answer, because the checks look at how it got there. One of them
walks the list and insists $J$ never rises between consecutive iterations — below the
bound the surface is descended monotonically, and a sign error shows up there before it
shows up anywhere else. Another runs at $1.05\times$ the bound and requires the weights to
exceed $10^3$. The last one measures convergence at $\rho = 0.5$ and $\rho = 0.9$, spreads
of 3 and 19, and asks for a factor of four between them — the same $\lambda_{min}$ that
cost 200 iterations above, charged again.
''',
                },
            ],
            "quiz": {
                "title": "Which eigenvalue is charging you, and for what",
                "minutes": 8,
                "questions": [
                    {
                        "q": "On the bowl with $\\lambda = 1.9$ and $\\lambda = 0.1$, running at $\\mu = 1/1.9$, the weight error after the first update lies exactly along the eigenvector for $\\lambda = 0.1$ and never leaves it. What did that?",
                        "opts": [
                            "Starting at the origin already puts the whole initial error along that eigenvector",
                            "The factor $1 - \\mu\\lambda$ is exactly zero for the other mode, so that component is removed in one step",
                            "The two modes exchange energy each iteration, so whichever one is smaller at the start ends up carrying all of the error",
                            "The larger eigenvalue direction holds most of the input power, so the noise in that direction averages itself away first",
                        ],
                        "a": 1,
                        "whys": [
                            r"The initial error is $-w_o = [-1.447368, +1.052632]$, whose components are not negatives of each other, so it is not along $[1,-1]$ at all — it acquires that direction on the first update rather than starting there.",
                            r"$\mu\lambda = (1/1.9)(1.9) = 1$, so the multiplier is zero and that component is gone for good.",
                            r"There is no exchange: $I - \mu R$ is diagonal in the eigenvector basis, which is exactly what makes each mode a separate scalar recursion with no coupling term.",
                            r"Nothing here is random — this is the deterministic recursion, with $R$ and $p$ known exactly and not a sample of noise anywhere in it.",
                        ],
                        "why": r"""
$v(n+1) = (I - \mu R)v(n)$, and along an eigenvector that matrix is the scalar
$1 - \mu\lambda$. Setting $\mu = 1/\lambda_{max}$ makes that scalar exactly zero for the
$\lambda = 1.9$ mode, so one update annihilates it and there is nothing to bring it back.
The printed trace shows it: the two components of $w - w_o$ are exact negatives from
iteration 1 onwards, and their sum reads $-0.000000$ forever after.
""",
                    },
                    {
                        "q": "The same bowl converges in 66 iterations at $\\mu = 0.95\\times$ the bound and in 250 at $\\mu = 0.99\\times$ the bound. What went wrong at 0.99?",
                        "opts": [
                            "Rounding error grows with the step size and stalls the walk near the bound",
                            "The $\\lambda = 0.1$ mode slows down as $\\mu$ rises, because its factor $1 - \\mu\\lambda$ moves further from zero",
                            "Its factor for $\\lambda = 1.9$ has swung to $-0.98$, so the fast mode has become the slow one",
                            "The bowl loses convexity along the largest eigenvalue once the step exceeds $1/\\lambda_{max}$, so descent no longer applies",
                        ],
                        "a": 2,
                        "whys": [
                            r"These runs are nowhere near the precision limit — the weights are order 1 and the tolerance is $10^{-3}$, so double precision has thirteen digits to spare.",
                            r"Backwards: $|1 - \mu\lambda_{min}|$ falls from 0.9789 to 0.8926 across the whole table, so raising $\mu$ helps the slow mode slightly. It is the fast mode that is being ruined.",
                            r"$1 - 0.99 \times (2/1.9) \times 1.9 = -0.98$, and $0.98^n$ decays more slowly than $0.9^n$.",
                            r"The bowl is a property of $R$ alone and does not know what step size you chose; $R$ stays positive definite and $J$ stays convex at every $\mu$.",
                        ],
                        "why": r"""
Convergence is set by $\max_i |1 - \mu\lambda_i|$, and that maximum is not monotone in
$\mu$. The $\lambda = 1.9$ factor falls to zero at $\mu = 1/1.9$ and then grows again with
a negative sign, reaching $-1$ at the bound — where the mode flips sign forever without
shrinking. The best step equalises the two ends, $\mu = 2/(\lambda_{max} + \lambda_{min})
= 1.0$, giving factors of $\pm 0.9$ and the 66-iteration row.
""",
                    },
                    {
                        "q": "The far-end level is raised by 20 dB, so every entry of $R$ and of $p$ grows by a factor of 100. The step size is left alone. What happens?",
                        "opts": [
                            "Nothing changes, because $R$ and $p$ scaled together and the Wiener solution is unmoved",
                            "It converges 100 times faster, since the gradient at every point is 100 times larger",
                            "It converges to weights 100 times larger, cancelling far too much echo",
                            "It diverges, because $2/\\lambda_{max}$ has fallen by 100 while $\\mu$ stayed put",
                        ],
                        "a": 3,
                        "whys": [
                            r"The Wiener solution really is unmoved — $(100R)^{-1}(100p) = R^{-1}p$ — which is what makes this the tempting answer. The destination is unchanged; whether the walk can reach it is a separate question, and that one depends on $\mu\lambda_{max}$.",
                            r"The step $\mu\lambda$ per mode is 100 times larger, and past $\mu\lambda = 2$ larger is not faster, it is unbounded.",
                            r"Nothing scales the solution: the extra factor of 100 in $p$ is cancelled by the factor of 100 in $R$, so the taps are the same taps.",
                            r"$\mu\lambda_{max}$ goes from below 2 to roughly 100 times that, so $|1 - \mu\lambda_{max}|$ is enormous.",
                        ],
                        "why": r"""
Two separate things are being asked about. Where the walk ends is set by $R^{-1}p$, which
is invariant to a common scaling. Whether it gets there is set by $\mu\lambda_{max} < 2$,
and $\lambda_{max}$ has grown by 100. This is exactly the failure NLMS is built to remove
in module 3: dividing the step by the measured input energy makes the stable range of
$\mu$ independent of how loud the far end happens to be.
""",
                    },
                    {
                        "q": "The input is whitened before the filter, so $R$ becomes the identity. What does that do to the walk?",
                        "opts": [
                            "It slows convergence, because whitening removes the correlation the filter was exploiting to predict the echo",
                            "It removes the bound on $\\mu$ entirely, since there is no longer a largest eigenvalue to violate",
                            "Every mode shares one factor $1 - \\mu$, so the whole walk finishes in the time the fastest mode used to take",
                            "It leaves the iteration count alone, because the spread belongs to the algorithm rather than to the data",
                        ],
                        "a": 2,
                        "whys": [
                            r"Whitening the *input* does not remove what the input shares with the desired signal, and it is $p$ that carries that. The prediction is unharmed; what disappears is the elongation of the bowl.",
                            r"The bound is $2/\lambda_{max}$ and $\lambda_{max}$ is now 1, so the bound is 2 — a number, not an absence. Step past it and this walk diverges like any other.",
                            r"With every $\lambda_i = 1$ there is one factor, one time constant, and no slow direction to wait for.",
                            r"The spread is the condition number of $R$, and $R$ is built entirely from the input's own statistics. The algorithm contributes $\mu$ and nothing else.",
                        ],
                        "why": r"""
The eigenvalue spread lives in the data. Steepest descent is slow on correlated input
because the bowl is an elongated valley, and a gradient points across a valley rather than
along it. Make the bowl circular and the gradient points at the minimum from everywhere.
This is the reason whitening-flavoured algorithms exist at all, and it is what RLS in
module 4 buys with its $O(M^2)$ arithmetic — an implicit $R^{-1}$ in the update.
""",
                    },
                    {
                        "q": "You set $\\mu$ as close to $2/\\lambda_{max}$ as stability allows. Roughly how many iterations does the slowest mode then need?",
                        "opts": [
                            "About one, since the largest step available is the deadbeat step for the whole system",
                            "About $M$, one iteration per tap, in the way a direct solve costs one elimination per row",
                            "About $\\lambda_{max}/2\\lambda_{min}$ — half the eigenvalue spread, and no choice of $\\mu$ removes it",
                            "About $2/\\lambda_{max}$ iterations, since the step size and the number of iterations needed are reciprocal quantities",
                        ],
                        "a": 2,
                        "whys": [
                            r"The deadbeat step $\mu = 1/\lambda$ kills one mode in one iteration, and no single $\mu$ is deadbeat for two different eigenvalues at once. That is precisely the difficulty.",
                            r"The filter length sets the dimension of the problem, not the conditioning. Two taps here needed 200 iterations, and a hundred well-conditioned taps could need a dozen.",
                            r"$\tau = 1/(\mu\lambda_{min})$ with $\mu \approx 2/\lambda_{max}$ gives $\lambda_{max}/(2\lambda_{min})$.",
                            r"The two are reciprocal only through $\lambda_{min}$: $\tau = 1/(\mu\lambda_{min})$, and dropping the eigenvalue leaves a quantity with the wrong units and no dependence on conditioning at all.",
                        ],
                        "why": r"""
Substitute the largest usable step into the time constant: $\tau = 1/(\mu\lambda_{min})$
becomes $\lambda_{max}/(2\lambda_{min})$, which is half the eigenvalue spread and contains
no $\mu$. That is why the two-tap bowl at spread 19 took a couple of hundred iterations
whatever was done to the step size. The spread is a property of the input spectrum, so the
only way past it is a different algorithm.
""",
                    },
                    {
                        "q": "Steepest descent converges monotonically and provably. Why does no echo canceller run it?",
                        "opts": [
                            "Every update contains $R$ and $p$, and knowing those means the answer was already available",
                            "The monotone descent guarantee holds only for two taps and is lost for longer filters",
                            "It needs a fresh matrix inverse at every single iteration, which costs $O(M^3)$ of arithmetic per sample",
                            "Its step-size bound cannot be met once the filter is longer than a handful of taps",
                        ],
                        "a": 0,
                        "whys": [
                            r"Estimating $R$ well enough to iterate on means estimating the very thing whose inverse is the answer.",
                            r"The mode decomposition works for any $M$ — an $M \times M$ symmetric $R$ has $M$ orthogonal eigenvectors — and monotone descent below the bound holds with it.",
                            r"The update is $w + \mu(p - Rw)$: one matrix-vector product, $O(M^2)$, and no inverse anywhere. The cost is a fair objection to *forming* $R^{-1}$, which is why descent was reached for, and it does not apply to descent itself.",
                            r"The bound $2/\lambda_{max}$ shrinks as taps are added, since $\lambda_{max}$ grows with the total input power, but it stays a positive number and is always satisfiable.",
                        ],
                        "why": r"""
The algorithm is circular as an implementation: it iterates towards $R^{-1}p$ using $R$
and $p$ at every step. It earns its place as an analysis — the geometry of the walk, the
bound, the time constants — and module 3 keeps that analysis while throwing the
requirement away, by replacing the expectation with the single most recent sample. What
survives the substitution is the mode picture; what is added is a noise floor.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "One mode of the descent as a single pole",
                "visualiser": "z-plane",
                "minutes": 8,
                "initial": {"r": 0.85, "th": 0},
                "brief": r'''
Along one eigenvector of $R$, steepest descent is nothing but a one-pole recursion:

$$v(n+1) = (1 - \mu\lambda)\,v(n)$$

where $v$ is the distance from the Wiener solution in that direction. So set the
pole radius to $|1 - \mu\lambda|$ and read the impulse response as the weight error
dying away — or not.

Angle $\theta = 0$ means $1 - \mu\lambda$ is positive; $\theta = \pi$ means it has
gone negative.
''',
                "notice": [
                    "With $\\theta = 0$, drag $r$ from 0.99 down to 0.2. The same algebra, a hundredfold difference in iterations — and $r$ is only $|1 - \\mu\\lambda|$, so this is entirely a statement about $\\mu\\lambda$.",
                    "Push $r$ just past 1. The response grows without bound: that is $\\mu > 2/\\lambda$, the step-size bound being violated by the fastest mode.",
                    "Set $\\theta = \\pi$ with $r$ around 0.7. The response alternates sign — $1 - \\mu\\lambda$ is negative, so the filter overshoots the Wiener solution every single iteration and still converges.",
                ],
            },
            "derive": {
                "title": "Why the step size is bounded by the largest eigenvalue",
                "minutes": 14,
                "vars": ["J", "w", "w_o", "mu", "lambda", "lambda_max", "n", "v", "v_0",
                         "R", "p", "sigma_d", "tau"],
                "brief": r'''
The cost is the quadratic bowl from module 1,

$$J(w) = \sigma_d^2 - 2w^\top p + w^\top R w$$

with $R$ symmetric and positive definite. Steepest descent steps against the
gradient with a fixed step size $\mu$.
''',
                "steps": [
                    {
                        "prompt": "Write the gradient $\\nabla J$ with respect to $w$, in terms of $R$, $w$ and $p$.",
                        "answer": "2 R w - 2 p",
                        "hint": "Treat it exactly like the scalar case: $\\sigma_d^2$ is constant, the linear term gives $-2p$, and the quadratic term gives $2Rw$ because $R$ is symmetric.",
                        "deconstruct": [
                            "$\\nabla(w^\\top R w) = 2Rw$ when $R = R^\\top$.",
                            "$\\nabla(-2w^\\top p) = -2p$.",
                        ],
                    },
                    {
                        "prompt": "The update is $w(n+1) = w(n) - \\frac{\\mu}{2}\\nabla J$. Write $w(n+1)$ in terms of $w$, $\\mu$, $R$ and $p$.",
                        "answer": "w + \\mu (p - R w)",
                        "hint": "The factor of one half is there purely to cancel the 2 in the gradient.",
                        "deconstruct": [
                            "$-\\frac{\\mu}{2}(2Rw - 2p) = -\\mu(Rw - p)$.",
                            "Add that to $w$ and reverse the sign inside the bracket.",
                        ],
                    },
                    {
                        "prompt": "Let $v = w - w_o$, where $Rw_o = p$. Along an eigenvector of $R$ with eigenvalue $\\lambda$, the update becomes $v(n+1) = c\\,v(n)$. Write the scalar $c$.",
                        "answer": "1 - \\mu\\lambda",
                        "hint": "Substitute $w = w_o + v$ and use $p - Rw_o = 0$; you are left with $v - \\mu R v$, and $Rv = \\lambda v$ along an eigenvector.",
                        "deconstruct": [
                            "$w(n+1) - w_o = v + \\mu(p - R(w_o + v)) = v - \\mu Rv$.",
                            "Along an eigenvector $Rv = \\lambda v$, so the bracket collapses to $(1 - \\mu\\lambda)v$.",
                        ],
                    },
                    {
                        "prompt": "Write $v$ after $n$ iterations, in terms of $v_0$, $\\mu$, $\\lambda$ and $n$.",
                        "answer": "v_0 (1 - \\mu\\lambda)^n",
                        "hint": "Multiplying by the same scalar $n$ times is that scalar to the power $n$.",
                        "deconstruct": [
                            "$v_1 = c v_0$, $v_2 = c^2 v_0$, and so on.",
                            "Substitute $c = 1 - \\mu\\lambda$.",
                        ],
                    },
                    {
                        "prompt": "Every mode must decay, which needs $|1 - \\mu\\lambda| < 1$ for all eigenvalues. Write the upper bound on $\\mu$.",
                        "answer": "\\frac{2}{\\lambda_{max}}",
                        "hint": "$|1 - \\mu\\lambda| < 1$ means $0 < \\mu\\lambda < 2$; the binding constraint comes from the largest eigenvalue.",
                        "deconstruct": [
                            "For each mode, $\\mu < 2/\\lambda$.",
                            "All of those must hold at once, so the smallest of them wins.",
                        ],
                    },
                    {
                        "prompt": "The mode decays as $(1 - \\mu\\lambda)^n = e^{n\\ln(1-\\mu\\lambda)}$. For small $\\mu\\lambda$, $\\ln(1 - \\mu\\lambda) \\approx -\\mu\\lambda$. Write the time constant $\\tau$ in iterations.",
                        "answer": "\\frac{1}{\\mu\\lambda}",
                        "hint": "The time constant is the $n$ at which the exponent reaches $-1$.",
                        "deconstruct": [
                            "$e^{-n\\mu\\lambda}$ falls to $1/e$ when $n\\mu\\lambda = 1$.",
                            "Solve that for $n$.",
                        ],
                    },
                ],
                "closing": r'''
Put the last two results together. The step is capped by $2/\lambda_{max}$, and the
slowest mode takes $1/(\mu\lambda_{min})$ iterations. Choose $\mu$ as large as the
bound allows and the slowest mode still needs about $\lambda_{max}/(2\lambda_{min})$
iterations — the eigenvalue spread, unchanged and unavoidable. No choice of step
size removes it; only a different algorithm does.
''',
            },
            "blanks": {
                "title": "How far you may step, and how long it takes",
                "minutes": 9,
                "caption": "steepest_descent.py — the eigenvalues decide both",
                "lang": "python",
                "brief": r"""
Steepest descent has one parameter and the eigenvalues of $R$ decide everything about it:
how large it may be, and how long the walk takes once it is. Fill in the chain.
""",
                "listing": """grad = 2 * (R @ w - p)
w    = w - (mu / 2) * grad          # i.e.  w = w + mu * (p - R @ w)

# Change to the eigenvector coordinates of R and the update decouples
# into M independent scalar recursions, one per mode:
#
#     v_i(n+1) = ___ * v_i(n)
#
# Every mode converges only if all M factors are inside the unit circle:
#
#     0 < mu < ___
#
# The step is capped by the largest eigenvalue, but the time taken is set
# by ___ , so the walk is slow whenever the
# eigenvalue spread ___ is large.
""",
                "blanks": [
                    {
                        "prompt": "One mode, one factor per iteration.",
                        "hole": "?",
                        "opts": ["(1 - mu * lambda_i)", "(1 - mu)", "mu * lambda_i", "(1 + mu * lambda_i)"],
                        "a": 0,
                        "why": "Each mode shrinks by $(1 - \\mu\\lambda_i)$ every step — a geometric sequence, so convergence is exponential and the rate differs from mode to mode. This single expression contains the whole of the next two blanks.",
                        "whys": [
                            "Each mode shrinks by $(1 - \\mu\\lambda_i)$ every step — a geometric sequence, so convergence is exponential and the rate differs from mode to mode. This single expression contains the whole of the next two blanks.",
                            "Without $\\lambda_i$ every mode would converge at the same rate and the eigenvalue spread would not matter — which would be pleasant and is not what happens.",
                            "Missing the 1, so a small step size would make the modes vanish instantly rather than barely move.",
                            "The sign is wrong: this grows without bound for any positive $\\mu$ and $\\lambda$.",
                        ],
                    },
                    {
                        "prompt": "Which eigenvalue binds the step size?",
                        "hole": "?",
                        "opts": ["2 / lambda_max", "2 / lambda_min", "1 / lambda_max", "2 / trace(R)"],
                        "a": 0,
                        "why": "$|1 - \\mu\\lambda_i| < 1$ needs $\\mu < 2/\\lambda_i$ for every mode, so the *largest* eigenvalue sets the tightest constraint. Exceed it and the strongest mode diverges first — the algorithm blows up in the direction the input energy is concentrated in.",
                        "whys": [
                            "$|1 - \\mu\\lambda_i| < 1$ needs $\\mu < 2/\\lambda_i$ for every mode, so the *largest* eigenvalue sets the tightest constraint. Exceed it and the strongest mode diverges first — the algorithm blows up in the direction the input energy is concentrated in.",
                            "The smallest eigenvalue gives the loosest bound, which every other mode then violates. Using it guarantees divergence.",
                            "Safe, but a factor of two conservative — it halves the achievable convergence rate for no reason.",
                            "$\\text{trace}(R) = \\sum\\lambda_i$ is a usable *conservative* bound, since it is at least $\\lambda_{max}$, and it has the practical virtue of being measurable as the input power without an eigendecomposition. It is not the exact condition.",
                        ],
                    },
                    {
                        "prompt": "And which one decides how long you wait?",
                        "hole": "?",
                        "opts": ["lambda_min", "lambda_max", "trace(R)", "mu"],
                        "a": 0,
                        "why": "The slowest mode is the one with the smallest $\\lambda$, since its factor $(1 - \\mu\\lambda_{min})$ is closest to 1. So the largest eigenvalue caps the step and the smallest sets the finish line — the two ends of the spectrum pulling against each other.",
                        "whys": [
                            "The slowest mode is the one with the smallest $\\lambda$, since its factor $(1 - \\mu\\lambda_{min})$ is closest to 1. So the largest eigenvalue caps the step and the smallest sets the finish line — the two ends of the spectrum pulling against each other.",
                            "The largest eigenvalue converges *fastest* — it is the one that limits how big a step you may take, not the one you end up waiting for.",
                            "The trace is a sum over all modes and does not identify the slow one.",
                            "$\\mu$ is what you choose; the question is what constrains the choice.",
                        ],
                    },
                    {
                        "prompt": "Name the ratio that predicts a slow walk.",
                        "hole": "?",
                        "opts": [
                            "lambda_max / lambda_min",
                            "lambda_max * lambda_min",
                            "lambda_min / lambda_max",
                            "trace(R)",
                        ],
                        "a": 0,
                        "why": "The eigenvalue spread, which is the condition number of $R$. It is a purely geometric statement: a highly correlated input makes the error bowl a long narrow valley, and steepest descent zig-zags across it instead of running down it. That is what RLS in module 4 buys its way out of.",
                        "whys": [
                            "The eigenvalue spread, which is the condition number of $R$. It is a purely geometric statement: a highly correlated input makes the error bowl a long narrow valley, and steepest descent zig-zags across it instead of running down it. That is what RLS in module 4 buys its way out of.",
                            "A product does not measure spread: scaling the input scales every eigenvalue and changes the product without changing the difficulty at all.",
                            "Inverted, so a perfectly conditioned white input would score worst.",
                            "The trace measures total input power, not how unevenly it is distributed. Two very different inputs can share a trace.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Descend a known error surface",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Here $R$ and $p$ are handed to you, so this is the deterministic algorithm — no
data, no noise, just the recursion.

- `max_step(R)` returns $2/\lambda_{max}$, using `np.linalg.eigvalsh` because $R$ is
  symmetric.
- `mse(R, p, var_d, w)` returns $J(w) = \sigma_d^2 - 2p^\top w + w^\top R w$.
- `descend(R, p, mu, iters, w0=None)` runs $w \leftarrow w + \mu(p - Rw)$ and
  returns a **list of length `iters + 1`**: the starting weights first, then the
  weights after each iteration. Start from zeros when `w0` is `None`.

Returning the whole trajectory rather than the final answer is the point — the
checks look at how it got there.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def max_step(R):
    """Largest step size that keeps every mode of steepest descent convergent."""
    R = np.asarray(R, dtype=float)
    # TODO: 2 divided by the largest eigenvalue.
    return 0.0


def mse(R, p, var_d, w):
    """J(w) = var_d - 2 p.w + w.R.w"""
    R = np.asarray(R, dtype=float)
    p = np.asarray(p, dtype=float).ravel()
    w = np.asarray(w, dtype=float).ravel()
    # TODO
    return 0.0


def descend(R, p, mu, iters, w0=None):
    """Return [w0, w1, ..., w_iters] for w <- w + mu (p - R w)."""
    R = np.asarray(R, dtype=float)
    p = np.asarray(p, dtype=float).ravel()
    w = np.zeros(p.size) if w0 is None else np.array(w0, dtype=float).ravel()
    traj = [w.copy()]
    # TODO: append a copy of the weights after every update.
    return traj


if __name__ == "__main__":
    R = np.array([[1.0, 0.9], [0.9, 1.0]])
    p = np.array([0.5, 0.25])
    mu = 0.5 * max_step(R)
    traj = descend(R, p, mu, 200)
    print("mu =", round(mu, 6))
    print("final weights:", np.round(traj[-1], 6).tolist())
    print("final J:", round(mse(R, p, 1.0, traj[-1]), 8))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def max_step(R):
    """Largest step size that keeps every mode of steepest descent convergent."""
    R = np.asarray(R, dtype=float)
    lam_max = float(np.max(np.linalg.eigvalsh(R)))
    return 2.0 / lam_max


def mse(R, p, var_d, w):
    """J(w) = var_d - 2 p.w + w.R.w"""
    R = np.asarray(R, dtype=float)
    p = np.asarray(p, dtype=float).ravel()
    w = np.asarray(w, dtype=float).ravel()
    return float(var_d - 2.0 * (p @ w) + w @ R @ w)


def descend(R, p, mu, iters, w0=None):
    """Return [w0, w1, ..., w_iters] for w <- w + mu (p - R w)."""
    R = np.asarray(R, dtype=float)
    p = np.asarray(p, dtype=float).ravel()
    w = np.zeros(p.size) if w0 is None else np.array(w0, dtype=float).ravel()
    traj = [w.copy()]
    for _ in range(iters):
        w = w + mu * (p - R @ w)
        traj.append(w.copy())
    return traj


if __name__ == "__main__":
    R = np.array([[1.0, 0.9], [0.9, 1.0]])
    p = np.array([0.5, 0.25])
    mu = 0.5 * max_step(R)
    traj = descend(R, p, mu, 200)
    print("mu =", round(mu, 6))
    print("final weights:", np.round(traj[-1], 6).tolist())
    print("final J:", round(mse(R, p, 1.0, traj[-1]), 8))
'''}],
                "hints": [
                    "`np.linalg.eigvalsh` returns the eigenvalues of a symmetric matrix in ascending order, so the last one is $\\lambda_{max}$.",
                    "`w @ R @ w` is the quadratic form; no transposes are needed for a one-dimensional array.",
                    "Append `w.copy()`, not `w` — appending the same array object repeatedly gives a trajectory in which every entry is the final answer.",
                ],
                "tests": [
                    {"name": "the step bound comes from the largest eigenvalue", "code": r'''
import numpy as np
_R = np.array([[1.0, 0.9], [0.9, 1.0]])
_ms = max_step(_R)
assert abs(_ms - 1.0526315789473684) < 1e-9, \
    f"eigenvalues are 0.1 and 1.9, so the bound is 2/1.9 = 1.05263; got {_ms}"
_R2 = np.diag([4.0, 1.0])
assert abs(max_step(_R2) - 0.5) < 1e-12, \
    f"the bound is set by the largest eigenvalue alone, here 2/4 = 0.5; got {max_step(_R2)}"
'''},
                    {"name": "the cost function reads correctly at both ends", "code": r'''
import numpy as np
_R = np.array([[1.0, 0.9], [0.9, 1.0]])
_p = np.array([0.5, 0.25])
assert abs(mse(_R, _p, 1.0, np.zeros(2)) - 1.0) < 1e-12, \
    "with zero weights the filter outputs nothing, so J is just the desired-signal power"
_wo = np.linalg.solve(_R, _p)
assert abs(mse(_R, _p, 1.0, _wo) - 0.5394736842105263) < 1e-9, \
    f"at the Wiener solution J should be var_d - p.wo = 0.53947; got {mse(_R, _p, 1.0, _wo)}"
'''},
                    {"name": "descent reaches the Wiener solution", "code": r'''
import numpy as np
_R = np.array([[1.0, 0.9], [0.9, 1.0]])
_p = np.array([0.5, 0.25])
_traj = descend(_R, _p, 0.5 * max_step(_R), 200)
assert len(_traj) == 201, f"the trajectory should hold the start plus 200 updates, got {len(_traj)}"
assert np.max(np.abs(_traj[0])) < 1e-12, "with w0 unset the walk starts at the origin"
_wo = np.linalg.solve(_R, _p)
assert np.linalg.norm(_traj[-1] - _wo) < 1e-3, \
    f"below the bound the walk must end at R^-1 p = {np.round(_wo, 4).tolist()}, got {np.round(_traj[-1], 4).tolist()}"
'''},
                    {"name": "the cost falls at every single iteration", "code": r'''
import numpy as np
_R = np.array([[1.0, 0.9], [0.9, 1.0]])
_p = np.array([0.5, 0.25])
_traj = descend(_R, _p, 0.5 * max_step(_R), 200)
_J = [mse(_R, _p, 1.0, _w) for _w in _traj]
for _i in range(len(_J) - 1):
    assert _J[_i + 1] <= _J[_i] + 1e-12, \
        f"J rose from {_J[_i]:.6f} to {_J[_i+1]:.6f} at iteration {_i} — below the bound the surface is descended monotonically"
assert abs(_J[-1] - 0.5394736842105263) < 1e-6, \
    f"J should settle on the minimum 0.53947; got {_J[-1]}"
'''},
                    {"name": "past the bound it diverges", "code": r'''
import numpy as np
_R = np.array([[1.0, 0.9], [0.9, 1.0]])
_p = np.array([0.5, 0.25])
_traj = descend(_R, _p, 1.05 * max_step(_R), 200)
assert np.linalg.norm(_traj[-1]) > 1e3, \
    f"5 per cent past 2/lambda_max the fastest mode has |1 - mu lambda| > 1 and must blow up; ended at {np.round(_traj[-1], 3).tolist()}"
'''},
                    {"name": "eigenvalue spread sets the number of iterations", "code": r'''
import numpy as np
_p = np.array([0.5, 0.25])


def _iters(rho, tol=1e-3):
    _R = np.array([[1.0, rho], [rho, 1.0]])
    _wo = np.linalg.solve(_R, _p)
    _traj = descend(_R, _p, 0.5 * max_step(_R), 4000)
    for _n, _w in enumerate(_traj):
        if np.linalg.norm(_w - _wo) < tol * np.linalg.norm(_wo):
            return _n
    return 10 ** 9


_n_mild = _iters(0.5)
_n_hard = _iters(0.9)
assert _n_mild < 40, f"spread 3 should converge in a few dozen iterations, took {_n_mild}"
assert _n_hard > 4 * _n_mild, \
    f"spread 19 should cost several times more iterations than spread 3; got {_n_hard} against {_n_mild}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "LMS and its normalised cousin",
            "summary": "Replace the expectation with one sample. The algorithm becomes implementable, and gains a noise floor of its own.",
            "concepts": [
                "The instantaneous gradient $-2e(n)x(n)$: an unbiased but extremely noisy estimate of $\\nabla J$.",
                "The LMS update $w(n+1) = w(n) + \\mu e(n)x(n)$ — $2M$ multiplications per sample and nothing else.",
                "Convergence in the mean needs the same bound as steepest descent; in practice $0 < \\mu < 2/\\text{trace}(R)$, because the trace is measurable and $\\lambda_{max}$ is not.",
                "Gradient noise never vanishes, so LMS hovers above $J_{min}$: misadjustment $\\approx \\mu\\,\\text{trace}(R)/2$.",
                "NLMS divides the step by the instantaneous input energy, making the stable range of $\\mu$ independent of input power — it does not fix the eigenvalue spread.",
            ],
            "read": [
                {
                    "title": "One sample where an expectation used to be",
                    "minutes": 17,
                    "body": r'''
Back on the hands-free unit. The gradient of the true cost at $w = 0$ is $-2p$, and for
the recording from module 1 that is $[-2.0174, 1.0103, -0.5021]$. Getting those three
numbers took four thousand samples and three passes over the record. The phone has
125 microseconds and one new sample.

So take the one sample. The instantaneous squared error is $\hat{J}(n) = e(n)^2$ with
$e(n) = d(n) - w^\top x(n)$, and its gradient is $-2e(n)x(n)$ — no expectation anywhere.
The question is how much has been thrown away.

```python
import random

M = 3
far = random.Random(7)
mic = random.Random(8)
room = [1.0, -0.5, 0.25]
N = 4000
x = [far.gauss(0.0, 1.0) for _ in range(N)]
d = [sum(room[k] * x[n - k] for k in range(M) if n - k >= 0) + 0.01 * mic.gauss(0.0, 1.0)
     for n in range(N)]

# The true gradient at w = 0 is -2p, with p estimated over the whole record.
p = [sum(d[n] * x[n - k] for n in range(k, N)) / N for k in range(M)]
print("true gradient at w = 0:      ", [round(-2 * v, 4) for v in p])

for n in (100, 101, 102):
    g = [round(-2 * d[n] * x[n - k], 4) for k in range(M)]
    print(f"one-sample estimate at n={n}: ", g)

for span in (10, 100, 1000, 4000):
    avg = [round(sum(-2 * d[n] * x[n - k] for n in range(span)) / span, 4) for k in range(M)]
    print(f"averaged over {span:5d} samples: ", avg)
```

The single-sample estimates are `[-0.3531, 0.1632, -0.5999]`, `[-0.5854, -0.2927,
0.1353]`, `[0.0321, 0.1731, 0.0865]`. Not one of them resembles the answer; the second has
the wrong sign in two places out of three. Averaged over ten samples it is still
`[-0.6783, -0.0559, 0.2611]`, which points in nearly the wrong direction. At a hundred it
has become `[-1.794, 0.8213, -0.1507]`, at a thousand `[-1.9729, 1.0388, -0.4145]`, and at
four thousand `[-2.0174, 1.0099, -0.5012]`, which is the answer.

That is the whole bargain. The estimate is unbiased — $E[-2ex] = \nabla J$ — so its error
is noise rather than a wrong direction, and a hundred small steps down a hundred noisy
gradients arrive roughly where one step down the true gradient would have gone. Nothing
about it needs $R$, $p$, or a second pass over the data.

## The algorithm is two lines

Step against half the instantaneous gradient, the half chosen so that the 2 cancels as it
did in module 2:

$$w(n+1) = w(n) - \frac{\mu}{2}\big({-2}e(n)x(n)\big) = w(n) + \mu\,e(n)\,x(n)$$

That is least mean squares. Per sample it is $M$ multiplications to form the output, $M$
to apply the update, and no division, no matrix, and no memory beyond the tap delay line
the filter already had. The derive unit *From the true gradient to LMS, and the price of
the substitution* takes those two lines and then charges for them.

```python
import random


def lms(x, d, M, mu, report=()):
    """w <- w + mu e x, with the error taken before the update."""
    w = [0.0] * M
    err = [0.0] * len(x)
    for n in range(len(x)):
        u = [x[n - k] if n - k >= 0 else 0.0 for k in range(M)]
        e = d[n] - sum(w[k] * u[k] for k in range(M))
        err[n] = e
        for k in range(M):
            w[k] += mu * e * u[k]
        if n + 1 in report:
            print(f"n = {n + 1:5d}   w = {[round(v, 4) for v in w]}")
    return w, err


M, N = 3, 4000
far = random.Random(7)
mic = random.Random(8)
room = [1.0, -0.5, 0.25]
x = [far.gauss(0.0, 1.0) for _ in range(N)]
d = [sum(room[k] * x[n - k] for k in range(M) if n - k >= 0) + 0.01 * mic.gauss(0.0, 1.0)
     for n in range(N)]

power = sum(v * v for v in x) / N
print("input power:", round(power, 4), "  practical bound 2/(M*power):",
      round(2.0 / (M * power), 6))
w, err = lms(x, d, M, 0.01, report=(1, 10, 100, 500, 2000, 4000))
print("first error e(0) =", round(err[0], 6), " and d(0) =", round(d[0], 6))
```

After one sample the weights are `[0.0006, 0.0, 0.0]`; after 100, `[0.5956, -0.2883,
0.0966]`; after 500, `[0.994, -0.4942, 0.2458]`; after 2000, `[0.9995, -0.4992, 0.2502]`.
The room was found without $R$ ever being formed.

The bound printed above deserves a look. Convergence in the mean is governed by the same
$|1 - \mu\lambda_i| < 1$ as module 2, because the expected LMS update *is* the
steepest-descent update — so $\mu < 2/\lambda_{max}$ again. But $\lambda_{max}$ needs an
eigendecomposition of a matrix nobody has. What is available is
$\text{trace}(R) = \sum_i \lambda_i = M\sigma_x^2$, which is at least $\lambda_{max}$ and
is one running average away. Here that gives `0.661043`, and $\mu = 0.01$ sits at 1.5 per
cent of it.

## The bill for using one sample

The gradient noise does not fade as the weights approach $w_o$. At the optimum $e(n)$ is
whatever the microphone noise was, $x(n)$ is not zero, and $\mu ex$ is not zero either — so
the weights keep being kicked around $w_o$ forever and the mean-square error settles
*above* $J_{min}$. The theory says the excess is a fraction $\mu\,\text{trace}(R)/2$ of
$J_{min}$. Measure it.

```python
import random


def run(mu, N=30000, noise=0.3):
    far = random.Random(5)
    mic = random.Random(6)
    room = [1.0, -0.5, 0.25]
    M = 3
    x = [far.gauss(0.0, 1.0) for _ in range(N)]
    d = [sum(room[k] * x[n - k] for k in range(M) if n - k >= 0) + noise * mic.gauss(0.0, 1.0)
         for n in range(N)]
    w = [0.0] * M
    tail = 0.0
    half = N // 2
    for n in range(N):
        u = [x[n - k] if n - k >= 0 else 0.0 for k in range(M)]
        e = d[n] - sum(w[k] * u[k] for k in range(M))
        if n >= half:
            tail += e * e
        for k in range(M):
            w[k] += mu * e * u[k]
    return tail / (N - half)


print("   mu     predicted   measured")
for mu in (0.002, 0.02, 0.05, 0.2):
    predicted = 0.09 * (1.0 + mu * 3 * 1.0 / 2.0)
    print(f"  {mu:.3f}    {predicted:.5f}     {run(mu):.5f}")
```

With $\sigma_v = 0.3$ the floor is $J_{min} = 0.09$. At $\mu = 0.002$ the prediction is
`0.09027` and the measurement `0.09060`; at $0.02$, `0.09270` against `0.09328`; at
$0.05$, `0.09675` against `0.09816`. Three step sizes, three agreements to about one per
cent of the excess.

At $\mu = 0.2$ the prediction is `0.11700` and the measurement `0.14984`, a 28 per cent
under-estimate. That is not a failure of the experiment; it is the formula's own small-$\mu$
assumption expiring, and the direction of the error is the useful part — the real cost of a
large step is worse than the linear rule promises.

Put that beside the time constant $1/(\mu\lambda_{min})$ from module 2. Misadjustment goes
as $\mu$; convergence time goes as $1/\mu$; the product contains no $\mu$ at all. There is
no setting that is both fast and quiet, only a position on a fixed curve.

## The mistake: expecting NLMS to fix the conditioning

A $\mu$ that works on quiet speech diverges on loud speech, because the bound depends on
the input power. The repair is to divide the step by the measured energy of the current
input window, $\mu/(\varepsilon + x^\top x)$, and it is exact: the step $1/x^\top x$ is
precisely the one that drives the *a posteriori* error $d - w(n+1)^\top x$ to zero, so
$\mu$ becomes a dimensionless number in $(0, 2)$ with no units to get wrong.

Because that division looks like dividing by a correlation, and because NLMS is
conspicuously faster on speech, it is widely taken to fix the eigenvalue spread as well.
It does not, and the reason is one line: $x^\top x$ is a scalar. A scalar rescales the
bowl; only a matrix can reshape it.

```python
import math
import random

ROOM = [0.60, -0.35, 0.22, -0.14, 0.09, -0.05, 0.03, -0.02]
M = len(ROOM)


def far_end(N, rho, seed=31):
    g = random.Random(seed)
    scale = math.sqrt(1.0 - rho * rho)
    x = [0.0] * N
    for n in range(1, N):
        x[n] = rho * x[n - 1] + scale * g.gauss(0.0, 1.0)
    return x


def nlms(x, d, mu=0.5, tol=0.02):
    """Return (final weights, first sample at which every tap is within tol)."""
    w = [0.0] * M
    hit = None
    for n in range(len(x)):
        u = [x[n - k] if n - k >= 0 else 0.0 for k in range(M)]
        e = d[n] - sum(w[k] * u[k] for k in range(M))
        energy = 1e-6 + sum(v * v for v in u)
        for k in range(M):
            w[k] += mu * e * u[k] / energy
        if hit is None and max(abs(w[k] - ROOM[k]) for k in range(M)) < tol:
            hit = n + 1
    return w, hit


def echo(x, seed=32):
    mic = random.Random(seed)
    return [sum(ROOM[k] * x[n - k] for k in range(M) if n - k >= 0)
            + 0.001 * mic.gauss(0.0, 1.0) for n in range(len(x))]


print("  rho    r(1)/r(0)   two-tap spread   NLMS samples to converge")
for rho in (0.0, 0.8, 0.95, 0.99):
    x = far_end(20000, rho)
    _, hit = nlms(x, echo(x))
    print(f"  {rho:.2f}      {rho:.2f}          {(1 + rho) / (1 - rho):7.1f}          {hit}")

x = far_end(4000, 0.8)
d = echo(x)
w_quiet, _ = nlms(x, d)
w_loud, _ = nlms([10 * v for v in x], [10 * v for v in d])
print("largest tap difference when the far end is 20 dB louder:",
      round(max(abs(a - b) for a, b in zip(w_quiet, w_loud)), 12))
```

Eight taps, one $\mu = 0.5$, four far-end signals differing in nothing but correlation.
White input converges in `27` samples. At $\rho = 0.8$ it takes `58`, at $\rho = 0.95$,
`366`, and at $\rho = 0.99$, `676` — twenty-five times slower with the normalisation
working perfectly throughout. The two-tap spread $(1+\rho)/(1-\rho)$ in the third column
is a lower bound on the eight-tap spread by eigenvalue interlacing, and it tracks the
slowdown.

The last line is what normalisation *does* buy: raise the far end by 20 dB and the
converged taps move by `4.15e-10`. Not exactly zero, and the residue is instructive — the
$\varepsilon = 10^{-6}$ that protects against silence is the one term in the denominator
that does not scale with the input, and it is the entire discrepancy. The sandbox *The
samples an echo canceller is actually handed* is about the case that $\varepsilon$ exists
for: a full-amplitude tone at exactly $f_s/2$ whose sampling instants land on the zero
crossings, delivering a window with no energy in it at all.

## Where this stops holding

The mean and mean-square analyses both assume $x(n)$ is independent from one sample to the
next. A tapped delay line makes that false by construction: consecutive input vectors share
$M-1$ of their $M$ entries. The results survive as approximations for small $\mu$, which is
why the practical advice is a fraction of the trace bound rather than the bound itself, and
why $\mu = 0.2$ missed its prediction above.

Convergence *in the mean* is also weaker than it sounds. It says $E[w(n)] \to w_o$, which a
sequence can satisfy while its variance grows without limit. Mean-square convergence is the
stricter condition and the one that matters, and it bites first.

And LMS tracks a moving optimum only when the optimum moves more slowly than the filter
adapts. The capstone changes the room at the midpoint of the call, which is the honest
version of this: one $\mu$ must be small enough for a quiet residual and large enough to
catch the change, and those two demands are the misadjustment trade in another costume.

## What you are about to build

The lab *LMS, NLMS and what normalisation actually buys* is `window(x, n, M)` for the input
vector, `lms(x, d, M, mu)` and `nlms(x, d, M, mu, eps)` returning the final weights and the
*a priori* error for every sample, and `step_bound(x, M)` returning $2/(M\hat{\sigma}_x^2)$
— the `0.661043` above.

One check exists purely to catch the commonest bug in that loop: it asserts that `err[0]`
equals `d[0]` exactly. The weights start at zero, so the first error can only be the
desired sample itself — unless the error was computed *after* the update, in which case it
is the a posteriori error, always smaller, and a learning curve drawn from it will look
handsome while the filter diverges. Another check scales the input and the desired signal
by ten and requires the NLMS weights to be unchanged while plain LMS at a fixed step blows
up, which is the `4.15e-10` line and the hundredfold shift in the bound standing next to
each other.
''',
                },
            ],
            "sandbox": {
                "title": "The samples an echo canceller is actually handed",
                "visualiser": "spectrum",
                "minutes": 8,
                "initial": {"fsig": 190, "fs": 200},
                "brief": r'''
LMS has no model of the world. It correlates the numbers it is given, and adapts
until the residual is uncorrelated with them — whatever those numbers happen to
mean.

The sandbox opens with an interference tone at 190 Hz sampled at 200 Hz, which is
the situation an echo canceller is in when the reference channel is sampled too
slowly.
''',
                "notice": [
                    "The dots trace a slow 10 Hz wave that is nowhere in the true signal. LMS fed this reference converges perfectly happily — on the alias. Nothing in the algorithm can detect the error.",
                    "Raise $f_s$ above $2f_{sig}$ and the samples follow the true tone again. Sampling rate is a system decision the adaptive filter cannot make for you.",
                    "Set $f_{sig}$ to exactly $f_s/2$: the sampling instants land on the zero crossings and every dot drops onto the axis. The reference channel carries a full-amplitude tone and hands the filter an input window of no energy at all — which is why the NLMS step is $\\mu/(\\varepsilon + \\lVert x\\rVert^2)$ and not $\\mu/\\lVert x\\rVert^2$.",
                ],
            },
            "derive": {
                "title": "From the true gradient to LMS, and the price of the substitution",
                "minutes": 15,
                "vars": ["w", "mu", "e", "x", "d", "M", "sigma_x", "E_x", "R",
                         "lambda_max", "n", "misadj"],
                "brief": r'''
Steepest descent needs $R$ and $p$, which require expectations you do not have.
LMS drops the expectation entirely: it minimises the *instantaneous* squared error

$$\hat{J}(n) = e(n)^2, \qquad e(n) = d(n) - w^\top x(n)$$

and takes one gradient step per sample.
''',
                "steps": [
                    {
                        "prompt": "Write the gradient of $\\hat{J} = e^2$ with respect to $w$, in terms of $e$ and $x$.",
                        "answer": "-2 e x",
                        "hint": "Chain rule: $\\nabla e^2 = 2e\\nabla e$, and $e = d - w^\\top x$ depends on $w$ only through that inner product.",
                        "deconstruct": [
                            "$\\nabla_w e = \\nabla_w (d - w^\\top x) = -x$.",
                            "So $\\nabla \\hat{J} = 2e \\cdot (-x)$.",
                        ],
                    },
                    {
                        "prompt": "Step against half that gradient with step size $\\mu$. Write $w(n+1)$ in terms of $w$, $\\mu$, $e$ and $x$.",
                        "answer": "w + \\mu e x",
                        "hint": "The half is chosen precisely so the 2 disappears, as it did in module 2.",
                        "deconstruct": [
                            "$w - \\frac{\\mu}{2}(-2ex)$.",
                            "The two factors of 2 cancel and the sign flips to a plus.",
                        ],
                    },
                    {
                        "prompt": "The stability bound wants $\\lambda_{max}$, which you cannot measure cheaply, so the trace is used instead. For $M$ taps of a stationary input with power $\\sigma_x^2$, write $\\text{trace}(R)$.",
                        "answer": "M \\sigma_x^2",
                        "hint": "Every diagonal entry of $R$ is $r(0)$, and $r(0)$ is the input power.",
                        "deconstruct": [
                            "$R$ has $M$ diagonal entries, each equal to $E[x^2] = \\sigma_x^2$.",
                            "The trace is their sum.",
                        ],
                    },
                    {
                        "prompt": "The trace is the sum of the eigenvalues, so it is at least $\\lambda_{max}$ and the resulting bound is conservative. Write the practical upper bound on $\\mu$ in terms of $M$ and $\\sigma_x$.",
                        "answer": "\\frac{2}{M \\sigma_x^2}",
                        "hint": "Take the bound from module 2 and put the trace where $\\lambda_{max}$ was.",
                        "deconstruct": [
                            "The bound was $2/\\lambda_{max}$.",
                            "Replacing $\\lambda_{max}$ by the larger quantity $\\text{trace}(R)$ gives a smaller, safer step.",
                        ],
                    },
                    {
                        "prompt": "NLMS picks the step that drives the *a posteriori* error $d - w(n+1)^\\top x$ to zero. Writing the instantaneous input energy as $E_x = x^\\top x$, write the step size $\\mu$ that achieves it.",
                        "answer": "\\frac{1}{E_x}",
                        "hint": "Substitute $w(n+1) = w + \\mu e x$ into $d - w(n+1)^\\top x$; you get $e(1 - \\mu E_x)$.",
                        "deconstruct": [
                            "$d - (w + \\mu ex)^\\top x = e - \\mu e\\,x^\\top x = e(1 - \\mu E_x)$.",
                            "That vanishes when $\\mu E_x = 1$.",
                        ],
                    },
                    {
                        "prompt": "The gradient noise never dies, so LMS settles above $J_{min}$ by a fraction $\\mu\\,\\text{trace}(R)/2$. Write that misadjustment in terms of $\\mu$, $M$ and $\\sigma_x$.",
                        "answer": "\\frac{\\mu M \\sigma_x^2}{2}",
                        "hint": "You already wrote the trace two steps ago; substitute it.",
                        "deconstruct": [
                            "$\\text{trace}(R) = M\\sigma_x^2$.",
                            "Multiply by $\\mu$ and halve it.",
                        ],
                    },
                ],
                "closing": r'''
Look at the last result next to the time constant $1/(\mu\lambda)$ from module 2.
Misadjustment is proportional to $\mu$; convergence time is proportional to
$1/\mu$. Their product does not contain $\mu$ at all. You are not choosing between
a good filter and a bad one — you are choosing where on a fixed curve to sit.
''',
            },
            "quiz": {
                "title": "One sample instead of an expectation",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What does LMS substitute for the true gradient?",
                        "opts": [
                            "$-2e(n)x(n)$ — the gradient of the instantaneous squared error",
                            "A running average of past gradients",
                            "A finite difference of the cost",
                            "The Wiener solution",
                        ],
                        "a": 0,
                        "why": r"""
Drop the expectation and use the single most recent sample. It is an unbiased estimate —
its mean is the true gradient — and it is extremely noisy, which is the entire character
of the algorithm: it works because the noise averages out over many steps, and it never
settles exactly because the noise never stops. The step size controls that trade
directly.
""",
                    },
                    {
                        "q": "What does one LMS update cost, for an $M$-tap filter?",
                        "opts": [
                            "About $2M$ multiplications",
                            "About $M^2$",
                            "About $M^3$",
                            "About $M\\log M$",
                        ],
                        "a": 0,
                        "why": r"""
$M$ to compute the output, $M$ to apply the update, no division and no matrix anywhere.
That is the reason LMS is in every echo canceller and equaliser ever shipped: it is
about as cheap as an FIR filter you were running anyway. RLS gets the same answer far
faster and costs $M^2$ per sample, and choosing between them is almost always a budget
question rather than a statistical one.
""",
                    },
                    {
                        "q": "What is misadjustment?",
                        "opts": [
                            "The excess error left over because the weights keep jittering around the optimum",
                            "The bias of the converged solution",
                            "The error caused by too few taps",
                            "The delay before convergence begins",
                        ],
                        "a": 0,
                        "why": r"""
LMS never stops moving: the gradient noise keeps kicking the weights around $w_o$, and
the resulting excess mean-square error is proportional to $\mu$. So the step size buys
speed with accuracy, in a straight trade — and that is why practical implementations
start with a large $\mu$ and reduce it once the filter has converged. It is not bias:
the *mean* of the weights is correct.
""",
                    },
                    {
                        "q": "What does NLMS divide the step size by?",
                        "opts": [
                            "The input power $\\|x(n)\\|^2$",
                            "The number of taps",
                            "The error magnitude",
                            "The time index",
                        ],
                        "a": 0,
                        "why": r"""
$\mu/(\varepsilon + \|x\|^2)$, which makes the effective step independent of the input
level. It matters because the stability bound depends on the input power, so a fixed
$\mu$ tuned on quiet speech diverges on loud speech. Normalising turns the tuning
parameter into a dimensionless number between 0 and 2, which is the real practical win.
The $\varepsilon$ is there to survive silence.
""",
                    },
                    {
                        "q": "How does LMS's stability bound compare with steepest descent's?",
                        "opts": [
                            "The same in the mean, but practice needs a good deal less",
                            "Much larger, because the update is noisier",
                            "Identical in every respect",
                            "There is no bound for LMS",
                        ],
                        "a": 0,
                        "why": r"""
Convergence *in the mean* gives the same $0 < \mu < 2/\lambda_{max}$, because the
expected update is the steepest-descent update. But the mean is not the whole story:
convergence in mean *square* is a stricter condition, and a $\mu$ that satisfies the
first can still let the variance grow. In practice people use a small fraction of the
bound, often $2/(3\,\text{tr}\,R)$ or less.
""",
                    },
                ],
            },
            "lab": {
                "title": "LMS, NLMS and what normalisation actually buys",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Both algorithms are one loop over the samples.

- `window(x, n, M)` returns the input vector $[x(n), x(n-1), \dots, x(n-M+1)]$ as a
  length-`M` array, zero-padded where the index would go negative. Most-recent
  sample first.
- `lms(x, d, M, mu)` returns `(w, err)`: the final weights and an array of the
  *a priori* errors $e(n) = d(n) - w(n)^\top x(n)$, one per sample. The error is
  computed **before** the update, from the weights the filter had at the time.
- `nlms(x, d, M, mu, eps=1e-6)` is the same loop with the step divided by
  $\varepsilon + x^\top x$.
- `step_bound(x, M)` returns $2/(M\hat{\sigma}_x^2)$, using the measured mean square
  of `x`.

Start the weights at zero in both, so `err[0]` is exactly `d[0]`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def window(x, n, M):
    """[x(n), x(n-1), ..., x(n-M+1)], zeros where the index runs off the start."""
    x = np.asarray(x, dtype=float)
    u = np.zeros(M)
    # TODO
    return u


def lms(x, d, M, mu):
    """Least mean squares. Return (final weights, a priori error per sample)."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    err = np.zeros(x.size)
    # TODO: for each n, form the window, compute e, store it, then update w.
    return w, err


def nlms(x, d, M, mu, eps=1e-6):
    """Normalised LMS: the same update with the step divided by the input energy."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    err = np.zeros(x.size)
    # TODO
    return w, err


def step_bound(x, M):
    """The practical LMS bound 2 / (M * mean square of x)."""
    x = np.asarray(x, dtype=float)
    # TODO
    return 0.0


if __name__ == "__main__":
    rng = np.random.default_rng(11)
    x = rng.standard_normal(4000)
    h = np.array([1.0, -0.5, 0.25])
    d = np.convolve(x, h)[:4000] + 0.01 * rng.standard_normal(4000)
    w, err = lms(x, d, 3, 0.01)
    print("step bound:", round(step_bound(x, 3), 6))
    print("LMS taps: ", np.round(w, 4).tolist())
    wn, errn = nlms(x, d, 3, 0.5)
    print("NLMS taps:", np.round(wn, 4).tolist())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def window(x, n, M):
    """[x(n), x(n-1), ..., x(n-M+1)], zeros where the index runs off the start."""
    x = np.asarray(x, dtype=float)
    u = np.zeros(M)
    lo = max(0, n - M + 1)
    seg = x[lo:n + 1][::-1]
    u[:seg.size] = seg
    return u


def lms(x, d, M, mu):
    """Least mean squares. Return (final weights, a priori error per sample)."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    err = np.zeros(x.size)
    for n in range(x.size):
        u = window(x, n, M)
        e = float(d[n] - w @ u)
        err[n] = e
        w = w + mu * e * u
    return w, err


def nlms(x, d, M, mu, eps=1e-6):
    """Normalised LMS: the same update with the step divided by the input energy."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    err = np.zeros(x.size)
    for n in range(x.size):
        u = window(x, n, M)
        e = float(d[n] - w @ u)
        err[n] = e
        w = w + mu * e * u / (eps + float(u @ u))
    return w, err


def step_bound(x, M):
    """The practical LMS bound 2 / (M * mean square of x)."""
    x = np.asarray(x, dtype=float)
    return float(2.0 / (M * np.mean(x * x)))


if __name__ == "__main__":
    rng = np.random.default_rng(11)
    x = rng.standard_normal(4000)
    h = np.array([1.0, -0.5, 0.25])
    d = np.convolve(x, h)[:4000] + 0.01 * rng.standard_normal(4000)
    w, err = lms(x, d, 3, 0.01)
    print("step bound:", round(step_bound(x, 3), 6))
    print("LMS taps: ", np.round(w, 4).tolist())
    wn, errn = nlms(x, d, 3, 0.5)
    print("NLMS taps:", np.round(wn, 4).tolist())
'''}],
                "hints": [
                    "`x[max(0, n - M + 1):n + 1][::-1]` is the window in the right order; write it into the front of a zero array so short windows pad at the back.",
                    "Store the error before updating the weights. Computing it after the update gives the a posteriori error, which is always smaller and hides divergence.",
                    "`float(u @ u)` is the instantaneous input energy that NLMS divides by.",
                ],
                "tests": [
                    {"name": "the input window is ordered and zero-padded", "code": r'''
import numpy as np
_x = np.array([1.0, 2.0, 3.0, 4.0])
_u = window(_x, 3, 3)
assert _u.shape == (3,), f"the window should have M entries, got {_u.shape}"
assert np.allclose(_u, [4.0, 3.0, 2.0]), \
    f"the most recent sample comes first: expected [4, 3, 2], got {_u.tolist()}"
_u0 = window(_x, 0, 3)
assert np.allclose(_u0, [1.0, 0.0, 0.0]), \
    f"before the record starts the filter sees zeros: expected [1, 0, 0], got {_u0.tolist()}"
'''},
                    {"name": "LMS identifies a three-tap channel", "code": r'''
import numpy as np
_rng = np.random.default_rng(11)
_x = _rng.standard_normal(4000)
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:4000] + 0.01 * _rng.standard_normal(4000)
_w, _e = lms(_x, _d, 3, 0.01)
assert _e.shape == (4000,), f"one error per sample, got {_e.shape}"
assert abs(_e[0] - _d[0]) < 1e-12, \
    f"the weights start at zero, so the first a priori error is d[0] = {_d[0]:.6f}; got {_e[0]:.6f} (are you storing the error after the update?)"
assert np.max(np.abs(_w - _h)) < 0.02, \
    f"LMS should land on the channel taps {_h.tolist()}; got {np.round(_w, 4).tolist()}"
'''},
                    {"name": "the step bound is read from the input power", "code": r'''
import numpy as np
_rng = np.random.default_rng(11)
_x = _rng.standard_normal(4000)
_b = step_bound(_x, 3)
_want = float(2.0 / (3 * np.mean(_x * _x)))
assert abs(_b - _want) < 1e-12, f"expected 2/(M * mean square) = {_want:.6f}, got {_b:.6f}"
assert abs(_b - 0.6668452909704738) < 1e-6, \
    f"for this unit-power input with 3 taps the bound is about 0.6668; got {_b:.6f}"
'''},
                    {"name": "a step past the bound destroys the filter", "code": r'''
import numpy as np
_rng = np.random.default_rng(11)
_x = _rng.standard_normal(4000)
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:4000] + 0.01 * _rng.standard_normal(4000)
_w, _e = lms(_x, _d, 3, 1.5 * step_bound(_x, 3))
_blew_up = (not np.all(np.isfinite(_w))) or float(np.max(np.abs(_w))) > 1e3
assert _blew_up, \
    f"at 1.5x the bound the weight error grows every iteration and must run away; got {np.round(_w, 4).tolist()}"
_w2, _e2 = lms(_x, _d, 3, 0.5 * step_bound(_x, 3))
assert np.max(np.abs(_w2 - _h)) < 0.05, \
    f"at half the bound it should still converge; got {np.round(_w2, 4).tolist()}"
'''},
                    {"name": "NLMS does not care how loud the input is", "code": r'''
import numpy as np
_rng = np.random.default_rng(11)
_x = _rng.standard_normal(4000)
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:4000] + 0.01 * _rng.standard_normal(4000)
_w1, _ = nlms(_x, _d, 3, 0.5)
_w2, _ = nlms(10 * _x, 10 * _d, 3, 0.5)
assert np.max(np.abs(_w1 - _w2)) < 1e-6, \
    f"scaling input and desired signal together must leave the NLMS weights unchanged; they moved by {np.max(np.abs(_w1 - _w2)):.3e}"
_l1, _ = lms(_x, _d, 3, 0.05)
_l2, _ = lms(10 * _x, 10 * _d, 3, 0.05)
assert np.max(np.abs(_l1 - _h)) < 0.05, "plain LMS at mu = 0.05 is stable at this input power"
assert (not np.all(np.isfinite(_l2))) or float(np.max(np.abs(_l2))) > 1e3, \
    "the same LMS step size on a 10x louder input is 100x past the bound and must diverge — that is the whole point of normalising"
'''},
                    {"name": "a bigger step costs steady-state accuracy", "code": r'''
import numpy as np
_rng = np.random.default_rng(5)
_x = _rng.standard_normal(30000)
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:30000] + 0.3 * _rng.standard_normal(30000)
_, _e_slow = lms(_x, _d, 3, 0.002)
_, _e_fast = lms(_x, _d, 3, 0.2)
_slow = float(np.mean(_e_slow[-15000:] ** 2))
_fast = float(np.mean(_e_fast[-15000:] ** 2))
assert _slow < 0.095, f"with mu = 0.002 the tail MSE should sit just above the 0.09 noise floor; got {_slow:.5f}"
assert _fast > 1.3 * _slow, \
    f"misadjustment grows with mu: the tail MSE at mu = 0.2 ({_fast:.5f}) should clearly exceed the one at mu = 0.002 ({_slow:.5f})"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "RLS, forgetting and misadjustment",
            "summary": "Solve the least-squares problem exactly at every sample. It converges in a few taps' worth of data and costs you a matrix.",
            "concepts": [
                "Exponentially weighted least squares: minimise $\\sum_i \\lambda^{n-i}e(i)^2$ rather than an expectation.",
                "The matrix inversion lemma turns the update of $R^{-1}$ into a rank-one correction, giving $O(M^2)$ per sample instead of $O(M^3)$.",
                "The gain vector $k(n) = P(n-1)x(n)/(\\lambda + x^\\top P(n-1)x)$ is a Kalman gain in all but name.",
                "$\\lambda$ sets the memory: about $1/(1-\\lambda)$ samples. Short memory tracks a changing system and raises misadjustment.",
                "The covariance recursion loses symmetry to rounding and will diverge; symmetrising $P$ each step costs nothing and fixes it.",
            ],
            "read": [
                {
                    "title": "Twenty-five samples, and what they cost",
                    "minutes": 17,
                    "body": r'''
The far end from module 3 at its most correlated: an AR(1) process with $\rho = 0.99$,
driving an eight-tap room. Normalised LMS needed 676 samples to bring every tap within
0.02 of the truth. Give the same recording to recursive least squares.

```python
import math
import random

ROOM = [0.60, -0.35, 0.22, -0.14, 0.09, -0.05, 0.03, -0.02]
M = len(ROOM)


def call(N=4000, rho=0.99):
    g = random.Random(31)
    mic = random.Random(32)
    scale = math.sqrt(1.0 - rho * rho)
    x = [0.0] * N
    for n in range(1, N):
        x[n] = rho * x[n - 1] + scale * g.gauss(0.0, 1.0)
    d = [sum(ROOM[k] * x[n - k] for k in range(M) if n - k >= 0)
         + 0.001 * mic.gauss(0.0, 1.0) for n in range(N)]
    return x, d


def rls(x, d, lam=0.99, delta=0.01, tol=0.02):
    w = [0.0] * M
    P = [[(1.0 / delta if i == j else 0.0) for j in range(M)] for i in range(M)]
    hit = None
    for n in range(len(x)):
        u = [x[n - k] if n - k >= 0 else 0.0 for k in range(M)]
        pi = [sum(P[i][j] * u[j] for j in range(M)) for i in range(M)]
        den = lam + sum(u[i] * pi[i] for i in range(M))
        k = [v / den for v in pi]
        e = d[n] - sum(w[i] * u[i] for i in range(M))
        w = [w[i] + k[i] * e for i in range(M)]
        P = [[(P[i][j] - k[i] * pi[j]) / lam for j in range(M)] for i in range(M)]
        P = [[0.5 * (P[i][j] + P[j][i]) for j in range(M)] for i in range(M)]
        if hit is None and max(abs(w[i] - ROOM[i]) for i in range(M)) < tol:
            hit = n + 1
    return w, hit


def nlms(x, d, mu=0.5, tol=0.02):
    w = [0.0] * M
    hit = None
    for n in range(len(x)):
        u = [x[n - k] if n - k >= 0 else 0.0 for k in range(M)]
        e = d[n] - sum(w[i] * u[i] for i in range(M))
        energy = 1e-6 + sum(v * v for v in u)
        for i in range(M):
            w[i] += mu * e * u[i] / energy
        if hit is None and max(abs(w[i] - ROOM[i]) for i in range(M)) < tol:
            hit = n + 1
    return w, hit


x, d = call()
w_r, n_r = rls(x, d)
w_n, n_n = nlms(x, d)
print("RLS  converged at sample", n_r, " taps", [round(v, 4) for v in w_r[:4]], "...")
print("NLMS converged at sample", n_n, " taps", [round(v, 4) for v in w_n[:4]], "...")
```

`RLS converged at sample 25`. Eight taps, twenty-five samples, on the input that took
normalised LMS twenty-seven times longer. Both end up on the same room. Something in that
loop is doing what no scalar step size could.

## What $P$ turns out to be

RLS is defined by its criterion rather than by its recursion: at every sample it minimises
the exponentially weighted sum of squared errors

$$\sum_{i=0}^{n} \lambda^{\,n-i}\,e(i)^2$$

exactly, over all $w$. Differentiating gives a normal equation identical in form to
module 1, with the deterministic sums in place of expectations:

$$R(n)\,w(n) = p(n), \qquad
  R(n) = \sum_i \lambda^{n-i} u(i)u(i)^\top, \qquad
  p(n) = \sum_i \lambda^{n-i} d(i)u(i)$$

Both accumulators obey a one-line recursion, $R(n) = \lambda R(n-1) + u(n)u(n)^\top$, so
the only expensive part is the inverse — $O(M^3)$ per sample if it is redone from scratch.
The matrix inversion lemma removes exactly that: a rank-one update of $R$ corresponds to a
rank-one update of $R^{-1}$, which is $O(M^2)$. The claim is that the matrix `P` in the
listing above *is* $R(n)^{-1}$, having never inverted anything. Check it against an
explicit inverse.

```python
import math
import random

M = 3
ROOM = [1.0, -0.5, 0.25]
LAM, DELTA = 0.98, 0.01


def solve(A, b):
    n = len(b)
    aug = [list(row) + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        piv = max(range(i, n), key=lambda t: abs(aug[t][i]))
        aug[i], aug[piv] = aug[piv], aug[i]
        for j in range(i + 1, n):
            f = aug[j][i] / aug[i][i]
            for c in range(i, n + 1):
                aug[j][c] -= f * aug[i][c]
    v = [0.0] * n
    for i in range(n - 1, -1, -1):
        v[i] = (aug[i][n] - sum(aug[i][c] * v[c] for c in range(i + 1, n))) / aug[i][i]
    return v


g = random.Random(17)
N = 60
x = [g.gauss(0.0, 1.0) for _ in range(N)]

P = [[(1.0 / DELTA if i == j else 0.0) for j in range(M)] for i in range(M)]
Racc = [[(DELTA if i == j else 0.0) for j in range(M)] for i in range(M)]
print("  n    max |P - (weighted R)^-1|")
for n in range(N):
    u = [x[n - k] if n - k >= 0 else 0.0 for k in range(M)]
    pi = [sum(P[i][j] * u[j] for j in range(M)) for i in range(M)]
    den = LAM + sum(u[i] * pi[i] for i in range(M))
    k = [v / den for v in pi]
    P = [[(P[i][j] - k[i] * pi[j]) / LAM for j in range(M)] for i in range(M)]
    Racc = [[LAM * Racc[i][j] + u[i] * u[j] for j in range(M)] for i in range(M)]
    inv = [solve(Racc, [1.0 if i == c else 0.0 for i in range(M)]) for c in range(M)]
    gap = max(abs(P[i][j] - inv[j][i]) for i in range(M) for j in range(M))
    if n + 1 in (3, 10, 30, 60):
        print(f"{n + 1:4d}          {gap:.3e}")
```

After three samples the recursively maintained `P` and the explicitly inverted accumulator
agree to `1.810e-14`, and the gap falls from there — `3.220e-15`, `1.318e-16`,
`2.255e-17` — as $P$ itself shrinks. They are the same matrix.

Read the weight update with that in hand. LMS was $w \leftarrow w + \mu\,e\,u$: the
gradient direction, scaled by a number. RLS is $w \leftarrow w + P u\,e$: the same
gradient direction, premultiplied by $R^{-1}$. Module 3 ended on the observation that a
scalar rescales the bowl and only a matrix can reshape it. This is the matrix. The
eigenvalue spread that cost 200 iterations in module 2 and 676 samples in module 3 is
divided out of the update, which is why 25 samples were enough on input at $\rho = 0.99$.

The gain $k = Pu/(\lambda + u^\top Pu)$ is a Kalman gain and $P$ an inverse covariance,
which is worth carrying: the blanks unit *RLS, and what forgetting costs* leans on that
correspondence, and the division by $\lambda$ in the $P$ recursion is the analogue of a
Kalman predict step adding process noise.

## $\lambda$ is a memory, measured in samples

The weight on a sample $i$ steps back is $\lambda^i$, and those weights sum to
$1/(1-\lambda)$, so the estimate is effectively an average over that many samples:
100 at $\lambda = 0.99$, 1000 at $\lambda = 0.999$. The derive unit *Memory, forgetting
and the fixed price of speed* does that geometric series and then inverts it, and the
sandbox *The forgetting factor is a pole* draws the weighting as the impulse response of a
single pole at $z = \lambda$, which is exactly what it is.

## The mistake: $\lambda = 1$, because more data is better

$\lambda = 1$ makes RLS the exact least-squares solution over the whole record. For a
system that never changes, that is optimal and provably so, and it is the reason the
choice is tempting: every sample is used, nothing is discarded, and the estimate keeps
improving. Change the room halfway through and read the same table again.

```python
import random

M = 3
H1 = [1.0, -0.5, 0.25]
H2 = [0.4, 0.8, -0.3]
SWITCH = 4000


def run(lam, N=8000, delta=0.01):
    g = random.Random(41)
    mic = random.Random(42)
    x = [g.gauss(0.0, 1.0) for _ in range(N)]
    w = [0.0] * M
    P = [[(1.0 / delta if i == j else 0.0) for j in range(M)] for i in range(M)]
    out = {}
    for n in range(N):
        u = [x[n - k] if n - k >= 0 else 0.0 for k in range(M)]
        room = H1 if n < SWITCH else H2
        d = sum(room[i] * u[i] for i in range(M)) + 0.02 * mic.gauss(0.0, 1.0)
        pi = [sum(P[i][j] * u[j] for j in range(M)) for i in range(M)]
        den = lam + sum(u[i] * pi[i] for i in range(M))
        k = [v / den for v in pi]
        e = d - sum(w[i] * u[i] for i in range(M))
        w = [w[i] + k[i] * e for i in range(M)]
        P = [[(P[i][j] - k[i] * pi[j]) / lam for j in range(M)] for i in range(M)]
        P = [[0.5 * (P[i][j] + P[j][i]) for j in range(M)] for i in range(M)]
        for mark in (SWITCH - 1, SWITCH + 99, SWITCH + 499, SWITCH + 3999):
            if n == mark:
                ref = H1 if n < SWITCH else H2
                out[mark] = max(abs(w[i] - ref[i]) for i in range(M))
    return out


print("           before   +100 after  +500 after  +4000 after")
for lam in (0.98, 0.999, 1.0):
    o = run(lam)
    print(f"lam={lam:<6} {o[SWITCH - 1]:.5f}    {o[SWITCH + 99]:.5f}     "
          f"{o[SWITCH + 499]:.5f}     {o[SWITCH + 3999]:.5f}")
```

Before the switch, $\lambda = 1$ is the best of the three by an order of magnitude:
`0.00008` against `0.00211` for $\lambda = 0.98$. Every promise it makes is kept. One
hundred samples after the switch all three are wrong, as they must be. Five hundred
samples after it, $\lambda = 0.98$ is back to `0.00377` while $\lambda = 1$ still reads
`1.16954`. Four thousand samples later — half a second at 8 kHz — it is at `0.63994`,
which is a tap error larger than most of the taps.

The mechanism is in the gain. With $\lambda = 1$ the accumulator $R(n)$ grows without
bound, so $P = R^{-1}$ shrinks like $1/n$ and so does $k$. By sample 4000 the correction
applied to each new error is a four-thousandth of what it was at the start. The algorithm
has not broken; it has finished. Forgetting is what keeps the gain alive, and an
adaptive filter that cannot forget is a filter that adapts once.

## And the bill for forgetting

```python
import random

M = 3
ROOM = [1.0, -0.5, 0.25]


def tail_error(lam, N=20000, delta=0.01, noise=0.1):
    g = random.Random(51)
    mic = random.Random(52)
    x = [g.gauss(0.0, 1.0) for _ in range(N)]
    w = [0.0] * M
    P = [[(1.0 / delta if i == j else 0.0) for j in range(M)] for i in range(M)]
    acc = 0.0
    half = N // 2
    for n in range(N):
        u = [x[n - k] if n - k >= 0 else 0.0 for k in range(M)]
        d = sum(ROOM[i] * u[i] for i in range(M)) + noise * mic.gauss(0.0, 1.0)
        pi = [sum(P[i][j] * u[j] for j in range(M)) for i in range(M)]
        den = lam + sum(u[i] * pi[i] for i in range(M))
        k = [v / den for v in pi]
        e = d - sum(w[i] * u[i] for i in range(M))
        w = [w[i] + k[i] * e for i in range(M)]
        P = [[(P[i][j] - k[i] * pi[j]) / lam for j in range(M)] for i in range(M)]
        P = [[0.5 * (P[i][j] + P[j][i]) for j in range(M)] for i in range(M)]
        if n >= half:
            acc += sum((w[i] - ROOM[i]) ** 2 for i in range(M))
    return acc / (N - half)


print("  lam    memory 1/(1-lam)   mean squared tap error over the second half")
for lam in (0.9, 0.99, 0.999, 1.0):
    mem = "infinite" if lam == 1.0 else f"{1 / (1 - lam):8.0f}"
    print(f"  {lam:<6} {mem:>10}          {tail_error(lam):.3e}")
```

On a room that never moves: `1.692e-03` at $\lambda = 0.9$, `1.785e-04` at $0.99$,
`1.858e-05` at $0.999$. Each factor of ten in memory buys a factor of about ten in the
variance of the taps, which is what averaging over ten times as much data buys anywhere
else. This is RLS's misadjustment, and it is proportional to $1 - \lambda$ in the same way
that LMS's is proportional to $\mu$.

So the shape of the trade survives the change of algorithm. What RLS buys is a better
curve to sit on — convergence in a few multiples of $M$ rather than in a few multiples of
the eigenvalue spread — and it pays $O(M^2)$ per sample for it, against LMS's $2M$. At
$M = 512$ that is 256 times the arithmetic, which is why the cheap algorithm is still the
one in most shipping hardware.

## Where this stops holding

The recursion assumes the input keeps exciting every direction. Let the far end go silent
with $\lambda < 1$ and the update contributes nothing while the division by $\lambda$
continues, so $P$ grows as $\lambda^{-n}$: at $\lambda = 0.99$, one per cent per sample,
which doubles $P$ in seventy samples and multiplies it by $10^{34}$ over a second at
8 kHz. The next loud sample then arrives at a filter with an enormous gain and throws the
weights across the room. This is covariance windup, it is the reason real echo cancellers
freeze adaptation when the far end is quiet, and it is a failure mode LMS does not have.

The arithmetic is fragile in a second way. $P$ is symmetric in exact arithmetic, and the
rank-one update is not symmetric in floating point; the asymmetry compounds, the matrix
loses positive definiteness, and the weights go to `nan`. The one-line remedy
$P \leftarrow (P + P^\top)/2$ appears in every listing above for that reason and nowhere
in the algebra.

Finally, RLS is optimal for a criterion that is not the one module 1 posed. It minimises a
weighted sum over the data it happened to see, not $E[e^2]$, so its solution is a random
variable even after convergence — the `1.785e-04` above is not measurement error, it is
the estimate itself moving.

## What you are about to build

The lab *Recursive least squares, and what the forgetting factor does* gives you
`lms_weights` already written, so that the comparison in the first listing can be made
sample by sample, and asks for `rls(x, d, M, lam=0.99, delta=0.01)` returning the whole
weight history. Its checks are the four measurements above: RLS converged by sample 200 on
input at $\rho = 0.95$ while LMS is still more than 0.5 away; $\lambda = 0.9$ following a
channel change that $\lambda = 0.9999$ cannot see; every weight finite after 8000 samples,
which is the symmetrising line being tested rather than described; and two values of
`delta` reaching the same answer from different starting speeds, because $\delta$ sets
$P(0)$ and nothing else.
''',
                },
            ],
            "quiz": {
                "title": "Buying convergence, and what the invoice says",
                "minutes": 8,
                "questions": [
                    {
                        "q": "On far-end input at $\\rho = 0.99$ with eight taps, RLS is converged by sample 25 and NLMS needs 676. What does RLS have that normalisation does not?",
                        "opts": [
                            "A smaller effective step, so the correlation in the input disturbs its trajectory much less than it disturbs the other",
                            "An update premultiplied by an estimate of $R^{-1}$, which is a matrix and can reshape the bowl",
                            "Access to the whole record rather than one sample, so each update is computed from far more data",
                            "A gain normalised by the input energy, which the other only approximates with a single scalar",
                        ],
                        "a": 1,
                        "whys": [
                            r"A smaller step slows everything down; it does not make a badly conditioned problem well conditioned. Shrinking $\mu$ in NLMS lengthens the 676 rather than shortening it.",
                            r"$w \leftarrow w + Pue$ against $w \leftarrow w + \mu eu$: the direction is the same and the thing in front of it is not.",
                            r"RLS also sees one sample per update. What it keeps is a running $M \times M$ summary of everything before it, which is a different claim and the interesting one.",
                            r"NLMS divides by the input energy exactly, not approximately, and that is why its weights are unchanged to $4\times10^{-10}$ when the far end is 20 dB louder. Energy normalisation is the part both have.",
                        ],
                        "why": r"""
Both updates move along $e\,u$. LMS multiplies that by a number, NLMS by a number derived
from $u^\top u$, and RLS by the matrix $P \approx R^{-1}$. Only the matrix can change the
*shape* of the error surface, and the shape is what the eigenvalue spread measures. Divide
$R$ out of the update and a spread of 200 stops costing anything — at the price of
$O(M^2)$ arithmetic and a covariance matrix to look after.
""",
                    },
                    {
                        "q": "With $\\lambda = 1$ on a stationary room, RLS reaches a tap error of 0.00008 — an order of magnitude better than $\\lambda = 0.98$. Four thousand samples after the room changes it still reads 0.63994. What has gone wrong?",
                        "opts": [
                            "The accumulated $R(n)$ grows without bound, so the gain shrinks like $1/n$ and new errors barely move the weights",
                            "The covariance $P$ has lost its symmetry to rounding, and the recursion is drifting towards divergence",
                            "At $\\lambda = 1$ the criterion is no longer least squares, so the fixed point it converges to is not the true room",
                            "The old and the new room are being averaged together, and the average is what it converged on originally",
                        ],
                        "a": 0,
                        "whys": [
                            r"$P = R^{-1}$ and $R$ has been accumulating since sample 0, so by sample 4000 each correction is a four-thousandth of its original size.",
                            r"Symmetry loss is a real RLS failure and it looks nothing like this: it produces `nan` or a blow-up, not a stable, confidently wrong answer that was accurate before the change.",
                            r"$\lambda = 1$ is the *purest* least-squares case — every residual weighted equally — and its fixed point on stationary data is exactly right, which is the 0.00008.",
                            r"An average of the two rooms would sit between them and would keep moving towards the new one as data accumulated. This estimate is stuck near the old room and getting there more slowly every sample.",
                        ],
                        "why": r"""
$\lambda = 1$ keeps every sample at full weight, so $R(n)$ grows linearly, $P$ shrinks like
$1/n$, and the gain $k$ with it. That is correct behaviour for a system that never changes:
confidence should grow and the steps should shorten. It also means the filter has stopped
being adaptive. Forgetting is what holds the gain up, and $1/(1-\lambda)$ is how many
samples it holds it up over.
""",
                    },
                    {
                        "q": "A room that never moves, and $\\lambda$ taken from 0.9 to 0.99 to 0.999. The mean squared tap error falls by a factor of about ten each time. Why that factor?",
                        "opts": [
                            "Each step multiplies the gain by ten, and the tap error is inversely proportional to the gain",
                            "Each step multiplies the effective averaging length by ten, and averaging cuts variance in proportion",
                            "Each step reduces the eigenvalue spread of the weighted correlation matrix by exactly the same factor of ten",
                            "Each step lengthens the record, so the filter has ten times as many samples to work with by the end",
                        ],
                        "a": 1,
                        "whys": [
                            r"The gain does fall as $\lambda$ rises, but a gain is not an error. What links the two is how many independent samples the estimate rests on, and that is the memory.",
                            r"Memory $1/(1-\lambda)$ goes 10, 100, 1000, and the variance of an average of $N$ samples goes as $1/N$.",
                            r"The spread belongs to the input spectrum. $\lambda$ changes how much history is weighted in, not the shape of the input's correlation.",
                            r"The record is 20000 samples long in all three runs, and the measurement is taken over the same second half of it. Nothing about the amount of available data changed.",
                        ],
                        "why": r"""
This is ordinary averaging arithmetic wearing an exponential window. The estimate is
effectively formed from $1/(1-\lambda)$ samples, and the variance of an average falls as
one over the number of samples averaged — so ten times the memory, a tenth of the tap
variance. It is also the exact counterpart of LMS's misadjustment being proportional to
$\mu$: the same trade, different knob.
""",
                    },
                    {
                        "q": "$\\delta$ initialises $P$ to $I/\\delta$. Two runs with $\\delta = 0.001$ and $\\delta = 0.1$ end within $10^{-3}$ of each other but differ early on. What is $\\delta$?",
                        "opts": [
                            "A regularisation term that biases the converged weights towards zero, by an amount proportional to itself",
                            "A second memory parameter, setting the window length in samples in the same way that $\\lambda$ does",
                            "A guard against a singular covariance, which has to be kept above the power of the input for the recursion to stay stable",
                            "A statement of how little you know at the start, which sets the first few steps and is then forgotten",
                        ],
                        "a": 3,
                        "whys": [
                            r"It does act as a ridge term in the very first samples — $R(0) = \delta I$ — and that is what makes this tempting. But the accumulating $u u^\top$ terms swamp $\delta I$ within a few samples, and with $\lambda < 1$ its contribution decays as $\lambda^n$ on top of that.",
                            r"Memory is $1/(1-\lambda)$ and $\delta$ appears nowhere in it. The two runs converge to the same place precisely because $\delta$ has no lasting influence.",
                            r"There is no such stability condition. A small $\delta$ makes $P(0)$ large and the first steps bold, which is a transient, not an instability.",
                            r"A small $\delta$ means a large $P(0)$, which means a large gain while there is no data to contradict it.",
                        ],
                        "why": r"""
$P(0) = I/\delta$ is a prior covariance: small $\delta$ says the initial weights are not to
be trusted, so take big steps; large $\delta$ says the opposite. Either way the data
accumulates into $R(n)$ and overwhelms the prior within a handful of samples, and with
$\lambda < 1$ the prior is actively forgotten at rate $\lambda^n$. The lab checks both
halves of this: the same destination, and a faster start for the smaller $\delta$.
""",
                    },
                    {
                        "q": "An echo canceller runs RLS at $\\lambda = 0.99$ and the far end goes silent for a second at 8 kHz. What happens?",
                        "opts": [
                            "The weights freeze, since a zero input contributes a zero gain and there is nothing to update with",
                            "$P$ is divided by $\\lambda$ 8000 times with nothing added back, and the gain becomes enormous",
                            "The forgetting factor discards the room response, so adaptation restarts from zero when speech returns",
                            "Nothing at all: the error is zero too, and the update is a product of the two",
                        ],
                        "a": 1,
                        "whys": [
                            r"The gain going to zero would indeed be safe, and it is what makes this the comfortable answer. The recursion does the opposite: $P \leftarrow P/\lambda$ runs whether or not the input contributed anything.",
                            r"$0.99^{-8000}$ is about $10^{34}$, and the first loud sample afterwards is multiplied by it.",
                            r"The weights themselves are untouched by a silent stretch — they are only ever changed by $ke$. It is the covariance that moves, and it moves the wrong way.",
                            r"The near-end talker, the microphone noise and the room's own tail all keep the error non-zero while the reference is silent, which is exactly the combination that fires the enormous gain.",
                        ],
                        "why": r"""
This is covariance windup. With no excitation the rank-one term adds nothing while the
division by $\lambda$ keeps inflating $P$, so the filter's stated uncertainty grows without
any information arriving to justify it. One per cent per sample doubles $P$ in seventy
samples and reaches $10^{34}$ over a second. Real systems detect far-end silence and freeze
the update, or bound $P$ directly. LMS has no analogue of this: a zero input gives a zero
update and nothing accumulates.
""",
                    },
                    {
                        "q": "Every RLS listing here ends its update with $P \\leftarrow (P + P^\\top)/2$. What is that line for?",
                        "opts": [
                            "It enforces in floating point a symmetry the algebra guarantees but the rank-one update does not preserve",
                            "It restores the positive definiteness that the division by $\\lambda$ removes on every single iteration of the loop",
                            "It is the projection step that keeps the weight vector inside the region where the lemma is valid",
                            "It halves the covariance each step, which is the mechanism by which older samples are forgotten",
                        ],
                        "a": 0,
                        "whys": [
                            r"$P - k\pi^\top$ is symmetric on paper and is computed as two different roundings off the diagonal, so the asymmetry compounds until $P$ stops being a covariance at all.",
                            r"Dividing by $\lambda$ scales every eigenvalue by the same positive factor and cannot change a sign. Loss of definiteness here is a symptom of the accumulated asymmetry, not of the division.",
                            r"The matrix inversion lemma is an identity with no region of validity, and this line touches $P$ rather than $w$.",
                            r"$(P + P^\top)/2$ is an average of a matrix with its own transpose, which leaves a symmetric matrix exactly unchanged. Forgetting is the division by $\lambda$, and it is a separate line.",
                        ],
                        "why": r"""
$P$ is a covariance and therefore symmetric, but $(P - k\pi^\top)/\lambda$ computes the
$(i,j)$ and $(j,i)$ entries by different sequences of floating-point operations. The
difference is around $10^{-16}$ per step and it compounds, because an asymmetric $P$ feeds
an asymmetric update. Left alone, a long run ends in `nan`. Averaging $P$ with its
transpose costs $M^2$ additions and removes the failure entirely, which is why the lab
runs 8000 samples and asserts that every weight is still finite.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "The forgetting factor is a pole",
                "visualiser": "z-plane",
                "minutes": 8,
                "initial": {"r": 0.99, "th": 0},
                "brief": r'''
RLS weights a sample $i$ steps into the past by $\lambda^i$. That is the impulse
response of a one-pole filter with the pole at $z = \lambda$, so set the radius to
$\lambda$ and leave the angle at zero: the curve you see is literally how much the
algorithm still cares about each past sample.

Effective memory is roughly $1/(1-\lambda)$ samples.
''',
                "notice": [
                    "At $r = 0.99$ the response is still visible a hundred samples back: memory $1/(1-0.99) = 100$. That is a long average, so a quiet estimate — and a filter that will not notice the room changing.",
                    "Drop $r$ to 0.9. Memory collapses to ten samples. With eight taps to estimate from ten samples of data, the estimate rattles: this is misadjustment, seen directly.",
                    "Take $r$ to 1.0 exactly. Nothing is ever forgotten — growing-window least squares, the lowest misadjustment available and no tracking ability whatsoever.",
                ],
            },
            "derive": {
                "title": "Memory, forgetting and the fixed price of speed",
                "minutes": 13,
                "vars": ["lambda", "i", "n", "N", "M", "mu", "sigma_x", "lambda_min",
                         "misadj", "tau", "R"],
                "brief": r'''
RLS minimises the exponentially weighted sum of squared errors

$$\sum_{i=0}^{n} \lambda^{\,n-i} e(i)^2, \qquad 0 < \lambda \le 1$$

so a sample's influence decays geometrically as it recedes into the past.
''',
                "steps": [
                    {
                        "prompt": "Write the weight that the cost places on a sample $i$ steps in the past.",
                        "answer": "\\lambda^i",
                        "hint": "Set $i = n - $ (sample index) in the exponent above.",
                        "deconstruct": [
                            "The sample at time $n$ has exponent $n - n = 0$, so weight 1.",
                            "The one before it has exponent 1, and so on.",
                        ],
                    },
                    {
                        "prompt": "Sum that weight over all past samples, for $0 < \\lambda < 1$. Write the total.",
                        "answer": "\\frac{1}{1-\\lambda}",
                        "hint": "It is a geometric series with ratio $\\lambda$, starting at 1.",
                        "deconstruct": [
                            "$1 + \\lambda + \\lambda^2 + \\dots$",
                            "A geometric series with $|\\lambda| < 1$ sums to $1/(1-\\lambda)$.",
                        ],
                    },
                    {
                        "prompt": "That total is the effective number of samples the filter is averaging over. If you want a memory of $N$ samples, write $\\lambda$.",
                        "answer": "1 - \\frac{1}{N}",
                        "hint": "Set the previous answer equal to $N$ and solve.",
                        "deconstruct": [
                            "$1/(1-\\lambda) = N$ gives $1 - \\lambda = 1/N$.",
                            "Rearrange for $\\lambda$.",
                        ],
                    },
                    {
                        "prompt": "The correlation estimate obeys $R(n) = \\lambda R(n-1) + x(n)x(n)^\\top$. For white input of power $\\sigma_x^2$, write the value each diagonal entry settles on as $n \\to \\infty$.",
                        "answer": "\\frac{\\sigma_x^2}{1-\\lambda}",
                        "hint": "Take expectations: the steady state satisfies $\\bar{R} = \\lambda\\bar{R} + \\sigma_x^2$.",
                        "deconstruct": [
                            "In steady state the diagonal entry stops changing, so $\\bar{r} = \\lambda\\bar{r} + \\sigma_x^2$.",
                            "Collect $\\bar{r}$ and divide.",
                        ],
                    },
                    {
                        "prompt": "Back to LMS for the comparison. Its misadjustment is $\\mu M\\sigma_x^2/2$ and its slowest time constant is $1/(\\mu\\lambda_{min})$ iterations. Write the product of the two.",
                        "answer": "\\frac{M \\sigma_x^2}{2 \\lambda_{min}}",
                        "hint": "Multiply them and watch what happens to $\\mu$.",
                        "deconstruct": [
                            "$\\left(\\frac{\\mu M\\sigma_x^2}{2}\\right)\\cdot\\frac{1}{\\mu\\lambda_{min}}$.",
                            "The step size cancels, leaving a quantity fixed by the problem alone.",
                        ],
                    },
                ],
                "closing": r'''
The last line is the sentence to remember from the whole course: for LMS, speed
times misadjustment is a constant of the problem, not of your tuning. RLS does not
repeal that trade-off — $\lambda$ moves along its own version of the same curve —
but it buys a much better curve, converging in roughly $2M$ samples regardless of
the eigenvalue spread, in exchange for $O(M^2)$ arithmetic and a covariance matrix
that must be kept symmetric or it will quietly destroy itself.
''',
            },
            "blanks": {
                "title": "RLS, and what forgetting costs",
                "minutes": 9,
                "caption": "rls.py — exact least squares, one sample at a time",
                "lang": "python",
                "brief": r"""
RLS solves the least-squares problem *exactly* at every sample, which is why it converges
in a couple of filter lengths' worth of data rather than a few thousand. The matrix
inversion lemma is what makes that affordable. Fill in the four places $\lambda$ and the
gain appear.
""",
                "listing": """# Minimise  sum_i  lam**(n-i) * e(i)**2   -- exponentially weighted.

k = P @ x / (___ + x.T @ P @ x)      # gain vector
e = d - w.T @ x                      # a priori error, before the update
w = w + ___                          # weight update
P = (P - np.outer(k, x.T @ P)) / ___ # rank-one update of the inverse

# Choosing lam < 1 gives the algorithm an effective memory of
# roughly ___ samples.
""",
                "blanks": [
                    {
                        "prompt": "The forgetting factor appears in the denominator of the gain.",
                        "hole": "?",
                        "opts": ["lam", "1", "1 - lam", "x.T @ x"],
                        "a": 0,
                        "why": "$k = Px/(\\lambda + x^\\top Px)$. With $\\lambda = 1$ this is the growing-window least-squares gain, which shrinks steadily as data accumulates; $\\lambda < 1$ stops it shrinking to nothing and keeps the filter responsive.",
                        "whys": [
                            "$k = Px/(\\lambda + x^\\top Px)$. With $\\lambda = 1$ this is the growing-window least-squares gain, which shrinks steadily as data accumulates; $\\lambda < 1$ stops it shrinking to nothing and keeps the filter responsive.",
                            "A fixed 1 is the special case $\\lambda = 1$ — correct arithmetic for an infinite window, but then the algorithm eventually stops adapting altogether.",
                            "$1 - \\lambda$ is a small number near 0.01, which would make the gain enormous and the recursion unstable.",
                            "The input's own energy without $P$ is the NLMS normaliser, not the RLS one. RLS weights by the inverse correlation matrix, which is where its speed comes from.",
                        ],
                    },
                    {
                        "prompt": "Gain times error.",
                        "hole": "?",
                        "opts": ["k * e", "mu * e * x", "k * d", "e * x"],
                        "a": 0,
                        "why": "$w \\leftarrow w + ke$ — identical in shape to a Kalman correction, which is exactly what it is: $k$ is a Kalman gain and $P$ is an inverse covariance. Seeing that connection makes both algorithms easier to remember.",
                        "whys": [
                            "$w \\leftarrow w + ke$ — identical in shape to a Kalman correction, which is exactly what it is: $k$ is a Kalman gain and $P$ is an inverse covariance. Seeing that connection makes both algorithms easier to remember.",
                            "That is the LMS update. Substituting it here gives up everything RLS was paying for — the whole point is that $k$ already contains the input's correlation structure, and $\\mu x$ does not.",
                            "Correcting by the desired signal rather than the error never converges: even a perfect filter would keep being pushed.",
                            "Missing the gain entirely, so the correlation structure never enters and the update is unscaled.",
                        ],
                    },
                    {
                        "prompt": "And in the P recursion.",
                        "hole": "?",
                        "opts": ["lam", "1 - lam", "1", "x.T @ P @ x"],
                        "a": 0,
                        "why": "Dividing by $\\lambda$ inflates $P$ a little every step, which is what keeps the algorithm willing to move. It is the direct analogue of the Kalman filter's predict step adding process noise — both are the same idea: deliberately forget, so that you can still learn.",
                        "whys": [
                            "Dividing by $\\lambda$ inflates $P$ a little every step, which is what keeps the algorithm willing to move. It is the direct analogue of the Kalman filter's predict step adding process noise — both are the same idea: deliberately forget, so that you can still learn.",
                            "Dividing by $1 - \\lambda$ would multiply $P$ by about 100 every sample and the recursion would explode within a few dozen steps.",
                            "Leaving $P$ undivided is the $\\lambda = 1$ case: $P$ shrinks monotonically and the filter freezes, which is correct only if the statistics never change.",
                            "That scalar is already accounted for inside $k$; applying it again double-counts the update.",
                        ],
                    },
                    {
                        "prompt": "How far back does lambda let it remember?",
                        "hole": "?",
                        "opts": ["1 / (1 - lam)", "lam", "1 - lam", "M"],
                        "a": 0,
                        "why": "$\\lambda = 0.99$ gives a memory of about 100 samples, $\\lambda = 0.999$ about 1000. It is the same $1/(1-\\lambda)$ that governs any exponential average, and it is the knob for the fundamental trade: a short memory tracks a changing environment and a long one rejects noise, and you cannot have both.",
                        "whys": [
                            "$\\lambda = 0.99$ gives a memory of about 100 samples, $\\lambda = 0.999$ about 1000. It is the same $1/(1-\\lambda)$ that governs any exponential average, and it is the knob for the fundamental trade: a short memory tracks a changing environment and a long one rejects noise, and you cannot have both.",
                            "$\\lambda$ itself is just under 1 and does not measure a number of samples.",
                            "This is the reciprocal of the answer — about 0.01 samples, which is not a memory.",
                            "The filter length sets how many taps there are, not how much history the weighting retains.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Recursive least squares, and what the forgetting factor does",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
`lms_weights` is written for you — the same algorithm as module 3, but returning
the whole weight history so the two can be compared iteration by iteration.

Write `rls(x, d, M, lam=0.99, delta=0.01)`, returning `(W, err)` where `W` has shape
`(N, M)` and `W[n]` is the weight vector **after** the update at sample `n`.

The recursion, per sample:

```text
u  = window(x, n, M)
pi = P @ u
k  = pi / (lam + u @ pi)
e  = d[n] - w @ u
w  = w + k * e
P  = (P - outer(k, pi)) / lam
P  = (P + P.T) / 2
```

starting from `w = 0` and `P = I / delta`. That last line is not cosmetic: `P` is
symmetric in exact arithmetic, floating point does not respect that, and the
asymmetry grows until the recursion diverges. One of the checks runs long enough to
prove it.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def window(x, n, M):
    """[x(n), x(n-1), ..., x(n-M+1)], zeros where the index runs off the start."""
    x = np.asarray(x, dtype=float)
    u = np.zeros(M)
    lo = max(0, n - M + 1)
    seg = x[lo:n + 1][::-1]
    u[:seg.size] = seg
    return u


def lms_weights(x, d, M, mu):
    """Module 3's LMS, returning the full weight history for comparison."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    W = np.zeros((x.size, M))
    err = np.zeros(x.size)
    for n in range(x.size):
        u = window(x, n, M)
        e = float(d[n] - w @ u)
        err[n] = e
        w = w + mu * e * u
        W[n] = w
    return W, err


def rls(x, d, M, lam=0.99, delta=0.01):
    """Recursive least squares. Return (weight history, a priori error per sample)."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    P = np.eye(M) / delta
    W = np.zeros((x.size, M))
    err = np.zeros(x.size)
    # TODO: gain, error, weight update, covariance update, symmetrise.
    return W, err


if __name__ == "__main__":
    rng = np.random.default_rng(21)
    v = rng.standard_normal(3000)
    x = np.zeros(3000)
    for n in range(1, 3000):
        x[n] = 0.95 * x[n - 1] + v[n]
    h = np.array([1.0, -0.5, 0.25])
    d = np.convolve(x, h)[:3000] + 0.01 * rng.standard_normal(3000)
    W, err = rls(x, d, 3, 0.99)
    print("RLS taps: ", np.round(W[-1], 5).tolist())
    Wl, _ = lms_weights(x, d, 3, 0.002)
    print("LMS taps: ", np.round(Wl[-1], 5).tolist())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def window(x, n, M):
    """[x(n), x(n-1), ..., x(n-M+1)], zeros where the index runs off the start."""
    x = np.asarray(x, dtype=float)
    u = np.zeros(M)
    lo = max(0, n - M + 1)
    seg = x[lo:n + 1][::-1]
    u[:seg.size] = seg
    return u


def lms_weights(x, d, M, mu):
    """Module 3's LMS, returning the full weight history for comparison."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    W = np.zeros((x.size, M))
    err = np.zeros(x.size)
    for n in range(x.size):
        u = window(x, n, M)
        e = float(d[n] - w @ u)
        err[n] = e
        w = w + mu * e * u
        W[n] = w
    return W, err


def rls(x, d, M, lam=0.99, delta=0.01):
    """Recursive least squares. Return (weight history, a priori error per sample)."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    P = np.eye(M) / delta
    W = np.zeros((x.size, M))
    err = np.zeros(x.size)
    for n in range(x.size):
        u = window(x, n, M)
        pi = P @ u
        k = pi / (lam + float(u @ pi))
        e = float(d[n] - w @ u)
        err[n] = e
        w = w + k * e
        P = (P - np.outer(k, pi)) / lam
        P = 0.5 * (P + P.T)
        W[n] = w
    return W, err


if __name__ == "__main__":
    rng = np.random.default_rng(21)
    v = rng.standard_normal(3000)
    x = np.zeros(3000)
    for n in range(1, 3000):
        x[n] = 0.95 * x[n - 1] + v[n]
    h = np.array([1.0, -0.5, 0.25])
    d = np.convolve(x, h)[:3000] + 0.01 * rng.standard_normal(3000)
    W, err = rls(x, d, 3, 0.99)
    print("RLS taps: ", np.round(W[-1], 5).tolist())
    Wl, _ = lms_weights(x, d, 3, 0.002)
    print("LMS taps: ", np.round(Wl[-1], 5).tolist())
'''}],
                "hints": [
                    "`np.outer(k, pi)` is the rank-one correction; `pi` is `P @ u` computed *before* `P` is updated, so keep it in a variable.",
                    "The a priori error uses the old weights, exactly as in LMS — compute `e` before `w` is updated.",
                    "If a long run produces `nan`, the covariance has lost symmetry. `P = 0.5 * (P + P.T)` after every update is the standard remedy.",
                ],
                "tests": [
                    {"name": "RLS identifies a channel through correlated input", "code": r'''
import numpy as np
_rng = np.random.default_rng(21)
_v = _rng.standard_normal(3000)
_x = np.zeros(3000)
for _n in range(1, 3000):
    _x[_n] = 0.95 * _x[_n - 1] + _v[_n]
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:3000] + 0.01 * _rng.standard_normal(3000)
_W, _e = rls(_x, _d, 3, 0.99)
assert _W.shape == (3000, 3), f"the history should be (N, M), got {_W.shape}"
assert abs(_e[0] - _d[0]) < 1e-12, \
    f"the weights start at zero, so the first a priori error is d[0] = {_d[0]:.6f}; got {_e[0]:.6f}"
assert np.max(np.abs(_W[-1] - _h)) < 0.01, \
    f"RLS should land on {_h.tolist()}; got {np.round(_W[-1], 4).tolist()}"
'''},
                    {"name": "RLS converges while LMS is still nowhere near", "code": r'''
import numpy as np
_rng = np.random.default_rng(21)
_v = _rng.standard_normal(3000)
_x = np.zeros(3000)
for _n in range(1, 3000):
    _x[_n] = 0.95 * _x[_n - 1] + _v[_n]
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:3000] + 0.01 * _rng.standard_normal(3000)
_Wr, _ = rls(_x, _d, 3, 0.99)
_Wl, _ = lms_weights(_x, _d, 3, 0.002)
_rls_err = float(np.linalg.norm(_Wr[200] - _h))
_lms_err = float(np.linalg.norm(_Wl[200] - _h))
assert _rls_err < 0.05, \
    f"after 200 samples RLS should be essentially converged; weight error {_rls_err:.4f}"
assert _lms_err > 0.5, \
    f"LMS on input this correlated is still far away at 200 samples; if it is not ({_lms_err:.4f}), check the comparison is using the same data"
'''},
                    {"name": "a short memory tracks a change and a long one does not", "code": r'''
import numpy as np
_h1 = np.array([1.0, -0.5, 0.25])
_h2 = np.array([0.4, 0.8, -0.3])
_rng = np.random.default_rng(4)
_N = 8000
_x = _rng.standard_normal(_N)
_d = np.zeros(_N)
for _n in range(_N):
    _u = window(_x, _n, 3)
    _d[_n] = float((_h1 if _n < _N // 2 else _h2) @ _u)
_d = _d + 0.02 * _rng.standard_normal(_N)
_Wf, _ = rls(_x, _d, 3, 0.9)
_Ws, _ = rls(_x, _d, 3, 0.9999)
_fast = float(np.linalg.norm(_Wf[_N // 2 + 100] - _h2))
_slow = float(np.linalg.norm(_Ws[_N // 2 + 100] - _h2))
assert _fast < 0.1, \
    f"lambda = 0.9 remembers about 10 samples, so 100 samples after the channel changes it should have followed; weight error {_fast:.4f}"
assert _slow > 1.0, \
    f"lambda = 0.9999 remembers 10000 samples and cannot notice a change this recent; expected it to still be wrong, got {_slow:.4f}"
'''},
                    {"name": "the covariance recursion survives a long run", "code": r'''
import numpy as np
_rng = np.random.default_rng(4)
_N = 8000
_x = _rng.standard_normal(_N)
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:_N] + 0.02 * _rng.standard_normal(_N)
_W, _e = rls(_x, _d, 3, 0.9)
assert np.all(np.isfinite(_W)), \
    "the weights went to nan or inf: P has lost its symmetry to rounding — symmetrise it with P = 0.5 * (P + P.T) after every update"
assert np.max(np.abs(_W[-1] - _h)) < 0.05, \
    f"even with a ten-sample memory the estimate should hover around the true taps; got {np.round(_W[-1], 4).tolist()}"
'''},
                    {"name": "delta sets the start, not the destination", "code": r'''
import numpy as np
_rng = np.random.default_rng(21)
_v = _rng.standard_normal(3000)
_x = np.zeros(3000)
for _n in range(1, 3000):
    _x[_n] = 0.95 * _x[_n - 1] + _v[_n]
_h = np.array([1.0, -0.5, 0.25])
_d = np.convolve(_x, _h)[:3000] + 0.01 * _rng.standard_normal(3000)
_Wa, _ = rls(_x, _d, 3, 0.99, 0.001)
_Wb, _ = rls(_x, _d, 3, 0.99, 0.1)
assert np.max(np.abs(_Wa[-1] - _Wb[-1])) < 1e-3, \
    f"delta only sets P(0) and its influence is forgotten; the two runs ended {np.max(np.abs(_Wa[-1] - _Wb[-1])):.2e} apart"
assert float(np.linalg.norm(_Wa[50] - _h)) < float(np.linalg.norm(_Wb[50] - _h)), \
    "a smaller delta means a larger initial P, which means bigger early steps and a faster start"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Cancel an echo through a room that changes",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
A hands-free call. The far-end signal `x` comes out of the loudspeaker, bounces
around the room, and arrives back at the microphone as `d`. Your job is to model
the room with an 8-tap FIR filter and subtract its output, so the far end hears
itself as little as possible.

Two things make it real. The far-end signal is **correlated** — an AR(1) process
with $\rho = 0.8$, which is far closer to speech than white noise and gives a
substantial eigenvalue spread. And halfway through the call the **room changes**:
`signals.session()` switches to a different impulse response at the midpoint,
because somebody moved.

Implement, in `main.py`:

1. `wiener(x, d, M)` — the block solution from module 1.
2. `lms(x, d, M, mu)` and `nlms(x, d, M, mu, eps)` — returning `(w, err)`.
3. `rls(x, d, M, lam, delta)` — returning `(w, err)`.
4. `erle(d, err, tail)` — echo return loss enhancement over the last `tail`
   samples, in decibels: $10\log_{10}\left(\frac{E[d^2]}{E[e^2]}\right)$.

## Suggested order

Get `wiener` working against a stationary session first — it is the only piece with
a closed-form answer to check against, and if it is wrong the rest will be too.
Then LMS, then the one-line change that makes it NLMS, then RLS. `erle` is three
lines and is what turns all of it into a number you can defend.

The checks run in that order, so they light up as you go.
''',
        "deliverables": [
            "`wiener(x, d, M)` solving the normal equations from a block of data, agreeing with the true room response of a stationary session to three decimal places.",
            "`lms` and `nlms`, both returning the a priori error per sample, with NLMS demonstrably insensitive to the level of the far-end signal.",
            "`rls` with a forgetting factor and a symmetrised covariance update, converging within a few hundred samples on the correlated far-end input.",
            "`erle(d, err, tail)` in decibels, and a run of the switching session showing the canceller recovering after the room changes.",
            "A comment at the top of `main.py` naming the step sizes and forgetting factor you chose, with the convergence-versus-misadjustment argument for each.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, no DSP library.",
            "`signals.py` is fixed. The adaptive filters may read `x` and `d` and nothing else; reading `echo_path()` inside an adaptive routine defeats the exercise.",
            "Errors reported must be a priori: computed from the weights the filter held before the update at that sample.",
            "Eight taps throughout. The room is exactly eight taps long, so this is an identification problem with no modelling error to hide behind.",
        ],
        "rubric": [
            {"criterion": "Block solution", "weight": 25,
             "evidence": "The Wiener filter recovers the true eight-tap room response of a stationary session to within 0.01 per tap, using the biased autocorrelation estimate."},
            {"criterion": "Gradient methods", "weight": 30,
             "evidence": "LMS and NLMS both converge on the room response, NLMS weights are unchanged when the far-end level is scaled, and LMS at a fixed step diverges under the same scaling."},
            {"criterion": "Recursive least squares", "weight": 25,
             "evidence": "RLS reaches the room response within a few hundred samples of correlated input, an order of magnitude ahead of LMS on the same data, and stays finite over the whole call."},
            {"criterion": "Trade-off argued with numbers", "weight": 20,
             "evidence": "ERLE after the room change exceeds 20 dB, and the measured tail error rises with the step size as the misadjustment result predicts."},
        ],
        "hints": [
            "`window(x, n, M)` from module 3 is the only helper all four algorithms need; write it once at the top.",
            "For `wiener`, reuse the biased autocorrelation and the `r[abs(i-j)]` Toeplitz trick from module 1.",
            "For `rls`, keep `pi = P @ u` in a variable — it appears in both the gain and the covariance update — and symmetrise `P` after every step.",
            "`erle` should compare the microphone signal with the residual over the *same* tail window; averaging over the whole call hides the transient after the room changes.",
        ],
        "files": [
            {"name": "signals.py", "ro": True, "content": r'''
"""The far-end signal and the room that echoes it. Do not edit."""
import numpy as np

TAPS = 8


def echo_path(variant=0):
    """Two 8-tap room responses; the second is what the room becomes mid-call."""
    if variant == 0:
        return np.array([0.60, -0.35, 0.22, -0.14, 0.09, -0.05, 0.03, -0.02])
    return np.array([0.20, 0.50, -0.30, 0.18, -0.11, 0.07, -0.04, 0.02])


def far_end(N, seed=0, rho=0.8):
    """AR(1) far-end speech surrogate, unit variance, strongly correlated."""
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(N)
    x = np.zeros(N)
    scale = np.sqrt(1.0 - rho * rho)
    for n in range(1, N):
        x[n] = rho * x[n - 1] + scale * v[n]
    return x


def session(N=12000, seed=3, switch=True, noise=0.01, rho=0.8):
    """Return (x, d): the far-end signal and the microphone signal it echoes into."""
    x = far_end(N, seed=seed, rho=rho)
    rng = np.random.default_rng(seed + 1000)
    h0 = echo_path(0)
    h1 = echo_path(1) if switch else h0
    half = N // 2
    d = np.zeros(N)
    for n in range(N):
        h = h0 if n < half else h1
        acc = 0.0
        for k in range(TAPS):
            if n - k >= 0:
                acc += h[k] * x[n - k]
        d[n] = acc
    return x, d + noise * rng.standard_normal(N)
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from signals import session, echo_path, TAPS

# Chosen settings:
#   LMS  mu     -> TODO, and the argument for it
#   NLMS mu     -> TODO
#   RLS  lambda -> TODO


def window(x, n, M):
    """[x(n), x(n-1), ..., x(n-M+1)], zeros where the index runs off the start."""
    x = np.asarray(x, dtype=float)
    u = np.zeros(M)
    lo = max(0, n - M + 1)
    seg = x[lo:n + 1][::-1]
    u[:seg.size] = seg
    return u


def wiener(x, d, M):
    """Block Wiener solution: build R and p from the data, then solve R w = p."""
    # TODO
    return np.zeros(M)


def lms(x, d, M, mu):
    """Return (final weights, a priori error per sample)."""
    # TODO
    return np.zeros(M), np.zeros(np.asarray(x).size)


def nlms(x, d, M, mu, eps=1e-6):
    """Return (final weights, a priori error per sample)."""
    # TODO
    return np.zeros(M), np.zeros(np.asarray(x).size)


def rls(x, d, M, lam=0.99, delta=0.01):
    """Return (final weights, a priori error per sample)."""
    # TODO
    return np.zeros(M), np.zeros(np.asarray(x).size)


def erle(d, err, tail=2000):
    """Echo return loss enhancement over the last `tail` samples, in dB."""
    # TODO
    return 0.0


if __name__ == "__main__":
    x, d = session(12000, seed=3)
    w, err = nlms(x, d, TAPS, 0.5)
    print("NLMS taps:", np.round(w, 4).tolist())
    print("true room:", echo_path(1).tolist())
    print("ERLE:", round(erle(d, err), 2), "dB")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from signals import session, echo_path, TAPS

# Chosen settings:
#   LMS  mu     -> 0.01. The far end has unit power and there are 8 taps, so the
#                  practical bound is 2/(8*1) = 0.25; a quarter of the way there
#                  keeps misadjustment small while still tracking the room change.
#   NLMS mu     -> 0.5. Normalised, so this is a fraction of the way to the a
#                  posteriori zero at mu = 1: fast, and stable at any input level.
#   RLS  lambda -> 0.99, a memory of about 100 samples. Long enough to average the
#                  measurement noise, short enough to follow the room.


def window(x, n, M):
    """[x(n), x(n-1), ..., x(n-M+1)], zeros where the index runs off the start."""
    x = np.asarray(x, dtype=float)
    u = np.zeros(M)
    lo = max(0, n - M + 1)
    seg = x[lo:n + 1][::-1]
    u[:seg.size] = seg
    return u


def wiener(x, d, M):
    """Block Wiener solution: build R and p from the data, then solve R w = p."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    N = x.size
    r = np.array([float(np.dot(x[k:], x[:N - k]) / N) for k in range(M)])
    p = np.array([float(np.dot(d[k:], x[:N - k]) / N) for k in range(M)])
    idx = np.abs(np.subtract.outer(np.arange(M), np.arange(M)))
    return np.linalg.solve(r[idx], p)


def lms(x, d, M, mu):
    """Return (final weights, a priori error per sample)."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    err = np.zeros(x.size)
    for n in range(x.size):
        u = window(x, n, M)
        e = float(d[n] - w @ u)
        err[n] = e
        w = w + mu * e * u
    return w, err


def nlms(x, d, M, mu, eps=1e-6):
    """Return (final weights, a priori error per sample)."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    err = np.zeros(x.size)
    for n in range(x.size):
        u = window(x, n, M)
        e = float(d[n] - w @ u)
        err[n] = e
        w = w + mu * e * u / (eps + float(u @ u))
    return w, err


def rls(x, d, M, lam=0.99, delta=0.01):
    """Return (final weights, a priori error per sample)."""
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    w = np.zeros(M)
    P = np.eye(M) / delta
    err = np.zeros(x.size)
    for n in range(x.size):
        u = window(x, n, M)
        pi = P @ u
        k = pi / (lam + float(u @ pi))
        e = float(d[n] - w @ u)
        err[n] = e
        w = w + k * e
        P = (P - np.outer(k, pi)) / lam
        P = 0.5 * (P + P.T)
    return w, err


def erle(d, err, tail=2000):
    """Echo return loss enhancement over the last `tail` samples, in dB."""
    d = np.asarray(d, dtype=float)[-tail:]
    e = np.asarray(err, dtype=float)[-tail:]
    return float(10.0 * np.log10(float(np.mean(d * d)) / float(np.mean(e * e))))


if __name__ == "__main__":
    x, d = session(12000, seed=3)
    w, err = nlms(x, d, TAPS, 0.5)
    print("NLMS taps:", np.round(w, 4).tolist())
    print("true room:", echo_path(1).tolist())
    print("ERLE:", round(erle(d, err), 2), "dB")
'''},
        ],
        "tests": [
            {"name": "the block solution finds the room", "code": r'''
import numpy as np
from signals import session, echo_path, TAPS
_x, _d = session(6000, seed=3, switch=False)
_w = wiener(_x, _d, TAPS)
assert _w.shape == (TAPS,), f"expected {TAPS} taps, got shape {_w.shape}"
assert np.max(np.abs(_w - echo_path(0))) < 0.01, \
    f"on a stationary session the Wiener filter is the room response; expected {echo_path(0).tolist()}, got {np.round(_w, 4).tolist()}"
'''},
            {"name": "the gradient methods converge and report a priori errors", "code": r'''
import numpy as np
from signals import session, echo_path, TAPS
_x, _d = session(6000, seed=3, switch=False)
_wl, _el = lms(_x, _d, TAPS, 0.01)
_wn, _en = nlms(_x, _d, TAPS, 0.5)
assert _el.shape == (6000,) and _en.shape == (6000,), "one error per sample from both"
assert abs(_el[0] - _d[0]) < 1e-12, \
    f"weights start at zero, so the first a priori error is d[0] = {_d[0]:.6f}; got {_el[0]:.6f}"
assert np.max(np.abs(_wl - echo_path(0))) < 0.05, \
    f"LMS should reach the room response; got {np.round(_wl, 4).tolist()}"
assert np.max(np.abs(_wn - echo_path(0))) < 0.05, \
    f"NLMS should reach the room response; got {np.round(_wn, 4).tolist()}"
'''},
            {"name": "normalisation makes the step independent of level", "code": r'''
import numpy as np
from signals import session, TAPS
_x, _d = session(6000, seed=3, switch=False)
_w1, _ = nlms(_x, _d, TAPS, 0.5)
_w2, _ = nlms(4 * _x, 4 * _d, TAPS, 0.5)
assert np.max(np.abs(_w1 - _w2)) < 1e-6, \
    f"turning the loudspeaker up must not change the NLMS solution; the weights moved by {np.max(np.abs(_w1 - _w2)):.2e}"
_l2, _ = lms(4 * _x, 4 * _d, TAPS, 0.05)
assert (not np.all(np.isfinite(_l2))) or float(np.max(np.abs(_l2))) > 1e3, \
    "a fixed LMS step that was stable at the old level is 16x past the bound at four times the amplitude, and must diverge"
'''},
            {"name": "RLS converges an order of magnitude sooner", "code": r'''
import numpy as np
from signals import session, echo_path, TAPS
_x, _d = session(6000, seed=3, switch=False)
_h = echo_path(0)
_wr, _ = rls(_x[:800], _d[:800], TAPS, 0.99)
_wn, _ = nlms(_x[:800], _d[:800], TAPS, 0.5)
_wl, _ = lms(_x[:800], _d[:800], TAPS, 0.01)
_er = float(np.linalg.norm(_wr - _h))
_en = float(np.linalg.norm(_wn - _h))
_el = float(np.linalg.norm(_wl - _h))
assert _er < 0.05, f"RLS should be converged after 800 samples of correlated input; weight error {_er:.4f}"
assert _en < 0.05, f"NLMS should also be close after 800 samples; weight error {_en:.4f}"
assert _el > 0.1, \
    f"LMS at mu = 0.01 should still be visibly behind at 800 samples ({_el:.4f}) — if it is not, the three are not being run on the same data"
'''},
            {"name": "the canceller recovers after the room changes", "code": r'''
import numpy as np
from signals import session, echo_path, TAPS
_x, _d = session(12000, seed=3)
_w, _e = nlms(_x, _d, TAPS, 0.5)
_erle = erle(_d, _e, 2000)
assert _erle > 20.0, \
    f"over the last 2000 samples the residual should be more than 20 dB below the microphone signal; got {_erle:.2f} dB"
assert np.max(np.abs(_w - echo_path(1))) < 0.05, \
    f"by the end of the call the filter should hold the *second* room response {echo_path(1).tolist()}; got {np.round(_w, 4).tolist()}"
_zero = erle(_d, _d, 2000)
assert abs(_zero) < 1e-9, \
    f"a canceller that subtracts nothing has 0 dB of ERLE by definition; got {_zero:.4f}"
'''},
            {"name": "the step size buys speed and is charged for it", "code": r'''
import numpy as np
from signals import session, TAPS
_x, _d = session(20000, seed=9, switch=False, noise=0.05)
_, _slow = lms(_x, _d, TAPS, 0.002)
_, _fast = lms(_x, _d, TAPS, 0.05)
_tail_slow = float(np.mean(_slow[-8000:] ** 2))
_tail_fast = float(np.mean(_fast[-8000:] ** 2))
assert np.isfinite(_tail_slow) and np.isfinite(_tail_fast), "both step sizes are well inside the bound"
assert _tail_slow < 0.005, \
    f"at mu = 0.002 the tail error should sit near the 0.0025 noise floor; got {_tail_slow:.5f}"
assert _tail_fast > 2.0 * _tail_slow, \
    f"misadjustment is proportional to the step size, so mu = 0.05 must leave a clearly larger tail error; got {_tail_fast:.5f} against {_tail_slow:.5f}"
'''},
        ],
    },
}
