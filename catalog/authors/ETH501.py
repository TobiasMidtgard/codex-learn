"""ETH501 — Ethics, Policy & Technology Law."""

COURSE = {
    "id": "ETH501",
    "title": "Ethics, Policy & Technology Law",
    "year": 5,
    "level": "Intermediate",
    "prereqs": ["SE201", "ML401"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 110,
    "icon": "⚖",
    "summary": (
        "Obligations that arrive as prose — non-discrimination, data protection, "
        "transparency — have to leave as code that runs in a pipeline. You build the "
        "audit tooling: fairness metrics computed from per-group confusion matrices, a "
        "k-anonymity and differential-privacy checker, a data-subject-request handler "
        "with retention and legal-hold rules, and a tamper-evident audit log."
    ),
    "outcomes": [
        "Compute demographic parity, equal opportunity, equalised odds and calibration from group confusion matrices",
        "Demonstrate arithmetically why calibration and equalised odds cannot both hold across unequal base rates",
        "Measure k-anonymity and l-diversity, and quantify what a generalisation step costs in utility",
        "Implement the Laplace mechanism and account for an epsilon budget across several queries",
        "Implement access, rectification and erasure requests against a record store with retention and legal-hold exceptions",
        "Emit a model card and a hash-chained audit log in which any later edit is detectable",
        "Choose a defensible threshold and record the reason it was chosen, rather than reporting a number alone",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Barocas, Hardt & Narayanan, *Fairness and Machine Learning: Limitations and Opportunities*, MIT Press 2023 — chapters 2-3",
        "Dwork & Roth, *The Algorithmic Foundations of Differential Privacy*, FnTTCS 9(3-4), 2014 — chapters 2-3",
        "Regulation (EU) 2016/679 (GDPR) — Articles 5, 15, 16, 17 and Recital 26",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Fairness metrics and their incompatibility",
            "summary": "Four group criteria from one confusion matrix each, and a proof that two of them clash.",
            "concepts": [
                "A protected attribute partitions the evaluation set; every metric below is computed per group and then compared",
                "Demographic parity constrains the selection rate P(Ŷ=1) and ignores the outcome entirely",
                "Equal opportunity constrains the true positive rate; equalised odds constrains TPR and FPR together",
                "Calibration within a score bin is equality of the positive predictive value P(Y=1 | Ŷ=1)",
                "The base rate P(Y=1) is a property of the world, not of the classifier",
                "Chouldechova's identity: fixing TPR and FPR fixes PPV as a function of the base rate alone",
                "Reporting a gap without a threshold and a justification for that threshold is not an audit",
            ],
            "lab": {
                "title": "A group-fairness metric suite",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Evaluation data arrives as rows: `{"group": "A", "y_true": 1, "y_pred": 0}`, where
`1` means the positive class and `1` in `y_pred` means the model selected the row.

**`confusion_matrices(rows)`** — `{group: {"tp": .., "fp": .., "fn": .., "tn": ..}}`.
Raise `ValueError` for a label that is not `0` or `1`, or a row missing a key.

**`rates(cm)`** — from one confusion matrix, a dict:

```text
base_rate       (tp + fn) / n        what fraction really are positive
selection_rate  (tp + fp) / n        what fraction the model selected
tpr             tp / (tp + fn)       true positive rate
fpr             fp / (fp + tn)       false positive rate
ppv             tp / (tp + fp)       positive predictive value
```

A rate with a zero denominator is `None`, not zero — the group carries no evidence
about it. Raise `ValueError` when the matrix is empty.

**`gap(cms, key)`** — the largest minus the smallest value of `rates(...)[key]`
across groups. One group gives `0.0`. Raise `ValueError` when any group's value
is `None`, naming the group and the rate.

Then four one-line wrappers: **`demographic_parity_gap`** on `selection_rate`,
**`equal_opportunity_gap`** on `tpr`, **`calibration_gap`** on `ppv`, and
**`equalised_odds_gap`**, which is the larger of the `tpr` and `fpr` gaps.

**`ppv_from_rates(base_rate, tpr, fpr)`** — Chouldechova's identity:

```text
ppv = b·tpr / ( b·tpr + (1 − b)·fpr )
```

Raise `ValueError` for an argument outside `[0, 1]`, or when the denominator is
zero (the model selected nobody).

**`impossibility_demo(base_a, base_b, tpr, fpr)`** — hold equalised odds by giving
both groups the same `tpr` and `fpr`, then return

```text
{"ppv_a": .., "ppv_b": .., "calibration_gap": .., "calibrated": bool}
```

`calibrated` is `True` only when the two PPVs agree to within `1e-9`. Equal base
rates make it `True`; unequal base rates make it `False`, and no choice of
threshold repairs that.
''',
                "files": [{"name": "main.py", "content": r'''
def confusion_matrices(rows):
    """group -> {"tp": int, "fp": int, "fn": int, "tn": int}."""
    # your code here


def rates(cm):
    """One confusion matrix -> the five rates; None where undefined."""
    # your code here


def gap(cms, key):
    """max - min of rates(...)[key] across groups. ValueError when undefined."""
    # your code here


def demographic_parity_gap(cms):
    """Spread of the selection rate."""
    # your code here


def equal_opportunity_gap(cms):
    """Spread of the true positive rate."""
    # your code here


def equalised_odds_gap(cms):
    """The larger of the TPR and FPR spreads."""
    # your code here


def calibration_gap(cms):
    """Spread of the positive predictive value."""
    # your code here


def ppv_from_rates(base_rate, tpr, fpr):
    """PPV implied by a base rate and an error profile."""
    # your code here


def impossibility_demo(base_a, base_b, tpr, fpr):
    """Two groups under identical error rates. Are they also calibrated?"""
    # your code here


ROWS = ([{"group": "A", "y_true": 1, "y_pred": 1}] * 30
        + [{"group": "A", "y_true": 0, "y_pred": 1}] * 20
        + [{"group": "A", "y_true": 1, "y_pred": 0}] * 10
        + [{"group": "A", "y_true": 0, "y_pred": 0}] * 40
        + [{"group": "B", "y_true": 1, "y_pred": 1}] * 10
        + [{"group": "B", "y_true": 0, "y_pred": 1}] * 10
        + [{"group": "B", "y_true": 1, "y_pred": 0}] * 30
        + [{"group": "B", "y_true": 0, "y_pred": 0}] * 50)

CMS = confusion_matrices(ROWS)
print(demographic_parity_gap(CMS), equal_opportunity_gap(CMS))
print(impossibility_demo(0.1, 0.5, 0.8, 0.2))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def confusion_matrices(rows):
    """group -> {"tp": int, "fp": int, "fn": int, "tn": int}."""
    out = {}
    for row in rows:
        for key in ("group", "y_true", "y_pred"):
            if key not in row:
                raise ValueError(f"row is missing {key!r}: {row!r}")
        truth, pred = row["y_true"], row["y_pred"]
        if truth not in (0, 1) or pred not in (0, 1):
            raise ValueError(f"labels must be 0 or 1, got {truth!r} and {pred!r}")
        cm = out.setdefault(row["group"], {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
        if truth == 1 and pred == 1:
            cm["tp"] += 1
        elif truth == 0 and pred == 1:
            cm["fp"] += 1
        elif truth == 1 and pred == 0:
            cm["fn"] += 1
        else:
            cm["tn"] += 1
    return out


def _ratio(num, den):
    """None rather than zero: an absent denominator carries no evidence."""
    return None if den == 0 else num / den


def rates(cm):
    """One confusion matrix -> the five rates; None where undefined."""
    tp, fp, fn, tn = cm["tp"], cm["fp"], cm["fn"], cm["tn"]
    n = tp + fp + fn + tn
    if n == 0:
        raise ValueError("an empty confusion matrix has no rates")
    return {
        "base_rate": (tp + fn) / n,
        "selection_rate": (tp + fp) / n,
        "tpr": _ratio(tp, tp + fn),
        "fpr": _ratio(fp, fp + tn),
        "ppv": _ratio(tp, tp + fp),
    }


def gap(cms, key):
    """max - min of rates(...)[key] across groups. ValueError when undefined."""
    if not cms:
        raise ValueError("no groups to compare")
    values = []
    for group in sorted(cms):
        value = rates(cms[group])[key]
        if value is None:
            raise ValueError(f"{key} is undefined for group {group!r}")
        values.append(value)
    return max(values) - min(values)


def demographic_parity_gap(cms):
    """Spread of the selection rate."""
    return gap(cms, "selection_rate")


def equal_opportunity_gap(cms):
    """Spread of the true positive rate."""
    return gap(cms, "tpr")


def equalised_odds_gap(cms):
    """The larger of the TPR and FPR spreads."""
    return max(gap(cms, "tpr"), gap(cms, "fpr"))


def calibration_gap(cms):
    """Spread of the positive predictive value."""
    return gap(cms, "ppv")


def ppv_from_rates(base_rate, tpr, fpr):
    """PPV implied by a base rate and an error profile."""
    for name, value in (("base_rate", base_rate), ("tpr", tpr), ("fpr", fpr)):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must lie in [0, 1], got {value!r}")
    selected = base_rate * tpr + (1 - base_rate) * fpr
    if selected == 0:
        raise ValueError("the model selects nobody, so PPV is undefined")
    return base_rate * tpr / selected


def impossibility_demo(base_a, base_b, tpr, fpr):
    """Two groups under identical error rates. Are they also calibrated?"""
    ppv_a = ppv_from_rates(base_a, tpr, fpr)
    ppv_b = ppv_from_rates(base_b, tpr, fpr)
    spread = abs(ppv_a - ppv_b)
    return {"ppv_a": ppv_a, "ppv_b": ppv_b,
            "calibration_gap": spread, "calibrated": spread < 1e-9}


ROWS = ([{"group": "A", "y_true": 1, "y_pred": 1}] * 30
        + [{"group": "A", "y_true": 0, "y_pred": 1}] * 20
        + [{"group": "A", "y_true": 1, "y_pred": 0}] * 10
        + [{"group": "A", "y_true": 0, "y_pred": 0}] * 40
        + [{"group": "B", "y_true": 1, "y_pred": 1}] * 10
        + [{"group": "B", "y_true": 0, "y_pred": 1}] * 10
        + [{"group": "B", "y_true": 1, "y_pred": 0}] * 30
        + [{"group": "B", "y_true": 0, "y_pred": 0}] * 50)

CMS = confusion_matrices(ROWS)
print(demographic_parity_gap(CMS), equal_opportunity_gap(CMS))
print(impossibility_demo(0.1, 0.5, 0.8, 0.2))
'''}],
                "hints": [
                    "`out.setdefault(group, {\"tp\": 0, \"fp\": 0, \"fn\": 0, \"tn\": 0})` gives you the counter dict to increment in one line.",
                    "Write one `_ratio(num, den)` helper that returns `None` when `den == 0`; every undefined rate then falls out of it.",
                    "`gap` should iterate `sorted(cms)` so the error message names groups in a stable order — audit output that changes between runs is not evidence.",
                    "In `ppv_from_rates` the denominator is the overall selection rate, `b·tpr + (1−b)·fpr`; the numerator is the part of it that is genuinely positive.",
                ],
                "tests": [
                    {"name": "confusion_matrices counts and validates", "code": r'''
_rows = [{"group": "A", "y_true": 1, "y_pred": 1},
         {"group": "A", "y_true": 0, "y_pred": 1},
         {"group": "A", "y_true": 1, "y_pred": 0},
         {"group": "B", "y_true": 0, "y_pred": 0}]
_cms = confusion_matrices(_rows)
assert _cms["A"] == {"tp": 1, "fp": 1, "fn": 1, "tn": 0}, f"group A came out {_cms['A']!r}"
assert _cms["B"] == {"tp": 0, "fp": 0, "fn": 0, "tn": 1}, f"group B came out {_cms['B']!r}"
assert confusion_matrices([]) == {}, "no rows means no groups"
for _bad in ([{"group": "A", "y_true": 2, "y_pred": 0}], [{"group": "A", "y_pred": 0}]):
    try:
        confusion_matrices(_bad)
        assert False, f"confusion_matrices({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "rates, including the undefined ones", "code": r'''
_r = rates({"tp": 30, "fp": 20, "fn": 10, "tn": 40})
assert abs(_r["base_rate"] - 0.40) < 1e-9, f"base_rate is {_r['base_rate']!r}"
assert abs(_r["selection_rate"] - 0.50) < 1e-9, f"selection_rate is {_r['selection_rate']!r}"
assert abs(_r["tpr"] - 0.75) < 1e-9, f"tpr is {_r['tpr']!r}"
assert abs(_r["fpr"] - 1 / 3) < 1e-9, f"fpr is {_r['fpr']!r}"
assert abs(_r["ppv"] - 0.60) < 1e-9, f"ppv is {_r['ppv']!r}"
_none = rates({"tp": 0, "fp": 0, "fn": 0, "tn": 7})
assert _none["tpr"] is None, "a group with no positives has no TPR — that is not zero"
assert _none["ppv"] is None, "a group with no selections has no PPV"
assert _none["fpr"] == 0.0, "seven true negatives do define an FPR of zero"
try:
    rates({"tp": 0, "fp": 0, "fn": 0, "tn": 0})
    assert False, "an empty matrix should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The four gaps on a worked example", "code": r'''
_cms = {"A": {"tp": 30, "fp": 20, "fn": 10, "tn": 40},
        "B": {"tp": 10, "fp": 10, "fn": 30, "tn": 50}}
assert abs(demographic_parity_gap(_cms) - 0.30) < 1e-9, f"got {demographic_parity_gap(_cms)!r}"
assert abs(equal_opportunity_gap(_cms) - 0.50) < 1e-9, f"got {equal_opportunity_gap(_cms)!r}"
assert abs(equalised_odds_gap(_cms) - 0.50) < 1e-9, f"got {equalised_odds_gap(_cms)!r}"
assert abs(calibration_gap(_cms) - 0.10) < 1e-9, f"got {calibration_gap(_cms)!r}"
assert abs(gap(_cms, "fpr") - (1 / 3 - 1 / 6)) < 1e-9, f"fpr gap is {gap(_cms, 'fpr')!r}"
'''},
                    {"name": "One group is trivially fair, and gaps refuse missing evidence", "code": r'''
_one = {"A": {"tp": 5, "fp": 5, "fn": 5, "tn": 5}}
for _f in (demographic_parity_gap, equal_opportunity_gap, equalised_odds_gap, calibration_gap):
    assert _f(_one) == 0.0, f"{_f.__name__} over a single group should be 0.0, got {_f(_one)!r}"
_missing = {"A": {"tp": 5, "fp": 5, "fn": 5, "tn": 5},
            "B": {"tp": 0, "fp": 0, "fn": 0, "tn": 9}}
try:
    equal_opportunity_gap(_missing)
    assert False, "group B has no positives, so the TPR gap is undefined"
except ValueError as _e:
    assert "B" in str(_e), f"the error should name the group, it said {_e}"
try:
    gap({}, "tpr")
    assert False, "no groups at all should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "ppv_from_rates matches the counted PPV", "code": r'''
_cm = {"tp": 30, "fp": 20, "fn": 10, "tn": 40}
_r = rates(_cm)
_implied = ppv_from_rates(_r["base_rate"], _r["tpr"], _r["fpr"])
assert abs(_implied - _r["ppv"]) < 1e-9, f"identity gave {_implied!r}, counting gave {_r['ppv']!r}"
assert abs(ppv_from_rates(0.5, 1.0, 0.0) - 1.0) < 1e-9, "a perfect classifier has PPV 1"
for _bad in ((1.5, 0.5, 0.5), (0.5, -0.1, 0.5), (0.5, 0.5, 2.0)):
    try:
        ppv_from_rates(*_bad)
        assert False, f"ppv_from_rates{_bad!r} should raise ValueError"
    except ValueError:
        pass
try:
    ppv_from_rates(0.5, 0.0, 0.0)
    assert False, "selecting nobody leaves PPV undefined"
except ValueError:
    pass
'''},
                    {"name": "Equal base rates allow both criteria at once", "code": r'''
_d = impossibility_demo(0.3, 0.3, 0.8, 0.2)
assert _d["calibrated"] is True, f"identical base rates should be calibrated, got {_d!r}"
assert abs(_d["calibration_gap"]) < 1e-9, f"gap should vanish, got {_d['calibration_gap']!r}"
assert abs(_d["ppv_a"] - _d["ppv_b"]) < 1e-9
'''},
                    {"name": "Unequal base rates make the two criteria incompatible", "code": r'''
_d = impossibility_demo(0.1, 0.5, 0.8, 0.2)
assert _d["calibrated"] is False, "equalised odds plus unequal base rates cannot be calibrated"
assert abs(_d["ppv_a"] - 0.08 / 0.26) < 1e-9, f"ppv_a is {_d['ppv_a']!r}"
assert abs(_d["ppv_b"] - 0.80) < 1e-9, f"ppv_b is {_d['ppv_b']!r}"
assert _d["calibration_gap"] > 0.4, f"the gap is {_d['calibration_gap']!r}"
for _ba in (0.05, 0.2, 0.45):
    for _bb in (0.5, 0.7, 0.9):
        for _t, _f in ((0.9, 0.1), (0.7, 0.3), (0.6, 0.05)):
            assert impossibility_demo(_ba, _bb, _t, _f)["calibrated"] is False, \
                f"base rates {_ba} and {_bb} under ({_t}, {_f}) should not be calibrated"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Anonymisation and differential privacy",
            "summary": "Measure re-identification risk, then buy a bounded amount of protection with noise.",
            "concepts": [
                "Quasi-identifiers: fields that are not identifiers alone but are jointly unique",
                "k-anonymity is the size of the smallest equivalence class over the quasi-identifiers",
                "k-anonymity says nothing about the sensitive value; l-diversity constrains that separately",
                "Generalisation and suppression buy anonymity by destroying utility — the trade is the point",
                "Differential privacy is a property of the mechanism, not of the released table",
                "The Laplace mechanism adds noise of scale Δf/ε, where Δf is the query's sensitivity",
                "Sequential composition: epsilons add, so a budget must be accounted for across queries",
            ],
            "lab": {
                "title": "k-anonymity, l-diversity and an epsilon budget",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A record is a dict, for example
`{"age": 34, "postcode": "2050", "diagnosis": "flu"}`.

**`equivalence_classes(records, quasi_ids)`** — `{tuple_of_values: [records]}`,
grouped on the quasi-identifier fields in the given order. Raise `ValueError` when
`quasi_ids` is empty or a record lacks one of the fields.

**`k_anonymity(records, quasi_ids)`** — the size of the smallest class; `0` for an
empty table.

**`l_diversity(records, quasi_ids, sensitive)`** — the smallest number of distinct
values of the sensitive field within any one class; `0` for an empty table.

**`generalise_numeric(records, field, width)`** — new records, originals untouched,
with the numeric `field` replaced by a bucket label:

```text
age 34, width 10  ->  "30-39"
age 7,  width 5   ->  "5-9"
```

Raise `ValueError` when `width < 1` or the value is not an integer.

**`suppress(records, quasi_ids, k)`** — drop every record whose class is smaller
than `k`. Raise `ValueError` when `k < 1`.

**`laplace_noise(rng, scale)`** — one sample from Laplace(0, `scale`) by inverse
transform, using a single `rng.random()`:

```text
u = rng.random() − 0.5
noise = −scale · sign(u) · ln(1 − 2|u|)
```

Raise `ValueError` when `scale <= 0`.

**`PrivacyBudget(epsilon)`** — `spent`, `remaining`, and `spend(eps)` which returns
the new remaining budget and raises `ValueError` for a non-positive request or one
that would overspend.

**`dp_count(records, predicate, epsilon, rng, budget=None)`** — the count of
records satisfying `predicate`, plus Laplace noise of scale `1/epsilon` (a count
has sensitivity 1). Spend `epsilon` from `budget` when one is given, before
answering. Raise `ValueError` when `epsilon <= 0`.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random

PATIENTS = [
    {"age": 34, "postcode": "2050", "diagnosis": "flu"},
    {"age": 36, "postcode": "2051", "diagnosis": "flu"},
    {"age": 31, "postcode": "2052", "diagnosis": "cancer"},
    {"age": 47, "postcode": "2050", "diagnosis": "flu"},
    {"age": 42, "postcode": "2051", "diagnosis": "hiv"},
    {"age": 45, "postcode": "2052", "diagnosis": "flu"},
]


def equivalence_classes(records, quasi_ids):
    """Group records on the quasi-identifier values."""
    # your code here


def k_anonymity(records, quasi_ids):
    """Size of the smallest equivalence class."""
    # your code here


def l_diversity(records, quasi_ids, sensitive):
    """Fewest distinct sensitive values inside any one class."""
    # your code here


def generalise_numeric(records, field, width):
    """Copies of records with a numeric field replaced by a bucket label."""
    # your code here


def suppress(records, quasi_ids, k):
    """Records whose equivalence class has at least k members."""
    # your code here


def laplace_noise(rng, scale):
    """One Laplace(0, scale) sample by inverse transform."""
    # your code here


class PrivacyBudget:
    """An epsilon budget spent across a sequence of queries."""

    def __init__(self, epsilon):
        # your code here
        pass

    @property
    def remaining(self):
        # your code here
        pass

    def spend(self, eps):
        """Charge eps to the budget and return what is left."""
        # your code here


def dp_count(records, predicate, epsilon, rng, budget=None):
    """A count released through the Laplace mechanism."""
    # your code here


print(k_anonymity(PATIENTS, ["age", "postcode"]))
coarse = generalise_numeric(PATIENTS, "age", 20)
print(k_anonymity(coarse, ["age"]), l_diversity(coarse, ["age"], "diagnosis"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random

PATIENTS = [
    {"age": 34, "postcode": "2050", "diagnosis": "flu"},
    {"age": 36, "postcode": "2051", "diagnosis": "flu"},
    {"age": 31, "postcode": "2052", "diagnosis": "cancer"},
    {"age": 47, "postcode": "2050", "diagnosis": "flu"},
    {"age": 42, "postcode": "2051", "diagnosis": "hiv"},
    {"age": 45, "postcode": "2052", "diagnosis": "flu"},
]


def equivalence_classes(records, quasi_ids):
    """Group records on the quasi-identifier values."""
    if not quasi_ids:
        raise ValueError("at least one quasi-identifier is required")
    classes = {}
    for record in records:
        key = []
        for field in quasi_ids:
            if field not in record:
                raise ValueError(f"record is missing quasi-identifier {field!r}")
            key.append(record[field])
        classes.setdefault(tuple(key), []).append(record)
    return classes


def k_anonymity(records, quasi_ids):
    """Size of the smallest equivalence class."""
    classes = equivalence_classes(records, quasi_ids)
    if not classes:
        return 0
    return min(len(group) for group in classes.values())


def l_diversity(records, quasi_ids, sensitive):
    """Fewest distinct sensitive values inside any one class."""
    classes = equivalence_classes(records, quasi_ids)
    if not classes:
        return 0
    counts = []
    for group in classes.values():
        for record in group:
            if sensitive not in record:
                raise ValueError(f"record is missing sensitive field {sensitive!r}")
        counts.append(len({record[sensitive] for record in group}))
    return min(counts)


def generalise_numeric(records, field, width):
    """Copies of records with a numeric field replaced by a bucket label."""
    if width < 1:
        raise ValueError("width must be at least 1")
    out = []
    for record in records:
        if field not in record:
            raise ValueError(f"record is missing {field!r}")
        value = record[field]
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{field!r} must be a whole number, got {value!r}")
        low = (value // width) * width
        copy = dict(record)
        copy[field] = f"{low}-{low + width - 1}"
        out.append(copy)
    return out


def suppress(records, quasi_ids, k):
    """Records whose equivalence class has at least k members."""
    if k < 1:
        raise ValueError("k must be at least 1")
    classes = equivalence_classes(records, quasi_ids)
    keep = {id(record) for group in classes.values() if len(group) >= k
            for record in group}
    return [record for record in records if id(record) in keep]


def laplace_noise(rng, scale):
    """One Laplace(0, scale) sample by inverse transform."""
    if scale <= 0:
        raise ValueError("scale must be positive")
    u = rng.random() - 0.5
    # guard the log against the (vanishingly rare) endpoint u == -0.5
    tail = max(1e-12, 1 - 2 * abs(u))
    sign = -1.0 if u < 0 else 1.0
    return -scale * sign * math.log(tail)


class PrivacyBudget:
    """An epsilon budget spent across a sequence of queries."""

    def __init__(self, epsilon):
        if epsilon <= 0:
            raise ValueError("the budget must be positive")
        self.epsilon = float(epsilon)
        self.spent = 0.0

    @property
    def remaining(self):
        return self.epsilon - self.spent

    def spend(self, eps):
        """Charge eps to the budget and return what is left."""
        if eps <= 0:
            raise ValueError("each query must spend a positive epsilon")
        if eps > self.remaining + 1e-12:
            raise ValueError(
                f"budget exhausted: {eps} requested, {self.remaining} left")
        self.spent += eps
        return self.remaining


def dp_count(records, predicate, epsilon, rng, budget=None):
    """A count released through the Laplace mechanism."""
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if budget is not None:
        budget.spend(epsilon)          # charge before answering, never after
    true_count = sum(1 for record in records if predicate(record))
    return true_count + laplace_noise(rng, 1.0 / epsilon)


print(k_anonymity(PATIENTS, ["age", "postcode"]))
coarse = generalise_numeric(PATIENTS, "age", 20)
print(k_anonymity(coarse, ["age"]), l_diversity(coarse, ["age"], "diagnosis"))
'''}],
                "hints": [
                    "The class key must be a tuple, because a list cannot be a dict key — build it in the order `quasi_ids` gives you.",
                    "`(value // width) * width` is the bucket floor; the label runs to `low + width - 1`, so width 10 gives `30-39`, not `30-40`.",
                    "`generalise_numeric` must copy: `dict(record)` before assigning, otherwise you have silently mutated the caller's table.",
                    "Charge the budget in `dp_count` before you compute anything, so a refused query cannot leak an answer as a side effect.",
                ],
                "tests": [
                    {"name": "Equivalence classes and k-anonymity", "code": r'''
_c = equivalence_classes(PATIENTS, ["postcode"])
assert sorted(_c) == [("2050",), ("2051",), ("2052",)], f"class keys were {sorted(_c)!r}"
assert len(_c[("2050",)]) == 2, "two patients share postcode 2050"
assert k_anonymity(PATIENTS, ["age", "postcode"]) == 1, "every age/postcode pair is unique"
assert k_anonymity(PATIENTS, ["postcode"]) == 2, "postcode alone gives classes of two"
assert k_anonymity([], ["postcode"]) == 0, "an empty table has k = 0"
try:
    equivalence_classes(PATIENTS, [])
    assert False, "no quasi-identifiers should raise ValueError"
except ValueError:
    pass
try:
    equivalence_classes(PATIENTS, ["surname"])
    assert False, "an absent field should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "l-diversity is a separate question from k", "code": r'''
assert l_diversity(PATIENTS, ["postcode"], "diagnosis") == 1, \
    "postcode 2050 holds two patients with the same diagnosis, so l = 1"
assert l_diversity(PATIENTS, ["postcode"], "age") == 2, "ages differ inside every postcode"
assert l_diversity([], ["postcode"], "diagnosis") == 0, "an empty table has l = 0"
_two = [{"z": 1, "s": "a"}, {"z": 1, "s": "b"}, {"z": 2, "s": "a"}, {"z": 2, "s": "b"}]
assert k_anonymity(_two, ["z"]) == 2 and l_diversity(_two, ["z"], "s") == 2, \
    "this table is 2-anonymous and 2-diverse"
'''},
                    {"name": "Generalisation buys anonymity and costs precision", "code": r'''
_g = generalise_numeric(PATIENTS, "age", 20)
assert _g[0]["age"] == "20-39", f"age 34 in buckets of 20 is 20-39, got {_g[0]['age']!r}"
assert generalise_numeric([{"age": 7}], "age", 5)[0]["age"] == "5-9"
assert generalise_numeric([{"age": 0}], "age", 10)[0]["age"] == "0-9"
assert PATIENTS[0]["age"] == 34, "the original records must not be mutated"
assert k_anonymity(PATIENTS, ["age"]) == 1, "raw ages are unique"
assert k_anonymity(_g, ["age"]) == 3, "bucketing by 20 pulls k up to 3"
for _bad in (("age", 0), ("age", -3)):
    try:
        generalise_numeric(PATIENTS, *_bad)
        assert False, f"width {_bad[1]} should raise ValueError"
    except ValueError:
        pass
try:
    generalise_numeric([{"age": "old"}], "age", 10)
    assert False, "a non-integer value should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Suppression removes the rare classes", "code": r'''
_kept = suppress(PATIENTS, ["postcode"], 2)
assert len(_kept) == 6, "every postcode class already has two members"
_mixed = PATIENTS + [{"age": 60, "postcode": "9999", "diagnosis": "flu"}]
_kept = suppress(_mixed, ["postcode"], 2)
assert len(_kept) == 6 and all(_r["postcode"] != "9999" for _r in _kept), \
    f"the singleton class should be dropped, got {_kept!r}"
assert suppress(_mixed, ["age", "postcode"], 2) == [], "with unique keys everything is suppressed"
assert k_anonymity(_kept, ["postcode"]) >= 2, "what survives is 2-anonymous"
try:
    suppress(PATIENTS, ["postcode"], 0)
    assert False, "k = 0 should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The Laplace mechanism has the right shape", "code": r'''
import random as _random
import statistics as _stats
_rng = _random.Random(7)
_samples = [laplace_noise(_rng, 2.0) for _ in range(4000)]
assert abs(_stats.fmean(_samples)) < 0.3, f"Laplace noise should be centred, mean was {_stats.fmean(_samples)!r}"
assert abs(_stats.fmean([abs(_x) for _x in _samples]) - 2.0) < 0.3, \
    "the mean absolute deviation of Laplace(0, b) is b"
assert any(_x > 0 for _x in _samples) and any(_x < 0 for _x in _samples), "noise goes both ways"
_a = laplace_noise(_random.Random(3), 1.0)
_b = laplace_noise(_random.Random(3), 1.0)
assert _a == _b, "a seeded generator must reproduce its sample exactly"
for _bad in (0, -1.0):
    try:
        laplace_noise(_random.Random(1), _bad)
        assert False, f"scale {_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The budget composes and then refuses", "code": r'''
_b = PrivacyBudget(1.0)
assert abs(_b.remaining - 1.0) < 1e-12 and _b.spent == 0.0, "a fresh budget is untouched"
assert abs(_b.spend(0.4) - 0.6) < 1e-12, "spend returns what is left"
_b.spend(0.4)
assert abs(_b.remaining - 0.2) < 1e-9, f"remaining is {_b.remaining!r}, expected 0.2"
try:
    _b.spend(0.5)
    assert False, "overspending should raise ValueError"
except ValueError:
    pass
assert abs(_b.remaining - 0.2) < 1e-9, "a refused query must not change the budget"
_b.spend(0.2)
assert abs(_b.remaining) < 1e-9, "the budget is now exhausted"
for _bad in (0, -0.1):
    try:
        PrivacyBudget(1.0).spend(_bad)
        assert False, f"spending {_bad} should raise ValueError"
    except ValueError:
        pass
try:
    PrivacyBudget(0)
    assert False, "a non-positive budget should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "dp_count answers approximately and charges exactly", "code": r'''
import random as _random
import statistics as _stats
_rng = _random.Random(11)
_flu = lambda _r: _r["diagnosis"] == "flu"
_budget = PrivacyBudget(10.0)
_answers = [dp_count(PATIENTS, _flu, 0.5, _rng, _budget) for _ in range(20)]
assert abs(_budget.remaining) < 1e-9, f"twenty queries at 0.5 spend the whole budget, {_budget.remaining!r} left"
assert abs(_stats.fmean(_answers) - 4.0) < 1.5, \
    f"the true count is 4; the noisy mean was {_stats.fmean(_answers)!r}"
assert any(_a != 4 for _a in _answers), "an answer with no noise at all is not private"
_tight = dp_count(PATIENTS, _flu, 50.0, _random.Random(2))
assert abs(_tight - 4.0) < 0.5, f"a large epsilon means little noise, got {_tight!r}"
try:
    dp_count(PATIENTS, _flu, 0.0, _random.Random(1))
    assert False, "epsilon 0 should raise ValueError"
except ValueError:
    pass
_small = PrivacyBudget(0.3)
try:
    dp_count(PATIENTS, _flu, 0.5, _random.Random(1), _small)
    assert False, "a query larger than the budget should raise ValueError"
except ValueError:
    pass
assert _small.spent == 0.0, "a refused query must not be charged"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Compliance as code: data-subject requests",
            "summary": "Access, rectification and erasure against a store with retention rules and legal holds.",
            "concepts": [
                "GDPR Article 15 (access), 16 (rectification) and 17 (erasure) as three operations on a record store",
                "The right to erasure is not absolute: Article 17(3) preserves legal obligations and legal claims",
                "Storage limitation (Article 5(1)(e)) is a duty to delete, and cuts the opposite way to a legal hold",
                "A refusal must carry a reason; 'no' without a ground is itself a compliance failure",
                "Exports must be copies, or the response leaks a handle to live data",
                "Every request and every refusal is logged, because the controller carries the burden of proof",
                "Deleting on request and retaining under obligation are decided per record, not per subject",
            ],
            "lab": {
                "title": "A data-subject request handler",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A record is
`{"id": 1, "subject": "ada", "category": "invoice", "created": 100, "data": {...}}`.
`created` and `today` are plain day numbers.

Two policies are supplied:

```text
RETENTION_DAYS      how long each category may be kept at all
MANDATORY           categories a legal obligation forces you to keep
```

Build `RecordStore`.

- **`add(record)`** — `ValueError` for a missing key, an unknown category or a
  duplicate id.
- **`place_hold(record_id)`** / **`release_hold(record_id)`** — `KeyError` for an
  unknown id.
- **`export(subject)`** — Article 15. Deep copies of that subject's records,
  sorted by id. An unknown subject gives `[]`.
- **`rectify(subject, record_id, field, value)`** — Article 16. Update
  `record["data"][field]`. `KeyError` when the id is unknown or belongs to another
  subject; `ValueError` when the field is not already present.
- **`erase(subject, today)`** — Article 17. Returns
  `(erased_ids, refusals)`. A record is refused with reason `"legal_hold"` when it
  is under hold, and `"retention"` when its category is in `MANDATORY` and
  `today - created < RETENTION_DAYS[category]`. A hold outranks retention.
- **`expired(today)`** — Article 5(1)(e). Sorted ids where
  `today - created >= RETENTION_DAYS[category]`.
- **`purge_expired(today)`** — delete the expired records that are not under hold;
  return the sorted ids removed.

Every one of `export`, `rectify`, `erase` and `purge_expired` appends
`{"op": name, "subject": subject_or_None, "ids": [...]}` to `self.log`, in call
order. `rectify` logs the single id it changed; a refused operation that raises
logs nothing.
''',
                "files": [{"name": "main.py", "content": r'''
import copy

RETENTION_DAYS = {"invoice": 2555, "marketing": 365, "support": 730}
MANDATORY = {"invoice"}
REQUIRED_KEYS = ("id", "subject", "category", "created", "data")


class RecordStore:
    """A record store that answers data-subject requests."""

    def __init__(self):
        self.records = []
        self.holds = set()
        self.log = []

    def add(self, record):
        """Store one record. ValueError for a malformed or duplicate one."""
        # your code here

    def _find(self, record_id):
        """The record with this id. KeyError when there is none."""
        # your code here

    def place_hold(self, record_id):
        """Mark a record as being under legal hold."""
        # your code here

    def release_hold(self, record_id):
        """Lift a legal hold."""
        # your code here

    def export(self, subject):
        """Article 15: copies of everything held about the subject."""
        # your code here

    def rectify(self, subject, record_id, field, value):
        """Article 16: correct one field of one record."""
        # your code here

    def erase(self, subject, today):
        """Article 17: (erased_ids, {id: reason})."""
        # your code here

    def expired(self, today):
        """Article 5(1)(e): ids kept past their retention period."""
        # your code here

    def purge_expired(self, today):
        """Delete expired records that are not under hold."""
        # your code here


store = RecordStore()
store.add({"id": 1, "subject": "ada", "category": "marketing",
           "created": 0, "data": {"email": "ada@example.org"}})
store.add({"id": 2, "subject": "ada", "category": "invoice",
           "created": 900, "data": {"total": 42}})
print(store.export("ada"))
print(store.erase("ada", 1000))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import copy

RETENTION_DAYS = {"invoice": 2555, "marketing": 365, "support": 730}
MANDATORY = {"invoice"}
REQUIRED_KEYS = ("id", "subject", "category", "created", "data")


class RecordStore:
    """A record store that answers data-subject requests."""

    def __init__(self):
        self.records = []
        self.holds = set()
        self.log = []

    def add(self, record):
        """Store one record. ValueError for a malformed or duplicate one."""
        for key in REQUIRED_KEYS:
            if key not in record:
                raise ValueError(f"record is missing {key!r}")
        if record["category"] not in RETENTION_DAYS:
            raise ValueError(f"unknown category {record['category']!r}")
        if any(r["id"] == record["id"] for r in self.records):
            raise ValueError(f"duplicate record id {record['id']!r}")
        self.records.append(record)

    def _find(self, record_id):
        """The record with this id. KeyError when there is none."""
        for record in self.records:
            if record["id"] == record_id:
                return record
        raise KeyError(f"no record with id {record_id!r}")

    def place_hold(self, record_id):
        """Mark a record as being under legal hold."""
        self._find(record_id)
        self.holds.add(record_id)

    def release_hold(self, record_id):
        """Lift a legal hold."""
        self._find(record_id)
        self.holds.discard(record_id)

    def export(self, subject):
        """Article 15: copies of everything held about the subject."""
        found = sorted((r for r in self.records if r["subject"] == subject),
                       key=lambda r: r["id"])
        out = [copy.deepcopy(record) for record in found]
        self.log.append({"op": "export", "subject": subject,
                         "ids": [r["id"] for r in out]})
        return out

    def rectify(self, subject, record_id, field, value):
        """Article 16: correct one field of one record."""
        record = self._find(record_id)
        if record["subject"] != subject:
            raise KeyError(f"record {record_id!r} does not belong to {subject!r}")
        if field not in record["data"]:
            raise ValueError(f"record {record_id!r} has no field {field!r}")
        record["data"][field] = value
        self.log.append({"op": "rectify", "subject": subject, "ids": [record_id]})
        return record

    def erase(self, subject, today):
        """Article 17: (erased_ids, {id: reason})."""
        erased, refusals = [], {}
        keep = []
        for record in self.records:
            if record["subject"] != subject:
                keep.append(record)
                continue
            if record["id"] in self.holds:
                refusals[record["id"]] = "legal_hold"
                keep.append(record)
            elif (record["category"] in MANDATORY
                  and today - record["created"] < RETENTION_DAYS[record["category"]]):
                refusals[record["id"]] = "retention"
                keep.append(record)
            else:
                erased.append(record["id"])
        self.records = keep
        erased.sort()
        self.log.append({"op": "erase", "subject": subject, "ids": list(erased)})
        return erased, refusals

    def expired(self, today):
        """Article 5(1)(e): ids kept past their retention period."""
        return sorted(r["id"] for r in self.records
                      if today - r["created"] >= RETENTION_DAYS[r["category"]])

    def purge_expired(self, today):
        """Delete expired records that are not under hold."""
        doomed = [i for i in self.expired(today) if i not in self.holds]
        self.records = [r for r in self.records if r["id"] not in doomed]
        self.log.append({"op": "purge_expired", "subject": None, "ids": list(doomed)})
        return doomed


store = RecordStore()
store.add({"id": 1, "subject": "ada", "category": "marketing",
           "created": 0, "data": {"email": "ada@example.org"}})
store.add({"id": 2, "subject": "ada", "category": "invoice",
           "created": 900, "data": {"total": 42}})
print(store.export("ada"))
print(store.erase("ada", 1000))
'''}],
                "hints": [
                    "`copy.deepcopy` is what makes `export` an export rather than a loan — a shallow copy still shares the nested `data` dict.",
                    "Build `erase` as one pass that partitions into a `keep` list and an `erased` list, then reassign `self.records`; deleting from a list you are iterating skips entries.",
                    "Check the hold before the retention rule, so a record that is both gets the reason that actually decided it.",
                    "`expired` compares `today - created >= RETENTION_DAYS[category]`; the same expression with `<` is the retention refusal in `erase`, and only one of the two is about a legal obligation.",
                ],
                "tests": [
                    {"name": "add validates the record", "code": r'''
_s = RecordStore()
_ok = {"id": 1, "subject": "ada", "category": "support", "created": 0, "data": {"note": "x"}}
_s.add(_ok)
assert len(_s.records) == 1
for _bad in ({"id": 2, "subject": "ada", "category": "astrology", "created": 0, "data": {}},
             {"id": 3, "subject": "ada", "created": 0, "data": {}},
             {"id": 1, "subject": "bob", "category": "support", "created": 0, "data": {}}):
    try:
        _s.add(_bad)
        assert False, f"add({_bad!r}) should raise ValueError"
    except ValueError:
        pass
assert len(_s.records) == 1, "a refused add must not change the store"
'''},
                    {"name": "export copies, filters and logs", "code": r'''
_s = RecordStore()
_s.add({"id": 2, "subject": "ada", "category": "support", "created": 0, "data": {"note": "b"}})
_s.add({"id": 1, "subject": "ada", "category": "marketing", "created": 0, "data": {"note": "a"}})
_s.add({"id": 3, "subject": "bob", "category": "support", "created": 0, "data": {"note": "c"}})
_out = _s.export("ada")
assert [_r["id"] for _r in _out] == [1, 2], f"export should be sorted by id, got {[_r['id'] for _r in _out]!r}"
_out[0]["data"]["note"] = "TAMPERED"
assert _s._find(1)["data"]["note"] == "a", "the export must be a deep copy, not a live handle"
assert _s.export("nobody") == [], "an unknown subject holds no records"
assert _s.log[0] == {"op": "export", "subject": "ada", "ids": [1, 2]}, f"log[0] is {_s.log[0]!r}"
'''},
                    {"name": "rectify corrects one field and refuses the rest", "code": r'''
_s = RecordStore()
_s.add({"id": 1, "subject": "ada", "category": "support", "created": 0, "data": {"email": "old@x"}})
_s.add({"id": 2, "subject": "bob", "category": "support", "created": 0, "data": {"email": "b@x"}})
_s.rectify("ada", 1, "email", "new@x")
assert _s._find(1)["data"]["email"] == "new@x", "the field should have been updated"
try:
    _s.rectify("ada", 2, "email", "hijack@x")
    assert False, "rectifying another subject's record should raise KeyError"
except KeyError:
    pass
assert _s._find(2)["data"]["email"] == "b@x", "the refused rectification must change nothing"
try:
    _s.rectify("ada", 1, "shoe_size", 42)
    assert False, "an unknown field should raise ValueError"
except ValueError:
    pass
try:
    _s.rectify("ada", 99, "email", "x@x")
    assert False, "an unknown id should raise KeyError"
except KeyError:
    pass
assert [_e["op"] for _e in _s.log] == ["rectify"], f"only the successful call logs, got {_s.log!r}"
'''},
                    {"name": "erase honours the legal hold", "code": r'''
_s = RecordStore()
_s.add({"id": 1, "subject": "ada", "category": "marketing", "created": 0, "data": {}})
_s.add({"id": 2, "subject": "ada", "category": "support", "created": 0, "data": {}})
_s.place_hold(2)
_erased, _refused = _s.erase("ada", 500)
assert _erased == [1], f"only the unheld record can go, got {_erased!r}"
assert _refused == {2: "legal_hold"}, f"refusals were {_refused!r}"
assert [_r["id"] for _r in _s.records] == [2], "the held record stays in the store"
try:
    _s.place_hold(99)
    assert False, "holding an unknown id should raise KeyError"
except KeyError:
    pass
'''},
                    {"name": "erase honours a mandatory retention period", "code": r'''
_s = RecordStore()
_s.add({"id": 1, "subject": "ada", "category": "invoice", "created": 900, "data": {}})
_s.add({"id": 2, "subject": "ada", "category": "marketing", "created": 900, "data": {}})
_erased, _refused = _s.erase("ada", 1000)
assert _erased == [2], f"the marketing record is erasable, got {_erased!r}"
assert _refused == {1: "retention"}, f"the invoice is held by law, refusals were {_refused!r}"
_erased, _refused = _s.erase("ada", 900 + RETENTION_DAYS["invoice"])
assert _erased == [1] and _refused == {}, \
    f"once the obligation lapses the invoice goes too, got {_erased!r} {_refused!r}"
assert _s.records == [], "the store is now empty"
'''},
                    {"name": "A hold outranks retention, and other subjects are untouched", "code": r'''
_s = RecordStore()
_s.add({"id": 1, "subject": "ada", "category": "invoice", "created": 0, "data": {}})
_s.add({"id": 2, "subject": "bob", "category": "marketing", "created": 0, "data": {}})
_s.place_hold(1)
_erased, _refused = _s.erase("ada", 99999)
assert _erased == [] and _refused == {1: "legal_hold"}, \
    f"the hold, not the lapsed retention, is the operative reason: {_refused!r}"
assert any(_r["id"] == 2 for _r in _s.records), "bob's record is none of ada's business"
_s.release_hold(1)
assert _s.erase("ada", 99999)[0] == [1], "releasing the hold makes it erasable"
'''},
                    {"name": "Storage limitation purges, but not through a hold", "code": r'''
_s = RecordStore()
_s.add({"id": 1, "subject": "ada", "category": "marketing", "created": 0, "data": {}})
_s.add({"id": 2, "subject": "bob", "category": "marketing", "created": 0, "data": {}})
_s.add({"id": 3, "subject": "cy", "category": "support", "created": 0, "data": {}})
assert _s.expired(100) == [], "nothing is past its retention on day 100"
assert _s.expired(400) == [1, 2], f"marketing lapses after 365 days, got {_s.expired(400)!r}"
_s.place_hold(2)
assert _s.purge_expired(400) == [1], "record 2 is expired but under hold"
assert sorted(_r["id"] for _r in _s.records) == [2, 3], "record 1 is gone, the others remain"
assert _s.log[-1] == {"op": "purge_expired", "subject": None, "ids": [1]}, f"log tail is {_s.log[-1]!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Transparency and tamper-evident records",
            "summary": "Documentation a reviewer can read, and a log an operator cannot quietly rewrite.",
            "concepts": [
                "Model cards (Mitchell et al., FAT* 2019): intended use, out-of-scope use, data, metrics, limitations",
                "Documentation is a control only when a missing section is an error rather than a blank",
                "Canonical serialisation: the same content must hash the same regardless of key order",
                "A hash chain binds each entry to its predecessor, so an edit invalidates every later link",
                "Tamper-evident is not tamper-proof: detection requires an independently held head hash",
                "Append-only logging is what turns 'we assessed the risk' into evidence",
                "Binding the card's hash into the log ties a released model to the claims made about it",
            ],
            "lab": {
                "title": "Model cards and a hash-chained audit log",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
**`model_card(meta)`** — render a card as markdown. `meta` must carry every key in
`REQUIRED`; a missing one raises `ValueError` whose message contains the key name.
`limitations` must be a non-empty list, `metrics` a dict. The layout, exactly:

```text
# Model Card: <name>

**Version:** <version>

## Intended use
<intended_use>

## Out of scope
<out_of_scope>

## Training data
<training_data>

## Metrics
- accuracy: 0.910
- recall: 0.740

## Limitations
- <first limitation>
- <second limitation>

## Contact
<contact>
```

Metric lines are sorted by name and formatted to three decimals. There is exactly
one blank line between a section and the next heading.

**`card_hash(card)`** — the SHA-256 hex digest of the card text, UTF-8 encoded.

**`canonical(entry)`** — `json.dumps` with `sort_keys=True` and
`separators=(",", ":")`, so two dicts with the same content hash alike.

**`chain_hash(prev, entry)`** — `sha256(prev + canonical(entry))`, hex.

**`AuditLog`** — append-only.

- `GENESIS` is 64 zeros, the predecessor of the first entry.
- `head` — the hash of the last entry, or `GENESIS` when empty.
- `append(entry)` — store `{"seq": n, "entry": entry, "prev": head, "hash": ...}`
  and return the new head.
- `verify()` — `None` when the chain is intact, otherwise the index of the first
  entry whose `prev` does not match its predecessor's hash or whose `hash` does not
  match its own content.
''',
                "files": [{"name": "main.py", "content": r'''
import hashlib
import json

REQUIRED = ("name", "version", "intended_use", "out_of_scope",
            "training_data", "metrics", "limitations", "contact")


def model_card(meta):
    """A markdown model card. ValueError when a required section is missing."""
    # your code here


def card_hash(card):
    """SHA-256 hex digest of the card text."""
    # your code here


def canonical(entry):
    """Key-order independent JSON serialisation."""
    # your code here


def chain_hash(prev, entry):
    """The hash linking one entry to its predecessor."""
    # your code here


class AuditLog:
    """An append-only log in which every entry commits to the one before it."""

    GENESIS = "0" * 64

    def __init__(self):
        self.entries = []

    @property
    def head(self):
        """Hash of the last entry, or GENESIS when the log is empty."""
        # your code here

    def append(self, entry):
        """Add an entry and return the new head."""
        # your code here

    def verify(self):
        """None when intact, else the index of the first broken link."""
        # your code here


CARD = {
    "name": "loan-scorer",
    "version": "2.1.0",
    "intended_use": "Rank applications for manual review.",
    "out_of_scope": "Automated rejection without a human decision.",
    "training_data": "Internal applications 2019-2024, 118k rows.",
    "metrics": {"accuracy": 0.9104, "recall": 0.7362},
    "limitations": ["Under-represents applicants under 25.",
                    "Not validated outside the domestic market."],
    "contact": "model-governance@example.org",
}

log = AuditLog()
log.append({"event": "card_published", "card": card_hash(model_card(CARD))})
print(log.verify())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import hashlib
import json

REQUIRED = ("name", "version", "intended_use", "out_of_scope",
            "training_data", "metrics", "limitations", "contact")


def model_card(meta):
    """A markdown model card. ValueError when a required section is missing."""
    for key in REQUIRED:
        if key not in meta:
            raise ValueError(f"model card is missing the {key!r} section")
    if not isinstance(meta["metrics"], dict):
        raise ValueError("metrics must be a dict of name to value")
    if not isinstance(meta["limitations"], list) or not meta["limitations"]:
        raise ValueError("limitations must be a non-empty list")

    parts = [f"# Model Card: {meta['name']}",
             f"**Version:** {meta['version']}",
             "## Intended use\n" + str(meta["intended_use"]),
             "## Out of scope\n" + str(meta["out_of_scope"]),
             "## Training data\n" + str(meta["training_data"])]

    metric_lines = [f"- {name}: {meta['metrics'][name]:.3f}"
                    for name in sorted(meta["metrics"])]
    parts.append("## Metrics\n" + "\n".join(metric_lines))
    parts.append("## Limitations\n"
                 + "\n".join(f"- {item}" for item in meta["limitations"]))
    parts.append("## Contact\n" + str(meta["contact"]))
    return "\n\n".join(parts) + "\n"


def card_hash(card):
    """SHA-256 hex digest of the card text."""
    return hashlib.sha256(card.encode("utf-8")).hexdigest()


def canonical(entry):
    """Key-order independent JSON serialisation."""
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))


def chain_hash(prev, entry):
    """The hash linking one entry to its predecessor."""
    return hashlib.sha256((prev + canonical(entry)).encode("utf-8")).hexdigest()


class AuditLog:
    """An append-only log in which every entry commits to the one before it."""

    GENESIS = "0" * 64

    def __init__(self):
        self.entries = []

    @property
    def head(self):
        """Hash of the last entry, or GENESIS when the log is empty."""
        return self.entries[-1]["hash"] if self.entries else self.GENESIS

    def append(self, entry):
        """Add an entry and return the new head."""
        prev = self.head
        self.entries.append({"seq": len(self.entries), "entry": entry,
                             "prev": prev, "hash": chain_hash(prev, entry)})
        return self.head

    def verify(self):
        """None when intact, else the index of the first broken link."""
        prev = self.GENESIS
        for i, record in enumerate(self.entries):
            if record["prev"] != prev:
                return i
            if record["hash"] != chain_hash(record["prev"], record["entry"]):
                return i
            prev = record["hash"]
        return None


CARD = {
    "name": "loan-scorer",
    "version": "2.1.0",
    "intended_use": "Rank applications for manual review.",
    "out_of_scope": "Automated rejection without a human decision.",
    "training_data": "Internal applications 2019-2024, 118k rows.",
    "metrics": {"accuracy": 0.9104, "recall": 0.7362},
    "limitations": ["Under-represents applicants under 25.",
                    "Not validated outside the domestic market."],
    "contact": "model-governance@example.org",
}

log = AuditLog()
log.append({"event": "card_published", "card": card_hash(model_card(CARD))})
print(log.verify())
'''}],
                "hints": [
                    "Build the card as a list of section strings and join with a blank line — `\"\\n\\n\".join(parts)` — rather than concatenating newlines by hand.",
                    "`f\"- {name}: {value:.3f}\"` over `sorted(meta[\"metrics\"])` gives the metric block in one comprehension.",
                    "`hashlib.sha256(text.encode(\"utf-8\")).hexdigest()` — hash bytes, never a str, and pick the encoding explicitly.",
                    "`verify` carries the expected `prev` forward as it walks; check the stored `prev` first, then recompute the entry's own hash, and return the index the moment either disagrees.",
                ],
                "tests": [
                    {"name": "The card has every section, in order", "code": r'''
_c = model_card(CARD)
assert _c.startswith("# Model Card: loan-scorer"), f"the card starts {_c[:40]!r}"
assert "**Version:** 2.1.0" in _c, "the version line is missing"
_order = ["## Intended use", "## Out of scope", "## Training data",
          "## Metrics", "## Limitations", "## Contact"]
_at = [_c.find(_h) for _h in _order]
assert all(_i >= 0 for _i in _at), f"missing headings: {[_h for _h, _i in zip(_order, _at) if _i < 0]!r}"
assert _at == sorted(_at), f"the sections are out of order: {_at!r}"
assert "Rank applications for manual review." in _c, "the intended use text is missing"
assert "model-governance@example.org" in _c, "the contact is missing"
'''},
                    {"name": "Metrics and limitations render as bullets", "code": r'''
_c = model_card(CARD)
assert "- accuracy: 0.910" in _c, "metrics are rounded to three decimals"
assert "- recall: 0.736" in _c, f"recall line missing from:\n{_c}"
assert _c.find("- accuracy") < _c.find("- recall"), "metrics are sorted by name"
assert "- Under-represents applicants under 25." in _c, "limitations are bullets"
assert "- Not validated outside the domestic market." in _c
'''},
                    {"name": "A missing section is an error, not a blank", "code": r'''
for _key in REQUIRED:
    _meta = dict(CARD)
    del _meta[_key]
    try:
        model_card(_meta)
        assert False, f"a card without {_key!r} should raise ValueError"
    except ValueError as _e:
        assert _key in str(_e), f"the message should name {_key!r}, it said {_e}"
_empty = dict(CARD)
_empty["limitations"] = []
try:
    model_card(_empty)
    assert False, "an empty limitations list should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Canonical form ignores key order", "code": r'''
assert canonical({"b": 1, "a": 2}) == canonical({"a": 2, "b": 1}), \
    "canonical output must not depend on insertion order"
assert canonical({"a": 1}) == '{"a":1}', f"got {canonical({'a': 1})!r}, expected compact separators"
assert chain_hash(AuditLog.GENESIS, {"x": 1, "y": 2}) == chain_hash(AuditLog.GENESIS, {"y": 2, "x": 1})
assert chain_hash(AuditLog.GENESIS, {"x": 1}) != chain_hash("1" * 64, {"x": 1}), \
    "the predecessor hash must go into the digest"
assert len(card_hash("anything")) == 64, "a SHA-256 hex digest is 64 characters"
assert card_hash("a") != card_hash("b")
'''},
                    {"name": "The chain links and verifies", "code": r'''
_l = AuditLog()
assert _l.head == AuditLog.GENESIS, "an empty log heads at the genesis hash"
assert _l.verify() is None, "an empty log is intact"
_h1 = _l.append({"event": "trained", "rows": 118000})
_h2 = _l.append({"event": "evaluated", "accuracy": 0.91})
assert _h1 != _h2 and _l.head == _h2, "append returns the new head"
assert _l.entries[0]["prev"] == AuditLog.GENESIS, "the first entry points at genesis"
assert _l.entries[1]["prev"] == _h1, "each entry commits to the one before it"
assert [_e["seq"] for _e in _l.entries] == [0, 1], "sequence numbers count from zero"
assert _l.verify() is None, "an untouched chain verifies"
'''},
                    {"name": "Editing any entry breaks verification", "code": r'''
_l = AuditLog()
for _i in range(4):
    _l.append({"event": "step", "n": _i})
assert _l.verify() is None
_l.entries[2]["entry"]["n"] = 99
assert _l.verify() == 2, f"editing entry 2 should be detected there, got {_l.verify()!r}"
_l.entries[2]["entry"]["n"] = 2
assert _l.verify() is None, "restoring the value restores the chain"
_l.entries[1]["hash"] = "f" * 64
assert _l.verify() == 1, f"a forged hash should be caught at its own index, got {_l.verify()!r}"
'''},
                    {"name": "Deleting or reordering entries is detected", "code": r'''
_l = AuditLog()
for _i in range(4):
    _l.append({"event": "step", "n": _i})
_kept = list(_l.entries)
del _l.entries[1]
assert _l.verify() == 1, f"a removed entry breaks the link at index 1, got {_l.verify()!r}"
_l.entries = list(_kept)
_l.entries[1], _l.entries[2] = _l.entries[2], _l.entries[1]
assert _l.verify() == 1, f"a swap breaks the chain at index 1, got {_l.verify()!r}"
_l.entries = list(_kept)
assert _l.verify() is None, "the original ordering still verifies"
_bind = AuditLog()
_bind.append({"event": "card_published", "card": card_hash(model_card(CARD))})
assert _bind.verify() is None and len(_bind.entries[0]["entry"]["card"]) == 64, \
    "the released card should be bound into the log by its digest"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an accountability toolkit",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
One tool that audits a supplied model and dataset on four axes and emits a signed
report. `toolkit.py` holds the logic and is what the checks import; `main.py` runs
it over the sample data and prints the rendered report plus its signature.

## Audits

**`fairness_audit(rows, threshold=0.1)`** — rows are
`{"group": .., "y_true": 0|1, "y_pred": 0|1}`. Returns

```text
{"groups": [sorted group names],
 "demographic_parity": float, "equal_opportunity": float,
 "equalised_odds": float, "calibration": float,
 "flagged": [sorted metric names whose gap exceeds threshold]}
```

Raise `ValueError` for a label outside `{0, 1}`, for fewer than two groups, or for
a group whose rates are undefined.

**`privacy_audit(records, quasi_ids, sensitive)`** — returns
`{"k": .., "l": .., "singletons": .., "risk": ..}` where `singletons` counts
records alone in their equivalence class and `risk` is `"high"` when `k < 2`,
`"medium"` when `k < 5` or `l < 2`, and `"low"` otherwise.

**`retention_audit(records, today, holds)`** — records carry `id`, `category` and
`created`. Returns `{"expired": [...], "held": [...], "compliant": bool}`:
`expired` is the sorted ids past their retention period and not under hold,
`held` those that are, and `compliant` is true exactly when `expired` is empty.
Raise `ValueError` for an unknown category.

## Report

**`build_report(model_meta, fairness, privacy, retention, limitations)`** — a dict
with keys `model`, `fairness`, `privacy`, `retention`, `limitations`. `model` keeps
only `name` and `version`. Raise `ValueError` when `limitations` is empty: an audit
that documents no limitation has not been done.

**`canonical(report)`**, **`sign_report(report, key)`** (HMAC-SHA256, hex) and
**`verify_signature(report, key, signature)`** — comparison via
`hmac.compare_digest`, so a report that changed by one digit fails.

**`render(report)`** — markdown, headings `## Fairness`, `## Privacy`,
`## Retention`, `## Limitations`, gaps to three decimals, `flagged: none` when the
list is empty, and `compliant: yes` or `compliant: no`.
''',
        "deliverables": [
            "`toolkit.py` — the four audits, the report builder, the signer and the renderer, importable with no side effects",
            "`main.py` — a run over the supplied sample data that prints the rendered report and its signature",
            "Fairness gaps for all four criteria, with a threshold that is an argument rather than a constant buried in the code",
            "A privacy verdict that reports k, l and the singleton count, not a single opaque risk word",
            "A retention verdict that separates 'should have been deleted' from 'lawfully retained under hold'",
            "A signature over a canonical serialisation, so reordering keys does not change the signature but changing a number does",
        ],
        "constraints": [
            "Standard library only: `json`, `hmac` and `hashlib` are all you need",
            "`toolkit.py` must print nothing on import",
            "Every audit function raises `ValueError` on malformed input rather than returning a partial verdict",
            "`build_report` must refuse an empty limitations list",
            "No metric may be silently reported as `0.0` when its denominator is empty — refuse instead",
        ],
        "rubric": [
            {"criterion": "Metric correctness", "weight": 30,
             "evidence": "All four fairness gaps, k, l and the expired set match hand-computed values on the sample data."},
            {"criterion": "Refusal behaviour", "weight": 25,
             "evidence": "Undefined rates, unknown categories, a single group and an empty limitations list all raise ValueError."},
            {"criterion": "Integrity of the signed report", "weight": 25,
             "evidence": "The signature is stable under key reordering and fails after any change to a value or the key."},
            {"criterion": "Legibility of the output", "weight": 20,
             "evidence": "render() produces the four sections with three-decimal gaps, an explicit flagged line and a yes/no compliance line."},
        ],
        "hints": [
            "Reuse the lab work: `confusion_matrices` and `rates` from module 1 and `equivalence_classes` from module 2 are the whole numeric core.",
            "`flagged` is `sorted(name for name, value in gaps.items() if value > threshold)` — strictly greater, so a gap exactly at the threshold is not flagged.",
            "`canonical` must be the only place that serialises: sign and verify both call it, so they cannot drift apart.",
            "`hmac.new(key.encode(), canonical(report).encode(), hashlib.sha256).hexdigest()` — and compare with `hmac.compare_digest`, not `==`.",
        ],
        "files": [
            {"name": "toolkit.py", "content": r'''
import hashlib
import hmac
import json

RETENTION_DAYS = {"invoice": 2555, "marketing": 365, "support": 730}


def confusion_matrices(rows):
    """group -> {"tp", "fp", "fn", "tn"}. ValueError on a bad label."""
    # your code here


def rates(cm):
    """base_rate, selection_rate, tpr, fpr, ppv; None where undefined."""
    # your code here


def fairness_audit(rows, threshold=0.1):
    """The four group gaps plus the metrics that exceed the threshold."""
    # your code here


def equivalence_classes(records, quasi_ids):
    """Group records on their quasi-identifier values."""
    # your code here


def privacy_audit(records, quasi_ids, sensitive):
    """k, l, the singleton count and a risk band."""
    # your code here


def retention_audit(records, today, holds):
    """Which records outlived their retention period, and which are held."""
    # your code here


def build_report(model_meta, fairness, privacy, retention, limitations):
    """Assemble the report. ValueError when no limitation is documented."""
    # your code here


def canonical(report):
    """Key-order independent JSON serialisation."""
    # your code here


def sign_report(report, key):
    """HMAC-SHA256 of the canonical report, hex."""
    # your code here


def verify_signature(report, key, signature):
    """True when the signature matches the report under this key."""
    # your code here


def render(report):
    """The report as markdown."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from toolkit import (fairness_audit, privacy_audit, retention_audit,
                     build_report, render, sign_report)

ROWS = ([{"group": "A", "y_true": 1, "y_pred": 1}] * 30
        + [{"group": "A", "y_true": 0, "y_pred": 1}] * 20
        + [{"group": "A", "y_true": 1, "y_pred": 0}] * 10
        + [{"group": "A", "y_true": 0, "y_pred": 0}] * 40
        + [{"group": "B", "y_true": 1, "y_pred": 1}] * 10
        + [{"group": "B", "y_true": 0, "y_pred": 1}] * 10
        + [{"group": "B", "y_true": 1, "y_pred": 0}] * 30
        + [{"group": "B", "y_true": 0, "y_pred": 0}] * 50)

RECORDS = [
    {"id": 1, "postcode": "2050", "band": "30-39", "diagnosis": "flu",
     "category": "marketing", "created": 0},
    {"id": 2, "postcode": "2050", "band": "30-39", "diagnosis": "flu",
     "category": "support", "created": 0},
    {"id": 3, "postcode": "2051", "band": "40-49", "diagnosis": "hiv",
     "category": "invoice", "created": 0},
]

META = {"name": "loan-scorer", "version": "2.1.0"}
LIMITS = ["Evaluated on a single quarter of data.",
          "Group B is under-represented in the evaluation set."]

report = build_report(META,
                      fairness_audit(ROWS),
                      privacy_audit(RECORDS, ["postcode", "band"], "diagnosis"),
                      retention_audit(RECORDS, 400, {3}),
                      LIMITS)
print(render(report))
print("signature:", sign_report(report, "shared-secret"))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "toolkit.py", "content": r'''
import hashlib
import hmac
import json

RETENTION_DAYS = {"invoice": 2555, "marketing": 365, "support": 730}


def confusion_matrices(rows):
    """group -> {"tp", "fp", "fn", "tn"}. ValueError on a bad label."""
    out = {}
    for row in rows:
        for key in ("group", "y_true", "y_pred"):
            if key not in row:
                raise ValueError(f"row is missing {key!r}: {row!r}")
        truth, pred = row["y_true"], row["y_pred"]
        if truth not in (0, 1) or pred not in (0, 1):
            raise ValueError(f"labels must be 0 or 1, got {truth!r} and {pred!r}")
        cm = out.setdefault(row["group"], {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
        if truth == 1 and pred == 1:
            cm["tp"] += 1
        elif truth == 0 and pred == 1:
            cm["fp"] += 1
        elif truth == 1 and pred == 0:
            cm["fn"] += 1
        else:
            cm["tn"] += 1
    return out


def rates(cm):
    """base_rate, selection_rate, tpr, fpr, ppv; None where undefined."""
    tp, fp, fn, tn = cm["tp"], cm["fp"], cm["fn"], cm["tn"]
    n = tp + fp + fn + tn
    if n == 0:
        raise ValueError("an empty confusion matrix has no rates")
    ratio = lambda num, den: None if den == 0 else num / den
    return {"base_rate": (tp + fn) / n, "selection_rate": (tp + fp) / n,
            "tpr": ratio(tp, tp + fn), "fpr": ratio(fp, fp + tn),
            "ppv": ratio(tp, tp + fp)}


def _gap(cms, key):
    values = []
    for group in sorted(cms):
        value = rates(cms[group])[key]
        if value is None:
            raise ValueError(f"{key} is undefined for group {group!r}")
        values.append(value)
    return max(values) - min(values)


def fairness_audit(rows, threshold=0.1):
    """The four group gaps plus the metrics that exceed the threshold."""
    cms = confusion_matrices(rows)
    if len(cms) < 2:
        raise ValueError("a group comparison needs at least two groups")
    gaps = {
        "demographic_parity": _gap(cms, "selection_rate"),
        "equal_opportunity": _gap(cms, "tpr"),
        "equalised_odds": max(_gap(cms, "tpr"), _gap(cms, "fpr")),
        "calibration": _gap(cms, "ppv"),
    }
    result = {"groups": sorted(cms)}
    result.update(gaps)
    result["flagged"] = sorted(name for name, value in gaps.items()
                               if value > threshold)
    return result


def equivalence_classes(records, quasi_ids):
    """Group records on their quasi-identifier values."""
    if not quasi_ids:
        raise ValueError("at least one quasi-identifier is required")
    classes = {}
    for record in records:
        key = []
        for field in quasi_ids:
            if field not in record:
                raise ValueError(f"record is missing quasi-identifier {field!r}")
            key.append(record[field])
        classes.setdefault(tuple(key), []).append(record)
    return classes


def privacy_audit(records, quasi_ids, sensitive):
    """k, l, the singleton count and a risk band."""
    classes = equivalence_classes(records, quasi_ids)
    if not classes:
        raise ValueError("an empty table cannot be assessed")
    for group in classes.values():
        for record in group:
            if sensitive not in record:
                raise ValueError(f"record is missing sensitive field {sensitive!r}")
    k = min(len(group) for group in classes.values())
    l = min(len({r[sensitive] for r in group}) for group in classes.values())
    singletons = sum(len(group) for group in classes.values() if len(group) == 1)
    if k < 2:
        risk = "high"
    elif k < 5 or l < 2:
        risk = "medium"
    else:
        risk = "low"
    return {"k": k, "l": l, "singletons": singletons, "risk": risk}


def retention_audit(records, today, holds):
    """Which records outlived their retention period, and which are held."""
    holds = set(holds or ())
    over = []
    for record in records:
        category = record["category"]
        if category not in RETENTION_DAYS:
            raise ValueError(f"unknown category {category!r}")
        if today - record["created"] >= RETENTION_DAYS[category]:
            over.append(record["id"])
    expired = sorted(i for i in over if i not in holds)
    held = sorted(i for i in over if i in holds)
    return {"expired": expired, "held": held, "compliant": not expired}


def build_report(model_meta, fairness, privacy, retention, limitations):
    """Assemble the report. ValueError when no limitation is documented."""
    for key in ("name", "version"):
        if key not in model_meta:
            raise ValueError(f"model metadata is missing {key!r}")
    if not limitations:
        raise ValueError("an audit that documents no limitation is not an audit")
    return {
        "model": {"name": model_meta["name"], "version": model_meta["version"]},
        "fairness": fairness,
        "privacy": privacy,
        "retention": retention,
        "limitations": list(limitations),
    }


def canonical(report):
    """Key-order independent JSON serialisation."""
    return json.dumps(report, sort_keys=True, separators=(",", ":"))


def sign_report(report, key):
    """HMAC-SHA256 of the canonical report, hex."""
    return hmac.new(key.encode("utf-8"), canonical(report).encode("utf-8"),
                    hashlib.sha256).hexdigest()


def verify_signature(report, key, signature):
    """True when the signature matches the report under this key."""
    return hmac.compare_digest(sign_report(report, key), signature)


def render(report):
    """The report as markdown."""
    model = report["model"]
    fair = report["fairness"]
    priv = report["privacy"]
    ret = report["retention"]

    lines = [f"# Accountability report: {model['name']} {model['version']}", ""]

    lines.append("## Fairness")
    lines.append("- groups: " + ", ".join(fair["groups"]))
    for name in ("demographic_parity", "equal_opportunity",
                 "equalised_odds", "calibration"):
        lines.append(f"- {name}: {fair[name]:.3f}")
    lines.append("- flagged: " + (", ".join(fair["flagged"]) if fair["flagged"]
                                  else "none"))
    lines.append("")

    lines.append("## Privacy")
    lines.append(f"- k-anonymity: {priv['k']}")
    lines.append(f"- l-diversity: {priv['l']}")
    lines.append(f"- singleton records: {priv['singletons']}")
    lines.append(f"- risk: {priv['risk']}")
    lines.append("")

    lines.append("## Retention")
    lines.append("- expired and unpurged: "
                 + (", ".join(str(i) for i in ret["expired"]) if ret["expired"]
                    else "none"))
    lines.append("- expired under legal hold: "
                 + (", ".join(str(i) for i in ret["held"]) if ret["held"]
                    else "none"))
    lines.append("- compliant: " + ("yes" if ret["compliant"] else "no"))
    lines.append("")

    lines.append("## Limitations")
    for item in report["limitations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"
'''},
            {"name": "main.py", "content": r'''
from toolkit import (fairness_audit, privacy_audit, retention_audit,
                     build_report, render, sign_report)

ROWS = ([{"group": "A", "y_true": 1, "y_pred": 1}] * 30
        + [{"group": "A", "y_true": 0, "y_pred": 1}] * 20
        + [{"group": "A", "y_true": 1, "y_pred": 0}] * 10
        + [{"group": "A", "y_true": 0, "y_pred": 0}] * 40
        + [{"group": "B", "y_true": 1, "y_pred": 1}] * 10
        + [{"group": "B", "y_true": 0, "y_pred": 1}] * 10
        + [{"group": "B", "y_true": 1, "y_pred": 0}] * 30
        + [{"group": "B", "y_true": 0, "y_pred": 0}] * 50)

RECORDS = [
    {"id": 1, "postcode": "2050", "band": "30-39", "diagnosis": "flu",
     "category": "marketing", "created": 0},
    {"id": 2, "postcode": "2050", "band": "30-39", "diagnosis": "flu",
     "category": "support", "created": 0},
    {"id": 3, "postcode": "2051", "band": "40-49", "diagnosis": "hiv",
     "category": "invoice", "created": 0},
]

META = {"name": "loan-scorer", "version": "2.1.0"}
LIMITS = ["Evaluated on a single quarter of data.",
          "Group B is under-represented in the evaluation set."]

report = build_report(META,
                      fairness_audit(ROWS),
                      privacy_audit(RECORDS, ["postcode", "band"], "diagnosis"),
                      retention_audit(RECORDS, 400, {3}),
                      LIMITS)
print(render(report))
print("signature:", sign_report(report, "shared-secret"))
'''},
        ],
        "tests": [
            {"name": "fairness_audit reproduces the hand-computed gaps", "code": r'''
from toolkit import fairness_audit
_rows = ([{"group": "A", "y_true": 1, "y_pred": 1}] * 30
         + [{"group": "A", "y_true": 0, "y_pred": 1}] * 20
         + [{"group": "A", "y_true": 1, "y_pred": 0}] * 10
         + [{"group": "A", "y_true": 0, "y_pred": 0}] * 40
         + [{"group": "B", "y_true": 1, "y_pred": 1}] * 10
         + [{"group": "B", "y_true": 0, "y_pred": 1}] * 10
         + [{"group": "B", "y_true": 1, "y_pred": 0}] * 30
         + [{"group": "B", "y_true": 0, "y_pred": 0}] * 50)
_f = fairness_audit(_rows)
assert _f["groups"] == ["A", "B"], f"groups came out {_f['groups']!r}"
assert abs(_f["demographic_parity"] - 0.30) < 1e-9, f"got {_f['demographic_parity']!r}"
assert abs(_f["equal_opportunity"] - 0.50) < 1e-9, f"got {_f['equal_opportunity']!r}"
assert abs(_f["equalised_odds"] - 0.50) < 1e-9, f"got {_f['equalised_odds']!r}"
assert abs(_f["calibration"] - 0.10) < 1e-9, f"got {_f['calibration']!r}"
'''},
            {"name": "The threshold is an argument, and the boundary is strict", "code": r'''
from toolkit import fairness_audit
_rows = ([{"group": "A", "y_true": 1, "y_pred": 1}] * 30
         + [{"group": "A", "y_true": 0, "y_pred": 1}] * 20
         + [{"group": "A", "y_true": 1, "y_pred": 0}] * 10
         + [{"group": "A", "y_true": 0, "y_pred": 0}] * 40
         + [{"group": "B", "y_true": 1, "y_pred": 1}] * 10
         + [{"group": "B", "y_true": 0, "y_pred": 1}] * 10
         + [{"group": "B", "y_true": 1, "y_pred": 0}] * 30
         + [{"group": "B", "y_true": 0, "y_pred": 0}] * 50)
assert fairness_audit(_rows, 0.1)["flagged"] == \
    ["demographic_parity", "equal_opportunity", "equalised_odds"], \
    f"got {fairness_audit(_rows, 0.1)['flagged']!r} — calibration sits exactly at 0.1"
assert fairness_audit(_rows, 0.6)["flagged"] == [], "a slack threshold flags nothing"
assert "calibration" in fairness_audit(_rows, 0.05)["flagged"], "a tight threshold flags it"
'''},
            {"name": "fairness_audit refuses what it cannot measure", "code": r'''
from toolkit import fairness_audit
_one = [{"group": "A", "y_true": 1, "y_pred": 1}, {"group": "A", "y_true": 0, "y_pred": 0}]
try:
    fairness_audit(_one)
    assert False, "a single group cannot be compared — that should raise ValueError"
except ValueError:
    pass
_undefined = _one + [{"group": "B", "y_true": 0, "y_pred": 0}]
try:
    fairness_audit(_undefined)
    assert False, "group B has no positives, so TPR is undefined — refuse, do not report 0.0"
except ValueError:
    pass
try:
    fairness_audit([{"group": "A", "y_true": 2, "y_pred": 0},
                    {"group": "B", "y_true": 0, "y_pred": 0}])
    assert False, "a label of 2 should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "privacy_audit reports k, l and the singletons", "code": r'''
from toolkit import privacy_audit
_recs = [{"postcode": "2050", "band": "30-39", "diagnosis": "flu"},
         {"postcode": "2050", "band": "30-39", "diagnosis": "flu"},
         {"postcode": "2051", "band": "40-49", "diagnosis": "hiv"}]
_p = privacy_audit(_recs, ["postcode", "band"], "diagnosis")
assert _p == {"k": 1, "l": 1, "singletons": 1, "risk": "high"}, f"got {_p!r}"
_wide = [{"postcode": "2050", "band": "30-39", "diagnosis": _d}
         for _d in ("flu", "hiv", "cancer", "flu", "gout", "hiv")]
_p = privacy_audit(_wide, ["postcode"], "diagnosis")
assert _p["k"] == 6 and _p["l"] == 4 and _p["singletons"] == 0, f"got {_p!r}"
assert _p["risk"] == "low", f"k = 6 and l = 4 is low risk, got {_p['risk']!r}"
_uniform = [{"postcode": "2050", "diagnosis": "flu"}] * 6
assert privacy_audit(_uniform, ["postcode"], "diagnosis")["risk"] == "medium", \
    "k is large but l is 1, so the sensitive value is still disclosed"
try:
    privacy_audit([], ["postcode"], "diagnosis")
    assert False, "an empty table should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "retention_audit separates overdue from lawfully held", "code": r'''
from toolkit import retention_audit
_recs = [{"id": 1, "category": "marketing", "created": 0},
         {"id": 2, "category": "support", "created": 0},
         {"id": 3, "category": "marketing", "created": 0}]
_r = retention_audit(_recs, 100, set())
assert _r == {"expired": [], "held": [], "compliant": True}, f"got {_r!r}"
_r = retention_audit(_recs, 400, {3})
assert _r["expired"] == [1] and _r["held"] == [3], f"got {_r!r}"
assert _r["compliant"] is False, "an unpurged expired record is a compliance failure"
_r = retention_audit(_recs, 400, {1, 3})
assert _r["expired"] == [] and _r["held"] == [1, 3] and _r["compliant"] is True, \
    f"everything overdue is under hold, so the controller is compliant: {_r!r}"
try:
    retention_audit([{"id": 9, "category": "astrology", "created": 0}], 10, set())
    assert False, "an unknown category should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "build_report insists on a documented limitation", "code": r'''
from toolkit import build_report
_f = {"groups": ["A", "B"], "demographic_parity": 0.3, "equal_opportunity": 0.5,
      "equalised_odds": 0.5, "calibration": 0.1, "flagged": ["equalised_odds"]}
_p = {"k": 1, "l": 1, "singletons": 1, "risk": "high"}
_t = {"expired": [1], "held": [3], "compliant": False}
_rep = build_report({"name": "m", "version": "1", "secret": "x"}, _f, _p, _t, ["a limit"])
assert sorted(_rep) == ["fairness", "limitations", "model", "privacy", "retention"], f"got {sorted(_rep)!r}"
assert _rep["model"] == {"name": "m", "version": "1"}, "only name and version belong in the report"
assert _rep["limitations"] == ["a limit"]
try:
    build_report({"name": "m", "version": "1"}, _f, _p, _t, [])
    assert False, "an empty limitations list should raise ValueError"
except ValueError:
    pass
try:
    build_report({"name": "m"}, _f, _p, _t, ["a limit"])
    assert False, "missing model metadata should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The signature is canonical and key-bound", "code": r'''
from toolkit import build_report, canonical, sign_report, verify_signature
_f = {"groups": ["A", "B"], "demographic_parity": 0.3, "equal_opportunity": 0.5,
      "equalised_odds": 0.5, "calibration": 0.1, "flagged": []}
_p = {"k": 2, "l": 2, "singletons": 0, "risk": "medium"}
_t = {"expired": [], "held": [], "compliant": True}
_rep = build_report({"name": "m", "version": "1"}, _f, _p, _t, ["a limit"])
_sig = sign_report(_rep, "secret")
assert len(_sig) == 64, f"an HMAC-SHA256 hex digest is 64 characters, got {len(_sig)}"
assert verify_signature(_rep, "secret", _sig) is True, "the intact report should verify"
assert verify_signature(_rep, "other-secret", _sig) is False, "a different key must not verify"
_reordered = {_k: _rep[_k] for _k in reversed(sorted(_rep))}
assert canonical(_reordered) == canonical(_rep), "canonical form must ignore key order"
assert verify_signature(_reordered, "secret", _sig) is True, "reordering keys is not a change"
'''},
            {"name": "Any edit to the report breaks the signature", "code": r'''
import copy as _copy
from toolkit import build_report, sign_report, verify_signature
_f = {"groups": ["A", "B"], "demographic_parity": 0.3, "equal_opportunity": 0.5,
      "equalised_odds": 0.5, "calibration": 0.1, "flagged": []}
_p = {"k": 2, "l": 2, "singletons": 0, "risk": "medium"}
_t = {"expired": [], "held": [], "compliant": True}
_rep = build_report({"name": "m", "version": "1"}, _f, _p, _t, ["a limit"])
_sig = sign_report(_rep, "secret")
_tampered = _copy.deepcopy(_rep)
_tampered["fairness"]["equalised_odds"] = 0.05
assert verify_signature(_tampered, "secret", _sig) is False, "a softened metric must be detected"
_dropped = _copy.deepcopy(_rep)
_dropped["limitations"] = ["a limit", "and another"]
assert verify_signature(_dropped, "secret", _sig) is False, "added text must be detected"
assert verify_signature(_rep, "secret", "0" * 64) is False, "a forged signature must not verify"
'''},
            {"name": "render lays out all four sections", "code": r'''
from toolkit import build_report, render
_f = {"groups": ["A", "B"], "demographic_parity": 0.3, "equal_opportunity": 0.5,
      "equalised_odds": 0.5, "calibration": 0.1, "flagged": ["equalised_odds"]}
_p = {"k": 1, "l": 1, "singletons": 1, "risk": "high"}
_t = {"expired": [1], "held": [3], "compliant": False}
_text = render(build_report({"name": "loan-scorer", "version": "2.1.0"},
                            _f, _p, _t, ["Evaluated on one quarter."]))
assert _text.startswith("# Accountability report: loan-scorer 2.1.0"), f"starts {_text[:50]!r}"
_order = ["## Fairness", "## Privacy", "## Retention", "## Limitations"]
_at = [_text.find(_h) for _h in _order]
assert all(_i >= 0 for _i in _at) and _at == sorted(_at), f"section offsets {_at!r}"
assert "- demographic_parity: 0.300" in _text, "gaps are shown to three decimals"
assert "- flagged: equalised_odds" in _text, "the flagged metrics must be named"
assert "- k-anonymity: 1" in _text and "- risk: high" in _text
assert "- compliant: no" in _text, "compliance is a yes or a no, not a bool repr"
assert "- Evaluated on one quarter." in _text, "the limitations are bullets"
'''},
            {"name": "An empty flagged list and a clean run read plainly", "code": r'''
from toolkit import build_report, render
_f = {"groups": ["A", "B"], "demographic_parity": 0.01, "equal_opportunity": 0.02,
      "equalised_odds": 0.02, "calibration": 0.0, "flagged": []}
_p = {"k": 8, "l": 4, "singletons": 0, "risk": "low"}
_t = {"expired": [], "held": [], "compliant": True}
_text = render(build_report({"name": "m", "version": "1"}, _f, _p, _t, ["None material."]))
assert "- flagged: none" in _text, "an empty flagged list reads as none, not as []"
assert "- expired and unpurged: none" in _text, f"missing from:\n{_text}"
assert "- compliant: yes" in _text
assert "- calibration: 0.000" in _text, "a zero gap is still reported to three decimals"
'''},
            {"name": "toolkit.py is import-clean", "code": r'''
_src = open("toolkit.py").read()
assert "print(" not in _src, "toolkit.py defines the audits; the printing belongs in main.py"
'''},
        ],
    },
}
