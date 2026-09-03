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
            "read": [
                {
                    "title": "Two traces from one shift register",
                    "minutes": 16,
                    "body": r'''
Here is a three-stage shift register, and two traces of its output. One of them is
what the hardware does.

```text
   in --> | D0 | --> | D1 | --> | D2 | --> out

   input bits   1  0  0  0
   trace A      0  0  0  1  0  0  0
   trace B      0  1  0  0  0  0  0
```

A single 1 is presented at the input in cycle 0. In trace A it reaches the output in
cycle 3, one cycle per stage, which is what three flip-flops in a row are for. In
trace B it reaches the output in cycle 1, having crossed all three of them inside a
single clock period.

Both traces came out of the same model, on the same input, with the same three
stages. The only thing that differed between the runs producing them was the order in
which the three stages were written down inside the loop that drives them. Nothing
about a shift register should care about that.

```python
class Reg:
    """A bank of flip-flops. Reads see q; writes land in d."""

    def __init__(self, width, value=0):
        self.mask = (1 << width) - 1
        self.q = value & self.mask
        self.d = self.q

    def drive(self, value):
        self.d = value & self.mask

    def commit(self):
        self.q = self.d


class EagerReg(Reg):
    def drive(self, value):
        self.d = value & self.mask
        self.q = self.d               # the one extra line


def shift(cls, bits, head_first, depth=3):
    chain = [cls(1) for _ in range(depth)]
    out = []
    for c in range(len(bits) + depth):
        out.append(chain[-1].q)
        stages = range(depth) if head_first else range(depth - 1, -1, -1)
        for i in stages:
            if i == 0:
                chain[0].drive(bits[c] if c < len(bits) else 0)
            else:
                chain[i].drive(chain[i - 1].q)
        for r in chain:
            r.commit()
    return out


for cls in (Reg, EagerReg):
    for head_first in (True, False):
        print("%-8s %-10s %s" % (cls.__name__,
                                 "head first" if head_first else "tail first",
                                 shift(cls, [1, 0, 0, 0], head_first)))
```

```text
Reg      head first [0, 0, 0, 1, 0, 0, 0]
Reg      tail first [0, 0, 0, 1, 0, 0, 0]
EagerReg head first [0, 1, 0, 0, 0, 0, 0]
EagerReg tail first [0, 0, 0, 1, 0, 0, 0]
```

Three of the four runs agree. The fourth is trace B, and the difference between the
two classes is one line.

## D and Q are different wires

A D flip-flop has an input and an output, and they are not the same node. $Q$ carries
the value that was on $D$ at the last rising edge and holds it, unchanged, for the
whole of the cycle that follows. $D$ carries whatever the combinational logic in front
of the flop is currently producing, and it moves around during the cycle as that logic
settles. The edge is the only moment at which the two are connected.

Follow the consequences for a whole design rather than one flop. Every combinational
cloud in the design reads some flop's $Q$ and drives some flop's $D$. Because the $Q$s
do not move during the cycle, every cloud is computing on the same snapshot of the
design's state — the one that was latched at the previous edge. The next edge then
copies every $D$ onto its $Q$ at the same instant. So a cycle has exactly two events
in it, and only two: *evaluate everything from the current state*, then *commit
everything at once*.

That is the entire model, and it explains the four lines of output above. `Reg.drive`
writes $D$ and leaves $Q$ where it was, so `chain[i].drive(chain[i - 1].q)` reads a
value that no other `drive` in that cycle can have disturbed. `EagerReg.drive` writes
$Q$ as well, which is a wire from $D$ straight through to $Q$ with no edge in between,
and the model stops being a model of flip-flops.

The Verilog for the same thing is two lines, and the operator carries the rule:

```verilog
always_ff @(posedge clk) begin
  a <= b;
  b <= a;      // both right-hand sides are the pre-edge values, so this swaps
end
```

`<=` is not an assignment that happens later out of politeness. It is the statement
that the right-hand side is evaluated now and the left-hand side updated at the end of
the time step, together with every other non-blocking update scheduled in that step,
which is what "one edge, everywhere at once" means when it is written down as a
simulation rule.

## The mistake, and why it survives

The tempting position is that the two-phase split is bookkeeping — that as long as you
write the stages down in the right order, updating each register as you go produces the
same answer for less machinery. It is tempting because on most of what you test, it
does.

```python
class Reg:
    def __init__(self, width, value=0):
        self.mask = (1 << width) - 1
        self.q = value & self.mask
        self.d = self.q

    def drive(self, value):
        self.d = value & self.mask

    def commit(self):
        self.q = self.d


class EagerReg(Reg):
    def drive(self, value):
        self.d = value & self.mask
        self.q = self.d


def run(regs, logic, cycles):
    out = []
    for c in range(cycles):
        out.append(tuple(r.q for r in regs))
        logic(c)
        for r in regs:
            r.commit()
    return out


def swap(cls):
    a, b = cls(4, 1), cls(4, 2)

    def logic(c):
        a.drive(b.q)
        b.drive(a.q)

    return run([a, b], logic, 4)


def count(cls):
    r = cls(3, 0)
    return [s[0] for s in run([r], lambda c: r.drive(r.q + 1), 10)]


for cls in (Reg, EagerReg):
    print("%-8s swap  %s" % (cls.__name__, swap(cls)))
    print("%-8s count %s" % (cls.__name__, count(cls)))
```

```text
Reg      swap  [(1, 2), (2, 1), (1, 2), (2, 1)]
Reg      count [0, 1, 2, 3, 4, 5, 6, 7, 0, 1]
EagerReg swap  [(1, 2), (2, 2), (2, 2), (2, 2)]
EagerReg count [0, 1, 2, 3, 4, 5, 6, 7, 0, 1]
```

The counter is identical under both kernels, and so, from the first listing, is the
tail-first shift register. A design with one register cannot expose the defect at all,
because there is nothing for a stale read to be stale relative to; and a chain driven
from its tail happens to read each stage before that stage is overwritten, so it
launders the bug. Two of the three designs in the lab's `__main__` pass with a broken
kernel. The one that does not is the swap, which collapses to $(2,2)$ and stays there,
because `b.drive(a.q)` read an `a` that had already taken `b`'s value on the line
above.

That is why the lab *A two-phase register kernel* ends on a check that drives the same
chain both ways and compares the two traces against each other rather than against an
expected list. An expected list can be satisfied by a kernel that is right by accident
on that ordering. Agreement between two orderings cannot be, because order-independence
is the property being claimed, and it is the property that lets you write the stages of
a real design in whatever order the source file happens to put them.

## The period the model does not have

Everything above counts cycles and says nothing about how long a cycle is. That
separation is what makes a cycle-accurate model worth running — the sandbox *One row
per instruction, one column per clock* has no time axis finer than a column, and it is
exact about what the machine computes and how many cycles it takes — but it also means
the model cannot tell you whether the design runs at 2 GHz or at 200 MHz. That number
comes from one path.

Between the launching edge and the capturing edge, three delays happen in series: the
launching flop's clock-to-output $t_{cq}$, the combinational cloud's propagation
$t_{logic}$, and the setup window $t_{setup}$ during which the capturing flop's input
must already be still. If the capture clock arrives $t_{skew}$ later than the launch
clock, that much extra time is available. So

$$T + t_{skew} \ge t_{cq} + t_{logic} + t_{setup}$$

and the slack — how much of the period was left over — is the difference between the
two sides. Those are the first three steps of the derivation *What has to fit between
two edges*; put numbers in them.

```python
t_cq, t_setup, t_hold, t_skew = 42, 35, 40, 15


def slack(T, t_logic):
    return T + t_skew - t_cq - t_logic - t_setup


def hold_margin(t_short):
    return t_cq + t_short - t_hold - t_skew


t_min = t_cq + 420 + t_setup - t_skew
print("critical path 420 ps: T_min = %d ps, f_max = %.3f GHz" % (t_min, 1000.0 / t_min))
for T in (450, 500, 550):
    print("  T = %3d ps: slack %+4d ps at 420 ps, %+4d ps at 450 ps"
          % (T, slack(T, 420), slack(T, 450)))
for T in (450, 500, 4000):
    print("  T = %4d ps: hold margin on an 8 ps path %+d ps" % (T, hold_margin(8)))
```

```text
critical path 420 ps: T_min = 482 ps, f_max = 2.075 GHz
  T = 450 ps: slack  -32 ps at 420 ps,  -62 ps at 450 ps
  T = 500 ps: slack  +18 ps at 420 ps,  -12 ps at 450 ps
  T = 550 ps: slack  +68 ps at 420 ps,  +38 ps at 450 ps
  T =  450 ps: hold margin on an 8 ps path -5 ps
  T =  500 ps: hold margin on an 8 ps path -5 ps
  T = 4000 ps: hold margin on an 8 ps path -5 ps
```

Read the middle block first. At a 500 ps period the 420 ps path has 18 ps to spare and
the 450 ps path is 12 ps short, and stretching the period to 550 ps rescues both. That
is the whole of setup closure, and it is why a part that misses its frequency target is
still a part: it is sold at a lower bin.

Now read the last three lines, which are identical. $T$ does not appear in the hold
margin at all. A path so short that the new data arrives at the capturing flop before
that flop has finished sampling the old data is broken at every clock frequency,
including a stopped clock, and the 8 ps path above is 5 ps broken. Hold is fixed by
adding delay to the fast path or by rebalancing the clock tree, never by slowing down.
The inference that a timing failure can be run slower is drawn from experience, because
setup failures are the ones you meet first and slowing down does fix those.

## Where the model stops holding

The two-phase update assumes there is one edge. A design with two clocks has two, at no
fixed offset, and a signal crossing between them can be sampled while it is changing —
the flop's output then settles to a legal level after an unbounded delay, and the
synchroniser that makes this improbable enough to ship is a different subject with a
different arithmetic. The model in this module has one `tick`, and every register in it
commits on that tick.

The single-cycle setup equation also assumes the two flops are clocked by edges one
period apart. Multicycle paths, where the design guarantees the destination will not
sample for two or three periods, are exceptions declared to the timing tool by hand,
and an undeclared one is reported as a violation that is not there while a wrongly
declared one hides a violation that is.

And a cycle-accurate model has nothing to say about what happens between edges. A glitch
on a combinational output is invisible to it and can still be fatal — asynchronous
resets, clock enables built from combinational logic and anything driving an output pad
all care about the transient, not only the settled value. Module 2 returns to this as
the reason a Moore output is worth its extra cycle.

## What you are about to build

The lab *A two-phase register kernel* is the `Reg`, `tick` and `run` above, plus the
three small designs the listings used: the swap, the counter and the shift register. Its
checks are the numbers on this page — $(1,2)$ alternating with $(2,1)$, a three-bit
counter wrapping from 7 to 0, a bit arriving at the tail in cycle 3 — and the one that
does the real work compares a head-first chain with a tail-first one. Everything later
in the course runs on that kernel, including the capstone's two-stage pipeline. The
derivation *What has to fit between two edges* writes the five expressions this page
used numbers for, and ends where the numbers above ended: on the margin that has no $T$
in it.
''',
                },
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
            "quiz": {
                "title": "One edge, one update, everywhere at once",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In the synchronous model, where does state live?",
                        "opts": [
                            "Only in registers",
                            "In registers and in the combinational logic between them",
                            "Wherever a signal is assigned",
                            "In whatever the simulator remembers between events",
                        ],
                        "a": 0,
                        "why": r"""
Everything between two registers is a pure function of the current register contents —
it has no memory, and whatever transient it goes through during the cycle is irrelevant
provided it has settled by the next edge. That single restriction is what makes digital
design tractable: an unbounded analogue problem becomes a finite state machine plus a
timing constraint.
""",
                    },
                    {
                        "q": "At the clock edge, every next-state function is evaluated from what?",
                        "opts": [
                            "The current values, all simultaneously",
                            "The values as updated in program order",
                            "The values from the previous edge but one",
                            "Whichever values have settled first",
                        ],
                        "a": 0,
                        "why": r"""
All at once, from the pre-edge values. Two registers that swap contents do so correctly
and simultaneously, which has no equivalent in sequential code — and it is exactly what
non-blocking assignment expresses in Verilog. Using blocking assignment in a clocked
block makes the result depend on the order the lines happen to be written, which is
where a design and its synthesis diverge silently.
""",
                    },
                    {
                        "q": "What must the clock period exceed?",
                        "opts": [
                            "The slowest register-to-register path, plus setup time and clock skew",
                            "The average combinational delay",
                            "The sum of every path in the design",
                            "The propagation delay of the slowest gate",
                        ],
                        "a": 0,
                        "why": r"""
One path decides the whole clock, and it is the worst one — averages are irrelevant, and
so is the total, since the paths run in parallel. Note the additions: setup time is the
register's own requirement and skew is the clock arriving at the two ends at different
moments, and both eat into the period before any logic is done. Which is why timing
closure is so often about the last hundred picoseconds.
""",
                    },
                    {
                        "q": "How fine a time axis does a cycle-accurate model need?",
                        "opts": [
                            "None finer than the edge — cycle count is the answer",
                            "Picoseconds, to model the gates",
                            "Nanoseconds, to model the clock",
                            "It depends on the technology",
                        ],
                        "a": 0,
                        "why": r"""
If the timing constraint is met, nothing observable happens between edges, so a model can
step edge to edge and still be exact about *what* the machine computes and *how many
cycles* it takes. That is why a cycle-accurate simulator can run thousands of times
faster than a gate-level one and still answer architectural questions correctly — and
why it cannot answer the question of what the clock frequency will be.
""",
                    },
                    {
                        "q": "Which assignment belongs in a clocked block?",
                        "opts": [
                            "Non-blocking, because it models simultaneous update",
                            "Blocking, because it is faster to simulate",
                            "Either, as they are equivalent",
                            "Blocking, because it matches synthesis",
                        ],
                        "a": 0,
                        "why": r"""
Non-blocking schedules the update for the end of the time step, so every right-hand side
reads pre-edge values — exactly the hardware's behaviour. Blocking assignment in a clocked
block simulates as sequential code, and the synthesised circuit does *not*, so the design
passes its test bench and fails in silicon. It is the most consequential style rule in
RTL, and it is a rule precisely because both compile.
""",
                    },
                ],
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
            "read": [
                {
                    "title": "Two detectors, and the cycle between them",
                    "minutes": 17,
                    "body": r'''
Two machines watch the same bit stream for the pattern `1101`, overlaps counted. Here
is what they produce for seven bits.

```text
   cycle        0  1  2  3  4  5  6  7
   bit in       1  1  0  1  1  0  1  -
   Mealy out    0  0  0  1  0  0  1  -
   Moore out    0  0  0  0  1  0  0  1
```

Two matches, at bit index 0 and at bit index 3, sharing the `1` in the middle. The
Mealy machine reports each one in the cycle the fourth bit arrives. The Moore machine
reports each one the cycle after, which is why its output vector has eight entries for
seven bits: the last match needs a cycle in which to be visible, and there is no eighth
bit to accompany it.

Both machines are correct. They differ in where the output is read from, and that
choice fixes everything else about them — how many states they need, what their
transition tables look like, and how much of the clock period is left for whatever is
downstream.

## Numbering the states so the table writes itself

A detector has to remember how much of the pattern is already in hand. Give a state
that meaning and nothing else: **state $s$ means the last $s$ bits seen are exactly the
first $s$ bits of `1101`, and no longer run of them is**. That is one rule, and every
transition follows from it without a diagram.

```python
PATTERN = "1101"


def state_after(seen):
    """The longest suffix of `seen` that is still a prefix of PATTERN."""
    for k in range(min(len(seen), len(PATTERN)), -1, -1):
        if seen[len(seen) - k:] == PATTERN[:k]:
            return k


MOORE = {(s, b): state_after(PATTERN[:s] + str(b))
         for s in range(5) for b in (0, 1)}
for s in range(5):
    print("state %d (%-4s) --0--> %d   --1--> %d"
          % (s, PATTERN[:s] or "-", MOORE[(s, 0)], MOORE[(s, 1)]))


def run_moore(bits):
    s, out = 0, []
    for b in bits:
        out.append(1 if s == 4 else 0)
        s = MOORE[(s, b)]
    out.append(1 if s == 4 else 0)
    return out


def occurrences(bits):
    text = "".join(str(b) for b in bits)
    return sum(1 for i in range(len(text) - 3) if text[i:i + 4] == PATTERN)


wrong = sum(1 for n in range(1 << 12)
            for bits in [[(n >> i) & 1 for i in range(11, -1, -1)]]
            if sum(run_moore(bits)) != occurrences(bits))
print("streams of 12 bits where the table miscounts: %d of 4096" % wrong)
```

```text
state 0 (-   ) --0--> 0   --1--> 1
state 1 (1   ) --0--> 0   --1--> 2
state 2 (11  ) --0--> 3   --1--> 2
state 3 (110 ) --0--> 0   --1--> 4
state 4 (1101) --0--> 0   --1--> 2
streams of 12 bits where the table miscounts: 0 of 4096
```

Ten transitions, none of them guessed, and a brute-force count over every twelve-bit
stream agrees with the machine on all 4096 of them.

Two rows are worth reading slowly, because they are the two people write down wrong.
From state 2, holding `11`, another `1` gives `111`; the longest suffix of that which is
a prefix of `1101` is `11`, so the machine stays in state 2 — a run of ones never costs
you the `11` you already have. And from state 4, holding `1101`, another `1` gives
`11011`; the longest suffix of that which is a prefix is `11`, so the machine goes to
state 2 and not to state 1 and not back to 0. That single transition is what makes the
detector find the second match in `1101101`. A machine that returns to state 1 there
under-reports on 180 of the 4096 twelve-bit streams and never over-reports, which is a
failure that looks like a quiet stream rather than like a bug.

## The Mealy machine is not this table with a row deleted

The Mealy detector has four states. The usual account is that state 4 was removed
because the match is now signalled on the transition into it, and that is the right
story about the *output*. It is not enough to build the next-state table, and the
listing above says why.

```python
PATTERN = "1101"


def state_after(seen):
    for k in range(min(len(seen), len(PATTERN)), -1, -1):
        if seen[len(seen) - k:] == PATTERN[:k]:
            return k


MOORE = {(s, b): state_after(PATTERN[:s] + str(b))
         for s in range(5) for b in (0, 1)}
print("row for state 4:", [MOORE[(4, b)] for b in (0, 1)])
print("row for state 1:", [MOORE[(1, b)] for b in (0, 1)])

MEALY = {}
for s in range(4):
    for b in (0, 1):
        t = MOORE[(s, b)]
        MEALY[(s, b)] = 1 if t == 4 else t
print("mealy_next(3, 1) =", MEALY[(3, 1)])


def run_moore(bits):
    s, out = 0, []
    for b in bits:
        out.append(1 if s == 4 else 0)
        s = MOORE[(s, b)]
    out.append(1 if s == 4 else 0)
    return out


def run_mealy(bits, table=MEALY):
    s, out = 0, []
    for b in bits:
        out.append(1 if (s == 3 and b) else 0)
        s = table[(s, b)]
    return out


stream = [1, 1, 0, 1, 1, 0, 1]
print("moore:", run_moore(stream))
print("mealy:", run_mealy(stream))
print("moore[1:] == mealy:", run_moore(stream)[1:] == run_mealy(stream))
```

```text
row for state 4: [0, 2]
row for state 1: [0, 2]
mealy_next(3, 1) = 1
moore: [0, 0, 0, 0, 1, 0, 0, 1]
mealy: [0, 0, 0, 1, 0, 0, 1]
moore[1:] == mealy: True
```

States 4 and 1 have identical rows. Whatever the stream does next, a machine sitting in
state 4 and a machine sitting in state 1 will be in the same state ever after — the two
are indistinguishable by their futures. The only thing that told them apart was the
Moore output, which is a function of the state and therefore has to give them different
values. Move the output onto the transition and that last distinction goes, so 4 and 1
may be merged, and the Mealy machine's state 1 *is* the pair of them.

Read `mealy_next(3, 1)` in that light. The bit being consumed is the fourth bit of the
match; the machine has now seen `1101`, which is Moore state 4, which is the same thing
as Mealy state 1. So the transition goes to 1, and the last line of the output confirms
the two machines are the same detector one cycle apart: `moore[1:] == mealy` over the
whole stream.

## The mistake: copying the transition out of the Moore table

Here is what the reasoning above is competing with, and it is close enough to be
persuasive. State 4 leaves on a `1` for state 2. The Mealy machine has no state 4, so
the transition that would have gone through it should go where state 4's own outgoing
edge goes — to state 2. Same picture, one fewer hop.

```python
PATTERN = "1101"


def state_after(seen):
    for k in range(min(len(seen), len(PATTERN)), -1, -1):
        if seen[len(seen) - k:] == PATTERN[:k]:
            return k


MOORE = {(s, b): state_after(PATTERN[:s] + str(b)) for s in range(5) for b in (0, 1)}
MEALY = {(s, b): (1 if MOORE[(s, b)] == 4 else MOORE[(s, b)])
         for s in range(4) for b in (0, 1)}
COPIED = dict(MEALY)
COPIED[(3, 1)] = MOORE[(4, 1)]          # "state 4 leaves on a 1 for state 2"


def run_mealy(bits, table):
    s, out = 0, []
    for b in bits:
        out.append(1 if (s == 3 and b) else 0)
        s = table[(s, b)]
    return out


def occurrences(bits):
    text = "".join(str(b) for b in bits)
    return sum(1 for i in range(len(text) - 3) if text[i:i + 4] == PATTERN)


print("mealy_next(3, 1): correct %d, copied %d" % (MEALY[(3, 1)], COPIED[(3, 1)]))
for name, bits in (("1101101", [1, 1, 0, 1, 1, 0, 1]),
                   ("110101 ", [1, 1, 0, 1, 0, 1])):
    print("%s correct %s  copied %s"
          % (name, run_mealy(bits, MEALY), run_mealy(bits, COPIED)))

over = under = 0
for n in range(1 << 12):
    bits = [(n >> i) & 1 for i in range(11, -1, -1)]
    d = sum(run_mealy(bits, COPIED)) - occurrences(bits)
    over += d > 0
    under += d < 0
print("over 12-bit streams: %d over-report, %d under-report" % (over, under))
```

```text
mealy_next(3, 1): correct 1, copied 2
1101101 correct [0, 0, 0, 1, 0, 0, 1]  copied [0, 0, 0, 1, 0, 0, 1]
110101  correct [0, 0, 0, 1, 0, 0]  copied [0, 0, 0, 1, 0, 1]
over 12-bit streams: 443 over-report, 0 under-report
```

The second line is the reason this bug reaches review. On `1101101`, the stream in the
lab's `__main__` and the one this page opened with, the copied table is output-for-output
identical to the correct one. Both find both matches, in the right cycles. The shortest
stream that separates them is six bits, `110101`, where the copied machine reports a
match in the last cycle that is not there: it went from the completed `1101` to state 2,
which claims two bits of credit for a `01` that contains one.

The error is one-directional, which makes it worse. Across all 4096 twelve-bit streams
it over-reports on 443 and under-reports on none, so a bench that only ever asks "did we
find the matches we planted" passes every time. The check that catches it in the lab
*A sequence detector, twice* is the one that counts: its sixteen-bit stream contains
four occurrences and the copied table asserts five, and `assert sum(_y) == 4` is what
turns that into a failure.

## What the cycle costs, in picoseconds

The Moore output is a function of the state register alone, so its path starts at that
register's clock output. The Mealy output is a function of the state *and* the
input, so its path starts wherever the input started — another flop, with another cloud
in front of it. Charge both with module 1's numbers.

```python
T, t_cq, t_setup = 500, 42, 35
t_out = 60          # the output function's own delay
t_in = 180          # combinational delay in front of this machine's input

moore_valid = t_cq + t_out
mealy_valid = t_cq + t_in + t_out
print("Moore output valid at %3d ps into the cycle" % moore_valid)
print("Mealy output valid at %3d ps into the cycle" % mealy_valid)
for name, valid in (("Moore", moore_valid), ("Mealy", mealy_valid)):
    print("  %s leaves the consumer %3d ps of the %d ps period"
          % (name, T - valid - t_setup, T))
```

```text
Moore output valid at 102 ps into the cycle
Mealy output valid at 282 ps into the cycle
  Moore leaves the consumer 363 ps of the 500 ps period
  Mealy leaves the consumer 183 ps of the 500 ps period
```

The cycle the Mealy machine saves in latency it spends in the period, and it spends it
on the consumer's side of the interface where it is hardest to get back. The Moore
output is also stable for the whole cycle by construction, because the state register
does not move between edges, whereas the Mealy output carries every glitch the input's
cloud produces while it settles. Anything edge-sensitive downstream — a write enable, an
output pad, a synchroniser into another clock — wants the Moore output for that reason
alone.

## Encodings, and the codes nobody meant to write

The five states above need three flip-flops in a binary encoding, and three flops have
eight codes, so three of them mean nothing. One-hot spends five flops, one per state,
and 27 of its 32 codes are illegal. The trade is that one-hot's next-state logic needs
no decoder: the bit for state 2 is an OR of the state-1 bit and the state-2 bit under
input `1`, which is one gate, where the binary encoding has to decode three bits before
it can decide anything.

The illegal codes are not a curiosity: a state graph is written over the states you
named, and the synthesised logic still has to do *something* in every code the flops can
hold. `reachable(next_fn, n_states)` in the lab explores the graph from reset over both
inputs and returns what can actually be entered; on the correct detector it returns all
five states, and on the deliberately broken machine in the last check it returns
`[0, 1, 2, 3]` out of six encoded states. Those two missing states are flops and decode
that no input sequence uses — and if a particle strike ever puts the machine in one, what
happens next is whatever the synthesiser's don't-care optimisation happened to build.

The sandbox *A controller that holds instead of advancing* shows the other shape a
transition takes. A stall is not an extra state: the state register reloads its own
value, the sequence pauses where it stands, and the row on screen occupies the same
stage for three columns instead of one. A self-loop is how a controller waits, and the
derivation *What a multi-cycle controller costs and what it buys* prices a graph made
mostly of them — an iterative divider takes $W + 2$ cycles per operation and runs at a
period of $t_{it} + t_{reg}$ instead of $W \cdot t_{it} + t_{reg}$.

## Where this stops holding

The suffix rule builds a machine for *one* pattern. It is the failure function of the
Knuth–Morris–Pratt string search, and it gives one state per prefix because there is one
pattern to be a prefix of. Watch for several at once and states stop corresponding
to prefixes of any one of them: the construction that keeps the count manageable is a
different one, and the state count is no longer the pattern length.

The merge of states 4 and 1 was licensed by two facts together: their next-state rows
agree, and the output no longer distinguishes them. Drop either and the merge is illegal.
This is the whole of state minimisation — two states may be merged when they agree on
output and their successors merge, applied until nothing more can be — and it is why the
Moore machine cannot have four states while the Mealy machine can.

Finally, a Mealy output feeding another machine's input puts combinational logic between
two state registers in different blocks, and if that machine's output comes back you have
a loop with no register in it, which no timing tool can close. Module 3 meets the same
constraint in different clothes: `ready` may not depend combinationally on `valid`.

## What you are about to build

The lab *A sequence detector, twice* asks for `moore_next`, `run_moore`, `mealy_next`,
`mealy_out`, `run_mealy` and `reachable`. Its checks are the numbers on this page:
`moore_next(4, 1) == 2`, the Moore vector `[0, 0, 0, 0, 1]` for `1101`, the two
overlapping matches at indices 4 and 7 of `1101101`, and `moore[1:] == mealy` over a
sixteen-bit stream with four occurrences in it. The blanks unit *The three blocks, and where the output
comes from* names the structure the two share: one clocked state register, one
combinational next-state function, one combinational output function, and one decision
about which the output hangs off.
''',
                },
            ],
            "quiz": {
                "title": "Where the output comes from, and what it costs",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A five-state Moore detector for `1101` numbers its states by how much of the pattern is in hand, and it is sitting in the state that means the last four bits were `1101`. The next bit is a `1`. Which state must it enter, and why?",
                        "opts": [
                            "The state meaning `11`, because the last two bits of what has been seen begin the pattern",
                            "The state meaning `1`, because the match is finished and one bit of it is left over",
                            "The state meaning nothing yet, because the four bits of the match have all been used up",
                            "The state meaning `1101` again, because the machine keeps matching while ones keep arriving",
                        ],
                        "a": 0,
                        "why": r"""
The state number is defined as the length of the longest suffix of everything seen so far
that is still a prefix of `1101`. Everything seen now ends in `11011`; its suffixes are
`11011`, `1011`, `011`, `11`, `1` and nothing, and the longest of those that begins
`1101` is `11`. So the machine goes to the state meaning `11`. Send `1101101` through a
machine that returns to the state meaning `1` instead and the second match, which shares
the middle `1`, is never found — across all 4096 twelve-bit streams that variant
under-reports on 180 of them and over-reports on none.
""",
                        "whys": [
                            r"Two bits of credit survive the completed match, because `11011` ends in `11`, and that is what the state number is defined to measure.",
                            r"This is the answer that feels like housekeeping — the match is over, so start again from the bit that has arrived. It throws away a bit that is still good: the `1` before this one is also part of `11`, and dropping it loses every overlapping second match.",
                            r"That would be right if occurrences could not overlap, and the specification here says they can. Consuming all four bits makes `1101101` report one match where there are two.",
                            r"The state that means `1101` is entered only by completing the pattern, and `11011` has not completed anything — the machine would report a match on the next cycle that no four consecutive bits support.",
                        ],
                    },
                    {
                        "q": "The Mealy version of the same detector has four states rather than five. What licenses dropping one, and what does it change in the next-state table?",
                        "opts": [
                            "Two Moore states have identical next-state rows, and moving the output onto the transition removes the only thing telling them apart",
                            "A Mealy machine is always one state smaller, since it reads the input directly and so needs no state in which to hold the completed match",
                            "The completed-match state is unreachable once the output is combinational, so it drops out of the reachability search on its own",
                            "The output function no longer reads the state, so states that produce the same output can be collapsed together whatever their transitions",
                        ],
                        "a": 0,
                        "why": r"""
The state meaning `1101` and the state meaning `1` both go to the state meaning nothing
on a `0` and to the state meaning `11` on a `1`. Identical futures — so the only thing
that separated them was the Moore output, which is a function of the state and had to
give them different values. Take the output off the state and the two may be merged,
which is state minimisation's rule in full: merge when the outputs agree and the
successors merge. This is also why the merged transition goes to the state meaning `1`
rather than copying the completed state's own outgoing edge to `11` — the transition is
consuming the fourth bit, so what has been seen is `1101`, not `11011`.
""",
                        "whys": [
                            r"Equal rows plus an output that no longer distinguishes them is exactly the condition under which two states may be merged.",
                            r"There is no such rule. Mealy machines are often smaller, and for this pattern the saving is one state, but it comes from a merge that has to be checked rather than from the style of the machine.",
                            r"It stays perfectly reachable — the machine still passes through that condition every time the pattern completes. What changes is that the condition no longer needs a state of its own to be visible.",
                            r"Equal outputs alone are not enough, or every state producing a `0` in this machine would collapse into one. The successors have to merge too, which is what makes the rule recursive.",
                        ],
                    },
                    {
                        "q": "A Mealy table is built by deleting the completed-match state and sending the transition that used to enter it wherever that state's own `1` edge went. On the stream `1101101` this machine's output is identical to the correct one. Where does it first go wrong?",
                        "opts": [
                            "On `110101`, where it reports a match in the very last cycle that no four consecutive bits support",
                            "On `11011`, where it reports the second match a cycle earlier than the correct machine reports it",
                            "On `1101`, where it misses the only match because the transition it takes has no output attached",
                            "On a long run of ones, where it cycles between two states and stops responding to the `0` that follows",
                        ],
                        "a": 0,
                        "why": r"""
The copied transition claims two bits of credit — the state meaning `11` — for a match
that has this moment consumed its own `1101`. What actually survives is one bit, so the machine
is running one bit ahead of the stream. Feed it `110101`: after the genuine match at
index 3 it sits in the state meaning `11`, the `0` takes it to the state meaning `110`,
and the final `1` fires an output. Six bits is the shortest stream that separates the two
tables. Across all 4096 twelve-bit streams the copied table over-reports on 443 and
under-reports on none, so any test that counts only the matches it planted will pass.
""",
                        "whys": [
                            r"One bit of credit survives a completed match, not two, and the extra bit lets a `01` finish a pattern that was never there.",
                            r"Both machines fire in the cycle the fourth bit arrives — the copied table gets the timing of every genuine match right, which is a large part of why it survives review. What it adds is matches, not shifts.",
                            r"The output is decided by `state == 3 and bit`, and that is untouched by this error, so the genuine match on `1101` is reported correctly by both tables.",
                            r"A run of ones parks both machines in the state meaning `11` and both leave it for the state meaning `110` on the next `0`. The transition out of a completed match is the only entry that differs.",
                        ],
                    },
                    {
                        "q": "With a 500 ps period, 42 ps of clock-to-output, 35 ps of setup, a 60 ps output function and 180 ps of logic in front of the machine's input, what does choosing a Mealy output cost the block downstream?",
                        "opts": [
                            "It leaves 183 ps rather than 363 ps, because the path now starts at the input's source flop rather than at the state register",
                            "It leaves 265 ps rather than 363 ps, because the output function's own 60 ps is charged twice, once for the state and once for the input",
                            "It costs nothing measurable, because both outputs leave a register and the 180 ps belongs to the previous stage's own budget",
                            "It leaves 138 ps rather than 363 ps, because the setup time of the consumer has to be paid on the launching side as well",
                        ],
                        "a": 0,
                        "why": r"""
A Moore output is a function of the state register, so its path is $t_{cq} + t_{out} =
102$ ps and the consumer gets $500 - 102 - 35 = 363$ ps. A Mealy output is a function of
the input as well, and the input arrived through 180 ps of someone else's cloud, so the
output is not valid until $42 + 180 + 60 = 282$ ps and the consumer gets 183 ps. The
cycle of latency a Mealy output saves is paid for out of the period, on the far side of
the interface where it is hardest to recover.
""",
                        "whys": [
                            r"$42 + 180 + 60 = 282$ ps against $42 + 60 = 102$ ps, and the consumer gets whatever is left after setup.",
                            r"The output function is evaluated once, not twice. Its 60 ps appears in both figures exactly once; what differs between them is the 180 ps of logic ahead of the input.",
                            r"This is the tempting one, and the word doing the damage is 'previous'. There is no register between the input's cloud and this machine's output — that is what makes the output Mealy — so the two delays are on one path and share one period.",
                            r"Setup is charged once, at the capturing flop, which is the 35 ps already subtracted. Charging it at both ends double-counts a delay that belongs to the consumer.",
                        ],
                    },
                    {
                        "q": "`reachable(next_fn, 6)` on a machine encoded for six states returns `[0, 1, 2, 3]`. What has it established?",
                        "opts": [
                            "That two encoded states can never be entered from reset, so their flops and decode do no work the design asked for",
                            "That the machine has a bug, since a correctly written state machine reaches every state its encoding allows for",
                            "That states 4 and 5 are safe, because the machine cannot enter them and therefore cannot behave incorrectly in them",
                            "That the encoding should be one-hot, because a binary encoding with unused codes cannot be made to recover from an upset",
                        ],
                        "a": 0,
                        "why": r"""
The search follows both input values from reset until nothing new appears, so what it
returns is what the state graph can actually enter. Two encoded states outside that set
are dead logic, and the interesting question is the second one: the synthesiser was free
to build anything at all for those codes, because you told it they cannot happen. If an
upset ever puts the machine in one, whether it finds its way back is whatever the
don't-care optimisation happened to produce. A binary encoding of five states has three
such codes and a one-hot encoding of five has twenty-seven.
""",
                        "whys": [
                            r"Unreachable states are decode and flops that no input sequence uses, and the codes they occupy are where a design's behaviour after an upset stops being specified.",
                            r"Plenty of correct machines have unreachable codes — any state count that is not a power of two leaves some — so the search reports a fact about the encoding rather than a verdict on the design.",
                            r"Backwards. The machine cannot enter them through its inputs, which is precisely why nothing was specified for them, and that is what makes them dangerous rather than safe.",
                            r"One-hot has far more unused codes than binary, not fewer: five states cost twenty-seven illegal codes one-hot against three in binary. Recovery comes from writing the transition out of them, whichever encoding is used.",
                        ],
                    },
                    {
                        "q": "A controller stalls for two cycles. How does that appear in the state graph, and what does it cost in states?",
                        "opts": [
                            "The state register reloads its own value, so the graph gains an edge from that state back to itself and no new state at all",
                            "The controller enters a dedicated wait state and returns, so the graph gains one state and two edges for each stall it can take",
                            "The clock to the state register is gated off for two cycles, so the graph is untouched and the stall is invisible in it",
                            "Each stalled cycle needs its own state, so a two-cycle stall costs two states and the graph grows with the longest stall",
                        ],
                        "a": 0,
                        "why": r"""
Holding is `next_state = state`, which is a self-loop. Nothing is added to the state set,
and the sequence resumes from exactly where it paused. The sandbox for this module shows
the shape: a stalled row occupies the same stage for three columns instead of one, and
what changed was the hold condition rather than the sequence. A dedicated wait state is a
different machine — sometimes the right one, when what happens during the wait genuinely
differs — and it costs states and the transitions in and out of them.
""",
                        "whys": [
                            r"A self-loop is how a synchronous controller waits, and it is free in states because the machine is already in the state it wants to stay in.",
                            r"That is a real design and occasionally the right one, but it is a choice rather than what stalling means. It also loses the property that the sequence resumes unchanged, because the wait state has to remember where to go back to.",
                            r"Gating the clock is a way to stall and a poor first choice — the gate lands on the clock tree with its own skew, and it hides the stall from anything reading the state. The graph is not untouched either, since something has to decide when to gate.",
                            r"That would make the state count depend on the longest stall the design can take, which for a memory wait is unbounded. The whole value of a self-loop is that it holds for as long as the condition lasts.",
                        ],
                    },
                ],
            },
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
            "blanks": {
                "title": "The three blocks, and where the output comes from",
                "minutes": 8,
                "caption": "fsm.py — the canonical form, and the one real choice in it",
                "lang": "text",
                "brief": r"""
Every state machine worth writing has the same three pieces. The only genuine design
decision is where the output is taken from, and it has consequences for timing that show
up two blocks downstream.
""",
                "listing": """The canonical form:

  1.  a ___ , clocked

  2.  a combinational ___ ,
      which reads the state and the inputs

  3.  a combinational ___

Moore outputs depend on ___ ,
so they are stable for the whole cycle and glitch-free.

Mealy outputs depend additionally on ___ ,
so they appear a cycle earlier and carry the input's glitches with them.
""",
                "blanks": [
                    {
                        "prompt": "The only clocked piece.",
                        "hole": "?",
                        "opts": ["state register", "output register", "counter", "memory array"],
                        "a": 0,
                        "why": "One register holding the current state, and it is the only sequential element in the canonical form. Keeping it in a block of its own — nothing but the reset and `state <= next_state` — is what makes the machine easy to read and impossible to get subtly wrong.",
                        "whys": [
                            "One register holding the current state, and it is the only sequential element in the canonical form. Keeping it in a block of its own — nothing but the reset and `state <= next_state` — is what makes the machine easy to read and impossible to get subtly wrong.",
                            "Registering the output is a legitimate variation, and it is not the state-holding element the machine is built around.",
                            "A counter is one particular state machine, not the general form.",
                            "A memory array is storage the machine may address, not the machine's own state.",
                        ],
                    },
                    {
                        "prompt": "What decides where to go next?",
                        "hole": "?",
                        "opts": ["next-state function", "output function", "reset function", "clock divider"],
                        "a": 0,
                        "why": "Purely combinational, reading the current state and the inputs. It needs a default assignment or a complete case: an incompletely specified next state infers a latch, which is the single most common accidental sequential element in RTL.",
                        "whys": [
                            "Purely combinational, reading the current state and the inputs. It needs a default assignment or a complete case: an incompletely specified next state infers a latch, which is the single most common accidental sequential element in RTL.",
                            "That is the third block, and mixing the two is what makes a state machine hard to follow.",
                            "Reset is a property of the register block, not a separate function.",
                            "Clock division is not part of a state machine's structure.",
                        ],
                    },
                    {
                        "prompt": "And the third block.",
                        "hole": "?",
                        "opts": ["output function", "next-state function", "state register", "decoder"],
                        "a": 0,
                        "why": "Separating it from the next-state logic is what lets you change Moore to Mealy by editing one block. Fusing them is legal and tempting and makes every later change touch both concerns at once.",
                        "whys": [
                            "Separating it from the next-state logic is what lets you change Moore to Mealy by editing one block. Fusing them is legal and tempting and makes every later change touch both concerns at once.",
                            "Already the second block.",
                            "Already the first block, and it is the clocked one.",
                            "A decoder is one possible implementation of the output function, not the role itself.",
                        ],
                    },
                    {
                        "prompt": "Moore outputs are a function of what?",
                        "hole": "?",
                        "opts": ["the state alone", "the inputs alone", "the state and the inputs", "the previous output"],
                        "a": 0,
                        "why": "Which is why they are stable: the state only changes at an edge, so a Moore output is clean for the whole cycle and safe to send anywhere, including off-chip or into another clock domain's synchroniser.",
                        "whys": [
                            "Which is why they are stable: the state only changes at an edge, so a Moore output is clean for the whole cycle and safe to send anywhere, including off-chip or into another clock domain's synchroniser.",
                            "An output depending only on the inputs is not a state machine's output at all.",
                            "That is Mealy, the next blank.",
                            "Feeding the output back to itself is a latch, not a state machine output.",
                        ],
                    },
                    {
                        "prompt": "And Mealy adds what?",
                        "hole": "?",
                        "opts": [
                            "the current input",
                            "the next state",
                            "the clock",
                            "the previous state",
                        ],
                        "a": 0,
                        "why": "Which buys a cycle of latency — the output responds in the same cycle the input arrives rather than after the next edge — and costs stability, because any glitch on the input reaches the output directly. It also usually needs fewer states. The right choice depends on what is downstream: a Mealy output into another block's combinational logic is where long paths and awkward timing come from.",
                        "whys": [
                            "Which buys a cycle of latency — the output responds in the same cycle the input arrives rather than after the next edge — and costs stability, because any glitch on the input reaches the output directly. It also usually needs fewer states. The right choice depends on what is downstream: a Mealy output into another block's combinational logic is where long paths and awkward timing come from.",
                            "The next state is an internal signal of the machine; using it as an output source is a third variation (a registered Mealy) rather than the definition.",
                            "The clock gates when the state changes, not what the output is a function of.",
                            "The machine keeps only the current state; the previous one is not available unless you register it deliberately.",
                        ],
                    },
                ],
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
            "read": [
                {
                    "title": "Six items, seven cycles and twelve",
                    "minutes": 17,
                    "body": r'''
A source with six items to hand over. A sink that is ready in every cycle and never
once stalls. Between them, a buffer. Here is how long the six items take.

```python
def step_slice(q, in_valid, in_data, out_ready, depth):
    """One cycle. Every returned signal is decided from the registered queue."""
    in_ready = 1 if len(q) < depth else 0
    out_valid = 1 if q else 0
    out_data = q[0] if q else None
    nxt = list(q)
    if out_valid and out_ready:
        nxt.pop(0)
    if in_valid and in_ready:
        nxt.append(in_data)
    return nxt, in_ready, out_valid, out_data


def run_link(data, depth):
    q, sent, got, cycle = [], 0, [], 0
    while cycle < 40 * (len(data) + 4):
        offer = 1 if sent < len(data) else 0
        item = data[sent] if sent < len(data) else None
        q, in_ready, out_valid, out_data = step_slice(q, offer, item, 1, depth)
        if offer and in_ready:
            sent += 1
        if out_valid:
            got.append(out_data)
        cycle += 1
        if sent == len(data) and not q:
            break
    return got, cycle


for depth in (1, 2):
    got, cycles = run_link(list(range(6)), depth)
    print("depth %d: %2d cycles, delivered %s" % (depth, cycles, got))
```

```text
depth 1: 12 cycles, delivered [0, 1, 2, 3, 4, 5]
depth 2:  7 cycles, delivered [0, 1, 2, 3, 4, 5]
```

Nothing stalled. Every item arrived, exactly once and in order, under both buffers. One
took a cycle per item and the other took two, and the difference is one storage element.

## Two wires and one edge

A producer has a beat of data; a consumer has room for it; neither can see inside the
other and neither may go first. A producer that hands over before the consumer has room
loses the beat, and a consumer that commits before the producer has data wastes the slot.
So each side states a condition and the transfer happens where both hold. `valid` is the
producer saying *I have a beat and it is on the data wires now*; `ready` is the consumer
saying *I can take one this cycle*; a rising edge with both high is the transfer, and no
acknowledgement follows it.

The asymmetry that makes this composable is a rule about dependence. `valid` may be
computed from `ready` — a producer is allowed to say "I have data whenever you will take
it". `ready` may not be computed from `valid`: put that in a block whose producer computes
`valid` from `ready` and the loop closes through no register at all, where no simulator
converges and no timing tool can close.

## Where the second entry goes

```python
def timeline(depth, n=6, cycles=12):
    q, sent, held, rdy, acc = [], 0, [], [], []
    for c in range(cycles):
        in_ready = 1 if len(q) < depth else 0
        held.append(len(q))
        rdy.append(in_ready)
        nxt = list(q)
        if q:
            nxt.pop(0)                      # the sink is ready in every cycle
        take = 1 if (sent < n and in_ready) else 0
        acc.append(take)
        if take:
            nxt.append(sent)
            sent += 1
        q = nxt
    return held, rdy, acc


print("cycle            " + "".join("%3d" % c for c in range(12)))
for depth in (1, 2):
    held, rdy, acc = timeline(depth)
    print("depth %d  held    " % depth + "".join("%3d" % v for v in held))
    print("         in_ready" + "".join("%3d" % v for v in rdy))
    print("         accepted" + "".join("%3d" % v for v in acc))
```

```text
cycle              0  1  2  3  4  5  6  7  8  9 10 11
depth 1  held      0  1  0  1  0  1  0  1  0  1  0  1
         in_ready  1  0  1  0  1  0  1  0  1  0  1  0
         accepted  1  0  1  0  1  0  1  0  1  0  1  0
depth 2  held      0  1  1  1  1  1  1  0  0  0  0  0
         in_ready  1  1  1  1  1  1  1  1  1  1  1  1
         accepted  1  1  1  1  1  1  0  0  0  0  0  0
```

Read the `in_ready` row of the one-entry slice: 1, 0, 1, 0 all the way across. In every
odd cycle the slice is holding an item, so it is full, so `in_ready` is low and the source
may not offer — low even though that is the cycle in which the item leaves, because
`in_ready` was decided from the registered queue at the start of it. The slot is about to
be free and the producer is not allowed to know. One item every two cycles: six items,
twelve cycles.

The two-entry slice never fills. Its occupancy sits at one, the second entry is never
touched, and `in_ready` stays high throughout. Seven cycles for six items — one per item,
plus one of latency for the first.

So the second entry is not capacity in any useful sense; the steady state above does not
use it. It is there so that the cycle in which back-pressure arrives has somewhere to put
the beat that is already in flight. The producer decided to offer on the previous edge,
from information one cycle old; if the sink stalls now, that beat has to land somewhere,
and the empty second entry is where. The shape has a name, a skid buffer, and the skid is
exactly one beat because the stale information is exactly one cycle stale.

## The mistake: deciding `ready` after the pop

There is one obvious repair for the one-entry slice and it is a single line. The slice
knows whether the head is leaving this cycle. Apply the departure first, then ask whether
there is room. The slot is genuinely free, so why refuse?

```python
def run_link(data, depth, sink_pattern=(1,), pop_first=False):
    q, sent, got, cycle = [], 0, [], 0
    while cycle < 40 * (len(data) + 4):
        offer = 1 if sent < len(data) else 0
        rdy = sink_pattern[cycle % len(sink_pattern)]
        nxt = list(q)
        if q and rdy:
            got.append(q[0])
            nxt.pop(0)
        # the one line this section is about
        in_ready = 1 if len(nxt if pop_first else q) < depth else 0
        if offer and in_ready:
            nxt.append(data[sent])
            sent += 1
        q = nxt
        cycle += 1
        if sent == len(data) and not q:
            break
    return got, cycle


twelve = list(range(12))
for pop_first in (False, True):
    for depth in (1, 2):
        got, cycles = run_link(twelve, depth, pop_first=pop_first)
        print("in_ready %s, depth %d: %2d cycles, in order: %s"
              % ("after the pop " if pop_first else "from the queue",
                 depth, cycles, got == twelve))

print()
print("  sink accepts     depth 1   2   3   4")
for name, pat in (("every cycle", (1,)), ("2 cycles in 3", (1, 1, 0)),
                  ("1 cycle in 2", (1, 0)), ("1 cycle in 3", (1, 0, 0))):
    row = [run_link(twelve, d, pat)[1] for d in (1, 2, 3, 4)]
    print("  %-15s %5d %3d %3d %3d" % (name, *row))

print()
T, t_cq, t_setup, t_skew, t_slice = 500, 42, 35, 15, 40
budget = T + t_skew - t_cq - t_setup
print("  logic budget at T = %d ps: %d ps" % (T, budget))
for n in (10, 11):
    print("  %2d slices at %d ps each: %3d ps, slack %+4d ps"
          % (n, t_slice, n * t_slice, budget - n * t_slice))
```

```text
in_ready from the queue, depth 1: 24 cycles, in order: True
in_ready from the queue, depth 2: 13 cycles, in order: True
in_ready after the pop , depth 1: 13 cycles, in order: True
in_ready after the pop , depth 2: 13 cycles, in order: True

  sink accepts     depth 1   2   3   4
  every cycle        24  13  13  13
  2 cycles in 3      34  19  19  19
  1 cycle in 2       25  25  25  25
  1 cycle in 3       37  37  37  37

  logic budget at T = 500 ps: 438 ps
  10 slices at 40 ps each: 400 ps, slack  +38 ps
  11 slices at 40 ps each: 440 ps, slack   -2 ps
```

The change nearly doubles the throughput of the one-entry slice — twelve items in 13
cycles where the honest version needs 24 — for one storage element rather than two. Every
item is delivered once, in order, at both depths. A protocol checker watching the
output interface sees nothing wrong: `valid` is never withdrawn, the data never changes
under a stalled sink, the ordering is perfect. No functional test fails.

What changed is not visible in cycles at all. `in_ready` is computed from `nxt`, and `nxt`
was computed from `out_ready`, so `in_ready` is now a combinational function of the sink's
`ready` wire. Chain two of these and the source's `ready` depends on the sink's through
both of them; chain ten, and it depends on it through ten. The last three lines are module
1's budget applied to that path: 438 ps of logic inside a 500 ps period, and slices
contributing 40 ps of ready logic each fit ten deep with 38 ps to spare and eleven deep
with 2 ps short. Breaking that dependence is the entire reason a register slice is put
into a long link. A slice whose `ready` runs straight through it has been built to solve a
problem it does not solve, and the failure surfaces at the end of place-and-route rather
than in simulation.

It is also half of a combinational loop. On its own the path only ripples backwards, since
nothing here computes `valid` from `ready`; but the protocol permits a producer to do
precisely that, and one of those connected to a consumer whose `ready` depends on `valid`
closes a ring with no register in it. Which is why the lab *A slice that does not drop
data* states the rule as a property of the block rather than of the link and checks it
directly: `step_slice` is called twice with the same queue and different `out_ready`, and
the two `in_ready` values have to agree.

## What the buffer can and cannot buy

The middle table above gives the sink a stall pattern and varies the depth. Every row past
depth 2 is flat, and the bottom two rows are flat across the whole width. A sink that
accepts one beat in three needs 36 cycles to take twelve of them however deep the buffer
is; the measured 37 is those 36 plus the cycle the first item spends in the slice. The
rate of a link is the lower of its two rates, and no amount of storage raises it — which
is what the lab's own check means when it reports 37 cycles for a stalling sink and adds
that the depth does not change it.

The one row where depth matters is the first, and the reason is the slice itself: at depth
1 the *slice* is the slower side, at one beat in two. The third row says the same thing
from the other direction — a sink accepting one cycle in two is exactly as slow as a
depth-1 slice, so the slice's limit is invisible behind it and every depth gives 25.

Two entries is therefore the number rather than a number. One is too few, because the
slice becomes the bottleneck. Three and beyond raise no rate and buy only elasticity —
somewhere for a burst to sit while the sink catches up — which matters when the two sides
stall in patterns rather than at steady rates. The derivation *Pipeline speedup, and the
ceiling it runs into* prices the difference from the other end: cycles per item is
$1 + p \cdot b$ once the pipeline is long, and a stall that propagates through $k$ stages
contributes to $p$ at every one of them, where a stall a buffer absorbs contributes at
one. The sandbox *Bubbles are the absence of a path* is the picture of the first case — a
row waits, and every row behind it waits with it.

## The rule that keeps a beat from being invented

The last piece is a promise the producer makes: once `valid` is asserted it stays
asserted, and the data does not change, until a transfer takes the beat away.

```text
   cycle       0     1     2     3
   valid       1     1     1     0
   ready       0     0     1     -        legal: held until it was taken
   data        7     7     7     -

   valid       1     0                    illegal: withdrawn while stalled
   ready       0     0

   valid       1     1                    illegal: the sink accepted 8,
   ready       0     1                    having been shown 7
   data        7     8
```

There is no wire for "I am about to take this". `ready` going high in a cycle is the
consumer's decision for that cycle, taken from state that was fixed at the previous edge,
and the consumer is entitled to begin acting on the offered data before the edge that
completes the transfer — addressing a memory with it, starting an operation on it. If the
producer may change the data inside the cycle, what transfers is settled by a race between
two clouds instead of by two registered decisions, which is the analogue uncertainty the
discipline of module 1 exists to remove. The third case above is the sharp one: the sink
accepts a value that was never offered for a whole cycle, and nothing downstream can tell.

## Where this stops holding

Ready and valid make one channel safe and say nothing about several at once, which is
where elastic designs deadlock. Split a stream into two channels, do different work on
each, and join them in order with finite buffers: a burst down one branch fills its
buffer, back-pressures its source, and the source stops feeding the other branch, which
the join is waiting on. Every block obeyed the protocol and the system stopped. Buffer
sizing at a fork is a global argument, not a local one.

The protocol also fixes no latency. A legal consumer may hold `ready` low forever, so
correctness here means that no beat is lost or duplicated, and never means that a beat
arrives. Closing that gap takes two measurements rather than one, which is why the
capstone asks for a protocol monitor and a cycle count side by side.

It also assumes the two ends share a clock and sit close enough that `ready` gets back
inside a period. Across a long link the round trip is several cycles, a stall arrives too
late to prevent an overrun, and flow control moves to a credit scheme: the receiver issues
buffer credits in advance and the sender spends them.

## What you are about to build

The lab *A slice that does not drop data* is `step_slice`, `run_link` and
`handshake_legal`, the listings on this page with the ends filled in. Its checks
are the numbers above: seven cycles for six items at depth 2, twelve at depth 1, 37 for
twelve items into a sink accepting one beat in three, and the two calls to `step_slice`
with different `out_ready` that have to return the same `in_ready`. The capstone reuses
all of it, with two such stages back to back and a monitor that reports which cycle a
violation happened in rather than whether one did.
''',
                },
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
            "quiz": {
                "title": "Two wires and one rule",
                "minutes": 7,
                "questions": [
                    {
                        "q": "When does a transfer happen on a ready/valid interface?",
                        "opts": [
                            "On a clock edge where both are high",
                            "When valid rises",
                            "When ready rises",
                            "One cycle after both are high",
                        ],
                        "a": 0,
                        "why": r"""
The coincidence at the edge is the transfer — one beat of data moves and both sides know
it, with no acknowledgement to follow. That is the whole protocol, and its economy is why
it is everywhere: two wires, one rule, and blocks written years apart connect without
negotiation.
""",
                    },
                    {
                        "q": "Once `valid` is asserted, what may the producer do?",
                        "opts": [
                            "Hold it, and the data, until a transfer occurs",
                            "Withdraw it if it changes its mind",
                            "Change the data while waiting",
                            "Withdraw it after one cycle",
                        ],
                        "a": 0,
                        "why": r"""
The stability rule. Without it a consumer could see `valid` and commit to accepting in
the same cycle the producer withdraws, and a beat is lost with no way for either side to
detect it. This is the rule that makes the interface *composable* — a register slice can
be dropped into any link precisely because both sides obey it, and the rule is why such a
slice needs two storage elements rather than one.
""",
                    },
                    {
                        "q": "Why must `ready` not depend combinationally on `valid`?",
                        "opts": [
                            "Two connected blocks would form a combinational loop",
                            "It would violate setup time",
                            "It would make the interface Mealy",
                            "It would need an extra wire",
                        ],
                        "a": 0,
                        "why": r"""
If A's `valid` feeds B's `ready` and B's `ready` feeds A's `valid`, the loop closes
through no register at all and the design will not converge in simulation and cannot be
timed in synthesis. The asymmetry is deliberate: `valid` may depend on `ready`, but not
the other way round. Getting this backwards produces a block that works perfectly in
isolation and hangs the moment two of them are connected.
""",
                    },
                    {
                        "q": "May `ready` be asserted before `valid` arrives?",
                        "opts": [
                            "Yes — a consumer with room may sit ready indefinitely",
                            "No, it must wait for valid",
                            "Only for one cycle",
                            "Only if the producer permits it",
                        ],
                        "a": 0,
                        "why": r"""
Yes, and it is the common case: a consumer with space asserts `ready` and leaves it
there, so transfers happen the instant data appears with no handshake latency at all.
That asymmetry is precisely what the previous question's rule permits, and it is what
makes the protocol full-throughput rather than costing a cycle per beat.
""",
                    },
                    {
                        "q": "What is back-pressure?",
                        "opts": [
                            "The consumer deasserting `ready` to stall the producer",
                            "The producer stalling because it has no data",
                            "A buffer overflowing",
                            "An error signal from the consumer",
                        ],
                        "a": 0,
                        "why": r"""
Flow control travelling backwards, and it propagates: a full consumer stalls its
producer, which fills and stalls *its* producer, all the way to the source. That is what
makes a pipeline of such blocks safe by construction — no element can ever be overrun,
so no data is lost and no overflow check is needed anywhere. It is the property that
makes the protocol worth its two wires.
""",
                    },
                ],
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
            "read": [
                {
                    "title": "Cycle 5, and the beat that goes missing at cycle 8",
                    "minutes": 17,
                    "body": r'''
A four-deep FIFO written by another team, and the specification it was meant to
implement, run side by side on ten cycles of stimulus.

```python
class Fifo:
    """The design as handed over. One line of it does not match the specification."""

    def __init__(self, depth):
        self.depth, self.q = depth, []

    def step(self, push, data, pop):
        full = len(self.q) >= self.depth
        empty = len(self.q) == 0
        popped = None
        if pop and self.q:
            popped = self.q.pop(0)
        if push and not full:                    # tests the flag sampled above
            self.q.append(data)
        return popped, full, empty


class RefFifo(Fifo):
    """The specification: room is judged after this cycle's pop is accounted for."""

    def step(self, push, data, pop):
        full = len(self.q) >= self.depth
        empty = len(self.q) == 0
        popped = None
        if pop and self.q:
            popped = self.q.pop(0)
        if push and len(self.q) < self.depth:
            self.q.append(data)
        return popped, full, empty


def trace(model, ops):
    return [tuple(model.step(*op)) for op in ops]


ops = [(1, 10, 0), (1, 11, 0), (1, 12, 0), (1, 13, 0), (1, 99, 1)] + [(0, 0, 1)] * 5
ref, dut = trace(RefFifo(4), ops), trace(Fifo(4), ops)
print("cycle  op              reference             design")
for c, (op, r, d) in enumerate(zip(ops, ref, dut)):
    label = "push %-2d pop %d" % (op[1], op[2]) if op[0] else "        pop %d" % op[2]
    mark = "  <-- first divergence" if r != d and ref[:c] == dut[:c] else ""
    print(("%4d   %-14s  %-21s %-21s%s" % (c, label, r, d, mark)).rstrip())
```

```text
cycle  op              reference             design
   0   push 10 pop 0   (None, False, True)   (None, False, True)
   1   push 11 pop 0   (None, False, False)  (None, False, False)
   2   push 12 pop 0   (None, False, False)  (None, False, False)
   3   push 13 pop 0   (None, False, False)  (None, False, False)
   4   push 99 pop 1   (10, True, False)     (10, True, False)
   5           pop 1   (11, True, False)     (11, False, False)     <-- first divergence
   6           pop 1   (12, False, False)    (12, False, False)
   7           pop 1   (13, False, False)    (13, False, False)
   8           pop 1   (99, False, False)    (None, False, True)
   9           pop 1   (None, False, True)   (None, False, True)
```

Three cycles are worth naming, and they are all different cycles.

Cycle 4 is where the bug happens. The FIFO holds four items, so `full` is sampled true;
the pop takes 10 out, leaving three; the push of 99 then tests the flag that was sampled
before the pop and refuses. The design drops the item. Both models return
`(10, True, False)` and there is nothing on the interface to see.

Cycle 5 is where the divergence first shows: the reference holds four items and reports
`full`, the design holds three and does not. That is an occupancy flag, not data.

Cycle 8 is where the data goes missing — the reference pops 99 and the design pops
nothing. A bench that compares only the popped stream sees the fault four cycles after
it happened, and a bench that stopped at cycle 6 saw nothing at all. This is why
`directed_ops` in the lab fills the FIFO, collides a push with a pop, and then *drains*:
the drain is not tidying up, it is the part of the sequence that makes the missing item
observable.

## Two derivations of one intent

A test that prints waveforms for a human to read is a test that runs once. To run it ten
thousand times unattended, something in the bench has to decide pass or fail, and that
something is a second model of the same specification with a comparison between them.

The value is in the word *second*. Two independent derivations of the same intent agree
wherever both are right and disagree wherever one is wrong, so the comparison localises
error without knowing which side holds it. That is the whole mechanism, and it has one
precondition: independence. The moment the reference is derived from the design, both
sides are the same derivation and the comparison can only report that a thing equals
itself.

## The mistake: reading the design instead of the specification

The design is right there. It is unambiguous, it is already in the language you are
working in, and it runs. The specification is a paragraph of English that has to be
interpreted. Writing the reference by working through the design is faster, produces a
model that agrees on the first try, and feels like understanding the block.

```python
import random


class Fifo:
    def __init__(self, depth):
        self.depth, self.q = depth, []

    def step(self, push, data, pop):
        full = len(self.q) >= self.depth
        empty = len(self.q) == 0
        popped = None
        if pop and self.q:
            popped = self.q.pop(0)
        if push and not full:
            self.q.append(data)
        return popped, full, empty


class RefFifo(Fifo):
    def step(self, push, data, pop):
        full = len(self.q) >= self.depth
        empty = len(self.q) == 0
        popped = None
        if pop and self.q:
            popped = self.q.pop(0)
        if push and len(self.q) < self.depth:
            self.q.append(data)
        return popped, full, empty


class CopiedRef(Fifo):
    """A reference written by reading the design instead of the specification."""


def stimulus(seed, cycles, p_push=0.5, p_pop=0.5):
    rng = random.Random(seed)
    ops = []
    for _ in range(cycles):
        push = 1 if rng.random() < p_push else 0
        data = rng.getrandbits(8)
        pop = 1 if rng.random() < p_pop else 0
        ops.append((push, data, pop))
    return ops


def bench(reference, ops):
    """Returns (first divergent cycle, total divergent cycles, corner reached)."""
    ref, dut, first, total, corner = reference(4), Fifo(4), None, 0, 0
    for c, (push, data, pop) in enumerate(ops):
        if push and pop and len(ref.q) >= 4:
            corner += 1
        if ref.step(push, data, pop) != dut.step(push, data, pop):
            total += 1
            if first is None:
                first = c
    return first, total, corner


print("reference from the specification, 200 cycles per seed")
print("  first divergence:", [bench(RefFifo, stimulus(s, 200))[0] for s in range(8)])
print("  cycles differing:", [bench(RefFifo, stimulus(s, 200))[1] for s in range(8)])
print("reference copied from the design")
print("  first divergence:", [bench(CopiedRef, stimulus(s, 200))[0] for s in range(8)])
print()
for name, seed, n, pp, pq in (("balanced   ", 0, 200, 0.5, 0.5),
                              ("drain-heavy", 11, 20000, 0.25, 0.9)):
    first, _, corner = bench(RefFifo, stimulus(seed, n, pp, pq))
    print("%s %6d cycles, push %.2f pop %.2f: corner reached %2d times, "
          "first divergence %s" % (name, n, pp, pq, corner, first))
```

```text
reference from the specification, 200 cycles per seed
  first divergence: [18, 115, 19, 29, 30, 45, 53, 6]
  cycles differing: [19, 12, 41, 35, 66, 22, 45, 81]
reference copied from the design
  first divergence: [None, None, None, None, None, None, None, None]

balanced       200 cycles, push 0.50 pop 0.50: corner reached  3 times, first divergence 18
drain-heavy  20000 cycles, push 0.25 pop 0.90: corner reached  0 times, first divergence None
```

Eight seeds, two hundred cycles each, sixteen hundred cycles of stimulus through a design
that drops data — and the copied reference reports `None` on every one of them. Written
out honestly, that reference is `class CopiedRef(Fifo)` with nothing in the body, which is
what the listing says, and the bench comparing it with the design is asking whether the
design equals itself. It never fails, it never will, and every green run adds confidence
that is not evidence of anything.

The reference written from the specification finds the fault under all eight seeds, the
slowest at cycle 115 and the quickest at cycle 6.

## Report the first divergence, not the divergences

The second row is the argument for stopping at the first one. Seed 7 diverges at cycle 6
and then differs on 81 of its 200 cycles; seed 4 diverges at cycle 30 and differs on 66.
None of those later cycles is a second bug. Once the design has dropped an item its
occupancy is permanently one behind the reference's, so every subsequent flag and every
subsequent pop is compared against a machine in a different state — one cause, eighty
consequences. A scoreboard that prints them all has buried the cycle that matters under
the ones that follow from it, which is why `compare` in the lab returns an index rather
than a list.

## What directed stimulus is for, and what random stimulus is for

The directed sequence at the top of this page reaches the disagreement in six cycles, and
it does so because someone reasoned about where the design could go wrong before writing
it. That reasoning is the expensive part and the sequence is trivial: fill, collide,
drain. Directed tests prove the things you knew to ask about.

Random stimulus asks about things nobody wrote down, and the derivation *How long a random
test takes to find one corner* prices it. For a single bad pair of $W$-bit operands the
probability per vector is $p = 2^{-2W}$ and the expected number of draws is $1/p$: 65,536
at $W = 8$, which is a second of simulation, and $1.8 \times 10^{19}$ at $W = 32$, which is
never. Randomisation does not search a space, it samples one.

Which is exactly why it works on this FIFO. The corner is not one vector out of $2^{2W}$;
it is a *state* — full, with a push and a pop arriving together — and an enormous number
of different sequences reach it. The balanced run above hits it three times in 200 cycles.
What decides whether random stimulus finds a bug is the measure of the set of stimuli that
reach it, and that has almost nothing to do with the size of the input space.

## Coverage is a different question from pass

The last two lines are the same design, the same reference and the same generator, with the
push and pop probabilities moved from 0.50 and 0.50 to 0.25 and 0.90. Twenty thousand
cycles, a hundred times as many as the balanced run, and the FIFO never once meets a push
and a pop while full. Zero divergences. The bench passes.

Nothing about that result is a fact about the design. It is a fact about the stimulus, and
no amount of running it longer changes it, because the distribution keeps the queue drained
and the corner lives at the other end. The measurement that separates the two runs is not
pass or fail, which is identical in kind for both, but the `corner reached` column: three
times against zero. That is coverage, and it is the reason a green regression is not by
itself evidence. The sandbox *Where a model stops responding to its inputs* is the same
lesson on this module's own toy — a slider whose upper half changes neither the drawing nor
the cycle count is dead stimulus, and a random test sweeping it would report a full pass
having exercised nothing.

Seeding is what makes any of this repeatable. The listings above name a seed, so the eight
runs can be replayed exactly and the failing one bisected; a bench whose stimulus depends on
the wall clock produces failures nobody can reproduce. The lab's `random_ops` draws from
NumPy's generator rather than the standard library's, so its cycle indices differ from the
ones printed here — `find_bug(4, 200, range(8))` reports `(0, 92)` — and the check that
matters is the discipline rather than the number: the same seed gives the same stimulus, a
different seed gives different stimulus, and both are asserted.

## Where this stops holding

Agreement with a reference is agreement, not correctness. If the specification is wrong,
two independent derivations of it agree and both are wrong, and no amount of stimulus will
say so. The clause at issue here — that a push arriving with a pop at a full FIFO must
succeed — is a design decision somebody made, and a FIFO that refused it would be a
perfectly reasonable block whose reference model is the one called `Fifo` above. The bench
can only tell you which document the design implements.

Coverage measures what the stimulus reached, not what the bench checked. A corner entered
ten thousand times with no comparison on the signal it corrupts is a covered corner and an
unverified one, and a coverage report cannot tell those apart.

And this entire module compares what a design computes, cycle by cycle, against what it
should compute. It says nothing about whether the design meets the period from module 1,
nothing about what happens on a clock crossing, nothing about power. A design can pass
every bench here and fail in silicon for a reason no simulation of this kind can represent.

## What you are about to build

The lab *Find the bug in someone else's FIFO* asks for `RefFifo` written from the docstring
in `dut.py` and not from the code below it, `trace`, `compare`, `first_mismatch`,
`directed_ops`, `random_ops` and `find_bug`. Its checks are the numbers on this page: a
calm stream that keeps the FIFO nearly empty must report no mismatch, the directed sequence
must first differ at cycle 5, a trace compared with itself must return `None`, and one that
stops a cycle early must be a mismatch rather than a pass. The blanks unit *A bench that
checks itself* states the four decisions in four lines — where the reference comes from,
what a design-derived model agrees with, what the scoreboard reports, and which corners
each kind of stimulus reaches.
''',
                },
            ],
            "quiz": {
                "title": "What a green bench has and has not proved",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The FIFO drops an item at cycle 4, the occupancy flags first disagree at cycle 5, and the popped data first disagrees at cycle 8. What does that spread demand of a directed test sequence?",
                        "opts": [
                            "That it drain after the collision, since the lost item is only observable once everything ahead of it has left",
                            "That it compare the internal queue as well as the interface, because the interface hides the drop entirely",
                            "That it stop at the first divergence, so the flag mismatch is reported before the data mismatch confuses it",
                            "That it repeat the collision several times, because one dropped item is within the tolerance of a flag comparison",
                        ],
                        "a": 0,
                        "why": r"""
Nothing is visible at cycle 4 at all: both models return the same triple, because the item
that was refused never appears on any output. The occupancy flag disagrees a cycle later
and the data four cycles after that, when the pops have worked through the three items
that were ahead of the one that never arrived. A sequence that fills, collides and stops
tests the cycle the bug happens in and observes none of it. The drain is what makes the
loss reach an output, which is why the lab's `directed_ops` ends with `depth + 1` pops.
""",
                        "whys": [
                            r"The dropped item sits behind three others, so the pops that empty them are the stimulus that makes its absence reach an output.",
                            r"Reaching into the queue would find it sooner, and it is the thing a bench should avoid: a checker bound to the design's internals has to be rewritten whenever the implementation changes, and cannot be run against a different implementation of the same specification at all.",
                            r"Stopping at the first divergence is the right policy for a scoreboard and it does nothing here, because without the drain there is no second divergence to be confused by — the run ends while the two models still agree.",
                            r"One dropped item is a definite mismatch, not noise; there is no tolerance to be inside. Repeating the collision makes the eventual failure larger without making it any earlier.",
                        ],
                    },
                    {
                        "q": "A reference model written by working through the design's source reports no mismatch across eight seeds of two hundred cycles each, on a design that demonstrably drops data. What has those 1600 cycles established?",
                        "opts": [
                            "That the design agrees with itself, since the two models are one derivation and the comparison has no second opinion in it",
                            "That the random stimulus never reached the corner, so the run needs more seeds or a longer schedule before it means anything",
                            "That the design is correct on everything the stimulus covered, and the fault lies outside the space those eight seeds explored",
                            "That the reference is too abstract to see the fault, and it needs the cycle-level detail the design's own source carries",
                        ],
                        "a": 0,
                        "why": r"""
Written out, that reference is a subclass of the design with an empty body. The comparison
asks whether the design equals itself, so it cannot fail — not on these seeds, not on
sixteen million cycles, not ever. The stimulus is not the problem: the same seeds and the
same cycles find the fault immediately once the reference is written from the
specification, at cycle 6 for the quickest seed and cycle 115 for the slowest. Independence
is the property being bought, and a model read off the design has none of it.
""",
                        "whys": [
                            r"Two derivations that are the same derivation agree everywhere, including on the design's mistakes.",
                            r"The identical seeds do reach the corner — the specification-derived reference catches it under all eight of them — so the stimulus is doing its job and the comparison is not.",
                            r"This is the reading a green regression invites, and it treats the run as evidence about the design when it is evidence about the bench. No conclusion about the design survives a checker that cannot fail.",
                            r"Abstraction is not the issue: this reference has exactly the design's level of detail, which is the difficulty. A more abstract model written from the specification would have caught it.",
                        ],
                    },
                    {
                        "q": "Under one seed the two models first differ at cycle 6 and go on to differ on 81 of the 200 cycles. Why should the scoreboard report the first cycle rather than all 81?",
                        "opts": [
                            "Because after the first divergence the two machines hold different state, so later cycles are consequences of it rather than separate faults",
                            "Because 81 mismatches out of 200 is close to what an unseeded comparison produces by chance, and only the first one is statistically meaningful",
                            "Because the later mismatches are on flags rather than data, and a flag mismatch is not a failure until an item is actually lost",
                            "Because reporting them all would take a comparison at every cycle, and a bench that compares once per run is much cheaper to execute",
                        ],
                        "a": 0,
                        "why": r"""
Once the design has refused an item its occupancy is permanently one behind, so every later
flag and every later pop is being compared against a machine in a state the design can no
longer be in. Eighty of those 81 cycles are downstream of one cause. Printing them all
buries the cycle that carries the information under the ones that follow from it, which is
why `compare` returns an index. It is also why the count varies so much between seeds — 12
cycles under one and 81 under another — while the number of bugs does not.
""",
                        "whys": [
                            r"One cause, eighty consequences: the state divergence persists, so every later comparison is against a machine that has already been knocked out of step.",
                            r"There is no chance involved. The comparison is deterministic given the stimulus, and two correct models produce zero mismatches on any seed whatsoever.",
                            r"Both kinds appear among the 81, and a flag mismatch is a genuine failure — the design is reporting an occupancy it does not have, which anything upstream would act on.",
                            r"The comparison runs every cycle either way; what differs is only how much of it is printed. Cost is not what makes the first index the useful one.",
                        ],
                    },
                    {
                        "q": "The same reference and design run for 20,000 cycles with the push probability at 0.25 and the pop probability at 0.90, and report no mismatch. A 200-cycle run at 0.50 and 0.50 finds one. What separates the two runs?",
                        "opts": [
                            "The drain-heavy distribution never lets the queue fill, so the state the bug lives in is reached zero times against three in the shorter run",
                            "Twenty thousand cycles is long enough for the two models to resynchronise after a divergence, which hides mismatches the shorter run still shows",
                            "The higher pop probability means most cycles pop nothing, so the useful stimulus in that run is a small fraction of its length",
                            "The shorter run is the one to distrust, since 200 cycles is too few for a random comparison and its single mismatch may be an artefact",
                        ],
                        "a": 0,
                        "why": r"""
Pushing a quarter of the time and popping nine tenths of the time keeps the FIFO drained,
and the fault only exists when a push meets a pop at a full FIFO. The instrumented count is
the whole answer: that condition arises three times in the 200-cycle balanced run and not
once in 20,000 drain-heavy cycles. Running it for a million would not change that, because
the distribution and not the length is what excludes the corner. Pass and fail are the same
verdict in both runs; the coverage count is the only measurement that tells them apart.
""",
                        "whys": [
                            r"The corner is a state, and a distribution that keeps the queue empty never enters it however long it runs.",
                            r"They cannot resynchronise. A dropped item leaves the design permanently one item behind the reference, so a divergence once seen never heals.",
                            r"A high pop probability is exactly what keeps the queue drained, so this notices the right parameter and draws the wrong conclusion from it. The wasted cycles are not idle pops, they are pushes that never accumulate.",
                            r"The 200-cycle mismatch is reproducible from its seed and is backed by a directed sequence that reaches the same disagreement in six cycles. It is the long run's clean result that carries no information.",
                        ],
                    },
                    {
                        "q": "The derivation in this module gives $1/p = 2^{2W}$ as the expected number of random vectors needed to hit one particular pair of $W$-bit operands — $1.8 \\times 10^{19}$ at $W = 32$. Why does random stimulus nonetheless find this FIFO's bug within a hundred cycles?",
                        "opts": [
                            "The corner here is a state that a great many different stimulus sequences reach, not one point in the input space",
                            "The FIFO's inputs are one bit each, so its input space is small enough for random draws to enumerate it in full",
                            "The stimulus is seeded, and a seeded generator covers its range far more evenly than independent draws would",
                            "Sequential designs accumulate stimulus across cycles, so the probability of a hit rises with every cycle already run",
                        ],
                        "a": 0,
                        "why": r"""
What decides whether randomisation finds a bug is the measure of the set of stimuli that
reach it, and that is not the same as the size of the input space. A bug at one $(a, b)$
pair is reachable by one vector out of $2^{2W}$. A bug at "full, with a push and a pop
together" is reachable by any of an enormous number of sequences, and the balanced run
enters it three times in 200 cycles. The moral is not that randomisation is strong or weak
but that it is worth measuring: the corner you can name gets a directed test, and the
coverage count tells you whether the random stimulus went anywhere near it.
""",
                        "whys": [
                            r"An enormous set of sequences ends in a full queue with both controls asserted, and the corner's probability follows from the size of that set.",
                            r"The data field is eight bits wide, and even if it were one, enumerating an input space is not what happened — the corner is about the queue's occupancy, which no single vector determines.",
                            r"A seed makes a run reproducible and changes nothing about how the draws are distributed. The stream from `random.Random(0)` is as uneven as any other.",
                            r"Each cycle's draw is independent of the ones before it. What accumulates across cycles is the design's state, which is why a state-shaped corner is easy to reach and a vector-shaped one is not.",
                        ],
                    },
                    {
                        "q": "The bench compares the design against a reference derived from the specification and finds them in agreement over millions of cycles. Which claim is still out of reach?",
                        "opts": [
                            "That the specification itself says what the system needs, since two faithful derivations of a wrong clause agree with each other",
                            "That the design behaves correctly on the stimulus that was run, which needs a formal proof rather than a comparison against a model",
                            "That the design and the reference implement the same function, which agreement over that many cycles cannot make probable",
                            "That the reference model is free of defects, since any bug in it would have shown up as a mismatch during the run",
                        ],
                        "a": 0,
                        "why": r"""
A scoreboard compares a design with a document's meaning as two people understood it. If
the document is wrong, both derivations are wrong together and agree perfectly. The clause
in this module is a live example: a FIFO that refuses a push arriving with a pop while full
is a defensible block, and against *that* specification the design is correct and the
reference is the faulty model. What the bench establishes is which document the design
implements, never whether that document should have been written.
""",
                        "whys": [
                            r"Both models can be faithful to a clause that should not have been written, and agreement between them is silent about it.",
                            r"Agreement on the stimulus that was run is precisely what the comparison does establish, cycle by cycle. Proof is needed for the stimulus that was not run, which is a different claim.",
                            r"Millions of agreeing cycles are strong evidence for exactly that, which is why the technique is worth its cost. It is evidence rather than proof, but it is not out of reach.",
                            r"A reference bug on a path the design also gets wrong in the same way stays hidden, and one on a path the stimulus never covers stays hidden too. The run bounds where the reference has been exercised, not whether it is sound.",
                        ],
                    },
                ],
            },
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
            "blanks": {
                "title": "A bench that checks itself",
                "minutes": 8,
                "caption": "bench.py — where the reference comes from, and what it catches",
                "lang": "text",
                "brief": r"""
A test that prints waveforms is a test nobody runs twice. A test that compares against a
model written independently is a test that can run ten thousand times unattended. Fill in
the four decisions that separate the two.
""",
                "listing": """The reference model is written from ___ ,

not from the design -- because a model derived from the design
will faithfully agree with ___ .

A scoreboard compares the two streams and reports ___ ,
which is the one place worth looking.

Directed stimulus reaches ___ .

Randomised stimulus, given enough runs, reaches ___ .
""",
                "blanks": [
                    {
                        "prompt": "Where does the reference come from?",
                        "hole": "?",
                        "opts": ["the specification", "the RTL", "the waveform dump", "the previous version"],
                        "a": 0,
                        "why": "Independently, from what the block is supposed to do. That independence is the entire value: two derivations of the same intent, disagreeing only where one of them is wrong.",
                        "whys": [
                            "Independently, from what the block is supposed to do. That independence is the entire value: two derivations of the same intent, disagreeing only where one of them is wrong.",
                            "A model read off the design has no independence and cannot disagree with it in the places that matter.",
                            "Waveforms are output, not specification, and reading a reference from them enshrines whatever the design did on that run.",
                            "Comparing against the previous version catches regressions and cannot catch a bug both versions share.",
                        ],
                    },
                    {
                        "prompt": "What does a design-derived model agree with?",
                        "hole": "?",
                        "opts": ["the design's bugs", "the specification", "nothing", "the timing"],
                        "a": 0,
                        "why": "Including them, silently. This is why an engineer verifying their own block should write the model first, or from the document, or ideally have someone else write it — and why 'the test passes' from a model written afterwards is much weaker evidence than it feels.",
                        "whys": [
                            "Including them, silently. This is why an engineer verifying their own block should write the model first, or from the document, or ideally have someone else write it — and why 'the test passes' from a model written afterwards is much weaker evidence than it feels.",
                            "Only where the design happens to be right, which is exactly the part that needed no checking.",
                            "It will agree with a great deal — that is the problem.",
                            "Timing is a separate concern from functional equivalence.",
                        ],
                    },
                    {
                        "prompt": "What should the scoreboard report?",
                        "hole": "?",
                        "opts": [
                            "the first divergence",
                            "every divergence",
                            "the total number of mismatches",
                            "the final state of both models",
                        ],
                        "a": 0,
                        "why": "The first one, because everything after it is downstream of a machine already in the wrong state — a thousand reported mismatches are usually one bug plus nine hundred and ninety-nine consequences. Stopping there points at the cause instead of burying it.",
                        "whys": [
                            "The first one, because everything after it is downstream of a machine already in the wrong state — a thousand reported mismatches are usually one bug plus nine hundred and ninety-nine consequences. Stopping there points at the cause instead of burying it.",
                            "Reporting all of them buries the useful information in noise generated by the first.",
                            "A count says a bug exists and nothing about where.",
                            "Final states will differ once anything has gone wrong, and comparing only them says nothing about when.",
                        ],
                    },
                    {
                        "prompt": "What does directed stimulus find?",
                        "hole": "?",
                        "opts": [
                            "the corners you already thought of",
                            "the corners you did not think of",
                            "timing violations",
                            "synthesis errors",
                        ],
                        "a": 0,
                        "why": "Which is genuinely valuable — it is how you check the cases the specification calls out — and is bounded by your own imagination. Directed tests prove the things you know to ask about.",
                        "whys": [
                            "Which is genuinely valuable — it is how you check the cases the specification calls out — and is bounded by your own imagination. Directed tests prove the things you know to ask about.",
                            "That is what randomisation is for, and the contrast is the point of pairing the two.",
                            "Timing is checked by static analysis, not by stimulus.",
                            "Synthesis errors are caught by the synthesiser.",
                        ],
                    },
                    {
                        "prompt": "And randomised stimulus?",
                        "hole": "?",
                        "opts": [
                            "the corners you did not think of",
                            "the same corners, more slowly",
                            "only common cases",
                            "nothing a directed test cannot",
                        ],
                        "a": 0,
                        "why": "Random sequences reach interleavings no one would have written down — the back-to-back stall on the cycle a flush arrives, and so on. It needs coverage measurement to say when enough is enough, and constraints to keep it legal, and with both it finds bugs directed testing structurally cannot.",
                        "whys": [
                            "Random sequences reach interleavings no one would have written down — the back-to-back stall on the cycle a flush arrives, and so on. It needs coverage measurement to say when enough is enough, and constraints to keep it legal, and with both it finds bugs directed testing structurally cannot.",
                            "It reaches a different set, which is why the two are complementary rather than redundant.",
                            "Unconstrained randomisation spends most of its time on unusual cases, not common ones — the opposite complaint is the usual one.",
                            "If that were true nobody would run it; the whole industry does.",
                        ],
                    },
                ],
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
