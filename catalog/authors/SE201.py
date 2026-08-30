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
            "quiz": {
                "title": "Where the ambiguity actually lives",
                "minutes": 7,
                "questions": [
                    {
                        "q": "The rule says the discount applies to orders *over £100*. What has to be in the suite before anyone can claim that boundary is pinned down?",
                        "opts": [
                            "A case at exactly £100 and a case at £100.01",
                            "A case at £50 and a case at £150, one well inside each partition",
                            "A single case at £101 — the rule has one branch, so one example covers it",
                            "A random sample of subtotals, so the suite cannot overfit to chosen values",
                        ],
                        "a": 0,
                        "why": r"""
*Over* is a strict comparison, and the only place a strict comparison behaves
differently from a loose one is at the boundary value itself. A pair at £100 and
£100.01 fails the moment somebody types `>=`. A pair at £50 and £150 passes under
either operator, so it carries no information about which one was meant. A single
case at £101 is consistent with a threshold anywhere between £100 and £101. And
random subtotals are no defence either: the inputs that separate the two readings
are a vanishing fraction of the range, so randomness reliably misses them.
""",
                    },
                    {
                        "q": "In Python, `round(0.5)` is `0` and `round(1.5)` is `2`. Both arguments are exactly representable and both sit exactly halfway. What rule produced that?",
                        "opts": [
                            "`round` truncates towards zero",
                            "Neither 0.5 nor 1.5 is representable in binary, so there is no real tie to break",
                            "Ties go to the nearest even result, so 0.5 falls to 0 and 1.5 rises to 2",
                            "`round` alternates direction between calls, to keep a column of figures unbiased",
                        ],
                        "a": 2,
                        "why": r"""
Half-to-even, usually called banker's rounding, and it is the IEEE-754 default. It
exists because always rounding halves upwards drags a long column of figures
steadily upwards with them. Truncation would have produced `0` and `1`, so that is
not what happened, and both values are exact in binary — 0.5 and 1.5 are 2⁻¹ and
3×2⁻¹ — so representation is not the explanation either. Nothing about `round`
keeps state between calls. Money usually wants half-up instead, which is why the
lab reaches for `Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`
rather than arguing with the built-in.
""",
                    },
                    {
                        "q": "A test computes its expected value by calling the function under test, then asserts the two are equal. What can that test detect?",
                        "opts": [
                            "Only non-determinism, and a crash — it passes for any implementation that returns the same thing twice",
                            "That the function matches its specification",
                            "Nothing, because an assertion like that always fails",
                            "That the function's boundary handling is correct",
                        ],
                        "a": 0,
                        "why": r"""
Both sides of the comparison come from the same code, so the assertion reduces to
`f(x) == f(x)`. That is true of a correct implementation and equally true of one
that returns 42 for everything. It will fire if the function is non-deterministic
or raises, and that is the whole of its power. It is also why the lab reads the
source of `spec_cases` and refuses it if `order_total` appears inside: a
specification that asks the implementation what it thinks is not a specification,
it is a mirror.
""",
                    },
                    {
                        "q": "A rule turns on three independent booleans and one three-way enumeration. How many rows does the exhaustive decision table have?",
                        "opts": ["8", "12", "24", "9"],
                        "a": 2,
                        "why": r"""
2 × 2 × 2 × 3 = 24 — the arities multiply, they do not add. The count matters even
when you have no intention of writing all 24 rows, because equivalence partitioning
is a decision to leave rows out, and that is only a defensible decision if you know
how many there were to begin with. Twenty-four is also small enough to be worth
generating: `itertools.product` over the four axes costs one line and removes the
question of whether you missed a combination.
""",
                    },
                    {
                        "q": "Why does an acceptance criterion belong to the requirement rather than to the implementation that satisfies it?",
                        "opts": [
                            "A criterion written against the implementation has to be rewritten whenever the implementation changes, and then it is no longer independent evidence",
                            "Product owners are not permitted to read source code",
                            "A criterion attached to the implementation runs more slowly in CI",
                            "A requirement is allowed at most one criterion, so the rest have to live elsewhere",
                        ],
                        "a": 0,
                        "why": r"""
The criterion is the thing that is supposed to survive the rewrite. If it names
internals — a helper, a private attribute, the order the multipliers are applied in
— then every refactoring edits it, and a check you edit until it passes is not a
check. Criteria phrased in the domain's own terms, *a £100.01 order pays 90.01*,
outlive three implementations and are still readable by the person who asked for
the feature. Who may read code, how fast CI runs and how many criteria a
requirement may carry are all beside the point.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The resolved rule, five holes deep",
                "minutes": 9,
                "caption": "main.py — the specification, written out as code",
                "lang": "python",
                "brief": r'''
One sentence of English became five separate decisions, and each of them is a place
the code can be wrong without ever *looking* wrong. Every hole below is a choice
between readings that a reasonable person could have made — the operator at the
volume boundary, the rounding policy, and which number each discount is taken from.

Nothing is executed here. You are choosing between interpretations, which is the
part that happens before any code gets written.
''',
                "listing": r'''
from decimal import Decimal, ROUND_HALF_UP


def round_money(value):
    """Two decimals, half away from zero, handed back as a float."""
    return float(Decimal(___).quantize(Decimal("0.01"), rounding=___))


def order_total(subtotal, member=False, express=False):
    """The payable total for one order, following the resolved specification."""
    if subtotal < 0:
        raise ValueError("subtotal must not be negative")
    amount = subtotal * 0.90 if subtotal ___ 100 else float(subtotal)
    if member:
        amount = ___ * 0.95
    shipping = 0.0 if ___ >= 50 else 4.99
    if express:
        shipping = shipping + 9.99
    return round_money(amount + shipping)
''',
                "blanks": [
                    {
                        "prompt": "`Decimal` will happily accept a float. Why does it get something else here?",
                        "hole": "arg",
                        "opts": ["str(value)", "value", "round(value, 2)", "float(value)"],
                        "a": 0,
                        "why": "`Decimal(str(2.675))` is exactly 2.675, because what gets parsed is the decimal digits. Going through the string is the whole trick: it recovers the number the user typed rather than the double the machine stored.",
                        "whys": [
                            "`Decimal(str(2.675))` is exactly 2.675, because what gets parsed is the decimal digits. Going through the string is the whole trick: it recovers the number the user typed rather than the double the machine stored.",
                            "`Decimal(2.675)` is `2.67499999999999982236431605997495353221893310546875` — the exact value of the nearest double. Quantising that gives 2.67, which is precisely the behaviour this function exists to avoid.",
                            "`round` is the half-to-even rounding being replaced. Calling it first settles the question the wrong way, and then the quantise re-rounds an already-rounded number.",
                            "`float(value)` is a no-op on a float and lands in the same trap as passing it straight through: `Decimal` receives the binary value, not the decimal one.",
                        ],
                    },
                    {
                        "prompt": "Which rounding mode does the money policy call for?",
                        "hole": "mode",
                        "opts": ["ROUND_HALF_EVEN", "ROUND_CEILING", "ROUND_HALF_UP", "ROUND_DOWN"],
                        "a": 2,
                        "why": "Half away from zero: 2.675 becomes 2.68, and 2.674 still becomes 2.67. It is a policy rather than a fact — plenty of finance systems use half-even on purpose — and what matters is that the specification names one and the code obeys it.",
                        "whys": [
                            "`ROUND_HALF_EVEN` is the `decimal` default and reproduces the built-in `round`'s tie-breaking, which is the behaviour the exercise set out to replace.",
                            "`ROUND_CEILING` rounds towards positive infinity, so it never rounds down at all: 2.671 would become 2.68 and every customer would be overcharged by up to a penny.",
                            "Half away from zero: 2.675 becomes 2.68, and 2.674 still becomes 2.67. It is a policy rather than a fact — plenty of finance systems use half-even on purpose — and what matters is that the specification names one and the code obeys it.",
                            "`ROUND_DOWN` truncates towards zero, so 2.679 becomes 2.67. Consistent, and consistently in the customer's favour, but it is not what the specification says.",
                        ],
                    },
                    {
                        "prompt": "The specification says the volume discount applies to a subtotal *strictly greater* than 100.",
                        "hole": "op",
                        "opts": [">", ">=", "<", "!="],
                        "a": 0,
                        "why": "`order_total(100.0)` is 100.0 and `order_total(100.01)` is 90.01 — the two worked examples that exist purely to pin this operator down. Strictly greater is the reading the team settled on, so the code has to say so out loud.",
                        "whys": [
                            "`order_total(100.0)` is 100.0 and `order_total(100.01)` is 90.01 — the two worked examples that exist purely to pin this operator down. Strictly greater is the reading the team settled on, so the code has to say so out loud.",
                            "`>=` gives the discount at exactly 100, so `order_total(100.0)` would return 90.0. That is a perfectly defensible rule and it is not this one, which is exactly why a boundary pair belongs in the suite.",
                            "`<` inverts the rule entirely: small orders would collect the volume discount and large ones would not.",
                            "`!=` discounts everything except an order of exactly 100 — a rule nobody wrote down, and one that a suite without a boundary pair would never notice.",
                        ],
                    },
                    {
                        "prompt": "*A further 5%* — five per cent of what?",
                        "hole": "base",
                        "opts": ["subtotal", "amount", "round_money(subtotal)", "amount + shipping"],
                        "a": 1,
                        "why": "The member discount compounds on the already-discounted amount: 200 × 0.90 × 0.95 = 171.0, which is the worked example. Taking the 5% from the raw subtotal instead gives 180.0 − 10.0 = 170.0, and both readings are defensible English — which is why the resolution has to be written down.",
                        "whys": [
                            "`subtotal * 0.95` throws the volume discount away altogether, so a member ordering 200 would pay 190.0 instead of 171.0. Even the charitable reading of that line, *5% of the original*, lands on 170.0.",
                            "The member discount compounds on the already-discounted amount: 200 × 0.90 × 0.95 = 171.0, which is the worked example. Taking the 5% from the raw subtotal instead gives 180.0 − 10.0 = 170.0, and both readings are defensible English — which is why the resolution has to be written down.",
                            "Rounding to pennies mid-calculation bakes a rounding error into everything downstream, and it still takes the 5% from the wrong base.",
                            "`shipping` has not been computed yet at this line, so this is a `NameError`. Once it is computed, discounting the postage as well is a third rule again, and nobody asked for it.",
                        ],
                    },
                    {
                        "prompt": "Free shipping is decided on which number — before or after the discounts?",
                        "hole": "basis",
                        "opts": ["subtotal", "amount", "amount + 4.99", "round_money(amount)"],
                        "a": 0,
                        "why": "The specification says the *pre-discount* subtotal, so shipping never changes just because a discount was applied. Deciding on the discounted figure would create a band of orders just above 50 where the customer's own discount takes their free postage away.",
                        "whys": [
                            "The specification says the *pre-discount* subtotal, so shipping never changes just because a discount was applied. Deciding on the discounted figure would create a band of orders just above 50 where the customer's own discount takes their free postage away.",
                            "`amount` is the discounted figure, not the figure anybody pays. A member ordering 51.00 has goods of 48.45, which is under 50, so the postage is charged and the total comes to 53.44 — while a non-member on the identical order pays 51.00 and nothing for delivery. Membership would cost them their free postage and leave them worse off, which is nobody's reading of *free on larger orders*.",
                            "Adding the postage to the goods before the comparison quietly moves the free-shipping threshold down to 45.01 of goods, and nothing in the code says so.",
                            "Rounding is not the no-op it looks like: a member ordering 52.63 has `amount = 49.9985`, which `round_money` lifts to exactly 50.00, so this basis gives free postage where a bare `amount` charges 4.99 — the two spellings differ by £4.99 on that order. Either way it commits to the discounted amount as the basis, which is the deciding error here, hidden behind a harmless-looking call.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "What *a further 5%* actually costs",
                "minutes": 11,
                "vars": ["S", "d_1", "d_2", "T", "e"],
                "brief": r'''
The product owner wrote *"Give customers 10% off big orders. Members get a further
5%."* Two people read that and reach two different totals, and neither is being
careless: *a further 5%* can mean five more points off the original, or 5% off
whatever is left after the first discount. The team chose the second.

Work out what single discount that choice actually amounts to.
''',
                "steps": [
                    {
                        "prompt": r"A subtotal $S$ has the volume discount $d_1$ applied to it. Write what the customer owes afterwards.",
                        "answer": r"S \cdot (1 - d_1)",
                        "hint": r"Taking the fraction $d_1$ away leaves the fraction $1 - d_1$ behind.",
                        "deconstruct": [
                            r"The discount removes $S d_1$ from the bill.",
                            r"What is left is $S - S d_1$, and $S$ factors out.",
                        ],
                    },
                    {
                        "prompt": r"The member discount $d_2$ is then applied to *that* amount, not to $S$. Write the total $T$.",
                        "given": r"You have $S(1 - d_1)$ going in.",
                        "answer": r"S \cdot (1 - d_1) \cdot (1 - d_2)",
                        "hint": r"Do to the previous line exactly what the previous line did to $S$.",
                        "deconstruct": [
                            r"Removing the fraction $d_2$ from a quantity leaves $(1 - d_2)$ of it.",
                            r"The quantity here is $S(1 - d_1)$, so multiply that by $(1 - d_2)$.",
                        ],
                    },
                    {
                        "prompt": r"Now find the single effective discount $e$ that would reach the same total in one step, so that $T = S(1 - e)$. Give $e$ in terms of $d_1$ and $d_2$.",
                        "answer": r"d_1 + d_2 - d_1 \cdot d_2",
                        "hint": r"Expand $(1 - d_1)(1 - d_2)$, then read off what is being subtracted from 1.",
                        "deconstruct": [
                            r"$(1 - d_1)(1 - d_2) = 1 - d_1 - d_2 + d_1 d_2$.",
                            r"Match that against $1 - e$: every sign flips, so $e = d_1 + d_2 - d_1 d_2$.",
                        ],
                    },
                    {
                        "prompt": r"Put the specification's numbers in — $d_1 = 0.10$ and $d_2 = 0.05$ — and give $e$ as a decimal.",
                        "given": r"$e = d_1 + d_2 - d_1 d_2$.",
                        "answer": r"0.145",
                        "hint": r"$0.10 \times 0.05$ is the term that stops this being 0.15.",
                        "deconstruct": [
                            r"$d_1 + d_2 = 0.15$.",
                            r"$d_1 d_2 = 0.005$, and it is subtracted, not added.",
                        ],
                    },
                ],
                "closing": r'''
So *a further 5%* is 14.5% off, not 15%. The missing half a point is the 5% that
was never charged on the tenth of the bill already taken away — and it is real
money: on a £200 order the two readings differ by exactly £1.00, which is why the
lab's worked example says `171.0` and not `170.0`.

The general shape is worth carrying around. Discounts compose as
$1 - e = (1 - d_1)(1 - d_2)$, never as $e = d_1 + d_2$, and the naive sum always
errs in the same direction — it overstates the discount. Interest, tax and margin
compose the same way, which is why *"a further n%"* is worth a clarifying question
every single time somebody writes it.
''',
            },
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
            "quiz": {
                "title": "Changing the shape without changing the behaviour",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Halfway through a refactoring, a test that was failing starts passing. What has happened?",
                        "opts": [
                            "Behaviour changed, so whatever that move was, it was not a refactoring",
                            "The refactoring worked — a cleaner structure fixes defects as a side effect",
                            "The test was flaky and should be deleted",
                            "Nothing worth stopping for, as long as no other test broke",
                        ],
                        "a": 0,
                        "why": r"""
Refactoring is defined as a behaviour-preserving transformation, and that is not
pedantry — it is the entire reason you are allowed to do it without asking anybody.
If nothing observable moves, nothing observable can break. A test changing its
verdict in *either* direction is evidence that something observable did move. The
change may well be an improvement; take it, but take it as its own deliberate
commit, so that the commit which fixes a bug is not also the commit that moved four
hundred lines around.
""",
                    },
                    {
                        "q": "`legacy_quote(0.0, 10, False, \"standard\")` returns `None` today, and the business says a zero-weight parcel ought to be a validation error instead. What goes into the characterisation suite for that call?",
                        "opts": [
                            "`None` — the suite records what the code does today, not what it ought to do",
                            "A `ValueError`, so that the suite drives the fix",
                            "Nothing; leave the case out until the behaviour is corrected",
                            "Both, with the `None` marked as a known defect",
                        ],
                        "a": 0,
                        "why": r"""
A characterisation suite is a detector of *change*, not a statement of intent.
Record the desired behaviour and the suite is red from the moment it is written,
and a red suite cannot tell you whether your last extraction broke something.
Record the `None`, get to green, refactor to green, and only then change the
behaviour on purpose — in its own commit, where the suite's diff shows exactly one
recorded value moving. That diff is the best documentation the fix will ever have.
Leaving the case out is worse than either: it is the one input most likely to be
handled differently by the replacement.
""",
                    },
                    {
                        "q": "A module written last week, in the current framework, with no tests. Is it legacy code, under the definition this module uses?",
                        "opts": [
                            "No; legacy means code that predates the current framework",
                            "No; legacy means code whose author has left the team",
                            "Only once it is large enough that nobody can hold it in their head",
                            "Yes — code without tests is legacy, whatever its age",
                        ],
                        "a": 3,
                        "why": r"""
The definition is operational rather than chronological: legacy code is code you
cannot change with confidence, and tests are what supply the confidence. Last
week's untested module and a ten-year-old one leave you in exactly the same
position, and the first move on either is to write the characterisation suite you
wish somebody had left behind. Age, absent authors and sheer size all correlate
with the problem, which is why they get used as shorthand, but none of them is the
property that actually decides whether you can touch the code.
""",
                    },
                    {
                        "q": "`shipping_quote` opens with `if weight <= 0 or distance <= 0 or priority not in PRIORITIES: return None`, replacing three nested `if`s. What does that flattening buy, on its own?",
                        "opts": [
                            "A body with no unstated preconditions: after the guard, every remaining line reads at one level of indentation as the case that succeeds",
                            "Three fewer decision points, and so a lower cyclomatic complexity",
                            "A guarantee that the function can no longer raise",
                            "Fewer conditions to get wrong — the same three checks have become two",
                        ],
                        "a": 0,
                        "why": r"""
The win is for the reader, and the complexity metric barely registers it. Score
both regions under this course's own rules. The nest is `if weight > 0`, `if
distance > 0`, and `if priority == "standard" or priority == "two-day" or priority
== "next-day"` — three `if`s, plus two more for the three-valued `or` inside the
third: five decision points. The guard is one `if` plus two for its own
three-valued `or`, and `not in` is a comparison, which scores nothing: three. So
the flattening removes two decision points, not three, off a function that scores
18 — a rounding error. The number really does move across the whole refactoring —
`legacy_quote` scores 18 as a single function, while nothing in `refactored.py`
scores above 4 — but that is the *extraction* doing the work, not the early return.
Nothing about a guard clause prevents a raise, and the three checks are still three
checks, merely negated and moved to the top.
""",
                    },
                    {
                        "q": "Why re-run the safety net after every single extraction, rather than once when the refactoring is finished?",
                        "opts": [
                            "A failure then names the one move that caused it, instead of leaving a dozen candidates to bisect",
                            "The suite gets slower as more of the legacy code is replaced",
                            "The recorded expectations have to be regenerated from the new code after each move",
                            "The runner stops at its first failure, so later moves would be masked",
                        ],
                        "a": 0,
                        "why": r"""
The cost of diagnosis grows much faster than the number of changes you have to
consider. One move between green and red makes it free. Twelve moves turns it into
a bisection, and a bisection over a refactoring is worse than it sounds, because
the intermediate states may not even run. Regenerating the expectations would be
circular — the recorded values are taken from `legacy_quote` once and then never
touched again, which is the only thing that makes them evidence. Whether a runner
stops at the first failure is a flag, not a reason.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Reading the constants back out of the nest",
                "minutes": 9,
                "caption": "refactored.py — the same behaviour, laid out flat",
                "lang": "python",
                "brief": r'''
Once the safety net is up, `legacy.py` *is* the specification: there is nothing else
to derive the numbers from. Every hole below is a constant or a decision that has to
come out of the nest unchanged, and three of them are places where a plausible
alternative silently changes what customers get charged.

The last hole is the interesting one. Look at where `legacy_quote` calls `round`,
and what the band is computed from.
''',
                "listing": r'''
# refactored.py — the same behaviour as legacy.py, laid out flat.
# fragile_multiplier, priority_adjust and band_for live further down the file.

PRIORITIES = ("standard", "two-day", "next-day")


def base_rate(weight):
    """The weight-band charge, before distance, fragility and priority."""
    if weight < 1:
        return 4.0
    if weight < 5:
        return 4.0 + (weight - 1) * ___
    if weight < 20:
        return ___ + (weight - 5) * 1.1
    return 26.5 + (weight - 20) * 0.8


def distance_surcharge(distance):
    """What the distance adds. Nothing at all under 100 km."""
    if distance > 500:
        return 12.0 + (distance - 500) * 0.02
    if distance > 100:
        return (distance - ___) * 0.03
    return 0.0


def shipping_quote(weight, distance, fragile, priority):
    """(rounded rate, band), or a refusal. Guard clauses first, then flat arithmetic."""
    if weight <= 0 or distance <= 0 or priority not in PRIORITIES:
        return ___
    rate = base_rate(weight) + distance_surcharge(distance)
    rate = rate * fragile_multiplier(weight, fragile)
    rate = priority_adjust(rate, priority)
    return (round(rate, 2), band_for(___))
''',
                "blanks": [
                    {
                        "prompt": "The per-kilogram rate for the 1–5 kg band.",
                        "hole": "rate",
                        "opts": ["1.1", "0.8", "4.0", "1.5"],
                        "a": 3,
                        "why": "`rate = 4.0 + (weight - 1) * 1.5` is the line buried in the nest. The three bands charge 1.5, then 1.1, then 0.8 per kilogram — heavier parcels cost less per kilogram, which is the usual shape of a carrier's tariff.",
                        "whys": [
                            "1.1 is the 5–20 kg rate. Using it here undercharges every parcel between 1 and 5 kg, and the safety net catches it on the first case that lands in that band.",
                            "0.8 belongs to the band above 20 kg and is the cheapest of the three. Rates fall as the parcel gets heavier, so the lightest band cannot have the lowest one.",
                            "4.0 is the flat charge for anything under a kilogram — the band's starting price, not its slope.",
                            "`rate = 4.0 + (weight - 1) * 1.5` is the line buried in the nest. The three bands charge 1.5, then 1.1, then 0.8 per kilogram — heavier parcels cost less per kilogram, which is the usual shape of a carrier's tariff.",
                        ],
                    },
                    {
                        "prompt": "Where the 5–20 kg band starts. It is not a free choice.",
                        "hole": "base",
                        "opts": ["10.0", "4.0", "26.5", "5.5"],
                        "a": 0,
                        "why": "10.0 — and it is forced, because the band below ends at `4.0 + (5 - 1) * 1.5 = 10.0`. That is what makes the price continuous across the 5 kg boundary; a 4.999 kg parcel and a 5.001 kg one should not differ by pounds.",
                        "whys": [
                            "10.0 — and it is forced, because the band below ends at `4.0 + (5 - 1) * 1.5 = 10.0`. That is what makes the price continuous across the 5 kg boundary; a 4.999 kg parcel and a 5.001 kg one should not differ by pounds.",
                            "4.0 is where the *lightest* band starts. Using it here makes a 5 kg parcel about £6 cheaper than a 4.9 kg one, and a customer who noticed would repackage.",
                            "26.5 is the base above 20 kg, and it is continuous for exactly the same reason: `10.0 + (20 - 5) * 1.1 = 26.5`. The tariff is built so that every band picks up where the last one left off.",
                            "5.5 appears nowhere in `legacy.py`. The constants are the specification now, and there is nothing to derive them from except the code itself.",
                        ],
                    },
                    {
                        "prompt": "The middle band charges 3p per kilometre — measured from where?",
                        "hole": "from",
                        "opts": ["500", "0", "100", "12.0"],
                        "a": 2,
                        "why": "From 100, because the surcharge is what the distance adds *beyond* the free first 100 km. At exactly 101 km it is 3p, not £3.03. Subtracting the band's own lower edge is also what keeps the charge continuous at 100, where it has to be zero from both sides.",
                        "whys": [
                            "500 is this band's upper edge. Subtracting it makes the surcharge negative for every distance under 500 km — a discount for going further.",
                            "Subtracting nothing charges 3p from the very first kilometre, so a 101 km trip picks up £3.03 of surcharge instead of 3p, and the free-under-100 rule quietly evaporates.",
                            "From 100, because the surcharge is what the distance adds *beyond* the free first 100 km. At exactly 101 km it is 3p, not £3.03. Subtracting the band's own lower edge is also what keeps the charge continuous at 100, where it has to be zero from both sides.",
                            "12.0 is the fixed part of the band above 500 km, not a distance at all. It is also the number that keeps *that* band continuous, since `(500 - 100) * 0.03 = 12.0`.",
                        ],
                    },
                    {
                        "prompt": "What does the legacy code hand back for input it refuses?",
                        "hole": "value",
                        "opts": ["None", '(0.0, "A")', "0.0", "False"],
                        "a": 0,
                        "why": "`None`, from all three `else` branches of the nest. Preserving it matters more than whether it is a good design: somewhere there is a caller testing `if quote is None`, and the safety net records the `None` precisely so that changing it later has to be a visible, deliberate act.",
                        "whys": [
                            "`None`, from all three `else` branches of the nest. Preserving it matters more than whether it is a good design: somewhere there is a caller testing `if quote is None`, and the safety net records the `None` precisely so that changing it later has to be a visible, deliberate act.",
                            "This one looks harmless and is the worst of the four, because it is a *valid-shaped* answer: a caller unpacking the tuple carries on cheerfully and bills the customer nothing.",
                            "`0.0` is a bare number where every other path returns a tuple, so callers break — but they break at the unpacking, a long way from the cause.",
                            "`False` is falsy like `None` and equal to `0` like the number, so roughly half the callers keep working and the other half do not. That is worse than either consistent choice.",
                        ],
                    },
                    {
                        "prompt": "The band is decided on which rate — the one that gets returned, or the one before rounding?",
                        "hole": "rate",
                        "opts": ["round(rate, 2)", "rate", "round(rate)", "base_rate(weight)"],
                        "a": 1,
                        "why": "`legacy_quote` computes `band` from `rate` and only rounds inside the `return`, so the band is decided on the unrounded value. The two disagree whenever the rate sits in the last half-penny below a boundary: 9.9961 bands as A and then prints as 10.0, which *looks* like a B. Preserving that is the job here; deciding it is a bug is a later conversation.",
                        "whys": [
                            "Rounding first pushes every rate in the last half-penny below a boundary up into the next band. It is arguably the more defensible rule, and it is not the one the code implements.",
                            "`legacy_quote` computes `band` from `rate` and only rounds inside the `return`, so the band is decided on the unrounded value. The two disagree whenever the rate sits in the last half-penny below a boundary: 9.9961 bands as A and then prints as 10.0, which *looks* like a B. Preserving that is the job here; deciding it is a bug is a later conversation.",
                            "Rounding to a whole unit moves the boundaries by up to half a unit in either direction, which changes far more cases than rounding to pennies would.",
                            "`base_rate(weight)` is the charge before distance, fragility and priority. Banding on it would ignore most of the price — an 800 km fragile next-day parcel would band as though it were going next door.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "Running the nest by hand",
                "minutes": 8,
                "figure": "`legacy_quote(12.0, 800, True, \"next-day\")` — a 12 kg fragile parcel, 800 km, next-day",
                "brief": r'''
Before you can characterise something you have to be able to read it, and the only
honest test of whether you have read this nest correctly is to run it in your head
and get the same number the machine gets.

```python
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
                ...
                return (round(rate, 2), band)
```

The four adjustments apply in the order the nest applies them, and the order
matters: `* 1.25` then `* 1.6 + 3.0` is not the same as the other way round.
''',
                "prompt": "What rate does `legacy_quote(12.0, 800, True, \"next-day\")` return?",
                "note": "The rate only, rounded to two decimals. Ignore the band.",
                "given": [
                    {"label": "weight", "value": "12.0 kg"},
                    {"label": "distance", "value": "800 km"},
                    {"label": "fragile", "value": "True"},
                    {"label": "priority", "value": "next-day"},
                ],
                "answer": 74.4,
                "tol": 0.01,
                "unit": "",
                "hint": "Four steps, in nest order: the weight band, then the distance surcharge, then the fragile multiplier, then the priority uplift. Nothing is rounded until the return.",
                "wrong": "The two easy slips are taking the wrong weight band — 12 kg is in the 5–20 band, so it is 10.0 + 7 × 1.1, not 26.5 + something — and forgetting that next-day is a multiplier *and* a flat 3.00 on top.",
                "aside": "74.40 is at or above 60, so this parcel bands as D.",
                "why": r'''
Step by step, in the order the nest applies them:

- **weight band** — 12 is not under 1 and not under 5, but it is under 20, so
  `rate = 10.0 + (12 - 5) * 1.1 = 10.0 + 7.7 = 17.70`.
- **distance** — 800 is over 100 and also over 500, so the far-band form applies:
  `17.70 + 12.0 + (800 - 500) * 0.02 = 17.70 + 12.0 + 6.0 = 35.70`.
- **fragile** — it is fragile and 12 kg is at or above 5, so the heavier uplift
  applies: `35.70 * 1.25 = 44.625`.
- **priority** — next-day is a multiplier and a fixed charge:
  `44.625 * 1.6 + 3.0 = 71.40 + 3.0 = 74.40`.

Rounded at the return, that is **74.40**, and since it is at or above 60 the band
is D. Notice what running it by hand costs: four nested lookups, and one wrong
turn at any of them changes the answer without changing its plausibility. That
opacity is the reason the flat version is worth having, and the reason the safety
net gets built before anything is touched.
''',
            },
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
            "quiz": {
                "title": "Patterns, and the forces that justify them",
                "minutes": 7,
                "questions": [
                    {
                        "q": "`PricingStrategy` subclasses `abc.ABC` and marks `price` with `@abc.abstractmethod`. What does `PricingStrategy()` do?",
                        "opts": [
                            "Returns an object whose `price` returns `None`",
                            "Raises `TypeError` at construction",
                            "Raises `NotImplementedError` on the first call to `price`",
                            "Raises `AttributeError`, because `price` has no body",
                        ],
                        "a": 1,
                        "why": r"""
`ABCMeta` refuses to construct any class whose `__abstractmethods__` set is still
non-empty, so the failure lands at the point where the mistake was made rather than
at the first call to `price` — which might be an hour into a batch job. It is worth
knowing what does *not* do this: a plain base class whose `price` raises
`NotImplementedError` instantiates perfectly happily and only complains later, and
an `abc.ABC` subclass that has overridden every abstract method is fully
constructible, which is exactly what makes `FlatPricing` legal.
""",
                    },
                    {
                        "q": "The checkout used to hold `if kind == \"flat\": ... elif kind == \"tiered\": ...`. A strategy object replaces it. Where did the conditional go?",
                        "opts": [
                            "Into one place that decides which object to build, run once when the strategy is constructed",
                            "It is gone entirely — polymorphism means there is no conditional left anywhere",
                            "Into each strategy, which now has to check which kind it is",
                            "Into `place`, which must now be told the kind on every call",
                        ],
                        "a": 0,
                        "why": r"""
The branch does not evaporate; it gets confined. Something has to turn the string
`"tiered"` into a `TieredPricing`, and in the lab that something is a single
`REGISTRY` lookup, performed once, in a function with no pricing logic in it at
all. What has been bought is that the decision now happens once per strategy rather
than once per price, and that adding a kind touches one line in one place.
`Checkout.place` never learns which strategy it is holding, which is the actual
test of whether the refactoring worked.
""",
                    },
                    {
                        "q": "A subscriber raises inside `publish`. Why does the bus record the failure and carry on rather than letting it propagate?",
                        "opts": [
                            "The publisher does not know its subscribers, so it is in no position to decide that one failure invalidates the others",
                            "Because raising out of a loop would leave the list of handlers in an inconsistent state",
                            "Because the payload has already been delivered, so nothing can fail",
                            "Because exception handling is faster than the alternative",
                        ],
                        "a": 0,
                        "why": r"""
Not knowing its subscribers is what makes the observer worth having, and it is also
what makes the publisher unqualified to judge. Let the exception out and whichever
handler happens to be registered third can silently cancel the fourth, with the
ordering decided by an accident of import order. So each handler is isolated. The
price is that the failure is now invisible, which is exactly why it goes into
`bus.errors` with the event and the handler's name rather than into a bare
`except: pass` — a swallowed error nobody can find is a worse bug than the one it
came from.
""",
                    },
                    {
                        "q": "A new pricing kind is added by writing `REGISTRY[\"free\"] = lambda spec: FreePricing()`. Which claim is that evidence for?",
                        "opts": [
                            "Open for extension, closed for modification: behaviour arrived without editing `make_strategy`",
                            "That `make_strategy` has become a pure function",
                            "That the registry removes the need for the abstract base class",
                            "That the `free` kind will be chosen automatically when no other kind matches",
                        ],
                        "a": 0,
                        "why": r"""
One line of new code, no line of existing code touched, and a new capability in the
system: that is open-closed in its practical form. Note what it is *not* evidence
for. `make_strategy` mutates nothing but reads a module-level dict, so it is not
pure — and the moment somebody registers a kind, the dict is global mutable state
with all the ordering hazards that implies. The base class is doing separate work,
guaranteeing that whatever comes out of the registry actually has a `price`. And
nothing about a registry entry makes it a default; an unknown kind still raises.
""",
                    },
                    {
                        "q": "A codebase has exactly one pricing rule and no plausible second one on the horizon. What is a strategy hierarchy for it?",
                        "opts": [
                            "Debt: an indirection with no force to resolve, paid for on every read",
                            "Correct, since a pattern is always preferable to a conditional",
                            "Necessary, because a single concrete class cannot be unit tested",
                            "Free, since the extra classes cost nothing at run time",
                        ],
                        "a": 0,
                        "why": r"""
The run-time cost is not the point and never was. The cost is a reader following an
interface to a single implementation, discovering there was never a choice to make,
and having learned nothing for the trip. Patterns name *forces* — a variation that
actually varies, a dependency that actually needs inverting — and a pattern applied
where the force is absent has all of the cost and none of the payoff. The honest
version of this is to write the one rule plainly and introduce the interface on the
day the second rule arrives, which is a small refactoring and a well-understood one.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Three patterns, five decisions",
                "minutes": 9,
                "caption": "main.py — the skeleton of the pricing engine",
                "lang": "python",
                "brief": r'''
Each of these holes is the line that makes its pattern actually work. Get any of
them wrong and the code still runs, still looks like the pattern, and quietly does
not deliver what the pattern promises — an abstract class that instantiates, a
registry that has to be edited to be extended, a bus that loses a subscriber
halfway through.

Nothing is executed here. Choose the line, then read the surrounding block back and
check that it now says what the pattern's name claims.
''',
                "listing": r'''
import abc


class PricingStrategy(abc.ABC):
    """The strategy interface: price a number of units."""

    @abc.___
    def price(self, units):
        """The charge for this many units."""


REGISTRY = {
    "flat": lambda spec: FlatPricing(spec["unit_price"]),
    "tiered": lambda spec: TieredPricing(spec["tiers"]),
}


def make_strategy(spec):
    """Build a strategy from a plain dict, without knowing the kinds."""
    kind = spec.get("kind")
    if kind not in ___:
        raise ValueError("unknown pricing kind: " + repr(kind))
    return ___


class EventBus:
    """Publishers know events. They never know their subscribers."""

    def publish(self, event, payload):
        """Deliver payload to every subscriber; returns how many were invoked."""
        delivered = 0
        for handler in ___(self._handlers.get(event, [])):
            delivered += 1
            try:
                handler(payload)
            except ___ as exc:
                name = getattr(handler, "__name__", repr(handler))
                self.errors.append((event, name, str(exc)))
        return delivered
''',
                "blanks": [
                    {
                        "prompt": "Which is the *current* spelling that makes `PricingStrategy()` refuse to build?",
                        "hole": "decorator",
                        "opts": ["abstractmethod", "abstractproperty", "staticmethod", "abstractclassmethod"],
                        "a": 0,
                        "why": "`@abc.abstractmethod` puts the name into `__abstractmethods__`, and `ABCMeta` refuses to construct any class where that set is non-empty. It is also the only spelling here that is still current: `abc.abstractproperty` and `abc.abstractclassmethod` set `__isabstractmethod__` too and would block construction just as well, but both have been deprecated since Python 3.3. Leave the decorator off altogether and `abc.ABC` is an ordinary base class — `PricingStrategy()` succeeds and hands you an object whose `price` returns `None`.",
                        "whys": [
                            "`@abc.abstractmethod` puts the name into `__abstractmethods__`, and `ABCMeta` refuses to construct any class where that set is non-empty. It is also the only spelling here that is still current: `abc.abstractproperty` and `abc.abstractclassmethod` set `__isabstractmethod__` too and would block construction just as well, but both have been deprecated since Python 3.3. Leave the decorator off altogether and `abc.ABC` is an ordinary base class — `PricingStrategy()` succeeds and hands you an object whose `price` returns `None`.",
                            "`abc.abstractproperty` does set `__isabstractmethod__`, so `PricingStrategy()` genuinely would refuse to build under it — that is not what is wrong with it. It has been deprecated since Python 3.3, and it declares `price` as a property: an attribute the base says you read, rather than a method you call with `units`. A subclass can still satisfy it with an ordinary `def price(self, units)`, which is the trap — the base ends up documenting a shape nothing follows.",
                            "There is no `abc.staticmethod`. The module exports `abstractmethod`, `abstractproperty`, `abstractclassmethod` and `abstractstaticmethod`; plain `staticmethod` is a builtin, not an `abc` attribute. `@abc.staticmethod` raises `AttributeError` while the class body is still being evaluated, so the module never imports and no class is created at all.",
                            "`abc.abstractclassmethod` sets `__isabstractmethod__` as well, so it too would keep `PricingStrategy()` from building. It has been deprecated since Python 3.3 — the replacement is `classmethod` stacked on `abstractmethod` — and it declares `price` as a classmethod, bound to the class, with no instance in that shape to read a `unit_price` from. A subclass is free to define an ordinary method anyway and the declaration is satisfied, which is the trap again: a contract the base states and nothing enforces.",
                        ],
                    },
                    {
                        "prompt": "The check that decides whether this kind is known.",
                        "hole": "in what",
                        "opts": ["spec", "PricingStrategy", "REGISTRY.values()", "REGISTRY"],
                        "a": 3,
                        "why": "`kind not in REGISTRY` tests the dictionary's keys, and those keys are exactly the set of kinds that exist. The guard and the lookup on the next line consult the same object, so they can never disagree about what is registered — which is what makes registering a new kind sufficient.",
                        "whys": [
                            "`kind not in spec` asks whether the string `\"flat\"` is a key of the spec dict. It is not — `\"kind\"` is — so every well-formed spec would be rejected as unknown.",
                            "`PricingStrategy` is a class, and `in` on a class raises `TypeError` rather than testing membership of anything.",
                            "`REGISTRY.values()` holds the factory callables, not their names. A string is never in there, so every call would raise, including the valid ones.",
                            "`kind not in REGISTRY` tests the dictionary's keys, and those keys are exactly the set of kinds that exist. The guard and the lookup on the next line consult the same object, so they can never disagree about what is registered — which is what makes registering a new kind sufficient.",
                        ],
                    },
                    {
                        "prompt": "Turn the spec into an actual strategy object.",
                        "hole": "build",
                        "opts": ["REGISTRY[kind](spec)", "REGISTRY[kind]", "REGISTRY[spec](kind)", "REGISTRY[kind](**spec)"],
                        "a": 0,
                        "why": "Look the factory up by kind, then call it with the whole spec. Each factory knows which keys it needs — `FlatPricing` wants `unit_price`, `TieredPricing` wants `tiers` — so `make_strategy` never has to know, and that ignorance is what lets it stay closed to modification.",
                        "whys": [
                            "Look the factory up by kind, then call it with the whole spec. Each factory knows which keys it needs — `FlatPricing` wants `unit_price`, `TieredPricing` wants `tiers` — so `make_strategy` never has to know, and that ignorance is what lets it stay closed to modification.",
                            "This returns the `lambda` itself rather than calling it. The caller receives a function where it expected a strategy, and finds out at `strategy.price(units)`, a long way from here.",
                            "The subscript and the argument have been swapped. A dict is unhashable, so this raises `TypeError` before it gets anywhere near building a strategy.",
                            "`**spec` spreads the spec into keyword arguments, so every factory would also receive `kind=\"flat\"` and every one of them would have to accept and ignore it. Passing the dict whole keeps that coupling out of the factories.",
                        ],
                    },
                    {
                        "prompt": "Iterate over what, exactly?",
                        "hole": "wrap",
                        "opts": ["sorted", "iter", "list", "set"],
                        "a": 2,
                        "why": "A snapshot. A handler is entitled to unsubscribe itself while it is running, and mutating a list you are iterating skips the following entry without saying a word. `list(...)` copies, so the publish delivers to exactly the set of subscribers that existed when it began.",
                        "whys": [
                            "`sorted` has to compare the handlers, and functions do not support `<` — so this raises `TypeError` as soon as a second subscriber appears. It would also throw away the subscription order the bus promises.",
                            "`iter` hands back a cursor over the live list rather than a copy, so a handler that unsubscribes during delivery still corrupts the walk. It looks like a defensive wrapper and defends against nothing.",
                            "A snapshot. A handler is entitled to unsubscribe itself while it is running, and mutating a list you are iterating skips the following entry without saying a word. `list(...)` copies, so the publish delivers to exactly the set of subscribers that existed when it began.",
                            "`set` loses the delivery order the bus documents, and it would silently collapse a handler that had been subscribed twice into one — a real pattern when two modules independently register the same logger.",
                        ],
                    },
                    {
                        "prompt": "How wide should the net around one handler be?",
                        "hole": "catch",
                        "opts": ["BaseException", "Exception", "ValueError", "Error"],
                        "a": 1,
                        "why": "`Exception` catches everything a handler can plausibly go wrong with and nothing else. It deliberately excludes `KeyboardInterrupt` and `SystemExit`, which sit under `BaseException` and are the user or the runtime asking the process to stop.",
                        "whys": [
                            "`BaseException` also catches `KeyboardInterrupt` and `SystemExit`. Ctrl-C during a publish would be filed as a subscriber error and the loop would carry on to the next handler — an unkillable process, built by a line meant to add robustness.",
                            "`Exception` catches everything a handler can plausibly go wrong with and nothing else. It deliberately excludes `KeyboardInterrupt` and `SystemExit`, which sit under `BaseException` and are the user or the runtime asking the process to stop.",
                            "`ValueError` isolates one kind of failure and lets every other kind escape, so a subscriber raising `KeyError` still takes the whole publish down. The isolation would hold only for the failures somebody thought of in advance.",
                            "There is no built-in named `Error` in Python, so this raises `NameError` the moment a handler fails — from inside the code written to handle handlers failing.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Where the subscription stops paying",
                "minutes": 12,
                "vars": ["u", "p", "m", "c", "n"],
                "brief": r'''
Two strategies, one customer. `FlatPricing(p)` charges $p$ per unit for ever.
`SubscriptionPricing(m, n, c)` charges $m$ a month, which covers $n$ units, and
then $c$ for every unit beyond that.

A pricing engine exists so that somebody can answer *which of these is cheaper for
me?* — so work out the crossover. Take $u$ for the number of units.
''',
                "steps": [
                    {
                        "prompt": r"Write the flat strategy's charge for $u$ units.",
                        "answer": r"p \cdot u",
                        "hint": r"`FlatPricing.price` is a single multiplication, and there is no quota in it.",
                        "deconstruct": [
                            r"Every unit costs the same $p$, whatever $u$ is.",
                            r"So the bill is $p$ added to itself $u$ times.",
                        ],
                    },
                    {
                        "prompt": r"Now the subscription, for a customer who is *over* the quota — that is, $u \ge n$. Write its charge.",
                        "answer": r"m + c \cdot (u - n)",
                        "hint": r"The monthly fee is paid whatever happens; the overage is charged only on the units past $n$.",
                        "deconstruct": [
                            r"$m$ is owed before a single unit is used.",
                            r"The units beyond the quota number $u - n$, and each costs $c$.",
                        ],
                    },
                    {
                        "prompt": r"Set the two charges equal and solve for $u$: the crossover, still assuming $u \ge n$.",
                        "given": r"$p u = m + c(u - n)$.",
                        "answer": r"\frac{m - c \cdot n}{p - c}",
                        "hint": r"Collect the $u$ terms on one side. Everything else is a constant.",
                        "deconstruct": [
                            r"Expand the right-hand side: $p u = m + c u - c n$.",
                            r"Move $c u$ across: $u(p - c) = m - c n$.",
                            r"Divide by $(p - c)$, which is positive whenever the overage rate undercuts the flat rate.",
                        ],
                    },
                    {
                        "prompt": r"Below the quota the subscription costs just the flat fee $m$, however few units are used. Set $p u = m$ and solve for $u$ — the crossover in *that* region.",
                        "answer": r"\frac{m}{p}",
                        "hint": r"With no overage there is no $c$ and no $n$ left in the equation.",
                        "deconstruct": [
                            r"For $u < n$ the subscription's charge does not depend on $u$ at all: it is $m$.",
                            r"So the flat strategy is cheaper exactly while $p u < m$.",
                        ],
                    },
                ],
                "closing": r'''
Now put the lab's numbers in, and watch the interesting thing happen. With
$m = 99$, $n = 50$, $c = 1.75$ and $p = 2.50$, the crossover from the third step is
$(99 - 87.5)/0.75 = 15.33$ units — but 15.33 is **below** the quota of 50, so the
assumption $u \ge n$ that produced the formula does not hold there. That root is
spurious. It is a real solution of an equation that describes a region it does not
lie in.

The fourth step gives $99/2.5 = 39.6$ units, and 39.6 *is* below 50, so that one is
genuine: under 40 units the flat rate wins, and from 40 upwards the subscription
does. Check it by hand if you like — at 39 units flat costs 97.50 against 99.00,
and at 40 units it costs 100.00 against the same 99.00.

A closed form is only true inside the case that produced it, and a piecewise
function has one closed form per piece. That is module 1's boundary discipline
again, in algebra rather than in examples: the answer is not the formula, it is the
formula plus the region it is valid in.
''',
            },
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
            "quiz": {
                "title": "Counting branches, and reading a diff",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A function contains one `if`, one `for`, and the expression `a and b or c`. What is its cyclomatic complexity under the rules in this module?",
                        "opts": ["4", "3", "5", "6"],
                        "a": 2,
                        "why": r"""
Start at 1, add 1 for the `if` and 1 for the `for`, and then apply the boolean rule:
each boolean operation adds `len(values) - 1`. `a and b or c` parses as
`(a and b) or c`, which is *two* nodes — an `or` over two values and an `and` over
two values — so it contributes 2, not 1. That totals 5. The reason booleans count at
all is short-circuiting: `b` is evaluated on some paths and skipped on others, and a
piece of code that can be skipped is a branch whether or not it was spelled with an
`if`.
""",
                    },
                    {
                        "q": "A function contains a chain of `if` / `elif` / `elif` / `else`. How much does that chain add?",
                        "opts": ["3", "1", "4", "2"],
                        "a": 0,
                        "why": r"""
Python's grammar has no `elif` node. The parser nests each one as an `If` inside the
previous one's `orelse`, so the chain is three `If` nodes and the rule counts them
one apiece. The `else` adds nothing, because it is not a decision — it is where
control goes once every decision has already been made. That is also why the lab's
scorer needs no special case for `elif`: walking the tree finds three `If`s without
being told to look for them.
""",
                    },
                    {
                        "q": "`quality_gate(source, 3)` returns `[(\"Router.dispatch\", 6), (\"guarded\", 4)]`. What does the 3 mean?",
                        "opts": [
                            "Anything strictly above 3 is reported; a function scoring exactly 3 passes",
                            "Anything scoring 3 or more is reported",
                            "At most three functions may fail before the build is broken",
                            "Only the three worst functions are examined",
                        ],
                        "a": 0,
                        "why": r"""
The gate keeps `score > limit`, so 3 is the highest score that still passes. That
choice has to be written down somewhere a reader will find it, because *limit 3* is
equally readable as *3 fails* and the difference is a whole band of functions. The
ordering matters for the same reason the threshold does: worst first, ties broken by
name, so the report is stable between runs. A gate whose output reorders itself
produces a diff on every build and gets ignored within a fortnight.
""",
                    },
                    {
                        "q": "A released function gains a new parameter that has no default. Which bump does the rule in this module require?",
                        "opts": ["minor", "major", "patch", "none — every existing call still works"],
                        "a": 1,
                        "why": r"""
Every existing call site is now short an argument, and in Python that is a
`TypeError` at the call. Widening a contract is compatible: a new *optional*
parameter is `minor`, because code written against the old surface still binds and
still runs. Narrowing it is not, and required is the narrowest a parameter can be.
The same asymmetry decides the rest of the table, which is why
`required-to-optional` is minor and `optional-to-required` is major even though
they describe the same parameter moving between the same two states.
""",
                    },
                    {
                        "q": "`connect(host, port)` becomes `connect(port, host)`, with both parameters still required. Why does the surface diff call that major?",
                        "opts": [
                            "Positional order is part of the contract, and every existing positional call now binds its arguments to the wrong parameters",
                            "It is minor: the names are unchanged, so callers are unaffected",
                            "It is a patch: nothing was added and nothing was removed",
                            "It depends on whether the two parameters have the same type",
                        ],
                        "a": 0,
                        "why": r"""
Callers using keywords do survive, and that is precisely what makes this dangerous
rather than merely broken: `connect("db.internal", 5432)` still runs, with the
string landing in `port` and the number landing in `host`. A `TypeError` would have
been a kindness. This is why `api_changes` compares the *surviving* required
parameters in order and raises `params-reordered` only when two that both still
exist have swapped — the one change in the table that no signature-level check at
the call site can rescue you from.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Five releases off 1.4.2",
                "minutes": 8,
                "caption": "One change per release, and the version it ships as",
                "lang": "text",
                "brief": r'''
`required_bump` decides the severity; `bump_version` decides the digits. Both have
to be right, and the second is where a surprising number of releases go wrong — a
minor bump zeroes the patch, and a major bump zeroes both.

Each row below is one change, shipped on its own from a library sitting at 1.4.2.
''',
                "listing": r'''
A library is released at 1.4.2. Each row is one change, shipped on its own.
What version does each release carry?

  removed the public connect(host, port) entirely        1.4.2 -> ___
  added an optional retries=3 to connect                 1.4.2 -> ___
  timeout was optional on send; it is now required       1.4.2 -> ___
  fixed an off-by-one inside send, signature unchanged   1.4.2 -> ___
  connect(host, port) became connect(port, host)         1.4.2 -> ___
''',
                "blanks": [
                    {
                        "prompt": "A public function disappears.",
                        "hole": "x.y.z",
                        "opts": ["2.0.0", "1.5.0", "1.4.3", "1.5.2"],
                        "a": 0,
                        "why": "`removed` is major, and a major bump zeroes both of the digits below it — 2.0.0, not 2.4.2. Every call site of `connect` stops working, which is what *breaks callers* means in the plainest possible form.",
                        "whys": [
                            "`removed` is major, and a major bump zeroes both of the digits below it — 2.0.0, not 2.4.2. Every call site of `connect` stops working, which is what *breaks callers* means in the plainest possible form.",
                            "A minor release announces *something was added and nothing broke*. Deleting a public function breaks every caller it had.",
                            "A patch release claims the surface did not move at all. A function that no longer exists is the largest move there is.",
                            "Wrong on both digits: the change is not minor, and a minor bump would have zeroed the patch in any case.",
                        ],
                    },
                    {
                        "prompt": "A new parameter arrives, carrying a default.",
                        "hole": "x.y.z",
                        "opts": ["2.0.0", "1.5.0", "1.4.3", "1.5.2"],
                        "a": 1,
                        "why": "Widening: every call written against 1.4.2 still binds, because the new parameter supplies its own value. That is `optional-param-added`, which is minor — and a minor bump resets the patch to zero.",
                        "whys": [
                            "A major bump would be right if the parameter had no default, since every existing call would then be short an argument. With a default, none of them is.",
                            "Widening: every call written against 1.4.2 still binds, because the new parameter supplies its own value. That is `optional-param-added`, which is minor — and a minor bump resets the patch to zero.",
                            "A patch release claims the surface did not change. It did: there is a name in the signature that was not there before, and callers may now pass it.",
                            "The severity is right and the arithmetic is not. A minor bump resets the patch to zero, so the trailing 2 cannot survive.",
                        ],
                    },
                    {
                        "prompt": "A parameter that had a default no longer has one.",
                        "hole": "x.y.z",
                        "opts": ["2.0.0", "1.5.0", "1.4.3", "1.5.2"],
                        "a": 0,
                        "why": "`optional-to-required` is major. Every call that relied on the default is now missing an argument, and it fails with a `TypeError` at the call site — including calls in code nobody on the team can see.",
                        "whys": [
                            "`optional-to-required` is major. Every call that relied on the default is now missing an argument, and it fails with a `TypeError` at the call site — including calls in code nobody on the team can see.",
                            "A minor release is the bump for widening a contract. Taking a default away narrows it: fewer call shapes are legal than were legal before.",
                            "A patch release says nothing observable changed. Calls that used to work now raise, which is about as observable as it gets.",
                            "Neither digit survives scrutiny: the change is major, and a minor bump would have zeroed the patch.",
                        ],
                    },
                    {
                        "prompt": "The behaviour was wrong; the signature is untouched.",
                        "hole": "x.y.z",
                        "opts": ["2.0.0", "1.5.0", "1.4.3", "1.5.2"],
                        "a": 2,
                        "why": "`api_changes` finds nothing at all, so `required_bump` falls through to patch and 1.4.2 becomes 1.4.3. This is the row worth arguing about: if callers have come to depend on the bug, the fix breaks them — but semantic versioning is defined over the *declared* contract, and the declared contract always said the function was correct.",
                        "whys": [
                            "A major bump is for changes that break the declared contract. This one restores it. If callers had come to rely on the defect that is a genuine problem, and it is a problem semantic versioning does not attempt to model.",
                            "A minor release announces new surface. There is none here: no function, no parameter, nothing a caller can do that it could not do before.",
                            "`api_changes` finds nothing at all, so `required_bump` falls through to patch and 1.4.2 becomes 1.4.3. This is the row worth arguing about: if callers have come to depend on the bug, the fix breaks them — but semantic versioning is defined over the *declared* contract, and the declared contract always said the function was correct.",
                            "This raises the minor digit for a release that added no surface, and leaves the patch digit exactly where it was — the one digit that should have moved.",
                        ],
                    },
                    {
                        "prompt": "Two required parameters swap places.",
                        "hole": "x.y.z",
                        "opts": ["2.0.0", "1.5.0", "1.4.3", "1.5.2"],
                        "a": 0,
                        "why": "`params-reordered` is major. Positional callers keep running and start passing the port where the host belongs, which is worse than a crash, because nothing announces it and the failure surfaces somewhere else entirely.",
                        "whys": [
                            "`params-reordered` is major. Positional callers keep running and start passing the port where the host belongs, which is worse than a crash, because nothing announces it and the failure surfaces somewhere else entirely.",
                            "A minor release says callers are safe. Only the ones already passing keywords are, and no library gets to assume that of everybody.",
                            "A patch release says the surface is unchanged. The names are unchanged; the order is not, and order is what a positional call binds by.",
                            "Wrong severity, and a minor bump would have zeroed the patch even if the severity had been right.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "Scoring one function by hand",
                "minutes": 8,
                "figure": "`normalise(records, strict=False)` — one loop, one `try`, one conditional expression, one comprehension",
                "brief": r'''
A gate nobody can reproduce by hand is a gate nobody trusts. Score this function
the way `cyclomatic_complexity` will score it, then check the tool against yourself
rather than the other way round.

```python
def normalise(records, strict=False):
    out = []
    for row in records:
        if row is None or not row.get("id"):
            continue
        try:
            value = int(row["value"])
        except (TypeError, ValueError):
            if strict:
                raise
            value = 0
        out.append((row["id"], value if value >= 0 else 0))
    return [r for r in out if r[1] > 0]
```

Watch for the three that are easy to walk past: the `or`, the comprehension, and
the `if` inside it.
''',
                "prompt": "What is the cyclomatic complexity of `normalise`?",
                "note": "One whole number. Score it under the rules in the table, not under any other tool's conventions.",
                "given": [
                    {"label": "a function starts at", "value": "1"},
                    {"label": "each `if`, `for`, `while`, `except`, `assert`", "value": "+1"},
                    {"label": "each conditional expression `a if c else b`", "value": "+1"},
                    {"label": "each boolean operation", "value": "+ len(values) - 1"},
                    {"label": "each comprehension clause", "value": "+1, and +1 per `if` in it"},
                ],
                "answer": 9,
                "tol": 0,
                "unit": "",
                "hint": "Six lines carry decisions and four of them are not `if` statements — and two of those six are worth two points rather than one. The `try` itself scores nothing; it is the handler that counts.",
                "wrong": "The two commonest slips are counting `except (TypeError, ValueError)` twice, once per exception class — it is one handler, so it is one point — and forgetting that a comprehension scores for its `for` clause as well as for its filter.",
                "aside": "Under a limit of 8 this function fails the gate; under a limit of 10 it passes with room to spare.",
                "why": r'''
Start at **1**, then add:

- `for row in records:` — **+1** (2)
- `if row is None or not ...:` — **+1** for the `if` (3)
- the `or` in that condition, two values — **+1** (4)
- `except (TypeError, ValueError):` — **+1** for the handler, and only one: it is a
  single `except` clause that happens to name two classes (5)
- `if strict:` — **+1** (6)
- `value if value >= 0 else 0` — **+1** for the conditional expression (7)
- `[r for r in out if r[1] > 0]` — **+1** for the comprehension clause (8) and
  **+1** for its filter (9)

That is **9**. What scores nothing is as instructive as what does: `try` on its own
is not a branch, `continue` and `raise` are jumps rather than decisions, `not` is an
operator, and `r[1] > 0` is a comparison — the point is scored by the `if` that
uses it, not by the comparison itself. Nine on twelve lines is also a fair warning
that the metric is blunt: this function is perfectly readable, and it would fail a
gate set at 8.
''',
            },
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
