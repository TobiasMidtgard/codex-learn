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
            "read": [
                {
                    "title": "A wheel with 256 positions",
                    "minutes": 10,
                    "body": r'''
Take an eight-bit register and add one to it, over and over. It counts 0, 1, 2 and so on
up to 255, and then the next add produces 256, which needs a ninth bit. There is no ninth
bit. The carry falls off the end, the register holds 0, and the count starts again. An
eight-bit register is not a number line; it is a wheel with 256 positions, and adding
moves you round it.

Now read the wheel backwards. If 255 + 1 lands on 0, then 255 is behaving exactly as −1
would: it is the thing you add to 1 to get 0. And 254 is the thing you add to 2 to get 0,
so it behaves as −2. Nobody had to decide that 255 means −1. The wrap-around decided it,
and every other consequence of two's complement falls out of the same wheel.

## The pattern for a negative number

On a wheel with $2^w$ positions, moving $x$ steps backwards from 0 lands on position
$2^w - x$. That is the whole rule: the $w$-bit pattern for $-x$ is the unsigned number
$2^w - x$. For $-37$ in eight bits, $256 - 37 = 219$, and 219 in binary is `11011011`.

The invert-and-add-one recipe that every textbook gives is the same arithmetic in
disguise. Write $2^w - x$ as $(2^w - 1) - x + 1$. The number $2^w - 1$ is $w$ ones, and
subtracting $x$ from a row of ones never needs a borrow, because every column is $1 - 0$
or $1 - 1$. So $(2^w - 1) - x$ is $x$ with every bit flipped, and the trailing $+1$ is the
add-one step.

```python
x = 37
width = 8
ones = (1 << width) - 1            # 0b11111111
inverted = ones ^ x                # every bit of x flipped, no borrows anywhere
print(f"{x:08b} inverted is {inverted:08b} = {inverted}")
print(f"plus one: {inverted + 1:08b} = {inverted + 1}, and 256 - 37 = {256 - 37}")
```

Both routes reach 219, and they always will, because they are the same subtraction
written two ways.

## Which half of the wheel is negative

The wheel has no sign on it. The patterns 0 to 255 are all there; the question is which
of them you choose to read as negative. Two's complement draws the line at the top bit:
patterns with bit 7 clear are read as themselves, 0 to 127, and patterns with bit 7 set
are read as the pattern minus 256, which runs from $128 - 256 = -128$ up to
$255 - 256 = -1$.

Two things about that range deserve a second look. There is exactly one zero,
`00000000`, because the wheel has one position at the top. Sign-magnitude
representation, where the top bit is a flag and the rest is the size, has both
`00000000` and `10000000` meaning zero, and hardware that has to compare two zeros for
equality is hardware that is slower and wrong more often. Second, the range is lopsided:
$-128$ to $127$. Zero has to live somewhere, and it lives in the non-negative half, so
that half has one fewer non-zero value. In general a $w$-bit two's-complement register
holds $-2^{w-1}$ to $2^{w-1} - 1$.

Python's integers have no width at all, so to model a register you supply the width
yourself. Reducing modulo $2^w$ gives the pattern; reading the top bit gives it back.

```python
def to_twos(value, width):
    return value % (1 << width)        # Python's % is never negative, so this lands on the wheel

def from_twos(bits, width):
    if bits >> (width - 1):            # top bit set: the negative half of the wheel
        return bits - (1 << width)
    return bits

for value in (37, -37, -1, -128, 127):
    bits = to_twos(value, 8)
    print(f"{value:5d} -> {bits:08b} ({bits:3d}) -> {from_twos(bits, 8):5d}")
```

`value & 0xFF` gives the same pattern as `value % 256`, and it is the form you will meet
in C and in the lab hints. It works because Python behaves as though a negative integer
had infinitely many leading one bits, and the mask keeps the low eight of them.

## Adding, and the carry that tells you nothing

Add two patterns on the wheel and you get a pattern on the wheel. Whether the *signed*
reading of that pattern is the true sum is a separate question, and the answer is no
exactly when the true sum falls outside $-128$ to $127$. That event is signed overflow,
and the hardware needs a way to detect it that does not involve knowing the true sum.

Watch three additions with the carries written down. In each, the ninth bit that falls
off the end is the carry *out of* the sign position; the carry that arrives at bit 7 from
bit 6 is the carry *into* it.

```python
def add_with_carries(a_bits, b_bits, width):
    carry = 0
    result = 0
    carry_into_top = 0
    for bit in range(width):
        column = ((a_bits >> bit) & 1) + ((b_bits >> bit) & 1) + carry
        result |= (column & 1) << bit
        if bit == width - 1:
            carry_into_top = carry
        carry = column >> 1
    return result, carry_into_top, carry       # carry is now the carry OUT of the top bit

for a, b in ((127, 1), (-1, 1), (-128, -1), (100, 27)):
    result, c_in, c_out = add_with_carries(a % 256, b % 256, 8)
    signed = result - 256 if result >> 7 else result
    print(f"{a:5d} + {b:5d} = {result:08b} read as {signed:5d}   "
          f"carry into sign {c_in}, out of sign {c_out}, overflow {c_in != c_out}")
```

$127 + 1$: `01111111 + 00000001` produces `10000000`. A carry arrived at bit 7 and none
left it, and the result reads as $-128$. Overflow. $-1 + 1$: `11111111 + 00000001`
produces `00000000` with a carry out; a carry also arrived at bit 7. Both carries, no
overflow, and the answer 0 is right. $-128 + (-1)$: `10000000 + 11111111`. No carry
arrives at bit 7, because the low seven columns are `0000000 + 1111111` with no carry
anywhere, but $1 + 1$ at bit 7 produces a carry out. The result `01111111` reads as
$127$. Overflow again, in the other direction.

So the rule is: signed overflow happens when the carry into the sign bit differs from
the carry out of it. The carry out on its own means nothing for signed arithmetic;
$-1 + 1$ has one and is fine. The tempting mistake is to read the carry-out flag, which
is what unsigned arithmetic uses, as the overflow flag. It is tempting because the
carry-out is the bit that visibly fell off the end, and losing a bit feels like an error.
Processors keep both flags, as separate bits, because they answer different questions.

There is a second way to say the same rule that needs no carries at all: overflow
happens when two operands of the same sign produce a result of the opposite sign. Two
positives cannot honestly sum to a negative, two negatives cannot sum to a positive, and
operands of different signs can never leave the range. The lab's `add_twos` uses this
second form, because it has the operands and the result in hand and does not have to
rebuild the ripple carry.

## Changing width

Move the eight-bit $-37$, `11011011`, into a sixteen-bit register. The value should
still be $-37$, whose sixteen-bit pattern is $65536 - 37 = 65499$, or
`1111111111011011`. The new top byte is all ones. That is not a coincidence:
$2^{16} - 37 = (2^{16} - 2^8) + (2^8 - 37)$, and $2^{16} - 2^8$ is eight ones in the
upper byte with zeros below. So widening a two's-complement number means copying its top
bit into every new position. That is sign extension, and in hardware it is wires, not
gates.

```python
value = -37
narrow = value & 0xFF                                  # 8-bit pattern
wide = value & 0xFFFF                                  # 16-bit pattern
print(f"{narrow:08b}   {wide:016b}")
extended = narrow | (0xFF00 if narrow & 0x80 else 0)   # copy bit 7 into bits 8..15
print(extended == wide, wide, 65536 - 37)
```

Going the other way, from sixteen bits to eight, you drop the top byte. That is
truncation, and it preserves the value only when every dropped bit equals the new top
bit: $-37$ survives, but $300$, which is `0000000100101100`, becomes `00101100`, which
is 44.

## The mistake: reading a pattern without saying its width

A pattern on its own has no value. `0xFF` is $-1$ at eight bits and $255$ at sixteen;
`0x80` is $-128$ at eight bits and $128$ at any wider width. The concept list for this
module calls a byte a viewpoint rather than a type, and this is what it means: the bits
are the same, and the reading depends on the width you bring to them.

C makes this mistake easy to commit, because it changes widths on your behalf. In an
arithmetic expression, a `char` or `short` is promoted to `int` before anything happens
to it, and a signed `int` meeting an `unsigned int` is converted to unsigned.

```c
unsigned int big = 1;
int minus_one = -1;
if (minus_one < big)
    puts("less");          /* never prints: -1 becomes 4294967295 first */
```

The comparison is done at 32 bits unsigned, so $-1$ is read as $4294967295$ and is not
less than anything. It is tempting because the source reads as a comparison of two small
numbers, and nothing on the page says a width change happened.

## Where the wheel stops matching

Python integers do not wrap, so `127 + 1` is `128` and stays there. Everything in this
reading is a simulation of a register, which is why the lab asks you to write the width
into every call. The simulation also has to refuse what the hardware cannot express, and
there is one value that catches people: the most negative number has no positive
partner. Negating $-128$ on an eight-bit wheel means $256 - 128 = 128$, which is
`10000000`, which reads as $-128$ again. Real hardware does that silently, and C calls
the result undefined behaviour; a `to_twos` with a range check turns it into an error
you can see.

```python
# raises ValueError
def to_twos(value, width):
    low, high = -(1 << (width - 1)), (1 << (width - 1)) - 1
    if not low <= value <= high:
        raise ValueError(f"{value} does not fit in {width} signed bits")
    return value & ((1 << width) - 1)

print(to_twos(-128, 8))        # 128: the pattern of the most negative number
print(to_twos(-(-128), 8))     # 128 is above 127: its negation has no pattern at all
```

The lab **Bit patterns: two's complement and binary32** asks for `to_twos` and
`from_twos` at any width, with the range checks that make out-of-range values and
malformed patterns errors rather than wrong answers, and for `add_twos`, which returns
the truncated sum together with the overflow flag from the same-sign rule above. The
tests include `add_twos(-128, -1, 8)` and `add_twos(-1, 1, 8)`, the two cases that
separate carry-out from overflow. The second reading in this module covers the other
half of the lab, where the same 32 bits are read as a floating-point number.
''',
                },
                {
                    "title": "Scientific notation in 32 bits",
                    "minutes": 11,
                    "body": r'''
Avogadro's number is written $6.022 \times 10^{23}$ rather than as a 24-digit integer,
and the notation carries three separate pieces of information: a sign, a string of
significant digits, and a count of how far the point has been slid. Floating-point
hardware stores numbers the same way, in base two. The number $0.15625$ is
$\frac{5}{32}$, which is $\frac{5}{4} \times \frac{1}{8}$, which is $1.25 \times 2^{-3}$,
or in binary $1.01_2 \times 2^{-3}$. A sign, the digits `1.01`, and the exponent $-3$:
that is everything binary32 stores about it.

## Deriving the layout from the notation

Normalise any non-zero binary number so that there is exactly one non-zero digit before
the point. That digit is a 1, because binary has no other non-zero digit, so the leading
1 is always there and carries no information. Do not store it. The 23 bits after the
point are stored and the 1 in front is implied: this is the implicit leading bit, and it
buys a 24-bit significand for the price of 23.

The exponent needs to run negative as well as positive. Two's complement would do, but
IEEE-754 stores the exponent plus 127 as an unsigned eight-bit field instead. Slide the
number line so that $-127$ maps to 0 and $128$ maps to 255, and the field never needs a
sign of its own. The reason is comparison. For two positive floats, the one with the
larger exponent is the larger number, and with a biased exponent sitting above the
fraction, that comparison is the same as comparing the two 32-bit patterns as unsigned
integers. A biased exponent lets the integer comparator judge floats. Two's complement
would put the negative exponents *above* the positive ones and break that.

So the word is sign, then eight bits of exponent plus 127, then 23 bits of fraction. For
$0.15625$: sign 0, exponent field $-3 + 127 = 124$, which is `01111100`, and fraction
`01` followed by 21 zeros. Assembled, that is `0 01111100 01000000000000000000000`, or
`0x3E200000`.

## Doing it with frexp and ldexp

The lab forbids `struct` because the point is to do the scaling yourself, and two
functions in `math` do it exactly. `math.frexp(x)` returns a mantissa $m$ and an
exponent $e$ with $x = m \times 2^e$ and $0.5 \le m < 1$, which is one position off
from the $1.f$ form, so the exponent you want is $e - 1$. `math.ldexp(x, k)` computes
$x \times 2^k$ without any rounding, because scaling by a power of two only moves the
exponent.

```python
import math

x = 0.15625
mantissa, raw_exp = math.frexp(x)            # x == mantissa * 2**raw_exp, 0.5 <= mantissa < 1
exponent = raw_exp - 1                       # the 1.f form sits one place to the left
significand = math.ldexp(x, 23 - exponent)   # all 24 significand bits moved into the integer part
print(mantissa, raw_exp, exponent)           # 0.625 -2 -3
print(significand, hex(int(significand)))    # 10485760.0 0xa00000
fraction = int(significand) - (1 << 23)      # drop the implicit 1
word = ((exponent + 127) << 23) | fraction
print(hex(word))                             # 0x3e200000
```

Multiplying by $2^{23 - e}$ turns $1.f \times 2^e$ into a 24-bit integer: the leading 1
lands at bit 23 and the 23 fraction bits sit below it. Subtracting $2^{23}$ removes the
leading 1, and what is left is the fraction field.

## The number that is not there

For $0.15625$ the scaled significand was a whole number, because $0.15625$ has a short
binary expansion. Most decimals do not. $0.1$ in binary is $0.000110011001100\ldots$,
repeating forever, and $1.6 \times 2^{-4}$ in the normalised form. Scaling by $2^{27}$
gives $13421772.8$, and the fraction field has no room for the $.8$: something has to
be rounded.

```python
import math

def round_half_even(value):
    low = math.floor(value)
    rest = value - low
    if rest > 0.5:
        return low + 1
    if rest < 0.5:
        return low
    return low if low % 2 == 0 else low + 1

x = 0.1
_, raw_exp = math.frexp(x)
exponent = raw_exp - 1                        # -4, because 0.1 = 1.6 * 2**-4
scaled = math.ldexp(x, 23 - exponent)         # 13421772.8
significand = round_half_even(scaled)         # 13421773
print(exponent, scaled, significand)
word = ((exponent + 127) << 23) | (significand - (1 << 23))
print(hex(word))                              # 0x3dcccccd
stored = significand / 2 ** 27
print(f"{stored:.30f}")                       # 0.100000001490116119384765625000
```

The stored value is $13421773 / 2^{27}$, which is $0.100000001490116119384765625$
exactly. That is the number a `float` variable holding 0.1 contains, and it is why
`0.1 + 0.2 == 0.3` fails: each of the three is a nearby binary fraction, and the errors
do not cancel.

Rounding is to the nearest representable value, and when the scaled significand sits
exactly halfway, the tie goes to whichever neighbour has an even last bit. Round-half-up,
the schoolroom rule, would nudge every tie in the same direction, and over a long sum
those nudges accumulate into a bias. Ties to even go up half the time and down half the
time, so on average they cancel. The lab supplies `round_half_even` and its test
constructs the two ties on either side of `0x3F800001` to see which way each one falls.

```python
import struct

def bits_of(x):
    return struct.unpack(">I", struct.pack(">f", x))[0]

one = 1.0
next_up = 1.0 + 2 ** -23                     # 0x3F800001, the binary32 after 1.0
halfway = (one + next_up) / 2                # exact as a Python float, a tie in binary32
print(hex(bits_of(halfway)))                 # 0x3f800000 -- down, to the even fraction 0
after = next_up + 2 ** -23                   # 0x3F800002
print(hex(bits_of((next_up + after) / 2)))   # 0x3f800002 -- up, to the even fraction 2
```

`struct` is used here only to check the answer; the lab has you produce it.

## The bottom of the range, and the seam

The exponent field runs from 0 to 255, and the two ends are reserved. Field 255 with a
zero fraction is infinity, with the sign bit choosing which; field 255 with any non-zero
fraction is NaN, the result of $0/0$ or $\sqrt{-1}$, and the lab accepts `0x7FC00000`
for it. A magnitude too large for field 254 becomes infinity: `float_to_bits(3.5e38)` is
`0x7F800000`.

Field 0 is where the implicit bit is switched off. With it on, the smallest normal number
would be $1.0 \times 2^{-126}$ and the next number below it would be zero, a gap of
$2^{-126}$ next to a region where neighbouring numbers differ by $2^{-149}$. Field 0
instead means $0.f \times 2^{-126}$: no leading 1, and the exponent held at $-126$
rather than the $-127$ the bias formula would give. These are the subnormals, and they
fill the gap between zero and the smallest normal with the same spacing as the normals
directly above them.

```python
import math

smallest_normal = math.ldexp(1.0, -126)
step = math.ldexp(1.0, -149)                          # 2**-126 / 2**23: the subnormal spacing
largest_subnormal = math.ldexp((1 << 23) - 1, -149)   # field 0, fraction all ones
print(smallest_normal - largest_subnormal == step)    # True: no seam between the two families
print(largest_subnormal / step)                       # 8388607.0 -- 2**23 - 1 steps up from zero

wrong_largest = math.ldexp((1 << 23) - 1, -150)       # what an exponent of -127 would give
print(smallest_normal - wrong_largest > 4_000_000 * step)   # True: a gap millions of steps wide
```

The tempting mistake is to write `exponent - 127` for field 0 too, because the formula
looks uniform and one special case is easier to remember than two. It is not uniform:
field 0 and field 1 share the exponent $-126$, and what changes between them is the
implicit bit. `bits_to_float(0x00000001)` must be $2^{-149}$, and with $-127$ it comes
out at half that. The lab's decode test checks that pattern by name.

There is also a zero for each sign: `0x00000000` and `0x80000000` compare equal but are
different patterns, and `float_to_bits(-0.0)` has to preserve the sign bit rather than
testing `x == 0` and returning zero. `math.copysign(1.0, x)` sees the sign of a negative
zero; `x < 0` does not.

## Where 32 bits stop being enough

A `float` and an `int` both occupy 32 bits, and it is tempting to think the float, which
reaches $3.4 \times 10^{38}$, holds everything the int does. It does not. The
significand is 24 bits, so every integer up to $2^{24} = 16777216$ is exact and the very
next one is not.

```python
import struct

def as_binary32(x):
    return struct.unpack(">f", struct.pack(">f", x))[0]

print(as_binary32(16777216.0))     # 16777216.0
print(as_binary32(16777217.0))     # 16777216.0 -- the odd number has no pattern of its own
print(as_binary32(0.1) == 0.1)     # False: the 24-bit value differs from the 53-bit one
```

Range was bought with precision. Above $2^{24}$ the representable numbers are two
apart, above $2^{25}$ four apart, and a loop that adds 1.0 to a float counter stops
counting altogether at 16777216.

Everything here is binary32. Python's own `float` is binary64, with 11 exponent bits, a
bias of 1023 and 52 stored fraction bits, which is why the halfway values in the tie
test could be built exactly: a binary64 has room for a bit below the binary32 grid. The
layout generalises but the constants do not, and a decoder written with 23 and 127
hard-coded is a binary32 decoder only.

The lab **Bit patterns: two's complement and binary32** asks for `float_to_bits` and
`bits_to_float`. Handle the special cases first, NaN, the sign, infinity and zero, then
split on whether the exponent is below $-126$, and only then scale, round and assemble.
A rounded significand can reach $2^{24}$ when a fraction of all ones rounds up; when it
does, halve it and add one to the exponent, and if the exponent then passes 127 the
answer is infinity.
''',
                },
            ],
            "quiz": {
                "title": "Widths, carries and the seams of binary32",
                "minutes": 8,
                "questions": [
                    {
                        "q": r'''
A byte read from a file holds the pattern `0xF0`. A program reads it as an 8-bit
two's-complement value, then copies the bits into the low byte of a 16-bit register and
fills the upper byte with zeros. What does the 16-bit register read as, and why?
''',
                        "opts": [
                            "240: zero-filling the top byte clears the sign bit, so the 16-bit reading is the unsigned 240",
                            "−16: the bits are the same bits, and the value of a pattern does not change when it is widened",
                            "65520: the register holds the 16-bit pattern of −16, which read as unsigned is 65536 − 16",
                            "−240: the sign comes from the original byte and the magnitude from the new, wider width",
                        ],
                        "a": 0,
                        "whys": [
                            r"The 16-bit pattern is 0000000011110000, whose top bit is clear, so it sits in the non-negative half of the wheel. Zero-filling is what changed the value; copying the top bit would have preserved it.",
                            r"The bits in the low byte are the same, but a pattern has no value until a width is chosen, and at 16 bits the bit that made it negative is no longer the top bit. Zero-filling is not value-preserving; sign extension is.",
                            r"65520 is what sign extension would produce when read unsigned: 1111111111110000. The upper byte here was filled with zeros, not ones, so the pattern is 0000000011110000 and reads as 240.",
                            r"Two's complement has no separate sign that travels with the number; the sign is a property of the top bit at the current width. Nothing in the process computed a magnitude of 240 with a minus attached.",
                        ],
                        "why": r"""
The pattern 11110000 is −16 at eight bits because its top bit is set. Zero-filling to
sixteen bits gives 0000000011110000, whose top bit is clear, so it reads as 240. A byte
is a viewpoint: the same eight bits are −16 or 240 depending on the width you read them
at, and moving between widths preserves the value only when the top bit is copied into
the new positions. C's promotions do that copy for signed types and skip it for unsigned
ones, which is where most of the surprising results come from.
""",
                    },
                    {
                        "q": r'''
`add_twos(-100, -28, 8)` adds the patterns `10011100` and `11100100`. The addition
produces a ninth bit, which is discarded. What does the function return, and what does
the discarded carry say about overflow?
''',
                        "opts": [
                            "`(-128, False)`: the sum fits, and a carry out of the sign bit means nothing on its own",
                            "`(-128, True)`: a carry fell off the end, and a lost carry is what overflow means",
                            "`(128, True)`: the eight-bit result `10000000` is 128, above the signed maximum of 127",
                            "`(127, True)`: the true sum is below −127, so the result wraps to the largest positive value",
                        ],
                        "a": 0,
                        "whys": [
                            r"Both operands are negative and the result 10000000 reads as −128, also negative: the same-sign rule finds no overflow. The carry into the sign bit and the carry out of it are both 1, and equal carries mean the same thing.",
                            r"The discarded carry is the carry out of the top bit, which unsigned arithmetic cares about. Signed overflow is the carry into the sign bit differing from the carry out, and here both are 1. −1 + 1 also drops a carry and is not an overflow.",
                            r"10000000 is 128 only when read unsigned. `add_twos` reads the truncated sum as signed, where a set top bit means the pattern minus 256: −128, which is inside the range.",
                            r"The range of an 8-bit signed value is −128 to 127, so −128 is inside it and no wrap occurs. Wrapping to 127 is what happens for −128 + (−1), one step further down.",
                        ],
                        "why": r"""
−100 + (−28) is −128, the most negative 8-bit value and still in range. The patterns 156
and 228 sum to 384; discarding the ninth bit leaves 128, and read as signed that is −128.
Two negative operands gave a negative result, so the same-sign rule reports no overflow.
The carry that fell off the end is the carry out of the sign bit, and it is the carry
*into* the sign bit differing from it that signals overflow; here both are 1. Unsigned
arithmetic reads the carry-out as its overflow, and hardware keeps the two flags apart
because they answer different questions.
""",
                    },
                    {
                        "q": r'''
IEEE-754 stores the exponent as an unsigned field with 127 added, rather than as a
two's-complement value. What does the bias buy?
''',
                        "opts": [
                            "Positive floats then order the same way as their bit patterns read as unsigned integers, so one comparator serves both",
                            "It gives the exponent one more usable value, since two's complement wastes a pattern on a second zero",
                            "Negative exponents never occur in practice, so an unsigned field loses nothing and saves a sign bit",
                            "It is what makes the implicit leading 1 possible, because a biased exponent field is never zero for any normal number",
                        ],
                        "a": 0,
                        "whys": [
                            r"With the biased exponent sitting above the fraction, a larger exponent gives a larger unsigned pattern, and within one exponent a larger fraction does too. The integer comparator can sort positive floats.",
                            r"Two's complement has one zero, not two; the second zero belongs to sign-magnitude. Both encodings offer 256 exponent patterns, and the bias changes which number each pattern stands for, not how many there are.",
                            r"Every value below 1.0, including 0.5 and 0.1, has a negative exponent. The field has to represent −126 to 127, and the bias is how it does so without a sign of its own.",
                            r"The implicit 1 comes from normalisation, which works with any exponent encoding. Field 0 is reserved for subnormals by a separate rule; the bias does not cause that reservation.",
                        ],
                        "why": r"""
The bias exists for comparison. Slide the exponents so the smallest is 0 and the largest
255, place that field above the fraction, and for two positive floats the one with the
larger bit pattern as an unsigned integer is the larger number. Two's complement would
put −1 above 127 as a pattern and break the ordering. Negative exponents are the ordinary
case, not a rarity; every magnitude below 1 has one. Neither encoding gains a value, and
the implicit 1 is a consequence of normalising, not of how the exponent is written.
""",
                    },
                    {
                        "q": r'''
Exponent field 0 denotes $0.f \times 2^{-126}$, the same power of two as field 1,
rather than the $2^{-127}$ that `field - 127` would give. What goes wrong with
$2^{-127}$?
''',
                        "opts": [
                            "The largest subnormal lands near half the smallest normal, leaving a gap millions of subnormal steps wide",
                            "The subnormals overlap the normals, so some values get two patterns and equality comparisons fail",
                            "Zero can no longer be represented, since a non-zero power of two multiplies every fraction, including 0",
                            "Nothing goes wrong; the choice is a convention, and either exponent gives a consistent set of values",
                        ],
                        "a": 0,
                        "whys": [
                            r"With −127, the fraction of all ones gives about $2^{-127}$, while the smallest normal is $2^{-126}$. The seam is a gap of about $2^{-127}$, or $2^{22}$ steps of $2^{-149}$, in a region where neighbours should be one step apart.",
                            r"Overlap is the opposite failure. With −127 the subnormals stop short of the normals rather than reaching into them, and with −126 they end exactly one step below the smallest normal; neither choice makes two patterns denote one value.",
                            r"Zero is field 0 with fraction 0, and $0 \times 2^{k}$ is zero for any $k$. The exponent chosen for subnormals has no effect on whether zero exists.",
                            r"The two choices give different sets of values, and only one of them makes the spacing continuous across the seam. `bits_to_float(1)` must be $2^{-149}$; with −127 it would be $2^{-150}$, and the lab test catches that.",
                        ],
                        "why": r"""
Subnormals exist to fill the space between zero and the smallest normal with the same
spacing the normals have there, $2^{-149}$. That only works if the subnormal family ends
one step below $1.0 \times 2^{-126}$, which requires its exponent to be −126: the
fraction of all ones then gives $(2^{23} - 1) \times 2^{-149}$, exactly one step short.
Use −127 and the subnormals end near $2^{-127}$, leaving a gap of about four million
steps where the number line suddenly becomes coarse. The uniform-looking `field - 127`
is the mistake to avoid: field 0 and field 1 share an exponent, and what differs between
them is the implicit bit.
""",
                    },
                    {
                        "q": r'''
The scaled significand of 0.1 comes out as 13421772.8, which rounds to 13421773. If some
value's scaled significand came out as exactly 13421772.5, a tie, IEEE-754 rounds it to
13421772. Why does the standard send ties this way rather than always up?
''',
                        "opts": [
                            "Rounding every tie upward pushes the errors of a long sum in one direction; ties to even split them so they cancel",
                            "Rounding up on a tie would need one more bit of significand to hold the carried value, and there are only 23",
                            "Ties to even produces the exact result more often, since an even significand represents more decimal values",
                            "Rounding up is cheaper in hardware, but it breaks the round-trip identity that makes `bits_to_float` invert `float_to_bits`",
                        ],
                        "a": 0,
                        "whys": [
                            r"Half-up biases every tie upward, and a sum of many rounded values drifts. Sending ties to the even neighbour goes down about as often as up, so the drift averages out.",
                            r"Rounding up on a tie is an increment of the significand, which the encoder already handles when a fraction of all ones rounds up to $2^{24}$. Bit width is not the constraint.",
                            r"Both rules produce a representable value at the same distance from the true one on every tie; neither is more exact. The difference is the direction, and over many operations the direction is what accumulates.",
                            r"The round trip through `bits_to_float` is exact for any pattern under any rounding rule, because decoding involves no rounding at all. Half-up is not meaningfully cheaper, and the objection to it is statistical.",
                        ],
                        "why": r"""
A tie is a value sitting exactly between two representable neighbours, and either
neighbour is equally close. What matters is what happens over millions of such choices.
Always up gives every tie a positive error, and a long accumulation drifts upward by a
predictable amount. Sending ties to whichever neighbour has an even last bit chooses up
half the time and down half the time, and the drift cancels. This is why
`round_half_even` is the rule the lab supplies, and why the lab constructs ties on both
sides of `0x3F800001`: one must go down and one up.
""",
                    },
                    {
                        "q": r'''
A 32-bit `int` and a 32-bit `float` are each handed the value 16777217, which is
$2^{24} + 1$. Which is right?
''',
                        "opts": [
                            "The int holds it exactly; the float holds 16777216, because 24 significand bits cannot express the 25th",
                            "Both hold it exactly, because 16777217 is far below the 32-bit limit of either representation",
                            "The int holds it exactly; the float holds 16777218, because the tie goes to the even neighbour",
                            r"The float holds it exactly, since its range reaches $3.4 \times 10^{38}$; the int overflows past $2^{24}$",
                        ],
                        "a": 0,
                        "whys": [
                            r"16777217 is one more than $2^{24}$, so it needs a 1 at bit 24 and a 1 at bit 0: 25 significant bits. A binary32 has 24, and the number is rounded to a neighbour.",
                            r"The int limit is $2^{31} - 1$, and 16777217 is inside it. The float has no such limit on magnitude, but its precision is 24 bits, and this number needs 25 significant bits.",
                            r"The two neighbours are 16777216, with significand $2^{23}$, and 16777218, with significand $2^{23} + 1$. Evenness is judged on the stored significand, and the even one is the first, so the tie goes down to 16777216.",
                            r"The int limit is $2^{31} - 1$, and $2^{24}$ is well inside it. The float trades precision for range: above $2^{24}$ it can only hold even integers.",
                        ],
                        "why": r"""
The two types hold the same number of bits and spend them differently. The int spends
all 32 on magnitude, so any integer below $2^{31}$ is exact. The float spends 8 on an
exponent and keeps 24 for significant digits, so integers are exact only up to $2^{24}$;
above that the representable values are two apart, and 16777217 is a tie between
16777216 and 16777218. Ties go to the even significand, which is $2^{23}$ for 16777216,
so the float holds 16777216. The other neighbour is tempting because 16777218 is an even
integer, but evenness here is judged on the last stored bit, not on the decimal value.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "A form with fixed columns",
                    "minutes": 11,
                    "body": r'''
A telegram form from the days of the wire had ruled boxes: so many for the destination,
so many for the sender, one for the priority, and the rest for the message. A clerk could
pull the destination off any form without reading the message, because it was always in
the same boxes. CW-32 instruction words are forms of this kind. Every one is 32 bits, the
opcode is always bits 31 to 26, the first register field is always bits 25 to 21, and a
decoder can pull the opcode out of any word without knowing what the word does.

Take `ADD r2, r1, r1`. The opcode for `ADD` is 1, the destination is `r2`, and both
sources are `r1`. Put 1 in the opcode boxes, 2 in the `f1` boxes, 1 in `f2` and 1 in
`f3`, and the word is the number those boxes spell.

## From boxes to a number

A field that starts at bit $p$ and holds the value $v$ contributes $v \times 2^p$ to the
word, for the same reason the hundreds digit of 372 contributes $3 \times 100$.
Positional notation does not care that the digits here are five and six bits wide. So
the word for `ADD r2, r1, r1` is

$$1 \times 2^{26} + 2 \times 2^{21} + 1 \times 2^{16} + 1 \times 2^{11}.$$

Shifting left by $p$ is multiplication by $2^p$, and because the fields do not overlap,
OR-ing the shifted fields together is the same as adding them.

```python
OPCODE_ADD = 1
rd, rs, rt = 2, 1, 1
word = (OPCODE_ADD << 26) | (rd << 21) | (rs << 16) | (rt << 11)
print(f"0x{word:08X}")
print(f"{word:032b}")
# reading a field back: shift it down to bit 0, then mask to its width
print(word >> 26, (word >> 21) & 31, (word >> 16) & 31, (word >> 11) & 31)
```

`0x04410800`, and the four fields read back as `1 2 1 1`. The mask `31` is `0b11111`,
five ones, which is why a register field can hold 0 to 31 and no more: 32 registers is
not a design taste, it is what five bits can name. Six opcode bits give 64 opcodes; CW-32
uses fourteen and leaves fifty for whoever extends it. In the register form, bits 10 to 0
are not used at all. Eleven bits in every arithmetic instruction carry nothing, and that
waste is deliberate: a fixed-width word makes fetch trivial, since instruction $n$ is
always word $n$, and the decoder never has to work out where an instruction ends.

## The ISA is the contract

The layout above is part of an instruction set architecture, and an ISA is a contract
with two parties. The compiler writer, or the assembler writer, promises to emit only
words in this layout; the hardware designer promises that a word in this layout will do
what the table says. Neither needs to see the other's work. That is what lets a program
assembled today run on a processor designed next year, and it is why changing the
layout, even to fix an ugliness, breaks every binary ever produced.

The contract has to say what an address is. CW-32 is word-addressed: memory is an array
of 32-bit words, address 7 is the eighth word, and `LW r4, 1(r5)` loads the word after
the one `r5` points at. Most machines you will meet are byte-addressed, where address 7
is the eighth byte and a word occupies four addresses. There, an offset of 1 would point
into the middle of a word, and the assembler for such a machine has to write `4(r5)` to
mean the next word. The number in the instruction is the same kind of number; what it
counts depends on the contract.

## Sixteen bits of immediate

The immediate form has no `f3`; bits 15 to 0 hold a constant. Sixteen bits hold 65536
patterns, and the contract says the CPU sign-extends the field when it decodes it, so
the pattern `0xFFFF` is read as $-1$ and the field covers $-32768$ to $32767$. The
assembler stores `imm & 0xFFFF`, which for a negative number is its sixteen-bit
two's-complement pattern from the previous module.

```python
for imm in (5, -1, 65535, 40000, -25536):
    field = imm & 0xFFFF
    back = field - 0x10000 if field >= 0x8000 else field
    print(f"{imm:7d} -> field 0x{field:04X} -> the CPU reads {back:7d}")
```

`-1` and `65535` produce the same field and the same instruction: the lab's assembler
accepts both spellings, which is why its range is $-32768$ to $65535$ rather than the
signed range alone. But look at `40000`. It is inside the accepted range, it assembles
without complaint, and the CPU reads it as $-25536$. Two spellings of one pattern is a
convenience; a positive number that turns negative is a trap, and the contract here
lets it through. Knowing what your assembler accepts and what the hardware then does
with it is the whole job.

What the assembler must never do is mask before it checks. `70000 & 0xFFFF` is `4464`,
a number that looks like a perfectly good immediate and is not what anyone wrote. The
brief's phrase for this is "never a silent wrong word", and the range check has to run
on the value before the mask runs on it.

```python
imm = 70000
print(hex(imm & 0xFFFF), imm & 0xFFFF)     # 0x1170 4464: plausible, wrong, and silent
```

## Labels, and why one pass is not enough

Here is the loop from the lab, summing 1 to 10.

```asm
        ADDI r1, r0, 0        ; total
        ADDI r2, r0, 1        ; i
        ADDI r3, r0, 11       ; limit
loop:   BEQ  r2, r3, done
        ADD  r1, r1, r2
        ADDI r2, r2, 1
        JMP  loop
done:   SW   r1, 0(r0)
        HALT
```

Branch targets in CW-32 are absolute word addresses, so `BEQ r2, r3, done` needs the
number of the word `done` labels. Walk the source top to bottom emitting words as you
go and you reach the `BEQ` at address 3 with `done` still unseen: it is a forward
reference, and its address depends on how many instructions sit between here and there.
A single pass cannot know that. So the assembler makes two: the first counts addresses
and records where each label lands, the second emits words with every label already
known.

The first pass has one rule that people get wrong: a label names the address of the
*next instruction*, and only instructions consume addresses. Blank lines, comment-only
lines and a label sitting alone on a line take none.

```python
lines = [
    "; header",
    "start: ADDI r1, r0, 5",
    "",
    "  ADD r2, r1, r1",
    "end:",
    "  HALT",
]
labels = {}
address = 0
for raw in lines:
    text = raw.split(";")[0].strip()
    if ":" in text:
        name, _, text = text.partition(":")
        labels[name.strip()] = address        # the address of whatever comes next
        text = text.strip()
    if text:                                  # only a real instruction moves the counter
        address += 1
print(labels)                                 # {'start': 0, 'end': 2}
print("instructions:", address)               # 3
```

`end` is on line 5 of the source, counting from 1, and labels address 2, the `HALT`.
The tempting shortcut is to use the line number, or to add one to the counter on every
line that is not blank; both give `end` an address that points at nothing, and the
branch to it lands one word off. It is tempting because for a source with no comments,
no blank lines and no lone labels the shortcut gives the right answer, and the first
program anyone assembles usually looks like that. The bug then makes a loop run once too
often, and is very hard to see in the hex.

For the loop above, the first pass finds `loop` at 3 and `done` at 7. The second pass
then encodes `BEQ r2, r3, done` as opcode 10, `f1` = 2, `f2` = 3, immediate 7, and
`JMP loop` as opcode 12 with immediate 3.

```python
OPCODES = {"BEQ": 10, "JMP": 12}
labels = {"loop": 3, "done": 7}
beq = (OPCODES["BEQ"] << 26) | (2 << 21) | (3 << 16) | (labels["done"] & 0xFFFF)
jmp = (OPCODES["JMP"] << 26) | (labels["loop"] & 0xFFFF)
print(f"0x{beq:08X} 0x{jmp:08X}")            # 0x28430007 0x30000003
```

Those two words are what the lab's sample-program test checks at positions 3 and 6.

## The zero register and the instructions that do not exist

`r0` reads as zero whatever is written to it. That costs one register out of 32 and buys
a whole family of instructions for free. There is no `MOV` in CW-32, but
`ADD r1, r2, r0` copies `r2` into `r1`. There is no load-immediate, but
`ADDI r1, r0, 5` puts 5 in `r1`. There is no unconditional branch-on-register, but
`BEQ r0, r0, target` always jumps. An assembler can offer these as pseudo-instructions,
spellings that expand to real words, and the hardware never learns they exist.

```python
OPCODES = {"NOP": 0, "ADD": 1, "ADDI": 7}

def encode(op, f1=0, f2=0, f3=0, imm=None):
    word = (OPCODES[op] << 26) | (f1 << 21) | (f2 << 16)
    return word | (f3 << 11) if imm is None else word | (imm & 0xFFFF)

print(hex(encode("ADD", 1, 2, 0)))         # MOV r1, r2   is  ADD r1, r2, r0
print(hex(encode("ADDI", 1, 0, imm=5)))    # LI r1, 5     is  ADDI r1, r0, 5
print(encode("NOP") == 0)                  # the all-zero word does nothing, by design
```

Opcode 0 being `NOP` is also deliberate: memory that was never written reads as zeros,
and a processor that wanders into it does nothing rather than something.

## Where this layout stops being typical

CW-32 was designed to be assembled in an afternoon, and three of its choices are
unusual. Real RISC branches are PC-relative: the field holds the distance from the
instruction after the branch, so code can be loaded anywhere without re-assembly, and
the second pass has to know its own address to compute `target - (address + 1)`. Real
immediates are often split across the word, as in RISC-V, where the store instruction's
immediate lives in two separate fields so that the register fields can stay in the same
place for every format; the assembler cuts the constant in two and the decoder glues it
back. And x86 has no fixed width at all: instructions run from one byte to fifteen, and
the decoder has to read the first bytes to learn how many more there are. The two-pass
structure survives all of these. The field arithmetic does not.

The lab **A two-pass assembler for CW-32** asks for `strip_comment`, `parse_register`,
`parse_mem`, `first_pass` and `assemble`, with every failure raised as `AsmError`. The
tests feed it an unknown mnemonic, a label that is never defined, an instruction with
the wrong number of operands, and immediates of 70000 and $-40000$; each has to be
refused, and none may become a word.
''',
                },
            ],
            "quiz": {
                "title": "Fields, labels and the words an assembler must refuse",
                "minutes": 8,
                "questions": [
                    {
                        "q": r'''
The word `0x04410800` is `0000 0100 0100 0001 0000 1000 0000 0000` in binary. Using the
CW-32 layout, with the opcode in bits 31 to 26 and three 5-bit register fields whose
top bits are 25, 20 and 15, which instruction is it?
''',
                        "opts": [
                            "`ADD r2, r1, r1`: opcode 1, then the fields 2, 1 and 1 read downward from bit 25",
                            "`ADD r1, r2, r1`: opcode 1, with the destination in the second field as MIPS has it",
                            "`ADDI r2, r1, 2048`: opcode 1, with the low sixteen bits `0x0800` read as an immediate",
                            "`ADD r1, r1, r2`: opcode 1, with the fields read upward from bit 11 as rd, rs and rt",
                        ],
                        "a": 0,
                        "whys": [
                            r"Bits 25 to 21 are 00010, bits 20 to 16 are 00001 and bits 15 to 11 are 00001; the layout puts rd first, so the destination is r2 and both sources are r1.",
                            r"MIPS puts rd in the third register field, but CW-32 is its own contract: the table says f1 is rd for every register-form instruction. Reading another ISA's layout into this word transposes the fields.",
                            r"Opcode 1 is ADD, and ADD uses the register form, so bits 15 to 11 are the rt field and bits 10 to 0 are unused. `0x0800` is rt = 1 shifted to bit 11, not an immediate.",
                            r"The fields are read from the top of the word down: f1 at bits 25 to 21 is the highest-placed register field and is rd. Reading upward from bit 11 hands the destination to the rt position.",
                        ],
                        "why": r"""
Peel the fields from the top. The top six bits are 000001, opcode 1, ADD. The next five
are 00010, so f1 is 2; then 00001 and 00001, so f2 and f3 are both 1. The table says
ADD's fields are rd, rs, rt in that order, giving `ADD r2, r1, r1`. The bits below 11
are zero because the register form does not use them. The layout is a contract specific
to this ISA, and the moment you carry MIPS's field order over, or read the bottom
sixteen bits as an immediate because they are non-zero, the same bits spell a different
instruction.
""",
                    },
                    {
                        "q": r'''
`first_pass` is given these six lines, one per list element:

```text
; header
start: ADDI r1, r0, 5

  ADD r2, r1, r1
end:
  HALT
```

What address does `end` map to, and why?
''',
                        "opts": [
                            "2, the address of `HALT`: a label names the next instruction, and only instructions consume addresses",
                            "4, its zero-based line number: labels are positions in the source, and the source is what a branch targets",
                            "3, because the comment line takes no address but the blank line and the label line each take one",
                            "5, because a label on its own line is an instruction of length one, an empty slot the branch lands on",
                        ],
                        "a": 0,
                        "whys": [
                            r"The comment, the blank line and the lone label consume nothing. Addresses go to `ADDI` (0), `ADD` (1) and `HALT` (2), and `end` names whatever instruction comes next, which is `HALT`.",
                            r"Line numbers count source lines, and a branch target has to be a word address in the assembled program. The header comment and the blank line are not in the program at all.",
                            r"A blank line has nothing to assemble and a lone label has nothing to assemble; neither produces a word. Counting them puts `end` one past `HALT`, where a branch would run off the program.",
                            r"A label produces no word; it is a name for the address of the word that follows. If it took a slot, every label would insert a NOP into the program and shift every address after it.",
                        ],
                        "why": r"""
The first pass keeps a counter that advances only when a line still has an instruction
on it after comments and labels are stripped. The header comment and the blank line
leave nothing, the `end:` line leaves nothing, so the counter goes 0 for `ADDI`, 1 for
`ADD`, and `end` is recorded as 2, the address `HALT` will take. Using line numbers, or
counting every non-empty line, gives a label an address that points at nothing, and a
branch to it lands one word off. That is the lab test named `first_pass places labels
at the next instruction`, which expects `{'start': 0, 'end': 2}`.
""",
                    },
                    {
                        "q": r'''
Why does the assembler need two passes over the source rather than one?
''',
                        "opts": [
                            "A branch may name a label defined further down, whose address is unknown until the instructions before it are counted",
                            "Syntax has to be checked on every line before any word is emitted, so that an error late in the file emits nothing at all",
                            "Labels must be collected and sorted by address so that the second pass can look each one up with a binary search",
                            "Immediates are range-checked in the first pass and masked in the second, and the two steps cannot share one loop",
                        ],
                        "a": 0,
                        "whys": [
                            r"`BEQ r2, r3, done` at address 3 needs the address of `done`, which is 7, and 7 is only known once the instructions between have been counted. One pass reaches the branch before it knows.",
                            r"Checking before emitting is a property of the lab's design, not the reason for two passes: a single pass could check and emit each line together and discard the output on error. Forward references are what one pass cannot resolve.",
                            r"A dict lookup needs no sorting, and the assembler uses one. The second pass exists because the dict has to be complete before the first branch is encoded, not because of how it is searched.",
                            r"Range-checking and masking happen together in the second pass, in `fit_immediate`, on the same value. Neither has anything to do with the first pass, which only counts addresses and records labels.",
                        ],
                        "why": r"""
The whole reason is the forward reference. Encoding `BEQ r2, r3, done` requires the
word address of `done`, and that depends on how many instructions lie between the branch
and the label, which a top-to-bottom pass has not yet seen. So the first pass counts and
records, and the second encodes with the complete map in hand. Everything else,
checking, sorting, masking, could be done in one pass and is arranged the way it is for
tidiness. A single-pass assembler is possible with backpatching, going back to fix up
each branch once its label appears, but two passes is the simpler contract.
""",
                    },
                    {
                        "q": r'''
The assembler accepts `ADDI r1, r0, 65535` and emits a word with the immediate field
`0xFFFF`. When the CW-32 processor executes it, what does `r1` hold?
''',
                        "opts": [
                            "−1: the CPU sign-extends the sixteen-bit field, and `0xFFFF` is the pattern of −1",
                            "65535: the assembler accepted the number, so the field holds it and the processor adds it",
                            "32767: a sixteen-bit signed field saturates at its maximum, dropping the excess",
                            "Nothing; the assembler should have raised `AsmError`, since 65535 is above the signed limit",
                        ],
                        "a": 0,
                        "whys": [
                            r"The immediate is stored as a pattern and read back sign-extended, so `0xFFFF` becomes 32 bits of ones, which is −1. `65535` and `-1` are two spellings of the same instruction.",
                            r"The assembler accepts a range wider than the signed one on purpose, so that a pattern can be written either way. What the processor does with the pattern is the ISA's business, and the ISA says sign-extend.",
                            r"Nothing saturates; there is no logic for it. The field holds a pattern of sixteen bits, and every pattern denotes some value between −32768 and 32767 once sign-extended.",
                            r"The brief sets the accepted range at −32768 to 65535, and 65535 is inside it. The assembler is right to accept it; the surprise lives in what the value means once decoded.",
                        ],
                        "why": r"""
The contract has two halves. The assembler's half says the immediate field is
`imm & 0xFFFF` and that anything from −32768 to 65535 is acceptable, so `65535` becomes
`0xFFFF` without complaint. The processor's half says the sixteen-bit field is
sign-extended in decode, so `0xFFFF` is read as −1 and `r1` becomes −1. The same is true
of `40000`, which reads back as −25536: a positive number accepted by the assembler and
turned negative by the hardware. Knowing which range your assembler accepts and what the
hardware does with the pattern is the whole of this module's warning about immediates.
""",
                    },
                    {
                        "q": r'''
`LW r4, 1(r5)` executes with `r5` holding 20. On CW-32, which is word-addressed, which
word is loaded, and what would the same offset mean on a byte-addressed 32-bit machine?
''',
                        "opts": [
                            "Word 21 here; on a byte-addressed machine, byte 21, which is a quarter of the way into a word",
                            "Word 21 here; on a byte-addressed machine the hardware scales the offset by four, so byte 84, word 21",
                            "Word 24 here, because a word address is the register plus four times the offset; on a byte machine, byte 21",
                            "Word 21 on both machines, since a load offset counts whole words whatever the addressing",
                        ],
                        "a": 0,
                        "whys": [
                            r"On CW-32 the effective address is `regs[f2] + imm`, 21, and memory is an array of words, so word 21. On a byte-addressed machine 21 is a byte address, and word boundaries sit at multiples of four.",
                            r"Ordinary RISC machines add the offset as written and leave scaling to the assembler; that is why their assembly says `4(r5)` for the next word. A machine that scaled offsets would be a different contract, not the usual one.",
                            r"CW-32 adds the offset as it stands: 20 + 1 = 21. Multiplying the offset by four is a byte-machine habit that the programmer, not the hardware, performs, and it does not apply to a word-addressed machine at all.",
                            r"What an offset counts is part of the ISA contract. On a byte-addressed machine the number 21 names a byte, and the word beginning at byte 20 is the only one nearby that a 32-bit load can legitimately fetch.",
                        ],
                        "why": r"""
The address computed is the same number on both machines: 20 + 1 = 21. What differs is
what 21 names. On CW-32 memory is a list of words and 21 is the twenty-second word. On a
byte-addressed machine 21 is a byte, the word that contains it starts at 20, and a load
from 21 is misaligned; machines either trap or fetch from 20, depending on their rules.
To load the next word on such a machine you write `4(r5)`, and it is the programmer or
the compiler that supplies the four. The lab's `parse_mem` and the simulator never
multiply the offset, because in a word-addressed ISA there is nothing to multiply by.
""",
                    },
                    {
                        "q": r'''
A learner's `fit_immediate` is written as `return value & 0xFFFF`, with no range check.
Which of these lines assembles without error into a word that does something other than
what the line says?
''',
                        "opts": [
                            "`ADDI r1, r0, 70000`, which becomes an add of 4464 with no complaint from anyone",
                            "`ADDI r1, r0, -1`, whose field `0xFFFF` the processor will read back as 65535",
                            "`SW r4, -8(r5)`, whose negative offset cannot be stored in an unsigned field",
                            "`ADDI r1, r0, 65535`, which the proper assembler rejects but the bare mask lets through",
                        ],
                        "a": 0,
                        "whys": [
                            r"70000 is `0x11170`; the mask keeps `0x1170`, which is 4464. The word is well-formed, the processor executes it, and nothing anywhere records that the programmer wrote 70000.",
                            r"`-1 & 0xFFFF` is `0xFFFF`, and the processor sign-extends it back to −1. This is the intended encoding of a negative immediate, and the instruction does what it says.",
                            r"`-8 & 0xFFFF` is `0xFFF8`, the sixteen-bit pattern of −8, which decode sign-extends to −8. Negative offsets are ordinary; the lab test on loads, stores and negative immediates has one.",
                            r"The brief's range is −32768 to 65535, so a proper assembler accepts 65535 and emits `0xFFFF`, the same word as for −1. The mask does the same thing here; nothing has gone wrong on that line.",
                        ],
                        "why": r"""
Masking is the correct last step for every immediate that fits in sixteen bits: negative
values become their two's-complement pattern, and the processor reads the pattern back.
It is the wrong first step for a value that does not fit, because `& 0xFFFF` throws away
the high bits and keeps a plausible-looking remainder. 70000 becomes 4464, the program
assembles, and the error is invisible until the results are wrong. That is the silent
wrong word the brief warns about, and it is why the range check has to run before the
mask, on the original value.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "What one tick of the clock does",
                    "minutes": 12,
                    "body": r'''
Picture a clerk at a desk. In front of the clerk is a tray of numbered cards, one
instruction per card; a slip of paper with a single number on it, the card to read next;
a rack of 32 pigeonholes, each holding one 32-bit number; and, across the room, a filing
cabinet with 64 drawers. Every tick of a clock the clerk does the same thing. Read the
card whose number is on the slip. Look at which pigeonholes it names and take their
contents out. Do the arithmetic it asks for. If it says so, walk to the cabinet and read
or write one drawer. Put the result in the pigeonhole it names. Write the number of the
next card on the slip. Then wait for the next tick.

That loop is the whole of a processor. The slip is the program counter, the pigeonholes
are the register file, the cards are instruction memory, the cabinet is data memory,
and the five things the clerk does are the five stages every architecture book names:
fetch, decode, execute, memory, write-back. Nothing in the loop knows what the program
is for. It reads a card and does what the card says, and the meaning of the program is
in the sequence of cards, not in the clerk.

## The program counter is the only thing that moves

Nothing on the desk decides where the program goes except the slip. After most cards,
the clerk writes the current number plus one. A branch card says: compare two
pigeonholes, and if they match, write this other number instead. A jump card says: write
this other number. That is all control flow is. There is no separate mechanism for loops
or calls; there is one register that holds the next address, a default rule for updating
it, and a handful of instructions that override the default.

That framing gives the simulator a clean shape. Compute `next_pc = pc + 1` before
looking at the instruction, let a taken branch or a jump overwrite it, and store it once
at the end of the step. The tempting alternative is to write `self.pc += 1` inside every
branch of the big `if` chain, and it is tempting because each case then looks complete
on its own. Forget it in one of them, and a `NOP` that does not advance the counter runs
forever.

## Decoding: one word, five fields, one sign extension

The assembler put the fields in known places, so taking them out is the shift-and-mask
from the previous module in reverse. One field needs more than a mask. The 16-bit
immediate was stored as a pattern, and the register it will be added to is 32 bits wide.
The pattern `0xFFFF` has to become the 32-bit $-1$, not the 32-bit $65535$: sign
extension, done once, in decode, so that every consumer of the immediate sees the same
value.

```python
word = (7 << 26) | (6 << 21) | (6 << 16) | (-1 & 0xFFFF)   # ADDI r6, r6, -1
field = word & 0xFFFF
print(hex(field))                                          # 0xffff
unsigned_reading = field
signed_reading = field - 0x10000 if field & 0x8000 else field
print(10 + unsigned_reading, 10 + signed_reading)          # 65545 9
```

A simulator that skips the sign extension turns a countdown loop into a climb through
65545, 131080 and onward, and the bug does not show for small positive immediates, which
is why it survives the first three tests. In hardware the extension is not even logic:
bit 15 is wired to bits 16 through 31 of the ALU input, sixteen copies of one wire.

## The register file, and the pigeonhole that is glued shut

Thirty-two registers are a list of 32 integers. The hardware keeps each one at 32 bits,
so a simulator has to keep them there too: $2147483647 + 1$ in a register is
$-2147483648$, not $2147483648$, and Python will not do that for you.

```python
def to_signed32(value):
    value &= 0xFFFFFFFF
    return value - (1 << 32) if value >> 31 else value

print(to_signed32(2147483647 + 1))     # -2147483648: the register wrapped
print(to_signed32(0xFFFFFFFF))         # -1
print(2147483647 + 1)                  # 2147483648: Python did not
```

Register 0 is glued shut. Reads return 0 and writes are dropped. In hardware that is a
register with no write-enable wire; in a simulator it is one guard in one place. The
mistake is to put the guard in `step`, next to the `ADDI` case, and then forget it in
the `LW` case, where a load into `r0` quietly makes zero into something else and every
`ADDI r1, r0, 5` after it goes wrong. Route every write through one method and the
guard lives there.

## Tracing the loop, and where 46 comes from

The lab's program sums 1 to 10, and the brief promises it takes exactly 46 steps. That
number is worth deriving before you run anything, because a simulator that reports 45 or
47 has a specific bug, and knowing which count corresponds to which bug is faster than
reading the code.

```text
step  pc  instruction          effect
   1   0  ADDI r1, r0, 0       r1 = 0
   2   1  ADDI r2, r0, 1       r2 = 1
   3   2  ADDI r3, r0, 11      r3 = 11
   4   3  BEQ  r2, r3, 7       1 != 11: not taken, pc -> 4
   5   4  ADD  r1, r1, r2      r1 = 1
   6   5  ADDI r2, r2, 1       r2 = 2
   7   6  JMP  3               pc -> 3
   8   3  BEQ  r2, r3, 7       2 != 11: not taken
   ...
```

Three set-up instructions run once. Each trip round the loop, with `r2` from 1 to 10,
runs the not-taken `BEQ`, the `ADD`, the `ADDI` and the `JMP`: four instructions, ten
times. Then `r2` reaches 11, the `BEQ` is taken, and `SW` and `HALT` finish.

```python
setup = 3                 # ADDI, ADDI, ADDI
per_iteration = 4         # BEQ not taken, ADD, ADDI, JMP
iterations = 10           # r2 runs 1..10
exit_check = 1            # the BEQ that is finally taken
tail = 2                  # SW, HALT
print(setup + per_iteration * iterations + exit_check + tail)   # 46
print(sum(range(1, 11)))                                        # 55, what r1 holds
```

A count of 45 means the taken `BEQ` or the `HALT` was not counted as a step; the brief
says `HALT` sets the flag *and* counts. A count of 42 means the loop ran nine times,
which is a `BEQ` comparing the wrong registers or an immediate off by one.

## Control is a function of the opcode

Between decode and execute the datapath has to be told what to do: whether the ALU's
second input is a register or the immediate, whether data memory is read, written or
left alone, whether the result goes back to the register file, whether the PC might be
overridden. In a single-cycle design every one of those signals is a pure function of
the six opcode bits. There is no state in the control unit and no memory of the last
instruction; the opcode goes in and the settings come out, and a table is a complete
specification of it.

```python
CONTROL = {
    #        RegWrite ALUSrc MemRead MemWrite Branch Jump
    "ADD":  (True,  False, False, False, False, False),
    "ADDI": (True,  True,  False, False, False, False),
    "LW":   (True,  True,  True,  False, False, False),
    "SW":   (False, True,  False, True,  False, False),
    "BEQ":  (False, False, False, False, True,  False),
    "JMP":  (False, False, False, False, False, True),
}
NAMES = ("RegWrite", "ALUSrc", "MemRead", "MemWrite", "Branch", "Jump")
for op, signals in CONTROL.items():
    on = [name for name, bit in zip(NAMES, signals) if bit]
    print(f"{op:5s} {' '.join(on)}")
```

`LW` and `SW` both use the immediate as the ALU's second input, because the address is
`regs[f2] + imm` and the ALU is the adder that computes it; `SW` is the only one of the
six that writes nothing back. A simulator does not need the table, because the `if`
chain in `step` *is* the table, one row per opcode. But it is the reason the chain can
be flat: no case needs to know what the previous instruction was.

## One instruction per cycle, and why that is slow

The single-cycle machine retires one instruction every clock tick, so its CPI is 1, and
it is tempting to read that as the fastest a processor can be. The catch is the length
of the tick. The clock has to be long enough for the slowest instruction to finish, and
the slowest is `LW`, which passes through all five stages: fetch from instruction
memory, read the register file, add in the ALU, read data memory, write the register
file. Everything else waits the same time whether it needs it or not.

```python
STAGE_PS = {"fetch": 200, "regread": 100, "alu": 200, "memory": 200, "regwrite": 100}
PATH = {
    "ADDI": ("fetch", "regread", "alu", "regwrite"),
    "ADD":  ("fetch", "regread", "alu", "regwrite"),
    "BEQ":  ("fetch", "regread", "alu"),
    "JMP":  ("fetch",),
    "SW":   ("fetch", "regread", "alu", "memory"),
    "LW":   ("fetch", "regread", "alu", "memory", "regwrite"),
    "HALT": ("fetch",),
}
MIX = {"ADDI": 13, "BEQ": 11, "ADD": 10, "JMP": 10, "SW": 1, "HALT": 1}   # the 46 steps by type

latency = {op: sum(STAGE_PS[s] for s in path) for op, path in PATH.items()}
clock = max(latency.values())
print("clock period:", clock, "ps, set by", max(latency, key=latency.get))
print("single-cycle total:", clock * sum(MIX.values()), "ps")
print("if each instruction took only its own time:", sum(latency[op] * n for op, n in MIX.items()), "ps")
```

With these made-up but realistically proportioned delays, the clock is 800 ps because
`LW` needs 800 ps, and the 46-step program takes 36800 ps. The program contains no `LW`
at all. Ten of its steps are `JMP`, which is finished after 200 ps and then sits idle for
600. If each instruction could take only its own time the total would be 22200 ps, and
that gap is the argument for every design after this one: a multicycle machine that
gives each instruction the number of ticks it needs, and then the pipeline in this
course's capstone, which overlaps the stages of five instructions so that the tick is one
stage long rather than five.

## Refusing to execute nonsense

A real processor that fetches a word with no valid opcode raises an illegal-instruction
trap, and one that addresses memory it does not have raises a fault. The alternative,
doing something arbitrary and carrying on, is how a wild jump into data becomes a
machine that appears to be working while producing garbage. The simulator has the same
choice and should make the same one: `decode` raises `ValueError` for an opcode outside
the table, `load` and `store` raise `IndexError` for an address outside memory, and
`step` raises `IndexError` when the PC has left the program.

```python
# raises ValueError
NAMES = {0: "NOP", 1: "ADD", 13: "HALT"}

def opcode_name(word):
    code = word >> 26
    if code not in NAMES:
        raise ValueError(f"unknown opcode {code}")
    return NAMES[code]

print(opcode_name(13 << 26))     # HALT
print(opcode_name(40 << 26))     # opcode 40 names nothing: refuse it rather than guess
```

Stepping a halted machine is an error for the same reason, and `run` takes a
`max_steps` so that a program with a `JMP` to itself ends in a `RuntimeError` instead of
a frozen tab. Every one of these is a case where the honest answer is "this is not a
program", and saying so is worth more than any value the machine could invent.

## What the model leaves out

Instruction memory and data memory are separate lists here, and each responds within
the cycle. Real machines have one memory holding both, which is why a jump into data is
possible at all, and it answers in hundreds of cycles rather than a fraction of one; the
next module is about the caches that hide that. The `steps` counter is a count of
instructions, not of time, and the timing block above is the only place in this module
where the two are told apart. And the machine has no interrupts, no privilege levels,
and no way to be stopped from outside: it runs until `HALT` or until it breaks.

The lab **A single-cycle CW-32 simulator** asks for `to_signed32`, `decode`, and a
`CPU` class with `write`, `load`, `store`, `step` and `run`. `decode` sign-extends the
immediate once; `write` protects `r0` once; `step` computes `next_pc` first and lets
branches override it. The sample program must halt after exactly 46 steps with `r1` and
`mem[0]` both holding 55.
''',
                },
            ],
            "quiz": {
                "title": "One tick at a time",
                "minutes": 8,
                "questions": [
                    {
                        "q": r'''
The sample program sets `r3` to 11 and halts after 46 steps. If the limit were 21
instead, so that the loop sums 1 to 20, how many steps would `run()` report?
''',
                        "opts": [
                            "86: three set-up steps, twenty trips of four, the taken branch, and the store and halt",
                            "92: doubling the limit doubles the work, so the 46 steps of the original become 92",
                            "83: three set-up steps and twenty trips of four, with nothing further left to count",
                            "90: twenty-one trips of four, since the branch runs once per limit value, plus six others",
                        ],
                        "a": 0,
                        "whys": [
                            r"The loop body runs for `r2` from 1 to 20, twenty times, at four instructions each; add the three set-up instructions, the final taken `BEQ`, the `SW` and the `HALT`: 3 + 80 + 1 + 2 = 86.",
                            r"The set-up, the exit check and the tail run once regardless of the limit. Only the four-per-iteration part scales, from 40 to 80, so the total goes from 46 to 86, not to 92.",
                            r"The taken `BEQ` is a step: it is fetched, decoded and executed, and it changes the PC. So are the `SW` and the `HALT`. Leaving them out gives 83, which is three short.",
                            r"The `BEQ` runs 21 times, but twenty of those are inside the four-instruction loop body and one is the exit. Counting 21 full trips of four treats the exit branch as a whole iteration.",
                        ],
                        "why": r"""
Break the count into parts that scale and parts that do not. Three set-up instructions
run once. The loop body, a not-taken `BEQ`, the `ADD`, the `ADDI` and the `JMP`, runs
once per value of `r2` from 1 to the limit minus one: twenty times for a limit of 21, so
80 steps. Then the `BEQ` that is finally taken, the `SW` and the `HALT`, three more. The
total is 86. The same decomposition gives 46 for the lab's limit of 11, and a simulator
that reports 45 or 42 for the original program has dropped a specific one of those
parts.
""",
                    },
                    {
                        "q": r'''
Where should the 16-bit immediate be sign-extended to 32 bits, and why there?
''',
                        "opts": [
                            "In decode, once, so that arithmetic, address calculation and the branch target all see one 32-bit value",
                            "In the ALU, only for `ADDI` and `SUB`, since loads and stores use the immediate as an unsigned offset",
                            "In the assembler, by emitting a 32-bit immediate, so that the processor never has to extend anything",
                            "Nowhere: the field is stored as `imm & 0xFFFF`, so it is an unsigned quantity by definition and stays one",
                        ],
                        "a": 0,
                        "whys": [
                            r"The immediate feeds the adder for `ADDI`, the address adder for `LW` and `SW`, and the next-PC for branches. Extending it in decode means every one of them receives the same value and none of them can forget.",
                            r"`LW r1, -8(r30)` is a legal instruction and the lab tests it; offsets are signed. Extending only for some opcodes is both a special case to maintain and wrong for the loads and stores.",
                            r"The word is 32 bits with 16 already spent on opcode and registers. There is no room for a 32-bit immediate in the fixed-width format; the field is 16 bits, and extension is the hardware's job.",
                            r"The field is stored as a pattern, and the contract says the pattern is read as a signed value. `0xFFFF` denotes −1, and a simulator that treats it as 65535 turns every countdown into a climb.",
                        ],
                        "why": r"""
The immediate is a sixteen-bit pattern whose meaning is a signed value, and it is
consumed by several parts of the datapath. Sign-extend it once, in decode, and every
consumer receives the same 32-bit number; in hardware that extension is wires, bit 15
fanned out to the sixteen upper positions. Extending it in some cases and not others is
the bug the lab's `decode` test is written to catch, with `imm=-1` expected to come back
as −1 and `32767` as itself. The assembler cannot help, because the field is sixteen
bits wide and no wider.
""",
                    },
                    {
                        "q": r'''
A program runs `ADDI r0, r0, 99` and then `ADD r1, r0, r0`. When it halts, what does
`r1` hold?
''',
                        "opts": [
                            "0, because the write to `r0` was dropped and both operands of the `ADD` read as zero",
                            "99, because the first instruction stored 99 in `r0` and the second copied it across",
                            "198, because `r0` held 99 after the first instruction and the `ADD` summed it with itself",
                            "Nothing; the simulator raises an error, since writing to `r0` is an illegal instruction",
                        ],
                        "a": 0,
                        "whys": [
                            r"`r0` is hardwired: writes to it are discarded and reads return 0. The `ADDI` had no effect, and 0 + 0 went into `r1`.",
                            r"The write to `r0` never landed. In hardware there is no write-enable for register 0; in the simulator, `write` skips index 0. Nothing was there to copy.",
                            r"Doubling 99 assumes the 99 was stored. It was not; the register file's zero slot cannot be written, so the `ADD` summed two zeros.",
                            r"Writing to `r0` is legal and common; `ADDI r0, r0, 0` is a standard way to spell a no-op. The ISA drops the write rather than trapping it, and the lab test on the zero register expects exactly that.",
                        ],
                        "why": r"""
Register 0 is the one pigeonhole that is glued shut. Instructions may name it as a
destination, and pseudo-instructions depend on being able to, but the write is dropped;
reads always return zero. So `ADDI r0, r0, 99` does nothing and `ADD r1, r0, r0` writes
0 + 0 into `r1`. The lab's hint is to route every register write through one method
that skips index 0, because the mistake that survives longest is guarding `ADDI` and
forgetting `LW`.
""",
                    },
                    {
                        "q": r'''
The stage delays are fetch 200 ps, register read 100, ALU 200, data memory 200 and
register write 100. `LW` uses all five and sets the clock at 800 ps. Suppose the ISA
dropped `LW`, so that the slowest remaining instruction is `SW`. What happens to the
single-cycle machine?
''',
                        "opts": [
                            "The clock period falls to 700 ps, the time `SW` needs, and every instruction now takes 700 ps",
                            "The clock period stays at 800 ps, because it is the sum of the five stage delays whatever instructions exist",
                            "The clock period falls to 600 ps, since arithmetic instructions dominate the mix and so set the pace",
                            "Nothing changes, because CPI is 1 either way and CPI is what determines the execution time",
                        ],
                        "a": 0,
                        "whys": [
                            r"The period is set by the longest path any instruction takes. Remove the longest and the next longest, `SW` at fetch + read + ALU + memory = 700 ps, sets it. Every instruction still waits the whole period.",
                            r"The period is the longest path through the datapath that some instruction actually uses, not the sum of everything that exists. With no instruction using all five stages, the 800 ps path is never exercised.",
                            r"The most common instruction does not set the clock; the slowest does. A single-cycle design cannot give `ADD` a shorter tick than `SW`, however many `ADD`s there are.",
                            r"CPI is 1 in both cases, and time is CPI times the period times the instruction count. The period is what changed, from 800 to 700 ps, so the same program runs about 12% faster.",
                        ],
                        "why": r"""
A single-cycle machine has one clock, and it has to be long enough for the slowest
instruction to complete, because the clock does not know which instruction is in flight.
`LW` is slowest at 800 ps. Take it away and `SW`, at 700 ps, is the new worst case, so
the period drops to 700 ps and every instruction, `JMP` included, takes 700 ps. This is
why CPI 1 is not the same as fast: execution time is instructions times CPI times
period, and the period is held hostage by the longest path. The pipeline in the capstone
shortens the tick to one stage by overlapping instructions, at the cost of the hazards
it then has to manage.
""",
                    },
                    {
                        "q": r'''
From the datapath's point of view, what makes `BEQ r2, r3, 7` different from
`SUB r4, r2, r3`?
''',
                        "opts": [
                            "Only what is written to the PC at the end of the cycle; the comparison is the same subtraction the ALU does anyway",
                            "The branch stalls the datapath until the comparison result is known, so it necessarily takes more than one clock cycle",
                            "The branch writes the target address into a register first and then jumps to it on the following tick",
                            "The branch reads its operands in a different stage, because the PC must be updated before decode can begin",
                        ],
                        "a": 0,
                        "whys": [
                            r"Both read `r2` and `r3` and run them through the ALU. `SUB` sends the result to the register file; `BEQ` sends the zero flag to the next-PC mux, which chooses 7 or PC + 1. Same datapath, different destination.",
                            r"Stalls belong to the pipeline, where later instructions have already been fetched. In a single-cycle machine the comparison, the mux and the PC write all fit inside the one period; nothing waits.",
                            r"The target is an immediate in the instruction and goes straight to the next-PC mux. Passing it through a register would add a write-back and a second instruction to what is one operation.",
                            r"All instructions read their operands in decode, after fetch, and the PC is written at the end of the cycle for every instruction. A branch changes which value is written, not when.",
                        ],
                        "why": r"""
A branch is the ordinary datapath with a different consumer. `BEQ` reads two registers
and subtracts them, as `SUB` does; the ALU's zero output, rather than its result, is
what the branch uses, and it steers a multiplexer that picks between `pc + 1` and the
immediate. That mux is there for every instruction, set to `pc + 1` by default, and a
taken branch flips it. The PC is state, updated once per cycle; control flow is nothing
but choosing what to write into it. Stalls, delayed decisions and multi-cycle branches
are pipeline phenomena, and they appear only when the next instruction has been fetched
before this one has decided.
""",
                    },
                    {
                        "q": r'''
A program's last word is `SW r1, 0(r0)`, with no `HALT` after it. After executing it the
PC is 9, one past the end of the program list. What should `step()` do, and why?
''',
                        "opts": [
                            "Raise `IndexError`: there is no instruction at 9, and executing whatever sits there is what a real processor would do",
                            "Treat the missing word as `NOP` and set `halted`, since running off the end is how a program without `HALT` finishes",
                            "Return normally with `steps` unchanged, because the program has done its work and there is nothing left to execute",
                            "Fetch `mem[9]` and execute it, since instructions and data share one memory and the program continues into the data",
                        ],
                        "a": 0,
                        "whys": [
                            r"The brief says a `pc` outside the program raises `IndexError`, and the reason is that silently doing something is worse than stopping. A real processor here would execute data as instructions.",
                            r"Inventing a `HALT` that the program did not contain hides the bug. The programmer forgot to halt, and a simulator that halts for them will never tell them so.",
                            r"Returning without executing anything leaves the machine with `halted` false, so `run()` loops forever, and `steps` never reaches `max_steps` because it never advances.",
                            r"The simulator keeps `program` and `mem` as separate lists, so there is no data at instruction address 9. Real von Neumann machines do fetch data as code in this situation, which is precisely why the model refuses.",
                        ],
                        "why": r"""
The choice is between an honest error and a plausible fiction. A real processor at this
point fetches whatever bits sit past the program, decodes them, and executes the result;
if the bits happen to be data, the machine runs garbage while looking busy. The
simulator has a cleaner option: `pc` is outside the program, so raise `IndexError` and
say so. The lab's test on halting, stepping past halt and runaway programs checks this,
along with `RuntimeError` for stepping a halted machine and for a program that never
halts. Each is a case where the model can say that this is not a program rather than
invent behaviour.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "A library desk with eight shelves",
                    "minutes": 13,
                    "body": r'''
A university library keeps its stacks in a building across the road. Fetching a book
from there takes a runner about ten minutes. At the front desk there is a shelf with
eight slots, and the desk's rule is that a book that has been fetched stays in a slot
until something pushes it out, so that the second request for it takes ten seconds
instead of ten minutes. The desk is a cache. The stacks are DRAM. The proportions are
about right: a processor core can do arithmetic in a nanosecond and a trip to main
memory costs on the order of a hundred. That gap is the memory wall, and every number in
this module comes from trying to stand in front of it.

The rule that makes the desk work is a bet: a book that was wanted once will be wanted
again soon, and a book near it on the shelf will be wanted too. The first bet is
temporal locality, the second is spatial. A loop re-reads its counter every iteration; a
scan of an array touches consecutive words. Neither is a law of nature. They are habits
of the programs people write, and the memory hierarchy is built on the assumption that
programs keep them.

## Finding a book in one look

The desk shelf has eight slots and the stacks have millions of call numbers, so a slot
has to serve many books, and the desk needs to know in one glance whether a requested
book is on the shelf. Searching all eight slots is eight comparisons; the hardware
equivalent is eight comparators running in parallel, which is affordable for eight and
not for eight thousand. The cheaper rule is to decide in advance which slot a book *may*
occupy, so that a request checks one slot and no others.

Take the call number modulo eight. Call number 37 may live in slot 5 and nowhere else.
The slot holds a label saying which of its many possible books is there right now, and
a request compares the label against the request's number: match, and it is a hit;
mismatch, and the runner goes to the stacks and the incoming book displaces whatever
the slot held.

Now the second bet. Books that sit together in the stacks are wanted together, so the
runner brings back a bundle of four neighbours rather than one book, and the slot holds
the bundle. Which four? The bundle boundary has to be fixed, or the same book could
arrive in two different bundles and be on the shelf twice; so the bundles are call
numbers 0 to 3, 4 to 7, 8 to 11 and so on, and a request for 37 fetches 36, 37, 38 and
39 together. A slot now holds a bundle, so it is the *bundle number*,
$\lfloor 37 / 4 \rfloor = 9$, that is taken modulo eight to choose the slot, and 37
lands in slot 1.

## The three fields fall out of the arithmetic

Say the cache has `sets` slots and each holds a block of `block_words` words, both
powers of two, and addresses count words. Dividing by `block_words` is a right shift by
$\log_2(\text{block words})$ bits, and the bits shifted away are the position of the
word inside its block: the offset. Taking the block number modulo `sets` keeps its low
$\log_2(\text{sets})$ bits: the index. Whatever bits remain above those two fields are
the tag, the label that says which of the many blocks sharing this index is present.

$$\text{address} = \underbrace{\text{tag}}_{\text{whatever remains}}\;\underbrace{\text{index}}_{\log_2 \text{sets}}\;\underbrace{\text{offset}}_{\log_2 \text{block words}}$$

```python
sets, block_words = 8, 4
offset_bits = block_words.bit_length() - 1        # 2: log2 of 4
index_bits = sets.bit_length() - 1                # 3: log2 of 8

def fields(address):
    offset = address & (block_words - 1)
    index = (address >> offset_bits) & (sets - 1)
    tag = address >> (offset_bits + index_bits)
    return tag, index, offset

for address in (37, 31, 32, 0):
    print(f"{address:3d} = {address:07b} -> tag, index, offset = {fields(address)}")
```

Address 37 is `0100101`: offset `01`, index `001`, tag `1`. Address 31 is `0011111`:
offset 3, index 7, tag 0, the last word of the last block that fits before the tags
start. Address 32 is one further and wraps round to index 0 with tag 1. Those are the
lab's first three test cases, and every other number in the lab rests on this split.

The mistake people make is to take the index from the address rather than from the
block number, because "call number modulo eight" was the rule before bundles were
introduced, and it is hard to let go of a rule that was right a paragraph ago.

```python
sets = 8
address = 37
print("index from the address:", address & (sets - 1))         # 5: wrong
print("index from the block:  ", (address >> 2) & (sets - 1))  # 1: right
```

With the wrong split, the four words of one block scatter into four different sets,
spatial locality buys nothing, and the row-order hit rate below drops from 0.75 to
something the tests will reject.

The index comes from the *low* bits of the block number for a reason. Consecutive blocks
then land in consecutive sets, so a sequential scan spreads across the whole cache. Take
the index from the high bits and every block in a 32-word neighbourhood would map to
the same set, and a scan would evict its own previous block at every step.

## Same data, same cache, two orders

Store an 8 by 8 matrix row-major, so element $(r, c)$ is at word $8r + c$, and read
every element once. Row order visits 0, 1, 2, 3, 4, and so on. Column order visits 0,
8, 16, 24, up to 56, then 1, 9, 17. Both traces contain the same 64 addresses. Run them
through the 8-set, direct-mapped, 4-word cache.

```text
column order, the first ten accesses:
 address  block  index  tag   slot held   result
    0       0      0     0    empty       miss
    8       2      2     0    empty       miss
   16       4      4     0    empty       miss
   24       6      6     0    empty       miss
   32       8      0     1    tag 0       miss, evicts block 0
   40      10      2     1    tag 0       miss, evicts block 2
   48      12      4     1    tag 0       miss
   56      14      6     1    tag 0       miss
    1       0      0     0    tag 1       miss, evicts block 8
    9       2      2     0    tag 1       miss
```

Block 0 was fetched for address 0 and held addresses 1, 2 and 3 as well. By the time
address 1 is asked for, block 8 has taken its slot, and by the time 33 is asked for,
block 0 has taken it back. Every access misses. The spatial locality was there, in the
fetched block, and the placement rule threw it away before it could be used.

```python
sets = 8

def simulate(trace):
    lines = [None] * sets                   # the tag each set holds
    hits = 0
    for address in trace:
        block = address >> 2                # 4-word blocks
        index, tag = block & (sets - 1), block >> 3
        if lines[index] == tag:
            hits += 1
        else:
            lines[index] = tag
    return hits, len(trace) - hits

row = [8 * r + c for r in range(8) for c in range(8)]
col = [8 * r + c for c in range(8) for r in range(8)]
print("row order:    hits, misses =", simulate(row))      # (48, 16)
print("column order: hits, misses =", simulate(col))      # (0, 64)
```

Row order misses once per block and hits the three words behind it: 16 misses, 48 hits,
a hit rate of 0.75. Column order: 64 misses, 0 hits. Same 64 words, same instructions
executed, and a memory system that is spending a hundred nanoseconds on every one of
them in one case and on a quarter of them in the other.

## Naming the misses

Sixteen of the column walk's misses are unavoidable: sixteen blocks, each fetched for
the first time. Those are compulsory misses, and no cache of any design avoids them. The
other 48 are not because the cache is too small: eight blocks hold 32 words, and a
column pass touches eight blocks, which fit. They happen because two blocks the program
needs at the same time are forced into the same slot. Those are conflict misses, and the
test for a conflict miss is that giving the cache the same capacity with more freedom in
placement makes it go away.

Give each set two slots instead of one. A block may now sit in either of its set's two
ways, and blocks 0 and 8 can live side by side. The 2-way column walk misses 16 times
and hits 48, the same as the row walk; that is the lab's final test, and the whole of
the argument for set associativity in two numbers. A miss that survives every increase
in associativity, because the working set is bigger than the cache, is the third kind: a
capacity miss.

## Choosing the victim

Two ways per set means that on a miss into a full set something has to go, and the
choice is a bet on the future: evict the block least likely to be wanted again. The
usual proxy is the block that has gone longest without being touched, the least recently
used. Keep each set's blocks in order of last use, move a block to the back on a hit,
and take the front on a miss.

```python
sets, ways = 2, 2
lines = [[] for _ in range(sets)]           # each set: tags, least recently used first

def access(address):
    index, tag = address & (sets - 1), address >> 1    # 1-word blocks: no offset bits
    entries = lines[index]
    if tag in entries:
        entries.remove(tag)
        entries.append(tag)                 # a hit makes it the most recent
        return "hit"
    if len(entries) == ways:
        entries.pop(0)                      # the front has waited longest
    entries.append(tag)
    return "miss"

print([access(a) for a in (0, 2, 0, 4)])   # ['miss', 'miss', 'hit', 'miss']
print(lines[0])                             # [0, 2]: the hit on 0 saved it; address 2's block went
```

Addresses 0, 2 and 4 all have index 0 in a two-set cache, with tags 0, 1 and 2. After
the third access the set's order is tag 1 then tag 0, so the miss on tag 2 removes tag 1
rather than tag 0, which arrived first. A first-in-first-out cache would have removed
tag 0 and got the next access to it wrong. The lab test named "LRU picks the right
victim" is this trace.

True LRU is cheap in a Python list and expensive in silicon. An $n$-way set has $n!$
possible recency orders, and the state needed to tell them apart grows with
$\log_2 n!$.

```python
import math

for ways in (2, 4, 8, 16):
    orderings = math.factorial(ways)
    bits = math.ceil(math.log2(orderings))
    print(f"{ways:2d}-way: {orderings:15d} orders, {bits:2d} bits per set for true LRU")
```

One bit per set for two ways; five for four; sixteen for eight, plus the logic to update
them on every hit. Real caches above four ways keep a tree of "which half was used more
recently" bits, or pick at random, and accept a hit rate a little below true LRU for
hardware a lot below it.

## Turning a hit rate into time

A hit rate is not a speed. The number a program feels is the average time per access,
which is the hit time plus the fraction of accesses that miss times what a miss costs:

$$\text{AMAT} = t_{\text{hit}} + (1 - h) \times t_{\text{miss}}.$$

The formula is nothing more than an average: every access pays the hit time to look,
and the ones that miss pay the penalty on top.

```python
hit_time, miss_penalty = 1.0, 100.0        # nanoseconds
for label, hit_rate in (("row, 1-way", 0.75), ("column, 1-way", 0.0), ("column, 2-way", 0.75)):
    amat = hit_time + (1 - hit_rate) * miss_penalty
    print(f"{label:14s} hit rate {hit_rate:.2f}  AMAT {amat:6.1f} ns  64 accesses: {64 * amat:7.1f} ns")
```

The row walk averages 26 ns per access and the column walk 101 ns, about four times
slower, for the same data and the same instruction count. Notice what the penalty does
to the arithmetic: moving the hit rate from 0.90 to 0.95 halves the miss rate and takes
AMAT from 11 ns to 6 ns. Small changes in the hit rate are large changes in time when
the penalty is a hundred times the hit, and a hit rate reported to one decimal place is
hiding most of what matters.

## Where the model stops

The lab's cache counts reads and nothing else. Real caches have to decide what a write
does: write it through to memory every time, or mark the block dirty and write it back
on eviction, at which point an eviction costs a memory trip too. There is one level here
and three in a real core, each larger and slower, with the miss penalty of one being the
AMAT of the next. Addresses here are the program's own; a real cache is indexed with
bits that pass through a page table first. And the trace is fixed before the cache sees
it, which is right for what a program touches and wrong for when: a real processor
issues loads out of order and overlaps a miss with useful work, so the cost of a miss is
less than the penalty when there is something else to do, and the whole penalty when
there is not.

The lab **A cache simulator over an access trace** asks for a
`Cache(sets, ways, block_words)` with `fields`, `access`, `hit_rate` and `stats`, plus
`run_trace` and `matrix_trace`. The geometry must be validated, a negative address
refused, and `hit_rate` must return 0.0 before any access rather than dividing by zero.
The tests then replay the row and column walks through 1-way and 2-way caches and
expect 0.75, 0.0 and 0.75.
''',
                },
            ],
            "quiz": {
                "title": "Where the misses come from",
                "minutes": 8,
                "questions": [
                    {
                        "q": r'''
`Cache(4, 1, 2)` has four sets and two-word blocks. What does `fields(13)` return, as
`(tag, index, offset)`?
''',
                        "opts": [
                            "`(1, 2, 1)`: one offset bit, then two index bits taken from the block number 6, then the rest",
                            "`(3, 1, 1)`: one offset bit, and the index is the address itself taken modulo the number of sets",
                            "`(0, 6, 1)`: one offset bit, and the index is everything above it, since 6 is the block number",
                            "`(1, 1, 2)`: the index is the lowest bits, the offset sits above it, and the tag is what remains",
                        ],
                        "a": 0,
                        "whys": [
                            r"13 is `1101`. The low bit, 1, is the offset. Shift it off to get block 6, `110`; the low two bits of that, `10`, are index 2; what remains, `1`, is the tag.",
                            r"`13 & 3` is 1, but that takes the index from the address, not from the block number. The offset bit has to be removed first, and doing so moves the index to 2 and the tag to 1.",
                            r"The index is the block number *modulo the number of sets*, so it must be masked to two bits: `6 & 3` is 2, and the bit that was masked away, 1, is the tag. A cache with four sets has no set 6.",
                            r"The offset is the lowest field, because it selects a word within a block and neighbouring words share a block. Putting the index below it would scatter one block's words across sets.",
                        ],
                        "why": r"""
Slice from the bottom. Two-word blocks need one offset bit: `13 & 1` is 1. Shift that
bit away and the block number is `13 >> 1`, which is 6. Four sets need two index bits:
`6 & 3` is 2. Everything above those three bits is the tag: `13 >> 3` is 1. So
`(1, 2, 1)`. The lab test `Address decomposition` does the same to
`Cache(4, 1, 1).fields(6)`, expecting `(1, 2, 0)`. The result to watch for is
`(3, 1, 1)`: the index taken from the address instead of the block, which is the mistake
the reading names.
""",
                    },
                    {
                        "q": r'''
Column order through the 8-set direct-mapped cache misses all 64 times, where 16 misses
would be the minimum. What kind are the other 48, and what is the evidence?
''',
                        "opts": [
                            "Conflict misses: a 2-way cache of the same capacity turns all 48 of them into hits",
                            "Capacity misses: the matrix is 64 words and the cache holds 32, so half of it can never fit",
                            "Compulsory misses: each of the 64 words is being touched for the first time in the trace",
                            "Capacity misses: a column pass touches eight blocks, every block the cache has",
                        ],
                        "a": 0,
                        "whys": [
                            r"Same 32 words of capacity, same trace, one placement rule loosened: 16 misses and 48 hits. A miss that disappears when placement is freed, with no extra capacity, is a conflict miss by definition.",
                            r"Row order walks the same 64 words through the same 32-word cache and scores 0.75. If capacity were the problem it would be a problem in both orders; the difference between them is placement.",
                            r"Compulsory misses are one per block, and there are 16 blocks of four words. The other 48 accesses are to words already fetched as part of a block, then evicted before they were used.",
                            r"A column pass does fill the cache, but the next column reuses exactly those eight blocks, which an eight-block fully associative cache would hold. They fit; they are mapped to four sets instead of eight.",
                        ],
                        "why": r"""
The three C's are told apart by what fixes them. Compulsory misses are the first touch
of each block and nothing avoids them: 16 here. Capacity misses go away only with a
bigger cache. Conflict misses go away when the same capacity is arranged more flexibly,
and that is the experiment the lab runs: `Cache(8, 2, 4)` holds the same 32 words as
`Cache(8, 1, 4)` and takes the column walk from 64 misses to 16. Blocks 0 and 8 both
need set 0 within one column pass and can now share it. The evidence that it is not
capacity is that the row walk, through the identical cache, scores 0.75.
""",
                    },
                    {
                        "q": r'''
Hit time is 1 ns and the miss penalty is 100 ns. A change takes the hit rate from 0.90
to 0.95. What happens to the average memory access time?
''',
                        "opts": [
                            "It falls from 11 ns to 6 ns: the miss rate halved, and the penalty is where nearly all the time is",
                            "It falls by about 5%, from 11 ns to roughly 10.5 ns, in proportion to the improvement in hit rate",
                            "It falls from 10 ns to 5 ns, since the hit time is paid only on hits and the penalty only on misses",
                            "It barely moves from 11 ns, because 90% of accesses were already hitting and hits were already fast",
                        ],
                        "a": 0,
                        "whys": [
                            r"AMAT is $1 + 0.10 \times 100 = 11$ ns before and $1 + 0.05 \times 100 = 6$ ns after. Halving the miss rate halves the penalty term, which is ten times the hit term.",
                            r"AMAT is not proportional to the hit rate; it is the hit time plus the miss rate times the penalty. Five points of hit rate is half the misses, and the misses are 10 of the 11 ns.",
                            r"Every access pays the hit time, because the cache is checked first whether it hits or not; the penalty is added on a miss. $0.9 \times 1 + 0.1 \times 100$ is 10.9, not 10, and it is not the formula anyway.",
                            r"The accesses that were already hitting are not where the time goes. Ten misses per hundred cost 1000 ns and ninety hits cost 90 ns; cutting the misses to five removes 500 of the 1090.",
                        ],
                        "why": r"""
AMAT is the hit time plus the miss rate times the miss penalty. At 0.90 that is
$1 + 0.1 \times 100 = 11$ ns; at 0.95 it is $1 + 0.05 \times 100 = 6$ ns. The hit rate
moved by five points, and the access time nearly halved, because the miss term dominates
when the penalty is a hundred times the hit time. This is why the row and column walks
differ by four times in time while differing by 0.75 in hit rate, and why a hit rate
quoted to one decimal place hides most of what matters.
""",
                    },
                    {
                        "q": r'''
A 2-way set receives accesses to tags 0, 2, 0 and 4 in that order, all mapping to the
same set. On the fourth access, which tag is evicted, and why?
''',
                        "opts": [
                            "Tag 2: the hit on 0 moved it to most recent, leaving 2 as the block untouched for longest",
                            "Tag 0: it entered the set first, and the block that has been resident longest is the one to go",
                            "Tag 4: the set is full, so the miss is served from memory and the set is left unchanged",
                            "Neither: the set has two ways, and tag 4 goes into the second way because the first holds 0 and 2",
                        ],
                        "a": 0,
                        "whys": [
                            r"The recency order after the third access is 2 then 0, oldest first. The miss on 4 takes the front of that order, and the front is 2.",
                            r"Residence time is the FIFO rule, not LRU. Tag 0 has been resident longest but was touched most recently; LRU keeps it and evicts 2, which the lab test on LRU victims checks.",
                            r"Every miss allocates: the block is brought in and something is evicted to make room. A cache that did not allocate on a miss would never fill, and every access would miss forever.",
                            r"Two ways means the set holds two blocks, and it already holds 0 and 2. A third block cannot fit, and the choice of which of the two to evict is the whole question.",
                        ],
                        "why": r"""
LRU keeps each set in order of last use and evicts the one that has waited longest.
Trace the set: tag 0 arrives, then tag 2, and the order is 0, 2. The hit on 0 moves it
to the back: 2, 0. Tag 4 misses into a full set, the front is evicted, and the front is
2. First-in-first-out would evict 0 instead because it arrived first, and the next
access to 0 would then miss where LRU hits. The lab keeps each set as a list with the
oldest at the front, so a hit is a remove and append, and a miss into a full set is a
pop from the front.
""",
                    },
                    {
                        "q": r'''
The index is taken from the low bits of the block number, and the tag from the bits
above. What would go wrong if the index were taken from the high bits instead?
''',
                        "opts": [
                            "Consecutive blocks would all map to the same set, so a sequential scan would evict its own previous block at every step",
                            "The tag would become too short to distinguish the blocks that share a set, and false hits would begin to occur",
                            "Nothing, provided the choice is made consistently; any fixed set of bits partitions the blocks evenly across the sets",
                            "High bits change less often than low bits, so the sets would be chosen less randomly and would fill up unevenly",
                        ],
                        "a": 0,
                        "whys": [
                            r"With three index bits from the top of a seven-bit block number, blocks 0 through 15 all have the same high bits and land in one set. A scan through them thrashes one set while seven sit empty.",
                            r"The tag is however many bits are left, and its length is the same whichever end the index comes from. A tag of the right length never yields a false hit; the problem is which blocks collide, not whether collisions are detected.",
                            r"Every choice partitions the blocks evenly in the abstract, but programs do not touch blocks uniformly. They touch neighbours, and neighbours differ in their low bits, which is why the low bits spread them out.",
                            r"This is on the right track but backwards in effect: low bits changing often is the point. A sequential scan changes the low bits with every block and the high bits almost never, so low bits spread the scan across the sets.",
                        ],
                        "why": r"""
Locality says a program's next block is likely to be the neighbour of the last one, and
neighbouring block numbers differ in their low bits. Index by the low bits and eight
consecutive blocks fill eight different sets; the cache holds a contiguous run of memory,
which is what a scan wants. Index by the high bits and a contiguous run maps entirely to
one set, so a scan would evict block 0 to fetch block 1 while seven sets stayed empty.
The tag is whatever is left over either way, and a tag comparison is exact, so
correctness is not the issue; what is at stake is whether the cache's capacity is
available to the access pattern programs actually have.
""",
                    },
                    {
                        "q": r'''
Keep 8 sets and 1 way but double the block to 8 words, so that the cache holds 64 words.
What hit rate does the column walk over the 8 by 8 matrix score now?
''',
                        "opts": [
                            "0.875: each row is now one block, the eight rows fill the eight sets, and after the first column everything hits",
                            "0.0: the column stride still sends each access to a different set, and each set is overwritten before it is reused",
                            "0.5: a block twice as long brings in twice as many neighbours, which halves the misses of the 4-word case",
                            "0.75: block size changes only the compulsory misses, and the conflict misses of the column walk are unaffected",
                        ],
                        "a": 0,
                        "whys": [
                            r"Word $8r + c$ is in block $r$, and block $r$ has index $r$ in eight sets: every row gets its own set, with the same tag 0. The first column misses eight times and brings in the whole matrix; the other 56 accesses hit.",
                            r"Each access in a column does go to a different set, but that is now a feature: the eight blocks of the first column are eight different rows in eight different sets, and nothing is overwritten. The matrix fits.",
                            r"The misses do not halve; they fall from 64 to 8. Longer blocks help by more than their length here because they also change which blocks conflict, and with one block per row there are no conflicts left.",
                            r"Block size changed the mapping, not only the number of compulsory misses. With a 4-word block two rows share a set and conflict; with an 8-word block each row has its own set, and the conflicts vanish.",
                        ],
                        "why": r"""
Work the geometry. Eight-word blocks make each row of the matrix exactly one block: word
$8r + c$ has block number $r$ and offset $c$. Eight sets with one way hold eight blocks,
and block $r$ maps to set $r$, so all eight rows sit in the cache together with tag 0.
The column walk's first eight accesses, one per row, miss and load all 64 words; the
remaining 56 hit. That is 8 misses in 64, a hit rate of 0.875, the same as the row walk
gets on this cache. The lesson is that block size, set count and associativity interact
through the address split, and a trace that thrashes one geometry can fit another of the
same capacity.
""",
                    },
                ],
            },
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
