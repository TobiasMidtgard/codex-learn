"""CE201 — Computer Organization & Architecture. Author module."""

COURSE = {
    "id": "CE201",
    "title": "Computer Organization & Architecture",
    "year": 2,
    "level": "Intermediate",
    "prereqs": ["CE101", "CS101"],
    "stack": ["C (reference)", "Python"],
    "credits": 10,
    "hours": 130,
    "icon": "⚙",
    "summary": (
        "How a machine turns a bit pattern into work. You encode numbers the way "
        "hardware does, write an assembler that emits real instruction words, build "
        "a single-cycle processor that executes them, and then measure why the same "
        "program runs at wildly different speeds depending on how it touches memory. "
        "Every model here is small enough to hold in your head and complete enough to "
        "run a program end to end."
    ),
    "outcomes": [
        "Encode and decode two's-complement integers at an arbitrary bit width, and detect signed overflow",
        "Pack and unpack IEEE-754 single-precision values by hand, including zero, subnormal and infinite cases",
        "Specify an instruction encoding and implement a two-pass assembler with label resolution",
        "Implement a fetch-decode-execute loop over a register file and word-addressed memory",
        "Quantify cache behaviour for a given access trace under direct-mapped and set-associative organisations",
        "Explain how pipelining changes throughput, and identify the data hazards that stall it",
        "Reason about CPI as the product of a program, an ISA and a microarchitecture",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Patterson & Hennessy, *Computer Organization and Design: The Hardware/Software Interface*, RISC-V ed. — chapters 2-5",
        "Hennessy & Patterson, *Computer Architecture: A Quantitative Approach*, 6th ed. — appendix B, memory hierarchy",
        "Goldberg, 'What Every Computer Scientist Should Know About Floating-Point Arithmetic', *ACM Computing Surveys* 23(1), 1991",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Data representation",
            "summary": "What a bit pattern means is a convention, and you implement the convention.",
            "concepts": [
                "Positional notation in base 2 and 16; a byte is a viewpoint, not a type",
                "Two's complement: one representation of zero, and an asymmetric range −2^(w−1) … 2^(w−1)−1",
                "Sign extension, truncation, and why C's integer promotions bite",
                "Signed overflow is a carry into, but not out of, the sign bit",
                "IEEE-754 binary32: 1 sign bit, 8 biased exponent bits, 23 stored fraction bits",
                "The implicit leading 1, and how exponent 0 switches it off to give subnormals",
                "Round-to-nearest-even, and why 0.1 is not 0.1",
            ],
            "lab": {
                "title": "Bit patterns: two's complement and binary32",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
No `struct`, no `int.to_bytes` shortcuts for the floating-point half — the point
is to do the arithmetic that the hardware does.

## Two's complement

**`to_twos(value, width)`** — the unsigned integer whose `width`-bit pattern
represents `value`. **`from_twos(bits, width)`** is the inverse.

```text
to_twos(-1, 8)    -> 255          from_twos(255, 8)  -> -1
to_twos(-128, 8)  -> 128          from_twos(128, 8)  -> -128
to_twos(127, 8)   -> 127          from_twos(1, 1)    -> -1
```

Both raise `ValueError` for `width < 1`, for a `value` outside
`-2**(width-1) .. 2**(width-1)-1`, and for `bits` outside `0 .. 2**width - 1`.

**`add_twos(a, b, width)`** — returns `(result, overflowed)`. The result is the
truncated `width`-bit sum read back as a signed number; `overflowed` is `True`
exactly when two operands of the same sign produce a result of the other sign.

```text
add_twos(127, 1, 8)    -> (-128, True)
add_twos(-128, -1, 8)  -> (127, True)
add_twos(-1, 1, 8)     -> (0, False)
```

## IEEE-754 binary32

```text
 31 30      23 22                    0
 +--+---------+-----------------------+
 |s | exponent|        fraction       |
 +--+---------+-----------------------+
```

Exponent field `e` in `1..254` means `(-1)**s * 1.fraction * 2**(e-127)`.
`e == 0` means `(-1)**s * 0.fraction * 2**-126`, which is zero when the fraction
is zero and a subnormal otherwise. `e == 255` means infinity (fraction 0) or NaN.

**`float_to_bits(x)`** returns the 32-bit pattern as an `int`;
**`bits_to_float(bits)`** returns the `float`. Use `math.frexp` and `math.ldexp`
to scale by powers of two exactly, and the supplied `round_half_even` for the
rounding step. Any NaN may encode as `0x7FC00000`; overflow becomes infinity.

```text
float_to_bits(1.0)       -> 0x3F800000
float_to_bits(-0.0)      -> 0x80000000
float_to_bits(0.1)       -> 0x3DCCCCCD
bits_to_float(0x00000001) -> 2**-149
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def round_half_even(value):
    """Given. Round a non-negative float to an int, ties to the even neighbour."""
    low = math.floor(value)
    rest = value - low
    if rest > 0.5:
        return low + 1
    if rest < 0.5:
        return low
    return low if low % 2 == 0 else low + 1


def to_twos(value, width):
    """Unsigned width-bit pattern for the signed value. ValueError when it will not fit."""
    # your code here


def from_twos(bits, width):
    """Signed value of a width-bit pattern. ValueError when bits is not a width-bit pattern."""
    # your code here


def add_twos(a, b, width):
    """(truncated signed sum, signed-overflow flag)."""
    # your code here


def float_to_bits(x):
    """The IEEE-754 binary32 bit pattern of x, as a 32-bit int."""
    # your code here


def bits_to_float(bits):
    """The float a 32-bit binary32 pattern denotes."""
    # your code here


print(to_twos(-1, 8), from_twos(255, 8))
print(add_twos(127, 1, 8))
print(hex(float_to_bits(0.1)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def round_half_even(value):
    """Given. Round a non-negative float to an int, ties to the even neighbour."""
    low = math.floor(value)
    rest = value - low
    if rest > 0.5:
        return low + 1
    if rest < 0.5:
        return low
    return low if low % 2 == 0 else low + 1


def to_twos(value, width):
    """Unsigned width-bit pattern for the signed value. ValueError when it will not fit."""
    if width < 1:
        raise ValueError("width must be at least 1 bit")
    low = -(1 << (width - 1))
    high = (1 << (width - 1)) - 1
    if not low <= value <= high:
        raise ValueError(f"{value} does not fit in {width} signed bits")
    return value & ((1 << width) - 1)


def from_twos(bits, width):
    """Signed value of a width-bit pattern. ValueError when bits is not a width-bit pattern."""
    if width < 1:
        raise ValueError("width must be at least 1 bit")
    if not 0 <= bits < (1 << width):
        raise ValueError(f"{bits} is not a {width}-bit pattern")
    if bits >> (width - 1):
        return bits - (1 << width)
    return bits


def add_twos(a, b, width):
    """(truncated signed sum, signed-overflow flag)."""
    mask = (1 << width) - 1
    raw = (to_twos(a, width) + to_twos(b, width)) & mask
    result = from_twos(raw, width)
    same_sign = (a < 0) == (b < 0)
    overflow = same_sign and (result < 0) != (a < 0)
    return (result, overflow)


def float_to_bits(x):
    """The IEEE-754 binary32 bit pattern of x, as a 32-bit int."""
    x = float(x)
    if x != x:
        return 0x7FC00000
    sign = 1 if math.copysign(1.0, x) < 0 else 0
    x = abs(x)
    if math.isinf(x):
        return (sign << 31) | 0x7F800000
    if x == 0.0:
        return sign << 31
    _, raw_exp = math.frexp(x)
    exponent = raw_exp - 1
    if exponent < -126:
        fraction = round_half_even(math.ldexp(x, 149))
        return (sign << 31) | fraction
    fraction = round_half_even(math.ldexp(x, 23 - exponent))
    if fraction == (1 << 24):
        fraction >>= 1
        exponent += 1
    if exponent > 127:
        return (sign << 31) | 0x7F800000
    return (sign << 31) | ((exponent + 127) << 23) | (fraction - (1 << 23))


def bits_to_float(bits):
    """The float a 32-bit binary32 pattern denotes."""
    if not 0 <= bits < (1 << 32):
        raise ValueError(f"{bits} is not a 32-bit pattern")
    sign = -1.0 if (bits >> 31) & 1 else 1.0
    exponent = (bits >> 23) & 0xFF
    fraction = bits & 0x7FFFFF
    if exponent == 0xFF:
        return sign * math.inf if fraction == 0 else math.nan
    if exponent == 0:
        return sign * math.ldexp(fraction, -149)
    return sign * math.ldexp(fraction + (1 << 23), exponent - 150)


print(to_twos(-1, 8), from_twos(255, 8))
print(add_twos(127, 1, 8))
print(hex(float_to_bits(0.1)))
'''}],
                "hints": [
                    "`value & ((1 << width) - 1)` already gives the two's-complement pattern for a negative int — Python's `&` behaves as if the number had infinitely many leading sign bits.",
                    "A pattern is negative exactly when its top bit is set: `if bits >> (width - 1): return bits - (1 << width)`.",
                    "`math.frexp(x)` gives `(m, e)` with `x == m * 2**e` and `0.5 <= m < 1`, so the unbiased exponent of the `1.f` form is `e - 1`.",
                    "`math.ldexp(x, 23 - exponent)` lands the 24 significand bits in the integer part exactly; round it, and if it becomes `1 << 24` shift right and bump the exponent.",
                ],
                "tests": [
                    {"name": "to_twos and from_twos round-trip", "code": r'''
for _v, _w, _want in [(-1, 8, 255), (-128, 8, 128), (127, 8, 127), (0, 8, 0),
                      (-1, 1, 1), (0, 1, 0), (-1, 32, 4294967295), (-32768, 16, 32768)]:
    _got = to_twos(_v, _w)
    assert _got == _want, f"to_twos({_v}, {_w}) gave {_got!r}, expected {_want}"
    _back = from_twos(_want, _w)
    assert _back == _v, f"from_twos({_want}, {_w}) gave {_back!r}, expected {_v}"
'''},
                    {"name": "Range and width are enforced", "code": r'''
for _v, _w in [(128, 8), (-129, 8), (1, 1), (-2, 1), (0, 0), (5, -3)]:
    try:
        to_twos(_v, _w)
        assert False, f"to_twos({_v}, {_w}) should raise ValueError"
    except ValueError:
        pass
for _b, _w in [(256, 8), (-1, 8), (2, 1), (0, 0)]:
    try:
        from_twos(_b, _w)
        assert False, f"from_twos({_b}, {_w}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "add_twos truncates and flags overflow", "code": r'''
for _a, _b, _w, _want in [(127, 1, 8, (-128, True)), (-128, -1, 8, (127, True)),
                          (-1, 1, 8, (0, False)), (100, 27, 8, (127, False)),
                          (-100, -28, 8, (128 - 256, False)), (64, 64, 8, (-128, True)),
                          (-1, -1, 1, (0, True)), (0, 0, 4, (0, False))]:
    _got = add_twos(_a, _b, _w)
    assert tuple(_got) == _want, f"add_twos({_a}, {_b}, {_w}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "Known binary32 encodings", "code": r'''
for _x, _want in [(1.0, 0x3F800000), (-1.0, 0xBF800000), (2.0, 0x40000000),
                  (0.15625, 0x3E200000), (0.0, 0x00000000), (-0.0, 0x80000000),
                  (0.1, 0x3DCCCCCD), (float("inf"), 0x7F800000),
                  (float("-inf"), 0xFF800000), (3.5e38, 0x7F800000)]:
    _got = float_to_bits(_x)
    assert _got == _want, f"float_to_bits({_x!r}) gave 0x{_got:08X}, expected 0x{_want:08X}"
_nan = float_to_bits(float("nan"))
assert (_nan >> 23) & 0xFF == 0xFF and (_nan & 0x7FFFFF) != 0, \
    f"NaN encoded as 0x{_nan:08X}: exponent must be all ones with a non-zero fraction"
'''},
                    {"name": "float_to_bits agrees with the C encoder", "code": r'''
import struct as _struct
for _x in [0.0, -0.0, 1.0, -1.0, 0.5, 0.1, 2.5, 7.0, 1e-5, 1234.5678,
           3.4e38, 1.5e-40, 5.877472e-39, 2.0 ** -149, 6.1e-5, -98765.4321]:
    _want = _struct.unpack(">I", _struct.pack(">f", _x))[0]
    _got = float_to_bits(_x)
    assert _got == _want, f"float_to_bits({_x!r}) gave 0x{_got:08X}, expected 0x{_want:08X}"
'''},
                    {"name": "Ties round to the even significand", "code": r'''
_a = bits_to_float(0x3F800000)
_b = bits_to_float(0x3F800001)
_c = bits_to_float(0x3F800002)
_got = float_to_bits((_a + _b) / 2)
assert _got == 0x3F800000, f"halfway below 0x3F800001 gave 0x{_got:08X}, expected 0x3F800000"
_got = float_to_bits((_b + _c) / 2)
assert _got == 0x3F800002, f"halfway above 0x3F800001 gave 0x{_got:08X}, expected 0x3F800002"
'''},
                    {"name": "bits_to_float decodes every class", "code": r'''
import math as _math
import struct as _struct
for _b in [0x00000000, 0x80000000, 0x3F800000, 0xBF800000, 0x3DCCCCCD,
           0x00000001, 0x007FFFFF, 0x00800000, 0x7F7FFFFF, 0x3E200000]:
    _want = _struct.unpack(">f", _struct.pack(">I", _b))[0]
    _got = bits_to_float(_b)
    assert _got == _want, f"bits_to_float(0x{_b:08X}) gave {_got!r}, expected {_want!r}"
assert bits_to_float(0x00000001) == _math.ldexp(1, -149), "0x00000001 is the smallest subnormal"
assert bits_to_float(0x7F800000) == _math.inf, "exponent 255 with fraction 0 is infinity"
assert _math.isnan(bits_to_float(0x7FC00000)), "exponent 255 with a fraction is NaN"
try:
    bits_to_float(1 << 32)
    assert False, "bits_to_float(1 << 32) should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Instruction sets and assembly",
            "summary": "An ISA is a contract; an assembler is the first program that honours it.",
            "concepts": [
                "The ISA as the interface between the compiler writer and the hardware designer",
                "Fixed-width encoding: opcode, register fields, immediate field, and the bits left over",
                "Register-register, register-immediate and control-transfer instruction formats",
                "Word addressing versus byte addressing, and what an offset means in each",
                "Forward references force a two-pass assembler: collect labels, then emit",
                "Pseudo-instructions, and the hardwired zero register that makes them cheap",
                "Assembly-time errors are cheaper than run-time ones: range-check every immediate",
            ],
            "lab": {
                "title": "A two-pass assembler for CW-32",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
CW-32 is a 32-bit, word-addressed, 32-register load/store machine. `r0` always
reads as zero. Every instruction is one 32-bit word:

```text
 31    26 25   21 20   16 15   11 10        0
 +-------+-------+-------+-------+-----------+
 | opcode|  f1   |  f2   |  f3   |  (unused) |     register form
 +-------+-------+-------+-------+-----------+
 | opcode|  f1   |  f2   |     immediate     |     immediate form
 +-------+-------+-------+-------------------+
```

| syntax | fields |
| --- | --- |
| `ADD/SUB/AND/OR/XOR/SLT rd, rs, rt` | f1=rd, f2=rs, f3=rt |
| `ADDI rd, rs, imm` | f1=rd, f2=rs, imm |
| `LW rd, off(rs)` | f1=rd, f2=rs, imm=off |
| `SW rt, off(rs)` | f1=rt, f2=rs, imm=off |
| `BEQ/BNE rs, rt, target` | f1=rs, f2=rt, imm=target |
| `JMP target` | imm=target |
| `NOP` / `HALT` | nothing |

Branch and jump targets are **absolute word addresses**, written as a label or a
number. Immediates occupy 16 bits and are stored as `imm & 0xFFFF`.

Write four functions. Every failure raises `AsmError` — never a bare `ValueError`
and never a silent wrong word.

- **`strip_comment(line)`** — drop everything from the first `#` or `;`, then strip.
- **`parse_register(token)`** — `"r7"`, `"R7"` → `7`. `"x1"`, `"r32"`, `"r"` → `AsmError`.
- **`parse_mem(token)`** — `"4(r2)"` → `(4, 2)`; `"-8(r30)"` → `(-8, 30)`.
  Anything not of that shape raises `AsmError`.
- **`first_pass(lines)`** — returns `(labels, items)`. `labels` maps each label to
  the word address of the next instruction; `items` is a list of
  `(address, tokens)` with the mnemonic uppercased and commas already gone.
  A line may carry a label, an instruction, both, or neither. A repeated label is
  an `AsmError`.
- **`assemble(text)`** — the whole thing: a list of 32-bit ints.

```text
assemble("top: ADDI r1, r0, 5\nJMP top\n")  ->  [0x1C200005, 0x30000000]
```

Reject an unknown mnemonic, an unknown label, the wrong number of operands, and
an immediate outside `-32768 .. 65535`.
''',
                "files": [{"name": "main.py", "content": r'''
OPCODES = {
    "NOP": 0, "ADD": 1, "SUB": 2, "AND": 3, "OR": 4, "XOR": 5, "SLT": 6,
    "ADDI": 7, "LW": 8, "SW": 9, "BEQ": 10, "BNE": 11, "JMP": 12, "HALT": 13,
}
R_TYPE = {"ADD", "SUB", "AND", "OR", "XOR", "SLT"}


class AsmError(Exception):
    """Raised when a source line cannot be assembled."""


SOURCE = r"""
        ADDI r1, r0, 0        ; total
        ADDI r2, r0, 1        ; i
        ADDI r3, r0, 11       ; limit
loop:   BEQ  r2, r3, done
        ADD  r1, r1, r2
        ADDI r2, r2, 1
        JMP  loop
done:   SW   r1, 0(r0)
        HALT
"""


def strip_comment(line):
    """The line with any # or ; comment removed, stripped of surrounding space."""
    # your code here


def parse_register(token):
    """'r7' -> 7. AsmError for anything that is not r0..r31."""
    # your code here


def parse_mem(token):
    """'4(r2)' -> (4, 2). AsmError for anything else."""
    # your code here


def first_pass(lines):
    """(labels, items) where items is a list of (word address, token list)."""
    # your code here


def assemble(text):
    """The whole source as a list of 32-bit instruction words."""
    # your code here


for _address, _word in enumerate(assemble(SOURCE) or []):
    print(f"{_address:04d}  0x{_word:08X}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
OPCODES = {
    "NOP": 0, "ADD": 1, "SUB": 2, "AND": 3, "OR": 4, "XOR": 5, "SLT": 6,
    "ADDI": 7, "LW": 8, "SW": 9, "BEQ": 10, "BNE": 11, "JMP": 12, "HALT": 13,
}
R_TYPE = {"ADD", "SUB", "AND", "OR", "XOR", "SLT"}


class AsmError(Exception):
    """Raised when a source line cannot be assembled."""


SOURCE = r"""
        ADDI r1, r0, 0        ; total
        ADDI r2, r0, 1        ; i
        ADDI r3, r0, 11       ; limit
loop:   BEQ  r2, r3, done
        ADD  r1, r1, r2
        ADDI r2, r2, 1
        JMP  loop
done:   SW   r1, 0(r0)
        HALT
"""


def strip_comment(line):
    """The line with any # or ; comment removed, stripped of surrounding space."""
    for marker in ("#", ";"):
        cut = line.find(marker)
        if cut != -1:
            line = line[:cut]
    return line.strip()


def parse_register(token):
    """'r7' -> 7. AsmError for anything that is not r0..r31."""
    text = token.strip().lower()
    if not text.startswith("r") or not text[1:].isdigit():
        raise AsmError(f"expected a register, got {token!r}")
    number = int(text[1:])
    if not 0 <= number <= 31:
        raise AsmError(f"register out of range: {token!r}")
    return number


def parse_mem(token):
    """'4(r2)' -> (4, 2). AsmError for anything else."""
    text = token.strip()
    if not text.endswith(")") or "(" not in text:
        raise AsmError(f"expected offset(register), got {token!r}")
    offset_text, _, register_text = text[:-1].partition("(")
    offset_text = offset_text.strip()
    if not offset_text:
        raise AsmError(f"expected offset(register), got {token!r}")
    try:
        offset = int(offset_text, 0)
    except ValueError:
        raise AsmError(f"bad offset in {token!r}")
    return offset, parse_register(register_text)


def first_pass(lines):
    """(labels, items) where items is a list of (word address, token list)."""
    labels = {}
    items = []
    address = 0
    for raw in lines:
        text = strip_comment(raw)
        while text and ":" in text:
            head, _, rest = text.partition(":")
            name = head.strip()
            if not name or " " in name:
                raise AsmError(f"bad label {head!r}")
            if name in labels:
                raise AsmError(f"duplicate label {name!r}")
            labels[name] = address
            text = rest.strip()
        if not text:
            continue
        tokens = text.replace(",", " ").split()
        tokens[0] = tokens[0].upper()
        items.append((address, tokens))
        address += 1
    return labels, items


def fit_immediate(value):
    """The 16-bit field for an immediate. AsmError when it will not fit."""
    if not -32768 <= value <= 65535:
        raise AsmError(f"immediate {value} does not fit in 16 bits")
    return value & 0xFFFF


def resolve(token, labels):
    """A label or a literal number, as a word address."""
    if token in labels:
        return labels[token]
    try:
        return int(token, 0)
    except ValueError:
        raise AsmError(f"unknown label {token!r}")


def assemble(text):
    """The whole source as a list of 32-bit instruction words."""
    labels, items = first_pass(text.split("\n"))
    words = []
    for _address, tokens in items:
        op = tokens[0]
        args = tokens[1:]
        if op not in OPCODES:
            raise AsmError(f"unknown mnemonic {op!r}")
        code = OPCODES[op]
        if op in R_TYPE:
            if len(args) != 3:
                raise AsmError(f"{op} takes rd, rs, rt")
            rd, rs, rt = [parse_register(a) for a in args]
            word = (code << 26) | (rd << 21) | (rs << 16) | (rt << 11)
        elif op == "ADDI":
            if len(args) != 3:
                raise AsmError("ADDI takes rd, rs, imm")
            rd = parse_register(args[0])
            rs = parse_register(args[1])
            word = (code << 26) | (rd << 21) | (rs << 16) | fit_immediate(resolve(args[2], labels))
        elif op in ("LW", "SW"):
            if len(args) != 2:
                raise AsmError(f"{op} takes a register and offset(base)")
            reg = parse_register(args[0])
            offset, base = parse_mem(args[1])
            word = (code << 26) | (reg << 21) | (base << 16) | fit_immediate(offset)
        elif op in ("BEQ", "BNE"):
            if len(args) != 3:
                raise AsmError(f"{op} takes rs, rt, target")
            rs = parse_register(args[0])
            rt = parse_register(args[1])
            word = (code << 26) | (rs << 21) | (rt << 16) | fit_immediate(resolve(args[2], labels))
        elif op == "JMP":
            if len(args) != 1:
                raise AsmError("JMP takes a target")
            word = (code << 26) | fit_immediate(resolve(args[0], labels))
        else:
            if args:
                raise AsmError(f"{op} takes no operands")
            word = code << 26
        words.append(word)
    return words


for _address, _word in enumerate(assemble(SOURCE) or []):
    print(f"{_address:04d}  0x{_word:08X}")
'''}],
                "hints": [
                    "`line.find('#')` returns -1 when the marker is absent, so slice only when it is not -1.",
                    "In `first_pass`, peel labels off the front in a loop — `head, _, rest = text.partition(':')` — and only count an address when something is left to assemble.",
                    "The second pass never needs to know where it is: every target is absolute, so `labels[token]` is the answer directly.",
                    "Build each word by OR-ing shifted fields: `(code << 26) | (rd << 21) | (rs << 16) | (rt << 11)`. Mask immediates with `& 0xFFFF` *after* range-checking them.",
                ],
                "tests": [
                    {"name": "Tokenising: comments, registers, offsets", "code": r'''
assert strip_comment("  ADD r1, r2, r3  ; sum") == "ADD r1, r2, r3", \
    f"strip_comment gave {strip_comment('  ADD r1, r2, r3  ; sum')!r}"
assert strip_comment("# all comment") == "", "A comment-only line strips to nothing"
assert parse_register("r7") == 7 and parse_register("R31") == 31, "r0..r31, either case"
assert parse_mem("4(r2)") == (4, 2), f"parse_mem('4(r2)') gave {parse_mem('4(r2)')!r}"
assert parse_mem("-8(r30)") == (-8, 30), f"parse_mem('-8(r30)') gave {parse_mem('-8(r30)')!r}"
'''},
                    {"name": "Bad registers and bad memory operands raise AsmError", "code": r'''
for _bad in ["x1", "r32", "r", "1", "rr1", ""]:
    try:
        parse_register(_bad)
        assert False, f"parse_register({_bad!r}) should raise AsmError"
    except AsmError:
        pass
for _bad in ["r2", "(r2)", "4r2", "4(r2", "x(r2)"]:
    try:
        parse_mem(_bad)
        assert False, f"parse_mem({_bad!r}) should raise AsmError"
    except AsmError:
        pass
'''},
                    {"name": "first_pass places labels at the next instruction", "code": r'''
_labels, _items = first_pass(["; header", "start: ADDI r1, r0, 5", "", "  ADD r2, r1, r1",
                              "end:", "  HALT"])
assert _labels == {"start": 0, "end": 2}, f"labels came out as {_labels!r}"
assert [a for a, _t in _items] == [0, 1, 2], f"addresses came out as {[a for a, _t in _items]!r}"
assert _items[0][1] == ["ADDI", "r1", "r0", "5"], f"tokens came out as {_items[0][1]!r}"
try:
    first_pass(["a: NOP", "a: NOP"])
    assert False, "a duplicate label should raise AsmError"
except AsmError:
    pass
'''},
                    {"name": "Encoding matches the field layout", "code": r'''
_words = assemble("start: ADDI r1, r0, 5\nADD r2, r1, r1\nJMP start\nHALT\n")
assert len(_words) == 4, f"expected 4 words, got {len(_words)}"
_want = [(OPCODES["ADDI"] << 26) | (1 << 21) | (0 << 16) | 5,
         (OPCODES["ADD"] << 26) | (2 << 21) | (1 << 16) | (1 << 11),
         (OPCODES["JMP"] << 26) | 0,
         (OPCODES["HALT"] << 26)]
assert _words == _want, f"assembled {[hex(w) for w in _words]}, expected {[hex(w) for w in _want]}"
assert _words[0] == 0x1C200005, f"word 0 is 0x{_words[0]:08X}, expected 0x1C200005"
'''},
                    {"name": "Loads, stores, branches and negative immediates", "code": r'''
_words = assemble("LW r4, 8(r5)\nSW r4, -1(r5)\nBNE r4, r0, 0\nADDI r6, r6, -1\n")
assert _words[0] == (OPCODES["LW"] << 26) | (4 << 21) | (5 << 16) | 8, \
    f"LW encoded as 0x{_words[0]:08X}"
assert _words[1] == (OPCODES["SW"] << 26) | (4 << 21) | (5 << 16) | 0xFFFF, \
    f"SW with offset -1 encoded as 0x{_words[1]:08X}"
assert _words[2] == (OPCODES["BNE"] << 26) | (4 << 21) | (0 << 16) | 0, \
    f"BNE encoded as 0x{_words[2]:08X}"
assert _words[3] & 0xFFFF == 0xFFFF, "an immediate of -1 occupies the field as 0xFFFF"
'''},
                    {"name": "The worked example assembles to nine words", "code": r'''
_program = assemble(SOURCE)
assert len(_program) == 9, f"the sample program is 9 instructions, got {len(_program)}"
assert _program[3] == (OPCODES["BEQ"] << 26) | (2 << 21) | (3 << 16) | 7, \
    f"BEQ r2, r3, done should target word 7, got 0x{_program[3]:08X}"
assert _program[6] == (OPCODES["JMP"] << 26) | 3, \
    f"JMP loop should target word 3, got 0x{_program[6]:08X}"
assert _program[8] == (OPCODES["HALT"] << 26), "the last word is HALT"
assert "0x1C200000" in _out, "the demo should print each word as 0x-prefixed hex"
'''},
                    {"name": "Bad programs are refused", "code": r'''
for _bad in ["FROB r1, r2, r3\n", "JMP nowhere\n", "ADD r1, r2\n", "HALT r1\n",
             "ADDI r1, r0, 70000\n", "ADDI r1, r0, -40000\n", "LW r1, r2\n"]:
    try:
        assemble(_bad)
        assert False, f"assemble({_bad!r}) should raise AsmError"
    except AsmError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Datapath and control",
            "summary": "Fetch, decode, execute — the loop that gives the instruction words meaning.",
            "concepts": [
                "The five classical steps: fetch, decode, execute, memory, write-back",
                "A register file as a small addressed array; the hardwired zero register",
                "Sign extension of the immediate happens in decode, not in the ALU",
                "Control signals are a function of the opcode alone in a single-cycle design",
                "The program counter is state: a branch is just a different next-PC",
                "Single-cycle timing is set by the slowest instruction, which is why CPI 1 is not fast",
                "Trapping bad opcodes and bad addresses rather than executing nonsense",
            ],
            "lab": {
                "title": "A single-cycle CW-32 simulator",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
The assembler from the last lab produced words. Now execute them.

**`to_signed32(value)`** — reduce an arbitrary Python int to the signed 32-bit
value the hardware would hold. `to_signed32(0xFFFFFFFF) == -1`.

**`decode(word)`** — a dict `{"op", "f1", "f2", "f3", "imm"}`. `f1`, `f2`, `f3`
are the 5-bit register fields at bits 25, 20 and 15; `imm` is bits 15..0
**sign-extended** to a Python int. A word whose opcode is not in the table, or a
value outside `0 .. 2**32 - 1`, raises `ValueError`.

**`CPU(program, mem_words=64)`** holds `regs` (32 ints), `mem` (`mem_words` ints),
`pc`, `steps` and `halted`.

- `write(index, value)` — store `to_signed32(value)`, except into `r0`, which
  stays 0 whatever is written to it.
- `load(address)` / `store(address, value)` — word-addressed; an address outside
  `0 .. mem_words - 1` raises `IndexError`.
- `step()` — execute the instruction at `pc`, advance `pc`, add one to `steps`,
  and return the decoded dict. Calling it on a halted machine raises
  `RuntimeError`; a `pc` outside the program raises `IndexError`.
- `run(max_steps=10000)` — step until `halted`, then return `steps`. If the
  machine is still going after `max_steps`, raise `RuntimeError` rather than
  freezing the tab.

Semantics: `SLT` writes 1 when `regs[f2] < regs[f3]` signed, else 0. `LW`/`SW`
address is `regs[f2] + imm`. `BEQ`/`BNE` compare `regs[f1]` with `regs[f2]` and,
when taken, set `pc` to `imm`. `JMP` sets `pc` to `imm`. `HALT` sets `halted`.

`PROGRAM` in the starter sums 1..10 and stores the answer at `mem[0]`.
Executed correctly it takes exactly **46 steps** and leaves `regs[1] == 55`.
''',
                "files": [{"name": "main.py", "content": r'''
OPCODES = {
    "NOP": 0, "ADD": 1, "SUB": 2, "AND": 3, "OR": 4, "XOR": 5, "SLT": 6,
    "ADDI": 7, "LW": 8, "SW": 9, "BEQ": 10, "BNE": 11, "JMP": 12, "HALT": 13,
}
NAMES = {code: name for name, code in OPCODES.items()}


def encode(op, f1=0, f2=0, f3=0, imm=None):
    """Given. Build one instruction word in the CW-32 layout."""
    word = (OPCODES[op] << 26) | (f1 << 21) | (f2 << 16)
    if imm is None:
        return word | (f3 << 11)
    return word | (imm & 0xFFFF)


PROGRAM = [
    encode("ADDI", 1, 0, imm=0),    # 0  r1 = 0             total
    encode("ADDI", 2, 0, imm=1),    # 1  r2 = 1             i
    encode("ADDI", 3, 0, imm=11),   # 2  r3 = 11            limit
    encode("BEQ", 2, 3, imm=7),     # 3  if r2 == r3 -> 7
    encode("ADD", 1, 1, 2),         # 4  r1 = r1 + r2
    encode("ADDI", 2, 2, imm=1),    # 5  r2 = r2 + 1
    encode("JMP", imm=3),           # 6  -> 3
    encode("SW", 1, 0, imm=0),      # 7  mem[0] = r1
    encode("HALT"),                 # 8
]


def to_signed32(value):
    """The signed 32-bit value of an arbitrary int."""
    # your code here


def decode(word):
    """{'op', 'f1', 'f2', 'f3', 'imm'} for one instruction word."""
    # your code here


class CPU:
    def __init__(self, program, mem_words=64):
        self.program = list(program)
        self.regs = [0] * 32
        self.mem = [0] * mem_words
        self.pc = 0
        self.steps = 0
        self.halted = False

    def write(self, index, value):
        """Write a register, except r0."""
        # your code here

    def load(self, address):
        """Read one data word. IndexError when the address is out of range."""
        # your code here

    def store(self, address, value):
        """Write one data word. IndexError when the address is out of range."""
        # your code here

    def step(self):
        """Execute one instruction and return its decoded form."""
        # your code here

    def run(self, max_steps=10000):
        """Step until halted; return the step count."""
        # your code here


machine = CPU(PROGRAM)
machine.run()
print("steps:", machine.steps, "r1:", machine.regs[1], "mem[0]:", machine.mem[0])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
OPCODES = {
    "NOP": 0, "ADD": 1, "SUB": 2, "AND": 3, "OR": 4, "XOR": 5, "SLT": 6,
    "ADDI": 7, "LW": 8, "SW": 9, "BEQ": 10, "BNE": 11, "JMP": 12, "HALT": 13,
}
NAMES = {code: name for name, code in OPCODES.items()}


def encode(op, f1=0, f2=0, f3=0, imm=None):
    """Given. Build one instruction word in the CW-32 layout."""
    word = (OPCODES[op] << 26) | (f1 << 21) | (f2 << 16)
    if imm is None:
        return word | (f3 << 11)
    return word | (imm & 0xFFFF)


PROGRAM = [
    encode("ADDI", 1, 0, imm=0),    # 0  r1 = 0             total
    encode("ADDI", 2, 0, imm=1),    # 1  r2 = 1             i
    encode("ADDI", 3, 0, imm=11),   # 2  r3 = 11            limit
    encode("BEQ", 2, 3, imm=7),     # 3  if r2 == r3 -> 7
    encode("ADD", 1, 1, 2),         # 4  r1 = r1 + r2
    encode("ADDI", 2, 2, imm=1),    # 5  r2 = r2 + 1
    encode("JMP", imm=3),           # 6  -> 3
    encode("SW", 1, 0, imm=0),      # 7  mem[0] = r1
    encode("HALT"),                 # 8
]


def to_signed32(value):
    """The signed 32-bit value of an arbitrary int."""
    value &= 0xFFFFFFFF
    return value - (1 << 32) if value >> 31 else value


def decode(word):
    """{'op', 'f1', 'f2', 'f3', 'imm'} for one instruction word."""
    if not 0 <= word < (1 << 32):
        raise ValueError(f"{word} is not a 32-bit instruction word")
    code = word >> 26
    if code not in NAMES:
        raise ValueError(f"unknown opcode {code}")
    immediate = word & 0xFFFF
    if immediate >= 0x8000:
        immediate -= 0x10000
    return {"op": NAMES[code], "f1": (word >> 21) & 31, "f2": (word >> 16) & 31,
            "f3": (word >> 11) & 31, "imm": immediate}


class CPU:
    """A single-cycle CW-32 machine: one instruction retired per step."""

    def __init__(self, program, mem_words=64):
        self.program = list(program)
        self.regs = [0] * 32
        self.mem = [0] * mem_words
        self.pc = 0
        self.steps = 0
        self.halted = False

    def write(self, index, value):
        """Write a register, except r0."""
        if index != 0:
            self.regs[index] = to_signed32(value)

    def load(self, address):
        """Read one data word. IndexError when the address is out of range."""
        if not 0 <= address < len(self.mem):
            raise IndexError(f"data address {address} is outside memory")
        return self.mem[address]

    def store(self, address, value):
        """Write one data word. IndexError when the address is out of range."""
        if not 0 <= address < len(self.mem):
            raise IndexError(f"data address {address} is outside memory")
        self.mem[address] = to_signed32(value)

    def step(self):
        """Execute one instruction and return its decoded form."""
        if self.halted:
            raise RuntimeError("the machine has already halted")
        if not 0 <= self.pc < len(self.program):
            raise IndexError(f"pc {self.pc} is outside the program")
        instruction = decode(self.program[self.pc])
        op = instruction["op"]
        f1, f2, f3 = instruction["f1"], instruction["f2"], instruction["f3"]
        immediate = instruction["imm"]
        regs = self.regs
        next_pc = self.pc + 1
        if op == "NOP":
            pass
        elif op == "ADD":
            self.write(f1, regs[f2] + regs[f3])
        elif op == "SUB":
            self.write(f1, regs[f2] - regs[f3])
        elif op == "AND":
            self.write(f1, regs[f2] & regs[f3])
        elif op == "OR":
            self.write(f1, regs[f2] | regs[f3])
        elif op == "XOR":
            self.write(f1, regs[f2] ^ regs[f3])
        elif op == "SLT":
            self.write(f1, 1 if regs[f2] < regs[f3] else 0)
        elif op == "ADDI":
            self.write(f1, regs[f2] + immediate)
        elif op == "LW":
            self.write(f1, self.load(regs[f2] + immediate))
        elif op == "SW":
            self.store(regs[f2] + immediate, regs[f1])
        elif op == "BEQ":
            if regs[f1] == regs[f2]:
                next_pc = immediate
        elif op == "BNE":
            if regs[f1] != regs[f2]:
                next_pc = immediate
        elif op == "JMP":
            next_pc = immediate
        elif op == "HALT":
            self.halted = True
        self.pc = next_pc
        self.steps += 1
        return instruction

    def run(self, max_steps=10000):
        """Step until halted; return the step count."""
        while not self.halted:
            if self.steps >= max_steps:
                raise RuntimeError(f"still running after {max_steps} steps")
            self.step()
        return self.steps


machine = CPU(PROGRAM)
machine.run()
print("steps:", machine.steps, "r1:", machine.regs[1], "mem[0]:", machine.mem[0])
'''}],
                "hints": [
                    "`to_signed32`: mask with `0xFFFFFFFF`, then subtract `1 << 32` when bit 31 is set.",
                    "Sign-extend the immediate once, in `decode` — `if imm >= 0x8000: imm -= 0x10000` — so `step` never has to think about it.",
                    "Compute `next_pc = self.pc + 1` before the big `if` chain and let branches overwrite it; assign `self.pc` once at the end.",
                    "`write` is the only place `r0` is protected, so route every register write through it, including `LW`.",
                ],
                "tests": [
                    {"name": "to_signed32 wraps at 32 bits", "code": r'''
for _v, _want in [(0, 0), (1, 1), (0xFFFFFFFF, -1), (1 << 31, -2147483648),
                  ((1 << 31) - 1, 2147483647), (-1, -1), (1 << 32, 0), (4294967294, -2)]:
    _got = to_signed32(_v)
    assert _got == _want, f"to_signed32({_v}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "decode splits the fields", "code": r'''
_d = decode(encode("ADD", 3, 1, 2))
assert _d["op"] == "ADD" and (_d["f1"], _d["f2"], _d["f3"]) == (3, 1, 2), f"got {_d!r}"
_d = decode(encode("ADDI", 5, 6, imm=-1))
assert _d["op"] == "ADDI" and _d["imm"] == -1, f"immediate -1 decoded as {_d['imm']!r}"
_d = decode(encode("ADDI", 5, 6, imm=32767))
assert _d["imm"] == 32767, f"immediate 32767 decoded as {_d['imm']!r}"
assert decode(0)["op"] == "NOP", "the all-zero word is NOP"
'''},
                    {"name": "decode rejects nonsense", "code": r'''
for _bad in [63 << 26, 40 << 26, 1 << 32, -1]:
    try:
        decode(_bad)
        assert False, f"decode({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The sample program sums 1..10", "code": r'''
_cpu = CPU(PROGRAM)
_steps = _cpu.run()
assert _cpu.halted, "the machine should halt"
assert _cpu.regs[1] == 55, f"r1 is {_cpu.regs[1]!r}, expected 55"
assert _cpu.regs[2] == 11, f"r2 is {_cpu.regs[2]!r}, expected 11 after the loop"
assert _cpu.mem[0] == 55, f"mem[0] is {_cpu.mem[0]!r}, expected 55"
assert _steps == 46 == _cpu.steps, f"the program takes 46 steps, run() reported {_steps!r}"
'''},
                    {"name": "ALU operations and the zero register", "code": r'''
_cpu = CPU([encode("ADDI", 1, 0, imm=-5), encode("ADDI", 2, 0, imm=3),
            encode("SUB", 3, 1, 2), encode("SLT", 4, 1, 2), encode("SLT", 5, 2, 1),
            encode("XOR", 6, 1, 2), encode("ADDI", 0, 0, imm=99), encode("HALT")])
_cpu.run()
assert _cpu.regs[3] == -8, f"-5 - 3 gave {_cpu.regs[3]!r}, expected -8"
assert _cpu.regs[4] == 1, f"SLT with -5 < 3 gave {_cpu.regs[4]!r}, expected 1"
assert _cpu.regs[5] == 0, f"SLT with 3 < -5 gave {_cpu.regs[5]!r}, expected 0"
assert _cpu.regs[6] == (-5) ^ 3, f"XOR gave {_cpu.regs[6]!r}, expected {(-5) ^ 3}"
assert _cpu.regs[0] == 0, "r0 must stay 0 however hard you write to it"
'''},
                    {"name": "Loads and stores go through memory", "code": r'''
_cpu = CPU([encode("ADDI", 1, 0, imm=42), encode("SW", 1, 0, imm=5),
            encode("LW", 2, 0, imm=5), encode("ADD", 3, 2, 2), encode("HALT")], mem_words=8)
_cpu.run()
assert _cpu.mem[5] == 42, f"mem[5] is {_cpu.mem[5]!r}, expected 42"
assert _cpu.regs[2] == 42, f"r2 is {_cpu.regs[2]!r}, expected the loaded 42"
assert _cpu.regs[3] == 84, f"r3 is {_cpu.regs[3]!r}, expected 84"
try:
    CPU([encode("SW", 0, 0, imm=100), encode("HALT")], mem_words=8).run()
    assert False, "storing outside memory should raise IndexError"
except IndexError:
    pass
'''},
                    {"name": "Halting, stepping past halt, and runaway programs", "code": r'''
_cpu = CPU([encode("HALT")])
_cpu.step()
assert _cpu.halted and _cpu.steps == 1, f"after HALT: halted={_cpu.halted!r} steps={_cpu.steps!r}"
try:
    _cpu.step()
    assert False, "stepping a halted machine should raise RuntimeError"
except RuntimeError:
    pass
try:
    CPU([encode("JMP", imm=0)]).run(max_steps=50)
    assert False, "a program that never halts should raise RuntimeError"
except RuntimeError:
    pass
try:
    CPU([encode("JMP", imm=99), encode("HALT")]).run(max_steps=50)
    assert False, "jumping outside the program should raise IndexError"
except IndexError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Memory hierarchy",
            "summary": "The processor is fast; DRAM is not. Everything else follows from that.",
            "concepts": [
                "The memory wall, and why locality is an architectural assumption",
                "Temporal and spatial locality, and the traversal orders that destroy each",
                "Splitting an address into tag, index and block offset",
                "Direct-mapped, N-way set associative and fully associative as one parameterised design",
                "The three C's: compulsory, capacity and conflict misses",
                "LRU replacement, its cost in hardware, and why real caches approximate it",
                "Average memory access time = hit time + miss rate x miss penalty",
            ],
            "lab": {
                "title": "A cache simulator over an access trace",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Addresses here are **word** addresses. A cache is described by three numbers:
`sets`, `ways` and `block_words`.

```text
address =  [ tag | index | offset ]
                          <- log2(block_words) bits
                  <- log2(sets) bits
```

**`Cache(sets, ways, block_words)`** — `sets` and `block_words` must be powers of
two and `ways` at least 1, or `ValueError`. It exposes counters `hits`, `misses`
and `evictions`.

- `fields(address)` — `(tag, index, offset)`. A negative address raises `ValueError`.
- `access(address)` — returns `"hit"` or `"miss"`, updating the counters. On a
  miss into a full set, evict the **least recently used** block and count one
  eviction. A hit refreshes recency.
- `hit_rate()` — hits over accesses, or `0.0` before any access.
- `stats()` — `{"accesses", "hits", "misses", "evictions", "hit_rate"}`.

**`run_trace(cache, trace)`** — replay every address, then return `cache.stats()`.

**`matrix_trace(rows, cols, order)`** — the word addresses touched by walking a
row-major `rows x cols` matrix in `"row"` order (`0, 1, 2, …`) or `"col"` order
(`0, cols, 2*cols, …`). Any other order raises `ValueError`.

The pay-off: an 8-set, 1-way, 4-word-block cache walking an 8x8 matrix scores a
hit rate of **0.75** in row order and **0.0** in column order — same data, same
cache, same instruction count.
''',
                "files": [{"name": "main.py", "content": r'''
class Cache:
    def __init__(self, sets, ways, block_words):
        """Validate the geometry and set up empty sets."""
        # your code here

    def fields(self, address):
        """(tag, index, offset) for a word address."""
        # your code here

    def access(self, address):
        """'hit' or 'miss', updating hits / misses / evictions."""
        # your code here

    def hit_rate(self):
        """Hits over accesses; 0.0 when nothing has been accessed."""
        # your code here

    def stats(self):
        """accesses, hits, misses, evictions, hit_rate."""
        # your code here


def run_trace(cache, trace):
    """Replay every address through the cache and return its stats."""
    # your code here


def matrix_trace(rows, cols, order):
    """Word addresses for a row-major matrix walked in 'row' or 'col' order."""
    # your code here


for _ways in (1, 2):
    for _order in ("row", "col"):
        _stats = run_trace(Cache(8, _ways, 4), matrix_trace(8, 8, _order))
        print(f"{_ways}-way {_order:>3} order: hit rate {_stats['hit_rate']:.3f}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class Cache:
    """A parameterised cache: sets x ways blocks of block_words words, LRU."""

    def __init__(self, sets, ways, block_words):
        """Validate the geometry and set up empty sets."""
        for name, value in (("sets", sets), ("block_words", block_words)):
            if not isinstance(value, int) or value < 1 or value & (value - 1):
                raise ValueError(f"{name} must be a power of two, got {value!r}")
        if not isinstance(ways, int) or ways < 1:
            raise ValueError(f"ways must be at least 1, got {ways!r}")
        self.sets = sets
        self.ways = ways
        self.block_words = block_words
        self.offset_bits = block_words.bit_length() - 1
        self.index_bits = sets.bit_length() - 1
        self.lines = [[] for _ in range(sets)]
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def fields(self, address):
        """(tag, index, offset) for a word address."""
        if not isinstance(address, int) or address < 0:
            raise ValueError(f"address must be a non-negative int, got {address!r}")
        offset = address & (self.block_words - 1)
        index = (address >> self.offset_bits) & (self.sets - 1)
        tag = address >> (self.offset_bits + self.index_bits)
        return (tag, index, offset)

    def access(self, address):
        """'hit' or 'miss', updating hits / misses / evictions."""
        tag, index, _offset = self.fields(address)
        entries = self.lines[index]
        if tag in entries:
            entries.remove(tag)
            entries.append(tag)
            self.hits += 1
            return "hit"
        self.misses += 1
        if len(entries) >= self.ways:
            entries.pop(0)
            self.evictions += 1
        entries.append(tag)
        return "miss"

    def hit_rate(self):
        """Hits over accesses; 0.0 when nothing has been accessed."""
        total = self.hits + self.misses
        return self.hits / total if total else 0.0

    def stats(self):
        """accesses, hits, misses, evictions, hit_rate."""
        return {"accesses": self.hits + self.misses, "hits": self.hits,
                "misses": self.misses, "evictions": self.evictions,
                "hit_rate": self.hit_rate()}


def run_trace(cache, trace):
    """Replay every address through the cache and return its stats."""
    for address in trace:
        cache.access(address)
    return cache.stats()


def matrix_trace(rows, cols, order):
    """Word addresses for a row-major matrix walked in 'row' or 'col' order."""
    if order == "row":
        return [row * cols + col for row in range(rows) for col in range(cols)]
    if order == "col":
        return [row * cols + col for col in range(cols) for row in range(rows)]
    raise ValueError(f"order must be 'row' or 'col', got {order!r}")


for _ways in (1, 2):
    for _order in ("row", "col"):
        _stats = run_trace(Cache(8, _ways, 4), matrix_trace(8, 8, _order))
        print(f"{_ways}-way {_order:>3} order: hit rate {_stats['hit_rate']:.3f}")
'''}],
                "hints": [
                    "A positive int is a power of two exactly when `value & (value - 1) == 0`.",
                    "Keep each set as a plain list of tags in recency order, oldest first: a hit does `remove` then `append`, a miss into a full set does `pop(0)`.",
                    "`offset_bits = block_words.bit_length() - 1`, and the index is `(address >> offset_bits) & (sets - 1)`.",
                    "Column order visits `row * cols + col` with the column loop *outside*; that stride of `cols` words is what defeats the cache.",
                ],
                "tests": [
                    {"name": "Address decomposition", "code": r'''
_c = Cache(8, 1, 4)
assert _c.fields(37) == (1, 1, 1), f"fields(37) gave {_c.fields(37)!r}, expected (1, 1, 1)"
assert _c.fields(0) == (0, 0, 0), f"fields(0) gave {_c.fields(0)!r}"
assert _c.fields(31) == (0, 7, 3), f"fields(31) gave {_c.fields(31)!r}, expected (0, 7, 3)"
assert _c.fields(32) == (1, 0, 0), f"fields(32) gave {_c.fields(32)!r}, expected (1, 0, 0)"
_d = Cache(4, 1, 1)
assert _d.fields(6) == (1, 2, 0), f"fields(6) on a 1-word-block cache gave {_d.fields(6)!r}"
'''},
                    {"name": "Bad geometry and bad addresses are refused", "code": r'''
for _args in [(3, 1, 1), (4, 1, 3), (0, 1, 1), (4, 0, 1), (4, 1, 0), (-4, 1, 1)]:
    try:
        Cache(*_args)
        assert False, f"Cache{_args!r} should raise ValueError"
    except ValueError:
        pass
try:
    Cache(4, 1, 1).fields(-1)
    assert False, "a negative address should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Temporal locality: reuse hits", "code": r'''
_c = Cache(4, 1, 1)
_s = run_trace(_c, [0, 1, 2, 3, 0, 1, 2, 3])
assert (_s["misses"], _s["hits"]) == (4, 4), f"got {_s!r}, expected 4 misses then 4 hits"
assert _s["hit_rate"] == 0.5, f"hit_rate is {_s['hit_rate']!r}, expected 0.5"
assert _s["evictions"] == 0, f"nothing should be evicted, got {_s['evictions']!r}"
assert Cache(4, 1, 1).hit_rate() == 0.0, "an untouched cache reports 0.0, it must not divide by zero"
'''},
                    {"name": "Conflict misses, and what associativity fixes", "code": r'''
_s = run_trace(Cache(4, 1, 1), [0, 4, 0, 4])
assert (_s["misses"], _s["hits"], _s["evictions"]) == (4, 0, 3), \
    f"direct-mapped got {_s!r}, expected 4 misses, 0 hits, 3 evictions"
_s = run_trace(Cache(4, 2, 1), [0, 4, 0, 4])
assert (_s["misses"], _s["hits"]) == (2, 2), \
    f"2-way got {_s!r}, expected 2 misses then 2 hits"
'''},
                    {"name": "LRU picks the right victim", "code": r'''
_s = run_trace(Cache(2, 2, 1), [0, 2, 4, 0, 2])
assert (_s["misses"], _s["hits"]) == (5, 0), \
    f"cycling 3 blocks through a 2-way set gave {_s!r}, expected 5 misses"
_c = Cache(2, 2, 1)
run_trace(_c, [0, 2, 0, 4])
assert _c.lines[0] == [0, 2] or set(_c.lines[0]) == {0, 2}, \
    f"after 0, 2, 0, 4 the set should hold tags 0 and 2, it holds {_c.lines[0]!r}"
assert (_c.hits, _c.misses) == (1, 3), f"got hits={_c.hits} misses={_c.misses}, expected 1 and 3"
'''},
                    {"name": "Spatial locality: the same data, two orders", "code": r'''
_row = matrix_trace(8, 8, "row")
_col = matrix_trace(8, 8, "col")
assert _row[:4] == [0, 1, 2, 3], f"row order starts {_row[:4]!r}"
assert _col[:4] == [0, 8, 16, 24], f"column order starts {_col[:4]!r}"
assert sorted(_row) == sorted(_col) == list(range(64)), "both orders touch the same 64 words"
_s = run_trace(Cache(8, 1, 4), _row)
assert (_s["misses"], _s["hits"]) == (16, 48), f"row order gave {_s!r}, expected 16 misses"
assert abs(_s["hit_rate"] - 0.75) < 1e-12, f"row order hit rate {_s['hit_rate']!r}"
_s = run_trace(Cache(8, 1, 4), _col)
assert (_s["misses"], _s["hits"]) == (64, 0), \
    f"column order through a direct-mapped cache gave {_s!r}, expected 64 misses"
'''},
                    {"name": "Associativity rescues the column walk", "code": r'''
_s = run_trace(Cache(8, 2, 4), matrix_trace(8, 8, "col"))
assert (_s["misses"], _s["hits"]) == (16, 48), \
    f"2-way column order gave {_s!r}, expected 16 misses and 48 hits"
try:
    matrix_trace(4, 4, "diagonal")
    assert False, "an unknown order should raise ValueError"
except ValueError:
    pass
assert "hit rate" in _out, "the demo should print a hit rate for each configuration"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a pipelined CW-32 with hazard analysis",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
The single-cycle machine retires one instruction per step but each step is long.
A five-stage pipeline shortens the step and overlaps five instructions — until
one instruction needs a result that is still in flight.

Build a **static pipeline analyser** for CW-32 assembly. `pipeline.py` holds the
logic and is what the checks import; `main.py` is a demo that runs it.

## Model

Stages `IF ID EX MEM WB`, one instruction issued per cycle, in order. Cycles are
numbered from 1, so instruction 0 occupies EX in cycle 3. Write `ex[i]` for the
cycle in which instruction `i` occupies EX. With no hazards `ex[i] = ex[i-1] + 1`
and a program of `n` instructions takes `n + 4` cycles.

**Data hazards (RAW).** For each source register of instruction `i`, find the
nearest earlier `j` with `j >= i - 3` that writes it. Then

| | required | reason |
| --- | --- | --- |
| forwarding, ALU producer | `ex[i] >= ex[j] + 1` | EX/EX bypass |
| forwarding, `LW` producer | `ex[i] >= ex[j] + 2` | the value only exists after MEM |
| no forwarding | `ex[i] >= ex[j] + 3` | wait for WB, read in the same cycle |

`r0` is never a hazard: it is not a real destination and reading it needs nobody.

**Control hazards.** Assume every `BEQ`, `BNE` and `JMP` is mispredicted: the
instruction after a control instruction is delayed by `branch_penalty` cycles
(default 2) *before* data hazards are considered.

`ex[i]` is the maximum of the earliest issue cycle and every hazard requirement.
Total cycles is `ex[n-1] + 2`; an empty program takes 0 cycles.

## What to build in `pipeline.py`

- `ProgramError` — the one exception type parsing raises.
- `Instr` — a record with `op`, `dest` (register written, or `None`), `sources`
  (tuple of registers read, `r0` removed, no duplicates) and `text`. Properties
  `is_load` (`LW`) and `is_control` (`BEQ`, `BNE`, `JMP`).
- `parse_program(text)` — CW-32 assembly to a list of `Instr`. Labels, `#` and
  `;` comments and blank lines behave as they did in the assembler lab. An
  unknown mnemonic, a bad register or the wrong operand count raises `ProgramError`.
- `raw_hazards(program)` — one dict `{"consumer", "producer", "reg", "distance"}`
  per hazard, in consumer order then source order.
- `Pipeline(program, forwarding=True, branch_penalty=2)` with `run()` returning a
  `Report`.
- `Report` — `instructions`, `total_cycles`, `stall_cycles`, `data_stalls`,
  `control_stalls`, `cpi`, `schedule` (the `ex` list) and `hazards`.
  `stall_cycles == data_stalls + control_stalls`, and
  `total_cycles == instructions + 4 + stall_cycles` for a non-empty program.
- `report_text(report)` — a readable multi-line summary containing the lines
  `instructions`, `total cycles`, `stall cycles` and `CPI`.

## Worked figures

```text
LW r1, 0(r0) / ADD r2, r1, r1 / SW r2, 1(r0) / HALT
  forwarding    ->  9 cycles, 1 stall,  CPI 2.250
  no forwarding -> 12 cycles, 4 stalls, CPI 3.000
```
''',
        "deliverables": [
            "`pipeline.py` — parser, hazard detector, pipeline model and report formatter, importable with no side effects",
            "`main.py` — a demo that parses a loop, runs it with and without forwarding and prints both reports",
            "`raw_hazards` output that names consumer, producer, register and distance for every real RAW dependence",
            "A `Report` whose `stall_cycles` splits cleanly into data and control components",
            "`ProgramError` raised for every malformed line rather than a silently mis-parsed instruction",
            "A `report_text` summary a human can read without opening the code",
        ],
        "constraints": [
            "Standard library only; `dataclasses` is enough structure for `Instr` and `Report`",
            "`pipeline.py` must not print anything — running it produces no output",
            "The model is static: analyse the instruction list as written, never simulate branch outcomes",
            "`r0` must not appear as a destination or as a hazard source anywhere",
            "Two `Pipeline` objects over the same program must not share mutable state",
        ],
        "rubric": [
            {"criterion": "Correctness of the pipeline model", "weight": 40,
             "evidence": "Cycle counts, stall totals and CPI match the specified model for straight-line, load-use, branch and empty programs."},
            {"criterion": "Hazard detection", "weight": 20,
             "evidence": "raw_hazards finds the nearest producer within three instructions, ignores r0, and reports the correct distance."},
            {"criterion": "Parsing and error handling", "weight": 20,
             "evidence": "Labels, comments and every CW-32 operand form parse correctly; malformed lines raise ProgramError."},
            {"criterion": "Structure and readability", "weight": 20,
             "evidence": "Instr and Report are declarative records, pipeline.py is side-effect free, and the forwarding rule lives in one place."},
        ],
        "hints": [
            "Write `parse_program` first and give each `Instr` its `dest` and `sources` there; every later stage then works on registers, not on text.",
            "Drop `r0` when you build `sources`, and set `dest = None` when the destination field is 0 — it removes a whole class of false hazards.",
            "The scheduler is one loop: compute `earliest` from the previous instruction plus any branch penalty, then raise it with `max()` for each hazard requirement.",
            "Track `data_stalls` as `ex[i] - earliest` and `control_stalls` as the penalty you added; their sum must equal `total_cycles - instructions - 4`.",
        ],
        "files": [
            {"name": "pipeline.py", "content": r'''
from dataclasses import dataclass, field

R_TYPE = {"ADD", "SUB", "AND", "OR", "XOR", "SLT"}
CONTROL = {"BEQ", "BNE", "JMP"}


class ProgramError(Exception):
    """Raised when a line of CW-32 assembly cannot be understood."""


@dataclass
class Instr:
    op: str
    dest: object = None
    sources: tuple = ()
    text: str = ""

    @property
    def is_load(self):
        """True for LW, whose result only exists after MEM."""
        # your code here

    @property
    def is_control(self):
        """True for BEQ, BNE and JMP."""
        # your code here


@dataclass
class Report:
    instructions: int
    total_cycles: int
    stall_cycles: int
    data_stalls: int
    control_stalls: int
    cpi: float
    schedule: list = field(default_factory=list)
    hazards: list = field(default_factory=list)


def parse_register(token):
    """'r7' -> 7. ProgramError for anything that is not r0..r31."""
    # your code here


def parse_mem(token):
    """'4(r2)' -> (4, 2). ProgramError for anything else."""
    # your code here


def parse_program(text):
    """CW-32 assembly source -> a list of Instr."""
    # your code here


def raw_hazards(program):
    """One dict per read-after-write dependence within the pipeline window."""
    # your code here


class Pipeline:
    def __init__(self, program, forwarding=True, branch_penalty=2):
        self.program = list(program)
        self.forwarding = forwarding
        self.branch_penalty = branch_penalty

    def required_gap(self, producer):
        """Cycles that must separate the producer's EX from the consumer's EX."""
        # your code here

    def run(self):
        """Schedule the program and return a Report."""
        # your code here


def report_text(report):
    """A multi-line human summary of a Report."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from pipeline import Pipeline, parse_program, raw_hazards, report_text

SOURCE = r"""
        ADDI r1, r0, 0
        ADDI r2, r0, 1
        ADDI r3, r0, 11
loop:   BEQ  r2, r3, done
        ADD  r1, r1, r2
        ADDI r2, r2, 1
        JMP  loop
done:   SW   r1, 0(r0)
        HALT
"""

program = parse_program(SOURCE)
for setting in (True, False):
    print("forwarding:", setting)
    print(report_text(Pipeline(program, forwarding=setting).run()))
    print()
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "pipeline.py", "content": r'''
from dataclasses import dataclass, field

R_TYPE = {"ADD", "SUB", "AND", "OR", "XOR", "SLT"}
CONTROL = {"BEQ", "BNE", "JMP"}


class ProgramError(Exception):
    """Raised when a line of CW-32 assembly cannot be understood."""


@dataclass
class Instr:
    op: str
    dest: object = None
    sources: tuple = ()
    text: str = ""

    @property
    def is_load(self):
        """True for LW, whose result only exists after MEM."""
        return self.op == "LW"

    @property
    def is_control(self):
        """True for BEQ, BNE and JMP."""
        return self.op in CONTROL


@dataclass
class Report:
    instructions: int
    total_cycles: int
    stall_cycles: int
    data_stalls: int
    control_stalls: int
    cpi: float
    schedule: list = field(default_factory=list)
    hazards: list = field(default_factory=list)


def parse_register(token):
    """'r7' -> 7. ProgramError for anything that is not r0..r31."""
    text = token.strip().lower()
    if not text.startswith("r") or not text[1:].isdigit():
        raise ProgramError(f"expected a register, got {token!r}")
    number = int(text[1:])
    if not 0 <= number <= 31:
        raise ProgramError(f"register out of range: {token!r}")
    return number


def parse_mem(token):
    """'4(r2)' -> (4, 2). ProgramError for anything else."""
    text = token.strip()
    if not text.endswith(")") or "(" not in text:
        raise ProgramError(f"expected offset(register), got {token!r}")
    offset_text, _, register_text = text[:-1].partition("(")
    offset_text = offset_text.strip()
    if not offset_text:
        raise ProgramError(f"expected offset(register), got {token!r}")
    try:
        offset = int(offset_text, 0)
    except ValueError:
        raise ProgramError(f"bad offset in {token!r}")
    return offset, parse_register(register_text)


def real_sources(*registers):
    """Registers that can carry a dependence: r0 dropped, duplicates removed."""
    seen = []
    for register in registers:
        if register != 0 and register not in seen:
            seen.append(register)
    return tuple(seen)


def expect(tokens, count, op):
    """Raise unless an instruction was given exactly count operands."""
    if len(tokens) != count:
        raise ProgramError(f"{op} takes {count} operand(s), got {len(tokens)}")


def parse_program(text):
    """CW-32 assembly source -> a list of Instr."""
    program = []
    for raw in text.split("\n"):
        line = raw
        for marker in ("#", ";"):
            cut = line.find(marker)
            if cut != -1:
                line = line[:cut]
        line = line.strip()
        while ":" in line:
            line = line.partition(":")[2].strip()
        if not line:
            continue
        tokens = line.replace(",", " ").split()
        op = tokens[0].upper()
        args = tokens[1:]
        if op in R_TYPE:
            expect(args, 3, op)
            rd, rs, rt = [parse_register(a) for a in args]
            instruction = Instr(op, rd or None, real_sources(rs, rt), line)
        elif op == "ADDI":
            expect(args, 3, op)
            rd = parse_register(args[0])
            rs = parse_register(args[1])
            instruction = Instr(op, rd or None, real_sources(rs), line)
        elif op == "LW":
            expect(args, 2, op)
            rd = parse_register(args[0])
            _offset, base = parse_mem(args[1])
            instruction = Instr(op, rd or None, real_sources(base), line)
        elif op == "SW":
            expect(args, 2, op)
            rt = parse_register(args[0])
            _offset, base = parse_mem(args[1])
            instruction = Instr(op, None, real_sources(rt, base), line)
        elif op in ("BEQ", "BNE"):
            expect(args, 3, op)
            rs = parse_register(args[0])
            rt = parse_register(args[1])
            instruction = Instr(op, None, real_sources(rs, rt), line)
        elif op == "JMP":
            expect(args, 1, op)
            instruction = Instr(op, None, (), line)
        elif op in ("NOP", "HALT"):
            expect(args, 0, op)
            instruction = Instr(op, None, (), line)
        else:
            raise ProgramError(f"unknown mnemonic {op!r}")
        program.append(instruction)
    return program


def find_producer(program, consumer, register):
    """Index of the nearest earlier writer of register within the pipeline window."""
    for index in range(consumer - 1, max(-1, consumer - 4), -1):
        if program[index].dest == register:
            return index
    return None


def raw_hazards(program):
    """One dict per read-after-write dependence within the pipeline window."""
    found = []
    for consumer, instruction in enumerate(program):
        for register in instruction.sources:
            producer = find_producer(program, consumer, register)
            if producer is not None:
                found.append({"consumer": consumer, "producer": producer,
                              "reg": register, "distance": consumer - producer})
    return found


class Pipeline:
    """A static five-stage schedule of one CW-32 instruction sequence."""

    def __init__(self, program, forwarding=True, branch_penalty=2):
        self.program = list(program)
        self.forwarding = forwarding
        self.branch_penalty = branch_penalty

    def required_gap(self, producer):
        """Cycles that must separate the producer's EX from the consumer's EX."""
        if not self.forwarding:
            return 3
        return 2 if producer.is_load else 1

    def run(self):
        """Schedule the program and return a Report."""
        program = self.program
        count = len(program)
        schedule = []
        data_stalls = 0
        control_stalls = 0
        for index, instruction in enumerate(program):
            if index == 0:
                penalty = 0
                earliest = 3
            else:
                penalty = self.branch_penalty if program[index - 1].is_control else 0
                earliest = schedule[index - 1] + 1 + penalty
            when = earliest
            for register in instruction.sources:
                producer = find_producer(program, index, register)
                if producer is not None:
                    when = max(when, schedule[producer] + self.required_gap(program[producer]))
            data_stalls += when - earliest
            control_stalls += penalty
            schedule.append(when)
        total = schedule[-1] + 2 if count else 0
        return Report(
            instructions=count,
            total_cycles=total,
            stall_cycles=data_stalls + control_stalls,
            data_stalls=data_stalls,
            control_stalls=control_stalls,
            cpi=total / count if count else 0.0,
            schedule=schedule,
            hazards=raw_hazards(program),
        )


def report_text(report):
    """A multi-line human summary of a Report."""
    lines = [
        f"instructions   {report.instructions}",
        f"total cycles   {report.total_cycles}",
        f"stall cycles   {report.stall_cycles} "
        f"(data {report.data_stalls}, control {report.control_stalls})",
        f"CPI            {report.cpi:.3f}",
    ]
    for hazard in report.hazards:
        lines.append(
            f"  RAW r{hazard['reg']}: instruction {hazard['consumer']} reads what "
            f"{hazard['producer']} writes, {hazard['distance']} apart"
        )
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from pipeline import Pipeline, parse_program, raw_hazards, report_text

SOURCE = r"""
        ADDI r1, r0, 0
        ADDI r2, r0, 1
        ADDI r3, r0, 11
loop:   BEQ  r2, r3, done
        ADD  r1, r1, r2
        ADDI r2, r2, 1
        JMP  loop
done:   SW   r1, 0(r0)
        HALT
"""

program = parse_program(SOURCE)
print("instructions parsed:", len(program))
print("RAW dependences:", len(raw_hazards(program)))
print()

for setting in (True, False):
    print("forwarding:", setting)
    print(report_text(Pipeline(program, forwarding=setting).run()))
    print()

LOAD_USE = r"""
LW  r1, 0(r0)
ADD r2, r1, r1
SW  r2, 1(r0)
HALT
"""

for setting in (True, False):
    report = Pipeline(parse_program(LOAD_USE), forwarding=setting).run()
    print(f"load-use, forwarding={setting}: "
          f"{report.total_cycles} cycles, CPI {report.cpi:.3f}")
'''},
        ],
        "tests": [
            {"name": "Parsing produces the right destinations and sources", "code": r'''
from pipeline import parse_program
_p = parse_program("ADD r3, r1, r2\nADDI r4, r3, -1\nLW r5, 8(r4)\nSW r5, 0(r0)\nHALT\n")
assert len(_p) == 5, f"expected 5 instructions, got {len(_p)}"
assert (_p[0].op, _p[0].dest, _p[0].sources) == ("ADD", 3, (1, 2)), f"got {_p[0]!r}"
assert (_p[1].dest, _p[1].sources) == (4, (3,)), f"ADDI parsed as {_p[1]!r}"
assert (_p[2].dest, _p[2].sources) == (5, (4,)), f"LW parsed as {_p[2]!r}"
assert (_p[3].dest, _p[3].sources) == (None, (5,)), f"SW parsed as {_p[3]!r} — r0 is not a source"
assert (_p[4].dest, _p[4].sources) == (None, ()), f"HALT parsed as {_p[4]!r}"
assert _p[2].is_load and not _p[0].is_load, "only LW is a load"
'''},
            {"name": "Labels, comments and blank lines are skipped", "code": r'''
from pipeline import parse_program
_p = parse_program("# header\n\nloop:   ADD r1, r1, r2   ; body\n  BEQ r1, r2, loop\nend:\nHALT\n")
assert [i.op for i in _p] == ["ADD", "BEQ", "HALT"], f"parsed ops {[i.op for i in _p]!r}"
assert _p[1].is_control and not _p[0].is_control, "BEQ is a control instruction, ADD is not"
assert parse_program("") == [], "an empty source parses to an empty program"
'''},
            {"name": "Malformed lines raise ProgramError", "code": r'''
from pipeline import parse_program, ProgramError
for _bad in ["FROB r1, r2, r3\n", "ADD r1, r2\n", "ADD r1, r2, r3, r4\n", "HALT r1\n",
             "LW r1, r2\n", "ADDI x1, r0, 1\n", "ADDI r32, r0, 1\n", "JMP\n"]:
    try:
        parse_program(_bad)
        assert False, f"parse_program({_bad!r}) should raise ProgramError"
    except ProgramError:
        pass
'''},
            {"name": "raw_hazards finds the nearest producer", "code": r'''
from pipeline import parse_program, raw_hazards
_h = raw_hazards(parse_program("ADDI r1, r0, 1\nADDI r1, r0, 2\nADD r2, r1, r1\nHALT\n"))
assert len(_h) == 1, f"one register, one hazard — got {_h!r}"
assert _h[0] == {"consumer": 2, "producer": 1, "reg": 1, "distance": 1}, f"got {_h[0]!r}"
_h = raw_hazards(parse_program("ADDI r1, r0, 1\nNOP\nNOP\nNOP\nADD r2, r1, r1\nHALT\n"))
assert _h == [], f"a producer four instructions back is out of the window, got {_h!r}"
_h = raw_hazards(parse_program("ADDI r1, r0, 1\nADDI r2, r0, 2\nADD r3, r1, r2\nHALT\n"))
assert [x["reg"] for x in _h] == [1, 2], f"both sources should be reported, got {_h!r}"
assert [x["distance"] for x in _h] == [2, 1], f"distances came out as {_h!r}"
'''},
            {"name": "r0 never creates a hazard", "code": r'''
from pipeline import parse_program, raw_hazards, Pipeline
_p = parse_program("ADDI r0, r0, 5\nADD r1, r0, r0\nHALT\n")
assert _p[0].dest is None, f"writing r0 is not a destination, got {_p[0].dest!r}"
assert _p[1].sources == (), f"reading r0 is not a source, got {_p[1].sources!r}"
assert raw_hazards(_p) == [], f"expected no hazards, got {raw_hazards(_p)!r}"
_r = Pipeline(_p).run()
assert _r.stall_cycles == 0 and _r.total_cycles == 7, \
    f"3 instructions with no hazards take 7 cycles, got {_r.total_cycles} with {_r.stall_cycles} stalls"
'''},
            {"name": "A hazard-free program takes n + 4 cycles", "code": r'''
from pipeline import parse_program, Pipeline
_p = parse_program("ADDI r1, r0, 1\nADDI r2, r0, 2\nADDI r3, r0, 3\nADDI r4, r0, 4\nHALT\n")
_r = Pipeline(_p).run()
assert _r.instructions == 5, f"instructions is {_r.instructions!r}"
assert _r.total_cycles == 9, f"5 instructions, no hazards -> 9 cycles, got {_r.total_cycles}"
assert _r.schedule == [3, 4, 5, 6, 7], f"EX cycles came out as {_r.schedule!r}"
assert _r.stall_cycles == 0, f"expected no stalls, got {_r.stall_cycles}"
assert abs(_r.cpi - 1.8) < 1e-12, f"CPI is {_r.cpi!r}, expected 1.8"
assert Pipeline([]).run().total_cycles == 0, "an empty program takes 0 cycles"
assert Pipeline([]).run().cpi == 0.0, "an empty program must not divide by zero"
'''},
            {"name": "Forwarding removes the ALU stalls", "code": r'''
from pipeline import parse_program, Pipeline
_p = parse_program("ADDI r1, r0, 5\nADDI r2, r0, 7\nADD r3, r1, r2\nHALT\n")
_on = Pipeline(_p, forwarding=True).run()
assert (_on.total_cycles, _on.stall_cycles) == (8, 0), \
    f"with forwarding: {_on.total_cycles} cycles / {_on.stall_cycles} stalls, expected 8 / 0"
_off = Pipeline(_p, forwarding=False).run()
assert (_off.total_cycles, _off.data_stalls) == (10, 2), \
    f"without forwarding: {_off.total_cycles} cycles / {_off.data_stalls} data stalls, expected 10 / 2"
assert _off.schedule == [3, 4, 7, 8], f"EX cycles without forwarding came out as {_off.schedule!r}"
'''},
            {"name": "The load-use hazard survives forwarding", "code": r'''
from pipeline import parse_program, Pipeline
_p = parse_program("LW r1, 0(r0)\nADD r2, r1, r1\nSW r2, 1(r0)\nHALT\n")
_on = Pipeline(_p, forwarding=True).run()
assert (_on.total_cycles, _on.data_stalls) == (9, 1), \
    f"load-use with forwarding gave {_on.total_cycles} cycles / {_on.data_stalls} stalls, expected 9 / 1"
assert abs(_on.cpi - 2.25) < 1e-12, f"CPI is {_on.cpi!r}, expected 2.25"
_off = Pipeline(_p, forwarding=False).run()
assert (_off.total_cycles, _off.data_stalls) == (12, 4), \
    f"load-use without forwarding gave {_off.total_cycles} cycles / {_off.data_stalls} stalls, expected 12 / 4"
assert abs(_off.cpi - 3.0) < 1e-12, f"CPI is {_off.cpi!r}, expected 3.0"
'''},
            {"name": "Control instructions cost the branch penalty", "code": r'''
from pipeline import parse_program, Pipeline
_p = parse_program("ADDI r1, r0, 1\nBEQ r1, r1, done\nADD r2, r1, r1\ndone: HALT\n")
_r = Pipeline(_p).run()
assert (_r.control_stalls, _r.data_stalls) == (2, 0), \
    f"expected 2 control stalls and no data stalls, got {_r.control_stalls} / {_r.data_stalls}"
assert _r.total_cycles == 10, f"expected 10 cycles, got {_r.total_cycles}"
assert _r.schedule == [3, 4, 7, 8], f"EX cycles came out as {_r.schedule!r}"
_free = Pipeline(_p, branch_penalty=0).run()
assert _free.total_cycles == 8, f"with a perfect predictor: expected 8 cycles, got {_free.total_cycles}"
'''},
            {"name": "The loop from the demo, both ways", "code": r'''
from pipeline import parse_program, Pipeline
_src = "ADDI r1, r0, 0\nADDI r2, r0, 1\nADDI r3, r0, 11\nloop: BEQ r2, r3, done\n" \
       "ADD r1, r1, r2\nADDI r2, r2, 1\nJMP loop\ndone: SW r1, 0(r0)\nHALT\n"
_p = parse_program(_src)
assert len(_p) == 9, f"expected 9 instructions, got {len(_p)}"
_on = Pipeline(_p, forwarding=True).run()
assert (_on.total_cycles, _on.data_stalls, _on.control_stalls) == (17, 0, 4), \
    f"with forwarding: {_on.total_cycles} cycles, {_on.data_stalls} data, {_on.control_stalls} control"
_off = Pipeline(_p, forwarding=False).run()
assert (_off.total_cycles, _off.data_stalls, _off.control_stalls) == (19, 2, 4), \
    f"without forwarding: {_off.total_cycles} cycles, {_off.data_stalls} data, {_off.control_stalls} control"
assert _off.cpi > _on.cpi, "forwarding must not make CPI worse"
'''},
            {"name": "The accounting identity holds", "code": r'''
from pipeline import parse_program, Pipeline
_src = "LW r1, 0(r0)\nADD r2, r1, r1\nBEQ r2, r1, end\nSUB r3, r2, r1\nend: SW r3, 2(r0)\nHALT\n"
for _fwd in (True, False):
    for _pen in (0, 1, 2, 3):
        _r = Pipeline(parse_program(_src), forwarding=_fwd, branch_penalty=_pen).run()
        assert _r.stall_cycles == _r.data_stalls + _r.control_stalls, \
            f"stall_cycles {_r.stall_cycles} != {_r.data_stalls} + {_r.control_stalls}"
        assert _r.total_cycles == _r.instructions + 4 + _r.stall_cycles, \
            f"total {_r.total_cycles} != {_r.instructions} + 4 + {_r.stall_cycles}"
        assert abs(_r.cpi - _r.total_cycles / _r.instructions) < 1e-12, f"CPI is {_r.cpi!r}"
        assert _r.schedule == sorted(_r.schedule) and len(set(_r.schedule)) == len(_r.schedule), \
            f"EX cycles must be strictly increasing, got {_r.schedule!r}"
'''},
            {"name": "report_text summarises, pipeline.py stays silent", "code": r'''
from pipeline import parse_program, Pipeline, report_text
_r = Pipeline(parse_program("LW r1, 0(r0)\nADD r2, r1, r1\nHALT\n")).run()
_text = report_text(_r)
assert isinstance(_text, str), "report_text returns a string, it does not print"
for _label in ["instructions", "total cycles", "stall cycles", "CPI"]:
    assert _label in _text, f"the summary should mention {_label!r}; got:\n{_text}"
_src = open("pipeline.py").read()
assert "print(" not in _src, "pipeline.py is a library; the printing belongs in main.py"
assert "cycles" in _out.lower(), "main.py should print the cycle counts it computed"
'''},
        ],
    },
}
