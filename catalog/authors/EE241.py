"""EE241 — Embedded C and Microcontrollers.

Second year. It assumes EE121 (Boolean algebra, gates, binary) and EE131 (Python:
functions, loops, lists, dicts), plus the Year 1 circuit courses for the two build
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
    ],
    "assessment": (
        "Four quizzes, two circuits drawn and measured in the schematic editor, one "
        "guided derivation, two Python labs checked by execution, and a capstone that "
        "drives a simulated memory-mapped peripheral through a complete integer-only "
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
Option B clears bit 5, which was already clear, so nothing happens at all; option D
writes `0x00000005`, setting bits 0 and 2 and clearing everything else, because 5 is
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
the code changes behaviour without being edited. Option C is the assumption that makes
this bug: reserved does not mean ignored, it means undefined, and undefined includes
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

        # ---- M3 -----------------------------------------------------------
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

        # ---- M4 -----------------------------------------------------------
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
                        "placeholder": "2^{N}",
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
                        "placeholder": "\\frac{V_{ref}}{2^{N}}",
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
                        "placeholder": "\\frac{V_{ref}}{2^{N+1}}",
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
                        "placeholder": "\\frac{A B}{2^{f}}",
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
