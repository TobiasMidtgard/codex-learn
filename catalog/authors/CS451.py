"""CS451 — Research Methods & Experimental Computer Science. Author module."""

COURSE = {
    "id": "CS451",
    "title": "Research Methods & Experimental Computer Science",
    "year": 5,
    "level": "Advanced",
    "prereqs": ["MA201", "SE201", "CS301"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "⌕",
    "summary": (
        "A thesis is not a program that works; it is a claim somebody else can check. "
        "This course is the machinery for making one: reading a paper for the claim it "
        "actually supports, designing an experiment whose factors are not confounded, "
        "putting an interval round a benchmark result instead of a mean of three runs, "
        "correcting a p-value across the family of comparisons you really ran, and "
        "building a harness that re-runs the whole thing and notices when it does not "
        "come out the same. Every idea here arrives as code you can execute."
    ),
    "outcomes": [
        "Reduce a paper to a ledger of claims, each with its magnitude, baseline and uncertainty",
        "Lay out a factorial design, detect confounded factors, and size it from a minimum detectable effect",
        "Report a benchmark as a bootstrap interval over timing samples rather than a mean of three runs",
        "Estimate a speedup with an interval, and say what a ratio interval that straddles 1 means",
        "Compute permutation p-values and correct a family of comparisons with Holm-Bonferroni",
        "Build a re-run harness that hashes artefacts and locates the step that is not reproducible",
        "Assemble the four into one study report that states what it found and what it could not",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone study harness (60%).",
    "reading": [
        "Jain, *The Art of Computer Systems Performance Analysis* (Wiley, 1991) — parts II and IV",
        "Georges, Buytaert & Eeckhout, 'Statistically Rigorous Java Performance Evaluation', OOPSLA 2007",
        "Efron & Tibshirani, *An Introduction to the Bootstrap* (Chapman & Hall, 1993) — chapters 6, 12-14",
        "Holm, 'A Simple Sequentially Rejective Multiple Test Procedure', Scand. J. Statist. 6 (1979)",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Reading a paper for the claim it supports",
            "summary": "Turning an abstract into a ledger of claims, each with a magnitude, a baseline and an uncertainty.",
            "concepts": [
                "A citable claim carries three things: a magnitude, the baseline it is relative to, and an uncertainty",
                "A structured abstract separates the evidence (Results) from the sales pitch (Conclusion)",
                "The Conclusion field routinely generalises past the Method field's scope, and it is the sentence people quote",
                "Reading order is claim, then method, then results — front to back is the slowest way to find out a paper is irrelevant",
                "A claim ledger is a table of rows a machine can count, not an impression",
                "A sentence splitter for scientific prose must not break 41.2 into two sentences",
                "The ledger says nothing about whether the experiment was any good — that is the next module",
            ],
            "read": [
                {
                    "title": "Nine per cent faster than what?",
                    "minutes": 13,
                    "body": r'''
Here is a structured abstract, of the kind a systems conference asks for. It is
invented, but its shape is not.

```text
Background:  Regular-expression matching dominates the cost of log ingestion.
Objective:   We ask what compiling each pattern ahead of time to a DFA does to
             end-to-end ingestion latency.
Method:      We built AOTRE and compared it with the standard library matcher on
             the 12 patterns of a public Zeek log corpus, 3 runs of each pattern,
             one machine.
Results:     Median ingestion latency was 8.7 per cent lower than the standard
             library matcher (37.6 ms against 41.2 ms; 95% CI [6.1, 11.2]).
Conclusion:  Ahead-of-time compilation makes log ingestion substantially faster.
```

Six months later somebody writes, in the related-work section of their own paper,
*ahead-of-time compilation makes log ingestion substantially faster [14]*. That
sentence is in the abstract, word for word, so the citation is accurate. It is also
almost content-free, and the gap between those two facts is the subject of this
module.

## Three things a number needs before it can be quoted

Put the Results sentence and the Conclusion sentence side by side and ask what the
second one lost.

The Results sentence says **8.7 per cent** — a magnitude. It says **lower than the
standard library matcher** — a baseline, the thing the magnitude is relative to. And
it says **95% CI [6.1, 11.2]** — an uncertainty, the range the study is prepared to
defend. Take away any one of the three and the sentence stops being checkable.
Without the magnitude you have "faster", which is compatible with 0.4 per cent.
Without the baseline you have "8.7 per cent faster", which is compatible with being
slower than everything anyone would actually use. Without the uncertainty you have
one number from one sample, and no way to tell 8.7 from noise.

That is not a definition handed down; it is what is left when you subtract the
Conclusion from the Results. The Conclusion has none of the three. It is the only
sentence in the abstract written to be quotable, and it is quotable precisely because
it has been stripped of everything that would let a reader disagree with it.

So the rule for the whole module: **a claim is citable when it names a magnitude, a
baseline and an uncertainty.** Anything comparative that does not is a row in the
ledger with a hole in it, and the hole is the interesting part.

## Counting the three, by machine

The rule is mechanical enough to execute. Split the abstract into its fields, and for
each field count the numbers, look for a word that introduces a comparison, and look
for a marker of spread.

```python
import re

ABSTRACT = """
Background: Regular-expression matching dominates the cost of log ingestion.
Objective: We ask what compiling each pattern ahead of time to a DFA does to
  end-to-end ingestion latency.
Method: We built AOTRE and compared it with the standard library matcher on the
  12 patterns of a public Zeek log corpus, 3 runs of each pattern, one machine.
Results: Median ingestion latency was 8.7 per cent lower than the standard
  library matcher (37.6 ms against 41.2 ms; 95% CI [6.1, 11.2]).
Conclusion: Ahead-of-time compilation makes log ingestion substantially faster.
"""

FIELD = re.compile(r"^([A-Z][a-z]+):\s*(.*)$")
QUANTITY = re.compile(r"\d+(?:\.\d+)?")
BASELINE = ("than", "compared", "against", "versus")
UNCERTAINTY = ("CI", "interval", "s.d.", "standard deviation")

fields = []
for line in ABSTRACT.strip().split("\n"):
    m = FIELD.match(line)
    if m:
        fields.append([m.group(1), m.group(2)])
    else:
        fields[-1][1] += " " + line.strip()

for name, text in fields:
    n = len(QUANTITY.findall(text))
    base = any(w in text for w in BASELINE)
    spread = any(w in text for w in UNCERTAINTY)
    print(f"{name:<11} numbers={n}  baseline={base!s:<5} uncertainty={spread}")
```

The table it prints is the paper in miniature:

```text
Background  numbers=0  baseline=False uncertainty=False
Objective   numbers=0  baseline=False uncertainty=False
Method      numbers=2  baseline=True  uncertainty=False
Results     numbers=6  baseline=True  uncertainty=True
Conclusion  numbers=0  baseline=False uncertainty=False
```

One row has all three. It is not the row anybody cites.

## What the Method field is for

The Method row is the one that decides whether the Results row means anything
outside the paper. It carries two numbers, 12 and 3, and both are small. Twelve
patterns from one corpus; three runs of each. One machine — a number so unremarkable
it was written as a word.

Now re-read the Conclusion with those three facts in hand. *Log ingestion* is a
population; the study saw twelve patterns from one corpus. *Substantially faster* is
a claim about magnitude; the study measured a median difference whose interval runs
down to 6.1 per cent. *Makes* is a claim about mechanism on any machine; the study
ran on one. None of that makes the paper wrong. It makes the Conclusion a sentence
about a different, larger thing than the one that was measured, and the distance
between the two is called **scope**.

Scope is why the ledger records which field a claim came from. A quantified claim in
the Results field is evidence. The same claim in the Conclusion field, with the
numbers removed, is an extrapolation — and reading the abstract from the bottom up
is the fastest way to see whether the authors did it.

## The mistake, and why it is tempting

The mistake is citing the Conclusion. Everybody knows not to, and everybody does it,
because of a structural fact about the two sentences: the Conclusion is the only one
that can be dropped into your own prose without editing. The Results sentence would
have to be rewritten to fit — it carries a corpus, an interval and two absolute
latencies, and all of that has to be introduced before it makes sense. The Conclusion
is already a clause in someone else's paragraph.

The second temptation is subtler and shows up in your own writing rather than your
reading. Having measured 8.7 per cent with an interval of [6.1, 11.2], it is very
natural to write a conclusion that says "substantially faster", because you know what
the numbers were and the sentence feels like a faithful summary *to you*. It is not
faithful to a reader who has only the sentence. The test is whether the sentence
survives being read by someone who never sees the Results field, and the honest
version of the same conclusion is not much longer: *ahead-of-time compilation lowered
median ingestion latency by 6 to 11 per cent on this corpus*.

## Where the ledger stops working

It is a text tool, and it has the reach of one.

It cannot tell you whether the experiment was sound. A sentence reading *our method
is 40 per cent faster than the baseline (95% CI [38, 42])* scores a perfect three out
of three and can still come from a baseline nobody tuned, a test set the method was
developed on, or twelve runs on a laptop that was compiling something else at the
time. Those are module 2 and module 3.

It cannot read an unstructured abstract as reliably. A paragraph abstract has the
same fields in it, but they are separated by rhetoric rather than by labels, and the
field a sentence belongs to becomes a judgement.

And keyword matching mistakes prose for meaning in both directions: *no faster than
the baseline* contains the word *than* and reports a baseline, which is right, while
a sentence reporting a 40 per cent regression is scored exactly like one reporting a
40 per cent improvement, because *lower* and *higher* are both comparisons. The
ledger is a way of finding the sentences worth reading closely. It is not a way of
avoiding reading them.

## One detail the lab will make you get right

Sentence splitting. Scientific prose is full of periods that do not end sentences,
and the naive split is worse than it looks:

```python
import re

SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")
line = ("Median ingestion latency was 8.7 per cent lower than the standard "
        "library matcher (37.6 ms against 41.2 ms; 95% CI [6.1, 11.2]). "
        "The effect held on all 12 patterns.")
for i, s in enumerate(SENTENCE.split(line), 1):
    print(i, s)
print("pieces from splitting on a bare period:", len(line.split(".")))
```

Two sentences, correctly. Splitting on the period alone gives eight pieces, six of
them fragments of decimal numbers. The lookbehind demands a sentence-ending
punctuation mark, the `\s+` demands the space that a decimal point never has after
it, and the lookahead demands that whatever comes next starts a sentence.

That is the first function of **the lab for this module, a claim ledger from a
structured abstract**: `parse_abstract`, `sentences`, `quantities`,
`mentions_baseline`, `mentions_uncertainty`, `grade`, `claim_ledger` and `audit`.
Handed the abstract above, your `audit` has to find exactly one supported claim, and
it has to flag the Conclusion — the sentence everybody cites — as an overreach.
''',
                },
            ],
            "quiz": {
                "title": "What a claim has to carry",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A results sentence reads: *our scheduler cut tail latency by 22 per cent (95% CI [19, 25])*. Which of the three parts of a citable claim is missing?",
                        "opts": [
                            "The baseline — nothing says what the 22 per cent is measured against",
                            "The uncertainty — an interval is not really a statement of uncertainty",
                            "The magnitude — a percentage is a ratio, so no absolute size is stated",
                            "Nothing is missing; a magnitude with an interval beside it is enough",
                        ],
                        "a": 0,
                        "whys": [
                            "Cut it from what? A previous version of the same scheduler, the default one, or the best published result are three very different claims, and a reader cannot tell which was meant.",
                            "The interval is exactly what an uncertainty is: the range the study is prepared to defend. This sentence has one, and it is the part it does best.",
                            "Twenty-two per cent is a magnitude. It is relative rather than absolute, which is why it needs a baseline stated, but the size itself is on the page.",
                            "Two of the three are present and the third is not. A magnitude and an interval with no named comparison can be read as a huge result or a trivial one.",
                        ],
                        "why": r"""
Magnitude, baseline, uncertainty. The 22 per cent is the magnitude and the interval
[19, 25] is the uncertainty, but *cut by 22 per cent* is a comparison with nothing
named on the other side of it. Against an untuned default it may be unremarkable;
against the best published scheduler it may be the paper. Notice that the interval
being narrow does nothing to repair this — a precise measurement of an unnamed
comparison is a precise measurement of nothing in particular.
""",
                    },
                    {
                        "q": "Why does a claim ledger record which field of the abstract each sentence came from, rather than the sentence alone?",
                        "opts": [
                            "Because the field is what tells you whether a sentence is evidence or an extrapolation from it",
                            "Because sentences in later fields are more likely to be quantified than early ones",
                            "Because the ordering of the fields is fixed, so the field can be recovered from the position anyway",
                            "Because only the Method field is allowed to contain numbers in a structured abstract",
                        ],
                        "a": 0,
                        "whys": [
                            "The same words carry different weight in different fields: quantified in Results they are a measurement, unquantified in Conclusion they are a generalisation of it.",
                            "The traffic runs the other way in most abstracts. Results is where the numbers are, and Conclusion is usually the least quantified field in the whole paper.",
                            "Position and field are indeed redundant when the labels are present, but that is an argument about storage, not about why the distinction is worth keeping at all.",
                            "Results is where most numbers live, and Method carries the design's counts. No field is forbidden numbers; the fields differ in what a number there means.",
                        ],
                        "why": r"""
A sentence saying *log ingestion is substantially faster* is a summary when it sits
in Results underneath the measurements, and a generalisation past the measured scope
when it sits in Conclusion with the numbers removed. The words can be identical. What
changes their status is the field, which is why the ledger keeps it as a column and
why `overreach` in the lab is defined as a comparative Conclusion sentence with no
number behind it.
""",
                    },
                    {
                        "q": "A paper's Method field says *12 patterns from one corpus, 3 runs each, one machine*. What does that most directly limit?",
                        "opts": [
                            "The scope: the population that the measured effect can be claimed to hold for",
                            "The magnitude: an effect measured on 12 patterns must be smaller than the truth",
                            "The direction: with so few runs the sign of the difference cannot be settled",
                            "Nothing much, provided the confidence interval reported alongside is narrow",
                        ],
                        "a": 0,
                        "whys": [
                            "Twelve patterns from one corpus on one machine is what was sampled, and it is the widest population the result can be claimed for without an argument that the sample represents more.",
                            "A small sample makes an estimate noisy, not systematically small. Selection effects can bias a result in either direction, and nothing here forces it downwards.",
                            "The sign is recoverable from very few runs when the effect is large relative to the spread — that is what an interval away from zero reports, and this one is.",
                            "A narrow interval says the measurement is repeatable on this corpus and this machine. It says nothing at all about the corpus and machine it was not run on.",
                        ],
                        "why": r"""
Scope is what the Method field buys and what it costs. The interval [6.1, 11.2]
describes the uncertainty in the estimate *for the thing that was measured*: twelve
patterns, one corpus, one machine. Widening that to *log ingestion* is a separate
claim requiring a separate argument, and no amount of narrowing the interval supplies
it. This is why the ledger keeps the Method row even though it rarely contains a
claim itself: it is the row that bounds every other row.
""",
                    },
                    {
                        "q": "Splitting an abstract into sentences on the period alone is a bad idea. What specifically breaks?",
                        "opts": [
                            "Decimal numbers split into two pieces, so 41.2 ms becomes two fragments",
                            "Sentences ending in a question mark are joined to the sentence after them",
                            "The field labels are lost, because a colon is treated as a sentence end",
                            "Nothing breaks in practice; the pieces just need their whitespace stripped afterwards",
                        ],
                        "a": 0,
                        "whys": [
                            "Every decimal in the abstract is a false sentence boundary, and a results field is mostly decimals — six of the eight pieces in the worked example are fragments of numbers.",
                            "That is a genuine flaw of splitting on the period, but a smaller one: abstracts rarely ask questions, while they are full of decimals.",
                            "A colon is not a period, so field labels survive a period split intact. They are lost by a different mistake, splitting before the fields are parsed.",
                            "Stripping whitespace does not rejoin 41 and 2, and a ledger built on those fragments finds comparative words in sentences that were never sentences.",
                        ],
                        "why": r"""
The worked example splits into eight pieces on a bare period where there are two
sentences, and six of the eight are halves of decimal numbers. The fix is to demand
the things a decimal point never has: whitespace after the period, and a capital
letter or an opening bracket after that. Hence `(?<=[.!?])\s+(?=[A-Z(])`, three
conditions each of which a decimal fails. Abbreviations such as *cf.* and *Fig. 3*
still defeat it, which is a limit worth knowing rather than a reason to go back.
""",
                    },
                    {
                        "q": "Two sentences each score three out of three on magnitude, baseline and uncertainty. One reports a 40 per cent improvement, the other a 40 per cent regression. How does the ledger treat them?",
                        "opts": [
                            "Identically — it detects that a comparison was made, never which way it went",
                            "It scores the regression lower, because a regression is not a contribution",
                            "It refuses the regression, because a negative result has no magnitude to record",
                            "It scores the improvement lower, because improvements are the claims most often overstated",
                        ],
                        "a": 0,
                        "whys": [
                            "The words that mark a comparison are direction-blind: lower and higher, fell and rose, are all merely evidence that two things were put side by side.",
                            "The ledger has no notion of which result the authors wanted. A regression reported with a magnitude, a baseline and an interval is exactly as citable as an improvement.",
                            "A regression has a perfectly good magnitude — 40 per cent of it. Nothing in the scoring inspects the sign of the effect at all.",
                            "The scoring has no model of author incentives, and could not act on one if it did. It counts three features of a sentence and stops there.",
                        ],
                        "why": r"""
It is keyword matching, so it sees that a comparison happened and not which way. That
is a real limit and worth stating plainly: the ledger finds the sentences that carry
checkable claims, and then you read them. Treating the score as a verdict on the
paper is the way this tool gets misused. The same blindness is why *no faster than
the baseline* scores a baseline: the word is there, and the negation is not something
a word list can see.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The grading rule, five holes deep",
                "minutes": 9,
                "lang": "python",
                "caption": "ledger.py — how a sentence is scored, and what counts as overreach",
                "brief": r'''
The whole ledger rests on one small function that puts a sentence into one of three
buckets, and on one filter that says which of those rows is worth complaining about.
Every hole below is a decision that changes what the audit reports without changing
whether it runs.

Nothing is executed here. Filled in correctly, the Results sentence of the worked
abstract grades as supported and the Conclusion sentence grades as unquantified.
''',
                "listing": r'''
QUANTITY = re.compile(r"\d+(?:\.\d+)?")
COMPARATIVE = ("faster", "slower", "lower", "higher", "reduction", "than")
BASELINE = ("than", "compared", "against", "versus", "baseline")
UNCERTAINTY = ("CI", "±", "interval", "s.d.", "standard deviation")


def grade(sentence):
    """One of supported, vague or unquantified; None when nothing is being compared."""
    if not any(word in sentence.lower() for word in ___):
        return None
    numbers = QUANTITY.findall(sentence)
    if ___:
        return "unquantified"
    if not any(mark in sentence for mark in ___):
        return "vague"
    if not any(word in sentence.lower() for word in BASELINE):
        return ___
    return "supported"


def overreach(rows):
    """Comparative conclusions with no number behind them."""
    return [r for r in rows if r["field"] == ___ and r["grade"] == "unquantified"]
''',
                "blanks": [
                    {
                        "prompt": "Which list decides whether this sentence is making a comparison at all?",
                        "hole": "?",
                        "opts": ["COMPARATIVE", "UNCERTAINTY", "BASELINE", "QUANTITY.findall(sentence)"],
                        "a": 0,
                        "why": "A sentence that compares nothing is not a claim about a difference, so it leaves the ledger entirely. COMPARATIVE is the only list whose members are all lowercase, which matters because the test lowercases the sentence first.",
                        "whys": [
                            "A sentence that compares nothing is not a claim about a difference, so it leaves the ledger entirely. COMPARATIVE is the only list whose members are all lowercase, which matters because the test lowercases the sentence first.",
                            "This asks whether the sentence reports a spread, which is the third test rather than the first, and it holds CI in capitals — against a lowercased sentence that member can never match.",
                            "Close, and it shares the word than with the comparative list, so it would let many real claims through. It would also admit a method sentence saying compared with previous work, which describes the design rather than making a claim.",
                            "This returns the numbers in the sentence, so the test would ask whether any digit appears inside the lowercased sentence. Every sentence containing a number would be admitted and every purely verbal comparison dropped.",
                        ],
                    },
                    {
                        "prompt": "The sentence compares something. When is it unquantified?",
                        "hole": "?",
                        "opts": ["not numbers", "numbers", "len(numbers) > 1", "numbers is None"],
                        "a": 0,
                        "why": "findall returns a list, and an empty list is falsy, so an absent magnitude is exactly an empty match list. This is the branch that catches the Conclusion sentence of the worked abstract.",
                        "whys": [
                            "findall returns a list, and an empty list is falsy, so an absent magnitude is exactly an empty match list. This is the branch that catches the Conclusion sentence of the worked abstract.",
                            "Inverted: this returns unquantified whenever numbers were found and falls through whenever none were. The Results sentence would be reported as the empty one and the Conclusion as fully supported.",
                            "This makes a single number count as no number at all, so a clean claim of the form 8.7 per cent lower with no other figure in it is thrown into the wrong bucket.",
                            "findall never returns None; it returns an empty list. The test is false whatever the sentence says, so no sentence is ever reported as unquantified.",
                        ],
                    },
                    {
                        "prompt": "There is a magnitude. Which list decides whether an uncertainty was reported?",
                        "hole": "?",
                        "opts": ["UNCERTAINTY", "COMPARATIVE", "BASELINE", "numbers"],
                        "a": 0,
                        "why": "UNCERTAINTY holds the markers a spread is written with, and the test deliberately does not lowercase the sentence so that CI matches as written. A magnitude with no spread beside it is one sample dressed as a finding.",
                        "whys": [
                            "UNCERTAINTY holds the markers a spread is written with, and the test deliberately does not lowercase the sentence so that CI matches as written. A magnitude with no spread beside it is one sample dressed as a finding.",
                            "This tests for a comparison, which was already established by the first branch. Every sentence reaching this line passes it, so nothing is ever graded as vague.",
                            "This tests for a named comparison, and it is used two lines further down. Putting it here checks the same thing twice and leaves the uncertainty unexamined entirely.",
                            "These are the strings that were found, so the test asks whether one of them appears in the sentence they came from. That is always true, and again nothing is ever vague.",
                        ],
                    },
                    {
                        "prompt": "There is a magnitude and a spread, but no baseline is named. What is this claim?",
                        "hole": "?",
                        "opts": ['"vague"', '"supported"', '"unquantified"', "None"],
                        "a": 0,
                        "why": "Two of the three parts are present and the third is not, which is the definition of vague here: a precise measurement of an unnamed comparison. It is the bucket that catches cut tail latency by 22 per cent with an interval and no named rival.",
                        "whys": [
                            "Two of the three parts are present and the third is not, which is the definition of vague here: a precise measurement of an unnamed comparison. It is the bucket that catches cut tail latency by 22 per cent with an interval and no named rival.",
                            "This makes the baseline check dead code: the branch computes an answer and then returns the same verdict the line below returns anyway, so a claim with nothing to compare against is called citable.",
                            "There is a number in the sentence, so calling it unquantified contradicts the branch above and puts a measured claim in the bucket reserved for slogans.",
                            "Returning None drops the row out of the ledger, which hides the most common defective claim there is rather than recording it.",
                        ],
                    },
                    {
                        "prompt": "Which field is being singled out as the place a bare comparison does real damage?",
                        "hole": "?",
                        "opts": ['"conclusion"', '"results"', '"method"', '"background"'],
                        "a": 0,
                        "why": "The Conclusion field is the one whose sentences get quoted, and a comparative sentence there with no number is the extrapolation this whole exercise exists to catch.",
                        "whys": [
                            "The Conclusion field is the one whose sentences get quoted, and a comparative sentence there with no number is the extrapolation this whole exercise exists to catch.",
                            "An unquantified comparison in Results would be worth a raised eyebrow, but that field carries the measurements and rarely offends. Filtering on it reports almost nothing.",
                            "The Method field describes the design, and comparative language there is usually ordinary prose about what was compared with what rather than a claim about the outcome.",
                            "Background summarises other people's work, where unquantified comparisons are expected and carry the citation that supports them. Flagging those buries the real finding in noise.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "A claim ledger from a structured abstract",
                "minutes": 45,
                "runtime": "python",
                "brief": r'''
Turn an abstract into rows a machine can count. Everything lives in `main.py`,
which already holds the worked abstract as `ABSTRACT` and the four word lists.

1. `parse_abstract(text)` — a dict mapping the **lowercased** field name to the
   field's text. A field starts on a line matching `Name:`; any line that does
   not is a continuation and is appended to the field above it with a single
   space between. Text before the first field label, or text with no field
   label at all, is a `ValueError`. Insertion order is the order of the fields.

2. `sentences(text)` — split on `(?<=[.!?])\s+(?=[A-Z(])` and drop empties.
   `41.2 ms` must survive as one token.

3. `quantities(sentence)` — every number, with an immediately following unit
   when there is one, using `\d+(?:\.\d+)?(?:\s*(?:%|per cent|ms|s\b))?`.
   So `(37.6 ms against 41.2 ms; 95% CI [6.1, 11.2])` gives five entries,
   two of them carrying `ms` and one carrying `%`.

4. `mentions_baseline(sentence)` and `mentions_uncertainty(sentence)` — the
   first is case-insensitive against `BASELINE`, the second is **case
   sensitive** against `UNCERTAINTY`, so that `CI` matches as written.

5. `is_comparative(sentence)` — case-insensitive against `COMPARATIVE`.

6. `grade(sentence)` — `None` when the sentence is not comparative, otherwise
   `"unquantified"` with no quantity, `"vague"` with a quantity but no
   uncertainty **or** no baseline, and `"supported"` with all three.

7. `claim_ledger(text)` — one row per comparative sentence, in reading order:
   `{"field": ..., "sentence": ..., "quantities": [...], "grade": ...}`.

8. `overreach(rows)` — the rows whose field is `"conclusion"` and whose grade
   is `"unquantified"`.

9. `audit(text)` — `{"claims", "supported", "vague", "unquantified",
   "overreach"}`, where the first four are counts and `overreach` is a list of
   the offending **sentences**.

```text
audit(ABSTRACT) == {
    "claims": 3, "supported": 1, "vague": 1, "unquantified": 1,
    "overreach": ["Ahead-of-time compilation makes log ingestion substantially faster."],
}
```

Three comparative sentences, one per bucket. The Method sentence is one of
them, and it is a false positive worth meeting early: it says *compared* and it
carries the numbers 12 and 3, but those are design counts rather than a
measured magnitude, and it reports no spread. Work out which bucket each of the
three lands in before you run anything; the checks are unforgiving about it.
''',
                "hints": [
                    "Build `parse_abstract` with a running `current` name: on a match, start a new field; otherwise append to `current`, and raise if `current` is still None.",
                    "`re.split` with a pattern made only of lookarounds and `\\s+` consumes the whitespace and keeps both sentences whole.",
                    "In `quantities`, put `per cent` before `%` in the alternation only if you want it preferred — they cannot both match at the same position, so the order that matters is `ms` before `s\\b`.",
                    "`grade` is a chain of early returns in the order comparative, quantity, uncertainty, baseline. Write it in that order and the buckets fall out.",
                    "The Method sentence is comparative and has numbers but no interval, so it is not supported and not unquantified either. Decide which bucket that leaves before arguing with the checks.",
                ],
                "files": [{"name": "main.py", "content": r'''
import re

ABSTRACT = """
Background: Regular-expression matching dominates the cost of log ingestion.
Objective: We ask what compiling each pattern ahead of time to a DFA does to
  end-to-end ingestion latency.
Method: We built AOTRE and compared it with the standard library matcher on the
  12 patterns of a public Zeek log corpus, 3 runs of each pattern, one machine.
Results: Median ingestion latency was 8.7 per cent lower than the standard
  library matcher (37.6 ms against 41.2 ms; 95% CI [6.1, 11.2]).
Conclusion: Ahead-of-time compilation makes log ingestion substantially faster.
"""

FIELD = re.compile(r"^([A-Z][A-Za-z]*):\s*(.*)$")
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")
QUANTITY = re.compile(r"\d+(?:\.\d+)?(?:\s*(?:%|per cent|ms|s\b))?")

COMPARATIVE = ("faster", "slower", "lower", "higher", "reduction", "reduced",
               "improve", "outperform", "cut", "fell", "rose",
               "than", "compared", "versus", "against")
BASELINE = ("than", "compared", "against", "versus", "baseline")
UNCERTAINTY = ("CI", "±", "interval", "s.d.", "standard deviation")


def parse_abstract(text):
    """Lowercased field name -> field text, continuation lines joined."""
    # your code here


def sentences(text):
    """Split scientific prose without breaking decimals."""
    # your code here


def quantities(sentence):
    """Every number, with its unit when one follows immediately."""
    # your code here


def mentions_baseline(sentence):
    """True when the sentence names what it is comparing against."""
    # your code here


def mentions_uncertainty(sentence):
    """True when the sentence reports a spread. Case sensitive, for CI."""
    # your code here


def is_comparative(sentence):
    """True when the sentence puts two things side by side."""
    # your code here


def grade(sentence):
    """None, or one of unquantified, vague, supported."""
    # your code here


def claim_ledger(text):
    """One row per comparative sentence, in reading order."""
    # your code here


def overreach(rows):
    """Comparative conclusions with no number behind them."""
    # your code here


def audit(text):
    """Counts per bucket, plus the offending conclusion sentences."""
    # your code here


if __name__ == "__main__":
    report = audit(ABSTRACT)
    if report:
        for key in ("claims", "supported", "vague", "unquantified"):
            print(f"{key:<13} {report[key]}")
        for sentence in report["overreach"]:
            print("overreach:", sentence)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import re

ABSTRACT = """
Background: Regular-expression matching dominates the cost of log ingestion.
Objective: We ask what compiling each pattern ahead of time to a DFA does to
  end-to-end ingestion latency.
Method: We built AOTRE and compared it with the standard library matcher on the
  12 patterns of a public Zeek log corpus, 3 runs of each pattern, one machine.
Results: Median ingestion latency was 8.7 per cent lower than the standard
  library matcher (37.6 ms against 41.2 ms; 95% CI [6.1, 11.2]).
Conclusion: Ahead-of-time compilation makes log ingestion substantially faster.
"""

FIELD = re.compile(r"^([A-Z][A-Za-z]*):\s*(.*)$")
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")
QUANTITY = re.compile(r"\d+(?:\.\d+)?(?:\s*(?:%|per cent|ms|s\b))?")

COMPARATIVE = ("faster", "slower", "lower", "higher", "reduction", "reduced",
               "improve", "outperform", "cut", "fell", "rose",
               "than", "compared", "versus", "against")
BASELINE = ("than", "compared", "against", "versus", "baseline")
UNCERTAINTY = ("CI", "±", "interval", "s.d.", "standard deviation")


def parse_abstract(text):
    """Lowercased field name -> field text, continuation lines joined."""
    fields = {}
    current = None
    for line in str(text).strip().split("\n"):
        if not line.strip():
            continue
        match = FIELD.match(line)
        if match:
            current = match.group(1).lower()
            fields[current] = match.group(2).strip()
        elif current is None:
            raise ValueError("text before the first field label: " + line.strip()[:40])
        else:
            fields[current] = (fields[current] + " " + line.strip()).strip()
    if not fields:
        raise ValueError("no field labels found — this is not a structured abstract")
    return fields


def sentences(text):
    """Split scientific prose without breaking decimals."""
    return [s.strip() for s in SENTENCE.split(str(text).strip()) if s.strip()]


def quantities(sentence):
    """Every number, with its unit when one follows immediately."""
    return [m.strip() for m in QUANTITY.findall(sentence)]


def mentions_baseline(sentence):
    """True when the sentence names what it is comparing against."""
    low = sentence.lower()
    return any(word in low for word in BASELINE)


def mentions_uncertainty(sentence):
    """True when the sentence reports a spread. Case sensitive, for CI."""
    return any(mark in sentence for mark in UNCERTAINTY)


def is_comparative(sentence):
    """True when the sentence puts two things side by side."""
    low = sentence.lower()
    return any(word in low for word in COMPARATIVE)


def grade(sentence):
    """None, or one of unquantified, vague, supported."""
    if not is_comparative(sentence):
        return None
    if not quantities(sentence):
        return "unquantified"
    if not mentions_uncertainty(sentence):
        return "vague"
    if not mentions_baseline(sentence):
        return "vague"
    return "supported"


def claim_ledger(text):
    """One row per comparative sentence, in reading order."""
    rows = []
    for field, body in parse_abstract(text).items():
        for sentence in sentences(body):
            verdict = grade(sentence)
            if verdict is None:
                continue
            rows.append({"field": field, "sentence": sentence,
                         "quantities": quantities(sentence), "grade": verdict})
    return rows


def overreach(rows):
    """Comparative conclusions with no number behind them."""
    return [r for r in rows if r["field"] == "conclusion" and r["grade"] == "unquantified"]


def audit(text):
    """Counts per bucket, plus the offending conclusion sentences."""
    rows = claim_ledger(text)
    return {
        "claims": len(rows),
        "supported": sum(1 for r in rows if r["grade"] == "supported"),
        "vague": sum(1 for r in rows if r["grade"] == "vague"),
        "unquantified": sum(1 for r in rows if r["grade"] == "unquantified"),
        "overreach": [r["sentence"] for r in overreach(rows)],
    }


if __name__ == "__main__":
    report = audit(ABSTRACT)
    if report:
        for key in ("claims", "supported", "vague", "unquantified"):
            print(f"{key:<13} {report[key]}")
        for sentence in report["overreach"]:
            print("overreach:", sentence)
'''}],
                "tests": [
                    {"name": "parse_abstract keeps five fields in order and joins continuations", "code": r'''
_f = parse_abstract(ABSTRACT)
assert list(_f) == ["background", "objective", "method", "results", "conclusion"], \
    f"fields were {list(_f)!r}"
assert _f["objective"].endswith("ingestion latency."), \
    f"the continuation line was not joined: {_f['objective']!r}"
assert "  " not in _f["method"], f"continuations join with one space: {_f['method']!r}"
assert _f["conclusion"] == "Ahead-of-time compilation makes log ingestion substantially faster.", \
    f"got {_f['conclusion']!r}"
'''},
                    {"name": "An unlabelled abstract is refused", "code": r'''
for _bad in ("Regular expressions are slow. We made them faster.",
             "We measured it.\nBackground: too late to matter."):
    try:
        parse_abstract(_bad)
        assert False, f"parse_abstract({_bad[:24]!r}...) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "sentences does not split a decimal", "code": r'''
_line = ("Latency was 8.7 per cent lower (37.6 ms against 41.2 ms; 95% CI [6.1, 11.2]). "
         "The effect held on all 12 patterns.")
_got = sentences(_line)
assert len(_got) == 2, f"expected 2 sentences, got {len(_got)}: {_got!r}"
assert _got[0].endswith("[6.1, 11.2])."), f"first sentence was {_got[0]!r}"
assert _got[1] == "The effect held on all 12 patterns.", f"second sentence was {_got[1]!r}"
assert sentences("   ") == [], "an empty body has no sentences"
'''},
                    {"name": "quantities keeps the unit that follows a number", "code": r'''
_got = quantities("(37.6 ms against 41.2 ms; 95% CI [6.1, 11.2])")
assert _got == ["37.6 ms", "41.2 ms", "95%", "6.1", "11.2"], f"got {_got!r}"
assert quantities("8.7 per cent lower") == ["8.7 per cent"], \
    f"got {quantities('8.7 per cent lower')!r}"
assert quantities("3 runs of each pattern") == ["3"], \
    "a following word that is not a unit must not be swallowed"
assert quantities("no numbers here") == [], "a sentence with no digits has no quantities"
'''},
                    {"name": "baseline and uncertainty are detected, and CI is case sensitive", "code": r'''
assert mentions_baseline("8.7 per cent lower than the standard library matcher")
assert mentions_baseline("Compared with the default scheduler, ours wins"), "case-insensitive"
assert not mentions_baseline("Median latency was 37.6 ms")
assert mentions_uncertainty("a reduction of 8.7 per cent (95% CI [6.1, 11.2])")
assert mentions_uncertainty("37.6 ± 1.4 ms")
assert not mentions_uncertainty("we ci ted the original paper"), \
    "UNCERTAINTY is matched case sensitively so that CI does not fire on ordinary prose"
'''},
                    {"name": "grade puts each sentence of the abstract in the right bucket", "code": r'''
_f = parse_abstract(ABSTRACT)
assert grade(_f["background"]) is None, "not a comparison, so not a row at all"
assert grade(_f["objective"]) is None, "an aim is not a claim"
assert grade(_f["method"]) == "vague", \
    f"the method sentence compares and carries counts but reports no spread: got {grade(_f['method'])!r}"
assert grade(_f["results"]) == "supported", f"got {grade(_f['results'])!r}"
assert grade(_f["conclusion"]) == "unquantified", f"got {grade(_f['conclusion'])!r}"
assert grade("Ours cut tail latency by 22 per cent (95% CI [19, 25])") == "vague", \
    "a magnitude and an interval with nothing named to compare against is vague"
'''},
                    {"name": "claim_ledger records the field and the quantities of each row", "code": r'''
_rows = claim_ledger(ABSTRACT)
assert [r["field"] for r in _rows] == ["method", "results", "conclusion"], \
    f"rows came from {[r['field'] for r in _rows]!r}"
assert _rows[1]["quantities"] == ["8.7 per cent", "37.6 ms", "41.2 ms", "95%", "6.1", "11.2"], \
    f"results quantities were {_rows[1]['quantities']!r}"
assert _rows[2]["quantities"] == [], "the conclusion has no numbers in it at all"
assert set(_rows[0]) == {"field", "sentence", "quantities", "grade"}, \
    f"a row has four keys, got {sorted(_rows[0])!r}"
'''},
                    {"name": "audit counts the buckets and flags the conclusion", "code": r'''
_report = audit(ABSTRACT)
assert _report["claims"] == 3, f"claims was {_report['claims']}"
assert _report["supported"] == 1, f"supported was {_report['supported']}"
assert _report["vague"] == 1, f"vague was {_report['vague']}"
assert _report["unquantified"] == 1, f"unquantified was {_report['unquantified']}"
assert _report["overreach"] == \
    ["Ahead-of-time compilation makes log ingestion substantially faster."], \
    f"overreach was {_report['overreach']!r}"
assert _report["supported"] + _report["vague"] + _report["unquantified"] == _report["claims"], \
    "every row lands in exactly one bucket"
'''},
                    {"name": "overreach ignores an unquantified comparison outside the conclusion", "code": r'''
_text = ("Method: We compared it with the default matcher on 12 patterns.\n"
         "Results: Ours was faster.\n"
         "Conclusion: Ours was 9.0 per cent faster than the default (95% CI [7, 11]).")
_rows = claim_ledger(_text)
assert len(_rows) == 3, f"three comparative sentences, got {len(_rows)}"
assert overreach(_rows) == [], \
    "a quantified conclusion is not an overreach, however bare the results sentence is"
assert audit(_text)["unquantified"] == 1, "only the bare results sentence carries no magnitude"
assert audit(_text)["supported"] == 1, "the conclusion here names a magnitude, a baseline and an interval"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Designing the experiment",
            "summary": "Factors, confounds, missing cells, and how many runs the question you asked actually needs.",
            "concepts": [
                "A factor is something varied on purpose; everything else is held fixed, randomised, or recorded",
                "Two factors that move together are one column of the design, and no quantity of data separates them",
                "A full factorial design is the cross product of the levels; a missing cell is an interaction that cannot be estimated",
                r"The minimum detectable effect is $\delta = (z_{1-\alpha/2} + z_{1-\beta})\,\sigma\sqrt{2/n}$, so it falls only as $1/\sqrt{n}$",
                "Halving the effect you can detect costs four times the runs, which is why sample size is decided before the study",
                "An untuned baseline is a confound in disguise: effort is a factor, and it was not held fixed",
                "Every look at the test set spends some of its power to surprise you, so tuning decisions belong on a development split",
            ],
            "read": [
                {
                    "title": "The allocator and the machine were the same column",
                    "minutes": 14,
                    "body": r'''
A student has a custom memory allocator and wants to show it beats the system one.
The study looks careful. Two allocators, two workloads, two runs of each
combination, eight runs in all, every timing recorded to a tenth of a millisecond.

```text
run  allocator  machine  workload   ms
  1  system     A        json      76.8
  2  system     A        regex     66.5
  3  system     A        json      71.0
  4  system     A        regex     71.3
  5  custom     B        json      66.4
  6  custom     B        regex     56.1
  7  custom     B        json      61.0
  8  custom     B        regex     61.3
```

The system allocator averages 71.4 ms, the custom one 61.2 ms. That is a 14.3 per
cent reduction, and it is not small against the run-to-run scatter, which is about
4 ms in each group. As a measurement it holds up. It is worthless anyway.

The reason is in the third column. Every `system` run happened on machine A and every
`custom` run happened on machine B, because machine B was the one free on the Tuesday.
The 10.2 ms difference is the allocator, or the machine, or any mixture of the two,
and the data cannot say which — not because there were too few runs, but because
there is no arithmetic that could separate them. Sixteen more runs on the same
schedule would give the same 10.2 ms with a tighter interval around it, which is
worse: a precise measurement of a quantity that has no meaning.

## What confounding actually is

Look at what the columns do rather than what they are called. `allocator` takes the
value `system` on runs 1 to 4 and `custom` on runs 5 to 8. `machine` takes the value
`A` on runs 1 to 4 and `B` on runs 5 to 8. The two columns carry the same partition
of the eight runs. One is a relabelling of the other, so the design contains one
column that has been written down twice.

That gives a test with nothing subjective in it: two factors are confounded when
knowing the level of the first tells you the level of the second, **and** the reverse.
Both directions are needed. If every `custom` run were on machine B but the `system`
runs were split across A and B, the level of the allocator would still determine the
machine for one of its levels, and only the reverse direction would catch it.

```python
RUNS = [
    {"allocator": "system", "machine": "A", "workload": "json"},
    {"allocator": "system", "machine": "A", "workload": "regex"},
    {"allocator": "system", "machine": "A", "workload": "json"},
    {"allocator": "system", "machine": "A", "workload": "regex"},
    {"allocator": "custom", "machine": "B", "workload": "json"},
    {"allocator": "custom", "machine": "B", "workload": "regex"},
    {"allocator": "custom", "machine": "B", "workload": "json"},
    {"allocator": "custom", "machine": "B", "workload": "regex"},
]


def confounded(runs, a, b):
    """True when the level of a determines the level of b, and the reverse."""
    forward, backward = {}, {}
    for run in runs:
        forward.setdefault(run[a], set()).add(run[b])
        backward.setdefault(run[b], set()).add(run[a])
    if len(forward) < 2 or len(backward) < 2:
        return False
    return (all(len(seen) == 1 for seen in forward.values())
            and all(len(seen) == 1 for seen in backward.values()))


names = sorted(RUNS[0])
for i, a in enumerate(names):
    for b in names[i + 1:]:
        print(f"{a:<10} vs {b:<9} confounded={confounded(RUNS, a, b)}")
```

```text
allocator  vs machine   confounded=True
allocator  vs workload  confounded=False
machine    vs workload  confounded=False
```

The workload column is the one that was done properly: both workloads appear under
both allocators, so the allocator effect can be estimated with the workload varying
underneath it. That is the repair for the machine column too — run each allocator on
both machines. Eight cells instead of four, and the same eight runs.

The guard at the top of the function earns its place. A factor with a single level —
one machine for the whole study — maps that level to every level of everything else,
so `forward` has one entry and the loop below would report it as confounded with the
entire design. A constant is not confounded with anything; it is not a factor at
all, and its effect is unmeasured rather than tangled.

## How many runs the question needs

The second half of designing an experiment is deciding its size, and the honest way
round is to start from the smallest difference that would change what anyone does.
Suppose the allocator work is worth pursuing only if it saves at least 2 ms, and the
run-to-run spread of this benchmark is $\sigma = 4.0$ ms — which is roughly what the
four `system` timings above scatter by.

A two-sample comparison at significance $\alpha$ rejects when the observed difference
exceeds $z_{1-\alpha/2}$ standard errors of zero. To have probability $1-\beta$ of
getting there when the true difference is $\delta$, the true difference has to sit
$z_{1-\beta}$ standard errors beyond that threshold. So $\delta$ must cover both, in
units of the standard error of a difference of two means, which MA201 gives as
$\sigma\sqrt{2/n}$ for equal groups:

$$\delta = (z_{1-\alpha/2} + z_{1-\beta})\,\sigma\sqrt{\frac{2}{n}} .$$

Nothing was announced there: the two $z$ values are the two things that have to be
cleared, and the $\sqrt{2/n}$ is the standard error the course already had.
Rearranged for $n$,

$$n = 2\left(\frac{\sigma\,(z_{1-\alpha/2} + z_{1-\beta})}{\delta}\right)^{2} .$$

Both quantiles come out of the normal distribution, and `math.erf` is enough to
invert it by bisection.

```python
import math


def z_quantile(p):
    """The inverse standard normal, by bisection on erf."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must lie strictly between 0 and 1")
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


Z = z_quantile(0.975) + z_quantile(0.80)
print(f"z(0.975) = {z_quantile(0.975):.6f}   z(0.80) = {z_quantile(0.80):.6f}")
for n in (3, 5, 10, 20, 63):
    print(f"n={n:<3} smallest detectable difference = {Z * 4.0 * math.sqrt(2 / n):.2f} ms")
print("runs per group needed for 2.00 ms:", math.ceil(2 * (4.0 * Z / 2.0) ** 2))
```

```text
z(0.975) = 1.959964   z(0.80) = 0.841621
n=3   smallest detectable difference = 9.15 ms
n=5   smallest detectable difference = 7.09 ms
n=10  smallest detectable difference = 5.01 ms
n=20  smallest detectable difference = 3.54 ms
n=63  smallest detectable difference = 2.00 ms
runs per group needed for 2.00 ms: 63
```

Read the middle of that table before the ends. Four runs a side — the shape of the
study at the top of this reading — can only detect a difference of about 8 ms, four
times the 2 ms anyone cared about. Its observed 10.2 ms cleared that bar, and it did
so with nothing to spare; a genuine 3 ms saving would have been invisible to the same
design, and the student would have concluded there was nothing there. Going from five
runs to twenty halves the
detectable difference, exactly, because $\delta$ depends on $n$ only through
$\sqrt{2/n}$: four times the runs for half the resolution, for ever. That is the
single most useful fact in experimental design, and it is why the size of a study is
settled before it is run rather than after it disappoints.

## The mistakes, and why they are tempting

**Reporting a mean of three runs with no spread.** Three runs is a defensible number
of runs; a mean with nothing beside it is not a defensible way to report them. It is
tempting because the mean is the only number the reader asked for and the spread makes
the result look weaker. The table above is the argument against it: without $\sigma$
there is no $\delta$, so a bare mean cannot say whether the study could have detected
the effect it is claiming.

**Tuning on the test set.** You try eleven parameter settings, evaluate each on the
held-out set, and report the best. The number you report is the maximum of eleven
noisy estimates, and the maximum of eleven draws is biased upwards even when all
eleven are the same underlying quantity. It is tempting because each individual
evaluation felt like an honest measurement, and it was — the dishonesty is in the
selection, which nobody wrote down. The fix costs nothing: choose on a development
split, and touch the test set once.

**Comparing against an untuned baseline.** Your system has had six months of your
attention; the baseline was installed from a package manager with its defaults. The
comparison is real, but effort is a factor and it was not held fixed, which makes it
a confound with exactly the structure of the machine column above. It is tempting
because tuning somebody else's system is unrewarding work that can only shrink your
result, and because there is no bright line saying when the baseline is tuned enough.
Reporting what tuning each side received is not a fix, but it lets a reader apply
their own discount.

## Where this stops holding

The sample-size formula assumes independent observations of roughly equal spread, and
a mean whose distribution is near enough normal. Benchmark timings break the first
two routinely: consecutive runs share a warm cache and are correlated, and a tail of
slow runs makes the spread of one system larger than the other. Treat the $n$ it
gives as a floor rather than a target, and use it before the study, where a rough
$\sigma$ from a pilot is all it needs.

Confound detection has a harder limit: it can only see the columns you recorded. If
the Tuesday runs were also the runs on a machine whose fan was failing, and nobody
wrote down the date, no analysis recovers it. Randomising the run order is the defence
against the factors you did not think of, and it is the one design decision that
protects against unknowns rather than known ones.

The lab for this module, **an experiment-design audit**, builds all of it:
`full_factorial`, `missing_cells`, `is_balanced`, `confounded_pairs`, `z_quantile`,
`min_detectable_effect`, `runs_needed`, and an `audit_design` that reports on the
eight broken runs above.
''',
                },
            ],
            "quiz": {
                "title": "Designs that can and cannot answer the question",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Every run with the new allocator used machine B and every run with the old one used machine A. Which of these repairs the study?",
                        "opts": [
                            "Running each allocator on both machines, so the two columns stop agreeing",
                            "Collecting many more runs on the same schedule, until the interval is tight",
                            "Reporting the machine alongside the result, so a reader can judge the effect",
                            "Discarding the machine column, since it was never a factor of interest",
                        ],
                        "a": 0,
                        "whys": [
                            "Crossing the two factors is the whole repair: once both allocators appear on both machines, the allocator effect can be estimated with the machine varying underneath it.",
                            "More runs shrink the interval around a quantity that is still the allocator and the machine added together. A precise estimate of an uninterpretable number is the worse outcome, not the better one.",
                            "Disclosure lets a reader distrust the number, which is worth something, but it does not let anyone recover the allocator effect. The information is absent from the data, not from the write-up.",
                            "Dropping the column changes the analysis and not the runs. The machine still varied with the allocator; deleting the record of it only hides that it did.",
                        ],
                        "why": r"""
Confounding is a property of which runs were performed, so it is repaired by
performing different runs. Once each allocator appears on both machines, the two
columns partition the runs differently and the allocator effect has somewhere to
show up that the machine effect does not. Notice that nothing about the analysis
fixes it: the data from the broken schedule contain one difference, 10.2 ms, and no
estimator can split one number into two.
""",
                    },
                    {
                        "q": "A study runs entirely on one machine. Should the confound detector report `machine` as confounded with `allocator`?",
                        "opts": [
                            "No — a factor with one level is a constant, and its effect is missing not tangled",
                            "Yes — every allocator run shares that machine, which is exactly what confounding means",
                            "Yes, but only when the machine is named in the write-up as a factor of the design",
                            "No — a machine is hardware rather than a treatment, so it cannot confound anything",
                        ],
                        "a": 0,
                        "whys": [
                            "Both directions of the test have to hold, and one of them fails trivially: the single machine level maps to every allocator, so it determines nothing about which allocator ran.",
                            "The forward direction does hold, which is why the guard is needed. The reverse fails: knowing the machine tells you nothing about the allocator when there is only one machine.",
                            "Whether something is named in a write-up cannot change what the data can distinguish. The detector works on the recorded levels, and one level is one level.",
                            "Hardware confounds results constantly — the broken study in the reading is exactly that. What saves this case is the single level, not the kind of thing the factor is.",
                        ],
                        "why": r"""
The guard `len(forward) < 2 or len(backward) < 2` exists for this case. A constant
column carries no partition of the runs, so it cannot be a relabelling of another
column, and reporting it as confounded would flag every study that fixed anything.
The real cost of a constant factor is different and worth naming: the result is
measured on that one machine only, which is a limit on scope rather than a
confounding of effects, and it belongs in the write-up as such.
""",
                    },
                    {
                        "q": "A design with 5 runs per group can detect a 7.1 ms difference. About how many runs per group would it take to detect 3.5 ms?",
                        "opts": [
                            "About 20, because the detectable difference falls as one over the square root of n",
                            "About 10, because halving the difference means doubling the number of runs",
                            "About 40, because the detectable difference falls as one over the fourth root of n",
                            "It cannot be worked out without knowing how large the true difference actually is",
                        ],
                        "a": 0,
                        "whys": [
                            "Since the detectable difference scales with the square root of two over n, quartering it means sixteen times the runs and halving it means four times: five becomes twenty.",
                            "This reads the relationship as linear in n. It is linear in the square root of n, so doubling the runs buys only a factor of 1.41, taking 7.1 ms down to about 5.0.",
                            "A fourth-root law would make runs even more expensive than they are, demanding forty for a factor of two. The standard error of a mean falls as the square root, and this inherits that.",
                            "The true difference is what the study is trying to find out. The detectable difference depends on the spread, the significance level and the power, none of which need it.",
                        ],
                        "why": r"""
The formula is $\delta = (z_{1-\alpha/2} + z_{1-\beta})\,\sigma\sqrt{2/n}$, and the
only place $n$ appears is under a square root. Halving $\delta$ therefore needs four
times the runs, so 5 becomes 20 and the printed table confirms it: 7.09 ms at five
runs and 3.54 ms at twenty, a ratio of exactly two. This is the fact that makes
sample size a decision rather than a habit — reaching 2 ms from 4 ms of spread takes
63 runs a side, and nobody discovers that comfortably after the study is over.
""",
                    },
                    {
                        "q": "You evaluate eleven parameter settings on the held-out test set and report the best. Why is that number optimistic?",
                        "opts": [
                            "The maximum of eleven noisy estimates sits above the average of what they estimate",
                            "Eleven evaluations wear out a fixed test set, so its labels become progressively less accurate",
                            "The best setting is likely to be one of the extreme values of the parameter grid",
                            "Each evaluation is unbiased, so the number is fine; the eleven p-values are the problem",
                        ],
                        "a": 0,
                        "whys": [
                            "Selection is the bias. Every individual estimate was honest, and taking the largest of them systematically overshoots, by more the noisier they are and the more of them there were.",
                            "Nothing about evaluating a set degrades it; the labels are exactly what they were. What degrades is the meaning of a number chosen after the set was consulted eleven times.",
                            "Where in the grid the winner sits is a fact about the parameter, not about the bias. The same overshoot happens with eleven settings that are all equally good.",
                            "The p-values would indeed need correcting, and module 4 does that. But the reported performance is biased upwards before any p-value is computed, by the act of taking a maximum.",
                        ],
                        "why": r"""
Take eleven settings that are genuinely identical in quality. Each measurement is
that quality plus noise, so the largest of the eleven is the quality plus the largest
of eleven noise draws, which is positive on average and grows with the number of
settings tried. Reporting it as the performance of the winning setting reports the
noise as if it were skill. The defence is procedural rather than statistical: choose
on a development split, and evaluate the chosen thing on the test set once.
""",
                    },
                    {
                        "q": "Why is comparing your tuned system against an out-of-the-box baseline described as a confound rather than merely as bad manners?",
                        "opts": [
                            "Effort is a factor of the design, and it varied together with the system being measured",
                            "The baseline authors did not consent to the comparison, so the result cannot be published",
                            "Default settings are chosen to be slow, so any baseline left at defaults is unrepresentative",
                            "It is only a confound when the baseline and your system are run on different machines",
                        ],
                        "a": 0,
                        "whys": [
                            "Tuning effort has levels — six months and none — and those levels line up perfectly with the system column, which is the same structure as the machine column in the broken study.",
                            "Consent is not what makes a comparison informative. A baseline nobody objected to, left at its defaults, produces exactly the same uninterpretable difference.",
                            "Defaults are usually chosen to be safe across many workloads rather than deliberately slow, and a well-chosen default can be hard to beat. The problem is the imbalance of attention, not the values.",
                            "Different machines are a second confound and an independent one. Running both systems on the same machine leaves the effort column exactly as tangled as it was.",
                        ],
                        "why": r"""
Write the design out with effort as a column and it looks precisely like the machine
column: `tuned` on every run of your system, `default` on every run of the baseline,
one partition of the runs written down twice. The measured difference is your idea
plus six months of attention, and the data cannot say how much of it is which. It is
worth adding that the repair is genuinely expensive here, which is why the honest
minimum is to report the tuning each side received and let the reader discount the
result themselves.
""",
                    },
                    {
                        "q": "A full factorial over three two-level factors has eight cells, and one cell was never run. What is lost?",
                        "opts": [
                            "The effect of each factor is still estimable, but that combination's interaction is not",
                            "Nothing, provided the remaining seven cells each have the same number of runs",
                            "The whole design collapses, because the three factors are now confounded with each other",
                            "Only the precision of the estimates, which the missing runs would have improved",
                        ],
                        "a": 0,
                        "whys": [
                            "Each factor still varies against the others across the seven surviving cells, so its main effect survives; what has no observation at all is how the three levels behave together in that one corner.",
                            "Equal replication across seven cells makes the design tidy, not complete. A cell with no runs contributes no information about itself however evenly the others are filled.",
                            "Confounding needs two columns to agree everywhere, and dropping one cell out of eight leaves both factors varying against each other in the rest of the design.",
                            "Precision is part of it, since seven cells is fewer runs than eight, but the specific loss is a quantity with no observations behind it rather than a noisier version of one.",
                        ],
                        "why": r"""
A missing cell is a combination of levels that was never observed, so anything
specific to that combination has to be assumed rather than measured — usually by
assuming the factors act additively, which is the assumption an interaction term
exists to test. The main effects survive because each factor still changes level
against the others somewhere in the remaining seven cells. This is why
`missing_cells` in the lab returns the cells rather than a count: which corner is
missing determines what you are no longer allowed to say.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Confounds and sample size, five holes deep",
                "minutes": 9,
                "lang": "python",
                "caption": "design.py — the two-directional confound test, and the two sample-size formulas",
                "brief": r'''
Two small functions carry the whole module. The first decides whether two columns of
the design are the same column written twice; the second decides how many runs the
question needs. Each hole below is a place where a plausible alternative changes the
answer without changing whether the code runs.

Nothing is executed here. Filled in correctly, the eight broken runs report the
allocator confounded with the machine and nothing else, and 4.0 ms of spread needs 63
runs a side to detect a 2.0 ms difference.
''',
                "listing": r'''
def confounded(runs, a, b):
    """True when the level of a determines the level of b, and the reverse."""
    forward, backward = {}, {}
    for run in runs:
        forward.setdefault(run[a], set()).add(run[b])
        backward.setdefault(run[b], set()).add(run[a])
    if len(forward) < ___ or len(backward) < 2:
        return False
    return (all(len(seen) == ___ for seen in forward.values())
            and all(len(seen) == 1 for seen in backward.values()))


def min_detectable_effect(sd, n, alpha=0.05, power=0.80):
    """The smallest true difference this design would detect, with that power."""
    z = z_quantile(___) + z_quantile(power)
    return z * sd * math.sqrt(___)


def runs_needed(sd, delta, alpha=0.05, power=0.80):
    """The smallest n per group whose detectable effect is at most delta."""
    z = z_quantile(1 - alpha / 2) + z_quantile(power)
    return math.ceil(2 * (sd * z / delta) ** ___)
''',
                "blanks": [
                    {
                        "prompt": "How many distinct levels must a factor have before confounding is even a question?",
                        "hole": "?",
                        "opts": ["2", "1", "0", "len(runs)"],
                        "a": 0,
                        "why": "A column with one level partitions nothing, so it cannot be a relabelling of another column. Without this guard, a study run on a single machine reports that machine as confounded with every factor in the design.",
                        "whys": [
                            "A column with one level partitions nothing, so it cannot be a relabelling of another column. Without this guard, a study run on a single machine reports that machine as confounded with every factor in the design.",
                            "Every non-empty column has at least one level, so this guard never fires and the constant-factor case walks straight through into a false report.",
                            "A column with no levels at all only happens when there are no runs, so this catches an empty study and nothing else. Every real design passes it.",
                            "This demands as many levels as there are runs, which is true only when every run had its own unique setting. Ordinary two-level factors would be dismissed as unconfoundable.",
                        ],
                    },
                    {
                        "prompt": "Each level of a maps to a set of levels of b. How large may that set be if a determines b?",
                        "hole": "?",
                        "opts": ["1", "2", "0", "len(backward)"],
                        "a": 0,
                        "why": "Determining means exactly one: if a level of the allocator were seen with two machines, knowing the allocator would leave the machine open, and the two columns would no longer agree.",
                        "whys": [
                            "Determining means exactly one: if a level of the allocator were seen with two machines, knowing the allocator would leave the machine open, and the two columns would no longer agree.",
                            "Requiring exactly two turns the test upside down: a properly crossed design, where each allocator is seen on both machines, would be reported as the confounded one.",
                            "A set built by adding one element per run is never empty, so the test is false everywhere and no pair is ever reported, however tangled the design.",
                            "Comparing against the number of levels of b makes the test true only when one level of a was seen with all of them, which is the definition of a crossed design rather than a confounded one.",
                        ],
                    },
                    {
                        "prompt": "The significance threshold is two-sided at alpha. Which quantile does that need?",
                        "hole": "?",
                        "opts": ["1 - alpha / 2", "1 - alpha", "alpha / 2", "1 - power / 2"],
                        "a": 0,
                        "why": "A two-sided test spends alpha across both tails, so each tail gets alpha over two and the critical value is the quantile at 1 minus that. At alpha 0.05 it is the familiar 1.96.",
                        "whys": [
                            "A two-sided test spends alpha across both tails, so each tail gets alpha over two and the critical value is the quantile at 1 minus that. At alpha 0.05 it is the familiar 1.96.",
                            "This is the one-sided critical value, 1.645 at alpha 0.05. Using it in a two-sided test understates the threshold and reports a smaller detectable effect than the design can actually deliver.",
                            "This is the quantile in the lower tail, about -1.96, and adding a negative number to the power term shrinks the sum instead of building it. The detectable effect comes out far too small.",
                            "Power is not split across two tails — the whole of it belongs to the second term of the sum — so this halves the wrong quantity and puts the significance threshold at a quantile of about 0.25.",
                        ],
                    },
                    {
                        "prompt": "What goes under the square root, given the standard error of a difference of two means of size n?",
                        "hole": "?",
                        "opts": ["2 / n", "1 / n", "n / 2", "2 * n"],
                        "a": 0,
                        "why": "Each mean carries variance sigma squared over n, and the two groups are independent, so the variances add: the difference carries two sigma squared over n, and its standard error is sigma times the root of two over n.",
                        "whys": [
                            "Each mean carries variance sigma squared over n, and the two groups are independent, so the variances add: the difference carries two sigma squared over n, and its standard error is sigma times the root of two over n.",
                            "This is the standard error of a single mean. Using it forgets that the quantity being tested is a difference, and it understates the noise by a factor of about 1.41 for every design.",
                            "This grows with n instead of shrinking, so more runs would make the study less able to detect anything — at 63 runs a side it claims a detectable effect of about 63 ms rather than 2 ms.",
                            "This also grows with n, and faster. Both inverted forms are caught by the same sanity check: the detectable difference has to fall as the study gets bigger.",
                        ],
                    },
                    {
                        "prompt": "Solving the detectable-effect formula for n squares which side?",
                        "hole": "?",
                        "opts": ["2", "1", "0.5", "3"],
                        "a": 0,
                        "why": "The formula has n under a square root, so isolating n squares everything else. That squaring is the reason halving the detectable difference costs four times the runs.",
                        "whys": [
                            "The formula has n under a square root, so isolating n squares everything else. That squaring is the reason halving the detectable difference costs four times the runs.",
                            "Leaving the expression to the first power inverts a square root that is still there, giving about 11 runs where 63 are needed, and a study that quietly cannot detect what it was sized for.",
                            "Taking a square root here goes the wrong way twice over, and returns about 4 runs for a design needing 63. The exponent has to undo a root, not apply another one.",
                            "Cubing has no derivation behind it, and it inflates the answer enormously: a design needing 63 runs a side would be told to perform roughly 350.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "An experiment-design audit",
                "minutes": 50,
                "runtime": "python",
                "brief": r'''
Given a set of factors and the runs that were actually performed, say what the
design can and cannot answer. `main.py` already holds `FACTORS`, the eight
`BROKEN` runs from the reading, and a `REPAIRED` schedule that crosses them
properly.

1. `full_factorial(factors)` — `factors` maps a name to its list of levels.
   Return one dict per cell, in `itertools.product` order, so the **last**
   factor varies fastest. An empty `factors`, or any factor with no levels, is
   a `ValueError`.

2. `missing_cells(factors, runs)` — the cells of the full factorial that no run
   matches, in factorial order. A run matches a cell when it agrees on every
   factor name.

3. `is_balanced(factors, runs)` — `True` when every cell holds the same number
   of runs and that number is at least one.

4. `confounded_pairs(runs)` — every pair `(a, b)` with `a < b` whose levels
   determine each other in both directions, sorted. A factor with fewer than
   two distinct levels is in no pair. Empty `runs`, or runs whose key sets
   differ from each other, is a `ValueError`.

5. `z_quantile(p)` — the inverse standard normal, by bisection on `math.erf`
   over the bracket `[-12, 12]`. `p` outside the open interval `(0, 1)` is a
   `ValueError`.

6. `min_detectable_effect(sd, n, alpha=0.05, power=0.80)` — the formula from
   the reading. A non-positive `sd` or `n` is a `ValueError`.

7. `runs_needed(sd, delta, alpha=0.05, power=0.80)` — the smallest whole `n`
   per group whose detectable effect is at most `delta`.

8. `audit_design(factors, runs, sd, delta)` — a report:

```text
{"cells": 8, "runs": 8, "replication": 0,
 "missing": [ ...the four cells nobody ran... ],
 "balanced": False,
 "confounded": [("allocator", "machine")],
 "mde": None,
 "runs_needed": 63}
```

`replication` is the number of runs in the emptiest cell, `mde` is
`min_detectable_effect(sd, replication)` or `None` when that is zero, and
`runs_needed` uses `sd` and `delta`. Run the audit on `BROKEN` and on
`REPAIRED` and read the difference between the two reports.
''',
                "hints": [
                    "`itertools.product(*factors.values())` zipped back against `factors` gives the cells in the required order in one line.",
                    "For `missing_cells`, build a set of tuples of the factor values of each run and test each cell's tuple against it — dicts are not hashable.",
                    "`confounded_pairs` is the reading's `confounded` applied to every pair from `sorted(keys)`; keep the two-level guard or a constant factor pairs with everything.",
                    "Bisection on `0.5 * (1 + math.erf(z / math.sqrt(2)))` converges to twelve digits in about 50 halvings of [-12, 12]; 200 is free and leaves no doubt.",
                    "`runs_needed` has a closed form, `ceil(2 * (sd * z / delta) ** 2)`, and no loop is needed. Check it against `min_detectable_effect` at n and at n - 1.",
                ],
                "files": [{"name": "main.py", "content": r'''
import math
from itertools import product

FACTORS = {
    "allocator": ["system", "custom"],
    "machine": ["A", "B"],
    "workload": ["json", "regex"],
}

BROKEN = [
    {"allocator": "system", "machine": "A", "workload": "json"},
    {"allocator": "system", "machine": "A", "workload": "regex"},
    {"allocator": "system", "machine": "A", "workload": "json"},
    {"allocator": "system", "machine": "A", "workload": "regex"},
    {"allocator": "custom", "machine": "B", "workload": "json"},
    {"allocator": "custom", "machine": "B", "workload": "regex"},
    {"allocator": "custom", "machine": "B", "workload": "json"},
    {"allocator": "custom", "machine": "B", "workload": "regex"},
]

REPAIRED = [
    {"allocator": "system", "machine": "A", "workload": "json"},
    {"allocator": "system", "machine": "A", "workload": "regex"},
    {"allocator": "system", "machine": "B", "workload": "json"},
    {"allocator": "system", "machine": "B", "workload": "regex"},
    {"allocator": "custom", "machine": "A", "workload": "json"},
    {"allocator": "custom", "machine": "A", "workload": "regex"},
    {"allocator": "custom", "machine": "B", "workload": "json"},
    {"allocator": "custom", "machine": "B", "workload": "regex"},
]


def full_factorial(factors):
    """One dict per cell, last factor varying fastest."""
    # your code here


def missing_cells(factors, runs):
    """The cells nobody ran, in factorial order."""
    # your code here


def is_balanced(factors, runs):
    """True when every cell holds the same non-zero number of runs."""
    # your code here


def confounded_pairs(runs):
    """Sorted (a, b) pairs whose levels determine each other both ways."""
    # your code here


def z_quantile(p):
    """The inverse standard normal, by bisection on erf."""
    # your code here


def min_detectable_effect(sd, n, alpha=0.05, power=0.80):
    """The smallest true difference this design would detect."""
    # your code here


def runs_needed(sd, delta, alpha=0.05, power=0.80):
    """The smallest n per group whose detectable effect is at most delta."""
    # your code here


def audit_design(factors, runs, sd, delta):
    """What this design can and cannot answer."""
    # your code here


if __name__ == "__main__":
    for label, schedule in (("broken", BROKEN), ("repaired", REPAIRED)):
        report = audit_design(FACTORS, schedule, 4.0, 2.0)
        if report:
            print(label, report["confounded"], "missing", len(report["missing"]),
                  "balanced", report["balanced"])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
from itertools import product

FACTORS = {
    "allocator": ["system", "custom"],
    "machine": ["A", "B"],
    "workload": ["json", "regex"],
}

BROKEN = [
    {"allocator": "system", "machine": "A", "workload": "json"},
    {"allocator": "system", "machine": "A", "workload": "regex"},
    {"allocator": "system", "machine": "A", "workload": "json"},
    {"allocator": "system", "machine": "A", "workload": "regex"},
    {"allocator": "custom", "machine": "B", "workload": "json"},
    {"allocator": "custom", "machine": "B", "workload": "regex"},
    {"allocator": "custom", "machine": "B", "workload": "json"},
    {"allocator": "custom", "machine": "B", "workload": "regex"},
]

REPAIRED = [
    {"allocator": "system", "machine": "A", "workload": "json"},
    {"allocator": "system", "machine": "A", "workload": "regex"},
    {"allocator": "system", "machine": "B", "workload": "json"},
    {"allocator": "system", "machine": "B", "workload": "regex"},
    {"allocator": "custom", "machine": "A", "workload": "json"},
    {"allocator": "custom", "machine": "A", "workload": "regex"},
    {"allocator": "custom", "machine": "B", "workload": "json"},
    {"allocator": "custom", "machine": "B", "workload": "regex"},
]


def full_factorial(factors):
    """One dict per cell, last factor varying fastest."""
    if not factors:
        raise ValueError("a design with no factors has no cells")
    for name, levels in factors.items():
        if not levels:
            raise ValueError(f"factor {name!r} has no levels")
    names = list(factors)
    return [dict(zip(names, combo)) for combo in product(*factors.values())]


def missing_cells(factors, runs):
    """The cells nobody ran, in factorial order."""
    names = list(factors)
    seen = {tuple(run[name] for name in names) for run in runs}
    return [cell for cell in full_factorial(factors)
            if tuple(cell[name] for name in names) not in seen]


def is_balanced(factors, runs):
    """True when every cell holds the same non-zero number of runs."""
    names = list(factors)
    counts = []
    for cell in full_factorial(factors):
        key = tuple(cell[name] for name in names)
        counts.append(sum(1 for run in runs
                          if tuple(run[name] for name in names) == key))
    return bool(counts) and min(counts) > 0 and len(set(counts)) == 1


def confounded_pairs(runs):
    """Sorted (a, b) pairs whose levels determine each other both ways."""
    if not runs:
        raise ValueError("no runs to audit")
    names = sorted(runs[0])
    for run in runs:
        if sorted(run) != names:
            raise ValueError("every run must record the same factors")
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            forward, backward = {}, {}
            for run in runs:
                forward.setdefault(run[a], set()).add(run[b])
                backward.setdefault(run[b], set()).add(run[a])
            if len(forward) < 2 or len(backward) < 2:
                continue
            if (all(len(seen) == 1 for seen in forward.values())
                    and all(len(seen) == 1 for seen in backward.values())):
                pairs.append((a, b))
    return sorted(pairs)


def z_quantile(p):
    """The inverse standard normal, by bisection on erf."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must lie strictly between 0 and 1")
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def min_detectable_effect(sd, n, alpha=0.05, power=0.80):
    """The smallest true difference this design would detect."""
    if sd <= 0 or n <= 0:
        raise ValueError("a spread and a group size must both be positive")
    z = z_quantile(1 - alpha / 2) + z_quantile(power)
    return z * sd * math.sqrt(2 / n)


def runs_needed(sd, delta, alpha=0.05, power=0.80):
    """The smallest n per group whose detectable effect is at most delta."""
    if sd <= 0 or delta <= 0:
        raise ValueError("a spread and a target effect must both be positive")
    z = z_quantile(1 - alpha / 2) + z_quantile(power)
    return math.ceil(2 * (sd * z / delta) ** 2)


def audit_design(factors, runs, sd, delta):
    """What this design can and cannot answer."""
    names = list(factors)
    cells = full_factorial(factors)
    counts = []
    for cell in cells:
        key = tuple(cell[name] for name in names)
        counts.append(sum(1 for run in runs
                          if tuple(run[name] for name in names) == key))
    replication = min(counts) if counts else 0
    return {
        "cells": len(cells),
        "runs": len(runs),
        "replication": replication,
        "missing": missing_cells(factors, runs),
        "balanced": is_balanced(factors, runs),
        "confounded": confounded_pairs(runs),
        "mde": min_detectable_effect(sd, replication) if replication else None,
        "runs_needed": runs_needed(sd, delta),
    }


if __name__ == "__main__":
    for label, schedule in (("broken", BROKEN), ("repaired", REPAIRED)):
        report = audit_design(FACTORS, schedule, 4.0, 2.0)
        if report:
            print(label, report["confounded"], "missing", len(report["missing"]),
                  "balanced", report["balanced"])
'''}],
                "tests": [
                    {"name": "full_factorial crosses the levels, last factor fastest", "code": r'''
_cells = full_factorial(FACTORS)
assert len(_cells) == 8, f"2 x 2 x 2 is 8 cells, got {len(_cells)}"
assert _cells[0] == {"allocator": "system", "machine": "A", "workload": "json"}, f"got {_cells[0]!r}"
assert _cells[1] == {"allocator": "system", "machine": "A", "workload": "regex"}, \
    f"the last factor varies fastest; got {_cells[1]!r}"
assert _cells[-1] == {"allocator": "custom", "machine": "B", "workload": "regex"}, f"got {_cells[-1]!r}"
for _bad in ({}, {"machine": []}, {"a": ["x"], "b": []}):
    try:
        full_factorial(_bad)
        assert False, f"full_factorial({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "missing_cells names the corners nobody ran", "code": r'''
assert missing_cells(FACTORS, REPAIRED) == [], "the repaired schedule covers every cell"
_gap = missing_cells(FACTORS, REPAIRED[:-1])
assert _gap == [{"allocator": "custom", "machine": "B", "workload": "regex"}], f"got {_gap!r}"
_broken_gap = missing_cells(FACTORS, BROKEN)
assert len(_broken_gap) == 4, f"the broken schedule visits only 4 of the 8 cells, got {8 - len(_broken_gap)}"
assert {c["allocator"] for c in _broken_gap} == {"system", "custom"}, \
    "the unrun cells are the ones pairing each allocator with the other machine"
'''},
                    {"name": "is_balanced wants every cell filled equally", "code": r'''
assert is_balanced(FACTORS, REPAIRED), "one run in each of the eight cells is balanced"
assert is_balanced(FACTORS, REPAIRED + REPAIRED), "two runs in each cell is balanced too"
assert not is_balanced(FACTORS, BROKEN), "four empty cells cannot be balanced"
assert not is_balanced(FACTORS, REPAIRED + REPAIRED[:1]), \
    "one cell with two runs and the rest with one is not balanced"
assert not is_balanced(FACTORS, []), "a design with no runs at all is not balanced"
'''},
                    {"name": "confounded_pairs finds the machine column and only that", "code": r'''
assert confounded_pairs(BROKEN) == [("allocator", "machine")], \
    f"got {confounded_pairs(BROKEN)!r}"
assert confounded_pairs(REPAIRED) == [], \
    f"the repaired schedule crosses every factor; got {confounded_pairs(REPAIRED)!r}"
_pairs = confounded_pairs([{"a": 1, "b": "x", "c": "p"}, {"a": 1, "b": "x", "c": "q"},
                           {"a": 2, "b": "y", "c": "p"}, {"a": 2, "b": "y", "c": "q"}])
assert _pairs == [("a", "b")], f"got {_pairs!r}"
'''},
                    {"name": "A constant factor is in no pair, and ragged runs are refused", "code": r'''
_one_machine = [dict(run, machine="A") for run in REPAIRED]
assert confounded_pairs(_one_machine) == [], \
    "a factor with one level partitions nothing, so it is confounded with nothing"
try:
    confounded_pairs([])
    assert False, "an empty schedule should raise ValueError"
except ValueError:
    pass
try:
    confounded_pairs([{"a": 1, "b": 2}, {"a": 1}])
    assert False, "runs recording different factors should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "z_quantile inverts the normal, and refuses impossible p", "code": r'''
assert abs(z_quantile(0.975) - 1.959964) < 1e-5, f"got {z_quantile(0.975)!r}"
assert abs(z_quantile(0.80) - 0.841621) < 1e-5, f"got {z_quantile(0.80)!r}"
assert abs(z_quantile(0.5)) < 1e-9, f"the median of a standard normal is 0, got {z_quantile(0.5)!r}"
for _p in (0.01, 0.3, 0.9):
    assert abs(z_quantile(_p) + z_quantile(1 - _p)) < 1e-9, f"symmetry fails at p={_p}"
for _bad in (0.0, 1.0, -0.5, 2.0):
    try:
        z_quantile(_bad)
        assert False, f"z_quantile({_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "min_detectable_effect matches the reading and falls as one over root n", "code": r'''
assert abs(min_detectable_effect(4.0, 5) - 7.0875) < 1e-3, f"got {min_detectable_effect(4.0, 5)!r}"
assert abs(min_detectable_effect(4.0, 20) - 3.5437) < 1e-3, f"got {min_detectable_effect(4.0, 20)!r}"
assert abs(min_detectable_effect(4.0, 5) / min_detectable_effect(4.0, 20) - 2.0) < 1e-9, \
    "four times the runs must halve the detectable difference, exactly"
assert abs(min_detectable_effect(8.0, 5) / min_detectable_effect(4.0, 5) - 2.0) < 1e-9, \
    "the detectable difference is proportional to the spread"
for _bad in ((0.0, 5), (-1.0, 5), (4.0, 0)):
    try:
        min_detectable_effect(*_bad)
        assert False, f"min_detectable_effect{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "runs_needed is the smallest n that reaches the target", "code": r'''
_n = runs_needed(4.0, 2.0)
assert _n == 63, f"4.0 ms of spread needs 63 runs a side to detect 2.0 ms, got {_n!r}"
assert min_detectable_effect(4.0, _n) <= 2.0, "n must actually reach the target"
assert min_detectable_effect(4.0, _n - 1) > 2.0, "and n - 1 must not, or it is not the smallest"
assert runs_needed(4.0, 4.0) == 16, f"a target equal to the spread needs 16, got {runs_needed(4.0, 4.0)!r}"
assert runs_needed(8.0, 2.0) == 4 * 63 - 1 or runs_needed(8.0, 2.0) == 4 * 63, \
    f"doubling the spread quadruples the runs, got {runs_needed(8.0, 2.0)!r}"
'''},
                    {"name": "audit_design reports the broken schedule for what it is", "code": r'''
_report = audit_design(FACTORS, BROKEN, 4.0, 2.0)
assert _report["cells"] == 8 and _report["runs"] == 8, f"got {_report['cells']!r}, {_report['runs']!r}"
assert _report["replication"] == 0, "the emptiest cell holds no runs at all"
assert _report["mde"] is None, "with an empty cell there is no detectable effect to quote"
assert _report["balanced"] is False and len(_report["missing"]) == 4, f"got {_report!r}"
assert _report["confounded"] == [("allocator", "machine")], f"got {_report['confounded']!r}"
assert _report["runs_needed"] == 63, f"got {_report['runs_needed']!r}"
_fixed = audit_design(FACTORS, REPAIRED, 4.0, 2.0)
assert _fixed["confounded"] == [] and _fixed["missing"] == [] and _fixed["balanced"] is True
assert _fixed["replication"] == 1 and abs(_fixed["mde"] - min_detectable_effect(4.0, 1)) < 1e-12
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Statistics for benchmarks",
            "summary": "Warm-up, skew, and putting a bootstrap interval on a speedup instead of a mean on three runs.",
            "concepts": [
                "A timing sample has a hard floor and a long right tail, so its mean is not its centre",
                "The first runs measure the cache, the allocator and any ahead-of-time work — declare the warm-up, never hide it",
                "Whether the warm-up belongs in the report is decided by the question, not by the statistics",
                "The bootstrap of MA201 gives an interval for a median, where no closed form exists",
                "A speedup is a ratio, so its interval is bootstrapped on the ratio, not assembled from two separate intervals",
                "An interval that straddles $1$ means the experiment did not resolve the direction, not that the systems are equal",
                "The bootstrap needs a statistic smooth in the data, which rules out the minimum — the very statistic benchmarking folklore recommends",
            ],
            "read": [
                {
                    "title": "The first run measured the compiler",
                    "minutes": 15,
                    "body": r'''
Twelve runs of a log-ingestion benchmark, in the order they were taken, in
milliseconds. `base` is the standard library matcher; `opt` compiles each pattern to
a DFA before it starts.

```text
base  44.1  42.0  41.6  40.9  41.2  41.0  41.5  40.8  41.3  47.9  41.1  41.4
opt   96.4  51.2  37.6  37.2  37.9  37.4  37.1  37.8  43.6  37.3  37.5  37.0
```

The report everybody writes first is a mean of the first three runs, because three
runs is what fits in the time available and a mean is what a benchmark reports. It
comes to 42.57 ms for `base` and 61.73 ms for `opt`. The optimisation is a
31 per cent regression, the afternoon has been wasted, and the number is wrong.

Extend it to all twelve and the picture improves without becoming right: 42.07 ms
against 44.00 ms, still a regression, now of 4.6 per cent. Two summaries of the same
data disagree by a factor of six, and neither carries anything that would let a
reader see that.

## What the numbers are actually shaped like

Sort each row and the structure is immediate.

```text
base  40.8 40.9 41.0 41.1 41.2 41.3 41.4 41.5 41.6 42.0 44.1 47.9
opt   37.0 37.1 37.2 37.3 37.4 37.5 37.6 37.8 37.9 43.6 51.2 96.4
```

Neither sample is symmetric, and they cannot be. A run cannot take less time than the
work requires, so there is a hard floor; there is no ceiling at all, because anything
that interrupts a run adds to it. Every timing distribution has that shape — a wall
on the left, a tail on the right — which means the mean sits above the bulk of the
data and moves whenever a straggler does. The 96.4 alone pulls the `opt` mean up by
nearly 5 ms.

That is enough to condemn the mean of three runs, and worth being precise about why.
The problem is not that three is a small number. It is that the mean of a
right-skewed sample is not estimating the thing the reader thinks it is, and with no
spread reported there is nothing on the page that would reveal it.

## The stragglers are two different things

Look at where they sit in time rather than in sorted order. `opt`'s 96.4 and 51.2 are
runs 1 and 2. `base`'s 44.1 and 42.0 are runs 1 and 2 as well. They are the warm-up:
the file is not in the page cache, the allocator has not reached a steady state, and
`opt` additionally builds its DFA on the first call. Those are not noise; they are the
cost of starting, and they are entirely predictable from the position in the sequence.

`base`'s 47.9 is run 10 and `opt`'s 43.6 is run 9. Nothing distinguishes them by
position. Something interrupted the machine, and it will interrupt a user's machine
too. Those belong in the sample.

So the rule the module runs on: **discard a declared number of leading runs, and keep
everything else.** Declared, because `warmup=2` is a decision a reader has to be able
to disagree with, and because a study that removes runs it did not name in advance
has removed whichever runs made the result worse.

```python
BASE = [44.1, 42.0, 41.6, 40.9, 41.2, 41.0, 41.5, 40.8, 41.3, 47.9, 41.1, 41.4]
OPT = [96.4, 51.2, 37.6, 37.2, 37.9, 37.4, 37.1, 37.8, 43.6, 37.3, 37.5, 37.0]


def mean(xs):
    return sum(xs) / len(xs)


def percentile(xs, q):
    ys = sorted(xs)
    position = q * (len(ys) - 1)
    low = int(position)
    high = min(low + 1, len(ys) - 1)
    return ys[low] * (1 - (position - low)) + ys[high] * (position - low)


print(f"first three   base {mean(BASE[:3]):6.2f}  opt {mean(OPT[:3]):6.2f}"
      f"   speedup {mean(BASE[:3]) / mean(OPT[:3]):.4f}")
print(f"all twelve    base {mean(BASE):6.2f}  opt {mean(OPT):6.2f}"
      f"   speedup {mean(BASE) / mean(OPT):.4f}")
warm_base, warm_opt = BASE[2:], OPT[2:]
print(f"warm-up gone  base {mean(warm_base):6.2f}  opt {mean(warm_opt):6.2f}"
      f"   speedup {mean(warm_base) / mean(warm_opt):.4f}")
print(f"their medians base {percentile(warm_base, 0.5):6.2f}  "
      f"opt {percentile(warm_opt, 0.5):6.2f}"
      f"   speedup {percentile(warm_base, 0.5) / percentile(warm_opt, 0.5):.4f}")
```

```text
first three   base  42.57  opt  61.73   speedup 0.6895
all twelve    base  42.07  opt  44.00   speedup 0.9561
warm-up gone  base  41.87  opt  38.04   speedup 1.1007
their medians base  41.25  opt  37.45   speedup 1.1015
```

Two lines of policy — declare a warm-up, prefer the median — turn a 31 per cent
regression into a 10 per cent improvement. Which is why neither of them may be
chosen after seeing the answer.

## Putting an interval on it

A speedup of 1.1015 is one number from one sample, and the module 1 rule applies to
your own work as much as to anyone else's: without an uncertainty it is not citable.
There is no closed form for the standard error of a ratio of medians, so this is the
case MA201 built the bootstrap for. Resample each group with replacement to its own
size, recompute the statistic, and read the middle 95 per cent of what comes out.

The detail that matters is **what gets resampled**. The statistic is
$\hat{\theta} = \tilde{x}_{\text{base}} / \tilde{x}_{\text{opt}}$, a single number
computed from both samples, so each bootstrap trial must draw a new `base` sample
*and* a new `opt` sample and take their ratio. Bootstrapping the two medians
separately and then dividing the interval endpoints is a different, wrong calculation.

```python
import random

BASE = [41.6, 40.9, 41.2, 41.0, 41.5, 40.8, 41.3, 47.9, 41.1, 41.4]
OPT = [37.6, 37.2, 37.9, 37.4, 37.1, 37.8, 43.6, 37.3, 37.5, 37.0]


def percentile(xs, q):
    ys = sorted(xs)
    position = q * (len(ys) - 1)
    low = int(position)
    high = min(low + 1, len(ys) - 1)
    return ys[low] * (1 - (position - low)) + ys[high] * (position - low)


def median(xs):
    return percentile(xs, 0.5)


rng = random.Random(451)
ratios, base_medians, opt_medians = [], [], []
for _ in range(2000):
    rb = [rng.choice(BASE) for _ in BASE]
    ro = [rng.choice(OPT) for _ in OPT]
    ratios.append(median(rb) / median(ro))
    base_medians.append(median(rb))
    opt_medians.append(median(ro))

print(f"speedup            {median(BASE) / median(OPT):.4f}")
print(f"bootstrap on ratio [{percentile(ratios, 0.025):.4f}, "
      f"{percentile(ratios, 0.975):.4f}]")
print(f"base median CI     [{percentile(base_medians, 0.025):.4f}, "
      f"{percentile(base_medians, 0.975):.4f}]")
print(f"opt median CI      [{percentile(opt_medians, 0.025):.4f}, "
      f"{percentile(opt_medians, 0.975):.4f}]")
print(f"endpoints divided  [{percentile(base_medians, 0.025) / percentile(opt_medians, 0.975):.4f}, "
      f"{percentile(base_medians, 0.975) / percentile(opt_medians, 0.025):.4f}]")
```

```text
speedup            1.1015
bootstrap on ratio [1.0891, 1.1128]
base median CI     [41.0000, 41.5000]
opt median CI      [37.2000, 37.8000]
endpoints divided  [1.0847, 1.1156]
```

The interval to report is [1.089, 1.113]. The endpoints-divided version is wider at
both ends, and the reason is worth seeing: dividing the low end of one interval by
the high end of the other describes a world in which `base` was unusually fast at the
same moment `opt` was unusually slow. No single resample produces both, because a
resample is one draw of the whole experiment. The ratio has its own sampling
distribution, and that is the thing to take percentiles of.

The interval excludes 1.0, so the direction is resolved: on this corpus, on this
machine, the DFA version is faster, by somewhere between 8.9 and 11.3 per cent. Had
it come out as [0.988, 1.016] the honest sentence would be *this experiment did not
resolve the direction* — which is not the same sentence as *the two are equally
fast*, a claim the data would still not support.

## The mistakes

**A mean of three runs with no spread.** The whole of the first section. It is
tempting because a benchmark result feels like a measurement of the program rather
than a sample from a distribution, and a program does not have error bars.

**Deleting the outliers.** The 47.9 and the 43.6 are the most annoying numbers in the
sample and there is always a story available — another process, a background index,
a bad turn of the scheduler. Deleting them is tempting because it makes the interval
narrower and the result cleaner, and because the story is often true. It is still
wrong: the same interruptions happen to a user, so a study that removes them is
reporting a machine nobody has. Removing a *declared* warm-up prefix is a different
act, because the rule is stated before the data is seen and applies to both systems
alike.

**Reading a straddling interval as "no difference".** An interval containing 1.0 is
compatible with a 1 per cent win and with a 1 per cent loss. It says the study was
too small or too noisy to tell. Announcing equality from it turns an absence of
evidence into a finding, which is the single most common misreading in the whole
subject.

## Where this stops holding

The bootstrap resamples the data you have, so it estimates the uncertainty of running
*this benchmark on this machine* again. It cannot tell you what a different machine
would do; that is a scope question, and only a design that varied the machine answers
it.

It also needs a statistic that is smooth in the data, and MA201 named the exact
failure: the maximum, whose resamples can never exceed the largest observed value.
The same argument condemns the minimum, and the minimum is precisely what benchmarking
folklore tells you to report — *take the fastest run, it is the one with the least
interference*. That is a defensible estimand when what you want is the machine's
best-case throughput, but its bootstrap interval is not to be believed, because every
resample is bounded below by the one fastest run you happened to observe.

Finally, consecutive runs are not independent. Nothing above assumed they were, which
is one reason the bootstrap is a better fit here than a t interval, but a benchmark
whose runs drift steadily upwards over an afternoon is telling you about the machine
warming up, and no resampling scheme will notice.

The lab for this module, **a benchmark report with an interval on it**, builds
`drop_warmup`, `summarise`, `bootstrap`, `bootstrap_ci`, `speedup`, `speedup_ci`,
`resolved` and `report`, on the twelve runs above. `stats.py` arrives finished: the
mean, the sample variance and the interpolating `percentile` are MA201's, and this
module is about using them rather than rebuilding them.
''',
                },
            ],
            "quiz": {
                "title": "Reading a timing sample",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A paper reports a benchmark as the mean of three runs, with no spread. What is the strongest objection?",
                        "opts": [
                            "Nothing on the page shows whether the difference claimed exceeds the run-to-run noise",
                            "Three is below the sample size at which a mean becomes a valid estimator at all",
                            "The mean is the wrong estimator, and the median of three runs would be defensible",
                            "Three runs cannot be reproduced by a reader, who would need the original machine and OS",
                        ],
                        "a": 0,
                        "whys": [
                            "Without a spread there is nothing to compare the claimed difference against, so the reader cannot tell a real effect from a rearrangement of the noise.",
                            "A mean is a perfectly valid estimator of a mean at any sample size, including one. Small samples make it imprecise, and no threshold turns it valid.",
                            "Swapping the estimator helps with skew, and the reading recommends it, but a bare median of three runs is every bit as unreportable as a bare mean of three.",
                            "Reproduction on another machine is a separate and real concern, and it applies equally to a study reporting a hundred runs with full intervals.",
                        ],
                        "why": r"""
The missing spread is the defect, and it is missing whichever estimator is used. Give
the same three runs a spread and a reader can ask the module 2 question — could this
design have detected the effect it claims? — and answer it. The skew of timing data
is a second and smaller objection: it makes the mean estimate something other than
the centre, which is why the lab summarises with a median as well, but a median with
no interval beside it is no more citable than the mean was.
""",
                    },
                    {
                        "q": "Why is discarding the first two runs of each system defensible while discarding the slowest run is not?",
                        "opts": [
                            "The warm-up is identified by position and declared in advance; the slowest run by its value",
                            "The warm-up runs are always the two slowest, so removing them removes the outliers anyway",
                            "Two runs is a small enough fraction of twelve to be harmless, whereas one more would not be",
                            "Discarding by value is only a problem when the two systems have different numbers of runs",
                        ],
                        "a": 0,
                        "whys": [
                            "A rule stated before the data is seen cannot be tuned to the answer, and it applies to both systems alike; a rule that names the slowest run can only ever flatter the result.",
                            "They usually are among the slowest, but that is a consequence rather than the justification, and it is not always true — the base sample's slowest run is number 10.",
                            "The fraction removed is not what makes it legitimate. Removing a declared warm-up of six would be defensible; removing one run chosen by its value would not.",
                            "Unequal run counts are a separate nuisance. Selecting by value biases the result even when both systems have exactly the same number of runs.",
                        ],
                        "why": r"""
The distinction is when the rule was fixed. `warmup=2` is a statement about the
protocol that a reader can disagree with and that applies identically to both
systems; it does not consult the timings. Dropping the slowest run consults them, and
a rule whose input is the answer will always improve the answer. Notice that the
reading keeps the base sample's 47.9 ms — run 10, no warm-up excuse available — for
exactly this reason: it is an interruption that a user would also experience.
""",
                    },
                    {
                        "q": "In each bootstrap trial, why must the resample be the same size as the original sample?",
                        "opts": [
                            "The interval estimates the uncertainty at that sample size, and another size estimates another",
                            "Resamples of a different size would not be drawn with replacement",
                            "Otherwise some observations would be drawn twice and others not at all",
                            "Any other size makes the bootstrap distribution non-normal, so the percentiles stop being valid",
                        ],
                        "a": 0,
                        "whys": [
                            "The spread of a statistic depends on how many observations went into it, so resampling ten values from ten is the only draw whose variability mimics the experiment that was run.",
                            "Drawing with replacement is a property of how each value is picked, and it works at any size. The size and the replacement are independent choices.",
                            "That happens in every bootstrap resample and is the mechanism, not a flaw. It is exactly how a resample of ten values differs from the original ten.",
                            "The bootstrap distribution is not required to be normal, and the percentile interval is chosen precisely because it does not assume it is.",
                        ],
                        "why": r"""
The bootstrap approximates *the sampling distribution of the statistic for a study of
this size*. Draw five values instead of ten and you get the sampling distribution of
a five-run study, which is wider, and reporting it as the uncertainty of a ten-run
study overstates it. Draw twenty and you understate it. The size is not a tunable
parameter; it is the part of the experiment being imitated.
""",
                    },
                    {
                        "q": "The base median interval is [41.0, 41.5] and the opt median interval is [37.2, 37.8]. Why is [41.0/37.8, 41.5/37.2] not the interval for the speedup?",
                        "opts": [
                            "It pairs the extremes of two samples that were never both extreme in the same resample",
                            "It is arithmetically invalid, because an interval cannot be divided by another interval",
                            "It reverses the direction of the ratio, so the endpoints come out the wrong way round",
                            "It would be correct if the two samples had the same number of runs, which they do not here",
                        ],
                        "a": 0,
                        "whys": [
                            "Each endpoint of the combined interval describes a world where one sample was at its 2.5th percentile while the other was simultaneously at its 97.5th, which is far rarer than 2.5 per cent.",
                            "Dividing interval endpoints is a well-defined operation and it produces a valid interval for something — a wider one, for a differently defined quantity.",
                            "Dividing the low base endpoint by the high opt endpoint does give the low end of the ratio, so the endpoints are the right way round. The problem is that they are too far apart.",
                            "Both samples here hold ten runs after the warm-up is dropped. Equal sizes do not rescue the combination, because the objection is about coincident extremes.",
                        ],
                        "why": r"""
A resample is one draw of the entire experiment, and the ratio has its own sampling
distribution — which is why the bootstrap computes the ratio inside each trial and
takes percentiles of that. Combining the two intervals asks for the worst of one at
the same instant as the best of the other, an event much rarer than the 5 per cent
the interval is supposed to exclude. The result, [1.0847, 1.1156] against the correct
[1.0891, 1.1128], is conservative here, and being conservative by an unknown amount
is not the same as being right.
""",
                    },
                    {
                        "q": "A speedup interval comes out as [0.988, 1.016]. What may be written?",
                        "opts": [
                            "That the experiment did not resolve the direction of the difference",
                            "That the two systems perform the same, within measurement error",
                            "That the new system is slightly faster, since the point estimate exceeds 1",
                            "That the result is invalid and the runs have to be repeated with a larger sample",
                        ],
                        "a": 0,
                        "whys": [
                            "An interval spanning 1 is compatible with a small win and with a small loss, so what the study established is that it could not tell which.",
                            "Equality is a claim, and this interval supports it no better than it supports a 1.5 per cent win. Absence of evidence has been converted into evidence of absence.",
                            "The point estimate always sits somewhere, and reporting its direction while ignoring an interval that spans 1 is exactly what the interval was computed to prevent.",
                            "There is nothing invalid about the runs. The design was too small for the effect, which is a fact worth reporting and a reason to size the next study, not a reason to discard this one.",
                        ],
                        "why": r"""
The interval says the data are consistent with anything between a 1.2 per cent
regression and a 1.6 per cent improvement. Writing *no difference* upgrades that into
a positive claim about equality, which would need its own design — an equivalence
test with a stated margin. The useful thing to do with a straddling interval is to
feed it back into module 2: given the spread you now know, `runs_needed` says how
many runs would resolve the smallest effect you care about.
""",
                    },
                    {
                        "q": "Benchmarking folklore says to report the fastest run. What does that cost you here?",
                        "opts": [
                            "A bootstrap interval for a minimum is untrustworthy: no resample beats the fastest run seen",
                            "Nothing — the minimum is the least noisy statistic, so its interval is the narrowest and the most reliable",
                            "The minimum is biased upwards, so the reported speedup is systematically too small",
                            "The minimum cannot be computed from a sample containing a declared warm-up prefix",
                        ],
                        "a": 0,
                        "whys": [
                            "Every resample is drawn from the observed values, so its minimum is bounded below by the one fastest run, and the resulting interval understates how much that run could have moved.",
                            "The minimum is an extreme rather than a centre, and MA201 named exactly this failure for the maximum: resampling cannot explore beyond the data on the side that matters.",
                            "The sample minimum is biased the other way if anything, sitting at or above the true floor, and the direction is not what makes its interval untrustworthy.",
                            "It computes perfectly well once the warm-up is dropped. The difficulty is with the interval around it, not with the number itself.",
                        ],
                        "why": r"""
The minimum is a defensible *estimand* — it answers "how fast is this on an
undisturbed machine", which is sometimes the question — but it is exactly the kind of
non-smooth statistic MA201 warned the bootstrap about. A resample can only contain
values already observed, so the bootstrap distribution of the minimum piles up on the
single fastest run and its spread is an artefact of how often that one value gets
drawn. Report a minimum if the question calls for it, and do not put a resampling
interval around it.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Bootstrapping a ratio, five holes deep",
                "minutes": 9,
                "lang": "python",
                "caption": "bench.py — one resample of the whole experiment, and the percentile interval it feeds",
                "brief": r'''
The whole of this module is two short functions: one that draws the experiment again
and again, and one that reads the middle of what came out. Each hole is a place where
a plausible alternative quietly changes the quantity being estimated, or reaches for
the global random state that a reproducible study must never touch.

Nothing is executed here. Filled in correctly, the ten warm runs of each system give
a speedup of 1.1015 with a 95 per cent interval of [1.0891, 1.1128].
''',
                "listing": r'''
def bootstrap_ratio(base, opt, trials=2000, seed=451):
    """The sampling distribution of the ratio of the two medians."""
    rng = random.___(seed)
    ratios = []
    for _ in range(trials):
        rb = [rng.choice(base) for _ in range(___)]
        ro = [rng.choice(opt) for _ in range(len(opt))]
        ratios.append(median(rb) / median(___))
    return ratios


def bootstrap_ci(values, level=0.95):
    """The percentile interval of a bootstrap distribution."""
    tail = (1 - level) / ___
    return percentile(values, tail), percentile(values, ___)
''',
                "blanks": [
                    {
                        "prompt": "The study must be reproducible and must not disturb anything else that draws numbers. What is constructed here?",
                        "hole": "?",
                        "opts": ["Random", "seed", "choice", "sample"],
                        "a": 0,
                        "why": "A private generator carries its own state, so the function returns the same list every time and nothing outside it is affected. Every other caller of the module keeps whatever stream it had.",
                        "whys": [
                            "A private generator carries its own state, so the function returns the same list every time and nothing outside it is affected. Every other caller of the module keeps whatever stream it had.",
                            "This reseeds the process-wide generator and returns None, so the next line fails immediately — and had it been written as a bare statement instead, the function would silently reach into global state and change what every other part of the program draws.",
                            "This picks one element from a sequence rather than building a generator, so it would need a sequence rather than an integer and could not supply the stream the loop below consumes.",
                            "This draws several distinct elements without replacement, which is the wrong operation twice over: it is not a constructor, and sampling without replacement is not what a bootstrap does.",
                        ],
                    },
                    {
                        "prompt": "How many values does one resample of the base group hold?",
                        "hole": "?",
                        "opts": ["len(base)", "len(opt)", "trials", "len(base) - 1"],
                        "a": 0,
                        "why": "A resample imitates the study that was run, and that study had this many base observations. Any other size estimates the uncertainty of a study nobody performed.",
                        "whys": [
                            "A resample imitates the study that was run, and that study had this many base observations. Any other size estimates the uncertainty of a study nobody performed.",
                            "The two groups need not be the same size, and borrowing the other group's count silently reports the uncertainty of a differently shaped experiment whenever they differ.",
                            "This draws two thousand values per trial from a sample of ten, which collapses the variability almost to nothing and produces an interval far too narrow to be honest.",
                            "This is the jackknife instinct, leaving one observation out. It shrinks every resample by one and reports the uncertainty of a nine-run study rather than a ten-run one.",
                        ],
                    },
                    {
                        "prompt": "The numerator is the median of the freshly drawn base sample. What is the denominator?",
                        "hole": "?",
                        "opts": ["ro", "opt", "rb", "base"],
                        "a": 0,
                        "why": "Both halves of the experiment are drawn again in every trial, so the ratio varies the way a repeated study would. The resampled opt group is the one built on the line above.",
                        "whys": [
                            "Both halves of the experiment are drawn again in every trial, so the ratio varies the way a repeated study would. The resampled opt group is the one built on the line above.",
                            "Using the original opt sample freezes the denominator, so the interval reflects only the variability of the base group and comes out too narrow. It also makes the line above dead code.",
                            "This divides the resampled base median by itself, giving exactly 1.0 in every trial and an interval of zero width around a number that means nothing.",
                            "This freezes the numerator instead, and combined with a resampled denominator it estimates the uncertainty of the wrong half of the experiment.",
                        ],
                    },
                    {
                        "prompt": "A 95 per cent interval leaves 5 per cent outside. How is that split?",
                        "hole": "?",
                        "opts": ["2", "1", "100", "trials"],
                        "a": 0,
                        "why": "The excluded mass is shared between the two tails, so each end discards 2.5 per cent and the interval runs from the 0.025 quantile to the 0.975 one.",
                        "whys": [
                            "The excluded mass is shared between the two tails, so each end discards 2.5 per cent and the interval runs from the 0.025 quantile to the 0.975 one.",
                            "This puts the whole 5 per cent in the lower tail and none in the upper, giving a one-sided bound reported as though it were a two-sided interval.",
                            "This treats the level as a percentage rather than a fraction, and the tail comes out at 0.0005 — an interval so wide it is effectively the whole bootstrap distribution.",
                            "The number of trials controls how finely the distribution is estimated, not how much of it the interval excludes. Dividing by it makes the tail vanish as the trials increase.",
                        ],
                    },
                    {
                        "prompt": "The lower endpoint sits at the tail quantile. Where does the upper one sit?",
                        "hole": "?",
                        "opts": ["1 - tail", "tail", "level", "1 - level"],
                        "a": 0,
                        "why": "Symmetry about the middle: as much is discarded above as below, so the upper endpoint is as far from 1 as the lower is from 0. At level 0.95 that is the 0.975 quantile.",
                        "whys": [
                            "Symmetry about the middle: as much is discarded above as below, so the upper endpoint is as far from 1 as the lower is from 0. At level 0.95 that is the 0.975 quantile.",
                            "Both endpoints would then be the same quantile, so the interval has zero width and reports the 2.5th percentile of the bootstrap distribution twice.",
                            "The 0.95 quantile leaves 5 per cent above it rather than 2.5, so the interval covers about 92.5 per cent of the distribution while claiming 95.",
                            "This is 0.05, which sits below the lower endpoint, and the interval comes out inverted with its upper bound smaller than its lower one.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "A benchmark report with an interval on it",
                "minutes": 55,
                "runtime": "python",
                "brief": r'''
`stats.py` arrives finished and is not to be edited: `mean`, `sample_variance`,
`percentile` and `median` are MA201's estimators, imported rather than rebuilt.
Everything below goes in `main.py`, which already holds `BASE` and `OPT` — the
twelve runs of each system from the reading, warm-up included.

1. `drop_warmup(samples, k)` — a **new** list without the first `k` entries. A
   negative `k`, or a `k` that would leave nothing, is a `ValueError`.

2. `summarise(samples)` — `{"n", "mean", "median", "p95", "sd", "min"}`, where
   `sd` is the square root of the sample variance and `p95` is
   `percentile(samples, 0.95)`. Empty input is a `ValueError`.

3. `bootstrap(samples, statistic, trials=2000, seed=451)` — a list of `trials`
   values, each `statistic` applied to a resample of the same length as
   `samples`, drawn with replacement from a **private** `random.Random(seed)`.
   A non-positive `trials` is a `ValueError`.

4. `bootstrap_ci(values, level=0.95)` — the percentile interval, as a tuple.

5. `speedup(base, opt)` — `median(base) / median(opt)`.

6. `speedup_ci(base, opt, trials=2000, seed=451, level=0.95)` — resample
   **both** groups inside each trial, `base` first, from one generator; take the
   ratio of the two medians; return the percentile interval of those ratios.

7. `resolved(ci)` — `True` when the interval does not contain `1.0`.

8. `report(base, opt, warmup=2, trials=2000, seed=451)` —
   `{"warmup", "base", "opt", "speedup", "ci", "resolved"}`, where `base` and
   `opt` are `summarise` of the warm-up-dropped samples and the rest follow from
   them.

```text
report(BASE, OPT)["speedup"]   ->  1.1014686248331107
report(BASE, OPT)["ci"]        ->  (1.0890927866547992, 1.112751677852349)
report(BASE, OPT)["resolved"]  ->  True
report(BASE, OPT, warmup=0)["ci"]  ->  (1.014814358131251, 1.1155913978494623)
```

Drawing order is part of the answer: within one trial, draw the whole base
resample before the first opt value, or the seed will not reproduce these
numbers.
''',
                "hints": [
                    "`rng = random.Random(seed)` gives a generator whose state belongs to this call alone — `random.seed(...)` would reach into the process-wide stream instead.",
                    "`[rng.choice(samples) for _ in samples]` is a resample of the right length in one line.",
                    "`bootstrap_ci` needs the tail from the level: `tail = (1 - level) / 2`, then `percentile(values, tail)` and `percentile(values, 1 - tail)`.",
                    "`speedup_ci` cannot call `bootstrap` twice — two independent loops would each start the generator afresh and pair up draws that never happened together.",
                    "`report` is assembly: drop the warm-up from both, summarise each, and pass the dropped samples to `speedup` and `speedup_ci`.",
                ],
                "files": [
                    {"name": "stats.py", "ro": True, "content": r'''
"""The estimators MA201 built. Read-only: this module is about using them."""


def mean(values):
    """The arithmetic mean."""
    if not values:
        raise ValueError("no values to average")
    return sum(values) / len(values)


def sample_variance(values):
    """The unbiased sample variance, with the n - 1 divisor."""
    if len(values) < 2:
        raise ValueError("a variance needs at least two observations")
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - 1)


def percentile(values, q):
    """The q quantile, by linear interpolation between order statistics."""
    if not values:
        raise ValueError("no values to take a percentile of")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must lie in [0, 1]")
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    position = q * (len(xs) - 1)
    low = int(position)
    high = min(low + 1, len(xs) - 1)
    weight = position - low
    return xs[low] * (1 - weight) + xs[high] * weight


def median(values):
    """The 0.5 quantile."""
    return percentile(values, 0.5)
'''},
                    {"name": "main.py", "content": r'''
import math
import random

from stats import mean, median, percentile, sample_variance

BASE = [44.1, 42.0, 41.6, 40.9, 41.2, 41.0, 41.5, 40.8, 41.3, 47.9, 41.1, 41.4]
OPT = [96.4, 51.2, 37.6, 37.2, 37.9, 37.4, 37.1, 37.8, 43.6, 37.3, 37.5, 37.0]


def drop_warmup(samples, k):
    """A new list without the first k entries."""
    # your code here


def summarise(samples):
    """n, mean, median, p95, sd and min, as a dict."""
    # your code here


def bootstrap(samples, statistic, trials=2000, seed=451):
    """The statistic recomputed on `trials` resamples of the same length."""
    # your code here


def bootstrap_ci(values, level=0.95):
    """The percentile interval of a bootstrap distribution."""
    # your code here


def speedup(base, opt):
    """How many times faster the opt runs are, at the median."""
    # your code here


def speedup_ci(base, opt, trials=2000, seed=451, level=0.95):
    """The interval for the ratio, bootstrapped on the ratio itself."""
    # your code here


def resolved(ci):
    """True when the interval does not contain 1.0."""
    # your code here


def report(base, opt, warmup=2, trials=2000, seed=451):
    """The whole benchmark, warm-up dropped and an interval attached."""
    # your code here


if __name__ == "__main__":
    result = report(BASE, OPT)
    if result:
        print(f"speedup {result['speedup']:.4f} "
              f"[{result['ci'][0]:.4f}, {result['ci'][1]:.4f}] "
              f"resolved={result['resolved']}")
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random

from stats import mean, median, percentile, sample_variance

BASE = [44.1, 42.0, 41.6, 40.9, 41.2, 41.0, 41.5, 40.8, 41.3, 47.9, 41.1, 41.4]
OPT = [96.4, 51.2, 37.6, 37.2, 37.9, 37.4, 37.1, 37.8, 43.6, 37.3, 37.5, 37.0]


def drop_warmup(samples, k):
    """A new list without the first k entries."""
    if k < 0:
        raise ValueError("a warm-up cannot be negative")
    if k >= len(samples):
        raise ValueError(f"dropping {k} of {len(samples)} runs leaves nothing to report")
    return list(samples[k:])


def summarise(samples):
    """n, mean, median, p95, sd and min, as a dict."""
    if not samples:
        raise ValueError("nothing to summarise")
    return {
        "n": len(samples),
        "mean": mean(samples),
        "median": median(samples),
        "p95": percentile(samples, 0.95),
        "sd": math.sqrt(sample_variance(samples)) if len(samples) > 1 else 0.0,
        "min": min(samples),
    }


def bootstrap(samples, statistic, trials=2000, seed=451):
    """The statistic recomputed on `trials` resamples of the same length."""
    if not samples:
        raise ValueError("nothing to resample")
    if trials <= 0:
        raise ValueError("need at least one bootstrap trial")
    rng = random.Random(seed)
    return [statistic([rng.choice(samples) for _ in samples]) for _ in range(trials)]


def bootstrap_ci(values, level=0.95):
    """The percentile interval of a bootstrap distribution."""
    if not 0.0 < level < 1.0:
        raise ValueError("a confidence level lies strictly between 0 and 1")
    tail = (1 - level) / 2
    return percentile(values, tail), percentile(values, 1 - tail)


def speedup(base, opt):
    """How many times faster the opt runs are, at the median."""
    return median(base) / median(opt)


def speedup_ci(base, opt, trials=2000, seed=451, level=0.95):
    """The interval for the ratio, bootstrapped on the ratio itself."""
    if trials <= 0:
        raise ValueError("need at least one bootstrap trial")
    rng = random.Random(seed)
    ratios = []
    for _ in range(trials):
        resampled_base = [rng.choice(base) for _ in base]
        resampled_opt = [rng.choice(opt) for _ in opt]
        ratios.append(median(resampled_base) / median(resampled_opt))
    return bootstrap_ci(ratios, level)


def resolved(ci):
    """True when the interval does not contain 1.0."""
    low, high = ci
    return not (low <= 1.0 <= high)


def report(base, opt, warmup=2, trials=2000, seed=451):
    """The whole benchmark, warm-up dropped and an interval attached."""
    warm_base = drop_warmup(base, warmup)
    warm_opt = drop_warmup(opt, warmup)
    interval = speedup_ci(warm_base, warm_opt, trials, seed)
    return {
        "warmup": warmup,
        "base": summarise(warm_base),
        "opt": summarise(warm_opt),
        "speedup": speedup(warm_base, warm_opt),
        "ci": interval,
        "resolved": resolved(interval),
    }


if __name__ == "__main__":
    result = report(BASE, OPT)
    if result:
        print(f"speedup {result['speedup']:.4f} "
              f"[{result['ci'][0]:.4f}, {result['ci'][1]:.4f}] "
              f"resolved={result['resolved']}")
'''}],
                "tests": [
                    {"name": "drop_warmup takes from the front and refuses the impossible", "code": r'''
assert drop_warmup(BASE, 2) == BASE[2:], "the first two runs go, the rest stay in order"
_copy = drop_warmup(BASE, 0)
assert _copy == BASE and _copy is not BASE, "k=0 returns a copy, not the caller's list"
_copy.append(999)
assert len(BASE) == 12, "drop_warmup must not hand back an alias of its argument"
for _bad in (-1, 12, 13):
    try:
        drop_warmup(BASE, _bad)
        assert False, f"drop_warmup(BASE, {_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "summarise reports the six numbers of a warm sample", "code": r'''
_s = summarise(drop_warmup(BASE, 2))
assert _s["n"] == 10, f"n was {_s['n']!r}"
assert abs(_s["mean"] - 41.87) < 1e-9, f"mean was {_s['mean']!r}"
assert abs(_s["median"] - 41.25) < 1e-9, f"median was {_s['median']!r}"
assert abs(_s["p95"] - 45.065) < 1e-9, f"p95 was {_s['p95']!r}"
assert abs(_s["sd"] - 2.1344007746) < 1e-6, f"sd was {_s['sd']!r}"
assert abs(_s["min"] - 40.8) < 1e-9, f"min was {_s['min']!r}"
assert _s["mean"] > _s["median"], "a right tail drags the mean above the median"
try:
    summarise([])
    assert False, "summarise([]) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "bootstrap is seeded, sized correctly, and drawn from the sample", "code": r'''
_warm = drop_warmup(BASE, 2)
_a = bootstrap(_warm, median, trials=500, seed=7)
_b = bootstrap(_warm, median, trials=500, seed=7)
assert _a == _b, "the same seed must give the identical list"
assert bootstrap(_warm, median, trials=500, seed=8) != _a, "a different seed must give a different list"
assert len(_a) == 500, f"one value per trial, got {len(_a)}"
assert min(_a) >= min(_warm) and max(_a) <= max(_warm), \
    "a resample holds only observed values, so its median cannot leave their range"
assert abs(bootstrap(_warm, len, trials=3, seed=1)[0] - len(_warm)) < 1e-9, \
    "each resample is the same length as the sample it came from"
try:
    bootstrap(_warm, median, trials=0)
    assert False, "trials=0 should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "bootstrap never touches the process-wide random stream", "code": r'''
_warm = drop_warmup(BASE, 2)
random.seed(7)
_before = random.random()
_drawn = bootstrap(_warm, median, trials=200, seed=451)
_after = random.random()
random.seed(7)
assert len(_drawn) == 200, f"the bootstrap returned {_drawn!r} rather than 200 values"
assert [random.random(), random.random()] == [_before, _after], \
    "the bootstrap consumed values from the global generator — use random.Random(seed)"
random.seed(1)
_x = speedup_ci(_warm, drop_warmup(OPT, 2), trials=200)
random.seed(999)
_y = speedup_ci(_warm, drop_warmup(OPT, 2), trials=200)
assert _x == _y, "the result must not depend on the global seed"
'''},
                    {"name": "bootstrap_ci brackets the statistic it was built from", "code": r'''
_warm = drop_warmup(BASE, 2)
_lo, _hi = bootstrap_ci(bootstrap(_warm, median))
assert abs(_lo - 41.0) < 1e-9 and abs(_hi - 41.5) < 1e-9, f"got ({_lo!r}, {_hi!r})"
assert _lo <= median(_warm) <= _hi, "the interval should contain the observed median"
_wide = bootstrap_ci(bootstrap(_warm, median), level=0.50)
assert _wide[0] >= _lo and _wide[1] <= _hi, "a 50 per cent interval sits inside a 95 per cent one"
for _bad in (0.0, 1.0, 1.5):
    try:
        bootstrap_ci([1.0, 2.0], level=_bad)
        assert False, f"level={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "speedup and its interval match the reading", "code": r'''
_b, _o = drop_warmup(BASE, 2), drop_warmup(OPT, 2)
assert abs(speedup(_b, _o) - 1.1014686248331107) < 1e-12, f"got {speedup(_b, _o)!r}"
_ci = speedup_ci(_b, _o)
assert abs(_ci[0] - 1.0890927866547992) < 1e-9, f"low end was {_ci[0]!r}"
assert abs(_ci[1] - 1.112751677852349) < 1e-9, f"high end was {_ci[1]!r}"
assert _ci[0] <= speedup(_b, _o) <= _ci[1], "the interval must contain the point estimate"
assert _ci[0] > 1.0, "this interval excludes 1, so the direction is resolved"
'''},
                    {"name": "The ratio is bootstrapped on the ratio, not assembled from two intervals", "code": r'''
_b, _o = drop_warmup(BASE, 2), drop_warmup(OPT, 2)
_ci = speedup_ci(_b, _o)
_base_ci = bootstrap_ci(bootstrap(_b, median))
_opt_ci = bootstrap_ci(bootstrap(_o, median))
_combined = (_base_ci[0] / _opt_ci[1], _base_ci[1] / _opt_ci[0])
assert _combined[0] < _ci[0] and _combined[1] > _ci[1], \
    "dividing the endpoints of two intervals is wider at both ends than the ratio bootstrap"
assert abs(_combined[0] - 1.0846560846560847) < 1e-9, f"combined low was {_combined[0]!r}"
'''},
                    {"name": "resolved reads an interval against 1.0", "code": r'''
assert resolved((1.089, 1.113)) is True, "an interval entirely above 1 resolves the direction"
assert resolved((0.87, 0.94)) is True, "and so does one entirely below it"
assert resolved((0.988, 1.016)) is False, "an interval spanning 1 resolves nothing"
assert resolved((1.0, 1.2)) is False, "touching 1 at an endpoint is not excluding it"
assert resolved((0.9, 1.0)) is False, "nor at the other endpoint"
'''},
                    {"name": "report assembles it, and the warm-up is what turns the result round", "code": r'''
_r = report(BASE, OPT)
assert set(_r) == {"warmup", "base", "opt", "speedup", "ci", "resolved"}, f"keys were {sorted(_r)!r}"
assert _r["warmup"] == 2 and _r["base"]["n"] == 10 and _r["opt"]["n"] == 10, f"got {_r['warmup']!r}"
assert abs(_r["speedup"] - 1.1014686248331107) < 1e-12, f"speedup was {_r['speedup']!r}"
assert abs(_r["ci"][0] - 1.0890927866547992) < 1e-9, f"ci was {_r['ci']!r}"
assert _r["resolved"] is True
_raw = report(BASE, OPT, warmup=0)
assert _raw["base"]["n"] == 12 and abs(_raw["opt"]["mean"] - 44.0) < 1e-9, f"got {_raw['opt']!r}"
assert (_raw["ci"][1] - _raw["ci"][0]) > 3 * (_r["ci"][1] - _r["ci"][0]), \
    "leaving the warm-up in should widen the interval several times over"
assert report(BASE, OPT) == _r, "two calls with the same arguments must agree exactly"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Families of comparisons",
            "summary": "Permutation p-values, the family-wise error rate, and correcting a sweep with Holm-Bonferroni.",
            "concepts": [
                r"A sweep of $m$ comparisons at $\alpha$ raises the chance of at least one false alarm to $1 - (1-\alpha)^{m}$",
                r"Twelve independent comparisons at $\alpha = 0.05$ produce a false alarm 46 per cent of the time",
                "A permutation test builds the null distribution by relabelling, and assumes exchangeability rather than normality",
                r"The $+1$ correction, $p = (1 + \text{hits}) / (1 + B)$, keeps a permutation p-value away from an impossible zero",
                r"Bonferroni compares every p-value with $\alpha/m$; Holm steps down through $\alpha/(m-k)$ and rejects at least as much",
                "Holm's adjusted p-values need a running maximum, or they can decrease as the rank rises",
                "Controlling the family-wise error rate costs power, and the family is whatever you actually looked at",
            ],
            "read": [
                {
                    "title": "Twelve flags, one winner, and a coin that lands heads far too often",
                    "minutes": 15,
                    "body": r'''
A student sweeps twelve compiler flag combinations against an unmodified build, eight
runs of each, and tests every one of them. Eleven come back unremarkable. The twelfth
gives $p = 0.032$, which is below 0.05, and the write-up says the flag makes the
program faster.

The trouble is not the test. It is that twelve tests were run and one was reported.

## What a significance level promises, and to whom

A test at $\alpha = 0.05$ promises that, when nothing is going on, it raises a false
alarm at most 5 per cent of the time. That promise is about one test. Run $m$ of them
on data where nothing is going on, and each has its own 5 per cent chance, so the
chance that **none** of them fires is $0.95^{m}$ and the chance that at least one does
is what is left:

$$P(\text{any}) = 1 - (1 - \alpha)^{m} .$$

Nothing here is an extra assumption dressed up as a rule; it is the complement of
twelve independent events all failing to happen.

```python
for m in (1, 2, 6, 12, 20):
    print(f"m={m:<3} at least one false alarm with probability {1 - 0.95 ** m:.4f}")
```

```text
m=1   at least one false alarm with probability 0.0500
m=2   at least one false alarm with probability 0.0975
m=6   at least one false alarm with probability 0.2649
m=12  at least one false alarm with probability 0.4596
m=20  at least one false alarm with probability 0.6415
```

Twelve comparisons at the 5 per cent level are a coin that lands heads 46 per cent of
the time. A sweep of twenty is worse than a fair coin. The single reported $p = 0.032$
was never a 3 per cent event; it was one draw from a procedure that produces something
like it almost half the time.

## Watching it happen

That is an argument. Here is the thing itself: twelve comparisons in which the two
groups are drawn from the same generator, so every null hypothesis is true by
construction, and no effect exists anywhere in the data.

The p-values come from a **permutation test**, which is the right tool for benchmark
timings. Its logic is short. If the label `base` or `variant` makes no difference,
then the sixteen numbers in front of you would have been the same sixteen numbers
under any relabelling, so shuffle the labels a thousand times, recompute the statistic
each time, and see where the observed value falls among them. That assumes only
**exchangeability** — that the labels are arbitrary under the null — and in
particular it assumes nothing about the shape of the distribution, which is welcome,
because the data below are uniform rather than normal and module 3 established that
timings are neither.

```python
import random


def mean(xs):
    return sum(xs) / len(xs)


def permutation_p(a, b, trials=999, seed=451):
    """Two-sided p-value by relabelling, with the +1 correction."""
    rng = random.Random(seed)
    observed = abs(mean(a) - mean(b))
    pool = list(a) + list(b)
    hits = 0
    for _ in range(trials):
        rng.shuffle(pool)
        if abs(mean(pool[:len(a)]) - mean(pool[len(a):])) >= observed - 1e-12:
            hits += 1
    return (1 + hits) / (1 + trials)


rng = random.Random(7)
for i in range(12):
    a = [round(100.0 + 12.0 * (rng.random() - 0.5), 3) for _ in range(8)]
    b = [round(100.0 + 12.0 * (rng.random() - 0.5), 3) for _ in range(8)]
    p = permutation_p(a, b)
    print(f"flag{i + 1:<4} p = {p:.3f}" + ("   <- 'significant'" if p < 0.05 else ""))
```

```text
flag1    p = 0.678
flag2    p = 0.186
flag3    p = 0.121
flag4    p = 0.600
flag5    p = 0.682
flag6    p = 0.197
flag7    p = 0.739
flag8    p = 0.013   <- 'significant'
flag9    p = 0.161
flag10   p = 0.443
flag11   p = 0.292
flag12   p = 0.045   <- 'significant'
```

Two discoveries, from data containing nothing to discover. One of them at
$p = 0.013$, which is the kind of number that gets a sentence in an abstract.

Two details of that function are worth stopping on. The comparison uses `abs`, which
is what makes the test two-sided: a relabelling that pushes the difference the other
way is equally extreme. And the returned value is $(1 + \text{hits}) / (1 + B)$ rather
than $\text{hits}/B$. A permutation p-value of exactly zero would claim that no
relabelling out of all of them is as extreme as the observed one, which is false — the
identity relabelling is — so the observed arrangement is counted in, and the smallest
value the test can return is $1/(B+1)$, here $0.001$.

## Holm, and why it beats Bonferroni for free

Bonferroni is the obvious repair: if $m$ tests each get $\alpha/m$, then by the union
bound the chance that any of them fires is at most $m \cdot \alpha/m = \alpha$. At
twelve comparisons that threshold is $0.05/12 = 0.004167$, and neither of the two
false alarms above comes close to it. It works.

It is also stricter than it needs to be, and Holm's procedure gets the same guarantee
while rejecting more. Sort the p-values ascending. Compare the smallest with
$\alpha/m$, the next with $\alpha/(m-1)$, the next with $\alpha/(m-2)$, and so on;
stop at the first one that fails, and retain it and everything after it. The reasoning
is that once the smallest has been rejected, only $m-1$ hypotheses are still in play,
so the remaining budget may be divided among those.

Take a real sweep of six flags with the p-values below.

```python
P = [0.0021, 0.0090, 0.0290, 0.0331, 0.0402, 0.2100]
NAMES = ["O3", "lto", "pgo", "unroll", "fastmath", "prefetch"]
alpha, m = 0.05, len(P)
order = sorted(range(m), key=lambda i: P[i])
running = 0.0
stopped = False
print(f"{'rank':<6}{'flag':<10}{'p':>8}{'threshold':>11}{'adjusted':>10}  verdict")
for rank, i in enumerate(order):
    threshold = alpha / (m - rank)
    running = max(running, min(1.0, (m - rank) * P[i]))
    if not stopped and P[i] > threshold:
        stopped = True
    print(f"{rank + 1:<6}{NAMES[i]:<10}{P[i]:>8.4f}{threshold:>11.6f}"
          f"{running:>10.4f}  {'retain' if stopped else 'REJECT'}")
print("Bonferroni rejects:", sum(1 for p in P if p <= alpha / m))
```

```text
rank  flag             p  threshold  adjusted  verdict
1     O3          0.0021   0.008333    0.0126  REJECT
2     lto         0.0090   0.010000    0.0450  REJECT
3     pgo         0.0290   0.012500    0.1160  retain
4     unroll      0.0331   0.016667    0.1160  retain
5     fastmath    0.0402   0.025000    0.1160  retain
6     prefetch    0.2100   0.050000    0.2100  retain
Bonferroni rejects: 1
```

Bonferroni holds every p-value against $0.008333$ and keeps only `O3`. Holm keeps
`O3` and `lto`, because by the time `lto` is examined the threshold has relaxed to
$0.05/5 = 0.01$ and $0.0090$ clears it. One extra finding, the same family-wise
guarantee, and no additional data.

## Why the adjusted column needs a running maximum

The `adjusted` column is the same decision written as a number: multiply each sorted
p-value by how many hypotheses were still in play when it was examined, and reject
whatever comes out at or below $\alpha$. Compare against the threshold column and the
two agree everywhere.

But look at the raw products before the running maximum is applied. Rank 3 gives
$4 \times 0.0290 = 0.1160$, rank 4 gives $3 \times 0.0331 = 0.0993$, and rank 5 gives
$2 \times 0.0402 = 0.0804$. They go **down** as the p-values go up, because the
multiplier shrinks faster than the p-value grows. Reported as they stand, `fastmath`
would carry a smaller adjusted p-value than `pgo` despite a larger raw one, and a
threshold drawn anywhere between 0.0804 and 0.1160 would reject a hypothesis while
retaining a more significant one. The running maximum — each adjusted value is the
largest product seen so far — removes that, which is why the three of them read
0.1160 in the table.

## The mistakes

**Reading non-significance as no effect.** Nothing above survived correction, and the
sentence that follows is *this sweep found no flag whose effect it could establish*,
not *no flag helps*. The distinction matters most exactly here, because correction
makes non-significance more common by design.

**Deciding the family after seeing the p-values.** The family is every comparison the
result was selected from, including the ones that went unreported and the ones tried
before the analysis was settled. It is tempting to count only the comparisons that
appear in the paper, since those are the ones the reader sees, and that is precisely
the count that makes the correction meaningless.

**Correcting when there is one pre-registered comparison.** Correction is not a
ritual. A study with a single stated hypothesis and a single test does not divide
anything, and applying a correction there only discards power.

## Where this stops holding

The $1 - (1-\alpha)^{m}$ figure assumes the comparisons are independent, and a sweep
of flags against a shared baseline is not: every comparison reuses the same baseline
runs, so the p-values are correlated and the true family-wise rate is lower than 0.46.
Bonferroni and Holm both survive that, because the union bound they rest on needs no
independence at all — it is loose under positive dependence, so the correction is
conservative rather than wrong.

The family-wise error rate is also not always the quantity you want. Screening ten
thousand configurations to find candidates worth investigating is better served by
controlling the false discovery rate, which tolerates a known proportion of mistakes
among the rejections instead of forbidding all of them. Holm is the right default for
a handful of comparisons in a thesis chapter, not for a genome.

And a permutation test needs exchangeability. Runs that drift as a machine warms up
are not exchangeable, because their order carries information, and shuffling destroys
exactly the structure that would have revealed the drift.

The lab for this module, **a family of comparisons, corrected**, builds
`permutation_p`, `bonferroni`, `holm`, `holm_adjusted`, `family_error` and
`family_report`, and runs the whole sweep of twelve null comparisons through them.
''',
                },
            ],
            "quiz": {
                "title": "What twelve tests cost",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Twelve independent comparisons are each tested at the 5 per cent level on data where nothing differs. How often does at least one come out significant?",
                        "opts": [
                            "About 46 per cent of the time, which is one minus 0.95 raised to the twelfth",
                            "About 5 per cent of the time, since that is what the significance level promises",
                            "About 60 per cent of the time, since twelve times five per cent exceeds one half",
                            "It cannot be stated without knowing how large each of the twelve samples was",
                        ],
                        "a": 0,
                        "whys": [
                            "The chance that all twelve stay quiet is 0.95 multiplied by itself twelve times, about 0.54, and the complement of that is the chance at least one fires.",
                            "That promise is about a single test. Repeating it twelve times gives twelve separate chances to fire, and the guarantee was never about the collection.",
                            "Twelve times five per cent is 0.60, and that sum is the union bound rather than the probability — it double-counts the outcomes where two or more fire at once.",
                            "The sample size affects the power to detect a real effect. Under the null the false-alarm rate is the significance level whatever the sample size is.",
                        ],
                        "why": r"""
$1 - 0.95^{12} = 0.4596$. The complement is the easy way to see it: all twelve have to
stay quiet, each does so with probability 0.95, and independent events multiply.
Notice that $12 \times 0.05 = 0.6$ is not far off and is always an overestimate — that
is the union bound, which counts the overlaps twice, and it is exactly the bound
Bonferroni rests on.
""",
                    },
                    {
                        "q": "Why does a permutation p-value use the count of extreme shuffles plus one, over the number of shuffles plus one?",
                        "opts": [
                            "The observed arrangement is itself a relabelling, so a p-value of zero would be false",
                            "It compensates for using a finite number of shuffles rather than all of them",
                            "It keeps the p-value below 1 when every shuffle turns out to be at least as extreme",
                            "It converts a one-sided count into a two-sided p-value without recomputing the statistic",
                        ],
                        "a": 0,
                        "whys": [
                            "Whatever else the shuffles do, the identity relabelling is one of the arrangements and is exactly as extreme as itself, so at least one always counts.",
                            "The finite number of shuffles makes the p-value noisy, and more shuffles reduce that noise, but neither effect is what the plus one repairs.",
                            "When every shuffle is at least as extreme the value comes out at exactly 1, which is correct and needs no protection. The floor is what is being protected.",
                            "Two-sidedness comes from taking the absolute difference inside the loop. The plus one appears identically in a one-sided test.",
                        ],
                        "why": r"""
Without it, a study reporting `hits = 0` from 999 shuffles would print $p = 0$, a
claim that no relabelling whatever is as extreme as the observed one. The observed
labelling is a relabelling and ties itself, so it belongs in the numerator and in the
denominator. The practical consequence is a floor: with $B = 999$ the smallest
attainable p-value is $0.001$, and a study wanting to report something smaller has to
run more shuffles rather than write a smaller number.
""",
                    },
                    {
                        "q": "What does a permutation test assume that a two-sample t test does not have to?",
                        "opts": [
                            "Nothing extra — it drops the normality assumption and needs only exchangeable labels",
                            "That the two groups have the same number of observations in each of them",
                            "That the observations are normally distributed, which the shuffling then exploits fully",
                            "That the effect, if any, is a shift in the mean rather than a change in spread",
                        ],
                        "a": 0,
                        "whys": [
                            "Under the null the labels are arbitrary, and that is the whole premise; the reference distribution is built from the data rather than assumed.",
                            "Unequal group sizes are handled by splitting each shuffled pool at the original boundary. Nothing in the procedure requires the two sizes to match.",
                            "This inverts the relationship. Freedom from the normal assumption is the reason to reach for a permutation test on timing data in the first place.",
                            "The choice of statistic decides what the test is sensitive to, and a difference of means is indeed a shift statistic — but that is a choice you make, not an assumption the method imposes.",
                        ],
                        "why": r"""
Exchangeability is the premise: if the label carries no information, the observed
arrangement is one of the equally likely relabellings, and its rank among them is the
p-value. That is weaker than normality, which is why the reading uses uniform data and
gets valid p-values anyway. It is not free of assumptions: exchangeability fails when
the order of the runs matters, which is exactly what happens when a machine warms up
over an afternoon.
""",
                    },
                    {
                        "q": "Six p-values are corrected. Bonferroni rejects one, Holm rejects two. Where does Holm's extra rejection come from?",
                        "opts": [
                            "Once the smallest is rejected only five remain, so the next threshold is alpha over five",
                            "Holm controls a weaker error rate, so it is allowed to be less strict about each test",
                            "Holm applies the correction to the sorted p-values rather than to the unsorted ones",
                            "Holm uses a sharper bound than the union bound, and the extra rejection comes out of that",
                        ],
                        "a": 0,
                        "whys": [
                            "The step-down is the whole of it: the divisor shrinks as hypotheses are eliminated, so the second p-value faces 0.01 rather than the 0.008333 Bonferroni holds everything to.",
                            "Both control the family-wise error rate at the same alpha. Holm is uniformly at least as powerful while giving away nothing, which is what makes it the better default.",
                            "Sorting is how the procedure is organised, and Bonferroni is unaffected by order. Sorting alone changes no decision; the shrinking divisor does.",
                            "Holm rests on the same union bound. What it adds is the observation that the bound need only cover the hypotheses still under consideration at each step.",
                        ],
                        "why": r"""
Bonferroni holds all six against $0.05/6 = 0.008333$, and `lto` at $0.0090$ misses.
Holm examines the sorted list: `O3` at $0.0021$ clears $0.05/6$, and now only five
hypotheses are live, so `lto` is held against $0.05/5 = 0.01$ and clears it. The
guarantee is unchanged, because at each step the budget is spread over exactly the
hypotheses that have not yet been rejected. Holm is never worse than Bonferroni and
sometimes better, which makes preferring Bonferroni a habit rather than a choice.
""",
                    },
                    {
                        "q": "In the Holm table, rank 3 gives a raw product of 0.1160 and rank 4 gives 0.0993. Why is a running maximum applied?",
                        "opts": [
                            "Otherwise a weaker result would carry a smaller adjusted value than a stronger one",
                            "Otherwise the adjusted values could exceed 1, which no probability may do",
                            "Otherwise the adjusted values would not agree with the raw p-values they came from",
                            "Otherwise the procedure would reject more hypotheses than the step-down rule allows",
                        ],
                        "a": 0,
                        "whys": [
                            "The multiplier falls faster than the p-value rises, so the raw products can decrease, and a threshold drawn between them would reject the weaker result while retaining the stronger.",
                            "Exceeding 1 is a real hazard and it is handled, but by the separate cap that takes the minimum with 1.0. The running maximum addresses the ordering.",
                            "The adjusted values deliberately differ from the raw p-values — multiplying them is the adjustment. Agreement with the raw values is not something to preserve.",
                            "The step-down rule and the adjusted values agree once the running maximum is in place; without it they disagree in both directions, not only by rejecting more.",
                        ],
                        "why": r"""
The products at ranks 3, 4 and 5 are 0.1160, 0.0993 and 0.0804, falling as the raw
p-values 0.0290, 0.0331 and 0.0402 rise, because the multiplier drops from 4 to 3 to
2. Left alone, `fastmath` would look more significant than `pgo` after adjustment
despite being less significant before it. Taking the running maximum forces the
adjusted values to rise with the raw ones, and it is what makes them agree with the
step-down decisions exactly.
""",
                    },
                    {
                        "q": "After Holm correction none of the twelve flags is significant. What may the write-up claim?",
                        "opts": [
                            "That this sweep established no flag effect, with the smallest adjusted p-value reported",
                            "That the flags make no difference to the runtime of the program",
                            "That flag8, at a raw p of 0.013, is significant before correction and so is worth reporting as a finding",
                            "That the correction was too strict, since two flags were significant on their own",
                        ],
                        "a": 0,
                        "whys": [
                            "It reports what the study did and did not establish, and the adjusted value lets a reader see how far from the threshold the best candidate fell.",
                            "That is a claim of no effect, which needs its own design with a stated margin. The sweep is equally consistent with a small real effect it was too small to find.",
                            "Reporting the raw value as a finding is what the correction exists to prevent — it was chosen as the smallest of twelve, and the selection is the whole problem.",
                            "The correction did what it promised on data with no effect in it. Calling it too strict because it refused two false alarms inverts the test of whether it works.",
                        ],
                        "why": r"""
The data here were generated with no effect anywhere, so a procedure rejecting nothing
is a procedure working correctly. The honest sentence names the negative result and
gives the reader the number: the smallest Holm-adjusted p-value in the sweep is 0.156.
That is informative — it says the best candidate was not close — and it lets someone
else size a bigger study with module 2's `runs_needed`. Reporting the raw 0.013 as a
finding would be the exact error the whole module is about.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The p-value and the step-down, five holes deep",
                "minutes": 9,
                "lang": "python",
                "caption": "family.py — the permutation p-value, the step-down rule, and the adjusted column",
                "brief": r'''
Three short functions decide whether a sweep found anything. Each hole below is a
place where a reasonable-looking alternative changes a p-value, a threshold or an
ordering without changing whether the code runs.

Nothing is executed here. Filled in correctly, six flags with p-values of 0.0021,
0.0090, 0.0290, 0.0331, 0.0402 and 0.2100 give two rejections and an adjusted column
that never decreases.
''',
                "listing": r'''
def permutation_p(a, b, trials=999, seed=451):
    """Two-sided p-value by relabelling, with the conservative correction."""
    rng = random.Random(seed)
    observed = ___
    pool = list(a) + list(b)
    hits = 0
    for _ in range(trials):
        rng.shuffle(pool)
        if abs(mean(pool[:len(a)]) - mean(pool[len(a):])) >= observed - 1e-12:
            hits += 1
    return (1 + hits) / (___)


def holm(pvalues, alpha=0.05):
    """Step-down rejections, in the original order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: ___)
    reject = [False] * m
    for rank, i in enumerate(order):
        if pvalues[i] > alpha / (___):
            break
        reject[i] = True
    return reject


def holm_adjusted(pvalues):
    """Adjusted p-values, in the original order and never decreasing."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted, running = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        running = ___(running, min(1.0, (m - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted
''',
                "blanks": [
                    {
                        "prompt": "The observed statistic, against which every shuffle is compared. What makes the test two-sided?",
                        "hole": "?",
                        "opts": ["abs(mean(a) - mean(b))", "mean(a) - mean(b)", "abs(mean(a)) - abs(mean(b))", "mean(a) / mean(b)"],
                        "a": 0,
                        "why": "Taking the magnitude means a relabelling that pushes the difference the other way counts as equally extreme, which is exactly what a two-sided test asks. The loop already takes the magnitude of each shuffle, so both sides of the comparison have to match.",
                        "whys": [
                            "Taking the magnitude means a relabelling that pushes the difference the other way counts as equally extreme, which is exactly what a two-sided test asks. The loop already takes the magnitude of each shuffle, so both sides of the comparison have to match.",
                            "A signed difference is compared with a magnitude in the loop below, so whenever the observed difference is negative almost every shuffle clears it and the p-value drifts towards 1 regardless of the evidence.",
                            "Taking the magnitude of each mean before subtracting is a different quantity entirely, and for timings, which are all positive, it collapses to the signed difference and carries the same defect.",
                            "A ratio is a perfectly good statistic for a permutation test, but the loop below compares against a difference, so the two sides of the comparison would be measuring different things.",
                        ],
                    },
                    {
                        "prompt": "The denominator of the p-value, given that the observed arrangement counts as one of the relabellings.",
                        "hole": "?",
                        "opts": ["1 + trials", "trials", "1 + hits", "trials + hits"],
                        "a": 0,
                        "why": "The observed labelling is added to both the numerator and the denominator, which is what keeps the smallest attainable p-value at one over trials plus one rather than zero.",
                        "whys": [
                            "The observed labelling is added to both the numerator and the denominator, which is what keeps the smallest attainable p-value at one over trials plus one rather than zero.",
                            "Adding the observed arrangement to the numerator but not the denominator lets the p-value exceed 1 when every shuffle ties, which is not a probability.",
                            "This makes the p-value 1 for every input, since the numerator and denominator are then the same expression, and no comparison could ever be significant.",
                            "This denominator grows with the evidence against the null, so a strongly separated pair of groups is divided by nearly twice the trials and its p-value is halved for no reason.",
                        ],
                    },
                    {
                        "prompt": "The step-down examines the hypotheses in which order?",
                        "hole": "?",
                        "opts": ["pvalues[i]", "-pvalues[i]", "i", "alpha / pvalues[i]"],
                        "a": 0,
                        "why": "Ascending p-value order is what the shrinking divisor is matched to: the strongest evidence faces the strictest threshold, and the procedure stops at the first hypothesis that fails.",
                        "whys": [
                            "Ascending p-value order is what the shrinking divisor is matched to: the strongest evidence faces the strictest threshold, and the procedure stops at the first hypothesis that fails.",
                            "Descending order hands the strictest threshold to the weakest evidence, so the loop breaks on the very first hypothesis in almost every sweep and nothing is ever rejected.",
                            "Leaving the hypotheses in the order they were authored makes the threshold depend on where a comparison happened to sit in the list, so renaming a flag could change the verdict.",
                            "This is descending order again, dressed up as a rate. It sorts the least significant results first and breaks immediately, with the added flaw of dividing by a p-value that can be zero.",
                        ],
                    },
                    {
                        "prompt": "How many hypotheses are still in play when the one at this rank is examined?",
                        "hole": "?",
                        "opts": ["m - rank", "m", "rank + 1", "m - rank - 1"],
                        "a": 0,
                        "why": "At rank 0 all m are live and the threshold is the Bonferroni one; each rejection removes one from the pool, so the divisor falls and the threshold relaxes. That relaxation is the whole of Holm's advantage.",
                        "whys": [
                            "At rank 0 all m are live and the threshold is the Bonferroni one; each rejection removes one from the pool, so the divisor falls and the threshold relaxes. That relaxation is the whole of Holm's advantage.",
                            "Holding every hypothesis against alpha over m is Bonferroni exactly, so the step-down structure is built and then never used. It stays valid and rejects less.",
                            "This runs the divisor the wrong way, starting at 1 and growing, so the smallest p-value is held against the whole of alpha and the largest against alpha over m — a procedure with no error guarantee at all.",
                            "This is off by one and at the last rank divides by zero. It also relaxes the threshold faster than the union bound supports, so the family-wise guarantee no longer holds.",
                        ],
                    },
                    {
                        "prompt": "The adjusted values must never decrease as the raw p-values rise. What enforces that?",
                        "hole": "?",
                        "opts": ["max", "min", "sum", "abs"],
                        "a": 0,
                        "why": "Each adjusted value is the largest product seen so far, so the column can only rise. Without it the products fall from 0.1160 to 0.0993 to 0.0804 while the raw p-values are rising.",
                        "whys": [
                            "Each adjusted value is the largest product seen so far, so the column can only rise. Without it the products fall from 0.1160 to 0.0993 to 0.0804 while the raw p-values are rising.",
                            "Taking the smaller of the two makes the column non-increasing, which is the defect inverted: the least significant hypothesis would end up with the smallest adjusted value in the sweep.",
                            "Accumulating a sum makes the column rise, but it rises by an amount with no meaning, and the total quickly exceeds 1 and stops being interpretable as a p-value at all.",
                            "The magnitude of a product of two non-negative numbers is that product, so this changes nothing and the column still falls where the multiplier shrinks faster than the p-value grows.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "A family of comparisons, corrected",
                "minutes": 50,
                "runtime": "python",
                "brief": r'''
A sweep of twelve flags, none of which does anything, and the machinery that has
to say so. `main.py` already holds `WORKED`, the six p-values from the reading,
and `null_family()`, which regenerates the twelve comparisons exactly.

1. `mean(values)` — the arithmetic mean; empty input is a `ValueError`.

2. `permutation_p(a, b, trials=999, seed=451)` — pool the two groups, shuffle a
   private `random.Random(seed)` `trials` times, split each shuffle at
   `len(a)`, and count the shuffles whose absolute mean difference is at least
   the observed one, allowing `1e-12` of slack. Return
   `(1 + hits) / (1 + trials)`. An empty group or a non-positive `trials` is a
   `ValueError`.

3. `family_error(m, alpha=0.05)` — `1 - (1 - alpha) ** m`. A negative `m` is a
   `ValueError`.

4. `bonferroni(pvalues, alpha=0.05)` — one boolean per p-value, in the original
   order, `True` when it is at most `alpha / m`.

5. `holm(pvalues, alpha=0.05)` — the step-down rule, booleans in the **original**
   order. Examine the p-values in ascending order against `alpha / (m - rank)`
   and stop at the first failure.

6. `holm_adjusted(pvalues)` — the adjusted p-values in the original order: the
   running maximum of `min(1.0, (m - rank) * p)` down the sorted list.

7. `family_report(comparisons, alpha=0.05, trials=999, seed=451)` —
   `comparisons` is a list of `(name, a, b)`. Return a list of
   `{"name", "p", "adjusted", "reject"}` sorted by `p` ascending, then by name.

```text
holm(WORKED)           ->  [True, True, False, False, False, False]
bonferroni(WORKED)     ->  [True, False, False, False, False, False]
holm_adjusted(WORKED)  ->  [0.0126, 0.045, 0.116, 0.116, 0.116, 0.21]
family_error(12)       ->  0.4596...
```

Every comparison in `null_family()` is between two samples from the same
generator, so a correction that rejects any of them is broken. Two of the twelve
have a raw p-value below 0.05, and that is the point of the exercise.
''',
                "hints": [
                    "`rng.shuffle(pool)` shuffles in place, so pool the two groups once outside the loop and let each shuffle overwrite the last.",
                    "The `- 1e-12` slack matters: a shuffle that reproduces the original split must count as at least as extreme, and floating-point sums of the same values need not be bit-identical.",
                    "`sorted(range(m), key=lambda i: pvalues[i])` gives the ranking while keeping the original indices, which is what lets both results come back in the input's order.",
                    "`holm` stops at the first failure — write the loop with a `break`, not with a `continue`, or you are running an unsound procedure that is stricter in places and looser in others.",
                    "`holm_adjusted` and `holm` must agree: a hypothesis is rejected exactly when its adjusted p-value is at most alpha. Check that on `WORKED` before moving on.",
                ],
                "files": [{"name": "main.py", "content": r'''
import random

WORKED = [0.0021, 0.0090, 0.0290, 0.0331, 0.0402, 0.2100]
WORKED_NAMES = ["O3", "lto", "pgo", "unroll", "fastmath", "prefetch"]


def null_family(seed=7, groups=12, n=8):
    """Twelve comparisons in which both groups come from the same generator."""
    rng = random.Random(seed)
    out = []
    for i in range(groups):
        a = [round(100.0 + 12.0 * (rng.random() - 0.5), 3) for _ in range(n)]
        b = [round(100.0 + 12.0 * (rng.random() - 0.5), 3) for _ in range(n)]
        out.append((f"flag{i + 1}", a, b))
    return out


def mean(values):
    """The arithmetic mean."""
    # your code here


def permutation_p(a, b, trials=999, seed=451):
    """Two-sided p-value by relabelling, with the +1 correction."""
    # your code here


def family_error(m, alpha=0.05):
    """The chance of at least one false alarm across m independent tests."""
    # your code here


def bonferroni(pvalues, alpha=0.05):
    """One boolean per p-value, in the original order."""
    # your code here


def holm(pvalues, alpha=0.05):
    """The step-down rule, in the original order."""
    # your code here


def holm_adjusted(pvalues):
    """Adjusted p-values, in the original order and never decreasing."""
    # your code here


def family_report(comparisons, alpha=0.05, trials=999, seed=451):
    """One row per comparison, sorted by p-value."""
    # your code here


if __name__ == "__main__":
    rows = family_report(null_family())
    for row in rows or []:
        print(f"{row['name']:<8} p={row['p']:.3f} adjusted={row['adjusted']:.3f} "
              f"reject={row['reject']}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import random

WORKED = [0.0021, 0.0090, 0.0290, 0.0331, 0.0402, 0.2100]
WORKED_NAMES = ["O3", "lto", "pgo", "unroll", "fastmath", "prefetch"]


def null_family(seed=7, groups=12, n=8):
    """Twelve comparisons in which both groups come from the same generator."""
    rng = random.Random(seed)
    out = []
    for i in range(groups):
        a = [round(100.0 + 12.0 * (rng.random() - 0.5), 3) for _ in range(n)]
        b = [round(100.0 + 12.0 * (rng.random() - 0.5), 3) for _ in range(n)]
        out.append((f"flag{i + 1}", a, b))
    return out


def mean(values):
    """The arithmetic mean."""
    if not values:
        raise ValueError("no values to average")
    return sum(values) / len(values)


def permutation_p(a, b, trials=999, seed=451):
    """Two-sided p-value by relabelling, with the +1 correction."""
    if not a or not b:
        raise ValueError("both groups need at least one observation")
    if trials <= 0:
        raise ValueError("need at least one relabelling")
    rng = random.Random(seed)
    observed = abs(mean(a) - mean(b))
    pool = list(a) + list(b)
    split = len(a)
    hits = 0
    for _ in range(trials):
        rng.shuffle(pool)
        if abs(mean(pool[:split]) - mean(pool[split:])) >= observed - 1e-12:
            hits += 1
    return (1 + hits) / (1 + trials)


def family_error(m, alpha=0.05):
    """The chance of at least one false alarm across m independent tests."""
    if m < 0:
        raise ValueError("a family cannot hold a negative number of tests")
    return 1 - (1 - alpha) ** m


def bonferroni(pvalues, alpha=0.05):
    """One boolean per p-value, in the original order."""
    m = len(pvalues)
    if not m:
        raise ValueError("no p-values to correct")
    return [p <= alpha / m for p in pvalues]


def holm(pvalues, alpha=0.05):
    """The step-down rule, in the original order."""
    m = len(pvalues)
    if not m:
        raise ValueError("no p-values to correct")
    order = sorted(range(m), key=lambda i: pvalues[i])
    reject = [False] * m
    for rank, i in enumerate(order):
        if pvalues[i] > alpha / (m - rank):
            break
        reject[i] = True
    return reject


def holm_adjusted(pvalues):
    """Adjusted p-values, in the original order and never decreasing."""
    m = len(pvalues)
    if not m:
        raise ValueError("no p-values to adjust")
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def family_report(comparisons, alpha=0.05, trials=999, seed=451):
    """One row per comparison, sorted by p-value."""
    if not comparisons:
        raise ValueError("an empty family has nothing to correct")
    names = [name for name, _a, _b in comparisons]
    pvalues = [permutation_p(a, b, trials, seed) for _name, a, b in comparisons]
    adjusted = holm_adjusted(pvalues)
    verdicts = holm(pvalues, alpha)
    rows = [{"name": n, "p": p, "adjusted": adj, "reject": r}
            for n, p, adj, r in zip(names, pvalues, adjusted, verdicts)]
    return sorted(rows, key=lambda row: (row["p"], row["name"]))


if __name__ == "__main__":
    rows = family_report(null_family())
    for row in rows or []:
        print(f"{row['name']:<8} p={row['p']:.3f} adjusted={row['adjusted']:.3f} "
              f"reject={row['reject']}")
'''}],
                "tests": [
                    {"name": "permutation_p is bounded, floored, and never zero", "code": r'''
assert abs(permutation_p([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) - 1.0) < 1e-12, \
    "identical groups: every relabelling ties, so p is 1"
_p = permutation_p([1, 2, 3, 4, 5, 6, 7, 8], [101, 102, 103, 104, 105, 106, 107, 108])
assert abs(_p - 0.001) < 1e-12, f"a total separation reaches the floor 1/(1+999), got {_p!r}"
assert _p >= 1 / (999 + 1) - 1e-12, "a permutation p-value can never be 0"
assert 0.0 < permutation_p([1, 2, 3, 4], [2, 3, 4, 5]) <= 1.0, "p lies in (0, 1]"
for _bad in (([], [1, 2]), ([1, 2], []),):
    try:
        permutation_p(*_bad)
        assert False, f"permutation_p{_bad!r} should raise ValueError"
    except ValueError:
        pass
try:
    permutation_p([1, 2], [3, 4], trials=0)
    assert False, "trials=0 should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "permutation_p is seeded, symmetric, and leaves the global stream alone", "code": r'''
_a, _b = [12.0, 13.5, 11.8, 14.2], [15.1, 16.0, 14.9, 15.7]
assert permutation_p(_a, _b) == permutation_p(_a, _b), "the same seed must give the same p"
assert permutation_p(_a, _b) == permutation_p(_b, _a), \
    "a two-sided test cannot depend on which group was named first"
assert 0.0 < permutation_p(_a, _b, seed=99) <= 1.0, "another seed still gives a valid p-value"
random.seed(3)
_before = random.random()
_p = permutation_p(_a, _b, trials=200)
_after = random.random()
random.seed(3)
assert 0.0 < _p <= 1.0, f"p was {_p!r}"
assert [random.random(), random.random()] == [_before, _after], \
    "permutation_p drew from the global generator — use random.Random(seed)"
'''},
                    {"name": "family_error counts the chance of any false alarm", "code": r'''
assert abs(family_error(1) - 0.05) < 1e-12, "one test is just the significance level"
assert abs(family_error(0)) < 1e-12, "no tests, no false alarms"
assert abs(family_error(12) - (1 - 0.95 ** 12)) < 1e-12, f"got {family_error(12)!r}"
assert abs(family_error(12) - 0.45963991) < 1e-6, "twelve tests raise a false alarm 46% of the time"
assert family_error(20) > family_error(12) > family_error(6), "more tests, more chances"
assert abs(family_error(12, alpha=0.01) - (1 - 0.99 ** 12)) < 1e-12, "alpha is a parameter"
try:
    family_error(-1)
    assert False, "a negative family size should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "bonferroni holds every p-value against alpha over m", "code": r'''
assert bonferroni(WORKED) == [True, False, False, False, False, False], \
    f"got {bonferroni(WORKED)!r}; the threshold is 0.05/6 = 0.008333"
assert bonferroni([0.04]) == [True], "one test, one threshold of 0.05"
assert bonferroni([0.04, 0.04]) == [False, False], "two tests halve the threshold"
assert bonferroni(WORKED, alpha=0.30) == [True, True, True, True, True, False], \
    f"a threshold of 0.30/6 = 0.05 clears all but the last; got {bonferroni(WORKED, alpha=0.30)!r}"
try:
    bonferroni([])
    assert False, "an empty family should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "holm steps down and rejects more than Bonferroni", "code": r'''
assert holm(WORKED) == [True, True, False, False, False, False], f"got {holm(WORKED)!r}"
assert sum(holm(WORKED)) == 2 and sum(bonferroni(WORKED)) == 1, \
    "Holm should find one more than Bonferroni on this sweep"
for _p, _h in zip(bonferroni(WORKED), holm(WORKED)):
    assert not _p or _h, "anything Bonferroni rejects, Holm must reject too"
assert holm([0.01, 0.9, 0.9]) == [True, False, False], "0.01 clears 0.05/3, and 0.9 stops the walk"
assert holm([0.02, 0.9, 0.9]) == [False, False, False], "0.02 misses 0.05/3 = 0.016667 by a little"
'''},
                    {"name": "holm stops at the first failure and retains everything after it", "code": r'''
_p = [0.001, 0.03, 0.04]
assert holm(_p) == [True, False, False], \
    f"0.04 would clear its own threshold of 0.05, but the walk stopped at 0.03: got {holm(_p)!r}"
assert holm([0.04, 0.001, 0.03]) == [False, True, False], \
    "the verdicts come back in the input order however the p-values were arranged"
assert holm(_p, alpha=0.99) == [True, True, True], \
    "with a wide enough alpha nothing fails and everything is rejected"
assert holm([0.9, 0.9, 0.9]) == [False, False, False], "nothing clears the first threshold"
assert holm([0.001, 0.002, 0.003])[0] is True, "the smallest faces alpha/m"
'''},
                    {"name": "holm_adjusted matches the reading and never decreases", "code": r'''
_adj = holm_adjusted(WORKED)
for _got, _want in zip(_adj, [0.0126, 0.045, 0.116, 0.116, 0.116, 0.21]):
    assert abs(_got - _want) < 1e-9, f"adjusted was {_adj!r}"
_sorted_adj = [_adj[i] for i in sorted(range(len(WORKED)), key=lambda i: WORKED[i])]
assert all(x <= y + 1e-15 for x, y in zip(_sorted_adj, _sorted_adj[1:])), \
    f"the adjusted column must never fall as the raw p-values rise: {_sorted_adj!r}"
assert holm_adjusted([0.4, 0.5, 0.9]) == [1.0, 1.0, 1.0], \
    "an adjusted p-value is capped at 1.0"
assert holm(WORKED) == [a <= 0.05 for a in _adj], \
    "the step-down verdicts and the adjusted values have to agree"
'''},
                    {"name": "family_report ranks the sweep and corrects it", "code": r'''
_rows = family_report(null_family())
assert len(_rows) == 12, f"twelve comparisons, got {len(_rows)}"
assert set(_rows[0]) == {"name", "p", "adjusted", "reject"}, f"got {sorted(_rows[0])!r}"
assert [r["p"] for r in _rows] == sorted(r["p"] for r in _rows), "rows come back sorted by p"
assert _rows[0]["name"] == "flag8" and abs(_rows[0]["p"] - 0.013) < 1e-12, \
    f"the smallest raw p is flag8 at 0.013, got {_rows[0]['name']!r} at {_rows[0]['p']!r}"
assert sum(1 for r in _rows if r["p"] < 0.05) == 2, \
    "two of the twelve look significant on their own"
'''},
                    {"name": "Nothing survives correction, because nothing was there", "code": r'''
_rows = family_report(null_family())
assert not any(r["reject"] for r in _rows), \
    "every group came from the same generator, so a rejection here is a false alarm"
assert abs(min(r["adjusted"] for r in _rows) - 0.156) < 1e-9, \
    f"the smallest adjusted p-value is 0.156, got {min(r['adjusted'] for r in _rows)!r}"
assert _rows[0]["adjusted"] > 0.05, "the best candidate is not close to the corrected threshold"
assert abs(family_error(len(_rows)) - 0.45963991) < 1e-6, \
    "twelve uncorrected comparisons would raise a false alarm 46 per cent of the time"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Reproducibility",
            "summary": "A harness that runs the pipeline twice, hashes every stage, and names the step that moved.",
            "concepts": [
                "Reproducible means a stated procedure on stated inputs produces a byte-identical artefact",
                "Determinism is a property of one pipeline step, and it is testable: run it twice and compare digests",
                "A digest needs a canonical serialisation — key order, float formatting and encoding all pinned",
                "An unseeded shuffle is the commonest defect, and a private generator is the fix a global seed only pretends to be",
                "Everything downstream of the first divergent step also diverges, so the first one is the one to repair",
                "A manifest records the digest of every input, parameter and source file the run depended on",
                "Reproducing a number is not validating it — a wrong pipeline reproduces perfectly",
            ],
            "read": [
                {
                    "title": "The same command, twice, and two different numbers",
                    "minutes": 14,
                    "body": r'''
A three-line pipeline. Load forty measurements, split them seventy-thirty into a
development set and a held-out set, report the gap between the two means. On Monday
the gap is $-2.1257$. On Tuesday, from an unchanged working tree and the same
command, it is $-0.8194$.

Nobody edited anything. Both numbers are correct arithmetic on the data that was
loaded. And the study now has no result at all, because a number that changes when
nothing changed cannot be attributed to anything.

## Bisecting a pipeline instead of reading it

The instinct is to read the code until the bug appears. On a three-step pipeline that
works; on the twelve-step one this becomes, it does not. The mechanical approach is
better and scales: run the whole pipeline twice, take a fingerprint of what each step
produced, and find the first step whose two fingerprints disagree.

A fingerprint is a hash of the step's output. It has to be a hash of a **canonical**
rendering of that output, because two structures that mean the same thing must
fingerprint the same, and Python is happy to hand you the same dictionary in two key
orders. More on that below; for now, `digest` turns any nested structure of numbers,
strings, lists and dicts into 64 hex characters.

```python
import hashlib
import json
import random


def canonical(obj):
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, str)):
        return json.dumps(obj)
    if isinstance(obj, float):
        return f"{obj:.12g}"
    if isinstance(obj, list):
        return "[" + ",".join(canonical(x) for x in obj) + "]"
    pairs = sorted(obj.items(), key=lambda kv: str(kv[0]))
    return "{" + ",".join(json.dumps(str(k)) + ":" + canonical(v) for k, v in pairs) + "}"


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def load(_previous=None):
    return [round(100.0 + 12.0 * ((i * 37 % 101) / 100.0 - 0.5), 3) for i in range(40)]


def split(rows):
    shuffled = list(rows)
    random.shuffle(shuffled)
    cut = int(0.7 * len(shuffled))
    return {"train": shuffled[:cut], "test": shuffled[cut:]}


def score(parts):
    train_mean = sum(parts["train"]) / len(parts["train"])
    test_mean = sum(parts["test"]) / len(parts["test"])
    return {"gap": round(train_mean - test_mean, 4)}


def trace(steps):
    out, value = [], None
    for name, fn in steps:
        value = fn(value)
        out.append((name, digest(value)))
    return out


PIPELINE = [("load", load), ("split", split), ("score", score)]
first, second = trace(PIPELINE), trace(PIPELINE)
moved = None
for (name, one), (_same_name, two) in zip(first, second):
    print(f"{name:<7} digests agree: {one == two}")
    if one != two and moved is None:
        moved = name
print("first step that moved:", moved)
```

```text
load    digests agree: True
split   digests agree: False
score   digests agree: False
first step that moved: split
```

`score` disagrees as well, and `score` is entirely deterministic: it reads what
`split` produced, and its output cannot agree once its input does not. Everything
downstream of a divergence diverges with it, which is exactly why the **first**
divergent step is the one to repair. Chasing the last one leads to the innocent
function at the end of the chain, every time.

## What was wrong, and what is not the fix

`random.shuffle` with no generator argument draws from the module-level generator,
which is seeded from the operating system when `random` is first imported. Two runs,
two seeds, two splits, two answers.

The fix that looks obvious is `random.seed(451)` at the top of the script. It works
today and it is fragile in a specific way: the process-wide generator is shared with
everything else in the process, so any other code that draws from it — a library
shuffling something during import, a plotting routine jittering points, a second
analysis added next month — shifts the stream and changes your split without touching
your file. Module 3's bootstrap avoided the same trap for the same reason. Pass a
generator that belongs to the step:

```python
import hashlib
import json
import random


def canonical(obj):
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, str)):
        return json.dumps(obj)
    if isinstance(obj, float):
        return f"{obj:.12g}"
    if isinstance(obj, list):
        return "[" + ",".join(canonical(x) for x in obj) + "]"
    pairs = sorted(obj.items(), key=lambda kv: str(kv[0]))
    return "{" + ",".join(json.dumps(str(k)) + ":" + canonical(v) for k, v in pairs) + "}"


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def load(_previous=None):
    return [round(100.0 + 12.0 * ((i * 37 % 101) / 100.0 - 0.5), 3) for i in range(40)]


def split(rows, seed=451):
    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    cut = int(0.7 * len(shuffled))
    return {"train": shuffled[:cut], "test": shuffled[cut:]}


def score(parts):
    train_mean = sum(parts["train"]) / len(parts["train"])
    test_mean = sum(parts["test"]) / len(parts["test"])
    return {"train_mean": round(train_mean, 4), "test_mean": round(test_mean, 4),
            "gap": round(train_mean - test_mean, 4)}


value = None
for name, fn in [("load", load), ("split", split), ("score", score)]:
    value = fn(value)
    print(f"{name:<7} {digest(value)[:16]}...")
print("gap", value["gap"], " train", value["train_mean"], " test", value["test_mean"])
```

```text
load    9beedd6c56e6d6a4...
split   e520375ca33c7f39...
score   162a5bb16bd6aca9...
gap -2.1257  train 99.3443  test 101.47
```

Those sixteen characters are now the result. Run the pipeline on another machine next
year and a matching `162a5bb1…` says the whole chain reproduced; a different one says
something moved, and the per-step trace says which link.

## Why the serialisation has to be canonical

A hash is defined on bytes, so producing bytes from a Python object is a decision, and
two of the obvious ways are wrong.

Dictionary key order is preserved in Python but is not part of what a dictionary
*means*: `{"a": 2, "b": 1}` and `{"b": 1, "a": 2}` are equal and would hash
differently under `str()`. Sorting the keys removes that.

Float formatting is the other. `0.1 + 0.2` is `0.30000000000000004`, and a pipeline
that computes the same quantity by a different route can land one bit away from a
value it should equal. Formatting to twelve significant digits collapses that
difference before it reaches the hash — a deliberate loss of precision, chosen so that
a digest reports a real change rather than the last bit of a sum.

```python
import json

def canonical(obj):
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, str)):
        return json.dumps(obj)
    if isinstance(obj, float):
        return f"{obj:.12g}"
    if isinstance(obj, list):
        return "[" + ",".join(canonical(x) for x in obj) + "]"
    pairs = sorted(obj.items(), key=lambda kv: str(kv[0]))
    return "{" + ",".join(json.dumps(str(k)) + ":" + canonical(v) for k, v in pairs) + "}"


print(canonical({"b": 1, "a": 2}))
print(canonical({"a": 2, "b": 1}))
print(canonical(0.1 + 0.2), "vs", canonical(0.3))
print("bool before int:", canonical(True), canonical(1))
```

```text
{"a":2,"b":1}
{"a":2,"b":1}
0.3 vs 0.3
bool before int: true 1
```

The last line is the trap that catches everyone once. `isinstance(True, int)` is
`True` in Python, so a type ladder that tests `int` before `bool` renders `True` as
`1`, and a run that stored a flag as a boolean fingerprints identically to one that
stored it as the number one. The bool branch has to come first.

## The manifest

Knowing *that* a result changed is half of it. A manifest records the digest of every
input file, every parameter and every source file the run depended on, so that when
the result moves you can compare two manifests and see which dependency moved with it.
It turns "the number is different" into "the number is different and so is the input
data, and nothing else is", which is a diagnosis.

## The mistakes

**"It reproduces on my machine."** Running the same script twice in the same process
with the same environment tests almost nothing, and it is tempting because it is the
only test that is free. The harness in this module is deliberately more demanding: it
compares per-step digests, so it fails on the unseeded shuffle that a
run-it-twice-and-eyeball-it check would pass whenever the final number happened to
round the same way.

**Reproducing and validating are the same thing.** They are opposites in an
instructive sense: a pipeline that divides by the wrong denominator reproduces
perfectly, for ever, on every machine. Reproducibility is a property of the procedure,
correctness is a property of the answer, and a digest can only speak to the first.
This is also why a reproduced result is not an independent replication, which is a
different study by different people.

## Where this stops holding

Timings never hash equal. A benchmark run is a physical measurement, so a
reproducibility harness for module 3's work has to fingerprint the analysis — the
warm-up rule, the seed, the number of bootstrap trials and the resulting interval —
rather than the milliseconds. What is being claimed is that the same raw samples plus
the same procedure give the same interval, and that is a claim a digest can check.

A digest is also all-or-nothing. It tells you two things differ and never by how much,
so a pipeline whose floats are genuinely allowed to move a little needs a tolerance
comparison beside it; the twelve-digit rounding above buys some slack, and it is slack
rather than a policy.

And environment capture has no bottom. The Python version, the operating system, the
libm the floats went through, the CPU: all of them can change a result, and a manifest
records what you thought to record. What it buys is not certainty, it is a list of
suspects.

The lab for this module, **a re-run harness that finds the step that moved**, builds
`canonical`, `digest`, `trace`, `is_deterministic`, `first_divergent`, `manifest`,
`compare_manifests` and `reproduce`, and runs the broken pipeline above through them
until it names `split`.
''',
                },
            ],
            "quiz": {
                "title": "What a digest can and cannot tell you",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A pipeline's last step gives a different number on two runs. Why hunt for the FIRST step whose digest differs rather than the last?",
                        "opts": [
                            "Every step after a divergence inherits it, so only the first one can be the cause",
                            "The last step is usually the shortest, so a defect there is easier to overlook",
                            "Digests of later steps are less reliable, because they are computed over larger structures",
                            "The first step is the one that reads external files, which is where non-determinism enters",
                        ],
                        "a": 0,
                        "whys": [
                            "A step that consumes a changed input produces a changed output however deterministic it is, so divergence propagates forwards and the earliest one is the only candidate.",
                            "How long a step is has nothing to do with whether it introduced the difference, and a one-line step is perfectly capable of consuming a changed input faithfully.",
                            "A digest over a large structure is exactly as reliable as one over a small structure; that is the property a hash is chosen for.",
                            "Reading a file is one source of non-determinism among several, and in the worked pipeline the load step is the one that reproduces perfectly while the shuffle does not.",
                        ],
                        "why": r"""
Divergence flows downstream. Once `split` produced two different partitions, `score`
was always going to produce two different summaries, and `score` is entirely
deterministic. Chasing the last differing digest leads to the innocent function at the
end of the chain every time. This is why the lab's `first_divergent` returns a name
rather than a list: the list would be the tail of the pipeline, and only its head is
information.
""",
                    },
                    {
                        "q": "The unseeded shuffle is replaced with `random.seed(451)` at the top of the script. What is still wrong?",
                        "opts": [
                            "The stream is shared, so anything else drawing from it shifts every later result",
                            "A fixed seed still produces different sequences on different Python versions",
                            "Seeding once means every shuffle in the program produces the identical order",
                            "Nothing is wrong at all; a module-level seed is the standard way to fix exactly this",
                        ],
                        "a": 0,
                        "whys": [
                            "The process-wide generator belongs to everyone, so a library that draws from it during import, or a second analysis added later, silently changes your split.",
                            "The Mersenne Twister sequence for a given seed is stable across versions, so this particular fear is unfounded — the fragility is about sharing, not versioning.",
                            "Successive draws advance the state, so the second shuffle differs from the first. That is the intended behaviour of a generator and not a defect.",
                            "It is common, and it is the arrangement that breaks the first time somebody adds a call above yours. A generator local to the step cannot be disturbed that way.",
                        ],
                        "why": r"""
`random.seed` sets the state of one generator shared by the whole process. Your split
then depends not only on the seed but on how many values everything else drew before
it, which is a dependency nobody records and nobody expects. `random.Random(451)`
creates a generator owned by that call, so the step reproduces regardless of what else
runs. Module 3 refused the global generator in the bootstrap for exactly this reason,
and the lab's checks enforce it in both places.
""",
                    },
                    {
                        "q": "Why does the canonical form sort dictionary keys before hashing?",
                        "opts": [
                            "Two dicts that are equal must fingerprint equally, and key order is not part of equality",
                            "Sorted keys compress better, which keeps the digest computation fast on large structures",
                            "Python dictionaries have no defined order, so the keys arrive in an arbitrary sequence",
                            "Sorting the keys is what makes the digest independent of the values stored under them",
                        ],
                        "a": 0,
                        "whys": [
                            "The hash is meant to answer whether the artefact changed, and a rearrangement of the same pairs is not a change, so the rendering must not depend on the order.",
                            "Compression has nothing to do with it, and the digest of a canonical string costs the same whatever order the keys were written in.",
                            "Dictionaries have preserved insertion order since Python 3.7, which is precisely why the problem is easy to miss: the order is defined but not meaningful.",
                            "The digest is supposed to depend on the values — that is the whole point. Sorting affects the order the pairs are written in, not whether they are included.",
                        ],
                        "why": r"""
`{"a": 2, "b": 1} == {"b": 1, "a": 2}` is `True`, so the two must produce the same
fingerprint or the harness reports a change where none happened. Insertion order is
preserved by the language and is a property of how the dict was built rather than of
what it holds, which is what makes this trap quiet: it only fires when some
refactoring alters the order things were inserted, and then it fires on an unrelated
commit.
""",
                    },
                    {
                        "q": "In the type ladder inside `canonical`, why must the `bool` branch come before the `int` branch?",
                        "opts": [
                            "`isinstance(True, int)` is True, so an int branch placed first would render True as 1",
                            "`bool` values cannot be rendered by `json.dumps`, so they need handling of their own",
                            "Booleans hash to the same value as integers, which would collide in the digest",
                            "The ladder is checked in reverse, so the last matching branch is the one that applies",
                        ],
                        "a": 0,
                        "whys": [
                            "Python's bool is a subclass of int, so the int test matches a boolean, and a run storing a flag as True would fingerprint identically to one storing the number 1.",
                            "It renders them perfectly well, as true and false. The branch exists to get in first, not to compensate for a gap in the library.",
                            "Nothing is hashed until the whole structure has been rendered to text, so there is no per-value hash for two types to collide in.",
                            "The ladder is a sequence of ifs with returns, so the first matching branch wins. If the last one won, every value would fall through to the dict case.",
                        ],
                        "why": r"""
`bool` is a subclass of `int` in Python, so `isinstance(True, int)` is `True` and an
`int` branch placed first swallows every boolean. The harness would then report that a
run recording `{"tuned": True}` and one recording `{"tuned": 1}` produced identical
artefacts. It is a small thing that costs an afternoon exactly once, and it is the
reason the lab's checks include a boolean and the integer one side by side.
""",
                    },
                    {
                        "q": "A colleague reruns your pipeline and gets your digest exactly. What has been established?",
                        "opts": [
                            "That the procedure is reproducible, which says nothing about whether it is right",
                            "That the analysis is correct, since an independent run agrees with yours",
                            "That the result would hold on a different dataset drawn in the same way as this one",
                            "That the pipeline contains no unseeded randomness anywhere in it",
                        ],
                        "a": 0,
                        "whys": [
                            "A matching digest says the stated procedure on the stated inputs gives the stated artefact, and a pipeline with the wrong denominator satisfies that for ever.",
                            "Agreement between two runs of the same code is not independent evidence about the code. Both runs share every mistake in it.",
                            "A different dataset is a different input, so it would produce a different digest by design. Generalisation is a question about scope, which no hash touches.",
                            "It is good evidence about the paths that ran, and no evidence about a branch neither run took — a seeding defect in an untaken code path survives untouched.",
                        ],
                        "why": r"""
Reproducibility and correctness are separate properties, and only the first is what a
digest can speak to: the same inputs and the same code gave the same artefact.
A systematic error reproduces at least as reliably as a correct calculation. It is
also worth separating this from *replication*, which is a different study, by
different people, that reaches a compatible conclusion — the thing reproducibility is
sometimes mistaken for and the thing that would actually be evidence.
""",
                    },
                    {
                        "q": "How should a reproducibility harness treat module 3's benchmark, whose timings are never the same twice?",
                        "opts": [
                            "Fingerprint the analysis of a stored sample: the warm-up, the seed, the trials, the interval",
                            "Fingerprint the timings after rounding them, which makes repeated runs agree",
                            "Leave benchmarks out of the harness, since a physical measurement cannot be reproducible",
                            "Fingerprint the machine's configuration instead, since that is what determines the timings taken",
                        ],
                        "a": 0,
                        "whys": [
                            "The reproducible claim is that these recorded samples, put through this stated procedure, yield this interval — and every part of that is an artefact a digest can check.",
                            "Rounding does not rescue a fresh measurement: two runs differ by far more than any rounding that would leave the timings meaningful.",
                            "The measurement is not reproducible, but the analysis of it certainly is, and that analysis is where almost every reporting mistake in this course lives.",
                            "A configuration record is a useful part of a manifest and it explains nothing on its own, because the same configuration still produces different timings on every run.",
                        ],
                        "why": r"""
Split the claim in two. *This machine gives these timings* is not reproducible and
never will be. *These recorded timings, with a warm-up of 2, seed 451 and 2000
bootstrap trials, give the interval [1.0891, 1.1128]* is exactly reproducible, and it
is the half where the mistakes are: the warm-up chosen after seeing the data, the seed
that was never written down, the trial count that changed between drafts. Store the
samples, fingerprint the analysis, and the raw measurement becomes an input like any
other.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The canonical form and the bisect, five holes deep",
                "minutes": 9,
                "lang": "python",
                "caption": "harness.py — rendering an artefact to bytes, and finding the step that moved",
                "brief": r'''
A digest is only as good as the rendering underneath it, and a bisect is only useful
if it runs the pipeline twice rather than comparing one run with itself. Each hole
below is a place where a plausible alternative produces a harness that runs and
reports nothing.

Nothing is executed here. Filled in correctly, the unseeded pipeline reports that its
split step moved, and the seeded one reports nothing at all.
''',
                "listing": r'''
def canonical(obj):
    """A deterministic text form: sorted keys, 12 significant digits, no spaces."""
    if obj is None:
        return "null"
    if isinstance(obj, ___):
        return "true" if obj else "false"
    if isinstance(obj, (int, str)):
        return json.dumps(obj)
    if isinstance(obj, float):
        return f"{obj:___}"
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(canonical(x) for x in obj) + "]"
    pairs = ___(obj.items(), key=lambda kv: str(kv[0]))
    return "{" + ",".join(json.dumps(str(k)) + ":" + canonical(v) for k, v in pairs) + "}"


def first_divergent(pipeline):
    """The name of the first step whose two runs disagree, or None."""
    a, b = trace(pipeline), ___
    for (name, one), (_again, two) in zip(a, b):
        if one != two:
            return ___
    return None
''',
                "blanks": [
                    {
                        "prompt": "Which type has to be caught before the int branch below it?",
                        "hole": "?",
                        "opts": ["bool", "int", "str", "(bool, int)"],
                        "a": 0,
                        "why": "Python's bool is a subclass of int, so the branch below matches True and False and would render them as 1 and 0. Catching them first is what keeps a flag distinguishable from the number beside it.",
                        "whys": [
                            "Python's bool is a subclass of int, so the branch below matches True and False and would render them as 1 and 0. Catching them first is what keeps a flag distinguishable from the number beside it.",
                            "This makes the branch fire on every integer, so 7 renders as true and 0 renders as false, and every count in the artefact collapses to a boolean.",
                            "Strings are already handled two lines down, and sending them here renders every non-empty string as true, which loses their contents entirely.",
                            "Naming both types catches the booleans, and also catches every integer along with them, so the specific repair is undone by the second half of the tuple.",
                        ],
                    },
                    {
                        "prompt": "The float format. Which one collapses a last-bit difference without destroying the value?",
                        "hole": "?",
                        "opts": [".12g", ".17g", ".2f", ".3e"],
                        "a": 0,
                        "why": "Twelve significant digits keep far more precision than any measurement carries while rendering 0.30000000000000004 and 0.3 identically, so the digest reports real changes rather than rounding noise.",
                        "whys": [
                            "Twelve significant digits keep far more precision than any measurement carries while rendering 0.30000000000000004 and 0.3 identically, so the digest reports real changes rather than rounding noise.",
                            "Seventeen digits is the round-trip precision of a double, so it preserves exactly the last-bit difference the canonical form exists to absorb, and two routes to the same quantity fingerprint differently.",
                            "Two decimal places is far too coarse: a bootstrap interval of [1.0891, 1.1128] and one of [1.0912, 1.1104] would fingerprint identically, and the harness would miss a genuine change.",
                            "Scientific notation with three digits is coarser still, and it also renders 100.0 and 99.95 the same way, so most of the differences worth catching disappear.",
                        ],
                    },
                    {
                        "prompt": "The pairs of a dict, in an order that does not depend on how the dict was built.",
                        "hole": "?",
                        "opts": ["sorted", "list", "reversed", "iter"],
                        "a": 0,
                        "why": "Two equal dicts must render identically, and insertion order is a fact about how each was assembled rather than about what it holds. Sorting by the key text removes that dependency.",
                        "whys": [
                            "Two equal dicts must render identically, and insertion order is a fact about how each was assembled rather than about what it holds. Sorting by the key text removes that dependency.",
                            "This keeps insertion order, so a refactoring that assigns two fields in the other order changes the digest of an artefact that did not change at all.",
                            "Reversing insertion order is as arbitrary as keeping it, and it rejects the key argument as well, so the line does not even run.",
                            "This yields the pairs in insertion order and ignores the key argument, leaving the digest dependent on assembly order exactly as if nothing had been done.",
                        ],
                    },
                    {
                        "prompt": "The second trace, which is what makes this a test of determinism at all.",
                        "hole": "?",
                        "opts": ["trace(pipeline)", "a", "list(a)", "trace(pipeline[::-1])"],
                        "a": 0,
                        "why": "The pipeline has to be run a second time, from the start, so that a step drawing fresh randomness gets a fresh chance to disagree with itself. Anything derived from the first run compares it with itself.",
                        "whys": [
                            "The pipeline has to be run a second time, from the start, so that a step drawing fresh randomness gets a fresh chance to disagree with itself. Anything derived from the first run compares it with itself.",
                            "Binding the same list to both names compares every digest with itself, so the loop finds nothing and the harness certifies every pipeline as deterministic.",
                            "A copy of the first trace holds the same digests in the same order, so this has exactly the defect above with an extra allocation to disguise it.",
                            "Running the steps backwards feeds each one the wrong input, so the second trace usually crashes and, when it does not, reports the first step as divergent every time.",
                        ],
                    },
                    {
                        "prompt": "What the bisect reports when it finds a disagreement.",
                        "hole": "?",
                        "opts": ["name", "one", "a.index(name)", "(one, two)"],
                        "a": 0,
                        "why": "The caller needs to know which step to repair, so the useful answer is its name. The digests themselves carry no information beyond the fact that they differ.",
                        "whys": [
                            "The caller needs to know which step to repair, so the useful answer is its name. The digests themselves carry no information beyond the fact that they differ.",
                            "This hands back one of the two hashes, which tells the caller nothing about where in the pipeline the problem is and changes on every run.",
                            "The trace holds name and digest pairs rather than bare names, so this raises rather than returning a position, and a position would be less useful than the name anyway.",
                            "Returning the pair of digests confirms they differ, which the caller already knows from the fact that something was returned, and still omits the one thing needed to act.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "A re-run harness that finds the step that moved",
                "minutes": 55,
                "runtime": "python",
                "brief": r'''
`main.py` already holds the pipeline from the reading in two versions: `BROKEN`,
whose `split` draws from the process-wide generator, and `SEEDED`, whose `split`
owns its generator. Build the harness that tells them apart.

1. `canonical(obj)` — a deterministic text rendering. `None` is `"null"`;
   `bool` is `"true"`/`"false"` and must be tested **before** `int`; `int` and
   `str` go through `json.dumps`; `float` is `f"{obj:.12g}"` and a non-finite
   float is a `ValueError`; a `list` or `tuple` is `[a,b,c]` with no spaces; a
   `dict` is `{"k":v,...}` with keys sorted by `str(key)`. Anything else is a
   `TypeError`.

2. `digest(obj)` — the SHA-256 hex digest of `canonical(obj)` encoded as UTF-8.

3. `trace(pipeline)` — `pipeline` is a list of `(name, fn)`. Call the first with
   `None`, feed each result to the next, and return `[(name, digest(output))]`.

4. `is_deterministic(pipeline)` — two traces agree, step for step.

5. `first_divergent(pipeline)` — the name of the first step whose two runs
   disagree, or `None`.

6. `manifest(inputs, params, code)` — `{"input.<key>": digest(value)}` for every
   entry of `inputs`, plus `"params"` and `"code"`.

7. `compare_manifests(a, b)` — the sorted keys whose entries differ, counting a
   key present in only one of them.

8. `reproduce(pipeline, expected)` — run the pipeline once and return
   `(matches, actual_digest)` for its **final** step.

```text
first_divergent(BROKEN)   ->  "split"
first_divergent(SEEDED)   ->  None
trace(SEEDED)[-1][1]      ->  "162a5bb16bd6aca95af837c39a0a342aa11cd6eff9e0a5b9bb97fe54107ad454"
canonical({"b": 1, "a": 2})  ->  '{"a":2,"b":1}'
```

That hex string is the artefact this whole course has been building towards: a
result somebody else can check by running one command.
''',
                "hints": [
                    "Write `canonical` as a ladder of `isinstance` tests with an early return in each, and put `bool` above `int` or every flag renders as a number.",
                    "`hashlib.sha256(text.encode('utf-8')).hexdigest()` — the encoding is part of the specification, not a detail.",
                    "`trace` threads one value through the steps: start at `None`, reassign it in the loop, and append `(name, digest(value))` each time.",
                    "`first_divergent` must call `trace` twice. Comparing a trace with a copy of itself certifies everything as deterministic.",
                    "`compare_manifests` is `sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))` — the union is what catches a key that appeared or vanished.",
                ],
                "files": [{"name": "main.py", "content": r'''
import hashlib
import json
import random


def load(_previous=None):
    """The raw measurements. Deterministic by construction."""
    return [round(100.0 + 12.0 * ((i * 37 % 101) / 100.0 - 0.5), 3) for i in range(40)]


def split_broken(rows):
    """Shuffle and split 70/30, using the process-wide generator."""
    shuffled = list(rows)
    random.shuffle(shuffled)
    cut = int(0.7 * len(shuffled))
    return {"train": shuffled[:cut], "test": shuffled[cut:]}


def split_seeded(rows, seed=451):
    """The same split, from a generator of its own."""
    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    cut = int(0.7 * len(shuffled))
    return {"train": shuffled[:cut], "test": shuffled[cut:]}


def score(parts):
    """The reported statistic."""
    train_mean = sum(parts["train"]) / len(parts["train"])
    test_mean = sum(parts["test"]) / len(parts["test"])
    return {"train_mean": round(train_mean, 4), "test_mean": round(test_mean, 4),
            "gap": round(train_mean - test_mean, 4)}


BROKEN = [("load", load), ("split", split_broken), ("score", score)]
SEEDED = [("load", load), ("split", split_seeded), ("score", score)]
SEEDED_RESULT = "162a5bb16bd6aca95af837c39a0a342aa11cd6eff9e0a5b9bb97fe54107ad454"


def canonical(obj):
    """A deterministic text rendering: sorted keys, 12 significant digits."""
    # your code here


def digest(obj):
    """The SHA-256 hex digest of the canonical rendering."""
    # your code here


def trace(pipeline):
    """(name, digest) for every step, threading one value through."""
    # your code here


def is_deterministic(pipeline):
    """True when two runs agree step for step."""
    # your code here


def first_divergent(pipeline):
    """The name of the first step whose two runs disagree, or None."""
    # your code here


def manifest(inputs, params, code):
    """A digest per input, plus one for the parameters and one for the code."""
    # your code here


def compare_manifests(a, b):
    """The sorted keys whose entries differ."""
    # your code here


def reproduce(pipeline, expected):
    """(matches, actual) for the pipeline's final artefact."""
    # your code here


if __name__ == "__main__":
    for label, pipeline in (("broken", BROKEN), ("seeded", SEEDED)):
        print(label, "first divergent step:", first_divergent(pipeline))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import hashlib
import json
import random


def load(_previous=None):
    """The raw measurements. Deterministic by construction."""
    return [round(100.0 + 12.0 * ((i * 37 % 101) / 100.0 - 0.5), 3) for i in range(40)]


def split_broken(rows):
    """Shuffle and split 70/30, using the process-wide generator."""
    shuffled = list(rows)
    random.shuffle(shuffled)
    cut = int(0.7 * len(shuffled))
    return {"train": shuffled[:cut], "test": shuffled[cut:]}


def split_seeded(rows, seed=451):
    """The same split, from a generator of its own."""
    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    cut = int(0.7 * len(shuffled))
    return {"train": shuffled[:cut], "test": shuffled[cut:]}


def score(parts):
    """The reported statistic."""
    train_mean = sum(parts["train"]) / len(parts["train"])
    test_mean = sum(parts["test"]) / len(parts["test"])
    return {"train_mean": round(train_mean, 4), "test_mean": round(test_mean, 4),
            "gap": round(train_mean - test_mean, 4)}


BROKEN = [("load", load), ("split", split_broken), ("score", score)]
SEEDED = [("load", load), ("split", split_seeded), ("score", score)]
SEEDED_RESULT = "162a5bb16bd6aca95af837c39a0a342aa11cd6eff9e0a5b9bb97fe54107ad454"


def canonical(obj):
    """A deterministic text rendering: sorted keys, 12 significant digits."""
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, str)):
        return json.dumps(obj)
    if isinstance(obj, float):
        if obj != obj or obj in (float("inf"), float("-inf")):
            raise ValueError("a digest cannot be taken of a non-finite float")
        return f"{obj:.12g}"
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(canonical(x) for x in obj) + "]"
    if isinstance(obj, dict):
        pairs = sorted(obj.items(), key=lambda kv: str(kv[0]))
        return "{" + ",".join(json.dumps(str(k)) + ":" + canonical(v) for k, v in pairs) + "}"
    raise TypeError("no canonical form for " + type(obj).__name__)


def digest(obj):
    """The SHA-256 hex digest of the canonical rendering."""
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def trace(pipeline):
    """(name, digest) for every step, threading one value through."""
    if not pipeline:
        raise ValueError("an empty pipeline has nothing to trace")
    out = []
    value = None
    for name, step in pipeline:
        value = step(value)
        out.append((name, digest(value)))
    return out


def is_deterministic(pipeline):
    """True when two runs agree step for step."""
    return trace(pipeline) == trace(pipeline)


def first_divergent(pipeline):
    """The name of the first step whose two runs disagree, or None."""
    a, b = trace(pipeline), trace(pipeline)
    for (name, one), (_again, two) in zip(a, b):
        if one != two:
            return name
    return None


def manifest(inputs, params, code):
    """A digest per input, plus one for the parameters and one for the code."""
    entry = {"input." + str(key): digest(value) for key, value in inputs.items()}
    entry["params"] = digest(params)
    entry["code"] = digest(code)
    return entry


def compare_manifests(a, b):
    """The sorted keys whose entries differ."""
    return sorted(key for key in set(a) | set(b) if a.get(key) != b.get(key))


def reproduce(pipeline, expected):
    """(matches, actual) for the pipeline's final artefact."""
    actual = trace(pipeline)[-1][1]
    return actual == expected, actual


if __name__ == "__main__":
    for label, pipeline in (("broken", BROKEN), ("seeded", SEEDED)):
        print(label, "first divergent step:", first_divergent(pipeline))
'''}],
                "tests": [
                    {"name": "canonical is order-free, bool-aware and space-free", "code": r'''
assert canonical({"b": 1, "a": 2}) == '{"a":2,"b":1}', f"got {canonical({'b': 1, 'a': 2})!r}"
assert canonical({"a": 2, "b": 1}) == canonical({"b": 1, "a": 2}), \
    "two equal dicts must render identically"
assert canonical(True) == "true" and canonical(1) == "1", \
    f"bool must be caught before int: got {canonical(True)!r} and {canonical(1)!r}"
assert canonical(None) == "null", f"got {canonical(None)!r}"
assert canonical([1, 2.5, "a"]) == '[1,2.5,"a"]', f"got {canonical([1, 2.5, 'a'])!r}"
assert canonical({"z": [1], "a": {"k": True}}) == '{"a":{"k":true},"z":[1]}', \
    f"got {canonical({'z': [1], 'a': {'k': True}})!r}"
'''},
                    {"name": "canonical rounds floats and refuses what it cannot render", "code": r'''
assert canonical(0.1 + 0.2) == canonical(0.3) == "0.3", \
    f"twelve significant digits should absorb the last bit: got {canonical(0.1 + 0.2)!r}"
assert canonical(1.0 / 3.0) == "0.333333333333", f"got {canonical(1.0 / 3.0)!r}"
assert canonical(101.47) == "101.47", f"got {canonical(101.47)!r}"
for _bad in (float("nan"), float("inf")):
    try:
        canonical(_bad)
        assert False, f"canonical({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    canonical({1, 2})
    assert False, "a set has no order, so it should raise TypeError"
except TypeError:
    pass
'''},
                    {"name": "digest is 64 hex characters and follows the content", "code": r'''
_d = digest({"gap": -2.1257})
assert isinstance(_d, str) and len(_d) == 64, f"got {_d!r}"
assert all(c in "0123456789abcdef" for c in _d), f"not lower-case hex: {_d!r}"
assert digest({"a": 1, "b": 2}) == digest({"b": 2, "a": 1}), "key order must not matter"
assert digest({"a": 1}) != digest({"a": 2}), "a changed value must change the digest"
assert digest({"tuned": True}) != digest({"tuned": 1}), \
    "a flag and the number one must not fingerprint the same"
assert digest([1, 2]) != digest([2, 1]), "a list is ordered, so its order counts"
'''},
                    {"name": "trace threads one value through and names every step", "code": r'''
_t = trace(SEEDED)
assert [name for name, _d in _t] == ["load", "split", "score"], f"got {_t!r}"
assert all(len(d) == 64 for _n, d in _t), "every step is fingerprinted"
assert len(set(d for _n, d in _t)) == 3, "the three steps produce three different artefacts"
assert _t[0][1] == digest(load()), "the first step is called with None and its output hashed"
try:
    trace([])
    assert False, "an empty pipeline should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The unseeded shuffle is found, and only it", "code": r'''
assert first_divergent(BROKEN) == "split", f"got {first_divergent(BROKEN)!r}"
assert first_divergent(SEEDED) is None, f"got {first_divergent(SEEDED)!r}"
assert is_deterministic(SEEDED) is True, "the seeded pipeline reproduces"
assert is_deterministic(BROKEN) is False, "the broken one does not"
assert first_divergent([("load", load)]) is None, "a deterministic step on its own is fine"
assert first_divergent([("load", load), ("split", split_broken)]) == "split", \
    "the divergence is still located when it is the last step"
'''},
                    {"name": "The seeded pipeline reproduces the recorded artefact", "code": r'''
assert trace(SEEDED)[-1][1] == SEEDED_RESULT, f"got {trace(SEEDED)[-1][1]!r}"
_ok, _actual = reproduce(SEEDED, SEEDED_RESULT)
assert _ok is True and _actual == SEEDED_RESULT, f"got {(_ok, _actual)!r}"
_bad_ok, _bad_actual = reproduce(SEEDED, "0" * 64)
assert _bad_ok is False and _bad_actual == SEEDED_RESULT, \
    "a mismatch still hands back what the run actually produced"
_result = score(split_seeded(load()))
assert abs(_result["gap"] + 2.1257) < 1e-9, f"the seeded split gives a gap of -2.1257, got {_result!r}"
assert abs(_result["test_mean"] - 101.47) < 1e-9, f"got {_result!r}"
'''},
                    {"name": "manifest records a digest for every dependency", "code": r'''
_m = manifest({"rows": load()}, {"seed": 451, "warmup": 2}, "print(1)")
assert sorted(_m) == ["code", "input.rows", "params"], f"got {sorted(_m)!r}"
assert _m["input.rows"] == digest(load()), "each input is fingerprinted on its own"
assert _m["params"] == digest({"warmup": 2, "seed": 451}), "parameter order must not matter"
assert _m["code"] == digest("print(1)")
_two = manifest({"a": [1], "b": [2]}, {}, "x")
assert sorted(_two) == ["code", "input.a", "input.b", "params"], f"got {sorted(_two)!r}"
'''},
                    {"name": "compare_manifests names exactly what moved", "code": r'''
_a = manifest({"rows": load()}, {"seed": 451}, "print(1)")
_b = manifest({"rows": load()}, {"seed": 452}, "print(1)")
assert compare_manifests(_a, _a) == [], "a manifest agrees with itself"
assert compare_manifests(_a, _b) == ["params"], f"only the seed moved; got {compare_manifests(_a, _b)!r}"
_c = manifest({"rows": load()[:-1]}, {"seed": 451}, "print(2)")
assert compare_manifests(_a, _c) == ["code", "input.rows"], f"got {compare_manifests(_a, _c)!r}"
_d = manifest({"rows": load(), "extra": [0]}, {"seed": 451}, "print(1)")
assert compare_manifests(_a, _d) == ["input.extra"], \
    f"a key present in only one of them counts as a difference; got {compare_manifests(_a, _d)!r}"
'''},
                    {"name": "A changed input moves every digest downstream of it", "code": r'''
def _shorter_load(_previous=None):
    return load()[:-1]

_variant = [("load", _shorter_load), ("split", split_seeded), ("score", score)]
_before = dict(trace(SEEDED))
_after = dict(trace(_variant))
assert first_divergent(_variant) is None, "the variant is still deterministic"
for _name in ("load", "split", "score"):
    assert _before[_name] != _after[_name], \
        f"the {_name} digest should have moved when the input changed"
assert reproduce(_variant, SEEDED_RESULT)[0] is False, \
    "the recorded artefact must not reproduce from different data"
'''},
                ],
            },
        },
    ],
    # ------------------------------------------------------------ capstone
    "capstone": {
        "title": "Capstone — a benchmark study somebody else can check",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Four systems, two workloads, twelve runs of each: ninety-six timings, already
recorded in `RUNS`. Turn them into a study report that states what was found,
what was not resolved, and a fingerprint that lets anybody re-run the whole
thing and confirm they got your numbers.

Three files, and the dependency points one way.

## `analysis.py` — the estimators

- `mean(values)`, `percentile(values, q)` (linear interpolation between order
  statistics), `median(values)`. Empty input, or a `q` outside `[0, 1]`, is a
  `ValueError`.
- `bootstrap_ratio_ci(base, variant, trials=2000, seed=451, level=0.95)` —
  inside each trial resample **base first**, then variant, both to their own
  length, from one private `random.Random(seed)`; take
  `median(resampled_base) / median(resampled_variant)`; return the percentile
  interval as a tuple.
- `permutation_p(a, b, trials=999, seed=451)` — pool, shuffle a private
  generator `trials` times, split at `len(a)`, count shuffles whose absolute
  mean difference is at least the observed one within `1e-12`, and return
  `(1 + hits) / (1 + trials)`.
- `holm_adjusted(pvalues)` — the running maximum of `min(1.0, (m - rank) * p)`
  down the sorted list, returned in the original order.

## `study.py` — the study layer

- `drop_warmup(timings, k)` — a new list without the first `k`; a negative `k`
  or one that would empty the list is a `ValueError`.
- `cells(runs)` — the sorted `(system, workload)` pairs that were run.
- `missing_cells(runs)` — the sorted pairs in the cross product of the systems
  present with the workloads present that no run covers.
- `canonical(obj)` and `digest(obj)` — module 5's rendering: `None` is `"null"`,
  `bool` before `int`, `int` and `str` through `json.dumps`, `float` as
  `f"{obj:.12g}"`, lists and tuples as `[a,b,c]`, dicts as `{"k":v,...}` with
  keys sorted by `str(key)`, anything else a `TypeError`; `digest` is the
  SHA-256 hex of the UTF-8 canonical text.
- `compare(runs, baseline="base", warmup=2, alpha=0.05, trials=2000, seed=451)`
  — one row per non-baseline cell, sorted by `(system, workload)`:
  `{"system", "workload", "speedup", "ci", "p", "resolved", "adjusted",
  "significant"}`. `speedup` is `median(base) / median(variant)` on the
  warm samples, `ci` is the bootstrap ratio interval, `resolved` is `True` when
  that interval excludes `1.0`, `adjusted` is the Holm-adjusted p-value **across
  every row of the family**, and `significant` is `adjusted <= alpha`. A
  workload with no baseline cell is a `ValueError`.
- `study_report(runs, baseline="base", warmup=2, alpha=0.05, trials=2000,
  seed=451)` — `{"baseline", "warmup", "alpha", "trials", "seed", "missing",
  "comparisons", "digest"}`, where `digest` is the digest of that same dict
  **without** its own `digest` key.

## `main.py`

Print the table and the digest. It is the only file that prints.

```text
dfa     json    speedup 1.1015  ci [1.0891, 1.1128]  p 0.001  adj 0.0060  significant
dfa     regex   speedup 1.1585  ci [1.1473, 1.1693]  p 0.001  adj 0.0060  significant
hybrid  json    speedup 1.0456  ci [1.0354, 1.0560]  p 0.027  adj 0.1080  not significant
hybrid  regex   speedup 1.0054  ci [0.9928, 1.0164]  p 0.534  adj 1.0000  unresolved
simd    json    speedup 1.0000  ci [0.9892, 1.0097]  p 0.820  adj 1.0000  unresolved
simd    regex   speedup 1.0018  ci [0.9919, 1.0109]  p 0.747  adj 1.0000  unresolved
digest  b4fe41c7283497d22eb0b05d9f91f1aba6fb7d17d9f9006a7ff5e0ad058f551c
```

Read the third row before you start. `hybrid` on `json` has an interval that
excludes 1.0, so the direction is resolved, and a raw p-value of 0.027, which
would be a finding on its own. Its Holm-adjusted p-value is 0.108, so across
the six comparisons that were actually made it is not one. The interval is
uncorrected and the p-value is corrected; they are answering different
questions, and a report that shows both is telling the truth about a result
that is genuinely on the edge.
''',
        "deliverables": [
            "`analysis.py` — mean, percentile, median, the bootstrap ratio interval, the permutation p-value and the Holm adjustment, importing nothing from the study layer",
            "`study.py` — warm-up removal, the design audit, the canonical digest, and the comparison table across the whole family",
            "`main.py` — a demo that prints the six-row table and the report digest",
            "A speedup with a bootstrap interval for every variant on every workload, computed on the ratio itself",
            "Holm-adjusted p-values across all six comparisons, and a `significant` flag that uses them rather than the raw ones",
            "A `digest` over the whole report that reproduces byte for byte, and a `missing` list naming any cell nobody ran",
        ],
        "constraints": [
            "Standard library only; `hashlib`, `json`, `math` and `random` are all you need",
            "`analysis.py` must not import `study.py` — the dependency points one way only",
            "Every generator is a private `random.Random(seed)`; nothing may draw from the process-wide stream",
            "Importing `analysis.py` or `study.py` must print nothing and touch no global state",
            "The report's `digest` is taken over the report without its own `digest` key, or it could never be computed",
        ],
        "rubric": [
            {"criterion": "Estimator correctness", "weight": 35,
             "evidence": "The percentile, the ratio interval and the permutation p-value reproduce the stated numbers, including the interval floor of one over trials plus one."},
            {"criterion": "Family-wise correction", "weight": 20,
             "evidence": "Holm is applied across all six comparisons at once, the adjusted column never decreases, and significance is read from it rather than from the raw p-values."},
            {"criterion": "Reproducibility", "weight": 25,
             "evidence": "The report digest is identical across runs and across processes, moves when the warm-up or seed moves, and no function draws from the process-wide generator."},
            {"criterion": "Design audit and honest reporting", "weight": 20,
             "evidence": "missing_cells names any unrun combination, unresolved intervals are reported as unresolved rather than as no difference, and the layering holds."},
        ],
        "hints": [
            "Build `analysis.py` first and check `median` against a list you can order by eye; every later number rests on it.",
            "`bootstrap_ratio_ci` draws base then variant inside one trial from one generator — two separate loops would pair up draws that never happened together.",
            "Compute every row's p-value first, then hand the whole list to `holm_adjusted` once. Correcting each row on its own is a family of size one, six times over.",
            "`study_report` builds the dict, digests a copy of it, and then adds the digest — a dict cannot contain its own fingerprint.",
            "If the digest does not match, print `canonical(report)` and compare it with a colleague's: the first differing character names the field that moved.",
        ],
        "files": [
            {"name": "analysis.py", "content": r'''
import random


def mean(values):
    """The arithmetic mean."""


def percentile(values, q):
    """The q quantile, by linear interpolation between order statistics."""


def median(values):
    """The 0.5 quantile."""


def bootstrap_ratio_ci(base, variant, trials=2000, seed=451, level=0.95):
    """The percentile interval for median(base) / median(variant)."""


def permutation_p(a, b, trials=999, seed=451):
    """Two-sided p-value by relabelling, with the +1 correction."""


def holm_adjusted(pvalues):
    """Adjusted p-values, in the original order and never decreasing."""
'''},
            {"name": "study.py", "content": r'''
import hashlib
import json

from analysis import (bootstrap_ratio_ci, holm_adjusted, mean, median,
                      percentile, permutation_p)

RUNS = [
    {"system": "base", "workload": "json",
     "timings": [44.1, 42.0, 41.6, 40.9, 41.2, 41.0, 41.5, 40.8, 41.3, 47.9, 41.1, 41.4]},
    {"system": "base", "workload": "regex",
     "timings": [61.2, 58.4, 55.9, 55.2, 55.6, 55.4, 55.8, 55.1, 55.7, 62.3, 55.3, 55.5]},
    {"system": "dfa", "workload": "json",
     "timings": [96.4, 51.2, 37.6, 37.2, 37.9, 37.4, 37.1, 37.8, 43.6, 37.3, 37.5, 37.0]},
    {"system": "dfa", "workload": "regex",
     "timings": [110.5, 66.1, 48.2, 47.6, 48.5, 47.9, 47.4, 48.3, 54.1, 47.7, 48.0, 47.5]},
    {"system": "hybrid", "workload": "json",
     "timings": [50.1, 44.2, 39.6, 39.1, 39.8, 39.3, 39.0, 39.7, 45.2, 39.2, 39.4, 39.5]},
    {"system": "hybrid", "workload": "regex",
     "timings": [60.8, 57.2, 55.1, 54.6, 55.9, 54.9, 55.4, 54.4, 56.1, 60.2, 54.8, 55.6]},
    {"system": "simd", "workload": "json",
     "timings": [45.0, 42.3, 41.4, 40.7, 41.6, 41.1, 40.9, 41.8, 46.8, 41.0, 41.3, 41.2]},
    {"system": "simd", "workload": "regex",
     "timings": [62.0, 58.1, 55.5, 55.0, 55.9, 55.2, 55.6, 54.9, 56.2, 61.8, 55.1, 55.4]},
]


def drop_warmup(timings, k):
    """A new list without the first k runs."""


def cells(runs):
    """The sorted (system, workload) pairs that were run."""


def missing_cells(runs):
    """The sorted pairs of the cross product that nobody ran."""


def canonical(obj):
    """A deterministic text rendering: sorted keys, 12 significant digits."""


def digest(obj):
    """The SHA-256 hex digest of the canonical rendering."""


def compare(runs, baseline="base", warmup=2, alpha=0.05, trials=2000, seed=451):
    """One row per non-baseline cell, corrected across the whole family."""


def study_report(runs, baseline="base", warmup=2, alpha=0.05, trials=2000, seed=451):
    """The whole study, with a digest of itself."""
'''},
            {"name": "main.py", "content": r'''
from study import RUNS, study_report

report = study_report(RUNS)
if report:
    for row in report["comparisons"]:
        verdict = ("significant" if row["significant"]
                   else "not significant" if row["resolved"] else "unresolved")
        print(f"{row['system']:<8}{row['workload']:<7} speedup {row['speedup']:.4f}  "
              f"ci [{row['ci'][0]:.4f}, {row['ci'][1]:.4f}]  p {row['p']:.3f}  "
              f"adj {row['adjusted']:.4f}  {verdict}")
    print("digest ", report["digest"])
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "analysis.py", "content": r'''
import random


def mean(values):
    """The arithmetic mean."""
    if not values:
        raise ValueError("no values to average")
    return sum(values) / len(values)


def percentile(values, q):
    """The q quantile, by linear interpolation between order statistics."""
    if not values:
        raise ValueError("no values to take a percentile of")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must lie in [0, 1]")
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    position = q * (len(xs) - 1)
    low = int(position)
    high = min(low + 1, len(xs) - 1)
    weight = position - low
    return xs[low] * (1 - weight) + xs[high] * weight


def median(values):
    """The 0.5 quantile."""
    return percentile(values, 0.5)


def bootstrap_ratio_ci(base, variant, trials=2000, seed=451, level=0.95):
    """The percentile interval for median(base) / median(variant)."""
    if not base or not variant:
        raise ValueError("both groups need at least one observation")
    if trials <= 0:
        raise ValueError("need at least one bootstrap trial")
    if not 0.0 < level < 1.0:
        raise ValueError("a confidence level lies strictly between 0 and 1")
    rng = random.Random(seed)
    ratios = []
    for _ in range(trials):
        resampled_base = [rng.choice(base) for _ in base]
        resampled_variant = [rng.choice(variant) for _ in variant]
        ratios.append(median(resampled_base) / median(resampled_variant))
    tail = (1 - level) / 2
    return percentile(ratios, tail), percentile(ratios, 1 - tail)


def permutation_p(a, b, trials=999, seed=451):
    """Two-sided p-value by relabelling, with the +1 correction."""
    if not a or not b:
        raise ValueError("both groups need at least one observation")
    if trials <= 0:
        raise ValueError("need at least one relabelling")
    rng = random.Random(seed)
    observed = abs(mean(a) - mean(b))
    pool = list(a) + list(b)
    split = len(a)
    hits = 0
    for _ in range(trials):
        rng.shuffle(pool)
        if abs(mean(pool[:split]) - mean(pool[split:])) >= observed - 1e-12:
            hits += 1
    return (1 + hits) / (1 + trials)


def holm_adjusted(pvalues):
    """Adjusted p-values, in the original order and never decreasing."""
    m = len(pvalues)
    if not m:
        raise ValueError("no p-values to adjust")
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted
'''},
            {"name": "study.py", "content": r'''
import hashlib
import json

from analysis import (bootstrap_ratio_ci, holm_adjusted, mean, median,
                      percentile, permutation_p)

RUNS = [
    {"system": "base", "workload": "json",
     "timings": [44.1, 42.0, 41.6, 40.9, 41.2, 41.0, 41.5, 40.8, 41.3, 47.9, 41.1, 41.4]},
    {"system": "base", "workload": "regex",
     "timings": [61.2, 58.4, 55.9, 55.2, 55.6, 55.4, 55.8, 55.1, 55.7, 62.3, 55.3, 55.5]},
    {"system": "dfa", "workload": "json",
     "timings": [96.4, 51.2, 37.6, 37.2, 37.9, 37.4, 37.1, 37.8, 43.6, 37.3, 37.5, 37.0]},
    {"system": "dfa", "workload": "regex",
     "timings": [110.5, 66.1, 48.2, 47.6, 48.5, 47.9, 47.4, 48.3, 54.1, 47.7, 48.0, 47.5]},
    {"system": "hybrid", "workload": "json",
     "timings": [50.1, 44.2, 39.6, 39.1, 39.8, 39.3, 39.0, 39.7, 45.2, 39.2, 39.4, 39.5]},
    {"system": "hybrid", "workload": "regex",
     "timings": [60.8, 57.2, 55.1, 54.6, 55.9, 54.9, 55.4, 54.4, 56.1, 60.2, 54.8, 55.6]},
    {"system": "simd", "workload": "json",
     "timings": [45.0, 42.3, 41.4, 40.7, 41.6, 41.1, 40.9, 41.8, 46.8, 41.0, 41.3, 41.2]},
    {"system": "simd", "workload": "regex",
     "timings": [62.0, 58.1, 55.5, 55.0, 55.9, 55.2, 55.6, 54.9, 56.2, 61.8, 55.1, 55.4]},
]


def drop_warmup(timings, k):
    """A new list without the first k runs."""
    if k < 0:
        raise ValueError("a warm-up cannot be negative")
    if k >= len(timings):
        raise ValueError(f"dropping {k} of {len(timings)} runs leaves nothing to report")
    return list(timings[k:])


def cells(runs):
    """The sorted (system, workload) pairs that were run."""
    return sorted({(r["system"], r["workload"]) for r in runs})


def missing_cells(runs):
    """The sorted pairs of the cross product that nobody ran."""
    present = set(cells(runs))
    systems = sorted({system for system, _w in present})
    workloads = sorted({workload for _s, workload in present})
    return sorted((s, w) for s in systems for w in workloads if (s, w) not in present)


def canonical(obj):
    """A deterministic text rendering: sorted keys, 12 significant digits."""
    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, str)):
        return json.dumps(obj)
    if isinstance(obj, float):
        if obj != obj or obj in (float("inf"), float("-inf")):
            raise ValueError("a digest cannot be taken of a non-finite float")
        return f"{obj:.12g}"
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(canonical(x) for x in obj) + "]"
    if isinstance(obj, dict):
        pairs = sorted(obj.items(), key=lambda kv: str(kv[0]))
        return "{" + ",".join(json.dumps(str(k)) + ":" + canonical(v) for k, v in pairs) + "}"
    raise TypeError("no canonical form for " + type(obj).__name__)


def digest(obj):
    """The SHA-256 hex digest of the canonical rendering."""
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def compare(runs, baseline="base", warmup=2, alpha=0.05, trials=2000, seed=451):
    """One row per non-baseline cell, corrected across the whole family."""
    warm = {(r["system"], r["workload"]): drop_warmup(r["timings"], warmup) for r in runs}
    wanted = sorted(key for key in warm if key[0] != baseline)
    rows = []
    for system, workload in wanted:
        if (baseline, workload) not in warm:
            raise ValueError(f"no {baseline!r} runs for the {workload!r} workload")
        base = warm[(baseline, workload)]
        variant = warm[(system, workload)]
        low, high = bootstrap_ratio_ci(base, variant, trials, seed)
        rows.append({
            "system": system,
            "workload": workload,
            "speedup": median(base) / median(variant),
            "ci": [low, high],
            "p": permutation_p(base, variant, 999, seed),
            "resolved": not (low <= 1.0 <= high),
        })
    if not rows:
        raise ValueError("no variants to compare against the baseline")
    for row, adjusted in zip(rows, holm_adjusted([row["p"] for row in rows])):
        row["adjusted"] = adjusted
        row["significant"] = adjusted <= alpha
    return rows


def study_report(runs, baseline="base", warmup=2, alpha=0.05, trials=2000, seed=451):
    """The whole study, with a digest of itself."""
    report = {
        "baseline": baseline,
        "warmup": warmup,
        "alpha": alpha,
        "trials": trials,
        "seed": seed,
        "missing": missing_cells(runs),
        "comparisons": compare(runs, baseline, warmup, alpha, trials, seed),
    }
    report["digest"] = digest(report)
    return report
'''},
            {"name": "main.py", "content": r'''
from study import RUNS, study_report

report = study_report(RUNS)
if report:
    for row in report["comparisons"]:
        verdict = ("significant" if row["significant"]
                   else "not significant" if row["resolved"] else "unresolved")
        print(f"{row['system']:<8}{row['workload']:<7} speedup {row['speedup']:.4f}  "
              f"ci [{row['ci'][0]:.4f}, {row['ci'][1]:.4f}]  p {row['p']:.3f}  "
              f"adj {row['adjusted']:.4f}  {verdict}")
    print("digest ", report["digest"])
'''},
        ],
        "tests": [
            {"name": "The estimators reproduce the numbers the study rests on", "code": r'''
from analysis import bootstrap_ratio_ci, mean, median, percentile
_warm_base = [41.6, 40.9, 41.2, 41.0, 41.5, 40.8, 41.3, 47.9, 41.1, 41.4]
_warm_dfa = [37.6, 37.2, 37.9, 37.4, 37.1, 37.8, 43.6, 37.3, 37.5, 37.0]
assert abs(median(_warm_base) - 41.25) < 1e-9, f"got {median(_warm_base)!r}"
assert abs(mean(_warm_base) - 41.87) < 1e-9, f"got {mean(_warm_base)!r}"
assert abs(percentile(_warm_base, 0.95) - 45.065) < 1e-9, f"got {percentile(_warm_base, 0.95)!r}"
assert abs(percentile([1, 2, 3, 4], 0.0) - 1) < 1e-12 and abs(percentile([1, 2, 3, 4], 1.0) - 4) < 1e-12
_low, _high = bootstrap_ratio_ci(_warm_base, _warm_dfa)
assert abs(_low - 1.0890927866547992) < 1e-9, f"low end was {_low!r}"
assert abs(_high - 1.112751677852349) < 1e-9, f"high end was {_high!r}"
assert _low <= median(_warm_base) / median(_warm_dfa) <= _high, \
    "the interval must contain the point estimate it was built around"
for _bad in ([], [1.0]):
    try:
        percentile(_bad, 1.5)
        assert False, "a q outside [0, 1] should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "The permutation p-value and the Holm adjustment behave", "code": r'''
from analysis import holm_adjusted, permutation_p
_a = [41.6, 40.9, 41.2, 41.0, 41.5, 40.8, 41.3, 47.9, 41.1, 41.4]
_b = [37.6, 37.2, 37.9, 37.4, 37.1, 37.8, 43.6, 37.3, 37.5, 37.0]
assert abs(permutation_p(_a, _b) - 0.001) < 1e-12, \
    f"a clean separation reaches the floor 1/(1+999), got {permutation_p(_a, _b)!r}"
assert permutation_p(_a, _b) == permutation_p(_b, _a), "a two-sided test is symmetric"
assert abs(permutation_p([1.0, 2.0], [1.0, 2.0]) - 1.0) < 1e-12, "identical groups give p = 1"
assert permutation_p(_a, _b) >= 1 / 1000 - 1e-12, "a permutation p-value is never 0"
_adj = holm_adjusted([0.0021, 0.0090, 0.0290, 0.0331, 0.0402, 0.2100])
for _got, _want in zip(_adj, [0.0126, 0.045, 0.116, 0.116, 0.116, 0.21]):
    assert abs(_got - _want) < 1e-9, f"adjusted was {_adj!r}"
assert holm_adjusted([0.4, 0.5, 0.9]) == [1.0, 1.0, 1.0], "an adjusted p-value is capped at 1"
'''},
            {"name": "The design audit reads the table of runs", "code": r'''
from study import RUNS, cells, drop_warmup, missing_cells
assert drop_warmup([1, 2, 3, 4], 2) == [3, 4], "the warm-up comes off the front"
_copy = drop_warmup([1, 2, 3], 0)
assert _copy == [1, 2, 3] and _copy is not None, "k = 0 returns a copy of the list"
for _bad in (-1, 3, 4):
    try:
        drop_warmup([1, 2, 3], _bad)
        assert False, f"drop_warmup with k={_bad} should raise ValueError"
    except ValueError:
        pass
assert len(cells(RUNS)) == 8, f"four systems by two workloads, got {len(cells(RUNS))}"
assert cells(RUNS)[0] == ("base", "json"), f"sorted pairs; got {cells(RUNS)[0]!r}"
assert missing_cells(RUNS) == [], "every combination was run"
_gap = [r for r in RUNS if not (r["system"] == "simd" and r["workload"] == "regex")]
assert missing_cells(_gap) == [("simd", "regex")], f"got {missing_cells(_gap)!r}"
'''},
            {"name": "compare produces the six rows the study reports", "code": r'''
from study import RUNS, compare
_rows = compare(RUNS)
assert len(_rows) == 6, f"three variants on two workloads, got {len(_rows)}"
assert [(r["system"], r["workload"]) for r in _rows] == \
    [("dfa", "json"), ("dfa", "regex"), ("hybrid", "json"),
     ("hybrid", "regex"), ("simd", "json"), ("simd", "regex")], \
    f"rows come back sorted; got {[(r['system'], r['workload']) for r in _rows]!r}"
assert set(_rows[0]) == {"system", "workload", "speedup", "ci", "p", "resolved",
                         "adjusted", "significant"}, f"got {sorted(_rows[0])!r}"
assert abs(_rows[0]["speedup"] - 1.1014686248331107) < 1e-12, f"got {_rows[0]['speedup']!r}"
assert abs(_rows[1]["speedup"] - 1.1584984358706985) < 1e-12, f"got {_rows[1]['speedup']!r}"
assert [r["significant"] for r in _rows] == [True, True, False, False, False, False], \
    f"only the dfa rows survive correction; got {[r['significant'] for r in _rows]!r}"
assert [r["resolved"] for r in _rows] == [True, True, True, False, False, False], \
    f"got {[r['resolved'] for r in _rows]!r}"
'''},
            {"name": "The hybrid row is the one the correction changes", "code": r'''
from study import RUNS, compare
_rows = compare(RUNS)
_hybrid = next(r for r in _rows if r["system"] == "hybrid" and r["workload"] == "json")
assert abs(_hybrid["p"] - 0.027) < 1e-12, f"its raw p-value is 0.027, got {_hybrid['p']!r}"
assert _hybrid["p"] < 0.05, "on its own it would be a finding"
assert abs(_hybrid["adjusted"] - 0.108) < 1e-9, f"its adjusted p-value is 0.108, got {_hybrid['adjusted']!r}"
assert _hybrid["significant"] is False, "across six comparisons it is not"
assert _hybrid["resolved"] is True, "its interval still excludes 1.0"
assert _hybrid["ci"][0] > 1.0, f"got {_hybrid['ci']!r}"
_sorted_adj = sorted(r["adjusted"] for r in _rows)
assert all(x <= y + 1e-15 for x, y in zip(_sorted_adj, _sorted_adj[1:])), \
    "the adjusted values must never fall as the raw p-values rise"
'''},
            {"name": "The report fingerprints itself and reproduces", "code": r'''
from study import RUNS, canonical, digest, study_report
_report = study_report(RUNS)
assert set(_report) == {"baseline", "warmup", "alpha", "trials", "seed", "missing",
                        "comparisons", "digest"}, f"got {sorted(_report)!r}"
assert _report["digest"] == \
    "b4fe41c7283497d22eb0b05d9f91f1aba6fb7d17d9f9006a7ff5e0ad058f551c", \
    f"got {_report['digest']!r}"
_without = {k: v for k, v in _report.items() if k != "digest"}
assert digest(_without) == _report["digest"], "the digest covers the report minus itself"
assert study_report(RUNS)["digest"] == _report["digest"], "two runs must agree exactly"
assert study_report(RUNS, warmup=3)["digest"] != _report["digest"], \
    "a different warm-up is a different study"
assert study_report(RUNS, seed=452)["digest"] != _report["digest"], \
    "a different seed is a different study"
assert canonical({"b": 1, "a": 2}) == '{"a":2,"b":1}', f"got {canonical({'b': 1, 'a': 2})!r}"
assert canonical(True) == "true" and canonical(1) == "1", "bool must be tested before int"
'''},
            {"name": "Nothing draws from the process-wide generator, and the layering holds", "code": r'''
import random
from study import RUNS, study_report
random.seed(11)
_before = random.random()
_digest = study_report(RUNS)["digest"]
_after = random.random()
random.seed(11)
assert len(_digest) == 64, f"the report digest is 64 hex characters, got {_digest!r}"
assert [random.random(), random.random()] == [_before, _after], \
    "the study consumed values from the global generator — every seed must be private"
_analysis = open("analysis.py").read()
_study = open("study.py").read()
assert "import study" not in _analysis and "from study" not in _analysis, \
    "analysis.py must not depend on study.py — the dependency points one way"
assert "from analysis" in _study or "import analysis" in _study, \
    "study.py should build on the estimators rather than re-implement them"
for _name, _src in (("analysis.py", _analysis), ("study.py", _study)):
    assert "print(" not in _src, f"{_name} is a library; the printing belongs in main.py"
    assert "random.seed(" not in _src, f"{_name} must not reseed the process-wide generator"
'''},
        ],
    },
}
