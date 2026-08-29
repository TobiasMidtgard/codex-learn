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
    "stack": ["Python", "Verilog"],
    "credits": 10,
    "hours": 130,
    "icon": "▣",
    "summary": (
        "RV32I has one instruction length, one register file and forty-odd opcodes, "
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
                        "placeholder": "t_{if} + t_{id} + t_{ex} + t_{me} + t_{wb} + t_{reg}",
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
                        "placeholder": "810",
                        "hint": "Add the five delays, then add the register overhead once.",
                        "deconstruct": [
                            "$180 + 120 + 200 + 190 + 90 = 780$.",
                            "Plus $t_{reg} = 30$ gives 810 ps.",
                        ],
                    },
                    {
                        "prompt": "Now cut the path with four pipeline registers. Every stage is bounded by registers, so the period is the slowest stage plus one $t_{reg}$. What is it, in picoseconds?",
                        "answer": "230",
                        "placeholder": "230",
                        "hint": "The slowest of the five delays is EX at 200 ps.",
                        "deconstruct": [
                            "The clock must satisfy every stage, so it is set by the largest, $t_{ex} = 200$.",
                            "Each stage still writes a register: $200 + 30 = 230$ ps.",
                        ],
                    },
                    {
                        "prompt": "On a long stream of instructions with no hazards, the pipelined machine retires one instruction per cycle. Write its speedup over the single-cycle machine.",
                        "answer": "\\frac{810}{230}",
                        "placeholder": "\\frac{810}{230}",
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
                        "placeholder": "\\frac{k \\cdot t_{stage} + t_{reg}}{t_{stage} + t_{reg}}",
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
                    "Rows i1, i2 and i3 each start two cycles later than the row above, while i4 downwards keep the one-cycle spacing — only the first `dep` instructions are made dependent, and each dependence costs exactly two cycles.",
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
                        "placeholder": "N + k - 1",
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
                        "placeholder": "\\frac{N + k - 1}{N}",
                        "hint": "CPI is cycles divided by instructions retired.",
                        "deconstruct": [
                            "Divide the cycle count by $N$.",
                            "For $k=5$ and $N=1000$ that is 1.004 — the fill cost is real but it is not what makes CPI bad.",
                        ],
                    },
                    {
                        "prompt": "A producer enters IF in cycle $c$. In which cycle is it in WB, writing the register file?",
                        "answer": "c + 4",
                        "placeholder": "c + 4",
                        "hint": "IF is stage 0 and WB is stage 4, one cycle each.",
                        "deconstruct": [
                            "The stages are IF, ID, EX, MEM, WB at cycles $c$, $c+1$, $c+2$, $c+3$, $c+4$.",
                        ],
                    },
                    {
                        "prompt": "A consumer of that register must have its ID no earlier than cycle $c+4$. ID is one cycle after IF, so write the earliest cycle the consumer may enter IF.",
                        "answer": "c + 3",
                        "placeholder": "c + 3",
                        "hint": "If ID must be at $c+4$ and ID is IF plus one, then IF is at $c+4-1$.",
                        "deconstruct": [
                            "The write happens in the first half of $c+4$ and the read in the second half of the same cycle, so ID at $c+4$ is legal.",
                            "IF is one cycle earlier: $c + 3$.",
                        ],
                    },
                    {
                        "prompt": "The instruction immediately behind the producer would otherwise have entered IF in cycle $c+1$. How many bubbles does the stall insert?",
                        "answer": "2",
                        "placeholder": "2",
                        "hint": "Subtract the natural issue cycle from the earliest legal one.",
                        "deconstruct": [
                            "Earliest legal IF is $c+3$; the natural one is $c+1$.",
                            "$(c+3) - (c+1) = 2$ cycles of nothing.",
                        ],
                    },
                    {
                        "prompt": "Let $f_1$ be the fraction of instructions whose nearest producer is one instruction ahead, and $f_2$ the fraction whose nearest producer is two ahead (worth one bubble). Write the CPI, ignoring the fill cost.",
                        "answer": "1 + 2 \\cdot f_1 + f_2",
                        "placeholder": "1 + 2 \\cdot f_1 + f_2",
                        "hint": "Start from one cycle per instruction and add the average number of bubbles per instruction.",
                        "deconstruct": [
                            "Every instruction costs one cycle to begin with.",
                            "A fraction $f_1$ of them adds two, and a fraction $f_2$ adds one.",
                        ],
                    },
                    {
                        "prompt": "Measurements on a compiled kernel give $f_1 = 0.30$ and $f_2 = 0.15$. What is the CPI?",
                        "answer": "1.75",
                        "placeholder": "1.75",
                        "hint": "Substitute into the expression you just wrote.",
                        "deconstruct": [
                            "$2 \\times 0.30 = 0.60$ and $f_2 = 0.15$.",
                            "$1 + 0.60 + 0.15 = 1.75$ — the machine is doing well under 60% of its peak.",
                        ],
                    },
                ],
                "closing": r'''
A CPI of 1.75 on a machine whose peak is 1.0 is not a rounding error; it is 43%
of the throughput thrown away on nothing but register dependences, which every
compiled program is full of. The next module removes almost all of it with about
two hundred gates.
''',
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
                    "`if r and r in writer` does two jobs at once: it skips `None` and it skips `x0`, which is register 0 and therefore falsy.",
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
    f"six instructions, four dependences, 18 cycles against an ideal 10: got {cycles(_p)}"
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
                        "placeholder": "c + r",
                        "hint": "It entered IF (stage 0) in cycle $c$ and advances one stage per cycle.",
                        "deconstruct": [
                            "Stage 0 is cycle $c$, stage 1 is cycle $c+1$, and so on.",
                            "So stage $r$ is cycle $c + r$, and the result exists at the end of it.",
                        ],
                    },
                    {
                        "prompt": "In which cycle does the consumer need the operand — that is, which cycle is its stage $u$?",
                        "answer": "c + d + u",
                        "placeholder": "c + d + u",
                        "hint": "The consumer entered IF in cycle $c + d$; apply the same counting.",
                        "deconstruct": [
                            "Its stage 0 is cycle $c + d$.",
                            "Its stage $u$ is $u$ cycles later.",
                        ],
                    },
                    {
                        "prompt": "The value is available to any stage that *starts* after the producer's stage $r$ has finished, so the no-stall condition is $c + d + u \\ge c + r + 1$. Solve it for the smallest distance $d$ that needs no stall.",
                        "answer": "r + 1 - u",
                        "placeholder": "r + 1 - u",
                        "hint": "Cancel $c$ from both sides and rearrange for $d$.",
                        "deconstruct": [
                            "$c + d + u \\ge c + r + 1$ gives $d + u \\ge r + 1$.",
                            "So $d \\ge r + 1 - u$.",
                        ],
                    },
                    {
                        "prompt": "An ALU instruction is ready at the end of EX and another ALU instruction needs its operands at the start of EX. Substitute $r = 2$, $u = 2$ and write the minimum distance.",
                        "answer": "1",
                        "placeholder": "1",
                        "hint": "$r + 1 - u$ with both stages equal to 2.",
                        "deconstruct": [
                            "$2 + 1 - 2 = 1$.",
                            "A distance of one is back-to-back, so an EX-to-EX forward removes the hazard entirely.",
                        ],
                    },
                    {
                        "prompt": "A load is ready only at the end of MEM. With $r = 3$ and a consumer needing it in EX ($u = 2$), what is the minimum distance now?",
                        "answer": "2",
                        "placeholder": "2",
                        "hint": "Same expression, one stage later.",
                        "deconstruct": [
                            "$3 + 1 - 2 = 2$.",
                            "Distance two means one instruction must sit between the load and its use — either useful work, or a bubble.",
                        ],
                    },
                    {
                        "prompt": "Now let the consumer be a store using the loaded value as the data it writes, needed at the start of MEM ($u = 3$). What is the minimum distance?",
                        "answer": "1",
                        "placeholder": "1",
                        "hint": "$r = 3$, $u = 3$.",
                        "deconstruct": [
                            "$3 + 1 - 3 = 1$: back-to-back is fine.",
                            "A load feeding a store's data operand needs a MEM-to-MEM path and costs nothing — a memory copy runs at full rate.",
                        ],
                    },
                    {
                        "prompt": "With full forwarding the only stalls left are load-use pairs, a fraction $f_{lu}$ of all instructions, one bubble each. Write the CPI.",
                        "answer": "1 + f_{lu}",
                        "placeholder": "1 + f_{lu}",
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
                    "Set dependent pairs to 6 while leaving forwarding on: still CPI 1.89, and every cycle above 1.0 is a control hazard. That number is the entire budget a branch predictor has to work with.",
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
                        "placeholder": "1 + f_{br} \\cdot (1 - a) \\cdot c_{mis}",
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
                        "placeholder": "1.04",
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
                        "placeholder": "1.2",
                        "hint": "Only $c_{mis}$ changed, and it is a linear factor.",
                        "deconstruct": [
                            "$0.20 \\times 0.10 \\times 10 = 0.20$.",
                            "CPI $= 1.20$: the same predictor that was adequate is now costing a fifth of the machine.",
                        ],
                    },
                    {
                        "prompt": "Rearrange the CPI expression for the accuracy $a$ needed to hit a target CPI.",
                        "answer": "1 - \\frac{CPI - 1}{f_{br} \\cdot c_{mis}}",
                        "placeholder": "1 - \\frac{CPI - 1}{f_{br} \\cdot c_{mis}}",
                        "hint": "Subtract 1 from both sides, divide by $f_{br} c_{mis}$, and solve for $a$.",
                        "deconstruct": [
                            "$CPI - 1 = f_{br}(1-a)c_{mis}$.",
                            "So $1 - a = (CPI-1)/(f_{br}c_{mis})$.",
                        ],
                    },
                    {
                        "prompt": "On that deep machine, what accuracy brings the CPI back down to 1.04?",
                        "answer": "0.98",
                        "placeholder": "0.98",
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
assert _p.predict(0x100) is False or _p.predict(0x100) == False, \
    "the counters start at 1, which is weakly not taken"
for _ in range(4):
    _p.update(0x100, True)
assert _p.predict(0x100), "four takens should saturate the counter at 3"
_p.update(0x100, False)
assert _p.predict(0x100), \
    "one surprise must not change the prediction — that hysteresis is the whole point"
_p.update(0x100, False)
assert not _p.predict(0x100), "two in a row should flip it"
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
assert _m < 20, \
    ("gshare gives each history context its own counter, so it should learn the "
     "alternation in a handful of branches: got %d of 200" % _m)
assert _m > 0, "it still has to learn it; a predictor that starts perfect is not learning"
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
                    {"name": "nothing predicts noise", "code": r'''
import traces
_learnable = traces.loop_trace(trips=30, body=12)
_noise = traces.pseudo_random(400, percent_taken=70, seed=12345)
_good = evaluate(Bimodal(), _learnable) / len(_learnable)
_bad = evaluate(Bimodal(), _noise) / len(_noise)
assert _good < 0.12, f"the same predictor handles the loop well, got {_good:.3f} wrong"
assert _bad > 0.25, \
    ("and cannot do better than the bias on an unpredictable stream: got %.3f" % _bad)
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

A register file of 32 words with `x0` hard-wired to zero, a word-addressed data
memory as a dict, and a program counter. `execute(ins)` applies one instruction
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
# Forwarding is worth 31 cycles here and the predictor 14, and the two are
# almost independent: they remove different cycles.


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
