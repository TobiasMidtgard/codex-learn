"""EE121 — Digital Logic and Boolean Algebra. Author module.

First year, no prerequisites: school arithmetic and nothing else. Every term is
defined where it is first used, and every module leads with a quiz that checks the
definition landed before anything is computed with it.

Authoring rules, as for the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number was produced by running the code, not assumed
"""

COURSE = {
    "id": "EE121",
    "title": "Digital Logic and Boolean Algebra",
    "band": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "▣",
    "summary": (
        "A digital circuit is an analogue circuit that has agreed to notice only two "
        "voltages. Everything else follows from that agreement: numbers written in twos, "
        "an algebra with two values, tables that specify a circuit completely, gates that "
        "realise the tables, and finally a loop of two gates that remembers. This course "
        "starts at counting and ends at a flip-flop, with a schematic editor and a Python "
        "runner to check every claim it makes."
    ),
    "outcomes": [
        "Convert between decimal, binary and hexadecimal, and say how many values a given number of bits can hold.",
        "Write the truth table of a Boolean expression, and use De Morgan's laws to move a complement across an AND or an OR.",
        "Turn a truth table into a sum-of-products expression and reduce it with a Karnaugh map.",
        "Explain what makes a circuit sequential, and how an edge-triggered flip-flop differs from a transparent latch.",
        "Relate a propagation delay measured on an RC circuit to the shortest clock period a synchronous design can use.",
    ],
    "assessment": (
        "Four quizzes and four small labs, all checked by execution, two circuits drawn and "
        "measured in the schematic editor, and a capstone that builds a counter and its "
        "display decoder from a truth table upwards."
    ),
    "reading": [
        "*Digital Design and Computer Architecture*, Harris & Harris — chapters 1 to 3 cover this whole course.",
        "*The Elements of Computing Systems*, Nisan & Schocken — chapters 1 to 3: logic, then arithmetic, then memory, in that order.",
        "*Code*, Petzold — no equations at all, and a patient account of why binary won.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Two voltages, and the numbers they carry",
            "summary": "Why binary, how place value works in any base, and what hexadecimal is for.",
            "concepts": [
                "A **bit** is one of two symbols, 0 and 1. In a circuit they are two voltage ranges: near 0 V and near the supply, with a forbidden band between them that no settled signal is allowed to sit in.",
                "Two ranges rather than ten because a gap of volts is easy to keep clean. Noise has to be enormous before a 0 is mistaken for a 1, and that tolerance is the whole reason digital electronics is reliable.",
                "**Place value**: a digit is worth its face value times the base raised to the position. In binary the places are 1, 2, 4, 8, 16 — each one double the last, counted from the right.",
                "An **n-bit** unsigned number holds $2^n$ different values, from 0 to $2^n - 1$. Four bits is a **nibble**, eight bits is a **byte**.",
                "**Hexadecimal** is base sixteen, with digits 0-9 then a-f. One hex digit is exactly four bits, so conversion is done in nibbles and never needs long division.",
                "Appending a 0 on the right multiplies by the base — by two in binary, by ten in decimal. It is the same fact both times.",
            ],
            "quiz": {
                "title": "Reading a number written in twos",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What is the binary number `1011` as a decimal number?",
                        "opts": ["11", "13", "23", "1011"],
                        "a": 0,
                        "why": (
                            "Counting from the **right**, the places are worth 1, 2, 4 and 8. The digits "
                            "1, 0, 1, 1 therefore select 8, nothing, 2 and 1, and 8 + 2 + 1 = 11. "
                            "Applying the places from the left instead gives 1 + 0 + 4 + 8 = 13, which is "
                            "the usual slip: in binary, exactly as in decimal, the smallest place is the "
                            "rightmost digit."
                        ),
                    },
                    {
                        "q": "How many different values can an 8-bit number take?",
                        "opts": ["8", "128", "255", "256"],
                        "a": 3,
                        "why": (
                            "Each extra bit doubles the count, so eight bits give $2^8 = 256$ patterns, "
                            "`00000000` through `11111111`. 255 is the largest *value*, not the number of "
                            "values — there are 256 of them because zero is one of them. Off-by-one "
                            "between $2^n$ and $2^n - 1$ is worth fixing here rather than in a debugger."
                        ),
                    },
                    {
                        "q": "The hexadecimal digit `b` stands for which four bits?",
                        "opts": ["1011", "1101", "1110", "0011"],
                        "a": 0,
                        "why": (
                            "`b` is eleven, and eleven is 8 + 2 + 1, so the nibble is 1011. Hexadecimal is "
                            "used precisely because one hex digit is exactly four bits: `0xb3` is "
                            "`1011 0011` and you never divide anything. `1101` is thirteen, which is `d`."
                        ),
                    },
                    {
                        "q": "What is the largest value a 4-bit unsigned number can hold?",
                        "opts": ["8", "15", "16", "31"],
                        "a": 1,
                        "why": (
                            "All four bits set is 8 + 4 + 2 + 1 = 15, which is $2^4 - 1$. 16 is how many "
                            "patterns there are; the largest value is one less than that because the "
                            "count starts at zero. This is the same distinction as the previous question, "
                            "asked from the other side."
                        ),
                    },
                    {
                        "q": "Writing an extra `0` on the right of a binary number — `1011` becomes `10110` — does what to its value?",
                        "opts": ["Adds one to it", "Doubles it", "Halves it", "Leaves it unchanged"],
                        "a": 1,
                        "why": (
                            "Every digit has moved one place to the left, and every place in binary is "
                            "worth twice the one to its right, so the value doubles: 11 becomes 22. In "
                            "decimal the same move multiplies by ten. The rule is not about zeros, it is "
                            "about the base — which is why processors implement 'multiply by two' as a "
                            "shift and get it for almost nothing."
                        ),
                    },
                ],
            },
            "build": {
                "title": "Place value, built out of resistors",
                "minutes": 25,
                "brief": r'''
A binary number is not just a row of symbols: each place is *worth* something, and
the worth doubles as you move left. This circuit makes that worth physical.

Two bits drive one shared node, each through its own resistor:

* the **twos bit** drives it through a resistor `R`
* the **ones bit** drives it through a resistor of **twice** that value, `2R`

A bit that is HIGH sits at 5 V. A bit that is LOW sits at 0 V, which is just ground.
Because a resistor's ability to pull a node is $1/R$, the twos bit pulls exactly
twice as hard as the ones bit. That is place value, in copper.

Build the case `10` in binary — twos bit HIGH, ones bit LOW:

* one 5 V source for the HIGH bit, its negative terminal at ground
* a resistor from that source to the shared node
* a resistor of **twice** the value from the shared node down to ground: that is the
  LOW bit, sitting at 0 V
* a probe on the shared node

`10` in binary is two, out of a full scale of `11` = three, so the node must land at
two thirds of 5 V, which is **3.33 V**. Any pair of resistors in a 1:2 ratio does it.
Keep the current the rail has to deliver below 1 mA.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [7, 3], "b": [9, 3]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3},
                        {"id": "p4", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 20000},
                        {"id": "p5", "kind": "GND", "x": 9, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [7, 3], "b": [9, 3]},
                        {"a": [9, 3], "b": [9, 4]},
                        {"a": [9, 6], "b": [9, 8]},
                    ],
                },
                "checks": [
                    {"name": "one 5 V rail stands for logic HIGH", "code": r'''
var vs = c.values('V');
var high = vs.filter(function (x) { return Math.abs(x - 5) < 0.005; });
c.assert(high.length === 1,
  'Exactly one source has to sit at 5 V — it is the HIGH bit. Found ' + high.length + '.');
c.assert(vs.every(function (x) { return Math.abs(x - 5) < 0.005 || Math.abs(x) < 0.005; }),
  'Every source here stands for a logic level, so each one is either 5 V (HIGH) or 0 V (LOW). ' +
  'Drawing the LOW bit as a wire to ground is the same circuit with one part fewer.');
'''},
                    {"name": "the probe sits on the shared node, not on the rail", "code": r'''
c.assert(c.count('R') >= 2, 'A two-bit weighted network needs a resistor for each bit — one to the rail, one to ground.');
c.assert(Math.abs(c.vout() - 5) > 0.1,
  'The probe is reading 5 V, so it is on the rail itself. Move it to the node where the two resistors meet.');
'''},
                    {"name": "the shared node sits at two thirds of the rail", "code": r'''
c.close(c.vout(), 10 / 3, 0.02,
  'the shared node for the input 10 (binary two, out of a full scale of three)');
'''},
                    {"name": "the rail delivers less than 1 mA", "code": r'''
var cur = c.dc().currents;
var mags = Object.keys(cur).map(function (k) { return Math.abs(cur[k]); });
c.assert(mags.length > 0, 'There is no source current to measure — is the rail connected to anything?');
var worst = Math.max.apply(null, mags);
c.assert(worst < 1e-3,
  'The rail is delivering ' + c.fmt(worst, 'A') + '. Keep it under 1 mA: scale both resistors up, ' +
  'keeping their 1:2 ratio, and the voltage does not change at all.');
'''},
                ],
                "hints": [
                    "With one bit HIGH and one bit LOW the network is an ordinary divider: the node sits at $5 \\times R_{\\text{low}} / (R_{\\text{high}} + R_{\\text{low}})$, where $R_{\\text{low}}$ is the resistor to ground.",
                    "Only the ratio matters. 10 kΩ to the rail and 20 kΩ to ground gives 3.33 V; so does 4.7 kΩ and 9.4 kΩ.",
                    "Under 1 mA from 5 V means at least 5 kΩ in the path, and the path here is $R + 2R = 3R$, so $R$ has to be above about 1.7 kΩ. 1 kΩ with 2 kΩ draws 1.67 mA and fails; 10 kΩ with 20 kΩ draws 0.17 mA.",
                    "The probe goes on the node where the two resistors meet — the wire between them, not either end of the rail.",
                ],
            },
            "lab": {
                "title": "Converting between the three bases",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
Three small functions, each written the way the place-value argument goes rather
than by calling `bin()` or `hex()`.

**`to_binary(n, width)`** — the binary string for a non-negative `n`, padded with
leading zeros to exactly `width` digits. `to_binary(13, 8)` is `"00001101"`.

**`from_binary(s)`** — the integer a binary string stands for. Work left to right,
doubling what you have so far and adding the next digit; that is the place-value
rule read forwards.

**`to_hex(n)`** — the lowercase hexadecimal string for `n`, with no `0x` prefix and
no leading zeros. `to_hex(0)` is `"0"`, `to_hex(2748)` is `"abc"`.
''',
                "files": [{"name": "main.py", "content": r'''
DIGITS = "0123456789abcdef"


def to_binary(n, width=8):
    """Binary string for n, zero-padded to `width` digits, most significant first."""
    # TODO: take one bit at a time, from the highest place down to the lowest.
    return ""


def from_binary(s):
    """The integer that the binary string s stands for."""
    # TODO: start at 0; for each character, double what you have and add the digit.
    return 0


def to_hex(n):
    """Lowercase hexadecimal for n, no prefix, no leading zeros. to_hex(0) == "0"."""
    # TODO: peel off n % 16 as one digit, then divide n by 16, until nothing is left.
    return ""


if __name__ == "__main__":
    print("13 in binary :", to_binary(13, 8))
    print("1011 back    :", from_binary("1011"))
    print("2748 in hex  :", to_hex(2748))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
DIGITS = "0123456789abcdef"


def to_binary(n, width=8):
    """Binary string for n, zero-padded to `width` digits, most significant first."""
    out = ""
    for place in range(width - 1, -1, -1):
        out += "1" if (n >> place) & 1 else "0"
    return out


def from_binary(s):
    """The integer that the binary string s stands for."""
    value = 0
    for ch in s:
        value = value * 2 + (1 if ch == "1" else 0)
    return value


def to_hex(n):
    """Lowercase hexadecimal for n, no prefix, no leading zeros. to_hex(0) == "0"."""
    if n == 0:
        return "0"
    out = ""
    while n > 0:
        out = DIGITS[n % 16] + out
        n //= 16
    return out


if __name__ == "__main__":
    print("13 in binary :", to_binary(13, 8))
    print("1011 back    :", from_binary("1011"))
    print("2748 in hex  :", to_hex(2748))
'''}],
                "hints": [
                    "`(n >> place) & 1` is the bit at that place: shift it down to the bottom, then keep only the last one.",
                    "In `from_binary`, `value = value * 2 + digit` is the whole loop — doubling is what moving one place left means.",
                    "`to_hex` needs its own answer for zero, because the loop `while n > 0` never runs and would return an empty string.",
                ],
                "tests": [
                    {"name": "to_binary pads to the requested width", "code": r'''
assert to_binary(13, 8) == "00001101", f'expected "00001101", got {to_binary(13, 8)!r}'
assert to_binary(0, 4) == "0000", f'zero is still four digits wide, got {to_binary(0, 4)!r}'
assert to_binary(255, 8) == "11111111", f'expected all ones, got {to_binary(255, 8)!r}'
'''},
                    {"name": "to_binary respects place value", "code": r'''
assert to_binary(1, 4) == "0001", "the ones place is the rightmost digit"
assert to_binary(8, 4) == "1000", "the eights place is the leftmost of four"
assert to_binary(6, 4) == "0110", f'6 = 4 + 2, so "0110"; got {to_binary(6, 4)!r}'
'''},
                    {"name": "from_binary reads a string back", "code": r'''
assert from_binary("1011") == 11, f'expected 11, got {from_binary("1011")}'
assert from_binary("0") == 0
assert from_binary("11111111") == 255, f'expected 255, got {from_binary("11111111")}'
'''},
                    {"name": "the two directions agree on every byte", "code": r'''
for _n in range(256):
    _s = to_binary(_n, 8)
    assert len(_s) == 8, f"{_n} produced {len(_s)} digits, not 8"
    assert from_binary(_s) == _n, f"{_n} became {_s!r} which read back as {from_binary(_s)}"
'''},
                    {"name": "to_hex is lowercase, unpadded, and right", "code": r'''
assert to_hex(0) == "0", f'zero should be "0", got {to_hex(0)!r}'
assert to_hex(10) == "a", f'ten is one digit, got {to_hex(10)!r}'
assert to_hex(16) == "10", f'sixteen is the first two-digit value, got {to_hex(16)!r}'
assert to_hex(255) == "ff", f'expected "ff", got {to_hex(255)!r}'
assert to_hex(2748) == "abc", f'expected "abc", got {to_hex(2748)!r}'
'''},
                    {"name": "one hex digit is exactly four bits", "code": r'''
for _n in range(16):
    _nibble = to_binary(_n, 4)
    assert from_binary(_nibble) == _n
    assert to_hex(_n) == "0123456789abcdef"[_n], \
        f"{_nibble} should print as {'0123456789abcdef'[_n]!r}, got {to_hex(_n)!r}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Boolean algebra and truth tables",
            "summary": "An algebra with two values, and the table that says everything there is to say about a function.",
            "concepts": [
                "A **Boolean variable** takes one of two values, 0 and 1. The three basic operations are **NOT** (invert), **AND** (1 only when both are 1) and **OR** (1 when either is 1).",
                "Notation: `A'` or a bar for NOT, `AB` or `A·B` for AND, `A + B` for OR. AND binds tighter than OR, exactly as multiplication binds tighter than addition.",
                "A **truth table** lists every combination of the inputs with the output for each. For $n$ inputs it has $2^n$ rows, and it is the complete specification — two expressions with the same table are the same function.",
                "The identities worth knowing by name: $A + 0 = A$, $A \\cdot 1 = A$, $A + 1 = 1$, $A \\cdot 0 = 0$, $A + A = A$, $A \\cdot A' = 0$, $A + A' = 1$, and absorption $A + AB = A$.",
                "**De Morgan's laws**: $(A + B)' = A'B'$ and $(AB)' = A' + B'$. Pushing a complement inwards flips the operation. This is the single most useful rewrite in the subject.",
                "**XOR**, written $A \\oplus B$, is 1 exactly when the inputs differ. It is not a basic operation but is common enough to be given a symbol.",
            ],
            "quiz": {
                "title": "Two values and the laws they obey",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What does `A AND (NOT A)` evaluate to?",
                        "opts": ["`A`", "`NOT A`", "0", "1"],
                        "a": 2,
                        "why": (
                            "There is no value of `A` for which `A` and `NOT A` are both 1, and AND needs "
                            "both, so the result is 0 whatever `A` is. Its partner law is `A OR (NOT A) = 1`, "
                            "which is 1 whatever `A` is for the mirror reason. Together they are what makes "
                            "this an algebra of two values rather than of numbers."
                        ),
                    },
                    {
                        "q": "`NOT (A OR B)` is the same as which of these?",
                        "opts": [
                            "`(NOT A) OR (NOT B)`",
                            "`(NOT A) AND (NOT B)`",
                            "`A AND B`",
                            "`(NOT A) AND B`",
                        ],
                        "a": 1,
                        "why": (
                            "This is De Morgan's law. In words: 'not either of them' means 'neither of them', "
                            "which is 'not A **and** not B'. Moving the complement inwards flips the OR into "
                            "an AND. Keeping the OR is the standard error, and one row settles it: with "
                            "A = 1 and B = 0, `NOT (1 OR 0)` is 0, while `(NOT 1) OR (NOT 0)` is `0 OR 1` = 1."
                        ),
                    },
                    {
                        "q": "How many rows does the truth table of a function of four inputs have?",
                        "opts": ["4", "8", "16", "32"],
                        "a": 2,
                        "why": (
                            "Each input doubles the number of combinations, so four inputs give $2^4 = 16$ "
                            "rows. 8 is the answer for three inputs. This is the same doubling as in "
                            "module 1: a truth table is just a count in binary with an answer column "
                            "written beside it."
                        ),
                    },
                    {
                        "q": "`A + A·B` simplifies to what?",
                        "opts": ["`A`", "`B`", "`A·B`", "`A + B`"],
                        "a": 0,
                        "why": (
                            "This is absorption. Whenever `A` is 1 the first term already makes the whole "
                            "expression 1, whatever `B` does; whenever `A` is 0 both terms are 0. So the "
                            "value never depends on `B` at all and the second term can be deleted. Note "
                            "how different `A + A'B` is — there the answer really is `A + B`."
                        ),
                    },
                    {
                        "q": "An XOR gate outputs 1 exactly when:",
                        "opts": [
                            "both inputs are 1",
                            "the two inputs differ",
                            "at least one input is 1",
                            "both inputs are 0",
                        ],
                        "a": 1,
                        "why": (
                            "XOR is the 'not equal' gate: 0 for 00 and 11, 1 for 01 and 10. 'At least one "
                            "input is 1' describes OR, which differs from XOR only on the row where both "
                            "are 1 — and that one row is the whole distinction. XOR is what an adder uses "
                            "for its sum bit, which is where you will meet it next."
                        ),
                    },
                ],
            },
            "lab": {
                "title": "Truth tables, and using them to settle an argument",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Two functions. Between them they turn "these expressions look the same" into
something a machine can decide.

**`truth_table(fn, n)`** — return the complete table of a function of `n` inputs, as
a list of `(inputs, output)` pairs. `inputs` is a tuple of 0s and 1s, most
significant first, and the rows are in counting order, so for `n = 3` row 5 is
`((1, 0, 1), ...)`. `fn` may return `True`/`False` rather than 1/0, so convert the
output to an `int` before storing it.

**`equivalent(f, g, n)`** — `True` when `f` and `g` agree on all $2^n$ rows. There
are only $2^n$ of them, so there is nothing clever to do: check them all.

With those two in hand, De Morgan stops being something to remember and becomes
something to test.
''',
                "files": [{"name": "main.py", "content": r'''
def truth_table(fn, n):
    """Every row of the truth table of `fn`, as (inputs_tuple, output_int) pairs."""
    rows = []
    # TODO: for each row number 0 .. 2**n - 1, build the input tuple (most
    # significant bit first) and call fn on it.
    return rows


def equivalent(f, g, n):
    """True when f and g give the same output on every one of the 2**n rows."""
    # TODO: compare the two functions row by row.
    return False


if __name__ == "__main__":
    for inputs, out in truth_table(lambda a, b: a and not b, 2):
        print(inputs, "->", out)
    print("De Morgan holds:",
          equivalent(lambda a, b: not (a or b),
                     lambda a, b: (not a) and (not b), 2))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def truth_table(fn, n):
    """Every row of the truth table of `fn`, as (inputs_tuple, output_int) pairs."""
    rows = []
    for row in range(2 ** n):
        inputs = tuple((row >> (n - 1 - k)) & 1 for k in range(n))
        rows.append((inputs, 1 if fn(*inputs) else 0))
    return rows


def equivalent(f, g, n):
    """True when f and g give the same output on every one of the 2**n rows."""
    for inputs, out in truth_table(f, n):
        if out != (1 if g(*inputs) else 0):
            return False
    return True


if __name__ == "__main__":
    for inputs, out in truth_table(lambda a, b: a and not b, 2):
        print(inputs, "->", out)
    print("De Morgan holds:",
          equivalent(lambda a, b: not (a or b),
                     lambda a, b: (not a) and (not b), 2))
'''}],
                "hints": [
                    "The row number *is* the input pattern read as a binary number, so `(row >> (n - 1 - k)) & 1` gives the k-th input counting from the left.",
                    "`fn(*inputs)` unpacks the tuple into separate arguments, so one line works for any `n`.",
                    "`1 if fn(...) else 0` normalises `True`/`False` and anything else truthy into the 0/1 you want to store.",
                    "`equivalent` can be written on top of `truth_table` — build the table of `f` and check `g` against each row.",
                ],
                "tests": [
                    {"name": "the table has the right shape and order", "code": r'''
_t = truth_table(lambda a, b, c: a and not b, 3)
assert len(_t) == 8, f"three inputs give 2**3 = 8 rows, got {len(_t)}"
assert _t[0][0] == (0, 0, 0), f"row 0 should be all zeros, got {_t[0][0]}"
assert _t[5][0] == (1, 0, 1), f"row 5 written in binary is 101, got {_t[5][0]}"
assert _t[7][0] == (1, 1, 1), f"the last row should be all ones, got {_t[7][0]}"
'''},
                    {"name": "outputs are stored as 0 and 1", "code": r'''
_t = truth_table(lambda a, b: a and b, 2)
assert all(o in (0, 1) and isinstance(o, int) and not isinstance(o, bool) for _, o in _t), \
    f"outputs should be the ints 0 and 1, got {[o for _, o in _t]}"
assert sum(o for _, o in _t) == 1, "AND is 1 on exactly one of the four rows"
'''},
                    {"name": "De Morgan survives the check", "code": r'''
assert equivalent(lambda a, b: not (a or b),
                  lambda a, b: (not a) and (not b), 2) is True, \
    "NOT(A OR B) really is (NOT A) AND (NOT B)"
assert equivalent(lambda a, b: not (a and b),
                  lambda a, b: (not a) or (not b), 2) is True, \
    "and the other law: NOT(A AND B) is (NOT A) OR (NOT B)"
'''},
                    {"name": "a wrong law is caught, and a right one is not", "code": r'''
assert equivalent(lambda a, b: not (a or b),
                  lambda a, b: (not a) or (not b), 2) is False, \
    "keeping the OR is wrong, and the row A=1 B=0 proves it — equivalent should say so"
assert equivalent(lambda a, b: a and b, lambda a, b: b and a, 2) is True, \
    "AND is symmetric, so this pair really is the same function — always answering False decides nothing"
'''},
                    {"name": "absorption and a three-input case", "code": r'''
assert equivalent(lambda a, b: a or (a and b), lambda a, b: a, 2) is True, \
    "A + AB = A"
assert equivalent(lambda a, b, c: (a and b) or (a and c),
                  lambda a, b, c: a and (b or c), 3) is True, \
    "AND distributes over OR"
assert equivalent(lambda a, b, c: a or b, lambda a, b, c: a or c, 3) is False, \
    "these differ on the row (0, 1, 0)"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "From table to gates: combinational design",
            "summary": "Every truth table has an expression, every expression has a circuit, and a Karnaugh map makes the circuit smaller.",
            "concepts": [
                "A **combinational** circuit's output depends only on its inputs right now. No memory, no clock: change the inputs and the output follows after a delay.",
                "A **minterm** is one row of the table where the output is 1, written as an AND of all the variables, each complemented if it is 0 in that row. Row `101` of three variables gives `A B' C`.",
                "**Canonical sum-of-products**: OR every minterm together. It always works, it is unique, and it is almost never the smallest.",
                "The one move behind all reduction is $XY + XY' = X$: if two terms differ in exactly one variable, that variable does not matter and drops out.",
                "A **Karnaugh map** is the truth table drawn so that neighbouring cells differ in one variable only — which is why the labels run 00, 01, 11, 10 rather than in counting order. Circling a block of adjacent 1s applies the rule above, visually.",
                "Block sizes are powers of two: a block of 2 removes one variable, a block of 4 removes two, a block of 8 removes three. Blocks wrap around the edges of the map.",
                "**NAND is universal**: NOT, AND and OR can all be built from NAND alone, so any circuit whatever can be built from one kind of gate. Real chips do lean on NAND, but for a separate reason — in CMOS a NAND costs less silicon than a NOR of the same width.",
                "The **half adder** adds two bits (sum = XOR, carry = AND). The **full adder** adds three, and chaining four of them gives a 4-bit adder.",
            ],
            "quiz": {
                "title": "Minterms, maps and adders",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A function of three variables is 1 in exactly five of its rows. How many AND terms does its canonical sum-of-products have?",
                        "opts": ["2", "3", "5", "8"],
                        "a": 2,
                        "why": (
                            "One minterm per row where the output is 1, so five terms — each an AND of all "
                            "three variables, ORed together. 8 is the number of rows in the table, and 3 is "
                            "the number of rows where the output is 0. The canonical form is never the "
                            "smallest expression; it is the one you can always write down without thinking."
                        ),
                    },
                    {
                        "q": "Why are the columns of a Karnaugh map labelled 00, 01, 11, 10 instead of 00, 01, 10, 11?",
                        "opts": [
                            "So the map is symmetric about its centre",
                            "So that neighbouring cells differ in exactly one variable",
                            "It is only a convention and any order works",
                            "So the row numbers increase along the map",
                        ],
                        "a": 1,
                        "why": (
                            "The whole point of the map is that adjacency means 'differs in one variable', "
                            "because that is the condition for $XY + XY' = X$ to apply. Counting order puts "
                            "01 next to 10, which differ in **two** variables, and circling them would be "
                            "wrong. The order 00, 01, 11, 10 is called Gray code and it is chosen for "
                            "exactly this property."
                        ),
                    },
                    {
                        "q": "In a four-variable Karnaugh map, a circled block of four adjacent 1s becomes a term with how many literals?",
                        "opts": ["1", "2", "3", "4"],
                        "a": 1,
                        "why": (
                            "Each doubling of the block size removes one variable: a single cell needs all "
                            "four literals, a block of 2 needs three, a block of 4 needs two, a block of 8 "
                            "needs one. So the answer is two. Bigger blocks are always better, and this is "
                            "why you look for the largest legal circles first."
                        ),
                    },
                    {
                        "q": "The carry-out of a full adder is 1 exactly when:",
                        "opts": [
                            "exactly one of its three inputs is 1",
                            "at least two of its three inputs are 1",
                            "all three of its inputs are 1",
                            "its sum output is 1",
                        ],
                        "a": 1,
                        "why": (
                            "A full adder adds three bits, and the total needs a carry as soon as it "
                            "reaches two. So carry-out is the **majority** function: `AB + AC + BC`. "
                            "'All three' is only the last of those four rows. The sum output is the "
                            "opposite kind of function — it is 1 when an *odd* number of inputs is 1, "
                            "which is XOR of all three."
                        ),
                    },
                    {
                        "q": "Which connection turns a two-input NAND gate into a NOT gate?",
                        "opts": [
                            "Tie both inputs to the same signal",
                            "Tie one input to 0 and feed the signal to the other",
                            "Tie both inputs to 1",
                            "Connect the output back to one of the inputs",
                        ],
                        "a": 0,
                        "why": (
                            "`A NAND A` is `NOT (A AND A)` = `NOT A`. Tying an input to 0 does the opposite "
                            "of what is wanted: an AND with 0 is always 0, so the NAND output is stuck at 1 "
                            "and the signal is ignored entirely. Holding the spare input at **1** would "
                            "also work, and connecting the output back to an input builds a loop — which is "
                            "not a mistake so much as the subject of the next module."
                        ),
                    },
                ],
            },
            "lab": {
                "title": "A full adder, and four of them in a row",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
The adder is the first circuit worth building, because it is where a truth table
turns into arithmetic.

**`full_adder(a, b, cin)`** — add three bits and return the pair `(sum, cout)`.
The sum bit is 1 when an odd number of the three inputs is 1; the carry-out is 1
when at least two of them are.

**`add4(a_bits, b_bits, cin=0)`** — add two 4-bit numbers and return
`(bits, cout)`. Both arguments are lists of four 0/1 values, **most significant
first**, and `bits` comes back in the same form. Work from the least significant
end, feeding each stage's carry-out into the next stage's carry-in. That chain is
called a ripple-carry adder, and it is exactly how the four full adders are wired.

Four bits wrap around: 15 + 1 is 0 with a carry-out of 1, which is not an error but
the honest answer of a circuit with only four wires.
''',
                "files": [{"name": "main.py", "content": r'''
def full_adder(a, b, cin):
    """Add three bits. Return (sum_bit, carry_out)."""
    # TODO: sum is 1 when an odd number of inputs is 1; carry when two or more are.
    return 0, 0


def add4(a_bits, b_bits, cin=0):
    """Add two 4-bit lists (most significant first). Return (bits, carry_out)."""
    out = [0, 0, 0, 0]
    # TODO: run from index 3 down to index 0, carrying as you go.
    return out, 0


def bits_of(n):
    """A convenience for the printout: n as four bits, most significant first."""
    return [(n >> place) & 1 for place in (3, 2, 1, 0)]


if __name__ == "__main__":
    print("1 + 1 + 1 =", full_adder(1, 1, 1))
    print("5 + 3 =", add4(bits_of(5), bits_of(3)))
    print("15 + 1 =", add4(bits_of(15), bits_of(1)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def full_adder(a, b, cin):
    """Add three bits. Return (sum_bit, carry_out)."""
    total = a + b + cin
    return total % 2, 1 if total >= 2 else 0


def add4(a_bits, b_bits, cin=0):
    """Add two 4-bit lists (most significant first). Return (bits, carry_out)."""
    out = [0, 0, 0, 0]
    carry = cin
    for i in range(3, -1, -1):
        out[i], carry = full_adder(a_bits[i], b_bits[i], carry)
    return out, carry


def bits_of(n):
    """A convenience for the printout: n as four bits, most significant first."""
    return [(n >> place) & 1 for place in (3, 2, 1, 0)]


if __name__ == "__main__":
    print("1 + 1 + 1 =", full_adder(1, 1, 1))
    print("5 + 3 =", add4(bits_of(5), bits_of(3)))
    print("15 + 1 =", add4(bits_of(15), bits_of(1)))
'''}],
                "hints": [
                    "`a ^ b ^ cin` is the sum bit — XOR is exactly 'an odd number of these is 1'. Adding the three and taking the remainder on division by 2 says the same thing.",
                    "The carry is `1 if a + b + cin >= 2 else 0`, which is the majority function from the quiz.",
                    "In `add4`, index 3 is the **least** significant bit because the lists are most significant first. `range(3, -1, -1)` walks them in the right order.",
                    "The carry variable starts at `cin` and is overwritten by each stage; whatever is left in it at the end is the carry-out.",
                ],
                "tests": [
                    {"name": "the full adder matches its truth table", "code": r'''
_want = {(0, 0, 0): (0, 0), (0, 0, 1): (1, 0), (0, 1, 0): (1, 0), (0, 1, 1): (0, 1),
         (1, 0, 0): (1, 0), (1, 0, 1): (0, 1), (1, 1, 0): (0, 1), (1, 1, 1): (1, 1)}
for _row, _exp in _want.items():
    _got = tuple(full_adder(*_row))
    assert _got == _exp, f"full_adder{_row} should be {_exp}, got {_got}"
'''},
                    {"name": "add4 adds a simple pair", "code": r'''
_bits, _c = add4([0, 1, 0, 1], [0, 0, 1, 1])
assert _bits == [1, 0, 0, 0] and _c == 0, \
    f"5 + 3 should be 1000 with no carry, got {_bits} carry {_c}"
'''},
                    {"name": "four bits wrap around, and say so", "code": r'''
_bits, _c = add4([1, 1, 1, 1], [0, 0, 0, 1])
assert _bits == [0, 0, 0, 0], f"15 + 1 should wrap to 0000, got {_bits}"
assert _c == 1, "the carry-out is how the circuit reports that it ran out of bits"
'''},
                    {"name": "the carry-in is honoured", "code": r'''
_bits, _c = add4([0, 1, 1, 1], [0, 0, 0, 0], 1)
assert _bits == [1, 0, 0, 0] and _c == 0, \
    f"7 + 0 + 1 should be 1000, got {_bits} carry {_c}"
'''},
                    {"name": "every pair of 4-bit numbers adds correctly", "code": r'''
def _val(bs):
    return bs[0] * 8 + bs[1] * 4 + bs[2] * 2 + bs[3]
for _a in range(16):
    for _b in range(16):
        _bits, _c = add4(bits_of(_a), bits_of(_b))
        assert _val(_bits) == (_a + _b) % 16, \
            f"{_a} + {_b} gave {_val(_bits)}, expected {(_a + _b) % 16}"
        assert _c == (_a + _b) // 16, \
            f"{_a} + {_b} gave carry {_c}, expected {(_a + _b) // 16}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Circuits that remember: latches, flip-flops and the clock",
            "summary": "Feed an output back to an input and the circuit acquires a past. Then everything becomes a question of timing.",
            "concepts": [
                "A **sequential** circuit's output depends on the history of its inputs, not only their present values. The mechanism is always the same: a path from an output back round to an input.",
                "The **SR latch**, two cross-coupled NOR gates, is the smallest memory there is. S = 1 sets it, R = 1 resets it, both 0 holds whatever it had. Both 1 is forbidden: it drives both outputs to 0, so Q and Q' stop being opposites.",
                "A **transparent D latch** is an SR latch with an enable. While the enable is high the output follows the input; when it goes low the last value is trapped.",
                "An **edge-triggered D flip-flop** samples its input only at the instant the clock rises. Between edges the input can do whatever it likes. This is what makes a synchronous design analysable.",
                "**Setup time** is how long the data must already be stable before the clock edge; **hold time** is how long it must remain stable after it. Violate either and the flip-flop may store neither value.",
                "The clock period must exceed clock-to-output delay + longest combinational path + setup time. That inequality is the entire speed budget of a synchronous circuit.",
                "Signals take time because every wire and every gate input is a capacitance charged through a resistance. A logic level is not reached until the voltage crosses the receiving gate's threshold.",
            ],
            "sandbox": {
                "title": "What the flip-flops between stages are doing",
                "visualiser": "pipeline",
                "minutes": 8,
                "initial": {"dep": 3, "fwd": 0, "miss": 1},
                "brief": r'''
Nine instructions, drawn as nine rows, moving left to right through five stages:
fetch (`IF`), decode (`ID`), execute (`EX`), memory (`ME`) and write-back (`WB`),
which are the labels in the cells. Each cell is one clock cycle.

The reason a picture like this can be drawn at all is the flip-flop. Between every
pair of stages sits a bank of them, and on each clock edge every bank hands its
contents to the next stage at the same instant. Nothing drifts; everything moves
one column per cycle. That is the only claim from this module the picture rests on.

Three controls, each defined here so nothing has to be taken on trust:

* **dependent pairs** — how many instructions need a number the instruction above
  them has not finished computing. Such an instruction cannot start until that
  number exists, so its row is pushed to the right.
* **forwarding on** — whether a finished result is wired straight across from one
  execute stage to the next, rather than being written into the register file in
  `WB` and read back out of it in `ID` several cycles later.
* **branch mispredicts** — how many times the machine guesses wrong about which
  instruction comes next and has to discard the rows it began by mistake.

The readout underneath counts what each one costs, in cycles and in cycles per
instruction. Every cost is a whole number of cycles, and that is the flip-flop
again: data moves on clock edges or not at all.
''',
                "notice": [
                    "With `forwarding` at no, i1 and i2 each begin three cycles after the row above rather than one. Those two extra columns are the gap between a result being written back in `WB` and the next instruction reading it in `ID`. Row i3 is pushed five cycles rather than three, because it is both dependent and the first mispredicted branch.",
                    "Turn `forwarding` to yes. All three of those two-cycle gaps close, and the readout falls from 21 cycles to 15 — the result is handed straight from one execute stage to the next instead of going round through the register file. The branch penalty on i3 is untouched, because forwarding has nothing to say about a wrong guess.",
                    "Push `branch mispredicts` past 2 and nothing further changes. Only two of the nine instructions are treated as branches, so there is no third one left to mispredict.",
                ],
            },
            "quiz": {
                "title": "Memory, edges and the speed limit",
                "minutes": 9,
                "questions": [
                    {
                        "q": "What makes a circuit sequential rather than combinational?",
                        "opts": [
                            "It has more than one output",
                            "Its output depends on the history of its inputs, not only on their present values",
                            "It is built from NAND gates rather than AND and OR",
                            "It has a clock input",
                        ],
                        "a": 1,
                        "why": (
                            "Memory is the definition: the same inputs can give different outputs depending "
                            "on what happened before. A clock is the usual way to organise that, but it is "
                            "not what makes it so — a plain SR latch has no clock at all and is thoroughly "
                            "sequential. The gates used and the number of outputs have nothing to do with it."
                        ),
                    },
                    {
                        "q": "In an SR latch built from two cross-coupled NOR gates, what happens if S and R are both driven to 1?",
                        "opts": [
                            "It holds whatever it was storing",
                            "Both outputs go to 0, so Q and Q' are no longer opposites",
                            "It toggles to the other state",
                            "Nothing at all — the inputs are ignored",
                        ],
                        "a": 1,
                        "why": (
                            "A NOR gate with any input at 1 outputs 0, so both gates output 0 at once and "
                            "the two outputs stop being complements. Worse, when S and R return to 0 "
                            "together the latch settles into whichever state wins a race, so the stored "
                            "value is unpredictable. **Holding** is what S = R = 0 does; this combination "
                            "is simply not allowed to occur."
                        ),
                    },
                    {
                        "q": "How does a transparent D latch differ from an edge-triggered D flip-flop?",
                        "opts": [
                            "The latch has no clock input at all",
                            "While the clock is high the latch output follows its input, whereas the flip-flop samples only at the instant the clock rises",
                            "The flip-flop can store a 1 but not a 0",
                            "The latch is faster because it uses fewer gates",
                        ],
                        "a": 1,
                        "why": (
                            "That window is the entire difference, and it is why designs are built from "
                            "flip-flops. A latch left transparent lets a change race through it and reach "
                            "the next stage in the same clock phase; a flip-flop's output can change only "
                            "at edges, so the value a stage reads is definitely the one stored on the "
                            "previous edge. The latch does have a clock — it is just level-sensitive rather "
                            "than edge-sensitive."
                        ),
                    },
                    {
                        "q": "The setup time of a flip-flop is:",
                        "opts": [
                            "How long the data must already be stable before the clock edge",
                            "How long the data must stay stable after the clock edge",
                            "How long the output takes to change after the clock edge",
                            "The shortest clock period the flip-flop can be driven at",
                        ],
                        "a": 0,
                        "why": (
                            "Setup is before the edge. \"Stable *after* the edge\" is **hold** time, and "
                            "\"how long the output takes to change\" is the clock-to-output delay. All "
                            "three are separate numbers on a "
                            "datasheet and all three appear in the timing budget. Missing setup does not "
                            "give the old value or the new one — the flip-flop can hang between the two, "
                            "which is called metastability."
                        ),
                    },
                    {
                        "q": "Logic between two flip-flops has a longest path of 6 ns. The flip-flops take 2 ns from clock edge to output and need 1 ns of setup. What is the shortest clock period that works?",
                        "opts": ["6 ns", "7 ns", "8 ns", "9 ns"],
                        "a": 3,
                        "why": (
                            "Add the three in order round the loop: 2 ns to get the value out of the first "
                            "flip-flop, 6 ns through the logic, and 1 ns of stability before the next edge. "
                            "That is 9 ns, so the fastest clock is about 111 MHz. Quoting only the 6 ns "
                            "path is the usual mistake: it claims 167 MHz for a circuit that cannot be "
                            "clocked above 111 MHz. Notice that the "
                            "**longest** path sets the period: every other path simply finishes early and "
                            "waits."
                        ),
                    },
                ],
            },
            "build": {
                "title": "Where the propagation delay comes from",
                "minutes": 25,
                "brief": r'''
A gate output does not step. It charges the wire and the input capacitance of
whatever it drives, through its own output resistance, and the gate downstream does
not see a 1 until the voltage has climbed past its threshold. That climb is the
**propagation delay**, and it is why a clock has a maximum speed.

Nothing about capacitors has been assumed so far, so here is the whole of what this
module needs. A **capacitor** holds charge, and its voltage rises as charge arrives.
A resistor limits how fast charge can arrive. Put the two together and the pair has
a natural timescale — the product `RC`, in seconds — over which the voltage climbs
towards its final value.

Model it with the parts you have:

* the driving gate is a 5 V source that comes on at $t = 0$, behind a resistor `R`
* everything it drives is a capacitor `C` from that node to ground
* the probe is the input pin of the next gate

The node charges along $v(t) = 5\left(1 - e^{-t / RC}\right)$, and the receiving gate
calls it a 1 once it passes half the supply, 2.5 V. Setting $v = 2.5$ and solving:

$$t_{pd} = RC \ln 2 \approx 0.69 \, RC$$

Design for a delay **between 5 µs and 10 µs** — long enough to measure, short enough
to be worth building. Only the product `RC` matters, so there are many right answers.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [7, 3], "b": [9, 3]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3},
                        {"id": "p4", "kind": "C", "x": 9, "y": 5, "rot": 1, "value": 1e-9},
                        {"id": "p5", "kind": "GND", "x": 9, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [7, 3], "b": [9, 3]},
                        {"a": [9, 3], "b": [9, 4]},
                        {"a": [9, 6], "b": [9, 8]},
                    ],
                },
                "checks": [
                    {"name": "a 5 V driver, one resistance and one load capacitance", "code": r'''
c.assert(c.count('V') === 1, 'One voltage source: the driving gate, switching to 5 V at t = 0.');
c.close(c.values('V')[0], 5.0, 0.001, 'the supply voltage');
c.assert(c.count('C') >= 1,
  'There has to be a capacitance for the driver to charge — it stands for the input of the gate being driven.');
c.assert(c.count('R') >= 1, 'That capacitance has to charge through a resistance, or there is no delay to speak of.');
'''},
                    {"name": "the output really does settle at logic HIGH", "code": r'''
var r = c.step(2e-4);
c.close(r.v[r.v.length - 1], 5.0, 0.02,
  'the output level 200 µs after the driver switched. Short of 5 V means one of two things: ' +
  'a second resistor to ground is dividing it down, so the next gate would never see a 1, or ' +
  'RC is so large that 200 µs is not yet a long time');
'''},
                    {"name": "the threshold is crossed between 5 and 10 microseconds", "code": r'''
var r = c.step(4e-5);
var t = null;
for (var i = 0; i < r.t.length; i++) { if (r.v[i] >= 2.5) { t = r.t[i]; break; } }
c.assert(t !== null, 'The output never reaches the 2.5 V threshold at all within 40 µs — RC is far too large.');
c.assert(t >= 5e-6 && t <= 1e-5,
  'The threshold is crossed at ' + c.fmt(t, 's') + ', outside the 5-10 µs window. ' +
  'Remember t = 0.69 RC, so aim for an RC product between about 7 µs and 14 µs.');
'''},
                    {"name": "nothing is drawn once it has settled", "code": r'''
var cur = c.dc().currents;
var mags = Object.keys(cur).map(function (k) { return Math.abs(cur[k]); });
var worst = Math.max.apply(null, mags);
c.assert(worst < 1e-9,
  'Once settled the driver is delivering ' + c.fmt(worst, 'A') + '. A capacitor passes no steady current, ' +
  'so anything measurable here means a resistive path to ground that should not be there.');
'''},
                ],
                "hints": [
                    "The window 5-10 µs on the delay means an RC product between 7.2 µs and 14.4 µs. 10 kΩ with 1 nF gives 10 µs, and a delay of about 6.9 µs.",
                    "Values in the editor take engineering suffixes: `10k` for the resistor, `1n` for the capacitor.",
                    "The capacitor goes from the probed node **to ground**. It is the load, not something in the signal path.",
                    "Do not add a second resistor from the node to ground: the level would settle at a divided-down voltage and the last check would fail, because the next gate would never see a full 1.",
                ],
            },
            "lab": {
                "title": "A latch and a flip-flop, tick by tick",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Both devices store one bit. They differ only in **when** they look at their input,
and simulating them side by side is the quickest way to see how much that matters.

Both functions take two equal-length lists of 0s and 1s — the data and the clock,
sampled tick by tick — and an initial stored value `q0`. Both return the list of
stored values, one per tick, recorded **after** that tick has been processed.

**`d_latch(d_seq, clk_seq, q0=0)`** — transparent while the clock is high: on any
tick with `clk == 1` the stored value becomes `d`, otherwise it is left alone.

**`d_flip_flop(d_seq, clk_seq, q0=0)`** — edge-triggered: the stored value changes
only on a tick where the clock is 1 and was 0 on the previous tick. Take the clock
before the first tick to have been 0, so a run starting with `clk == 1` counts as
an edge.

Run `main.py` and compare the two output rows against the clock. Everywhere the
latch wobbles mid-pulse, the flip-flop sits still.
''',
                "files": [{"name": "main.py", "content": r'''
CLK = [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
D = [1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1]


def d_latch(d_seq, clk_seq, q0=0):
    """Transparent latch: while the clock is 1 the stored value follows d."""
    q = q0
    out = []
    # TODO: for each tick, update q when the clock is high, then record q.
    return out


def d_flip_flop(d_seq, clk_seq, q0=0):
    """Edge-triggered: the stored value changes only when the clock goes 0 -> 1."""
    q = q0
    prev_clk = 0
    out = []
    # TODO: detect the rising edge by comparing this tick's clock with the last one.
    return out


def row(name, seq):
    return name + " " + "".join(str(x) for x in seq)


if __name__ == "__main__":
    print(row("clk  ", CLK))
    print(row("d    ", D))
    print(row("latch", d_latch(D, CLK)))
    print(row("ff   ", d_flip_flop(D, CLK)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
CLK = [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
D = [1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1]


def d_latch(d_seq, clk_seq, q0=0):
    """Transparent latch: while the clock is 1 the stored value follows d."""
    q = q0
    out = []
    for d, clk in zip(d_seq, clk_seq):
        if clk:
            q = d
        out.append(q)
    return out


def d_flip_flop(d_seq, clk_seq, q0=0):
    """Edge-triggered: the stored value changes only when the clock goes 0 -> 1."""
    q = q0
    prev_clk = 0
    out = []
    for d, clk in zip(d_seq, clk_seq):
        if clk and not prev_clk:
            q = d
        prev_clk = clk
        out.append(q)
    return out


def row(name, seq):
    return name + " " + "".join(str(x) for x in seq)


if __name__ == "__main__":
    print(row("clk  ", CLK))
    print(row("d    ", D))
    print(row("latch", d_latch(D, CLK)))
    print(row("ff   ", d_flip_flop(D, CLK)))
'''}],
                "hints": [
                    "`zip(d_seq, clk_seq)` walks both lists together, one tick at a time.",
                    "In the latch, the only line inside the `if` is `q = d`. Recording `q` happens on every tick either way.",
                    "The flip-flop needs to remember the previous clock value. Update `prev_clk` at the end of each tick, after the edge test has used it.",
                    "With `prev_clk` starting at 0, a sequence that begins with the clock already high counts its first tick as an edge — which is what the brief asks for.",
                ],
                "tests": [
                    {"name": "both return one value per tick", "code": r'''
assert len(d_latch(D, CLK)) == len(CLK), "one recorded value per tick"
assert len(d_flip_flop(D, CLK)) == len(CLK), "one recorded value per tick"
'''},
                    {"name": "the latch is transparent while the clock is high", "code": r'''
_got = d_latch(D, CLK)
assert _got == [0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1], \
    f"expected [0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1], got {_got}"
'''},
                    {"name": "the flip-flop only moves on a rising edge", "code": r'''
_got = d_flip_flop(D, CLK)
assert _got == [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], \
    f"expected [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0], got {_got}"
'''},
                    {"name": "the difference is the mid-pulse change", "code": r'''
_l = d_latch(D, CLK)
_f = d_flip_flop(D, CLK)
assert _l[2] == 0 and _f[2] == 1, (
    "at tick 2 the data has already changed but the clock has not fallen: "
    f"the latch should follow it to 0 and the flip-flop should hold 1, got {_l[2]} and {_f[2]}")
assert _l[10] == 1 and _f[10] == 0, \
    f"the same thing again at tick 10, got {_l[10]} and {_f[10]}"
'''},
                    {"name": "the initial value is held until something changes it", "code": r'''
assert d_flip_flop([0, 0, 0, 0], [0, 0, 0, 0], 1) == [1, 1, 1, 1], \
    "with no rising edge the flip-flop must keep q0"
assert d_latch([0, 0, 0, 0], [0, 0, 0, 0], 1) == [1, 1, 1, 1], \
    "with the clock low throughout the latch must keep q0 too"
assert d_flip_flop([1, 1], [1, 1], 0) == [1, 1], \
    "the clock is taken to have been 0 before the first tick, so tick 0 is an edge"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A 4-bit counter and the display that reads it out",
        "runtime": "python",
        "minutes": 100,
        "brief": r'''
Everything in this course, assembled into one small machine: a 4-bit counter that
advances on every clock tick, and a combinational decoder that lights the right
segments of a seven-segment display for whatever the counter is holding.

The display is a figure of eight made from seven bars, named `a` at the top then
clockwise `b`, `c`, `d`, `e`, `f`, with `g` across the middle. Which bars are lit
for each of the sixteen values is fixed by the font in `display.py`, which you must
not edit — that file is the specification, and your job is to build logic that
reproduces it.

## What you are building

The counter is the **sequential** half: four flip-flops holding the count, with
combinational logic computing what the count should be after the next edge. That
logic is an adder — adding 1 — so the adder comes first.

The decoder is the **combinational** half. For each of the seven segments there is
a Boolean function of the four counter bits, and you will build all seven the same
way: read the column out of the font as a truth table, then turn that table into a
canonical sum-of-products.

## Suggested order

Work up from the adder: `full_adder`, then `add4`, then `count_next` and
`run_counter`. Then the algebra: `sop` and `sop_expression`. Then join the two with
`segment_rows`, `segment_functions` and `display_for`, and finish with `simulate`.
The checks are ordered the same way, so they light up as you go.

Bit order is fixed throughout: a 4-bit value is a list of four 0/1 values, **most
significant first**, so 13 is `[1, 1, 0, 1]`.
''',
        "deliverables": [
            "`full_adder(a, b, cin)` and `add4(a_bits, b_bits, cin=0)` — ripple-carry arithmetic, with `add4` built by calling `full_adder` once per bit rather than by converting to integers.",
            "`count_next(q)` and `run_counter(cycles, start=0)` — the counter's next-state logic expressed as 'add one with the adder', and a run of it over a number of clock ticks.",
            "`sop(rows)` and `sop_expression(rows, names)` — the canonical sum-of-products of any truth table, as a callable function and as a readable expression string.",
            "`segment_rows(seg)`, `segment_functions()` and `display_for(q)` — one Boolean function per segment, built from the font table, and the lit segments for a given 4-bit value.",
            "`simulate(cycles, start=0)` — the whole machine: the segment string the display shows on each of `cycles` successive clock ticks.",
            "A comment at the top of `main.py` stating the bit ordering you are using and naming which parts of the design are combinational and which are sequential.",
        ],
        "constraints": [
            "The standard library only — no NumPy needed here, and nothing else is available.",
            "`add4` must call `full_adder` four times. Converting the lists to Python integers, adding, and converting back is not building an adder.",
            "`count_next` must use `add4`; the counter's next state is its present state plus one, computed by the same hardware that does everything else.",
            "The decoder must be built from `display.py` at run time. Typing out the sixteen answers by hand defeats the exercise and the segment check will not tell you apart, but the rubric will.",
            "`sop` must produce the canonical form — one AND term per row where the output is 1, all ORed together — not a lookup table dressed up as a function.",
        ],
        "rubric": [
            {"criterion": "Arithmetic", "weight": 30,
             "evidence": "The full adder matches its truth table on all eight rows, and add4 gives the right sum and carry for all 256 pairs of 4-bit inputs, built by calling full_adder once per bit."},
            {"criterion": "Sequential logic", "weight": 25,
             "evidence": "count_next computes the next state through add4, and run_counter produces the right sequence including the wrap from 15 back to 0."},
            {"criterion": "Canonical forms", "weight": 25,
             "evidence": "sop reproduces an arbitrary truth table exactly, and sop_expression writes the matching expression with complements marked and terms in row order."},
            {"criterion": "The whole machine", "weight": 20,
             "evidence": "The seven segment functions, built from the font table rather than hard-coded, reproduce the display for all sixteen values, and simulate shows the right sequence of patterns over a wrap."},
        ],
        "hints": [
            "`add4` is the module 3 lab unchanged. Copy it in and move on.",
            "`count_next(q)` is one line: `add4(q, [0, 0, 0, 1])[0]` — the carry-out is what falls off the end when 15 wraps to 0, and the counter simply ignores it.",
            "In `sop`, collect the input tuples of the rows whose output is 1. The returned function checks its arguments against each of those tuples in turn: a term matches when every variable agrees with the literal, and the OR means any one match gives 1.",
            "`sop_expression` walks the same rows in order and builds one string per minterm: the variable's name if the bit is 1, the name followed by an apostrophe if it is 0. Join the terms with `\" + \"`, and return `\"0\"` when there are no terms at all.",
            "`segment_rows('a')` asks the font one question sixteen times: is `a` among the letters listed for this value? That yes/no column is a truth table of the four counter bits, and `sop` turns it into logic.",
        ],
        "files": [
            {"name": "display.py", "ro": True, "content": r'''
"""The seven-segment font. Do not edit — this file is the specification.

Segments are named a to g:

      aaaa
     f    b
     f    b
      gggg
     e    c
     e    c
      dddd

SEGMENTS[value] lists the segments that must be lit to show that value, using the
usual hexadecimal display font, in alphabetical order.
"""

SEGMENT_NAMES = "abcdefg"

SEGMENTS = {
    0: "abcdef",
    1: "bc",
    2: "abdeg",
    3: "abcdg",
    4: "bcfg",
    5: "acdfg",
    6: "acdefg",
    7: "abc",
    8: "abcdefg",
    9: "abcdfg",
    10: "abcefg",
    11: "cdefg",
    12: "adef",
    13: "bcdeg",
    14: "adefg",
    15: "aefg",
}
'''},
            {"name": "main.py", "content": r'''
"""A 4-bit counter and its seven-segment decoder.

Bit ordering: TODO — say which end of the list is the most significant bit.
Combinational parts: TODO.
Sequential parts: TODO.
"""

from display import SEGMENTS, SEGMENT_NAMES


def full_adder(a, b, cin):
    """Add three bits. Return (sum_bit, carry_out)."""
    # TODO
    return 0, 0


def add4(a_bits, b_bits, cin=0):
    """Add two 4-bit lists (most significant first). Return (bits, carry_out)."""
    # TODO: call full_adder once per bit, least significant first.
    return [0, 0, 0, 0], 0


def bits_of(n):
    """n as four bits, most significant first."""
    return [(n >> place) & 1 for place in (3, 2, 1, 0)]


def value_of(q):
    """The number a 4-bit list stands for."""
    return q[0] * 8 + q[1] * 4 + q[2] * 2 + q[3]


def count_next(q):
    """The next state of the counter: the present state plus one, via add4."""
    # TODO
    return [0, 0, 0, 0]


def run_counter(cycles, start=0):
    """The counter's value on each of `cycles` successive clock ticks."""
    # TODO: the first entry is `start` itself, before any edge.
    return []


def sop(rows):
    """Canonical sum-of-products of a truth table, as a callable function.

    `rows` is a list of (inputs_tuple, output) pairs. The returned function takes
    the same number of arguments and returns 0 or 1.
    """
    # TODO
    return lambda *args: 0


def sop_expression(rows, names):
    """The same canonical form written out, e.g. "A'B + AB". "0" when never 1."""
    # TODO
    return ""


def segment_rows(seg):
    """The truth table of one segment: 16 rows of (four bits, lit or not)."""
    # TODO: ask SEGMENTS whether `seg` is lit for each value 0..15.
    return []


def segment_functions():
    """A dict from segment name to the Boolean function that drives it."""
    # TODO
    return {}


def display_for(q):
    """The segments lit for a 4-bit value, in alphabetical order, as a string."""
    # TODO
    return ""


def simulate(cycles, start=0):
    """What the display shows on each of `cycles` successive clock ticks."""
    # TODO
    return []


if __name__ == "__main__":
    print("count :", run_counter(6, 13))
    print("shows :", simulate(6, 13))
    print("seg a :", sop_expression(segment_rows("a"), "QRST")[:60], "...")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""A 4-bit counter and its seven-segment decoder.

Bit ordering: a 4-bit value is a list of four 0/1 values, most significant first,
so index 0 is the eights place and index 3 is the ones place.

Combinational: full_adder, add4, count_next's arithmetic, and all seven segment
functions — their outputs depend only on the bits presented to them.

Sequential: run_counter and simulate, which hold a state between clock ticks. In
hardware that state lives in four edge-triggered flip-flops, and count_next is the
combinational cloud between their outputs and their inputs.
"""

from display import SEGMENTS, SEGMENT_NAMES


def full_adder(a, b, cin):
    """Add three bits. Return (sum_bit, carry_out)."""
    total = a + b + cin
    return total % 2, 1 if total >= 2 else 0


def add4(a_bits, b_bits, cin=0):
    """Add two 4-bit lists (most significant first). Return (bits, carry_out)."""
    out = [0, 0, 0, 0]
    carry = cin
    for i in range(3, -1, -1):
        out[i], carry = full_adder(a_bits[i], b_bits[i], carry)
    return out, carry


def bits_of(n):
    """n as four bits, most significant first."""
    return [(n >> place) & 1 for place in (3, 2, 1, 0)]


def value_of(q):
    """The number a 4-bit list stands for."""
    return q[0] * 8 + q[1] * 4 + q[2] * 2 + q[3]


def count_next(q):
    """The next state of the counter: the present state plus one, via add4."""
    nxt, _carry = add4(list(q), [0, 0, 0, 1])
    return nxt


def run_counter(cycles, start=0):
    """The counter's value on each of `cycles` successive clock ticks."""
    q = bits_of(start)
    out = []
    for _ in range(cycles):
        out.append(value_of(q))
        q = count_next(q)
    return out


def sop(rows):
    """Canonical sum-of-products of a truth table, as a callable function."""
    minterms = [inputs for inputs, out in rows if out]

    def f(*args):
        for term in minterms:
            hit = 1
            for arg, literal in zip(args, term):
                bit = 1 if arg else 0
                hit = hit and (bit if literal else 1 - bit)
            if hit:
                return 1
        return 0
    return f


def sop_expression(rows, names):
    """The same canonical form written out, e.g. "A'B + AB". "0" when never 1."""
    terms = []
    for inputs, out in rows:
        if not out:
            continue
        terms.append("".join(nm if bit else nm + "'"
                             for nm, bit in zip(names, inputs)))
    return " + ".join(terms) if terms else "0"


def segment_rows(seg):
    """The truth table of one segment: 16 rows of (four bits, lit or not)."""
    rows = []
    for value in range(16):
        rows.append((tuple(bits_of(value)), 1 if seg in SEGMENTS[value] else 0))
    return rows


def segment_functions():
    """A dict from segment name to the Boolean function that drives it."""
    return {seg: sop(segment_rows(seg)) for seg in SEGMENT_NAMES}


def display_for(q):
    """The segments lit for a 4-bit value, in alphabetical order, as a string."""
    fns = segment_functions()
    return "".join(seg for seg in SEGMENT_NAMES if fns[seg](*q))


def simulate(cycles, start=0):
    """What the display shows on each of `cycles` successive clock ticks."""
    return [display_for(bits_of(value)) for value in run_counter(cycles, start)]


if __name__ == "__main__":
    print("count :", run_counter(6, 13))
    print("shows :", simulate(6, 13))
    print("seg a :", sop_expression(segment_rows("a"), "QRST")[:60], "...")
'''},
        ],
        "tests": [
            {"name": "the full adder matches its truth table", "code": r'''
_want = {(0, 0, 0): (0, 0), (0, 0, 1): (1, 0), (0, 1, 0): (1, 0), (0, 1, 1): (0, 1),
         (1, 0, 0): (1, 0), (1, 0, 1): (0, 1), (1, 1, 0): (0, 1), (1, 1, 1): (1, 1)}
for _row, _exp in _want.items():
    _got = tuple(full_adder(*_row))
    assert _got == _exp, f"full_adder{_row} should be {_exp}, got {_got}"
'''},
            {"name": "add4 is right on all 256 pairs", "code": r'''
for _a in range(16):
    for _b in range(16):
        _bits, _c = add4(bits_of(_a), bits_of(_b))
        assert value_of(_bits) == (_a + _b) % 16, \
            f"{_a} + {_b} gave {value_of(_bits)}, expected {(_a + _b) % 16}"
        assert _c == (_a + _b) // 16, \
            f"{_a} + {_b} gave carry {_c}, expected {(_a + _b) // 16}"
'''},
            {"name": "add4 is built out of full adders", "code": r'''
_calls = []
_orig = full_adder


def _spy(a, b, cin):
    _calls.append((a, b, cin))
    return _orig(a, b, cin)


full_adder = _spy
try:
    _bits, _c = add4([0, 1, 0, 1], [0, 0, 1, 1])
finally:
    full_adder = _orig
assert len(_calls) == 4, (
    f"add4 called full_adder {len(_calls)} times; it should be exactly 4, "
    "one per bit — converting to integers and back is not an adder")
assert _bits == [1, 0, 0, 0], f"and it should still give 5 + 3 = 1000, got {_bits}"
'''},
            {"name": "the counter counts, and wraps", "code": r'''
assert count_next([0, 0, 0, 0]) == [0, 0, 0, 1], "0 + 1 = 1"
assert count_next([1, 1, 1, 1]) == [0, 0, 0, 0], "15 + 1 wraps to 0 in four bits"
_seq = run_counter(20, 13)
assert _seq == [13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0], \
    f"expected a wrapping count from 13, got {_seq}"
'''},
            {"name": "sop reproduces any truth table", "code": r'''
import random
random.seed(7)
_table = []
for _i in range(16):
    _inputs = tuple((_i >> (3 - _k)) & 1 for _k in range(4))
    _table.append((_inputs, random.randint(0, 1)))
_f = sop(_table)
for _inputs, _want in _table:
    assert _f(*_inputs) == _want, \
        f"sop function gave {_f(*_inputs)} on {_inputs}, table says {_want}"
_none = sop([((0,), 0), ((1,), 0)])
assert _none(0) == 0 and _none(1) == 0, "a table of all zeros is the constant 0"
'''},
            {"name": "sop_expression writes the canonical form", "code": r'''
_rows = [((0, 0), 0), ((0, 1), 1), ((1, 0), 0), ((1, 1), 1)]
assert sop_expression(_rows, "AB") == "A'B + AB", \
    f"expected \"A'B + AB\", got {sop_expression(_rows, 'AB')!r}"
assert sop_expression([((0,), 0), ((1,), 0)], "A") == "0", \
    "a function that is never 1 is written 0"
assert sop_expression([((0,), 1), ((1,), 1)], "A") == "A' + A", \
    "the canonical form does not simplify — that is what the K-map is for"
'''},
            {"name": "the decoder reproduces the font", "code": r'''
_fns = segment_functions()
assert set(_fns) == set(SEGMENT_NAMES), f"expected one function per segment, got {sorted(_fns)}"
for _value in range(16):
    _q = bits_of(_value)
    _lit = "".join(_s for _s in SEGMENT_NAMES if _fns[_s](*_q))
    assert _lit == SEGMENTS[_value], \
        f"value {_value} should light {SEGMENTS[_value]!r}, the functions light {_lit!r}"
    assert display_for(_q) == SEGMENTS[_value], \
        f"display_for({_q}) gave {display_for(_q)!r}, expected {SEGMENTS[_value]!r}"
'''},
            {"name": "the whole machine runs", "code": r'''
_shown = simulate(6, 13)
assert _shown == ['bcdeg', 'adefg', 'aefg', 'abcdef', 'bc', 'abdeg'], \
    f"expected d E F 0 1 2 across the wrap, got {_shown}"
assert len(simulate(16)) == 16 and len(set(simulate(16))) == 16, \
    "sixteen consecutive ticks should show sixteen different patterns"
'''},
        ],
    },
}
