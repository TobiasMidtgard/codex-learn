"""VLSI510 — RISC-V Microarchitecture.

Band 6 of the EE M.S. track. The shape is CTRL510's: every module is sandbox,
derivation, lab, and the capstone is the four of them wired together.

Authoring rules, unchanged:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed; nothing else outside the standard library
  * seed every RNG, and every expected value must be one that was computed

The timing model these labs build is stated once and never varies: five stages
IF ID EX MEM WB numbered 0 to 4, instruction i entering IF in cycle s_i, the
register file written in the first half of WB and read in the second half of ID,
and a branch resolved in EX. Every cycle count in every check follows from those
four sentences.
"""

# The assembler every module after the first is handed. Writing an assembler is
# not the lesson anywhere in this course; being able to state a test program as
# text rather than as eight hex digits is what makes the later labs readable.
ISA_PY = r'''
"""RV32I assembler and decoder for the subset these labs use. Read only.

The encoding is module 1's material. From module 2 onward the subject is timing,
so this file exists to let a check write a program as text.

    assemble(text)  -> a list of 32-bit words, resolving 'label:' definitions
                       and branch or jump targets named by label
    encode(line)    -> one word from one line, e.g. encode('lw x4, 8(x2)')
    decode(word)    -> the fields, with name, fmt, rd, rs1, rs2 and imm

Supported: add sub sll slt xor srl or and, addi slti xori ori andi, lw, sw,
beq bne blt bge, lui, jal, and the pseudo-instruction nop.
"""

R_ALU = {
    "add": (0x00, 0x0), "sub": (0x20, 0x0), "sll": (0x00, 0x1),
    "slt": (0x00, 0x2), "xor": (0x00, 0x4), "srl": (0x00, 0x5),
    "or": (0x00, 0x6), "and": (0x00, 0x7),
}
I_ALU = {"addi": 0x0, "slti": 0x2, "xori": 0x4, "ori": 0x6, "andi": 0x7}
BRANCH = {"beq": 0x0, "bne": 0x1, "blt": 0x4, "bge": 0x5}

OP_R, OP_I, OP_LOAD, OP_STORE = 0x33, 0x13, 0x03, 0x23
OP_BRANCH, OP_LUI, OP_JAL = 0x63, 0x37, 0x6F

FORMAT = {OP_R: "R", OP_I: "I", OP_LOAD: "I", OP_STORE: "S",
          OP_BRANCH: "B", OP_LUI: "U", OP_JAL: "J"}


def _reg(tok):
    tok = tok.strip()
    if tok == "zero":
        return 0
    if not tok.startswith("x"):
        raise ValueError("not a register: %r" % tok)
    n = int(tok[1:])
    if not 0 <= n < 32:
        raise ValueError("register out of range: %r" % tok)
    return n


def _imm(tok):
    return int(tok.strip(), 0)


def _split(line):
    line = line.split("#")[0].strip()
    if not line:
        return None, []
    parts = line.replace(",", " ").split()
    return parts[0], parts[1:]


def encode(line, pc=0, labels=None):
    """Assemble one line of text into a 32-bit instruction word."""
    labels = labels or {}
    op, args = _split(line)
    if op is None:
        raise ValueError("empty line")
    if op == "nop":
        return encode("addi x0, x0, 0")

    def target(tok):
        tok = tok.strip()
        return labels[tok] - pc if tok in labels else _imm(tok)

    if op in R_ALU:
        f7, f3 = R_ALU[op]
        rd, rs1, rs2 = _reg(args[0]), _reg(args[1]), _reg(args[2])
        return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | OP_R
    if op in I_ALU:
        f3 = I_ALU[op]
        rd, rs1, im = _reg(args[0]), _reg(args[1]), _imm(args[2])
        return ((im & 0xFFF) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | OP_I
    if op in ("lw", "sw"):
        off, base = args[1].split("(")
        im, rs1 = _imm(off), _reg(base.rstrip(")"))
        if op == "lw":
            rd = _reg(args[0])
            return ((im & 0xFFF) << 20) | (rs1 << 15) | (0x2 << 12) | (rd << 7) | OP_LOAD
        rs2 = _reg(args[0])
        lo, hi = im & 0x1F, (im >> 5) & 0x7F
        return (hi << 25) | (rs2 << 20) | (rs1 << 15) | (0x2 << 12) | (lo << 7) | OP_STORE
    if op in BRANCH:
        f3 = BRANCH[op]
        rs1, rs2 = _reg(args[0]), _reg(args[1])
        im = target(args[2]) & 0x1FFF
        return (((im >> 12) & 1) << 31) | (((im >> 5) & 0x3F) << 25) | (rs2 << 20) | \
               (rs1 << 15) | (f3 << 12) | (((im >> 1) & 0xF) << 8) | \
               (((im >> 11) & 1) << 7) | OP_BRANCH
    if op == "lui":
        rd, im = _reg(args[0]), _imm(args[1])
        return ((im & 0xFFFFF) << 12) | (rd << 7) | OP_LUI
    if op == "jal":
        rd = _reg(args[0])
        im = target(args[1]) & 0x1FFFFF
        return (((im >> 20) & 1) << 31) | (((im >> 1) & 0x3FF) << 21) | \
               (((im >> 11) & 1) << 20) | (((im >> 12) & 0xFF) << 12) | (rd << 7) | OP_JAL
    raise ValueError("unsupported mnemonic: %r" % op)


def assemble(text):
    """Assemble a block of text, resolving labels, into a list of words."""
    body, labels, pc = [], {}, 0
    for line in text.splitlines():
        stripped = line.split("#")[0].strip()
        if not stripped:
            continue
        while ":" in stripped:
            name, _, stripped = stripped.partition(":")
            labels[name.strip()] = pc
            stripped = stripped.strip()
        if stripped:
            body.append((pc, stripped))
            pc += 4
    return [encode(src, pc=at, labels=labels) for at, src in body]


def _sx(value, bits):
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


def decode(word):
    """Return the fields of one instruction word.

    Keys: name, fmt, opcode, rd, rs1, rs2, imm, funct3, funct7. A field the
    format does not carry is None.
    """
    word &= 0xFFFFFFFF
    opcode = word & 0x7F
    fmt = FORMAT.get(opcode)
    if fmt is None:
        raise ValueError("unknown opcode 0x%02x" % opcode)
    rd = (word >> 7) & 0x1F
    f3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    f7 = (word >> 25) & 0x7F

    if fmt == "R":
        imm = None
    elif fmt == "I":
        imm = _sx(word >> 20, 12)
    elif fmt == "S":
        imm = _sx((f7 << 5) | rd, 12)
    elif fmt == "B":
        imm = _sx((((word >> 31) & 1) << 12) | (((word >> 7) & 1) << 11) |
                  (((word >> 25) & 0x3F) << 5) | (((word >> 8) & 0xF) << 1), 13)
    elif fmt == "U":
        imm = _sx(word >> 12, 20) << 12
    else:
        imm = _sx((((word >> 31) & 1) << 20) | (((word >> 12) & 0xFF) << 12) |
                  (((word >> 20) & 1) << 11) | (((word >> 21) & 0x3FF) << 1), 21)

    name = None
    if opcode == OP_R:
        for k, (a, b) in R_ALU.items():
            if a == f7 and b == f3:
                name = k
    elif opcode == OP_I:
        for k, b in I_ALU.items():
            if b == f3:
                name = k
    elif opcode == OP_LOAD:
        name = "lw"
    elif opcode == OP_STORE:
        name = "sw"
    elif opcode == OP_BRANCH:
        for k, b in BRANCH.items():
            if b == f3:
                name = k
    elif opcode == OP_LUI:
        name = "lui"
    elif opcode == OP_JAL:
        name = "jal"

    return {
        "name": name, "fmt": fmt, "opcode": opcode,
        "rd": rd if fmt in ("R", "I", "U", "J") else None,
        "rs1": rs1 if fmt in ("R", "I", "S", "B") else None,
        "rs2": rs2 if fmt in ("R", "S", "B") else None,
        "imm": imm, "funct3": f3 if fmt in ("R", "I", "S", "B") else None,
        "funct7": f7 if fmt == "R" else None,
    }
'''

# Branch outcome traces for module 4. Generating a trace is bookkeeping; the lab
# is the predictor that has to guess it.
TRACES_PY = r'''
"""Deterministic branch traces. Read only.

Every generator returns a list of (pc, taken) pairs in retirement order. No
randomness that is not seeded, so two runs of the same trace are identical.
"""


def loop_trace(trips=20, body=10, pc=0x100):
    """One backward branch: taken body-1 times, then once not taken, per trip."""
    out = []
    for _ in range(trips):
        for k in range(body):
            out.append((pc, k != body - 1))
    return out


def alternating(n=200, pc=0x200):
    """One branch, taken every other time. Period two, for ever."""
    return [(pc, i % 2 == 0) for i in range(n)]


def two_loops(trips=15, a=6, b=4):
    """Two loop branches at different addresses, one nested after the other."""
    out = []
    for _ in range(trips):
        for k in range(a):
            out.append((0x300, k != a - 1))
        for k in range(b):
            out.append((0x340, k != b - 1))
    return out


def pseudo_random(n=400, percent_taken=70, seed=12345, pcs=(0x400, 0x420, 0x440)):
    """A linear congruential trace: biased, but with no pattern to learn."""
    state = seed & 0xFFFFFFFF
    out = []
    for i in range(n):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        out.append((pcs[i % len(pcs)], (state >> 16) % 100 < percent_taken))
    return out
'''


COURSE = {
    "id": "VLSI510",
    "title": "RISC-V Microarchitecture",
    "band": 6,
    "level": "Advanced",
    "prereqs": [],
    "stack": ["Python"],
    "credits": 10,
    "hours": 130,
    "icon": "▣",
    "summary": (
        "RV32I has one instruction length, one register file and forty base instructions, "
        "which makes it small enough to hold in your head and complete enough to run "
        "real programs. This course takes that instruction set apart bit by bit and "
        "then builds the machine that runs it: five stages, the hazards that stop them, "
        "the forwarding paths that mostly fix the hazards, and the branch predictor "
        "that pays for the ones nothing else can reach."
    ),
    "outcomes": [
        "Decode any RV32I word by hand, and explain why the immediate fields are scrambled the way they are.",
        "Account for the cycles a five-stage pipeline takes on a given instruction stream, hazard by hazard.",
        "Derive the forwarding condition from operand availability and operand use, and identify the cases forwarding cannot reach.",
        "Build and measure a branch predictor, and turn its accuracy into a CPI figure.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that runs a real program on a cycle-accurate model of the whole pipeline.",
    "reading": [
        "*The RISC-V Instruction Set Manual, Volume I: Unprivileged ISA* — chapter 2 and the encoding tables, freely available.",
        "*Computer Organization and Design, RISC-V Edition*, Patterson & Hennessy — chapter 4 for the pipeline this course models.",
        "*Computer Architecture: A Quantitative Approach*, Hennessy & Patterson — appendix C for the hazard algebra in its general form.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Reading an RV32I instruction word",
            "summary": "Six formats, thirty-two bits, and one design rule that explains every oddity in the layout.",
            "concepts": [
                "Fixed 32-bit words: `rd`, `rs1`, `rs2` and `funct3` sit at the *same* bit positions in every format that has them, so the register file can be read before the opcode is understood.",
                "The six formats — R, I, S, B, U, J — differ only in what they do with the bits the register fields leave over.",
                "Immediates are scrambled so that each immediate bit comes from as few different word positions as possible: the sign bit is always bit 31, so sign extension starts before decoding finishes.",
                "B and J immediates encode a multiple of two and omit bit 0; the bit you would expect at position 0 is not stored at all.",
                "A field the format does not define is not zero — it is whatever the immediate happened to put there, which is why a decoder must report absence rather than a number.",
            ],
            "read": [
                {
                    "title": "Taking 0xFE512E23 apart",
                    "minutes": 15,
                    "body": r'''
Here is one word, lifted out of an instruction memory:

```text
0xFE512E23
```

Nothing on the outside says what it is. There is no tag byte, no length prefix,
no header. There are thirty-two bits, and every design decision in RV32I is
visible in how they get cut up. So cut them.

```python
word = 0xFE512E23
print("bits:", format(word, "032b"))
for hi, lo in ((31, 25), (24, 20), (19, 15), (14, 12), (11, 7), (6, 0)):
    field = (word >> lo) & ((1 << (hi - lo + 1)) - 1)
    print("  word[%2d:%2d] = %-7s = %3d" % (hi, lo, format(field, "0%db" % (hi - lo + 1)), field))
```

Six slices, and one of them has to be looked up before any of the others mean
anything: `word[6:0]` is `0100011`, which is 0x23, which the opcode map calls
STORE. That is the only lookup in the whole exercise. Everything after it is
arithmetic on bits whose meaning the opcode has now fixed.

## The three fields that never move

Take the two five-bit slices in the middle. `word[19:15]` is 2 and `word[24:20]`
is 5. Those are `rs1` and `rs2`, and the interesting fact about them is not their
values but their addresses: bits 19:15 and 24:20 hold `rs1` and `rs2` in *every*
format that has source registers, and bits 11:7 hold `rd` in every format that
has a destination. The fields do not move when the format changes.

That is not tidiness. Work out what it buys by asking when the register file can
start reading. A register file read is a decode of five bits into one of 32 word
lines, then a long wire, then a sense amplifier — a few hundred picoseconds on a
path that has nothing to spare. If `rs1` sat at bits 19:15 for R-type and
somewhere else for I-type, the read could not start until the opcode had been
examined and a multiplexer had chosen which five bits to send. Decode, then
multiplex, then read: three delays in series inside one stage.

Fix the fields and the read starts on the raw instruction bits the cycle they
arrive, in parallel with the opcode decode, and the two finish together. The
values are then thrown away if the format turns out not to use them, which costs
nothing but energy. That is why ID is one stage rather than two, and it is worth
holding on to, because it is the constraint that forces every awkward thing about
the immediates below.

Notice what this same rule says about the word in front of us. A store has no
destination register, so bits 11:7 are free — and `word[11:7]` is `11100`, which
is 28. Twenty-eight is a perfectly ordinary register number. Nothing in the bit
pattern warns you that reading it as `rd` is wrong.

## Putting the immediate back together

The store needs an offset, and the only bits left are 31:25 and 11:7 — seven bits
above and five below, split around the `rs2` field that is not allowed to move.
The S format defines `imm[11:5] = word[31:25]` and `imm[4:0] = word[11:7]`, so
the two halves concatenate in that order and the result is read as a twelve-bit
two's complement number.

```python
word = 0xFE512E23
hi = (word >> 25) & 0x7F          # imm[11:5]
lo = (word >> 7) & 0x1F           # imm[4:0]
raw = (hi << 5) | lo
print("pieces  ", format(hi, "07b"), format(lo, "05b"))
print("joined  ", format(raw, "012b"), "=", raw, "unsigned")
top = 1 << 11
print("signed  ", (raw & (top - 1)) - (raw & top))
print("bits 11:7 read as a register number:", lo)
```

The joined field is `111111111100`, which is 4092 unsigned and $-4$ signed. With
`funct3 = 010` selecting a full word, the instruction is `sw x5, -4(x2)`: store
the word in `x5` four bytes below the address in `x2`. It is a push.

Two things in that trace are worth slowing down over. The first is that the
twelve bits are *one* number, sign-extended once at the end, not two numbers
extended separately — extending each half would turn `1111111` and `11100` into
$-1$ and $-4$, and no arrangement of those gives $-4$. The second is the last
line: 28. That is the number a decoder hands back if it reads bits 11:7 as `rd`
for every format instead of asking whether this format has a `rd` at all. It is
not a crash and it is not a nonsense value; it is a plausible register that some
later stage will happily forward from. The lab's check named *fields the format
does not define are reported as absent* exists for exactly this word, and the
rule it enforces is that a decoder reports `None` rather than a number it is not
entitled to.

## Why the bits are shuffled

The immediates look gratuitously scrambled. B-type takes bit 12 from word bit 31,
bit 11 from word bit 7, bits 10:5 from word bits 30:25 and bits 4:1 from word
bits 11:8. Written out it looks like malice. It is a minimisation, and the
quantity being minimised can be counted directly: for each bit of the assembled
immediate, how many *different* positions in the instruction word does it ever
come from? A bit with one source is a wire. A bit with three sources is a
three-input multiplexer, and there are 32 of them in the immediate generator.

```python
# Where each immediate bit comes from, format by format. Reference-manual data.
SRC = {
    "I": {k: 20 + k for k in range(0, 12)},
    "S": {**{k: 7 + k for k in range(0, 5)}, **{k: 20 + k for k in range(5, 12)}},
    "B": {**{k: 7 + k for k in range(1, 5)}, **{k: 20 + k for k in range(5, 11)},
          11: 7, 12: 31},
    "U": {k: k for k in range(12, 32)},
    "J": {**{k: 20 + k for k in range(1, 11)}, **{k: k for k in range(12, 20)},
          11: 20, 20: 31},
}
fanin = {}
for table in SRC.values():
    for imm_bit, word_bit in table.items():
        fanin.setdefault(imm_bit, set()).add(word_bit)
single = [b for b in fanin if len(fanin[b]) == 1]
print("immediate bits fed by exactly one word bit: %d of %d" % (len(single), len(fanin)))
for b in sorted(b for b in fanin if len(fanin[b]) > 1):
    print("  imm[%2d] <- word bits %s" % (b, sorted(fanin[b])))
```

Twenty-four of the thirty-two immediate bits have exactly one possible source
across all five formats that carry an immediate, so twenty-four of them are bare
wires with no selection logic at all. Of the eight that need a choice, seven are
a two-way pick and one — `imm[11]`, which lands at word bit 31 in I and S, at
word bit 7 in B and at word bit 20 in J — has three sources. `imm[10:5]` does not
appear in the list at all: it
comes from word bits 30:25 in every format that reaches that far, which is why
those six bits sit where they do in I, S, B and J alike.

The sign bit is the extreme case of the same rule. Whenever an immediate is
signed, its sign lives at word bit 31 — I, S, B and J all agree, and U places its
top bit there too. Sign extension is a fan-out from a single wire, and it can
start before the opcode has been decoded, in parallel with the register read. The
encoding is unpleasant to read and cheap to build, and the trade was made
deliberately in that direction: people read disassembly a few times a year, and
the immediate generator runs every cycle for the life of the part.

## The bit that is not stored

B and J both encode a byte offset and both omit bit 0. Neither format has room
for the bit, and neither needs it: an instruction address is even, so bit 0 of
any legal branch target is zero and storing it would spend a bit to transmit a
constant. Dropping it doubles the reach. A B-type field holds twelve stored bits
that become a thirteen-bit signed offset, $\pm 4$ KiB; J holds twenty that become
twenty-one, $\pm 1$ MiB.

The consequence for a decoder is a sign-extension width that surprises people.
The B immediate is assembled *including* the always-zero bit 0, giving a
thirteen-bit quantity, and it is sign-extended at thirteen bits — not twelve.
Extend at twelve and every backward branch comes out with the wrong magnitude
while every short forward branch still looks right, which is the worst possible
failure signature: the test that would have caught it is the one nobody wrote.
The lab's check *a B immediate is scrambled, and always even* decodes
`0x800002E3` and expects $-2044$ for this reason.

## Where the picture stops holding

The rule that a field never moves holds inside RV32I and stops at its edge. In
the compressed extension every 16-bit form places its register fields somewhere
else, and it gets away with it because a compressed instruction is expanded to a
32-bit form before the register read — an extra decode step paid for by the
halved code size. The rule also says nothing about *unused* fields: an R-type
word has no immediate, and asking for one is a question about a field that does
not exist, which is why the lab returns `None` rather than 0.

The opcode map is sparser than a five-format story suggests, too. The subset in
this course uses seven of the 128 possible opcodes, the full base ISA a handful
more, and the rest are unallocated or reserved for extensions;
`decode` on an unknown opcode should raise rather than guess a
format, because a guessed format produces a full set of confident, wrong fields.

Two units in this module build on what is above. The sandbox *The machine the
encoding feeds* shows the pipeline these words are fed into, with every hazard
turned off, so you can see the shape the next three modules spend their time
defending. The derivation *What the pipeline registers buy* prices that shape:
five stages of 180, 120, 200, 190 and 90 ps become a 230 ps clock instead of an
810 ps one, a speedup of 3.52 rather than the 5 the stage count suggests. Then
the lab, *Write an RV32I decoder*, asks for `bits`, `sign_extend`, `immediate`
and `decode` — the four functions the traces above were made of, with the
absent-field rule as the check that separates a decoder from a set of shifts.
''',
                },
            ],
            "sandbox": {
                "title": "The machine the encoding feeds",
                "visualiser": "pipeline",
                "minutes": 7,
                "initial": {"dep": 0, "fwd": 0, "miss": 0},
                "brief": r'''
Before taking the instruction word apart, look at what consumes it. Nine
instructions, five stages each, drawn as one row per instruction and one column
per cycle. Everything is set to zero here, so nothing is in anybody's way — this
is the machine at its best, and every later module is about what takes it away
from this picture.
''',
                "notice": [
                    "With all three sliders at zero the nine rows form a clean diagonal: each instruction starts exactly one cycle after the row above it, and five instructions are in flight at once.",
                    "Count the cells in one row. Five, always. The width of a row is the *latency* of one instruction; the slope of the diagonal is the *throughput*. This picture is the only place those two numbers are drawn separately.",
                    "The third cell of every row is the highlighted one — that is EX, the single pass through the ALU that every format gets, whatever it does with the result.",
                ],
            },
            "derive": {
                "title": "What the pipeline registers buy",
                "minutes": 14,
                "vars": ["t_if", "t_id", "t_ex", "t_me", "t_wb", "t_reg", "t_stage", "k"],
                "brief": r'''
A single-cycle machine puts all five blocks in series inside one clock period. A
pipelined machine puts a register between each pair of blocks, so the clock only
has to outrun the slowest block — but it pays for a register in every stage.

Call the combinational delays $t_{if}$, $t_{id}$, $t_{ex}$, $t_{me}$, $t_{wb}$, and
let $t_{reg}$ be the clock-to-Q plus setup overhead of one pipeline register.
''',
                "steps": [
                    {
                        "prompt": "Write the shortest clock period a single-cycle machine can use, in terms of the five stage delays and $t_{reg}$.",
                        "answer": "t_{if} + t_{id} + t_{ex} + t_{me} + t_{wb} + t_{reg}",
                        "hint": "Everything is in series between one clock edge and the next, and the state elements at each end cost one $t_{reg}$ altogether.",
                        "deconstruct": [
                            "In a single-cycle machine one instruction occupies one clock period from fetch to write-back.",
                            "So the period must cover every block in the path, plus the overhead of the one register pair that bounds it.",
                        ],
                    },
                    {
                        "prompt": "Take $t_{if}=180$, $t_{id}=120$, $t_{ex}=200$, $t_{me}=190$, $t_{wb}=90$ and $t_{reg}=30$, all in picoseconds. What is that period?",
                        "given": "Substitute into the expression you just wrote.",
                        "answer": "810",
                        "hint": "Add the five delays, then add the register overhead once.",
                        "deconstruct": [
                            "$180 + 120 + 200 + 190 + 90 = 780$.",
                            "Plus $t_{reg} = 30$ gives 810 ps.",
                        ],
                    },
                    {
                        "prompt": "Now cut the path with four pipeline registers. Every stage is bounded by registers, so the period is the slowest stage plus one $t_{reg}$. What is it, in picoseconds?",
                        "answer": "230",
                        "hint": "The slowest of the five delays is EX at 200 ps.",
                        "deconstruct": [
                            "The clock must satisfy every stage, so it is set by the largest, $t_{ex} = 200$.",
                            "Each stage still writes a register: $200 + 30 = 230$ ps.",
                        ],
                    },
                    {
                        "prompt": "On a long stream of instructions with no hazards, the pipelined machine retires one instruction per cycle. Write its speedup over the single-cycle machine.",
                        "answer": "\\frac{810}{230}",
                        "hint": "Both machines retire one instruction per clock; only the clock differs.",
                        "deconstruct": [
                            "Single-cycle: one instruction every 810 ps.",
                            "Pipelined: one instruction every 230 ps, once the pipeline is full.",
                            "The ratio is about 3.52 — not 5.",
                        ],
                    },
                    {
                        "prompt": "Generalise. With $k$ perfectly balanced stages of delay $t_{stage}$ each, write the speedup of the pipelined machine over the single-cycle one.",
                        "answer": "\\frac{k \\cdot t_{stage} + t_{reg}}{t_{stage} + t_{reg}}",
                        "hint": "Write both periods first: the unpipelined path is $k$ stages in series plus one register overhead.",
                        "deconstruct": [
                            "Single-cycle period: $k\\,t_{stage} + t_{reg}$.",
                            "Pipelined period: $t_{stage} + t_{reg}$.",
                            "Divide. As $t_{reg} \\to 0$ this tends to $k$, and never reaches it.",
                        ],
                    },
                ],
                "closing": r'''
Two things fall out that no amount of cleverness removes. The speedup is bounded
by the *stage count*, not by anything about the instruction set; and it is
strictly below that bound by a factor set by $t_{reg}/t_{stage}$, which is why
pipelines stopped getting deeper once the register overhead became a visible
fraction of a stage. And this is all before a single hazard — the next three
modules are about how much of the 3.52 you actually keep.
''',
            },
            "quiz": {
                "title": "Why the encoding looks the way it does",
                "minutes": 7,
                "questions": [
                    {
                        "q": "`rd`, `rs1` and `rs2` occupy the same bit positions in every format that has them. What does that buy?",
                        "opts": [
                            "The register file can be read before the instruction has been decoded",
                            "It makes the immediates contiguous",
                            "It allows a variable instruction length",
                            "It reduces the number of opcodes needed",
                        ],
                        "a": 0,
                        "why": r"""
The register read and the decode happen in the same cycle, in parallel, because the
fetch unit can point at bits 19:15 and 24:20 without yet knowing what the instruction
*is*. If those fields moved between formats, the read would have to wait for the
decoder and the pipeline would grow a stage. This is the design rule that explains
almost every oddity in the layout — including the scrambled immediates, which are the
price paid for it.
""",
                    },
                    {
                        "q": "How many instruction formats does RV32I define?",
                        "opts": ["Six: R, I, S, B, U, J", "Four: R, I, S, U", "Three: R, I, J", "Eight, one per opcode class"],
                        "a": 0,
                        "why": r"""
Six, and they differ only in what they do with the bits *not* used for registers —
that is, in how they assemble an immediate. B and J are not really separate encodings
so much as S and U with the immediate bits permuted for branch and jump targets, which
is why some references count four base formats plus two variants. Either way the
register fields are common to all of them.
""",
                    },
                    {
                        "q": "The immediate bits are scrambled rather than laid out in order. Why?",
                        "opts": [
                            "So each immediate bit comes from as few different instruction bits as possible",
                            "To leave room for future 64-bit extensions",
                            "To make the encoding harder to disassemble",
                            "Because the assembler emits them in that order",
                        ],
                        "a": 0,
                        "why": r"""
Every immediate bit that can come from only one place in the word needs no multiplexer
in front of it — just a wire. The scrambling is chosen to maximise how many bits are in
that happy position across all six formats, so the immediate-generation logic is a
handful of gates rather than a wide mux. It is ugly to read and cheap to build, and
that trade is made deliberately: humans read disassembly, silicon builds muxes.
""",
                    },
                    {
                        "q": "S-type splits its 12-bit immediate into two pieces. What forces the split?",
                        "opts": [
                            "The `rs1` and `rs2` fields must stay where they always are",
                            "12 bits do not fit in one contiguous field",
                            "The two halves are sign-extended separately",
                            "The upper half is optional",
                        ],
                        "a": 0,
                        "why": r"""
A store needs two source registers and no destination, so `rs2` occupies bits 24:20 —
right where an I-type immediate would have been. The immediate has to go round it, and
the pieces land in the `rd` slot and the `funct7` slot. Twelve contiguous bits do exist
elsewhere in the word; using them would have moved `rs1` or `rs2`, and that is the one
thing the design will not do. Both halves are one number, sign-extended once.
""",
                    },
                    {
                        "q": "Branch offsets are stored without their least significant bit. Why can they be?",
                        "opts": [
                            "Instruction addresses are even, so that bit is always zero",
                            "Branches can only jump forwards",
                            "The bit is stored in the opcode instead",
                            "It doubles the number of registers that can be addressed",
                        ],
                        "a": 0,
                        "why": r"""
With the compressed extension present, instructions are 2-byte aligned, so a target
address always has bit 0 clear and storing it would waste a bit. Dropping it doubles
the reach of the same field: a 12-bit encoded field becomes a 13-bit signed byte
offset, $\pm 4$ KiB. The same trick, one bit further, is what gives J-type its
$\pm 1$ MiB range.
""",
                    },
                ],
            },
            "lab": {
                "title": "Write an RV32I decoder",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Take a 32-bit word apart into the fields the datapath needs. Four functions.

`bits(word, hi, lo)` returns the inclusive slice `word[hi:lo]` as an unsigned
integer — `bits(0xFF, 3, 0)` is 15.

`sign_extend(value, width)` treats a `width`-bit unsigned `value` as two's
complement and returns a Python `int` of the right sign.

`immediate(word, fmt)` assembles the immediate for one format and sign-extends
it. This is the part that is not mechanical:

```text
I   imm[11:0]  = word[31:20]
S   imm[11:5]  = word[31:25],  imm[4:0]  = word[11:7]
B   imm[12]    = word[31],     imm[11]   = word[7],
    imm[10:5]  = word[30:25],  imm[4:1]  = word[11:8],   imm[0] = 0
U   imm[31:12] = word[31:12],  imm[11:0] = 0
J   imm[20]    = word[31],     imm[19:12]= word[19:12],
    imm[11]    = word[20],     imm[10:1] = word[30:21],  imm[0] = 0
```

R has no immediate: return `None`.

`decode(word)` puts it together and returns a dict with the keys `fmt`, `opcode`,
`rd`, `rs1`, `rs2`, `funct3`, `funct7`, `imm` — with **`None` for every field the
format does not define**. That last rule is the whole point: those bit positions
still hold something, and reporting the something as a register number is how a
decoder bug becomes a silent wrong answer.
''',
                "files": [{"name": "main.py", "content": r'''
# Opcode to format. Reference-manual data, not something to derive.
OPCODES = {
    0x33: "R",   # add sub sll slt xor srl or and
    0x13: "I",   # addi slti xori ori andi
    0x03: "I",   # lw
    0x23: "S",   # sw
    0x63: "B",   # beq bne blt bge
    0x37: "U",   # lui
    0x6F: "J",   # jal
}

HAS_RD = ("R", "I", "U", "J")
HAS_RS1 = ("R", "I", "S", "B")
HAS_RS2 = ("R", "S", "B")
HAS_FUNCT3 = ("R", "I", "S", "B")


def bits(word, hi, lo):
    """The inclusive slice word[hi:lo], as an unsigned integer."""
    # TODO: shift down by lo, then mask off (hi - lo + 1) bits.
    return 0


def sign_extend(value, width):
    """Read a width-bit unsigned value as two's complement."""
    # TODO: if the top bit is set, the value is negative.
    return value


def immediate(word, fmt):
    """Assemble and sign-extend the immediate of one format. R has none."""
    word &= 0xFFFFFFFF
    # TODO: one branch per format, following the table in the brief.
    return 0


def decode(word):
    """Every field of one instruction, with None where the format has none."""
    word &= 0xFFFFFFFF
    # TODO: read the six raw slices, look up the format, and blank the fields
    # this format does not define.
    return {"fmt": None, "opcode": None, "rd": None, "rs1": None, "rs2": None,
            "funct3": None, "funct7": None, "imm": None}


if __name__ == "__main__":
    for word in (0x00500093, 0x002081B3, 0xFE512E23, 0xFE209EE3):
        print("0x%08X" % word, decode(word))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
# Opcode to format. Reference-manual data, not something to derive.
OPCODES = {
    0x33: "R",   # add sub sll slt xor srl or and
    0x13: "I",   # addi slti xori ori andi
    0x03: "I",   # lw
    0x23: "S",   # sw
    0x63: "B",   # beq bne blt bge
    0x37: "U",   # lui
    0x6F: "J",   # jal
}

HAS_RD = ("R", "I", "U", "J")
HAS_RS1 = ("R", "I", "S", "B")
HAS_RS2 = ("R", "S", "B")
HAS_FUNCT3 = ("R", "I", "S", "B")


def bits(word, hi, lo):
    """The inclusive slice word[hi:lo], as an unsigned integer."""
    return (word >> lo) & ((1 << (hi - lo + 1)) - 1)


def sign_extend(value, width):
    """Read a width-bit unsigned value as two's complement."""
    top = 1 << (width - 1)
    return (value & (top - 1)) - (value & top)


def immediate(word, fmt):
    """Assemble and sign-extend the immediate of one format. R has none."""
    word &= 0xFFFFFFFF
    if fmt == "R":
        return None
    if fmt == "I":
        return sign_extend(bits(word, 31, 20), 12)
    if fmt == "S":
        return sign_extend((bits(word, 31, 25) << 5) | bits(word, 11, 7), 12)
    if fmt == "B":
        raw = (bits(word, 31, 31) << 12) | (bits(word, 7, 7) << 11) | \
              (bits(word, 30, 25) << 5) | (bits(word, 11, 8) << 1)
        return sign_extend(raw, 13)
    if fmt == "U":
        return sign_extend(bits(word, 31, 12), 20) << 12
    raw = (bits(word, 31, 31) << 20) | (bits(word, 19, 12) << 12) | \
          (bits(word, 20, 20) << 11) | (bits(word, 30, 21) << 1)
    return sign_extend(raw, 21)


def decode(word):
    """Every field of one instruction, with None where the format has none."""
    word &= 0xFFFFFFFF
    opcode = bits(word, 6, 0)
    fmt = OPCODES.get(opcode)
    if fmt is None:
        raise ValueError("unknown opcode 0x%02x" % opcode)
    return {
        "fmt": fmt,
        "opcode": opcode,
        "rd": bits(word, 11, 7) if fmt in HAS_RD else None,
        "rs1": bits(word, 19, 15) if fmt in HAS_RS1 else None,
        "rs2": bits(word, 24, 20) if fmt in HAS_RS2 else None,
        "funct3": bits(word, 14, 12) if fmt in HAS_FUNCT3 else None,
        "funct7": bits(word, 31, 25) if fmt == "R" else None,
        "imm": immediate(word, fmt),
    }


if __name__ == "__main__":
    for word in (0x00500093, 0x002081B3, 0xFE512E23, 0xFE209EE3):
        print("0x%08X" % word, decode(word))
'''}],
                "hints": [
                    "`bits(word, hi, lo)` is `(word >> lo) & ((1 << (hi - lo + 1)) - 1)` — write it once and never index bits by hand again.",
                    "Sign extension without a branch: `(value & (top - 1)) - (value & top)` where `top = 1 << (width - 1)`.",
                    "For B and J, build the raw immediate *including* the always-zero bit 0, then sign-extend at 13 and 21 bits respectively — not 12 and 20.",
                ],
                "tests": [
                    {"name": "the register fields sit at fixed positions", "code": r'''
_add = decode(0x002081B3)   # add x3, x1, x2
assert _add["fmt"] == "R", f"opcode 0x33 is the R format, got {_add['fmt']!r}"
assert (_add["rd"], _add["rs1"], _add["rs2"]) == (3, 1, 2), \
    f"rd/rs1/rs2 live at bits 11:7, 19:15, 24:20 — got {(_add['rd'], _add['rs1'], _add['rs2'])}"
_sub = decode(0x407302B3)   # sub x5, x6, x7
assert _sub["funct7"] == 0x20, \
    f"sub is add with funct7 = 0x20 at bits 31:25, got {_sub['funct7']}"
assert _sub["imm"] is None, "an R-type word carries no immediate at all"
'''},
                    {"name": "an I immediate is sign-extended from twelve bits", "code": r'''
assert decode(0x00500093)["imm"] == 5, "addi x1, x0, 5 has immediate 5"
_neg = decode(0xFFF08113)   # addi x2, x1, -1
assert _neg["imm"] == -1, \
    f"0xFFF is -1 in twelve-bit two's complement, not 4095 — got {_neg['imm']}"
assert decode(0x00812203)["imm"] == 8, "lw x4, 8(x2) is an I-type with immediate 8"
'''},
                    {"name": "an S immediate is glued back together from two pieces", "code": r'''
assert decode(0x00512623)["imm"] == 12, "sw x5, 12(x2) stores at offset +12"
_back = decode(0xFE512E23)   # sw x5, -4(x2)
assert _back["imm"] == -4, \
    f"S splits the immediate across bits 31:25 and 11:7 — got {_back['imm']}"
assert _back["rs2"] == 5 and _back["rs1"] == 2, \
    "the value stored is rs2 and the address base is rs1"
'''},
                    {"name": "a B immediate is scrambled, and always even", "code": r'''
assert decode(0x00208463)["imm"] == 8, "beq x1, x2, 8 jumps eight bytes forward"
assert decode(0xFE209EE3)["imm"] == -4, \
    "bne x1, x2, -4 branches backwards; bit 12 is the sign and lives at word bit 31"
_far = decode(0x800002E3)   # beq x0, x0, -2044
assert _far["imm"] == -2044, f"expected -2044, got {_far['imm']}"
assert _far["imm"] % 2 == 0, "bit 0 of a branch offset is not stored, so it is always 0"
'''},
                    {"name": "U puts its twenty bits at the top and J is the worst of them", "code": r'''
assert decode(0x123453B7)["imm"] == 0x12345000, \
    "lui shifts its twenty bits up by twelve; the low twelve bits are zero"
assert decode(0xFFFFF2B7)["imm"] == -4096, \
    "the U immediate is signed once placed: 0xFFFFF000 is -4096"
assert decode(0x008000EF)["imm"] == 8, "jal x1, 8"
assert decode(0xFF9FF0EF)["imm"] == -8, \
    "the J immediate takes bit 11 from word bit 20 and bits 10:1 from 30:21"
assert decode(0x7FC0006F)["imm"] == 2044, "jal x0, 2044"
'''},
                    {"name": "fields the format does not define are reported as absent", "code": r'''
_sw = decode(0x00512623)    # sw x5, 12(x2)
assert _sw["rd"] is None, \
    "bits 11:7 of a store are immediate bits, not a destination register"
_b = decode(0x00208463)     # beq x1, x2, 8
assert _b["rd"] is None, "a branch writes no register"
_lui = decode(0x123453B7)
assert _lui["rs1"] is None and _lui["rs2"] is None, \
    "U has no source registers; bits 19:15 are part of its immediate"
assert _lui["funct3"] is None, \
    "there is no funct3 in U or J — those three bits belong to the immediate"
_jal = decode(0xFF9FF0EF)
assert _jal["rd"] == 1 and _jal["rs1"] is None, "jal writes the return address to rd"
'''},
                    {"name": "the primitives work on their own", "code": r'''
assert bits(0xFFFFFFFF, 3, 0) == 15, "a four-bit slice of all ones is 15"
assert bits(0x000000FF, 15, 8) == 0, "bits 15:8 of 0x000000FF are zero"
assert bits(0x12345678, 31, 28) == 1, "the top nibble of 0x12345678 is 1"
assert sign_extend(0xFFF, 12) == -1, "0xFFF as a signed twelve-bit value is -1"
assert sign_extend(0x7FF, 12) == 2047, "0x7FF is the largest positive twelve-bit value"
assert sign_extend(0x800, 12) == -2048, "0x800 is the most negative twelve-bit value"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Hazards, and the cost of a bubble",
            "summary": "Five instructions in flight means five instructions that can get in each other's way. Count the cycles it costs.",
            "concepts": [
                "Structural hazard: two instructions want the same piece of hardware in the same cycle. Split instruction and data memory and most of them disappear.",
                "Data hazard (RAW): an instruction reads a register a still-in-flight instruction has not written yet.",
                "Control hazard: the next fetch address is not known until the branch has been resolved.",
                "The register file writes in the first half of WB and reads in the second half of ID, so a consumer's ID may sit in the *same* cycle as the producer's WB — this is worth two bubbles, and it is the difference between two and three in every textbook table.",
                "Which registers an instruction actually reads is a property of its *format*, not its mnemonic: a store reads two and writes none, a branch reads two and writes none, `lui` reads none.",
            ],
            "read": [
                {
                    "title": "Where the eight cycles went",
                    "minutes": 15,
                    "body": r'''
Two instructions, drawn against a cycle counter:

```text
cycle       0    1    2    3    4    5    6    7    8
addi x1     IF   ID   EX  MEM   WB
add  x2          IF   ID   EX  MEM   WB
```

`add x2, x1, x1` reads `x1` in its ID, which the diagram puts in cycle 2. The
`addi` writes `x1` in its WB, which the diagram puts in cycle 4. The read happens
two cycles before the write. Nothing in the drawing is wrong; the drawing is what
the hardware does if nobody stops it, and what it does is hand the `add` whatever
`x1` held before the program started.

So the `add` has to be held back. How far? The register file is written in the
first half of a cycle and read in the second half of the same cycle — a
half-cycle trick that costs a latch and no extra time — so the earliest legal ID
for the consumer is cycle 4, the same cycle as the producer's WB. ID is one cycle
after IF, so the consumer's IF moves from cycle 1 to cycle 3, and the fixed
diagram is:

```text
cycle       0    1    2    3    4    5    6    7    8
addi x1     IF   ID   EX  MEM   WB
add  x2                    IF   ID   EX  MEM   WB
```

Two cycles of nothing. Written as a rule over issue cycles, with instruction $i$
entering IF in cycle $s_i$: a consumer that reads a register written by
instruction $j$ obeys $s_i \ge s_j + 3$, alongside the in-order rule
$s_i \ge s_{i-1} + 1$ that applies to everything. The 3 is not a constant anyone
chose. It is $4 - 1$: WB is four stages after IF, ID is one stage after IF, and
the difference is how far the consumer must slide.

That subtraction is where a whole family of disagreements between textbooks comes
from. Drop the half-cycle register file and the consumer's ID may not sit in the
same cycle as the producer's WB, only after it — so the earliest ID is cycle 5,
the earliest IF is cycle 4, and the rule becomes $s_i \ge s_j + 4$: three bubbles
instead of two. Both tables are correct about their own machine. The number 3 in
this course is a claim about the register file, and every cycle count below rests
on it.

## What it costs on real code

Two bubbles per dependence sounds survivable until you count them on something
that computes. Here is a kernel that loads a word, adds to it and stores it
back — six instructions, no branches, nothing pathological:

```python
# addi x1,x0,10 / addi x2,x0,20 / add x3,x1,x2 / lw x4,0(x3) / add x5,x4,x1 / sw x5,4(x3)
# Sources listed as register numbers; x0 is hard-wired to zero and never stalls.
PROG = [("addi x1", 1, []), ("addi x2", 2, []), ("add  x3", 3, [1, 2]),
        ("lw   x4", 4, [3]), ("add  x5", 5, [4, 1]), ("sw   x5", None, [3, 5])]

starts, writer, stalls = [], {}, 0
for i, (text, dest, srcs) in enumerate(PROG):
    inorder = 0 if i == 0 else starts[-1] + 1
    earliest, reason = inorder, "in order"
    for r in srcs:
        if r in writer and starts[writer[r]] + 3 > earliest:
            earliest, reason = starts[writer[r]] + 3, "waits on x%d" % r
    stalls += earliest - inorder
    starts.append(earliest)
    if dest is not None:
        writer[dest] = i
    print("%s  IF in cycle %2d  (%s)" % (text, earliest, reason))
print("stall cycles: %d   total: %d   ideal: %d" % (stalls, starts[-1] + 5, len(PROG) + 4))
print("CPI %.2f against an ideal %.2f" % ((starts[-1] + 5) / len(PROG), (len(PROG) + 4) / len(PROG)))
```

Eighteen cycles for six instructions, against ten if nothing had stalled. CPI 3.00
where the hardware is built for 1.00 and the fill cost alone would have given
1.67. Eight of the eighteen cycles are a pipeline holding still.

Read the reasons column, because it says something the totals hide. There are
seven read-after-write dependences in those six instructions, and only four of
them cost anything: `x2` into the `add`, `x3` into the `lw`, `x4` into the second
`add`, `x5` into the `sw`. The other three — `x1` into the first `add`, `x1` into
the second, `x3` into the `sw` — are covered by a stall some other operand had
already forced, or by distance. That is the general shape. A dependence is not a
stall; a dependence whose producer is fewer than three instructions back is a
stall, and only the tightest one on each instruction is charged for.

Three instructions back is the threshold, and it follows from the same
subtraction: if $s_i \ge s_j + 3$ and in-order issue has already given
$s_i = s_j + 3$ because two instructions sit between them, the constraint is
satisfied with nothing to add. This is why `nop, nop` between a producer and a
consumer costs the same two cycles as a stall would have — and why a compiler
that has two useful instructions to put there gets those two cycles free.

## What the number becomes over a long run

The kernel above spends 8 stall cycles on 6 instructions, a stall rate of 1.33
per instruction. That rate is what survives; the fill cost is not.

```python
def cpi(N, D, S):
    """N instructions, D stages, S stall cycles in total."""
    return (N + (D - 1) + S) / N

print("the six-instruction kernel      : %.3f" % cpi(6, 5, 8))
print("the same stall rate, N = 1000000: %.3f" % cpi(10**6, 5, 8 * 10**6 // 6))
print("no stalls at all, N = 1000000   : %.3f" % cpi(10**6, 5, 0))
for f1, f2 in ((0.30, 0.15), (0.10, 0.10)):
    print("f1=%.2f f2=%.2f -> CPI %.2f" % (f1, f2, 1 + 2 * f1 + f2))
```

Between the first line and the second, only $N$ changed: 3.000 falls to 2.333
because the four fill cycles are spread over a million instructions instead of
six, and there the improvement stops. The stall term $S/N$ does not shrink,
because $S$ grows with $N$. A deeper pipeline pays more for the fill and exactly
the same for each bubble — depth is free in steady state and expensive only in
what it does to branch penalties, which is module 4. This is the arithmetic the
fill-in exercise *Counting cycles in a five-stage pipe* asks you to assemble line
by line.

The last two lines are the same statement in the form a measurement usually
arrives in. Instead of a stall total, a profiler gives fractions: $f_1$ of
instructions have their nearest producer one ahead, worth two bubbles each, and
$f_2$ have it two ahead, worth one. CPI is then $1 + 2f_1 + f_2$, and the
compiled kernel measured in *Cycles, stalls and CPI* — $f_1 = 0.30$,
$f_2 = 0.15$ — gives 1.75. A machine running at $1/1.75$ of its peak is throwing
away 43% of the throughput the pipeline was built to deliver, on nothing but
register dependences.

## The mistake that survives review

Ask which registers an instruction reads and the honest answer comes from its
*format*, not from how the assembly line looks. The trap is the store:

```python
PAIR = [("add  x5, x1, x2", 5, []), ("sw   x5, 0(x10)", None, [10, 5])]
starts, writer = [], {}
for i, (text, dest, srcs) in enumerate(PAIR):
    t = 0 if i == 0 else starts[-1] + 1
    for r in srcs:
        if r in writer:
            t = max(t, starts[writer[r]] + 3)
    starts.append(t)
    if dest is not None:
        writer[dest] = i
print("store reads rs2   :", starts, "->", starts[-1] + 5, "cycles")

writer, starts = {}, []
for i, (text, dest, srcs) in enumerate(PAIR):
    t = 0 if i == 0 else starts[-1] + 1
    for r in (srcs[:1] if i else srcs):          # the address base alone
        if r in writer:
            t = max(t, starts[writer[r]] + 3)
    starts.append(t)
    if dest is not None:
        writer[dest] = i
print("address base alone:", starts, "->", starts[-1] + 5, "cycles")
```

Eight cycles against six: a hazard unit that tracks only the address base misses
this pair entirely and reports six cycles where the hardware takes eight, a
quarter of the run unaccounted for.
The reason the bug is tempting is written into the assembly syntax. In
`add x5, x1, x2` the register directly after the mnemonic is the destination; in
`sw x5, 0(x10)` the register in that same position is a *source*, the value being
written to memory. The syntax puts a read where the eye has learned to expect a
write, and `sw` is the only instruction in this subset that does it. Decode the
format instead of the text and the question does not arise: S reads `rs1` and
`rs2` and writes nothing, B does the same, `lui` reads neither. The lab's check
*the value a store writes to memory is a read too* is this pair, expecting
`[0, 3]`.

## Where this model stops describing a machine

Three simplifications are load-bearing here and get removed later or never.

There is no forwarding in any of the above, which is why the numbers are as bad
as they are. Module 3 adds it and most of the eight cycles disappear.

Memory always answers in one cycle. A real data cache misses, and a miss is worth
tens of cycles — more than every hazard on this page put together. The model says
nothing about it, and a CPI computed here is a floor, not a prediction.

Write-after-write and write-after-read hazards do not appear, and their absence
is a property of the machine rather than of the programs. Instructions issue in
order, one at a time, and every one writes its register in WB, in issue order, so
a later instruction cannot possibly write before an earlier one; and every read
happens in ID, before any later instruction has reached WB. Reorder the
instructions, or add a second issue slot, and both hazards come back immediately —
which is exactly what the register renaming in an out-of-order machine exists to
handle.

Two units in this module make the counting concrete. The sandbox *What a bubble
costs* draws the same nine instructions with the dependence count on a slider:
push it to 6 and the caption goes from CPI 1.44 to 2.78 without a single
instruction changing. Then the lab, *A stalling pipeline model*, asks for
`sources`, `destination` and `schedule` over programs assembled from text — the
same rule as the block above, applied to real decoded words, with the store as
the check that separates a model from a guess.
''',
                },
            ],
            "quiz": {
                "title": "Counting the cycles a dependence costs",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A producer enters IF in cycle $c$ and the very next instruction reads the register it writes. Why is the consumer held to $s \\ge c + 3$ rather than $s \\ge c + 4$?",
                        "opts": [
                            "The register file is written in the first half of a cycle and read in the second half, so the consumer's ID may share the producer's WB cycle",
                            "The producer's result already exists at the end of its EX stage, so the consumer is able to pick it up two whole stages before it ever reaches the register file",
                            "The stall is measured from ID rather than from IF, and ID is one stage later than IF for both instructions",
                            "The last stage of the producer overlaps the first stage of the consumer whenever they are adjacent in program order",
                        ],
                        "a": 0,
                        "whys": [
                            r"Write in the first half of cycle $c+4$, read in the second half of the same cycle, so ID at $c+4$ is legal and IF at $c+3$ follows.",
                            r"True of the hardware and irrelevant to this model — that is forwarding, and no operand in this module travels by any route other than the register file. Without a forwarding path, the value is unreadable until WB has written it, whatever the ALU finished and when.",
                            r"Both instructions have ID one stage after IF, so measuring from ID rather than IF subtracts the same 1 from each side and changes nothing at all. The 3 comes from $4 - 1$: the producer's WB against the consumer's ID.",
                            r"Nothing overlaps between adjacent instructions beyond the ordinary one-cycle skew every pair has. The half-cycle split inside the register file is a real mechanism; a stage overlapping a stage is not.",
                        ],
                        "why": r"""
The 3 is $4 - 1$: the producer writes in WB, four stages after its IF, and the
consumer reads in ID, one stage after its own IF. Making those meet needs
$s_i + 1 \ge s_j + 4$. The half-cycle register file is what allows them to *meet*
rather than merely miss — write in the first half, read in the second — and
without it the answer is $s_i \ge s_j + 4$, three bubbles instead of two. That
one design choice is the difference between the two-bubble and three-bubble
tables in different textbooks, and neither is wrong about its own machine.
""",
                    },
                    {
                        "q": "`add x5, x1, x2` is followed immediately by `sw x5, 0(x10)`. What does the pair cost on the no-forwarding model?",
                        "opts": [
                            "Nothing: a store has no destination register, so it cannot be in a read-after-write dependence",
                            "Two bubbles: the stored value is `rs2`, and a store reads it the same way any instruction reads a source",
                            "One bubble: the store needs the value in MEM rather than in EX, so it is a stage later than an ALU use",
                            "Two bubbles, forced by `x10` rather than by `x5`, since the address base is what the store computes with",
                        ],
                        "a": 1,
                        "whys": [
                            r"Having no destination stops a store from being the *producer* of a hazard, never the consumer. It reads two registers, and reading is what a read-after-write dependence is about.",
                            r"$s_i \ge s_j + 3$ with the store one instruction behind, so it issues in cycle 3 rather than 1, and the pair takes 8 cycles instead of 6.",
                            r"The MEM-versus-EX distinction is real, and it is what makes this pair free once forwarding exists. With no forwarding at all there is only one rule, $s_i \ge s_j + 3$, and the use stage does not enter it.",
                            r"`x10` is written by nothing in this pair, so it constrains nothing. The binding dependence is `x5`, which the `add` produced one instruction earlier.",
                        ],
                        "why": r"""
A store reads two registers: `rs1` for the address base and `rs2` for the value
it writes to memory. `x5` is `rs2` here, so the ordinary rule applies and the
store issues in cycle 3 rather than 1 — eight cycles for the pair against six.
What makes the bug tempting is the assembly syntax: in `add x5, x1, x2` the
register after the mnemonic is written, and in `sw x5, 0(x10)` the register in
that same position is read. Decoding the format rather than reading the line
removes the ambiguity, since S reads `rs1` and `rs2` and writes nothing.
""",
                    },
                    {
                        "q": "Six instructions in this course's kernel contain seven read-after-write dependences, and the schedule stalls for only four of them. What accounts for the other three?",
                        "opts": [
                            "Their producers write registers that a later instruction overwrites before the read happens",
                            "They are dependences on `x0`, which is hard-wired to zero and never causes an interlock",
                            "Their producers are far enough back, or a tighter dependence on the same instruction has already forced the wait",
                            "The scheduler charges one stall per instruction at most, so extra dependences on the same instruction are dropped",
                        ],
                        "a": 2,
                        "whys": [
                            r"Overwriting a register later has no effect on a read that already happened; each read is matched to the most recent writer *before* it, and that writer's dependence stands.",
                            r"`x0` really is exempt, and the kernel's `addi x1, x0, 10` reads it — but nothing in the kernel writes `x0`, so no `x0` dependence was ever counted among the seven.",
                            r"A dependence binds only when $s_j + 3$ exceeds what in-order issue already gives.",
                            r"Nothing is dropped: every dependence is evaluated and the constraint is a maximum over all of them. Three of the seven lose the maximum rather than being ignored.",
                        ],
                        "why": r"""
Each instruction takes the maximum over its constraints, so a dependence costs
nothing when some other constraint already dominates it. Two things dominate
here: distance, since a producer three or more instructions back has already
satisfied $s_i \ge s_j + 3$ through in-order issue alone, and a tighter sibling
dependence on the same consumer. Both `x1` uses in the kernel lose to a nearer
producer, and `x3` into the `sw` loses to distance. The general rule worth taking
away is that a dependence is not a stall — only the binding one is.
""",
                    },
                    {
                        "q": "Why does a five-stage in-order pipeline never have to detect write-after-write hazards?",
                        "opts": [
                            "Every instruction writes in WB and instructions reach WB in issue order, so an earlier write cannot land after a later one",
                            "The compiler removes them by renaming registers before the program ever reaches the hardware",
                            "A write-after-write conflict is caught by the same interlock that handles read-after-write dependences",
                            "Two writes to the same register in a five-stage pipeline are always separated by at least three intervening instructions in program order",
                        ],
                        "a": 0,
                        "whys": [
                            r"One write stage, entered in issue order, so the writes are already in program order for free.",
                            r"Compilers do allocate registers, and they cheerfully emit two writes to the same register a few instructions apart. What makes those safe is the hardware's single in-order write stage, not anything the compiler did.",
                            r"The read-after-write interlock compares a consumer's sources against earlier destinations; it never compares two destinations, so it would not notice a write-after-write conflict if one could occur.",
                            r"Nothing enforces a gap between two writes to the same register — `addi x1, x0, 1` followed by `addi x1, x0, 2` is legal and common. The ordering is safe because of where writes happen, not how far apart they are.",
                        ],
                        "why": r"""
There is exactly one stage that writes the register file, instructions enter it
in issue order, and one instruction enters it per cycle. Two writes to the same
register therefore land in program order with no hardware asked to check
anything. The same argument covers write-after-read: every read happens in ID,
which is earlier than any later instruction's WB. Both hazards return the moment
either assumption goes — reorder the instructions, or add a second issue slot,
and register renaming becomes necessary rather than decorative.
""",
                    },
                    {
                        "q": "The kernel costs 18 cycles for 6 instructions, a CPI of 3.00. Run the same code with the same stall rate over a million instructions and the CPI settles at 2.33. What changed?",
                        "opts": [
                            "The stalls overlap once enough instructions are in flight to hide them",
                            "The four cycles of pipeline fill are spread over a million instructions instead of six",
                            "Longer runs let the register file's same-cycle write-then-read path cover more of the dependences",
                            "The measured stall rate falls as the working set warms up and fewer operands come from memory",
                        ],
                        "a": 1,
                        "whys": [
                            r"Stalls do not overlap in an in-order single-issue pipeline: every bubble is a cycle in which no instruction is issued, and two bubbles are two such cycles whatever else is in flight.",
                            r"$(D-1)/N$ goes to zero; $S/N$ does not, because $S$ grows with $N$.",
                            r"The same-cycle write-then-read path is what makes the penalty two cycles rather than three, and it applies to every dependence from the first instruction onward. Nothing about it improves with run length.",
                            r"This model has one memory latency and it never changes; there is no cache in it at all. On a real machine warming a cache moves CPI the other way at the start of a run, and it is a far larger effect than anything here.",
                        ],
                        "why": r"""
CPI is $1 + (D-1)/N + S/N$. The fill term is a fixed four cycles divided by a
growing $N$, so it vanishes; the stall term does not, because $S$ grows in
proportion to $N$. What is left, 1.33 stall cycles per instruction, is the
program's own property. The practical consequence is that pipeline depth is
nearly free in steady state — a deeper pipe pays more fill, once — and that the
number worth quoting from a profile is the stall rate rather than a cycle total,
because only the rate compares across programs of different lengths.
""",
                    },
                    {
                        "q": "Splitting the single memory into separate instruction and data memories removes most structural hazards. Which conflict does the split actually resolve?",
                        "opts": [
                            "A load in MEM and an instruction fetch in IF wanting the same memory port in the same cycle",
                            "Two instructions in EX at once, which a single ALU cannot serve",
                            "A store in MEM and a write-back in WB competing for the register file's write port",
                            "An instruction fetch and a branch target calculation both needing the adder in the same cycle",
                        ],
                        "a": 0,
                        "whys": [
                            r"With five stages in flight, some instruction is in MEM in the same cycle another is in IF, and a load or store makes that a genuine two-port demand.",
                            r"Two instructions are never in EX at once in a single-issue pipeline — one stage holds one instruction per cycle, which is what the stages are for. That conflict belongs to a superscalar machine.",
                            r"A store writes memory and no register at all, so it never contends for the register file's write port. One write port serves the machine because only WB writes, one instruction per cycle.",
                            r"The target adder is a separate adder precisely so this does not arise, and it is a handful of gates. Duplicating small combinational logic is the cheap fix; duplicating a memory port is the expensive one, which is why the memory case is the interesting one.",
                        ],
                        "why": r"""
In steady state one instruction is in IF while another is in MEM every single
cycle, so a unified memory would need two accesses per cycle whenever the older
instruction is a load or a store. Separate instruction and data memories — in
practice separate level-one caches behind a shared level two — give each stage
its own port and the hazard disappears. The general principle is that a
structural hazard is a resource shortage rather than a data problem, so the fix
is duplication rather than an interlock. The residue is the register file, and
that is handled by making the write and the read happen in different halves of
the same cycle.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "What a bubble costs",
                "visualiser": "pipeline",
                "minutes": 8,
                "initial": {"dep": 3, "fwd": 0, "miss": 0},
                "brief": r'''
The same nine instructions as before, with forwarding switched off. The
`dependent pairs` slider makes the first *n* instructions after `i0` read a
register the instruction above them writes. Watch where the rows go.
''',
                "notice": [
                    "Rows i1, i2 and i3 each start three cycles after the row above rather than one, while i4 downwards keep the one-cycle spacing — only the first `dep` instructions are made dependent, and each dependence costs exactly two cycles on top of the one the instruction was going to take anyway.",
                    "Push dependent pairs to 6 and read the caption: the same nine instructions now take 25 cycles instead of 13, CPI 2.78 instead of 1.44. Nothing about the instructions changed, only what they read.",
                    "Notice what is *not* drawn: there is no cell marked `bubble`. A stall is only visible as a gap between one row's start and the next, which is exactly how it appears on a waveform — a stage holding its previous contents while nothing new arrives.",
                ],
            },
            "derive": {
                "title": "Cycles, stalls and CPI",
                "minutes": 15,
                "vars": ["N", "k", "c", "f_1", "f_2", "CPI"],
                "brief": r'''
Number the stages IF = 0 through WB = 4, and let instruction $i$ enter IF in
cycle $s_i$. In-order issue means $s_i \ge s_{i-1} + 1$: no instruction may start
before the one in front of it.

The register file is written in the first half of a cycle and read in the second
half of one, so a consumer may read in the *same* cycle its producer writes.
''',
                "steps": [
                    {
                        "prompt": "With no stalls at all, how many cycles does a $k$-stage pipeline take to retire $N$ instructions? Write it in terms of $N$ and $k$.",
                        "answer": "N + k - 1",
                        "hint": "The first instruction takes $k$ cycles on its own; each of the remaining $N-1$ adds one.",
                        "deconstruct": [
                            "Filling the pipeline costs $k$ cycles before the first instruction retires.",
                            "After that one instruction retires per cycle, so $N - 1$ more.",
                            "$k + (N-1) = N + k - 1$.",
                        ],
                    },
                    {
                        "prompt": "Write the CPI that corresponds to it.",
                        "answer": "\\frac{N + k - 1}{N}",
                        "hint": "CPI is cycles divided by instructions retired.",
                        "deconstruct": [
                            "Divide the cycle count by $N$.",
                            "For $k=5$ and $N=1000$ that is 1.004 — the fill cost is real but it is not what makes CPI bad.",
                        ],
                    },
                    {
                        "prompt": "A producer enters IF in cycle $c$. In which cycle is it in WB, writing the register file?",
                        "answer": "c + 4",
                        "hint": "IF is stage 0 and WB is stage 4, one cycle each.",
                        "deconstruct": [
                            "The stages are IF, ID, EX, MEM, WB at cycles $c$, $c+1$, $c+2$, $c+3$, $c+4$.",
                        ],
                    },
                    {
                        "prompt": "A consumer of that register must have its ID no earlier than cycle $c+4$. ID is one cycle after IF, so write the earliest cycle the consumer may enter IF.",
                        "answer": "c + 3",
                        "hint": "If ID must be at $c+4$ and ID is IF plus one, then IF is at $c+4-1$.",
                        "deconstruct": [
                            "The write happens in the first half of $c+4$ and the read in the second half of the same cycle, so ID at $c+4$ is legal.",
                            "IF is one cycle earlier: $c + 3$.",
                        ],
                    },
                    {
                        "prompt": "The instruction immediately behind the producer would otherwise have entered IF in cycle $c+1$. How many bubbles does the stall insert?",
                        "answer": "2",
                        "hint": "Subtract the natural issue cycle from the earliest legal one.",
                        "deconstruct": [
                            "Earliest legal IF is $c+3$; the natural one is $c+1$.",
                            "$(c+3) - (c+1) = 2$ cycles of nothing.",
                        ],
                    },
                    {
                        "prompt": "Let $f_1$ be the fraction of instructions whose nearest producer is one instruction ahead, and $f_2$ the fraction whose nearest producer is two ahead (worth one bubble). Write the CPI, ignoring the fill cost.",
                        "answer": "1 + 2 \\cdot f_1 + f_2",
                        "hint": "Start from one cycle per instruction and add the average number of bubbles per instruction.",
                        "deconstruct": [
                            "Every instruction costs one cycle to begin with.",
                            "A fraction $f_1$ of them adds two, and a fraction $f_2$ adds one.",
                        ],
                    },
                    {
                        "prompt": "Measurements on a compiled kernel give $f_1 = 0.30$ and $f_2 = 0.15$. What is the CPI?",
                        "answer": "1.75",
                        "hint": "Substitute into the expression you just wrote.",
                        "deconstruct": [
                            "$2 \\times 0.30 = 0.60$ and $f_2 = 0.15$.",
                            "$1 + 0.60 + 0.15 = 1.75$ — at $1/1.75$ the machine is doing 57% of its peak.",
                        ],
                    },
                ],
                "closing": r'''
A CPI of 1.75 on a machine whose peak is 1.0 is not a rounding error; it is 43%
of the throughput thrown away on nothing but register dependences, which every
compiled program is full of. The next module removes almost all of it with a
comparator on each source register and one multiplexer in front of each ALU
input.
''',
            },
            "blanks": {
                "title": "Counting cycles in a five-stage pipe",
                "minutes": 8,
                "caption": "cpi.py — fill, stalls, and what CPI actually converges to",
                "lang": "python",
                "brief": r"""
Every claim a microarchitect makes reduces to this arithmetic. Fill it in once and the
rest of the course is bookkeeping.

`N` instructions through a `D`-stage pipeline, with `S` stall cycles inserted in total.
""",
                "listing": """D = 5                       # stages
# The first instruction takes D cycles; every one after it retires one per cycle,
# so a pipeline with no hazards at all finishes N instructions in
cycles_ideal = N + ___

# Each stall inserts one bubble, and bubbles simply add:
cycles = N + (D - 1) + ___

# Cycles per instruction is that, over N:
CPI = 1 + (D - 1) / N + ___

# For large N the fill term vanishes and CPI tends to
CPI_large_N = 1 + ___
""",
                "blanks": [
                    {
                        "prompt": "The fill cost: how many cycles before the first result appears?",
                        "hole": "?",
                        "opts": ["D - 1", "D", "N", "0"],
                        "a": 0,
                        "why": "Four extra cycles for a five-stage pipe. The first instruction needs all $D$ cycles, but $D-1$ of those overlap with nothing, so the total is $N + (D-1)$ — one cycle per instruction plus the fill.",
                        "whys": [
                            "Four extra cycles for a five-stage pipe. The first instruction needs all $D$ cycles, but $D-1$ of those overlap with nothing, so the total is $N + (D-1)$ — one cycle per instruction plus the fill.",
                            "Off by one: this counts the first instruction twice, once in $N$ and once in $D$. Check it against $N = 1$, where the answer must be exactly $D$.",
                            "That would make the pipeline take $2N$ cycles regardless of depth, which is the cost of no pipelining at all.",
                            "Only true for an infinitely deep-throughput machine with no start-up, which is the approximation the last line makes on purpose — but not the exact count.",
                        ],
                    },
                    {
                        "prompt": "S bubbles have been inserted. How do they enter the total?",
                        "hole": "?",
                        "opts": ["S", "S * N", "4 * S", "S / N"],
                        "a": 0,
                        "why": "One bubble is one wasted cycle, so they add straight in. Bubbles do not compound and they do not scale with depth — which is why a deeper pipe costs more in *fill* but not more per stall.",
                        "whys": [
                            "One bubble is one wasted cycle, so they add straight in. Bubbles do not compound and they do not scale with depth — which is why a deeper pipe costs more in *fill* but not more per stall.",
                            "This would mean every instruction pays for every stall in the program. $S$ is already a total over the whole run, not a per-instruction rate.",
                            "The stall count does not scale with depth: a bubble occupies one cycle whether the pipe is five stages or fifteen. Depth shows up in the branch *penalty*, which is a different term.",
                            "That is the per-instruction stall rate, which belongs in the CPI expression rather than the cycle count.",
                        ],
                    },
                    {
                        "prompt": "Divide the stall cycles by the instruction count.",
                        "hole": "?",
                        "opts": ["S / N", "S", "S * N", "N / S"],
                        "a": 0,
                        "why": "$S/N$ is the average number of stall cycles per instruction, and that is what CPI is made of. It is also the number worth quoting in a report: 'stalls cost 0.31 CPI' is comparable across programs in a way that a raw bubble count is not.",
                        "whys": [
                            "$S/N$ is the average number of stall cycles per instruction, and that is what CPI is made of. It is also the number worth quoting in a report: 'stalls cost 0.31 CPI' is comparable across programs in a way that a raw bubble count is not.",
                            "Adding a whole-program total to a per-instruction average mixes units; the result grows without bound as the program gets longer.",
                            "Multiplying makes the penalty worse the longer the program runs, which is the opposite of how an average behaves.",
                            "Inverted, so a program with no stalls at all would have infinite CPI.",
                        ],
                    },
                    {
                        "prompt": "N grows large. What survives?",
                        "hole": "?",
                        "opts": ["S / N", "(D - 1) / N", "D - 1", "0, so CPI tends to 1"],
                        "a": 0,
                        "why": "The fill term $(D-1)/N$ vanishes because it is a fixed cost spread over more and more instructions, but $S$ grows *with* $N$, so $S/N$ tends to the program's stall rate and stays. Deep pipelines are not penalised by depth in steady state; they are penalised by the longer branch penalties depth causes.",
                        "whys": [
                            "The fill term $(D-1)/N$ vanishes because it is a fixed cost spread over more and more instructions, but $S$ grows *with* $N$, so $S/N$ tends to the program's stall rate and stays. Deep pipelines are not penalised by depth in steady state; they are penalised by the longer branch penalties depth causes.",
                            "This is the term that *disappears* — $D$ is a constant and $N$ is growing, so it goes to zero. Start-up cost is irrelevant to a long-running program.",
                            "Depth does not appear in steady-state CPI at all. That is the whole argument for pipelining: the fill is paid once.",
                            "Only for a program with no hazards. Real code stalls, and $S/N$ is the number the rest of this course is about reducing.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "A stalling pipeline model",
                "runtime": "python",
                "minutes": 42,
                "brief": r'''
Build the timing model of a five-stage pipeline with **interlocks and no
forwarding**, and use it to count cycles for a real instruction stream.

`isa.py` is provided: `isa.assemble(text)` turns assembly into a list of words
and `isa.decode(word)` gives you the fields, exactly as your module 1 decoder
did. Do not edit it.

Three functions.

`sources(ins)` — the register numbers this instruction *reads*, from its format:

```text
R   rs1, rs2      I   rs1        S   rs1, rs2
B   rs1, rs2      U   nothing    J   nothing
```

`destination(ins)` — the register it writes, or `None`.

`schedule(words)` — the cycle in which each instruction enters IF, as a list.
Two rules, and nothing else:

- in-order issue: `s[i] >= s[i-1] + 1`
- a read-after-write dependence on register `r` written by instruction `j`:
  `s[i] >= s[j] + 3`

`x0` is hard-wired to zero, so it never causes a stall — neither as a source nor
as a destination.

`cycles(words)` is then `schedule(words)[-1] + 5`: the last instruction still has
to walk its five stages.
''',
                "files": [
                    {"name": "isa.py", "ro": True, "content": ISA_PY},
                    {"name": "main.py", "content": r'''
import isa


def sources(ins):
    """The register numbers this instruction reads, decided by its format."""
    # TODO: R, S and B read rs1 and rs2; I reads rs1; U and J read nothing.
    return []


def destination(ins):
    """The register this instruction writes, or None."""
    # TODO: R, I, U and J write rd. S and B write nothing.
    return None


def schedule(words):
    """The cycle each instruction enters IF, with interlocks and no forwarding."""
    prog = [isa.decode(w) for w in words]
    starts = []
    # TODO: in-order issue, plus s[i] >= s[j] + 3 for every register instruction
    # i reads that instruction j writes. Ignore x0.
    for _ in prog:
        starts.append(0)
    return starts


def cycles(words):
    """Total cycles: the last instruction's IF, plus its five stages."""
    # TODO
    return 0


if __name__ == "__main__":
    prog = isa.assemble("""
        addi x1, x0, 1
        add  x2, x1, x1
        add  x3, x2, x2
    """)
    print("starts:", schedule(prog))
    print("cycles:", cycles(prog))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import isa


def sources(ins):
    """The register numbers this instruction reads, decided by its format."""
    fmt = ins["fmt"]
    if fmt in ("R", "S", "B"):
        return [ins["rs1"], ins["rs2"]]
    if fmt == "I":
        return [ins["rs1"]]
    return []


def destination(ins):
    """The register this instruction writes, or None."""
    if ins["fmt"] in ("R", "I", "U", "J"):
        return ins["rd"]
    return None


def schedule(words):
    """The cycle each instruction enters IF, with interlocks and no forwarding."""
    prog = [isa.decode(w) for w in words]
    starts, writer = [], {}
    for i, ins in enumerate(prog):
        t = 0 if i == 0 else starts[i - 1] + 1
        for r in sources(ins):
            if r and r in writer:
                t = max(t, starts[writer[r]] + 3)
        starts.append(t)
        d = destination(ins)
        if d:
            writer[d] = i
    return starts


def cycles(words):
    """Total cycles: the last instruction's IF, plus its five stages."""
    starts = schedule(words)
    return starts[-1] + 5 if starts else 0


if __name__ == "__main__":
    prog = isa.assemble("""
        addi x1, x0, 1
        add  x2, x1, x1
        add  x3, x2, x2
    """)
    print("starts:", schedule(prog))
    print("cycles:", cycles(prog))
'''}],
                "hints": [
                    "Keep a dict from register number to the index of the most recent instruction that writes it. Only the most recent matters — anything older has already written back.",
                    "`if r and r in writer` skips `x0` without a special case, because register 0 is the one register number that is falsy.",
                    "Record the write *after* computing this instruction's own start, or an instruction that reads and writes the same register will stall on itself.",
                ],
                "tests": [
                    {"name": "reads and writes follow the format, not the mnemonic", "code": r'''
import isa
_sw = isa.decode(isa.encode("sw x5, 0(x2)"))
assert sorted(sources(_sw)) == [2, 5], \
    f"a store reads its address base and the value it stores, got {sources(_sw)}"
assert destination(_sw) is None, "a store writes no register"
_b = isa.decode(isa.encode("beq x1, x2, 8"))
assert sorted(sources(_b)) == [1, 2], f"a branch compares two registers, got {sources(_b)}"
assert destination(_b) is None, "a branch writes no register"
_lui = isa.decode(isa.encode("lui x7, 0x1"))
assert sources(_lui) == [], f"lui reads nothing at all, got {sources(_lui)}"
assert destination(_lui) == 7, "lui writes rd"
_lw = isa.decode(isa.encode("lw x4, 8(x2)"))
assert sources(_lw) == [2], f"a load reads only its address base, got {sources(_lw)}"
assert destination(_lw) == 4, "a load writes rd"
'''},
                    {"name": "independent instructions issue one per cycle", "code": r'''
import isa
_p = isa.assemble("""
    addi x1, x0, 1
    addi x2, x0, 2
    addi x3, x0, 3
    addi x4, x0, 4
""")
assert schedule(_p) == [0, 1, 2, 3], \
    f"nothing here depends on anything, so nothing should stall: got {schedule(_p)}"
assert cycles(_p) == 8, f"four instructions plus four stages of drain is 8, got {cycles(_p)}"
'''},
                    {"name": "a dependent chain costs two bubbles per link", "code": r'''
import isa
_p = isa.assemble("""
    addi x1, x0, 1
    add  x2, x1, x1
    add  x3, x2, x2
    add  x4, x3, x3
""")
assert schedule(_p) == [0, 3, 6, 9], \
    f"each consumer waits for its producer's WB: expected [0, 3, 6, 9], got {schedule(_p)}"
assert cycles(_p) == 14, \
    f"14 cycles for four instructions, against 8 with no hazards, got {cycles(_p)}"
'''},
                    {"name": "a producer three instructions back is already free", "code": r'''
import isa
_p = isa.assemble("""
    addi x1, x0, 1
    nop
    nop
    add  x2, x1, x1
""")
assert schedule(_p) == [0, 1, 2, 3], \
    f"a distance of three needs no stall at all: got {schedule(_p)}"
_q = isa.assemble("""
    addi x1, x0, 1
    nop
    add  x2, x1, x1
""")
assert schedule(_q) == [0, 1, 3], \
    f"a distance of two still costs one cycle: expected [0, 1, 3], got {schedule(_q)}"
'''},
                    {"name": "x0 is not a dependence", "code": r'''
import isa
_p = isa.assemble("""
    addi x0, x0, 5
    add  x1, x0, x0
    nop
""")
assert schedule(_p) == [0, 1, 2], \
    f"writes to x0 are discarded, so nothing may ever stall on x0: got {schedule(_p)}"
'''},
                    {"name": "the value a store writes to memory is a read too", "code": r'''
import isa
_p = isa.assemble("""
    add  x5, x1, x2
    sw   x5, 0(x10)
""")
assert schedule(_p) == [0, 3], \
    ("the store needs x5, which the add has not written back yet — forgetting that a "
     "store reads rs2 is the classic hazard-unit bug: got %r" % (schedule(_p),))
assert cycles(_p) == 8, f"expected 8 cycles, got {cycles(_p)}"
'''},
                    {"name": "a longer stream adds up", "code": r'''
import isa
_p = isa.assemble("""
    addi x1, x0, 10
    addi x2, x0, 20
    add  x3, x1, x2
    lw   x4, 0(x3)
    add  x5, x4, x1
    sw   x5, 4(x3)
""")
_s = schedule(_p)
assert _s == [0, 1, 4, 7, 10, 13], f"expected [0, 1, 4, 7, 10, 13], got {_s}"
assert cycles(_p) == 18, \
    f"four of the seven dependences bind, two cycles each: 18 against an ideal 10, got {cycles(_p)}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Forwarding, and where it runs out",
            "summary": "The value exists long before it is architecturally visible. Route it, and most stalls disappear — but not all.",
            "concepts": [
                "A result is finished at the end of the stage that computes it, not when it reaches the register file three cycles later.",
                "The forwarding condition is one inequality: a consumer stalls only when the operand's *use* stage arrives before the producer's *ready* stage has passed.",
                "Ready stages differ by producer: an ALU result is ready at the end of EX, a load result only at the end of MEM.",
                "Use stages differ by operand: both ALU operands are needed at the start of EX, but the *data* operand of a store is not needed until MEM.",
                "The load-use hazard is the residue forwarding cannot remove, and it is why compilers schedule an independent instruction into the slot after a load.",
            ],
            "read": [
                {
                    "title": "The value is already there",
                    "minutes": 16,
                    "body": r'''
Module 2 held `add x2, x1, x1` back by two cycles because `x1` had not been
written yet. Draw the unstalled version again and ask a narrower question — not
"has the register been written", but "does the number exist anywhere in the
machine":

```text
cycle        0    1    2    3    4    5    6
addi x1      IF   ID   EX  MEM   WB
add  x2           IF   ID   EX  MEM   WB
                            ^
             the addi's sum is in the EX/MEM latch at the end of cycle 2;
             the add wants it at the start of cycle 3
```

The `addi` computes its sum in EX, which is cycle 2, and that sum is captured in
the EX/MEM pipeline register at the end of that cycle. The `add` needs an operand
at the start of its own EX, which is cycle 3. The number is sitting in a latch,
one cycle early, with two stages of pure bookkeeping still to go before it
becomes architecturally visible in the register file. A wire from that latch back
to the ALU input, and a multiplexer to choose it over the register file's output,
delivers it on time. Nothing waits.

That is the whole idea, and the rest of this module is working out precisely
which dependences it reaches.

## One inequality

Name two stages and the answer falls out. Let $r$ be the stage at whose **end**
the producer's result exists, and $u$ the stage at whose **start** the consumer
needs it. A producer entering IF in cycle $c$ is in stage $r$ during cycle
$c + r$, so its result exists from the end of that cycle. A consumer entering IF
in cycle $c + d$ — that is, $d$ instructions behind — is in stage $u$ during
cycle $c + d + u$, and it needs the value at the start of that cycle.

A value that exists at the end of cycle $c+r$ is available to any stage that
starts in cycle $c + r + 1$ or later, so the no-stall condition is

$$c + d + u \ge c + r + 1 \quad\Longrightarrow\quad d \ge r + 1 - u.$$

That is one line, it has no case analysis in it, and it prices every forwarding
path in the machine. There are four combinations that occur in this instruction
set:

```python
IF, ID, EX, ME, WB = 0, 1, 2, 3, 4
CASES = [("ALU result -> ALU operand", EX, EX),
         ("ALU result -> store data ", EX, ME),
         ("load value -> ALU operand", ME, EX),
         ("load value -> store data ", ME, ME)]
for label, ready, use in CASES:
    d = ready + 1 - use
    print("%s  r=%d u=%d  d_min = %2d  %s"
          % (label, ready, use, d, "no interlock" if d <= 1 else "%d bubble(s)" % (d - 1)))
```

Three of the four need $d \le 1$, which is satisfied by back-to-back
instructions, so three of the four are free. The exception is a load feeding an
ALU operand, where $d_{min} = 2$: one instruction must sit between them.

Two of those rows deserve their own sentence. The `ALU result -> store data` row
returns $d_{min} = 0$, a distance no pair can actually have; the meaning is that
the path has slack, because a store does not need the value it is writing until
MEM, a stage after the ALU operands are consumed. And `load value -> store data`
returns 1 — a memory-to-memory copy, `lw` followed immediately by `sw`, runs at
full rate through a MEM-to-MEM path. The stage an operand is needed in is a
property of the *operand*, not of the instruction, and the lab's check *the stage
an operand is needed in depends on the operand* is built on exactly that: the
same load feeding a store's data costs nothing, and feeding the same store's
address costs a bubble.

## The one that does not work, shown

Here is the load-use case with nothing hidden. The load's value comes out of
memory at the end of MEM, cycle 3; the consumer wants it at the start of its EX,
cycle 3. Same cycle, wrong half, and no wire fixes it:

```text
cycle        0    1    2    3    4    5    6
lw   x1      IF   ID   EX  MEM   WB
add  x2           IF   ID   EX  MEM   WB
                            ^^^
             the add's EX is cycle 3, and the memory answers at the END of
             cycle 3 — forwarding moves a value across stages, not backwards
             through time
```

Delay the consumer by one cycle and the two line up: the `add` issues in cycle 2,
its EX becomes cycle 4, and the value has been available since the end of cycle 3.

```python
IF, ID, EX, ME, WB = 0, 1, 2, 3, 4
# Each entry: text, destination, ready stage, [(source register, use stage)]
TRIO = [("lw   x1, 0(x10)", 1, ME, []),
        ("add  x2, x1, x1", 2, EX, [(1, EX)]),
        ("add  x3, x2, x2", 3, EX, [(2, EX)])]
SCHEDULED = [("lw   x1, 0(x10)", 1, ME, []),
             ("addi x9, x0, 7", 9, EX, []),
             ("add  x2, x1, x1", 2, EX, [(1, EX)])]

def run(prog, forwarding):
    starts, writer = [], {}
    for i, (text, dest, ready, srcs) in enumerate(prog):
        t = 0 if i == 0 else starts[-1] + 1
        for r, use in srcs:
            j = writer.get(r)
            if j is not None:
                t = max(t, starts[j] + prog[j][2] + 1 - use if forwarding else starts[j] + 3)
        starts.append(t)
        writer[dest] = i
    return starts, starts[-1] + 5

print("load-use, no forwarding :", run(TRIO, False))
print("load-use, forwarding    :", run(TRIO, True))
print("one instruction moved in:", run(SCHEDULED, True))
```

Eleven cycles becomes eight, and the issue cycles are `[0, 2, 3]`: the second
instruction slips by one and the third does not slip at all, because by then the
producer is an ALU instruction again. The third line is what a compiler does
about it. Move any independent instruction into the slot after the load —
`addi x9, x0, 7` will do, it need not be related to anything — and the issue
cycles are `[0, 1, 2]` with no bubble at all, seven cycles. The instruction was
going to be executed regardless; the only decision was where.

## "Forwarding removes all stalls"

This is the sentence to be careful with, and it is tempting for three separate
reasons that all point the same way. The EX-to-EX case, which is most of the
dependences in most code, really is free. The sandbox *Forwarding, in one switch*
shows six dependent pairs collapsing from CPI 2.78 to 1.44 the moment the switch
is flipped, and then sweeping the dependence count from 0 to 6 moves nothing —
the visualiser does not draw load-use at all, so within that picture the claim is
true. And the derivation's closing figure, $1 + f_{lu}$, is close enough to 1 on
ordinary code that the residue is easy to round away.

Run the module 2 kernel through both models and the residue is visible as a
single line:

```python
IF, ID, EX, ME, WB = 0, 1, 2, 3, 4
# addi x1 / addi x2 / add x3,x1,x2 / lw x4,0(x3) / add x5,x4,x1 / sw x5,4(x3)
KERNEL = [("addi x1", 1, EX, []), ("addi x2", 2, EX, []),
          ("add  x3", 3, EX, [(1, EX), (2, EX)]),
          ("lw   x4", 4, ME, [(3, EX)]),
          ("add  x5", 5, EX, [(4, EX), (1, EX)]),
          ("sw   x5", None, EX, [(3, EX), (5, ME)])]

def run(forwarding):
    starts, writer, out = [], {}, []
    for i, (text, dest, ready, srcs) in enumerate(KERNEL):
        t, why = (0, "first") if i == 0 else (starts[-1] + 1, "in order")
        for r, use in srcs:
            j = writer.get(r)
            if j is None:
                continue
            need = starts[j] + KERNEL[j][2] + 1 - use if forwarding else starts[j] + 3
            if need > t:
                t, why = need, "waits on x%d" % r
        starts.append(t)
        out.append("%s  IF %2d  (%s)" % (text, t, why))
        if dest is not None:
            writer[dest] = i
    return starts, out

for on in (False, True):
    s, rows = run(on)
    print("--- forwarding", on, "---")
    for row in rows:
        print(" ", row)
    print("  cycles %d   CPI %.2f" % (s[-1] + 5, (s[-1] + 5) / len(KERNEL)))
print("ideal cycles 10, CPI %.2f" % (10 / 6))
```

Eighteen cycles fall to eleven, and five of the six instructions issue on the
in-order bound. One does not: `add x5` waits on `x4`, which the `lw` produced one
instruction earlier. That is the load-use pair, one bubble, and the CPI is 1.83
where a machine with no hazards at all would be at 1.67. Forwarding recovered
seven of the eight stall cycles and left one, and the remaining one is the only
kind it can never take.

Notice the `sw` in the forwarded run: without forwarding it was one of the four
binding stalls, and now it issues in order. It reads `x5`, produced by the
instruction immediately in front of it, and it gets away with it because a store
consumes its data in MEM. Nothing about the program changed; a different pair of
stage numbers went into the same inequality.

## The bug the inequality does not protect you from

Timing is one half of a forwarding unit and selection is the other. Consider
three instructions where the first two both write `x1`:

```text
addi x1, x0, 1        in EX in cycle 2, in MEM in cycle 3
addi x1, x0, 2        in EX in cycle 3, in MEM in cycle 4
add  x3, x1, x1       in EX in cycle 4 — and BOTH latches match x1
```

In cycle 4 the third instruction is in EX, the second is in MEM with `x1 = 2` in
the EX/MEM latch, and the first is in WB with `x1 = 1` in the MEM/WB latch. Both
comparators fire. The correct source is the *newer* value, from EX/MEM, and a
forwarding unit that checks MEM/WB first delivers 1 instead of 2. Every timing
count in this module stays right and the program computes the wrong answer, which
is why a cycle-accurate model and a functional model catch different bugs — and
why the capstone insists on both.

## Where forwarding stops being free

The model in this module charges nothing for a forwarding path, and that is the
useful lie. In silicon each path is a multiplexer in front of an ALU input, fed
by comparators over register numbers, and it sits on the EX critical path — the
200 ps that set the 230 ps clock in module 1's derivation. Adding paths widens
that mux; widening it lengthens $t_{ex}$; lengthening $t_{ex}$ slows every
instruction, including the ones that never forward. A path is worth building when
the cycles it saves exceed the cycles the whole program loses to a longer clock,
which is why real designs build EX-to-EX and MEM-to-EX and then start arguing.

Three other boundaries are worth stating plainly. Forwarding does nothing for
control hazards, because there is no value anywhere in the machine to route —
until the branch resolves nobody knows which instruction should have been
fetched, and that is module 4. It does nothing for a cache miss: the "load value
ready at the end of MEM" assumption is a one-cycle memory, and a miss stalls the
whole pipeline for tens of cycles regardless of routing. And it assumes a
single-cycle EX; give the machine a multi-cycle multiplier or a floating-point
unit and $r$ stops being a constant per instruction class, so $d \ge r + 1 - u$
still holds while $r$ has to be looked up rather than assumed.

The lab, *Forwarding paths and the load-use interlock*, is this page in three
functions: `ready_stage` for the producer, `use_stage` for the consumer, and one
line in `schedule` that is the inequality above. Watch the corner its checks aim
at — in `sw x5, 0(x5)` one register is both the address and the data, and the
earlier use has to win.
''',
                },
            ],
            "sandbox": {
                "title": "Forwarding, in one switch",
                "visualiser": "pipeline",
                "minutes": 8,
                "initial": {"dep": 6, "fwd": 0, "miss": 0},
                "brief": r'''
Six dependent pairs, forwarding off: the worst case from the last module. There
is one switch in this sandbox that matters.
''',
                "notice": [
                    "Flip forwarding to yes. Every row snaps back to one cycle after the one above, and the caption falls from CPI 2.78 to 1.44 — six dependences removed at once, without touching the program.",
                    "Now sweep dependent pairs from 0 to 6 with forwarding still on. Nothing moves at all: in this model a forwarded dependence is free. That is the useful lie. In silicon it costs a multiplexer in front of each ALU input, and those multiplexers sit on the critical path that sets $t_{ex}$.",
                    "The one hazard this model does not draw is the load-use case, where the value is still in the memory stage when the next instruction wants it. Forwarding cannot fix that one, and you build it yourself in the lab.",
                ],
            },
            "derive": {
                "title": "The forwarding condition",
                "minutes": 15,
                "vars": ["c", "d", "r", "u", "f_lu", "CPI"],
                "brief": r'''
Stages are numbered IF = 0, ID = 1, EX = 2, MEM = 3, WB = 4.

A producer enters IF in cycle $c$, and its result is finished at the end of its
stage $r$. A consumer enters IF in cycle $c + d$ — $d$ instructions behind — and
needs the operand at the start of its stage $u$. Forwarding is a wire from the
output of stage $r$ to the input of stage $u$; the only question is whether the
value is there in time.
''',
                "steps": [
                    {
                        "prompt": "The producer's stage $r$ occupies one cycle. Which cycle is it?",
                        "answer": "c + r",
                        "hint": "It entered IF (stage 0) in cycle $c$ and advances one stage per cycle.",
                        "deconstruct": [
                            "Stage 0 is cycle $c$, stage 1 is cycle $c+1$, and so on.",
                            "So stage $r$ is cycle $c + r$, and the result exists at the end of it.",
                        ],
                    },
                    {
                        "prompt": "In which cycle does the consumer need the operand — that is, which cycle is its stage $u$?",
                        "answer": "c + d + u",
                        "hint": "The consumer entered IF in cycle $c + d$; apply the same counting.",
                        "deconstruct": [
                            "Its stage 0 is cycle $c + d$.",
                            "Its stage $u$ is $u$ cycles later.",
                        ],
                    },
                    {
                        "prompt": "The value is available to any stage that *starts* after the producer's stage $r$ has finished, so the no-stall condition is $c + d + u \\ge c + r + 1$. Solve it for the smallest distance $d$ that needs no stall.",
                        "answer": "r + 1 - u",
                        "hint": "Cancel $c$ from both sides and rearrange for $d$.",
                        "deconstruct": [
                            "$c + d + u \\ge c + r + 1$ gives $d + u \\ge r + 1$.",
                            "So $d \\ge r + 1 - u$.",
                        ],
                    },
                    {
                        "prompt": "An ALU instruction is ready at the end of EX and another ALU instruction needs its operands at the start of EX. Substitute $r = 2$, $u = 2$ and write the minimum distance.",
                        "answer": "1",
                        "hint": "$r + 1 - u$ with both stages equal to 2.",
                        "deconstruct": [
                            "$2 + 1 - 2 = 1$.",
                            "A distance of one is back-to-back, so an EX-to-EX forward removes the hazard entirely.",
                        ],
                    },
                    {
                        "prompt": "A load is ready only at the end of MEM. With $r = 3$ and a consumer needing it in EX ($u = 2$), what is the minimum distance now?",
                        "answer": "2",
                        "hint": "Same expression, one stage later.",
                        "deconstruct": [
                            "$3 + 1 - 2 = 2$.",
                            "Distance two means one instruction must sit between the load and its use — either useful work, or a bubble.",
                        ],
                    },
                    {
                        "prompt": "Now let the consumer be a store using the loaded value as the data it writes, needed at the start of MEM ($u = 3$). What is the minimum distance?",
                        "answer": "1",
                        "hint": "$r = 3$, $u = 3$.",
                        "deconstruct": [
                            "$3 + 1 - 3 = 1$: back-to-back is fine.",
                            "A load feeding a store's data operand needs a MEM-to-MEM path and costs nothing — a memory copy runs at full rate.",
                        ],
                    },
                    {
                        "prompt": "With full forwarding the only stalls left are load-use pairs, a fraction $f_{lu}$ of all instructions, one bubble each. Write the CPI.",
                        "answer": "1 + f_{lu}",
                        "hint": "One cycle per instruction, plus the average bubble count.",
                        "deconstruct": [
                            "Every instruction costs one cycle.",
                            "A fraction $f_{lu}$ of them costs one more.",
                        ],
                    },
                ],
                "closing": r'''
One inequality, $d \ge r + 1 - u$, covers every forwarding path in the machine —
EX to EX, MEM to EX, MEM to MEM — and it also tells you which paths are worth
building: any pair with $r + 1 - u \le 1$ needs no interlock at all. The module 2
figure of 1.75 becomes about $1 + f_{lu}$, which on ordinary compiled code is
nearer 1.1.
''',
            },
            "quiz": {
                "title": "Forwarding, and the one case it cannot save",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why is forwarding possible at all?",
                        "opts": [
                            "The value is finished several stages before it becomes architecturally visible",
                            "The register file can be written and read in the same cycle",
                            "The compiler has already reordered the instructions",
                            "The ALU is faster than the register file",
                        ],
                        "a": 0,
                        "why": r"""
An ALU result exists at the end of EX; it is not written to the register file until WB,
two stages later. Those two stages are pure bookkeeping as far as the value is
concerned, so a wire from the EX/MEM latch back to the ALU input delivers it early. The
same-cycle write-then-read trick in the register file is a real and separate
optimisation — it handles the distance-three case — but it is not what forwarding is.
""",
                    },
                    {
                        "q": "Which dependence can forwarding *not* eliminate?",
                        "opts": [
                            "A load followed immediately by an instruction that uses the loaded value",
                            "An ALU result used by the very next instruction",
                            "An ALU result used two instructions later",
                            "A branch that depends on the instruction before it",
                        ],
                        "a": 0,
                        "why": r"""
Load-use, and the reason is timing, not routing: a load's value arrives at the end of
MEM, but the consumer needs it at the *start* of its EX — which is the same cycle.
Forwarding can move a value across stages, not backwards in time. One bubble makes the
two line up, and that single unavoidable cycle is why compilers try to put an
independent instruction after every load.
""",
                    },
                    {
                        "q": "An ALU result is needed by the instruction two later. Where does it come from?",
                        "opts": [
                            "The MEM/WB latch, forwarded into EX",
                            "The EX/MEM latch, forwarded into EX",
                            "The register file, with no forwarding needed",
                            "It requires a one-cycle stall",
                        ],
                        "a": 0,
                        "why": r"""
By then the producer has moved on a stage, so the value is sitting in MEM/WB rather
than EX/MEM. Both paths exist and the forwarding unit picks between them by comparing
register numbers; getting the priority wrong here is a classic bug, because when *both*
match you must take the newer value from EX/MEM, not the stale one from MEM/WB.
""",
                    },
                    {
                        "q": "With full forwarding, how many bubbles does a load followed by a dependent instruction cost?",
                        "opts": ["One", "Two", "Three", "None"],
                        "a": 0,
                        "why": r"""
Exactly one. Forwarding has already done everything it can: the interlock delays the
consumer by a single cycle so that MEM's output and the consumer's EX input meet.
Without any forwarding it would be three, which is the measurement worth making in the
lab — the difference between those two numbers is what the forwarding paths are worth.
""",
                    },
                    {
                        "q": "Which hazard does forwarding do nothing about?",
                        "opts": ["Control hazards", "Read-after-write hazards", "Write-after-write hazards", "Structural hazards on the register file"],
                        "a": 0,
                        "why": r"""
Forwarding moves *data* that already exists. A control hazard is the absence of
information: until the branch resolves, nobody knows which instruction should be
fetched next, and there is no value anywhere in the machine to route. That is why the
next module is about guessing — it is the only tool left.
""",
                    },
                ],
            },
            "lab": {
                "title": "Forwarding paths and the load-use interlock",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Extend the module 2 model with forwarding. `sources` and `destination` are given
this time; the timing is yours.

Write three functions.

`ready_stage(ins)` — the stage at whose end this instruction's result exists.
EX (2) for anything the ALU computes, MEM (3) for a load.

`use_stage(ins, reg)` — the stage at whose start `ins` needs register `reg`.
EX (2) for everything, **except** the value a store writes to memory, which is
not needed until MEM (3). Careful: in `sw x5, 0(x5)` the same register is both
the address and the data, and the address is needed in EX — the earlier use wins.

`schedule(words, forwarding=True)` — the issue cycle of each instruction:

```text
in-order            s[i] >= s[i-1] + 1
forwarding off      s[i] >= s[j] + 3
forwarding on       s[i] + use >= s[j] + ready + 1
```

where `j` is the most recent writer of a register `i` reads. `cycles` is
`schedule(...)[-1] + 5` as before.
''',
                "files": [
                    {"name": "isa.py", "ro": True, "content": ISA_PY},
                    {"name": "main.py", "content": r'''
import isa

IF, ID, EX, ME, WB = 0, 1, 2, 3, 4


def sources(ins):
    """The register numbers this instruction reads. Module 2's answer, given."""
    fmt = ins["fmt"]
    if fmt in ("R", "S", "B"):
        return [ins["rs1"], ins["rs2"]]
    if fmt == "I":
        return [ins["rs1"]]
    return []


def destination(ins):
    """The register this instruction writes, or None. Module 2's answer, given."""
    if ins["fmt"] in ("R", "I", "U", "J"):
        return ins["rd"]
    return None


def ready_stage(ins):
    """The stage at whose end this instruction's result exists."""
    # TODO: EX for the ALU, MEM for a load.
    return EX


def use_stage(ins, reg):
    """The stage at whose start `ins` needs register `reg`."""
    # TODO: EX for everything, MEM for the data operand of a store.
    return EX


def schedule(words, forwarding=True):
    """The cycle each instruction enters IF."""
    prog = [isa.decode(w) for w in words]
    starts = []
    # TODO: in-order issue, then one constraint per read-after-write dependence.
    for _ in prog:
        starts.append(0)
    return starts


def cycles(words, forwarding=True):
    """Total cycles: the last instruction's IF, plus its five stages."""
    # TODO
    return 0


if __name__ == "__main__":
    prog = isa.assemble("""
        lw   x1, 0(x10)
        add  x2, x1, x1
        add  x3, x2, x2
    """)
    print("stalling :", schedule(prog, False), cycles(prog, False))
    print("forwarded:", schedule(prog, True), cycles(prog, True))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import isa

IF, ID, EX, ME, WB = 0, 1, 2, 3, 4


def sources(ins):
    """The register numbers this instruction reads. Module 2's answer, given."""
    fmt = ins["fmt"]
    if fmt in ("R", "S", "B"):
        return [ins["rs1"], ins["rs2"]]
    if fmt == "I":
        return [ins["rs1"]]
    return []


def destination(ins):
    """The register this instruction writes, or None. Module 2's answer, given."""
    if ins["fmt"] in ("R", "I", "U", "J"):
        return ins["rd"]
    return None


def ready_stage(ins):
    """The stage at whose end this instruction's result exists."""
    return ME if ins["name"] == "lw" else EX


def use_stage(ins, reg):
    """The stage at whose start `ins` needs register `reg`."""
    if ins["fmt"] == "S" and reg == ins["rs2"] and reg != ins["rs1"]:
        return ME
    return EX


def schedule(words, forwarding=True):
    """The cycle each instruction enters IF."""
    prog = [isa.decode(w) for w in words]
    starts, writer = [], {}
    for i, ins in enumerate(prog):
        t = 0 if i == 0 else starts[i - 1] + 1
        for r in sources(ins):
            if r and r in writer:
                j = writer[r]
                if forwarding:
                    t = max(t, starts[j] + ready_stage(prog[j]) + 1 - use_stage(ins, r))
                else:
                    t = max(t, starts[j] + 3)
        starts.append(t)
        d = destination(ins)
        if d:
            writer[d] = i
    return starts


def cycles(words, forwarding=True):
    """Total cycles: the last instruction's IF, plus its five stages."""
    starts = schedule(words, forwarding)
    return starts[-1] + 5 if starts else 0


if __name__ == "__main__":
    prog = isa.assemble("""
        lw   x1, 0(x10)
        add  x2, x1, x1
        add  x3, x2, x2
    """)
    print("stalling :", schedule(prog, False), cycles(prog, False))
    print("forwarded:", schedule(prog, True), cycles(prog, True))
'''}],
                "hints": [
                    "The whole forwarding rule is one line: `t = max(t, starts[j] + ready_stage(prog[j]) + 1 - use_stage(ins, r))`.",
                    "`ready_stage` is about the *producer* and `use_stage` about the *consumer* — passing the wrong instruction to either is the mistake that makes an ALU chain stall.",
                    "In `use_stage`, check `reg != ins['rs1']` before returning MEM, or `sw x5, 0(x5)` will be scheduled a cycle too early.",
                ],
                "tests": [
                    {"name": "an ALU chain runs at one instruction per cycle", "code": r'''
import isa
_p = isa.assemble("""
    addi x1, x0, 1
    add  x2, x1, x1
    add  x3, x2, x2
    add  x4, x3, x3
""")
assert schedule(_p, True) == [0, 1, 2, 3], \
    f"EX-to-EX forwarding removes every one of these hazards: got {schedule(_p, True)}"
assert cycles(_p, True) == 8, f"expected 8 cycles with forwarding, got {cycles(_p, True)}"
assert cycles(_p, False) == 14, \
    f"the same code without forwarding still costs 14, got {cycles(_p, False)}"
'''},
                    {"name": "a load feeding the next instruction still costs one bubble", "code": r'''
import isa
_p = isa.assemble("""
    lw   x1, 0(x10)
    add  x2, x1, x1
    add  x3, x2, x2
""")
_s = schedule(_p, True)
assert _s == [0, 2, 3], \
    ("the load's value is not ready until the end of MEM, so its use waits one cycle "
     "and the ALU pair after it does not: expected [0, 2, 3], got %r" % (_s,))
assert cycles(_p, True) == 8, f"expected 8, got {cycles(_p, True)}"
'''},
                    {"name": "one independent instruction after a load costs nothing", "code": r'''
import isa
_p = isa.assemble("""
    lw   x1, 0(x10)
    addi x9, x0, 7
    add  x2, x1, x1
""")
assert schedule(_p, True) == [0, 1, 2], \
    ("with one instruction in the slot the load's result arrives in time — this is the "
     "reordering a compiler performs: got %r" % (schedule(_p, True),))
'''},
                    {"name": "the stage an operand is needed in depends on the operand", "code": r'''
import isa
_data = isa.assemble("""
    lw   x1, 0(x10)
    sw   x1, 4(x10)
""")
assert schedule(_data, True) == [0, 1], \
    ("a store's data operand is not needed until MEM, so load-to-store data forwards "
     "with no stall at all: got %r" % (schedule(_data, True),))
_addr = isa.assemble("""
    lw   x1, 0(x10)
    sw   x9, 4(x1)
""")
assert schedule(_addr, True) == [0, 2], \
    ("the same load feeding the store's *address* is needed in EX and does cost a "
     "bubble: got %r" % (schedule(_addr, True),))
'''},
                    {"name": "the two stage functions report the right stages", "code": r'''
import isa
_lw = isa.decode(isa.encode("lw x1, 0(x10)"))
_add = isa.decode(isa.encode("add x2, x1, x1"))
_sw = isa.decode(isa.encode("sw x5, 0(x2)"))
assert ready_stage(_lw) == 3, f"a load is ready at the end of MEM (3), got {ready_stage(_lw)}"
assert ready_stage(_add) == 2, f"an ALU result is ready at the end of EX (2), got {ready_stage(_add)}"
assert use_stage(_add, 1) == 2, "ALU operands are needed at the start of EX"
assert use_stage(_sw, 5) == 3, \
    f"the value a store writes is not needed until MEM (3), got {use_stage(_sw, 5)}"
assert use_stage(_sw, 2) == 2, \
    f"the address base of a store is needed in EX (2), got {use_stage(_sw, 2)}"
_same = isa.decode(isa.encode("sw x5, 0(x5)"))
assert use_stage(_same, 5) == 2, \
    "when one register is both address and data, the earlier use decides"
'''},
                    {"name": "forwarding is worth most of the pipeline", "code": r'''
import isa
_p = isa.assemble("""
    addi x1, x0, 10
    addi x2, x0, 20
    add  x3, x1, x2
    lw   x4, 0(x3)
    add  x5, x4, x1
    sw   x5, 4(x3)
""")
assert cycles(_p, False) == 18, f"expected 18 stalling, got {cycles(_p, False)}"
assert cycles(_p, True) == 11, f"expected 11 forwarded, got {cycles(_p, True)}"
assert cycles(_p, True) - 10 == 1, \
    "six instructions have an ideal cost of 10 cycles, and exactly one load-use bubble is left"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Guessing the next fetch",
            "summary": "The branch is resolved in EX, and the front end cannot wait. So it guesses, and you pay for the guesses it gets wrong.",
            "concepts": [
                "A control hazard is not a data dependence — the machine does not know *which* instruction to fetch, so stalling means fetching nothing.",
                "Resolving a branch in EX costs two fetched instructions on a mispredict; resolving it in MEM costs three. Pipeline depth is bought with misprediction penalty.",
                "A two-bit saturating counter is hysteresis: one surprise changes the counter but not the prediction, which is exactly what a loop's final iteration needs.",
                "A single counter per branch cannot represent a pattern. Alternating taken and not-taken is predicted wrong 100% of the time, worse than a coin toss.",
                "gshare indexes the counter table with the branch address XORed with a global history register, so the same branch gets different counters in different contexts.",
            ],
            "read": [
                {
                    "title": "Twenty wrong out of two hundred",
                    "minutes": 16,
                    "body": r'''
A branch enters IF in cycle 0. It is compared in EX, which is cycle 2. The front
end does not stop fetching while it waits:

```text
cycle        0    1    2    3    4    5    6    7
beq          IF   ID   EX  MEM   WB
i+1               IF   ID    x                    fetched in cycle 1, squashed
i+2                    IF    x                    fetched in cycle 2, squashed
target                       IF   ID   EX  MEM   WB
```

Two instructions were fetched down a path the machine turned out not to take.
They are squashed — their pipeline registers cleared, their writes suppressed —
and the correct target enters IF in cycle 3 rather than cycle 1. Two cycles gone.
That is the whole of the mispredict penalty, and it is worth seeing where the 2
comes from, because it is not the pipeline depth. It is the number of cycles
between the fetch of the branch and the resolution of the branch: EX is stage 2,
IF is stage 0, so two fetch slots have been spent on a guess. Move the comparison
into ID and the penalty is 1, paid for with a longer cycle. Deepen the front end
and the penalty grows with it.

This is not a data hazard and no amount of forwarding touches it. A data hazard
is a value that exists in the wrong place; a control hazard is the absence of a
value. Until the comparison happens there is nothing anywhere in the machine that
says which instruction should be fetched next, so the only options are to stop
fetching, or to guess.

Stopping is a real option and it is priced the same way: with a fifth of
instructions being branches, stalling on every one of them costs
$1 + 0.20 \times 2 = 1.40$ cycles per instruction, a 40% loss on a machine
otherwise running at its peak. Guessing costs only for the guesses that are
wrong. If $f_{br}$ is the branch fraction, $a$ the accuracy and $c_{mis}$ the
penalty, then mispredicted branches are $f_{br}(1-a)$ of all instructions and

$$\mathrm{CPI} = 1 + f_{br}\,(1 - a)\,c_{mis}.$$

That is the expression the derivation *Accuracy, penalty and CPI* builds, and it
turns a predictor from a piece of cleverness into a number.

## A loop, and three predictors

The trace to measure on is the one every program is full of: a backward branch
that is taken for nine iterations and falls through on the tenth, twenty times
over. Two hundred branch outcomes, 180 of them taken.

```python
def loop_outcomes(trips=20, body=10):
    """A backward branch: taken body-1 times, then not taken, once per trip."""
    return [k != body - 1 for _ in range(trips) for k in range(body)]

def one_bit(outcomes):
    state, wrong = False, 0
    for taken in outcomes:
        wrong += state != taken
        state = taken
    return wrong

def two_bit(outcomes, counter=1):
    wrong = 0
    for taken in outcomes:
        wrong += (counter >= 2) != taken
        counter = min(3, counter + 1) if taken else max(0, counter - 1)
    return wrong

loop = loop_outcomes()
alt = [i % 2 == 0 for i in range(200)]
print("trace         n    one-bit  two-bit  always-taken")
for name, tr in (("loop 20x10", loop), ("alternating", alt)):
    print("%-12s %3d   %6d %8d %13d"
          % (name, len(tr), one_bit(tr), two_bit(tr), sum(1 for t in tr if not t)))
```

The one-bit predictor remembers the last outcome and repeats it, and it gets 40
of 200 wrong: exactly two per trip. Trace one trip and both are visible. The loop
exits, the predictor said taken, that is one mistake — and the exit also
*rewrites* the state to not-taken, so when the loop is entered again the first
iteration is predicted not-taken and is a second mistake. One surprise has cost
two mispredictions, and the second one is the avoidable half.

The two-bit saturating counter avoids it by refusing to change its mind on a
single surprise. Four states, and the prediction is taken in the top two:

```text
   0            1            2            3
 strong-N --> weak-N  --> weak-T   --> strong-T
 not taken    not taken     taken        taken
      <-- one not-taken step per arrow, saturating at each end -->
```

A loop that runs nine iterations pushes the counter to 3 and holds it there. The
exit drops it to 2 — still predicting taken — so the mistake is not repeated on
re-entry. Twenty-one wrong of 200: one per exit, plus one at the very start when
the counter began at 1 and the first branch was taken. One extra flip-flop per
table entry has halved the mispredictions on the pattern loops actually produce,
and the two-bit saturating counter has been the base cell of predictor designs
ever since. The fill-in exercise *What a wrong guess costs* asks for the same
argument in one blank.

## The comparison that ought to be embarrassing

Look at the third column of that table again. Always-taken — a predictor with no
state, no table and no update logic — gets 20 wrong on the same trace. The
two-bit counter gets 21. The counter *loses*, by exactly the one mistake it spent
warming up.

That is a curiosity on a loop. On a trace with no pattern to learn it stops being
a curiosity:

```python
def pseudo_random(n=400, percent_taken=70, seed=12345, pcs=(0x400, 0x420, 0x440)):
    """The linear congruential trace the lab is measured on. No pattern to learn."""
    state, out = seed & 0xFFFFFFFF, []
    for i in range(n):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        out.append((pcs[i % len(pcs)], (state >> 16) % 100 < percent_taken))
    return out

def bimodal(trace, index_bits=6):
    mask, table, wrong = (1 << index_bits) - 1, [1] * (1 << index_bits), 0
    for pc, taken in trace:
        i = (pc >> 2) & mask
        wrong += (table[i] >= 2) != taken
        table[i] = min(3, table[i] + 1) if taken else max(0, table[i] - 1)
    return wrong

trace = pseudo_random()
taken = sum(1 for _pc, t in trace if t)
print("branches %d, taken %d (%.2f%%)" % (len(trace), taken, 100 * taken / len(trace)))
print("two-bit counters wrong : %3d  (%.3f)" % (bimodal(trace), bimodal(trace) / len(trace)))
print("always-taken wrong     : %3d  (%.3f)"
      % (len(trace) - taken, (len(trace) - taken) / len(trace)))
```

The trace is 68.75% taken, so a machine that guesses taken every time and learns
nothing is wrong 31.25% of the time. The two-bit counters are wrong 39.0% of the
time. The adaptive predictor is beaten by the constant, and beaten by nearly
eight percentage points.

The reason is that a counter is a *low-pass filter over recent outcomes*, and
filtering noise produces noise. When the underlying probability is fixed at
0.6875 and independent from branch to branch, the counter spends its time in
whichever state the last two or three outcomes pushed it to, and it drops below 2
often enough to predict not-taken on a stream that is mostly taken. The bias is
information; the recent history is not. A predictor that tracks the recent
history throws away some of the bias in exchange for a pattern that is not there.

This is the mistake worth naming, because it is tempting in a way that survives
being told: adaptivity feels like it can only help, on the reasoning that a
learner which can represent the constant answer will settle on it. A two-bit
counter cannot represent the constant answer. It has four states and it moves on
every branch, so it has no way to say "taken, 69% of the time, and stop asking".
The lab's check *a counter chasing noise loses to a static guess* is this
measurement, and it is there so the number arrives before the intuition hardens.

## One counter is one bit of memory about the world

The clearest failure of the bimodal table takes only one line to state and 200
branches to demonstrate: a branch that alternates, taken, not taken, taken, not
taken, is predicted wrong **every single time** — the second column of the first
table, 200 of 200. A coin would have scored 100.

Follow the counter. It starts at 1 and predicts not-taken; the branch is taken,
so that is a miss and the counter goes to 2. Now it predicts taken; the branch is
not taken, another miss, back to 1. The counter is always one step behind a
pattern whose period is two, and being consistently, perfectly wrong is what a
one-step-behind predictor does on a period-two signal. Nothing about the counter
is broken. It is being asked a question it has no state to answer: *what is this
branch usually doing* is the only question a per-address counter can hear, and
the answer here is "half and half".

The pattern is trivially predictable given the right index. Replace "which branch
is this" with "which branch is this, in the context of the last few outcomes":

```python
alt = [i % 2 == 0 for i in range(200)]

def gshare(outcomes, history_bits=4):
    """One counter per recent-history pattern rather than one per branch."""
    hmask = (1 << history_bits) - 1
    table, history, wrong = [1] * (1 << history_bits), 0, 0
    for taken in outcomes:
        i = history & hmask
        wrong += (table[i] >= 2) != taken
        table[i] = min(3, table[i] + 1) if taken else max(0, table[i] - 1)
        history = ((history << 1) | (1 if taken else 0)) & hmask
    return wrong

print("one counter for this branch :", 200, "wrong of 200")
print("one counter per history     :", gshare(alt), "wrong of 200")
```

Three wrong out of 200. The alternating trace visits two history patterns —
`...1010` and `...0101` — and each gets its own counter, one saturating at taken
and the other at not-taken. After a handful of branches to train them the
predictor is never wrong again. That is gshare: the same two-bit counters,
indexed by the branch address XORed with a global history register, so the same
static branch consults different counters in different dynamic contexts. Note the
ordering the lab insists on — index with the *old* history, update the counter,
then shift the outcome in. Shift first and every prediction is made with a
history the machine could not yet have had, which is a model that predicts the
future and a hardware design that does not exist.

## What the accuracy is worth

Accuracy is not the number to optimise; CPI is. Take the loop trace, assume
branches are a fifth of all instructions, so 200 branches means 1000
instructions:

```python
def cpi(mispredicts, instructions, penalty):
    return 1 + penalty * mispredicts / instructions

print("predictor      wrong   accuracy   CPI at penalty 2   at penalty 10")
for name, wrong in (("always-taken", 20), ("one-bit     ", 40), ("two-bit     ", 21)):
    print("%s %5d   %7.1f%%   %14.3f %15.2f"
          % (name, wrong, 100 * (1 - wrong / 200), cpi(wrong, 1000, 2), cpi(wrong, 1000, 10)))
print("accuracy needed for CPI 1.04 with f_br = 0.20 and penalty 10: %.2f"
      % (1 - (1.04 - 1) / (0.20 * 10)))
```

At a penalty of 2 the gap between the best and the worst of these is 1.040
against 1.080 — four hundredths of a cycle per instruction, which is close to
nothing, and it is the honest reason a five-stage machine in 1990 shipped with a
static predictor. At a penalty of 10 the same three predictors are at 1.20, 1.40
and 1.21, and the difference has become a fifth of the machine. The penalty
multiplies the error rate, so the value of accuracy is set by the pipeline it is
attached to. That last line is the same expression rearranged: to hold CPI at
1.04 on the deep machine, the predictor has to be 98% accurate rather than 90% —
which is the distance between a counter per branch and a history-indexed table,
and the reason branch prediction research tracked pipeline depth so closely.

## Where the model runs out

Four things this page assumes are worth writing down as assumptions.

A direction predictor does not give an address. Guessing "taken" is useless
without knowing where, and the target of a taken branch is not known until the
immediate has been decoded and added to the pc — one cycle after fetch. Real
front ends carry a branch target buffer alongside the direction predictor, a
cache from pc to predicted target, and a BTB miss costs a cycle even when the
direction was right. Indirect jumps and function returns need more than that
again; returns get their own hardware stack, because the target is on a stack in
software and predicting it from a BTB fails on the first shared callee.

The tables here are indexed by low address bits and are finite, so two branches
can share a counter. Constructive sharing is harmless and destructive sharing —
one branch mostly taken, one mostly not, in the same entry — costs both of them.
This is the cost gshare pays for XORing history into the index: it spreads one
branch across many entries, so a small table starts colliding sooner. The lab's
comparison of four and eight history bits on the *two loops* trace is that trade
in miniature: eight bits reach back far enough to tell the two loop exits apart
and four do not, while on a single loop the four-bit version is the better of the
two, because there the longer history only scatters one branch across more
entries. More history is not uniformly better.

The traces are direction sequences with no timing in them, so nothing here
accounts for what wrong-path fetches do to the caches — sometimes prefetching
usefully, sometimes evicting something wanted — or for the fact that the two
squashed instructions consumed fetch bandwidth and energy whether or not they
were on the right path.

And accuracy is measured on a warm predictor. Every table starts cold, and a
context switch, a system call or a jump into unfamiliar code empties it in
effect. The 21-of-200 figure includes one warm-up miss because the trace is 200
branches long; on a trace of 20 it would be one in twenty.

The sandbox *What a wrong guess costs* prices the flush in the pipeline picture:
two mispredictions in a nine-instruction window push CPI from 1.44 to 1.89, and
the four cycles between those numbers are the entire budget a predictor has to
work with. The lab, *Build and measure a branch predictor*, is what spends it —
`Bimodal`, `Gshare`, `evaluate` and `cpi`, run against the four traces above,
with the noise trace as the check that a predictor which learns is not
automatically a predictor that wins.
''',
                },
            ],
            "quiz": {
                "title": "What prediction is worth, and when",
                "minutes": 8,
                "questions": [
                    {
                        "q": "On this five-stage machine a mispredicted branch costs two cycles. Which quantity is the 2?",
                        "opts": [
                            "The number of stages that follow EX, since every stage after the resolve point has to be refilled from the corrected target address",
                            "The number of cycles between the branch's fetch and its resolution, which is how many instructions were fetched on the guess",
                            "The depth of the pipeline minus the three stages a branch actually needs to complete its own work",
                            "The number of pipeline registers that must be cleared, one for each latch between the fetch stage and the comparison",
                        ],
                        "a": 1,
                        "whys": [
                            r"MEM and WB do follow EX, and it is a coincidence that there are two of them. Stages after the resolve point hold instructions *older* than the branch, which are on the correct path and are never squashed.",
                            r"IF is stage 0 and EX is stage 2, so fetch slots in cycles 1 and 2 were spent on a guess.",
                            r"Arithmetic that lands on 2 by accident. A branch uses IF, ID and EX and then idles through MEM and WB like everything else; nothing in the penalty is about how much work the branch itself does.",
                            r"Latches are cleared, and there happen to be two of them here, but counting hardware rather than cycles gives the wrong answer as soon as a stage takes more than one cycle. The penalty is a count of wasted fetch opportunities.",
                        ],
                        "why": r"""
The penalty is the distance from fetch to resolution: IF is stage 0, the
comparison happens in EX which is stage 2, so instructions were fetched in cycles
1 and 2 on the strength of a guess and both die. Moving the comparison into ID
makes the penalty 1 and lengthens the cycle, which is a trade some designs take.
Pipeline depth enters only through where the resolve point ends up — a deep front
end pushes it later and the penalty grows with it, which is the whole reason
prediction accuracy became worth spending transistors on.
""",
                    },
                    {
                        "q": "A loop runs nine taken iterations then falls through, twenty times over. A one-bit predictor gets 40 of the 200 branches wrong. Where does the second mistake per trip come from?",
                        "opts": [
                            "The predictor is wrong on the exit, and wrong again on the first iteration of the next trip because the exit rewrote its state",
                            "The first and last iterations of every trip go in opposite directions, so any predictor at all is bound to miss both of them each trip",
                            "The predictor needs one branch to train after each exit and cannot make a prediction at all until it has",
                            "The exit is mispredicted twice, once when the branch is fetched and once when the target is finally resolved",
                        ],
                        "a": 0,
                        "whys": [
                            r"One surprise, two mistakes: the miss on the exit, and the miss it plants in the state for the re-entry.",
                            r"A two-bit counter gets the re-entry right on the same trace, so it is not forced by the trace at all — the 21-versus-40 gap is exactly this claim being false.",
                            r"A one-bit predictor always has a prediction available; the bit holds the last outcome and is read on the next branch with no training period of any kind.",
                            r"A misprediction is counted once, when the outcome is known. Fetch and resolution are two moments in the life of the same guess, not two guesses.",
                        ],
                        "why": r"""
The exit is one miss, and it also overwrites the stored bit with not-taken. The
loop is then re-entered and the first iteration is predicted not-taken and is
taken, which is the second miss. Two per trip, twenty trips, 40 of 200. The
second one is what hysteresis removes: a two-bit counter sitting at 3 drops to 2
on the exit, still predicts taken, and gets the re-entry right — 21 wrong instead
of 40, for one extra flip-flop per table entry.
""",
                    },
                    {
                        "q": "The same loop trace: a two-bit counter gets 21 wrong and always-taken, a predictor with no state at all, gets 20. What does the extra one represent?",
                        "opts": [
                            "Destructive aliasing, where a second branch shares the counter and pushes it in the other direction",
                            "The exit of the twentieth trip, which the counter has no later branch to correct",
                            "The first branch of the trace, predicted not-taken because the counters start at weakly not-taken",
                            "Rounding, since accuracy on 200 branches cannot resolve a difference of one prediction",
                        ],
                        "a": 2,
                        "whys": [
                            r"Aliasing needs at least two branch addresses; this trace has one, so the counter belongs to it alone and nothing else can move it.",
                            r"Always-taken misses that exit too — every one of its 20 misses is an exit. The two predictors agree on all twenty exits, so the difference has to lie elsewhere.",
                            r"The table starts at 1, so the very first branch is predicted not-taken and is taken.",
                            r"One misprediction in 200 is 0.5% and both numbers are exact counts, not estimates. The difference is a specific branch that can be pointed at.",
                        ],
                        "why": r"""
The counters are initialised to 1, weakly not-taken, so the first branch of the
trace is predicted not-taken and is taken: one warm-up miss that a stateless
always-taken predictor never pays. After that the two agree, missing once per
exit, twenty times. The lesson is not that counters are useless but that learning
has a cost, and on a trace where the static guess is already right 90% of the
time the cost is not recovered. It is also why an accuracy quoted on a short
trace is worth less than the same accuracy on a long one.
""",
                    },
                    {
                        "q": "A branch alternates taken, not taken, taken, not taken. A single two-bit counter is wrong on all 200 of them — worse than a coin toss. Why?",
                        "opts": [
                            "The counter saturates at one end and can no longer move, so it repeats one prediction for ever",
                            "Two bits cannot encode four outcomes, so a period-two pattern overflows the state the counter has",
                            "The counter predicts what the branch did most recently, and most recently is exactly the opposite of what comes next",
                            "The prediction is read before the update happens, so the counter is always one branch behind the outcome it was trained on",
                        ],
                        "a": 2,
                        "whys": [
                            r"It never saturates on this trace: it oscillates between 1 and 2, one step in each direction, and both predictions get used. Saturation is what happens on a *biased* stream, and it is the behaviour that makes counters useful there.",
                            r"Two bits encode four states, which is plenty; the counter is asked to predict one outcome, not to store the pattern. The shortage is of *context*, not of bits in the counter.",
                            r"Chasing the last outcome on a period-two signal is being wrong in step, every time.",
                            r"Predicting before updating is correct and necessary — the hardware cannot consult an outcome it has not seen. Reversing the order would be a model that cheats, not a fix.",
                        ],
                        "why": r"""
The counter oscillates between 1 and 2 and is always one step behind: it says
not-taken after a not-taken, and the next outcome is taken. On a period-two
signal, one step behind means wrong in step, so a perfectly consistent predictor
is perfectly wrong. Nothing is broken — a per-address counter can only answer
"what does this branch usually do", and the answer here is "half and half". The
fix is a different index rather than a bigger counter: gshare XORs a global
history register into the index, so the two phases of the alternation land in
different entries and each saturates on its own answer, three wrong out of 200.
""",
                    },
                    {
                        "q": "On a trace that is 68.75% taken with no learnable pattern, two-bit counters are wrong 39.0% of the time while always-taken is wrong 31.25%. What is the adaptive predictor doing wrong?",
                        "opts": [
                            "It tracks the last two or three outcomes, so noise drives it below the taken threshold on a stream that is mostly taken",
                            "Its counters alias with one another across the three branch addresses in the trace and interfere destructively",
                            "It has not been given enough branches to converge, and its accuracy would pass always-taken over a longer run",
                            "It is measured before the tables are warm, so the early mispredictions are being counted against the steady-state rate it later settles at",
                        ],
                        "a": 0,
                        "whys": [
                            r"A counter is a filter over recent outcomes, and filtering noise yields noise; the bias is information, the recent history is not.",
                            r"Three addresses, index bits 0, 8 and 16 of a 64-entry table: no two collide. Aliasing is a real effect and it is not this one.",
                            r"There is nothing to converge to. The outcomes are independent with a fixed probability, so a longer run leaves the counter's behaviour unchanged rather than improving it.",
                            r"Warm-up costs a handful of branches out of 400 and cannot account for eight percentage points. The gap is steady-state behaviour, not a start-up artefact.",
                        ],
                        "why": r"""
A saturating counter is a low-pass filter over recent outcomes, and there is no
signal in this trace to filter for — the outcomes are independent with a fixed
probability of 0.6875. Two or three not-takens in a row drag the counter below 2
and it predicts not-taken on a stream that is mostly taken, which a constant
predictor never does. A two-bit counter has no state that means "taken, about 69%
of the time"; it has four states and it moves on every branch. Adaptivity feels
strictly safe because a learner seems able to settle on the constant answer, and
this one cannot represent it.
""",
                    },
                    {
                        "q": "A predictor gives 90% accuracy with branches at a fifth of instructions. Moving to a deeper front end raises the mispredict penalty from 2 to 10 cycles. What happens?",
                        "opts": [
                            "CPI goes from 1.04 to 1.20, and holding it at 1.04 would now need an accuracy of nearer 98% than 90%",
                            "CPI goes from 1.04 to 1.40, since a penalty of 10 costs five times as much on every branch executed",
                            "CPI is unchanged, because the deeper pipeline retires one instruction per cycle exactly as the shallow one did",
                            "CPI goes from 1.04 to 1.08, as only the branches that were already mispredicted are affected by the change",
                        ],
                        "a": 0,
                        "whys": [
                            r"$0.20 \times 0.10 \times 10 = 0.20$, and inverting the expression for $a$ at a target of 1.04 gives 0.98.",
                            r"This charges the penalty to every branch rather than to the mispredicted tenth of them. It is the cost of stalling on every branch instead of predicting, which is the option prediction exists to avoid.",
                            r"Peak throughput is indeed one per cycle at any depth, and that is the 1 in the expression. The penalty term is added on top of it, and that term has grown fivefold.",
                            r"Only mispredicted branches are affected, which is right, but each of them now costs five times as much: the penalty is a multiplier on the error rate, not an addition to it.",
                        ],
                        "why": r"""
$\mathrm{CPI} = 1 + f_{br}(1-a)c_{mis}$, so with $f_{br} = 0.20$ and $a = 0.90$
the penalty term goes from $0.20 \times 0.10 \times 2 = 0.04$ to
$0.20 \times 0.10 \times 10 = 0.20$. Rearranged for accuracy,
$a = 1 - (\mathrm{CPI} - 1)/(f_{br}c_{mis})$, and a target of 1.04 at a penalty
of 10 needs $a = 0.98$. The predictor did not get worse; the machine got less
tolerant. This is the reason a design that shipped happily with a static
predictor at a penalty of 2 needs a history-indexed table at a penalty of 20.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "What a wrong guess costs",
                "visualiser": "pipeline",
                "minutes": 8,
                "initial": {"dep": 0, "fwd": 1, "miss": 2},
                "brief": r'''
Forwarding is on and there are no data hazards, so everything left in this
picture is control. The `branch mispredicts` slider flushes the front end at
instruction i3 and again at i6.
''',
                "notice": [
                    "Take mispredicts from 0 to 1 to 2. Each one pushes every row below it two cycles to the right — that is the front end being emptied and refilled, and the flush is drawn as the same kind of gap a data stall makes.",
                    "Now go from 2 to 4. Nothing happens. In a nine-instruction window this model only offers two branch slots, i3 and i6, so the third and fourth mispredictions have nowhere to land and the caption stays at CPI 1.89.",
                    "Set dependent pairs to 6 while leaving forwarding on: still CPI 1.89. Seventeen cycles retire nine instructions, and the eight cycles of difference split evenly — four are the pipeline fill, four are the two flushes. Everything above the hazard-free 1.44 is control, and those four cycles are the entire budget a branch predictor has to work with.",
                ],
            },
            "derive": {
                "title": "Accuracy, penalty and CPI",
                "minutes": 13,
                "vars": ["f_br", "a", "c_mis", "CPI"],
                "brief": r'''
Let $f_{br}$ be the fraction of retired instructions that are branches, $a$ the
prediction accuracy, and $c_{mis}$ the cycles lost per misprediction. Assume
forwarding has removed the data hazards, so a correctly predicted branch is free.
''',
                "steps": [
                    {
                        "prompt": "Write the CPI in terms of $f_{br}$, $a$ and $c_{mis}$.",
                        "answer": "1 + f_{br} \\cdot (1 - a) \\cdot c_{mis}",
                        "hint": "The fraction of instructions that are *mispredicted* branches is $f_{br}(1-a)$.",
                        "deconstruct": [
                            "Every instruction costs one cycle.",
                            "A fraction $f_{br}$ are branches, and $(1-a)$ of those are wrong.",
                            "Each of those costs $c_{mis}$ extra cycles.",
                        ],
                    },
                    {
                        "prompt": "A five-stage machine resolves branches in EX, so $c_{mis} = 2$. With $f_{br} = 0.20$ and $a = 0.90$, what is the CPI?",
                        "answer": "1.04",
                        "hint": "$0.20 \\times 0.10 \\times 2$, then add one.",
                        "deconstruct": [
                            "Mispredicted branches are $0.20 \\times 0.10 = 0.02$ of all instructions.",
                            "Each costs two cycles: $0.04$.",
                            "CPI $= 1.04$ — a shallow pipeline barely notices a mediocre predictor.",
                        ],
                    },
                    {
                        "prompt": "Now deepen the pipeline until a branch resolves ten cycles after fetch, so $c_{mis} = 10$. Same $f_{br} = 0.20$ and $a = 0.90$. What is the CPI?",
                        "answer": "1.2",
                        "hint": "Only $c_{mis}$ changed, and it is a linear factor.",
                        "deconstruct": [
                            "$0.20 \\times 0.10 \\times 10 = 0.20$.",
                            "CPI $= 1.20$: the same predictor that was adequate is now costing a fifth of the machine.",
                        ],
                    },
                    {
                        "prompt": "Rearrange the CPI expression for the accuracy $a$ needed to hit a target CPI.",
                        "answer": "1 - \\frac{CPI - 1}{f_{br} \\cdot c_{mis}}",
                        "hint": "Subtract 1 from both sides, divide by $f_{br} c_{mis}$, and solve for $a$.",
                        "deconstruct": [
                            "$CPI - 1 = f_{br}(1-a)c_{mis}$.",
                            "So $1 - a = (CPI-1)/(f_{br}c_{mis})$.",
                        ],
                    },
                    {
                        "prompt": "On that deep machine, what accuracy brings the CPI back down to 1.04?",
                        "answer": "0.98",
                        "hint": "Substitute $CPI = 1.04$, $f_{br} = 0.20$, $c_{mis} = 10$.",
                        "deconstruct": [
                            "$(1.04 - 1)/(0.20 \\times 10) = 0.04/2 = 0.02$.",
                            "$a = 1 - 0.02 = 0.98$.",
                            "Going from 90% to 98% is not a tweak; it is the difference between a counter per branch and a history-indexed table.",
                        ],
                    },
                ],
                "closing": r'''
The same predictor is adequate on one machine and unaffordable on another,
because the penalty multiplies the error rate. This is why branch prediction
research followed pipeline depth: at $c_{mis} = 2$ nobody needed gshare, and at
$c_{mis} = 20$ nothing else would do.
''',
            },
            "blanks": {
                "title": "What a wrong guess costs",
                "minutes": 8,
                "caption": "branch.py — penalty, accuracy, and the CPI they produce",
                "lang": "python",
                "brief": r"""
A predictor is judged by one number, and it is not its accuracy — it is the CPI that
accuracy buys. Fill in the chain that connects them.

The branch resolves in EX, and the front end has been fetching all along.
""",
                "listing": """# Instructions fetched after the branch and thrown away on a mispredict:
penalty = ___

b = 0.20                      # fraction of instructions that are branches
a = 0.92                      # fraction of those predicted correctly

# Added CPI from mispredicts:
cpi_penalty = b * ___ * penalty

# A two-bit saturating counter changes its prediction only after ___ ,
# which is why a loop's single exit no longer flips it.
""",
                "blanks": [
                    {
                        "prompt": "Fetch is in stage 1, the branch resolves in stage 3. How many are in flight?",
                        "hole": "?",
                        "opts": ["2", "1", "3", "5"],
                        "a": 0,
                        "why": "Two: the instructions fetched in the cycles the branch spent in ID and EX. They are squashed when the real target arrives. Resolving one stage earlier would save one of them, which is exactly why some designs move branch comparison into ID and pay for it with a longer cycle.",
                        "whys": [
                            "Two: the instructions fetched in the cycles the branch spent in ID and EX. They are squashed when the real target arrives. Resolving one stage earlier would save one of them, which is exactly why some designs move branch comparison into ID and pay for it with a longer cycle.",
                            "One is the cost if the branch resolved in ID. Here it resolves a stage later, and the front end has fetched one more by then.",
                            "Three would be the cost of resolving in MEM. Counting stages between fetch and resolve is the way to get this right, rather than memorising a number.",
                            "The depth of the pipe is not the penalty: instructions ahead of the branch are unaffected, and stages after the resolve point have nothing to squash.",
                        ],
                    },
                    {
                        "prompt": "Only the wrong guesses cost anything.",
                        "hole": "?",
                        "opts": ["(1 - a)", "a", "(1 + a)", "1"],
                        "a": 0,
                        "why": "The mispredict *rate*. Here $0.20 \\times 0.08 \\times 2 = 0.032$ — three hundredths of a cycle per instruction, from a predictor that is wrong nearly one time in twelve. That small number is why prediction is worth doing and why chasing the last percent of accuracy has such poor returns.",
                        "whys": [
                            "The mispredict *rate*. Here $0.20 \\times 0.08 \\times 2 = 0.032$ — three hundredths of a cycle per instruction, from a predictor that is wrong nearly one time in twelve. That small number is why prediction is worth doing and why chasing the last percent of accuracy has such poor returns.",
                            "That charges the penalty to every branch predicted *correctly*, which is precisely the set that costs nothing — a perfect predictor would come out as the most expensive.",
                            "Greater than one, so the machine would lose more cycles than it has branches.",
                            "This is the no-prediction case, where every branch pays. Comparing it against the correct expression is the honest way to state what the predictor bought.",
                        ],
                    },
                    {
                        "prompt": "What makes a two-bit counter different from a one-bit one?",
                        "hole": "?",
                        "opts": [
                            "two consecutive surprises",
                            "one surprise",
                            "every branch",
                            "a pipeline flush",
                        ],
                        "a": 0,
                        "why": "Two-bit is hysteresis. A loop that runs a hundred times and exits once flips a one-bit predictor twice — wrong on the exit, then wrong again on the next entry — while a two-bit counter absorbs the exit as a single surprise and is still predicting 'taken' when the loop restarts. One extra flip-flop per entry, and it halves the mispredicts on exactly the pattern loops produce.",
                        "whys": [
                            "Two-bit is hysteresis. A loop that runs a hundred times and exits once flips a one-bit predictor twice — wrong on the exit, then wrong again on the next entry — while a two-bit counter absorbs the exit as a single surprise and is still predicting 'taken' when the loop restarts. One extra flip-flop per entry, and it halves the mispredicts on exactly the pattern loops produce.",
                            "That is the one-bit predictor, and it is the behaviour the second bit exists to prevent.",
                            "A predictor that changed its mind on every branch would carry no state and predict nothing.",
                            "The flush is the consequence of a mispredict, not the thing the counter responds to; the counter is updated by the branch's actual outcome.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Build and measure a branch predictor",
                "runtime": "python",
                "minutes": 42,
                "brief": r'''
`traces.py` is provided and returns lists of `(pc, taken)` pairs. Do not edit it.
Build the predictors that have to guess them.

`Bimodal(index_bits)` — a table of $2^{\text{index bits}}$ two-bit saturating
counters, every one starting at 1 (weakly not taken). Index with `(pc >> 2) &
mask` — the low two bits of an aligned address carry no information.

- `predict(pc)` returns `True` when the counter is 2 or 3.
- `update(pc, taken)` moves the counter one step towards the outcome and
  saturates at 0 and 3.

`Gshare(index_bits, history_bits)` — the same table, indexed by
`((pc >> 2) ^ history) & mask`, where `history` is a shift register of the last
`history_bits` outcomes, 1 for taken. `update` must shift the outcome in **after**
using the old history for the index.

`evaluate(pred, trace)` runs a trace and returns the number of mispredictions,
predicting each branch before updating on it.

`cpi(mispredicts, instructions, penalty)` returns
$1 + \text{penalty} \times \text{mispredicts} / \text{instructions}$.
''',
                "files": [
                    {"name": "traces.py", "ro": True, "content": TRACES_PY},
                    {"name": "main.py", "content": r'''
import traces


class Bimodal:
    """A two-bit saturating counter per branch address."""

    def __init__(self, index_bits=6):
        self.mask = (1 << index_bits) - 1
        self.table = [1] * (1 << index_bits)

    def index(self, pc):
        # TODO: drop the two always-zero low bits, then mask.
        return 0

    def predict(self, pc):
        # TODO: taken when the counter is in the top half of its range.
        return False

    def update(self, pc, taken):
        # TODO: one step towards the outcome, saturating at 0 and 3.
        pass


class Gshare:
    """The same counters, indexed by address XOR global history."""

    def __init__(self, index_bits=6, history_bits=4):
        self.mask = (1 << index_bits) - 1
        self.hmask = (1 << history_bits) - 1
        self.table = [1] * (1 << index_bits)
        self.history = 0

    def index(self, pc):
        # TODO: XOR the shifted pc with the history register.
        return 0

    def predict(self, pc):
        # TODO: the same rule as Bimodal, over this class's index.
        return False

    def update(self, pc, taken):
        # TODO: update the counter, then shift the outcome into the history.
        pass


def evaluate(pred, trace):
    """Run a trace and count the mispredictions."""
    # TODO: predict first, then update, for every (pc, taken) pair.
    return 0


def cpi(mispredicts, instructions, penalty=2):
    """CPI of an otherwise ideal pipeline with this many mispredictions."""
    # TODO
    return 0.0


if __name__ == "__main__":
    for name, trace in (("loop", traces.loop_trace()),
                        ("alternating", traces.alternating()),
                        ("two loops", traces.two_loops()),
                        ("noise", traces.pseudo_random())):
        b = evaluate(Bimodal(), trace)
        g = evaluate(Gshare(history_bits=8), trace)
        print("%-12s n=%4d  bimodal=%4d  gshare=%4d" % (name, len(trace), b, g))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import traces


class Bimodal:
    """A two-bit saturating counter per branch address."""

    def __init__(self, index_bits=6):
        self.mask = (1 << index_bits) - 1
        self.table = [1] * (1 << index_bits)

    def index(self, pc):
        return (pc >> 2) & self.mask

    def predict(self, pc):
        return self.table[self.index(pc)] >= 2

    def update(self, pc, taken):
        i = self.index(pc)
        if taken:
            self.table[i] = min(3, self.table[i] + 1)
        else:
            self.table[i] = max(0, self.table[i] - 1)


class Gshare:
    """The same counters, indexed by address XOR global history."""

    def __init__(self, index_bits=6, history_bits=4):
        self.mask = (1 << index_bits) - 1
        self.hmask = (1 << history_bits) - 1
        self.table = [1] * (1 << index_bits)
        self.history = 0

    def index(self, pc):
        return ((pc >> 2) ^ self.history) & self.mask

    def predict(self, pc):
        return self.table[self.index(pc)] >= 2

    def update(self, pc, taken):
        i = self.index(pc)
        if taken:
            self.table[i] = min(3, self.table[i] + 1)
        else:
            self.table[i] = max(0, self.table[i] - 1)
        self.history = ((self.history << 1) | (1 if taken else 0)) & self.hmask


def evaluate(pred, trace):
    """Run a trace and count the mispredictions."""
    wrong = 0
    for pc, taken in trace:
        if pred.predict(pc) != taken:
            wrong += 1
        pred.update(pc, taken)
    return wrong


def cpi(mispredicts, instructions, penalty=2):
    """CPI of an otherwise ideal pipeline with this many mispredictions."""
    return 1.0 + penalty * mispredicts / instructions


if __name__ == "__main__":
    for name, trace in (("loop", traces.loop_trace()),
                        ("alternating", traces.alternating()),
                        ("two loops", traces.two_loops()),
                        ("noise", traces.pseudo_random())):
        b = evaluate(Bimodal(), trace)
        g = evaluate(Gshare(history_bits=8), trace)
        print("%-12s n=%4d  bimodal=%4d  gshare=%4d" % (name, len(trace), b, g))
'''}],
                "hints": [
                    "Saturation without a branch table: `min(3, c + 1)` when taken, `max(0, c - 1)` when not.",
                    "`predict` must not change any state. If `evaluate` gives a suspiciously low number, check that you are not updating before predicting.",
                    "In `Gshare.update`, compute the index from the *old* history, update that counter, and only then shift the outcome in. Doing it the other way round predicts with a history the machine could not have had.",
                ],
                "tests": [
                    {"name": "a two-bit counter has hysteresis", "code": r'''
_p = Bimodal()
assert _p.index(0x100) != _p.index(0x104), \
    ("two instructions four bytes apart must land in different counters; an index that "
     "keeps the two low bits puts them in the same one: got %d and %d"
     % (_p.index(0x100), _p.index(0x104)))
assert not _p.predict(0x100), "the counters start at 1, which is weakly not taken"
_p.update(0x100, True)
assert _p.predict(0x100), "one taken takes the counter from 1 to 2, which predicts taken"
for _ in range(3):
    _p.update(0x100, True)
assert _p.table[_p.index(0x100)] == 3, \
    f"four takens saturate at 3 and must not run past it, got {_p.table[_p.index(0x100)]}"
_p.update(0x100, False)
assert _p.predict(0x100), \
    "one surprise must not change the prediction — that hysteresis is the whole point"
_p.update(0x100, False)
assert not _p.predict(0x100), "two in a row should flip it"
for _ in range(3):
    _p.update(0x100, False)
assert _p.table[_p.index(0x100)] == 0, \
    f"and it saturates at 0 at the bottom, got {_p.table[_p.index(0x100)]}"
'''},
                    {"name": "a loop is predicted well after the first trip", "code": r'''
import traces
_t = traces.loop_trace(trips=20, body=10)
_m = evaluate(Bimodal(), _t)
assert _m == 21, \
    ("a ten-iteration loop should cost about one mispredict per trip, at the exit: "
     "expected 21 out of 200, got %d" % _m)
'''},
                    {"name": "one counter cannot represent an alternating pattern", "code": r'''
import traces
_t = traces.alternating(200)
_m = evaluate(Bimodal(), _t)
assert _m == 200, \
    ("a single counter chases the last outcome and is therefore wrong every single "
     "time on a period-two pattern: expected 200 of 200, got %d" % _m)
'''},
                    {"name": "history turns the same pattern into an easy one", "code": r'''
import traces
_t = traces.alternating(200)
_m = evaluate(Gshare(history_bits=4), _t)
assert _m == 3, \
    ("gshare gives each history context its own counter, so it learns the alternation "
     "in a handful of branches and is never wrong again: expected 3 of 200, got %d" % _m)
'''},
                    {"name": "history length is what separates two loops", "code": r'''
import traces
_t = traces.two_loops(trips=15)
_bi = evaluate(Bimodal(), _t)
_short = evaluate(Gshare(history_bits=4), _t)
_long = evaluate(Gshare(history_bits=8), _t)
assert _long < _bi, \
    ("eight bits of history reach back far enough to tell the two loop exits apart: "
     "gshare-8 got %d against bimodal's %d" % (_long, _bi))
assert _long < _short, \
    ("four bits are not enough for a six-iteration loop: gshare-4 got %d, gshare-8 %d"
     % (_short, _long))
'''},
                    {"name": "a counter chasing noise loses to a static guess", "code": r'''
import traces
_learnable = traces.loop_trace(trips=30, body=12)
_noise = traces.pseudo_random(400, percent_taken=70, seed=12345)
_good = evaluate(Bimodal(), _learnable) / len(_learnable)
assert _good < 0.12, f"the same predictor handles the loop well, got {_good:.3f} wrong"
_bad = evaluate(Bimodal(), _noise) / len(_noise)
_static = sum(1 for _pc, _taken in _noise if not _taken) / len(_noise)
assert abs(_static - 0.3125) < 1e-12, \
    f"this trace is 68.75% taken, so always-taken is wrong 0.3125 of the time, got {_static}"
assert _bad > _static, \
    ("with no pattern to learn, a counter that chases the last outcome is beaten by a "
     "predictor with no state at all: it gets %.3f wrong against always-taken's %.3f"
     % (_bad, _static))
'''},
                    {"name": "mispredictions become a CPI", "code": r'''
assert abs(cpi(20, 1000, 2) - 1.04) < 1e-12, \
    f"20 mispredicts in 1000 instructions at 2 cycles each is CPI 1.04, got {cpi(20, 1000, 2)}"
assert abs(cpi(20, 1000, 10) - 1.2) < 1e-12, \
    f"the same predictor on a deeper pipeline costs 1.2, got {cpi(20, 1000, 10)}"
assert abs(cpi(0, 1000, 10) - 1.0) < 1e-12, "a perfect predictor costs nothing"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A cycle-accurate RV32I core",
        "runtime": "python",
        "minutes": 150,
        "brief": r'''
Put the four modules together into one model that both **executes** an RV32I
program and **times** it, and use it to answer the question the whole course has
been circling: what does this machine actually cost per instruction?

`isa.py` is provided again — assembler and decoder, unchanged. Everything else
is yours.

## The functional half

A register file of 32 words with `x0` hard-wired to zero, a data memory as a dict from
byte address to the 32-bit word stored there, and a program counter. `execute(ins)` applies one instruction
and returns `(next_pc, taken)`:

- R and I arithmetic: `add sub sll slt xor srl or and`, `addi slti xori ori andi`
- `lw` / `sw` at `reg[rs1] + imm`
- `beq bne blt bge`, signed, target `pc + imm`
- `lui` writes the immediate; `jal` writes `pc + 4` and jumps
- results wrap to 32 bits; comparisons are signed

Execution stops when the pc leaves the program.

## The timing half

The same model as modules 2 and 3, applied to the *dynamic* instruction stream:

```text
stages         IF=0 ID=1 EX=2 MEM=3 WB=4, instruction i enters IF in cycle s[i]
in-order       s[i] >= s[i-1] + 1
no forwarding  s[i] >= s[j] + 3
forwarding     s[i] + use >= s[j] + ready + 1
mispredict     the next instruction issues at s[branch] + 3
total          s[last] + 5
```

`ready` is EX for the ALU and MEM for a load; `use` is EX for everything except
the data operand of a store, which is MEM. A branch resolves in EX, so a wrong
guess costs `FLUSH = 2` cycles. A correct guess costs nothing, in either
direction.

## The predictors

`NotTaken` is given. Write `Bimodal` — the module 4 predictor, two-bit counters
indexed by `(pc >> 2)`.

## What to report

`stats()` returns `cycles`, `retired`, `cpi`, `mispredicts` and `stalls`, where
`stalls` is the total number of cycles instructions were held back by data
hazards alone.

The reference core runs the ten-element sum in `main.py` in **76 cycles** with
forwarding and a not-taken predictor, and **107** without forwarding. If your
numbers differ, the timing rules above are the place to look, one line at a time.
''',
        "deliverables": [
            "`execute(ins)` — the functional semantics of the subset, returning the next pc and whether a branch was taken, with `x0` unwritable and all results wrapped to 32 bits.",
            "`Core.run()` — fetch, decode, execute and retire until the pc leaves the program, accumulating the issue cycle of every dynamic instruction.",
            "The timing rules of modules 2 and 3 applied to the dynamic stream, with `forwarding` switchable so the two can be compared on the same program.",
            "`Bimodal`, and a mispredict penalty of two cycles applied to the instruction behind a wrongly predicted branch.",
            "`stats()` reporting cycles, retired instructions, CPI, mispredicts and data-hazard stall cycles, and a comment at the top of `main.py` giving the CPI you measure for the sum program under each of the four configurations.",
        ],
        "constraints": [
            "The standard library only — no numpy needed anywhere in this build.",
            "`isa.py` is read-only; if you find yourself wanting to change it, the change belongs in your own code.",
            "The timing model must never look at an instruction that has not been fetched: the issue cycle of instruction `i` may depend only on instructions before it.",
            "Deterministic: the same program and the same predictor must give the same cycle count every run.",
            "Do not special-case the test programs. Every check runs code that is assembled from text at check time.",
        ],
        "rubric": [
            {"criterion": "Functional correctness", "weight": 30,
             "evidence": "The summation program leaves 55 in a register and in memory, x0 stays zero after a program writes to it, and branches are taken exactly when the signed comparison says so."},
            {"criterion": "Hazard timing", "weight": 30,
             "evidence": "Cycle counts match the stated rules on straight-line code, a dependent chain, and a load-use pair, with and without forwarding, on programs assembled at check time."},
            {"criterion": "Branch prediction", "weight": 25,
             "evidence": "A bimodal predictor mispredicts strictly fewer branches than always-not-taken on a loop, and each avoided mispredict is worth exactly two cycles in the total."},
            {"criterion": "Reporting", "weight": 15,
             "evidence": "stats() reports cycles, retired, CPI, mispredicts and stall cycles consistently, with CPI equal to cycles divided by retired instructions."},
        ],
        "hints": [
            "Build the functional half first and get 55 out of the sum program with no timing at all. A timing model wrapped around a wrong execution is unreadable.",
            "Keep two dicts through the run: register number to the issue cycle of its most recent writer, and register number to that writer's decoded instruction. The second one is what `ready_stage` needs.",
            "The mispredict penalty is not a stall on the branch — the branch itself issues on time. It delays the *next* instruction, so apply it to the running `earliest` bound after the branch has been scheduled.",
            "Count `stalls` as the difference between the cycle an instruction actually issues and the cycle in-order issue alone would have allowed, before adding any flush penalty.",
        ],
        "files": [
            {"name": "isa.py", "ro": True, "content": ISA_PY},
            {"name": "main.py", "content": r'''
import isa

MASK = 0xFFFFFFFF
IF, ID, EX, ME, WB = 0, 1, 2, 3, 4
FLUSH = 2          # a branch resolves in EX, so two fetched instructions die

# Measured CPI for the sum program:
#   forwarding + not-taken   -> TODO
#   forwarding + bimodal     -> TODO
#   stalling   + not-taken   -> TODO
#   stalling   + bimodal     -> TODO


def to_signed(v):
    """Read a 32-bit pattern as a signed integer."""
    v &= MASK
    return v - (1 << 32) if v & 0x80000000 else v


class NotTaken:
    """The cheapest predictor there is: the fall-through path, always. Given."""

    def predict(self, pc):
        return False

    def update(self, pc, taken):
        pass


class Bimodal:
    """Two-bit saturating counters indexed by the branch address."""

    def __init__(self, index_bits=6):
        self.mask = (1 << index_bits) - 1
        self.table = [1] * (1 << index_bits)

    def predict(self, pc):
        # TODO
        return False

    def update(self, pc, taken):
        # TODO
        pass


class Core:
    def __init__(self, words, data=None, forwarding=True, predictor=None, limit=100000):
        self.imem = list(words)
        self.dmem = dict(data or {})
        self.reg = [0] * 32
        self.pc = 0
        self.forwarding = forwarding
        self.predictor = predictor if predictor is not None else NotTaken()
        self.limit = limit
        self.cycles = 0
        self.retired = 0
        self.mispredicts = 0
        self.stalls = 0

    # ---- functional
    def execute(self, ins):
        """Apply one instruction. Return (next_pc, branch_taken)."""
        # TODO: read the operands, compute, write rd unless it is x0, and
        # decide the next pc.
        return self.pc + 4, False

    # ---- timing
    def sources(self, ins):
        """The registers this instruction reads. Module 2's answer, given."""
        fmt = ins["fmt"]
        if fmt in ("R", "S", "B"):
            return [ins["rs1"], ins["rs2"]]
        if fmt == "I":
            return [ins["rs1"]]
        return []

    def ready_stage(self, ins):
        """The stage at whose end this instruction's result exists."""
        # TODO
        return EX

    def use_stage(self, ins, reg):
        """The stage at whose start this instruction needs `reg`."""
        # TODO
        return EX

    def run(self):
        """Fetch, execute and time until the pc leaves the program."""
        # TODO: the whole loop. Return the number of instructions retired.
        return 0

    def stats(self):
        return {"cycles": self.cycles, "retired": self.retired,
                "cpi": self.cycles / self.retired if self.retired else 0.0,
                "mispredicts": self.mispredicts, "stalls": self.stalls}


SUM = """
    addi x1, x0, 0        # running total
    addi x2, x0, 0        # byte offset into the array
    addi x3, x0, 40       # one past the end
loop:
    lw   x4, 0(x2)
    add  x1, x1, x4
    addi x2, x2, 4
    bne  x2, x3, loop
    sw   x1, 64(x0)
"""

if __name__ == "__main__":
    words = isa.assemble(SUM)
    data = {4 * i: i + 1 for i in range(10)}
    for fwd in (True, False):
        for name, pred in (("not-taken", NotTaken()), ("bimodal", Bimodal())):
            core = Core(words, data, forwarding=fwd, predictor=pred)
            core.run()
            print("forwarding=%-5s %-10s x1=%s %s"
                  % (fwd, name, core.reg[1], core.stats()))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import isa

MASK = 0xFFFFFFFF
IF, ID, EX, ME, WB = 0, 1, 2, 3, 4
FLUSH = 2          # a branch resolves in EX, so two fetched instructions die

# Measured CPI for the sum program (44 instructions retired):
#   forwarding + not-taken   -> 76 cycles, CPI 1.73
#   forwarding + bimodal     -> 62 cycles, CPI 1.41
#   stalling   + not-taken   -> 107 cycles, CPI 2.43
#   stalling   + bimodal     -> 93 cycles, CPI 2.11
# Forwarding is worth 31 cycles under either predictor and the predictor 14 under
# either forwarding setting: on this program the two savings are exactly additive,
# because they remove different cycles.


def to_signed(v):
    """Read a 32-bit pattern as a signed integer."""
    v &= MASK
    return v - (1 << 32) if v & 0x80000000 else v


class NotTaken:
    """The cheapest predictor there is: the fall-through path, always. Given."""

    def predict(self, pc):
        return False

    def update(self, pc, taken):
        pass


class Bimodal:
    """Two-bit saturating counters indexed by the branch address."""

    def __init__(self, index_bits=6):
        self.mask = (1 << index_bits) - 1
        self.table = [1] * (1 << index_bits)

    def predict(self, pc):
        return self.table[(pc >> 2) & self.mask] >= 2

    def update(self, pc, taken):
        i = (pc >> 2) & self.mask
        self.table[i] = min(3, self.table[i] + 1) if taken else max(0, self.table[i] - 1)


class Core:
    def __init__(self, words, data=None, forwarding=True, predictor=None, limit=100000):
        self.imem = list(words)
        self.dmem = dict(data or {})
        self.reg = [0] * 32
        self.pc = 0
        self.forwarding = forwarding
        self.predictor = predictor if predictor is not None else NotTaken()
        self.limit = limit
        self.cycles = 0
        self.retired = 0
        self.mispredicts = 0
        self.stalls = 0

    # ---- functional
    def execute(self, ins):
        """Apply one instruction. Return (next_pc, branch_taken)."""
        pc, r = self.pc, self.reg
        name, rd, rs1, rs2, imm = (ins["name"], ins["rd"], ins["rs1"],
                                   ins["rs2"], ins["imm"])
        a = to_signed(r[rs1]) if rs1 is not None else 0
        b = to_signed(r[rs2]) if rs2 is not None else 0
        nxt, taken, val = pc + 4, False, None
        if ins["fmt"] == "R":
            val = {"add": a + b, "sub": a - b, "sll": a << (b & 31),
                   "slt": 1 if a < b else 0, "xor": a ^ b,
                   "srl": (a & MASK) >> (b & 31), "or": a | b, "and": a & b}[name]
        elif name in ("addi", "slti", "xori", "ori", "andi"):
            val = {"addi": a + imm, "slti": 1 if a < imm else 0, "xori": a ^ imm,
                   "ori": a | imm, "andi": a & imm}[name]
        elif name == "lw":
            val = to_signed(self.dmem.get((a + imm) & MASK, 0))
        elif name == "sw":
            self.dmem[(a + imm) & MASK] = b & MASK
        elif ins["fmt"] == "B":
            taken = {"beq": a == b, "bne": a != b, "blt": a < b, "bge": a >= b}[name]
            if taken:
                nxt = pc + imm
        elif name == "lui":
            val = imm
        elif name == "jal":
            val, nxt, taken = pc + 4, pc + imm, True
        if val is not None and rd:
            r[rd] = val & MASK
        return nxt, taken

    # ---- timing
    def sources(self, ins):
        """The registers this instruction reads. Module 2's answer, given."""
        fmt = ins["fmt"]
        if fmt in ("R", "S", "B"):
            return [ins["rs1"], ins["rs2"]]
        if fmt == "I":
            return [ins["rs1"]]
        return []

    def ready_stage(self, ins):
        """The stage at whose end this instruction's result exists."""
        return ME if ins["name"] == "lw" else EX

    def use_stage(self, ins, reg):
        """The stage at whose start this instruction needs `reg`."""
        if ins["fmt"] == "S" and reg == ins["rs2"] and reg != ins["rs1"]:
            return ME
        return EX

    def run(self):
        """Fetch, execute and time until the pc leaves the program."""
        writer, producer = {}, {}
        start, earliest = 0, 0
        while 0 <= self.pc < 4 * len(self.imem) and self.retired < self.limit:
            ins = isa.decode(self.imem[self.pc // 4])
            t = earliest
            for r in self.sources(ins):
                if r and r in writer:
                    if self.forwarding:
                        need = self.use_stage(ins, r)
                        have = self.ready_stage(producer[r])
                        t = max(t, writer[r] + have + 1 - need)
                    else:
                        t = max(t, writer[r] + 3)
            self.stalls += t - earliest
            start = t
            if ins["fmt"] in ("R", "I", "U", "J") and ins["rd"]:
                writer[ins["rd"]] = start
                producer[ins["rd"]] = ins
            nxt, taken = self.execute(ins)
            earliest = start + 1
            if ins["fmt"] == "B":
                guess = self.predictor.predict(self.pc)
                self.predictor.update(self.pc, taken)
                if guess != taken:
                    self.mispredicts += 1
                    earliest = start + 1 + FLUSH
            self.retired += 1
            self.pc = nxt
        self.cycles = start + 5 if self.retired else 0
        return self.retired

    def stats(self):
        return {"cycles": self.cycles, "retired": self.retired,
                "cpi": self.cycles / self.retired if self.retired else 0.0,
                "mispredicts": self.mispredicts, "stalls": self.stalls}


SUM = """
    addi x1, x0, 0        # running total
    addi x2, x0, 0        # byte offset into the array
    addi x3, x0, 40       # one past the end
loop:
    lw   x4, 0(x2)
    add  x1, x1, x4
    addi x2, x2, 4
    bne  x2, x3, loop
    sw   x1, 64(x0)
"""

if __name__ == "__main__":
    words = isa.assemble(SUM)
    data = {4 * i: i + 1 for i in range(10)}
    for fwd in (True, False):
        for name, pred in (("not-taken", NotTaken()), ("bimodal", Bimodal())):
            core = Core(words, data, forwarding=fwd, predictor=pred)
            core.run()
            print("forwarding=%-5s %-10s x1=%s %s"
                  % (fwd, name, core.reg[1], core.stats()))
'''},
        ],
        "tests": [
            {"name": "the core executes a real program", "code": r'''
import isa
_words = isa.assemble(SUM)
_data = {4 * i: i + 1 for i in range(10)}
_c = Core(_words, _data, forwarding=True, predictor=NotTaken())
_c.run()
assert _c.reg[1] == 55, f"the sum of 1..10 is 55, and it should be in x1; got {_c.reg[1]}"
assert _c.dmem.get(64) == 55, "the final store should put the total at address 64"
assert _c.retired == 44, \
    f"three setup instructions plus ten trips of four plus one store is 44, got {_c.retired}"
'''},
            {"name": "x0 cannot be written and branches compare signed", "code": r'''
import isa
_p = isa.assemble("""
    addi x0, x0, 7
    addi x1, x0, 3
    addi x2, x0, -5
    blt  x2, x1, ahead
    addi x3, x0, 99
ahead:
    addi x4, x0, 1
""")
_c = Core(_p, {}, forwarding=True, predictor=NotTaken())
_c.run()
assert _c.reg[0] == 0, f"x0 is hard-wired to zero and must survive a write, got {_c.reg[0]}"
assert _c.reg[1] == 3, "x1 = x0 + 3 must be 3, which also proves x0 read as zero"
assert _c.reg[3] == 0, \
    "blt is a *signed* comparison: -5 < 3, so the branch is taken and x3 is skipped"
assert _c.reg[4] == 1, "execution should continue at the branch target"
'''},
            {"name": "straight-line code costs one cycle per instruction", "code": r'''
import isa
_p = isa.assemble("""
    addi x1, x0, 1
    addi x2, x0, 2
    addi x3, x0, 3
    addi x4, x0, 4
    addi x5, x0, 5
    addi x6, x0, 6
""")
_c = Core(_p, {}, forwarding=True, predictor=NotTaken())
_c.run()
assert _c.cycles == 10, \
    f"six independent instructions and four cycles of drain is 10, got {_c.cycles}"
assert _c.stalls == 0, f"nothing here can stall, got {_c.stalls} stall cycles"
assert abs(_c.stats()["cpi"] - 10.0 / 6.0) < 1e-12, "cpi is cycles over retired"
'''},
            {"name": "forwarding removes the chain stalls and not the load-use one", "code": r'''
import isa
_chain = isa.assemble("""
    addi x1, x0, 1
    add  x2, x1, x1
    add  x3, x2, x2
    add  x4, x3, x3
""")
_fast = Core(_chain, {}, forwarding=True, predictor=NotTaken())
_fast.run()
_slow = Core(_chain, {}, forwarding=False, predictor=NotTaken())
_slow.run()
assert _fast.cycles == 8, f"forwarded, this chain is hazard-free: expected 8, got {_fast.cycles}"
assert _slow.cycles == 14, f"stalling, each link costs two bubbles: expected 14, got {_slow.cycles}"
assert _fast.reg[4] == _slow.reg[4] == 8, \
    "timing must not change the answer: x4 is 8 either way"

_lu = isa.assemble("""
    lw   x1, 0(x0)
    add  x2, x1, x1
""")
_c = Core(_lu, {0: 21}, forwarding=True, predictor=NotTaken())
_c.run()
assert _c.cycles == 7, \
    f"one load-use bubble on top of the ideal 6: expected 7, got {_c.cycles}"
assert _c.stalls == 1, f"exactly one stall cycle, got {_c.stalls}"
assert _c.reg[2] == 42, "and the loaded value is still doubled correctly"
'''},
            {"name": "a wrong guess costs exactly two cycles", "code": r'''
import isa
_words = isa.assemble(SUM)
_data = {4 * i: i + 1 for i in range(10)}
_nt = Core(_words, _data, forwarding=True, predictor=NotTaken())
_nt.run()
_bi = Core(_words, _data, forwarding=True, predictor=Bimodal())
_bi.run()
assert _nt.mispredicts == 9, \
    f"always-not-taken misses every taken back-edge: expected 9, got {_nt.mispredicts}"
assert _bi.mispredicts == 2, \
    ("two-bit counters learn the loop and only miss the exit and the warm-up: "
     "expected 2, got %d" % _bi.mispredicts)
assert _nt.cycles - _bi.cycles == 2 * (_nt.mispredicts - _bi.mispredicts), \
    ("seven avoided mispredicts must be worth exactly fourteen cycles: %d against %d"
     % (_nt.cycles, _bi.cycles))
assert _nt.stalls == _bi.stalls, \
    "the predictor changes no data hazard, so the stall count must be identical"
'''},
            {"name": "the four configurations line up with the reference", "code": r'''
import isa
_words = isa.assemble(SUM)
_data = {4 * i: i + 1 for i in range(10)}
_got = {}
for _fwd in (True, False):
    for _name, _pred in (("nt", NotTaken()), ("bi", Bimodal())):
        _c = Core(_words, _data, forwarding=_fwd, predictor=_pred)
        _c.run()
        assert _c.reg[1] == 55, f"every configuration must still compute 55, got {_c.reg[1]}"
        _got[(_fwd, _name)] = _c.cycles
assert _got[(True, "nt")] == 76, f"forwarding + not-taken should be 76, got {_got[(True, 'nt')]}"
assert _got[(False, "nt")] == 107, f"stalling + not-taken should be 107, got {_got[(False, 'nt')]}"
assert _got[(True, "bi")] == 62, f"forwarding + bimodal should be 62, got {_got[(True, 'bi')]}"
assert _got[(False, "bi")] == 93, f"stalling + bimodal should be 93, got {_got[(False, 'bi')]}"
'''},
            {"name": "the model is deterministic", "code": r'''
import isa
_words = isa.assemble(SUM)
_data = {4 * i: i + 1 for i in range(10)}
_a = Core(_words, _data, forwarding=True, predictor=Bimodal())
_a.run()
_b = Core(_words, _data, forwarding=True, predictor=Bimodal())
_b.run()
assert _a.stats()["retired"] == 44 and _a.stats()["cycles"] == 62, \
    f"this run should retire 44 instructions in 62 cycles, got {_a.stats()}"
assert _a.stats() == _b.stats(), \
    f"two identical runs must report identical statistics: {_a.stats()} vs {_b.stats()}"
assert _a.dmem == _b.dmem and _a.dmem.get(64) == 55, \
    "and identical memory, with the total still stored at address 64"
'''},
        ],
    },
}
