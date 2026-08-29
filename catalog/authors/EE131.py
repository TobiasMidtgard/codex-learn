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
    ],
    "assessment": "Four quizzes, two circuits drawn and measured in the schematic editor, four Python labs checked by execution, and a capstone that simulates a measured circuit and proves the simulation right.",
    "reading": [
        "*Think Python*, Downey — chapters 1 to 6, freely available online.",
        "The NumPy *absolute beginner's guide*, in the official documentation.",
        "*Numerical Methods in Engineering with Python*, Kiusalaas — chapter 7, for Euler and what comes after it.",
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
                            "The second. It asks the engineering question — is the gap small compared with "
                            "the quantity — and it is symmetric, so a reading above and a reading below are "
                            "treated alike. The third option drops the `abs`, so any measurement that is far "
                            "too low passes. Rounding turns a tolerance into a step: 4.4 and 4.6 differ by "
                            "about 4% and round to 4 and 5, and 4.49 and 4.51 barely differ and round apart."
                        ),
                    },
                ],
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
                            "a resistor at the same rate. The *mean* really is 0 V, which is the trap in the "
                            "last option — a mean of zero says nothing about how much signal is present."
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

        # ---- M4 -----------------------------------------------------------
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
                            "the step before being added to the value. The second option leaves `dt` out, "
                            "which makes the simulation's speed depend on how finely you chose to sample it "
                            "— always a sign the timestep has gone missing. The last option overwrites the "
                            "voltage with the rate, which is not even the right unit."
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
