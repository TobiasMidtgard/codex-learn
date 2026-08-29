"""SE201 — Software Engineering Principles. Author module."""

COURSE = {
    "id": "SE201",
    "title": "Software Engineering Principles",
    "year": 2,
    "level": "Intermediate",
    "prereqs": ["CS102"],
    "stack": ["Python", "Git", "pytest"],
    "credits": 10,
    "hours": 130,
    "icon": "⚒",
    "summary": (
        "Programs are written once and read for years, so this course is about the "
        "practices that keep a codebase changeable: pinning a vague requirement down "
        "into executable examples, refactoring behind a characterisation harness, "
        "applying the handful of design patterns that actually earn their keep, and "
        "automating the quality gates that stop a team drifting. Everything is built "
        "test-first and every claim about the code is checked by a machine."
    ),
    "outcomes": [
        "Translate an ambiguous requirement into a decision table of executable examples",
        "Write characterisation tests that pin down legacy behaviour before touching it",
        "Refactor with extract-method and guard clauses while proving behaviour is unchanged",
        "Apply strategy, observer and factory to remove conditionals and hard-wired coupling",
        "Measure cyclomatic complexity from an abstract syntax tree and gate on it",
        "Derive the required semantic-version bump from a diff of two API surfaces",
        "Design a layered service with an append-only event log that can rebuild its own state",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed. (Addison-Wesley, 2018) — chapters 1-3, 6",
        "Gamma, Helm, Johnson & Vlissides, *Design Patterns* (Addison-Wesley, 1994) — Strategy, Observer, Abstract Factory",
        "Preston-Werner, *Semantic Versioning 2.0.0*, semver.org",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Requirements, specification and executable examples",
            "summary": "Turning a sentence a stakeholder said into examples a machine can check.",
            "concepts": [
                "Ambiguity taxonomy: boundaries ('over £100'), ordering, rounding, and units",
                "A specification is only unambiguous once every boundary has an example on both sides",
                "Decision tables: enumerate the conditions, then the expected outcome of each combination",
                "Boundary-value analysis and equivalence partitioning as test-selection strategies",
                "Money is not a float problem — it is a rounding-policy problem (half-up vs banker's)",
                "Acceptance criteria belong to the requirement, not to the implementation that satisfies it",
                "Circular tests: an expected value computed by the code under test proves nothing",
            ],
            "lab": {
                "title": "From an ambiguous rule to an executable specification",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
A product owner writes:

> *"Give customers 10% off big orders. Members get a further 5%. Shipping is
> free on larger orders, and express delivery costs extra."*

Every noun in that sentence hides a decision. The team has resolved them, and
the result is the specification below. Implement it, then **write the examples
that prove it** — including examples on both sides of every boundary.

## The resolved specification

1. `round_money(value)` returns `value` rounded to two decimals using
   **half-up** rounding, as a float. Python's built-in `round` uses banker's
   rounding (`round(2.675, 2)` is `2.67`), which is wrong for money: the spec
   requires `2.68`. Use `decimal.Decimal(str(value))` and
   `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.

2. `order_total(subtotal, member=False, express=False)`:
   - a negative `subtotal` raises `ValueError`;
   - **volume discount** — when `subtotal` is *strictly greater* than `100`,
     multiply by `0.90`; at exactly `100` there is no discount;
   - **member discount** — members then get a further `0.95` multiplier,
     applied to the already-discounted amount, not to the original;
   - **shipping** — `4.99`, but free when the *pre-discount* `subtotal` is
     `50` or more; express delivery adds `9.99` on top in every case;
   - the total is `round_money(discounted + shipping)`.

```text
order_total(49.99)                  ->  54.98
order_total(50.0)                   ->  50.0
order_total(100.0)                  -> 100.0
order_total(100.01)                 ->  90.01
order_total(200.0, member=True)     -> 171.0
order_total(49.99, True, True)      ->  62.47
```

3. `spec_cases()` returns a list of `(subtotal, member, express, expected)`
   tuples — your executable specification. It must contain at least eight
   cases and must straddle **both** boundaries (below and at/above 50, and at
   or below 100 as well as above 100), with both values of `member` and both
   values of `express` represented.

**Work out each `expected` on paper.** A case whose expected value is produced
by calling `order_total` tests nothing at all, and the checks reject it.
''',
                "files": [{"name": "main.py", "content": r'''
from decimal import Decimal, ROUND_HALF_UP


def round_money(value):
    """Round to 2 decimals, half away from zero, returned as a float."""
    # your code here


def order_total(subtotal, member=False, express=False):
    """The payable total for one order, following the resolved specification."""
    # your code here


def spec_cases():
    """The executable specification: (subtotal, member, express, expected) tuples.

    Every expected value must be worked out by hand, never by calling the
    function under test.
    """
    # your code here


for case in spec_cases() or []:
    print(case)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
from decimal import Decimal, ROUND_HALF_UP


def round_money(value):
    """Round to 2 decimals, half away from zero, returned as a float."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def order_total(subtotal, member=False, express=False):
    """The payable total for one order, following the resolved specification."""
    if subtotal < 0:
        raise ValueError("subtotal must not be negative")
    amount = subtotal * 0.90 if subtotal > 100 else float(subtotal)
    if member:
        amount = amount * 0.95
    shipping = 0.0 if subtotal >= 50 else 4.99
    if express:
        shipping = shipping + 9.99
    return round_money(amount + shipping)


def spec_cases():
    """The executable specification: (subtotal, member, express, expected) tuples."""
    return [
        (0.0, False, False, 4.99),
        (49.99, False, False, 54.98),
        (50.0, False, False, 50.0),
        (50.0, True, False, 47.5),
        (100.0, False, False, 100.0),
        (100.0, True, False, 95.0),
        (100.01, False, False, 90.01),
        (120.0, False, False, 108.0),
        (200.0, True, False, 171.0),
        (500.0, False, True, 459.99),
        (49.99, True, True, 62.47),
        (0.0, True, True, 14.98),
    ]


for case in spec_cases() or []:
    print(case)
'''}],
                "hints": [
                    "`Decimal(str(value))` is the important detail — `Decimal(2.675)` picks up the float's error and rounds down again.",
                    "Apply the multipliers in the order the spec lists them: volume first, then member, and only then add shipping.",
                    "Both shipping decisions look at the *original* subtotal, so compute shipping before you overwrite the amount.",
                    "For `spec_cases`, take the six worked examples in the brief and add cases for the combinations they do not cover.",
                ],
                "tests": [
                    {"name": "round_money rounds half up, not to even", "code": r'''
for _v, _want in [(2.675, 2.68), (0.125, 0.13), (1.005, 1.01), (10, 10.0), (2.674, 2.67)]:
    _got = round_money(_v)
    assert abs(_got - _want) < 1e-9, f"round_money({_v}) gave {_got!r}, expected {_want}"
assert round(2.675, 2) == 2.67, "built-in round is banker's rounding — that is the point of the exercise"
'''},
                    {"name": "Worked examples from the brief", "code": r'''
for _args, _want in [((49.99,), 54.98), ((50.0,), 50.0), ((100.0,), 100.0),
                     ((100.01,), 90.01), ((200.0, True), 171.0), ((49.99, True, True), 62.47)]:
    _got = order_total(*_args)
    assert abs(_got - _want) < 1e-9, f"order_total{_args!r} gave {_got!r}, expected {_want}"
'''},
                    {"name": "Boundaries are strict where the spec says so", "code": r'''
assert abs(order_total(100.0) - 100.0) < 1e-9, "at exactly 100 there is no volume discount"
assert abs(order_total(50.0) - 50.0) < 1e-9, "at exactly 50 shipping is already free"
assert abs(order_total(49.99) - 54.98) < 1e-9, "just below 50 the 4.99 shipping applies"
assert abs(order_total(0.0, False, True) - 14.98) < 1e-9, "express adds 9.99 on top of paid shipping"
'''},
                    {"name": "Member discount compounds on the discounted amount", "code": r'''
_got = order_total(200.0, member=True)
assert abs(_got - 171.0) < 1e-9, f"order_total(200, member=True) gave {_got!r}; 200*0.9*0.95 is 171.0"
assert abs(order_total(100.0, member=True) - 95.0) < 1e-9, "a member below the volume boundary still gets 5%"
'''},
                    {"name": "A negative subtotal is refused", "code": r'''
for _bad in (-0.01, -1, -250.0):
    try:
        order_total(_bad)
        assert False, f"order_total({_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "spec_cases straddles every boundary", "code": r'''
_cases = spec_cases()
assert isinstance(_cases, (list, tuple)) and len(_cases) >= 8, \
    f"spec_cases returned {len(_cases) if _cases else 0} cases, at least 8 are needed"
for _c in _cases:
    assert len(_c) == 4, f"each case is (subtotal, member, express, expected), got {_c!r}"
_subs = [_c[0] for _c in _cases]
assert any(_s < 50 for _s in _subs), "no case below the free-shipping boundary"
assert any(_s >= 50 for _s in _subs), "no case at or above the free-shipping boundary"
assert any(_s <= 100 for _s in _subs), "no case at or below the volume boundary"
assert any(_s > 100 for _s in _subs), "no case above the volume boundary"
assert {bool(_c[1]) for _c in _cases} == {True, False}, "both member values must appear"
assert {bool(_c[2]) for _c in _cases} == {True, False}, "both express values must appear"
'''},
                    {"name": "Every declared expectation holds, and none is circular", "code": r'''
for _s, _m, _e, _want in spec_cases():
    _got = order_total(_s, _m, _e)
    assert abs(_got - _want) < 1e-9, \
        f"spec_cases claims order_total({_s}, {_m}, {_e}) == {_want}, but it gave {_got!r}"
_src = open("main.py").read()
_start = _src.index("def spec_cases")
_rest = _src[_start:]
_cut = _rest.find("\ndef ", 1)
_body = _rest if _cut == -1 else _rest[:_cut]
assert "order_total" not in _body, \
    "spec_cases must state expected values as literals — calling order_total makes the check circular"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Refactoring under a safety net",
            "summary": "Characterise what the legacy code does, then change its shape without changing that.",
            "concepts": [
                "Refactoring is a behaviour-preserving transformation — anything else is a rewrite",
                "Characterisation (golden-master) tests record current behaviour, bugs included",
                "Legacy code is code without tests, regardless of its age",
                "Extract method: give a named concept a name, and the nesting collapses",
                "Guard clauses replace an arrow-shaped nest of ifs with early returns",
                "Replace nested conditional with a lookup table when the branches are data",
                "Small steps: run the safety net after every single move, never at the end",
            ],
            "lab": {
                "title": "Untangling a shipping quote",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
`legacy.py` holds `legacy_quote(weight, distance, fragile, priority)`, six
levels deep and untouched since the person who wrote it left. It returns
`(rate, band)` where `rate` is rounded to two decimals, or `None` for input it
refuses. You may **read** it but not edit it.

Work in `refactored.py`, in this order.

## 1. Build the safety net

`characterisation_suite()` returns a list of `(args, expected)` pairs, where
`expected` is whatever `legacy_quote(*args)` returns **today**. Sweep a grid
that crosses every boundary in the legacy code: weights either side of 1, 5
and 20, distances either side of 100 and 500, both values of `fragile`, all
three valid priorities plus one invalid one, and non-positive weights and
distances. At least 100 pairs.

## 2. Extract the concepts

Then implement these, each one flat and separately testable:

| function | meaning |
| --- | --- |
| `base_rate(weight)` | the weight band charge, before anything else |
| `distance_surcharge(distance)` | the extra the distance adds, `0.0` under 100 km |
| `fragile_multiplier(weight, fragile)` | `1.0`, `1.15` or `1.25` |
| `priority_adjust(rate, priority)` | the priority uplift applied to a rate |
| `band_for(rate)` | `"A"`, `"B"`, `"C"` or `"D"` from the **unrounded** rate |
| `shipping_quote(w, d, fragile, priority)` | the whole thing, as a guard-clause function |

Read the exact constants out of `legacy.py` — that is the specification now.
`shipping_quote` must open with guard clauses returning `None` for a
non-positive weight, a non-positive distance, or an unknown priority, and the
body that follows must be flat: at most two levels of nesting anywhere in the
file, and at most eight statements in `shipping_quote` itself.

Behaviour must be identical for every pair in the safety net.
''',
                "files": [
                    {"name": "legacy.py", "ro": True, "content": r'''
def legacy_quote(weight, distance, fragile, priority):
    if weight > 0:
        if distance > 0:
            if priority == "standard" or priority == "two-day" or priority == "next-day":
                if weight < 1:
                    rate = 4.0
                else:
                    if weight < 5:
                        rate = 4.0 + (weight - 1) * 1.5
                    else:
                        if weight < 20:
                            rate = 10.0 + (weight - 5) * 1.1
                        else:
                            rate = 26.5 + (weight - 20) * 0.8
                if distance > 100:
                    if distance > 500:
                        rate = rate + 12.0 + (distance - 500) * 0.02
                    else:
                        rate = rate + (distance - 100) * 0.03
                if fragile:
                    if weight >= 5:
                        rate = rate * 1.25
                    else:
                        rate = rate * 1.15
                if priority == "next-day":
                    rate = rate * 1.6 + 3.0
                else:
                    if priority == "two-day":
                        rate = rate * 1.25
                if rate < 10.0:
                    band = "A"
                else:
                    if rate < 25.0:
                        band = "B"
                    else:
                        if rate < 60.0:
                            band = "C"
                        else:
                            band = "D"
                return (round(rate, 2), band)
            else:
                return None
        else:
            return None
    else:
        return None
'''},
                    {"name": "refactored.py", "content": r'''
import itertools

from legacy import legacy_quote

PRIORITIES = ("standard", "two-day", "next-day")


def characterisation_suite():
    """[(args, expected)] recording what legacy_quote does today."""
    # sweep a grid across every boundary, and record legacy_quote(*args)


def base_rate(weight):
    """The weight-band charge before distance, fragility and priority."""
    # your code here


def distance_surcharge(distance):
    """What the distance adds to the rate."""
    # your code here


def fragile_multiplier(weight, fragile):
    """1.0 when it is not fragile, otherwise the weight-dependent uplift."""
    # your code here


def priority_adjust(rate, priority):
    """The rate after the priority uplift."""
    # your code here


def band_for(rate):
    """A, B, C or D for an unrounded rate."""
    # your code here


def shipping_quote(weight, distance, fragile, priority):
    """(rounded rate, band), or None. Guard clauses first, then flat arithmetic."""
    # your code here
'''},
                    {"name": "main.py", "content": r'''
from legacy import legacy_quote
from refactored import shipping_quote

for args in [(0.5, 50, False, "standard"), (12.0, 800, True, "next-day"),
             (2.5, 300, False, "two-day"), (0.0, 10, False, "standard")]:
    print(args, legacy_quote(*args), shipping_quote(*args))
'''},
                ],
                "main": "main.py",
                "solution": [
                    {"name": "refactored.py", "content": r'''
import itertools

from legacy import legacy_quote

PRIORITIES = ("standard", "two-day", "next-day")

GRID_WEIGHTS = (-3.0, 0.0, 0.5, 1.0, 2.5, 5.0, 12.0, 20.0, 35.0)
GRID_DISTANCES = (-5, 0, 1, 100, 101, 500, 501, 1200)
GRID_PRIORITIES = ("standard", "two-day", "next-day", "same-hour")


def characterisation_suite():
    """[(args, expected)] recording what legacy_quote does today."""
    cases = []
    for args in itertools.product(GRID_WEIGHTS, GRID_DISTANCES,
                                  (False, True), GRID_PRIORITIES):
        cases.append((args, legacy_quote(*args)))
    return cases


def base_rate(weight):
    """The weight-band charge before distance, fragility and priority."""
    if weight < 1:
        return 4.0
    if weight < 5:
        return 4.0 + (weight - 1) * 1.5
    if weight < 20:
        return 10.0 + (weight - 5) * 1.1
    return 26.5 + (weight - 20) * 0.8


def distance_surcharge(distance):
    """What the distance adds to the rate."""
    if distance > 500:
        return 12.0 + (distance - 500) * 0.02
    if distance > 100:
        return (distance - 100) * 0.03
    return 0.0


def fragile_multiplier(weight, fragile):
    """1.0 when it is not fragile, otherwise the weight-dependent uplift."""
    if not fragile:
        return 1.0
    return 1.25 if weight >= 5 else 1.15


def priority_adjust(rate, priority):
    """The rate after the priority uplift."""
    if priority == "next-day":
        return rate * 1.6 + 3.0
    if priority == "two-day":
        return rate * 1.25
    return rate


def band_for(rate):
    """A, B, C or D for an unrounded rate."""
    if rate < 10.0:
        return "A"
    if rate < 25.0:
        return "B"
    if rate < 60.0:
        return "C"
    return "D"


def shipping_quote(weight, distance, fragile, priority):
    """(rounded rate, band), or None. Guard clauses first, then flat arithmetic."""
    if weight <= 0 or distance <= 0 or priority not in PRIORITIES:
        return None
    rate = base_rate(weight) + distance_surcharge(distance)
    rate = rate * fragile_multiplier(weight, fragile)
    rate = priority_adjust(rate, priority)
    return (round(rate, 2), band_for(rate))
'''},
                    {"name": "main.py", "content": r'''
from legacy import legacy_quote
from refactored import characterisation_suite, shipping_quote

suite = characterisation_suite()
print("safety net:", len(suite), "cases")
print("mismatches:", sum(1 for args, expected in suite if shipping_quote(*args) != expected))

for args in [(0.5, 50, False, "standard"), (12.0, 800, True, "next-day"),
             (2.5, 300, False, "two-day"), (0.0, 10, False, "standard")]:
    print(args, legacy_quote(*args), shipping_quote(*args))
'''},
                ],
                "hints": [
                    "Build the safety net before you write a single line of the replacement — it is the only evidence you have that nothing broke.",
                    "`itertools.product(weights, distances, (False, True), priorities)` gives the whole grid without four nested loops.",
                    "A guard clause is an early `return`: handle every refusal at the top, and the happy path stops being indented at all.",
                    "The bands read as a ladder of `if rate < ...: return ...` — each `return` makes the next `else` unnecessary.",
                ],
                "tests": [
                    {"name": "The safety net is broad and truthful", "code": r'''
from legacy import legacy_quote
from refactored import characterisation_suite
_suite = characterisation_suite()
assert isinstance(_suite, (list, tuple)) and len(_suite) >= 100, \
    f"characterisation_suite has {len(_suite) if _suite else 0} pairs, at least 100 are needed"
for _args, _expected in _suite:
    _actual = legacy_quote(*_args)
    assert _actual == _expected, \
        f"the net claims legacy_quote{_args!r} == {_expected!r}, but it returns {_actual!r}"
'''},
                    {"name": "The net crosses every boundary", "code": r'''
from refactored import characterisation_suite
_suite = characterisation_suite()
_bands = {e[1] for a, e in _suite if e is not None}
assert _bands == {"A", "B", "C", "D"}, f"the net only reaches bands {sorted(_bands)}"
assert any(e is None for a, e in _suite), "the net never exercises the refusal path"
_weights = {a[0] for a, e in _suite}
assert any(w < 1 for w in _weights) and any(1 <= w < 5 for w in _weights) \
   and any(5 <= w < 20 for w in _weights) and any(w >= 20 for w in _weights), \
    f"the weight grid misses a band: {sorted(_weights)}"
_dists = {a[1] for a, e in _suite}
assert any(0 < d <= 100 for d in _dists) and any(100 < d <= 500 for d in _dists) \
   and any(d > 500 for d in _dists), f"the distance grid misses a band: {sorted(_dists)}"
'''},
                    {"name": "Extracted helpers agree with the legacy constants", "code": r'''
from refactored import base_rate, band_for, distance_surcharge, fragile_multiplier, priority_adjust
for _w, _want in [(0.5, 4.0), (1.0, 4.0), (2.5, 6.25), (5.0, 10.0), (12.0, 17.7), (20.0, 26.5), (35.0, 38.5)]:
    _got = base_rate(_w)
    assert abs(_got - _want) < 1e-9, f"base_rate({_w}) gave {_got!r}, expected {_want}"
for _d, _want in [(1, 0.0), (100, 0.0), (101, 0.03), (500, 12.0), (501, 12.02), (1200, 26.0)]:
    _got = distance_surcharge(_d)
    assert abs(_got - _want) < 1e-9, f"distance_surcharge({_d}) gave {_got!r}, expected {_want}"
assert fragile_multiplier(12.0, False) == 1.0, "not fragile means no uplift"
assert abs(fragile_multiplier(4.9, True) - 1.15) < 1e-9, "under 5 kg the fragile uplift is 1.15"
assert abs(fragile_multiplier(5.0, True) - 1.25) < 1e-9, "from 5 kg the fragile uplift is 1.25"
for _p, _want in [("standard", 10.0), ("two-day", 12.5), ("next-day", 19.0)]:
    _got = priority_adjust(10.0, _p)
    assert abs(_got - _want) < 1e-9, f"priority_adjust(10.0, {_p!r}) gave {_got!r}, expected {_want}"
for _r, _want in [(9.99, "A"), (10.0, "B"), (24.999, "B"), (25.0, "C"), (59.99, "C"), (60.0, "D")]:
    _got = band_for(_r)
    assert _got == _want, f"band_for({_r}) gave {_got!r}, expected {_want!r}"
'''},
                    {"name": "Behaviour is unchanged across the whole net", "code": r'''
from refactored import characterisation_suite, shipping_quote
_bad = []
for _args, _expected in characterisation_suite():
    _got = shipping_quote(*_args)
    if _expected is None or _got is None:
        _same = _got == _expected
    else:
        _same = _got[1] == _expected[1] and abs(_got[0] - _expected[0]) <= 0.011
    if not _same:
        _bad.append((_args, _expected, _got))
assert not _bad, f"{len(_bad)} case(s) changed behaviour, first: {_bad[0]!r}"
'''},
                    {"name": "The refusal path still refuses", "code": r'''
from refactored import shipping_quote
for _args in [(0, 100, False, "standard"), (-2.0, 100, False, "standard"),
              (5.0, 0, False, "standard"), (5.0, -1, True, "next-day"),
              (5.0, 100, False, "same-hour"), (5.0, 100, False, "")]:
    _got = shipping_quote(*_args)
    assert _got is None, f"shipping_quote{_args!r} gave {_got!r}, expected None"
'''},
                    {"name": "The nesting is gone", "code": r'''
import ast as _ast
_tree = _ast.parse(open("refactored.py").read())
def _depth(_node):
    _best = 0
    for _child in _ast.iter_child_nodes(_node):
        if isinstance(_child, (_ast.If, _ast.For, _ast.While, _ast.Try, _ast.With)):
            _best = max(_best, 1 + _depth(_child))
        elif isinstance(_child, (_ast.FunctionDef, _ast.ClassDef)):
            continue
        else:
            _best = max(_best, _depth(_child))
    return _best
_fns = {n.name: n for n in _tree.body if isinstance(n, _ast.FunctionDef)}
assert "shipping_quote" in _fns, "refactored.py must define shipping_quote at module level"
for _name, _node in _fns.items():
    _d = _depth(_node)
    assert _d <= 2, f"{_name} still nests {_d} levels deep — extract it further"
assert len(_fns) >= 6, f"only {len(_fns)} top-level functions — the extractions are missing"
_stmts = len(_fns["shipping_quote"].body)
assert _stmts <= 8, f"shipping_quote has {_stmts} top-level statements, at most 8 are allowed"
'''},
                    {"name": "legacy.py was not edited", "code": r'''
_src = open("legacy.py").read()
assert "def legacy_quote(weight, distance, fragile, priority):" in _src, \
    "legacy.py is the reference behaviour — it must stay exactly as it was"
assert _src.count("if ") >= 12, "legacy.py has been rewritten; restore it and refactor in refactored.py"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Design patterns that earn their keep",
            "summary": "Strategy, observer and factory, in one pricing and notification pipeline.",
            "concepts": [
                "Programme to an interface: `abc.ABC` plus `@abstractmethod` makes the contract enforceable",
                "Strategy replaces a switch over algorithm variants with polymorphism",
                "Factory method / registry decouples 'which class' from 'where it is used'",
                "Observer inverts control: publishers know events, not subscribers",
                "Open-closed in practice: adding a pricing rule must not edit the checkout",
                "Isolating subscriber failures — one broken listener must not sink the publish",
                "Patterns are a vocabulary, not a goal; a pattern applied without a force to resolve is debt",
            ],
            "lab": {
                "title": "A pricing engine with a notification bus",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
One checkout, three patterns.

## Strategy

`PricingStrategy` is an abstract base class (`abc.ABC`) with one abstract
method `price(units)` returning a float. Instantiating it directly must raise
`TypeError`. Three concrete strategies:

- `FlatPricing(unit_price)` — `unit_price * units`.
- `TieredPricing(tiers)` where `tiers` is a list of `(threshold, unit_price)`
  ascending by threshold, starting at `0`. Pricing is **marginal**: units are
  charged at the rate of the band they fall into. With
  `[(0, 3.0), (100, 2.5), (500, 2.0)]`, 250 units cost
  `100*3.0 + 150*2.5 = 675.0`, and 600 units cost
  `100*3.0 + 400*2.5 + 100*2.0 = 1500.0`.
- `SubscriptionPricing(monthly, included, overage)` — `monthly`, plus
  `overage` for every unit beyond `included`.

Negative `units` raises `ValueError` in every strategy; zero units is legal.

## Factory

`make_strategy(spec)` builds a strategy from a plain dict:

```text
{"kind": "flat", "unit_price": 2.5}
{"kind": "tiered", "tiers": [[0, 3.0], [100, 2.5], [500, 2.0]]}
{"kind": "subscription", "monthly": 99.0, "included": 50, "overage": 1.75}
```

An unknown `kind` raises `ValueError`. New kinds must be addable by
registering into the `REGISTRY` dict, without editing `make_strategy`.

## Observer

`EventBus` with `subscribe(event, handler)`, `unsubscribe(event, handler)` and
`publish(event, payload)`. Handlers run in subscription order and receive the
payload. `publish` returns the number of handlers it invoked, and a handler
that raises must not stop the others: record `(event, handler_name, message)`
in `bus.errors` and carry on. Publishing to an event with no subscribers
returns `0`.

## Putting it together

`Checkout(strategy, bus)` with `place(order_id, units)`: it prices the order,
publishes `"order.priced"` with payload
`{"order_id": ..., "units": ..., "total": ...}`, and returns the total. It must
work with any strategy without knowing which one it holds.
''',
                "files": [{"name": "main.py", "content": r'''
import abc


class PricingStrategy(abc.ABC):
    """The strategy interface: price a number of units."""

    @abc.abstractmethod
    def price(self, units):
        """The charge for this many units."""


class FlatPricing(PricingStrategy):
    def __init__(self, unit_price):
        pass

    def price(self, units):
        pass


class TieredPricing(PricingStrategy):
    def __init__(self, tiers):
        pass

    def price(self, units):
        pass


class SubscriptionPricing(PricingStrategy):
    def __init__(self, monthly, included, overage):
        pass

    def price(self, units):
        pass


REGISTRY = {}


def make_strategy(spec):
    """Build a strategy from a plain dict spec, via REGISTRY."""
    # your code here


class EventBus:
    """A minimal observer: subscribe, unsubscribe, publish."""

    def __init__(self):
        self.errors = []

    def subscribe(self, event, handler):
        pass

    def unsubscribe(self, event, handler):
        pass

    def publish(self, event, payload):
        pass


class Checkout:
    """Prices an order with whatever strategy it was handed, then announces it."""

    def __init__(self, strategy, bus):
        pass

    def place(self, order_id, units):
        pass


bus = EventBus()
bus.subscribe("order.priced", lambda p: print("invoice for", p["order_id"], p["total"]))
checkout = Checkout(make_strategy({"kind": "flat", "unit_price": 2.5}), bus)
print(checkout.place("A-1", 40))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import abc


class PricingStrategy(abc.ABC):
    """The strategy interface: price a number of units."""

    @abc.abstractmethod
    def price(self, units):
        """The charge for this many units."""

    @staticmethod
    def check_units(units):
        """Reject a negative quantity before any arithmetic happens."""
        if units < 0:
            raise ValueError("units must not be negative")
        return units


class FlatPricing(PricingStrategy):
    """One price per unit, for ever."""

    def __init__(self, unit_price):
        self.unit_price = float(unit_price)

    def price(self, units):
        return self.unit_price * self.check_units(units)


class TieredPricing(PricingStrategy):
    """Marginal pricing: each band charges only the units that fall in it."""

    def __init__(self, tiers):
        self.tiers = sorted((int(t), float(p)) for t, p in tiers)

    def price(self, units):
        units = self.check_units(units)
        total = 0.0
        for index, (threshold, unit_price) in enumerate(self.tiers):
            if units <= threshold:
                break
            ceiling = self.tiers[index + 1][0] if index + 1 < len(self.tiers) else units
            in_band = min(units, ceiling) - threshold
            total += in_band * unit_price
        return total


class SubscriptionPricing(PricingStrategy):
    """A monthly fee that covers a quota, then per-unit overage."""

    def __init__(self, monthly, included, overage):
        self.monthly = float(monthly)
        self.included = int(included)
        self.overage = float(overage)

    def price(self, units):
        units = self.check_units(units)
        return self.monthly + max(0, units - self.included) * self.overage


REGISTRY = {
    "flat": lambda spec: FlatPricing(spec["unit_price"]),
    "tiered": lambda spec: TieredPricing(spec["tiers"]),
    "subscription": lambda spec: SubscriptionPricing(
        spec["monthly"], spec["included"], spec["overage"]),
}


def make_strategy(spec):
    """Build a strategy from a plain dict spec, via REGISTRY."""
    kind = spec.get("kind")
    if kind not in REGISTRY:
        raise ValueError("unknown pricing kind: " + repr(kind))
    return REGISTRY[kind](spec)


class EventBus:
    """A minimal observer: subscribe, unsubscribe, publish."""

    def __init__(self):
        self.errors = []
        self._handlers = {}

    def subscribe(self, event, handler):
        """Register a handler; subscription order is delivery order."""
        self._handlers.setdefault(event, []).append(handler)
        return handler

    def unsubscribe(self, event, handler):
        """Remove a handler. True when one was removed."""
        handlers = self._handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False

    def publish(self, event, payload):
        """Deliver payload to every subscriber; returns how many were invoked."""
        delivered = 0
        for handler in list(self._handlers.get(event, [])):
            delivered += 1
            try:
                handler(payload)
            except Exception as exc:
                name = getattr(handler, "__name__", repr(handler))
                self.errors.append((event, name, str(exc)))
        return delivered


class Checkout:
    """Prices an order with whatever strategy it was handed, then announces it."""

    def __init__(self, strategy, bus):
        self.strategy = strategy
        self.bus = bus

    def place(self, order_id, units):
        """Price the order, publish order.priced, return the total."""
        total = self.strategy.price(units)
        self.bus.publish("order.priced",
                         {"order_id": order_id, "units": units, "total": total})
        return total


bus = EventBus()
bus.subscribe("order.priced", lambda p: print("invoice for", p["order_id"], p["total"]))
checkout = Checkout(make_strategy({"kind": "flat", "unit_price": 2.5}), bus)
print(checkout.place("A-1", 40))
'''}],
                "hints": [
                    "`abc.ABC` plus `@abc.abstractmethod` is what makes `PricingStrategy()` raise TypeError — the base class needs no other machinery.",
                    "For the tiers, walk the bands in order and charge `min(units, next_threshold) - threshold` units at the band rate.",
                    "Keep `REGISTRY` a dict of `kind -> callable(spec)`; `make_strategy` then only looks up and calls, so a new kind never touches it.",
                    "Wrap each handler call in `try` / `except Exception` inside the publish loop, and append to `self.errors` rather than re-raising.",
                ],
                "tests": [
                    {"name": "The strategy interface is abstract", "code": r'''
try:
    PricingStrategy()
    assert False, "PricingStrategy() should raise TypeError — it has an abstract method"
except TypeError:
    pass
for _cls in (FlatPricing, TieredPricing, SubscriptionPricing):
    assert issubclass(_cls, PricingStrategy), f"{_cls.__name__} should subclass PricingStrategy"
'''},
                    {"name": "Flat and subscription pricing", "code": r'''
_flat = FlatPricing(2.5)
for _u, _want in [(0, 0.0), (1, 2.5), (40, 100.0), (1000, 2500.0)]:
    _got = _flat.price(_u)
    assert abs(_got - _want) < 1e-9, f"FlatPricing(2.5).price({_u}) gave {_got!r}, expected {_want}"
_sub = SubscriptionPricing(99.0, 50, 1.75)
for _u, _want in [(0, 99.0), (50, 99.0), (51, 100.75), (70, 134.0)]:
    _got = _sub.price(_u)
    assert abs(_got - _want) < 1e-9, f"subscription price({_u}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "Tiered pricing is marginal, not flat-per-band", "code": r'''
_tiered = TieredPricing([(0, 3.0), (100, 2.5), (500, 2.0)])
for _u, _want in [(0, 0.0), (50, 150.0), (100, 300.0), (101, 302.5),
                  (250, 675.0), (500, 1300.0), (600, 1500.0)]:
    _got = _tiered.price(_u)
    assert abs(_got - _want) < 1e-9, f"tiered price({_u}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "Negative quantities are refused everywhere", "code": r'''
for _s in [FlatPricing(2.5), TieredPricing([(0, 3.0), (100, 2.5)]),
           SubscriptionPricing(99.0, 50, 1.75)]:
    try:
        _s.price(-1)
        assert False, f"{type(_s).__name__}.price(-1) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The factory builds from specs and refuses unknown kinds", "code": r'''
_a = make_strategy({"kind": "flat", "unit_price": 2.5})
assert isinstance(_a, FlatPricing) and abs(_a.price(4) - 10.0) < 1e-9, f"flat spec built {_a!r}"
_b = make_strategy({"kind": "tiered", "tiers": [[0, 3.0], [100, 2.5], [500, 2.0]]})
assert isinstance(_b, TieredPricing) and abs(_b.price(250) - 675.0) < 1e-9, f"tiered spec built {_b!r}"
_c = make_strategy({"kind": "subscription", "monthly": 99.0, "included": 50, "overage": 1.75})
assert isinstance(_c, SubscriptionPricing) and abs(_c.price(70) - 134.0) < 1e-9, f"subscription spec built {_c!r}"
for _bad in [{"kind": "barter"}, {"kind": None}, {}]:
    try:
        make_strategy(_bad)
        assert False, f"make_strategy({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "A new kind needs no edit to make_strategy", "code": r'''
class _FreePricing(PricingStrategy):
    def price(self, units):
        return 0.0
REGISTRY["free"] = lambda spec: _FreePricing()
_f = make_strategy({"kind": "free"})
assert isinstance(_f, _FreePricing), f"registering into REGISTRY should be enough, got {_f!r}"
assert _f.price(999) == 0.0, "the registered strategy should price as written"
del REGISTRY["free"]
'''},
                    {"name": "The bus delivers in order and survives a bad handler", "code": r'''
_bus = EventBus()
_seen = []
def _first(payload):
    _seen.append(("first", payload["n"]))
def _boom(payload):
    raise RuntimeError("subscriber exploded")
def _last(payload):
    _seen.append(("last", payload["n"]))
_bus.subscribe("tick", _first)
_bus.subscribe("tick", _boom)
_bus.subscribe("tick", _last)
_count = _bus.publish("tick", {"n": 1})
assert _count == 3, f"publish returned {_count!r}, expected 3 handlers invoked"
assert _seen == [("first", 1), ("last", 1)], f"handlers ran as {_seen!r} — order matters, and _last must still run"
assert len(_bus.errors) == 1 and _bus.errors[0][0] == "tick", f"bus.errors is {_bus.errors!r}"
assert "exploded" in _bus.errors[0][2], f"the recorded message was {_bus.errors[0][2]!r}"
assert _bus.publish("nobody-listens", {}) == 0, "publishing to an empty event returns 0"
assert _bus.unsubscribe("tick", _boom) is True, "unsubscribe should report that it removed a handler"
_seen.clear()
assert _bus.publish("tick", {"n": 2}) == 2, "after unsubscribing, two handlers remain"
assert len(_bus.errors) == 1, "the removed handler must not run again"
'''},
                    {"name": "Checkout works with any strategy and announces the price", "code": r'''
_bus = EventBus()
_received = []
_bus.subscribe("order.priced", lambda p: _received.append(p))
for _spec, _units, _want in [
        ({"kind": "flat", "unit_price": 2.5}, 40, 100.0),
        ({"kind": "tiered", "tiers": [[0, 3.0], [100, 2.5], [500, 2.0]]}, 600, 1500.0),
        ({"kind": "subscription", "monthly": 99.0, "included": 50, "overage": 1.75}, 70, 134.0)]:
    _total = Checkout(make_strategy(_spec), _bus).place("O-1", _units)
    assert abs(_total - _want) < 1e-9, f"place with {_spec['kind']} gave {_total!r}, expected {_want}"
assert len(_received) == 3, f"three orders should publish three events, got {len(_received)}"
assert _received[0] == {"order_id": "O-1", "units": 40, "total": 100.0}, f"payload was {_received[0]!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Quality gates and versioning",
            "summary": "Measuring complexity from the syntax tree, and deriving the version bump from an API diff.",
            "concepts": [
                "McCabe's cyclomatic complexity: edges minus nodes plus two, counted as decision points plus one",
                "Static analysis over `ast` rather than regular expressions over text",
                "A gate is a policy with a threshold, applied automatically on every change",
                "Semantic versioning: MAJOR breaks callers, MINOR adds compatibly, PATCH fixes",
                "The public API surface is a contract; a diff of two surfaces determines the bump",
                "Widening a contract is compatible; narrowing it is not — required parameters are narrowing",
                "Gates must be explainable: report which function failed and by how much",
            ],
            "lab": {
                "title": "A complexity gate and a compatibility checker",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Two gates a CI pipeline would run on every merge request.

## Part 1 — cyclomatic complexity

`cyclomatic_complexity(source)` parses Python source with `ast` and returns
`{dotted_name: complexity}` for every `def` in it. A function starts at **1**
and gains:

- `+1` for each `if` (an `elif` is a nested `if`, so it counts by itself);
- `+1` for each `for` and each `while`;
- `+1` for each `except` handler;
- `+1` for each `assert`;
- `+1` for each conditional expression (`a if c else b`);
- `+len(values) - 1` for each boolean operation — `a and b` adds 1,
  `a or b or c` adds 2;
- `+1` for each comprehension clause, plus `+1` for each `if` inside it.

Names are dotted by their enclosing class or function: a method `dispatch` of
class `Router` is `"Router.dispatch"`, a closure `inner` inside `outer` is
`"outer.inner"`. A nested `def` gets its own entry and its nodes count **only**
towards that entry, never towards the enclosing function.

`quality_gate(source, limit)` returns the offenders — `(name, complexity)`
pairs strictly above `limit`, worst first, ties broken by name.

## Part 2 — semantic versioning over an API surface

An API surface is `{function_name: {"required": [...], "optional": [...]}}`,
where `required` is **ordered** (positional parameters) and `optional` is not.

`api_changes(old, new)` returns a sorted list of unique
`(severity, function_name, detail)` triples, sorted by
`(function_name, detail, severity)`:

| detail | severity | when |
| --- | --- | --- |
| `removed` | major | the function is gone |
| `added` | minor | the function is new |
| `required-param-removed` | major | a required parameter vanished entirely |
| `required-param-added` | major | a brand-new required parameter appeared |
| `optional-to-required` | major | an optional parameter became required |
| `optional-param-removed` | major | an optional parameter vanished entirely |
| `required-to-optional` | minor | a required parameter became optional |
| `optional-param-added` | minor | a brand-new optional parameter appeared |
| `params-reordered` | major | the surviving required parameters swapped order |

`required_bump(old, new)` is `"major"` if any change is major, else `"minor"`
if any is minor, else `"patch"`. `bump_version(version, level)` applies it to a
`"MAJOR.MINOR.PATCH"` string — a major bump zeroes minor and patch, a minor
bump zeroes patch. Anything that is not three dotted integers, and any unknown
level, raises `ValueError`.
''',
                "files": [{"name": "main.py", "content": r'''
import ast

SAMPLE = r"""
def simple(a):
    return a + 1


def guarded(a, b):
    if a is None or b is None:
        return 0
    if a > b:
        return a
    return b


class Router:
    def dispatch(self, verb, path):
        for route in self.routes:
            if route.verb == verb and route.matches(path):
                try:
                    return route.handler(path)
                except KeyError:
                    return 404
                except ValueError:
                    return 400
        return 405

    def names(self):
        return [r.name for r in self.routes if r.enabled]


def outer(xs):
    def inner(y):
        return y if y > 0 else -y
    return [inner(x) for x in xs]
"""


def cyclomatic_complexity(source):
    """dotted function name -> McCabe complexity."""
    # your code here


def quality_gate(source, limit):
    """(name, complexity) for every function above limit, worst first."""
    # your code here


def api_changes(old, new):
    """Sorted unique (severity, function, detail) triples between two surfaces."""
    # your code here


def required_bump(old, new):
    """major, minor or patch."""
    # your code here


def bump_version(version, level):
    """Apply a bump level to a MAJOR.MINOR.PATCH string."""
    # your code here


print(cyclomatic_complexity(SAMPLE))
print(quality_gate(SAMPLE, 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import ast

SAMPLE = r"""
def simple(a):
    return a + 1


def guarded(a, b):
    if a is None or b is None:
        return 0
    if a > b:
        return a
    return b


class Router:
    def dispatch(self, verb, path):
        for route in self.routes:
            if route.verb == verb and route.matches(path):
                try:
                    return route.handler(path)
                except KeyError:
                    return 404
                except ValueError:
                    return 400
        return 405

    def names(self):
        return [r.name for r in self.routes if r.enabled]


def outer(xs):
    def inner(y):
        return y if y > 0 else -y
    return [inner(x) for x in xs]
"""

DECISION_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While,
                  ast.ExceptHandler, ast.Assert, ast.IfExp)
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def _decision_points(node):
    """Decision points inside node, not descending into a nested scope."""
    total = 0
    for child in ast.iter_child_nodes(node):
        if isinstance(child, SCOPES):
            continue
        if isinstance(child, DECISION_NODES):
            total += 1
        if isinstance(child, ast.BoolOp):
            total += len(child.values) - 1
        if isinstance(child, ast.comprehension):
            total += 1 + len(child.ifs)
        total += _decision_points(child)
    return total


def cyclomatic_complexity(source):
    """dotted function name -> McCabe complexity."""
    scores = {}

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                walk(child, prefix + child.name + ".")
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                scores[name] = 1 + _decision_points(child)
                walk(child, name + ".")
            else:
                walk(child, prefix)

    walk(ast.parse(source), "")
    return scores


def quality_gate(source, limit):
    """(name, complexity) for every function above limit, worst first."""
    scores = cyclomatic_complexity(source)
    offenders = [(name, score) for name, score in scores.items() if score > limit]
    return sorted(offenders, key=lambda pair: (-pair[1], pair[0]))


def api_changes(old, new):
    """Sorted unique (severity, function, detail) triples between two surfaces."""
    changes = set()
    for name in old:
        if name not in new:
            changes.add(("major", name, "removed"))
    for name in new:
        if name not in old:
            changes.add(("minor", name, "added"))
    for name in set(old) & set(new):
        old_req = list(old[name].get("required", []))
        old_opt = list(old[name].get("optional", []))
        new_req = list(new[name].get("required", []))
        new_opt = list(new[name].get("optional", []))
        for param in old_req:
            if param in new_req:
                continue
            if param in new_opt:
                changes.add(("minor", name, "required-to-optional"))
            else:
                changes.add(("major", name, "required-param-removed"))
        for param in new_req:
            if param in old_req:
                continue
            if param in old_opt:
                changes.add(("major", name, "optional-to-required"))
            else:
                changes.add(("major", name, "required-param-added"))
        for param in old_opt:
            if param not in new_req and param not in new_opt:
                changes.add(("major", name, "optional-param-removed"))
        for param in new_opt:
            if param not in old_req and param not in old_opt:
                changes.add(("minor", name, "optional-param-added"))
        if [p for p in old_req if p in new_req] != [p for p in new_req if p in old_req]:
            changes.add(("major", name, "params-reordered"))
    return sorted(changes, key=lambda c: (c[1], c[2], c[0]))


def required_bump(old, new):
    """major, minor or patch."""
    severities = {severity for severity, _, _ in api_changes(old, new)}
    if "major" in severities:
        return "major"
    if "minor" in severities:
        return "minor"
    return "patch"


def bump_version(version, level):
    """Apply a bump level to a MAJOR.MINOR.PATCH string."""
    parts = str(version).split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError("not a release version: " + repr(version))
    major, minor, patch = (int(part) for part in parts)
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    if level == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError("unknown bump level: " + repr(level))


print(cyclomatic_complexity(SAMPLE))
print(quality_gate(SAMPLE, 3))
'''}],
                "hints": [
                    "Two passes make this much easier: one that finds every `def` and names it, and one that scores a single function without descending into nested scopes.",
                    "`ast.iter_child_nodes` walks one level; recurse yourself so you can stop at a nested FunctionDef, ClassDef or Lambda.",
                    "A generator expression carries `ast.comprehension` nodes with an `.ifs` list — score the clause and its filters together.",
                    "For the API diff, classify each parameter by where it was and where it is now; collect the triples in a set so duplicates from two removed parameters collapse.",
                ],
                "tests": [
                    {"name": "Complexity of the sample module", "code": r'''
_got = cyclomatic_complexity(SAMPLE)
_want = {"simple": 1, "guarded": 4, "Router.dispatch": 6, "Router.names": 3,
         "outer": 2, "outer.inner": 2}
assert _got == _want, f"cyclomatic_complexity(SAMPLE) gave {_got!r}, expected {_want}"
'''},
                    {"name": "Each decision kind is counted once", "code": r'''
_cases = [("def f():\n    pass\n", 1),
          ("def f(a):\n    if a:\n        return 1\n    return 0\n", 2),
          ("def f(a):\n    if a:\n        return 1\n    elif a == 2:\n        return 2\n    return 0\n", 3),
          ("def f(xs):\n    for x in xs:\n        pass\n", 2),
          ("def f(n):\n    while n:\n        n -= 1\n", 2),
          ("def f(a, b, c):\n    return a and b and c\n", 3),
          ("def f(a):\n    assert a\n", 2),
          ("def f(a):\n    return 1 if a else 2\n", 2),
          ("def f(xs):\n    return [x for x in xs if x if x > 1]\n", 4),
          ("def f():\n    try:\n        g()\n    except KeyError:\n        pass\n    except ValueError:\n        pass\n", 3)]
for _src, _want in _cases:
    _got = cyclomatic_complexity(_src)["f"]
    assert _got == _want, f"complexity of {_src!r} gave {_got!r}, expected {_want}"
'''},
                    {"name": "Nested definitions are separate entries", "code": r'''
_src = "def outer(xs):\n    def inner(y):\n        if y:\n            return 1\n        return 0\n    return inner\n"
_got = cyclomatic_complexity(_src)
assert _got == {"outer": 1, "outer.inner": 2}, \
    f"Got {_got!r} — a nested def gets its own dotted entry and does not inflate the parent"
_cls = "class A:\n    def m(self, x):\n        return 1 if x else 2\n"
assert cyclomatic_complexity(_cls) == {"A.m": 2}, f"Got {cyclomatic_complexity(_cls)!r}"
assert cyclomatic_complexity("x = 1\n") == {}, "a module with no functions scores nothing"
'''},
                    {"name": "The gate reports offenders worst first", "code": r'''
_got = quality_gate(SAMPLE, 3)
assert _got == [("Router.dispatch", 6), ("guarded", 4)], f"quality_gate(SAMPLE, 3) gave {_got!r}"
assert quality_gate(SAMPLE, 6) == [], "nothing exceeds a limit of 6, so the gate passes"
_tie = "def bbb(a):\n    if a:\n        pass\n\n\ndef aaa(a):\n    if a:\n        pass\n"
assert quality_gate(_tie, 1) == [("aaa", 2), ("bbb", 2)], \
    f"equal scores sort by name, got {quality_gate(_tie, 1)!r}"
'''},
                    {"name": "API diff: additions are minor", "code": r'''
_v1 = {"connect": {"required": ["host", "port"], "optional": ["timeout"]},
       "send": {"required": ["payload"], "optional": []},
       "close": {"required": [], "optional": []}}
_v2 = {"connect": {"required": ["host", "port"], "optional": ["timeout", "retries"]},
       "send": {"required": ["payload"], "optional": ["flush"]},
       "close": {"required": [], "optional": []},
       "ping": {"required": [], "optional": []}}
_got = api_changes(_v1, _v2)
_want = [("minor", "connect", "optional-param-added"),
         ("minor", "ping", "added"),
         ("minor", "send", "optional-param-added")]
assert _got == _want, f"api_changes gave {_got!r}, expected {_want}"
assert required_bump(_v1, _v2) == "minor", f"Got {required_bump(_v1, _v2)!r}"
assert api_changes(_v1, _v1) == [], "an unchanged surface has no changes"
assert required_bump(_v1, _v1) == "patch", "no changes means a patch release"
'''},
                    {"name": "API diff: narrowing is major", "code": r'''
_v1 = {"connect": {"required": ["host", "port"], "optional": ["timeout"]},
       "send": {"required": ["payload"], "optional": []},
       "close": {"required": [], "optional": []}}
_v3 = {"connect": {"required": ["host", "port", "tls"], "optional": ["timeout"]},
       "send": {"required": ["payload"], "optional": []}}
_got = api_changes(_v1, _v3)
_want = [("major", "close", "removed"), ("major", "connect", "required-param-added")]
assert _got == _want, f"api_changes gave {_got!r}, expected {_want}"
assert required_bump(_v1, _v3) == "major", f"Got {required_bump(_v1, _v3)!r}"
_tight = {"connect": {"required": ["host", "port", "timeout"], "optional": []},
          "send": {"required": ["payload"], "optional": []},
          "close": {"required": [], "optional": []}}
assert ("major", "connect", "optional-to-required") in api_changes(_v1, _tight), \
    f"promoting an optional parameter breaks callers: {api_changes(_v1, _tight)!r}"
_drop = {"connect": {"required": ["host", "port"], "optional": []},
         "send": {"required": ["payload"], "optional": []},
         "close": {"required": [], "optional": []}}
assert api_changes(_v1, _drop) == [("major", "connect", "optional-param-removed")], \
    f"Got {api_changes(_v1, _drop)!r}"
'''},
                    {"name": "API diff: relaxing is minor, reordering is not", "code": r'''
_v1 = {"connect": {"required": ["host", "port"], "optional": ["timeout"]},
       "send": {"required": ["payload"], "optional": []},
       "close": {"required": [], "optional": []}}
_relaxed = {"connect": {"required": ["host"], "optional": ["timeout", "port"]},
            "send": {"required": ["payload"], "optional": []},
            "close": {"required": [], "optional": []}}
assert api_changes(_v1, _relaxed) == [("minor", "connect", "required-to-optional")], \
    f"Got {api_changes(_v1, _relaxed)!r}"
assert required_bump(_v1, _relaxed) == "minor"
_swapped = {"connect": {"required": ["port", "host"], "optional": ["timeout"]},
            "send": {"required": ["payload"], "optional": []},
            "close": {"required": [], "optional": []}}
assert api_changes(_v1, _swapped) == [("major", "connect", "params-reordered")], \
    f"positional order is part of the contract: {api_changes(_v1, _swapped)!r}"
'''},
                    {"name": "bump_version follows semver and validates", "code": r'''
for _v, _level, _want in [("1.4.2", "minor", "1.5.0"), ("1.4.2", "major", "2.0.0"),
                          ("1.4.2", "patch", "1.4.3"), ("0.9.1", "major", "1.0.0"),
                          ("2.0.0", "patch", "2.0.1")]:
    _got = bump_version(_v, _level)
    assert _got == _want, f"bump_version({_v!r}, {_level!r}) gave {_got!r}, expected {_want!r}"
for _bad in [("1.4", "minor"), ("1.4.2.1", "minor"), ("1.x.2", "patch"), ("", "patch"),
             ("1.4.2", "huge"), ("1.4.2", "")]:
    try:
        bump_version(*_bad)
        assert False, f"bump_version{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a task tracker core, built test-first",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
A task-tracker **core** — no user interface, no database, just the part a team
would still trust in five years. Three files, three layers:

- `domain.py` — values, invariants and the workflow. Knows nothing about
  storage or events.
- `service.py` — the application layer: validates through the domain, keeps
  the tasks, and appends to an event log.
- `main.py` — a demo that uses the other two.

## `domain.py`

- `ValidationError(ValueError)` and `InvalidTransition(ValueError)`.
- `Status` — an `enum.Enum` with members `TODO`, `DOING`, `DONE`, `CANCELLED`
  and values `"todo"`, `"doing"`, `"done"`, `"cancelled"`.
- `ALLOWED` — the transition table: `TODO` may go to `DOING` or `CANCELLED`;
  `DOING` to `TODO`, `DONE` or `CANCELLED`; `DONE` is terminal; `CANCELLED`
  may be reopened to `TODO` only.
- `validate_title(title)` returns the trimmed title; `ValidationError` for a
  non-string, a blank string, or more than `MAX_TITLE` (80) characters.
- `validate_priority(priority)` returns an `int` in `1..5`; `ValidationError`
  otherwise, and a `bool` is not an acceptable int.
- `normalise_tags(tags)` returns a tuple of trimmed, lowercased, de-duplicated,
  alphabetically sorted tags, dropping empties.
- `can_transition(current, target)` consults `ALLOWED`.
- `Task` — a **frozen** dataclass with `id`, `title`, `priority`, `tags`,
  `status` (default `Status.TODO`), plus `with_status(target)` and
  `with_title(title)`, each returning a **new** `Task`.

## `service.py`

- `TaskNotFound(KeyError)`.
- `EventLog` — `append(kind, payload)` stores
  `{"seq": n, "kind": ..., "payload": dict(payload)}` with `seq` counting from
  1 and returns `n`; `events(kind=None)` returns a copy — entries *and* their
  payloads copied, so a caller cannot reach in and edit history — optionally
  filtered to one kind; `len(log)` works.
- `TaskService(log=None)` — ids allocated from 1 upwards; makes its own
  `EventLog` when given none.
  - `create(title, priority=3, tags=())` validates, stores, logs
    `"task.created"` with `{"id", "title", "priority", "tags"}` (tags as a
    list), returns the `Task`.
  - `get(task_id)` returns the task or raises `TaskNotFound`.
  - `move(task_id, target)` logs `"task.moved"` with `{"id", "from", "to"}`
    (status **values**, not members).
  - `retitle(task_id, title)` logs `"task.retitled"` with `{"id", "from", "to"}`.
  - `list(status=None, tag=None)` — matching tasks, highest priority first,
    then lowest id; `tag` matches case-insensitively.
  - `stats()` — `{status value: count}` with all four statuses present.
- `rebuild(log)` — a module-level function returning a **new** `TaskService`
  whose state is derived from the event log alone.

A rejected operation must log nothing and change nothing: validate first,
mutate second, log third.
''',
        "deliverables": [
            "`domain.py` — statuses, the transition table, validators and an immutable `Task`",
            "`service.py` — `EventLog`, `TaskService` and `rebuild`, importing only from `domain`",
            "`main.py` — a demo that creates, moves, retitles, reports and replays",
            "An append-only event log whose entries carry a sequence number, kind and payload",
            "A `rebuild` that reconstructs identical service state from the log alone",
            "Docstrings on every public class and method, describing the contract rather than the code",
        ],
        "constraints": [
            "Standard library only; `dataclasses` and `enum` are the only imports you need",
            "`domain.py` must not import `service.py` — the dependency points one way only",
            "Importing either module must print nothing and touch no global state",
            "`Task` is frozen: every change returns a new instance",
            "A rejected create, move or retitle appends no event and leaves the store untouched",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "Every automated check passes, including the empty-service, unknown-id and illegal-transition paths."},
            {"criterion": "Layering", "weight": 20,
             "evidence": "domain.py holds the rules and imports nothing from service.py; the service validates through the domain instead of re-implementing it."},
            {"criterion": "Event log & replay", "weight": 20,
             "evidence": "Events are appended in order with the specified payloads, and rebuild(log) reproduces the service state exactly."},
            {"criterion": "Atomicity", "weight": 10,
             "evidence": "A rejected operation leaves both the store and the log unchanged."},
            {"criterion": "Documented API", "weight": 10,
             "evidence": "Every public class and method carries a docstring stating its contract, including what it raises."},
        ],
        "hints": [
            "Write the check you want to pass, watch it fail, then write the smallest code that satisfies it — the order is the point of the exercise.",
            "`@dataclass(frozen=True)` plus `dataclasses.replace(self, status=target)` gives you immutable updates in one line.",
            "Validate through the domain *before* touching `self._tasks` and before logging, so a rejection cannot leave a half-applied change.",
            "`rebuild` should walk `log.events()` in order and apply each kind; `Status(payload['to'])` turns a stored value back into a member.",
        ],
        "files": [
            {"name": "domain.py", "content": r'''
from dataclasses import dataclass, replace
from enum import Enum

MAX_TITLE = 80


class ValidationError(ValueError):
    """Raised when a value is rejected before it can enter the domain."""


class InvalidTransition(ValueError):
    """Raised when a status change is not allowed by the workflow."""


class Status(Enum):
    pass


ALLOWED = {}


def validate_title(title):
    """Return the trimmed title, or raise ValidationError."""


def validate_priority(priority):
    """Return the priority as an int in 1..5, or raise ValidationError."""


def normalise_tags(tags):
    """Lowercased, trimmed, de-duplicated tags in alphabetical order."""


def can_transition(current, target):
    """True when moving from current to target is allowed."""


class Task:
    """One task. Frozen: every change returns a new instance."""
'''},
            {"name": "service.py", "content": r'''
from domain import (Status, Task, ValidationError, normalise_tags,
                    validate_priority, validate_title)


class TaskNotFound(KeyError):
    """Raised when no task carries the requested id."""


class EventLog:
    """An append-only record of everything the service did."""

    def __init__(self):
        self.events_ = []

    def append(self, kind, payload):
        """Record one event and return its 1-based sequence number."""

    def events(self, kind=None):
        """A copy of the log, optionally filtered to one kind."""


class TaskService:
    """The application layer: validates, stores, and records what happened."""

    def __init__(self, log=None):
        pass

    def create(self, title, priority=3, tags=()):
        """Validate and store a new task, logging task.created."""

    def get(self, task_id):
        """The task with this id, or TaskNotFound."""

    def move(self, task_id, target):
        """Move a task to a new status, logging task.moved."""

    def retitle(self, task_id, title):
        """Give a task a new validated title, logging task.retitled."""

    def list(self, status=None, tag=None):
        """Tasks matching the filters, most urgent first then by id."""

    def stats(self):
        """How many tasks sit in each status, every status present."""


def rebuild(log):
    """A fresh TaskService reconstructed from an event log alone."""
'''},
            {"name": "main.py", "content": r'''
from domain import Status
from service import EventLog, TaskService, rebuild

log = EventLog()
service = TaskService(log)

# create a few tasks, move one to DONE, retitle another,
# then print the list, the stats, and the stats of rebuild(log)
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "domain.py", "content": r'''
from dataclasses import dataclass, replace
from enum import Enum

MAX_TITLE = 80


class ValidationError(ValueError):
    """Raised when a value is rejected before it can enter the domain."""


class InvalidTransition(ValueError):
    """Raised when a status change is not allowed by the workflow."""


class Status(Enum):
    """Where a task sits in the workflow."""

    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    CANCELLED = "cancelled"


ALLOWED = {
    Status.TODO: (Status.DOING, Status.CANCELLED),
    Status.DOING: (Status.TODO, Status.DONE, Status.CANCELLED),
    Status.DONE: (),
    Status.CANCELLED: (Status.TODO,),
}


def validate_title(title):
    """Return the trimmed title, or raise ValidationError."""
    if not isinstance(title, str):
        raise ValidationError("title must be a string")
    trimmed = title.strip()
    if not trimmed:
        raise ValidationError("title must not be blank")
    if len(trimmed) > MAX_TITLE:
        raise ValidationError(f"title must be at most {MAX_TITLE} characters")
    return trimmed


def validate_priority(priority):
    """Return the priority as an int in 1..5, or raise ValidationError."""
    if isinstance(priority, bool) or not isinstance(priority, int):
        raise ValidationError("priority must be an int")
    if not 1 <= priority <= 5:
        raise ValidationError("priority must be between 1 and 5")
    return priority


def normalise_tags(tags):
    """Lowercased, trimmed, de-duplicated tags in alphabetical order."""
    cleaned = set()
    for tag in tags or ():
        if not isinstance(tag, str):
            raise ValidationError("tags must be strings")
        slug = tag.strip().lower()
        if slug:
            cleaned.add(slug)
    return tuple(sorted(cleaned))


def can_transition(current, target):
    """True when moving from current to target is allowed."""
    return target in ALLOWED.get(current, ())


@dataclass(frozen=True)
class Task:
    """One task. Frozen: every change returns a new instance."""

    id: int
    title: str
    priority: int
    tags: tuple
    status: Status = Status.TODO

    def with_status(self, target):
        """A copy in the new status; InvalidTransition when the move is illegal."""
        if not can_transition(self.status, target):
            raise InvalidTransition(f"{self.status.value} -> {target.value} is not allowed")
        return replace(self, status=target)

    def with_title(self, title):
        """A copy with a validated new title."""
        return replace(self, title=validate_title(title))
'''},
            {"name": "service.py", "content": r'''
from domain import (Status, Task, ValidationError, normalise_tags,
                    validate_priority, validate_title)


class TaskNotFound(KeyError):
    """Raised when no task carries the requested id."""


class EventLog:
    """An append-only record of everything the service did."""

    def __init__(self):
        self._events = []

    def append(self, kind, payload):
        """Record one event and return its 1-based sequence number."""
        seq = len(self._events) + 1
        self._events.append({"seq": seq, "kind": kind, "payload": dict(payload)})
        return seq

    def events(self, kind=None):
        """A copy of the log, optionally filtered to one kind."""
        return [{"seq": event["seq"], "kind": event["kind"],
                 "payload": dict(event["payload"])}
                for event in self._events
                if kind is None or event["kind"] == kind]

    def __len__(self):
        return len(self._events)


class TaskService:
    """The application layer: validates, stores, and records what happened."""

    def __init__(self, log=None):
        self._tasks = {}
        self._next_id = 1
        self.log = log if log is not None else EventLog()

    def create(self, title, priority=3, tags=()):
        """Validate and store a new task, logging task.created."""
        clean_title = validate_title(title)
        clean_priority = validate_priority(priority)
        clean_tags = normalise_tags(tags)
        task = Task(id=self._next_id, title=clean_title, priority=clean_priority,
                    tags=clean_tags, status=Status.TODO)
        self._tasks[task.id] = task
        self._next_id += 1
        self.log.append("task.created", {"id": task.id, "title": task.title,
                                         "priority": task.priority,
                                         "tags": list(task.tags)})
        return task

    def get(self, task_id):
        """The task with this id, or TaskNotFound."""
        if task_id not in self._tasks:
            raise TaskNotFound(f"no task with id {task_id}")
        return self._tasks[task_id]

    def move(self, task_id, target):
        """Move a task to a new status, logging task.moved."""
        task = self.get(task_id)
        moved = task.with_status(target)
        self._tasks[task_id] = moved
        self.log.append("task.moved", {"id": task_id, "from": task.status.value,
                                       "to": moved.status.value})
        return moved

    def retitle(self, task_id, title):
        """Give a task a new validated title, logging task.retitled."""
        task = self.get(task_id)
        renamed = task.with_title(title)
        self._tasks[task_id] = renamed
        self.log.append("task.retitled", {"id": task_id, "from": task.title,
                                          "to": renamed.title})
        return renamed

    def list(self, status=None, tag=None):
        """Tasks matching the filters, most urgent first then by id."""
        wanted = tag.strip().lower() if isinstance(tag, str) else None
        chosen = [task for task in self._tasks.values()
                  if (status is None or task.status is status)
                  and (wanted is None or wanted in task.tags)]
        return sorted(chosen, key=lambda task: (-task.priority, task.id))

    def stats(self):
        """How many tasks sit in each status, every status present."""
        counts = {status.value: 0 for status in Status}
        for task in self._tasks.values():
            counts[task.status.value] += 1
        return counts


def rebuild(log):
    """A fresh TaskService reconstructed from an event log alone."""
    service = TaskService(EventLog())
    tasks = {}
    next_id = 1
    for event in log.events():
        payload = event["payload"]
        task_id = payload["id"]
        kind = event["kind"]
        if kind == "task.created":
            tasks[task_id] = Task(id=task_id, title=payload["title"],
                                  priority=payload["priority"],
                                  tags=tuple(payload["tags"]), status=Status.TODO)
            next_id = max(next_id, task_id + 1)
        elif kind == "task.moved":
            tasks[task_id] = tasks[task_id].with_status(Status(payload["to"]))
        elif kind == "task.retitled":
            tasks[task_id] = tasks[task_id].with_title(payload["to"])
        else:
            raise ValidationError("unknown event kind " + repr(kind))
    service._tasks = tasks
    service._next_id = next_id
    return service
'''},
            {"name": "main.py", "content": r'''
from domain import Status
from service import EventLog, TaskService, rebuild

log = EventLog()
service = TaskService(log)

spec = service.create("Write the framing spec", priority=5, tags=["Docs", "spec"])
legacy = service.create("Characterise the legacy quote", priority=4, tags=["legacy"])
chore = service.create("Delete the dead config flag", priority=1, tags=["chore"])

service.move(spec.id, Status.DOING)
service.move(spec.id, Status.DONE)
service.retitle(chore.id, "Delete the dead config flag (approved)")

for task in service.list():
    print(task.priority, task.status.value, task.title)

print("stats:", service.stats())
print("events:", len(log))
print("replayed:", rebuild(log).stats())
'''},
        ],
        "tests": [
            {"name": "The domain validators accept and reject", "code": r'''
from domain import MAX_TITLE, ValidationError, validate_priority, validate_title
assert validate_title("  Ship it  ") == "Ship it", f'Got {validate_title("  Ship it  ")!r}'
assert validate_title("x" * MAX_TITLE) == "x" * MAX_TITLE, "a title of exactly MAX_TITLE is legal"
for _bad in ["", "   ", "x" * (MAX_TITLE + 1), None, 42]:
    try:
        validate_title(_bad)
        assert False, f"validate_title({_bad!r}) should raise ValidationError"
    except ValidationError:
        pass
for _good in (1, 3, 5):
    assert validate_priority(_good) == _good, f"validate_priority({_good}) should return {_good}"
for _bad in (0, 6, -1, "3", 2.0, True):
    try:
        validate_priority(_bad)
        assert False, f"validate_priority({_bad!r}) should raise ValidationError"
    except ValidationError:
        pass
'''},
            {"name": "Tags are normalised", "code": r'''
from domain import normalise_tags
_got = normalise_tags([" Docs ", "spec", "DOCS", "", "  "])
assert _got == ("docs", "spec"), f"Got {_got!r}, expected ('docs', 'spec')"
assert normalise_tags(()) == (), "no tags means an empty tuple"
assert normalise_tags(None) == (), "None is treated as no tags"
assert isinstance(normalise_tags(["a"]), tuple), "tags come back as a tuple, not a list"
'''},
            {"name": "The workflow table is enforced", "code": r'''
from domain import ALLOWED, InvalidTransition, Status, Task, can_transition
assert [s.value for s in Status] == ["todo", "doing", "done", "cancelled"], \
    f"Status values are {[s.value for s in Status]!r}"
assert can_transition(Status.TODO, Status.DOING) is True
assert can_transition(Status.DOING, Status.DONE) is True
assert can_transition(Status.CANCELLED, Status.TODO) is True
assert can_transition(Status.TODO, Status.DONE) is False, "TODO cannot jump straight to DONE"
assert ALLOWED[Status.DONE] == () or list(ALLOWED[Status.DONE]) == [], "DONE is terminal"
_t = Task(id=1, title="a", priority=3, tags=())
_moved = _t.with_status(Status.DOING)
assert _moved is not _t and _moved.status is Status.DOING, "with_status returns a new Task"
assert _t.status is Status.TODO, "the original Task must be unchanged — it is frozen"
try:
    _t.with_status(Status.DONE)
    assert False, "TODO -> DONE should raise InvalidTransition"
except InvalidTransition:
    pass
'''},
            {"name": "create allocates ids and validates", "code": r'''
from domain import Status, ValidationError
from service import TaskService
_s = TaskService()
_a = _s.create("  First  ", priority=5, tags=["Docs", "docs"])
_b = _s.create("Second")
assert (_a.id, _b.id) == (1, 2), f"ids should start at 1 and increase, got {(_a.id, _b.id)!r}"
assert _a.title == "First" and _a.tags == ("docs",), f"Got {_a!r}"
assert _b.priority == 3, f"the default priority is 3, got {_b.priority!r}"
assert _a.status is Status.TODO, "a new task starts in TODO"
_before = len(_s.log.events())
for _bad in [("", 3), ("ok", 9), ("ok", "high")]:
    try:
        _s.create(*_bad)
        assert False, f"create{_bad!r} should raise ValidationError"
    except ValidationError:
        pass
assert len(_s.log.events()) == _before, "a rejected create must append no event"
assert len(_s.list()) == 2, "a rejected create must not store anything"
'''},
            {"name": "get raises TaskNotFound for an unknown id", "code": r'''
from service import TaskNotFound, TaskService
_s = TaskService()
_t = _s.create("Only one")
assert _s.get(_t.id).title == "Only one", "get should return the stored task"
for _bad in (0, 99, -1):
    try:
        _s.get(_bad)
        assert False, f"get({_bad}) should raise TaskNotFound"
    except TaskNotFound:
        pass
'''},
            {"name": "move and retitle, and their rejections", "code": r'''
from domain import InvalidTransition, Status, ValidationError
from service import TaskNotFound, TaskService
_s = TaskService()
_t = _s.create("Draft", priority=2)
_s.move(_t.id, Status.DOING)
_done = _s.move(_t.id, Status.DONE)
assert _done.status is Status.DONE, f"Got {_done.status!r}"
assert _s.get(_t.id).status is Status.DONE, "the stored task should reflect the move"
_events_before = len(_s.log.events())
try:
    _s.move(_t.id, Status.DOING)
    assert False, "DONE is terminal — moving out of it should raise InvalidTransition"
except InvalidTransition:
    pass
try:
    _s.move(404, Status.DOING)
    assert False, "moving an unknown id should raise TaskNotFound"
except TaskNotFound:
    pass
assert len(_s.log.events()) == _events_before, "a rejected move must append no event"
_r = _s.retitle(_t.id, "  Draft v2 ")
assert _r.title == "Draft v2", f"Got {_r.title!r}"
try:
    _s.retitle(_t.id, "   ")
    assert False, "a blank retitle should raise ValidationError"
except ValidationError:
    pass
assert _s.get(_t.id).title == "Draft v2", "a rejected retitle must leave the title alone"
'''},
            {"name": "list filters and orders, stats counts", "code": r'''
from domain import Status
from service import TaskService
_s = TaskService()
_a = _s.create("low", priority=1, tags=["ops"])
_b = _s.create("high", priority=5, tags=["Ops", "urgent"])
_c = _s.create("mid", priority=5, tags=[])
_order = [t.id for t in _s.list()]
assert _order == [_b.id, _c.id, _a.id], f"list order was {_order!r}: priority first, then id"
_s.move(_a.id, Status.CANCELLED)
assert [t.id for t in _s.list(status=Status.CANCELLED)] == [_a.id], "status filter"
assert [t.id for t in _s.list(tag="OPS")] == [_b.id, _a.id], "tag filter is case-insensitive"
assert _s.list(tag="nothing") == [], "an unmatched tag gives an empty list"
assert _s.stats() == {"todo": 2, "doing": 0, "done": 0, "cancelled": 1}, f"Got {_s.stats()!r}"
assert TaskService().stats() == {"todo": 0, "doing": 0, "done": 0, "cancelled": 0}, \
    "an empty service still reports every status"
'''},
            {"name": "The event log is ordered and carries the right payloads", "code": r'''
from domain import Status
from service import EventLog, TaskService
_log = EventLog()
_s = TaskService(_log)
_t = _s.create("Ship", priority=4, tags=["Rel"])
_s.move(_t.id, Status.DOING)
_s.retitle(_t.id, "Ship it")
_events = _log.events()
assert [e["seq"] for e in _events] == [1, 2, 3], f"sequence numbers were {[e['seq'] for e in _events]!r}"
assert [e["kind"] for e in _events] == ["task.created", "task.moved", "task.retitled"], \
    f"kinds were {[e['kind'] for e in _events]!r}"
assert _events[0]["payload"] == {"id": _t.id, "title": "Ship", "priority": 4, "tags": ["rel"]}, \
    f"created payload was {_events[0]['payload']!r}"
assert _events[1]["payload"] == {"id": _t.id, "from": "todo", "to": "doing"}, \
    f"moved payload was {_events[1]['payload']!r}"
assert _events[2]["payload"] == {"id": _t.id, "from": "Ship", "to": "Ship it"}, \
    f"retitled payload was {_events[2]['payload']!r}"
assert len(_log) == 3, f"len(log) gave {len(_log)!r}, expected 3"
assert [e["kind"] for e in _log.events("task.moved")] == ["task.moved"], "events(kind) filters"
_events[0]["payload"]["title"] = "tampered"
assert _log.events()[0]["payload"]["title"] == "Ship", "events() must hand back a copy, not the log itself"
'''},
            {"name": "rebuild reproduces the service from the log alone", "code": r'''
from domain import Status
from service import EventLog, TaskService, rebuild
_log = EventLog()
_s = TaskService(_log)
_a = _s.create("alpha", priority=5, tags=["x"])
_b = _s.create("beta", priority=2)
_s.move(_a.id, Status.DOING)
_s.move(_a.id, Status.DONE)
_s.move(_b.id, Status.CANCELLED)
_s.retitle(_b.id, "beta reborn")
_copy = rebuild(_log)
assert isinstance(_copy, TaskService), "rebuild returns a TaskService"
assert _copy.stats() == _s.stats(), f"replayed stats {_copy.stats()!r} != live stats {_s.stats()!r}"
assert [(t.id, t.title, t.priority, t.tags, t.status) for t in _copy.list()] == \
       [(t.id, t.title, t.priority, t.tags, t.status) for t in _s.list()], \
    "the replayed tasks should match the live ones exactly"
_next = _copy.create("gamma")
assert _next.id == 3, f"the rebuilt service should continue the id sequence, got {_next.id!r}"
assert rebuild(EventLog()).stats() == {"todo": 0, "doing": 0, "done": 0, "cancelled": 0}, \
    "an empty log rebuilds an empty service"
'''},
            {"name": "The layering holds and the modules are import-clean", "code": r'''
_domain = open("domain.py").read()
_service = open("service.py").read()
assert "import service" not in _domain and "from service" not in _domain, \
    "domain.py must not depend on service.py — the dependency points one way"
assert "from domain" in _service or "import domain" in _service, \
    "service.py should build on the domain rather than re-implement its rules"
for _name, _src in [("domain.py", _domain), ("service.py", _service)]:
    assert "print(" not in _src, f"{_name} is a library; the printing belongs in main.py"
'''},
        ],
    },
}
