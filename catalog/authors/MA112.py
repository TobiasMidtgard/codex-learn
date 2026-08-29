"""MA112 — Calculus II: Integration & Series."""

COURSE = {
    "id": "MA112",
    "title": "Calculus II — Integration & Series",
    "year": 1,
    "level": "Intermediate",
    "prereqs": ["MA111"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 110,
    "icon": "∑",
    "summary": (
        "Integration and infinite series, built numerically so that every theorem "
        "leaves a measurable trace. You implement the Newton-Cotes rules and watch "
        "their error orders appear in the data, drive an adaptive integrator to a "
        "requested tolerance, tame improper integrals by substitution, and turn "
        "Taylor's theorem and the convergence tests into code that reports how "
        "wrong it might be."
    ),
    "outcomes": [
        "Derive and implement the left, right, midpoint, trapezoid and Simpson rules",
        "Measure an observed error order and match it against the theoretical one",
        "Drive an adaptive quadrature to a caller-supplied tolerance with a depth guard",
        "Convert an improper integral into a proper one by a change of variable",
        "Construct Taylor coefficients and bound the truncation error with the Lagrange remainder",
        "Apply the ratio and integral tests, and estimate a radius of convergence numerically",
        "Report a numerical answer together with a defensible error bound",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone library (60%).",
    "reading": [
        "Stewart, *Calculus: Early Transcendentals*, 9th ed. — chapters 5-8 and 11",
        "Burden, Faires & Burden, *Numerical Analysis*, 10th ed. — chapter 4",
        "Spivak, *Calculus*, 4th ed. — chapters 13-14 and 22-24",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Riemann sums and the Newton-Cotes rules",
            "summary": "From the definition of the integral to the rules that make it computable.",
            "concepts": [
                "The Riemann integral as the common limit of left, right and midpoint sums",
                "The Fundamental Theorem of Calculus links antiderivatives to areas",
                "Trapezoid rule = average of the left and right sums; error term -(b-a)h^2 f''(c)/12",
                "Midpoint rule has the same order but half the constant, and the opposite sign",
                "Simpson's rule integrates the interpolating parabola exactly, and is exact for cubics",
                "Composite error orders: O(h) for left/right, O(h^2) for midpoint/trapezoid, O(h^4) for Simpson",
                "Observed order p = log2(E(n) / E(2n)) — halving h should divide the error by 2^p",
            ],
            "lab": {
                "title": "Quadrature rules and their error orders",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Implement the five classical rules on `n` equal panels of width `h = (b - a) / n`,
then *measure* the error order each one actually achieves.

**`left_sum(f, a, b, n)`**, **`right_sum(f, a, b, n)`**, **`midpoint_sum(f, a, b, n)`**
— the three Riemann sums, sampling each panel at its left edge, right edge and
centre respectively.

**`trapezoid(f, a, b, n)`** — `h * (f(a)/2 + f(x_1) + ... + f(x_{n-1}) + f(b)/2)`.

**`simpson(f, a, b, n)`** — the 1-4-2-4-...-4-1 pattern, scaled by `h / 3`.

All five raise `ValueError` for `n < 1`; `simpson` additionally raises for odd `n`,
because it consumes panels in pairs.

```text
f(x) = x**2 on [0, 1] with n = 4
left_sum      -> 0.21875
right_sum     -> 0.46875
midpoint_sum  -> 0.328125
trapezoid     -> 0.34375
simpson       -> 0.3333333333333333
```

**`observed_order(rule, f, a, b, exact, n)`** — the empirical convergence order

```text
p = log2( |rule(f,a,b,n) - exact| / |rule(f,a,b,2n) - exact| )
```

Return `math.inf` when the finer error is exactly zero (the rule is exact for
that integrand, as Simpson is for any cubic).

Nothing here depends on the sign of `b - a`: with `b < a` the width `h` is
negative and every rule returns the negated integral automatically.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def left_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its left edge."""
    # your code here


def right_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its right edge."""
    # your code here


def midpoint_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its centre."""
    # your code here


def trapezoid(f, a, b, n):
    """Composite trapezoid rule on n panels."""
    # your code here


def simpson(f, a, b, n):
    """Composite Simpson rule; n must be even and at least 2."""
    # your code here


def observed_order(rule, f, a, b, exact, n):
    """log2 of the error ratio between n panels and 2n panels."""
    # your code here


print(trapezoid(lambda x: x * x, 0.0, 1.0, 4))
print(simpson(math.exp, 0.0, 1.0, 100))
print(observed_order(simpson, math.exp, 0.0, 1.0, math.e - 1.0, 32))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def left_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its left edge."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    return h * sum(f(a + i * h) for i in range(n))


def right_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its right edge."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    return h * sum(f(a + i * h) for i in range(1, n + 1))


def midpoint_sum(f, a, b, n):
    """Riemann sum sampling each of n panels at its centre."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    return h * sum(f(a + (i + 0.5) * h) for i in range(n))


def trapezoid(f, a, b, n):
    """Composite trapezoid rule on n panels."""
    if n < 1:
        raise ValueError("n must be at least 1")
    h = (b - a) / n
    total = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        total += f(a + i * h)
    return h * total


def simpson(f, a, b, n):
    """Composite Simpson rule; n must be even and at least 2."""
    if n < 2 or n % 2 != 0:
        raise ValueError("n must be an even integer of at least 2")
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 == 1 else 2) * f(a + i * h)
    return h * total / 3.0


def observed_order(rule, f, a, b, exact, n):
    """log2 of the error ratio between n panels and 2n panels."""
    coarse = abs(rule(f, a, b, n) - exact)
    fine = abs(rule(f, a, b, 2 * n) - exact)
    if fine == 0.0:
        return math.inf
    return math.log2(coarse / fine)


print(trapezoid(lambda x: x * x, 0.0, 1.0, 4))
print(simpson(math.exp, 0.0, 1.0, 100))
print(observed_order(simpson, math.exp, 0.0, 1.0, math.e - 1.0, 32))
'''}],
                "hints": [
                    "Compute `h = (b - a) / n` once, then the sample points are `a + i * h`. The left sum uses `i` from 0 to n-1, the right sum 1 to n, the midpoint `a + (i + 0.5) * h`.",
                    "Trapezoid: start the accumulator at `0.5 * (f(a) + f(b))`, add every interior point at full weight, and multiply by `h` at the end.",
                    "Simpson's weights alternate: interior index `i` gets 4 when `i` is odd and 2 when it is even. `(4 if i % 2 == 1 else 2)` inside the loop is the whole trick.",
                    "`observed_order` must guard against a zero denominator *before* calling `math.log2` — a rule that is exact at 2n panels has infinite observed order.",
                ],
                "tests": [
                    {"name": "The three Riemann sums on x^2", "code": r'''
_f = lambda x: x * x
for _name, _rule, _want in [("left_sum", left_sum, 0.21875),
                            ("right_sum", right_sum, 0.46875),
                            ("midpoint_sum", midpoint_sum, 0.328125)]:
    _got = _rule(_f, 0.0, 1.0, 4)
    assert abs(_got - _want) < 1e-12, f"{_name}(x^2, 0, 1, 4) gave {_got!r}, expected {_want}"
_got = left_sum(_f, 0.0, 1.0, 1)
assert abs(_got - 0.0) < 1e-12, f"left_sum with n=1 gave {_got!r}, expected 0.0"
_got = midpoint_sum(_f, 0.0, 1.0, 1)
assert abs(_got - 0.25) < 1e-12, f"midpoint_sum with n=1 gave {_got!r}, expected 0.25"
'''},
                    {"name": "Trapezoid is the mean of left and right", "code": r'''
_f = lambda x: math.exp(-x) + x ** 3
for _n in (1, 3, 7, 20):
    _mean = 0.5 * (left_sum(_f, 0.0, 2.0, _n) + right_sum(_f, 0.0, 2.0, _n))
    _got = trapezoid(_f, 0.0, 2.0, _n)
    assert abs(_got - _mean) < 1e-12, \
        f"trapezoid(n={_n}) gave {_got!r}, but (left+right)/2 is {_mean!r}"
_got = trapezoid(lambda x: 2.0 * x + 1.0, 0.0, 3.0, 3)
assert abs(_got - 12.0) < 1e-12, f"trapezoid is exact on straight lines; got {_got!r}, expected 12.0"
'''},
                    {"name": "Simpson is exact for cubics", "code": r'''
_got = simpson(lambda x: x ** 3, 0.0, 1.0, 2)
assert abs(_got - 0.25) < 1e-14, f"simpson(x^3, 0, 1, 2) gave {_got!r}, expected 0.25"
_got = simpson(lambda x: 4.0 * x ** 3 - 3.0 * x + 5.0, -1.0, 2.0, 4)
assert abs(_got - 25.5) < 1e-12, f"simpson on a cubic gave {_got!r}, expected 25.5"
_got = simpson(lambda x: x * x, 0.0, 1.0, 4)
assert abs(_got - 1.0 / 3.0) < 1e-14, f"simpson(x^2, 0, 1, 4) gave {_got!r}, expected 1/3"
'''},
                    {"name": "Bad panel counts are refused", "code": r'''
for _name, _rule in [("left_sum", left_sum), ("right_sum", right_sum),
                     ("midpoint_sum", midpoint_sum), ("trapezoid", trapezoid),
                     ("simpson", simpson)]:
    for _bad in (0, -1, -8):
        try:
            _rule(math.sin, 0.0, 1.0, _bad)
            assert False, f"{_name} with n={_bad} should raise ValueError"
        except ValueError:
            pass
for _odd in (1, 3, 15):
    try:
        simpson(math.sin, 0.0, 1.0, _odd)
        assert False, f"simpson with n={_odd} should raise ValueError (odd panel count)"
    except ValueError:
        pass
'''},
                    {"name": "Refinement really does converge", "code": r'''
_exact = math.e - 1.0
_e_trap = abs(trapezoid(math.exp, 0.0, 1.0, 1000) - _exact)
assert _e_trap < 1e-6, f"trapezoid with n=1000 was off by {_e_trap!r}, expected under 1e-6"
_e_mid = abs(midpoint_sum(math.exp, 0.0, 1.0, 1000) - _exact)
assert _e_mid < 1e-6, f"midpoint_sum with n=1000 was off by {_e_mid!r}, expected under 1e-6"
_e_simp = abs(simpson(math.exp, 0.0, 1.0, 100) - _exact)
assert _e_simp < 1e-9, f"simpson with n=100 was off by {_e_simp!r}, expected under 1e-9"
'''},
                    {"name": "Observed orders match the theory", "code": r'''
_exact = math.e - 1.0
for _name, _rule, _want in [("left_sum", left_sum, 1.0), ("right_sum", right_sum, 1.0),
                            ("midpoint_sum", midpoint_sum, 2.0), ("trapezoid", trapezoid, 2.0)]:
    _p = observed_order(_rule, math.exp, 0.0, 1.0, _exact, 64)
    assert abs(_p - _want) < 0.05, f"observed_order for {_name} gave {_p!r}, expected about {_want}"
_p = observed_order(simpson, math.exp, 0.0, 1.0, _exact, 32)
assert abs(_p - 4.0) < 0.05, f"observed_order for simpson gave {_p!r}, expected about 4.0"
'''},
                    {"name": "An exact rule has infinite order", "code": r'''
_p = observed_order(simpson, lambda x: x ** 3, 0.0, 1.0, 0.25, 4)
assert _p == math.inf, f"observed_order gave {_p!r}; a zero fine error should give math.inf"
'''},
                    {"name": "A reversed interval flips the sign", "code": r'''
for _name, _rule in [("trapezoid", trapezoid), ("midpoint_sum", midpoint_sum)]:
    _fwd = _rule(math.sin, 0.0, math.pi, 8)
    _bwd = _rule(math.sin, math.pi, 0.0, 8)
    assert abs(_fwd + _bwd) < 1e-12, \
        f"{_name} over [pi, 0] gave {_bwd!r}, expected the negation of {_fwd!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Adaptive quadrature and improper integrals",
            "summary": "Spending effort where the integrand is difficult, and taming infinite domains.",
            "concepts": [
                "A fixed panel count wastes work on smooth stretches and starves the hard ones",
                "Richardson extrapolation: comparing S(a,b) with S(a,c)+S(c,b) estimates the error",
                "The 1/15 factor comes from Simpson's h^4 order — halving h divides the error by 16",
                "Recursive bisection with a per-half tolerance of tol/2 keeps the global budget",
                "A depth limit is mandatory: a singularity would otherwise recurse forever",
                "Improper integrals of the first kind (infinite limit) yield to x = a + t/(1-t)",
                "Improper integrals of the second kind (endpoint blow-up) often yield to x = a + u^2",
            ],
            "lab": {
                "title": "Adaptive Simpson to a requested tolerance",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
## Adaptive Simpson

**`adaptive_simpson(f, a, b, tol, max_depth=30)`**

One Simpson panel over `[a, b]` is `(b - a) / 6 * (f(a) + 4 f(m) + f(b))` with
`m` the midpoint. Split the interval, compute the two half panels, and compare:

```text
delta = left + right - whole
```

Accept `left + right + delta / 15` when `abs(delta) <= 15 * tol` or the depth
budget is exhausted; otherwise recurse into each half with tolerance `tol / 2`.

`tol <= 0` raises `ValueError`. `a == b` returns `0.0`. `b < a` returns the
negation of the forward integral.

## Improper integrals

Each of the three below rewrites the integral as a proper one over a finite
interval and then calls `adaptive_simpson`. The substituted integrand is only
*removably* singular at the endpoint, so clamp the variable to `CLAMP = 1e-12`
away from it rather than evaluating the limit symbolically.

**`integrate_to_infinity(f, a, tol)`** — with `x = a + t/(1-t)` and
`dx = dt/(1-t)^2`,

```text
∫[a, ∞) f(x) dx  =  ∫[0, 1) f(a + t/(1-t)) / (1-t)^2 dt
```

**`integrate_real_line(f, tol)`** — split at 0 and reflect: the left half is
`integrate_to_infinity(lambda x: f(-x), 0, tol/2)`.

**`integrate_endpoint_singular(f, a, b, tol)`** — for an integrable blow-up at
`a`, substitute `x = a + u^2`, `dx = 2u du`:

```text
∫[a, b] f(x) dx  =  ∫[0, sqrt(b-a)] 2u f(a + u^2) du
```

The factor `2u` is exactly what kills a `1/sqrt(x - a)` singularity. Raise
`ValueError` unless `a < b`.

```text
integrate_to_infinity(lambda x: math.exp(-x), 0.0, 1e-10)      -> 1.0
integrate_real_line(lambda x: math.exp(-x*x), 1e-10)           -> sqrt(pi)
integrate_endpoint_singular(lambda x: 1/math.sqrt(x), 0, 1, 1e-10) -> 2.0
```
''',
                "files": [{"name": "main.py", "content": r'''
import math

CLAMP = 1e-12


def _panel(f, a, b):
    """One Simpson panel over [a, b]."""
    # your code here


def adaptive_simpson(f, a, b, tol, max_depth=30):
    """Recursive Simpson refinement to an absolute tolerance."""
    # your code here


def integrate_to_infinity(f, a, tol):
    """Integral of f from a to +infinity, via x = a + t/(1-t)."""
    # your code here


def integrate_real_line(f, tol):
    """Integral of f over the whole real line."""
    # your code here


def integrate_endpoint_singular(f, a, b, tol):
    """Integral of f over [a, b] with an integrable singularity at a."""
    # your code here


print(adaptive_simpson(math.sin, 0.0, math.pi, 1e-10))
print(integrate_real_line(lambda x: math.exp(-x * x), 1e-10))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

CLAMP = 1e-12


def _panel(f, a, b):
    """One Simpson panel over [a, b]."""
    c = 0.5 * (a + b)
    return (b - a) / 6.0 * (f(a) + 4.0 * f(c) + f(b))


def _refine(f, a, b, tol, whole, depth):
    """Bisect until the Richardson estimate of the panel error is small enough."""
    c = 0.5 * (a + b)
    left = _panel(f, a, c)
    right = _panel(f, c, b)
    delta = left + right - whole
    if depth <= 0 or abs(delta) <= 15.0 * tol:
        return left + right + delta / 15.0
    return (_refine(f, a, c, tol / 2.0, left, depth - 1)
            + _refine(f, c, b, tol / 2.0, right, depth - 1))


def adaptive_simpson(f, a, b, tol, max_depth=30):
    """Recursive Simpson refinement to an absolute tolerance."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    if a == b:
        return 0.0
    if b < a:
        return -adaptive_simpson(f, b, a, tol, max_depth)
    return _refine(f, a, b, tol, _panel(f, a, b), max_depth)


def integrate_to_infinity(f, a, tol):
    """Integral of f from a to +infinity, via x = a + t/(1-t)."""
    def g(t):
        u = 1.0 - t
        if u < CLAMP:
            u = CLAMP
        return f(a + (1.0 - u) / u) / (u * u)
    return adaptive_simpson(g, 0.0, 1.0, tol)


def integrate_real_line(f, tol):
    """Integral of f over the whole real line."""
    return (integrate_to_infinity(f, 0.0, tol / 2.0)
            + integrate_to_infinity(lambda x: f(-x), 0.0, tol / 2.0))


def integrate_endpoint_singular(f, a, b, tol):
    """Integral of f over [a, b] with an integrable singularity at a."""
    if b <= a:
        raise ValueError("need a < b")

    def g(u):
        if u < CLAMP:
            u = CLAMP
        return 2.0 * u * f(a + u * u)
    return adaptive_simpson(g, 0.0, math.sqrt(b - a), tol)


print(adaptive_simpson(math.sin, 0.0, math.pi, 1e-10))
print(integrate_real_line(lambda x: math.exp(-x * x), 1e-10))
'''}],
                "hints": [
                    "Put the recursion in a helper that already knows the value of the whole panel, so no point is ever evaluated twice for the same reason: `_refine(f, a, b, tol, whole, depth)`.",
                    "The accepted value is `left + right + delta / 15`, not `left + right` — that extra term is the Richardson correction and it buys you two extra orders for free.",
                    "For the infinite tail, work with `u = 1 - t` so the clamp is a single `if u < CLAMP: u = CLAMP`, and then `x = a + (1 - u) / u` and the Jacobian is `1 / u**2`.",
                    "`integrate_endpoint_singular` needs no clamp for `1/sqrt(x)` — `2u * f(u**2)` is the constant 2 — but `log` still needs one, so keep it.",
                ],
                "tests": [
                    {"name": "Proper integrals to ten digits", "code": r'''
for _name, _f, _a, _b, _want in [("sin on [0, pi]", math.sin, 0.0, math.pi, 2.0),
                                 ("exp on [0, 1]", math.exp, 0.0, 1.0, math.e - 1.0),
                                 ("x^3 on [0, 1]", lambda x: x ** 3, 0.0, 1.0, 0.25)]:
    _got = adaptive_simpson(_f, _a, _b, 1e-10)
    assert abs(_got - _want) < 1e-9, f"adaptive_simpson({_name}) gave {_got!r}, expected {_want!r}"
_got = adaptive_simpson(lambda x: 1.0 / (1.0 + 25.0 * x * x), -1.0, 1.0, 1e-10)
_want = 2.0 * math.atan(5.0) / 5.0
assert abs(_got - _want) < 1e-9, f"Runge integral gave {_got!r}, expected {_want!r}"
'''},
                    {"name": "Degenerate and reversed intervals", "code": r'''
_got = adaptive_simpson(math.sin, 1.0, 1.0, 1e-10)
assert _got == 0.0, f"adaptive_simpson over an empty interval gave {_got!r}, expected 0.0"
_fwd = adaptive_simpson(math.sin, 0.0, math.pi, 1e-10)
_bwd = adaptive_simpson(math.sin, math.pi, 0.0, 1e-10)
assert abs(_fwd + _bwd) < 1e-12, f"Reversed limits gave {_bwd!r}, expected the negation of {_fwd!r}"
'''},
                    {"name": "A non-positive tolerance is refused", "code": r'''
for _bad in (0.0, -1e-6, -3.0):
    try:
        adaptive_simpson(math.sin, 0.0, 1.0, _bad)
        assert False, f"adaptive_simpson with tol={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The tolerance is actually honoured", "code": r'''
_exact = math.e - 1.0
_loose = abs(adaptive_simpson(math.exp, 0.0, 1.0, 1e-3) - _exact)
_tight = abs(adaptive_simpson(math.exp, 0.0, 1.0, 1e-12) - _exact)
assert _loose < 1e-3, f"tol=1e-3 left an error of {_loose!r}"
assert _tight < 1e-11, f"tol=1e-12 left an error of {_tight!r}"
assert _tight <= _loose, f"Tightening the tolerance made things worse: {_tight!r} vs {_loose!r}"
'''},
                    {"name": "Infinite upper limit", "code": r'''
for _name, _f, _a, _want in [("exp(-x) from 0", lambda x: math.exp(-x), 0.0, 1.0),
                             ("1/(1+x^2) from 0", lambda x: 1.0 / (1.0 + x * x), 0.0, math.pi / 2.0),
                             ("x^2 exp(-x) from 0", lambda x: x * x * math.exp(-x), 0.0, 2.0),
                             ("x^-3 from 1", lambda x: x ** -3.0, 1.0, 0.5)]:
    _got = integrate_to_infinity(_f, _a, 1e-10)
    assert abs(_got - _want) < 1e-8, f"integrate_to_infinity({_name}) gave {_got!r}, expected {_want!r}"
'''},
                    {"name": "The whole real line", "code": r'''
_got = integrate_real_line(lambda x: math.exp(-x * x), 1e-10)
assert abs(_got - math.sqrt(math.pi)) < 1e-8, \
    f"Gaussian integral gave {_got!r}, expected {math.sqrt(math.pi)!r}"
_got = integrate_real_line(lambda x: 1.0 / (1.0 + x * x), 1e-10)
assert abs(_got - math.pi) < 1e-8, f"Cauchy integral gave {_got!r}, expected {math.pi!r}"
'''},
                    {"name": "Endpoint singularities", "code": r'''
_got = integrate_endpoint_singular(lambda x: 1.0 / math.sqrt(x), 0.0, 1.0, 1e-10)
assert abs(_got - 2.0) < 1e-9, f"Integral of x^-1/2 over [0, 1] gave {_got!r}, expected 2.0"
_got = integrate_endpoint_singular(math.log, 0.0, 1.0, 1e-10)
assert abs(_got + 1.0) < 1e-8, f"Integral of log over [0, 1] gave {_got!r}, expected -1.0"
_got = integrate_endpoint_singular(lambda x: x * x, 0.0, 1.0, 1e-10)
assert abs(_got - 1.0 / 3.0) < 1e-9, \
    f"The substitution must also work on smooth integrands; got {_got!r}, expected 1/3"
for _bad in [(1.0, 1.0), (2.0, 1.0)]:
    try:
        integrate_endpoint_singular(math.log, _bad[0], _bad[1], 1e-8)
        assert False, f"integrate_endpoint_singular{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Taylor and Maclaurin series",
            "summary": "Replacing a function by a polynomial, and knowing exactly what that costs.",
            "concepts": [
                "The Taylor coefficient c_k = f^(k)(a) / k!, and the Maclaurin case a = 0",
                "Maclaurin series for exp, sin and cos, and the parity that zeroes half their coefficients",
                "Horner evaluation costs n multiplications and is far better conditioned than powers",
                "Taylor's theorem with Lagrange remainder: R_n(x) = f^(n+1)(c) x^(n+1) / (n+1)!",
                "Bounding the remainder means bounding the derivative on the interval, not at a point",
                "Factorial growth beats any fixed power, so exp/sin/cos converge for every x",
                "Catastrophic cancellation: exp(-20) by Maclaurin series loses every significant digit",
            ],
            "lab": {
                "title": "Series coefficients and the Lagrange remainder",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Work with `kind` drawn from `"exp"`, `"sin"`, `"cos"`. Anything else raises
`ValueError`, as does a negative `n`.

**`taylor_coefficients(kind, n)`** — the Maclaurin coefficients `c_0 .. c_n`
as a list of `n + 1` floats.

```text
taylor_coefficients("exp", 4)  ->  [1.0, 1.0, 0.5, 1/6, 1/24]
taylor_coefficients("sin", 5)  ->  [0.0, 1.0, 0.0, -1/6, 0.0, 1/120]
taylor_coefficients("cos", 5)  ->  [1.0, 0.0, -0.5, 0.0, 1/24, 0.0]
```

**`evaluate(coeffs, x)`** — Horner's scheme: start from the last coefficient
and repeatedly multiply by `x` and add the next one down. An empty list raises
`ValueError`.

**`remainder_bound(kind, x, n)`** — the Lagrange bound on `|f(x) - P_n(x)|`:

```text
M * |x|^(n+1) / (n+1)!
```

where `M` bounds `|f^(n+1)|` between 0 and `x`. Every derivative of sin and cos
is bounded by 1; for exp the largest value on that interval is `exp(|x|)`.

```text
remainder_bound("sin", 0.5, 3)  ->  0.0026041666666666665
remainder_bound("exp", 1.0, 5)  ->  0.0037753914284153404
```

**`terms_for_tolerance(kind, x, tol, max_n=400)`** — the smallest `n` whose
remainder bound is `<= tol`. `tol <= 0` raises `ValueError`, and so does a
tolerance still unreached at `max_n`.

```text
terms_for_tolerance("sin", 1.0, 1e-6)   ->  9
terms_for_tolerance("cos", 0.5, 1e-12)  ->  11
```
''',
                "files": [{"name": "main.py", "content": r'''
import math

KINDS = ("exp", "sin", "cos")


def taylor_coefficients(kind, n):
    """Maclaurin coefficients c_0 .. c_n for exp, sin or cos."""
    # your code here


def evaluate(coeffs, x):
    """Evaluate the polynomial with these coefficients at x, by Horner."""
    # your code here


def remainder_bound(kind, x, n):
    """Lagrange bound on the error of the degree-n Maclaurin polynomial at x."""
    # your code here


def terms_for_tolerance(kind, x, tol, max_n=400):
    """Smallest n whose remainder bound at x is at most tol."""
    # your code here


print(taylor_coefficients("cos", 6))
print(evaluate(taylor_coefficients("exp", 20), 1.0), math.e)
print(terms_for_tolerance("sin", 1.0, 1e-6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

KINDS = ("exp", "sin", "cos")


def taylor_coefficients(kind, n):
    """Maclaurin coefficients c_0 .. c_n for exp, sin or cos."""
    if kind not in KINDS:
        raise ValueError("kind must be one of exp, sin, cos")
    if n < 0:
        raise ValueError("n must not be negative")
    coeffs = []
    for k in range(n + 1):
        if kind == "exp":
            coeffs.append(1.0 / math.factorial(k))
        elif kind == "sin":
            if k % 2 == 0:
                coeffs.append(0.0)
            else:
                coeffs.append((-1.0) ** ((k - 1) // 2) / math.factorial(k))
        else:
            if k % 2 == 1:
                coeffs.append(0.0)
            else:
                coeffs.append((-1.0) ** (k // 2) / math.factorial(k))
    return coeffs


def evaluate(coeffs, x):
    """Evaluate the polynomial with these coefficients at x, by Horner."""
    if not coeffs:
        raise ValueError("need at least one coefficient")
    total = 0.0
    for c in reversed(coeffs):
        total = total * x + c
    return total


def remainder_bound(kind, x, n):
    """Lagrange bound on the error of the degree-n Maclaurin polynomial at x."""
    if kind not in KINDS:
        raise ValueError("kind must be one of exp, sin, cos")
    if n < 0:
        raise ValueError("n must not be negative")
    m = math.exp(abs(x)) if kind == "exp" else 1.0
    return m * abs(x) ** (n + 1) / math.factorial(n + 1)


def terms_for_tolerance(kind, x, tol, max_n=400):
    """Smallest n whose remainder bound at x is at most tol."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    for n in range(max_n + 1):
        if remainder_bound(kind, x, n) <= tol:
            return n
    raise ValueError("tolerance not reachable below max_n")


print(taylor_coefficients("cos", 6))
print(evaluate(taylor_coefficients("exp", 20), 1.0), math.e)
print(terms_for_tolerance("sin", 1.0, 1e-6))
'''}],
                "hints": [
                    "Validate `kind` and `n` first; every one of these functions shares the same two guards.",
                    "For sin, only odd k survives and the sign alternates with `(k - 1) // 2`; for cos only even k survives, alternating with `k // 2`.",
                    "Horner is three lines: `total = 0.0`, then `for c in reversed(coeffs): total = total * x + c`, then return.",
                    "`terms_for_tolerance` is a linear search over n calling `remainder_bound` — do not re-derive the factorial by hand.",
                ],
                "tests": [
                    {"name": "Coefficients for the three kinds", "code": r'''
_got = taylor_coefficients("exp", 4)
_want = [1.0, 1.0, 0.5, 1.0 / 6.0, 1.0 / 24.0]
assert len(_got) == 5, f"taylor_coefficients('exp', 4) gave {len(_got)} entries, expected 5"
for _i, (_g, _w) in enumerate(zip(_got, _want)):
    assert abs(_g - _w) < 1e-15, f"exp coefficient {_i} is {_g!r}, expected {_w!r}"
_got = taylor_coefficients("sin", 5)
_want = [0.0, 1.0, 0.0, -1.0 / 6.0, 0.0, 1.0 / 120.0]
for _i, (_g, _w) in enumerate(zip(_got, _want)):
    assert abs(_g - _w) < 1e-15, f"sin coefficient {_i} is {_g!r}, expected {_w!r}"
_got = taylor_coefficients("cos", 5)
_want = [1.0, 0.0, -0.5, 0.0, 1.0 / 24.0, 0.0]
for _i, (_g, _w) in enumerate(zip(_got, _want)):
    assert abs(_g - _w) < 1e-15, f"cos coefficient {_i} is {_g!r}, expected {_w!r}"
'''},
                    {"name": "Degree zero and bad arguments", "code": r'''
assert taylor_coefficients("exp", 0) == [1.0], f"Got {taylor_coefficients('exp', 0)!r}, expected [1.0]"
assert taylor_coefficients("sin", 0) == [0.0], f"Got {taylor_coefficients('sin', 0)!r}, expected [0.0]"
for _args in [("tan", 3), ("EXP", 3), ("exp", -1), ("sin", -4)]:
    try:
        taylor_coefficients(*_args)
        assert False, f"taylor_coefficients{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Horner evaluation", "code": r'''
_got = evaluate([5.0], 12.0)
assert _got == 5.0, f"A constant polynomial gave {_got!r}, expected 5.0"
_got = evaluate([1.0, -2.0, 3.0], 2.0)
assert abs(_got - 9.0) < 1e-12, f"1 - 2x + 3x^2 at x=2 gave {_got!r}, expected 9.0"
_got = evaluate([1.0, 1.0, 0.5], 0.0)
assert _got == 1.0, f"Any polynomial at x=0 is its constant term; got {_got!r}"
try:
    evaluate([], 1.0)
    assert False, "evaluate([], 1.0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The polynomials really approximate", "code": r'''
for _kind, _fn, _n, _x in [("exp", math.exp, 20, 1.0), ("exp", math.exp, 25, -2.0),
                           ("sin", math.sin, 15, 0.7), ("sin", math.sin, 25, 3.0),
                           ("cos", math.cos, 25, 2.0), ("cos", math.cos, 10, -0.4)]:
    _got = evaluate(taylor_coefficients(_kind, _n), _x)
    _want = _fn(_x)
    assert abs(_got - _want) < 1e-10, \
        f"{_kind} series of degree {_n} at {_x} gave {_got!r}, expected {_want!r}"
'''},
                    {"name": "Known remainder bounds", "code": r'''
_got = remainder_bound("sin", 0.5, 3)
_want = 0.5 ** 4 / 24.0
assert abs(_got - _want) < 1e-18, f"remainder_bound('sin', 0.5, 3) gave {_got!r}, expected {_want!r}"
_got = remainder_bound("exp", 1.0, 5)
_want = math.e / 720.0
assert abs(_got - _want) < 1e-15, f"remainder_bound('exp', 1.0, 5) gave {_got!r}, expected {_want!r}"
assert remainder_bound("cos", 0.0, 0) == 0.0, "At x=0 the remainder bound is exactly 0"
for _args in [("tan", 1.0, 3), ("sin", 1.0, -1)]:
    try:
        remainder_bound(*_args)
        assert False, f"remainder_bound{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The bound is never violated", "code": r'''
for _kind, _fn in [("exp", math.exp), ("sin", math.sin), ("cos", math.cos)]:
    for _x in (-2.0, -0.3, 0.0, 0.75, 3.0):
        for _n in (2, 5, 9, 14):
            _err = abs(evaluate(taylor_coefficients(_kind, _n), _x) - _fn(_x))
            _bound = remainder_bound(_kind, _x, _n)
            assert _err <= _bound + 1e-14, \
                f"{_kind} at x={_x}, n={_n}: error {_err!r} exceeds the bound {_bound!r}"
'''},
                    {"name": "terms_for_tolerance is the smallest such n", "code": r'''
for _kind, _x, _tol, _want in [("sin", 1.0, 1e-6, 9), ("exp", 1.0, 1e-6, 9),
                               ("cos", 0.5, 1e-12, 11), ("exp", 0.0, 1e-12, 0)]:
    _got = terms_for_tolerance(_kind, _x, _tol)
    assert _got == _want, f"terms_for_tolerance({_kind!r}, {_x}, {_tol}) gave {_got!r}, expected {_want}"
    assert remainder_bound(_kind, _x, _got) <= _tol, "The returned n must satisfy the tolerance"
    if _got > 0:
        assert remainder_bound(_kind, _x, _got - 1) > _tol, "n-1 must NOT satisfy it"
for _bad in (0.0, -1e-9):
    try:
        terms_for_tolerance("sin", 1.0, _bad)
        assert False, f"terms_for_tolerance with tol={_bad} should raise ValueError"
    except ValueError:
        pass
try:
    terms_for_tolerance("exp", 5.0, 1e-9, max_n=3)
    assert False, "An unreachable tolerance within max_n should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Sequences, series and convergence tests",
            "summary": "Deciding whether an infinite sum exists, and pinning down its value.",
            "concepts": [
                "A series converges exactly when its sequence of partial sums converges",
                "The n-th term test is necessary, not sufficient — the harmonic series is the counterexample",
                "Ratio test: L < 1 converges absolutely, L > 1 diverges, L = 1 says nothing",
                "Numerically the ratio approaches its limit like L + c/n, so extrapolate with 2r(2n) - r(n)",
                "Integral test: for f positive and decreasing, the tail is squeezed between two integrals",
                "That squeeze is a computable error bar, which is what makes the test practically useful",
                "Radius of convergence R = 1/limsup |c_n|^(1/n), estimated from consecutive non-zero coefficients",
            ],
            "lab": {
                "title": "Convergence tests and the radius of convergence",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Throughout, `term(k)` supplies the k-th term of a series indexed from `k = 1`.

**`partial_sums(term, n)`** — the list `[S_1, S_2, ..., S_n]`. `n < 1` raises
`ValueError`.

```text
partial_sums(lambda k: 0.5 ** k, 3)  ->  [0.5, 0.75, 0.875]
```

**`ratio_test(term, n=200)`** — returns `(verdict, limit)`. Estimate the ratio
`r(m) = abs(term(m+1) / term(m))` at `m = n` and `m = 2n`, then extrapolate:

```text
limit = max(0.0, 2 * r(2n) - r(n))
```

`verdict` is `"converges"` below `1 - 1e-3`, `"diverges"` above `1 + 1e-3`, and
`"inconclusive"` in between. A zero term makes the ratio undefined — raise
`ValueError`. `n < 1` also raises.

```text
ratio_test(lambda k: 0.5 ** k)      ->  ("converges", 0.5)
ratio_test(lambda k: 1.0 / k ** 2)  ->  ("inconclusive", ~1.0)
ratio_test(lambda k: 2.0 ** k)      ->  ("diverges", 2.0)
```

**`estimate_sum(term, tail_integral, tol, max_terms=200000)`** — the integral
test turned into an answer with an error bar. `tail_integral(x)` supplies the
exact value of the improper integral of the underlying positive decreasing `f`
from `x` to infinity. After summing `n` terms,

```text
tail_integral(n+1)  <=  sum of the remaining terms  <=  tail_integral(n)
```

so take the midpoint of that bracket and half its width. Grow `n` until the
half-width is `<= tol`, then return `(estimate, half_width, n)`. `tol <= 0`
raises, and so does exhausting `max_terms`.

```text
estimate_sum(lambda k: 1/k**2, lambda x: 1/x, 1e-6)  ->  (~1.6449340678, ~1e-6, 707)
```

**`radius_of_convergence(coeff, n_max=60)`** — `coeff(k)` gives the k-th power
series coefficient. Define one estimate from the last two non-zero indices
`n < m` at or below a cut-off:

```text
rho = (abs(coeff(m)) / abs(coeff(n))) ** (1 / (m - n)),   R = 1 / rho
```

Compute `R_full` at `n_max` and `R_half` at `n_max // 2`. Return `math.inf`
when `R_full >= 1.9 * R_half` (shrinking faster than any geometric rate),
`0.0` when `R_full <= 0.55 * R_half`, and `R_full` otherwise. Fewer than two
non-zero coefficients at either cut-off raises `ValueError`.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def partial_sums(term, n):
    """[S_1, ..., S_n] for a series indexed from k = 1."""
    # your code here


def ratio_test(term, n=200):
    """(verdict, extrapolated ratio limit) for the ratio test."""
    # your code here


def estimate_sum(term, tail_integral, tol, max_terms=200000):
    """(estimate, half_width, terms_used) from the integral-test bracket."""
    # your code here


def radius_of_convergence(coeff, n_max=60):
    """Estimated radius of convergence of the power series with these coefficients."""
    # your code here


print(partial_sums(lambda k: 1.0 / k, 4))
print(ratio_test(lambda k: 0.5 ** k))
print(estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def partial_sums(term, n):
    """[S_1, ..., S_n] for a series indexed from k = 1."""
    if n < 1:
        raise ValueError("n must be at least 1")
    sums = []
    total = 0.0
    for k in range(1, n + 1):
        total += term(k)
        sums.append(total)
    return sums


def ratio_test(term, n=200):
    """(verdict, extrapolated ratio limit) for the ratio test."""
    if n < 1:
        raise ValueError("n must be at least 1")

    def ratio(m):
        below = term(m)
        if below == 0:
            raise ValueError("the ratio test needs non-zero terms")
        return abs(term(m + 1) / below)

    limit = 2.0 * ratio(2 * n) - ratio(n)
    if limit < 0.0:
        limit = 0.0
    if limit < 1.0 - 1e-3:
        return ("converges", limit)
    if limit > 1.0 + 1e-3:
        return ("diverges", limit)
    return ("inconclusive", limit)


def estimate_sum(term, tail_integral, tol, max_terms=200000):
    """(estimate, half_width, terms_used) from the integral-test bracket."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    total = 0.0
    for n in range(1, max_terms + 1):
        total += term(n)
        upper = tail_integral(n)
        lower = tail_integral(n + 1)
        half = 0.5 * (upper - lower)
        if half <= tol:
            return (total + 0.5 * (upper + lower), half, n)
    raise ValueError("tolerance not reached within max_terms")


def radius_of_convergence(coeff, n_max=60):
    """Estimated radius of convergence of the power series with these coefficients."""
    def estimate(top):
        live = [k for k in range(top + 1) if coeff(k) != 0]
        if len(live) < 2:
            raise ValueError("need at least two non-zero coefficients")
        n, m = live[-2], live[-1]
        rho = (abs(coeff(m)) / abs(coeff(n))) ** (1.0 / (m - n))
        if rho == 0.0:
            return math.inf
        return 1.0 / rho

    full = estimate(n_max)
    half = estimate(n_max // 2)
    if full == math.inf or full >= 1.9 * half:
        return math.inf
    if full <= 0.55 * half:
        return 0.0
    return full


print(partial_sums(lambda k: 1.0 / k, 4))
print(ratio_test(lambda k: 0.5 ** k))
print(estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-6))
'''}],
                "hints": [
                    "`partial_sums` is the running-total pattern: one accumulator, one append per step. Do not re-sum from k=1 for every entry.",
                    "Write the ratio as a small inner function `ratio(m)` so you can call it twice; check `term(m) == 0` inside it and raise there.",
                    "In `estimate_sum` the bracket is `[tail_integral(n+1), tail_integral(n)]`. The midpoint is the estimate and half the width is the guaranteed bound — return both.",
                    "For `radius_of_convergence`, build the list of indices with non-zero coefficients first, then work with its last two entries; the `1 / (m - n)` exponent is what handles series such as sin whose coefficients skip every other index.",
                ],
                "tests": [
                    {"name": "Partial sums accumulate", "code": r'''
_got = partial_sums(lambda k: 0.5 ** k, 3)
assert len(_got) == 3, f"partial_sums(..., 3) gave {len(_got)} entries, expected 3"
for _i, _w in enumerate([0.5, 0.75, 0.875]):
    assert abs(_got[_i] - _w) < 1e-12, f"S_{_i + 1} is {_got[_i]!r}, expected {_w}"
_got = partial_sums(lambda k: 1.0 / k, 4)
_want = [1.0, 1.5, 1.0 + 0.5 + 1.0 / 3.0, 1.0 + 0.5 + 1.0 / 3.0 + 0.25]
for _i in range(4):
    assert abs(_got[_i] - _want[_i]) < 1e-12, f"S_{_i + 1} is {_got[_i]!r}, expected {_want[_i]!r}"
assert partial_sums(lambda k: 7.0, 1) == [7.0], "A single-term run returns one entry"
for _bad in (0, -3):
    try:
        partial_sums(lambda k: 1.0, _bad)
        assert False, f"partial_sums with n={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Ratio test on geometric series", "code": r'''
_v, _L = ratio_test(lambda k: 0.5 ** k)
assert _v == "converges", f"Geometric with ratio 1/2 gave verdict {_v!r}"
assert abs(_L - 0.5) < 1e-6, f"Ratio limit was {_L!r}, expected 0.5"
_v, _L = ratio_test(lambda k: 2.0 ** k)
assert _v == "diverges", f"Geometric with ratio 2 gave verdict {_v!r}"
assert abs(_L - 2.0) < 1e-6, f"Ratio limit was {_L!r}, expected 2.0"
_v, _L = ratio_test(lambda k: (-1.0) ** k / 3.0 ** k)
assert _v == "converges", f"Alternating geometric gave verdict {_v!r}"
assert abs(_L - 1.0 / 3.0) < 1e-6, f"Ratio limit was {_L!r}, expected 1/3"
'''},
                    {"name": "Ratio test is honest about L = 1", "code": r'''
for _name, _term in [("1/k", lambda k: 1.0 / k), ("1/k^2", lambda k: 1.0 / k ** 2),
                     ("1/k^3", lambda k: 1.0 / k ** 3)]:
    _v, _L = ratio_test(_term)
    assert _v == "inconclusive", f"ratio_test on {_name} gave {_v!r}, expected 'inconclusive'"
    assert abs(_L - 1.0) < 1e-3, f"ratio_test on {_name} gave limit {_L!r}, expected about 1.0"
_v, _L = ratio_test(lambda k: 1.0 / math.factorial(k), 40)
assert _v == "converges" and _L < 1e-2, f"1/k! gave {(_v, _L)!r}, expected a ratio near 0"
'''},
                    {"name": "Ratio test refuses degenerate input", "code": r'''
try:
    ratio_test(lambda k: 0.0)
    assert False, "A series of zero terms should raise ValueError"
except ValueError:
    pass
for _bad in (0, -5):
    try:
        ratio_test(lambda k: 0.5 ** k, _bad)
        assert False, f"ratio_test with n={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "estimate_sum hits the Basel problem", "code": r'''
_est, _half, _n = estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-6)
assert _n == 707, f"estimate_sum used {_n} terms, expected 707"
assert _half <= 1e-6, f"Returned half-width {_half!r} exceeds the tolerance"
assert abs(_est - math.pi ** 2 / 6.0) <= _half, \
    f"Estimate {_est!r} is further than {_half!r} from pi^2/6 = {math.pi ** 2 / 6.0!r}"
_est, _half, _n = estimate_sum(lambda k: 1.0 / k ** 3, lambda x: 0.5 / x ** 2, 1e-8)
assert abs(_est - 1.2020569031595943) <= _half, \
    f"Apery estimate {_est!r} is outside its own bound {_half!r}"
'''},
                    {"name": "estimate_sum guards its arguments", "code": r'''
for _bad in (0.0, -1e-9):
    try:
        estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, _bad)
        assert False, f"estimate_sum with tol={_bad} should raise ValueError"
    except ValueError:
        pass
try:
    estimate_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-9, max_terms=10)
    assert False, "Running out of terms before the tolerance should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Radius of convergence, finite cases", "code": r'''
_got = radius_of_convergence(lambda k: 2.0 ** k)
assert abs(_got - 0.5) < 1e-9, f"Coefficients 2^k give R = 0.5; got {_got!r}"
_got = radius_of_convergence(lambda k: 0.0 if k == 0 else 1.0 / k)
assert abs(_got - 1.0) < 0.05, f"Coefficients 1/k give R = 1; got {_got!r}"
_got = radius_of_convergence(lambda k: 0.0 if k == 0 else 1.0 / (3.0 ** k * k * k))
assert abs(_got - 3.0) < 0.2, f"Coefficients 1/(3^k k^2) give R = 3; got {_got!r}"
'''},
                    {"name": "Radius of convergence, degenerate cases", "code": r'''
_got = radius_of_convergence(lambda k: 1.0 / math.factorial(k))
assert _got == math.inf, f"The exp series has an infinite radius; got {_got!r}"
_sin = lambda k: 0.0 if k % 2 == 0 else (-1.0) ** ((k - 1) // 2) / math.factorial(k)
_got = radius_of_convergence(_sin)
assert _got == math.inf, f"The sin series has an infinite radius; got {_got!r}"
_got = radius_of_convergence(lambda k: float(math.factorial(k)))
assert _got == 0.0, f"Coefficients k! give R = 0; got {_got!r}"
try:
    radius_of_convergence(lambda k: 1.0 if k == 0 else 0.0)
    assert False, "A series with one non-zero coefficient should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — quadrature and series library with error guarantees",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Fold the four labs into one library. `quadlib.py` holds every routine and is
what the checks import; `main.py` is a demo that integrates a handful of
awkward integrals, sums a series and prints an error report.

Every numerical routine returns the same record, so callers never have to guess
what a bare float means.

## `Result`

A dataclass with three fields, in this order:

- `value` — the number
- `error` — the routine's own estimate of how wrong it might be
- `evaluations` — how many times the integrand or term was called

## Integration

- `simpson(f, a, b, n)` — composite Simpson on `n` even panels; `ValueError`
  for odd `n` or `n < 2`. Returns a plain float, not a `Result`.
- `adaptive(f, a, b, tol, max_depth=30)` — the recursive Simpson of lab 2,
  returning a `Result`. `error` is the sum of `abs(delta) / 15` over the
  accepted panels; `evaluations` counts every call made to `f`. An empty
  interval gives `Result(0.0, 0.0, 0)`; a reversed one negates `value` only.
- `integrate(f, a, b, tol=1e-9)` — the front door. `a` or `b` may be
  `math.inf` / `-math.inf`, handled by the substitutions from lab 2 (split the
  doubly infinite case at 0 and give each half `tol / 2`). `tol <= 0` and any
  NaN bound raise `ValueError`.

## Series

- `taylor_coefficients(kind, n)`, `taylor_eval(coeffs, x)`,
  `taylor_bound(kind, x, n)` — exactly as in lab 3.
- `series_sum(term, tail_integral, tol, max_terms=200000)` — lab 4's
  `estimate_sum`, returning a `Result` whose `evaluations` is the number of
  terms used.

## Reporting

`error_report(entries)` takes a list of `(name, result, exact_or_None)` and
returns a string of exactly `len(entries) + 2` lines:

1. a header line beginning with `quantity`
2. one line per entry, starting with `name`, containing the value, the claimed
   bound and — when `exact` is given — the actual error
3. a final line starting with `TOTAL EVALUATIONS` and ending with the summed
   evaluation count

## Suggested order

`Result` and `simpson`, then `adaptive` with its counter, then `integrate`'s
dispatch on infinite bounds, then the series half, and `error_report` last.
''',
        "deliverables": [
            "`quadlib.py` — the whole library, importable with no output and no side effects",
            "`main.py` — a demo integrating a proper, an infinite and an oscillatory integral, then summing a series",
            "A `Result` record carrying value, error estimate and evaluation count from every routine",
            "`integrate` dispatching correctly on finite, semi-infinite and doubly infinite domains",
            "`series_sum` returning an integral-test bracket that provably contains the true sum",
            "`error_report` producing a table a marker can read without running anything",
        ],
        "constraints": [
            "Standard library only; `math` and `dataclasses` are all you need",
            "`quadlib.py` must define names only — importing it must print nothing",
            "No global mutable state: two concurrent integrations must not share an evaluation counter",
            "Every public routine validates its arguments and raises `ValueError` rather than returning nonsense",
            "The whole demo must finish in well under a second",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the infinite-domain, reversed-interval and empty-interval cases."},
            {"criterion": "Error control", "weight": 25,
             "evidence": "Reported error estimates actually bound the observed error on the tested integrals, and tightening tol tightens the answer."},
            {"criterion": "Argument validation", "weight": 15,
             "evidence": "Non-positive tolerances, odd Simpson panel counts and NaN bounds all raise ValueError."},
            {"criterion": "Design", "weight": 12,
             "evidence": "integrate dispatches onto shared helpers rather than duplicating the refinement loop, and the counter is per-call."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public routine, no dead code, no debug prints left in quadlib.py."},
        ],
        "hints": [
            "Wrap the integrand in a small closure that increments a list-of-one counter; returning `(wrapped, box)` from a helper keeps the state local to one call.",
            "Have `_refine` return the pair `(value, error)` and add the two halves' errors on the way back up — that is the whole error budget.",
            "`integrate` is a dispatch table, not an algorithm: empty interval, reversed interval, both infinite, upper infinite, lower infinite, otherwise `adaptive`. Reflect the lower-infinite case with `lambda x: f(-x)` and negated bounds.",
            "Merge sub-results with one helper that sums values, sums errors and sums evaluation counts, so every branch of `integrate` returns the same shape.",
        ],
        "files": [
            {"name": "quadlib.py", "content": r'''
import math
from dataclasses import dataclass

CLAMP = 1e-12
KINDS = ("exp", "sin", "cos")


@dataclass
class Result:
    value: float
    error: float
    evaluations: int


def simpson(f, a, b, n):
    """Composite Simpson rule on n even panels. Returns a float."""
    # your code here


def adaptive(f, a, b, tol, max_depth=30):
    """Adaptive Simpson to an absolute tolerance. Returns a Result."""
    # your code here


def integrate(f, a, b, tol=1e-9):
    """Integral of f over [a, b], where either bound may be infinite."""
    # your code here


def taylor_coefficients(kind, n):
    """Maclaurin coefficients c_0 .. c_n for exp, sin or cos."""
    # your code here


def taylor_eval(coeffs, x):
    """Horner evaluation of a coefficient list at x."""
    # your code here


def taylor_bound(kind, x, n):
    """Lagrange remainder bound for the degree-n Maclaurin polynomial."""
    # your code here


def series_sum(term, tail_integral, tol, max_terms=200000):
    """Sum a positive decreasing series to a tolerance. Returns a Result."""
    # your code here


def error_report(entries):
    """Table of (name, result, exact_or_None) rows plus a totals line."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
import math
from quadlib import integrate, series_sum, error_report

rows = [
    ("exp on [0,1]", integrate(math.exp, 0.0, 1.0, 1e-10), math.e - 1.0),
    ("exp(-x) to inf", integrate(lambda x: math.exp(-x), 0.0, math.inf, 1e-10), 1.0),
    ("gaussian", integrate(lambda x: math.exp(-x * x), -math.inf, math.inf, 1e-10), math.sqrt(math.pi)),
    ("basel series", series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-8), math.pi ** 2 / 6.0),
]

print(error_report(rows))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "quadlib.py", "content": r'''
import math
from dataclasses import dataclass

CLAMP = 1e-12
KINDS = ("exp", "sin", "cos")


@dataclass
class Result:
    value: float
    error: float
    evaluations: int


def _counted(f):
    """Wrap f so every call is tallied in a private one-element box."""
    box = [0]

    def wrapped(x):
        box[0] += 1
        return f(x)

    return wrapped, box


def _merge(parts):
    """Add up a list of Results field by field."""
    return Result(sum(p.value for p in parts),
                  sum(p.error for p in parts),
                  sum(p.evaluations for p in parts))


def simpson(f, a, b, n):
    """Composite Simpson rule on n even panels. Returns a float."""
    if n < 2 or n % 2 != 0:
        raise ValueError("n must be an even integer of at least 2")
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 == 1 else 2) * f(a + i * h)
    return h * total / 3.0


def _panel(f, a, b):
    """One Simpson panel over [a, b]."""
    c = 0.5 * (a + b)
    return (b - a) / 6.0 * (f(a) + 4.0 * f(c) + f(b))


def _refine(f, a, b, tol, whole, depth):
    """Return (value, error estimate) for the refined panel."""
    c = 0.5 * (a + b)
    left = _panel(f, a, c)
    right = _panel(f, c, b)
    delta = left + right - whole
    if depth <= 0 or abs(delta) <= 15.0 * tol:
        return (left + right + delta / 15.0, abs(delta) / 15.0)
    lv, le = _refine(f, a, c, tol / 2.0, left, depth - 1)
    rv, re = _refine(f, c, b, tol / 2.0, right, depth - 1)
    return (lv + rv, le + re)


def adaptive(f, a, b, tol, max_depth=30):
    """Adaptive Simpson to an absolute tolerance. Returns a Result."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    if a == b:
        return Result(0.0, 0.0, 0)
    sign = 1.0
    if b < a:
        a, b, sign = b, a, -1.0
    counted, box = _counted(f)
    value, error = _refine(counted, a, b, tol, _panel(counted, a, b), max_depth)
    return Result(sign * value, error, box[0])


def _tail(f, a, tol):
    """Integral of f from a to +infinity, via x = a + t/(1-t)."""
    def g(t):
        u = 1.0 - t
        if u < CLAMP:
            u = CLAMP
        return f(a + (1.0 - u) / u) / (u * u)
    return adaptive(g, 0.0, 1.0, tol)


def integrate(f, a, b, tol=1e-9):
    """Integral of f over [a, b], where either bound may be infinite."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    if math.isnan(a) or math.isnan(b):
        raise ValueError("bounds must not be nan")
    if a == b:
        return Result(0.0, 0.0, 0)
    if b < a:
        flipped = integrate(f, b, a, tol)
        return Result(-flipped.value, flipped.error, flipped.evaluations)
    if a == -math.inf and b == math.inf:
        return _merge([_tail(f, 0.0, tol / 2.0),
                       _tail(lambda x: f(-x), 0.0, tol / 2.0)])
    if b == math.inf:
        return _tail(f, a, tol)
    if a == -math.inf:
        return _tail(lambda x: f(-x), -b, tol)
    return adaptive(f, a, b, tol)


def taylor_coefficients(kind, n):
    """Maclaurin coefficients c_0 .. c_n for exp, sin or cos."""
    if kind not in KINDS:
        raise ValueError("kind must be one of exp, sin, cos")
    if n < 0:
        raise ValueError("n must not be negative")
    coeffs = []
    for k in range(n + 1):
        if kind == "exp":
            coeffs.append(1.0 / math.factorial(k))
        elif kind == "sin":
            if k % 2 == 0:
                coeffs.append(0.0)
            else:
                coeffs.append((-1.0) ** ((k - 1) // 2) / math.factorial(k))
        else:
            if k % 2 == 1:
                coeffs.append(0.0)
            else:
                coeffs.append((-1.0) ** (k // 2) / math.factorial(k))
    return coeffs


def taylor_eval(coeffs, x):
    """Horner evaluation of a coefficient list at x."""
    if not coeffs:
        raise ValueError("need at least one coefficient")
    total = 0.0
    for c in reversed(coeffs):
        total = total * x + c
    return total


def taylor_bound(kind, x, n):
    """Lagrange remainder bound for the degree-n Maclaurin polynomial."""
    if kind not in KINDS:
        raise ValueError("kind must be one of exp, sin, cos")
    if n < 0:
        raise ValueError("n must not be negative")
    m = math.exp(abs(x)) if kind == "exp" else 1.0
    return m * abs(x) ** (n + 1) / math.factorial(n + 1)


def series_sum(term, tail_integral, tol, max_terms=200000):
    """Sum a positive decreasing series to a tolerance. Returns a Result."""
    if tol <= 0:
        raise ValueError("tol must be positive")
    total = 0.0
    for n in range(1, max_terms + 1):
        total += term(n)
        upper = tail_integral(n)
        lower = tail_integral(n + 1)
        half = 0.5 * (upper - lower)
        if half <= tol:
            return Result(total + 0.5 * (upper + lower), half, n)
    raise ValueError("tolerance not reached within max_terms")


def error_report(entries):
    """Table of (name, result, exact_or_None) rows plus a totals line."""
    lines = [f"{'quantity':<22}{'value':>18}{'bound':>12}{'actual':>12}"]
    for name, result, exact in entries:
        actual = "-" if exact is None else f"{abs(result.value - exact):.2e}"
        lines.append(f"{name:<22}{result.value:>18.12f}"
                     f"{result.error:>12.2e}{actual:>12}")
    total = sum(entry[1].evaluations for entry in entries)
    lines.append(f"{'TOTAL EVALUATIONS':<22}{total:>18d}")
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
import math
from quadlib import integrate, series_sum, error_report

rows = [
    ("exp on [0,1]", integrate(math.exp, 0.0, 1.0, 1e-10), math.e - 1.0),
    ("exp(-x) to inf", integrate(lambda x: math.exp(-x), 0.0, math.inf, 1e-10), 1.0),
    ("gaussian", integrate(lambda x: math.exp(-x * x), -math.inf, math.inf, 1e-10), math.sqrt(math.pi)),
    ("basel series", series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-8), math.pi ** 2 / 6.0),
]

print(error_report(rows))

runge = integrate(lambda x: 1.0 / (1.0 + 25.0 * x * x), -1.0, 1.0, 1e-10)
print("Runge integral:", runge.value, "in", runge.evaluations, "evaluations")
'''},
        ],
        "tests": [
            {"name": "Result carries value, error and evaluations", "code": r'''
import math as _m
from quadlib import Result, adaptive
_r = Result(1.5, 1e-9, 42)
assert (_r.value, _r.error, _r.evaluations) == (1.5, 1e-9, 42), f"Result fields came back as {_r!r}"
_got = adaptive(_m.sin, 0.0, _m.pi, 1e-10)
assert isinstance(_got, Result), f"adaptive returned {type(_got).__name__}, expected Result"
assert abs(_got.value - 2.0) < 1e-9, f"adaptive(sin, 0, pi) gave {_got.value!r}, expected 2.0"
assert _got.evaluations > 0, "adaptive must count its integrand calls"
'''},
            {"name": "Composite Simpson", "code": r'''
import math as _m
from quadlib import simpson
_got = simpson(lambda x: x ** 3, 0.0, 1.0, 2)
assert abs(_got - 0.25) < 1e-14, f"simpson(x^3, 0, 1, 2) gave {_got!r}, expected 0.25"
_got = simpson(_m.exp, 0.0, 1.0, 100)
assert abs(_got - (_m.e - 1.0)) < 1e-9, f"simpson(exp, 0, 1, 100) gave {_got!r}"
for _bad in (1, 3, 0, -2):
    try:
        simpson(_m.sin, 0.0, 1.0, _bad)
        assert False, f"simpson with n={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "adaptive hits proper integrals", "code": r'''
import math as _m
from quadlib import adaptive
for _name, _f, _a, _b, _want in [("sin", _m.sin, 0.0, _m.pi, 2.0),
                                 ("exp", _m.exp, 0.0, 1.0, _m.e - 1.0),
                                 ("runge", lambda x: 1.0 / (1.0 + 25.0 * x * x), -1.0, 1.0,
                                  2.0 * _m.atan(5.0) / 5.0)]:
    _r = adaptive(_f, _a, _b, 1e-10)
    assert abs(_r.value - _want) < 1e-9, f"adaptive on {_name} gave {_r.value!r}, expected {_want!r}"
    assert abs(_r.value - _want) <= _r.error + 1e-12, \
        f"On {_name} the actual error beat the claimed bound {_r.error!r}"
'''},
            {"name": "Empty, reversed and invalid intervals", "code": r'''
import math as _m
from quadlib import adaptive, integrate
_r = adaptive(_m.sin, 2.0, 2.0, 1e-9)
assert (_r.value, _r.error, _r.evaluations) == (0.0, 0.0, 0), f"Empty interval gave {_r!r}"
_f = adaptive(_m.sin, 0.0, _m.pi, 1e-10)
_b = adaptive(_m.sin, _m.pi, 0.0, 1e-10)
assert abs(_f.value + _b.value) < 1e-12, f"Reversed interval gave {_b.value!r}, expected -{_f.value!r}"
assert _b.error >= 0.0, "The error estimate must stay non-negative when the limits are swapped"
for _bad in (0.0, -1.0):
    try:
        integrate(_m.sin, 0.0, 1.0, _bad)
        assert False, f"integrate with tol={_bad} should raise ValueError"
    except ValueError:
        pass
try:
    integrate(_m.sin, float("nan"), 1.0)
    assert False, "A NaN bound should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Evaluation counters do not leak between calls", "code": r'''
import math as _m
from quadlib import adaptive
_one = adaptive(_m.sin, 0.0, _m.pi, 1e-10)
_two = adaptive(_m.sin, 0.0, _m.pi, 1e-10)
assert _one.evaluations == _two.evaluations, \
    f"Two identical calls counted {_one.evaluations} and {_two.evaluations} evaluations — the counter is shared"
'''},
            {"name": "integrate on semi-infinite domains", "code": r'''
import math as _m
from quadlib import integrate
for _name, _f, _a, _b, _want in [("exp(-x) from 0", lambda x: _m.exp(-x), 0.0, _m.inf, 1.0),
                                 ("x^-3 from 1", lambda x: x ** -3.0, 1.0, _m.inf, 0.5),
                                 ("lorentz to 0", lambda x: 1.0 / (1.0 + x * x), -_m.inf, 0.0, _m.pi / 2.0)]:
    _r = integrate(_f, _a, _b, 1e-10)
    assert abs(_r.value - _want) < 1e-8, f"integrate({_name}) gave {_r.value!r}, expected {_want!r}"
    assert _r.evaluations > 0, f"integrate({_name}) reported no evaluations"
'''},
            {"name": "integrate on the whole real line", "code": r'''
import math as _m
from quadlib import integrate
_r = integrate(lambda x: _m.exp(-x * x), -_m.inf, _m.inf, 1e-10)
assert abs(_r.value - _m.sqrt(_m.pi)) < 1e-8, \
    f"Gaussian integral gave {_r.value!r}, expected {_m.sqrt(_m.pi)!r}"
_r = integrate(lambda x: 1.0 / (1.0 + x * x), -_m.inf, _m.inf, 1e-10)
assert abs(_r.value - _m.pi) < 1e-8, f"Cauchy integral gave {_r.value!r}, expected {_m.pi!r}"
_r = integrate(_m.sin, 3.0, 3.0)
assert _r.value == 0.0 and _r.evaluations == 0, f"A degenerate interval gave {_r!r}"
'''},
            {"name": "Tightening the tolerance tightens the answer", "code": r'''
import math as _m
from quadlib import integrate
_exact = _m.e - 1.0
_loose = integrate(_m.exp, 0.0, 1.0, 1e-3)
_tight = integrate(_m.exp, 0.0, 1.0, 1e-12)
assert abs(_loose.value - _exact) < 1e-3, f"tol=1e-3 left an error of {abs(_loose.value - _exact)!r}"
assert abs(_tight.value - _exact) < 1e-11, f"tol=1e-12 left an error of {abs(_tight.value - _exact)!r}"
assert _tight.evaluations > _loose.evaluations, \
    f"A tighter tolerance used {_tight.evaluations} evaluations vs {_loose.evaluations} — it should cost more"
'''},
            {"name": "Taylor half of the library", "code": r'''
import math as _m
from quadlib import taylor_coefficients, taylor_eval, taylor_bound
assert taylor_coefficients("exp", 3) == [1.0, 1.0, 0.5, 1.0 / 6.0], \
    f"Got {taylor_coefficients('exp', 3)!r}"
assert taylor_coefficients("cos", 4)[1] == 0.0 and abs(taylor_coefficients("cos", 4)[2] + 0.5) < 1e-15, \
    f"cos coefficients came back as {taylor_coefficients('cos', 4)!r}"
_got = taylor_eval(taylor_coefficients("sin", 15), 0.7)
assert abs(_got - _m.sin(0.7)) < 1e-12, f"sin series at 0.7 gave {_got!r}, expected {_m.sin(0.7)!r}"
assert abs(taylor_bound("sin", 0.5, 3) - 0.5 ** 4 / 24.0) < 1e-18, \
    f"taylor_bound('sin', 0.5, 3) gave {taylor_bound('sin', 0.5, 3)!r}"
for _kind, _fn in [("exp", _m.exp), ("cos", _m.cos)]:
    for _x in (-1.5, 0.4, 2.0):
        _err = abs(taylor_eval(taylor_coefficients(_kind, 8), _x) - _fn(_x))
        assert _err <= taylor_bound(_kind, _x, 8) + 1e-14, \
            f"{_kind} at {_x}: error {_err!r} exceeds its bound"
for _args in [("tanh", 3), ("exp", -1)]:
    try:
        taylor_coefficients(*_args)
        assert False, f"taylor_coefficients{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "series_sum brackets the true sum", "code": r'''
import math as _m
from quadlib import series_sum, Result
_r = series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-6)
assert isinstance(_r, Result), f"series_sum returned {type(_r).__name__}, expected Result"
assert _r.evaluations == 707, f"series_sum used {_r.evaluations} terms, expected 707"
assert _r.error <= 1e-6, f"Claimed bound {_r.error!r} exceeds the tolerance"
assert abs(_r.value - _m.pi ** 2 / 6.0) <= _r.error, \
    f"Estimate {_r.value!r} lies outside its own bound of {_r.error!r} around pi^2/6"
_r = series_sum(lambda k: 1.0 / k ** 3, lambda x: 0.5 / x ** 2, 1e-8)
assert abs(_r.value - 1.2020569031595943) <= _r.error, f"Apery estimate {_r.value!r} is outside its bound"
for _bad in (0.0, -1e-9):
    try:
        series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, _bad)
        assert False, f"series_sum with tol={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "error_report shapes the table", "code": r'''
import math as _m
from quadlib import integrate, series_sum, error_report
_rows = [("exp on [0,1]", integrate(_m.exp, 0.0, 1.0, 1e-10), _m.e - 1.0),
         ("basel", series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-8), _m.pi ** 2 / 6.0),
         ("no exact", integrate(_m.sin, 0.0, 1.0, 1e-10), None)]
_rep = error_report(_rows)
assert isinstance(_rep, str), "error_report returns a string, it does not print"
_lines = _rep.split("\n")
assert len(_lines) == 5, f"Expected 1 header + 3 rows + 1 total = 5 lines, got {len(_lines)}"
assert _lines[0].startswith("quantity"), f"Header line was {_lines[0]!r}"
for _i, _row in enumerate(_rows):
    assert _lines[_i + 1].startswith(_row[0]), f"Line {_i + 1} was {_lines[_i + 1]!r}, expected to start with {_row[0]!r}"
assert _lines[3].rstrip().endswith("-"), f"A row with no exact value should end in a dash; got {_lines[3]!r}"
assert _lines[-1].startswith("TOTAL EVALUATIONS"), f"Last line was {_lines[-1]!r}"
_total = sum(_row[1].evaluations for _row in _rows)
assert _lines[-1].rstrip().endswith(str(_total)), \
    f"Totals line {_lines[-1]!r} should end with {_total}"
'''},
            {"name": "quadlib.py is import-clean and fast", "code": r'''
import time as _t
_src = open("quadlib.py").read()
assert "print(" not in _src, "quadlib.py defines routines; the printing belongs in main.py"
for _banned in ("numpy", "scipy"):
    assert _banned not in _src, f"quadlib.py must not reach for {_banned}"
import math as _m
from quadlib import integrate, series_sum
_start = _t.time()
integrate(lambda x: _m.exp(-x * x), -_m.inf, _m.inf, 1e-10)
series_sum(lambda k: 1.0 / k ** 2, lambda x: 1.0 / x, 1e-8)
_elapsed = _t.time() - _start
assert _elapsed < 5.0, f"The demo workload took {_elapsed:.2f}s, which is far too slow"
'''},
        ],
    },
}
