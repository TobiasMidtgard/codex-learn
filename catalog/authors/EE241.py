"""EE241 — Embedded C and Microcontrollers.

Second year. It assumes EE121 (Boolean algebra, gates, binary) and EE131 (Python:
functions, loops, lists, dicts), plus the Year 1 circuit courses for the five build
exercises. It assumes nothing about C, nothing about processors, and nothing about
converters.

Authoring rules, as for every course module:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only; this course uses neither beyond `math`
  * every expected number was produced by running the code, not assumed
  * sandbox notices were written against the visualiser source in src/studio.js
  * build checks are JavaScript against the circuit API, and they measure what the
    circuit does rather than compare it to the reference drawing
"""

COURSE = {
    "id": "EE241",
    "title": "Embedded C and Microcontrollers",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE121", "EE131"],
    "stack": ["Python", "C (reference)"],
    "credits": 10,
    "hours": 130,
    "icon": "▣",
    "summary": (
        "A microcontroller is a processor with the peripherals wired to it on the same "
        "die, and every one of those peripherals is controlled by writing bits into an "
        "address. This course is about that address: what a memory-mapped register is, "
        "how to change three bits of one without disturbing the other twenty-nine, and "
        "what happens when an interrupt lands halfway through. Around that sits the "
        "hardware a pin actually drives, the timer that generates PWM, the converter "
        "that turns a voltage into an integer, and the arithmetic you are left with on "
        "a machine that has no floating-point unit at all."
    ),
    "outcomes": [
        "Set, clear, toggle and read a named bit field of a 32-bit peripheral register without disturbing the rest of it.",
        "Explain what `volatile` tells a C compiler, and identify the two situations in which omitting it produces code that is wrong rather than merely slow.",
        "Size the external components a GPIO pin needs to drive an indicator or read a switch, within the pin's stated current and voltage limits.",
        "Choose between polling and an interrupt for a given deadline, and state the worst-case latency each one delivers.",
        "Configure a timer's prescaler, period and compare value to produce a required PWM frequency and duty cycle, and filter that output into an analogue voltage.",
        "Convert between volts, ADC codes and fixed-point integers, and predict the quantisation error, the dead band and the overflow points of an integer-only signal chain.",
        "Read a peripheral's register map as a C struct, and predict the address, the access width and the padding of any field in it — along with what integer promotion does to the expression that reads it.",
        "Work a clock from the crystal through the PLL and the bus prescalers to the peripheral, and say which settings have to be in place before the clock is raised.",
        "Design the small amount of hardware a pin needs that no software can replace: a transistor switch and its flyback diode, an RC that turns one press into one interrupt, a divider that survives its own capacitance, an I²C pull-up that meets both the rise time and the sink current.",
        "Bound the worst-case delay before an interrupt handler starts, and write a critical section that does not lengthen that bound for every other interrupt in the system.",
        "Compute a UART's baud divider and the sampling error it accumulates across a frame, and say which of framing, parity and overrun a given failure would report.",
    ],
    "assessment": (
        "Ten quizzes, five circuits drawn and measured in the schematic editor, three "
        "guided derivations, a symbol drill, a filter tuned against three constraints "
        "at once, two listings to complete, two numeric answers, one of them checked "
        "against the solver, five Python labs checked by execution, and a capstone that drives a "
        "simulated memory-mapped peripheral through a complete integer-only "
        "measurement chain."
    ),
    "reading": [
        "*The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors*, Joseph Yiu — chapters 4 and 7.",
        "*Making Embedded Systems*, Elecia White — for the working habits rather than the syntax.",
        "Any vendor reference manual, at the GPIO and ADC chapters. Reading one is the actual skill this course teaches.",
        "*Embedded Systems: Introduction to Arm Cortex-M Microcontrollers*, Valvano — for the fixed-point chapter.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Registers, bit fields and the word volatile",
            "summary": "A peripheral is a set of numbered boxes in the address space. Everything else in this course is a consequence of that.",
            "concepts": [
                "A peripheral register is a fixed address that behaves like a variable to the processor and like a control panel to the hardware. Writing 1 to bit 5 of address 0x40020014 does store that bit, and you can read it back — but storing it is not the point of the write. Raising a pin is.",
                "In C the address is given a type and dereferenced: `*(volatile uint32_t *)0x40020014 = value;`. The cast says how wide the access is, and a 32-bit register must be written 32 bits at a time.",
                "The four operations on a bit field are `|=` to set, `&= ~` to clear, `^=` to toggle and `&` to test. Learn them as four idioms rather than four puzzles.",
                "Each of those is a **read-modify-write**: the processor fetches the whole word, changes some bits, and writes the whole word back. Anything that alters the register between the read and the write is lost.",
                "A multi-bit field is extracted with a shift then a mask, `(word >> shift) & ((1 << width) - 1)`, and inserted by clearing the field first and then OR-ing the new value in. Skipping the clear leaves the old bits underneath.",
                "`volatile` tells the compiler that this address may change without the program changing it, and that reads and writes of it are effects that must not be removed, reordered or merged. Without it, `while (*STATUS & READY);` can be compiled into a single read and an infinite loop.",
                "Some status bits are **write-1-to-clear**: writing a 1 clears the flag and writing a 0 leaves it alone. For those registers the read-modify-write idiom is actively wrong — it clears every flag that happened to be set.",
                "Reserved bits are reserved because the vendor may use them later. Read-modify-write preserves them; writing a whole constant word does not.",
            ],
            "read": [
                {
                    "title": "One address, thirty-two switches",
                    "minutes": 14,
                    "body": r'''
Put a debugger on a running board and open a memory window at address `0x40020014`. One
32-bit word sits there:

```text
40020014   0x00000085
```

Type `0x000000A5` over it and press enter. An LED wired to pin 5 of that port lights.

No line of your program ran. Nothing was called, nothing was scheduled, no driver was
involved. A number in a window changed and a piece of the physical world changed with
it, and that single observation is what the rest of this course is built on.

## The address is a doorway, not a box

`0x40020014` looks like memory and behaves like memory to the load-store instructions
that reach it. It is not memory. Behind it sits the output stage of a GPIO port, and the
32 bits of that word are wired to 32 pins. Writing the word does store it — read it back
and you get `0xA5` — but storing it is a side effect. Raising a pin is the point.

Everything that follows from that is worth stating once. The width of the access is part
of the specification, because the hardware decodes a 32-bit bus transaction and not a
byte one. The value you read back may not be the value you wrote, because some bits are
driven by the hardware rather than by you. And the *order* of your accesses is
observable, in a way that the order of writes to two ordinary variables is not.

## What actually changed between 0x85 and 0xA5

Write the two words in binary, one under the other:

```text
0x85   0000 0000 0000 0000 0000 0000 1000 0101
0xA5   0000 0000 0000 0000 0000 0000 1010 0101
                                       ^
```

One bit moved: number 5, counting from zero at the right-hand end. Pins 0, 2 and 7 were
already high before the edit and were still high after it. That is the requirement a
driver has to meet on every write it ever makes — move some switches, leave the other
thirty-odd exactly where they were — and the four idioms everybody memorises fall out of
three truth tables rather than needing to be memorised at all.

Take one bit `x` and one mask bit, and ask what each operator leaves behind.

`x | 0` is `x`, and `x | 1` is 1. So OR-ing with a mask forces every masked bit to 1 and
leaves every unmasked bit untouched. That is **set**, and it is why `reg |= mask` is
written the way it is.

`x & 1` is `x`, and `x & 0` is 0. AND has the same shape running the other way: it
preserves where the mask holds a 1 and forces 0 where the mask holds a 0. So to clear the
bits you have named, the mask has to be inverted first, which is where the second `~`
in `reg &= ~mask` comes from. It is not decoration and it is not a style choice.

`x ^ 0` is `x`, and `x ^ 1` is the opposite of `x`. XOR inverts exactly the masked bits,
which is **toggle**.

And `word & mask` keeps the masked bits and zeroes everything else, which is how you
**test**. Compare the result against `mask` to ask whether all of them are set, and
against zero to ask whether any of them are. Those are different questions with different
answers, and confusing them is the defect the `all_set` test in this module's lab exists
to catch.

## A field is a small number living inside a big one

Bits are the easy case. Most configuration is not one bit per setting but two, three or
four, and then you have a *field*: a run of adjacent bits holding a small integer.

The GPIO mode register `MODER` holds two bits per pin, so pin 5's mode lives in bits 11
and 10. Reading it is a shift and a mask — bring the field down to the bottom, then
discard everything above it:

$$\text{field} = (\text{word} \gg \text{shift}) \;\&\; (2^{\text{width}} - 1)$$

Writing it is where people come unstuck. Suppose `MODER` currently reads `0xA8000800`.
The field for pin 5 is `(0xA8000800 >> 10) & 0b11`, which is `0b10` — analogue mode on
this part. You want `0b01`, a plain output.

```python
MODER = 0xA8000800
shift, width, value = 10, 2, 0b01
mask = ((1 << width) - 1) << shift

print("before         ", format(MODER, "#010x"), "field =", (MODER >> shift) & 3)
wrong = MODER | (value << shift)
print("OR alone       ", format(wrong, "#010x"), "field =", (wrong >> shift) & 3)
right = (MODER & ~mask) | ((value << shift) & mask)
print("clear then OR  ", format(right, "#010x"), "field =", (right >> shift) & 3)
```

That prints three lines. The first reports `0xa8000800` with a field of 2. The second,
the tempting one-line update, reports `0xa8000c00` with a field of **3** — OR can only
ever turn bits on, so `0b10` OR `0b01` is `0b11`, a third mode that is neither the old
one nor the new one. The third reports `0xa8000400` with a field of 1, which is what was
wanted.

So a field insert is two halves and always has been:

$$\text{word} \leftarrow (\text{word} \;\&\; \sim\!\text{mask}) \;|\; ((\text{value} \ll \text{shift}) \;\&\; \text{mask})$$

The first half makes room. The second half fills it, and the extra `& mask` on the value
trims anything too wide to fit so that an over-large value cannot spill sideways into the
neighbouring pin's field. Both halves earn their place.

## The mistake, and why it is tempting

The single most common defect in beginner embedded code is not any of the above. It is
this:

```c
ODR = 1 << 5;      /* pin 5 high */
```

The comment is honest about the intent and the code does something else. `=` writes
`0x00000020` over the entire word, so pin 5 goes high and pins 0, 2 and 7 go **low**.
It is tempting for a reason that has nothing to do with misunderstanding C: during
bring-up there is usually one LED on one pin and nothing else attached, so the line works
perfectly and gets copied into the next driver, and the next. The fault surfaces weeks
later as "the status LED goes out whenever the relay fires", which nobody connects to a
line of code that has been working since the first afternoon.

The habit that prevents it is to read every register write as a sentence about all
thirty-two bits, not about the one you were thinking of.

## Where this model stops holding

The read-modify-write picture is right about *what* the bits do and silent about *when*.
Three cases break it, and all three are real.

**It is not one operation.** `reg |= (1 << 3)` is a load, an OR and a store. An interrupt
that lands between the load and the store, and that touches the same register, has its
change overwritten when the store completes. `volatile` does not help here, and believing
it does produces a fault that appears perhaps once a day. The fixes are elsewhere: a
critical section, an atomic instruction, or a peripheral that offers separate set and
clear registers so that no read is needed at all. Module 7 takes that apart properly.

**Some registers are write-1-to-clear.** In a status register, writing a 1 to a flag
clears it and writing a 0 leaves it alone. On those, `SR &= ~OVERRUN` is actively
destructive: it reads the whole word, writes 1s back into every *other* flag that
happened to be set, and clears them too. The correct line is `SR = OVERRUN`, a plain
assignment — the very thing that was wrong two paragraphs ago. Which idiom is right is
decided by the register's documented behaviour and by nothing else.

**Some registers change when you read them.** Reading a UART data register clears the
receive flag; reading certain status registers arms a clear-on-read sequence. A
read-modify-write on one of those has already had its effect by the time you get to the
modify, and a debugger watching the address will trigger it too, which is why a bus that
works under the debugger and fails without it is worth suspecting early.

Finally, `volatile` itself. It says an access must happen, that it must happen where the
source says, and that it may not be merged with another. Without it, `while (!(*STATUS &
READY)) { }` compiles into a single read and an infinite loop, because the compiler can
see that nothing in the loop body changes `*STATUS`. That is a correctness failure rather
than a slow one, and it appears only once optimisation is switched on. What `volatile`
does not give you is atomicity, ordering against non-volatile accesses, or any statement
about caches. It is a smaller promise than its reputation.

## What you are about to build

The lab for this module, **The six operations on a bit field**, asks for those six
functions in Python: `set_bits`, `clear_bits`, `toggle_bits`, `all_set`, `read_field`
and `write_field`. Python integers do not overflow, so each one masks its result with
`0xFFFFFFFF` — work a real 32-bit register does for you by being 32 bits wide.

`write_field` is the one to think about, and the tests are pointed at exactly the two
failures above: a field that was not cleared before the new value went in, and an
over-wide value that spilled into its neighbour. Get those six right and every driver in
the remaining nine modules is the same expressions with semicolons after them.
''',
                },
            ],
            "quiz": {
                "title": "What a write to a register actually does",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A 32-bit register at `ODR` currently holds `0x00000085`, so pins 0, 2 and 7 are high and pin 5 is low. You want pin 5 high, leaving every other pin exactly as it was. Which line does that?",
                        "opts": [
                            "`ODR = 1 << 5;`",
                            "`ODR &= ~(1 << 5);`",
                            "`ODR |= (1 << 5);`",
                            "`ODR = 5;`",
                        ],
                        "a": 2,
                        "why": r'''
`|=` sets the named bit and leaves the other 31 untouched, taking `0x85` to `0xA5`,
which is what "leaving every other pin as it was" demands. The tempting answer is
`ODR = 1 << 5;`, and it is the single most common beginner defect in embedded code: it
writes `0x00000020` over the whole word, so pin 5 goes high and **pins 0, 2 and 7 go
low**. It will often appear to work, because during bring-up only one pin is in use.
The `&= ~(1 << 5)` line clears bit 5, which was already clear, so nothing happens at
all; `ODR = 5;` writes `0x00000005`, setting bits 0 and 2 and clearing everything else, because 5 is
`0b101` rather than a pin number.
''',
                    },
                    {
                        "q": "`MODER` holds two bits per pin, so pin 5's mode lives in bits 11 and 10. You want to write the mode `0b01` there without disturbing any other pin. What must happen first?",
                        "opts": [
                            "bits 11 and 10 must be cleared, before the new value is OR-ed in",
                            "the whole register must be set to zero",
                            "nothing — OR-ing `0b01 << 10` is enough on its own",
                            "the register must be read twice, to be sure of the value",
                        ],
                        "a": 0,
                        "why": r'''
Clear the field, then OR. `MODER |= (0b01 << 10)` on its own can only ever turn bits
*on*, so a field that already held `0b10` becomes `0b11` — a different mode entirely,
and one that is often analogue. That is the whole reason a field insert is written
`reg = (reg & ~mask) | ((value << shift) & mask)`: the first half makes room, the
second half fills it. Zeroing the whole register would work for pin 5 and destroy
every other pin's configuration.
''',
                    },
                    {
                        "q": "A status register's `OVERRUN` flag is documented as write-1-to-clear. Which line clears just that flag?",
                        "opts": [
                            "`SR &= ~OVERRUN;`",
                            "`SR |= OVERRUN;`",
                            "`SR = 0;`",
                            "`SR = OVERRUN;`",
                        ],
                        "a": 3,
                        "why": r'''
`SR = OVERRUN;` writes a 1 in that one bit position and a 0 everywhere else — and in a
write-1-to-clear register a 0 means "leave alone", so exactly one flag is cleared.
The trap is `SR &= ~OVERRUN;`, which is the correct idiom for an ordinary register and
here reads the whole word, writes 1s back into every *other* flag that happened to be
set, and so silently clears them too. This is why you cannot learn one idiom and apply
it everywhere: the register's documented behaviour decides which idiom is right.
''',
                    },
                    {
                        "q": "A C loop `while (!(*STATUS & READY)) { }` compiles, runs, and never exits, although a debugger shows READY is set. `STATUS` is declared `uint32_t *`. What is wrong?",
                        "opts": [
                            "the mask should be `|` rather than `&`",
                            "`STATUS` is not declared `volatile`, so the compiler read it once and kept the value in a register",
                            "the loop body is empty, which is undefined behaviour",
                            "the processor caches peripheral addresses and needs a cache flush",
                        ],
                        "a": 1,
                        "why": r'''
Without `volatile` the compiler is entitled to assume that nothing changes an object
the program does not write to. It reads `*STATUS` once, notices the loop body cannot
change it, and hoists the read out — leaving either an infinite loop or no loop at
all, depending on the first value read. Declaring it `volatile uint32_t *` forbids
that: every evaluation of `*STATUS` in the source must become an access in the object
code. Note that this is a *correctness* bug, not a performance one, and that it
appears only once optimisation is switched on, which is why it is usually discovered
the week before a deadline.
''',
                    },
                    {
                        "q": "`volatile` is often described as making an access atomic. What does it actually guarantee about `reg |= (1 << 3);`?",
                        "opts": [
                            "the read, the OR and the write happen as one uninterruptible operation",
                            "the compiler will use a single-instruction bit-set if the processor has one",
                            "nothing about atomicity — the read and the write are separate accesses and an interrupt can land between them",
                            "that no other core can access the register at the same time",
                        ],
                        "a": 2,
                        "why": r'''
`volatile` is a statement about *when* accesses happen, not about how many of them can
be grouped together. `reg |= (1 << 3)` is still a load, an OR and a store, and an
interrupt that lands between the load and the store, and which modifies the same
register, has its change overwritten when the store completes. Fixing that needs
something else: disabling interrupts around the sequence, a hardware atomic
instruction, or a peripheral that provides separate set and clear registers so no
read is needed at all. Believing `volatile` handles it produces a bug that appears
perhaps once a day and is nearly impossible to reproduce.
''',
                    },
                    {
                        "q": "A vendor manual shows bits 20 to 31 of a control register as \"Reserved. Must be kept at reset value.\" Which style of update respects that?",
                        "opts": [
                            "read-modify-write, because it writes back whatever those bits already held",
                            "writing the whole word from a constant, because the constant has zeros there",
                            "either, since reserved bits are ignored by the hardware",
                            "neither — reserved bits require a special unlock sequence",
                        ],
                        "a": 0,
                        "why": r'''
Read-modify-write carries the reserved bits across untouched, which is exactly what
"must be kept at reset value" asks for. Writing a whole constant word forces them to
whatever the constant says, usually zero, which may or may not be their reset value —
and on the next silicon revision, when the vendor gives one of those bits a meaning,
the code changes behaviour without being edited. "Either, since reserved bits are ignored by the hardware" is the assumption that
makes this bug: reserved does not mean ignored, it means undefined, and undefined includes
"used by a chip you have not bought yet".
''',
                    },
                ],
            },
            "lab": {
                "title": "The six operations on a bit field",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
Every register access in the rest of this course is one of six operations. Write them
once, in Python, where you can see the results, and the C versions afterwards are the
same expressions with semicolons.

A register here is a plain Python integer holding a 32-bit word. Python integers do
not overflow, so every function must mask its result with `0xFFFFFFFF` to keep it
inside 32 bits — a real register does that for you by being 32 bits wide.

- `set_bits(word, mask)` — return `word` with every bit of `mask` set.
- `clear_bits(word, mask)` — return `word` with every bit of `mask` cleared.
- `toggle_bits(word, mask)` — return `word` with every bit of `mask` inverted.
- `all_set(word, mask)` — `True` when **every** bit of `mask` is set in `word`.
- `read_field(word, shift, width)` — the `width`-bit field starting at bit `shift`,
  returned as a small integer in its own right.
- `write_field(word, shift, width, value)` — `word` with that field replaced by
  `value`. Anything in `value` above `width` bits is discarded rather than allowed to
  spill into the neighbouring field.

`write_field` is the one worth thinking about. Build the field mask first,
`((1 << width) - 1) << shift`, use it to clear the old contents, and use it again to
trim the new value before OR-ing it in.

Note the difference between `all_set` and a bare `word & mask`. A test for a single
bit is the same either way; a test for two bits is not, and `(word & mask) != 0` is
true when *either* is set.
''',
                "files": [{"name": "main.py", "content": r'''
"""Bit fields, as the six operations every driver is built from."""

WORD = 0xFFFFFFFF  # a 32-bit register wraps; a Python integer does not


def set_bits(word, mask):
    """`word` with every bit of `mask` set."""
    # TODO: OR the mask in, then keep 32 bits.
    return 0


def clear_bits(word, mask):
    """`word` with every bit of `mask` cleared."""
    # TODO: AND with the inverted mask, then keep 32 bits.
    return 0


def toggle_bits(word, mask):
    """`word` with every bit of `mask` inverted."""
    # TODO: exclusive-OR flips exactly the bits of the mask.
    return 0


def all_set(word, mask):
    """True when every bit of `mask` is set in `word`."""
    # TODO: compare the masked word with the mask itself.
    return False


def read_field(word, shift, width):
    """The `width`-bit field starting at bit `shift`, as a small integer."""
    # TODO: shift the field down, then mask off everything above it.
    return 0


def write_field(word, shift, width, value):
    """`word` with that field replaced by `value`, trimmed to `width` bits."""
    # TODO: clear the field, then OR in the trimmed value.
    return 0


if __name__ == "__main__":
    odr = 0x000000A5
    print("pin 5 high:", hex(set_bits(odr, 1 << 5)))
    print("pin 0 low: ", hex(clear_bits(odr, 1 << 0)))
    moder = 0xFFFFFFFF
    print("pin 5 mode 01:", hex(write_field(moder, 10, 2, 0b01)))
    print("reads back as:", read_field(write_field(moder, 10, 2, 0b01), 10, 2))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Bit fields, as the six operations every driver is built from."""

WORD = 0xFFFFFFFF  # a 32-bit register wraps; a Python integer does not


def set_bits(word, mask):
    """`word` with every bit of `mask` set."""
    return (word | mask) & WORD


def clear_bits(word, mask):
    """`word` with every bit of `mask` cleared."""
    return (word & ~mask) & WORD


def toggle_bits(word, mask):
    """`word` with every bit of `mask` inverted."""
    return (word ^ mask) & WORD


def all_set(word, mask):
    """True when every bit of `mask` is set in `word`."""
    return (word & mask) == mask


def read_field(word, shift, width):
    """The `width`-bit field starting at bit `shift`, as a small integer."""
    return (word >> shift) & ((1 << width) - 1)


def write_field(word, shift, width, value):
    """`word` with that field replaced by `value`, trimmed to `width` bits."""
    mask = ((1 << width) - 1) << shift
    return ((word & ~mask) | ((value << shift) & mask)) & WORD


if __name__ == "__main__":
    odr = 0x000000A5
    print("pin 5 high:", hex(set_bits(odr, 1 << 5)))
    print("pin 0 low: ", hex(clear_bits(odr, 1 << 0)))
    moder = 0xFFFFFFFF
    print("pin 5 mode 01:", hex(write_field(moder, 10, 2, 0b01)))
    print("reads back as:", read_field(write_field(moder, 10, 2, 0b01), 10, 2))
'''}],
                "hints": [
                    "`set_bits` is `(word | mask) & WORD`. The mask at the end matters only because Python integers are unbounded; in C the type does it.",
                    "`~mask` in Python is negative, which looks alarming and is harmless: `word & ~mask` still clears the right bits, and the final `& WORD` brings the result back into range.",
                    "`all_set` must compare `word & mask` with `mask`, not with zero. `(word & mask) != 0` answers 'any of them', which is a different question.",
                    "In `write_field`, build `mask = ((1 << width) - 1) << shift` once and use it twice: `word & ~mask` empties the field, and `(value << shift) & mask` trims the new value so an over-wide value cannot reach the next field along.",
                ],
                "tests": [
                    {"name": "setting a bit leaves the others alone", "code": r'''
got = set_bits(0x0000000F, 1 << 5)
assert got == 0x2F, f"0x0F with bit 5 set is 0x2F, got {hex(got)}"
assert set_bits(0x2F, 1 << 5) == 0x2F, "setting a bit that is already set changes nothing"
'''},
                    {"name": "clearing the top bit stays inside 32 bits", "code": r'''
got = clear_bits(0xFFFFFFFF, 1 << 31)
assert got == 0x7FFFFFFF, f"expected 0x7FFFFFFF, got {hex(got)}"
assert got >= 0, "the result must be a positive 32-bit word, not a negative Python int"
'''},
                    {"name": "toggling twice returns the original word", "code": r'''
once = toggle_bits(0xA5A5A5A5, 0xFFFF)
assert once == 0xA5A55A5A, f"expected 0xA5A55A5A, got {hex(once)}"
twice = toggle_bits(once, 0xFFFF)
assert twice == 0xA5A5A5A5, f"toggling twice should undo itself, got {hex(twice)}"
'''},
                    {"name": "all_set means every bit, not any bit", "code": r'''
assert all_set(0b1011, 0b1010), "0b1011 does contain both bits of 0b1010"
assert not all_set(0b1001, 0b1010), \
    "0b1001 has only one of the two bits, so all_set must be False"
assert not all_set(0, 1 << 7), "no bits set at all"
'''},
                    {"name": "a field comes back as a small integer", "code": r'''
got = read_field(0xDEADBEEF, 8, 8)
assert got == 0xBE, f"bits 15..8 of 0xDEADBEEF are 0xBE, got {hex(got)}"
assert read_field(0xDEADBEEF, 0, 4) == 0xF, "the bottom nibble is 0xF"
assert read_field(0xFFFFFFFF, 10, 2) == 0b11, "a two-bit field maxes out at 3"
'''},
                    {"name": "writing a field clears it first", "code": r'''
got = write_field(0x00000000, 10, 2, 0b01)
assert got == 0x400, f"0b01 at bit 10 is 0x400, got {hex(got)}"
got = write_field(0xFFFFFFFF, 10, 2, 0b01)
assert got == 0xFFFFF7FF, \
    f"the field must be cleared before the new value goes in, got {hex(got)}"
assert read_field(got, 12, 2) == 0b11, "the neighbouring field must be untouched"
'''},
                    {"name": "an over-wide value is trimmed, not spilled", "code": r'''
got = write_field(0x00000000, 4, 4, 0x3F)
assert got == 0xF0, \
    f"0x3F does not fit in four bits; only its low nibble may land, got {hex(got)}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Types, pointers and the map of the address space",
            "summary": "You have written `*(volatile uint32_t *)0x40020014`. This module is the rest of that line: what the type does, what the number points at, and what the compiler does with both.",
            "concepts": [
                "C's built-in integer types have no fixed width — `int` is whatever the machine calls natural, and on a small microcontroller that is 32 bits while on the compiler you tested with it may not be. `<stdint.h>` gives the ones that are fixed: `uint8_t`, `int16_t`, `uint32_t`. A register access must be exactly as wide as the register, so here the type is part of the hardware specification and not a matter of taste.",
                "Anything narrower than `int` is promoted to `int` before arithmetic, keeping its value. So for two `uint8_t` variables holding 200 and 100, `a + b` is 300 — the truncation to 44 happens on the way back into an 8-bit variable, not during the addition. And when signed meets unsigned of the same rank the signed side converts, which is why `-1 < 1u` is false and why a loop counter that is `unsigned` and counts down past zero never ends.",
                "A pointer's type says how wide the object it points at is, and pointer arithmetic counts objects rather than bytes: adding 5 to a `uint32_t *` moves the address on by 20. Casting a pointer changes the arithmetic and the access width; it does not change the address, and it does not change what the hardware has at that address.",
                "A peripheral is a run of consecutive registers, so a `struct` of `volatile uint32_t` members laid over the base address names them: `GPIOA->ODR` compiles to exactly the same load-store as `*(volatile uint32_t *)(0x40020000 + 0x14)`. The members must appear in the manual's order, with an explicit reserved member wherever the manual leaves a gap, or every register after the gap is off by four.",
                "The address space is a map, not a memory. Flash holds the code and anything `const`; SRAM holds the writable globals — `.data`, whose initial values are copied out of flash before `main` runs, and `.bss`, which the startup code zeroes — and the stack, which grows down from the top of SRAM towards them. Peripheral registers are a third region that is not memory at all. Nothing in C stops you forming a pointer into a region where writes do nothing, or where they fault.",
            ],
            "read": [
                {
                    "title": "The rest of that line: what a type knows that an address does not",
                    "minutes": 15,
                    "body": r'''
Put a bus analyser between the core and the peripheral bus, run two lines of C that
differ by four characters, and capture what comes out. The port's output register starts
at `0x0000A585`, so pins 0, 2, 7, 8, 10, 13 and 15 are high.

```text
 #   address       width    data on the bus     ODR afterwards
 1   0x40020014   32-bit   0x000000AA           0x000000AA
 2   0x40020014    8-bit   0xAA                 0x0000A5AA
```

Line 1 was `*(volatile uint32_t *)0x40020014 = 0xAA;` and line 2 was
`*(volatile uint8_t *)0x40020014 = 0xAA;`. Same address, same value, same syntax. One of
them turned off seven pins on the upper half of the port and the other left them alone.

The address did not decide that. The type did.

## A pointer type carries two facts

Strip a pointer down and it is a number. What the type adds is two pieces of information
the number cannot hold, and both of them reach the hardware.

The first is the **width of the access**. A `uint32_t *` produces a 32-bit bus
transaction; a `uint8_t *` produces an 8-bit one. That is line 1 against line 2 above.
It also runs the other way: many peripherals are documented as requiring a 32-bit
access and behave unpredictably, or fault, when a byte write reaches them. So the cast
in `*(volatile uint32_t *)0x40020014` is load-bearing. It is not there to quiet the
compiler.

The second is the **stride of the arithmetic**. `p + n` in C means "n objects further
on", so the byte address it produces is

$$\text{byte address} = p + n \cdot \text{sizeof}(*p)$$

Take the base of the GPIO block and step five `uint32_t` along it:

```text
(uint32_t *)0x40020000 + 5   ->   0x40020000 + 5*4   ->   0x40020014
```

That is the address from the previous module. The constant you were handed was a base
plus an offset all along, and `0x14` is 20 bytes, which is the sixth register of the
block counting from zero. The same arithmetic on a `uint8_t *` gives `0x40020005`, which
is inside a register rather than at one. This is why a cast on a pointer is a change of
meaning rather than a change of notation.

## A run of registers is a struct

A peripheral is a set of consecutive registers, so a struct of `volatile uint32_t`
members laid over the base address names them, and `GPIOA->ODR` compiles to exactly the
load-store you would have written by hand. The compiler adds the member's offset to the
base and does nothing else — `GPIOA` is not a variable holding a struct, it is a number.

Offsets come from one rule applied left to right: each member starts at the next address
that is a multiple of its own size, padding is inserted wherever that forces a gap, and
the whole structure is rounded up to a multiple of its widest member so that an array of
them stays aligned. Write the rule out and it computes both halves of this module's
fill-in drill:

```python
def layout(members):
    off = 0
    widest = 1
    for name, size in members:
        widest = max(widest, size)
        pad = (-off) % size
        off += pad
        note = f"   ({pad} bytes of padding before it)" if pad else ""
        print(f"  {name:<8} offset {off:>3} = 0x{off:02X}{note}")
        off += size
    tail = (-off) % widest
    print(f"  sizeof = {off + tail} bytes")

print("GPIO_TypeDef:")
layout([("MODER", 4), ("OTYPER", 4), ("OSPEEDR", 4),
        ("PUPDR", 4), ("IDR", 4), ("ODR", 4)])
print("a word, a byte and another word:")
layout([("a", 4), ("b", 1), ("c", 4)])
```

The first call prints offsets 0x00, 0x04, 0x08, 0x0C, 0x10 and 0x14, and a `sizeof` of
24 bytes: six members of four bytes, no padding anywhere, and `ODR` landing on the
`0x14` the bus analyser saw. The second prints `a` at 0, `b` at 4, then three bytes of
padding before `c` at offset 8, and a `sizeof` of 12 — not 9, which adds the widths and
ignores alignment, and not 16, which pads every member to a word.

The failure this predicts is worth naming. Reference manuals leave gaps: a block will
document registers at `0x00` through `0x14` and then nothing until `0x20`. If the struct
does not contain an explicit reserved member across that gap, every register after it
sits four bytes early, and the symptom is that the first few registers of a peripheral
work perfectly and the rest read as garbage. That is the shape of the bug: not "the
driver is broken" but "the driver is broken from a certain register onwards".

## The other half of the line: what C does to the integers

The type also decides what happens to the value before it ever reaches an address, and
here C has two rules that surprise people.

Anything narrower than `int` is promoted to `int` before arithmetic, keeping its value.
And when signed meets unsigned of the same rank, the *signed* operand is converted. Both
are silent. Model them and they stop being surprising:

```python
def store(value, bits, signed):
    m = value & ((1 << bits) - 1)
    if signed and m >= (1 << (bits - 1)):
        m -= 1 << bits
    return m

total8 = 0
for v in (200, 100, 50):
    total8 = store(total8 + v, 8, False)
print("uint8_t accumulator over 200,100,50 :", total8)
print("uint32_t accumulator over the same  :", sum((200, 100, 50)))
print("200 + 100 as an expression:", 200 + 100, "  stored into a uint8_t:", store(300, 8, False))
print("1 << 31 as int:", store(1 << 31, 32, True), "  as unsigned:", store(1 << 31, 32, False))
print("is -1 < 1u ?", store(-1, 32, False) < store(1, 32, False))
```

Run it and the first two lines read **94** and **350**. Follow the 8-bit accumulator by
hand: 0 + 200 is 200 and fits; 200 + 100 is 300, which does not, and lands as 44; 44 + 50
is 94. The sum is not merely inaccurate, it is 27% of the right answer, and nothing
reported anything.

The next line separates the two halves of that. `200 + 100` on its own is **300** —
both operands were promoted to `int`, where there is room to spare — and it is the
assignment back into eight bits that produces **44**. The addition and the store are
different events with different results, and a checksum that reads low is one of them
happening where you expected the other.

The last two lines print `-2147483648` against `2147483648` for the same bit pattern, and
`False` for `-1 < 1u`. That last one is the rule about signed meeting unsigned: −1
converts to 4294967295, so the comparison is false, and it compiles without a murmur
unless you have asked for `-Wsign-compare`.

## The mistake, and why it is tempting

```c
for (unsigned int i = n; i >= 0; i--) { ... }
```

This loop never ends. `i` is unsigned, so `i >= 0` cannot be false — when `i` is 0 the
decrement takes it to 4294967295 and round it goes.

It is tempting because it reads exactly like the sentence it was meant to be: count down
until you reach zero. It is also tempting because `unsigned` is the *correct* type for an
index, and choosing it feels like the careful decision. The fix is to change the test
rather than the type, usually by counting `i` down from `n` and testing `i-- > 0`, or by
indexing with `n - 1 - i` from an ordinary ascending loop.

The same instinct produces the 8-bit accumulator above: the data is bytes, so the total
feels like it should be a byte. An accumulator needs the width of the *sum*, not the
width of the samples.

## The map, and where things actually live

The address space is a map, not a memory. Flash holds the code and anything `const`;
SRAM holds `.data`, whose initial values are copied out of flash before `main` runs, and
`.bss`, which the startup code zeroes; and the stack grows down from the top of SRAM
towards them. Peripheral registers are a third region that is not memory at all.

A linker map on a part with 8 KB of SRAM says this in numbers:

```text
.text     0x08000000   0x4794      code and constants          in flash
.rodata   0x08004794    0x800      2 KB const lookup table     in flash
.data     0x20000000    0x1A8      initialised globals         in SRAM, copied from flash
.bss      0x200001A8   0x1730      zeroed globals              in SRAM
                                   -> 6248 of 8192 bytes used, 1944 left for the stack
```

Delete one keyword — the `const` on that lookup table — and the same table becomes
initialised writable data. It now costs 2 KB of SRAM *and* 2 KB of flash for the initial
values, plus the copy at startup, and SRAM goes to 8296 bytes on a part that has 8192.
One qualifier is a quarter of your memory here.

The stack is where this gets dangerous, because nothing checks it. A function that
declares `uint8_t buf[4096]` as a local on this part will write straight down past the
bottom of the stack into `.bss`. The compiler cannot warn, because it does not know how
deep the call chain will be at run time. What you get is an unrelated variable changing
value, or a return address overwritten and the chip executing nonsense, at a point in the
program that has nothing to do with the array.

## Where these models stop holding

The integer model above is a description of what compilers do, not of what the standard
promises, and the gap matters in two places. Signed overflow is *undefined behaviour*,
not wrapping: an optimiser is entitled to assume it never happens and to delete a check
written on the assumption that it does. Shifting a 1 into the sign bit of a signed 32-bit
type is undefined for the same reason, which is why a mask for bit 31 is written
`1u << 31` rather than relying on the answer the model prints.

The width assumption is the other gap. This model hard-codes a 32-bit `int` because that
is what the parts in this course have. On an 8-bit or 16-bit target `int` is 16 bits, and
then the promotion of two `uint8_t` still gives 300, but a great deal else changes.

And a pointer cast changes the arithmetic and the access width without changing the
address or what the hardware has at it. Casting a `uint8_t *` to a `uint32_t *` on an
address that is not four-byte aligned is undefined, and on some cores traps.

Finally, the map says *where* things are and nothing about what reaching them costs.
That is what this module's sandbox, **What an access pattern costs when the memory is
slower than the core**, is for: the same number of bytes touched in a different order
can cost sixteen times as many memory fetches, and the decision that sets it is how you
lay a structure out.

## What you are about to build

Two exercises follow directly from the two halves above. The fill-in drill, **The GPIO
block, from struct member to address**, walks the struct offsets to `&GPIOA->ODR` and
makes the pointer arithmetic agree with it — the `layout` output above is the same sum
done by machine. The lab, **C's integer rules, written out**, asks for `store`, `add_u8`,
`assign_u8`, `shl`, `shl_u` and `lt_mixed`, and its last test is the 8-bit accumulator
reaching 94 where a 32-bit one reaches 350.
''',
                },
            ],
            "sandbox": {
                "title": "What an access pattern costs when the memory is slower than the core",
                "visualiser": "cache",
                "minutes": 8,
                "initial": {"kb": 8, "ways": 1, "stride": 4},
                "brief": r'''
The map you have just read says where things are. It says nothing about what reaching
them costs, and on any part where the core runs faster than the flash, that cost is
decided by the *order* you touch things in rather than by how much you touch.

This is a memory walk. The horizontal axis is how much cache sits between the core and
the memory, the curve is the resulting miss rate, and the **stride** slider is the gap
in bytes between one access and the next — 4 bytes for stepping along an array of
`uint32_t`, 64 or more for reading one field out of each element of an array of
structs. A line is 64 bytes wide: a miss fetches all 64 whether you wanted one byte of
it or all of them.

Small microcontrollers have no cache at all, and the largest of them have a real one;
in between sit the prefetch buffers and flash accelerators that exist for exactly this
reason. The architecture courses take the mechanism apart. What it is doing here is
putting a number on a decision you make in C: how you lay a structure out decides how
much of each fetched line you actually use.
''',
                "notice": [
                    "It opens at 8 KB, direct-mapped, with a stride of 4 bytes — an ordinary walk along an array of 32-bit words. The marker sits at **6.25%**, which is one miss in sixteen: sixteen 4-byte words fit in a 64-byte line, so the first word of each line pays for the fifteen behind it.",
                    "Leave the stride at 4 and drag the cache size up. Nothing happens until 16 KB, then the miss rate falls steadily to **2.08%** at 32 KB and flattens — 32 KB is what this walk touches, so from there on the second and third passes are all hits and only the first pass still misses. Past 32 KB a bigger cache buys nothing at all, which is the shape of every capacity curve there is.",
                    "Put the size back to 8 KB and step the stride through 8, 16, 32 and 64 bytes. The miss rate reads 12.5%, 25%, 50% and then **100%**: every doubling of the gap halves the number of useful bytes in each line you fetch, until at 64 bytes every single access drags in a whole line to use four bytes of it.",
                    "That last case is the one to remember, because it is a data-structure decision and not a hardware one. An array of 64-byte structs, walked to read one `uint32_t` field out of each element, is exactly the stride-64 case. Splitting that one field into an array of its own turns the same loop back into the stride-4 case at the top of this list.",
                    "With the stride at 64, drag the size up again: 16 KB is still at 100%, and only above that does it come down, reaching **33.3%** at 32 KB. That figure and the 2.08% from two paragraphs ago are the same event counted differently — both walks fetch exactly the same 512 lines once each, and the only difference is whether sixteen accesses are served from each line or one. The memory traffic is identical; the useful work is not.",
                    "Finally, take the associativity slider from direct to 16-way. At 8 KB, at 16 KB and at 32 KB the marker does not move: below the knee every line is evicted before the next pass wants it whatever the placement rule, and at 32 KB the whole walk fits. Between those, from about 17 to 31 KB, the faint comparison curves separate from the one you are on and the marker moves the *wrong* way — at 24 KB with a stride of 4 the miss rate is **4.17%** direct-mapped, 5.21% two-way and 6.25% at four-way and above. Wider sets mean fewer sets, so more of the walk collides, and within a set LRU evicts exactly the line a walk that repeats in address order will ask for first. Associativity is the cure for a *conflict* pattern, and this one is a capacity pattern; here the size and the line width are what you are buying.",
                ],
            },
            "quiz": {
                "title": "Widths, promotions and addresses",
                "minutes": 10,
                "questions": [
                    {
                        "q": "`uint8_t a = 200, b = 100;` and the program prints the value of `a + b` as a plain integer. What appears?",
                        "opts": ["255", "300", "44", "it is undefined behaviour"],
                        "a": 1,
                        "why": r'''
300. Both operands are promoted to `int` before the addition — that is the *integer
promotion* rule, and it is value-preserving — so the sum is computed in 32 bits with
room to spare. The value 44 is what you get from `uint8_t c = a + b;`, where the
truncation happens on the assignment; the two are different lines with different
results, and confusing them is how a checksum that should read 350 ends up reading 94.
There is no undefined behaviour here: `int` overflow would be undefined, but 300 is
nowhere near the limit.
''',
                    },
                    {
                        "q": "`uint32_t *p = (uint32_t *)0x40020000;` and then `p += 5;`. What does `p` hold?",
                        "opts": ["0x40020005", "0x40020014", "0x40020020", "0x40020050"],
                        "a": 1,
                        "why": r'''
0x40020014. Pointer arithmetic counts *objects*, not bytes, and a `uint32_t` is four
bytes wide, so five of them is twenty bytes — 0x14. That number should look familiar:
it is the offset of `ODR` in the GPIO block, which is simply the sixth register along.
The value 0x40020005 is the answer for a `uint8_t *`, and the difference between the
two is the entire reason a cast on a pointer is a change of meaning rather than a
change of notation.
''',
                    },
                    {
                        "q": "A `uint8_t *` and a `uint32_t *` both hold the address 0x40020014. `*p8 = 0xAA;` puts one byte there. What does `*p32 = 0xAA;` do?",
                        "opts": [
                            "the same thing, since the value fits in one byte",
                            "a single 32-bit write of 0x000000AA, replacing all four bytes",
                            "four separate byte writes of 0xAA",
                            "it is a compile error, because 0xAA is not a 32-bit value",
                        ],
                        "a": 1,
                        "why": r'''
The pointer's type decides the *width of the bus access*, not just the arithmetic. A
`uint32_t *` produces one 32-bit store, so the three bytes above the one you were
thinking about are written too — with zeros. For a peripheral this is the difference
between configuring one field and clearing everything else in the register, and it runs
the other way as well: many peripherals require a 32-bit access and behave unpredictably,
or fault, when written a byte at a time. This is why the cast in
`*(volatile uint32_t *)0x40020014` is load-bearing rather than decorative.
''',
                    },
                    {
                        "q": "On the same 32-bit part: `int i = -1; unsigned int n = 1; if (i < n) { ... }`. Does the body run?",
                        "opts": [
                            "no — `i` is converted to unsigned and becomes 4294967295",
                            "yes — −1 is less than 1",
                            "no — comparing signed with unsigned is a compile error",
                            "it depends on the compiler",
                        ],
                        "a": 0,
                        "why": r'''
It does not run. When signed and unsigned of the same rank meet, the usual arithmetic
conversions turn the *signed* one unsigned, so −1 becomes 4294967295 and the comparison
is false. It compiles without complaint unless you have asked for `-Wsign-compare`,
which is one of the strongest arguments for turning warnings on. The same rule is why
`for (unsigned i = n; i >= 0; i--)` never terminates: the condition cannot be false.
''',
                    },
                    {
                        "q": "A function declares `uint8_t buf[4096];` as a local variable, on a part with 8 KB of SRAM. What is the characteristic symptom?",
                        "opts": [
                            "the compiler reports that there is not enough memory",
                            "the array is placed in flash instead, and writes to it are ignored",
                            "unrelated variables change value, or the chip resets, at a point in the code that has nothing to do with the array",
                            "the array is silently reduced in size",
                        ],
                        "a": 2,
                        "why": r'''
The array is on the stack, and the stack grows down from the top of SRAM towards the
globals. Nothing checks that it has room: the writes simply continue past the bottom
into whatever `.bss` holds there, so a variable somewhere else in the program changes
value, or a return address is overwritten and the chip ends up executing nonsense. The
compiler cannot warn, because it does not know how deep the call chain will be at run
time — it is the linker's map file and a stack-painting check at start-up that catch
this, not the build.
''',
                    },
                    {
                        "q": "A 2 KB lookup table is declared at file scope as `const uint16_t table[1024]`. Where does it live once the program is running, and what does it cost in SRAM?",
                        "opts": [
                            "in flash, costing nothing in SRAM",
                            "in SRAM, costing 2 KB, with a second copy in flash",
                            "in flash, but copied into SRAM at start-up",
                            "in SRAM only, costing 2 KB",
                        ],
                        "a": 0,
                        "why": r'''
`const` at file scope goes in the read-only section, which the linker places in flash,
and it is read from there — so it costs 2 KB of flash and nothing at all of SRAM. Drop
the `const` and the same array becomes initialised writable data: 2 KB of SRAM held for
the whole run, *plus* 2 KB of flash for the initial values, plus the time the startup
code spends copying one to the other. On a part with 8 KB of SRAM that one keyword is a
quarter of your memory.
''',
                    },
                ],
            },
            "blanks": {
                "title": "The GPIO block, from struct member to address",
                "minutes": 9,
                "caption": "one peripheral, described twice, and the two descriptions must agree",
                "lang": "c",
                "brief": r'''
Below is how a vendor header describes the GPIO block, and underneath it the same
addresses worked out by hand. Both are in every embedded project, and they have to come
out the same: the struct is only a convenience for the arithmetic you are about to do
in the lower half.

Every member here is one 32-bit register, listed in the order the reference manual
prints them. Fill the holes in order.
''',
                "listing": r'''
/* The GPIO block, as the vendor's header lays it out. */

typedef struct {
    volatile uint32_t MODER;    /* offset 0x00 : pin mode, 2 bits per pin  */
    volatile uint32_t OTYPER;   /* offset 0x04 : push-pull or open-drain   */
    volatile uint32_t OSPEEDR;  /* offset ___  : slew rate                 */
    volatile uint32_t PUPDR;    /* offset 0x0C : pull-up / pull-down       */
    volatile uint32_t IDR;      /* offset 0x10 : what the pins read as     */
    volatile uint32_t ODR;      /* offset ___  : what the pins are driven to */
} GPIO_TypeDef;

#define GPIOA ((GPIO_TypeDef *) 0x40020000u)

--------------------------------------------------------------------------

  six members, four bytes each, nothing narrower than a word anywhere

    sizeof(GPIO_TypeDef)                      =  ___ bytes

  the compiler adds the member's offset to the base and nothing else

    &GPIOA->ODR                               =  ___

  and by hand, with no struct at all: the same block as a plain array of
  words, ODR being the sixth of them

    ((volatile uint32_t *) 0x40020000u) + 5   =  ___

  now one that is not all words, to see what alignment costs

    struct { uint32_t a; uint8_t b; uint32_t c; }  occupies  ___ bytes
''',
                "blanks": [
                    {
                        "prompt": "OSPEEDR is the third member. Four bytes each, counting from zero.",
                        "hole": "?",
                        "opts": ["0x08", "0x03", "0x02", "0x0C"],
                        "a": 0,
                        "why": "Two whole registers sit above it, so its offset is $2 \\times 4 = 8$ "
                               "bytes, written 0x08. The value 0x03 counts members rather than bytes "
                               "— which is what pointer arithmetic does for you, and exactly why "
                               "the two notations are not interchangeable. The value 0x0C is the "
                               "member after it, PUPDR, and is what you get by counting the register "
                               "you are naming as well as the ones before it.",
                    },
                    {
                        "prompt": "ODR is the sixth member of the struct, and the fifth one along from the base.",
                        "hole": "?",
                        "opts": ["0x14", "0x18", "0x05", "0x10"],
                        "a": 0,
                        "why": "Five registers above it, so $5 \\times 4 = 20$ bytes, which is 0x14. "
                               "That is the number in `0x40020014` from the previous module — the "
                               "address you were given as a constant is a base plus this offset. The "
                               "value 0x18 is one register too far, and 0x10 is IDR, the register "
                               "that reads the pins rather than driving them: swapping those two is "
                               "a bug that looks like the output not working.",
                    },
                    {
                        "prompt": "Six members of four bytes each, with no padding needed anywhere.",
                        "hole": "?",
                        "opts": ["24", "6", "20", "28"],
                        "a": 0,
                        "why": "$6 \\times 4 = 24$ bytes. The value 6 counts members, which is what "
                               "`sizeof` would give you if it worked in elements — it does not, "
                               "it works in bytes, and that is why `sizeof(arr)/sizeof(arr[0])` is "
                               "the idiom for a count. The value 20 stops at the last member's "
                               "offset instead of its end.",
                    },
                    {
                        "prompt": "The base is 0x40020000 and ODR sits at the offset you worked out above.",
                        "hole": "?",
                        "opts": ["0x40020014", "0x40020005", "0x40020020", "0x40020140"],
                        "a": 0,
                        "why": "$\\text{0x40020000} + \\text{0x14} = \\text{0x40020014}$. The "
                               "arrow does one addition and no indirection: `GPIOA` is not a variable "
                               "holding a struct, it is a number the compiler adds an offset to. The "
                               "value 0x40020005 adds the member index instead of the byte offset, "
                               "and 0x40020140 is the same digits with the hexadecimal shifted a "
                               "place — worth a second look whenever an address is 'nearly' right.",
                    },
                    {
                        "prompt": "The same block treated as an array of 32-bit words, indexed five along.",
                        "hole": "?",
                        "opts": ["0x40020014", "0x40020005", "0x40020050", "0x4002000A"],
                        "a": 0,
                        "why": "The same address, 0x40020014, because adding 5 to a `uint32_t *` "
                               "advances by $5 \\times 4$ bytes. That agreement is the point of this "
                               "exercise: the struct is doing arithmetic you could do yourself, and "
                               "when a register comes out at the wrong address it is nearly always "
                               "because a reserved gap in the manual was left out of the struct, so "
                               "every member after it has slid four bytes.",
                    },
                    {
                        "prompt": "A word, a byte and another word. The 32-bit members must be four-byte aligned.",
                        "hole": "?",
                        "opts": ["12", "9", "16", "10"],
                        "a": 0,
                        "why": "12. The byte lands at offset 4, then three bytes of padding carry the "
                               "next `uint32_t` to offset 8, and the structure ends at 12. The value 9 "
                               "adds the widths and ignores alignment; 16 assumes each member is "
                               "padded to a word, which is not what the rule says — padding goes "
                               "wherever it is needed to align the *next* member, and at the end to "
                               "keep the whole structure's size a multiple of its widest member.",
                    },
                ],
            },
            "lab": {
                "title": "C's integer rules, written out",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
The promotions and conversions are hard to believe until you have watched them happen,
and in C they happen silently. So write them out: six small functions that model what a
C compiler does to integers, in Python, where nothing is hidden.

- `store(value, bits, signed)` — the value that actually lands in a `bits`-wide C
  integer variable. Mask to the width first; then, if the type is signed and the top
  bit is set, subtract $2^{bits}$ to get the two's-complement reading. So storing 300
  in a `uint8_t` gives 44, and storing 200 in an `int8_t` gives −56.
- `add_u8(a, b)` — the value of the C expression `a + b` where both are `uint8_t`. Both
  operands are promoted to `int` first, so this does **not** wrap: it is the ordinary
  sum of the two stored values.
- `assign_u8(a, b)` — the value of `uint8_t c = a + b;`. Same addition, then stored back
  into eight bits.
- `shl(value, n)` — `value << n` where `value` has type `int`: shift, then store into a
  signed 32-bit type.
- `shl_u(value, n)` — the same shift with `unsigned int`, so the result is stored into
  an unsigned 32-bit type.
- `lt_mixed(i, u)` — the value of `i < u` where `i` is an `int` and `u` an
  `unsigned int`. The usual arithmetic conversions make the signed operand unsigned
  before the comparison, so convert both with `store(..., 32, False)` and compare those.

Two of these model something C calls undefined rather than merely surprising. Shifting a
1 into the sign bit of a signed 32-bit type is undefined behaviour; every compiler you
will meet produces the two's-complement answer this model gives, and that is exactly why
the fix is to write `1u << 31` and stop relying on it. Signed overflow is the other, and
it is the one optimisers really do exploit.

No imports are needed.
''',
                "files": [{"name": "main.py", "content": r'''
"""What a C compiler does to integers, made visible."""


def store(value, bits, signed):
    """The value that lands in a `bits`-wide C integer variable."""
    # TODO: mask to `bits` bits; if signed and the top bit is set, subtract 2**bits.
    return 0


def add_u8(a, b):
    """The value of `a + b` for two uint8_t operands: promoted to int, so no wrap."""
    # TODO: store each operand in eight unsigned bits, then add them as integers.
    return 0


def assign_u8(a, b):
    """The value of `uint8_t c = a + b;` — the same sum, stored back into eight bits."""
    # TODO: reuse add_u8, then store the result.
    return 0


def shl(value, n):
    """`value << n` where `value` has type int: a signed 32-bit result."""
    # TODO: shift, then store into 32 signed bits.
    return 0


def shl_u(value, n):
    """`value << n` where `value` has type unsigned int: a 32-bit unsigned result."""
    # TODO: shift, then store into 32 unsigned bits.
    return 0


def lt_mixed(i, u):
    """`i < u`, where `i` is an int and `u` an unsigned int."""
    # TODO: convert both to unsigned 32-bit first, then compare.
    return False


if __name__ == "__main__":
    print("uint8_t 300 ->", store(300, 8, False))
    print("int8_t  200 ->", store(200, 8, True))
    print("200 + 100 as an expression:", add_u8(200, 100))
    print("200 + 100 stored in a uint8_t:", assign_u8(200, 100))
    print("1 << 31 signed:", shl(1, 31), " unsigned:", shl_u(1, 31))
    print("-1 < 1u is", lt_mixed(-1, 1))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""What a C compiler does to integers, made visible."""


def store(value, bits, signed):
    """The value that lands in a `bits`-wide C integer variable."""
    masked = value & ((1 << bits) - 1)
    if signed and masked >= (1 << (bits - 1)):
        masked -= (1 << bits)
    return masked


def add_u8(a, b):
    """The value of `a + b` for two uint8_t operands: promoted to int, so no wrap."""
    return store(a, 8, False) + store(b, 8, False)


def assign_u8(a, b):
    """The value of `uint8_t c = a + b;` — the same sum, stored back into eight bits."""
    return store(add_u8(a, b), 8, False)


def shl(value, n):
    """`value << n` where `value` has type int: a signed 32-bit result."""
    return store(value << n, 32, True)


def shl_u(value, n):
    """`value << n` where `value` has type unsigned int: a 32-bit unsigned result."""
    return store(value << n, 32, False)


def lt_mixed(i, u):
    """`i < u`, where `i` is an int and `u` an unsigned int."""
    return store(i, 32, False) < store(u, 32, False)


if __name__ == "__main__":
    print("uint8_t 300 ->", store(300, 8, False))
    print("int8_t  200 ->", store(200, 8, True))
    print("200 + 100 as an expression:", add_u8(200, 100))
    print("200 + 100 stored in a uint8_t:", assign_u8(200, 100))
    print("1 << 31 signed:", shl(1, 31), " unsigned:", shl_u(1, 31))
    print("-1 < 1u is", lt_mixed(-1, 1))
'''}],
                "hints": [
                    "`store` is two steps: `value & ((1 << bits) - 1)` throws away everything above the width, and then a signed type reinterprets the top bit by subtracting `1 << bits`.",
                    "Check `store` against a case you can do in your head: 0xF0 in an `int8_t` is −16, because 0xF0 is 240 and 240 − 256 = −16.",
                    "`add_u8` must not mask its result. That is the whole point of the promotion rule: the addition happens in `int`, and 200 + 100 is 300 there.",
                    "`shl` and `shl_u` differ only in the last argument to `store`. Compare `shl(1, 31)` with `shl_u(1, 31)`: same bit pattern, two different numbers, and the reason a bit mask for bit 31 is written `1u << 31`.",
                    "In `lt_mixed`, the conversion the standard performs is on the *signed* operand only: `u` already has the common type and is left alone. `store(u, 32, False)` is therefore a no-op for any value a real `unsigned int` could hold, so putting both through it is a harmless convenience that also keeps an out-of-range test argument in range.",
                ],
                "tests": [
                    {"name": "storing truncates, and a signed type reinterprets", "code": r'''
assert store(300, 8, False) == 44, f"300 in a uint8_t is 44, got {store(300, 8, False)}"
assert store(200, 8, True) == -56, f"200 in an int8_t is -56, got {store(200, 8, True)}"
assert store(0xF0, 8, True) == -16, f"0xF0 as an int8_t is -16, got {store(0xF0, 8, True)}"
assert store(-1, 16, False) == 65535, f"-1 in a uint16_t is 65535, got {store(-1, 16, False)}"
assert store(-1, 32, True) == -1, "-1 fits in an int32_t unchanged"
assert store(42, 8, False) == 42, "a value that fits is stored unchanged"
'''},
                    {"name": "the addition happens in int, so it does not wrap", "code": r'''
assert add_u8(200, 100) == 300, f"promotion means this is 300, got {add_u8(200, 100)}"
assert add_u8(255, 255) == 510, f"got {add_u8(255, 255)}"
assert add_u8(0, 0) == 0
'''},
                    {"name": "the truncation happens on the assignment", "code": r'''
assert assign_u8(200, 100) == 44, f"300 stored in eight bits is 44, got {assign_u8(200, 100)}"
assert assign_u8(255, 1) == 0, f"255 + 1 wraps to 0, got {assign_u8(255, 1)}"
assert assign_u8(100, 100) == 200, "200 fits, so nothing is lost"
'''},
                    {"name": "a shift into the sign bit", "code": r'''
assert shl(1, 30) == 1073741824, f"got {shl(1, 30)}"
assert shl(1, 31) == -2147483648, \
    f"in a signed 32-bit type that bit pattern reads as -2147483648, got {shl(1, 31)}"
assert shl(0x80, 1) == 256, \
    f"a uint8_t operand is promoted before the shift, so 0x80 << 1 is 256, not 0; got {shl(0x80, 1)}"
assert shl(0xFF, 24) == -16777216, f"got {shl(0xFF, 24)}"
'''},
                    {"name": "the same shift on an unsigned type", "code": r'''
assert shl_u(1, 31) == 2147483648, f"got {shl_u(1, 31)}"
assert shl_u(0xFF, 24) == 4278190080, f"got {shl_u(0xFF, 24)}"
assert shl_u(0x80000000, 1) == 0, \
    f"the bit shifts off the top of a 32-bit type and is gone, got {shl_u(0x80000000, 1)}"
'''},
                    {"name": "signed loses to unsigned in a comparison", "code": r'''
assert lt_mixed(1, 2) is True or lt_mixed(1, 2) == True, "1 < 2 either way"
assert not lt_mixed(-1, 1), \
    "-1 converts to 4294967295, so it is not less than 1 - this is the whole trap"
assert not lt_mixed(-1, 4294967295), "-1 converts to exactly that value, so it is not less"
assert lt_mixed(0, 1), "0 < 1 with no conversion trouble"
'''},
                    {"name": "the checksum that reads low", "code": r'''
total = 0
for value in (200, 100, 50):
    total = store(total + value, 8, False)
assert total == 94, \
    f"an 8-bit accumulator wraps twice on the way to 350 and ends at 94, got {total}"
wide = 0
for value in (200, 100, 50):
    wide = store(wide + value, 32, False)
assert wide == 350, "the same loop with a 32-bit accumulator keeps the answer"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "A pin is a circuit",
            "summary": "The register decides what the pin is trying to do. Ohm's law decides what actually happens.",
            "concepts": [
                "A GPIO pin configured as an output is a pair of transistors that connect it either to the supply rail or to ground. Treat it as an ideal voltage source of 0 V or $V_{DD}$ with a small series resistance, usually tens of ohms.",
                "That source has a current limit, typically around 8 mA per pin, and a second limit on the total drawn through the whole port that is far below the per-pin figure multiplied by the number of pins. Eight pins rated at 8 mA each do not give you 64 mA. Exceeding either does not blow up immediately; it drags the output voltage away from the rail, which is worse, because the circuit half works.",
                "An LED is a diode: below its forward voltage it passes nothing, and above it the current rises so steeply that a small change in voltage is a large change in current. For design work it is modelled as a fixed drop, around 2.0 V for a red one, and the series resistor sets the current.",
                "That resistor is not optional. Without it the pin and the diode are two voltage sources connected together, and the current is limited only by the pin's own output resistance.",
                "A pin configured as an input is close to an open circuit, so an unconnected input floats: it picks up whatever charge is nearby and reads randomly. Every input needs something defining its voltage.",
                "A pull-up resistor holds an input at $V_{DD}$ until a switch pulls it to ground. Most microcontrollers have internal pull-ups of 30 to 50 kΩ enabled by a register bit, which is one resistor you do not have to buy.",
                "An input reads 1 above $V_{IH}$ and 0 below $V_{IL}$, and between them the answer is not defined. A slowly changing signal crossing that band can be read as either, and a divider feeding an input must be designed to land clearly outside it.",
                "Open-drain output can only pull down; the pull-up does the rest. That is what lets several devices share one wire, and it is why $I^2$C looks the way it does.",
            ],
            "read": [
                {
                    "title": "The pin droops: what a GPIO output really is",
                    "minutes": 15,
                    "body": r'''
Wire a red LED from a 3.3 V microcontroller pin straight to ground, no resistor, and put
a meter on the pin. Set the pin high.

The LED lights. The meter reads **2.0 V**.

It should read 3.3. Nothing is broken, nothing has reported an error, and the code is
four characters long and correct. Yet a third of the supply voltage has gone missing
somewhere between the register bit and the piece of copper the meter is touching, and
until you know where, none of the design work in this module is possible.

## Where the missing volt went

A GPIO pin configured as an output is a pair of transistors: one that connects the pin to
the supply rail and one that connects it to ground, with the register bit choosing which.
A transistor that is on is not a wire. It has a channel resistance of a few tens of ohms,
and every milliamp you pull through it drops a voltage across it.

You do not have to guess that resistance, because the datasheet states it in disguise.
Find the line in the DC characteristics table that reads something like

```text
V_OL   output low voltage    -    -   0.4 V    at I_OL = 8 mA
```

That is a measurement: at 8 mA of load the output is 0.4 V away from the rail it is
trying to reach. Divide, and the output stage's resistance is $0.4/0.008 = 50$ Ω in the
worst case the vendor will guarantee, with typical parts nearer 25 to 40 Ω. So a pin is
an ideal voltage source of 0 V or $V_{DD}$ in series with a resistor, and it is that
resistor which ate the volt.

The other half of the picture is the LED. A diode's current is exponential in its
voltage, $I = I_s(e^{V/nV_T} - 1)$, and the useful consequence of an exponential is how
*little* the voltage moves. Multiplying the current by ten costs $nV_T\ln 10$, which for
a real LED is roughly 0.1 V. Over the whole range you would ever run an indicator at —
say 2 mA to 20 mA, a factor of ten — the forward voltage moves about a tenth of a volt.
That is why the design model for an LED is a fixed drop, $V_F \approx 2.0$ V for a red
one, and why the model is accurate enough to design with.

Now the loop closes. Kirchhoff round it: the supply provides $V_{DD}$, the LED holds
$V_F$, and everything left over is across the resistances in series with them. With no
external resistor at all, the only resistance in the loop is the pin's own:

$$I = \frac{V_{DD} - V_F}{R_{out}} = \frac{3.3 - 2.0}{40} = 32.5\ \text{mA}$$

and the pin voltage is $V_{DD} - I R_{out} = 2.0$ V, which is what the meter said. The
pin is not delivering 3.3 V into an LED; it is being dragged down to the LED's forward
voltage and asked for four times its 8 mA rating to get there.

## The design equation, and the whole table at once

Put an external resistor $R$ in the loop and the same law gives what you want directly:

$$I = \frac{V_{DD} - V_F}{R + R_{out}} \qquad\Longrightarrow\qquad R = \frac{V_{DD} - V_F}{I} - R_{out}$$

The subtraction at the front is the part that matters and the part people skip. The LED
takes its 2.0 V whatever happens, so the resistor never sees 3.3 V — it sees the
remaining 1.3 V, and that is the number to divide by the current you want.

Work an indicator through. Target 6 mA, comfortably visible and comfortably inside the
pin's 8 mA. Then $R \approx 1.3/0.006 = 217$ Ω, and the nearest stock value at or above
it is **220 Ω**. Check it back, and check the pin at the same time:

```python
VDD, VF, ROUT = 3.3, 2.0, 40.0

def current(r):
    return (VDD - VF) / (r + ROUT)

for r in (0.0, 82.0, 200.0, 220.0, 470.0):
    print("R = %6.1f ohm -> %5.2f mA, and the pin sits at %.2f V"
          % (r, 1000 * current(r), VDD - current(r) * ROUT))
```

The five lines it prints are the whole design space of this circuit. With no resistor,
32.50 mA and a pin at 2.00 V — the bench measurement at the top of this reading,
reproduced. With 82 Ω, 10.66 mA, still over the rating. With 200 Ω, 5.42 mA and a pin at
3.08 V; with 220 Ω, exactly 5.00 mA at 3.10 V; with 470 Ω, 2.55 mA, which is a visible
but dim indicator.

Two things fall out of that table that the one-line formula hides. The pin's own 40 Ω is
not negligible: at 220 Ω it is 15% of the loop, and it always makes the LED *dimmer*
than the arithmetic without it predicts, never brighter. And the current is far more
sensitive to $R$ at the small end than at the large end, because $R_{out}$ and $V_F$
stop being small corrections there.

## Inputs: the pin that reads whatever you like

Configured as an input, the same pin is close to an open circuit — leakage of perhaps a
microamp. Connect a push-button between the pin and ground and nothing else, and ask
what the pin reads when the button is *not* pressed.

Nothing defines its voltage. The pin has a few picofarads of capacitance holding whatever
charge last reached it, and mains hum, a finger near the board or the neighbouring pin
switching will move it across the decision threshold. During bring-up it will read 1
"most of the time", which is exactly what makes this fault survive into shipped products:
it looks like it works.

A pull-up resistor fixes the voltage. It holds the pin at $V_{DD}$ and leaves the button
the single job of overriding it. Sizing it is a two-sided argument, and both sides are
arithmetic. Too large and the input's own leakage matters: 1 µA through 1 MΩ is a volt of
error, and the pin is defenceless against noise as well. Too small and you burn current
every time the button is held: 3.3 V across 100 Ω is 33 mA, on a battery, to report a
button. Ten kilohms puts $3.3/10\,\text{k} = 330$ µA through a pressed button and leaves
the leakage contributing 10 mV. Most microcontrollers have an internal pull-up of 30 to
50 kΩ that a register bit switches on, which is a resistor you do not have to buy.

The threshold is not a threshold, either. An input reads 1 above $V_{IH}$ and 0 below
$V_{IL}$, and between them the answer is not defined. So a level-shifting divider has to
land well outside that band at both ends. A 5 V sensor read by a 3.3 V pin through
10 kΩ over 20 kΩ gives $5 \times 20/30 = 3.33$ V at the top of its swing — over the
rail — while a 4.5 V logic high gives 3.0 V, which clears $V_{IH} = 2.0$ V and stays
under 3.3 V. Both checks are separate and both matter: too low and the reading is
undefined, too high and current flows into the pin's protection diode.

## The mistake, and why it is tempting

The resistor is not optional, and the belief that it is has a specific form: *the diode
limits its own current*.

It is tempting for two honest reasons. The first is that the I-V curve really is very
steep, so it feels like a device that picks its own operating point. The second, and the
stronger one, is that leaving the resistor out **works**. The LED lights, the chip does
not fail, and a meter that is not on the pin sees nothing wrong. What has actually
happened is that the pin's own output resistance has become the current-limiting element
by default — a resistor chosen by nobody, specified by nobody, and dissipating inside the
package rather than in a component that was designed to get warm.

The related trap is the port total. Eight pins rated at 8 mA each do not give you 64 mA;
the whole port has its own limit, typically far below the sum, and exceeding it does not
blow anything up. It drags every output on that port away from the rail, which is worse,
because the circuit half works.

## Where these models stop holding

The constant-drop LED model fails when $V_{DD} - V_F$ is small. A white or blue LED has
$V_F$ around 3.2 V, and from a 3.3 V rail that leaves 0.1 V for the resistor. The
part-to-part spread of $V_F$ alone is ±0.2 V, so one LED from the reel draws far too much
and the next one does not light at all. In that regime the resistor no longer sets the
current, and the honest answers are a higher supply, a boost converter, or a proper
constant-current driver.

The Thevenin picture of the output stage is linear, and a transistor is not. Its channel
resistance rises with temperature and varies with supply voltage, and near the current
limit the stage leaves the region where a single resistance describes it at all. Treat
$R_{out}$ as a bound worth including, not as a measured constant.

Everything above is also static. It says nothing about *edges* — driving a long track, or
a scope probe, means charging capacitance, and how fast the pin does that is what the
slew-rate register controls and what makes a fast edge a source of radiated noise.

And $V_{IH}$ and $V_{IL}$ describe a band, not a line. A slowly-changing input crossing
that band can be read as either value, and can oscillate between them several times on
one crossing. That is a genuine failure mode for a signal from an RC filter, and the
device that removes it is a Schmitt-trigger input with hysteresis, which module 7 uses
for exactly this reason.

## What you are about to build

The build for this module, **An indicator the pin can afford**, is the loop above drawn
in the schematic editor. The 3.3 V pin is on the left, the LED is modelled the way it was
modelled here — a 2.0 V source, since the editor has no diode symbol — and the probe sits
on its anode. Nothing joins the two yet, so no current flows at all.

Your job is the series resistor, and the checks measure the finished circuit: the LED
current has to land between 5 mA and 8 mA, the probe has to read the LED's 2.0 V, and
every milliamp the pin sources has to go through the LED rather than round it.

One difference to hold in mind. The editor models the pin as an ideal 3.3 V source with
no output resistance, so 220 Ω there gives $1.3/220 = 5.91$ mA rather than the 5.00 mA
of the table above. Both are inside the window, which is the point of aiming at the
middle of a range rather than at its edge.
''',
                },
            ],
            "quiz": {
                "title": "What the pin can and cannot drive",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A 3.3 V pin drives a red LED with a 2.0 V forward drop through a series resistor. What voltage appears across the resistor?",
                        "opts": ["3.3 V", "1.3 V", "2.0 V", "it depends on the resistor value"],
                        "a": 1,
                        "why": r'''
1.3 V. Kirchhoff's voltage law round the loop: the pin provides 3.3 V, the LED takes
2.0 V of it, and whatever is left is across the resistor. The resistor value does not
change that — it changes the *current*, which is $1.3/R$. Answering "it depends"
is the reflex of treating the LED as a resistor; the point of the constant-drop model
is that the diode fixes its own voltage and lets the resistor take the remainder.
''',
                    },
                    {
                        "q": "The same pin is rated at 8 mA. Which series resistor keeps the LED inside that rating?",
                        "opts": ["10 Ω", "0 Ω, since the LED limits itself", "82 Ω", "220 Ω"],
                        "a": 3,
                        "why": r'''
$R = 1.3/0.008 = 162.5$ Ω is the smallest permitted value, so 220 Ω passes and 82 Ω
would ask for 15.9 mA — twice the rating. Note which way the inequality runs: a
*larger* resistor is always electrically safe and merely dimmer. The dangerous answer
is B, and it is a real belief: a diode does not limit its own current in any useful
way, and with no resistor the only thing standing between the rail and ground is the
pin's own output resistance of a few tens of ohms.
''',
                    },
                    {
                        "q": "A push-button connects an input pin to ground when pressed. Nothing else is attached to the pin. What does the pin read when the button is *not* pressed?",
                        "opts": [
                            "an unpredictable value that may change from moment to moment",
                            "a reliable 1",
                            "a reliable 0",
                            "0 V, because the pin is internally grounded",
                        ],
                        "a": 0,
                        "why": r'''
Nothing defines the pin's voltage when the button is open, so it floats: the tiny
capacitance of the pin holds whatever charge last reached it, and mains hum, a nearby
finger or the neighbouring pin switching will move it across the threshold. The fix is
a pull-up — internal, enabled by a register bit, or external, typically 10 kΩ — which
holds the pin at $V_{DD}$ so that the button's job is only to override it. Reading 1
"most of the time" during bring-up is exactly what a floating input looks like, and it
is why this fault survives into shipped products.
''',
                    },
                    {
                        "q": "A 5 V sensor output must be read by a 3.3 V input, so it is divided by 10 kΩ over 20 kΩ. The sensor's logic high is 4.5 V and the input's $V_{IH}$ is 2.0 V. Does a high read correctly?",
                        "opts": [
                            "no, because 3.0 V exceeds the 3.3 V supply",
                            "no, because the divider output is below $V_{IH}$",
                            "yes — the divider gives 3.0 V, which is above $V_{IH}$ and below the supply",
                            "it cannot be decided without knowing the sensor's output resistance",
                        ],
                        "a": 2,
                        "why": r'''
$4.5 \times 20/(10+20) = 3.0$ V, which clears $V_{IH} = 2.0$ V comfortably and stays
under the 3.3 V rail, so the input is neither ambiguous nor over-driven. The two
checks are separate and both matter: too low and the reading is undefined, too high
and current flows into the pin's protection diode. A divider that lands *between*
$V_{IL}$ and $V_{IH}$ is the worst outcome of all, because it reads correctly on the
bench and incorrectly at temperature.
''',
                    },
                    {
                        "q": "Why can several open-drain outputs share one wire, when several push-pull outputs cannot?",
                        "opts": [
                            "because open-drain outputs are current sources rather than voltage sources",
                            "because an open-drain output can only pull the wire down, so two of them can never fight",
                            "because open-drain outputs switch more slowly",
                            "because the pull-up resistor isolates them from one another",
                        ],
                        "a": 1,
                        "why": r'''
An open-drain stage has only the lower transistor. It can connect the wire to ground
or let go of it entirely, so the worst two devices can do together is pull down at the
same time, which is harmless. Two push-pull outputs disagreeing put the supply rail
and ground in series through two transistors, and the current is limited by nothing
useful. The pull-up is what returns the shared wire to a high level once everyone has
let go — it does not isolate anything, and choosing its value trades speed against
current, which is the whole of $I^2$C bus design.
''',
                    },
                ],
            },
            "build": {
                "title": "An indicator the pin can afford",
                "minutes": 22,
                "brief": r'''
A 3.3 V GPIO pin has to light a red LED. The pin is rated at **8 mA**, and the LED is
too dim to see below about **5 mA**. Your job is to place the series resistor that
lands the current between those two figures.

## How the LED is drawn here

The schematic editor has no diode symbol, so the LED is modelled the way it is modelled
on paper: as a **2.0 V source** in series with the current path. That is the
constant-forward-drop model, and for a design like this one it is accurate to better
than a tenth of a volt. It is already on the canvas, with a probe on its anode.

The pin is the 3.3 V source at the left, already wired to a rail. Nothing joins the
rail to the LED yet, so no current flows at all.

## What the finished circuit must do

- the current through the LED is between **5 mA and 8 mA**
- the probe, which sits on the LED's anode, reads **2.0 V**
- every milliamp the pin sources goes through the LED, with no path around it

## Working it out

Kirchhoff's voltage law round the loop gives the voltage across the resistor before
you know anything else. Divide by the current you want, and pick a resistance in the
resulting range. The checks measure the finished circuit, so any value that lands the
current inside the window passes.

Click a component to edit its value; `1k`, `220` and `4k7` are all understood.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "V", "x": 9, "y": 9, "rot": 1, "value": 2.0},
                        {"id": "p3", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p4", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [11, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "V", "x": 9, "y": 9, "rot": 1, "value": 2.0},
                        {"id": "p3", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p4", "kind": "OUT", "x": 11, "y": 8},
                        {"id": "p5", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 200},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [11, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                    ],
                },
                "checks": [
                    {"name": "the pin and the LED are both still in the circuit, with the LED on the probed node", "code": r'''
const vs = c.values('V');
c.assert(vs.length === 2,
  'This circuit has two sources: the 3.3 V pin and the 2.0 V LED model. Found ' + vs.length + '.');
c.assert(vs.some(function (v) { return Math.abs(v - 3.3) <= 0.02; }), 'The 3.3 V pin must stay.');
c.assert(vs.some(function (v) { return Math.abs(v - 2.0) <= 0.02; }),
  'The 2.0 V source is the LED. Do not delete it — it is what makes this a design problem.');
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'V' && Math.abs(p.value - 2.0) <= 0.02 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'The LED must run from the probed node down to ground. A part sitting on the canvas ' +
   'with one end unconnected is not in the circuit.');
'''},
                    {"name": "the probe reads the LED's 2.0 V forward drop", "code": r'''
c.close(c.vout(), 2.0, 0.01,
  'the anode voltage — with the LED conducting, the probe should sit at its forward drop');
'''},
                    {"name": "the LED gets between 5 mA and 8 mA", "code": r'''
const led = c.net.parts.filter(function (p) {
  return p.kind === 'V' && Math.abs(p.value - 2.0) <= 0.02;
})[0];
c.assert(led, 'No 2.0 V LED model found.');
const i = Math.abs(c.dc().currents[led.id]);
c.assert(i >= 5e-3 * 0.99,
  'Below about 5 mA the LED is not visibly lit; this circuit gives it ' + c.fmt(i, 'A') +
  '. A smaller resistor passes more current.');
c.assert(i <= 8e-3 * 1.01,
  'The pin is rated at 8 mA and this circuit asks it for ' + c.fmt(i, 'A') +
  '. A larger resistor passes less current.');
'''},
                    {"name": "everything the pin sources goes through the LED", "code": r'''
const parts = c.net.parts.filter(function (p) { return p.kind === 'V'; });
const led = parts.filter(function (p) { return Math.abs(p.value - 2.0) <= 0.02; })[0];
const pin = parts.filter(function (p) { return Math.abs(p.value - 3.3) <= 0.02; })[0];
c.assert(led && pin, 'Both sources must be present.');
const cur = c.dc().currents;
const iLed = Math.abs(cur[led.id]);
const iPin = Math.abs(cur[pin.id]);
c.assert(iLed > 1e-4,
  'No current is reaching the LED at all — the loop from the pin through a resistor ' +
  'and down through the LED to ground is not complete.');
c.close(iPin, iLed, 0.02,
  'the pin current against the LED current. They must be equal: anything that lets ' +
  'current round the LED loads the pin without lighting anything');
c.assert(iPin <= 8e-3 * 1.01,
  'The pin is delivering ' + c.fmt(iPin, 'A') + ', which is over its 8 mA rating.');
'''},
                ],
                "hints": [
                    "Start with KVL: 3.3 V from the pin, minus 2.0 V taken by the LED, leaves 1.3 V for the resistor.",
                    "$R = 1.3/I$. At the 8 mA limit that is 162.5 Ω, and at 5 mA it is 260 Ω, so any value between those two works.",
                    "220 Ω is the value that would actually be fitted, because it is a stock E12 part in the middle of the range. 200 Ω is equally acceptable to the checks.",
                    "Place the resistor vertically between the rail wire at the top and the LED's anode below it, so the current has one path: pin, resistor, LED, ground.",
                    "If the checks report 0 A, look for a gap in the loop. The rail already reaches across; what is missing is the run down through the resistor into the LED's top pin.",
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Driving a load the pin cannot",
            "summary": "Between an 8 mA pin and a relay coil there is a transistor, a resistor and a diode. Each of the three is there for a reason you can put a number on.",
            "concepts": [
                "Once the load draws more than the pin's rating, or runs from a different rail, the pin's job stops being to supply the current and becomes to operate a switch. A transistor used as a switch is either off or hard on: the region in between is where an amplifier lives, and where a switch turns supply current into heat.",
                "A bipolar transistor is driven by current. To hold a collector current $I_C$ in saturation you supply a base current of at least $I_C/h_{FE}$, and because the datasheet's $h_{FE}$ is a *minimum* that falls as the current rises, real designs overdrive it by two to ten times. The base looks like a diode, so the base resistor sees $V_{pin} - V_{BE}$, about $3.3 - 0.8$ V in hard saturation, and the pin's 8 mA ceiling then puts a ceiling on the collector current you can switch this way.",
                "A MOSFET is driven by voltage, so it takes no steady gate current at all. What it takes instead is charge: the gate is a few nanofarads, and the pin has to move that charge at every edge, which is why a slow driver makes a hot transistor. The other requirement is that the threshold be low enough for 3.3 V to turn the part fully on — a **logic-level** device — because a part specified at 10 V will half-open at 3.3 and dissipate accordingly.",
                "Low side means the switch sits between the load and ground, and it is the easy case: the emitter or source is at ground, which is where the control voltage is measured from. High side means the switch sits between the supply and the load, and now the device's reference terminal moves with the load — which needs a P-channel part, or a driver that can hold the gate above the supply rail.",
                "A coil will not let its current stop. Open the switch and the inductance produces whatever voltage it takes to keep the current flowing, which is hundreds of volts across a transistor rated for tens, and the failure is immediate and permanent. A flyback diode across the coil — reverse-biased, so it does nothing at all while the load is on — gives that current a path the instant the switch opens, and clamps the excursion to a diode drop above the supply.",
            ],
            "read": [
                {
                    "title": "Three components between a pin and a relay",
                    "minutes": 15,
                    "body": r'''
Put a meter across the relay coil on the bench. It reads **102 Ω**, and the part is a
12 V relay, so operating it means moving $12/102 = 118$ mA through that coil.

The pin that has to command it is rated at 8 mA.

There is a factor of fifteen between those two measurements and no line of code closes
it. What closes it is three components, and the useful thing about this module is that
each of the three has a number attached — a base resistor you can compute, a dissipation
you can compute, and a voltage spike you can compute. None of them is a rule of thumb.

## The pin stops supplying and starts commanding

Once the load draws more than the pin can source, or runs from a different rail, the
pin's job changes. It is no longer the thing that delivers the current; it is the thing
that operates a switch, and the switch delivers the current from the load's own supply.

A transistor used as a switch lives in one of two states. Off, it passes almost nothing
and dissipates almost nothing. Hard on — *saturated* — it holds perhaps 0.2 V across
itself and dissipates almost nothing again. The region in between is where an amplifier
lives and where a switch turns supply current into heat, so the whole of switch design is
about staying out of it.

A bipolar transistor is driven by current. To hold a collector current $I_C$ the base
must be supplied with enough current that the transistor *could* pass more than the
circuit is asking of it, which means

$$I_B \geq \frac{I_C}{h_{FE}}$$

and here the datasheet is doing something people misread. The $h_{FE}$ in that table is a
**minimum**, it falls as the collector current rises, and it falls again when the part is
cold. Designing at $I_C/h_{FE}$ exactly puts you on the boundary of saturation for the
worst part on the worst day, so practice multiplies by an overdrive factor of two to ten.

The other half of the base circuit is a diode. The base-emitter junction holds its own
voltage — about 0.8 V when driven hard into saturation, a little above the 0.7 V quoted
for a junction on the edge of conduction — so the resistor never sees the pin's whole
output. It sees what is left:

$$R_B = \frac{V_{pin} - V_{BE}}{I_B}$$

which is the same subtraction as the LED in the previous module, for the same reason.

## Working one through

Take the relay above at 120 mA, and a small transistor whose datasheet guarantees
$h_{FE} \geq 40$ at that collector current. An overdrive of three asks for
$I_B = 3 \times 120/40 = 9$ mA, and the pin is rated at 8. The design does not close, and
that is a real result rather than an arithmetic slip: the honest moves from here are a
part with a higher guaranteed gain, a Darlington, a logic-level MOSFET, or a second
transistor to drive the first.

So work the other way instead. Fix the resistor and see what gain you are demanding:

```python
VPIN, VBE, IC, HFE_MIN = 3.3, 0.8, 0.120, 40

print(" R_B       I_B     forced gain   saturated?")
for rb in (330, 470, 1000, 2200, 10000):
    ib = (VPIN - VBE) / rb
    beta = IC / ib
    print("%5d ohm  %5.2f mA  %8.1f      %s"
          % (rb, 1000 * ib, beta, "yes" if beta <= HFE_MIN else "NO"))
```

The five lines say the whole story. A **330 Ω** base resistor draws 7.58 mA from the pin
— inside its 8 mA, with nothing spare — and demands a forced gain of 15.8, which any part
guaranteed to reach 40 will supply with room to spare. That transistor is properly
saturated. 470 Ω gives 5.32 mA and a forced gain of 22.6, still comfortable.

At **1 kΩ** the base current falls to 2.5 mA and the forced gain rises to 48.0, above
the guaranteed 40. The transistor comes out of saturation. At 2.2 kΩ it is asking for
105.6 and at 10 kΩ for 480, which is an amplifier, not a switch.

What "coming out of saturation" costs is a multiplication:

$$P = V_{CE} I_C$$

Saturated at $V_{CE} = 0.2$ V and 120 mA, the transistor dissipates 24 mW and is cold.
Half-on at $V_{CE} = 1.5$ V it dissipates 180 mW, and the same failure on a load of
500 mA gives $1.5 \times 0.5 = 0.75$ W, against the half-watt or so a TO-92 package can
shed into still air. The part is on its way out, and the cause is a resistor value rather
than a transistor rating.

## The coil will not let go of its current

A board came back from the field with a dead transistor: 0.6 Ω from collector to emitter
in both directions, a short. It had switched about four hundred times. Nothing in the
circuit ever asked it to pass more than 120 mA, and it was rated at 40 V and 600 mA.

An inductor opposes a change in its current, and the voltage it produces to do so is
$v = L\,di/dt$. When the transistor turns off, $di/dt$ is enormous:

```python
L, I0, R_COIL = 0.085, 0.118, 102.0

for t_off in (1e-6, 1e-5, 1e-4):
    print("current falling to zero in %6.1f us would need %8.0f V"
          % (t_off * 1e6, L * I0 / t_off))
print("with a diode fitted, the current decays with L/R = %.2f ms"
      % (1000 * L / R_COIL))
```

An 85 mH coil carrying 118 mA, switched off in a microsecond, would need **10030 V**.
Ten microseconds still needs 1003 V, and a hundred needs 100 V. Nothing supplies ten
kilovolts, of course — what happens instead is that the collector junction avalanches at
its rated 40 V, and the coil's energy is dumped into a millimetre of silicon that was
never meant to absorb it. Once is survivable. Four hundred times is not, which is why
the part degrades slowly and the product fails in the field rather than on the bench.

The last line of that block is the fix. A diode across the coil, cathode to the positive
end, is reverse-biased and conducts nothing while the relay is energised. The instant the
switch opens, the coil reverses the voltage across itself, the diode conducts, and the
current circulates around the coil-and-diode loop, decaying with $L/R = 0.83$ ms instead
of vanishing. The excursion is clamped to one diode drop above the supply, and the
mechanism that killed the transistor no longer exists.

That number has a cost attached, which is worth knowing before somebody blames you for
it: 0.83 ms of decay is 0.83 ms of the relay staying closed after you told it to open. If
release time matters, a resistor or a Zener in series with the diode shortens the decay
by allowing a larger — but still bounded — voltage.

## The mistake, and why it is tempting

Fitting a 1 kΩ base resistor.

It is the reflex value. A resistor into a base is "about a kilohm" in the same way that a
pull-up is "about ten", and on this circuit it gives 2.5 mA, a forced gain of 48, and a
transistor that is not saturated. What makes it genuinely hard to catch is that it
*works*: at room temperature, on a part from the good end of the gain spread, the relay
clicks and the LED lights and every test passes. What has changed is that $V_{CE}$ is now
1.5 V rather than 0.2 V, the transistor is warm, and the margin that was supposed to
absorb temperature and part spread has been spent.

Its close relative is dividing the pin's whole 3.3 V by the base resistor instead of
$3.3 - 0.8$. That is a 25% error in base current in the direction of less drive, and it
is tempting because 3.3 V is the number printed on the schematic.

## Where these models stop holding

The fixed 0.8 V for $V_{BE}$ is a design convenience. It moves with current, and it moves
about −2 mV per °C with temperature, so a design that only closes at 25 °C does not
close at 85 °C.

The $h_{FE}$ number is worse. It spreads by 3:1 across parts of the same type, falls at
high collector current, and falls further when cold. A design that uses the *typical*
figure from the datasheet is not a design; use the guaranteed minimum at your actual
collector current, and then overdrive it.

The saturation picture is a DC one. It says nothing about the transition, during which
the device passes through the linear region and dissipates. At a few operations a second
that is nothing at all; at tens of kilohertz it is the dominant loss, and it is why fast
switching moves to MOSFETs — where the pin no longer supplies steady current at all, but
must instead charge and discharge a few nanofarads of gate at every edge, through its own
output resistance. "Logic-level" is a specification and not an adjective: an ordinary
MOSFET characterised at $V_{GS} = 10$ V is part-way on at 3.3 V, and part-way on is the
expensive state.

Everything above is also low side — the switch between the load and ground, with the
emitter or source at the same potential as the control voltage is measured from. Move the
switch between the supply and the load and the reference terminal moves with the load,
which needs a P-channel part or a driver that can hold a gate above the supply rail. A
3.3 V pin cannot pull the base of a PNP whose emitter is at 12 V anywhere near low
enough, and it cannot survive being pulled up to 12 V either.

## What you are about to build

Two exercises follow. The numeric question, **What the base resistor asks of the pin**,
draws the base loop alone — the pin, a 330 Ω resistor and the junction modelled as its
0.8 V — and asks how much current the pin has to supply. That is the first line of the
table above, and the answer is checked against the app's own solver rather than against
arithmetic somebody did once.

The symbol drill, **Five symbols from a driver schematic**, asks you to read each part by
its *job* rather than its name: the NPN low-side switch and the arrow that identifies it,
the PNP you would reach for on the high side, the flyback diode and which way round its
bar goes, the load's own supply drawn separately from the logic supply, and the
mechanical contact whose bounce is the subject of module 7.
''',
                },
            ],
            "match": {
                "title": "Five symbols from a driver schematic",
                "minutes": 6,
                "brief": r'''
A driver stage is a handful of components and the reason for each one is a different
sentence. These are the symbols you meet around one — the low-side switch itself, the
complementary device you would reach for instead on the high side, and the parts that
surround them. Read each label as a *job* rather than a name: in a schematic you have
not seen before, the job is what you are trying to work out, and the symbol is the clue.

There are six labels and five symbols, so one label describes a part that is not drawn
here at all.
''',
                "prompt": "Pick a label, then tap the symbol that does that job.",
                "labels": [
                    "The switch: a small current into the base lets a much larger one through the collector, and the arrow leaves on the emitter",
                    "The same device built the other way up, for a switch that has to sit between the supply and the load rather than between the load and ground",
                    "The part that gives the coil's current somewhere to go the instant the switch opens, and that does nothing at all while the load is energised",
                    "The load's own supply, which need not be — and usually is not — the rail the processor runs from",
                    "The mechanical contact whose few milliseconds of bounce are the reason an input needs filtering",
                    "A part that emits light when current passes and blocks it entirely the other way",
                ],
                "items": [
                    {"sym": "NPN", "a": 0, "why": "An NPN transistor, the ordinary low-side switch. "
                     "The arrow is on the emitter and points outward, which is the whole difference "
                     "from its complement: read the arrow as the direction conventional current "
                     "leaves. Base current in, collector current through, and the emitter carries "
                     "the sum of the two back to ground."},
                    {"sym": "PNP", "a": 1, "why": "A PNP transistor. The arrow points *into* the "
                     "device, and everything about it is upside down: the emitter goes to the "
                     "positive rail and it turns on when the base is pulled *below* the emitter. "
                     "That is what makes it the high-side part, and also why a 3.3 V pin cannot "
                     "drive one whose emitter sits at 12 V without something in between — the "
                     "pin cannot get the base far enough below 12 V, and it cannot survive being "
                     "pulled up to it either."},
                    {"sym": "D", "a": 2, "why": "A diode, here the flyback (or freewheel) diode, "
                     "wired across the coil with its cathode — the bar — to the positive "
                     "end. In normal operation that is reverse bias and it conducts nothing. When "
                     "the switch opens, the coil reverses the voltage across itself trying to "
                     "maintain its current, the diode becomes forward biased, and the current "
                     "circulates through it and decays instead of arcing across the transistor. "
                     "Fit it the other way round and it shorts out the supply."},
                    {"sym": "BATT", "a": 3, "why": "A battery, standing here for the load's own "
                     "supply. The long bar is positive. Drawing it separately from the logic supply "
                     "is a habit worth keeping even when they come from the same regulator, because "
                     "it makes you ask the two questions that matter: does the load's return current "
                     "share a track with the processor's ground, and is there a capacitor near the "
                     "coil to take the surge when it switches?"},
                    {"sym": "SW", "a": 4, "why": "A mechanical switch. It appears on a driver "
                     "schematic as the thing that *commands* the load rather than the thing that "
                     "carries it — and its contacts bounce for a few milliseconds on every "
                     "operation, which is why the input it drives needs filtering before an "
                     "interrupt is attached to it."},
                ],
            },
            "quiz": {
                "title": "Base current, saturation and the spike",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A relay coil draws 120 mA. The transistor's datasheet guarantees $h_{FE} \\geq 40$ at that collector current, and the usual practice is to overdrive the base by a factor of three. What base current does that ask for?",
                        "opts": ["3 mA", "9 mA", "0.9 mA", "40 mA"],
                        "a": 1,
                        "why": r'''
$I_B = 3 \times 120/40 = 9$ mA — which is more than the 8 mA the pin is rated for, and
that is the useful part of the answer. The bare $120/40 = 3$ mA is the *edge* of
saturation at the guaranteed minimum gain, and designing at that edge means the
transistor comes out of saturation whenever the gain is at the low end of its spread or
the part is cold. Faced with 9 mA against an 8 mA pin you have three honest moves: a
transistor with a higher guaranteed gain, a Darlington or a logic-level MOSFET, or a
second transistor to drive the first.
''',
                    },
                    {
                        "q": "A 3.3 V pin drives that base through a resistor, and the base-emitter junction sits at about 0.8 V in hard saturation. Which resistor gives 5 mA of base current?",
                        "opts": ["660 Ω", "500 Ω", "2.5 kΩ", "160 Ω"],
                        "a": 1,
                        "why": r'''
$R_B = (3.3 - 0.8)/0.005 = 500$ Ω. The base junction takes its 0.8 V whatever the
current, so the resistor only ever sees the remaining 2.5 V — exactly the same
subtraction as the LED two modules ago, and for the same reason. Using the whole 3.3 V
gives 660 Ω and about 3.8 mA, a quarter less base current than intended, which is the
difference between saturated and warm.
''',
                    },
                    {
                        "q": "The relay works, but after a few hundred operations the transistor fails short. No flyback diode was fitted. What killed it?",
                        "opts": [
                            "the coil current exceeded the transistor's rating",
                            "the base resistor was too small and overheated the junction",
                            "the coil generated a large reverse voltage each time the current was interrupted, and the collector junction broke down",
                            "the relay contacts welded and shorted the supply into the transistor",
                        ],
                        "a": 2,
                        "why": r'''
An inductor opposes a change in its current, and the only way it can do that when the
switch opens is to develop whatever voltage the change demands: $v = L\,di/dt$, and
$di/dt$ at switch-off is enormous. A 12 V relay easily produces a few hundred volts
against a transistor rated at 40, and the collector junction avalanches. It rarely fails
on the first operation, which is what makes it so dangerous: the part degrades over
thousands of cycles and the product fails in the field rather than on the bench. The
diode across the coil costs a penny and removes the mechanism entirely.
''',
                    },
                    {
                        "q": "Where does the flyback diode go, and which way round?",
                        "opts": [
                            "across the coil, cathode to the positive supply",
                            "across the coil, cathode to the transistor's collector",
                            "in series with the coil, cathode towards the collector",
                            "from the collector to ground, cathode to ground",
                        ],
                        "a": 0,
                        "why": r'''
Across the coil, with the bar — the cathode — at the positive end. In normal operation
that puts the supply on the cathode and the collector, which is near ground, on the
anode: reverse-biased, conducting nothing. When the switch opens, the coil's voltage
reverses, the anode goes *above* the supply, the diode conducts and the coil's current
circulates around the coil-and-diode loop until the resistance of the loop dissipates
it. Turning it round instead puts a forward diode straight across the supply, which is
a short circuit that works exactly as long as it takes to get warm. Putting it in
series with the coil merely blocks the load.
''',
                    },
                    {
                        "q": "A transistor switching 500 mA is given too little base current and settles at $V_{CE} = 1.5$ V instead of the 0.2 V of saturation. How much power does it dissipate?",
                        "opts": ["0.10 W", "0.75 W", "6.0 W", "7.5 mW"],
                        "a": 1,
                        "why": r'''
$P = V_{CE} I_C = 1.5 \times 0.5 = 0.75$ W, against $0.2 \times 0.5 = 0.10$ W when it is
properly saturated. A small transistor in a TO-92 package can shed perhaps half a watt
into still air before it exceeds its junction temperature, so this one is on its way out
— and the cause is a resistor value, not a transistor rating. This is the concrete
reason a switch is driven hard rather than adequately: the dissipation is set by how
far into saturation you push it, and base current is much cheaper than heat.
''',
                    },
                    {
                        "q": "Why is a logic-level MOSFET usually the better choice here, and what does the pin still have to do for it?",
                        "opts": [
                            "it needs no steady gate current, but the pin must charge and discharge a few nanofarads of gate capacitance at each edge",
                            "it needs no gate connection at all once it has been switched on",
                            "it needs a smaller base resistor, and the pin must supply the same current more briefly",
                            "it dissipates nothing at any gate voltage, so the drive does not matter",
                        ],
                        "a": 0,
                        "why": r'''
The gate is insulated, so once it is charged the steady current is leakage —
nanoamps — and the 8 mA problem disappears. What replaces it is charge: a few
nanofarads that the pin must fill and empty at every transition, and the pin's own
output resistance sets how long that takes. During that time the device is partly on and
dissipating, which is why gate resistors are chosen small for switching and why a
MOSFET switched slowly by a weak pin runs hotter than one switched quickly. The word
"logic-level" is the other half: an ordinary MOSFET specified at $V_{GS} = 10$ V is only
part-way on at 3.3 V, and part-way on is the expensive state.
''',
                    },
                ],
            },
            "numeric": {
                "title": "What the base resistor asks of the pin",
                "minutes": 8,
                "brief": r'''
The base-emitter junction is drawn here the way the LED was: as the fixed voltage it
holds while it conducts. In hard saturation that is about **0.8 V** — a little above the
0.7 V quoted for a junction on the edge of conduction, because the base is being driven
well past it. (The editor does have an NPN symbol and will solve one; a `numeric` unit's
diagram is restricted to the seven linear kinds, and in any case the question below is
about one loop, for which the fixed drop is the right model.)

So what is on the canvas is the pin, the base resistor, and the junction. The collector
side of the transistor is not drawn at all, and does not need to be: the base current is
decided entirely by this loop.
''',
                "prompt": "How much current must the pin supply into the base?",
                "note": "Give the answer in milliamps, to two decimal places.",
                "diagram": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                        {"id": "rb", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 330},
                        {"id": "vbe", "kind": "V", "x": 9, "y": 9, "rot": 1, "value": 0.8},
                        {"id": "g1", "kind": "GND", "x": 9, "y": 11},
                        {"id": "out", "kind": "OUT", "x": 12, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [12, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                    ],
                },
                "given": [
                    {"label": "Pin output", "value": "3.30 V"},
                    {"label": "Base resistor", "value": "330 Ω"},
                    {"label": "$V_{BE}$ in saturation", "value": "0.80 V"},
                    {"label": "Pin rating", "value": "8 mA"},
                ],
                "aside": "One loop, so one current, and the junction takes its 0.8 V before the "
                         "resistor gets any say in the matter.",
                "answer": 7.5758,
                "tol": 0.05,
                "unit": "mA",
                "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'rb'; })[0];
return 1000 * Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value;
''',
                "hint": "Kirchhoff round the loop: the pin provides 3.3 V, the junction takes "
                        "0.8 V of it, and the resistor has the rest across it. Then Ohm's law.",
                "wrong": "Check whether you divided the whole 3.3 V by the resistor. The junction "
                         "holds its own drop, and only what is left appears across the 330 Ω.",
                "why": "$(3.3 - 0.8)/330 = 7.58$ mA, which is just inside the pin's 8 mA rating and "
                       "leaves nothing spare. Read it as a design result rather than an arithmetic "
                       "one: with 7.58 mA of base current, a transistor holding 250 mA of collector "
                       "current is being run at a forced gain of $250/7.58 = 33$, so any part whose "
                       "guaranteed $h_{FE}$ at 250 mA is above about 35 will saturate. Drop to a "
                       "1 kΩ base resistor and the base current falls to 2.5 mA, the forced gain "
                       "rises to 100, and the same transistor comes out of saturation and starts "
                       "dissipating watts.",
            },
        },

        # ---- M5 -----------------------------------------------------------
        {
            "title": "Clocks, reset and the first instruction",
            "summary": "Nothing you have written so far runs at all until the chip has come out of reset with its flash timing right, and none of the peripherals answer until someone has given them a clock.",
            "concepts": [
                "Every peripheral sits behind a clock gate, and a gated peripheral is not merely slow — it is absent. Its registers read back as zero and its writes go nowhere. Setting the configuration before setting the enable bit is the first bug almost everybody meets, and the symptom is indistinguishable from a wrong address, which is why it costs an afternoon rather than a minute.",
                "The oscillator is a specification, not a preference. An internal RC starts in microseconds and holds perhaps 1% over temperature; a crystal holds tens of parts per million but takes milliseconds to start and needs its two load capacitors. What the clock has to agree with decides which: a UART at 115200 tolerates a couple of percent, USB needs 0.25%, and a clock that has to still be right in a month needs a crystal cut for it.",
                "A PLL is integer arithmetic wrapped around a feedback loop: divide the input by $M$ to make the reference, multiply it by $N$ in the oscillator, divide the result by $P$ on the way out. Each of those has a legal range — the reference must stay inside a window, the oscillator has a minimum and a maximum — and between them they mean some target frequencies are simply not reachable from some crystals.",
                "The core can outrun the flash. Above some frequency the flash needs wait states, and the *order* of the two changes matters: raise the wait states first, then the clock. Do it the other way round and the very next instruction is fetched too quickly to be read correctly, which is a hang with no error message and nothing on the stack to explain it.",
                "Reset is not one event. Power-on, brown-out, the external pin, the watchdog and a software request all arrive at the same vector, and a status register records which one it was. Reading that register at start-up, and keeping a count of what it said, is the difference between knowing why a product restarted in the field and guessing.",
            ],
            "read": [
                {
                    "title": "Zero comes back: clocks, wait states and the first instruction",
                    "minutes": 16,
                    "body": r'''
Single-step this in a debugger:

```c
GPIOA->MODER = 0x00000400;          /* pin 5 as an output */
uint32_t back = GPIOA->MODER;       /* read it straight back */
```

`back` is `0x00000000`.

The address is right — you checked it against the manual and against `&GPIOA->MODER`.
The chip is not in a fault handler. The write executed, the read executed, and the value
did not survive the round trip. Change the pin number, change the value, write it twice:
zero every time.

Nothing is wrong with the two lines. The peripheral they are talking to is not switched
on.

## A gated peripheral is absent, not slow

Every peripheral on a modern microcontroller sits behind a clock gate, and the gate is
off at reset because a block with no clock costs no power. A gated peripheral does not
respond to the bus at all: writes are discarded and reads return zero. It is not running
slowly, and it is not ignoring you selectively. From the core's point of view there is
nothing at that address.

The enable bit is in a different peripheral — the reset-and-clock-control block — with a
different chapter and a different base address, and that is exactly why this costs people
an afternoon rather than a minute. The symptom is indistinguishable from a wrong address,
so the search goes to the address, which is correct, and the actual missing line is
somewhere the GPIO chapter never mentions.

Two habits follow. Enable the clock before touching anything else about a peripheral, as
the first line of its init function. And during bring-up, read a configuration register
back after writing it: it costs two instructions and it distinguishes "not there" from
"wrong value" immediately.

## Where the clock comes from, and why it is a specification

Two sources start a chip. An internal RC oscillator is free, starts in microseconds, and
holds about ±1% over temperature. A crystal costs a part and two load capacitors, takes a
couple of milliseconds to start, and holds tens of parts per million.

Which you need is decided by whatever the clock has to agree with, and the numbers are
not close together. A UART at 115200 tolerates a couple of percent between the two ends.
USB allows the bit clock 0.25%. A clock that has to still be right in a month — a
real-time count, a scheduled wake — needs a crystal cut for it. Against a 0.25%
requirement, ±1% is four times the whole budget, and no amount of multiplication improves
it: a PLL multiplies frequency, and the *fractional* error travels through untouched.

## The PLL is integer arithmetic wrapped round a feedback loop

The loop contains a voltage-controlled oscillator, a divider by $N$ in its feedback path,
and a phase detector comparing the divided output against a reference. The loop settles
where those two agree, so

$$\frac{f_{vco}}{N} = \frac{f_x}{M} \qquad\Longrightarrow\qquad f_{vco} = \frac{N f_x}{M}$$

and an output divider by $P$ makes the system clock $N f_x/(MP)$. Nothing analogue
survives into the answer; it is three integers.

What makes configuring one awkward is that each integer carries a window. The phase
detector needs its reference inside a range — 1 to 2 MHz on the part modelled here. The
oscillator has a minimum and a maximum, 100 to 432 MHz. And the system clock has a
ceiling of its own. Between them, some target frequencies are not reachable from some
crystals at all, and the reliable way to find out is to search:

```python
M_RANGE, N_RANGE, P_CHOICES = range(2, 64), range(50, 433), (2, 4, 6, 8)

def legal(fx, m, n, p):
    ref, vco = fx / m, fx * n / m
    return 1e6 <= ref <= 2e6 and 100e6 <= vco <= 432e6 and vco / p <= 168e6

def best(fx, target):
    win, err = None, None
    for m in M_RANGE:
        for n in N_RANGE:
            for p in P_CHOICES:
                if not legal(fx, m, n, p):
                    continue
                e = abs(fx * n / (m * p) - target)
                if err is None or e < err:
                    win, err = (m, n, p), e
    return win

for fx, target in ((8e6, 168e6), (16e6, 48e6), (25e6, 168e6), (12e6, 100e6)):
    m, n, p = best(fx, target)
    print("%4.0f MHz crystal -> M=%2d N=%3d P=%d gives %7.3f MHz (wanted %.0f)"
          % (fx / 1e6, m, n, p, fx * n / (m * p) / 1e6, target / 1e6))
```

Four lines come out, and all four are exact. An 8 MHz crystal reaches 168.000 MHz with
$M=4$, $N=168$, $P=2$; a 16 MHz crystal reaches the 48.000 MHz that USB wants with
$M=8$, $N=96$, $P=4$; a 25 MHz crystal — an unpromising number — reaches 168.000 MHz by
dividing all the way down to a 1 MHz reference first, $M=25$, $N=336$, $P=2$; and 12 MHz
reaches 100.000 MHz with $M=6$, $N=100$, $P=2$.

The middle value is the one to watch while you read that. With $M=4$ on an 8 MHz crystal
the reference is 2 MHz and the oscillator runs at $2 \times 168 = 336$ MHz, inside its
100-to-432 window. A setting that produced the right *system* clock through an illegal
600 MHz oscillator would not be a setting; it would be a chip that never locks.

## The core can outrun the flash

At 168 MHz the core wants an instruction every 5.95 ns. The flash on the same die has an
access time of about 33 ns, fixed by physics and unaffected by anything you configure.
The gap is bridged with wait states — cycles in which the bus waits — and how many you
need is a division:

$$\text{wait states} = \left\lceil \frac{t_{acc}}{T_{core}} \right\rceil - 1$$

```python
import math

T_ACC = 33.3e-9          # the flash's access time, from the datasheet

for f in (16e6, 30e6, 84e6, 168e6):
    period = 1.0 / f
    ws = max(0, math.ceil(T_ACC / period) - 1)
    print("%6.1f MHz: core period %5.2f ns, flash needs %d wait state(s)"
          % (f / 1e6, 1e9 * period, ws))
```

At 16 MHz the period is 62.50 ns, longer than the flash needs, so zero wait states. At
30.0 MHz the period is 33.33 ns and it is still zero — which is where the familiar "one
more wait state per 30 MHz" rule in the datasheet comes from; it is this same division
with $t_{acc}$ around 33 ns. At 84 MHz the answer is 2, and at 168 MHz it is 5.

Now the part that has no error message. Those two changes — the wait states and the clock
— have an order, and it is **wait states first**. Setting them early costs a handful of
wasted cycles while the part is still running at 16 MHz and nothing else. Setting them
late means the instruction immediately *after* the clock switch is fetched from a flash
that can no longer keep up, and what the core executes is whatever the bus happened to
return. The chip stops, or runs nonsense, with a program counter pointing somewhere
plausible and nothing on the stack to explain it.

The general rule underneath is worth carrying past this module: when two settings must
both change and one order is harmless, do the harmless one first.

## Holding the chip in reset while the board catches up

The last thing that has to be right before the first instruction is that the board around
the processor is ready. The 8 MHz crystal takes about 2 ms to start oscillating; the
sensor on the I²C bus does not answer for 3 ms after its own supply is valid. The
processor, left alone, is running code within microseconds of the rail coming up.

The reset pin releases the core when it rises past $0.7\,V_{DD}$, which on 3.3 V is
2.31 V. A capacitor charging through a resistor from zero follows
$v(t) = V_{DD}(1 - e^{-t/\tau})$ with $\tau = RC$, so the time to reach a fraction $f$ of
the supply is found by rearranging:

$$t = \tau \ln\!\frac{1}{1-f}$$

```python
import math

k = math.log(1.0 / (1.0 - 0.7))
print("the 0.7 V_DD threshold is reached after %.3f time constants" % k)
for r, c in ((100e3, 0.0), (10e3, 100e-9), (10e3, 470e-9), (47e3, 100e-9)):
    tau = r * c
    print("R = %5.0f k, C = %6.1f nF -> tau = %5.2f ms, released after %5.2f ms"
          % (r / 1e3, c * 1e9, 1e3 * tau, 1e3 * k * tau))
```

The constant is **1.204**, so the hold time is about $1.2\,RC$ and the design is one
division. Wanting a 6 ms hold gives $RC = 5$ ms, and the resistor is bounded from above
by leakage: the reset pin can leak up to 1 µA, and across anything larger than 50 kΩ that
alone moves the release point by 50 mV or more, drifting with temperature. So 10 kΩ, and
then $C = 5\,\text{ms}/10\,\text{k} = 500$ nF, of which the stock value is 470 nF.

The four rows show that. 100 kΩ with no capacitor at all releases at 0.00 ms — a resistor
with nothing after it carries no current and drops no voltage, so the pin follows the
rail. 10 kΩ with 100 nF releases after 1.20 ms, which is before the crystal has started.
10 kΩ with 470 nF releases after **5.66 ms**, comfortably inside a 3-to-15 ms window, and
47 kΩ with 100 nF gives an identical answer because it is the same $RC$ product.

## The mistake, and why it is tempting

Configuring a peripheral before enabling its clock, and then debugging the address.

It is tempting because the code reads correctly from top to bottom. Every line is about
GPIO, in the order the GPIO chapter presents them, and the missing line belongs to a
different peripheral entirely. It is tempting again because zero is such a plausible
wrong answer: a wrong address usually reads as zero too, and so does an unmapped region,
so the evidence points at the one thing that is not wrong.

Its twin is raising the clock before the wait states, which is tempting for the opposite
reason — the clock is the interesting change and the wait states feel like housekeeping
to be tidied up afterwards.

## Where these models stop holding

The PLL equation is a ratio and says nothing about time. A PLL takes tens to hundreds of
microseconds to lock, and using its output before the ready flag is set gives an
unspecified frequency to a core you have already told to expect the final one. It also
says nothing about jitter: the output of a PLL is noisier than its reference, which
matters for a converter's sampling instant even when the average frequency is perfect.

The reset model assumes the supply is a step. It is not — the rail rises over some
hundreds of microseconds, and the capacitor charges while it does, so a real board
releases earlier than $1.2\,RC$ suggests. The model also ignores any internal pull-up on
the reset pin, which sits in parallel with your resistor and shortens $\tau$.

The wait-state count is a worst case, not an average. Real parts put a prefetch buffer
and an instruction cache in front of the flash, so straight-line code runs at close to
full speed with five wait states configured, and it is branches and interrupt entries
that pay. That is why a change that shortens a loop can slow a program down.

And reset is not one event. Power-on, brown-out, the external pin, the watchdog and a
software request all arrive at the same vector, and a status register records which one
it was. Reading that register at start-up, and keeping a count of what it said, is the
difference between knowing why a product restarted in the field and guessing.

## What you are about to build

Three exercises, one per section above. The derivation, **From the crystal to the
peripheral, one divider at a time**, walks $f_x$, $M$, $N$, $P$ and the bus divider $Q$
through to how long a 16-bit timer can measure before it wraps — 1.56 ms on the numbers
here, which is why the prescaler in the next module exists. The lab, **Finding a PLL
setting that exists**, asks for the three frequency functions, the four legality rules and
the search above, with a stated tie-break so that the answer is reproducible. And the
build, **Holding reset until the board is ready**, asks you to place the capacitor that
turns a resistor into a delay, with the checks simulating the power-up and measuring when
the pin crosses 2.31 V.
''',
                },
            ],
            "quiz": {
                "title": "Gates, multipliers and the reasons a chip restarts",
                "minutes": 10,
                "questions": [
                    {
                        "q": "You write 0x00000400 into a GPIO port's MODER, read it straight back, and get zero. The address is right and the chip is not in a fault handler. What is the most likely cause?",
                        "opts": [
                            "the register is write-only",
                            "the port's clock enable bit has not been set, so the peripheral is not there to write to",
                            "the pointer is missing `volatile`, so the read was optimised away",
                            "the value needs to be written twice, because the register is double-buffered",
                        ],
                        "a": 1,
                        "why": r'''
A gated peripheral does not respond to the bus at all: writes are discarded and reads
come back as zero. Enabling the clock is a separate write to a completely different
block — the clock controller — and it is the line everybody forgets, because nothing
about the GPIO chapter of the manual mentions it. A missing `volatile` is a real bug
with a different symptom: it makes a *later* read return a stale value the compiler
kept in a register, not a fresh zero from the bus. And it is worth noticing what this
failure mode teaches: reading a register back after writing it, at least during
bring-up, is how you find out.
''',
                    },
                    {
                        "q": "An 8 MHz crystal feeds a PLL configured with $M = 8$, $N = 336$ and $P = 2$. What is the system clock?",
                        "opts": ["336 MHz", "168 MHz", "21 MHz", "42 MHz"],
                        "a": 1,
                        "why": r'''
The input divider makes a 1 MHz reference, the loop multiplies it to
$1 \times 336 = 336$ MHz, and the output divider halves that to **168 MHz**. Each stage
is a plain integer ratio, and the intermediate value matters as much as the answer: the
oscillator itself has a legal range — typically 100 to 432 MHz — so a setting that gives
the right system clock through an illegal 600 MHz oscillator frequency is not a setting,
it is a lock-up. The value 336 MHz is the loop frequency rather than the output, and
21 MHz divides by $M$ twice.
''',
                    },
                    {
                        "q": "A part boots from its 16 MHz internal oscillator and the code switches it to a 168 MHz PLL. The flash needs five wait states above 150 MHz. In which order must the two changes happen?",
                        "opts": [
                            "wait states first, then the clock switch",
                            "clock switch first, then the wait states",
                            "either order, as long as both happen before the first flash access",
                            "they must be written in the same instruction",
                        ],
                        "a": 0,
                        "why": r'''
Wait states first, always. Setting them early costs a few cycles of unnecessary slowness
at 16 MHz and nothing else; setting them late means the instruction *after* the clock
switch is fetched from a flash that can no longer keep up, and what the core executes is
whatever the bus happened to return. The failure has no diagnostics: the chip stops, or
runs nonsense, with a program counter that points somewhere plausible. The general rule
underneath it is worth carrying: when two settings must both change, do the one that is
harmless early first.
''',
                    },
                    {
                        "q": "A design needs USB, whose specification allows the bit clock to be off by 0.25%. Its microcontroller has an internal RC oscillator specified at ±1% over temperature. What follows?",
                        "opts": [
                            "the internal oscillator is fine, since 1% is close to 0.25%",
                            "the internal oscillator can be used if the PLL multiplies it up, because the PLL improves the accuracy",
                            "a crystal is required, because a PLL multiplies the input's error along with its frequency",
                            "the internal oscillator is fine as long as the part is calibrated at room temperature",
                        ],
                        "a": 2,
                        "why": r'''
A PLL multiplies frequency, and the fractional error travels through untouched: 1% in is
1% out, four times the budget. Calibrating at room temperature deals with the part-to-
part spread and not with the drift, which is the part of the ±1% that shows up as a
product that works on the bench and fails in a car. Some parts get round this with a
crystal-less USB mode that trims the RC against the host's own frame timing — which is
not the oscillator being good enough, it is a second control loop being added to make it
good enough.
''',
                    },
                    {
                        "q": "A watchdog is reloaded from inside a timer interrupt that runs every millisecond. What does that arrangement actually prove?",
                        "opts": [
                            "that the main program is making progress",
                            "that interrupts are still being serviced, which they are even if the main loop is stuck forever",
                            "nothing at all, because a watchdog cannot be reloaded from an interrupt",
                            "that the timer is configured correctly, which is the point of the watchdog",
                        ],
                        "a": 1,
                        "why": r'''
It proves the timer interrupt still runs, and nothing else. A main loop blocked forever
on a peripheral that will never answer keeps this watchdog fed indefinitely — the exact
failure the watchdog was fitted to catch. The reload belongs where the evidence of
progress is: at the top of the main loop, or better, after each task has set a flag
saying it has run recently and something has checked that all the flags are set. The
same argument applies to reloading it inside a delay function, which is the other
common way to build a watchdog that cannot fire.
''',
                    },
                    {
                        "q": "The supply on a battery-powered board sags to 2.1 V for a few milliseconds when a motor starts. The part is specified down to 2.7 V. What does the brown-out reset circuit do for you?",
                        "opts": [
                            "it holds the chip in reset while the supply is below the valid range, so the code never executes out of a flash that cannot be read reliably",
                            "it maintains the supply from an internal capacitor until the dip passes",
                            "it slows the clock down so the chip can keep running at 2.1 V",
                            "it does nothing until the supply reaches zero, then restarts",
                        ],
                        "a": 0,
                        "why": r'''
It converts an undefined situation into a defined one. Below the specified supply the
flash may return wrong data and the logic may fail in ways nobody characterised, so
executing at all is the danger — a corrupted write to configuration memory is the
classic result. The brown-out detector holds reset until the rail is valid again and the
program starts cleanly, and the reset-status register then says so, which is how you
find out that the motor and the processor are sharing a supply that cannot support both.
Riding the dip out is a job for a capacitor and a regulator, not for the processor.
''',
                    },
                ],
            },
            "build": {
                "title": "Holding reset until the board is ready",
                "minutes": 24,
                "brief": r'''
This part's reset pin releases the processor when it rises past **0.7 $V_{DD}$**, which
on a 3.3 V board is 2.31 V. The supply itself rises in well under a millisecond, but two
other things on the board are slower: the 8 MHz crystal takes about 2 ms to start
oscillating, and the sensor on the other end of the I²C bus does not answer for 3 ms
after its own supply is valid. So the processor must be held in reset for a while after
power is applied.

On the canvas: the 3.3 V rail on the left, a **100 kΩ** resistor from it towards the
reset pin, and the probe sitting on the reset pin itself. As drawn, the pin follows the
rail immediately — a resistor with nothing after it carries no current and drops no
voltage, so there is no delay at all.

## What the finished network must do

- the reset pin must not reach 2.31 V until at least **3 ms** after power is applied
- it must get there within **15 ms**, so the product starts promptly
- it must end up at the full 3.3 V, not at some fraction of it
- every resistor must be between **1 kΩ and 50 kΩ**: the reset pin's input leakage is
  specified at up to 1 µA, and across anything larger than 50 kΩ that alone moves the
  release point by 50 mV or more, drifting with temperature as leakage does

## Working it out

A capacitor charging through a resistor from zero reaches a fraction $f$ of the supply
at $t = \tau \ln(1/(1-f))$, with $\tau = RC$. For the 0.7 threshold that
logarithm is 1.20, so the hold time is about $1.2\,RC$ — pick the hold you want, divide,
and you have the product $RC$. Then split that product between a resistor the leakage
rule allows and a capacitor you can buy.

The checks simulate the power-up and measure when the pin crosses the threshold, so any
network that lands inside the window passes. Click a component to change its value;
`470n`, `4k7` and `10k` are all understood.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 100000},
                        {"id": "p3", "kind": "OUT", "x": 12, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [12, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 10000},
                        {"id": "p3", "kind": "OUT", "x": 12, "y": 7},
                        {"id": "p4", "kind": "C", "x": 10, "y": 9, "rot": 1, "value": 4.7e-7},
                        {"id": "p5", "kind": "GND", "x": 10, "y": 11},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [12, 7]},
                        {"a": [10, 7], "b": [10, 8]},
                        {"a": [10, 10], "b": [10, 11]},
                    ],
                },
                "checks": [
                    {"name": "reset is still held 3 ms after power is applied", "code": r'''
const TH = 0.7 * 3.3;
const s = c.step(0.03);
let t = null;
for (let i = 0; i < s.v.length; i++) {
  if (s.v[i] >= TH) {
    t = i === 0 ? 0 : s.t[i - 1] + (TH - s.v[i - 1]) / (s.v[i] - s.v[i - 1]) * (s.t[i] - s.t[i - 1]);
    break;
  }
}
c.assert(t !== null,
  'The reset pin never reaches 2.31 V at all within 30 ms. Something is holding it down ' +
  'permanently — check that nothing shunts the pin to ground through a resistor.');
c.assert(t >= 0.003,
  'Reset is released after only ' + c.fmt(t, 's') + ', and the crystal will not have ' +
  'started. A larger RC product delays it further.');
'''},
                    {"name": "and released within 15 ms", "code": r'''
const TH = 0.7 * 3.3;
const s = c.step(0.03);
let t = null;
for (let i = 0; i < s.v.length; i++) {
  if (s.v[i] >= TH) {
    t = i === 0 ? 0 : s.t[i - 1] + (TH - s.v[i - 1]) / (s.v[i] - s.v[i - 1]) * (s.t[i] - s.t[i - 1]);
    break;
  }
}
c.assert(t !== null && t <= 0.015,
  'The processor is still in reset ' + (t === null ? 'after 30 ms' : c.fmt(t, 's') + ' in') +
  '. That is a visible pause before the product does anything; reduce the RC product.');
'''},
                    {"name": "the pin settles at the full supply", "code": r'''
c.close(c.vout(), 3.3, 0.01,
  'the steady voltage on the reset pin. It has to end up at the rail: a network that ' +
  'divides the supply leaves the pin near its threshold, where noise resets the chip');
'''},
                    {"name": "the leakage rule is respected", "code": r'''
const rs = c.values('R');
c.assert(rs.length >= 1, 'The network needs at least one resistor.');
rs.forEach(function (r) {
  c.assert(r >= 1000 * 0.99,
    'A ' + c.fmt(r, 'Ω') + ' resistor draws more from the rail than this needs and makes ' +
    'the capacitor implausibly large. Keep every resistor at 1 kΩ or above.');
  c.assert(r <= 50000 * 1.01,
    'A ' + c.fmt(r, 'Ω') + ' resistor is large enough that the pin\'s 1 µA of input ' +
    'leakage shifts the release threshold. Keep every resistor at 50 kΩ or below.');
});
'''},
                ],
                "hints": [
                    "The missing part is a capacitor from the reset pin down to ground. Until it is there the resistor has nothing to charge and the pin is simply tied to the rail.",
                    "Aim for the middle of the window rather than its edge. A 6 ms hold needs $RC = 6\\,\\text{ms}/1.2 = 5$ ms.",
                    "The 100 kΩ that is already there fails the leakage rule on its own, so it has to change whatever else you do. With 10 kΩ instead, $C = 5\\,\\text{ms}/10\\,\\text{k} = 500$ nF, and the stock value next to it is 470 nF.",
                    "10 kΩ with 470 nF gives $\\tau = 4.7$ ms and a hold of about 5.7 ms — comfortably inside 3 to 15 ms. 47 kΩ with 100 nF gives exactly the same product and passes too.",
                    "If the pin never reaches the threshold at all, look for a second resistor to ground: that makes a divider, and a divider that lands below 2.31 V holds the processor in reset forever.",
                ],
            },
            "derive": {
                "title": "From the crystal to the peripheral, one divider at a time",
                "minutes": 12,
                "vars": ["f_x", "M", "N", "P", "Q"],
                "brief": r'''
Four dividers stand between the crystal and the timer you are trying to configure, and
the reason clock arithmetic goes wrong is almost always that one of them was forgotten
rather than that any of it is hard. So write the chain out once.

$f_x$ is the crystal frequency. $M$ divides it down to the PLL's reference, $N$
multiplies that up inside the loop, $P$ divides the loop's output to make the system
clock, and $Q$ divides the system clock to make the peripheral bus clock.
''',
                "steps": [
                    {
                        "prompt": "The crystal runs at $f_x$, and the PLL's input divider divides it by $M$ to make the reference the loop compares against. Write the reference frequency.",
                        "answer": "\\frac{f_x}{M}",
                        "hint": "Divide, nothing more. This is the frequency the loop's phase detector sees.",
                        "deconstruct": [
                            "A divider by $M$ produces one output cycle for every $M$ input cycles.",
                            "So the reference is $f_x/M$ — for an 8 MHz crystal and $M = 8$, 1 MHz.",
                        ],
                    },
                    {
                        "prompt": "The loop runs its oscillator at $N$ times the reference. Write the oscillator's frequency in terms of $f_x$, $M$ and $N$.",
                        "given": "The reference you have just written is $f_x/M$.",
                        "answer": "\\frac{N f_x}{M}",
                        "hint": "Multiply the previous answer by $N$.",
                        "deconstruct": [
                            "The loop holds its output divided by $N$ equal to the reference.",
                            "So the oscillator runs at $N \\cdot f_x/M$ — with $N = 336$ and a 1 MHz reference, 336 MHz. This is the number that has to stay inside the oscillator's legal range.",
                        ],
                    },
                    {
                        "prompt": "The output divider $P$ turns that into the system clock. Write the system clock in terms of $f_x$, $M$, $N$ and $P$.",
                        "given": "The oscillator runs at $N f_x / M$.",
                        "answer": "\\frac{N f_x}{M P}",
                        "hint": "One more division, by $P$.",
                        "deconstruct": [
                            "Dividing $N f_x / M$ by $P$ gives $N f_x/(M P)$.",
                            "With $f_x = 8$ MHz, $M = 8$, $N = 336$ and $P = 2$ that is 168 MHz.",
                        ],
                    },
                    {
                        "prompt": "The peripheral bus runs at the system clock divided by $Q$, and a 16-bit timer on that bus wraps after 65536 ticks. Write the longest interval that timer can measure without wrapping, in terms of $f_x$, $M$, $N$, $P$ and $Q$.",
                        "given": "A counter ticking at $f$ takes $1/f$ per tick.",
                        "answer": "\\frac{65536 M P Q}{N f_x}",
                        "hint": "Write the peripheral clock first, then invert it and multiply by 65536. Everything on the bottom of a frequency ends up on the top of a time.",
                        "deconstruct": [
                            "The peripheral clock is $N f_x/(M P Q)$.",
                            "One tick therefore takes $M P Q/(N f_x)$ seconds.",
                            "65536 of them take $65536\\,M P Q/(N f_x)$ — which for the numbers above, with $Q = 4$, is 1.56 ms.",
                        ],
                    },
                ],
                "closing": r'''
Put the numbers in and the result is worth remembering: an 8 MHz crystal, multiplied to
168 MHz and divided by 4 for the peripheral bus, gives a 42 MHz timer clock, and a
16-bit counter on it wraps every **1.56 ms**. That is why the prescaler in the previous
module exists. Anything you want to time in milliseconds has to be prescaled before it
reaches the counter, and the two `+1`s from that module attach to the same chain: the
full expression for a timer period is
$(\text{PSC}+1)(\text{ARR}+1)\,M P Q/(N f_x)$, and every symbol in it is a register
field somebody has to set correctly.
''',
            },
            "lab": {
                "title": "Finding a PLL setting that exists",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Configuring a PLL by hand means guessing three integers and checking three ranges, which
is a job for a search. Write the search.

The part modelled here is a common one. Its rules:

- the reference $f_x/M$ must be between **1 and 2 MHz**, inclusive
- the oscillator $f_x N/M$ must be between **100 and 432 MHz**, inclusive
- $M$ is 2 to 63, $N$ is 50 to 432, and $P$ is one of 2, 4, 6 or 8
- the system clock $f_x N/(M P)$ must not exceed **168 MHz**

The functions:

- `vco_input(f_xtal, m)`, `vco_output(f_xtal, m, n)` and `sysclk(f_xtal, m, n, p)` —
  the three frequencies of the chain, in hertz. Ordinary division is fine; these are
  not integers.
- `is_legal(f_xtal, m, n, p)` — `True` when all four rules above hold, including that
  each of `m`, `n` and `p` is one of the allowed values.
- `best_pll(f_xtal, target)` — the `(m, n, p)` whose system clock is closest to
  `target`, searched **`m` ascending, then `n` ascending, then `p` in the order
  (2, 4, 6, 8)**, keeping a candidate only when it is *strictly* better than the best
  found so far. That rule matters: several settings usually hit the same frequency
  exactly, and without a stated tie-break the answer is whichever one your loop happened
  to reach.
- `wait_states(f_hz)` — how many flash wait states this part needs at that frequency:
  0 up to 30 MHz, then one more for each further 30 MHz, to a maximum of 5. So 30 MHz
  needs none, 30.5 MHz needs one, and anything above 150 MHz needs five.

`best_pll` searches about ninety-five thousand combinations, which is a fraction of a
second. Write it as three plain loops; the point of the exercise is the rules, not the
search.
''',
                "files": [{"name": "main.py", "content": r'''
"""Three integers and four rules: configuring a PLL by search."""

VCO_IN_MIN = 1_000_000
VCO_IN_MAX = 2_000_000
VCO_OUT_MIN = 100_000_000
VCO_OUT_MAX = 432_000_000
SYS_MAX = 168_000_000

M_RANGE = range(2, 64)         # 2 .. 63
N_RANGE = range(50, 433)       # 50 .. 432
P_CHOICES = (2, 4, 6, 8)


def vco_input(f_xtal, m):
    """The PLL reference frequency, in hertz."""
    # TODO: the crystal divided by m.
    return 0.0


def vco_output(f_xtal, m, n):
    """The oscillator frequency inside the loop, in hertz."""
    # TODO: the reference multiplied by n.
    return 0.0


def sysclk(f_xtal, m, n, p):
    """The system clock, in hertz."""
    # TODO: the oscillator divided by p.
    return 0.0


def is_legal(f_xtal, m, n, p):
    """True when m, n, p are in range and all three frequency limits hold."""
    # TODO: check m, n and p first, then the reference window, the oscillator
    # window, and the system clock ceiling.
    return False


def best_pll(f_xtal, target):
    """The (m, n, p) whose system clock is closest to `target`."""
    # TODO: three nested loops in the stated order; skip illegal combinations;
    # keep a candidate only when its error is strictly smaller than the best so far.
    return None


def wait_states(f_hz):
    """Flash wait states needed at this system clock: 0 to 5."""
    # TODO: 0 up to 30 MHz, one more per further 30 MHz, capped at 5.
    return 0


if __name__ == "__main__":
    for xtal in (8e6, 12e6, 25e6):
        m, n, p = best_pll(xtal, 168e6) or (0, 0, 0)
        f = sysclk(xtal, m, n, p) if m else 0
        print("%2.0f MHz crystal -> M=%d N=%d P=%d giving %.3f MHz, %d wait states"
              % (xtal / 1e6, m, n, p, f / 1e6, wait_states(f)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Three integers and four rules: configuring a PLL by search."""

VCO_IN_MIN = 1_000_000
VCO_IN_MAX = 2_000_000
VCO_OUT_MIN = 100_000_000
VCO_OUT_MAX = 432_000_000
SYS_MAX = 168_000_000

M_RANGE = range(2, 64)         # 2 .. 63
N_RANGE = range(50, 433)       # 50 .. 432
P_CHOICES = (2, 4, 6, 8)


def vco_input(f_xtal, m):
    """The PLL reference frequency, in hertz."""
    return f_xtal / m


def vco_output(f_xtal, m, n):
    """The oscillator frequency inside the loop, in hertz."""
    return f_xtal * n / m


def sysclk(f_xtal, m, n, p):
    """The system clock, in hertz."""
    return f_xtal * n / (m * p)


def is_legal(f_xtal, m, n, p):
    """True when m, n, p are in range and all three frequency limits hold."""
    if m not in M_RANGE or n not in N_RANGE or p not in P_CHOICES:
        return False
    if not (VCO_IN_MIN <= vco_input(f_xtal, m) <= VCO_IN_MAX):
        return False
    if not (VCO_OUT_MIN <= vco_output(f_xtal, m, n) <= VCO_OUT_MAX):
        return False
    return sysclk(f_xtal, m, n, p) <= SYS_MAX


def best_pll(f_xtal, target):
    """The (m, n, p) whose system clock is closest to `target`."""
    best = None
    best_err = None
    for m in M_RANGE:
        for n in N_RANGE:
            for p in P_CHOICES:
                if not is_legal(f_xtal, m, n, p):
                    continue
                err = abs(sysclk(f_xtal, m, n, p) - target)
                if best_err is None or err < best_err:
                    best_err = err
                    best = (m, n, p)
    return best


def wait_states(f_hz):
    """Flash wait states needed at this system clock: 0 to 5."""
    for i, top in enumerate((30, 60, 90, 120, 150)):
        if f_hz <= top * 1_000_000:
            return i
    return 5


if __name__ == "__main__":
    for xtal in (8e6, 12e6, 25e6):
        m, n, p = best_pll(xtal, 168e6) or (0, 0, 0)
        f = sysclk(xtal, m, n, p) if m else 0
        print("%2.0f MHz crystal -> M=%d N=%d P=%d giving %.3f MHz, %d wait states"
              % (xtal / 1e6, m, n, p, f / 1e6, wait_states(f)))
'''}],
                "hints": [
                    "The three frequency functions are one line each, and each one is the previous one with another factor: `f_xtal / m`, then `* n`, then `/ p`.",
                    "In `is_legal`, check membership before arithmetic — `m not in M_RANGE` — so that a nonsensical `p` is rejected rather than producing a frequency that happens to look reasonable.",
                    "Python's chained comparison reads exactly like the datasheet: `VCO_IN_MIN <= vco_input(f_xtal, m) <= VCO_IN_MAX`.",
                    "In `best_pll`, keep the best error in its own variable and compare with `<`, not `<=`. Using `<=` keeps the *last* equally good candidate rather than the first, and every value in the tests would change.",
                    "`wait_states` is a loop over the boundaries (30, 60, 90, 120, 150) returning the index of the first one the frequency does not exceed, and 5 if it exceeds all of them.",
                ],
                "tests": [
                    {"name": "the three frequencies of the chain", "code": r'''
assert vco_input(8e6, 4) == 2e6, f"8 MHz over 4 is 2 MHz, got {vco_input(8e6, 4)}"
assert vco_input(8e6, 8) == 1e6, f"got {vco_input(8e6, 8)}"
assert vco_output(8e6, 8, 336) == 336e6, f"got {vco_output(8e6, 8, 336)}"
assert sysclk(8e6, 8, 336, 2) == 168e6, \
    f"the canonical 8 MHz to 168 MHz setting, got {sysclk(8e6, 8, 336, 2)}"
assert sysclk(8e6, 8, 336, 4) == 84e6, "the same loop with a bigger output divider"
'''},
                    {"name": "the rules reject what the datasheet rejects", "code": r'''
assert is_legal(8e6, 8, 336, 2), "M=8 N=336 P=2 from an 8 MHz crystal is the stock setting"
assert not is_legal(8e6, 2, 336, 2), \
    "M=2 puts the reference at 4 MHz, outside the 1-2 MHz window"
assert not is_legal(8e6, 4, 432, 2), \
    "M=4 N=432 runs the oscillator at 864 MHz, twice its limit"
assert not is_legal(8e6, 4, 200, 2), \
    "that combination gives a 200 MHz system clock, above the 168 MHz ceiling"
assert not is_legal(8e6, 8, 336, 3), "3 is not one of the allowed output dividers"
assert not is_legal(8e6, 1, 336, 2), "M starts at 2"
'''},
                    {"name": "an 8 MHz crystal reaches 168 MHz exactly", "code": r'''
got = best_pll(8e6, 168e6)
assert got == (4, 168, 2), f"expected (4, 168, 2) under the stated search order, got {got}"
assert is_legal(8e6, *got), "the answer must itself be legal"
assert sysclk(8e6, *got) == 168e6, "and it must be exact, not merely close"
'''},
                    {"name": "a 25 MHz crystal reaches it too, by a different route", "code": r'''
got = best_pll(25e6, 168e6)
assert got == (25, 336, 2), f"expected (25, 336, 2), got {got}"
assert sysclk(25e6, *got) == 168e6, \
    f"25 MHz divided by 25 is a 1 MHz reference, multiplied by 336 and halved; got {sysclk(25e6, *got)}"
'''},
                    {"name": "and lower targets from other crystals", "code": r'''
assert best_pll(16e6, 48e6) == (8, 96, 4), f"got {best_pll(16e6, 48e6)}"
assert sysclk(16e6, 8, 96, 4) == 48e6, "48 MHz exactly, which is what USB needs"
assert best_pll(12e6, 100e6) == (6, 100, 2), f"got {best_pll(12e6, 100e6)}"
assert best_pll(8e6, 84e6) == (4, 84, 2), f"got {best_pll(8e6, 84e6)}"
'''},
                    {"name": "wait states, at the boundaries where they change", "code": r'''
assert wait_states(16e6) == 0, "well under the first boundary"
assert wait_states(30e6) == 0, "30 MHz itself still needs none"
assert wait_states(30.5e6) == 1, "just above it needs one"
assert wait_states(84e6) == 2, f"got {wait_states(84e6)}"
assert wait_states(120e6) == 3 and wait_states(150e6) == 4, "the middle boundaries"
assert wait_states(168e6) == 5, "the top of the range needs five"
'''},
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Polling, interrupts, timers and PWM",
            "summary": "Two ways to notice that something happened, and one peripheral that makes things happen on time.",
            "concepts": [
                "Polling is a loop that reads a flag. Its worst-case latency is one trip round the whole superloop — the *sum* of everything in it, not just the slowest item — so adding an unrelated slow task anywhere in the loop lengthens the deadline for every flag it polls.",
                "An interrupt is the hardware branching the processor into a handler between two instructions. Its latency is a fixed number of cycles for the vector fetch and register save, plus however long any higher-or-equal-priority handler is already running.",
                "An interrupt is not free. The processor stacks registers on entry and unstacks them on exit, and any pipeline it had filled is thrown away — so a handler that does almost nothing still costs tens of cycles.",
                "Because the handler runs between two instructions of the main program, any variable shared between the two is a race. Declaring it `volatile` makes the main program actually re-read it; it does nothing about the read-modify-write in the middle.",
                "The safe pattern is to keep the handler short: set a flag or push one value into a buffer, and let the main loop do the work. Anything longer delays every interrupt below it in priority.",
                "A timer is a counter clocked from the peripheral clock through a **prescaler**. It counts to an auto-reload value and wraps, so the period is $(\\text{PSC}+1)(\\text{ARR}+1)/f_{clk}$, with the two `+1`s there because both registers count from zero.",
                "PWM comes from a compare register: the output is high while the counter is below the compare value and low above it, so the duty cycle is $\\text{CCR}/(\\text{ARR}+1)$. The frequency is fixed by the reload, the duty by the compare, and the two are independent.",
                "A PWM output is a square wave, not a voltage. Averaging it with a low-pass filter turns it into one, and the filter's corner frequency has to be far below the PWM frequency for the ripple to disappear — which is the same trade against response time as any other filter.",
            ],
            "read": [
                {
                    "title": "Three milliseconds late, and nothing in the code changed",
                    "minutes": 15,
                    "body": r'''
Put two channels of a logic analyser on a running board. Channel 1 is a sensor's
data-ready line. Channel 2 is a spare pin that the program toggles the instant it reads
the sensor. Capture two hundred presses of the trigger and measure the gap between the
two edges:

```text
gap between DATA-READY rising and the pin toggling, 200 captures
  shortest    12 us
  median    1590 us
  longest   3150 us
```

The code that reads the sensor takes eleven microseconds. The other three milliseconds
are not spent reading anything. They are spent somewhere else in the program, and the
distribution is flat, which is the tell: a delay caused by work would cluster, and a
delay caused by *waiting your turn* spreads evenly across whatever you are waiting for.

## Polling promises a number, and the number is the whole loop

The program is a superloop. It reads the sensor, runs a control law, repaints a display
and services a console, then goes round again. The flag it polls can be set at any
moment, including one instruction after the poll that missed it — and then the next look
is a full trip away.

So the worst case is not the slowest thing in the loop. It is the sum of everything in
it, because a flag set at the wrong instant waits for all of them:

$$t_{\text{worst}} = \sum_{i} t_i$$

Put the four tasks in and the histogram above stops being mysterious.

```python
LOOP = [
    ("read the sensor", 120),
    ("run the control law", 340),
    ("repaint the display", 2600),
    ("service the console", 90),
]

total = 0
for name, us in LOOP:
    total += us
    print("%-22s %5d us" % (name, us))
print("%-22s %5d us  <- the worst-case wait for any flag" % ("once round the loop", total))

grown = total + 6800
print("add a 6.8 ms card write: %d us, and every deadline in the loop moved with it"
      % grown)
print("an interrupt instead: 12 cycles at 48 MHz = %.2f us" % (1e6 * 12 / 48e6))
```

The total is **3150 µs**, which is the longest gap the analyser found, to the
microsecond. Nothing else needed explaining.

The next line is the property that makes polling dangerous rather than merely slow. Add
a 6.8 ms write to an SD card — an unrelated feature, in an unrelated part of the
program — and the loop becomes 9950 µs. Every deadline in the system has now moved,
including deadlines belonging to code that nobody touched. Polling couples everything to
everything, and the coupling is invisible in the source.

The last line is the alternative. An interrupt is the hardware branching into a handler
between two instructions of whatever was running, and the branch costs about a dozen
cycles for the vector fetch and the register save — a quarter of a microsecond at
48 MHz. That is four orders of magnitude below the loop, and, more usefully, it does not
grow when the loop does.

## An interrupt is not free, and it is not magic

Two costs come with it. The first is the entry and exit: the processor stacks the
caller-saved registers on the way in and unstacks them on the way out, and any work the
pipeline had speculatively started is thrown away, because an interrupt is a branch
nothing predicted. This module's sandbox, **What an interruption costs, drawn as
cycles**, draws that directly — a mispredicted branch opening a three-column hole in an
otherwise clean staircase of instructions. A handler that does nothing at all still pays
for it.

The second cost is that the handler runs *between two instructions of the main program*,
so anything they share is now a race. The classic case is a counter incremented in both
places: `count++` is a read, an add and a store, and a handler landing between the read
and the store has its own increment overwritten. `volatile` does not help, because both
accesses genuinely happen — they interleave badly. Module 7 takes that apart and prices
the fix.

What follows in practice is a rule about size. A handler should do the smallest thing
that cannot wait — store one sample, set one flag — and hand everything else to the
loop, because whatever it does, it does while every interrupt of equal or lower priority
waits.

## A timer counts, and two registers divide

A timer is a counter clocked from the peripheral clock through a prescaler. It counts up
to an auto-reload value and wraps. Both registers count from zero, so a prescaler holding
$\text{PSC}$ divides by $\text{PSC}+1$, and a counter reloading at $\text{ARR}$ visits
$\text{ARR}+1$ distinct values before it comes back round. Two divisions in series:

$$f_{\text{PWM}} = \frac{f_{clk}}{(\text{PSC}+1)(\text{ARR}+1)}$$

PWM comes out of a third register. The output is high while the counter is below the
compare value $\text{CCR}$ and low above it, so out of the $\text{ARR}+1$ ticks in a
period it spends $\text{CCR}$ of them high:

$$D = \frac{\text{CCR}}{\text{ARR}+1}$$

The reload sets the frequency and the compare sets the duty, and neither disturbs the
other. What the reload *does* decide, besides the frequency, is how finely the duty can
be adjusted — one count of $\text{CCR}$ is one step, and there are only $\text{ARR}+1$ of
them. Three settings that all produce 1 kHz at 25% make the point:

```python
F_CLK = 48000000


def pwm(psc, arr, ccr):
    return F_CLK / ((psc + 1) * (arr + 1)), 100.0 * ccr / (arr + 1)


for psc, arr, ccr in ((47, 999, 250), (0, 47999, 12000), (479, 99, 25)):
    f, duty = pwm(psc, arr, ccr)
    print("PSC=%5d ARR=%5d CCR=%5d -> %8.3f Hz at %5.2f %%, one step = %6.4f %%"
          % (psc, arr, ccr, f, duty, 100.0 / (arr + 1)))

slip = F_CLK / (47 * 1000)
print("dividing by PSC rather than PSC+1: %.1f Hz, %+.2f %% off"
      % (slip, 100 * (slip - 1000) / 1000))
```

All three lines report 1000.000 Hz at 25.00%. What separates them is the last column:
$\text{PSC}=47$ with $\text{ARR}=999$ gives duty steps of **0.1000%**, prescaling by
nothing at all and reloading at 47999 gives **0.0021%**, and prescaling hard so that
$\text{ARR}$ is only 99 leaves steps of a whole **1%**. The rule falls out of it — take
the prescaler as low as the reload register's width allows, because every count you throw
away in the prescaler is resolution you cannot get back in the compare.

The fourth line is what happens when the two `+1`s are forgotten. Dividing 48 MHz by 47
instead of 48 gives **1021.3 Hz**, 2.13% high.

## From a square wave to a voltage

A PWM output is not an analogue level; it is a pin slamming between 0 V and 3.3 V. What
makes it usable as one is that its *average* over a period is $D \cdot V_{DD}$, which
follows from the definition of an average: the pin holds 3.3 V for a fraction $D$ of
every period and 0 V for the rest.

Averaging is what a low-pass filter does. Feed the square wave through an RC and the DC
term passes untouched, while the fundamental at $f_{\text{PWM}}$ is attenuated by

$$|H(f)| = \frac{1}{\sqrt{1 + (f/f_c)^2}}, \qquad f_c = \frac{1}{2\pi RC}$$

and the same $RC$ that removes the ripple is the time constant the output takes to reach
a new value. One component choice, two consequences pulling in opposite directions:

```python
import math

F_PWM = 10000.0

print("    R        C      corner    ripple at 10 kHz     tau    98 % after")
for r, c in ((20e3, 8e-9), (20e3, 100e-9), (20e3, 200e-9), (20e3, 1e-6)):
    tau = r * c
    fc = 1.0 / (2 * math.pi * tau)
    att = 1.0 / math.sqrt(1.0 + (F_PWM / fc) ** 2)
    print("%5.0f k  %7.0f nF  %8.2f Hz  %9.3f %%       %6.2f ms  %7.1f ms"
          % (r / 1e3, c * 1e9, fc, 100 * att, 1000 * tau, 4000 * tau))
```

Four rows, one resistor, four capacitors. At 8 nF the corner is 994.72 Hz and **9.898%**
of the 10 kHz fundamental survives — an output that is recognisably a square wave with
rounded corners, not a level. The quiz in this module describes a worse version of the
same failure, with the corner only one octave below the switching frequency. At
100 nF the corner is 79.58 Hz, the ripple is down to 0.796%, and the output reaches 98%
of a new value in 8.0 ms. At 200 nF the ripple halves again to 0.398% and the settling
doubles to 16.0 ms. At 1 µF there is essentially no ripple left and the thing takes
80 ms to respond, which for a control loop is not a filter, it is a lag.

## The mistake, and why it is tempting

Writing the divisor into the prescaler.

The datasheet's prose says "a prescaler value of 48", the register is called `PSC`, and
so 48 goes into it — which divides by 49. The same reflex puts 1000 into `ARR` for a
thousand-tick period. Each `+1` is worth about 0.1% on its own, and both together on the
numbers above give a 2% frequency error.

It is tempting for a reason that has nothing to do with not knowing the rule: on an
oscilloscope, 1021 Hz and 1000 Hz are the same trace. Nothing looks wrong, nothing
reports anything, and the error surfaces only when the timer has to agree with something
external — a servo's pulse window, a UART's bit rate, a real-time count that is a minute
out after a day.

Its relative belongs to the filter. Putting the corner "below the switching frequency"
is the rule everybody remembers, and one octave below is below — which is the 8 nF row,
with a tenth of the input still on the output. Ripple rejection is a matter of *decades*,
not of being on the correct side.

## Where these models stop holding

The polling bound assumes the loop is the only thing running. Add interrupts and the loop
takes longer than the sum of its parts, by an amount that depends on the handlers' share
of the processor — which is the arithmetic the derivation in module 7 sets out.

The interrupt latency of "about a dozen cycles" is the hardware's entry cost and not the
number you can promise. The real bound also contains every higher-priority handler that
could be running first, and the longest stretch anywhere in the program during which
interrupts are switched off. That second term is under your control and invisible in the
source, and it is where deadlines are actually missed.

The PWM equations are exact and the duty is not continuous. $\text{CCR}$ is an integer,
so the achievable duty cycles are a grid of $1/(\text{ARR}+1)$, and a control loop that
asks for a finer adjustment than the grid allows sits between two values and dithers, or
stops moving altogether.

Finally, the filter arithmetic treats the pin as an ideal source and the output as
unloaded. Neither survives contact: the pin has tens of ohms of its own, which add to $R$,
and anything you connect to the output forms a divider with it. That is why the build's
resistor window has a ceiling as well as a floor — a filter made from megohms has the
right corner and no ability to drive what comes next.

## What you are about to build

The sandbox, **What an interruption costs, drawn as cycles**, is the interrupt-entry cost
drawn as a picture: instructions down the page, cycles across it, and the hole that
appears when the processor takes a branch it did not predict. Turn forwarding on and off
and watch which gaps close and which do not — the one that survives is the branch, and an
interrupt is a branch.

The build, **Turning a PWM pin into a voltage**, is the table above turned into a
component. A 10 kHz PWM pin and a 20 kΩ resistor are already on the canvas, and the
resistor has no partner, so the output follows the input at every frequency. Add the
capacitor. Five checks measure what you draw: the slow signal within 2%, the corner
between 60 Hz and 90 Hz, the 10 kHz ripple down by a hundred times, settling to 2% inside
15 ms, and every resistor between 1 kΩ and 100 kΩ. The second row of the table above meets
all five. The third row has half the ripple and fails on both the corner and the settling,
which is the whole exercise: the two requirements are the same number read from opposite
ends, and only a window of values satisfies both.
''',
                },
            ],
            "sandbox": {
                "title": "What an interruption costs, drawn as cycles",
                "visualiser": "pipeline",
                "minutes": 9,
                "initial": {"dep": 3, "fwd": 0, "miss": 1},
                "brief": r'''
This is a processor pipeline: one row per instruction, one column per clock cycle, and
five stages across each row — fetch, decode, execute, memory, write-back. The execute
stage is the highlighted one. When nothing gets in the way, each row starts exactly one
column after the row above it, and the machine retires one instruction per cycle.

The sliders introduce the two things that break that. **Dependent pairs** are
instructions that need a result the previous instruction has not finished producing;
**branch mispredicts** are jumps the processor guessed wrong about and had to undo.
**Forwarding** is the hardware fix for the first of them.

None of this is something you configure. It matters here because it is where the
"tens of cycles" of interrupt overhead come from: an interrupt is a branch the
processor did not predict at all, and the picture shows what an unpredicted branch
does to a pipeline that was running smoothly.
''',
                "notice": [
                    "Read down the left-hand labels as the sandbox opens. Row `i0` starts one column in, `i1` three columns after it, and `i2` three columns after that. Each of those two extra columns is one instruction waiting for a value the one above it has not written back yet.",
                    "Rows `i4` to `i8` step down by a single column each, the way the whole picture would if nothing were wrong. That staircase is the machine working properly, and it is the thing every stall is measured against.",
                    "Set **forwarding** to yes. Both three-column gaps close to one column, so `i0`, `i1` and `i2` now start at columns 1, 2 and 3 — a clean staircase, because the result travels straight from one execute stage to the next without visiting the register file. One gap survives: `i3` still starts three columns after `i2`, and that one is the mispredicted branch, which forwarding cannot help.",
                    "Leave forwarding on and drag **branch mispredicts** from 1 up to 4. The gap at `i3` is joined by one at `i6`, and then nothing further happens: only two of these nine instructions are branches, so the fourth mispredict has nothing to mispredict. The caption's cycle count stops moving at the same point.",
                    "Now set dependent pairs to 0, forwarding off and mispredicts to 0. Every row starts one column after the last, and the caption reads a CPI of 1.44 — thirteen cycles for nine instructions. Those four extra cycles are not waste; they are the time it takes to fill a five-stage pipe, and an interrupt pays them again every time it lands.",
                ],
            },
            "quiz": {
                "title": "Deadlines, races and the timer",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A superloop takes at worst 4 ms to go round, and polls a flag once per pass. What is the worst-case delay between the flag being set and the code noticing?",
                        "opts": ["a few microseconds", "2 ms", "4 ms", "it cannot be bounded"],
                        "a": 2,
                        "why": r'''
4 ms — the flag can be set immediately after the poll, so the next look is a full loop
away. Answering 2 ms averages instead of bounding, and an average is the wrong quantity
for a deadline: a system that meets its deadline on average fails it regularly. The
useful property of polling is that this number is *knowable*, being just the loop's
worst-case execution time; the useful property of an interrupt is that the number is
much smaller and does not grow when you add work to the loop.
''',
                    },
                    {
                        "q": "An interrupt handler increments a shared counter with `count++`, and the main loop does the same. Occasionally a count is lost. What is the cause?",
                        "opts": [
                            "`count` needs to be declared `volatile`",
                            "`count++` is a read, an add and a write, and the interrupt can land between them",
                            "the compiler reorders the increment across the handler",
                            "the counter overflows",
                        ],
                        "a": 1,
                        "why": r'''
The increment is not one operation. The main loop reads `count`, the interrupt fires
and does its own read, add and write, the main loop then adds one to the *stale* value
it is still holding and stores it — and the handler's increment is gone. `volatile`
does not help, because both accesses do happen; they simply interleave badly. The fix
is to make the sequence indivisible: disable interrupts around it, use an atomic
instruction, or arrange for only one side to write. Reaching for `volatile` here is the
most common wrong answer in embedded work, and it makes the bug rarer rather than
absent, which is worse.
''',
                    },
                    {
                        "q": "A timer is clocked at 48 MHz with a prescaler value PSC = 47 and an auto-reload value ARR = 999. What is the PWM frequency?",
                        "opts": ["48 kHz", "1.02 kHz", "1.00 kHz", "48 Hz"],
                        "a": 2,
                        "why": r'''
The prescaler divides by $\text{PSC}+1 = 48$, giving a 1 MHz counter clock, and the
counter then takes $\text{ARR}+1 = 1000$ ticks to wrap, so the period is 1 ms and the
frequency is exactly 1.00 kHz. Both `+1`s are there because a counter that reloads at
999 visits 1000 distinct values, 0 to 999 inclusive. Drop the prescaler's `+1` and you
divide 48 MHz by 47 instead of 48, which gives 1.02 kHz — a 2% error that is invisible
on an oscilloscope and fatal in anything that has to agree with another device about
timing. Drop the reload's `+1` instead and the answer is 1.001 kHz, wrong by only a
tenth of a percent, which is worse in its way: that one hides until something has to
count on it for a long time.
''',
                    },
                    {
                        "q": "With that timer, which compare value CCR gives a 25% duty cycle?",
                        "opts": ["250", "249", "25", "750"],
                        "a": 0,
                        "why": r'''
The duty is $\text{CCR}/(\text{ARR}+1) = \text{CCR}/1000$, so 250 gives exactly 25%.
The `+1` appears here for the same reason as before, and note that it appears in the
denominator only: the compare value itself is a count of ticks spent high, not an index,
so 249 would give 24.9%. The value 750 is the *complement*, which is what you would
need if the output polarity were inverted — a register bit worth checking before
assuming which way round it is.
''',
                    },
                    {
                        "q": "A 1 kHz PWM output feeds an RC low-pass filter with a corner at 500 Hz, intended to produce a steady analogue voltage. What will be seen at the output?",
                        "opts": [
                            "a clean DC voltage proportional to the duty cycle",
                            "nothing — the filter blocks the signal entirely",
                            "a DC level that is wrong by a factor of two",
                            "the right average, buried under a large 1 kHz ripple",
                        ],
                        "a": 3,
                        "why": r'''
The average is correct — a first-order filter passes DC untouched whatever its corner —
but the corner is only one octave below the switching frequency, so the fundamental is
attenuated by barely a factor of two. With $\tau = 318$ µs against a half-period of
500 µs the capacitor nearly finishes charging each way before the pin switches back,
so what appears is a square wave with rounded corners swinging about 2.2 V of the
3.3 V input — recognisably the input, not a level. Making the ripple small needs the
corner *decades* below the PWM frequency, and the cost is response time: the same RC
that removes the ripple also
means the output takes several time constants to reach a new value. That trade is the
whole design, and it is what the next exercise asks you to place numbers on.
''',
                    },
                    {
                        "q": "Which of these belongs inside an interrupt handler on a small microcontroller?",
                        "opts": [
                            "a loop that waits for a second peripheral to become ready",
                            "storing one sample into a buffer and setting a flag",
                            "formatting a message with `printf` and sending it",
                            "a delay of a few milliseconds, to debounce a switch",
                        ],
                        "a": 1,
                        "why": r'''
A handler should do the smallest thing that cannot wait, and hand the rest to the main
loop. Storing a sample and setting a flag is exactly that. The other three all block:
`printf` can take milliseconds and is often not re-entrant, a wait loop inside a handler
holds off every lower-priority interrupt for as long as it spins, and a debounce delay
in a handler wastes time the processor could have spent running the program that the
button press was for. Debouncing belongs to a timer and a state machine in the loop.
''',
                    },
                ],
            },
            "build": {
                "title": "Turning a PWM pin into a voltage",
                "minutes": 26,
                "brief": r'''
A **10 kHz PWM** output has to become a steady analogue control voltage. The pin is on
the left, drawn as a 3.3 V source — for filter design what matters is the response
shape, and that does not depend on the amplitude. A 20 kΩ resistor is already placed
between the pin and the output node, and the probe is on that node.

As drawn, the resistor does nothing at all: with nowhere for current to go, the output
follows the input at every frequency. Add what is missing and give the resistor a
partner.

## What the finished filter must do

- **pass a slow control signal**: at 1 Hz the output must be within 2% of the input
- **have its −3 dB corner between 60 Hz and 90 Hz**
- **cut the 10 kHz ripple by at least a factor of 100** relative to that slow signal
- **settle to within 2% of a new value in 15 ms**, so the loop above it stays usable
- use only resistors between **1 kΩ and 100 kΩ**: below that the pin cannot drive the
  filter, and above it the converter's own input leakage starts to matter

## Working it out

The corner of a first-order RC low-pass is $f_c = 1/(2\pi RC)$, and its step response
rises with time constant $\tau = RC$, reaching 98% of the way in about four time
constants. Those two are the same number seen from opposite ends: pick the corner and
the settling time follows, so check both before you commit.

For the ripple, a first-order filter falls at 20 dB per decade above its corner. A
corner at 100 Hz would put 10 kHz two decades up and cut it by a factor of exactly
100, which is the figure the brief asks for — and landing on a requirement dead level
is not meeting it. That is why the ceiling above is 90 Hz: at 90 Hz the 10 kHz ripple
comes down to 0.9% of the wanted signal, a tenth inside the limit, which leaves the
corner window as the single constraint that decides the answer.

The checks measure the response of whatever you draw. One resistor and one capacitor
is the expected answer; anything else that meets all five requirements passes too.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "rot": 0, "value": 20000},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [11, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "rot": 0, "value": 20000},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 5},
                        {"id": "p4", "kind": "C", "x": 11, "y": 7, "rot": 1, "value": 1e-7},
                        {"id": "p5", "kind": "GND", "x": 11, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [11, 5]},
                        {"a": [11, 5], "b": [11, 6]},
                        {"a": [11, 8], "b": [11, 9]},
                    ],
                },
                "checks": [
                    {"name": "the slow control signal gets through untouched", "code": r'''
const src = c.values('V');
c.assert(src.length === 1, 'One source, standing in for the PWM pin. Found ' + src.length + '.');
const dc = c.gain(1) / src[0];
c.close(dc, 1.0, 0.02,
  'the response at 1 Hz relative to the input — a filter that also attenuates the ' +
  'wanted signal has thrown away the thing it was meant to deliver');
'''},
                    {"name": "the corner lands between 60 Hz and 90 Hz", "code": r'''
const fc = c.corner(1, 200000);
c.assert(fc >= 60 * 0.98,
  'The corner is at ' + c.fmt(fc, 'Hz') + ', below the 60 Hz floor. That filter is ' +
  'slower than the brief allows — a smaller R or C moves the corner up.');
c.assert(fc <= 90 * 1.02,
  'The corner is at ' + c.fmt(fc, 'Hz') + ', above the 90 Hz ceiling, so not enough ' +
  'of the 10 kHz ripple is removed. A larger R or C moves the corner down.');
'''},
                    {"name": "the 10 kHz ripple is cut by at least a hundred times", "code": r'''
const slow = c.gain(1);
const ripple = c.gain(10000);
c.assert(slow > 0, 'Nothing reaches the probe even at 1 Hz.');
const ratio = ripple / slow;
c.assert(ratio <= 0.01,
  'At 10 kHz the output is ' + (ratio * 100).toFixed(2) + '% of the slow-signal level, ' +
  'and the brief asks for 1% or less. Push the corner further below the switching frequency.');
'''},
                    {"name": "a new value settles within 15 ms", "code": r'''
const s = c.step(0.015);
const src = c.values('V')[0];
const settled = s.v[s.v.length - 1] / src;
c.assert(settled >= 0.98,
  'After 15 ms the output has only reached ' + (settled * 100).toFixed(1) + '% of its ' +
  'final value. The filter is too slow for the loop above it — raise the corner.');
c.assert(settled <= 1.02,
  'The output overshoots its final value, which a first-order low-pass cannot do. ' +
  'Check what else is in the signal path.');
'''},
                    {"name": "the pin can drive every resistor you used", "code": r'''
const rs = c.values('R');
c.assert(rs.length >= 1, 'The filter needs at least one resistor.');
rs.forEach(function (r) {
  c.assert(r >= 1000 * 0.99,
    'A ' + c.fmt(r, 'Ω') + ' resistor asks the pin for more current than it has. ' +
    'Keep every resistor at 1 kΩ or above.');
  c.assert(r <= 100000 * 1.01,
    'A ' + c.fmt(r, 'Ω') + ' resistor is high enough that converter input leakage ' +
    'shifts the output. Keep every resistor at 100 kΩ or below.');
});
'''},
                ],
                "hints": [
                    "The missing part is a capacitor from the output node to ground. Without it the resistor has no partner and the network is just a wire.",
                    "Rearrange $f_c = 1/(2\\pi RC)$ into $C = 1/(2\\pi R f_c)$. With the 20 kΩ already placed and a target near 80 Hz, that is about 100 nF.",
                    "Type the value as `100n`. The editor understands the p, n, u, k, M and m suffixes.",
                    "Check the settling before you run: $\\tau = RC = 20\\text{k} \\times 100\\text{n} = 2$ ms, and 15 ms is seven and a half time constants, comfortably inside the 2% requirement.",
                    "If you would rather change the resistor, keep the product $RC$ near $2\\times10^{-3}$ s: 10 kΩ with 200 nF and 47 kΩ with 47 nF both land in the window.",
                ],
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "The vector table, priority and the critical section",
            "summary": "What the hardware does between two instructions when an interrupt arrives, what it costs to make a sequence indivisible, and how to bound the delay before a handler starts.",
            "concepts": [
                "The vector table is an array of addresses at the very bottom of the address space. The first word is not code: it is the value loaded into the stack pointer at reset. The second is the address of the reset handler, and every entry after that belongs to one exception or one peripheral interrupt. An interrupt 'calling' your function is the hardware fetching a word out of this table and branching to it, which is why a handler with the wrong name silently never runs — the table still holds the default entry.",
                "Entry and exit are automatic and are not free. The processor stacks the caller-saved registers and the return address on the way in and unstacks them on the way out, a fixed cost of roughly a dozen cycles each way. That is why splitting work across two handlers pays the cost twice, and why a Cortex-M optimises the case of a second interrupt already waiting: it *tail-chains* straight into it without unstacking and restacking.",
                "Priority is a number, and lower means more urgent. A higher-priority interrupt preempts a running handler; an equal or lower one stays pending and is taken when the current handler returns. Two sources given the same priority can therefore never preempt each other, which is a design tool — it lets them share a buffer with no locking at all.",
                "Worst-case response time is not the entry latency. It is the entry latency, plus every higher-priority handler that can legitimately be running or arrive first, plus the longest stretch anywhere in the program during which interrupts are disabled. The last term is the one you control and the one that is invisible in the source: a critical section inside a library function lengthens the deadline of an interrupt written by somebody else.",
                "A critical section is how a read-modify-write is made indivisible against a handler: save the current interrupt-enable state, disable, do the sequence, restore what you saved. Restore rather than blanket-enable — a function that ends with an unconditional enable, called from inside another critical section, silently opens the outer one. And `volatile` is no substitute: it guarantees that accesses happen, not that a pair of them cannot be split.",
            ],
            "read": [
                {
                    "title": "An array of addresses, and the microseconds nobody wrote down",
                    "minutes": 16,
                    "body": r'''
Open a memory window at address zero on a board that boots, and read the first few words:

```text
00000000   0x20005000
00000004   0x08000141
00000008   0x08000165
0000000C   0x08000165
00000010   0x08000165
```

Two things in that dump are worth stopping over.

The first word is not code and is not an address in flash. `0x20005000` is in SRAM, and
in fact it is the top of it — the processor loads that word into the stack pointer before
executing a single instruction, which is what lets the very first line of the startup
code push a register.

And three consecutive entries hold the same value, `0x08000165`. Three different
exceptions, one handler. Nobody wrote three identical handlers; the linker put the same
default one in every slot that no named function claimed.

## The table is an array, and the index is the exception number

There is no dispatch, no lookup, no comparison. When exception number $n$ fires, the
hardware loads the word at $4n$ and branches to it. That is the whole mechanism, and
everything else about interrupts on this architecture is a consequence of it.

The numbering starts with the system exceptions and continues into the peripheral
interrupts, so peripheral IRQ $k$ is exception $16+k$ and lives at

$$\text{offset} = 4(16 + k)$$

```python
def offset(exception):
    return 4 * exception


for name, exc in (("initial stack pointer", 0), ("Reset", 1), ("NMI", 2),
                  ("HardFault", 3), ("SysTick", 15)):
    print("%-22s exception %2d -> offset 0x%04X" % (name, exc, offset(exc)))
for n in (0, 28, 37):
    print("%-22s exception %2d -> offset 0x%04X" % ("IRQ %d" % n, 16 + n, offset(16 + n)))

stored = 0x08000141
print("a handler at 0x%08X is stored as 0x%08X" % (stored & ~1, stored))
```

The initial stack pointer sits at offset 0 and the reset vector at 4, which is the pair
in the dump. SysTick is exception 15 at **0x003C**, so the peripheral interrupts start
immediately after it at **0x0040**, and IRQ 28 — a timer, on a good many parts — is at
**0x00B0**. If you ever need to know where a vector lives, that multiplication is the
whole answer.

The last line explains the odd address. The handler is at `0x08000140`, an even address
as every instruction must be, and the *stored* word is `0x08000141`. Bit 0 is not part of
the address; it tells the processor to enter in Thumb state. A hand-written table with
the even address in it faults on the first interrupt, and the fault is a
`HardFault` with a `UsageFault` reason that says nothing about vectors.

Now the three identical entries. A handler is bound to a slot by *name*: the startup file
defines every handler as a weak symbol aliased to an infinite loop, and your definition
overrides it if — and only if — the names match. Misspell `TIM2_IRQHandler`, and nothing
warns you. There is no reference to resolve, no link error, no unused-function warning.
The slot keeps the default, the interrupt fires, the chip spins in a loop it never leaves,
and the symptom is that the peripheral is configured perfectly and the handler never runs.
A breakpoint on the first line of the handler that never hits is the fastest way to see it.

## Entry costs cycles, and so does leaving

Taking an interrupt is not a branch. The processor stacks the caller-saved registers and
the return address, fetches the vector, and starts the handler — around a dozen cycles —
and unstacks the same on the way out. That is why splitting one job across two handlers
costs the pair twice, and it is why a Cortex-M optimises the case of a second interrupt
already pending when a handler returns: it *tail-chains* straight into it, skipping the
unstack and the restack entirely.

## Priority is a number, and the small numbers win

A higher-priority interrupt preempts a running handler. An equal or lower one stays
pending and is taken when the current handler returns. The numbers run backwards from
the intuition — priority 1 outranks priority 3 — and that inversion is where most of the
confusion in this subject is planted.

Two consequences are worth carrying. The first is a cost: with several levels in use, the
worst case has one stacked frame per level, all at once, so a stack budget is not the
deepest handler but the sum of them. The second is a tool. Two sources given the *same*
priority can never preempt each other, so a buffer shared between them needs no lock at
all. Choosing priorities is partly a locking decision, not only a timing one.

## The number that is actually missed

Entry latency is a hardware constant and it is not the answer to "will this handler start
in time". The bound has three terms: the entry cost, everything of higher priority that
can legitimately go first, and the longest stretch anywhere in the program during which
interrupts are switched off.

$$R = t_{\text{entry}} + \sum_{j \in \text{higher}} C_j + B_{\text{max}}$$

```python
F_CORE = 48e6


def us(cycles):
    return 1e6 * cycles / F_CORE


ENTRY = 12
AHEAD = (("the ADC handler, 10 kHz", 300), ("the SPI handler", 90))

total = ENTRY
print("%-38s %7.2f us" % ("hardware entry latency", us(ENTRY)))
for name, cyc in AHEAD:
    total += cyc
    print("%-38s %7.2f us" % ("+ " + name, us(cyc)))
for disabled in (0, 200, 1500):
    worst = us(total + disabled)
    print("+ %4d cycles of interrupts-off  -> worst case %7.2f us   %s"
          % (disabled, worst, "inside 20 us" if worst <= 20 else "MISSES 20 us"))
```

Entry is **0.25 µs** and rounds to nothing. The two handlers that can be ahead cost
6.25 µs and 1.88 µs, so with interrupts never disabled the worst case is **8.38 µs**,
comfortably inside a 20 µs deadline. Two hundred cycles of critical section takes it to
12.54 µs, still inside. Fifteen hundred cycles takes it to **39.62 µs** and the deadline
is gone.

Read the last term again, because it is the one that behaves differently from the others.
$B_{\text{max}}$ belongs to whatever code holds the longest critical section anywhere in
the program, which is frequently a library, frequently written by somebody else, and
never visible from the interrupt whose deadline it destroys. Raising the priority does
not help: disabling interrupts is not a priority mechanism, it is an off switch, and the
hardware will not take the interrupt at any priority while it is thrown.

## Making a sequence indivisible, without lengthening everyone else's bound

A critical section is the fix for the race in the previous module — the increment that a
handler lands in the middle of. It has exactly four steps, and the first one is the one
people leave out:

```c
uint32_t primask = __get_PRIMASK();   /* remember whether they were already off */
__disable_irq();
count += 1;                           /* the read-modify-write, now indivisible */
__set_PRIMASK(primask);               /* put back what you found */
```

Save, disable, do the work, *restore*. Restoring rather than enabling is what lets the
function be called from anywhere, including from inside a longer critical section that
somebody else opened, and it is what makes the pattern compose.

## The mistake, and why it is tempting

Ending the section with `__enable_irq()`.

It reads as the natural counterpart of `__disable_irq()`, and on its own it behaves
correctly: interrupts were on, they went off, they came back on. It is tempting because
it is symmetric, because it is one line shorter, and above all because the function is
tested by calling it from the main loop, where it is right.

What it does not do is restore. Called from inside another critical section, it enables
interrupts halfway through somebody else's indivisible sequence, and the outer sequence
is now split at a point its author proved could not be split. The corruption is rare,
timing-dependent, and lives in code that reviews perfectly. That is why every RTOS wraps
critical sections as save-and-restore, and why the intrinsic pair exists at all.

Its relative is reaching for `volatile` when the problem is atomicity. `volatile`
guarantees that every access happens, where the source says, unmerged. It says nothing
about a pair of accesses being inseparable, and adding it to a shared counter makes the
lost-update bug rarer without making it absent — which is worse than leaving it alone,
because it moves the failure out of the tests and into the field.

## Where these models stop holding

The response-time sum above assumes each higher-priority handler goes ahead of you once.
If one of them can fire repeatedly inside your window — a 10 kHz source against a 200 µs
deadline — the term is not $C_j$ but $C_j$ multiplied by how many times it can arrive,
and the honest calculation is a fixed-point iteration rather than a sum. Treat the block
above as the shape of the argument on a lightly loaded system, not as a proof.

Disabling interrupts does not disable everything. A non-maskable interrupt and a
HardFault are taken regardless, which is the point of them. Nor does it stop a DMA
controller, which moves data without asking the core at all: a buffer shared with DMA is
not protected by a critical section, and the mechanisms for it are different.

The utilisation argument in this module's derivation is an *average*. It answers whether
the work fits over a long window and says nothing about the worst case at any instant —
those are two different questions with two different formulas, and using one where the
other belongs is how a system passes a soak test and misses a deadline.

And the RC debounce in the tune unit is an idealisation. A real button charges through
the internal pull-up and discharges through the closed contacts, so the two directions
have different time constants, and the filtered edge crosses the input threshold slowly
enough to sit in the undefined band on the way through — which is what a Schmitt-trigger
input is for, and why the software answer, a timer that ignores further edges for a few
milliseconds, is the more common one in production.

## What you are about to build

The derivation, **What the handlers leave for the main loop**, is four steps from a
handler's cost to the work a deadline can actually hold: a share $C_h/T_h$ per source,
what is left after both, the wall-clock time $W/(1-u)$ that $W$ cycles of loop work then
take, and the budget $D(1-u)$ that follows. Watch what the last one does as $u$ nears 1.

The tune unit, **One press, one interrupt**, is a resistor and a capacitor against three
requirements at once: keep 0.95 of a 10 Hz press, put the 1 kHz bounce 26 dB down, and
hold the time constant under 5 ms so the button still feels immediate. Those pull two
ways, and the window between them is narrower than it looks:

```python
import math

F_PRESS, F_BOUNCE = 10.0, 1000.0

amp = 10.0 ** (-26.0 / 20.0)
lo_keep = F_PRESS / math.sqrt(1.0 / (0.95 * 0.95) - 1.0)
hi_rej = F_BOUNCE / math.sqrt(1.0 / (amp * amp) - 1.0)
lo_tau = 1.0 / (2 * math.pi * 5.0e-3)
print("keep 0.95 of 10 Hz needs a corner above %6.2f Hz" % lo_keep)
print("26 dB down at 1 kHz needs a corner below %6.2f Hz" % hi_rej)
print("a 5 ms time constant needs a corner above %6.2f Hz" % lo_tau)
print("so RC lands between %.2f ms and %.2f ms"
      % (1000 / (2 * math.pi * hi_rej), 1000 / (2 * math.pi * lo_tau)))

print("    R        C     corner    kept at 10 Hz   1 kHz down    tau")
for r, c in ((1000, 100), (10000, 100), (4700, 1000), (10000, 1000)):
    tau = r * c * 1e-9
    fc = 1.0 / (2 * math.pi * tau)
    keep = 1.0 / math.sqrt(1.0 + (F_PRESS / fc) ** 2)
    rej = 20.0 * math.log10(1.0 / math.sqrt(1.0 + (F_BOUNCE / fc) ** 2))
    print("%6d ohm %5d nF %8.2f Hz %10.4f %10.2f dB %7.2f ms"
          % (r, c, fc, keep, rej, 1000 * tau))
```

The three bounds print as **30.42 Hz**, **50.18 Hz** and **31.83 Hz**, so the corner has
to land between about 31.8 and 50.2 Hz, which is a time constant between **3.17 ms and
5.00 ms**. Notice which constraint binds at the bottom: the settling requirement, not the
one about keeping the press.

Then the four rows. The sliders open at 1 kΩ and 100 nF, a corner at 1591.55 Hz, which
passes the press through untouched and attenuates the bounce by 1.45 dB — a filter in
name only. Ten times the resistance reaches −16.07 dB, better and still nowhere near.
4.7 kΩ with 1 µF gives a corner of 33.86 Hz, keeps 0.9591 of the press, puts the bounce
**29.41 dB** down and has a 4.70 ms time constant: all three at once. Ten kilohms with
the same capacitor rejects the bounce better still, at −35.96 dB, and fails the other two.
''',
                },
            ],
            "quiz": {
                "title": "Vectors, priorities and indivisible sequences",
                "minutes": 10,
                "questions": [
                    {
                        "q": "What is stored in the very first word of the vector table, at address 0x00000000?",
                        "opts": [
                            "the address of the reset handler",
                            "the initial value of the stack pointer",
                            "a branch instruction to the startup code",
                            "the address of the first interrupt handler",
                        ],
                        "a": 1,
                        "why": r'''
The initial stack pointer. The processor loads it before executing anything, which is
what lets the very first instruction of the reset handler push a register — there is a
usable stack before a single line of your code has run. The reset handler's *address* is
the second word. Getting these two the wrong way round in a hand-written table produces
a chip that faults immediately on reset with a stack pointer pointing into flash, and it
is worth knowing because the linker script and the startup file are the two places you
will ever have to look at them.
''',
                    },
                    {
                        "q": "A handler at priority 3 is running when an interrupt at priority 1 arrives. What happens?",
                        "opts": [
                            "the priority 1 interrupt preempts it, and the priority 3 handler resumes afterwards",
                            "the priority 1 interrupt waits until the priority 3 handler returns",
                            "the priority 3 handler is abandoned",
                            "the two run alternately, a few instructions at a time",
                        ],
                        "a": 0,
                        "why": r'''
Priority 1 is more urgent than priority 3 — the numbers run the opposite way to the
intuition, and this is where the confusion is usually planted — so it preempts. The
lower-priority handler is not abandoned: its state was stacked on entry to the new one
and it resumes exactly where it stopped. Note what this means for your stack budget,
which is the part that surprises people: with several priority levels in use, the
worst case has one frame stacked per level, all at once.
''',
                    },
                    {
                        "q": "Two interrupt sources are given the same priority. One is running when the other becomes pending. What follows?",
                        "opts": [
                            "the pending one preempts, because equal priorities alternate",
                            "the pending one is taken when the running handler returns, and the two can share data without locking",
                            "an error is raised, because two sources may not share a priority",
                            "whichever has the lower vector number preempts",
                        ],
                        "a": 1,
                        "why": r'''
Equal priority means no preemption in either direction, so the second handler runs only
after the first has returned. That turns into a genuine engineering technique: two
handlers at the same priority are mutually exclusive by construction, so a buffer shared
between *them* needs no critical section at all. The main loop is still not covered — it
runs below every interrupt — so data shared with the loop still does. Choosing
priorities is therefore partly a locking decision and not only a timing one.
''',
                    },
                    {
                        "q": "A utility function protects a shared counter by disabling interrupts at the top and calling `__enable_irq()` at the bottom. What is wrong with it?",
                        "opts": [
                            "nothing, provided the function is short",
                            "interrupts must be disabled with a compiler barrier as well",
                            "called from inside another critical section, it enables interrupts halfway through the outer one",
                            "`__enable_irq()` is slower than restoring the saved state",
                        ],
                        "a": 2,
                        "why": r'''
It does not restore, it asserts. Called on its own the behaviour is right; called from
inside a longer critical section it opens a window in the middle of somebody else's
indivisible sequence, and the resulting corruption is rare, timing-dependent and appears
in code that looks correct. The fix is to read the current state into a local, disable,
and write the local back at the end — which is what the `__get_PRIMASK()` and
`__set_PRIMASK()` pair is for, and why every RTOS wraps critical sections that way. A
compiler barrier is a real requirement too, and it comes for free with the intrinsics.
''',
                    },
                    {
                        "q": "A handler must begin within 20 µs of its interrupt. The core runs at 48 MHz, entry costs 12 cycles, and one function in the main loop disables interrupts for 1500 cycles. Is the deadline met?",
                        "opts": [
                            "yes — 12 cycles at 48 MHz is a quarter of a microsecond",
                            "no — the disabled region alone is 31 µs, which is longer than the whole deadline",
                            "yes, provided the interrupt is given the highest priority",
                            "it cannot be decided without knowing how often the interrupt fires",
                        ],
                        "a": 1,
                        "why": r'''
$1500/48\,\text{MHz} = 31.25$ µs, and that is time during which the hardware will not
take the interrupt at all — no priority level helps, because disabling is not a priority
mechanism, it is an off switch. The entry cost of 12 cycles is 0.25 µs and rounds to
nothing beside it. The deadline is missed by the critical section, in a function that
probably has nothing to do with the interrupt in question, and the fix is to shorten the
section rather than to raise the priority. This is the single most useful reason to know
what your worst-case disabled region is.
''',
                    },
                    {
                        "q": "A 32-bit millisecond counter is incremented in a timer handler and read in the main loop on an 8-bit machine. It is declared `volatile`. Occasionally the loop reads a value that was never in the counter at all. Why?",
                        "opts": [
                            "the counter overflows and wraps",
                            "the read takes four separate byte accesses, and the handler can update the counter between two of them",
                            "`volatile` prevents the compiler from reading the variable at all",
                            "the handler and the loop are using different copies of the variable",
                        ],
                        "a": 1,
                        "why": r'''
A 32-bit value on an 8-bit machine is four loads, and an interrupt between the second and
the third gives you two bytes of the old value and two of the new — a number that never
existed. `volatile` makes every one of those four accesses happen, which is necessary and
nowhere near sufficient. The usual fixes are a critical section around the read, or a
read-twice-and-compare loop that repeats until two consecutive reads agree. The same
tearing happens on a 32-bit machine for anything wider than a word, and for any pair of
variables that have to be consistent with each other.
''',
                    },
                ],
            },
            "tune": {
                "title": "One press, one interrupt",
                "minutes": 10,
                "brief": r'''
An external interrupt is attached to a pushbutton, and every press produces between ten
and fifty of them. Nothing is wrong with the code: the contacts of a mechanical switch
bounce for a few milliseconds as they close, and the edge-triggered input faithfully
reports every one of those edges.

Before writing a line of software to work around that, it is worth pricing the hardware
answer. A resistor and a capacitor at the pin make a low-pass filter, and the two signals
you are trying to separate are far apart: the press itself is an event at a few hertz,
and the bounce is a burst at around a kilohertz.

Two sliders, three things that must hold at once. The filter is modelled here as one
resistor and one capacitor, which is the symmetric idealisation; a real pull-up and
switch charge and discharge through different resistances, and the honest versions of
this circuit either add a Schmitt-trigger input or do the same filtering in software with
a timer.
''',
                "prompt": "Pass the press, remove the bounce, and keep the button feeling immediate.",
                "note": "The corner has to sit between the two, and the time constant decides how "
                        "late the interrupt arrives. All three constraints must hold together.",
                "model": "rc-lowpass",
                "initial": {"r": 1000, "c": 100},
                "constants": {"fsig": 10, "fnoise": 1000},
                "constraints": [
                    {"k": "keep", "label": "at least 0.95 of a 10 Hz press survives", "min": 0.95},
                    {"k": "reject", "label": "1 kHz bounce down by 26 dB or more", "max": -26.0},
                    {"k": "tau", "label": "time constant ≤ 5 ms, so the press still feels instant", "max": 5.0},
                ],
            },
            "derive": {
                "title": "What the handlers leave for the main loop",
                "minutes": 12,
                "vars": ["C_h", "T_h", "C_l", "T_l", "u", "W", "D"],
                "brief": r'''
Interrupts do not run alongside the main loop; they run *instead of* it. So a loop whose
work you have measured on a quiet system takes longer on a busy one, by an amount that
depends only on the handlers' share of the processor. Four steps put that on a page.

Everything here is in cycles. A handler of cost $C_h$ cycles runs once every $T_h$
cycles; a second one costs $C_l$ every $T_l$; $u$ is the share the handlers take between
them; the loop has $W$ cycles of work to do and a deadline of $D$ cycles to do it in.
''',
                "steps": [
                    {
                        "prompt": "One handler costs $C_h$ cycles and runs once every $T_h$ cycles. Write the fraction of the processor's cycles it takes.",
                        "answer": "\\frac{C_h}{T_h}",
                        "hint": "Cycles spent, over cycles available, across one period of the interrupt.",
                        "deconstruct": [
                            "In any window of $T_h$ cycles, exactly $C_h$ of them belong to the handler.",
                            "So the share is $C_h/T_h$ — for a 200-cycle handler every 10000 cycles, 2%.",
                        ],
                    },
                    {
                        "prompt": "A second source costs $C_l$ cycles every $T_l$ cycles. Write the fraction of the processor that is left for the main loop.",
                        "given": "Shares of the processor add, as long as the total stays below 1.",
                        "answer": "1 - \\frac{C_h}{T_h} - \\frac{C_l}{T_l}",
                        "hint": "Start from the whole processor and take both shares away.",
                        "deconstruct": [
                            "The two handlers take $C_h/T_h$ and $C_l/T_l$ of the cycles.",
                            "Everything else is the loop's, so the loop gets $1 - C_h/T_h - C_l/T_l$.",
                            "Note what happens as that approaches zero: the loop does not slow down gracefully, it stops.",
                        ],
                    },
                    {
                        "prompt": "Write the wall-clock time, in cycles, that the loop takes to finish $W$ cycles of work when the handlers take a share $u$ between them.",
                        "given": "The loop advances by only $(1-u)$ cycles of its own work per cycle of wall-clock time.",
                        "answer": "\\frac{W}{1 - u}",
                        "hint": "If you get a fraction of the machine, you need proportionally more wall-clock time. Divide.",
                        "deconstruct": [
                            "In $t$ cycles of wall-clock time the loop gets $(1-u)t$ cycles of work done.",
                            "Setting $(1-u)t = W$ and solving gives $t = W/(1-u)$.",
                            "At $u = 0.5$ the loop takes twice as long; at $u = 0.9$, ten times.",
                        ],
                    },
                    {
                        "prompt": "The loop must complete within a deadline of $D$ cycles of wall-clock time. Write the largest amount of work $W$ that fits.",
                        "given": "You have just shown that $W$ cycles of work take $W/(1-u)$ of wall-clock time.",
                        "answer": "D(1 - u)",
                        "hint": "Set the time you just wrote equal to $D$ and solve for $W$.",
                        "deconstruct": [
                            "The requirement is $W/(1-u) \\leq D$.",
                            "Multiplying both sides by $(1-u)$ gives $W \\leq D(1-u)$.",
                        ],
                    },
                ],
                "closing": r'''
The last line is the one to keep. A budget of $D$ cycles is worth only $D(1-u)$ of your
own code, and $u$ is set by decisions taken elsewhere — an ADC interrupt at 10 kHz whose
handler takes 300 cycles on a 48 MHz part occupies 6.25 µs of every 100 µs, which is
6.25% of the machine gone before your loop starts.

Two warnings about using it. It is an *average*, so it tells you whether the work fits
over a long window and says nothing about the worst case at any instant — that needs the
response-time argument from the concepts above, with the disabled regions in it. And it
assumes the handlers always fit: as $u$ passes 1 the formula returns a negative number,
which is the arithmetic's way of reporting that the interrupts alone now need more than
the whole processor, and that no main loop exists at all.
''',
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Asynchronous serial: the frame, the baud rate and the error budget",
            "summary": "Two wires, no clock, and a receiver that has to work out where every bit is from a single falling edge.",
            "concepts": [
                "Asynchronous means the clock is not on the wire. The line idles high, a start bit takes it low, and the receiver — running at its own nominally identical rate, usually oversampling sixteen times — uses that one edge to place its sampling points in the middle of each bit that follows. Everything the standard specifies is there to make that placement survive.",
                "A frame is start, then the data **least significant bit first**, then an optional parity bit, then one or two stop bits. `8N1` puts ten bits on the wire for eight bits of payload, so the byte rate is the baud rate divided by ten and not by eight — 11520 bytes per second at 115200 baud, before any protocol of your own takes its share.",
                "The baud rate comes from an integer divider off the peripheral clock, so what you get is $f_{clk}/\\text{DIV}$ rather than what you asked for. The error that matters is the accumulated one: the sampling point drifts by the fractional error on every bit, and the middle of the stop bit is 9.5 bit times from the start edge, so an error of $e$ has become $9.5e$ of a bit by the time the frame ends. Half a bit is where the sample lands in the wrong bit, and both ends contribute, which is where the familiar 2% budget comes from.",
                "The three errors a UART reports mean three different things. **Framing**: the stop bit was not high, which nearly always means the two ends disagree about the baud rate. **Parity**: an odd number of bits changed, and an even number is invisible. **Overrun**: the data register was not read before the next byte arrived, and a byte that was received correctly has been lost — a software failure, not a wiring one.",
                "A logic-level UART is not RS-232. RS-232 idles at about −12 V and inverts the data, so connecting one directly to a 3.3 V pin destroys the pin. Between two boards sharing a supply, two wires and a common ground are enough; across a room, or between separately powered boxes, the ground is no longer common and the link needs a transceiver, or an isolator.",
            ],
            "read": [
                {
                    "title": "One falling edge, and nine and a half bit times of trust",
                    "minutes": 16,
                    "body": r'''
Send the single character `A` — `0x41` — down a serial link at 115200 baud and capture the
line with a logic analyser:

```text
     ____        _____________________        ____________
 ____|   |______|                     |______|
       t = 0                             8.68 us per division
```

Ten divisions of 8.68 µs, and reading the line left to right the pattern is
`0 1 0 0 0 0 0 1 0 1`. Strip the first and last and eight bits remain: `1 0 0 0 0 0 1 0`,
which read as a binary number is `0x82`.

`0x41` went in. `0x82` is on the wire. Nothing is broken — the link works, the far end
recovers an `A` — and the two numbers are bit-reversals of each other, which is the first
thing this module has to explain.

## There is no clock on the wire, so the receiver has to invent one

Asynchronous means what it says: the two devices share no timing signal. The line idles
high; a start bit takes it low; and that single falling edge is the only synchronisation
the receiver will ever get for the whole frame. From it, and from its own idea of how long
a bit lasts, it places its sampling points:

$$t_k = \left(k + \tfrac{1}{2}\right) T_{\text{bit}}, \qquad T_{\text{bit}} = \frac{1}{\text{baud}}$$

The half is what matters. Sampling in the middle of a bit rather than at its edge is what
buys tolerance: the sample can drift by nearly half a bit in either direction before it
lands in a neighbour. Real receivers oversample the line sixteen times per bit and take
three samples around the centre, which also gives them a way to reject a glitch, but the
geometry is the one above.

Now the bit order. The transmitter shifts the byte out of a shift register, and a shift
register gives up its least significant bit first — so `d0` goes first and `d7` last. The
analyser draws time left to right, and we write numbers most significant digit first, so
the two conventions run in opposite directions and the trace looks backwards. It is not
backwards; it is a number written in the order a shift register produces it.

```python
def frame(byte, stops=1):
    bits = [0]
    for i in range(8):
        bits.append((byte >> i) & 1)
    bits.extend([1] * stops)
    return bits


f = frame(0x41)
print("0x41 is %s, and one 8N1 frame of it is" % format(0x41, "08b"))
print("   " + "  ".join(str(b) for b in f))
print("   S  b0 b1 b2 b3 b4 b5 b6 b7 T")
naive = 0
for b in f[1:9]:
    naive = (naive << 1) | b
print("reading those eight left to right as a number gives 0x%02X" % naive)
print("ten bits carry eight, so 115200 baud is %d bytes/s and one frame is %.2f us"
      % (115200 // 10, 1e6 * 10 / 115200))
```

The frame prints as `0 1 0 0 0 0 0 1 0 1`, which is the capture, and reading it the wrong
way gives **0x82**, which is the puzzle at the top of this reading dissolved.

The last line carries a fact worth more than it looks. `8N1` puts **ten** bits on the wire
for eight of payload, so the byte rate is the baud rate divided by ten: 115200 baud is
**11520 bytes per second**, not 14400. The start and stop bits are 20% overhead and they
do not go away, and one whole frame occupies **86.81 µs** — a number to keep, because it
is how long your software has to collect a byte before the next one lands on top of it.

## The divider, and the error it cannot avoid

The peripheral makes its bit clock by dividing the peripheral clock by an integer. You ask
for a baud rate; the hardware gives you $f_{clk}/\text{DIV}$, and the two agree only when
the division happens to come out whole.

$$\text{DIV} = \operatorname{round}\!\left(\frac{f_{clk}}{\text{baud}}\right), \qquad
e = \frac{f_{clk}/\text{DIV} - \text{baud}}{\text{baud}}$$

```python
def divisor(f_clk, baud):
    d = int(f_clk / baud + 0.5)
    return d if d >= 1 else 1


for f_clk in (48e6, 8e6, 1e6, 72e6):
    d = divisor(f_clk, 115200)
    actual = f_clk / d
    err = 100.0 * (actual - 115200) / 115200
    print("%5.1f MHz: DIV = %4d -> %9.1f baud, error %+6.2f %%" % (f_clk / 1e6, d, actual, err))
```

Four clocks, four different answers to the same request. A 48 MHz clock wants a divider of
416.667 and gets 417, so the rate lands at 115107.9 baud, **−0.08%** low — and note the
sign, because the divider is underneath: rounding it *up* makes the rate *lower*. An
ordinary 8 MHz clock gives a divider of 69 and **+0.64%**. A 1 MHz internal oscillator
gives a divider of **9**, and with an integer that small the reachable rates are far apart:
9 gives 111111 baud and 8 would give 125000, with nothing in between, so the error is
**−3.55%**. And 72 MHz divides by exactly 625 and has no error at all, which is why
peripheral clocks get chosen with serial rates in mind rather than for roundness.

Rounding rather than truncating is not a detail. Truncating 416.667 to 416 gives +0.16%
where rounding gives −0.08%, so a cast to `int` doubles the error for nothing.

## Where the error goes: nine and a half bit times

A per-bit error of a fraction of a percent sounds harmless, and taken one bit at a time it
is. The trouble is that every sampling point is measured from the *same* start edge, so
the error does not reset — it accumulates across the frame, and the last sample is the
worst placed.

The middle of the stop bit of an 8N1 frame is 9.5 bit times after the start edge: one
half-bit into the start bit, eight bits of data, and half of the stop bit. So a fractional
rate error $e$ has become $9.5e$ of a bit by the time the receiver checks the stop bit, and
both ends contribute their own:

$$9.5\,(|e_{rx}| + |e_{tx}|) < \tfrac{1}{2}$$

```python
STOP = 9.5

for e_rx, e_tx in ((0.08, 0.0), (0.64, 1.0), (3.0, 2.0), (3.55, 2.0)):
    drift = STOP * (e_rx + e_tx)
    print("receiver %4.2f %% + transmitter %4.2f %% -> %5.1f %% of a bit by the stop bit  %s"
          % (e_rx, e_tx, drift, "ok" if drift < 50 else "FRAMING ERRORS"))
print("so the two ends together have %.2f %% to share" % (50.0 / STOP))
```

The 48 MHz part against a perfect transmitter drifts 0.8% of a bit and is not doing
anything interesting. The 8 MHz part against a transmitter that is 1% out reaches 15.6%,
still comfortable. A 3% receiver against a 2% transmitter reaches **47.5%** — it works,
and it works with nothing left over, so it fails the first time temperature moves either
crystal. Push the receiver to 3.55% and the total is **52.7%**: the stop-bit sample has
crossed into the next bit and the link reports framing errors on nearly every byte.

The last line is the rule the whole subject is usually reduced to. The two ends together
have **5.26%** to share, which is where the familiar "2% each" budget comes from, with the
rest kept back for temperature and part spread.

## Three errors, three different accusations

When a link goes wrong the peripheral names the failure, and the three names mean genuinely
different things.

**Framing** means the stop bit was not high where the receiver looked. That is the
arithmetic above going wrong, so it accuses the bit timing — and the first thing to doubt
is not the configured baud rate but the *peripheral clock the divider was computed from*.
If the PLL did not lock, or the bus prescaler is not what the header assumes, the constant
is wrong and every rate derived from it is wrong with it. Repeatable wrong values are the
signature; random corruption points at noise instead.

**Parity** means an odd number of bits changed. An even number is invisible, which is the
honest limit of a single parity bit: it detects, it does not correct, and it misses half
of everything that could go wrong.

**Overrun** means a byte arrived before the previous one had been read out of the data
register. Every byte on the wire was perfect and one of them was thrown away inside your
own chip — because a handler was slow, or a higher-priority one was ahead of it, or
interrupts were disabled somewhere for longer than the 86.81 µs a frame takes. That is a
latency failure, and the response-time argument from module 7 is what bounds it.

## The mistake, and why it is tempting

Shifting the byte out most significant bit first.

It is what writing looks like. You have `0x41`, you write it `0100 0001`, and you send it
in the order you wrote it — and it is reinforced by the analyser trace at the top of this
reading, which appears to show exactly that.

What makes it survive is the test people run. A single byte, checked by eye, chosen from
the small set that happens to be a palindrome in binary: `0x00`, `0xFF`, `0x18`, `0x3C`.
Every one of those round-trips perfectly through a bit-reversed codec. It is only when
arbitrary data goes through that the received byte turns out to be the bit-reversal of the
sent one — `0x41` arriving as `0x82` — and the symptom looks so much like a timing fault
that the search goes to the baud rate, where there is nothing wrong.

The test that catches it in one line is the round trip over all 256 values, which is the
last test of this module's lab, and it is the only kind of test worth writing for a codec.

The related slip is a data-rate budget divided by eight. Ten bits carry eight, so
`115200/8 = 14400` bytes per second is 25% optimistic, and the overhead it forgets is
sitting in plain sight on the wire.

## Where these models stop holding

The accumulation argument assumes 8N1. Add a parity bit or a second stop bit and the frame
is longer, the last sample is further from the start edge, and the tolerance shrinks —
9.5 becomes 10.5 or 11.5, and a 5% budget becomes 4.3%. Send nine data bits and it moves
again.

The two errors are treated above as constants that add, which is a worst case rather than
a description. Crystal error is roughly constant; an internal RC drifts with temperature
and supply during the very minutes a product warms up, so a link that passes on the bench
can fail after twenty minutes in a case.

The whole of this reading is about *timing* and says nothing about *levels*. A UART frame
is only recoverable if the receiver reads a 1 as a 1, and a signal arriving through a
divider and a metre of cable takes real time to get there. If the edge has not settled by
the time the sample is taken, the timing arithmetic was irrelevant. That is the design
problem this module's build sets.

And a logic-level UART is not RS-232. RS-232 carries the same frame at ±5 to ±12 V with the
sense inverted, so wiring one to a 3.3 V pin puts voltages above the supply and below
ground onto it and the protection diodes conduct until something gives. Two boards sharing
a supply need two wires and a common ground; two separately powered boxes do not have a
common ground at all, and the link needs a transceiver or an isolator.

## What you are about to build

Three exercises, one per section above.

The build, **A 5 V talker and a 3.3 V listener**, is the levels problem: a 5 V transmit
pin, a 3.3 V input, and 1 nF of cable already on the canvas that you may not delete. Two
resistors set the level and the *pair* of them in parallel sets the speed, so the ratio and
the time constant are not independent choices. The budget is 1.7 µs to cross 2.0 V — a
fifth of the 8.68 µs bit, so the level is long settled before the receiver samples at
4.34 µs.

The fill-in drill, **The baud divider, and where the error goes**, is the second and third
blocks above done by hand on three clocks, ending at the 33.7% of a bit that the 1 MHz part
has drifted by the stop bit.

The lab, **A frame on the wire, and a divider that misses**, asks for `parity_bit`,
`frame`, `decode`, `divisor` and `error_pct`. `frame` and `decode` are the pair to watch:
feeding one into the other has to return the byte you started with for all 256 values, and
`decode` has to reject what a receiver rejects — a wrong length, a start bit that is not 0,
a stop bit that is not 1, a parity bit that does not match. That last rejection is a
framing error, written out in Python.
''',
                },
            ],
            "quiz": {
                "title": "What is on the wire, and how far it can drift",
                "minutes": 10,
                "questions": [
                    {
                        "q": "The byte 0x41 is sent as 8N1. Reading the line from the first bit to the last, what appears?",
                        "opts": [
                            "0 0 1 0 0 0 0 0 1 1",
                            "0 1 0 0 0 0 0 1 0 1",
                            "1 1 0 0 0 0 0 1 0 0",
                            "0 1 0 0 0 0 0 1 1",
                        ],
                        "a": 1,
                        "why": r'''
0x41 is `0100 0001`, and the data goes out least significant bit first, so the eight data
bits are 1, 0, 0, 0, 0, 0, 1, 0 — wrapped in a low start bit at the front and a high stop
bit at the end. Sending it most significant bit first gives a completely different
waveform and is what a bit-banged implementation produces when the shift goes the wrong
way; the received byte is then the bit-reversal of the one sent, which is 0x82 here, and
looks like a baud rate problem until you write the bits out.
''',
                    },
                    {
                        "q": "A link runs at 115200 baud, 8N1, with no gaps between frames. What is the highest sustained data rate?",
                        "opts": ["14400 bytes/s", "11520 bytes/s", "115200 bytes/s", "10472 bytes/s"],
                        "a": 1,
                        "why": r'''
Ten bits carry eight, so $115200/10 = 11520$ bytes per second. Dividing by eight gives
14400 and quietly ignores the start and stop bits, which is how a data-rate budget ends
up 25% optimistic — the overhead is not small and it does not go away. Adding a parity
bit makes it eleven bits per byte and 10472 bytes per second, which is the figure for
8E1 rather than 8N1.
''',
                    },
                    {
                        "q": "A receiver's clock is 3% fast and the transmitter's is 2% slow. Which part of an 8N1 frame goes wrong first?",
                        "opts": [
                            "the start bit, because it is sampled first",
                            "the stop bit, because the sampling error accumulates from the start edge",
                            "the least significant data bit, because it is closest to the start edge",
                            "no part of it — 5% is within the tolerance of any UART",
                        ],
                        "a": 1,
                        "why": r'''
Every sampling point is measured from the one start edge, so the error grows through the
frame and the last bit is the worst placed. The middle of the stop bit is 9.5 bit times
out, and $9.5 \times 5 = 47.5$% of a bit — just inside the half-bit at which the
sample crosses into the neighbouring bit. So this link works, marginally, and fails as
soon as anything else moves: temperature, a different part with the same nominal clock,
or one more stop bit's worth of frame. The failure appears as framing errors, which is
the receiver saying "the stop bit was not where I looked".
''',
                    },
                    {
                        "q": "A peripheral reports a framing error on nearly every byte, and the received values are wrong but repeatable. What is the first thing to check?",
                        "opts": [
                            "the parity setting on both ends",
                            "the baud rate — including what the peripheral clock actually is, rather than what the configuration assumes",
                            "the flow control wiring",
                            "the length of the cable",
                        ],
                        "a": 1,
                        "why": r'''
A framing error is the stop bit not being high where the receiver looked, and the usual
cause is a disagreement about bit timing. The trap in the wording is *what the peripheral
clock actually is*: the divider is computed from a constant in the code, and if the PLL
did not lock, or the peripheral bus prescaler is not what the header assumes, that
constant is wrong and every derived baud rate is wrong with it. Repeatable wrong values
are the signature — random corruption points at noise or a floating line instead. Parity
is not it: a parity error is reported separately, and would not shift the framing.
''',
                    },
                    {
                        "q": "An interrupt-driven receiver reports an overrun. What has happened?",
                        "opts": [
                            "a byte arrived before the previous one had been read out of the data register, and is lost",
                            "the transmit buffer in software has filled up",
                            "more than 256 bytes were received in one burst",
                            "the sender ignored the flow-control line",
                        ],
                        "a": 0,
                        "why": r'''
The peripheral holds one received byte, occasionally two, and if nothing reads it before
the next frame completes, the new one has nowhere to go. Every byte arrived perfectly;
one of them was thrown away inside your own chip, because a handler was too slow, or was
blocked by a higher-priority one, or interrupts were disabled somewhere for longer than
a byte time — 87 µs at 115200 baud. Ignoring flow control can *cause* an overrun, but the
error itself is about your latency and not about the wire, which is why the fix is a
shorter path from interrupt to buffer rather than a better cable.
''',
                    },
                    {
                        "q": "A 3.3 V microcontroller UART is wired directly to a PC's nine-pin RS-232 port. What happens?",
                        "opts": [
                            "it works, since both are serial at the same baud rate",
                            "it works but only in one direction",
                            "the RS-232 line idles near −12 V and swings to +12 V, which is outside the pin's ratings in both directions",
                            "nothing at all happens, because the signals are inverted",
                        ],
                        "a": 2,
                        "why": r'''
RS-232 is a different electrical standard that happens to carry the same frame. It idles
at a negative voltage, inverts the sense of the bits, and swings ±5 to ±12 V — so the pin
sees voltages beyond its supply in one direction and below ground in the other, and the
protection diodes conduct until something fails. The inversion is real too, and on its
own would leave you with a permanent framing error. A transceiver chip does both jobs:
it shifts the levels and inverts the sense.
''',
                    },
                ],
            },
            "build": {
                "title": "A 5 V talker and a 3.3 V listener",
                "minutes": 26,
                "brief": r'''
A sensor board's transmit pin swings to **5 V**, and it has to be read by a 3.3 V input
running at **115200 baud**. The pin is drawn here as the 5 V source on the left. A
1 nF capacitor is already on the canvas between the input node and ground: that is the
cable and the pin's own capacitance, it is not yours to choose, and it is the reason
this is a design problem rather than a division.

A 10 kΩ resistor is placed between the source and the input, which on its own does
nothing useful — with nowhere else to go, the input just follows the transmitter to 5 V.

## What the finished circuit must do

- the steady high level at the input is between **2.4 V and 3.2 V**: clear of the 2.0 V
  the input needs to read a 1, and clear of the 3.3 V supply above which the pin's
  protection diodes start conducting
- the input reaches 2.0 V within **1.7 µs** of the transmitter going high — one bit at
  115200 baud is 8.68 µs, the receiver takes its sample in the middle of it at 4.34 µs,
  and a fifth of a bit is the settling budget this design is held to so that the level
  is long since steady when that sample is taken
- the transmitter is asked for no more than **5 mA**
- every resistor is between **220 Ω and 100 kΩ**

## Working it out

Two resistors set the level, and the *pair* sets the speed: what charges the capacitor is
the two of them in parallel, because as far as a rising edge is concerned the supply and
ground are both fixed voltages. So the ratio decides the level and the parallel
combination decides the time constant, and making the ratio right with two large
resistors gives the right voltage far too slowly.

An RC network reaching a final value $V_f$ crosses a threshold $V_t$ at
$t = \tau \ln(V_f/(V_f - V_t))$, with $\tau$ the parallel resistance times 1 nF.

The checks measure the circuit, so any pair that meets all four requirements passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5.0},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "rot": 0, "value": 10000},
                        {"id": "p3", "kind": "OUT", "x": 13, "y": 5},
                        {"id": "p4", "kind": "C", "x": 11, "y": 7, "rot": 1, "value": 1e-9},
                        {"id": "p5", "kind": "GND", "x": 11, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [13, 5]},
                        {"a": [11, 5], "b": [11, 6]},
                        {"a": [11, 8], "b": [11, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5.0},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "rot": 0, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 13, "y": 5},
                        {"id": "p4", "kind": "C", "x": 11, "y": 7, "rot": 1, "value": 1e-9},
                        {"id": "p5", "kind": "GND", "x": 11, "y": 9},
                        {"id": "p6", "kind": "R", "x": 9, "y": 7, "rot": 1, "value": 1500},
                        {"id": "p7", "kind": "GND", "x": 9, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [13, 5]},
                        {"a": [11, 5], "b": [11, 6]},
                        {"a": [11, 8], "b": [11, 9]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 8], "b": [9, 9]},
                    ],
                },
                "checks": [
                    {"name": "the steady high level is inside the input's window", "code": r'''
const v = c.vout();
c.assert(v >= 2.4,
  'The input sits at ' + c.fmt(v, 'V') + ', which leaves almost no margin above the ' +
  '2.0 V the pin needs to read a 1. Take less of the 5 V away.');
c.assert(v <= 3.2,
  'The input sits at ' + c.fmt(v, 'V') + ', at or above the 3.3 V supply, so current ' +
  'flows into the pin\'s protection diode. Divide the 5 V down further.');
'''},
                    {"name": "the edge arrives inside a fifth of a bit", "code": r'''
const s = c.step(1.7e-5);
let t = null;
for (let i = 0; i < s.v.length; i++) {
  if (s.v[i] >= 2.0) {
    t = i === 0 ? 0 : s.t[i - 1] + (2.0 - s.v[i - 1]) / (s.v[i] - s.v[i - 1]) * (s.t[i] - s.t[i - 1]);
    break;
  }
}
c.assert(t !== null,
  'The input never reaches 2.0 V at all, so the receiver sees a permanent zero.');
c.assert(t <= 1.7e-6,
  'The input takes ' + c.fmt(t, 's') + ' to pass 2.0 V, against a settling budget of ' +
  '1.7 µs — a fifth of the 8.68 µs bit. Lower resistances charge the 1 nF faster.');
'''},
                    {"name": "the transmitter is not overloaded", "code": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; });
c.assert(src.length === 1, 'One source, the 5 V transmitter. Found ' + src.length + '.');
const i = Math.abs(c.dc().currents[src[0].id]);
c.assert(i <= 5e-3 * 1.01,
  'The network draws ' + c.fmt(i, 'A') + ' from the transmitter, over the 5 mA budget. ' +
  'Larger resistances draw less.');
'''},
                    {"name": "the cable is still on the input, and the resistors are buyable", "code": r'''
const cs = c.values('C');
c.assert(cs.length === 1 && Math.abs(cs[0] - 1e-9) <= 1e-11,
  'The 1 nF is the cable and the pin. Deleting or changing it does not make the real ' +
  'circuit faster, it only stops the checks measuring what the real one does.');
const rs = c.values('R');
c.assert(rs.length >= 1, 'The level has to come from somewhere.');
rs.forEach(function (r) {
  c.assert(r >= 220 * 0.99, 'A ' + c.fmt(r, 'Ω') + ' resistor is below the 220 Ω floor.');
  c.assert(r <= 100000 * 1.01, 'A ' + c.fmt(r, 'Ω') + ' resistor is above the 100 kΩ ceiling.');
});
'''},
                ],
                "hints": [
                    "The missing part is a second resistor, from the input node down to ground. Without it there is no divider and no current, so the node simply sits at 5 V.",
                    "Take the level first: $5 \\times R_2/(R_1 + R_2)$ has to land between 2.4 and 3.2 V, so the ratio $R_2/(R_1+R_2)$ is between 0.48 and 0.64. A ratio of 0.6 gives exactly 3.0 V.",
                    "Now the speed. The capacitor charges through $R_1$ and $R_2$ in parallel, so with 1 nF the parallel resistance must be about 1.5 kΩ or less to cross 2.0 V inside 1.7 µs.",
                    "1 kΩ over 1.5 kΩ gives 3.0 V, a parallel resistance of 600 Ω, and an edge that passes 2.0 V in 0.67 µs — with 2 mA drawn from the transmitter.",
                    "2.2 kΩ over 3.3 kΩ keeps the same ratio and still passes, at 1.47 µs. 4.7 kΩ over 6.8 kΩ has the level right and takes 3.2 µs, which is where a divider that looks perfectly sensible on paper starts corrupting bytes.",
                ],
            },
            "blanks": {
                "title": "The baud divider, and where the error goes",
                "minutes": 9,
                "caption": "the same sum on three different peripheral clocks",
                "lang": "text",
                "brief": r'''
The configuration line for a UART is one division and one rounding, and everything that
goes wrong with a serial link that is wired correctly is in the rounding. Below is that
calculation on three parts: one with a clock chosen for serial work, one with an
ordinary crystal, and one running from an internal oscillator.

Fill the holes in order. Each is one step from the line above it.
''',
                "listing": r'''
peripheral clock 48.000 MHz, wanted 115200 baud, integer divider only
---------------------------------------------------------------------

  the divider the wanted rate would need, if it could be fractional

    48000000 / 115200                    =  416.667
    DIV      =  round(416.667)           =  ___

  and what the hardware then actually produces

    baud     =  48000000 / DIV           =  ___ baud

  as a fraction of what both ends agreed on

    error    =  (baud - 115200) / 115200 =  ___ %

  the same sum on a part whose peripheral clock is an ordinary 8 MHz

    8000000 / 115200 = 69.44,  DIV = 69,  baud = 115942,  error = +0.64 %

  and on one running from a 1 MHz internal oscillator

    1000000 / 115200 = 8.68,   DIV = ___,  baud = 111111,  error = -3.55 %

  a receiver samples in the middle of each bit, and the middle of the stop
  bit of an 8N1 frame is 9.5 bit times after the start edge, so by then the
  1 MHz part's sampling point has drifted by

    9.5 * 3.55 %                         =  ___ % of a bit
''',
                "blanks": [
                    {
                        "prompt": "416.667 rounded to the nearest whole divider.",
                        "hole": "?",
                        "opts": ["417", "416", "4167", "115200"],
                        "a": 0,
                        "why": "417, because 416.667 is nearer to 417 than to 416. Rounding rather "
                               "than truncating matters: 416 would give 115385 baud, an error of "
                               "+0.16% instead of −0.08%, so simply casting the division to an "
                               "integer doubles the error for free. Real peripherals do better "
                               "still by keeping a few fractional bits of the divider, which is "
                               "what the 'fraction' field in a modern UART's baud register is for.",
                    },
                    {
                        "prompt": "48000000 divided by the whole divider you just chose.",
                        "hole": "?",
                        "opts": ["115108", "115200", "115385", "114833"],
                        "a": 0,
                        "why": "$48000000/417 = 115107.9$, which rounds to 115108 baud. The value "
                               "115200 is what was asked for and is exactly what the hardware "
                               "cannot produce from this clock — that gap is the whole subject "
                               "here. The value 115385 comes from truncating the divider to 416 "
                               "instead of rounding, and 114833 from rounding it the wrong way to "
                               "418.",
                    },
                    {
                        "prompt": "How far 115108 is from 115200, as a percentage of 115200.",
                        "hole": "?",
                        "opts": ["-0.08", "+0.08", "-0.80", "-8.0"],
                        "a": 0,
                        "why": "$(115108 - 115200)/115200 = -0.0008$, which is −0.08%. The sign is "
                               "worth carrying: a divider rounded *up* makes the rate *lower*, "
                               "because the divider is underneath. As an error budget this is "
                               "nothing at all — 9.5 bit times of it is 0.8% of a bit, so the "
                               "sampling point is still essentially in the middle of the stop bit.",
                    },
                    {
                        "prompt": "8.68 rounded to the nearest whole divider.",
                        "hole": "?",
                        "opts": ["9", "8", "10", "87"],
                        "a": 0,
                        "why": "9, giving $1000000/9 = 111111$ baud. This is where a slow peripheral "
                               "clock bites: the divider is a small integer, so the steps between "
                               "the rates you can reach are enormous — 8 would give 125000 baud, "
                               "+8.5%, and there is nothing available in between. The general rule "
                               "falls out of it: the higher the peripheral clock, the finer the "
                               "grid of reachable baud rates.",
                    },
                    {
                        "prompt": "3.55% of drift per bit, accumulated over 9.5 bit times.",
                        "hole": "?",
                        "opts": ["33.7", "3.55", "35.5", "50"],
                        "a": 0,
                        "why": "$9.5 \\times 3.55 = 33.7$% of a bit. That is a third of the way "
                               "from the middle of the stop bit towards its edge, and it works — "
                               "just — provided the other end is perfect. It is not: give the "
                               "transmitter its own 1% and the total is over 43%, and the link "
                               "starts reporting framing errors that no amount of staring at the "
                               "wiring will explain. The value 3.55 is the per-bit error, which is "
                               "harmless on its own; the accumulation is the whole point.",
                    },
                ],
            },
            "lab": {
                "title": "A frame on the wire, and a divider that misses",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Five functions covering both halves of this module: what the bits are, and what the
timing does to them.

- `parity_bit(byte, kind)` — the bit that makes the count of 1s in the data *plus the
  parity bit itself* even (`kind == "even"`) or odd (`kind == "odd"`). Return `None`
  for any other `kind`.
- `frame(byte, parity=None, stops=1)` — the line levels of one complete frame, as a
  list of 0s and 1s: a start bit (0), then the eight data bits **least significant
  first**, then the parity bit if one was asked for, then `stops` stop bits (1).
- `decode(bits, parity=None, stops=1)` — the byte a receiver recovers, or `None` if the
  frame is malformed. Reject a list of the wrong length, a start bit that is not 0, any
  stop bit that is not 1, and a parity bit that does not match. Otherwise reassemble the
  byte, remembering which end the bits came out of.
- `divisor(f_clk, baud)` — the integer divider, rounded to nearest, never less than 1.
- `error_pct(f_clk, baud)` — how far the resulting rate is from the wanted one, as a
  signed percentage: $100\,(f_{clk}/\text{DIV} - \text{baud})/\text{baud}$.

`bin(x).count("1")` counts the set bits in one step, and is worth knowing.

The pair to look at when it works is `frame` and `decode`. Feeding one into the other
must return the byte you started with for all 256 values, which is the property a test
below checks — and it is the only kind of test worth writing for a codec.
''',
                "files": [{"name": "main.py", "content": r'''
"""A UART frame, and the divider that decides where its bits land."""


def parity_bit(byte, kind):
    """The bit that makes the total count of 1s even or odd."""
    # TODO: count the 1s in the byte; for "even" return that count mod 2,
    # for "odd" return the complement of it, otherwise None.
    return None


def frame(byte, parity=None, stops=1):
    """The line levels of one frame: start, data LSB first, parity, stop(s)."""
    # TODO: build the list. The start bit is 0 and the stop bits are 1.
    return []


def decode(bits, parity=None, stops=1):
    """The byte a receiver recovers, or None if the frame is malformed."""
    # TODO: check the length, the start bit and every stop bit, reassemble the
    # data bits, then check the parity bit if there is one.
    return None


def divisor(f_clk, baud):
    """The integer baud divider, rounded to nearest, at least 1."""
    # TODO: f_clk / baud, rounded, floored at 1.
    return 0


def error_pct(f_clk, baud):
    """How far the achievable rate is from the wanted one, as a signed percentage."""
    # TODO: work out the achievable rate from the divisor, then compare.
    return 0.0


if __name__ == "__main__":
    print("0x41 on the wire:", frame(0x41))
    print("and back again:  ", decode(frame(0x41)))
    for f in (48e6, 8e6, 1e6):
        print("%5.1f MHz clock: DIV = %d, error %+.2f %%"
              % (f / 1e6, divisor(f, 115200), error_pct(f, 115200)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""A UART frame, and the divider that decides where its bits land."""


def parity_bit(byte, kind):
    """The bit that makes the total count of 1s even or odd."""
    ones = bin(byte & 0xFF).count("1")
    if kind == "even":
        return ones % 2
    if kind == "odd":
        return 1 - ones % 2
    return None


def frame(byte, parity=None, stops=1):
    """The line levels of one frame: start, data LSB first, parity, stop(s)."""
    bits = [0]
    for i in range(8):
        bits.append((byte >> i) & 1)
    if parity is not None:
        bits.append(parity_bit(byte, parity))
    bits.extend([1] * stops)
    return bits


def decode(bits, parity=None, stops=1):
    """The byte a receiver recovers, or None if the frame is malformed."""
    want = 1 + 8 + (0 if parity is None else 1) + stops
    if len(bits) != want:
        return None
    if bits[0] != 0:
        return None
    if any(b != 1 for b in bits[-stops:]):
        return None
    byte = 0
    for i in range(8):
        byte |= bits[1 + i] << i
    if parity is not None and bits[9] != parity_bit(byte, parity):
        return None
    return byte


def divisor(f_clk, baud):
    """The integer baud divider, rounded to nearest, at least 1."""
    d = int(f_clk / baud + 0.5)
    return d if d >= 1 else 1


def error_pct(f_clk, baud):
    """How far the achievable rate is from the wanted one, as a signed percentage."""
    actual = f_clk / divisor(f_clk, baud)
    return (actual - baud) / baud * 100.0


if __name__ == "__main__":
    print("0x41 on the wire:", frame(0x41))
    print("and back again:  ", decode(frame(0x41)))
    for f in (48e6, 8e6, 1e6):
        print("%5.1f MHz clock: DIV = %d, error %+.2f %%"
              % (f / 1e6, divisor(f, 115200), error_pct(f, 115200)))
'''}],
                "hints": [
                    "For even parity the bit is simply the count of 1s in the data, modulo 2: send that, and the total number of 1s including it is even. Odd parity is its complement.",
                    "`frame` is a list built in order. The data loop is `for i in range(8): bits.append((byte >> i) & 1)`, and starting at `i = 0` is what puts the least significant bit on the wire first.",
                    "In `decode`, work out the expected length before anything else — `1 + 8 + (0 if parity is None else 1) + stops` — and reject a list that does not match it. A codec that indexes into a short list raises where it should have returned None.",
                    "Reassembling is the mirror of building: `byte |= bits[1 + i] << i`. Shifting by `7 - i` instead gives the bit-reversed value, which passes the single-byte case in your head and fails the round trip over all 256.",
                    "`divisor` must round rather than truncate: `int(f_clk / baud + 0.5)`. Python's built-in `round` uses banker's rounding and would send an exact .5 to the nearest even integer, which is not what a datasheet means by 'rounded'.",
                ],
                "tests": [
                    {"name": "parity, both senses", "code": r'''
assert parity_bit(0x41, "even") == 0, \
    f"0x41 has two 1 bits, so even parity needs a 0; got {parity_bit(0x41, 'even')}"
assert parity_bit(0x41, "odd") == 1, f"got {parity_bit(0x41, 'odd')}"
assert parity_bit(0x01, "even") == 1, "one 1 bit, so even parity needs another"
assert parity_bit(0xFF, "even") == 0, "eight 1 bits is already even"
assert parity_bit(0x00, "odd") == 1, "no 1 bits at all, so odd parity needs one"
assert parity_bit(0x41, "none") is None, "an unknown kind gives None"
'''},
                    {"name": "a frame, least significant bit first", "code": r'''
got = frame(0x41)
assert got == [0, 1, 0, 0, 0, 0, 0, 1, 0, 1], \
    f"start, then 0x41 backwards, then stop; got {got}"
assert len(frame(0x00)) == 10, "8N1 is always ten bits"
assert frame(0x00) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], "only the stop bit is high"
assert frame(0xFF) == [0, 1, 1, 1, 1, 1, 1, 1, 1, 1], "only the start bit is low"
'''},
                    {"name": "parity and a second stop bit lengthen it", "code": r'''
got = frame(0x41, "even", 2)
assert got == [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1], f"got {got}"
assert len(frame(0x41, "odd", 1)) == 11, "8O1 is eleven bits"
'''},
                    {"name": "decoding rejects what a receiver rejects", "code": r'''
assert decode(frame(0x41)) == 0x41, f"got {decode(frame(0x41))}"
assert decode([1, 1, 0, 0, 0, 0, 0, 1, 0, 1]) is None, \
    "the start bit is not 0, so this is not a frame"
assert decode([0, 1, 0, 0, 0, 0, 0, 1, 0, 0]) is None, \
    "the stop bit is not 1 - this is exactly what a framing error is"
assert decode([0, 1, 0, 0, 0, 1]) is None, "too few bits"
assert decode(frame(0x41, "even"), "even") == 0x41, "a good parity bit passes"
bad = frame(0x41, "even")
bad[1] ^= 1
assert decode(bad, "even") is None, "one flipped data bit must fail the parity check"
'''},
                    {"name": "the round trip holds for every byte", "code": r'''
for b in range(256):
    assert decode(frame(b)) == b, f"8N1 round trip failed at {hex(b)}"
    assert decode(frame(b, "even"), "even") == b, f"8E1 round trip failed at {hex(b)}"
    assert decode(frame(b, "odd", 2), "odd", 2) == b, f"8O2 round trip failed at {hex(b)}"
'''},
                    {"name": "the divider rounds, and never reaches zero", "code": r'''
assert divisor(48e6, 115200) == 417, f"48 MHz over 115200 is 416.67; got {divisor(48e6, 115200)}"
assert divisor(8e6, 115200) == 69, f"got {divisor(8e6, 115200)}"
assert divisor(1e6, 115200) == 9, f"8.68 rounds up to 9; got {divisor(1e6, 115200)}"
assert divisor(16e6, 9600) == 1667, f"got {divisor(16e6, 9600)}"
assert divisor(1e6, 4000000) == 1, "a divider can never be zero, however hopeless the request"
'''},
                    {"name": "and the error that leaves behind", "code": r'''
e = error_pct(48e6, 115200)
assert abs(e - (-0.0799)) < 0.001, f"48 MHz gives -0.08 %; got {e}"
e = error_pct(8e6, 115200)
assert abs(e - 0.6441) < 0.001, f"8 MHz gives +0.64 %; got {e}"
e = error_pct(1e6, 115200)
assert abs(e - (-3.5494)) < 0.001, f"1 MHz gives -3.55 %; got {e}"
assert abs(error_pct(72e6, 115200)) < 1e-9, \
    "72 MHz divides by exactly 625, so this one has no error at all"
assert abs(error_pct(48e6, 9600)) < 1e-9, "and 9600 from 48 MHz is exact too"
'''},
                ],
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "Sharing wires: SPI and I²C",
            "summary": "Two ways to put the clock on the wire instead of guessing it, and the reason one of them comes with resistors.",
            "concepts": [
                "Synchronous means the clock travels with the data, so there is no rate to agree on beforehand and no error to accumulate: the receiver samples on an edge the transmitter provided. What replaces the baud rate as the thing both ends must agree about is *which* edge, and that is all CPOL and CPHA are — the clock's idle level, and whether data is sampled on the first or the second edge of each bit.",
                "SPI is four wires — clock, one data line each way, and a select line per device — and it is full duplex: every clock edge shifts one bit out and one bit in at the same time. Reading a byte therefore means writing one, usually a dummy, and that is not a quirk of the driver but the shape of the hardware, which is a pair of shift registers joined into a ring.",
                "SPI has no addressing and no acknowledgement. The select line picks the device, so nothing needs a name, and nothing on the bus can tell the master it is not there: a disconnected peripheral returns whatever the idle line reads as, usually 0x00 or 0xFF, quietly and forever. What it buys for that is speed — tens of megahertz — and what it costs is a pin per device.",
                "I²C is two wires for any number of devices, so it must supply the two things SPI leaves out: an address, sent as the first seven bits of the first byte, and an acknowledgement, which is a ninth clock in which the addressed device pulls the data line down. Nine bits per byte is an 11% tax on everything you send, and it buys the ability to know that something answered.",
                "Both I²C lines are open-drain: a device can pull down or let go, never drive up. That is what makes it safe for several devices to share one wire, and it means the rising edge is not driven at all — a pull-up resistor and the bus capacitance charge it. Choosing that resistor is the whole of I²C's electrical design: small enough to charge the capacitance inside the rise-time budget, large enough that whichever device is pulling down stays inside its sink-current limit.",
            ],
            "read": [
                {
                    "title": "One wire, two kinds of edge",
                    "minutes": 16,
                    "body": r'''
Put a scope on the SDA line of a working I²C bus and look at one byte going past. The
falling edges are vertical. The rising edges are not — each one is a curve, and the
measurement cursors put it a little under a microsecond from the bottom of the swing to
the top:

```text
        _____                   ______
SDA  \ /     \                 /
      X       \_______________/
     / \
      |         |
   20 ns      940 ns
   falling     rising
```

Same wire, same capacitance, same two devices. One edge is fifty to a hundred times slower
than the other, and nothing about the protocol asked for that asymmetry. It is a
consequence of how the pin is built, and everything else about designing an I²C bus
follows from it.

## One edge is driven and the other is left to a resistor

An I²C pin is open-drain. It contains a transistor to ground and nothing to the supply, so
a device has exactly two things it can do: pull the line down, or let go of it. Pulling
down puts a saturated transistor of a few tens of ohms across the bus capacitance. Letting
go leaves the pull-up resistor to charge that same capacitance on its own.

Both edges are the same exponential, $\tau = RC$, with two very different values of $R$:

```python
C_BUS = 200e-12
R_ON, R_PULLUP = 40.0, 4700.0

for name, r in (("held down by a transistor", R_ON),
                ("released, charged by the pull-up", R_PULLUP)):
    print("%-34s R = %7.0f ohm, tau = %8.2f ns" % (name, r, 1e9 * r * C_BUS))
print("the rising edge is %.0f times slower than the falling one, on the same wire"
      % (R_PULLUP / R_ON))
```

Forty ohms against 200 pF is a time constant of **8 ns**; 4.7 kΩ against the same 200 pF
is **940 ns**. The rising edge is **118 times** slower, which is the scope picture,
and the ratio is nothing but the ratio of the two resistances.

## Why the protocol insists on it

Being unable to drive high is what makes sharing safe. Any number of devices can pull the
line down at the same moment and nothing is damaged, because pulling down twice is the
same as pulling down once — the line is the logical AND of everything on it. Two push-pull
outputs disagreeing would instead put the supply and ground in series through two
transistors.

That is also what makes the acknowledgement possible. After eight bits the master releases
the data line and issues a ninth clock, and the *addressed* device pulls it down to say it
is there. A device answering on a line the master has let go of works because letting go is
a state the hardware supports.

So the two things SPI leaves out — an address and an acknowledgement — are exactly what
I²C spends its two wires on, and it can afford them because open-drain makes a shared wire
safe.

## Choosing the resistor is a floor and a ceiling on the same number

The ceiling comes from the rising edge. The specification does not measure it from zero; it
measures $t_r$ between $0.3\,V_{DD}$ and $0.7\,V_{DD}$, which are the two logic thresholds.
Charging towards $V_{DD}$, the line reaches a fraction $f$ of the supply at
$t = \tau \ln\frac{1}{1-f}$, so the specified edge is the difference of two of those:

$$t_r = \tau\left(\ln\frac{1}{0.3} - \ln\frac{1}{0.7}\right) = \tau \ln\frac{7}{3}$$

The floor comes from the falling edge, or rather from what holds the line down. A device
pulling down holds the line at $V_{OL} = 0.4$ V and is specified to sink no more than 3 mA,
and every milliamp of that comes through your pull-up:

$$R_p \geq \frac{V_{DD} - V_{OL}}{I_{sink}}$$

```python
import math

V_DD, V_OL, I_SINK = 3.3, 0.4, 3.0e-3
K = math.log(7.0 / 3.0)
print("the edge from 0.3 to 0.7 V_DD takes %.4f tau" % K)
for c in (100e-12, 200e-12, 400e-12):
    print("at %3.0f pF the pull-up must be under %5.0f ohm, and over %3.0f ohm to stay inside 3 mA"
          % (1e12 * c, 1e-6 / (K * c), (V_DD - V_OL) / I_SINK))
print("4.7 k against 200 pF gives an edge of %.0f ns" % (1e9 * 4700 * 200e-12 * K))
```

The constant is **0.8473**, so the useful form of the rule is $t_r \approx 0.85\,R_pC$.
Against the 1 µs that 100 kHz standard mode allows, a bus with 100 pF on it can take a
pull-up up to **11802 Ω**; at 200 pF that halves to **5901 Ω**; and at the 400 pF the
specification permits as an absolute maximum it is down to **2951 Ω**. The floor stays at
**967 Ω** throughout, because it has nothing to do with capacitance.

Look at what those two columns are doing. The floor is fixed and the ceiling falls as
$1/C_{bus}$, so the window closes as the bus grows. That is the honest reason the
specification caps bus capacitance at 400 pF, and it is why adding a sixth device, or
half a metre of ribbon cable, can stop a bus that has worked for three years.

## SPI drives both edges, and pays for it in pins

SPI makes the opposite trade. Every line is push-pull and driven hard, so there is no
resistor, no rise-time budget, and no reason it cannot run at tens of megahertz.

It is four wires: a clock, one data line in each direction, and a select line per device.
The master generates every clock edge, and each edge shifts one bit out of the master and
one bit in from the peripheral at the same time — the two devices are a single ring of
shift registers. So a read *is* a write. Clocking a byte out is how you clock a byte in,
which is why an SPI driver is one `transfer(byte)` function rather than a read and a write,
and why reading a sensor means sending a byte nobody cares about.

What both ends still have to agree on is which edge the data is valid on, and that is all
CPOL and CPHA are: the clock's idle level, and whether the sample is taken on the first or
the second edge of each bit. Get it wrong and both devices clock away contentedly while the
master samples half a bit early or late — the received byte is often the right one shifted
by a position, repeatably, with nothing reporting an error, because SPI has no mechanism
for reporting one.

That absence is the real cost of the four wires. No address means nothing needs a name; no
acknowledgement means nothing can tell you it is not there. A peripheral whose select line
is never asserted returns whatever the idle line reads as — `0x00` or `0xFF` — completely
and forever, through a transfer that completes normally with a clean status register.

## Nine clocks a byte, and what that buys

The acknowledgement is not free either. Every I²C byte takes nine clock periods: eight of
data and one in which somebody pulls the line down. That is an 11% tax on everything the
bus carries, and it is worth pricing against what the bus is asked to do.

```python
for f_bus in (100e3, 400e3):
    t = 9 * 4 / f_bus
    print("%3.0f kHz: one four-byte read takes %6.1f us, and 200 a second is %5.1f %% of the bus"
          % (f_bus / 1e3, 1e6 * t, 100.0 * t * 200))
t8 = 8 * 4 / 100e3
print("eight clocks a byte instead of nine: %.1f %%, the acknowledgement quietly dropped"
      % (100.0 * t8 * 200))
spi = 8 * 4 / 8e6
print("the same four bytes on an 8 MHz SPI bus: %.1f us, %.2f %% at the same rate"
      % (1e6 * spi, 100.0 * spi * 200))
```

Reading one register out of a sensor is four bytes on the wire — the address with a write
bit, the register number, the address again with a read bit after a repeated start, and the
data — so 36 clock periods. At 100 kHz that is **360 µs**, and two hundred reads a second
is **7.2%** of every second gone. Counting eight clocks a byte instead of nine gives 6.4%
and has silently thrown the acknowledgement away. Moving to 400 kHz brings it to **1.8%**,
which is the honest reason to raise a bus speed: not that any single transaction felt slow,
but that the bus is a shared resource with a budget. The same four bytes over SPI at 8 MHz
take 4 µs and **0.08%**.

## The mistake, and why it is tempting

Fitting 4.7 kΩ.

It is on nearly every reference schematic and in nearly every application note, and against
200 pF it genuinely does meet standard mode: the block above puts that edge at **796 ns**,
inside the microsecond. It is not a wrong number. It is a number with no margin, chosen
without reference to the bus it is on.

What makes it dangerous is the direction it fails in. The ceiling falls as capacitance
rises, so at 400 pF the largest legal pull-up is 2951 Ω and the same 4.7 kΩ is 59% over —
and nobody re-checks a resistor when they add a device. The failure is not immediate
either: an edge that is slightly too slow still crosses the threshold most of the time, so
the bus works, mostly, and the occasional missed acknowledgement is put down to the sensor.
Raise the clock to 400 kHz, where the rise-time budget is 300 ns, and it stops working
altogether — and the change that broke it was in software.

The related trap is the other end. Reaching for 1 kΩ to be safe on rise time puts 2.9 mA
through whichever device is holding the line down, at the very edge of what it is specified
to sink, and its $V_{OL}$ climbs until the line no longer reads as a low.

## Where these models stop holding

The single-RC model treats the bus as one lumped capacitor charged through one resistor.
Real capacitance is distributed along the tracks and cable, the pull-up is not the only
current path, and every device's input adds a few picofarads plus a leakage current. Use it
to size a resistor and to know which direction to move it, not as a prediction of an edge
to the nanosecond.

The rise-time budget above is standard mode's. Fast mode at 400 kHz allows 300 ns, which is
a third of the ceiling from the same arithmetic, and fast-mode-plus at 1 MHz allows 120 ns
and expects a driven pull-up rather than a resistor. The method survives the change of
mode; the numbers do not.

The timing budget also assumes the master controls the pace. It does not: I²C explicitly
permits a peripheral to hold the clock line down while it thinks — clock stretching — and a
device that stretches for a millisecond has taken a millisecond of your bus whatever your
arithmetic said. Multi-master arbitration, where two masters start talking at once and one
detects that the line is lower than it is driving, is the same open-drain property again
and adds its own delays.

And SPI stops being a digital problem at speed. At tens of megahertz a few centimetres of
track is a transmission line, edges reflect off unterminated ends, and the clock skew
between a master and a peripheral at opposite corners of a board eats into the setup window
the mode diagram assumes.

## What you are about to build

The build, **Sizing an I²C pull-up**, is the second block above turned into a component
choice. The 200 pF of bus capacitance is already on the canvas and is not yours to delete —
it is the devices, the tracks and the cable. A 47 kΩ resistor is fitted, which is what "it
needs a pull-up" gets you, and its edge is nowhere near the budget. Three checks measure
the line you draw: the edge from 0.99 V to 2.31 V inside 1 µs, a settled level at the full
3.3 V, and every pull-up at 1 kΩ or more. The arithmetic above gives a window of 967 Ω to
5901 Ω at 200 pF, so the build's floor is the next stock value up, and 5.6 kΩ is the
largest stock value under the ceiling.

The numeric question, **How much of the second the bus is busy**, is the third block done
by hand: four bytes, nine clock periods each, 200 reads a second on a 100 kHz bus. The
answer is checked to one decimal place, and the difference between the right answer and the
tempting one is entirely the acknowledgement.
''',
                },
            ],
            "quiz": {
                "title": "Edges, addresses and the ninth bit",
                "minutes": 10,
                "questions": [
                    {
                        "q": "An SPI driver needs to read one byte from a sensor. What must it do?",
                        "opts": [
                            "wait for the sensor to clock the byte out on its own",
                            "clock out a byte of its own, because the same clock edges shift data in both directions",
                            "assert the select line and read the data register without generating a clock",
                            "send a read command and then release the clock line",
                        ],
                        "a": 1,
                        "why": r'''
The master generates every clock edge, and each edge shifts a bit out of the master and a
bit in from the peripheral at the same time — the two devices are a single ring of shift
registers. So a read is a write whose transmitted byte nobody cares about, and this is
why SPI drivers are written as one `transfer(byte)` call rather than as separate read and
write functions. Nothing arrives without the master asking for it, which is also why SPI
peripherals that need to report something urgently come with a separate interrupt pin.
''',
                    },
                    {
                        "q": "A peripheral expects data to be sampled on the falling edge of the clock, and the master is configured to sample on the rising edge. What is seen?",
                        "opts": [
                            "nothing at all — the peripheral will not respond",
                            "the right bytes, delayed by one clock",
                            "values that are consistently wrong, often the correct byte shifted by one bit",
                            "an acknowledgement error reported by the peripheral",
                        ],
                        "a": 2,
                        "why": r'''
Both devices happily clock away; they simply disagree about when the data line is valid,
so the master samples half a bit early or late and captures the neighbouring bit. The
result is repeatable nonsense — often the expected byte shifted by one position, which is
the clue worth recognising. There is no error to report, because SPI has no mechanism for
reporting one: nothing checks anything. Mode mismatches are found by reading a register
whose value you already know, which is why so many SPI devices have a "who am I" register
with a fixed value in it.
''',
                    },
                    {
                        "q": "An I²C bus runs at 400 kHz. Ignoring the start and stop conditions, what is the highest byte rate?",
                        "opts": ["50000 bytes/s", "44444 bytes/s", "40000 bytes/s", "400000 bytes/s"],
                        "a": 1,
                        "why": r'''
Every byte takes nine clocks — eight of data and one for the acknowledgement — so it is
$400000/9 = 44444$ bytes per second. Dividing by eight gives 50000 and forgets the
acknowledgement, which is the same class of mistake as forgetting a UART's start and stop
bits, and it is worth being consistent about: a bus's bit rate is never its data rate.
The real figure is lower again, because every transaction also spends time on its start,
its address byte and its stop.
''',
                    },
                    {
                        "q": "Why must an I²C device's data pin be open-drain rather than push-pull?",
                        "opts": [
                            "so that several devices can be connected without two of them ever driving the line in opposite directions",
                            "because open-drain outputs switch faster",
                            "so that the bus can run at a different voltage from the devices",
                            "because the protocol requires the master to control the line at all times",
                        ],
                        "a": 0,
                        "why": r'''
The point is that a device can only pull the line down or let go of it. Two devices doing
that at once is harmless, so a device can start talking while another is talking without
a short circuit — and the acknowledgement, in which the *addressed* device pulls down a
line the master has released, works for the same reason. Push-pull outputs disagreeing
would put the supply and ground in series through two transistors. Open-drain is
demonstrably not faster: the rising edge is left to a resistor, and that is precisely
what limits how fast the bus can go. The level-shifting point is a real bonus of
open-drain, but it is not why the protocol requires it.
''',
                    },
                    {
                        "q": "A 400 kHz bus with 200 pF of total capacitance is fitted with 10 kΩ pull-ups. What goes wrong?",
                        "opts": [
                            "the devices cannot pull the line low enough",
                            "the line needs about 2.4 µs to climb from low to a valid high, and it is released for only about half of each 2.5 µs clock period, so it never gets there",
                            "the pull-ups draw too much current from the supply",
                            "nothing — 10 kΩ is the standard value",
                        ],
                        "a": 1,
                        "why": r'''
$\tau = 10\,\text{k} \times 200\,\text{pF} = 2$ µs, and reaching 70% of the supply takes
$1.2\tau = 2.4$ µs, against a clock period of 2.5 µs of which the line is only released
for about half. The line is still climbing when the next edge arrives, so it never gets
clearly high and the bus reads as though everything were zero — or works at 100 kHz and
fails when someone raises the speed, which is the version that reaches production. The
sink-current problem is the *opposite* failure, from a pull-up that is too small.
''',
                    },
                    {
                        "q": "An SPI sensor is fitted the wrong way round and its select pin is never asserted. What does the driver see?",
                        "opts": [
                            "a bus error from the peripheral",
                            "a timeout, because no clock is returned",
                            "consistent 0x00 or 0xFF bytes, with nothing at all reporting a problem",
                            "the previous device's data",
                        ],
                        "a": 2,
                        "why": r'''
Nothing is listening, so nothing drives the input line, and what the master shifts in is
whatever the line idles at — all ones if a pull-up holds it, all zeros if a pull-down
does. The transfer completes normally and the status register is clean, because there is
no acknowledgement in the protocol to be missing. This is the practical cost of SPI's
simplicity and the reason every driver should start by reading an identity register:
0x00 and 0xFF are the two values that mean "no answer", and a real device almost never
reports either.
''',
                    },
                ],
            },
            "build": {
                "title": "Sizing an I²C pull-up",
                "minutes": 24,
                "brief": r'''
This is one line of an I²C bus — SDA, though SCL is the same problem — at the instant a
device lets go of it. Nothing drives the line high: the **200 pF** of bus capacitance
already on the canvas has to be charged through the pull-up, and until it is, the line
is not a valid high.

A 47 kΩ resistor is fitted, which is what "it just needs a pull-up" gets you.

## What the finished bus must do

- when the line is released, the edge must climb from **0.3 $V_{DD}$ = 0.99 V to
  0.7 $V_{DD}$ = 2.31 V in no more than 1 µs**, which is the rise-time budget for
  100 kHz standard-mode I²C — the specification measures $t_r$ between those two
  levels, not up from zero
- it must settle at the full 3.3 V, so the inputs on the bus read an unambiguous 1
- every pull-up must be **1 kΩ or more**: a device pulling the line down holds it at
  0.4 V and must sink no more than 3 mA, and $(3.3 - 0.4)/1\,\text{k} = 2.9$ mA is
  already at that limit

## Working it out

Charging through a resistor to a supply $V_{DD}$, the line reaches $0.3\,V_{DD}$ after
$\tau \ln(1/0.7)$ and $0.7\,V_{DD}$ after $\tau \ln(1/0.3)$, so the edge the
specification measures takes the difference between them: $\tau \ln(7/3) = 0.847\,\tau$,
with $\tau = R_p C_{bus}$. Put the budget in, get the largest $\tau$ you can afford, and
divide by 200 pF.

Then notice what the two constraints leave you: they are a floor and a ceiling on the
same resistor, and the whole of I²C bus design is keeping that window open. It is why
the specification puts a hard limit of 400 pF on bus capacitance, and why adding a sixth
device, or a longer cable, can stop a bus that has worked for years.

The checks measure the line, so anything inside the window passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 47000},
                        {"id": "p3", "kind": "OUT", "x": 13, "y": 7},
                        {"id": "p4", "kind": "C", "x": 11, "y": 9, "rot": 1, "value": 2e-10},
                        {"id": "p5", "kind": "GND", "x": 11, "y": 11},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [13, 7]},
                        {"a": [11, 7], "b": [11, 8]},
                        {"a": [11, 10], "b": [11, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 2200},
                        {"id": "p3", "kind": "OUT", "x": 13, "y": 7},
                        {"id": "p4", "kind": "C", "x": 11, "y": 9, "rot": 1, "value": 2e-10},
                        {"id": "p5", "kind": "GND", "x": 11, "y": 11},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [13, 7]},
                        {"a": [11, 7], "b": [11, 8]},
                        {"a": [11, 10], "b": [11, 11]},
                    ],
                },
                "checks": [
                    {"name": "the released edge crosses 0.3 to 0.7 V_DD inside a microsecond", "code": r'''
const s = c.step(2e-5);
function cross(th) {
  for (let i = 0; i < s.v.length; i++) {
    if (s.v[i] >= th) {
      return i === 0 ? 0 : s.t[i - 1] + (th - s.v[i - 1]) / (s.v[i] - s.v[i - 1]) * (s.t[i] - s.t[i - 1]);
    }
  }
  return null;
}
const tLo = cross(0.3 * 3.3);
const tHi = cross(0.7 * 3.3);
c.assert(tHi !== null,
  'The line never reaches 2.31 V within 20 µs. Check that the pull-up really runs from ' +
  'the 3.3 V rail to the probed node.');
c.assert(tHi - tLo <= 1e-6,
  'The edge takes ' + c.fmt(tHi - tLo, 's') + ' to get from 0.99 V to 2.31 V, against ' +
  'the 1 µs standard mode allows between 0.3 and 0.7 V_DD. A smaller pull-up charges ' +
  'the 200 pF faster.');
'''},
                    {"name": "and settles at the full supply", "code": r'''
c.close(c.vout(), 3.3, 0.01,
  'the idle level of the line. It must reach the rail: anything that divides the supply ' +
  'leaves the inputs on the bus reading a level that is neither a 1 nor a 0');
'''},
                    {"name": "no device is asked to sink more than 3 mA", "code": r'''
const rs = c.values('R');
c.assert(rs.length >= 1, 'The line needs a pull-up.');
rs.forEach(function (r) {
  const sink = (3.3 - 0.4) / r;
  c.assert(r >= 1000 * 0.99,
    'A ' + c.fmt(r, 'Ω') + ' pull-up asks the device holding the line low for ' +
    c.fmt(sink, 'A') + ', past the 3 mA it is specified for. Keep it at 1 kΩ or above.');
});
'''},
                    {"name": "the bus capacitance is still there", "code": r'''
const cs = c.values('C');
c.assert(cs.length === 1 && Math.abs(cs[0] - 200e-12) <= 2e-12,
  'The 200 pF is the devices, the tracks and the cable. Removing it does not make the ' +
  'real bus faster; it only stops these checks measuring the real bus.');
'''},
                ],
                "hints": [
                    "Start from the budget: $1\\,\\mu\\text{s} = 0.847\\,\\tau$ gives $\\tau = 1.18\\,\\mu$s, and $1.18\\,\\mu\\text{s}/200\\,\\text{pF} = 5.9$ kΩ — but that lands the edge exactly *on* the 1 µs limit rather than inside it, so the pull-up has to come below it.",
                    "The floor is 1 kΩ from the sink-current rule, so the window runs from 1 kΩ up to just under 5.9 kΩ, and 5.6 kΩ is the largest stock value inside it. 2.2 kΩ sits comfortably in the middle and is a stock value.",
                    "4.7 kΩ is the value most people reach for, and at 200 pF it does meet the budget: $4.7\\,\\text{k} \\times 200\\,\\text{pF} \\times \\ln(7/3) = 796$ ns. What it has no margin for is a bus that grows. The ceiling falls as $1/C_{bus}$, so at the specification's own 400 pF limit the largest pull-up is 2.95 kΩ and the same 4.7 kΩ is 59% over.",
                    "Check the current the other way round before you commit: at 2.2 kΩ, a device holding the line at 0.4 V sinks $(3.3-0.4)/2200 = 1.3$ mA, comfortably inside its 3 mA.",
                    "If the line never reaches the threshold at all, look for a second resistor to ground. A divider on an I²C line leaves it sitting between the two logic thresholds, which is the one place a digital input must never be left.",
                ],
            },
            "numeric": {
                "title": "How much of the second the bus is busy",
                "minutes": 8,
                "brief": r'''
Reading one register out of an I²C sensor is not one byte on the wire, it is four: the
address with a write bit, the register number, the address again with a read bit after a
repeated start, and finally the data. Each of those four is nine clock periods — eight
bits and the acknowledgement.

Count the clock periods only. The start, repeated start and stop conditions each take
roughly half a clock period more, which adds about 5% to the answer and is not what this
question is about.
''',
                "prompt": "The sensor is read 200 times a second on a 100 kHz bus. What percentage of wall-clock time is the bus busy?",
                "note": "Give the answer as a percentage, to one decimal place.",
                "figure": r'''
**One register read, in order along the wire.** A start condition; the sensor's address
with a write bit, and its acknowledgement; the register number, and its acknowledgement;
a repeated start; the address again with a read bit, and its acknowledgement; the data
byte, which the master does *not* acknowledge, to say it wants no more; a stop condition.

That is **four bytes**, and every one of them occupies **nine clock periods** — eight
bits and the acknowledgement that follows them.
''',
                "given": [
                    {"label": "Bus clock", "value": "100 kHz"},
                    {"label": "Clock periods per transaction", "value": "4 × 9 = 36"},
                    {"label": "Transactions per second", "value": "200"},
                ],
                "aside": "One clock period at 100 kHz is 10 µs, and everything else is multiplication.",
                "answer": 7.2,
                "tol": 0.15,
                "unit": "%",
                "hint": "Work out how long one transaction takes, multiply by how many happen in a "
                        "second, and compare that with the second.",
                "wrong": "Check whether you used eight clocks per byte instead of nine. The "
                         "acknowledgement is a full clock period and it is on every byte.",
                "why": "36 clock periods at 10 µs each is 360 µs per read, and 200 of those is "
                       "72 ms out of every second — **7.2%**. Using eight clocks per byte gives "
                       "6.4% and quietly loses the acknowledgement. The figure matters because it "
                       "is a budget on a shared resource: a second sensor on the same bus at the "
                       "same rate takes another 7.2%, and a device that stretches the clock while "
                       "it thinks — which I²C explicitly permits — takes as much again on top. Move "
                       "the same traffic to 400 kHz and it becomes 1.8%, which is the honest reason "
                       "to raise the bus speed, rather than any single transaction feeling slow.",
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "The converter, quantisation and fixed point",
            "summary": "A voltage becomes an integer, and from there on all the arithmetic is integer arithmetic.",
            "concepts": [
                "An $N$-bit ADC compares its input against a reference and reports one of $2^N$ codes. The code is a *number of steps*, and one step, the LSB, is $q = V_{ref}/2^N$.",
                "For a 12-bit converter on a 3.3 V reference, $q = 3.3/4096 = 805.7$ µV. No amount of averaging changes what one code is worth; it changes only how much noise sits on top.",
                "Quantisation error is the difference between the input and what the code represents. A converter that truncates has an error between 0 and $q$; one that rounds has an error of at most $q/2$, which is why the error is usually quoted as $\\pm\\frac{1}{2}$ LSB.",
                "The converter samples: it looks at the input at one instant and holds it while it converts. Everything above half the sample rate is folded down into the band below it, and no later processing can separate a folded component from a real one.",
                "That is why the anti-alias filter is analogue and sits before the converter. It is the same RC low-pass as the PWM filter, doing the same job in the other direction.",
                "Averaging $M$ samples of a signal buried in white noise reduces the noise by $\\sqrt{M}$, which is worth half a bit for every doubling of $M$. It costs time, and it does nothing about a systematic offset.",
                "Small microcontrollers have no floating-point unit, so a `float` multiply becomes a library call of tens or hundreds of cycles. Fixed point keeps the speed of integer arithmetic by agreeing where the binary point sits and never storing it.",
                "In Q$f$ format a real number $x$ is held as the integer $X = \\text{round}(x \\cdot 2^{f})$. Adding two Q$f$ numbers is an ordinary integer add; multiplying them gives a Q$2f$ result, which must be shifted right by $f$ to come back.",
                "Two things then have to be watched. The intermediate product needs twice the width of the operands, so a Q15 multiply must be done in 32 bits. And the shift throws away the bits below the point, which gives a fixed-point filter a **dead band**: it stops moving while it is still short of its target.",
            ],
            "read": [
                {
                    "title": "The reading that will not move",
                    "minutes": 16,
                    "body": r'''
Put a bench supply on the input of a 12-bit ADC running from a 3.3 V reference. Set it to
exactly 1.0000 V and log twenty conversions:

```text
1241 1241 1241 1241 1241 1241 1241 1241 1241 1241
1241 1241 1241 1241 1241 1241 1241 1241 1241 1241
```

Now wind the supply up slowly and watch. Nothing happens. At 1.0002 V it still reads 1241;
at 1.0004 V it still reads 1241; at 1.0006 V it still reads 1241. Somewhere past that it
becomes 1242 and stops again.

The converter is not averaging, and it is not broken. It is doing the only thing a
converter can do, and the width of that flat step is the number the rest of this module is
built on.

## The code is a count of steps

An $N$-bit converter compares its input against a reference and reports which of $2^N$
codes the input falls into. The codes divide the reference into equal steps, so one step —
one least significant bit — is

$$q = \frac{V_{ref}}{2^{N}}$$

and for 12 bits on 3.3 V that is $3.3/4096$. Every reading is a *count of those steps*, and
between one count and the next there is nothing the converter can say.

```python
import math

VREF, BITS = 3.3, 12
q = VREF / (1 << BITS)
print("one step of a 12-bit converter on %.1f V is %.3f uV" % (VREF, 1e6 * q))
for mv in (999.5, 999.9, 1000.0, 1000.5, 1000.6, 1000.7):
    code = math.floor((mv / 1000.0) / q)
    print("%8.1f mV -> code %4d, standing for %9.5f V, low by %6.1f uV"
          % (mv, code, code * q, 1e6 * (mv / 1000.0 - code * q)))
```

One step is **805.664 µV**, and the six rows are the bench experiment. 999.5 mV falls in
code 1240. From 999.9 mV all the way to 1000.6 mV the answer is **1241** and does not
budge, which is the flat step, and only at 1000.7 mV does it become 1242. The step is
806 µV wide because that is what one step *is*.

The last column is the error, and its shape is worth reading. This converter truncates: it
reports the code *below* the input, so the input is somewhere in a band one step wide above
what the code stands for, and the error runs from 0 up to $q$ and is always in the same
direction. A converter that rounds instead is wrong by at most $q/2$ in either direction,
which is where the familiar $\pm\frac{1}{2}$ LSB comes from — the same hardware with half a
step of offset added, and worth one bit of accuracy for free. Which of the two you have is
a line in the datasheet, and knowing it is the difference between a systematic 400 µV
offset and none.

No amount of averaging changes any of this. Averaging reduces *noise*; it does not make a
step narrower, and against a perfectly steady input a truncating converter returns the same
code forever, however many times you ask.

## The converter looks at instants, not at intervals

The second thing a converter does is sample. It looks at the input at one moment, holds
that value, and converts it — so what it records is a sequence of instants, and several
different waves fit the same instants exactly.

Take a 6 kHz signal sampled at 10 kHz, and compare it against a 4 kHz one:

```python
import math

FS, F1 = 10000.0, 6000.0
F2 = FS - F1
print("sampled at %.0f kHz, %.0f kHz and %.0f kHz land on the same instants:"
      % (FS / 1e3, F1 / 1e3, F2 / 1e3))
worst = 0.0
for n in range(6):
    t = n / FS
    a = math.sin(2 * math.pi * F1 * t)
    b = -math.sin(2 * math.pi * F2 * t)
    worst = max(worst, abs(a - b))
    print("  n = %d   6 kHz gives %+8.5f   inverted 4 kHz gives %+8.5f" % (n, a, b))
print("largest disagreement across the six samples: %.1e" % worst)
```

Every pair agrees to **1.2e-15**, which is floating-point dust. The samples of a 6 kHz wave
and of an inverted 4 kHz wave are the same numbers. The algebra behind that is one line:
$\sin(2\pi(f_s - f)n/f_s) = \sin(2\pi n - 2\pi f n/f_s) = -\sin(2\pi f n/f_s)$, so a
component at $f_s - f$ is indistinguishable from one at $f$ once you only have the samples.

The consequence is the harsh one. Nothing downstream can undo it — not a longer window, not
a better filter, not a cleverer algorithm — because there is no information left to
separate the two. That is why the anti-alias filter is analogue and sits *in front of* the
converter, and it is the same RC low-pass as the PWM filter in module 6, doing the same job
in the other direction. This module's sandbox, **Sampling, and the frequency that comes
back as something else**, is that experiment with sliders on it.

## No floating-point unit, so agree where the point is

Once a voltage is an integer, everything after it is arithmetic, and on a small part there
is no hardware to do it in floating point. A `float` multiply becomes a library call of
tens or hundreds of cycles, which inside a 10 kHz sample interrupt is a serious fraction of
the machine.

Fixed point keeps the speed of integer arithmetic by agreeing on a scale factor and never
storing it. In Q$f$ format the real number $x$ is held as the integer

$$X = \operatorname{round}\!\left(x \cdot 2^{f}\right)$$

Adding two of them is an ordinary integer add, because both carry the same factor.
Multiplying is where the format shows itself: $XY = xy \cdot 2^{2f}$, which is a Q$2f$
number, and getting back to Q$f$ means dividing out one factor of $2^f$ — a right shift by
$f$.

```python
import math


def to_fixed(x, frac):
    return math.floor(x * (1 << frac) + 0.5)


def fx_mul(a, b, frac):
    return (a * b) >> frac


for x in (0.5, 0.25, 0.1, 1.0):
    print("%.2f in Q15 is %6d" % (x, to_fixed(x, 15)))
half, tenth = to_fixed(0.5, 15), to_fixed(0.1, 15)
print("0.5 x 0.5 -> %d, which reads back as %.5f" % (fx_mul(half, half, 15),
                                                     fx_mul(half, half, 15) / 32768.0))
print("0.1 x 0.1 -> %d, against the ideal %d" % (fx_mul(tenth, tenth, 15), to_fixed(0.01, 15)))

state, target, alpha = 0, 2048, 3277
steps = 0
while True:
    move = (alpha * (target - state) + 16384) >> 15
    if move == 0:
        break
    state += move
    steps += 1
print("the Q15 filter reaches %d after %d steps and stops %d counts short of %d"
      % (state, steps, target - state, target))
```

The first four lines are the format. 0.5 is **16384**, 0.25 is 8192, 0.1 is **3277** —
which is 3276.8 rounded, so the stored value is already 0.006% away from the number you
asked for. And 1.0 maps to **32768**, which does not fit in a signed 16-bit integer: Q15
holds the half-open range $[-1, 1)$, and 1.0 is not in it. That is the format, not a defect.

Then the multiply. $16384 \times 16384 = 268435456$, shifted right by 15 gives **8192**,
which reads back as 0.25 exactly. And $3277 \times 3277$ shifted right by 15 gives **327**
where the ideal answer is **328** — one count low, because the shift discards the bits
below the point rather than rounding them.

## The dead band

That one-count truncation is not a rounding footnote; it is a behaviour. The last lines run
a first-order low-pass entirely in integers — the update the capstone asks for:

```text
state <- state + ((alpha * (sample - state) + 16384) >> 15)
```

with $\alpha = 3277$, which is 0.1 in Q15, and a `+ 16384` that adds half a step before the
shift so the arithmetic rounds instead of always falling short. The filter climbs towards
2048, and after **57 steps** it reaches **2044** and stops. Not slows: stops. Once the
difference $d$ is small enough that $3277d + 16384 < 32768$ — that is, $d \leq 4$ — the
shift produces zero, the state cannot move, and no number of further samples will change
it.

Every fixed-point loop has a dead band, and its width follows from the same arithmetic:
roughly $2^{f-1}/\alpha$ counts. The fixes are to widen the state — keep the filter in Q30
and read the top half out — or to accumulate the discarded remainder and feed it back in.
Neither is free, and choosing between them is a design decision rather than a bug fix.

## The mistake, and why it is tempting

Dividing before multiplying.

Converting a code to millivolts without floating point is

```text
mV = (code * vref_mv) >> bits
```

and the version people write instead divides first, to keep the intermediate small:

```python
code, vref_mv, bits = 1241, 3300, 12
print("multiply then shift: (%d * %d) >> %d = %d mV"
      % (code, vref_mv, bits, (code * vref_mv) >> bits))
print("shift then multiply: (%d >> %d) * %d = %d mV"
      % (code, bits, vref_mv, (code >> bits) * vref_mv))
print("the float the hardware is imitating: %.2f mV" % (code * 3.3 / 4096.0 * 1000.0))
print("the widest intermediate the first form needs: %d, which is %d bits"
      % (code * vref_mv, (code * vref_mv).bit_length()))
```

Multiplying first gives **999 mV**, against the 999.83 mV the floating-point calculation
would produce. Shifting first gives **0 mV** — the entire reading thrown away, because
shifting 1241 right by 12 bits leaves nothing to multiply.

What makes it tempting is that the instinct behind it is a good one. Integer overflow is a
real hazard, "reduce before you multiply" is sound advice in plenty of places, and the
person writing it is being careful rather than careless. The answer is not to divide
earlier but to make the intermediate wider: the product here needs **22 bits**, which a
32-bit `int` holds with room to spare, and a Q15 multiply needs 32 bits for the same
reason. Precision in integer arithmetic lives in the intermediate, and every bit shifted
away is gone for good.

## Where these models stop holding

The converter above is ideal, and a real one is not. Differential non-linearity means the
steps are not all the same width and some codes may be missing entirely; integral
non-linearity bends the whole transfer curve; and offset and gain errors shift and tilt it.
A datasheet quoting 12 bits and ±2 LSB of INL is describing a converter with about ten
honest bits.

The reference is the other half of every number here. $q$ is $V_{ref}/2^N$, so the answer
is only as accurate as the reference, and a part that uses its own 3.3 V supply as the
reference measures voltages against a rail that moves with load and temperature. A ratio
between two things measured on the same reference is far better behaved than either of them
alone, which is why bridge and divider measurements are usually arranged as ratios.

The sampling picture assumes the input is steady while the converter looks at it. It has to
be held, and the sample-and-hold takes time to acquire through whatever source impedance
you present it with — so the filter you put in front, sized in module 6 with resistors up
to 100 kΩ, is also part of the converter's own timing. A source that is too high-impedance
gives a reading that is low and depends on what was converted before it.

Averaging $M$ samples reduces white noise by $\sqrt{M}$, which is half a bit for every
doubling. It assumes the noise is uncorrelated between samples, which fails against
interference at a frequency related to your sample rate, and it does nothing whatever about
a systematic offset — averaging a thousand readings of a converter that is 3 mV low gives
you a very precise 3 mV error.

And Q15 arithmetic wraps rather than saturating. Add two Q15 values near the top of the
range and the result appears at the bottom, which in a control loop is full positive
becoming full negative in one sample. Saturating is what you do instead, and it is why the
lab asks you to write it.

## What you are about to build

Three exercises follow the three halves of this reading.

The sandbox, **Sampling, and the frequency that comes back as something else**, puts a
signal frequency and a sample rate under two sliders, with the time picture above and the
spectrum below. Take the signal past the sample rate and watch an amber alias appear at a
frequency that was never there.

The derivation, **From reference voltage to one bit of the answer**, is four steps: how
many codes $N$ bits give, what one step is worth, the worst-case error of a converter that
rounds, and what happens to the scale factor when two Q$f$ numbers meet. The last step is
the shift, derived rather than asserted.

The lab, **A converter and a Q15 multiply**, asks for `lsb`, `adc_code`, `code_to_volts`,
`to_fixed`, `fx_mul` and `saturate`. Its tests are pointed at exactly the edges above: a
truncating converter reading low by between zero and one step, an input above the reference
clamping to 4095, `0.1 x 0.1` landing at 327 rather than 328, and a two's-complement range
that is not symmetric — 16 bits run from −32768 to +32767, one more negative value than
positive. Get those six right and the capstone is this arithmetic wrapped around a
peripheral you cannot see inside.
''',
                },
            ],
            "sandbox": {
                "title": "Sampling, and the frequency that comes back as something else",
                "visualiser": "spectrum",
                "minutes": 9,
                "initial": {"fsig": 30, "fs": 200},
                "brief": r'''
The top plot is time: the smooth grey curve is the real signal at the input, the round
markers are the instants the converter looked at it, and the milliseconds run along the
bottom. When the samples are consistent with some *other*, lower-frequency wave, that
wave is drawn in amber straight through them.

The bottom plot is the same situation in frequency. The dashed vertical line is half
the sample rate — the Nyquist limit — and the spikes are the signal and, when there is
one, its alias.

Two sliders: the frequency of the signal arriving at the pin, and the rate at which
your timer triggers a conversion.
''',
                "notice": [
                    "As it opens, 30 Hz sampled at 200 Hz: one grey spike, well to the left of the dashed line at 100 Hz, and no amber anywhere. The markers sit on the grey curve and nothing else is consistent with them.",
                    "Drag the signal up to 230 Hz — past the sample rate itself. The grey spike moves far to the right of the dashed line and an amber spike appears at 30 Hz, with an amber 30 Hz wave drawn through the sample markers in the top plot: every marker sits on it exactly. The converter cannot tell 230 Hz from 30 Hz, and neither can anything you write afterwards.",
                    "Set the signal to exactly 100 Hz, half the sample rate. Every marker in the top plot lands on the zero line, because each sample happens exactly one half-cycle after the last — and yet the caption still reports that nothing is lost. Nyquist is an open limit: *below* half the sample rate the samples determine the wave, and *at* it they need not.",
                    "Put the signal back to 30 Hz and drag the sample rate down to its minimum of 20 Hz. There are now three markers across the whole 100 ms window, the dashed line has moved in to 10 Hz, and the 30 Hz signal reappears as an amber 10 Hz spike. Sampling too slowly does not blur a signal; it invents a different one.",
                    "Now take the signal to 170 Hz and the sample rate to its maximum of 400 Hz. The amber vanishes: the dashed line has moved out to 200 Hz, past the signal. That is the honest fix and it is not free — 170 Hz needed the rate doubled from the 200 Hz it started at, which is twice the conversions, twice the interrupts and twice the data to store. The other fix is to put a filter in front of the converter and remove the 170 Hz before it is ever sampled.",
                ],
            },
            "quiz": {
                "title": "Codes, steps and the binary point",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A 10-bit converter runs from a 5.0 V reference. What is one LSB worth?",
                        "opts": ["5.0 mV", "4.88 mV", "0.5 mV", "9.77 mV"],
                        "a": 1,
                        "why": r'''
$q = 5.0/2^{10} = 5.0/1024 = 4.883$ mV. The common slip is to divide by $2^{10}-1 =
1023$, giving 4.888 mV; that is the spacing between the *first* and *last* code centres
rather than the width of one step, and which convention a datasheet uses is worth
checking, though the difference is a tenth of a percent. Answering 9.77 mV divides by
512, which is $2^9$ — an off-by-one in the exponent, and a factor of two in the answer.
''',
                    },
                    {
                        "q": "A 12-bit converter on a 3.3 V reference truncates rather than rounds. Its worst-case error in reconstructing the input voltage is:",
                        "opts": ["zero", "about 403 µV", "about 806 µV", "about 1.6 mV"],
                        "a": 2,
                        "why": r'''
A truncating converter reports the code *below* the input, so the input can be anywhere
in a band one LSB wide above what the code represents: the error runs from 0 up to
$q = 3.3/4096 = 806$ µV. The answer 403 µV is $q/2$, which is the worst case for a
converter that rounds — the same hardware with half an LSB of offset added, which is
exactly how it is usually arranged, and why $\pm\frac{1}{2}$ LSB is the figure most
often quoted. Knowing which of the two you have is worth one bit of accuracy.
''',
                    },
                    {
                        "q": "A signal at 6 kHz is sampled at 10 kHz with no anti-alias filter. At what frequency does it appear in the samples?",
                        "opts": ["4 kHz", "6 kHz", "1 kHz", "16 kHz"],
                        "a": 0,
                        "why": r'''
It folds about half the sample rate: $10 - 6 = 4$ kHz. The samples are now
indistinguishable from a genuine 4 kHz signal, and nothing downstream can undo that —
which is the whole reason the anti-alias filter is analogue and sits in front of the
converter rather than in the code afterwards. Answering 6 kHz assumes the converter
records what it was given; it records only the instants it looked, and several
different waves fit the same instants.
''',
                    },
                    {
                        "q": "Two numbers are held in Q15, so 0.5 is stored as 16384. They are multiplied as 32-bit integers. What must be done to the product to get a Q15 result?",
                        "opts": [
                            "nothing — the product is already Q15",
                            "shift it left by 15",
                            "divide it by 32767",
                            "shift it right by 15",
                        ],
                        "a": 3,
                        "why": r'''
Multiplying a Q15 by a Q15 gives a Q30 product: both scale factors of $2^{15}$ are
present, so the result is $2^{30}$ times the real answer. Shifting right by 15 removes
one of them. Concretely, $16384 \times 16384 = 268435456$, and shifting that right by
15 gives 8192, which in Q15 is 0.25 — correct. Dividing by 32767 is the reflex of
thinking the format's largest value is the scale factor; the scale factor is $2^{15} =
32768$, and 32767 is merely the largest integer that fits.
''',
                    },
                ],
            },
            "derive": {
                "title": "From reference voltage to one bit of the answer",
                "minutes": 12,
                "vars": ["V_ref", "N", "q", "A", "B", "f"],
                "brief": r'''
Four short steps that put the numbers behind the module on one page: what a converter
divides its reference into, what one division is worth, how wrong the answer can be,
and what happens to the scale factor when two fixed-point numbers meet.

Throughout, $V_{ref}$ is the reference voltage, $N$ is the number of bits, and $q$ is
the size of one step.
''',
                "steps": [
                    {
                        "prompt": "An $N$-bit converter reports a code made of $N$ binary digits. How many distinct codes is that?",
                        "answer": "2^{N}",
                        "hint": "Each bit doubles the number of patterns available.",
                        "deconstruct": [
                            "One bit gives 2 codes, two bits give 4, three give 8.",
                            "So $N$ bits give $2^N$, running from 0 to $2^N - 1$.",
                        ],
                    },
                    {
                        "prompt": "Those codes divide the reference into equal steps. Write the size $q$ of one step, in terms of $V_{ref}$ and $N$.",
                        "given": "The full-scale span is $V_{ref}$, shared out among the codes you just counted.",
                        "answer": "\\frac{V_{ref}}{2^{N}}",
                        "hint": "Divide the span by the number of steps. Nothing else is involved.",
                        "deconstruct": [
                            "The span is $V_{ref}$ and there are $2^N$ steps across it.",
                            "So one step is $V_{ref}/2^N$ — for 12 bits on 3.3 V, 806 µV.",
                        ],
                    },
                    {
                        "prompt": "A converter that rounds to the nearest code is wrong by at most half a step. Write that worst-case error in terms of $V_{ref}$ and $N$ alone.",
                        "given": "You have just shown that one step is $q = V_{ref}/2^{N}$.",
                        "answer": "\\frac{V_{ref}}{2^{N+1}}",
                        "hint": "Halve $q$. Halving a power of two is the same as adding one to the exponent underneath.",
                        "deconstruct": [
                            "Half of $q$ is $\\frac{1}{2} \\cdot \\frac{V_{ref}}{2^{N}}$.",
                            "And $\\frac{1}{2} \\cdot \\frac{1}{2^{N}} = \\frac{1}{2^{N+1}}$.",
                        ],
                    },
                    {
                        "prompt": "In Q$f$ format the real number $a$ is stored as the integer $A = a \\cdot 2^{f}$, and $b$ as $B = b \\cdot 2^{f}$. Write the integer that represents the product $ab$ in the same Q$f$ format, in terms of $A$, $B$ and $f$.",
                        "given": "The stored integer for a real number $x$ is always $x \\cdot 2^{f}$, so the answer you want is $ab \\cdot 2^{f}$.",
                        "answer": "\\frac{A B}{2^{f}}",
                        "hint": "Multiply $A$ by $B$ and see how many factors of $2^{f}$ you are left holding.",
                        "deconstruct": [
                            "$A B = a \\cdot 2^{f} \\cdot b \\cdot 2^{f} = ab \\cdot 2^{2f}$.",
                            "You wanted $ab \\cdot 2^{f}$, so there is one factor of $2^{f}$ too many.",
                            "Dividing it out is a right shift by $f$ bits, which is why the operation is written `(A * B) >> f`.",
                        ],
                    },
                ],
                "closing": r'''
The last step is the whole of fixed-point multiplication, and the two practical
warnings both live in it. $AB$ needs twice the width of $A$ and $B$, so a Q15 multiply
must be evaluated in 32 bits before the shift. And the shift discards the bits below
the point rather than rounding them, so repeated multiplication drifts downwards — the
fix is to add half a step, $2^{f-1}$, before shifting, which is exactly the `+ 16384`
you will write in the lab.
''',
            },
            "lab": {
                "title": "A converter and a Q15 multiply",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Six functions covering the path from a voltage to an integer and back, and the
arithmetic you are left with once the floats are gone.

The first three are the converter, written with floats so you can see what the hardware
is doing:

- `lsb(vref, bits)` — the size of one step, in volts.
- `adc_code(volts, vref, bits)` — the integer a **truncating** converter returns:
  the number of whole steps that fit in `volts`, clamped to the range 0 to
  $2^{\text{bits}} - 1$. An input above the reference gives the top code, and a
  negative input gives 0.
- `code_to_volts(code, vref, bits)` — the voltage that code stands for, which is the
  bottom of its band.

The last three are the integer world:

- `to_fixed(x, frac)` — the Q`frac` integer for the real number `x`, rounded to
  nearest. Use `math.floor(x * (1 << frac) + 0.5)`, which rounds halves upwards and
  behaves consistently for negative numbers.
- `fx_mul(a, b, frac)` — two Q`frac` integers multiplied, returned in Q`frac`. This is
  one line: `(a * b) >> frac`. Python's `>>` on a negative integer rounds towards
  minus infinity, exactly as a C compiler's arithmetic shift does on a signed type.
- `saturate(x, bits)` — clamp `x` to the range of a signed `bits`-bit two's-complement
  integer, which is $-2^{bits-1}$ to $2^{bits-1} - 1$. Saturating is what you do
  instead of letting a value wrap: a sensor reading that runs off the top of its range
  should stay at the top, not reappear at the bottom.

`math` is imported for you and is all you need.

One thing to notice while you are here: `to_fixed(1.0, 15)` is 32768, which does not
fit in a signed 16-bit integer. Q15 represents the half-open range $[-1, 1)$, so 1.0
itself is not in it. That is not a defect in your code; it is what the format is.
''',
                "files": [{"name": "main.py", "content": r'''
"""From a voltage to an integer, and the arithmetic afterwards."""

import math


def lsb(vref, bits):
    """The size of one converter step, in volts."""
    # TODO: the reference divided by the number of steps.
    return 0.0


def adc_code(volts, vref, bits):
    """The code a truncating converter returns, clamped to its range."""
    # TODO: how many whole steps fit in `volts`, then clamp to 0 .. 2**bits - 1.
    return 0


def code_to_volts(code, vref, bits):
    """The voltage a code stands for: the bottom of its band."""
    # TODO: the code counts steps, so multiply by the step size.
    return 0.0


def to_fixed(x, frac):
    """The Q`frac` integer for the real number `x`, rounded to nearest."""
    # TODO: math.floor(x * (1 << frac) + 0.5)
    return 0


def fx_mul(a, b, frac):
    """Two Q`frac` integers multiplied, returned in Q`frac`."""
    # TODO: the product is Q(2*frac); shift it back down.
    return 0


def saturate(x, bits):
    """Clamp `x` to the range of a signed `bits`-bit two's-complement integer."""
    # TODO: work out the two limits from `bits`, then clamp.
    return 0


if __name__ == "__main__":
    print("one 12-bit step on 3.3 V:", lsb(3.3, 12), "V")
    code = adc_code(1.0, 3.3, 12)
    print("1.000 V reads as code", code, "=", code_to_volts(code, 3.3, 12), "V")
    half = to_fixed(0.5, 15)
    print("0.5 in Q15 is", half, "and 0.5 * 0.5 is", fx_mul(half, half, 15))
    print("40000 saturated to 16 bits:", saturate(40000, 16))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""From a voltage to an integer, and the arithmetic afterwards."""

import math


def lsb(vref, bits):
    """The size of one converter step, in volts."""
    return vref / (1 << bits)


def adc_code(volts, vref, bits):
    """The code a truncating converter returns, clamped to its range."""
    top = (1 << bits) - 1
    code = math.floor(volts / lsb(vref, bits))
    if code < 0:
        return 0
    if code > top:
        return top
    return code


def code_to_volts(code, vref, bits):
    """The voltage a code stands for: the bottom of its band."""
    return code * lsb(vref, bits)


def to_fixed(x, frac):
    """The Q`frac` integer for the real number `x`, rounded to nearest."""
    return math.floor(x * (1 << frac) + 0.5)


def fx_mul(a, b, frac):
    """Two Q`frac` integers multiplied, returned in Q`frac`."""
    return (a * b) >> frac


def saturate(x, bits):
    """Clamp `x` to the range of a signed `bits`-bit two's-complement integer."""
    lo = -(1 << (bits - 1))
    hi = (1 << (bits - 1)) - 1
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


if __name__ == "__main__":
    print("one 12-bit step on 3.3 V:", lsb(3.3, 12), "V")
    code = adc_code(1.0, 3.3, 12)
    print("1.000 V reads as code", code, "=", code_to_volts(code, 3.3, 12), "V")
    half = to_fixed(0.5, 15)
    print("0.5 in Q15 is", half, "and 0.5 * 0.5 is", fx_mul(half, half, 15))
    print("40000 saturated to 16 bits:", saturate(40000, 16))
'''}],
                "hints": [
                    "`lsb` is `vref / (1 << bits)`. Using `2 ** bits` is identical; the shift is the form you will meet in C.",
                    "In `adc_code`, divide first and take `math.floor` of the result, then clamp. Clamping before flooring lets a value just above full scale through.",
                    "`code_to_volts` deliberately does not add half a step. The code stands for the bottom of its band, which is why a truncating converter reads low.",
                    "`fx_mul` is one line. Resist writing `int(a * b / 2 ** frac)` — that goes through a float and loses the exactness that was the point of fixed point.",
                    "In `saturate`, `lo` and `hi` are not symmetric: two's complement has one more negative value than positive, so 16 bits run from −32768 to +32767.",
                ],
                "tests": [
                    {"name": "one step of a 12-bit converter on 3.3 V", "code": r'''
q = lsb(3.3, 12)
assert abs(q - 0.0008056640625) < 1e-15, f"3.3 / 4096 is 0.0008056640625 V, got {q}"
assert abs(lsb(5.0, 10) - 0.0048828125) < 1e-15, "5.0 / 1024 is 4.8828125 mV"
'''},
                    {"name": "a voltage becomes a code, and clamps at both ends", "code": r'''
c = adc_code(1.0, 3.3, 12)
assert c == 1241, f"1.0 V is 1241 whole steps of 805.7 uV, got {c}"
assert adc_code(2.5, 5.0, 10) == 512, "half of a 10-bit range is code 512"
assert adc_code(4.0, 3.3, 12) == 4095, "an input above the reference must clamp to 4095"
assert adc_code(-0.5, 3.3, 12) == 0, "a negative input must clamp to 0"
'''},
                    {"name": "a code becomes a voltage again, low by up to one step", "code": r'''
v = code_to_volts(1241, 3.3, 12)
assert abs(v - 0.9998291015624999) < 1e-12, f"1241 steps is 0.99983 V, got {v}"
err = 1.0 - code_to_volts(adc_code(1.0, 3.3, 12), 3.3, 12)
assert 0.0 <= err < lsb(3.3, 12), \
    f"a truncating converter reads low by between 0 and one step, got {err}"
assert abs(code_to_volts(4095, 3.3, 12) - 3.2991943359375) < 1e-12, \
    "the top code is one step below the reference"
'''},
                    {"name": "Q15 stores a fraction as an integer", "code": r'''
assert to_fixed(0.5, 15) == 16384, f"0.5 * 32768 is 16384, got {to_fixed(0.5, 15)}"
assert to_fixed(-0.5, 15) == -16384, f"got {to_fixed(-0.5, 15)}"
assert to_fixed(0.1, 15) == 3277, \
    f"0.1 * 32768 is 3276.8, which rounds to 3277, got {to_fixed(0.1, 15)}"
assert to_fixed(1.0, 15) == 32768, \
    "1.0 maps to 32768 — outside signed 16 bits, which is the point of the note in the brief"
'''},
                    {"name": "a Q15 multiply shifts the scale factor back out", "code": r'''
half = to_fixed(0.5, 15)
assert fx_mul(half, half, 15) == 8192, \
    f"0.5 * 0.5 is 0.25, which is 8192 in Q15, got {fx_mul(half, half, 15)}"
assert fx_mul(-half, half, 15) == -8192, "a negative operand keeps its sign"
tenth = to_fixed(0.1, 15)
assert fx_mul(tenth, tenth, 15) == 327, \
    f"0.1 * 0.1 lands one count below the ideal 328 because the shift truncates, got {fx_mul(tenth, tenth, 15)}"
'''},
                    {"name": "saturation is asymmetric, as two's complement is", "code": r'''
assert saturate(100, 16) == 100, "a value inside the range passes through unchanged"
assert saturate(40000, 16) == 32767, f"got {saturate(40000, 16)}"
assert saturate(-40000, 16) == -32768, f"got {saturate(-40000, 16)}"
assert saturate(200, 8) == 127 and saturate(-200, 8) == -128, \
    "8 bits run from -128 to +127"
'''},
                    {"name": "the whole chain, from volts to a Q15 fraction", "code": r'''
code = adc_code(1.65, 3.3, 12)
frac = code / 4096.0
q15 = to_fixed(frac, 15)
assert code == 2048, f"half the reference is code 2048, got {code}"
assert q15 == 16384, f"a half-scale reading is 0.5 in Q15, got {q15}"
scaled = fx_mul(q15, to_fixed(0.25, 15), 15)
assert scaled == 4096, \
    f"0.5 scaled by a Q15 gain of 0.25 is 0.125, which is 4096 in Q15, got {scaled}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A bare-metal sensor channel, in integers",
        "runtime": "python",
        "minutes": 150,
        "brief": r'''
Everything in this course now has to run together against a peripheral you cannot see
inside. `mcu.py` is a small simulated microcontroller: a dictionary of 32-bit registers
at fixed addresses, an ADC that takes a few accesses to finish a conversion, and a log
of every access anyone makes. You may read it. You may not edit it, and you may not
reach into `mcu.reg` — the only way in is `read32` and `write32`, exactly as it would
be on real silicon.

Your job is the driver and the maths on top of it, with no floating point anywhere in
the signal path.

## The peripheral

```text
GPIO_ODR   output data register — one bit per pin
ADC_CR     control:  bit 0 = START, written to begin a conversion
ADC_SR     status:   bit 1 = READY, set when a result is waiting.
                     Write-1-to-clear: writing a 1 clears it, writing a 0 leaves it.
ADC_DR     data:     the 12-bit result of the last conversion
TIM_ARR    timer auto-reload — the counter wraps after ARR + 1 ticks
TIM_CCR1   timer compare — the output is high for CCR1 of those ticks
```

A conversion does not finish immediately. After START is written, the result appears a
couple of accesses later, so the driver has to poll READY rather than assume. If you
read DR without waiting, you get the previous conversion — which is the classic way an
ADC channel ends up reporting the value it had one sample ago, forever.

## What you are building

1. `set_bits(mcu, addr, mask)`, `clear_bits(mcu, addr, mask)` and
   `all_set(mcu, addr, mask)` — read-modify-write helpers over `read32`/`write32`.
   `all_set` returns `True` only when every bit of the mask is set.
2. `read_adc(mcu)` — start a conversion, poll until READY, read the result, clear
   READY, and return the raw code. Clearing READY must be a write-1-to-clear write, not
   a read-modify-write, or the next conversion will look ready before it is.
3. `to_millivolts(code, vref_mv, bits)` — the reading in millivolts, using integers
   only: `(code * vref_mv) >> bits`. Multiply first and shift afterwards, or the
   multiplication has nothing left to work with.
4. `iir_q15(state, sample, alpha_q15)` — one step of a first-order low-pass, in
   integers:

   ```text
   state + ((alpha_q15 * (sample - state) + 16384) >> 15)
   ```

   The `+ 16384` is the half-step from the derivation, added before the shift so the
   filter rounds instead of always truncating downwards.
5. `pwm_compare(arr, percent)` — the compare value for a duty cycle given as a whole
   percentage, rounded to nearest: `((arr + 1) * percent + 50) // 100`.

## The thing to look for

Run the filter for a long time against a constant input and watch where it stops. With
`alpha_q15 = 3277` it settles four counts short of its target and stays there: once the
difference is small enough, `(3277 * d + 16384) >> 15` is zero and the state cannot
move. That dead band is not a bug in your code, it is what fixed point costs, and it is
why a fixed-point control loop needs either a wider state or an integrator that
accumulates the remainder. Say which you would choose, in a comment.

## Constraints

The standard library only. No floats in `read_adc`, `to_millivolts`, `iir_q15` or
`pwm_compare` — the checks test that the values you return are Python `int`s, and a
single `/` will turn one into a `float`.
''',
        "deliverables": [
            "`set_bits`, `clear_bits` and `all_set`, implemented as read-modify-write sequences over the mcu's `read32` and `write32` and nothing else.",
            "`read_adc`, driving the full conversion protocol: write START, poll READY, read DR, clear READY write-1-to-clear — verified against the peripheral's own access log rather than against its result alone.",
            "`to_millivolts`, converting a raw code to millivolts with integer arithmetic only, returning an `int`.",
            "`iir_q15`, one step of a rounded Q15 first-order low-pass, returning an `int`.",
            "`pwm_compare`, the timer compare value for a whole-percentage duty cycle, plus a comment in `main.py` naming which fix you would use for the filter's dead band and why.",
        ],
        "constraints": [
            "The standard library only. No NumPy.",
            "Do not edit `mcu.py`, and do not touch `mcu.reg`, `mcu.samples_mv` or any other attribute directly — `read32` and `write32` are the whole interface, as they would be on hardware.",
            "No floating point in the signal path. `read_adc`, `to_millivolts`, `iir_q15` and `pwm_compare` must all return `int`.",
            "`read_adc` must poll. Reading `ADC_DR` without first seeing READY set is the defect the checks are looking for.",
            "Clear READY by writing the bit, not by reading, clearing and writing back.",
        ],
        "rubric": [
            {"criterion": "Register discipline", "weight": 20,
             "evidence": "set_bits, clear_bits and all_set change only the bits named by the mask, leave every other bit of the word as it was, and go through read32/write32 rather than the register dictionary."},
            {"criterion": "Conversion protocol", "weight": 30,
             "evidence": "read_adc writes START, polls READY at least twice before reading DR, clears READY with a write-1-to-clear, and returns fresh data on consecutive calls rather than repeating the first result."},
            {"criterion": "Integer signal path", "weight": 25,
             "evidence": "to_millivolts and pwm_compare return exact integers matching hand calculation across the full range, including the endpoints, with no float appearing anywhere."},
            {"criterion": "Fixed-point filter", "weight": 25,
             "evidence": "iir_q15 rounds rather than truncates, converges towards a constant input from both directions, and its residual dead band is measured and accounted for in the comment."},
        ],
        "hints": [
            "`set_bits` is three lines: read the word, OR the mask in, write it back. `clear_bits` is the same with `& ~mask`, and remember to mask the result to 32 bits before writing.",
            "`all_set` reads once and compares `word & mask` with `mask`. Comparing with zero answers a different question, and for a single-bit mask you will not notice the difference until you use it on two bits.",
            "`read_adc` in order: `set_bits(mcu, ADC_CR, ADC_CR_START)`, then `while not all_set(mcu, ADC_SR, ADC_SR_READY): pass`, then `code = mcu.read32(ADC_DR)`, then `mcu.write32(ADC_SR, ADC_SR_READY)`.",
            "That last write is a plain write, not a read-modify-write. In a write-1-to-clear register, writing back the flags you just read clears all of them.",
            "If a check reports the same code twice, READY was never cleared, so the second poll loop exited immediately and read a conversion that had not finished.",
            "In `to_millivolts`, `(code * vref_mv) >> bits` keeps everything in integers. Writing `code * (vref_mv / (1 << bits))` produces a float and fails the type check even when the number looks right.",
            "For the dead-band comment: the two usual fixes are to hold the filter state in a wider format — Q15 millivolts rather than whole millivolts — or to keep the discarded remainder and add it back on the next step. Pick one and say what it costs.",
        ],
        "files": [
            {"name": "mcu.py", "ro": True, "content": r'''
"""A very small memory-mapped machine. Read it; do not edit it.

Nothing here knows anything about your driver. It exposes two operations, read32 and
write32, and it records every one of them so the checks can see how the peripheral was
driven rather than only what your functions returned.

The ADC is deliberately not instantaneous: writing START begins a conversion that
completes a couple of bus accesses later. A driver that reads ADC_DR without waiting
for READY gets whatever was there before.
"""

GPIO_MODER = 0x40020000
GPIO_ODR = 0x40020014
ADC_CR = 0x40012400
ADC_SR = 0x40012404
ADC_DR = 0x40012408
TIM_ARR = 0x40000C2C
TIM_CCR1 = 0x40000C34

ADC_CR_START = 1 << 0
ADC_SR_READY = 1 << 1

WORD = 0xFFFFFFFF


class Mcu(object):
    """Registers, an ADC with a settling time, and an access log."""

    def __init__(self, samples_mv=(1650,), vref_mv=3300, bits=12):
        self.reg = {
            GPIO_MODER: 0, GPIO_ODR: 0,
            ADC_CR: 0, ADC_SR: 0, ADC_DR: 0,
            TIM_ARR: 0, TIM_CCR1: 0,
        }
        self.samples_mv = list(samples_mv)
        self.vref_mv = vref_mv
        self.bits = bits
        self.log = []          # ('r', addr) and ('w', addr, value), in order
        self.conversions = 0
        self._pending = 0
        self._ticks = 0

    # -- the bus ---------------------------------------------------------
    def read32(self, addr):
        if addr not in self.reg:
            raise KeyError("no register at 0x%08X" % addr)
        self.log.append(("r", addr))
        self._tick()
        return self.reg[addr] & WORD

    def write32(self, addr, value):
        if addr not in self.reg:
            raise KeyError("no register at 0x%08X" % addr)
        value = int(value) & WORD
        self.log.append(("w", addr, value))
        if addr == ADC_SR:
            # write-1-to-clear: a 1 clears the flag, a 0 leaves it alone
            self.reg[ADC_SR] = self.reg[ADC_SR] & ~value & WORD
        else:
            self.reg[addr] = value
            if addr == ADC_CR and (value & ADC_CR_START) and self._pending == 0:
                self._pending = 3
        self._tick()

    # -- the ADC ---------------------------------------------------------
    def _tick(self):
        self._ticks += 1
        if self._ticks > 100000:
            raise RuntimeError(
                "100000 bus accesses and still going. A poll loop is waiting for a "
                "flag that nothing will ever set - check that START was written."
            )
        if self._pending <= 0:
            return
        self._pending -= 1
        if self._pending:
            return
        mv = self.samples_mv[self.conversions % len(self.samples_mv)]
        self.conversions += 1
        code = (int(mv) * (1 << self.bits)) // self.vref_mv
        if code < 0:
            code = 0
        top = (1 << self.bits) - 1
        if code > top:
            code = top
        self.reg[ADC_DR] = code
        self.reg[ADC_SR] = self.reg[ADC_SR] | ADC_SR_READY
        self.reg[ADC_CR] = self.reg[ADC_CR] & ~ADC_CR_START & WORD

    # -- helpers for the checks -----------------------------------------
    def reads_of(self, addr):
        return [e for e in self.log if e[0] == "r" and e[1] == addr]

    def writes_of(self, addr):
        return [e for e in self.log if e[0] == "w" and e[1] == addr]
'''},
            {"name": "main.py", "content": r'''
"""A sensor channel with no floating-point unit underneath it.

Dead band: TODO - say which fix you would use and what it costs.
"""

from mcu import (
    Mcu, GPIO_ODR, ADC_CR, ADC_SR, ADC_DR, TIM_ARR, TIM_CCR1,
    ADC_CR_START, ADC_SR_READY,
)

WORD = 0xFFFFFFFF


def set_bits(mcu, addr, mask):
    """Read-modify-write: set every bit of `mask` in the register at `addr`."""
    # TODO: read32, OR the mask in, write32 the result back.
    return None


def clear_bits(mcu, addr, mask):
    """Read-modify-write: clear every bit of `mask` in the register at `addr`."""
    # TODO: read32, AND with ~mask, write32 the result back.
    return None


def all_set(mcu, addr, mask):
    """True when every bit of `mask` is set in the register at `addr`."""
    # TODO: one read32, then compare the masked word with the mask.
    return False


def read_adc(mcu):
    """Start a conversion, wait for it, return the raw code, clear the flag."""
    # TODO: START, poll READY, read ADC_DR, clear READY with a write-1-to-clear.
    return 0


def to_millivolts(code, vref_mv, bits):
    """The reading in millivolts, integers only."""
    # TODO: multiply by the reference first, then shift right by `bits`.
    return 0


def iir_q15(state, sample, alpha_q15):
    """One step of a rounded first-order low-pass, entirely in integers."""
    # TODO: state + ((alpha_q15 * (sample - state) + 16384) >> 15)
    return 0


def pwm_compare(arr, percent):
    """Timer compare value for a whole-percentage duty cycle, rounded to nearest."""
    # TODO: ((arr + 1) * percent + 50) // 100
    return 0


if __name__ == "__main__":
    mcu = Mcu(samples_mv=[1650] * 8)
    state = 0
    for _ in range(8):
        mv = to_millivolts(read_adc(mcu), 3300, 12)
        state = iir_q15(state, mv, 3277)
    print("after 8 samples the filter reads", state, "mV")
    print("50% duty on a 1000-tick period is CCR1 =", pwm_compare(999, 50))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""A sensor channel with no floating-point unit underneath it.

Dead band: with alpha_q15 = 3277 the filter stops four counts short of a constant
input, because once the difference d falls below 5, (3277 * d + 16384) >> 15 is zero
and the state cannot move. I would hold the state in Q15 millivolts rather than whole
millivolts - one extra shift on the way in and out, no extra multiplies, and the dead
band shrinks by a factor of 32768. Keeping the discarded remainder would also work and
costs one more integer of state, but it makes the filter's response depend on its
history, which is harder to reason about when something goes wrong.
"""

from mcu import (
    Mcu, GPIO_ODR, ADC_CR, ADC_SR, ADC_DR, TIM_ARR, TIM_CCR1,
    ADC_CR_START, ADC_SR_READY,
)

WORD = 0xFFFFFFFF


def set_bits(mcu, addr, mask):
    """Read-modify-write: set every bit of `mask` in the register at `addr`."""
    mcu.write32(addr, (mcu.read32(addr) | mask) & WORD)


def clear_bits(mcu, addr, mask):
    """Read-modify-write: clear every bit of `mask` in the register at `addr`."""
    mcu.write32(addr, (mcu.read32(addr) & ~mask) & WORD)


def all_set(mcu, addr, mask):
    """True when every bit of `mask` is set in the register at `addr`."""
    return (mcu.read32(addr) & mask) == mask


def read_adc(mcu):
    """Start a conversion, wait for it, return the raw code, clear the flag."""
    set_bits(mcu, ADC_CR, ADC_CR_START)
    while not all_set(mcu, ADC_SR, ADC_SR_READY):
        pass
    code = mcu.read32(ADC_DR)
    # write-1-to-clear: a plain write of the one bit, never a read-modify-write
    mcu.write32(ADC_SR, ADC_SR_READY)
    return int(code)


def to_millivolts(code, vref_mv, bits):
    """The reading in millivolts, integers only."""
    return (int(code) * int(vref_mv)) >> bits


def iir_q15(state, sample, alpha_q15):
    """One step of a rounded first-order low-pass, entirely in integers."""
    return int(state) + ((int(alpha_q15) * (int(sample) - int(state)) + 16384) >> 15)


def pwm_compare(arr, percent):
    """Timer compare value for a whole-percentage duty cycle, rounded to nearest."""
    return ((int(arr) + 1) * int(percent) + 50) // 100


if __name__ == "__main__":
    mcu = Mcu(samples_mv=[1650] * 8)
    state = 0
    for _ in range(8):
        mv = to_millivolts(read_adc(mcu), 3300, 12)
        state = iir_q15(state, mv, 3277)
    print("after 8 samples the filter reads", state, "mV")
    print("50% duty on a 1000-tick period is CCR1 =", pwm_compare(999, 50))
'''},
        ],
        "tests": [
            {"name": "the bit helpers touch only the bits of the mask", "code": r'''
m = Mcu()
m.write32(GPIO_ODR, 0x00000085)
set_bits(m, GPIO_ODR, 1 << 5)
assert m.read32(GPIO_ODR) == 0xA5, \
    f"setting bit 5 of 0x85 gives 0xA5, got {hex(m.read32(GPIO_ODR))}"
clear_bits(m, GPIO_ODR, 1 << 0)
assert m.read32(GPIO_ODR) == 0xA4, \
    f"clearing bit 0 of 0xA5 gives 0xA4, got {hex(m.read32(GPIO_ODR))}"
assert all_set(m, GPIO_ODR, 0b100), "bit 2 is set in 0xA4"
assert not all_set(m, GPIO_ODR, 0b101), \
    "bit 0 was cleared, so 'all of bits 0 and 2' is False"
m.write32(GPIO_ODR, 0xFFFFFFFF)
clear_bits(m, GPIO_ODR, 1 << 31)
assert m.read32(GPIO_ODR) == 0x7FFFFFFF, \
    f"the result must stay a positive 32-bit word, got {hex(m.read32(GPIO_ODR))}"
assert not all_set(m, GPIO_ODR, 1 << 31), "bit 31 was just cleared"
'''},
            {"name": "the helpers go through the bus, not round it", "code": r'''
m = Mcu()
before = len(m.log)
set_bits(m, GPIO_ODR, 1 << 3)
entries = m.log[before:]
kinds = [e[0] for e in entries]
assert kinds == ["r", "w"], \
    f"set_bits should be exactly one read then one write, got {kinds}"
assert entries[1][2] == (1 << 3), \
    f"the value written should be the modified word, got {hex(entries[1][2])}"
'''},
            {"name": "read_adc drives the whole conversion protocol", "code": r'''
m = Mcu(samples_mv=[500])
before = len(m.log)
code = read_adc(m)
seq = m.log[before:]
starts = [e for e in seq if e[0] == "w" and e[1] == ADC_CR and (e[2] & ADC_CR_START)]
assert starts, "no write to ADC_CR ever set the START bit"
first_dr = next((i for i, e in enumerate(seq) if e[0] == "r" and e[1] == ADC_DR), None)
assert first_dr is not None, "ADC_DR was never read"
sr_polls = [i for i, e in enumerate(seq[:first_dr]) if e[0] == "r" and e[1] == ADC_SR]
assert len(sr_polls) >= 2, \
    f"the result is not ready immediately; ADC_SR must be polled until READY, got {len(sr_polls)} read(s)"
clears = [e for e in seq if e[0] == "w" and e[1] == ADC_SR and (e[2] & ADC_SR_READY)]
assert clears, "READY was never cleared, so the next conversion will look ready at once"
assert code == 620, f"500 mV on a 3.3 V 12-bit converter is code 620, got {code}"
assert isinstance(code, int) and not isinstance(code, bool), \
    f"read_adc must return an int — nothing in the signal path may be a float, got {type(code).__name__}"
'''},
            {"name": "consecutive conversions return fresh data", "code": r'''
m = Mcu(samples_mv=[500, 1500])
a = read_adc(m)
b = read_adc(m)
assert a == 620, f"the first sample is 500 mV, code 620, got {a}"
assert b == 1861, \
    f"the second sample is 1500 mV, code 1861 - getting {b} means READY was not cleared"
assert m.conversions == 2, \
    f"exactly two conversions should have been started, the peripheral counted {m.conversions}"
'''},
            {"name": "codes become millivolts with no float in sight", "code": r'''
mv = to_millivolts(1241, 3300, 12)
assert mv == 999, f"(1241 * 3300) >> 12 is 999, got {mv}"
assert isinstance(mv, int) and not isinstance(mv, bool), \
    f"to_millivolts must return an int, got {type(mv).__name__}"
assert to_millivolts(0, 3300, 12) == 0, "code 0 is 0 mV"
assert to_millivolts(2048, 3300, 12) == 1650, "half scale is half the reference"
assert to_millivolts(4095, 3300, 12) == 3299, "the top code is one step short of 3300 mV"
'''},
            {"name": "the Q15 filter rounds, converges, and stalls where it should", "code": r'''
s = iir_q15(0, 1000, 3277)
assert s == 100, f"one tenth of the way from 0 to 1000 is 100, got {s}"
assert isinstance(s, int) and not isinstance(s, bool), \
    f"iir_q15 must return an int, got {type(s).__name__}"
s = 0
for _ in range(200):
    s = iir_q15(s, 1000, 3277)
assert s == 996, f"the filter stalls four counts short of 1000; got {s}"
d = 1000
for _ in range(300):
    d = iir_q15(d, 0, 3277)
assert d == 4, f"coming down from 1000 it stalls four counts above 0; got {d}"
'''},
            {"name": "the timer compare value is exact at both ends", "code": r'''
assert pwm_compare(999, 0) == 0, "0% duty is compare 0"
assert pwm_compare(999, 50) == 500, f"50% of 1000 ticks is 500, got {pwm_compare(999, 50)}"
assert pwm_compare(999, 100) == 1000, \
    f"100% duty needs the full 1000 ticks, not 999, got {pwm_compare(999, 100)}"
assert pwm_compare(999, 33) == 330, f"33% of 1000 is 330, got {pwm_compare(999, 33)}"
assert pwm_compare(255, 10) == 26, \
    f"10% of 256 is 25.6, which rounds to 26, got {pwm_compare(255, 10)}"
assert isinstance(pwm_compare(999, 50), int), "pwm_compare must return an int"
'''},
            {"name": "the whole channel, end to end", "code": r'''
m = Mcu(samples_mv=[1650] * 64)
state = 0
for _ in range(40):
    state = iir_q15(state, to_millivolts(read_adc(m), 3300, 12), 3277)
assert m.conversions == 40, \
    f"forty samples means forty conversions, the peripheral counted {m.conversions}"
assert state == 1627, \
    f"forty steps of a 0.1 filter towards 1650 mV from cold reaches 1627 mV, got {state}"
for _ in range(80):
    state = iir_q15(state, to_millivolts(read_adc(m), 3300, 12), 3277)
assert state == 1646, \
    f"another eighty steps gets to 1646 mV and stops there - the dead band; got {state}"
'''},
        ],
    },
}
