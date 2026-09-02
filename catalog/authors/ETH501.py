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
            "read": [
                {
                    "title": "Four gaps from one table, and the two that cannot both close",
                    "minutes": 14,
                    "body": r'''
A bank runs a model that scores loan applications and flags some of them for
approval. A year on, someone in the risk team pulls the evaluation set — every scored
application whose true outcome is now known — and splits it by the applicant's
neighbourhood into two groups, A and B. Each group gets a two-by-two table: the model
said yes or no, and the applicant did or did not repay. For group A the table reads
30 flagged and repaid, 20 flagged and defaulted, 10 not flagged but would have repaid,
40 not flagged and would have defaulted. For group B the same four cells read 10, 10,
30, 50. Two hundred applications, eight numbers, and somewhere in those eight numbers
is the answer to the question a regulator is about to ask: does this model treat the
two groups the same?

There is no single answer, and this reading is about why. There are at least four
defensible ways to read "the same" off those two tables, and the arithmetic below
shows that two of them cannot both hold once the groups differ in a way no classifier
controls.

## Everything comes from one table per group

Call the four cells by their usual names. A *true positive* is an applicant the model
flagged who repaid; a *false positive* was flagged and defaulted; a *false negative*
was not flagged and would have repaid; a *true negative* was not flagged and would
have defaulted. For group A that is $tp = 30$, $fp = 20$, $fn = 10$, $tn = 40$, and
$n = 100$.

Every rate in this module is a ratio of some of those cells to some others, and each
ratio answers a different question. Two of them divide by the whole group. The *base
rate* is the fraction who really would repay, $(tp + fn) / n$ — the people who
repaid, whether the model noticed or not. The *selection rate* is the fraction the
model said yes to, $(tp + fp) / n$ — the people flagged, whether they deserved it or
not. Those two look alike on the page and are about different things: the base rate
is a fact about the applicants, the selection rate a fact about the model.

The other three divide by a row or a column of the table rather than by $n$. The
*true positive rate* asks, of the people who would repay, what fraction did the model
flag: $tp / (tp + fn)$. The *false positive rate* asks, of the people who would
default, what fraction did it flag anyway: $fp / (fp + tn)$. And the *positive
predictive value* turns the question round — of the people the model flagged, what
fraction repaid: $tp / (tp + fp)$. The first two are conditioned on the truth; the
third is conditioned on the model's verdict. Hold onto that difference, because it
is the whole of the incompatibility later.

```text
group A          repaid   defaulted
flagged            30        20        selected  50 of 100
not flagged        10        40        would repay 40 of 100

base_rate       = 40 / 100 = 0.40
selection_rate  = 50 / 100 = 0.50
tpr             = 30 / 40  = 0.75
fpr             = 20 / 60  = 0.333
ppv             = 30 / 50  = 0.60
```

Group B, with cells 10, 10, 30, 50, works out to a base rate of 0.40, a selection rate
of 0.20, a TPR of 0.25, an FPR of 0.167 and a PPV of 0.50. Notice the base rates
agree: the two neighbourhoods contain the same proportion of people who would repay.
Everything else differs.

## Four criteria, four gaps

Each fairness criterion in this module picks one of those rates and asks that it be
equal across groups, and the *gap* is how far from equal it is — the largest group
value minus the smallest. With one group there is nothing to compare and the gap is
zero by construction.

*Demographic parity* asks for equal selection rates: the model should say yes to the
same fraction of each group. It looks at the verdicts and ignores the outcomes
entirely, which is both its appeal — it needs no ground truth — and its weakness,
since a model that flags people at random satisfies it perfectly. Here the gap is
$0.50 - 0.20 = 0.30$.

*Equal opportunity* asks for equal true positive rates: among the people who would
repay, each group should be found at the same rate. The gap is $0.75 - 0.25 = 0.50$,
and it is the most damning number in the table. Three quarters of group A's good
borrowers were flagged; one quarter of group B's were.

*Equalised odds* asks for equal TPR *and* equal FPR — the model's error profile
should be the same in both groups. Its gap is the larger of the two component gaps,
which here is the TPR gap, 0.50, since the FPR gap is only $0.333 - 0.167 = 0.167$.

*Calibration* asks for equal PPV: a "yes" from the model should mean the same thing
whichever group you are in. The gap is $0.60 - 0.50 = 0.10$, the smallest of the
four.

```python
def rates(cm):
    tp, fp, fn, tn = cm["tp"], cm["fp"], cm["fn"], cm["tn"]
    n = tp + fp + fn + tn
    ratio = lambda num, den: None if den == 0 else num / den
    return {"base_rate": (tp + fn) / n, "selection_rate": (tp + fp) / n,
            "tpr": ratio(tp, tp + fn), "fpr": ratio(fp, fp + tn),
            "ppv": ratio(tp, tp + fp)}

A = rates({"tp": 30, "fp": 20, "fn": 10, "tn": 40})
B = rates({"tp": 10, "fp": 10, "fn": 30, "tn": 50})
for key in ("base_rate", "selection_rate", "tpr", "fpr", "ppv"):
    print(f"{key:15s} A={A[key]:.3f}  B={B[key]:.3f}  gap={abs(A[key] - B[key]):.3f}")
```

The output is the five rows of the table above with the gaps in a third column:
0.000 for the base rate, 0.300 for selection, 0.500 for TPR, 0.167 for FPR and
0.100 for PPV. Those are the numbers the lab's tests check to nine decimal places.

So is the bank's model fair? By calibration, nearly. By equal opportunity, not at all.
The same eight numbers, honestly computed, support both sentences. That is not a flaw
in the metrics — it is the reason this module asks for all four rather than one, and
the reason the last section of this reading is about writing down which one you
chose and why.

## The rate the model does not own

The base rate is where the trouble starts. In the bank's data both groups had a base
rate of 0.40, which is convenient and unusual. Suppose instead that group A's is 0.10
and group B's is 0.50 — one neighbourhood where a tenth of applicants would repay, one
where half would. That is a fact about the applicants, and no adjustment to the model
changes it.

Now suppose the bank has done the hard work and achieved equalised odds: the model has
a TPR of 0.80 and an FPR of 0.20 in *both* groups. What does a "yes" mean in each?
Count it out for a group of $n$ people with base rate $b$. There are $nb$ people who
would repay, and the model catches a fraction $\text{tpr}$ of them, so
$tp = nb \cdot \text{tpr}$. There are $n(1 - b)$ who would default, and the model
wrongly flags a fraction $\text{fpr}$ of those, so $fp = n(1 - b) \cdot \text{fpr}$.
The PPV is $tp / (tp + fp)$, and the $n$ cancels:

$$\text{ppv} = \frac{b \cdot \text{tpr}}{b \cdot \text{tpr} + (1 - b) \cdot \text{fpr}}$$

This is Chouldechova's identity, and the thing to see in it is what is *not* there.
Once TPR and FPR are fixed, PPV is a function of the base rate alone. Two groups with
the same error profile and different base rates get different PPVs, and no threshold
setting alters that, because moving the threshold changes TPR and FPR for both groups
at once and the base rates stay where they were.

```python
def ppv_from_rates(b, tpr, fpr):
    return b * tpr / (b * tpr + (1 - b) * fpr)

print(round(ppv_from_rates(0.10, 0.8, 0.2), 3))
print(round(ppv_from_rates(0.50, 0.8, 0.2), 3))
```

For group A: $0.10 \times 0.8 = 0.08$ on top, $0.08 + 0.90 \times 0.2 = 0.26$
underneath, PPV $= 0.308$. For group B: $0.40$ over $0.40 + 0.10$, PPV $= 0.800$.
The block prints `0.308` and `0.8`. A "yes" in group A is right less than a third of
the time; a "yes" in group B is right four times in five. The model with equalised
odds is badly miscalibrated, with a gap of 0.49, and it is miscalibrated *because* it
has equalised odds. Turn it round and the same identity says that a model calibrated
across groups with unequal base rates must have unequal TPR or FPR. You may have one
or the other. The lab's `impossibility_demo` is this paragraph as a function.

## Where it stops holding

The identity has two escape hatches, and both are worth knowing because they are the
cases a colleague will bring up. If the base rates are equal, PPV is the same
function of the same inputs in both groups and the two criteria coexist — the bank's
original data was such a case, which is why its calibration gap was small while its
odds gap was large rather than the other way round. And if $\text{fpr} = 0$, the
denominator collapses to $b \cdot \text{tpr}$ and PPV is 1 in every group whatever
the base rate: a model that never flags a defaulter is trivially calibrated. Real
models are not that model, and real groups do not share base rates, so in practice
the incompatibility is a law rather than a curiosity.

There is a broader limit too. Every criterion here is a statement about a *group*
average. A model can have a zero gap on all four and still do something indefensible
to a particular applicant, and splitting each group by a second attribute — age
within neighbourhood — can expose gaps that the coarser split averaged away. Group
metrics are where an audit starts, not where it finishes.

## The mistake: writing zero where there is nothing

A rate with a zero denominator is undefined. If group C contains nobody who would
repay, its TPR is $0 / 0$, and the tempting thing to write is `0.0` — it is a number,
the code keeps running, and the report comes out complete. But `0.0` has a meaning:
it says the model found *none* of group C's good borrowers, and compared with A's
0.75 it yields an equal-opportunity gap of 0.75 out of thin air. The report now
accuses the model of something the data cannot speak to.

```python
def tpr(cm):
    positives = cm["tp"] + cm["fn"]
    return None if positives == 0 else cm["tp"] / positives

C = {"tp": 0, "fp": 0, "fn": 0, "tn": 7}
print(tpr({"tp": 30, "fp": 20, "fn": 10, "tn": 40}), tpr(C))
```

That prints `0.75 None`. The lab's `rates` returns `None` for an undefined rate and
its `gap` refuses to compare a `None`, naming the group and the rate in the error.
An audit tool that cannot measure something must say so rather than print a zero,
because the zero will be read, and it will be read as a finding.

## A number is not an audit

The gaps above are 0.30, 0.50, 0.50 and 0.10. Which of them is a problem? That
depends on a threshold, and the threshold is a decision somebody has to own. One
real anchor is the "four-fifths rule" used in US employment law, which flags a
selection *ratio* below 0.8 — here B's 0.20 against A's 0.50 is a ratio of 0.4, far
under it. A difference threshold of 0.1 is another common choice, and it is what the
capstone defaults to. Neither is right in general; the record of an audit is the
number, the threshold, and the sentence explaining why that threshold and not another.

## What you are about to build

The lab in this module, *A group-fairness metric suite*, is the code behind this
reading. `confusion_matrices` turns rows of `{"group", "y_true", "y_pred"}` into one
four-cell table per group and refuses a label that is not 0 or 1; `rates` computes
the five rates with `None` where a denominator is empty; `gap` takes the spread of
one rate across groups and raises when any group cannot supply it. The four one-line
criteria sit on top of `gap`. `ppv_from_rates` is the identity, and
`impossibility_demo` feeds it two base rates under one error profile and reports
whether the PPVs agree to within $10^{-9}$. When you run the starter's last line you
should see `0.308` and `0.8` again, and a `calibrated` of `False` that no argument
you pass can turn into `True` while the base rates differ.
''',
                },
            ],
            "quiz": {
                "title": "Which criterion, and what it can and cannot tell you",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Group A's confusion matrix is $tp=30, fp=20, fn=10, tn=40$ and group B's is $tp=10, fp=10, fn=30, tn=50$. Both groups have a base rate of 0.40. What does the equal-opportunity gap of 0.50 say?",
                        "opts": [
                            "The model flags 50% more of group A overall, so the selection rates differ by half",
                            "Among the people who would repay, group A is flagged at 0.75 and group B at 0.25",
                            "A flagged applicant in group A repays 50 percentage points more often than one in B",
                            "Group A's applicants default half as often as group B's, so base rates differ",
                        ],
                        "a": 1,
                        "whys": [
                            r"That is the demographic-parity gap, which compares selection rates (0.50 against 0.20, a gap of 0.30). Equal opportunity conditions on the truth: only the people who would repay are counted.",
                            r"TPR is $tp / (tp + fn)$: $30/40$ for A and $10/40$ for B. Three quarters of A's good borrowers were found; one quarter of B's.",
                            r"That would be a calibration gap, which conditions on the model's verdict rather than the truth. The PPVs here are 0.60 and 0.50, a gap of 0.10, not 0.50.",
                            r"The base rates are equal — 40 of 100 in both groups. The 0.50 is entirely the model's doing, which is what makes it a finding about the model rather than about the applicants.",
                        ],
                        "why": r"""
Equal opportunity conditions on the truth: of the people who would repay, what
fraction did the model flag? For A that is $30/40 = 0.75$, for B it is $10/40 = 0.25$.
The base rates are identical, so nothing about the applicants explains the gap; the
model finds good borrowers in one neighbourhood three times as readily as in the
other. Demographic parity looks at selection rates (0.30 apart) and calibration at
PPVs (0.10 apart); each is a different question about the same eight numbers.
""",
                    },
                    {
                        "q": "A model has TPR 0.8 and FPR 0.2 in both groups. Group A's base rate is 0.1 and group B's is 0.5. Why is the model miscalibrated, with PPVs of about 0.31 and 0.80?",
                        "opts": [
                            "The threshold was set on group B's scores, so it sits in the wrong place for group A",
                            "Equalised odds was only approximately achieved, and the residual error shows up in PPV",
                            "With TPR and FPR fixed, PPV depends on the base rate alone, and the base rates differ",
                            "The evaluation set is too small in group A for its PPV to be estimated reliably",
                        ],
                        "a": 2,
                        "whys": [
                            r"A threshold that differs between groups would give them different TPR and FPR. These groups have the same TPR and FPR, so the same threshold behaviour applies to both; the identity says that is exactly what forces the PPVs apart.",
                            r"The TPR and FPR are stated as equal, not approximately equal, and the identity still yields 0.308 against 0.800. The miscalibration is not residual error; it is what equal error rates produce under unequal base rates.",
                            r"$\text{ppv} = b\cdot\text{tpr} / (b\cdot\text{tpr} + (1-b)\cdot\text{fpr})$ has nothing in it but $b$ once the error rates are fixed.",
                            r"No sample size is involved — these are population rates fed into an identity. A larger group A would give the same 0.308, because 0.308 is what a 0.1 base rate under (0.8, 0.2) must produce.",
                        ],
                        "why": r"""
Count a group of $n$ with base rate $b$: $tp = nb\cdot\text{tpr}$ and
$fp = n(1-b)\cdot\text{fpr}$, so
$\text{ppv} = b\cdot\text{tpr} / (b\cdot\text{tpr} + (1-b)\cdot\text{fpr})$.
With TPR and FPR pinned, the only thing left to vary is
$b$: $0.08/0.26 = 0.308$ for A and $0.40/0.50 = 0.800$ for B. The miscalibration is
not an artefact of thresholds or sample size; it is what equalised odds costs
whenever the base rates differ, and moving the threshold changes both groups' error
rates together without touching the base rates at all.
""",
                    },
                    {
                        "q": "In an audit, one group contains no applicant who would have repaid. What should `rates` report for that group's true positive rate?",
                        "opts": [
                            "Zero, because the model found none of the group's good borrowers, and there were none",
                            "`None`, because the rate is undefined and a gap built on it would be a finding from nothing",
                            "One, because the model cannot have missed a good borrower when there was none to miss",
                            "The group's selection rate, as the nearest defined quantity that measures roughly the same thing",
                        ],
                        "a": 1,
                        "whys": [
                            r"Zero reads as a finding — the model caught none of them — and against another group's 0.75 it manufactures an equal-opportunity gap of 0.75 from nothing. There were no good borrowers to catch, so no catch rate exists.",
                            r"$0/0$ carries no evidence about the model. The lab's `gap` refuses a `None` and names the group, so the report says what it cannot measure rather than printing a number that will be read.",
                            r"One is as invented as zero. A rate of 1 claims the model found every good borrower, and there is no observation behind that claim either; the denominator is empty, so any value is fiction.",
                            r"The selection rate conditions on nothing and counts flagged defaulters as well; it does not measure how good borrowers are treated. Substituting it changes the question while keeping the label.",
                        ],
                        "why": r"""
A rate with an empty denominator is not a small number or a large one; it is not a
number. The tempting substitute is zero, because the code keeps running, but zero
has a meaning — the model found nobody — and it will be compared with the other
groups and reported as a gap. The lab returns `None`, and `gap` raises a
`ValueError` naming the group and the rate, so that an audit says "cannot measure"
in the one place where the alternative is a fabricated finding.
""",
                    },
                    {
                        "q": "A colleague proposes fixing the calibration gap between two groups with unequal base rates by using a different score threshold for each group. What happens?",
                        "opts": [
                            "It works: separate thresholds let each group's PPV be set independently while TPR and FPR stay equal",
                            "It cannot work at all: PPV is fixed by the base rate and no change to the model alters it",
                            "It can equalise PPV, but only by giving the groups different TPR or FPR, so equalised odds is lost",
                            "It equalises the selection rates instead, which is demographic parity rather than calibration",
                        ],
                        "a": 2,
                        "whys": [
                            r"Changing a group's threshold changes that group's TPR and FPR; that is the only lever a threshold has. If both remain equal across groups the identity says PPV is unchanged, so the gap cannot close without breaking equalised odds.",
                            r"PPV is fixed by the base rate only once TPR and FPR are held fixed. Release them — different thresholds per group — and PPV moves. What the identity forbids is having both criteria, not having calibration.",
                            r"PPV depends on $b$, TPR and FPR together; with $b$ unequal, equal PPV needs unequal error profiles. That is the trade the identity describes.",
                            r"A per-group threshold moves every rate in that group — selection rate, TPR, FPR and PPV together. It could be tuned to equalise PPV; whether it also equalises selection rates is a separate accident.",
                        ],
                        "why": r"""
Chouldechova's identity ties three things together: base rate, error profile
(TPR, FPR) and PPV. With unequal base rates you can hold the error profile equal
and accept unequal PPVs, or hold PPV equal by letting the error profiles differ.
Per-group thresholds do the second — they are the standard way to buy calibration —
and the price is equalised odds. The identity does not say calibration is
unreachable; it says both criteria together are, and an audit should record which
one was chosen and why.
""",
                    },
                    {
                        "q": "A fairness report states: `demographic_parity = 0.30, equal_opportunity = 0.50, calibration = 0.10`. What is missing before it counts as an audit?",
                        "opts": [
                            "The equalised-odds gap, since three criteria cannot be interpreted without the fourth",
                            "The threshold each gap is judged against and the reason that threshold was chosen",
                            "A single combined fairness score, so the reader is not left to weigh three numbers",
                            "The base rate of each group, without which none of the three gaps can be computed",
                        ],
                        "a": 1,
                        "whys": [
                            r"Adding a fourth number leaves the same problem: four gaps and no line saying which are acceptable. Equalised odds is worth reporting, but it is not what turns numbers into a verdict.",
                            r"A gap of 0.10 is a problem under a 0.05 threshold and fine under 0.2. The threshold is a decision, and the record of the decision is the audit.",
                            r"Collapsing incompatible criteria into one score hides which one was sacrificed. The point of computing four is that they disagree; a weighted average erases the disagreement it should be reporting.",
                            r"The three gaps are already computed, so their inputs were available. Base rates are worth reporting for interpretation, but the gaps do not depend on being told them again.",
                        ],
                        "why": r"""
The three numbers are honest and incomplete. Whether 0.10 is acceptable depends on
a threshold, and the threshold is a choice somebody must own: the four-fifths
ratio, a 0.1 difference, something stricter for a high-stakes decision. An audit
records the number, the threshold, and the reason for that threshold, so that a
reader can disagree with the choice rather than wonder whether one was made.
Combining the gaps into one score, or adding more gaps, does not supply the missing
decision.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Six patients, a voter roll, and the price of a number",
                    "minutes": 15,
                    "body": r'''
In the mid-1990s the Massachusetts Group Insurance Commission released hospital
discharge records for state employees to researchers. Names, addresses and social
security numbers had been stripped; what remained was medical and, for each row, the
patient's date of birth, sex and five-digit ZIP code. Latanya Sweeney, then a graduate
student, bought the Cambridge voter roll for twenty dollars. It listed name, address,
date of birth, sex and ZIP. Six people in the voter roll shared the governor's birth
date; three of them were men; one of those lived in his ZIP code. She posted his
hospital records to his office. Her later estimate was that date of birth, sex and
ZIP alone pick out about 87% of the US population uniquely.

None of the three fields is an identifier. Together they are, and that is the picture
the first half of this reading is built on: the fields that re-identify someone are
the ones that look harmless on their own. The second half is about a different idea
altogether — not scrubbing a table so that it can be released, but answering questions
about it with a controlled amount of noise, and keeping an account of how much you
have spent.

## Quasi-identifiers and the smallest crowd

Take the six-row table from this module's lab:

```text
age  postcode  diagnosis
34   2050      flu
36   2051      flu
31   2052      cancer
47   2050      flu
42   2051      hiv
45   2052      flu
```

`diagnosis` is the sensitive field, the thing we do not want linked to a person.
`age` and `postcode` are *quasi-identifiers*: nobody is identified by being 34, or by
living in 2050, but an attacker with a voter roll who knows that a 34-year-old in 2050
is in the table finds exactly one row.

The measure of that risk is how small a crowd each person hides in. Group the rows by
their quasi-identifier values — every row with the same (age, postcode) lands in the
same *equivalence class* — and the size of the smallest class is the table's
$k$-anonymity. If every class has at least $k$ members, an attacker who knows a
person's quasi-identifiers can narrow them to $k$ rows and no further. On (age,
postcode) every row here is alone: $k = 1$, and the table is Sweeney's hospital data
in miniature. On postcode alone the classes are 2050 with two rows, 2051 with two and
2052 with two, so $k = 2$.

```python
def classes(records, quasi_ids):
    out = {}
    for r in records:
        out.setdefault(tuple(r[f] for f in quasi_ids), []).append(r)
    return out

def k_anonymity(records, quasi_ids):
    c = classes(records, quasi_ids)
    return min(len(g) for g in c.values()) if c else 0

def l_diversity(records, quasi_ids, sensitive):
    c = classes(records, quasi_ids)
    return min(len({r[sensitive] for r in g}) for g in c.values()) if c else 0

PATIENTS = [
    {"age": 34, "postcode": "2050", "diagnosis": "flu"},
    {"age": 36, "postcode": "2051", "diagnosis": "flu"},
    {"age": 31, "postcode": "2052", "diagnosis": "cancer"},
    {"age": 47, "postcode": "2050", "diagnosis": "flu"},
    {"age": 42, "postcode": "2051", "diagnosis": "hiv"},
    {"age": 45, "postcode": "2052", "diagnosis": "flu"},
]
print(k_anonymity(PATIENTS, ["age", "postcode"]))
print(k_anonymity(PATIENTS, ["postcode"]),
      l_diversity(PATIENTS, ["postcode"], "diagnosis"))
```

The block prints `1` and then `2 1`. The `1` on the second line is the part people
miss.

## The crowd that all have the same secret

Postcode 2050 holds two patients, so an attacker who knows their neighbour is in the
table and lives in 2050 cannot tell which row is theirs. It does not matter. Both
rows say flu. The attacker learns the diagnosis without ever learning the row, and
$k = 2$ did nothing to stop it. This is the *homogeneity attack*, and the number
that catches it is $l$-diversity: within each class, how many distinct sensitive
values are there? The smallest such count across classes is $l$. For postcode 2050
it is one, so the table's $l$ is 1 whatever its $k$.

The two numbers answer different questions. $k$ asks whether a person can be found;
$l$ asks whether, found or not, their secret can be. A table needs both, and the lab
computes them separately for that reason.

## Buying $k$ with precision

How do you raise $k$ on a table that is already collected? You cannot invent people,
so you make the existing ones less distinguishable. *Generalisation* replaces a
value with a coarser one: age 34 becomes the bucket "20-39". *Suppression* drops the
rows whose class is still too small after that.

Generalise the ages into buckets of width 20. The bucket floor is
$\lfloor 34 / 20 \rfloor \times 20 = 20$ and the label runs to $20 + 20 - 1$, so 34,
36 and 31 all become "20-39" and 47, 42 and 45 all become "40-59". On the bucketed
age alone the classes are two groups of three: $k = 3$. Within "20-39" the diagnoses
are flu, flu, cancer — two distinct values — and within "40-59" they are flu, hiv,
flu, also two. So $l = 2$. The lab's starter prints `3 2` for this, and the tests
check that the original table was left untouched: generalisation returns copies.

What did it cost? Before, the table could answer "how many patients are in their
thirties?" exactly: four. After, the question cannot be answered at all — "20-39"
lumps a 31-year-old with a 39-year-old who is not there and hides the 34 and 36 among
them. Every step of generalisation trades a specific question for a wider crowd, and
the trade is the whole point rather than a side effect. Suppression is the same trade
at its limit: a row dropped answers no question at all. On the raw (age, postcode)
key, suppressing to $k = 2$ removes every row.

## Where $k$-anonymity stops holding

Raising $k$ and $l$ makes one table safer against one attacker who knows one set of
quasi-identifiers. It says nothing about an attacker who knows more fields than you
guessed, and it says nothing about two releases side by side: a table generalised on
age and the same table generalised on postcode can be joined on the sensitive field
to recover what each hid alone. There is no arithmetic that tells you how a
$k$-anonymous release composes with the next one. That gap is what the second idea
was invented to close.

## A promise about the mechanism, not the table

Change the picture. Instead of releasing the table, you answer questions about it —
"how many patients have flu?" — and you promise every patient that the answer would
have been almost the same had their row been absent. Write $D$ for the table and $D'$
for the table with one row removed or changed. A randomised mechanism $M$ is
$\varepsilon$-differentially private if for every possible output $S$,

$$\Pr[M(D) \in S] \le e^{\varepsilon} \cdot \Pr[M(D') \in S]$$

The promise is about $M$, the procedure, and it holds for every pair of neighbouring
tables at once. This is why differential privacy is a property of the mechanism and
not of anything you release: the same noisy number, produced by a different procedure,
carries no guarantee.

To build such an $M$ for a count, ask how much one row can move the true answer. A
count changes by at most 1 when a row comes or goes; that is the query's
*sensitivity*, $\Delta f = 1$. Now add noise drawn from the Laplace distribution with
scale $b$, whose density is proportional to $e^{-|x| / b}$. At any output $x$, the
density under true count $c$ against true count $c + 1$ is the ratio
$e^{(|x - c - 1| - |x - c|) / b}$, and the exponent's numerator is at most 1 in
absolute value. So the ratio is at most $e^{1/b}$. Set $b = 1 / \varepsilon$ and it
is at most $e^{\varepsilon}$, which is the promise. For a query with sensitivity
$\Delta f$ the same argument gives $b = \Delta f / \varepsilon$. Nothing was announced
here: the scale is what the inequality demands.

## Drawing the noise from one uniform number

The lab asks for a Laplace sample from a single call to `rng.random()`, and the
route is the inverse of the distribution function. For $x \ge 0$ the Laplace CDF is
$F(x) = 1 - \tfrac{1}{2} e^{-x/b}$, and by symmetry $F(x) = \tfrac{1}{2} e^{x/b}$ for
$x < 0$. Take $u$ uniform on $(-\tfrac{1}{2}, \tfrac{1}{2})$; for positive $u$ solve
$\tfrac{1}{2} + u = 1 - \tfrac{1}{2} e^{-x/b}$, which gives $e^{-x/b} = 1 - 2u$ and
$x = -b \ln(1 - 2u)$. The negative side mirrors it, and both halves fold into

$$x = -b \cdot \operatorname{sign}(u) \cdot \ln(1 - 2|u|)$$

Trace one draw. With `random.Random(3)` the first `random()` is about 0.238, so
$u \approx -0.262$; $1 - 2|u| \approx 0.476$; $\ln 0.476 \approx -0.742$; the sign is
negative, so $x = -1 \cdot (-1) \cdot (-0.742) \approx -0.742$ at scale 1.

```python
import math
import random
import statistics

def laplace_noise(rng, scale):
    u = rng.random() - 0.5
    sign = -1.0 if u < 0 else 1.0
    return -scale * sign * math.log(max(1e-12, 1 - 2 * abs(u)))

print(round(laplace_noise(random.Random(3), 1.0), 3))
rng = random.Random(7)
draws = [laplace_noise(rng, 2.0) for _ in range(4000)]
print(round(statistics.fmean(draws), 2),
      round(statistics.fmean(abs(d) for d in draws), 2))
```

The first line prints `-0.742`, the trace above. The second prints `-0.06 2.03`:
four thousand draws at scale 2 average close to zero and their mean absolute size is
close to 2, because the mean absolute deviation of Laplace$(0, b)$ is $b$ exactly.
That second number is what the lab's test measures, and it is the reason the scale
is worth reading as "how far off, typically, the answer will be."

## The mistake: asking twice

Here is where people's intuition fails. Release the flu count with
$\varepsilon = 0.5$, so the noise has scale 2. The true count is 4; one answer might
be 3.8. An analyst who is told "the answer is private, ask whatever you like" asks
again, and again, a hundred times, and averages.

```python
import math
import random
import statistics

def laplace_noise(rng, scale):
    u = rng.random() - 0.5
    sign = -1.0 if u < 0 else 1.0
    return -scale * sign * math.log(max(1e-12, 1 - 2 * abs(u)))

rng = random.Random(11)
answers = [4 + laplace_noise(rng, 2.0) for _ in range(100)]
print(round(answers[0], 1), round(statistics.fmean(answers), 1))
```

That prints `3.8 3.9`. One answer was uncertain to about $\pm 2$; a hundred of them
pin the true count to a tenth. The noise did not fail — each answer honoured its
$\varepsilon$ — but the promises multiplied. Run the inequality twice and the ratio
bound is $e^{\varepsilon_1} \cdot e^{\varepsilon_2} = e^{\varepsilon_1 +
\varepsilon_2}$: epsilons *add*. This is sequential composition, and it turns
$\varepsilon$ from a per-query parameter into a *budget*. A hundred queries at 0.5
have spent 50, and a promise at $\varepsilon = 50$ is no promise at all, since
$e^{50}$ bounds nothing.

The tempting version of the mistake is subtler than asking a hundred times. It is
adding noise "for privacy" without any account of how much has been added to what,
which feels careful and is equivalent to keeping no budget. The lab's
`PrivacyBudget` is the account: `spend` charges before an answer is computed, so a
refused query leaks nothing by having run, and `dp_count` will not answer without
paying.

## Where the noise stops helping

$\varepsilon$ is a knob with no rule attached. Scale 2 on a count of 4 is noise the
same size as the answer, which is useless for six patients and negligible for a count
of six million. Differential privacy earns its keep on large populations and exact
aggregates; on a tiny table it protects everyone by telling nobody anything. And the
promise is about your mechanism only. If an attacker already knew five of the six
diagnoses, the sixth was never yours to protect. Sweeney's governor was undone by a
release, not a query, and the lesson the two halves share is that protection is
something you measure and pay for, never something a table has by looking harmless.

## What you are about to build

The lab, *k-anonymity, l-diversity and an epsilon budget*, is the code for both
halves. `equivalence_classes` groups records on a tuple of quasi-identifier values
and refuses an empty field list; `k_anonymity` and `l_diversity` read the smallest
class and the fewest distinct secrets from it. `generalise_numeric` buckets a numeric
field into width-$w$ labels on copies of the records, and `suppress` drops the rows
whose class is under $k$. Then `laplace_noise` is the inverse-transform draw above,
`PrivacyBudget` keeps the ledger, and `dp_count` charges the budget, counts, and adds
noise at scale $1 / \varepsilon$. The tests measure the noise's mean absolute
deviation, check that twenty queries at 0.5 spend a budget of 10 to the last decimal,
and check that a refused query is not charged.
''',
                },
            ],
            "quiz": {
                "title": "Crowds, secrets and the epsilon ledger",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A released table has $k = 5$ on its quasi-identifiers. An attacker knows their neighbour is in it and knows the neighbour's quasi-identifier values. What can the attacker still learn?",
                        "opts": [
                            "Nothing, because five candidate rows is the definition of the neighbour being unidentifiable",
                            "The neighbour's sensitive value, whenever the five rows in that class all share the same one",
                            "Which row is the neighbour's, by eliminating the four rows with the wrong sensitive value",
                            "Only that the neighbour is present, which $k$-anonymity has never claimed to conceal",
                        ],
                        "a": 1,
                        "whys": [
                            r"Five candidate rows hide which row is theirs. If those five rows all say the same diagnosis, the attacker never needed to know which row: the class discloses the secret while $k$ holds.",
                            r"$k$ bounds how well a person can be located; it says nothing about the sensitive column. That is what $l$-diversity measures separately.",
                            r"The attacker does not know the sensitive value to eliminate by — it is the thing being sought. Elimination runs the other way: a homogeneous class hands over the value without any row being singled out.",
                            r"Presence is assumed in the setup, so it is not the disclosure at stake. A homogeneous class discloses the sensitive value itself, which is the disclosure $k$-anonymity was supposed to prevent and does not.",
                        ],
                        "why": r"""
$k$-anonymity guarantees a crowd of at least $k$ rows around every person. It
makes no promise about what those rows say. If the five rows in a class all carry
the same diagnosis, the attacker learns the diagnosis without learning the row —
the homogeneity attack — and the table's $l$-diversity is 1. Both numbers are
needed: $k$ for whether a person can be found, $l$ for whether their secret can be
read off the crowd they hide in.
""",
                    },
                    {
                        "q": "Generalising the six patients' ages into buckets of width 20 lifts $k$ from 1 to 3. What did that step cost?",
                        "opts": [
                            "Three of the six records, which had to be suppressed to make the remaining classes large enough",
                            "Nothing measurable: the same six records are present, so every query on the table still answers",
                            "Any question about age finer than the bucket, such as how many patients are in their thirties",
                            "The $l$-diversity of the table, since coarser classes pull more identical diagnoses together",
                        ],
                        "a": 2,
                        "whys": [
                            r"Generalisation keeps every row; it is suppression that drops rows. After bucketing, all six records remain and the classes are two groups of three.",
                            r"The records are present but their ages are gone, replaced by labels. \"How many patients are in their thirties?\" had an exact answer, four, and now has none — the utility loss is the mechanism, not a side effect.",
                            r"Every step of generalisation buys anonymity by destroying a specific question. That is the trade, and the lab has you measure both sides of it.",
                            r"On this table $l$ went from 1 (on postcode) to 2 (on the bucketed age): each class holds two distinct diagnoses. Coarser classes can raise or lower $l$; it is a separate measurement, not a fixed cost.",
                        ],
                        "why": r"""
Generalisation replaces 34 with "20-39" on a copy of each record. All six rows
survive, and the table is now 3-anonymous on age. The price is precision: any
question finer than the bucket — patients in their thirties, patients under 35 —
can no longer be answered from the table at all. Suppression is the same trade at
its limit, where a dropped row answers nothing. Utility is what anonymity is
bought with, and the lab makes you pay for it explicitly.
""",
                    },
                    {
                        "q": "Why does the Laplace mechanism for a count use noise of scale $1/\\varepsilon$ rather than some other scale?",
                        "opts": [
                            "Because a count has sensitivity 1, and at scale $\\Delta f/\\varepsilon$ the density ratio of neighbouring tables is at most $e^{\\varepsilon}$",
                            "Because Laplace noise with scale $1/\\varepsilon$ has variance exactly $\\varepsilon$, so that the privacy loss and the noise added are one number",
                            "Because scale $1/\\varepsilon$ makes the noise integer-valued on average, keeping a noisy count close to a real count",
                            "Because the inverse-transform formula only produces a valid Laplace sample when the scale is the reciprocal of a positive number",
                        ],
                        "a": 0,
                        "whys": [
                            r"One row moves a count by at most 1, and at scale $b$ the density ratio between neighbouring tables is at most $e^{1/b}$; $b = 1/\varepsilon$ makes that $e^{\varepsilon}$.",
                            r"The variance of Laplace$(0, b)$ is $2b^2$, not $\varepsilon$; no such equality holds. The scale is chosen to bound a ratio of probabilities, not to match a variance to a parameter.",
                            r"Laplace noise is continuous and never integer-valued; a noisy count is 3.8 or 4.56, not a whole number. Nothing about the scale makes it otherwise.",
                            r"The inverse transform works for any positive scale — the lab's `laplace_noise` takes an arbitrary `scale`. The constraint on the scale comes from the privacy inequality, not from the sampling formula.",
                        ],
                        "why": r"""
The scale is derived, not chosen. A count changes by at most $\Delta f = 1$
between neighbouring tables. Laplace noise has density proportional to
$e^{-|x|/b}$, so at any output the ratio of densities under two true counts one
apart is at most $e^{1/b}$. The definition requires that ratio to be at most
$e^{\varepsilon}$, which forces $b = 1/\varepsilon$ — and $b = \Delta f/\varepsilon$
for a query of general sensitivity. Variance, integrality and the sampling route
do not enter into it.
""",
                    },
                    {
                        "q": "A count is released through the Laplace mechanism at $\\varepsilon = 0.5$. An analyst asks for the same count 100 times and averages. What has happened?",
                        "opts": [
                            "Nothing changed: each release satisfied $\\varepsilon = 0.5$ independently, so the guarantee still stands at 0.5",
                            "The epsilons added to 50, the privacy guarantee is void, and the average recovers the true count closely",
                            "The noise cancelled because Laplace draws are symmetric, but the guarantee is unaffected since noise was still added",
                            "The guarantee tightened to $0.5/100$, because averaging reduces noise and therefore reduces privacy loss",
                        ],
                        "a": 1,
                        "whys": [
                            r"Each release did satisfy 0.5 on its own, and that is the trap: the bounds multiply across releases, $e^{0.5 \times 100}$, so the combined guarantee is $\varepsilon = 50$, which bounds nothing useful.",
                            r"Sequential composition: epsilons add. And the mean of 100 draws at scale 2 sits within a few tenths of the truth.",
                            r"The noise did average away — that is precisely the problem, not a consolation. \"Noise was added\" is not a guarantee; a bounded $\varepsilon$ is, and 100 queries have spent 50 of it.",
                            r"Backwards: less noise in the final estimate means more information about the table has leaked, which is more privacy loss, not less. Averaging is the attack; the budget is what makes it cost something.",
                        ],
                        "why": r"""
Run the defining inequality across two mechanisms and the bound is
$e^{\varepsilon_1} e^{\varepsilon_2} = e^{\varepsilon_1 + \varepsilon_2}$: epsilons
add. A hundred queries at 0.5 have spent 50, and the averaged answer — 3.9 against
a true count of 4 in the reading's trace — shows what that means in practice.
Every single answer was honest; the total is not. This is why $\varepsilon$ is a
budget rather than a setting, and why the lab's `dp_count` refuses to answer
without charging one.
""",
                    },
                    {
                        "q": "In the lab, `dp_count` must call `budget.spend(epsilon)` before computing the count. Why the order?",
                        "opts": [
                            "So the noise scale can be derived from the remaining budget rather than from the epsilon requested",
                            "So that a query the budget refuses never produced an answer that could leak as a side effect",
                            "Because Python evaluates method calls lazily, and the charge would otherwise be skipped",
                            "So the budget records the query even when it is refused, keeping the log of attempts complete",
                        ],
                        "a": 1,
                        "whys": [
                            r"The scale is $1/\varepsilon$ for the epsilon actually spent on this query; the remaining budget is what decides whether the query may run at all, not how noisy it is.",
                            r"Charge first, and a refusal raises before any count exists. Compute first, and the count exists in memory and in whatever was logged, even though the query was refused.",
                            r"Python evaluates method calls eagerly, in order. The ordering is a design decision about what should exist when a refusal happens, not a language quirk.",
                            r"A refused `spend` raises and changes nothing — the tests check that `spent` stays at zero after a refusal. The budget is an account of what was released, not a log of what was asked.",
                        ],
                        "why": r"""
The budget is the whole of the guarantee, so the answer must not exist until the
budget has agreed to pay for it. Charging first means a refused query raises with
no count ever computed — nothing to log by accident, nothing to return from a
half-finished path. Charging afterwards would let the count be computed, possibly
recorded, and then the refusal arrive too late to matter. The tests check both
halves: a refused query leaves `spent` untouched, and a query that runs has been
charged exactly its epsilon.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Ada asks to be forgotten, and the invoice says no",
                    "minutes": 14,
                    "body": r'''
An email arrives on day 1000. It is from a customer called Ada, it cites Article 17
of the GDPR, and it asks that everything you hold about her be deleted. You hold two
records. One is a marketing profile — her email address and a few preferences —
created on day 0 when she signed up for a newsletter. The other is an invoice for
42 units, created on day 900 when she bought something. Two records, one request,
and the correct answer is to delete one of them, refuse the other with a stated
reason, and write down that you did both. This reading is about why the answer is
split, and about a third fact that the audit should have caught before the email
ever arrived.

## Three rights as three operations

The rights in the regulation read as prose, and each one is an operation on a
record store. Article 15 is the right of *access*: a subject may ask what you hold
about them and receive a copy. Article 16 is *rectification*: a subject may have an
inaccurate field corrected. Article 17 is *erasure*: a subject may have their
personal data deleted. In the lab these are `export`, `rectify` and `erase`, and the
store that answers them is a list of records, each shaped as
`{"id", "subject", "category", "created", "data"}`, with `created` and `today` as
plain day numbers so that the arithmetic stays visible.

Only one of the three is unconditional in practice, and it is not the one people
expect. Access has narrow exceptions. Rectification is almost always granted. Erasure
is the right with the longest list of reasons to say no.

## The exception that decides Ada's invoice

Article 17(3) says the right to erasure does not apply where processing is necessary,
among other things, "for compliance with a legal obligation" or "for the
establishment, exercise or defence of legal claims". Tax law is the everyday case of
the first: an invoice must be kept for a fixed number of years whether or not the
customer would like it gone. The lab encodes that as two policies. `RETENTION_DAYS`
says how long each category may be kept at all — 2555 days for an invoice, which is
seven years, 365 for marketing, 730 for support. `MANDATORY` names the categories a
legal obligation forces you to keep for that whole period; here it is `{"invoice"}`.

So for a record in a mandatory category, erasure is refused while
$\text{today} - \text{created} < \text{RETENTION\_DAYS[category]}$. Ada's invoice was
created on day 900 and today is day 1000, so $1000 - 900 = 100$, which is less than
2555. Refused, reason `"retention"`. Her marketing record is not in a mandatory
category, so no obligation protects it. Erased.

```python
RETENTION_DAYS = {"invoice": 2555, "marketing": 365, "support": 730}
MANDATORY = {"invoice"}

def decide(record, today, holds):
    if record["id"] in holds:
        return "legal_hold"
    if (record["category"] in MANDATORY
            and today - record["created"] < RETENTION_DAYS[record["category"]]):
        return "retention"
    return None

records = [{"id": 1, "subject": "ada", "category": "marketing", "created": 0},
           {"id": 2, "subject": "ada", "category": "invoice", "created": 900}]
for today in (1000, 900 + 2555):
    erased = [r["id"] for r in records if decide(r, today, set()) is None]
    refused = {r["id"]: decide(r, today, set()) for r in records
               if decide(r, today, set()) is not None}
    print(today, erased, refused)
```

That prints `1000 [1] {2: 'retention'}` and then `3455 [1, 2] {}`. On day 3455 the
obligation has lapsed — seven years have passed since the invoice was raised — and
the same request that was half refused on day 1000 is granted in full. Nothing about
Ada changed; the calendar did. The lab's `erase` returns exactly this pair, a sorted
list of ids erased and a dict of id to reason, and the test named *erase honours a
mandatory retention period* runs both dates.

## The second exception, and why it comes first

The other ground in Article 17(3) is legal claims. If Ada's invoice is evidence in a
dispute — she is suing you, or you are suing her — deleting it is destroying
evidence, and the mechanism that prevents that is a *legal hold*: a flag on a
specific record that says it may not be deleted by anyone until the hold is lifted.
The lab's `place_hold` and `release_hold` manage a set of held ids.

A record can be both under hold and within its retention period, and the decision
function above checks the hold first. The reason is not that one exception is
stronger in law; it is that a refusal must carry the reason that would still apply
if the other were removed. Retention lapses on its own with time. A hold does not.
Tell Ada on day 3455 that her invoice is refused for `"retention"` and you have told
her something false; tell her `"legal_hold"` and the reason is the one that decided
it. The test *A hold outranks retention* sets `today` to 99999 and checks that the
reason is the hold.

## The duty that runs the other way

Article 5(1)(e), storage limitation, is not a right the subject exercises. It is an
obligation on you: personal data must be kept "for no longer than is necessary". Once
a record is past its retention period it should be gone whether or not anyone asked,
and the lab's `expired(today)` lists the ids that are.

Look again at Ada's marketing record. Created day 0, category marketing, retention
365. On day 1000 it is 635 days past its retention period. The correct finding about
Ada's request is not that it was handled well; it is that the record it deleted
should have been purged on day 365, and an audit that lists `expired(1000)` before
the email arrives finds `[1]` sitting there. `purge_expired(today)` is the routine
that should have run — it deletes what `expired` lists, except for anything under
hold, because a hold outranks storage limitation too.

Erasure and storage limitation are the two directions of one rule. One is "delete
because asked, unless obliged to keep"; the other is "delete because obliged, unless
obliged to keep". The lab's hint points at the same expression appearing twice with
the comparison flipped: `today - created >= RETENTION_DAYS[category]` in `expired`,
and `<` in the retention refusal inside `erase`. Only one of those is about a legal
obligation to keep; the other is a legal obligation to delete.

## Per record, never per subject

The mistake people make with Ada's request is to treat it as one decision. "She has
an invoice we must keep, so we cannot honour her erasure request" — refuse the
whole thing. It is tempting because the request came in as one email and the reply
goes out as one, and because refusing once is less work than deciding twice. But the
exception in Article 17(3) attaches to *processing that is necessary*, and keeping
the invoice does not make keeping her newsletter preferences necessary. The decision
is made per record. Ada's reply says: one record erased, one retained, and here is
why for each.

The equal and opposite mistake is refusing without a ground. Article 12(4) requires
that a subject who is not going to get what they asked for be told the reasons. A
bare `False` from `erase` is a compliance failure by itself. That is why the lab's
return value is a dict of reasons rather than a count of refusals.

## Two bugs that look like working code

The first is in `export`. Article 15 asks for a copy, and the obvious code returns
the matching records. It runs, the tests that check ids pass, and it has handed the
caller a live handle into the store.

```python
import copy

store = [{"id": 1, "subject": "ada", "data": {"email": "ada@example.org"}}]
loan = [r for r in store if r["subject"] == "ada"]
loan[0]["data"]["email"] = "TAMPERED"
print(store[0]["data"]["email"])

store[0]["data"]["email"] = "ada@example.org"
shallow = [dict(r) for r in store if r["subject"] == "ada"]
shallow[0]["data"]["email"] = "TAMPERED"
print(store[0]["data"]["email"])

store[0]["data"]["email"] = "ada@example.org"
deep = [copy.deepcopy(r) for r in store if r["subject"] == "ada"]
deep[0]["data"]["email"] = "TAMPERED"
print(store[0]["data"]["email"])
```

That prints `TAMPERED`, then `TAMPERED` again, then `ada@example.org`. The first
export is the list of the records themselves. The second looks fixed — `dict(r)` is a
copy — but it is a *shallow* copy: the new dict's `"data"` key points at the same
inner dict as the original, so writing through it still reaches the store. Only
`copy.deepcopy` gives the subject a document rather than a door. The test *export
copies, filters and logs* writes through the export and checks the store did not
move.

The second bug is in `erase`, and it is the oldest bug in list handling.

```python
records = [{"id": 1, "subject": "ada"}, {"id": 2, "subject": "ada"},
           {"id": 3, "subject": "bob"}]
for r in records:
    if r["subject"] == "ada":
        records.remove(r)
print([r["id"] for r in records])
```

That prints `[2, 3]`. Removing record 1 shifted record 2 into its slot, the loop
moved on to the next index, and record 2 was never examined. Ada's second record
survives an erasure that reported success. The lab's hint has you partition into a
`keep` list and an `erased` list in one pass and then reassign `self.records`, which
cannot skip anything.

## The log is the point

Article 5(2) makes the controller responsible for *demonstrating* compliance, which
means that when a regulator asks what happened to Ada's request the answer has to
be a record rather than a recollection. Every `export`, `rectify`, `erase` and
`purge_expired` in the lab appends `{"op", "subject", "ids"}` to `self.log`. Note what
is logged and what is not: the ids and the operation, never the data, so the log
itself does not become a second copy of what was erased. And an operation that raises
logs nothing, because it did nothing — a rectification refused for touching another
subject's record is not an event in Ada's history.

## Where it stops holding

Day numbers stand in for dates, and 2555 stands in for a retention period that is a
fact about a jurisdiction rather than about code: it changes by country, by category
and by year, and the right place for it is a policy table someone else maintains,
which is why the lab reads it from `RETENTION_DAYS` rather than hard-coding a number
in `erase`. The store is also never the only copy. Backups, processors, the marketing
platform's own database — `erase` reaches none of them, and a real handler has to
propagate. Nothing here verifies that the email really came from Ada, which Article
12(6) lets you check before acting. And the log proves what the code did, not that
the code was right: if `MANDATORY` had been wrong, every refusal it produced would be
faithfully recorded and faithfully unlawful.

## What you are about to build

The lab, *A data-subject request handler*, is `RecordStore`. `add` validates a
record's keys, category and id. `export` deep-copies a subject's records sorted by
id. `rectify` changes one existing field of one record that belongs to the subject
asking. `erase` decides per record — hold first, then mandatory retention — and
returns the erased ids with a dict of reasons. `expired` and `purge_expired` are
storage limitation, with the hold respected. Every successful operation appends to
the log; every refusal that raises leaves it alone. Run the starter and the two
prints are Ada's export and then `([1], {2: 'retention'})` — the answer this reading
worked out by hand.
''',
                },
            ],
            "quiz": {
                "title": "Which record, which reason, and who has to prove it",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Ada holds a marketing record (day 0) and an invoice (day 900). Invoices are mandatory for 2555 days. She requests erasure on day 1000. What is the correct outcome?",
                        "opts": [
                            "Both records are erased, because the request was valid and no legal hold is in place",
                            "The whole request is refused, because a mandatory record makes her data necessary to keep",
                            "The marketing record is erased; the invoice is refused with the reason `\"retention\"`",
                            "Both are refused until day 3455, after which the invoice's obligation lapses and both go",
                        ],
                        "a": 2,
                        "whys": [
                            r"The invoice is 100 days into a 2555-day legal obligation. Article 17(3) preserves processing necessary for compliance with a legal obligation, so it cannot be erased on request, hold or no hold.",
                            r"The exception attaches to the processing that is necessary — keeping the invoice. It says nothing about the newsletter preferences, which no obligation protects. Refusing everything because one record is protected is the per-subject mistake.",
                            r"Per record: no obligation covers marketing, so it goes; the invoice is inside its mandatory period, so it stays, and the refusal carries its reason.",
                            r"Only the invoice waits until 3455. The marketing record has no mandatory retention and should have been deleted already under storage limitation; nothing ties its fate to the invoice's calendar.",
                        ],
                        "why": r"""
Erasure is decided one record at a time. The marketing record sits in no mandatory
category, so nothing in Article 17(3) protects it, and it is erased. The invoice
was created 100 days ago and must be kept for 2555, so it is refused, and the
refusal names its ground. The lab returns `([1], {2: "retention"})`. Refusing the
whole request because one record is protected treats a per-record exception as a
per-subject one; erasing everything ignores the obligation altogether.
""",
                    },
                    {
                        "q": "A record is both under legal hold and inside its mandatory retention period. Why does the lab report the refusal as `\"legal_hold\"` rather than `\"retention\"`?",
                        "opts": [
                            "Because a hold is the stronger ground in law, and the regulation ranks legal claims above legal obligations",
                            "Because retention lapses on its own with time while the hold does not, so the hold is the reason that will still apply",
                            "Because holds are checked by id and retention by category, and id-level rules take precedence over category-level ones",
                            "Because reporting retention would reveal the record's category to the subject, which the hold exists to conceal",
                        ],
                        "a": 1,
                        "whys": [
                            r"The regulation lists both grounds in Article 17(3) without ranking them. The ordering in the lab is a design decision about which reason is durable, not a claim about legal precedence.",
                            r"Tell the subject `retention` and on the day the period lapses the stated reason is false while the record is still refused. The hold is the ground that decided it.",
                            r"Nothing in the lab gives id-level rules precedence as a principle; `add` and `expired` work by category too. The order in `erase` is chosen for the reason a refusal must remain true, not for the granularity of the check.",
                            r"A hold conceals nothing about the record; the subject can `export` it and see the category. The reason is about giving the subject a ground that would still stand if the other were removed.",
                        ],
                        "why": r"""
A refusal must carry the reason that actually decided it. Retention is a clock:
on the day it runs out, a refusal that cited it becomes wrong. A legal hold has no
clock; it stays until someone lifts it. Checking the hold first means that a record
protected by both gets the reason that would survive the other's removal, and the
test that sets `today` far past every retention period and still expects
`"legal_hold"` is checking exactly that. Neither ground outranks the other in the
regulation; the order is about telling the subject the truth.
""",
                    },
                    {
                        "q": "`export` is implemented as `[dict(r) for r in self.records if r[\"subject\"] == subject]`. A test writes to the returned copy's `data` and finds the store changed. Why?",
                        "opts": [
                            "`dict(r)` copies the outer dict only, so the nested `data` dict is still shared with the store",
                            "The list comprehension evaluates lazily, so the copies are only made after the test has written",
                            "`dict(r)` returns the same object when its argument is already a dict, as an optimisation",
                            "The filter keeps references because `==` on strings compares identity rather than content",
                        ],
                        "a": 0,
                        "whys": [
                            r"A shallow copy has new keys pointing at the same values. `copy[\"data\"]` is the original inner dict, and writing through it reaches the store.",
                            r"A list comprehension runs eagerly and the copies exist before `export` returns. The problem is what kind of copies they are, not when they are made.",
                            r"`dict(r)` always builds a new dict; `dict(r) is r` is `False`. What it does not do is copy the values, so a nested dict is shared between old and new.",
                            r"`==` on strings compares content, and the filter is not where the sharing happens. Even a correctly filtered record is shared if only its outer dict was copied.",
                        ],
                        "why": r"""
`dict(r)` builds a new outer dict whose values are the same objects as before —
including the inner `data` dict. Writing `copy["data"]["email"] = ...` mutates
that shared inner dict, and the store sees the change. Only `copy.deepcopy`
copies the nested structure, which is what turns an export into a document the
subject can hold rather than a handle into live data. The reading's three-print
block shows the loan, the shallow copy and the deep copy in turn: `TAMPERED`,
`TAMPERED`, then the original value.
""",
                    },
                    {
                        "q": "On day 1000 the audit finds Ada's marketing record (created day 0, retention 365) still in the store. Which duty was breached, and by whom?",
                        "opts": [
                            "None: the record was lawfully held until Ada asked, since erasure is triggered by a request",
                            "Storage limitation, Article 5(1)(e), by the controller, who should have purged it on day 365",
                            "The right to erasure, Article 17, by Ada, who waited 635 days longer than the regulation allows",
                            "The retention policy, which set marketing at 365 days when the legal minimum for it is longer",
                        ],
                        "a": 1,
                        "whys": [
                            r"Storage limitation does not wait for a request. Data kept longer than necessary is unlawfully kept whether or not the subject ever writes in; the request only made the overdue record visible.",
                            r"Article 5(1)(e) is a duty on the controller to delete when data is no longer necessary. The lab's `expired(1000)` would have listed this id, and `purge_expired` should have run long before.",
                            r"A subject has no deadline for exercising a right, and no duty at all under Article 5. The 635 days are the controller's failure to purge, not the subject's delay in asking.",
                            r"Marketing has no legal minimum retention; it is not in `MANDATORY`. The 365 is the controller's own limit on how long the data stays useful, and the breach is exceeding it, not setting it.",
                        ],
                        "why": r"""
Article 5(1)(e) obliges the controller to keep personal data no longer than
necessary, and the controller set that period at 365 days for marketing. The
record is 635 days past it. No request was needed; `expired(today)` lists it and
`purge_expired` should have removed it on day 365. Ada's erasure request did not
create the duty to delete this record — it exposed that the duty had been
neglected for nearly two years.
""",
                    },
                    {
                        "q": "`rectify` is called with an id that belongs to another subject and raises `KeyError`. The lab says this must append nothing to `self.log`. What is the reasoning?",
                        "opts": [
                            "Logging a refused operation would reveal that the other subject's record exists, which is a disclosure",
                            "The log records what was done to the store, and nothing was; a refusal that raised is not an event there",
                            "An exception unwinds the call before the log line runs, so nothing could be appended even if the code tried",
                            "Refusals are logged elsewhere by the exception handler, and logging them twice would inflate the audit trail",
                        ],
                        "a": 1,
                        "whys": [
                            r"The log holds ids and operations, not data, and the subject never sees it; disclosure to the subject is not what is at stake. The reason is about what the log is for.",
                            r"The log exists to demonstrate what happened to each subject's data. A refused rectification changed nothing, so recording it as a `rectify` would claim an event that did not occur.",
                            r"Code can log before raising, and many systems do. The lab's rule is a choice about the meaning of a log entry, not a consequence of how exceptions propagate.",
                            r"There is no other handler in the lab, and nothing about double-counting is at issue. The rule is that the log records operations that changed or copied data; a refusal did neither.",
                        ],
                        "why": r"""
The log is the controller's evidence of what was done: exports made, fields
changed, records erased or purged. An operation that raised did nothing to the
store, so a log line for it would assert an event that did not happen — and a
`rectify` entry against a record the subject did not own would be a false record
of a change. The lab's rule is that successful operations log their ids and
refusals that raise log nothing; a separate access log for attempts would be a
different artefact with a different purpose.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "What you knew when you shipped it, and how anyone can tell",
                    "minutes": 14,
                    "body": r'''
Fourteen months after a loan-scoring model went live, a complaint reaches the
regulator: applicants from one neighbourhood were rejected at a rate nobody can
account for. The regulator's first question is not whether the model was fair. It is
what you *knew* when you released it — what the evaluation showed, what limitations
were recorded, who signed off. You have a folder of documents and a file called
`audit.log` that the operations team has been appending to since launch. The
operations team also has write access to `audit.log`. So does the person who signed
off. So, for that matter, did the contractor who left in March.

Every line in that file may be true. The problem is that nothing about the file lets
anyone tell, and a record whose integrity rests on the good faith of everyone who
could edit it is not evidence; it is a claim. This reading is about two artefacts
that turn "we assessed it" into something a stranger can check: a document whose
missing sections are errors rather than blanks, and a log in which any later edit is
detectable.

## A document that refuses to be incomplete

The document first, because it is simpler and because the log ends up pointing at
it. Mitchell and colleagues proposed the *model card* in 2019 as a fixed set of
sections that ship with a trained model: what it is for, what it is *not* for, what
it was trained on, how it scores, what its known limitations are, and whom to ask.
The sections are unremarkable individually. What makes the card a control rather
than a courtesy is that every section is required.

Consider the two ways a card can lack a limitations section. In a template, the
heading sits there over an empty space, the card looks finished, and nobody reading
it fourteen months later can tell whether the team found no limitations or never
looked. In the lab's `model_card`, a missing or empty `limitations` raises
`ValueError` naming the section, and no card is produced at all. The absence is loud
at the moment someone could still do something about it. That is the entire
difference between documentation and a control: a control makes the wrong state
impossible to reach quietly.

The lab's card is markdown with a fixed layout — a title, a version line, then six
`##` sections in a fixed order with one blank line between them, metrics sorted by
name and printed to three decimals. The rigidity is deliberate. A card that renders
the same way every time can be hashed, and a hash is how the card gets into the log.

## Hashing a document, and why one hash is not enough

A cryptographic hash such as SHA-256 maps any input to 64 hex characters, so that a
one-character change in the input produces an unrelated digest and nobody can
construct a second input with the same digest. If you hold the digest of the card
you released, you can prove later that a card someone shows you is or is not that
card. The lab's `card_hash` is one line: encode the text as UTF-8 and digest it.

Now try to protect `audit.log` the same way. Store each entry's hash beside it. An
operator who edits entry 7 recomputes entry 7's hash, stores that beside it, and the
file is self-consistent again. A hash stored next to the thing it hashes protects
nothing against someone who can write both. What is needed is for each entry to be
committed to by something the editor cannot reach — and the something can be the
*next entry*.

## Chaining the entries

Give the log a starting point, `GENESIS`, sixty-four zeros. Each entry's stored hash
is not the hash of the entry alone but of its predecessor's hash followed by its own
content: $h_i = \text{SHA256}(h_{i-1} \,\|\, \text{entry}_i)$, with $h_{-1}$ being
`GENESIS`. Every entry also records which predecessor hash it was computed against,
in a field called `prev`.

Now edit entry 2. Its content changed, so recomputing $h_2$ from its stored `prev`
and its new content gives something other than the stored $h_2$: a verifier that
walks the chain recomputing each hash stops at index 2. Suppose the editor also
recomputes and stores a fresh $h_2$. Then entry 3's `prev` field, which still holds
the old $h_2$, disagrees with entry 2's new hash, and the verifier stops at index 3
instead. Either way the edit is found. Delete an entry, and the entry after it points
at a predecessor that is not there. Swap two entries, and the first of them points
at a predecessor that is now two places back. The chain turns any change into a
broken link somewhere at or after the change.

```python
import hashlib
import json

GENESIS = "0" * 64

def canonical(entry):
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))

def chain_hash(prev, entry):
    return hashlib.sha256((prev + canonical(entry)).encode("utf-8")).hexdigest()

def append(entries, entry):
    prev = entries[-1]["hash"] if entries else GENESIS
    entries.append({"seq": len(entries), "entry": entry, "prev": prev,
                    "hash": chain_hash(prev, entry)})

def verify(entries):
    prev = GENESIS
    for i, rec in enumerate(entries):
        if rec["prev"] != prev or rec["hash"] != chain_hash(rec["prev"], rec["entry"]):
            return i
        prev = rec["hash"]
    return None

log = []
for n in range(4):
    append(log, {"event": "step", "n": n})
print(verify(log))
log[2]["entry"]["n"] = 99
print(verify(log))
log[2]["entry"]["n"] = 2
del log[1]
print(verify(log))
```

That prints `None`, then `2`, then `1`. The untouched chain verifies. Editing entry
2's content is caught at 2, because its stored hash no longer matches its content.
Restoring the value and deleting entry 1 is caught at 1: what is now at index 1 was
computed against the old entry 1's hash, and the verifier arrived expecting entry
0's. This is the lab's `AuditLog.verify`, and its tests do exactly these three
things plus a swap and a forged hash.

## The mistake: hashing something that is not the same bytes twice

The hash covers bytes, and a Python dict is not bytes. Somewhere between the dict
and the digest there is a serialisation, and if it is not fixed the same entry will
hash differently on different days for no reason anyone did.

```python
import hashlib
import json

a = {"event": "trained", "rows": 118000}
b = {"rows": 118000, "event": "trained"}
loose = lambda d: hashlib.sha256(json.dumps(d).encode()).hexdigest()
tight = lambda d: hashlib.sha256(
    json.dumps(d, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
print(json.dumps(a) == json.dumps(b), loose(a) == loose(b))
print(tight(a) == tight(b), json.dumps(a, sort_keys=True, separators=(",", ":")))
```

That prints `False False` and then `True {"event":"trained","rows":118000}`. The two
dicts are equal — `a == b` is `True` — but `json.dumps` writes keys in insertion
order, so their default serialisations differ and so do their digests. With
`sort_keys=True` and fixed separators the serialisation is *canonical*: the same
content gives the same bytes regardless of how the dict was built. The lab's
`canonical` is that call, and `chain_hash` goes through it.

Why is this the mistake people make? Because it does not show up in testing. The
process that writes an entry and the process that verifies it share a Python
version and build their dicts the same way, so the hashes agree. Then a rewrite
in another language, or a database that returns columns in a different order,
verifies the log and finds every link broken. The verifier is now crying wolf, and a
verifier that cries wolf gets switched off. A related trap is Python's built-in
`hash()`, which is randomised per process for strings so that `hash("abc")` differs
between two runs of the interpreter; it was designed for dictionaries, not for
evidence, and it is the wrong tool here for that reason.

## Where the chain stops holding

Return to the operator who wants to change entry 2. The chain caught a lazy edit.
What about a diligent one? Edit entry 2, recompute its hash, then walk forward
rewriting every later entry's `prev` and `hash` to match. The chain is now internally
consistent and `verify` returns `None`.

```python
import hashlib
import json

GENESIS = "0" * 64
canonical = lambda e: json.dumps(e, sort_keys=True, separators=(",", ":"))
chain_hash = lambda prev, e: hashlib.sha256((prev + canonical(e)).encode()).hexdigest()

def verify(entries):
    prev = GENESIS
    for i, rec in enumerate(entries):
        if rec["prev"] != prev or rec["hash"] != chain_hash(rec["prev"], rec["entry"]):
            return i
        prev = rec["hash"]
    return None

log = []
for n in range(4):
    prev = log[-1]["hash"] if log else GENESIS
    log.append({"entry": {"n": n}, "prev": prev, "hash": chain_hash(prev, {"n": n})})
witnessed_head = log[-1]["hash"]

log[2]["entry"]["n"] = 99
for i in range(2, len(log)):
    log[i]["prev"] = log[i - 1]["hash"] if i else GENESIS
    log[i]["hash"] = chain_hash(log[i]["prev"], log[i]["entry"])
print(verify(log), log[-1]["hash"] == witnessed_head)
```

That prints `None False`. The rewritten chain verifies, and the only thing that
gives the edit away is that the head — the last hash — is no longer the one that was
recorded elsewhere before the edit. That is the limit of the idea, stated precisely:
a hash chain is *tamper-evident*, not tamper-proof, and it is evident only to someone
who holds a head hash the editor could not reach. In practice that means the head is
published, or sent to a counterparty, or written into board minutes, at intervals;
every entry before a witnessed head is then fixed, and every entry after it is not
yet. A chain nobody has witnessed is `audit.log` with more arithmetic.

There is a second limit, which is not about integrity at all. The chain proves that
the entries have not changed since they were witnessed. It says nothing about
whether they were true when written. An entry reading `"evaluated, accuracy 0.91"`
appended by someone who ran no evaluation is preserved with the same fidelity as an
honest one. The chain converts "the log was not rewritten" into a checkable fact;
"the log was accurate" stays a matter of who wrote it and what else was recorded.

## Binding the card to the log

Put the two artefacts together. When the model is released, the card is rendered,
hashed, and the digest is appended to the log as an entry: `{"event":
"card_published", "card": "<64 hex characters>"}`. From then on, a card that anyone
produces can be checked against the log, and the log can be checked against the
witnessed head. Fourteen months later, the answer to "what did you know?" is: this
card, whose hash is in this log, whose head was in the minutes of this meeting. The
regulator does not have to trust the operations team, the signer, or the contractor
from March. They have to trust SHA-256 and the minutes, which is a smaller ask.

## What you are about to build

The lab, *Model cards and a hash-chained audit log*, has both halves. `model_card`
renders the fixed markdown layout and raises `ValueError` naming any missing section;
`card_hash` digests the text. `canonical` is the sorted, compact `json.dumps`;
`chain_hash` digests the predecessor's hash followed by the canonical entry.
`AuditLog` keeps a list of `{"seq", "entry", "prev", "hash"}` records, exposes `head`
as the last hash or `GENESIS`, appends by computing the next link, and `verify`
walks the chain returning `None` or the first index at which a `prev` or a `hash`
disagrees. The starter's last line binds the card's hash into a fresh log and prints
`verify()`, which should be `None` — and the tests then edit, forge, delete and
swap entries and expect the index that this reading traced for each.
''',
                },
            ],
            "quiz": {
                "title": "What a chain proves, and what it cannot",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A four-entry chain is intact. Someone edits entry 2's content and recomputes entry 2's `hash` to match, leaving everything else. Where does `verify()` stop, and why?",
                        "opts": [
                            "At index 2, because the recomputed hash does not match the content that was originally hashed",
                            "At index 3, because its stored `prev` still names the old hash of entry 2, which is now gone",
                            "Nowhere: recomputing the hash makes entry 2 self-consistent, so the chain verifies as intact",
                            "At index 0, because the change to entry 2 propagates backwards through every `prev` field",
                        ],
                        "a": 1,
                        "whys": [
                            r"Entry 2 is self-consistent after the recompute: its `hash` matches its new content and its `prev`. The verifier passes it. What it cannot fix is that entry 3 was computed against the *old* hash of entry 2.",
                            r"Entry 3's `prev` was fixed when entry 3 was appended. The editor changed entry 2's hash, so the link from 3 back to 2 is broken at 3.",
                            r"Only entry 2 is self-consistent. The verifier carries the expected predecessor hash forward, and at index 3 the stored `prev` disagrees with the new hash of entry 2, so the chain does not verify.",
                            r"Hashes commit forwards: each entry contains its predecessor's hash, not its successor's. Changing entry 2 cannot alter entries 0 and 1, which were fixed before entry 2 existed.",
                        ],
                        "why": r"""
Each entry stores the hash of its predecessor. Recomputing entry 2's hash makes
entry 2 consistent with itself, but entry 3 recorded the old hash of entry 2 in
its `prev` when it was appended, and that field was not touched. The verifier
walks forward carrying the expected predecessor hash; at index 3 the stored
`prev` disagrees with the new hash of entry 2 and verification stops there. A
lazy edit is caught at its own index; a half-diligent one is caught at the next.
Only rewriting every later entry hides it — which the head hash then exposes.
""",
                    },
                    {
                        "q": "Two processes append entries built from equal dicts, `{\"event\": \"trained\", \"rows\": 118000}` and `{\"rows\": 118000, \"event\": \"trained\"}`. Why must `chain_hash` serialise through `canonical` rather than plain `json.dumps`?",
                        "opts": [
                            "Plain `json.dumps` writes keys in insertion order, so equal dicts can give different bytes and hashes",
                            "Plain `json.dumps` escapes non-ASCII text, which changes the byte length and therefore the SHA-256 digest",
                            "`canonical` compresses the entry, so the chain hashes fewer bytes and verification runs faster",
                            "`canonical` includes the predecessor hash inside the JSON, which plain `json.dumps` cannot do",
                        ],
                        "a": 0,
                        "whys": [
                            r"The two dicts compare equal and hash differently under default `json.dumps`. `sort_keys=True` with fixed separators makes the bytes depend on content alone.",
                            r"Escaping is consistent between the two calls, so it does not make equal dicts hash differently. The difference between the two serialisations here is key order, which escaping does not touch.",
                            r"The compact separators do shave bytes, but that is a side effect; SHA-256 costs the same to within noise. The reason for `canonical` is determinism, not speed.",
                            r"The predecessor hash is prepended to the canonical string by `chain_hash`, outside the JSON. `canonical` serialises only the entry; the concatenation is a separate step.",
                        ],
                        "why": r"""
A hash covers bytes, and a dict is not bytes until something serialises it.
Default `json.dumps` preserves insertion order, so `{"event": ..., "rows": ...}`
and `{"rows": ..., "event": ...}` — equal as dicts — produce different strings
and different digests. `sort_keys=True` with `separators=(",", ":")` gives one
serialisation per content, so a verifier written elsewhere, or a database that
returns columns in another order, recomputes the same hash. Without it the
verifier eventually breaks on honest data, and a verifier that cries wolf is
switched off.
""",
                    },
                    {
                        "q": "An operator edits entry 2 and then rewrites the `prev` and `hash` of every later entry so the chain is consistent again. `verify()` returns `None`. What, if anything, can still detect the edit?",
                        "opts": [
                            "Nothing: a chain that verifies is by definition unaltered, so the edit has been made fully undetectable",
                            "A copy of the head hash recorded somewhere the operator could not write to before the edit was made",
                            "The `seq` numbers, which would now be out of order because the rewrite renumbers the later entries",
                            "The SHA-256 digests themselves, since a rewritten hash is distinguishable from an original one",
                        ],
                        "a": 1,
                        "whys": [
                            r"A verifying chain proves internal consistency, which a diligent editor can restore. Tamper-evident is not tamper-proof; the chain needs an anchor outside the editor's reach.",
                            r"The rewritten chain ends in a different head. Compare it with the head that was published, minuted or sent to a counterparty, and the mismatch is the evidence.",
                            r"The rewrite changes hashes, not positions; the `seq` field stays 0, 1, 2, 3. Sequence numbers detect gaps and reorderings, not a content edit that keeps every entry in place.",
                            r"A digest is 64 hex characters with no marker of provenance. A recomputed SHA-256 is indistinguishable from an original; that is the point of a hash function, and why the anchor must be held elsewhere.",
                        ],
                        "why": r"""
The chain makes any edit change every hash after it, including the last one, the
head. If the head was witnessed before the edit — published, minuted, handed to a
counterparty — the rewritten chain's head disagrees with the witnessed one, and
every entry before that witnessed head is thereby fixed. Without such a witness
the chain is merely consistent, and consistency is something the editor can
manufacture. A hash chain is tamper-evident exactly to the extent that someone
outside the writers holds a head.
""",
                    },
                    {
                        "q": "The lab's `model_card` raises `ValueError` when `limitations` is an empty list rather than rendering a card with an empty section. What does this achieve?",
                        "opts": [
                            "It makes the absence loud at authoring time, when it can be fixed, rather than months later when a blank says nothing",
                            "It keeps the markdown well-formed, since an empty bullet list under a heading would not render in most viewers",
                            "It prevents the card from being hashed, so an incomplete card cannot be bound into the audit log by accident",
                            "It ensures that every model documents at least one limitation, since a model with none at all would be a statistical impossibility",
                        ],
                        "a": 0,
                        "whys": [
                            r"A blank section reads the same whether nobody looked or nobody found anything. An error at the moment of rendering turns the missing section into something that must be resolved now.",
                            r"A heading over nothing renders fine; markdown is tolerant. The rigid layout exists so the card can be hashed, not because an empty section would break a viewer.",
                            r"It does have that consequence — no card, no hash — but as a side effect. The reason is that the documentation is a control only when the wrong state cannot be reached quietly, and a hashed blank is as quiet as an unhashed one.",
                            r"Whether a model has limitations is not the claim. The claim is that the team looked and recorded what it found; an empty list cannot distinguish a thorough review from a skipped one.",
                        ],
                        "why": r"""
Documentation becomes a control when a missing section is an error rather than
a blank. An empty `limitations` under a heading looks finished, and a reader
later cannot tell whether the team found none or never looked. Raising at render
time makes the omission loud while someone can still act on it. That the
unrendered card also cannot be hashed and bound into the log is a welcome
consequence, but the mechanism is the refusal, not the hash.
""",
                    },
                    {
                        "q": "A chain verifies against a witnessed head. An entry in it reads `{\"event\": \"evaluated\", \"accuracy\": 0.91}`. What does the verified chain establish about that entry?",
                        "opts": [
                            "That an evaluation was run and scored 0.91, since the entry could not have been added otherwise",
                            "That the entry has not been altered since the head was witnessed, and nothing about whether it was true",
                            "That the entry was written at the time its position in the sequence implies, relative to the other entries",
                            "That the evaluation's own data can be recovered by inverting the hash, if the entry is ever disputed",
                        ],
                        "a": 1,
                        "whys": [
                            r"Anyone with append access could have written that entry without running anything. The chain preserves it faithfully either way; integrity of the record is not accuracy of the claim.",
                            r"Tamper-evidence is about changes after the fact. It fixes the bytes; whether those bytes described something that happened depends on who wrote them and what else was recorded.",
                            r"The sequence fixes the order of entries, not the times. An entry can carry a timestamp, but the timestamp is itself a claim inside the entry, preserved with the same fidelity as any other claim.",
                            r"A hash is one-way; nothing is recovered from it. The chain holds the entry's content in the clear and the hash proves it unchanged — it does not store or reconstruct the evaluation behind it.",
                        ],
                        "why": r"""
The chain converts "the log was not rewritten since the head was witnessed" into
a checkable fact. It does not convert "the log was accurate" into one. An entry
that claims an evaluation was preserved exactly as written, whether or not an
evaluation happened, and its timestamp — if it has one — is a claim inside the
entry with no more standing than the accuracy figure. Binding the model card's
hash into the log adds a second fixed artefact to point at; the truth of what
either says still rests on who wrote it.
""",
                    },
                ],
            },
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
