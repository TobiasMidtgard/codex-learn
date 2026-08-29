"""MA111 — Calculus I: Limits & Derivatives. Author module."""

COURSE = {
    "id": "MA111",
    "title": "Calculus I — Limits & Derivatives",
    "year": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python"],
    "credits": 10,
    "hours": 110,
    "icon": "∫",
    "summary": (
        "Limits, derivatives and their numerical shadows. Every definition in the "
        "course is turned into a procedure that a machine can run, so you see where "
        "the epsilon-delta bookkeeping actually bites and where floating point "
        "quietly ruins an otherwise correct formula."
    ),
    "outcomes": [
        "Estimate a limit numerically and recognise when no limit exists",
        "Produce a delta witness for a given epsilon and check it by sampling",
        "Derive and implement forward and central difference quotients",
        "Measure the observed convergence order of a numerical rule and match it to theory",
        "Implement Newton-Raphson with derivative, divergence and iteration guards",
        "Locate critical points by a sign change of the derivative and classify them",
        "Report the global extrema of a function on a closed interval",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Stewart, *Calculus: Early Transcendentals*, 8th ed. — chapters 1-4",
        "Spivak, *Calculus*, 4th ed. — chapters 5-11",
        "Burden & Faires, *Numerical Analysis*, 10th ed. — sections 2.3 and 4.1",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Limits and continuity",
            "summary": "What a limit asserts, and how to probe one with a finite machine.",
            "concepts": [
                "The limit of f at a describes the punctured neighbourhood, never f(a) itself",
                "One-sided limits; a two-sided limit exists only when both agree",
                "The epsilon-delta definition: for every eps > 0 there is a delta > 0",
                "Failure modes: a jump, an unbounded blow-up, and endless oscillation",
                "Continuity at a means the limit exists and equals f(a)",
                "Numerical probing is evidence, not proof — catastrophic cancellation lies",
            ],
            "lab": {
                "title": "Numerical limits and an epsilon-delta witness",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Three functions that turn the definition of a limit into something executable.

## `limit_table(f, a, hs)`

For each step `h` in `hs`, record the pair of values either side of `a`.
Return a list of triples `(h, f(a - h), f(a + h))`, in the order `hs` gives.
Raise `ValueError` if any `h` is zero or negative — a step must shrink towards
`a` from somewhere.

```text
limit_table(lambda x: x * x, 3, [0.1]) -> [(0.1, 8.41, 9.61)]
```

## `estimate_limit(f, a, tol=1e-4, hs=HS)`

Take the **smallest** step in `hs`, evaluate `left = f(a - h)` and
`right = f(a + h)`, and then decide:

- if calling `f` raises `ArithmeticError` or `ValueError`, return `None`
- if either value is not finite, or exceeds `HUGE` in magnitude, return `None`
- if `abs(left - right) > tol * max(1.0, abs(left), abs(right))`, return `None`
- otherwise return `(left + right) / 2`

The third rule is *relative*: a steep but continuous function has a genuinely
large gap between the two sides, and must not be mistaken for a jump.

```text
estimate_limit(lambda x: math.sin(x) / x, 0.0)  ->  0.9999999999998333
estimate_limit(lambda x: abs(x) / x, 0.0)       ->  None
estimate_limit(lambda x: 1 / (x * x), 0.0)      ->  None
```

## `delta_for(f, a, L, eps, deltas)`

The witness checker. Return the **largest** `delta` in `deltas` for which every
sampled point of the punctured interval satisfies `abs(f(x) - L) < eps`, or
`None` when no candidate works. `deltas` may arrive in any order.

Sample `x = a + delta * k / SAMPLES` and `x = a - delta * k / SAMPLES` for
`k = 1 .. SAMPLES`; `k` never reaches 0, so `a` itself is never evaluated.
Raise `ValueError` when `eps` is zero or negative.
''',
                "files": [{"name": "main.py", "content": r'''
import math

HS = (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6)
HUGE = 1e8
SAMPLES = 50


def limit_table(f, a, hs):
    """[(h, f(a - h), f(a + h)) for h in hs]. ValueError if any h <= 0."""
    # your code here


def estimate_limit(f, a, tol=1e-4, hs=HS):
    """Two-sided estimate at the smallest step, or None when no limit is seen."""
    # your code here


def delta_for(f, a, L, eps, deltas):
    """Largest delta in deltas that witnesses the eps claim, else None."""
    # your code here


print(estimate_limit(lambda x: math.sin(x) / x, 0.0))
print(delta_for(lambda x: 3 * x + 1, 2.0, 7.0, 0.1, [1.0, 0.5, 0.05, 0.01]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

HS = (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6)
HUGE = 1e8
SAMPLES = 50


def limit_table(f, a, hs):
    """[(h, f(a - h), f(a + h)) for h in hs]. ValueError if any h <= 0."""
    rows = []
    for h in hs:
        if h <= 0:
            raise ValueError("every step h must be strictly positive")
        rows.append((h, f(a - h), f(a + h)))
    return rows


def estimate_limit(f, a, tol=1e-4, hs=HS):
    """Two-sided estimate at the smallest step, or None when no limit is seen."""
    h = min(hs)
    try:
        left = f(a - h)
        right = f(a + h)
    except (ArithmeticError, ValueError):
        # f is not even defined on one side of a, so nothing two-sided exists.
        return None
    if not (math.isfinite(left) and math.isfinite(right)):
        return None
    if abs(left) > HUGE or abs(right) > HUGE:
        return None
    # Relative gap: a steep continuous function must not read as a jump.
    scale = max(1.0, abs(left), abs(right))
    if abs(left - right) > tol * scale:
        return None
    return (left + right) / 2


def delta_for(f, a, L, eps, deltas):
    """Largest delta in deltas that witnesses the eps claim, else None."""
    if eps <= 0:
        raise ValueError("eps must be strictly positive")
    for delta in sorted(deltas, reverse=True):
        ok = True
        for k in range(1, SAMPLES + 1):
            offset = delta * k / SAMPLES
            for x in (a - offset, a + offset):
                if abs(f(x) - L) >= eps:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return delta
    return None


print(estimate_limit(lambda x: math.sin(x) / x, 0.0))
print(delta_for(lambda x: 3 * x + 1, 2.0, 7.0, 0.1, [1.0, 0.5, 0.05, 0.01]))
'''}],
                "hints": [
                    "Validate before you compute: loop over `hs` once, raise on the first bad step.",
                    "`min(hs)` picks the smallest step; the table order does not matter for the estimate.",
                    "`math.isfinite(v)` is False for both `inf` and `nan`, which is exactly the blow-up test.",
                    "`sorted(deltas, reverse=True)` gives you the candidates largest-first, so the first success is the answer.",
                ],
                "tests": [
                    {"name": "limit_table records both sides", "code": r'''
_rows = limit_table(lambda x: x * x, 3, [0.1, 0.01])
assert len(_rows) == 2, f"limit_table gave {len(_rows)} rows, expected 2"
assert abs(_rows[0][0] - 0.1) < 1e-12, f"first row step is {_rows[0][0]!r}, expected 0.1"
assert abs(_rows[0][1] - 8.41) < 1e-9, f"f(a-h) is {_rows[0][1]!r}, expected 8.41"
assert abs(_rows[0][2] - 9.61) < 1e-9, f"f(a+h) is {_rows[0][2]!r}, expected 9.61"
assert abs(_rows[1][1] - 8.9401) < 1e-9, f"second row f(a-h) is {_rows[1][1]!r}"
'''},
                    {"name": "limit_table refuses a non-positive step", "code": r'''
for _bad in ([0.1, 0.0], [-0.5], [0.0]):
    try:
        limit_table(lambda x: x, 1.0, _bad)
        assert False, f"limit_table with hs={_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "estimate_limit finds removable and ordinary limits", "code": r'''
import math as _math
_got = estimate_limit(lambda x: _math.sin(x) / x, 0.0)
assert _got is not None and abs(_got - 1.0) < 1e-9, f"sin(x)/x at 0 gave {_got!r}, expected ~1"
_got = estimate_limit(lambda x: (x * x - 1) / (x - 1), 1.0)
assert _got is not None and abs(_got - 2.0) < 1e-5, f"(x^2-1)/(x-1) at 1 gave {_got!r}, expected ~2"
_got = estimate_limit(lambda x: x * x + 3 * x, 2.0)
assert _got is not None and abs(_got - 10.0) < 1e-6, f"x^2+3x at 2 gave {_got!r}, expected ~10"
'''},
                    {"name": "A steep continuous function still has a limit", "code": r'''
_got = estimate_limit(lambda x: 1000.0 * x, 1.0)
assert _got is not None, "1000x is continuous — the gap test must be relative, not absolute"
assert abs(_got - 1000.0) < 1e-6, f"1000x at 1 gave {_got!r}, expected ~1000"
'''},
                    {"name": "estimate_limit rejects jumps, blow-ups and undefined sides", "code": r'''
import math as _math
assert estimate_limit(lambda x: abs(x) / x, 0.0) is None, "|x|/x jumps at 0 — expected None"
assert estimate_limit(lambda x: 1.0 / x, 0.0) is None, "1/x is unbounded at 0 — expected None"
assert estimate_limit(lambda x: 1.0 / (x * x), 0.0) is None, "1/x^2 blows up at 0 — expected None"
assert estimate_limit(_math.log, 0.0) is None, "log is undefined left of 0 — expected None"
'''},
                    {"name": "delta_for returns the largest witness", "code": r'''
_f = lambda x: 3 * x + 1
assert delta_for(_f, 2.0, 7.0, 0.1, [0.01, 1.0, 0.05, 0.5]) == 0.01, \
    f"Got {delta_for(_f, 2.0, 7.0, 0.1, [0.01, 1.0, 0.05, 0.5])!r}, expected 0.01"
assert delta_for(_f, 2.0, 7.0, 10.0, [0.01, 1.0, 0.05, 0.5]) == 1.0, \
    "With eps=10 even delta=1 works, and it is the largest candidate"
_g = lambda x: (x * x - 1) / (x - 1)
assert delta_for(_g, 1.0, 2.0, 0.01, [0.1, 0.02, 0.005]) == 0.005, \
    "The punctured neighbourhood must never evaluate f at a itself"
'''},
                    {"name": "delta_for gives up, and refuses a non-positive eps", "code": r'''
_f = lambda x: 3 * x + 1
assert delta_for(_f, 2.0, 7.0, 1e-9, [0.01, 1.0, 0.05]) is None, \
    "No candidate delta is small enough, so the answer is None"
assert delta_for(_f, 2.0, 7.0, 1.0, []) is None, "No candidates at all means None"
for _bad in (0.0, -1.0):
    try:
        delta_for(_f, 2.0, 7.0, _bad, [1.0])
        assert False, f"eps={_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "The derivative as a limit",
            "summary": "Difference quotients, their truncation error, and the order that error obeys.",
            "concepts": [
                "The derivative is the limit of a difference quotient, not a formula to memorise",
                "Forward difference: f'(x) = (f(x+h) - f(x))/h + O(h)",
                "Central difference: f'(x) = (f(x+h) - f(x-h))/(2h) + O(h^2)",
                "Taylor expansion is where both error terms come from",
                "Observed order p from a pair of steps: p = log(e1/e2) / log(h1/h2)",
                "Richardson extrapolation cancels the leading error term and buys two orders",
                "Roundoff sets a floor: shrinking h forever makes the answer worse",
            ],
            "lab": {
                "title": "Finite differences and their error order",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Four functions. The last two measure how fast the first two converge.

## `forward_diff(f, x, h)` and `central_diff(f, x, h)`

The two standard quotients. Both raise `ValueError` when `h <= 0`.

```text
f(x) = x*x + 3x,  x = 2,  h = 0.5
forward_diff -> 7.5     central_diff -> 7.0     exact f'(2) = 7
```

Central difference is exact for any quadratic; forward difference is off by
roughly `f''(x) * h / 2`. That is the whole point of the module.

## `richardson(f, x, h)`

Combine two central differences to cancel the `h^2` term:

```text
richardson(f, x, h) = (4 * central_diff(f, x, h/2) - central_diff(f, x, h)) / 3
```

The remaining error is `O(h^4)`.

## `errors_for(rule, f, x, exact, hs)` and `error_order(errors, hs)`

`errors_for` returns `[abs(rule(f, x, h) - exact) for h in hs]`.

`error_order` turns that list into a single observed order: the **mean** of

```text
log(e_i / e_{i+1}) / log(h_i / h_{i+1})
```

over every consecutive pair. Raise `ValueError` if the two lists differ in
length, hold fewer than two points, contain an error that is not strictly
positive, or contain two equal steps.

With `hs = (0.4, 0.2, 0.1, 0.05)` and `f = sin` at `x = 1` you should observe
about `1.03` for forward, `2.00` for central and `4.00` for Richardson.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def forward_diff(f, x, h):
    """(f(x+h) - f(x)) / h. ValueError when h <= 0."""
    # your code here


def central_diff(f, x, h):
    """(f(x+h) - f(x-h)) / (2h). ValueError when h <= 0."""
    # your code here


def richardson(f, x, h):
    """(4 * central_diff(f, x, h/2) - central_diff(f, x, h)) / 3."""
    # your code here


def errors_for(rule, f, x, exact, hs):
    """Absolute error of rule at each step in hs."""
    # your code here


def error_order(errors, hs):
    """Mean observed convergence order over consecutive (h, error) pairs."""
    # your code here


HS = (0.4, 0.2, 0.1, 0.05)
for name, rule in [("forward", forward_diff), ("central", central_diff),
                   ("richardson", richardson)]:
    errs = errors_for(rule, math.sin, 1.0, math.cos(1.0), HS)
    print(name, round(error_order(errs, HS), 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def forward_diff(f, x, h):
    """(f(x+h) - f(x)) / h. ValueError when h <= 0."""
    if h <= 0:
        raise ValueError("h must be strictly positive")
    return (f(x + h) - f(x)) / h


def central_diff(f, x, h):
    """(f(x+h) - f(x-h)) / (2h). ValueError when h <= 0."""
    if h <= 0:
        raise ValueError("h must be strictly positive")
    return (f(x + h) - f(x - h)) / (2 * h)


def richardson(f, x, h):
    """(4 * central_diff(f, x, h/2) - central_diff(f, x, h)) / 3."""
    # The h^2 terms of the two central differences cancel exactly, leaving O(h^4).
    return (4 * central_diff(f, x, h / 2) - central_diff(f, x, h)) / 3


def errors_for(rule, f, x, exact, hs):
    """Absolute error of rule at each step in hs."""
    return [abs(rule(f, x, h) - exact) for h in hs]


def error_order(errors, hs):
    """Mean observed convergence order over consecutive (h, error) pairs."""
    errors = list(errors)
    hs = list(hs)
    if len(errors) != len(hs):
        raise ValueError("errors and hs must have the same length")
    if len(hs) < 2:
        raise ValueError("need at least two points to observe an order")
    if any(e <= 0 for e in errors):
        raise ValueError("an error of zero has no order — the rule is exact here")
    if any(h <= 0 for h in hs):
        raise ValueError("every step h must be strictly positive")
    orders = []
    for i in range(len(hs) - 1):
        if hs[i] == hs[i + 1]:
            raise ValueError("two equal steps give no information")
        orders.append(math.log(errors[i] / errors[i + 1])
                      / math.log(hs[i] / hs[i + 1]))
    return sum(orders) / len(orders)


HS = (0.4, 0.2, 0.1, 0.05)
for name, rule in [("forward", forward_diff), ("central", central_diff),
                   ("richardson", richardson)]:
    errs = errors_for(rule, math.sin, 1.0, math.cos(1.0), HS)
    print(name, round(error_order(errs, HS), 3))
'''}],
                "hints": [
                    "Guard `h` first in both quotients, then return the one-line expression.",
                    "`richardson` must call `central_diff`, not re-derive it: `(4 * central_diff(f, x, h/2) - central_diff(f, x, h)) / 3`.",
                    "`errors_for` is a single list comprehension over `hs`.",
                    "Do every validation in `error_order` before the loop, so a bad input never reaches `math.log`.",
                ],
                "tests": [
                    {"name": "Both quotients on a quadratic", "code": r'''
_f = lambda x: x * x + 3 * x
assert abs(forward_diff(_f, 2.0, 0.5) - 7.5) < 1e-12, \
    f"forward_diff gave {forward_diff(_f, 2.0, 0.5)!r}, expected 7.5"
assert abs(central_diff(_f, 2.0, 0.5) - 7.0) < 1e-12, \
    f"central_diff gave {central_diff(_f, 2.0, 0.5)!r}, expected 7.0 exactly"
assert abs(central_diff(_f, 2.0, 1e-3) - 7.0) < 1e-9, \
    "central difference is exact for quadratics at every step size"
'''},
                    {"name": "Both quotients refuse a non-positive step", "code": r'''
for _rule in (forward_diff, central_diff):
    for _bad in (0.0, -0.1):
        try:
            _rule(lambda x: x, 1.0, _bad)
            assert False, f"{_rule.__name__} with h={_bad!r} should raise ValueError"
        except ValueError:
            pass
'''},
                    {"name": "richardson is far sharper than central", "code": r'''
import math as _math
_exact = _math.cos(1.0)
_c = abs(central_diff(_math.sin, 1.0, 0.1) - _exact)
_r = abs(richardson(_math.sin, 1.0, 0.1) - _exact)
assert _r < _c / 1000, f"richardson error {_r!r} should be far below central error {_c!r}"
assert _r < 1e-6, f"richardson error at h=0.1 is {_r!r}, expected below 1e-6"
'''},
                    {"name": "errors_for lines the errors up with the steps", "code": r'''
import math as _math
_hs = (0.4, 0.2, 0.1, 0.05)
_e = errors_for(central_diff, _math.sin, 1.0, _math.cos(1.0), _hs)
assert len(_e) == 4, f"errors_for gave {len(_e)} entries, expected 4"
assert all(_e[i] > _e[i + 1] for i in range(3)), f"Errors should shrink with h: {_e!r}"
assert abs(_e[0] - 0.0142932) < 1e-4, f"error at h=0.4 is {_e[0]!r}, expected about 0.014293"
'''},
                    {"name": "Observed orders match the theory", "code": r'''
import math as _math
_hs = (0.4, 0.2, 0.1, 0.05)
_p = error_order(errors_for(forward_diff, _math.sin, 1.0, _math.cos(1.0), _hs), _hs)
assert abs(_p - 1.0) < 0.1, f"forward difference observed order {_p!r}, expected about 1"
_p = error_order(errors_for(central_diff, _math.sin, 1.0, _math.cos(1.0), _hs), _hs)
assert abs(_p - 2.0) < 0.05, f"central difference observed order {_p!r}, expected about 2"
_p = error_order(errors_for(richardson, _math.sin, 1.0, _math.cos(1.0), _hs), _hs)
assert abs(_p - 4.0) < 0.1, f"richardson observed order {_p!r}, expected about 4"
'''},
                    {"name": "error_order on a clean synthetic sequence", "code": r'''
_hs = [0.1, 0.05, 0.025]
_errs = [3.0 * h ** 2 for h in _hs]
assert abs(error_order(_errs, _hs) - 2.0) < 1e-9, \
    f"A pure h^2 sequence must read exactly 2, got {error_order(_errs, _hs)!r}"
'''},
                    {"name": "error_order rejects unusable input", "code": r'''
for _errs, _hs in [([1.0], [0.1]),
                   ([1.0, 0.5], [0.1]),
                   ([1.0, 0.0], [0.1, 0.05]),
                   ([1.0, -0.5], [0.1, 0.05]),
                   ([1.0, 0.5], [0.1, 0.1]),
                   ([1.0, 0.5], [0.1, 0.0])]:
    try:
        error_order(_errs, _hs)
        assert False, f"error_order({_errs!r}, {_hs!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Newton-Raphson and the failure modes of iteration",
            "summary": "Tangent-line root finding, and the three ways it goes wrong.",
            "concepts": [
                "Newton's step is the root of the tangent line: x - f(x)/f'(x)",
                "Quadratic convergence near a simple root, and what breaks it",
                "A vanishing derivative leaves the tangent horizontal — no next point exists",
                "Divergence: iterates can run away, as they do for arctan from a large start",
                "Attracting cycles: x^3 - 2x + 2 from 0 alternates between 0 and 1 forever",
                "A relative step h * max(1, |x|) keeps the numerical derivative usable at large x",
                "Every iteration needs a cap; a browser tab has no Ctrl-C",
            ],
            "lab": {
                "title": "Newton's method with guards",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
The two exception classes at the top of `main.py` are given. Use them.

## `numeric_derivative(f, x, h=1e-6)`

A central difference with a **relative** step: `step = h * max(1.0, abs(x))`.
At `x = 120000` an absolute step of `1e-6` is smaller than one unit in the last
place of `x`, so `f(x+h)` and `f(x-h)` become the same number and the quotient
collapses to zero. Scaling the step with `x` avoids that.

## `newton(f, x0, tol=1e-12, max_iter=50, h=1e-6)`

Return `(root, iterations)`, where `iterations` counts the Newton steps taken.

The loop, in order:

1. `fx = f(x)`. If `abs(fx) <= tol`, return `(x, iterations)`.
2. If the cap is reached, raise `Diverged`.
3. `d = numeric_derivative(f, x, h)`. If `abs(d) < DERIV_FLOOR`, raise
   `ZeroDerivative`.
4. `x = x - fx / d`.
5. If `x` is not finite, or `abs(x) > DIVERGE_LIMIT`, raise `Diverged`.

Raise `ValueError` for `tol <= 0` or `max_iter < 1` — those are caller mistakes,
not iteration failures.

```text
newton(lambda x: x*x - 2, 1.0)          -> (1.4142135623730951, 5)
newton(lambda x: x*x + 1, 0.0)          -> ZeroDerivative   f'(0) = 0
newton(lambda x: x**3 - 2*x + 2, 0.0)   -> Diverged         a 2-cycle: 0, 1, 0, 1, ...
newton(math.atan, 2.0)                  -> Diverged         the iterates run away
```
''',
                "files": [{"name": "main.py", "content": r'''
import math

DERIV_FLOOR = 1e-14
DIVERGE_LIMIT = 1e9


class ZeroDerivative(RuntimeError):
    """The tangent is horizontal, so Newton has no next point."""


class Diverged(RuntimeError):
    """The iterates ran away, or the iteration cap was reached."""


def numeric_derivative(f, x, h=1e-6):
    """Central difference with a step scaled by max(1, |x|)."""
    # your code here


def newton(f, x0, tol=1e-12, max_iter=50, h=1e-6):
    """(root, iterations). ZeroDerivative / Diverged on failure."""
    # your code here


print(newton(lambda x: x * x - 2, 1.0))
print(newton(lambda x: math.cos(x) - x, 1.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

DERIV_FLOOR = 1e-14
DIVERGE_LIMIT = 1e9


class ZeroDerivative(RuntimeError):
    """The tangent is horizontal, so Newton has no next point."""


class Diverged(RuntimeError):
    """The iterates ran away, or the iteration cap was reached."""


def numeric_derivative(f, x, h=1e-6):
    """Central difference with a step scaled by max(1, |x|)."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - f(x - step)) / (2 * step)


def newton(f, x0, tol=1e-12, max_iter=50, h=1e-6):
    """(root, iterations). ZeroDerivative / Diverged on failure."""
    if tol <= 0:
        raise ValueError("tol must be strictly positive")
    if max_iter < 1:
        raise ValueError("max_iter must be at least 1")

    x = float(x0)
    for taken in range(max_iter + 1):
        fx = f(x)
        if abs(fx) <= tol:
            return (x, taken)
        if taken == max_iter:
            raise Diverged(f"no convergence in {max_iter} iterations")
        d = numeric_derivative(f, x, h)
        if abs(d) < DERIV_FLOOR:
            raise ZeroDerivative(f"derivative vanished at x={x!r}")
        x = x - fx / d
        # Check the magnitude before the next derivative: a runaway iterate
        # makes the difference quotient meaningless as well as useless.
        if not math.isfinite(x) or abs(x) > DIVERGE_LIMIT:
            raise Diverged(f"iterates left the useful range at x={x!r}")
    raise Diverged("unreachable")


print(newton(lambda x: x * x - 2, 1.0))
print(newton(lambda x: math.cos(x) - x, 1.0))
'''}],
                "hints": [
                    "`step = h * max(1.0, abs(x))` — then divide by `2 * step`, not by `2 * h`.",
                    "Validate `tol` and `max_iter` before the loop starts; those are argument errors, not iteration failures.",
                    "Use `for taken in range(max_iter + 1)` so the convergence test gets one look at the final iterate before the cap fires.",
                    "Raise `Diverged` immediately after updating `x`, before the next derivative is taken.",
                ],
                "tests": [
                    {"name": "numeric_derivative is accurate", "code": r'''
import math as _math
assert abs(numeric_derivative(_math.sin, 1.0) - _math.cos(1.0)) < 1e-8, \
    f"d/dx sin at 1 gave {numeric_derivative(_math.sin, 1.0)!r}, expected {_math.cos(1.0)!r}"
assert abs(numeric_derivative(_math.exp, 2.0) - _math.exp(2.0)) < 1e-6, \
    f"d/dx exp at 2 gave {numeric_derivative(_math.exp, 2.0)!r}"
assert abs(numeric_derivative(lambda x: x * x, 3.0) - 6.0) < 1e-8, "d/dx x^2 at 3 is 6"
'''},
                    {"name": "The relative step survives a large x", "code": r'''
import math as _math
_d = numeric_derivative(_math.atan, 121977.0)
assert _d != 0.0, "An absolute step of 1e-6 vanishes at x=121977 — scale it by |x|"
assert abs(_d - 1.0 / (1.0 + 121977.0 ** 2)) < 1e-14, f"Got {_d!r}"
'''},
                    {"name": "newton finds simple roots quickly", "code": r'''
import math as _math
_r, _n = newton(lambda x: x * x - 2, 1.0)
assert abs(_r - _math.sqrt(2)) < 1e-10, f"sqrt(2) came out as {_r!r}"
assert _n <= 10, f"Newton took {_n} iterations for sqrt(2), expected under 10"
_r, _n = newton(lambda x: _math.cos(x) - x, 1.0)
assert abs(_r - 0.7390851332151607) < 1e-9, f"cos(x)=x root came out as {_r!r}"
_r, _n = newton(lambda x: x ** 3 - 2 * x - 5, 2.0)
assert abs(_r - 2.0945514815423265) < 1e-9, f"cubic root came out as {_r!r}"
'''},
                    {"name": "The starting point decides which root you get", "code": r'''
import math as _math
_r, _n = newton(lambda x: x * x - 2, -1.0)
assert abs(_r + _math.sqrt(2)) < 1e-10, f"From x0=-1 the root should be -sqrt(2), got {_r!r}"
'''},
                    {"name": "Starting on the root costs no iterations", "code": r'''
import math as _math
_r, _n = newton(lambda x: x * x - 2, _math.sqrt(2))
assert _n == 0, f"Already at the root, so 0 steps — got {_n}"
assert abs(_r - _math.sqrt(2)) < 1e-15, f"Got {_r!r}"
'''},
                    {"name": "A horizontal tangent raises ZeroDerivative", "code": r'''
try:
    newton(lambda x: x * x + 1, 0.0)
    assert False, "f'(0) = 0 for x^2 + 1, so this must raise ZeroDerivative"
except ZeroDerivative:
    pass
'''},
                    {"name": "Cycles and runaways raise Diverged", "code": r'''
import math as _math
try:
    newton(lambda x: x ** 3 - 2 * x + 2, 0.0)
    assert False, "x^3 - 2x + 2 from 0 cycles forever, so this must raise Diverged"
except Diverged:
    pass
try:
    newton(_math.atan, 2.0)
    assert False, "arctan from x0=2 runs away, so this must raise Diverged"
except Diverged:
    pass
try:
    newton(lambda x: x ** 3 - 2 * x - 5, 2.0, max_iter=1)
    assert False, "One iteration is not enough here, so this must raise Diverged"
except Diverged:
    pass
'''},
                    {"name": "Bad arguments raise ValueError, not Diverged", "code": r'''
for _kw in ({"tol": 0.0}, {"tol": -1e-9}, {"max_iter": 0}, {"max_iter": -3}):
    try:
        newton(lambda x: x * x - 2, 1.0, **_kw)
        assert False, f"newton(..., {_kw!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Critical points and optimisation",
            "summary": "Finding where the derivative changes sign, and deciding what happens there.",
            "concepts": [
                "Fermat's theorem: an interior extremum forces f'(x) = 0",
                "A sign change of f' brackets a critical point; bisection then locates it",
                "The second derivative test, and the cases where it is silent",
                "The first derivative test as the fallback when f''(x) is zero",
                "The extreme value theorem: on a closed interval the candidates are the critical points plus the two endpoints",
                "Grid-based search misses anything narrower than the grid — state the limitation",
                "A sample that lands exactly on a root produces no sign change and must be handled separately",
            ],
            "lab": {
                "title": "Locating and classifying critical points",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
`derivative` and `second_derivative` are given at the top of `main.py`. You
write the four functions below.

## `bracket_sign_changes(g, a, b, n)`

Evaluate `g` at the `n + 1` points `x_k = a + k * (b - a) / n`. Walk the
samples in order and emit:

- `(x_k, x_k)` — a *degenerate* bracket — whenever `g(x_k)` is exactly `0.0`
- `(x_k, x_{k+1})` when `g(x_k) * g(x_{k+1}) < 0`

Check every index once, including the last point. Raise `ValueError` when
`n < 1` or `a >= b`.

The degenerate case is not pedantry: for `f(x) = x^4 - 2x^2` on `[-2, 2]` with
`n = 400` the grid lands exactly on `-1`, `0` and `1`, where `f'` is zero and
never changes sign across a pair.

## `bisect(g, lo, hi, tol=1e-12, max_iter=200)`

Bisection. Return `lo` immediately when `lo == hi`. Raise `ValueError` when
`g(lo) * g(hi) > 0`. Otherwise halve until the bracket is no wider than `tol`
or the cap is reached, then return the midpoint.

## `critical_points(f, a, b, n=400)`

Bracket the sign changes of `derivative(f, ·)`, bisect each one, round the
roots to 9 decimal places, drop duplicates, and return a list of `(x, kind)`
sorted by `x`. Classify with the second derivative test, threshold `1e-5`:

```text
f''(x) >  1e-5   -> "minimum"
f''(x) < -1e-5   -> "maximum"
otherwise        -> first derivative test one grid step either side:
                    negative then positive -> "minimum"
                    positive then negative -> "maximum"
                    anything else          -> "inflection"
```

## `optimise(f, a, b, n=400)`

The extreme value theorem, mechanised. Consider the endpoints and every
critical point, and return `{"min": (x, f(x)), "max": (x, f(x))}`. Ties in the
value are broken by the smaller `x`.
''',
                "files": [{"name": "main.py", "content": r'''
import math

CLASSIFY_TOL = 1e-5


def derivative(f, x, h=1e-6):
    """Given. Central difference with a step scaled by max(1, |x|)."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - f(x - step)) / (2 * step)


def second_derivative(f, x, h=1e-4):
    """Given. Second-order central difference."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - 2 * f(x) + f(x - step)) / (step * step)


def bracket_sign_changes(g, a, b, n):
    """Brackets where g changes sign, plus degenerate (x, x) for exact zeros."""
    # your code here


def bisect(g, lo, hi, tol=1e-12, max_iter=200):
    """Bisect a bracket down to width tol. ValueError if the signs agree."""
    # your code here


def critical_points(f, a, b, n=400):
    """Sorted [(x, kind)] with kind in minimum / maximum / inflection."""
    # your code here


def optimise(f, a, b, n=400):
    """{"min": (x, f(x)), "max": (x, f(x))} over endpoints and critical points."""
    # your code here


print(critical_points(lambda x: x ** 3 - 3 * x, -3.0, 3.0))
print(optimise(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

CLASSIFY_TOL = 1e-5


def derivative(f, x, h=1e-6):
    """Given. Central difference with a step scaled by max(1, |x|)."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - f(x - step)) / (2 * step)


def second_derivative(f, x, h=1e-4):
    """Given. Second-order central difference."""
    step = h * max(1.0, abs(x))
    return (f(x + step) - 2 * f(x) + f(x - step)) / (step * step)


def bracket_sign_changes(g, a, b, n):
    """Brackets where g changes sign, plus degenerate (x, x) for exact zeros."""
    if n < 1:
        raise ValueError("n must be at least 1")
    if a >= b:
        raise ValueError("need a < b")
    step = (b - a) / n
    xs = [a + step * k for k in range(n + 1)]
    vals = [g(x) for x in xs]
    out = []
    for i in range(n):
        if vals[i] == 0.0:
            out.append((xs[i], xs[i]))
        elif vals[i] * vals[i + 1] < 0.0:
            out.append((xs[i], xs[i + 1]))
    if vals[n] == 0.0:
        out.append((xs[n], xs[n]))
    return out


def bisect(g, lo, hi, tol=1e-12, max_iter=200):
    """Bisect a bracket down to width tol. ValueError if the signs agree."""
    if lo == hi:
        return lo
    g_lo, g_hi = g(lo), g(hi)
    if g_lo * g_hi > 0.0:
        raise ValueError("g does not change sign across the bracket")
    for _ in range(max_iter):
        if hi - lo <= tol:
            break
        mid = 0.5 * (lo + hi)
        g_mid = g(mid)
        if g_mid == 0.0:
            return mid
        if g_lo * g_mid < 0.0:
            hi, g_hi = mid, g_mid
        else:
            lo, g_lo = mid, g_mid
    return 0.5 * (lo + hi)


def critical_points(f, a, b, n=400):
    """Sorted [(x, kind)] with kind in minimum / maximum / inflection."""
    slope = lambda x: derivative(f, x)
    step = (b - a) / n
    roots = []
    for lo, hi in bracket_sign_changes(slope, a, b, n):
        roots.append(round(bisect(slope, lo, hi), 9) + 0.0)
    out = []
    for x in sorted(set(roots)):
        out.append((x, _classify(f, x, step)))
    return out


def _classify(f, x, step):
    """Second derivative test, falling back to the first derivative test."""
    d2 = second_derivative(f, x)
    if d2 > CLASSIFY_TOL:
        return "minimum"
    if d2 < -CLASSIFY_TOL:
        return "maximum"
    left = derivative(f, x - step)
    right = derivative(f, x + step)
    if left < 0.0 < right:
        return "minimum"
    if left > 0.0 > right:
        return "maximum"
    return "inflection"


def optimise(f, a, b, n=400):
    """Endpoints plus critical points; ties in the value keep the smaller x."""
    xs = sorted(set([a, b] + [x for x, _ in critical_points(f, a, b, n)]))
    pairs = [(x, f(x)) for x in xs]
    lowest = min(pairs, key=lambda pair: (pair[1], pair[0]))
    highest = max(pairs, key=lambda pair: (pair[1], -pair[0]))
    return {"min": lowest, "max": highest}


print(critical_points(lambda x: x ** 3 - 3 * x, -3.0, 3.0))
print(optimise(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0))
'''}],
                "hints": [
                    "Evaluate `g` once per grid point into a list; calling it again inside the loop doubles the work and invites inconsistency.",
                    "In `bisect`, keep the sign of `g(lo)` in a variable and update it with the bracket — one evaluation per halving.",
                    "`round(x, 9) + 0.0` both deduplicates near-identical roots and turns `-0.0` into `0.0`.",
                    "`min(pairs, key=lambda p: (p[1], p[0]))` and `max(pairs, key=lambda p: (p[1], -p[0]))` give the tie rule in one line each.",
                ],
                "tests": [
                    {"name": "bracket_sign_changes finds ordinary crossings", "code": r'''
_b = bracket_sign_changes(lambda x: x * x - 2, 0.0, 3.0, 30)
assert len(_b) == 1, f"x^2-2 crosses once on [0,3], got {_b!r}"
_lo, _hi = _b[0]
assert _lo < 1.4142135623730951 < _hi, f"Bracket {_b[0]!r} should straddle sqrt(2)"
assert bracket_sign_changes(lambda x: x * x + 1, -1.0, 1.0, 20) == [], \
    "x^2+1 has no zero, so there is nothing to bracket"
'''},
                    {"name": "An exact zero on the grid gives a degenerate bracket", "code": r'''
_b = bracket_sign_changes(lambda x: x * (x - 1), -1.0, 2.0, 30)
assert (0.0, 0.0) in _b, f"g(0) is exactly 0 on this grid, expected (0.0, 0.0) in {_b!r}"
_deg = [p for p in _b if p[0] == p[1]]
assert len(_deg) == 2, f"Both 0 and 1 sit on the grid, expected 2 degenerate brackets, got {_deg!r}"
'''},
                    {"name": "bracket_sign_changes validates its interval", "code": r'''
for _args in [(0.0, 1.0, 0), (0.0, 1.0, -5), (1.0, 1.0, 10), (2.0, 1.0, 10)]:
    try:
        bracket_sign_changes(lambda x: x, *_args)
        assert False, f"bracket_sign_changes(g, {_args!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "bisect converges, and refuses a bad bracket", "code": r'''
import math as _math
_g = lambda x: x * x - 2
assert abs(bisect(_g, 1.0, 2.0) - _math.sqrt(2)) < 1e-10, \
    f"bisect gave {bisect(_g, 1.0, 2.0)!r}, expected sqrt(2)"
assert bisect(_g, 1.5, 1.5) == 1.5, "A degenerate bracket returns its own point"
try:
    bisect(_g, 2.0, 3.0)
    assert False, "g has the same sign at both ends, so this must raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "critical_points of x^3 - 3x", "code": r'''
_cp = critical_points(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
assert len(_cp) == 2, f"Expected two critical points, got {_cp!r}"
assert abs(_cp[0][0] + 1.0) < 1e-6 and _cp[0][1] == "maximum", f"Got {_cp[0]!r}, expected (-1, maximum)"
assert abs(_cp[1][0] - 1.0) < 1e-6 and _cp[1][1] == "minimum", f"Got {_cp[1]!r}, expected (1, minimum)"
'''},
                    {"name": "critical_points of the double well, grid points and all", "code": r'''
_cp = critical_points(lambda x: x ** 4 - 2 * x * x, -2.0, 2.0)
assert len(_cp) == 3, f"x^4-2x^2 has three critical points on [-2,2], got {_cp!r}"
_kinds = [k for _, k in _cp]
assert _kinds == ["minimum", "maximum", "minimum"], f"Got {_kinds!r}"
assert abs(_cp[0][0] + 1.0) < 1e-6 and abs(_cp[1][0]) < 1e-6 and abs(_cp[2][0] - 1.0) < 1e-6, \
    f"Critical points should sit at -1, 0, 1 — got {[x for x, _ in _cp]!r}"
'''},
                    {"name": "The first derivative fallback catches a flat minimum", "code": r'''
_cp = critical_points(lambda x: x ** 4, -1.0, 1.0)
assert len(_cp) == 1, f"x^4 has one critical point on [-1,1], got {_cp!r}"
assert abs(_cp[0][0]) < 1e-6, f"It sits at 0, got {_cp[0][0]!r}"
assert _cp[0][1] == "minimum", \
    "f''(0) is zero for x^4, so the first derivative test must decide — expected minimum"
'''},
                    {"name": "optimise solves the open-box problem", "code": r'''
_V = lambda x: x * (30 - 2 * x) * (16 - 2 * x)
_r = optimise(_V, 0.0, 8.0)
_x, _y = _r["max"]
assert abs(_x - 10.0 / 3.0) < 1e-6, f"The box is largest at x=10/3, got {_x!r}"
assert abs(_y - 19600.0 / 27.0) < 1e-4, f"Maximum volume is 19600/27, got {_y!r}"
assert _r["min"] == (0.0, 0.0), f"Both endpoints give volume 0; ties keep the smaller x — got {_r['min']!r}"
'''},
                    {"name": "optimise weighs endpoints against interior points", "code": r'''
_r = optimise(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
assert abs(_r["min"][0] + 3.0) < 1e-9 and abs(_r["min"][1] + 18.0) < 1e-6, \
    f"Global minimum is the left endpoint (-3, -18), got {_r['min']!r}"
assert abs(_r["max"][0] - 3.0) < 1e-9 and abs(_r["max"][1] - 18.0) < 1e-6, \
    f"Global maximum is the right endpoint (3, 18), got {_r['max']!r}"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — single-variable function analyser",
        "runtime": "python",
        "minutes": 240,
        "brief": r'''
Everything in the course, assembled into one reusable object. `analyser.py`
holds the class and is what the checks import; `main.py` is a demo that
analyses two functions and prints their reports.

## `FunctionAnalyser(f, a, b, samples=400)`

Stores `f`, the closed interval `[a, b]` as floats, the sample count, and the
grid step `(b - a) / samples`. It refuses bad input at construction time with
`ValueError`: a non-callable `f`, an interval where `a >= b`, or fewer than two
samples.

## Numerical primitives

- `derivative(x, h=1e-6)` — central difference, step `h * max(1, abs(x))`
- `second_derivative(x, h=1e-4)` — `(f(x+s) - 2f(x) + f(x-s)) / s^2`, same
  relative step

## Structure

- `roots()` — sorted `x` values in `[a, b]` where `f` crosses zero, or where a
  grid sample lands exactly on a zero. Round each to 9 decimals and deduplicate.
- `critical_points()` — sorted `(x, kind)` pairs from the zeros of the
  derivative, `kind` in `"minimum"`, `"maximum"`, `"inflection"`. Classify with
  the second derivative test at threshold `1e-5`, falling back to the sign of
  the derivative one grid step either side.
- `inflection_points()` — zeros of the second derivative, kept **only** when
  the second derivative genuinely changes sign one grid step either side. A
  touch that does not cross is not an inflection.
- `monotonic_intervals()` — cut `[a, b]` at the critical points and label each
  piece `"increasing"`, `"decreasing"` or `"constant"` by the sign of the
  derivative at its midpoint. Returns `(lo, hi, label)` triples.
- `extrema()` — `{"min": (x, f(x)), "max": (x, f(x))}` over the endpoints and
  the critical points, ties broken by the smaller `x`.

## `report()`

A nine-line string, in this order, values formatted to six decimals and an
empty list written as `none`:

```text
interval: [-3.000000, 3.000000]
roots: -1.732051, 0.000000, 1.732051
minima: 1.000000
maxima: -1.000000
inflections: 0.000000
increasing: [-3.000000, -1.000000], [1.000000, 3.000000]
decreasing: [-1.000000, 1.000000]
global min: f(-3.000000) = -18.000000
global max: f(3.000000) = 18.000000
```

## Known limitations, which you should state in a docstring

A grid search cannot see a feature narrower than one grid step, and a double
root where `f` touches zero without crossing is only found when a sample lands
on it exactly. Say so rather than pretending otherwise.
''',
        "deliverables": [
            "`analyser.py` — the `FunctionAnalyser` class, importable with no side effects",
            "`main.py` — a demo that builds two analysers and prints both reports",
            "Constructor validation that raises `ValueError` instead of storing a broken interval",
            "A shared bracket-and-bisect helper reused by roots, critical points and inflections",
            "Classification that falls back to the first derivative test when the second is silent",
            "A `report()` string a human can read in a terminal",
        ],
        "constraints": [
            "Standard library only; `math` is the only import you need",
            "`analyser.py` must define the class only — importing it must print nothing",
            "No global mutable state: two analysers must not share any cached result",
            "Every public method returns a value; none of them print",
            "Bisection must be capped, so no input can hang the browser tab",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the empty-result and validation cases."},
            {"criterion": "Numerical robustness", "weight": 25,
             "evidence": "Relative step sizes, exact-zero grid samples handled, bisection capped, inflections confirmed by an actual sign change."},
            {"criterion": "Decomposition and reuse", "weight": 20,
             "evidence": "One bracketing helper and one bisection helper serve roots, critical points and inflections; nothing is copied three times."},
            {"criterion": "Readability and documentation", "weight": 15,
             "evidence": "Docstrings on every public method, the grid limitation stated honestly, no dead code or debug prints."},
        ],
        "hints": [
            "Write `_brackets(g)` and `_bisect(g, lo, hi)` first — every structural method is then three lines on top of `_roots_of(g)`.",
            "`self.derivative` and `self.second_derivative` are bound methods, so you can pass them straight into `_roots_of` as the callable `g`.",
            "`round(x, 9) + 0.0` deduplicates and kills `-0.0`; `sorted(set(...))` then finishes the job.",
            "Format with a helper that snaps anything below `5e-10` to `0.0`, otherwise a root at zero prints as `-0.000000`.",
        ],
        "files": [
            {"name": "analyser.py", "content": r'''
import math

CLASSIFY_TOL = 1e-5


class FunctionAnalyser:
    """Numerical shape analysis of one real function on a closed interval."""

    def __init__(self, f, a, b, samples=400):
        # validate, then store f, a, b, samples and the grid step
        pass

    def derivative(self, x, h=1e-6):
        pass

    def second_derivative(self, x, h=1e-4):
        pass

    def roots(self):
        pass

    def critical_points(self):
        pass

    def inflection_points(self):
        pass

    def monotonic_intervals(self):
        pass

    def extrema(self):
        pass

    def report(self):
        pass
'''},
            {"name": "main.py", "content": r'''
from analyser import FunctionAnalyser

cubic = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
print(cubic.report())
print()

box = FunctionAnalyser(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0)
print(box.report())
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "analyser.py", "content": r'''
import math

CLASSIFY_TOL = 1e-5


def _fmt(value):
    """Six decimals, with anything within half an ulp of zero snapped to 0.0."""
    return f"{0.0 if abs(value) < 5e-10 else value:.6f}"


def _join(values):
    return ", ".join(_fmt(v) for v in values) if values else "none"


def _join_intervals(items):
    if not items:
        return "none"
    return ", ".join(f"[{_fmt(lo)}, {_fmt(hi)}]" for lo, hi, _ in items)


class FunctionAnalyser:
    """Numerical shape analysis of one real function on a closed interval.

    The search is grid based: features narrower than one grid step are
    invisible, and a double root where f touches zero without crossing is only
    reported when a sample happens to land on it exactly. Raise the sample
    count when that matters.
    """

    def __init__(self, f, a, b, samples=400):
        if not callable(f):
            raise ValueError("f must be callable")
        if not a < b:
            raise ValueError("need a < b")
        if samples < 2:
            raise ValueError("samples must be at least 2")
        self.f = f
        self.a = float(a)
        self.b = float(b)
        self.samples = int(samples)
        self.step = (self.b - self.a) / self.samples

    # ------------------------------------------------------------- primitives
    def derivative(self, x, h=1e-6):
        """Central difference with a step scaled by max(1, |x|)."""
        step = h * max(1.0, abs(x))
        return (self.f(x + step) - self.f(x - step)) / (2 * step)

    def second_derivative(self, x, h=1e-4):
        """Second-order central difference, same relative step."""
        step = h * max(1.0, abs(x))
        return (self.f(x + step) - 2 * self.f(x) + self.f(x - step)) / (step * step)

    # ------------------------------------------------------------- machinery
    def _brackets(self, g):
        """Sign-change brackets of g on the grid; exact zeros give (x, x)."""
        xs = [self.a + self.step * k for k in range(self.samples + 1)]
        vals = [g(x) for x in xs]
        out = []
        for i in range(self.samples):
            if vals[i] == 0.0:
                out.append((xs[i], xs[i]))
            elif vals[i] * vals[i + 1] < 0.0:
                out.append((xs[i], xs[i + 1]))
        if vals[self.samples] == 0.0:
            out.append((xs[self.samples], xs[self.samples]))
        return out

    @staticmethod
    def _bisect(g, lo, hi, tol=1e-12, max_iter=200):
        """Capped bisection. A degenerate bracket returns its own point."""
        if lo == hi:
            return lo
        g_lo, g_hi = g(lo), g(hi)
        if g_lo * g_hi > 0.0:
            raise ValueError("g does not change sign across the bracket")
        for _ in range(max_iter):
            if hi - lo <= tol:
                break
            mid = 0.5 * (lo + hi)
            g_mid = g(mid)
            if g_mid == 0.0:
                return mid
            if g_lo * g_mid < 0.0:
                hi, g_hi = mid, g_mid
            else:
                lo, g_lo = mid, g_mid
        return 0.5 * (lo + hi)

    def _roots_of(self, g):
        """Every zero of g on the grid, rounded to 9 decimals and deduplicated."""
        found = [round(self._bisect(g, lo, hi), 9) + 0.0
                 for lo, hi in self._brackets(g)]
        return sorted(set(found))

    # ------------------------------------------------------------- structure
    def roots(self):
        """Sorted zeros of f on [a, b]."""
        return self._roots_of(self.f)

    def critical_points(self):
        """Sorted (x, kind) pairs from the zeros of the derivative."""
        return [(x, self._classify(x)) for x in self._roots_of(self.derivative)]

    def _classify(self, x):
        """Second derivative test, falling back to the first derivative test."""
        d2 = self.second_derivative(x)
        if d2 > CLASSIFY_TOL:
            return "minimum"
        if d2 < -CLASSIFY_TOL:
            return "maximum"
        left = self.derivative(x - self.step)
        right = self.derivative(x + self.step)
        if left < 0.0 < right:
            return "minimum"
        if left > 0.0 > right:
            return "maximum"
        return "inflection"

    def inflection_points(self):
        """Zeros of f'' that are genuine sign changes, not mere touches."""
        keep = []
        for x in self._roots_of(self.second_derivative):
            left = self.second_derivative(x - self.step)
            right = self.second_derivative(x + self.step)
            if left * right < 0.0:
                keep.append(x)
        return keep

    def monotonic_intervals(self):
        """(lo, hi, label) pieces cut at the critical points."""
        cuts = sorted(set([self.a, self.b]
                          + [x for x, _ in self.critical_points()]))
        out = []
        for lo, hi in zip(cuts, cuts[1:]):
            slope = self.derivative(0.5 * (lo + hi))
            if slope > 0.0:
                label = "increasing"
            elif slope < 0.0:
                label = "decreasing"
            else:
                label = "constant"
            out.append((lo, hi, label))
        return out

    def extrema(self):
        """Global min and max over endpoints and critical points."""
        xs = sorted(set([self.a, self.b]
                        + [x for x, _ in self.critical_points()]))
        pairs = [(x, self.f(x)) for x in xs]
        lowest = min(pairs, key=lambda pair: (pair[1], pair[0]))
        highest = max(pairs, key=lambda pair: (pair[1], -pair[0]))
        return {"min": lowest, "max": highest}

    # ------------------------------------------------------------- reporting
    def report(self):
        """A nine-line human-readable summary of everything above."""
        crit = self.critical_points()
        mono = self.monotonic_intervals()
        ext = self.extrema()
        lines = [
            f"interval: [{_fmt(self.a)}, {_fmt(self.b)}]",
            "roots: " + _join(self.roots()),
            "minima: " + _join([x for x, kind in crit if kind == "minimum"]),
            "maxima: " + _join([x for x, kind in crit if kind == "maximum"]),
            "inflections: " + _join(self.inflection_points()),
            "increasing: " + _join_intervals([i for i in mono if i[2] == "increasing"]),
            "decreasing: " + _join_intervals([i for i in mono if i[2] == "decreasing"]),
            f"global min: f({_fmt(ext['min'][0])}) = {_fmt(ext['min'][1])}",
            f"global max: f({_fmt(ext['max'][0])}) = {_fmt(ext['max'][1])}",
        ]
        return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from analyser import FunctionAnalyser

cubic = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
print(cubic.report())
print()

box = FunctionAnalyser(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0)
print(box.report())
print()
print("largest box:", box.extrema()["max"])
'''},
        ],
        "tests": [
            {"name": "The constructor validates its interval", "code": r'''
from analyser import FunctionAnalyser
for _args in [(None, 0.0, 1.0), (lambda x: x, 1.0, 1.0), (lambda x: x, 2.0, 1.0),
              (lambda x: x, 0.0, 1.0, 1), (lambda x: x, 0.0, 1.0, 0)]:
    try:
        FunctionAnalyser(*_args)
        assert False, f"FunctionAnalyser{_args!r} should raise ValueError"
    except ValueError:
        pass
_fa = FunctionAnalyser(lambda x: x, 0.0, 4.0, samples=8)
assert abs(_fa.step - 0.5) < 1e-12, f"step is {_fa.step!r}, expected 0.5"
'''},
            {"name": "The numerical primitives are accurate", "code": r'''
import math as _math
from analyser import FunctionAnalyser
_fa = FunctionAnalyser(_math.sin, 0.0, 6.0)
assert abs(_fa.derivative(1.0) - _math.cos(1.0)) < 1e-8, f"f'(1) gave {_fa.derivative(1.0)!r}"
assert abs(_fa.second_derivative(1.0) + _math.sin(1.0)) < 1e-6, \
    f"f''(1) gave {_fa.second_derivative(1.0)!r}, expected {-_math.sin(1.0)!r}"
_q = FunctionAnalyser(lambda x: 5 * x * x, -1.0, 1.0)
assert abs(_q.second_derivative(0.3) - 10.0) < 1e-5, f"f'' of 5x^2 is 10, got {_q.second_derivative(0.3)!r}"
'''},
            {"name": "roots of a cubic, and a function with none", "code": r'''
import math as _math
from analyser import FunctionAnalyser
_r = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).roots()
assert len(_r) == 3, f"x^3-3x has three roots on [-3,3], got {_r!r}"
for _got, _want in zip(_r, [-_math.sqrt(3), 0.0, _math.sqrt(3)]):
    assert abs(_got - _want) < 1e-6, f"root {_got!r}, expected {_want!r}"
assert FunctionAnalyser(lambda x: x * x + 1, -2.0, 2.0).roots() == [], \
    "x^2+1 has no real root, so the list is empty"
'''},
            {"name": "critical_points classifies a cubic and a double well", "code": r'''
from analyser import FunctionAnalyser
_cp = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).critical_points()
assert len(_cp) == 2, f"Expected two critical points, got {_cp!r}"
assert abs(_cp[0][0] + 1.0) < 1e-6 and _cp[0][1] == "maximum", f"Got {_cp[0]!r}"
assert abs(_cp[1][0] - 1.0) < 1e-6 and _cp[1][1] == "minimum", f"Got {_cp[1]!r}"
_cp = FunctionAnalyser(lambda x: x ** 4 - 2 * x * x, -2.0, 2.0).critical_points()
assert [k for _, k in _cp] == ["minimum", "maximum", "minimum"], f"Got {_cp!r}"
'''},
            {"name": "The first derivative fallback still decides", "code": r'''
from analyser import FunctionAnalyser
_cp = FunctionAnalyser(lambda x: x ** 4, -1.0, 1.0).critical_points()
assert len(_cp) == 1 and abs(_cp[0][0]) < 1e-6, f"Got {_cp!r}"
assert _cp[0][1] == "minimum", \
    "f''(0) is zero for x^4, so the first derivative test must call it a minimum"
'''},
            {"name": "inflection_points needs a real sign change", "code": r'''
from analyser import FunctionAnalyser
_i = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).inflection_points()
assert len(_i) == 1 and abs(_i[0]) < 1e-6, f"x^3-3x inflects only at 0, got {_i!r}"
assert FunctionAnalyser(lambda x: x ** 4, -1.0, 1.0).inflection_points() == [], \
    "f'' of x^4 touches zero at 0 without crossing, so it is not an inflection"
assert FunctionAnalyser(lambda x: x * x, -2.0, 2.0).inflection_points() == [], \
    "A parabola has no inflection point"
'''},
            {"name": "monotonic_intervals cuts at the critical points", "code": r'''
from analyser import FunctionAnalyser
_m = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).monotonic_intervals()
assert len(_m) == 3, f"Two critical points cut [-3,3] into three pieces, got {_m!r}"
assert [t[2] for t in _m] == ["increasing", "decreasing", "increasing"], f"Got {_m!r}"
assert abs(_m[0][0] + 3.0) < 1e-9 and abs(_m[-1][1] - 3.0) < 1e-9, \
    f"The pieces must span the whole interval, got {_m!r}"
assert abs(_m[0][1] + 1.0) < 1e-6 and abs(_m[1][1] - 1.0) < 1e-6, f"Got {_m!r}"
'''},
            {"name": "monotonic_intervals on a function with no critical point", "code": r'''
from analyser import FunctionAnalyser
_m = FunctionAnalyser(lambda x: 2 * x + 1, 0.0, 1.0).monotonic_intervals()
assert len(_m) == 1, f"A straight line gives one piece, got {_m!r}"
assert _m[0][2] == "increasing", f"Got {_m[0]!r}"
'''},
            {"name": "extrema weighs endpoints against interior points", "code": r'''
from analyser import FunctionAnalyser
_e = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).extrema()
assert abs(_e["min"][0] + 3.0) < 1e-9 and abs(_e["min"][1] + 18.0) < 1e-6, f"Got {_e['min']!r}"
assert abs(_e["max"][0] - 3.0) < 1e-9 and abs(_e["max"][1] - 18.0) < 1e-6, f"Got {_e['max']!r}"
_box = FunctionAnalyser(lambda x: x * (30 - 2 * x) * (16 - 2 * x), 0.0, 8.0)
_e = _box.extrema()
assert abs(_e["max"][0] - 10.0 / 3.0) < 1e-6, f"The box is largest at 10/3, got {_e['max'][0]!r}"
assert abs(_e["max"][1] - 19600.0 / 27.0) < 1e-4, f"Got {_e['max'][1]!r}"
assert _e["min"] == (0.0, 0.0), f"Ties keep the smaller x, so (0.0, 0.0) — got {_e['min']!r}"
'''},
            {"name": "Two analysers share nothing", "code": r'''
from analyser import FunctionAnalyser
_a = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0)
_b = FunctionAnalyser(lambda x: x * x + 1, -2.0, 2.0)
_a.roots()
assert _b.roots() == [], "The second analyser must not see the first one's results"
assert len(_a.roots()) == 3, "And the first must be unchanged by the second"
'''},
            {"name": "report has nine labelled lines", "code": r'''
from analyser import FunctionAnalyser
_rep = FunctionAnalyser(lambda x: x ** 3 - 3 * x, -3.0, 3.0).report()
assert isinstance(_rep, str), "report() returns a string, it does not print"
_lines = _rep.strip().split("\n")
assert len(_lines) == 9, f"Expected nine lines, got {len(_lines)}: {_lines!r}"
_labels = ["interval:", "roots:", "minima:", "maxima:", "inflections:",
           "increasing:", "decreasing:", "global min:", "global max:"]
for _line, _label in zip(_lines, _labels):
    assert _line.startswith(_label), f"Expected a line starting {_label!r}, got {_line!r}"
assert "-18.000000" in _lines[7], f"Global minimum line was {_lines[7]!r}"
assert "18.000000" in _lines[8], f"Global maximum line was {_lines[8]!r}"
'''},
            {"name": "An empty list is written as none", "code": r'''
from analyser import FunctionAnalyser
_rep = FunctionAnalyser(lambda x: x * x + 1, -2.0, 2.0).report()
_lines = _rep.strip().split("\n")
assert _lines[1] == "roots: none", f"No roots, so the line reads 'roots: none' — got {_lines[1]!r}"
assert _lines[4] == "inflections: none", f"Got {_lines[4]!r}"
'''},
            {"name": "analyser.py is import-clean", "code": r'''
_src = open("analyser.py").read()
assert "print(" not in _src, "analyser.py defines the class; the printing belongs in main.py"
assert "class FunctionAnalyser" in _src, "The class must live in analyser.py"
'''},
        ],
    },
}
