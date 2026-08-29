"""CE101 — Digital Logic & Computer Systems. Author module."""

COURSE = {
    "id": "CE101",
    "title": "Digital Logic & Computer Systems",
    "year": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Verilog (reference)", "Python"],
    "credits": 10,
    "hours": 120,
    "icon": "⎓",
    "summary": (
        "Everything a processor does is built out of one switch that says 'not both'. "
        "This course climbs that ladder in software: Boolean algebra and canonical "
        "forms, gates assembled from NAND into adders, flip-flops that give a circuit "
        "memory, and finally an arithmetic-logic unit and a small datapath that fetches "
        "and executes instructions of your own encoding."
    ),
    "outcomes": [
        "Derive a truth table, minterm list and sum-of-products form for a Boolean function",
        "Reduce a function to its prime implicants and prove the reduction preserves behaviour",
        "Construct NOT, AND, OR and XOR from NAND alone, and adders from those gates",
        "Explain why edge-triggered storage makes a synchronous circuit predictable",
        "Design a Moore finite-state machine and simulate it over discrete clock ticks",
        "Compute two's-complement arithmetic and set the zero, negative, carry and overflow flags correctly",
        "Assemble a register file, ALU and control FSM into a datapath that runs a micro-program",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone datapath build (60%).",
    "reading": [
        "Harris & Harris, *Digital Design and Computer Architecture*, 2nd ed. — chapters 1-5",
        "Nisan & Schocken, *The Elements of Computing Systems*, 2nd ed. — chapters 1-3",
        "Patterson & Hennessy, *Computer Organization and Design*, 5th ed. — appendix 'The Basics of Logic Design'",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Boolean algebra and canonical forms",
            "summary": "From a truth table to a minimal expression, with equivalence as the referee.",
            "concepts": [
                "The Boolean algebra axioms: identity, complement, distributivity, De Morgan's laws",
                "A truth table is the complete specification of a combinational function",
                "Minterms: each row where the function is 1 names one AND term",
                "Canonical sum-of-products is unique; the minimal SOP normally is not",
                "The adjacency rule `XY + XY' = X` is the single move behind all reduction",
                "Prime implicants and the Quine-McCluskey merging procedure",
                "Two expressions are equal only if they agree on all 2^n rows — check, do not assume",
            ],
            "lab": {
                "title": "Truth tables, minterms and prime implicants",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
A Boolean function of `n` inputs is fully described by its `2**n` truth-table
rows. This lab turns that table into algebra and then shrinks the algebra.

Inputs are always listed **most significant first**, so for `n = 3` row 5 is
`(1, 0, 1)`.

**`truth_table(fn, n)`** — every row as an `(inputs, output)` pair, in binary
counting order. `inputs` is a tuple of 0/1 and `output` is `1` or `0` (never
`True`, never any other truthy value). Raise `ValueError` when `n < 1`.

```text
truth_table(lambda a, b: a and b, 2)
  -> [((0,0), 0), ((0,1), 0), ((1,0), 0), ((1,1), 1)]
```

**`minterms(fn, n)`** — the row numbers where the output is 1, ascending.

**`minterm_patterns(ms, n)`** — each minterm as an `n`-character bit string.
Raise `ValueError` if any minterm is negative or does not fit in `n` bits.

```text
minterm_patterns([3, 5], 3)  ->  ["011", "101"]
```

**`term_expression(pattern)`** — one *implicant* as a product term. A pattern
is a string of `"0"`, `"1"` and `"-"`, one character per variable, and the
variables are named `A`, `B`, `C`, ... A `"1"` contributes the plain letter, a
`"0"` the letter followed by `'`, and a `"-"` contributes nothing because that
variable has been eliminated. An all-`"-"` pattern is the constant `1`.

```text
term_expression("101")  ->  "AB'C"
term_expression("1-0")  ->  "AC'"
term_expression("--")   ->  "1"
```

**`sop_expression(patterns)`** — the terms joined with `" + "`, in the order
given. An empty list is the constant `"0"`.

**`prime_implicants(ms, n)`** — Quine-McCluskey. Start from the minterm
patterns. Repeatedly merge every pair that differs in exactly one position (and
only where neither has a `"-"` there) into one pattern with `"-"` at that
position. Any pattern that merged with nothing in a round is prime. Return the
primes sorted, with no duplicates.

```text
prime_implicants([3, 5, 6, 7], 3)  ->  ["-11", "1-1", "11-"]   (majority: BC + AC + AB)
prime_implicants([1, 2, 4, 7], 3)  ->  ["001", "010", "100", "111"]   (parity will not shrink)
prime_implicants([], 2)            ->  []
```

**`from_patterns(patterns)`** — a *function* that evaluates the OR of those
implicants: it returns 1 when the argument bits match at least one pattern,
ignoring `"-"` positions.

**`equivalent(f, g, n)`** — `True` when the two functions agree on every one of
the `2**n` rows. Compare truth values, not identities: `1` and `True` agree.

Together these let you reduce a function and then *prove* the reduction:
`equivalent(f, from_patterns(prime_implicants(minterms(f, n), n)), n)`.
''',
                "files": [{"name": "main.py", "content": r'''
NAMES = "ABCDEFGH"


def truth_table(fn, n):
    """Every (inputs, output) row for fn, MSB first. ValueError when n < 1."""
    # your code here


def minterms(fn, n):
    """Ascending row numbers where fn is 1."""
    # your code here


def minterm_patterns(ms, n):
    """Each minterm as an n-character bit string. ValueError if one will not fit."""
    # your code here


def term_expression(pattern):
    """One implicant pattern as a product term; all dashes means the constant 1."""
    # your code here


def sop_expression(patterns):
    """Product terms joined with ' + '; no patterns means the constant 0."""
    # your code here


def prime_implicants(ms, n):
    """Quine-McCluskey prime implicants of the minterm list, sorted."""
    # your code here


def from_patterns(patterns):
    """A function evaluating the OR of these implicants."""
    # your code here


def equivalent(f, g, n):
    """True when f and g agree on all 2**n rows."""
    # your code here


def majority(a, b, c):
    return 1 if a + b + c >= 2 else 0


ms = minterms(majority, 3)
print(sop_expression(minterm_patterns(ms, 3)))
print(sop_expression(prime_implicants(ms, 3)))
print(equivalent(majority, from_patterns(prime_implicants(ms, 3)), 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
NAMES = "ABCDEFGH"


def truth_table(fn, n):
    """Every (inputs, output) row for fn, MSB first. ValueError when n < 1."""
    if n < 1:
        raise ValueError("a function needs at least one input")
    rows = []
    for index in range(1 << n):
        bits = tuple((index >> (n - 1 - k)) & 1 for k in range(n))
        rows.append((bits, 1 if fn(*bits) else 0))
    return rows


def minterms(fn, n):
    """Ascending row numbers where fn is 1."""
    return [index for index, (_, out) in enumerate(truth_table(fn, n)) if out]


def minterm_patterns(ms, n):
    """Each minterm as an n-character bit string. ValueError if one will not fit."""
    if n < 1:
        raise ValueError("a function needs at least one input")
    patterns = []
    for m in ms:
        if m < 0 or m >= (1 << n):
            raise ValueError(f"minterm {m} does not fit in {n} bits")
        patterns.append(format(m, "0" + str(n) + "b"))
    return patterns


def term_expression(pattern):
    """One implicant pattern as a product term; all dashes means the constant 1."""
    literals = []
    for position, char in enumerate(pattern):
        if char == "1":
            literals.append(NAMES[position])
        elif char == "0":
            literals.append(NAMES[position] + "'")
    if not literals:
        return "1"
    return "".join(literals)


def sop_expression(patterns):
    """Product terms joined with ' + '; no patterns means the constant 0."""
    if not patterns:
        return "0"
    return " + ".join(term_expression(p) for p in patterns)


def merge(left, right):
    """The merged pattern when the two differ in exactly one fixed bit, else None."""
    position = -1
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            if position != -1 or a == "-" or b == "-":
                return None
            position = index
    if position == -1:
        return None
    return left[:position] + "-" + left[position + 1:]


def prime_implicants(ms, n):
    """Quine-McCluskey prime implicants of the minterm list, sorted."""
    current = sorted(set(minterm_patterns(ms, n)))
    primes = set()
    while current:
        used = set()
        nxt = set()
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                merged = merge(current[i], current[j])
                if merged is not None:
                    used.add(current[i])
                    used.add(current[j])
                    nxt.add(merged)
        for pattern in current:
            if pattern not in used:
                primes.add(pattern)
        current = sorted(nxt)
    return sorted(primes)


def from_patterns(patterns):
    """A function evaluating the OR of these implicants."""
    def fn(*bits):
        for pattern in patterns:
            if all(int(char) == bit for char, bit in zip(pattern, bits) if char != "-"):
                return 1
        return 0
    return fn


def equivalent(f, g, n):
    """True when f and g agree on all 2**n rows."""
    for bits, out in truth_table(f, n):
        if out != (1 if g(*bits) else 0):
            return False
    return True


def majority(a, b, c):
    return 1 if a + b + c >= 2 else 0


ms = minterms(majority, 3)
print(sop_expression(minterm_patterns(ms, 3)))
print(sop_expression(prime_implicants(ms, 3)))
print(equivalent(majority, from_patterns(prime_implicants(ms, 3)), 3))
'''}],
                "hints": [
                    "Row `index` has bit `k` equal to `(index >> (n - 1 - k)) & 1` when the first variable is the most significant.",
                    "`format(m, \"0\" + str(n) + \"b\")` pads a minterm to exactly n binary digits.",
                    "Two patterns merge only when they differ in one position *and* neither holds a dash there — check both conditions before returning the merged pattern.",
                    "Quine-McCluskey is a loop over rounds: collect every merge of the current list, mark the patterns that merged, promote the unmarked ones to primes, and repeat on the merged list until it is empty.",
                ],
                "tests": [
                    {"name": "truth_table shape, order and 0/1 outputs", "code": r'''
_got = truth_table(lambda a, b: a and b, 2)
_want = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
assert _got == _want, f"truth_table(AND, 2) gave {_got!r}, expected {_want}"
assert all(_o in (0, 1) and type(_o) is int for _, _o in _got), "outputs must be the ints 0 and 1"
_t3 = truth_table(lambda a, b, c: c, 3)
assert len(_t3) == 8, f"a 3-input table has 8 rows, got {len(_t3)}"
assert _t3[5][0] == (1, 0, 1), f"row 5 should be (1, 0, 1), got {_t3[5][0]!r}"
try:
    truth_table(lambda a: a, 0)
    assert False, "truth_table(fn, 0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "minterms lists the rows that are 1", "code": r'''
assert minterms(lambda a, b: a or b, 2) == [1, 2, 3], f"OR gave {minterms(lambda a, b: a or b, 2)!r}"
assert minterms(lambda a, b, c: a ^ b ^ c, 3) == [1, 2, 4, 7], "odd parity is minterms 1, 2, 4, 7"
assert minterms(lambda a, b: 0, 2) == [], "a constant-0 function has no minterms"
assert minterms(lambda a, b: 1, 2) == [0, 1, 2, 3], "a constant-1 function has every minterm"
'''},
                    {"name": "minterm_patterns pads and validates", "code": r'''
assert minterm_patterns([3, 5], 3) == ["011", "101"], f"Got {minterm_patterns([3, 5], 3)!r}"
assert minterm_patterns([], 4) == [], "no minterms, no patterns"
for _bad in ([8], [-1]):
    try:
        minterm_patterns(_bad, 3)
        assert False, f"minterm_patterns({_bad!r}, 3) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "term_expression and sop_expression", "code": r'''
assert term_expression("101") == "AB'C", f'Got {term_expression("101")!r}'
assert term_expression("1-0") == "AC'", f'Got {term_expression("1-0")!r}'
assert term_expression("--") == "1", "an implicant with no literals is the constant 1"
assert sop_expression(["-11", "1-1", "11-"]) == "BC + AC + AB", \
    f'Got {sop_expression(["-11", "1-1", "11-"])!r}'
assert sop_expression([]) == "0", "no implicants means the constant 0"
assert sop_expression(["011"]) == "A'BC", f'Got {sop_expression(["011"])!r}'
'''},
                    {"name": "prime_implicants merges adjacent minterms", "code": r'''
assert prime_implicants([3, 5, 6, 7], 3) == ["-11", "1-1", "11-"], \
    f"majority gave {prime_implicants([3, 5, 6, 7], 3)!r}, expected ['-11', '1-1', '11-']"
assert prime_implicants([1, 2, 3], 2) == ["-1", "1-"], \
    f"OR gave {prime_implicants([1, 2, 3], 2)!r}, expected ['-1', '1-']"
assert prime_implicants([0, 1, 2, 3], 2) == ["--"], "a tautology reduces to the constant 1"
assert prime_implicants([], 2) == [], "nothing to imply"
assert prime_implicants([1, 2, 4, 7], 3) == ["001", "010", "100", "111"], \
    "three-input parity has no adjacent minterms, so every minterm is prime"
'''},
                    {"name": "from_patterns rebuilds a working function", "code": r'''
_f = from_patterns(["-11", "1-1", "11-"])
for _bits, _want in [((0, 0, 0), 0), ((0, 1, 1), 1), ((1, 0, 1), 1),
                     ((1, 1, 0), 1), ((1, 1, 1), 1), ((1, 0, 0), 0)]:
    _got = _f(*_bits)
    assert _got == _want, f"rebuilt majority{_bits} gave {_got!r}, expected {_want}"
assert from_patterns([])(0, 1) == 0, "no implicants is the constant 0"
assert from_patterns(["--"])(0, 1) == 1, "an all-dash implicant is the constant 1"
'''},
                    {"name": "equivalence proves the reduction", "code": r'''
def _maj(a, b, c):
    return 1 if a + b + c >= 2 else 0
_primes = prime_implicants(minterms(_maj, 3), 3)
assert equivalent(_maj, from_patterns(_primes), 3), "the reduced form must match the original"
assert equivalent(_maj, from_patterns(minterm_patterns(minterms(_maj, 3), 3)), 3), \
    "the canonical form must match the original too"
assert equivalent(lambda a, b: a and b, lambda a, b: not (not a or not b), 2), \
    "De Morgan: AB and (A'+B')' are the same function"
assert not equivalent(lambda a, b: a and b, lambda a, b: a or b, 2), \
    "AND and OR differ on (0, 1), so equivalent() must be False"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Gates, universality and adders",
            "summary": "NAND is enough for everything; build up to a ripple-carry adder.",
            "concepts": [
                "NAND (and NOR) are functionally complete — every gate reduces to them",
                "NOT from a NAND with both inputs tied together; AND from NAND then NOT",
                "OR from NAND by De Morgan: `A + B = (A'B')'`",
                "XOR as a four-NAND network, and why it costs more than AND",
                "The half adder: sum is XOR, carry is AND",
                "The full adder chains two half adders and ORs the carries",
                "Ripple-carry delay grows linearly with word width — the motivation for carry-lookahead",
            ],
            "lab": {
                "title": "From one NAND to a 4-bit adder",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
`nand(a, b)` is already written for you. It is the **only** primitive you may
compute with: everything else in this file must be built from it, directly or
indirectly. No `and`, `or`, `not`, `^`, `+` or `if` on the signal values
themselves — the checks watch how often `nand` is called.

**`not_gate(a)`, `and_gate(a, b)`, `or_gate(a, b)`, `xor_gate(a, b)`** —
the four familiar gates, each returning 0 or 1.

**`half_adder(a, b)`** — returns `(sum, carry)`.

```text
half_adder(1, 1)  ->  (0, 1)
half_adder(1, 0)  ->  (1, 0)
```

**`full_adder(a, b, cin)`** — returns `(sum, cout)`. Build it from two half
adders and one OR; do not write out a fresh truth table.

**`to_bits(value, width)`** — the unsigned value as a list of 0/1,
**most significant bit first**. Raise `ValueError` when the value is negative or
will not fit.

**`from_bits(bits)`** — the reverse.

```text
to_bits(10, 4)          ->  [1, 0, 1, 0]
from_bits([1, 0, 1, 0]) ->  10
```

**`ripple_add(a_bits, b_bits, cin=0)`** — returns `(sum_bits, cout)`. Chain one
full adder per bit position, starting at the least significant end and passing
each carry along. Raise `ValueError` when the two operands have different
widths, or when they are empty.

```text
ripple_add([0, 1, 1, 1], [0, 0, 0, 1])  ->  ([1, 0, 0, 0], 0)     7 + 1 = 8
ripple_add([1, 1, 1, 1], [0, 0, 0, 1])  ->  ([0, 0, 0, 0], 1)    15 + 1 = 16
```

The width is whatever you pass, so the same function is a 4-bit adder and a
16-bit adder.
''',
                "files": [{"name": "main.py", "content": r'''
def nand(a, b):
    """The one primitive you are given: 0 only when both inputs are 1."""
    return 0 if (a and b) else 1


def not_gate(a):
    """NOT from a single NAND."""
    # your code here


def and_gate(a, b):
    """AND from NANDs."""
    # your code here


def or_gate(a, b):
    """OR from NANDs."""
    # your code here


def xor_gate(a, b):
    """XOR from NANDs."""
    # your code here


def half_adder(a, b):
    """(sum, carry) for two bits."""
    # your code here


def full_adder(a, b, cin):
    """(sum, cout) for two bits and a carry in."""
    # your code here


def to_bits(value, width):
    """Unsigned value as a width-long list of bits, MSB first."""
    # your code here


def from_bits(bits):
    """Bits, MSB first, back to an unsigned integer."""
    # your code here


def ripple_add(a_bits, b_bits, cin=0):
    """(sum_bits, cout) from a chain of full adders."""
    # your code here


print(half_adder(1, 1))
print(full_adder(1, 1, 1))
print(ripple_add(to_bits(7, 4), to_bits(9, 4)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def nand(a, b):
    """The one primitive you are given: 0 only when both inputs are 1."""
    return 0 if (a and b) else 1


def not_gate(a):
    """NOT from a single NAND."""
    return nand(a, a)


def and_gate(a, b):
    """AND from NANDs."""
    return not_gate(nand(a, b))


def or_gate(a, b):
    """OR from NANDs: De Morgan turns A + B into (A'B')'."""
    return nand(not_gate(a), not_gate(b))


def xor_gate(a, b):
    """XOR from NANDs: the classic four-gate network."""
    shared = nand(a, b)
    return nand(nand(a, shared), nand(b, shared))


def half_adder(a, b):
    """(sum, carry) for two bits."""
    return xor_gate(a, b), and_gate(a, b)


def full_adder(a, b, cin):
    """(sum, cout) for two bits and a carry in."""
    sum1, carry1 = half_adder(a, b)
    sum2, carry2 = half_adder(sum1, cin)
    return sum2, or_gate(carry1, carry2)


def to_bits(value, width):
    """Unsigned value as a width-long list of bits, MSB first."""
    if width < 1:
        raise ValueError("width must be at least 1")
    if value < 0 or value >= (1 << width):
        raise ValueError(f"{value} does not fit in {width} unsigned bits")
    return [(value >> (width - 1 - k)) & 1 for k in range(width)]


def from_bits(bits):
    """Bits, MSB first, back to an unsigned integer."""
    value = 0
    for bit in bits:
        value = value * 2 + bit
    return value


def ripple_add(a_bits, b_bits, cin=0):
    """(sum_bits, cout) from a chain of full adders."""
    if len(a_bits) != len(b_bits):
        raise ValueError("operands must be the same width")
    if not a_bits:
        raise ValueError("width must be at least 1")
    carry = cin
    out = []
    for a, b in zip(reversed(a_bits), reversed(b_bits)):
        bit, carry = full_adder(a, b, carry)
        out.append(bit)
    out.reverse()
    return out, carry


print(half_adder(1, 1))
print(full_adder(1, 1, 1))
print(ripple_add(to_bits(7, 4), to_bits(9, 4)))
'''}],
                "hints": [
                    "`not_gate(a)` is `nand(a, a)`: tying both inputs together leaves NAND with nothing to do but invert.",
                    "AND is a NAND followed by an inverter; OR is an inverter on each input followed by a NAND.",
                    "XOR needs four NANDs. Compute `shared = nand(a, b)` once, then `nand(nand(a, shared), nand(b, shared))`.",
                    "`ripple_add` walks the operands with `zip(reversed(a_bits), reversed(b_bits))`, keeps the carry in a variable between iterations, and reverses the collected sum bits at the end.",
                ],
                "tests": [
                    {"name": "NOT, AND and OR", "code": r'''
assert (not_gate(0), not_gate(1)) == (1, 0), f"not_gate gave {(not_gate(0), not_gate(1))!r}"
for _a, _b, _want in [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)]:
    _got = and_gate(_a, _b)
    assert _got == _want, f"and_gate({_a}, {_b}) gave {_got!r}, expected {_want}"
for _a, _b, _want in [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)]:
    _got = or_gate(_a, _b)
    assert _got == _want, f"or_gate({_a}, {_b}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "XOR", "code": r'''
for _a, _b, _want in [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]:
    _got = xor_gate(_a, _b)
    assert _got == _want, f"xor_gate({_a}, {_b}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "Every gate is built from nand", "code": r'''
_calls = []
_real_nand = nand
def _spy(a, b):
    _calls.append((a, b))
    return _real_nand(a, b)
nand = _spy
for _name, _fn, _args in [("not_gate", not_gate, (1,)), ("and_gate", and_gate, (1, 0)),
                          ("or_gate", or_gate, (1, 0)), ("xor_gate", xor_gate, (1, 0))]:
    _before = len(_calls)
    _fn(*_args)
    assert len(_calls) > _before, f"{_name} must be built from nand(), not from Python operators"
nand = _real_nand
'''},
                    {"name": "half_adder", "code": r'''
for _a, _b, _want in [(0, 0, (0, 0)), (0, 1, (1, 0)), (1, 0, (1, 0)), (1, 1, (0, 1))]:
    _got = tuple(half_adder(_a, _b))
    assert _got == _want, f"half_adder({_a}, {_b}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "full_adder, all eight rows", "code": r'''
for _a in (0, 1):
    for _b in (0, 1):
        for _c in (0, 1):
            _s, _co = full_adder(_a, _b, _c)
            _total = _a + _b + _c
            assert (_s, _co) == (_total % 2, _total // 2), \
                f"full_adder({_a}, {_b}, {_c}) gave {(_s, _co)!r}, expected {(_total % 2, _total // 2)}"
'''},
                    {"name": "to_bits / from_bits round-trip and limits", "code": r'''
assert to_bits(10, 4) == [1, 0, 1, 0], f"to_bits(10, 4) gave {to_bits(10, 4)!r}"
assert to_bits(0, 1) == [0], f"to_bits(0, 1) gave {to_bits(0, 1)!r}"
assert from_bits([1, 0, 1, 0]) == 10, f"from_bits([1,0,1,0]) gave {from_bits([1, 0, 1, 0])!r}"
assert from_bits([0]) == 0, "a single zero bit is 0"
for _v in range(64):
    assert from_bits(to_bits(_v, 6)) == _v, f"round-trip failed for {_v}"
for _bad in [(16, 4), (-1, 4), (2, 1)]:
    try:
        to_bits(*_bad)
        assert False, f"to_bits{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "ripple_add matches arithmetic on every 4-bit pair", "code": r'''
for _a in range(16):
    for _b in range(16):
        _bits, _cout = ripple_add(to_bits(_a, 4), to_bits(_b, 4))
        _total = _a + _b
        assert from_bits(_bits) == _total & 15, \
            f"{_a} + {_b} gave sum bits {_bits!r} ({from_bits(_bits)}), expected {_total & 15}"
        assert _cout == (_total >> 4) & 1, \
            f"{_a} + {_b} gave carry {_cout!r}, expected {(_total >> 4) & 1}"
_bits, _cout = ripple_add(to_bits(7, 4), to_bits(8, 4), 1)
assert (from_bits(_bits), _cout) == (0, 1), \
    f"7 + 8 + carry-in gave {(from_bits(_bits), _cout)!r}, expected (0, 1)"
'''},
                    {"name": "ripple_add rejects bad operands", "code": r'''
for _a, _b in [([1, 0], [1]), ([], [])]:
    try:
        ripple_add(_a, _b)
        assert False, f"ripple_add({_a!r}, {_b!r}) should raise ValueError"
    except ValueError:
        pass
_bits, _cout = ripple_add([1] * 16, [0] * 15 + [1])
assert (from_bits(_bits), _cout) == (0, 1), \
    f"the same function should add 16-bit words, got {(from_bits(_bits), _cout)!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Sequential logic and state machines",
            "summary": "Storage, the clock edge, and a Moore machine that watches a bit stream.",
            "concepts": [
                "Combinational output depends on inputs alone; sequential output depends on history",
                "A D flip-flop copies D to Q on the clock edge and holds it in between",
                "Sampling then updating is what makes shift registers work — every flop reads the old values",
                "A register is n flip-flops on a shared clock, usually with a load enable",
                "Setup and hold times, and why glitches between edges do not matter",
                "Moore machines output from the state; Mealy machines output from state and input",
                "Overlapping pattern detection: the next state is the longest suffix that is still a prefix",
            ],
            "lab": {
                "title": "Flip-flops, registers and a 1011 detector",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Nothing here happens because you assigned a value. Things happen on a **clock
edge**, and only then.

## `DFlipFlop`

- `DFlipFlop(q=0)` — starts holding `q`, with the D input equal to it. Raise
  `ValueError` if `q` is not 0 or 1.
- `set_d(value)` — drive the D input. `ValueError` for anything but 0 or 1.
  **`q` must not change.**
- `tick()` — the rising edge: copy D into `q` and return the new `q`.

That split is the whole point. Two flops wired in a chain both sample *before*
either updates, so a value moves exactly one stage per tick rather than racing
all the way down.

## `Register`

- `Register(width, value=0)` — `width` flip-flops, LSB at index 0. `ValueError`
  for a width below 1 or a value that will not fit.
- `read()` — the stored word as an unsigned integer.
- `set_input(value, enable=1)` — with `enable` truthy, drive the D inputs from
  `value` (`ValueError` if it does not fit in `width` bits). With `enable`
  falsy, drive each flop's D from its own `q`, so the next tick keeps the word.
- `tick()` — clock every flop and return the new `read()`.

## `SequenceDetector`

A Moore machine that raises its output for one cycle whenever the last four
bits it has seen are `1, 0, 1, 1`. Occurrences may overlap.

States: `"S0"`, `"S1"`, `"S10"`, `"S101"`, `"S1011"` — each named for the part
of the pattern matched so far.

- `SequenceDetector(state="S0")` — `ValueError` for a state not in `STATES`.
- `next_state(state, bit)` — the transition table, as a pure function.
- `output()` — 1 exactly in `"S1011"`, otherwise 0. It depends on the state
  alone: that is what makes the machine Moore rather than Mealy.
- `step(bit)` — advance one clock and return the new output. `ValueError` for a
  bit that is not 0 or 1.
- `run(bits)` — the output after each bit, as a list.

The transitions you need to get right are the ones that fail a partial match.
From `"S101"` a `0` does not go back to `"S0"`: the stream now ends `1010`, and
`10` is still a live prefix, so the machine lands in `"S10"`. From `"S1011"` a
`1` leaves the stream ending `10111`, whose longest useful suffix is `1`.

```text
run([1, 1, 0, 1, 0, 1, 1, 0, 1, 1])
  -> [0, 0, 0, 0, 0, 0, 1, 0, 0, 1]
```
''',
                "files": [{"name": "main.py", "content": r'''
class DFlipFlop:
    """One bit of edge-triggered storage."""

    def __init__(self, q=0):
        # your code here
        pass

    def set_d(self, value):
        """Drive the D input. Q does not move until the next tick."""
        # your code here

    def tick(self):
        """Rising clock edge: Q takes the value of D."""
        # your code here


class Register:
    """width flip-flops sharing one clock, with a load enable."""

    def __init__(self, width, value=0):
        # your code here
        pass

    def read(self):
        """The stored word as an unsigned integer."""
        # your code here

    def set_input(self, value, enable=1):
        """Drive the D inputs, or hold the current word when enable is falsy."""
        # your code here

    def tick(self):
        """Clock every flip-flop, then return the new word."""
        # your code here


class SequenceDetector:
    """Moore machine: output 1 for one cycle on each (overlapping) 1011."""

    STATES = ("S0", "S1", "S10", "S101", "S1011")

    def __init__(self, state="S0"):
        # your code here
        pass

    def next_state(self, state, bit):
        """The transition table."""
        # your code here

    def output(self):
        """A function of the state only."""
        # your code here

    def step(self, bit):
        """One clock: move state, return the new output."""
        # your code here

    def run(self, bits):
        """The output after each bit."""
        # your code here


reg = Register(4)
reg.set_input(10)
print(reg.tick())
print(SequenceDetector().run([1, 1, 0, 1, 0, 1, 1, 0, 1, 1]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class DFlipFlop:
    """One bit of edge-triggered storage."""

    def __init__(self, q=0):
        if q not in (0, 1):
            raise ValueError("a flip-flop holds 0 or 1")
        self.q = q
        self.d = q

    def set_d(self, value):
        """Drive the D input. Q does not move until the next tick."""
        if value not in (0, 1):
            raise ValueError("D must be 0 or 1")
        self.d = value

    def tick(self):
        """Rising clock edge: Q takes the value of D."""
        self.q = self.d
        return self.q


class Register:
    """width flip-flops sharing one clock, with a load enable."""

    def __init__(self, width, value=0):
        if width < 1:
            raise ValueError("a register needs at least one bit")
        if value < 0 or value >= (1 << width):
            raise ValueError(f"{value} does not fit in {width} bits")
        self.width = width
        self.flops = [DFlipFlop((value >> i) & 1) for i in range(width)]

    def read(self):
        """The stored word as an unsigned integer."""
        word = 0
        for i, flop in enumerate(self.flops):
            word |= flop.q << i
        return word

    def set_input(self, value, enable=1):
        """Drive the D inputs, or hold the current word when enable is falsy."""
        if not enable:
            for flop in self.flops:
                flop.set_d(flop.q)
            return
        if value < 0 or value >= (1 << self.width):
            raise ValueError(f"{value} does not fit in {self.width} bits")
        for i, flop in enumerate(self.flops):
            flop.set_d((value >> i) & 1)

    def tick(self):
        """Clock every flip-flop, then return the new word."""
        for flop in self.flops:
            flop.tick()
        return self.read()


class SequenceDetector:
    """Moore machine: output 1 for one cycle on each (overlapping) 1011."""

    STATES = ("S0", "S1", "S10", "S101", "S1011")

    TABLE = {
        ("S0", 0): "S0",
        ("S0", 1): "S1",
        ("S1", 0): "S10",
        ("S1", 1): "S1",
        ("S10", 0): "S0",
        ("S10", 1): "S101",
        ("S101", 0): "S10",
        ("S101", 1): "S1011",
        ("S1011", 0): "S10",
        ("S1011", 1): "S1",
    }

    def __init__(self, state="S0"):
        if state not in self.STATES:
            raise ValueError(f"unknown state {state!r}")
        self.state = state

    def next_state(self, state, bit):
        """The transition table."""
        if state not in self.STATES:
            raise ValueError(f"unknown state {state!r}")
        if bit not in (0, 1):
            raise ValueError("the input bit must be 0 or 1")
        return self.TABLE[(state, bit)]

    def output(self):
        """A function of the state only."""
        return 1 if self.state == "S1011" else 0

    def step(self, bit):
        """One clock: move state, return the new output."""
        self.state = self.next_state(self.state, bit)
        return self.output()

    def run(self, bits):
        """The output after each bit."""
        return [self.step(bit) for bit in bits]


reg = Register(4)
reg.set_input(10)
print(reg.tick())
print(SequenceDetector().run([1, 1, 0, 1, 0, 1, 1, 0, 1, 1]))
'''}],
                "hints": [
                    "Keep `self.d` and `self.q` as separate attributes — `set_d` touches only the first, `tick` copies the first into the second.",
                    "Store the register's flops LSB first, so bit `i` of the word is `(value >> i) & 1` and reading back is `flop.q << i`.",
                    "Write the ten transitions out as a dict keyed by `(state, bit)`; it is easier to check against the pattern than a chain of ifs.",
                    "For a failed match, ask which suffix of the stream is still a prefix of 1011: after `S101` and a 0 the stream ends `...1010`, so the answer is `10`, not the start state.",
                ],
                "tests": [
                    {"name": "A flip-flop is not transparent", "code": r'''
_ff = DFlipFlop()
assert _ff.q == 0, f"a fresh flip-flop starts at 0, got {_ff.q!r}"
_ff.set_d(1)
assert _ff.q == 0, "set_d must not move Q — storage changes only on the clock edge"
assert _ff.tick() == 1, "tick() should copy D into Q and return it"
assert _ff.q == 1, f"after the edge Q is 1, got {_ff.q!r}"
_ff.tick()
assert _ff.q == 1, "with D unchanged, a second edge holds the same value"
'''},
                    {"name": "A flip-flop rejects non-binary values", "code": r'''
try:
    DFlipFlop(2)
    assert False, "DFlipFlop(2) should raise ValueError"
except ValueError:
    pass
try:
    DFlipFlop().set_d(7)
    assert False, "set_d(7) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Two flops in a chain update together", "code": r'''
_a = DFlipFlop(1)
_b = DFlipFlop(0)
_a.set_d(0)
_b.set_d(_a.q)
_a.tick()
_b.tick()
assert (_a.q, _b.q) == (0, 1), \
    f"after one edge the chain should read (0, 1), got {(_a.q, _b.q)!r} — sample before you update"
'''},
                    {"name": "Register loads, reads and holds", "code": r'''
_r = Register(4)
assert _r.read() == 0, f"a fresh register reads 0, got {_r.read()!r}"
_r.set_input(10)
assert _r.read() == 0, "set_input must not change the stored word"
assert _r.tick() == 10, f"tick() should return the newly loaded word, got {_r.tick()!r}"
_r.set_input(5, enable=0)
_r.tick()
assert _r.read() == 10, f"with enable 0 the register holds; got {_r.read()!r}, expected 10"
_r.set_input(5, enable=1)
_r.tick()
assert _r.read() == 5, f"with enable 1 the register loads; got {_r.read()!r}"
assert Register(8, 200).read() == 200, "a register may start with a value"
'''},
                    {"name": "Register widths and ranges are checked", "code": r'''
for _args in [(0,), (4, 16), (4, -1), (-3,)]:
    try:
        Register(*_args)
        assert False, f"Register{_args!r} should raise ValueError"
    except ValueError:
        pass
try:
    Register(4).set_input(16)
    assert False, "set_input(16) on a 4-bit register should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The transition table handles failed matches", "code": r'''
_m = SequenceDetector()
for _state, _bit, _want in [("S0", 0, "S0"), ("S0", 1, "S1"), ("S1", 1, "S1"),
                            ("S1", 0, "S10"), ("S10", 0, "S0"), ("S10", 1, "S101"),
                            ("S101", 0, "S10"), ("S101", 1, "S1011"),
                            ("S1011", 0, "S10"), ("S1011", 1, "S1")]:
    _got = _m.next_state(_state, _bit)
    assert _got == _want, f"next_state({_state!r}, {_bit}) gave {_got!r}, expected {_want!r}"
assert _m.output() == 0, "S0 does not assert the output"
assert SequenceDetector("S1011").output() == 1, "S1011 asserts the output"
try:
    SequenceDetector("S99")
    assert False, "an unknown start state should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The detector finds overlapping patterns", "code": r'''
for _stream in ([1, 1, 0, 1, 0, 1, 1, 0, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1],
                [0] * 6,
                [1, 0, 1, 1, 1, 0, 1, 1]):
    _want = [1 if _stream[max(0, _i - 3):_i + 1] == [1, 0, 1, 1] else 0
             for _i in range(len(_stream))]
    _got = SequenceDetector().run(_stream)
    assert _got == _want, f"run({_stream!r}) gave {_got!r}, expected {_want!r}"
assert SequenceDetector().run([]) == [], "an empty stream produces no outputs"
try:
    SequenceDetector().step(2)
    assert False, "step(2) should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Two's complement and the ALU",
            "summary": "One adder, several operations, and the four flags that interpret the result.",
            "concepts": [
                "Two's complement: negate by inverting every bit and adding one",
                "The same adder serves signed and unsigned operands — only the flags differ",
                "Subtraction is `a + (~b) + 1`, so one circuit does both",
                "Zero and negative flags read the result; carry and overflow read the operation",
                "Carry is the unsigned out-of-range signal; overflow is the signed one",
                "Overflow for addition: both operands share a sign and the result does not",
                "Logical shifts and their carry-out; why arithmetic right shift differs",
            ],
            "lab": {
                "title": "An n-bit ALU with correct flags",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Build the arithmetic-logic unit that the capstone datapath will use.

## Helpers

**`to_signed(value, width)`** — read an unsigned word as two's complement.
**`from_signed(value, width)`** — the reverse, producing the raw word.
Both raise `ValueError` for a value outside the representable range.

```text
to_signed(0xFF, 8)   -> -1
to_signed(0x80, 8)   -> -128
from_signed(-1, 8)   ->  255
from_signed(-128, 8) ->  128
from_signed(128, 8)  ->  ValueError
```

## `ALU(width=8)`

`execute(op, a, b=0)` returns `(result, flags)`. `op` is one of `"ADD"`,
`"SUB"`, `"AND"`, `"OR"`, `"XOR"`, `"SHL"`, `"SHR"` — anything else is a
`ValueError`, as is an operand outside `0 .. 2**width - 1`. `result` is always
masked back down to `width` bits.

`flags` is a dict with exactly the keys `"Z"`, `"N"`, `"C"`, `"V"`, each 0 or 1:

- **Z** — the result is zero.
- **N** — the top bit of the result is set (negative when read as signed).
- **C** — carry out. For `ADD` it is the bit that fell off the top. For `SUB`
  it is the carry out of `a + (~b & mask) + 1`, so **1 means no borrow**. For
  `SHL` it is the bit shifted out of the top, for `SHR` the bit shifted out of
  the bottom, and for the logical operations it is 0.
- **V** — signed overflow. Nonzero only for `ADD` and `SUB`. For addition it is
  set when both operands have the same sign bit and the result does not; for
  subtraction, when the operands differ in sign and the result differs from `a`.

Worked examples for `width=8`:

```text
ADD 0x7F, 0x01  ->  0x80  Z=0 N=1 C=0 V=1     127 + 1 overflows signed
ADD 0xFF, 0x01  ->  0x00  Z=1 N=0 C=1 V=0      -1 + 1 is fine, unsigned wraps
SUB 0x05, 0x03  ->  0x02  Z=0 N=0 C=1 V=0     no borrow
SUB 0x03, 0x05  ->  0xFE  Z=0 N=1 C=0 V=0     borrow; the answer is -2
SUB 0x80, 0x01  ->  0x7F  Z=0 N=0 C=1 V=1    -128 - 1 overflows signed
SHL 0x80        ->  0x00  Z=1 N=0 C=1 V=0
SHR 0x01        ->  0x00  Z=1 N=0 C=1 V=0
```

`width` is a constructor argument, so the same class is a 4-bit or a 16-bit
ALU. Write the masks in terms of `self.width`; do not hard-code `0xFF`.
''',
                "files": [{"name": "main.py", "content": r'''
def to_signed(value, width):
    """Read an unsigned word as two's complement."""
    # your code here


def from_signed(value, width):
    """Turn a signed integer into its raw width-bit word."""
    # your code here


class ALU:
    """An n-bit arithmetic-logic unit with Z, N, C and V flags."""

    OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR")

    def __init__(self, width=8):
        self.width = width
        self.mask = (1 << width) - 1
        self.sign_bit = 1 << (width - 1)

    def execute(self, op, a, b=0):
        """(result, {"Z": .., "N": .., "C": .., "V": ..})."""
        # your code here


alu = ALU(8)
print(alu.execute("ADD", 0x7F, 0x01))
print(alu.execute("SUB", 0x03, 0x05))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def to_signed(value, width):
    """Read an unsigned word as two's complement."""
    if width < 1:
        raise ValueError("width must be at least 1")
    if value < 0 or value >= (1 << width):
        raise ValueError(f"{value} is not a {width}-bit word")
    if value >= (1 << (width - 1)):
        return value - (1 << width)
    return value


def from_signed(value, width):
    """Turn a signed integer into its raw width-bit word."""
    if width < 1:
        raise ValueError("width must be at least 1")
    low = -(1 << (width - 1))
    high = (1 << (width - 1)) - 1
    if value < low or value > high:
        raise ValueError(f"{value} is not representable in {width} signed bits")
    return value & ((1 << width) - 1)


class ALU:
    """An n-bit arithmetic-logic unit with Z, N, C and V flags."""

    OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR")

    def __init__(self, width=8):
        self.width = width
        self.mask = (1 << width) - 1
        self.sign_bit = 1 << (width - 1)

    def execute(self, op, a, b=0):
        """(result, {"Z": .., "N": .., "C": .., "V": ..})."""
        if op not in self.OPS:
            raise ValueError(f"unknown operation {op!r}")
        for operand in (a, b):
            if operand < 0 or operand > self.mask:
                raise ValueError(f"{operand} is not a {self.width}-bit word")

        carry = 0
        overflow = 0
        if op == "ADD":
            total = a + b
            result = total & self.mask
            carry = 1 if total > self.mask else 0
            overflow = 1 if (~(a ^ b)) & (a ^ result) & self.sign_bit else 0
        elif op == "SUB":
            total = a + (~b & self.mask) + 1
            result = total & self.mask
            carry = 1 if total > self.mask else 0
            overflow = 1 if (a ^ b) & (a ^ result) & self.sign_bit else 0
        elif op == "AND":
            result = a & b
        elif op == "OR":
            result = a | b
        elif op == "XOR":
            result = a ^ b
        elif op == "SHL":
            result = (a << 1) & self.mask
            carry = 1 if a & self.sign_bit else 0
        else:
            result = a >> 1
            carry = a & 1

        flags = {
            "Z": 1 if result == 0 else 0,
            "N": 1 if result & self.sign_bit else 0,
            "C": carry,
            "V": overflow,
        }
        return result, flags


alu = ALU(8)
print(alu.execute("ADD", 0x7F, 0x01))
print(alu.execute("SUB", 0x03, 0x05))
'''}],
                "hints": [
                    "`to_signed` only has to subtract `1 << width` when the sign bit is set; everything below that is already the right number.",
                    "Do subtraction the way the hardware does: `total = a + (~b & self.mask) + 1`. The carry flag is then simply whether `total` exceeded the mask.",
                    "Signed overflow for ADD is `(~(a ^ b)) & (a ^ result) & self.sign_bit` — 'the operands agreed on sign and the result disagreed'. For SUB, drop the outer complement: `(a ^ b) & (a ^ result) & self.sign_bit`.",
                    "Set Z and N once at the end from `result`; only C and V depend on which operation ran.",
                ],
                "tests": [
                    {"name": "to_signed / from_signed", "code": r'''
for _v, _want in [(0, 0), (127, 127), (128, -128), (255, -1), (1, 1)]:
    _got = to_signed(_v, 8)
    assert _got == _want, f"to_signed({_v}, 8) gave {_got!r}, expected {_want}"
for _v, _want in [(0, 0), (-1, 255), (-128, 128), (127, 127)]:
    _got = from_signed(_v, 8)
    assert _got == _want, f"from_signed({_v}, 8) gave {_got!r}, expected {_want}"
assert to_signed(8, 4) == -8, f"to_signed(8, 4) gave {to_signed(8, 4)!r}, expected -8"
for _v in range(256):
    assert from_signed(to_signed(_v, 8), 8) == _v, f"round-trip failed for {_v}"
for _args in [(256, 8), (-1, 8)]:
    try:
        to_signed(*_args)
        assert False, f"to_signed{_args!r} should raise ValueError"
    except ValueError:
        pass
for _args in [(128, 8), (-129, 8)]:
    try:
        from_signed(*_args)
        assert False, f"from_signed{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Logical operations and their flags", "code": r'''
_alu = ALU(8)
for _op, _a, _b, _want in [("AND", 0xF0, 0x3C, 0x30), ("OR", 0xF0, 0x0F, 0xFF),
                           ("XOR", 0xFF, 0x0F, 0xF0), ("AND", 0x0F, 0xF0, 0x00)]:
    _r, _f = _alu.execute(_op, _a, _b)
    assert _r == _want, f"{_op} {_a:#04x}, {_b:#04x} gave {_r:#04x}, expected {_want:#04x}"
    assert _f["C"] == 0 and _f["V"] == 0, f"{_op} must leave C and V clear, got {_f!r}"
_r, _f = _alu.execute("OR", 0xF0, 0x0F)
assert _f == {"Z": 0, "N": 1, "C": 0, "V": 0}, f"OR 0xF0, 0x0F flags were {_f!r}"
_r, _f = _alu.execute("AND", 0x0F, 0xF0)
assert _f == {"Z": 1, "N": 0, "C": 0, "V": 0}, f"AND 0x0F, 0xF0 flags were {_f!r}"
'''},
                    {"name": "ADD, with carry and overflow", "code": r'''
_alu = ALU(8)
for _a, _b, _wr, _wf in [
        (0x7F, 0x01, 0x80, {"Z": 0, "N": 1, "C": 0, "V": 1}),
        (0xFF, 0x01, 0x00, {"Z": 1, "N": 0, "C": 1, "V": 0}),
        (0x01, 0x02, 0x03, {"Z": 0, "N": 0, "C": 0, "V": 0}),
        (0x80, 0x80, 0x00, {"Z": 1, "N": 0, "C": 1, "V": 1}),
        (0x00, 0x00, 0x00, {"Z": 1, "N": 0, "C": 0, "V": 0})]:
    _r, _f = _alu.execute("ADD", _a, _b)
    assert _r == _wr, f"ADD {_a:#04x}, {_b:#04x} gave {_r:#04x}, expected {_wr:#04x}"
    assert _f == _wf, f"ADD {_a:#04x}, {_b:#04x} flags were {_f!r}, expected {_wf!r}"
'''},
                    {"name": "SUB, with borrow and overflow", "code": r'''
_alu = ALU(8)
for _a, _b, _wr, _wf in [
        (0x05, 0x03, 0x02, {"Z": 0, "N": 0, "C": 1, "V": 0}),
        (0x03, 0x05, 0xFE, {"Z": 0, "N": 1, "C": 0, "V": 0}),
        (0x80, 0x01, 0x7F, {"Z": 0, "N": 0, "C": 1, "V": 1}),
        (0x07, 0x07, 0x00, {"Z": 1, "N": 0, "C": 1, "V": 0}),
        (0x00, 0x01, 0xFF, {"Z": 0, "N": 1, "C": 0, "V": 0})]:
    _r, _f = _alu.execute("SUB", _a, _b)
    assert _r == _wr, f"SUB {_a:#04x}, {_b:#04x} gave {_r:#04x}, expected {_wr:#04x}"
    assert _f == _wf, f"SUB {_a:#04x}, {_b:#04x} flags were {_f!r}, expected {_wf!r}"
'''},
                    {"name": "Shifts and their carry-out", "code": r'''
_alu = ALU(8)
for _op, _a, _wr, _wc in [("SHL", 0x01, 0x02, 0), ("SHL", 0x80, 0x00, 1),
                          ("SHL", 0xC0, 0x80, 1), ("SHR", 0x01, 0x00, 1),
                          ("SHR", 0xFF, 0x7F, 1), ("SHR", 0x02, 0x01, 0)]:
    _r, _f = _alu.execute(_op, _a)
    assert _r == _wr, f"{_op} {_a:#04x} gave {_r:#04x}, expected {_wr:#04x}"
    assert _f["C"] == _wc, f"{_op} {_a:#04x} gave C={_f['C']}, expected {_wc}"
    assert _f["V"] == 0, f"{_op} must leave V clear, got {_f!r}"
_r, _f = _alu.execute("SHL", 0x40)
assert (_r, _f["N"]) == (0x80, 1), f"SHL 0x40 gave {(_r, _f['N'])!r}, expected (128, 1)"
'''},
                    {"name": "ADD and SUB agree with plain arithmetic", "code": r'''
_alu = ALU(8)
for _a in range(0, 256, 7):
    for _b in range(0, 256, 5):
        _r, _f = _alu.execute("ADD", _a, _b)
        assert _r == (_a + _b) & 0xFF, f"ADD {_a}, {_b} gave {_r}, expected {(_a + _b) & 0xFF}"
        assert _f["C"] == (1 if _a + _b > 255 else 0), f"ADD {_a}, {_b} carry was {_f['C']}"
        _signed = to_signed(_a, 8) + to_signed(_b, 8)
        _wantv = 0 if -128 <= _signed <= 127 else 1
        assert _f["V"] == _wantv, f"ADD {_a}, {_b} gave V={_f['V']}, expected {_wantv}"
        _r, _f = _alu.execute("SUB", _a, _b)
        assert _r == (_a - _b) & 0xFF, f"SUB {_a}, {_b} gave {_r}, expected {(_a - _b) & 0xFF}"
        assert _f["C"] == (1 if _a >= _b else 0), f"SUB {_a}, {_b} carry was {_f['C']}"
        _signed = to_signed(_a, 8) - to_signed(_b, 8)
        _wantv = 0 if -128 <= _signed <= 127 else 1
        assert _f["V"] == _wantv, f"SUB {_a}, {_b} gave V={_f['V']}, expected {_wantv}"
'''},
                    {"name": "Bad operations and operands are refused", "code": r'''
_alu = ALU(8)
for _args in [("MUL", 1, 2), ("add", 1, 2), ("ADD", 256, 0), ("ADD", 0, -1)]:
    try:
        _alu.execute(*_args)
        assert False, f"execute{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The same class works at other widths", "code": r'''
_alu4 = ALU(4)
_r, _f = _alu4.execute("ADD", 0b1111, 0b0001)
assert (_r, _f) == (0, {"Z": 1, "N": 0, "C": 1, "V": 0}), \
    f"4-bit ADD 15, 1 gave {(_r, _f)!r}, expected (0, Z=1 C=1)"
_r, _f = _alu4.execute("ADD", 0b0111, 0b0001)
assert (_r, _f["V"], _f["N"]) == (8, 1, 1), \
    f"4-bit ADD 7, 1 gave {(_r, _f['V'], _f['N'])!r}, expected (8, 1, 1)"
_r, _f = _alu4.execute("SHL", 0b1000)
assert (_r, _f["C"], _f["Z"]) == (0, 1, 1), f"4-bit SHL 8 gave {(_r, _f['C'], _f['Z'])!r}"
try:
    _alu4.execute("ADD", 16, 0)
    assert False, "16 is not a 4-bit word"
except ValueError:
    pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an 8-bit datapath simulator",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Put the four labs together into a machine that executes instructions.
`datapath.py` holds the hardware and is what the checks import; `main.py` is a
demo that loads a program and runs it.

## Memory and encoding

256 bytes of memory, byte-addressed. Every instruction is **two bytes**:

```text
byte 0:  opcode (4 bits) | rd (2 bits) | rs (2 bits)
byte 1:  operand — an immediate or an address
```

The sixteen opcodes are already named as module constants:

```text
0 NOP                 8  XOR rd, rs
1 LDI rd, imm         9  SHL rd
2 LD  rd, addr        10 SHR rd
3 ST  rs, addr        11 JMP addr
4 ADD rd, rs          12 JZ  addr     (taken when the Z flag is set)
5 SUB rd, rs          13 JNZ addr
6 AND rd, rs          14 MOV rd, rs
7 OR  rd, rs          15 HLT
```

`encode(op, rd=0, rs=0, operand=0)` returns the two bytes and raises
`ValueError` for a field that will not fit. `decode(byte0, byte1)` returns
`(op, rd, rs, operand)`. `assemble(instructions)` flattens a list of tuples into
a flat list of bytes, padding short tuples with zeros.

## `RegisterFile(count=4, width=8)`

`read(index)` and `write(index, value)`. Writes are masked to `width` bits;
an index outside `0 .. count - 1` is a `ValueError`.

## `ALU(width=8)`

Exactly the unit from module 4: `execute(op, a, b=0) -> (result, flags)` with
`"Z"`, `"N"`, `"C"`, `"V"`.

## `CPU(program=None, start=0)`

A Moore control FSM over the states `"FETCH"`, `"DECODE"`, `"EXECUTE"` and
`"HALTED"`, plus `pc`, `mem`, `regs`, `flags` and the instruction register `ir`.

- `load_program(program, start=0)` — assemble and write the bytes into memory.
  `ValueError` if the program does not fit.
- `tick()` — advance **one** control state and return the new state.
  - FETCH: latch `mem[pc]` and `mem[pc + 1]` into `ir`, advance `pc` by 2
    (wrapping at 256), go to DECODE.
  - DECODE: split `ir` into `op`, `rd`, `rs`, `operand`, go to EXECUTE.
  - EXECUTE: perform the operation, then go back to FETCH — or to HALTED
    for `HLT`. A tick in HALTED does nothing.
- `step()` — tick until the machine is back in FETCH or has HALTED.
- `run(max_steps=10000)` — step until HALTED, returning the number of
  instructions executed. Raise `RuntimeError` if the limit is reached first:
  a simulator that hangs the browser tab is not a simulator.

Only ADD, SUB, AND, OR, XOR, SHL and SHR touch `flags`; loads, stores, moves
and jumps leave them alone, which is what makes `OR rd, rd` a useful way to
test a register before a branch.

## The micro-program

Finish `SUM_PROGRAM`: it must read `n` from address `0x40`, compute
`n + (n-1) + ... + 1` and store the total at `0x41`, then halt. Remember that
jump targets are **byte** addresses, so instruction `k` sits at address `2 * k`.
The sketch below is one correct shape; the loop needs a flag-setting
instruction before its branch.

```text
addr 0   LD  R0, 0x40      R0 = n
addr 2   LDI R1, 0         R1 = running total
addr 4   LDI R3, 1         R3 = the constant 1
addr 6   OR  R0, R0        set Z from R0 without changing it
addr 8   JZ  16            n reached zero, go and store
addr 10  ADD R1, R0        total += n
addr 12  SUB R0, R3        n -= 1
addr 14  JMP 6             back to the test
addr 16  ST  R1, 0x41      store the total
addr 18  HLT
```
''',
        "deliverables": [
            "`datapath.py` — `encode`/`decode`/`assemble`, `RegisterFile`, `ALU` and `CPU`, importable with no side effects",
            "A control FSM whose `tick()` exposes FETCH, DECODE, EXECUTE and HALTED as separate observable states",
            "All sixteen opcodes implemented, with flags updated only by the arithmetic and logic operations",
            "`SUM_PROGRAM` — a working micro-program that reads `n` from 0x40 and leaves the triangular number at 0x41",
            "`main.py` — a demo that loads the program for a couple of values of `n` and prints the results",
            "Termination safety: `run()` raises `RuntimeError` rather than looping forever",
        ],
        "constraints": [
            "Standard library only, and no imports are needed at all",
            "`datapath.py` must define constants, classes and functions only — running it prints nothing",
            "Memory is exactly 256 bytes and every stored value stays in `0 .. 255`",
            "The program counter wraps at 256 rather than running off the end of memory",
            "Two `CPU()` objects must not share memory or registers",
        ],
        "rubric": [
            {"criterion": "Instruction set correctness", "weight": 35,
             "evidence": "Every opcode moves the right data, and encode/decode round-trip for all valid field combinations."},
            {"criterion": "Control FSM", "weight": 20,
             "evidence": "tick() exposes the three-phase cycle, HLT parks the machine, and step()/run() are built on tick() rather than duplicating it."},
            {"criterion": "Flags and branching", "weight": 20,
             "evidence": "Z, N, C and V follow the module 4 rules, only arithmetic and logic write them, and JZ/JNZ branch on the latched Z."},
            {"criterion": "Micro-program", "weight": 15,
             "evidence": "SUM_PROGRAM returns the correct total for n = 0, 1 and larger values, using byte addresses for its jump targets."},
            {"criterion": "Robustness and readability", "weight": 10,
             "evidence": "Bad opcodes, registers and addresses raise ValueError; run() refuses to hang; every public method carries a docstring."},
        ],
        "hints": [
            "Write `encode` and `decode` first and test them against each other — every later bug looks like an encoding bug until you rule it out.",
            "Keep `tick()` as a single `if`/`elif` over `self.state`; `step()` should then be nothing but `while True: self.tick()` with a stop condition.",
            "Dispatch the opcode inside EXECUTE from a plain chain of comparisons against the module constants, and map the arithmetic opcodes to their ALU operation names with one dict.",
            "The jump instructions assign to `self.pc` *after* FETCH has already advanced it, so the branch simply overwrites the sequential address.",
            "In `SUM_PROGRAM`, remember that `SUB R0, R3` sets Z but `JMP` does not — the `OR R0, R0` at the top of the loop is what makes the test at address 8 meaningful.",
        ],
        "files": [
            {"name": "datapath.py", "content": r'''
NOP, LDI, LD, ST, ADD, SUB, AND, OR, XOR, SHL, SHR, JMP, JZ, JNZ, MOV, HLT = range(16)

OPNAMES = {
    NOP: "NOP", LDI: "LDI", LD: "LD", ST: "ST", ADD: "ADD", SUB: "SUB",
    AND: "AND", OR: "OR", XOR: "XOR", SHL: "SHL", SHR: "SHR", JMP: "JMP",
    JZ: "JZ", JNZ: "JNZ", MOV: "MOV", HLT: "HLT",
}

MEM_SIZE = 256


def encode(op, rd=0, rs=0, operand=0):
    """(byte0, byte1) for one instruction. ValueError on a field that will not fit."""
    # your code here


def decode(byte0, byte1):
    """(op, rd, rs, operand)."""
    # your code here


def assemble(instructions):
    """A list of (op, rd, rs, operand) tuples as a flat list of bytes."""
    # your code here


class RegisterFile:
    """A small bank of width-bit registers."""

    def __init__(self, count=4, width=8):
        # your code here
        pass

    def read(self, index):
        """The value in register `index`."""
        # your code here

    def write(self, index, value):
        """Store `value`, masked to the register width."""
        # your code here


class ALU:
    """The unit from module 4, reused unchanged."""

    OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR")

    def __init__(self, width=8):
        self.width = width
        self.mask = (1 << width) - 1
        self.sign_bit = 1 << (width - 1)

    def execute(self, op, a, b=0):
        """(result, {"Z": .., "N": .., "C": .., "V": ..})."""
        # your code here


class CPU:
    """Memory, registers, an ALU and a three-phase control FSM."""

    STATES = ("FETCH", "DECODE", "EXECUTE", "HALTED")

    def __init__(self, program=None, start=0):
        # your code here
        pass

    def load_program(self, program, start=0):
        """Assemble the instructions into memory at `start`."""
        # your code here

    def tick(self):
        """Advance one control state and return the new state."""
        # your code here

    def step(self):
        """Run one whole instruction."""
        # your code here

    def run(self, max_steps=10000):
        """Step until HALTED; RuntimeError if the machine will not stop."""
        # your code here


# n at 0x40, the sum 1..n at 0x41. Finish it.
SUM_PROGRAM = [
    (LD, 0, 0, 0x40),
    (LDI, 1, 0, 0),
]
'''},
            {"name": "main.py", "content": r'''
from datapath import CPU, SUM_PROGRAM

for n in (0, 1, 5, 10):
    cpu = CPU(SUM_PROGRAM)
    cpu.mem[0x40] = n
    steps = cpu.run()
    print(f"n={n:>3}  sum={cpu.mem[0x41]:>3}  instructions={steps}")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "datapath.py", "content": r'''
NOP, LDI, LD, ST, ADD, SUB, AND, OR, XOR, SHL, SHR, JMP, JZ, JNZ, MOV, HLT = range(16)

OPNAMES = {
    NOP: "NOP", LDI: "LDI", LD: "LD", ST: "ST", ADD: "ADD", SUB: "SUB",
    AND: "AND", OR: "OR", XOR: "XOR", SHL: "SHL", SHR: "SHR", JMP: "JMP",
    JZ: "JZ", JNZ: "JNZ", MOV: "MOV", HLT: "HLT",
}

MEM_SIZE = 256

ALU_OP = {ADD: "ADD", SUB: "SUB", AND: "AND", OR: "OR", XOR: "XOR",
          SHL: "SHL", SHR: "SHR"}


def encode(op, rd=0, rs=0, operand=0):
    """(byte0, byte1) for one instruction. ValueError on a field that will not fit."""
    if not 0 <= op <= 15:
        raise ValueError(f"opcode {op} does not fit in 4 bits")
    if not 0 <= rd <= 3:
        raise ValueError(f"no register R{rd}")
    if not 0 <= rs <= 3:
        raise ValueError(f"no register R{rs}")
    if not 0 <= operand <= 255:
        raise ValueError(f"operand {operand} does not fit in a byte")
    return (op << 4) | (rd << 2) | rs, operand


def decode(byte0, byte1):
    """(op, rd, rs, operand)."""
    return byte0 >> 4, (byte0 >> 2) & 3, byte0 & 3, byte1


def assemble(instructions):
    """A list of (op, rd, rs, operand) tuples as a flat list of bytes."""
    out = []
    for instruction in instructions:
        fields = tuple(instruction) + (0,) * (4 - len(instruction))
        byte0, byte1 = encode(*fields)
        out.append(byte0)
        out.append(byte1)
    return out


class RegisterFile:
    """A small bank of width-bit registers."""

    def __init__(self, count=4, width=8):
        self.count = count
        self.width = width
        self.mask = (1 << width) - 1
        self.values = [0] * count

    def _check(self, index):
        if not 0 <= index < self.count:
            raise ValueError(f"no register R{index}")

    def read(self, index):
        """The value in register `index`."""
        self._check(index)
        return self.values[index]

    def write(self, index, value):
        """Store `value`, masked to the register width."""
        self._check(index)
        self.values[index] = value & self.mask


class ALU:
    """The unit from module 4, reused unchanged."""

    OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR")

    def __init__(self, width=8):
        self.width = width
        self.mask = (1 << width) - 1
        self.sign_bit = 1 << (width - 1)

    def execute(self, op, a, b=0):
        """(result, {"Z": .., "N": .., "C": .., "V": ..})."""
        if op not in self.OPS:
            raise ValueError(f"unknown operation {op!r}")
        for operand in (a, b):
            if operand < 0 or operand > self.mask:
                raise ValueError(f"{operand} is not a {self.width}-bit word")

        carry = 0
        overflow = 0
        if op == "ADD":
            total = a + b
            result = total & self.mask
            carry = 1 if total > self.mask else 0
            overflow = 1 if (~(a ^ b)) & (a ^ result) & self.sign_bit else 0
        elif op == "SUB":
            total = a + (~b & self.mask) + 1
            result = total & self.mask
            carry = 1 if total > self.mask else 0
            overflow = 1 if (a ^ b) & (a ^ result) & self.sign_bit else 0
        elif op == "AND":
            result = a & b
        elif op == "OR":
            result = a | b
        elif op == "XOR":
            result = a ^ b
        elif op == "SHL":
            result = (a << 1) & self.mask
            carry = 1 if a & self.sign_bit else 0
        else:
            result = a >> 1
            carry = a & 1

        return result, {
            "Z": 1 if result == 0 else 0,
            "N": 1 if result & self.sign_bit else 0,
            "C": carry,
            "V": overflow,
        }


class CPU:
    """Memory, registers, an ALU and a three-phase control FSM."""

    STATES = ("FETCH", "DECODE", "EXECUTE", "HALTED")

    def __init__(self, program=None, start=0):
        self.mem = [0] * MEM_SIZE
        self.regs = RegisterFile(4, 8)
        self.alu = ALU(8)
        self.flags = {"Z": 0, "N": 0, "C": 0, "V": 0}
        self.pc = start
        self.state = "FETCH"
        self.ir = (0, 0)
        self.op = NOP
        self.rd = 0
        self.rs = 0
        self.operand = 0
        if program:
            self.load_program(program, start)

    def load_program(self, program, start=0):
        """Assemble the instructions into memory at `start`."""
        code = assemble(program)
        if start < 0 or start + len(code) > MEM_SIZE:
            raise ValueError("the program does not fit in memory")
        for offset, byte in enumerate(code):
            self.mem[start + offset] = byte

    def tick(self):
        """Advance one control state and return the new state."""
        if self.state == "FETCH":
            self.ir = (self.mem[self.pc], self.mem[(self.pc + 1) % MEM_SIZE])
            self.pc = (self.pc + 2) % MEM_SIZE
            self.state = "DECODE"
        elif self.state == "DECODE":
            self.op, self.rd, self.rs, self.operand = decode(*self.ir)
            self.state = "EXECUTE"
        elif self.state == "EXECUTE":
            self._execute()
        return self.state

    def _execute(self):
        """Carry out the decoded instruction and choose the next control state."""
        op, rd, rs, operand = self.op, self.rd, self.rs, self.operand
        if op == HLT:
            self.state = "HALTED"
            return
        if op == NOP:
            pass
        elif op == LDI:
            self.regs.write(rd, operand)
        elif op == LD:
            self.regs.write(rd, self.mem[operand])
        elif op == ST:
            self.mem[operand] = self.regs.read(rs)
        elif op == MOV:
            self.regs.write(rd, self.regs.read(rs))
        elif op in (ADD, SUB, AND, OR, XOR):
            result, flags = self.alu.execute(ALU_OP[op], self.regs.read(rd),
                                             self.regs.read(rs))
            self.regs.write(rd, result)
            self.flags = flags
        elif op in (SHL, SHR):
            result, flags = self.alu.execute(ALU_OP[op], self.regs.read(rd))
            self.regs.write(rd, result)
            self.flags = flags
        elif op == JMP:
            self.pc = operand
        elif op == JZ:
            if self.flags["Z"]:
                self.pc = operand
        elif op == JNZ:
            if not self.flags["Z"]:
                self.pc = operand
        else:
            raise ValueError(f"unknown opcode {op}")
        self.state = "FETCH"

    def step(self):
        """Run one whole instruction."""
        if self.state == "HALTED":
            return self.state
        while True:
            self.tick()
            if self.state in ("FETCH", "HALTED"):
                return self.state

    def run(self, max_steps=10000):
        """Step until HALTED; RuntimeError if the machine will not stop."""
        steps = 0
        while self.state != "HALTED":
            if steps >= max_steps:
                raise RuntimeError(f"no HLT within {max_steps} instructions")
            self.step()
            steps += 1
        return steps


# n at 0x40, the sum 1..n at 0x41.
SUM_PROGRAM = [
    (LD, 0, 0, 0x40),
    (LDI, 1, 0, 0),
    (LDI, 3, 0, 1),
    (OR, 0, 0, 0),
    (JZ, 0, 0, 16),
    (ADD, 1, 0, 0),
    (SUB, 0, 3, 0),
    (JMP, 0, 0, 6),
    (ST, 0, 1, 0x41),
    (HLT, 0, 0, 0),
]
'''},
            {"name": "main.py", "content": r'''
from datapath import CPU, SUM_PROGRAM

for n in (0, 1, 5, 10):
    cpu = CPU(SUM_PROGRAM)
    cpu.mem[0x40] = n
    steps = cpu.run()
    print(f"n={n:>3}  sum={cpu.mem[0x41]:>3}  instructions={steps}")
'''},
        ],
        "tests": [
            {"name": "encode / decode round-trip", "code": r'''
from datapath import encode, decode, assemble, LDI, ADD, JMP, HLT
_b0, _b1 = encode(ADD, 2, 3, 0)
assert (_b0, _b1) == ((4 << 4) | (2 << 2) | 3, 0), f"encode(ADD, 2, 3) gave {(_b0, _b1)!r}"
for _op in range(16):
    for _rd in range(4):
        for _rs in range(4):
            for _operand in (0, 1, 128, 255):
                assert decode(*encode(_op, _rd, _rs, _operand)) == (_op, _rd, _rs, _operand), \
                    f"round-trip failed for {(_op, _rd, _rs, _operand)!r}"
assert assemble([(LDI, 1, 0, 7), (HLT,)]) == [(1 << 4) | (1 << 2), 7, 15 << 4, 0], \
    f"assemble gave {assemble([(LDI, 1, 0, 7), (HLT,)])!r}"
for _bad in [(16, 0, 0, 0), (-1, 0, 0, 0), (ADD, 4, 0, 0), (ADD, 0, 4, 0), (JMP, 0, 0, 256)]:
    try:
        encode(*_bad)
        assert False, f"encode{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "RegisterFile masks and checks", "code": r'''
from datapath import RegisterFile
_rf = RegisterFile(4, 8)
assert _rf.read(0) == 0, "registers start at zero"
_rf.write(2, 300)
assert _rf.read(2) == 300 & 0xFF, f"R2 is {_rf.read(2)!r}, expected {300 & 0xFF} after masking"
_rf.write(3, -1)
assert _rf.read(3) == 255, f"R3 is {_rf.read(3)!r}, expected 255"
for _bad in (4, -1, 99):
    try:
        _rf.read(_bad)
        assert False, f"read({_bad}) should raise ValueError"
    except ValueError:
        pass
try:
    _rf.write(4, 0)
    assert False, "write to R4 should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The ALU still sets the module 4 flags", "code": r'''
from datapath import ALU
_alu = ALU(8)
for _op, _a, _b, _wr, _wf in [
        ("ADD", 0x7F, 0x01, 0x80, {"Z": 0, "N": 1, "C": 0, "V": 1}),
        ("ADD", 0xFF, 0x01, 0x00, {"Z": 1, "N": 0, "C": 1, "V": 0}),
        ("SUB", 0x03, 0x05, 0xFE, {"Z": 0, "N": 1, "C": 0, "V": 0}),
        ("SUB", 0x80, 0x01, 0x7F, {"Z": 0, "N": 0, "C": 1, "V": 1}),
        ("OR", 0x00, 0x00, 0x00, {"Z": 1, "N": 0, "C": 0, "V": 0})]:
    _r, _f = _alu.execute(_op, _a, _b)
    assert (_r, _f) == (_wr, _wf), \
        f"{_op} {_a:#04x}, {_b:#04x} gave {(_r, _f)!r}, expected {(_wr, _wf)!r}"
'''},
            {"name": "The control FSM runs three phases per instruction", "code": r'''
from datapath import CPU, LDI, HLT
_cpu = CPU([(LDI, 1, 0, 7), (HLT,)])
assert _cpu.state == "FETCH", f"a fresh CPU starts in FETCH, got {_cpu.state!r}"
assert _cpu.pc == 0, f"pc starts at 0, got {_cpu.pc!r}"
assert _cpu.tick() == "DECODE", "FETCH is followed by DECODE"
assert _cpu.pc == 2, f"FETCH advances the pc by 2, got {_cpu.pc!r}"
assert _cpu.tick() == "EXECUTE", "DECODE is followed by EXECUTE"
assert _cpu.regs.read(1) == 0, "the write happens in EXECUTE, not in DECODE"
assert _cpu.tick() == "FETCH", "EXECUTE returns to FETCH"
assert _cpu.regs.read(1) == 7, f"R1 is {_cpu.regs.read(1)!r}, expected 7"
assert _cpu.step() == "HALTED", "the second instruction is HLT"
assert _cpu.tick() == "HALTED", "a halted machine stays halted"
'''},
            {"name": "Data movement: LDI, MOV, ST and LD", "code": r'''
from datapath import CPU, LDI, MOV, ST, LD, HLT
_cpu = CPU([(LDI, 0, 0, 0x2A), (MOV, 1, 0, 0), (ST, 0, 1, 0x80),
            (LD, 2, 0, 0x80), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 0x2A, f"R0 is {_cpu.regs.read(0)!r}, expected 42"
assert _cpu.regs.read(1) == 0x2A, f"MOV left R1 at {_cpu.regs.read(1)!r}, expected 42"
assert _cpu.mem[0x80] == 0x2A, f"ST wrote {_cpu.mem[0x80]!r} to 0x80, expected 42"
assert _cpu.regs.read(2) == 0x2A, f"LD left R2 at {_cpu.regs.read(2)!r}, expected 42"
_other = CPU()
assert _other.mem[0x80] == 0 and _other.regs.read(0) == 0, \
    "two CPUs must not share memory or registers"
'''},
            {"name": "Arithmetic and logic write back and set flags", "code": r'''
from datapath import CPU, LDI, ADD, SUB, AND, XOR, SHL, SHR, HLT
_cpu = CPU([(LDI, 0, 0, 200), (LDI, 1, 0, 100), (ADD, 0, 1, 0), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 44, f"200 + 100 in 8 bits is 44, got {_cpu.regs.read(0)!r}"
assert _cpu.flags["C"] == 1, f"that addition carries; flags were {_cpu.flags!r}"
_cpu = CPU([(LDI, 0, 0, 5), (LDI, 1, 0, 5), (SUB, 0, 1, 0), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 0 and _cpu.flags["Z"] == 1, \
    f"5 - 5 should leave 0 with Z set, got {_cpu.regs.read(0)!r} and {_cpu.flags!r}"
_cpu = CPU([(LDI, 0, 0, 0xF0), (LDI, 1, 0, 0x3C), (AND, 0, 1, 0),
            (LDI, 2, 0, 0x81), (SHL, 2, 0, 0), (LDI, 3, 0, 0x05), (SHR, 3, 0, 0), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 0x30, f"0xF0 AND 0x3C is 0x30, got {_cpu.regs.read(0):#04x}"
assert _cpu.regs.read(2) == 0x02, f"SHL 0x81 is 0x02, got {_cpu.regs.read(2):#04x}"
assert _cpu.regs.read(3) == 0x02, f"SHR 0x05 is 0x02, got {_cpu.regs.read(3):#04x}"
_cpu = CPU([(LDI, 0, 0, 9), (XOR, 0, 0, 0), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 0, "XOR of a register with itself clears it"
'''},
            {"name": "Loads and jumps leave the flags alone", "code": r'''
from datapath import CPU, LDI, SUB, LD, MOV, HLT
_cpu = CPU([(LDI, 0, 0, 4), (LDI, 1, 0, 4), (SUB, 0, 1, 0),
            (LDI, 2, 0, 99), (MOV, 3, 2, 0), (LD, 1, 0, 0x90), (HLT,)])
_cpu.run()
assert _cpu.flags["Z"] == 1, \
    f"only ALU operations touch the flags, so Z should still be 1; got {_cpu.flags!r}"
'''},
            {"name": "Branches", "code": r'''
from datapath import CPU, LDI, SUB, JZ, JNZ, JMP, HLT
_taken = CPU([(LDI, 0, 0, 3), (LDI, 1, 0, 3), (SUB, 0, 1, 0), (JZ, 0, 0, 10),
              (LDI, 2, 0, 111), (LDI, 3, 0, 222), (HLT,)])
_taken.run()
assert _taken.regs.read(2) == 0, "JZ with Z set must skip the instruction at address 8"
assert _taken.regs.read(3) == 222, f"execution should resume at address 10, got R3={_taken.regs.read(3)!r}"
_nottaken = CPU([(LDI, 0, 0, 3), (LDI, 1, 0, 1), (SUB, 0, 1, 0), (JZ, 0, 0, 10),
                 (LDI, 2, 0, 111), (LDI, 3, 0, 222), (HLT,)])
_nottaken.run()
assert _nottaken.regs.read(2) == 111, "with Z clear the JZ falls through"
_jnz = CPU([(LDI, 0, 0, 3), (LDI, 1, 0, 1), (SUB, 0, 1, 0), (JNZ, 0, 0, 10),
            (LDI, 2, 0, 111), (LDI, 3, 0, 222), (HLT,)])
_jnz.run()
assert _jnz.regs.read(2) == 0 and _jnz.regs.read(3) == 222, "JNZ branches when Z is clear"
_jmp = CPU([(JMP, 0, 0, 4), (LDI, 2, 0, 111), (LDI, 3, 0, 222), (HLT,)])
_jmp.run()
assert _jmp.regs.read(2) == 0 and _jmp.regs.read(3) == 222, "JMP is unconditional"
'''},
            {"name": "SUM_PROGRAM computes the triangular numbers", "code": r'''
from datapath import CPU, SUM_PROGRAM
for _n in (0, 1, 2, 5, 10, 22):
    _cpu = CPU(SUM_PROGRAM)
    _cpu.mem[0x40] = _n
    _cpu.run()
    _want = _n * (_n + 1) // 2
    _got = _cpu.mem[0x41]
    assert _got == _want, f"n={_n} left {_got!r} at 0x41, expected {_want}"
'''},
            {"name": "SUM_PROGRAM halts and does not scribble on itself", "code": r'''
from datapath import CPU, SUM_PROGRAM, assemble
_code = assemble(SUM_PROGRAM)
_cpu = CPU(SUM_PROGRAM)
_cpu.mem[0x40] = 6
_steps = _cpu.run()
assert _cpu.state == "HALTED", f"the program must end in HALTED, got {_cpu.state!r}"
assert _steps < 100, f"summing to 6 took {_steps} instructions — the loop should be tight"
assert _cpu.mem[:len(_code)] == _code, "the program must not overwrite its own instructions"
'''},
            {"name": "run() refuses to hang", "code": r'''
from datapath import CPU, JMP, NOP
_cpu = CPU([(JMP, 0, 0, 0)])
try:
    _cpu.run(max_steps=50)
    assert False, "an endless loop should raise RuntimeError, not spin forever"
except RuntimeError:
    pass
_cpu = CPU([(NOP,)])
try:
    _cpu.run(max_steps=200)
    assert False, "a program with no HLT should also raise RuntimeError"
except RuntimeError:
    pass
'''},
            {"name": "datapath.py is import-clean", "code": r'''
_src = open("datapath.py").read()
assert "print(" not in _src, "datapath.py is the hardware; the printing belongs in main.py"
assert "import " not in _src, "no imports are needed — the standard library is not required here"
'''},
        ],
    },
}
