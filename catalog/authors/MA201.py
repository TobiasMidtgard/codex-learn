"""MA201 — Probability & Statistics for Computing. Author module."""

COURSE = {
    "id": "MA201",
    "title": "Probability & Statistics for Computing",
    "year": 2,
    "level": "Intermediate",
    "prereqs": ["MA112"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "σ",
    "summary": (
        "Randomness is the working material of hashing, load balancing, benchmarking "
        "and machine learning, and every claim made about it is a statistical claim. "
        "You build the distributions, estimators and tests from their definitions — no "
        "statistics library — and finish with an A/B-test analyser that states its own "
        "assumptions."
    ),
    "outcomes": [
        "Derive pmf, cdf, expectation and variance for Bernoulli, binomial and geometric variables",
        "Implement exact binomial coefficients without floating-point overflow or a library call",
        "Run reproducible Monte Carlo experiments from a seeded generator",
        "Demonstrate the law of large numbers and the central limit theorem empirically",
        "Compute sample statistics, a Welch two-sample t statistic and a chi-square goodness-of-fit test by hand",
        "Read a critical-value table correctly and state what rejecting the null does and does not mean",
        "Update beliefs with Bayes' rule and build a Laplace-smoothed naive Bayes classifier",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Ross, *A First Course in Probability*, 10th ed. — chapters 4, 5, 7 and 8",
        "Wasserman, *All of Statistics* — chapters 6-10",
        "Mitzenmacher & Upfal, *Probability and Computing*, 2nd ed. — chapters 1-4",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Discrete distributions from first principles",
            "summary": "Three distributions, built from their definitions rather than imported.",
            "concepts": [
                "A pmf assigns non-negative mass summing to one; a cdf is its running total",
                "Bernoulli(p) as the single-trial atom that binomial and geometric are built from",
                "Binomial(n, p) counts successes in n independent trials: C(n,k) p^k (1-p)^(n-k)",
                "Geometric(p) counts trials up to and including the first success — memoryless",
                "Expectation is linear whether or not the variables are independent",
                "Var(X) = E[(X - mu)^2] = E[X^2] - mu^2, and why the centred form loses less precision",
                "Exact integer binomial coefficients: multiply then divide, never factorial then divide",
            ],
            "lab": {
                "title": "pmf, cdf and the first two moments",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
No `math.comb`, no `statistics` module. Build these from the definitions.

**`choose(n, k)`** — the exact integer binomial coefficient. `0` when `k` is
negative or larger than `n`; `ValueError` when `n` is negative. Build it up
multiplicatively — `result = result * (n - i) // (i + 1)` stays exact and never
touches a huge factorial.

**`bernoulli_pmf(p, k)`** — `1 - p` at `k = 0`, `p` at `k = 1`, `0.0` elsewhere.

**`binomial_pmf(n, p, k)`** and **`binomial_cdf(n, p, k)`** — mass and running
total. Both return `0.0` below the support and the cdf returns `1.0` at or above
`n`.

**`geometric_pmf(p, k)`** and **`geometric_cdf(p, k)`** — trials up to and
including the first success, so the support starts at `k = 1`:

```text
geometric_pmf(0.5, 3)  ->  0.125
geometric_cdf(0.5, 3)  ->  0.875
```

Every one of these raises `ValueError` for a probability outside its range —
`[0, 1]` for Bernoulli and binomial, `(0, 1]` for geometric, where `p = 0` would
mean waiting for ever.

**`binomial_table(n, p)`** and **`geometric_table(p, kmax)`** — dicts from
outcome to probability, over `0..n` and `1..kmax` respectively.

**`expectation(pmf)`** and **`variance(pmf)`** — over any such dict. Both raise
`ValueError` if a mass is negative or the masses do not sum to 1 within `1e-9`.
Use the centred form for the variance.

The tables let you check the closed forms you were taught: a binomial table
should give back `n p` and `n p (1 - p)`, and a geometric table `1 / p` and
`(1 - p) / p^2`.
''',
                "files": [{"name": "main.py", "content": r'''
def choose(n, k):
    """Exact integer C(n, k). 0 outside the support, ValueError for n < 0."""
    # your code here


def bernoulli_pmf(p, k):
    """P(X = k) for a single trial with success probability p."""
    # your code here


def binomial_pmf(n, p, k):
    """P(X = k) for k successes in n independent trials."""
    # your code here


def binomial_cdf(n, p, k):
    """P(X <= k)."""
    # your code here


def geometric_pmf(p, k):
    """P(X = k), trials up to and including the first success."""
    # your code here


def geometric_cdf(p, k):
    """P(X <= k)."""
    # your code here


def binomial_table(n, p):
    """{k: P(X = k)} for k in 0..n."""
    # your code here


def geometric_table(p, kmax):
    """{k: P(X = k)} for k in 1..kmax."""
    # your code here


def expectation(pmf):
    """E[X] over a {value: probability} dict."""
    # your code here


def variance(pmf):
    """Var(X), computed about the mean."""
    # your code here


table = binomial_table(10, 0.3)
print("E[X] =", expectation(table), " Var(X) =", variance(table))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def choose(n, k):
    """Exact integer C(n, k). 0 outside the support, ValueError for n < 0."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)                     # C(n, k) == C(n, n - k), fewer terms
    result = 1
    for i in range(k):
        # the running product is always divisible, so // keeps this exact
        result = result * (n - i) // (i + 1)
    return result


def _check_prob(p, strict_low=False):
    if p < 0 or p > 1 or (strict_low and p == 0):
        raise ValueError(f"probability out of range: {p!r}")


def bernoulli_pmf(p, k):
    """P(X = k) for a single trial with success probability p."""
    _check_prob(p)
    if k == 0:
        return 1.0 - p
    if k == 1:
        return float(p)
    return 0.0


def binomial_pmf(n, p, k):
    """P(X = k) for k successes in n independent trials."""
    _check_prob(p)
    if n < 0:
        raise ValueError("n must be non-negative")
    if k < 0 or k > n:
        return 0.0
    return choose(n, k) * p ** k * (1 - p) ** (n - k)


def binomial_cdf(n, p, k):
    """P(X <= k)."""
    _check_prob(p)
    if k < 0:
        return 0.0
    return sum(binomial_pmf(n, p, j) for j in range(0, min(k, n) + 1))


def geometric_pmf(p, k):
    """P(X = k), trials up to and including the first success."""
    _check_prob(p, strict_low=True)
    if k < 1:
        return 0.0
    return (1 - p) ** (k - 1) * p


def geometric_cdf(p, k):
    """P(X <= k)."""
    _check_prob(p, strict_low=True)
    if k < 1:
        return 0.0
    return 1.0 - (1 - p) ** k             # closed form: the complement of k failures


def binomial_table(n, p):
    """{k: P(X = k)} for k in 0..n."""
    return {k: binomial_pmf(n, p, k) for k in range(n + 1)}


def geometric_table(p, kmax):
    """{k: P(X = k)} for k in 1..kmax."""
    return {k: geometric_pmf(p, k) for k in range(1, kmax + 1)}


def _check_pmf(pmf):
    if any(mass < 0 for mass in pmf.values()):
        raise ValueError("a probability mass cannot be negative")
    total = sum(pmf.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"masses sum to {total!r}, not 1")


def expectation(pmf):
    """E[X] over a {value: probability} dict."""
    _check_pmf(pmf)
    return sum(value * mass for value, mass in pmf.items())


def variance(pmf):
    """Var(X), computed about the mean."""
    _check_pmf(pmf)
    mu = sum(value * mass for value, mass in pmf.items())
    return sum(mass * (value - mu) ** 2 for value, mass in pmf.items())


table = binomial_table(10, 0.3)
print("E[X] =", expectation(table), " Var(X) =", variance(table))
'''}],
                "hints": [
                    "`result = result * (n - i) // (i + 1)` is exact at every step because the partial product of i+1 consecutive integers is always divisible by (i+1)!.",
                    "Write one private validator for the probability argument and call it from every public function, so the error message is identical everywhere.",
                    "`geometric_cdf` does not need a loop: k failures then anything has probability (1-p)^k, so the cdf is 1 minus that.",
                    "Compute the mean once inside `variance` and reuse it; recomputing it inside the sum is both slower and easier to get wrong.",
                ],
                "tests": [
                    {"name": "choose is exact and bounded", "code": r'''
for _n, _k, _want in [(5, 2, 10), (0, 0, 1), (10, 5, 252), (52, 5, 2598960), (5, 5, 1)]:
    _got = choose(_n, _k)
    assert _got == _want, f"choose({_n}, {_k}) gave {_got!r}, expected {_want}"
assert isinstance(choose(52, 5), int), "choose returns an exact integer, not a float"
assert choose(5, 6) == 0 and choose(5, -1) == 0, "Outside the support the count is 0"
try:
    choose(-1, 0)
    assert False, "choose(-1, 0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Bernoulli and binomial masses", "code": r'''
assert bernoulli_pmf(0.3, 1) == 0.3 and abs(bernoulli_pmf(0.3, 0) - 0.7) < 1e-12
assert bernoulli_pmf(0.3, 2) == 0.0, "Only 0 and 1 carry mass"
assert abs(binomial_pmf(5, 0.5, 2) - 0.3125) < 1e-12, f"Got {binomial_pmf(5, 0.5, 2)!r}"
assert binomial_pmf(5, 0.5, 6) == 0.0 and binomial_pmf(5, 0.5, -1) == 0.0
assert binomial_pmf(4, 0.0, 0) == 1.0, "With p = 0 all the mass sits at k = 0"
assert binomial_pmf(4, 1.0, 4) == 1.0, "With p = 1 all the mass sits at k = n"
assert abs(sum(binomial_table(9, 0.37).values()) - 1.0) < 1e-12, "A pmf must sum to 1"
for _bad in (-0.1, 1.4):
    try:
        binomial_pmf(5, _bad, 2)
        assert False, f"binomial_pmf with p={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The binomial cdf accumulates", "code": r'''
assert binomial_cdf(5, 0.5, -1) == 0.0, "Below the support the cdf is 0"
assert abs(binomial_cdf(5, 0.5, 5) - 1.0) < 1e-12, "At n the cdf is 1"
assert abs(binomial_cdf(5, 0.5, 99) - 1.0) < 1e-12, "Above n the cdf stays 1"
assert abs(binomial_cdf(5, 0.5, 2) - 0.5) < 1e-12, f"Got {binomial_cdf(5, 0.5, 2)!r}"
_prev = -1.0
for _k in range(-1, 7):
    _now = binomial_cdf(6, 0.4, _k)
    assert _now >= _prev - 1e-15, f"The cdf dipped at k={_k}"
    _prev = _now
'''},
                    {"name": "Geometric mass and its closed-form cdf", "code": r'''
assert abs(geometric_pmf(0.5, 3) - 0.125) < 1e-12, f"Got {geometric_pmf(0.5, 3)!r}"
assert geometric_pmf(0.5, 0) == 0.0, "The support starts at one trial"
assert abs(geometric_cdf(0.5, 3) - 0.875) < 1e-12, f"Got {geometric_cdf(0.5, 3)!r}"
assert geometric_cdf(0.5, 0) == 0.0
for _k in range(1, 12):
    _summed = sum(geometric_pmf(0.31, _j) for _j in range(1, _k + 1))
    assert abs(geometric_cdf(0.31, _k) - _summed) < 1e-12, \
        f"cdf and the summed pmf disagree at k={_k}"
assert geometric_pmf(1.0, 1) == 1.0, "A certain success always lands on the first trial"
try:
    geometric_pmf(0.0, 3)
    assert False, "p = 0 never succeeds, so it should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Binomial moments match n p and n p (1 - p)", "code": r'''
for _n, _p in [(10, 0.3), (7, 0.5), (20, 0.15)]:
    _t = binomial_table(_n, _p)
    assert abs(expectation(_t) - _n * _p) < 1e-9, \
        f"E[X] for Binomial({_n}, {_p}) is {expectation(_t)!r}, expected {_n * _p}"
    assert abs(variance(_t) - _n * _p * (1 - _p)) < 1e-9, \
        f"Var(X) for Binomial({_n}, {_p}) is {variance(_t)!r}, expected {_n * _p * (1 - _p)}"
'''},
                    {"name": "Geometric moments match 1/p and (1-p)/p^2", "code": r'''
for _p, _kmax in [(0.25, 400), (0.5, 80)]:
    _t = geometric_table(_p, _kmax)
    assert abs(expectation(_t) - 1 / _p) < 1e-6, \
        f"E[X] for Geometric({_p}) is {expectation(_t)!r}, expected {1 / _p}"
    assert abs(variance(_t) - (1 - _p) / _p ** 2) < 1e-6, \
        f"Var(X) for Geometric({_p}) is {variance(_t)!r}, expected {(1 - _p) / _p ** 2}"
'''},
                    {"name": "The moment functions refuse a non-distribution", "code": r'''
for _bad in ({0: 0.5, 1: 0.2}, {0: 1.2, 1: -0.2}, {}):
    for _fn in (expectation, variance):
        try:
            _fn(_bad)
            assert False, f"{_fn.__name__}({_bad!r}) should raise ValueError"
        except ValueError:
            pass
assert abs(variance({0: 0.5, 1: 0.5}) - 0.25) < 1e-12, "A fair coin has variance 1/4"
assert variance({4: 1.0}) == 0.0, "A point mass has no spread"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Simulation, the law of large numbers and the CLT",
            "summary": "Seeded Monte Carlo, and the two limit theorems that make it trustworthy.",
            "concepts": [
                "A pseudo-random generator is a deterministic function of its seed — reproducibility is a choice",
                "The weak law of large numbers: the sample mean converges in probability to E[X]",
                "Convergence is in probability, not monotone — a curve that wobbles is not a bug",
                "The central limit theorem: sample means approach a normal shape whatever the parent distribution",
                "The standard error of the mean is sigma / sqrt(n), so precision costs quadratically",
                "The unbiased sample variance divides by n - 1; dividing by n underestimates systematically",
                "Binning a sample into a histogram, and what its shape can and cannot tell you",
            ],
            "lab": {
                "title": "Convergence you can watch",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Every experiment here takes a seed, so two runs of the same call produce
identical numbers. Use `random.Random(seed)` — a private generator — and never
the module-level `random.random`, which shares global state.

**`sample_mean(xs)`** — `ValueError` on an empty sample.

**`sample_variance(xs)`** — the **unbiased** estimator, dividing by `n - 1`.
`ValueError` for fewer than two values, since one observation says nothing about
spread. **`sample_sd(xs)`** is its square root.

**`standardise(xs)`** — the z-scores `(x - mean) / sd`. `ValueError` when the sd
is zero.

**`lln_curve(seed, p, checkpoints)`** — draw Bernoulli(p) values from **one**
stream and record the running mean at each checkpoint, returning
`[(n, mean_after_n), ...]` in ascending order of `n`. `ValueError` for an empty
checkpoint list or a checkpoint below 1.

**`clt_means(seed, trials, n)`** — `trials` sample means, each of `n` draws from
`Uniform(0, 1)`. `ValueError` when either count is below 1.

**`histogram(values, lo, hi, bins)`** — counts per equal-width bin over
`[lo, hi)`. Values outside the range are ignored; a value exactly equal to `lo`
lands in bin 0. `ValueError` when `bins < 1` or `hi <= lo`.

Uniform(0, 1) has mean 1/2 and variance 1/12, so the means of `n` draws should
scatter around 0.5 with standard deviation `sqrt(1/12) / sqrt(n)`. Quadrupling
`n` should halve that scatter — the checks verify exactly this.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def sample_mean(xs):
    """Arithmetic mean. ValueError on an empty sample."""
    # your code here


def sample_variance(xs):
    """Unbiased sample variance, dividing by n - 1."""
    # your code here


def sample_sd(xs):
    """Square root of the unbiased variance."""
    # your code here


def standardise(xs):
    """z-scores. ValueError when the sample has no spread."""
    # your code here


def lln_curve(seed, p, checkpoints):
    """Running mean of Bernoulli(p) draws at each checkpoint."""
    # your code here


def clt_means(seed, trials, n):
    """`trials` sample means, each of n Uniform(0, 1) draws."""
    # your code here


def histogram(values, lo, hi, bins):
    """Counts per equal-width bin over [lo, hi)."""
    # your code here


for n, mean in lln_curve(7, 0.3, [10, 100, 1000, 10000, 50000]):
    print(f"{n:>6}  {mean:.5f}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def sample_mean(xs):
    """Arithmetic mean. ValueError on an empty sample."""
    if not xs:
        raise ValueError("the mean of an empty sample is undefined")
    return sum(xs) / len(xs)


def sample_variance(xs):
    """Unbiased sample variance, dividing by n - 1."""
    if len(xs) < 2:
        raise ValueError("need at least two observations to estimate spread")
    mu = sample_mean(xs)
    return sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)


def sample_sd(xs):
    """Square root of the unbiased variance."""
    return math.sqrt(sample_variance(xs))


def standardise(xs):
    """z-scores. ValueError when the sample has no spread."""
    sd = sample_sd(xs)
    if sd == 0:
        raise ValueError("a constant sample cannot be standardised")
    mu = sample_mean(xs)
    return [(x - mu) / sd for x in xs]


def lln_curve(seed, p, checkpoints):
    """Running mean of Bernoulli(p) draws at each checkpoint."""
    if not checkpoints:
        raise ValueError("need at least one checkpoint")
    marks = sorted(checkpoints)
    if marks[0] < 1:
        raise ValueError("checkpoints must be positive")
    rng = random.Random(seed)
    curve = []
    successes = 0
    wanted = set(marks)
    for i in range(1, marks[-1] + 1):
        successes += 1 if rng.random() < p else 0
        if i in wanted:
            curve.append((i, successes / i))
    return curve


def clt_means(seed, trials, n):
    """`trials` sample means, each of n Uniform(0, 1) draws."""
    if trials < 1 or n < 1:
        raise ValueError("trials and n must both be positive")
    rng = random.Random(seed)
    # one stream for the whole experiment keeps the run reproducible
    return [sum(rng.random() for _ in range(n)) / n for _ in range(trials)]


def histogram(values, lo, hi, bins):
    """Counts per equal-width bin over [lo, hi)."""
    if bins < 1:
        raise ValueError("need at least one bin")
    if hi <= lo:
        raise ValueError("hi must be greater than lo")
    counts = [0] * bins
    width = (hi - lo) / bins
    for value in values:
        if value < lo or value >= hi:
            continue
        index = int((value - lo) / width)
        counts[min(index, bins - 1)] += 1   # guard the top edge against rounding
    return counts


for n, mean in lln_curve(7, 0.3, [10, 100, 1000, 10000, 50000]):
    print(f"{n:>6}  {mean:.5f}")
'''}],
                "hints": [
                    "`sample_variance` should call `sample_mean` rather than recomputing the mean, so the two can never disagree.",
                    "`lln_curve` must draw from a single stream: loop once to the largest checkpoint, keep a running count of successes, and record when the index is a checkpoint.",
                    "`random.Random(seed)` gives an isolated generator; two calls with the same seed produce the same sequence, which is what makes these checks possible.",
                    "In `histogram`, `int((value - lo) / width)` can land on `bins` for a value a hair under `hi` — clamp with `min(index, bins - 1)`.",
                ],
                "tests": [
                    {"name": "The estimators are unbiased and guarded", "code": r'''
_xs = [2, 4, 4, 4, 5, 5, 7, 9]
assert sample_mean(_xs) == 5.0, f"sample_mean gave {sample_mean(_xs)!r}, expected 5.0"
assert abs(sample_variance(_xs) - 32 / 7) < 1e-12, \
    f"sample_variance gave {sample_variance(_xs)!r}, expected 32/7 — divide by n - 1"
assert abs(sample_sd(_xs) - (32 / 7) ** 0.5) < 1e-12
assert sample_variance([3, 5]) == 2.0, f"Got {sample_variance([3, 5])!r}, expected 2.0"
try:
    sample_mean([])
    assert False, "sample_mean([]) should raise ValueError"
except ValueError:
    pass
for _bad in ([], [4]):
    try:
        sample_variance(_bad)
        assert False, f"sample_variance({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "standardise centres and scales", "code": r'''
_z = standardise([2, 4, 4, 4, 5, 5, 7, 9])
assert abs(sample_mean(_z)) < 1e-12, f"z-scores should average 0, got {sample_mean(_z)!r}"
assert abs(sample_sd(_z) - 1.0) < 1e-12, f"z-scores should have sd 1, got {sample_sd(_z)!r}"
try:
    standardise([3, 3, 3])
    assert False, "A constant sample has no spread and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "histogram bins and clamps", "code": r'''
assert histogram([0.0, 0.1, 0.5, 0.9], 0.0, 1.0, 2) == [2, 2], \
    f"Got {histogram([0.0, 0.1, 0.5, 0.9], 0.0, 1.0, 2)!r}"
assert histogram([1.0, -0.5, 3.0], 0.0, 1.0, 4) == [0, 0, 0, 0], \
    "hi is exclusive and values outside the range are dropped"
assert histogram([0.999999999], 0.0, 1.0, 4) == [0, 0, 0, 1], "The top bin must not overflow"
assert sum(histogram([0.2] * 7, 0.0, 1.0, 5)) == 7, "Every in-range value is counted once"
for _bad in ((0.0, 1.0, 0), (1.0, 1.0, 4), (1.0, 0.0, 4)):
    try:
        histogram([0.5], *_bad)
        assert False, f"histogram(..., {_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The law of large numbers, watched", "code": r'''
_curve = lln_curve(7, 0.3, [10, 100, 1000, 10000, 50000])
assert [n for n, _ in _curve] == [10, 100, 1000, 10000, 50000], f"Got {_curve!r}"
assert lln_curve(7, 0.3, [10, 100]) == _curve[:2], \
    "The same seed and prefix must reproduce the same running means"
assert abs(_curve[-1][1] - 0.3) < 0.01, \
    f"After 50000 draws the mean is {_curve[-1][1]!r}, it should be within 0.01 of 0.3"
assert abs(_curve[-1][1] - 0.3) < abs(_curve[0][1] - 0.3), \
    "The estimate at 50000 draws should beat the one at 10 draws"
for _bad in ([], [0], [5, -1]):
    try:
        lln_curve(7, 0.3, _bad)
        assert False, f"lln_curve with checkpoints {_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Sample means centre on the true mean", "code": r'''
_means = clt_means(11, 400, 50)
assert len(_means) == 400, f"Expected 400 sample means, got {len(_means)}"
assert all(0.0 <= m <= 1.0 for m in _means), "A mean of Uniform(0, 1) draws stays in [0, 1]"
assert abs(sample_mean(_means) - 0.5) < 0.01, \
    f"The means average {sample_mean(_means)!r}; Uniform(0, 1) has mean 0.5"
assert clt_means(11, 5, 3) == clt_means(11, 5, 3), "The same seed must give the same experiment"
assert clt_means(11, 5, 3) != clt_means(12, 5, 3), "A different seed must give a different run"
for _bad in ((0, 5), (5, 0), (-1, 5)):
    try:
        clt_means(1, *_bad)
        assert False, f"clt_means(1, {_bad[0]}, {_bad[1]}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The standard error scales as 1/sqrt(n)", "code": r'''
import math as _math
_theory = _math.sqrt(1 / 12) / _math.sqrt(50)
_sd = sample_sd(clt_means(11, 400, 50))
assert abs(_sd - _theory) / _theory < 0.20, \
    f"Spread of the sample means is {_sd!r}, theory says about {_theory!r}"
_sd25 = sample_sd(clt_means(3, 500, 25))
_sd100 = sample_sd(clt_means(3, 500, 100))
assert _sd100 < _sd25, "Four times as many draws must reduce the scatter"
assert 1.6 < _sd25 / _sd100 < 2.5, \
    f"The ratio of the two spreads is {_sd25 / _sd100!r}; sqrt(4) = 2 is the prediction"
'''},
                    {"name": "The sampling distribution is bell-shaped", "code": r'''
_z = standardise(clt_means(5, 600, 40))
_counts = histogram(_z, -3.0, 3.0, 6)
assert sum(_counts) > 570, f"Almost every z-score should fall within 3 sd, got {sum(_counts)}"
assert _counts[2] + _counts[3] > _counts[0] + _counts[5] * 3, \
    f"The centre bins should dominate the tails, counts were {_counts!r}"
assert _counts[2] > _counts[1] and _counts[3] > _counts[4], \
    f"The histogram should fall away from the centre, counts were {_counts!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Estimation and hypothesis testing",
            "summary": "Two-sample comparison and goodness of fit, done by hand against a printed table.",
            "concepts": [
                "Point estimate, standard error and confidence interval as three views of one estimate",
                "The null hypothesis is the claim you try to reject, never the one you try to prove",
                "The two-sample t statistic as a signal-to-noise ratio: mean difference over its standard error",
                "Welch's variant drops the equal-variance assumption at the cost of a fractional degrees of freedom",
                "The Welch-Satterthwaite formula, and reading a table conservatively by rounding df down",
                "Chi-square goodness of fit: summed squared residuals scaled by expected counts, with k - 1 df",
                "A rejected null is not a large effect, and a p-value is not the probability of the hypothesis",
            ],
            "lab": {
                "title": "A t test and a chi-square test, by hand",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
The two critical-value tables are given to you at the top of `main.py`, both at
the 5% level. Write everything else.

**`summarise(xs)`** — `(n, mean, variance)` with the unbiased variance.
`ValueError` for fewer than two observations.

**`welch_t(a, b)`** — returns `(t, df)` where

```text
t  = (mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b)
df = (var_a/n_a + var_b/n_b)^2
     / ( (var_a/n_a)^2/(n_a-1) + (var_b/n_b)^2/(n_b-1) )
```

**`t_critical(df)`** — the two-sided 5% critical value. Real degrees of freedom
are fractional, and the table is not; round **down** to the largest tabulated
entry that does not exceed `df`. That is the conservative reading. `ValueError`
for `df < 1`.

**`t_decision(a, b)`** — `{"t", "df", "critical", "reject"}`, rejecting when
`abs(t)` exceeds the critical value.

**`expected_uniform(total, k)`** — `k` equal expected counts summing to `total`.

**`chi_square(observed, expected)`** — the statistic. `ValueError` when the two
lists differ in length, hold fewer than two categories, contain a negative
observation, or contain an expected count that is not strictly positive.

**`chi_square_decision(observed, expected)`** — `{"statistic", "df", "critical",
"reject"}` with `df = k - 1`; `ValueError` when that df is not in the table.

The die in `main.py` was rolled 120 times. Its statistic is 6.1 against a
critical value of 11.070, so the data give no reason to call it loaded.
''',
                "files": [{"name": "main.py", "content": r'''
import math

# two-sided critical values of Student's t at alpha = 0.05
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 24: 2.064,
    30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 1000: 1.962,
}

# upper-tail critical values of chi-square at alpha = 0.05
CHI2_CRITICAL_95 = {
    1: 3.841, 2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070, 6: 12.592, 7: 14.067,
    8: 15.507, 9: 16.919, 10: 18.307, 11: 19.675, 12: 21.026, 15: 24.996,
    20: 31.410,
}

CONTROL = [12, 15, 14, 10, 13]
TREATMENT = [22, 19, 25, 21, 23]
DIE_ROLLS = [22, 17, 20, 26, 12, 23]


def summarise(xs):
    """(n, mean, unbiased variance). ValueError for fewer than two values."""
    # your code here


def welch_t(a, b):
    """(t, df) for the Welch two-sample t statistic."""
    # your code here


def t_critical(df):
    """Two-sided 5% critical value, rounding df down to the table."""
    # your code here


def t_decision(a, b):
    """{t, df, critical, reject}."""
    # your code here


def expected_uniform(total, k):
    """k equal expected counts summing to total."""
    # your code here


def chi_square(observed, expected):
    """Sum of (O - E)^2 / E."""
    # your code here


def chi_square_decision(observed, expected):
    """{statistic, df, critical, reject}."""
    # your code here


print(t_decision(CONTROL, TREATMENT))
print(chi_square_decision(DIE_ROLLS, expected_uniform(sum(DIE_ROLLS), 6)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

# two-sided critical values of Student's t at alpha = 0.05
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 24: 2.064,
    30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 1000: 1.962,
}

# upper-tail critical values of chi-square at alpha = 0.05
CHI2_CRITICAL_95 = {
    1: 3.841, 2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070, 6: 12.592, 7: 14.067,
    8: 15.507, 9: 16.919, 10: 18.307, 11: 19.675, 12: 21.026, 15: 24.996,
    20: 31.410,
}

CONTROL = [12, 15, 14, 10, 13]
TREATMENT = [22, 19, 25, 21, 23]
DIE_ROLLS = [22, 17, 20, 26, 12, 23]


def summarise(xs):
    """(n, mean, unbiased variance). ValueError for fewer than two values."""
    n = len(xs)
    if n < 2:
        raise ValueError("need at least two observations")
    mean = sum(xs) / n
    variance = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return n, mean, variance


def welch_t(a, b):
    """(t, df) for the Welch two-sample t statistic."""
    na, ma, va = summarise(a)
    nb, mb, vb = summarise(b)
    sa, sb = va / na, vb / nb            # the two squared standard errors
    se = math.sqrt(sa + sb)
    if se == 0:
        raise ValueError("both samples are constant, so the statistic is undefined")
    t = (ma - mb) / se
    df = (sa + sb) ** 2 / (sa ** 2 / (na - 1) + sb ** 2 / (nb - 1))
    return t, df


def t_critical(df):
    """Two-sided 5% critical value, rounding df down to the table."""
    if df < 1:
        raise ValueError("degrees of freedom must be at least 1")
    usable = [k for k in T_CRITICAL_95 if k <= df]
    return T_CRITICAL_95[max(usable)]    # rounding down is the safe direction


def t_decision(a, b):
    """{t, df, critical, reject}."""
    t, df = welch_t(a, b)
    critical = t_critical(df)
    return {"t": t, "df": df, "critical": critical, "reject": abs(t) > critical}


def expected_uniform(total, k):
    """k equal expected counts summing to total."""
    if k < 1:
        raise ValueError("need at least one category")
    return [total / k] * k


def chi_square(observed, expected):
    """Sum of (O - E)^2 / E."""
    if len(observed) != len(expected):
        raise ValueError("observed and expected must have the same length")
    if len(observed) < 2:
        raise ValueError("goodness of fit needs at least two categories")
    if any(o < 0 for o in observed):
        raise ValueError("counts cannot be negative")
    if any(e <= 0 for e in expected):
        raise ValueError("every expected count must be strictly positive")
    return sum((o - e) ** 2 / e for o, e in zip(observed, expected))


def chi_square_decision(observed, expected):
    """{statistic, df, critical, reject}."""
    statistic = chi_square(observed, expected)
    df = len(observed) - 1
    if df not in CHI2_CRITICAL_95:
        raise ValueError(f"no tabulated critical value for df = {df}")
    critical = CHI2_CRITICAL_95[df]
    return {"statistic": statistic, "df": df, "critical": critical,
            "reject": statistic > critical}


print(t_decision(CONTROL, TREATMENT))
print(chi_square_decision(DIE_ROLLS, expected_uniform(sum(DIE_ROLLS), 6)))
'''}],
                "hints": [
                    "Name the two squared standard errors `va/na` and `vb/nb` once; both the statistic and the Welch-Satterthwaite denominator reuse them.",
                    "`max(k for k in T_CRITICAL_95 if k <= df)` is the whole of the conservative table lookup.",
                    "Validate `chi_square` before summing: a zero expected count would divide by zero, and the error message is far more useful than the traceback.",
                    "`df` for goodness of fit is the number of categories minus one — no parameters were estimated from the data here.",
                ],
                "tests": [
                    {"name": "summarise reports n, mean and unbiased variance", "code": r'''
assert summarise(CONTROL) == (5, 12.8, 3.7), f"Got {summarise(CONTROL)!r}, expected (5, 12.8, 3.7)"
_n, _m, _v = summarise(TREATMENT)
assert (_n, _m) == (5, 22.0) and abs(_v - 5.0) < 1e-12, f"Got {(_n, _m, _v)!r}"
for _bad in ([], [3]):
    try:
        summarise(_bad)
        assert False, f"summarise({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The Welch statistic and its degrees of freedom", "code": r'''
_t, _df = welch_t(CONTROL, TREATMENT)
assert abs(_t - (-6.974502000925911)) < 1e-9, f"t is {_t!r}, expected about -6.9745"
assert abs(_df - 7.825277849573533) < 1e-9, f"df is {_df!r}, expected about 7.8253"
_t2, _df2 = welch_t(TREATMENT, CONTROL)
assert abs(_t2 + _t) < 1e-12, "Swapping the samples flips the sign of t"
assert abs(_df2 - _df) < 1e-12, "The degrees of freedom are symmetric in the two samples"
'''},
                    {"name": "The table is read conservatively", "code": r'''
assert t_critical(7.825277849573533) == 2.365, \
    f"df 7.83 must round down to the df 7 row, got {t_critical(7.825277849573533)!r}"
assert t_critical(1) == 12.706 and t_critical(60) == 2.000
assert t_critical(11.9) == 2.228, "There is no df 11 row, so df 10 is used"
assert t_critical(500) == 1.980, "df 500 falls back to the df 120 row"
for _bad in (0, 0.5, -3):
    try:
        t_critical(_bad)
        assert False, f"t_critical({_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The t test separates and refuses to over-claim", "code": r'''
_d = t_decision(CONTROL, TREATMENT)
assert _d["reject"] is True, f"These groups differ by nine points; got {_d!r}"
assert _d["critical"] == 2.365 and abs(_d["t"] + 6.9745) < 1e-3, f"Got {_d!r}"
_similar = t_decision(CONTROL, [13, 14, 12, 15, 11])
assert _similar["reject"] is False, \
    f"Two overlapping samples must not be declared different; got {_similar!r}"
assert abs(_similar["t"]) < _similar["critical"], "reject must agree with the comparison"
'''},
                    {"name": "The chi-square statistic", "code": r'''
assert expected_uniform(120, 6) == [20.0] * 6, f"Got {expected_uniform(120, 6)!r}"
_stat = chi_square(DIE_ROLLS, expected_uniform(120, 6))
assert abs(_stat - 6.1) < 1e-9, f"The statistic is {_stat!r}, expected 6.1"
assert chi_square([20, 20, 20], [20, 20, 20]) == 0.0, "A perfect fit scores zero"
assert abs(chi_square([40, 10, 20, 20, 20, 10], expected_uniform(120, 6)) - 30.0) < 1e-9, \
    "A badly skewed table should score 30.0"
'''},
                    {"name": "chi_square validates its inputs", "code": r'''
for _obs, _exp in [([1, 2], [1]), ([5], [5]), ([1, -2], [2, 2]), ([1, 2], [0, 3]),
                   ([1, 2], [2, -1])]:
    try:
        chi_square(_obs, _exp)
        assert False, f"chi_square({_obs!r}, {_exp!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The goodness-of-fit decision", "code": r'''
_fair = chi_square_decision(DIE_ROLLS, expected_uniform(120, 6))
assert _fair["df"] == 5 and _fair["critical"] == 11.070, f"Got {_fair!r}"
assert _fair["reject"] is False, "6.1 is well under 11.070, so the die survives the test"
_loaded = chi_square_decision([40, 10, 20, 20, 20, 10], expected_uniform(120, 6))
assert _loaded["reject"] is True, f"A statistic of 30 must reject; got {_loaded!r}"
try:
    chi_square_decision([1] * 14, [1] * 14)
    assert False, "df 13 is not in the table, so this should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Bayesian reasoning and naive Bayes",
            "summary": "Turning a prior and a likelihood into a posterior, then scaling that up to a classifier.",
            "concepts": [
                "Bayes' rule as prior times likelihood, renormalised over the hypotheses",
                "The base-rate fallacy: a 99% accurate test on a rare condition still yields mostly false positives",
                "Sequential updating — yesterday's posterior is today's prior, and the order does not matter",
                "The naive conditional-independence assumption, and why it works despite being false",
                "Working in log space so a hundred-word document does not underflow to zero",
                "Laplace (add-alpha) smoothing: an unseen word must not annihilate a whole class",
                "The MAP decision rule, and how the prior shows up as a constant additive term",
            ],
            "lab": {
                "title": "Posterior updates and a spam filter",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
## Part 1 — Bayes' rule

**`bayes_posterior(prior, likelihood)`** — both are dicts keyed by hypothesis.
Returns the renormalised posterior. `ValueError` when the prior does not sum to 1
within `1e-9`, when a hypothesis is missing from `likelihood`, or when the total
evidence probability is zero — that last case means the observation was
impossible under every hypothesis, which is a modelling error, not a number.

**`sequential_update(prior, observations)`** — fold a list of likelihood dicts in
left to right, each posterior becoming the next prior.

The screening example: a condition affecting 1 in 1000, a test that catches 99%
of cases and gives a false positive 5% of the time. One positive result takes
you from 0.001 to about 0.0194 — a nineteenfold jump that still leaves the
answer almost certainly "no".

## Part 2 — naive Bayes

`NaiveBayes(alpha=1.0)` with add-alpha smoothing over the shared vocabulary.

- `tokenise(text)` — a static method: lowercase, then every run of letters and
  digits, so `"Buy CHEAP pills!"` gives `["buy", "cheap", "pills"]`.
- `train(docs)` — `docs` is a list of `(text, label)`. `ValueError` when empty.
- `log_prob(text, label)` — `log P(label) + sum of log P(word | label)`, where

```text
P(word | label) = (count(word, label) + alpha) / (total(label) + alpha * |V|)
```

  and `|V|` is the size of the vocabulary seen in training. `ValueError` before
  training or for an unknown label.
- `classify(text)` — the label with the highest `log_prob`; ties go to the
  alphabetically first label, so an all-unseen document has a defined answer.

Work in logs throughout. A product of two hundred small probabilities underflows
to exactly zero in double precision, and a comparison of zeros decides nothing.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import re

CORPUS = [
    ("buy cheap pills", "spam"),
    ("cheap deal now", "spam"),
    ("meet me for lunch", "ham"),
    ("lunch tomorrow", "ham"),
]


def bayes_posterior(prior, likelihood):
    """Prior times likelihood, renormalised."""
    # your code here


def sequential_update(prior, observations):
    """Fold a list of likelihood dicts into the prior, left to right."""
    # your code here


class NaiveBayes:
    """Multinomial naive Bayes with add-alpha smoothing."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.counts = {}      # label -> {word: count}
        self.totals = {}      # label -> tokens seen
        self.docs = {}        # label -> documents seen
        self.total_docs = 0
        self.vocab = set()

    @staticmethod
    def tokenise(text):
        """Lowercased runs of letters and digits."""
        # your code here

    def train(self, docs):
        """Count words per label. ValueError on an empty corpus."""
        # your code here

    def log_prob(self, text, label):
        """log P(label) + sum of log P(word | label)."""
        # your code here

    def classify(self, text):
        """The most probable label; ties break alphabetically."""
        # your code here


print(bayes_posterior({"ill": 0.001, "well": 0.999},
                      {"ill": 0.99, "well": 0.05}))
model = NaiveBayes()
model.train(CORPUS)
print(model.classify("cheap pills"), model.classify("lunch tomorrow"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import re

CORPUS = [
    ("buy cheap pills", "spam"),
    ("cheap deal now", "spam"),
    ("meet me for lunch", "ham"),
    ("lunch tomorrow", "ham"),
]


def bayes_posterior(prior, likelihood):
    """Prior times likelihood, renormalised."""
    if abs(sum(prior.values()) - 1.0) > 1e-9:
        raise ValueError(f"the prior sums to {sum(prior.values())!r}, not 1")
    if any(mass < 0 for mass in prior.values()):
        raise ValueError("a prior probability cannot be negative")
    missing = set(prior) - set(likelihood)
    if missing:
        raise ValueError(f"no likelihood given for {sorted(missing)}")
    joint = {h: prior[h] * likelihood[h] for h in prior}
    evidence = sum(joint.values())
    if evidence == 0:
        raise ValueError("the observation is impossible under every hypothesis")
    return {h: value / evidence for h, value in joint.items()}


def sequential_update(prior, observations):
    """Fold a list of likelihood dicts into the prior, left to right."""
    posterior = dict(prior)
    for likelihood in observations:
        posterior = bayes_posterior(posterior, likelihood)
    return posterior


class NaiveBayes:
    """Multinomial naive Bayes with add-alpha smoothing."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.counts = {}      # label -> {word: count}
        self.totals = {}      # label -> tokens seen
        self.docs = {}        # label -> documents seen
        self.total_docs = 0
        self.vocab = set()

    @staticmethod
    def tokenise(text):
        """Lowercased runs of letters and digits."""
        return re.findall(r"[a-z0-9]+", text.lower())

    def train(self, docs):
        """Count words per label. ValueError on an empty corpus."""
        if not docs:
            raise ValueError("cannot train on an empty corpus")
        for text, label in docs:
            self.counts.setdefault(label, {})
            self.totals.setdefault(label, 0)
            self.docs[label] = self.docs.get(label, 0) + 1
            self.total_docs += 1
            for word in self.tokenise(text):
                self.counts[label][word] = self.counts[label].get(word, 0) + 1
                self.totals[label] += 1
                self.vocab.add(word)
        return self

    def log_prob(self, text, label):
        """log P(label) + sum of log P(word | label)."""
        if not self.total_docs:
            raise ValueError("the model has not been trained")
        if label not in self.counts:
            raise ValueError(f"unknown label {label!r}")
        denominator = self.totals[label] + self.alpha * len(self.vocab)
        score = math.log(self.docs[label] / self.total_docs)
        for word in self.tokenise(text):
            count = self.counts[label].get(word, 0)
            # every word gets alpha of imaginary evidence, so nothing is impossible
            score += math.log((count + self.alpha) / denominator)
        return score

    def classify(self, text):
        """The most probable label; ties break alphabetically."""
        if not self.total_docs:
            raise ValueError("the model has not been trained")
        best_label = None
        best_score = None
        for label in sorted(self.counts):        # sorted, so ties go alphabetically
            score = self.log_prob(text, label)
            if best_score is None or score > best_score:
                best_label, best_score = label, score
        return best_label


print(bayes_posterior({"ill": 0.001, "well": 0.999},
                      {"ill": 0.99, "well": 0.05}))
model = NaiveBayes()
model.train(CORPUS)
print(model.classify("cheap pills"), model.classify("lunch tomorrow"))
'''}],
                "hints": [
                    "`bayes_posterior` is three lines of arithmetic and four of validation: multiply, sum, divide.",
                    "`sequential_update` should call `bayes_posterior` in a loop rather than reimplementing it — that also inherits the validation.",
                    "Accumulate the vocabulary across *all* labels; the smoothing denominator uses the shared |V|, not the per-label word count.",
                    "Iterate the labels in `sorted()` order inside `classify` and compare with a strict `>`; the first-seen label then wins any tie.",
                ],
                "tests": [
                    {"name": "The base-rate fallacy, in numbers", "code": r'''
_post = bayes_posterior({"ill": 0.001, "well": 0.999}, {"ill": 0.99, "well": 0.05})
assert abs(_post["ill"] - 0.019434628975265017) < 1e-12, \
    f"P(ill | positive) is {_post['ill']!r}, expected about 0.01943"
assert abs(sum(_post.values()) - 1.0) < 1e-12, "A posterior is still a distribution"
assert _post["ill"] > 0.001, "One positive test should still raise the probability nineteenfold"
'''},
                    {"name": "bayes_posterior validates its inputs", "code": r'''
for _prior, _like in [({"a": 0.5, "b": 0.2}, {"a": 1.0, "b": 1.0}),
                      ({"a": 0.5, "b": 0.5}, {"a": 1.0}),
                      ({"a": 0.5, "b": 0.5}, {"a": 0.0, "b": 0.0}),
                      ({"a": 1.5, "b": -0.5}, {"a": 1.0, "b": 1.0})]:
    try:
        bayes_posterior(_prior, _like)
        assert False, f"bayes_posterior({_prior!r}, {_like!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Evidence accumulates across observations", "code": r'''
_prior = {"ill": 0.001, "well": 0.999}
_test = {"ill": 0.99, "well": 0.05}
_one = sequential_update(_prior, [_test])
_two = sequential_update(_prior, [_test, _test])
assert abs(_one["ill"] - bayes_posterior(_prior, _test)["ill"]) < 1e-12, \
    "One observation is just a single Bayes update"
assert _two["ill"] > _one["ill"] > _prior["ill"], "A second positive must raise it further"
assert abs(_two["ill"] - 0.2818323) < 1e-6, f"After two positives: {_two['ill']!r}"
_negative = {"ill": 0.01, "well": 0.95}
assert abs(sequential_update(_prior, [_test, _negative])["ill"]
           - sequential_update(_prior, [_negative, _test])["ill"]) < 1e-12, \
    "Independent evidence gives the same posterior in either order"
assert sequential_update(_prior, []) == _prior, "No evidence leaves the prior alone"
'''},
                    {"name": "tokenise normalises text", "code": r'''
assert NaiveBayes.tokenise("Buy CHEAP pills!") == ["buy", "cheap", "pills"], \
    f'Got {NaiveBayes.tokenise("Buy CHEAP pills!")!r}'
assert NaiveBayes.tokenise("") == [], "No words, no tokens"
assert NaiveBayes.tokenise("...!!!") == [], "Punctuation alone yields nothing"
assert NaiveBayes.tokenise("win 100 now") == ["win", "100", "now"], "Digits are kept"
'''},
                    {"name": "Smoothed conditional probabilities are exact", "code": r'''
import math as _math
_nb = NaiveBayes()
_nb.train(CORPUS)
assert len(_nb.vocab) == 10, f"The shared vocabulary has {len(_nb.vocab)} words, expected 10"
assert _nb.totals["spam"] == 6 and _nb.totals["ham"] == 6, f"totals: {_nb.totals!r}"
_want = _math.log(0.5) + _math.log(3 / 16)
assert abs(_nb.log_prob("cheap", "spam") - _want) < 1e-12, \
    f"log_prob('cheap', 'spam') is {_nb.log_prob('cheap', 'spam')!r}, expected {_want!r}"
_want_ham = _math.log(0.5) + _math.log(1 / 16)
assert abs(_nb.log_prob("cheap", "ham") - _want_ham) < 1e-12, \
    "An unseen word still gets alpha / (total + alpha |V|), never zero"
'''},
                    {"name": "The classifier separates the two classes", "code": r'''
_nb = NaiveBayes()
_nb.train(CORPUS)
assert _nb.classify("cheap pills") == "spam", "Both words appear only in spam"
assert _nb.classify("lunch tomorrow") == "ham", "Both words appear only in ham"
assert _nb.classify("cheap cheap cheap lunch") == "spam", "Repeated evidence should compound"
assert _nb.classify("zzz") == "ham", \
    "An all-unseen document ties, and the tie breaks to the alphabetically first label"
assert _nb.log_prob("zzz qqq", "spam") > float("-inf"), \
    "Smoothing must keep the score finite for unseen words"
'''},
                    {"name": "The model refuses to guess before it is trained", "code": r'''
_fresh = NaiveBayes()
for _call in (lambda: _fresh.classify("anything"), lambda: _fresh.log_prob("x", "spam")):
    try:
        _call()
        assert False, "Using an untrained model should raise ValueError"
    except ValueError:
        pass
try:
    _fresh.train([])
    assert False, "Training on an empty corpus should raise ValueError"
except ValueError:
    pass
_nb = NaiveBayes()
_nb.train(CORPUS)
try:
    _nb.log_prob("cheap", "banana")
    assert False, "An unknown label should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an A/B test analyser",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
An experiment produced two samples of a continuous metric — session length,
latency, basket value. Turn them into a decision that survives being questioned.
`abtest.py` holds the statistics and is what the checks import; `main.py` runs
one analysis and prints the report.

Both critical-value tables are given at the top of the starter.

## Descriptives

`summarise(xs)` — `{"n", "mean", "var", "sd"}` with the unbiased variance;
`ValueError` for fewer than two observations.

## Classical inference

- `welch_t(a, b)` — `(t, df)`, exactly as in the inference lab, with
  `t = (mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b)`.
- `t_critical(df)` — the two-sided 5% value, rounding `df` **down** to the
  largest tabulated entry; `ValueError` for `df < 1`.
- `mean_diff_ci(a, b)` — the interval for `mean_b - mean_a`, that difference plus
  and minus `t_critical(df)` standard errors. Returned low end first.
- `cohens_d(a, b)` — `(mean_b - mean_a)` over the pooled standard deviation
  `sqrt(((n_a-1) var_a + (n_b-1) var_b) / (n_a + n_b - 2))`. `ValueError` when
  that pooled deviation is zero.

## Resampling

- `percentile(values, q)` — the `q` quantile by linear interpolation between
  order statistics: index `q * (n - 1)`, interpolating between its neighbours.
  `ValueError` on an empty sample or `q` outside `[0, 1]`.
- `bootstrap_diffs(a, b, trials=2000, seed=7)` — resample each group **with
  replacement** to its own size, `trials` times, and return the list of
  `mean_b - mean_a`. Use one `random.Random(seed)`, drawing `a` before `b` in
  each trial, so the output is reproducible. `ValueError` for `trials < 1`.
- `bootstrap_ci(a, b, trials=2000, seed=7)` — the 2.5th and 97.5th percentiles of
  those differences.

## The decision

`analyse(a, b, trials=2000, seed=7)` returns a dict with `n_control`,
`n_treatment`, `mean_control`, `mean_treatment`, `diff`, `t`, `df`, `critical`,
`significant`, `effect_size`, `ci`, `bootstrap_ci`, `decision` and
`assumptions`.

`decision` is `"ship"` when the result is significant and the difference is
positive, `"roll back"` when significant and negative, and `"hold"` otherwise.
`assumptions` is a list of at least three plain sentences naming what the
analysis takes on trust — independence, what the test does and does not say, and
what a confidence interval means.

## Suggested order

Descriptives, then the t machinery, then `percentile` (test it against a list you
can check by eye), then the bootstrap, and `analyse` last as pure assembly.
''',
        "deliverables": [
            "`abtest.py` — descriptives, Welch t, effect size, both intervals and `analyse`, importable with no side effects",
            "A conservative critical-value lookup that rounds fractional degrees of freedom down",
            "A percentile function built on linear interpolation between order statistics",
            "A seeded bootstrap whose output is bit-identical across runs",
            "`analyse` returning one dict that carries the estimate, the interval and the decision together",
            "`main.py` — a worked analysis of two samples, printed as a readable report",
        ],
        "constraints": [
            "Standard library only: `math` and `random` are the two imports you need",
            "`abtest.py` defines functions only — importing it must print nothing",
            "Every random draw comes from a `random.Random(seed)` instance, never the module-level functions",
            "No hard-coded critical values outside the two tables given",
            "`analyse` must not print or decide anything it cannot also report as a number",
        ],
        "rubric": [
            {"criterion": "Statistical correctness", "weight": 40,
             "evidence": "Welch t, degrees of freedom, effect size and both intervals reproduce the reference values to nine decimal places."},
            {"criterion": "Reproducibility", "weight": 20,
             "evidence": "The bootstrap gives identical output for a given seed and different output for a different one; nothing touches global random state."},
            {"criterion": "Edge cases and validation", "weight": 20,
             "evidence": "Single-observation samples, constant samples, empty percentile input and non-positive trial counts all raise ValueError."},
            {"criterion": "Reporting", "weight": 12,
             "evidence": "analyse returns every required field, decision agrees with significance and sign, and the assumptions are stated in the output."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public function, no duplicated variance code, and main.py free of statistics logic."},
        ],
        "hints": [
            "`summarise` is the only place that computes a mean or a variance; everything else consumes its dict.",
            "For `percentile`, `position = q * (n - 1)`, `low = int(position)`, and the weight is `position - low`; the top edge needs `min(low + 1, n - 1)`.",
            "Draw the control resample before the treatment resample inside each bootstrap trial, and take both from the same generator — that ordering is what makes the seed reproduce.",
            "`analyse` should call the other functions rather than recompute anything; if a number appears twice in your file, one of the two is wrong.",
        ],
        "files": [
            {"name": "abtest.py", "content": r'''
import math
import random

# two-sided critical values of Student's t at alpha = 0.05
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 24: 2.064,
    30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 1000: 1.962,
}


def summarise(xs):
    """{n, mean, var, sd} with the unbiased variance."""
    # your code here


def welch_t(a, b):
    """(t, df) for the Welch two-sample t statistic."""
    # your code here


def t_critical(df):
    """Two-sided 5% critical value, rounding df down to the table."""
    # your code here


def mean_diff_ci(a, b):
    """Confidence interval for mean(b) - mean(a), low end first."""
    # your code here


def cohens_d(a, b):
    """Standardised mean difference, using the pooled standard deviation."""
    # your code here


def percentile(values, q):
    """The q quantile by linear interpolation between order statistics."""
    # your code here


def bootstrap_diffs(a, b, trials=2000, seed=7):
    """Resampled values of mean(b) - mean(a)."""
    # your code here


def bootstrap_ci(a, b, trials=2000, seed=7):
    """The middle 95% of the bootstrap distribution."""
    # your code here


def analyse(a, b, trials=2000, seed=7):
    """Estimate, intervals, effect size and a decision, in one dict."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from abtest import analyse

CONTROL = [12, 15, 14, 10, 13, 11, 14, 12]
TREATMENT = [22, 19, 25, 21, 23, 20, 24, 22]

report = analyse(CONTROL, TREATMENT)
print(f"control    n={report['n_control']} mean={report['mean_control']:.3f}")
print(f"treatment  n={report['n_treatment']} mean={report['mean_treatment']:.3f}")
print(f"difference {report['diff']:.3f}  effect size {report['effect_size']:.3f}")
print(f"t={report['t']:.3f} df={report['df']:.2f} critical={report['critical']}")
print("decision:", report["decision"])
for line in report["assumptions"]:
    print(" -", line)
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "abtest.py", "content": r'''
import math
import random

# two-sided critical values of Student's t at alpha = 0.05
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 24: 2.064,
    30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 1000: 1.962,
}


def summarise(xs):
    """{n, mean, var, sd} with the unbiased variance."""
    n = len(xs)
    if n < 2:
        raise ValueError("need at least two observations")
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return {"n": n, "mean": mean, "var": var, "sd": math.sqrt(var)}


def _standard_error(a, b):
    """The Welch standard error of the difference, and its two components."""
    sa = summarise(a)
    sb = summarise(b)
    va = sa["var"] / sa["n"]
    vb = sb["var"] / sb["n"]
    return sa, sb, va, vb, math.sqrt(va + vb)


def welch_t(a, b):
    """(t, df) for the Welch two-sample t statistic."""
    sa, sb, va, vb, se = _standard_error(a, b)
    if se == 0:
        raise ValueError("both samples are constant, so the statistic is undefined")
    t = (sa["mean"] - sb["mean"]) / se
    df = (va + vb) ** 2 / (va ** 2 / (sa["n"] - 1) + vb ** 2 / (sb["n"] - 1))
    return t, df


def t_critical(df):
    """Two-sided 5% critical value, rounding df down to the table."""
    if df < 1:
        raise ValueError("degrees of freedom must be at least 1")
    return T_CRITICAL_95[max(k for k in T_CRITICAL_95 if k <= df)]


def mean_diff_ci(a, b):
    """Confidence interval for mean(b) - mean(a), low end first."""
    sa, sb, _va, _vb, se = _standard_error(a, b)
    _t, df = welch_t(a, b)
    margin = t_critical(df) * se
    diff = sb["mean"] - sa["mean"]
    return diff - margin, diff + margin


def cohens_d(a, b):
    """Standardised mean difference, using the pooled standard deviation."""
    sa = summarise(a)
    sb = summarise(b)
    pooled_var = ((sa["n"] - 1) * sa["var"] + (sb["n"] - 1) * sb["var"]) \
        / (sa["n"] + sb["n"] - 2)
    pooled = math.sqrt(pooled_var)
    if pooled == 0:
        raise ValueError("both samples are constant, so the effect size is undefined")
    return (sb["mean"] - sa["mean"]) / pooled


def percentile(values, q):
    """The q quantile by linear interpolation between order statistics."""
    if not values:
        raise ValueError("no values to take a percentile of")
    if q < 0 or q > 1:
        raise ValueError("q must lie in [0, 1]")
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def bootstrap_diffs(a, b, trials=2000, seed=7):
    """Resampled values of mean(b) - mean(a)."""
    if trials < 1:
        raise ValueError("need at least one bootstrap trial")
    if len(a) < 2 or len(b) < 2:
        raise ValueError("need at least two observations in each group")
    rng = random.Random(seed)              # private stream: reproducible
    diffs = []
    for _ in range(trials):
        # control first, then treatment — the draw order is part of the seed contract
        resample_a = [rng.choice(a) for _ in range(len(a))]
        resample_b = [rng.choice(b) for _ in range(len(b))]
        diffs.append(sum(resample_b) / len(b) - sum(resample_a) / len(a))
    return diffs


def bootstrap_ci(a, b, trials=2000, seed=7):
    """The middle 95% of the bootstrap distribution."""
    diffs = bootstrap_diffs(a, b, trials, seed)
    return percentile(diffs, 0.025), percentile(diffs, 0.975)


def analyse(a, b, trials=2000, seed=7):
    """Estimate, intervals, effect size and a decision, in one dict."""
    sa = summarise(a)
    sb = summarise(b)
    t, df = welch_t(a, b)
    critical = t_critical(df)
    significant = abs(t) > critical
    diff = sb["mean"] - sa["mean"]
    if significant:
        decision = "ship" if diff > 0 else "roll back"
    else:
        decision = "hold"
    return {
        "n_control": sa["n"], "n_treatment": sb["n"],
        "mean_control": sa["mean"], "mean_treatment": sb["mean"],
        "diff": diff,
        "t": t, "df": df, "critical": critical, "significant": significant,
        "effect_size": cohens_d(a, b),
        "ci": mean_diff_ci(a, b),
        "bootstrap_ci": bootstrap_ci(a, b, trials, seed),
        "decision": decision,
        "assumptions": [
            "Observations are independent within and between the two groups.",
            "The two groups may have different variances, which is why Welch's t is used "
            "rather than the pooled-variance form.",
            "A significant result means the data would be unusual if the groups were "
            "identical; it is not the probability that the treatment works.",
            "The confidence interval covers the true difference in 95% of repeated "
            "experiments, not with 95% probability for this one.",
            "The bootstrap assumes each sample represents its population well, which is "
            "a strong assumption at these sample sizes.",
        ],
    }
'''},
            {"name": "main.py", "content": r'''
from abtest import analyse

CONTROL = [12, 15, 14, 10, 13, 11, 14, 12]
TREATMENT = [22, 19, 25, 21, 23, 20, 24, 22]

report = analyse(CONTROL, TREATMENT)
print(f"control    n={report['n_control']} mean={report['mean_control']:.3f}")
print(f"treatment  n={report['n_treatment']} mean={report['mean_treatment']:.3f}")
print(f"difference {report['diff']:.3f}  effect size {report['effect_size']:.3f}")
print(f"t={report['t']:.3f} df={report['df']:.2f} critical={report['critical']}")
print(f"95% CI     [{report['ci'][0]:.3f}, {report['ci'][1]:.3f}]")
print(f"bootstrap  [{report['bootstrap_ci'][0]:.3f}, {report['bootstrap_ci'][1]:.3f}]")
print("decision:", report["decision"])
for line in report["assumptions"]:
    print(" -", line)
'''},
        ],
        "tests": [
            {"name": "summarise reports the four descriptives", "code": r'''
from abtest import summarise
_s = summarise([12, 15, 14, 10, 13])
assert _s["n"] == 5 and _s["mean"] == 12.8, f"Got {_s!r}"
assert abs(_s["var"] - 3.7) < 1e-12, f"var is {_s['var']!r}, expected 3.7 — divide by n - 1"
assert abs(_s["sd"] - 3.7 ** 0.5) < 1e-12, "sd is the square root of the variance"
for _bad in ([], [4]):
    try:
        summarise(_bad)
        assert False, f"summarise({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "The Welch statistic matches the reference", "code": r'''
from abtest import welch_t
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
_t, _df = welch_t(_a, _b)
assert abs(_t - (-6.974502000925911)) < 1e-9, f"t is {_t!r}, expected about -6.9745"
assert abs(_df - 7.825277849573533) < 1e-9, f"df is {_df!r}, expected about 7.8253"
try:
    welch_t([5, 5, 5], [5, 5, 5])
    assert False, "Two constant samples give a zero standard error and should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The critical-value lookup rounds down", "code": r'''
from abtest import t_critical
assert t_critical(7.825277849573533) == 2.365, f"Got {t_critical(7.825277849573533)!r}"
assert t_critical(1) == 12.706 and t_critical(11.9) == 2.228 and t_critical(500) == 1.980
for _bad in (0, 0.99, -4):
    try:
        t_critical(_bad)
        assert False, f"t_critical({_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "The confidence interval brackets the difference", "code": r'''
from abtest import mean_diff_ci
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
_lo, _hi = mean_diff_ci(_a, _b)
assert _lo < 9.2 < _hi, f"The interval {(_lo, _hi)!r} should contain the observed difference 9.2"
assert abs(_lo - 6.080350742) < 1e-6, f"Lower bound is {_lo!r}, expected about 6.0804"
assert abs(_hi - 12.319649258) < 1e-6, f"Upper bound is {_hi!r}, expected about 12.3196"
assert _lo > 0, "The whole interval is above zero, which is why the result is significant"
'''},
            {"name": "Cohen's d standardises the difference", "code": r'''
from abtest import cohens_d
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
assert abs(cohens_d(_a, _b) - 4.411062373665534) < 1e-9, f"Got {cohens_d(_a, _b)!r}"
assert cohens_d(_b, _a) == -cohens_d(_a, _b), "Swapping the groups flips the sign"
assert abs(cohens_d(_a, _a)) < 1e-12, "A group against itself has no effect"
try:
    cohens_d([5, 5, 5], [7, 7, 7])
    assert False, "A zero pooled deviation should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "percentile interpolates between order statistics", "code": r'''
from abtest import percentile
assert percentile([1, 2, 3, 4, 5], 0.5) == 3, f"Got {percentile([1, 2, 3, 4, 5], 0.5)!r}"
assert percentile([1, 2, 3, 4], 0.5) == 2.5, "The median of four values sits between the middle two"
assert percentile([5, 1, 3], 0.0) == 1 and percentile([5, 1, 3], 1.0) == 5, \
    "The extremes are the smallest and largest values, whatever the input order"
assert abs(percentile([0, 10], 0.25) - 2.5) < 1e-12, f"Got {percentile([0, 10], 0.25)!r}"
for _bad in (-0.1, 1.1):
    try:
        percentile([1, 2, 3], _bad)
        assert False, f"percentile(values, {_bad}) should raise ValueError"
    except ValueError:
        pass
try:
    percentile([], 0.5)
    assert False, "percentile([], 0.5) should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The bootstrap is reproducible", "code": r'''
from abtest import bootstrap_diffs
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
_one = bootstrap_diffs(_a, _b, trials=200, seed=7)
assert len(_one) == 200, f"Expected 200 resampled differences, got {len(_one)}"
assert _one == bootstrap_diffs(_a, _b, trials=200, seed=7), \
    "The same seed must reproduce the same bootstrap exactly"
assert _one != bootstrap_diffs(_a, _b, trials=200, seed=8), \
    "A different seed must give a different bootstrap"
assert all(min(_b) - max(_a) <= d <= max(_b) - min(_a) for d in _one), \
    "A resampled mean cannot leave the range of its own sample"
for _bad in ((0, 7), (-5, 7)):
    try:
        bootstrap_diffs(_a, _b, trials=_bad[0], seed=_bad[1])
        assert False, f"bootstrap_diffs with trials={_bad[0]} should raise ValueError"
    except ValueError:
        pass
try:
    bootstrap_diffs([1], _b)
    assert False, "A one-observation group should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The bootstrap interval agrees with the t interval", "code": r'''
from abtest import bootstrap_ci, mean_diff_ci
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
_blo, _bhi = bootstrap_ci(_a, _b, trials=1000, seed=7)
assert _blo < 9.2 < _bhi, f"The bootstrap interval {(_blo, _bhi)!r} should contain 9.2"
assert _blo > 0, "The bootstrap should also place the whole interval above zero"
_tlo, _thi = mean_diff_ci(_a, _b)
assert abs(_blo - _tlo) < 4 and abs(_bhi - _thi) < 4, \
    f"The two intervals {(_blo, _bhi)!r} and {(_tlo, _thi)!r} should broadly agree"
'''},
            {"name": "analyse reports a significant difference", "code": r'''
from abtest import analyse
_r = analyse([12, 15, 14, 10, 13], [22, 19, 25, 21, 23], trials=500, seed=7)
for _key in ("n_control", "n_treatment", "mean_control", "mean_treatment", "diff",
             "t", "df", "critical", "significant", "effect_size", "ci",
             "bootstrap_ci", "decision", "assumptions"):
    assert _key in _r, f"analyse is missing the {_key!r} field"
assert _r["significant"] is True and _r["decision"] == "ship", f"Got {_r['decision']!r}"
assert abs(_r["diff"] - 9.2) < 1e-12, f"diff is {_r['diff']!r}, expected 9.2"
assert _r["critical"] == 2.365, f"critical is {_r['critical']!r}"
assert len(_r["assumptions"]) >= 3, "State at least three assumptions in plain sentences"
assert all(isinstance(s, str) and len(s) > 20 for s in _r["assumptions"]), \
    "Each assumption should be a readable sentence, not a keyword"
'''},
            {"name": "analyse holds when the groups overlap", "code": r'''
from abtest import analyse
_r = analyse([12, 15, 14, 10, 13], [13, 14, 12, 15, 11], trials=500, seed=7)
assert _r["significant"] is False, f"Overlapping groups must not be called different: {_r['t']!r}"
assert _r["decision"] == "hold", f"decision is {_r['decision']!r}, expected 'hold'"
assert _r["ci"][0] < 0 < _r["ci"][1], \
    f"An interval that straddles zero is the whole point here: {_r['ci']!r}"
_down = analyse([22, 19, 25, 21, 23], [12, 15, 14, 10, 13], trials=500, seed=7)
assert _down["decision"] == "roll back", \
    f"A significant drop should roll back, got {_down['decision']!r}"
assert _down["effect_size"] < 0, "A drop has a negative effect size"
'''},
            {"name": "abtest.py is import-clean and main.py reports", "code": r'''
_src = open("abtest.py").read()
assert "print(" not in _src, "abtest.py defines functions; the printing belongs in main.py"
assert "random.random(" not in _src and "random.choice(" not in _src, \
    "Use a random.Random(seed) instance, never the module-level generator"
assert "decision:" in _out, f"main.py should print the decision; stdout was {_out!r}"
assert "difference" in _out and "bootstrap" in _out, \
    "main.py should report the difference and the bootstrap interval"
'''},
        ],
    },
}
