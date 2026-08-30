"""EE131 — Programming for Engineers.

A first-year course. It assumes school mathematics and nothing else: no prior
circuits, no prior programming beyond arithmetic. Every term is defined where it
first appears.

Authoring rules, as for the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number in a test was produced by running the code
"""

COURSE = {
    "id": "EE131",
    "title": "Programming for Engineers",
    "band": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 120,
    "icon": "▶",
    "summary": (
        "An engineer writes code to answer a question about a physical thing. This "
        "course starts at the beginning — what a variable is, what a type is, what a "
        "loop does — and ends with a simulation of a circuit you have drawn yourself, "
        "checked against the answer calculus gives for the same circuit. The point is "
        "never the syntax. The point is being able to say why you believe the number "
        "that came out."
    ),
    "outcomes": [
        "Read and write small Python programs using variables, conditionals, loops and functions, and say what each line does.",
        "Explain why floating-point arithmetic is approximate, and compare measured quantities with a tolerance rather than with equality.",
        "Hold a signal in a NumPy array, read one in from a text log, and summarise it with mean, RMS and peak.",
        "Integrate a first-order differential equation with forward Euler, and demonstrate by measurement that the answer has converged.",
        "Design a two-resistor divider and a single-pole RC filter to a stated specification, and verify both by simulation.",
        "Hold engineering data in lists, dictionaries and records, and read a text netlist into them, engineering notation and all.",
        "Replace an element-by-element loop with a NumPy expression built from masks and broadcasting, and say why the two give the same answer.",
        "Tell a failure that stops the program from one that returns a plausible wrong number, and defend against each in the way it deserves.",
        "Integrate a system with two states, and use a quantity the physics conserves to expose the integrator's own error.",
        "Solve for a value the algebra will not isolate, by bisection and by Newton's method, and say which of the two is guaranteed and which is fast.",
    ],
    "assessment": "Ten quizzes, four circuits drawn and measured in the schematic editor, two guided derivations, nine Python labs checked by execution, and a capstone that simulates a measured circuit and proves the simulation right.",
    "reading": [
        "*Think Python*, Downey — chapters 1 to 6, and 10 to 12 for lists, dictionaries and files. Freely available online.",
        "The NumPy *absolute beginner's guide*, in the official documentation.",
        "*Numerical Methods in Engineering with Python*, Kiusalaas — chapter 4 for root finding, chapter 7 for Euler and what comes after it.",
        "*What Every Computer Scientist Should Know About Floating-Point Arithmetic*, Goldberg — the first three sections, for cancellation and why the quadratic formula has two spellings.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Names, values and types",
            "summary": "A program moves numbers around. Before it can, you have to know what a number is to Python, and what a name is.",
            "concepts": [
                "A *variable* is a name bound to a value. `r = 4700` does not state a fact; it makes the name `r` refer to the value 4700 from that line onwards.",
                "A *type* is what a value is: `int` for a whole number, `float` for a decimal, `str` for text, `bool` for `True` or `False`.",
                "`/` always produces a float, even `4 / 2`. `//` divides and throws away the remainder; `%` keeps only the remainder.",
                "A float is stored in binary and is almost always slightly wrong. `0.1 + 0.2` is not `0.3`, and no amount of care makes it so.",
                "Because of that, two measured quantities are compared with a tolerance — `abs(a - b) <= tol` — never with `==`.",
                "An f-string builds a line of text from values: `f\"{v:.3f} V\"` formats `v` to three decimal places.",
            ],
            "read": [
                {
                    "title": "A name, a value, and the line that ties them together",
                    "minutes": 11,
                    "body": r'''
A resistor on the bench has a resistance whether or not anybody writes it down. The
number you would write is 4700. The moment you type

```python
r = 4700
```

two separate things exist inside the machine. Somewhere in memory there is a value —
the whole number 4700, held as a pattern of bits — and somewhere else there is a name,
`r`, which is a label with a piece of string running from it to that value. The line
did not state a fact about the world, and it did not set up an equation. It carried
out an action, once, at that point in the program: *from here on, the name `r` refers
to that value*.

Nearly everything that surprises people in their first program follows from taking
that sentence literally.

## The equals sign is a verb

In mathematics $x = y + 1$ is a standing claim. It was true before you read it and it
is true after; if $y$ moves then $x$ moves with it, because the two were never
independent things. A spreadsheet behaves the same way — type `=A1` into cell B1 and
B1 will follow A1 for the rest of the afternoon.

Python's `=` is none of that. It is an instruction with a moment attached, and it
always does the same two steps in the same order: **work out the value on the right,
then tie the name on the left to whatever came back.** Nothing is remembered about how
that value was arrived at.

Three lines are enough to see it:

```python
a = 5      # tie the name a to the value 5
b = a      # look up what a refers to right now (5), and tie b to that
a = 9      # re-tie a to 9. Nobody consults b, and b does not move
print(b)   # 5
```

Line by line, with the state of the world after each one:

```
line        a       b     what the line actually did
------------------------------------------------------------------------
a = 5       5       —     evaluated 5; bound the name a to it
b = a       5       5     evaluated a, which was 5; bound the name b to it
a = 9       9       5     evaluated 9; re-bound a. b was never mentioned
```

Answering 9 is not carelessness. It is the mathematically literate answer, which is
precisely why it is worth naming: if `b = a` set up a *relationship* rather than
performing an *event*, then 9 would be right and Python would be wrong. The habit to
build is reading every `=` as "gets", never as "equals".

The counter that appears in every program settles the argument:

```python
count = 0
count = count + 1
```

As an equation the second line claims $0 = 1$, which is nonsense. As an instruction it
is ordinary: work out `count + 1` using whatever `count` refers to *now*, which gives
1, then re-tie the name `count` to that. Right-hand side first, always. Python offers
`count += 1` as a shorthand, and it means exactly the longer line — not something
cleverer.

## A value has a kind, and the kind decides what an operator means

A value is not merely a number; it is a value *of some type*, and the type travels
with it. Four types carry this module:

```python
type(4700)      # <class 'int'>     a whole number. Exact, and no size limit
type(4700.0)    # <class 'float'>   a decimal, stored in binary, usually approximate
type("4700")    # <class 'str'>     four characters: '4', '7', '0', '0'
type(True)      # <class 'bool'>    True or False, and nothing else
```

Print the first three and the screen shows `4700`, `4700.0` and `4700` — almost the
same thing three times over. `type` is what tells them apart, and the difference is
not cosmetic. `4700 + 4700` is 9400. `"4700" + "4700"` is the text `47004700`, because
`+` on two strings joins them end to end. And `"4700" + 4700` is refused outright,
with a `TypeError`, because Python will not guess which of those two meanings you
wanted. One operator, three outcomes, chosen entirely by the types of the values
either side of it.

(`bool` is quietly a kind of `int`: `True + True` is 2. That reads as a curiosity and
becomes useful the first time you want to count how many readings passed a test.)

## Worked example 1: 47 resistors, six to a board

A tape holds 47 resistors and each board takes six of them. Three sensible questions,
three different operators, and three answers that are not interchangeable:

```
how many boards can be fully populated?    47 // 6  =  7          int
how many resistors are left over?          47  % 6  =  5          int
sharing all 47 over the six positions
of a single board, how many each?          47  / 6  =  7.8333...  float
```

Check the first two against each other, which is the habit worth forming early:

```
7 boards x 6 resistors   =  42
resistors left on the tape   +  5
                            ----
                              47   which is what we started with
```

That identity — `(a // b) * b + a % b == a` — holds for every pair of whole numbers,
and it is what the two operators are *for*. Between them they account for every item
on the tape: `//` says how many complete groups, `%` says what could not be grouped.
Ask for the leftovers with `47 - 7 * 6` if you like; `%` is the same arithmetic with
the intermediate step removed.

`/` is different in kind, not merely in rounding. It is *true* division, and its result
is always a `float` — even when the division is exact. `4 / 2` is `2.0`, not `2`. That
looks like pedantry until the answer has to be used as a count: `range(10 / 2)` fails
with a `TypeError`, because a number of repetitions has to be an `int` and `5.0` is
not one however round it looks. `range(10 // 2)` works. The type of an answer is part
of the answer.

## Worked example 2: one line of arithmetic, traced

```python
vin = 15          # volts,  an int
r1  = 20000       # ohms,   an int
r2  = 10000       # ohms,   an int
vout = vin * r2 / (r1 + r2)
```

The last line is a single instruction, and its whole right-hand side is worked out
before the name `vout` is touched at all. In the order Python does it:

```
brackets first:   r1 + r2       =  20000 + 10000  =   30000     int
then the times:   vin * r2      =  15 * 10000     =  150000     int
then the divide:  150000 / 30000                  =       5.0   FLOAT
```

`vout` is bound to `5.0`. A float — because `/` produced one — even though the
division came out exact. Ask for `type(vout)` and the answer is `float`; ask whether
`vout == 5` and the answer is `True`, because 5.0 and 5 compare equal across the two
types. Both of those facts are worth having, and neither is guessable.

Follow the units alongside the numbers, in a column the machine cannot see:

```
15 V x 10000 Ω            = 150000 V·Ω
150000 V·Ω / 30000 Ω      =      5.0 V      the ohms cancel; volts survive
```

Python tracked none of that. It does not know what a volt is; it multiplied and
divided numbers, and you supplied the meaning. That division of labour never changes
in this course, and it is the reason a numerically flawless result can still be
completely wrong: nothing inside the machine will tell you that you divided by the
wrong resistance.

## The mistake people actually make

Two, and they are cousins.

The first is expecting Python to guess. `"4700" + 4700` looks as though it obviously
means 9400 — or obviously means the text `47004700`, depending on who is reading — and
a language that picked one would be right half the time and silently wrong the other
half. Python refuses instead. That refusal is a feature, and it costs you one `int()`
or `float()` call at the boundary where text becomes numbers, which is a price worth
paying.

The second is reading `=` as a constraint. It is tempting because you have spent years
in a subject where that is exactly what it means, and because the counter idiom
`count = count + 1` is the only line in a first program that makes the reading
impossible. Until you meet that line, the equation reading and the instruction reading
agree on every example, so nothing forces the correction.

## Where this stops holding

- **`//` floors; it does not truncate.** `-7 // 2` is `-4`, not `-3`: −3.5 goes *down*
  to the next whole number rather than towards zero. `%` follows suit, so `-7 % 2` is
  `1` rather than `-1`, and in Python `a % b` always carries the sign of `b`. C, Java
  and Rust made the opposite choice: there, integer `-7 / 2` truncates towards zero to
  −3, and `-7 % 2` is −1. Both
  conventions are self-consistent; Python's keeps `a % n` inside the range `0` to
  `n - 1` for positive `n`, which is exactly what you want for stepping round a
  circular buffer, and it is why that operation needs a special case for negative
  indices in C and needs none here.
- **An `int` has no size limit in Python.** `2 ** 200` is computed exactly, all
  sixty-one digits of it, because a Python integer grows as many bits as it needs.
  That stops being true of the `int64` inside a NumPy array in module 5, and of the
  32-bit registers in the microcontroller you are eventually writing for, where the
  same multiplication wraps round to a wrong answer without a word of complaint.
- **The division in worked example 2 came out exactly right, and that was luck.**
  30000 goes into 150000 a whole number of times. Ask for `9 * 2200 / 6900` instead
  and you get 2.869565217391304, which is not the true value of that fraction and
  never can be. The next reading unit is about what happens the rest of the time —
  which is nearly always.
''',
                },
                {
                    "title": "Why 0.1 + 0.2 is not 0.3",
                    "minutes": 14,
                    "body": r'''
Type this into Python and watch it disagree with arithmetic you learned at seven:

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
```

Nothing is broken. No setting fixes it, no other language does better, and the answer
is not "a rounding error" in the loose sense of something that could have been avoided
by being more careful. The machine did exactly what it is built to do, and what it is
built to do is not decimal arithmetic.

## A ruler with the wrong marks on it

Imagine a steel rule with marks only at halves, quarters, eighths, sixteenths — every
mark at a power of two, and nothing in between. Measure a rod against it and you can
report only the nearest mark. Most rods will not land on one, so most measurements
come back a hair off, and the hair is at most half the gap between neighbouring marks.

That is not an analogy for what a `float` is. It is a description of one. A float is a
number of the form

$$m \times 2^{e}$$

with $m$ a whole number of fixed width and $e$ a whole-number exponent. In the
double-precision format that Python uses for every float, $m$ carries 53 bits — so
$2^{52} \le m < 2^{53}$ — and $e$ ranges over about $\pm 1000$. Every value the
machine can hold is one of those. Everything else gets the nearest one.

The marks are not evenly spaced along the number line; they are evenly spaced *within
each doubling*. Between 1 and 2 there are $2^{52}$ of them, so the gap is $2^{-52}
\approx 2.22\times10^{-16}$. Between 2 and 4 the same $2^{52}$ marks are stretched
over twice the distance, so the gap doubles. Between 0.25 and 0.5 it halves twice,
to $2^{-54} \approx 5.55\times10^{-17}$. Relative precision is what stays constant:
whatever the magnitude, a stored double is within a factor of about
$1 \pm 1.1\times10^{-16}$ of the number you meant, and that bound —
$u = 2^{-53}$ — is the single most useful number in this unit.

## Every base has fractions it cannot write

One third has no exact decimal form. Write 0.3333 and you are short; write 0.3334 and
you are over; no finite string of decimal digits is ever exactly $1/3$. Nobody finds
this shocking, because everybody meets it at school.

Base two has the same problem with a different set of fractions, and the set is
larger. A fraction terminates in base $b$ only when the prime factors of its
denominator all divide $b$. Ten factorises as $2 \times 5$, so decimal handles halves
and fifths and anything built from them. Two has only itself, so binary handles halves
and nothing else. One tenth is $1/(2 \times 5)$, and that five is fatal.

You can watch it fail. To write a fraction in binary, double it repeatedly and record
the whole part each time:

```
0.1 x 2 = 0.2   ->  0
0.2 x 2 = 0.4   ->  0
0.4 x 2 = 0.8   ->  0
0.8 x 2 = 1.6   ->  1, keep 0.6
0.6 x 2 = 1.2   ->  1, keep 0.2
0.2 ...             we have seen 0.2 already, so it all repeats from here
```

So $0.1_{10} = 0.0001100110011\ldots_2$, with `0011` recurring forever. The machine
has 53 bits and the expansion does not stop, so it must cut it off and round.

## Worked example 1: what 0.1 actually is

Round that expansion to 53 significant bits and you get a specific whole number over a
specific power of two. Python will show you the fraction itself:

```
>>> (0.1).as_integer_ratio()
(3602879701896397, 36028797018963968)          and 36028797018963968 = 2**55

exact decimal value of that fraction:
    0.1000000000000000055511151231257827021181583404541015625

what you wrote:
    0.1
                                    ----------------------------
    stored value is HIGH by about    5.55e-18
    as a fraction of 0.1, that is    5.55e-17     comfortably inside u
```

The name `0.1` in your program does not refer to one tenth. It refers to that
55-decimal-place value, which is the closest a double can come. Every arithmetic operation
from then on is performed on *that*, exactly and correctly, and one tenth never enters
the machine at all.

## Worked example 2: the addition, all the way through

Now do the same for 0.2. It is 0.1 doubled, and doubling is exact in binary — it just
adds one to the exponent — so 0.2 is stored high by twice as much:

```
0.1 stored ->  0.1000000000000000055511151231257827021181583404541015625
0.2 stored ->  0.200000000000000011102230246251565404236316680908203125
              ---------------------------------------------------------
exact sum      0.3000000000000000166533453693773481063544750213623046875
```

That sum is the true sum of the two stored values, and it is not itself a double: near
0.3 the marks on the rule are $2^{-54}$ apart, and this number falls between two of
them. The two candidates are

```
below:   0.299999999999999988897769753748434595763683319091796875
above:   0.3000000000000000444089209850062616169452667236328125
```

and the exact sum sits **exactly halfway between them** — $2.7755\times10^{-17}$ from
each, which is $2^{-55}$, half a gap. A tie. The rule for ties is round-half-to-even:
take whichever neighbour has an even last bit, so that ties do not all drift the same
way and accumulate a bias. Written over the common denominator $2^{54}$ the two
candidates are $5404319552844595$ and $5404319552844596$, and the even one is the
upper. So the answer is the higher mark, and it prints as `0.30000000000000004`.

Meanwhile, what does the literal `0.3` in your program refer to? The double nearest one
tenth times three — which is the *lower* of those same two marks. So:

```
0.1 + 0.2  ->  5404319552844596 / 2**54
0.3        ->  5404319552844595 / 2**54
                    ---------------------
difference          1 / 2**54  =  5.551115123125783e-17
```

They differ by one step of the rule. Not a big error, not a small error — the smallest
non-zero difference that can exist at that magnitude. And it is enough to make `==`
answer `False`, because `==` on floats asks whether two values are the same mark, and
these are two adjacent marks.

## Then why does the screen say 0.1?

Because printing a float does not show you the stored value; it shows the *shortest
decimal string that would round back to the same stored value*. Since `0.1` is the
shortest string that lands on that mark, `0.1` is what you see. Ask for more digits and
the truth surfaces:

```python
>>> f"{0.1:.20f}"
'0.10000000000000000555'
```

This is why the problem is so hard to catch by looking. The display is designed to
agree with what you typed, and it succeeds right up until two values that print
identically fail to compare equal.

## The mistake people actually make

The mistake is `==`. It is tempting because it is right for every other type you have
met — `"R7" == "R7"`, `47 == 47`, `True == True` — and because the two numbers you are
comparing genuinely *should* be equal, so testing whether they are feels like the
direct question.

Its usual companion is the belief that rounding first fixes it: `round(a) == round(b)`,
or the same idea at two decimals. That trades one wrong answer for another. Rounding
does not create a tolerance; it creates a *grid*, and a grid gets both kinds of
question wrong:

```
4.49 and 4.51    differ by  0.4%   round to 4 and 5   ->  judged DIFFERENT
4.51 and 5.49    differ by 21.7%   round to 5 and 5   ->  judged the SAME
```

A test whose verdict depends on which side of an arbitrary line each value fell, rather
than on how far apart they are, is not a tolerance at all.

## What replaces it

Ask the engineering question instead: *is the gap small compared with the quantity?*

```python
abs(a - b) <= tol_frac * abs(b)
```

Worked, with a 5 V rail and a 1% tolerance:

```
tol_frac = 0.01, b = 5.00 V, so the allowed gap is 0.05 V

a = 4.96 V:   gap = |4.96 - 5.00| = 0.04 V  <= 0.05  ->  passes  (0.8% low)
a = 4.90 V:   gap = |4.90 - 5.00| = 0.10 V  >  0.05  ->  fails   (2.0% low)
a = 5.04 V:   gap = |5.04 - 5.00| = 0.04 V  <= 0.05  ->  passes  (0.8% high)
```

Both `abs` calls earn their place. The one on the gap makes the test symmetric, so a
reading that is far too low fails in the same way as one that is far too high; without
it, `a - b <= 0.05` is satisfied by *every* reading below 5 V, including 0. The one on
`b` stops a negative reference — a −12 V rail, say — from turning the allowed gap
negative and rejecting everything, including a perfect measurement.

And notice how much bigger this tolerance is than the arithmetic it is protecting you
from. Float noise is at the $10^{-16}$ level; a 1% tolerance is $10^{-2}$. The
tolerance is really about your meter, your resistors and your temperature. Float error
is a rounding detail that the honest engineering test absorbs for free.

## Where this stops holding

- **Integers are exact, and unlimited.** None of the above applies to `int`
  arithmetic. `//` and `%` on whole numbers are exact for numbers of any size, so
  money is counted in whole pence and time in whole samples, not in floats.
- **Some decimals are exact, which is worse than none being exact.** Halves, quarters
  and eighths land on marks: `0.5 + 0.25 == 0.75` is `True`. A test written entirely
  with such values passes, proves nothing, and will not warn you the day real
  measurements arrive.
- **Errors accumulate.** Add 0.1 to itself ten times and you get
  `0.9999999999999999`, not 1.0 — each addition rounds, and the roundings do not
  cancel. A loop written `while t < 1.0: t += 0.1` therefore runs eleven times, not
  ten, which is the sort of bug that shows up as one extra sample at the end of a
  simulation. Module 8 integrates a differential equation with exactly this loop, and
  counts its steps rather than trusting the accumulated time.
- **Large magnitudes lose the small ones entirely.** `1e16 + 1 == 1e16` is `True`: up
  there the marks are two apart and 1 has nowhere to go. This is also why an
  *absolute* tolerance is only meaningful once you know the scale: 0.01 V is loose on
  a 3.3 V rail, at 0.3% of it, and utterly meaningless on the 5 mV output of a
  thermocouple, where it admits every reading there is.
- **But relative tolerance fails at zero.** If the expected value is 0, `tol_frac *
  abs(b)` is 0 and only exactness will pass. Where a quantity can legitimately be
  zero, allow both: `abs(a - b) <= max(rel * abs(b), abs_floor)`, which is what
  `math.isclose(a, b, rel_tol=..., abs_tol=...)` does for you.
- **Subtraction of near-equal numbers is a different and worse problem.** There the
  leading digits agree and cancel, promoting the rounding noise in the last few bits
  to the whole of the answer. Module 7 takes that apart, with a quadratic formula that
  returns 0 for a root that is not zero.
- **If you truly need decimal, ask for it.** `decimal.Decimal("0.1") +
  Decimal("0.2")` is exactly `Decimal("0.3")`, and `fractions.Fraction` is exact for
  rationals. Both cost a few times as much per operation, and neither can live inside
  a NumPy array of machine numbers, so every operation on a million of them runs at
  Python speed rather than the CPU's. Use them where exact decimal *is* the
  specification — currency, billing — and floats everywhere a measurement is involved.
''',
                },
                {
                    "title": "Text that looks like a number",
                    "minutes": 10,
                    "body": r'''
Open any measurement log, any netlist, any CSV a colleague sends you, and the first
thing to be clear about is that it contains no numbers at all. It contains characters.
The line

```text
R7 4900.0 4700
```

is a run of fourteen characters, six of which happen to be the shapes `4`, `9`, `0`,
`0`, `.` and `0`. Whether that means four thousand nine hundred ohms is a question
about *interpretation*, and interpretation is your job, not the file's.

Python keeps the two things apart on purpose, and the seam between them is where most
first-week bugs live.

## Why `"12" + 3` is refused

```python
>>> "12" + 3
TypeError: can only concatenate str (not "int") to str
```

There are two entirely defensible answers here. `+` joins two strings, so `"12" + "3"`
is `"123"`. `+` adds two numbers, so `12 + 3` is `15`. With one of each, a language has
to choose, and any choice is wrong about half the time. JavaScript chooses to join,
which is why `"12" + 3` is `"123"` there and why a whole genre of web bug consists of
totals that concatenate instead of adding. Python refuses and makes you say which you
meant:

```python
int("12") + 3        # 15         text becomes a number
"12" + str(3)        # '123'      the number becomes text
```

The cost is one conversion call at the boundary. The benefit is that the failure
happens on the line where the mistake was made, loudly, instead of thirty lines later
as a plausible wrong answer.

## The conversions, and where they refuse

`int()` and `float()` are strict, and the strictness is the point:

```python
float("4700")        # 4700.0
float("  4700\n")    # 4700.0     surrounding whitespace is ignored
int("4700")          # 4700
int("4700.0")        # ValueError: invalid literal for int()
float("4k7")         # ValueError: could not convert string to float
```

`int("4700.0")` failing surprises people. `int` parses an *integer literal*, and
`4700.0` is not one; if you want truncation, ask for it with `int(float("4700.0"))` and
the two steps make the intent visible. As for `4k7` — that is an engineer's notation,
not Python's, and no library will decode it for you. Module 4 writes the function that
does, because a netlist is full of them.

## Worked example: one line of a log, end to end

```python
line = "R7 4900.0 4700"

ref, meas_s, nom_s = line.split()   # ['R7', '4900.0', '4700'] unpacked into three names
meas = float(meas_s)                # 4900.0   a number at last
nom  = float(nom_s)                 # 4700.0
err  = 100 * (meas - nom) / nom     # per cent, signed
```

The arithmetic, in the order it happens:

```
meas - nom          = 4900.0 - 4700.0  =  200.0            ohms
200.0 / 4700.0                         =  0.0425531914...  dimensionless
x 100                                  =  4.2553191489...  per cent
```

Note what `split()` handed back: three *strings*, including `'4700'`, which looks
exactly like a number and is not one. Skip the `float` calls and `meas - nom` fails
with a `TypeError` — which is the good outcome. The bad outcome is a program that
compares `'4900.0' < '4700'` and gets `False` by comparing them alphabetically, one
character at a time, with no error anywhere.

## Reporting it: the format mini-language

An f-string evaluates whatever is inside the braces and applies the format after the
colon:

```python
f"{err:.1f}"        # '4.3'          fixed point, one decimal
f"{err:+.1f}"       # '+4.3'         always show the sign
f"{err:8.3f}"       # '   4.255'     eight columns wide, three decimals
f"{4700:.2e}"       # '4.70e+03'     scientific
f"{7:04d}"          # '0007'         integer, zero-padded to four
f"{1234567:,}"      # '1,234,567'    thousands separators
f"{'R7':<6}"        # 'R7    '       left-aligned in six columns
f"{'R7':>6}"        # '    R7'       right-aligned in six columns
```

The general shape is `[align][width][.precision][type]`, and every part of it is
optional. Text defaults to left-aligned and numbers to right-aligned, which is the
convention that makes a column of figures readable — units line up under units, tens
under tens.

So the report line for the log entry above is one expression:

```python
print(f"{ref}: {meas:.0f} ohms, {err:+.1f} % of nominal")
# R7: 4900 ohms, +4.3 % of nominal
```

The crucial property is that formatting changes **the printed form only**. `err` is
still 4.25531914893617 afterwards, to the last bit. Report to two decimals and keep
computing with all of them; that is precisely the separation you want between what a
human reads and what the next line of code works on.

## Worked example: three rows that line up

The whole of the log, reported as a table. This is the shape of nearly every script
you will write in this course — read a line, convert it, compute something, report it
— and the only new thing in it is that the widths are stated:

```python
log = ["R1 4655.0 4700", "R2 2247.0 2200", "R3 3410.0 3300"]

print(f"{'ref':<4}{'measured':>9}{'nominal':>9}{'err %':>8}")
for line in log:
    ref, meas_s, nom_s = line.split()
    meas, nom = float(meas_s), float(nom_s)
    err = 100 * (meas - nom) / nom
    print(f"{ref:<4}{meas:>9.1f}{nom:>9.1f}{err:>8.2f}")
```

The arithmetic on each row, and what it prints:

```
R1:  100 x (4655 - 4700) / 4700  =  -0.9574468...  ->  '   -0.96'
R2:  100 x (2247 - 2200) / 2200  =   2.1363636...  ->  '    2.14'
R3:  100 x (3410 - 3300) / 3300  =   3.3333333...  ->  '    3.33'

ref  measured  nominal   err %
R1     4655.0   4700.0   -0.96
R2     2247.0   2200.0    2.14
R3     3410.0   3300.0    3.33
```

Three things to take from it. The header and the rows share their widths, so the
columns line up because you made them, not because the numbers happened to be similar
lengths — feed in a 470 kΩ part and the table still holds together. The `<` on the
reference and the `>` on the numbers is the ordinary convention, and reversing it makes
a table that is noticeably harder to scan. And `err` for R3 is 3.3333333333333335 in
the variable and `3.33` on the page: what you would put in a report and what you would
carry into the next calculation are two different numbers, and the f-string is the
only place they are allowed to differ.

## Worked example: the rounding you did not order

```python
f"{2/3:.2f}"        # '0.67'    as expected
f"{2.675:.2f}"      # '2.67'    ... not '2.68'
```

The second is not a bug in the formatter. Look at what `2.675` actually refers to:

```
stored value of 2.675 = 2.67499999999999982236431605997495353221893310546875
                        ^^^^^^ the digit after 2.67 is a 4, not a 5
so rounding that to two decimals correctly gives 2.67
```

The formatter rounded the number it was given, faithfully. The number it was given was
never 2.675 — the reading unit before this one explains why it could not have been.
The same effect appears in `round`, with a second cause on top: `round(0.5)` is `0`
and `round(2.5)` is `2`, because Python rounds halves to the nearest *even* result
rather than always upward, which stops a long column of roundings from drifting
systematically high.

## The mistake people actually make

Treating the formatted string as if it were the value. Two shapes of it:

- `float(f"{x:.2f}")` — formatting a number and parsing it back. This throws away the
  precision you paid for and replaces it with a number that has a short decimal
  spelling, which is not the same as an accurate one.
- comparing report lines instead of numbers: `f"{a:.2f}" == f"{b:.2f}"`. That is
  rounding to a grid and comparing grid squares, with all the edge behaviour the
  previous unit warned about — 4.994 and 4.996 differ by 0.04% and land in different
  squares.

Format for the human. Compare with a tolerance. They are separate jobs and the same
line of code cannot do both.

## Where this stops holding

- **`print` and the interpreter show you different things for the same value.** `print`
  uses `str`, the interpreter's echo uses `repr`, and for floats they now agree — both
  give the shortest string that round-trips. For other types they diverge: `print("a")`
  shows `a`, while the echo shows `'a'` with quotes. When you are debugging, the quotes
  are the information: they are what tells you the `4700` on the screen was text all
  along.
- **A formatted number is not a measurement.** `f"{v:.6f}"` on a reading from a meter
  with three digits of accuracy prints six digits, four of which are fiction. Formatting
  cannot add precision, and printing more digits than you have is a way of misleading
  the next reader — quite possibly you.
- **Reading text is not free.** Everything above assumes the line is shaped as you
  expected. `line.split()` with no argument splits on runs of whitespace and quietly
  ignores the ragged spacing a human left behind, which is why it suits a log; a CSV
  needs `line.split(",")`, and that one does *not* forgive whitespace, so
  `float(" 4700 ")` doing the stripping for you is the only reason it works at all. An
  empty line splits to an empty list, and the unpacking on the next line then fails
  with `ValueError: not enough values to unpack`. Real files have blank lines,
  comments, missing fields and commas where points should be. Module 6 reads a netlist
  properly, and module 7 is about what a program should do when the line it is handed
  is not the line it was promised.
''',
                },
            ],
            "quiz": {
                "title": "What the machine actually did",
                "minutes": 8,
                "questions": [
                    {
                        "q": "You run `n = 7` then `m = 2` then `print(n / m)`. What appears?",
                        "opts": ["3", "3.5", "4", "The text `n / m`"],
                        "a": 1,
                        "why": (
                            "`/` is true division and its result is always a float: 7 / 2 is 3.5, and even "
                            "4 / 2 is 2.0 rather than 2. The operator that throws the remainder away is `//`, "
                            "so 7 // 2 is 3. Choosing 3 is the common slip, and it comes from expecting "
                            "Python to guess that you wanted whole numbers. It never guesses."
                        ),
                    },
                    {
                        "q": "What does `0.1 + 0.2 == 0.3` evaluate to?",
                        "opts": ["True", "False", "0.30000000000000004", "It raises an error"],
                        "a": 1,
                        "why": (
                            "False. A float is stored as a sum of binary fractions, and 0.1 has no exact "
                            "binary form any more than one third has an exact decimal form. The stored "
                            "values are each a hair off, and the sum lands on 0.30000000000000004. Nothing "
                            "is broken and nothing can be fixed: this is what the arithmetic is. Compare "
                            "measured quantities with `abs(a - b) <= tol` instead."
                        ),
                    },
                    {
                        "q": "After `a = 5`, then `b = a`, then `a = 9`, what is `b`?",
                        "opts": ["9", "5", "It depends on what happens next", "It raises an error"],
                        "a": 1,
                        "why": (
                            "5. The line `b = a` bound the name `b` to the value `a` referred to at that "
                            "moment, which was 5. It did not tie the two names together. Rebinding `a` "
                            "afterwards changes only what `a` refers to. Answering 9 means reading `=` as "
                            "an equation to be maintained, which is what it means in mathematics and not "
                            "what it means here."
                        ),
                    },
                    {
                        "q": "What does `\"12\" + 3` do?",
                        "opts": ["Gives 15", "Gives the text `123`", "Gives the text `12 3`", "Raises a TypeError"],
                        "a": 3,
                        "why": (
                            "It raises a TypeError. `+` joins two strings and adds two numbers, but it has "
                            "no meaning for one of each, so Python refuses rather than picking one. "
                            "`int(\"12\") + 3` gives 15; `\"12\" + str(3)` gives the text 123. This matters the "
                            "moment you read numbers out of a file, because everything read from a file "
                            "arrives as text."
                        ),
                    },
                    {
                        "q": "What is the value of `f\"{2 / 3:.2f}\"`?",
                        "opts": ["The text `0.67`", "The number 0.67", "The text `0.6666666666666666`", "The text `2 / 3`"],
                        "a": 0,
                        "why": (
                            "The text `0.67`. An f-string evaluates what is inside the braces, applies the "
                            "format after the colon — here `.2f`, meaning fixed point to two decimals — and "
                            "produces a string. Note that it rounds only the printed form; the value 2 / 3 "
                            "itself is untouched, which is exactly what you want when reporting a result "
                            "without corrupting the calculation that produced it."
                        ),
                    },
                    {
                        "q": "You have two voltages, `measured` and `expected`, and you want to know whether they agree to within 1%. Which test is right?",
                        "opts": [
                            "`measured == expected`",
                            "`abs(measured - expected) <= 0.01 * abs(expected)`",
                            "`measured - expected <= 0.01`",
                            "`round(measured) == round(expected)`",
                        ],
                        "a": 1,
                        "why": (
                            "The relative test, `abs(measured - expected) <= 0.01 * abs(expected)`. It "
                            "asks the engineering question — is the gap small compared with the quantity — "
                            "and it is symmetric, so a reading above and a reading below are treated alike. "
                            "The version without `abs` lets the difference run as negative as it likes, so "
                            "any measurement that is far too low passes. Rounding turns a tolerance into a "
                            "step: 4.4 and 4.6 differ by "
                            "about 4% and round to 4 and 5, and 4.49 and 4.51 barely differ and round apart."
                        ),
                    },
                ],
            },
            "blanks": [
                {
                    "title": "One line of the log, checked",
                    "minutes": 9,
                    "lang": "python",
                    "caption": "check.py — four holes, and a printed line at the bottom that says what the filled-in version must produce",
                    "brief": r'''
A measurement arrives as text and leaves as a verdict. Between those two points the
value has to become a number, be compared with its nominal, and be reported to a human
— and each of those steps has one spelling that works and several that quietly do not.

Nothing runs here. The comment under the `print` is the anchor: every choice you make
has to be consistent with that exact line of output.
''',
                    "listing": r'''
# One line of the resistor log, checked against its nominal value.
line = "R7 4300.0 4700"

ref, meas_s, nom_s = line.split()

meas = ___(meas_s)                   # ohms, as a number
nom  = float(nom_s)

err  = 100 * (meas - nom) ___ nom    # signed, per cent
ok   = ___ <= 5.0                    # is it inside a 5% band?

print(f"{ref}: {meas:.0f} ohms, {err:___} % of nominal, ok={ok}")
# R7: 4300 ohms, -8.5 % of nominal, ok=False
''',
                    "blanks": [
                        {
                            "prompt": "`split` handed back strings. This one has a decimal point in it.",
                            "hole": "call",
                            "opts": ["float", "int", "str", "round"],
                            "a": 0,
                            "why": "`float(\"4300.0\")` gives 4300.0, which is a number and can be subtracted from another. Everything read from a file arrives as text, and this call is the boundary where it stops being text.",
                            "whys": [
                                "`float(\"4300.0\")` gives 4300.0, which is a number and can be subtracted from another. Everything read from a file arrives as text, and this call is the boundary where it stops being text.",
                                "`int` parses an integer literal, and `\"4300.0\"` is not one — it raises `ValueError: invalid literal for int() with base 10: '4300.0'`. The decimal point is fatal even though the value it spells is whole. `int(float(s))` works, and says out loud that you meant to truncate.",
                                "`str` of a string is the same string, so `meas` stays text and the program dies one line later on `meas - nom`, a `TypeError`. That is the good failure; the bad one is a program that compares two strings alphabetically and never complains at all.",
                                "`round` wants a number, not text, so this is a `TypeError` immediately. Rounding is something you do to a value after you have one.",
                            ],
                        },
                        {
                            "prompt": "The error as a fraction of nominal, kept as a decimal.",
                            "hole": "op",
                            "opts": ["/", "//", "%", "*"],
                            "a": 0,
                            "why": "`/` is true division and always yields a float: $100 \\times (4300 - 4700)/4700 = -8.5106\\ldots$, which prints as $-8.5$ exactly as the comment says.",
                            "whys": [
                                "`/` is true division and always yields a float: $100 \\times (4300 - 4700)/4700 = -8.5106\\ldots$, which prints as $-8.5$ exactly as the comment says.",
                                "`//` floors the result to a whole number, and it floors *downwards*: $-8.51$ becomes $-9.0$, not $-8.0$. The printed line would read `-9.0`, and the error would have grown in the rounding rather than shrunk.",
                                "`%` is the remainder, so this computes $-40000 \\bmod 4700 = 2300.0$ — a leftover in ohms-times-hundred, reported as though it were a percentage. It is the operator you want for wrapping an index round a buffer and never for this.",
                                "`*` multiplies where the units demand a division: $-40000 \\times 4700$, or $-1.88\\times10^{8}$. A result eight orders of magnitude out is the easy kind of mistake to catch, which is the only good thing about it.",
                            ],
                        },
                        {
                            "prompt": "A reading 8.5% BELOW nominal has to fail a 5% band, exactly as one 8.5% above would.",
                            "hole": "test",
                            "opts": ["abs(err)", "err", "round(err)", "abs(meas - nom)"],
                            "a": 0,
                            "why": "`abs(err)` compares the *size* of the deviation with the band, so 8.5 is tested against 5.0 and fails, giving the `ok=False` in the comment. Both directions are treated alike, which is what a tolerance means.",
                            "whys": [
                                "`abs(err)` compares the *size* of the deviation with the band, so 8.5 is tested against 5.0 and fails, giving the `ok=False` in the comment. Both directions are treated alike, which is what a tolerance means.",
                                "Without `abs`, the test reads $-8.51 \\le 5.0$, which is true — and would be true for a resistor reading zero. Dropping the `abs` does not loosen the test slightly; it removes the lower half of it entirely, and the printed line would say `ok=True`.",
                                "`round(err)` gives $-9$, and $-9 \\le 5$ is still true. Rounding has not fixed the missing `abs`, and it has thrown away the tenth of a per cent you might have wanted to report.",
                                "`abs(meas - nom)` is 400.0 — an amount in **ohms** being compared with 5.0, a number of **per cent**. It happens to give the right verdict here and gives the wrong one for any resistor smaller than about 100 Ω, where 400 Ω of error is enormous and every reading would still be rejected for the same reason.",
                            ],
                        },
                        {
                            "prompt": "One decimal place, in ordinary fixed-point notation.",
                            "hole": "format",
                            "opts": [".1f", ".0f", ".3f", ".2e"],
                            "a": 0,
                            "why": "`.1f` is fixed point to one decimal, so $-8.5106\\ldots$ prints as `-8.5`, which is what the comment shows. The value of `err` is untouched — formatting changes the report, never the number.",
                            "whys": [
                                "`.1f` is fixed point to one decimal, so $-8.5106\\ldots$ prints as `-8.5`, which is what the comment shows. The value of `err` is untouched — formatting changes the report, never the number.",
                                "`.0f` gives `-9`: no decimals at all, and a tenth of a per cent of resolution thrown away in a line whose whole purpose is to say how far off the part is.",
                                "`.3f` gives `-8.511`, which is three decimals of a quantity derived from a four-digit reading. It is not wrong, it is over-claiming: two of those digits are noise dressed as measurement.",
                                "`.2e` gives `-8.51e+00`, correct and unreadable. Scientific notation earns its place when the exponent is doing work, and here the exponent is zero.",
                            ],
                        },
                    ],
                },
                {
                    "title": "A 5% resistor, and whether these two are inside the band",
                    "minutes": 8,
                    "lang": "text",
                    "caption": "the same test as `close_enough`, one line at a time",
                    "brief": r'''
A tolerance printed on a part is a **fraction of that part's own nominal value**, not
a fixed number of ohms. That is the whole reason the comparison in the lab is written
`abs(a - b) <= tol_frac * abs(b)` rather than with a constant on the right: 5% of a
4.7 kΩ resistor is 235 Ω, and 5% of a 47 Ω resistor is 2.35 Ω, and a
single absolute figure cannot serve both.

Fill in the arithmetic below, then read the two calls at the bottom that say the same
thing in code.
''',
                    "listing": r'''
a resistor marked 4k7, tolerance 5%, and two of them measured
-------------------------------------------------------------

  nominal      = 4k7
               = ___ ohms

  allowed gap  = 5% of nominal
               = ___ * 4700              the tolerance as a FRACTION
               = 235 ohms                so anything from 4465 to 4935 passes

  sample A     = 4935 ohms
  gap          = abs(4935 - 4700)  =  235
  test         = 235 <= 235        ->  ___

  sample B     = 4462 ohms
  gap          = abs(4462 - 4700)  =  ___
  test         = 238 <= 235        ->  False

  and the same two verdicts, from the function you are about to write:

  close_enough(4935, ___, 0.05)    ->  True
  close_enough(4462, 4700, 0.05)   ->  False
''',
                    "blanks": [
                        {
                            "prompt": "`4k7` in ohms.",
                            "hole": "value",
                            "opts": ["4700", "47", "4.7", "470000"],
                            "a": 0,
                            "why": "The `k` stands for kilo and takes the place of the decimal point, so `4k7` is 4.7 kΩ, or 4700 Ω. Writing the multiplier where the point goes is deliberate: a smudged or photocopied decimal point has lost circuits, and a `k` cannot fall off.",
                            "whys": [
                                "The `k` stands for kilo and takes the place of the decimal point, so `4k7` is 4.7 kΩ, or 4700 Ω. Writing the multiplier where the point goes is deliberate: a smudged or photocopied decimal point has lost circuits, and a `k` cannot fall off.",
                                "47 Ω would be written `47R` or just `47`. Losing the `k` costs a factor of a hundred here, and the giveaway is downstream: 47 Ω across 5 V draws over 100 mA, which no divider is meant to do.",
                                "4.7 is the mantissa with the multiplier dropped. It is the number you say out loud — 'four point seven k' — and not the number you compute with.",
                                "470000 Ω is `470k`. The exponent is the part of a value most often got wrong and least often noticed, because every wrong reading of `4k7` still has a 4 and a 7 in it.",
                            ],
                        },
                        {
                            "prompt": "5%, written as the fraction the code multiplies by.",
                            "hole": "frac",
                            "opts": ["0.05", "5", "0.5", "1.05"],
                            "a": 0,
                            "why": "Per cent means per hundred, so 5% is $5/100 = 0.05$, and $0.05 \\times 4700 = 235$ Ω. Every tolerance handed to code should be a fraction, because that is the form that multiplies straight into the value with no stray factor of a hundred anywhere.",
                            "whys": [
                                "Per cent means per hundred, so 5% is $5/100 = 0.05$, and $0.05 \\times 4700 = 235$ Ω. Every tolerance handed to code should be a fraction, because that is the form that multiplies straight into the value with no stray factor of a hundred anywhere.",
                                "5 as a bare number makes the allowed gap $5 \\times 4700 = 23500$ Ω — five times the resistor itself. A test that generous passes anything, and it will pass quietly for years.",
                                "0.5 is 50%, ten times the tolerance printed on the part. This is the same error as the one above, made once instead of twice.",
                                "1.05 is the *multiplier* that turns nominal into the top of the band: $4700 \\times 1.05 = 4935$. It is a useful number and it is not a tolerance; used here it would allow a gap larger than the resistor.",
                            ],
                        },
                        {
                            "prompt": "The gap is exactly equal to the allowed gap. Does it pass?",
                            "hole": "bool",
                            "opts": ["True", "False"],
                            "a": 0,
                            "why": "`<=` includes the boundary, so a part exactly on the edge of its band passes. That matches how a tolerance is specified — 4935 Ω is a legal 5% 4k7 — and it is why the comparison is written `<=` rather than `<`. Note that a real 4935 Ω reading is not exactly 235 away in floating point either, which is one more reason never to lean on an exact boundary in a real spec.",
                            "whys": [
                                "`<=` includes the boundary, so a part exactly on the edge of its band passes. That matches how a tolerance is specified — 4935 Ω is a legal 5% 4k7 — and it is why the comparison is written `<=` rather than `<`. Note that a real 4935 Ω reading is not exactly 235 away in floating point either, which is one more reason never to lean on an exact boundary in a real spec.",
                                "That would be the answer if the test were `<`, which is the one place the two spellings differ. A part sitting precisely on its stated limit is within specification, so the inclusive comparison is the right one.",
                            ],
                        },
                        {
                            "prompt": "The size of the gap for sample B, in ohms.",
                            "hole": "gap",
                            "opts": ["238", "-238", "242", "4462"],
                            "a": 0,
                            "why": "$|4462 - 4700| = |-238| = 238$ Ω, which is 3 Ω outside the 235 Ω band. The part is 5.06% low, so it fails — just.",
                            "whys": [
                                "$|4462 - 4700| = |-238| = 238$ Ω, which is 3 Ω outside the 235 Ω band. The part is 5.06% low, so it fails — just.",
                                "$-238$ is the signed difference, and `abs` is there precisely to remove the sign. Left signed, $-238 \\le 235$ is true and the part passes a band it is outside — the exact failure the `abs` in `close_enough` exists to prevent.",
                                "242 would be the gap from 4704, not from 4700. Worth checking your subtraction: 4700 − 4462 = 238.",
                                "4462 is the reading itself. Comparing a reading with a tolerance rather than comparing the *deviation* with it is a units error — ohms against ohms-of-allowed-error — and it rejects every part ever made.",
                            ],
                        },
                        {
                            "prompt": "Which value does `close_enough` measure the reading against?",
                            "hole": "ref",
                            "opts": ["4700", "4935", "235", "0.05"],
                            "a": 0,
                            "why": "The tolerance is a fraction *of the nominal*, so the nominal 4700 is the reference the gap is scaled by. `close_enough(4935, 4700, 0.05)` asks whether 4935 is within 5% of 4700, which is the question the part's marking poses.",
                            "whys": [
                                "The tolerance is a fraction *of the nominal*, so the nominal 4700 is the reference the gap is scaled by. `close_enough(4935, 4700, 0.05)` asks whether 4935 is within 5% of 4700, which is the question the part's marking poses.",
                                "Passing 4935 as its own reference makes the gap zero and the test true for any tolerance at all — a check that cannot fail, which proves nothing about the resistor.",
                                "235 is the allowed gap in ohms, already computed. Handing it in as the reference would ask whether 4935 is within 5% of 235 Ω, which is a question about nothing.",
                                "0.05 is the tolerance, and it belongs in the third argument where it already is. Two arguments of the same call carrying the same value is a sign the arguments have been shuffled.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Six to a board, forty-seven on the tape",
                    "minutes": 4,
                    "brief": r'''
One operator, one answer, and nothing to convert. The only thing that can go wrong is
picking the wrong one of the three ways Python can divide.
''',
                    "prompt": "What number does this program print?",
                    "note": "A whole number of boards.",
                    "figure": r'''
```python
tape      = 47      # resistors on the reel
per_board = 6       # each board takes six of them

print(tape // per_board)
```

`//` divides and throws the remainder away. `%` keeps only the remainder, and `/`
keeps everything and hands back a float.
''',
                    "given": [
                        {"label": "Resistors on the tape", "value": "47"},
                        {"label": "Resistors per board", "value": "6"},
                        {"label": "Operator", "value": "//"},
                    ],
                    "aside": "Sanity check whatever you get: the boards you can build, times six, plus "
                             "the ones left over, must come back to 47.",
                    "answer": 7.0,
                    "tol": 0.01,
                    "unit": "boards",
                    "hint": "How many complete groups of six fit inside 47? The remainder is not part of the answer — that is what `%` would give you.",
                    "wrong": "7.83 is what `/` gives, and there is no such thing as 0.83 of a populated "
                             "board. 5 is what `%` gives — the five resistors left on the tape once "
                             "seven boards have been built.",
                    "why": "$47 // 6 = 7$. Check it the way you would check any integer division: "
                           "$7 \\times 6 = 42$ resistors used, $47 - 42 = 5$ left over, and $42 + 5 = 47$. "
                           "That identity, $(a // b) \\times b + a \\% b = a$, holds for every pair of "
                           "whole numbers, and between them the two operators account for every item on "
                           "the reel. Note also the type of what came back: `//` on two ints gives an "
                           "int, and an int is what you need if the answer is about to be used as a count "
                           "— `range(47 / 6)` is a TypeError, while `range(47 // 6)` runs seven times.",
                },
                {
                    "title": "What the f-string prints",
                    "minutes": 6,
                    "brief": r'''
Two steps: the arithmetic, then the formatting. The formatting is not decoration here
— the question asks for what appears on the screen, and that is a different number
from the one in the variable.
''',
                    "prompt": "What number does this program print?",
                    "note": "Exactly as printed, to two decimal places.",
                    "figure": r'''
```python
vin = 9.0           # volts
r1  = 4700.0        # ohms, the upper resistor
r2  = 2200.0        # ohms, the lower resistor

vout = vin * r2 / (r1 + r2)
print(f"{vout:.2f}")
```

`{vout:.2f}` means: take the value of `vout` and write it in fixed point with two
decimal places. It rounds; it does not chop.
''',
                    "given": [
                        {"label": "vin", "value": "9.0 V"},
                        {"label": "r1 (upper)", "value": "4700 Ω"},
                        {"label": "r2 (lower)", "value": "2200 Ω"},
                        {"label": "Format", "value": ".2f"},
                    ],
                    "aside": "Do the bracket first. The resistor next to the output is the one on top of "
                             "the fraction.",
                    "answer": 2.87,
                    "tol": 0.005,
                    "unit": "V",
                    "hint": "$9.0 \\times 2200 = 19800$, and $4700 + 2200 = 6900$. Divide, then round the "
                            "result to two decimals rather than cutting it off.",
                    "wrong": "2.86 is the answer you get by chopping the third decimal off instead of "
                             "rounding it. 6.13 is what comes out if the two resistors change places — "
                             "the one across the output belongs on top.",
                    "why": "$9.0 \\times 2200 / 6900 = 2.869565217391304$, and `.2f` rounds that to "
                           "**2.87**. Two things are worth taking away. The value in `vout` is unchanged "
                           "by the printing: it is still 2.8695652... to the last bit, and every later "
                           "calculation uses all of it. And that stored value is not the exact value of "
                           "the fraction $19800/6900$ either, because $6900$ does not divide $19800$ a "
                           "power of two number of times — no float ever holds that fraction exactly. "
                           "Neither fact matters at two decimal places, which is the ordinary situation: "
                           "the digits you report are far coarser than the digits you carry.",
                },
                {
                    "title": "How many of the five boards pass?",
                    "minutes": 8,
                    "brief": r'''
Five boards come off the line and each one's 5 V rail is measured. The test is the
relative comparison from this module, written out in full, and the answer is a count
rather than a voltage.

Work through the readings one at a time and keep the allowed gap in volts in front of
you. Two of them are worth arguing about.
''',
                    "prompt": "How many of the five readings pass the test?",
                    "note": "A count, from 0 to 5.",
                    "figure": r'''
```python
NOM = 5.00                                  # volts, what the rail should be
readings = [5.06, 4.89, 5.10, 4.93, 5.21]   # volts, five boards

passed = 0
for v in readings:
    if abs(v - NOM) <= 0.02 * NOM:          # inside +/- 2% of nominal
        passed += 1

print(passed)
```
''',
                    "given": [
                        {"label": "Nominal", "value": "5.00 V"},
                        {"label": "Tolerance", "value": "2% of nominal"},
                        {"label": "Readings", "value": "5.06, 4.89, 5.10, 4.93, 5.21 V"},
                    ],
                    "aside": "Compute the allowed gap once, in volts, before you look at a single "
                             "reading. It is the same for all five.",
                    "answer": 3.0,
                    "tol": 0.01,
                    "unit": "readings",
                    "hint": "$0.02 \\times 5.00 = 0.10$ V. Now take $|v - 5.00|$ for each reading and "
                            "compare it with 0.10, remembering that `<=` lets the boundary through.",
                    "wrong": "4 is what you get by dropping the `abs`: $v - 5.00 \\le 0.10$ is satisfied "
                             "by every reading below the nominal, however far below, so 4.89 sneaks "
                             "through. 2 comes from reading `<=` as `<` and rejecting the reading that "
                             "sits exactly on the limit.",
                    "why": "The allowed gap is $0.02 \\times 5.00 = 0.10$ V, so the band is 4.90 V to "
                           "5.10 V inclusive.\n\n"
                           "```\n"
                           "5.06   gap 0.06   <= 0.10   pass\n"
                           "4.89   gap 0.11   >  0.10   fail\n"
                           "5.10   gap 0.10   <= 0.10   pass   exactly on the limit\n"
                           "4.93   gap 0.07   <= 0.10   pass\n"
                           "5.21   gap 0.21   >  0.10   fail\n"
                           "```\n\n"
                           "Three pass. The reading on the limit is the interesting one. `<=` admits it, "
                           "which is what a stated tolerance means: a part sitting exactly on its "
                           "published limit is in specification. But look at what the machine actually "
                           "compared. The limit $0.02 \\times 5.00$ is exactly the double nearest 0.1, "
                           "while the gap $|5.10 - 5.00|$ evaluates to 0.09999999999999964 — neither "
                           "number is the one on the page, and this time the wobble happened to fall "
                           "inwards. Nothing about the board decided that. A specification whose verdict "
                           "turns on a reading sitting precisely on its own limit is a badly written "
                           "specification: widen the band or tighten the line, and do not ask the last "
                           "bit of a float to make an engineering decision.",
                },
                {
                    "title": "Where the clock actually stops",
                    "minutes": 9,
                    "brief": r'''
A simulation advances its clock by 0.1 s a step and stops when the clock reaches 1.0 s.
Written out it looks obviously correct, and if floats held decimals exactly it would
be.

The question is not how many steps were intended. It is what value `t` holds when the
loop finally lets go — and answering it needs the direction of the error, not just
its existence.
''',
                    "prompt": "What is the value of t after the loop finishes?",
                    "note": "In seconds, to one decimal place.",
                    "figure": r'''
```python
t = 0.0
while t < 1.0:
    t += 0.1        # advance the clock by one step

print(t)
```

Adding 0.1 ten times does not give exactly 1.0: each addition rounds to the nearest
double, and the roundings do not cancel. In this case the running total lands a hair
**below** one — `0.9999999999999999`.
''',
                    "given": [
                        {"label": "Start", "value": "t = 0.0 s"},
                        {"label": "Step", "value": "0.1 s"},
                        {"label": "Loop continues while", "value": "t < 1.0"},
                        {"label": "Ten steps of 0.1 give", "value": "0.9999999999999999"},
                    ],
                    "aside": "The test happens before each pass, on the value t holds at that moment. "
                             "Ask what the tenth pass leaves behind, and whether that value gets past "
                             "the test.",
                    "answer": 1.1,
                    "tol": 0.005,
                    "unit": "s",
                    "hint": "After ten additions t is 0.9999999999999999, which is still less than 1.0, "
                            "so the loop runs once more. Each pass adds one more step of 0.1.",
                    "wrong": "1.0 is the answer if the ten additions are assumed to land exactly on one. "
                             "They land just under it, and `while t < 1.0` looks at the value rather than "
                             "at your intention. 0.9 comes from counting the additions but stopping one "
                             "early.",
                    "why": "The loop runs **eleven** times, not ten, and finishes with `t` at "
                           "1.0999999999999999 — 1.1 s to any precision you would report.\n\n"
                           "```\n"
                           "after  9 additions   t = 0.8999999999999999   < 1.0, so continue\n"
                           "after 10 additions   t = 0.9999999999999999   < 1.0, so continue (!)\n"
                           "after 11 additions   t = 1.0999999999999999   loop ends\n"
                           "```\n\n"
                           "One extra pass is not a rounding detail. It is a whole extra sample on the "
                           "end of the run, at a time 10% past where the simulation was supposed to "
                           "stop, and every summary computed afterwards — mean, RMS, final value "
                           "— includes it. The repair is never to accumulate a float you intend to "
                           "compare: count in integers and derive the time from the count, "
                           "`t = i * dt` with `i` running over `range(10)`. That gives exactly ten "
                           "samples, always, and the last one is at 0.9 s, where it belongs. Module 8 "
                           "integrates a differential equation with this loop and is written that way "
                           "for this reason.",
                },
            ],
            "derive": {
                "title": "How wrong is the answer, if the readings are 1% out?",
                "minutes": 12,
                "vars": ["a", "b", "a_m", "b_m", "P", "alpha", "beta", "epsilon"],
                "brief": r'''
The module says to compare measured quantities with a tolerance rather than with `==`.
It does not say what tolerance, and that is the question an engineer actually has to
answer. If two readings are each good to 1%, how good is something computed from them?

Write the true values as $a$ and $b$, and the numbers your meter reports as

$$a_m = a(1 + \alpha) \qquad b_m = b(1 + \beta)$$

so $\alpha$ and $\beta$ are the *relative* errors: $\alpha = 0.01$ means the reading is
1% high. Nothing below is about floating point, which sits fourteen orders of magnitude
lower down and never joins in. This is about the instrument.

Write each answer as an expression in the symbols named.
''',
                "steps": [
                    {
                        "prompt": "The program multiplies the two readings together. Write that product, $a_m b_m$, in terms of $a$, $b$, $\\alpha$ and $\\beta$, leaving the brackets as they stand.",
                        "answer": "a b (1 + \\alpha)(1 + \\beta)",
                        "hint": "Substitute the two definitions and collect the true values at the front. Do not multiply the brackets out yet.",
                    },
                    {
                        "prompt": "The true product is $P = ab$. Write the relative error of the computed product, $(a_m b_m - P)/P$, as an expression in $\\alpha$ and $\\beta$ alone, with the brackets multiplied out.",
                        "answer": "\\alpha + \\beta + \\alpha \\beta",
                        "hint": "Divide your last answer by $ab$ and the true values disappear. What is left is $(1+\\alpha)(1+\\beta) - 1$.",
                        "deconstruct": [
                            "$\\dfrac{a_m b_m}{P} = \\dfrac{ab(1+\\alpha)(1+\\beta)}{ab} = (1+\\alpha)(1+\\beta)$.",
                            "$(1+\\alpha)(1+\\beta) = 1 + \\alpha + \\beta + \\alpha\\beta$.",
                            "Subtracting the 1 leaves $\\alpha + \\beta + \\alpha\\beta$, which is the relative error of the product.",
                        ],
                    },
                    {
                        "prompt": "Suppose each reading is good to a relative error of at most $\\epsilon$ in size, so $|\\alpha| \\le \\epsilon$ and $|\\beta| \\le \\epsilon$. Write the largest value that expression can take, in terms of $\\epsilon$.",
                        "answer": "2 \\epsilon + \\epsilon^{2}",
                        "hint": "Every term is at its largest when both errors are at $+\\epsilon$. Substitute $\\alpha = \\beta = \\epsilon$ and keep all three terms.",
                        "deconstruct": [
                            "Putting $\\alpha = \\beta = \\epsilon$ gives $\\epsilon + \\epsilon + \\epsilon^2$.",
                            "That is $2\\epsilon + \\epsilon^2$ — and the second term is the one everybody drops, correctly, once they have seen how small it is.",
                        ],
                    },
                    {
                        "prompt": "Now a ratio rather than a product — a resistance computed as a voltage over a current, say. Write $\\dfrac{a_m/b_m}{a/b} - 1$ as a single fraction in $\\alpha$ and $\\beta$.",
                        "answer": "\\frac{\\alpha - \\beta}{1 + \\beta}",
                        "hint": "The true values cancel as before, leaving $\\dfrac{1+\\alpha}{1+\\beta} - 1$. Put the 1 over the same denominator and subtract.",
                        "deconstruct": [
                            "$\\dfrac{a(1+\\alpha)}{b(1+\\beta)} \\times \\dfrac{b}{a} = \\dfrac{1+\\alpha}{1+\\beta}$.",
                            "$\\dfrac{1+\\alpha}{1+\\beta} - \\dfrac{1+\\beta}{1+\\beta} = \\dfrac{(1+\\alpha)-(1+\\beta)}{1+\\beta}$.",
                            "The ones cancel on the top, leaving $\\dfrac{\\alpha-\\beta}{1+\\beta}$.",
                        ],
                    },
                    {
                        "prompt": "$\\beta$ is a per cent or so, so the denominator is 1 to within that same per cent. Set $\\beta = 0$ in the denominator only, and write what remains.",
                        "answer": "\\alpha - \\beta",
                        "hint": "Only the bottom of the fraction changes. The top is left exactly as it is.",
                    },
                ],
                "closing": r'''
Put 1% into both results and look at what you have.

```
product,  both readings 1% out:   2 x 0.01 + 0.01^2  =  0.02 + 0.0001
                                                     =  2.01 %

quotient, worst case is alpha = +1%, beta = -1%:
                                  0.01 - (-0.01)     =  2.00 %
```

Two things fall out of that, and both are worth keeping.

**Relative errors add.** Multiply or divide two quantities and their percentage errors
add — in the worst case, when the two happen to lean the same way for a product or
opposite ways for a quotient. Three measured quantities in an expression, each 1%, and
you should expect 3%. This is the arithmetic behind the rule of thumb every lab manual
states without proof.

**The $\epsilon^2$ term is real and negligible.** At 1% it contributes 0.0001, which is
one two-hundredth of the 0.02 beside it. Dropping it is not sloppiness; it is a
decision you can now defend with a number, and it is what "to first order" means
everywhere it appears in engineering. It stops being negligible when $\epsilon$ stops
being small — at 50% tolerance the correction is a quarter of the answer.

Now use it. When you call `close_enough(measured, expected, tol_frac)`, the tolerance
you pass is not a matter of taste: it is the sum of the relative errors of everything
that fed the calculation, plus whatever the process itself is allowed to vary by. A 1%
tolerance on a value computed from two 1% resistors will reject correct code roughly
half the time, and you will spend a day hunting a bug that is not there. Meanwhile the
floating-point noise from the previous reading unit is around $10^{-16}$, which is one
part in a hundred trillion of the 2% you have just derived. It disappears into this
tolerance without trace, which is the real reason a tolerance comparison is the right
tool: it was always going to be needed for the physics, and it absorbs the arithmetic
for nothing.
''',
            },
            "lab": {
                "title": "Resistors, and the numbers that describe them",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
Four small functions. Nothing here is longer than two lines, and the point is
getting the types and the comparison right rather than the algebra.

`parallel(r1, r2)` returns the resistance of two resistors side by side, which is
`r1 * r2 / (r1 + r2)`.

`divider_out(vin, r1, r2)` returns the voltage at the joint of two resistors in a
line, with `vin` applied across the pair and the far end of `r2` at zero. That
voltage is `vin * r2 / (r1 + r2)`. You will build this circuit for real in the next
module.

`close_enough(a, b, tol_frac)` returns `True` when `a` and `b` agree to within
`tol_frac` as a fraction of `b` — so `tol_frac=0.01` means one per cent. Use
`abs`, and never `==`.

`describe(vin, r1, r2)` returns one line of text, in exactly this form:

```text
15.0 V in, 5.000 V out
```

That is the supply to one decimal place, then the divider output to three.
''',
                "files": [{"name": "main.py", "content": r'''
def parallel(r1, r2):
    """Resistance of r1 and r2 side by side, in ohms."""
    # TODO: r1 * r2 / (r1 + r2)
    return 0.0


def divider_out(vin, r1, r2):
    """Voltage at the joint of r1 and r2, with vin across the pair."""
    # TODO: vin * r2 / (r1 + r2)
    return 0.0


def close_enough(a, b, tol_frac=0.01):
    """True when a is within tol_frac (a fraction, not a percentage) of b."""
    # TODO: compare the size of the gap with the size of b. Use abs on both.
    return False


def describe(vin, r1, r2):
    """One line: the supply to 1 decimal, then the output to 3."""
    vout = divider_out(vin, r1, r2)
    # TODO: build the string with an f-string.
    return ""


if __name__ == "__main__":
    print("two 1k in parallel:", parallel(1000.0, 1000.0), "ohms")
    print(describe(15.0, 20000.0, 10000.0))
    print("0.1 + 0.2 == 0.3 ?", 0.1 + 0.2 == 0.3)
    print("close_enough(0.1 + 0.2, 0.3) ?", close_enough(0.1 + 0.2, 0.3, 1e-9))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def parallel(r1, r2):
    """Resistance of r1 and r2 side by side, in ohms."""
    return r1 * r2 / (r1 + r2)


def divider_out(vin, r1, r2):
    """Voltage at the joint of r1 and r2, with vin across the pair."""
    return vin * r2 / (r1 + r2)


def close_enough(a, b, tol_frac=0.01):
    """True when a is within tol_frac (a fraction, not a percentage) of b."""
    return abs(a - b) <= abs(b) * tol_frac


def describe(vin, r1, r2):
    """One line: the supply to 1 decimal, then the output to 3."""
    vout = divider_out(vin, r1, r2)
    return f"{vin:.1f} V in, {vout:.3f} V out"


if __name__ == "__main__":
    print("two 1k in parallel:", parallel(1000.0, 1000.0), "ohms")
    print(describe(15.0, 20000.0, 10000.0))
    print("0.1 + 0.2 == 0.3 ?", 0.1 + 0.2 == 0.3)
    print("close_enough(0.1 + 0.2, 0.3) ?", close_enough(0.1 + 0.2, 0.3, 1e-9))
'''}],
                "hints": [
                    "Two equal resistors in parallel come to half of one of them, so `parallel(1000, 1000)` must be 500.0. That is the quickest way to tell whether you have the formula upside down.",
                    "In `divider_out` the resistor next to the output is `r2`, so `r2` is on top of the fraction. If your answer grows when `r1` grows, you have swapped them.",
                    "`close_enough` needs `abs` twice: once on the gap, once on `b`, so a negative `b` does not silently make the tolerance negative and reject everything.",
                    "The format after the colon in an f-string is the whole trick: `f\"{x:.3f}\"` gives three decimals.",
                ],
                "tests": [
                    {"name": "two equal resistors halve", "code": r'''
_p = parallel(1000.0, 1000.0)
assert abs(_p - 500.0) < 1e-9, f"1k beside 1k is 500 ohms, got {_p}"
'''},
                    {"name": "a small resistor dominates a large one", "code": r'''
_p = parallel(1000.0, 1.0)
assert abs(_p - 0.999000999000999) < 1e-12, \
    f"1 ohm beside 1k is just under 1 ohm, got {_p}"
'''},
                    {"name": "the divider divides the right way round", "code": r'''
_v = divider_out(15.0, 20000.0, 10000.0)
assert abs(_v - 5.0) < 1e-12, f"20k over 10k from 15 V gives 5 V, got {_v}"
_e = divider_out(9.0, 4700.0, 4700.0)
assert abs(_e - 4.5) < 1e-12, f"two equal resistors halve the supply, got {_e}"
_b = divider_out(15.0, 10000.0, 20000.0)
assert abs(_b - 10.0) < 1e-12, \
    f"swapping the resistors must change the answer to 10 V, got {_b} - check which one is on top"
'''},
                    {"name": "close_enough forgives float noise but not real error", "code": r'''
assert close_enough(0.1 + 0.2, 0.3, 1e-9), \
    "0.1 + 0.2 differs from 0.3 by about 5.5e-17, which is well inside 1e-9"
assert not close_enough(5.0, 4.0, 0.01), "5 and 4 are 25% apart, not 1%"
assert close_enough(4.96, 5.0, 0.01), "4.96 is 0.8% below 5.0"
assert not close_enough(4.9, 5.0, 0.01), "4.9 is 2% below 5.0"
'''},
                    {"name": "close_enough is symmetric", "code": r'''
assert close_enough(4.0, 5.0, 0.5) and close_enough(6.0, 5.0, 0.5), \
    "4 and 6 are each one unit from 5, well inside a 50% tolerance, so both must pass"
assert not close_enough(4.0, 5.0, 0.01), \
    "4.0 is 20% below 5.0 and must fail a 1% tolerance; without abs on the gap it passes"
assert not close_enough(6.0, 5.0, 0.01), \
    "and 6.0 is 20% above 5.0, so it must fail in exactly the same way"
'''},
                    {"name": "describe formats exactly as specified", "code": r'''
_s = describe(15.0, 20000.0, 10000.0)
assert _s == "15.0 V in, 5.000 V out", f"expected '15.0 V in, 5.000 V out', got {_s!r}"
_t = describe(3.3, 1000.0, 2000.0)
assert _t == "3.3 V in, 2.200 V out", f"expected '3.3 V in, 2.200 V out', got {_t!r}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Choices, loops and functions",
            "summary": "Three constructs cover almost everything: do this if that, do this many times, and give a piece of work a name.",
            "concepts": [
                "`if` / `elif` / `else` runs the first branch whose condition is true and skips the rest, so the order of the branches is part of the meaning.",
                "Indentation is the grouping. The indented lines under an `if` are its body; there are no braces and no `end`.",
                "`for x in range(n)` repeats the body `n` times, with `x` taking 0, 1, ... n-1. `range(a, b, step)` counts from `a` up to but not including `b`.",
                "`while` repeats for as long as its condition holds, so something inside the body must eventually make it false.",
                "A function is a named piece of work. `return` hands a value back; a function with no `return` hands back `None`.",
                "A name first assigned inside a function is local to that call and disappears when the call ends.",
                "A *search* is the pattern behind most engineering code: try every candidate, score each one, keep the best.",
            ],
            "read": [
                {
                    "title": "Three readings, three verdicts, and the order of the questions",
                    "minutes": 12,
                    "body": r'''
A board comes off the line and its 5 V rail is measured. The meter says 5.06 V. Is
that a good board?

Nothing written so far can answer that. Arithmetic produces numbers, and a number is
not a decision. Every program that does anything useful with a measurement eventually
has to take one action rather than another because of what it just read, and `if` is
the whole of that idea: a fork in the road, with a test at the fork.

## The condition is a value, not a question

The smallest useful version is two lines:

```python
v = 5.06
if v > 5.10:
    print("too high")
```

The part after `if` is not a question the language interprets specially. It is an
ordinary expression, worked out exactly the way `v * 2` is worked out, and what comes
back is a value of type `bool`:

```python
>>> v = 5.06
>>> v > 5.10
False
>>> type(v > 5.10)
<class 'bool'>
```

`>` is an operator like `*`. It takes two numbers and produces `True` or `False`.
`if` then does exactly one thing with that value: run the indented block if it is
true, skip it if it is false. There are six of these operators — `<`, `<=`, `>`,
`>=`, `==`, `!=` — and they can be combined with `and`, `or` and `not`, which take
bools and give bools back.

Seeing the condition as a value rather than as syntax pays off immediately. You can
print it, store it, or hand it to a function, and `passed = v <= 5.10` is a perfectly
ordinary line that binds a name to `True` or `False`.

## Indentation is the grouping

The indented lines under an `if` are its body. The indentation is the only thing that
says so: there are no braces, no `begin`, no `end`. A line dedented back to the left
margin is outside the `if` and runs whichever way the test went.

```python
v = 5.06
if v > 5.10:
    print("too high")
    print("reject the board")    # indented: only for a high reading
print("measurement logged")      # not indented: printed for every reading
```

For `v = 5.06` that program prints one line, `measurement logged`. Move the last
`print` four spaces right and it prints nothing at all. This is the one place in the
language where whitespace changes meaning, and it is a deliberate trade: the layout
that everybody uses to make a program readable is the layout the machine reads too,
so the two can never disagree.

## Worked example 1: three readings through one classifier

The rail is nominally 5.00 V and the specification allows 2%. Two per cent of 5.00 V
is $0.02 \times 5.00 = 0.10$ V, so any reading from 4.90 V to 5.10 V inclusive is a
good board, and there are three verdicts to hand out rather than two.

```python
NOM  = 5.00                  # volts, what the rail should be
BAND = 0.02 * NOM            # volts, the allowed departure: 0.10

if v > NOM + BAND:           # above 5.10 V
    verdict = "high"
elif v < NOM - BAND:         # below 4.90 V
    verdict = "low"
else:
    verdict = "in spec"
```

Three boards, and every test each one is actually put through, in the order the
machine does them:

```
v = 5.06 V
   5.06 > 5.10 ?   False    skip the body, go on to the next test
   5.06 < 4.90 ?   False    skip the body, fall through to else
   verdict = "in spec"

v = 5.21 V
   5.21 > 5.10 ?   True     verdict = "high"
                            and nothing further is tested at all

v = 4.89 V
   4.89 > 5.10 ?   False
   4.89 < 4.90 ?   True     verdict = "low"
```

Look at what did not happen to the 5.21 V board. Once a branch of an `if`/`elif`
chain is taken, the rest of the chain is skipped without being evaluated — not
evaluated and found false, but never looked at. The chain is one decision with three
possible outcomes, not three separate decisions.

A fourth board is worth adding, because it is the one that decides how the code
should be written:

```
v = 5.10 V   (exactly on the upper limit)
   5.10 > 5.10 ?   False    strictly greater, and it is not strictly greater
   5.10 < 4.90 ?   False
   verdict = "in spec"
```

A part sitting exactly on its published limit is inside specification, and the strict
`>` is what says so. Had it been written `>=`, that board would be scrapped. Which
also means: never build a test whose verdict turns on a reading landing precisely on
its own limit. In real floating point, $0.02 \times 5.00$ and a meter's 5.10 are two
numbers whose last bits nobody controls.

## elif, and the branch that can never run

Why `elif` at all? Three separate `if` statements look like the same thing, and for
conditions that cannot both be true they behave identically. The difference shows up
the moment the conditions overlap:

```python
if v > 0:
    print("positive")
elif v > 5:
    print("big")
```

The second branch cannot run for any value of `v` whatsoever. Anything greater than 5
is also greater than 0, so the first test catches it and the chain stops. Trace two
values and compare them with the same two tests put the other way round:

```
v       v > 5    v > 0     as written above     narrowest condition first
12.0    True     True      "positive"           "big"
 3.0    False    True      "positive"           "positive"
```

The rule this gives you: **in an `if`/`elif` chain, put the most specific condition
first.** The classifier in worked example 1 obeys it — `v > 5.10` is a narrower claim
than "not in spec", and the catch-all `else` is last, where a catch-all belongs.

Nothing complains about the broken version. It is not a syntax error, it runs to
completion, and it prints a plausible word every time. There is no warning for a
branch that cannot be reached, which is what makes this worth recognising by eye.

## Worked example 2: two conditions that must both hold

The build in this module asks for a divider that reads 5.00 V from a 15 V supply
*and* draws between 0.2 mA and 1.5 mA. Two requirements, and a candidate has to
satisfy both:

```python
VIN = 15.0

def ok(r1, r2):
    vout = VIN * r2 / (r1 + r2)
    i    = VIN / (r1 + r2)
    return abs(vout - 5.0) <= 0.10 and 2e-4 <= i <= 1.5e-3
```

Three candidate pairs, all of them with exactly the right ratio:

```
r1 = 20 kOhm, r2 = 10 kOhm
   total = 30 kOhm
   vout  = 15.0 x 10000 / 30000    = 5.000 V    |5.000 - 5| = 0.000 <= 0.10   True
   i     = 15.0 / 30000            = 0.500 mA   0.2 <= 0.500 <= 1.5           True
   True and True                                                        -> pass

r1 = 200 kOhm, r2 = 100 kOhm
   total = 300 kOhm
   vout  = 15.0 x 100000 / 300000  = 5.000 V                                  True
   i     = 15.0 / 300000           = 0.050 mA   below 0.2 mA                  False
   True and False                                                       -> fail

r1 = 2 kOhm, r2 = 1 kOhm
   total = 3 kOhm
   vout  = 15.0 x 1000 / 3000      = 5.000 V                                  True
   i     = 15.0 / 3000             = 5.000 mA   above 1.5 mA                  False
   True and False                                                       -> fail
```

All three divide 15 V into 5 V exactly. Only one of them is a circuit anybody would
build, and the other two fail for opposite reasons: the 300 kΩ pair is so weak that
anything you connect to it drags the output down, and the 3 kΩ pair burns 75 mW
holding a voltage nobody asked it to hold. The ratio was never the whole
specification, and `and` is how a program says so.

Two details about `and` are worth having now. It **short-circuits**: in
`if r1 + r2 > 0 and VIN * r2 / (r1 + r2) > 3`, when the left side is false the right
side is never evaluated, so the division by zero never happens. That is a guarantee
about evaluation order, not an optimisation, and guarding a risky expression with a
cheap test to its left is a standard use of it. And `2e-4 <= i <= 1.5e-3` is a real
chained comparison in Python: `i` is evaluated once and tested against both ends. In
C the same line silently means something else, which is why people arriving from
there write it as two comparisons joined by `and` — also correct, and one character
longer.

## The mistake people actually make

Two, and they are unrelated.

The first is ordering an `if`/`elif` chain the way the cases occurred to you, which
is nearly always widest first, because the general case is the one you thought of
first. The unreachable branch that results is invisible in the source and quiet at
run time. Read every chain from the top and ask what the *first* test lets through.

The second is `==` on a measured or computed float. The closest divider you can build
from stock resistors gives $15 \times 3300 / 10100 = 4.900990099009901$ V, so
`if vout == 5.0` is `False` and always will be, and a program that tests for success
that way rejects the best circuit available. It is tempting because equality is the
natural English for "is it the right value", and because `if n == 0` on an integer
count works perfectly, which is where most people meet `==` first. Measured
quantities get a band: `abs(vout - 5.0) <= 0.10`.

## Where this stops holding

- **Truthiness is not what you want here.** `if v:` is legal and treats `0.0` as
  false, so a rail measured at exactly 0.00 V — a dead board, the single most
  important case — would be skipped in silence. Test the thing you mean:
  `if v > 0:`, or `if v is not None:` when the question is whether a reading exists
  at all.
- **`and` and `or` work on one value at a time.** In module 6 a whole array of
  readings is classified at once, and `readings > 5.10` becomes an array of bools.
  Feeding that to `and` raises a ValueError about an ambiguous truth value; the
  element-by-element `&` and `|` replace it, with brackets round each comparison. The
  idea survives, the spelling does not.
- **A chain of `elif`s decides between a handful of named cases.** When the cases are
  ten, or arrive from a file rather than from you, the chain becomes a dictionary
  lookup, which is module 3.
- **None of this survives a reading that is not a number.** A blank line in a log, or
  a meter that returned `OL` for over-range, fails inside `float(...)` before your
  `if` gets a look at it. Module 8 is about what a program should do then.
''',
                },
                {
                    "title": "A loop is a stopping rule with work attached",
                    "minutes": 13,
                    "body": r'''
You want the current a 15 V supply pushes through each of seven candidate resistors.
You could write the division seven times. At seventy you would not, and at seven
hundred thousand — one per sample of a measured waveform — the idea is not merely
tedious, it is impossible. So the line gets written once, and something else decides
how many times it runs.

That is all a loop is: **a piece of work, and a rule that says when to stop.** Python
spells the rule two ways, and which one you reach for depends on a single question —
do you know the number of repetitions before you start?

## for, and why range stops early

When the answer is yes, `for` takes the count off your hands:

```python
for r in range(1000, 10001, 1500):
    print(r, 15.0 / r)
```

`range(start, stop, step)` produces values beginning at `start`, adding `step` each
time, and **stopping before `stop`**. The name `r` is bound to each value in turn,
and the body runs once for each.

That the stop value is excluded is the detail everyone gets wrong once. It is not an
arbitrary choice. Three things fall out of it, and all three are worth more than the
convenience of counting to ten:

- `range(n)` produces exactly `n` values, so the count is written on the page.
- `range(a, b)` produces exactly $b - a$ values, so a length is a subtraction with no
  correction term.
- `range(0, 5)` and `range(5, 10)` fit together with no overlap and no gap, which is
  what lets you split a run of samples in two without arguing about who owns the
  join.

The same convention is why array indices start at 0: `range(len(readings))` lands on
every element exactly once, from the first to the last, with no `+ 1` anywhere.

## Worked example 1: the sweep, and the seven values it visits

Here is the sweep above, worked all the way out. The supply is 15.0 V and the current
through each candidate is $I = V/R$:

```
r        15.0 / r          in mA
-------------------------------------
 1000    0.015             15.000
 2500    0.006              6.000
 4000    0.00375            3.750
 5500    0.002727...        2.727
 7000    0.002142...        2.143
 8500    0.001764...        1.765
10000    0.0015             1.500
```

Seven passes. Count them without listing: the values run from 1000 up to 10000 in
steps of 1500, so the number of steps taken is $(10000 - 1000)/1500 = 6$, and the
number of *values* is one more than the number of steps, 7. The fence-post count —
seven posts, six gaps — is the arithmetic behind every off-by-one there is.

Now look at the stop value: it is 10001, not 10000. Write `range(1000, 10000, 1500)`
instead and the last value produced is 8500; the 10 kΩ candidate, the only one in the
whole sweep that meets the build's 1.5 mA ceiling, is silently missing. Nothing
errors. The program prints six tidy lines and the answer is wrong. When the endpoint
matters, push `stop` past it.

## The accumulator, and the three places its lines live

A loop that only prints is rare. Usually something is being built up across the
passes, and that shape is always the same three lines in the same three places:

```python
total = 0.0                              # before: start from nothing
for r in range(1000, 10001, 1500):
    total = total + 15.0 / r             # inside: fold this pass into the running value
print(total * 1000, "mA")                # after: use it, once the loop is done
```

Run on the sweep above, the seven currents add to 32.885 mA — the current the supply
would deliver if all seven resistors hung across it at once. The `total = total + x`
line is exactly the counter from module 1, and reads the same way: work out the right
side using the value `total` has *now*, then re-bind the name. `total += 15.0 / r` is
the same line, shorter.

Both of the ways to get this wrong are about placement rather than arithmetic. Put
`total = 0.0` inside the loop and it is reset on every pass, so what comes out is the
last term rather than the sum — 1.5 mA instead of 32.885 mA, which is a plausible
enough number to survive a review. Put the `print` inside and you get seven lines of
partial sums, the last of which happens to be right.

## while, when you do not know how many

Sometimes the count is the thing you are trying to find. The build asks for a total
resistance that keeps the supply current at or below 1 mA; you can solve that in your
head, but the general shape of the question — *keep going until a condition is
satisfied* — is exactly what `while` is for.

```python
VIN = 15.0
r = 1000.0
i = VIN / r
while i > 1.0e-3:        # while the current is still too big
    r = r + 1000.0       # try the next 1 kOhm step up
    i = VIN / r          # and re-measure
print(r, i)
```

## Worked example 2: raising the resistance until the current is legal

The condition is tested *before* each pass, on the values the names hold at that
moment. Traced:

```
                r          i = 15.0 / r      i > 1.0e-3 ?
before loop      1000       15.000 mA         True   -> run the body
after pass  1    2000        7.500 mA         True
after pass  2    3000        5.000 mA         True
   ...
after pass 12   13000        1.154 mA         True
after pass 13   14000        1.071 mA         True   -> still too big, run once more
after pass 14   15000        1.000 mA         False  -> stop
```

Fourteen passes, and `r` finishes at 15000.0 Ω with the current at exactly 1.000 mA.
The last two rows are the whole question. At 14 kΩ the current is 1.071 mA, which is
over the limit by 7%, so the loop keeps going; at 15 kΩ it is 1.000 mA, and
`1.000e-3 > 1.000e-3` is false, so the loop lets go. A limit written with `>` admits
the value that sits exactly on it.

Two things about `while` follow directly from the fact that nothing counts for you.

**Something in the body must move the condition towards false.** Delete the
`i = VIN / r` line and `i` stays at 0.015 for ever; the loop runs until you kill the
program, and Python neither notices nor objects, because a runaway loop is a logic
error and not a syntax error. A `for` loop cannot fail this way, which is the reason
to prefer one whenever the count is known.

**Never let the condition rest on an accumulated float.** Module 1 showed
`while t < 1.0` with `t += 0.1` running eleven times instead of ten. The trace above
is safe only because 1000.0 added to itself is exact in binary and 15.0/15000.0 lands
exactly on 0.001. Change the step to 1100.0 and the reasoning changes with it. When
the count is knowable, count in integers and derive the quantity from the count.

## The search, which is most engineering code in disguise

Put the two together — a loop that visits candidates and an accumulator that
remembers the best one — and you have the pattern behind an enormous amount of real
work, including this module's lab:

```python
best = None
best_error = None
for r1 in values:                       # every candidate for the upper resistor
    for r2 in values:                   # crossed with every candidate for the lower
        error = abs(divider_out(vin, r1, r2) - vtarget)
        if best_error is None or error < best_error:
            best_error = error          # a new champion; remember both parts of it
            best = (r1, r2)
```

Three ideas, none of them new: try every candidate, score each one, keep the best.
The `best_error is None` test handles the first candidate, which has nothing to beat.

Count the work. The inner loop runs all the way through for *each* pass of the outer
one, so with $n$ candidate values the body runs $n^2$ times. The E12 values from
1 kΩ to 100 kΩ number 25, so the search scores $25^2 = 625$ pairs, which is nothing.
Widen the range to 1 MΩ and $n = 37$, giving 1369. Nesting a third loop for a
three-resistor network would make it $n^3 = 50653$, still bearable — and a fourth
would not be. Exhaustive search is the right tool exactly as long as you can afford
to count how expensive it is.

## The mistake people actually make

**Re-binding the loop variable and expecting the loop to care.**

```python
for r in range(1000, 10001, 1500):
    r = r * 2          # has no effect on which values come next
```

Every pass begins by binding `r` to the next value from the range, throwing away
whatever you put there. This is module 1's rule with no exceptions: `=` is an event,
not a relationship, and the loop performs its own `=` at the top of each pass. If you
want the doubled value, give it its own name.

**Reading `range(1, 10, 3)` as "up to 10".** It gives 1, 4, 7. The next value would
be 10, and `stop` is never produced. The tell is that the answer often *looks* right
— a list of the correct shape, one item short.

## Where this stops holding

- **A loop over indices when you wanted the items.**
  `for i in range(len(parts)): p = parts[i]` is correct and clumsy;
  `for p in parts:` says the same thing and cannot go out of bounds. Module 3 covers
  iterating over containers directly, which is what you will use nine times in ten.
- **A `while` whose condition depends on a float that the body accumulates.** Above.
  It is the commonest way a loop runs one pass too many, and the fix is structural,
  not a smaller epsilon.
- **$n^2$ stops being affordable.** When the candidate list is large the answer is
  not a faster loop; it is fewer candidates. This module's derivation removes an
  entire loop from the search with two lines of algebra, and module 10 replaces
  "try everything" with methods that aim: bisection and Newton, which reach an answer
  in tens of steps rather than thousands.
- **A loop over a million samples in Python is slow enough to notice**, because the
  interpreter re-examines every line on every pass. Module 6 writes the same
  arithmetic as one array expression, gets identical numbers, and hands the looping
  to compiled code. The loop does not go away; it stops being written by you.
''',
                },
                {
                    "title": "Giving a piece of work a name",
                    "minutes": 11,
                    "body": r'''
By the end of this module the expression `vin * r2 / (r1 + r2)` has appeared in a
quiz question, in a circuit you drew, in the lab you are about to write, and inside a
search that evaluates it six hundred times. Four appearances is four chances to swap
the two resistors, and — worse — four places to visit when you discover you did.

A function is the fix, and it is a small idea: **give a piece of work a name, so that
the work exists in exactly one place.** Everything else about functions follows from
taking that seriously.

## What def does, and what a call does

```python
def divider_out(vin, r1, r2):
    """Voltage at the joint of r1 and r2, with vin across the pair."""
    return vin * r2 / (r1 + r2)
```

The `def` line runs once, when Python reads it, and it does something very close to
what `=` does: it binds the name `divider_out` to a value which happens to be a
function. The body does not run. Nothing is computed. `vin`, `r1` and `r2` are
*parameters* — names with no values yet, waiting for a call to supply them.

A call is where the work happens, and it has four steps:

1. evaluate the arguments at the call site;
2. bind the parameter names to those values, in order;
3. run the body until a `return`;
4. hand that value back, and discard the names.

## Worked example 1: one call, all four steps

```python
v = divider_out(15.0, 20000.0, 10000.0)
```

```
step 1   arguments evaluate to    15.0        20000.0        10000.0
step 2   bind, by position        vin = 15.0  r1 = 20000.0   r2 = 10000.0
step 3   run the body
             r1 + r2             = 20000.0 + 10000.0 = 30000.0
             vin * r2            = 15.0 * 10000.0    = 150000.0
             150000.0 / 30000.0                      = 5.0
step 4   return 5.0; vin, r1 and r2 cease to exist
         the caller binds v = 5.0
```

Now the same function, same three numbers, two of them exchanged:

```
divider_out(15.0, 10000.0, 20000.0)
    vin = 15.0   r1 = 10000.0   r2 = 20000.0
    15.0 * 20000.0 / 30000.0  =  10.0 V
```

Ten volts rather than five. Nothing has gone wrong inside the function: arguments are
matched to parameters **by position**, so the order in the call is part of the
contract, and `r2` — the resistor across the output — is the one on top of the
fraction. The function also has no idea that any of this is volts and ohms. It
multiplies and divides three numbers you supplied, and the meaning is yours to keep
straight, exactly as in module 1.

## return is not print

This is the distinction that catches everybody, and it is worth being blunt about.
`print` puts characters on a screen for a human. `return` hands a *value* back to the
program. A function that prints its result and returns nothing looks correct when you
run it by hand and is useless to everything else:

```python
def divider_out_broken(vin, r1, r2):
    print(vin * r2 / (r1 + r2))       # no return

v = divider_out_broken(15.0, 20000.0, 10000.0)   # screen shows 5.0
print(v * 2)
```

`5.0` appears on the screen, so the first line looks fine. But a function that ends
without a `return` hands back `None`, so `v` is `None`, and the last line dies with
`TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'` — an error
naming a line that has nothing wrong with it, about a type you never mentioned. The
distance between the cause and the symptom is what makes this expensive.

There is a practical consequence for this course: every lab's tests call your
function and inspect what it returned. A function that prints the right answer and
returns `None` fails every test, and the failure message will be about `NoneType`.

## Names inside a call belong to that call

```python
def measure():
    reading = 4.7
    return reading

measure()
print(reading)        # NameError: name 'reading' is not defined
```

A name first assigned inside a function is *local*: created when the call starts,
destroyed when it ends, invisible from outside. `measure()` did produce 4.7 and did
hand it back — the value was simply dropped on the floor, because the call was
written as a statement rather than as the right-hand side of an assignment.
`reading = measure()` is the whole repair.

That isolation is the point rather than a restriction. It is what allows the search
loop to use `r1` and `r2` while the function it calls uses `r1` and `r2` for its own
parameters, with no interference and no coordination between the two. Ten functions
can each have a loop counter called `i` and none of them can disturb another.

## Worked example 2: the swap, and what it costs

Suppose the scoring line inside the search is written with its arguments the wrong
way round — a single transposition, the easiest typo in engineering:

```python
error = abs(divider_out(vin, r2, r1) - vtarget)      # r2 and r1 exchanged
```

Chasing 5.00 V from a 15 V supply with E12 parts, the search now reports the pair
`(3300.0, 6800.0)` — 3.3 kΩ on top, 6.8 kΩ underneath — and claims it gives 4.9010 V.
Both halves of that sentence come from the same wrong line:

```
what the search scored:   divider_out(15.0, 6800.0, 3300.0)
                        = 15.0 * 3300 / (6800 + 3300)   = 4.9010 V     looks perfect

what the drawing says:    3.3 kOhm upper, 6.8 kOhm lower
what the board does:      15.0 * 6800 / (3300 + 6800)   = 10.0990 V
```

Ten volts into a part expecting five. The search was not wrong about arithmetic; it
scored a different circuit from the one it reported. And notice where the repair
goes: one line, in one place, and every one of the 625 candidates is re-scored
correctly the next time it runs. Had the formula been typed out inline at each of the
four places it appears in this module, fixing three of them and missing the fourth is
the likely outcome — and the fourth is the one that gets built.

## Defaults, and calling with fewer arguments

The lab's search is declared like this:

```python
def best_pair(vin, vtarget, lo=1e3, hi=1e5):
```

`lo` and `hi` have **default values**, so `best_pair(15.0, 5.0)` is a legal call that
searches 1 kΩ to 100 kΩ, while `best_pair(15.0, 5.0, 1e4, 1e6)` overrides both.
Defaults are for the choice a caller usually does not want to make. They are
evaluated once, when the `def` runs — which is harmless for a number and a trap for a
list, one that module 3 comes back to once lists exist.

## The mistake people actually make

Computing the answer and not returning it. It is tempting because the function is
finished from the author's point of view — the arithmetic is right there, on the last
line — and because the interactive prompt echoes the value of the last expression,
which trains the eye to believe the value escaped. It did not. If a value is supposed
to leave a function, some `return` has to say so.

Its close cousin is reaching for a local name after the call, above. Both come from
the same picture: a function as a region of the program where things happen, rather
than as a machine with two openings — arguments in, a returned value out. Everything
else it touches is its own.

## Where this stops holding

- **The local rule is about names, not about objects.** Rebinding a parameter inside
  a function cannot affect the caller, but *mutating* something the caller passed in
  can. There is nothing in this module you can mutate, which is why the rule looks
  absolute here; module 3 introduces lists and the exception with them.
- **A function that reads a module-level constant works until a second value of it
  exists.** Writing `VIN` straight into the body instead of taking `vin` as a
  parameter is fine for one supply rail and wrong the day the same board runs from
  3.3 V. The lab's `divider_out` takes the supply as an argument for exactly this
  reason.
- **Calls are not free.** One call costs a fraction of a microsecond, which is
  invisible at 625 of them and very visible at ten million. Module 6 is largely about
  not calling a Python function once per array element: the same arithmetic, written
  as one array expression, hands the repetition to compiled code and runs in
  milliseconds where the loop takes seconds.
''',
                },
            ],
            "quiz": {
                "title": "Reading control flow",
                "minutes": 9,
                "questions": [
                    {
                        "q": "How many lines does `for i in range(3): print(i)` print, and what is the last one?",
                        "opts": ["3 lines, last is 3", "3 lines, last is 2", "4 lines, last is 3", "2 lines, last is 2"],
                        "a": 1,
                        "why": (
                            "Three lines: 0, 1 and 2. `range(3)` means three values starting at 0, and the "
                            "value 3 is the stopping point rather than one of the items. Expecting 1, 2, 3 "
                            "is the single most common off-by-one error in Python, and it is why array "
                            "indices also start at 0: `range(len(a))` then lands on every element exactly once."
                        ),
                    },
                    {
                        "q": "With `v = 5.5`, what does this print?\n\n```python\nif v > 0:\n    print(\"positive\")\nelif v > 5:\n    print(\"big\")\nelse:\n    print(\"other\")\n```",
                        "opts": ["`positive`", "`big`", "Both `positive` and `big`", "`other`"],
                        "a": 0,
                        "why": (
                            "Only `positive`. An `if`/`elif` chain stops at the first true condition, and "
                            "5.5 > 0 is true, so the `elif` is never tested. The branch that says `big` can "
                            "never run for any value at all, because anything greater than 5 is also greater "
                            "than 0. Chains like this are written narrowest condition first."
                        ),
                    },
                    {
                        "q": "What does this print?\n\n```python\ndef double(x):\n    y = 2 * x\n\nprint(double(4))\n```",
                        "opts": ["8", "`None`", "Nothing at all", "It raises an error"],
                        "a": 1,
                        "why": (
                            "`None`. The function computes `y` and then ends without a `return`, so the call "
                            "hands back `None`, Python's word for no value. Computing something is not the "
                            "same as returning it. This is worth recognising on sight, because the symptom "
                            "downstream is usually a confusing TypeError about `NoneType` somewhere far "
                            "from the function that caused it."
                        ),
                    },
                    {
                        "q": "Which values does `range(1, 10, 3)` produce?",
                        "opts": ["1, 3, 6, 9", "1, 4, 7", "1, 4, 7, 10", "3, 6, 9"],
                        "a": 1,
                        "why": (
                            "1, 4 and 7. The three arguments are start, stop and step: begin at 1, add 3 "
                            "each time, and stop before reaching 10. The next value would be 10, and stop "
                            "is never included, so it does not appear. Reading the third argument as the "
                            "first value produced is the usual confusion."
                        ),
                    },
                    {
                        "q": "What happens here?\n\n```python\nn = 0\nwhile n < 3:\n    print(n)\n```",
                        "opts": [
                            "It prints 0, 1, 2",
                            "It prints 0 once",
                            "It prints 0 forever",
                            "It raises an error because n never changes",
                        ],
                        "a": 2,
                        "why": (
                            "It prints 0 forever. A `while` loop re-tests its condition and nothing in the "
                            "body changes `n`, so the condition stays true. Python does not notice and does "
                            "not object; a runaway loop is a logic error, not a syntax error. Every `while` "
                            "needs something in the body that moves it towards ending, which is exactly what "
                            "a `for` loop gives you for free."
                        ),
                    },
                    {
                        "q": "Why does this raise a NameError on the last line?\n\n```python\ndef measure():\n    reading = 4.7\n    return reading\n\nmeasure()\nprint(reading)\n```",
                        "opts": [
                            "`reading` is spelled differently inside the function",
                            "`reading` is local to the call and does not exist outside it",
                            "The function was called without storing its result",
                            "`print` cannot show a float",
                        ],
                        "a": 1,
                        "why": (
                            "A name first assigned inside a function belongs to that call and vanishes when "
                            "the call ends, so there is no `reading` outside. The way to get the value out "
                            "is the `return`, which is already there — the call just needs to be written as "
                            "`reading = measure()`. This isolation is a feature: two functions can both use "
                            "the name `i` without interfering."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "The search, one decision at a time",
                "minutes": 9,
                "lang": "python",
                "caption": "four candidate values instead of twenty-five, so the whole trace fits on a page",
                "brief": r'''
This is the shape of the lab's `best_pair`, cut down to four candidate resistors so
that every pair can be checked by hand. It is the pattern from the reading unit —
try every candidate, score it, keep the best — with the four decisions that make it
work left blank.

Run it in your head as you fill it in. With these four values the winner is
4.7 kΩ over 2.2 kΩ, which gives $15.0 \times 2200 / 6900 = 4.7826$ V: not 5 V, and
the closest 5 V that four resistors can reach.
''',
                "listing": r'''
values  = [1000.0, 2200.0, 3300.0, 4700.0]   # ohms, four candidates
vin     = 15.0                               # volts, the supply
vtarget = 5.0                                # volts, what we want at the joint

best       = None
best_error = ___              # nothing has been scored yet

for r1 in values:             # r1 is the upper resistor
    for r2 in values:         # r2 is the lower one, next to the output
        out   = vin * r2 / (r1 + r2)
        error = ___           # how far this candidate lands from the target
        if best_error is None or error ___ best_error:
            best_error = error
            best       = ___  # what has to be remembered about the winner

# the two loops between them run the body ___ times
print(best, round(best_error, 4))     # (4700.0, 2200.0) 0.2174
''',
                "blanks": [
                    {
                        "prompt": "The score to beat, before anything has been scored.",
                        "hole": "start",
                        "opts": ["None", "0.0", "error", "vtarget"],
                        "a": 0,
                        "why": "`None` is Python's word for no value, and it is what the `best_error is None` test on the line below is looking for. The first candidate then wins by default, having nothing to be compared with, and every candidate after it is judged against a real score.",
                        "whys": [
                            "`None` is Python's word for no value, and it is what the `best_error is None` test on the line below is looking for. The first candidate then wins by default, having nothing to be compared with, and every candidate after it is judged against a real score.",
                            "Starting at 0.0 says the best pair found so far is a perfect one. Since no error can be smaller than zero, nothing ever beats it, and the search returns `None` after examining every pair — a loop that runs correctly and answers nothing.",
                            "`error` does not exist yet on this line; it is created inside the inner loop. Using it here raises a NameError before the first pass. A running best has to be initialised outside the loop, from something that already exists.",
                            "`vtarget` is 5.0, a voltage, and this name is about to hold an error in volts. It does not crash, and here it even gives the right pair, because the winning error of 0.2174 V is comfortably under 5 and the true champion still gets through. It is a seeded score rather than an initialisation: a target that no available pair reaches to within 5 V would come back as `None` from a search that examined every candidate.",
                        ],
                    },
                    {
                        "prompt": "The score itself: how far this pair lands from the target.",
                        "hole": "score",
                        "opts": ["abs(out - vtarget)", "out - vtarget", "vtarget - out", "abs(out) - vtarget"],
                        "a": 0,
                        "why": "A distance has no sign. `abs(out - vtarget)` is how far the candidate is from 5 V whichever side it lands on, so 4.78 V scores 0.2174 and 5.22 V would score 0.2174 as well, which is what makes the two comparable.",
                        "whys": [
                            "A distance has no sign. `abs(out - vtarget)` is how far the candidate is from 5 V whichever side it lands on, so 4.78 V scores 0.2174 and 5.22 V would score 0.2174 as well, which is what makes the two comparable.",
                            "Left signed, a candidate that undershoots scores negative, and the further below the target it falls the better it looks. The search would settle on the pair that gets closest to 0 V — here 4.7 kΩ over 1 kΩ, giving 2.63 V — and report it as the best 5 V divider available.",
                            "This is the same error with the sign reversed: now every overshoot scores negative and the winner is whichever pair comes closest to the supply rail. Reversing which way the bug points does not remove it.",
                            "`abs` applied to `out` alone does nothing at all here, because a divider output from a positive supply is already positive. The quantity that needs its sign removed is the difference, so the bracket has to close after `vtarget`.",
                        ],
                    },
                    {
                        "prompt": "The comparison that decides whether this candidate displaces the champion.",
                        "hole": "cmp",
                        "opts": ["<", ">", "<=", "=="],
                        "a": 0,
                        "why": "A smaller error is a better candidate, so a new champion is one whose score is strictly less than the best so far. Strictly, rather than `<=`, so that an exactly equal candidate does not displace the one already found — with `<` the first pair encountered wins any tie, and the answer no longer depends on the order the list happened to be in.",
                        "whys": [
                            "A smaller error is a better candidate, so a new champion is one whose score is strictly less than the best so far. Strictly, rather than `<=`, so that an exactly equal candidate does not displace the one already found — with `<` the first pair encountered wins any tie, and the answer no longer depends on the order the list happened to be in.",
                            "Keeping the candidate with the *larger* error searches for the worst divider in the list. It runs, it prints a pair, and the pair is 1 kΩ over 4.7 kΩ, whose output of 12.37 V is as far from 5 V as these four values can manage.",
                            "This keeps the last of any tied group rather than the first. It is not wrong in the sense of missing the best score, but the pair it reports depends on the order of `values`, so re-sorting the candidate list changes the published design.",
                            "`==` keeps a candidate only when it ties exactly, so nothing ever improves on the first score recorded. Equality between two computed floats is also the comparison module 1 spent a whole reading unit warning about.",
                        ],
                    },
                    {
                        "prompt": "What the search has to remember about the winner.",
                        "hole": "keep",
                        "opts": ["(r1, r2)", "out", "error", "r1 + r2"],
                        "a": 0,
                        "why": "The answer to the question is a pair of resistors, so both have to be kept, and a tuple holds the two together in the order the divider needs them. Keep only what you will need afterwards and the search has to be run again to find out what to order.",
                        "whys": [
                            "The answer to the question is a pair of resistors, so both have to be kept, and a tuple holds the two together in the order the divider needs them. Keep only what you will need afterwards and the search has to be run again to find out what to order.",
                            "`out` is the voltage this pair produces, which is worth reporting and cannot be built. Two different pairs can give the same output, so the voltage does not identify the design.",
                            "`error` is already being kept on the line above, in `best_error`. Storing it twice loses the one piece of information the caller actually asked for.",
                            "The total resistance sets the current but not the ratio: 6.9 kΩ could be 4700 over 2200 or 2200 over 4700, and those two divide 15 V into 4.78 V and 10.22 V. A sum cannot be taken apart again.",
                        ],
                    },
                    {
                        "prompt": "How many times the body of the inner loop runs in total.",
                        "hole": "count",
                        "opts": ["16", "8", "4", "12"],
                        "a": 0,
                        "why": "The inner loop runs all the way through for every pass of the outer one, so with four values the count is $4 \\times 4 = 16$. That includes the four pairs where `r1` and `r2` are the same resistor, which are legal dividers giving half the supply. In general $n$ candidates cost $n^2$ scorings, which is why the lab's 25 values mean 625 of them.",
                        "whys": [
                            "The inner loop runs all the way through for every pass of the outer one, so with four values the count is $4 \\times 4 = 16$. That includes the four pairs where `r1` and `r2` are the same resistor, which are legal dividers giving half the supply. In general $n$ candidates cost $n^2$ scorings, which is why the lab's 25 values mean 625 of them.",
                            "Eight is $4 + 4$, which is what nesting would cost if the two loops ran one after the other instead of one inside the other. Written as they are, the inner loop restarts on every pass of the outer.",
                            "Four is the number of passes of the outer loop alone. Each of those passes carries a whole inner loop with it.",
                            "Twelve is $4 \\times 3$, the count if a pair were forbidden from using the same value twice. Nothing here forbids it, and `r1 = r2 = 1000` is a perfectly good divider — it just gives 7.5 V rather than 5 V.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "The last value the sweep reaches",
                    "minutes": 4,
                    "brief": r'''
One rule, one unknown. The whole question is what `range` does with its three
arguments, and the only trap is the stop value.
''',
                    "prompt": "What is the last resistance this sweep visits?",
                    "note": "In ohms.",
                    "figure": r'''
```python
for r in range(1000, 10001, 1500):
    print(r, 15.0 / r)      # ohms, and the current in amps
```

`range(start, stop, step)` begins at `start`, adds `step` each time, and stops
**before** `stop`.
''',
                    "given": [
                        {"label": "Start", "value": "1000"},
                        {"label": "Stop", "value": "10001"},
                        {"label": "Step", "value": "1500"},
                    ],
                    "aside": "Write the values out. There are not many of them, and counting the steps "
                             "from 1000 is quicker than reasoning about the endpoint in the abstract.",
                    "answer": 10000.0,
                    "tol": 1.0,
                    "unit": "Ω",
                    "hint": "1000, 2500, 4000, ... keep adding 1500 and stop as soon as the next value "
                            "would reach 10001.",
                    "wrong": "8500 is the last value if the stop is read as 10000 rather than 10001 — "
                             "which is exactly what `range(1000, 10000, 1500)` would give you. 11500 is "
                             "one step too far: the loop never produces a value at or past `stop`.",
                    "why": r'''
The values are 1000, 2500, 4000, 5500, 7000, 8500, 10000 — seven of them, and the
last is **10000 Ω**. Count without listing if you prefer: $(10000 - 1000)/1500 = 6$
steps, and seven values sit at the ends of six steps.

The stop of 10001 is doing real work. `range` never produces a value at or past
`stop`, so `range(1000, 10000, 1500)` would end at 8500 and the 10 kΩ candidate — the
only one in the sweep that keeps the supply current down to the 1.5 mA the build asks
for — would silently never be tried. Nothing errors; the program prints six tidy
lines and the answer is wrong.

The exclusive stop is not an inconvenience to be worked around. It is what makes
`range(n)` produce exactly $n$ values and `range(a, b)` exactly $b - a$ of them, and
what lets `range(0, 5)` and `range(5, 10)` tile a run of ten samples with no overlap
and no gap. When you want the endpoint included, push `stop` past it — one past is
enough, and `10001` is the conventional way to say so.
''',
                },
                {
                    "title": "Where the while loop lets go",
                    "minutes": 7,
                    "brief": r'''
A `while` loop counts nothing for you. It re-tests its condition before every pass,
on the values the names hold at that moment, and stops the first time the test comes
out false.

The question is not how many passes were intended. It is what `r` holds when the loop
finally releases — which needs the boundary reasoned about, not just the trend.
''',
                    "prompt": "What value does r hold when the loop finishes?",
                    "note": "In ohms.",
                    "figure": r'''
```python
VIN = 15.0

r = 1000.0
i = VIN / r
while i > 1.0e-3:        # while the supply current is still above 1 mA
    r = r + 1000.0       # try the next kilohm up
    i = VIN / r          # and work out the new current

print(r)
```

The build wants the supply current at or below 1 mA. Here the search for a resistance
that achieves it is done by stepping.
''',
                    "given": [
                        {"label": "Supply", "value": "15.0 V"},
                        {"label": "Starting resistance", "value": "1000 Ω"},
                        {"label": "Step", "value": "1000 Ω"},
                        {"label": "Loop continues while", "value": "i > 1.0 mA"},
                    ],
                    "aside": "Work out the resistance at which the current is exactly 1 mA first, then "
                             "decide whether the loop stops at that value or one step past it.",
                    "answer": 15000.0,
                    "tol": 1.0,
                    "unit": "Ω",
                    "hint": "$15.0 / r = 1.0 \\times 10^{-3}$ A gives $r = 15$ kΩ. The test is "
                            "`i > 1.0e-3`, so ask whether a current of exactly 1.000 mA keeps the loop "
                            "running.",
                    "wrong": "14000 is where the loop would stop if the test were `i >= 1.0e-3`; at "
                             "14 kΩ the current is 1.071 mA, still above the limit, so the body runs "
                             "again. 16000 comes from carrying on one pass after the condition has "
                             "already gone false — the test happens before each pass, not after.",
                    "why": r'''
The loop makes fourteen passes and leaves `r` at **15000 Ω**, with the current at
exactly 1.000 mA.

```
                r          i = 15.0 / r     i > 1.0e-3 ?
before loop      1000       15.000 mA        True   -> run the body
after pass  1    2000        7.500 mA        True
after pass  2    3000        5.000 mA        True
   ...
after pass 13   14000        1.071 mA        True   -> still too big, run once more
after pass 14   15000        1.000 mA        False  -> stop
```

The last two rows are the whole question. At 14 kΩ the current is
$15.0/14000 = 1.0714$ mA, over the limit by 7%, so the body runs again. At 15 kΩ it is
$15.0/15000 = 1.000$ mA exactly, and `1.0e-3 > 1.0e-3` is false, so the loop lets go
with the limit met rather than beaten. A condition written with `>` admits the value
sitting exactly on it.

Two things this loop is only just getting away with. Deleting the `i = VIN / r` line
would leave `i` at 0.015 for ever and the loop would never end — a runaway loop is a
logic error, not a syntax error, and Python will not say a word about it. And the
trace is exact only because 1000.0 added to itself repeatedly stays exact in binary
and $15.0/15000.0$ lands precisely on the double nearest $10^{-3}$. Change the step
to 1100.0 and the boundary row becomes a question about the last bit of a float,
which is never where an engineering decision should live. When the count is knowable
in advance — and here it is, $r = V/I$ solves it in one line — a `for` loop over
integers is the safer instrument.
''',
                },
                {
                    "title": "How many parts the two loops keep",
                    "minutes": 8,
                    "brief": r'''
The lab builds a list of every E12 resistor value in a range, and it does it with a
loop over the decades wrapped round a loop over the twelve base numbers, with a test
in the middle deciding what survives.

Three constructs at once, and the only way to get the count right is to take the
decades one at a time.
''',
                    "prompt": "What number does this program print?",
                    "note": "A count of resistor values.",
                    "figure": r'''
```python
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

n = 0
for k in range(2, 5):                    # the decade: 10**2, 10**3, 10**4
    for v in E12:
        r = v * 10.0 ** k                # ohms
        if 500.0 <= r <= 20000.0:        # keep only what is in range
            n += 1

print(n)
```

Every E12 base number is available multiplied by any power of ten: 1.2 Ω, 12 Ω,
120 Ω, 1.2 kΩ and so on.
''',
                    "given": [
                        {"label": "Base values", "value": "the twelve E12 numbers"},
                        {"label": "Decades visited", "value": "k = 2, 3, 4"},
                        {"label": "Kept when", "value": "500 Ω ≤ r ≤ 20 kΩ"},
                    ],
                    "aside": "Take one decade at a time and count how many of the twelve survive the "
                             "test in that decade. Only the first and last decades lose anything.",
                    "answer": 19.0,
                    "tol": 0.01,
                    "unit": "values",
                    "hint": "In the 100 Ω decade only the values from 5.6 upwards reach 500 Ω. The whole "
                            "1 kΩ decade fits. In the 10 kΩ decade the survivors stop once the value "
                            "passes 20 kΩ.",
                    "wrong": "36 is $3 \\times 12$ — the count with the `if` ignored, which is what the "
                             "loops alone would give. 24 assumes two full decades and forgets that the "
                             "10 kΩ decade contributes four values of its own.",
                    "why": r'''
Nineteen. Decade by decade:

```
k = 2   100 Ω decade    100 120 150 180 220 270 330 390 470 | 560 680 820
                        the first nine are below 500 Ω          3 kept

k = 3   1 kΩ decade     1000 ... 8200, all twelve between
                        500 Ω and 20 kΩ                        12 kept

k = 4   10 kΩ decade    10000 12000 15000 18000 | 22000 ...
                        the rest are above 20 kΩ                4 kept
                                                              ----
                                                               19
```

The two loops between them visit $3 \times 12 = 36$ values, and the `if` throws away
seventeen of them. That is the ordinary arrangement: the loops generate candidates,
the condition decides which ones count, and the accumulator `n` — initialised once
before both loops, updated inside — carries the answer out.

One detail from the lab is hiding in this listing. `8.2 * 10.0 ** 2` does not come out
as 820.0; it comes out as 819.9999999999999, because neither 8.2 nor the product is
exactly representable in binary. Here it makes no difference, since the test is a
comparison with a wide margin either side. It matters the moment such a value is
printed as a part number, compared with `==`, or used as a dictionary key, which is
why the lab rounds each value with `round(r, 9)` before keeping it — and why the
comparisons there carry a slack of $10^{-9}$ at each end rather than trusting the
endpoints to land exactly.
''',
                },
                {
                    "title": "What the chosen divider does once something is connected to it",
                    "minutes": 10,
                    "brief": r'''
The lab's search picks 6.8 kΩ over 3.3 kΩ as the closest 5 V it can reach from a 15 V
supply with E12 parts: $15.0 \times 3300 / 10100 = 4.9010$ V. Its scoring line
assumed the divider was working into nothing at all.

It is not. The circuit below is that divider with the thing it feeds drawn in — an
input that behaves like a 10 kΩ resistor to ground, which is an unremarkable figure
for a sensor input or a meter. The load sits **across** the lower resistor, because
both of them run from the output node to ground, and two resistors between the same
pair of nodes are one resistor of a smaller value.

Everything you need is in module 1's lab: `parallel(r1, r2)` and then
`divider_out(vin, r1, r2)`, in that order.
''',
                    "prompt": "What does the probe read?",
                    "note": "In volts, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 15},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 9},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 6800},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3300},
                            {"id": "rl", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 4], "b": [13, 4]},
                            {"a": [13, 4], "b": [13, 5]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [13, 7], "b": [13, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "15.0 V"},
                        {"label": "Upper resistor", "value": "6.8 kΩ"},
                        {"label": "Lower resistor", "value": "3.3 kΩ"},
                        {"label": "Load across the output", "value": "10 kΩ"},
                        {"label": "Unloaded, this divider gives", "value": "4.9010 V"},
                    ],
                    "aside": "Two rules, in order. Combine the two resistors that share both ends into "
                             "one, then divide the supply between that and the resistor above it.",
                    "check": "return c.vout();",
                    "answer": 4.010,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": "The two lower resistors combine to "
                            "$3300 \\times 10000 / 13300 = 2481$ Ω. Put that number where the 3300 used "
                            "to be and run the divider formula again.",
                    "wrong": "4.901 V is the unloaded answer — the one the search believed, and the one "
                             "you get by leaving the 10 kΩ out. 9.925 V comes from adding the load to "
                             "the lower resistor instead of combining it in parallel: the two share "
                             "both nodes, so the arm gets *smaller*, not larger, and connecting a "
                             "resistor to a divider output can never raise that output.",
                    "why": r'''
The lower arm is no longer 3.3 kΩ. The load and the lower resistor run between the
same two nodes — the output and ground — so they are in parallel:

```
R_lower = 3300 x 10000 / (3300 + 10000)
        = 33000000 / 13300
        = 2481.20 Ω          smaller than either of them, as a parallel pair must be

total   = 6800 + 2481.20  =  9281.20 Ω

Vout    = 15.0 x 2481.20 / 9281.20
        = 37218.05 / 9281.20
        = 4.0100 V
```

**4.010 V**, where the search promised 4.901 V. The circuit lost 0.891 V — 18% of its
output — to a load the scoring line never knew about, and no arithmetic in that line
was wrong: it answered a question about a different circuit.

This is the quantitative version of the sentence in the build brief about large
resistors letting a load drag the output down. The mechanism is visible in the
numbers: what matters is the load compared with the divider's own arm. Here 10 kΩ
against 3.3 kΩ is a heavy load and the output collapses. Scale the divider down by
ten — 680 Ω over 330 Ω, the same ratio and the same 4.901 V unloaded — and the same
10 kΩ load takes the output only to 4.794 V, an error of 2.2% instead of 18%, at the
cost of 15.0 mA out of the supply instead of 1.5 mA. That is the trade
the build's current window is really about, and it is why a divider is specified by
two numbers rather than by a ratio.

The repair in code is one line inside the search: score each candidate with the load
in place, `divider_out(vin, r1, parallel(r2, rload))`, and the pairs it prefers change
completely — it will start choosing small resistors, because those are the ones a
10 kΩ load barely notices.
''',
                },
            ],
            "derive": {
                "title": "Removing a loop with algebra",
                "minutes": 12,
                "vars": ["V_in", "V_t", "R_1", "R_2", "n"],
                "brief": r'''
The lab's search tries every pair. That is honest and it is wasteful: for a chosen
lower resistor, the upper one that hits the target exactly is not something to be
searched for at all — it can be *computed*, and the only candidates worth scoring are
the two stock values either side of it.

Below, $V_{in}$ is the supply, $V_t$ the target output, $R_1$ the upper resistor and
$R_2$ the lower one, with the output taken at their joint. Work in symbols
throughout; the numbers come at the end.
''',
                "steps": [
                    {
                        "prompt": "Write the output voltage of the divider in terms of $V_{in}$, $R_1$ and $R_2$.",
                        "answer": "\\frac{V_{in} R_2}{R_1 + R_2}",
                        "placeholder": "\\frac{...}{...}",
                        "hint": "The same current flows through both resistors, so the supply divides between them in proportion to their resistances. The output is measured across the lower one.",
                        "deconstruct": [
                            "The pair carries a current $I = V_{in}/(R_1 + R_2)$, because in series the resistances add.",
                            "The output node sits above the lower resistor, so the voltage there is the drop across $R_2$ alone: $I R_2$.",
                            "Substituting gives $V_{in} R_2 / (R_1 + R_2)$.",
                        ],
                    },
                    {
                        "prompt": "Set that output equal to the target $V_t$ and solve for $R_1$. Write $R_1$ in terms of $R_2$, $V_{in}$ and $V_t$.",
                        "answer": "\\frac{R_2 (V_{in} - V_t)}{V_t}",
                        "hint": "Cross-multiply to clear the fraction, gather the $R_1$ terms on one side, and divide.",
                        "deconstruct": [
                            "$V_t (R_1 + R_2) = V_{in} R_2$ after multiplying both sides by $R_1 + R_2$.",
                            "Expanding: $V_t R_1 + V_t R_2 = V_{in} R_2$, so $V_t R_1 = V_{in} R_2 - V_t R_2$.",
                            "Dividing by $V_t$ leaves $R_1 = R_2 (V_{in} - V_t)/V_t$.",
                        ],
                    },
                    {
                        "prompt": "Divide through by $R_2$ to get the required ratio $R_1/R_2$, in terms of $V_{in}$ and $V_t$ only.",
                        "answer": "\\frac{V_{in} - V_t}{V_t}",
                        "hint": "Only $R_2$ leaves the expression; nothing else changes.",
                    },
                    {
                        "prompt": "The lab scores every ordered pair drawn from a list of $n$ stock values. How many candidates is that? Write it as an expression in $n$.",
                        "answer": "n^{2}",
                        "placeholder": "an expression in n",
                        "hint": "The inner loop runs all the way through for each pass of the outer one.",
                    },
                    {
                        "prompt": "Now use the ratio. Loop over $R_2$ only, compute the exact $R_1$ it needs, and score just the two stock values either side of that number. How many candidates now, in terms of $n$?",
                        "answer": "2 n",
                        "hint": "One pass per value of $R_2$, and each pass scores a fixed number of upper resistors rather than all of them.",
                    },
                    {
                        "prompt": "Write the ratio of the first count to the second — the factor by which the algebra cut the work.",
                        "answer": "\\frac{n}{2}",
                        "hint": "Divide one expression by the other and cancel.",
                    },
                ],
                "closing": r'''
Put the numbers in.

```
E12 values from 1 kOhm to 100 kOhm:      n  =   25
    every ordered pair:                  n^2 =  625 candidates
    one loop plus two neighbours:        2n  =   50 candidates
    saving:                              n/2 = 12.5 x

widen the range to 10 Ohm .. 1 MOhm:     n  =   61
                                         n^2 = 3721
                                         2n  =  122
                                         saving                30.5 x

for 15 V in and 5 V out:   R1/R2 = (15 - 5)/5 = 2
                           so with R2 = 3.3 kOhm the ideal R1 is 6.6 kOhm,
                           and the E12 values either side are 5.6 k and 6.8 k
```

Three things are worth taking from this, and only one of them is about speed.

**The candidate that is not searched for is the one you computed.** The step from
$n^2$ to $2n$ came entirely from rearranging one equation. This is the standard shape
of making a program faster: not a tighter loop, but a loop that never runs, because
something about the problem was understood well enough to skip it.

**Why two neighbours and not one.** For a fixed $R_2$, raising $R_1$ can only lower
the output — the expression falls monotonically in $R_1$ — so the error $|V - V_t|$
falls as $R_1$ approaches the ideal value from either side and rises after it. The
best stock choice is therefore always one of the two values bracketing the ideal, and
which of the two it is depends on where the ideal sits between them. Checking both is
cheap and removes the argument. Checking only the nearer one is a guess that is
usually right, and "usually right" is not a specification.

**The exhaustive search keeps its place.** $n^2$ at $n = 25$ is 625 evaluations of a
three-operation formula, which is over before you have taken your finger off the key.
Write the version you can prove correct first; replace it with the version you can
prove *equivalent* only when the count says you must, and keep the slow one to check
the fast one against. Module 10 makes exactly this move on a problem where the
algebra will not rearrange at all, and has to aim at the answer instead.
''',
            },
            "build": {
                "title": "A divider that gives 5 V from a 15 V supply",
                "minutes": 25,
                "brief": r'''
This is the circuit your `divider_out` function described. Now draw it.

The canvas already holds a **15 V supply** and two grounds. Add two resistors in a
line across the supply, put a **probe** on the joint between them, and choose values
so that the probe reads **5.00 V**.

Two things constrain the choice, and they pull in opposite directions:

- the ratio has to be right, so the lower resistor is one third of the total;
- the supply must deliver **between 0.2 mA and 1.5 mA**. Small resistors give a
  stiff output and waste current as heat; large ones save current but let any load
  drag the output down. Every resistor you use must be between 1 kΩ and 1 MΩ.

There is no single right pair. Any pair with the correct ratio and a total between
about 10 kΩ and 75 kΩ passes, because the checks measure the circuit rather than
compare it with a drawing.

**Drawing it.** Pick a part from the palette and click to place it. Drag from one
pin to another to wire them. A wire and a pin are connected when they land on the
same grid point, and on nothing less.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 15},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "GND", "x": 9, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 15},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p3", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 20000},
                        {"id": "p4", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 10000},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 4], "b": [11, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                    ],
                },
                "checks": [
                    {"name": "the 15 V supply is still there and still 15 V", "code": r'''
c.assert(c.count("V") === 1,
  "keep exactly one voltage source: the 15 V supply you started with");
c.close(c.values("V")[0], 15, 0.001, "the supply voltage");
'''},
                    {"name": "the probe reads 5 V", "code": r'''
c.close(c.vout(), 5.0, 0.02, "the probed output");
'''},
                    {"name": "the supply delivers between 0.2 mA and 1.5 mA", "code": r'''
var src = c.net.parts.filter(function (p) { return p.kind === "V"; })[0];
c.assert(src, "there is no voltage source for the current to come from");
var i = Math.abs(c.dc().currents[src.id]);
c.assert(i >= 2e-4 && i <= 1.5e-3,
  "the supply delivers " + c.fmt(i, "A") + ", and the brief asks for 0.2 mA to 1.5 mA");
'''},
                    {"name": "every resistor is a real, orderable value", "code": r'''
var rs = c.values("R");
c.assert(rs.length >= 2,
  "a two-resistor divider needs two resistors, and this circuit has " + rs.length);
rs.forEach(function (r) {
  c.assert(r >= 1000 && r <= 1e6,
    "every resistor must be between 1 kOhm and 1 MOhm; found " + c.fmt(r, "Ohm"));
});
'''},
                ],
                "hints": [
                    "The output is one third of the supply, so the lower resistor is one third of the total resistance and the upper one is the other two thirds. The upper resistor is twice the lower.",
                    "The current spec fixes the total: 15 V across a total R gives 15/R amps, so a total of 30 kΩ draws 0.5 mA, comfortably inside the window.",
                    "The probe is a single-pin part. Place it on the wire joining the two resistors, not on the supply rail — probing the rail reads 15 V, and the check will say so.",
                    "If a check complains that there is no ground, one of the wires does not quite reach: pins connect only when they sit on exactly the same grid point.",
                ],
            },
            "lab": {
                "title": "Choosing a divider you can actually buy",
                "runtime": "python",
                "minutes": 35,
                "brief": r'''
Resistors are not sold in every value. The **E12 series** is twelve numbers,

```text
1.0  1.2  1.5  1.8  2.2  2.7  3.3  3.9  4.7  5.6  6.8  8.2
```

each available multiplied by any power of ten: 1.2 Ω, 12 Ω, 120 Ω, 1.2 kΩ and so
on. Notice what is missing: there is no 2.0, so the 10 kΩ from the circuit you just
drew can be ordered and its 20 kΩ partner cannot. Most ratios you want are not
available exactly, and you have to search for the closest pair that is.

Write three functions.

`e12_values(lo, hi)` returns a sorted list of every E12 value between `lo` and `hi`
inclusive. Loop over the decades with `for k in range(-2, 8)` and over the twelve
base numbers inside that; keep `v * 10.0 ** k` when it lands in range. Round each
kept value with `round(r, 9)` so that 1.2 × 10³ is exactly 1200.0 rather than
1200.0000000000002.

`divider_out(vin, r1, r2)` is the same one-liner as the last lab.

`best_pair(vin, vtarget, lo, hi)` tries **every** pair of E12 values in range as
`(r1, r2)`, scores each by how far its output is from `vtarget`, and returns the
`(r1, r2)` of the best. Keep a candidate only when it is strictly better than the
best so far, so that the first pair found wins any tie and the answer is
predictable.
''',
                "files": [{"name": "main.py", "content": r'''
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]


def e12_values(lo, hi):
    """Every E12 value between lo and hi inclusive, sorted ascending."""
    out = []
    # TODO: for each decade k, for each base value v, keep v * 10.0 ** k when
    # it falls between lo and hi. Round to 9 decimals before keeping it.
    return sorted(out)


def divider_out(vin, r1, r2):
    """Voltage at the joint of r1 and r2, with vin across the pair."""
    # TODO: same as the previous lab.
    return 0.0


def best_pair(vin, vtarget, lo=1e3, hi=1e5):
    """The (r1, r2) of E12 values whose divider output is closest to vtarget."""
    values = e12_values(lo, hi)
    best = None
    best_error = None
    # TODO: two nested loops, score each pair, keep the strictly better one.
    return best


if __name__ == "__main__":
    print("E12 values from 1k to 10k:", e12_values(1e3, 1e4))
    pair = best_pair(15.0, 5.0, 1e3, 1e5)
    print("closest pair to 5 V from 15 V:", pair)
    if pair:
        print("which gives:", round(divider_out(15.0, pair[0], pair[1]), 4), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]


def e12_values(lo, hi):
    """Every E12 value between lo and hi inclusive, sorted ascending."""
    out = []
    for k in range(-2, 8):
        for v in E12:
            r = round(v * 10.0 ** k, 9)
            if lo - 1e-9 <= r <= hi + 1e-9:
                out.append(r)
    return sorted(out)


def divider_out(vin, r1, r2):
    """Voltage at the joint of r1 and r2, with vin across the pair."""
    return vin * r2 / (r1 + r2)


def best_pair(vin, vtarget, lo=1e3, hi=1e5):
    """The (r1, r2) of E12 values whose divider output is closest to vtarget."""
    values = e12_values(lo, hi)
    best = None
    best_error = None
    for r1 in values:
        for r2 in values:
            error = abs(divider_out(vin, r1, r2) - vtarget)
            if best_error is None or error < best_error - 1e-15:
                best_error = error
                best = (r1, r2)
    return best


if __name__ == "__main__":
    print("E12 values from 1k to 10k:", e12_values(1e3, 1e4))
    pair = best_pair(15.0, 5.0, 1e3, 1e5)
    print("closest pair to 5 V from 15 V:", pair)
    if pair:
        print("which gives:", round(divider_out(15.0, pair[0], pair[1]), 4), "V")
'''}],
                "hints": [
                    "`10.0 ** k` with a negative `k` gives a fraction, so `range(-2, 8)` runs from 0.01 Ω up to 8.2 × 10⁷ Ω, which is wider than any resistor you will meet. Nothing outside `lo` and `hi` survives the test anyway.",
                    "`8.2 * 10.0 ** 2` comes out as 819.9999999999999, which is what the `round(r, 9)` is there to clean up. Comparing with a small slack — `lo - 1e-9 <= r <= hi + 1e-9` — guards the two endpoints a second time, for when `lo` or `hi` is itself the result of a calculation.",
                    "The search is two `for` loops, one inside the other, with an `if` in the middle. `r1` and `r2` come from the same list, and a pair may use the same value twice.",
                    "`error < best_error - 1e-15` rather than `error < best_error` means an exactly equal candidate does not displace the one already found, so the result does not depend on how the list happened to be ordered.",
                ],
                "tests": [
                    {"name": "1k to 10k inclusive is thirteen values", "code": r'''
_v = e12_values(1e3, 1e4)
assert len(_v) == 13, f"1k to 10k inclusive is the twelve E12 values plus 10k itself, got {len(_v)}"
assert abs(_v[0] - 1000.0) < 1e-6, f"the smallest should be 1000.0, got {_v[0]}"
assert abs(_v[-1] - 10000.0) < 1e-6, f"the largest should be 10000.0, got {_v[-1]}"
assert _v == sorted(_v), "the list must come back sorted ascending"
'''},
                    {"name": "E12 values are clean numbers", "code": r'''
_v = e12_values(1e3, 1e4)
assert 1200.0 in _v, f"1.2k should be present exactly as 1200.0; got {_v}"
assert 6800.0 in _v, f"6.8k should be present exactly as 6800.0; got {_v}"
assert 2000.0 not in _v, "2.0 is not an E12 number, so 2k must not appear"
'''},
                    {"name": "the range really is a range", "code": r'''
assert len(e12_values(1e3, 1e5)) == 25, \
    f"two decades plus the endpoint is 25 values, got {len(e12_values(1e3, 1e5))}"
assert e12_values(1e6, 2e6) == [1000000.0, 1200000.0, 1500000.0, 1800000.0], \
    f"the decades keep going: got {e12_values(1e6, 2e6)}"
assert e12_values(2000.0, 2100.0) == [], "there is no E12 value between 2.0k and 2.1k"
'''},
                    {"name": "the divider still divides", "code": r'''
assert abs(divider_out(15.0, 20000.0, 10000.0) - 5.0) < 1e-12
assert abs(divider_out(15.0, 10000.0, 20000.0) - 10.0) < 1e-12, \
    "r2 is the one next to the output, so swapping the pair must change the answer"
'''},
                    {"name": "the search finds the best available 5 V", "code": r'''
_p = best_pair(15.0, 5.0, 1e3, 1e5)
assert _p is not None and len(_p) == 2, f"expected a pair, got {_p!r}"
_got = divider_out(15.0, _p[0], _p[1])
assert abs(_got - 4.900990099009901) < 1e-9, \
    f"the closest E12 pair reaches 4.9010 V, not 5 V exactly; your pair {_p} gives {_got}"
'''},
                    {"name": "the search is not hard-wired to one target", "code": r'''
_p = best_pair(5.0, 3.3, 1e3, 1e5)
_got = divider_out(5.0, _p[0], _p[1])
assert abs(_got - 3.235294117647059) < 1e-9, \
    f"3.3 V from 5 V comes out at 3.2353 V with E12 parts; your pair {_p} gives {_got}"
'''},
                    {"name": "an exactly reachable target is reached exactly", "code": r'''
_p = best_pair(10.0, 5.0, 1e3, 1e5)
_got = divider_out(10.0, _p[0], _p[1])
assert abs(_got - 5.0) < 1e-12, \
    f"half of the supply needs only two equal resistors; your pair {_p} gives {_got}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Lists, dictionaries and records",
            "summary": "One number fits in a variable. A board does not. Three containers cover almost everything an engineer has to hold at once, and each answers a different question about the same parts list.",
            "concepts": [
                "A *list* is an ordered sequence you can change: `parts[0]` is the first element, `parts.append(x)` adds one to the end, `len(parts)` counts them, and the order is remembered.",
                "A *tuple* is a fixed sequence written with commas — `(\"mid\", \"0\")` — and cannot be altered once made. Reach for one when the positions themselves carry meaning, as the two ends of a component do.",
                "A *dictionary* maps a key to a value, so `p[\"kind\"]` looks a thing up by name rather than by position. `p.get(\"kind\", \"?\")` returns the fallback instead of raising when the key is absent.",
                "A *record* is a dictionary standing for one thing — one line of a parts list, one reading from a meter — carrying the same keys every time. A list of records is the shape almost all engineering data arrives in.",
                "`for p in parts:` walks a list. `for k, v in d.items():` walks a dictionary in pairs; looping over a dictionary on its own gives you the keys and nothing else.",
                "`sorted(xs, key=f)` returns a *new* list ordered by `f(x)` and leaves `xs` untouched. `xs.sort()` reorders `xs` where it stands and returns `None`, which is the difference that bites.",
            ],
            "read": [
                {
                    "title": "A row of things, and why a name is not a box",
                    "minutes": 13,
                    "body": r'''
A finished board in front of you carries forty-one components. You want to know what
the lot cost, how many of them are resistors, and which one has the largest value.
Nothing written so far can hold it. A name binds to a single value — `r1 = 4700.0`
gives you one resistor — and forty more lines give you forty more names, each of
which then has to be typed out by hand in every sum you write afterwards. Add a
forty-second part and every one of those sums is wrong.

What is wanted is one name for the whole row, and a way of saying "the next one"
without knowing in advance how many there are.

## The list

A **list** is an ordered run of values under one name:

```python
values = [4700.0, 2200.0, 3300.0, 1000.0, 47.0]   # ohms, five resistors
```

Three claims are packed into that line, and each of them earns its keep.

**It is one value.** `values` is a single name bound to a single object, exactly as
`r = 4700` was. It can be passed to a function, returned from one, and re-bound. That
the object happens to contain five numbers changes nothing about the binding itself.

**It is ordered.** The five resistors are in the order you typed them and will stay
that way until something moves them. `values[0]` is 4700.0 and `values[4]` is 47.0.
Order is part of what a list *is*, which is why two lists holding the same numbers in
a different order are not equal.

**It can be changed.** `values.append(680.0)` makes the list six long. The object
itself is edited: no new list is made, and no name is re-bound. That last point is
where the surprises live, and the second worked example below is about nothing else.

### Counting from zero, and slicing

Positions run $0, 1, 2, \ldots$, so the last index of a list of $n$ things is $n - 1$
and `len(values)` is 5 for the list above. Negative indices count from the far end:
`values[-1]` is the last element and `values[-2]` the one before it. That saves
writing `values[len(values) - 1]`, which is the same thing with more places to slip.

A **slice** takes a run of them. `values[1:4]` is a *new* list holding the elements at
positions 1, 2 and 3 — start included, stop excluded, exactly as `range` behaved in
module 2. Two things fall out of the exclusive stop, and both are worth more than the
convenience of counting inclusively:

- the length of `xs[a:b]` is $b - a$, with no correction term anywhere;
- `xs[:k]` and `xs[k:]` fit together with no overlap and no gap, whatever `k` is, so
  splitting a run of samples in two never involves an argument about who owns the
  join.

## Worked example 1: seven readings, and the window in the middle

A meter logs seven currents, in milliamps:

```python
i = [0.42, 1.87, 3.05, 2.14, 0.98, 1.61, 0.77]
```

Take it apart. `len(i)` is 7, so the valid indices are 0 to 6.

```
i[0]      0.42                       the first
i[6]      0.77                       the last, counted forwards
i[-1]     0.77                       the last, counted backwards - same element
i[-2]     1.61
i[2:5]    [3.05, 2.14, 0.98]         positions 2, 3, 4: three of them, 5 - 2 = 3
i[:3]     [0.42, 1.87, 3.05]
i[3:]     [2.14, 0.98, 1.61, 0.77]   3 + 4 = 7 - nothing lost, nothing twice
```

Now ask the list something. The mean of the whole run:

```
sum(i) = 0.42 + 1.87 + 3.05 + 2.14 + 0.98 + 1.61 + 0.77
       = 10.84
mean   = 10.84 / 7 = 1.5485714...   ->  1.549 mA
```

and the mean of the three-sample window in the middle:

```
sum(i[2:5]) = 3.05 + 2.14 + 0.98 = 6.17
mean        = 6.17 / 3 = 2.0566666...   ->  2.057 mA
```

The window sits about a third above the run as a whole, which is the sort of thing
you take a window in order to find out. Notice what `sum`, `len` and `max` have in
common: not one of them cares how long the list is, and none of them had to be told.
`max(i)` is 3.05 and `i.index(3.05)` reports *where* that is, namely 2 — the third
reading. What the largest value was and where it happened are two different
questions, and a list answers both.

## Growing a list, and the difference between two ways of doing it

`append` adds **one** element:

```python
refs = ["R1", "R2"]
refs.append("C1")            # ['R1', 'R2', 'C1']
```

`extend` adds **each element of** something else:

```python
refs.extend(["C2", "C3"])    # ['R1', 'R2', 'C1', 'C2', 'C3']
```

`refs.append(["C2", "C3"])` is legal and does something else entirely: it puts the
two-element list in as a single element, leaving `refs` four long with a list sitting
inside it. Nothing complains. You find out later, when something takes the first
character of `refs[3]` to work out what kind of part it is and gets `"C2"` rather than
`"C"`.

The operators behave as their names suggest and not as arithmetic suggests.
`[1, 2] + [3]` is `[1, 2, 3]` — concatenation, and a new list. `[0.0] * 3` is
`[0.0, 0.0, 0.0]` — repetition, the ordinary way to make a list of known length full
of zeros. Neither does arithmetic on the contents: `values * 2` does not double five
resistances, it gives you ten resistors.

## Worked example 2: two names, one list

This is the most expensive misunderstanding in the module, so it is worth tracing a
line at a time.

```python
ordered = ["R1", "R2", "C1"]
shipped = ordered            # a second name for the SAME list
shipped.append("C2")
spare   = ordered[:]         # a copy: a second list
spare.append("L1")
```

`=` binds a name to a value. It never copies. So `shipped = ordered` hands the
existing list a second label, while `ordered[:]` — a slice of the whole thing —
builds a new list holding the same elements.

```
line                       object A            object B             len(ordered)
--------------------------------------------------------------------------------
ordered = [R1,R2,C1]       [R1,R2,C1]          -                         3
shipped = ordered          [R1,R2,C1]          -                         3
                           ^ two names on it
shipped.append("C2")       [R1,R2,C1,C2]       -                         4  <-
spare = ordered[:]         [R1,R2,C1,C2]       [R1,R2,C1,C2]             4
spare.append("L1")         [R1,R2,C1,C2]       [R1,R2,C1,C2,L1]          4
```

At the end `len(ordered)` is 4 and `len(shipped)` is 4 — they are the same object, so
of course they are — while `len(spare)` is 5. `shipped is ordered` is `True`;
`spare is ordered` is `False`, even though `spare == ordered` was `True` right up
until the final line.

The line that changed `ordered` without mentioning it is `shipped.append("C2")`. Put
those two names in different functions written by different people and this is a bug
that costs an afternoon. There is nothing subtle about the rule — `=` binds, it does
not copy — and it goes unnoticed for as long as it does only because integers and
strings cannot be edited in place, so with them the distinction never shows itself.

When you want a copy, ask for one: `spare = ordered[:]` or `spare = list(ordered)`,
which do the same thing. Both are *shallow* — the new list holds the very same objects
the old one held. For a list of numbers or strings that is a complete copy in every
way that matters. For a list of records, which is what the next reading is about, it
is not: `spare[0]["qty"] = 9` still changes what `ordered[0]` sees, because the copy
duplicated the row of labels and not the things they point at.

## The tuple: a sequence that refuses to be edited

`("mid", "0")` is a **tuple**. It indexes and slices exactly as a list does, and
`t[0] = "in"` raises a TypeError instead of working.

That sounds like a list with a feature taken away, and it is better read the other way
round. Reach for a tuple when the positions themselves carry a meaning that is fixed:
the two nodes a resistor joins, an $(x, y)$ on the schematic grid, a `(kind, value)`
pair. Those are not collections that might grow — they are one thing with parts. A
container that refuses to be edited says so in the type rather than in a comment, and
because it cannot change it can be used as a dictionary key, which a list can never
be.

## The mistakes people actually make

**`xs = xs.sort()`.** `.sort()` reorders the list where it stands and returns `None`,
following Python's habit of never handing back the object it has just modified. So
the list is sorted and the name is then immediately re-bound to nothing, and the
failure surfaces two lines later as `TypeError: object of type 'NoneType' has no
len()`. `sorted(xs)` is the one that returns a new list. The wrong spelling is
tempting because nearly every other line you write has the shape
`name = something(...)`.

**Reading `i[1:3]` as "elements one to three".** It is two elements, not three. The
tell is an answer of exactly the right shape that is one item short, which is the kind
of wrong a review almost never catches.

**Removing from a list while looping over it.** The loop walks by position, and the
positions move underneath it:

```python
readings = [0.42, 1.87, 3.05, 2.14]
for v in readings:
    if v > 1.5:
        readings.remove(v)
print(readings)          # [0.42, 3.05]
```

The intended answer is `[0.42]`. What happens instead: position 0 holds 0.42 and is
kept; position 1 holds 1.87, which is removed, so everything after it shifts down and
3.05 is now at position 1 — which the loop has already been past. Position 2 now holds
2.14, which is removed; position 3 is off the end, and the loop stops. The largest
reading in the run has survived a filter written to delete it, and nothing was raised.
Build a new list instead: `[v for v in readings if v <= 1.5]`.

## Where the list stops being the right container

- **Finding a part by its reference.** `refs.index("R3")` walks from the front
  comparing as it goes. With 400 parts and 400 lookups that is on the order of 80,000
  comparisons for work a dictionary does without comparing anything at all. The next
  reading is about that, and this module's derivation counts it exactly.
- **Arithmetic on the whole run.** Doubling every reading needs a loop or a
  comprehension, because `readings * 2` repeats the list instead. Module 6 replaces
  the list with a NumPy array, where `readings * 2` does the arithmetic on every
  element and the loop disappears into compiled code.
- **Growing by concatenation inside a loop.** `out = out + [x]` builds an entirely new
  list on each pass, so filling $n$ elements costs about $n^2/2$ element copies;
  `out.append(x)` edits one list in place and costs $n$. At $n = 10$ nobody notices.
  At $n = 100{,}000$ one takes an instant and the other takes minutes.
- **A row of fields belonging to one part.** `["R1", "R", 4700.0, 1]` works and is
  unreadable: `p[2]` says nothing about what it holds, and inserting a field
  renumbers everything after it in every file that touches it. That is the job the
  next reading gives to a record.
''',
                },
                {
                    "title": "Looking a thing up by its name",
                    "minutes": 14,
                    "body": r'''
Ten parts drawers, unlabelled, in an order you have memorised — the 4.7 kΩ resistors
are the third along. That is a list. Ten drawers with the value written on the front:
that is a dictionary. Both hold the same components in the same room. The difference
is what you must know in order to open the right one, and how long it takes you when
there are four hundred drawers instead of ten.

## A dictionary maps a key to a value

```python
r = {"ref": "R1", "kind": "R", "value": 4700.0, "qty": 1}
```

`r["value"]` is 4700.0. The lookup is by **key**, not by position, and position is not
something you can ask about: there is no `r[2]`, and if there were it would mean "the
value filed under the key `2`" rather than "the third field". Keys are usually
strings, may be numbers or tuples, and must be *immutable* — which is exactly why a
tuple can be a key and a list can never be one.

Three operations, and one of them is where the accidents happen:

```python
r["qty"]                # 1        - the key is there
r["price"]              # KeyError - the key is not
r.get("price", 0.0)     # 0.0      - the key is not, and you said what to do about it
```

`KeyError` is the right default. A missing field in a parts list is usually a typo in
the file, and you want to hear about it at the line that caused it rather than three
functions later, when a `None` refuses to be multiplied. `get` is for when absence is
genuinely expected and has a sensible stand-in, and writing it says so out loud.

Assignment creates the key if it is absent and replaces the value if it is present:
`r["price"] = 0.04` works either way. That symmetry is what makes the tally below one
line long. It is also why a mistyped key is not an error — `r["referance"] = "R9"`
adds a fourth-and-a-bit field and the program carries cheerfully on.

### Walking a dictionary

```python
counts = {"R": 4, "C": 3, "D": 1}

for k in counts:              # 'R', 'C', 'D'                    - the KEYS
for v in counts.values():     # 4, 3, 1
for k, v in counts.items():   # ('R', 4), ('C', 3), ('D', 1)
```

Looping over a dictionary gives keys. It is short, and it is the line here that gets
misread, because "for thing in collection" everywhere else in Python hands you the
things. When you need both halves, `for kind, n in counts.items():` says so plainly.
Since Python 3.7 the order is the order the keys were first inserted, so a walk is
repeatable rather than arbitrary — but insertion order is not sorted order, and a
dictionary keeps its keys in no useful sequence whatever.

## Worked example 1: the tally

Five lines of a bill of materials, and the question is how many of each *kind* the
board takes. Kind is not unique — three of these lines are resistors — so the answer
is not a selection but a sum grouped by a field.

```python
BOM = [
    {"ref": "R1", "kind": "R", "qty": 1},
    {"ref": "C1", "kind": "C", "qty": 3},
    {"ref": "R2", "kind": "R", "qty": 1},
    {"ref": "D1", "kind": "D", "qty": 4},
    {"ref": "R3", "kind": "R", "qty": 2},
]

total = {}
for p in BOM:
    total[p["kind"]] = total.get(p["kind"], 0) + p["qty"]
```

One line does the work, and it repays being watched as it runs:

```
part  kind  qty   total.get(kind, 0)   total afterwards
----------------------------------------------------------------------
R1     R     1     0   (never seen)    {'R': 1}
C1     C     3     0   (never seen)    {'R': 1, 'C': 3}
R2     R     1     1                   {'R': 2, 'C': 3}
D1     D     4     0   (never seen)    {'R': 2, 'C': 3, 'D': 4}
R3     R     2     2                   {'R': 4, 'C': 3, 'D': 4}
```

Five lines in, three entries out. Check it the way you check any grouping: the
quantities on the lines add to $1 + 3 + 1 + 4 + 2 = 11$, and the tally's values add to
$4 + 3 + 4 = 11$. A tally that does not conserve the total has dropped something, and
you learn that before you learn what.

`get(kind, 0)` does one specific job — it turns "I have never seen this kind" into
"the running total so far is zero", which is exactly true, and it lets the same line
handle the first resistor and the third. Write `total[p["kind"]]` instead and the
program raises a KeyError on the very first part, because at that instant the
dictionary is empty. The only way to avoid that without `get` is to seed every
possible key by hand before the loop, which means knowing every kind the file contains
before you have read the file.

Two other spellings give plausible wrong numbers here rather than an error, which is
worse. Adding `1` instead of `p["qty"]` counts *lines* and gives
`{'R': 3, 'C': 1, 'D': 1}` — five rather than eleven. That is a real question with a
real answer, just not this one, which is precisely what makes it dangerous. And
writing `total[p["kind"]] = p["qty"]`, assignment where accumulation was meant, keeps
only the last line of each kind, giving `{'R': 2, 'C': 3, 'D': 4}` — in which the two
kinds that happen to have one line each are right, so two-thirds of the output looks
correct.

## A record is a dictionary standing for one thing

Each element of `BOM` above is a **record**: a dictionary carrying the same keys as
all the others, describing one line of the order. A **list of records** is the shape
almost all engineering data arrives in — a netlist, a log of measurements, a parts
order, a table exported from anything at all — and it earns its place by being good at
two different questions at once. The list keeps the order and lets you walk
everything; the dictionaries let each row be asked about by field name rather than by
column number. `p["value"]` is self-describing in a way `p[2]` is not, and adding a
field at the front breaks nothing that already reads the others.

## Worked example 2: an index, and the comparisons it saves

Here is a question the list alone answers badly. A netlist names a reference on every
line, and for each one you need that part's record.

```python
def find(parts, ref):
    for p in parts:              # walk from the front
        if p["ref"] == ref:      # comparing as you go
            return p
    return None
```

That is correct, and it is a **scan**. For the five-record `BOM` above, finding `R1`
costs one comparison and finding `R3` costs five. A reference equally likely to be any
of the five costs $(1 + 2 + 3 + 4 + 5)/5 = 3$ comparisons on average — in general
$(n + 1)/2$ for $n$ records — and a reference that is *not* there costs all $n$ before
the function is entitled to say so.

Build the lookup once instead:

```python
by_ref = {}
for p in BOM:
    by_ref[p["ref"]] = p         # 'R1' -> the whole record

by_ref["R3"]["qty"]              # 2, with no searching at all
```

A dictionary finds its entry by computing a number from the key and going straight
there, so the cost of a lookup does not grow with how many entries there are. Put
numbers on it. With $n = 5$ records and $m = 40$ netlist lines to resolve:

```
scan     40 lookups x 3 comparisons each       = 120 comparisons
index    5 insertions to build + 40 lookups    =  45 operations
                                         ratio =   2.7 x
```

and on a board-sized problem, $n = 60$ parts and $m = 200$ lines:

```
scan     200 x (60 + 1)/2 = 200 x 30.5         = 6100 comparisons
index    60 + 200                              =  260 operations
                                         ratio =  23.5 x
```

The gap widens with $n$, because the scan's cost per lookup *is* essentially $n$ and
the index's is not. This module's derivation does that algebra properly and works out
how many lookups it takes before building the index has paid for itself. The answer is
smaller than you would guess.

## Sorting records

`sorted` has to be told what to sort *on*, because a record has no natural order:
`sorted(BOM)` raises a TypeError, since `<` is not defined between two dictionaries
and Python declines to guess which field you meant. The `key` argument names a
function applied to each element, and whatever it returns is what gets compared:

```python
sorted(BOM, key=lambda p: p["qty"])                 # by quantity, smallest first
sorted(BOM, key=lambda p: -p["qty"])                # largest first
max(by_ref, key=lambda ref: by_ref[ref]["qty"])     # the ref with the largest qty
```

`lambda p: p["qty"]` is a one-expression function with no name, and here it does
nothing more than say which field. Two of its properties matter in practice. `sorted`
returns a **new** list and leaves the original alone, which is what you want when the
order of the file is itself information. And it is **stable**: elements that compare
equal keep the order they already had, so sorting by value and then by kind gives you
kinds in order with values ascending inside each — and you get that by sorting twice,
least important key first, rather than by writing a cleverer key.

## The mistakes people actually make

**Assuming a key is unique when it is not.** `by_ref[p["ref"]] = p` is right, because
references are unique. Do the same with `by_kind[p["kind"]] = p` and each resistor
silently overwrites the last, leaving one record where five were meant. Nothing is
raised. The dictionary is simply shorter than the list it came from, and comparing the
two lengths is the only thing that would have caught it. When the key repeats, the
value has to be a list: `by_kind.setdefault(p["kind"], []).append(p)`.

**Using a float as a key.** `d[0.3]` and `d[0.1 + 0.2]` are two different keys,
because $0.1 + 0.2$ is 0.30000000000000004 and a dictionary compares keys exactly.
Module 1's rule about `==` on floats turns up here with no escape hatch at all: there
is no tolerance available inside a hash lookup. Key on a string, on an integer, or on
a number you rounded deliberately.

**Changing a dictionary while looping over it.** Adding or deleting a key inside
`for k in d:` raises `RuntimeError: dictionary changed size during iteration`. That
one is at least loud — the list version of the same mistake, in the previous reading,
quietly gives the wrong answer instead. Loop over `list(d.keys())` if you must edit as
you go.

## Where this stops holding

- **Fixed, known fields and a great many rows.** A dictionary stores its key strings
  alongside every record, so a million measurements held as a million records is
  mostly a million copies of the word `"value"`. Columns of arrays, one per field, are
  what module 6 reaches for, and they are both smaller and very much faster.
- **A typo in a key is only half an error.** Reading `p["referance"]` raises, which is
  fine; writing it does not, and quietly adds a field nobody will ever read. A record
  type declared once — a `dataclass` or a `namedtuple` — refuses both, at the price of
  having to declare it.
- **A dictionary answers "which record has this reference", not "which records have a
  value above 1 kΩ".** Range questions still need a scan, or a list held in sorted
  order. No single container is best at everything, which is the reason this module is
  about choosing rather than about one container.
- **The data does not fit in memory.** Everything here assumes the whole parts list is
  loaded at once. Module 4 reads a netlist a line at a time, and a genuinely large one
  is answered by a database — which is a dictionary, a sorted list and a scan, written
  by somebody else and kept on a disk.
''',
                },
            ],
            "quiz": {
                "title": "Which container, and what it did",
                "minutes": 9,
                "questions": [
                    {
                        "q": "What does this print?\n\n```python\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(len(a))\n```",
                        "opts": ["3", "4", "It raises an error", "1"],
                        "a": 1,
                        "why": (
                            "4. `b = a` binds a second name to the *same* list rather than copying it, so "
                            "appending through one name is visible through the other. This is the same rule "
                            "as `b = a` on a number, and it looks different only because a list can be "
                            "changed in place and a number cannot. When you want a copy, ask for one: "
                            "`b = a[:]` or `b = list(a)`."
                        ),
                    },
                    {
                        "q": "`d = {\"kind\": \"R\", \"value\": 4700.0}`. What does `d[\"qty\"]` do?",
                        "opts": [
                            "Returns `None`",
                            "Returns 0",
                            "Raises a KeyError",
                            "Adds the key with an empty value",
                        ],
                        "a": 2,
                        "why": (
                            "It raises a KeyError, naming the key it could not find. That is the useful "
                            "behaviour: a missing field in a parts list is usually a typo in the file, and "
                            "you want to hear about it at the line that caused it. When absence is genuinely "
                            "expected, `d.get(\"qty\", 1)` says so out loud and hands back the fallback."
                        ),
                    },
                    {
                        "q": "What does `print([3, 1, 2].sort())` print?",
                        "opts": ["`[1, 2, 3]`", "`None`", "`[3, 1, 2]`", "It raises an error"],
                        "a": 1,
                        "why": (
                            "`None`. The `.sort()` method reorders the list in place and returns nothing, "
                            "following Python's habit of never returning the thing it just modified. The "
                            "function `sorted([3, 1, 2])` is the one that hands back a new sorted list. "
                            "Writing `xs = xs.sort()` is how this becomes a bug: the list is sorted and then "
                            "immediately replaced by `None`."
                        ),
                    },
                    {
                        "q": "`t = (\"mid\", \"0\")`. What happens on `t[0] = \"in\"`?",
                        "opts": [
                            "`t` becomes `(\"in\", \"0\")`",
                            "It raises a TypeError",
                            "It creates a new tuple and leaves `t` alone",
                            "It raises an IndexError",
                        ],
                        "a": 1,
                        "why": (
                            "A TypeError: a tuple does not support item assignment. That is the whole point "
                            "of choosing one — the pair of nodes a resistor joins is fixed once the schematic "
                            "is drawn, and a container that refuses to be edited says so in the type rather "
                            "than in a comment. Reading `t[0]` is fine; only writing is refused."
                        ),
                    },
                    {
                        "q": "`counts = {\"R\": 4, \"C\": 3}`. What does `for k in counts:` give `k` on each pass?",
                        "opts": [
                            "The keys, `\"R\"` then `\"C\"`",
                            "The values, 4 then 3",
                            "The pairs `(\"R\", 4)` then `(\"C\", 3)`",
                            "Nothing — a dictionary cannot be looped over",
                        ],
                        "a": 0,
                        "why": (
                            "The keys. Looping over a dictionary gives keys, which is short but easy to "
                            "misread as giving values. `counts.values()` gives 4 and 3; `counts.items()` "
                            "gives the pairs and is what you want when you need both, usually written "
                            "`for kind, n in counts.items():`. Since Python 3.7 the order is the order the "
                            "keys were first inserted, so it is stable rather than arbitrary."
                        ),
                    },
                    {
                        "q": "You are counting how many of each kind of part a board uses. Which line does the job for a kind that may or may not have been seen before?",
                        "opts": [
                            "`counts[kind] = counts[kind] + 1`",
                            "`counts[kind] = counts.get(kind, 0) + 1`",
                            "`counts.append(kind)`",
                            "`counts[kind] += counts[kind]`",
                        ],
                        "a": 1,
                        "why": (
                            "`counts[kind] = counts.get(kind, 0) + 1` treats never-seen-before as zero and "
                            "carries on, which is exactly the tally you want. Reading `counts[kind]` "
                            "directly raises a KeyError the first time each kind appears, so the count only "
                            "works if you have already seeded every key by hand. `append` is a list method "
                            "and a dictionary does not have one; and doubling the existing count never adds "
                            "the one you just found."
                        ),
                    },
                ],
            },
            "match": {
                "title": "Five symbols, five kind codes",
                "minutes": 6,
                "brief": r'''
A parts list is only as good as the field that says what each part *is*. A netlist
gives a component a one-letter kind code, and it is the first character of the
reference — `R1` is a resistor, `C4` a capacitor — so `ref[0]` is a working answer
to "what kind of thing is this?".

Five of them cover most of a board. You will key a dictionary by codes like these
in the lab, so it is worth being able to look at a symbol and say the code without
stopping to think.
''',
                "prompt": "Pick a label, then tap the symbol that carries that kind code.",
                "labels": [
                    "kind \"R\" — resists current, dissipates the difference as heat",
                    "kind \"C\" — stores charge between two plates that never touch",
                    "kind \"L\" — stores energy in a magnetic field around a coil",
                    "kind \"D\" — conducts one way and blocks the other",
                    "kind \"S\" — makes or breaks the connection mechanically",
                ],
                "items": [
                    {"sym": "R", "a": 0, "why": "A resistor. The zig-zag and the plain rectangle are the "
                     "same component drawn in two standards, and neither is polarised, so a parts list "
                     "records a value and nothing about which way round it goes."},
                    {"sym": "C", "a": 1, "why": "A capacitor: two bars with a gap, because the gap is the "
                     "device. Two equal straight bars means non-polarised. Its value in a netlist is in "
                     "farads, which is why almost every real capacitor is written with an `n` or a `u` in "
                     "it \u2014 a whole farad is enormous."},
                    {"sym": "L", "a": 2, "why": "An inductor: a coil, drawn as a run of humps. It is the "
                     "capacitor's opposite in every respect that matters \u2014 it resists a change of "
                     "current the way a capacitor resists a change of voltage \u2014 and the two together "
                     "give you the oscillation you will simulate later in the course."},
                    {"sym": "D", "a": 3, "why": "A diode: a triangle pointing into a bar, and the bar is "
                     "the wall. Conventional current passes in the direction the triangle points and is "
                     "blocked the other way. It is polarised, so a parts list for a diode has to record "
                     "an orientation as well as a part number."},
                    {"sym": "SW", "a": 4, "why": "A switch: a lever lifted off its contact. It is the one "
                     "part here whose state is not in the netlist at all \u2014 the schematic shows how it "
                     "is wired, and whether it happens to be open or closed is a fact about the moment "
                     "rather than about the board."},
                ],
            },
            "blanks": {
                "title": "Condensing a parts list two ways",
                "minutes": 9,
                "lang": "python",
                "caption": "bom.py — four holes, and two printed results that must come out exactly as shown",
                "brief": r'''
Two things you will want from any list of records: a tally grouped by some field,
and a selection of it put in order. Both are three lines, and both have one spot
where the obvious-looking choice quietly produces something else.

Nothing runs here: you are choosing keys, methods and operators rather than writing
code. The two `print` lines at the bottom state what the filled-in version must
produce, so every choice can be checked against them rather than taken on trust.
''',
                "listing": r'''
# The parts list, condensed two ways.
parts = [
    {"ref": "R1", "kind": "R", "value": 4700.0, "qty": 1},
    {"ref": "C1", "kind": "C", "value": 1e-7,   "qty": 3},
    {"ref": "R2", "kind": "R", "value": 2200.0, "qty": 1},
]

total = {}
for p in parts:
    total[p[___]] = total.___(p["kind"], 0) + p["qty"]

resistors = [p for p in parts if p["kind"] ___ "R"]
in_order = sorted(resistors, key=lambda p: p[___])

print(total)                          # {'R': 2, 'C': 3}
print([p["ref"] for p in in_order])   # ['R2', 'R1']
''',
                "blanks": [
                    {
                        "prompt": "The tally is grouped by what the part is, not by which one it is.",
                        "hole": "key",
                        "opts": ["\"kind\"", "\"ref\"", "\"qty\"", "\"value\""],
                        "a": 0,
                        "why": "`\"kind\"` is the field two different resistors share, so `R1` and `R2` land on the same key and their quantities add. The printed tally has two entries for three parts, which is only possible if the key is something more than one record can carry.",
                        "whys": [
                            "`\"kind\"` is the field two different resistors share, so `R1` and `R2` land on the same key and their quantities add. The printed tally has two entries for three parts, which is only possible if the key is something more than one record can carry.",
                            "`\"ref\"` is unique to each line, so the tally would come out as `{'R1': 1, 'C1': 3, 'R2': 1}` — three entries, nothing grouped, and no more informative than the list it came from.",
                            "`\"qty\"` keys the tally by the count itself, and the `.get` on the same line still looks up `p[\"kind\"]`, which is now never a key — so it returns 0 every time and nothing accumulates. The result is `{1: 1, 3: 3}`: the thing being counted has become the label, and the two resistors have not even been added together.",
                            "`\"value\"` groups by resistance, so the two resistors stay apart and a float becomes a dictionary key — legal, and a trap, because two values that differ in the last bit are two different keys.",
                        ],
                    },
                    {
                        "prompt": "A kind that has not been seen yet has to count as zero rather than raise.",
                        "hole": "method",
                        "opts": ["get", "index", "keys", "count"],
                        "a": 0,
                        "why": "`get(key, 0)` returns the running total if the key is there and 0 if it is not, which is exactly the seed a tally needs. Writing `total[p[\"kind\"]]` instead raises a KeyError the first time each kind appears.",
                        "whys": [
                            "`get(key, 0)` returns the running total if the key is there and 0 if it is not, which is exactly the seed a tally needs. Writing `total[p[\"kind\"]]` instead raises a KeyError the first time each kind appears.",
                            "`index` is a list method: it reports where a value sits in a sequence. A dictionary has no positions to report, so this raises an AttributeError before it can do anything wrong.",
                            "`keys()` takes no arguments and returns the whole collection of keys, so this is a TypeError. Even given the right call, a collection of keys is not a number and cannot be added to a quantity.",
                            "`count` is another list method, and it counts occurrences of a value rather than looking one up. Dictionaries do not have it.",
                        ],
                    },
                    {
                        "prompt": "Keep the records whose kind is the letter R.",
                        "hole": "op",
                        "opts": ["==", "=", "!=", ">"],
                        "a": 0,
                        "why": "`==` compares two values and yields True or False, which is what a comprehension's `if` needs. Both resistors survive and the capacitor does not, giving the two references printed at the bottom.",
                        "whys": [
                            "`==` compares two values and yields True or False, which is what a comprehension's `if` needs. Both resistors survive and the capacitor does not, giving the two references printed at the bottom.",
                            "A single `=` is assignment, and assignment is a statement rather than an expression: this is a SyntaxError, not a subtly wrong answer. Python separates the two spellings precisely so that this typo cannot compile.",
                            "`!=` keeps everything that is *not* a resistor, so `resistors` would hold the capacitor alone and the printed list would read `['C1']`.",
                            "`>` compares strings alphabetically, and `\"R\" > \"R\"` is False, so both resistors are thrown away and the list comes out empty. It is legal Python, which is what makes it worth recognising.",
                        ],
                    },
                    {
                        "prompt": "Smallest resistance first.",
                        "hole": "key",
                        "opts": ["\"value\"", "\"ref\"", "\"kind\"", "\"qty\""],
                        "a": 0,
                        "why": "Sorting on `\"value\"` puts 2200 before 4700, so `R2` comes out ahead of `R1` — which is the order printed at the bottom, and the reverse of the order the records were written in.",
                        "whys": [
                            "Sorting on `\"value\"` puts 2200 before 4700, so `R2` comes out ahead of `R1` — which is the order printed at the bottom, and the reverse of the order the records were written in.",
                            "Sorting on `\"ref\"` orders the strings alphabetically and gives `['R1', 'R2']`, which happens to be the order they were already in. It looks like it worked and tells you nothing about resistance.",
                            "Every record here has the same kind, so sorting on it changes nothing at all: `sorted` is stable and leaves equal keys in their original order, giving `['R1', 'R2']`.",
                            "Both resistors have `\"qty\"` of 1, so this is the same do-nothing sort — and it would fall apart the moment someone ordered two of one of them.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "Three on the reel, three more from the drawer",
                    "minutes": 4,
                    "brief": r'''
One list, two ways of adding to it, and a length at the end. There is no arithmetic
here worth the name — only a decision about what each of the two methods actually
puts in.
''',
                    "prompt": "What number does this program print?",
                    "note": "A count of entries in the list.",
                    "figure": r'''
```python
stock = ["R1", "R2", "R3"]

stock.append("C1")             # add one element
stock.extend(["C2", "C3"])     # add each element of another sequence

print(len(stock))
```

`append` puts its argument in as a single element, whatever that argument happens to
be. `extend` walks the sequence it is handed and appends each item separately.
''',
                    "given": [
                        {"label": "Starting length", "value": "3"},
                        {"label": "append", "value": "one string"},
                        {"label": "extend", "value": "a list of two strings"},
                    ],
                    "aside": "Count what each call adds, not how many arguments it was given.",
                    "answer": 6.0,
                    "tol": 0.01,
                    "unit": "entries",
                    "hint": "`append` always adds exactly one entry. `extend` adds as many entries as the thing you hand it contains.",
                    "wrong": "5 is what you get if `extend` is read as `append` — the two-element list goes in whole and sits inside `stock` as a single entry, which is what `stock.append([\"C2\", \"C3\"])` genuinely does. 4 is the length after the `append` alone, which is where you stop if `extend` is read as handing back a new list and leaving `stock` as it was — that is what `stock + [\"C2\", \"C3\"]` really does, and it is the commoner of the two mistakes.",
                    "why": r'''
Three to start with, one from `append`, two from `extend`: $3 + 1 + 2 = 6$.

```
stock = ["R1", "R2", "R3"]      ['R1', 'R2', 'R3']                      3
stock.append("C1")              ['R1', 'R2', 'R3', 'C1']                4
stock.extend(["C2", "C3"])      ['R1', 'R2', 'R3', 'C1', 'C2', 'C3']    6
```

The distinction is worth more than the two entries it moved. `append` takes one object
and makes it one element — a string, a number, a record, or a list, and that last case
is where the trouble starts. Write `stock.append(["C2", "C3"])` and `stock` comes out
five long with its final element a list. Nothing raises, nothing is printed in red.
You find out much later, when something asks for `stock[4][0]` expecting the letter
that says what kind of part it is and gets `"C2"` instead.

Both methods edit the list in place and return `None`, so `stock = stock.append("C1")`
throws the list away and leaves the name bound to nothing at all. That shape — change
the object, return nothing — is the same one `.sort()` has, for the same reason:
Python does not hand back the thing it has just modified, so that you cannot mistake
an edit for a copy.
''',
                },
                {
                    "title": "The window in the middle of the log",
                    "minutes": 6,
                    "brief": r'''
Six readings from a meter, and a slice that keeps some of them. Two steps: work out
which readings the slice contains, then add them. Almost everyone who gets this wrong
gets the second step right.
''',
                    "prompt": "What number does this program print?",
                    "note": "Exactly as printed, to two decimal places.",
                    "figure": r'''
```python
i_mA = [0.42, 1.87, 3.05, 2.14, 0.98, 1.61]   # six currents, milliamps

window = i_mA[1:4]
print(round(sum(window), 2))
```

A slice `xs[a:b]` starts at position `a` and stops *before* position `b`. Positions
count from 0.
''',
                    "given": [
                        {"label": "Readings", "value": "0.42, 1.87, 3.05, 2.14, 0.98, 1.61 mA"},
                        {"label": "Slice", "value": "[1:4]"},
                        {"label": "Reported to", "value": "two decimal places"},
                    ],
                    "aside": "Write the six positions out, 0 to 5, with a reading under each, before you decide which ones the slice takes.",
                    "answer": 7.06,
                    "tol": 0.005,
                    "unit": "mA",
                    "hint": "The slice takes positions 1, 2 and 3 — three readings, because $4 - 1 = 3$ — and stops before position 4.",
                    "wrong": "8.04 takes the reading at position 4 as well, which is what `i_mA[1:5]` would do. 5.34 is the first three readings, which is where you land by counting the list from 1 instead of from 0.",
                    "why": r'''
The slice runs from position 1 up to but not including position 4:

```
position     0     1     2     3     4     5
reading    0.42  1.87  3.05  2.14  0.98  1.61
                  |-----------|
                  i_mA[1:4] = [1.87, 3.05, 2.14]
```

and the three of them add up:

```
1.87 + 3.05 = 4.92
4.92 + 2.14 = 7.06
```

so the program prints **7.06** mA. The length of the slice is $4 - 1 = 3$ with no
correction term, and that is the entire reason the stop is excluded: it makes `xs[:k]`
and `xs[k:]` fit together with no overlap and no gap for any `k` you care to pick, so
a run of samples can be split in two without an argument about who owns the join.

One detail is worth seeing here, because it is module 1's rule turning up somewhere
nobody looks for it. `sum(window)` is not 7.06. It is 7.0600000000000005, because none
of 1.87, 3.05 and 2.14 is exactly representable in binary and this time the errors did
not cancel. `round(..., 2)` cleans that up for display and the printed answer is
correct. But had you written `sum(window) == 7.06` you would have got `False`, and had
you compared two such sums for equality you would have had a test that fails on
nothing at all. Round for printing; compare with a tolerance.
''',
                },
                {
                    "title": "How many capacitors does the board take?",
                    "minutes": 7,
                    "brief": r'''
A bill of materials and a tally by kind. The trap is not in the loop — it is in the
difference between a line of the order and a part on the board. Two of these lines
are capacitors, and neither of them is a line for one capacitor.
''',
                    "prompt": "What number does this program print?",
                    "note": "A count of parts.",
                    "figure": r'''
```python
BOM = [
    {"ref": "R1", "kind": "R", "qty": 2},
    {"ref": "C1", "kind": "C", "qty": 3},
    {"ref": "R2", "kind": "R", "qty": 1},
    {"ref": "C2", "kind": "C", "qty": 4},
    {"ref": "D1", "kind": "D", "qty": 1},
]

count = {}
for p in BOM:
    count[p["kind"]] = count.get(p["kind"], 0) + p["qty"]

print(count["C"])
```

`d.get(k, 0)` returns `d[k]` if the key is there and 0 if it is not.
''',
                    "given": [
                        {"label": "Capacitor lines", "value": "C1 qty 3, C2 qty 4"},
                        {"label": "Other lines", "value": "R1 qty 2, R2 qty 1, D1 qty 1"},
                        {"label": "Printed", "value": "count[\"C\"]"},
                    ],
                    "aside": "Only the lines whose kind is \"C\" reach the entry that gets printed. The rest of the tally is built and never looked at.",
                    "answer": 7.0,
                    "tol": 0.01,
                    "unit": "capacitors",
                    "hint": "Two lines carry kind `\"C\"`. Add their quantities — the loop is doing nothing more than that for each kind separately.",
                    "wrong": "2 counts the capacitor *lines* rather than the capacitors, which is what adding 1 instead of `p[\"qty\"]` would give. 4 is what comes out if the body reads `count[p[\"kind\"]] = p[\"qty\"]` — assignment where accumulation was meant, so C2 overwrites C1 and only the last line of each kind survives. 11 is every part on the board, of every kind.",
                    "why": r'''
Walk the loop one line at a time. `count` starts empty.

```
part  kind  qty   count.get(kind, 0)   count afterwards
--------------------------------------------------------------------
R1     R     2      0  (never seen)    {'R': 2}
C1     C     3      0  (never seen)    {'R': 2, 'C': 3}
R2     R     1      2                  {'R': 3, 'C': 3}
C2     C     4      3                  {'R': 3, 'C': 7}
D1     D     1      0  (never seen)    {'R': 3, 'C': 7, 'D': 1}
```

`count["C"]` is **7**: three from C1 and four from C2.

Check the tally the way you check any grouping — it has to conserve the total. The
quantities on the five lines are $2 + 3 + 1 + 4 + 1 = 11$, and the finished
dictionary's values are $3 + 7 + 1 = 11$. When those two disagree something has been
dropped or double-counted, and you know that before you know which.

`get(kind, 0)` is doing exactly one job, and it is the job that lets a single line
handle both the first capacitor line and the second: it turns "this kind has never
been seen" into "the running total so far is zero", which is true. Read
`count[p["kind"]]` directly instead and the program raises a KeyError on the very
first part, because at that instant the dictionary is empty — and the only way round
that without `get` is to seed every key by hand before the loop, which means knowing
every kind the file contains before you have read the file.

Worth noticing what the answer is *not*. There are five lines, two of them
capacitors, and seven capacitors. Three different true numbers describe the same
order, and a quantity column exists precisely because they differ.
''',
                },
                {
                    "title": "Where R3 lands once the list is sorted",
                    "minutes": 8,
                    "brief": r'''
Sorting is only half of this one. The question asks for a *position*, which means
doing the sort in your head, writing the order out with the references attached, and
then counting — counting the way Python counts.
''',
                    "prompt": "What number does this program print?",
                    "note": "A position in the list.",
                    "figure": r'''
```python
parts = [
    {"ref": "R1", "value": 4700.0},
    {"ref": "R2", "value": 220.0},
    {"ref": "R3", "value": 3300.0},
    {"ref": "R4", "value": 47.0},
    {"ref": "R5", "value": 1000.0},
]

in_order = sorted(parts, key=lambda p: p["value"])
refs = [p["ref"] for p in in_order]

print(refs.index("R3"))
```

`sorted(xs, key=f)` returns a new list ordered by `f(x)`, smallest first.
`refs.index(x)` returns the position of the first `x` in `refs`, counting from 0.
''',
                    "given": [
                        {"label": "R1", "value": "4700 Ω"},
                        {"label": "R2", "value": "220 Ω"},
                        {"label": "R3", "value": "3300 Ω"},
                        {"label": "R4", "value": "47 Ω"},
                        {"label": "R5", "value": "1000 Ω"},
                    ],
                    "aside": "Write the five values out in ascending order with the reference beside each. Only then start counting.",
                    "answer": 3.0,
                    "tol": 0.01,
                    "hint": "Ascending, the values are 47, 220, 1000, 3300, 4700. R3 is the 3300 one. Now count positions from 0 rather than from 1.",
                    "wrong": "4 is the same place counted from 1 — the fourth item sits at index 3. 2 is where R3 sits if the list is sorted by reference instead of by value, which here is the order it was already written in.",
                    "why": r'''
Sort on the value and keep the reference beside it:

```
value       ref     position
----------------------------
   47.0     R4         0
  220.0     R2         1
 1000.0     R5         2
 3300.0     R3         3     <--
 4700.0     R1         4
```

so `refs` is `['R4', 'R2', 'R5', 'R3', 'R1']` and `refs.index("R3")` is **3**.

Three things this question is really about.

**`key` says what to compare, not what to keep.** `sorted(parts, key=lambda p: p["value"])`
reorders whole records; the lambda is consulted only to decide which record goes
first. What comes out are the same record objects that went in, which is why
`p["ref"]` is still there to be read afterwards. Ask for `sorted(parts)` with no key
and you get a TypeError, because `<` is not defined between two dictionaries and
Python declines to guess which field you meant.

**`sorted` builds a new list.** After this runs, `parts` is still in the order it was
written, R1 first — which is why `refs` had to be built from `in_order` and not from
`parts`. That is usually the behaviour you want, because the order of a file is
itself information. `parts.sort(key=...)` would reorder `parts` where it stands and
return `None`.

**Counting from 0 is not a convention you can opt out of.** The 3300 Ω resistor is the
fourth smallest and sits at index 3. The identity that makes an index worth having is
`refs[refs.index(x)] == x`, and it holds only because the two count the same way. Mix
the conventions — a position written down as "the fourth" and then used as an index —
and you fetch the neighbour instead, silently, since index 4 is a perfectly good
position with a perfectly good resistor in it.
''',
                },
                {
                    "title": "What share of the order is the dearest line?",
                    "minutes": 10,
                    "brief": r'''
Five lines, and an answer that appears on none of them. You need every line's cost,
the total of those, which line is the biggest, and then a ratio — four steps, and a
wrong turn at any one of them still produces a plausible-looking percentage.
''',
                    "prompt": "What number does this program print?",
                    "note": "A percentage, to one decimal place.",
                    "figure": r'''
```python
BOM = [
    {"ref": "R1", "kind": "R", "qty": 6, "price": 0.03},
    {"ref": "C1", "kind": "C", "qty": 4, "price": 0.12},
    {"ref": "L1", "kind": "L", "qty": 1, "price": 1.25},
    {"ref": "D1", "kind": "D", "qty": 8, "price": 0.07},
    {"ref": "C2", "kind": "C", "qty": 2, "price": 0.41},
]

cost = {}
for p in BOM:
    cost[p["ref"]] = p["qty"] * p["price"]      # what that LINE costs

top = max(cost, key=cost.get)                   # the ref with the largest line cost

print(round(100.0 * cost[top] / sum(cost.values()), 1))
```

`price` is per part; `qty` is how many of them the order takes.
`max(d, key=d.get)` returns the KEY whose value is largest.
''',
                    "given": [
                        {"label": "R1", "value": "6 at 0.03"},
                        {"label": "C1", "value": "4 at 0.12"},
                        {"label": "L1", "value": "1 at 1.25"},
                        {"label": "D1", "value": "8 at 0.07"},
                        {"label": "C2", "value": "2 at 0.41"},
                    ],
                    "aside": "Work the five line costs out first and write them down. Everything after that is arithmetic on those five numbers.",
                    "answer": 38.0,
                    "tol": 0.05,
                    "unit": "%",
                    "hint": "A line costs quantity times price. Add the five to get the order total, take the largest of the five, and write it as a percentage of that total.",
                    "wrong": "66.5 comes from ranking and totalling the *unit prices* and ignoring quantity throughout — 1.25 out of 1.88. 17.0 is D1's share, which is where you land if the dearest line is taken to be the one with the most parts on it.",
                    "why": r'''
Four steps, and the intermediate numbers are the whole of it.

```
ref    qty   price    line cost
-------------------------------
R1      6    0.03       0.18
C1      4    0.12       0.48
L1      1    1.25       1.25    <-- the largest
D1      8    0.07       0.56
C2      2    0.41       0.82
-------------------------------
                        3.29     the order total
```

$$\frac{1.25}{3.29} \times 100 = 37.9939\ldots \approx \mathbf{38.0}\ \%$$

One inductor is more than a third of the bill of materials, and it is the only line on
the board with a single part on it.

**Why quantity has to be inside the comparison and not only inside the total.** D1 is
eight parts and R1 is six; L1 is one. Rank by how many of something the board takes
and D1 wins, giving $0.56/3.29 = 17.0\ \%$. Rank by unit price and L1 wins too — the
same answer as ranking by line cost, this time — so a correct-looking result here is
not evidence that you multiplied. Change one row, say C2 to 40 parts at 0.41, and the
two rankings part company at once.

**What `max(cost, key=cost.get)` returns.** Iterating a dictionary gives keys, so
`max` is choosing among the five reference strings; `key=cost.get` tells it to compare
`cost.get(ref)` — the line cost — rather than the strings themselves. Drop the `key`
and it compares `'R1'`, `'C1'`, `'L1'`, `'D1'`, `'C2'` alphabetically and hands back
`'R1'`, which is a real answer to a question nobody asked ($0.18/3.29 = 5.5\ \%$).
`max(cost.values())` gives 1.25, the cost itself, and then you have the number without
the line it belongs to — which is why the index is keyed by reference in the first
place.

**On the arithmetic.** All five products and their total happen to come out as the
nearest double to the decimal you would write by hand, so nothing prints with a tail
of nines. That is luck: $6 \times 0.03$ is a float multiplication like any other, and
one more row would probably have spoiled it. It is why the final line rounds for
display, and why two such totals are compared with a tolerance rather than with `==`.
''',
                },
            ],
            "derive": {
                "title": "When an index has paid for itself",
                "minutes": 14,
                "vars": ["n", "m"],
                "brief": r'''
The lab finds a part by walking the list until it hits one with the right reference.
That is honest and it is fine — until the number of lookups grows, at which point
the same work is better done by building a dictionary once and then never comparing
anything again.

"At which point" is a real question with a real answer, and it is arithmetic rather
than taste. Let $n$ be the number of records in the parts list and $m$ the number of
lookups you are going to do against it. Count comparisons for the scan, count
operations for the index, set the two equal, and solve.
''',
                "steps": [
                    {
                        "prompt": "A scan compares the wanted reference against each record in turn, from the front. How many comparisons does it take to establish that a reference is *not* in the list at all? Write it in terms of $n$.",
                        "answer": "n",
                        "hint": "There is no way to be sure something is absent without having looked everywhere it could have been.",
                        "deconstruct": [
                            "The scan knows nothing about where a match might be, so it cannot skip a record.",
                            "It stops early only when it finds a match, and an absent reference never produces one.",
                            "So every one of the $n$ records is compared: $n$ comparisons.",
                        ],
                    },
                    {
                        "prompt": "Now take a reference that IS present, equally likely to be at any of the $n$ positions. Finding it at position $k$ (counting from 1) costs $k$ comparisons. Write the average cost over all $n$ positions.",
                        "answer": "\\frac{n + 1}{2}",
                        "placeholder": "\\frac{...}{...}",
                        "hint": "Average the whole numbers from 1 to $n$. Their sum is $n(n+1)/2$.",
                        "deconstruct": [
                            "The costs are $1, 2, 3, \\ldots, n$, each equally likely.",
                            "Their sum is $n(n+1)/2$.",
                            "Dividing by the $n$ positions leaves $(n+1)/2$.",
                        ],
                    },
                    {
                        "prompt": "You do $m$ lookups, every one of them present. Write the total number of comparisons the scan costs, in terms of $m$ and $n$.",
                        "answer": "\\frac{m(n + 1)}{2}",
                        "hint": "Each lookup costs the average you just found, and there are $m$ of them.",
                    },
                    {
                        "prompt": "The index is built by one pass over the parts list — one insertion per record — after which each of the $m$ lookups costs one operation regardless of $n$. Write the total cost of the index, in terms of $m$ and $n$.",
                        "answer": "n + m",
                        "hint": "$n$ insertions to build it, then $m$ lookups at one operation each. Nothing is compared more than once.",
                    },
                    {
                        "prompt": "Set the two totals equal and solve for $m$: the number of lookups at which the index has exactly paid for itself. Write $m$ in terms of $n$.",
                        "answer": "\\frac{2n}{n - 1}",
                        "placeholder": "an expression in n",
                        "hint": "Multiply through to clear the 2, gather the $m$ terms on one side, and factor $m$ out.",
                        "deconstruct": [
                            "$m(n+1)/2 = n + m$, so $m(n+1) = 2n + 2m$.",
                            "Expanding the left side: $mn + m = 2n + 2m$, hence $mn + m - 2m = 2n$.",
                            "That is $mn - m = 2n$, or $m(n-1) = 2n$, giving $m = 2n/(n-1)$.",
                        ],
                    },
                    {
                        "prompt": "Take the common case of one lookup per record, $m = n$. Write the ratio of the scan's cost to the index's cost, simplified, in terms of $n$.",
                        "answer": "\\frac{n + 1}{4}",
                        "hint": "Substitute $m = n$ into both totals and divide one by the other. An $n$ cancels.",
                        "deconstruct": [
                            "With $m = n$ the scan costs $n(n+1)/2$ and the index costs $n + n = 2n$.",
                            "The ratio is $\\frac{n(n+1)/2}{2n}$.",
                            "Cancelling the $n$ and combining the constants leaves $(n+1)/4$.",
                        ],
                    },
                ],
                "closing": r'''
Put numbers in.

```
n = 60 parts, m = 200 references to resolve

    scan     m(n+1)/2 = 200 x 30.5     = 6100 comparisons
    index    n + m    =  60 + 200      =  260 operations
    ratio                              =   23.5 x

breakeven, m = 2n/(n-1)

    n =   5      m = 2.50      index ahead from the 3rd lookup on
    n =  60      m = 2.03      index ahead from the 3rd lookup on
    n = 400      m = 2.01      index ahead from the 3rd lookup on

one lookup per record, m = n:  ratio (n+1)/4

    n =   5        1.5 x
    n =  60       15.25 x
    n = 400      100.25 x
```

Four things come out of that, and only one of them is about speed.

**The breakeven barely depends on $n$.** $2n/(n-1)$ is 2.5 at $n = 5$ and 2.005 at
$n = 400$; it falls towards 2 and never goes below it. As a rule of thumb: if you are
going to look something up more than twice, build the index. That is a far simpler
answer than the algebra threatened, and it is the one worth carrying around.

**Look something up once, and the scan wins.** At $m = 1$ the scan costs $(n+1)/2$ and
the index costs $n + 1$, so the index is twice as expensive — it touched every record
to build itself and you then used one of them. This is not a defect in the model. It
is the reason `find` in the lab is the right function to have written: a single lookup
does not deserve a data structure.

**The two counts are not the same currency, and it does not matter.** A string
comparison and a dictionary insertion are not the same price, and a hash lookup is
several machine operations rather than one. Every constant above could be out by a
factor of two or three. What cannot be out by a factor of two is the *shape*: the
scan's cost per lookup grows with $n$ and the index's does not, so whatever the
constants turn out to be, there is some $n$ past which the index wins by as large a
factor as you like. Getting the shape right and the constants roughly right is what
counting operations is for. If you need the constants exactly, stop counting and
measure.

**Misses make the case stronger, not weaker.** The first step counted $n$ comparisons
for a reference that is absent, against $(n+1)/2$ for one that is present. A netlist
naming a part the bill of materials does not carry is precisely the error you are
hunting, and it costs the scan its worst case every single time, while the index
answers it in the same one operation it uses for a hit. The check you most want to run
is the one the scan is worst at.

Module 6 makes the same trade in a different currency: an array expression and a
Python loop compute identical numbers, and the array wins for a structural reason
rather than because somebody wrote a tighter loop. Recognising that shape — the cost
that grows with the data against the cost that does not — is most of what
"making it faster" means.
''',
            },
            "lab": {
                "title": "What a parts list can be asked",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
`BOM` in the starter is a bill of materials: a list of records, one per line of the
order, each with a reference, a kind, a value, a quantity and a unit price. Five
functions, and none of them is longer than about four lines.

`total_cost(parts)` returns what the whole order costs — quantity times price,
summed. Watch the quantity: a line for four diodes at 7p is 28p, not 7p.

`count_by_kind(parts)` returns a dictionary from kind code to the total quantity of
that kind, so four resistors spread over three lines come back as one entry reading
4.

`refs_of_kind(parts, kind)` returns the references of every part of that kind, in the
order they appear in the list.

`dearest_line(parts)` returns the reference of the line that costs the most —
quantity times price again, so a cheap part ordered many times can beat an expensive
one ordered once. When two lines tie, keep the earlier.

`sorted_refs(parts, kind)` returns the references of that kind ordered by value,
smallest first, and must leave `parts` in the order it was given. Use `sorted`, not
`.sort()`.
''',
                "files": [{"name": "main.py", "content": r'''
BOM = [
    {"ref": "R1", "kind": "R", "value": 4700.0, "qty": 1, "price": 0.04},
    {"ref": "R2", "kind": "R", "value": 2200.0, "qty": 1, "price": 0.04},
    {"ref": "R3", "kind": "R", "value": 3300.0, "qty": 2, "price": 0.04},
    {"ref": "C1", "kind": "C", "value": 1e-7,   "qty": 3, "price": 0.11},
    {"ref": "C2", "kind": "C", "value": 1e-5,   "qty": 1, "price": 0.38},
    {"ref": "L1", "kind": "L", "value": 1e-2,   "qty": 1, "price": 1.25},
    {"ref": "D1", "kind": "D", "value": 0.0,    "qty": 4, "price": 0.07},
]


def total_cost(parts):
    """What the whole order costs: quantity times price, summed."""
    # TODO: one loop, or one sum over a comprehension.
    return 0.0


def count_by_kind(parts):
    """Kind code -> total quantity of that kind."""
    out = {}
    # TODO: tally into out, treating an unseen kind as 0.
    return out


def refs_of_kind(parts, kind):
    """The references of every part of that kind, in list order."""
    # TODO
    return []


def dearest_line(parts):
    """The reference of the line costing the most; earlier line wins a tie."""
    # TODO: keep a best-so-far, replace it only when strictly beaten.
    return ""


def sorted_refs(parts, kind):
    """References of that kind, by value ascending. Must not reorder parts."""
    # TODO: select first, then sorted(..., key=...).
    return []


if __name__ == "__main__":
    print("total:", round(total_cost(BOM), 2))
    print("by kind:", count_by_kind(BOM))
    print("resistors:", refs_of_kind(BOM, "R"))
    print("dearest line:", dearest_line(BOM))
    print("resistors by value:", sorted_refs(BOM, "R"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
BOM = [
    {"ref": "R1", "kind": "R", "value": 4700.0, "qty": 1, "price": 0.04},
    {"ref": "R2", "kind": "R", "value": 2200.0, "qty": 1, "price": 0.04},
    {"ref": "R3", "kind": "R", "value": 3300.0, "qty": 2, "price": 0.04},
    {"ref": "C1", "kind": "C", "value": 1e-7,   "qty": 3, "price": 0.11},
    {"ref": "C2", "kind": "C", "value": 1e-5,   "qty": 1, "price": 0.38},
    {"ref": "L1", "kind": "L", "value": 1e-2,   "qty": 1, "price": 1.25},
    {"ref": "D1", "kind": "D", "value": 0.0,    "qty": 4, "price": 0.07},
]


def total_cost(parts):
    """What the whole order costs: quantity times price, summed."""
    return sum(p["qty"] * p["price"] for p in parts)


def count_by_kind(parts):
    """Kind code -> total quantity of that kind."""
    out = {}
    for p in parts:
        out[p["kind"]] = out.get(p["kind"], 0) + p["qty"]
    return out


def refs_of_kind(parts, kind):
    """The references of every part of that kind, in list order."""
    return [p["ref"] for p in parts if p["kind"] == kind]


def dearest_line(parts):
    """The reference of the line costing the most; earlier line wins a tie."""
    best = None
    for p in parts:
        if best is None or p["qty"] * p["price"] > best["qty"] * best["price"]:
            best = p
    return best["ref"] if best else ""


def sorted_refs(parts, kind):
    """References of that kind, by value ascending. Must not reorder parts."""
    chosen = [p for p in parts if p["kind"] == kind]
    return [p["ref"] for p in sorted(chosen, key=lambda p: p["value"])]


if __name__ == "__main__":
    print("total:", round(total_cost(BOM), 2))
    print("by kind:", count_by_kind(BOM))
    print("resistors:", refs_of_kind(BOM, "R"))
    print("dearest line:", dearest_line(BOM))
    print("resistors by value:", sorted_refs(BOM, "R"))
'''}],
                "hints": [
                    "`sum(p[\"qty\"] * p[\"price\"] for p in parts)` is the whole of `total_cost`. The multiplication has to be inside the sum, not applied to it afterwards.",
                    "The tally line is `out[p[\"kind\"]] = out.get(p[\"kind\"], 0) + p[\"qty\"]`. Adding 1 instead of the quantity gives you a count of lines rather than a count of parts, and the two differ here.",
                    "`dearest_line` is the search pattern from module 2: keep a best-so-far and replace it only when the new candidate is strictly better, so a tie leaves the earlier one in place.",
                    "`sorted(chosen, key=lambda p: p[\"value\"])` returns a new list; `chosen.sort()` would try to compare dictionaries and raise. Either way, `parts` itself must come back untouched, which is why the selection is taken first.",
                ],
                "tests": [
                    {"name": "the total counts every unit, not every line", "code": r'''
_t = total_cost(BOM)
assert abs(_t - 2.40) < 1e-9, \
    (f"the order comes to 2.40; got {_t}. If you got 1.93 you summed the prices and "
     "ignored the quantities")
'''},
                    {"name": "the tally groups three resistor lines into one entry", "code": r'''
_c = count_by_kind(BOM)
assert _c == {"R": 4, "C": 4, "L": 1, "D": 4}, \
    (f"expected {{'R': 4, 'C': 4, 'L': 1, 'D': 4}}, got {_c}. Four resistors arrive on three "
     "lines because R3 is ordered twice")
'''},
                    {"name": "selection keeps the order of the list", "code": r'''
assert refs_of_kind(BOM, "R") == ["R1", "R2", "R3"], \
    f"expected ['R1', 'R2', 'R3'], got {refs_of_kind(BOM, 'R')}"
assert refs_of_kind(BOM, "L") == ["L1"], f"got {refs_of_kind(BOM, 'L')}"
assert refs_of_kind(BOM, "Q") == [], "a kind that is not on the board gives an empty list"
'''},
                    {"name": "the dearest line is a line, not a part", "code": r'''
assert dearest_line(BOM) == "L1", \
    (f"L1 costs 1.25 and is the most expensive line; got {dearest_line(BOM)!r}. "
     "D1 is the answer if you compared quantities and forgot the price. Comparing "
     "unit prices happens to give L1 here too, so a pass is not proof you multiplied")
'''},
                    {"name": "sorting is by value and leaves the list alone", "code": r'''
_before = [p["ref"] for p in BOM]
assert sorted_refs(BOM, "R") == ["R2", "R3", "R1"], \
    f"2200, 3300, 4700 gives ['R2', 'R3', 'R1']; got {sorted_refs(BOM, 'R')}"
assert sorted_refs(BOM, "C") == ["C1", "C2"], f"got {sorted_refs(BOM, 'C')}"
assert [p["ref"] for p in BOM] == _before, \
    "BOM came back reordered - use sorted(...), which returns a new list, not .sort()"
'''},
                    {"name": "nothing is hard-wired to this particular order", "code": r'''
_other = [
    {"ref": "R9", "kind": "R", "value": 100.0, "qty": 5, "price": 0.02},
    {"ref": "D2", "kind": "D", "value": 0.0, "qty": 1, "price": 0.90},
    {"ref": "R8", "kind": "R", "value": 47.0, "qty": 1, "price": 0.02},
]
assert abs(total_cost(_other) - 1.02) < 1e-9, f"expected 1.02, got {total_cost(_other)}"
assert count_by_kind(_other) == {"R": 6, "D": 1}, f"got {count_by_kind(_other)}"
assert dearest_line(_other) == "D2", f"0.90 beats 0.10 and 0.02; got {dearest_line(_other)!r}"
assert sorted_refs(_other, "R") == ["R8", "R9"], f"47 before 100; got {sorted_refs(_other, 'R')}"
assert total_cost([]) == 0, "an empty order costs nothing rather than raising"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Text, files, and the numbers hiding in them",
            "summary": "Everything a program reads from a file arrives as text. Turning it back into numbers is where a large share of the wrong answers in engineering software are born.",
            "concepts": [
                "`\"4k7\"` is 4700 \u03a9. Engineering notation puts the multiplier where the decimal point would go, so a smudged dot cannot turn 4.7 k\u03a9 into 47 k\u03a9. `float(\"4k7\")` raises \u2014 it is not a number until you make it one.",
                "The prefixes are powers of a thousand: `p` 10\u207b\u00b9\u00b2, `n` 10\u207b\u2079, `u` 10\u207b\u2076, `m` 10\u207b\u00b3, `k` 10\u00b3, `M` 10\u2076. Case matters: `m` is milli and `M` is mega, a factor of a billion apart.",
                "String methods do the cutting: `s.strip()` removes surrounding whitespace, `s.split()` cuts on runs of whitespace, `s.split(\",\")` cuts on a character, `s.startswith(\"#\")` tests the beginning.",
                "A string is a sequence: `s[0]` is a character, `s[1:]` the rest, `s[-1]` the last. None of it can be changed in place \u2014 every string operation returns a new string.",
                "A *netlist* is the text form of a schematic: one component per line, giving its reference, the two nodes it joins and its value. Every circuit simulator ever written reads one.",
                "Skip blank lines and comment lines before interpreting anything. A parser that trusts every line dies on the header, and one that silently ignores what it cannot read hands you a smaller dataset and no warning.",
            ],
            "read": [
                {
                    "title": "Everything arrives as text",
                    "minutes": 15,
                    "body": r'''
A reel of resistors arrives with `4K7` printed on the paper tape. A bench meter
writes `2024-03-11 09:41:02  0.4870  11.98` into a log file once a second. The
schematic editor you drew a circuit in exports it as six lines you could read aloud.
Not one of those things wrote a number. Every one of them wrote **characters** — and
a character is a shape, not a quantity.

Somewhere between the tape and the sum, a shape has to become a value. That step is
short, it is unglamorous, and a startling share of the wrong answers in engineering
software are born in it. Not because the arithmetic afterwards was hard, but because
the thing being added up was never the number anybody thought it was.

## A string is a sequence, and it cannot be edited

A **string** is an ordered run of characters under one name, written between quotes:

```python
field = "4k7"
```

It indexes and slices exactly as the list in module 3 did, and for the same reason —
both are sequences, and Python gives every sequence the same notation:

```
field[0]     '4'          the first character, counting from zero
field[1]     'k'
field[-1]    '7'          the last, counted backwards
field[:1]    '4'          everything before position 1
field[2:]    '7'          everything from position 2 on
len(field)    3
'k' in field  True        does this character appear anywhere?
field.index('k')  1       and if so, where?
```

There is no separate character type: `field[0]` is itself a string, one character
long. That is convenient and occasionally confusing — `field[0] == "4"` is a
comparison of two strings and is `True`, while `field[0] == 4` compares a string with
an integer and is `False`, quietly, without complaint.

The one place a string differs sharply from a list is that **it cannot be changed**.
`field[0] = "5"` raises a `TypeError`. Every string method that looks like it edits
one in fact builds a new string and hands it back, leaving the original exactly as it
was:

```python
s = "  4k7 \n"
s.strip()          # -> '4k7'   ... and thrown away
print(s)           # '  4k7 \n' - unchanged
s = s.strip()      # the version that keeps the result
```

Calling `s.strip()` and ignoring what comes back is a line that reads like it did
something and did not. It is the same shape of mistake as `xs.sort()` from module 3,
arriving from the opposite direction: `sort` edits and returns nothing, `strip`
returns and edits nothing, and both punish the assumption that a method call must do
one particular one of those two things.

## The three cuts

Almost all the text an engineer meets is cut apart with three methods.

**`strip()`** removes whitespace — spaces, tabs, newlines — from both ends and
nothing from the middle. It is what makes a file written by a human, with its ragged
alignment and its trailing spaces, behave like a file written by a machine.
`lstrip()` and `rstrip()` do one end each; `rstrip()` alone is what you want when a
line's trailing `\n` is the only problem.

**`split()`** cuts a string into a list of pieces. Called with no argument it cuts on
*runs* of whitespace and discards them, which is precisely right for a column-aligned
file:

```
"R1   in   mid   4k7".split()      ->  ['R1', 'in', 'mid', '4k7']
```

Called with a separator it cuts on each occurrence of exactly that string, keeps
everything else including spaces, and — this is the part that surprises people —
produces an empty string wherever two separators sit together:

```
" 12 , 3 ".split(",")     ->  [' 12 ', ' 3 ']
"a,,b".split(",")         ->  ['a', '', 'b']
"a   b".split(" ")        ->  ['a', '', '', 'b']
```

The last line is the argument for bare `split()` on anything aligned into columns.
`split(" ")` treats three spaces as three separators with two empty fields between
them; `split()` treats them as one gap.

**`startswith(prefix)`** answers a yes-or-no question about the beginning, which is
how comment lines are recognised. `line.startswith("#")` and `line[0] == "#"` say the
same thing, except that the second raises an `IndexError` on an empty line and the
first calmly returns `False`.

## Why the letter stands where the decimal point goes

Now the value field itself. A resistor of 4.7 kΩ is written `4k7`, not `4.7k`, and
this is not decoration.

A decimal point is one dot of ink. Photocopy a parts list twice, print it on a
dot-matrix printer, mark it up in the workshop, or read it off a component body
0.3 mm long, and that dot is the first thing to disappear — and losing it turns 4.7
into 47, a factor of ten, in a way that leaves behind a perfectly plausible-looking
number. A letter cannot fall off. So the multiplier is moved into the position the
point would have occupied and does both jobs at once: it says *where the point is*
and *what power of a thousand to apply*, and the field survives being smudged,
scanned and shouted across a workshop.

The prefixes are powers of a thousand:

```
    p     1e-12      pico
    n     1e-9       nano
    u     1e-6       micro     (a plain 'u' stands in for the Greek mu)
    m     1e-3       milli
    R     1e0        no prefix at all - the letter is there to hold the point
    k     1e3        kilo
    M     1e6        mega
```

Two of those are worth staring at. `R` is a multiplier of one: `470R` is 470 Ω and
`4R7` is 4.7 Ω, and the letter earns its place purely by marking the point. And `m`
and `M` differ only in case while differing by a factor of $10^9$ in value — a
billion — so a parser that helpfully upper-cases its input before looking anything up
has just turned every milliamp into a megaamp.

Python knows none of this. `float("4k7")` does not return 4700 and does not return
4.7: it raises

```
ValueError: could not convert string to float: '4k7'
```

which is exactly the right behaviour and worth being glad about. The alternative — a
conversion that ignores what it does not recognise and hands back 4.7 — would put
every value in the design out by a factor of a thousand with nothing on screen to say
so. Turning `4k7` into 4700.0 is a job the standard library will not do for you,
because it is a convention from an engineering standard rather than a fact about
arithmetic. You have to write it.

## Worked example 1: `4k7`, one character at a time

The rule in words: scan the field for a prefix letter; the digits before it are whole
units of that prefix and the digits after it are the fraction; join the two halves
with a decimal point between them and multiply by the prefix.

Trace it on `"4k7"`.

```
i   ch    is ch a prefix?      what happens
--------------------------------------------------------------
0   '4'   no                   keep scanning
1   'k'   yes, 1e3             stop here

    left   = text[:1]   = '4'          before the letter
    right  = text[2:]   = '7'          after the letter
    digits = '4' + '.' + '7'  = '4.7'
    value  = float('4.7') * 1e3
           = 4.7 * 1000
           = 4700.0
```

Two details in that trace do real work. The slice after the letter is `text[i+1:]`
and not `text[i:]` — position `i` holds the letter itself, and leaving it in gives
`digits = '4.k7'`, which `float` refuses. And the join is done on *strings*, before
any arithmetic happens: `"4" + "." + "7"` is the three-character string `"4.7"`, and
only then does `float` see a thing it recognises. Trying to do it numerically —
taking 4, taking 7, and combining them — needs to know how many digits are in the
second half, which is a division and a logarithm and an opportunity to be wrong.
Concatenating characters needs to know nothing.

## Worked example 2: three more fields, and one that must refuse

```
'100n'    i=3, ch='n' (1e-9)
          left='100', right=''          nothing after the letter
          right is empty, so digits = left = '100'
          value = float('100') * 1e-9 = 100.0 * 1e-9

'2M2'     i=1, ch='M' (1e6)
          left='2', right='2'
          digits = '2.2'
          value = 2.2 * 1e6 = 2200000.0

'0.1'     no prefix letter anywhere
          value = float('0.1') = 0.1

'4,7k'    i=3, ch='k' (1e3)
          left='4,7', right=''
          digits = '4,7'
          float('4,7')  ->  ValueError
```

The empty-`right` case is what makes `3.3k`, `470R` and `100n` work: when the letter
comes last there is nothing to join, the digits in front of it are already the whole
number, and inserting a point would give `'100.'` — which `float` happens to accept
as 100.0, so the bug would not even show here, only on a field like `4k` becoming
`4.` and still, by luck, meaning four. Handle it deliberately rather than relying on
that.

The `100n` line hides something worth knowing. `100.0 * 1e-9` does not produce the
float nearest to $10^{-7}$; it produces the one next to it. Print it and you get
`1.0000000000000001e-07` rather than `1e-07`. The two differ by about
$1.3\times10^{-23}$, which is one unit in the last place and about a hundredth of a
part per quadrillion of the value — utterly irrelevant to any capacitor, and a
guaranteed failure of `parse_eng("100n") == 1e-7`. That is module 1's rule arriving
in a new costume: compare with a tolerance, never with `==`.

## The mistakes people actually make

**Swallowing the exception.** The most expensive line in this module is

```python
try:
    value = parse_eng(field)
except ValueError:
    continue          # skip anything we cannot read
```

It is tempting because it is defensive, and because on a good file it never fires. On
the day a supplier sends a file written in a country where the decimal separator is a
comma, *every* line fails, every failure is skipped, and the program reports an empty
circuit as though empty were the answer. A loud problem has been converted into a
silent one. Letting the exception out names the offending text and the reason, and
costs a minute; hunting a silently empty dataset costs a morning.

**Reading `4k7` as 47 kΩ.** The digits are right, the exponent is not, and the
result is a number that looks entirely reasonable. This is the signature of every
units bug: the mantissa survives and the power of ten does not. The defence is a
sanity check against something you already know — a few volts across a few kilohms is
a few milliamps; an amp is not.

**Upper-casing, lower-casing, or otherwise tidying the field before parsing it.**
`field.upper()` is a reflex from handling names, and here it turns milli into mega.
Case is data in this notation, not formatting.

**Counting fields from one.** `line.split()` gives four pieces numbered 0 to 3, so
the value is `f[3]` and the second node is `f[2]`. Off by one, and the program still
runs: it just uses a node name where a value was meant, or the reference where a node
was meant, and the circuit that comes out is a different circuit that nothing
complains about.

## Where this stops holding

The scanner above is deliberately small, and it is worth knowing its edges before you
trust it with a file you did not write.

**It takes the first prefix letter it meets and asks no further questions.** `4k7k`
parses happily as `float('4.7k')` — which raises, so that one is safe — but `1M0M`
gives `float('0M')`, which also raises. The failures are loud here by luck rather
than by design. A parser that must not be fooled should check that what is left after
removing the one prefix letter is entirely digits and at most one point.

**A comma is a decimal point in most of the world.** You cannot fix this by replacing
`","` with `"."`, because in the other half of the world the comma is the *thousands*
separator and `4,700` means 4700, not 4.7. The two conventions are not
distinguishable from the text alone: `1,234` is genuinely ambiguous. The fix is to
know where the file came from, not to guess from its contents.

**`float` accepts more than you may want.** `float("1e3")` is 1000.0, `float("inf")`
is infinity, `float("nan")` is a value that is not equal to itself, and
`float("1_000")` is 1000.0 because Python allows underscores in numeric text. Every
one of those is a legal float and none of them is a resistor. If the field must be a
positive finite resistance, check that after converting it, not before.

**Bytes are not characters.** The `µ` of microfarads is one character but two bytes
in UTF-8 and a different byte again in the older encodings a 1990s CAD package
writes. Read a latin-1 file as UTF-8 and it raises; read a UTF-8 file as latin-1 and
`µ` silently becomes two junk characters, neither of which is in the prefix table.
And a file exported from a spreadsheet often begins with an invisible byte-order
mark, the character `\ufeff`, which glues itself to the front of the first field.
The reference then prints as `V1`, compares unequal to `"V1"`, and is three
characters long rather than two — so the kind, taken as its leading character, is the
invisible mark rather than `V`, and nothing matches. When a parser fails on exactly
one line and that line is the first, this is very often why.

The next reading takes the field parser as done and asks the larger question: what a
whole file says, what it deliberately does not say, and how a run of lines becomes a
circuit.
''',
                },
                {
                    "title": "A file is lines, a line is a record",
                    "minutes": 16,
                    "body": r'''
The person who drew the schematic and the program that simulates it never meet. What
passes between them is a file, and whatever is not in that file is lost. So the file
has to be enough — enough to rebuild the circuit exactly, with no picture, no notes
and nobody to ask.

That constraint is what gives a **netlist** its shape. One component to a line, and
on each line: what the component is called, which two points it joins, and what its
value is. Nothing else. Every circuit simulator ever written reads one, and the
format has barely changed since 1971, because there is not much to change.

```text
* loaded-divider.net
V1  in   0    DC 9

R1  in   mid  4k7
# the load, fitted later
R2  mid  0    2k2
R3  mid  0    3k3
```

## What the file says, and what it leaves you to work out

Read the component lines as a table:

```
ref   first node   second node   value
------------------------------------------
V1    in           0             9 V supply
R1    in           mid           4700 ohm
R2    mid          0             2200 ohm
R3    mid          0             3300 ohm
```

A **node** is a name, and that is genuinely all it is. `in`, `mid` and `0` are three
labels; two pins are electrically the same point if and only if they carry the same
label. `0` is ground by a convention as old as the format, and every other name is
arbitrary — rename `mid` to `q7` throughout and the circuit is unchanged.

Now notice what the file does **not** say. It does not say that R2 and R3 are in
parallel. It says that R2 runs between `mid` and `0`, and that R3 runs between `mid`
and `0`, and *being in parallel is a consequence of that* — a fact about the pair
that has to be worked out by whatever reads the file. It does not say which node is
the output, or that R1 and the pair form a divider, or that anything is a divider at
all. It lists parts and connections. Every structural word an engineer would use —
series, parallel, divider, load — is an interpretation laid on top.

This is exactly why the format has survived. Interpretations go out of date; a list
of what is joined to what does not.

## Worked example 1: six lines of text to 1.97 volts

Take the file at face value and work out the voltage at `mid`.

R2 and R3 share both their endpoints, so the same voltage stands across each of them
and their currents add. Conductances add for that arrangement:

```
    1/Rp = 1/2200 + 1/3300
         = 4.5455e-4 + 3.0303e-4
         = 7.5758e-4  siemens
    Rp   = 1 / 7.5758e-4
         = 1320.0 ohm
```

or by the two-resistor shortcut, which is the same statement rearranged:

```
    Rp = (2200 x 3300) / (2200 + 3300)
       = 7 260 000 / 5500
       = 1320.0 ohm
```

R1 then carries every bit of the current that the pair carries between them, so those
two resistances are in series and add:

```
    Rtotal = 4700 + 1320 = 6020 ohm
    I      = 9 / 6020 = 1.4950e-3 A = 1.495 mA
```

and `mid` sits at whatever that current makes across the lower 1320 Ω:

```
    V_mid = 1.4950e-3 x 1320 = 1.9734 V
```

Check it the other way, as a ratio, which avoids the current entirely:

```
    V_mid = 9 x 1320 / 6020 = 11880 / 6020 = 1.9734 V
```

and check the loop closes: R1 drops $1.4950\times10^{-3} \times 4700 = 7.0266$ V, and
$7.0266 + 1.9734 = 9.0000$ V, which is the supply. Every joule handed to a coulomb
comes back before it gets home.

The two branch currents, for later: $1.9734/2200 = 0.8970$ mA through R2 and
$1.9734/3300 = 0.5980$ mA through R3, and $0.8970 + 0.5980 = 1.4950$ mA, which is
what came down through R1. Nothing accumulates at `mid`.

Every one of those numbers came out of four lines of text and no picture at all. That
is the claim the format makes, and it holds.

## The loop, and the three guards in front of it

Reading the file is a loop over lines with three tests before any interpretation
happens:

```python
for line in text.splitlines():
    line = line.strip()
    if not line:                    # guard 1: blank
        continue
    if line[0] in "*#":             # guard 2: comment
        continue
    f = line.split()                # guard 3 is the shape of f
    ...
```

`splitlines()` cuts on line endings and throws them away, and — unlike
`split("\n")` — it copes with a file written on Windows, where each line ends `\r\n`,
without leaving a stray `\r` glued to the last field. That stray would make the final
value field `'2k2\r'`, and while `strip()` on the whole line removes it, a program
that splits before it strips will not.

Trace the guards over the file, line by line:

```
line  text                          strip -> what happens
-----------------------------------------------------------------------
 1    "* loaded-divider.net"        comment, starts '*'   -> skipped
 2    "V1  in   0    DC 9"          5 fields              -> record
 3    ""                            empty                 -> skipped
 4    "R1  in   mid  4k7"           4 fields              -> record
 5    "# the load, fitted later"    comment, starts '#'   -> skipped
 6    "R2  mid  0    2k2"           4 fields              -> record
 7    "R3  mid  0    3k3"           4 fields              -> record

                                    7 lines in, 4 records out
```

Note the order of the first two guards. `if line[0] in "*#"` on an empty line raises
`IndexError: string index out of range`, so the blank test has to come first — or the
comment test has to be written `line.startswith(("*", "#"))`, which is safe on an
empty string. Either is fine; the crash from getting it wrong is at least loud.

Note also *why* the comment line matters beyond being noise. `"# the load, fitted
later"` splits into five fields, so a parser that skips only blank lines survives the
`len(f)` test and then reaches for the value: `f[3]` is `'fitted'`, and `parse_eng`
hands `'fitted'` to `float`, which raises. The header line `"* loaded-divider.net"`
splits into two fields and dies on `f[3]` with an `IndexError` instead. The two bad
lines fail in two different ways, which is a fair picture of what unguarded parsing
feels like.

A record is then a dictionary standing for one component, in the shape module 3
called a record:

```python
{"ref": "R1", "kind": "R", "nodes": ("in", "mid"), "value": 4700.0}
```

`kind` is `ref[0]`, the leading letter, which is the convention the format uses to
say what a part is: `R` resistor, `C` capacitor, `L` inductor, `V` voltage source.
`nodes` is a **tuple** rather than a list, because a component has exactly two ends
and that number is not going to change while the program runs.

One wrinkle: the field count is not constant. `V1  in  0  DC 9` has five fields,
because the source states a type before its value. So the value is `f[4]` on a source
line and `f[3]` on a component line, and something has to decide which:

```python
value = float(f[4]) if f[3] == "DC" else parse_eng(f[3])
```

This is the smallest honest version. A real reader would branch on `kind` and would
know that `DC`, `AC`, `SIN` and `PULSE` each take a different number of arguments
after them.

## Worked example 2: the file the supplier sent

Now the same file, exported by different software:

```text
V1;in;0;DC 9
R1;in;mid;4,7k
R2;mid;0;2,2k
R3;mid;0;3,3k
```

Semicolons for separators, commas for decimal points. Run the reader above on it and
follow what happens under each of two error policies.

**Policy A — let it raise.** `line.split()` finds no whitespace, so `f` is a
one-element list holding the whole line, and `f[3]` raises `IndexError` on the very
first component line. You get a traceback, a line number, and ten minutes of work.

**Policy B — wrap each line in `try` and skip what fails.** Every line fails, every
failure is skipped, and `read_netlist` returns `[]`. No exception, no message, no
output that looks wrong. The simulator is then handed an empty circuit and reports
whatever an empty circuit reports — very often 0.000 V, printed to three decimal
places with all the authority of a real measurement.

Policy B is worse, and it is worse in the way that matters: it is wrong *quietly*.
The instinct behind it is sound — a program should not fall over on one bad line —
but the correct expression of that instinct counts and reports what it skipped:

```
read 4 lines, 4 unreadable, 0 records: first failure on line 2, 'R1;in;mid;4,7k'
```

Now consider the nastier version of the same failure. Suppose only R3's line is
malformed and the other three parse. Policy B returns three records — a circuit
missing one resistor — and the simulation runs perfectly:

```
    with R3:      Rp = 1320 ohm,  V_mid = 9 x 1320 / 6020 = 1.973 V
    without R3:   the divider is 4700 over 2200
                  V_mid = 9 x 2200 / 6900 = 2.870 V
```

2.870 V is not an obviously silly number. It is 45% high, it is the right order of
magnitude, it is between 0 and the supply, and there is nothing about it to catch the
eye. A program that returns a plausible wrong number is more dangerous than one that
crashes, because a crash gets fixed on the day it happens.

## The mistakes people actually make

**Trusting the first line.** Almost every exported file has a header, and almost
every header is not a component. Parsers that work on a hand-typed test file and fail
on the real export usually fail here.

**Splitting on a fixed number of spaces.** The file above is aligned into columns,
and it is tempting to read the value as `line[20:26]`. That works until someone opens
the file, adds a component with a four-character reference, and lets the editor
re-align it. Split on whitespace and the alignment stops being load-bearing.

**Skipping quietly.** Covered above, and worth repeating because the tempting
spelling is one line shorter than the correct one.

**Assuming the field count.** `f[4]` on a four-field line is an `IndexError`, and
`f[3]` on a five-field source line is the string `'DC'`. The first is loud; the second
is a `ValueError` from `float`, one step later and one step further from the cause.

**Comparing node names loosely.** `"MID"`, `"mid"` and `" mid"` are three different
strings and therefore three different nodes. Two of those nodes will have exactly one
component attached, and a node with one component attached carries no current — so
the simulation runs, and one resistor in your circuit has quietly become a dead end.

## Where this stops holding

The reader in this module handles a file of the shape given above and no more.

**Real SPICE netlists are considerably larger than this.** A line beginning `+` is a
continuation of the one before it. A line beginning `.` is a command rather than a
component: `.model`, `.tran`, `.subckt`. Subcircuits nest, so node names have scope
and the same name means different points in different blocks. Semicolons start
comments in some dialects and separate fields in others. None of that is hard; all of
it is more code.

**Separator-delimited data needs the `csv` module, not `split`.** As soon as a field
can itself contain the separator — a part description with a comma in it — splitting
is wrong, because the correct answer depends on quoting rules that `split` knows
nothing about. Do not write that parser; import one.

**A file that does not fit in memory has to be read a line at a time.**
`text.splitlines()` builds a list of every line at once, which is fine for a netlist
of forty components and not fine for a two-gigabyte logic-analyser capture. Iterating
over the open file object — `for line in open(path):` — reads one line at a time and
keeps the rest on disk.

**Records are not a circuit yet.** What comes out of this module is a list of
dictionaries: text turned into structured data, and no more. Nobody has worked out
which pins share a node, built the conductance matrix, or solved anything. That is
the work of the capstone, and it starts from exactly the records this reading has
described — which is the point of getting them right.
''',
                },
            ],
            "quiz": {
                "title": "Reading what the file actually said",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A netlist line reads `R1 in mid 4k7`. What resistance is that?",
                        "opts": ["4.7 \u03a9", "47 \u03a9", "4700 \u03a9", "4.7 M\u03a9"],
                        "a": 2,
                        "why": (
                            "4700 \u03a9, or 4.7 k\u03a9. The letter stands where the decimal point would go, "
                            "so `4k7` is 4.7 thousand: the digits before the letter are whole units of the "
                            "prefix and the digits after are the fraction. The notation exists because a "
                            "printed dot can be lost to a bad photocopy or a speck of dust, and losing it "
                            "moves the value by a factor of ten. A letter cannot fall off."
                        ),
                    },
                    {
                        "q": "What does `float(\"100n\")` do?",
                        "opts": [
                            "Gives 1e-07",
                            "Gives 100.0",
                            "Raises a ValueError",
                            "Gives 0.0",
                        ],
                        "a": 2,
                        "why": (
                            "It raises a ValueError, because `float` implements the syntax of a number and "
                            "`100n` is not one. This is the right behaviour and worth being glad about: the "
                            "alternative, a function that quietly returns 100.0 having ignored the letter, "
                            "would put every capacitance in the design out by a factor of a billion with "
                            "nothing on screen to say so."
                        ),
                    },
                    {
                        "q": "What does `\" 12 , 3 \".split(\",\")` give?",
                        "opts": [
                            "`['12', '3']`",
                            "`[' 12 ', ' 3 ']`",
                            "`['12,3']`",
                            "`[' 12 ', ',', ' 3 ']`",
                        ],
                        "a": 1,
                        "why": (
                            "`[' 12 ', ' 3 ']` \u2014 splitting on a comma cuts at the comma and keeps "
                            "everything else, spaces included. The separator itself is thrown away but the "
                            "padding is not, which is why `float(part.strip())` is the usual pairing. Note "
                            "that `\"a b\".split()` with no argument behaves differently again: it cuts on "
                            "runs of whitespace and discards them, which is what you want for a netlist line."
                        ),
                    },
                    {
                        "q": "`line = \"R1 in mid 4k7\"`. What is `line.split()[2]`?",
                        "opts": ["`'R1'`", "`'in'`", "`'mid'`", "`'4k7'`"],
                        "a": 2,
                        "why": (
                            "`'mid'`. Splitting gives four fields \u2014 reference, first node, second node, "
                            "value \u2014 and they are numbered from 0, so field 2 is the third one. Counting "
                            "from 1 here is the single most common parsing bug, and it is quiet: the program "
                            "runs, and one node name is used where another was meant."
                        ),
                    },
                    {
                        "q": "`s = \"  4k7 \\n\"`. After `s.strip()`, what is `s`?",
                        "opts": [
                            "`'4k7'`",
                            "`'  4k7 \\n'`, unchanged",
                            "`''`",
                            "It raises, because strings cannot be modified",
                        ],
                        "a": 1,
                        "why": (
                            "`s` is unchanged. Strings are immutable, so `strip` cannot alter one \u2014 it "
                            "returns a new string and leaves the original alone. To keep the trimmed version "
                            "you have to catch it: `s = s.strip()`. Calling `s.strip()` and ignoring the "
                            "result is a line that looks like it did something and did not, which is the "
                            "same shape of mistake as `xs.sort()` returning `None`."
                        ),
                    },
                    {
                        "q": "Your parser wraps each line in a `try` and skips any line it cannot read. A supplier sends a file where every value is written `4,7k` with a comma. What do you see?",
                        "opts": [
                            "A ValueError naming the first bad line",
                            "An empty result and no error at all",
                            "Every value multiplied by ten",
                            "The file read correctly \u2014 a comma is a decimal point in most of the world",
                        ],
                        "a": 1,
                        "why": (
                            "Nothing comes back and nothing complains. Every line fails, every failure is "
                            "swallowed, and the program reports an empty circuit as though that were the "
                            "answer. A parser that skips what it cannot read converts a loud problem into a "
                            "silent one; letting the exception out names the offending line and the reason, "
                            "and takes a minute to fix rather than a morning to find."
                        ),
                    },
                ],
            },
            "blanks": [
                {
                    "title": "Where the prefix letter goes",
                    "minutes": 9,
                    "lang": "python",
                    "caption": "eng.py — five holes, and three printed values that must come out exactly as shown",
                    "brief": r'''
This is the whole of engineering notation, in nine lines. Every hole is a decision
about *where the letter sits* or *what it is worth*, and each wrong choice below is
one somebody has actually shipped.

Nothing runs here. The three `print` lines state what the finished function must
produce, so every choice can be settled against them rather than guessed at.
''',
                    "listing": r'''
# "4k7" -> 4700.0. The letter stands where the decimal point would go.
MULT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": ___,
        "R": 1.0,   "k": 1e3,  "M": ___}


def parse_eng(text):
    text = text.strip()
    for i, ch in ___(text):
        if ch in MULT:
            left, right = text[:i], text[i + ___:]
            digits = left + "." + right if right else ___
            return float(digits) * MULT[ch]
    return float(text)


print(parse_eng("4k7"))      # 4700.0
print(parse_eng("3.3k"))     # 3300.0
print(parse_eng("2M2"))      # 2200000.0
''',
                    "blanks": [
                        {
                            "prompt": "Lower-case `m` is milli.",
                            "hole": "multiplier",
                            "opts": ["1e-3", "1e-6", "1e3", "1e6"],
                            "a": 0,
                            "why": "Milli is a thousandth, $10^{-3}$. It sits one step below the plain unit, between micro at $10^{-6}$ and kilo at $10^{3}$, and the whole table walks in steps of a thousand.",
                            "whys": [
                                "Milli is a thousandth, $10^{-3}$. It sits one step below the plain unit, between micro at $10^{-6}$ and kilo at $10^{3}$, and the whole table walks in steps of a thousand.",
                                "$10^{-6}$ is micro, which already has its own row in the table under the letter `u`. Two letters mapping to the same multiplier means one of them is wrong, and every current written in milliamps would come out a thousand times too small.",
                                "$10^{3}$ is kilo, and it is the *upper* case that would be wrong here rather than the lower. `1m` would then be 1000 instead of 0.001, an error of a million in the ratio.",
                                "$10^{6}$ is mega, which is what upper-case `M` means on the line below. Making `m` mean it too is the exact confusion the table exists to prevent, and it is worth a factor of a billion.",
                            ],
                        },
                        {
                            "prompt": "Upper-case `M` is mega.",
                            "hole": "multiplier",
                            "opts": ["1e6", "1e-3", "1e9", "1e-6"],
                            "a": 0,
                            "why": "Mega is a million, $10^{6}$, so `2M2` is 2.2 MΩ. Case is *data* in this notation: `m` and `M` are one letter apart and $10^{9}$ apart, which is why a parser must never tidy the field's case before looking it up.",
                            "whys": [
                                "Mega is a million, $10^{6}$, so `2M2` is 2.2 MΩ. Case is *data* in this notation: `m` and `M` are one letter apart and $10^{9}$ apart, which is why a parser must never tidy the field's case before looking it up.",
                                "$10^{-3}$ is milli, the lower-case `m` above. Giving both cases the same value makes `2M2` come out as 0.0022 Ω — a value low enough to be a short circuit, from a field that says two megohms.",
                                "$10^{9}$ is giga, written `G`, and it is not in this table at all. Resistors and capacitors rarely need it; frequencies do, which is why a signal-processing parser carries a longer table than this one.",
                                "$10^{-6}$ is micro. This would make `2M2` mean 2.2 µΩ, and it would do it silently, since nothing in the field itself says which way round the two cases go.",
                            ],
                        },
                        {
                            "prompt": "The scan needs both the position and the character at that position.",
                            "hole": "builtin",
                            "opts": ["enumerate", "range", "reversed", "len"],
                            "a": 0,
                            "why": "`enumerate(text)` yields `(0, '4')`, `(1, 'k')`, `(2, '7')` — the index and the character together, which is exactly what the two slices below need. Without the index there is nothing to slice around.",
                            "whys": [
                                "`enumerate(text)` yields `(0, '4')`, `(1, 'k')`, `(2, '7')` — the index and the character together, which is exactly what the two slices below need. Without the index there is nothing to slice around.",
                                "`range(text)` raises a TypeError: `range` counts integers and cannot be handed a string. Even `range(len(text))` — which does work — gives positions only, so `ch` would be a number and `ch in MULT` would never be true.",
                                "`reversed(text)` walks the characters from the end, and hands over characters rather than pairs, so the unpacking into `i, ch` fails immediately. Scanning backwards would also find the wrong letter first in a field carrying two of them.",
                                "`len(text)` is a single integer, and a `for` loop cannot walk an integer — this is a TypeError before anything else can go wrong.",
                            ],
                        },
                        {
                            "prompt": "Everything after the letter, not including the letter itself.",
                            "hole": "offset",
                            "opts": ["1", "0", "2", "i"],
                            "a": 0,
                            "why": "Position `i` holds the prefix letter, so the fraction starts at `i + 1`. On `\"4k7\"` that gives `right = '7'` and `digits = '4.7'`, which is the 4700.0 printed at the bottom.",
                            "whys": [
                                "Position `i` holds the prefix letter, so the fraction starts at `i + 1`. On `\"4k7\"` that gives `right = '7'` and `digits = '4.7'`, which is the 4700.0 printed at the bottom.",
                                "`text[i:]` keeps the letter, so `right` is `'k7'` and `digits` is `'4.k7'` — which `float` refuses with a ValueError. Loud, at least, and on every single field.",
                                "`text[i + 2:]` skips the letter *and* the first digit of the fraction. On `\"4k7\"` the fraction is one character long, so `right` comes out empty, `digits` becomes `'4'`, and the answer is 4000.0 — a plausible resistor value that is nowhere in the file.",
                                "`text[i + i:]` happens to be right when `i` is 1, which it is for `\"4k7\"`, and wrong for everything else: on `\"470R\"` the letter is at position 3, so this slices from position 6 and loses the fraction entirely.",
                            ],
                        },
                        {
                            "prompt": "When the letter comes last there is no fraction to join on, and the digits in front of it are already the whole number.",
                            "hole": "expr",
                            "opts": ["left", "text", "right", "\"0\""],
                            "a": 0,
                            "why": "With nothing after the letter, `left` is the entire number: `\"3.3k\"` gives `left = '3.3'`, and $3.3 \\times 10^{3} = 3300.0$ as printed. This is the branch that makes `470R`, `100n` and `3.3k` work at all.",
                            "whys": [
                                "With nothing after the letter, `left` is the entire number: `\"3.3k\"` gives `left = '3.3'`, and $3.3 \\times 10^{3} = 3300.0$ as printed. This is the branch that makes `470R`, `100n` and `3.3k` work at all.",
                                "`text` is the field with the letter still in it, so `float('3.3k')` raises a ValueError. The letter has to come out somewhere, and this branch is the only place left to do it.",
                                "`right` is empty — that is the condition that got us into this branch — and `float('')` raises a ValueError. Every trailing-prefix field in the file would fail.",
                                "`\"0\"` converts without complaint and returns $0 \\times 10^{3} = 0.0$ for every trailing-prefix field. A zero-ohm resistor is a short circuit, and the simulation that comes back will be confidently, silently wrong.",
                            ],
                        },
                    ],
                },
                {
                    "title": "Six lines in, three records out",
                    "minutes": 9,
                    "lang": "python",
                    "caption": "read.py — five holes; the three printed lines fix every one of them",
                    "brief": r'''
The field parser is done; this is the loop around it. Three of the holes are the
guards that stand between a line of text and any attempt to interpret it, and two are
the indices that pull a record out of a line once it has survived them.

Count the lines in `NET` before you start: there are six, and only three of them
describe a component.
''',
                    "listing": r'''
from eng import parse_eng            # "4k7" -> 4700.0, from the listing above

NET = ("* divider.net\n"
       "V1 in 0 DC 9\n"
       "\n"
       "R1 in mid 4k7\n"
       "# the load\n"
       "R2 mid 0 2k2\n")

out = []
for line in NET.___():
    line = line.___()
    if not line or line[0] in "*#":
        ___
    f = line.split()
    value = float(f[4]) if f[3] == "DC" else parse_eng(f[3])
    out.append({"ref": f[0], "kind": f[0][___],
                "nodes": (f[1], f[___]), "value": value})

print(len(out))                      # 3
print(out[1]["nodes"])               # ('in', 'mid')
print(out[2]["value"])               # 2200.0
''',
                    "blanks": [
                        {
                            "prompt": "Cut the whole file into its lines, without leaving the line endings attached.",
                            "hole": "method",
                            "opts": ["splitlines", "split", "strip", "readlines"],
                            "a": 0,
                            "why": "`splitlines()` cuts on line endings and discards them, and it recognises `\\r\\n` as one ending rather than two characters — so a file written on Windows does not leave a stray `\\r` glued to the last field of every line.",
                            "whys": [
                                "`splitlines()` cuts on line endings and discards them, and it recognises `\\r\\n` as one ending rather than two characters — so a file written on Windows does not leave a stray `\\r` glued to the last field of every line.",
                                "`split()` with no argument cuts on *every* run of whitespace, so the entire file becomes one flat list of words with no idea where one line ended and the next began. The loop would then walk words, and `line[0] in \"*#\"` would test single characters.",
                                "`strip()` returns one string with its ends tidied, not a list. Looping over a string walks it one character at a time, so `line` would be `'*'`, then `' '`, then `'d'`, and nothing after that makes sense.",
                                "`readlines()` is a method of an open file object, not of a string. `NET` is text already in memory, so this is an AttributeError.",
                            ],
                        },
                        {
                            "prompt": "Tidy both ends of the line before anything looks at either of them.",
                            "hole": "method",
                            "opts": ["strip", "rstrip", "lower", "title"],
                            "a": 0,
                            "why": "`strip()` clears whitespace from both ends. The leading end matters as much as the trailing one: a comment indented by a single space fails the `line[0] in \"*#\"` test, and a line that is only spaces is not caught by `not line` until it has been stripped.",
                            "whys": [
                                "`strip()` clears whitespace from both ends. The leading end matters as much as the trailing one: a comment indented by a single space fails the `line[0] in \"*#\"` test, and a line that is only spaces is not caught by `not line` until it has been stripped.",
                                "`rstrip()` clears the trailing end only, which handles line endings and nothing else. An indented comment then survives both guards, splits into four fields, and `parse_eng` is handed the word `load`.",
                                "`lower()` case-folds the line, which is destructive here: `2M2` becomes `2m2`, and mega becomes milli. That is a factor of $10^{9}$ applied by a line that was meant to be tidying.",
                                "`title()` capitalises the first letter of every word, so `in` becomes `In` and `mid` becomes `Mid`. Node names are compared as strings, so this quietly renames every node in the circuit.",
                            ],
                        },
                        {
                            "prompt": "A blank or a comment is not an error — go and get the next line.",
                            "hole": "statement",
                            "opts": ["continue", "pass", "break", "return"],
                            "a": 0,
                            "why": "`continue` abandons this pass and starts the next one, which is what skipping a line means. It is the only choice here that leaves the loop running and the line unread.",
                            "whys": [
                                "`continue` abandons this pass and starts the next one, which is what skipping a line means. It is the only choice here that leaves the loop running and the line unread.",
                                "`pass` does nothing at all — it is a placeholder that keeps an indented block syntactically legal — so control falls straight through to `line.split()`. The header splits into two fields and `f[3]` raises an IndexError; the comment splits into three and does the same.",
                                "`break` leaves the loop entirely at the first comment, which is the header on line 1. `out` comes back empty, no exception is raised, and the program reports a circuit with nothing in it.",
                                "`return` ends the enclosing function, and at module level there is no enclosing function, so this is a SyntaxError. Inside `read_netlist` it would be a subtler version of the same fault as leaving the loop early.",
                            ],
                        },
                        {
                            "prompt": "What kind of part it is, taken from the reference: `R1` is a resistor, `V1` a source.",
                            "hole": "index",
                            "opts": ["0", "1", "-1", "2"],
                            "a": 0,
                            "why": "The kind is the leading character of the reference, so `f[0][0]` is `'R'` for `R1` and `'V'` for `V1`. That single letter is the whole of what the netlist format says about what a component *is*.",
                            "whys": [
                                "The kind is the leading character of the reference, so `f[0][0]` is `'R'` for `R1` and `'V'` for `V1`. That single letter is the whole of what the netlist format says about what a component *is*.",
                                "Position 1 is the number, not the letter: `f[0][1]` is `'1'` for both `R1` and `V1`, so every part in the circuit would come out the same kind, and that kind would be a digit.",
                                "`f[0][-1]` is the last character, which is the same `'1'` here and would differ on a two-digit reference like `R12`, where it gives `'2'`. Right answer by accident on short references, wrong on long ones — the worst kind of index.",
                                "`f[0][2]` is past the end of a two-character reference, so this raises an IndexError on the first record it reaches.",
                            ],
                        },
                        {
                            "prompt": "The second of the two nodes the component joins.",
                            "hole": "index",
                            "opts": ["2", "1", "3", "0"],
                            "a": 0,
                            "why": "The fields are numbered from zero — reference, first node, second node, value — so the second node is `f[2]`. For `R1 in mid 4k7` that pair is `('in', 'mid')`, which is what the middle `print` demands.",
                            "whys": [
                                "The fields are numbered from zero — reference, first node, second node, value — so the second node is `f[2]`. For `R1 in mid 4k7` that pair is `('in', 'mid')`, which is what the middle `print` demands.",
                                "`f[1]` is the *first* node, so the pair would be `('in', 'in')` and every component would have both ends on the same point. A resistor wired that way carries no current and the circuit falls apart quietly.",
                                "`f[3]` is the value field, so `R1` would be recorded as joining `in` to `4k7` — a node named after a resistance. Nothing raises: node names are just strings, and this one is a perfectly good string.",
                                "`f[0]` is the reference, so the pair would be `('in', 'R1')` and every component would sit on a private node named after itself. Each part is then a dead end and the simulator sees no complete loop anywhere.",
                            ],
                        },
                    ],
                },
            ],
            "build": {
                "title": "Draw the circuit this netlist describes",
                "minutes": 25,
                "brief": r'''
Here is a file, exactly as a schematic exporter wrote it. Nothing else about the
circuit exists — no picture, no notes.

```text
* loaded-divider.net
V1  in   0    DC 9

R1  in   mid  4k7
# the load, fitted later
R2  mid  0    2k2
R3  mid  0    3k3
```

Read it and draw it. Each component line gives a **reference**, the **two nodes** it
joins, and its **value**; node `0` is ground, and every other name is just a name.
Lines beginning with `*` or `#` are comments.

Put a **probe** on the node called `mid`.

The checks measure the circuit you drew rather than compare it to a picture, so any
layout is fine. What they will not forgive is a value read wrongly: `4k7` is 4.7 kΩ,
and `2k2` and `3k3` are 2.2 kΩ and 3.3 kΩ. The supply is a plain 9.

Notice that nothing in the file says R2 and R3 are in parallel. It says they both
run between `mid` and `0`, and being in parallel is a consequence of that, worked
out by whatever reads the file.

**Drawing it.** Pick a part from the palette and click to place it. Drag from one pin
to another to wire them. A wire and a pin are connected when they land on the same
grid point, and on nothing less.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p4", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                        {"id": "p5", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 2200},
                        {"id": "p6", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 3300},
                        {"id": "p7", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 4], "b": [13, 4]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [13, 7], "b": [13, 9]},
                    ],
                },
                "checks": [
                    {"name": "the supply is the 9 V the file asked for", "code": r'''
c.assert(c.count("V") === 1,
  "the file lists one source, V1, so the canvas should hold exactly one");
c.close(c.values("V")[0], 9, 0.001, "the supply voltage");
'''},
                    {"name": "three resistors, at the three values written in the file", "code": r'''
var rs = c.values("R").slice().sort(function (a, b) { return a - b; });
c.assert(rs.length === 3,
  "the file lists R1, R2 and R3; this circuit has " + rs.length + " resistor(s)");
var want = [2200, 3300, 4700];
for (var i = 0; i < 3; i++) {
  c.close(rs[i], want[i], 0.01,
    "one of the resistors: the file says 4k7, 2k2 and 3k3, which are " +
    "4.7 kOhm, 2.2 kOhm and 3.3 kOhm");
}
'''},
                    {"name": "the probe is on mid, and mid sits where the values put it", "code": r'''
c.close(c.vout(), 1.9734, 0.01,
  "the voltage at mid — 2k2 beside 3k3 is 1.32 kOhm, and 9 V across 4k7 above that " +
  "1.32 kOhm leaves 1.97 V at the joint");
'''},
                    {"name": "the supply delivers what that network draws", "code": r'''
var src = c.net.parts.filter(function (p) { return p.kind === "V"; })[0];
c.assert(src, "there is no voltage source for the current to come from");
var i = Math.abs(c.dc().currents[src.id]);
c.close(i, 1.495e-3, 0.02,
  "the supply current: 9 V across 4.7 kOhm + 1.32 kOhm is 1.495 mA. Anything below " +
  "about 1.4 mA means only one of the two lower resistors actually reached the mid node");
'''},
                ],
                "hints": [
                    "Three nodes appear in the file: `in`, `mid` and `0`. Draw them as three places on the canvas and the wiring follows — R1 bridges `in` to `mid`, and both R2 and R3 run from `mid` down to ground.",
                    "R2 and R3 have the same pair of node names, so their top pins must end up on the same electrical point. Two vertical resistors hanging off one horizontal wire is the easiest way to draw that.",
                    "The probe marks the node the checks read. It belongs on the wire joining R1, R2 and R3 — probing `in` reads 9 V and the check will say so.",
                    "If a check reports a resistance that is out by a factor of ten or a thousand, re-read the value field: the letter sits where the decimal point goes, so `4k7` is 4.7 k and not 47 k.",
                ],
            },
            "numeric": [{
                "title": "What current does this line of the file draw?",
                "minutes": 7,
                "brief": r'''
One component, one supply, and the only difficulty in the whole question is reading
the value the way the file wrote it.

```text
V1  in  0  DC 5
R1  in  0  4k7
```

Ohm's law gives the current as the voltage across the part divided by its
resistance. Answer in **milliamps**.
''',
                "prompt": "How much current does the supply deliver?",
                "note": "Two decimal places is plenty. The trap is the value, not the arithmetic.",
                "diagram": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 5},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                        {"id": "r1", "kind": "R", "x": 11, "y": 7, "rot": 1, "value": 4700},
                        {"id": "g1", "kind": "GND", "x": 11, "y": 10},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 4]},
                        {"a": [3, 4], "b": [11, 4]},
                        {"a": [11, 4], "b": [11, 6]},
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [11, 8], "b": [11, 10]},
                    ],
                },
                # The prompt asks for the current the supply delivers, so the check
                # reads exactly that: the branch current the solver carries for the
                # source itself, converted to milliamps. Nothing here repeats 4700 or
                # 5, so redrawing the schematic with a different resistor moves this
                # number and the gate says so.
                "check": r'''
var src = c.net.parts.filter(function (p) { return p.kind === "V"; })[0];
c.assert(src, "the schematic has no supply for the current to come from");
return Math.abs(c.dc().currents[src.id]) * 1000;
''',
                "given": [
                    {"label": "Supply, as written", "value": "DC 5"},
                    {"label": "R1, as written", "value": "4k7"},
                    {"label": "Answer wanted in", "value": "mA"},
                ],
                "aside": "The whole circuit is one resistor across one source, so the current through "
                         "the resistor and the current out of the supply are the same number.",
                "answer": 1.0638,
                "tol": 0.02,
                "unit": "mA",
                "hint": "Convert the value first and write it down in ohms before dividing. `4k7` is "
                        "4.7 k\u03a9. Then $I = V/R$, and a result in amps becomes milliamps by "
                        "multiplying by a thousand.",
                "wrong": "Check the resistance you used. Reading `4k7` as 4.7 \u03a9 gives about 1.06 A "
                         "and reading it as 47 k\u03a9 gives about 0.106 mA \u2014 both look like "
                         "plausible answers, which is exactly why this is worth getting right.",
                "why": "$5 / 4700 = 1.064\\times10^{-3}$ A, or 1.06 mA. Notice how forgiving the digits "
                       "are and how unforgiving the exponent is: every wrong reading of `4k7` gives an "
                       "answer with the same three digits in it and a different power of ten. That is "
                       "the characteristic signature of a units bug, and it is why a result should "
                       "always be sanity-checked against something you know \u2014 a few milliamps "
                       "through a few kilohms from a few volts is ordinary; an amp is not.",
            }, {
                "title": "Three values, three notations, one total",
                "minutes": 6,
                "brief": r'''
Three resistors, one after the other, and the file writes each value in a different
style. Nothing here is in parallel and nothing splits: whatever current leaves the
supply goes through all three parts in turn, so the three resistances add.

```text
V1  in  0    DC 10

R1  in  a    4k7
R2  a   b    3.3k
R3  b   0    470R
```

Convert all three into ohms before you add anything. The three notations are the
whole difficulty; the arithmetic afterwards is one sum.
''',
                "prompt": "What resistance does the supply see?",
                "note": "Answer in kilohms, to two decimal places.",
                "diagram": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                        {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                        {"id": "r2", "kind": "R", "x": 10, "y": 4, "rot": 0, "value": 3300},
                        {"id": "r3", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 470},
                        {"id": "g1", "kind": "GND", "x": 13, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [11, 4], "b": [13, 4]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [13, 7], "b": [13, 9]},
                    ],
                },
                # Nothing here restates 8470. The check asks the solver what current the
                # supply delivers and divides the supply's own voltage by it, so a
                # resistor redrawn at another value moves this number and the gate says so.
                "check": r'''
var src = c.net.parts.filter(function (p) { return p.kind === "V"; })[0];
c.assert(src, "the schematic has no supply");
return src.value / Math.abs(c.dc().currents[src.id]) / 1000;
''',
                "given": [
                    {"label": "R1, as written", "value": "4k7"},
                    {"label": "R2, as written", "value": "3.3k"},
                    {"label": "R3, as written", "value": "470R"},
                    {"label": "Answer wanted in", "value": "kΩ"},
                ],
                "aside": "All three notations are legal and all three appear in real files. `4k7` puts "
                         "the letter where the point goes, `3.3k` writes the point out and puts the "
                         "letter last, and `470R` uses `R` as the prefix meaning no prefix at all.",
                "answer": 8.47,
                "tol": 0.02,
                "unit": "kΩ",
                "hint": "Write all three in ohms first: 4700, 3300, 470. Series resistances add, and "
                        "a total in ohms becomes kilohms by dividing by a thousand.",
                "wrong": "If you got 478, `470R` was read as 470 kΩ — `R` is the prefix that "
                         "means no prefix at all. If you got 50.77, `4k7` went in as 47 kΩ. And if "
                         "you got 0.378, the three were combined as though they were in parallel, "
                         "which is the rule for the other arrangement and always gives a total "
                         "below the smallest part rather than above the largest.",
                "why": r'''
```
    4k7   ->  4700 ohm
    3.3k  ->  3300 ohm
    470R  ->   470 ohm
              ------
              8470 ohm  =  8.47 kohm
```

The supply therefore delivers $10/8470 = 1.181$ mA, and that same current passes
through every one of the three parts, because there is nowhere along the loop for any
of it to go anywhere else. That is what "in series" means, and it is a statement
about the *drawing* rather than about the values: three parts are in series when each
node between them joins exactly two pins.

Worth noticing which resistor dominates. The 470 Ω contributes 5.5% of the total, so
replacing it with a 390 Ω moves the supply current by about 1%. In a series chain the
largest resistance decides almost everything and the smallest is nearly furniture —
which is exactly backwards from a parallel group, where the smallest resistance
carries most of the current and the largest is the one that barely matters.
''',
            }, {
                "title": "Where the file puts the middle node",
                "minutes": 8,
                "brief": r'''
Now a file with three components and a node that two of them share.

```text
V1  in   0    DC 12

R1  in   mid  2k2
R2  mid  0    4k7
R3  mid  0    10k
```

Nothing in the file says R2 and R3 are in parallel. It says both of them run between
`mid` and `0`, and being in parallel is what that *means* — a consequence you work
out, not a fact the file states.

The probe is on `mid`.
''',
                "prompt": "What voltage does the file put on the node called `mid`?",
                "note": "Volts, to three decimal places.",
                "diagram": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                        {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 2200},
                        {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4700},
                        {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                        {"id": "r3", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 10000},
                        {"id": "g2", "kind": "GND", "x": 13, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 4], "b": [13, 4]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [13, 7], "b": [13, 9]},
                    ],
                },
                "check": r'''
return c.vout();
''',
                "given": [
                    {"label": "Supply", "value": "12 V"},
                    {"label": "R1, in to mid", "value": "2k2"},
                    {"label": "R2, mid to 0", "value": "4k7"},
                    {"label": "R3, mid to 0", "value": "10k"},
                ],
                "aside": "Two resistors that share both of their node names have the same voltage "
                         "across them, so their currents add and their conductances add. Reduce the "
                         "pair to one number and what is left is an ordinary two-resistor divider.",
                "answer": 7.1086,
                "tol": 0.02,
                "unit": "V",
                "hint": "Combine R2 and R3 first: $R_p = R_2R_3/(R_2+R_3)$. Then `mid` takes the "
                        "supply in the ratio $R_p/(R_1+R_p)$.",
                "wrong": "If you got 8.17, R3 was left out and the divider treated as 2k2 over 4k7 "
                         "alone. If you got 9.84, R2 was the one left out. If you got 4.89, the two "
                         "halves of the divider have been swapped — the ratio uses the resistance "
                         "below the tap, not the resistance above it. And if you got 10.44, R2 and "
                         "R3 were added rather than combined in parallel: adding is the series "
                         "rule, and two parts sharing both their nodes are not in series.",
                "why": r'''
```
    R2 || R3 = (4700 x 10000) / (4700 + 10000)
             = 47 000 000 / 14 700
             = 3197.28 ohm

    Rtotal   = 2200 + 3197.28  =  5397.28 ohm
    I        = 12 / 5397.28    =  2.2233 mA
    V_mid    = 2.2233e-3 x 3197.28  =  7.1086 V
```

or in one step as a ratio, which is the same statement with the current cancelled out:
$12 \times 3197.28/5397.28 = 7.1086$ V.

Check it closes. R1 drops $12 - 7.1086 = 4.8914$ V, and
$4.8914/2200 = 2.2233$ mA — the supply current, as it must be, since R1 carries all
of it. Below the tap, R2 takes $7.1086/4700 = 1.5125$ mA and R3 takes
$7.1086/10000 = 0.7109$ mA, and $1.5125 + 0.7109 = 2.2234$ mA, which is the same
number to the rounding. Nothing piles up at `mid`.

The parallel result is worth a second look: 4.7 kΩ beside 10 kΩ gives 3.20 kΩ, which
is *below the smaller of the two*. That is always true and it is the sanity check to
carry — adding a second path can only make it easier for current to get through, so
the combination is always smaller than either part alone, and never more than a
factor of two below the smaller one.
''',
            }, {
                "title": "The voltage across a part the file never names",
                "minutes": 9,
                "brief": r'''
A file with four resistors and two internal nodes. One branch off the middle node is
a single resistor to ground; the other is two resistors in series.

```text
V1  in  0   DC 12

R1  in  a   2k2
R2  a   0   4k7
R3  a   b   3k3
R4  b   0   1k
```

The question asks for something the netlist has no field for. A file gives node
names; a component's voltage is the *difference* between the two nodes it joins, and
you have to solve the circuit to know either of them.
''',
                "prompt": "What voltage stands across R3, the 3k3?",
                "note": "Volts, to three decimal places. The sign is not wanted, only the size.",
                "diagram": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                        {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 2200},
                        {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4700},
                        {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                        {"id": "r3", "kind": "R", "x": 11, "y": 4, "rot": 0, "value": 3300},
                        {"id": "r4", "kind": "R", "x": 14, "y": 6, "rot": 1, "value": 1000},
                        {"id": "g2", "kind": "GND", "x": 14, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [10, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [12, 4], "b": [14, 4]},
                        {"a": [14, 4], "b": [14, 5]},
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [14, 7], "b": [14, 9]},
                    ],
                },
                # The prompt names R3, so the check measures R3: the difference between the
                # two node voltages the solver put on its own pins. Neither 3300 nor any
                # node voltage is restated here.
                "check": r'''
var d = c.dc();
var r = c.net.parts.filter(function (p) { return p.id === "r3"; })[0];
c.assert(r, "R3 is not on the schematic");
return Math.abs(d.v[r.n1] - d.v[r.n2]);
''',
                "given": [
                    {"label": "Supply", "value": "12 V"},
                    {"label": "R1, in to a", "value": "2k2"},
                    {"label": "R2, a to 0", "value": "4k7"},
                    {"label": "R3, a to b", "value": "3k3"},
                    {"label": "R4, b to 0", "value": "1k"},
                ],
                "aside": "R3 and R4 are in series with each other and that pair is in parallel with "
                         "R2. Reduce from the far end inwards — the two that add first, then the "
                         "parallel pair, then R1 — and the supply current falls out.",
                "answer": 4.6518,
                "tol": 0.02,
                "unit": "V",
                "hint": "Find the voltage at `a` first. Then the R3-R4 branch is a divider of its "
                        "own, hanging off that voltage, and R3 takes the share $R_3/(R_3+R_4)$ of it.",
                "wrong": "If you got 6.06, that is the voltage at `a` — the whole of what the "
                         "branch gets, before R4 takes its share. If you got 1.41, that is R4's "
                         "share rather than R3's. If you got 6.09, R2 was left out of the "
                         "reduction: the R3–R4 branch is not the only load hanging on R1, and "
                         "leaving R2 out raises every voltage below it.",
                "why": r'''
```
    R3 + R4       = 3300 + 1000            = 4300 ohm     (series: same current)
    that || R2    = (4300 x 4700) / 9000   = 2245.56 ohm
    Rtotal        = 2200 + 2245.56         = 4445.56 ohm

    V_a           = 12 x 2245.56 / 4445.56 = 6.0615 V
    I in R3,R4    = 6.0615 / 4300          = 1.4096 mA
    V across R3   = 1.4096e-3 x 3300       = 4.6518 V
```

The last two lines can be collapsed into one: the branch is itself a divider, so R3
takes $6.0615 \times 3300/4300 = 4.6518$ V of it directly, and R4 takes the other
$6.0615 \times 1000/4300 = 1.4096$ V. The two shares add back to 6.0615 V, which is
the whole of what the branch was given.

Check the currents at node `a`. R1 delivers $(12 - 6.0615)/2200 = 2.6993$ mA; R2
takes $6.0615/4700 = 1.2897$ mA and the R3–R4 branch takes 1.4096 mA, and
$1.2897 + 1.4096 = 2.6993$ mA. Whatever arrives, leaves.

Notice what had to happen before any of that. The netlist gave four resistances and
four node names — `in`, `a`, `b` and `0` — and nothing at all about the arrangement. "R3 and R4 are in series" is a
deduction from the fact that node `b` appears on exactly two component lines and on
nothing else — a node with only two pins on it has no third path, so both parts carry
the same current. That test, *count the pins on each node*, is what a program does to
recognise a series pair, and it is the only thing that makes the phrase mean anything.
''',
            }, {
                "title": "Two sources, and the resistor between them",
                "minutes": 11,
                "brief": r'''
The file now has two supply lines, and the obvious one is not the only one.

```text
V1  in   0    DC 9
V2  ref  0    DC 3

R1  in   mid  4k7
R2  mid  ref  2k2
R3  mid  0    3k3
```

R2 does not go to ground. It goes to `ref`, which another source is holding at 3 V,
so neither end of R2 is at a voltage you know before you start. Nothing here reduces
by series and parallel: the two supplies are pushing against each other through the
network, and no pair of resistors shares both of its node names.

The way in is the node itself. `mid` has exactly one unknown voltage on it, and the
currents arriving there from the three resistors must add to nothing, because a node
is a junction of wires and stores no charge. That single statement determines it.
''',
                "prompt": "What current flows in R2, the 2k2 between `mid` and `ref`?",
                "note": "Answer in microamps, to the nearest microamp. The size, not the sign.",
                "diagram": {
                    "parts": [
                        {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                        {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                        {"id": "r3", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3300},
                        {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                        {"id": "r2", "kind": "R", "x": 11, "y": 4, "rot": 0, "value": 2200},
                        {"id": "v2", "kind": "V", "x": 14, "y": 6, "rot": 1, "value": 3},
                        {"id": "g2", "kind": "GND", "x": 14, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [10, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [12, 4], "b": [14, 4]},
                        {"a": [14, 4], "b": [14, 5]},
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [14, 7], "b": [14, 9]},
                    ],
                },
                # R2's own drop and its own value, both taken out of the solve. The 3 V of
                # V2 is never restated: change it on the schematic and this number moves.
                "check": r'''
var d = c.dc();
var r = c.net.parts.filter(function (p) { return p.id === "r2"; })[0];
c.assert(r, "R2 is not on the schematic");
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1e6;
''',
                "given": [
                    {"label": "V1, on node in", "value": "9 V"},
                    {"label": "V2, on node ref", "value": "3 V"},
                    {"label": "R1, in to mid", "value": "4k7"},
                    {"label": "R2, mid to ref", "value": "2k2"},
                    {"label": "R3, mid to 0", "value": "3k3"},
                ],
                "aside": "Call the unknown voltage at `mid` $V_m$. Each resistor carries a current "
                         "set by the difference between $V_m$ and whatever is at its far end. Add the "
                         "three, set the sum to zero, and one equation gives you $V_m$.",
                "answer": 172.15,
                "tol": 0.5,
                "unit": "µA",
                "hint": "Write the three currents *arriving* at `mid`: $(9-V_m)/4700$, "
                        "$(3-V_m)/2200$ and $(0-V_m)/3300$. Their sum is zero. Gather the $V_m$ "
                        "terms on one side and divide.",
                "wrong": "If you got 1364, the whole 3 V was put across R2, which is what stands "
                         "across it only if `mid` happens to sit at 0. If you got 1196, that is the "
                         "current in R1, and if you got 1024 it is the current in R3 — both real "
                         "currents in this circuit, and neither the one asked for. If you got "
                         "0.172, the answer is right in milliamps: $1.72\\times10^{-4}$ A is 172 "
                         "µA.",
                "why": r'''
Let $V_m$ be the voltage at `mid`. The three currents arriving there add to zero:

$$\frac{9 - V_m}{4700} + \frac{3 - V_m}{2200} + \frac{0 - V_m}{3300} = 0$$

Gather. The terms with no $V_m$ in them are the current the sources push in:

```
    I = 9/4700 + 3/2200
      = 1.91489e-3 + 1.36364e-3
      = 3.27853e-3 A
```

and the coefficient of $V_m$ is the total conductance tied to the node:

```
    G = 1/4700 + 1/2200 + 1/3300
      = 2.12766e-4 + 4.54545e-4 + 3.03030e-4
      = 9.70342e-4 S
```

so $V_m = I/G = 3.27853\times10^{-3} / 9.70342\times10^{-4} = 3.3787$ V, and

```
    I(R2) = (3.3787 - 3) / 2200
          = 0.3787 / 2200
          = 1.7215e-4 A
          = 172.15 uA
```

flowing from `mid` towards `ref` — out of the node, because `mid` sits above the 3 V
that V2 is holding.

Check the node. R1 brings in $(9 - 3.3787)/4700 = 1196.0$ µA; R3 takes
$3.3787/3300 = 1023.9$ µA away to ground and R2 takes 172.2 µA away to `ref`, and
$1023.9 + 172.2 = 1196.1$ µA. The books balance to the rounding.

Two things this circuit shows that the earlier ones could not. **The 3 V source is
absorbing current, not delivering it.** 172 µA is flowing *into* its positive
terminal, which for a battery means charging and for a bench supply usually means
complaining. A netlist happily describes a circuit that no series-parallel reduction
can touch and that does something the word "supply" does not cover.

**And there is no reduction to be found.** R2 and R3 both touch `mid`, but their far
ends are different nodes, so they are not in parallel; R1 and R2 both touch `mid`,
but so does R3, so they are not in series either. What replaces the reduction is the
node equation — one unknown, one statement of conservation — and unlike the
reduction it never fails to apply. That is why every simulator is built on it, and
why the derivation in this module is about that equation rather than about the divider.
''',
            }],
            "derive": {
                "title": "What one unknown node solves to",
                "minutes": 14,
                "vars": ["V_m", "V_1", "V_2", "R_1", "R_2", "R_3", "G", "I"],
                "brief": r'''
The last numeric was solved by writing one equation and turning a handle. This is
that handle, done once with symbols so it never has to be improvised again — and it
is very nearly the whole of what a circuit simulator does.

The circuit is the one from the file: a node called `mid`, at an unknown voltage
$V_m$, tied to three places. $R_1$ joins it to a node held at $V_1$, $R_2$ joins it
to a node held at $V_2$, and $R_3$ joins it to ground, which is held at zero. Write
each answer as an expression in the symbols named, with no numbers in it.
''',
                "steps": [
                    {
                        "prompt": "Start with one branch. $R_1$ runs from a node held at $V_1$ to the node `mid`, which sits at $V_m$. Write the current *arriving at* `mid` along that resistor.",
                        "answer": "\\frac{V_1 - V_m}{R_1}",
                        "hint": "Ohm's law on $R_1$. The voltage across it is the difference between its two ends, and writing that difference as far-end minus near-end makes the result positive when current flows towards `mid`.",
                        "deconstruct": [
                            "The current in any resistor is the voltage across it divided by its resistance.",
                            "The voltage across $R_1$ is $V_1 - V_m$ if you take it in the direction of travel, from the far end to `mid`.",
                            "So the current arriving is $(V_1 - V_m)/R_1$, and it comes out negative on its own if $V_m$ happens to be the higher of the two.",
                        ],
                    },
                    {
                        "prompt": "Now all three. $R_2$ joins `mid` to a node held at $V_2$, and $R_3$ joins it to ground, which is a node held at zero volts. Write the total current arriving at `mid` — the expression that KCL sets equal to zero.",
                        "answer": "\\frac{V_1 - V_m}{R_1} + \\frac{V_2 - V_m}{R_2} - \\frac{V_m}{R_3}",
                        "placeholder": "a sum of three terms",
                        "hint": "Each branch contributes a term of the same shape as the first: far end minus $V_m$, over its own resistance. Ground's far end is 0.",
                        "deconstruct": [
                            "$R_2$ contributes $(V_2 - V_m)/R_2$, by exactly the argument used for $R_1$.",
                            "$R_3$ contributes $(0 - V_m)/R_3$, which is $-V_m/R_3$.",
                            "A node stores no charge, so what arrives must leave: the three terms add to zero.",
                        ],
                    },
                    {
                        "prompt": "Multiply that out and separate it into two parts. Each resistor ties the node to somewhere through its own *conductance*, $1/R$. Write $G$, the sum of the three conductances — the coefficient that multiplies $V_m$.",
                        "answer": "\\frac{1}{R_1} + \\frac{1}{R_2} + \\frac{1}{R_3}",
                        "hint": "Every one of the three terms contains a $-V_m$ divided by that branch's resistance, and nothing else does.",
                        "deconstruct": [
                            "Expanding: $V_1/R_1 - V_m/R_1 + V_2/R_2 - V_m/R_2 - V_m/R_3$.",
                            "The three terms carrying $V_m$ are $-V_m(1/R_1 + 1/R_2 + 1/R_3)$.",
                            "So $G = 1/R_1 + 1/R_2 + 1/R_3$, and it depends on the resistors alone — no source appears in it.",
                        ],
                    },
                    {
                        "prompt": "Write $I$, the other part: the total current the sources push into the node, which is everything left after the $V_m$ terms are taken out.",
                        "answer": "\\frac{V_1}{R_1} + \\frac{V_2}{R_2}",
                        "hint": "Two of the three branches end on a source. The third ends on ground, and contributes $0/R_3$.",
                        "deconstruct": [
                            "From the expansion, the terms without $V_m$ are $V_1/R_1$ and $V_2/R_2$.",
                            "$R_3$'s far end is at zero volts, so its contribution to this half is $0/R_3 = 0$.",
                            "$I$ is what would flow into the node if it were held at zero volts — which is the short-circuit current, and worth remembering under that name.",
                        ],
                    },
                    {
                        "prompt": "The whole of KCL at the node is now $I - G V_m = 0$. Write $V_m$ in terms of $I$ and $G$.",
                        "answer": "\\frac{I}{G}",
                        "placeholder": "a ratio of the two",
                        "hint": "One rearrangement and one division. This is Ohm's law for a whole node rather than for one resistor.",
                    },
                    {
                        "prompt": "Substitute both halves back and clear the fractions inside. Write $V_m$ as a single fraction in $V_1$, $V_2$, $R_1$, $R_2$ and $R_3$, with no fraction inside it.",
                        "answer": "\\frac{V_1 R_2 R_3 + V_2 R_1 R_3}{R_1 R_2 + R_1 R_3 + R_2 R_3}",
                        "placeholder": "\\frac{...}{...}",
                        "hint": "Multiply the top and the bottom of $I/G$ by $R_1R_2R_3$ and every inner fraction disappears at once.",
                        "deconstruct": [
                            "Top: $\\left(\\frac{V_1}{R_1} + \\frac{V_2}{R_2}\\right)R_1R_2R_3 = V_1R_2R_3 + V_2R_1R_3$.",
                            "Bottom: $\\left(\\frac{1}{R_1} + \\frac{1}{R_2} + \\frac{1}{R_3}\\right)R_1R_2R_3 = R_2R_3 + R_1R_3 + R_1R_2$.",
                            "The bottom is symmetric in all three resistors, and the top is not — it weights each source by the product of the *other* two resistances, so the branch with the smallest resistance has the loudest voice.",
                        ],
                    },
                    {
                        "prompt": "Finally, the quantity the last numeric asked for. $R_2$ runs from `mid` to the node held at $V_2$. Write the current in it, counted positive when it flows out of `mid`, in terms of $V_m$, $V_2$ and $R_2$.",
                        "answer": "\\frac{V_m - V_2}{R_2}",
                        "hint": "The same Ohm's law as the first step, with the subtraction the other way round because the current is now being counted in the other direction.",
                        "deconstruct": [
                            "The voltage across $R_2$ is the difference between its ends, whichever way you take it.",
                            "Taking it as $V_m - V_2$ makes the current positive when `mid` is the higher of the two, which is what 'flowing out of `mid`' means.",
                            "It is the negative of the term written in the second step, and it has to be: that one counted the same current arriving.",
                        ],
                    },
                ],
                "closing": r'''
Put the numeric's file through it. $V_1 = 9$, $V_2 = 3$, $R_1 = 4700$, $R_2 = 2200$,
$R_3 = 3300$:

```text
    top     9 x 2200 x 3300  +  3 x 4700 x 3300
          = 65 340 000       +  46 530 000        = 111 870 000

    bottom  4700x2200 + 4700x3300 + 2200x3300
          = 10 340 000 + 15 510 000 + 7 260 000   =  33 110 000

    V_m   = 111 870 000 / 33 110 000              = 3.3787 V
    I(R2) = (3.3787 - 3) / 2200                   = 172.15 uA
```

Now set $V_2 = 0$, which is what the build's file describes — R2 running to ground
rather than to a second supply:

```text
    V_m = 9 x 2200 x 3300 / 33 110 000 = 65 340 000 / 33 110 000 = 1.9734 V
```

which is the number the build's checks measure. The loaded divider is not a separate
result. It is this one with a source set to zero, and that is worth more than the
saving in algebra: it says that a resistor to ground and a resistor to a supply are
*the same kind of thing* to the node, differing only in the number at the far end.

Three things to carry out of this.

**The formula is the node, not the circuit.** Nothing in the derivation asked what
the components were arranged into. There was no reduction, no "these two are in
parallel", no picture. There was a node, a list of what is tied to it, and a
conservation law. That is precisely the shape of a netlist record — a component, its
two ends, its value — which is why a program can go from text to answer without ever
forming a mental image of the circuit.

**It generalises by adding terms, not by getting cleverer.** Ten resistors on the
node give ten terms in $G$ and ten in $I$, and the answer is still $I/G$. In code
that is one loop over the records:

```python
G = 0.0
I = 0.0
for rec in net:
    if rec["kind"] == "R" and "mid" in rec["nodes"]:
        far = rec["nodes"][0] if rec["nodes"][1] == "mid" else rec["nodes"][1]
        G += 1.0 / rec["value"]
        I += voltage_at(far) / rec["value"]
v_mid = I / G
```

**Where it stops.** Every step assumed the far end of each resistor was a voltage you
already knew. With two unknown nodes there are two equations, each mentioning the
other's unknown, and no amount of rearranging one of them alone will do it — you need
both at once, which means a matrix. The capstone builds that matrix from a list of
records exactly like the ones this module produces, and the second-hardest thing
about it is reading the file.
''',
            },
            "lab": {
                "title": "A netlist reader",
                "runtime": "python",
                "minutes": 35,
                "brief": r'''
Turn the file from the build into records your code can use. Three functions, and
the first one is where all the care goes.

`parse_eng(text)` returns the number a value field stands for. A prefix letter — one
of `p n u m R k M` — may appear anywhere in the field, and it stands where the
decimal point goes:

```text
4k7   -> 4700.0        470R -> 470.0
3.3k  -> 3300.0        100n -> 1e-07
2M2   -> 2200000.0     0.1  -> 0.1
```

So `4k7` splits into `4` before the letter and `7` after, joins back up as `4.7`,
and is multiplied by 1000. When the letter comes last there is nothing to join: the
digits in front of it are already the number, so `3.3k`, `470R` and `100n` are read
as they stand and then multiplied. A field with no letter at all is just a number.
Anything that is not a number at all must raise — leave that to `float`, which
already does it properly.

`read_netlist(text)` returns a list of records, one per component line, skipping
blank lines and any line starting with `*` or `#`. Each record is a dictionary with

* `"ref"` — the reference, such as `"R1"`
* `"kind"` — its first character, `"R"`
* `"nodes"` — a **tuple** of the two node names
* `"value"` — a float

Source lines carry an extra field: `V1 in 0 DC 9` has `DC` where a component has its
value, and the number after it. Component lines have four fields, source lines five.

`nodes(net)` returns every node name that appears anywhere in the netlist, sorted and
without repeats.
''',
                "files": [{"name": "main.py", "content": r'''
NET = """
* loaded-divider.net
V1  in   0    DC 9

R1  in   mid  4k7
# the load, fitted later
R2  mid  0    2k2
R3  mid  0    3k3
"""

MULT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
        "R": 1.0, "k": 1e3, "M": 1e6}


def parse_eng(text):
    """The number a netlist value field stands for. 4k7 -> 4700.0"""
    text = text.strip()
    # TODO: find the prefix letter, split around it, rejoin with a '.' between the
    # halves, and multiply. With no letter, hand the whole thing to float.
    return 0.0


def read_netlist(text):
    """One record per component line: ref, kind, nodes tuple, value."""
    out = []
    # TODO: strip each line, skip blanks and lines starting with '*' or '#',
    # split on whitespace, and build the record.
    return out


def nodes(net):
    """Every node name in the netlist, sorted, no repeats."""
    # TODO
    return []


if __name__ == "__main__":
    for field in ("4k7", "100n", "2M2", "470R", "3.3k", "0.1"):
        print(field, "->", parse_eng(field))
    net = read_netlist(NET)
    for rec in net:
        print(rec)
    print("nodes:", nodes(net))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
NET = """
* loaded-divider.net
V1  in   0    DC 9

R1  in   mid  4k7
# the load, fitted later
R2  mid  0    2k2
R3  mid  0    3k3
"""

MULT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
        "R": 1.0, "k": 1e3, "M": 1e6}


def parse_eng(text):
    """The number a netlist value field stands for. 4k7 -> 4700.0"""
    text = text.strip()
    for i, ch in enumerate(text):
        if ch in MULT:
            left = text[:i]
            right = text[i + 1:]
            digits = left + "." + right if right else left
            return float(digits) * MULT[ch]
    return float(text)


def read_netlist(text):
    """One record per component line: ref, kind, nodes tuple, value."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line[0] in "*#":
            continue
        f = line.split()
        value = float(f[4]) if f[3] == "DC" else parse_eng(f[3])
        out.append({"ref": f[0], "kind": f[0][0],
                    "nodes": (f[1], f[2]), "value": value})
    return out


def nodes(net):
    """Every node name in the netlist, sorted, no repeats."""
    seen = set()
    for rec in net:
        seen.update(rec["nodes"])
    return sorted(seen)


if __name__ == "__main__":
    for field in ("4k7", "100n", "2M2", "470R", "3.3k", "0.1"):
        print(field, "->", parse_eng(field))
    net = read_netlist(NET)
    for rec in net:
        print(rec)
    print("nodes:", nodes(net))
'''}],
                "hints": [
                    "`for i, ch in enumerate(text):` gives you the position and the character together, which is what you need to slice the field into the part before the letter and the part after it.",
                    "`text[:i]` is everything before position `i` and `text[i + 1:]` everything after it. When the second half is empty the letter was a suffix, so the first half is already the whole number and nothing needs joining.",
                    "Do not try to catch a bad field. `float(\"fred\")` raises a ValueError that names the offending text, and that message is far more useful than anything you would write in its place.",
                    "`line[0] in \"*#\"` tests the first character against both comment markers at once. Strip the line first, or a comment indented by one space is not recognised as one.",
                ],
                "tests": [
                    {"name": "the letter stands where the decimal point goes", "code": r'''
assert abs(parse_eng("4k7") - 4700.0) < 1e-9, f"4k7 is 4.7 kOhm; got {parse_eng('4k7')}"
assert abs(parse_eng("2M2") - 2.2e6) < 1e-3, f"2M2 is 2.2 MOhm; got {parse_eng('2M2')}"
assert abs(parse_eng("470R") - 470.0) < 1e-9, \
    f"470R is 470 ohms - R is the prefix meaning no prefix; got {parse_eng('470R')}"
assert abs(parse_eng("100n") - 1e-7) < 1e-15, f"100n is 100 nF; got {parse_eng('100n')}"
'''},
                    {"name": "a trailing letter and a plain number both work", "code": r'''
assert abs(parse_eng("3.3k") - 3300.0) < 1e-9, f"got {parse_eng('3.3k')}"
assert abs(parse_eng("0.1") - 0.1) < 1e-12, "a field with no prefix is just a number"
assert abs(parse_eng("  22u  ") - 2.2e-5) < 1e-12, "surrounding spaces must not matter"
assert abs(parse_eng("1m") - 1e-3) < 1e-12, "lower-case m is milli"
assert abs(parse_eng("1M") - 1e6) < 1e-6, \
    "upper-case M is mega, a factor of a billion away from milli"
'''},
                    {"name": "a field that is not a number raises", "code": r'''
_raised = False
try:
    parse_eng("fred")
except ValueError:
    _raised = True
assert _raised, \
    "an unreadable value must raise a ValueError, not come back as 0.0 - a zero-ohm " \
    "resistor is a short circuit and the simulation will not tell you where it came from"
'''},
                    {"name": "comments, the star line and the blank line are skipped", "code": r'''
_n = read_netlist(NET)
assert len(_n) == 4, \
    (f"the file holds four components and three non-component lines; got {len(_n)} record(s). "
     "If you got 7 the comment lines are being parsed")
assert [r["ref"] for r in _n] == ["V1", "R1", "R2", "R3"], \
    f"expected V1, R1, R2, R3 in file order; got {[r['ref'] for r in _n]}"
'''},
                    {"name": "each record carries the right four fields", "code": r'''
_n = read_netlist(NET)
_r1 = _n[1]
assert _r1["kind"] == "R", f"the kind is the first character of the reference; got {_r1['kind']!r}"
assert _r1["nodes"] == ("in", "mid"), f"expected ('in', 'mid'); got {_r1['nodes']!r}"
assert isinstance(_r1["nodes"], tuple), \
    f"nodes must be a tuple, not a {type(_r1['nodes']).__name__} - the pair is fixed once drawn"
assert abs(_r1["value"] - 4700.0) < 1e-9, f"R1 is 4k7; got {_r1['value']}"
assert abs(_n[2]["value"] - 2200.0) < 1e-9, f"R2 is 2k2; got {_n[2]['value']}"
assert abs(_n[3]["value"] - 3300.0) < 1e-9, f"R3 is 3k3; got {_n[3]['value']}"
'''},
                    {"name": "a source line has its value one field further along", "code": r'''
_v = read_netlist(NET)[0]
assert _v["kind"] == "V", f"got {_v['kind']!r}"
assert _v["nodes"] == ("in", "0"), f"got {_v['nodes']!r}"
assert abs(_v["value"] - 9.0) < 1e-12, \
    f"V1 is 9 V, written after the DC keyword; got {_v['value']}"
'''},
                    {"name": "the node list is every name, once, in order", "code": r'''
_n = read_netlist(NET)
assert nodes(_n) == ["0", "in", "mid"], \
    (f"three distinct nodes appear in the file; got {nodes(_n)}. Ground is called 0 and "
     "sorts before the letters")
assert nodes([]) == [], "an empty netlist has no nodes"
'''},
                ],
            },
        },

        # ---- M5 -----------------------------------------------------------
        {
            "title": "Arrays as signals",
            "summary": "A measurement is not one number, it is thousands. NumPy lets you hold the whole run in one name and work on all of it at once.",
            "concepts": [
                "A NumPy array holds many numbers of the same type in one object, and arithmetic on it applies to every element: `2 * a` doubles all of them.",
                "The same expression on a plain Python list means something else entirely — `2 * [1, 2]` gives `[1, 2, 1, 2]`. The type decides the meaning.",
                "`np.arange(start, stop, step)` counts by a step and stops before `stop`; `np.linspace(start, stop, n)` gives exactly `n` values including both ends.",
                "Sampling: measuring a continuous signal every `1/fs` seconds. `fs` is the sample rate, and `n` samples cover `n / fs` seconds.",
                "Indexing counts from 0, and `a[-1]` is the last element. A slice `a[10:20]` runs from index 10 up to but not including 20.",
                "Summaries of a signal: mean (the DC level), RMS (`sqrt(mean(v**2))`, which is what a true-RMS meter reads), and peak (`max(abs(v))`).",
                "Aliasing: sampled at `fs`, a signal above `fs/2` is indistinguishable from a lower one. The information is gone at the converter and no later processing recovers it.",
            ],
            "read": [
                {
                    "title": "A recording is a list of moments",
                    "minutes": 16,
                    "body": r'''
A bench meter reads 4.87 V, you write 4.87 in a notebook, and the notebook is the
right place for it. Now put a scope probe on the same node while the regulator is
switching. What is there is not a number. It is a voltage that has a different value
at every instant, and the only honest way to write it down is to say what it was at a
great many instants and to admit that nothing at all was recorded in between.

That object — many numbers, in order, with a rule saying when each was taken — is a
**recording**. Everything in this module is about holding one inside a program and
asking questions of it.

## A list will hold it, and will not let you work with it

Module 3 put engineering data in lists, and a list will certainly hold ten thousand
voltages. The trouble starts the moment you want to do arithmetic to all of them.
Suppose the probe has a 10:1 divider in its tip, so every reading is a tenth of the
real voltage and the whole run needs multiplying by ten:

```python
v = [0.487, 0.491, 0.488, 0.502]
real = 10 * v            # not what you want
```

`10 * v` on a list means *repeat the list ten times*. You asked for a recording ten
times as tall and got one ten times as long; nothing raised an error, and `len(real)`
comes back as a perfectly plausible 40. The correction is a loop:

```python
real = []
for x in v:
    real.append(10 * x)
```

which is right, and which you will write again for the offset, again for the
squaring, again for every step of every calculation. Three lines of bookkeeping per
line of arithmetic is not a syntax annoyance. It is a thinking problem: the loop is
about *elements*, and the thing you actually have an opinion about is the *signal*.

## What an array is

A NumPy array is a run of numbers, all of one type, laid end to end in one block of
memory, under one name:

```python
import numpy as np
v = np.array([0.487, 0.491, 0.488, 0.502])
```

Two consequences follow from "all of one type, laid end to end", and they are the
whole reason the type exists.

The first is that arithmetic can be defined on the array as a whole. `10 * v` scales
every element, `v - 0.5` shifts every element, `v * v` multiplies element by element
against a partner of the same length. The loop has not gone away — NumPy is running
one, in C, inside the multiplication — but it has stopped being something you write
and something you can get wrong.

The second is that the same symbol now means two different things depending on what
is to the left of it. `2 * a` repeats a list and scales an array. Nothing in the line
tells you which; only the type does. This is why a signal belongs in an array from
the moment it is created, and why the conversion belongs at the boundary — as the
file is read — rather than three functions later, where half the code has already
been written under the wrong assumption.

## The time axis is not in the array

An array of 12 000 voltages does not know when any of them was taken. What makes it a
recording rather than a bag of numbers is one extra fact kept alongside it: the
**sample rate** `fs`, in samples per second. From that single number everything about
timing follows.

- Sample `i` was taken at $t_i = i / f_s$, counting the first sample as $i = 0$.
- $n$ samples cover $n / f_s$ seconds of the world.
- The last sample sits at $(n - 1) / f_s$, not at $n / f_s$.

That last line is a fencepost, and it is worth staring at. Twelve samples at 8 kHz
occupy eleven gaps of 125 µs each, so the last one is at 1.375 ms even though the
recording is said to be 1.5 ms long. Both statements are true. The duration counts
intervals; the timestamp counts steps taken from zero.

NumPy gives you two ways to build the axis and they fail in opposite directions.
`np.arange(start, stop, step)` counts by a step and stops *before* `stop`;
`np.linspace(start, stop, n)` gives exactly `n` values including both ends and works
out its own step. For a time axis, the step is the thing you know and the endpoint is
the thing you do not, so:

```python
t = np.arange(v.size) / FS          # right: index over the samples, then scale
t = np.linspace(0, v.size / FS, v.size)   # wrong: quietly changes the sample rate
```

The second line looks harmless and is not. Asking for 24 values from 0 to 3 ms
inclusive gives a step of $3\,\text{ms}/23 = 130.4$ µs, when the converter was
running at 125 µs. Every timestamp after the first is wrong, by more as you go, and
nothing about the array's shape reveals it.

## Worked example: three milliseconds at 8 kHz

A logger runs at $f_s = 8$ kHz and captures 3 ms.

```text
    sample interval   1 / 8000            = 125 us
    samples in 3 ms   0.003 * 8000        = 24 samples
    indices           0, 1, 2, ... 23
    t of sample 0     0 / 8000            = 0 us
    t of sample 1     1 / 8000            = 125 us
    t of sample 23    23 / 8000           = 2875 us = 2.875 ms
    duration          24 / 8000           = 3.000 ms
```

`np.arange(0, 3e-3, 1/8000)` produces exactly those 24 values and stops, because
3 ms is a stop value it never reaches. That is the behaviour you want here and the
behaviour that catches people out elsewhere: with a step that does not divide the
span evenly, floating-point rounding decides whether the final value squeaks in or
not, and `arange` can return $n$ or $n+1$ elements for what looks like the same
request. When the count matters more than the step, `linspace` is the honest tool.

## Slices are windows in time

Indexing counts from zero and `v[-1]` is the last element, counted backwards, which
is the spelling to reach for because it stays right when the recording changes
length. A slice `v[a:b]` runs from index `a` up to but *not including* `b`, so it
holds `b - a` elements — the same half-open convention that makes `arange` stop
early, and for the same reason: adjacent slices then meet exactly once, with no
element shared and none missed.

To turn a window in seconds into a window in indices, multiply by the rate. The event
between 20 ms and 50 ms of an 8 kHz recording is:

```text
    i0 = 0.020 * 8000 = 160
    i1 = 0.050 * 8000 = 400
    window = v[160:400]      ->  240 samples  =  30 ms
```

and 240 samples at 8 kHz is 30 ms, which is the 50 minus the 20. A step in the slice
throws samples away: `v[::4]` keeps every fourth one and hands back a recording at a
quarter of the rate. That is a real operation with a real consequence, and the next
reading unit is about what the consequence is.

## The three numbers you report

Nobody reads twelve thousand voltages. What gets written on the test sheet is three
numbers, and each answers a different question.

The **mean**, `np.mean(v)`, is the DC level: what a slow meter, or a capacitor, or
your eye averaging the trace, would see.

The **peak**, `np.max(np.abs(v))`, is the largest excursion in either direction. It
is what decides whether the signal fits inside the converter's range or the
amplifier's rails.

The **RMS** is the useful one, and it is the one worth deriving rather than
memorising. Put the signal across a resistor $R$. The instantaneous power dissipated
is $v(t)^2 / R$ — the square is what makes the negative half of a wave heat the
resistor exactly as much as the positive half. The average power over the run is
therefore the *mean of the squares*, divided by $R$. Now ask what steady DC voltage
would heat the same resistor at the same rate: call it $V$, so $V^2/R$ equals that
average, and

$$V = \sqrt{\overline{v^2}}$$

the square root of the mean of the squares. RMS, backwards. It is not an arbitrary
average with a strange definition; it is the answer to "how much *work* is this
signal doing", and that is why a true-RMS meter reads it and why mains is quoted as
230 V when it swings to 325 V.

```python
rms = np.sqrt(np.mean(v * v))
```

## Worked example: four readings, by hand

Take the four values from the bench log in this module's lab: 0.00, 0.31, 0.59 and
0.81 volts.

```text
    sum        0.00 + 0.31 + 0.59 + 0.81            = 1.71
    mean       1.71 / 4                             = 0.4275 V

    squares    0.0000, 0.0961, 0.3481, 0.6561
    sum sq     0.0000 + 0.0961 + 0.3481 + 0.6561    = 1.1003
    mean sq    1.1003 / 4                           = 0.275075
    rms        sqrt(0.275075)                       = 0.5245 V

    peak       max(|0.00|, |0.31|, |0.59|, |0.81|)  = 0.81 V
    crest      0.81 / 0.5245                        = 1.544
```

Notice that the RMS, 0.5245 V, is larger than the mean, 0.4275 V. It always is, for
any signal that is not perfectly flat, because squaring gives the big readings more
weight than the small ones before the averaging happens. And notice that the mean of
the squares, 0.275075, is nothing like the square of the mean, $0.4275^2 = 0.18276$.
Those two are the same only for a constant signal, and the gap between them is
exactly the variance of the run.

## Worked example: what the meter reads on a real waveform

A rail sits at 1.5 V DC with 2.0 V of 50 Hz ripple on it — amplitude 2.0 V, so the
voltage swings between −0.5 V and +3.5 V.

```text
    mean       1.5 V                       the DC term; the sine averages to zero
    peak       1.5 + 2.0                 = 3.5 V
    mean sq    1.5^2 + (2.0^2)/2
             = 2.25  + 2.00             = 4.25 V^2
    rms        sqrt(4.25)                 = 2.0616 V
    crest      3.5 / 2.0616               = 1.698
```

The $A^2/2$ is the mean square of a sine of amplitude $A$, and the fact that the DC
and the sine contribute separately — that their squares add rather than their
amplitudes — is the derivation later in this module. For now, take the shape of the
result: **RMS adds in quadrature.** A 1.5 V rail with 2 V of ripple is not a 3.5 V
signal and not a 1.75 V one; it is 2.06 V RMS.

## The mistake, and why it is tempting

The mistake is reading a mean of zero as an absence of signal. A perfect 10 V sine
has a mean of 0.000 V, and so does a dead channel, and so does a broken probe. The
mean is the right summary for a DC level and it is blind by construction to anything
symmetric — which is most of what is interesting on a bench.

It is tempting because `np.mean` is the first function anybody reaches for and
because on a DC measurement it is exactly right. The habit worth building is to
report mean *and* RMS together and to look at both: mean near zero with a healthy RMS
is an AC signal, mean near zero with RMS near zero is a dead channel, and the two
cases are indistinguishable from either number alone.

Two smaller ones, in the same family. `np.mean(v)**2` is not `np.mean(v**2)`, as the
worked example above shows, and swapping them silently understates the power.
`abs(np.max(v))` is not `np.max(np.abs(v))`: on a signal that goes to +0.2 V and
−9.0 V the first says 0.2 and the second says 9.0, and only the second is the peak.

## Where this stops holding

**An array is fixed in size.** Appending to one in a loop copies the whole thing every
time, which turns a linear job into a quadratic one. Accumulate into a Python list
and convert once at the end, or work out the length first and preallocate with
`np.zeros(n)`.

**The array carries no time and no units.** `fs` has to travel with it, in a variable,
a filename or a header, and a column of numbers with no stated rate is not a
recording — it is a puzzle. Half the bugs in this course's remaining labs are a rate
that was assumed rather than read.

**A summary assumes the run is representative.** The mean of a capacitor charging
depends entirely on how long you left the logger running. Mean, RMS and peak describe
a signal whose character is not changing; applied to a transient they describe the
window you happened to choose, and the honest thing is to report the window with the
number.

**Peak is a single sample.** One glitch, one bit flipped in transmission, one static
discharge into the probe, and the peak of the whole run belongs to it. This is why
production tests usually quote a high percentile rather than the maximum, and why the
crest factor — peak divided by RMS — is worth carrying: a sine's is 1.414, a square
wave's is 1.0, and a value of 8 means the recording is mostly quiet with something
sharp in it.

**And memory is not free.** One hour at one megasample per second is $3.6\times10^9$
float64 values, which is 28.8 GB and will not be held in one name on any machine you
own. Past a certain size the whole approach changes: you process the recording in
blocks as it arrives and keep only the summaries. The mean and the mean square can
both be accumulated a block at a time, which is the practical reason those two
particular summaries are the ones instruments compute.
''',
                },
                {
                    "title": "What the converter kept, and what it threw away",
                    "minutes": 12,
                    "body": r'''
A film camera takes twenty-four photographs a second. Point it at a wagon wheel and
the wheel sometimes turns backwards on the screen, sometimes stands still, sometimes
crawls forward while the wagon races along. Nobody thinks the wheel did any of that.
The camera recorded twenty-four instants a second and every spoke position between
them is a story the projector is telling you.

An analogue-to-digital converter is that camera. It closes a switch, holds whatever
voltage was on the input at that instant, measures it, and opens the switch again,
`fs` times a second. Between one sample and the next it is not looking. Nothing that
happened there was recorded, and no processing afterwards can un-not-record it.

This unit is about what survives that shutter and what does not, because the answer
is sharper and less forgiving than people expect.

## Many curves pass through the same dots

Draw eight dots on a page. You can put a smooth curve through them; you can also put
a wildly wiggly one through the same eight dots, and a faster one still, and so on
without end. The dots do not determine the curve.

That sounds fatal and is not, because we are not asking for *any* curve. We are asking
which **sinusoids** fit, and sinusoids are a much smaller family. So the question
becomes concrete: given a sample rate $f_s$, which two sine frequencies produce
identical sets of samples?

## The algebra of folding

Sample $x(t) = \sin(2\pi f t)$ at instants $t = n/f_s$. The recorded sequence is

$$x[n] = \sin\left(2\pi f \frac{n}{f_s}\right) = \sin\left(2\pi \frac{f}{f_s} n\right)$$

Everything now depends on $f$ only through the ratio $f/f_s$, and it appears inside a
sine, which repeats every $2\pi$. Two things follow immediately.

**Add a whole sample rate to the frequency and nothing changes.** Put $f' = f + k f_s$
for any whole number $k$:

$$x'[n] = \sin\left(2\pi \frac{f + kf_s}{f_s} n\right)
        = \sin\left(2\pi \frac{f}{f_s} n + 2\pi k n\right)$$

and $2\pi k n$ is a whole number of turns, since $k$ and $n$ are both integers. The
sine is unchanged. Every frequency in the family $f, f \pm f_s, f \pm 2f_s, \dots$
produces *exactly* the same numbers — not nearly, not to within rounding, but
identically.

**Reflect the frequency about the sample rate and the wave comes back inverted.** Put
$f' = f_s - f$:

$$x'[n] = \sin\left(2\pi \frac{f_s - f}{f_s} n\right)
        = \sin\left(2\pi n - 2\pi \frac{f}{f_s} n\right)
        = -\sin\left(2\pi \frac{f}{f_s} n\right)$$

using $\sin(2\pi n - \theta) = -\sin\theta$. Same magnitude, opposite sign — which is
why the alias drawn in this module's sandbox is the mirror image of the samples
rather than lying on top of them.

Put the two together and every frequency has a whole family of impostors. Whatever
you sample, the recording is consistent with an unlimited number of input
frequencies, and the converter has no way to tell you which one arrived.

## Nyquist, stated as what it actually buys you

Take the family of impostors and ask how wide a band of frequencies you can allow in
before two of its members collide. The spacing of the family is $f_s$ and each member
has a reflection, so the widest band with no two members in it runs from 0 up to
$f_s/2$. Above that, everything folds down into it.

That half rate is the **Nyquist frequency**. The rule is: *a signal known in advance
to contain nothing above $f_s/2$ is recovered uniquely by sampling at $f_s$.* Every
word is load-bearing. "Known in advance" — the data cannot tell you. "Nothing above"
— not "very little". "Uniquely" — there is still only one sinusoid in the allowed
band that fits the dots, which is the whole of what sampling gives you.

To find where a stray frequency lands, fold it in two moves. First strip off whole
sample rates, which the algebra above says change nothing: let $f_a$ be the remainder
of $f$ divided by $f_s$. Then reflect if you have to — if $f_a \le f_s/2$ the tone
appears at $f_a$, and if $f_a > f_s/2$ it appears at $f_s - f_a$.

## Worked example: 150 Hz sampled at 200 Hz

The Nyquist frequency is 100 Hz and the signal is above it, so expect trouble. Fold
it: $150 \,\mathrm{mod}\, 200 = 150$, which exceeds 100, so the apparent frequency is
$200 - 150 = 50$ Hz.

That is the claim. Here is the check, in samples. The sample interval is 5 ms, and
$\sin(2\pi \cdot 150 \cdot n/200) = \sin(1.5\pi n)$ against
$\sin(2\pi \cdot 50 \cdot n/200) = \sin(0.5\pi n)$:

```text
    n      t        150 Hz sample        50 Hz sample
    0      0 ms     sin(0)      =  0     sin(0)      =  0
    1      5 ms     sin(1.5pi)  = -1     sin(0.5pi)  = +1
    2     10 ms     sin(3.0pi)  =  0     sin(1.0pi)  =  0
    3     15 ms     sin(4.5pi)  = +1     sin(1.5pi)  = -1
    4     20 ms     sin(6.0pi)  =  0     sin(2.0pi)  =  0
    5     25 ms     sin(7.5pi)  = -1     sin(2.5pi)  = +1
```

Column three is column four with every sign flipped, exactly as the reflection
algebra promised. So the 150 Hz input and an *inverted* 50 Hz input give the same
recording, digit for digit. Ask any program to tell them apart and it is being asked
to read a number that was never written down.

## Worked example: two more folds, and one that goes backwards

A vibration channel is sampled at 6 kHz and the machine has a tone at 4.7 kHz.

```text
    Nyquist        6000 / 2                = 3000 Hz
    4700 mod 6000                          = 4700 Hz   (above 3000)
    apparent       6000 - 4700             = 1300 Hz
```

A 410 Hz tone recorded at 200 Hz:

```text
    410 mod 200    410 - 2 * 200           = 10 Hz     (below 100, so no reflection)
    apparent                               = 10 Hz
```

Two whole sample rates vanish without trace and 10 Hz is left. Now run it backwards,
which is the situation you are actually in on a bench: the recording shows a strong
tone at **120 Hz**, sampled at **1 kHz**, and you want to know what is really out
there. Invert the fold — every frequency whose family contains 120 Hz:

```text
    k = 0    120                     and   1000 - 120  =  880
    k = 1    1000 + 120 = 1120       and   2000 - 120  = 1880
    k = 2    2000 + 120 = 2120       and   3000 - 120  = 2880
    ...
```

The data alone cannot choose between them. What chooses is knowledge you brought with
you — a tachometer reading, a datasheet, a filter you know is in the path. If the
shaft is turning such that the tone must lie between 1.80 and 2.00 kHz, then 1880 Hz
is the only candidate in range and the question has an answer. Without that outside
fact it does not.

## The mistake, and why it is tempting

The mistake is planning to deal with it later: *sample it, look at the spectrum, and
filter out anything that turns out to be an alias.*

It is tempting because that is how every other kind of interference behaves.
Mains hum, drift, a noisy neighbour on the board — all of those leave the signal
intact underneath and can be subtracted afterwards with enough care. Aliasing does
not. By the time the numbers exist, the 150 Hz tone and the inverted 50 Hz tone are
*the same numbers*. There is no underneath. A filter applied to the array cannot
separate two things that are one thing.

That is the entire argument for an **anti-alias filter**, and for it being analogue
and sitting physically before the converter. It is the only place in the chain where
the two are still distinguishable.

The sibling mistake is treating $2\times$ as a target rather than a limit. Sample a
sine at exactly twice its frequency and you get
$\sin(2\pi f n/(2f)) = \sin(\pi n) = 0$ for every $n$ — a recording of nothing at all,
from a signal that was there the whole time. Land the samples on the peaks instead
and you get full amplitude; the phase decides, and the phase is not yours to choose.
Real systems leave a guard band: CD audio samples at 44.1 kHz for a 20 kHz band, not
40 kHz, and the 2.05 kHz of headroom is where the analogue filter is allowed to roll
off at a physically buildable rate.

## Where this stops holding

**Sampling below the signal can be deliberate.** Nothing above says the band has to
start at zero. A signal confined to 9.0–9.5 MHz sampled at 4 MHz lands at 1.0–1.5 MHz
— $9.0 \,\mathrm{mod}\, 4 = 1.0$, $9.5 \,\mathrm{mod}\, 4 = 1.5$, both below the 2 MHz Nyquist frequency
and with no multiple of $f_s/2$ falling inside the band, so nothing in it folds onto
anything else in it and the band arrives intact and merely moved. This is **bandpass sampling**, and radios use it on purpose to avoid
building a converter that runs at twenty megasamples. The requirement was never "fast
enough for the highest frequency". It is "fast enough for the *width* of the band,
and placed so the band does not fold onto itself".

**Amplitude survives the fold; only frequency moves.** Every line of the algebra above
left the amplitude alone. An aliased tone contributes its full share to the RMS of
the recording, in the wrong place in the spectrum. That is worth knowing in both
directions: the total power you measure is honest even when the frequency is a lie.

**Frequency is only defined for something that lasts.** The whole argument assumed a
steady sinusoid running for the length of the recording. A click, a step, a switching
edge is not one frequency and folds as a smear rather than a line. The rule still
applies — it applies to every component of the thing — but "the aliased frequency" is
no longer a single number to compute.

**Time is not the only axis being sampled.** The converter also rounds each reading to
one of its finite set of levels. Quantisation is a separate, independent loss: a
16-bit converter running gloriously fast still throws away everything below its least
significant bit, and no sample rate fixes that.

**And the clock is not perfect.** All of the above assumed the samples arrived at
exactly $n/f_s$. Real clocks jitter, and a sample taken slightly early on a fast
signal is a sample of the wrong voltage. On slow signals it is invisible; on a fast
one it sets a ceiling on the effective resolution that has nothing to do with how
many bits the datasheet claims.
''',
                },
            ],
            "blanks": [
                {
                    "title": "The time axis, and the three numbers that go on the sheet",
                    "minutes": 9,
                    "lang": "python",
                    "caption": "summarise.py — a 12 000-sample bench run, reduced to one printed line",
                    "brief": r'''
Nothing here is new arithmetic. Every hole is a place where two spellings both look
reasonable and only one is the quantity named in the comment beside it.

The recording is 12 000 samples taken at 8 kHz, so it is 1.5 seconds long. Settle each
choice against that, rather than against what looks familiar.
''',
                    "listing": r'''
import numpy as np

FS = 8000.0                     # samples per second -- the array does not know this
v = np.load("run.npy")          # 12 000 readings from the bench logger

t = np.arange(___) / FS         # one timestamp per sample, the first at zero
duration = v.size / FS          # 1.500 s of recording
t_last = ___ / FS               # the instant the LAST reading was taken

mean = np.mean(v)               # the DC level
rms = np.sqrt(np.mean(v ___ 2))
peak = np.max(___(v))           # the largest excursion, either way up
crest = peak / ___              # 1.414 for a sine, 1.0 for a square wave

print(f"{duration:.3f} s  {mean:+.4f} V dc  {rms:.4f} V rms  {peak:.4f} V pk")
''',
                    "blanks": [
                        {
                            "prompt": "One timestamp per sample means counting 0, 1, 2, ... once for each reading.",
                            "hole": "count",
                            "opts": ["v.size", "FS", "v.size - 1", "duration"],
                            "a": 0,
                            "why": "`np.arange(v.size)` gives 0 to 11999 — one index per reading — and dividing by `FS` turns each index into seconds. The array's own length is the only place that count can honestly come from.",
                            "whys": [
                                "`np.arange(v.size)` gives 0 to 11999 — one index per reading — and dividing by `FS` turns each index into seconds. The array's own length is the only place that count can honestly come from.",
                                "`np.arange(FS)` counts to 8000, which is neither the number of samples nor a length in seconds. It happens to look plausible because 8000 is a round number in the problem, and the resulting `t` would be shorter than `v`, so every later expression pairing them raises a shape error.",
                                "`np.arange(v.size - 1)` is one timestamp short. Pairing an 11 999-long time axis with a 12 000-long recording fails on the first plot, which is the good case; slicing them separately first would let it through silently.",
                                "`duration` is 1.5, a float in seconds. `np.arange(1.5)` counts whole numbers below 1.5 and returns just `[0, 1]` — two timestamps for twelve thousand readings, with no error raised anywhere.",
                            ],
                        },
                        {
                            "prompt": "The last reading is at index 11 999, not 12 000. The recording lasts 1.5 s; the last sample is taken slightly before the end of it.",
                            "hole": "index",
                            "opts": ["v.size - 1", "v.size", "t[0]", "FS"],
                            "a": 0,
                            "why": "Indices run 0 to `v.size - 1`, so the final instant is $(n-1)/f_s = 11999/8000 = 1.499875$ s. The recording is 1.5 s long because it contains 12 000 *intervals* of 125 µs, and the last sample sits one interval before the far end of the last one.",
                            "whys": [
                                "Indices run 0 to `v.size - 1`, so the final instant is $(n-1)/f_s = 11999/8000 = 1.499875$ s. The recording is 1.5 s long because it contains 12 000 *intervals* of 125 µs, and the last sample sits one interval before the far end of the last one.",
                                "`v.size / FS` is the duration, already computed on the line above. Using it here says the last reading was taken at 1.500 s, one whole sample interval later than it was — the classic fencepost, and it puts every frequency you later derive from this axis slightly out.",
                                "`t[0]` is zero, so this would report that the last reading was taken at the same instant as the first. It also reads `t` while `t` is still being built in the line above, which is fragile even when it is not wrong.",
                                "`FS / FS` is 1.0 second. It is dimensionally sound and numerically meaningless: the answer would be 1 s for every recording ever made, at any rate, of any length.",
                            ],
                        },
                        {
                            "prompt": "RMS is the square root of the mean of the squares, so each element has to be squared first.",
                            "hole": "operator",
                            "opts": ["**", "*", "^", "//"],
                            "a": 0,
                            "why": "`v ** 2` raises every element to the second power. `np.mean` of that is the mean square, and the square root of it is the RMS — the DC voltage that would heat a resistor at the same rate as this signal.",
                            "whys": [
                                "`v ** 2` raises every element to the second power. `np.mean` of that is the mean square, and the square root of it is the RMS — the DC voltage that would heat a resistor at the same rate as this signal.",
                                "`v * 2` doubles every element instead of squaring it. The mean of that is twice the mean, and its square root is a number with no meaning at all — but it is finite, positive and roughly the right size, so it prints without complaint.",
                                "`v ^ 2` is the bitwise exclusive-or, not a power — Python spells exponentiation `**`. On a float array it raises a TypeError, which at least is loud; on an integer array it would return the elements with a bit flipped.",
                                "`v // 2` is integer division: every reading is halved and rounded towards minus infinity. On a signal in volts that mostly produces zeros and minus ones, and the RMS of that says nothing about the recording.",
                            ],
                        },
                        {
                            "prompt": "The peak is the largest magnitude, so a −9 V spike counts as 9 V.",
                            "hole": "function",
                            "opts": ["np.abs", "np.sign", "np.sqrt", "np.mean"],
                            "a": 0,
                            "why": "`np.max(np.abs(v))` strips the signs first and then takes the largest, so a run that reaches +0.2 V and −9.0 V has a peak of 9.0 V. Written the other way round, `abs(np.max(v))` finds the largest *signed* value, 0.2, and then removes a sign it never had.",
                            "whys": [
                                "`np.max(np.abs(v))` strips the signs first and then takes the largest, so a run that reaches +0.2 V and −9.0 V has a peak of 9.0 V. Written the other way round, `abs(np.max(v))` finds the largest *signed* value, 0.2, and then removes a sign it never had.",
                                "`np.sign` returns −1, 0 or +1 for each element, so the maximum is 1 for any recording containing a single positive reading. A peak of exactly 1.0 on every channel is the sort of wrong answer that survives review.",
                                "`np.sqrt` of a recording that goes negative gives `nan` for those elements, and `np.max` of an array containing `nan` is `nan`. The crest factor below then becomes `nan` too, which at least propagates visibly.",
                                "`np.mean(v)` is the DC level, already computed two lines up. Taking `np.max` of a single number returns that number, so the peak and the mean would print identically — and on an AC signal both would be near zero.",
                            ],
                        },
                        {
                            "prompt": "Crest factor compares the largest excursion with the signal's heating value.",
                            "hole": "denominator",
                            "opts": ["rms", "mean", "duration", "np.sqrt(2)"],
                            "a": 0,
                            "why": "Crest factor is peak divided by RMS. A sine gives $A / (A/\\sqrt{2}) = 1.414$ and a square wave gives 1.0, so the number says how spiky a recording is independently of how big it is — which is exactly what you want when deciding how much headroom an amplifier needs.",
                            "whys": [
                                "Crest factor is peak divided by RMS. A sine gives $A / (A/\\sqrt{2}) = 1.414$ and a square wave gives 1.0, so the number says how spiky a recording is independently of how big it is — which is exactly what you want when deciding how much headroom an amplifier needs.",
                                "Dividing by the mean blows up on any AC signal, where the mean is near zero: the ratio runs off to enormous values or to `inf`, and it changes completely if a small DC offset drifts. The comment's promise of 1.414 for a sine would fail immediately.",
                                "`duration` is 1.5 seconds, so this divides volts by seconds. The result changes if you record for longer, which no property of the waveform's shape should.",
                                "Dividing by $\\sqrt{2}$ gives $A/1.414$ for a sine of amplitude $A$ — a voltage, not a ratio, and one that happens to equal the RMS itself. It is the right constant remembered in the wrong place: $\\sqrt{2}$ is the *answer* for a sine, not part of the definition.",
                            ],
                        },
                    ],
                },
                {
                    "title": "Where the window starts and where it stops",
                    "minutes": 9,
                    "lang": "python",
                    "caption": "window.py — cutting an event out of a run, and thinning what is left",
                    "brief": r'''
The same 12 000-sample, 8 kHz recording. This time the interesting part is a burst
between 20 ms and 50 ms, and afterwards the file has to be thinned to a quarter of
its size before being sent on.

Two of the holes decide *which* samples you keep. The last one decides what a tone
in the thinned file will claim to be.
''',
                    "listing": r'''
import numpy as np

FS = 8000.0
v = np.load("run.npy")               # 12 000 samples, 1.5 s

# the burst runs from 20 ms to 50 ms after the start of the file
i0 = int(round(0.020 * ___))         # -> 160
i1 = int(round(0.050 * FS))          # -> 400
window = v[i0:___]
print(window.size)                   # 240 samples, which is the 30 ms asked for

settled = window[___]                # the final reading of the burst

# thin the whole run to a quarter of the rate before sending it on
decim = v[::___]
fs_new = FS / 4                      # 2000 Hz, so 1 kHz is the new Nyquist limit
f_alias = abs(1700 - ___)            # a 1.7 kHz tone comes back at 300 Hz
''',
                    "blanks": [
                        {
                            "prompt": "Seconds times samples-per-second gives samples.",
                            "hole": "rate",
                            "opts": ["FS", "1000", "v.size", "FS / 1000"],
                            "a": 0,
                            "why": "$0.020\\,\\text{s} \\times 8000\\,\\text{samples/s} = 160$ samples. Multiplying a time by the sample rate is the only conversion in this direction, and the units cancel to leave a count.",
                            "whys": [
                                "$0.020\\,\\text{s} \\times 8000\\,\\text{samples/s} = 160$ samples. Multiplying a time by the sample rate is the only conversion in this direction, and the units cancel to leave a count.",
                                "1000 converts seconds to milliseconds, giving 20 — a number in the wrong unit that is nevertheless a valid index. The window would start at 20 samples, 2.5 ms in, and the code would run perfectly and analyse the wrong stretch of the recording.",
                                "`v.size` is 12 000, so this gives index 240. It is dimensionally wrong — length times time — and it depends on how long you recorded for, so the window would move whenever the file did.",
                                "`FS / 1000` is 8, giving index 0. That is samples per millisecond, which is the right idea one prefix out; the burst would appear to start at the very beginning of the file.",
                            ],
                        },
                        {
                            "prompt": "A slice runs up to but not including its second index.",
                            "hole": "stop",
                            "opts": ["i1", "i1 - i0", "i0 + i1", "240"],
                            "a": 0,
                            "why": "`v[i0:i1]` is `v[160:400]`, which holds $400 - 160 = 240$ elements — the count printed on the next line. Because the stop is exclusive, the *length* of a slice is the difference of its two indices, which is why adjacent slices meet exactly once with nothing shared and nothing missed.",
                            "whys": [
                                "`v[i0:i1]` is `v[160:400]`, which holds $400 - 160 = 240$ elements — the count printed on the next line. Because the stop is exclusive, the *length* of a slice is the difference of its two indices, which is why adjacent slices meet exactly once with nothing shared and nothing missed.",
                                "`i1 - i0` is 240, and `v[160:240]` is 80 samples — 10 ms of the 30 asked for. This is the difference confused with the endpoint, and the giveaway is that the printed size would be 80 while the number 240 appears in the code.",
                                "`i0 + i1` is 560, so the window runs to 70 ms and holds 400 samples. It ends 20 ms past the burst, quietly including whatever came after it.",
                                "The literal 240 is the length of the window, not where it stops, so `v[160:240]` again cuts 80 samples. Hard-coding it also means the line stops being right the moment either time in the comment above changes.",
                            ],
                        },
                        {
                            "prompt": "The last element of the window, without depending on how many there are.",
                            "hole": "index",
                            "opts": ["-1", "0", "len(window)", "i1"],
                            "a": 0,
                            "why": "`window[-1]` counts one back from the end, so it stays correct if the burst's boundaries move. `window[239]` reaches the same element today and silently reads the wrong one the day the window changes length.",
                            "whys": [
                                "`window[-1]` counts one back from the end, so it stays correct if the burst's boundaries move. `window[239]` reaches the same element today and silently reads the wrong one the day the window changes length.",
                                "`window[0]` is the first reading of the burst, at 20 ms — the value before anything has settled, which is the opposite of what the name `settled` claims.",
                                "`window[len(window)]` is `window[240]`, one past the end, and raises an IndexError. The highest valid index is always one less than the length, which is the same fencepost as the timestamp of the last sample.",
                                "`window[i1]` is `window[400]`, well past the end of a 240-element slice — an IndexError. `i1` indexes into `v`, and `window` has its own numbering starting from zero.",
                            ],
                        },
                        {
                            "prompt": "Keep every fourth sample and discard the other three.",
                            "hole": "step",
                            "opts": ["4", "2", "0.25", "-4"],
                            "a": 0,
                            "why": "`v[::4]` takes indices 0, 4, 8, ... — one sample in four, so 3000 remain and the effective rate falls to 2 kHz, as the next line asserts.",
                            "whys": [
                                "`v[::4]` takes indices 0, 4, 8, ... — one sample in four, so 3000 remain and the effective rate falls to 2 kHz, as the next line asserts.",
                                "`v[::2]` keeps every second sample, halving the rate to 4 kHz rather than quartering it to 2 kHz. The file would be twice the size promised and `fs_new` would be a lie about it, which is the worst kind of mismatch: nothing raises, and the frequency axis of every later plot is out by two.",
                                "A slice step must be an integer; `v[::0.25]` raises a TypeError. The instinct is right — a quarter of the samples — but the step counts indices to skip, not a fraction to keep.",
                                "`v[::-4]` walks the recording backwards, so the samples come out in reverse order. The count is right and the file is time-reversed, which for a burst with a rise and a decay is very obviously wrong to a human and not at all obvious to a program.",
                            ],
                        },
                        {
                            "prompt": "Above the new Nyquist limit a tone folds back from the sample rate.",
                            "hole": "rate",
                            "opts": ["fs_new", "FS", "fs_new / 2", "1700"],
                            "a": 0,
                            "why": "After thinning, $f_s = 2000$ Hz and $1700 \\,\\mathrm{mod}\\, 2000 = 1700$, which is above the 1 kHz limit, so it reflects to $2000 - 1700 = 300$ Hz. The fold is always about the *sample rate* in the subtraction, even though the *limit* being crossed is half of it.",
                            "whys": [
                                "After thinning, $f_s = 2000$ Hz and $1700 \\,\\mathrm{mod}\\, 2000 = 1700$, which is above the 1 kHz limit, so it reflects to $2000 - 1700 = 300$ Hz. The fold is always about the *sample rate* in the subtraction, even though the *limit* being crossed is half of it.",
                                "`FS` is the rate before thinning, 8000 Hz, giving 6300 Hz. At the original rate 1.7 kHz was comfortably below the 4 kHz limit and did not alias at all — the tone only became a problem when the samples were thrown away.",
                                "`fs_new / 2` is the Nyquist frequency, 1000 Hz, giving 700 Hz. This is the limit confused with the mirror: the fold reflects *about* 1000 Hz, and reflecting 1700 about 1000 lands at 300, not 700. Subtracting the limit itself is the commonest way to get an alias wrong.",
                                "Subtracting 1700 from itself gives 0 Hz for every tone. A frequency does alias to zero when it equals a whole multiple of the sample rate, but that is a coincidence of particular numbers, not a rule.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "How long is the file?",
                    "minutes": 5,
                    "brief": r'''
A vibration logger was left running on a gearbox and came back with one file. The
only two facts you need are in the header.

The sample rate is a count per second, so a count divided by a rate is a time.
''',
                    "prompt": "How long a stretch of the gearbox's life does this file cover? Answer in **milliseconds**.",
                    "figure": r'''
```text
run.hdr
    channel .......... acc_z
    sample rate ...... 8000 samples/s
    samples .......... 12000
    format ........... float64
```
''',
                    "given": [
                        {"label": "Sample rate", "value": "8 kHz"},
                        {"label": "Samples in the file", "value": "12 000"},
                        {"label": "Answer wanted in", "value": "ms"},
                    ],
                    "note": "One division. The units do the work: samples divided by samples-per-second leaves seconds.",
                    "hint": "$n / f_s$ gives the answer in seconds. Multiply by 1000 for milliseconds.",
                    "wrong": "Check which way up the division goes. Rate over count gives 0.667, which has units of 1/s and is not a time at all — if the answer is smaller than 1 when the file is clearly longer than a millisecond, the fraction is upside down.",
                    "answer": 1500.0,
                    "tol": 1.0,
                    "unit": "ms",
                    "why": r'''
$12000 / 8000 = 1.5$ s, which is 1500 ms.

Worth noticing what this does *not* say. The last sample was not taken at 1.5 s; it
was taken at $11999/8000 = 1.499875$ s, because the first one was taken at zero. The
file covers 1.5 s because it holds 12 000 intervals of 125 µs, and the readings sit
at the leading edge of each. Duration counts gaps, timestamps count steps, and the
two differ by exactly one sample interval — an error small enough to survive review
and large enough to shift a frequency estimate.
''',
                },
                {
                    "title": "What the true-RMS meter reads on a rail with ripple",
                    "minutes": 7,
                    "brief": r'''
A linear supply is meant to give a clean 2.4 V. On the scope it is 2.4 V with a
plainly sinusoidal ripple riding on it at twice the mains frequency, 5.0 V from the
bottom of the trough to the top of the crest.

A true-RMS meter across the rail does not read 2.4, and does not read 4.9 either. It
reports the square root of the mean of the squares of everything present.
''',
                    "prompt": "What does the true-RMS meter read across this rail? Answer in **volts**.",
                    "figure": r'''
```text
    +4.90 V  ---------  crest
                 ^
                 |      5.0 V peak-to-peak of 100 Hz ripple
    +2.40 V  ---------  mean (the DC level)
                 |
                 v
    -0.10 V  ---------  trough
```
''',
                    "given": [
                        {"label": "DC level", "value": "2.4 V"},
                        {"label": "Ripple", "value": "5.0 V peak-to-peak, sinusoidal"},
                        {"label": "Answer wanted in", "value": "V"},
                    ],
                    "note": "Two steps: turn peak-to-peak into an amplitude, then combine the DC and the ripple the way squares combine.",
                    "hint": "The mean square of a sine of amplitude $A$ is $A^2/2$, and the mean square of a constant $V_0$ is $V_0^2$. They add. Peak-to-peak is twice the amplitude.",
                    "wrong": "Two near misses to check against. Reading 5.0 V as the amplitude rather than the peak-to-peak gives 4.27 V. Adding the DC and the ripple's RMS as voltages, 2.4 + 1.768, gives 4.17 V — that is the quadrature rule ignored, and it always overstates.",
                    "answer": 2.9808,
                    "tol": 0.01,
                    "unit": "V",
                    "why": r'''
```text
    amplitude      5.0 / 2                       = 2.50 V
    ripple mean sq 2.50^2 / 2 = 6.25 / 2         = 3.125 V^2
    dc mean sq     2.40^2                        = 5.760 V^2
    total mean sq  5.760 + 3.125                 = 8.885 V^2
    rms            sqrt(8.885)                   = 2.9808 V
```

The step that carries the physics is adding the two mean squares rather than the two
voltages. Mean square is proportional to power, and the DC and the ripple deliver
their power independently — the cross term between them averages to zero over a whole
number of cycles, which is what the derivation in this module works through.

So the meter reads 2.98 V on a rail whose *average* is 2.40 V. The gap is not an
instrument error; it is 0.58 V of genuine extra heating that the ripple is doing in
whatever the rail is feeding. A DC voltmeter on the same rail would read 2.40 V and
be equally correct about a different question.
''',
                },
                {
                    "title": "The tone at 120 Hz that is not at 120 Hz",
                    "minutes": 9,
                    "brief": r'''
An accelerometer on a compressor is logged at 1.0 kHz. The spectrum of the recording
has one dominant line, at 120 Hz.

The service manual says the vane-pass tone of this compressor sits between 1.80 kHz
and 2.00 kHz, and there is no anti-alias filter in the path — the logger was chosen
for its battery life, not its front end.

Work out which real frequency produced that line.
''',
                    "prompt": "What is the true frequency of the tone? Answer in **hertz**.",
                    "figure": r'''
```text
    recorded spectrum, fs = 1000 Hz

    |                    #
    |                    #
    |____________________#________________________
    0                   120                     500  Hz
                                        (Nyquist limit)

    manual: vane-pass tone lies in 1800 .. 2000 Hz
```
''',
                    "given": [
                        {"label": "Sample rate", "value": "1.0 kHz"},
                        {"label": "Line seen at", "value": "120 Hz"},
                        {"label": "Tone known to lie in", "value": "1800-2000 Hz"},
                        {"label": "Answer wanted in", "value": "Hz"},
                    ],
                    "note": "Run the fold backwards. Every frequency of the form $k f_s \\pm 120$ produces this same line; only one of them is in the range the manual allows.",
                    "hint": "Adding a whole sample rate to a frequency leaves the samples unchanged, and reflecting about a multiple of the sample rate changes only the sign. So list $120$, $1000-120$, $1000+120$, $2000-120$, $2000+120$, ... and see which lands between 1800 and 2000.",
                    "wrong": "If the answer came out as 2120 Hz, the reflection went the wrong way at $k = 2$ — that candidate is real, but it is above 2000 and the manual rules it out. If it came out as 880 or 1120, that is the $k = 1$ pair, below the stated range.",
                    "answer": 1880.0,
                    "tol": 5.0,
                    "unit": "Hz",
                    "why": r'''
```text
    k = 0      120                    1000 - 120  =  880
    k = 1     1120                    2000 - 120  = 1880   <-- in 1800..2000
    k = 2     2120                    3000 - 120  = 2880
```

Every one of those frequencies, sampled at 1 kHz, produces a line at 120 Hz, and the
recording contains no information whatever that distinguishes them. Only 1880 Hz
falls inside the band the manual allows, so that is the tone — and the answer rests
on the manual as much as on the data.

That is the honest shape of an aliasing problem. The forward direction is arithmetic:
$1880 \,\mathrm{mod}\, 1000 = 880$, which is above the 500 Hz limit, so it reflects to
$1000 - 880 = 120$. The backward direction is arithmetic *plus* a fact from outside
the recording. Without the manual there is no answer here, only a family of them,
and any program that picks one is guessing on your behalf.

The practical consequence is worth stating plainly: this logger cannot be used on
this machine as configured. Move the vane-pass tone below 500 Hz and it cannot be
done; the fix is an analogue low-pass filter before the converter, or a faster
logger, and no amount of work on the file that came back will substitute for either.
''',
                },
                {
                    "title": "Three components, one number on the sheet",
                    "minutes": 11,
                    "brief": r'''
A sensor output is logged at 1.0 kHz for exactly 50 ms — 50 samples — and the array
is summarised with `np.sqrt(np.mean(v**2))`. What is on the line the signal generator
is producing:

  * a 1.5 V DC offset,
  * a 60 Hz sine of amplitude 2.0 V,
  * a 900 Hz sine of amplitude 0.8 V.

The 900 Hz component is above the 500 Hz limit, so the recording will not show it
where it belongs. The question is what the RMS of the recorded array comes to.

Both frequencies complete a whole number of cycles in 50 ms, so there is no partial
cycle to worry about.
''',
                    "prompt": "What RMS does the program report for the recorded array? Answer in **volts**.",
                    "figure": r'''
```text
    on the wire                          in the array (fs = 1000 Hz)

    1.5 V  dc                            1.5 V  dc          unmoved
    2.0 V  amplitude @   60 Hz           2.0 V  @   60 Hz   below the limit
    0.8 V  amplitude @  900 Hz           0.8 V  @  100 Hz   folded: 1000 - 900

    50 samples at 1 kHz = 50 ms
      60 Hz -> 3 whole cycles
     100 Hz -> 5 whole cycles
```
''',
                    "given": [
                        {"label": "DC", "value": "1.5 V"},
                        {"label": "Component 1", "value": "2.0 V amplitude, 60 Hz"},
                        {"label": "Component 2", "value": "0.8 V amplitude, 900 Hz"},
                        {"label": "Sample rate, length", "value": "1.0 kHz, 50 samples"},
                        {"label": "Answer wanted in", "value": "V"},
                    ],
                    "note": "Decide first whether the fold changes the number you are being asked for. Then add mean squares, not voltages.",
                    "hint": "Aliasing moves a component's frequency and leaves its amplitude alone — look again at the algebra of the fold and see that nothing multiplies the sine. So the mean square is $V_0^2 + A_1^2/2 + A_2^2/2$ whether or not the second tone folded.",
                    "wrong": "If the answer came out near 2.06 V, the 900 Hz component was dropped as 'lost to aliasing' — it is not lost, it is misplaced, and it heats a resistor exactly as much at 100 Hz as it did at 900. If it came out near 3.48 V, the three contributions were added as voltages instead of as squares.",
                    "answer": 2.1378,
                    "tol": 0.01,
                    "unit": "V",
                    "why": r'''
```text
    dc            1.5^2                     = 2.250 V^2
    60 Hz         2.0^2 / 2 = 4.00 / 2      = 2.000 V^2
    900 Hz        0.8^2 / 2 = 0.64 / 2      = 0.320 V^2
    total mean sq 2.250 + 2.000 + 0.320     = 4.570 V^2
    rms           sqrt(4.570)               = 2.1378 V
```

Three things had to be settled before that arithmetic was allowed.

**The fold does not touch the amplitude.** Sampling 900 Hz at 1 kHz gives
$\sin(2\pi \cdot 0.9 n) = -\sin(2\pi \cdot 0.1 n)$: the frequency moved to 100 Hz and
the sign flipped, and nothing scaled. Since the RMS squares everything anyway, the
sign flip cannot matter either. The recorded array has the same mean square as an
unaliased one would.

**The cross terms vanish.** Two sines at different frequencies multiply to
$\tfrac{1}{2}[\cos(\text{difference}) - \cos(\text{sum})]$, and both of those average
to zero over a whole number of cycles. In 50 ms the 60 Hz tone does 3 cycles and the
folded 100 Hz tone does 5, so the difference and sum terms complete 2 and 8 cycles
respectively and both sum to exactly zero across the 50 samples. That is what makes
the contributions independent and the addition legal.

**The DC belongs in the sum too.** Its mean square is $1.5^2$, undivided — there is no
factor of a half, because a constant is not oscillating and its square is not
oscillating either. Forgetting this is the same slip as reading a rail's ripple as
its whole content.

For contrast, the peak of this recorded array is 4.225 V, so its crest factor is
$4.225 / 2.138 = 1.98$ — nearly twice a sine's 1.414, and a fair warning that a
2.1 V RMS signal here still needs better than 4.3 V of headroom.
''',
                },
            ],
            "derive": {
                "title": "Why RMS adds in quadrature",
                "minutes": 14,
                "vars": ["A", "A_1", "A_2", "V_0", "V_rms", "omega", "t"],
                "brief": r'''
Two of the numerics in this module leaned on a rule that was stated and not shown:
that a DC level and a sine, or two sines at different frequencies, contribute to the
RMS through their squares rather than through their voltages. This is where it comes
from.

The signal runs for a whole number of cycles of everything in it, so an average over
the run is an average over complete cycles. Write $\overline{x}$ for that average.
Answers are expressions in the symbols named, with no numbers where a symbol will do.
''',
                "steps": [
                    {
                        "prompt": "Start with the one fact everything else is built on. Using $\\sin^2\\theta = \\tfrac{1}{2}(1 - \\cos 2\\theta)$, write the average of $\\sin^2(\\omega t)$ over a whole number of cycles.",
                        "answer": "\\frac{1}{2}",
                        "placeholder": "a plain number",
                        "hint": "The identity splits the square into a constant plus a cosine at twice the frequency. A cosine over whole cycles averages to zero, so only the constant survives.",
                        "deconstruct": [
                            "$\\sin^2(\\omega t) = \\tfrac{1}{2} - \\tfrac{1}{2}\\cos(2\\omega t)$.",
                            "Averaging is linear, so average the two pieces separately.",
                            "The average of $\\tfrac{1}{2}$ is $\\tfrac{1}{2}$; the average of $\\cos(2\\omega t)$ over whole cycles is 0. A sine spends as much time squared-large as squared-small, and it works out to exactly half.",
                        ],
                    },
                    {
                        "prompt": "Now a real signal. Write the mean square $\\overline{v^2}$ of $v(t) = A\\sin(\\omega t)$.",
                        "answer": "\\frac{A^2}{2}",
                        "placeholder": "in terms of A",
                        "hint": "$v^2 = A^2\\sin^2(\\omega t)$, and $A^2$ is a constant that comes straight out of the average.",
                        "deconstruct": [
                            "Squaring: $v(t)^2 = A^2 \\sin^2(\\omega t)$.",
                            "$A^2$ does not vary with time, so $\\overline{A^2 \\sin^2} = A^2\\,\\overline{\\sin^2}$.",
                            "The previous step gives $\\overline{\\sin^2} = 1/2$, so the mean square is $A^2/2$. Units check: a mean square of a voltage is in volts squared, and so is this.",
                        ],
                    },
                    {
                        "prompt": "Take the square root. Write the RMS value of $A\\sin(\\omega t)$.",
                        "answer": "\\frac{A}{\\sqrt{2}}",
                        "placeholder": "in terms of A",
                        "hint": "RMS is the square root of the answer to the last step, and $\\sqrt{A^2/2} = A/\\sqrt{2}$ for positive $A$.",
                        "deconstruct": [
                            "$V_{rms} = \\sqrt{\\overline{v^2}} = \\sqrt{A^2/2}$.",
                            "The root distributes: $\\sqrt{A^2}/\\sqrt{2} = A/\\sqrt{2}$.",
                            "Numerically that is $0.7071\\,A$, so a sine that reaches 325 V at its peak is the 230 V rms of a mains outlet.",
                        ],
                    },
                    {
                        "prompt": "Add a DC level: $v(t) = V_0 + A\\sin(\\omega t)$. Square it and average term by term. Write $\\overline{v^2}$.",
                        "answer": "V_0^2 + \\frac{A^2}{2}",
                        "placeholder": "a sum of two terms",
                        "hint": "The square has three terms. Two of them you have already averaged; the third contains a bare $\\sin(\\omega t)$, which averages to zero over whole cycles.",
                        "deconstruct": [
                            "$(V_0 + A\\sin\\omega t)^2 = V_0^2 + 2V_0A\\sin(\\omega t) + A^2\\sin^2(\\omega t)$.",
                            "$\\overline{V_0^2} = V_0^2$, since it does not vary. $\\overline{2V_0A\\sin(\\omega t)} = 2V_0A \\cdot 0 = 0$, because a sine over whole cycles averages to zero.",
                            "$\\overline{A^2\\sin^2(\\omega t)} = A^2/2$ from the earlier step, so the total is $V_0^2 + A^2/2$. The cross term dying is the whole trick: it is why the two contributions never interfere.",
                        ],
                    },
                    {
                        "prompt": "Write the RMS of that signal — the number a true-RMS meter would report for a rail at $V_0$ carrying ripple of amplitude $A$.",
                        "answer": "\\sqrt{V_0^2 + \\frac{A^2}{2}}",
                        "placeholder": "\\sqrt{...}",
                        "hint": "Square root of the previous line, and it does not simplify further — a sum inside a root stays inside it.",
                        "deconstruct": [
                            "$V_{rms} = \\sqrt{\\overline{v^2}}$, so put the previous answer under the root.",
                            "It cannot be split: $\\sqrt{a + b}$ is not $\\sqrt{a} + \\sqrt{b}$, which is exactly the mistake the word *quadrature* is warning about.",
                            "With $V_0 = 2.4$ V and $A = 2.5$ V this is $\\sqrt{5.76 + 3.125} = 2.98$ V, the reading in the ripple numeric.",
                        ],
                    },
                    {
                        "prompt": "Now two sines at *different* frequencies on top of the DC: $v = V_0 + A_1\\sin(\\omega_1 t) + A_2\\sin(\\omega_2 t)$. Every cross term averages to zero for the same reason as before. Write the RMS.",
                        "answer": "\\sqrt{V_0^2 + \\frac{A_1^2}{2} + \\frac{A_2^2}{2}}",
                        "placeholder": "\\sqrt{...}",
                        "hint": "Each component contributes its own mean square and nothing else. The pattern from the last step just gains a term.",
                        "deconstruct": [
                            "Squaring gives three squared terms and three cross terms.",
                            "$\\overline{\\sin(\\omega_1 t)\\sin(\\omega_2 t)} = \\tfrac{1}{2}\\overline{\\cos((\\omega_1-\\omega_2)t)} - \\tfrac{1}{2}\\overline{\\cos((\\omega_1+\\omega_2)t)} = 0$ when the two frequencies differ, and the DC-times-sine terms vanish as before.",
                            "What is left is $V_0^2 + A_1^2/2 + A_2^2/2$ under the root. With 1.5 V, 2.0 V and 0.8 V that is $\\sqrt{2.25 + 2 + 0.32} = 2.1378$ V, the answer to the three-component numeric.",
                        ],
                    },
                    {
                        "prompt": "Finally, put the meter on AC coupling, which passes the signal through a capacitor and removes the DC. Write what it reads now.",
                        "answer": "\\sqrt{\\frac{A_1^2}{2} + \\frac{A_2^2}{2}}",
                        "placeholder": "\\sqrt{...}",
                        "hint": "One term leaves the sum and the rest are untouched, because they never depended on it.",
                        "deconstruct": [
                            "AC coupling subtracts the mean, so $V_0$ becomes 0.",
                            "Setting $V_0 = 0$ in the previous answer removes exactly one term.",
                            "For the three-component signal that is $\\sqrt{2 + 0.32} = 1.523$ V against 2.138 V DC-coupled. Two readings, both correct, of the same wire — which is why an RMS figure without its coupling stated is not a measurement.",
                        ],
                    },
                ],
                "closing": r'''
Three things to carry out of this.

**Quadrature is a consequence, not a convention.** Nothing was assumed about the
signal except that the average of a sine over whole cycles is zero. That single fact
killed every cross term, and killing the cross terms is what lets separate
contributions add through their squares. The rule generalises without effort:

$$V_{rms} = \sqrt{V_0^2 + \tfrac{1}{2}\sum_k A_k^2}$$

for any number of components at distinct frequencies, which is why an instrument can
report a signal's RMS without knowing anything about what is in it.

**Squares add because power adds.** Mean square is proportional to the power delivered
into a resistance, and power from independent sources adds. The algebra above is that
physical statement, done with a pencil.

**Where it stops.** The cross term only vanishes when the two frequencies *differ*.
Two components at the *same* frequency do not add in quadrature at all — they add as
phasors, amplitude and phase together, and two 1 V tones at the same frequency give
anything between 0 V and 2 V depending on their relative phase. The same caveat
covers correlated noise: two noise sources that share a cause are not independent,
their cross term does not average away, and quoting a total by adding squares
understates or overstates it. Independence is doing real work in this derivation, and
"different frequency" is the easiest way — not the only way — to get it.

One more caveat that this module has already met. The averages here were taken over a
*whole number of cycles*. Cut the run at 47.3 cycles instead and the cross terms
leave a small residue that does not cancel, which is why an instrument's RMS reading
wobbles on a signal whose frequency does not divide neatly into its gate time.
''',
            },
            "sandbox": {
                "title": "What sampling keeps and what it destroys",
                "visualiser": "spectrum",
                "minutes": 9,
                "initial": {"fsig": 30, "fs": 200},
                "brief": r'''
The top panel shows 100 ms of a sine wave: the true wave as a faint line, and the
moments the converter looked at it as dots. The bottom panel is the same story in
frequency — a spike where the signal is, and a dashed line at half the sample rate.

This is the picture behind the array your code will hold. Every number in that array
is one of those dots, and nothing between them was ever recorded.
''',
                "notice": [
                    "As it opens, the signal is 30 Hz and the sample rate 200 Hz. There is one spike, well to the left of the dashed line, and no amber curve. Below half the sample rate the dots pin the wave down uniquely.",
                    "Drag the signal up to 150 Hz. A second, amber spike appears at 50 Hz — that is 200 − 150, the signal folded back about the dashed line — and an amber 50 Hz wave is drawn across the samples. Watch its sign: it is the mirror image of the dots, because folding reverses the phase of the copy as well as moving its frequency. An inverted 50 Hz sine would produce these dots exactly, and after the converter nothing tells it from the 150 Hz input.",
                    "Set the signal to 200 Hz, equal to the sample rate. The amber curve flattens onto zero and its spike sits at the far left: every sample lands at the same point in the cycle, so the recording says the input was a constant.",
                    "Put the signal back to 30 Hz and lower the sample rate to 50 Hz instead. The signal has not changed, yet an alias appears at 20 Hz. Aliasing is a property of the pair, never of the signal alone.",
                ],
            },
            "quiz": {
                "title": "Arrays, samples and what the meter reads",
                "minutes": 9,
                "questions": [
                    {
                        "q": "How many values does `np.arange(0, 1, 0.25)` contain?",
                        "opts": ["3", "4", "5", "It depends on the floating-point rounding"],
                        "a": 1,
                        "why": (
                            "Four: 0, 0.25, 0.5 and 0.75. `arange` stops *before* the stop value, exactly as "
                            "`range` does, so 1.0 is not included. When you want both ends and an exact "
                            "count, `np.linspace(0, 1, 5)` is the tool — it gives 0, 0.25, 0.5, 0.75, 1.0. "
                            "With a step that does not divide the span evenly, `arange` really can be "
                            "unpredictable at the last element, which is the reason `linspace` exists."
                        ),
                    },
                    {
                        "q": "`a = [1, 2, 3]` and `b = np.array([1, 2, 3])`. What are `2 * a` and `2 * b`?",
                        "opts": [
                            "Both give `[2, 4, 6]`",
                            "`2 * a` gives `[1, 2, 3, 1, 2, 3]`, `2 * b` gives `[2, 4, 6]`",
                            "`2 * a` raises an error, `2 * b` gives `[2, 4, 6]`",
                            "Both give `[1, 2, 3, 1, 2, 3]`",
                        ],
                        "a": 1,
                        "why": (
                            "Multiplying a list repeats it; multiplying an array scales every element. The "
                            "symbol is the same and the meaning comes entirely from the type, which is why "
                            "a signal belongs in an array and not in a list. The error this catches is "
                            "usually silent: a doubled-length signal looks plausible until you ask how long "
                            "the recording is supposed to be."
                        ),
                    },
                    {
                        "q": "You sample for 2 seconds at 500 Hz. How many samples do you have?",
                        "opts": ["250", "500", "1000", "1002"],
                        "a": 2,
                        "why": (
                            "1000. The sample rate is samples per second, so the count is rate times "
                            "duration. Working the other way round is the more useful habit: given an array "
                            "of `n` samples taken at `fs`, the recording lasts `n / fs` seconds and sample "
                            "`i` was taken at `i / fs`. Every time axis you build in this course comes from "
                            "that one relationship."
                        ),
                    },
                    {
                        "q": "A 150 Hz sine is sampled at 200 Hz. What does the recorded data look like?",
                        "opts": [
                            "A 150 Hz sine, slightly rough",
                            "A 50 Hz sine",
                            "A 350 Hz sine",
                            "Noise with no particular frequency",
                        ],
                        "a": 1,
                        "why": (
                            "A 50 Hz sine, and not approximately — the samples are *identical* to those a "
                            "genuine 50 Hz input would have produced. Above half the sample rate a signal "
                            "folds back: 200 − 150 = 50. Because the two are indistinguishable in the data, "
                            "no filter, no averaging and no clever algorithm applied afterwards can separate "
                            "them, which is why the anti-alias filter is analogue and sits before the converter."
                        ),
                    },
                    {
                        "q": "`v` holds 1000 samples. Which expression reads the last one without your having to know how many there are?",
                        "opts": ["`v[1000]`", "`v[999]`", "`v[-1]`", "`v[len(v)]`"],
                        "a": 2,
                        "why": (
                            "`v[-1]`, which counts one back from the end. `v[999]` does reach the last "
                            "sample — indices run 0 to 999 — but only while the recording is exactly 1000 "
                            "long, and it silently reads the wrong element the day it is not, which is why "
                            "it does not answer the question asked. `v[1000]` and `v[len(v)]` are the same "
                            "mistake written twice: the highest valid index is one less than the length, so "
                            "both raise an IndexError."
                        ),
                    },
                    {
                        "q": "A sine wave swings between −2 V and +2 V. What is its RMS value?",
                        "opts": ["2 V", "about 1.41 V", "about 0.64 V", "0 V, because it is symmetric"],
                        "a": 1,
                        "why": (
                            "About 1.414 V, the peak divided by the square root of 2. RMS is "
                            "`sqrt(mean(v**2))`: squaring removes the sign, so the negative half contributes "
                            "as much as the positive half, and the result is the DC voltage that would heat "
                            "a resistor at the same rate. The *mean* really is 0 V, which is the trap in "
                            "the \"0 V, because it is symmetric\" answer — a mean of zero says nothing "
                            "about how much signal is present."
                        ),
                    },
                ],
            },
            "lab": {
                "title": "Read a log, summarise it, draw it in text",
                "runtime": "python",
                "minutes": 35,
                "brief": r'''
A logger writes readings to a text file, one per line, as `time,value`, with blank
lines and `#` comments scattered through it. Turn that into arrays and say something
about them.

`read_readings(text)` returns two NumPy arrays, the times and the values. Skip blank
lines and any line whose first non-space character is `#`. Split the rest on the
comma and convert both halves with `float`, because everything read from a file
arrives as text.

`summarise(v)` returns a dictionary with keys `"n"`, `"mean"`, `"rms"` and `"peak"`:
the count, the average, `sqrt(mean(v**2))`, and `max(abs(v))`.

`alias_frequency(fsig, fs)` returns the frequency a sine at `fsig` appears to have
after sampling at `fs`. Fold it: take `fsig % fs`, and if that is above `fs / 2`,
subtract it from `fs`.

`sparkline(v, width)` returns a `width`-character string picturing the signal, using
the eight characters of `LEVELS` from lowest to highest. Take `width` samples spread
evenly across the array with `np.linspace(0, len(v) - 1, width)` rounded to whole
indices; scale them so the smallest maps to `LEVELS[0]` and the largest to
`LEVELS[7]`; return `LEVELS[0] * width` when every sample is the same, because a
flat signal has no range to scale by.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

LEVELS = " .:-=+*#"

SAMPLE = """
# t,v -- bench log, 4 readings
0.000,0.00
0.001,0.31

# the logger dropped out here
0.002,0.59
0.003,0.81
"""


def read_readings(text):
    """Parse 'time,value' lines into two float arrays, skipping blanks and comments."""
    times = []
    values = []
    # TODO: loop over text.splitlines(), strip each line, skip the empty ones and
    # the ones starting with '#', split the rest on ',' and convert with float.
    return np.array(times), np.array(values)


def summarise(v):
    """Count, mean, RMS and peak of a signal."""
    v = np.asarray(v, dtype=float)
    # TODO: build the dictionary. RMS is sqrt(mean(v**2)); peak is max(abs(v)).
    return {"n": 0, "mean": 0.0, "rms": 0.0, "peak": 0.0}


def alias_frequency(fsig, fs):
    """The frequency a sine at fsig appears to have once sampled at fs."""
    # TODO: fold fsig about fs/2.
    return 0.0


def sparkline(v, width=40):
    """A width-character picture of v, using LEVELS from lowest to highest."""
    v = np.asarray(v, dtype=float)
    # TODO: pick width evenly spaced samples, scale them onto 0..7, join the chars.
    return ""


if __name__ == "__main__":
    t, v = read_readings(SAMPLE)
    print("samples read:", len(v))
    print("150 Hz sampled at 200 Hz looks like", alias_frequency(150.0, 200.0), "Hz")
    if len(v):
        print(summarise(v))
        print("[" + sparkline(v, 16) + "]")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

LEVELS = " .:-=+*#"

SAMPLE = """
# t,v -- bench log, 4 readings
0.000,0.00
0.001,0.31

# the logger dropped out here
0.002,0.59
0.003,0.81
"""


def read_readings(text):
    """Parse 'time,value' lines into two float arrays, skipping blanks and comments."""
    times = []
    values = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        left, right = line.split(",")
        times.append(float(left))
        values.append(float(right))
    return np.array(times), np.array(values)


def summarise(v):
    """Count, mean, RMS and peak of a signal."""
    v = np.asarray(v, dtype=float)
    return {
        "n": int(v.size),
        "mean": float(np.mean(v)),
        "rms": float(np.sqrt(np.mean(v * v))),
        "peak": float(np.max(np.abs(v))),
    }


def alias_frequency(fsig, fs):
    """The frequency a sine at fsig appears to have once sampled at fs."""
    fa = abs(fsig % fs)
    if fa > fs / 2:
        fa = fs - fa
    return fa


def sparkline(v, width=40):
    """A width-character picture of v, using LEVELS from lowest to highest."""
    v = np.asarray(v, dtype=float)
    idx = np.round(np.linspace(0, v.size - 1, width)).astype(int)
    s = v[idx]
    lo = float(np.min(s))
    hi = float(np.max(s))
    if hi - lo < 1e-15:
        return LEVELS[0] * width
    steps = np.round((s - lo) / (hi - lo) * (len(LEVELS) - 1)).astype(int)
    steps = np.clip(steps, 0, len(LEVELS) - 1)
    return "".join(LEVELS[int(k)] for k in steps)


if __name__ == "__main__":
    t, v = read_readings(SAMPLE)
    print("samples read:", len(v))
    print("150 Hz sampled at 200 Hz looks like", alias_frequency(150.0, 200.0), "Hz")
    if len(v):
        print(summarise(v))
        print("[" + sparkline(v, 16) + "]")
'''}],
                "hints": [
                    "`line.strip()` removes the spaces and the newline, which is what makes `if not line` a reliable test for a blank line and `line.startswith('#')` a reliable test for a comment.",
                    "`left, right = line.split(',')` unpacks the two halves in one step. It raises if a line has the wrong number of commas, which is better than quietly recording nonsense.",
                    "In `summarise`, `v * v` squares element by element, so `np.mean(v * v)` is the mean square and `np.sqrt` of it is the RMS. Wrap each result in `float(...)` so the dictionary holds plain numbers.",
                    "For the sparkline, `(s - lo) / (hi - lo)` puts every sample on 0 to 1; multiplying by 7 and rounding lands it on one of the eight characters. The flat-signal guard has to come first, or you divide by zero.",
                ],
                "tests": [
                    {"name": "the reader skips blanks and comments", "code": r'''
_t, _v = read_readings(SAMPLE)
assert len(_t) == 4 and len(_v) == 4, \
    f"the sample log holds 4 readings, two comments and a blank line; got {len(_v)} readings"
assert abs(float(_t[1]) - 0.001) < 1e-12, f"second time should be 0.001, got {_t[1]}"
assert abs(float(_v[-1]) - 0.81) < 1e-12, f"last value should be 0.81, got {_v[-1]}"
'''},
                    {"name": "the reader returns numbers, not text", "code": r'''
import numpy as np
_t, _v = read_readings(SAMPLE)
assert isinstance(_v, np.ndarray), f"expected a numpy array, got {type(_v).__name__}"
assert _v.dtype.kind == "f", \
    f"the values must be floats, not text; dtype came back as {_v.dtype}"
assert abs(float(np.sum(_v)) - 1.71) < 1e-12, \
    "if the values were still strings this sum would not be possible"
'''},
                    {"name": "summarise measures a sine correctly", "code": r'''
import numpy as np
_fs = 1000.0
_t = np.arange(0, 1.0, 1.0 / _fs)
_sig = np.sin(2 * np.pi * 50 * _t)
_s = summarise(_sig)
assert _s["n"] == 1000, f"expected 1000 samples, got {_s['n']}"
assert abs(_s["mean"]) < 1e-9, f"a whole number of cycles averages to zero, got {_s['mean']}"
assert abs(_s["rms"] - 0.7071067811865476) < 1e-6, \
    f"the RMS of a unit sine is 1/sqrt(2) = 0.7071, got {_s['rms']}"
assert abs(_s["peak"] - 1.0) < 1e-6, f"the peak should be 1.0, got {_s['peak']}"
'''},
                    {"name": "summarise does not confuse mean with peak", "code": r'''
import numpy as np
_s = summarise(np.array([3.0, 3.0, 3.0, -9.0]))
assert abs(_s["mean"] - 0.0) < 1e-12, f"mean of 3, 3, 3, -9 is 0, got {_s['mean']}"
assert abs(_s["peak"] - 9.0) < 1e-12, f"peak is the largest magnitude, 9, got {_s['peak']}"
assert abs(_s["rms"] - 5.196152422706632) < 1e-9, \
    f"RMS is sqrt((9+9+9+81)/4) = 5.196, got {_s['rms']}"
'''},
                    {"name": "aliasing folds about half the sample rate", "code": r'''
assert abs(alias_frequency(30.0, 200.0) - 30.0) < 1e-9, \
    "30 Hz is below the 100 Hz Nyquist limit and comes through untouched"
assert abs(alias_frequency(150.0, 200.0) - 50.0) < 1e-9, \
    "150 Hz sampled at 200 Hz folds to 200 - 150 = 50 Hz"
assert abs(alias_frequency(200.0, 200.0) - 0.0) < 1e-9, \
    "sampling exactly once per cycle records a constant, so the apparent frequency is 0"
assert abs(alias_frequency(410.0, 200.0) - 10.0) < 1e-9, \
    "410 Hz is 2 whole sample rates plus 10 Hz, so it appears at 10 Hz"
'''},
                    {"name": "the sparkline is the right length and the right way up", "code": r'''
import numpy as np
_ramp = sparkline(np.linspace(0.0, 1.0, 100), 16)
assert len(_ramp) == 16, f"asked for 16 characters, got {len(_ramp)}"
assert _ramp[0] == LEVELS[0], f"a rising ramp must start at the lowest level, got {_ramp!r}"
assert _ramp[-1] == LEVELS[-1], f"and end at the highest, got {_ramp!r}"
assert _ramp == "  ..::--==++**##", f"got {_ramp!r}"
'''},
                    {"name": "a flat signal does not divide by zero", "code": r'''
import numpy as np
_flat = sparkline(np.ones(50), 12)
assert _flat == LEVELS[0] * 12, f"a constant signal has no range to scale by; got {_flat!r}"
'''},
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Whole arrays at once",
            "summary": "The loop you would write and the array expression that replaces it compute the same numbers. One of them says what you meant, and one of them the machine can go fast at. They are the same one.",
            "concepts": [
                "*Broadcasting*: an operation between an array and a single number is applied to every element. `v - v.mean()` removes the DC level from a whole recording, and there is no loop anywhere in it.",
                "A comparison on an array gives an array of `True` and `False` — a *mask*, exactly as long as the signal. `v[v > 1.0]` then selects the elements where the mask is true.",
                "Masks combine with `&`, `|` and `~`, and each side needs its own brackets: `(v > lo) & (v < hi)`. The words `and` and `or` do not work on arrays; they raise rather than guess.",
                "`np.count_nonzero(mask)` counts what a mask found and `mask.any()` says whether it found anything. `np.argmax(mask)` gives the index of the first `True` — and 0 when there is none, which is a real index and a real trap.",
                "`np.where(cond, a, b)` chooses element by element, and `np.minimum` / `np.maximum` clamp against a limit. Between them they replace almost every `if` that would have sat inside a loop.",
                "An array is one contiguous block of memory holding one type. The machine fetches memory in lines of 64 bytes — eight doubles — so reading an array in order costs one fetch per eight numbers, and reading it in jumps costs one fetch per number.",
            ],
            "read": [
                {
                    "title": "The loop you would write, and the sentence that replaces it",
                    "minutes": 17,
                    "body": r'''
A logger comes back from a fortnight on a 5 V rail with 1.2 million readings in it,
and the same handful of questions gets asked of every file like it. How far does the
rail wander. How many readings fell outside the band. When did it first come up. What
does it look like with the DC level taken away.

Not one of those is a question about reading number 814 003. Every one of them is a
question about *the recording* — and the recording is the thing you have a single name
for. This module is about writing the question the same way round as you asked it.

## What a loop actually says

Here is the second question, written the way Module 2 taught you to write it.

```python
n_hot = 0
for x in v:
    if x > 5.25:
        n_hot += 1
```

Nothing is wrong with that. It is correct, it is readable, and it runs. But read what
it says out loud: *take the readings one at a time, in this order, keep a running
counter, and here is what to do to the counter at each reading.* Only the last clause
came from the question. The order was never asked about — the count is the same
whichever way you walk the file. The counter was not asked about either; it is a
device you supplied for turning many answers into one.

That machinery has to be supplied again for every question, and each supply is a
fresh chance to get it wrong: initialise in the wrong place, update inside the wrong
branch, divide by `len(v)` where you meant `n_hot`. Four questions become four loops,
twelve lines of bookkeeping wrapped around four lines of arithmetic, and the four
lines that carry the meaning are the ones hardest to see.

What follows is a second way to say the same things, one in which the subject of each
sentence is the recording.

## An operation whose subject is the whole array

An arithmetic operation between an array and a single number is applied to every
element. This is called **broadcasting**, and the picture that goes with it is that
the lone number is stretched — conceptually, not in memory — to the length of the
array, and then the two are combined element against element.

```python
v * 10        # every reading scaled
v - 0.5       # every reading shifted
v * v         # every reading squared, against a partner of the same length
```

The most useful instance in the whole module is removing a DC level:

```text
    v          = [4.90, 5.10, 5.00, 5.20, 4.80, 5.00]
    sum        = 30.00
    v.mean()   = 30.00 / 6 = 5.00
    v - 5.00   = [-0.10, 0.10, 0.00, 0.20, -0.20, 0.00]
```

Written as `v - v.mean()`, and printed by NumPy as
`[-0.1  0.1  0.   0.2 -0.2  0. ]`. Two things are worth noticing before moving on.

The first is that `v.mean()` runs to completion *before* the subtraction starts: it is
one number, produced by one full sweep of the data, and then a second sweep does the
subtracting. The expression is two passes over the recording, written on one line.
That fact comes back in the derivation later in this module, where one of the two
passes gets removed and something else breaks.

The second is that the order matters and the failure is silent. `v.mean() - v` centres
the signal *and* turns it upside down, and at this scale no plot will show you which
one you have.

## A comparison is an operation too

`v > 5.25` broadcasts in exactly the way `v - 0.5` does, and gives back an array of
the same length holding `True` and `False`. That array is a **mask**. It is not a
count and it is not a selection; it is a verdict per sample, and everything else is
built on top of it.

Twelve readings from that 5 V rail, tested against a band of 4.75 V to 5.25 V,
inclusive at both ends:

```text
    reading   >= 4.75 ?   <= 5.25 ?   mask
     4.98        yes         yes      True
     5.31        yes         no       False
     4.75        yes  (on the limit)  True
     5.02        yes         yes      True
     4.61        no          yes      False
     5.25        yes  (on the limit)  True
     5.44        yes         no       False
     4.89        yes         yes      True
     5.09        yes         yes      True
     4.70        no          yes      False
     5.26        yes         no       False
     4.95        yes         yes      True
                                      ----------------
                                      True count:    7
```

In code that entire table is one line, plus one line for each question you want to ask
of it:

```python
ok = (v >= 4.75) & (v <= 5.25)
np.count_nonzero(ok)    # 7       how many
ok.mean()               # 0.5833  what fraction
ok.any()                # True    was there any at all
ok.all()                # False   were they all
```

`ok.mean()` deserves a second look. `True` counts as 1 and `False` as 0, so the mean
of a mask *is* the pass fraction: 7/12 = 0.5833, a 58.3% yield, with no separate
counter and no separate division to get wrong.

## Four different questions about one mask

Given a mask there are four distinct things you might want, and they come back in four
different shapes. Choosing the wrong one is the commonest muddle in early NumPy.

- **How many.** `np.count_nonzero(ok)` gives 7 — a single integer.
- **Which values.** `v[ok]` gives `array([4.98, 4.75, 5.02, 5.25, 4.89, 5.09, 4.95])`,
  a *new, shorter* array holding only the readings that passed. It is a copy, and the
  correspondence with the time axis is gone: element 3 of the result is not sample 3
  of the recording, and nothing in the result records which sample it was.
- **Which positions.** `np.nonzero(ok)[0]` gives `array([0, 2, 3, 5, 7, 8, 11])` — the
  indices themselves, which is what you need when the timing matters.
- **What each element should become.** `np.where(ok, v, 5.00)` chooses element by
  element and returns something *as long as the original*: the reading where it
  passed, the nominal where it did not. `np.where` is the `if` that used to sit inside
  the loop, lifted out to the level of the whole array.

`np.minimum` and `np.maximum` are the same idea with the condition built in.
`np.minimum(v, 5.25)` is `np.where(v < 5.25, v, 5.25)` written shorter: an array as
long as `v` with nothing in it above 5.25. Note the two letters that separate it from
`np.min(v)`, which collapses the whole array to its single smallest element. One
transforms and one reduces, and confusing them produces an error two lines later, in
the line that tried to index the number you thought was an array.

## Worked example: when did the rail come up

A 3.3 V rail is logged through power-up at 10 kHz, so the samples are 100 µs apart.
The question is when it first got above 3.0 V.

```text
    index      0      1      2      3      4      5      6      7
    volts    0.02   0.44   1.31   2.28   2.97   3.14   3.28   3.30
    > 3.0 ?    F      F      F      F      F      T      T      T
```

```python
hot = v > 3.0
i   = int(np.argmax(hot))      # 5
t   = i / 10_000               # 5 / 10000 = 0.0005 s = 500 us
```

`np.argmax` reports the position of the largest element, and in a mask the largest
element is `True`; ties go to the earliest, so the answer is the index of the first
crossing. Five samples at 100 µs each puts it at 500 µs — strictly, at or before
500 µs, since all the file proves is that the rail was under 3.0 V at 400 µs and over
it at 500 µs.

Now run the identical code over a board whose rail never came up at all, every sample
sitting at 0.02 V:

```text
    hot     = [F, F, F, F, F, F, F, F]
    argmax  = 0
    t       = 0 / 10000 = 0 s
```

The report says the rail crossed 3.0 V at time zero. Nothing raised, nothing printed,
and the number is not absurd on its face — a rail that was already up before the
recording started would give exactly this. `argmax` is not broken: every element of an
all-`False` mask is equally large and the earliest wins, so 0 is the correct answer to
the question `argmax` was asked. It was the wrong question. The guard is one line and
it is not optional:

```python
i = int(np.argmax(hot)) if hot.any() else -1
```

## The mistake everybody makes once

Sooner or later you will write the band test the way English says it:

```python
if (v >= 4.75) and (v <= 5.25):
```

and get `ValueError: The truth value of an array with more than one element is
ambiguous. Use a.any() or a.all()`. The keyword `and` needs each side to be a single
true-or-false value, and a mask of twelve booleans is neither true nor false as a
whole. NumPy will not guess whether you meant *any of them* or *all of them*, so it
refuses to guess at all. The element-by-element versions are `&`, `|` and `~`.

It is tempting because it is the same line that was right in Module 2, where `v` held
one reading. The type changed underneath the sentence and the sentence did not.

Its close relative is dropping the brackets:

```python
ok = v >= 4.75 & v <= 5.25          # TypeError, from a line that looks fine
```

`&` binds *more tightly* than `>=`, so Python evaluates `4.75 & v` first, asks for a
bitwise AND of two floats, and reports `ufunc 'bitwise_and' not supported for the
input types`. The error names an operation you never wrote, on operands you never
paired. Every comparison joined with `&` gets its own brackets, every time.

## Where element-by-element thinking stops

All of this rests on one assumption, worth stating plainly so that you can notice when
it fails: **the answer for element $i$ must not depend on the answer for element
$i-1$.** Scaling, shifting, comparing, clamping and choosing all satisfy it. A good
deal of real signal processing does not.

The standard counter-example is a single-pole digital filter, the discrete cousin of
the RC low-pass from Module 4:

$$y_i = y_{i-1} + \alpha\,(x_i - y_{i-1})$$

Every output needs the previous output, which needs the one before it, back to the
start. There is no expression over `x` alone that broadcasting can evaluate, because
the calculation is genuinely sequential: element 500 000 cannot begin until element
499 999 exists. Writing that as a loop is not a failure of imagination.

Three things replace vectorising when you hit this.

- **A prefix scan, when one exists.** Some recurrences have closed forms NumPy
  computes in a single pass: `np.cumsum` for running totals, `np.cumprod` for running
  products, `np.diff` for the difference between neighbours. The moving average in
  this module's lab is exactly that trick — a windowed sum looks sequential and is
  not, because the sum over a window is the difference of two cumulative sums.
- **Somebody else's compiled loop.** `np.convolve`, and `scipy.signal.lfilter` for the
  filter above, are the sequential loop written in C. The loop still happens; it stops
  happening in the interpreter.
- **Your own loop, kept.** If the recurrence is genuinely serial and runs a thousand
  times rather than a million, the loop is the right code, and rewriting it into
  something clever is one of the ways correct programs become wrong ones.

One last trap on the way out. A mask indexes an array only if the two are the same
length. `v[t > 0.5]`, with `t` the time axis and `v` the voltages, is an entirely
ordinary thing to want, and it works exactly as long as `t` and `v` came from the same
recording. Build one from a slice and the other from the whole file and you get
`IndexError: boolean index did not match indexed array` — a good error to get, because
it is the one place NumPy checks a correspondence you have been assuming all along.
''',
                },
                {
                    "title": "Why the array version is also the fast one",
                    "minutes": 16,
                    "body": r'''
Two programs, the same arithmetic, both correct. A million floats, each one doubled:

```text
    [2.0 * x for x in lst]      43.3 ms        43 ns per element
    2.0 * a                      2.5 ms        2.5 ns per element
```

Seventeen times, measured on the machine this was written on, for a job that is one
multiply per number. "NumPy is written in C" is true and does not explain it, because
the list comprehension is also running compiled code for the multiply itself. The
difference is in everything *around* the multiply, and knowing where it goes is what
lets you predict which rewrites will help and which will do nothing whatever.

## What a list of floats is in memory

A Python list of a million floats is not a million floats. It is a million *pointers*
laid end to end — 8.4 MB of them — and each pointer leads somewhere else in memory to
a `float` object of 24 bytes holding a type tag, a reference count, and eight bytes of
actual number. Call it 32 MB in total, and scattered: two readings adjacent in the
list are objects that may sit anywhere at all.

A NumPy array of a million `float64` is 8 MB. One block. No pointers, no objects, no
per-element tags — the type is recorded once, for the array, because every element has
the same one.

Now price the loop body. For each element the interpreter fetches a pointer, follows
it, checks that the thing at the far end really is a number, unboxes eight bytes, does
one multiply, allocates a *new* float object to hold the result, and appends a pointer
to that. The multiply is one machine instruction. Everything else is several dozen,
and the pointer-following is a memory access to somewhere the hardware could not
predict. The array expression pays the interpreter once, for the whole line, and then
runs a tight compiled loop over one contiguous block.

## Memory arrives in lines, not in numbers

The second half of the story is what the sandbox in this module is about, and it has
nothing to do with Python.

The machine does not fetch bytes; it fetches **cache lines**, 64 bytes at a time, into
a small fast memory sitting in front of the main one. Sixty-four bytes is eight
`float64`. Walk an array in order and the first element of each line pays for the trip
while the next seven arrive free: one slow access in eight, a miss rate of 12.5%. Walk
the same *number* of elements with 64 bytes between them and every access pays full
price — the same lines are fetched, and seven eighths of each one is thrown away.

That is the whole content of the sandbox: 32 KB of data through an 8 KB cache reads
12.5% misses at a stride of 8 bytes and 100% at a stride of 64, for arithmetic that is
identical in both cases. Contiguity is not a detail of the implementation, then. It is
the property that makes the hardware's own prefetcher work, and an array has it by
construction while a list of boxed objects cannot.

## Worked example: counting what an expression costs

Once you know that traffic is what matters, you can price a line of NumPy before
running it. Take four million samples of `float64` — 32 MB — and the standard
deviation written the obvious way:

```python
sigma = np.sqrt(np.mean(np.square(v - v.mean())))
```

Each intermediate array is a real allocation: written to memory as it is produced,
read back as it is consumed. Count every element that crosses the bus.

```text
    v.mean()            read v                    32 MB
    v - mu              read v, write d      32 + 32 MB
    np.square(d)        read d, write s      32 + 32 MB
    np.mean(s)          read s                    32 MB
                                             -----------
    total                                       192 MB
```

Six traversals of the data for one number out. On a machine sustaining 12 GB/s that is
$192\times10^{6} / 12\times10^{9} = 16$ ms, and the arithmetic — four million
subtractions and four million multiplies — is nowhere near enough work to hide behind.
The calculation is **memory-bound**: for most of those sixteen milliseconds the
processor is waiting.

Which immediately tells you what a rewrite is worth. Anything that reduces the
arithmetic is worth nothing. Anything that removes a traversal is worth 2.67 ms. Do
the centring in place and replace the square with a dot product:

```python
mu = v.mean()                             # read v                 32 MB
v -= mu                                   # read v, write v   32 + 32 MB
sigma = np.sqrt(np.dot(v, v) / v.size)    # read v                 32 MB
                                          # total                 128 MB
```

128 MB, 10.7 ms, a third off — and `v` has been modified, which may or may not be
acceptable in the surrounding program. The floor for any method that must look at
every sample twice, once to find the mean and once to measure the spread, is 64 MB or
5.3 ms. No cleverness in the arithmetic gets below the cost of reading the data, and
knowing that number is how you know when to stop optimising.

## Views and copies, and the aliasing that follows

A basic slice does **not** copy. `w = v[100:200]` builds a new array object pointing
into the same memory with a different start and length: no traffic, no allocation,
effectively instant. That is a large part of why slicing a signal is cheap enough to
do inside a loop over windows.

The consequence is that `w` and `v` are one set of numbers under two names:

```python
w = v[100:200]
w *= 0            # v[100:200] is now zero as well
```

This catches people because a *list* slice copies, so the identical line on a list is
harmless. When you need independence, ask for it: `w = v[100:200].copy()`.

Strided slices are views too, and the stride is where the traffic hides. `v[::2]` on
those four million samples is an array of two million values occupying no new memory —
but summing it touches every 64-byte line of the original, because each line holds
four of the elements you asked for. Half the data, all of the traffic, and a
measurement that shows no speed-up at all.

Boolean indexing is the opposite case: `v[v > 1.0]` cannot be a view, because the
elements it wants are not evenly spaced. It allocates a new array and copies the hits
into it. That is fine and usually what you want — but note that a mask used for
*selection* costs memory proportional to how many samples passed, while the same mask
used for *counting* costs none.

## Where "vectorise it" stops being advice

**Small arrays.** Every NumPy call carries a fixed overhead — argument parsing, shape
and type negotiation, allocating the output — of roughly half a microsecond. On ten
elements, measured on the same machine:

```text
    [2.0 * x for x in s]     0.31 us
    2.0 * sa                 0.45 us
```

The array version is *slower*, and stays slower until the arrays are a few hundred
elements long. Vectorising a six-element parts calculation buys nothing; do it because
it reads better, if it does, and not for a speed-up that is not there.

**Memory rather than time.** Every temporary in a chained expression is a full-size
allocation. The six-traversal standard deviation above needs three 32 MB arrays alive
at once. Scale the recording to 2 GB and the same line wants 6 GB of RAM and may
simply fail, on a machine that could have processed it a chunk at a time all
afternoon. The loop that was slower never had this problem.

**The answer is not bit-identical.** A sum taken in a different order rounds
differently. `np.sum` does not add left to right; it uses *pairwise* summation,
splitting the array into blocks and adding the partial sums, which stops the running
total from growing large enough to swallow the small values still to come. On a
million `float32` values that came out as:

```text
    exact sum (in float64)     499797.00461
    naive loop (float32)       499805.68750       error 8.68
    np.sum (float32)           499797.00000       error 0.0046
```

The vectorised answer differs from the loop's, and is nearly two thousand times closer
to the truth. That is the pleasant direction for a difference to run, but it is still
a difference, and a test demanding that the two agree to the last bit will fail for a
reason that has nothing to do with either being wrong.

**And the honest one.** A loop that is clear and runs a thousand times is finished
code. The reason to reach for the array expression is that it says what you meant with
less machinery wrapped around it; the speed is a consequence of the same property,
that you told the machine about the whole recording at once instead of about one
reading at a time, a million times over.
''',
                },
            ],
            "numeric": [
                {
                    "title": "How many readings the band keeps",
                    "minutes": 5,
                    "brief": r'''
Twelve readings from a 5 V rail, and one mask. The band runs from 4.75 V to 5.25 V and
both ends are inside it — that is what `>=` and `<=` mean — and two of the readings
sit exactly on a limit.

Count the `True` entries the mask would hold.
''',
                    "prompt": "How many of the twelve readings satisfy `(v >= 4.75) & (v <= 5.25)`?",
                    "figure": r'''
```python
import numpy as np

v = np.array([4.98, 5.31, 4.75, 5.02, 4.61, 5.25,
              5.44, 4.89, 5.09, 4.70, 5.26, 4.95])

ok = (v >= 4.75) & (v <= 5.25)
print(np.count_nonzero(ok))
```
''',
                    "given": [
                        {"label": "Readings", "value": "12"},
                        {"label": "Band", "value": "4.75 V to 5.25 V, both ends included"},
                    ],
                    "note": "A count, from 0 to 12. Work down the list; nothing here needs a calculator.",
                    "hint": "Reject anything below 4.75 or above 5.25. A reading equal to a limit is inside, because both comparisons are the *or equal to* kind.",
                    "wrong": "5 comes from reading `>=` and `<=` as strict, which throws out 4.75 and 5.25 — the two readings sitting precisely on the limits. 8 comes from letting 5.26 through, which is over the top by a hundredth of a volt and is a fail like any other.",
                    "answer": 7.0,
                    "tol": 0.01,
                    "unit": "readings",
                    "why": r'''
```text
    4.98   in                  5.44   over
    5.31   over                4.89   in
    4.75   in, on the limit    5.09   in
    5.02   in                  4.70   under
    4.61   under               5.26   over
    5.25   in, on the limit    4.95   in
                                      ---------------
                                      7 True
```

Seven. The mask itself is
`[True, False, True, True, False, True, False, True, True, False, False, True]` —
twelve verdicts, one per reading, exactly as long as the signal it came from. That
length is what makes it usable as an index: `v[ok]` returns the seven readings, and
`ok.mean()` returns 0.5833, the pass fraction, because `True` averages as 1.

The two readings on the limits are the ones worth arguing about, and the argument is
settled by the specification rather than by the code: a part sitting exactly on its
published limit is in specification, so `>=` and `<=` are the comparisons that match
the intent. Whether the machine agrees is a separate question — neither 4.75 nor 5.25
is exactly representable in binary, and the test succeeds here only because the
literal in the array and the literal in the comparison round to the same double.
Replace either with the result of a calculation and the verdict can flip, which is
Module 1's lesson arriving in a new costume.
''',
                },
                {
                    "title": "How long the smoothed record is",
                    "minutes": 6,
                    "brief": r'''
A 4096-sample capture. The stretches at each end are the trigger settling and get
thrown away with a slice; what is left is smoothed with a 64-sample moving average —
the cumulative-sum version from this module's lab, which produces one output per
window that fits entirely inside the input.

Two fenceposts, one after the other.
''',
                    "prompt": "How many samples does `smooth` end up holding?",
                    "figure": r'''
```python
import numpy as np

v = read_capture()          # 4096 samples, float64
core = v[512:3584]          # drop the settling at each end

n = 64
c = np.concatenate(([0.0], np.cumsum(core)))
smooth = (c[n:] - c[:-n]) / n

print(smooth.size)
```
''',
                    "given": [
                        {"label": "Capture", "value": "4096 samples"},
                        {"label": "Slice", "value": "[512:3584]"},
                        {"label": "Window", "value": "64 samples"},
                    ],
                    "note": "Do the slice first and the window second. A slice stops before its second index; a window of $n$ over $m$ samples gives $m - n + 1$ outputs.",
                    "hint": "$3584 - 512$ is the length of `core`. Then subtract the window and add one, because the number of positions a 64-long window can occupy in a 3072-long array counts places, not gaps.",
                    "wrong": "3008 is the fencepost lost: a 64-sample window fits into 3072 samples in 3009 places, not 3008 — put a 2-sample window on a 3-sample array and count them. 4033 is the window applied to the whole capture, with the slice forgotten.",
                    "answer": 3009.0,
                    "tol": 0.01,
                    "unit": "samples",
                    "why": r'''
```text
    core length     3584 - 512          = 3072 samples
    windows of 64   3072 - 64 + 1       = 3009 outputs
```

Both steps are fenceposts, and they point in opposite directions, which is why doing
them in one go so often lands one short.

A slice `v[a:b]` holds $b - a$ elements, because the stop index is the first one *not*
taken. That convention is what lets `v[:512]` and `v[512:]` fit together with no
sample counted twice and none missed.

A window is the other way round. The first 64-sample window covers indices 0 to 63 and
the last covers 3008 to 3071, so the number of starting positions, counting both ends,
is $3008 - 0 + 1 = 3009$. Gaps give 3008; places give 3009; a window occupies places.

The array arithmetic in the listing agrees, which is a useful way to check yourself.
`np.cumsum(core)` has 3072 entries, so `c` has 3073 after the leading zero; `c[64:]`
therefore has $3073 - 64 = 3009$ elements, and `c[:-64]` has the same. Every window's
sum is a single subtraction of two cumulative totals, so the whole moving average is
one pass over the data rather than 3009 passes over 64 samples each — which is what
makes a calculation that looks sequential vectorisable at all.
''',
                },
                {
                    "title": "What the expression asks of the memory system",
                    "minutes": 9,
                    "brief": r'''
Four million samples of `float64`, and one line that computes their standard
deviation. Every intermediate array in that line is a real allocation: written to
memory as it is produced, read back as it is consumed.

Count the bytes that cross the bus, then turn them into a time. Take the machine to
sustain 12 GB/s, and take the arithmetic to hide entirely behind the memory traffic —
which is the point of the exercise.
''',
                    "prompt": "How long does the memory traffic alone take? Answer in **milliseconds**.",
                    "figure": r'''
```python
import numpy as np

v = np.empty(4_000_000)         # float64: 8 bytes each
...
sigma = np.sqrt(np.mean(np.square(v - v.mean())))

#  mu = v.mean()          reads v
#  d  = v - mu            reads v, writes a new array
#  s  = np.square(d)      reads d, writes another new array
#       np.mean(s)        reads s
```
''',
                    "given": [
                        {"label": "Samples", "value": "4 000 000 float64"},
                        {"label": "One traversal", "value": "32 MB"},
                        {"label": "Bandwidth", "value": "12 GB/s"},
                        {"label": "Answer wanted in", "value": "ms"},
                    ],
                    "note": "Count every array element read and every element written, once per operation. Use 1 MB = $10^6$ bytes and 1 GB = $10^9$ bytes.",
                    "hint": "Four operations, six traversals — two of them read one array and write another. Total bytes divided by bytes per second is seconds.",
                    "wrong": "2.67 ms is a single traversal: what the line would cost if the whole chain were fused into one pass. That is the right floor to compare against and is not what NumPy did. 13.3 ms is five traversals, which is what you get by forgetting that `v.mean()` needs a full pass of its own before the subtraction can start.",
                    "answer": 16.0,
                    "tol": 0.4,
                    "unit": "ms",
                    "why": r'''
```text
    array size          4e6 * 8 bytes               =  32 MB

    v.mean()            read v                         32 MB
    v - mu              read v, write d           32 + 32 MB
    np.square(d)        read d, write s           32 + 32 MB
    np.mean(s)          read s                         32 MB
                                                  -----------
    total traffic                                     192 MB

    time                192e6 / 12e9                = 16.0 ms
```

Six traversals to produce one number. The arithmetic is four million subtractions and
four million multiplies, of order a millisecond of work on any modern core, so for
roughly fifteen of those sixteen milliseconds the processor is waiting on memory. The
calculation is memory-bound, and that one word tells you which rewrites are worth
trying.

Rewrites that reduce arithmetic will do nothing at all. Rewrites that remove a
traversal are worth 2.67 ms each. Centring in place and replacing the square with a
dot product gets it to four traversals, 128 MB and 10.7 ms; and the floor for any
method that must see every sample twice — once to find the mean, once to measure the
spread — is 64 MB, or 5.3 ms.

The comparison that matters, though, is not against a better NumPy expression. The
Python loop doing the same arithmetic moves the same 32 MB of data and takes of order
a second, because it is not paying for memory at all: it is paying for four million
interpreter steps. The array version is within a factor of three of what the hardware
can physically do. The loop is two orders of magnitude away from it, and no amount of
tuning the loop closes that, because the thing being paid for is not the work.
''',
                },
                {
                    "title": "When the rail actually crossed 3 V",
                    "minutes": 10,
                    "brief": r'''
A 5 V rail is logged through power-up at 50 kHz. The guarded threshold search from
this module reports the index of the first sample strictly above 3.00 V — but the
crossing did not happen at a sample. It happened somewhere in the gap between the last
sample below the threshold and the first sample above it.

Take the rail to rise in a straight line between those two samples, and find the
moment it passed 3.00 V, measured from sample 0 at $t = 0$.
''',
                    "prompt": "At what time did the rail pass 3.00 V? Answer in **microseconds**.",
                    "figure": r'''
```text
    fs = 50 kHz

    index      0      1      2      3      4      5      6      7
    volts    0.01   0.09   0.68   2.61   3.42   3.91   4.02   4.05
                                    ^      ^
                                    |      +--- first sample above 3.00 V
                                    +---------- last sample below it
```
''',
                    "given": [
                        {"label": "Sample rate", "value": "50 kHz"},
                        {"label": "Threshold", "value": "3.00 V"},
                        {"label": "Straddling samples", "value": "2.61 V and 3.42 V"},
                        {"label": "Answer wanted in", "value": "µs"},
                    ],
                    "note": "Three steps: the sample interval, the fraction of the way across the gap, and the two of them together as a time from zero.",
                    "hint": "The interval is $1/f_s$. The fraction is (threshold − lower) / (upper − lower), which is how far along the straight line between the two samples the threshold sits. The crossing is at (lower index + fraction) intervals.",
                    "wrong": "80 µs is the index the search returns times the interval — the first sample *after* the crossing, late by up to a whole interval, and what an unconsidered `argmax` reports. 60 µs is the sample before, early by the same amount. Both are defensible as bounds; neither answers the question asked.",
                    "answer": 69.63,
                    "tol": 0.3,
                    "unit": "µs",
                    "why": r'''
```text
    sample interval   1 / 50000                    = 20 us
    gap in volts      3.42 - 2.61                  = 0.81 V
    climb needed      3.00 - 2.61                  = 0.39 V
    fraction across   0.39 / 0.81                  = 0.481481
    crossing index    3 + 0.481481                 = 3.481481
    crossing time     3.481481 * 20 us             = 69.63 us
```

The index a mask gives you is an integer and the answer is not, which is the whole
point of the question. `np.argmax(v > 3.0)` returns 4; sample 4 sits at 80 µs; and
80 µs is not when the rail crossed 3 V, it is when the logger next looked. With a
20 µs interval that error is up to 20 µs — 25% of the answer here, and enough to fail
a power-sequencing specification that the board actually meets.

Two things this rests on, both worth being explicit about.

The first is the straight line. Nothing was recorded between two adjacent samples, so
the interpolation is an assumption rather than a measurement. It is a good assumption
when the signal moves by a small fraction of its range per sample and a bad one at a
sharp edge: a rail that snapped up in 2 µs somewhere inside that gap produces exactly
the same two readings, and the linear estimate is then simply wrong. Sampling faster
improves the assumption; nothing in the file you already have can check it.

The second is the guard. This calculation reads samples 3 and 4 out of the array, and
if the search never found a crossing then `argmax` returned 0, index $-1$ is the
sample at the far end of the recording, and the interpolation cheerfully produces a
time out of two unrelated readings. `if hot.any()` belongs before all of this
arithmetic, not after it.
''',
                },
                {
                    "title": "The ripple, from two running totals",
                    "minutes": 11,
                    "brief": r'''
A rail monitor's firmware has no room to keep the samples. It keeps two running totals
instead — the sum of the readings and the sum of their squares — and prints them with
the sample count at the end of the run.

That is enough. The DC level and the size of the ripple are both recoverable from
those three numbers, through the identity this module derives.

Report the RMS of the ripple: the AC part, with the DC level removed.
''',
                    "prompt": "What is the RMS of the ripple on this rail? Answer in **millivolts**.",
                    "figure": r'''
```text
    run summary, rail monitor

    N   (samples)          =      200 000
    S1  (sum of v)         =      960 000     V
    S2  (sum of v squared) =    4 608 180     V^2

    no samples retained
```
''',
                    "given": [
                        {"label": "Samples", "value": "200 000"},
                        {"label": "Sum of readings", "value": "960 000 V"},
                        {"label": "Sum of squares", "value": "4 608 180 V²"},
                        {"label": "Answer wanted in", "value": "mV"},
                    ],
                    "note": "The mean is $S_1/N$ and the mean square is $S_2/N$. The variance is the mean square minus the square of the mean; the ripple's RMS is its square root.",
                    "hint": "$\\sigma^2 = \\overline{v^2} - \\bar{v}^2$. Both of those terms are close to 23, and the answer lives in the fourth decimal place of their difference — carry every digit through.",
                    "wrong": "4800 mV is the DC level, $S_1/N$, which is the other thing these totals tell you. 4800.09 mV is $\\sqrt{S_2/N}$, the total RMS of the rail including its DC — what a true-RMS meter would read, and a tempting near-miss because it is a correct answer to a different question.",
                    "answer": 30.0,
                    "tol": 0.5,
                    "unit": "mV",
                    "why": r'''
```text
    mean              S1 / N   = 960000 / 200000        =  4.8000 V
    mean square       S2 / N   = 4608180 / 200000       = 23.0409 V^2
    square of mean    4.8^2                             = 23.0400 V^2
    variance          23.0409 - 23.0400                 =  0.0009 V^2
    ripple RMS        sqrt(0.0009)                      =  0.0300 V = 30.0 mV
```

A 4.8 V rail with 30 mV of ripple on it, recovered from three integers and no samples
at all.

Look hard at the fourth line, though, because it is the reason this method has a
reputation. Two numbers agreeing to five significant figures are subtracted, and
everything that survives lives in the digits they did not share. Here four of the
sixteen digits a `float64` carries are destroyed and twelve remain, which is plenty.
Run the same firmware on a 230 V mains monitor with the same 30 mV of ripple,
accumulating in `float32`, and the two terms become 52900.0039 and 52900.0000: their
difference is one single rounding step at that magnitude, and the answer comes back as
62.5 mV, more than twice the truth, with no warning of any kind.

That is why the two-pass form — `v - v.mean()`, then the mean of the squares — is what
`np.var` actually does. It costs a second traversal of the data and it never cancels,
because the numbers being squared are already the small quantities you are trying to
measure. The identity above is for when you cannot keep the data; and when you use it,
keep the accumulators in `float64` and know what the ratio of DC to ripple is doing to
your digits.
''',
                },
            ],
            "derive": {
                "title": "One pass over the data instead of two",
                "minutes": 14,
                "vars": ["N", "S_1", "S_2", "mu", "sigma", "x_i", "x_rms"],
                "brief": r'''
Removing a DC level with `v - v.mean()` reads the recording twice: once to find the
mean, once to subtract it. A logger with no room to store the samples cannot read them
twice at all. Both situations are answered by the same piece of algebra, which turns
the spread of a signal into something computable from two running totals.

Write $S_1$ for the sum of the $N$ readings and $S_2$ for the sum of their squares,
$\mu$ for the mean, and $\sigma$ for the standard deviation — the RMS of the signal
once its mean has been taken away. Answers are expressions in those symbols.
''',
                "steps": [
                    {
                        "prompt": "Start with the easy one. Write the mean $\\mu$ in terms of $S_1$ and $N$.",
                        "answer": "\\frac{S_1}{N}",
                        "placeholder": "a single fraction",
                        "hint": "The mean is the total divided by how many there were, and $S_1$ is the total.",
                        "deconstruct": [
                            "$S_1$ is defined as $x_0 + x_1 + \\dots + x_{N-1}$.",
                            "The mean of $N$ numbers is their sum over $N$.",
                            "So $\\mu = S_1/N$. This is the only place $S_1$ is needed on its own, and it is why firmware keeping a single running total already knows the DC level.",
                        ],
                    },
                    {
                        "prompt": "The quantity wanted is the average of $(x_i - \\mu)^2$. Expand that square, leaving it in terms of $x_i$ and $\\mu$.",
                        "answer": "x_i^2 - 2 \\mu x_i + \\mu^2",
                        "placeholder": "three terms",
                        "hint": "$(a-b)^2 = a^2 - 2ab + b^2$, with $a = x_i$ and $b = \\mu$.",
                        "deconstruct": [
                            "Multiply it out: $(x_i - \\mu)(x_i - \\mu)$.",
                            "That gives $x_i^2 - \\mu x_i - x_i\\mu + \\mu^2$.",
                            "The two middle terms are the same, so the expansion is $x_i^2 - 2\\mu x_i + \\mu^2$. Nothing has been approximated here, and nothing will be.",
                        ],
                    },
                    {
                        "prompt": "Average that over all $N$ samples, term by term. The average of $x_i^2$ is $S_2/N$ and the average of $x_i$ is $S_1/N$. Write the result in terms of $S_1$, $S_2$, $N$ and $\\mu$.",
                        "answer": "\\frac{S_2}{N} - \\frac{2 \\mu S_1}{N} + \\mu^2",
                        "placeholder": "three terms again",
                        "hint": "Averaging is linear, so average the three terms separately. $\\mu$ is constant across the sum, so it comes out of the middle term untouched, and the average of a constant is that constant.",
                        "deconstruct": [
                            "The first term: the average of $x_i^2$ is $S_2/N$, straight from the definition of $S_2$.",
                            "The middle term: $2\\mu$ does not depend on $i$, so its average is $2\\mu$ times the average of $x_i$, which is $2\\mu S_1/N$.",
                            "The last term: adding $\\mu^2$ to itself $N$ times and dividing by $N$ gives $\\mu^2$ back.",
                        ],
                    },
                    {
                        "prompt": "Now use the first step to remove $\\mu$ entirely. Write $\\sigma^2$ in terms of $S_1$, $S_2$ and $N$ only.",
                        "answer": "\\frac{S_2}{N} - \\frac{S_1^2}{N^2}",
                        "placeholder": "two terms, no mu",
                        "hint": "Substitute $\\mu = S_1/N$ in both places it still appears. The middle term becomes $2S_1^2/N^2$ and the last becomes $S_1^2/N^2$, so two of the three collapse into one.",
                        "deconstruct": [
                            "Middle term: $2\\mu S_1/N = 2(S_1/N)(S_1/N) = 2S_1^2/N^2$.",
                            "Last term: $\\mu^2 = S_1^2/N^2$.",
                            "So the whole thing is $S_2/N - 2S_1^2/N^2 + S_1^2/N^2 = S_2/N - S_1^2/N^2$. Two running totals and a count, and the spread of the signal falls out — which is the entire reason the identity is worth having.",
                        ],
                    },
                    {
                        "prompt": "Read the same identity the other way round. Since $\\sigma^2$ is the mean square minus $\\mu^2$, the mean square is $\\mu^2 + \\sigma^2$. Write the total RMS of the signal, $x_{rms}$, in terms of $\\mu$ and $\\sigma$.",
                        "answer": "\\sqrt{\\mu^2 + \\sigma^2}",
                        "placeholder": "a root over a sum",
                        "hint": "RMS is the square root of the mean square, and the mean square has just been written as a sum of two pieces.",
                        "deconstruct": [
                            "Rearranging the identity: the mean square equals $\\mu^2 + \\sigma^2$.",
                            "$x_{rms}$ is by definition the square root of the mean square.",
                            "So $x_{rms} = \\sqrt{\\mu^2 + \\sigma^2}$ — the quadrature rule the previous module derived for a DC level plus a sine, arrived at here without assuming anything at all about the shape of the ripple.",
                        ],
                    },
                    {
                        "prompt": "A true-RMS meter reports $x_{rms}$ and a DC meter reports $\\mu$. Write the ripple's RMS in terms of those two readings.",
                        "answer": "\\sqrt{x_{rms}^2 - \\mu^2}",
                        "placeholder": "a root over a difference",
                        "hint": "Square the previous answer, move $\\mu^2$ to the other side, and take the root of what is left.",
                        "deconstruct": [
                            "From $x_{rms}^2 = \\mu^2 + \\sigma^2$, subtract $\\mu^2$ from both sides.",
                            "That leaves $\\sigma^2 = x_{rms}^2 - \\mu^2$.",
                            "So $\\sigma = \\sqrt{x_{rms}^2 - \\mu^2}$: two bench meters on the same wire give you the ripple you would otherwise need a scope to see — provided the two readings differ by enough digits to leave something behind.",
                        ],
                    },
                ],
                "closing": r'''
The identity is exact. Every step above is ordinary algebra with no approximation
anywhere, and in real arithmetic $S_2/N - S_1^2/N^2$ and the average of
$(x_i - \mu)^2$ are the same number.

In floating point they are not, and the gap is not small.

**Why the one-pass form is dangerous.** Look at what the final subtraction does on a
real rail. A 4.8 V supply with 30 mV of ripple has a mean square of 23.0409 and a
squared mean of 23.0400. Those agree to five significant figures, so the subtraction
throws five figures away and the answer is assembled from whatever was left. In
`float64` that costs four digits out of sixteen and nobody notices. Run the same
firmware on a 230 V mains monitor with the same 30 mV of ripple, accumulating in
`float32`:

```text
    S2 / N      =  52900.00390625
    mu^2        =  52900.0
    difference  =      0.00390625     <- exactly one ulp at this magnitude
    sigma       =      0.0625 V       (the truth is 0.0300 V)
```

The subtraction did not return a small number. It returned a *rounding step*, and the
square root of a rounding step is 62.5 mV — more than twice the real ripple, with
nothing anywhere in the program to indicate that something has gone wrong. Push it a
little further, with a smaller ripple or a larger rail, and the difference comes out
as exactly zero, or negative, and `np.sqrt` returns `nan` from a calculation that was
algebraically incapable of producing one.

**What replaces it.** Three things, in order of preference.

*Two passes, when you have the data.* `v - v.mean()`, then the mean of the squares.
Nothing cancels, because the numbers being squared are already the small quantities
you are trying to measure. On the same `float32` mains data this returns 0.0300 V. It
is what `np.var` does, and it costs one extra traversal — 32 MB on the four-million
sample array from the numeric in this module, about 2.7 ms. That is a fair price for
an answer that is right.

*Shifted data, when you only get one pass.* Subtract any constant $K$ near the data —
the first reading will do — and accumulate $\sum(x_i - K)$ and $\sum(x_i - K)^2$
instead. A shift does not change the spread, so $\sigma$ comes out unaltered, and the
two totals are now small numbers whose difference has room to be accurate.

*Welford's method, when the data arrives forever.* It updates the mean and the sum of
squared deviations one sample at a time and never forms the large intermediate
quantities at all, which is the right answer for a monitor that has to run for months.

**And the part that generalises beyond variance.** The reason for putting this in a
module about array expressions is that the identity is exactly the kind of rewrite
vectorising invites. It removes a pass over memory, it is provably equivalent on
paper, and it is wrong in practice for a reason no amount of staring at the algebra
will reveal. Every optimisation that trades a traversal for an algebraic
rearrangement deserves the same two questions: what has to cancel for this to work,
and how big are the things that cancel compared with the answer left behind?
''',
            },
            "sandbox": {
                "title": "Why the order you touch memory matters",
                "visualiser": "cache",
                "minutes": 8,
                "initial": {"kb": 8, "ways": 1, "stride": 8},
                "brief": r'''
This is the reason an array expression beats a loop by more than the interpreter
alone can explain.

A program walks 32 KB of data three times over. The *stride* is how many bytes it
moves between one access and the next: 8 bytes is one `float64`, so a stride of 8 is
walking an array in order. The plot is the fraction of accesses that had to wait for
memory, against the size of the cache sitting in front of it.

Nothing here is about Python. It is about the shape of the data underneath it.
''',
                "notice": [
                    "It opens at a stride of 8 bytes — one double at a time, in order — with an 8 KB cache, and the miss rate reads 12.5%. That is exactly one miss in eight, because a fetch brings back 64 bytes: the first double of each line pays for the trip and the next seven arrive free.",
                    "Drag the stride to 64. The miss rate goes to 100%. The same number of bytes is being pulled in, and now only one useful double comes out of each 64-byte line — and because the 32 KB walk cannot fit in 8 KB, nothing survives to be reused on the next pass either.",
                    "Leave the stride at 64 and drag the cache up to 32 KB. The rate drops to 33.3%, which is one pass in three: the whole walk now fits, so the only misses left are the first touch of each line. That floor is compulsory — no cache is large enough to avoid reading data it has never seen.",
                    "Put the cache back to 8 KB, set the stride to 512, and then widen associativity all the way to 16. The miss rate does not move off 100%. With 8 KB split 16 ways there are only eight sets, and a 512-byte stride lands every single access on the same one; capacity is not the problem and adding more of it does not help.",
                ],
            },
            "quiz": {
                "title": "What the whole array did",
                "minutes": 9,
                "questions": [
                    {
                        "q": "`v = np.array([1.0, 2.0, 3.0])`. What is `v > 2`?",
                        "opts": [
                            "`True`",
                            "`array([False, False, True])`",
                            "`array([3.0])`",
                            "It raises, because an array cannot be compared with a number",
                        ],
                        "a": 1,
                        "why": (
                            "An array of three booleans, one per element. The comparison broadcasts the "
                            "single number across the array in exactly the way arithmetic does. A mask is "
                            "the same length as the signal it came from, which is what makes it usable as "
                            "an index: `v[v > 2]` then gives back the values, `array([3.0])`."
                        ),
                    },
                    {
                        "q": "You write `if (v > 1) and (v < 3):` for an array `v`. What happens?",
                        "opts": [
                            "It works, giving a mask of the elements between 1 and 3",
                            "It works, but only tests the first element",
                            "It raises a ValueError about the truth value of an array being ambiguous",
                            "It gives an array of the elements between 1 and 3",
                        ],
                        "a": 2,
                        "why": (
                            "A ValueError. The keyword `and` needs each side to be a single true-or-false "
                            "value, and a mask of a thousand booleans is neither true nor false as a whole. "
                            "NumPy refuses to guess whether you meant *any* or *all* and says so. The "
                            "element-by-element version is `(v > 1) & (v < 3)`, and the brackets are "
                            "compulsory because `&` binds more tightly than `>`."
                        ),
                    },
                    {
                        "q": "`np.argmax(v > 5)` on a signal that never exceeds 5 returns what?",
                        "opts": ["`-1`", "`None`", "`0`", "It raises a ValueError"],
                        "a": 2,
                        "why": (
                            "0 — which is a perfectly ordinary index and the reason this is worth "
                            "knowing. `argmax` reports where the largest value sits, every element of an "
                            "all-false mask is equally large, and the earliest wins. So a search for a "
                            "threshold crossing that never happened silently reports a crossing at the very "
                            "start of the recording. Test `mask.any()` before you trust the index."
                        ),
                    },
                    {
                        "q": "`v` is a signal. What is the difference between `np.min(v)` and `np.minimum(v, 1.0)`?",
                        "opts": [
                            "None — they are two spellings of the same function",
                            "`np.min` gives the smallest element; `np.minimum` caps every element at 1.0",
                            "`np.min` caps every element; `np.minimum` gives the smallest element",
                            "`np.minimum` only works on two arrays of the same length",
                        ],
                        "a": 1,
                        "why": (
                            "`np.min(v)` reduces the whole array to one number, the smallest. "
                            "`np.minimum(v, 1.0)` compares element by element and returns an array as long "
                            "as `v`, with every value above 1.0 replaced by 1.0. One collapses and one "
                            "transforms, and the names differ by two letters. Pairing it with `np.maximum` "
                            "clamps from both sides, which is what a clipping meter does."
                        ),
                    },
                    {
                        "q": "A recording sits on a 2.5 V offset. Which expression removes it?",
                        "opts": [
                            "`v - v.mean()`",
                            "`v.mean() - v`",
                            "`v / v.mean()`",
                            "`v - v.mean(v)`",
                        ],
                        "a": 0,
                        "why": (
                            "`v - v.mean()`. The mean is one number and subtracting it broadcasts across "
                            "every sample, leaving a signal centred on zero. Reversing the operands flips "
                            "the signal upside down as well as centring it, which is a sign error that "
                            "survives most plots unnoticed. Dividing rescales rather than shifts, and would "
                            "blow up on a recording whose mean is near zero already."
                        ),
                    },
                    {
                        "q": "The array version of a calculation runs far faster than the Python loop that does the same arithmetic. What is the main reason?",
                        "opts": [
                            "NumPy uses a better algorithm for the arithmetic",
                            "The loop is one interpreted step per element; the array expression is one interpreted step for the whole block, over data laid out end to end",
                            "NumPy spreads the work across every core of the machine",
                            "Floating-point arithmetic is faster on arrays than on single numbers",
                        ],
                        "a": 1,
                        "why": (
                            "The cost of a Python loop is the interpreting, not the arithmetic: every "
                            "element pays for a bytecode dispatch, a type check and an object. An array "
                            "expression pays that once and then runs a tight compiled loop over one "
                            "contiguous block, which is also the access pattern the memory system is built "
                            "for. The arithmetic is identical, and the answer usually is too — though "
                            "not always to the last bit, since a summation in a different order rounds "
                            "differently."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "Three loops that did not need to be loops",
                "minutes": 9,
                "lang": "python",
                "caption": "vectorise.py — four holes, and two printed lines that pin down every choice",
                "brief": r'''
The commented-out loops at the top are what this used to be. Underneath is the same
work written as array operations. Fill the holes so the two `print` lines produce
exactly what is written beside them.

The last line is the guarded threshold search from the quiz: `argmax` on its own
would report index 0 for a signal that never crosses, so the crossing has to be
confirmed before the index is believed.
''',
                "listing": r'''
import numpy as np

v = np.array([0.2, -1.4, 0.9, 2.7, -3.1, 0.4])
limit = 1.0

# What these used to be:
#   capped = [x if x < limit else limit for x in v]
#   peak   = max(abs(x) for x in v)
#   n_hot  = sum(1 for x in v if x > limit)

capped = np.___(v, limit)
peak   = np.max(np.___(v))
hot    = v > limit
n_hot  = np.___(hot)
first  = int(np.argmax(hot)) if hot.___() else -1

print(capped)                # [ 0.2 -1.4  0.9  1.  -3.1  0.4]
print(peak, n_hot, first)    # 3.1 1 3
''',
                "blanks": [
                    {
                        "prompt": "Nothing may exceed the limit; everything below it is left alone.",
                        "hole": "fn",
                        "opts": ["minimum", "maximum", "min", "max"],
                        "a": 0,
                        "why": "`np.minimum(v, limit)` compares each element against the limit and keeps the smaller, so 2.7 becomes 1.0 and −3.1 is untouched. That matches the printed array.",
                        "whys": [
                            "`np.minimum(v, limit)` compares each element against the limit and keeps the smaller, so 2.7 becomes 1.0 and −3.1 is untouched. That matches the printed array.",
                            "`np.maximum(v, limit)` keeps the larger, which raises everything below 1.0 up to 1.0 and leaves 2.7 alone — a floor rather than a ceiling, and the printed array would be almost all ones.",
                            "`np.min` reduces the array to its single smallest element, and its second argument is an axis number rather than a value to compare against, so this does not even mean what it looks like.",
                            "`np.max` has the same problem in the other direction: it collapses the array to one number, and `capped` would no longer be a signal at all.",
                        ],
                    },
                    {
                        "prompt": "The peak is about size, not about sign.",
                        "hole": "fn",
                        "opts": ["abs", "sign", "square", "sqrt"],
                        "a": 0,
                        "why": "`np.abs` strips the sign element by element, so the largest magnitude — 3.1, from a negative sample — comes out of the `np.max` around it. Without it the answer would be 2.7, the largest positive value, and the deepest excursion of the signal would go unreported.",
                        "whys": [
                            "`np.abs` strips the sign element by element, so the largest magnitude — 3.1, from a negative sample — comes out of the `np.max` around it. Without it the answer would be 2.7, the largest positive value, and the deepest excursion of the signal would go unreported.",
                            "`np.sign` reduces every sample to −1, 0 or +1, so the maximum is 1.0 whatever the signal was. It has thrown away precisely the information being asked for.",
                            "`np.square` does make everything positive, but it also changes the units: the maximum would be 9.61, which is 3.1 volts squared. You would have to take a square root afterwards to get back.",
                            "`np.sqrt` of a negative sample is `nan`, and `nan` propagates: the maximum of an array containing one is `nan`, and no error is raised anywhere along the way.",
                        ],
                    },
                    {
                        "prompt": "How many samples went over the limit?",
                        "hole": "fn",
                        "opts": ["count_nonzero", "size", "argmax", "nonzero"],
                        "a": 0,
                        "why": "`np.count_nonzero` counts the `True` entries of the mask, giving 1 here. It says what it does, which is worth something in a line whose meaning is otherwise carried entirely by the mask above it.",
                        "whys": [
                            "`np.count_nonzero` counts the `True` entries of the mask, giving 1 here. It says what it does, which is worth something in a line whose meaning is otherwise carried entirely by the mask above it.",
                            "`np.size` gives the length of the mask, which is 6 — the number of samples examined rather than the number that qualified. It is the same answer whatever the signal does, which makes it a bug that never looks obviously wrong.",
                            "`np.argmax` gives the position of the first `True`, which is 3. That is the value the next line is after, not this one.",
                            "`np.nonzero` returns a tuple of index arrays, so `n_hot` would print as something like `(array([3]),)` rather than a count. It is what you want when you need the positions themselves.",
                        ],
                    },
                    {
                        "prompt": "Only believe the index if there was a crossing at all.",
                        "hole": "method",
                        "opts": ["any", "all", "sort", "copy"],
                        "a": 0,
                        "why": "`hot.any()` is `True` when at least one sample crossed, which is exactly the condition under which `argmax` means anything. Here one sample did, so the index 3 is reported rather than −1.",
                        "whys": [
                            "`hot.any()` is `True` when at least one sample crossed, which is exactly the condition under which `argmax` means anything. Here one sample did, so the index 3 is reported rather than −1.",
                            "`hot.all()` demands that *every* sample crossed the limit. One did, so this is `False` and the answer comes back as −1 — a signal with a clear crossing reported as having none.",
                            "`hot.sort()` reorders the mask in place and returns `None`, which is never true. The guard would reject every signal, and the mask would have been scrambled as a side effect.",
                            "`hot.copy()` returns an array, and asking whether a multi-element array is true is the ambiguous-truth-value error from the quiz. This raises rather than answering.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Five summaries, no loops",
                "runtime": "python",
                "minutes": 35,
                "brief": r'''
Five functions over a signal held in a NumPy array. Every one of them can be written
without a `for` in it, and the point of the exercise is that the version without the
loop is also the version that reads like its own description.

`rms(v)` returns the root mean square, `sqrt(mean(v**2))`.

`count_between(v, lo, hi)` returns how many samples lie in the closed interval — `lo`
and `hi` themselves count. Build a mask and count it.

`clip_to(v, lo, hi)` returns a new array with everything below `lo` raised to `lo` and
everything above `hi` lowered to `hi`. It must not modify `v`.

`first_above(v, level)` returns the index of the first sample strictly greater than
`level`, or `-1` when there is none. Guard the `argmax`.

`moving_average(v, n)` returns the average of every run of `n` consecutive samples, so
an array of length `len(v) - n + 1`. Use the cumulative-sum trick: with
`c = np.concatenate(([0.0], np.cumsum(v)))`, the sum of the window starting at `i` is
`c[i + n] - c[i]`, so the whole answer is `(c[n:] - c[:-n]) / n`. Raise a `ValueError`
when `n` is less than 1 or longer than the signal.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def rms(v):
    """Root mean square: sqrt(mean(v**2))."""
    v = np.asarray(v, dtype=float)
    # TODO
    return 0.0


def count_between(v, lo, hi):
    """How many samples lie between lo and hi, both included."""
    v = np.asarray(v, dtype=float)
    # TODO: one mask, one count. Remember the brackets around each comparison.
    return 0


def clip_to(v, lo, hi):
    """A new array with every sample held inside [lo, hi]."""
    v = np.asarray(v, dtype=float)
    # TODO: np.minimum and np.maximum, one inside the other.
    return v


def first_above(v, level):
    """Index of the first sample strictly above level, or -1 if there is none."""
    v = np.asarray(v, dtype=float)
    # TODO: build the mask, check it found something, then argmax.
    return -1


def moving_average(v, n):
    """The mean of each run of n consecutive samples."""
    v = np.asarray(v, dtype=float)
    # TODO: raise ValueError for a window that does not fit, then cumulative sums.
    return v


if __name__ == "__main__":
    fs = 2000.0
    t = np.arange(0, 0.1, 1.0 / fs)
    sig = 3.0 * np.sin(2 * np.pi * 60 * t)
    print("samples:", t.size, " rms:", round(rms(sig), 6))
    print("within a volt of zero:", count_between(sig, -1.0, 1.0))
    print("first above 2 V at index:", first_above(sig, 2.0))
    print("smoothed length:", moving_average(sig, 8).size)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def rms(v):
    """Root mean square: sqrt(mean(v**2))."""
    v = np.asarray(v, dtype=float)
    return float(np.sqrt(np.mean(v * v)))


def count_between(v, lo, hi):
    """How many samples lie between lo and hi, both included."""
    v = np.asarray(v, dtype=float)
    return int(np.count_nonzero((v >= lo) & (v <= hi)))


def clip_to(v, lo, hi):
    """A new array with every sample held inside [lo, hi]."""
    v = np.asarray(v, dtype=float)
    return np.minimum(np.maximum(v, lo), hi)


def first_above(v, level):
    """Index of the first sample strictly above level, or -1 if there is none."""
    v = np.asarray(v, dtype=float)
    hits = v > level
    if not hits.any():
        return -1
    return int(np.argmax(hits))


def moving_average(v, n):
    """The mean of each run of n consecutive samples."""
    v = np.asarray(v, dtype=float)
    if n < 1 or n > v.size:
        raise ValueError("a window of %d does not fit %d samples" % (n, v.size))
    c = np.concatenate(([0.0], np.cumsum(v)))
    return (c[n:] - c[:-n]) / n


if __name__ == "__main__":
    fs = 2000.0
    t = np.arange(0, 0.1, 1.0 / fs)
    sig = 3.0 * np.sin(2 * np.pi * 60 * t)
    print("samples:", t.size, " rms:", round(rms(sig), 6))
    print("within a volt of zero:", count_between(sig, -1.0, 1.0))
    print("first above 2 V at index:", first_above(sig, 2.0))
    print("smoothed length:", moving_average(sig, 8).size)
'''}],
                "hints": [
                    "`(v >= lo) & (v <= hi)` needs both pairs of brackets: `&` binds more tightly than `>=`, so leaving them out compares `lo & v` and produces an error about integers rather than the mask you wanted.",
                    "`np.maximum(v, lo)` lifts the floor and `np.minimum(..., hi)` lowers the ceiling. Both return new arrays, so `v` is never touched — which is what the test about the input surviving is checking.",
                    "In `first_above`, `hits.any()` is the guard. Without it a signal that never crosses returns index 0, and index 0 is a sample like any other, so nothing downstream can tell the difference.",
                    "For the moving average, `c` is one longer than `v` because of the leading zero, and `c[n:] - c[:-n]` lines up each window's end against its start. If your result is one element too long or too short, count the elements of `c` again.",
                ],
                "tests": [
                    {"name": "rms measures size, not average", "code": r'''
import numpy as np
_sq = np.array([0.0, 4.0, 0.0, 4.0, 0.0, 4.0, 0.0, 4.0])
assert abs(rms(_sq) - 2.8284271247461903) < 1e-9, \
    f"half the time at 0 and half at 4 gives sqrt(8) = 2.8284; got {rms(_sq)}"
_fs = 2000.0
_t = np.arange(0, 0.1, 1.0 / _fs)
_sig = 3.0 * np.sin(2 * np.pi * 60 * _t)
assert _t.size == 200, f"0.1 s at 2 kHz is 200 samples; got {_t.size}"
assert abs(rms(_sig) - 3.0 / np.sqrt(2)) < 1e-9, \
    f"a 3 V peak sine has an RMS of 2.1213; got {rms(_sig)}"
'''},
                    {"name": "counting a mask includes both ends", "code": r'''
import numpy as np
_a = np.array([-3.0, -0.4, 0.0, 0.4, 1.6, 5.0])
assert count_between(_a, -0.5, 0.5) == 3, \
    f"-0.4, 0.0 and 0.4 are inside; got {count_between(_a, -0.5, 0.5)}"
assert count_between(_a, -0.4, 0.4) == 3, \
    "the interval is closed, so a sample sitting exactly on an end still counts"
assert count_between(_a, 10.0, 20.0) == 0, "nothing is up there"
assert count_between(_a, -100.0, 100.0) == 6, "everything is in there"
'''},
                    {"name": "clipping is two-sided and leaves the input alone", "code": r'''
import numpy as np
_a = np.array([-3.0, -0.4, 0.0, 0.4, 1.6, 5.0])
_c = clip_to(_a, -1.0, 1.0)
assert np.allclose(_c, [-1.0, -0.4, 0.0, 0.4, 1.0, 1.0]), f"got {_c}"
assert abs(float(_a[0]) + 3.0) < 1e-12 and abs(float(_a[-1]) - 5.0) < 1e-12, \
    "the input array came back modified; np.minimum and np.maximum both return new arrays"
assert isinstance(_c, np.ndarray), f"expected an array, got {type(_c).__name__}"
'''},
                    {"name": "the threshold search is guarded", "code": r'''
import numpy as np
_ramp = np.linspace(0.0, 10.0, 11)
assert first_above(_ramp, 6.5) == 7, \
    f"the ramp is 0, 1, 2 ... so the first sample above 6.5 is 7 at index 7; got {first_above(_ramp, 6.5)}"
assert first_above(_ramp, -1.0) == 0, "every sample is above -1, so the first one is index 0"
assert first_above(np.zeros(5), 1.0) == -1, \
    ("a signal that never crosses must report -1; an unguarded argmax returns 0 here, "
     "which is indistinguishable from a crossing on the very first sample")
assert first_above(_ramp, 10.0) == -1, "strictly above, so the final 10.0 does not count"
'''},
                    {"name": "the moving average is the right length and the right values", "code": r'''
import numpy as np
_m = moving_average(np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]), 3)
assert _m.size == 4, f"six samples in windows of three is four windows; got {_m.size}"
assert np.allclose(_m, [2.0, 3.0, 4.0, 5.0]), f"got {_m}"
_sq = np.array([0.0, 4.0, 0.0, 4.0, 0.0, 4.0, 0.0, 4.0])
assert np.allclose(moving_average(_sq, 2), [2.0] * 7), \
    f"a two-sample window flattens an alternating signal completely; got {moving_average(_sq, 2)}"
assert np.allclose(moving_average(_sq, 8), [2.0]), \
    "a window as long as the signal gives one number, the overall mean"
'''},
                    {"name": "a window that does not fit is refused", "code": r'''
import numpy as np
for _n in (0, -2, 9):
    _raised = False
    try:
        moving_average(np.zeros(8), _n)
    except ValueError:
        _raised = True
    assert _raised, \
        f"a window of {_n} over 8 samples must raise a ValueError rather than return something"
'''},
                    {"name": "everything works on a real signal", "code": r'''
import numpy as np
_fs = 2000.0
_t = np.arange(0, 0.1, 1.0 / _fs)
_sig = 3.0 * np.sin(2 * np.pi * 60 * _t)
_sm = moving_average(_sig, 8)
assert _sm.size == 193, f"200 samples in windows of 8 is 193 windows; got {_sm.size}"
assert float(np.max(np.abs(_sm))) < 3.0, \
    "smoothing a sine must reduce its amplitude, never increase it"
assert count_between(_sig, -3.1, 3.1) == 200, "every sample of a 3 V sine is within 3.1 V"
_clipped = clip_to(_sig, -1.0, 1.0)
assert abs(float(np.max(_clipped)) - 1.0) < 1e-12, "the clipped signal tops out at exactly 1.0"
assert rms(_clipped) < rms(_sig), "clipping removes energy"
'''},
                ],
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "Errors that crash, and errors that do not",
            "summary": "A program can fail loudly or quietly. The loud kind stops and names the line; the quiet kind hands you a number and lets you act on it. Only one of the two is actually dangerous.",
            "concepts": [
                "An *exception* stops the program and names what went wrong. `ValueError` means the right type carrying a value that makes no sense, `TypeError` the wrong type entirely, and `KeyError`, `IndexError` and `ZeroDivisionError` say exactly what they say.",
                "`raise ValueError(\"a window of 9 does not fit 8 samples\")` is how your own function refuses. Refuse at the top, while the caller's mistake is still the nearest thing to the error.",
                "`try:` / `except ValueError:` catches one named kind. A bare `except:` swallows everything, including the typo in the line you were trying to protect, and turns a bug you would have found in a minute into one you will not find at all.",
                "`assert cond, \"message\"` records something you believe must hold at that point in your own reasoning. It is not a way to validate input from outside, because assertions can be switched off and then check nothing.",
                "The failure worth fearing returns a number. *Cancellation*: subtract two nearly equal floats and the leading digits agree and vanish, leaving whatever rounding noise was in the last few — promoted, silently, to the whole of the answer.",
                "A check that cannot fail proves nothing. Before trusting one, break the code on purpose and confirm it goes red; a test suite that stays green against a deliberately wrong answer is measuring the wrong thing.",
            ],
            "quiz": {
                "title": "Which failure was that?",
                "minutes": 9,
                "questions": [
                    {
                        "q": "`float(\"4k7\")` fails. What kind of exception is it?",
                        "opts": ["TypeError", "ValueError", "SyntaxError", "KeyError"],
                        "a": 1,
                        "why": (
                            "A ValueError. The argument is a string, which is a type `float` accepts, and "
                            "the trouble is that this particular string is not the text of a number. A "
                            "TypeError is what you get from `float([1, 2])`, where the type itself is "
                            "wrong. The distinction is worth keeping straight, because catching the wrong "
                            "one lets the failure you were guarding against sail past."
                        ),
                    },
                    {
                        "q": "What is wrong with wrapping a parser in `try: ... except: pass`?",
                        "opts": [
                            "Nothing — it is the standard way to skip malformed lines",
                            "It catches every failure, including mistakes in your own code, and reports none of them",
                            "It is slower than checking each line first",
                            "It only catches the first exception and then stops",
                        ],
                        "a": 1,
                        "why": (
                            "It catches everything and reports nothing. A misspelled variable name inside "
                            "the block raises a NameError, and the NameError is swallowed along with the "
                            "malformed lines, so the parser quietly returns fewer records than the file "
                            "contains and no message says why. Catch the specific kind you can actually "
                            "handle, and let the rest through."
                        ),
                    },
                    {
                        "q": "You compute `1e16 + 1 - 1e16` in Python. What comes out?",
                        "opts": ["1.0", "0.0", "2.0", "It raises an OverflowError"],
                        "a": 1,
                        "why": (
                            "0.0. A double carries about sixteen significant digits, so adding 1 to 10¹⁶ "
                            "has no representable effect and the addition returns 10¹⁶ unchanged; "
                            "subtracting it then leaves nothing. Nothing is raised, nothing is flagged, and "
                            "the answer is off by 100%. Notice that `1e16 - 1e16 + 1` gives 1.0: with "
                            "floating point the order of operations is part of the result."
                        ),
                    },
                    {
                        "q": "Which of these is the right use of `assert`?",
                        "opts": [
                            "Checking that a value typed by a user is in range",
                            "Checking that the file the program was given exists",
                            "Recording that a probability you just computed lies between 0 and 1",
                            "Replacing `raise ValueError` everywhere, because it is shorter",
                        ],
                        "a": 2,
                        "why": (
                            "An assertion states something your own code should have guaranteed — an "
                            "internal invariant, checked so that a mistake in your reasoning surfaces near "
                            "where it happened. Input from outside the program is different: it is expected "
                            "to be wrong sometimes, and it deserves a real check and a real exception, "
                            "because Python run with `-O` removes every assert and would then let bad input "
                            "straight through."
                        ),
                    },
                    {
                        "q": "A function returns 0.0 when it cannot parse its argument. What is the consequence for a circuit simulation that reads a component value with it?",
                        "opts": [
                            "The simulation refuses to run, which is safe",
                            "The simulation runs with a zero-ohm resistor — a short circuit — and reports an answer",
                            "The value is treated as missing and the component is left out",
                            "NumPy raises a warning about the zero",
                        ],
                        "a": 1,
                        "why": (
                            "It runs, with that component replaced by a short. The simulator has no way to "
                            "distinguish a resistor genuinely specified as zero from a line the parser "
                            "could not read, so it solves a circuit nobody drew and hands back voltages "
                            "that look entirely plausible. A default value is a decision about the physics, "
                            "and a parser is not entitled to make one."
                        ),
                    },
                    {
                        "q": "You add a test for a function and it passes on the first run. What should you do before believing it?",
                        "opts": [
                            "Nothing — a passing test is a passing test",
                            "Add more tests until one fails",
                            "Break the function deliberately and confirm the test goes red",
                            "Run it again to make sure it is not flaky",
                        ],
                        "a": 2,
                        "why": (
                            "Break it on purpose. A test that passes against a wrong implementation is "
                            "testing something other than what you meant — comparing an array against "
                            "itself, asserting a condition that is true for every input, or calling a "
                            "function whose result it then ignores. Watching a check go red for a known "
                            "reason is the only cheap evidence that it is connected to anything."
                        ),
                    },
                ],
            },
            "build": {
                "title": "Build to a specification that is only checks",
                "minutes": 25,
                "brief": r'''
No description of the circuit this time. The specification below *is* the five
measurements, and the exercise is to build something that satisfies all of them.

With a 1 V source at the input and a probe on the output node:

| at | the output must be |
| --- | --- |
| 50 Hz | about a tenth of the input |
| 500 Hz | 0.707 of the input — the corner |
| 5 kHz | essentially all of the input |
| 500 Hz | **+45°** of phase, output *leading* input |

The canvas gives you a 1 V source, two grounds, and a **100 nF capacitor already in
line** with the signal. Add one resistor and a probe.

Read the table before you reach for a formula. Little gets through at low frequency
and everything at high frequency, which is the opposite way round from the filter
you will build in the next module of this course — and the positive phase says the
same thing a second time. For this circuit the corner is still

```text
f_c = 1 / (2 * pi * R * C)
```

and the checks allow the nearest ordinary resistor value rather than demanding the
exact one.

This is what an executable specification looks like. Nobody has told you what to
draw; they have told you how what you draw will be measured, and there is no room
left for the two of you to have meant different things.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p3", "kind": "C", "x": 6, "y": 4, "rot": 0, "value": 1e-7},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p3", "kind": "C", "x": 6, "y": 4, "rot": 0, "value": 1e-7},
                        {"id": "p4", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3300},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 4], "b": [11, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                    ],
                },
                "checks": [
                    {"name": "the source is the 1 V the specification drives", "code": r'''
c.assert(c.count("V") === 1, "keep exactly one source: the 1 V supply you started with");
c.close(c.values("V")[0], 1, 0.001, "the source amplitude");
'''},
                    {"name": "at 50 Hz about a tenth gets through", "code": r'''
c.close(c.gain(50), 0.0995, 0.25,
  "the gain at 50 Hz, a decade below the corner. A reading near 1 means the low " +
  "frequencies are passing, which is the wrong filter");
'''},
                    {"name": "at 500 Hz the output is 0.707 of the input", "code": r'''
c.close(c.gain(500), 0.7071, 0.07, "the gain at 500 Hz, which is where the corner belongs");
'''},
                    {"name": "at 5 kHz essentially all of it gets through", "code": r'''
c.close(c.gain(5000), 1.0, 0.03,
  "the gain at 5 kHz, a decade above the corner, must be within a few per cent of 1");
'''},
                    {"name": "the phase at 500 Hz is plus 45 degrees", "code": r'''
var ph = c.phase(500);
c.assert(ph > 0,
  "the phase at 500 Hz measures " + ph.toFixed(1) + " degrees. A negative phase means " +
  "the output lags, which is what the other arrangement of these two parts does");
c.close(ph, 45, 0.2, "the phase at 500 Hz");
'''},
                ],
                "hints": [
                    "Everything above the corner passes and everything below it is attenuated. The capacitor is already in line, so the resistor is the part that goes from the output node down to ground.",
                    "Rearranged for the unknown, R = 1 / (2 * pi * f_c * C). With 500 Hz and 100 nF that is 3183 Ω, and the nearest ordinary value, 3.3 kΩ, puts the corner at 482 Hz — inside what the checks allow.",
                    "If the gain at 50 Hz comes back near 1 and the gain at 5 kHz near a tenth, the two parts are the other way round: that arrangement is the low-pass of the next module, and it fails this specification at every frequency in the table.",
                    "The probe belongs on the node between the capacitor and the resistor. Probing the source side reads the input, and the input is 1 V at every frequency, so the corner check will report a gain of 1 wherever you look.",
                ],
            },
            "derive": {
                "title": "The quadratic formula that does not lose the answer",
                "minutes": 12,
                "vars": ["a", "b", "c", "x"],
                "brief": r'''
The roots of $ax^2 + bx + c = 0$ are

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

Take $a = 1$, $b = 10^{9}$, $c = 1$. The root near zero is $-10^{-9}$, and the $+$
branch is the one that should produce it. Its numerator is
$-10^{9} + \sqrt{10^{18} - 4}$. Up at $10^{18}$ the gap between one representable
double and the next is 128, so the $-4$ has nowhere to go: $b^2 - 4ac$ rounds back to
exactly $10^{18}$, its root is exactly $10^{9}$, and the subtraction gives exactly
zero. Python reports that the root of $x^2 + 10^{9}x + 1$ is 0, without a word.

More precision only moves the value of $b$ at which this happens. What fixes it is
rewriting the expression so the subtraction never occurs, and the tool for that is
the difference of two squares.
''',
                "steps": [
                    {
                        "prompt": "Multiply the top and the bottom of $x = \\dfrac{-b + \\sqrt{b^2 - 4ac}}{2a}$ by $-b - \\sqrt{b^2 - 4ac}$. What does the numerator simplify to?",
                        "answer": "4 a c",
                        "hint": "$(p + q)(p - q) = p^2 - q^2$, with $p = -b$ and $q = \\sqrt{b^2 - 4ac}$.",
                        "deconstruct": [
                            "$p^2 = (-b)^2 = b^2$.",
                            "$q^2 = \\left(\\sqrt{b^2 - 4ac}\\right)^2 = b^2 - 4ac$.",
                            "$b^2 - (b^2 - 4ac) = 4ac$, and both $b^2$ terms have gone.",
                        ],
                    },
                    {
                        "prompt": "Write the new denominator, without simplifying it.",
                        "answer": "2 a (-b - \\sqrt{b^{2} - 4 a c})",
                        "hint": "It is whatever the denominator already was, times the factor you just multiplied by.",
                        "deconstruct": [
                            "The denominator was $2a$.",
                            "You multiplied top and bottom by $-b - \\sqrt{b^2 - 4ac}$, so the bottom picks it up as a factor.",
                        ],
                    },
                    {
                        "prompt": "Divide, cancelling the factor the top and bottom have in common. Write the root.",
                        "answer": "\\frac{2 c}{-b - \\sqrt{b^{2} - 4 a c}}",
                        "hint": "$4ac$ over $2a$ leaves $2c$; nothing else cancels.",
                        "deconstruct": [
                            "$\\dfrac{4ac}{2a\\left(-b - \\sqrt{b^2 - 4ac}\\right)}$.",
                            "The $2a$ divides into the $4ac$, leaving $2c$ on top.",
                        ],
                    },
                ],
                "closing": r'''
Look at what changed. The original numerator subtracted two nearly equal numbers; the
new denominator *adds* them, whenever $b$ is positive. Nothing cancels, no digits are
lost, and with $a=1$, $b=10^{9}$, $c=1$ this form returns $-10^{-9}$ exactly.

It is the same root. The two expressions are equal for every $a$, $b$ and $c$ — which
is exactly why the failure is so hard to see. Two lines of code that a mathematician
would call identical agree on nothing at all here: one of them has every digit right
and the other has none.

For $b$ negative the danger swaps to the other branch, so the usual rule is: compute
whichever root's formula does the *adding*, then get the second from
$x_1 x_2 = c/a$ rather than from the formula at all.
''',
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Integration, and a simulation you can trust",
            "summary": "Stepping a differential equation forward is four lines of code. Knowing whether the answer means anything is the rest of the module.",
            "concepts": [
                "A first-order system is described by a rate: for a capacitor charging through a resistor, `dv/dt = (vin - v) / (R*C)`.",
                "The *time constant* is `tau = R*C`. After one time constant the capacitor has reached 63.2% of the way; after five it is within 1%.",
                "Forward Euler: assume the rate holds for the whole step, so `v_next = v + dt * rate(v)`. That is the entire method.",
                "Euler is *first order*: halve the timestep and the error roughly halves. Halving it and watching the answer barely move is how you know you have converged.",
                "Too large a step does not merely blur the answer, it destroys it. For this system, `dt` above `2*tau` makes the simulated voltage oscillate and grow without bound.",
                "Agreeing with an analytic solution validates the *integrator*. It says nothing about whether the equation describes the circuit — only a measurement can say that.",
            ],
            "sandbox": {
                "title": "The shape a simulation has to reproduce",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 0.35, "wn": 4},
                "brief": r'''
The RC circuit you are about to simulate settles smoothly, with no overshoot.
Systems with two energy stores — a spring and a mass, an inductor and a capacitor —
can overshoot and ring instead, and this is what that looks like.

The left panel is the s-plane, and the two dots are the *poles*: numbers that encode
how fast the response decays and how fast it oscillates. The right panel is the
response to a sudden step at the input, which is what your simulation computes.
Change one panel and watch the other.
''',
                "notice": [
                    "As it opens, damping is 0.35 and the two dots sit off the horizontal axis, one above it and one below. The note in the top-left corner of the s-plane reads ω_d = 3.75, the rate at which those poles ring, in rad/s. The response on the right overshoots the dashed line at 1 and then settles onto it.",
                    "Drag damping to zero. The dots land on the vertical axis and the response swings between 0 and 2 for ever. Nothing removes the energy, so it never settles — the simulation of such a system has nowhere to converge to.",
                    "Take damping past 1, to about 1.3. Both dots turn amber and drop onto the horizontal axis, the note in the corner changes from a ringing frequency to `both poles real`, and the overshoot disappears entirely. That is the regime the RC circuit lives in.",
                    "Hold damping at 0.35 and double the natural frequency from 4 to 8. The curve keeps its exact shape and only the numbers on the time axis halve. Speed and shape are separate: a simulation whose timestep suits one may be far too coarse for the other.",
                ],
            },
            "quiz": {
                "title": "Does the number mean anything?",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A capacitor charging through a resistor obeys `dv/dt = (vin - v) / (R*C)`. What is the forward Euler step?",
                        "opts": [
                            "`v = v + dt * (vin - v) / (R*C)`",
                            "`v = v + (vin - v) / (R*C)`",
                            "`v = v * dt * (vin - v) / (R*C)`",
                            "`v = (vin - v) / (R*C)`",
                        ],
                        "a": 0,
                        "why": (
                            "The rate is a change *per second*, so it must be multiplied by the length of "
                            "the step before being added to the value. Leaving `dt` out makes the "
                            "simulation's speed depend on how finely you chose to sample it — always a "
                            "sign the timestep has gone missing. Writing `v = (vin - v) / (R*C)` "
                            "overwrites the voltage with the rate, which is not even the right unit."
                        ),
                    },
                    {
                        "q": "You run a forward Euler simulation, halve `dt`, and run it again. What should happen to the difference between your answer and the exact one?",
                        "opts": [
                            "It stays the same",
                            "It roughly halves",
                            "It roughly quarters",
                            "It doubles",
                        ],
                        "a": 1,
                        "why": (
                            "It roughly halves. Forward Euler is a first-order method: the error is "
                            "proportional to `dt`, so halving the step halves the error. Expecting a quarter "
                            "is the natural guess and describes a second-order method such as trapezoidal or "
                            "midpoint. Either way the *test* is the same, and it is the one worth "
                            "remembering: halve the step, and if the answer moves by more than you can "
                            "tolerate, it had not converged."
                        ),
                    },
                    {
                        "q": "For this RC system, `tau = R*C` is 160 µs. You run the simulation with `dt` = 350 µs. What comes out?",
                        "opts": [
                            "The right curve, sampled coarsely",
                            "A curve that settles at the wrong final value",
                            "A voltage that flips sign every step and grows without bound",
                            "The right curve, but delayed by one step",
                        ],
                        "a": 2,
                        "why": (
                            "It oscillates and diverges. Each step multiplies the remaining error by "
                            "`1 - dt/tau`, which is −1.19 here; a factor with magnitude above 1 makes the "
                            "error grow, and its negative sign flips it each step. The dangerous part is "
                            "that this is not a rounding problem you can shrug at: with `dt` above `2*tau` "
                            "the method is unstable and the output is not an approximation of anything."
                        ),
                    },
                    {
                        "q": "Your simulated curve matches the analytic solution of the same differential equation to seven decimal places. What have you established?",
                        "opts": [
                            "That the circuit behaves as the model says",
                            "That your integrator solves that equation correctly",
                            "That the timestep is as large as it can safely be",
                            "That the model has no approximations in it",
                        ],
                        "a": 1,
                        "why": (
                            "Only that your integrator solves that equation correctly. The equation might "
                            "still be the wrong description of the circuit — it ignores the resistor's stray "
                            "capacitance, the capacitor's leakage and the source's output resistance, and no "
                            "amount of agreement between two solutions of the same equation can reveal that. "
                            "Comparing with the analytic answer tests the code; comparing with a measurement "
                            "tests the model. The capstone does both, in that order."
                        ),
                    },
                    {
                        "q": "With `R` = 1.6 kΩ and `C` = 100 nF, roughly how long until the capacitor reaches 63% of the supply?",
                        "opts": ["160 ns", "16 µs", "160 µs", "1.6 ms"],
                        "a": 2,
                        "why": (
                            "160 µs. The time constant is the product: 1600 Ω × 100 × 10⁻⁹ F = 1.6 × 10⁻⁴ s. "
                            "Getting the powers of ten right here is most of the work, and it is worth doing "
                            "before you write any code, because a simulation whose answer is out by a factor "
                            "of a thousand looks perfectly plausible on a plot with no units. Five time "
                            "constants, 800 µs, is where it is within 1% of settled."
                        ),
                    },
                ],
            },
            "build": {
                "title": "A low-pass filter with a 1 kHz corner",
                "minutes": 25,
                "brief": r'''
A **low-pass filter** passes signals below some frequency and attenuates those above
it. The simplest one is a resistor followed by a capacitor to ground, and the
frequency where it hands over is the **corner**, where the output has fallen to
1/√2 of the input — 3 dB down.

For a resistor and capacitor, that corner sits at

```text
f_c = 1 / (2 * pi * R * C)
```

The canvas opens with a **1 V source**, two grounds, and a **1.6 kΩ resistor**
already placed. Add a capacitor from the resistor's right-hand end to ground, put a
probe on that same node, and choose the capacitance that puts the corner at
**1 kHz**.

What the checks measure, all of it on your circuit rather than on any reference
drawing:

- the gain well below the corner, which must be essentially 1;
- the corner itself, found by sweeping the frequency and looking for the 3 dB point;
- the *phase* at 1 kHz — how far the output sine lags the input, measured as a
  fraction of a cycle in degrees — which at the corner of this filter is −45°,
  an eighth of a cycle behind;
- the gain a decade above the corner, which must be about a tenth — 20 dB per decade;
- the step response, which must reach 63% of its final value after one time constant.

If you prefer a different resistor, change it. Any pair with the same product passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p3", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1600},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p3", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1600},
                        {"id": "p4", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-7},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 4], "b": [11, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 7], "b": [9, 9]},
                    ],
                },
                "checks": [
                    {"name": "the 1 V source is still there", "code": r'''
c.assert(c.count("V") === 1, "keep exactly one source: the 1 V supply you started with");
c.close(c.values("V")[0], 1, 0.001, "the source amplitude");
'''},
                    {"name": "low frequencies pass through untouched", "code": r'''
c.close(c.gain(10), 1.0, 0.02,
  "the gain at 10 Hz, two decades below the corner, must be essentially 1");
'''},
                    {"name": "the corner is at 1 kHz", "code": r'''
var fc = c.corner(10, 1e6);
c.close(fc, 1000, 0.05, "the measured 3 dB corner");
'''},
                    {"name": "the phase at the corner is minus 45 degrees", "code": r'''
c.close(c.phase(1000), -45, 0.2, "the phase at 1 kHz");
'''},
                    {"name": "it rolls off at 20 dB per decade", "code": r'''
var g = c.gain(10000);
c.close(g, 0.0995, 0.15,
  "the gain at 10 kHz, one decade above the corner, should be about a tenth");
'''},
                    {"name": "the step reaches 63% after one time constant", "code": r'''
var s = c.step(0.001);
var tau = 1 / (2 * Math.PI * 1000);
var k = 0;
for (var i = 0; i < s.t.length; i++) {
  if (Math.abs(s.t[i] - tau) < Math.abs(s.t[k] - tau)) k = i;
}
c.close(s.v[k], 0.632, 0.06, "the step response one time constant in");
c.close(s.v[s.v.length - 1], 1.0, 0.02, "the settled value after 1 ms");
'''},
                ],
                "hints": [
                    "Rearrange the corner formula for the unknown: C = 1 / (2 * pi * f_c * R). With 1 kHz and 1.6 kΩ that is 99.5 nF, and the nearest real part is 100 nF, which lands the corner within half a per cent.",
                    "The capacitor goes from the output node to ground, not in line with the signal. A capacitor in line makes a high-pass filter, and the check on the gain at 10 Hz will fail immediately if you build one.",
                    "Place the capacitor vertically so its top pin meets the wire from the resistor and its bottom pin can reach the ground symbol.",
                    "The time constant follows from the corner alone: tau = 1 / (2 * pi * f_c) = 159 µs, whatever R and C you chose to make it. That is why the step check works for every correct answer.",
                ],
            },
            "lab": {
                "title": "Simulate the filter you just drew",
                "runtime": "python",
                "minutes": 35,
                "brief": r'''
The circuit from the build, in code. The capacitor voltage obeys

```text
dv/dt = (vin - v) / (R*C)
```

and starts at zero.

`rc_step(r, c, vin, dt, tstop)` returns two arrays, the times and the voltages, using
forward Euler. Build the time axis as `n = int(round(tstop / dt)) + 1` points spaced
by `dt`, start the voltage at 0, and fill each next value from the one before with

```text
v[i + 1] = v[i] + dt * (vin - v[i]) / (r * c)
```

`rc_exact(r, c, vin, t)` returns the answer calculus gives for the same equation,
`vin * (1 - exp(-t / (r*c)))`, for an array of times.

`max_error(r, c, vin, dt, tstop)` runs the simulation, evaluates the exact answer at
the *same* times, and returns the largest absolute difference. That single number is
what you will halve `dt` against to decide whether the simulation has converged.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def rc_step(r, c, vin, dt, tstop):
    """Forward Euler on dv/dt = (vin - v)/(r*c). Returns (times, voltages)."""
    tau = r * c
    n = int(round(tstop / dt)) + 1
    t = dt * np.arange(n)
    v = np.zeros(n)
    # TODO: loop from 0 to n-2, filling v[i + 1] from v[i].
    return t, v


def rc_exact(r, c, vin, t):
    """The analytic answer to the same equation, at the times in t."""
    t = np.asarray(t, dtype=float)
    # TODO: vin * (1 - exp(-t / (r*c)))
    return np.zeros_like(t)


def max_error(r, c, vin, dt, tstop):
    """Largest gap between the simulation and the exact answer, over the whole run."""
    t, v = rc_step(r, c, vin, dt, tstop)
    # TODO: compare v with rc_exact at the same times and return the largest gap.
    return 0.0


if __name__ == "__main__":
    R, C, VIN = 1600.0, 1e-7, 1.0
    print("tau =", R * C, "s")
    t, v = rc_step(R, C, VIN, 1e-6, 1e-3)
    print("samples:", len(t), "final volts:", round(float(v[-1]), 6))
    print("error at dt = 1 us: ", max_error(R, C, VIN, 1e-6, 1e-3))
    print("error at dt = 0.5 us:", max_error(R, C, VIN, 5e-7, 1e-3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def rc_step(r, c, vin, dt, tstop):
    """Forward Euler on dv/dt = (vin - v)/(r*c). Returns (times, voltages)."""
    tau = r * c
    n = int(round(tstop / dt)) + 1
    t = dt * np.arange(n)
    v = np.zeros(n)
    for i in range(n - 1):
        v[i + 1] = v[i] + dt * (vin - v[i]) / tau
    return t, v


def rc_exact(r, c, vin, t):
    """The analytic answer to the same equation, at the times in t."""
    t = np.asarray(t, dtype=float)
    return vin * (1.0 - np.exp(-t / (r * c)))


def max_error(r, c, vin, dt, tstop):
    """Largest gap between the simulation and the exact answer, over the whole run."""
    t, v = rc_step(r, c, vin, dt, tstop)
    return float(np.max(np.abs(v - rc_exact(r, c, vin, t))))


if __name__ == "__main__":
    R, C, VIN = 1600.0, 1e-7, 1.0
    print("tau =", R * C, "s")
    t, v = rc_step(R, C, VIN, 1e-6, 1e-3)
    print("samples:", len(t), "final volts:", round(float(v[-1]), 6))
    print("error at dt = 1 us: ", max_error(R, C, VIN, 1e-6, 1e-3))
    print("error at dt = 0.5 us:", max_error(R, C, VIN, 5e-7, 1e-3))
'''}],
                "hints": [
                    "The loop runs `for i in range(n - 1)`, not `range(n)`: the last index has no successor to write into, and `range(n)` walks off the end of the array.",
                    "`v[0]` is already 0 from `np.zeros`, and it must stay 0 — the capacitor starts empty. If your first value is not 0 you have written into the wrong slot.",
                    "In `rc_exact`, `np.exp` works on the whole array at once, so the body is one line with no loop in it.",
                    "`max_error` must evaluate the exact answer at `t`, the times the simulation actually produced. Comparing against a different time axis measures the mismatch of the axes rather than the error of the method.",
                ],
                "tests": [
                    {"name": "the time axis has the right length and spacing", "code": r'''
import numpy as np
_t, _v = rc_step(1600.0, 1e-7, 1.0, 1e-6, 1e-3)
assert len(_t) == 1001, f"1 ms in steps of 1 us is 1000 steps and 1001 points, got {len(_t)}"
assert abs(float(_t[0])) < 1e-18, f"the run starts at t = 0, got {_t[0]}"
assert abs(float(_t[-1]) - 1e-3) < 1e-12, f"and ends at 1 ms, got {_t[-1]}"
assert len(_v) == len(_t), f"one voltage per time, got {len(_v)} against {len(_t)}"
assert float(np.max(_v)) > 0.9, \
    ("1 ms is 6.25 time constants, so the voltage has to climb close to the 1 V supply; "
     f"the largest value was {np.max(_v)}, which is what an array the loop never touched "
     "looks like")
'''},
                    {"name": "the capacitor starts empty and charges to the supply", "code": r'''
import numpy as np
_t, _v = rc_step(1600.0, 1e-7, 1.0, 1e-6, 1e-3)
assert abs(float(_v[0])) < 1e-18, f"the capacitor starts at 0 V, got {_v[0]}"
assert abs(float(_v[-1]) - 0.9981070390083471) < 1e-9, \
    f"after 1 ms, which is 6.25 time constants, it should be at 0.99811 V, got {_v[-1]}"
'''},
                    {"name": "the exact solution passes 63.2% at one time constant", "code": r'''
import numpy as np
_tau = 1600.0 * 1e-7
_e = float(rc_exact(1600.0, 1e-7, 1.0, np.array([_tau]))[0])
assert abs(_e - 0.6321205588285577) < 1e-12, \
    f"1 - exp(-1) is 0.63212, got {_e}"
_five = float(rc_exact(1600.0, 1e-7, 1.0, np.array([5 * _tau]))[0])
assert abs(_five - 0.9932620530009145) < 1e-12, \
    f"after five time constants it is within 1% of the supply, got {_five}"
'''},
                    {"name": "a coarse Euler run is wrong in the way Euler is wrong", "code": r'''
import numpy as np
_tau = 1600.0 * 1e-7
_t, _v = rc_step(1600.0, 1e-7, 1.0, _tau / 4, 1e-3)
assert abs(float(_v[4]) - 0.68359375) < 1e-12, \
    ("with dt = tau/4 each step multiplies the shortfall by 0.75, so after four steps "
     f"the value is 1 - 0.75**4 = 0.68359; got {_v[4]}")
assert float(_v[4]) > 0.6321205588285577, \
    "forward Euler uses the rate from the start of the step, so it overshoots the true curve here"
'''},
                    {"name": "the error is measured against the same times", "code": r'''
_e = max_error(1600.0, 1e-7, 1.0, 1e-6, 1e-3)
assert abs(_e - 0.0011526264528429753) < 1e-9, \
    f"at dt = 1 us the largest gap is 1.1526e-3 V, got {_e}"
'''},
                    {"name": "halving the timestep halves the error", "code": r'''
_coarse = max_error(1600.0, 1e-7, 1.0, 2e-6, 1e-3)
_fine = max_error(1600.0, 1e-7, 1.0, 1e-6, 1e-3)
_finer = max_error(1600.0, 1e-7, 1.0, 5e-7, 1e-3)
assert _coarse > _fine > _finer > 0, \
    f"the error must fall as dt falls: got {_coarse}, {_fine}, {_finer}"
assert abs(_coarse / _fine - 2.0) < 0.05, \
    f"forward Euler is first order, so this ratio should be about 2; got {_coarse / _fine}"
assert abs(_fine / _finer - 2.0) < 0.05, \
    f"and so should this one; got {_fine / _finer}"
'''},
                    {"name": "too large a step destroys the answer", "code": r'''
import numpy as np
_t, _v = rc_step(1600.0, 1e-7, 1.0, 3.5e-4, 2e-3)
assert float(np.min(_v)) < -0.5, \
    ("with dt = 350 us against tau = 160 us the method is unstable and the voltage "
     f"should swing negative; the lowest value was {np.min(_v)}")
assert float(np.max(np.abs(_v))) > 2.0, \
    "an unstable run grows without bound, so some value should exceed twice the supply"
'''},
                ],
            },
        },
        # ---- M9 -----------------------------------------------------------
        {
            "title": "Two states at once",
            "summary": "One rate and one unknown was the easy case. A circuit with two places to put energy needs two numbers to say where it is, and they have to be stepped forward together.",
            "concepts": [
                "The *state* of a system is the smallest set of numbers that, with the input, fixes its whole future. An RC circuit has one — the capacitor voltage. Put an inductor beside the capacitor and there are two, because the current is now something the circuit remembers.",
                "A capacitor ties its current to the rate of change of its voltage, `C dv/dt = i`. An inductor ties its voltage to the rate of change of its current, `L di/dt = v`. Wire the two together and each one supplies the other's rate: `dv/dt = -i/C` and `di/dt = v/L`.",
                "Nothing about the integration is new. Forward Euler is still `next = now + dt * rate`; there are simply two of them, and both rates are worked out from the *current* pair before either value is replaced.",
                "The pair oscillates at `w0 = 1/sqrt(L*C)` radians per second, energy moving back and forth between the magnetic field in the inductor and the charge on the capacitor and never leaving.",
                "The stored energy is `0.5*C*v**2 + 0.5*L*i**2`. Nothing in the equations removes it, so a simulation whose energy climbs is reporting the error of its own integrator and nothing about the circuit.",
                "*Semi-implicit* Euler updates one state and then uses the value it has just written to update the other. It is a one-character change in the code, and it turns energy that grows without bound into a small bounded wobble.",
            ],
            "sandbox": {
                "title": "A state is a point, and time is a path",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "initial": {"a11": 0, "a12": 1, "a21": -1, "a22": 0},
                "brief": r'''
Two states means the picture is a plane rather than a line. Every point is one
complete state of the system — a voltage and a current, or a displacement and a
speed — and running time forward traces a path through it.

The little strokes are the direction the state moves from wherever you are: the
right-hand side of the two equations, drawn everywhere at once. The coloured curves
are eight runs started around a ring. The four sliders are the coefficients, so
$\dot{x}_1 = a_{11}x_1 + a_{12}x_2$ and $\dot{x}_2 = a_{21}x_1 + a_{22}x_2$.

The line under the picture names the two numbers that decide the behaviour, and
what it calls the result.
''',
                "notice": [
                    "It opens on $\\dot{x}_1 = x_2$ and $\\dot{x}_2 = -x_1$, which is the oscillator with the timescale chosen so that one radian per second falls out. The read-out says trace 0, determinant 1, a centre: closed loops that neither grow nor shrink. Those loops are the two states of an LC circuit taking turns to hold the energy.",
                    "Follow one curve all the way round. It does not quite close — each turn ends a little further out than the one before. Nothing in these equations adds energy, so that creep is not the system: it is the picture's own forward Euler, stepping along the tangent and landing just outside the circle every single time. Measuring that error is what the lab does.",
                    "Set $a_{22}$ to −0.6. The trace goes negative, the read-out changes to a stable spiral, and every path now winds into the origin instead of circling it. That coefficient is the loss — a resistor in the circuit, friction in the mechanism — and it is the difference between a system that rings for ever and one that settles.",
                    "Put $a_{22}$ back to 0 and take $a_{21}$ from −1 to −0.25. The determinant falls to 0.25, the oscillation halves in frequency, and the loops flatten into wide ellipses: the same displacement now comes with half the rate. The outward creep nearly vanishes at the same time, because the error of a step depends on how far the state moves during it.",
                ],
            },
            "quiz": {
                "title": "Stepping a pair forward",
                "minutes": 9,
                "questions": [
                    {
                        "q": "How many numbers do you need to say where an LC circuit is, so that its whole future follows?",
                        "opts": ["One", "Two", "Three", "It depends on the values of L and C"],
                        "a": 1,
                        "why": (
                            "Two: the capacitor voltage and the inductor current. Knowing only the voltage "
                            "is not enough, because the same voltage with the current running one way and "
                            "with it running the other leads to completely different futures. The count is "
                            "one per independent energy store and has nothing to do with the values — "
                            "changing L and C changes how fast it oscillates, not how many numbers describe it."
                        ),
                    },
                    {
                        "q": "A capacitor obeys `C dv/dt = i`. Written as a rate to step forward, what is `dv/dt`?",
                        "opts": ["`i / C`", "`C / i`", "`C * i`", "`i * dt / C`"],
                        "a": 0,
                        "why": (
                            "`i / C`. Divide both sides by the capacitance, and note what it says: a large "
                            "capacitor changes its voltage slowly for the same current, which is exactly "
                            "why a big one is used to hold a supply rail steady. Including `dt` in the rate "
                            "is the standard slip — the timestep belongs in the step, `v = v + dt * rate`, "
                            "not in the rate itself."
                        ),
                    },
                    {
                        "q": "You step both states forward with forward Euler. Which is the correct one step?",
                        "opts": [
                            "`v = v + dt * (-i / C)` then `i = i + dt * (v / L)`, using the `v` you just wrote",
                            "Compute both rates from the current `v` and `i`, then update both",
                            "`i = i + dt * (v / L)` then `v = v + dt * (-i / C)`, using the `i` you just wrote",
                            "Update `v` with `dt`, and `i` with `dt / 2`",
                        ],
                        "a": 1,
                        "why": (
                            "Forward Euler evaluates every rate at the state you are stepping *from*, so "
                            "both rates come from the old pair and both values are then replaced. Writing "
                            "one update and immediately reading the new value in the next line gives a "
                            "different method — semi-implicit Euler, which is better behaved here and is "
                            "the point of the last part of the lab. Neither is wrong; they are just not the "
                            "same method, and a plot cannot tell you which one you wrote."
                        ),
                    },
                    {
                        "q": "Your LC simulation's total energy is 3% higher after five cycles than it was at the start. What does that tell you?",
                        "opts": [
                            "The circuit is resonating and gaining energy",
                            "There is a sign error in one of the two equations",
                            "The integrator is adding energy that the equations do not contain",
                            "The timestep is too small",
                        ],
                        "a": 2,
                        "why": (
                            "The integrator is adding it. An ideal L and C exchange energy and never create "
                            "it, so any drift in the total is a property of the numerical method rather "
                            "than of the circuit. It is a wonderfully cheap check: you get an exact "
                            "quantity the true solution must conserve, for nothing, and any departure from "
                            "it measures your error without needing the analytic answer at all."
                        ),
                    },
                    {
                        "q": "With L = 10 mH and C = 100 nF, roughly what is `w0 = 1/sqrt(L*C)`?",
                        "opts": [
                            "about 3.2 rad/s",
                            "about 3 200 rad/s",
                            "about 32 000 rad/s",
                            "about 3.2 million rad/s",
                        ],
                        "a": 2,
                        "why": (
                            "About 31 600 rad/s, which is 5.03 kHz. The product is 10⁻² × 10⁻⁷ = 10⁻⁹, its "
                            "square root is 3.16 × 10⁻⁵, and one over that is 3.16 × 10⁴. Getting the "
                            "exponent right matters more than the digits: it tells you the period is about "
                            "200 µs, and therefore what timestep could possibly resolve it — a few "
                            "microseconds, not a few milliseconds."
                        ),
                    },
                    {
                        "q": "Semi-implicit Euler differs from forward Euler by using a freshly updated state in the second line. What does that buy for an oscillator?",
                        "opts": [
                            "The answer becomes exact",
                            "The error per step becomes second order instead of first",
                            "The energy stops growing without bound and instead wobbles within a fixed band",
                            "It allows any timestep at all, however large",
                        ],
                        "a": 2,
                        "why": (
                            "The energy stops running away. Both methods are first order and both are "
                            "wrong by an amount proportional to `dt`, so the semi-implicit answer is not "
                            "more accurate over one step — but its error stops accumulating in one "
                            "direction. Over a long run that is worth far more than accuracy per step, "
                            "which is why the same idea underlies the integrators used for orbits and for "
                            "molecular dynamics. Too large a timestep still breaks it."
                        ),
                    },
                ],
            },
            "numeric": {
                "title": "How much current does the energy become?",
                "minutes": 8,
                "brief": r'''
A capacitor is charged to 5 V and then connected across an inductor with no current
flowing in it yet. Nothing dissipates: the loop is an ideal L and an ideal C.

The energy has to go somewhere, and there is only one other place for it. A quarter
of a cycle later the capacitor is empty and every joule that was in it is in the
inductor's magnetic field instead.

The two stores are

$$E_C = \tfrac{1}{2}Cv^2 \qquad E_L = \tfrac{1}{2}Li^2$$

Answer in **milliamps**.
''',
                "prompt": "What is the largest current the inductor ever carries?",
                "note": "No resistance anywhere, so nothing is lost on the way across.",
                # A text figure rather than a schematic, deliberately. The whole
                # question is about a state the circuit is already in at t = 0 — the
                # capacitor holding 5 V, the inductor holding no current — and a
                # drawn schematic cannot say that. The solver starts every capacitor
                # at zero volts and every inductor at zero amps and takes its
                # excitation only from sources, so the loop as drawn sits at rest
                # forever and the number it produces is 0, not 15.81 mA. Redrawing it
                # as something the solver can excite — a 5 V step into a series L and
                # C — would give the same peak, but it is a different circuit with a
                # source feeding it, and the lab immediately below integrates exactly
                # this one, from exactly these initial conditions.
                "figure": r'''
```text
                i(t) -->
        +--------UUUU--------+
        |     L = 10 mH      |
       ===  C = 100 nF       |
        |                    |
        +--------------------+

   at t = 0:   v_C = 5.00 V,   i_L = 0,   and no resistance anywhere
```

One capacitor and one inductor in a loop, and nothing else. There is no source: the
energy is already in the circuit before the clock starts, sitting in the electric
field between the capacitor's plates.
''',
                "given": [
                    {"label": "C", "value": "100 nF"},
                    {"label": "L", "value": "10 mH"},
                    {"label": "Capacitor voltage at t = 0", "value": "5.00 V"},
                    {"label": "Inductor current at t = 0", "value": "0"},
                ],
                "aside": "The peak current happens exactly when the capacitor voltage passes through "
                         "zero, because that is the moment all of the energy has arrived.",
                "answer": 15.81,
                "tol": 0.2,
                "unit": "mA",
                "hint": "Set the two energies equal: $\\tfrac{1}{2}Cv^2 = \\tfrac{1}{2}Li^2$. The halves "
                        "cancel, and rearranging gives $i = v\\sqrt{C/L}$.",
                "wrong": "Check the ratio inside the square root. $\\sqrt{C/L}$ is small here because "
                         "the capacitance is small and the inductance is not; $\\sqrt{L/C}$ upside down "
                         "would give 1580 A, which no 100 nF capacitor is going to supply.",
                "why": "$i = 5\\sqrt{10^{-7}/10^{-2}} = 5\\sqrt{10^{-5}} = 5 \\times 3.162\\times10^{-3}$ "
                       "= 15.8 mA. The quantity $\\sqrt{L/C}$ has units of ohms and is called the "
                       "characteristic impedance of the pair — 316 Ω here — and the peak "
                       "current is simply the peak voltage divided by it, exactly as though it were a "
                       "resistance. Your simulation must reproduce this number, and how closely it does "
                       "is one measure of whether the timestep was small enough.",
            },
            "lab": {
                "title": "An oscillation, and the energy the integrator invents",
                "runtime": "python",
                "minutes": 38,
                "brief": r'''
The LC pair from the question above, simulated two ways, with the total energy used
as the referee.

The equations are

```text
dv/dt = -i / C
di/dt =  v / L
```

`lc_euler(l, c, v0, dt, tstop)` returns three arrays — times, voltages and currents —
using forward Euler. Build the time axis exactly as in module 8:
`n = int(round(tstop / dt)) + 1` points spaced by `dt`. Start at `v[0] = v0` and
`i[0] = 0`. Then, for each step, compute **both** next values from the **current**
pair:

```text
v[k + 1] = v[k] - dt * i[k] / c
i[k + 1] = i[k] + dt * v[k] / l
```

`lc_semi(l, c, v0, dt, tstop)` is the same loop with two lines swapped and one value
changed: update the current first, then use that **new** current to update the
voltage.

```text
i[k + 1] = i[k] + dt * v[k] / l
v[k + 1] = v[k] - dt * i[k + 1] / c
```

`energy(l, c, v, i)` returns the array `0.5*c*v**2 + 0.5*l*i**2`, one value per
sample. Vectorised — no loop.

The last test is the one worth reading: run both for five cycles and compare what
each does to a quantity that is not allowed to change.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

L = 10e-3      # henries
C = 100e-9     # farads
V0 = 5.0       # volts on the capacitor at t = 0


def lc_euler(l, c, v0, dt, tstop):
    """Forward Euler on dv/dt = -i/c and di/dt = v/l. Returns (t, v, i)."""
    n = int(round(tstop / dt)) + 1
    t = dt * np.arange(n)
    v = np.zeros(n)
    i = np.zeros(n)
    v[0] = v0
    # TODO: both next values from the current pair.
    return t, v, i


def lc_semi(l, c, v0, dt, tstop):
    """Semi-implicit Euler: update i, then use the new i to update v."""
    n = int(round(tstop / dt)) + 1
    t = dt * np.arange(n)
    v = np.zeros(n)
    i = np.zeros(n)
    v[0] = v0
    # TODO: current first, then voltage from the current you just wrote.
    return t, v, i


def energy(l, c, v, i):
    """Total stored energy, one value per sample."""
    v = np.asarray(v, dtype=float)
    i = np.asarray(i, dtype=float)
    # TODO: 0.5*c*v**2 + 0.5*l*i**2, whole arrays at once.
    return np.zeros_like(v)


if __name__ == "__main__":
    w0 = 1.0 / np.sqrt(L * C)
    period = 2 * np.pi / w0
    dt = period / 200
    print("w0 =", round(w0, 1), "rad/s   period =", round(period * 1e6, 2), "us")
    for name, run in (("euler", lc_euler), ("semi ", lc_semi)):
        t, v, i = run(L, C, V0, dt, 5 * period)
        e = energy(L, C, v, i)
        print(name, "peak |i| =", round(float(np.max(np.abs(i))) * 1000, 3), "mA",
              " energy end/start =", round(float(e[-1] / e[0]), 4) if e[0] else "n/a")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

L = 10e-3      # henries
C = 100e-9     # farads
V0 = 5.0       # volts on the capacitor at t = 0


def lc_euler(l, c, v0, dt, tstop):
    """Forward Euler on dv/dt = -i/c and di/dt = v/l. Returns (t, v, i)."""
    n = int(round(tstop / dt)) + 1
    t = dt * np.arange(n)
    v = np.zeros(n)
    i = np.zeros(n)
    v[0] = v0
    for k in range(n - 1):
        v[k + 1] = v[k] - dt * i[k] / c
        i[k + 1] = i[k] + dt * v[k] / l
    return t, v, i


def lc_semi(l, c, v0, dt, tstop):
    """Semi-implicit Euler: update i, then use the new i to update v."""
    n = int(round(tstop / dt)) + 1
    t = dt * np.arange(n)
    v = np.zeros(n)
    i = np.zeros(n)
    v[0] = v0
    for k in range(n - 1):
        i[k + 1] = i[k] + dt * v[k] / l
        v[k + 1] = v[k] - dt * i[k + 1] / c
    return t, v, i


def energy(l, c, v, i):
    """Total stored energy, one value per sample."""
    v = np.asarray(v, dtype=float)
    i = np.asarray(i, dtype=float)
    return 0.5 * c * v * v + 0.5 * l * i * i


if __name__ == "__main__":
    w0 = 1.0 / np.sqrt(L * C)
    period = 2 * np.pi / w0
    dt = period / 200
    print("w0 =", round(w0, 1), "rad/s   period =", round(period * 1e6, 2), "us")
    for name, run in (("euler", lc_euler), ("semi ", lc_semi)):
        t, v, i = run(L, C, V0, dt, 5 * period)
        e = energy(L, C, v, i)
        print(name, "peak |i| =", round(float(np.max(np.abs(i))) * 1000, 3), "mA",
              " energy end/start =", round(float(e[-1] / e[0]), 4) if e[0] else "n/a")
'''}],
                "hints": [
                    "In `lc_euler` the order of the two assignment lines must not matter, and it only does not matter if the right-hand sides both read `v[k]` and `i[k]`. If you find yourself reading `v[k + 1]` on the second line you have written the other method by accident.",
                    "In `lc_semi` that accident is the whole point, deliberately: `i[k + 1]` appears on the right of the voltage line. One index, and it changes the long-run behaviour completely.",
                    "The sign on the voltage update is negative. With `+` the pair does not oscillate at all — both states grow exponentially, which is the same circuit with the inductor connected backwards and is not what the equations say.",
                    "`energy` needs no loop: `0.5 * c * v * v + 0.5 * l * i * i` works on the whole arrays and returns an array of the same length.",
                ],
                "tests": [
                    {"name": "the run starts where it was told to", "code": r'''
import numpy as np
_w0 = 1.0 / np.sqrt(L * C)
_T = 2 * np.pi / _w0
_dt = _T / 200
_t, _v, _i = lc_euler(L, C, V0, _dt, 5 * _T)
assert len(_t) == 1001, f"five periods in steps of T/200 is 1000 steps and 1001 points, got {len(_t)}"
assert abs(float(_v[0]) - 5.0) < 1e-12, f"the capacitor starts at 5 V, got {_v[0]}"
assert abs(float(_i[0])) < 1e-18, f"the inductor starts with no current, got {_i[0]}"
assert abs(float(_v[1]) - 5.0) < 1e-15, \
    ("the first voltage step is driven by the current, which is still zero, so v[1] is "
     f"still 5 V; got {_v[1]}")
assert abs(float(_i[1]) - _dt * 5.0 / L) < 1e-15, \
    f"the first current step is dt*v0/L = {_dt * 5.0 / L}; got {_i[1]}"
'''},
                    {"name": "energy is the sum of the two stores", "code": r'''
import numpy as np
_e = energy(L, C, np.array([5.0, 0.0]), np.array([0.0, 0.0158113883008419]))
assert abs(float(_e[0]) - 1.25e-6) < 1e-15, \
    f"0.5 * 100 nF * 25 V^2 is 1.25 uJ; got {_e[0]}"
assert abs(float(_e[1]) - 1.25e-6) < 1e-12, \
    ("at the peak current all of that energy is in the inductor, so the total is the "
     f"same 1.25 uJ; got {_e[1]}")
assert _e.shape == (2,), f"one energy per sample, so the shape should be (2,); got {_e.shape}"
'''},
                    {"name": "the peak current is near the value energy predicts", "code": r'''
import numpy as np
_w0 = 1.0 / np.sqrt(L * C)
_T = 2 * np.pi / _w0
_dt = _T / 200
_t, _v, _i = lc_euler(L, C, V0, _dt, 5 * _T)
_want = 5.0 * np.sqrt(C / L)
assert abs(float(_i[50]) - _want) / _want < 0.05, \
    (f"a quarter of a period in, the current should be near {_want * 1000:.2f} mA; "
     f"got {float(_i[50]) * 1000:.2f} mA")
assert float(_v[50]) < 0.05 * 5.0, \
    f"and the capacitor should be nearly empty at that moment; got {_v[50]} V"
'''},
                    {"name": "forward Euler manufactures energy, at a rate you can predict", "code": r'''
import numpy as np
_w0 = 1.0 / np.sqrt(L * C)
_T = 2 * np.pi / _w0
_dt = _T / 200
_t, _v, _i = lc_euler(L, C, V0, _dt, 5 * _T)
_e = energy(L, C, _v, _i)
_ratio = float(_e[-1] / _e[0])
_predicted = (1 + (_dt * _w0) ** 2) ** 1000
assert abs(_ratio - _predicted) / _predicted < 1e-6, \
    ("each step multiplies the stored energy by exactly 1 + (dt*w0)**2, so after 1000 "
     f"steps the ratio must be {_predicted:.6f}; got {_ratio:.6f}")
assert _ratio > 2.6, "which is a factor of about 2.68 - the run has nearly tripled its own energy"
'''},
                    {"name": "the semi-implicit run keeps its energy inside a band", "code": r'''
import numpy as np
_w0 = 1.0 / np.sqrt(L * C)
_T = 2 * np.pi / _w0
_dt = _T / 200
_t, _v, _i = lc_semi(L, C, V0, _dt, 5 * _T)
_e = energy(L, C, _v, _i)
assert abs(float(_v[0]) - 5.0) < 1e-12, f"same starting state; got {_v[0]}"
assert float(_e.max() / _e.min()) < 1.05, \
    (f"the energy should wobble by a few per cent and no more; the run spans a factor "
     f"of {float(_e.max() / _e.min()):.4f}")
assert abs(float(_e[-1] / _e[0]) - 1.0) < 1e-3, \
    (f"and after five whole cycles it should be back where it started to within a "
     f"tenth of a per cent; got {float(_e[-1] / _e[0]):.6f}")
'''},
                    {"name": "the two methods are visibly different runs", "code": r'''
import numpy as np
_w0 = 1.0 / np.sqrt(L * C)
_T = 2 * np.pi / _w0
_dt = _T / 200
_, _ve, _ie = lc_euler(L, C, V0, _dt, 5 * _T)
_, _vs, _is = lc_semi(L, C, V0, _dt, 5 * _T)
assert float(np.max(np.abs(_ve))) > 7.0, \
    (f"the forward-Euler voltage grows past 8 V over five cycles; the largest was "
     f"{float(np.max(np.abs(_ve))):.3f} V")
assert float(np.max(np.abs(_vs))) < 5.05, \
    (f"the semi-implicit voltage never meaningfully exceeds the 5 V it started with; "
     f"the largest was {float(np.max(np.abs(_vs))):.3f} V")
assert abs(float(_ie[1]) - float(_is[1])) < 1e-18, \
    "the very first current step is identical in both, because both read the same v[0]"
'''},
                    {"name": "a coarse step wrecks the explicit run and not the other", "code": r'''
import numpy as np
_w0 = 1.0 / np.sqrt(L * C)
_T = 2 * np.pi / _w0
_dt = _T / 20
_, _ve, _ie = lc_euler(L, C, V0, _dt, 5 * _T)
_, _vs, _is = lc_semi(L, C, V0, _dt, 5 * _T)
_ee = energy(L, C, _ve, _ie)
_es = energy(L, C, _vs, _is)
assert float(_ee[-1] / _ee[0]) > 1000, \
    (f"ten times the timestep, and forward Euler ends four orders of magnitude up; "
     f"got a factor of {float(_ee[-1] / _ee[0]):.1f}")
assert float(_es.max() / _es.min()) < 1.5, \
    (f"the semi-implicit run at the same coarse step stays within about 40 per cent; "
     f"got a factor of {float(_es.max() / _es.min()):.3f}")
'''},
                ],
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "Finding a root you cannot solve for",
            "summary": "Design questions arrive as 'what value gives me this answer', and the algebra usually will not rearrange. EE111 module 8 owns the two methods that answer them; here they are written as code, with the failures a caller has to be told about.",
            "concepts": [
                "The mathematics below belongs to EE111 module 8, *Equations that will not rearrange*, which develops bisection and Newton's method and applies them to a diode. The two courses run alongside each other, so nothing here assumes you have met it and the summary of the methods is stated in full. What this module adds is the code: a solver that takes the function as an argument rather than having one baked in, that raises instead of returning a plausible number when its assumptions do not hold, and that stops on a rule you chose rather than after a fixed number of passes.",
                "A *root* of `f` is an `x` with `f(x) = 0`. Almost every question of the form *what value of R gives me 3.3 V* becomes one, by moving everything onto one side.",
                "*Bracketing*: if `f` is continuous and `f(a)` and `f(b)` have opposite signs, a root lies somewhere between them. That is the entire guarantee bisection rests on, which is why the bracket must be checked and not assumed.",
                "*Bisection*: halve the bracket and keep the half whose ends still straddle zero. Each step halves the uncertainty, so after `n` steps the bracket is `(b - a) / 2**n` wide — about forty steps to go from a metre to a picometre, and never any faster.",
                "*Newton*: follow the tangent to where it crosses zero, `x - f(x)/f'(x)`. It roughly doubles the number of correct digits per step, needs a derivative, and can wander off entirely from a bad start or a flat spot.",
                "Bisection cannot fail once bracketed and cannot be fast. Newton can be very fast and can fail. Serious solvers use the first to get close and the second to finish.",
                "The equations worth this trouble are the ones with no rearrangement at all: `cos x = x`, or the time at which a ringing step response first reaches 90% of where it is going.",
            ],
            "tune": {
                "title": "Land a second-order system on 500 Hz without a resonant peak",
                "minutes": 10,
                "brief": r'''
Three sliders, two requirements, and no formula in front of you that gives R, L and C
from the answer you want.

The frequency comes from L and C together, through $\omega_n = 1/\sqrt{LC}$, so there
is a whole family of pairs that hit it. The damping comes from all three, through
$\zeta = \tfrac{R}{2}\sqrt{C/L}$, so choosing the pair is not the end of it — the
resistor still has to be picked to suit whichever pair you chose. Move one slider and
both read-outs change.

Watch what you actually do here. You will guess, read the result, decide which way to
move and by how much, and repeat until both numbers are inside their windows. That is
a root finder, run by eye, and the lab writes it down.
''',
                "prompt": "Put the natural frequency at 500 Hz and keep the peak gain at 1.02 or below.",
                "note": "A peak gain of 1 means no resonant rise at all. Both windows have to hold at once.",
                "model": "rlc",
                "initial": {"r": 100, "l": 100, "c": 2.5},
                "plotKey": "",
                "constraints": [
                    {"k": "fn", "label": "fₙ = 500 Hz ± 3", "eq": 500.0, "tol": 3.0},
                    {"k": "peak", "label": "peak gain ≤ 1.02", "max": 1.02},
                ],
            },
            "quiz": {
                "title": "Which method, and what it promises",
                "minutes": 9,
                "questions": [
                    {
                        "q": "You want the resistance that makes a divider output 3.30 V. What do you hand a root finder?",
                        "opts": [
                            "The function `vout(r)`",
                            "The function `vout(r) - 3.30`",
                            "The number 3.30",
                            "The function `3.30 / vout(r)`",
                        ],
                        "a": 1,
                        "why": (
                            "`vout(r) - 3.30`, because a root finder looks for a zero and the target has to "
                            "be moved onto the same side as everything else. Handing it `vout(r)` finds the "
                            "resistance that gives no output at all. The ratio is worse than useless: it "
                            "equals 1 at the answer and never reaches zero, and it blows up wherever the "
                            "output passes through zero instead."
                        ),
                    },
                    {
                        "q": "Bisection needs `f(a)` and `f(b)` to have opposite signs. What should your code do when they do not?",
                        "opts": [
                            "Return the midpoint, as the best available guess",
                            "Widen the bracket automatically until they do",
                            "Raise an exception naming the two ends and their values",
                            "Return 0 to signal that no root was found",
                        ],
                        "a": 2,
                        "why": (
                            "Raise. There may be no root in that interval, or there may be two, and the "
                            "method has nothing to offer in either case — everything it guarantees follows "
                            "from the sign change. Returning a number would be a made-up answer wearing "
                            "the same type as a real one. Widening on its own initiative is worse still: "
                            "the caller asked about a particular range for a reason, usually a physical one."
                        ),
                    },
                    {
                        "q": "A bracket 2 wide, and you need the root to 10⁻⁶. Roughly how many bisection steps?",
                        "opts": ["about 6", "about 21", "about 100", "about 1 000 000"],
                        "a": 1,
                        "why": (
                            "About 21. Each step halves the interval, so you need 2/2ⁿ below 10⁻⁶, which is "
                            "2ⁿ above 2 × 10⁶, and 2²¹ is 2.1 million. The useful thing about this count is "
                            "that it is fixed in advance and does not depend on the function at all: "
                            "bisection's speed is a property of the method, which is exactly what makes it "
                            "the one you fall back on."
                        ),
                    },
                    {
                        "q": "Newton's method is applied to `f(x) = x**2 - 2` starting from `x = 0`. What happens?",
                        "opts": [
                            "It converges to about 1.414 in a few steps",
                            "It converges to −1.414 instead",
                            "It divides by zero, because the derivative `2x` is 0 there",
                            "It converges, but needs about 40 steps",
                        ],
                        "a": 2,
                        "why": (
                            "The derivative is `2x`, which is zero at the start, so the very first step "
                            "divides by zero. Geometrically the tangent there is horizontal and never "
                            "crosses the axis, so there is nowhere to go. This is Newton's weakness in its "
                            "clearest form: it is fast when it works and it has no safety net, so a "
                            "practical implementation checks the derivative and raises rather than "
                            "producing an infinity."
                        ),
                    },
                    {
                        "q": "Bisection has a bracket of `[1, 2]` for `sqrt(2)` and Newton is started at `x = 1`. After four steps, which is closer?",
                        "opts": [
                            "Bisection, because it cannot go wrong",
                            "Newton, by a very large margin",
                            "They are about equally close",
                            "Neither has moved appreciably yet",
                        ],
                        "a": 1,
                        "why": (
                            "Newton, and not narrowly. Four bisections take a bracket of width 1 down to "
                            "1/16, so about one decimal place. Four Newton steps from 1 give "
                            "1.5, 1.4167, 1.414216, 1.4142136 — roughly doubling the correct digits each "
                            "time, and already at the limit of what a double can hold. The price is that "
                            "Newton offers no guarantee at all, while bisection's one-decimal-place answer "
                            "was certain before it started."
                        ),
                    },
                    {
                        "q": "Why is the time at which a ringing step response first reaches 90% a job for a root finder?",
                        "opts": [
                            "Because the formula involves a square root",
                            "Because the equation mixes an exponential with a sine and cannot be rearranged for t",
                            "Because the answer depends on the timestep of the simulation",
                            "Because the response is only known as measured data",
                        ],
                        "a": 1,
                        "why": (
                            "The response has `t` inside an exponential and inside a sine and a cosine at "
                            "once, and no rearrangement gets `t` alone on one side. That is what "
                            "*transcendental* means, and it is extremely common: the moment two different "
                            "kinds of function multiply each other, the algebra stops and the numerics "
                            "start. The function itself is perfectly easy to evaluate, which is all a root "
                            "finder ever needs."
                        ),
                    },
                ],
            },
            "derive": {
                "title": "Newton's method turns into a square root",
                "minutes": 12,
                "vars": ["x", "a"],
                "brief": r'''
Every machine you have used computes square roots, and none of them does it by
magic. Take the root of $a$ to be the positive solution of

$$f(x) = x^2 - a = 0$$

and apply Newton's step $x \mapsto x - f(x)/f'(x)$. What falls out is more than
three thousand years older than Newton — it was known to the Babylonians — and is
three lines of code.
''',
                "steps": [
                    {
                        "prompt": "Differentiate $f(x) = x^2 - a$ with respect to $x$. Remember that $a$ is a constant here.",
                        "answer": "2 x",
                        "hint": "The derivative of $x^2$ is $2x$, and the derivative of a constant is 0.",
                        "deconstruct": [
                            "$\\frac{d}{dx}x^2 = 2x$.",
                            "$a$ does not depend on $x$, so it contributes nothing.",
                        ],
                    },
                    {
                        "prompt": "Substitute $f$ and $f'$ into $x - f(x)/f'(x)$. Write it without simplifying.",
                        "answer": "x - \\frac{x^{2} - a}{2 x}",
                        "hint": "Put $x^2 - a$ over $2x$ and subtract the whole fraction from $x$.",
                        "deconstruct": [
                            "$f(x) = x^2 - a$ goes on top.",
                            "$f'(x) = 2x$ goes underneath.",
                            "The whole fraction is subtracted from $x$, not just its numerator.",
                        ],
                    },
                    {
                        "prompt": "Put that over the single denominator $2x$ and simplify the numerator.",
                        "answer": "\\frac{x^{2} + a}{2 x}",
                        "hint": "$x$ is $\\frac{2x^2}{2x}$, so the numerator becomes $2x^2 - (x^2 - a)$.",
                        "deconstruct": [
                            "$x = \\dfrac{2x^2}{2x}$.",
                            "$2x^2 - (x^2 - a) = x^2 + a$; note the sign change on both terms of the bracket.",
                        ],
                    },
                    {
                        "prompt": "That update is exactly one half of a sum of two terms. Write the sum.",
                        "answer": "x + \\frac{a}{x}",
                        "hint": "Split the single fraction into two, each still over $2x$, and take the factor of a half outside.",
                        "deconstruct": [
                            "$\\dfrac{x^2 + a}{2x} = \\dfrac{x^2}{2x} + \\dfrac{a}{2x}$.",
                            "$\\dfrac{x^2}{2x} = \\dfrac{x}{2}$ and $\\dfrac{a}{2x} = \\dfrac{1}{2}\\cdot\\dfrac{a}{x}$.",
                        ],
                    },
                ],
                "closing": r'''
Read the result as a sentence and it stops looking like calculus at all. Guess $x$.
If your guess is too large then $a/x$ is too small by roughly as much, and if it is
too small then $a/x$ is too large. So average them, and try again.

That reading also explains the speed. The two numbers straddle the answer, so each
average lands roughly at the midpoint of an interval that shrinks quadratically:
from a guess of 1 for $\sqrt{2}$ you have four correct digits after three steps and
sixteen after five. There is nothing else to it, and a `while` loop around this line
is what the lab asks you to write.
''',
            },
            "lab": {
                "title": "Two root finders, and a question only they can answer",
                "runtime": "python",
                "minutes": 38,
                "brief": r'''
Four functions. The first two are general tools; the last two use them.

`bisect(f, a, b, tol)` returns a root of `f` between `a` and `b`. Evaluate `f` at
both ends first: if either is exactly zero, that end is the answer, and if the two
have the *same* sign, raise a `ValueError` — there is no bracket and nothing to do.
Then halve repeatedly, keeping whichever half still straddles zero, until the bracket
is no wider than `tol`, and return its midpoint.

`newton(f, fp, x0, tol, maxit)` takes the function and its derivative. Each step is
`x = x - f(x)/fp(x)`. Raise a `ValueError` if the derivative is ever exactly zero, and
raise again if `maxit` steps go by without the step size falling to `tol` or below —
a solver that loops for ever is worse than one that gives up.

`sqrt_newton(a)` is the derivation, in code: start from `x = a` when `a >= 1` and from
`x = 1` otherwise, and repeat `x = 0.5 * (x + a / x)` until it stops moving by more
than a relative `1e-12`. Return 0.0 for `a = 0` and raise a `ValueError` for negative
`a`. Do not call `math.sqrt` anywhere in it.

`rise_time(zeta, wn)` returns the first time the unit step response reaches 0.9.
`step_response` is given to you. The response climbs monotonically from 0 up to its
first peak at `t = pi / wd`, and the peak of an underdamped system is above 1, so
`[0, pi / wd]` is a bracket that always works — which is the engineering in this
function. Raise a `ValueError` unless `0 < zeta < 1`, because the formula given is
only that case.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def bisect(f, a, b, tol=1e-9, maxit=200):
    """A root of f between a and b, to within tol. Raises on a bad bracket."""
    # TODO: check the ends, then halve.
    return 0.0


def newton(f, fp, x0, tol=1e-12, maxit=50):
    """A root of f from x0, following the tangent. Raises rather than looping."""
    # TODO
    return 0.0


def sqrt_newton(a, tol=1e-12):
    """The square root of a, by repeated averaging. No math.sqrt."""
    # TODO: guard a < 0 and a == 0, then loop on x = 0.5 * (x + a / x).
    return 0.0


def step_response(zeta, wn, t):
    """The unit step response of a second-order system, for 0 < zeta < 1."""
    wd = wn * math.sqrt(1 - zeta * zeta)
    return 1 - math.exp(-zeta * wn * t) * (
        math.cos(wd * t) + zeta / math.sqrt(1 - zeta * zeta) * math.sin(wd * t))


def rise_time(zeta, wn, frac=0.9):
    """The first time the step response reaches frac of its final value."""
    # TODO: guard zeta, build the bracket [0, pi/wd], and bisect.
    return 0.0


if __name__ == "__main__":
    print("cos(x) = x at x =", bisect(lambda x: math.cos(x) - x, 0.0, 1.0, 1e-12))
    print("sqrt(2) by bisection:", bisect(lambda x: x * x - 2, 1.0, 2.0, 1e-12))
    print("sqrt(2) by Newton:   ", newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0))
    print("sqrt(2) by averaging:", sqrt_newton(2.0))
    print("rise time, zeta 0.35, wn 4:", rise_time(0.35, 4.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def bisect(f, a, b, tol=1e-9, maxit=200):
    """A root of f between a and b, to within tol. Raises on a bad bracket."""
    fa = f(a)
    fb = f(b)
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0:
        raise ValueError("f(%g) and f(%g) have the same sign; that is not a bracket"
                         % (a, b))
    for _ in range(maxit):
        if b - a <= tol:
            break
        m = 0.5 * (a + b)
        fm = f(m)
        if fm == 0.0:
            return m
        if fa * fm < 0:
            b = m
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


def newton(f, fp, x0, tol=1e-12, maxit=50):
    """A root of f from x0, following the tangent. Raises rather than looping."""
    x = float(x0)
    for _ in range(maxit):
        d = fp(x)
        if d == 0.0:
            raise ValueError("the derivative is zero at x = %g; the tangent never "
                             "crosses" % x)
        step = f(x) / d
        x = x - step
        if abs(step) <= tol:
            return x
    raise ValueError("no convergence in %d iterations" % maxit)


def sqrt_newton(a, tol=1e-12):
    """The square root of a, by repeated averaging. No math.sqrt."""
    if a < 0:
        raise ValueError("%g has no real square root" % a)
    if a == 0:
        return 0.0
    x = a if a >= 1 else 1.0
    for _ in range(100):
        nxt = 0.5 * (x + a / x)
        if abs(nxt - x) <= tol * nxt:
            return nxt
        x = nxt
    return x


def step_response(zeta, wn, t):
    """The unit step response of a second-order system, for 0 < zeta < 1."""
    wd = wn * math.sqrt(1 - zeta * zeta)
    return 1 - math.exp(-zeta * wn * t) * (
        math.cos(wd * t) + zeta / math.sqrt(1 - zeta * zeta) * math.sin(wd * t))


def rise_time(zeta, wn, frac=0.9):
    """The first time the step response reaches frac of its final value."""
    if not 0 < zeta < 1:
        raise ValueError("this response is only defined for 0 < zeta < 1, not %g" % zeta)
    wd = wn * math.sqrt(1 - zeta * zeta)
    tpk = math.pi / wd
    return bisect(lambda t: step_response(zeta, wn, t) - frac, 0.0, tpk, 1e-12)


if __name__ == "__main__":
    print("cos(x) = x at x =", bisect(lambda x: math.cos(x) - x, 0.0, 1.0, 1e-12))
    print("sqrt(2) by bisection:", bisect(lambda x: x * x - 2, 1.0, 2.0, 1e-12))
    print("sqrt(2) by Newton:   ", newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0))
    print("sqrt(2) by averaging:", sqrt_newton(2.0))
    print("rise time, zeta 0.35, wn 4:", rise_time(0.35, 4.0))
'''}],
                "hints": [
                    "In `bisect`, keep `fa` alongside `a` and update the two together. Re-evaluating `f(a)` every pass is not wrong, only wasteful, but it hides the fact that the sign at the left end is the thing being carried forward.",
                    "The comparison that decides which half to keep is `fa * fm < 0`: opposite signs mean the root is in the left half, so the right end moves in. Getting this backwards converges beautifully to the wrong end of the interval.",
                    "`newton` must raise twice, for two different failures: a zero derivative on any step, and running out of iterations. Both are the same lesson as module 7 — a solver that returns a number it does not believe is worse than one that stops.",
                    "In `rise_time` the bracket is the engineering. `step_response(zeta, wn, 0)` is 0, which is below 0.9, and the value at `pi / wd` is the overshoot peak, which is above 1. Between them the response is climbing, so there is exactly one crossing.",
                ],
                "tests": [
                    {"name": "bisection finds a root it was given a bracket for", "code": r'''
import math
_r = bisect(lambda x: x * x - 2, 1.0, 2.0, 1e-12)
assert abs(_r - math.sqrt(2)) < 1e-9, f"expected 1.41421356, got {_r}"
_d = bisect(lambda x: math.cos(x) - x, 0.0, 1.0, 1e-12)
assert abs(_d - 0.7390851332151607) < 1e-9, \
    f"cos(x) = x at 0.739085; got {_d}"
_neg = bisect(lambda x: x + 3, -10.0, 0.0, 1e-12)
assert abs(_neg + 3.0) < 1e-9, f"a root at -3 is still a root; got {_neg}"
'''},
                    {"name": "an end that is already a root is returned as it stands", "code": r'''
_e = bisect(lambda x: x * x - 4, 2.0, 5.0, 1e-12)
assert abs(_e - 2.0) < 1e-15, \
    f"f(2) is exactly 0, so 2 is the answer without any halving; got {_e}"
'''},
                    {"name": "a pair of ends that does not straddle zero is refused", "code": r'''
_raised = False
try:
    bisect(lambda x: x * x + 1, 0.0, 1.0, 1e-12)
except ValueError:
    _raised = True
assert _raised, \
    "x**2 + 1 is positive at both ends and has no real root at all; that must raise"
_raised2 = False
try:
    bisect(lambda x: x - 5, 0.0, 1.0, 1e-12)
except ValueError:
    _raised2 = True
assert _raised2, \
    "x - 5 does have a root, but not between 0 and 1, and bisection cannot find it there"
'''},
                    {"name": "Newton converges fast and refuses a flat start", "code": r'''
import math
_n = newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0)
assert abs(_n - math.sqrt(2)) < 1e-12, f"expected 1.4142135623730951, got {_n}"
_c = newton(lambda x: math.cos(x) - x, lambda x: -math.sin(x) - 1, 0.5)
assert abs(_c - 0.7390851332151607) < 1e-12, f"got {_c}"
_flat = False
try:
    newton(lambda x: x * x + 1, lambda x: 2 * x, 0.0)
except ValueError:
    _flat = True
assert _flat, \
    "the derivative 2x is zero at the starting point, so the tangent is horizontal and " \
    "there is nowhere to step; that must raise rather than divide by zero"
'''},
                    {"name": "the square root is the derivation, running", "code": r'''
import math
for _a in (2.0, 10.0, 1.0, 1e-6, 1e12, 0.25):
    _s = sqrt_newton(_a)
    assert abs(_s - math.sqrt(_a)) <= 1e-9 * math.sqrt(_a), \
        f"sqrt({_a}) should be {math.sqrt(_a)}, got {_s}"
assert sqrt_newton(0.0) == 0.0, "zero is its own square root and must not divide by it"
_neg = False
try:
    sqrt_newton(-4.0)
except ValueError:
    _neg = True
assert _neg, "a negative argument has no real square root and must raise"
'''},
                    {"name": "the rise time is where the response says it is", "code": r'''
_rt = rise_time(0.35, 4.0)
assert abs(_rt - 0.46635280722419215) < 1e-6, \
    f"with zeta 0.35 and wn 4 the response first reaches 0.9 at t = 0.46635; got {_rt}"
assert abs(step_response(0.35, 4.0, _rt) - 0.9) < 1e-9, \
    "whatever time you returned, the response there must actually be 0.9"
assert abs(rise_time(0.7, 10.0) - 0.2631037015465947) < 1e-6, \
    f"got {rise_time(0.7, 10.0)}"
'''},
                    {"name": "rise time scales the way the equations say it must", "code": r'''
_slow = rise_time(0.35, 4.0)
_fast = rise_time(0.35, 8.0)
assert abs(_slow / _fast - 2.0) < 1e-6, \
    (f"time enters the response only as wn*t, so doubling wn must halve every time in "
     f"it; got a ratio of {_slow / _fast}")
_bad = False
try:
    rise_time(1.4, 4.0)
except ValueError:
    _bad = True
assert _bad, "the formula given covers 0 < zeta < 1 only, so an overdamped system must raise"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Match a simulation to a bench measurement",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
A rig on the bench has the low-pass filter you drew: a resistor, a capacitor, a
step of 1 V at the input, and a 12-bit converter watching the output at 100 kHz for
one millisecond. `rig.py` gives you that capture as a block of text, exactly as the
logger wrote it — comments, blank line and all.

Your job is to decide whether a simulation of that circuit agrees with what the rig
actually did, and to be able to say why you believe the answer.

Three separate questions, and they must not be confused with one another:

1. **Can I read the data?** Turn the log into arrays.
2. **Is my integrator right?** Compare the simulation with the analytic solution of
   the same equation, and shrink the timestep until they agree to a stated
   tolerance. This tests the code and nothing else.
3. **Is the model right?** Compare the converged simulation with the *measurement*.
   Only this step can tell you anything about the circuit.

## Suggested order

Write `parse_log` first and print how many samples came back; then `exact`, which is
one line; then `simulate`, which you have already written once. `converged_dt` is a
loop around the two of them, and `compare` needs `np.interp` because the simulation
runs on a much finer time axis than the logger recorded. `report` just puts the
pieces together and states a verdict.

The rig's true component values are in `rig.py`. Feeding `report` a *wrong* capacitance
must make it disagree — a report that says yes whatever you give it is worth nothing.
''',
        "deliverables": [
            "`parse_log(text)` returning the times and voltages of the capture as two NumPy arrays, ignoring blank lines and `#` comments.",
            "`exact(r, c, vin, t)` returning the analytic step response of the RC circuit at an array of times.",
            "`simulate(r, c, vin, dt, tstop)` returning the forward-Euler solution of the same equation on a time axis starting at 0 and spaced by `dt`.",
            "`converged_dt(r, c, vin, tstop, tol)` returning the largest timestep of the form `tau / 2**k` whose worst-case error against `exact` is below `tol`, and raising a `ValueError` when no reachable step qualifies.",
            "`compare(log_t, log_v, r, c, vin, dt)` returning the largest gap between the simulation, interpolated onto the logger's sample times, and the measured values.",
            "`report(text, r, c, vin, tol)` returning a dictionary with `samples`, `dt`, `mismatch` and `agrees`, and a comment at the top of `main.py` saying what tolerance you chose and why.",
        ],
        "constraints": [
            "NumPy and the standard library only.",
            "Do not edit `rig.py`; the checks rely on the values in it.",
            "The comparison with the measurement must use the timestep that `converged_dt` returned, so that any mismatch is the model's and not the integrator's.",
            "`converged_dt` must raise rather than loop for ever when the tolerance is unreachable, and must give up before the run would need more than 200 000 steps — an unbounded search does not merely take a long time, it asks for an array of 10¹² elements.",
            "`compare` must interpolate the simulation onto the logger's times. Do not force the simulation to run at the logger's sample rate, which is far too coarse to have converged.",
        ],
        "rubric": [
            {"criterion": "Reading the capture", "weight": 20,
             "evidence": "`parse_log` returns 101 float samples from the rig log, skipping the comment lines and the blank line, with the first time 0 and the last 1 ms."},
            {"criterion": "Integrator correctness", "weight": 30,
             "evidence": "`simulate` starts at 0 V and reproduces the forward-Euler value 1 - 0.75**4 at four steps of tau/4; `exact` gives 0.63212 at one time constant."},
            {"criterion": "Demonstrated convergence", "weight": 30,
             "evidence": "`converged_dt` returns a timestep meeting the tolerance whose double does not, showing the answer was taken at the coarsest step that qualifies rather than at an arbitrarily small one."},
            {"criterion": "Honest verdict", "weight": 20,
             "evidence": "`report` agrees with the rig for the true component values and disagrees when the capacitance is moved by 30%, so the verdict carries information."},
        ],
        "hints": [
            "`parse_log` is the reader from module 3 with a different file in front of it. Strip each line, skip the empty ones and those starting with `#`, split on the comma.",
            "`converged_dt` starts at `dt = r * c` — one whole time constant, certainly too coarse — and halves. Stop and raise a `ValueError` once forty candidate steps have been tried, and also as soon as `tstop / dt` would exceed 200 000 steps: an impossible tolerance would otherwise send the timestep towards zero and ask NumPy for an array of a trillion elements.",
            "Return the *first* `dt` that meets the tolerance. Because you are halving, that is by construction the largest qualifying step, which is what the check about the double asks for.",
            "`np.interp(log_t, t, v)` reads the simulation at the logger's sample times. It needs `t` increasing, which it is.",
            "The quantisation of the 12-bit converter puts a floor of about 0.12 mV on any possible agreement, so a tolerance of 2 mV is comfortable and 0.05 mV is not achievable no matter how good your code is.",
        ],
        "files": [
            {"name": "rig.py", "ro": True, "content": r'''
"""The bench rig. Do not edit - the checks rely on these numbers."""
import math

R = 1600.0        # ohms
C = 1e-7          # farads
VIN = 1.0         # volts, applied as a step at t = 0
BITS = 12         # the converter's resolution


def bench_log(fs=100000.0, tstop=1e-3):
    """The capture, as the logger wrote it: 'time,volts' with comments and a gap."""
    lines = ["# t_seconds,volts -- 12-bit capture, 100 kHz", ""]
    n = int(round(tstop * fs)) + 1
    full = 2.0 ** BITS - 1.0
    for i in range(n):
        t = i / fs
        v = VIN * (1.0 - math.exp(-t / (R * C)))
        q = round(v * full) / full
        lines.append("%.8f,%.6f" % (t, q))
    return "\n".join(lines) + "\n"
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from rig import bench_log, R, C, VIN

# Tolerance chosen: TODO, and why.


def parse_log(text):
    """Read 'time,volts' lines into two float arrays, skipping blanks and comments."""
    times = []
    values = []
    # TODO
    return np.array(times), np.array(values)


def exact(r, c, vin, t):
    """The analytic step response of the RC circuit at the times in t."""
    t = np.asarray(t, dtype=float)
    # TODO
    return np.zeros_like(t)


def simulate(r, c, vin, dt, tstop):
    """Forward Euler on dv/dt = (vin - v)/(r*c). Returns (times, voltages)."""
    n = int(round(tstop / dt)) + 1
    t = dt * np.arange(n)
    v = np.zeros(n)
    # TODO
    return t, v


MAX_STEPS = 200000


def converged_dt(r, c, vin, tstop, tol, dt0=None):
    """The largest dt of the form (r*c)/2**k whose error against exact is below tol."""
    if dt0 is None:
        dt0 = r * c
    # TODO: halve until the worst-case error is under tol. Give up and raise a
    # ValueError once forty steps have been tried, or as soon as tstop / dt
    # exceeds MAX_STEPS.
    return dt0


def compare(log_t, log_v, r, c, vin, dt):
    """Largest gap between the simulation and the measured values, at the log times."""
    # TODO: simulate as far as the log goes, interpolate onto log_t, compare.
    return 0.0


def report(text, r, c, vin, tol=2e-3):
    """Read, converge, compare, and state a verdict."""
    # TODO: return {"samples": ..., "dt": ..., "mismatch": ..., "agrees": ...}
    return {"samples": 0, "dt": 0.0, "mismatch": 0.0, "agrees": False}


if __name__ == "__main__":
    log = bench_log()
    t, v = parse_log(log)
    print("samples:", len(t))
    print("true values: ", report(log, R, C, VIN))
    print("C 30% high:  ", report(log, R, C * 1.3, VIN))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from rig import bench_log, R, C, VIN

# Tolerance chosen: 2 mV. The rig quantises to 12 bits over 1 V, so a single code
# is 0.24 mV and the rounding alone can be half of that. Anything tighter than
# about 0.5 mV would be measuring the converter rather than the model; 2 mV leaves
# room for that floor and still rejects a 30% error in C by a factor of nearly 50.


def parse_log(text):
    """Read 'time,volts' lines into two float arrays, skipping blanks and comments."""
    times = []
    values = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        left, right = line.split(",")
        times.append(float(left))
        values.append(float(right))
    return np.array(times), np.array(values)


def exact(r, c, vin, t):
    """The analytic step response of the RC circuit at the times in t."""
    t = np.asarray(t, dtype=float)
    return vin * (1.0 - np.exp(-t / (r * c)))


def simulate(r, c, vin, dt, tstop):
    """Forward Euler on dv/dt = (vin - v)/(r*c). Returns (times, voltages)."""
    tau = r * c
    n = int(round(tstop / dt)) + 1
    t = dt * np.arange(n)
    v = np.zeros(n)
    for i in range(n - 1):
        v[i + 1] = v[i] + dt * (vin - v[i]) / tau
    return t, v


MAX_STEPS = 200000


def converged_dt(r, c, vin, tstop, tol, dt0=None):
    """The largest dt of the form (r*c)/2**k whose error against exact is below tol."""
    if dt0 is None:
        dt0 = r * c
    dt = dt0
    for _ in range(40):
        if tstop / dt > MAX_STEPS:
            break
        t, v = simulate(r, c, vin, dt, tstop)
        err = float(np.max(np.abs(v - exact(r, c, vin, t))))
        if err < tol:
            return dt
        dt = dt * 0.5
    raise ValueError("no reachable timestep met the tolerance " + str(tol))


def compare(log_t, log_v, r, c, vin, dt):
    """Largest gap between the simulation and the measured values, at the log times."""
    log_t = np.asarray(log_t, dtype=float)
    log_v = np.asarray(log_v, dtype=float)
    t, v = simulate(r, c, vin, dt, float(np.max(log_t)))
    return float(np.max(np.abs(np.interp(log_t, t, v) - log_v)))


def report(text, r, c, vin, tol=2e-3):
    """Read, converge, compare, and state a verdict."""
    t, v = parse_log(text)
    dt = converged_dt(r, c, vin, float(np.max(t)), tol * 0.25)
    mismatch = compare(t, v, r, c, vin, dt)
    return {
        "samples": int(t.size),
        "dt": dt,
        "mismatch": mismatch,
        "agrees": bool(mismatch < tol),
    }


if __name__ == "__main__":
    log = bench_log()
    t, v = parse_log(log)
    print("samples:", len(t))
    print("true values: ", report(log, R, C, VIN))
    print("C 30% high:  ", report(log, R, C * 1.3, VIN))
'''},
        ],
        "tests": [
            {"name": "the capture is read correctly", "code": r'''
import numpy as np
from rig import bench_log
_t, _v = parse_log(bench_log())
assert _t.size == 101 and _v.size == 101, \
    f"1 ms at 100 kHz is 101 samples including both ends; got {_t.size}"
assert _v.dtype.kind == "f", f"the values must be floats, not text; got dtype {_v.dtype}"
assert abs(float(_t[0])) < 1e-15, f"the capture starts at t = 0, got {_t[0]}"
assert abs(float(_t[-1]) - 1e-3) < 1e-12, f"and ends at 1 ms, got {_t[-1]}"
assert abs(float(_v[0])) < 1e-15, f"the capacitor starts empty, got {_v[0]}"
assert abs(float(_v[-1]) - 0.998046) < 1e-9, f"the last reading is 0.998046 V, got {_v[-1]}"
'''},
            {"name": "the analytic solution is the analytic solution", "code": r'''
import numpy as np
from rig import R, C, VIN
_tau = R * C
_e = exact(R, C, VIN, np.array([0.0, _tau, 5 * _tau]))
assert abs(float(_e[0])) < 1e-15, f"it starts at 0 V, got {_e[0]}"
assert abs(float(_e[1]) - 0.6321205588285577) < 1e-12, \
    f"one time constant in, 1 - exp(-1) = 0.63212; got {_e[1]}"
assert abs(float(_e[2]) - 0.9932620530009145) < 1e-12, \
    f"five time constants in, 0.99326; got {_e[2]}"
'''},
            {"name": "the integrator really is forward Euler", "code": r'''
import numpy as np
from rig import R, C, VIN
_tau = R * C
_t, _v = simulate(R, C, VIN, _tau / 4, 1e-3)
assert abs(float(_v[0])) < 1e-15, f"the run starts at 0 V, got {_v[0]}"
assert abs(float(_t[4]) - _tau) < 1e-15, f"four steps of tau/4 land on tau, got {_t[4]}"
assert abs(float(_v[4]) - 0.68359375) < 1e-12, \
    ("each step of tau/4 closes a quarter of the gap, so after four steps the value is "
     f"1 - 0.75**4 = 0.68359375; got {_v[4]}")
_tf, _vf = simulate(R, C, VIN, 1e-6, 1e-3)
assert abs(float(_vf[-1]) - 0.9981070390083471) < 1e-9, \
    f"at dt = 1 us the run ends at 0.99811 V, got {_vf[-1]}"
'''},
            {"name": "convergence is demonstrated, not assumed", "code": r'''
import numpy as np
from rig import R, C, VIN
_tol = 5e-4
_dt = converged_dt(R, C, VIN, 1e-3, _tol)
_t, _v = simulate(R, C, VIN, _dt, 1e-3)
_err = float(np.max(np.abs(_v - exact(R, C, VIN, _t))))
assert _err < _tol, f"the returned dt = {_dt} still has error {_err}, above the tolerance {_tol}"
_t2, _v2 = simulate(R, C, VIN, 2 * _dt, 1e-3)
_err2 = float(np.max(np.abs(_v2 - exact(R, C, VIN, _t2))))
assert _err2 >= _tol, \
    (f"twice the returned dt has error {_err2}, which also meets the tolerance - "
     "return the largest qualifying step, not an arbitrarily small one")
assert abs(_dt - 3.125e-7) < 1e-12, \
    f"halving from tau = 1.6e-4, the first step to qualify is 3.125e-7 s; got {_dt}"
'''},
            {"name": "convergence gives up rather than looping for ever", "code": r'''
from rig import R, C, VIN
_raised = False
try:
    converged_dt(R, C, VIN, 1e-3, 1e-30)
except ValueError:
    _raised = True
except Exception as _e:
    raise AssertionError(f"expected a ValueError for an unreachable tolerance, got {type(_e).__name__}")
assert _raised, "an unreachable tolerance must raise, not return a timestep that does not meet it"
_t2, _v2 = simulate(R, C, VIN, 1e-6, 1e-3)
assert len(_t2) == 1001, "and the search must stop long before the timestep reaches zero"
'''},
            {"name": "the comparison uses the logger's own sample times", "code": r'''
import numpy as np
from rig import bench_log, R, C, VIN
_t, _v = parse_log(bench_log())
_m = compare(_t, _v, R, C, VIN, 1e-6)
assert abs(_m - 0.0012417652665180912) < 1e-6, \
    ("at dt = 1 us the worst gap between simulation and measurement is 1.2418e-3 V, "
     f"which is mostly the integrator's own error; got {_m}")
_wrong = compare(_t, _v, R, C * 1.3, VIN, 1e-6)
assert _wrong > 0.05, \
    f"a capacitance 30% high should miss the measurement badly; got {_wrong}"
'''},
            {"name": "the verdict carries information", "code": r'''
from rig import bench_log, R, C, VIN
_log = bench_log()
_good = report(_log, R, C, VIN)
for _k in ("samples", "dt", "mismatch", "agrees"):
    assert _k in _good, f"the report needs a {_k!r} key; got {sorted(_good)}"
assert _good["samples"] == 101, f"expected 101 samples, got {_good['samples']}"
assert _good["agrees"] is True, \
    f"with the rig's own values the simulation should agree; mismatch was {_good['mismatch']}"
assert _good["mismatch"] < 2e-3, f"the mismatch should be under the 2 mV tolerance, got {_good['mismatch']}"
_bad = report(_log, R, C * 1.3, VIN)
assert _bad["agrees"] is False, \
    "a capacitance 30% high must be rejected, or the report says yes to anything"
assert _bad["mismatch"] > 10 * _good["mismatch"], \
    (f"the wrong model should miss by far more than the right one: "
     f"{_bad['mismatch']} against {_good['mismatch']}")
'''},
        ],
    },
}
