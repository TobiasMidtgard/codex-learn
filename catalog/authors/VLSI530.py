"""VLSI530 — RTL Design and Verification.

Track 6 of the EE M.S. The course a learner takes once they can read a datapath
and now has to build one that closes timing and can be proved right.

Authoring rules, as for every module in this catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * seed every RNG, and every expected value must be one that was computed
"""

COURSE = {
    "id": "VLSI530",
    "title": "RTL Design and Verification",
    "band": 6,
    "level": "Advanced",
    "prereqs": ["VLSI510"],
    "stack": ["Python", "Verilog"],
    "credits": 10,
    "hours": 130,
    "icon": "▣",
    "summary": (
        "Register transfer level is not a language, it is a discipline: state lives in "
        "registers, everything between them is combinational, and one clock edge advances "
        "the whole design at once. This course builds that model as executable code, uses "
        "it to write finite state machines and elastic ready/valid interfaces, budgets the "
        "clock period that makes it physical, and finishes with the bench that proves the "
        "design does what the specification said."
    ),
    "outcomes": [
        "Model a synchronous design cycle-accurately, with a two-phase update that makes non-blocking assignment a property of the simulator rather than a rule to memorise.",
        "Design a finite state machine, choose between Moore and Mealy outputs knowing what each costs in latency, and prove which states are reachable.",
        "Implement a ready/valid interface that loses no data under back-pressure, and say why a two-entry skid buffer sustains a transfer every cycle where a one-entry slice cannot.",
        "Budget a clock period from setup, hold, clock-to-Q and skew, and turn a slack figure into a decision about where to cut the pipeline.",
        "Write a self-checking testbench with an independent reference model, directed corner cases and seeded random stimulus, and demonstrate that it catches a real bug.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that builds an elastic two-stage datapath together with the bench that proves it correct under back-pressure.",
    "reading": [
        "*Digital Design and Computer Architecture*, Harris & Harris — chapters 3 and 4 for sequential logic and HDL discipline.",
        "*CMOS VLSI Design*, Weste & Harris — chapter 10 for the timing constraint written out properly.",
        "*SystemVerilog for Verification*, Spear & Tumbush — for what a self-checking bench looks like at industrial scale.",
        "Cummings, *Nonblocking Assignments in Verilog Synthesis* (SNUG 2000) — the paper the first module of this course reimplements.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The clocked model and the period it has to fit in",
            "summary": "One edge, one update, everywhere at once — and a period long enough for the slowest path between two registers.",
            "concepts": [
                "State lives only in registers. Everything between two registers is a function of the values they held at the last edge.",
                "The two-phase update: evaluate every next-state function from the *current* values, then commit them all together. That is what `<=` means, and why `a <= b; b <= a` swaps.",
                "A cycle-accurate model needs no time axis finer than the edge: cycle count is the only clock the model has.",
                "The setup constraint, written out: `T + t_skew >= t_cq + t_logic + t_setup`. Slack is what is left of the period.",
                "The hold constraint does not contain `T` at all — no amount of slowing the clock down fixes a hold violation.",
            ],
            "sandbox": {
                "title": "One row per instruction, one column per clock",
                "visualiser": "pipeline",
                "minutes": 8,
                "initial": {"dep": 0, "fwd": 0, "miss": 0},
                "brief": r'''
This grid is what a cycle-accurate model produces: rows are instructions, columns
are clock cycles, and each cell says which stage that instruction occupies in that
cycle. Nothing here is analogue. The model knows only which cycle a thing happened
in, which is exactly the resolution RTL gives you.

Every slider is at zero to begin with, so nothing is stalling.
''',
                "notice": [
                    "With every slider at zero, each row starts exactly one column right of the row above. That single-column step is one register handoff per edge, and it is the only thing a synchronous model ever does.",
                    "Nine instructions occupy thirteen columns, and the reading says CPI 1.44 rather than 1.00. The four extra cycles are fill and drain — a five-stage pipe cannot retire anything until the first instruction reaches the fifth stage.",
                    "Raise dependent pairs to 3 with forwarding off. Rows i1, i2 and i3 now start three columns after their predecessor instead of one; the two extra columns are the bubbles. Rows i4 to i8 step by one again, because the model only marks the first `dep` instructions after i0 as dependent.",
                    "Now switch forwarding on with dependent pairs still at 3. Every bubble vanishes at once and the reading returns to 13 cycles — the schedule becomes identical to the one you started with.",
                ],
            },
            "derive": {
                "title": "What has to fit between two edges",
                "minutes": 14,
                "vars": ["T", "t_cq", "t_logic", "t_setup", "t_hold", "t_skew", "t_short", "f_max", "slack"],
                "brief": r'''
Two flip-flops with combinational logic between them. The launching flop is clocked
at $t = 0$; the capturing flop is clocked one period later. Between those two edges,
three things have to happen in sequence:

- $t_{cq}$, the launching flop's clock-to-output delay
- $t_{logic}$, the propagation delay of the combinational cloud
- $t_{setup}$, the window before the capture edge during which the data must already
  be stable

The capture clock does not arrive at the same instant as the launch clock. Call the
difference $t_{skew}$, positive when the capture clock is *late*.
''',
                "steps": [
                    {
                        "prompt": "Ignore skew for a moment. Write the smallest clock period $T$ for which the data arrives in time.",
                        "answer": "t_{cq} + t_{logic} + t_{setup}",
                        "hint": "The three delays happen one after another, and all three must fit inside one period.",
                        "deconstruct": [
                            "Data leaves the launching flop $t_{cq}$ after the edge.",
                            "It arrives at the capturing flop $t_{logic}$ later.",
                            "It must be there $t_{setup}$ before the next edge, so the period cannot be shorter than the sum.",
                        ],
                    },
                    {
                        "prompt": "Now let the capture clock arrive $t_{skew}$ late. The data has that much longer to get there. Write the smallest period again.",
                        "answer": "t_{cq} + t_{logic} + t_{setup} - t_{skew}",
                        "hint": "A late capture edge lends time to this path. It is borrowed, not created — the next stage pays it back.",
                        "deconstruct": [
                            "The capture edge happens at $T + t_{skew}$ rather than at $T$.",
                            "So the requirement is $T + t_{skew} \\ge t_{cq} + t_{logic} + t_{setup}$.",
                            "Solve for $T$.",
                        ],
                    },
                    {
                        "prompt": "For a period $T$ that is actually given to you, the setup slack is how much of it is left over. Write the slack.",
                        "answer": "T + t_{skew} - t_{cq} - t_{logic} - t_{setup}",
                        "hint": "Slack is required-arrival minus actual-arrival, and a negative number is a violation.",
                        "deconstruct": [
                            "The data is required by $T + t_{skew} - t_{setup}$.",
                            "It actually arrives at $t_{cq} + t_{logic}$.",
                            "Subtract the second from the first.",
                        ],
                    },
                    {
                        "prompt": "Write the highest frequency this path will run at, in terms of the delays.",
                        "answer": "\\frac{1}{t_{cq} + t_{logic} + t_{setup} - t_{skew}}",
                        "hint": "Frequency is the reciprocal of the smallest period you already wrote.",
                        "deconstruct": [
                            "You have $T_{min}$ from the second step.",
                            "$f_{max} = 1/T_{min}$, and note that only the slowest path in the design gets a say.",
                        ],
                    },
                    {
                        "prompt": "Hold is the opposite failure: new data racing through the logic and overwriting the capture flop's input before it has finished sampling the old value. With $t_{short}$ the *fastest* path through the cloud, write the hold margin.",
                        "answer": "t_{cq} + t_{short} - t_{hold} - t_{skew}",
                        "hint": "New data must not arrive before $t_{hold}$ after the capture edge, and the capture edge is $t_{skew}$ late.",
                        "deconstruct": [
                            "The earliest new data can arrive is $t_{cq} + t_{short}$ after the launch edge.",
                            "It must not arrive before $t_{skew} + t_{hold}$.",
                            "The margin is the difference.",
                        ],
                    },
                ],
                "closing": r'''
Look at the last expression: $T$ is not in it. A hold violation cannot be fixed by
slowing the clock down, which is why it is the one that scraps silicon. Setup
failures show up as a maximum frequency; hold failures show up as a part that never
works at any speed.
''',
            },
            "lab": {
                "title": "A two-phase register kernel",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Everything later in this course runs on the kernel you write here.

A register is a value with two faces: `q`, which everyone reads during the cycle,
and `d`, which is being prepared for the next edge. Combinational logic reads `q`
and writes `d`. The edge copies `d` into `q` for every register in the design at the
same instant. That single rule is the whole of non-blocking assignment:

```verilog
always_ff @(posedge clk) begin
  a <= b;
  b <= a;      // this swaps, because both right-hand sides are the old values
end
```

Fill in:

- `Reg.drive(value)` — store the value in `d`, truncated to `width` bits. `q` must
  not move.
- `Reg.commit()` — the edge.
- `tick(regs)` — one edge for a whole design: every register commits.
- `run(regs, logic, cycles)` — for each cycle: record `tuple(r.q for r in regs)`,
  then call `logic(cycle)`, then tick. The snapshot is taken *before* the edge, so
  entry 0 is the reset state.
- `swap_trace`, `counter_trace`, `shift_trace` — three tiny designs built on it.

`shift_trace` is the one that catches a broken kernel: with a correct two-phase
update, the order in which the stages are driven inside `logic` makes no difference
at all.
''',
                "files": [{"name": "main.py", "content": r'''
class Reg:
    """A bank of `width` flip-flops. Reads see q; writes land in d."""

    def __init__(self, width, value=0):
        self.width = int(width)
        self.mask = (1 << self.width) - 1
        self.q = int(value) & self.mask
        self.d = self.q

    def drive(self, value):
        """Schedule `value` for the next edge, truncated to `width` bits."""
        # TODO: write d. q must not change here.
        pass

    def commit(self):
        """The clock edge: what was scheduled becomes what is read."""
        # TODO
        pass


def tick(regs):
    """One edge for a whole design: every register commits together."""
    # TODO
    pass


def run(regs, logic, cycles):
    """Snapshot, evaluate, commit — `cycles` times.

    Returns one tuple(r.q for r in regs) per cycle, taken before the edge.
    """
    out = []
    # TODO: for each cycle c: record the snapshot, call logic(c), then tick(regs).
    return out


def swap_trace(a0, b0, cycles):
    """Two 4-bit registers, each taking the other's value every cycle."""
    a = Reg(4, a0)
    b = Reg(4, b0)

    def logic(c):
        # TODO: a takes b, b takes a.
        pass

    return run([a, b], logic, cycles)


def counter_trace(width, cycles):
    """A free-running counter. Return its value in each cycle."""
    reg = Reg(width, 0)

    def logic(c):
        # TODO: count up. The register width does the wrapping for you.
        pass

    return [s[0] for s in run([reg], logic, cycles)]


def shift_trace(bits, depth=3):
    """A `depth`-stage shift register fed by `bits`. Return the tail each cycle.

    Runs for len(bits) + depth cycles so the last bit has time to fall out.
    """
    chain = [Reg(1, 0) for _ in range(depth)]

    def logic(c):
        # TODO: stage i takes stage i-1; stage 0 takes bits[c], or 0 once
        # the input has run out.
        pass

    return [s[-1] for s in run(chain, logic, len(bits) + depth)]


if __name__ == "__main__":
    print("swap:   ", swap_trace(1, 2, 4))
    print("counter:", counter_trace(3, 10))
    print("shift:  ", shift_trace([1, 0, 0, 0], 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class Reg:
    """A bank of `width` flip-flops. Reads see q; writes land in d."""

    def __init__(self, width, value=0):
        self.width = int(width)
        self.mask = (1 << self.width) - 1
        self.q = int(value) & self.mask
        self.d = self.q

    def drive(self, value):
        """Schedule `value` for the next edge, truncated to `width` bits."""
        self.d = int(value) & self.mask

    def commit(self):
        """The clock edge: what was scheduled becomes what is read."""
        self.q = self.d


def tick(regs):
    """One edge for a whole design: every register commits together."""
    for r in regs:
        r.commit()


def run(regs, logic, cycles):
    """Snapshot, evaluate, commit — `cycles` times."""
    out = []
    for c in range(cycles):
        out.append(tuple(r.q for r in regs))
        logic(c)
        tick(regs)
    return out


def swap_trace(a0, b0, cycles):
    """Two 4-bit registers, each taking the other's value every cycle."""
    a = Reg(4, a0)
    b = Reg(4, b0)

    def logic(c):
        a.drive(b.q)
        b.drive(a.q)

    return run([a, b], logic, cycles)


def counter_trace(width, cycles):
    """A free-running counter. Return its value in each cycle."""
    reg = Reg(width, 0)

    def logic(c):
        reg.drive(reg.q + 1)

    return [s[0] for s in run([reg], logic, cycles)]


def shift_trace(bits, depth=3):
    """A `depth`-stage shift register fed by `bits`. Return the tail each cycle."""
    chain = [Reg(1, 0) for _ in range(depth)]

    def logic(c):
        for i in range(depth - 1, 0, -1):
            chain[i].drive(chain[i - 1].q)
        chain[0].drive(bits[c] if c < len(bits) else 0)

    return [s[-1] for s in run(chain, logic, len(bits) + depth)]


if __name__ == "__main__":
    print("swap:   ", swap_trace(1, 2, 4))
    print("counter:", counter_trace(3, 10))
    print("shift:  ", shift_trace([1, 0, 0, 0], 3))
'''}],
                "hints": [
                    "`drive` writes `self.d` and nothing else. The moment it touches `self.q`, the swap stops working and the shift register collapses into a wire.",
                    "`run` records before it evaluates, so the first snapshot is the reset state and the list is `cycles` long.",
                    "In `shift_trace` the loop order is deliberately backwards. Write it forwards as well and check that the trace does not change — if it does, `drive` is committing early.",
                ],
                "tests": [
                    {"name": "a register holds its output until the edge", "code": r'''
_r = Reg(4, 3)
_r.drive(9)
assert _r.q == 3, f"q must not move when d is driven — got {_r.q}, expected 3"
_r.commit()
assert _r.q == 9, f"after the edge q should be the driven value 9, got {_r.q}"
'''},
                    {"name": "a register is only as wide as it was declared", "code": r'''
_r = Reg(4, 0)
_r.drive(0x1F)
_r.commit()
assert _r.q == 15, f"a 4-bit register cannot hold 31 — expected 15 after truncation, got {_r.q}"
_c = Reg(3, 7)
_c.drive(8)
_c.commit()
assert _c.q == 0, f"a 3-bit counter wraps to 0 after 7, got {_c.q}"
'''},
                    {"name": "the whole design commits on one edge, so two registers swap", "code": r'''
_t = swap_trace(1, 2, 4)
assert len(_t) == 4, f"expected one snapshot per cycle, got {len(_t)}"
assert _t == [(1, 2), (2, 1), (1, 2), (2, 1)], (
    f"got {_t} — if the values do not alternate, the second drive is reading a "
    "register that has already committed")
'''},
                    {"name": "the trace starts at the reset state", "code": r'''
_t = swap_trace(5, 6, 3)
assert _t[0] == (5, 6), (
    f"the first snapshot is taken before any edge, so it should be (5, 6), got {_t[0]}")
'''},
                    {"name": "a three-bit counter wraps at eight", "code": r'''
_c = counter_trace(3, 10)
assert _c == [0, 1, 2, 3, 4, 5, 6, 7, 0, 1], (
    f"got {_c} — a counter is a register plus one, and the width does the wrapping")
'''},
                    {"name": "a bit takes one cycle per stage to cross a shift register", "code": r'''
_s = shift_trace([1, 0, 0, 0], 3)
assert len(_s) == 7, f"len(bits) + depth cycles were asked for, got {len(_s)}"
assert _s == [0, 0, 0, 1, 0, 0, 0], (
    f"got {_s} — the 1 should appear at the tail in cycle 3, one cycle per stage. "
    "Appearing in cycle 1 means the stages are committing as they are driven")
'''},
                    {"name": "the order the stages are written in does not matter", "code": r'''
_regs = [Reg(1, 0) for _ in range(3)]
_bits = [1, 1, 0, 1, 0, 0]


def _forwards(c):
    _regs[0].drive(_bits[c] if c < len(_bits) else 0)
    for _i in range(1, 3):
        _regs[_i].drive(_regs[_i - 1].q)


_fwd = [s[-1] for s in run(_regs, _forwards, len(_bits) + 3)]
_bwd = shift_trace(_bits, 3)
assert _fwd == _bwd, (
    f"driving the chain head-first gave {_fwd} and tail-first gave {_bwd}. In a "
    "two-phase update the order cannot matter; if it does, q is being written early")
assert _fwd.count(1) == 3, f"three ones went in, so three should come out, got {_fwd}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Finite state machines",
            "summary": "A state register, a next-state function, an output function. The only real choice is where the output comes from.",
            "concepts": [
                "The canonical three-block form: a state register, a combinational next-state function, and a combinational output function.",
                "Moore outputs depend only on the state, so they are registered and stable — and one cycle late.",
                "Mealy outputs depend on the state *and* the current input, so they are earlier by one cycle and inherit every glitch on that input.",
                "State encoding is an implementation choice: binary uses `ceil(log2 S)` flops, one-hot uses `S` flops and a much cheaper next-state cloud.",
                "A state your machine cannot reach is either dead logic or a missing reset, and whether an upset that lands the machine in one can get out again depends entirely on the next-state logic you wrote for that encoding.",
            ],
            "sandbox": {
                "title": "A controller that holds instead of advancing",
                "visualiser": "pipeline",
                "minutes": 7,
                "initial": {"dep": 6, "fwd": 0, "miss": 0},
                "brief": r'''
Read each row as one instruction walking a five-state sequence: IF, ID, EX, ME, WB,
in that order, one state per cycle. A stall is not a sixth state. It is the same
controller holding: the state register reloads its own value, so the sequence pauses
where it stands and resumes unchanged.

Six dependent pairs are stalling to begin with.
''',
                "notice": [
                    "Every row walks the same five states in the same order, and the only thing that differs between rows is which column the sequence starts in. That is a hard sequence controller: no branching in the state graph at all.",
                    "Rows i1 to i6 each start three columns after the row above rather than one. The two extra columns are the hold — the same state, occupied for three cycles instead of one.",
                    "Rows i7 and i8 step by one again even though the slider is at its maximum. The model marks only the first six instructions after i0 as dependent, which is a property of the model and not of any program.",
                    "Switch forwarding on. The stalls disappear in a single step, because the only thing `fwd` changes in the model is the hold condition — same states, same order, different decision about when to advance.",
                ],
            },
            "derive": {
                "title": "What a multi-cycle controller costs and what it buys",
                "minutes": 13,
                "vars": ["W", "C", "f", "t_it", "t_reg", "T"],
                "brief": r'''
An iterative divider. The controller spends one cycle in LOAD capturing the
operands, then $W$ cycles in ITER, one cycle per bit of the $W$-bit quotient, then
one cycle in WRITEBACK — from which it goes straight back to LOAD when the next
operation is already waiting, so back-to-back divisions cost nothing between them.

Write $t_{it}$ for the combinational delay of one iteration's logic, and $t_{reg}$
for the clock-to-output plus setup overhead of the register between cycles.
''',
                "steps": [
                    {
                        "prompt": "Write the number of clock cycles $C$ one division takes.",
                        "answer": "W + 2",
                        "hint": "Count the states the controller passes through for one operation: LOAD, then the iterations, then WRITEBACK.",
                        "deconstruct": [
                            "One cycle in LOAD.",
                            "$W$ cycles in ITER.",
                            "One cycle in WRITEBACK.",
                        ],
                    },
                    {
                        "prompt": "At clock frequency $f$, write the throughput in divisions per second.",
                        "answer": "\\frac{f}{W + 2}",
                        "hint": "Divisions per second is cycles per second divided by cycles per division.",
                        "deconstruct": [
                            "The machine completes one operation every $C$ cycles.",
                            "It gets $f$ cycles each second.",
                        ],
                    },
                    {
                        "prompt": "The longest path in this machine is one iteration. Write the clock period the iterative design can run at.",
                        "answer": "t_{it} + t_{reg}",
                        "hint": "One iteration's logic sits between two registers, and the register overhead is charged once per cycle.",
                        "deconstruct": [
                            "The path is register, one iteration of logic, register.",
                            "That is $t_{it}$ of logic and $t_{reg}$ of overhead.",
                        ],
                    },
                    {
                        "prompt": "Now unroll it completely: one combinational block doing all $W$ iterations, finishing in a single cycle. Write that design's clock period.",
                        "answer": "W \\cdot t_{it} + t_{reg}",
                        "hint": "The same register overhead, but now $W$ iterations of logic are in series between the two registers.",
                        "deconstruct": [
                            "Unrolling removes the registers between iterations, not the logic.",
                            "So the combinational delay is $W$ times one iteration, and the overhead is still charged once.",
                        ],
                    },
                    {
                        "prompt": "Write the ratio of the iterative machine's throughput to the unrolled machine's throughput.",
                        "answer": "\\frac{W \\cdot t_{it} + t_{reg}}{\\left(W + 2\\right) \\cdot \\left(t_{it} + t_{reg}\\right)}",
                        "placeholder": "\\frac{W \\cdot t_{it} + t_{reg}}{\\left(W + 2\\right)\\left(t_{it} + t_{reg}\\right)}",
                        "hint": "Each machine's throughput is one over (cycles per operation times period). Take the ratio and the units cancel.",
                        "deconstruct": [
                            "Iterative: one operation every $\\left(W+2\\right)\\left(t_{it}+t_{reg}\\right)$ seconds.",
                            "Unrolled: one operation every $W t_{it} + t_{reg}$ seconds.",
                            "The ratio is the second divided by the first.",
                        ],
                    },
                ],
                "closing": r'''
That ratio is always below one: the multi-cycle machine is slower, and no encoding
trick changes it. What it buys is area — one iteration's worth of logic instead of
$W$ — and a period short enough to close timing at all. The unrolled divider that
cannot meet $t_{reg} + W t_{it}$ has a throughput of zero.
''',
            },
            "lab": {
                "title": "A sequence detector, twice",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Build a detector for the bit pattern `1101`, allowing overlaps, as a Moore machine
and again as a Mealy machine, and measure the difference.

**Moore.** Five states, numbered by how much of the pattern has been matched so far:
`0` for nothing, `1` for `1`, `2` for `11`, `3` for `110`, `4` for `1101`. The output
is `1` exactly when the state is `4`.

Write `moore_next(state, bit)` and `run_moore(bits)`. `run_moore` returns
`len(bits) + 1` outputs: entry `i` is the output *during* cycle `i`, decided by the
state the register held at the start of that cycle. The extra entry is the cycle
after the last bit, which is where the final match shows up.

**Mealy.** Four states, `0` to `3`, with the same meaning. There is no state `4`: the
output is `1` in the same cycle as the fourth bit, whenever the state is `3` and the
bit is `1`. Write `mealy_next(state, bit)`, `mealy_out(state, bit)` and
`run_mealy(bits)`, which returns exactly `len(bits)` outputs.

Get the overlap right in both. The rule is the same in each: after any bit, the state
is the length of the longest suffix of everything seen so far that is still a prefix
of `1101`. After a match, that suffix is `1`, not nothing — and in the Mealy machine,
which has no state for the completed match, that transition has to be folded into
`mealy_next(3, 1)`.

**Reachability.** Write `reachable(next_fn, n_states, start=0)`, which explores the
state graph from `start` over both input values and returns the sorted list of states
that can actually be entered. A state missing from that list is either dead logic or
a machine that can never be reset out of it.
''',
                "files": [{"name": "main.py", "content": r'''
def moore_next(state, bit):
    """Next state of the five-state Moore detector for 1101, with overlap."""
    b = 1 if bit else 0
    # TODO: return the next state for every (state, b) pair, states 0..4.
    return 0


def run_moore(bits):
    """One output per cycle, plus the cycle after the last bit."""
    state = 0
    out = []
    # TODO: record the output for the current state, then advance the state.
    # After the loop, record the output one more time.
    return out


def mealy_next(state, bit):
    """Next state of the four-state Mealy detector for 1101, with overlap."""
    b = 1 if bit else 0
    # TODO: states 0..3 only.
    return 0


def mealy_out(state, bit):
    """The Mealy output: a function of the state *and* the input bit."""
    # TODO
    return 0


def run_mealy(bits):
    """Exactly one output per cycle."""
    state = 0
    out = []
    # TODO
    return out


def reachable(next_fn, n_states, start=0):
    """Sorted list of the states reachable from `start` over inputs 0 and 1."""
    # TODO: explore the graph. n_states is the number the encoding allows for.
    return []


if __name__ == "__main__":
    stream = [1, 1, 0, 1, 1, 0, 1]
    print("moore:", run_moore(stream))
    print("mealy:", run_mealy(stream))
    print("reachable:", reachable(moore_next, 5))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
MOORE = {
    (0, 0): 0, (0, 1): 1,
    (1, 0): 0, (1, 1): 2,
    (2, 0): 3, (2, 1): 2,
    (3, 0): 0, (3, 1): 4,
    (4, 0): 0, (4, 1): 2,
}

MEALY = {
    (0, 0): 0, (0, 1): 1,
    (1, 0): 0, (1, 1): 2,
    (2, 0): 3, (2, 1): 2,
    (3, 0): 0, (3, 1): 1,
}


def moore_next(state, bit):
    """Next state of the five-state Moore detector for 1101, with overlap."""
    b = 1 if bit else 0
    return MOORE[(state, b)]


def run_moore(bits):
    """One output per cycle, plus the cycle after the last bit."""
    state = 0
    out = []
    for bit in bits:
        out.append(1 if state == 4 else 0)
        state = moore_next(state, bit)
    out.append(1 if state == 4 else 0)
    return out


def mealy_next(state, bit):
    """Next state of the four-state Mealy detector for 1101, with overlap."""
    b = 1 if bit else 0
    return MEALY[(state, b)]


def mealy_out(state, bit):
    """The Mealy output: a function of the state *and* the input bit."""
    return 1 if (state == 3 and bit) else 0


def run_mealy(bits):
    """Exactly one output per cycle."""
    state = 0
    out = []
    for bit in bits:
        out.append(mealy_out(state, bit))
        state = mealy_next(state, bit)
    return out


def reachable(next_fn, n_states, start=0):
    """Sorted list of the states reachable from `start` over inputs 0 and 1."""
    seen = {start}
    frontier = [start]
    while frontier:
        s = frontier.pop()
        for b in (0, 1):
            t = next_fn(s, b)
            if t not in seen:
                seen.add(t)
                frontier.append(t)
    return sorted(seen)


if __name__ == "__main__":
    stream = [1, 1, 0, 1, 1, 0, 1]
    print("moore:", run_moore(stream))
    print("mealy:", run_mealy(stream))
    print("reachable:", reachable(moore_next, 5))
'''}],
                "hints": [
                    "The overlap rule is the whole exercise: from state 4 a `1` goes to state 2, not to state 1 and not back to 0. Ask what the longest suffix of what you have seen is that is still a prefix of `1101`.",
                    "From state 2 (`11`) a further `1` stays in state 2 — a run of ones never loses you the `11` you already have.",
                    "The Mealy machine has one state fewer, so the exit from the match lives in `mealy_next(3, 1)`. Ask what has been seen at that point (`1101`) and what the longest suffix of it is that is also a prefix of `1101`; the answer is one bit long. Getting this wrong reports a match on `...110101` that is not there.",
                    "`reachable` is a graph search, not a simulation: push the start state, pop, follow both edges, and stop when nothing new appears. `n_states` is only there so you can see which numbers never came up.",
                ],
                "tests": [
                    {"name": "the Moore machine handles an overlap", "code": r'''
assert moore_next(4, 1) == 2, (
    f"after 1101, another 1 leaves you holding 11 — expected state 2, got {moore_next(4, 1)}")
assert moore_next(4, 0) == 0, (
    f"after 1101, a 0 gives you 10, which is no prefix of 1101 — expected 0, got {moore_next(4, 0)}")
assert moore_next(2, 1) == 2, (
    f"a run of ones keeps you at 11 — expected 2, got {moore_next(2, 1)}")
assert moore_next(3, 1) == 4, "1101 completes from state 3 on a 1"
'''},
                    {"name": "the Moore detector fires one cycle after the pattern", "code": r'''
_m = run_moore([1, 1, 0, 1])
assert len(_m) == 5, f"len(bits) + 1 outputs were asked for, got {len(_m)}"
assert _m == [0, 0, 0, 0, 1], (
    f"got {_m} — the output is registered, so it appears in the cycle after the "
    "last bit of the pattern, not during it")
'''},
                    {"name": "overlapping matches are both found", "code": r'''
_m = run_moore([1, 1, 0, 1, 1, 0, 1])
assert _m == [0, 0, 0, 0, 1, 0, 0, 1], (
    f"got {_m} — 1101101 contains two overlapping matches, so there should be "
    "two ones, at indices 4 and 7")
'''},
                    {"name": "the Mealy detector fires during the last bit", "code": r'''
_y = run_mealy([1, 1, 0, 1, 1, 0, 1])
assert len(_y) == 7, f"exactly one output per cycle was asked for, got {len(_y)}"
assert _y == [0, 0, 0, 1, 0, 0, 1], (
    f"got {_y} — a Mealy output is combinational in the input, so it is asserted "
    "in the same cycle as the fourth bit")
'''},
                    {"name": "Moore is exactly one cycle behind Mealy", "code": r'''
_bits = [1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1]
_m = run_moore(_bits)
_y = run_mealy(_bits)
assert _m[1:] == _y, (
    f"moore[1:] = {_m[1:]} but mealy = {_y}. The two machines detect the same "
    "thing; the registered output simply arrives a cycle later")
assert sum(_y) == 4, (
    f"this stream contains four occurrences of 1101, at indices 0, 3, 7 and 12, "
    f"so four outputs should fire — got {sum(_y)}")
'''},
                    {"name": "every state of the detector is reachable", "code": r'''
_r = reachable(moore_next, 5)
assert _r == [0, 1, 2, 3, 4], (
    f"got {_r} — all five states of a correct 1101 detector can be entered from reset")
'''},
                    {"name": "reachability finds states that no input can enter", "code": r'''
def _broken(s, b):
    return (s + 1) % 4 if b else 0


_r = reachable(_broken, 6)
assert _r == [0, 1, 2, 3], (
    f"got {_r} — this machine is encoded for six states but can only ever occupy "
    "four; states 4 and 5 are decode and flops that no input sequence can use")
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Ready, valid and back-pressure",
            "summary": "Two wires and one rule make a composable interface. The rule is what makes it composable.",
            "concepts": [
                "A transfer happens on an edge where `valid` and `ready` are both high. Neither side waits for the other to go first.",
                "The stability rule: once `valid` is asserted it may not be withdrawn, and the data may not change, until the transfer is taken.",
                "`ready` must not depend combinationally on `valid`, or two connected blocks form a loop and neither has a defined value.",
                "A one-entry slice whose `ready` is registered can only accept every other cycle. Two entries — a skid buffer — sustain a transfer every cycle.",
                "Throughput is set by whichever side stalls more; the buffer between them only decides whether the two stalls collide.",
            ],
            "sandbox": {
                "title": "Bubbles are the absence of a path",
                "visualiser": "pipeline",
                "minutes": 8,
                "initial": {"dep": 4, "fwd": 0, "miss": 0},
                "brief": r'''
A bubble in a pipeline is a cycle in which a stage had nothing to hand on, either
because it was not ready or because what it needed had not arrived. Here the cause
is a dependency, but the shape on screen is the shape of any back-pressure: the row
below waits, and everything behind it waits with it.

Four dependent pairs, no forwarding.
''',
                "notice": [
                    "Four dependent pairs and no forwarding gives 21 cycles for nine instructions, CPI 2.33. The eight lost cycles are all in the gaps between rows i0 and i4.",
                    "Switch forwarding on: 13 cycles, CPI 1.44. The bubbles were never work — they were the absence of a path — and adding the path removes them entirely rather than making them faster.",
                    "With forwarding off, add one mispredict. Row i3 now starts five columns after i2 instead of three, because it pays the dependency stall and the flush in the same slot. A stall and a flush cost the same two cycles here but they are not the same event: one resumes, the other discards.",
                    "Sweep dependent pairs from 0 to 6 with forwarding off and watch the reading: exactly two cycles per step, a straight line. Back-pressure that is proportional to the number of stalled beats is the well-behaved case; the interesting bugs are the ones that are not.",
                ],
            },
            "derive": {
                "title": "Pipeline speedup, and the ceiling it runs into",
                "minutes": 13,
                "vars": ["n", "k", "S", "p", "b", "CPI"],
                "brief": r'''
A $k$-stage pipeline processing $n$ items, one entering per cycle, nothing stalling.
Compare it against a machine that does the same work but takes $k$ cycles per item
because it has no pipeline at all.
''',
                "steps": [
                    {
                        "prompt": "Write the number of cycles the pipeline needs to retire all $n$ items.",
                        "answer": "n + k - 1",
                        "hint": "The first item takes $k$ cycles to come out. After that, one comes out every cycle.",
                        "deconstruct": [
                            "Item 1 emerges at cycle $k$.",
                            "Each of the remaining $n-1$ items emerges one cycle after the last.",
                            "Total: $k + (n-1)$.",
                        ],
                    },
                    {
                        "prompt": "Write the speedup $S$ over the unpipelined machine, which needs $nk$ cycles.",
                        "answer": "\\frac{n \\cdot k}{n + k - 1}",
                        "hint": "Speedup is old cycles over new cycles.",
                        "deconstruct": [
                            "Unpipelined: $nk$ cycles.",
                            "Pipelined: $n + k - 1$ cycles.",
                            "Divide.",
                        ],
                    },
                    {
                        "prompt": "Let $n$ grow without bound. Write the limit of $S$.",
                        "answer": "k",
                        "hint": "Divide numerator and denominator by $n$ and see what survives.",
                        "deconstruct": [
                            "$S = k / \\left(1 + (k-1)/n\\right)$.",
                            "As $n \\to \\infty$ the second term in the denominator vanishes.",
                            "The number of stages is the ceiling, and it is never reached.",
                        ],
                    },
                    {
                        "prompt": "Now let a fraction $p$ of the items stall for $b$ cycles each. Write the total cycles.",
                        "answer": "n + k - 1 + n \\cdot p \\cdot b",
                        "hint": "$np$ items each cost $b$ extra cycles, on top of the ideal schedule.",
                        "deconstruct": [
                            "The ideal schedule is $n + k - 1$.",
                            "Of the $n$ items, $np$ of them stall.",
                            "Each stall adds $b$ cycles.",
                        ],
                    },
                    {
                        "prompt": "For large $n$ the fill term stops mattering. Write the cycles per item, $CPI$.",
                        "answer": "1 + p \\cdot b",
                        "hint": "Divide the previous answer by $n$ and drop the $\\left(k-1\\right)/n$ term.",
                        "deconstruct": [
                            "Cycles per item is $\\left(n + k - 1 + npb\\right)/n$.",
                            "That is $1 + (k-1)/n + pb$.",
                            "The middle term goes to zero.",
                        ],
                    },
                ],
                "closing": r'''
Both results are the same statement. Depth buys you a ceiling of $k$; stalls take a
fixed toll of $pb$ off every item, and once $pb$ is comparable to one, adding stages
buys nothing at all. This is why an elastic interface is worth its two registers:
it converts a stall that propagates into a stall that is absorbed.
''',
            },
            "lab": {
                "title": "A slice that does not drop data",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
Model one ready/valid buffer and the link it sits in.

`step_slice(q, in_valid, in_data, out_ready, depth=2)` is one clock cycle. `q` is the
registered queue, oldest item first. Return `(next_q, in_ready, out_valid, out_data)`
under exactly these rules:

- `in_ready` is 1 when `len(q) < depth`, decided from the registered queue alone.
  It must not consult `out_ready` — that would be a combinational path from the sink
  back to the source, and two such blocks connected together form a loop.
- `out_valid` is 1 when `q` is non-empty, and `out_data` is then `q[0]`, otherwise
  `None`.
- A transfer out happens when `out_valid` and `out_ready` are both true: drop the
  head.
- A transfer in happens when `in_valid` and `in_ready` are both true: append
  `in_data`.
- Return a new list; do not mutate `q`.

`run_link(data, src_pattern, sink_pattern, depth=2)` drives it. In cycle `c` the
source offers the next unsent item if `src_pattern[c % len(src_pattern)]` is 1, and
the sink is ready if `sink_pattern[c % len(sink_pattern)]` is 1. An empty pattern
means "always". Stop the cycle after everything has been sent and the queue has
drained, and return `(received, cycles)`.

`handshake_legal(record)` takes a list of `(valid, ready, data)` per cycle and
returns `True` only if the source obeyed the stability rule: whenever `valid` was
asserted and `ready` was not, the next cycle must still have `valid` asserted with
the *same* data.
''',
                "files": [{"name": "main.py", "content": r'''
def step_slice(q, in_valid, in_data, out_ready, depth=2):
    """One cycle of a ready/valid buffer. Return (next_q, in_ready, out_valid, out_data)."""
    # TODO: decide in_ready and out_valid from q alone, then apply the transfers.
    return list(q), 0, 0, None


def run_link(data, src_pattern, sink_pattern, depth=2):
    """Drive step_slice from the two patterns. Return (received, cycles)."""
    q = []
    sent = 0
    got = []
    cycle = 0
    limit = 40 * (len(data) + 4)
    while cycle < limit:
        offer = 1 if sent < len(data) else 0
        if src_pattern:
            offer = offer and src_pattern[cycle % len(src_pattern)]
        item = data[sent] if sent < len(data) else None
        rdy = sink_pattern[cycle % len(sink_pattern)] if sink_pattern else 1
        # TODO: step the slice, count an accepted item, collect a delivered one,
        # advance the queue and the cycle, and stop once everything has drained.
        break
    return got, cycle


def handshake_legal(record):
    """True when the source never withdrew valid, or changed data, before a transfer."""
    # TODO: look at each cycle and the one after it.
    return False


if __name__ == "__main__":
    payload = list(range(6))
    print("two entries:", run_link(payload, [1], [1], 2))
    print("one entry:  ", run_link(payload, [1], [1], 1))
    print("stalling sink:", run_link(payload, [1], [1, 0, 0], 2))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def step_slice(q, in_valid, in_data, out_ready, depth=2):
    """One cycle of a ready/valid buffer. Return (next_q, in_ready, out_valid, out_data)."""
    in_ready = 1 if len(q) < depth else 0
    out_valid = 1 if len(q) > 0 else 0
    out_data = q[0] if q else None
    nxt = list(q)
    if out_valid and out_ready:
        nxt.pop(0)
    if in_valid and in_ready:
        nxt.append(in_data)
    return nxt, in_ready, out_valid, out_data


def run_link(data, src_pattern, sink_pattern, depth=2):
    """Drive step_slice from the two patterns. Return (received, cycles)."""
    q = []
    sent = 0
    got = []
    cycle = 0
    limit = 40 * (len(data) + 4)
    while cycle < limit:
        offer = 1 if sent < len(data) else 0
        if src_pattern:
            offer = offer and src_pattern[cycle % len(src_pattern)]
        item = data[sent] if sent < len(data) else None
        rdy = sink_pattern[cycle % len(sink_pattern)] if sink_pattern else 1
        q, in_ready, out_valid, out_data = step_slice(q, offer, item, rdy, depth)
        if offer and in_ready:
            sent += 1
        if out_valid and rdy:
            got.append(out_data)
        cycle += 1
        if sent == len(data) and not q:
            break
    return got, cycle


def handshake_legal(record):
    """True when the source never withdrew valid, or changed data, before a transfer."""
    for c in range(len(record) - 1):
        valid, ready, data = record[c]
        if valid and not ready:
            nxt_valid, _, nxt_data = record[c + 1]
            if not nxt_valid or nxt_data != data:
                return False
    return True


if __name__ == "__main__":
    payload = list(range(6))
    print("two entries:", run_link(payload, [1], [1], 2))
    print("one entry:  ", run_link(payload, [1], [1], 1))
    print("stalling sink:", run_link(payload, [1], [1, 0, 0], 2))
'''}],
                "hints": [
                    "Compute `in_ready`, `out_valid` and `out_data` from `q` *before* you change anything. They are registered outputs; the transfers are what happens at the edge.",
                    "The removal and the append commute — the head leaves the front, the new item joins the back — so the order you write them in is not what to worry about. What breaks the block is deciding `in_ready` from the queue *after* the removal: on a `depth=1` slice that makes `in_ready` a function of `out_ready`, and the slice starts passing data through combinationally at one item per cycle instead of one per two.",
                    "In `run_link`, `offer and in_ready` is the acceptance and `out_valid and rdy` is the delivery. The loop ends when everything has been sent *and* the queue is empty — the last item still needs a cycle to leave.",
                ],
                "tests": [
                    {"name": "a slice accepts while it has room and refuses when full", "code": r'''
_nxt, _in_ready, _out_valid, _out_data = step_slice([], 0, None, 0, 2)
assert _in_ready, "an empty two-entry slice has room, so in_ready must be asserted"
assert not _out_valid, "an empty slice has nothing to offer downstream"
_nxt, _in_ready, _out_valid, _out_data = step_slice(["a", "b"], 1, "c", 0, 2)
assert not _in_ready, "a full slice must refuse, or the item it cannot store is lost"
assert _out_valid and _out_data == "a", (
    f"a non-empty slice offers its oldest item: expected 'a', got {_out_data!r}")
assert _nxt == ["a", "b"], f"nothing transferred this cycle, so the queue is unchanged, got {_nxt}"
'''},
                    {"name": "ready is decided without looking at the sink", "code": r'''
_a = step_slice(["x"], 1, "y", 0, 2)[1]
_b = step_slice(["x"], 1, "y", 1, 2)[1]
assert _a == _b, (
    f"in_ready came out {_a} with the sink stalled and {_b} with it ready. A "
    "combinational path from out_ready to in_ready makes two connected slices a loop")
assert _a, "the slice has one of two entries used, so it must be ready"
'''},
                    {"name": "the head leaves and the new item arrives in the same cycle", "code": r'''
_nxt, _in_ready, _out_valid, _out_data = step_slice(["a"], 1, "b", 1, 2)
assert _out_data == "a", f"the oldest item leaves first, got {_out_data!r}"
assert _nxt == ["b"], (
    f"got {_nxt} — with a transfer in and a transfer out in one cycle the queue "
    "should end up holding just the new item")
'''},
                    {"name": "nothing is lost or reordered when the sink stalls", "code": r'''
_data = list(range(12))
_got, _cycles = run_link(_data, [1], [1, 0, 0], 2)
assert _got == _data, (
    f"got {_got} — every item must come out exactly once and in order, however "
    "often the sink stalls")
assert _cycles == 37, (
    f"got {_cycles} — the sink accepts one beat in three, so the twelfth item leaves "
    "on cycle 36 and the loop stops on 37. The depth of the buffer does not change "
    "that: throughput is set by whichever side stalls more")
'''},
                    {"name": "two entries sustain one transfer per cycle", "code": r'''
_data = list(range(6))
_got, _cycles = run_link(_data, [1], [1], 2)
assert _got == _data, f"expected {_data}, got {_got}"
assert _cycles == 7, (
    f"got {_cycles} cycles for six items. A two-entry slice accepts and delivers "
    "in the same cycle, so it should take one cycle of latency plus one per item")
'''},
                    {"name": "one entry can only accept every other cycle", "code": r'''
_data = list(range(6))
_got, _cycles = run_link(_data, [1], [1], 1)
assert _got == _data, f"a one-entry slice must still deliver everything, got {_got}"
assert _cycles == 12, (
    f"got {_cycles} — with a single registered entry, the cycle that empties the "
    "slice is a cycle in which it was not ready, so the rate is one item per two cycles")
'''},
                    {"name": "the stability rule is enforced in both directions", "code": r'''
assert handshake_legal([(1, 0, 7), (1, 1, 7), (0, 1, None)]), (
    "this source held valid and its data until the transfer was taken — that is legal")
assert not handshake_legal([(1, 0, 7), (0, 0, None)]), (
    "valid was withdrawn before the sink accepted; a sink is allowed to be slow, "
    "and this source would have lost the beat")
assert not handshake_legal([(1, 0, 7), (1, 1, 8)]), (
    "the data changed under a stalled sink, so the sink accepts a value that was "
    "never offered for a full cycle")
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Self-checking benches",
            "summary": "A test that prints waveforms is a test nobody runs. A test that compares against a model you wrote separately is a test that fails when it should.",
            "concepts": [
                "The reference model is written from the specification, not from the design. If it is derived from the RTL it will agree with the RTL's bugs.",
                "A scoreboard compares two streams cycle by cycle and reports the first divergence — the only interesting one.",
                "Directed stimulus reaches the corners you already thought of; randomised stimulus reaches the ones you did not.",
                "Seed everything. A failure you cannot reproduce is a rumour.",
                "Coverage is the question 'did the stimulus ever get the design into that state', and it is a different question from 'did it pass'.",
            ],
            "sandbox": {
                "title": "Where a model stops responding to its inputs",
                "visualiser": "pipeline",
                "minutes": 7,
                "initial": {"dep": 2, "fwd": 0, "miss": 2},
                "brief": r'''
Treat this sandbox as a design under test with three inputs, and go looking for the
ranges over which it does not respond to them. Every one you find is a range in
which a randomised test would be burning cycles and proving nothing.
''',
                "notice": [
                    "Take mispredicts from 2 to 3 to 4. Neither the drawing nor the cycle count moves. The model can only flush at rows i3 and i6, so two is the most it will ever apply — and the top half of that slider's range is dead stimulus.",
                    "Switch forwarding on and sweep dependent pairs across its whole range. The count never changes. One input has made another irrelevant, and a random test that varies only `dep` while holding `fwd` at 1 would report a full pass having exercised nothing.",
                    "Switch forwarding back off and sweep dependent pairs again: the cycle count rises by exactly two per step. A model you can predict in closed form is a model you can write a scoreboard against, and that closed form is the reference this course keeps asking you to write.",
                    "Set dependent pairs to 6 and note that rows i7 and i8 never stall no matter what. The model marks only the first six instructions after i0; a bench that only ever measured the tail of the schedule would see a perfect pipeline and report success.",
                ],
            },
            "derive": {
                "title": "How long a random test takes to find one corner",
                "minutes": 12,
                "vars": ["p", "n", "W", "E"],
                "brief": r'''
A block takes two $W$-bit operands. Somewhere in the input space there is one
particular pair $(a, b)$ that breaks it. The bench draws operands uniformly at
random, independently each cycle.
''',
                "steps": [
                    {
                        "prompt": "Write the probability $p$ that one random vector is that exact pair.",
                        "answer": "\\frac{1}{2^{2 \\cdot W}}",
                        "hint": "Each operand has $2^W$ possible values, and the two are drawn independently.",
                        "deconstruct": [
                            "There are $2^W \\cdot 2^W$ equally likely pairs.",
                            "Exactly one of them is the bad one.",
                        ],
                    },
                    {
                        "prompt": "Write the probability that one random vector misses it.",
                        "answer": "1 - p",
                        "hint": "The vector either hits or it does not.",
                        "deconstruct": [
                            "The two outcomes are exhaustive and mutually exclusive.",
                        ],
                    },
                    {
                        "prompt": "The vectors are independent. Write the probability that $n$ of them all miss.",
                        "answer": "\\left(1 - p\\right)^{n}",
                        "hint": "Independent events multiply.",
                        "deconstruct": [
                            "Each vector misses with probability $1 - p$.",
                            "All $n$ missing is that, $n$ times over.",
                        ],
                    },
                    {
                        "prompt": "Write the expected number of vectors drawn until the first hit.",
                        "answer": "\\frac{1}{p}",
                        "hint": "This is the mean of a geometric distribution — the answer is as simple as it looks.",
                        "deconstruct": [
                            "Each draw is an independent trial with success probability $p$.",
                            "The expected number of trials to the first success is $1/p$.",
                        ],
                    },
                ],
                "closing": r'''
Put numbers in. At $W = 8$ that is 65,536 vectors on average — a second of
simulation. At $W = 32$ it is $1.8 \times 10^{19}$, which is never. Randomisation
does not search a space; it samples one. The corner you can name is the corner you
write a directed test for, and the random stimulus is there for the ones you cannot
name — which, in a sequential design, are mostly not single vectors at all but
sequences.
''',
            },
            "lab": {
                "title": "Find the bug in someone else's FIFO",
                "runtime": "python",
                "minutes": 38,
                "brief": r'''
`dut.py` is a synchronous FIFO written by another team, along with the specification
it was meant to implement. It does not implement it. Your job is the bench, not the
fix.

Write, in `main.py`:

- `RefFifo` — the specification as a model, with the same `step(push, data, pop)`
  interface returning `(popped, full, empty)`. Write it from the docstring in
  `dut.py`, not from the code below it. The one clause that matters: `full` and
  `empty` describe the queue at the *start* of the cycle, and a push is accepted
  whenever there is room once that cycle's pop has been accounted for.
- `trace(fifo, ops)` — run a list of `(push, data, pop)` triples through a model and
  return the list of `(popped, full, empty)` results, one per cycle.
- `compare(a, b)` — the index of the first differing cycle in two traces, or `None`
  when they agree for their whole common length and are the same length.
- `first_mismatch(depth, ops)` — build a `RefFifo(depth)` and a `Fifo(depth)`, run
  both on the same ops, and return `compare` of the two traces.
- `directed_ops(depth)` — a directed sequence you have reasoned your way to: fill the
  FIFO, then push and pop in the same cycle while it is full, then drain it. Return
  the op list.
- `random_ops(seed, cycles)` — `cycles` triples from `np.random.default_rng(seed)`,
  drawing in this exact order per cycle so the checks can reproduce them:
  `push = int(rng.integers(0, 2))`, then `data = int(rng.integers(0, 256))`, then
  `pop = int(rng.integers(0, 2))`.
- `find_bug(depth, cycles, seeds)` — try each seed in turn; return the first
  `(seed, index)` whose random stimulus mismatches, or `None`.

The bug is only visible when the FIFO is full, which is why a stream of pushes and
pops that keeps it half empty will never find it.
''',
                "files": [
                    {"name": "dut.py", "ro": True, "content": r'''
"""A synchronous FIFO handed over by the design team. Read it; do not edit it.

`Fifo(depth).step(push, data, pop)` is one clock cycle of the block.

  * `full` and `empty` describe the queue as it stood at the *start* of the cycle
  * a pop returns the head of the queue whenever the queue is not empty, and
    frees that slot in the same cycle
  * a push is accepted whenever there is room once that pop has been accounted
    for, so a push and a pop arriving together at a full FIFO must both succeed

`step` returns `(popped, full, empty)`, with `popped` None when nothing came out.
"""


class Fifo:
    def __init__(self, depth):
        self.depth = int(depth)
        self.q = []

    def step(self, push, data, pop):
        full = len(self.q) >= self.depth
        empty = len(self.q) == 0
        popped = None
        if pop and self.q:
            popped = self.q.pop(0)
        if push and not full:
            self.q.append(data)
        return popped, full, empty
'''},
                    {"name": "main.py", "content": r'''
import numpy as np
from dut import Fifo


class RefFifo:
    """The specification, written out as a model."""

    def __init__(self, depth):
        self.depth = int(depth)
        self.q = []

    def step(self, push, data, pop):
        # TODO: read full and empty from the queue as it stands now, then apply
        # the pop, then decide whether the push fits.
        return None, False, False


def trace(fifo, ops):
    """Run (push, data, pop) triples through a model, one cycle each."""
    # TODO
    return []


def compare(a, b):
    """Index of the first cycle where two traces differ, or None."""
    # TODO
    return None


def first_mismatch(depth, ops):
    """Run the reference and the DUT on the same ops and compare them."""
    # TODO
    return None


def directed_ops(depth):
    """Fill the FIFO, push and pop together while full, then drain."""
    # TODO
    return []


def random_ops(seed, cycles):
    """Seeded random stimulus: push, then data, then pop, every cycle."""
    rng = np.random.default_rng(seed)
    ops = []
    # TODO: draw in the documented order so the checks can reproduce this.
    return ops


def find_bug(depth, cycles, seeds):
    """First (seed, cycle index) whose random stimulus exposes a mismatch."""
    # TODO
    return None


if __name__ == "__main__":
    print("directed:", first_mismatch(4, directed_ops(4)))
    print("random:  ", find_bug(4, 200, range(8)))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np
from dut import Fifo


class RefFifo:
    """The specification, written out as a model."""

    def __init__(self, depth):
        self.depth = int(depth)
        self.q = []

    def step(self, push, data, pop):
        full = len(self.q) >= self.depth
        empty = len(self.q) == 0
        popped = None
        if pop and self.q:
            popped = self.q.pop(0)
        if push and len(self.q) < self.depth:
            self.q.append(data)
        return popped, full, empty


def trace(fifo, ops):
    """Run (push, data, pop) triples through a model, one cycle each."""
    out = []
    for push, data, pop in ops:
        out.append(tuple(fifo.step(push, data, pop)))
    return out


def compare(a, b):
    """Index of the first cycle where two traces differ, or None."""
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            return i
    if len(a) != len(b):
        return min(len(a), len(b))
    return None


def first_mismatch(depth, ops):
    """Run the reference and the DUT on the same ops and compare them."""
    return compare(trace(RefFifo(depth), ops), trace(Fifo(depth), ops))


def directed_ops(depth):
    """Fill the FIFO, push and pop together while full, then drain."""
    ops = [(1, 10 + i, 0) for i in range(depth)]
    ops.append((1, 99, 1))
    ops.extend((0, 0, 1) for _ in range(depth + 1))
    return ops


def random_ops(seed, cycles):
    """Seeded random stimulus: push, then data, then pop, every cycle."""
    rng = np.random.default_rng(seed)
    ops = []
    for _ in range(cycles):
        push = int(rng.integers(0, 2))
        data = int(rng.integers(0, 256))
        pop = int(rng.integers(0, 2))
        ops.append((push, data, pop))
    return ops


def find_bug(depth, cycles, seeds):
    """First (seed, cycle index) whose random stimulus exposes a mismatch."""
    for s in seeds:
        idx = first_mismatch(depth, random_ops(s, cycles))
        if idx is not None:
            return (s, idx)
    return None


if __name__ == "__main__":
    print("directed:", first_mismatch(4, directed_ops(4)))
    print("random:  ", find_bug(4, 200, range(8)))
'''}],
                "hints": [
                    "Write `RefFifo.step` in the order the specification states it: sample `full` and `empty`, apply the pop, then test for room. The DUT tests for room before the pop, which is the whole difference.",
                    "`compare` returning `None` must mean 'the same', so two traces of different lengths are a mismatch at the point where the shorter one ran out.",
                    "For the directed sequence, `depth` pushes fill it and the cycle after that is the interesting one. A trace carries `full` and `empty` as well as the popped value, so the disagreement surfaces on the occupancy flag the cycle after the collision — the dropped item itself only goes missing at the end of the drain, which is why the sequence still has to drain.",
                ],
                "tests": [
                    {"name": "the reference agrees with the DUT while the FIFO never fills", "code": r'''
_calm = [(1, i, 1) for i in range(12)]
_t = trace(RefFifo(8), _calm)
assert len(_t) == len(_calm), f"one result per cycle was asked for, got {len(_t)}"
assert sum(1 for r in _t if r[0] is not None) == 11, (
    f"eleven of those twelve cycles should pop something, got "
    f"{sum(1 for r in _t if r[0] is not None)} — the first cycle has nothing to pop yet")
assert first_mismatch(8, _calm) is None, (
    "a stream that keeps the FIFO nearly empty exercises nothing the two models "
    "disagree about, so this must not report a mismatch")
'''},
                    {"name": "the reference implements the concurrent push and pop", "code": r'''
_ops = [(1, 10, 0), (1, 11, 0), (1, 99, 1), (0, 0, 1), (0, 0, 1)]
_t = trace(RefFifo(2), _ops)
assert [r[0] for r in _t] == [None, None, 10, 11, 99], (
    f"popped sequence was {[r[0] for r in _t]} — a push arriving with a pop at a "
    "full FIFO takes the slot the pop just freed, so 99 must come out at the end")
assert _t[3][1] is True or _t[3][1] == 1, (
    "after the concurrent cycle the queue holds 11 and 99, so it is still full")
'''},
                    {"name": "the directed sequence exposes the mismatch", "code": r'''
_ops = directed_ops(4)
assert len(_ops) >= 6, f"the sequence must fill, collide and drain — got {len(_ops)} cycles"
_i = first_mismatch(4, _ops)
assert _i is not None, (
    "the directed sequence did not reach the disagreement — it has to fill the "
    "FIFO completely and then push and pop in the same cycle")
assert _i == 5, f"the two models first differ at cycle 5, got {_i}"
'''},
                    {"name": "random stimulus is reproducible", "code": r'''
_a = random_ops(3, 40)
_b = random_ops(3, 40)
_c = random_ops(4, 40)
assert len(_a) == 40, f"forty cycles were asked for, got {len(_a)}"
assert _a == _b, "the same seed must give the same stimulus, or a failure cannot be replayed"
assert _a != _c, "a different seed must give different stimulus, or the sweep is one test"
assert all(0 <= d < 256 for _, d, _ in _a), "data is drawn as an 8-bit value"
'''},
                    {"name": "random stimulus finds it too, and says where", "code": r'''
_hit = find_bug(4, 200, range(8))
assert _hit is not None, (
    "two hundred random cycles on a depth-4 FIFO reach the full state many times; "
    "if nothing was found, the reference is agreeing with the DUT rather than the spec")
assert _hit == (0, 92), (
    f"got {_hit} — with this generator seed 0 is the first to fail, at cycle 92")
'''},
                    {"name": "the checker does not cry wolf", "code": r'''
_ops = random_ops(5, 60)
_x = trace(RefFifo(4), _ops)
_y = trace(RefFifo(4), _ops)
assert len(_x) == 60, f"one result per cycle, got {len(_x)}"
assert any(r[0] is not None for r in _x), (
    "this stimulus pops plenty of data; a trace of nothing but None means the "
    "model never accepted a push")
assert compare(_x, _y) is None, "a model compared with itself must never mismatch"
assert compare(_x, _y[:-1]) == 59, (
    "a trace that stops early is a mismatch at the cycle where it ran out, not a pass")
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "An elastic datapath and the bench that proves it",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
Build a two-stage pipelined multiply-accumulate with ready/valid on both ends, and
the self-checking bench that proves it right under arbitrary back-pressure.

The function is $y = ab + a + b$ on 8-bit operands, taken modulo $2^{16}$, split
across two stages:

- **stage 1** computes $p = ab$ and carries $a$ and $b$ forward with it
- **stage 2** computes $y = p + a + b$

Each stage holds at most **two** items, and every handshake decision is taken from
the registered state:

- `in_ready` is 1 when stage 1 holds fewer than two items
- an item moves from stage 1 to stage 2 when stage 1 is non-empty and stage 2 holds
  fewer than two items
- `out_valid` is 1 when stage 2 is non-empty, and `out_item` is then its oldest entry
- a transfer out happens when `out_valid` and `out_ready` are both true

Apply the transfers in the order out, then move, then in, so that a slot freed this
cycle is available this cycle.

## The pieces

1. The register kernel from module 1: `Reg` with `drive`/`commit`, and `tick`.
2. `Pipeline.step(in_valid, in_item, out_ready)` returning
   `(in_ready, out_valid, out_item)`.
3. `run(items, valid_pat, ready_pat)` — drive the source from `valid_pat` and the
   sink from `ready_pat` exactly as `run_link` did in module 3, record the output
   interface as `(out_valid, out_ready, out_item)` per cycle, stop once everything
   has been sent and both stages are empty, and return
   `(received, cycles, violations)` where `violations` is `monitor(record)`.
4. `monitor(record)` — the protocol checker: the index of every cycle at which
   `valid` was high, `ready` was low, and the following cycle either dropped `valid`
   or changed the data.
5. `min_period(stage_delays, t_cq, t_setup, t_skew)` and `max_frequency(...)` — the
   budget from module 1, over a list of per-stage combinational delays.

`stimulus.py` generates the patterns and payloads; it is read-only and the checks
generate exactly the same ones.

## Suggested order

Get `Pipeline.step` right against `run(items, None, None)` first — with no stalls
anywhere, twelve items should take fourteen cycles. Only then bring in the patterns.
If items come out correct with no stalls but wrong with them, the fault is almost
always a handshake decision that looked at the other side's wire.
''',
        "deliverables": [
            "A two-phase register kernel (`Reg`, `tick`) in which every register commits on the same edge, carried over from module 1.",
            "`Pipeline.step` implementing both stages and all three handshakes, with every decision taken from the registered state.",
            "`run` driving the design from `stimulus.py`, collecting the delivered stream and the cycle count, and returning the protocol violations it recorded.",
            "`monitor`, a protocol checker over the output interface that reports the cycle index of every stability violation.",
            "`min_period` and `max_frequency`, plus a comment at the top of `main.py` naming the stage that sets the period and what splitting it would buy.",
        ],
        "constraints": [
            "NumPy and the standard library only.",
            "No handshake output may depend on the other side's signal in the same cycle: `in_ready` is a function of stage 1's occupancy alone, and `out_valid` of stage 2's.",
            "`stimulus.py` is read-only.",
            "The bench compares against a reference computed independently of the pipeline — never against the pipeline's own output.",
            "Every stage holds exactly two items. A one-deep stage fails on the cycle counts, and the depth itself is checked directly: with the sink held low the design must accept four items — two per stage — and then refuse.",
        ],
        "rubric": [
            {"criterion": "Cycle-accurate model", "weight": 25,
             "evidence": "Registers commit together on one edge, and the pipeline retires twelve items in fourteen cycles when nothing stalls — one cycle per item plus two of latency."},
            {"criterion": "Elastic handshake", "weight": 25,
             "evidence": "Under the seeded valid and ready patterns every item is delivered exactly once and in order, with no duplication and no loss, and in and out decisions are taken from the registered occupancy."},
            {"criterion": "Self-checking bench", "weight": 30,
             "evidence": "Results are compared against an independent reference function, the monitor reports an empty violation list for the real design and a non-empty one for a hand-made illegal trace."},
            {"criterion": "Timing budget", "weight": 20,
             "evidence": "min_period and max_frequency implement the setup constraint including skew, and correctly show what splitting the slowest stage buys in frequency."},
        ],
        "hints": [
            "Compute all three registered outputs — `in_ready`, `out_valid`, `out_item` — and the two internal decisions before you mutate either stage. Everything after that is bookkeeping.",
            "Stage 1 stores the tuple `(p, a, b)`, not just `p`: stage 2 needs the operands, and in RTL that means they are pipelined alongside the product in registers of their own.",
            "The loop ends when everything has been sent and both stages are empty. Test that condition after the cycle count is incremented, or the last item's departure cycle goes uncounted.",
            "`monitor` is the same rule as `handshake_legal` from module 3, except that it returns the offending cycle indices instead of a verdict — which is what makes a failure debuggable.",
        ],
        "files": [
            {"name": "stimulus.py", "ro": True, "content": r'''
"""Stimulus for the bench. Read-only: the checks generate exactly these patterns."""
import numpy as np


def payloads(seed, n):
    """`n` pairs of 8-bit operands."""
    rng = np.random.default_rng(seed)
    return [(int(a), int(b)) for a, b in rng.integers(0, 256, size=(n, 2))]


def valid_pattern(seed, cycles, duty=0.7):
    """A source-offers waveform: 1 on roughly `duty` of the cycles."""
    rng = np.random.default_rng(2000 + seed)
    return [int(x) for x in (rng.random(cycles) < duty)]


def ready_pattern(seed, cycles, duty=0.5):
    """A sink-ready waveform: 1 on roughly `duty` of the cycles."""
    rng = np.random.default_rng(1000 + seed)
    return [int(x) for x in (rng.random(cycles) < duty)]
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from stimulus import payloads, valid_pattern, ready_pattern

MASK16 = 0xFFFF

# Clock budget:
#   the stage that sets the period -> TODO, and what splitting it would buy
#   (the design has two stages: the multiply, then the adder)


class Reg:
    """A bank of `width` flip-flops. Reads see q; writes land in d."""

    def __init__(self, width, value=0):
        self.width = int(width)
        self.mask = (1 << self.width) - 1
        self.q = int(value) & self.mask
        self.d = self.q

    def drive(self, value):
        # TODO
        pass

    def commit(self):
        # TODO
        pass


def tick(regs):
    """One edge for a whole design."""
    # TODO
    pass


def expected(a, b):
    """The reference function, written from the specification."""
    # TODO
    return 0


class Pipeline:
    """Two elastic stages, each holding at most two items."""

    def __init__(self):
        self.s1 = []
        self.s2 = []

    def step(self, in_valid, in_item, out_ready):
        """One cycle. Return (in_ready, out_valid, out_item)."""
        # TODO: registered outputs first, then out / move / in.
        return 0, 0, None


def monitor(record):
    """Cycle indices at which the output interface broke the stability rule."""
    # TODO
    return []


def run(items, valid_pat, ready_pat):
    """Drive the pipeline. Return (received, cycles, violations)."""
    dut = Pipeline()
    sent = 0
    got = []
    record = []
    cycle = 0
    cap = 60 * (len(items) + 8)
    while cycle < cap:
        offer = 1 if sent < len(items) else 0
        if valid_pat:
            offer = offer and valid_pat[cycle % len(valid_pat)]
        item = items[sent] if sent < len(items) else None
        rdy = ready_pat[cycle % len(ready_pat)] if ready_pat else 1
        # TODO: step the pipeline, record the output interface, count what was
        # accepted and what was delivered, and stop once both stages are empty.
        break
    return got, cycle, monitor(record)


def min_period(stage_delays, t_cq, t_setup, t_skew):
    """The smallest period the slowest stage will close at."""
    # TODO
    return 0.0


def max_frequency(stage_delays, t_cq, t_setup, t_skew):
    """One over the minimum period."""
    # TODO
    return 0.0


if __name__ == "__main__":
    items = payloads(11, 12)
    got, cycles, bad = run(items, None, None)
    print("no stalls:", cycles, "cycles,", len(got), "items,", len(bad), "violations")
    print("min period:", min_period([1.2, 0.7], 0.05, 0.04, 0.02))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from stimulus import payloads, valid_pattern, ready_pattern

MASK16 = 0xFFFF

# Clock budget:
#   stage 1's multiply is 1.2 ns of logic and stage 2's adder is 0.7 ns, so the
#   multiply sets the period and the design closes at 1.27 ns. Splitting that multiply
#   into two 0.6 ns halves leaves the 0.7 ns adder critical and takes the period to
#   0.77 ns — a 1.65x frequency gain for one more stage of latency and one more set
#   of registers.


class Reg:
    """A bank of `width` flip-flops. Reads see q; writes land in d."""

    def __init__(self, width, value=0):
        self.width = int(width)
        self.mask = (1 << self.width) - 1
        self.q = int(value) & self.mask
        self.d = self.q

    def drive(self, value):
        self.d = int(value) & self.mask

    def commit(self):
        self.q = self.d


def tick(regs):
    """One edge for a whole design."""
    for r in regs:
        r.commit()


def expected(a, b):
    """The reference function, written from the specification."""
    return (a * b + a + b) & MASK16


class Pipeline:
    """Two elastic stages, each holding at most two items."""

    def __init__(self):
        self.s1 = []
        self.s2 = []

    def step(self, in_valid, in_item, out_ready):
        """One cycle. Return (in_ready, out_valid, out_item)."""
        in_ready = 1 if len(self.s1) < 2 else 0
        mid_valid = len(self.s1) > 0
        mid_ready = len(self.s2) < 2
        out_valid = 1 if len(self.s2) > 0 else 0
        out_item = self.s2[0] if self.s2 else None

        take_in = bool(in_valid) and bool(in_ready)
        move = mid_valid and mid_ready
        take_out = bool(out_valid) and bool(out_ready)

        if take_out:
            self.s2.pop(0)
        if move:
            p, a, b = self.s1.pop(0)
            self.s2.append((p + a + b) & MASK16)
        if take_in:
            a, b = in_item
            self.s1.append(((a * b) & MASK16, a, b))
        return in_ready, out_valid, out_item


def monitor(record):
    """Cycle indices at which the output interface broke the stability rule."""
    bad = []
    for c in range(len(record) - 1):
        valid, ready, data = record[c]
        if valid and not ready:
            nxt_valid, _, nxt_data = record[c + 1]
            if not nxt_valid or nxt_data != data:
                bad.append(c)
    return bad


def run(items, valid_pat, ready_pat):
    """Drive the pipeline. Return (received, cycles, violations)."""
    dut = Pipeline()
    sent = 0
    got = []
    record = []
    cycle = 0
    cap = 60 * (len(items) + 8)
    while cycle < cap:
        offer = 1 if sent < len(items) else 0
        if valid_pat:
            offer = offer and valid_pat[cycle % len(valid_pat)]
        item = items[sent] if sent < len(items) else None
        rdy = ready_pat[cycle % len(ready_pat)] if ready_pat else 1
        in_ready, out_valid, out_item = dut.step(offer, item, rdy)
        record.append((out_valid, rdy, out_item))
        if offer and in_ready:
            sent += 1
        if out_valid and rdy:
            got.append(out_item)
        cycle += 1
        if sent == len(items) and not dut.s1 and not dut.s2:
            break
    return got, cycle, monitor(record)


def min_period(stage_delays, t_cq, t_setup, t_skew):
    """The smallest period the slowest stage will close at."""
    return float(np.max(stage_delays)) + t_cq + t_setup - t_skew


def max_frequency(stage_delays, t_cq, t_setup, t_skew):
    """One over the minimum period."""
    return 1.0 / min_period(stage_delays, t_cq, t_setup, t_skew)


if __name__ == "__main__":
    items = payloads(11, 12)
    got, cycles, bad = run(items, None, None)
    print("no stalls:", cycles, "cycles,", len(got), "items,", len(bad), "violations")
    print("min period:", min_period([1.2, 0.7], 0.05, 0.04, 0.02))
'''},
        ],
        "tests": [
            {"name": "the register kernel commits everything on one edge", "code": r'''
_a = Reg(4, 1)
_b = Reg(4, 2)
_a.drive(_b.q)
_b.drive(_a.q)
assert (_a.q, _b.q) == (1, 2), (
    f"driving must not change q — got {(_a.q, _b.q)} before the edge")
tick([_a, _b])
assert (_a.q, _b.q) == (2, 1), (
    f"got {(_a.q, _b.q)} — both right-hand sides are the values held before the "
    "edge, so the two registers swap")
'''},
            {"name": "with nothing stalling the pipeline retires one item per cycle", "code": r'''
from stimulus import payloads
_items = payloads(11, 12)
_ref = [expected(a, b) for a, b in _items]
_got, _cycles, _bad = run(_items, None, None)
assert _got == _ref, (
    f"first mismatch at index {next((i for i, (g, r) in enumerate(zip(_got, _ref)) if g != r), None)}"
    f" — expected {_ref[:3]}..., got {_got[:3]}...")
assert _cycles == 14, (
    f"got {_cycles} cycles for twelve items. Two stages of latency plus one item "
    "per cycle is 14; more than that means a stage is not accepting while it drains")
assert _bad == [], f"no back-pressure was applied, so nothing could violate the protocol: {_bad}"
'''},
            {"name": "the reference is computed independently of the design", "code": r'''
assert expected(0, 0) == 0, "0*0 + 0 + 0 is 0"
assert expected(1, 1) == 3, f"1*1 + 1 + 1 is 3, got {expected(1, 1)}"
assert expected(255, 255) == 65535, (
    f"255*255 + 255 + 255 is 65535, which is exactly the 16-bit maximum, got "
    f"{expected(255, 255)}")
assert expected(200, 200) == 40400, (
    f"200*200 + 200 + 200 is 40400, got {expected(200, 200)}. Sixteen bits is "
    "exactly enough here and never actually truncates, which is worth knowing "
    "rather than assuming")
'''},
            {"name": "back-pressure loses nothing and duplicates nothing", "code": r'''
from stimulus import payloads, valid_pattern, ready_pattern
_items = payloads(11, 12)
_ref = [expected(a, b) for a, b in _items]
_vp = valid_pattern(4, 64)
_rp = ready_pattern(4, 64)
_got, _cycles, _bad = run(_items, _vp, _rp)
assert len(_got) == 12, (
    f"twelve items went in and {len(_got)} came out — a repeated item means the "
    "head was not removed on a transfer, a missing one means it was removed twice")
assert _got == _ref, f"the delivered stream is out of order or wrong: {_got[:4]} vs {_ref[:4]}"
assert _cycles == 28, (
    f"got {_cycles} — with this seeded pattern pair the run takes 28 cycles; a "
    "different count means the handshake is accepting or delivering on the wrong cycles")
'''},
            {"name": "each stage holds two items and no more", "code": r'''
_p = Pipeline()
_seq = []
for _c in range(10):
    _ir, _ov, _oi = _p.step(1, (3, 4), 0)
    _seq.append(int(bool(_ir)))
assert sum(_seq) == 4, (
    f"with the sink held low for ten cycles the design accepted {sum(_seq)} items. "
    "Two stages of two entries hold exactly four before the source is refused — a "
    "one-deep stage would take two, a four-deep stage eight")
assert _seq == [1, 1, 1, 1, 0, 0, 0, 0, 0, 0], (
    f"in_ready went {_seq}. It must stay asserted for four cycles even though "
    "out_ready was low throughout — it is a function of stage 1's occupancy alone — "
    "and once both stages are full it must stay low")
'''},
            {"name": "a stalled sink sees stable data, and the monitor would say so", "code": r'''
from stimulus import payloads, valid_pattern, ready_pattern
_got, _cycles, _bad = run(payloads(11, 12), valid_pattern(4, 64), ready_pattern(4, 64))
assert _bad == [], (
    f"the design withdrew valid or changed its data while the sink was stalled, at "
    f"cycles {_bad}")
assert monitor([(1, 0, 5), (0, 0, None)]) == [0], (
    "a source that drops valid before the transfer is a violation at cycle 0")
assert monitor([(1, 0, 5), (1, 1, 6)]) == [0], (
    "changing the data under a stalled sink is a violation at cycle 0")
assert monitor([(1, 0, 5), (1, 1, 5), (0, 1, None)]) == [], (
    "this trace holds valid and its data until the transfer — a monitor that flags "
    "it will flag every correct design")
'''},
            {"name": "the clock budget prices the slowest stage", "code": r'''
_p = min_period([1.2, 0.7], 0.05, 0.04, 0.02)
assert abs(_p - 1.27) < 1e-9, (
    f"got {_p} — only the slowest stage matters: 1.2 of logic, plus t_cq and "
    "t_setup, less the skew that is lent to the path")
_split = min_period([0.6, 0.6, 0.7], 0.05, 0.04, 0.02)
assert abs(_split - 0.77) < 1e-9, (
    f"got {_split} — splitting the 1.2 stage in two leaves the 0.7 adder critical")
_f0 = max_frequency([1.2, 0.7], 0.05, 0.04, 0.02)
_f1 = max_frequency([0.6, 0.6, 0.7], 0.05, 0.04, 0.02)
assert abs(_f0 - 1.0 / 1.27) < 1e-9, f"frequency is one over the period, got {_f0}"
assert abs(_f1 / _f0 - 1.27 / 0.77) < 1e-9, (
    f"the split should buy a factor of {1.27 / 0.77:.3f} in frequency, got {_f1 / _f0:.3f}")
'''},
        ],
    },
}
