"""CS101 — Introduction to Programming. Reference author module."""

COURSE = {
    "id": "CS101",
    "title": "Introduction to Programming",
    "year": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "▶",
    "summary": (
        "The first course of the degree. You go from typing a single expression to "
        "writing a small multi-file program that reads data, computes over it and "
        "persists results — and you learn to read the errors you cause along the way."
    ),
    "outcomes": [
        "Translate a plain-language rule into an expression that evaluates correctly",
        "Choose between if/elif/else, for and while for a given repetition problem",
        "Decompose a task into functions that return values instead of printing them",
        "Use lists and dictionaries to hold and aggregate structured data",
        "Read and write text and JSON files without leaking file handles",
        "Read a traceback and locate the defect it names",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Downey, *Think Python*, 3rd ed. — chapters 1-12",
        "Python Tutorial, docs.python.org — sections 3-7",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Values, expressions and output",
            "summary": "Numbers, strings, names, and getting results onto the screen.",
            "concepts": [
                "Literals and the four core types: int, float, str, bool",
                "Assignment binds a name to a value; names are not boxes",
                "Operator precedence, integer vs float division, the modulo operator",
                "String formatting with f-strings, including `:.2f` for fixed decimals",
                "Comments explain *why*; the code already says what",
                "Reading a NameError / TypeError traceback from the bottom up",
            ],
            "lab": {
                "title": "Trip cost calculator",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
A car burns `litres_per_100km` litres for every 100 km driven. The three
constants at the top of `main.py` describe one trip. Compute three new
variables from them — do not type the answers in by hand:

- `litres_used` — litres burned across the whole trip
- `fuel_cost` — what those litres cost
- `cost_per_km` — the fuel cost spread over each kilometre

Then print exactly these four lines, money and distance formatted as shown:

```text
Distance: 435.0 km
Litres: 27.84
Fuel cost: 552.62
Cost per km: 1.27
```

`{value:.2f}` inside an f-string rounds to two decimals; `{value:.1f}` to one.
''',
                "files": [{"name": "main.py", "content": r'''
distance_km = 435.0
litres_per_100km = 6.4
price_per_litre = 19.85

# 1. litres_used  — 100 km costs litres_per_100km litres
# 2. fuel_cost    — litres times the price per litre
# 3. cost_per_km  — fuel_cost shared over distance_km
# 4. print the four lines from the task, using f-strings
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
distance_km = 435.0
litres_per_100km = 6.4
price_per_litre = 19.85

litres_used = distance_km / 100 * litres_per_100km
fuel_cost = litres_used * price_per_litre
cost_per_km = fuel_cost / distance_km

print(f"Distance: {distance_km:.1f} km")
print(f"Litres: {litres_used:.2f}")
print(f"Fuel cost: {fuel_cost:.2f}")
print(f"Cost per km: {cost_per_km:.2f}")
'''}],
                "hints": [
                    "435 km is 4.35 lots of 100 km, so `distance_km / 100 * litres_per_100km`.",
                    "Build each line with an f-string: `print(f\"Litres: {litres_used:.2f}\")`.",
                    "`cost_per_km` divides the *cost* by the distance, not the litres.",
                ],
                "tests": [
                    {"name": "litres_used is computed, not typed", "code": r'''
assert abs(litres_used - 27.84) < 1e-9, f"litres_used is {litres_used!r}, expected 27.84"
_src = open("main.py").read()
assert "27.84" not in _src, "Compute litres_used from the constants instead of typing 27.84"
'''},
                    {"name": "fuel_cost multiplies by the price", "code": r'''
assert abs(fuel_cost - 552.624) < 1e-9, f"fuel_cost is {fuel_cost!r}, expected 552.624"
'''},
                    {"name": "cost_per_km spreads cost over distance", "code": r'''
assert abs(cost_per_km - 1.2704) < 1e-9, f"cost_per_km is {cost_per_km!r}, expected 1.2704"
'''},
                    {"name": "All four lines, formatted", "code": r'''
for _line in ["Distance: 435.0 km", "Litres: 27.84", "Fuel cost: 552.62", "Cost per km: 1.27"]:
    assert _line in _out, f"Missing line: {_line}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Control flow: choosing and repeating",
            "summary": "Conditions, loops, and the accumulator patterns built from them.",
            "concepts": [
                "Booleans and the comparison / logical operators",
                "if / elif / else runs exactly one branch — the first that matches",
                "Indentation *is* the block structure in Python",
                "`for` walks a known sequence; `while` repeats on a condition",
                "Accumulator patterns: running total, running best, counter",
                "`break` and `continue`, and why an unreachable base case hangs the tab",
            ],
            "lab": {
                "title": "Collatz chains",
                "runtime": "python",
                "minutes": 35,
                "brief": r'''
The Collatz rule: from `n`, go to `n / 2` when `n` is even, or `3n + 1` when it
is odd. Every start value seen so far eventually reaches 1.

Write two functions.

**`collatz_steps(n)`** — how many rule applications it takes to reach 1.

```text
collatz_steps(1)  ->   0     already there
collatz_steps(6)  ->   8     6 3 10 5 16 8 4 2 1
collatz_steps(27) -> 111
```

Raise `ValueError` when `n` is less than 1 — the rule says nothing about those.

**`longest_under(limit)`** — the start value below `limit` with the longest
chain, as a `(n, steps)` tuple. When two start values tie, return the smaller.

```text
longest_under(10)   -> (9, 19)
longest_under(1000) -> (871, 178)
```
''',
                "files": [{"name": "main.py", "content": r'''
def collatz_steps(n):
    """Number of Collatz steps from n down to 1. ValueError when n < 1."""
    # your code here


def longest_under(limit):
    """(n, steps) for the longest chain starting below limit; ties -> smaller n."""
    # your code here


print(collatz_steps(6))
print(longest_under(1000))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def collatz_steps(n):
    """Number of Collatz steps from n down to 1. ValueError when n < 1."""
    if n < 1:
        raise ValueError("n must be 1 or greater")
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def longest_under(limit):
    """(n, steps) for the longest chain starting below limit; ties -> smaller n."""
    best_n = 0
    best_steps = -1
    for n in range(1, limit):
        steps = collatz_steps(n)
        if steps > best_steps:
            best_n = n
            best_steps = steps
    return (best_n, best_steps)


print(collatz_steps(6))
print(longest_under(1000))
'''}],
                "hints": [
                    "Validate first, then loop: `if n < 1: raise ValueError(...)`.",
                    "Inside the loop, reassign n and add one to a counter — `n = n // 2 if n % 2 == 0 else 3 * n + 1`.",
                    "For the tie rule, use a strict `>` when comparing to the best so far: an equal chain never replaces the earlier (smaller) n.",
                ],
                "tests": [
                    {"name": "Known chain lengths", "code": r'''
for _n, _want in [(1, 0), (2, 1), (6, 8), (7, 16), (27, 111)]:
    _got = collatz_steps(_n)
    assert _got == _want, f"collatz_steps({_n}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "Refuses n below 1", "code": r'''
for _bad in (0, -1, -99):
    try:
        collatz_steps(_bad)
        assert False, f"collatz_steps({_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "longest_under finds the record holder", "code": r'''
assert longest_under(10) == (9, 19), f"longest_under(10) gave {longest_under(10)!r}"
assert longest_under(1000) == (871, 178), f"longest_under(1000) gave {longest_under(1000)!r}"
'''},
                    {"name": "Ties keep the smaller start value", "code": r'''
_n, _s = longest_under(3)
assert (_n, _s) == (2, 1), f"longest_under(3) gave {(_n, _s)!r}, expected (2, 1)"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Functions and decomposition",
            "summary": "Naming a piece of work, returning a value, and composing the pieces.",
            "concepts": [
                "`def`, parameters, arguments, and the difference between them",
                "`return` hands a value back; a function with no return gives None",
                "`return` is not `print` — only returned values compose",
                "Default and keyword arguments",
                "Local scope: names created inside a function do not escape it",
                "Docstrings, and building one function out of another",
            ],
            "lab": {
                "title": "Text statistics",
                "runtime": "python",
                "minutes": 35,
                "brief": r'''
Four small functions that build on each other. Each one **returns** its result.

**`normalise(text)`** — split on whitespace, lowercase each word, and strip the
punctuation `.,!?;:()` from both ends. Drop anything left empty. Returns a list.

```text
normalise("The cat, the HAT!")  ->  ["the", "cat", "the", "hat"]
```

**`word_frequencies(text)`** — a dict of word to how many times it appears.

```text
word_frequencies("Go go GO!")  ->  {"go": 3}
```

**`top_n(freqs, n)`** — the `n` most frequent `(word, count)` pairs, biggest
first, ties broken alphabetically.

```text
top_n({"a": 3, "c": 1, "b": 3}, 2)  ->  [("a", 3), ("b", 3)]
```

**`average_word_length(text)`** — mean word length rounded to 2 decimals, and
`0.0` for text with no words.

Build the last three on top of `normalise` rather than repeating its logic.
''',
                "files": [{"name": "main.py", "content": r'''
PUNCTUATION = ".,!?;:()"


def normalise(text):
    """Lowercased words with edge punctuation removed."""
    # your code here


def word_frequencies(text):
    """word -> count."""
    # your code here


def top_n(freqs, n):
    """The n biggest (word, count) pairs; ties alphabetical."""
    # your code here


def average_word_length(text):
    """Mean word length to 2 decimals, or 0.0 when there are no words."""
    # your code here


sample = "The quick brown fox. The lazy dog! The end."
print(word_frequencies(sample))
print(top_n(word_frequencies(sample), 3))
print(average_word_length(sample))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
PUNCTUATION = ".,!?;:()"


def normalise(text):
    """Lowercased words with edge punctuation removed."""
    words = []
    for raw in text.split():
        word = raw.lower().strip(PUNCTUATION)
        if word:
            words.append(word)
    return words


def word_frequencies(text):
    """word -> count."""
    freqs = {}
    for word in normalise(text):
        freqs[word] = freqs.get(word, 0) + 1
    return freqs


def top_n(freqs, n):
    """The n biggest (word, count) pairs; ties alphabetical."""
    ranked = sorted(freqs.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:n]


def average_word_length(text):
    """Mean word length to 2 decimals, or 0.0 when there are no words."""
    words = normalise(text)
    if not words:
        return 0.0
    return round(sum(len(word) for word in words) / len(words), 2)


sample = "The quick brown fox. The lazy dog! The end."
print(word_frequencies(sample))
print(top_n(word_frequencies(sample), 3))
print(average_word_length(sample))
'''}],
                "hints": [
                    "`raw.lower().strip(PUNCTUATION)` does both jobs in one expression.",
                    "The counting pattern: `freqs[word] = freqs.get(word, 0) + 1`.",
                    "`sorted(freqs.items(), key=lambda pair: (-pair[1], pair[0]))` sorts by count descending, then word ascending.",
                    "Guard the average against division by zero *before* you divide.",
                ],
                "tests": [
                    {"name": "normalise lowercases and strips", "code": r'''
_got = normalise("The cat, the HAT!")
assert _got == ["the", "cat", "the", "hat"], f"Got {_got!r}"
assert normalise("") == [], "No words means an empty list"
assert normalise("...") == [], "A word that is only punctuation should be dropped"
'''},
                    {"name": "word_frequencies counts", "code": r'''
assert word_frequencies("Go go GO!") == {"go": 3}, f'Got {word_frequencies("Go go GO!")!r}'
_r = word_frequencies("The quick brown fox. The lazy dog! The end.")
assert _r["the"] == 3 and _r["end"] == 1 and _r["fox"] == 1, f"Got {_r!r}"
assert word_frequencies("") == {}, "Empty text gives an empty dict"
'''},
                    {"name": "top_n ranks and breaks ties", "code": r'''
assert top_n({"a": 3, "c": 1, "b": 3}, 2) == [("a", 3), ("b", 3)], "Ties go alphabetical"
assert top_n({"a": 1}, 5) == [("a", 1)], "Asking for more than exists returns everything"
assert top_n({}, 3) == [], "Nothing to rank"
'''},
                    {"name": "average_word_length", "code": r'''
assert average_word_length("aa bbbb") == 3.0, f'Got {average_word_length("aa bbbb")!r}'
assert average_word_length("") == 0.0, "Empty text averages 0.0, it must not crash"
assert average_word_length("abc.") == 3.0, "Punctuation is stripped before measuring"
'''},
                    {"name": "The later functions reuse normalise", "code": r'''
_calls = []
_real = normalise
def _spy(text):
    _calls.append(text)
    return _real(text)
normalise = _spy
word_frequencies("a b")
average_word_length("a b")
normalise = _real
assert len(_calls) >= 2, "word_frequencies and average_word_length should both call normalise"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Collections, files and JSON",
            "summary": "Holding structured records, then getting them onto and off disk.",
            "concepts": [
                "Lists, indexing, slicing, and iteration order",
                "Dictionaries as records: key access, `.get`, `.items()`",
                "A list of dicts is the workhorse shape for tabular data",
                "`with open(...)` closes the file even when the block raises",
                "`json.dump` / `json.load` for structure that survives a restart",
                "Handling `FileNotFoundError` instead of crashing on a first run",
            ],
            "lab": {
                "title": "Score records",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
A results file holds one competitor per line: `name,score,team`.

**`parse_line(line)`** — turn one line into `{"name": ..., "score": int, "team": ...}`.
Return `None` for anything malformed: wrong field count, empty name or team, or a
score that is not a whole number. Surrounding spaces are trimmed.

```text
parse_line(" Ada , 90 , red ")  ->  {"name": "Ada", "score": 90, "team": "red"}
parse_line("Ada,ninety,red")    ->  None
parse_line("Ada,90")            ->  None
```

**`load_records(path)`** — every valid record in the file, in file order. Blank
lines and malformed lines are skipped. A missing file gives `[]`, not a crash.

**`team_totals(records)`** — `{team: summed score}`.

**`save_summary(path, totals)`** — write the totals dict to `path` as JSON.
''',
                "files": [{"name": "main.py", "content": r'''
import json


def parse_line(line):
    """One CSV line -> record dict, or None when it is malformed."""
    # your code here


def load_records(path):
    """Every valid record in the file. Missing file -> []."""
    # your code here


def team_totals(records):
    """team -> total score."""
    # your code here


def save_summary(path, totals):
    """Write the totals dict to path as JSON."""
    # your code here


with open("scores.csv", "w") as f:
    f.write("Ada,90,red\nLinus,75,blue\n\nbroken line\nGrace,88,red\n")

records = load_records("scores.csv")
print(records)
print(team_totals(records))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import json


def parse_line(line):
    """One CSV line -> record dict, or None when it is malformed."""
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 3:
        return None
    name, score, team = parts
    if not name or not team:
        return None
    if not score.lstrip("-").isdigit():
        return None
    return {"name": name, "score": int(score), "team": team}


def load_records(path):
    """Every valid record in the file. Missing file -> []."""
    records = []
    try:
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                record = parse_line(line)
                if record is not None:
                    records.append(record)
    except FileNotFoundError:
        return []
    return records


def team_totals(records):
    """team -> total score."""
    totals = {}
    for record in records:
        totals[record["team"]] = totals.get(record["team"], 0) + record["score"]
    return totals


def save_summary(path, totals):
    """Write the totals dict to path as JSON."""
    with open(path, "w") as f:
        json.dump(totals, f)


with open("scores.csv", "w") as f:
    f.write("Ada,90,red\nLinus,75,blue\n\nbroken line\nGrace,88,red\n")

records = load_records("scores.csv")
print(records)
print(team_totals(records))
'''}],
                "hints": [
                    "`[part.strip() for part in line.split(\",\")]` trims every field at once.",
                    "`score.lstrip(\"-\").isdigit()` accepts negative whole numbers and rejects `ninety`.",
                    "Wrap the whole `with open(...)` block in `try` / `except FileNotFoundError`.",
                    "`totals.get(team, 0) + score` is the accumulate-into-a-dict pattern again.",
                ],
                "tests": [
                    {"name": "parse_line accepts and trims", "code": r'''
assert parse_line(" Ada , 90 , red ") == {"name": "Ada", "score": 90, "team": "red"}, \
    f'Got {parse_line(" Ada , 90 , red ")!r}'
assert parse_line("Bo,-5,blue")["score"] == -5, "Negative scores are still whole numbers"
'''},
                    {"name": "parse_line rejects malformed lines", "code": r'''
for _bad in ["Ada,90", "Ada,90,red,extra", "Ada,ninety,red", ",90,red", "Ada,90,", "", "broken line"]:
    assert parse_line(_bad) is None, f"parse_line({_bad!r}) should be None"
'''},
                    {"name": "load_records skips junk, keeps order", "code": r'''
with open("t_load.csv", "w") as _f:
    _f.write("Ada,90,red\n\nnope\nLinus,75,blue\nBad,x,red\nGrace,88,red\n")
_r = load_records("t_load.csv")
assert [x["name"] for x in _r] == ["Ada", "Linus", "Grace"], f"Got {_r!r}"
assert _r[0]["score"] == 90 and isinstance(_r[0]["score"], int), "Scores come back as ints"
'''},
                    {"name": "Missing file gives an empty list", "code": r'''
assert load_records("definitely-not-here-4711.csv") == [], \
    "A missing file should give [] — catch FileNotFoundError"
'''},
                    {"name": "team_totals sums per team", "code": r'''
_r = [{"name": "A", "score": 90, "team": "red"},
      {"name": "B", "score": 75, "team": "blue"},
      {"name": "C", "score": 88, "team": "red"}]
assert team_totals(_r) == {"red": 178, "blue": 75}, f"Got {team_totals(_r)!r}"
assert team_totals([]) == {}, "No records means no totals"
'''},
                    {"name": "save_summary writes real JSON", "code": r'''
import json as _json
save_summary("t_summary.json", {"red": 178, "blue": 75})
with open("t_summary.json") as _f:
    assert _json.load(_f) == {"red": 178, "blue": 75}, "The file should contain plain JSON"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — personal expense ledger",
        "runtime": "python",
        "minutes": 240,
        "brief": r'''
Everything in the course, in one small program split across two files.
`expenses.py` holds the logic and is what the checks import; `main.py` is a
demo script that uses it.

## `Expense(description, amount, category, month)`

Stores the four values as attributes, with `category` lowercased and stripped
and `amount` kept as a float. It refuses bad input at construction time:
`ValueError` for an empty/whitespace description, and for an amount that is
zero or negative. `str(expense)` gives `"Coffee: 45.00 (food)"`.

## `Ledger()`

- `add(expense)` — append it.
- `total()` — every amount summed; `0` for an empty ledger.
- `by_category()` — `{category: summed amount}`.
- `top_category()` — the category with the largest total, ties broken
  alphabetically; `None` when the ledger is empty.
- `month_total(month)` — the total for one month string, e.g. `"2026-03"`.
- `save(path)` / `Ledger.load(path)` — round-trip through JSON. `load` is a
  **classmethod** returning a new `Ledger`, and a missing file gives an empty
  one rather than an exception.
- `report()` — a multi-line string: one `category` + amount line per category
  sorted alphabetically, then a final `TOTAL` line.

## Suggested order

`Expense` and its validation first, then `add` / `total` / `by_category`, then
the two lookups, then persistence, and `report()` last. The checks are ordered
the same way, so they light up roughly in the order you build.
''',
        "deliverables": [
            "`expenses.py` — the `Expense` and `Ledger` classes, importable with no side effects",
            "`main.py` — a demo run that adds several expenses, prints the report, saves and reloads",
            "Input validation that raises `ValueError` rather than storing nonsense",
            "JSON persistence that round-trips a ledger without losing precision",
            "A `report()` string a human can read in a terminal",
        ],
        "constraints": [
            "Standard library only — `json` is the only import you need",
            "`expenses.py` must define classes only; running it must print nothing",
            "No global mutable state: two `Ledger()` objects must not share expenses",
            "A refused `add` must leave the ledger exactly as it was",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 45,
             "evidence": "All automated checks pass, including the empty-ledger and missing-file edge cases."},
            {"criterion": "Validation & error handling", "weight": 20,
             "evidence": "Bad amounts and empty descriptions raise ValueError at construction; load survives a missing file."},
            {"criterion": "Decomposition", "weight": 20,
             "evidence": "top_category and report are built on by_category/total rather than re-summing from scratch."},
            {"criterion": "Readability", "weight": 15,
             "evidence": "Docstrings on every public method, snake_case names, no dead code or debug prints left behind."},
        ],
        "hints": [
            "Validate in `__init__` *before* assigning, so a rejected Expense never half-exists.",
            "`by_category` is the single source of truth — `top_category` and `report` should both call it.",
            "`sorted(cats.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]` gives the top category with the tie rule.",
            "`load` is decorated with `@classmethod` and takes `cls`; build with `cls()` so subclasses keep working.",
        ],
        "files": [
            {"name": "expenses.py", "content": r'''
import json


class Expense:
    def __init__(self, description, amount, category, month):
        pass

    def __str__(self):
        pass


class Ledger:
    def __init__(self):
        self.expenses = []

    def add(self, expense):
        pass

    def total(self):
        pass

    def by_category(self):
        pass

    def top_category(self):
        pass

    def month_total(self, month):
        pass

    def save(self, path):
        pass

    @classmethod
    def load(cls, path):
        pass

    def report(self):
        pass
'''},
            {"name": "main.py", "content": r'''
from expenses import Expense, Ledger

ledger = Ledger()
ledger.add(Expense("Coffee", 45.0, "Food", "2026-03"))
ledger.add(Expense("Train pass", 790.0, "transport", "2026-03"))
ledger.add(Expense("Lunch", 165.5, "food", "2026-04"))

print(ledger.report())
print("Top category:", ledger.top_category())
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "expenses.py", "content": r'''
import json


class Expense:
    """One spend: what it was, how much, which bucket, which month."""

    def __init__(self, description, amount, category, month):
        if not description or not str(description).strip():
            raise ValueError("description is required")
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.description = str(description).strip()
        self.amount = float(amount)
        self.category = str(category).strip().lower()
        self.month = month

    def __str__(self):
        return f"{self.description}: {self.amount:.2f} ({self.category})"


class Ledger:
    """A collection of expenses, with the summaries a budget actually needs."""

    def __init__(self):
        self.expenses = []

    def add(self, expense):
        """Append one Expense to the ledger."""
        self.expenses.append(expense)

    def total(self):
        """Every amount summed."""
        return sum(expense.amount for expense in self.expenses)

    def by_category(self):
        """category -> summed amount."""
        totals = {}
        for expense in self.expenses:
            totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
        return totals

    def top_category(self):
        """Biggest category by total; ties alphabetical. None when empty."""
        totals = self.by_category()
        if not totals:
            return None
        return sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]

    def month_total(self, month):
        """Total for one month string such as 2026-03."""
        return sum(e.amount for e in self.expenses if e.month == month)

    def save(self, path):
        """Write every expense to path as a JSON list."""
        rows = [
            {"description": e.description, "amount": e.amount,
             "category": e.category, "month": e.month}
            for e in self.expenses
        ]
        with open(path, "w") as f:
            json.dump(rows, f)

    @classmethod
    def load(cls, path):
        """Read a ledger back from path. Missing file -> an empty ledger."""
        ledger = cls()
        try:
            with open(path) as f:
                rows = json.load(f)
        except FileNotFoundError:
            return ledger
        for row in rows:
            ledger.add(Expense(row["description"], row["amount"],
                               row["category"], row["month"]))
        return ledger

    def report(self):
        """One line per category, alphabetical, then a TOTAL line."""
        lines = []
        for category, amount in sorted(self.by_category().items()):
            lines.append(f"{category:<14}{amount:>10.2f}")
        lines.append(f"{'TOTAL':<14}{self.total():>10.2f}")
        return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from expenses import Expense, Ledger

ledger = Ledger()
ledger.add(Expense("Coffee", 45.0, "Food", "2026-03"))
ledger.add(Expense("Train pass", 790.0, "transport", "2026-03"))
ledger.add(Expense("Lunch", 165.5, "food", "2026-04"))

print(ledger.report())
print("Top category:", ledger.top_category())

ledger.save("ledger.json")
again = Ledger.load("ledger.json")
print("Reloaded total:", again.total())
'''},
        ],
        "tests": [
            {"name": "Expense stores and normalises its fields", "code": r'''
from expenses import Expense
_e = Expense("  Coffee ", 45, "  Food ", "2026-03")
assert _e.description == "Coffee", f"description is {_e.description!r} — strip it"
assert _e.amount == 45.0 and isinstance(_e.amount, float), "amount should be stored as a float"
assert _e.category == "food", f"category is {_e.category!r} — lowercase and strip it"
assert _e.month == "2026-03"
'''},
            {"name": "Expense refuses bad input", "code": r'''
from expenses import Expense
for _bad in [("", 10, "food", "2026-03"), ("   ", 10, "food", "2026-03"),
             ("Coffee", 0, "food", "2026-03"), ("Coffee", -5, "food", "2026-03")]:
    try:
        Expense(*_bad)
        assert False, f"Expense{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "str() formats an expense", "code": r'''
from expenses import Expense
_s = str(Expense("Coffee", 45.0, "Food", "2026-03"))
assert _s == "Coffee: 45.00 (food)", f"Got {_s!r}, expected: Coffee: 45.00 (food)"
'''},
            {"name": "add and total", "code": r'''
from expenses import Expense, Ledger
_l = Ledger()
assert _l.total() == 0, "An empty ledger totals 0"
_l.add(Expense("a", 10.0, "food", "2026-03"))
_l.add(Expense("b", 2.5, "food", "2026-03"))
assert abs(_l.total() - 12.5) < 1e-9, f"total() gave {_l.total()!r}"
_other = Ledger()
assert _other.total() == 0, "Two ledgers must not share state — use an instance attribute"
'''},
            {"name": "by_category groups the spend", "code": r'''
from expenses import Expense, Ledger
_l = Ledger()
_l.add(Expense("a", 10.0, "Food", "2026-03"))
_l.add(Expense("b", 5.0, "transport", "2026-03"))
_l.add(Expense("c", 2.0, "food", "2026-04"))
assert _l.by_category() == {"food": 12.0, "transport": 5.0}, f"Got {_l.by_category()!r}"
assert Ledger().by_category() == {}, "Empty ledger, empty dict"
'''},
            {"name": "top_category, with the tie rule", "code": r'''
from expenses import Expense, Ledger
assert Ledger().top_category() is None, "An empty ledger has no top category"
_l = Ledger()
_l.add(Expense("a", 10.0, "food", "2026-03"))
_l.add(Expense("b", 30.0, "rent", "2026-03"))
assert _l.top_category() == "rent", f"Got {_l.top_category()!r}"
_tie = Ledger()
_tie.add(Expense("a", 10.0, "zebra", "2026-03"))
_tie.add(Expense("b", 10.0, "apple", "2026-03"))
assert _tie.top_category() == "apple", "Equal totals should break alphabetically"
'''},
            {"name": "month_total filters by month", "code": r'''
from expenses import Expense, Ledger
_l = Ledger()
_l.add(Expense("a", 10.0, "food", "2026-03"))
_l.add(Expense("b", 5.0, "food", "2026-04"))
assert abs(_l.month_total("2026-03") - 10.0) < 1e-9, f"Got {_l.month_total('2026-03')!r}"
assert _l.month_total("1999-01") == 0, "A month with no spend totals 0"
'''},
            {"name": "save / load round-trip", "code": r'''
from expenses import Expense, Ledger
_l = Ledger()
_l.add(Expense("Coffee", 45.0, "food", "2026-03"))
_l.add(Expense("Train", 790.0, "transport", "2026-03"))
_l.save("cap_ledger.json")
_back = Ledger.load("cap_ledger.json")
assert isinstance(_back, Ledger), "load should return a Ledger"
assert abs(_back.total() - 835.0) < 1e-9, f"Reloaded total is {_back.total()!r}"
assert _back.by_category() == {"food": 45.0, "transport": 790.0}, "Categories should survive the trip"
assert Ledger.load("no-such-ledger-9182.json").total() == 0, "A missing file gives an empty ledger"
'''},
            {"name": "report lists categories then TOTAL", "code": r'''
from expenses import Expense, Ledger
_l = Ledger()
_l.add(Expense("a", 10.0, "transport", "2026-03"))
_l.add(Expense("b", 30.0, "food", "2026-03"))
_rep = _l.report()
assert isinstance(_rep, str), "report() returns a string, it does not print"
_lines = _rep.strip().split("\n")
assert len(_lines) == 3, f"Expected 2 category lines and a TOTAL line, got {_lines!r}"
assert _lines[0].startswith("food"), "Categories should be alphabetical"
assert _lines[1].startswith("transport")
assert "TOTAL" in _lines[-1] and "40.00" in _lines[-1], f"Last line was {_lines[-1]!r}"
'''},
            {"name": "expenses.py is import-clean", "code": r'''
_src = open("expenses.py").read()
assert "print(" not in _src, "expenses.py defines classes; the printing belongs in main.py"
'''},
        ],
    },
}
