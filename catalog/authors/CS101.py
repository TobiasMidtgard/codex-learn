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
        "Raise an exception when an argument is outside what a function can accept",
        "Read a comprehension, a generator expression and a `sorted` key, and write the plain ones",
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
            "read": [
                {
                    "title": "Names, values, and three ways to divide",
                    "minutes": 13,
                    "body": r'''
Almost the first thing any program does is give a value a name.

```python
price = 45
```

Two things happen, in this order. The right-hand side is evaluated first, producing the
integer 45. Then the name `price` is made to refer to it. The order matters more than it
looks: it is why `total = total + 1` is legal — the old value of `total` is read before
the name is re-pointed — and why `total = total + 1` on a name that does not exist yet is
a `NameError` rather than a quiet zero.

## Names are labels, not boxes

The box picture says a name is a container you pour a value into. It survives about three
lines of real code. Try it on this:

```python
x = 5
y = x
x = 9
print(y)
```

If names were boxes, `y = x` copied 5 into the `y` box and `x = 9` refilled the `x` box,
so `y` is 5. That happens to be the right answer, and it is right for the wrong reason,
which is the sort of thing that catches up with you later. What actually happened is that
`y = x` pointed `y` at the value `x` was pointing at, and `x = 9` pointed `x` somewhere
else entirely. Nothing was poured, nothing was copied, and `y` was never touched by the
third line.

Hold the label picture and a second question answers itself: nothing anyone does to `x`
afterwards can reach `y`, because `x` is not connected to `y` — they were both connected
to 5, briefly, and one of them moved on.

## Four types, and one way to ask

```python
count   = 12         # int    — a whole number, no size limit
ratio   = 0.75       # float  — a number with a fractional part
label   = "amps"     # str    — text
ready   = True       # bool   — True or False
```

`type(count)` will tell you at any point, and `print(type(count))` is a perfectly
respectable thing to put in a program you are trying to understand. Most beginner
`TypeError`s are a value being one type where the code assumed another, and the fastest
way to find one is to stop guessing which.

The one that surprises people is that `bool` is a kind of `int`: `True + True` is 2. It
is a curiosity here, but it is the reason `sum(flags)` counts how many are true.

## Three ways to divide, and only one of them is division

Split 8735 cents between four people.

```text
8735 /  4   ->  2183.75     true division, always a float
8735 // 4   ->  2183        floor division, the whole part
8735 %  4   ->  3           the remainder
```

`/` is the one that surprises: it hands back a float **even when the division comes out
even**. `6 / 3` is `3.0`, not `3`. If a stray `.0` has appeared in your output, this is
almost always where it came from.

`//` and `%` are a pair, and they come with a guarantee:

```text
(a // b) * b + (a % b)  ==  a

     2183  * 4  +   3   ==  8735
```

That identity is the reason the pair is worth thinking of as one operation. The whole
part and the leftover between them account for every cent; nothing can go missing between
the two lines that compute them. Asserting it, as this module's fill-in-the-blanks
exercise does, is a cheap way to catch a `/` that should have been a `//`.

**Where it stops being obvious.** With a negative numerator, `//` rounds *down*, not
towards zero:

```text
-7 // 2  ->  -4        not -3
-7 %  2  ->   1        not -1
```

The identity still holds — `(-4) * 2 + 1` is `-7` — which is exactly why the results
look odd: Python keeps the guarantee and lets the rounding fall where it must. C and
Java make the opposite choice and truncate towards zero. If you are converting a
formula from one of those languages and the numbers go wrong only for negative inputs,
this is the reason.

## Floats are not decimals

```python
print(0.1 + 0.2)      # 0.30000000000000004
```

This is not a bug and it is not Python. A float is a binary fraction, and 0.1 is no more
expressible in binary than a third is in decimal — you get the nearest available value,
and the error shows up when it is magnified. `round(2.675, 2)` gives `2.67` for the same
reason: the float nearest to 2.675 is a hair below it.

Two habits follow. Compare floats with a tolerance — `abs(a - b) < 1e-9` — rather than
with `==`. And keep money in whole cents as an `int` for as long as you can, converting
to the main unit only at the moment of printing. That is why this module's bill exercise
works in cents throughout and divides by 100 on the last line.

## Getting it on the screen

```python
print(f"Each pays {as_currency:.2f} ({each} cents)")
```

Inside an f-string, `{` starts an expression and `:` starts the *format spec* for it.
`.2f` means fixed-point with exactly two digits after the point, so 21.83 prints as
`21.83` and 21.8 prints as `21.80` — which is what you want for money, where the second
digit has to be there even when it is a zero.

The format spec changes the string, never the value. `f"{7/3:.2f}"` is `"2.33"`, and
`7/3` is still 2.3333333333333335 afterwards. Leave the spec off and you get the float's
own repr — the shortest text that reads back as that exact float — which is honest and
almost never what a reader wants.

## Text is a value too

Strings have methods, and this course leans on four of them:

```python
"  Ada Lovelace ".strip()      ->  "Ada Lovelace"     trim both ends
"Ada Lovelace".lower()         ->  "ada lovelace"     case-folded copy
"Ada Lovelace".split()         ->  ["Ada", "Lovelace"]   split on whitespace
"-".join(["A", "L"])           ->  "A-L"              glue a list back together
```

`split()` with no argument splits on any run of whitespace and drops the empties, which
is the forgiving behaviour you want for text a human typed. `split(",")` with an argument
is strict: it splits on every single comma and *keeps* the empties, which is the
behaviour you want for a data file, where a missing field is information.

The thing to hold on to is that **none of these change the string**. Strings are
immutable; every one of those methods builds and returns a new one. `name.strip()` on a
line by itself is a statement that computes something and throws it away. You have to
catch it: `name = name.strip()`.

## When it goes wrong, read the bottom line first

```text
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    print(f"Each pays {totl}")
                       ^^^^
NameError: name 'totl' is not defined
```

Read it bottom-up. The last line is the *kind* of failure and it is doing real work:
`NameError` means a name was read with nothing bound to it, `TypeError` means an
operation met a value of the wrong type, `ZeroDivisionError` means what it says. Above
it is the line number where it happened. Only above that is the call history, and on a
one-file program it is usually one line long and tells you nothing you did not know.

`NameError` has two usual causes and it is worth knowing both, because they need
different fixes: a misspelling — `totl` for `total` — and an assignment that sits inside
an `if` or a loop that never ran, so the name was never created at all.
''',
                },
            ],
            "quiz": {
                "title": "Names, types, and the shape of a number",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What does `7 / 2` evaluate to?",
                        "opts": ["`3.5`", "`3`", "`1`", "`3.0`"],
                        "a": 0,
                        "why": r"""
A single `/` is true division and it always hands back a float, even when the
division comes out even — `6 / 3` is `3.0`, not `3`. The whole-number answer `3`
is what `7 // 2` gives, and `1` is what `7 % 2` gives: the quotient and the
remainder, the pair you get from long division. Reaching for `/` when you wanted a
whole count is the most common way a stray `.0` ends up in printed output.
""",
                    },
                    {
                        "q": "After `x = 5`, then `y = x`, then `x = 9` — what is `y`?",
                        "opts": ["`5`", "`9`", "`None`", "A NameError, because `y` was never assigned a value of its own"],
                        "a": 0,
                        "why": r"""
`y = x` binds `y` to the value `x` was pointing at *at that moment*, which is 5.
The later `x = 9` does not modify anything; it re-points the name `x` at a
different value and leaves `y` exactly where it was. This is what people mean by
"names are not boxes": nothing was poured into `y` that could later be stirred by
someone else writing to `x`.
""",
                    },
                    {
                        "q": "What does `print(f\"{7/3:.2f}\")` put on the screen?",
                        "opts": ["`2.33`", "`2.3`", "`2.3333333333333335`", "`0.33`"],
                        "a": 0,
                        "why": r"""
`:.2f` means fixed-point with two digits after the decimal, so the value is
rounded for display: `2.33`. `:.1f` would give `2.3`, and leaving the format spec
off entirely prints the float's own repr, `2.3333333333333335` — the shortest
string that reads back as this exact float, seventeen significant digits here,
which is almost never what a reader wants. Note the value
itself is untouched; only the string built from it is rounded.
""",
                    },
                    {
                        "q": "You have a whole number of seconds and want the seconds part of an `mm:ss` display. Which expression?",
                        "opts": [
                            "`total_seconds % 60`",
                            "`total_seconds // 60`",
                            "`total_seconds / 60`",
                            "`60 % total_seconds`",
                        ],
                        "a": 0,
                        "why": r"""
`%` is the remainder after dividing, which is exactly "what is left over once the
whole minutes have been taken out" — for 137 seconds it gives 17. `//` gives the
minutes themselves (2), which is the other half of the display. `/` gives
`2.2833...`, a float that is neither number you wanted. Reversing the operands asks
a different question altogether — what is left of 60 after dividing it by the total
— and for anything over a minute it just hands back 60.
""",
                    },
                    {
                        "q": "What is `2 + 3 * 4 ** 2`?",
                        "opts": ["`50`", "`80`", "`400`", "`146`"],
                        "a": 0,
                        "why": r"""
`**` binds tightest, so `4 ** 2` is 16; then `3 * 16` is 48; then `2 + 48` is 50.
The other numbers are what you get from plausible mis-groupings: `(2 + 3) * 4 ** 2`
is 80, `((2 + 3) * 4) ** 2` is 400, and `2 + (3 * 4) ** 2` is 146. When you are not
sure, brackets cost nothing and say what you meant.
""",
                    },
                    {
                        "q": "A traceback ends with `NameError: name 'totl' is not defined`. What went wrong?",
                        "opts": [
                            "A name was read before anything was bound to it — usually a typo, or a line that never ran",
                            "A file the program wanted was missing",
                            "An operation was applied to a value of the wrong type",
                            "Something was divided by zero",
                        ],
                        "a": 0,
                        "why": r"""
`NameError` is the interpreter saying it looked that name up and found nothing
bound to it. The two usual causes are a misspelling (`totl` for `total`) and an
assignment that sits inside an `if` or a loop that never ran. An operation on the
wrong type raises `TypeError`, a missing file raises `FileNotFoundError`, and
dividing by zero raises `ZeroDivisionError` — the exception name on the bottom line
is doing real work, so read it before anything else, then read upwards for the line
number where it happened.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Splitting a bill that will not divide evenly",
                "minutes": 9,
                "lang": "python",
                "caption": "bill.py — five holes, and one number that must stay whole",
                "brief": r"""
Money in whole cents is the standard reason a beginner meets `//` and `%` for real.
The bill is 8735 cents across four people, which does not divide evenly, so the
program has to decide what happens to the remainder rather than letting a float
quietly absorb it.

Nothing runs here — you are choosing operators and a format spec. When it is filled
in correctly the script prints `Each pays 21.83 (2183 cents)` and `3 cent(s) left
over`.
""",
                "listing": r'''
# Splitting a bill that will not divide evenly.
total_cents = 8735
people = 4

each = total_cents ___ people        # whole cents per person
left_over = total_cents ___ people   # cents that cannot be shared out
as_currency = each ___ 100           # cents, expressed in the main unit

assert each ___ people + left_over == total_cents

print(f"Each pays {as_currency___} ({each} cents)")
print(f"{left_over} cent(s) left over")
''',
                "blanks": [
                    {
                        "prompt": "Whole cents each, with nothing after the decimal point.",
                        "hole": "op",
                        "opts": ["//", "/", "%", "**"],
                        "a": 0,
                        "why": "`//` is floor division: it divides and throws away the fraction, so 8735 // 4 is 2183 and stays an `int`. That matters because the next line has to account for what was thrown away.",
                        "whys": [
                            "`//` is floor division: it divides and throws away the fraction, so 8735 // 4 is 2183 and stays an `int`. That matters because the next line has to account for what was thrown away.",
                            "`/` gives 2183.75 — a float, and a quarter of a cent that nobody can pay. It is also the value that makes the `assert` below fail, because the leftover has been silently absorbed into the fraction.",
                            "`%` gives the remainder, 3. That is the *other* number this program needs, and it belongs on the line below.",
                            "`**` raises 8735 to the fourth power. Nothing about splitting a bill involves exponentiation; this is a slip of the finger rather than a misunderstanding.",
                        ],
                    },
                    {
                        "prompt": "The cents that will not divide out.",
                        "hole": "op",
                        "opts": ["%", "//", "/", "-"],
                        "a": 0,
                        "why": "`%` is the remainder after floor division: 8735 % 4 is 3. Together with `//` it splits the total into a part that shares out evenly and a part that does not, and no cents go missing between them.",
                        "whys": [
                            "`%` is the remainder after floor division: 8735 % 4 is 3. Together with `//` it splits the total into a part that shares out evenly and a part that does not, and no cents go missing between them.",
                            "`//` repeats the line above and gives 2183, so `left_over` holds a whole extra share rather than three stray cents. The assertion then rebuilds 2183 * 5 = 10915 instead of 8735 and fails.",
                            "`/` gives 2183.75. The fractional part does encode the remainder, but only as 0.75 of a person's share — you would still have to multiply by 4 to get back to 3 cents.",
                            "`-` subtracts 4 from the total, which is 8731 and means nothing here. Subtraction only does this job if you have already worked out what to subtract.",
                        ],
                    },
                    {
                        "prompt": "Cents are the smallest unit; this converts them to the main one.",
                        "hole": "op",
                        "opts": ["/", "//", "%", "*"],
                        "a": 0,
                        "why": "This is the one place a fraction is wanted: 2183 cents is 21.83, and `/` is the operator that keeps the decimal part. It returns a float, which is exactly right for something about to be printed to two places.",
                        "whys": [
                            "This is the one place a fraction is wanted: 2183 cents is 21.83, and `/` is the operator that keeps the decimal part. It returns a float, which is exactly right for something about to be printed to two places.",
                            "`//` floors the result to 21, throwing away the 83 cents you just took such care to compute.",
                            "`%` gives 83 — the cents part on its own, with the 21 discarded. Useful if you wanted the two halves separately, wrong if you wanted one number.",
                            "`*` gives 218300, which is the amount in hundredths of a cent. Multiplying converts the other way.",
                        ],
                    },
                    {
                        "prompt": "The identity that proves nothing was lost: share times people, plus the remainder.",
                        "hole": "op",
                        "opts": ["*", "+", "//", "/"],
                        "a": 0,
                        "why": "2183 * 4 + 3 is 8735, back to the total. This is the guarantee that `//` and `%` come with as a pair, and asserting it is a cheap way to catch a division that quietly used the wrong operator.",
                        "whys": [
                            "2183 * 4 + 3 is 8735, back to the total. This is the guarantee that `//` and `%` come with as a pair, and asserting it is a cheap way to catch a division that quietly used the wrong operator.",
                            "2183 + 4 + 3 is 2190, nowhere near the total. Adding the head-count treats four people as four cents.",
                            "2183 // 4 is 545, and the assertion fails immediately. Dividing again undoes the share rather than rebuilding the total from it.",
                            "2183 / 4 is 545.75. Same mistake as dividing again, with a float on the end to make the failure message harder to read.",
                        ],
                    },
                    {
                        "prompt": "Two decimal places, pinned — so money always shows both cent digits.",
                        "hole": "fmt",
                        "opts": [":.2f", ":.2", ":2f", ".2f"],
                        "a": 0,
                        "why": "Inside an f-string the colon starts the format spec, `.2` is the precision and `f` asks for fixed-point notation: `{as_currency:.2f}` gives `21.83`.",
                        "whys": [
                            "Inside an f-string the colon starts the format spec, `.2` is the precision and `f` asks for fixed-point notation: `{as_currency:.2f}` gives `21.83`.",
                            "Without the `f` the precision means *significant digits* in general format, so this prints `2.2e+01`. It is legal, which is what makes it worth seeing once.",
                            "`:2f` reads the 2 as a minimum field width rather than a precision, and fixed-point then falls back to six decimals: `21.830000`.",
                            "Without the colon there is no format spec at all: Python tries to read `as_currency.2f` as an expression, and the f-string fails to compile before a single line is printed.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "Precedence, with no brackets to help",
                "minutes": 7,
                "brief": r"""
Every operator in this expression is one you have already met. What decides the
answer is not what they do individually but the order Python applies them in, and
that order is fixed — it is not the order you read them in, and it is not left to
right except within a level.

```python
value = 5 + 27 // 4 * 2 - 3 ** 2 % 5
```

Work it out on paper before you type a number. Then, if you like, paste the line
into the playground and see whether Python agrees with you.
""",
                "prompt": "What does `value` hold?",
                "note": "Every operand is a whole number, so the answer is one too.",
                "figure": r"""
**Precedence, tightest first.** `**` goes first. Then `*`, `//` and `%` — these
three sit at the *same* level, so among themselves they run left to right. Then `+`
and `-`, also as one level, also left to right. There is not a single bracket in
the expression, so that ladder is the only thing deciding what happens when.
""",
                "given": [
                    {"label": "Expression", "value": "5 + 27 // 4 * 2 - 3 ** 2 % 5"},
                    {"label": "Types", "value": "every operand is an int"},
                    {"label": "Brackets", "value": "none"},
                ],
                "aside": "`//` floors and `%` takes a remainder, and both keep whole numbers whole "
                         "— so nothing in this line ever becomes a float.",
                "answer": 13,
                "tol": 0,
                "unit": "",
                "hint": "Deal with `3 ** 2` first. Then sweep left to right through `//`, `*` and "
                        "`%`, which all share one level. Only when those are gone do you add and "
                        "subtract.",
                "wrong": "The two usual slips: grouping `27 // (4 * 2)` instead of `(27 // 4) * 2`, "
                         "and letting `+` or `-` run before the `%`.",
                "why": "`3 ** 2` is 9 and `9 % 5` is 4. On the other side `27 // 4` is 6 and "
                       "`6 * 2` is 12 — left to right, because `//` and `*` share a level, so "
                       "the division genuinely happens first. What is left is `5 + 12 - 4`, which "
                       "is 13. Change that one `//` to a plain `/` and the same line gives 14.5 "
                       "instead — one character, a different number and a different type.",
            },
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
            "read": [
                {
                    "title": "Loops that stop, four accumulators, and saying no",
                    "minutes": 14,
                    "body": r'''
There are two loops, and one question chooses between them: **do you already know how
many times?**

If the answer is yes — walk these ten records, try each of these five options, count from
1 to 100 — the sequence exists before the loop starts and `for` walks it. If the answer is
no — keep reading lines until the user types `quit`, keep halving until you reach 1 — then
the stopping point depends on something that has not happened yet, and that is `while`.

You can force either to do the other's job. A `for` faking a `while` needs a `break`; a
`while` faking a `for` needs you to manage an index by hand, which is where off-by-one
errors are born. Choosing the one that matches the problem is not style. It is how you
avoid writing the bookkeeping that goes wrong.

## `for`, and the endpoint rule

```python
for i in range(2, 11, 3):
    print(i)
```

`range(start, stop, step)` yields 2, 5, 8 — and then stops, because the next value would
be 11 and **`stop` is never included**. Three iterations.

Do not reason about that arithmetically. Say the values out loud: two, five, eight, next
would be eleven, stop. The endpoint rule is the single most common source of a loop that
runs once too many or once too few, and saying the values costs a second.

The same rule is why `range(n)` gives exactly `n` values — 0 up to `n - 1` — and why
`range(0)` gives none at all rather than erroring. A loop that should do nothing does
nothing, without a special case.

## `while`, and the failure with no traceback

```python
n = 40
while n != 1:
    if n % 2 == 0:
        n = n // 2
    else:
        n = 3 * n + 1
```

Every `while` makes you a promise: something in the body moves the condition towards
false. Break the promise and the program does not crash — there is nothing to crash. It
sits there. No traceback, no error line, no clue.

The classic way to break it:

```python
while n != 1:
    if n > 1000:
        continue          # <-- skips everything below, including the update
    n = n // 2
```

`continue` jumps straight back to the condition. The line that would have changed `n`
never runs, so the condition is tested against a value that has not moved and comes out
the same way it did last time, forever. The same mistake is harmless in a `for` loop,
because there the sequence advances on its own and `continue` cannot stop it.

When something hangs, look for the update and ask whether every path through the body
reaches it.

## The four accumulators

Nearly every loop you write in this course is one of four shapes. Learn them as shapes
and you will stop re-deriving them.

```python
total = 0                          # running total
for n in numbers:
    total += n

best = numbers[0]                  # running best  — seed with a real value
for n in numbers:
    if n > best:
        best = n

count = 0                          # counter
for n in numbers:
    if n % 2 == 0:
        count += 1

evens = []                         # collector
for n in numbers:
    if n % 2 == 0:
        evens.append(n)
```

The one that goes wrong is the running best, and it goes wrong at the seed. Start it at
`0` and a list of freezing temperatures reports a maximum of 0 — no error, no crash, a
plausible wrong number, which is the worst kind of bug there is. Seed with the first
element and the answer is always a value the data actually contains. (`float("-inf")` is
the other safe seed, and it is the one to use when the list may be empty and you would
rather get infinity than an `IndexError`.)

## Worked: counting a Collatz chain by hand

Halve an even number; on an odd one go to `3n + 1`. From 6:

```text
    6  even  ->  3        step 1
    3  odd   ->  10       step 2
   10  even  ->  5        step 3
    5  odd   ->  16       step 4
   16  even  ->  8        step 5
    8  even  ->  4        step 6
    4  even  ->  2        step 7
    2  even  ->  1        step 8      condition n != 1 now false, stop
```

Eight steps. Notice that the count is of *rule applications*, not of numbers visited —
nine numbers appear and the answer is eight. That is the counter accumulator, and the
reason it starts at 0 is that a chain starting at 1 is already finished.

## Two values out of one expression

```python
pair = (871, 178)
n, steps = pair          # unpacking: two names, one tuple
```

A tuple is an ordered group of values written with commas; the brackets are usually
optional and usually written anyway for clarity. It is the normal way for one expression
to produce more than one thing — a function returning `(n, steps)`, a loop variable over
`.items()`, or swapping two names in one line with `a, b = b, a`.

A tuple is **immutable**: `pair[0] = 5` raises `TypeError`. That is not a restriction so
much as a signal. A list is a collection that may grow; a tuple is one record whose shape
is fixed, and the fixed shape is what makes unpacking safe to write.

Tuples compare left to right — `(9, 19) < (9, 20)` is `True` because the first elements
tie and the second decides. That rule is doing quiet work later in the course, when a
sort key is a tuple.

## Saying no

Not every input is one a function can do anything with. The Collatz rule says nothing
about zero or about negative numbers, so the honest response is to refuse:

```python
def collatz_steps(n):
    if n < 1:
        raise ValueError("n must be 1 or greater")
    ...
```

`raise` stops the function immediately and hands the problem to the caller. If nobody
catches it the program stops with a traceback naming your message — which is the correct
outcome, because a caller passing 0 has a bug and needs to be told.

The tempting alternative is to return something instead — `return 0`, or `return None`.
It is worse, and it is worth knowing why. `0` is a legitimate answer for `n = 1`, so the
caller now cannot distinguish "no steps needed" from "your input was nonsense". `None`
is not a legitimate answer, but it is silent: it flows on to the next line and fails
there, in a different function, with a `TypeError` that names neither the bad value nor
where it came from. Raising fails at the place that knows what went wrong.

Validate first, before any real work, so a rejected call never half-happens.

## One small convenience

Python lets you chain comparisons the way mathematics does:

```python
if 0 <= score <= 100:
```

That is one test, and `score` is evaluated once. Most languages require
`score >= 0 && score <= 100`; Python does not, and the chained form is the idiomatic one.
''',
                },
            ],
            "quiz": {
                "title": "Which branch runs, and how many times",
                "minutes": 7,
                "questions": [
                    {
                        "q": "With `n = 12`, what does `if n > 5: print(\"big\")` / `elif n > 10: print(\"huge\")` / `else: print(\"small\")` print?",
                        "opts": ["`big`", "`huge`", "`big` and then `huge`", "Nothing — two tests match, so the chain is ambiguous"],
                        "a": 0,
                        "why": r"""
An if/elif/else chain runs exactly one branch: the first test that comes out true,
after which the rest of the chain is skipped without being evaluated. `n > 10` is
also true here, but nothing ever asks it. That is the bug this shape invites — a
chain has to be written most specific test first, so `n > 10` would need to come
before `n > 5` for `huge` to ever appear.
""",
                    },
                    {
                        "q": "You must keep reading input lines until the user types `quit`. Which loop?",
                        "opts": [
                            "`while`, because the number of repetitions is not known before you start",
                            "`for`, because every loop that reads input is a `for` loop",
                            "`for`, because `while` cannot contain an `if`",
                            "Either — they compile to the same thing",
                        ],
                        "a": 0,
                        "why": r"""
That is the whole distinction: `for` walks a sequence whose length is already
settled, and `while` repeats as long as a condition holds, which is what you need
when the stopping point depends on something that has not happened yet. They are
not interchangeable in practice even though you can force either to do the other's
job — a `for` faking a `while` needs a `break`, and a `while` faking a `for` needs
you to manage the index by hand, which is where off-by-one errors come from.
""",
                    },
                    {
                        "q": "How many times does the body of `for i in range(2, 11, 3):` run?",
                        "opts": ["3", "4", "9", "10"],
                        "a": 0,
                        "why": r"""
`range(start, stop, step)` yields 2, 5, 8 and then stops, because the next value
would be 11 and the stop value is never included. Three iterations. The habit worth
building is to say the values out loud rather than reasoning about the arithmetic:
the endpoint rule is the single most common source of a loop that runs once too
often or once too few.
""",
                    },
                    {
                        "q": "You are finding the largest of a non-empty list of temperatures, which may all be below zero. What should the running best start as?",
                        "opts": [
                            "The first reading in the list",
                            "`0`",
                            "`-1`",
                            "The number of readings",
                        ],
                        "a": 0,
                        "why": r"""
Seeding with the first reading is always safe, because it is a value the answer is
allowed to be. Seeding with `0` quietly reports 0 as the maximum of a list of
freezing temperatures — no error, no crash, just a wrong number, which is the worst
kind of bug. `-1` fails the same way one degree lower down, and the count of
readings has nothing to do with their values. The other safe seed is
`float("-inf")`, which is smaller than any real reading by construction.
""",
                    },
                    {
                        "q": "Inside a `while` loop, a `continue` sits above the line that advances the counter. What happens?",
                        "opts": [
                            "The loop never ends, because the update it skipped past is the one that would eventually stop it",
                            "The loop exits at once, like `break`",
                            "The body runs once more and then the loop exits",
                            "Nothing — `continue` only has an effect inside a `for` loop",
                        ],
                        "a": 0,
                        "why": r"""
`continue` jumps straight back to the condition, skipping the rest of the body —
including the increment. The condition is then tested against a value that has not
moved, so it comes out the same way it did last time, forever. This is the single
most common way to hang the tab, and it is also why the same mistake is harmless in
a `for` loop: there the sequence advances on its own and `continue` cannot stop it.
""",
                    },
                    {
                        "q": "`total = 0`, then `for n in [1, 2, 3]:` with **both** `total += n` and `print(total)` indented inside. What appears?",
                        "opts": [
                            "`1`, `3`, `6` on three lines",
                            "`6` on one line",
                            "`1`, `2`, `3` on three lines",
                            "`0` on one line, before the loop does anything",
                        ],
                        "a": 0,
                        "why": r"""
Both statements are in the loop body, so the print runs once per iteration and
shows the accumulator part-way through: 1, then 3, then 6. Move that one line four
spaces to the left and it is no longer part of the body — it runs once, after the
loop, and prints only 6. Nothing else about the program changes. That is what it
means to say indentation *is* the block structure rather than a convention on top
of it.
""",
                    },
                ],
            },
            "blanks": {
                "title": "A Collatz loop, one operator at a time",
                "minutes": 9,
                "lang": "python",
                "caption": "collatz.py — five holes; a wrong pick here hangs the loop rather than printing the wrong number",
                "brief": r"""
The same rule as the lab, written as a bare `while` loop. Every hole is an operator,
and most of the wrong choices do not produce a wrong answer — they produce a loop
that never reaches its stopping condition at all. That is the failure mode worth
recognising by sight, because there is no traceback to read when it happens.

Filled in correctly this prints `8`: from 40 the chain runs 40, 20, 10, 5, 16, 8, 4,
2, 1, which is eight applications of the rule.
""",
                "listing": r'''
# The Collatz rule: halve an even number, and 3n + 1 an odd one.
n = 40
steps = 0

while n ___ 1:
    if n ___ 2 == 0:
        n = n ___ 2
    else:
        n = 3 * n ___ 1
    steps ___ 1

print(steps)
''',
                "blanks": [
                    {
                        "prompt": "Keep going until the chain arrives at 1.",
                        "hole": "cmp",
                        "opts": ["!=", "==", ">=", "<"],
                        "a": 0,
                        "why": "`while n != 1` keeps looping while `n` is anything other than 1, and stops the moment it lands there. That is the stopping condition the rule actually describes.",
                        "whys": [
                            "`while n != 1` keeps looping while `n` is anything other than 1, and stops the moment it lands there. That is the stopping condition the rule actually describes.",
                            "`n == 1` is false at the very start, since `n` is 40, so the body never runs once and the program prints 0. A condition that is inverted usually shows up as this: an answer of zero rather than an error.",
                            "`n >= 1` is still true once `n` reaches 1, so the loop takes one more pass: 1 is odd, 3 * 1 + 1 is 4, and from there it runs 4, 2, 1, 4, 2, 1 forever. The condition is never false, so nothing stops it.",
                            "`n < 1` is false at the start and the loop is skipped entirely, printing 0 — the same silent nothing as testing for equality.",
                        ],
                    },
                    {
                        "prompt": "The evenness test.",
                        "hole": "op",
                        "opts": ["%", "//", "/", "**"],
                        "a": 0,
                        "why": "`n % 2` is the remainder on division by 2, which is 0 for an even number and 1 for an odd one. Comparing that remainder to 0 is the standard way to ask the question in any language that has a modulo operator.",
                        "whys": [
                            "`n % 2` is the remainder on division by 2, which is 0 for an even number and 1 for an odd one. Comparing that remainder to 0 is the standard way to ask the question in any language that has a modulo operator.",
                            "`n // 2 == 0` is only true for `n` of 0 or 1, so from 40 the test always fails, the odd branch always runs, and 3n + 1 grows without limit.",
                            "`n / 2 == 0` is true only when `n` is exactly 0. Same outcome: the even branch is unreachable and the number runs away upwards.",
                            "`n ** 2 == 0` squares the value and is true only at 0. Squaring answers no question about divisibility.",
                        ],
                    },
                    {
                        "prompt": "Halve an even number, keeping it a whole number.",
                        "hole": "op",
                        "opts": ["//", "%", "*", "-"],
                        "a": 0,
                        "why": "`n // 2` halves and stays an `int`, which matters because the chain has to compare exactly against 1 at the top. A float 1.0 would still stop the loop, but every later value would carry a `.0` through the arithmetic for no reason.",
                        "whys": [
                            "`n // 2` halves and stays an `int`, which matters because the chain has to compare exactly against 1 at the top. A float 1.0 would still stop the loop, but every later value would carry a `.0` through the arithmetic for no reason.",
                            "`n % 2` is 0 for every even number, so the first pass sends `n` to 0 and it is stuck there — 0 is even, 0 halves to 0, and the loop spins.",
                            "`n * 2` doubles instead of halving. Every value stays even, so the even branch runs every time and the number doubles forever.",
                            "`n - 2` counts down two at a time. From an even start it steps straight past 1 to 0 and then into the negatives, and the condition at the top is never satisfied.",
                        ],
                    },
                    {
                        "prompt": "The odd branch: three times the value, and then?",
                        "hole": "op",
                        "opts": ["+", "-", "*", "//"],
                        "a": 0,
                        "why": "The rule is 3n + 1. The `+ 1` is what makes an odd number even again — `3 * odd` is odd, so without it the next pass would take the odd branch again and the chain could never come back down.",
                        "whys": [
                            "The rule is 3n + 1. The `+ 1` is what makes an odd number even again — `3 * odd` is odd, so without it the next pass would take the odd branch again and the chain could never come back down.",
                            "3n - 1 is a different rule with different behaviour: from 5 it goes 14, 7, 20, 10, 5 and repeats forever, a cycle the loop has no way out of.",
                            "3n * 1 is just 3n, which stays odd, so the odd branch runs again and again on an ever-larger number.",
                            "3n // 1 is also just 3n — dividing by one changes nothing, and the same runaway follows.",
                        ],
                    },
                    {
                        "prompt": "Count this application of the rule.",
                        "hole": "op",
                        "opts": ["+=", "=", "-=", "=="],
                        "a": 0,
                        "why": "`steps += 1` reads the counter, adds one, and stores it back. It is the counter accumulator in its shortest form, and the loop needs it to survive from one pass to the next.",
                        "whys": [
                            "`steps += 1` reads the counter, adds one, and stores it back. It is the counter accumulator in its shortest form, and the loop needs it to survive from one pass to the next.",
                            "`steps = 1` overwrites the counter every pass, so however long the chain is the program prints 1. Nothing errors; the number is simply meaningless.",
                            "`steps -= 1` counts downwards and prints -8. The sign is a giveaway, which at least makes this one easy to spot.",
                            "`steps == 1` compares rather than assigns. Python evaluates it, throws the `True` or `False` away, and the counter stays at 0.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "How many times does a nested loop run?",
                "minutes": 12,
                "vars": ["n", "i", "j", "T"],
                "brief": r'''
This shape turns up the first time you compare every item in a collection with
every other item:

```python
for i in range(n):
    for j in range(i):
        ...
```

Nothing below depends on what the body does. The only question is how many times it
runs, written as a formula in $n$ — because that formula, not the body, is what
decides whether $n = 1000$ is a moment or an afternoon.
''',
                "steps": [
                    {
                        "prompt": "Fix a single value of $i$. `range(i)` produces the whole numbers below $i$, so how many times does the inner body run for that one $i$?",
                        "answer": r"i",
                        "hint": "`range(3)` gives 0, 1, 2 — three values. `range(0)` gives none at all, so the count is the same as the argument.",
                        "deconstruct": [
                            "`range(i)` counts from 0 up to but not including $i$.",
                            "That is exactly $i$ values, and it is correctly 0 when $i$ is 0.",
                        ],
                    },
                    {
                        "prompt": "The outer loop runs $i$ over $0, 1, \\dots, n-1$, so the total is $0 + 1 + 2 + \\dots + (n-1)$. Write that sum in closed form, in terms of $n$.",
                        "answer": r"\frac{n(n-1)}{2}",
                        "hint": "Pair the first term with the last: $0 + (n-1)$. Then the second with the second-to-last: $1 + (n-2)$. Every pair has the same sum.",
                        "deconstruct": [
                            "Write the sum forwards and then backwards, one line under the other, and add column by column: every column comes to $n-1$.",
                            "There are $n$ columns, so twice the sum is $n(n-1)$ and the sum itself is half of that.",
                        ],
                    },
                    {
                        "prompt": "Now change the inner loop to `range(i + 1)`, so the body also runs on the pass where $j$ reaches $i$. Write the new total in terms of $n$.",
                        "answer": r"\frac{n(n+1)}{2}",
                        "hint": "Every one of the $n$ outer passes now does exactly one extra step, so the total goes up by $n$.",
                        "deconstruct": [
                            "The new total is the old one plus $n$: $\\frac{n(n-1)}{2} + n$.",
                            "Put the $n$ over the same denominator: $\\frac{n(n-1) + 2n}{2} = \\frac{n^2 + n}{2}$.",
                        ],
                    },
                    {
                        "prompt": "Multiply out $\\frac{n(n-1)}{2}$ and keep only the term that decides how the count grows for large $n$. Write that single term.",
                        "answer": r"\frac{n^2}{2}",
                        "hint": "Expanding gives two terms. One of them grows in proportion to $n$, the other in proportion to $n$ squared — at large $n$ only one of those still matters.",
                        "deconstruct": [
                            "$\\frac{n(n-1)}{2} = \\frac{n^2}{2} - \\frac{n}{2}$.",
                            "At $n = 1000$ the first term is 500000 and the second is 500 — a tenth of a percent. At $n = 10$ the correction is a whole 10%, which is why the exact form is still the one to use for small inputs.",
                        ],
                    },
                ],
                "closing": r'''
Doubling $n$ multiplies $\frac{n^2}{2}$ by four, and that is the entire content of
calling this loop *quadratic*. The $-\frac{n}{2}$ is real — it is why the count at
$n = 100$ is 4950 rather than 5000 — but it never changes the shape of the curve,
which is why the term that survives is the one people quote.
''',
            },
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
            "read": [
                {
                    "title": "Return, not print — and the shape of a function you can build on",
                    "minutes": 14,
                    "body": r'''
Here is the mistake, and it is worth meeting deliberately rather than by accident:

```python
def double(x):
    print(x * 2)

result = double(5)
print(result + 1)
```

The first call puts `10` on the screen, so the function looks like it works. The next
line raises `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`.

`double` never handed anything back. A function that falls off the end without a `return`
returns `None` — always, silently, no warning. `result` is bound; it is bound to `None`.

`print` puts characters on a screen for a human to read. `return` hands a value back to
the calling code. Only the second one composes: you cannot add one to something that was
printed, cannot store it, cannot pass it on. Almost every function you write should
return; the printing belongs at the outside edge of the program, where a human is.

The error is worth recognising by sight, because it almost never points at the function
that caused it. `NoneType` in an arithmetic `TypeError` means "something returned None a
few lines ago" far more often than it means anything else.

## `return` names a value and leaves

```python
def sign(n):
    if n > 0:
        return 1
    if n < 0:
        return -1
    return 0
```

Three `return` statements; exactly one runs per call. Reaching a `return` ends the call
on the spot — nothing after it in that call happens.

That is why an early return can stand in for an `else`: once the positive case has
returned, the code below it is *already* the not-positive case and needs no guard. It is
also why an unconditional `return` part-way down a function makes everything below it
dead code that can never run, whatever the input.

## Parameters and arguments, and why the distinction earns its keep

```python
def area(w, h):        # w and h are the parameters — the slots
    return w * h

area(3, 4)             # 3 and 4 are the arguments — the values
```

The distinction sounds like pedantry until you read an error message.
`TypeError: area() missing 1 required positional argument: 'h'` is telling you a *slot*
went unfilled, and it names the slot. Knowing that the name in the message comes from the
`def` header, not from the call, is the fastest route to the value you forgot.

## Defaults and keywords

```python
def initials(full_name, separator="."):
    ...

initials("ada lovelace")                        # "A.L"
initials("ada lovelace", separator="-")         # "A-L"
```

A default makes a parameter optional. Naming an argument at the call site makes the
intent readable and lets you skip past parameters you do not care about.

Two rules come with it. Passing both by position fills the slots in header order, so
`greet("Hi", "Ada")` on `def greet(name, greeting="Hello")` sets `name` to `"Hi"` and
returns `"Ada, Hi"` — a bug that produces plausible-looking output, which is the
dangerous kind. And a positional argument after a keyword one is a `SyntaxError`: once
you start naming, you cannot go back to counting.

**Where defaults stop behaving.** The default expression is evaluated **once**, when the
`def` runs — not on each call. With an immutable default like `"."` or `0` you will never
notice. With a mutable one you will:

```python
def collect(item, into=[]):     # do not do this
    into.append(item)
    return into

collect(1)      # [1]
collect(2)      # [1, 2]   <- the same list as last time, still holding 1
```

Every call that omits `into` shares one list, created when the function was defined. The
fix is to default to `None` and build a fresh one inside:

```python
def collect(item, into=None):
    if into is None:
        into = []
    into.append(item)
    return into
```

## What happens inside stays inside

```python
count = 0

def bump():
    count = 1        # creates a *local* count; the outer one is untouched

bump()
print(count)         # 0
```

Assigning to a name anywhere inside a function makes that name local for the whole call.
The function made its own `count`, set it to 1, and discarded it on return.

This is a feature. It is what lets you write a function without first auditing every name
you used against the rest of the program. To get a value out, `return` it.

## Building one function out of another

The third lab asks you to write `normalise(text)` and then build `word_frequencies`,
`top_n` and `average_word_length` on top of it rather than re-splitting the text in each.
The reason is not speed — the extra call makes it very slightly slower — and it is not
memory. It is that **"what counts as a word" is a decision, and a decision should be
written down once.**

Today the rule is: lowercase it, strip `.,!?;:()` off both ends. The day you decide
apostrophes should survive so that `don't` stays one word, you change `normalise` and
every function built on it changes with it. Write the rule out three times and you will
change two of them, and the third goes quietly out of step — quietly, because nothing
errors. Decomposition buys you one place to change your mind.

## Two idioms the exercises hand you

Both appear in this module's lab hints, and neither is obvious on sight.

**A generator expression inside a call.**

```python
sum(len(word) for word in words)
```

Read it right to left: for each `word` in `words`, produce `len(word)`; `sum` adds them
as they arrive. It is the running-total accumulator from the previous module, written as
one expression. Nothing is built in between — the lengths are produced one at a time,
which is why `sum(...)` over a huge file does not need memory for a huge list.

**A sort key.**

```python
ranked = sorted(freqs.items(), key=lambda pair: (-pair[1], pair[0]))
```

`freqs.items()` gives `(word, count)` pairs. `key=` takes a function, and `sorted` calls
it on each item and sorts by whatever comes back rather than by the item itself.
`lambda pair: ...` is that function, written inline: `lambda` builds a small anonymous
function whose body is a single expression.

The key here returns a tuple, and tuples compare left to right — so this sorts by
`-count` first and only uses `word` to break ties. The negation is the trick worth
keeping: there is no "descending" option inside a key, so you negate the number and let
ascending order do the work. Sorting the word ascending in the same tuple is what makes
ties alphabetical.

Worked on `{"a": 3, "c": 1, "b": 3}`:

```text
.items() order      key            sorted ascending by key
("a", 3)            (-3, "a")      (-3, "a")   ->  ("a", 3)
("c", 1)            (-1, "c")      (-3, "b")   ->  ("b", 3)
("b", 3)            (-3, "b")      (-1, "c")   ->  ("c", 1)
```

`.items()` hands the pairs back in insertion order, not sorted order — the sorting is
entirely `sorted`'s doing.

`[:2]` off the front of that gives `[("a", 3), ("b", 3)]`, biggest first, ties
alphabetical — which is exactly what `top_n` is specified to return.
''',
                },
            ],
            "quiz": {
                "title": "What a call hands back",
                "minutes": 7,
                "questions": [
                    {
                        "q": "`def double(x): print(x * 2)` — after `result = double(5)`, what is `result`?",
                        "opts": ["`None`", "`10`", "`5`", "Nothing is assigned, because the function had no `return`"],
                        "a": 0,
                        "why": r"""
The call does print `10`, and then hands back `None`, because a function that falls
off the end without a `return` returns `None` — always, silently, with no warning.
The name `result` is definitely bound; it is bound to `None`, which is why the error
usually surfaces one line later as `TypeError: unsupported operand type(s)` when you
try to do arithmetic with it. `print` puts characters on a screen for a human;
`return` hands a value back to the caller. Only the second one composes.
""",
                    },
                    {
                        "q": "`count = 0`, then a function whose whole body is `count = 1`, then a call to it. What does `print(count)` show afterwards?",
                        "opts": ["`0`", "`1`", "`None`", "A NameError"],
                        "a": 0,
                        "why": r"""
Assigning to a name anywhere inside a function makes that name local to the call.
The function created its own `count`, set it to 1, and threw it away when the call
returned; the module-level `count` was never touched. This is a feature, not an
obstacle — it is what lets you write a function without first checking every name
you used against the rest of the program. To send a value out, `return` it.
""",
                    },
                    {
                        "q": "In `def area(w, h):` and the call `area(3, 4)` — which are the arguments?",
                        "opts": ["`3` and `4`", "`w` and `h`", "`area`, `w` and `h`", "Both pairs, since they name the same things"],
                        "a": 0,
                        "why": r"""
Parameters are the names in the `def` header — the slots. Arguments are the values
handed over at the call site, which get bound to those slots for the duration of the
call. The distinction matters as soon as you read an error message: "missing 1
required positional argument: 'h'" is telling you a *slot* went unfilled, and naming
the slot is the fastest way to find which value you forgot.
""",
                    },
                    {
                        "q": "`def greet(name, greeting=\"Hello\"): return f\"{greeting}, {name}\"`. Which call returns `\"Hi, Ada\"`?",
                        "opts": [
                            "`greet(\"Ada\", greeting=\"Hi\")`",
                            "`greet(\"Hi\", \"Ada\")`",
                            "`greet(greeting=\"Hi\")`",
                            "`greet(name=\"Ada\", \"Hi\")`",
                        ],
                        "a": 0,
                        "why": r"""
Naming the argument makes the intent unambiguous and lets you skip past the default.
Passing both by position fills the slots in header order, so `greet("Hi", "Ada")`
sets `name` to `"Hi"` and returns `"Ada, Hi"` — a bug that produces plausible-looking
output, which is the dangerous kind. Passing only the keyword leaves the required
`name` unfilled and raises `TypeError` at the call. And a positional argument after
a keyword one is a syntax error: once you start naming, you cannot go back to
counting.
""",
                    },
                    {
                        "q": "Why build `word_frequencies` on top of `normalise` rather than re-splitting the text inside it?",
                        "opts": [
                            "There is then one definition of what counts as a word, and changing it changes every function at once",
                            "It runs measurably faster",
                            "Python does not allow the same expression to appear twice in a file",
                            "It uses less memory",
                        ],
                        "a": 0,
                        "why": r"""
Decomposition is about where a decision lives. The rule "lowercase it and strip the
punctuation off both ends" is a decision; if it is written down twice, then the day
you decide apostrophes should survive, you have to remember both places, and the
function you forget goes quietly out of step with the other. Reuse costs an extra
call, so it is very slightly *slower*, and memory is roughly unchanged. You are
buying one place to change your mind.
""",
                    },
                    {
                        "q": "`def sign(n)` has three `return` statements, one per case. How many of them execute for `sign(-4)`?",
                        "opts": [
                            "One — reaching a `return` ends the call immediately",
                            "Two, since two of the conditions are checked",
                            "All three, and the last value wins",
                            "None, because `n` is negative",
                        ],
                        "a": 0,
                        "why": r"""
`return` does two things at once: it names the value, and it leaves. Nothing after it
in that call runs. That is why an early `return` can stand in for an `else` — once
the positive case has returned, the code below it is already the negative-or-zero
case and needs no guard — and why an unconditional `return` part-way through a
function makes everything below it dead code that will never execute, no matter what.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Two functions, one built on the other",
                "minutes": 9,
                "lang": "python",
                "caption": "initials.py — four holes across a definition and a call",
                "brief": r"""
Two functions in the shape the lab asks for: a small one that does the real work,
and a second one whose whole job is to call the first with a particular setting.
The holes are the four places the mechanics of a `def` show up — the default, the
method that produces the words, the way a value gets out, and the name that gets
called.

Filled in correctly, this prints `A-L-K`.
""",
                "listing": r'''
def initials(full_name, separator___"."):
    """The first letter of each part of a name, joined by the separator."""
    letters = []
    for part in full_name.___():
        letters.append(part[0].upper())
    ___ separator.join(letters)


def badge(full_name):
    """A short label, built out of the function above rather than repeating it."""
    return ___(full_name, separator="-")


print(badge("ada lovelace king"))
''',
                "blanks": [
                    {
                        "prompt": "Give the second parameter a default, so most callers need not supply it.",
                        "hole": "=",
                        "opts": ["=", "==", ":", ":="],
                        "a": 0,
                        "why": "A single `=` in a `def` header attaches a default value to a parameter. `separator` then becomes optional: callers who say nothing get `\".\"`, and callers who care pass something else.",
                        "whys": [
                            "A single `=` in a `def` header attaches a default value to a parameter. `separator` then becomes optional: callers who say nothing get `\".\"`, and callers who care pass something else.",
                            "`==` is the comparison operator and is a syntax error in a parameter list. It is worth meeting the distinction here, where the fix is one character: `=` binds, `==` asks.",
                            "A colon in a parameter list starts an annotation, so `separator: \".\"` is legal Python that labels the parameter and gives it no default at all. This listing still runs, because `badge` passes a separator anyway — but `initials(\"ada lovelace\")` on its own now fails with `TypeError: initials() missing 1 required positional argument`, which is exactly the convenience the default existed to provide.",
                            "`:=` is the walrus operator, which assigns inside an expression. It has no meaning in a parameter list and fails to parse.",
                        ],
                    },
                    {
                        "prompt": "Turn the whole name into its separate parts.",
                        "hole": "method",
                        "opts": ["split", "join", "strip", "upper"],
                        "a": 0,
                        "why": "`full_name.split()` with no argument splits on any run of whitespace and drops the empties, which is exactly right for a name typed by a human with an accidental double space in it.",
                        "whys": [
                            "`full_name.split()` with no argument splits on any run of whitespace and drops the empties, which is exactly right for a name typed by a human with an accidental double space in it.",
                            "`join` goes the other way — it glues a list of strings into one string, and it is already doing that job on the last line of the function.",
                            "`strip()` removes whitespace from the two ends and returns a single string, so the `for` would then walk it one character at a time and the initials would be every letter of the name.",
                            "`upper()` also returns a single string, so the loop would again see characters rather than words — and the uppercasing is already handled where it belongs, on the first letter of each part.",
                        ],
                    },
                    {
                        "prompt": "Hand the finished string back to whoever called.",
                        "hole": "kw",
                        "opts": ["return", "print", "pass", "yield"],
                        "a": 0,
                        "why": "`return` is what makes the value available to `badge`, which needs to pass it on to its own caller. Anything else leaves `initials` handing back `None`.",
                        "whys": [
                            "`return` is what makes the value available to `badge`, which needs to pass it on to its own caller. Anything else leaves `initials` handing back `None`.",
                            "The hole sits in front of an expression, not inside a call, so this becomes `print separator.join(letters)` — and Python 3 refuses to compile the file at all: `SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?`. Written properly as `print(separator.join(letters))` it would put `A-L-K` on the screen and *still* return `None`, so `badge` would hand back `None` and the last line would print `None` underneath. Showing a value is not the same as returning one.",
                            "`pass` is the do-nothing statement. It is a syntax error here because it takes no expression, and even written correctly it would leave the function returning `None`.",
                            "`yield` turns the function into a generator: calling it would build a lazy object rather than running the body, and `badge` would hand back something that prints as `<generator object ...>`.",
                        ],
                    },
                    {
                        "prompt": "Which function does `badge` call?",
                        "hole": "name",
                        "opts": ["initials", "badge", "separator", "join"],
                        "a": 0,
                        "why": "`badge` is a thin wrapper: all it decides is which separator to use, and the work is done by `initials`. That is the decomposition the module is about — one place that knows how to split a name, and callers that configure it.",
                        "whys": [
                            "`badge` is a thin wrapper: all it decides is which separator to use, and the work is done by `initials`. That is the decomposition the module is about — one place that knows how to split a name, and callers that configure it.",
                            "`badge` calling itself raises `TypeError: badge() got an unexpected keyword argument 'separator'`, because `badge` takes only a name — the separator is the whole reason the other function exists. Had the signatures matched, it would have recursed until the stack ran out instead.",
                            "`separator` is a parameter of the other function and does not exist here at all — this raises `NameError` the moment `badge` is called.",
                            "`join` is a string method, not a function in this file. Written bare like this it is a `NameError`; even reached correctly it would need a list, not a name and a keyword argument.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "Trace it: defaults, calls, and one returned number",
                "minutes": 7,
                "brief": r'''
Two functions, one of which uses the other. Nothing here is clever; the point is
that you can follow it exactly, and that following it exactly is a skill worth
practising before the programs get big enough that you cannot.

```python
def clamp(value, low=0, high=10):
    """Push value back inside the window [low, high]."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def average(values):
    """The mean of the clamped values."""
    total = 0
    for value in values:
        total += clamp(value)
    return total / len(values)


print(average([-4, 3, 12, 7, 8]))
```
''',
                "prompt": "What number does that `print` put on the screen?",
                "note": "`average` calls `clamp` without a `low` or a `high`, so the defaults apply on every call.",
                "figure": r"""
**How to trace it.** `average` walks the five values in order and calls `clamp` once
for each. Each call runs on its own, sees only the value it was handed and the two
defaults, and hands one number back — `average` never looks inside it. Write the
five returned numbers down in a column first. Only then add them up, and only then
divide by how many there were.
""",
                "given": [
                    {"label": "Input", "value": "[-4, 3, 12, 7, 8]"},
                    {"label": "clamp defaults", "value": "low = 0, high = 10"},
                    {"label": "Calls to clamp", "value": "5, one per value"},
                ],
                "aside": "`clamp` has three `return` statements and every call reaches exactly one of "
                         "them — whichever comes first.",
                "answer": 5.6,
                "tol": 0.005,
                "unit": "",
                "hint": "Two of the five values sit outside the window and neither survives the call "
                        "unchanged. Clamp all five first, then take the mean of what came back.",
                "wrong": "Averaging the raw list gives 5.2, which is the answer to a different "
                         "question — the one where `clamp` returned its input every time.",
                "why": "`clamp` is called once per value with `low = 0` and `high = 10`: -4 is below "
                       "the window so 0 comes back, 12 is above it so 10 comes back, and 3, 7 and 8 "
                       "pass straight through. The total is 0 + 3 + 10 + 7 + 8 = 28, and 28 / 5 is "
                       "5.6. Two things worth taking from it: `average` composes with whatever "
                       "`clamp` returns without knowing how it decided, and `/` produces a float, "
                       "so the answer is 5.6 rather than the 5 that `//` would have given.",
            },
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
            "read": [
                {
                    "title": "Records, files, and what survives the trip to disk",
                    "minutes": 14,
                    "body": r'''
Everything so far has lived for as long as the program ran and then vanished. This module
is about the two things that fix that: a shape to hold records in, and a way to write them
somewhere that outlives the process.

The shape is a **list of dicts**.

```python
rows = [
    {"name": "Ada",   "score": 90, "team": "red"},
    {"name": "Linus", "score": 75, "team": "blue"},
    {"name": "Grace", "score": 88, "team": "red"},
]
```

The two containers are doing different jobs, and that split is the whole reason it works.
The dict gives every field a name, so `row["team"]` says what it means where `row[2]`
does not — and stays correct when a column is inserted. The list gives the rows an order,
which is often the order they were read in and is worth not losing.

It is also exactly what `json.load` produces from a file of records, so almost no
conversion code is needed at the boundary.

## Two ways to read a key, and they mean different things

```python
row["score"]            # KeyError if it is missing
row.get("score", 0)     # 0 if it is missing
row.get("score")        # None if it is missing
```

This is not a choice between a safe one and a risky one. It is a place to say what you
believe about the data.

Square brackets mean *this must be here*: a record with no `team` is broken and you want
to be told, loudly, at the row that broke. `.get` with a default means *this may be
absent, and absent means zero* — a form field left blank, an optional column. Both are
correct; using the wrong one either hides a corrupt file or crashes on an ordinary one.

`.get` with no default is a third behaviour and the usual cause of a `TypeError` a few
lines later, because `None + 90` has no meaning. If you see that message, look for a
`.get` that lost its default.

The accumulate-into-a-dict pattern is built on exactly this:

```python
totals[team] = totals.get(team, 0) + int(score)
```

The default is the entire trick. The first line for each team arrives before the key
exists, and `0` is what makes that first line ordinary instead of a special case.

## Reading a comprehension

```python
parts = [part.strip() for part in line.split(",")]
```

This is the collector accumulator compressed into one expression: for each `part` in
`line.split(",")`, put `part.strip()` in a new list. Read it as *expression — for —
source*, and read the middle first.

Written out it is four lines and means the same thing. Use whichever is clearer; a
comprehension with a condition and a nested loop in it has stopped being clearer.

## Opening a file

```python
with open("results.csv") as f:
    for line in f:
        ...
```

`with` closes the file on the way out of the block whichever way you leave — falling off
the end, returning early, or raising half-way through. A bare `open` is not wrong so much
as fragile: it needs a matching `close()`, and the one path that skips it is the exception
path, which is the path you did not test.

The mode is the second argument and the default is `"r"`:

```text
"r"   read; the file must exist                     (the default)
"w"   write; creates it, and TRUNCATES it if it existed
"a"   append; creates it, and adds to the end
"x"   create; raises FileExistsError if it is there
```

`"w"` is the one to be careful with. It is right for a summary regenerated from scratch
each run, and it is the wrong answer to "make sure the file exists", because the way it
makes sure is by emptying it.

Iterating an open file gives you one line at a time, including its trailing newline —
which is why `line.strip()` is almost always the next thing to happen.

## JSON, and what does not survive the trip

```python
with open("totals.json", "w") as out:
    json.dump(totals, out)
```

`json.dump(obj, file)` writes into an open file; `json.dumps(obj)` builds a string and
hands it to you. The `s` is for *string*. `load` and `loads` are the same pair going the
other way.

JSON is a text format with six types, and Python has more than six. What comes back is
not always what went in:

```text
dict            ->  object     ->  dict            unchanged
list            ->  array      ->  list            unchanged
tuple           ->  array      ->  LIST            (1, 2) comes back as [1, 2]
str             ->  string     ->  str             unchanged
int / float     ->  number     ->  int / float     unchanged
True / False    ->  true/false ->  True / False    unchanged
None            ->  null       ->  None            unchanged
int as a KEY    ->  "1"        ->  STRING key      {1: "a"} comes back as {"1": "a"}
set             ->  TypeError: Object of type set is not JSON serializable
```

The bottom three are the ones that bite. A set fails loudly, which is the good case. A
tuple and an integer key both fail *quietly*: the file is valid, the load succeeds, and
`back[1]` raises `KeyError` while `back["1"]` works. Keep keys as strings from the start
when data is going to disk, and expect tuples to come back as lists.

## Catching exactly what you expect

On the very first run the data file does not exist. That is a normal situation, not an
error, and catching the one exception that describes it says so:

```python
try:
    with open(path) as f:
        return json.load(f)
except FileNotFoundError:
    return []
```

The narrowness is the point. A bare `except:` swallows everything — the permission error,
the corrupt-file error, the typo in your own code, and the reader's Ctrl-C, because
`KeyboardInterrupt` is an exception too. The bug it hides is always the one you did not
know you had.

Note also what is *not* wrapped: only the opening and loading. The wider you draw the
`try`, the more unrelated failures it catches by accident.

## Your own files are modules too

The capstone is in two files, and the second one starts:

```python
from expenses import Expense, Ledger
```

`import expenses` looks for `expenses.py` beside the file being run, **executes it top to
bottom**, and keeps the names it defined. `from expenses import Expense` does the same and
lifts two of those names into your namespace.

"Executes it top to bottom" is the part with consequences. Anything at the top level of
`expenses.py` — a `print`, a file being written, a long computation — happens on import,
before your program has done anything. That is why the capstone's constraints say
`expenses.py` must define classes and print nothing: a module is a thing to be imported,
and importing it should be quiet.

Which is also the honest place to say what the capstone assumes. It asks you to write two
classes, and classes are the one topic this course uses without teaching — they are
covered in the Python Foundations track that the degree assumes you have done, and they
are the entire subject of CS102, which comes next. If `class`, `__init__` and `self` are
unfamiliar when you reach the capstone, that is where to go and get them; nothing in these
four modules will have supplied them.
''',
                },
            ],
            "quiz": {
                "title": "Records in, records out",
                "minutes": 7,
                "questions": [
                    {
                        "q": "`row` is a dict with no `\"score\"` key. What is the difference between `row.get(\"score\", 0)` and `row[\"score\"]`?",
                        "opts": [
                            "`.get` hands back 0; the square brackets raise `KeyError`",
                            "Both hand back 0",
                            "Both raise `KeyError`",
                            "`.get` hands back `None`; the square brackets hand back 0",
                        ],
                        "a": 0,
                        "why": r"""
`.get(key, default)` is the "I expect this might be missing" form and returns the
default rather than raising. Square brackets are the "this must be here" form and
raise `KeyError` when it is not. Both are correct in the right place: use brackets
where a missing key means the data is broken and you want to be told, and `.get`
where a missing key means zero, or none, or not applicable. `.get(key)` with no
default returns `None`, which is a third behaviour again and the usual cause of a
`TypeError` a few lines later.
""",
                    },
                    {
                        "q": "Why `with open(path) as f:` rather than `f = open(path)`?",
                        "opts": [
                            "The file is closed when the block ends, including when the block raises",
                            "It is faster",
                            "It is the only way to read a file in Python",
                            "It stops other programs opening the same file",
                        ],
                        "a": 0,
                        "why": r"""
`with` closes the file on the way out of the block whichever way you leave it —
falling off the end, returning early, or raising half-way through. The bare `open`
is not wrong so much as fragile: it needs a matching `close()`, and the one path
that skips it is the exception path, which is the path you did not test. On the
speed question there is nothing in it, `open` is perfectly legal on its own, and
`with` takes no locks at all.
""",
                    },
                    {
                        "q": "You `json.dump({1: \"a\", 2: \"b\"}, f)` and then `json.load` it back. What are the keys?",
                        "opts": [
                            "The strings `\"1\"` and `\"2\"`",
                            "The integers `1` and `2`, unchanged",
                            "Nothing — `json.dump` raises on non-string keys",
                            "There are no keys; it comes back as a list",
                        ],
                        "a": 0,
                        "why": r"""
A JSON object's keys are strings by definition, so `json.dump` converts your integer
keys on the way out and `json.load` has no way to know they were ever anything else.
The round trip is not lossless, and it fails quietly: the file is valid, the load
succeeds, and `back[1]` raises `KeyError` while `back["1"]` works. This is the main
reason to keep keys as strings from the start when data is going to disk.
""",
                    },
                    {
                        "q": "`items = [\"a\", \"b\", \"c\", \"d\", \"e\"]`. What is `items[1:4]`?",
                        "opts": [
                            "`[\"b\", \"c\", \"d\"]`",
                            "`[\"b\", \"c\", \"d\", \"e\"]`",
                            "`[\"a\", \"b\", \"c\", \"d\"]`",
                            "`[\"b\", \"c\"]`",
                        ],
                        "a": 0,
                        "why": r"""
A slice starts at the first index and stops *before* the second, so it takes indices
1, 2 and 3. The handy consequence is that the length of `items[a:b]` is `b - a`,
which is 3 here — worth knowing because it means `items[:k]` and `items[k:]` split
a list with nothing missing and nothing duplicated, whatever `k` is.
""",
                    },
                    {
                        "q": "On the very first run the data file does not exist yet. What is the right shape for the loader?",
                        "opts": [
                            "Catch `FileNotFoundError` around the open and return an empty result",
                            "Open the file in `\"w\"` mode first so that it always exists",
                            "Wrap it in a bare `except:` and return an empty result",
                            "Let it crash — a missing file is the caller's problem",
                        ],
                        "a": 0,
                        "why": r"""
A first run is a normal situation, not an error, and catching the one exception that
describes it says so precisely. Opening in `"w"` mode does guarantee the file exists,
by truncating it — so the second run destroys the data the first run saved, which is
about as bad as a bug gets. A bare `except:` swallows everything: the permission
error, the corrupt-file error, the typo in your own code, and the reader's Ctrl-C.
And crashing is defensible only if a missing file really is a broken installation
rather than an empty one.
""",
                    },
                    {
                        "q": "Why is a list of dicts the workhorse shape for tabular data?",
                        "opts": [
                            "Each dict is one row keyed by column name, and the list keeps the rows in order",
                            "Dicts are faster to iterate than lists",
                            "JSON cannot represent anything else",
                            "A dict cannot hold more than one row",
                        ],
                        "a": 0,
                        "why": r"""
The two containers are doing different jobs, and the shape works because of that
split: the dict gives every field a name so `row["team"]` says what it means where
`row[2]` does not, and the list gives the rows an order that survives loading and
saving. It is also exactly what `json.load` produces from a file of records, which
is why so little conversion code is needed at the boundary. Speed is not the reason
— for a few thousand rows neither container is the bottleneck.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Read a file, total it up, write JSON",
                "minutes": 10,
                "lang": "python",
                "caption": "totals.py — five holes covering the whole round trip",
                "brief": r"""
The shape of nearly every small data script: open a file, accumulate into a dict,
write the result somewhere it will survive the program exiting. Each hole is a place
where a plausible-looking alternative fails in a different way — one raises, one
does nothing at all, and one destroys the output file.

`results.csv` holds one competitor per line as `name,score,team`, and the script
prints something like `{'red': 178, 'blue': 75}`.
""",
                "listing": r'''
import json

# results.csv holds one competitor per line:  name,score,team
totals = {}

___ open("results.csv") as f:
    for line in f:
        name, score, team = line.strip().split(",")
        totals[team] = ___ + ___

with open("totals.json", "___") as out:
    json.___(totals, out)

print(totals)
''',
                "blanks": [
                    {
                        "prompt": "Open the file so it is closed again whatever happens inside.",
                        "hole": "kw",
                        "opts": ["with", "for", "while", "if"],
                        "a": 0,
                        "why": "`with` binds the open file to `f` and closes it on the way out of the block — including the way out through an exception, which is the path that a hand-written `close()` reliably misses.",
                        "whys": [
                            "`with` binds the open file to `f` and closes it on the way out of the block — including the way out through an exception, which is the path that a hand-written `close()` reliably misses.",
                            "`for` needs an `in`, not an `as`, so this does not parse. Iterating the file is the job of the loop on the next line, over the object `with` has already given you.",
                            "`while` takes a condition and no `as` clause. Even if it parsed, a file object is always truthy, so it would describe a loop that never ends.",
                            "`if` also takes no `as` clause here and does not parse. Opening a file is not a question with a yes or no answer.",
                        ],
                    },
                    {
                        "prompt": "The running total for this team so far — remembering that the first line for a team arrives before the key exists.",
                        "hole": "expr",
                        "opts": ["totals.get(team, 0)", "totals[team]", "totals.get(team)", "0"],
                        "a": 0,
                        "why": "`totals.get(team, 0)` reads the running total when there is one and stands in a zero when there is not, which is exactly what the first line for each team needs. This is the accumulate-into-a-dict pattern, and the default is the whole trick.",
                        "whys": [
                            "`totals.get(team, 0)` reads the running total when there is one and stands in a zero when there is not, which is exactly what the first line for each team needs. This is the accumulate-into-a-dict pattern, and the default is the whole trick.",
                            "Square brackets demand the key already be there, so the first line of the file raises `KeyError` before a single total is built. It would work only if every team were seeded to zero beforehand — which means knowing the teams before reading the file.",
                            "`.get` with no default returns `None` for a key that is missing, and `None + 90` raises `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`. That message is worth recognising: it usually means a default went missing somewhere.",
                            "A literal zero throws away everything accumulated so far, so each team ends up holding only the score from its last line in the file. No error, plausible numbers, wrong answer.",
                        ],
                    },
                    {
                        "prompt": "Everything read from a file arrives as text.",
                        "hole": "expr",
                        "opts": ["int(score)", "score", "str(score)", "score.strip()"],
                        "a": 0,
                        "why": "`split` hands back strings, so `score` is `\"90\"` and not `90`. `int` converts it, and it also raises `ValueError` on a field that is not a whole number — which is a useful place for a broken line to announce itself.",
                        "whys": [
                            "`split` hands back strings, so `score` is `\"90\"` and not `90`. `int` converts it, and it also raises `ValueError` on a field that is not a whole number — which is a useful place for a broken line to announce itself.",
                            "Leaving it as a string raises `TypeError` on the addition, because `0 + \"90\"` has no meaning — Python will not guess whether you wanted 90 or `\"090\"`.",
                            "`str` converts to a string something that is already a string, so nothing changes and the addition fails the same way.",
                            "`.strip()` removes surrounding whitespace and hands back a string, so this fixes a formatting problem that `split` mostly did not leave and none of the type problem that matters here.",
                        ],
                    },
                    {
                        "prompt": "The mode for writing a fresh file.",
                        "hole": "mode",
                        "opts": ["w", "r", "a", "x"],
                        "a": 0,
                        "why": "`\"w\"` opens for writing, creating the file if it is absent and truncating it if it is not — which is what you want for a summary that is regenerated from scratch every run.",
                        "whys": [
                            "`\"w\"` opens for writing, creating the file if it is absent and truncating it if it is not — which is what you want for a summary that is regenerated from scratch every run.",
                            "`\"r\"` is read mode and is the default. `totals.json` is the file this script creates, so on a first run the `open` itself raises `FileNotFoundError` and `json.dump` is never reached; if a `totals.json` is left over from an earlier run, the open succeeds and the write then fails with `io.UnsupportedOperation: not writable`. Forgetting the mode entirely gives whichever of the two applies.",
                            "`\"a\"` appends. The first run writes valid JSON; the second run glues a second object onto the end of the first, and the file stops being loadable by anything.",
                            "`\"x\"` creates the file only if it does not already exist and raises `FileExistsError` otherwise, so the script would work exactly once. That is a real mode for a real purpose, but not this one.",
                        ],
                    },
                    {
                        "prompt": "Write the dict into the open file as JSON.",
                        "hole": "fn",
                        "opts": ["dump", "dumps", "load", "write"],
                        "a": 0,
                        "why": "`json.dump(obj, file)` serialises straight into an open file object. The trailing `s` in the other name is for *string*: that one builds the text and hands it to you instead.",
                        "whys": [
                            "`json.dump(obj, file)` serialises straight into an open file object. The trailing `s` in the other name is for *string*: that one builds the text and hands it to you instead.",
                            "`json.dumps` takes only the object positionally, so passing a file as a second positional argument raises `TypeError: dumps() takes 1 positional argument but 2 were given`. Even called correctly it returns a string that nobody writes anywhere, leaving an empty file.",
                            "`json.load` reads rather than writes: it takes one file to read from, so two positional arguments raise `TypeError: load() takes 1 positional argument but 2 were given`. Nothing about this direction of travel matches what the line is trying to do.",
                            "There is no `json.write`, so this raises `AttributeError: module 'json' has no attribute 'write'`. The file object has a `.write`, but it takes text, not a dict.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "Aggregating over records with a hole in them",
                "minutes": 7,
                "brief": r'''
Real files have short lines in them. Here one record made it into the list without a
`score` at all — a line with a missing field, a form somebody left blank — and the
loop has to say what that is worth before it can add anything up.

```python
rows = [
    {"name": "Ada",   "score": 90, "team": "red"},
    {"name": "Linus", "score": 75, "team": "blue"},
    {"name": "Grace", "score": 88, "team": "red"},
    {"name": "Ken",                "team": "red"},
]

total = 0
for row in rows:
    if row["team"] == "red":
        total += row.get("score", 0)

print(total)
```
''',
                "prompt": "What does `print(total)` show?",
                "note": "Every row has a `team`. Only three of the four have a `score`.",
                "figure": r"""
**Two filters, not one.** The `if` decides which rows are counted at all, and
`.get`'s default decides what a counted row with no `score` contributes. Work the
rows in order: for each one, ask whether it is on the red team, and if it is, ask
what `.get` hands back for it. Three rows get past the first question; one of those
three has nothing for the second.
""",
                "given": [
                    {"label": "Rows", "value": "4"},
                    {"label": "Rows on the red team", "value": "3"},
                    {"label": "Rows with no score key", "value": "1 (Ken, on red)"},
                ],
                "aside": "`row[\"team\"]` uses square brackets because a record with no team really is "
                         "broken; `row.get(\"score\", 0)` uses a default because a record with no "
                         "score is merely empty.",
                "answer": 178,
                "tol": 0,
                "unit": "",
                "hint": "Only the red rows are added, and the one without a `score` key still "
                        "contributes something — work out what `.get` returns for it.",
                "wrong": "Adding every row regardless of team gives 253. Skipping Ken entirely gives "
                         "the same total as counting him, which is worth noticing: his contribution "
                         "is zero either way.",
                "why": "Three rows are on the red team: 90, 88, and Ken's, which has no `score` key. "
                       "`row.get(\"score\", 0)` hands back 0 for that one instead of raising "
                       "`KeyError`, so the total is 90 + 88 + 0 = 178. Writing `row[\"score\"]` "
                       "there would have stopped the program on Ken's row — and that is a genuine "
                       "design choice rather than a mistake. A missing score is either “count it "
                       "as nothing” or “this file is broken”, and `.get` with a "
                       "default is how you say the first of those out loud.",
            },
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
