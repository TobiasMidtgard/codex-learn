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
