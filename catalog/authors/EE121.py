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
        "Read and write two’s complement, subtract by adding the complement, and say which of the carry and the overflow flag an addition has set.",
        "Account for the noise margin and the switching power of a CMOS gate, and explain why a settled gate draws almost no current.",
        "Build combinational logic from decoders and multiplexers, including using a multiplexer with constant data inputs as an arbitrary function.",
        "Draw the state diagram and state table of a small sequential machine, and say what a reset input and an input synchroniser each protect you from.",
    ],
    "assessment": (
        "A quiz in every module. Seven small labs checked by execution, five circuits drawn "
        "and measured in the schematic editor, two component-sizing targets to hit against "
        "stated constraints, two guided derivations, a symbol drill, two fill-in drills and "
        "two numerical questions — and a capstone that builds a counter and its display "
        "decoder from a truth table upwards."
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
                "A driver promises $V_{OH}$, the weakest HIGH it will put out, and $V_{OL}$, the strongest LOW; a receiver promises to read anything above $V_{IH}$ as HIGH and anything below $V_{IL}$ as LOW. The two gaps between those promises are the **noise margins**.",
                "A gate is **restoring**: it reads a level, throws the incoming voltage away, and drives a fresh one at the rail. That is why noise does not accumulate along a chain of gates the way it does along a chain of analogue stages.",
                "Bits become a voltage again through a **weighted resistor network**: give each bit a conductance proportional to its place value and the shared node settles at $V_s D/(2^n - 1)$, where $D$ is the number the bits spell.",
            ],
            "read": [
                {
                    "title": "Why a wire is allowed to mean only two things",
                    "minutes": 9,
                    "body": r'''
A logic signal is a voltage on a wire, and a voltage on a wire is an analogue
quantity like every other. Nothing about a circuit board knows that the 3.2 V sitting
on one of its tracks is supposed to mean *one*. The tracks have resistance and
capacitance to their neighbours, the ground plane underneath is not at exactly zero
volts everywhere at once, and a motor starting up two inches away will put a spike on
anything it can couple into. Whatever voltage you meant to send, what arrives is that
voltage plus whatever the board added on the way.

Digital electronics is not the art of building wires good enough that this stops
happening. It is an agreement about what counts as what — and the agreement turns out
to be worth far more than better wires would be.

## The trouble with meaning it exactly

Suppose a voltage means what it says: 2.000 V means two thousand millivolts of
something, and every millivolt matters. Send it through a buffer that is honest to
within 20 mV, then through another, then another. Each stage adds its own small error
to whatever it was handed, and the errors have no reason to cancel.

```
one stage, worst case              +/- 20 mV
after 12 stages, worst case        12 x 20 mV       = +/- 240 mV
as a fraction of a 2.000 V signal  240 / 2000       = +/- 12 %
```

Nothing has gone wrong in any single stage. The design is simply accumulating, and a
chain long enough will accumulate its way to nonsense. That is the fundamental problem
with a signal whose exact value is its meaning: **no operation can remove the error**,
because nothing downstream is able to tell the error from the signal.

Now change the agreement. Say that the only thing a voltage carries is one of two
answers: everything below some level means one answer, everything above another level
means the other. Feed 3.2 V into a gate whose rule is "anything above 1.6 V is HIGH"
and the gate does not pass 3.2 V along. It reads *HIGH*, and then it generates a fresh
HIGH of its own, pushed all the way to the supply rail by a transistor that is either
on or off. The 3.2 V — and the noise that made it 3.2 V rather than 3.4 V — is
discarded on the spot.

That property is what the whole field runs on, and it has a name: a logic gate is
**restoring**. Errors do not accumulate down a chain of gates, because every gate
throws its input away and starts again. What has to be true is only ever a statement
about *one hop*: did the voltage still land on the right side of the line by the time
it arrived?

## Four voltages, not two

"On the right side of the line" needs the line drawn, and in practice that takes four
numbers rather than one. Two of them are promises the **driver** makes about what it
puts out:

* $V_{OH}$ — the *lowest* voltage it will produce when it is driving HIGH
* $V_{OL}$ — the *highest* voltage it will produce when it is driving LOW

and two are promises the **receiver** makes about what it will accept:

* $V_{IH}$ — anything above this is read as HIGH
* $V_{IL}$ — anything below this is read as LOW

The useful part is the mismatch between the two pairs. A driver's worst HIGH is higher
than the worst HIGH a receiver demands, so there is room between them, and that room is
how much the board is allowed to steal on the way across. Subtract, and you have the
**noise margin**:

$$NM_H = V_{OH} - V_{IH} \qquad\qquad NM_L = V_{IL} - V_{OL}$$

Both are worst case against worst case: the weakest HIGH a driver may legally produce,
set against the highest voltage a receiver may legally refuse to call HIGH.

### Worked: a 5 V logic family

A common 5 V CMOS family guarantees the following, driving a light load. The figures are
quoted at a 4.5 V supply rather than 5.0 V because that is the bottom of a 5 V rail with
a 10 % tolerance, and a guarantee is only worth having at the worst corner. These are
real datasheet numbers, not illustrative ones.

```
V_OH  >= 4.40 V     the weakest HIGH it will ever put out
V_OL  <= 0.33 V     the strongest LOW  it will ever put out
V_IH   = 3.15 V     it reads anything above this as HIGH   (0.7 x 4.5)
V_IL   = 1.35 V     it reads anything below this as LOW    (0.3 x 4.5)

NM_H = V_OH - V_IH  =  4.40 - 3.15  =  1.25 V
NM_L = V_IL - V_OL  =  1.35 - 0.33  =  1.02 V

forbidden band = V_IH - V_IL = 3.15 - 1.35 = 1.80 V
```

The worse of the two margins is 1.02 V. Somebody would have to inject a whole volt of
interference onto that track, in the wrong direction, before the receiver read the
wrong answer — and if they injected 0.9 V instead, nothing at all would happen. Not
"the signal degrades slightly": nothing. The gate reads HIGH, drives a clean HIGH, and
the 0.9 V of noise ends there.

The 1.80 V in the middle is the **forbidden band**, the range no settled signal is
allowed to sit in, because a receiver is entitled to read anything in it either way.

## Why two, and not ten

The obvious objection is that two symbols per wire is wasteful. Ten symbols would
carry $\log_2 10 = 3.32$ times as much per wire per symbol. So why does nobody build
base-ten logic?

Put $b$ evenly spaced levels on a rail of $V$ volts. The gap between neighbouring
levels is

$$\text{spacing} = \frac{V}{b-1}$$

and a receiver deciding which level a voltage is nearest to has half a gap of room
before it decides wrongly:

$$\text{margin} = \frac{V}{2(b-1)}$$

### Worked: the same 5 V rail, cut two ways

```
b = 2 levels                      b = 10 levels
spacing = 5 / (2-1)  = 5.000 V    spacing = 5 / (10-1) = 0.556 V
margin  = 5.000 / 2  = 2.500 V    margin  = 0.556 / 2  = 0.278 V
```

278 mV. That is the same order as the ground bounce on an ordinary board when a dozen
outputs switch at once, and rather less than a nearby switching regulator will couple
into a track that runs past it. You would have bought 3.3 times the data per wire and
paid nine times the margin for it.

The margin is not even the largest part of the cost. A comparator with **one**
threshold is a couple of transistors — the receiver above does its entire job by being
a pair of transistors that are never both properly on. A ten-level receiver is a
subsystem: nine thresholds, every one of them accurate, all of them tracking
temperature and supply together, and a decoder behind them. Two levels is not merely
more robust than ten, it is enormously cheaper, and that combination is why it won.

## The mistake worth naming

The tempting belief is that **a 1 is 5 V**. It is not, and taking it literally is what
leads someone to put a meter on a perfectly good board, read 4.1 V on a signal that is
HIGH, and start hunting for a fault. There is no fault. A 1 is anything the receiver
will call HIGH, and the discipline consists precisely of never needing to know which
particular voltage arrived.

The second half of the same mistake is reading the forbidden band as a place the signal
never goes. Every transition crosses it — a signal on its way from 0 V to 5 V is at
2.4 V for a moment, necessarily. The rule is about signals that have **settled**. What
is genuinely forbidden is *staying* there, and a real circuit has two ways of doing
that. A very slow edge lingers in the band, and while it does, both transistors in the
receiving gate are partly on and the part draws a current it was never designed to
draw. And an input left unconnected floats to wherever leakage takes it, which is
frequently mid-band, where the gate oscillates and heats up. An unused CMOS input gets
tied to a rail, always, and this is the reason.

## Where this stops holding

**Two levels is a choice, not a law.** Where the channel is good and the wires are
expensive, engineers do use more. A fast serial link inside a data centre often runs
PAM-4 — four levels, two bits per symbol — and pays for the shrunken margin with
equalisation and forward error correction. Flash memory stores three or four bits per
cell as eight or sixteen levels of trapped charge, and spends a great deal of
error-correcting machinery keeping them apart. The trade is always the one above: bits
per symbol against millivolts of margin.

**The numbers here are board numbers.** Inside a chip, where the wires are microns
long and the supply may be 0.9 V rather than 5 V, margins are tens of millivolts and
the analysis becomes statistical rather than worst case.

**And none of it applies while the signal is moving.** Everything above describes a
settled logic level. How long "settled" takes, and what a circuit is allowed to believe
in the meantime, is the subject of the module on flip-flops and the clock — and it is
the single thing that decides how fast a digital system can run.
''',
                },
                {
                    "title": "Place value, and why the base is the only thing that changes",
                    "minutes": 9,
                    "body": r'''
Write down 214 and you have already used a convention so thoroughly that it is hard to
see. The symbols are 2, 1 and 4, but the number is not two, one and four; it is two
hundred and fourteen, and the reason the 2 is worth a hundred is that it is sitting in
the third position from the right.

Nothing about the symbol 2 says a hundred. The position says it.

## Where the positions come from

Watch a mechanical odometer, or count on your fingers, and the rule builds itself. You
have ten symbols. Count up through them: 0, 1, and on to 9. Now you are out of symbols,
and the only thing left to do is put the units wheel back to 0 and advance the wheel to
its left by one. That is what "10" records — one full turn of the units wheel, and
nothing left over.

Do it nine more times and the tens wheel runs out too, so it rolls over and advances the
hundreds wheel. The third wheel therefore counts full turns of the second, each of which
was ten turns of the first. It is worth $10 \times 10$, not because anyone decreed it,
but because that is how many counts it takes to move it once.

That is the whole of place value, and it holds for any number of symbols. With $b$
symbols the $i$-th wheel from the right advances once every $b^i$ counts, so it is worth
$b^i$, and a number written $d_{n-1}\,\dots\,d_1 d_0$ stands for

$$\text{value} \;=\; \sum_{i=0}^{n-1} d_i\, b^{\,i}$$

Base ten is one choice of $b$, and it is a choice about our hands rather than about
arithmetic.

## The places in binary

Take $b = 2$. There are two symbols, 0 and 1, so the wheels roll over twice as often,
and every place is worth twice the place to its right:

```
place        7    6    5    4    3    2    1    0
worth      128   64   32   16    8    4    2    1
```

Counted from the **right**, always, because the rightmost place is the one that advances
on every count. That is the same in binary as in decimal, and forgetting it is the
single most common error made with a binary number.

### Worked: reading `1101 0110`

The gap in the middle is only for the eye — it groups the byte into two nibbles of four
bits and changes nothing. Line the digits up against the places and add whatever is
selected:

```
  bit      1    1    0    1    0    1    1    0
  worth  128   64   32   16    8    4    2    1
  taken  128 + 64 +  0 + 16 +  0 +  4 +  2 +  0

         128 +  64 = 192
         192 +  16 = 208
         208 +   4 = 212
         212 +   2 = 214
```

So `11010110` is 214.

There is a second route that is less writing, and it is also how you would program it.
Read the digits left to right and, at each one, double what you have so far and add the
new digit. Doubling is exactly what "move one place left" means, so this is the same
rule read forwards:

```
  start            0
  1          0*2+1 = 1
  1          1*2+1 = 3
  0          3*2+0 = 6
  1          6*2+1 = 13
  0         13*2+0 = 26
  1         26*2+1 = 53
  1         53*2+1 = 107
  0        107*2+0 = 214
```

Same answer, no table of places, and no need to know how long the number is before you
start.

### Worked: going the other way, 214 into binary

Halve repeatedly and record the remainders. Each division by two is asking "is there a
one in the lowest remaining place?", so the remainders come out lowest place first and
the answer has to be read **upwards**:

```
  214 / 2 = 107  r 0     <-- ones place
  107 / 2 =  53  r 1
   53 / 2 =  26  r 1
   26 / 2 =  13  r 0
   13 / 2 =   6  r 1
    6 / 2 =   3  r 0
    3 / 2 =   1  r 1
    1 / 2 =   0  r 1     <-- 128s place

  read upwards:  1 1 0 1 0 1 1 0
```

which is where we came in. Reading the remainders downwards instead gives `01101011`,
which is 107 — and that mirrored answer is the standard way to get this wrong.

## How much a given number of bits holds

Each place is either 0 or 1, and the places are chosen independently, so $n$ places give
$2 \times 2 \times \cdots \times 2 = 2^n$ distinct patterns. Count them for eight bits:
`00000000` through `11111111`, which is 256 patterns.

The values those patterns stand for run from 0 to 255 — because zero is one of the 256.
That single fact is the source of more off-by-one bugs than anything else in the
subject, so it is worth stating in both directions:

$$\text{patterns} = 2^n \qquad\qquad \text{largest value} = 2^n - 1$$

Read backwards it answers the question a designer actually asks, which is *how many
wires do I need?* For 40 distinct things, $2^5 = 32$ is not enough and $2^6 = 64$ is, so
six bits, with 24 patterns going spare.

## Appending a zero, and why processors like it

Write a 0 on the right of `1011` to make `10110` and every digit has moved one place
left, into a place worth twice as much. So the value doubles: 11 becomes 22. In decimal
the identical move multiplies by ten, for the identical reason. The rule is not about
zeros, it is about the base.

This is why a processor implements "multiply by two" as a **shift** and gets it in one
gate delay, while a general multiply needs a substantial circuit. It is also why a shift
of three places to the right divides by eight, discarding whatever falls off the bottom.

## Hexadecimal, and why anyone bothers

Binary is correct and unreadable. `1101011010110110` is sixteen symbols with no
landmarks in it, and two people reading it aloud will disagree about where they are.
Decimal is readable and useless here: the same value in decimal is 54966, which tells
you nothing whatever about which bits are set.

Base sixteen splits the difference, and it does so because sixteen is $2^4$. One hex
digit is exactly four binary places, so conversion is a lookup on groups of four and
never requires dividing anything:

```
  1101 0110        1101 = 8+4+1 = 13 = d
   d    6          0110 =   4+2 =  6 = 6

  0xd6  =  13 x 16 + 6  =  208 + 6  =  214      the same number
```

The digits above 9 are written a, b, c, d, e, f for ten to fifteen. Going the other way
is just as mechanical — `0x2f9` is

```
   2    f    9
   2 x 256 + 15 x 16 + 9  =  512 + 240 + 9  =  761

   as bits:  0010 1111 1001
```

Hexadecimal is not a different kind of number, and there is no such operation as
converting a value "to hex". The value is 214 however it is written down; hex is a
notation for the same thing, chosen because it lines up with nibbles.

## Where this stops

Everything above is about **unsigned whole numbers**, and that is a narrow thing.

There is no minus sign anywhere in the scheme, and a circuit has no way to write one.
Making the same eight bits stand for negative numbers as well means giving up some of
the positive range and adopting a convention about what the top bit means. That is the
subject of the module on two's complement, where `11010110` stops being 214 and becomes
$-42$.

There is no radix point either. Representing a fraction means agreeing in advance where
the point sits, or moving to a floating-point format with an exponent field of its own.
Neither is visible in the bits.

And most importantly: **a bit pattern has no meaning of its own.** `11010110` is 214 as
an unsigned byte, $-42$ as a signed one, `0xd6` written down, a character in one text
encoding and an instruction opcode in another. The bits do not know which. The meaning
lives in what the circuit reading them was built to do with them, which is why the width
and the interpretation of every bus in a design are agreed before a single gate is
drawn.
''',
                },
                {
                    "title": "Place value in copper: turning the bits back into a voltage",
                    "minutes": 8,
                    "body": r'''
A number inside a chip is a row of voltages, each near 0 V or near the rail. Sooner or
later something outside the chip has to be *driven* with it: a loudspeaker cone, a
motor, the brightness of a lamp, the deflection of a beam. None of those takes a byte.
They take one voltage, somewhere between the rails, and picking the right one out of a
bit pattern is the job of a **digital-to-analogue converter**.

The interesting part is that the arithmetic of place value turns out to be something a
handful of resistors can do by themselves.

## Conductance is how hard a branch pulls

Connect one resistor between a node and a 5 V rail and the node goes to 5 V. Connect a
second between the same node and ground and the two are now arguing; where the node
settles depends on their values. The useful way to think about it is not resistance but
its reciprocal:

$$G = \frac{1}{R}$$

$G$ is the **conductance**, measured in siemens, and it says how hard that branch can
pull the node towards whatever is at its far end. A 10 kΩ resistor pulls with
$10^{-4}$ S; a 20 kΩ resistor pulls with $5\times10^{-5}$ S, exactly half as hard.

Halve the resistance and you double the pull. That is the fact place value needs.

## Several bits, one node

Give every bit of a number its own resistor and connect all of the resistors to one
shared node. Each bit sits at either $V_s$ (HIGH) or 0 V (LOW), so branch $i$ carries a
current $(b_i V_s - V)/R_i$ into the node, where $V$ is wherever the shared node has
settled and $b_i$ is 0 or 1.

Nothing else is connected to that node, so those currents must add to zero — whatever
flows in through some branches flows out through the others. Write that down and solve:

$$\sum_i \frac{b_i V_s - V}{R_i} = 0
\qquad\Longrightarrow\qquad
V = V_s\,\frac{\sum_i b_i G_i}{\sum_i G_i}$$

The node lands at a **conductance-weighted average** of the bit voltages. Now choose the
conductances to be the place values: the ones bit gets $G$, the twos bit $2G$, the fours
bit $4G$ — which means resistors of $4R$, $2R$ and $R$, the largest resistor on the least
significant bit. Then $\sum_i b_i G_i$ is $G$ times the number the bits spell,
$\sum_i G_i$ is $G$ times $2^n - 1$, the $G$ cancels, and

$$V = V_s\,\frac{D}{2^n - 1}$$

where $D$ is the value of the $n$-bit number. Place value, performed by copper, with no
arithmetic circuit anywhere in sight.

### Worked: three bits, input `101`

Take $R = 10$ kΩ, so the branches are 10 kΩ on the fours bit, 20 kΩ on the twos and
40 kΩ on the ones, with $V_s = 5$ V. The pattern `101` puts the fours and the ones at
5 V and the twos at 0 V.

```
  branch          resistor     conductance     driven to
  fours (b=1)      10 kΩ        100.0 µS         5 V
  twos  (b=0)      20 kΩ         50.0 µS         0 V
  ones  (b=1)      40 kΩ         25.0 µS         5 V
                                ---------
  total                         175.0 µS

  numerator = 5 V x (100.0 + 25.0) µS = 5 x 125.0
  V         = 5 x 125.0 / 175.0       = 3.5714 V
```

The shortcut agrees: `101` is 5, three bits have a full scale of $2^3 - 1 = 7$, and
$5 \times 5/7 = 3.5714$ V.

One step is worth $5/7 = 0.714$ V, so the eight patterns land on 0, 0.714, 1.429, 2.143,
2.857, 3.571, 4.286 and 5.000 V — evenly spaced, with the top of the scale sitting
exactly on the rail, because all three bits HIGH is nothing but three resistors tied to
5 V.

### Worked: one bit at a time, and the trap in doing it that way

Set only the ones bit and the formula gives $5 \times 1/7 = 0.714$ V; set only the fours
bit and it gives $5 \times 4/7 = 2.857$ V. Add the two and you have 3.571 V, the answer
above. That is not a coincidence — **superposition** holds because the network is
linear, and taking one source at a time is often the quickest way to work one of these
out.

But superposition has a trap in it, and it is the mistake people actually make. Turning
a source off here means setting it to **0 V**, which leaves its resistor connected to
the node and still pulling towards ground. It does not mean removing the branch. Delete
the fours branch rather than grounding it and the ones bit alone appears to give

```
  wrong:  fours branch deleted    5 x 25/(25+50)      = 1.667 V
  right:  fours branch grounded   5 x 25/(25+50+100)  = 0.714 V
```

which is out by a factor of more than two. The branches that are LOW are doing real
work: they are exactly what makes the divisor $2^n - 1$ instead of something smaller.

## Where the weighted network stops

It stops at about four bits, and the reason is the ratio between the largest resistor
and the smallest.

An eight-bit version needs $R$ through $128R$ — 10 kΩ up to 1.28 MΩ. Two problems arrive
together. One step at the output is $5/255 = 19.6$ mV, while the most significant branch
contributes $128/255$ of full scale, which is 2.51 V. Resistors are sold with a
tolerance, and a 1 % error on that one resistor moves its contribution by about 25 mV —
**more than a whole step**. The converter would then have codes that go backwards:
`10000000` could read lower than `01111111`. To be sure that never happens the MSB
resistor has to be accurate to better than half a step, which here is about 0.4 %, and
the requirement gets twice as hard for every bit you add.

The second problem is duller and just as real: 1.28 MΩ resistors have significant
temperature coefficients and pick up noise, and building a 128:1 spread of accurate
resistors on one piece of silicon costs area.

## R-2R: the same arithmetic with two resistor values

The fix is to stop encoding the weights in the resistors and encode them in the
*network* instead. An R-2R ladder uses only two values, $R$ and $2R$, arranged as a
chain: a series $R$ between each pair of nodes, a $2R$ from each node down to its bit,
and one extra $2R$ terminating the far end to ground.

The termination is the trick. Start at that far end: the terminating $2R$ sits in
parallel with the least significant bit's $2R$, which is $R$; add the series $R$ and you
are looking at $2R$ again from the next node up. Put that node's own $2R$ in parallel and
you are back to $R$; add the series $R$, and $2R$ once more. **Every node in the ladder
sees $2R$ looking towards the far end**, however long the ladder is, so each stage
divides the contribution coming from beyond it by exactly two. A factor of two per stage
is precisely place value, and the output comes out as

$$V = V_s\,\frac{D}{2^n}$$

Note the denominator: $2^n$, not $2^n - 1$. The full-scale code no longer reaches the
rail.

### Worked: four bits, input `1010`

With $R = 10$ kΩ, $2R = 20$ kΩ and $V_s = 5$ V, the code `1010` is $8 + 2 = 10$:

```
  V_out          = 5 x 10/16   = 3.1250 V
  one step       = 5/16        = 0.3125 V
  full scale     = 5 x 15/16   = 4.6875 V     -- never 5 V
```

Solve the whole ladder and its internal nodes come out at 1.172 V, 2.344 V, 2.188 V and
3.125 V, reading from the terminated end towards the output. Notice that the third is
*lower* than the second: the nodes along a ladder are not a monotone ramp, and there is
nothing to be read into any of them individually. Only the output node is the number.

## Where all of this stops

Both networks assume the bits are driven by ideal sources sitting at exactly 0 V and
exactly $V_s$. In a real converter the bits are analogue switches, and a switch's
on-resistance adds to whichever branch it is in — a systematic error, and worst on the
branches with the smallest resistors, which are the most significant ones.

Both also assume nothing is connected to the output. Hang a load on the shared node and
it becomes one more conductance in the sum, dragging every code down by a different
amount. The standard answer is to follow the network with an amplifier that draws no
input current, which is one of the things an operational amplifier is for.

And neither says anything about how fast the output may change, which for audio or video
is the whole design problem. Settling time, the glitch that appears when several bits
switch at slightly different instants, and the sample-and-hold that cleans it up belong
to a converter course. What this module claims is narrower and worth having on its own:
the worth of a place is a physical quantity, and a resistor is one way of storing it.
''',
                },
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
            "blanks": {
                "title": "Noise margins on a 3.3 V board",
                "minutes": 8,
                "caption": "four datasheet numbers, and the two subtractions that matter",
                "lang": "text",
                "brief": r'''
A driver promises two things about what it puts out — $V_{OH}$, the weakest HIGH it
will ever produce, and $V_{OL}$, the strongest LOW. A receiver promises two things
about what it will accept — it reads anything above $V_{IH}$ as HIGH and anything below
$V_{IL}$ as LOW.

The gaps between those promises are the **noise margins**, and they are the whole
reason a logic level survives a board with a switching regulator on it. Fill in the
sheet below for one 3.3 V link.
''',
                "listing": """a 3.3 V CMOS gate driving another one, on a board with 250 mV of ground bounce
-------------------------------------------------------------------------------

  supply                  Vcc  = 3.30 V

  the driver guarantees   V_OH >= 3.10 V         the weakest HIGH it puts out
                          V_OL <= 0.15 V         the strongest LOW it puts out

  the receiver promises   V_IH  = 0.7 * Vcc  = ___ V     read as HIGH above this
                          V_IL  = 0.3 * Vcc  = 0.99 V    read as LOW  below this

  HIGH noise margin  =  V_OH - V_IH
                     =  3.10 - 2.31              =  ___ V

  LOW  noise margin  =  ___
                     =  0.99 - 0.15              =  0.84 V

  forbidden band     =  V_IH - V_IL
                     =  2.31 - 0.99              =  1.32 V

  worst case on this board: 250 mV of noise subtracted from a HIGH

      3.10 - 0.25 = 2.85 V arrives, which clears V_IH by  ___ V
""",
                "blanks": [
                    {
                        "prompt": "The receiver calls anything above $0.7 V_{cc}$ a HIGH. On a 3.30 V supply, what is that?",
                        "hole": "?",
                        "opts": ["2.31", "0.99", "1.65", "2.64"],
                        "a": 0,
                        "why": "$0.7 \\times 3.30 = 2.31$ V. The value 0.99 is $0.3 V_{cc}$, which is the "
                               "other threshold and appears on the line below; 1.65 is half the supply, "
                               "which is where the gate switches but is not a threshold it guarantees "
                               "anything about; 2.64 would be $0.8 V_{cc}$. Thresholds specified as a "
                               "fraction of the supply are normal for CMOS, and they mean the margins "
                               "shrink when the rail sags.",
                    },
                    {
                        "prompt": "$V_{OH} - V_{IH}$, with the numbers on the line above it.",
                        "hole": "?",
                        "opts": ["0.79", "1.32", "0.20", "0.99"],
                        "a": 0,
                        "why": "$3.10 - 2.31 = 0.79$ V. That is how much the board is allowed to steal "
                               "from a HIGH before the receiver stops reading it as one. The value 1.32 "
                               "is the forbidden band computed two lines further down, and 0.20 is "
                               "$V_{cc} - V_{OH}$, which is how far the driver falls short of the rail — "
                               "a real number, but not a margin, because nothing downstream cares where "
                               "the rail is.",
                    },
                    {
                        "prompt": "Which subtraction is the LOW noise margin?",
                        "hole": "?",
                        "opts": ["V_IL - V_OL", "V_OL - V_IL", "V_OH - V_IL", "V_IH - V_OL"],
                        "a": 0,
                        "why": "A LOW leaves the driver at 0.15 V at worst and has to arrive below "
                               "0.99 V, so the room available is $V_{IL} - V_{OL} = 0.84$ V. Writing it "
                               "the other way round gives $-0.84$ V, and a negative margin would mean "
                               "the driver's own LOW was already too high to be read as one. The two "
                               "mixed pairs subtract an input threshold from the wrong output promise "
                               "and describe nothing.",
                    },
                    {
                        "prompt": "A HIGH of 3.10 V arrives 250 mV lower than it left. How far is it still above $V_{IH}$?",
                        "hole": "?",
                        "opts": ["0.54", "0.25", "0.79", "2.85"],
                        "a": 0,
                        "why": "$2.85 - 2.31 = 0.54$ V, which is also the 0.79 V margin with the 0.25 V "
                               "of noise taken out of it. The link works, with 540 mV to spare. The "
                               "value 2.85 is the voltage that arrived rather than the room left over, "
                               "and 0.79 is the margin before the noise was subtracted. Note what this "
                               "does *not* say: the receiver does not output 2.85 V. It reads HIGH and "
                               "drives a fresh HIGH of its own, and the 250 mV goes no further.",
                    },
                ],
            },
            "numeric": [
                {
                    "title": "A byte off the bus",
                    "minutes": 5,
                    "brief": r'''
One rule, applied once. The only thing that can go wrong here is the direction the
places are counted in.
''',
                    "prompt": "What decimal value is on the bus?",
                    "note": "Give the answer as a whole number.",
                    "figure": "A logic analyser has captured one instant on an 8-bit unsigned bus. Written "
                              "with the most significant bit on the left, the pattern is `1101 0110`. The "
                              "space in the middle is the analyser grouping the byte into nibbles; it is "
                              "not part of the number.",
                    "given": [
                        {"label": "Bus width", "value": "8 bits, unsigned"},
                        {"label": "Captured pattern", "value": "1101 0110"},
                    ],
                    "aside": "The rightmost place is worth 1, and each place to its left is worth twice "
                             "the one before: 1, 2, 4, 8, 16, 32, 64, 128.",
                    "answer": 214.0,
                    "tol": 0.5,
                    "unit": "",
                    "hint": "Add up the places where a 1 sits: $128 + 64 + 16 + 4 + 2$.",
                    "wrong": "If you got 107, the places were applied from the left instead of the "
                             "right — that is the value of the same digits written backwards, "
                             "`0110 1011`. If you got 11010110 or 1101, the pattern was read as a "
                             "decimal number rather than a binary one.",
                    "why": "Counting places from the right, the 1s sit in the 128, 64, 16, 4 and 2 "
                           "places, so the value is $128 + 64 + 16 + 4 + 2 = 214$. The doubling route "
                           "gets there without a table: starting from 0 and going left to right, "
                           "$1, 3, 6, 13, 26, 53, 107, 214$, doubling and adding each digit in turn. "
                           "In hexadecimal the same byte is `0xd6`, because `1101` is 13 and `0110` is "
                           "6 — which is why the analyser drew the gap where it did.",
                },
                {
                    "title": "How many wires does a state need?",
                    "minutes": 6,
                    "brief": r'''
The same rule as the previous question, used backwards. You are told how many things
have to be told apart and asked for the number of bits, which means finding the
smallest $n$ with $2^n$ at least as large as the count.

There is no rounding involved. A fractional bit is not a thing you can wire up, so the
answer is always the next whole number up.
''',
                    "prompt": "What is the smallest number of bits that can give every state its own pattern?",
                    "note": "Give the answer as a whole number of bits.",
                    "figure": "A vending machine controller moves between 40 distinct states. Each state is "
                              "to be held as a plain binary number in a bundle of flip-flops, one flip-flop "
                              "per bit, with no two states sharing a pattern.",
                    "given": [
                        {"label": "States to distinguish", "value": "40"},
                        {"label": "Encoding", "value": "plain binary, one flip-flop per bit"},
                    ],
                    "aside": "Write out the powers of two until one of them is big enough: 1, 2, 4, 8, "
                             "16, 32, 64.",
                    "answer": 6.0,
                    "tol": 0.5,
                    "unit": "bits",
                    "hint": "$n$ bits give $2^n$ patterns. Find the first $n$ for which $2^n \\ge 40$.",
                    "wrong": "If you got 5, note that $2^5 = 32$ and 32 patterns cannot label 40 states — "
                             "$\\log_2 40 = 5.32$, and 5.32 bits rounds *up*, never down. If you got 40, "
                             "that is one wire per state, which is a real encoding called one-hot and is "
                             "used deliberately in some designs, but it costs 40 flip-flops instead of 6.",
                    "why": "$2^5 = 32 < 40$ and $2^6 = 64 \\ge 40$, so six bits. Twenty-four of the 64 "
                           "patterns are then unused, and that spare space is not free: a machine that "
                           "somehow lands on one of them has to be able to get back, which is what a "
                           "reset input and a default branch in the state table are for. The same "
                           "arithmetic sizes everything else with an address on it — 12 address lines "
                           "reach $2^{12} = 4096$ locations, and a 6-bit opcode field allows 64 "
                           "instructions.",
                },
                {
                    "title": "Two bits pulling one node",
                    "minutes": 7,
                    "brief": r'''
The circuit from the build, with the bits the other way round. The twos bit is LOW, so
its 10 kΩ resistor goes straight to ground; the ones bit is HIGH, so its 20 kΩ resistor
goes to the 5 V rail. The input is therefore `01`.

Read off the node the probe is sitting on.
''',
                    "prompt": "What voltage does the shared node settle at?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r0", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 20000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "r1", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 10000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
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
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "Ones bit (HIGH), through", "value": "20 kΩ"},
                        {"label": "Twos bit (LOW), through", "value": "10 kΩ"},
                    ],
                    "aside": "Two resistors in a line between 5 V and ground. The node between them "
                             "sits at the rail times the share of the total resistance that lies below "
                             "it.",
                    "answer": 1.667,
                    "tol": 0.02,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "$V = 5 \\times R_{\\text{to ground}} / (R_{\\text{to rail}} + R_{\\text{to ground}})$, with 10 kΩ to ground and 20 kΩ to the rail.",
                    "wrong": "If you got 3.33 V, the two resistors were swapped: the larger one is the "
                             "one on the ones bit, and the node always leans towards whichever end is "
                             "reached through the smaller resistance. Here the smaller resistance leads "
                             "to ground, so the node must end up in the lower half of the range.",
                    "why": "$V = 5 \\times 10\\,\\text{k}/(20\\,\\text{k} + 10\\,\\text{k}) = 5/3 = "
                           "1.67$ V. Read it as place value instead and the same number falls out with "
                           "no resistors in it at all: the input is `01`, which is 1, two bits have a "
                           "full scale of $2^2 - 1 = 3$, and $5 \\times 1/3 = 1.67$ V. Compare with the "
                           "build, where the input was `10` and the node sat at $5 \\times 2/3 = 3.33$ "
                           "V — twice as far up the scale, because the twos bit is worth twice the ones "
                           "bit and its resistor is half the size.",
                },
                {
                    "title": "The current in the least significant branch",
                    "minutes": 10,
                    "brief": r'''
Three bits now, weighted 4, 2 and 1 by resistors of 10 kΩ, 20 kΩ and 40 kΩ. The fours
bit and the ones bit are HIGH, each with its own 5 V rail; the twos bit is LOW, so its
20 kΩ goes to ground. The input is `101`.

The question is not about the node this time. It asks what the rail feeding the **ones**
bit — the weakest branch, through the largest resistor — is actually delivering, which
means finding the node first and then coming back to the branch.
''',
                    "prompt": "How much current does the rail driving the ones bit deliver?",
                    "note": "Give the answer in microamps, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v2", "kind": "V", "x": 3, "y": 4, "rot": 1, "value": 5},
                            {"id": "g2", "kind": "GND", "x": 3, "y": 7},
                            {"id": "r2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "g1", "kind": "GND", "x": 3, "y": 11},
                            {"id": "r1", "kind": "R", "x": 6, "y": 11, "rot": 0, "value": 20000},
                            {"id": "v0", "kind": "V", "x": 3, "y": 16, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 19},
                            {"id": "r0", "kind": "R", "x": 6, "y": 15, "rot": 0, "value": 40000},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 11},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 7]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [11, 3]},
                            {"a": [3, 11], "b": [5, 11]},
                            {"a": [7, 11], "b": [11, 11]},
                            {"a": [3, 17], "b": [3, 19]},
                            {"a": [3, 15], "b": [5, 15]},
                            {"a": [7, 15], "b": [11, 15]},
                            {"a": [11, 3], "b": [11, 15]},
                            {"a": [11, 11], "b": [14, 11]},
                        ],
                    },
                    "given": [
                        {"label": "Rails", "value": "5.00 V"},
                        {"label": "Fours bit (HIGH), through", "value": "10 kΩ"},
                        {"label": "Twos bit (LOW), through", "value": "20 kΩ"},
                        {"label": "Ones bit (HIGH), through", "value": "40 kΩ"},
                    ],
                    "aside": "The shared node is a conductance-weighted average of the three bit "
                             "voltages. Once you have it, the ones branch is one resistor with a known "
                             "voltage at each end.",
                    "answer": 35.7,
                    "tol": 0.4,
                    "unit": "µA",
                    # The prompt asks for a branch current, which is no node of this circuit. The
                    # ones bit is identified structurally — it is the branch through the LARGEST
                    # resistor, because the least significant bit is the one that pulls least — so
                    # nothing here repeats a value that the diagram already states.
                    "check": r'''
const rs = c.net.parts.filter(function (p) { return p.kind === 'R'; });
const ones = rs.reduce(function (a, b) { return b.value > a.value ? b : a; });
const d = c.dc();
return Math.abs(d.v[ones.n1] - d.v[ones.n2]) / ones.value * 1e6;
''',
                    "hint": "The node sits at $5 \\times (100 + 25)/(100 + 50 + 25)$ V, working in "
                            "microsiemens — 10 kΩ is 100 µS, 20 kΩ is 50 µS, 40 kΩ is 25 µS. Then the "
                            "current in the ones branch is the 5 V rail minus that node voltage, "
                            "divided by 40 kΩ.",
                    "wrong": "If you got 125 µA, the node voltage was left out and the whole 5 V was "
                             "dropped across the 40 kΩ. If you got 89.3 µA, the drop was taken as the "
                             "node voltage itself rather than the difference between the rail and the "
                             "node.",
                    "why": "The node is a conductance-weighted average: the conductances are 100 µS, "
                           "50 µS and 25 µS, adding to 175 µS, and the two branches held at 5 V "
                           "contribute $100 + 25 = 125$ µS of it. So $V = 5 \\times 125/175 = 3.571$ V "
                           "— which is $5 \\times 5/7$, since `101` is 5 out of a full scale of 7. The "
                           "ones branch then has 5.000 V at one end and 3.571 V at the other, so it "
                           "carries $(5.000 - 3.571)/40\\,\\text{k} = 1.429/40\\,\\text{k} = 35.7$ µA. "
                           "Worth noticing: the fours branch carries $(5.000 - 3.571)/10\\,\\text{k} = "
                           "142.9$ µA and the grounded twos branch carries $3.571/20\\,\\text{k} = "
                           "178.6$ µA out of the node — and $142.9 + 35.7 = 178.6$, which is the "
                           "current balance the node voltage was chosen to satisfy in the first place.",
                },
                {
                    "title": "An R-2R ladder, and the rail that is not the obvious one",
                    "minutes": 12,
                    "brief": r'''
Four bits, and only two resistor values: 10 kΩ in series along the top, 20 kΩ hanging
down from every node — one to each bit, plus a terminating 20 kΩ to ground at the far
left. The eights bit and the twos bit are HIGH, each with its own 5 V rail; the fours
and the ones are LOW, so their 20 kΩ resistors go to ground. The input is `1010`.

An R-2R ladder is arranged so that from any node, looking towards the terminated end,
the network always measures $2R$ — which is what makes each stage halve the contribution
from beyond it, and gives the output $V_s D / 2^n$.

That rule hands you the probed node in one line. This question asks for something the
rule does not give you: the current out of the rail on the **twos** bit, four resistors
back from the output.
''',
                    "prompt": "How much current does the rail driving the twos bit deliver?",
                    "note": "Give the answer in microamps, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "gt", "kind": "GND", "x": 3, "y": 3},
                            {"id": "rt", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 20000},
                            {"id": "ra", "kind": "R", "x": 12, "y": 3, "rot": 0, "value": 10000},
                            {"id": "rb", "kind": "R", "x": 18, "y": 3, "rot": 0, "value": 10000},
                            {"id": "rc", "kind": "R", "x": 24, "y": 3, "rot": 0, "value": 10000},
                            {"id": "r0", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 20000},
                            {"id": "g0", "kind": "GND", "x": 9, "y": 8},
                            {"id": "r1", "kind": "R", "x": 15, "y": 5, "rot": 1, "value": 20000},
                            {"id": "v1", "kind": "V", "x": 15, "y": 8, "rot": 1, "value": 5},
                            {"id": "g1", "kind": "GND", "x": 15, "y": 11},
                            {"id": "r2", "kind": "R", "x": 21, "y": 5, "rot": 1, "value": 20000},
                            {"id": "g2", "kind": "GND", "x": 21, "y": 8},
                            {"id": "r3", "kind": "R", "x": 27, "y": 5, "rot": 1, "value": 20000},
                            {"id": "v3", "kind": "V", "x": 27, "y": 8, "rot": 1, "value": 5},
                            {"id": "g3", "kind": "GND", "x": 27, "y": 11},
                            {"id": "out", "kind": "OUT", "x": 30, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [11, 3]},
                            {"a": [13, 3], "b": [17, 3]},
                            {"a": [19, 3], "b": [23, 3]},
                            {"a": [25, 3], "b": [30, 3]},
                            {"a": [9, 3], "b": [9, 4]},
                            {"a": [9, 6], "b": [9, 8]},
                            {"a": [15, 3], "b": [15, 4]},
                            {"a": [15, 6], "b": [15, 7]},
                            {"a": [15, 9], "b": [15, 11]},
                            {"a": [21, 3], "b": [21, 4]},
                            {"a": [21, 6], "b": [21, 8]},
                            {"a": [27, 3], "b": [27, 4]},
                            {"a": [27, 6], "b": [27, 7]},
                            {"a": [27, 9], "b": [27, 11]},
                        ],
                    },
                    "given": [
                        {"label": "Rails", "value": "5.00 V"},
                        {"label": "Series resistors", "value": "R = 10 kΩ"},
                        {"label": "Branch and termination", "value": "2R = 20 kΩ"},
                        {"label": "Input", "value": "1010 (eights and twos HIGH)"},
                    ],
                    "aside": "Take the two live rails one at a time. For each one, work out what the "
                             "twos-bit node sits at, add the two contributions, and only then use Ohm's "
                             "law on that bit's own 20 kΩ.",
                    "answer": 132.8,
                    "tol": 1.0,
                    "unit": "µA",
                    # No node of this circuit is a branch current, so the check takes the twos bit
                    # rail's own current straight out of the solve. v1 is the source on the twos
                    # bit's 2R branch; the sign is negative because a delivering source carries
                    # current internally from its - terminal to its +.
                    "check": r'''
return Math.abs(c.dc().currents.v1) * 1e6;
''',
                    "hint": "With only the eights bit live, the output node sits at 2.50 V and every "
                            "step back down the ladder halves it, so the twos-bit node is at 0.625 V. "
                            "With only the twos bit live, that node sees 20 kΩ towards the terminated "
                            "end and 22 kΩ towards the output. Add the two answers, then take "
                            "$(5 - V)/20\\,\\text{k}$.",
                    "wrong": "If you got 93.8 µA, that is the eights bit's rail rather than the twos "
                             "bit's — the output node is at 3.125 V and $(5 - 3.125)/20\\,\\text{k}$ is "
                             "93.8 µA. If you got 250 µA, the node voltage was left out and the whole "
                             "5 V taken across the 20 kΩ.",
                    "why": "Superposition, one rail at a time. **Eights bit alone:** looking left from "
                           "the output node the ladder measures 20 kΩ, equal to that bit's own 20 kΩ, "
                           "so the output sits at 2.50 V; each stage back down the ladder halves it, "
                           "giving 1.25 V at the fours node and 0.625 V at the twos node. **Twos bit "
                           "alone:** from the twos node, the terminated side measures 20 kΩ and the "
                           "output side measures $10 + (20 \\parallel 30) = 22$ kΩ, which in parallel "
                           "is 10.48 kΩ, so the node sits at $5 \\times 10.48/(20 + 10.48) = 1.719$ V. "
                           "Adding them gives 2.344 V at the twos node, and the rail therefore "
                           "delivers $(5.000 - 2.344)/20\\,\\text{k} = 132.8$ µA. The probed output, "
                           "for comparison, is $5 \\times 10/16 = 3.125$ V, straight from the ladder "
                           "rule — `1010` is 10, and four bits divide by 16 rather than by 15. Note "
                           "also that the internal nodes run 1.172, 2.344, 2.188, 3.125 V from the "
                           "termination outwards: the third is *lower* than the second, so there is "
                           "nothing to be read into the individual nodes of a ladder. Only the output "
                           "is the number.",
                },
            ],
            "derive": {
                "title": "Why a weighted resistor network spells out the number",
                "minutes": 14,
                "vars": ["V", "V_s", "b_0", "b_1", "b_2", "R", "D", "n"],
                "brief": r'''
Two bits share one node. The **twos** bit reaches it through a resistor $R$, and the
**ones** bit reaches it through $2R$. Each bit is driven to $b V_s$ — that is $V_s$
when the bit is 1 and 0 V when it is 0 — so $b_1$ and $b_0$ are each either 0 or 1.

Nothing else touches the shared node, and it has settled at some voltage $V$.

Two facts are enough to get the whole formula out: the current through a resistor is
the voltage across it divided by its resistance, and the currents arriving at a node
with nowhere else to go must add to zero.
''',
                "steps": [
                    {
                        "prompt": "The twos bit sits at $b_1 V_s$ and reaches the node through $R$, and the node is at $V$. Write the current flowing from that bit *into* the node.",
                        "answer": "\\frac{b_1 V_s - V}{R}",
                        "hint": "Ohm's law across the one resistor: the voltage at the bit end minus the voltage at the node end, divided by the resistance.",
                        "deconstruct": [
                            "The voltage across that resistor is $b_1 V_s - V$, taking the bit end as the positive one.",
                            "Divide by $R$ and you have the current, positive when it flows towards the node.",
                        ],
                    },
                    {
                        "prompt": "The ones bit sits at $b_0 V_s$ and reaches the same node through $2R$. Write the current it delivers into the node.",
                        "answer": "\\frac{b_0 V_s - V}{2 R}",
                        "hint": "The same rule with twice the resistance underneath it.",
                    },
                    {
                        "prompt": "Nothing else is connected to the node, so those two currents add to zero. Solve for $V$ and write it in terms of $V_s$, $b_1$ and $b_0$.",
                        "given": "$\\dfrac{b_1 V_s - V}{R} + \\dfrac{b_0 V_s - V}{2R} = 0$",
                        "answer": "\\frac{V_s (2 b_1 + b_0)}{3}",
                        "placeholder": "\\frac{V_s(\\ldots)}{\\ldots}",
                        "hint": "Multiply the whole equation by $2R$ first. Every $R$ disappears, and what is left is linear in $V$.",
                        "deconstruct": [
                            "Multiplying by $2R$: $2(b_1 V_s - V) + (b_0 V_s - V) = 0$.",
                            "Collecting the $V$ terms on one side: $2 b_1 V_s + b_0 V_s = 3V$.",
                            "So $V = V_s(2 b_1 + b_0)/3$ — and $R$ has vanished, which is why only the *ratio* of the two resistors ever mattered.",
                        ],
                    },
                    {
                        "prompt": "Look at what that says: $2b_1 + b_0$ is the number the two bits spell, and 3 is the largest value two bits can hold. Now do three bits — fours through $R$, twos through $2R$, ones through $4R$ — and write $V$ in terms of $V_s$, $b_2$, $b_1$ and $b_0$.",
                        "answer": "\\frac{V_s (4 b_2 + 2 b_1 + b_0)}{7}",
                        "placeholder": "\\frac{V_s(\\ldots)}{\\ldots}",
                        "hint": "Multiply the three-term current sum by $4R$ this time. The coefficients come out 4, 2 and 1, and they add to 7 on the other side.",
                        "deconstruct": [
                            "The sum is $\\frac{b_2 V_s - V}{R} + \\frac{b_1 V_s - V}{2R} + \\frac{b_0 V_s - V}{4R} = 0$.",
                            "Multiply by $4R$: $4(b_2 V_s - V) + 2(b_1 V_s - V) + (b_0 V_s - V) = 0$.",
                            "The coefficients of $V$ add to $4 + 2 + 1 = 7$, giving $V = V_s(4b_2 + 2b_1 + b_0)/7$.",
                        ],
                    },
                    {
                        "prompt": "Both denominators were one less than a power of two. For an $n$-bit network built the same way, write the size of one step — how much $V$ moves when the number $D$ goes up by one — in terms of $V_s$ and $n$.",
                        "answer": "\\frac{V_s}{2^n - 1}",
                        "hint": "The general result is $V = V_s D/(2^n - 1)$, so a step is what happens to that when $D$ increases by 1.",
                        "deconstruct": [
                            "Two bits gave a denominator of 3, three bits gave 7; in general the conductances $1, 2, 4, \\dots, 2^{n-1}$ add to $2^n - 1$.",
                            "So $V = V_s D/(2^n - 1)$, and raising $D$ by one raises $V$ by $V_s/(2^n - 1)$.",
                        ],
                    },
                ],
                "closing": r'''
Notice what dropped out and what did not. $R$ cancelled in every case, so only the
*ratios* 1 : 2 : 4 matter and you may scale the whole network to whatever current the
rail can supply — which is exactly the freedom the build exploits. What did not drop
out is the $2^n - 1$: all bits HIGH puts every branch on the rail, so full scale lands
on $V_s$ itself, and the scale has $2^n - 1$ steps in it rather than $2^n$.

That is the signature of this topology, and it is how you tell it from an R-2R ladder
by looking at a single number. A ladder divides by $2^n$, so its full-scale code stops
one step short of the rail: four bits reach $5 \times 15/16 = 4.6875$ V, never 5 V.
The ladder pays for that with an extra resistor and buys something worth having — two
resistor values instead of $n$, and no 128:1 spread to hold to a tolerance.
''',
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
                "The operations are physical before they are symbolic: two switches **in series** conduct only when both are closed, which is AND; two **in parallel** conduct when either is closed, which is OR; a contact that opens when its relay energises is NOT.",
                "A **truth table** lists every combination of the inputs with the output for each. For $n$ inputs it has $2^n$ rows, and it is the complete specification — two expressions with the same table are the same function.",
                "Because the output column is $2^n$ independent bits, there are exactly $2^{2^n}$ different functions of $n$ variables: 16 of two variables, 256 of three, 65 536 of four.",
                "The identities worth knowing by name: $A + 0 = A$, $A \\cdot 1 = A$, $A + 1 = 1$, $A \\cdot 0 = 0$, $A + A = A$, $A \\cdot A' = 0$, $A + A' = 1$, and absorption $A + AB = A$.",
                "AND distributes over OR, $A(B + C) = AB + AC$, exactly as in arithmetic — and OR distributes over AND, $A + BC = (A + B)(A + C)$, which has no arithmetic counterpart at all.",
                "**De Morgan's laws**: $(A + B)' = A'B'$ and $(AB)' = A' + B'$. Pushing a complement inwards flips the operation. This is the single most useful rewrite in the subject.",
                "There is no subtraction and no division, so you may never cancel: $A + X = A + Y$ does **not** license $X = Y$.",
                "**XOR**, written $A \\oplus B$, is 1 exactly when the inputs differ. It is not a basic operation but is common enough to be given a symbol.",
            ],
            "read": [
                {
                    "title": "Switches in a line, switches side by side",
                    "minutes": 10,
                    "body": r'''
Put a battery, a lamp and two switches in one loop, one after the other. The lamp
lights when both switches are closed, and in no other case. Now rewire the same two
switches so that each one bridges the same gap on its own. The lamp lights whenever at
least one of them is closed.

That is the whole content of AND and OR, and every electrician knew it long before
anybody called it algebra. What was not obvious — and what Claude Shannon noticed in
1937, while wiring the control panel of a differential analyser at MIT — is that these
networks obey *laws*. Not loose analogies to arithmetic: exact laws, most of them the
same shape as the laws of ordinary algebra, plus several that ordinary algebra does
not have. Once the laws are written down you can shrink a switch network on paper the
way you shrink $3x + 2x$ into $5x$, and then go and build the smaller one, and be
certain in advance that it does the same job.

## Three operations, read off the wiring

Give each switch a letter, and let that letter stand for the statement *this switch is
closed*: 1 when it is closed, 0 when it is open. Then:

* Two switches **in series** make a path only when both are closed. Call that $A \cdot B$,
  or just $AB$. It is **AND**.
* Two switches **in parallel** make a path when either is closed. Call that $A + B$. It
  is **OR**.
* A relay carries **make** contacts, which close when it energises, and **break**
  contacts, which open. A break contact worked by the same relay as a make contact is
  $A'$. It is **NOT**.

Two things about that choice of symbols. The dot and the plus are borrowed from
arithmetic on purpose, because AND really does distribute over OR the way
multiplication distributes over addition — $A(B + C) = AB + AC$ is true of switch
networks for the reason it is true of numbers, and we will check it row by row in the
next reading. And the borrowing is only partial: $1 + 1 = 1$ here, because putting two
closed switches side by side gives you a closed path, not two of them.

## The laws you can see in the copper

Most of the identities in this module are not results to be memorised. They are
statements about wiring that you can settle by looking.

**$A + A = A$.** Wire two contacts of the same relay in parallel. Either one closing
completes the path, and they always close together, so the pair behaves exactly like a
single contact. You have spent a contact and bought nothing.

**$A \cdot A = A$.** The same two contacts in series. Both close together, so again the
pair behaves as one.

**$A \cdot A' = 0$.** A make contact and a break contact of the same relay, in series.
Whichever way the relay sits, one of the two is open, so the path is never complete —
and that is a wire that can be deleted along with everything in series with it.

**$A + A' = 1$.** The same pair in parallel. One of them is always closed, so the path
is always complete. The pair is a piece of wire.

**$A + AB = A$** (absorption). Run a plain wire from one terminal to the other through
contact $A$, and in parallel with it run a second path through $A$ and then $B$. The
second path can only conduct when $A$ is closed — and when $A$ is closed the first path
is already conducting. The second path never once changes the answer. Delete it.

That last one is the most useful, because it is the one people leave in. A schematic
grows by accretion: someone adds an interlock, someone else adds a permissive, and two
years later there is a branch that cannot alter the outcome in any state the machine
can reach.

## Worked: a series pair, in volts

Switches are not ideal, and it pays to see what the algebra is an idealisation of.
Take a 5 V rail, two contacts in series feeding the input of a logic gate, and a
4.7 kΩ resistor from that input down to ground so the input has a defined level when
the contacts are open. Real closed contacts are not shorts — gold-plated signal relay
contacts sit around 100 mΩ when new, but a switch that has been in a panel for ten
years may be hundreds of ohms. Take contact $A$ at 120 Ω and contact $B$ at 180 Ω. An
open contact is not an infinite resistance either; call it 1 MΩ, which is pessimistic
for a clean air gap and about right for one with a film of grime on it.

```
both closed (A = 1, B = 1)
  R_total = 120 + 180 + 4700              =     5 000 Ω
  I       = 5 V / 5 000 Ω                 =     1.000 mA
  V_in    = 1.000 mA x 4700 Ω             =     4.700 V

A closed, B open (A = 1, B = 0)
  R_total = 120 + 1 000 000 + 4700        = 1 004 820 Ω
  I       = 5 V / 1 004 820 Ω             =     4.976 µA
  V_in    = 4.976 µA x 4700 Ω             =     0.0234 V   (23.4 mV)

both open (A = 0, B = 0)
  R_total = 1 000 000 + 1 000 000 + 4700  = 2 004 700 Ω
  I       = 5 V / 2 004 700 Ω             =     2.494 µA
  V_in    = 2.494 µA x 4700 Ω             =     0.0117 V   (11.7 mV)
```

A 5 V CMOS input reads anything above $0.7 \times 5 = 3.5$ V as HIGH and anything below
$0.3 \times 5 = 1.5$ V as LOW. So 4.700 V is a HIGH with 1.2 V of margin, and 23.4 mV
is a LOW with 1.48 V of margin. The table the circuit produces is 1, 0, 0, 0 — the AND
table — and it produces it with enormous room to spare. That is the point of module 1
arriving before this one: the algebra is exact because the electrical picture behind it
is not even close to marginal.

## Worked: the same two contacts, in parallel

Rewire them side by side, everything else unchanged.

```
both closed
  R_pair  = (120 x 180) / (120 + 180) = 21600/300 =    72.00 Ω
  V_in    = 5 V x 4700 / (4700 + 72)              =     4.925 V

A closed, B open
  R_pair  = (120 x 1e6) / (120 + 1e6)             =   119.99 Ω
  V_in    = 5 V x 4700 / (4700 + 119.99)          =     4.876 V

A open, B closed
  R_pair  = (180 x 1e6) / (180 + 1e6)             =   179.97 Ω
  V_in    = 5 V x 4700 / (4700 + 179.97)          =     4.816 V

both open
  R_pair  = (1e6 x 1e6) / 2e6                     = 500 000 Ω
  V_in    = 5 V x 4700 / (4700 + 500000)          =     0.0466 V  (46.6 mV)
```

Three HIGHs and one LOW: the OR table, 1 for every row except the one where both
contacts are open. Notice that the three HIGHs are not equal — 4.925 V, 4.876 V,
4.816 V — and that nothing whatever depends on which of them arrived. Every one of
them is above 3.5 V, so the gate downstream reads HIGH and drives a fresh, clean HIGH
of its own. The 109 mV of spread between the best case and the worst is exactly the
kind of detail the two-valued agreement exists to throw away.

## The mistake people actually make

The plus sign is doing two jobs in a beginner's head at once, and the collision shows
up the first time somebody writes $1 + 1 = 10$ — carrying, as in module 1's binary
arithmetic. It is a completely reasonable confusion, because both notations are in
this course and both use the same two symbols. The distinction is what the symbols
*are*. In binary arithmetic `1` and `1` are numbers and `+` adds them, so the answer
needs two digits. In Boolean algebra $1$ and $1$ are truth values and $+$ is OR, and OR
of two trues is true: $1 + 1 = 1$. There is no carry because there is nowhere for one
to go — the result is a single wire, and a single wire has two states.

The way to keep them apart is to say the expression out loud in switches. "Two closed
switches in parallel" cannot possibly give you two of anything. It gives you a
completed path.

The second common error is subtler and costs more: assuming that because $A + A = A$
you may also cancel. In ordinary algebra, $A + X = A + Y$ lets you subtract $A$ and
conclude $X = Y$. Here it does not, and the counterexample is one line long. Absorption
says $A + AB = A$, and identity says $A + 0 = A$, so $A + AB = A + 0$. If cancelling
were allowed, $AB = 0$ — which is plainly false, since $AB$ is 1 when both are. The
step that fails is the subtraction, and it fails because there is no subtraction:
nothing in this algebra undoes an OR. Every legal move rewrites an expression into an
equal one; none of them removes a term from both sides of an equation.

## Where the switch picture stops holding

**A contact network has no direction and no gain.** Current flows through a closed
contact either way, and the output of one network is a piece of wire connected to the
input of the next, not a fresh signal. So networks do not compose: join two of them
and you may create a **sneak path**, a route through the second network backwards into
the first that completes a circuit nobody drew. Relay panels are full of blocking
diodes for exactly this reason. A logic gate has a direction and a fresh output, which
is why a million of them can be cascaded and a hundred relays cannot.

**The resistances have to stay far apart.** Every number above rests on the closed
contact being tiny compared with the load and the open one being enormous. Put a 4.7 kΩ
load behind a contact that has corroded to 4 kΩ and the HIGH lands at 2.7 V, in the
forbidden band, where the receiving gate is entitled to read either answer. The algebra
does not warn you about this, because the algebra has already assumed it away.

**And a contact network computes one output.** Ask for a second output of the same
inputs and you need a second network, with its own contacts. Gates share: one gate's
output can drive twenty inputs. That difference is why the rest of this course talks
about gates, and why the algebra — which survives the change completely intact — is the
part worth carrying forward.
''',
                },
                {
                    "title": "The table is the whole story",
                    "minutes": 11,
                    "body": r'''
A Boolean function of $n$ inputs is a rule that assigns a 0 or a 1 to every
combination of those inputs. That definition sounds too weak to be useful, but it has
a consequence that decides how the rest of this course is done: since there are only
finitely many combinations, you can simply **list them all**, and the list is the
function. Not a description of it, not a model of it — the function itself. Anything
you can ask about the function is answerable by reading the list.

That list is the **truth table**.

## Writing one down

The rows are the input combinations, and there is one row per combination. Since each
input independently takes two values, $n$ inputs give $2^n$ rows — the same doubling
that gave $2^n$ patterns to an $n$-bit number in module 1, and for the identical
reason. The convention is to write the rows in counting order, treating the input
pattern as a binary number, so a three-input table runs 000, 001, 010, 011, 100, 101,
110, 111. Following the convention is worth doing even though nothing depends on it,
because two tables in the same order can be compared column against column by eye.

Here is $F = AB + C'$ written out, with the intermediate columns kept so the arithmetic
is visible:

```
  A  B  C  |  A·B   C'  |  F = A·B + C'
  ---------+------------+---------------
  0  0  0  |   0     1  |       1
  0  0  1  |   0     0  |       0
  0  1  0  |   0     1  |       1
  0  1  1  |   0     0  |       0
  1  0  0  |   0     1  |       1
  1  0  1  |   0     0  |       0
  1  1  0  |   1     1  |       1
  1  1  1  |   1     0  |       1
```

Five of the eight rows are 1. Note the last two rows: the row 110 is 1 for two separate
reasons at once, and the row 111 is 1 because $A \cdot B$ is, even though $C'$ is 0. OR
does not care how many of its inputs are true.

## Why the table settles arguments

Two expressions that produce the same output column *are the same function*. There is
nothing else a function could be, since the table is all of it. This makes the table a
decision procedure: any claimed identity in this algebra can be checked by writing out
both sides and comparing columns, and the check always terminates.

Compare that with ordinary algebra, where $\sin^2 x + \cos^2 x = 1$ cannot be settled by
trying values because there are infinitely many of them. Here, eight rows is the whole
of the universe for a three-variable claim.

### Worked: is $A(B + C)$ really $AB + AC$?

```
  A  B  C  |  B+C   A·(B+C)  |  A·B   A·C   A·B + A·C
  ---------+-----------------+-------------------------
  0  0  0  |   0       0     |   0     0        0
  0  0  1  |   1       0     |   0     0        0
  0  1  0  |   1       0     |   0     0        0
  0  1  1  |   1       0     |   0     0        0
  1  0  0  |   0       0     |   0     0        0
  1  0  1  |   1       1     |   0     1        1
  1  1  0  |   1       1     |   1     0        1
  1  1  1  |   1       1     |   1     1        1
```

Both output columns read 0 0 0 0 0 1 1 1. Settled, with no cleverness required. AND
distributes over OR, exactly as multiplication distributes over addition.

### Worked: the law arithmetic does not have

Now try the mirror-image claim, $A + BC = (A + B)(A + C)$. In arithmetic it is
nonsense — $2 + 3 \times 4 = 14$ while $(2+3)(2+4) = 30$. In Boolean algebra:

```
  A  B  C  |  B·C   A + B·C  |  A+B   A+C   (A+B)·(A+C)
  ---------+-----------------+---------------------------
  0  0  0  |   0       0     |   0     0         0
  0  0  1  |   0       0     |   0     1         0
  0  1  0  |   0       0     |   1     0         0
  0  1  1  |   1       1     |   1     1         1
  1  0  0  |   0       1     |   1     1         1
  1  0  1  |   0       1     |   1     1         1
  1  1  0  |   0       1     |   1     1         1
  1  1  1  |   1       1     |   1     1         1
```

Both columns read 0 0 0 1 1 1 1 1. It holds. This is the first sign that Boolean
algebra is not merely arithmetic with small numbers: it is *more* symmetric than
arithmetic, and that extra symmetry is the duality principle you will use constantly —
swap every AND for an OR and every 0 for a 1 in a true statement and you get another
true statement.

## De Morgan, and the row that decides it

The claim is $(A + B)' = A' \cdot B'$: *not either of them* means *neither of them*.
The tempting alternative is $(A + B)' = A' + B'$, and the temptation comes from the
complement looking like a minus sign being distributed over a bracket. One row is
enough to kill it. Take $A = 1$, $B = 0$:

```
  (A + B)'  =  (1 + 0)'  =  1'  =  0
  A' + B'   =   0  + 1   =  1
```

0 against 1, so the two are different functions and the argument is over. Doing it
properly across all four rows shows what the wrong version *is* the answer to:

```
  A  B  |  A+B  (A+B)'  |  A'  B'  |  A'·B'   A'+B'  |  A·B  (A·B)'
  ------+---------------+----------+-----------------+--------------
  0  0  |   0      1    |  1   1   |    1       1    |   0      1
  0  1  |   1      0    |  1   0   |    0       1    |   0      1
  1  0  |   1      0    |  0   1   |    0       1    |   0      1
  1  1  |   1      0    |  0   0   |    0       0    |   1      0
```

$(A+B)'$ reads 1 0 0 0 and so does $A'B'$. Meanwhile $A' + B'$ reads 1 1 1 0, which is
the column of $(AB)'$ — the *other* De Morgan law. So the wrong answer is not random
nonsense; it is the right answer to the other question, which is precisely why it feels
plausible.

### Worked: De Morgan on a specification

A machine may start only if the guard is closed **and** the reset button has been
pressed. Write $G$ and $R$ for those two conditions, so the permissive is $G \cdot R$.
Now wire the STOP line, which must be asserted when the machine may *not* start:

$$\text{STOP} = (G \cdot R)' = G' + R'$$

In words: stop if the guard is open **or** reset has not been pressed. Read that back
into module 1's copper and it is the physical De Morgan: an AND of two make contacts in
series becomes an OR of two break contacts in parallel. Safety circuits are wired the
second way on purpose — a broken wire in a parallel break-contact network reads as
"stop", while a broken wire in a series make-contact network reads as "keep running".
The algebra says the two are the same function; the failure modes say they are not the
same circuit, and that difference is not something a truth table can see.

## How many functions are there?

Since a table is $2^n$ rows and the output column is one free bit per row, the number
of distinct functions of $n$ variables is $2$ raised to the number of rows:

```
   n     rows = 2^n     functions = 2^(2^n)
   1          2                          4
   2          4                         16
   3          8                        256
   4         16                     65 536
   5         32              4 294 967 296
   6         64        about 1.8 x 10^19
```

Sixteen functions of two variables, and only a handful of them have names: the constant
0, AND, XOR, OR, NOR, XNOR, NAND, the constant 1, the two projections $A$ and $B$, the
two complements, and four lopsided ones like $A' + B$ that logicians call implication.
That is the complete inventory — there is no seventeenth two-input gate waiting to be
invented, and knowing the count is what tells you so.

The count is also a piece of hardware. An FPGA's basic cell is a **4-input lookup
table**: sixteen memory bits, addressed by the four inputs, output whatever bit is
selected. Writing the output column of a truth table into those sixteen bits configures
the cell as that function, and since the sixteen bits can be anything, one cell can be
any of the 65 536 functions of four variables. Module 6 builds the same trick out of a
multiplexer, and module 10 uses it.

## Where the table stops being useful

**It grows as $2^n$.** Ten inputs is 1024 rows, which is a spreadsheet. Twenty is a
million, which is a file. Sixty-four inputs is $1.8 \times 10^{19}$ rows, which is more
rows than a machine could enumerate if it had been running since the formation of the
Earth. A 64-bit adder is a perfectly ordinary circuit with 129 inputs, and its truth
table does not exist in any physical sense. So the table remains the *definition* of
what a function is while ceasing to be a usable *representation* of one, and the
industry answer is to work with structures that are compact for the functions people
actually build — binary decision diagrams, and SAT solvers that search for a satisfying
row without listing the others.

**And a table says nothing about time.** It tells you what the output is once the
inputs have settled and the circuit has caught up. It has no vocabulary for the
nanosecond after an input changes, when different paths through the logic are arriving
at different moments and the output can show a value that appears in no row of the
table at all. Two circuits with identical tables can differ in exactly that way; one
**glitches** and the other does not. Module 6 meets the phenomenon and module 4 explains
why a synchronous design can afford to ignore it — because nothing looks at the output
until the clock edge, by which time the table is telling the truth again.
''',
                },
                {
                    "title": "Doing the algebra: moves, names, and knowing when to stop",
                    "minutes": 10,
                    "body": r'''
A truth table always works and always terminates, which makes it the right tool for
settling a question. It is the wrong tool for *building* something, because it gives
you $2^n$ rows and no idea which gates to buy. For that you manipulate the expression,
and manipulating expressions means knowing which moves are legal.

## The moves, sorted by whether arithmetic has them

Some of the laws are the ones you already use without thinking. These behave exactly as
they do with numbers:

$$A + B = B + A \qquad AB = BA \qquad (A+B)+C = A+(B+C) \qquad A(B+C) = AB + AC$$

Some are the two-valued special cases, and they have no arithmetic counterpart because
arithmetic has more than two values to work with:

$$A + A = A \qquad AA = A \qquad A + A' = 1 \qquad AA' = 0 \qquad A + 1 = 1 \qquad A \cdot 0 = 0$$

And one is the genuine surprise, established row by row in the previous reading:

$$A + BC = (A+B)(A+C)$$

OR distributes over AND. The consequence is **duality**: take any true statement, swap
every $+$ for a $\cdot$, every $\cdot$ for a $+$, every 0 for a 1 and every 1 for a 0,
and the result is also true. $A + 0 = A$ becomes $A \cdot 1 = A$. $A + A' = 1$ becomes
$AA' = 0$. Absorption $A + AB = A$ becomes $A(A + B) = A$. This halves how much there is
to remember, and it is a genuine theorem rather than a mnemonic — it follows from the
fact that every axiom of the algebra comes in a dual pair.

Two more that earn their names by how often they turn up:

* **Absorption**: $A + AB = A$, and its dual $A(A + B) = A$.
* **The one that is not absorption**: $A + A'B = A + B$. The prime changes everything.
  When $A$ is 1 the whole expression is 1 either way; when $A$ is 0, $A'B$ reduces to
  $B$. So the $A'$ is doing no work and can simply be dropped — but the $B$ stays.
  Confusing this with absorption, and deleting the whole term, is the single most
  common slip in the subject.

## Worked: the carry-out of a full adder

Here is a function that arrives from module 3 and that you will build for real. An
adder stage takes three bits in and produces a carry out whenever at least two of them
are 1. Written straight off the truth table, one term per row that is 1:

$$F = A'BC + AB'C + ABC' + ABC$$

Four terms of three literals each. The trick is that the last term is allowed to be
used more than once, because $X + X = X$ means you may write $ABC$ down as many times
as you find convenient:

```
  F = A'BC + AB'C + ABC' + ABC

    = A'BC + ABC  +  AB'C + ABC  +  ABC' + ABC        idempotence: ABC = ABC + ABC + ABC
    = BC(A' + A)  +  AC(B' + B)  +  AB(C' + C)        distribution, three times
    = BC·1        +  AC·1        +  AB·1              complement: X + X' = 1
    = BC + AC + AB                                    identity: X·1 = X
```

Twelve literals became six, and four three-input ANDs became three two-input ones.
Read the answer back in English and it is obviously right: the carry is 1 when any two
of the three inputs are 1, and $AB + BC + AC$ says exactly that, once each.

## Worked: an expression that grew by accretion

The second example is the kind of thing that comes out of a specification written by
three people:

```
  X = A·B + A·(B + C) + B·(B + C)

    = AB + AB + AC + BB + BC          distribution, twice
    = AB + AC + B + BC                idempotence AB + AB = AB, and B·B = B
    = AB + AC + B                     absorption: B + BC = B
    = B + AC                          absorption: B + AB = B
```

From six literals across three terms down to three literals across two, and one of the
original inputs turns out not to need a gate at all. Every step is one named law
applied once; if a step ever needs two, write it as two, because a step you cannot name
is a step you cannot check.

Notice which absorption was used at each point, since this is where slips happen. The
third line uses $B + BC = B$ — no primes anywhere, so the whole $BC$ term goes. The
fourth uses $B + AB = B$ for the same reason. Had the term been $B + B'C$ the answer
would have been $B + C$, and deleting it would have thrown away a real dependence on
$C$.

## The mistakes worth naming

**Cancelling.** Ordinary algebra lets you subtract the same thing from both sides. This
algebra has no subtraction, so you cannot. Concretely: $A + AB = A$ and $A + 0 = A$, so
$A + AB = A + 0$; cancelling the $A$ would give $AB = 0$, which is false whenever both
are 1. The same applies to division — there is no $A/B$ — and to "taking a term over to
the other side". The only legal move is to rewrite one expression as an equal one.

**Precedence.** $A + BC$ is $A$ OR ($B$ AND $C$), not ($A$ OR $B$) AND $C$. The
convention is exactly the one arithmetic uses, and the reason it survives here is that
AND really does behave like multiplication. When in doubt, bracket; a redundant pair of
brackets has never cost anybody anything, and the two readings above are different
functions — check them on the row $A = 1$, $B = 0$, $C = 0$, where the first is 1 and
the second is 0.

**Distributing a complement.** $(A + B)'$ is not $A' + B'$, and $(AB)'$ is not $A'B'$.
The bar over a whole expression is not a minus sign in front of a bracket. Push it
inwards one operator at a time with De Morgan, flipping the operator each time it
passes one, and check the result on a row before trusting it.

## Where the algebra stops holding

**It can verify, but it cannot find.** Every move above rewrites an expression into an
equal one, so if you arrive somewhere you know you are still correct. What no rule
tells you is *which* move to make next, or whether the expression in front of you is as
small as it gets. There is no procedure hidden in the identities. In the worked example
above, the step that made it work was writing $ABC$ down three times — that is,
deliberately making the expression *bigger* first, which no rule would ever suggest and
which you do only because you have seen it done.

This is not a small gap. It is the reason module 3 exists: a Karnaugh map does the same
job **visually**, by drawing the table so that terms differing in one variable end up
next to each other, and then the reduction is a matter of circling blocks rather than
of inspiration. For more variables than a map can hold there is the Quine–McCluskey
procedure, which is guaranteed to find a minimal form and is worth knowing exists —
though the problem it solves is one of the hard ones, and for large functions the tools
settle for good rather than best.

**And "smallest expression" is not the real target anyway.** Counting literals is a
proxy. What a chip pays for is transistors, wire, and the delay of the longest path,
and those do not track literal count reliably. A two-level sum-of-products form is the
fastest arrangement and often the most expensive one; a factored form like $A(B + C)$
uses fewer transistors than $AB + AC$ and takes an extra gate delay to settle. Module 5
puts numbers on that trade. The algebra of this module is what lets you move between
the two forms with confidence that you have not changed what the circuit computes —
which is exactly the guarantee you need before you can go looking for the cheapest one.
''',
                },
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
            "blanks": [
                {
                    "title": "De Morgan, settled by exhaustion",
                    "minutes": 9,
                    "caption": "four rows, six columns, and no argument left to have",
                    "lang": "text",
                    "brief": r'''
Two expressions with the same output column are the same function — that is the whole
authority a truth table has, and it is enough to settle any claim in this algebra by
writing the claim out.

Below are the four rows of two variables and every column De Morgan touches. Fill in
the gaps, then read the two output columns down and see which ones match.
''',
                    "listing": """the four rows of two variables, and every column De Morgan needs

  A  B  |  A+B  (A+B)'  |  A'  B'  |  A'·B'   A'+B'
  ------+---------------+----------+-----------------
  0  0  |   0      1    |  1   1   |    1       1
  0  1  |   1      0    |  1   0   |   ___      1
  1  0  |   1     ___   |  0   1   |    0       1
  1  1  |  ___     0    |  0   0   |    0      ___

  reading downwards,  (A+B)'  is   1 0 0 0
  and the only other column that reads 1 0 0 0 is   ___

  reading downwards,  A'+B'   is   1 1 1 0
  which is the column of   ___
""",
                    "blanks": [
                        {
                            "prompt": "Row `A = 0, B = 1`. There $A' = 1$ and $B' = 0$, so what is $A' \\cdot B'$?",
                            "hole": "?",
                            "opts": ["0", "1"],
                            "a": 0,
                            "why": "AND needs both of its inputs to be 1, and $B'$ is 0 on this row because "
                                   "$B$ is 1. So $1 \\cdot 0 = 0$. This is the row that separates $A'B'$ from "
                                   "$A' + B'$, which is 1 here — one row is all it takes for two expressions "
                                   "to be different functions.",
                        },
                        {
                            "prompt": "Row `A = 1, B = 0`. There $A + B = 1$, so what is $(A + B)'$?",
                            "hole": "?",
                            "opts": ["0", "1"],
                            "a": 0,
                            "why": "The complement of 1 is 0. Every row except the first has $A + B = 1$, so "
                                   "$(A+B)'$ is 0 on all three of them — the OR is 1 as soon as anything is, "
                                   "and its complement is correspondingly hard to satisfy.",
                        },
                        {
                            "prompt": "Row `A = 1, B = 1`. What is $A + B$?",
                            "hole": "?",
                            "opts": ["0", "1"],
                            "a": 1,
                            "why": "$1 + 1 = 1$. OR asks whether *at least one* input is 1 and does not count "
                                   "how many. Reading this as binary addition and writing 10 is the standard "
                                   "collision between the two notations in this course: here the symbols are "
                                   "truth values on one wire, and one wire has no room for a carry.",
                        },
                        {
                            "prompt": "Row `A = 1, B = 1`. There $A' = 0$ and $B' = 0$, so what is $A' + B'$?",
                            "hole": "?",
                            "opts": ["0", "1"],
                            "a": 0,
                            "why": "OR of two zeros is 0 — this is the one row where $A' + B'$ fails, which "
                                   "makes its column 1 1 1 0. Compare $A' \\cdot B'$, which is 0 on three rows "
                                   "and 1 only on the first. The two expressions differ on two of the four "
                                   "rows, so they are nowhere near the same function.",
                        },
                        {
                            "prompt": "Which column also reads 1 0 0 0 downwards?",
                            "hole": "?",
                            "opts": ["A'·B'", "A'+B'", "A·B", "A+B"],
                            "a": 0,
                            "why": "$A' \\cdot B'$ is 1 only on the row where both variables are 0, and that is "
                                   "exactly when $A + B$ is 0. So $(A+B)' = A'B'$ — De Morgan, proved by "
                                   "comparing columns. $A' + B'$ reads 1 1 1 0 and $A \\cdot B$ reads 0 0 0 1, "
                                   "and $A + B$ reads 0 1 1 1, which is what was complemented in the first "
                                   "place.",
                        },
                        {
                            "prompt": "The column 1 1 1 0 is the table of which expression?",
                            "hole": "?",
                            "opts": ["(A·B)'", "(A+B)'", "A·B", "A ⊕ B"],
                            "a": 0,
                            "why": "$A \\cdot B$ is 1 only on the last row, so its complement is 1 on the first "
                                   "three — the column 1 1 1 0, which is what $A' + B'$ reads. That is the "
                                   "second De Morgan law, $(AB)' = A' + B'$, and it is why writing "
                                   "$(A+B)' = A' + B'$ feels plausible: it is the correct answer to the other "
                                   "question. $(A+B)'$ reads 1 0 0 0, and $A \\oplus B$ reads 0 1 1 0.",
                        },
                    ],
                },
                {
                    "title": "Four moves, and the name of each one",
                    "minutes": 9,
                    "caption": "a simplification with the working shown and the laws blanked out",
                    "lang": "text",
                    "brief": r'''
A simplification you cannot name step by step is a simplification you cannot check. The
chain below is correct — each line follows from the one above it by exactly one law —
but the names have been taken off.

Put them back. The expression is the one a two-input function arrives as when it is
written straight off its truth table.
''',
                    "listing": """simplify  F = A·B + A·B' + A'·B

  F  =  A·B  +  A·B'  +  A'·B

     =  A·(B + B')  +  A'·B            ___

     =  A·1  +  A'·B                   ___

     =  A  +  A'·B                     ___

     =  A  +  B                        ___

  three AND terms and two ORs became one OR of two variables
""",
                    "blanks": [
                        {
                            "prompt": "$A \\cdot B + A \\cdot B'$ became $A \\cdot (B + B')$. Which law is that?",
                            "hole": "?",
                            "opts": [
                                "absorption — A + A·B = A",
                                "distribution — the A common to both terms comes outside the bracket",
                                "De Morgan — a complement moves inwards and flips the operator",
                                "idempotence — A + A = A",
                            ],
                            "a": 1,
                            "why": "This is $AB + AC = A(B + C)$ read right to left, with $C = B'$. It is the "
                                   "same factoring move as taking $x$ out of $3x + 2x$, and it is the one law "
                                   "shared with arithmetic that does real work here. Absorption would delete a "
                                   "term rather than rearrange two; De Morgan needs a complement over a whole "
                                   "bracket, and there is none; idempotence needs two identical terms, and "
                                   "$AB$ and $AB'$ differ.",
                        },
                        {
                            "prompt": "$B + B'$ became 1. Which law is that?",
                            "hole": "?",
                            "opts": [
                                "null — B + 1 = 1",
                                "identity — B + 0 = B",
                                "complement — B + B' = 1, since one of the two must be true",
                                "idempotence — B + B = B",
                            ],
                            "a": 2,
                            "why": "A variable and its complement cannot both be 0, so their OR is 1 whatever "
                                   "$B$ does — in switches, a make contact and a break contact of the same "
                                   "relay wired side by side are a piece of wire. The null law is about ORing "
                                   "with a constant 1, which is not what is on the line; identity is about "
                                   "ORing with 0; idempotence needs the same term twice, not a term and its "
                                   "complement.",
                        },
                        {
                            "prompt": "$A \\cdot 1$ became $A$. Which law is that?",
                            "hole": "?",
                            "opts": [
                                "identity — A·1 = A",
                                "null — A·0 = 0",
                                "complement — A·A' = 0",
                                "absorption — A·(A + B) = A",
                            ],
                            "a": 0,
                            "why": "1 is the element that leaves an AND alone, the way 1 leaves a "
                                   "multiplication alone: a permanently closed switch in series with $A$ is "
                                   "just $A$. Its dual is $A + 0 = A$. The null law is the other constant, "
                                   "$A \\cdot 0 = 0$, a permanently open switch that kills the path; the "
                                   "complement law needs an $A'$, and absorption needs a bracket containing "
                                   "$A$ itself.",
                        },
                        {
                            "prompt": "$A + A' \\cdot B$ became $A + B$. Which law is that?",
                            "hole": "?",
                            "opts": [
                                "absorption — A + A·B = A, so the second term simply goes",
                                "idempotence — A + A = A",
                                "A + A'·B = A + B — the A' is doing no work, but the B stays",
                                "De Morgan — (A·B)' = A' + B'",
                            ],
                            "a": 2,
                            "why": "When $A$ is 1 the expression is 1 whatever the second term says; when $A$ "
                                   "is 0, $A'B$ is just $B$. So the $A'$ can be dropped and the $B$ cannot. "
                                   "The formal route is $A + A'B = (A + A')(A + B) = 1 \\cdot (A + B)$, using "
                                   "the law that OR distributes over AND. Reading it as absorption and "
                                   "deleting the whole term gives $F = A$, which is wrong on the row "
                                   "$A = 0, B = 1$ — and that confusion between $A + AB$ and $A + A'B$ is the "
                                   "most common error in the subject.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Counting the ones",
                    "minutes": 5,
                    "brief": r'''
One rule, applied eight times. Write the rows out in counting order, work the
expression on each, and count.

Nothing here needs algebra. The only thing that can go wrong is losing track of which
rows have already been counted.
''',
                    "prompt": "In how many of the eight rows is $F$ equal to 1?",
                    "note": "Give the answer as a whole number of rows.",
                    "figure": "A function of three variables is given by the expression $F = A \\cdot B + C'$, "
                              "where $C'$ means NOT C. Its truth table has eight rows, one for each "
                              "combination of A, B and C.",
                    "given": [
                        {"label": "Expression", "value": "F = A·B + C'"},
                        {"label": "Variables", "value": "A, B, C"},
                        {"label": "Rows in the table", "value": "8"},
                    ],
                    "aside": "AND binds tighter than OR, so this reads as (A AND B) OR (NOT C), not as "
                             "A AND (B OR NOT C).",
                    "answer": 5.0,
                    "tol": 0.5,
                    "unit": "rows",
                    "hint": "$C'$ is 1 in the four rows where $C = 0$. $A \\cdot B$ is 1 in the two rows where "
                            "both $A$ and $B$ are 1. Now count the rows covered by at least one of those.",
                    "wrong": "If you got 6, the two lists were added: four rows with $C = 0$ plus two rows "
                             "with $A = B = 1$ — but the row 110 is in both lists and must not be counted "
                             "twice. If you got 2, only $A \\cdot B$ was counted and the $C'$ term was "
                             "dropped; if you got 4, only $C'$ was.",
                    "why": "Written out in counting order, $F$ is 1 on the rows 000, 010, 100, 110 and 111 — "
                           "five of the eight. Four of them are the rows where $C = 0$, which make $C'$ true "
                           "on its own; the fifth is 111, where $C'$ is 0 but $A \\cdot B$ is 1. The row 110 "
                           "is 1 for both reasons at once, and OR does not care how many of its inputs are "
                           "true, so it counts once. The three rows where $F$ is 0 are 001, 011 and 101 — "
                           "the rows with $C = 1$ and not both of $A$ and $B$.",
                },
                {
                    "title": "Two contacts in a line",
                    "minutes": 7,
                    "brief": r'''
AND, built out of copper. Two switch contacts in series feed the input of a logic gate,
and a 4.7 kΩ resistor holds that input near ground when the contacts are open.

Both contacts here are closed, but neither is a perfect short: a switch that has been
in a panel for a few years has ohms of contact resistance rather than milliohms. The
two drawn are 120 Ω and 180 Ω.

Read off the node the probe is sitting on.
''',
                    "prompt": "What voltage does the gate input settle at?",
                    "note": "Give the answer in volts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "ra", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                            {"id": "rb", "kind": "R", "x": 12, "y": 3, "rot": 0, "value": 180},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 3},
                            {"id": "rl", "kind": "R", "x": 15, "y": 5, "rot": 1, "value": 4700},
                            {"id": "g1", "kind": "GND", "x": 15, "y": 8},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [11, 3]},
                            {"a": [13, 3], "b": [15, 3]},
                            {"a": [15, 3], "b": [15, 4]},
                            {"a": [15, 6], "b": [15, 8]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "Contact A (closed)", "value": "120 Ω"},
                        {"label": "Contact B (closed)", "value": "180 Ω"},
                        {"label": "Pull-down at the gate input", "value": "4.7 kΩ"},
                    ],
                    "aside": "Three resistors in one line between the rail and ground. The probed node "
                             "sits at the rail times the share of the total resistance that lies below it.",
                    "answer": 4.7,
                    "tol": 0.01,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "Add the two contacts to the pull-down to get the total, then $V = 5 \\times "
                            "4700/R_{\\text{total}}$.",
                    "wrong": "If you got 5.00 V, the contact resistances were treated as perfect shorts — "
                             "which is the idealisation the algebra makes, and it is nearly right here, but "
                             "the question asks what the circuit does. If you got 0.30 V or thereabouts, the "
                             "divider was taken the wrong way up: the probe is above the pull-down, not "
                             "across the contacts.",
                    "why": "The three resistances are in series, so they add: $120 + 180 + 4700 = 5000$ Ω. "
                           "The current is $5/5000 = 1.000$ mA, and the drop across the pull-down is "
                           "$1.000\\,\\text{mA} \\times 4.7\\,\\text{k}\\Omega = 4.700$ V. The two contacts "
                           "between them lose $0.300$ V, which is 6 % of the rail and of no consequence: a "
                           "5 V CMOS input reads anything above $0.7 \\times 5 = 3.5$ V as HIGH, so this "
                           "arrives with 1.2 V of margin. Open either contact — swap its 120 Ω or 180 Ω for "
                           "the megohm of an air gap — and the same divider delivers about 23 mV, a solid "
                           "LOW. Series is AND, and here is the AND table in volts.",
                },
                {
                    "title": "Which branch of the OR carries what",
                    "minutes": 9,
                    "brief": r'''
OR, built out of copper: the same two contacts side by side instead of in a line, so
either one closing pulls the gate input up.

Both are closed this time, but they are not equal — one is a clean 120 Ω and the other
has aged to 360 Ω. The question is not about the node they share. It asks what the
**higher-resistance** contact is actually carrying, which means finding the node
voltage first and then coming back to one branch.
''',
                    "prompt": "What current flows through the 360 Ω contact?",
                    "note": "Give the answer in microamps, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "ra", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                            {"id": "rb", "kind": "R", "x": 6, "y": 7, "rot": 0, "value": 360},
                            {"id": "rl", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 4700},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 13, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [5, 3], "b": [5, 7]},
                            {"a": [7, 3], "b": [11, 3]},
                            {"a": [7, 7], "b": [11, 7]},
                            {"a": [11, 3], "b": [11, 9]},
                            {"a": [11, 11], "b": [11, 13]},
                            {"a": [11, 3], "b": [13, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "Contact A (closed, clean)", "value": "120 Ω"},
                        {"label": "Contact B (closed, aged)", "value": "360 Ω"},
                        {"label": "Pull-down at the gate input", "value": "4.7 kΩ"},
                    ],
                    "aside": "Two resistors in parallel combine to $R_1 R_2/(R_1 + R_2)$. Once you have the "
                             "voltage across the pair, each branch is one resistor with a known voltage at "
                             "each end.",
                    "answer": 261.0,
                    "tol": 2.0,
                    "unit": "µA",
                    "check": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const rail = src.n1;
const contacts = c.net.parts.filter(function (p) {
  return p.kind === 'R' && (p.n1 === rail || p.n2 === rail);
});
const aged = contacts.reduce(function (a, b) { return b.value > a.value ? b : a; });
const d = c.dc();
return Math.abs(d.v[aged.n1] - d.v[aged.n2]) / aged.value * 1e6;
''',
                    "hint": "The parallel pair is $120 \\times 360/480 = 90$ Ω, so the whole path is "
                            "$90 + 4700 = 4790$ Ω. Find the total current, then the voltage across the 90 Ω, "
                            "then divide that by 360 Ω.",
                    "wrong": "If you got 522 µA, the total current was split evenly between the two "
                             "branches — but they are not equal resistances, and the smaller one takes "
                             "three times as much. If you got 13.9 mA, the whole 5 V was dropped across the "
                             "360 Ω, forgetting that almost all of the rail lands on the 4.7 kΩ pull-down.",
                    "why": "The two contacts in parallel are $120 \\times 360/(120 + 360) = 43200/480 = 90$ Ω, "
                           "so the total path is $90 + 4700 = 4790$ Ω and the supply delivers "
                           "$5/4790 = 1.044$ mA. That current across the 90 Ω leaves "
                           "$1.044\\,\\text{mA} \\times 90\\,\\Omega = 93.9$ mV, which is the voltage across "
                           "*both* contacts, since parallel parts share their end nodes. So the aged branch "
                           "carries $93.9\\,\\text{mV}/360\\,\\Omega = 261$ µA and the clean one carries "
                           "$93.9\\,\\text{mV}/120\\,\\Omega = 783$ µA, and the two add back to the 1.044 mA "
                           "the rail supplied. Notice what the algebra never mentions: the two branches "
                           "carry a 3:1 split, and OR does not care in the slightest — the node lands at "
                           "4.906 V and is read as a 1 either way.",
                },
                {
                    "title": "A·(B + C), and the power it burns",
                    "minutes": 12,
                    "brief": r'''
A network with all three operations in it. Contact A is in series with the pair B and
C, which are in parallel, so the gate input goes HIGH only when A is closed **and** at
least one of B and C is — that is $F = A \cdot (B + C)$.

The state drawn is A closed at 120 Ω, B **open**, and C closed at 360 Ω. An open
contact is not an infinite resistance: a real air gap with a film of grime on it is
around 1 MΩ, which is what B is drawn as.

The question asks for the power in the pull-down. That is not a node voltage and not a
current, so there are two steps after the network resistance: find the voltage across
the pull-down, then square it.
''',
                    "prompt": "How much power is dissipated in the 4.7 kΩ pull-down?",
                    "note": "Give the answer in milliwatts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "ra", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                            {"id": "rb", "kind": "R", "x": 10, "y": 3, "rot": 0, "value": 1000000},
                            {"id": "rc", "kind": "R", "x": 10, "y": 7, "rot": 0, "value": 360},
                            {"id": "rl", "kind": "R", "x": 15, "y": 10, "rot": 1, "value": 4700},
                            {"id": "g1", "kind": "GND", "x": 15, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 17, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [9, 7]},
                            {"a": [11, 3], "b": [15, 3]},
                            {"a": [11, 7], "b": [15, 7]},
                            {"a": [15, 3], "b": [15, 9]},
                            {"a": [15, 11], "b": [15, 13]},
                            {"a": [15, 3], "b": [17, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "Contact A (closed)", "value": "120 Ω"},
                        {"label": "Contact B (open)", "value": "1 MΩ"},
                        {"label": "Contact C (closed)", "value": "360 Ω"},
                        {"label": "Pull-down at the gate input", "value": "4.7 kΩ"},
                    ],
                    "aside": "$P = V^2/R$ for a resistor, where $V$ is the voltage across that resistor "
                             "alone — not the rail.",
                    "answer": 4.379,
                    "tol": 0.02,
                    "unit": "mW",
                    "check": r'''
const load = c.net.parts.filter(function (p) {
  return p.kind === 'R' && (p.n1 === 0 || p.n2 === 0);
})[0];
const d = c.dc();
const v = Math.abs(d.v[load.n1] - d.v[load.n2]);
return v * v / load.value * 1000;
''',
                    "hint": "Combine B and C in parallel first, add A and the pull-down in series, find the "
                            "current, then the pull-down's own voltage, then $V^2/R$.",
                    "wrong": "If you got 5.32 mW, the whole 5 V was squared and divided by 4.7 kΩ, which "
                             "ignores the 0.463 V lost in the contacts. If you got 4.54 mW, the *voltage* "
                             "across the pull-down was reported rather than the power in it.",
                    "why": "B and C in parallel are $1\\,\\text{M} \\times 360/(1\\,\\text{M} + 360) = 359.87$ "
                           "Ω — a megohm in parallel with 360 Ω is 360 Ω for any purpose you care about, "
                           "which is the electrical statement of $B + C = C$ when $B$ is 0. Adding A and "
                           "the pull-down: $120 + 359.87 + 4700 = 5179.9$ Ω, so the supply delivers "
                           "$5/5179.9 = 965.3$ µA. The pull-down therefore has "
                           "$965.3\\,\\mu\\text{A} \\times 4700\\,\\Omega = 4.537$ V across it, and "
                           "$P = V^2/R = 4.537^2/4700 = 4.379$ mW. Two things worth noticing. The open "
                           "contact is carrying real current — 0.347 V across it divided by 1 MΩ is 347 nA, "
                           "small but not zero, and it is exactly this kind of leakage that makes a floating "
                           "CMOS input drift to somewhere unhelpful. And closing B as well moves the "
                           "answer very little: at 120 Ω, the same as A, the parallel pair falls to 90 Ω, "
                           "the total to 4910 Ω, the current to 1.018 mA and the power to 4.874 mW. The "
                           "algebra insists that $C$ and $B + C$ are different functions, and they are; "
                           "but the volts read 4.537 V against 4.786 V, both of them a HIGH by more than "
                           "a volt, which is why the two-valued reading is the useful one.",
                },
            ],
            "derive": {
                "title": "How many functions are there, and how big is the table",
                "minutes": 13,
                "vars": ["n", "R", "N", "m", "S"],
                "brief": r'''
A truth table is a complete specification, so *counting tables is counting functions*.
That turns a vague question — how much can a block of logic possibly do? — into
arithmetic you can finish in four lines.

Take a function of $n$ inputs with a single output. Write $R$ for the number of rows in
its table and $N$ for the number of distinct functions of $n$ inputs there are.

Two facts are all you need: each input independently takes two values, and each row's
output is one bit that may be chosen without reference to any other row.
''',
                "steps": [
                    {
                        "prompt": "The table has one row per combination of the inputs, and each of the $n$ inputs independently takes two values. Write the number of rows $R$ in terms of $n$.",
                        "answer": "2^{n}",
                        "hint": "One input gives two rows; adding an input doubles the count, because every row you had appears once with the new input at 0 and once at 1.",
                        "deconstruct": [
                            "With one input there are 2 rows, with two inputs 4, with three 8.",
                            "Each extra input doubles the count, so $n$ inputs give $2 \\times 2 \\times \\cdots$, $n$ times.",
                        ],
                    },
                    {
                        "prompt": "The table is fixed once its output column is fixed, and that column is $R$ bits chosen freely. Write the number of distinct output columns $N$ in terms of $R$.",
                        "answer": "2^{R}",
                        "hint": "This is the same counting question again with a different name on it: $R$ independent binary choices.",
                        "deconstruct": [
                            "Each row's output is one bit, so it can be filled in 2 ways.",
                            "The rows are independent, so the ways multiply: $2^R$ columns in all.",
                        ],
                    },
                    {
                        "prompt": "Substitute the first result into the second to get $N$ in terms of $n$ alone.",
                        "given": "$R = 2^{n}$ and $N = 2^{R}$",
                        "answer": "2^{2^{n}}",
                        "placeholder": "2^{\\ldots}",
                        "hint": "Put $2^n$ where the $R$ is. The exponent is itself a power of two, so the result is a tower two high.",
                        "deconstruct": [
                            "$N = 2^{R}$ and $R = 2^{n}$, so $N = 2^{(2^{n})}$.",
                            "Read the tower from the top down: $n$ inputs give $2^n$ rows, and $2^n$ rows give $2^{2^n}$ ways of filling them.",
                        ],
                    },
                    {
                        "prompt": "Put $n = 4$ into that and give the number of distinct functions of four variables.",
                        "answer": "65536",
                        "hint": "$2^4 = 16$ rows, and $2^{16}$ is the count you want.",
                        "deconstruct": [
                            "$2^4 = 16$, so the table has 16 rows.",
                            "$2^{16} = 65\\,536$ — which is why an FPGA's 4-input lookup table holds 16 configuration bits and can be made into any one of them.",
                        ],
                    },
                    {
                        "prompt": "A block with $m$ outputs needs one output column per output, each $R$ bits long. Write the total number of bits $S$ needed to write its whole table down, in terms of $m$ and $n$.",
                        "answer": "m \\cdot 2^{n}",
                        "placeholder": "m \\cdot \\ldots",
                        "hint": "One column of $R$ bits per output, and there are $m$ of them.",
                        "deconstruct": [
                            "Each output contributes a column of $R = 2^n$ bits.",
                            "There are $m$ such columns, so $S = m 2^{n}$ bits in total.",
                        ],
                    },
                    {
                        "prompt": "A seven-segment decoder takes a 4-bit number in and drives 7 segment outputs. How many bits is its complete truth table?",
                        "answer": "112",
                        "hint": "$m = 7$ and $n = 4$ in the formula you just wrote.",
                        "deconstruct": [
                            "$2^4 = 16$ rows.",
                            "$7 \\times 16 = 112$ bits — small enough to store outright, which is exactly what a lookup-table implementation does.",
                        ],
                    },
                ],
                "closing": r'''
Two numbers from that are worth keeping. **65 536** is the number of things a 4-input
lookup table can be, and it is why an FPGA cell is built the way it is: rather than
wiring gates, you store the output column and address it with the inputs. **112 bits**
is the entire seven-segment decoder you will build in the capstone, which tells you
before you start that the problem is small.

The third number is the warning. $2^{2^n}$ grows faster than almost anything else you
will meet: 256 functions of three variables, 65 536 of four, and $1.8 \times 10^{19}$
of six. By eight inputs the count exceeds the number of atoms in the observable
universe. So the space of functions is not something anyone searches; it is something
you navigate with structure, which is what the expression notation and the maps of
module 3 are for.

And the $m \cdot 2^n$ bits is why lookup tables lose. A 4-input, 7-output block is 112
bits and fits anywhere. The same idea for a 16-bit adder — 33 inputs, 17 outputs —
would need $17 \times 2^{33}$ bits, about 18 gigabytes, to do a job that 80 gates do in
a corner of a chip. The table is always available and almost never the answer.
''',
            },
            "build": {
                "title": "OR in copper: one closed contact is enough",
                "minutes": 22,
                "brief": r'''
Two contacts, wired so that the gate input goes HIGH when **either** of them is closed.
That is $A + B$, and the wiring that realises it is the two contacts side by side —
in parallel — rather than one after the other.

Contact A is closed and is drawn for you as a 120 Ω resistor. Contact B is **open**,
which is not an infinite resistance: model it as **1 MΩ**, the sort of figure a real
air gap with a little grime on it gives.

Add what is missing:

* the open contact, as a 1 MΩ resistor, wired so that it and the 120 Ω contact bridge
  the *same* gap — both from the rail to the shared output node
* a pull-down resistor from that node to ground, so the input has a defined level when
  both contacts open
* leave the probe on the node the two contacts feed

Two things have to be true of the result:

* the output reads at least **4.40 V**, so the gate downstream sees an unambiguous HIGH
* the rail delivers less than **1 mA**, which is what stops a bank of these from
  costing more current than the logic they feed

There is a range of pull-down values that does both; work out where the two limits are
before you pick one. Wire the two contacts in series instead and the output collapses
to a few millivolts, which is the whole difference between OR and AND in one
measurement.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                        {"id": "p3", "kind": "OUT", "x": 13, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [7, 3], "b": [11, 3]},
                        {"a": [11, 3], "b": [13, 3]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                        {"id": "p3", "kind": "OUT", "x": 13, "y": 3},
                        {"id": "p4", "kind": "R", "x": 6, "y": 7, "rot": 0, "value": 1000000},
                        {"id": "p5", "kind": "R", "x": 11, "y": 10, "rot": 1, "value": 10000},
                        {"id": "p6", "kind": "GND", "x": 11, "y": 13},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [5, 3], "b": [5, 7]},
                        {"a": [7, 3], "b": [11, 3]},
                        {"a": [7, 7], "b": [11, 7]},
                        {"a": [11, 3], "b": [11, 9]},
                        {"a": [11, 11], "b": [11, 13]},
                        {"a": [11, 3], "b": [13, 3]},
                    ],
                },
                "checks": [
                    {"name": "both contacts are on the board, one closed and one open", "code": r'''
var rs = c.values('R');
var closed = rs.filter(function (x) { return Math.abs(x - 120) < 2; });
var open = rs.filter(function (x) { return Math.abs(x - 1e6) < 1e4; });
c.assert(closed.length === 1,
  'Exactly one 120 Ω resistor stands for the closed contact. Found ' + closed.length + '.');
c.assert(open.length === 1,
  'The open contact is a 1 MΩ resistor, not a gap in the drawing — an open switch still ' +
  'leaks, and the point of the exercise is to see how little that matters. Found ' +
  open.length + ' resistor(s) near 1 MΩ.');
'''},
                    {"name": "the probe is on the shared node, not on the rail", "code": r'''
c.assert(c.count('R') >= 3,
  'Three resistors: the two contacts, and a pull-down so the node has a defined level ' +
  'when both contacts open.');
c.assert(Math.abs(c.vout() - 5) > 0.01,
  'The probe is reading the rail itself. Move it to the node the two contacts feed, ' +
  'above the pull-down.');
'''},
                    {"name": "one closed contact is enough — the output is a solid HIGH", "code": r'''
var v = c.vout();
c.assert(v >= 4.40,
  'The output is ' + c.fmt(v, 'V') + ', and it has to be at least 4.40 V. If it is a few ' +
  'millivolts, the two contacts are in series and you have built an AND: the open one is ' +
  'then a megohm in the only path there is. Wire them so each one bridges the gap on its own.');
'''},
                    {"name": "the rail delivers less than 1 mA", "code": r'''
var cur = c.dc().currents;
var mags = Object.keys(cur).map(function (k) { return Math.abs(cur[k]); });
c.assert(mags.length > 0, 'There is no source current to measure — is the rail connected to anything?');
var worst = Math.max.apply(null, mags);
c.assert(worst < 1e-3,
  'The rail is delivering ' + c.fmt(worst, 'A') + '. Raise the pull-down: the current is ' +
  'almost exactly 5 V divided by it, so anything above about 5 kΩ clears 1 mA.');
'''},
                ],
                "hints": [
                    "Parallel means both resistors span the same two nodes: one end of each on the rail, the other end of each on the output node.",
                    "With the 1 MΩ in parallel, the pair is $120 \\times 10^6/(120 + 10^6) = 120.0$ Ω to three figures — the open contact changes nothing measurable, which is the result you are demonstrating.",
                    "The output is $5 \\times R_{\\text{pd}}/(R_{\\text{pd}} + 120)$. For that to reach 4.40 V you need $R_{\\text{pd}}$ above about 880 Ω.",
                    "The rail current is about $5/R_{\\text{pd}}$, so under 1 mA needs $R_{\\text{pd}}$ above 4.9 kΩ. That is the binding constraint; 10 kΩ gives 4.94 V and 0.49 mA and clears both.",
                    "If the output comes out near 5 µV rather than near 5 V, the contacts ended up in series: every electron then has to cross the 1 MΩ.",
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
            "read": [
                {
                    "title": "From a table to a circuit, with nothing left to invent",
                    "minutes": 12,
                    "body": r'''
Module 2 left you able to *check* things. Given an expression you can write its truth
table; given two expressions you can decide whether they are the same function. Neither
of those is design. Design runs the other way. You start with a description of what the
circuit should do — and if you are sensible you turn that description into a table
first, because a table is the one form of a specification that cannot be ambiguous —
and you have to finish with something you could hand to a person holding a bag of
gates.

Nothing so far tells you how to get from a column of 0s and 1s to gates. That gap is
what this module closes, and the surprise is that there is nothing clever in it. There
is a completely mechanical procedure which turns any table whatever into a working
circuit, it takes a minute, and it never fails. What it produces is routinely two or
three times larger than it needs to be — and *that* is where the thinking lives, in the
next reading.

## One wire that is live on exactly one row

Put the algebra down for a moment and think about copper, the way module 2 did.

Give every input variable a relay. A relay has two kinds of contact: a **make** contact,
closed when the relay is energised, and a **break** contact, closed when it is not. Call
the relays A, B and C. A make contact of A is closed exactly when $A = 1$; a break
contact of A is closed exactly when $A = 0$. Between them they let you build a switch
that responds to either polarity of a variable.

Now wire three contacts in series between the supply rail and an output node — one
contact per relay, and for each relay you choose which kind. What does that chain do?

Series means every contact must be closed for anything to get through. So the chain
conducts on exactly one combination of A, B and C: the one in which every relay is in
the state its own contact wants. Choose make-A, break-B, make-C and the chain conducts
when and only when $A = 1$, $B = 0$, $C = 1$ — the row `101`, and none of the other
seven.

That is the whole trick, and it is worth stating on its own line:

> A series chain of one contact per variable is a wire that is live on exactly one row
> of the truth table, and you choose which row by choosing the contacts.

The rest is bookkeeping. To build a function that is 1 on five rows, build five chains,
one per row, and wire all five in parallel between the rail and the same output node.
The output is live if *any* of them conducts — which is to say, exactly when the input
is one of those five rows. The circuit is finished. Nothing about the function mattered
except which rows carried a 1, and there was no step in which you had to be clever.

## The same construction, written down

Series is AND and parallel is OR, and a break contact of A is $A'$. So the chain that
conducts only on `101` is the product $A \cdot B' \cdot C$, and the parallel bundle of
chains is the sum of those products.

A product that contains **every** variable exactly once, complemented where the row has
a 0 and plain where the row has a 1, is called a **minterm**. Reading one off a row is a
substitution done digit by digit: 1 becomes the variable, 0 becomes the variable with a
prime on it. Number the rows in binary counting order and the minterm belonging to row
$i$ is written $m_i$; `101` is row 5, so $A B' C = m_5$.

The OR of the minterms of every row where $F$ is 1 is the **canonical sum of products**,
written $F = \sum m(\ldots)$ with the row numbers in the brackets. Three properties are
worth stating flatly, because together they are why the procedure can be trusted.

* **It always works.** Any table at all, of any size, including tables nobody has found
  a pattern in.
* **It is unique.** Two people who do this to the same table write down the same
  expression, up to the order of the terms.
* **It is almost never the smallest.**

## Worked example 1 — the carry out of an adder

Three bits go in — the two bits being added and the carry coming from the column below
— and the carry out is 1 when the total reaches two. Write the table, and write the
minterm beside every row that carries a 1.

```
 A  B  Cin | Cout | row | minterm
 ----------+------+-----+---------------
 0  0   0  |  0   |  0  |
 0  0   1  |  0   |  1  |
 0  1   0  |  0   |  2  |
 0  1   1  |  1   |  3  |  A' · B  · Cin
 1  0   0  |  0   |  4  |
 1  0   1  |  1   |  5  |  A  · B' · Cin
 1  1   0  |  1   |  6  |  A  · B  · Cin'
 1  1   1  |  1   |  7  |  A  · B  · Cin
```

$$C_{out} = A'BC_{in} + AB'C_{in} + ABC_{in}' + ABC_{in} = \sum m(3,5,6,7)$$

As a circuit: four AND gates of three inputs each, one OR gate of four inputs, and an
inverter on each variable. Twelve literals in all.

Check it on a row it should pass, $A = 1$, $B = 0$, $C_{in} = 1$:

```
 A'·B·Cin    = 0 · 0 · 1 = 0
 A·B'·Cin    = 1 · 1 · 1 = 1     <- the minterm of this very row
 A·B·Cin'    = 1 · 0 · 0 = 0
 A·B·Cin     = 1 · 0 · 1 = 0
 OR of those =  1
```

And on a row it should fail, $A = 1$, $B = 0$, $C_{in} = 0$:

```
 A'·B·Cin    = 0 · 0 · 0 = 0
 A·B'·Cin    = 1 · 1 · 0 = 0
 A·B·Cin'    = 1 · 0 · 1 = 0
 A·B·Cin     = 1 · 0 · 0 = 0
 OR of those =  0
```

At most one term can be 1 at a time, whatever the input. Two different minterms disagree
about some variable, so their product contains both that variable and its complement and
is therefore 0 — the terms cannot both fire. That is what makes the construction airtight
rather than merely plausible: adding a term switches on exactly one row and touches
nothing else, so you can build the expression row by row and never revisit a decision.

## Worked example 2 — going the other way

Specifications rarely arrive as tables. They arrive as sentences that turn into a
shorthand expression, and then you want the table, or you want to compare with somebody
else's expression. Canonical form is the way to do it, because it is a *normal* form:
two expressions are the same function precisely when their canonical forms are
identical.

Take $F = A + B'C$ over the three variables A, B, C. Neither term is a minterm: the
first is missing B and C, the second is missing A. A term missing $k$ of the $n$
variables covers $2^k$ rows, so this expression's two terms will expand to four rows and
two rows respectively.

Expand by multiplying by 1, in the form $(X + X')$, once for each missing variable:

```
A     = A · (B + B') · (C + C')
      = A·B·C  +  A·B·C'  +  A·B'·C  +  A·B'·C'
        row 7     row 6      row 5      row 4

B'·C  = (A + A') · B'·C
      = A·B'·C  +  A'·B'·C
        row 5      row 1
```

Collect the six rows, notice that row 5 was produced twice, and delete the duplicate —
that is idempotence, $X + X = X$, and it is the only step here that is not pure
substitution:

$$F = \sum m(1,4,5,6,7)$$

Sanity check against the words: $F$ is 1 whenever A is 1, which is the top half of the
table, rows 4, 5, 6 and 7; and additionally whenever $B = 0$ and $C = 1$, which is rows
`001` and `101`, numbers 1 and 5. Row 5 satisfies both conditions and is listed once.
Five rows of eight.

Notice the cost. The expression went from 3 literals to 15. Expanding to canonical form
always makes things bigger, and it is still worth doing, because "bigger" is the price
of "comparable".

## The mistake people actually make

It happens on the row-to-minterm step, and it is writing row `101` as $A'BC'$ —
complementing the 1s instead of the 0s.

The reason it is tempting is that the flipped version is not nonsense; it is the
*other* standard construction. Work from the rows where the output is **0** instead, and
each such row contributes a **maxterm**: a sum, not a product, which is 0 on that row
and 1 everywhere else. Row `101` contributes the maxterm $A' + B + C'$ — and there the
primes do go on the 1s. AND the maxterms of all the zero rows together and you have the
canonical **product of sums**, which is just as valid and is the natural form when the
zeros are the rare ones. The two constructions are duals of each other and their primes
run opposite ways, so anybody who has met both without carefully separating them will
eventually write one while meaning the other.

The check takes five seconds and never fails: **substitute the row back into the term
you wrote**. $AB'C$ at $A=1, B=0, C=1$ is $1 \cdot 1 \cdot 1 = 1$. If your term does not
come out as 1 on its own row, it is not that row's minterm.

## Where this stops being the answer

Two limits, one about size and one about time.

**Size.** The construction's cost is set by how many 1s the table has, and tables grow
as $2^n$. Consider a 16-bit equality comparator: 32 inputs, one output, true on the
$2^{16}$ rows where the two halves match. Its canonical sum of products has 65 536 terms
of 32 literals each — a little over two million literals — for a circuit that any
engineer builds with 16 XNOR gates and one AND. The canonical form is a *proof that a
circuit exists*, not a proposal for building one. Everything after this reading is about
shrinking it, and the shrinking is only possible because there is so much slack in what
the construction hands you.

**Time.** Every claim above describes the circuit *after it has settled*. The table says
nothing whatever about the nanoseconds during which the inputs are changing, and what
happens then is not in the table. Change A and the new value reaches the four AND gates
along paths of different lengths — one of them through an inverter — so for a moment
some terms have seen the change and others have not, and the OR can briefly produce a
level that no row of the table permits. That is a **glitch**, and combinational logic is
full of them. It is harmless if the only thing reading the output is a flip-flop that
samples once a clock cycle, long after everything has settled, which is exactly why the
next module wraps flip-flops around every block of combinational logic and why
synchronous design is the default everywhere. It is not harmless if the output goes
somewhere that reacts the instant it moves.

So, said honestly: the construction gives you a circuit whose steady-state behaviour is
precisely the table you started with, at a price that is usually indefensible, and with
a transient behaviour it makes no promises about at all. The next reading deals with the
price. The module after this one deals with the transient.
''',
                },
                {
                    "title": "One move, and the map that makes it visible",
                    "minutes": 14,
                    "body": r'''
The canonical form is correct and too big. This reading is about making it small, and
there is only one idea in it. Everything else — the map, and the programs that replaced
the map — is machinery for *finding* the places where that one idea applies.

## Two chains that differ in one contact

Go back to the relay network from the previous reading. You have built the canonical
circuit for the carry out, $\sum m(3,5,6,7)$: four chains in parallel, three contacts
each, twelve contacts in total. Look at two of them.

```
 the chain for row 6 (110):   make-A --- make-B --- break-Cin
 the chain for row 7 (111):   make-A --- make-B --- make-Cin
```

Identical, except that the last contact is a break in one and a make in the other, and
both belong to the **same relay**. A relay is either energised or it is not, so of those
two contacts exactly one is closed at any instant — always precisely one. Whichever way
Cin goes, one of the two chains has its third contact closed.

So the pair of chains, taken together, conducts whenever make-A and make-B are both
closed, and the Cin relay is not deciding anything at all. Rip out both Cin contacts and
merge the two chains into one:

```
 the merged chain:            make-A --- make-B
```

Six contacts have become two, and the circuit does exactly what it did before. In
algebra it is one line:

$$XY + XY' = X(Y + Y') = X \cdot 1 = X$$

with $X = AB$ and $Y = C_{in}$. That identity is the entire content of logic
minimisation. If two product terms differ in exactly one variable, that variable does
not matter and drops out, taking one whole term with it.

## Why finding the pairs is the hard part

$\sum m(3,5,6,7)$. Which pairs differ in exactly one variable?

```
 3 = 011  vs  7 = 111    differ in A only        mergeable
 5 = 101  vs  7 = 111    differ in B only        mergeable
 6 = 110  vs  7 = 111    differ in Cin only      mergeable
 3 = 011  vs  5 = 101    differ in A and B       not mergeable
 3 = 011  vs  6 = 110    differ in A and Cin     not mergeable
 5 = 101  vs  6 = 110    differ in B and Cin     not mergeable
```

Four terms, six pairs, each a bit-by-bit comparison you can miscount. Ten terms would be
forty-five pairs — and worse, every successful merge produces a new, shorter term which
may itself merge with something, so the search restarts on a changed list.

What would make this bearable is a *picture* in which "differs in one variable" is the
same thing as "next to each other on the page", so that the eye does the searching. That
picture is the **Karnaugh map**, and it is nothing but the truth table with its rows
rearranged until adjacency on paper means adjacency in the algebra.

The rearrangement is forced, not chosen. Counting order — 00, 01, 10, 11 — puts 01 next
to 10, and those differ in *both* bits; in counting order some neighbours are mergeable
and some are not, which makes the picture worthless. Order them **00, 01, 11, 10** and
every step along the row changes exactly one bit. That sequence is called Gray code, and
this is why the map's labels are in it. It is also cyclic: the last entry 10 differs from
the first entry 00 in one bit as well. So the two ends of a row are neighbours too, and
that is the whole origin of the map's wrap-around. It is not an extra rule bolted on
afterwards; it is the same property, applied to the pair that happens to be drawn at
opposite edges.

## The three-variable map, on the carry function

Two variables on the rows, one on the columns. The cell for a row of the table sits
where its A, B label meets its C label.

```
                    C
            \     0     1
     A B  00 |    0     0        <- m0, m1
          01 |    0     1        <- m2, m3
          11 |    1     1        <- m6, m7
          10 |    0     1        <- m4, m5
```

Notice the row labels: 00, 01, 11, 10, and the rows in that order are m0/m1, m2/m3,
m6/m7, m4/m5 — not in numerical order, which is the point.

Now circle. Every block must be a rectangle of $2^k$ cells, and what survives into the
term is exactly the set of variables that hold the *same* value everywhere in the block.

```
 {m3, m7}   rows 01 and 11, column C=1.  A changes, B=1 and C=1 hold.  ->  B·C
 {m5, m7}   rows 10 and 11, column C=1.  B changes, A=1 and C=1 hold.  ->  A·C
 {m6, m7}   row 11, both columns.        C changes, A=1 and B=1 hold.  ->  A·B
```

Those three blocks cover all four 1s, so

$$C_{out} = AB + AC + BC$$

Six literals, down from twelve, and now the expression is recognisable: the carry out is
the **majority** of the three inputs, true when at least two of them are.

Two things in that example are worth dwelling on. First, $m_7$ belongs to all three
blocks at once, and that is fine — overlapping is not double counting, because
$X + X = X$. Second, there is no block of four here, even though four cells are 1: the
column $C = 1$ holds $m_1, m_3, m_7, m_5$ and $m_1$ is 0, so the three 1s in that column
are three cells, and three is not a power of two. Circling them would be wrong.

## Four variables, a wrap and a block of four

Rows carry A and B, columns carry C and D, both in Gray order. The cell in row $ab$ and
column $cd$ is minterm $8a + 4b + 2c + d$.

Take $F = \sum m(0, 2, 5, 7, 8, 10, 13, 15)$:

```
                        C D
                \    00   01   11   10
       A B   00 |     1    0    0    1
             01 |     0    1    1    0
             11 |     0    1    1    0
             10 |     1    0    0    1
```

Two blocks account for all eight 1s.

**The four corners.** Rows 00 and 10 are neighbours through the wrapped top-and-bottom
edge; columns 00 and 10 through the wrapped left-and-right edge. Wrapping in both
directions at once is legal, and the four corners form a rectangle of four cells. What
holds throughout: A takes both values, C takes both values, but $B = 0$ in every corner
and $D = 0$ in every corner. The term is $B'D'$.

**The square in the middle.** Rows 01 and 11, columns 01 and 11. A varies, C varies,
$B = 1$ and $D = 1$ throughout. The term is $BD$.

$$F = B'D' + BD$$

Four literals. The canonical form would have been eight terms of four literals each —
thirty-two — so this is an eight-fold reduction, and again the shrunken expression says
something the long one hid: $F$ is 1 exactly when B and D agree, which is
$F = (B \oplus D)'$, an XNOR of two of the four inputs with the other two irrelevant.

Verify a cell the slow way. $m_{13} = 1101$, so $A=1, B=1, C=0, D=1$: $B'D' = 0 \cdot 0 =
0$ and $BD = 1 \cdot 1 = 1$, so $F = 1$, and 13 is in the list. Now a cell that should be
0: $m_{12} = 1100$, so $B = 1, D = 0$: $B'D' = 0 \cdot 1 = 0$ and $BD = 1 \cdot 0 = 0$,
so $F = 0$, and 12 is not in the list.

## The rules, in five lines

1. One cell per row of the table, laid out in Gray code along both axes.
2. A block is a rectangle of $2^k$ cells — 1, 2, 4, 8, 16 — and it may wrap round either
   edge, or both.
3. A block of $2^k$ cells removes $k$ variables; the term keeps exactly the variables
   that hold one value throughout the block.
4. Every 1 must lie inside at least one block. Blocks may overlap as much as they like.
5. Take the largest blocks you can, then the fewest of them that cover everything.

Rule 5 is where the judgement is, and the vocabulary helps: a block that cannot be
enlarged is a **prime implicant**, and one that is the only block covering some
particular 1 is **essential**. Take every essential prime implicant first — you have no
choice about them — and only then decide how to mop up whatever 1s remain.

## Don't-cares

Some input combinations never occur. A binary-coded decimal digit uses four bits but
only 0000 to 1001 ever appear; 1010 through 1111 arrive from nowhere. Write an X in
those cells and treat each one as whichever value makes a block bigger. An X you did not
need stays uncircled, and the circuit will output whatever falls out of the gates on
that input — which is fine, because you promised not to care.

This is free minimisation and it is often substantial. A seven-segment decoder fed from
a BCD counter has six don't-care rows out of sixteen, and its segment expressions come
out markedly smaller for it. The decoder in this course's capstone is the other case: it
runs off a plain 4-bit counter that reaches all sixteen values and displays a hex digit
for every one of them, so there are no don't-cares to exploit and all sixteen rows are
specified.

## The mistakes people actually make

**Circling three cells.** Three adjacent 1s look exactly like a group, and they are not
one — $XY + XY' = X$ has no three-term version, and a block of three removes no variable
cleanly. The fix is to cover them with two overlapping blocks of two.

**Circling in counting order.** If you draw the map with its columns labelled 00, 01,
10, 11 out of habit, the middle two columns are no longer neighbours and every block
that straddles them is wrong. The labels are the mechanism, not decoration.

**Stopping at the first legal cover.** Every 1 being inside some block means the
expression is *correct*, not that it is small. It is worth one deliberate second, per
block, asking whether it could have been twice the size.

**Forgetting the wrap.** The four corners are the classic case, and a solver who has
never wrapped will produce four separate one-cell terms of four literals each where two
literals would do.

## Where the map stops

**At about five variables.** Five needs two four-variable maps stacked, with cells
directly above one another counting as adjacent; six needs four. Beyond that nobody
draws maps. The mechanical version of the same search is the Quine-McCluskey algorithm,
which is exact and takes exponential time, and beyond the sizes it can manage the
industry uses Espresso and its descendants, which are heuristics. Exact two-level
minimisation is NP-hard, so every tool you will ever run on a real design is giving you
a good answer rather than the best one.

**At minimality itself, which is not always what you want.** This is the more
interesting limit. Take $F = AB + A'C$, which is already a minimal sum of products, and
hold $B = C = 1$ while A falls from 1 to 0.

```
 with A = 1:   A·B = 1,  A'·C = 0    ->  F = 1
 with A = 0:   A·B = 0,  A'·C = 1    ->  F = 1
```

The table says the output does not move. The circuit disagrees for a moment. When A
falls, the $AB$ term switches off immediately, while the $A'C$ term cannot switch on
until A has crawled through an inverter first. In between, both terms are 0 and the
output dips to 0 — a **static-1 hazard**, a glitch on an output that was supposed to
hold still.

Look at where those two 1s are on the map. They are $m_3 = 011$ and $m_7 = 111$, which
differ in A alone and are therefore adjacent — but they were circled into *different*
blocks, and no block covers the pair. Add the block that does, and it gives the term
$BC$:

$$F = AB + A'C + BC$$

That term is logically redundant: the map was already covered, and no row of the table
changes. It is physically necessary: with $B = C = 1$ it is 1 regardless of A, so it
holds the output up while the other two terms hand over. A minimiser will delete it
unless it is told not to.

So "minimal" means fewest gates, and fewest gates is one thing worth wanting. Behaving
during the transition is another, and the two genuinely disagree. Which one you should
be optimising is decided by what reads the output — a clocked flip-flop does not care,
and an asynchronous reset line very much does.
''',
                },
                {
                    "title": "Two levels, one kind of gate, and the adder that pays for it",
                    "minutes": 13,
                    "body": r'''
A sum of products is not only an expression, it is a *shape*. Every SOP, whatever
function it computes, draws as one row of AND gates — one gate per product term — all
feeding a single OR gate. Two levels of logic, plus inverters wherever a literal is
complemented.

That is a strong claim about speed. Depth two means the delay is two gate delays no
matter how complicated the function is, and it is the reason minimisation targets
two-level form in the first place. It is also, taken literally, false in silicon, and
this reading is about the distance between the drawing and the thing on the die.

## What two levels actually costs

The price of shallow is wide. A product term of $k$ literals needs a $k$-input AND, and
the OR needs one input per term. The 16-bit comparator from the first reading would want
a 65 536-input OR gate. There is no such object.

Real gates have a fan-in of about two to four, above which they get slow. In CMOS the
reason is concrete: an $n$-input NAND puts $n$ transistors in series between the output
and ground, and series resistances add, so an 8-input gate pulls down roughly eight
times as feebly as an inverter of the same width. A wide AND is therefore built as a
*tree* of narrow ANDs, and a tree covering $m$ inputs is $\log_2 m$ deep.

So the honest version of the claim is: two-level logic is two levels *on paper*, and
$O(\log)$ levels in a standard-cell library. It is still the shallowest thing available,
which is why it is the target; it is just not the constant it looks like.

## One kind of gate is enough

NAND alone can build everything, and the proof is three lines of construction:

```
 NOT A       =  A NAND A                        since (A·A)' = A'
 A AND B     =  (A NAND B) NAND (A NAND B)      a NAND, then invert it
 A OR  B     =  (A NAND A) NAND (B NAND B)      = (A'·B')' = A'' + B'' = A + B
```

The third one is De Morgan doing the work: $A + B = (A' \cdot B')'$, which is precisely a
NAND fed with the two complements.

There are two reasons to care about this, and only one of them is the famous one.

The famous reason: a process that can make a NAND can make anything, so a gate array can
be a uniform sea of identical cells and the customer's function is decided entirely by
metal. True, and it mattered enormously in the 1980s.

The reason that decides real designs today: in CMOS a NAND is genuinely cheaper than a
NOR of the same width. A two-input NAND puts its two NMOS transistors in series and its
two PMOS in parallel; a NOR does exactly the opposite. Holes are two to three times less
mobile than electrons, so a PMOS transistor must be two to three times wider than an
NMOS to carry the same current — and a NOR stacks the *wide* ones in series, which costs
area and drags out the rising edge. So a standard-cell library has a brisk NAND and a
reluctant NOR, and synthesis knows it.

## Bubble pushing: AND-OR becomes NAND-NAND

Take the two-term sum of products $F = AB + CD$ and replace every gate in the drawing —
both ANDs and the OR — with a NAND, changing no wires at all. What comes out?

$$G = \big((AB)' \cdot (CD)'\big)'$$

De Morgan on the outer complement turns the product into a sum and moves the complement
inwards:

$$G = (AB)'' + (CD)'' = AB + CD = F$$

The same function, on the same wires. Nothing was added and nothing was removed: the
inversion bubble on each AND output is cancelled by the bubble that De Morgan puts on
the corresponding OR input. Draw the bubbles and they annihilate in pairs — which is all
"bubble pushing" means, and it is why a schematic that is nothing but NANDs is usually
best read as an AND-OR with the bubbles ignored.

One thing does not transfer. An inverted *literal* is not a gate bubble: $F = A'B + CD$
still needs its inverter on A after the conversion. NAND-NAND replaces the gates, not
the complements on the inputs.

## Worked example 1 — XOR out of four NANDs

XOR is the sum bit of an adder, so it is worth being able to build. The standard
four-gate arrangement computes an intermediate $g = (AB)'$ and feeds it back into two
more NANDs:

$$g = (AB)', \qquad \text{out} = \big((Ag)' \cdot (Bg)'\big)'$$

Expand the outer NAND with De Morgan, then substitute:

```
 out  =  (A·g)'' + (B·g)''        De Morgan on the outer complement
      =  A·g + B·g                two complements cancel
      =  A·(A·B)' + B·(A·B)'      substituting g
      =  A·(A' + B') + B·(A' + B')    De Morgan on (A·B)'
      =  A·A' + A·B' + A'·B + B·B'    multiplying out
      =  0 + A·B' + A'·B + 0          since X·X' = 0
      =  A·B' + A'·B  =  A XOR B
```

Check two rows against the gates rather than the algebra. With $A = 1, B = 1$:
$g = (1 \cdot 1)' = 0$, so $(Ag)' = (1 \cdot 0)' = 1$ and $(Bg)' = (1 \cdot 0)' = 1$, and
the output is $(1 \cdot 1)' = 0$ — correct, XOR of two 1s is 0. With $A = 1, B = 0$:
$g = (1 \cdot 0)' = 1$, so $(Ag)' = (1 \cdot 1)' = 0$ and $(Bg)' = (0 \cdot 1)' = 1$, and
the output is $(0 \cdot 1)' = 1$ — correct.

## Worked example 2 — the full adder, and how long it takes

The full adder's two outputs are the XOR of all three inputs and the majority of all
three:

$$S = A \oplus B \oplus C_{in}, \qquad C_{out} = AB + AC_{in} + BC_{in}$$

but nobody builds the carry that way. Define $p = A \oplus B$ — historically the
*propagate* signal — and write

$$S = p \oplus C_{in}, \qquad C_{out} = AB + p\,C_{in}$$

Why is that second expression the majority function? Two cases, and no algebra needed.

* If A and B **agree**, then $p = 0$, so $C_{out} = AB$, which equals A (and equals B).
  Two of the three votes are A, so the majority is A. Correct.
* If A and B **differ**, then $AB = 0$ and $p = 1$, so $C_{out} = C_{in}$. A and B have
  cast one vote each way, so $C_{in}$ decides. Correct.

The same function, then — but $p$ is now computed once and used twice, and, far more
important, the path from $C_{in}$ to $C_{out}$ passes through exactly one AND and one
OR. Everything else in the stage depends only on A and B, which are available at time
zero.

Now put numbers on it. Take a library with

```
 2-input XOR        0.25 ns
 2-input AND or OR  0.15 ns
```

and chain four full adders, each stage's carry out into the next stage's carry in. The
$p$ signals for all four stages are computed from the inputs simultaneously.

```
 all four p = A xor B, in parallel        ready at        0.25 ns

 C1 = A0·B0 + p0·C0
      A0·B0 ready at 0.15, p0·C0 at 0.25 + 0.15 = 0.40
      the OR then settles at 0.40 + 0.15  =              0.55 ns
 C2 = A1·B1 + p1·C1   ->  0.55 + 0.15 + 0.15  =          0.85 ns
 C3                   ->  0.85 + 0.30        =           1.15 ns
 C4, the carry out    ->  1.15 + 0.30        =           1.45 ns

 S3 = p3 xor C3       ->  1.15 + 0.25        =           1.40 ns
```

Worst case 1.45 ns, and it is the carry out, not the last sum bit, that arrives last —
by 0.05 ns, which is exactly $2 \times 0.15 - 0.25$. Choose a library whose XOR is
slower than two ordinary gate delays and the sum bit becomes the critical output
instead; nothing about the structure decides it, only the cell timings.

The trouble shows at width. Every extra bit adds one AND and one OR to the carry chain,
so a 32-bit ripple-carry adder settles at $0.25 + 32 \times 0.30 = 9.85$ ns and caps the
clock below 102 MHz all by itself, before any other logic in the datapath is counted.
The delay is **linear in the word length**, and that is the defect that the rest of
computer arithmetic exists to fix: carry-lookahead computes the carries from a tree of
generate and propagate terms in depth proportional to $\log n$, at a cost in gates that
is well worth paying above about eight bits.

## The mistakes people actually make

**Believing NAND-only means fewer gates.** It does not. $AB + CD$ is three gates as
AND-OR and three gates as NAND-NAND. What changes is which cell each one is, not how
many there are. Occasionally the conversion adds an inverter and occasionally it cancels
one; the count is a wash. The saving is in the cell library and the transistor count per
cell, not in the schematic.

**Reading "two-level logic has constant delay" as a statement about circuits.** It is a
statement about drawings, and it costs people real time. Two levels of unbounded fan-in
is two gate delays only if unbounded fan-in gates exist. Every synthesis tool takes the
minimal two-level form and immediately makes it multi-level again — deeper, narrower,
smaller, and usually *faster*, because a three-deep tree of quick two-input gates beats
one impossible thirty-input gate every time.

## Where this stops

**The delay model.** One number per gate is a fiction, useful for arithmetic like the
adder above and dangerous for anything else. A gate's delay depends on what it drives —
the capacitance of the wire and of every input hanging off it — and on how fast its own
input is moving. The same NAND driving one neighbouring cell and driving twelve cells
across a block can differ by a factor of three. Static timing analysis treats delay as a
function of load and input slew, interpolated from tables measured on silicon; the
single number in a datasheet is that function evaluated at one nominal load.

**Universality.** "Any function can be built from NANDs" is an existence result, not
advice. Nothing in a modern chip builds an XOR from the four NANDs above: the library
has an XOR cell made from transmission gates that is smaller and faster than four NANDs
wired together. The theorem tells you the toolbox is complete. It does not tell you
which tool to pick up, and those are different questions.
''',
                },
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
            "blanks": [
                {
                    "title": "Circling a four-variable map",
                    "minutes": 9,
                    "caption": "sixteen cells, two circles, and four literals at the end of it",
                    "lang": "text",
                    "brief": r'''
The map is drawn for you and two of its cells have been left out. Fill them in from the
list of minterms, then read the two blocks off the finished map.

Remember what a block leaves behind: the variables that hold the *same* value in every
cell of the block survive into the term, and the ones that change are the ones the block
has eliminated.
''',
                    "listing": """F(A,B,C,D) = sum m(0, 2, 5, 7, 8, 10, 13, 15)

  the cell in row `ab`, column `cd` holds minterm  8a + 4b + 2c + d

                            C D
                    \\    00   01   11   10
           A B   00 |     1    0    0   ___
                 01 |     0   ___   1    0
                 11 |     0    1    1    0
                 10 |     1    0    0    1

  block 1: the four corner cells, joined through both wrapped edges   ->  ___
  block 2: the two-by-two square in the middle                        ->  ___

  F  =  block 1  +  block 2  =  ___
""",
                    "blanks": [
                        {
                            "prompt": "Row `A B = 00`, column `C D = 10`. Which minterm is that cell, and is it in the list?",
                            "hole": "?",
                            "opts": ["0", "1"],
                            "a": 1,
                            "why": "The cell is $8(0) + 4(0) + 2(1) + 0 = m_2$, and 2 is in the list, so the "
                                   "cell holds a 1. Watch the column label: it is `10`, meaning $C = 1$ and "
                                   "$D = 0$, so the minterm is 2 rather than 1. Reading the Gray-code labels "
                                   "as if they were in counting order is what swaps $m_2$ and $m_3$ into "
                                   "each other's cells.",
                        },
                        {
                            "prompt": "Row `A B = 01`, column `C D = 01`. Which minterm is that cell, and is it in the list?",
                            "hole": "?",
                            "opts": ["0", "1"],
                            "a": 1,
                            "why": "The cell is $8(0) + 4(1) + 2(0) + 1 = m_5$, which is in the list, so it "
                                   "holds a 1. It is the top-left corner of the square in the middle of the "
                                   "map, and the other three cells of that square — $m_7$, $m_{13}$ and "
                                   "$m_{15}$ — are already printed.",
                        },
                        {
                            "prompt": "The four corners. A and C each take both values across them, so which term is left?",
                            "hole": "?",
                            "opts": ["B'·D'", "A'·C'", "B·D", "A'·D'"],
                            "a": 0,
                            "why": "The corners are $m_0 = 0000$, $m_2 = 0010$, $m_8 = 1000$ and "
                                   "$m_{10} = 1010$. Across those four, A is 0 twice and 1 twice, and C is "
                                   "0 twice and 1 twice, so both are eliminated; B is 0 in all four and D is "
                                   "0 in all four, so both survive complemented. That gives $B'D'$. $A'C'$ "
                                   "and $A'D'$ both keep an $A$, which cannot be right when A takes both "
                                   "values inside the block, and $BD$ has the two surviving variables the "
                                   "wrong way up — it is the term of the *other* block, where both are 1.",
                        },
                        {
                            "prompt": "The two-by-two square in the middle. Which term is that?",
                            "hole": "?",
                            "opts": ["B·D", "A·C", "B'·D'", "A·B"],
                            "a": 0,
                            "why": "The square is $m_5 = 0101$, $m_7 = 0111$, $m_{13} = 1101$ and "
                                   "$m_{15} = 1111$. A varies down the rows and C varies across the columns, "
                                   "so both go; $B = 1$ and $D = 1$ throughout, so the term is $BD$. Note "
                                   "that the rows involved are labelled 01 and 11, which are adjacent "
                                   "because they differ in A alone — that is the Gray ordering earning its "
                                   "keep.",
                        },
                        {
                            "prompt": "So what is $F$, and what is it in plainer language?",
                            "hole": "?",
                            "opts": [
                                "B'·D' + B·D, which is 1 exactly when B and D agree",
                                "B'·D' + A·C, which is 1 when B and D are both 0 or A and C are both 1",
                                "B ⊕ D, which is 1 exactly when B and D differ",
                                "A'·C' + A·C, which is 1 exactly when A and C agree",
                            ],
                            "a": 0,
                            "why": "Four literals, down from the eight terms of four literals that the "
                                   "canonical form would have needed. $B'D'$ catches the case where both are "
                                   "0 and $BD$ the case where both are 1, so $F$ is the XNOR of B and D — "
                                   "and A and C do not appear at all, which the map made obvious the moment "
                                   "the blocks came out four cells wide. The XOR reading has it exactly "
                                   "backwards: $B \\oplus D$ is the complement of this function and is 1 on "
                                   "the eight cells that hold 0 here.",
                        },
                    ],
                },
                {
                    "title": "Every gate a NAND, one law at a time",
                    "minutes": 8,
                    "caption": "the AND-OR to NAND-NAND conversion, with the laws taken off",
                    "lang": "text",
                    "brief": r'''
Replace all three gates of a two-term sum of products with NANDs, change no wires, and
the function is unaltered. That is not a coincidence and it is not a rule to memorise:
it is two laws applied once each.

The working is below with the names removed. Put them back.
''',
                    "listing": """F = A·B + C·D, redrawn with three NANDs in place of two ANDs and an OR

  G  =  NAND( NAND(A,B), NAND(C,D) )

     =  ( (A·B)' · (C·D)' )'          the output NAND, written out

     =  (A·B)''  +  (C·D)''           ___

     =  A·B  +  C·D  =  F             ___

  and the same gate makes an inverter:

  NAND(A, A)  =  (A · A)'  =  ___     ___
""",
                    "blanks": [
                        {
                            "prompt": "$\\big((A\\cdot B)' \\cdot (C \\cdot D)'\\big)'$ became a sum of two doubly-complemented products. Which law is that?",
                            "hole": "?",
                            "opts": [
                                "De Morgan — the complement of a product is the sum of the complements",
                                "distribution — a common factor comes outside the bracket",
                                "absorption — X + X·Y = X",
                                "involution — complementing twice returns the original",
                            ],
                            "a": 0,
                            "why": "The whole bracket is a product of two things, $(A\\cdot B)'$ and "
                                   "$(C \\cdot D)'$, and it is being complemented. De Morgan turns that into "
                                   "the OR of the two complements, and the complement of an already "
                                   "complemented term is what appears. Involution is the law used on the "
                                   "*next* line, once the double complements exist; distribution rearranges "
                                   "brackets without touching a complement, and there is no term here to "
                                   "absorb.",
                        },
                        {
                            "prompt": "$(A\\cdot B)''$ became $A \\cdot B$. Which law is that?",
                            "hole": "?",
                            "opts": [
                                "involution — complementing twice returns the original",
                                "De Morgan — a complement moves inwards and flips the operator",
                                "identity — X · 1 = X",
                                "complement — X · X' = 0",
                            ],
                            "a": 0,
                            "why": "With two values there is nowhere else for a complement to go, so "
                                   "$X'' = X$. Drawn as gates, this is the bubble on each AND's output being "
                                   "cancelled by the bubble De Morgan puts on the OR's input — which is the "
                                   "picture behind the phrase *bubble pushing*, and it is why a page of "
                                   "NANDs is usually best read as an AND-OR with the bubbles crossed off in "
                                   "pairs.",
                        },
                        {
                            "prompt": "$(A \\cdot A)'$ simplifies to what?",
                            "hole": "?",
                            "opts": ["A'", "A", "0", "1"],
                            "a": 0,
                            "why": "$A \\cdot A$ is $A$, so its complement is $A'$: a NAND with both inputs "
                                   "tied to the same signal is an inverter. Tying the spare input to a "
                                   "constant 1 works too, and tying it to 0 does not — an AND with 0 is "
                                   "always 0, so the output would sit at 1 and ignore the signal entirely.",
                        },
                        {
                            "prompt": "Which law turned $A \\cdot A$ into $A$?",
                            "hole": "?",
                            "opts": [
                                "idempotence — X · X = X",
                                "identity — X · 1 = X",
                                "complement — X · X' = 0",
                                "involution — X'' = X",
                            ],
                            "a": 0,
                            "why": "Idempotence: ANDing something with itself asks whether it is 1 twice "
                                   "over, which is no more demanding than asking once. Two switch contacts "
                                   "on the same relay wired in series are one contact. The identity law "
                                   "needs a literal constant 1 as the second operand, and there is none "
                                   "written here; the complement law needs an $A'$.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "The size of the form you can always write down",
                    "minutes": 5,
                    "brief": r'''
One rule, applied once. The canonical sum of products has one product term per row where
the output is 1, and every one of those terms names every variable exactly once.

A **literal** is one appearance of a variable, primed or not. Counting literals is the
usual first estimate of what an expression will cost in gate inputs, and here it needs no
algebra at all — only the two numbers below.
''',
                    "prompt": "How many literals does the canonical sum of products contain?",
                    "note": "Give the answer as a whole number of literals.",
                    "figure": "A function of the four variables A, B, C and D is 1 in exactly 9 of the "
                              "16 rows of its truth table, and 0 in the other 7. It is written out as a "
                              "canonical sum of products — the OR of the minterm of every row where the "
                              "function is 1.",
                    "given": [
                        {"label": "Variables", "value": "4 (A, B, C, D)"},
                        {"label": "Rows in the table", "value": "16"},
                        {"label": "Rows where the output is 1", "value": "9"},
                    ],
                    "aside": "A minterm of $n$ variables contains all $n$ of them, complemented where the "
                             "row has a 0. It never contains fewer and never contains more.",
                    "answer": 36.0,
                    "tol": 0.5,
                    "unit": "literals",
                    "hint": "One term per 1-row, and 4 literals in each term.",
                    "wrong": "If you got 9, that is the number of *terms*, not literals — each term still "
                             "has four variables in it. If you got 64, every row of the table was counted "
                             "rather than only the rows where the output is 1; the 7 zero rows contribute "
                             "nothing to a sum of products. If you got 28, the count was taken from the "
                             "zero rows, which is the row set the canonical *product of sums* uses.",
                    "why": "Nine rows carry a 1, so there are nine minterms; each minterm names all four "
                           "variables, so $9 \\times 4 = 36$ literals. As a circuit that is nine AND gates "
                           "of four inputs, one OR gate of nine inputs, and four inverters. Worth holding "
                           "on to for comparison: the same function will usually reduce to fewer than ten "
                           "literals once a map has been drawn, and the general shape of the canonical "
                           "form's cost is $r \\times n$ literals for $r$ one-rows and $n$ variables — "
                           "which grows as $2^n$ in the worst case, since $r$ can be as large as $2^n$ "
                           "itself.",
                },
                {
                    "title": "What the map saves, counted in gate inputs",
                    "minutes": 10,
                    "brief": r'''
The map below is already filled in. Find the smallest sum of products that covers every
1, then cost it the way a synthesis tool does: by counting **gate inputs**.

Each product term of $k$ literals is a $k$-input AND gate, contributing $k$ inputs. The
single OR gate that collects $t$ terms contributes $t$ inputs. Assume the complemented
literals are already available, so the inverters cost nothing here.

There are no don't-cares. Every 1 must be covered, and the blocks may overlap.
''',
                    "prompt": "How many gate inputs does the minimal two-level AND-OR network need?",
                    "note": "Give the answer as a whole number of gate inputs.",
                    "figure": "$F(A,B,C,D) = \\sum m(0,1,2,3,4,5,10,11,14,15)$, drawn on a Karnaugh map "
                              "with A and B on the rows and C and D on the columns, both in Gray order. "
                              "The cell in row `ab`, column `cd` holds the minterm $8a + 4b + 2c + d$.\n\n"
                              "```\n"
                              "                        C D\n"
                              "                \\    00   01   11   10\n"
                              "       A B   00 |     1    1    1    1\n"
                              "             01 |     1    1    0    0\n"
                              "             11 |     0    0    1    1\n"
                              "             10 |     0    0    1    1\n"
                              "```",
                    "given": [
                        {"label": "Cells holding a 1", "value": "10 of 16"},
                        {"label": "Cost of a k-literal term", "value": "k gate inputs"},
                        {"label": "Cost of the output OR", "value": "one input per term"},
                        {"label": "Inverters", "value": "free — both polarities are available"},
                    ],
                    "aside": "A block of 4 cells removes two variables and leaves a term of two literals. "
                             "Look for those before you settle for blocks of 2.",
                    "answer": 9.0,
                    "tol": 0.5,
                    "unit": "gate inputs",
                    "hint": "Three blocks of four cells cover the map: the whole top row, the left half of "
                            "the top two rows, and the right half of the bottom two rows.",
                    "wrong": "If you got 6, only the literals were counted and the OR gate's own inputs "
                             "were left out. If you got 50, the canonical form was costed instead: ten "
                             "four-input ANDs and a ten-input OR. If you got 10, the two cells $m_4$ and "
                             "$m_5$ were circled on their own as $A'BC'$ instead of being swept up into a "
                             "block of four with $m_0$ and $m_1$ — a correct cover that is one literal too "
                             "big, and the commonest way to finish a map with the wrong answer.",
                    "why": "Three blocks of four, each removing two variables. The top row entire, "
                           "$m_0 m_1 m_3 m_2$, has $A = 0$ and $B = 0$ throughout, giving $A'B'$. The left "
                           "half of the top two rows, $m_0 m_1 m_4 m_5$, has $A = 0$ and $C = 0$ "
                           "throughout, giving $A'C'$. The right half of the bottom two rows, "
                           "$m_{15} m_{14} m_{11} m_{10}$, has $A = 1$ and $C = 1$ throughout, giving $AC$. "
                           "So $F = A'B' + A'C' + AC$ — three AND gates of two inputs, which is 6, plus a "
                           "three-input OR, which is 3, for **9 gate inputs**. Every one of the three "
                           "blocks is essential: $m_2$ and $m_3$ are covered by nothing but $A'B'$, $m_4$ "
                           "and $m_5$ by nothing but $A'C'$, and the four cells at the bottom right by "
                           "nothing but $AC$. There is no block of eight anywhere on this map, so three "
                           "terms of two literals is the floor. Against the canonical form's ten "
                           "four-input ANDs and one ten-input OR — 50 gate inputs — the map has taken "
                           "about four fifths of the circuit away.",
                },
                {
                    "title": "A sum of products, in copper",
                    "minutes": 9,
                    "brief": r'''
The circuit from the build: two product terms, wired as two series chains side by side.
The upper chain is $A \cdot B$ with both contacts closed — 120 Ω and 180 Ω. The lower
chain is $A' \cdot C$, and since A is energised its **break** contact is open, drawn as
the 1 MΩ of a real air gap; the C contact below it is closed at 150 Ω. A 10 kΩ pull-down
holds the gate input near ground when neither chain conducts.

So the input state is $A = 1$, $B = 1$, $C = 1$, and $F = 1 \cdot 1 + 0 \cdot 1 = 1$.
Read off the node the probe is sitting on.
''',
                    "prompt": "What voltage does the gate input settle at?",
                    "note": "Give the answer in volts, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 12, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 15},
                            {"id": "ra", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                            {"id": "rb", "kind": "R", "x": 12, "y": 3, "rot": 0, "value": 180},
                            {"id": "rna", "kind": "R", "x": 6, "y": 7, "rot": 0, "value": 1000000},
                            {"id": "rc", "kind": "R", "x": 12, "y": 7, "rot": 0, "value": 150},
                            {"id": "rl", "kind": "R", "x": 17, "y": 10, "rot": 1, "value": 10000},
                            {"id": "g1", "kind": "GND", "x": 17, "y": 13},
                            {"id": "out", "kind": "OUT", "x": 20, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 13], "b": [3, 15]},
                            {"a": [3, 11], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [3, 7], "b": [5, 7]},
                            {"a": [7, 3], "b": [11, 3]},
                            {"a": [7, 7], "b": [11, 7]},
                            {"a": [13, 3], "b": [17, 3]},
                            {"a": [13, 7], "b": [17, 7]},
                            {"a": [17, 3], "b": [17, 9]},
                            {"a": [17, 11], "b": [17, 13]},
                            {"a": [17, 3], "b": [20, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "A·B chain: A closed, B closed", "value": "120 Ω + 180 Ω"},
                        {"label": "A'·C chain: A' open, C closed", "value": "1 MΩ + 150 Ω"},
                        {"label": "Pull-down at the gate input", "value": "10 kΩ"},
                    ],
                    "aside": "Add along each chain, combine the two chains in parallel, then treat the "
                             "result and the pull-down as a two-resistor divider.",
                    "answer": 4.854,
                    "tol": 0.01,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "The chains are $120 + 180 = 300$ Ω and $10^6 + 150$ Ω. In parallel they are "
                            "barely different from 300 Ω, and the divider is then that against 10 kΩ.",
                    "wrong": "If you got about 0.049 V, the four contacts were put in one line rather than "
                             "in two chains — that circuit is $A \\cdot B \\cdot A' \\cdot C$, which the "
                             "algebra says is 0, and the volts agree. If you got 5.00 V, the contact "
                             "resistances were treated as perfect shorts; that is the right idealisation "
                             "for reading the logic and the wrong answer to what the circuit does.",
                    "why": "Series adds, so the conducting chain is $120 + 180 = 300$ Ω and the open one is "
                           "$1\\,000\\,000 + 150 = 1\\,000\\,150$ Ω. In parallel: $300 \\times 1\\,000\\,150 "
                           "/ (300 + 1\\,000\\,150) = 299.910$ Ω — the open chain shifts the pair by less "
                           "than a tenth of an ohm, which is the electrical statement of $X + 0 = X$. "
                           "Against the 10 kΩ pull-down the total is $299.910 + 10\\,000 = 10\\,299.91$ Ω, "
                           "so the rail delivers $5/10\\,299.91 = 485.44$ µA and the pull-down holds "
                           "$485.44\\,\\mu\\text{A} \\times 10\\,\\text{k}\\Omega = 4.854$ V. Of that "
                           "485.44 µA, the two chains share the $5.0000 - 4.854 = 0.14559$ V that is left "
                           "over: the conducting one carries $0.14559\\,\\text{V}/300\\,\\Omega = 485.30$ "
                           "µA and the open one $0.14559\\,\\text{V}/1\\,000\\,150\\,\\Omega = 0.146$ µA — "
                           "the two add back to the total, and the second is the leakage that "
                           "the algebra does not have a symbol for. A 5 V CMOS input reads anything above "
                           "3.5 V as HIGH, so this arrives with 1.35 V of margin.",
                },
                {
                    "title": "The product term that is supposed to be zero",
                    "minutes": 13,
                    "brief": r'''
The carry out of a full adder is the majority of its three inputs, $C_{out} = A \cdot B +
A \cdot C + B \cdot C$, and here it is as three series chains in parallel — one chain per
product term, two contacts each.

The state is $A = 1$, $B = 1$, $C = 0$. So the $A \cdot B$ chain conducts through two
closed contacts, and the other two chains each contain an open contact standing for
$C$. Nothing here is ideal: the closed contacts are 120 Ω, 130 Ω, 150 Ω and 160 Ω, and
the two open ones are 1 MΩ and 1.2 MΩ, since two poles of the same relay never match.

The question is not about the probed node. It asks how much current is flowing in the
$B \cdot C$ chain — the branch that the algebra says is carrying a 0. That branch is the
one holding the largest resistance on the board, and finding its current means finding
the shared node first and then coming back to it.
''',
                    "prompt": "How much current flows in the B·C chain?",
                    "note": "Give the answer in nanoamps, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 16, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 19},
                            {"id": "ra1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                            {"id": "rb1", "kind": "R", "x": 12, "y": 3, "rot": 0, "value": 150},
                            {"id": "ra2", "kind": "R", "x": 6, "y": 7, "rot": 0, "value": 130},
                            {"id": "rc1", "kind": "R", "x": 12, "y": 7, "rot": 0, "value": 1000000},
                            {"id": "rb2", "kind": "R", "x": 6, "y": 11, "rot": 0, "value": 160},
                            {"id": "rc2", "kind": "R", "x": 12, "y": 11, "rot": 0, "value": 1200000},
                            {"id": "rl", "kind": "R", "x": 17, "y": 14, "rot": 1, "value": 10000},
                            {"id": "g1", "kind": "GND", "x": 17, "y": 17},
                            {"id": "out", "kind": "OUT", "x": 20, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 17], "b": [3, 19]},
                            {"a": [3, 15], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [3, 7], "b": [5, 7]},
                            {"a": [3, 11], "b": [5, 11]},
                            {"a": [7, 3], "b": [11, 3]},
                            {"a": [7, 7], "b": [11, 7]},
                            {"a": [7, 11], "b": [11, 11]},
                            {"a": [13, 3], "b": [17, 3]},
                            {"a": [13, 7], "b": [17, 7]},
                            {"a": [13, 11], "b": [17, 11]},
                            {"a": [17, 3], "b": [17, 13]},
                            {"a": [17, 15], "b": [17, 17]},
                            {"a": [17, 3], "b": [20, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "A·B chain (both closed)", "value": "120 Ω + 150 Ω"},
                        {"label": "A·C chain (C open)", "value": "130 Ω + 1 MΩ"},
                        {"label": "B·C chain (C open)", "value": "160 Ω + 1.2 MΩ"},
                        {"label": "Pull-down at the gate input", "value": "10 kΩ"},
                    ],
                    "aside": "Three parallel branches share the same pair of end nodes, so they all have "
                             "the same voltage across them. Get that voltage once and every branch current "
                             "follows from Ohm's law.",
                    "answer": 109.5,
                    "tol": 1.5,
                    "unit": "nA",
                    # The prompt asks for a branch current, which is no node of this circuit. The B·C
                    # chain is named structurally — it is the branch holding the largest resistance —
                    # so nothing here repeats a number the diagram already states.
                    "check": r'''
const rs = c.net.parts.filter(function (p) { return p.kind === 'R'; });
const worst = rs.reduce(function (a, b) { return b.value > a.value ? b : a; });
const d = c.dc();
return Math.abs(d.v[worst.n1] - d.v[worst.n2]) / worst.value * 1e9;
''',
                    "hint": "Work in conductances: the three chains are 270 Ω, 1 000 130 Ω and 1 200 160 Ω, "
                            "so the parallel combination is just under 270 Ω. Find the node voltage, "
                            "subtract it from 5 V to get the voltage across all three chains, then divide "
                            "that by the B·C chain's own resistance.",
                    "wrong": "If you got about 4.2 µA, the whole 5 V was dropped across the B·C chain, "
                             "which forgets that almost all of the rail lands on the 10 kΩ pull-down. If "
                             "you got about 131 nA, the A·C chain was measured instead — it is the other "
                             "non-conducting branch, and it carries slightly more because its open contact "
                             "is 1 MΩ rather than 1.2 MΩ.",
                    "why": "The three chains are $120 + 150 = 270$ Ω, $130 + 1\\,000\\,000 = 1\\,000\\,130$ "
                           "Ω and $160 + 1\\,200\\,000 = 1\\,200\\,160$ Ω. Their conductances are "
                           "$3703.70$ µS, $0.99987$ µS and $0.83322$ µS, adding to $3705.54$ µS, so the "
                           "three in parallel are $269.866$ Ω. With the pull-down that is "
                           "$269.866 + 10\\,000 = 10\\,269.87$ Ω, so the rail delivers "
                           "$5/10\\,269.87 = 486.86$ µA and the probed node sits at "
                           "$486.86\\,\\mu\\text{A} \\times 10\\,\\text{k}\\Omega = 4.8686$ V. That leaves "
                           "$5.0000 - 4.8686 = 0.13139$ V across all three chains at once, since parallel "
                           "branches share both end nodes. The B·C chain therefore carries "
                           "$0.13139\\,\\text{V}/1\\,200\\,160\\,\\Omega = 109.5$ nA. Two things are worth "
                           "taking away. The two 'zero' product terms are carrying 109.5 nA and 131.4 nA "
                           "between them — 0.05 % of the 486.9 µA the rail is supplying, which is why the "
                           "algebra can pretend they are not there, and not zero, which is why a contact "
                           "network with a thousand of these branches on one node eventually cannot. And "
                           "the conducting chain carries $0.13139/270 = 486.6$ µA; add the other two and "
                           "you recover the 486.9 µA the supply delivers, which is the current balance the "
                           "node voltage was chosen to satisfy in the first place.",
                },
            ],
            "derive": {
                "title": "How long a ripple-carry adder takes, and why it is the wrong shape",
                "minutes": 14,
                "vars": ["x", "g", "n", "c", "T"],
                "brief": r'''
The full adder built in the lab is correct at every width. Whether it is *usable* at
every width is a different question, and the answer comes out of one delay figure per
gate and a little bookkeeping.

Use the factored form, the one every real adder uses: with $p = A \oplus B$ computed
from the two operand bits alone,

$$S = p \oplus C_{in}, \qquad C_{out} = A \cdot B + p \cdot C_{in}$$

Write $x$ for the delay of a two-input XOR and $g$ for the delay of a two-input AND or
OR, taken as equal. Write $n$ for the number of bits.

The one fact that makes this tractable: every stage's $p$ depends only on that stage's
two operand bits, so all $n$ of them are computed at once and are all ready at time $x$.
Everything after that is the carry crawling along the chain.
''',
                "steps": [
                    {
                        "prompt": "Inside one stage, the path from $C_{in}$ to $C_{out}$ goes through the AND that forms $p \\cdot C_{in}$ and then the OR that adds $A \\cdot B$ to it. Write $c$, the delay one stage adds to the carry, in terms of $g$.",
                        "answer": "2 \\cdot g",
                        "hint": "Two gates in a line, each of delay $g$. The XOR is not on this path — $p$ was ready before the carry arrived.",
                        "deconstruct": [
                            "The carry enters the AND, so one $g$ elapses before $p \\cdot C_{in}$ is valid.",
                            "That feeds the OR, so a second $g$ elapses. The total is $2g$, and no XOR appears in it.",
                        ],
                    },
                    {
                        "prompt": "The carry into the bottom stage is available at time 0, but nothing can move until the $p$ signals exist at time $x$. After that the carry crosses $n$ stages. Write the time at which the adder's carry out is valid, in terms of $x$, $g$ and $n$.",
                        "answer": "x + 2 \\cdot g \\cdot n",
                        "placeholder": "x + \\ldots",
                        "hint": "Start the clock at $x$, then add one stage delay per bit.",
                        "deconstruct": [
                            "All the $p$ terms settle at $x$, in parallel, however wide the adder is.",
                            "Each of the $n$ stages then adds $c = 2g$, so the carry out is valid at $x + 2gn$.",
                        ],
                    },
                    {
                        "prompt": "The top sum bit is $S_{n-1} = p_{n-1} \\oplus C_{n-1}$, and $C_{n-1}$ — the carry out of the stage below it — is valid at $x + 2g(n-1)$. Write the time at which that last sum bit is valid.",
                        "answer": "2 \\cdot x + 2 \\cdot g \\cdot (n - 1)",
                        "placeholder": "\\ldots + 2 \\cdot g \\cdot (n - 1)",
                        "hint": "Take the arrival time of $C_{n-1}$ and add one more XOR delay.",
                        "deconstruct": [
                            "$C_{n-1}$ has crossed $n - 1$ stages, so it is valid at $x + 2g(n-1)$.",
                            "One XOR converts it into the sum bit, adding another $x$: $2x + 2g(n-1)$.",
                        ],
                    },
                    {
                        "prompt": "Subtract the second time from the first: by how much does the carry out arrive later than the last sum bit?",
                        "given": "carry out at $x + 2gn$, last sum bit at $2x + 2g(n-1)$",
                        "answer": "2 \\cdot g - x",
                        "hint": "The $2gn$ terms very nearly cancel — expand $2g(n-1)$ first and see what is left.",
                        "deconstruct": [
                            "$(x + 2gn) - (2x + 2gn - 2g) = x + 2gn - 2x - 2gn + 2g$.",
                            "The $2gn$ terms cancel and the $x$ terms leave $-x$, so the difference is $2g - x$. Notice it does not contain $n$: the gap between the two outputs is the same at every width, and it is the *cells* that decide which output is last.",
                        ],
                    },
                    {
                        "prompt": "Put $x = 0.25$ ns, $g = 0.15$ ns and $n = 4$ into the carry-out expression. Give the number of nanoseconds.",
                        "answer": "1.45",
                        "hint": "$0.25 + 2 \\times 0.15 \\times 4$.",
                        "deconstruct": [
                            "$2g = 0.30$ ns per stage, and there are 4 stages, so the carry spends 1.20 ns rippling.",
                            "Add the 0.25 ns the $p$ terms needed first: 1.45 ns. The last sum bit was ready at $2(0.25) + 0.30 \\times 3 = 1.40$ ns, so the carry is indeed last, by the $2g - x = 0.05$ ns the previous step predicted.",
                        ],
                    },
                    {
                        "prompt": "Same cells, but a 32-bit adder. Give the carry-out time in nanoseconds.",
                        "answer": "9.85",
                        "hint": "Only $n$ has changed: $0.25 + 0.30 \\times 32$.",
                        "deconstruct": [
                            "$0.30 \\times 32 = 9.60$ ns of rippling.",
                            "Plus the 0.25 ns for the $p$ terms: 9.85 ns, which caps the clock below 102 MHz on the adder alone.",
                        ],
                    },
                ],
                "closing": r'''
Read the shape of the result rather than the numbers. The total is $x + 2gn$: a constant
plus a term **linear in the word length**. Doubling the width doubles the delay, and
there is nothing in the structure that can be tuned to escape that — faster cells shrink
$g$, but the $n$ is architectural.

That is what makes ripple-carry the wrong shape above about eight bits, and it is why
the next thing anyone learns about arithmetic is carry-lookahead. Its trick is worth
seeing in outline even here. Each stage can be described by two signals that depend only
on its own operand bits: it **generates** a carry when $A \cdot B$ is 1, and it
**propagates** one when $p$ is 1. Written out for stage 1,

$$C_2 = G_1 + P_1 C_1 = G_1 + P_1(G_0 + P_0 C_0) = G_1 + P_1 G_0 + P_1 P_0 C_0$$

which is an AND-OR and so reaches $C_2$ two gate delays after the G and P terms exist,
rather than the four the two ripple stages would have taken. Carry on
substituting and every carry in the word becomes a two-level function of the G and P
terms and $C_0$ — flat, fast, and far too wide to build directly beyond a few bits, so
real designs group four bits at a time and build a tree of those groups. The depth then
goes as $\log n$ instead of $n$: a 32-bit lookahead adder settles in about 2 ns where the
ripple version takes 9.85 ns.

The gate count roughly triples. That trade — more silicon for shallower logic — is the
same one the Karnaugh map made in the other direction, and knowing which way to take it
is most of what arithmetic design consists of.
''',
            },
            "build": {
                "title": "Two product terms, wired as two chains",
                "minutes": 24,
                "brief": r'''
A sum of products is a parallel bundle of series chains: **one chain per product term,
one contact per literal**. This is that sentence, in copper.

The function is $F = A \cdot B + A' \cdot C$, and the state to build is $A = 1$,
$B = 1$, $C = 1$. Contact A is closed and is drawn for you as a 120 Ω resistor at the
head of the first chain. Add the rest:

* the second contact of the first chain, **B**, closed, as **180 Ω** in series with the
  120 Ω already there — that chain is the term $A \cdot B$
* the second chain, the term $A' \cdot C$: since A is energised its break contact is
  **open**, which is not an infinite resistance but about **1 MΩ** of grimy air gap,
  in series with contact **C**, closed, at **150 Ω**
* both chains must bridge the *same* gap — from the rail to the shared output node —
  because parallel is what OR means
* a pull-down from that node to ground, so the gate input has a defined level when
  neither chain conducts
* leave the probe on the shared node

Two things have to be true of the finished network:

* the output reads at least **4.60 V**, so the gate downstream sees an unambiguous HIGH
* the rail delivers less than **1 mA**, which is what stops a panel of these from
  costing more current than the logic they feed

There is a range of pull-down values that does both; find where each limit falls before
you choose one. Then, when it passes, try wiring all four contacts in one line instead:
that circuit is $A \cdot B \cdot A' \cdot C$, the output collapses to about 49 mV, and
you have measured $X \cdot X' = 0$.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 12, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 15},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                        {"id": "p3", "kind": "OUT", "x": 20, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 13], "b": [3, 15]},
                        {"a": [3, 11], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [7, 3], "b": [17, 3]},
                        {"a": [17, 3], "b": [20, 3]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 12, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 15},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 120},
                        {"id": "p3", "kind": "OUT", "x": 20, "y": 3},
                        {"id": "p4", "kind": "R", "x": 12, "y": 3, "rot": 0, "value": 180},
                        {"id": "p5", "kind": "R", "x": 6, "y": 7, "rot": 0, "value": 1000000},
                        {"id": "p6", "kind": "R", "x": 12, "y": 7, "rot": 0, "value": 150},
                        {"id": "p7", "kind": "R", "x": 17, "y": 10, "rot": 1, "value": 10000},
                        {"id": "p8", "kind": "GND", "x": 17, "y": 13},
                    ],
                    "wires": [
                        {"a": [3, 13], "b": [3, 15]},
                        {"a": [3, 11], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [3, 7], "b": [5, 7]},
                        {"a": [7, 3], "b": [11, 3]},
                        {"a": [7, 7], "b": [11, 7]},
                        {"a": [13, 3], "b": [17, 3]},
                        {"a": [13, 7], "b": [17, 7]},
                        {"a": [17, 3], "b": [17, 9]},
                        {"a": [17, 11], "b": [17, 13]},
                        {"a": [17, 3], "b": [20, 3]},
                    ],
                },
                "checks": [
                    {"name": "all four contacts are on the board, with the right values", "code": r'''
var rs = c.values('R');
function near(x, want, frac) { return Math.abs(x - want) <= Math.abs(want * frac); }
var a = rs.filter(function (x) { return near(x, 120, 0.02); });
var b = rs.filter(function (x) { return near(x, 180, 0.02); });
var na = rs.filter(function (x) { return near(x, 1e6, 0.02); });
var cc = rs.filter(function (x) { return near(x, 150, 0.02); });
c.assert(a.length === 1 && b.length === 1,
  'The A·B chain is a 120 Ω contact and a 180 Ω contact. Found ' + a.length +
  ' near 120 Ω and ' + b.length + ' near 180 Ω.');
c.assert(na.length === 1 && cc.length === 1,
  'The second chain is a 1 MΩ open contact (the break contact of A) and a 150 Ω closed ' +
  'one (contact C). An open switch is a megohm, not a gap in the drawing — the point of ' +
  'the exercise is to see how little that megohm matters. Found ' + na.length +
  ' near 1 MΩ and ' + cc.length + ' near 150 Ω.');
c.assert(c.count('R') >= 5,
  'Five resistors: four contacts and a pull-down, so the node has a defined level when ' +
  'neither chain conducts.');
'''},
                    {"name": "the probe is on the shared node, not on the rail", "code": r'''
c.assert(Math.abs(c.vout() - 5) > 0.01,
  'The probe is reading the rail itself. Move it to the node the two chains feed, above ' +
  'the pull-down.');
'''},
                    {"name": "one true product term is enough — the output is a solid HIGH", "code": r'''
var v = c.vout();
c.assert(v >= 4.60,
  'The output is ' + c.fmt(v, 'V') + ', and it has to be at least 4.60 V. If it is a few ' +
  'tens of millivolts, all four contacts are in one line, which is the product of A, B, ' +
  'NOT A and C — the megohm is then in the only path there is, and the algebra agrees ' +
  'with the volts. Wire the two chains so that each one bridges the gap on its own.');
'''},
                    {"name": "the second chain is connected at both ends, and leaking", "code": r'''
var d = c.dc();
var open = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 1e6) <= 2e4;
})[0];
c.assert(open, 'The 1 MΩ open contact is missing.');
var i = Math.abs(d.v[open.n1] - d.v[open.n2]) / open.value;
c.assert(i > 1e-9 && i < 1e-4,
  'The open contact is carrying ' + c.fmt(i, 'A') + '. It should carry a small but ' +
  'non-zero current — around 150 nA. Zero means the chain is dangling at one end rather ' +
  'than joining the rail and the output node.');
'''},
                    {"name": "the rail delivers less than 1 mA", "code": r'''
var cur = c.dc().currents;
var mags = Object.keys(cur).map(function (k) { return Math.abs(cur[k]); });
c.assert(mags.length > 0, 'There is no source current to measure — is the rail connected to anything?');
var worst = Math.max.apply(null, mags);
c.assert(worst < 1e-3,
  'The rail is delivering ' + c.fmt(worst, 'A') + '. Raise the pull-down: the current is ' +
  'almost exactly 5 V divided by it, so anything above about 5 kΩ clears 1 mA.');
'''},
                ],
                "hints": [
                    "Series means end to end: the 180 Ω picks up where the 120 Ω finishes, and only the far end of the pair reaches the output node.",
                    "Parallel means both chains span the same two nodes — one end of each on the rail, the other end of each on the shared output node.",
                    "The conducting chain is $120 + 180 = 300$ Ω and the open one is $1\\,000\\,150$ Ω; in parallel they are 299.9 Ω, so the open chain changes nothing measurable. That is the result you are demonstrating.",
                    "The output is $5 \\times R_{\\text{pd}}/(R_{\\text{pd}} + 299.9)$. Reaching 4.60 V needs $R_{\\text{pd}}$ above about 3.4 kΩ.",
                    "The rail current is $5/(R_{\\text{pd}} + 299.9)$, so staying under 1 mA needs $R_{\\text{pd}}$ above 4.70 kΩ. That is the binding limit of the two; 10 kΩ gives 4.854 V and 0.485 mA and clears both comfortably.",
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
            "read": [
                {
                    "title": "Two valleys and a hill: how a circuit acquires a past",
                    "minutes": 10,
                    "body": r'''
Everything in the first three modules had one shape. Put voltages on the input wires,
wait for the gates to settle, read the answer off the output. Ask the same question
twice and you get the same answer twice, because there is nothing inside the circuit
that could tell the second time from the first. That is what **combinational** means,
and it is a harder limitation than it sounds. Such a circuit cannot count, because
counting means knowing what the last number was. It cannot wait for a button, because
waiting means noticing that something happened and continuing to know it afterwards.
It cannot add up a column of figures. It has no yesterday.

This module builds the yesterday, and it takes exactly one new idea to do it: a wire
from an output back round to an input. Everything else in the module — the flip-flop,
the clock, the whole timing discipline that the second half is about — is a consequence
of that one wire.

## Two valleys with a hill between them

Start away from electronics. A light switch on a wall has two resting positions, and if
you push it half way and let go it does not stay half way: it snaps into one of the two.
A doorbell button has one resting position, and whatever you do to it, that is where it
goes back to. The difference is not how many positions you can hold it in with your
finger. It is how many positions it will sit in **on its own**.

Draw the energy of the switch against its angle and the picture is two valleys with a
hill between them. A ball in either valley stays there, and a small nudge rolls it back.
A ball balanced exactly on the crest of the hill also stays there, in the sense that the
forces on it cancel — but the smallest nudge sends it down one side and it does not come
back. Remember the crest. It is not a curiosity; two readings from now it comes back with
a name and a failure rate attached.

Memory is that hill. A device that remembers is one with more than one state it will
hold by itself, and something in between that keeps the states apart.

## The hill, made out of gates

Module 1 said a gate is **restoring**: hand it a voltage a little above its threshold
and it does not pass that voltage on, it manufactures a fresh full-rail output of its
own. Read that as a statement about slopes. Near the threshold a small change at the
input produces a large change at the output — the gate has **gain**, and in the middle
of its range a real CMOS inverter's gain is something like 20 or 30. That gain is the
hill. All that remains is to point it at itself.

Try the crudest version first: one inverter, output wired straight back to its own
input. Follow it round. If the node sits at 0 the inverter drives it to 1; now it is at
1, so the inverter drives it to 0. No value of the node survives a trip round the loop,
so the circuit never settles — it oscillates, at a frequency set by how long the inverter
takes. That is a real and useful circuit, a ring oscillator. It is a completely useless
memory.

Now use two. Call the nodes $P$ and $Q$: inverter X drives $Q$ from $P$, and inverter Y
drives $P$ from $Q$. Test $P = 0$. Then X drives $Q = 1$, and Y, seeing a 1, drives
$P = 0$ — which is where we started. The state is consistent; nothing in the circuit
wants to change it. Test $P = 1$. Then $Q = 0$, and Y drives $P = 1$. Consistent again.
Two states, each of which the pair will sit in indefinitely, and no way to get from one
to the other by waiting. That is one bit of memory, and the rule behind it is worth
keeping:

> An **odd** number of inversions round a loop oscillates. An **even** number latches.

There is a third solution to the loop equations, the one where $P$ and $Q$ are both stuck
at the voltage where an inverter's output equals its own input — around 2.5 V on a 5 V
part. That is the crest of the hill. It satisfies the equations and it is not stable: a
gain of 20 magnifies any disturbance, so a millivolt of noise becomes tens of millivolts
in one trip round the loop, and hundreds in two. Silicon is never quiet enough to stay
there for long.

## Writing to it

The two-inverter ring is a perfect memory and useless, because it has no inputs. To store
a value you have to be able to **overpower** one of the two gates: hold its output where
you want it, whatever the other gate is saying, for long enough that the loop reorganises
itself around the new value.

An inverter cannot be overpowered. It has one input and that input is already spoken for.
So give each gate a second input, chosen so that the pair still behaves as two inverters
when the new inputs are idle. A two-input NOR does exactly that, and the two identities
that matter are these:

$$\text{NOR}(x, 0) = \overline{x + 0} = \overline{x}, \qquad
  \text{NOR}(x, 1) = \overline{x + 1} = 0$$

The first says that with its spare input held at 0 a NOR **is** an inverter, so the ring
still latches. The second says that with its spare input driven to 1 the output is 0 no
matter what the other input does — the gate has been overpowered. One gate type, both
properties, which is why this is the circuit everybody draws.

Cross-couple two of them and name the spare inputs. Put $S$ (set) on the gate that
produces $\overline{Q}$ and $R$ (reset) on the gate that produces $Q$:

$$Q = \overline{R + \overline{Q}}, \qquad \overline{Q} = \overline{S + Q}$$

That is the **SR latch**. Every one of its four input combinations can now be read off
the two identities rather than memorised:

```
 S  R | what the gates do                                     | Q afterwards
 -----+-------------------------------------------------------+--------------
 0  0 | both spare inputs idle: it is the inverter ring        | unchanged
 1  0 | S overpowers its gate, Q' = 0, so Q = NOR(0, 0) = 1    | 1
 0  1 | R overpowers its gate, Q = 0, so Q' = NOR(0, 0) = 1    | 0
 1  1 | both gates overpowered: Q = 0 and Q' = 0 together      | 0, and not the
       |                                                       | complement of Q'
```

## Worked example 1 — a set pulse, in nanoseconds

Give each NOR a propagation delay of 3 ns. Start with the latch storing a 0, so $Q = 0$
and $\overline{Q} = 1$, with $S = R = 0$. At $t = 0$ the S input rises to 1 and stays
there for 20 ns.

```
 t =  0 ns   S goes to 1
 t =  3 ns   the gate with S on it now has an input at 1, so Q' falls from 1 to 0
 t =  6 ns   the other gate now sees R = 0 and Q' = 0, so Q rises from 0 to 1
 t =  6 ns   the first gate re-evaluates: NOR(S=1, Q=1) = 0. It is already 0. Nothing moves.
 t = 20 ns   S returns to 0
 t = 23 ns   the first gate re-evaluates: NOR(S=0, Q=1) = 0. Still 0. Nothing moves.
```

Two gate delays — 6 ns — to write the bit. Then read the last line again, because it is
the entire point of the circuit. When S is removed, **nothing happens**. The gate that S
was overpowering is now being held down by $Q$ instead, and $Q$ is being held up by that
gate. The latch is not remembering the input. It is holding itself up by its own
bootstraps, and the input has become irrelevant the moment the loop closed round the new
value.

That also gives the algebra. Substituting one equation into the other,

$$Q_{\text{next}} = \overline{R + \overline{S + Q}} = \overline{R} \cdot (S + Q)
= S\overline{R} + Q\overline{R}$$

which is a perfectly ordinary Boolean expression of module 2 — in three variables, of
which one is the latch's **own previous output**. That is the whole trick written down: a
sequential circuit is a combinational circuit with its own past fed in as an extra input.
Every state machine in module 9 is built on that sentence.

## Worked example 2 — the forbidden combination, and the race that follows

Set $S = R = 1$. Both gates are overpowered, both outputs go to 0, and $Q$ and
$\overline{Q}$ — which are supposed to be complements, and whose names say so — are equal.
That is bad but it is not the damage. The damage is what happens on the way out.

Take both inputs to 0 at the same instant, $t = 0$. Both gates now see 0 on both of their
inputs and both want to output 1. They will not manage it at the same moment, because no
two gates on a real die are identical. Say gate X takes 3.0 ns and gate Y takes 3.2 ns.

```
 t = 0.0 ns   S and R both fall to 0; both gates begin driving their outputs up
 t = 3.0 ns   X wins: Q reaches 1
 t = 3.0 ns   Y's input has just changed — it now sees Q = 1, so its output must be 0.
              The 0 -> 1 transition it had 0.2 ns left to complete is cancelled.
 settled      Q = 1, Q' = 0
```

Swap the two delays and the latch settles the other way. The stored value is decided by a
0.2 ns manufacturing difference between two gates — not by anything the designer wrote
down. And if the two were exactly matched, both outputs would rise together, both gates
would then see a 1 and start back down together, and the pair would sit on the crest of
the hill. That is the third solution to the loop equations, arrived at deliberately.

## The mistake people make

Two of them, and they have the same root.

The first is reading the S = R = 0 row as if it were an output value. Every truth table in
modules 1 to 3 had a 0 or a 1 in every output cell. This one has the word *unchanged*,
which is not a value at all — it is a reference to the past. The temptation is real,
because the table looks exactly like the tables that came before it. It is not one of
them: the latch's behaviour cannot be written as a function of S and R, only as a function
of S, R and the previous $Q$, which is precisely what the algebra above says.

The second is reading S = R = 1 as "it does both, so it does nothing". It does something
perfectly definite while it lasts: both outputs go to 0. What is undefined is only the
state it lands in afterwards, and "undefined" here means genuinely decided by picoseconds
of manufacturing spread, not merely unspecified in a textbook.

## Where this stops holding

The SR latch listens all the time. It has no notion of *when*, and that turns out to be
fatal in two separate ways.

A glitch writes it permanently. Module 3's hazards are exactly this: two paths through a
piece of combinational logic disagree for a few nanoseconds while one of them catches up,
and the output spikes. Feed a hazard-prone output into S and the latch is set by a signal
that was never supposed to exist, with nothing anywhere to undo it. A memory that can be
written by a glitch is not a memory.

And latches cannot be chained. Wire the output of one into the inputs of the next and the
moment the first changes, so does the second, and so does the third — a value cannot be
made to move one place per step, because nothing defines what a step is.

Both faults have the same shape. The latch answers *what* and nothing at all answers
*when*. Add a wire whose job is to say when, and the next reading gets first a latch you
can shut and then a flip-flop that is only ever open for an instant.
''',
                },
                {
                    "title": "From a window to an instant: the D latch and the flip-flop",
                    "minutes": 11,
                    "body": r'''
The SR latch has two control inputs for one bit of storage, and it listens continuously.
Both faults are cured by adding gates in front of it, and it is worth doing them in that
order, because the second fix is the one the rest of digital design is built on.

## One data wire instead of two

Of the four combinations of S and R, one is forbidden and one means "do nothing", so only
two are useful — and those two are exactly *store a 1* and *store a 0*. Two useful cases
is one bit of information, so two wires is one wire too many. Generate both from a single
data line $D$:

$$S = D, \qquad R = \overline{D}$$

Now $S$ and $R$ are never both 1, not by discipline but by construction: it would need $D$
to be 1 and 0 at the same time. The forbidden state has been designed out of existence.
The latch now stores $D$ — continuously, which is the second fault, untouched.

## A wire that says when

Add an enable, $EN$, ANDed into both:

$$S = D \cdot EN, \qquad R = \overline{D} \cdot EN$$

Four cases, and all four fall out of the two AND gates:

* $EN = 0$: both $S$ and $R$ are 0 whatever $D$ does, so the latch holds. The data input
  has been disconnected.
* $EN = 1$, $D = 1$: $S = 1$, $R = 0$ — set. $Q$ becomes 1.
* $EN = 1$, $D = 0$: $S = 0$, $R = 1$ — reset. $Q$ becomes 0.
* $S = R = 1$ would need $D \cdot EN = 1$ and $\overline{D} \cdot EN = 1$ together, so it
  cannot occur however the inputs are driven.

This is the **transparent D latch**, and the name describes it exactly. While $EN$ is 1
the output is a copy of the input, delayed by a couple of gates and otherwise following
every wiggle. When $EN$ falls the last value is trapped. Two modes: a window while the
enable is high, and a lock the moment it goes low.

That is a genuine improvement — the latch can no longer be written by a glitch that
arrives while the enable is low, which is most of the time. It still cannot be chained,
and the reason is worth working out in numbers rather than words.

## Worked example 1 — why a chain of latches is a lottery

Two D latches in a row, the output of the first feeding the input of the second, both
enabled by the same clock. Say the latch takes 12 ns from a change at $D$ to the matching
change at $Q$ while it is transparent, and the clock's high phase lasts 40 ns.

```
 t =  0 ns   the enable goes high; latch 1's input holds the value A
 t = 12 ns   latch 1's output becomes A  -- which is latch 2's input
 t = 24 ns   latch 2's output becomes A as well
 t = 40 ns   the enable falls. Both latches are now holding A.
```

The value crossed **two** stages in one clock phase. A three-latch chain: 36 ns, still
inside the 40 ns window, so it crosses three. A four-latch chain: 48 ns, so it crosses
three and stops part way into the fourth.

So the number of stages a value advances per clock is not one. It is however many fit
inside the high phase — and gate delays change with temperature, with supply voltage and
from one part to the next, so it is a number that changes while the equipment is running.
That is not a shift register. That is a lottery.

Notice what a fix would have to look like. To make the chain advance exactly one stage per
clock you would have to guarantee that the latch delay is **at least** 40 ns, and a
guaranteed *minimum* delay is the hardest thing in electronics to buy: a fast part is
always allowed to be faster than its datasheet suggests, and it is faster still when it is
cold. Designing something to work because a component is slow enough is designing on sand.

## The fix: never have both halves open at once

Put two latches in series with **opposite** enables. The first — call it the master — is
transparent while the clock is 0. The second, the slave, is transparent while the clock is
1. Now walk one clock cycle:

* **Clock low.** Master transparent, tracking $D$. Slave shut, holding the previous value
  at the output. Whatever $D$ does, it stops at the slave's closed door.
* **Clock rises.** The master shuts, trapping whatever $D$ happened to be at that instant.
  The slave opens and passes that trapped value out.
* **Clock high.** Master shut, so changes on $D$ go nowhere at all. The slave is
  transparent, but its input is the master's frozen output, so nothing moves.
* **Clock falls.** The slave shuts, holding the captured value at the output for the whole
  of the next low phase. The master reopens and starts tracking $D$ again.

At no instant in that cycle is there a transparent path from $D$ to $Q$. Exactly one door
is open at a time, and the handover happens at the edge. The output changes once per
cycle, at the rising edge, and the value it changes to is the value $D$ had at that edge.

That is an **edge-triggered D flip-flop** — positive-edge triggered, in this arrangement;
swap the two enables and it triggers on the falling edge. It costs two latches instead of
one. Memory that is safe to compose costs twice what memory that is not costs, and it is
one of the better bargains in the subject.

## Worked example 2 — three flip-flops, four edges

A 3-bit shift register: stage 1 takes an input line, stage 2 takes $Q_1$, stage 3 takes
$Q_2$, all three clocked together. Everything starts at 0, and the input line carries
1, 0, 1, 1 on four successive rising edges. Values are recorded **after** each edge.

```
 edge | in | Q1  Q2  Q3
 -----+----+------------
   -  |  - |  0   0   0
   1  |  1 |  1   0   0
   2  |  0 |  0   1   0
   3  |  1 |  1   0   1
   4  |  1 |  1   1   0
```

Take edge 3 apart, since it is the one that shows what is happening. Before it,
$Q_1 = 0$, $Q_2 = 1$, $Q_3 = 0$. All three flip-flops capture at the same instant: stage 1
captures the input line, which is 1; stage 2 captures $Q_1$, which is 0 — the value $Q_1$
had *before* the edge; stage 3 captures $Q_2$, which is 1. Afterwards: 1, 0, 1.

Every stage read the value its neighbour held before the edge, even though all three
neighbours changed at that same edge. The reason is a delay: a flip-flop's output does not
move until $t_{cq}$ after the edge, and by then every flip-flop has already captured. The
old values were still on the wires while the capturing was going on. With transparent
latches this table cannot be written down at all, because there is no instant at which the
values are unambiguously old.

## Setup and hold, from the inside

That last paragraph should make you suspicious, and it should. It says the design works
because of a race — the capture beats the output change — and a race that is not written
down is a race you eventually lose. Both sides of it have names.

Look at what the master latch has to do at the rising edge. It has to be **already
settled** on the value of $D$, because the instant its enable goes away the cross-coupled
pair keeps whatever it happens to be holding, and getting the loop to close round a new
value takes a couple of gate delays. So $D$ must have arrived and the master must have
latched onto it some time before the edge. That lead time is the **setup time**,
$t_{su}$.

And the enable does not vanish instantly either. For a short while after the edge the
master is still partly listening, so $D$ has to stay put a little longer. That is the
**hold time**, $t_{h}$.

Together they carve out a window around the edge, from $t_{su}$ before it to $t_{h}$
after it, in which $D$ must not move. Outside the window $D$ can do whatever it likes —
and that is what makes a synchronous design analysable. A requirement about a whole clock
phase, which the latch imposed and which nothing can check, has been replaced by a
requirement about a window of a few nanoseconds, which a tool can check on every path in
the design.

For scale: a 74HC74 flip-flop running at 5 V asks for something like 12 ns of setup and
3 ns of hold, and takes up to 25 ns from the clock edge to a settled output. A modern
logic family is a hundred times faster than that. The shape of the specification is
identical — three numbers, two before the edge and one after — and so is everything you do
with them.

## The mistake people make

*"The flip-flop samples $D$ at the edge, so $D$ only has to be right at the edge."*

It has to be right for a window **around** the edge, and the width of that window is
printed on the datasheet in nanoseconds. The temptation is the word *instant*: a
mathematical instant has no width, so a requirement stated at an instant sounds like no
requirement at all. But the master latch is a physical loop that takes time to make up its
mind, and the window is exactly the time it takes.

The second mistake is treating hold time as the flip-flop's own problem. It is not. It is
a race between two paths that start at the same clock edge — the data path out of the
launching flip-flop and through the logic, against the clock path to the capturing
flip-flop — and both of those are the designer's to control. The next reading turns that
race into an inequality.

## Where this stops holding

Everything above assumed the clock edge is fast and clean. Two ordinary ways it is not.

**A slow edge.** The master and the slave do not switch at exactly the same voltage, so
during a slow transition there is a band in which both are part-way open. If the edge
takes longer to cross that band than the delay through the master, a value can leak all
the way through and the flip-flop stops being edge-triggered at all. This is why
datasheets carry a maximum clock rise time — the 74HC family quotes hundreds of
nanoseconds — and why a clock that has travelled down a long, heavily loaded track gets a
Schmitt-trigger buffer before it is used.

**A bouncing edge.** A mechanical switch wired straight to a clock input does not produce
one edge. It produces dozens over a few milliseconds as the contacts settle, and a counter
clocked from a bare pushbutton advances by a random number every press. The cure is to
debounce the switch, which usually means an RC and a Schmitt trigger, or a small state
machine that ignores changes for a few milliseconds after each one it accepts.

And then the deep one. If $D$ moves inside the setup-and-hold window, the flip-flop is
being asked to decide something it has no basis for deciding, and what it does is the
crest of the hill from the previous reading. That is where the last section of the next
reading ends up.
''',
                },
                {
                    "title": "The clock is a budget, and two inequalities spend it",
                    "minutes": 13,
                    "body": r'''
A flip-flop's setup and hold times are numbers on a datasheet, but they are only half the
story: they say what the flip-flop needs, not whether the circuit around it delivers.
Turning that into a clock frequency needs one more ingredient — how long a signal takes to
get anywhere — and that has a physical answer worth deriving rather than quoting.

## Why anything takes time at all

Any two conductors separated by an insulator form a capacitor. A track running over a
ground plane is one. Two tracks side by side are another. And most of all, the gate of
every MOS transistor a signal is driving is one: a metal plate over a thin insulator over
silicon, which is a capacitor in the most literal possible sense. A CMOS logic input is a
few picofarads, and a short track adds a few more.

Nothing charges instantly, because charge has to be carried onto the plate: $q = Cv$, so
changing a capacitor's voltage means moving charge, and the current available to move it
is limited by the resistance of whatever is driving — tens to hundreds of ohms for a
transistor that is switched on.

So a gate output does not step. It ramps, and the gate downstream does not call it a 1
until the voltage climbs past its own threshold. That climb is the **propagation delay**,
and every timing number in this module is ultimately made of it.

## The charging law

Model the driver as a voltage $V$ behind a resistance $R$, and the load as a capacitance
$C$ from the node to ground. Two facts, one for each component:

$$i = C \frac{dv}{dt}, \qquad i = \frac{V - v}{R}$$

Set them equal and separate the variables:

$$RC \frac{dv}{dt} = V - v \quad \Longrightarrow \quad \frac{dv}{V - v} = \frac{dt}{RC}$$

Integrating from $v = 0$ at $t = 0$ gives $-\ln\!\left(\frac{V-v}{V}\right) = \frac{t}{RC}$,
and rearranging:

$$v(t) = V\left(1 - e^{-t/RC}\right)$$

The product $RC$ has units of seconds, which is worth checking once and never again: a
farad is a coulomb per volt and an ohm is a volt per amp, so
$\Omega \cdot \text{F} = \frac{\text{V}}{\text{A}} \cdot \frac{\text{C}}{\text{V}} =
\frac{\text{C}}{\text{A}} = \text{s}$. Call it $\tau$.

The receiving gate does not care about the curve. It cares about the moment the voltage
crosses its threshold, and a CMOS inverter with matched transistors switches close to half
the supply. Put $v = V/2$:

$$\frac{V}{2} = V\left(1 - e^{-t/\tau}\right) \;\Longrightarrow\; e^{-t/\tau} = \frac{1}{2}
\;\Longrightarrow\; t_{pd} = \tau \ln 2 \approx 0.693\,RC$$

Look at what dropped out. The supply voltage cancelled: in this model doubling the rail
does not change the delay at all, because the drive and the threshold scale together.

One generalisation will be needed later. If the node does not end up at the full rail —
because something else is pulling on it — write $V_f$ for the value it does settle at and
solve the same equation for an arbitrary threshold $V_{th}$:

$$t = \tau \ln\!\left(\frac{V_f}{V_f - V_{th}}\right)$$

with $\tau$ now the capacitance times the resistance seen looking out of the node, which
is the parallel combination of everything attached to it. If $V_f$ is *below* $V_{th}$ the
logarithm's argument turns negative and there is no answer, which is the algebra's way of
saying the node never crosses at all. That is not a curiosity: it is a pull-up too weak
for its load, and a gate downstream that never sees a 1 however long you wait.

## Worked example 1 — fanout

A gate with 250 Ω of output resistance drives five logic inputs of 4 pF each, along a
track that contributes 10 pF of its own.

```
 total load       C   = 5 x 4 pF + 10 pF      = 30 pF
 time constant    tau = 250 ohm x 30 pF       = 7.5 ns
 delay to V/2     t   = 0.693 x 7.5 ns        = 5.20 ns
```

Now hang three more inputs on the same node:

```
 total load       C   = 8 x 4 pF + 10 pF      = 42 pF
 time constant    tau = 250 ohm x 42 pF       = 10.5 ns
 delay to V/2     t   = 0.693 x 10.5 ns       = 7.28 ns
```

Sixty per cent more loads, forty per cent more delay — the track's own 10 pF dilutes the
effect, which is why the second number is not simply 8/5 of the first. That is the whole
of fanout: capacitances on one node add, the delay is proportional to their total, and the
designer has two levers. Fewer loads per node, or a smaller $R$ — a bigger driver.
Inserting a buffer to split a heavily loaded net is buying a smaller $R$ at the price of
one more gate delay, and it starts paying as soon as the load is large enough that the
saving beats the buffer.

## The loop that sets the clock

Now the budget. Two flip-flops with combinational logic between them and one clock to
both. Follow a single clock edge all the way round:

1. the edge reaches flip-flop 1, whose output takes $t_{cq}$ to change — the
   **clock-to-output** delay;
2. the new value crosses the logic, taking up to $t_{pd}$, and it must be the **longest**
   path, because the result is not trustworthy until the slowest input has arrived;
3. it has to be sitting still at flip-flop 2's input for $t_{su}$ before the *next* edge.

All three have to fit inside one period:

$$T \ge t_{cq} + t_{pd} + t_{su}$$

## Worked example 2 — a clock frequency, and the slack at a slower one

```
 clock-to-output of the launching flip-flop   t_cq = 0.40 ns
 longest path through the logic               t_pd = 4.35 ns
 setup time of the capturing flip-flop        t_su = 0.25 ns
 ---------------------------------------------------------
 shortest workable period                     T    = 5.00 ns
 fastest clock                                f    = 1 / 5.00 ns  = 200 MHz
```

Run the same circuit from a 6.00 ns clock — 166.7 MHz — and there is 1.00 ns to spare.
That spare time is called **slack**, and it is the number every timing tool prints. Zero or
positive means the path works; negative by any amount at all means it does not, and the
size of the negative number tells you how much delay has to come out.

The commonest mistake in this whole module lives right here: quoting $t_{pd}$ on its own.
4.35 ns "is" 230 MHz, and the circuit stops working at 201 MHz. The flip-flop overheads are
0.65 ns of the 5.00 ns period — thirteen per cent — and that fraction grows as the logic
between stages is made shorter, which is why cutting a design into ever more pipeline
stages eventually stops making it faster. The derivation in this module puts a number on
exactly that.

## The other inequality, and the surprise in it

Nothing above stops the data arriving too **early**. Follow the same edge again, but along
the fastest route this time: $t_{cq}$ at its minimum, then the shortest path through the
logic — the **contamination delay** $t_{cd}$, meaning the earliest the output can begin to
move, as opposed to the latest it settles. If that new value reaches flip-flop 2 while
flip-flop 2 is still holding its input steady for $t_h$ after the same edge, flip-flop 2
captures the new value instead of the old one, and a stage of the pipeline has been
skipped:

$$t_{cq,\min} + t_{cd} \ge t_h$$

Now look at what is missing from that inequality. **$T$ does not appear.** A hold violation
cannot be fixed by slowing the clock down — not at 10 MHz, not at 1 Hz — and that is the
single most surprising fact in synchronous design. A board that misbehaves at every clock
frequency you try, including absurdly slow ones, has a hold problem and no amount of
turning the crank more slowly will help. The fixes are to make the short path *longer*, by
inserting buffers whose only purpose is to waste time, or to repair the clock
distribution. Deliberately adding delay feels wrong the first ten times you do it.

```
 fastest clock-to-output                    t_cq,min = 0.15 ns
 shortest path through the logic            t_cd     = 0.10 ns
 ---------------------------------------------------------
 earliest the new data can arrive                    = 0.25 ns
 hold time required                         t_h      = 0.12 ns
 margin                                              = 0.13 ns   -> passes
```

## Skew, which helps one inequality and hurts the other

So far the clock was assumed to arrive everywhere at once. It does not: it travels down
tracks, through buffers, and reaches different flip-flops at different times. Define

$$t_{skew} = (\text{edge arrives at the capturing flop}) - (\text{edge arrives at the launching flop})$$

and put it into both constraints. A late capture edge gives the data more time to arrive,
so it helps setup; and it also extends the period during which the capturing flop wants its
input held still, so it hurts hold:

$$T + t_{skew} \ge t_{cq} + t_{pd} + t_{su}, \qquad
  t_{cq,\min} + t_{cd} \ge t_h + t_{skew}$$

Take the circuit from the two worked examples above and let the capture clock arrive
300 ps late:

```
 setup:  T >= 5.00 - 0.30 = 4.70 ns   ->  213 MHz, faster than before
 hold :  need 0.25 >= 0.12 + 0.30 = 0.42 ns   ->  short by 0.17 ns, broken
```

Three hundred picoseconds of clock skew has made the design faster on paper and
non-functional in fact. This is why clock distribution is not wiring but engineering — a
balanced tree of matched buffers, laid out so that every leaf is the same distance from the
root — and why *"just put a buffer in the clock line to that corner of the board"* is a
sentence to be suspicious of.

## Where the budget stops applying

Everything above is deterministic. Numbers add up, an inequality either holds or it does
not, and a tool can check every path. All of it rests on one assumption: that $D$ is stable
through the window around every edge. And that assumption is exactly what a signal from
outside your clock domain cannot give you. A button, a line from another board, a second
oscillator — none of them knows where your edges are, so sooner or later one of them
changes inside the window.

When that happens the master latch is left balanced near the crest of the hill from the
first reading. The loop gain then drives it off, and the departure from balance grows
exponentially, like $e^{t/\tau}$ with $\tau$ a property of the cell of the order of a
fraction of a gate delay. Nothing bounds how long it takes to resolve, because nothing
bounds how close to the crest it started.

So the question stops being *does it work* and becomes *how often does it fail*. The
standard model of the mean time between failures is

$$\text{MTBF} = \frac{e^{t_r / \tau}}{T_0 \, f_c \, f_d}$$

where $t_r$ is the time the metastable output is given to resolve before anything reads it,
$\tau$ and $T_0$ are two numbers characterising the flip-flop, $f_c$ is the clock frequency
and $f_d$ is the rate at which the asynchronous input changes.

## Worked example 3 — a failure every minute, and the flip-flop that fixes it

Take $\tau = 0.10$ ns and $T_0 = 0.5$ ns, a 500 MHz clock so $T = 2.00$ ns, an
asynchronous input changing 10 million times a second, and 0.10 ns of setup time on
whatever reads the result.

```
 one flip-flop
   resolving time    t_r = 2.00 - 0.10                     = 1.90 ns
   exponent          t_r / tau = 1.90 / 0.10               = 19
   e^19                                                    = 1.78e8
   T0 x fc x fd = 0.5e-9 s x 5e8 Hz x 1e7 Hz               = 2.5e6 per second
   MTBF = 1.78e8 / 2.5e6                                   = 71 seconds
```

Seventy-one seconds. A product that falls over roughly once a minute is not a product. Now
add a second flip-flop after the first, clocked by the same clock, and read only the second
one's output. The metastable state at the first flip-flop's output now has an entire extra
period to sort itself out before anything looks at it:

```
 two flip-flops
   resolving time    t_r = 2.00 + 1.90                     = 3.90 ns
   exponent          3.90 / 0.10                           = 39
   e^39                                                    = 8.66e16
   MTBF = 8.66e16 / 2.5e6                                  = 3.5e10 s, about 1100 years
```

One extra flip-flop, one extra clock cycle of latency, and a failure every minute becomes a
failure every eleven centuries. The exponential is doing all the work: every extra $\tau$ of
resolving time multiplies the MTBF by $e$, so the fix is cheap and enormous at the same
time. That two-flop arrangement is called a **synchroniser**, and it is not optional at any
asynchronous boundary.

Two limits worth naming before leaving it. A synchroniser makes a single wire safe and does
nothing whatever for a bus, because two wires can resolve to values captured from different
instants and hand you a word that was never sent — buses across a clock boundary need a
handshake, or a FIFO with Gray-coded pointers, so that only one bit can be in doubt at a
time. And the lumped $RC$ picture this reading started from fails once a signal's rise time
becomes short compared with the time it takes a wave to cross the track. Above a few
hundred megahertz on a board of any size, a wire stops being a capacitor and becomes a
transmission line with a characteristic impedance and reflections, the delay stops being
$0.693\,RC$ and becomes length divided by wave speed, and an unterminated track will ring
badly enough to clock a flip-flop twice. That is a different subject, and it begins exactly
where this one stops.
''',
                },
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
            "blanks": {
                "title": "A timing report with the numbers taken out",
                "minutes": 10,
                "caption": "one path, two checks, and the one of them a slower clock cannot help",
                "lang": "text",
                "brief": r'''
This is what a static timing analyser prints for a single path: the route a signal takes
from one flip-flop, through some logic, to the next, checked twice. The **setup** check
adds up the slow route and asks whether it fits in a period. The **hold** check adds up
the fast route and asks whether it arrives too soon after the same edge.

Every line is either a datasheet number or a sum of the lines above it. Fill in the sums,
then answer the question at the bottom, which is the one people get wrong.

Slack is *what you have* minus *what you need*, so a positive slack passes and a negative
one fails.
''',
                "listing": """timing report, path FF1 -> and2 -> or2 -> FF2         clock period 10.00 ns

  setup check  (the late route: worst case everywhere)
    clock-to-Q of FF1, worst case                1.80 ns
    combinational delay, longest route           6.40 ns
    setup time of FF2                            0.90 ns
    --------------------------------------------------
    data must be settled by                       ___ ns after the launching edge
    period available                            10.00 ns
    setup slack                                   ___ ns

  hold check  (the early route: best case everywhere)
    clock-to-Q of FF1, best case                 0.25 ns
    combinational delay, shortest route          0.15 ns
    --------------------------------------------------
    earliest the new data can arrive              ___ ns after that same edge
    hold time of FF2                             0.55 ns
    hold slack                                    ___ ns

  the clock is now slowed to 20.00 ns.  the hold slack becomes  ___ ns
""",
                "blanks": [
                    {
                        "prompt": "Add the three lines of the late route. How long after the launching edge is the data guaranteed to be settled and stable at FF2?",
                        "hole": "?",
                        "opts": ["7.30", "8.20", "9.10", "10.00"],
                        "a": 2,
                        "why": "$1.80 + 6.40 + 0.90 = 9.10$ ns. All three belong in the sum: the launching "
                               "flip-flop's own delay before anything leaves it, the logic, and then the "
                               "quiet time the capturing flip-flop demands before the next edge. Leaving "
                               "the setup time out gives 8.20, leaving the clock-to-Q out gives 7.30, and "
                               "10.00 is the clock period, which is what this sum is about to be compared "
                               "against rather than part of it.",
                    },
                    {
                        "prompt": "The period is 10.00 ns and the data needs 9.10 ns. What is the setup slack?",
                        "hole": "?",
                        "opts": ["0.90", "3.60", "-0.90", "0.00"],
                        "a": 0,
                        "why": "$10.00 - 9.10 = 0.90$ ns, and it is positive, so the path passes with "
                               "0.90 ns in hand — the clock could be tightened to 9.10 ns before this path "
                               "became the limit. 3.60 comes from subtracting only the logic delay and "
                               "forgetting that the flip-flops charge for their own overheads too. A "
                               "negative slack would mean the sum had exceeded the period.",
                    },
                    {
                        "prompt": "Now the early route. The same edge launches the data; how soon can the change reach FF2's input?",
                        "hole": "?",
                        "opts": ["0.15", "0.40", "0.55", "2.20"],
                        "a": 1,
                        "why": "$0.25 + 0.15 = 0.40$ ns. Both numbers are best-case, because a hold check is "
                               "a question about how *early* something can happen, and the earliest arrival "
                               "uses the fastest clock-to-Q and the shortest route through the logic. Using "
                               "0.15 alone forgets that the data cannot leave FF1 before FF1's output moves. "
                               "Note that the shortest route through the logic is a different physical path "
                               "from the longest one used in the setup check — the two checks are about "
                               "different wires.",
                    },
                    {
                        "prompt": "FF2 needs its input held for 0.55 ns after the edge, and the new data can arrive as early as 0.40 ns. What is the hold slack?",
                        "hole": "?",
                        "opts": ["-0.15", "0.15", "0.40", "0.95"],
                        "a": 0,
                        "why": "$0.40 - 0.55 = -0.15$ ns. Negative, so the path fails: the new value can "
                               "reach FF2 while FF2 is still supposed to be seeing the old one, and FF2 may "
                               "capture data meant for the following cycle. Getting $+0.15$ means the "
                               "subtraction was done the other way round — slack is always *what you have* "
                               "minus *what you need*, and here the 0.40 ns you have is less than the "
                               "0.55 ns demanded.",
                    },
                    {
                        "prompt": "The clock is halved in speed to a 20.00 ns period. What does the hold slack become?",
                        "hole": "?",
                        "opts": ["-0.15", "0.00", "9.85", "10.15"],
                        "a": 0,
                        "why": "Still $-0.15$ ns. Nothing changed, because the clock period does not appear "
                               "anywhere in a hold calculation: both sides of it are measured from the same "
                               "edge, and how long until the *next* edge is irrelevant. This is the single "
                               "most useful thing to know about hold violations — a board that fails at "
                               "every clock frequency you try, including a hand-pressed button, has one. "
                               "The 9.85 and 10.15 answers come from folding the extra 10 ns of period into "
                               "the sum, which is the setup check's arithmetic applied where it does not "
                               "belong. The fix is to make the *short path longer*, by inserting buffers "
                               "whose only purpose is to waste 0.15 ns, or to repair the clock tree that "
                               "made the two edges disagree.",
                    },
                ],
            },
            "numeric": [
                {
                    "title": "The fastest this pair of flip-flops can be clocked",
                    "minutes": 5,
                    "brief": r'''
One rule, applied once. A clock edge has to do three things in a row before the next edge
arrives: get a value out of the launching flip-flop, push it through the logic, and leave
it standing still long enough for the capturing flip-flop to take it.

$$T \ge t_{cq} + t_{pd} + t_{su}$$

Add the three, then turn a period into a frequency.
''',
                    "prompt": "What is the highest clock frequency this path allows?",
                    "note": "Give the answer in megahertz, to two decimal places.",
                    "figure": "Two flip-flops on the same clock, with a block of combinational logic "
                              "between them. The launching flip-flop's datasheet allows up to 2.4 ns from "
                              "the clock edge to a settled output. Static timing analysis reports the "
                              "longest path through the logic as 11.3 ns. The capturing flip-flop needs "
                              "its input steady for 1.3 ns before the edge that takes it. The clock "
                              "reaches both flip-flops at the same instant.",
                    "given": [
                        {"label": "Clock-to-output, launching flop", "value": "2.4 ns"},
                        {"label": "Longest path through the logic", "value": "11.3 ns"},
                        {"label": "Setup time, capturing flop", "value": "1.3 ns"},
                        {"label": "Clock skew", "value": "negligible"},
                    ],
                    "aside": "A period in nanoseconds inverts to a frequency in gigahertz, so divide by "
                             "1000 at the end — or remember that 10 ns is 100 MHz and scale from there.",
                    "answer": 66.67,
                    "tol": 0.05,
                    "unit": "MHz",
                    "hint": "Add the three delays to get the shortest workable period, then take the "
                            "reciprocal.",
                    "wrong": "If you got 88.50 MHz, only the logic was counted — that is $1/11.3$ ns, and "
                             "it is the commonest wrong answer in the whole of timing analysis. If you got "
                             "72.99 MHz, the setup time was dropped and the period taken as 13.7 ns. If "
                             "you got 15, that is the period in nanoseconds; the question asked for the "
                             "frequency.",
                    "why": "The three delays are in series round one loop, so they add: "
                           "$2.4 + 11.3 + 1.3 = 15.0$ ns is the shortest period at which the value still "
                           "arrives in time. The frequency is $1/15.0\\,\\text{ns} = 66.67$ MHz. Worth "
                           "noticing how much of the budget the flip-flops themselves took: 3.7 ns of the "
                           "15.0, very nearly a quarter, and none of it doing any logic. That fraction is "
                           "what limits how finely a design can be pipelined — cut the 11.3 ns of logic in "
                           "half and the period falls to 9.35 ns rather than 7.5 ns, because the 3.7 ns of "
                           "overhead is charged again in full.",
                },
                {
                    "title": "The violation that a slower clock will not fix",
                    "minutes": 8,
                    "brief": r'''
The other check, and the one that catches people out. A hold violation is not about the
data arriving too late; it is about the data arriving too **early** — soon enough after a
clock edge that the capturing flip-flop is still holding its input steady from that same
edge, and captures the new value a cycle before it should.

$$t_{cq,\min} + t_{cd} \ge t_h + t_{skew}$$

Both sides are measured from one edge. Everything on the left is best case, because the
question is how soon a change *can* arrive. $t_{cd}$ is the **contamination delay**: the
earliest the logic's output can begin to move, along its shortest path, which is a
different physical route from the longest one.

$t_{skew}$ is how much later the clock edge reaches the capturing flip-flop than the
launching one. A late capture edge extends the period during which that flip-flop wants
its input undisturbed, so it makes the requirement harder.

The path below fails. The fix is to insert buffers into the short route until it passes,
which means finding out how much delay is missing.
''',
                    "prompt": "How much delay must be added to the short path to bring the hold check to exactly zero margin?",
                    "note": "Give the answer in nanoseconds, to two decimal places.",
                    "figure": "One path between two flip-flops on the same clock. The launching flip-flop "
                              "can begin to change its output as soon as 0.32 ns after the clock edge. The "
                              "shortest route through the combinational logic contributes as little as "
                              "0.18 ns. The capturing flip-flop requires its input to stay unchanged for "
                              "0.75 ns after the edge, and the clock tree delivers the edge to it 0.14 ns "
                              "later than it delivers it to the launching flip-flop.",
                    "given": [
                        {"label": "Clock-to-output, best case", "value": "0.32 ns"},
                        {"label": "Contamination delay of the logic", "value": "0.18 ns"},
                        {"label": "Hold time required", "value": "0.75 ns"},
                        {"label": "Clock skew (capture edge later)", "value": "0.14 ns"},
                    ],
                    "aside": "The clock period is not stated anywhere in this question, and it is not "
                             "needed. Whatever answer you get is the same at every clock frequency.",
                    "hint": "Work out the two sides separately: what the data path actually delivers, and "
                            "what the flip-flop demands once the skew is included. The gap between them is "
                            "what has to be made up.",
                    "answer": 0.39,
                    "tol": 0.005,
                    "unit": "ns",
                    "wrong": "If you got 0.25 ns, the skew was left out and only $0.75 - 0.50$ was taken. "
                             "If you got 0.11 ns, the skew was subtracted instead of added — but an edge "
                             "that arrives at the capturing flip-flop *later* keeps that flip-flop "
                             "listening for longer, so it makes the hold requirement worse, not better. If "
                             "you got 0.89 ns, that is the whole requirement rather than the shortfall; "
                             "0.50 ns of it is already being delivered.",
                    "why": "The data path delivers $0.32 + 0.18 = 0.50$ ns. The requirement, once the skew "
                           "is folded in, is $0.75 + 0.14 = 0.89$ ns. The shortfall is "
                           "$0.89 - 0.50 = 0.39$ ns, so 0.39 ns of buffering in the short route brings the "
                           "margin to zero and anything more gives some margin back. Two things are worth "
                           "carrying away. Deliberately inserting delay to make a circuit work feels "
                           "wrong, and it is nevertheless the standard fix — every synthesis tool does it "
                           "automatically and calls the result a hold-fix buffer. And of the 0.39 ns "
                           "missing, 0.14 ns was put there by the clock distribution rather than by the "
                           "logic: skew of 140 ps, which is a few centimetres of track, turned a path with "
                           "0.25 ns to make up into one with 0.39 ns. The same skew was making the setup "
                           "check *easier* by the same 0.14 ns, which is why clock trees are balanced "
                           "rather than merely connected.",
                },
                {
                    "title": "Three gate inputs hung on one node",
                    "minutes": 9,
                    "brief": r'''
A driving gate is a switch that connects the node to the rail through a small resistance;
everything it drives is capacitance. The node charges along
$v(t) = V\left(1 - e^{-t/RC}\right)$, and the gates downstream do not read a 1 until it
crosses half the supply, which happens at $t = RC \ln 2 \approx 0.693\,RC$.

Here the driver's output resistance has been drawn as a series resistor, and each of the
three loads it feeds has been drawn as its own capacitor to ground. Nothing is hidden:
work out what the node's total capacitance is before doing anything else.
''',
                    "prompt": "How long after the driver switches does the node cross the 2.5 V threshold?",
                    "note": "Give the answer in microseconds, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r0", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2200},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "c1", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1.5e-9},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "c2", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1.5e-9},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 9},
                            {"id": "c3", "kind": "C", "x": 17, "y": 6, "rot": 1, "value": 1.5e-9},
                            {"id": "g3", "kind": "GND", "x": 17, "y": 9},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [17, 3]},
                            {"a": [9, 3], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [13, 3], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 9]},
                            {"a": [17, 3], "b": [17, 5]},
                            {"a": [17, 7], "b": [17, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, switching on at t = 0", "value": "5.00 V"},
                        {"label": "Driver output resistance", "value": "2.2 kΩ"},
                        {"label": "Load capacitances", "value": "three of 1.5 nF, all on the probed node"},
                        {"label": "Threshold of the receiving gate", "value": "half the supply, 2.5 V"},
                    ],
                    "aside": "Capacitances that share a pair of nodes are in parallel, and capacitances in "
                             "parallel **add** — the opposite of what resistors in parallel do. Two plates "
                             "side by side are one bigger plate.",
                    "check": r'''
var th = c.values('V')[0] / 2;
var r = c.step(1e-5);
for (var i = 1; i < r.t.length; i++) {
  if (r.v[i] >= th) {
    return (r.t[i - 1] + (th - r.v[i - 1]) * (r.t[i] - r.t[i - 1]) /
            (r.v[i] - r.v[i - 1])) * 1e6;
  }
}
throw new Error('the node never reaches the threshold');
''',
                    "answer": 6.86,
                    "tol": 0.05,
                    "unit": "µs",
                    "hint": "Total the capacitance first, then $\\tau = RC$, then $0.693\\,\\tau$.",
                    "wrong": "If you got 2.29 µs, only one of the three capacitors was counted. If you got "
                             "0.76 µs, the three were combined the way three *resistors* in parallel "
                             "combine — but capacitances in parallel add, so the node is heavier than any "
                             "one load, not lighter. If you got 9.90 µs, that is the time constant itself; "
                             "the node is only at 63 % of the rail then, well past the threshold but not "
                             "the answer to what was asked.",
                    "why": "The three capacitors all sit between the probed node and ground, so they are "
                           "in parallel and their values add: "
                           "$C = 3 \\times 1.5\\,\\text{nF} = 4.5\\,\\text{nF}$. The time constant is "
                           "$\\tau = 2.2\\,\\text{k}\\Omega \\times 4.5\\,\\text{nF} = 9.9\\,\\mu\\text{s}$, "
                           "and the threshold at half the rail is crossed at "
                           "$\\tau \\ln 2 = 0.693 \\times 9.9 = 6.86\\,\\mu\\text{s}$. That is the whole of "
                           "fanout, in one calculation: every extra input hung on this node adds 1.5 nF, "
                           "which adds $2.2\\,\\text{k}\\Omega \\times 1.5\\,\\text{nF} = 3.3\\,\\mu\\text{s}$ "
                           "to the time constant and $0.693 \\times 3.3 = 2.29\\,\\mu\\text{s}$ to the "
                           "delay. The delay is linear in the number of loads, and the two ways out are "
                           "fewer loads per node or a smaller driving resistance. Note also what did not "
                           "matter: the supply voltage cancelled out of $\\tau \\ln 2$ entirely, so raising "
                           "the rail to 10 V would not speed this up by one nanosecond — the node charges "
                           "faster but the threshold it has to reach is higher by exactly the same factor.",
                },
                {
                    "title": "A node that never reaches the rail, and the clock it allows",
                    "minutes": 14,
                    "brief": r'''
The same driver, but this time something else is pulling on the node: a **keeper**, a
weak resistor to ground that holds the line at a definite level when nothing is driving
it. It is a common and sensible thing to add, and it changes the delay calculation in two
ways at once.

The node now settles at a divided-down voltage rather than at the rail, so use the general
form:

$$v(t) = V_f\left(1 - e^{-t/\tau}\right) \quad \Longrightarrow \quad
t = \tau \ln\!\left(\frac{V_f}{V_f - V_{th}}\right)$$

where $V_f$ is what the node settles at and $\tau$ is the total capacitance times the
resistance seen **looking out of the node**, which is everything attached to it in
parallel. The threshold is unchanged at half the supply, because it belongs to the
receiving gate and the receiving gate is still powered from 5 V.

This RC is the combinational path between two flip-flops. The 4000-series parts on the
board are quoted at up to 0.40 µs from clock edge to settled output and want 0.10 µs of
setup, worst case at 5 V over temperature. Find what that whole loop can be clocked at.
''',
                    "prompt": "What is the highest clock frequency this stage can be run at?",
                    "note": "Give the answer in kilohertz, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rd", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "rk", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 40000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "cl", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-9},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 9},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [9, 3], "b": [13, 3]},
                            {"a": [13, 3], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Supply, switching on at t = 0", "value": "5.00 V"},
                        {"label": "Driver output resistance", "value": "10 kΩ"},
                        {"label": "Keeper to ground", "value": "40 kΩ"},
                        {"label": "Load capacitance", "value": "1 nF"},
                        {"label": "Threshold of the receiving gate", "value": "2.5 V"},
                        {"label": "Flip-flop clock-to-output, worst case", "value": "0.40 µs"},
                        {"label": "Flip-flop setup time", "value": "0.10 µs"},
                    ],
                    "aside": "Three separate things to find before the frequency: what the node settles "
                             "at, what the time constant is, and when the threshold is crossed. Only the "
                             "last of those goes into the timing budget.",
                    "check": r'''
var th = c.values('V')[0] / 2;
var r = c.step(1.2e-5);
var t = null;
for (var i = 1; i < r.t.length; i++) {
  if (r.v[i] >= th) {
    t = r.t[i - 1] + (th - r.v[i - 1]) * (r.t[i] - r.t[i - 1]) / (r.v[i] - r.v[i - 1]);
    break;
  }
}
if (t === null) throw new Error('the node never reaches the threshold');
return 1 / (t + 0.40e-6 + 0.10e-6) / 1e3;
''',
                    "answer": 119.8,
                    "tol": 0.5,
                    "unit": "kHz",
                    "hint": "The final value is a plain two-resistor divider. For the time constant, turn "
                            "the supply off in your head: from the node, the 10 kΩ now goes to ground too, "
                            "so it is 10 kΩ in parallel with 40 kΩ.",
                    "wrong": "If you got 134.6 kHz, the delay was taken as $0.693 \\times 10\\,\\text{k}\\Omega "
                             "\\times 1\\,\\text{nF}$ — the right formula for a node that charges to the "
                             "rail, and this one does not. If you got 165.4 kHz, the time constant was "
                             "worked out correctly as 8 µs but $0.693\\,\\tau$ was used anyway, which "
                             "assumes the node stops at 5 V. If you got 127.4 kHz, the delay is right and "
                             "the flip-flops' own 0.50 µs was left out of the period.",
                    "why": "Three steps and then a fourth.\n\n"
                           "**Where it settles.** At DC the capacitor is an open circuit, so the node is a "
                           "plain divider: "
                           "$V_f = 5\\,\\text{V} \\times 40/(10 + 40) = 4.00\\,\\text{V}$.\n\n"
                           "**The time constant.** The capacitor sees the two resistors in parallel — the "
                           "supply is a fixed voltage, so as far as a change on the node is concerned the "
                           "10 kΩ leads to ground just as the 40 kΩ does. "
                           "$R = 10 \\times 40 / 50 = 8\\,\\text{k}\\Omega$, so "
                           "$\\tau = 8\\,\\text{k}\\Omega \\times 1\\,\\text{nF} = 8\\,\\mu\\text{s}$.\n\n"
                           "**When it crosses 2.5 V.** "
                           "$t = 8\\,\\mu\\text{s} \\times \\ln\\!\\left(\\frac{4.00}{4.00 - 2.50}\\right) "
                           "= 8 \\times \\ln 2.667 = 8 \\times 0.9808 = 7.85\\,\\mu\\text{s}$.\n\n"
                           "**The period.** $0.40 + 7.85 + 0.10 = 8.35\\,\\mu\\text{s}$, so "
                           "$f = 1/8.35\\,\\mu\\text{s} = 119.8\\,\\text{kHz}$.\n\n"
                           "The keeper pulled this stage two ways at once. It cut the time constant from "
                           "10 µs to 8 µs, which on its own would have made the node faster; but it also "
                           "pulled the destination down from 5.00 V to 4.00 V, so the threshold now sits at "
                           "62.5 % of the final value instead of 50 %, and the crossing happens at "
                           "$0.98\\,\\tau$ rather than $0.69\\,\\tau$. The second effect wins: 7.85 µs "
                           "against the 6.93 µs the same driver and load would have given with no keeper "
                           "at all. And the effect has a cliff in it. Change the keeper to 10 kΩ and "
                           "$V_f = 2.50$ V exactly, which is the threshold: the logarithm's argument goes "
                           "to infinity and the node never crosses, however long you wait. Make the keeper "
                           "smaller still and the gate downstream reads a permanent 0 no matter what the "
                           "driver does. That is the same failure the build in this module warns about, "
                           "with a number attached to how close it is.",
                },
            ],
            "derive": {
                "title": "How deep to pipeline, and what the flip-flops charge for",
                "minutes": 15,
                "vars": ["D", "k", "h", "T", "S"],
                "brief": r'''
The budget from the reading, $T \ge t_{cq} + t_{pd} + t_{su}$, has an obvious consequence
that is worth pushing until it stops being obvious. If the period is set by the longest
run of logic between two flip-flops, then cutting that run in half by dropping a rank of
flip-flops into the middle of it should nearly halve the period. The pipeline sandbox in
this module is a picture of exactly that.

*Nearly*, because the new flip-flops charge for themselves. Write

* $D$ for the total combinational delay of the block, before anything is cut;
* $k$ for the number of stages it is cut into, assumed equal;
* $h$ for the per-stage flip-flop overhead, $t_{cq} + t_{su}$, which is paid once per
  stage however small the stage is.

Throughput here means results per second, which is one result per clock period once the
pipeline is full.
''',
                "steps": [
                    {
                        "prompt": "One stage holds $D/k$ of logic, with a rank of flip-flops on each side of it charging $h$ between them. Write the clock period $T$ in terms of $D$, $k$ and $h$.",
                        "answer": "\\frac{D}{k} + h",
                        "hint": "The logic in one stage, plus the overhead that stage is charged. Nothing else appears.",
                        "deconstruct": [
                            "Cutting $D$ into $k$ equal pieces leaves $D/k$ of logic between one rank of flip-flops and the next.",
                            "The launching flip-flop's clock-to-output and the capturing flip-flop's setup time are both charged once per stage, and $h$ was defined as their sum: $T = D/k + h$.",
                        ],
                    },
                    {
                        "prompt": "The unpipelined block is the case $k = 1$. Throughput is one result per period, so the speedup $S$ is the ratio of the two periods. Write $S$ in terms of $D$, $k$ and $h$.",
                        "answer": "\\frac{k D + k h}{D + k h}",
                        "placeholder": "\\frac{\\ldots}{\\ldots}",
                        "hint": "Put the $k = 1$ period over the $k$-stage period, then clear the fraction inside the fraction by multiplying top and bottom by $k$.",
                        "deconstruct": [
                            "At $k = 1$ the period is $D + h$; at $k$ stages it is $D/k + h$.",
                            "So $S = (D + h)/(D/k + h)$. Multiplying numerator and denominator by $k$ clears the inner fraction and gives $k(D + h)/(D + kh)$.",
                        ],
                    },
                    {
                        "prompt": "Let $k$ grow without limit, so that $D/k$ goes to zero. Write the ceiling on $S$ in terms of $D$ and $h$.",
                        "answer": "\\frac{D + h}{h}",
                        "hint": "In the unmultiplied form $S = (D + h)/(D/k + h)$, only the denominator depends on $k$.",
                        "deconstruct": [
                            "As $D/k \\to 0$ the denominator tends to $h$ alone: the period is all overhead and no logic.",
                            "So $S \\to (D + h)/h$, a fixed number set entirely by how the logic compares with the flip-flop overhead. No amount of further cutting gets past it.",
                        ],
                    },
                    {
                        "prompt": "Now numbers. The block holds $D = 12.00$ ns of logic; the flip-flops take 0.70 ns from clock to output and need 0.30 ns of setup, so $h = 1.00$ ns. Cut it into $k = 4$ stages and give the clock period in nanoseconds.",
                        "answer": "4",
                        "hint": "$12/4$, plus the overhead.",
                        "deconstruct": [
                            "$D/k = 12.00/4 = 3.00$ ns of logic per stage.",
                            "Plus $h = 1.00$ ns: $T = 4.00$ ns, which is a 250 MHz clock.",
                        ],
                    },
                    {
                        "prompt": "Same numbers. What is the speedup $S$ over the unpipelined block?",
                        "given": "$D = 12.00$ ns, $h = 1.00$ ns, $k = 4$",
                        "answer": "3.25",
                        "hint": "The unpipelined period is $12.00 + 1.00 = 13.00$ ns.",
                        "deconstruct": [
                            "Unpipelined, $T = D + h = 13.00$ ns, so 76.9 million results per second.",
                            "At four stages, $T = 4.00$ ns. The ratio is $13.00/4.00 = 3.25$ — not 4, because the overhead was paid once before and four times now.",
                        ],
                    },
                    {
                        "prompt": "With the same $D$ and $h$, what is the ceiling on the speedup — the value no depth of pipelining can beat?",
                        "answer": "13",
                        "hint": "Use the ceiling expression from the third step with $D = 12.00$ and $h = 1.00$.",
                        "deconstruct": [
                            "$(D + h)/h = 13.00/1.00 = 13$.",
                            "And it is approached slowly: at $k = 12$ the period is $1.00 + 1.00 = 2.00$ ns and $S = 6.5$, only half the ceiling, with twelve ranks of flip-flops already paid for.",
                        ],
                    },
                ],
                "closing": r'''
Read the shape rather than the numbers. $S = k(D+h)/(D+kh)$ rises steeply at first, bends
over, and flattens against $(D+h)/h$ — a ceiling fixed entirely by how the logic compares
with the flip-flop overhead. Cutting a block into four stages bought 3.25 times the
throughput; cutting the same block into twelve bought 6.5, which is 2 times more for 3
times the flip-flops. Everything after that is worse value again.

Three things the model leaves out, all of which make real pipelining worse than this.

**The split is never equal.** $D/k$ assumed the logic cuts into equal pieces, and it never
does — the period is set by the *largest* piece, so a four-way split that comes out as
4.0, 3.0, 3.0 and 2.0 ns runs at $4.0 + 1.0 = 5.0$ ns, not 4.0. Balancing the stages is
most of the work of pipelining something, and it is why the depth is usually chosen by
where the natural cut points are rather than by a formula.

**Latency gets worse, not better.** One result takes $k$ periods to come out the far end.
Unpipelined that is 13.00 ns; at four stages it is $4 \times 4.00 = 16.00$ ns; at twelve
it is $12 \times 2.00 = 24.00$ ns. Throughput went up by 6.5 and the time to get any single
answer nearly doubled. If what you need is one answer quickly — a control loop closing
round a sensor, say — pipelining is the wrong tool and you have made the problem worse.

**The stages do not stay full.** The model assumes a result comes out every cycle, which
holds only while nothing has to wait for anything. The sandbox in this module is the
counter-example: an instruction that needs a number the one above it has not finished
computing stalls, and a mispredicted branch throws away work already started. Both convert
cycles into nothing, so the real figure is not one result per cycle but rather less, and
the deeper the pipeline the more each mispredict costs, because there is more work in
flight to discard.

There is a fourth cost that does not appear in any of the timing arithmetic. Every rank of
flip-flops is clocked every cycle whether or not it is doing anything useful, and module 5
shows that a CMOS gate's power is paid per transition. Twelve ranks at 500 MHz burn twelve
ranks' worth of clock power, which is why the industry's answer to this question moved
during the 2000s from *deeper* to *wider*: more units side by side rather than more stages
in a line.
''',
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

        # ---- M5 -----------------------------------------------------------
        {
            "title": "What a gate is made of: switches, levels and margins",
            "summary": "Open a gate up and there are no ones and zeros in it — only switches, two supply rails and a voltage that has to be unambiguous by the time it arrives.",
            "concepts": [
                "A transistor used in logic is a **voltage-controlled switch**. An n-channel MOSFET conducts between its two terminals when its gate is held high and blocks when the gate is low; a p-channel one does the opposite. A CMOS gate is two networks of these — p-channel devices from the supply down to the output, n-channel devices from the output down to ground — wired so that exactly one network conducts for any input.",
                "That arrangement is why the output is never left floating, and why a settled gate draws almost no current: one path is always open and the other is always shut, so there is no route from supply to ground.",
                "The pull-down network conducts when its inputs are **high**, which pulls the output **low**, so the natural CMOS gate inverts. NAND and NOR cost four transistors each; AND and OR are those gates with an inverter bolted on the end, so they cost six and are one gate delay slower. That is the electrical half of the NAND-universality argument from module 3.",
                "Four voltages, not two. An output promises to drive at least $V_{OH}$ for a 1 and at most $V_{OL}$ for a 0; an input promises to read anything above $V_{IH}$ as a 1 and anything below $V_{IL}$ as a 0. The gaps between the promises are the **noise margins**, $NM_H = V_{OH} - V_{IH}$ and $NM_L = V_{IL} - V_{OL}$, and noise smaller than the margin cannot change what is read.",
                "**Diode logic** — two diodes and a resistor make an AND gate — works, and does not scale: every stage loses a diode drop and nothing puts it back, so after a few stages the level is sitting in the forbidden band. A transistor gate has **gain**: it produces a full 0 or a full 1 whatever arrived, which is the property that lets you cascade a million of them.",
                "Almost all the power in a digital chip goes into charging and discharging capacitance — the wires, and the gate terminals being driven — so it scales as $CV^2f$. Every extra input a gate drives (its **fan-out**) adds capacitance, and therefore adds delay and power together.",
            ],
            "read": [
                {
                    "title": "Underneath the symbol: two networks of switches",
                    "minutes": 13,
                    "body": r'''
Take the lid off a 74HC00 and put the die under a microscope. There are no ones and
zeros in there. There are four transistors, three wires that leave the package as A, B
and Y, and two more that go to the supply and to ground. Not one of those transistors
knows what a NAND is. Each of them does exactly one thing: it either lets current pass
between two of its terminals or it does not, according to the voltage on a third.

Everything in the modules before this one was about what a gate *means* — the table it
obeys, the algebra that rearranges it, the map that shrinks it. This module is about
what a gate *is*, and the two halves are joined by one translation:

> a switch that is closed is a 1.

Get that translation the right way round and the rest of this reading is Ohm's law
applied to resistors in series and in parallel.

## The switch

The device is a MOSFET, and the only part of its physics you need is the shape of it.
Two terminals, **source** and **drain**, sit at either end of a strip of silicon. Over
that strip, separated from it by an insulating layer of oxide a few atoms thick, lies a
third terminal: the **gate**. The gate touches nothing. It is one plate of a capacitor
whose other plate is the silicon channel underneath.

Put a voltage on the gate and its electric field drags charge carriers into the channel,
and the channel conducts between source and drain. Take the voltage away and the
carriers disperse, and the path between source and drain is as good as open.

Two consequences fall straight out of that arrangement, and both matter more than the
physics does.

**No steady current flows into a gate terminal.** It is a capacitor plate with an
insulator behind it, not a resistor to anywhere. A settled MOSFET input draws leakage —
nanoamps — and nothing else. That is why one CMOS output can feed fifty CMOS inputs
without its voltage sagging, and it is why fan-out will turn out to be a question about
speed rather than about levels.

**Changing a gate voltage costs charge**, because charging a capacitor always does. That
is where the power in a digital chip goes, and the derivation unit in this module takes
it as far as $P = CV^2f$. Notice that both facts come from the same piece of geometry:
the thing that makes the input free in steady state is the thing that makes it expensive
to change.

There are two flavours. An **n-channel** device conducts when its gate is held HIGH. A
**p-channel** device is built the opposite way round and conducts when its gate is held
**LOW**. That asymmetry is the single most consequential fact in this module, and the
place where nearly every beginner's circuit goes wrong.

For everything that follows, model a conducting device as a resistance of a few hundred
ohms and a non-conducting one as a very large resistance. That model is a linearisation,
and the last section says where it fails — but it gets the settled voltages right, which
is what a logic level is.

## First attempt: one switch and one resistor

Here is the cheapest thing that behaves like an inverter. A resistor from the supply
rail down to the output node, and an n-channel switch from the output node down to
ground, with the input on its gate.

Input HIGH, switch closed: the output is dragged down towards ground. Input LOW, switch
open: nothing else is connected, so the resistor pulls the output up to the rail. Input
inverted, output driven, job done — and this is genuinely how early integrated logic was
built.

The question that decides whether it is any good is: *how low is low?* Not zero. A closed
switch is a resistance, and a resistance in series with the pull-up resistor is a
voltage divider.

### Worked: what the LOW actually comes out at

A 5.00 V rail, a 10 kΩ pull-up, and a switch whose on-resistance is 470 Ω.

```
total resistance   10 000 + 470              = 10 470 ohm
current            5.00 / 10 470             = 477.6 uA
V_OL               477.6 uA x 470 ohm        = 0.2245 V

as a ratio         5.00 x 470 / 10 470       = 0.2245 V   (same thing)
```

0.2245 V. A 5 V CMOS input reads anything below $0.3 \times 5 = 1.5$ V as a LOW, so this
arrives with 1.28 V to spare. The level is fine. The bill is not.

```
supply current while the output is LOW       477.6 uA
power from the rail   5.00 V x 477.6 uA    =   2.39 mW   per gate, continuously
100 000 gates, half of them LOW at any time
                      50 000 x 2.39 mW     =    119 W
```

That current flows the entire time the output is LOW. Not on the edges — always. And the
obvious repair makes something else worse: to get $V_{OL}$ ten times smaller you make the
pull-up ten times bigger, which does cut the current by ten, but the same pull-up
resistor is the only thing charging the next stage's input capacitance when the output
goes HIGH, so the gate becomes ten times slower. Level quality, static power and speed
are one knob with three labels on it. The trade has a name — **ratioed logic** — and the
tuning unit in this module is that knob, with all three constraints switched on at once.

## The move that fixes all three

Replace the resistor with a *second switch*, chosen so that it is closed exactly when the
first one is open. A p-channel device above the output, an n-channel device below it,
and both gates tied to the same input. That is a CMOS inverter, and the word
**complementary** in CMOS is this arrangement and nothing else.

Input HIGH: the n-channel device conducts (high gate) and the p-channel one does not
(its gate is not low). The output is tied to ground through a few hundred ohms.

Input LOW: the p-channel device conducts and the n-channel one does not. The output is
tied to the rail through a few hundred ohms.

In each state, one path is a short and the other is an open circuit. So the output is
always driven and never floating; there is never a route from rail to ground, so the
settled current is leakage only; and both levels reach a rail rather than a fraction of
one.

### Worked: the same rail, the complementary way

Same 5.00 V. Take the n-channel on-resistance as 350 Ω and the p-channel one as 1.2 kΩ —
the p device is genuinely the weaker of the two for the same silicon area, because holes
move more slowly than electrons, and a library evens them up by drawing the p device two
or three times wider. Draw an off device as 4 MΩ.

```
input HIGH   n closed 350 ohm, p open 4 M
  V_OL = 5.00 x 350 / (4 000 000 + 350)      = 0.437 mV
input LOW    p closed 1.2 k, n open 4 M
  V_OH = 5.00 x 4 000 000 / (4 000 000 + 1200)
       = 4.99850 V,  which is 1.50 mV below the rail
static current, input HIGH   5.00 / (4 000 000 + 350)   = 1.25 uA
static current, input LOW    5.00 / (4 000 000 + 1200)  = 1.25 uA
```

Set that beside the ratioed inverter on the same rail: a LOW of 0.437 mV instead of
0.2245 V, about five hundred times better, and a static current of 1.25 µA instead of
477.6 µA, about four hundred times better. Nothing was tuned. One resistor was replaced
by a switch.

One honesty note about that 4 MΩ. A real MOSFET that is off is nothing like as
conductive as that — gigaohms is closer, and older parts are far beyond even that. It is
drawn small here so the deficit from the rail is a number you can actually see on the
page. With a realistic off device the deficit shrinks by another factor of a thousand,
so the conclusion only gets stronger.

## Series is AND, parallel is OR — of conduction

Now give the gate two inputs. Put two n-channel devices **in series** between the output
and ground: that path conducts only if A *and* B are both HIGH. Put them **in parallel**:
it conducts if A *or* B is HIGH.

The pull-down network is what drags the output LOW. So:

* series pull-down → output LOW when $A \cdot B$ → $Y = \overline{A \cdot B}$ → **NAND**
* parallel pull-down → output LOW when $A + B$ → $Y = \overline{A + B}$ → **NOR**

The pull-up network has to be the exact complement — conducting precisely when the
pull-down is not — and De Morgan hands you the construction for nothing. The series chain
conducts on $A \cdot B$; its complement is $\overline{A} + \overline{B}$; a p device
conducts on a LOW gate, which is what $\overline{A}$ means here; and an OR of two
conditions is two devices in parallel. So: **series below, parallel above**. Swap series
for parallel, swap n for p, and you have the pull-up. It is a mechanical construction —
the pull-up graph is the dual of the pull-down graph — not something to re-derive each
time.

Count the transistors:

```
inverter   1 n            + 1 p              = 2
NAND2      2 n in series  + 2 p in parallel  = 4
NOR2       2 n in parallel+ 2 p in series    = 4
AND2       NAND2 + an inverter               = 6   and one gate delay slower
OR2        NOR2  + an inverter               = 6   and one gate delay slower
```

The inverting gates are the cheap ones *and* the fast ones. Module 3 proved from the
algebra that NAND alone is enough to build anything; this table is the reason anyone
would want that to be true. The AND symbol you draw on a schematic is, in the silicon, a
NAND with an inverter bolted on the end.

Here is a 2-input NAND traced switch by switch, which is worth working through once by
hand:

```
 A  B | P_A  P_B  pull-up      | N_A  N_B  pull-down    | Y
 -----+-----------------------+------------------------+------
 0  0 | on   on   conducting   | off  off  open         | HIGH
 0  1 | on   off  conducting   | off  on   open         | HIGH
 1  0 | off  on   conducting   | on   off  open         | HIGH
 1  1 | off  off  open         | on   on   conducting   | LOW
```

Exactly one of the two networks conducts on every row. That is not a coincidence; it is
the property the dual construction guarantees, and it is what stops the output ever
floating or ever shorting the rail to ground.

## The mistake, twice

**"The p-channel device is the one that produces a 1, so it must turn on when the input
is 1."** This is tempting for a good reason: output-HIGH-when-input-HIGH is the pairing
that feels natural, and "pull-up" really does mean the device that reaches the high rail.
But the *gate* of a p-channel device must be **low** for it to conduct. Everything
downstream of that fact follows: the natural CMOS gate inverts, NAND and NOR are the
four-transistor cells, AND and OR are the expensive ones, and a standard-cell library is
built out of inverting logic.

**"If an n-channel switch works below the output, why not use one above it too and save a
process step?"** People built precisely this, and it half works. An n-channel device
needs its gate at least a threshold voltage above its *source* to keep conducting. Put
one above the output and the output is the source, so as the output rises the device
shuts itself off — and it stops at about $V_{DD} - V_{th}$. On a 3.3 V rail with a 0.7 V
threshold that is 2.6 V, and nothing recovers it: a second such stage arrives at 1.9 V.
Hence the rule worth memorising: an n device passes a strong 0 and a weak 1, a p device
passes a strong 1 and a weak 0. When you need a switch that passes both — inside a
multiplexer, say — you use one of each, wired in parallel, and the pair is called a
**transmission gate**.

## Where the switch model stops

**A conducting MOSFET is not really a resistor.** Over most of an output swing it behaves
much more like a current source whose value is set by the gate voltage, and only near the
ends of the swing does it look like a resistance at all. The resistance model is a
linearisation. It gets the settled levels right, which is why the $V_{OL}$ and $V_{OH}$
figures above can be trusted; it gets transition times right to within roughly a factor
of one and a half, which is why an RC estimate of a gate delay is an estimate and not a
number to design a clock around.

**This is also why the circuit questions in this module draw no transistors.** They draw
the on and off devices as the resistors they approximate, and that is a choice about the
model rather than a limit of the tool: the schematic editor does carry MOSFETs, and
solves them with the same Newton-Raphson iteration it uses on a diode. But a logic gate's
levels and its RC delay are exactly what the resistance model gives you, and asking a
square law for a number you are going to quote to one significant figure buys nothing.
EE202 uses the device itself, because there the shape of the curve is the subject.

**Stacking has a limit.** Every extra device in series with a pull-down adds its
on-resistance, so $V_{OL}$ climbs and the falling edge slows down. An 8-input NAND would
put eight devices in a chain. Real libraries stop at three or four inputs and build wide
gates as trees of narrow ones, which is why a synthesised design is full of NAND3 and
NOR2 cells and contains nothing eight inputs wide.

**Off is not open.** At the geometries used now, leakage through devices that are
supposed to be off is a large fraction of a chip's total power rather than a rounding
error, and a great deal of design effort goes into switching the supply away from blocks
that are idle. The 4 MΩ above was a fiction chosen to be visible on the page — but the
gap between that fiction and reality has been closing for twenty years.

**And none of this involves time.** Every voltage here is a settled DC state. What
happens *during* a transition, while both devices are partly on and a current flows
straight from rail to ground, is the subject of the next reading and of this module's
power derivation.
''',
                },
                {
                    "title": "The level has to survive the wire",
                    "minutes": 14,
                    "body": r'''
A signal leaves one chip at some voltage and arrives at another chip at a different one.
The track had resistance, the ground plane underneath was not at zero volts everywhere at
once, a switching regulator six centimetres away coupled a little of itself in, and the
receiving chip's own supply moved while its neighbours switched. None of that is a fault.
It is what a board does.

Module 1 stated the agreement that survives all of it: four voltages, two of them
promised by the driver and two demanded by the receiver, with the gaps between them
called noise margins. That reading announced those four numbers. This one shows where
they come from, which turns out to be a single curve, and then shows the two ways the
margins get eaten in practice — by the current the output is asked to deliver, and by the
number of inputs it is asked to feed.

## One curve, measured

Take an inverter and do something a logic textbook rarely does: sweep the input slowly
across the whole rail, and write down the output at each point. Not 0 and 1 — volts. This
is the **voltage transfer characteristic**, and here is one, from a 5 V part.

```
  Vin (V)   Vout (V)     slope of the segment ending here
   0.00      5.000
   2.00      4.980        (4.980-5.000)/2.00   =  -0.010
   2.30      4.920        (4.920-4.980)/0.30   =  -0.200
   2.40      4.820        (4.820-4.920)/0.10   =  -1.000
   2.45      4.400        (4.400-4.820)/0.05   =  -8.400
   2.50      2.500        (2.500-4.400)/0.05   = -38.000
   2.55      0.600        (0.600-2.500)/0.05   = -38.000
   2.60      0.180        (0.180-0.600)/0.05   =  -8.400
   2.70      0.080        (0.080-0.180)/0.10   =  -1.000
   3.00      0.020        (0.020-0.080)/0.30   =  -0.200
   5.00      0.000        (0.000-0.020)/2.00   =  -0.010
```

Flat, then very steep, then flat again. Read it against the two switches from the
previous reading and each region has an owner. On the left the p device is fully on and
the n device is off, so the output is pinned near the rail and barely notices the input
moving. On the right the roles have swapped. In the narrow middle both devices are partly
conducting at once, the node is being fought over, and a small movement at the input
throws the output across the rail.

That middle slope is a **voltage gain**, and it is large: 38, here. The gate is an
amplifier that happens to be operated at its ends.

## Where the four thresholds come from

Now the useful question. A signal arrives with some noise on it. Does the gate make the
noise bigger or smaller?

That is exactly what the slope says. A wobble of $\delta$ volts at the input comes out as
$|\text{slope}| \times \delta$ volts at the output. Where the magnitude of the slope is
below 1, the disturbance shrinks. Where it is above 1, it grows. So the boundary between
"safe" and "not safe" is not a matter of taste — it is the point where the slope is
exactly $-1$:

$$\left|\frac{dV_{out}}{dV_{in}}\right| = 1$$

There are two such points, one on each flat, and the table above was chosen so they land
on the sample points. Reading them off:

```
lower unity-gain point   Vin = 2.40 V  -> this is V_IL,  and the output there is V_OH
upper unity-gain point   Vin = 2.70 V  -> this is V_IH,  and the output there is V_OL

V_IL = 2.40 V     V_OH = 4.82 V
V_IH = 2.70 V     V_OL = 0.08 V

NM_H = V_OH - V_IH = 4.82 - 2.70 = 2.12 V
NM_L = V_IL - V_OL = 2.40 - 0.08 = 2.32 V
```

$V_{IL}$ and $V_{IH}$ are not conventions someone chose. They are the two places where
this gate stops attenuating noise and starts amplifying it. And $V_{OH}$ and $V_{OL}$ are
not separate promises either: they are what this gate puts out when it is fed the worst
input it is still required to accept.

Compare those with the datasheet figures for a real 5 V CMOS family — $V_{IH} = 3.5$ V,
$V_{IL} = 1.5$ V, quoted as $0.7V_{DD}$ and $0.3V_{DD}$. The datasheet is far more
pessimistic than the curve of any one part, and it has to be: those numbers must hold for
every part that leaves the factory, at every temperature between $-40$ and $+85$ °C, and
across the whole supply tolerance. A guarantee is a statement about the worst part on the
worst day, and the curve above is one part on a bench.

## Gain is what makes a chain possible

Because the gate has gain, a level that arrives degraded leaves clean. Feed 3.8 V into a
5 V part: the input is above $V_{IH}$, so the output is driven to within a few
millivolts of the rail. The 3.8 V is not passed along. It is discarded, and a fresh HIGH
is generated in its place. Do that a million times and nothing accumulates.

The counter-example is worth doing with numbers, because it is the reason transistors
displaced the thing that came before them. Two diodes and a resistor make a perfectly
serviceable OR gate: anodes to the two inputs, cathodes tied together, resistor to
ground. It works, and it has no gain at all — the output is one diode drop, about 0.7 V,
below whichever input is highest.

```
diode OR gates in a chain, starting from a clean 5.00 V HIGH

  stage 1 out   5.00 - 0.70  =  4.30 V     still a HIGH  (V_IH = 3.50)
  stage 2 out   4.30 - 0.70  =  3.60 V     still a HIGH, 0.10 V of margin left
  stage 3 out   3.60 - 0.70  =  2.90 V     inside the forbidden band
```

And the AND gate built the same way, with the diodes the other way round and the resistor
to the rail, does the mirror image to a LOW — it lifts it by a diode drop each time:

```
diode AND gates in a chain, starting from a clean 0.00 V LOW

  stage 1 out   0.00 + 0.70  =  0.70 V     still a LOW  (V_IL = 1.50)
  stage 2 out   0.70 + 0.70  =  1.40 V     still a LOW, 0.10 V of margin left
  stage 3 out   1.40 + 0.70  =  2.10 V     no longer a LOW
```

Three levels of logic and the signal means nothing. Note what is *not* wrong here: every
individual gate did its job correctly, every drop is within spec, nothing failed. The
circuit is simply accumulating, and no diode network anywhere downstream can undo it,
because nothing in it can tell the accumulated error from the signal. Gain is not a
refinement on diode logic. It is the property that makes logic of arbitrary depth exist.

## The first way the margin gets eaten: current

$V_{OH}$ is not a constant. Go back to the previous reading's model: an output driving
HIGH is the rail connected to the pin through the p device's on-resistance. Draw current
out of that pin and the on-resistance drops voltage, exactly as any resistance would.

A datasheet says this out loud, and it is worth learning to read. A 5 V CMOS family at
$V_{CC} = 4.5$ V quotes two figures for $V_{OH}$: at least 4.4 V when sourcing 20 µA, and
at least 3.98 V when sourcing 4 mA. One line of arithmetic extracts the resistance:

```
R_on(p)  =  (4.50 - 3.98) V / 4 mA  =  0.52 / 0.004  =  130 ohm
```

Now the margin becomes a question about the load rather than about the part. Suppose the
same output also drives an indicator LED needing 8 mA:

```
V_OH  =  4.50 - 0.008 x 130  =  4.50 - 1.04  =  3.46 V
NM_H  =  3.46 - 3.15         =  0.31 V        (V_IH is 3.15 V at a 4.5 V supply)
```

The margin went from 1.25 V to 0.31 V, and not one datasheet number changed. This is the
single most common way a design that "meets spec" fails on a bench: a margin was quoted
from the light-load column while the pin was doing real work.

## The second way: fan-out

Fan-out is the number of inputs one output drives, and CMOS splits the question in two.

**In DC terms it is almost free.** A CMOS input is an insulated gate, so it draws about
1 µA of leakage and no more. Fifty of them is 50 µA, which across the 130 Ω above costs
6.5 mV. You will run out of patience before you run out of DC drive.

**In AC terms it is the whole story.** Each of those inputs is a capacitor of a few
picofarads, and so is the track that reaches it. The driver has to charge the lot through
its on-resistance.

```
fan-out 2    C = 2 x 5 pF + 8 pF of track   =  18 pF
             tau = 130 ohm x 18 pF          =  2.34 ns
             10-90% rise = 2.2 tau          =  5.1 ns

fan-out 10   C = 10 x 5 pF + 15 pF of track =  65 pF
             tau = 130 ohm x 65 pF          =  8.45 ns
             10-90% rise = 2.2 tau          =  18.6 ns
```

Three and a half times the load, three and a half times the delay. And the same
capacitance appears in the power expression this module derives, so the bill arrives
twice. At 50 MHz on a 4.5 V rail:

```
18 pF   P = C V^2 f = 18e-12 x 4.5^2 x 50e6  =  18.2 mW
65 pF   P = C V^2 f = 65e-12 x 4.5^2 x 50e6  =  65.8 mW
```

Delay and power are the same quantity seen from two sides, and the quantity is
capacitance. That is why a large fan-out is broken up with a buffer tree rather than
driven from one output, and it is why a clock — which by definition reaches everything —
is the most expensive net on any chip.

## The mistake worth naming

The margin is a subtraction across a boundary between two *different* datasheets, and
three things go wrong with it.

**Mixing the pairs.** $NM_H = V_{OH} - V_{IH}$, never $V_{OH} - V_{IL}$. The wrong one is
tempting because $V_{IL}$ is "the low threshold", a HIGH is a long way from it, and the
number comes out comfortingly large. But the receiver only guarantees to read HIGH above
$V_{IH}$. Between $V_{IL}$ and $V_{IH}$ it is entitled to decide either way, and quoting
a margin down to $V_{IL}$ is quoting the distance to a line the receiver never promised
anything about.

**Reading both numbers off one part.** If a 3.3 V part drives a 5 V part, the driver's
$V_{OH}$ comes from one datasheet and the receiver's $V_{IH}$ from another. Take a 3.3 V
output at 3.10 V into a 5 V CMOS input whose $V_{IH}$ is 3.50 V and the high-side margin
is $3.10 - 3.50 = -0.40$ V. Negative. The link is not marginal, it is not guaranteed to
work at all, and it will often *appear* to work on the bench because a typical part
switches nearer 2.5 V than 3.5 V. The fill-in drill called *Two datasheets, one wire*
walks that exact interface, and the fix — a receiver with TTL-style thresholds at 2.0 V
and 0.8 V — as well.

**Confusing tolerance with compatibility.** A "5 V tolerant" input means the pin will not
be damaged by 5 V on it. It says nothing whatever about where its thresholds are. The two
properties are unrelated and the phrase has probably cost more engineering hours than any
other four characters in a datasheet.

## Where this stops holding

**Worst-case margins are a board technique.** Inside a chip, where a million devices
differ slightly from one another and the supply moves locally, the question stops being
"does the margin hold" and becomes "what fraction of parts fail", answered by Monte Carlo
over the process corners. There is no single $V_{IH}$ in there to subtract.

**At low supplies there is not much left to divide up.** On a 0.9 V core, the margins are
tens of millivolts and are budgeted against named noise sources — this much for supply
droop, this much for coupling — rather than guaranteed with a comfortable gap.

**A margin says nothing about time.** Everything above concerns a settled level. A signal
with a very slow edge sits in the steep middle of that transfer curve for a long time,
where both devices conduct and a current flows straight from rail to ground; a receiver
without hysteresis can also produce several output transitions from one such crossing.
The fix is a Schmitt trigger input, which deliberately pushes $V_{IH}$ and $V_{IL}$ apart
and makes each of them depend on which direction the input is coming from.

**And a fast edge on a long track is not a DC problem at all.** Reflections can drive a
receiver's input hundreds of millivolts past either rail for a few nanoseconds, whatever
the DC margin says. That is fixed with termination and controlled impedance, and it is a
different subject from this one.
''',
                },
            ],
            "quiz": {
                "title": "Transistors, levels and the cost of switching",
                "minutes": 8,
                "questions": [
                    {
                        "q": "In a CMOS gate, what is the pull-up network made of, and when does it conduct?",
                        "opts": [
                            "Resistors, which conduct all the time",
                            "p-channel transistors, which conduct when their gates are held low",
                            "n-channel transistors, which conduct when their gates are held high",
                            "p-channel transistors, which conduct when their gates are held high",
                        ],
                        "a": 1,
                        "why": (
                            "A p-channel device turns on with a **low** gate, so the pull-up network conducts "
                            "exactly when the inputs are low — which is when the output should be high. The "
                            "n-channel devices are the pull-down half and do the mirror job. A resistor pull-up "
                            "is a real technique, but it conducts even while the output is being held low, and "
                            "burning current in the 0 state is precisely what CMOS was designed to avoid."
                        ),
                    },
                    {
                        "q": "An output guarantees it will drive at least 4.4 V for a 1, and the input it feeds accepts anything above 3.5 V as a 1. How much noise can appear on that wire before the 1 stops being read as a 1?",
                        "opts": ["0.9 V", "1.5 V", "3.5 V", "4.4 V"],
                        "a": 0,
                        "why": (
                            "$4.4 - 3.5 = 0.9$ V, the high-level noise margin. It is a subtraction between two "
                            "different promises: what the sender guarantees to produce, and what the receiver "
                            "guarantees to accept. 4.4 V is only the first of those, and quoting it as the "
                            "margin assumes the receiver's threshold is at ground. The low-level margin is the "
                            "other subtraction, $V_{IL} - V_{OL}$, and the smaller of the two is the one that "
                            "decides how much interference the wire can survive."
                        ),
                    },
                    {
                        "q": "Why do CMOS libraries build most combinational logic out of NAND and NOR rather than AND and OR?",
                        "opts": [
                            "AND and OR cannot be built in CMOS at all",
                            "A CMOS switch network naturally inverts, so an AND gate is a NAND with an inverter after it — more transistors and more delay, not fewer",
                            "NAND and NOR draw less current when they are idle",
                            "NAND and NOR can take more inputs",
                        ],
                        "a": 1,
                        "why": (
                            "The pull-down network conducts when the inputs are high and pulls the output "
                            "**low**, so the cheap gate is an inverting one. A two-input NAND is four "
                            "transistors; the AND is that same NAND plus a two-transistor inverter, which is "
                            "half as big again and one gate delay slower. Idle current is the same for both, "
                            "because a settled CMOS gate of any kind draws almost nothing. Module 3 reached the "
                            "same conclusion from the algebra; this is the reason the algebra happens to be useful."
                        ),
                    },
                    {
                        "q": "Two diodes and a resistor make an AND gate that genuinely works. Why is a chain of them still no substitute for transistor gates?",
                        "opts": [
                            "Diodes switch too slowly to be useful",
                            "A diode gate cannot represent a logic 0",
                            "Each stage loses a diode drop and nothing restores it, so after a few stages the level is neither a 0 nor a 1",
                            "The resistor makes the gate draw too much current",
                        ],
                        "a": 2,
                        "why": (
                            "Diode logic has no gain: the output is always a little worse than the input it was "
                            "given, and the degradation accumulates down the chain until the voltage sits in "
                            "the forbidden band and the next stage cannot say what it is. A transistor gate "
                            "restores full levels at every stage, which is the whole reason arbitrarily deep "
                            "logic is possible. Speed and current are real drawbacks too, but they only make it "
                            "expensive; the missing gain makes it impossible."
                        ),
                    },
                    {
                        "q": "Dynamic power is $P = CV^2f$. Dropping the supply from 5 V to 1 V and changing nothing else multiplies the dynamic power by what?",
                        "opts": ["1/5", "1/25", "1/125", "1/2"],
                        "a": 1,
                        "why": (
                            "The voltage is squared, so a fivefold reduction becomes a twenty-fivefold one: "
                            "$(1/5)^2 = 1/25$. That is the reason supply voltages fell from 5 V to around 1 V "
                            "over the years that clock rates were climbing — it is the only term in the "
                            "expression that can be attacked quadratically. The price is that transistors "
                            "switch more slowly at a lower supply, so the saving is never quite free."
                        ),
                    },
                ],
            },
            "blanks": [
                {
                    "title": "A NOR gate, traced switch by switch",
                    "minutes": 9,
                    "caption": "four transistors, and which of them are closed on each of the four rows",
                    "lang": "text",
                    "brief": r'''
The reading traced a NAND: two n devices in series below the output, two p devices in
parallel above it. A NOR is that construction turned inside out — parallel below, series
above — and the whole table follows from two rules and nothing else:

* a p-channel device conducts when its gate is **LOW**, an n-channel device when its gate
  is **HIGH**;
* a **series** path needs every device in it closed, a **parallel** path needs only one.

Fill in the state of each network, and then the output. Where a network conducts, say
what it conducts *through*, because the resistance is the difference between a strong
level and a weak one.
''',
                    "listing": """2-input CMOS NOR

  pull-up   network:  P_A then P_B in SERIES,   between the 5 V rail and Y
  pull-down network:  N_A and  N_B in PARALLEL, between Y and ground

  on-resistance of one p device 1.2 k, of one n device 350 ohm; an open device is a megohm and up

   A  B | P_A  P_B  pull-up        | N_A  N_B  pull-down      | Y
   -----+------------------------+--------------------------+-------
   0  0 | on   on   ___            | off  off  open           | ___
   0  1 | on   off  open           | off  on   ___            | LOW
   1  0 | off  on   ___            | on   off  conducting     | LOW
   1  1 | off  off  open           | on   on   ___            | ___
""",
                    "blanks": [
                        {
                            "prompt": "A is 0 and B is 0, so both p devices have a LOW on the gate. What is the pull-up network doing?",
                            "hole": "?",
                            "opts": [
                                "conducting, through 2.4 kΩ — two on-resistances in series",
                                "conducting, through 600 Ω — two on-resistances in parallel",
                                "conducting, through 1.2 kΩ — one on-resistance",
                                "open",
                            ],
                            "a": 0,
                            "why": "Both p devices see a LOW gate, so both are closed, and they sit one after "
                                   "the other between the rail and Y. Series resistances add: $1200 + 1200 = "
                                   "2400$ Ω. This is the structural weakness of a NOR gate — its HIGH is "
                                   "driven through a *stack* of the slow devices, while its LOW goes through "
                                   "n devices in parallel. A NAND is the other way up, and since a p device is "
                                   "already two or three times weaker than an n device of the same size, that "
                                   "is why a CMOS library builds most of its logic out of NANDs and pays extra "
                                   "silicon to widen the p devices in the NORs it does use.",
                        },
                        {
                            "prompt": "With the pull-up conducting and the pull-down open, what is Y?",
                            "hole": "?",
                            "opts": ["HIGH", "LOW", "floating", "midway between the rails"],
                            "a": 0,
                            "why": "Y is tied to the 5 V rail through 2.4 kΩ and to ground through a "
                                   "megohm or more, so it settles within a millivolt or two of the rail — a "
                                   "solid HIGH. It is not floating: floating means *neither* network conducts, "
                                   "which is a state this construction is designed never to enter. And it "
                                   "cannot sit midway, because that would need both networks conducting at "
                                   "once, which is the state the dual construction also rules out. This is the "
                                   "$A + B = 0$ row, the only row where a NOR outputs a 1.",
                        },
                        {
                            "prompt": "A is 0 and B is 1. N_A is open and N_B is closed. What is the pull-down doing?",
                            "hole": "?",
                            "opts": [
                                "conducting, through 350 Ω — the one closed device",
                                "conducting, through 175 Ω — the two in parallel",
                                "conducting, through 700 Ω — the two in series",
                                "open — a parallel pair needs both devices closed",
                            ],
                            "a": 0,
                            "why": "The two n devices are side by side, so either one on its own is a complete "
                                   "path from Y to ground: 350 Ω, the on-resistance of the single closed "
                                   "device. The open one contributes a megohm in parallel with that, which "
                                   "changes it by a fraction of an ohm. 175 Ω would be right only if both were "
                                   "closed, and 700 Ω is what a *series* pair of them would give — that is the "
                                   "NAND's pull-down, not this one. The reason parallel-means-OR is exactly "
                                   "this: one closed switch is enough, which is what OR says.",
                        },
                        {
                            "prompt": "A is 1 and B is 0, so P_A has a HIGH on its gate and is open while P_B is closed. What is the pull-up doing?",
                            "hole": "?",
                            "opts": [
                                "open",
                                "conducting, through 1.2 kΩ — the one closed device",
                                "conducting, through 2.4 kΩ",
                                "conducting weakly, through the open device's leakage",
                            ],
                            "a": 0,
                            "why": "A series chain is only as good as its worst link, and one of these two "
                                   "links is a megohm or more. There is no path to the rail worth the name. "
                                   "The tempting answer is that the closed device still gives 1.2 kΩ, but that "
                                   "1.2 kΩ is in series with the open one, and $1200 + 4\\,\\text{M}$ is "
                                   "4 MΩ for every practical purpose. Calling the residue \"conducting weakly\" "
                                   "is not wrong about the physics — leakage is real — but it is the pull-down "
                                   "that decides this node, and it is winning by four orders of magnitude.",
                        },
                        {
                            "prompt": "A is 1 and B is 1, so both n devices are closed. What is the pull-down doing?",
                            "hole": "?",
                            "opts": [
                                "conducting, through 175 Ω — two on-resistances in parallel",
                                "conducting, through 700 Ω — two on-resistances in series",
                                "conducting, through 350 Ω",
                                "open",
                            ],
                            "a": 0,
                            "why": "Two 350 Ω paths side by side carry twice the current for the same voltage, "
                                   "so the pair looks like $350/2 = 175$ Ω. A NOR's LOW is therefore *stronger* "
                                   "than an inverter's, and stronger still than a NAND's, whose two n devices "
                                   "are in series at 700 Ω. Every gate in a library has this asymmetry "
                                   "somewhere: whichever network is the series one is the weak side, and it "
                                   "sets both the worse level and the slower edge.",
                        },
                        {
                            "prompt": "Both networks have now been settled for this row. What is Y?",
                            "hole": "?",
                            "opts": ["LOW", "HIGH", "floating", "undefined, because both inputs are 1"],
                            "a": 0,
                            "why": "The pull-down conducts through 175 Ω and the pull-up is open, so Y is "
                                   "held at ground within a fraction of a millivolt. Read the finished column "
                                   "downwards and it is HIGH, LOW, LOW, LOW — a NOR, produced by nothing but "
                                   "asking which switches are closed. Notice also that exactly one of the two "
                                   "networks conducted on every one of the four rows. That is the property the "
                                   "dual construction guarantees, and it is what makes \"floating\" and "
                                   "\"undefined\" impossible answers rather than merely unlikely ones.",
                        },
                    ],
                },
                {
                    "title": "Two datasheets, one wire",
                    "minutes": 9,
                    "caption": "a 3.3 V part driving a 5 V part, and the subtraction that says whether it works",
                    "lang": "text",
                    "brief": r'''
A noise margin is a subtraction across a boundary between two different parts. Both
numbers have to come from the right datasheet, and both have to be the guaranteed
figures rather than the typical ones.

Here is the interface that catches more people than any other: a 3.3 V logic output
feeding a 5 V CMOS input. The levels below are the light-load guarantees, which is the
best case — this link carries almost no current, so they are the fair ones to use.

Work the two margins, say whether the link is sound, then do it again with a receiver
whose thresholds are in a different place.
''',
                    "listing": """one wire, two parts       driver:   74LVC gate on a 3.3 V rail
                          receiver: 74HC  input on a 5.0 V rail

  what the driver guarantees to put out
    V_OH   weakest HIGH it will produce         3.10 V
    V_OL   strongest LOW it will produce        0.40 V

  what the receiver guarantees to accept
    V_IH   reads HIGH above this                3.50 V     (0.7 x 5.0)
    V_IL   reads LOW  below this                1.50 V     (0.3 x 5.0)

    NM_H = V_OH - V_IH  =  ___ V
    NM_L = V_IL - V_OL  =  ___ V
    verdict on this link:  ___

  now swap the receiver for a 74HCT, whose thresholds are V_IH = 2.00 V, V_IL = 0.80 V

    NM_H = ___ V        NM_L = ___ V        verdict:  ___
""",
                    "blanks": [
                        {
                            "prompt": "The driver's weakest HIGH is 3.10 V and the receiver reads HIGH only above 3.50 V. What is the high-side margin?",
                            "hole": "?",
                            "opts": ["-0.40", "0.40", "1.60", "6.60"],
                            "a": 0,
                            "why": "$3.10 - 3.50 = -0.40$ V. A negative margin is not a small margin, it is "
                                   "the absence of a guarantee: the strongest HIGH this driver promises is "
                                   "below the weakest HIGH this receiver promises to recognise, so nothing in "
                                   "either datasheet says the link works. Writing $+0.40$ means the "
                                   "subtraction was taken the other way round, which quietly converts a "
                                   "broken link into a working one. 1.60 is the distance down to $V_{IL}$, "
                                   "which is the wrong end of the receiver's specification, and 6.60 is the "
                                   "two numbers added.",
                        },
                        {
                            "prompt": "The driver's strongest LOW is 0.40 V and the receiver reads LOW below 1.50 V. What is the low-side margin?",
                            "hole": "?",
                            "opts": ["1.10", "0.40", "1.50", "-1.10"],
                            "a": 0,
                            "why": "$1.50 - 0.40 = 1.10$ V, and it is positive, so the LOW is in good shape "
                                   "with better than a volt of room. This is the half of the interface that "
                                   "works, and it is worth seeing that the two directions are independent "
                                   "subtractions with no reason to come out alike: pulling a node down to "
                                   "ground is an easy job for the driver, while pushing it up to 5 V is "
                                   "something it cannot do at all, because it has no 5 V to reach.",
                        },
                        {
                            "prompt": "One margin is +1.10 V and the other is -0.40 V. What is the verdict on the link?",
                            "hole": "?",
                            "opts": [
                                "broken — the HIGH is not guaranteed to be read as a HIGH",
                                "sound — the margins average out to a comfortable +0.35 V",
                                "broken — the LOW is the side that fails",
                                "sound, provided the track between them is kept short",
                            ],
                            "a": 0,
                            "why": "The worse of the two margins is the one that decides, and margins do not "
                                   "average — a wire that carries a reliable 0 and an unreliable 1 carries "
                                   "nothing you can use. The LOW side is fine at $+1.10$ V, so it is not the "
                                   "failure. Nor is track length the issue: shortening the wire removes noise, "
                                   "and there is no noise here to remove. The signal is arriving exactly as "
                                   "intended and is still not high enough. What makes this failure notorious "
                                   "is that it usually *appears* to work on a bench, because a typical 5 V "
                                   "CMOS part switches near 2.5 V rather than at its guaranteed 3.5 V — so "
                                   "the board runs fine until a cold morning or a different reel of parts.",
                        },
                        {
                            "prompt": "Same driver, but the receiver now reads HIGH above 2.00 V. What is the high-side margin?",
                            "hole": "?",
                            "opts": ["1.10", "0.40", "-1.10", "5.10"],
                            "a": 0,
                            "why": "$3.10 - 2.00 = 1.10$ V. Nothing about the driver changed; the receiver's "
                                   "threshold moved down by 1.50 V and took the margin with it. That is what "
                                   "the T in 74HCT buys — CMOS silicon with the input thresholds of the older "
                                   "TTL parts, put there precisely so that things which cannot reach 3.5 V "
                                   "can still talk to it. It is the cheapest fix for this interface, and it is "
                                   "a receiver-side fix, which is the general lesson: a level problem is "
                                   "solved wherever the mismatch is, not necessarily where it was noticed.",
                        },
                        {
                            "prompt": "And with the receiver now reading LOW below 0.80 V, what is the low-side margin?",
                            "hole": "?",
                            "opts": ["0.40", "1.10", "-0.40", "1.20"],
                            "a": 0,
                            "why": "$0.80 - 0.40 = 0.40$ V. The same swap that rescued the HIGH side cost the "
                                   "LOW side 0.70 V, because moving both thresholds down helps one direction "
                                   "and hurts the other. Nothing here is free: a receiver has one transfer "
                                   "curve, and sliding it along the axis trades one margin for the other.",
                        },
                        {
                            "prompt": "The two margins are now +1.10 V and +0.40 V. What is the verdict?",
                            "hole": "?",
                            "opts": [
                                "it works, and the LOW is now the tighter of the two margins",
                                "it works, and the HIGH is now the tighter of the two margins",
                                "still broken, because 0.40 V is a negative margin in disguise",
                                "it works, with equal margins in both directions",
                            ],
                            "a": 0,
                            "why": "Both margins are positive, so the link is guaranteed by the two "
                                   "datasheets together — and the smaller of them, 0.40 V, is the number to "
                                   "quote when someone asks how much noise the wire can survive. It is the "
                                   "LOW side that is now tighter, which is the reverse of where the trouble "
                                   "started, and it is worth carrying forward: 400 mV is enough for a short "
                                   "track on a quiet board and thin for a metre of ribbon cable running past "
                                   "a motor. Nothing about it is negative, and the two margins are plainly "
                                   "not equal.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "How low is the LOW of a ratioed inverter?",
                    "minutes": 6,
                    "brief": r'''
The cheapest circuit that inverts: a resistor from the rail down to the output, and one
n-channel switch from the output down to ground. The input is HIGH, so the switch is
closed — and a closed switch is not a short. It is a few hundred ohms.

The switch is drawn as the 470 Ω it behaves like. One rule and one unknown: read off the
node the probe is sitting on.
''',
                    "prompt": "What voltage does the output settle at while the pull-down is conducting?",
                    "note": "Give the answer in volts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rl", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "rn", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 470},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
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
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "Pull-up (load) resistor", "value": "10 kΩ"},
                        {"label": "Pull-down switch, closed", "value": "470 Ω"},
                        {"label": "Receiver reads LOW below", "value": "1.50 V"},
                    ],
                    "aside": "Two resistances in a line between the rail and ground. The node between them "
                             "sits at the rail times the share of the total that lies below it.",
                    "answer": 0.2245,
                    "tol": 0.004,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "$V = 5.00 \\times 470/(10\\,000 + 470)$.",
                    "wrong": "0 V assumes the closed switch is a perfect short, which is the idealisation the "
                             "algebra makes and not what the circuit does. 4.78 V is the divider read upside "
                             "down — the probe is above the switch, so the share it takes is the switch's, "
                             "not the resistor's.",
                    "why": "The two resistances are in series, so they add: $10\\,000 + 470 = 10\\,470$ Ω. The "
                           "current is $5.00/10\\,470 = 477.6$ µA, and the drop across the switch is "
                           "$477.6\\,\\mu\\text{A} \\times 470\\,\\Omega = 0.2245$ V. That is comfortably "
                           "below the 1.50 V the receiver needs, so the level is sound.\n\n"
                           "The interesting number is the other one. That 477.6 µA flows for as long as the "
                           "output is LOW — not on the edges, continuously — which is $5.00 \\times 477.6\\,"
                           "\\mu\\text{A} = 2.39$ mW per gate. A hundred thousand of these with half of them "
                           "LOW at any moment is about 119 W, and that is before anything switches. Replacing "
                           "the resistor with a complementary switch removes that current entirely, which is "
                           "the whole argument for CMOS in one figure.",
                },
                {
                    "title": "What a three-input stack costs while it holds a LOW",
                    "minutes": 8,
                    "brief": r'''
The same ratioed construction, now built as a 3-input NAND: three n-channel switches in
series between the output and ground, so the output is only pulled LOW when all three
inputs are HIGH. All three are, so all three are closed, and each is drawn as the 400 Ω
it behaves like.

This time the question is not about the node. It asks what the **supply** is handing over
while the gate sits there holding its LOW, which is one step further along than the
divider.
''',
                    "prompt": "How much power does the 5 V rail deliver to this gate while its output is held LOW?",
                    "note": "Give the answer in milliwatts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rl", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 12000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "na", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 400},
                            {"id": "nb", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 400},
                            {"id": "nc", "kind": "R", "x": 9, "y": 13, "rot": 1, "value": 400},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 17},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [9, 4]},
                            {"a": [9, 6], "b": [9, 8]},
                            {"a": [9, 10], "b": [9, 12]},
                            {"a": [9, 14], "b": [9, 17]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "Load resistor", "value": "12 kΩ"},
                        {"label": "Each closed switch", "value": "400 Ω"},
                        {"label": "Switches in the stack", "value": "3, in series"},
                    ],
                    "aside": "Power delivered by a source is its voltage times the current through it. The "
                             "current is the same everywhere in a single series loop.",
                    "answer": 1.894,
                    "tol": 0.02,
                    "unit": "mW",
                    "check": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const d = c.dc();
return Math.abs(d.currents[src.id]) * src.value * 1000;
''',
                    "hint": "Add the three switches to the load resistor for the total, get the current from "
                            "$I = V/R$, then $P = VI$ using the full 5.00 V of the rail.",
                    "wrong": "0.172 mW is the power in the stack alone ($I^2R$ with $R = 1200$ Ω) rather than "
                             "the power the rail delivers, which includes the far larger amount burned in the "
                             "load resistor. 2.08 mW comes from forgetting the stack and dividing by 12 kΩ "
                             "alone.",
                    "why": "The three switches are in series with each other and with the load, so everything "
                           "adds: $12\\,000 + 3 \\times 400 = 13\\,200$ Ω. The current is $5.00/13\\,200 = "
                           "378.8$ µA, and the rail delivers $5.00 \\times 378.8\\,\\mu\\text{A} = 1.894$ "
                           "mW.\n\n"
                           "Two things are hiding in that number. The output is sitting at $378.8\\,\\mu"
                           "\\text{A} \\times 1200\\,\\Omega = 0.455$ V, twice the 0.224 V an inverter managed "
                           "on a 10 kΩ load — every device you add to a series stack lifts the LOW, and a "
                           "wide NAND built this way eventually lifts it into the forbidden band. And of the "
                           "1.894 mW, only $I^2 \\times 1200 = 0.172$ mW is dissipated in the switches; the "
                           "other 1.72 mW is burned in the load resistor, whose entire function is to be in "
                           "the way. That is what a complementary pull-up removes.",
                },
                {
                    "title": "How far from the rail does a real CMOS HIGH sit?",
                    "minutes": 10,
                    "brief": r'''
A genuine 2-input CMOS NAND on a 3.3 V board, drawn as the four resistances its four
transistors behave like. Input A is LOW and input B is HIGH, so:

* the two p devices above the output are in **parallel** — P_A is closed at 1.2 kΩ
  because its gate is LOW, P_B is open at 4 MΩ;
* the two n devices below the output are in **series** — N_A is open at 4 MΩ, N_B is
  closed at 350 Ω.

The output should be a HIGH, and it is. The question is how good a HIGH: the answer is
not 3.3 V exactly, and the size of the shortfall is the point.
''',
                    "prompt": "How many millivolts below the 3.3 V rail does the output settle?",
                    "note": "Give the answer in millivolts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 3.3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 12},
                            {"id": "pa", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 1200},
                            {"id": "pb", "kind": "R", "x": 6, "y": 6, "rot": 0, "value": 4000000},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 3},
                            {"id": "na", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 4000000},
                            {"id": "nb", "kind": "R", "x": 9, "y": 13, "rot": 1, "value": 350},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 17},
                        ],
                        "wires": [
                            {"a": [3, 9], "b": [3, 12]},
                            {"a": [3, 7], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [5, 3], "b": [5, 6]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [7, 6], "b": [9, 6]},
                            {"a": [9, 3], "b": [9, 6]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [9, 6], "b": [9, 8]},
                            {"a": [9, 10], "b": [9, 12]},
                            {"a": [9, 14], "b": [9, 17]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "3.30 V"},
                        {"label": "P_A closed / P_B open", "value": "1.2 kΩ ∥ 4 MΩ"},
                        {"label": "N_A open + N_B closed", "value": "4 MΩ + 350 Ω"},
                        {"label": "Asked for", "value": "rail minus output, in mV"},
                    ],
                    "aside": "Reduce each network to one resistance first — the parallel pair above, the "
                             "series pair below — and what is left is a two-resistor divider.",
                    "answer": 0.989,
                    "tol": 0.015,
                    "unit": "mV",
                    "check": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
return (src.value - c.vout()) * 1000;
''',
                    "hint": "Pull-up: $1200 \\parallel 4\\,\\text{M} \\approx 1199.6$ Ω. Pull-down: $4\\,"
                            "\\text{M} + 350 \\approx 4\\,000\\,350$ Ω. The shortfall is the rail times the "
                            "pull-up's share of the total.",
                    "wrong": "If you got about 3.30 V, the question was read as asking for the output "
                             "itself rather than the gap between the output and the rail. If you got 2.55 V, "
                             "the open devices were dropped and the divider taken between the two *closed* "
                             "ones, 1.2 kΩ against 350 Ω — but a settled CMOS gate never has both networks "
                             "conducting, and the megohms are precisely what make the answer small.",
                    "why": "The parallel pair above is $1200 \\times 4\\,\\text{M}/(1200 + 4\\,\\text{M}) = "
                           "1199.64$ Ω — a megohm in parallel with a kilohm is a kilohm, and the open device "
                           "is doing nothing. The series pair below is $4\\,000\\,000 + 350 = 4\\,000\\,350$ "
                           "Ω, and here the open device is doing everything. The divider is "
                           "$3.30 \\times 1199.64/(1199.64 + 4\\,000\\,350) = 0.000989$ V, so the output sits "
                           "**0.989 mV** below the rail at 3.29901 V.\n\n"
                           "Under a millivolt of shortfall, from a gate whose strong device is a fairly "
                           "feeble 1.2 kΩ. That is the whole reason CMOS levels are quoted as rail-to-rail: "
                           "the divider is not between two comparable resistances but between one that is "
                           "thousands of times larger than the other, and the ratio is what sets the "
                           "shortfall, not the absolute size of either. Worth knowing that the 4 MΩ drawn "
                           "here is far more conductive than a real off device, which runs to gigaohms — the "
                           "figure is drawn pessimistically so that the shortfall is a number you can see. "
                           "With a realistic device it would be a microvolt.",
                },
                {
                    "title": "The margin a shared ground return takes away",
                    "minutes": 13,
                    "brief": r'''
A sensor board two metres away on a ribbon cable, and the same CMOS NAND from the last
question — but now with both inputs HIGH, so both n devices are closed at 350 Ω in series
and both p devices are open at 4 MΩ in parallel. Its output should therefore be a clean
LOW.

The catch is the ground. The ribbon carries one conductor back to the main board's
ground, and its resistance plus the two connectors comes to 0.6 Ω. That same conductor is
the return path for a small motor on the sensor board drawing 300 mA, drawn here as the
current source it behaves like.

The receiver is on the main board, so it measures the arriving signal against the **main
board's** ground, not the sensor board's. It reads LOW below 0.80 V. What margin is left?
''',
                    "prompt": "How much low-side noise margin does the receiver have left, $V_{IL}$ minus the voltage it actually sees?",
                    "note": "Give the answer in volts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 3.3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 12},
                            {"id": "pa", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 4000000},
                            {"id": "pb", "kind": "R", "x": 6, "y": 6, "rot": 0, "value": 4000000},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 3},
                            {"id": "na", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 350},
                            {"id": "nb", "kind": "R", "x": 9, "y": 13, "rot": 1, "value": 350},
                            {"id": "rr", "kind": "R", "x": 9, "y": 18, "rot": 1, "value": 0.6},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 22},
                            {"id": "i0", "kind": "I", "x": 14, "y": 16, "rot": 0, "value": 0.3},
                            {"id": "g2", "kind": "GND", "x": 17, "y": 16},
                        ],
                        "wires": [
                            {"a": [3, 9], "b": [3, 12]},
                            {"a": [3, 7], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [5, 3], "b": [5, 6]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [7, 6], "b": [9, 6]},
                            {"a": [9, 3], "b": [9, 6]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [9, 6], "b": [9, 8]},
                            {"a": [9, 10], "b": [9, 12]},
                            {"a": [9, 14], "b": [9, 16]},
                            {"a": [9, 16], "b": [9, 17]},
                            {"a": [9, 19], "b": [9, 22]},
                            {"a": [13, 16], "b": [9, 16]},
                            {"a": [15, 16], "b": [17, 16]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "3.30 V"},
                        {"label": "Pull-down, both closed", "value": "350 Ω + 350 Ω"},
                        {"label": "Pull-up, both open", "value": "4 MΩ ∥ 4 MΩ"},
                        {"label": "Shared ground return", "value": "0.6 Ω"},
                        {"label": "Motor current in that return", "value": "300 mA"},
                        {"label": "Receiver reads LOW below", "value": "0.80 V"},
                    ],
                    "aside": "The sensor board's local ground is no longer at zero. Find what it is sitting "
                             "at, then add the drop across the pull-down stack on top of it, then subtract "
                             "the total from $V_{IL}$.",
                    "answer": 0.619,
                    "tol": 0.004,
                    "unit": "V",
                    "check": r'''
/* V_IL belongs to the receiver's datasheet, not to the schematic, so it is stated here */
const VIL = 0.80;
return VIL - c.vout();
''',
                    "hint": "The motor current sets the local ground: $0.300\\,\\text{A} \\times 0.6\\,\\Omega$. "
                            "The gate's own current is tiny — the pull-up is 2 MΩ — so work out how little the "
                            "700 Ω stack adds on top, and then subtract the sum from 0.80 V.",
                    "wrong": "0.620 V comes from ignoring the pull-down stack entirely and using 0.180 V as "
                             "the arriving level; that is only 1 mV out here, which is worth noticing rather "
                             "than being annoyed by. 0.799 V is the answer with the motor current left out, "
                             "and that is the error that matters — it is the whole effect.",
                    "why": "Start at the bottom. The motor's 300 mA returns through 0.6 Ω, so the sensor "
                           "board's local ground sits at $0.300 \\times 0.6 = 0.180$ V above the main board's "
                           "ground. Everything on the sensor board is now referenced to that.\n\n"
                           "The gate's own current is small: the pull-up is $4\\,\\text{M} \\parallel 4\\,"
                           "\\text{M} = 2$ MΩ and the pull-down stack is $350 + 350 = 700$ Ω, so "
                           "$I = (3.30 - 0.180)/2\\,000\\,700 = 1.559$ µA and the drop across the stack is "
                           "$1.559\\,\\mu\\text{A} \\times 700\\,\\Omega = 1.09$ mV. The output therefore "
                           "arrives at $0.180 + 0.0011 = 0.1811$ V, and the margin is "
                           "$0.80 - 0.1811 = 0.619$ V.\n\n"
                           "Look at what those two contributions are worth. The transistors — the part of "
                           "the circuit anyone would think to check — contribute 1.09 mV. The ground wire "
                           "contributes 180 mV, one hundred and sixty times as much, and it does not appear "
                           "in any datasheet. This is why a logic 0 is defined against a *specific* ground "
                           "and why the return path is drawn deliberately rather than assumed: the moment "
                           "two boards disagree about where zero is, the disagreement is subtracted straight "
                           "out of the noise margin. Give the motor its own return conductor and the 180 mV "
                           "goes away.\n\n"
                           "One honest limit. This is the DC version of the effect. On a real board most "
                           "ground bounce comes from inductance rather than resistance — $L\\,di/dt$ across "
                           "the bond wires and connector pins while many outputs switch at once — which a DC "
                           "solver cannot show. The arithmetic is different; the conclusion, that the return "
                           "path eats the margin, is the same.",
                },
            ],
            "match": {
                "title": "The parts on a logic board",
                "minutes": 6,
                "brief": r'''
The algebra says nothing about what is actually on the board. These six turn up on
every piece of discrete logic ever built, and each of them is doing one specific job
for the gates around it — which is what the explanations are about, rather than the
shapes.
''',
                "prompt": "Pick a label, then tap the symbol it belongs to.",
                "labels": ["Switch", "Resistor", "Diode", "LED", "Ground", "Battery"],
                "items": [
                    {"sym": "SW", "a": 0, "why": (
                        "A switch: the simplest input a logic circuit can have. On its own it produces no "
                        "voltage at all — it either connects a node to something or leaves it floating — which "
                        "is why it is almost always drawn with a pull-up resistor beside it, so that the open "
                        "position still means something definite."
                    )},
                    {"sym": "R", "a": 1, "why": (
                        "A resistor. In logic its usual job is not to divide anything but to **pull up**: it "
                        "ties a node gently to the supply so that an otherwise floating input reads as a 1, "
                        "while being weak enough that anything actively pulling the node low wins the argument."
                    )},
                    {"sym": "D", "a": 2, "why": (
                        "A diode: current one way, blocked the other, drawn as a triangle pointing into a bar. "
                        "Two of them and a resistor make an AND gate, which is how logic was built before "
                        "transistors were cheap — and its lack of gain is why that stopped being enough."
                    )},
                    {"sym": "LED", "a": 3, "why": (
                        "An LED: the same triangle into a bar, with two arrows leaving it. It is a diode being "
                        "used as an output indicator, and like any diode it holds a roughly fixed forward drop, "
                        "so a series resistor is what actually sets its current."
                    )},
                    {"sym": "GND", "a": 4, "why": (
                        "Ground: the node every other voltage is quoted against, and the return path for the "
                        "pull-down half of every gate. A logic 0 is not an absence of anything — it is a wire "
                        "being actively held here."
                    )},
                    {"sym": "BATT", "a": 5, "why": (
                        "A battery — the supply, drawn as alternating long and short bars. A logic 1 is a "
                        "fraction of whatever this provides, and so is every threshold in this module: "
                        "$V_{OH}$, $V_{IH}$ and both noise margins move with the supply."
                    )},
                ],
            },
            "tune": {
                "title": "Sizing a ratioed inverter, with all three bills at once",
                "minutes": 11,
                "brief": r'''
Before complementary switches were cheap, an inverter was one n-channel device pulling
down against a resistor pulling up, and the whole design was the *ratio* between them.
That is the circuit here: R1 is the load resistor from the 5 V rail, R2 is the
on-resistance of the pull-down device, which a designer sets by choosing how wide to draw
it. The readout is the gate in its LOW state.

Three demands, and no two of them pull the same way.

**The LOW has to be a real LOW.** The output is a divider, so a small $V_{OL}$ needs
$R_1 \gg R_2$ — a large load resistor, or a very wide pull-down device, or both.

**The LOW must not cost too much.** That divider current flows the whole time the output
is LOW. Cutting it means making $R_1 + R_2$ large, which points the same way as the first
demand.

**But the gate has to be able to rise.** When the pull-down turns off, the load resistor
alone charges the next stage's input capacitance, and the current it can supply the
instant the output starts to move is exactly the current the readout is showing you. Too
little and the rising edge crawls. That points the opposite way.

The first two are satisfied by making everything bigger; the third is not. Find the
window where all three hold.
''',
                "prompt": "Get the LOW below 0.40 V while keeping the standing current between 0.25 mA and 0.50 mA.",
                "note": "R1 is the load resistor and R2 the pull-down device's on-resistance. All three constraints must hold at the same time.",
                "model": "divider",
                "initial": {"r1": 4700, "r2": 1000},
                "constants": {"vin": 5},
                "constraints": [
                    {"k": "vout", "label": "the LOW is a real LOW: Vout ≤ 0.40 V", "max": 0.40},
                    {"k": "i", "label": "no more than 0.50 mA burned while the output sits LOW", "max": 0.50},
                    {"k": "i", "label": "at least 0.25 mA available to start the rising edge", "min": 0.25},
                ],
            },
            "derive": {
                "title": "Where the power in a digital chip actually goes",
                "minutes": 13,
                "brief": r'''
A settled CMOS gate draws almost no current, and yet a processor gets hot enough to
need a fan. Both things are true, and the reconciliation is that a chip is almost
never settled: at three billion clock edges a second, its wires are being charged and
discharged continuously, and each of those movements of charge costs energy.

Take one gate output driving a total load capacitance $C$ from a supply of $V$ volts,
switching $f$ times a second. Six short steps get from the definition of capacitance
to the expression on every chip datasheet.
''',
                "vars": ["C", "V", "f", "Q", "W", "U", "P"],
                "steps": [
                    {
                        "prompt": "The output rises from 0 to $V$, which means charging the load capacitance $C$ up to $V$. Write the charge $Q$ that has to arrive on it.",
                        "answer": "C V",
                        "hint": "The definition of capacitance is $C = Q/V$. Rearrange it.",
                        "deconstruct": [
                            "Capacitance is charge per volt: $C = Q/V$.",
                            "So the charge needed to reach $V$ volts is $Q = CV$.",
                        ],
                    },
                    {
                        "prompt": "That charge is pushed through the pull-up network by the supply, which stays at $V$ the whole time. Write the energy $W$ the supply gives up.",
                        "given": "The supply does not sag: every coulomb it delivers falls through the full $V$.",
                        "answer": "C V^2",
                        "hint": "Energy is charge times the potential difference it is moved through, and here that difference is $V$ for every last coulomb.",
                        "deconstruct": [
                            "Energy delivered $= Q \\times V$.",
                            "Substitute $Q = CV$ from the previous step.",
                        ],
                    },
                    {
                        "prompt": "Now the energy $U$ that ends up stored in the capacitor once its voltage has reached $V$.",
                        "answer": "\\frac{1}{2} C V^2",
                        "hint": "The capacitor's own voltage climbs from 0 to $V$ as the charge arrives, so the average voltage the charge falls through is only half of $V$.",
                        "deconstruct": [
                            "The stored energy is $\\int v\\,dq$ with $v = q/C$.",
                            "Integrating from 0 to $Q$ gives $Q^2/2C$, which is $\\tfrac{1}{2}CV^2$.",
                        ],
                    },
                    {
                        "prompt": "The supply handed over $W$ and only $U$ was stored. The difference was dissipated as heat in the pull-up network on the way. Write that amount.",
                        "answer": "\\frac{1}{2} C V^2",
                        "hint": "Subtract the previous step from the one before it, and notice what the answer is a half of.",
                        "deconstruct": [
                            "$W - U = CV^2 - \\tfrac{1}{2}CV^2$.",
                            "Exactly half the energy drawn from the supply is lost, whatever the resistance of the network happens to be.",
                        ],
                    },
                    {
                        "prompt": "On the falling edge the capacitor discharges to ground through the pull-down network, giving up everything it had stored. Write the total energy dissipated over one complete cycle — one rise and one fall.",
                        "answer": "C V^2",
                        "hint": "Half of it went on the way up, and the stored half goes on the way down.",
                        "deconstruct": [
                            "Rising edge: $\\tfrac{1}{2}CV^2$ dissipated, $\\tfrac{1}{2}CV^2$ stored.",
                            "Falling edge: the stored $\\tfrac{1}{2}CV^2$ is dissipated too, and nothing is left.",
                        ],
                    },
                    {
                        "prompt": "Finally, $f$ complete cycles happen every second. Write the average power $P$.",
                        "answer": "C V^2 f",
                        "hint": "Power is energy per unit time: multiply the energy per cycle by the number of cycles per second.",
                        "deconstruct": [
                            "One cycle costs $CV^2$ joules.",
                            "There are $f$ of them per second, so $P = CV^2 f$ watts.",
                        ],
                    },
                ],
                "closing": r'''
$$P = C V^2 f$$

Three things follow, and all three shaped the last thirty years of hardware.

The resistance of the switch network never appeared. A slower gate takes longer to
dissipate the same $\tfrac{1}{2}CV^2$; it does not dissipate less. You cannot save
switching energy by making the transistors weaker.

The voltage is squared and the frequency is not, so the supply is the term worth
attacking. A processor core with 2 nF of capacitance switching at 3 GHz costs
$2\times10^{-9} \times 1.0^2 \times 3\times10^{9} = 6$ W at a 1 V supply. Run the
same core at the 5 V rail that logic used in the 1980s and it would be 150 W.

And a caveat worth carrying: not every node switches on every cycle, so the figure
quoted for a real chip is $P = \alpha C V^2 f$, where $\alpha$ is the fraction that
actually moves. The $C$ in a datasheet is an effective switched capacitance measured
on real workloads, not the physical capacitance of the silicon.
''',
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Decoders, multiplexers and the blocks everyone reuses",
            "summary": "Four standard blocks that appear in every design, and the useful fact that a multiplexer with its data inputs tied to constants is any function you like.",
            "concepts": [
                "A **decoder** takes $n$ inputs and drives $2^n$ outputs, exactly one of them active — the one whose number matches the input. It is the truth table's rows made physical, and it is how a memory picks a word and how an instruction picks an operation.",
                "A **multiplexer** goes the other way: $2^n$ data inputs, $n$ select inputs, and one output that copies whichever data input the select names. For the two-input case, $Y = S'D_0 + SD_1$ — which is a sum of products with the data lines carried along.",
                "Because that expression is the select's minterm expansion, tying the data inputs to **constants** makes the block any Boolean function of the select variables: write the truth table's output column down the data inputs and there is no logic left to design. This is exactly how an FPGA's lookup table works, and you will meet it again in module 10.",
                "An **encoder** is a decoder backwards: $2^n$ inputs of which one is active, $n$ outputs naming which. A plain encoder is just an OR of the codes and produces nonsense if two inputs are active at once; a **priority encoder** answers \"the highest-numbered active input\", which is what an interrupt controller needs, because more than one device can want attention at the same moment.",
                "A decoder's outputs **glitch** while its inputs are changing: different paths through the logic settle at different times, so for a few nanoseconds after an edge, outputs that should never be active together can be. In a synchronous design this costs nothing, because nothing reads the outputs until the clock edge, by which time everything has settled.",
                "An **enable** input, ANDed into every one of the $2^n$ products, is what lets a decoder mean *nothing*. Without it the address `000` is not \"off\", it is \"select device 0\", and a bus with nothing selected is an ordinary state that has to be representable.",
                "A wide decoder is not built flat. Split the address in half, decode each half on its own, and AND every high line against every low line: 640 gate inputs against 2048 at eight address bits, with no gate wider than four inputs. A memory array **is** that arrangement, and its two halves are the row decoder and the column decoder.",
                "**Shannon's expansion**, $F = x'\\,F|_{x=0} + x\\,F|_{x=1}$, is the identity underneath the lookup table. Stopping one variable short of the end puts an $n$-variable function on a $2^{n-1}$-to-1 multiplexer, with the data inputs drawn from $0$, $1$, $x$ and $x'$ — half the block for one shared inverter.",
                "A real **analogue** multiplexer is switches rather than gates, and it leaks in three ways: an on-resistance of order 100 Ω in series with the selected signal, a finite off-resistance on the others, and a few picofarads across each open switch which carry an unselected input through at roughly $2\\pi f R_{on} C_{off}$ — an isolation that worsens by 20 dB per decade.",
            ],
            "read": [
                {
                    "title": "One line out of many: the decoder",
                    "minutes": 14,
                    "body": r'''
Here is the problem the block exists to solve, stated before any gates.

A board carries eight memory chips and one bus. All eight see the same thirteen
address lines and the same eight data lines, wired in parallel, because running a
separate bus to each would need eight times the copper and buy nothing. What stops all
eight from answering at once is a single pin on each chip — the **chip select** — and
the rule of the board is that exactly one of those eight pins may be active at any
instant. Two active, and two chips drive the data bus together; a chip driving a 1 into
a chip driving a 0 is a path from the rail to ground through two output transistors,
which is how boards get hot. None active, and the bus floats at whatever the last
driver left on it.

So the requirement is precise, and notice that it is not "compute something". It is:
*given a number, make exactly one wire of a row active — the one whose position is that
number.* A number is a compact name for a thing. A place is a spread-out name for the
same thing. A **decoder** converts the first into the second, and that is all it does.

## The rows of a truth table, made out of copper

You already have the machinery. In module 3 every function of $n$ variables was written
as a sum of minterms, one minterm per row of the table, each minterm an AND of all $n$
variables with the ones that are 0 on that row complemented. The minterm for a row is 1
on that row and 0 on every other row in the table — that is the entire property that
made the canonical form work.

Read that property again with the chip-select problem in mind. *One signal per row,
exactly one of which is true at any moment.* The minterms of $n$ variables are already
a set of $2^n$ one-hot signals. A decoder is what you get when you build all of them
and stop before the OR gate that would have combined them.

That is worth saying plainly, because it is the whole design: **a decoder is the
canonical sum-of-products with the sum removed.** Nothing new is invented here: the
same $2^n$ AND gates that module 3 built and then discarded most of are all kept, and
each one is brought out to a pin.

## A 2-to-4 decoder, gate by gate

Two inputs, four outputs. Write the table with the outputs as four columns:

```
 A1 A0 | Y3 Y2 Y1 Y0
 ------+------------
  0  0 |  0  0  0  1
  0  1 |  0  0  1  0
  1  0 |  0  1  0  0
  1  1 |  1  0  0  0
```

Read each column down and it is a minterm, so the four expressions come off the table
with nothing to work out:

$$Y_0 = A_1'A_0' \qquad Y_1 = A_1'A_0 \qquad Y_2 = A_1A_0' \qquad Y_3 = A_1A_0$$

Four two-input AND gates and two inverters. Trace the input `10` all the way through,
because the arithmetic is short and it makes the one-hot property concrete rather than
asserted:

```
 A1 = 1, A0 = 0    so    A1' = 0, A0' = 1

 Y0 = A1'·A0' = 0 · 1 = 0
 Y1 = A1'·A0  = 0 · 0 = 0
 Y2 = A1 ·A0' = 1 · 1 = 1
 Y3 = A1 ·A0  = 1 · 0 = 0
```

`10` is two, and output number 2 is the one that came out 1. Every other output was
killed by at least one 0 in its product, and the reason no two can be 1 together is
that any two of those four products disagree about at least one literal — and a
variable and its complement cannot both be 1.

## An enable, and what it is really for

A decoder as written above is never off. Feed it `00` and $Y_0$ goes active; there is no
input pattern that means *nothing*. For a chip-select generator that is a problem, since
"no memory selected" is a perfectly ordinary state of a bus.

The fix is one more literal in every product. Add an input $E$ and AND it into all
$2^n$ terms:

$$Y_k = E \cdot m_k$$

With $E = 0$ every output is 0 regardless of the address. With $E = 1$ the block behaves
exactly as before. It costs one extra input on each AND gate, and it turns the decoder
from a converter into a converter with an off switch — which is what makes the next
trick possible.

## Worked example: eight chips and a memory map

Back to the board in the first paragraph, with real numbers on it. A processor with a
16-bit address bus can name $2^{16} = 65\,536$ bytes. The chips hold 8 KiB each — that
is $8192 = 2^{13}$ bytes — so thirteen address lines, $A_{12}$ down to $A_0$, go to
every chip in parallel and pick a byte *inside* whichever chip is selected. Three lines
are left, $A_{15}A_{14}A_{13}$, and they have nothing to do but choose the chip. One
3-to-8 decoder, eight chips, and the address space is covered exactly.

The map falls out of place value, because each of those three top bits is worth 8192
bytes:

```
 A15 A14 A13   output   addresses
 -----------   ------   -----------------
   0   0   0     Y0     0x0000 - 0x1FFF
   0   0   1     Y1     0x2000 - 0x3FFF
   0   1   0     Y2     0x4000 - 0x5FFF
   0   1   1     Y3     0x6000 - 0x7FFF
   1   0   0     Y4     0x8000 - 0x9FFF
   1   0   1     Y5     0xA000 - 0xBFFF
   1   1   0     Y6     0xC000 - 0xDFFF
   1   1   1     Y7     0xE000 - 0xFFFF
```

Decode `0x6A3C` by hand. In binary it is `0110 1010 0011 1100`. The top three bits are
`011`, which is three, so $Y_3$ is the output that goes active and chip 3 answers. The
thirteen bits underneath are the offset: $\text{0x6A3C} - \text{0x6000} =
\text{0x0A3C}$, which is 2620, so the byte wanted is number 2620 of chip 3. Every chip
sees the same 2620 on its address pins; seven of them are not selected and say nothing.

That last sentence is the design. The decoder does not route data anywhere and does not
touch the address lines. It only decides who is allowed to answer.

## Sixteen outputs out of five small decoders

Suppose you have 2-to-4 decoders and need a 4-to-16. Split the four address bits into a
high pair and a low pair.

* One 2-to-4 decoder takes $A_3A_2$. Its four outputs are the four **enables**.
* Four more 2-to-4 decoders all take the same $A_1A_0$, and each has its enable driven
  by one output of the first.

Follow the address `1101`:

```
 A3 A2 = 11   ->  the first decoder raises its output 3
                  which enables sub-decoder 3, and only that one
 A1 A0 = 01   ->  every sub-decoder decodes 01 internally,
                  but only sub-decoder 3 is enabled, so only its output 1 goes active

 global output number = 4 x 3 + 1 = 13
 and 1101 in binary is 13.
```

The arithmetic that matters here is $4 \times 3 + 1$: the high pair chooses which group
of four, the low pair chooses which member of the group, and place value does the rest.
That is exactly the same statement as "the address is $4h + l$, where $h$ is the top
pair read as a two-bit number and $l$ is the bottom pair", and it is the reason the
split works at all.

Now count what it cost, in gate inputs, the measure module 3 used for a Karnaugh map.

```
 flat 4-to-16   :  16 ANDs of 4 inputs                     = 64 gate inputs
 two-level      :  2 half-decoders, 4 ANDs of 2 each       = 16
                   16 final ANDs of 2 inputs               = 32
                                                     total = 48
```

Both need the same four inverters, so they cancel out of the comparison. 48 against 64
is a real but unexciting saving; the derivation later in this module works out what
happens at eight and sixteen address bits, where the gap becomes the difference between
a design and a fantasy.

One honest footnote on that count. The enable-cascade above is not quite the same
circuit as the two-level count: it duplicates the $A_1A_0$ decode inside all four
sub-decoders, so its ANDs are three-input and it comes to 56 gate inputs rather than 48.
The pure two-level form decodes each half **once** and then ANDs every high line against
every low line. Memory arrays are built the second way, and the two halves are called
the row decoder and the column decoder.

## Active LOW, because that is what the parts do

Open a datasheet for a 74HC138 — the standard 3-to-8 — and the selected output goes
**LOW** while the other seven sit HIGH. The outputs are drawn with a bar,
$\overline{Y_0}$, and by De Morgan the gates are NANDs rather than ANDs:
$\overline{Y_k} = \overline{E \cdot m_k}$.

There are two reasons and both still apply. Historically, bipolar outputs sink current
much better than they source it, so the active state was made the one that sinks.
Structurally, request lines are usually active LOW so that several open-drain devices
can share one wire: tie the outputs together with a single pull-up and the wire performs
an AND of the HIGH states, which by De Morgan is an OR of the active-LOW ones. A wire
that ORs is worth having and costs no gate. Chip selects are not shared like that, but
they inherited the polarity from the parts that are.

The practical consequence is that the idle state of a decoder's output bus is all ones,
not all zeros, and a scope trace of a working board looks like seven flat HIGH lines and
one that dips. Reading that as seven faults is the first thing everyone does.

## The glitch: two outputs active at once, for 1.2 ns

The one-hot property is a statement about the table, and the table describes only the
settled circuit. While the inputs are moving, it is not true.

Take the 2-to-4 decoder above and change the address from `01` to `11` — that is, $A_0$
stays 1 and $A_1$ rises at $t = 0$. Give the inverter 1.2 ns of delay and each AND gate
0.8 ns.

```
 t = 0        A1 rises. It reaches the AND gates immediately;
              the inverter has not reacted yet, so A1' is still 1.

 t = 0.8 ns   Y3 = A1·A0 rises.        Y3 is now HIGH.
              Y1 = A1'·A0 is also HIGH, because A1' is still 1.

 t = 1.2 ns   A1' finally falls.

 t = 2.0 ns   Y1 = A1'·A0 falls.       Now only Y3 is HIGH.

 overlap: from 0.8 ns to 2.0 ns  ->  1.2 ns with TWO outputs active
```

The overlap is 1.2 ns, which is exactly the inverter's delay — the extra gate in one
path and not the other is the whole mechanism. Run the address the other way, from `11`
to `01`, and the same imbalance produces a 1.2 ns window with **neither** output active.

In a synchronous design this costs nothing, because nothing looks at the decoder until
the clock edge and by then everything has settled. On a chip-select bus driving real
memories it is not nothing at all: for 1.2 ns two chips think they are selected, and if
their outputs are fast enough to react they will fight. This is why memory buses gate
the chip selects with the enable rather than letting the address ripple through bare,
and why the 74HC138 has three enable pins — you hold the decoder off while the address
moves, and turn it on once.

## The mistake people actually make

**Confusing the input count with the output count.** Given `101`, people write "outputs
1, 0 and 1". It is tempting because both sides of the block are rows of wires carrying
ones and zeros, and nothing in the picture says which row is a *number* and which is a
set of *places*. Three input wires; eight output wires; the three spell five, the eight
contain one active line at position five.

**Assuming a decoder can be idle.** Without an enable, address `000` is not "off", it is
"select device 0". Every real design needs a way to say nothing, and it is always an
enable, never an address.

**Believing the outputs are mutually exclusive at all times.** They are mutually
exclusive in the truth table, which is a statement about settled values. The 1.2 ns
above is the same fact from the other side.

## Where the idea stops

**At the fan-in of a real gate.** A 6-to-64 decoder needs sixty-four seven-input ANDs
if you count the enable. Seven-input gates exist in a library but they are slow, because
a CMOS gate's delay grows with the number of series transistors in it, and a wide gate
also presents a bigger load to whatever drives it. Past about four inputs a real
synthesiser stops building the gate and starts building a tree — which is the two-level
decoder arriving whether you asked for it or not.

**At full decoding, once the address space is large.** A 32-bit address has $2^{32}$
possible values and nobody builds a decoder with four billion outputs. A memory chip
decodes the low bits internally with a two-dimensional array of row and column
decoders, and the board decodes only the top few bits — sometimes fewer than it should.
**Partial decoding** is what happens when you leave an address line out of the decode to
save a gate. If a board decodes $A_{14}$ and $A_{13}$ but ignores $A_{15}$, then
`0x6A3C` and `0xEA3C` differ only in $A_{15}$ and both select the same chip at the same
offset. Every byte appears twice in the map. That is a real technique on cost-sensitive
boards, and it is also a real bug when it was not deliberate, because the symptom is
that a write to a variable at one address quietly corrupts an unrelated variable at
another.

**At the point where you do not want a number at all.** A decoder assumes the thing
selecting is a compact binary code. Some designs skip the code and keep the state one-hot
throughout — a one-hot state machine, in module 9, does exactly this — and then there is
no decoder anywhere, because the places were never encoded into a number in the first
place. Encoding and decoding are a matched pair, and the cheapest decoder is the one
you did not need.
''',
                },
                {
                    "title": "The multiplexer, and the moment its data inputs become constants",
                    "minutes": 15,
                    "body": r'''
Turn the decoder round. Instead of one number choosing which of many wires to activate,
one number chooses which of many wires to *listen to*. That is a **multiplexer**:
$2^n$ data inputs, $n$ select inputs, one output that carries a copy of whichever data
input the select names.

The mental picture is a rotary switch — a knob with a pointer, and the number on the
select lines is the position of the knob. It is worth holding onto that picture because
it says what a multiplexer does not do. It does not combine its inputs, average them, or
compute with them. It picks one and ignores the rest completely.

## Building one out of parts you already have

The requirement, in words: the output should be $D_k$ when the select is $k$. Written
as a sum over all the cases, for the two-input version with one select line $S$:

$$Y = S'D_0 + SD_1$$

Check it by cases, which is the only check this expression needs. With $S = 0$ the
second term is 0 and the first is $1 \cdot D_0 = D_0$. With $S = 1$ the first term is 0
and the second is $D_1$. The two products can never both be alive, because $S'$ and $S$
cannot both be 1 — the same fact that made the decoder's outputs one-hot, doing the same
job here.

And that is how the block is actually built: a decoder generates the one-hot conditions,
one AND gate per data line uses its condition as a gate, and one OR gate merges the
results. The OR is safe precisely because at most one of its inputs is ever non-zero.

For four inputs and two select lines the pattern extends by writing all four minterms of
the select:

$$Y = S_1'S_0'D_0 + S_1'S_0D_1 + S_1S_0'D_2 + S_1S_0D_3$$

## Worked example: four inputs, traced

Put $S_1S_0 = 10$ and the data lines at $D_0 = 1$, $D_1 = 0$, $D_2 = 1$, $D_3 = 0$.

```
 S1 = 1, S0 = 0   so   S1' = 0, S0' = 1

 term 0 :  S1'·S0'·D0 = 0 · 1 · 1 = 0
 term 1 :  S1'·S0 ·D1 = 0 · 0 · 0 = 0
 term 2 :  S1 ·S0'·D2 = 1 · 1 · 1 = 1
 term 3 :  S1 ·S0 ·D3 = 1 · 0 · 0 = 0

 Y = 0 + 0 + 1 + 0 = 1,  which is D2.
```

Now change $D_0$ to 0 and re-run: term 0 was already 0 because of $S_1'$, so nothing
moves. The output does not depend on the unselected inputs at all — not weakly, not
approximately. They are multiplied by zero.

## Shannon's expansion, and why constants on the data inputs work

Take any Boolean function $F$ of some variables, pick one of them — call it $x$ — and
split its truth table into the half where $x = 0$ and the half where $x = 1$. Write
$F|_{x=0}$ for the function of the remaining variables you get by fixing $x$ at 0, and
$F|_{x=1}$ likewise. Then

$$F = x' \cdot F|_{x=0} + x \cdot F|_{x=1}$$

This is not deep and it is worth seeing why it is true. For any assignment of the
variables, $x$ is either 0 or 1. If it is 0, the second term vanishes and the first
reduces to $F|_{x=0}$, which is $F$ on that half of the table by definition. If it is 1,
the mirror image happens. There is no third case. The identity is exact, it holds for
every $F$, and it is called **Shannon's expansion**.

Look at what it says structurally: *any* function can be written as a 2-to-1 multiplexer
with $x$ on the select and two simpler functions on the data inputs. Apply it again to
each of those two, on a second variable, and you get a 4-to-1 multiplexer with two
select lines and four still-simpler functions. Keep going until every variable is on a
select line. What is left on the data inputs is a function of no variables at all —
which is a constant, 0 or 1.

That is the whole result, and it is worth stating in one line: **a $2^n$-to-1
multiplexer with its select lines driven by $n$ variables and its data inputs tied to
constants is an arbitrary function of those $n$ variables.** The constants, read in
order, are the output column of the truth table. There is no logic left to design.

## Worked example: a carry-out on an 8-to-1 multiplexer

Module 3's full adder had $C_{out} = AB + AC_{in} + BC_{in}$, the majority of three.
Drive an 8-to-1 multiplexer's select lines with $S_2S_1S_0 = A, B, C_{in}$ and work out
the eight constants by evaluating the function on each row.

```
  A B Cin |  AB  ACin  BCin |  Cout   ->  data input
  --------+-----------------+------
  0 0  0  |  0    0     0   |   0     ->  d0 = 0
  0 0  1  |  0    0     0   |   0     ->  d1 = 0
  0 1  0  |  0    0     0   |   0     ->  d2 = 0
  0 1  1  |  0    0     1   |   1     ->  d3 = 1
  1 0  0  |  0    0     0   |   0     ->  d4 = 0
  1 0  1  |  0    1     0   |   1     ->  d5 = 1
  1 1  0  |  1    0     0   |   1     ->  d6 = 1
  1 1  1  |  1    1     1   |   1     ->  d7 = 1
```

So the eight constants are `0 0 0 1 0 1 1 1`, and that string *is* the design. Confirm
one row against the block rather than against the algebra: with $A=1, B=0, C_{in}=1$ the
select is `101`, which is five, so the multiplexer copies $d_5$ to the output, and
$d_5 = 1$. The formula agrees: $AB + AC_{in} + BC_{in} = 0 + 1 + 0 = 1$.

## Worked example: the same function on a multiplexer half the size

Stop applying Shannon's expansion one variable early. Put only $A$ and $B$ on the select
lines of a 4-to-1 multiplexer and let each data input be whatever function of $C_{in}$ is
left over — which can be $0$, $1$, $C_{in}$ or $C_{in}'$, all of which you can wire
without a gate except the last, which needs one inverter shared by the whole block.

Fix $A$ and $B$ and simplify $C_{out} = AB + (A + B)C_{in}$ four times:

```
 A=0, B=0 :  Cout = 0 + (0+0)·Cin = 0            ->  d0 = 0
 A=0, B=1 :  Cout = 0 + (0+1)·Cin = Cin          ->  d1 = Cin
 A=1, B=0 :  Cout = 0 + (1+0)·Cin = Cin          ->  d2 = Cin
 A=1, B=1 :  Cout = 1 + (1+1)·Cin = 1            ->  d3 = 1
```

A 4-to-1 multiplexer with its data inputs wired to `0`, `Cin`, `Cin`, `1`. Half the
block, no extra gates, same function. Check the same row as before: $A=1, B=0$ selects
$d_2 = C_{in} = 1$, so the output is 1, which is what the eight-input version gave.

This halving is not a special property of the carry function. An $n$-variable function
always fits on a $2^{n-1}$-to-1 multiplexer, because the last variable's residues can
only be one of four things and three of them are free. It is how a multiplexer-based
design is done in practice, and it is why a datasheet for a 74151 8-to-1 advertises
itself as a "universal logic element" for four variables rather than three.

## Trees, because nobody builds a sixteen-input OR gate

The flat form of a 16-to-1 multiplexer is sixteen five-input AND gates feeding one
sixteen-input OR gate. Two levels, and both of them impossible: real libraries stop at
about four inputs per gate, for the same reason the decoder did.

The alternative is to build the whole thing out of one repeated cell. A 2-to-1
multiplexer is small, and a tree of them selects from any power of two:

```
 level 1 :  eight 2-to-1 muxes, all switched by S0     16 lines -> 8
 level 2 :  four  2-to-1 muxes, all switched by S1      8 lines -> 4
 level 3 :  two   2-to-1 muxes, all switched by S2      4 lines -> 2
 level 4 :  one   2-to-1 mux,   switched by S3          2 lines -> 1

 total cells: 8 + 4 + 2 + 1 = 15,  depth: 4 cells
```

Fifteen identical cells, four deep, and every gate in sight has two inputs. The trade is
the usual one: the flat version is shallower on paper and unbuildable in practice; the
tree is deeper and made of one part repeated. In CMOS the tree wins by more than the
gate count suggests, because a 2-to-1 multiplexer can be built from two transmission
gates — four transistors, plus one inverter on the select line that the whole level
shares — rather than from AND and OR gates at all.

## The lookup table, and why FPGAs stopped at six inputs

An FPGA's logic cell is this trick and nothing else: a $k$-to-1 multiplexer whose
$2^k$ data inputs come from $2^k$ configuration bits loaded at power-up. Choose the bits
and you have chosen the function. Nothing is rewired; the wiring was always the same.

The cost is exponential in $k$ and that is what fixes the size:

```
 k = 4   ->  16 configuration bits per cell
 k = 5   ->  32
 k = 6   ->  64
 k = 10  ->  1024
```

Doubling with each input, while the number of functions a cell can express grows as
$2^{2^k}$ — for $k = 6$ that is $2^{64}$, about $1.8 \times 10^{19}$ distinct functions
out of one cell. Vendors settled on 4 for years and then on 6, because past that the
table is mostly paying for functions nobody writes.

## The mistake people actually make

**Attaching the constants in the wrong order.** You have the output column `0 0 0 1 0 1
1 1` and eight data pins, and the column has to be applied starting at $d_0$ with the
row numbered by the select value. Write it down the pins the other way round, or swap
which variable you called $S_1$, and you have built a different function that looks
exactly as convincing.

It is tempting because both objects are a column of bits and neither carries a label.
The concrete version: implement $F = A'B$ on a 4-to-1 with $S_1 = A$ and $S_0 = B$.
$A'B$ is 1 only on row $AB = 01$, which is row 1, so $d_1 = 1$ and the rest are 0. Attach
the same column starting from $d_3$ instead and you get $d_2 = 1$, which is $AB'$ — the
right shape, the wrong function. Worse, the two agree on both rows where $A = B$, so
half of a lazily written test bench passes. Pin the order down before wiring anything:
the data input's *number* is the select's *value*.

**Expecting the multiplexer to combine.** "What if two data inputs are 1?" is a question
about a circuit that does not exist. One is selected; the others are ANDed with zero.

## Where the idea stops

**At the select transition.** The same glitch the decoder had. When $S$ changes, the
term that was carrying the output switches off and the new term switches on, and the two
events are not simultaneous. The output can dip through 0 in between even when both
data inputs are 1. Synchronous logic does not care; an asynchronous reset line fed from
a multiplexer output does.

**At the moment the multiplexer stops being made of gates.** Everything above assumed
logic levels. A real analogue multiplexer — a 4051 and its descendants, and the input
selector of every oscilloscope and data-acquisition card — is a set of CMOS switches,
and the abstraction leaks in three places at once.

The selected switch has an **on-resistance**, on the order of 100 Ω, in series with the
signal. The unselected switches have a finite off-resistance, so a DC voltage on an
unselected input leaks a little current into the output node. And the unselected
switches have a **capacitance across them**, a few picofarads, which is a path that gets
better as frequency rises. That last one is the one that bites. With $R_{on} = 100$ Ω
and $C_{off} = 5$ pF, the fraction of an unselected input's signal that reaches the
output is about $2\pi f R_{on} C_{off}$, which is 20 dB per decade of frequency:

```
 at 100 kHz  :  2pi x 1e5 x 100 x 5e-12 = 0.000314  =  0.031 %   (-70 dB)
 at   1 MHz  :  2pi x 1e6 x 100 x 5e-12 = 0.00314   =  0.31 %    (-50 dB)
 at  10 MHz  :  2pi x 1e7 x 100 x 5e-12 = 0.0314    =  3.1 %     (-30 dB)
```

A datasheet calls this the **off-isolation**, quotes it at one frequency, and expects
you to know it degrades. One of this module's numerical questions works out where the
crossing to 1 % lands.

**At very wide selects.** A 256-to-1 multiplexer is a tree eight cells deep, and its
delay is eight cell delays. Anything that needs to select from a large set at speed —
a register file, a cache way — stops using a single multiplexer and starts using a
decoder plus a wired-OR bus, which is the shape a memory array already has. Module 10
comes back to it.
''',
                },
                {
                    "title": "Backwards: encoders, priority, and knowing that nothing happened",
                    "minutes": 11,
                    "body": r'''
A decoder turns a number into a place. Run the arrow the other way and you have an
**encoder**: $2^n$ input lines of which one is supposed to be active, and $n$ outputs
that say which one it was.

The application to hold in mind is an interrupt controller. Eight devices, each with a
wire it can raise when it wants attention, and a processor with a three-bit register
that has to end up holding the number of the device to service. Or a keypad: sixteen
switches, four wires out. Or the output stage of a flash analogue-to-digital converter,
where a column of comparators produces a run of 1s up to the input voltage and something
has to turn that into a binary number.

## The plain encoder is an OR gate per output bit

Suppose exactly one input $I_j$ is active. Then output bit $Y_k$ should be the $k$-th bit
of $j$. So $Y_k$ is 1 for exactly those inputs whose number has bit $k$ set, and the
expression is an OR over that list:

$$Y_2 = I_4 + I_5 + I_6 + I_7 \qquad
  Y_1 = I_2 + I_3 + I_6 + I_7 \qquad
  Y_0 = I_1 + I_3 + I_5 + I_7$$

Three OR gates of four inputs each, and that is the entire 8-to-3 encoder. Two things
are worth noticing. $I_0$ appears in none of them, because zero has no bits set — the
input for device 0 can be left disconnected and the circuit still works. And the
structure is the exact transpose of the decoder: the decoder had one AND per output
listing all the inputs, the encoder has one OR per output listing the inputs that
mention it.

## Two failures, and both of them are silent

**Two inputs active at once.** The gates have no way to notice. Raise $I_3$ and $I_4$
together:

```
 code for 3 = 011
 code for 4 = 100
 OR them    = 111   ->  the output says seven
```

Seven is a device that was not asking for anything. Nothing anywhere in the circuit is
in an error state; three OR gates did what OR gates do. This is not an unlikely case
either — two devices wanting attention in the same microsecond is the normal condition
of a loaded system, and coping with it is exactly what the priority version below
exists for.

**No input active.** All the ORs give 0, so the output is `000`, which is
indistinguishable from device 0 asking. Every real encoder therefore carries an extra
output, usually called **valid**, which is simply the OR of everything:

$$V = I_0 + I_1 + \dots + I_7$$

`000` with $V = 1$ means device 0. `000` with $V = 0$ means nobody. One extra gate buys
back a distinction the encoding threw away, and leaving it out is how an idle bus ends up
being serviced as an interrupt from device 0 forever.

## Priority: define the answer instead of hoping

A **priority encoder** answers a different and better-posed question: *what is the
highest-numbered active input?* That question has an answer for every input pattern,
including patterns with several inputs active, which is why real parts are priority
encoders.

Write the table for four inputs with `x` meaning "do not care", one row per possible
answer, each row down the page naming a higher-priority input than the last:

```
 I3 I2 I1 I0 |  Y1 Y0   V
 ------------+-----------
  0  0  0  0 |   0  0   0
  0  0  0  1 |   0  0   1
  0  0  1  x |   0  1   1
  0  1  x  x |   1  0   1
  1  x  x  x |   1  1   1
```

Five rows cover all sixteen input patterns, because each row after the first pins one
input at 1, everything of higher priority at 0, and lets the rest do as they please:
$1 + 1 + 2 + 4 + 8 = 16$. Read the equations off the rows where each output is 1:

$$Y_1 = I_3 + I_2 \qquad Y_0 = I_3 + I_2'I_1 \qquad V = I_3 + I_2 + I_1 + I_0$$

$Y_1$ is 1 whenever the answer is 2 or 3, which is whenever $I_3$ or $I_2$ is active
— nothing below them can change it. $Y_0$ is 1 when the answer is 1 or 3: $I_3$ gives
3 outright, and $I_1$ gives 1 only if $I_2$ is quiet, hence the $I_2'$. The $I_3'$ that
you might expect in front of $I_2'I_1$ is not needed: if $I_3$ is active the first term
has already made $Y_0$ equal 1, which is the correct answer.

## Worked example: two inputs active, by the equations

Feed it $I_3I_2I_1I_0 = 0110$, so $I_2$ and $I_1$ are both asking.

```
 Y1 = I3 + I2      = 0 + 1        = 1
 Y0 = I3 + I2'·I1  = 0 + 0·1      = 0
 V  = 0 + 1 + 1 + 0                = 1

 Y1 Y0 = 10, which is two -> device 2, the higher of the two. V says the answer means something.
```

The $I_2'$ is what did the work: $I_1$ is genuinely active and was genuinely ignored.
Compare the plain encoder on the same input, which would give $Y_1Y_0 = 10 + 01 = 11$
and report device 3.

Try one more, $I_3I_2I_1I_0 = 1001$:

```
 Y1 = 1 + 0     = 1
 Y0 = 1 + 0·0   = 1
 V  = 1

 Y1 Y0 = 11 -> device 3.  I0 is active and irrelevant, which is the definition of priority.
```

## Eight inputs, and a chain that ripples

Extend to 8-to-3 and the same reasoning gives, for the top bit,

$$Y_2 = I_7 + I_6 + I_5 + I_4$$

— a plain OR, because every input from 4 upwards has bit 2 set and nothing below them
can override. The lower bits collect longer products:

$$Y_0 = I_7 + I_6'I_5 + I_6'I_4'I_3 + I_6'I_4'I_2'I_1$$

Each term needs the inputs above it to be quiet, so the products get longer as you go
down the list, and the obvious implementation is a chain: input $j$ is granted only if a
"nobody above me" signal has travelled down from the top. That is a ripple, with the
same shape as module 3's ripple-carry adder — delay proportional to the number of
inputs — and the same fix applies. Group the inputs in fours, work out per-group "any
active" signals in parallel, and combine the groups in a tree. A 64-input priority
encoder built as a tree is about $\log_2 64 = 6$ levels rather than 64.

## Worked example: what priority does not fix

Eight devices on one interrupt controller. Device 7 raises its line every 10 µs and its
handler takes 8 µs to run.

```
 duty of device 7   :  8 µs out of every 10 µs  =  80 % of the processor
 left for the rest  :  2 µs out of every 10 µs  =  20 %, shared by seven devices
```

The encoder is working perfectly. It reports 7 every time, because 7 is the
highest-numbered active input, which is what it promised. Device 0 may never be
serviced at all, and nothing in the hardware regards that as a fault. Static priority
converts a race into a queue, and a queue with a monopolist at the front is still a
starved queue.

That is why real interrupt controllers add machinery the encoder does not have: a
**mask** register so an over-eager device can be switched off, **rotating** priority so
the winner drops to the bottom of the order, and nesting rules so a high-priority
handler can itself be interrupted. All of it sits on top of a priority encoder; none of
it is inside one.

## The mistake people actually make

**Using a plain encoder because "two can never be active at once".** It is tempting
because in the intended use exactly one line is meant to be up, and the plain version is
three OR gates against several times that. The failure is silent and it points
at the wrong device — the encoder reports a number that no input asked for, and every
layer above it treats that number as gospel. If two inputs can ever coincide, and on
asynchronous inputs they always eventually can, the plain encoder is wrong.

**Reading `000` as device 0.** Without the valid output there is no difference between
"device 0 is asking" and "nothing is asking", and the second is the state a system is
in almost all the time.

**Assuming the highest number is the most urgent.** Priority is wired into the block by
position. Whether device 7 deserves to win is a question about the system, decided when
the board was laid out, and it is not adjustable afterwards without a mask register.

## Where it stops

**At asynchronous inputs.** The inputs of an interrupt controller arrive whenever the
devices feel like it, and they change while the encoder's output is being sampled. The
output can then be caught mid-transition, producing a code for a device that is not
asking — the encoder's version of the decoder's glitch, and worse, because the sampling
register can go metastable. The fix is a synchroniser on each input, which module 9
takes up properly.

**At the thermometer code, which is the case priority handles best.** In a flash ADC,
seven comparators for three bits produce a run of 1s from the bottom up to the input
level: `0001111` means the level is above four thresholds. A priority encoder converts
that directly, since the highest active line is the answer. And when one comparator gets
it wrong near its threshold — a **bubble** in the code, `0001011` — a priority encoder
degrades gracefully, reporting the highest 1 rather than the nonsense a plain encoder
would emit. That is not a coincidence; it is why the priority encoder is the standard
output stage of a flash converter.

**At sixty-four inputs and beyond,** where the ripple has to become a tree, and past
that, where the whole one-hot input bus becomes the thing you cannot afford. At that
point the arbitration moves into a protocol — a serial daisy chain, or a request-and-grant
handshake — and there is no encoder in it at all.
''',
                },
            ],
            "quiz": {
                "title": "Selecting, decoding and the blocks in between",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A 3-to-8 decoder is given the input `101`. What do its outputs do?",
                        "opts": [
                            "Output 5 goes active and the other seven do not",
                            "Outputs 1, 0 and 1 go active",
                            "Outputs 5, 1 and 0 go active",
                            "All eight outputs go active",
                        ],
                        "a": 0,
                        "why": (
                            "`101` is five, so output number 5 goes active on its own. That one-hot pattern is "
                            "the point of the block: the input is a number, the outputs are places, and the "
                            "decoder converts between the two. Reading `101` as a per-output instruction "
                            "confuses the three input wires with the eight output wires, which is the mistake "
                            "worth getting out of the way here."
                        ),
                    },
                    {
                        "q": "A 4-to-1 multiplexer has its select inputs at $S_1S_0 = 10$. Which data input reaches the output?",
                        "opts": ["$D_0$", "$D_1$", "$D_2$", "$D_3$"],
                        "a": 2,
                        "why": (
                            "$10$ in binary is two, so $D_2$ is copied to the output and the other three are "
                            "ignored entirely. $D_1$ would be selected by $01$ — the same two symbols the other "
                            "way round, and the reason the select lines are always labelled with their place "
                            "value rather than left to be guessed at."
                        ),
                    },
                    {
                        "q": "You want an arbitrary function of three variables, built from one multiplexer with the three variables driving its select lines. How many data inputs does it need, and what goes on them?",
                        "opts": [
                            "3 data inputs, one per variable",
                            "8 data inputs, tied to the constants 0 and 1 according to the truth table's output column",
                            "8 data inputs, driven by the three variables and their complements",
                            "16 data inputs, tied to constants",
                        ],
                        "a": 1,
                        "why": (
                            "Three select lines address $2^3 = 8$ data inputs, and each one is simply tied to "
                            "the output the truth table gives for that row. No gates at all: the eight "
                            "constants *are* the design. Feeding the variables back into the data inputs would "
                            "be building something else entirely, and 16 inputs is what four select lines "
                            "would need."
                        ),
                    },
                    {
                        "q": "Two inputs of a plain, non-priority 8-to-3 encoder go active at once — say inputs 3 and 4. What appears on the outputs?",
                        "opts": [
                            "The code for input 4, because it is the higher of the two",
                            "The code for input 3, because it is the lower of the two",
                            "`111`, which is the bitwise OR of `011` and `100` and names neither input",
                            "`000`, because the encoder detects the conflict and gives up",
                        ],
                        "a": 2,
                        "why": (
                            "A plain encoder is nothing but an OR of the codes of its active inputs, so `011` "
                            "and `100` together give `111` — which is seven, an input that was not active at "
                            "all. Nothing in the circuit notices; there is no conflict detection to do the "
                            "giving up. A priority encoder exists precisely so that the answer is defined: it "
                            "would report 4 here, and usually raises a separate \"something is active\" line "
                            "so that a genuine `000` can be told apart from nothing happening."
                        ),
                    },
                    {
                        "q": "A decoder's outputs are watched on a fast scope, and briefly show two outputs active together — a pattern no input value should ever produce. What is going on?",
                        "opts": [
                            "The decoder is faulty and should be replaced",
                            "One of its inputs is floating",
                            "Paths through the logic have different delays, so intermediate patterns appear for a few nanoseconds after each input change",
                            "The decoder's flip-flops have gone metastable",
                        ],
                        "a": 2,
                        "why": (
                            "The block is combinational — it has no flip-flops to go metastable — and it is "
                            "behaving correctly. An input change reaches different gates after different "
                            "delays, so on the way from one settled answer to the next the outputs pass "
                            "through patterns that correspond to no input at all. Synchronous design deals "
                            "with this by not looking: the outputs are sampled at a clock edge, after "
                            "everything has settled, and the glitch is never seen by anything that matters."
                        ),
                    },
                ],
            },
            "numeric": [
                {
                    "title": "One segment, one output",
                    "minutes": 6,
                    "brief": r'''
The bottom rung. A decoder output drives one segment of a display from a 3.3 V board:
the rail, a series resistor, and the LED, which the build modelled as a **fixed forward
drop** — a source that holds its own voltage and lets the resistor decide the current.
This one is a red LED, so the drop is 1.8 V rather than the 2 V of the build.

Nothing has to be rearranged. There is one resistor, and you know the voltage at both
ends of it.
''',
                    "prompt": "How much current flows through the segment?",
                    "note": "Give the answer in milliamps, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rs", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 100},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "led", "kind": "V", "x": 9, "y": 5, "rot": 1, "value": 1.8},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
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
                    "given": [
                        {"label": "Rail", "value": "3.30 V"},
                        {"label": "Series resistor", "value": "100 Ω"},
                        {"label": "LED forward drop", "value": "1.80 V"},
                    ],
                    "aside": "The probe sits on the LED's anode. Whatever the resistor is, that node is "
                             "held at the forward drop, so the resistor gets what is left of the rail.",
                    "answer": 15.0,
                    "tol": 0.2,
                    "unit": "mA",
                    "check": r'''
var r = c.net.parts.filter(function (p) { return p.kind === 'R'; })[0];
var d = c.dc();
return Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value * 1e3;
''',
                    "hint": "The resistor has the rail at one end and the LED's drop at the other, so it "
                            "carries $(3.3 - 1.8)/100$ amps.",
                    "wrong": "If you got 33 mA, the whole rail was dropped across the resistor and the LED "
                             "was left out. If you got 18 mA, the LED's own drop was divided by the "
                             "resistor instead of the difference.",
                    "why": "The LED holds its anode at 1.80 V, so the resistor sees $3.30 - 1.80 = 1.50$ V "
                           "across it and carries $1.50/100 = 15.0$ mA. Notice how sensitive that is to the "
                           "forward drop: the same resistor with a blue LED at 3.0 V would carry "
                           "$(3.3 - 3.0)/100 = 3$ mA, a fifth as much, from a part that looks identical on "
                           "a schematic. It is also why a bare LED across a rail with no resistor fails "
                           "immediately — with nothing to take the difference, the current is whatever the "
                           "supply can deliver.",
                },
                {
                    "title": "One decoder output, four cards to pull up",
                    "minutes": 9,
                    "brief": r'''
A select line generated by a decoder runs across a backplane to four cards. Each card
fits its own 6.8 kΩ **pull-down** resistor on the line, so that the input is at a
defined level during reset when nothing is driving it. Four cards, four pull-downs, all
on the same wire.

The decoder output is not an ideal source. When it drives HIGH it connects the line to
the 5 V rail through its own output resistance, drawn here as a 150 Ω resistor in
series.

A 5 V CMOS input reads anything above $V_{IH} = 3.5$ V as HIGH. The question is what the
line actually settles at, and the way in is to notice that the four pull-downs share a
pair of nodes.
''',
                    "prompt": "What voltage does the select line settle at when the decoder drives it HIGH?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "ron", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 150},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "rp1", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 6800},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
                            {"id": "rp2", "kind": "R", "x": 13, "y": 5, "rot": 1, "value": 6800},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 8},
                            {"id": "rp3", "kind": "R", "x": 17, "y": 5, "rot": 1, "value": 6800},
                            {"id": "g3", "kind": "GND", "x": 17, "y": 8},
                            {"id": "rp4", "kind": "R", "x": 21, "y": 5, "rot": 1, "value": 6800},
                            {"id": "g4", "kind": "GND", "x": 21, "y": 8},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [21, 3]},
                            {"a": [9, 3], "b": [9, 4]},
                            {"a": [9, 6], "b": [9, 8]},
                            {"a": [13, 3], "b": [13, 4]},
                            {"a": [13, 6], "b": [13, 8]},
                            {"a": [17, 3], "b": [17, 4]},
                            {"a": [17, 6], "b": [17, 8]},
                            {"a": [21, 3], "b": [21, 4]},
                            {"a": [21, 6], "b": [21, 8]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "Decoder output resistance", "value": "150 Ω"},
                        {"label": "Pull-down per card", "value": "6.8 kΩ"},
                        {"label": "Cards on the line", "value": "4"},
                        {"label": "Receiver threshold", "value": "V_IH = 3.5 V"},
                    ],
                    "aside": "Four equal resistors between the same two nodes are one resistor of a quarter "
                             "the value. After that it is a divider with 150 Ω on top.",
                    "answer": 4.59,
                    "tol": 0.02,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "$6800/4 = 1700$ Ω to ground, 150 Ω to the rail, so the line sits at "
                            "$5 \\times 1700/(150 + 1700)$.",
                    "wrong": "If you got 4.89 V, only one pull-down was counted. If you got 0.41 V, the "
                             "divider was taken the wrong way up — the line is connected to the rail "
                             "through the *small* resistance, so it must end up near the rail, not near "
                             "ground.",
                    "why": "The four pull-downs all run from the select line to ground, so they are in "
                           "parallel: $6800/4 = 1700$ Ω. That leaves a divider, 150 Ω from the rail and "
                           "1700 Ω to ground, so the line settles at "
                           "$5 \\times 1700/1850 = 4.59$ V — comfortably above the 3.5 V threshold. The "
                           "interesting part is what happens as cards are added. The level stays above "
                           "3.5 V until the parallel pull-down falls to 350 Ω, which takes nineteen cards. "
                           "But the current the output has to source is $5/(150 + R_p)$, which is 2.7 mA "
                           "here and passes a 74HC part's rated 4 mA at only seven cards. The **logic "
                           "level** is not what limits the fan-out on a DC-loaded line; the **output "
                           "current rating** is, and it bites first by a factor of nearly three.",
                },
                {
                    "title": "Three segments, one resistor, and the bill for sharing it",
                    "minutes": 12,
                    "brief": r'''
A tempting simplification, and a mistake that gets built. Instead of one series resistor
per segment, the designer puts a single 100 Ω resistor in the common leg where all the
segments join before they reach ground. One part instead of seven.

Three segments are lit. Each has its own small 68 Ω resistor and its own LED, modelled
as a 2 V forward drop as in the build, and all three LEDs return to the common node the
probe is sitting on. The shared 100 Ω runs from that node to ground.

Nothing here is a single divider. The common node's voltage depends on the total current,
and the total current depends on the common node's voltage, so you have to solve for one
of them. Then the question is not about a node at all: it asks what the shared resistor
is dissipating.
''',
                    "prompt": "How much power does the shared 100 Ω resistor dissipate?",
                    "note": "Give the answer in milliwatts, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "ra", "kind": "R", "x": 7, "y": 5, "rot": 1, "value": 68},
                            {"id": "da", "kind": "V", "x": 7, "y": 9, "rot": 1, "value": 2},
                            {"id": "rb", "kind": "R", "x": 13, "y": 5, "rot": 1, "value": 68},
                            {"id": "db", "kind": "V", "x": 13, "y": 9, "rot": 1, "value": 2},
                            {"id": "rc", "kind": "R", "x": 19, "y": 5, "rot": 1, "value": 68},
                            {"id": "dc", "kind": "V", "x": 19, "y": 9, "rot": 1, "value": 2},
                            {"id": "rs", "kind": "R", "x": 11, "y": 14, "rot": 1, "value": 100},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 17},
                            {"id": "out", "kind": "OUT", "x": 23, "y": 12},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [19, 3]},
                            {"a": [7, 3], "b": [7, 4]},
                            {"a": [7, 6], "b": [7, 8]},
                            {"a": [7, 10], "b": [7, 12]},
                            {"a": [13, 3], "b": [13, 4]},
                            {"a": [13, 6], "b": [13, 8]},
                            {"a": [13, 10], "b": [13, 12]},
                            {"a": [19, 3], "b": [19, 4]},
                            {"a": [19, 6], "b": [19, 8]},
                            {"a": [19, 10], "b": [19, 12]},
                            {"a": [7, 12], "b": [23, 12]},
                            {"a": [11, 12], "b": [11, 13]},
                            {"a": [11, 15], "b": [11, 17]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "5.00 V"},
                        {"label": "Per-segment resistor", "value": "68 Ω"},
                        {"label": "LED forward drop", "value": "2.00 V each"},
                        {"label": "Shared resistor", "value": "100 Ω"},
                        {"label": "Segments lit", "value": "3"},
                    ],
                    "aside": "Call the common node $V_c$. Each branch carries $(5 - 2 - V_c)/68$, the shared "
                             "resistor carries three of those, and $V_c$ is 100 Ω times that total. One "
                             "equation, one unknown.",
                    "answer": 59.8,
                    "tol": 0.6,
                    "unit": "mW",
                    "check": r'''
var rs = c.net.parts.filter(function (p) {
  return p.kind === 'R' && (p.n1 === 0 || p.n2 === 0);
})[0];
var d = c.dc();
var v = d.v[rs.n1] - d.v[rs.n2];
return v * v / rs.value * 1e3;
''',
                    "hint": "Write $V_c = 100 \\times 3(3 - V_c)/68$ and solve; then the power is "
                            "$V_c^2/100$.",
                    "wrong": "If you got 4.5 mW, that is one 68 Ω resistor rather than the shared one. If "
                             "you got about 1750 mW, the branches were treated as independent — each "
                             "carrying $3/68 = 44.1$ mA as though the shared resistor dropped nothing — "
                             "and 132 mA through 100 Ω is 1.75 W, which no 100 Ω resistor on a display "
                             "board is rated for.",
                    "why": "Each branch has 5 V at the top and $V_c + 2$ at the bottom of its resistor, so "
                           "it carries $(3 - V_c)/68$. Three of them meet at the common node, and that "
                           "total flows through the 100 Ω: $V_c = 300(3 - V_c)/68$, so "
                           "$68V_c = 900 - 300V_c$, $368V_c = 900$ and $V_c = 2.446$ V. Then "
                           "$P = V_c^2/100 = 2.446^2/100 = 59.8$ mW — more than the three 68 Ω resistors "
                           "burn between them, which is $3 \\times 4.5 = 13.6$ mW. Each segment is getting "
                           "$(3 - 2.446)/68 = 8.15$ mA. Now redo it for other numbers of segments. One "
                           "alone: $168V_c = 300$, $V_c = 1.786$ V, and it carries 17.9 mA. All seven: "
                           "$768V_c = 2100$, $V_c = 2.734$ V, and each gets 3.91 mA. A digit `1` lights "
                           "two segments at 11.2 mA each; a digit `8` lights seven at 3.91 mA each — "
                           "nearly three times dimmer — so the display visibly changes brightness as it "
                           "counts. That is the whole argument for one resistor per segment: seven cheap "
                           "parts buy a current that does not depend on what the other six are doing.",
                },
                {
                    "title": "The unselected input that gets through anyway",
                    "minutes": 14,
                    "brief": r'''
The last rung, and it leaves the digital abstraction behind on purpose.

An **analogue** multiplexer is not gates; it is a row of CMOS switches. The selected one
connects its input to the output through an on-resistance $R_{on}$ of about 100 Ω. The
unselected ones are open — but an open CMOS switch still has a few picofarads across it,
and a capacitor is a path that gets better as frequency rises.

Drawn here is the leakage path on its own, which is how the measurement is actually
made. The signal source is an **unselected** input carrying 1 V. It reaches the output
node through $C_{off} = 5$ pF. The output node is held near ground by the *selected*
channel, whose source is quiet and whose on-resistance is the 100 Ω to ground. The probe
reads what leaks through.

This is a high-pass: the fraction that gets through is

$$\frac{V_{out}}{V_{in}} = \frac{\omega R_{on} C_{off}}{\sqrt{1 + (\omega R_{on} C_{off})^2}}
\;\approx\; 2\pi f R_{on} C_{off} \quad \text{while it is small}$$

A datasheet quotes this as **off-isolation** and it degrades at 20 dB per decade. Find
where it reaches 1 % — that is 10 mV of crosstalk on a 1 V aggressor, and the point at
which the channel you did not select is no longer negligible.
''',
                    "prompt": "At what frequency does the unselected input's crosstalk reach 1 % of its own amplitude?",
                    "note": "Give the answer in megahertz, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "vin", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "coff", "kind": "C", "x": 6, "y": 3, "rot": 0, "value": 5e-12},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "ron", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 100},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
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
                    "given": [
                        {"label": "Aggressor on the unselected input", "value": "1.00 V"},
                        {"label": "Off-switch capacitance", "value": "C_off = 5 pF"},
                        {"label": "On-resistance of the selected channel", "value": "R_on = 100 Ω"},
                        {"label": "Crosstalk to find", "value": "1 % — 10 mV out"},
                    ],
                    "aside": "While the ratio is small the square root is very nearly 1, so "
                             "$2\\pi f R_{on} C_{off} = 0.01$ is accurate to a part in ten thousand. "
                             "Rearrange for $f$.",
                    "answer": 3.18,
                    "tol": 0.03,
                    "unit": "MHz",
                    # The crossing is found on the solver's own response rather than from the formula,
                    # so the answer is checked against the drawn C and R and not against the algebra
                    # that produced it. Bisection on a monotonically rising high-pass magnitude.
                    "check": r'''
var lo = 1e3, hi = 1e9;
for (var i = 0; i < 80; i++) {
  var mid = Math.sqrt(lo * hi);
  if (c.gain(mid) < 0.01) lo = mid; else hi = mid;
}
return Math.sqrt(lo * hi) / 1e6;
''',
                    "hint": "$f = 0.01/(2\\pi R_{on} C_{off})$, with $R_{on}C_{off} = 100 \\times "
                            "5\\,\\text{pF} = 500$ ps.",
                    "wrong": "If you got 318 MHz, the 1 % was left out and what was found is the corner "
                             "frequency $1/(2\\pi R C)$ itself — the point where the crosstalk is 71 %, far "
                             "past anything usable. If you got 31.8 MHz, the factor is 10 % rather than "
                             "1 %.",
                    "why": "$R_{on}C_{off} = 100 \\times 5 \\times 10^{-12} = 5 \\times 10^{-10}$ s. "
                           "Setting $2\\pi f R C = 0.01$ gives "
                           "$f = 0.01/(2\\pi \\times 5 \\times 10^{-10}) = 3.18$ MHz. Solving the exact "
                           "expression instead of the approximation moves it by 0.005 %, which is why the "
                           "approximation is the one anybody uses. Read the result as a design limit: this "
                           "part is fine for audio, where 20 kHz gives $2\\pi \\times 2\\times10^{4} \\times "
                           "5\\times10^{-10} = 6.3 \\times 10^{-5}$, or −84 dB of isolation, and it is "
                           "useless for video. Note also what would improve it. Halving $R_{on}$ doubles "
                           "the frequency, and $R_{on}$ is set by how large the switch transistor is — but "
                           "a larger transistor has a larger $C_{off}$, so the product barely moves. That "
                           "trade-off, $R_{on}C_{off}$ roughly constant for a given process, is the figure "
                           "of merit an analogue switch is actually sold on.",
                },
            ],
            "blanks": [
                {
                "title": "The multiplexer, and the same block used as a lookup table",
                "minutes": 9,
                "brief": r'''
Two readings of one block. The first is the expression its gates realise — a sum of
products in which each product carries one data line along with it. The second is
what happens when the data lines stop being signals and become constants, which is
the trick that an FPGA is built out of.

Nothing runs here; you are choosing symbols. The notation is module 2's: $S'$ for
NOT, juxtaposition for AND, $+$ for OR.
''',
                "caption": "a 4-to-1 multiplexer, twice",
                "lang": "text",
                "listing": r'''
A 4-to-1 multiplexer.  s1 and s0 name which of d0 d1 d2 d3 reaches y.

    y  =  ___ ___ d0   +   s1' s0 ___   +   s1 s0' d2   +   ___ s0 d3

The same block as a lookup table.  Drive the selects from the variables
a and b, tie the four data inputs to constants, and y becomes whatever
function of a and b those constants spell out.  Taking s1 = a, s0 = b:

    y = a' b     needs     d0 d1 d2 d3  =  ___
''',
                "blanks": [
                    {
                        "prompt": "The term that carries $d_0$ is the one that is true when the select names input 0.",
                        "opts": ["s1'", "s1", "s0", "d0'"],
                        "a": 0,
                        "why": (
                            "Input 0 is selected when $s_1s_0 = 00$, so both select variables have to be "
                            "complemented in this product. $s_1$ uncomplemented would be the condition for "
                            "selecting input 2 or 3."
                        ),
                    },
                    {
                        "prompt": "And the other half of that same condition.",
                        "opts": ["s0", "s0'", "s1'", "d0"],
                        "a": 1,
                        "why": (
                            "$s_0$ also has to be 0 for input 0, so it appears complemented. The product is "
                            "$s_1's_0'd_0$: it contributes $d_0$ when the select is 00, and contributes "
                            "nothing at all the rest of the time, which is what lets the four terms be ORed "
                            "together without interfering."
                        ),
                    },
                    {
                        "prompt": "$s_1's_0$ is the condition for which data input?",
                        "opts": ["d0", "d1", "d2", "d3"],
                        "a": 1,
                        "why": (
                            "$s_1s_0 = 01$ is one, so this term carries $d_1$. Reading the two literals as a "
                            "binary number — complemented means 0, plain means 1 — gives the input number "
                            "directly, and that is true of every row of a sum of products, not just this one."
                        ),
                    },
                    {
                        "prompt": "The last term carries $d_3$, so what is missing from its condition?",
                        "opts": ["s1'", "s0'", "s1", "d3'"],
                        "a": 2,
                        "why": (
                            "Input 3 is $s_1s_0 = 11$, so both literals are uncomplemented: $s_1s_0d_3$. This "
                            "is the term that distinguishes the block from an OR gate — take the select "
                            "conditions away and all four data lines would reach the output at once."
                        ),
                    },
                    {
                        "prompt": "$a'b$ is 1 on exactly one row. Which four constants put that function on the output?",
                        "opts": ["0 1 0 0", "0 0 1 0", "1 0 0 0", "0 0 0 1"],
                        "a": 0,
                        "why": (
                            "With $s_1 = a$ and $s_0 = b$, data input $k$ is selected by the row whose binary "
                            "value is $k$. $a'b$ is true only when $a=0, b=1$, which is row 1, so $d_1 = 1$ "
                            "and the other three are 0. Setting $d_2$ instead would give $ab'$ — the same "
                            "function with the variables swapped, and the reason the order the constants are "
                            "written in has to be pinned down before any of this means anything."
                        ),
                    },
                ],
                },
                {
                    "title": "A priority encoder, and the line that says nothing happened",
                    "minutes": 10,
                    "brief": r'''
The encoder runs the decoder backwards, and it has to decide what to do when two inputs
ask at once. A **priority** encoder decides by rank: report the highest-numbered active
input, and raise a separate **valid** line so that a code of `00` can be told apart from
nobody asking at all.

Below is the table for four inputs, with `x` for "do not care", and the equations that
fall out of it. Fill the gaps in both, then use the equations on one input pattern.

Nothing runs; you are choosing symbols. The notation is module 2's: $i'$ for NOT,
juxtaposition for AND, $+$ for OR.
''',
                    "caption": "five rows that cover all sixteen patterns",
                    "lang": "text",
                    "listing": r'''
A 4-to-2 priority encoder.  i3 outranks i2 outranks i1 outranks i0.

    i3 i2 i1 i0 |  y1  y0   v
    ------------+-------------
     0  0  0  0 |   0   0    0
     0  0  0  1 |   0   0    1
     0  0  1  x |   0   1    1
     0  1  x  x |  ___  0    1
     1  x  x  x |   1  ___   1

The equations those rows give:

    y1  =  i3 + ___
    y0  =  i3 + ___
    v   =  i3 + i2 + i1 + ___

Now run the equations on i3 i2 i1 i0 = 0 1 1 0.

    y1 y0  =  ___          and v = 1
''',
                    "blanks": [
                        {
                            "prompt": "Row `0 1 x x`: the highest active input is $i_2$, so the answer is two. What is $y_1$?",
                            "opts": ["0", "1"],
                            "a": 1,
                            "why": (
                                "Two is `10` in binary, so $y_1 = 1$ and $y_0 = 0$, which is what the row "
                                "already shows for $y_0$. The `x` entries on $i_1$ and $i_0$ are the whole "
                                "point of priority: whatever those two are doing, $i_2$ outranks them and "
                                "the answer does not move."
                            ),
                        },
                        {
                            "prompt": "Row `1 x x x`: the answer is three. What is $y_0$?",
                            "opts": ["0", "1"],
                            "a": 1,
                            "why": (
                                "Three is `11`, so both output bits are 1. This row covers eight of the "
                                "sixteen input patterns on its own — every pattern with $i_3$ up — which "
                                "is why five rows are enough for a four-input table."
                            ),
                        },
                        {
                            "prompt": "$y_1$ is 1 on the rows where the answer is 2 or 3. Which term completes it?",
                            "opts": ["i2", "i2'", "i2·i1", "i3'·i2"],
                            "a": 0,
                            "why": (
                                "The answer is 2 or 3 exactly when $i_3$ or $i_2$ is active, and nothing "
                                "below them can change that, so $y_1 = i_3 + i_2$ with no complements "
                                "anywhere. Writing $i_3'i_2$ instead is not wrong in value — the $i_3$ "
                                "term has already covered that case — but it is an extra gate that buys "
                                "nothing, and the top bit of a priority encoder really is a plain OR."
                            ),
                        },
                        {
                            "prompt": "$y_0$ is 1 when the answer is 1 or 3. $i_3$ handles the 3. What handles the 1?",
                            "opts": ["i1", "i2'·i1", "i2·i1", "i1'"],
                            "a": 1,
                            "why": (
                                "The answer is 1 only when $i_1$ is active **and** $i_2$ is not — if $i_2$ "
                                "were up the answer would be 2, whose low bit is 0. So the term is "
                                "$i_2'i_1$. A bare $i_1$ would report `11` for the input `0110`, which is "
                                "device 3 asking when it is not. Note there is no $i_3'$ in front: if "
                                "$i_3$ is active the first term has already set $y_0$ to 1, and 1 is the "
                                "right answer then anyway."
                            ),
                        },
                        {
                            "prompt": "The valid output is 1 whenever anything at all is asking. What completes it?",
                            "opts": ["i0", "i0'", "i1·i0", "1"],
                            "a": 0,
                            "why": (
                                "$v$ is the OR of every input, $i_0$ included. It is the one place $i_0$ "
                                "appears — it contributes to neither output bit, because zero has no bits "
                                "set — and without it the code `00` means either \"device 0\" or \"nobody\", "
                                "with no way to tell. Tying $v$ to the constant 1 would report an "
                                "interrupt on an idle bus forever."
                            ),
                        },
                        {
                            "prompt": "With $i_3i_2i_1i_0 = 0110$, evaluate $y_1 = i_3 + i_2$ and $y_0 = i_3 + i_2'i_1$.",
                            "opts": ["00", "01", "10", "11"],
                            "a": 2,
                            "why": (
                                "$y_1 = 0 + 1 = 1$ and $y_0 = 0 + 0 \\cdot 1 = 0$, so the output is `10` — "
                                "device 2, the higher of the two that are asking. `11` is what a plain "
                                "non-priority encoder would give here, ORing the codes `10` and `01` "
                                "together to name a device that is not asking at all. `01` would be "
                                "reporting $i_1$, which is real but outranked."
                            ),
                        },
                    ],
                },
            ],
            "derive": {
                "title": "What a wide decoder costs, and why nobody builds one flat",
                "minutes": 15,
                "vars": ["n", "F", "T"],
                "brief": r'''
A decoder takes $n$ address bits and drives one output per address. The flat design is
the canonical sum of products with the OR removed: one AND gate per output, each AND
taking all $n$ address literals.

The reading claimed that above about six address bits nobody builds it that way. This is
where that claim gets its number.

Count in **gate inputs**, the same measure module 3 used for a Karnaugh map — a
four-input AND costs 4, a two-input AND costs 2. The $n$ inverters that produce the
complemented literals are needed by every design here, so they cancel out of the
comparison and are left out throughout.

Write $F$ for the flat cost and $T$ for the two-level cost.
''',
                "steps": [
                    {
                        "prompt": "Start with the size of the problem. How many outputs does an $n$-input decoder have?",
                        "answer": "2^{n}",
                        "hint": "One output per address, and $n$ bits count from 0 up to $2^n - 1$.",
                        "deconstruct": [
                            "Each address bit doubles the number of distinct addresses.",
                            "So $n$ bits name $2^n$ of them, and the decoder needs one output for each.",
                        ],
                    },
                    {
                        "prompt": "Each of those outputs is one AND gate taking all $n$ literals. Write $F$, the flat design's total gate inputs, in terms of $n$.",
                        "answer": "n \\cdot 2^{n}",
                        "placeholder": "n \\cdot \\ldots",
                        "hint": "Number of gates times inputs per gate.",
                        "deconstruct": [
                            "There are $2^n$ AND gates, one per output.",
                            "Each has $n$ inputs, so the total is $n \\cdot 2^n$.",
                        ],
                    },
                    {
                        "prompt": "Now the two-level design. Split the address into two halves of $n/2$ bits and give each half its own small decoder. Write the gate inputs used by the two half-decoders together, in terms of $n$.",
                        "answer": "n \\cdot 2^{n/2}",
                        "placeholder": "n \\cdot \\ldots",
                        "hint": "Apply the previous step's formula to a decoder of $n/2$ inputs, then double it.",
                        "deconstruct": [
                            "One half-decoder has $n/2$ inputs, so by the previous step it costs $(n/2) \\cdot 2^{n/2}$ gate inputs.",
                            "There are two of them, and the 2 cancels the $1/2$: the pair costs $n \\cdot 2^{n/2}$.",
                        ],
                    },
                    {
                        "prompt": "Every output of the full decoder is one high-half line ANDed with one low-half line. Write the gate inputs used by that final AND layer, in terms of $n$.",
                        "answer": "2^{n+1}",
                        "hint": "There is one two-input AND per output, and you counted the outputs in the first step.",
                        "deconstruct": [
                            "Each half-decoder has $2^{n/2}$ outputs, and every pairing of one from each is a different address: $2^{n/2} \\cdot 2^{n/2} = 2^n$ gates.",
                            "Each takes 2 inputs, so the layer costs $2 \\cdot 2^n = 2^{n+1}$.",
                        ],
                    },
                    {
                        "prompt": "Add the two parts. Write $T$, the two-level total, in terms of $n$.",
                        "given": "half-decoders $n \\cdot 2^{n/2}$, final layer $2^{n+1}$",
                        "answer": "n \\cdot 2^{n/2} + 2^{n+1}",
                        "hint": "Nothing cancels; the two terms are simply added.",
                    },
                    {
                        "prompt": "Put $n = 8$ into the flat cost $F = n \\cdot 2^n$. Give the number of gate inputs.",
                        "answer": "2048",
                        "hint": "$2^8 = 256$ outputs, each an eight-input AND.",
                        "deconstruct": [
                            "$2^8 = 256$, so there are 256 gates.",
                            "$8 \\times 256 = 2048$ gate inputs — and every one of those gates is an eight-input AND, which no standard cell library actually offers.",
                        ],
                    },
                    {
                        "prompt": "Now $n = 8$ into the two-level cost. Give the number of gate inputs.",
                        "answer": "640",
                        "hint": "Two 4-to-16 decoders, then 256 two-input ANDs.",
                        "deconstruct": [
                            "The half-decoders: $8 \\times 2^4 = 8 \\times 16 = 128$ gate inputs, which is two 4-to-16 decoders of 64 each.",
                            "The final layer: $2^9 = 512$ gate inputs, being 256 two-input ANDs.",
                            "$128 + 512 = 640$, against 2048 — and now the widest gate anywhere is four inputs.",
                        ],
                    },
                    {
                        "prompt": "For large $n$ the $n \\cdot 2^{n/2}$ term is negligible beside $2^{n+1}$. Write what the ratio $F/T$ tends to, in terms of $n$.",
                        "answer": "n/2",
                        "hint": "Drop the small term from $T$ and cancel the powers of two.",
                        "deconstruct": [
                            "With the small term dropped, $F/T \\approx n \\cdot 2^n / 2^{n+1}$.",
                            "$2^n/2^{n+1} = 1/2$, so the ratio tends to $n/2$ — the saving grows without limit as the address widens.",
                        ],
                    },
                ],
                "closing": r'''
Check the trend against the two ends. At $n = 4$ the flat design costs 64 gate inputs
and the two-level one 48, a ratio of 1.33 where $n/2$ predicts 2 — the $n \cdot 2^{n/2}$
term is still doing real work at that size. At $n = 8$ it is 2048 against 640, a ratio
of 3.2 where $n/2$ predicts 4. At $n = 16$ the flat design needs
$16 \times 65536 = 1\,048\,576$ gate inputs and the two-level one
$16 \times 256 + 131\,072 = 135\,168$, a ratio of 7.8 against a prediction of 8. The
approximation is poor when it is not needed and good when it is.

Two things this does not say. It does not say the two-level decoder is faster: it has
one more gate on the path from address to output, so it is slightly *slower*, and what
it buys is that every gate in it is narrow. On real silicon that reverses the
conclusion, because a wide CMOS gate is slow in a way that a gate-input count cannot
see — an eight-input AND stacks eight transistors in series, and the delay grows worse
than linearly with the stack.

And it does not stop at two levels. A memory array is a two-level decoder taken
literally into the layout: the high half becomes a **row decoder** down one side, the
low half a **column decoder** along the bottom, and the "final AND" is not a gate at all
but the cell sitting where the two selected wires cross. That is why the array is square
— $2^{n/2}$ rows by $2^{n/2}$ columns is exactly the split this derivation chose, and it
is chosen for the same reason. Module 10 comes back to it with the sense amplifiers
attached.
''',
            },
            "build": {
                "title": "Making a decoder's output visible",
                "minutes": 22,
                "brief": r'''
A decoder output that nothing can see is hard to believe in, and a seven-segment
display is a row of seven of them driving seven LEDs. This is one segment.

An LED is not a resistor. Below about 1.8 V it barely conducts at all; above about
2.2 V it conducts hard. Over the range of currents anyone drives one at, it holds a
roughly **fixed forward drop**, and the useful first-order model is a **2 V source**
that does not care what current flows. Which means the LED does not set its own
current — a series resistor has to.

Build the branch a decoder output would switch:

* a 5 V supply, its negative terminal at ground
* one resistor from that supply to the LED
* a 2 V source from there down to ground, standing for the LED itself
* a probe on the node between the resistor and the LED

The segment driver is rated to source **20 mA**, and below about **8 mA** the segment
is too dim to read across a room. Land the current between the two. Note what
voltage the probe reads before you work out the resistor: whatever the resistor is,
the LED fixes that node, and the resistor gets whatever is left of the rail.
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
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 300},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3},
                        {"id": "p4", "kind": "V", "x": 9, "y": 5, "rot": 1, "value": 2},
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
                    {"name": "a 5 V supply, and exactly one resistor in the path", "code": r'''
c.assert(c.values('V').some(function (x) { return Math.abs(x - 5) < 0.005; }),
  'One supply at 5 V: that is the rail the segment driver switches on.');
c.assert(c.count('R') === 1,
  'Exactly one resistor. Two in series is electrically the same circuit with an extra part in it, ' +
  'and the brief asks for the single series resistor a display driver actually uses.');
'''},
                    {"name": "the LED, modelled as a 2 V drop, between the resistor and ground", "code": r'''
var vs = c.values('V');
c.assert(vs.length === 2,
  'Two sources: the 5 V rail, and a 2 V source standing for the LED. Found ' + vs.length + '.');
c.assert(vs.some(function (x) { return Math.abs(x - 2) < 0.005; }),
  'The LED is modelled as a fixed 2 V forward drop, so one of the two sources has to sit at 2 V.');
'''},
                    {"name": "the probe reads the LED's anode, not the rail", "code": r'''
c.close(c.vout(), 2.0, 0.02,
  'the node where the resistor meets the LED. This one is not yours to choose: the LED pins it at ' +
  'its forward drop, and the resistor is left with the other 3 V');
'''},
                    {"name": "between 8 mA and 20 mA through the segment", "code": r'''
var cur = c.dc().currents;
var mags = Object.keys(cur).map(function (k) { return Math.abs(cur[k]); });
c.assert(mags.length > 0, 'There is no supply current to measure — is the branch complete all the way to ground?');
var worst = Math.max.apply(null, mags);
c.assert(worst >= 8e-3 && worst <= 20e-3,
  'The segment is getting ' + c.fmt(worst, 'A') + '. Below 8 mA it is too dim to read across a room; ' +
  'above 20 mA the driver is out of its rating. The resistor has 5 - 2 = 3 V across it, so it sets ' +
  'the current on its own.');
'''},
                ],
                "hints": [
                    "Work out the voltage across the resistor first. The rail is 5 V and the LED holds 2 V, so the resistor has exactly 3 V across it whatever you choose it to be.",
                    "Ohm's law then fixes the current: $I = 3/R$. For 10 mA, $R = 3/0.01 = 300\\ \\Omega$.",
                    "The 2 V source goes from the probed node **down to ground**, with its positive terminal upwards — an LED conducts one way only, and this is the way round that lights it.",
                    "Anything from about 150 Ω to 375 Ω lands inside the 8-20 mA window. The value in a real display driver is usually the largest one that is still bright enough, because seven of these run at once.",
                ],
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "Negative numbers, and how a circuit subtracts",
            "summary": "One encoding makes the adder you already built do subtraction as well, and produces two different overflow flags because it cannot know which kind of number you meant.",
            "concepts": [
                "**Sign-and-magnitude** — steal the top bit for a sign and leave the rest alone — is the obvious idea and the wrong one. It has two zeros, and adding a positive to a negative needs a comparison and a subtraction rather than an addition, so the hardware needs a second block.",
                "**Two's complement** keeps place value and makes the top place negative. In four bits the places are $-8, 4, 2, 1$, so `1011` is $-8 + 2 + 1 = -5$. The range is $-2^{n-1}$ to $2^{n-1} - 1$: one more negative value than positive, because zero takes a slot on the positive side. Widening a value copies the top bit leftwards rather than padding with zeros — `1011` in eight bits is `11111011`, still $-5$.",
                "Negating is **invert every bit and add one**, which is not a rule to memorise. A number and its bitwise inverse have a 1 in every place between them, so $x + \\overline{x} = 2^n - 1$, and therefore $\\overline{x} + 1 = 2^n - x$ — exactly what $-x$ has to be when everything is kept modulo $2^n$.",
                "So $a - b = a + \\overline{b} + 1$: a subtractor is the module 3 adder with a row of inverters on one input and the carry-in tied to 1. One block does both operations, which is why an arithmetic unit contains one adder rather than two.",
                "**Overflow is not the carry-out.** The carry-out says the result did not fit *if the operands were unsigned*. Signed overflow is a different event — two positives making a negative, or two negatives making a positive — and the hardware spots it as the carry **into** the top bit differing from the carry **out** of it. Both flags come out of every addition, because the adder has no idea which kind of number you meant.",
            ],
            "read": [
                {
                    "title": "The place that is worth minus eight",
                    "minutes": 13,
                    "body": r'''
A four-bit register is four wires, and each wire sits at one of two voltages. That
gives sixteen patterns, and sixteen patterns is the entire supply. There is no
seventeenth pattern hiding anywhere, no spare pin that means "this one is negative",
no ink. Whatever negative numbers are going to be on this machine, they have to be
made out of sixteen patterns that already exist and already mean something.

So the question is not *how do we store a minus sign*. It is: **which patterns shall
we agree stand for negative numbers, and does the agreement leave the adder we already
built still working?** Two agreements are worth looking at. Only one of them survives
the second half of that question.

## The obvious idea, and where it breaks

Steal the top wire for a sign and leave the other three alone. `0101` is $+5$; `1101`
is $-5$ — the same three magnitude bits with a flag on top. This is
**sign-and-magnitude**, it is exactly how a number is written on paper, it takes four
seconds to explain, and everybody invents it first.

Now hand two of those patterns to the ripple adder from module 3, which knows nothing
about any of this and simply adds columns. Take $+5$ and $-3$:

```
   0101      +5
 + 1011      -3   (sign 1, magnitude 011)
   ----
   0000      what the adder produces
```

The answer should be $+2$. The adder gave zero, and it was not being stupid: it added
`0101` and `1011` as bit patterns, got `10000`, and dropped the carry off the top.
Nothing is wrong with the adder. The encoding is simply not the one the adder
implements.

To make sign-and-magnitude work you would compare the two magnitudes, subtract the
smaller from the larger, and give the result the sign of the larger. That is a
comparator, a subtractor and a multiplexer — a second arithmetic block, larger than
the adder itself, sitting beside it and used every time the two signs disagree.

And there are two zeros. `0000` and `1000` both mean nothing at all, so every test for
zero has to check for both, and two patterns out of sixteen are spent saying the same
thing. (Floating point kept sign-and-magnitude anyway and does have a $+0$ and a $-0$.
That is a considered trade in a format where the sign has to survive a magnitude that
has underflowed away; in an integer unit it is only a nuisance.)

## Start from the machine instead

Here is the physical fact the second agreement is built on. An $n$-bit adder is $n$
full adders in a row, and the carry out of the top one has nowhere to go, so it is
dropped. Not handled — dropped, off the end of the chip. Every sum an $n$-bit adder
computes is therefore taken **modulo $2^n$**, whether anybody intended that or not. A
four-bit adder is a sixteen-position ring, and on it $15 + 1 = 0$ without being asked.

An odometer does the same thing. Wind a five-digit one forward from 99999 and it reads
00000. Wind it *backwards* one click from 00000 and it reads 99999. Nobody engraved a
minus sign anywhere on it, and yet 99999 behaves exactly like $-1$: add one to it and
you get zero, which is the only thing $-1$ has ever been asked to do.

So stop looking for a pattern that *looks* negative, and look for one that *behaves*
negative:

> $-x$ is whichever pattern, added to $x$, gives zero.

In four bits: what added to `0001` gives `0000`? `1111`, because `1111 + 0001 = 10000`
and the leading 1 falls off the end. So `1111` is $-1$. What added to `0010` gives
`0000`? `1110`, so `1110` is $-2$. Keep walking down and the table fills itself in:

```
 pattern   unsigned   two's complement
  0000         0             0
  0001         1            +1
  0010         2            +2
  0011         3            +3
  0100         4            +4
  0101         5            +5
  0110         6            +6
  0111         7            +7
  1000         8            -8
  1001         9            -7
  1010        10            -6
  1011        11            -5
  1100        12            -4
  1101        13            -3
  1110        14            -2
  1111        15            -1
```

Nothing was decided there. The top half of that table is what the adder's wrap-around
was already doing; the encoding only agrees to read it that way.

## What that does to place value

Read the right-hand column against the middle one. For the top eight rows they are the
same. For the bottom eight, the signed value is the unsigned value minus 16.

Sixteen is $2^4$, and the only bit that is 1 on all of those rows and 0 on all the
others is the top one, whose unsigned place is worth 8. Subtracting 16 exactly when
that bit is set is the same statement as saying its place is worth $8 - 16 = -8$:

$$v = -8b_3 + 4b_2 + 2b_1 + 1b_0$$

One coefficient changed sign. That is the whole encoding. Place value is intact, the
base is still two, the columns still double from the right — two's complement is not a
new number system, it is the ordinary one with a minus sign painted on the leftmost
column. Every conversion habit from module 1 still works on the columns that were not
touched.

The range falls straight out. The most negative value takes the $-8$ and nothing else:
`1000` is $-8$. The most positive takes everything but: `0111` is $+7$. In general
$-2^{n-1}$ up to $2^{n-1} - 1$, which for eight bits is $-128$ to $+127$ and for
thirty-two is $-2\,147\,483\,648$ to $+2\,147\,483\,647$. There is one more negative
value than positive, because zero occupies a slot on the positive side of the fence.
That asymmetry is not a wart waiting to be fixed; it is what an even number of patterns
costs when the things to be represented — the negatives, zero, the positives — come to
an odd count.

## Worked example: reading `11010110`

Eight bits, so the places are $-128, 64, 32, 16, 8, 4, 2, 1$.

```
 bit      1     1    0    1    0    1    1    0
 place -128    64   32   16    8    4    2    1
 taken  -128  +64        +16       +4   +2
```

```
 -128 + 64 = -64
  -64 + 16 = -48
  -48 +  4 = -44
  -44 +  2 = -42
```

So `11010110` is $-42$. Check it the other way round: the same bits read as unsigned
are $128 + 64 + 16 + 4 + 2 = 214$, and $214 - 256 = -42$. The two routes have to agree,
because "subtract $2^n$ when the top bit is set" and "the top place is negative" are
one statement written twice.

Three landmarks worth keeping in your head. `01111111` has its top bit clear so it is
positive, and it comes to $64+32+16+8+4+2+1 = 127$, the largest signed byte.
`10000000` takes only the $-128$, so it is $-128$, the most negative. And `11111111`
is $-128 + 127 = -1$ — the all-ones pattern is $-1$ at every width, which is the same
fact the odometer showed.

## Worked example: writing $-100$ in eight bits

Two routes, and they had better agree.

**By subtraction.** The pattern for a negative $v$ is the unsigned number $v + 2^n$,
here $-100 + 256 = 156$. Write 156 in binary by taking places off the top:

```
 156 - 128 =  28      place 128 taken
  28 -  16 =  12      place  16 taken
  12 -   8 =   4      place   8 taken
   4 -   4 =   0      place   4 taken

 -> 1001 1100
```

**By invert-and-add-one.** Start from $+100$, which is `0110 0100` — check it,
$64 + 32 + 4 = 100$.

```
 +100        0110 0100
 invert      1001 1011
 add one     1001 1100
```

The same pattern. Read it back to be sure: $-128 + 16 + 8 + 4 = -100$. Good.

The second route is the one hardware uses, because inverting is a wire passed through
an inverter and adding one is a carry-in that was sitting there unused. *Why* it is
equivalent to the first route is the guided derivation later in this module, and it is
four lines long.

## Widening, and why zeros are the wrong padding

Start from $-13$ in eight bits. $+13$ is `0000 1101`; invert to `1111 0010`; add one
to get `1111 0011`. Read it back: $-128 + 64 + 32 + 16 + 2 + 1 = -13$.

Now copy that into a sixteen-bit register. The rule is to copy the top bit leftwards —
**sign extension** — giving `1111 1111 1111 0011`. Here is why that keeps the value.

Go one bit at a time. Widening from $n$ to $n+1$ bits does two things at once: the old
top column stops being worth $-2^{n-1}$ and becomes worth $+2^{n-1}$, and a brand new
top column worth $-2^n$ appears. If the old top bit was 1, its contribution changes
from $-2^{n-1}$ to $+2^{n-1}$, a gain of $2^n$; putting a 1 into the new top column
contributes $-2^n$; and the two cancel exactly. If the old top bit was 0, its column
contributed nothing before or after, and a copied 0 in the new column contributes
nothing either — so one rule covers both signs without a second case.

```
  1011  as 4 bits :  -8 + 2 + 1        = -5
 11011  as 5 bits : -16 + 8 + 2 + 1    = -5
```

Pad with zeros instead and `0000 0000 1111 0011` is $243$ — which is the correct
widening of those eight bits read as *unsigned*, and a bug the moment they were meant
to be negative. This is why a processor carries two different instructions for making
a narrow value wide, and why a compiler that has lost track of a variable's signedness
cannot choose between them.

## The mistake people actually make

**Reading the top bit as a flag and the rest as a magnitude.** `1011` gets read as
$-3$: sign 1, magnitude `011`. It is tempting for two reasons that are each partly
true. The bit really is called the sign bit, and it really is 1 for every negative
value and 0 for every non-negative one, so the name is not a lie — it is just not a
*place-value* statement. And sign-and-magnitude is what everyone invents first, so the
reading arrives as a habit before the encoding does.

One line settles it. Take `1111`. Sign-and-magnitude says $-7$; two's complement says
$-1$. Add `0001` to `1111` on any machine you can find and the answer is zero, and
zero is what you get by adding one to $-1$, not by adding one to $-7$.

**Negating by setting the top bit.** `0110` is $+6$; setting the top bit gives `1110`,
which is $-8 + 4 + 2 = -2$, not $-6$. That move belongs to the other encoding, the one
where the low bits go on meaning what they always meant.

**Stopping after the inversion.** Inverting maps $x$ to $-x-1$, so it lands one short
every single time: inverting $+6$ gives `1001`, which is $-7$. The $+1$ is not a fudge
factor bolted on to make the answer come out — it is there because $x + \overline{x}$
is the all-ones pattern, and the all-ones pattern is $-1$ rather than $0$.

## Where the encoding stops being enough

**At its own asymmetry.** `1000` in four bits is $-8$, and negating it gives $-8$
back: invert to `0111`, add one, and you are at `1000` again. So an absolute-value
routine has one input it cannot answer, and the most negative integer is a landmine in
anything that negates. In C, `-INT_MIN` is undefined behaviour rather than merely
wrong; in Java, `Math.abs(Integer.MIN_VALUE)` is specified to return
`Integer.MIN_VALUE`, which is negative. The habit of writing a sort comparator as
`return a - b;` has a hole in it for the neighbouring reason: the subtraction itself
can leave the range.

**At the boundary with unsigned.** The encoding says nothing about which reading a
pattern gets; the *instruction* pointed at it does. Mix the two readings in one
expression and the language has rules you probably did not read. The classic is a loop
guard like `for (int i = 0; i < strlen(s) - 1; i++)`: `strlen` returns an unsigned
type, so on an empty string `strlen(s) - 1` is not $-1$ but the largest value a
`size_t` holds, and the guard stays true for every `i` the loop will ever reach.
Nothing overflowed and no bit is wrong. The same pattern was simply read by the rule
for the other type — `i` is widened and converted to unsigned to make the comparison,
which is a conversion the source code never mentions.

**Where something else replaces it entirely.** Two's complement is the right answer
for a fixed width that wraps, and that is not every situation.

* Floating point uses sign-and-magnitude on purpose: negating costs one bit, and the
  format wants the sign to outlive a magnitude that has shrunk to zero.
* A binary exponent field is usually **excess-K**, also called offset binary: store
  $e + 127$ as an ordinary unsigned number. Its virtue is that the unsigned ordering of
  the stored patterns is the ordering of the values they stand for, which is what lets
  two floats be compared by an integer comparator.
* Converters do the same thing in copper. A bipolar digital-to-analogue converter is
  usually an offset-binary one with a fixed current pushed into its summing node to
  move zero — which is one resistor, and the last question in this module works out its
  value.

Offset binary and two's complement differ by **inverting the top bit and nothing
else**: adding $2^{n-1}$ modulo $2^n$ flips that column and leaves every other alone.
So a converter that wants one encoding and is handed the other is reconciled by a
single inverter, which is worth knowing before anyone reaches for a subtractor.
''',
                },
                {
                    "title": "Subtraction, and the two flags it sets",
                    "minutes": 14,
                    "body": r'''
An arithmetic unit contains one adder. Look at the floorplan of any processor and
there is a single ripple of full adders — or a single carry-lookahead tree, which is
that done faster — and no second block anywhere doing subtraction. That is not thrift
for its own sake. The adder is the largest and slowest thing on the datapath,
everything on the critical path is timed against it, and a second one would cost the
area twice and the verification twice over for an operation that turns out to be the
first one wearing a hat.

This half of the module is about the hat, and about the two flags that fall out of it
because the adder has no idea what you meant.

## One block, two operations

The identity is $a - b = a + \overline{b} + 1$, and proving it is the guided
derivation later in this module. Take it as given here and look at what it asks the
hardware for.

* $\overline{b}$ — every bit of $b$ inverted, which is $n$ inverters.
* $+1$ — the adder's carry-in, which during a plain addition sits at 0 doing nothing
  at all.

Both of those are free or nearly so, and the way to get them under control is one
wire. Call it `SUB`:

```
   b_i ---+
          XOR ----> the adder's B input for bit i
  SUB ----+

  SUB ------------> the adder's carry-in
```

An XOR gate with one input tied to a control line is a **controllable inverter**:
$b \oplus 0 = b$, and $b \oplus 1 = \overline{b}$. With `SUB = 0` the block computes
$a + b + 0$. With `SUB = 1` it computes $a + \overline{b} + 1$, which is $a - b$. One
XOR per bit, one wire, and an adder that was going to be there anyway.

That is the whole subtractor. There is no borrow chain, no second carry network, and
nothing running in the opposite direction. The chain that propagates a *carry* when
adding is propagating what a schoolbook subtraction would call *not a borrow* when
subtracting, on the same wires, at the same speed.

## Worked example: $5 - 7$ in four bits

$a = 5$ is `0101`, $b = 7$ is `0111`, and `SUB = 1`, so the adder is handed `0101`,
$\overline{b} = $ `1000`, and a carry-in of 1.

```
 column       3     2     1     0
 a            0     1     0     1
 ~b           1     0     0     0
 carry in     0     0     1     1    <- the 1 at column 0 is the SUB line
 --------------------------------
 sum          1     1     1     0
 carry out    0     0     0     1
```

Column by column from the right: $1+0+1 = 2$, so sum 0 and carry 1. Then $0+0+1 = 1$,
sum 1 and carry 0. Then $1+0+0 = 1$, sum 1 and carry 0. Then $0+1+0 = 1$, sum 1 and
carry 0.

The result is `1110`, which is $-8+4+2 = -2$, and $5 - 7$ is indeed $-2$.

Look at the two carries at the top column: the carry **into** it is 0 and the carry
**out** of it is 0. They agree, and the next section shows that this is the hardware's
way of saying the signed answer can be trusted.

The carry-out being 0 means something else again. For a subtraction it says a **borrow
happened** — read as unsigned, $5 - 7$ cannot be done in four bits at all. Both
readings are being reported at once, about the same operation, and they are saying
different things. That is the whole of the next section in one sentence.

(A caution that costs people an afternoon: x86 stores the *borrow* in its carry flag
after a subtraction, so `CF = 1` here, while ARM stores the *carry out*, so `C = 0`
here. Same wire, complemented in one of the two families. Neither is more correct, and
both have to be read with the manual open.)

## Worked example: one subtraction, right and wrong at the same time

$12 - 5$ in four bits. $a = $ `1100`, $b = $ `0101`, $\overline{b} = $ `1010`, carry-in
1.

```
 column       3     2     1     0
 a            1     1     0     0
 ~b           1     0     1     0
 carry in     0     0     0     1
 --------------------------------
 sum          0     1     1     1
 carry out    1     0     0     0
```

The result is `0111`.

Read every pattern as unsigned and the operation is perfect: $12 - 5 = 7$, `0111` is
7, and the carry-out of 1 says no borrow was needed.

Read every pattern as signed and the operation is wrong. `1100` is $-4$ and `0101` is
$+5$, so what was asked for was $-4 - 5 = -9$, which is outside the $-8$ to $+7$
range. The stored answer `0111` is $+7$, and $-9 + 16 = 7$ — the wrap, exactly. And
the top column reports it: the carry into it is 0, the carry out of it is 1, and they
differ.

One subtraction. Correct as unsigned, overflowed as signed, and the hardware announced
both without being told which you wanted.

## Two flags, because the adder does not know what you meant

Every addition sets both of these, always:

**C, the carry flag** — the carry out of the top column. It says: *read as unsigned,
the true answer did not fit.*

**V, the overflow flag** — set when the carry **into** the top column differs from the
carry **out** of it. It says: *read as signed, the true answer did not fit.*

Here is why the carry rule detects signed overflow, rather than merely correlating
with it. Write $a$, $b$ for the two top operand bits, $c$ for the carry into the top
column, $s$ for the sum bit it produces and $c_n$ for the carry it emits, so that
$a + b + c = 2c_n + s$ by the definition of a full adder. Everything below the top
column is identical under both readings, so let $L$ be the value the stored lower bits
carry; the *true* value of the lower half is then $2^{n-1}c + L$, because the carry it
handed upwards is worth $2^{n-1}$.

```
 true sum      = -2^(n-1)(a + b) + 2^(n-1)c + L     top bits weigh -2^(n-1)
 stored result = -2^(n-1)s                    + L

 difference    = 2^(n-1)( c - a - b + s )
               = 2^(n-1)( c - a - b + (a + b + c - 2c_n) )
               = 2^(n-1)( 2c - 2c_n )
               = 2^n ( c - c_n )
```

The stored result differs from the truth by $2^n(c - c_n)$ — zero exactly when the two
carries are equal, and one whole wrap of $\pm 2^n$ when they are not. The rule is an
identity, not a heuristic, and as a bonus it names the size of the error it detects.

There is an equivalent test that is easier to run by eye: **V is set when the two
operands have the same sign and the result comes back with the other one.** Adding a
positive to a negative can never overflow, because the answer's magnitude is no bigger
than the larger operand's, and that one already fitted.

## Four additions, and all four combinations

Four-bit, and between them these cover every pairing of the two flags.

```
                        carry   carry
  a      b      sum     in top   out    C  V    as signed          as unsigned
 ----   ----   ----     ------  -----   -  -    ---------------    ----------------
 0011   0100   0111        0      0     0  0    +3 +4 = +7  ok      3 +  4 =  7  ok
 0110   0101   1011        1      0     0  1    +6 +5 = -5  BAD     6 +  5 = 11  ok
 1010   1011   0101        0      1     1  1    -6 -5 = +5  BAD    10 + 11 = 21 BAD
 0111   1001   0000        1      1     1  0    +7 -7 =  0  ok      7 +  9 = 16 BAD
```

Read the last two columns against the two flags and the correspondence is exact: **V
flags the signed column, C flags the unsigned column, and neither says anything
whatever about the other.** Only the third row sets both.

The fourth row is the one that kills the commonest intuition. The signed answer is
exactly right — $+7$ and $-7$ really do make zero — and the carry flag is 1. The
second row kills the other intuition, the one that says overflow ought to mean a carry
came out: $6 + 5$ overflows as a signed sum with a carry-out of 0, because the 1 that
the top column generated went *into* it and never came out.

## Worked example: one comparison, two right answers

A comparison instruction is a subtraction whose result is thrown away and whose flags
are kept. Take two bytes, $a = $ `0x50` and $b = $ `0xB0`, and compute $a - b$.

$\overline{b}$ is `0x4F`, so the adder is computing `0x50 + 0x4F + 1`:

```
 bit         7    6    5    4    3    2    1    0
 a           0    1    0    1    0    0    0    0
 ~b          0    1    0    0    1    1    1    1
 carry in    1    0    1    1    1    1    1    1
 -----------------------------------------------
 sum         1    0    1    0    0    0    0    0
 carry out   0    1    0    1    1    1    1    1
```

The result is `1010 0000`, which is `0xA0`. Now read it twice.

**As unsigned.** $a = 80$, $b = 176$, and $80 - 176$ needs a borrow. The carry out of
the top column is 0, which for a subtraction means exactly that, so the machine
reports *below* — correct, 80 is less than 176.

**As signed.** $a = +80$, and $b$ is $-128 + 32 + 16 = -80$, so the true answer is
$80 - (-80) = 160$, which does not fit in a signed byte. The flags say so: the carry
into the top column is 1 and the carry out is 0, so $V = 1$. The result's top bit is 1,
so $N = 1$. The signed less-than test is *$N$ differs from $V$*, and here they agree,
so the machine reports $a \geq b$ — correct, $+80$ is greater than $-80$, even though
the subtraction that decided it overflowed on the way.

Sixteen bits of input, one subtraction, two different answers and both of them right.
Nothing in the arithmetic separated them; the only difference was which flags the
branch instruction afterwards chose to look at. This is why every instruction set
carries two families of conditional branch — `JB`/`JAE` against `JL`/`JGE` on x86,
`BLO`/`BHS` against `BLT`/`BGE` on ARM — and why reaching for the wrong family is a
bug that survives every test in which the numbers happened to be small.

## The mistake people actually make

**Using the carry flag to detect signed overflow.** It is tempting because for
unsigned numbers the carry genuinely *is* the overflow, and most people carry one idea
called "it did not fit" rather than two. The fourth row of the table above is the
counterexample worth memorising: $7 + (-7) = 0$, the answer is exactly right, and
$C = 1$.

**Checking for overflow after the fact in C.** Writing `if (a + b < 0)` to catch a
positive overflow looks reasonable and is not merely unreliable: signed overflow is
undefined behaviour, so the compiler is entitled to assume `a + b` did not overflow, in
which case the test is provably false and it is within its rights to delete it. The
check has to be made on the operands before the addition, or through a builtin such as
`__builtin_add_overflow`, which compiles down to reading the flag the hardware had
already set and thrown away.

**Assuming the carry flag after a subtract means the same thing everywhere.** It does
not, as noted above. It is the one place in this material where two vendors made
opposite and equally defensible choices, and no amount of reasoning from first
principles will tell you which one is in front of you.

## Where wrapping stops being what you want

**Saturating arithmetic.** In an audio or image pipeline a wrap is far worse than a
clamp: an 8-bit pixel at 250, brightened by 10, becomes 4, and a highlight turns into a
black hole. Saturating instructions clamp to the end of the range instead — 255, or
$+127$ and $-128$ signed. The hardware is the same adder, with the overflow flag
driving a multiplexer that substitutes the rail for the wrapped answer. Wrapping is the
*default*, not a law of nature, and a DSP defaults the other way.

**Multiplication.** Two $n$-bit values make a $2n$-bit product, so a multiplier does
not have the adder's tidy property of taking $n$ bits in and giving $n$ bits back. The
low $n$ bits of the product are the same whether the operands were read as signed or
unsigned — the two readings of an operand differ by a multiple of $2^n$, so the
products differ by a multiple of $2^n$, which is invisible in the bottom half. The top
$n$ bits are not the same, and that is precisely why processors carry both a `MUL` and
an `IMUL`.

**Division, and the shift that is not division.** An arithmetic right shift copies the
sign bit in at the top, and it divides by two rounding towards *minus infinity*. C's
`/` rounds towards *zero*. For $-7$ in eight bits:

```
 -7           1111 1001
 -7 >> 1      1111 1100    = -4      floor(-3.5)
 -7 / 2                    = -3      truncated towards zero
```

They agree on every positive value and disagree on every negative odd one, so a
compiler cannot simply turn `x / 2` into `x >> 1` for a signed `x`. What it emits
instead is a conditional correction — add 1 first when `x` is negative, then shift.
For $-7$ that is $(-7 + 1) \gg 1 = -6 \gg 1 = -3$, which is the answer `/` is required
to give.

**At an unbounded width.** Once the number of bits is allowed to grow — a bignum
library, Python's own integers — there is no $2^n$ to wrap around and the entire
mechanism has nothing to stand on. Those libraries go back to sign-and-magnitude: a
sign field beside an array of digits. Two zeros are cheap when zero is one special case
in software, and the modulus that made two's complement work was only ever available
because the hardware had a fixed width off the end of which the carry could be lost.
''',
                },
            ],
            "quiz": {
                "title": "Reading, negating and overflowing",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is `1011` as a 4-bit two's complement number?",
                        "opts": ["$-5$", "$-3$", "$-11$", "$11$"],
                        "a": 0,
                        "why": (
                            "The places are $-8, 4, 2, 1$, and the digits select $-8$, nothing, 2 and 1, so the "
                            "value is $-5$. $-3$ is `1101`. The same bits read as unsigned really are 11, and "
                            "that is the point worth taking away: the circuit stores a pattern and nothing "
                            "else. Which of the two numbers it stands for is decided by the instruction you "
                            "point at it, not by the bits."
                        ),
                    },
                    {
                        "q": "What range of values does an 8-bit two's complement number cover?",
                        "opts": ["$-127$ to $+127$", "$-128$ to $+127$", "$-127$ to $+128$", "$0$ to $255$"],
                        "a": 1,
                        "why": (
                            "The top place is worth $-128$, and the remaining seven places can add back up to "
                            "$+127$, so the range runs from $-128$ to $+127$ — one more negative value than "
                            "positive, because zero occupies a slot on the positive side. A symmetric range is "
                            "what sign-and-magnitude gives, at the cost of having two patterns that both mean "
                            "zero. $0$ to $255$ is the same eight bits read as unsigned."
                        ),
                    },
                    {
                        "q": "Which operation turns the 4-bit pattern for $+6$ into the pattern for $-6$?",
                        "opts": [
                            "Set the top bit",
                            "Invert every bit",
                            "Invert every bit, then add one",
                            "Add one, then invert every bit",
                        ],
                        "a": 2,
                        "why": (
                            "$+6$ is `0110`; inverting gives `1001`, which is $-7$; adding one gives `1010`, "
                            "which is $-8 + 2 = -6$. Stopping after the inversion always leaves you one too "
                            "low, because inverting maps $x$ to $-x-1$. Setting the top bit gives `1110`, which "
                            "is $-2$ — that move belongs to sign-and-magnitude, where the other bits keep "
                            "meaning what they meant."
                        ),
                    },
                    {
                        "q": "A 4-bit adder is given `0110` and `0101`, and the operands are meant as signed. What has gone wrong?",
                        "opts": [
                            "Nothing: `1011` is the correct answer",
                            "Two positive numbers have produced a negative one — the true answer needs a fifth bit and there is not one",
                            "The carry-out is 1, so the answer is one too small",
                            "The sum is right but its sign bit has to be inverted before it is read",
                        ],
                        "a": 1,
                        "why": (
                            "$6 + 5 = 11$, which is outside the $-8$ to $+7$ range, and the adder produces "
                            "`1011` — which reads as $-5$. The carry-out here is **0**, and that is exactly why "
                            "the carry flag is not the signed-overflow flag: the hardware detects this case as "
                            "the carry into the top bit being 1 while the carry out of it is 0. Read the same "
                            "two patterns as unsigned and 11 is the right answer, with nothing wrong at all."
                        ),
                    },
                    {
                        "q": "The 8-bit signed value `11110011` is copied into a 16-bit register. What goes in the top eight bits?",
                        "opts": [
                            "Zeros",
                            "Copies of the bottom bit",
                            "Ones",
                            "Whatever the register held before",
                        ],
                        "a": 2,
                        "why": (
                            "`11110011` is $-13$, and the widened pattern has to be $-13$ as well. Copying the "
                            "sign bit leftwards gives `11111111 11110011`, which still is: each extra leading "
                            "1 doubles a negative place value and adds back the place below it, and the two "
                            "cancel. Padding with zeros gives $243$ instead — the correct widening of the same "
                            "bits read as unsigned, and a bug the moment the value was meant to be negative."
                        ),
                    },
                ],
            },
            "numeric": [
                {
                    "title": "One bit set, and it is the negative one",
                    "minutes": 6,
                    "brief": r'''
The bottom rung. This is the build's circuit with a different pattern standing on it.

Two bits read as a two's complement number, turned back into a voltage. Each bit's
resistor is tied to the output of the flip-flop holding that bit, and each resistor's
*conductance* is proportional to the magnitude of its place — so the ones bit gets
twice the resistance of the twos bit. The single thing that makes this signed rather
than unsigned is where the top bit's driver goes when it is HIGH: to $-5$ V, because
its place is worth $-2$ and not $+2$.

The pattern here is `10`, which in two's complement is $-2 + 0 = -2$. The sign bit is
HIGH so its driver sits at $-5$ V; the ones bit is LOW so its driver sits at 0 V. The
schematic is what is left once each driver is replaced by the rail it is holding.

Nothing has to be rearranged. Two resistors, and you know the voltage at the far end
of each.
''',
                    "prompt": "What voltage does the shared node settle at?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "vneg", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": -5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rs", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "r1", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 20000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
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
                    "given": [
                        {"label": "Pattern on the wires", "value": "10 — which is -2"},
                        {"label": "Sign bit, worth -2", "value": "10 kΩ to its driver, which is at -5 V"},
                        {"label": "Ones bit, worth +1", "value": "20 kΩ to its driver, which is at 0 V"},
                    ],
                    "aside": "Two resistors in series between $-5$ V and 0 V, with the probe where they "
                             "meet. The node lands nearer the end it is closer to in resistance.",
                    "answer": -3.33,
                    "tol": 0.02,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "It is an ordinary divider between $-5$ V and ground: the node sits at "
                            "$-5 \\times 20/(10 + 20)$.",
                    "wrong": "If you got $-1.67$ V, the two resistors were swapped and the sign bit was "
                             "given the larger one — but the sign bit is worth twice as much, so it has "
                             "to pull twice as hard, which means half the resistance. If you got $-5$ V, "
                             "the ones bit's resistor was left out; a LOW bit is not a disconnected bit, "
                             "it is a bit whose driver is holding 0 V.",
                    "why": "The 20 kΩ runs to 0 V and the 10 kΩ to $-5$ V, so the node sits at "
                           "$-5 \\times 20/30 = -3.33$ V. Read it as place value instead and you get the "
                           "same number with more meaning: the two conductances add to three units, so "
                           "one unit of value is worth $5/3 = 1.67$ V, and the pattern is $-2$ units. "
                           "That scale covers the whole code: `00` gives 0 V, `01` gives $+1.67$ V, `10` "
                           "gives $-3.33$ V and `11` gives $-1.67$ V. Two things about that list are "
                           "awkward, and they are separate problems. Half the outputs are below ground, "
                           "so whatever reads this node needs a negative supply of its own. And run the "
                           "four patterns in the order a counter produces them — 0, up, hard down, up — "
                           "and the output is not monotonic in the pattern, because the code is not "
                           "monotonic when its patterns are read as unsigned numbers. The last question "
                           "in this module cures the first problem with one resistor. Curing the second "
                           "costs an inverter, and the two fixes are unrelated.",
                },
                {
                    "title": "Three places, and the one that pulls the other way",
                    "minutes": 8,
                    "brief": r'''
The same idea one bit wider. Three bits, so the places are $-4$, $+2$ and $+1$, and
the conductances have to be in the ratio $4 : 2 : 1$ — which is 10 kΩ, 20 kΩ and
40 kΩ.

The pattern is `101`. The sign bit is HIGH, so its driver is at $-5$ V. The twos bit
is LOW, so its driver is holding 0 V. The ones bit is HIGH, so its driver is at
$+5$ V. Three branches now meet at the node instead of two, and one of them is pulling
against the other.

There is no divider here to read off. Every branch is a known voltage behind a known
resistance, which is the situation the conductance-weighted average was invented for.
''',
                    "prompt": "What voltage does the shared node settle at?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "vneg", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": -5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r4", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "r2", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 20000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
                            {"id": "r1", "kind": "R", "x": 15, "y": 5, "rot": 1, "value": 40000},
                            {"id": "vpos", "kind": "V", "x": 15, "y": 9, "rot": 1, "value": 5},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 12},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [15, 3]},
                            {"a": [9, 3], "b": [9, 4]},
                            {"a": [9, 6], "b": [9, 8]},
                            {"a": [15, 3], "b": [15, 4]},
                            {"a": [15, 6], "b": [15, 8]},
                            {"a": [15, 10], "b": [15, 12]},
                        ],
                    },
                    "given": [
                        {"label": "Pattern on the wires", "value": "101 — which is -4 + 1 = -3"},
                        {"label": "Sign bit, worth -4", "value": "10 kΩ to -5 V (HIGH)"},
                        {"label": "Twos bit, worth +2", "value": "20 kΩ to 0 V (LOW)"},
                        {"label": "Ones bit, worth +1", "value": "40 kΩ to +5 V (HIGH)"},
                    ],
                    "aside": "Add up the currents each branch would push into the node if the node were "
                             "at 0 V, then divide by the total conductance. Equivalently: the node is the "
                             "average of the three driver voltages, weighted by $1/R$.",
                    "answer": -2.14,
                    "tol": 0.02,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "$V = (-5/10\\text{k} + 0/20\\text{k} + 5/40\\text{k}) \\div "
                            "(1/10\\text{k} + 1/20\\text{k} + 1/40\\text{k})$.",
                    "wrong": "If you got $+3.57$ V, the pattern was read as the unsigned 5 with every "
                             "branch tied to the positive rail — that is what this network gives before "
                             "the sign bit's driver is moved to $-5$ V. If you got $-3.00$ V, the LOW "
                             "bit's branch was treated as disconnected; a LOW driver is a low-impedance "
                             "path to 0 V and not an open circuit, and leaving it out changes the "
                             "denominator as well as the numerator.",
                    "why": "In current: the sign branch offers $-5/10\\text{k} = -0.500$ mA, the twos "
                           "branch $0/20\\text{k} = 0$, and the ones branch "
                           "$5/40\\text{k} = +0.125$ mA, for $-0.375$ mA in total. The conductances add "
                           "to $0.100 + 0.050 + 0.025 = 0.175$ mS, so the node sits at "
                           "$-0.375/0.175 = -2.14$ V. As place value: the conductances are 4, 2 and 1 "
                           "units and they add to 7, so one unit of value is $5/7 = 0.714$ V, and the "
                           "pattern is $-3$ units, giving $-2.14$ V. That $2^n - 1$ in the denominator "
                           "is the same one module 1 found for the unsigned network — three bits share "
                           "the rail seven ways whichever encoding is written on them, and the only "
                           "thing the sign changes is which rail the top branch is tied to. Notice what "
                           "that costs as $n$ grows: the step between adjacent codes is "
                           "$5/(2^n - 1)$ volts, which for a twelve-bit converter is 1.2 mV, and the "
                           "largest resistor is $2^{n-1}$ times the smallest. Both of those are why "
                           "nobody builds a wide converter this way and why the R-2R ladder in module 1 "
                           "exists.",
                },
                {
                    "title": "What the negative rail is asked to supply",
                    "minutes": 9,
                    "brief": r'''
Four bits now: the places are $-8$, $+4$, $+2$, $+1$, and the resistors are 10 kΩ,
20 kΩ, 40 kΩ and 80 kΩ. The pattern is `1101`, which is $-8 + 4 + 1 = -3$, so three of
the four drivers are HIGH — one of them into the negative rail, two into the positive
one — and the $+2$ place is LOW and holding 0 V.

The question is not about the node this time. The negative supply has to source the
current that the sign bit's branch carries, and a bench supply, a charge pump or a
regulator all have a limit on that. Sizing it means knowing the number.

So: solve the node first, then look at the one resistor.
''',
                    "prompt": "How much current flows in the sign bit's 10 kΩ resistor?",
                    "note": "Give the answer in milliamps, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "vneg", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": -5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r8", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "r4", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 20000},
                            {"id": "vp1", "kind": "V", "x": 9, "y": 9, "rot": 1, "value": 5},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 12},
                            {"id": "r2", "kind": "R", "x": 15, "y": 5, "rot": 1, "value": 40000},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 8},
                            {"id": "r1", "kind": "R", "x": 21, "y": 5, "rot": 1, "value": 80000},
                            {"id": "vp2", "kind": "V", "x": 21, "y": 9, "rot": 1, "value": 5},
                            {"id": "g3", "kind": "GND", "x": 21, "y": 12},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [21, 3]},
                            {"a": [9, 3], "b": [9, 4]},
                            {"a": [9, 6], "b": [9, 8]},
                            {"a": [9, 10], "b": [9, 12]},
                            {"a": [15, 3], "b": [15, 4]},
                            {"a": [15, 6], "b": [15, 8]},
                            {"a": [21, 3], "b": [21, 4]},
                            {"a": [21, 6], "b": [21, 8]},
                            {"a": [21, 10], "b": [21, 12]},
                        ],
                    },
                    "given": [
                        {"label": "Pattern on the wires", "value": "1101 — which is -8 + 4 + 1 = -3"},
                        {"label": "Sign bit, worth -8", "value": "10 kΩ to -5 V (HIGH)"},
                        {"label": "Fours bit, worth +4", "value": "20 kΩ to +5 V (HIGH)"},
                        {"label": "Twos bit, worth +2", "value": "40 kΩ to 0 V (LOW)"},
                        {"label": "Ones bit, worth +1", "value": "80 kΩ to +5 V (HIGH)"},
                    ],
                    "aside": "Four conductances in the ratio 8:4:2:1 add to 15 units, so one unit of "
                             "value is $5/15$ of a volt. Get the node from that, then the resistor has a "
                             "known voltage at each end.",
                    "answer": 0.40,
                    "tol": 0.005,
                    "unit": "mA",
                    "check": r'''
var vneg = c.net.parts.filter(function (p) { return p.kind === 'V' && p.value < 0; })[0];
return Math.abs(c.dc().currents[vneg.id]) * 1e3;
''',
                    "hint": "The node is $5 \\times (-3)/15 = -1.00$ V. The sign resistor has $-5$ V on "
                            "one side of it and that on the other.",
                    "wrong": "If you got 0.50 mA, the node was taken as 0 V — which would be right only "
                             "if the other three branches were not there at all. If you got 0.60 mA, the "
                             "node's sign was dropped and $-5$ to $+1$ was used instead of $-5$ to $-1$.",
                    "why": "One unit of value is worth $5/15 = 0.333$ V, and the pattern is $-3$, so the "
                           "node sits at $-1.00$ V. The sign resistor then has $-5$ V at the rail end "
                           "and $-1$ V at the node, which is 4.00 V across 10 kΩ, so it carries "
                           "0.40 mA. The rest of the network balances that exactly, which is worth "
                           "checking: the two positive branches push in "
                           "$(5 + 1)/20\\text{k} = 0.300$ mA and $(5 + 1)/80\\text{k} = 0.075$ mA, and "
                           "the grounded branch pushes in $(0 + 1)/40\\text{k} = 0.025$ mA — "
                           "0.400 mA in, 0.400 mA out. The lesson is in the comparison. The output is "
                           "1.00 V from zero and the sign branch alone is moving 0.40 mA — and worse, "
                           "that current has almost nothing to do with the size of the number. `1111` "
                           "is $-1$, the smallest negative value four bits hold, and its node sits at "
                           "$-0.33$ V, so its sign branch carries "
                           "$(5 - 0.33)/10\\,\\text{k} = 0.47$ mA. `1000` is $-8$, eight times further "
                           "from zero, and its node sits at $-2.67$ V, so its sign branch carries only "
                           "$(5 - 2.67)/10\\,\\text{k} = 0.23$ mA — half as much. What sets the current "
                           "is which rail a branch is tied to and how far the node has been dragged "
                           "away from it, and the node never moves far. That is the opposite of a CMOS "
                           "gate, which draws almost nothing once it has settled, and it is why a "
                           "converter built this way gets switched off rather than left idling in "
                           "anything running on a battery.",
                },
                {
                    "title": "How long a subtraction takes, and when its overflow flag can be believed",
                    "minutes": 12,
                    "brief": r'''
Away from the copper for one question, because the cost of turning an adder into a
subtractor is paid in time and it is worth counting.

An 8-bit add/subtract block, built exactly as this module describes it: a row of eight
XOR gates that invert $b$ when `SUB` is asserted, the same `SUB` line tied to the
adder's carry-in, and eight full adders in a plain ripple. The overflow flag is one
more XOR, fed by the carry **into** the top full adder and the carry **out** of it.

Everything — $a$, $b$ and `SUB` — is valid at $t = 0$. The delays are in the table.

Signals that arrive early do not make a gate faster; a gate's output is valid once its
*latest* input has been valid for the gate's delay. So each stage settles at the worst
of its incoming paths.
''',
                    "prompt": "How long after the inputs go valid is the overflow flag V valid?",
                    "note": "Give the answer in nanoseconds, to one decimal place.",
                    "figure": r'''
```
 a7..a0  --------------------------------> the A inputs of the eight full adders
 b7..b0  --[ XOR with SUB, one per bit ]-> the B inputs
 SUB     --------------------------------> the carry-in of stage 0

 stage 0 -> stage 1 -> ... -> stage 6 -> stage 7        the carry ripples upwards

 carry INTO stage 7  ---+
                         XOR ---> V
 carry OUT of stage 7 --+
```

**Delays.** XOR gate 1.4 ns. Full adder: from either operand input to its carry-out
1.3 ns; from its carry-in to its carry-out 0.9 ns; from its carry-in to its sum output
1.1 ns; from either operand input to its sum output 1.5 ns.
''',
                    "given": [
                        {"label": "Width", "value": "8 bits"},
                        {"label": "XOR gate", "value": "1.4 ns"},
                        {"label": "Full adder, operand to carry-out", "value": "1.3 ns"},
                        {"label": "Full adder, carry-in to carry-out", "value": "0.9 ns"},
                        {"label": "Full adder, carry-in to sum", "value": "1.1 ns"},
                        {"label": "Full adder, operand to sum", "value": "1.5 ns"},
                        {"label": "Inputs valid at", "value": "t = 0"},
                    ],
                    "aside": "Three questions in order. When is the inverted $b$ ready? When does the "
                             "carry leave stage 0? And which of the two carries reaching the final XOR "
                             "arrives last?",
                    "answer": 10.4,
                    "tol": 0.05,
                    "unit": "ns",
                    "hint": "The ripple cannot start until the XOR row has settled, and V cannot settle "
                            "until the *later* of the two carries either side of the top stage has "
                            "arrived — which is the one that comes out of it.",
                    "wrong": "If you got 9.2 ns you timed the top sum bit rather than the flag. If you "
                             "got 9.5 ns the final XOR was fed from the carry *into* the top stage, at "
                             "8.1 ns — but it has both carries as inputs and settles on the later one. "
                             "9.0 ns is reachable by two different slips: stopping at the carry-out and "
                             "forgetting the XOR that turns two carries into a flag, or leaving the "
                             "input XOR row out of the front and carrying the mistake all the way "
                             "through. Those two errors are 1.4 ns each and they land on the same "
                             "number, which is worth noticing before you decide a matching answer "
                             "confirms the method.",
                    "why": "Walk it forward. The XOR row is eight gates in parallel, so every inverted "
                           "bit is valid at 1.4 ns. Stage 0 sees its carry-in at 0 (that is `SUB` "
                           "itself) and its operands at 1.4, so its carry-out is at "
                           "$\\max(0 + 0.9,\\ 1.4 + 1.3) = 2.7$ ns — the operand path wins, and it wins "
                           "in every stage. From there each stage adds 0.9 ns, because once the ripple "
                           "is moving the carry is always the last thing to arrive: stage 1 at 3.6, "
                           "stage 2 at 4.5, and so on. Stage 6's carry-out — which is the carry INTO "
                           "stage 7 — is $2.7 + 6 \\times 0.9 = 8.1$ ns, and stage 7's carry-out is "
                           "9.0 ns. The final XOR has to wait for the later of those, so "
                           "$V = 9.0 + 1.4 = 10.4$ ns. Three numbers fall out of the same walk and it "
                           "is worth keeping all three: the carry flag C is ready at 9.0 ns, the top "
                           "sum bit at $8.1 + 1.1 = 9.2$ ns, and the overflow flag last of all at "
                           "10.4 ns. So a machine that branches on a signed comparison is timed by a "
                           "path 13 % longer than the one that produces the answer, and the 1.4 ns XOR "
                           "row is charged to every ordinary addition too — which is exactly why a real "
                           "design does not use a plain ripple here, and pays for a lookahead network "
                           "to shorten the middle of that walk.",
                },
                {
                    "title": "The one resistor that moves zero",
                    "minutes": 14,
                    "brief": r'''
The same four-bit network, now holding `1000` — the most negative code there is,
$-8$. The sign bit's driver is at $-5$ V and the other three are LOW, holding 0 V.

Here is the complaint from the shop floor. Everything downstream of this converter
runs on a single positive supply, so a negative output is useless: it clips at the
input of the next stage and it needs a negative rail nobody wants to route. What is
wanted is an output that is **0 V at the most negative code** and climbs from there, so
that all sixteen codes land between 0 V and the positive rail.

The fix is one resistor from the shared node to the $+5$ V rail, permanently. It is
not drawn — working out its value is the question. The requirement is exact: with
`1000` on the wires, the node must sit at 0 V.

Before reaching for Thévenin, look at the drawn circuit again and ask what each branch
is carrying at the instant the node is at 0 V.
''',
                    "prompt": "What resistance, from the shared node to the +5 V rail, puts the node at exactly 0 V for this code?",
                    "note": "Give the answer in kilohms, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "vneg", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": -5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r8", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "r4", "kind": "R", "x": 9, "y": 5, "rot": 1, "value": 20000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
                            {"id": "r2", "kind": "R", "x": 15, "y": 5, "rot": 1, "value": 40000},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 8},
                            {"id": "r1", "kind": "R", "x": 21, "y": 5, "rot": 1, "value": 80000},
                            {"id": "g3", "kind": "GND", "x": 21, "y": 8},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [21, 3]},
                            {"a": [9, 3], "b": [9, 4]},
                            {"a": [9, 6], "b": [9, 8]},
                            {"a": [15, 3], "b": [15, 4]},
                            {"a": [15, 6], "b": [15, 8]},
                            {"a": [21, 3], "b": [21, 4]},
                            {"a": [21, 6], "b": [21, 8]},
                        ],
                    },
                    "given": [
                        {"label": "Pattern on the wires", "value": "1000 — which is -8"},
                        {"label": "Sign bit, worth -8", "value": "10 kΩ to -5 V (HIGH)"},
                        {"label": "The other three bits", "value": "20 kΩ, 40 kΩ, 80 kΩ, all to 0 V (LOW)"},
                        {"label": "Rails available", "value": "+5 V and -5 V"},
                        {"label": "Required node voltage", "value": "0.00 V"},
                    ],
                    "aside": "A branch with 0 V at both ends carries no current, whatever its resistance. "
                             "So with the node held at 0 V, three of the four drawn branches drop out of "
                             "the sum entirely and there is only one current left to cancel.",
                    "answer": 10.0,
                    "tol": 0.05,
                    "unit": "kΩ",
                    # Derived from the solved circuit, not from the algebra in the `why`: the node's
                    # open-circuit voltage times the conductance on it is the current the network
                    # injects, and the new resistor has to inject exactly the opposite from +5 V.
                    "check": r'''
var n = c.outNode();
var g = 0;
c.net.parts.forEach(function (p) {
  if (p.kind === 'R' && (p.n1 === n || p.n2 === n)) g += 1 / p.value;
});
/* the rails are symmetric, so the positive one is the magnitude of the drawn negative one */
var vp = Math.abs(c.values('V')[0]);
return vp / (-g * c.vout()) / 1000;
''',
                    "hint": "With the node at 0 V the three grounded branches carry nothing. The sign "
                            "branch carries $5/10\\text{k}$, and the new resistor has to carry the same "
                            "the other way, from a rail that is also 5 V away.",
                    "wrong": "If you got 5.33 kΩ, that is the Thévenin resistance the four drawn "
                             "branches present at the node — a real quantity, and not the one asked "
                             "for. If you got 11.43 kΩ, the new resistor was matched against the "
                             "parallel combination of the three grounded branches, "
                             "$20\\,\\text{k} \\parallel 40\\,\\text{k} \\parallel 80\\,\\text{k}$; but "
                             "those three carry nothing at all once the node is at 0 V, so there is "
                             "nothing there to match.",
                    "why": "With the node at 0 V, the 20 kΩ, 40 kΩ and 80 kΩ branches all have 0 V at "
                           "both ends and carry nothing at all. The only current left is the sign "
                           "branch's: $5\\,\\text{V}/10\\,\\text{k}\\Omega = 0.50$ mA flowing out of the "
                           "node into the $-5$ V rail. The new resistor has to push exactly 0.50 mA in "
                           "from a rail 5 V above the node, so it is "
                           "$5/0.0005 = 10\\,\\text{k}\\Omega$ — a twin of the sign resistor, and not by "
                           "accident. Adding an offset of $+8$ units has to cancel a place worth $-8$ "
                           "units exactly, so the offset branch's conductance must equal the sign "
                           "branch's. The characteristic that results is worth having. The "
                           "conductances now come to $8+4+2+1+8 = 23$ units instead of 15, and the "
                           "output for a signed value $v$ is $5(v + 8)/23$: `1000` gives 0 V, `0000` "
                           "gives $40/23 = 1.74$ V and `0111` gives $75/23 = 3.26$ V. Every code is "
                           "now positive and the output climbs steadily as the value runs from $-8$ up "
                           "to $+7$, which is what was asked for. Notice what the resistor has *not* "
                           "done: it has not changed the order the patterns arrive in, so `1000` still "
                           "follows `0111` when a counter counts and the output still falls from "
                           "3.26 V to 0 V at that step. Two other things are being paid for it. The "
                           "step between adjacent values shrinks from $5/15 = 0.333$ V to "
                           "$5/23 = 0.217$ V, because the offset resistor loads the node like every "
                           "other branch. And what has been built is no longer a two's complement "
                           "converter at all: the output is $5(v + 8)/23$, and $v + 8$ is precisely the "
                           "**offset binary** code for $v$. Which points at the cheaper way to get "
                           "here. Invert the top bit, drive every branch from the positive rail, and "
                           "throw away both the negative supply and the offset resistor: the plain "
                           "unsigned network of module 1 then puts out $5(v + 8)/15$ — the same zero at "
                           "the most negative code, the same order, and a larger step, for the price of "
                           "one inverter. That is why a bipolar converter is normally an offset-binary "
                           "part with a complemented MSB in front of it, and why the negative rail this "
                           "module has been leaning on is a way of making the sign bit visible rather "
                           "than a way anybody builds one.",
                },
            ],
            "blanks": [
                {
                    "title": "Reading, negating and widening, four bits at a time",
                    "minutes": 8,
                    "brief": r'''
A drill on the encoding itself, before any arithmetic is done with it. The places in
four bits are $-8$, $4$, $2$, $1$, and every entry below follows from those four
numbers and nothing else.

Nothing runs here; you are choosing patterns and values.
''',
                    "caption": "four bits, read and rewritten",
                    "lang": "text",
                    "listing": r'''
Four-bit two's complement.  The places are   -8   4   2   1

    pattern   value            pattern   value
    0000        0              1000       ___
    0001       +1              1001        -7
    0011       +3              1011       ___
    0111       +7              1111        -1

Negating +6:

    +6              0110
    invert          ___
    add one         1010        reads back as  -8 + 2 = -6

Widening -6 from four bits to eight:

    -6 in 4 bits            1010
    -6 in 8 bits       ___  1010

Negating the one value that has no partner:

    -8 in 4 bits    1000
    invert          0111
    add one         1000        which is  ___
''',
                    "blanks": [
                        {
                            "prompt": "`1000` takes the top place and nothing else. What is it worth?",
                            "opts": ["+8", "-8", "-0", "-7"],
                            "a": 1,
                            "why": (
                                "The top place is worth $-8$ and it is the only one taken, so the value "
                                "is $-8$ — the most negative value four bits hold. It is not a negative "
                                "zero: that is what sign-and-magnitude produces from this pattern, and "
                                "avoiding it is one of the reasons this encoding won. $-7$ is `1001`, "
                                "one place further along."
                            ),
                        },
                        {
                            "prompt": "`1011` — take the places that are set and add them up.",
                            "opts": ["-3", "-11", "-5", "+11"],
                            "a": 2,
                            "why": (
                                "$-8 + 2 + 1 = -5$. Reading the top bit as a sign and `011` as a "
                                "magnitude gives $-3$, which is the mistake this whole module exists to "
                                "unpick — $-3$ is `1101`. And $11$ is what the same four wires mean "
                                "when an unsigned instruction reads them, which is not wrong either; "
                                "the pattern does not know."
                            ),
                        },
                        {
                            "prompt": "Every bit of `0110` flips. What comes out?",
                            "opts": ["1010", "1001", "1101", "0111"],
                            "a": 1,
                            "why": (
                                "Bit by bit, `0110` becomes `1001`. That is $-8 + 1 = -7$, which is one "
                                "*below* the $-6$ being aimed at — inverting maps $x$ to $-x-1$ every "
                                "time, and the $+1$ that follows is what closes that gap. `1010` is the "
                                "finished answer rather than the intermediate one."
                            ),
                        },
                        {
                            "prompt": "The top four bits of $-6$ once it is widened to eight.",
                            "opts": ["0000", "1010", "1111", "0110"],
                            "a": 2,
                            "why": (
                                "Sign extension copies the top bit leftwards, so four ones go in front: "
                                "`1111 1010`, which reads $-128 + 64 + 32 + 16 + 8 + 2 = -6$. Padding "
                                "with zeros gives `0000 1010`, which is $+10$ — the correct widening of "
                                "those same four bits read as unsigned, and a bug in any other case. "
                                "This is the whole difference between a processor's two widening "
                                "instructions."
                            ),
                        },
                        {
                            "prompt": "Inverting `1000` and adding one has landed back on `1000`. What value is that?",
                            "opts": ["0", "+8", "-1", "-8 all over again"],
                            "a": 3,
                            "why": (
                                "`1000` is $-8$, and negating it gives $-8$ back, because $+8$ is not a "
                                "four-bit value at all — the range stops at $+7$. Every width has one "
                                "such value, and it is the reason an absolute-value routine has an "
                                "input it cannot answer and `-INT_MIN` is undefined behaviour in C. "
                                "Nothing has gone wrong in the arithmetic; the asymmetry of the range "
                                "has simply surfaced somewhere you can trip over it."
                            ),
                        },
                    ],
                },
                {
                    "title": "One subtraction, two verdicts",
                    "minutes": 9,
                    "brief": r'''
An 8-bit comparison, which is a subtraction whose result is discarded and whose flags
are kept. The same sixteen input bits are about to produce two different and equally
correct answers, and the only thing separating them is which flags get read.

`NOT b` is the row of XOR gates with `SUB` asserted; the extra $+1$ is `SUB` itself,
tied into the carry-in.
''',
                    "caption": "0x60 compared with 0xA0",
                    "lang": "text",
                    "listing": r'''
Eight bits.    a = 0x60          b = 0xA0

a - b  is computed as  a + NOT b + 1 :

             0110 0000       a
           + 0101 1111       NOT b
           +         1       the SUB line, into the carry-in
             ---------
             1100 0000       = 0xC0

    carry INTO the top column    = ___
    carry OUT of the top column  = 0

    N, the top bit of the result = 1
    C, the carry out             = 0     -> a borrow was needed
    V, the two carries differ    = ___

Read as UNSIGNED:   96 - 160.  The borrow says a is ___ b.

Read as SIGNED:     96 - (-96) = 192, which needs ___ .
                    The signed test is "N differs from V", and here
                    N = 1 and V = 1, so the machine reports  a ___ b.
''',
                    "blanks": [
                        {
                            "prompt": "Columns 0 to 6 all produced a carry. What reaches the top column?",
                            "opts": ["0", "1"],
                            "a": 1,
                            "why": (
                                "Every column below the top adds to two or more — column 6 is "
                                "$1 + 1 + 1 = 3$ — so a carry arrives at the top column. The top column "
                                "is then $0 + 0 + 1$, which is 1 with no carry out. That is the "
                                "asymmetry the overflow rule watches for: a 1 went in and nothing came "
                                "out."
                            ),
                        },
                        {
                            "prompt": "The carry in is 1 and the carry out is 0. What is V?",
                            "opts": ["1", "0"],
                            "a": 0,
                            "why": (
                                "The two carries differ, so V is set: read as signed, the true answer "
                                "did not fit. Note that C is 0 at the same moment. If the carry flag "
                                "were being used as the overflow flag, this operation would look "
                                "perfectly healthy, and it is the case where being wrong matters most."
                            ),
                        },
                        {
                            "prompt": "As unsigned, 96 minus 160 needed a borrow. What does that make a?",
                            "opts": ["above", "below", "equal to"],
                            "a": 1,
                            "why": (
                                "A borrow means the subtraction ran off the bottom, so $a$ is below $b$ "
                                "— and 96 really is less than 160. This is the whole unsigned "
                                "comparison: subtract and look at whether a borrow was needed. Nothing "
                                "else about the result matters, which is why the result itself is "
                                "thrown away."
                            ),
                        },
                        {
                            "prompt": "The signed answer is 192. How much room does that need?",
                            "opts": [
                                "nine bits — it is past the +127 where the signed range stops",
                                "eight bits, which is exactly what it has",
                                "no more room than 96 needed",
                            ],
                            "a": 0,
                            "why": (
                                "A signed byte stops at $+127$, so $192$ does not fit and needs a ninth "
                                "bit; the same 192 as an *unsigned* byte would have been fine, which is "
                                "the point. The stored result is `1100 0000`, which reads as $-64$ — "
                                "and $192 - 256 = -64$, the wrap, exactly as V predicted."
                            ),
                        },
                        {
                            "prompt": "N is 1 and V is 1, and the signed less-than test is that they differ.",
                            "opts": ["less than", "greater than or equal to", "equal to"],
                            "a": 1,
                            "why": (
                                "N and V agree, so the less-than test fails and the machine reports "
                                "$a \\geq b$ — which is right: $+96$ is greater than $-96$. Reading N "
                                "alone would have got it backwards, because the result's top bit is 1 "
                                "and the true answer was positive. That is exactly what V is for: it "
                                "records that the sign of the result is not to be trusted, and the "
                                "signed comparison corrects for it by XORing the two together."
                            ),
                        },
                    ],
                },
            ],
            "build": {
                "title": "The sign bit, in copper",
                "minutes": 25,
                "brief": r'''
Module 1 built a two-bit unsigned number as a voltage: two resistors in a 1:2 ratio
onto one shared node, and the node landed at two thirds of the rail for the pattern
`10`. This is the same circuit with **one wire moved**, and it is the whole of two's
complement in hardware.

Read the same two bits as signed. The top bit is now worth $-2$ instead of $+2$, so
its resistor must be pulled towards a **negative** rail rather than a positive one.
The ones bit is unchanged at $+1$ and keeps its resistor to $+5$ V.

Build the pattern `11`, which in two's complement is $-2 + 1 = -1$:

* a $+5$ V supply, and a resistor of **twice** the unit value from it to the shared node — that is the ones bit, HIGH
* a $-5$ V supply, and a resistor of the **unit** value from it to the same node — that is the sign bit, HIGH
* a probe on the shared node

The network scales one unit of value to $5/3$ of a volt, so the answer is
$-1 \times 5/3 = \mathbf{-1.67\ V}$. Only the ratio of the two resistors matters, and
the pair has to draw less than 1 mA from the rails.

To make the negative supply, place a voltage source and type a value of `-5`. Drawing
the battery upside down means the same thing, and is what you would see on a
schematic.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 20000},
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
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 20000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3},
                        {"id": "p4", "kind": "R", "x": 12, "y": 3, "rot": 0, "value": 10000},
                        {"id": "p5", "kind": "V", "x": 15, "y": 6, "rot": 1, "value": -5},
                        {"id": "p6", "kind": "GND", "x": 15, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [5, 3]},
                        {"a": [7, 3], "b": [9, 3]},
                        {"a": [9, 3], "b": [11, 3]},
                        {"a": [13, 3], "b": [15, 3]},
                        {"a": [15, 3], "b": [15, 5]},
                        {"a": [15, 7], "b": [15, 9]},
                    ],
                },
                "checks": [
                    {"name": "two rails: one at +5 V and one at -5 V", "code": r'''
var vs = c.values('V');
c.assert(vs.length === 2,
  'This network needs two supplies — the ones bit is pulled towards +5 V and the sign bit towards ' +
  '-5 V. Found ' + vs.length + '.');
c.assert(vs.some(function (x) { return Math.abs(x - 5) < 0.005; }),
  'One supply has to sit at +5 V: that is the rail a HIGH value bit is pulled towards.');
c.assert(vs.some(function (x) { return Math.abs(x + 5) < 0.005; }),
  'One supply has to sit at -5 V. Nothing else here can make a node voltage negative, and a ' +
  'negative node voltage is the entire point of a sign bit.');
'''},
                    {"name": "two resistors, meeting at the probed node", "code": r'''
c.assert(c.count('R') === 2, 'One resistor per bit: two of them, meeting at the shared node.');
c.assert(Math.abs(Math.abs(c.vout()) - 5) > 0.1,
  'The probe is reading a rail rather than the shared node. Move it to the wire where the two ' +
  'resistors meet.');
'''},
                    {"name": "the node reads the pattern 11, which is minus one", "code": r'''
c.close(c.vout(), -5 / 3, 0.02,
  'the shared node for the pattern 11. In twos complement that is -2 + 1 = -1, and this network ' +
  'is worth 5/3 of a volt per unit, so the answer is -1.67 V');
'''},
                    {"name": "the pair draws less than 1 mA", "code": r'''
var cur = c.dc().currents;
var mags = Object.keys(cur).map(function (k) { return Math.abs(cur[k]); });
c.assert(mags.length > 0, 'There is no supply current to measure — are both rails connected to anything?');
var worst = Math.max.apply(null, mags);
c.assert(worst < 1e-3,
  'The rails are pushing ' + c.fmt(worst, 'A') + ' through the pair. Scale both resistors up together, ' +
  'keeping the 1:2 ratio: the node voltage does not move by a millivolt.');
'''},
                ],
                "hints": [
                    "With the sign bit's resistor $R_s$ going to $-5$ V and the ones bit's $R_1$ going to $+5$ V, the shared node sits at $5(R_s - R_1)/(R_s + R_1)$ — the conductance-weighted average of the two rails.",
                    "The sign bit is worth twice as much as the ones bit, so it has to pull twice as hard: half the resistance. Put $R_1 = 2R_s$ into the expression above and it gives $-5/3$ V.",
                    "10 kΩ to $-5$ V and 20 kΩ to $+5$ V draws $10/30\\,\\text{k} = 0.33$ mA. 1 kΩ and 2 kΩ produce exactly the same voltage and draw 3.3 mA, which fails the last check.",
                    "The two rails are 10 V apart, not 5 — that is what the current check is measuring, and it is why the resistors have to be larger here than in module 1 for the same current budget.",
                ],
            },
            "derive": {
                "title": "Why inverting and adding one is negation",
                "minutes": 12,
                "brief": r'''
"Invert every bit and add one" is usually handed over as a recipe. It is not a
recipe; it is forced, and five short steps show why.

The one thing to hold onto is that an $n$-bit adder cannot count past $2^n$. Anything
above that falls off the end and is lost, so all its arithmetic is done **modulo
$2^n$** whether anyone intended that or not. Write $\overline{x}$ for the bitwise
inverse of $x$ — every 1 turned into a 0 and every 0 into a 1.
''',
                "vars": ["n", "x"],
                "steps": [
                    {
                        "prompt": "How many different patterns does an $n$-bit number have? Write it in terms of $n$.",
                        "answer": "2^n",
                        "hint": "Each extra bit doubles the count, exactly as in module 1.",
                        "deconstruct": [
                            "One bit has two patterns.",
                            "Every bit added doubles that, so $n$ bits have $2^n$.",
                        ],
                    },
                    {
                        "prompt": "For a pattern to deserve the name $-x$, adding it to $x$ must give zero in $n$ bits — that is, the true sum must be the one value that falls off the end and reads as zero. Write the value that pattern must have, in terms of $x$ and $n$.",
                        "given": "Adding is modulo $2^n$: the sum $2^n$ is stored as $0$ with the carry lost.",
                        "answer": "2^n - x",
                        "hint": "You need $x + (\\text{the pattern}) = 2^n$. Solve for the pattern.",
                        "deconstruct": [
                            "The requirement is $x + p = 2^n$, because $2^n$ is what reads back as zero.",
                            "Subtract $x$ from both sides.",
                        ],
                    },
                    {
                        "prompt": "Change tack. Between $x$ and its inverse $\\overline{x}$ there is a 1 in every place, so their sum is the all-ones pattern. Write the value of the all-ones $n$-bit pattern.",
                        "answer": "2^n - 1",
                        "hint": "It is the largest unsigned value $n$ bits can hold — one less than the number of patterns.",
                        "deconstruct": [
                            "All ones is $1 + 2 + 4 + \\cdots + 2^{n-1}$.",
                            "That geometric sum is $2^n - 1$, which is why the largest 8-bit value is 255 and not 256.",
                        ],
                    },
                    {
                        "prompt": "So $x + \\overline{x} = 2^n - 1$. Write the value of $\\overline{x}$ on its own, in terms of $x$ and $n$.",
                        "answer": "2^n - 1 - x",
                        "hint": "Subtract $x$ from both sides of the identity in the given.",
                        "deconstruct": [
                            "$x + \\overline{x} = 2^n - 1$.",
                            "Therefore $\\overline{x} = 2^n - 1 - x$ — inverting maps $x$ to one less than its negation, which is why the recipe does not stop there.",
                        ],
                    },
                    {
                        "prompt": "Add one to that, and write what $\\overline{x} + 1$ comes to.",
                        "answer": "2^n - x",
                        "hint": "The $-1$ and the $+1$ cancel. Then compare the result with what you wrote earlier for $-x$.",
                        "deconstruct": [
                            "$\\overline{x} + 1 = (2^n - 1 - x) + 1$.",
                            "$= 2^n - x$, which is exactly the pattern that had to stand for $-x$.",
                        ],
                    },
                ],
                "closing": r'''
$$\overline{x} + 1 = 2^n - x = -x \pmod{2^n}$$

Three consequences, all of them hardware.

Subtraction disappears as a separate operation. $a - b = a + (-b) = a + \overline{b} + 1$,
and the $+1$ costs nothing at all because the adder already has a carry-in sitting
unused at the bottom. An inverter per bit and a wire is the whole subtractor.

Nothing in the derivation mentioned the sign bit. It was never a sign bit — it is an
ordinary place that happens to be worth $-2^{n-1}$, and every rule you have follows
from the modulo arithmetic rather than from any special treatment of the top wire.

And there is one value with no partner. The most negative number is stored as the
pattern $2^{n-1}$ — a 1 followed by zeros — and negating it gives
$2^n - 2^{n-1} = 2^{n-1}$, the pattern it started from. Negating $-8$ in four bits
gives $-8$ back. That is not a bug in the encoding; it is the asymmetric range from
the second concept, showing up somewhere you can trip over it.
''',
            },
            "lab": {
                "title": "Two's complement, both directions, and the two overflow flags",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Four functions. Between them they turn every claim in this module into something a
loop can check.

Bit lists are **most significant first** throughout, as everywhere else in this
course, so $-5$ in four bits is `[1, 0, 1, 1]`.

**`to_signed(bits)`** — the value of a pattern read as two's complement. The leftmost
place is negative; every other place is positive.

**`to_bits(value, n)`** — the $n$-bit pattern for a value, which may be negative.
Python's `%` on a negative left operand returns a non-negative result, which is
exactly the modulo-$2^n$ reduction the derivation asked for.

**`negate(bits)`** — invert every bit and add one, using `add_signed` to do the
adding rather than converting to an integer.

**`add_signed(a_bits, b_bits, cin=0)`** — a ripple adder that also reports both
overflow conditions: the carry-out, and signed overflow, which is the carry into the
top bit differing from the carry out of it. You need to catch the carry on its way
into the last stage, which means noticing it before that stage overwrites it.
''',
                "files": [{"name": "main.py", "content": r'''
def to_signed(bits):
    """The value of a two's complement pattern, most significant bit first."""
    # TODO: every place is a power of two; the leftmost one is negative.
    return 0


def to_bits(value, n):
    """The n-bit two's complement pattern for `value`, most significant first."""
    # TODO: reduce the value modulo 2**n first, then peel the bits off.
    return [0] * n


def add_signed(a_bits, b_bits, cin=0):
    """Ripple-add two patterns of equal length.

    Return (bits, carry_out, overflow), where overflow is 1 when the carry INTO
    the top bit differs from the carry OUT of it.
    """
    n = len(a_bits)
    out = [0] * n
    # TODO: run from the least significant end (index n - 1) down to index 0,
    # remembering the carry as it goes into the last stage.
    return out, 0, 0


def negate(bits):
    """Invert every bit and add one, using add_signed to do the adding."""
    # TODO
    return list(bits)


if __name__ == "__main__":
    print("1011 signed :", to_signed([1, 0, 1, 1]))
    print("-5 in 8 bits:", to_bits(-5, 8))
    print("6 + 5       :", add_signed(to_bits(6, 4), to_bits(5, 4)))
    print("7 + (-7)    :", add_signed(to_bits(7, 4), to_bits(-7, 4)))
    print("negate 6    :", negate(to_bits(6, 4)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def to_signed(bits):
    """The value of a two's complement pattern, most significant bit first."""
    n = len(bits)
    value = 0
    for i, b in enumerate(bits):
        place = 2 ** (n - 1 - i)
        value += (-place if i == 0 else place) * b
    return value


def to_bits(value, n):
    """The n-bit two's complement pattern for `value`, most significant first."""
    pattern = value % (2 ** n)
    return [(pattern >> place) & 1 for place in range(n - 1, -1, -1)]


def add_signed(a_bits, b_bits, cin=0):
    """Ripple-add two patterns of equal length.

    Return (bits, carry_out, overflow), where overflow is 1 when the carry INTO
    the top bit differs from the carry OUT of it.
    """
    n = len(a_bits)
    out = [0] * n
    carry = cin
    top_cin = 0
    for i in range(n - 1, -1, -1):
        if i == 0:
            top_cin = carry
        total = a_bits[i] + b_bits[i] + carry
        out[i] = total % 2
        carry = 1 if total >= 2 else 0
    return out, carry, 1 if top_cin != carry else 0


def negate(bits):
    """Invert every bit and add one, using add_signed to do the adding."""
    flipped = [1 - b for b in bits]
    one = [0] * (len(bits) - 1) + [1]
    out, _carry, _over = add_signed(flipped, one)
    return out


if __name__ == "__main__":
    print("1011 signed :", to_signed([1, 0, 1, 1]))
    print("-5 in 8 bits:", to_bits(-5, 8))
    print("6 + 5       :", add_signed(to_bits(6, 4), to_bits(5, 4)))
    print("7 + (-7)    :", add_signed(to_bits(7, 4), to_bits(-7, 4)))
    print("negate 6    :", negate(to_bits(6, 4)))
'''}],
                "hints": [
                    "In `to_signed`, `enumerate` gives you the index; index 0 is the leftmost bit and the only one whose place is negative.",
                    "`value % (2 ** n)` does the whole of the modulo reduction: `-5 % 16` is 11 in Python, and 11 is `1011`, which is what $-5$ looks like in four bits.",
                    "In `add_signed`, the carry variable is overwritten by each stage, so capture it *before* the top stage runs — `if i == 0: top_cin = carry` at the head of the loop body does it.",
                    "`negate` does not need any arithmetic of its own: build the inverted list with `[1 - b for b in bits]`, build a pattern for one, and hand both to `add_signed`.",
                ],
                "tests": [
                    {"name": "patterns read back as the right values", "code": r'''
assert to_signed([1, 0, 1, 1]) == -5, f"1011 is -8 + 2 + 1; got {to_signed([1, 0, 1, 1])}"
assert to_signed([0, 1, 1, 1]) == 7, "0111 is the largest 4-bit signed value"
assert to_signed([1, 0, 0, 0]) == -8, "1000 is the most negative 4-bit value"
assert to_signed([1, 1, 1, 1]) == -1, f"all ones is -1, got {to_signed([1, 1, 1, 1])}"
assert to_signed([0, 0, 0, 0]) == 0
'''},
                    {"name": "values convert to patterns, and back again", "code": r'''
assert to_bits(-5, 4) == [1, 0, 1, 1], f"expected [1, 0, 1, 1], got {to_bits(-5, 4)}"
assert to_bits(-13, 8) == [1, 1, 1, 1, 0, 0, 1, 1], f"got {to_bits(-13, 8)}"
assert to_bits(0, 4) == [0, 0, 0, 0]
for _v in range(-8, 8):
    assert to_signed(to_bits(_v, 4)) == _v, f"{_v} did not survive the round trip"
for _v in range(-128, 128):
    assert to_signed(to_bits(_v, 8)) == _v, f"{_v} did not survive the round trip in 8 bits"
'''},
                    {"name": "negation is invert-and-add-one, with one exception", "code": r'''
for _v in range(-7, 8):
    assert to_signed(negate(to_bits(_v, 4))) == -_v, \
        f"negate should turn {_v} into {-_v}, got {to_signed(negate(to_bits(_v, 4)))}"
assert negate(to_bits(-8, 4)) == to_bits(-8, 4), \
    "-8 has no positive partner in four bits, so negating it gives -8 back"
'''},
                    {"name": "the two flags on four worked examples", "code": r'''
assert add_signed(to_bits(3, 4), to_bits(4, 4)) == ([0, 1, 1, 1], 0, 0), \
    f"3 + 4 fits: got {add_signed(to_bits(3, 4), to_bits(4, 4))}"
assert add_signed(to_bits(6, 4), to_bits(5, 4)) == ([1, 0, 1, 1], 0, 1), \
    "6 + 5 overflows as signed and the carry-out is still 0"
assert add_signed(to_bits(-6, 4), to_bits(-5, 4)) == ([0, 1, 0, 1], 1, 1), \
    "-6 + -5 overflows as signed, and here the carry-out happens to be 1"
assert add_signed(to_bits(7, 4), to_bits(-7, 4)) == ([0, 0, 0, 0], 1, 0), \
    "7 + (-7) is exactly right, and yet the carry-out is 1 — carry is not overflow"
'''},
                    {"name": "both flags agree with the definitions on all 256 pairs", "code": r'''
for _a in range(-8, 8):
    for _b in range(-8, 8):
        _bits, _cout, _over = add_signed(to_bits(_a, 4), to_bits(_b, 4))
        assert to_signed(_bits) == ((_a + _b + 8) % 16) - 8, \
            f"{_a} + {_b} gave {to_signed(_bits)}"
        assert _over == (0 if -8 <= _a + _b <= 7 else 1), \
            f"{_a} + {_b} is {'in' if -8 <= _a + _b <= 7 else 'out of'} range; overflow said {_over}"
        assert _cout == ((_a % 16) + (_b % 16)) // 16, \
            f"{_a} + {_b}: the carry-out is the unsigned overflow of the same bits, got {_cout}"
'''},
                ],
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Registers, shift registers and counters",
            "summary": "Flip-flops in groups. Hold a word, walk it sideways, or count with it — and pay for the cheap counter in outputs that are briefly wrong.",
            "concepts": [
                "A **register** is $n$ flip-flops sharing one clock. Everything it holds changes at the same instant or not at all, which is what makes a word transfer atomic: no half-updated value is ever visible to anything downstream.",
                "A **shift register** wires each flip-flop's output to the next one's input, so the word walks one place per edge. Serial in, parallel out turns a one-wire link into a word; parallel in, serial out does the reverse, and is how a handful of pins drives a great many outputs. Shifting left is multiplying by two — module 1's place-value fact, now with a clock attached.",
                "A **ripple counter** is the cheapest counter there is: each flip-flop toggles when the one before it changes, and only the first sees the clock. It costs almost no logic, and its outputs are wrong for a while after every edge, because the change has to walk down the chain one propagation delay per stage.",
                "A **synchronous counter** clocks every flip-flop from the same edge and works out the next state combinationally, so all the outputs move together. It costs more gates and buys the timing budget from module 4 — one clock-to-output delay plus one pass through the logic, whatever the width.",
                "A **modulo-N counter** is a synchronous counter with logic that spots $N-1$ and forces the next state back to zero. An **LFSR** replaces the adder with a couple of XOR gates and visits all $2^n - 1$ non-zero states in a scrambled order — much cheaper than a counter, and perfectly good wherever the order does not matter.",
            ],
            "read": [
                {
                    "title": "Eight flip-flops that agree on when",
                    "minutes": 14,
                    "body": r'''
Module 4 said everything there is to say about one flip-flop: an edge arrives,
whatever is sitting on D at that instant is captured, and Q holds it until the next
edge. That is a complete account of one bit, and one bit is almost nothing. An address
is 32 bits wide, a pixel is 24, a sample off a microphone is 16, and a counter that
only counts to one is not a counter. The interesting question is not how to store a
bit. It is what changes when you put a lot of them side by side.

Put eight flip-flops in a row and run **one wire** to all eight clock inputs. That is
a **register**, and that is the whole construction — no sequencer, no controller, no
logic between them. The only design decision in it is the shared wire, and the shared
wire is the entire point.

## What the shared wire buys

The way to see what it is for is to look at what you get without it.

Suppose the eight bits live in eight separate storage elements, each with its own
enable, and suppose those enables come from logic that is nearly the same for each but
not identical — a slightly different wire length, a gate with a slightly different
load. Now write a new byte. Bit 3 closes its enable 2 ns before bit 6 does. For those
2 ns the group holds bit 3 of the new byte and bit 6 of the old one, and anything
sampling the group during that window reads a byte that nobody ever wrote. It is not
the old value and it is not the new one. It is a splice.

That is not an exotic failure to be designed around with care. It is the *default*
behaviour of eight independent storage elements, and it will happen on nearly every
write, because two signals travelling down two different pieces of copper do not
arrive together.

One clock wire makes it impossible. Every flip-flop samples its D at the same edge,
every Q changes one clock-to-output delay later, and a reader that respects setup and
hold sees either the whole old byte or the whole new one. There is no third
possibility, because there is no moment at which some flip-flops have decided and
others have not.

The property has a name — **atomicity** — and buying it is the reason registers are
built this way and not some other way.

It is worth being precise about what atomicity does *not* buy, because the word invites
more than it delivers. Nothing here stops something reading the register while a write
is in progress. There is no lock, no busy flag, no interlock. The guarantee is only
that whatever a reader gets is a value that was really written. If what you need is
"nobody may read during a write", that is a protocol built on top of this, and it needs
hardware of its own.

## Loading only when you mean to

A register with nothing but a clock captures its D inputs on every single edge, which
is almost never what is wanted. A processor has thirty-two registers with the clock
running to all of them, and on any given cycle at most one of them is supposed to
change.

The obvious fix is to interrupt the clock: AND it with a `LOAD` signal so the
flip-flops only see an edge when the load is asserted. Do not do this. The gate you
have added has a delay, so this register's clock now arrives later than every other
register's clock and you have manufactured skew deliberately — and the next section
shows exactly what skew costs. Worse, if `LOAD` changes near the clock edge, the AND
gate emits a runt: a pulse too narrow to be a clock and too wide to be nothing, whose
effect on a flip-flop is not specified by anything.

The fix that works leaves the clock alone and changes what D sees:

```
                +-----------+
   new data --->| 1         |
                |       MUX |---> D
        +------>| 0         |
        |       +-----------+
        |             ^
        |             |
        |           LOAD
        |
        +---- Q  (this flip-flop's own output, fed back)
```

With `LOAD = 1` the flip-flop captures the new data. With `LOAD = 0` it captures its
own output — it clocks faithfully, every cycle, and rewrites the value it already had.
The contents change only when told, the clock is never touched, and the cost is one
two-input multiplexer per bit. Every register in every synchronous design you will
meet is built like this.

## Wire the outputs to the next inputs

Take the same eight flip-flops. Instead of giving each one its own D, wire flip-flop
$k$'s output to flip-flop $k+1$'s input, and feed a single wire into the first. That is
a **shift register**: the same silicon with the D inputs connected differently.

Now each edge moves the whole word one place along. Serial in, parallel out: eight
edges turn a one-wire link into a byte you can read all at once. Parallel in, serial
out: load all eight at once, then clock eight times and the byte leaves on one pin.
This is how three pins drive twenty-four LEDs, how an SD card talks to a
microcontroller, and how a chip with 200 internal test points reports all of them
through one leg.

## Why the word does not race through

Here is the question everybody asks once, and it is exactly the right question. Every
stage's D is the previous stage's Q, and all of them clock at the same instant. So when
the edge arrives, why does the serial input not shoot straight down all eight stages
and fall out the far end in one go?

Because a flip-flop's output does not change at the edge. It changes $t_{cq}$ *after*
the edge — the clock-to-output delay. And a flip-flop's input only has to be held
steady for $t_h$ after the edge — the hold time. Take a part with $t_{cq} = 5.0$ ns and
$t_h = 1.5$ ns and lay the two out on one timeline:

```
 t = 0.0 ns   the edge reaches every stage at once
 t = 0.0 ns   every stage begins capturing whatever is on its D
 t = 1.5 ns   the hold window closes; what was captured is committed
 t = 5.0 ns   every stage's Q changes to what it captured
```

Every stage captured the **old** output of the stage in front of it, because the new
one did not exist for another 3.5 ns. The word moves exactly one place. The race does
not happen because the flip-flops are slow — and here slowness is the mechanism rather
than the cost.

That timeline also prices the clock skew this arrangement can survive. Let $\Delta$ be
how much later stage $k+1$'s clock arrives than stage $k$'s. Stage $k+1$ then closes
its hold window at $\Delta + t_h$, while the new data from stage $k$ turns up at
$t_{cq}$. Nothing breaks as long as the data is late:

$$t_{cq} \;\ge\; \Delta + t_h \qquad\Longrightarrow\qquad \Delta \;\le\; t_{cq} - t_h$$

```
 delta  <=  5.0 ns - 1.5 ns  =  3.5 ns
```

Exceed 3.5 ns of skew between two neighbouring stages and the bit races through both of
them on one edge; the register drops a bit out of every word and the data comes out
shortened and wrong. And here is the part that catches people: **slowing the clock down
does not help at all.** Neither $t_{cq}$ nor $t_h$ has anything to do with the clock
period, so the inequality above does not contain it. A setup violation is a
speed problem and goes away when you go slower. A hold violation is a *skew* problem,
and the only cures are fixing the skew or deliberately adding delay in the data path.

## Worked example: a byte arriving on one wire

A 4-bit serial-in, parallel-out register, initially all zero. Write the stages left to
right as $Q_0\,Q_1\,Q_2\,Q_3$, with the serial input feeding $Q_0$ and each stage
handing on to its right-hand neighbour. The bits `1`, `0`, `1`, `1` arrive in that
order, one per edge.

```
 edge   bit in     Q0 Q1 Q2 Q3
  -        -        0  0  0  0
  1        1        1  0  0  0
  2        0        0  1  0  0
  3        1        1  0  1  0
  4        1        1  1  0  1
```

After four edges the register holds `1101` reading left to right. Check it against the
input: the bits arrived 1, 0, 1, 1, and the one that arrived **first** has been pushed
furthest, so it is in $Q_3$; the one that arrived last is still in $Q_0$. Read
$Q_3\,Q_2\,Q_1\,Q_0$ — right to left — and you get `1011`, the arrival order.

Which end you call the answer is a convention, and getting it backwards is the most
common bug in a serial link. It is why every datasheet says whether a device is
most-significant-bit-first or least-significant-bit-first, and why two devices that
disagree about it exchange bytes that are bit-reversed rather than garbled: `1011`
becomes `1101`, which is 11 sent and 13 received.

## Shifting is arithmetic

Module 1 established that in base two the columns double from the right. Move every bit
one place left and every column it occupies doubles, so the value doubles. That is not
an analogy, it is the same fact:

```
 0011  = 3     shift left ->  0110  =  6
 0110  = 6     shift left ->  1100  = 12
 1100  = 12    shift left ->  1000  =  8   ??
```

The last line is not an error in the arithmetic; it is the register running out of
room. $12 \times 2 = 24$, the bit that was worth 8 moved to a column worth 16 that does
not exist in four bits, and what is left is $24 - 16 = 8$. A shift left is a multiply
by two **modulo $2^n$**, which is the same modulo the adder in module 7 was already
working in.

Going the other way is a divide by two, and there the choice of what to feed in at the
top is the whole question. Feed in a 0 and `1010` (which is 10 unsigned) becomes `0101`
(5) — correct for unsigned. But `1010` read as two's complement is $-6$, and a 0 shifted
in gives `0101`, which is $+5$: the sign has been thrown away. Copy the top bit instead
and `1010` becomes `1101`, which is $-3$ — correct. That is why a processor has two
right-shift instructions and only one left-shift: there is nothing to decide on the way
up, and a sign to preserve on the way down.

## The mistake people actually make

**Treating the shift register as combinational.** Draw eight flip-flops with their
outputs wired to the next input and it looks, on paper, like a chain that a value can
run down. The instinct is that the bit propagates, and it does not: it advances one
stage per edge because the flip-flops are edge-triggered and slower to change than they
are to capture. The instinct is tempting because it is exactly right for the
*transparent latch* of module 4 — chain latches with a shared enable and the value
genuinely does run down the whole chain while the enable is high. That circuit exists,
it is broken in precisely this way, and it is why edge-triggered flip-flops were worth
inventing.

**Gating the clock to make a load enable.** It is the shortest thing to draw and it
appears to be free. It is neither: it adds skew to the one signal in the design whose
skew you cannot afford, and it can produce pulses that are not clean edges. The
multiplexer looks like more hardware and is less trouble.

**Assuming a slower clock fixes a shift register that drops bits.** It is a reasonable
thing to believe, because it is true of nearly every other timing failure. The
inequality $\Delta \le t_{cq} - t_h$ has no clock period in it, and that is the whole
story: a hold violation at 100 MHz is still a hold violation at 1 kHz.

## Where this stops being enough

**At the ends of the shift register.** Everything above assumed the data and the clock
travel together. The moment the serial link leaves the chip they do not: the wire has a
delay, the far end has a different clock, and by the time the word arrives, the
transmitter's edge and the receiver's edge have nothing to do with each other. What
replaces the plain shift register is either a clock sent alongside the data
(source-synchronous, which is what SPI and every parallel bus do) or a receiver that
recovers the clock from the data stream itself, which is what an asynchronous serial
port and every serialiser above a gigabit do.

**At the boundary between two clocks.** A register guarantees its own bits move
together. It guarantees nothing about a *reader* clocked by something else. Feed a
register's output into a circuit on an unrelated clock and that circuit can sample
mid-transition, and the answer is not merely old or new but genuinely undefined for a
while — the metastability of module 4. What replaces a plain wire there is a
synchroniser: two flip-flops in series on the receiving clock, which is a two-stage
shift register used for its settling time rather than for its shifting.

**When the word is wider than the link is long-lived.** A shift register moves one bit
per edge and nothing else, so it cannot hold two words at once and has nowhere to put a
word that arrives before the last one was read. What replaces it is a FIFO: a small
memory with a write pointer and a read pointer, which is module 10's material and, not
coincidentally, uses counters for both pointers.
''',
                },
                {
                    "title": "Counting is dividing by two, over and over",
                    "minutes": 15,
                    "body": r'''
Nobody designs a counter by writing down a state table with 65,536 rows. Counters are
built out of one observation, made once and then repeated: a flip-flop that toggles
divides a frequency in half, and place value in base two is nothing but a stack of
halvings.

## One flip-flop, half the frequency

Take a D flip-flop and wire $\overline{Q}$ back round to D. Every edge it captures the
opposite of what it holds, so every edge it changes state. That is a **toggle
flip-flop**, and it is one wire.

Watch its output. It goes high, stays high for one clock period, goes low, stays low
for one clock period, and repeats. One complete cycle of the output takes **two** clock
periods, so if the clock runs at $f$ the output runs at $f/2$. A toggle flip-flop is a
divide-by-two, exactly and with no tuning, and this is the reason digital designs are
full of powers of two rather than powers of ten: two is what one flip-flop gives you
for free.

## Chain them, and place value appears

Now clock a second toggle flip-flop from the first one's output rather than from the
clock. Its output runs at $f/4$. A third gives $f/8$. After $n$ stages the last output
runs at $f/2^n$.

Line the outputs up and read them as a binary number, $Q_{n-1}$ down to $Q_0$, and you
have not built a divider — you have built a counter. $Q_0$ changes on every clock,
$Q_1$ on every second clock, $Q_2$ on every fourth. That is precisely the pattern the
places of a binary number follow when you count up through them: the ones column
alternates every step, the twos column every two steps, the fours column every four.
Nothing was designed to make the count come out. It falls out of the halving, because
halving *is* place value.

There is one detail that decides whether the thing counts up or down. Stage $k+1$ must
flip when stage $k$ **rolls over** — goes from 1 back to 0 — because that is when the
column above it takes a carry. With negative-edge-triggered flip-flops, clocking stage
$k+1$ from $Q_k$ does exactly that: $Q_k$ falling is the roll-over. Clock it from
$\overline{Q_k}$ instead, or use positive-edge parts, and it flips on the wrong
transition and the whole thing counts down. It is a perfectly good down-counter and a
completely broken up-counter, and one inverter is the difference.

This arrangement is a **ripple counter**: only the first flip-flop is connected to the
clock, and every other stage is clocked by its neighbour. It costs $n$ flip-flops, $n$
wires and no logic whatsoever. Nothing else counts that cheaply.

## Worked example: a crystal to one pulse a second

A quartz watch crystal runs at 32,768 Hz. That number is not an accident of physics;
it is $2^{15}$, chosen so that fifteen toggle flip-flops in a row turn it into exactly
one pulse per second:

```
 32768 Hz  ->  stage 1  ->  16384 Hz
               stage 2  ->   8192 Hz
               ...
               stage 15 ->      1 Hz
```

Fifteen flip-flops, fourteen wires between them, no gates at all. Suppose each stage
takes 10 ns to respond to its input. The last stage's edge is then
$15 \times 10 = 150$ ns behind the crystal edge that caused it. That sounds bad until
you notice what kind of error it is. It is a fixed offset, the same 150 ns on every
tick, so it never accumulates: the watch is permanently 150 ns behind the crystal and
stays exactly that far behind for the rest of its life. What *does* accumulate is the
crystal's own frequency tolerance, typically $\pm 20$ parts per million, which comes to
about ten minutes a year. Over that year the divider chain contributes 150 nanoseconds
and the crystal contributes ten minutes; they are not in the same conversation.

This is the ripple counter at its best. Nothing looks at the intermediate stages,
nothing decodes the count, and the only output anybody cares about is the last one. Its
weakness is entirely invisible here.

## The weakness, when you do look at the outputs

The weakness is that the change has to **walk**. Only stage 0 hears the clock; every
other stage is waiting for its neighbour.

Take a 4-bit ripple counter with 10 ns per stage, going from 7 to 8. In binary that is
`0111` to `1000`, and it is the worst case, because every single stage has to flip.
Write the outputs $Q_3 Q_2 Q_1 Q_0$:

```
 t =  0 ns   the clock edge arrives          0111    = 7
 t = 10 ns   Q0 falls, which clocks stage 1  0110    = 6
 t = 20 ns   Q1 falls, which clocks stage 2  0100    = 4
 t = 30 ns   Q2 falls, which clocks stage 3  0000    = 0
 t = 40 ns   Q3 rises                        1000    = 8
```

For 40 ns after the edge the four output pins are showing something that is not 8. They
are not floating and they are not noise — they are firmly driven, perfectly valid logic
levels, spelling out 6, then 4, then 0. Anything reading those pins during that window
gets a wrong answer with no indication that anything is amiss.

Turn that into a clock limit. The next edge must not arrive until the last stage has
settled, so the period is at least $n \times t_{cq} = 4 \times 10 = 40$ ns, which caps
the clock at 25 MHz. Add a bit and it gets worse in proportion: eight stages is 80 ns
and 12.5 MHz, sixteen stages is 160 ns and 6.25 MHz. The limit is **inversely
proportional to the width**, which is a bad way for anything to scale.

## What the glitch actually breaks

The transient values are the real problem, more than the settling time is.

Put an AND gate across the outputs to detect a particular count — the usual way to make
something happen at a specific moment. Point it at zero, so it looks for
$\overline{Q_3}\,\overline{Q_2}\,\overline{Q_1}\,\overline{Q_0}$. Look at the timeline
above: at $t = 30$ ns the counter passes through `0000` on its way from 7 to 8, and the
gate fires for 10 ns in the middle of a count that has nothing to do with zero.

Nor is that the only time. Work through the sixteen transitions and the outputs pass
through `0000` on the way into 2, into 4 and into 8 as well — every time the count
crosses into a power of two, all the lower stages fall to zero before the new top stage
comes up. So the zero decoder produces four pulses per sixteen counts: one real one when
the counter genuinely reaches zero, and three that are pure artefact.

If those pulses drive a light, nobody will ever see them. If they drive the clock of
another flip-flop, or an interrupt, or a chip select, it is a fault that appears at
three counts in sixteen and will survive every test that does not look there. This is
why "do not decode a ripple counter combinationally" is a rule rather than a preference,
and why the fix is normally to re-time the decoded signal through a flip-flop clocked by
the master clock — which is to say, to stop being asynchronous.

## Clocking every stage at once

The alternative gives up the free carry and pays gates for it. In a **synchronous
counter** the clock goes to every flip-flop, all of them capture at the same edge, and
combinational logic works out beforehand which ones should change.

The rule that logic implements is the one you already use when counting on paper. A
column flips when every column below it is at its maximum and is about to roll over. In
base two, maximum means 1, so:

$$T_k \;=\; Q_0 \cdot Q_1 \cdot Q_2 \cdots Q_{k-1}$$

Bit 0 toggles every time ($T_0 = 1$). Bit 1 toggles when bit 0 is 1. Bit 3 toggles when
bits 0, 1 and 2 are all 1 — which happens once every eight counts, exactly as it should.
The count is the same count; the only difference is that it is computed rather than
propagated.

Because every flip-flop is clocked together, all the outputs change together, and the
transient states of the ripple counter simply do not exist. The outputs go from 7 to 8
with nothing in between except the flip-flops' own settling, which is the same 5-or-so
nanoseconds for every bit at once.

## Worked example: what the synchronous counter costs in time

The clock period has to cover one clock-to-output delay, one trip through the toggle
logic, and the setup time of the flip-flop that is about to capture:

$$T \;\ge\; t_{cq} + t_{logic} + t_{su}$$

Take $t_{cq} = 5.5$ ns, $t_{su} = 1.5$ ns and 2-input AND gates at 2.0 ns each.

For an 8-bit counter the widest toggle term is $T_7 = Q_0 Q_1 \cdots Q_6$, an AND of
seven signals. Built as a balanced tree of 2-input gates that is three levels deep
($\lceil \log_2 7 \rceil = 3$), so $t_{logic} = 3 \times 2.0 = 6.0$ ns:

```
 T  >=  5.5 + 6.0 + 1.5  =  13.0 ns      ->  76.9 MHz
```

For 16 bits the widest term ANDs fifteen signals, a tree four levels deep:

```
 T  >=  5.5 + 8.0 + 1.5  =  15.0 ns      ->  66.7 MHz
```

Now put that beside the ripple counter built from the same flip-flops, where the limit
is $n \times t_{cq}$:

```
  width    ripple            synchronous
   4      22.0 ns  45.5 MHz   11.0 ns  90.9 MHz
   8      44.0 ns  22.7 MHz   13.0 ns  76.9 MHz
  16      88.0 ns  11.4 MHz   15.0 ns  66.7 MHz
  32     176.0 ns   5.7 MHz   17.0 ns  58.8 MHz
```

The two columns tell the whole story. The ripple counter halves its speed every time
you double the width, because the delay is $n\,t_{cq}$. The synchronous counter loses
one gate delay every time you double it, because the depth of a balanced AND tree is
$\log_2 n$. At four bits the difference is a factor of two; at thirty-two it is a factor
of ten, and it keeps growing.

One caution on that table: it assumes the toggle terms are built as balanced trees. The
lazy construction chains them instead — each stage ANDs its own $Q$ with the enable
handed up from the stage below — which uses the same number of gates and puts them all
in series, so the depth grows with $n$ rather than with $\log_2 n$. For 16 bits that is
fourteen gates end to end, 28 ns of logic rather than 8:

```
  width    ripple      synchronous, chain   synchronous, tree
   16     88.0 ns          35.0 ns               15.0 ns
   32    176.0 ns          67.0 ns               17.0 ns
```

The chained version is still faster than the ripple counter — 2.0 ns of gate beats
5.5 ns of flip-flop — but it scales the same way the ripple counter does, and scaling
was the entire reason for paying the gates. The gate count is identical in both
synchronous columns. The topology is the only difference.

## The mistake people actually make

**Believing the ripple counter's outputs are merely late.** They are not late, they are
*wrong*: for 40 ns after the edge they spell out numbers the counter is not at. Late
would be harmless — you would wait. Wrong means anything that reads them during the
window is misinformed, and the reason this catches people is that on an oscilloscope,
with a slow enough clock, it genuinely does look like the answer arriving a bit late.

**Decoding a ripple counter with a gate.** It follows from the mistake above and it is
the most common way a design that worked on the bench fails in the field. The count
passes through other counts on its way, and any gate watching for one of those will
fire.

**Assuming "synchronous" means "fast".** It does not, on its own. A synchronous counter
whose toggle logic is a chain of ANDs rather than a tree can easily be slower than the
ripple counter, as the caution above shows. What synchronous buys is that the outputs
are all correct at the same instant. Speed is a separate purchase, made with the
topology of the logic.

**Forgetting that the ripple counter's first stage still sees the full clock.** The
divider chain is cheap in gates but its first flip-flop toggles at $f/2$ regardless, and
in a fast system that one flip-flop can dominate the power. Cheap in area is not the
same as cheap in watts.

## Where these stop being enough

**When even a log-depth tree is too slow.** Above a few hundred megahertz the AND tree
stops fitting in the period, and the fix is a **prescaler**: a very short, very fast
counter — often two or three stages, sometimes a specialised divide-by-2 built from
current-mode logic rather than CMOS — divides the clock down first, and an ordinary wide
counter runs on its output. The wide counter never sees the fast clock. The price is
that the low bits of the count now live in the prescaler and are awkward to read, which
is why a frequency counter's least significant digits are the ones that cost money.

**When something on another clock has to read the count.** All the outputs of a
synchronous counter change together, which is a virtue right up until a circuit on an
unrelated clock samples them. It will sometimes sample during the transition, and it
will catch some bits new and some old — a 7 read halfway to 8 can come back as 15. What
replaces the binary count is a **Gray code**, in which exactly one bit changes per step.
A sample taken during a Gray transition catches that one bit either before or after, so
it reads either the old count or the new one and never a third thing. This is why every
FIFO that crosses a clock boundary keeps its pointers in Gray code.

**When you need to count in something other than twos.** Everything here counts to a
power of two, because that is what a stack of halvings does. Counting to ten, or to
12,000, needs logic that spots a particular value and intervenes — which is the next
reading.
''',
                },
                {
                    "title": "Stopping short, and counting without a count",
                    "minutes": 12,
                    "body": r'''
Everything so far counts to a power of two, because a chain of halvings has no other
option. Very little in the world comes in sixteens. Clocks want tens and sixties, a
display wants a digit, a servo wants 20 ms, a UART wants a bit period. So a counter
usually has to be persuaded to stop short — and, once you are willing to give up the
count itself, there is a much cheaper way to visit a great many states.

## Two ways to stop at N

A **modulo-$N$** counter runs $0, 1, \ldots, N-1, 0, \ldots$. Building one means
spotting the moment to go back to zero, and there are two moments to choose from. The
difference between them is not a matter of taste.

**Asynchronous clear** watches for $N$ itself. A decade counter — modulo 10 — lets the
count reach `1010`, and a gate watching for `1010` drives the flip-flops' clear inputs
directly. The clear does not wait for a clock edge; it acts the moment the gate decides.

**Synchronous clear** watches for $N-1$. The gate spots `1001` and, instead of clearing
anything, tells the next-state logic that the value after this one is zero. The
flip-flops go from 9 to 0 on the next ordinary clock edge, like any other step.

Both give a counter that runs 0 to 9. Only one of them is a circuit you should ship.

## Worked example: the decade counter that clears itself

Asynchronous clear, with a 12 ns clock-to-output, a decode gate at 8 ns, and 6 ns from
the clear input to the outputs going low.

```
 t =  0 ns   the clock edge that takes 9 to 10
 t = 12 ns   the outputs settle at        1010    <- the state that must not exist
 t = 20 ns   the decode gate falls, CLR asserted
 t = 26 ns   the outputs are cleared to   0000
 t = 34 ns   the decode gate releases, CLR removed
```

Two numbers come out of that timeline, and they are the same two delays measured from
different starting points.

The forbidden state `1010` sits on the output pins from 12 ns to 26 ns — **14 ns** of
a count that the counter is not supposed to be able to reach. Anything decoding these
outputs sees it.

The clear pulse itself lasts from 20 ns to 34 ns — also 14 ns, because it is
self-terminating: the pulse exists only until it has destroyed the condition that
created it. And that is the real hazard. A flip-flop's datasheet states a minimum clear
pulse width, 20 ns say. This pulse is 14 ns. Some flip-flops will clear and some will
not, decided by process variation and temperature, and the counter lands in a state that
is not 0 and not 10. Nothing warns you. The circuit works on the bench at 25 °C and
fails in the field, or works on one batch of parts and not the next.

The synchronous version has none of this. The gate spots `1001`, the next-state logic
produces zero, and on the next edge the outputs go from `1001` to `0000` together. There
is no forbidden state, no self-terminating pulse and no race, and the cost is that the
decode gate now sits on the critical path along with the toggle logic — it has to settle
within $T - t_{cq} - t_{su}$ like everything else.

There is one pleasant accident worth noticing in both versions. Over the states 0 to 9,
$Q_3$ is set only in 8 (`1000`) and 9 (`1001`), and $Q_0$ is set in 9 but not 8. So
`1001` is picked out uniquely by the two-input AND $Q_3 Q_0$, and `1010` by $Q_3 Q_1$.
Neither decode needs to look at all four bits, because most of the sixteen patterns
never occur. That is why a decade counter costs barely more than a plain 4-bit one, and
why decade counters exist as parts at all.

## Worked example: 10 MHz down to 1 kHz

Divide by 10,000. There are two ways to spend the gates.

**One wide counter.** 10,000 needs 14 bits, and a comparator watching for 9,999 has to
examine all fourteen of them — a 14-input match, three or four levels of logic, sitting
squarely on the critical path.

**Four decade counters in series.** Each divides by ten using the two-input decode
above, and $10^4 = 10{,}000$. The widest gate anywhere in the design has two inputs.

```
 10 MHz --> /10 --> 1 MHz --> /10 --> 100 kHz --> /10 --> 10 kHz --> /10 --> 1 kHz
```

The cascade is also more useful: the intermediate outputs are the other frequencies you
probably wanted, and each stage's four bits are already one decimal digit, ready for a
seven-segment decoder without any division. This is why bench instruments are built out
of decade counters. It is also the same instinct that produced the 32,768 Hz watch
crystal, applied to a different cheap stage: there the cheapest divider is by two, so
the frequency was chosen to be a power of two; here the cheapest *decimal* stage is a
decade counter, so the frequency is chosen to be a power of ten. Both times the number
was picked to suit the divider rather than the other way round.

## Dropping the requirement that it counts

Here is a question worth asking of any counter: what is the count actually *for*? Very
often it is not for arithmetic at all. A built-in memory test wants to sweep the address
space in an order that is *not* a straight ramp, because neighbouring addresses are
exactly where the interesting faults hide. A scrambler wants a repeatable
pseudo-random bit stream. A cheap timer wants to know when a fixed number of clocks have
gone by. In none of those does anything care that state 7 comes after state 6.

Give that up and the toggle logic — the AND tree that is the whole extra cost of a
synchronous counter — disappears. What replaces it is a **linear-feedback shift
register**: an ordinary shift register whose serial input is the XOR of a few of its own
bits.

```
              feedback = s3 XOR s4
                   |
                   v
                +----+   +----+   +----+   +----+
                | s1 |-->| s2 |-->| s3 |-->| s4 |
                +----+   +----+   +----+   +----+
                                     |        |
                                     +--------+---> to the XOR above
```

Two gate inputs for the whole machine, at any width. A 32-bit LFSR needs one XOR; a
32-bit synchronous counter needs a thirty-one-input AND tree and 31 more gates besides.

## Worked example: four bits, taps at 3 and 4

Number the stages $s_1$ to $s_4$ from the left, shift left to right, and feed
$s_3 \oplus s_4$ back into $s_1$. Start at `0001`.

```
  0001  ->  s3^s4 = 0^1 = 1  ->  1000
  1000  ->  0^0 = 0          ->  0100
  0100  ->  0^0 = 0          ->  0010
  0010  ->  1^0 = 1          ->  1001
  1001  ->  0^1 = 1          ->  1100
  1100  ->  0^0 = 0          ->  0110
  0110  ->  1^0 = 1          ->  1011
  1011  ->  1^1 = 0          ->  0101
  0101  ->  0^1 = 1          ->  1010
  1010  ->  1^0 = 1          ->  1101
  1101  ->  0^1 = 1          ->  1110
  1110  ->  1^0 = 1          ->  1111
  1111  ->  1^1 = 0          ->  0111
  0111  ->  1^1 = 0          ->  0011
  0011  ->  1^1 = 0          ->  0001   <- back to the start
```

Fifteen states, every one of them different, and then it repeats. Read them as numbers —
1, 8, 4, 2, 9, 12, 6, 11, 5, 10, 13, 14, 15, 7, 3 — and there is no pattern a person
would guess, yet the sequence is completely determined and reproducible on any two
copies of the circuit.

## Why fifteen and not sixteen

One state is missing, and it has to be. The feedback is an XOR of state bits, and XORing
zeros gives zero, so `0000` maps to `0000`. It is a fixed point: the register can never
leave it, and — since every state has exactly one predecessor — it can never be entered
from anywhere else either. It sits outside the cycle entirely.

So the best an $n$-bit LFSR can do is $2^n - 1$ states, and a tap set that achieves it
is called **maximal length**. Which tap sets do is not obvious and is not guessed: the
taps correspond to the coefficients of a polynomial over the two-element field, and the
sequence is maximal exactly when that polynomial is primitive. Taps 3 and 4 above give
$x^4 + x^3 + 1$, which is primitive, hence fifteen. Taps 1 and 2 give a polynomial that
is not, and the damage is immediate rather than subtle: from `0001`, $s_1 \oplus s_2 =
0 \oplus 0 = 0$, so the next state is `0000` and the register is dead in a single clock.
In practice you look the taps up in a table, and it is one of the few places in digital
design where that is the correct professional response.

## The mistake people actually make

**Using an LFSR where the order matters.** The states are all distinct, so an LFSR is a
perfect address generator for a memory test and a perfect "has $2^n-1$ clocks gone by"
timer. It is useless the moment anything wants to compare two counts, work out how far
apart they are, or display the value, because its state is not the number of clocks
elapsed in any usable sense. Reaching for one because it is cheap, in a design that
later needs to know *how many*, means throwing it away.

**Seeding an LFSR with zero.** It is the obvious reset value, it is what every other
register in the design resets to, and here it is the one state that does not work. The
register comes out of reset dead and stays dead, and it looks exactly like a clock
failure. Reset it to anything else.

**Using the asynchronous clear because it needs one fewer gate.** It genuinely is
simpler to draw, and it genuinely does work most of the time, which is precisely what
makes it dangerous. The forbidden state is on the pins for real nanoseconds and the
clear pulse is too narrow to be reliable.

**Assuming an LFSR is random.** The output passes casual statistical tests, which is
what makes it tempting for anything wanting "random-looking" bits. It is entirely
predictable: observing $2n$ consecutive output bits is enough to recover both the state
and the tap positions by solving a linear system — the Berlekamp-Massey algorithm — and
after that the whole future and past of the sequence is known. Good for a scrambler,
good for a bit-error-rate test, useless for anything that must not be predicted.

## Where these stop being enough

**When N must change while it runs.** A hard-wired decode counts to one fixed number. A
timer whose period is set by software needs a comparator against a *register* rather
than against a constant, and a load path so the counter can be reset to zero or preset
to a value. That is what every microcontroller timer peripheral is, and its period
register is why it can generate any frequency and not just one.

**When the period must not be a whole number of clocks.** Divide a 10 MHz clock by
practically anything and the answer is a whole number of 100 ns ticks; ask for 44.1 kHz
and there is no integer that does it. What replaces the counter there is a
**fractional-N** scheme: alternate between dividing by $k$ and by $k+1$ in a ratio that
averages out, and accept jitter on the individual edges in exchange for a long-run
average that is exact. That is the accumulator inside a direct digital synthesiser and
the divider inside a modern phase-locked loop.

**When one counter is not enough to know where you are.** A counter tells you how many
clocks have passed. It cannot tell you what the machine should do next, because a
sequence of events is not usually a sequence of numbers. What replaces it is a state
machine with an arbitrary state graph, in which a counter is the special case whose
graph happens to be a single cycle with no choices in it — and that is the next module.
''',
                },
            ],
            "quiz": {
                "title": "Holding, shifting and counting",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Eight flip-flops share one clock and hold a byte. What does loading them on a single clock edge guarantee?",
                        "opts": [
                            "That the byte cannot be read while it is being written",
                            "That all eight bits change at the same instant, so no partly-updated byte is ever visible downstream",
                            "That the byte is stored in two places for safety",
                            "That the clock can be made faster",
                        ],
                        "a": 1,
                        "why": (
                            "Atomicity is the property being bought. Eight independent latches would each let "
                            "their bit through whenever their own enable happened to be high, and anything "
                            "reading the group could catch a mixture of the old value and the new one. One "
                            "edge for all eight makes that impossible. Nothing here stops a reader looking "
                            "while a write happens — it just guarantees that what they see is one value or "
                            "the other."
                        ),
                    },
                    {
                        "q": "A 4-bit shift register holds `1011` and shifts one place left, with a 0 fed in at the right. What does it hold after the edge?",
                        "opts": ["`0110`", "`1101`", "`0101`", "`1011`"],
                        "a": 0,
                        "why": (
                            "Every bit moves one place left, the leftmost 1 falls off the end, and the 0 "
                            "arrives at the right: `0110`. Shifting the other way, with a 0 fed in at "
                            "the left, would give `0101`; `1101` is not a shift at all but a rotation, "
                            "with the bit that falls off the end brought back round to the front. "
                            "Read as numbers, 11 has become 6 rather than 22 — and the missing 16 is exactly "
                            "the bit that fell off, which is what \"multiply by two\" means in a register "
                            "that cannot grow."
                        ),
                    },
                    {
                        "q": "A 4-bit ripple counter with 10 ns per flip-flop goes from `0111` to `1000`. What do its four outputs read 15 ns after the clock edge?",
                        "opts": [
                            "`1000`, the final answer",
                            "`0111`, still unchanged",
                            "`0110`, a value the counter never intended to show",
                            "Nothing — the outputs are floating while the chain settles",
                        ],
                        "a": 2,
                        "why": (
                            "Only the first stage sees the clock. It flips at 10 ns, taking `0111` to `0110`; "
                            "the second stage flips at 20 ns, the third at 30 and the fourth at 40. At 15 ns "
                            "exactly one stage has moved, so the outputs read `0110` — which is six, a value "
                            "the count is passing through rather than stopping at. The outputs are driven the "
                            "whole time; they are simply not all correct at the same moment, which is the "
                            "price of the cheap counter."
                        ),
                    },
                    {
                        "q": "Why does a synchronous counter need more logic than a ripple counter of the same width?",
                        "opts": [
                            "It needs more flip-flops",
                            "Every stage needs combinational logic deciding whether it toggles this cycle, because no stage is allowed to wait for another",
                            "It needs a faster clock to keep the stages in step",
                            "It needs a decoder on its outputs",
                        ],
                        "a": 1,
                        "why": (
                            "Both counters use the same number of flip-flops. The difference is what tells "
                            "each one to toggle: in the ripple counter that job is done for free by the "
                            "previous stage's output, and in the synchronous counter it has to be computed "
                            "from all the lower bits, since bit $k$ toggles only when every bit below it is "
                            "1. That AND chain is the extra hardware, and what it buys is outputs that are "
                            "all correct at the same instant."
                        ),
                    },
                    {
                        "q": "A 4-bit maximal-length LFSR cycles through how many states?",
                        "opts": [
                            "16 — every state, like a counter",
                            "15 — every state except all-zeros",
                            "15 — every state except all-ones",
                            "8 — half the states, in a scrambled order",
                        ],
                        "a": 1,
                        "why": (
                            "The feedback bit is an XOR of some of the state bits, and XORing zeros gives "
                            "zero, so all-zeros maps to itself: it is a trap the register can never leave and "
                            "never enter. The other 15 states form a single cycle, visited in an order that "
                            "looks random and is completely determined. All-ones is an ordinary state with "
                            "nothing special about it."
                        ),
                    },
                ],
            },
            "blanks": [
                {
                    "title": "One edge, one place",
                    "minutes": 8,
                    "brief": r'''
A 4-bit serial-in, parallel-out shift register, starting at all zeros. The stages are
written $Q_0\,Q_1\,Q_2\,Q_3$ from left to right; the serial input feeds $Q_0$, and each
stage hands its value to its right-hand neighbour on every edge.

Nothing runs here. You are filling in a timeline and one inequality.
''',
                    "caption": "four edges, and the skew the chain will tolerate",
                    "lang": "text",
                    "listing": r'''
Serial in -> Q0 -> Q1 -> Q2 -> Q3      one clock, all four stages

    edge   bit in     Q0 Q1 Q2 Q3
     -        -        0  0  0  0
     1        1        1  0  0  0
     2        0        0  1  0  0
     3        1        ___
     4        1        1  1  0  1

After the fourth edge the bit that arrived FIRST is held by  ___ .

Why one edge moves the word one place and not four:

    a stage's output changes    t_cq = 5.0 ns after its own clock edge
    a stage's input must hold   t_h  = 1.5 ns after its own clock edge

    so a stage captures its neighbour's ___ value

    and the skew between two neighbouring clocks may be at most  ___ ns

Shifting left, in four bits:

    0011  =  3   ->   0110  =  ___
    1011  = 11   ->   0110  =   6, because 22 does not fit and ___
''',
                    "blanks": [
                        {
                            "prompt": "Edge 3 clocks a 1 in while the register holds `0 1 0 0`. What comes out?",
                            "opts": ["1  0  1  0", "1  1  0  0", "0  0  1  0", "1  0  0  1"],
                            "a": 0,
                            "why": (
                                "Everything moves one place right and the new bit lands in $Q_0$: the 0 "
                                "in $Q_0$ goes to $Q_1$, the 1 in $Q_1$ goes to $Q_2$, and the arriving "
                                "1 takes $Q_0$. So `1 0 1 0`. `1 1 0 0` would be the answer if the "
                                "register shifted the other way, and `0 0 1 0` forgets to load the new "
                                "bit at all."
                            ),
                        },
                        {
                            "prompt": "The first bit arrived four edges ago and has been pushed along ever since.",
                            "opts": ["Q0", "Q1", "Q2", "Q3"],
                            "a": 3,
                            "why": (
                                "It has moved one place on each of four edges, so it is as far from the "
                                "input as it can get: $Q_3$. $Q_0$ holds the bit that arrived most "
                                "recently. This is why a serial link has to agree which end is which — "
                                "read $Q_0$ to $Q_3$ and you get `1101`, read $Q_3$ to $Q_0$ and you "
                                "get `1011`, which is the order the bits were actually sent in. Two "
                                "devices that disagree about it exchange bytes that are bit-reversed "
                                "rather than garbled, which is a much harder bug to see."
                            ),
                        },
                        {
                            "prompt": "The hold window shuts at 1.5 ns; the neighbour's new value does not appear until 5.0 ns.",
                            "opts": ["new", "old"],
                            "a": 1,
                            "why": (
                                "The capture is finished 1.5 ns after the edge and the neighbour's "
                                "output does not change until 5.0 ns after it, so what every stage "
                                "captured was the value its neighbour held *before* this edge. That is "
                                "the entire reason the word advances one place instead of racing down "
                                "the chain: the flip-flops are slower to change than they are to "
                                "capture, and here that slowness is the mechanism rather than the cost."
                            ),
                        },
                        {
                            "prompt": "Skew $\\Delta$ delays a stage's clock. Safety needs $t_{cq} \\ge \\Delta + t_h$.",
                            "opts": ["6.5", "5.0", "3.5", "1.5"],
                            "a": 2,
                            "why": (
                                "$\\Delta \\le t_{cq} - t_h = 5.0 - 1.5 = 3.5$ ns. Past that, a stage "
                                "closes its hold window after its neighbour's new value has already "
                                "arrived, so it captures the new value instead of the old one and the "
                                "bit travels two places on one edge — the register drops a bit out of "
                                "every word. Note what is missing from that inequality: the clock "
                                "period. Slowing the clock down does not help, because neither $t_{cq}$ "
                                "nor $t_h$ depends on it."
                            ),
                        },
                        {
                            "prompt": "`0011` is 3, and every bit has moved into a column worth twice as much.",
                            "opts": ["6", "1", "12", "3"],
                            "a": 0,
                            "why": (
                                "Each column of a binary number is worth twice the one to its right, so "
                                "moving every bit one place left doubles the value: $3 \\times 2 = 6$, "
                                "and `0110` is indeed 6. Shifting *right* would halve it, giving 1 with "
                                "the odd bit lost off the bottom."
                            ),
                        },
                        {
                            "prompt": "11 shifted left should be 22, and 22 is not a four-bit number.",
                            "opts": [
                                "the bit that was worth 8 moved to a column worth 16, which does not exist, so 16 is lost",
                                "the register rounds down to the nearest value it can hold",
                                "the shift stops early when the top bit is already 1",
                            ],
                            "a": 0,
                            "why": (
                                "$22 - 16 = 6$, and the missing 16 is exactly the bit that fell off the "
                                "end. A left shift is a multiply by two **modulo $2^n$** — the same "
                                "modulus the adder of module 7 works in, for the same reason: the top "
                                "column has nowhere to carry to. Nothing rounds and nothing stops "
                                "early; the register does the multiplication faithfully and then loses "
                                "the part of the answer it has no column for."
                            ),
                        },
                    ],
                },
                {
                    "title": "The count, and the moments it is not the count",
                    "minutes": 9,
                    "brief": r'''
A 4-bit ripple counter with 10 ns per flip-flop, stepping from 7 to 8 — the worst
transition there is, because every stage has to flip. Outputs are written
$Q_3\,Q_2\,Q_1\,Q_0$, most significant first.

Then the same width done synchronously, and the same chain used as a divider.
''',
                    "caption": "0111 to 1000, ten nanoseconds at a time",
                    "lang": "text",
                    "listing": r'''
Only Q0 is clocked by the clock.  Each other stage is clocked by its neighbour.

    t =  0 ns   the clock edge          0 1 1 1   = 7
    t = 10 ns   Q0 falls                0 1 1 0   = 6
    t = 20 ns   Q1 falls                0 1 0 0   = ___
    t = 30 ns   Q2 falls                0 0 0 0   = 0
    t = 40 ns   Q3 rises                1 0 0 0   = 8

    counts the outputs pass through on the way from 7 to 8:   ___
    the pins read something other than 8 for                   ___ ns

Same four bits, clocked synchronously instead:

    bit 0 toggles   always
    bit 1 toggles   when Q0 = 1
    bit 3 toggles   when ___

Same four stages, used as a divider, clocked at 12 MHz:

    Q0 = 6 MHz    Q1 = 3 MHz    Q2 = 1.5 MHz    Q3 = ___
''',
                    "blanks": [
                        {
                            "prompt": "`0 1 0 0` — take the places that are set.",
                            "opts": ["2", "4", "6", "8"],
                            "a": 1,
                            "why": (
                                "Only the fours place is set, so the pins are spelling out 4. The "
                                "counter is on its way from 7 to 8 and has never been at 4 during this "
                                "step, yet the outputs are firmly driven at valid logic levels saying "
                                "so. They are not floating and they are not noise; they are wrong."
                            ),
                        },
                        {
                            "prompt": "Not counting 7 at the start or 8 at the end, how many different values appear?",
                            "opts": ["0", "1", "3", "4"],
                            "a": 2,
                            "why": (
                                "6 at 10 ns, 4 at 20 ns and 0 at 30 ns — three of them, each on the "
                                "pins for a full 10 ns. Every one is a value the counter really does "
                                "visit at other times, which is what makes them dangerous: a gate "
                                "decoding zero cannot tell this passing `0000` from the real one. The "
                                "outputs sweep through `0000` on the way into 2, into 4 and into 8 as "
                                "well — every crossing into a power of two — so that decoder emits "
                                "three false pulses in every sixteen counts, forever."
                            ),
                        },
                        {
                            "prompt": "The last stage settles four flip-flop delays after the edge.",
                            "opts": ["10", "30", "40", "0"],
                            "a": 2,
                            "why": (
                                "$4 \\times 10 = 40$ ns. Nothing may believe these outputs until then, "
                                "which caps the clock at $1/40\\,\\text{ns} = 25$ MHz — and the cap gets "
                                "worse in proportion to the width, because the delay is $n\\,t_{cq}$. "
                                "Eight stages of the same part is 80 ns and 12.5 MHz."
                            ),
                        },
                        {
                            "prompt": "A column flips when every column below it is about to roll over.",
                            "opts": [
                                "Q0, Q1 and Q2 are all 1",
                                "Q2 is 1",
                                "Q0 is 1",
                                "Q0, Q1, Q2 and Q3 are all 1",
                            ],
                            "a": 0,
                            "why": (
                                "$T_3 = Q_0 Q_1 Q_2$: bit 3 toggles only when everything below it is at "
                                "its maximum and therefore about to carry, which happens once every "
                                "eight counts. Watching $Q_2$ alone would toggle it twice as often as "
                                "it should. Including $Q_3$ itself is a different mistake — a bit never "
                                "consults its own value to decide whether to toggle, only the ones "
                                "below it. That AND chain is the whole extra cost of going synchronous, "
                                "and what it buys is outputs that are all correct at the same instant."
                            ),
                        },
                        {
                            "prompt": "Each stage halves the frequency of the one before it.",
                            "opts": ["750 kHz", "3 MHz", "1.5 MHz", "375 kHz"],
                            "a": 0,
                            "why": (
                                "Four halvings: $12\\,\\text{MHz} / 2^4 = 750$ kHz. Read as a divider "
                                "the chain costs four flip-flops and no gates at all, and the 40 ns of "
                                "settling that ruins it as a counter is irrelevant here, because "
                                "nothing looks at the intermediate stages. This is the ripple counter "
                                "at its best, and it is why a watch crystal runs at 32,768 Hz — that is "
                                "$2^{15}$, so fifteen toggle flip-flops turn it into exactly one pulse "
                                "a second."
                            ),
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Twenty-four outputs down three wires",
                    "minutes": 5,
                    "brief": r'''
The bottom rung, and the reason shift registers are in almost every hobby project ever
built.

Three 8-bit shift registers are daisy-chained: the serial output of the first feeds the
serial input of the second, and so on. The controller has three pins on the whole
arrangement — data, clock, and a latch that copies the shift register into an output
register so the LEDs do not flicker while the word is walking through.

To refresh the display, the controller pushes 24 bits down the data pin, one bit per
clock edge, and then pulses the latch. One rule and one arithmetic step.
''',
                    "prompt": "How long does it take to shift one complete 24-bit frame into the chain?",
                    "note": "Give the answer in microseconds. Ignore the latch pulse.",
                    "figure": r'''
```
 data  ---> [ 8-bit SR ] ---> [ 8-bit SR ] ---> [ 8-bit SR ]
 clock ----------+-----------------+-----------------+
 latch ----------+-----------------+-----------------+
                 |                 |                 |
               8 LEDs            8 LEDs            8 LEDs
```
The three registers behave as one 24-stage shift register: the clock is common, and a
bit entering the first stage reaches the last one 24 edges later.
''',
                    "given": [
                        {"label": "Stages in the chain", "value": "24 (three 8-bit registers)"},
                        {"label": "Serial clock", "value": "4 MHz"},
                        {"label": "Bits moved per clock edge", "value": "1"},
                    ],
                    "answer": 6,
                    "tol": 0.05,
                    "unit": "µs",
                    "aside": "At 6 µs a frame the link could refresh the display 166,000 times a "
                             "second. Whatever eventually limits the frame rate of a display driven "
                             "this way, it is not the shift register.",
                    "hint": "One edge moves one bit, so the whole frame takes 24 clock periods. A "
                            "4 MHz clock has a period of 250 ns.",
                    "wrong": "2 µs is one register rather than the chain — the three share a clock, so "
                             "they are 24 stages, not 8. 96 µs multiplies by four instead of dividing, "
                             "which is what happens when 4 MHz is used as though it were a period.",
                    "why": (
                        "A 4 MHz clock has a period of $1/4\\,\\text{MHz} = 250$ ns, one bit goes in per "
                        "edge, and there are 24 of them: $24 \\times 250\\,\\text{ns} = 6\\ \\mu$s.\n\n"
                        "Two things are worth taking from a number that small. The obvious one is the "
                        "trade being made: 24 outputs are being driven by 3 pins, and the whole cost is "
                        "6 µs of serialising. A parallel bus would need 24 wires, 24 pins and 24 pads, "
                        "and would deliver the frame in 250 ns — forty times faster, for eight times the "
                        "copper, in a job where nothing whatever needed the speed.\n\n"
                        "The less obvious one is that the chain is 24 stages regardless of how it is "
                        "packaged. Nothing in the circuit knows where one chip ends and the next "
                        "begins; the serial output of a shift register is simply its last stage's Q, "
                        "so cascading them makes one longer register with one shared clock. That is "
                        "also why the bit you send first ends up furthest along the chain, in the "
                        "*last* register — get that backwards and the display lights up in three "
                        "blocks of the wrong eight."
                    ),
                },
                {
                    "title": "How fast can a ripple counter be read?",
                    "minutes": 7,
                    "brief": r'''
The ripple counter's cheapness has a price, and it is not subtle once you look for
it. Every stage waits for the one before it, so the width of the counter turns
directly into the time before anybody may believe its outputs.
''',
                    "prompt": "What is the highest clock frequency at which all four outputs have finished settling before the next clock edge arrives?",
                    "note": "Give the answer in megahertz.",
                    "figure": r'''
Four toggle flip-flops in a chain: `clk → Q0 → Q1 → Q2 → Q3`. Only the first
flip-flop is connected to the clock; each of the other three is clocked by the output
of the one before it. That is the whole circuit — no next-state logic anywhere, which
is what makes it cheap.
''',
                    "given": [
                        {"label": "Width", "value": "4 bits"},
                        {"label": "Type", "value": "ripple (asynchronous)"},
                        {"label": "Clock to output, each flip-flop", "value": "10 ns"},
                        {"label": "Setup time", "value": "neglected"},
                    ],
                    "answer": 25,
                    "tol": 0.5,
                    "unit": "MHz",
                    "aside": "The same 40 ns is the width of the window in which the outputs are showing a number the counter never meant to produce.",
                    "hint": "Count how many flip-flops the change has to pass through in the worst case, add up their delays, and turn the total into a frequency.",
                    "wrong": "100 MHz is one flip-flop's delay rather than the chain's. 40 is the settling time in nanoseconds, not the frequency in megahertz — invert it.",
                    "why": (
                        "The worst case is the count from `0111` to `1000`, where every stage has to flip in "
                        "turn: the first output moves 10 ns after the clock edge, the second 10 ns after that, "
                        "and so on, so the last one settles $4 \\times 10 = 40$ ns after the edge. A 40 ns period "
                        "is 25 MHz.\n\n"
                        "Two things are worth carrying away. The chain gets one stage longer for every bit "
                        "added, so the same flip-flops in an 8-bit ripple counter give 80 ns and 12.5 MHz — the "
                        "limit halves as the counter doubles. And a synchronous counter of any width settles in "
                        "one clock-to-output delay plus one pass through its next-state logic, because every "
                        "stage is clocked at the same instant. That is what the extra gates are for."
                    ),
                },
                {
                    "title": "How much of the chatter survives the filter",
                    "minutes": 9,
                    "brief": r'''
The tuning exercise in this module asks you to *choose* an $R$ and a $C$ that swallow
the contact bounce without blunting the press. This asks what a particular choice
actually does, which is the same physics run in the other direction.

A push-button pulls the node at the left of the resistor between 0 V and the 3.3 V rail.
A deliberate press is slow — a fast finger manages about five a second. The chatter is
not: the contacts bounce apart and back together in a burst of pulses roughly a
millisecond long, and the counter on the far side of this filter is perfectly happy to
treat every one of those as a clock edge.

Treat the chatter as a sinusoid at 1 kHz swinging the full rail. It is not really a
sinusoid — it is a burst of ragged pulses — but its energy sits around there, and this
is where the filter has to earn its place.

Two steps beyond the last question: the reactance of the capacitor depends on
frequency, so the divider ratio does too.
''',
                    "prompt": "What amplitude does the 1 kHz chatter still have at the probed node?",
                    "note": "Give the answer in millivolts. The logic input on the far side switches at about half the rail.",
                    "diagram": {
                        "parts": [
                            {"id": "vsw", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rf", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3},
                            {"id": "cf", "kind": "C", "x": 9, "y": 5, "rot": 1, "value": 1e-6},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 8},
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
                    "given": [
                        {"label": "Chatter at the button", "value": "1 kHz, 3.3 V amplitude"},
                        {"label": "Series resistor", "value": "10 kΩ"},
                        {"label": "Capacitor to ground", "value": "1 µF"},
                        {"label": "Logic threshold on the far side", "value": "about 1.65 V"},
                    ],
                    "answer": 52.51,
                    "tol": 0.3,
                    "unit": "mV",
                    "check": r'''
return c.gain(1000) * 1000;
''',
                    "aside": "The same network passes 95% of a 5 Hz press. One filter, two frequencies, "
                             "and the ratio between what it does to each is the entire design.",
                    "hint": "It is a divider between $R$ and the capacitor's reactance "
                            "$1/\\omega C$, so $|H| = 1/\\sqrt{1 + (\\omega R C)^2}$. Work out "
                            "$\\omega = 2\\pi f$ first.",
                    "wrong": "1.65 V is what you get by treating the capacitor as an open circuit and "
                             "reading a resistive divider — but at 1 kHz its reactance is 159 Ω against "
                             "a 10 kΩ resistor, so it is very nearly a short. 3.3 V is the answer with "
                             "no filter at all, which is the situation the filter exists to fix.",
                    "why": (
                        "$\\omega = 2\\pi \\times 1000 = 6283$ rad/s, so $\\omega RC = 6283 \\times "
                        "10^4 \\times 10^{-6} = 62.83$. Then\n\n"
                        "$$|H| = \\frac{1}{\\sqrt{1 + (\\omega R C)^2}} = "
                        "\\frac{1}{\\sqrt{1 + 3948}} = \\frac{1}{62.84} = 0.01591$$\n\n"
                        "and $3.3\\ \\text{V} \\times 0.01591 = 52.5$ mV. That is 36 dB down, and — the "
                        "number that actually matters — it is nowhere near the 1.65 V the logic input "
                        "needs to see before it will call anything an edge. The chatter cannot fake a "
                        "clock, so the counter counts one press once.\n\n"
                        "Now run the same expression at 5 Hz, which is the press itself: $\\omega RC = "
                        "0.314$, so $|H| = 1/\\sqrt{1 + 0.0987} = 0.954$. The press keeps 95% of its "
                        "amplitude while the chatter keeps 1.6%, and the reason the filter can do both "
                        "at once is that the two live two and a half decades apart. The corner sits at "
                        "$f_c = 1/(2\\pi RC) = 15.9$ Hz, comfortably above the press and far below the "
                        "chatter.\n\n"
                        "Where this stops working is when the two are not far apart. A key held down "
                        "and released quickly, or a rotary encoder turned fast, produces real edges at "
                        "hundreds of hertz, and no first-order filter separates those from a bounce at "
                        "1 kHz — one pole rolls off at 20 dB per decade, so half a decade of separation "
                        "buys 10 dB and nothing more. What replaces the filter there is a counter: "
                        "sample the input on a slow clock and only believe a change that has held for "
                        "several samples in a row. That is a shift register and an AND gate, and it "
                        "costs no analogue parts at all."
                    ),
                },
                {
                    "title": "Where a counter's power actually goes",
                    "minutes": 11,
                    "brief": r'''
The top of the ladder. Nothing here is hard on its own; the work is in noticing that
the sixteen outputs do not all switch at the same rate, and that the biggest consumer
in the circuit is not one of them.

Module 5 established that taking a node up to $V$ and back down again dissipates
$CV^2$ joules, whatever the path taken. So the switching power of any node is $CV^2$
times the number of complete cycles it makes per second — and in a binary counter every
bit cycles at a different rate. Bit 0 completes a cycle every two clock periods; bit 1
every four; bit $k$ every $2^{k+1}$.

One node in the circuit is not part of the count and cycles at the full clock rate on
every period: the clock net itself, which has to reach all sixteen flip-flops. Its
capacitance is given below alongside theirs.

Ignore the next-state logic, and ignore leakage. This is the dynamic power of the
sixteen outputs plus the clock.
''',
                    "prompt": "What total dynamic power does the counter dissipate?",
                    "note": "Give the answer in microwatts, to two decimal places.",
                    "figure": r'''
A 16-bit **synchronous** counter: one clock net reaching all sixteen flip-flops, and
sixteen outputs $Q_0 \ldots Q_{15}$ each driving a load of its own.

```
              +--------------------------------+
   clock ---> | 16 flip-flops, common clock    | ---> Q0   (cycles at f/2)
              |                                | ---> Q1   (cycles at f/4)
              |  next-state logic: ignore it   | ---> ...
              +--------------------------------+ ---> Q15  (cycles at f/65536)
```

The clock net is one node. It goes high and low once per clock period, so it completes
$f$ complete cycles a second — more than any output in the circuit.
''',
                    "given": [
                        {"label": "Width", "value": "16 bits"},
                        {"label": "Clock frequency", "value": "100 MHz"},
                        {"label": "Supply", "value": "1.8 V"},
                        {"label": "Capacitance on each output node", "value": "12 fF"},
                        {"label": "Capacitance of the whole clock net", "value": "128 fF"},
                        {"label": "Energy per full up-and-down cycle of a node", "value": "C V²"},
                    ],
                    "answer": 45.36,
                    "tol": 0.15,
                    "unit": "µW",
                    "aside": "The top eight bits account for 0.4% of the switching power in the "
                             "outputs, and the outputs account for 8.6% of the total. Almost all of a "
                             "counter's power is the clock arriving, not the counting.",
                    "hint": "The outputs sum to $CV^2f(\\tfrac12 + \\tfrac14 + \\cdots + 2^{-16})$, and "
                            "that bracket is $1 - 2^{-16}$, which is 1 to five decimal places. The "
                            "clock is a separate $C_{clk}V^2f$.",
                    "wrong": "3.89 µW is the counting on its own, with the clock left out — and it is "
                             "the smaller half of the answer by a long way. 103.7 µW comes from "
                             "assuming all sixteen outputs cycle at the clock rate; only bit 0 comes "
                             "close, and it manages half.",
                    "why": (
                        "**The outputs.** Bit $k$ completes $f/2^{k+1}$ cycles a second and each costs "
                        "$CV^2$, so the sixteen together come to\n\n"
                        "$$P_Q = CV^2 f\\left(\\tfrac12 + \\tfrac14 + \\cdots + 2^{-16}\\right) "
                        "= CV^2 f\\left(1 - 2^{-16}\\right)$$\n\n"
                        "```\n"
                        " C V^2 f = 12e-15 x 1.8^2 x 100e6 = 3.888e-6 W\n"
                        " x (1 - 2^-16) = x 0.9999847     = 3.888e-6 W   (3.888 uW)\n"
                        "```\n\n"
                        "The correction for the missing $2^{-16}$ is fifteen parts in a million. Every "
                        "bit above about the eighth contributes nothing you could measure.\n\n"
                        "**The clock.** One node, 128 fF, one full cycle every clock period:\n\n"
                        "```\n"
                        " C_clk V^2 f = 128e-15 x 3.24 x 100e6 = 41.472e-6 W   (41.47 uW)\n"
                        "```\n\n"
                        "**Together:** $3.888 + 41.472 = 45.36\\ \\mu$W, and the counting is 8.6% of "
                        "it.\n\n"
                        "That ratio is the point of the question. A counter's power is almost entirely "
                        "clock, for two reasons that compound: the clock net is physically the biggest "
                        "piece of copper in the block because it has to reach every flip-flop, and it "
                        "is the only node that cycles on every single period. Everything else halves, "
                        "and halves again, all the way up.\n\n"
                        "Two consequences follow directly. Widening the counter is nearly free — going "
                        "from 16 bits to 32 adds $CV^2f\\,(2^{-16} - 2^{-32})$ to the outputs, which "
                        "works out at 0.06 nW, though it does add sixteen more clock loads. And "
                        "the way to make a counter cheap is to stop the clock, not to shorten the "
                        "count: gating the clock at the root of its tree when the block is idle removes "
                        "the 41 µW outright, which is why every low-power design does it and why the "
                        "load-enable multiplexer from the first reading — which keeps the clock running "
                        "and merely recirculates the data — saves nothing at all in power. It was never "
                        "for that."
                    ),
                },
            ],
            "derive": {
                "title": "Why widening a counter costs almost no extra power",
                "minutes": 12,
                "brief": r'''
Module 5 established that driving a node from 0 up to $V$ and back down again
dissipates $CV^2$ joules — all of it, however fast or slow you do it. So the switching
power of any one node is $CV^2$ multiplied by the number of complete up-and-down cycles
it makes per second.

A binary counter is $n$ nodes, each cycling at a different rate. Adding those rates up
is the whole of this derivation, and the answer is more useful than it looks: it says
where a counter's power actually goes, and it is not where people expect.

Write $C$ for the capacitance of one output node, $V$ for the supply, $f$ for the clock
frequency and $n$ for the width.
''',
                "vars": ["C", "V", "f", "n", "k"],
                "steps": [
                    {
                        "prompt": "Bit 0 changes state on every active clock edge, so it takes two clock periods to go from 0 up to 1 and back to 0. Write the frequency at which bit 0 completes a full cycle.",
                        "answer": "\\frac{f}{2}",
                        "placeholder": "something over 2",
                        "hint": "One full cycle spans two clock periods, so the cycle rate is half the clock rate.",
                        "deconstruct": [
                            "One period of the clock takes bit 0 from 0 to 1; the next takes it back to 0.",
                            "Two clock periods per cycle means the cycle frequency is $f/2$.",
                        ],
                    },
                    {
                        "prompt": "Bit 1 changes only when bit 0 rolls over, so it cycles half as often again, and so on up the register. Write the cycle frequency of bit $k$, counting bit 0 as $k = 0$.",
                        "given": "Bit 0 cycles at $f/2$, bit 1 at $f/4$, bit 2 at $f/8$.",
                        "answer": "\\frac{f}{2^{k+1}}",
                        "hint": "Each bit halves the one below it, and bit 0 has already halved once.",
                        "deconstruct": [
                            "Bit $k$ has been halved $k$ times relative to bit 0.",
                            "Bit 0 is already $f/2$, so bit $k$ is $f/2^{k+1}$.",
                        ],
                    },
                    {
                        "prompt": "Each output node has capacitance $C$ and swings the full $V$, so each of its cycles costs $CV^2$. Write the switching power of bit $k$ on its own.",
                        "answer": "\\frac{C V^2 f}{2^{k+1}}",
                        "hint": "Power is energy per cycle multiplied by cycles per second.",
                        "deconstruct": [
                            "Energy per cycle is $CV^2$.",
                            "Cycles per second is $f/2^{k+1}$ from the previous step.",
                            "Multiply them.",
                        ],
                    },
                    {
                        "prompt": "Adding that over $k = 0, 1, \\ldots, n-1$ means summing $\\tfrac{1}{2} + \\tfrac{1}{4} + \\cdots + 2^{-n}$. Write that sum in closed form, in terms of $n$.",
                        "given": "A geometric series with first term $\\tfrac{1}{2}$ and ratio $\\tfrac{1}{2}$, with $n$ terms: $a(1 - r^n)/(1 - r)$.",
                        "answer": "1 - 2^{-n}",
                        "placeholder": "1 minus something small",
                        "hint": "Substitute $a = r = \\tfrac{1}{2}$; the denominator is $\\tfrac{1}{2}$ as well, so it cancels the first term.",
                        "deconstruct": [
                            "$a(1 - r^n)/(1 - r)$ with $a = r = \\tfrac{1}{2}$ is $\\tfrac{1}{2}(1 - 2^{-n})/\\tfrac{1}{2}$.",
                            "The halves cancel, leaving $1 - 2^{-n}$.",
                            "Sanity check: two terms give $\\tfrac{1}{2} + \\tfrac{1}{4} = \\tfrac{3}{4}$, and $1 - 2^{-2} = \\tfrac{3}{4}$.",
                        ],
                    },
                    {
                        "prompt": "Put the two together and write the total switching power of the whole $n$-bit counter.",
                        "answer": "C V^2 f (1 - 2^{-n})",
                        "hint": "$CV^2f$ is common to every term; what is left is the sum you just closed.",
                        "deconstruct": [
                            "The total is $\\sum_k CV^2 f / 2^{k+1}$.",
                            "Take $CV^2f$ outside the sum.",
                            "What remains inside is $1 - 2^{-n}$.",
                        ],
                    },
                ],
                "closing": r'''
$$P = C V^2 f \left(1 - 2^{-n}\right)$$

Put some widths into that bracket:

```
  n =  1    0.5
  n =  2    0.75
  n =  4    0.9375
  n =  8    0.99609
  n = 16    0.9999847
  n = 24    0.99999994
```

It climbs towards 1 and never reaches it. So the outputs of an entire counter, at any
width whatever, dissipate **less than $CV^2f$** — less than a single node driven at the
clock frequency would. Going from 8 bits to 24 costs three times the flip-flops and
0.4% more switching power in the outputs, because every bit you add moves half as often
as the one before it. That is a genuinely unusual shape for a hardware cost, and it is
worth remembering the next time a wide counter looks expensive.

It also says where the power really goes. There *is* one node driven at the full clock
frequency, and it reaches every flip-flop in the design: the clock net. It is the widest
piece of copper on the chip, it drives $n$ clock inputs rather than one gate input, and
it cycles $f$ times a second while the counter's own outputs manage $f(1 - 2^{-n})$
between all of them. In a real counter the clock is usually an order of magnitude more
power than the counting, which is why clock gating — genuinely stopping the clock to a
block that is idle, at the root of its tree rather than at each flip-flop — is the first
thing anyone reaches for, and why the load-enable multiplexer of the first reading is a
correctness tool rather than a power-saving one.

Two places this stops being the whole answer.

**The next-state logic switches too.** The AND tree of a synchronous counter has nodes
of its own, and they are not merely extra: a tree whose inputs arrive at different times
can toggle several times before settling on its final value. Those glitches dissipate
exactly as much per transition as a useful edge does. The derivation above counts
flip-flop outputs only.

**A Gray-code counter changes exactly one bit per step, by construction.** One
transition per clock is half a cycle per clock, so the whole register cycles $f/2$ times
a second and its switching power is $\tfrac{1}{2}CV^2f$ — about half what the binary
counter costs, since the binary counter averages very nearly two transitions per clock.
That is a second reason to use one, quite apart from the clock-domain-crossing argument
in the second reading.
''',
            },
            "tune": {
                "title": "A filter that passes the press and stops the chatter",
                "minutes": 10,
                "brief": r'''
Point a counter at a push-button and it will count 4, or 7, or 12 for a single press.
The contacts do not close cleanly: they bounce apart and back together several times
over the first few milliseconds, and each bounce is a perfectly good clock edge as far
as the counter is concerned.

The fix is a low-pass filter between the button and the logic. A deliberate press is
a slow event — even a fast finger manages about five a second — while the chatter is
a burst of pulses around a millisecond long. Those two live at very different
frequencies, which is exactly what a filter is for.

Two knobs, and they pull against each other: a filter slow enough to swallow the
chatter starts to blunt the press itself.
''',
                "prompt": "Pass a 5 Hz press with at least 90% of its amplitude, and put the 1 kHz chatter at least 35 dB down.",
                "note": "Both constraints must hold at once. The readout also gives the time constant, which is the number a datasheet would quote for this circuit.",
                "model": "rc-lowpass",
                "initial": {"r": 1000, "c": 100},
                "constants": {"fsig": 5, "fnoise": 1000},
                "constraints": [
                    {"k": "keep", "label": "the 5 Hz press survives: |H| ≥ 0.90", "min": 0.9},
                    {"k": "reject", "label": "the 1 kHz chatter is at least 35 dB down", "max": -35},
                ],
            },
            "lab": {
                "title": "A shift register, a ring counter and an LFSR",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Three blocks that are all the same block — flip-flops in a row — differing only in
what is fed back into the front.

Bit lists are leftmost-bit-first throughout.

**`shift_left(bits, fill=0)`** — everything moves one place left, the leftmost bit
falls off the end, and `fill` arrives at the right. Return a **new** list; the
argument must come back unchanged.

**`ring_counter(n, cycles)`** — a single 1 walking round `n` flip-flops. Start at
`[1, 0, 0, ...]`, rotate one place to the **right** per tick, and record the state on
each of `cycles` ticks, starting with the initial state itself.

**`lfsr_step(state, taps)`** — one clock of a Fibonacci linear-feedback shift
register. XOR together the bits at the tapped positions (`taps` are 1-based, counted
from the left), shift that new bit in at the **left**, and drop the bit that falls off
the right.

**`lfsr_run(state, taps, cycles)`** — the state on each of `cycles` ticks, starting
with `state` itself.

Run `main.py` and read the LFSR's fifteen states. Nothing about them looks like
counting, and yet not one of them repeats.
''',
                "files": [{"name": "main.py", "content": r'''
def shift_left(bits, fill=0):
    """One place left. The leftmost bit falls off; `fill` enters at the right."""
    # TODO: build and return a NEW list.
    return list(bits)


def ring_counter(n, cycles):
    """A single 1 walking round n flip-flops, recorded once per tick."""
    # TODO: start at [1, 0, 0, ...] and rotate one place right per tick.
    return []


def lfsr_step(state, taps):
    """One clock of a Fibonacci LFSR.

    `taps` are 1-based positions counted from the left. XOR the tapped bits, shift
    that bit in at the left, and drop the bit falling off the right.
    """
    # TODO
    return list(state)


def lfsr_run(state, taps, cycles):
    """The state on each of `cycles` ticks, starting with `state` itself."""
    # TODO
    return []


def show(rows):
    return " ".join("".join(str(b) for b in row) for row in rows)


if __name__ == "__main__":
    print("shift  :", shift_left([1, 0, 1, 1]))
    print("ring   :", show(ring_counter(4, 6)))
    print("lfsr   :", show(lfsr_run([0, 0, 0, 1], [3, 4], 15)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def shift_left(bits, fill=0):
    """One place left. The leftmost bit falls off; `fill` enters at the right."""
    return list(bits[1:]) + [fill]


def ring_counter(n, cycles):
    """A single 1 walking round n flip-flops, recorded once per tick."""
    state = [1] + [0] * (n - 1)
    out = []
    for _ in range(cycles):
        out.append(list(state))
        state = state[-1:] + state[:-1]
    return out


def lfsr_step(state, taps):
    """One clock of a Fibonacci LFSR.

    `taps` are 1-based positions counted from the left. XOR the tapped bits, shift
    that bit in at the left, and drop the bit falling off the right.
    """
    feedback = 0
    for t in taps:
        feedback ^= state[t - 1]
    return [feedback] + list(state[:-1])


def lfsr_run(state, taps, cycles):
    """The state on each of `cycles` ticks, starting with `state` itself."""
    out = []
    cur = list(state)
    for _ in range(cycles):
        out.append(list(cur))
        cur = lfsr_step(cur, taps)
    return out


def show(rows):
    return " ".join("".join(str(b) for b in row) for row in rows)


if __name__ == "__main__":
    print("shift  :", shift_left([1, 0, 1, 1]))
    print("ring   :", show(ring_counter(4, 6)))
    print("lfsr   :", show(lfsr_run([0, 0, 0, 1], [3, 4], 15)))
'''}],
                "hints": [
                    "`bits[1:] + [fill]` is the whole of `shift_left` — slicing already makes a new list, which is why the argument survives untouched.",
                    "Rotating right by one is `state[-1:] + state[:-1]`: take the last element and put it in front of the rest.",
                    "In `lfsr_step`, `feedback ^= state[t - 1]` accumulates the XOR over the taps; `^` on 0/1 integers is exactly the XOR gate from module 2.",
                    "`lfsr_run` records first and steps afterwards, so the list it returns begins with the state it was handed.",
                ],
                "tests": [
                    {"name": "the shift moves one place and leaves its input alone", "code": r'''
_start = [1, 0, 1, 1]
assert shift_left(_start) == [0, 1, 1, 0], f"expected [0, 1, 1, 0], got {shift_left(_start)}"
assert _start == [1, 0, 1, 1], "shift_left must return a new list, not edit the one it was given"
assert shift_left([0, 0, 0, 0], 1) == [0, 0, 0, 1], "the fill bit arrives at the right"
'''},
                    {"name": "shifting left is multiplying by two, modulo the width", "code": r'''
def _value(bs):
    v = 0
    for b in bs:
        v = v * 2 + b
    return v
for _n in range(16):
    _bits = [(_n >> _p) & 1 for _p in (3, 2, 1, 0)]
    assert _value(shift_left(_bits)) == (2 * _n) % 16, \
        f"{_n} shifted should be {(2 * _n) % 16}, got {_value(shift_left(_bits))}"
'''},
                    {"name": "the ring counter walks one place per tick and wraps", "code": r'''
_got = ring_counter(4, 6)
assert _got == [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1],
                [1, 0, 0, 0], [0, 1, 0, 0]], f"got {_got}"
assert all(sum(row) == 1 for row in ring_counter(5, 20)), \
    "exactly one flip-flop is ever set — that is what makes it one-hot"
'''},
                    {"name": "one clock of the LFSR", "code": r'''
assert lfsr_step([0, 0, 0, 1], [3, 4]) == [1, 0, 0, 0], \
    f"taps 3 and 4 hold 0 and 1, so the new left bit is 1; got {lfsr_step([0, 0, 0, 1], [3, 4])}"
assert lfsr_step([1, 0, 0, 0], [3, 4]) == [0, 1, 0, 0], \
    "taps 3 and 4 both hold 0 here, so a 0 shifts in"
assert lfsr_step([0, 0, 0, 0], [3, 4]) == [0, 0, 0, 0], \
    "all-zeros XORs to zero and shifts in a zero: the register can never leave it"
'''},
                    {"name": "taps 3 and 4 give a maximal cycle of fifteen", "code": r'''
_seq = lfsr_run([0, 0, 0, 1], [3, 4], 15)
assert len(_seq) == 15 and _seq[0] == [0, 0, 0, 1], "the run starts with the state it was given"
assert len({tuple(s) for s in _seq}) == 15, \
    f"all fifteen states should be different, got {len({tuple(s) for s in _seq})} distinct"
assert [0, 0, 0, 0] not in _seq, "all-zeros is outside the cycle"
assert lfsr_step(_seq[-1], [3, 4]) == [0, 0, 0, 1], \
    "the sixteenth step comes back to the start, which is what makes the length 15"
'''},
                    {"name": "a badly chosen tap set is much shorter", "code": r'''
_short = lfsr_run([0, 0, 0, 1], [1, 2], 16)
assert len(_short) == 16, f"lfsr_run should give one state per tick, got {len(_short)}"
assert len({tuple(s) for s in _short}) < 15, \
    "taps 1 and 2 do not give a maximal-length sequence — which tap positions work is not obvious, and is looked up"
'''},
                ],
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "Finite state machines",
            "summary": "A counter is a state machine that only ever goes one way. Once the diagram is drawn, every synchronous circuit is the same three pieces.",
            "concepts": [
                "A **finite state machine** is four things: a set of states, a register holding which one you are in, a combinational **next-state** function of the present state and the inputs, and a combinational **output** function. Every synchronous design is one of these, and drawing the diagram is the design; the gates follow from it mechanically.",
                "A **Moore** machine's output depends on the state alone, so it moves only just after a clock edge and is immune to whatever the inputs do in between, at the cost of arriving a cycle later than the input that caused it. Immune to *input* glitches is not the same as glitch-free: the output is still combinational logic on the state bits, so when several of them change on one edge it can pass through a wrong pattern on its way to the new one, for exactly the reason module 6 gave for a decoder. Only an output taken from a register of its own is free of that. A **Mealy** machine's output depends on the state *and* the current inputs, so it reacts a cycle earlier and inherits whatever the input does between edges.",
                "The state **names** are yours; the bit patterns are a design decision. A binary encoding of $N$ states uses $\\lceil \\log_2 N \\rceil$ flip-flops and more next-state logic; **one-hot** uses one flip-flop per state and almost no logic, because \"am I in state 7\" becomes a single wire rather than a comparison.",
                "Six states in three flip-flops leaves two patterns that name no state — until a glitch or a power-up puts the register into one. A machine with no way back out of an unused state is a machine that has hung, which is why a **reset** input is not optional and why unused states are usually pointed back at the start rather than left undefined.",
                "An input that is not synchronised to your clock can change inside a flip-flop's setup window and leave it **metastable**: neither 0 nor 1, for a time that has no guaranteed bound, with different gates reading it disagreeing about what it was. Two flip-flops in series on every asynchronous input is the standard answer. It does not abolish metastability; it gives it a whole clock period to decay, which drops the chance of anything downstream seeing it by many orders of magnitude.",
            ],
            "read": [
                {
                    "title": "The smallest thing a circuit has to remember",
                    "minutes": 16,
                    "body": r'''
Module 4 built a circuit that remembers one bit and module 8 put a lot of them side by
side, but neither said a word about *what* to remember. That is this module's question,
and it turns out to be a question about the problem rather than about flip-flops. Before
you can build the register you have to know how wide it is, and before you know that you
have to know how many genuinely different situations the thing you are building can be
in.

## The same input twice, and two different answers

A combinational circuit is a function. Give it the same inputs and it hands back the
same outputs today, tomorrow, and on the ten-thousandth try — that is the whole content
of a truth table, and it is why modules 2 and 3 could specify a circuit completely with
one.

Now watch a serial line and raise an output whenever the last three bits were `1 1 0`.
The input is one wire carrying one bit per clock. Feed it a `0` and ask what the output
should be. There is no answer. If the two bits before it were `1 1` the output must go
true; if they were anything else it must stay false. The same input, the same circuit,
two different required answers — so whatever this is, it is not a function of the input,
and no truth table over $x$ can specify it.

The fix is not subtle: keep some of the past. The interesting part is *how much*.

## What has to be kept is not the history

The tempting move is to store the input. Keep the last three bits in a shift register,
compare them against `110`, done — and for this particular problem that works and costs
three flip-flops. It stops working the moment the pattern is thirty bits long, or the
moment the interesting event is "the third `1` since the last reset", where there is no
bounded window to keep at all.

The move that scales is to store not the history but *what the history is worth*. Two
different pasts can be treated as the same thing if no future input will ever tell them
apart. Take the `110` detector and ask what a past is actually good for: it is good for
however much of `110` it has already supplied. A past ending in `0 1 0 1 1` and a past
ending in `1 1` are completely different sequences, but both end in `1 1`, so from here
on they behave identically — a `0` next completes a match for either, a `1` next leaves
both sitting on `1 1`. There is no experiment that separates them, so there is no reason
for the circuit to hold enough to separate them.

Lump the pasts into classes by that rule and the classes are the **states**. For this
problem there are four, and each one is named by how much of the pattern the past has
delivered:

```
  A   the tail of the input is no use at all
  B   the tail ends in  1
  C   the tail ends in  1 1
  D   the tail ends in  1 1 0   -- a match has just completed
```

That is the whole design. A pattern of length $m$ gives exactly $m+1$ states, one for
each prefix of it including the empty prefix and the whole thing, and the count does not
depend on how the pattern is written — a thirty-bit pattern needs thirty-one states and
five flip-flops, where a shift register would have needed thirty.

## The three pieces are now forced

Once the states exist, the hardware has no freedom left in it.

Something has to hold which class you are in: a **register**, $\lceil \log_2 N \rceil$
flip-flops wide for $N$ states. Something has to work out which class the next input
moves you into: **next-state logic**, a combinational function of the present state and
the inputs, because the class you land in depends on both. And something has to say what
to emit: **output logic**. Three blocks, one loop:

```
            +-------------------+
   inputs ->| next-state logic  |--- D ---> [ state register ] ---+---> Q
        +-->|                   |                ^                |
        |   +-------------------+                |                |
        |                                      clock              |
        +---------------------------------------------------------+
                                                                  |
                                       +--------------+           |
                                       | output logic |<----------+
                                       +--------------+---> outputs
```

Every synchronous design in this course is that picture. A counter is that picture with
the next-state logic set to "add one". A shift register is that picture with the
next-state logic set to "move everything along". Nothing else is going on.

## Worked example: `1 1 0`, all the way down to gates

Take the four states above and write down where each one goes. There is exactly one
question to ask at each entry, and no judgement in it: *after this bit, what is the
longest tail that is still a prefix of `1 1 0`?*

```
  state  means            x=0                       x=1
  -----  ---------------  ------------------------  ------------------------
   A     nothing useful   tail "0", no use     -> A tail "1"          -> B
   B     tail is 1        tail "10", no use    -> A tail "11"         -> C
   C     tail is 11       tail "110", a match! -> D tail "111", ends 11 -> C
   D     tail is 110      tail "1100", no use  -> A tail "1101", ends 1 -> B
```

Row D is the one people get wrong and it is worth staring at. The match is over, so the
instinct is to go back to A and start again. But the bit that arrives after a match is a
perfectly good first bit of the *next* match, and throwing it away means `1 1 0 1 1 0`
reports one match instead of two.

Output: $y = 1$ in D and nowhere else. That makes this a **Moore** machine — the output
reads the state and nothing else.

Now encode. Four states need two flip-flops, call them $Q_1 Q_0$, and the obvious
assignment is to number the states in order: A = 00, B = 01, C = 10, D = 11. Rewrite the
table in bits, with $Q_1^+ Q_0^+$ meaning the pattern after the next edge:

```
  Q1 Q0  x    Q1+ Q0+
   0  0  0     0   0
   0  0  1     0   1
   0  1  0     0   0
   0  1  1     1   0
   1  0  0     1   1
   1  0  1     1   0
   1  1  0     0   0
   1  1  1     0   1
```

That is two truth tables of three variables, which is module 3's problem exactly. Pull
the minterms out and put them on a map. $Q_1^+$ is 1 in rows `011`, `100`, `101`; the
last two differ only in $x$ and merge, the first has no neighbour:

$$Q_1^+ = Q_1\overline{Q_0} + \overline{Q_1}Q_0 x$$

$Q_0^+$ is 1 in rows `001`, `100`, `111`. Check each against its three neighbours and
none of them are adjacent to each other, so nothing merges at all:

$$Q_0^+ = \overline{Q_1}\,\overline{Q_0}\,x + Q_1\overline{Q_0}\,\overline{x} + Q_1 Q_0 x$$

$$y = Q_1 Q_0$$

Count what that costs, in gate inputs, the way module 3 counted:

```
  inverters for Q1', Q0', x'          3 gates,  3 gate inputs
  Q1+ : AND2 + AND3 + OR2             3 gates,  7 gate inputs
  Q0+ : AND3 x3 + OR3                 4 gates, 12 gate inputs
  y   : AND2                          1 gate,   2 gate inputs
  -----------------------------------------------------------
  total                              11 gates, 24 gate inputs
```

## The same machine with the patterns swapped

Nothing above required A to be 00 and B to be 01. The names are yours and so are the
bits. Try the Gray order instead — A = 00, B = 01, C = 11, D = 10 — so that consecutive
states differ in one bit:

```
  Q1 Q0  x    Q1+ Q0+       (A=00  B=01  C=11  D=10)
   0  0  0     0   0
   0  0  1     0   1
   0  1  0     0   0
   0  1  1     1   1
   1  1  0     1   0
   1  1  1     1   1
   1  0  0     0   0
   1  0  1     0   1
```

$Q_1^+$ is 1 in `011`, `110`, `111`. The last two merge to $Q_1 Q_0$; `011` and `111`
merge to $Q_0 x$. $Q_0^+$ is 1 in `001`, `011`, `101`, `111` — every row with $x = 1$
and no others, so the whole function collapses:

$$Q_1^+ = Q_1 Q_0 + Q_0 x = Q_0\left(Q_1 + x\right), \qquad
  Q_0^+ = x, \qquad y = Q_1 \overline{Q_0}$$

$Q_0^+ = x$ is not a coincidence and it is worth seeing why: in this assignment $Q_0$ is
1 in exactly the states B and C, which are precisely the states whose meaning is "the
last bit was a 1". So $Q_0$ *is* the last bit, delayed by one clock, and the flip-flop
holding it is doing nothing but delaying the input.

```
  Q1+ : OR2 + AND2                    2 gates,  4 gate inputs
  Q0+ : a wire                        0 gates,  0 gate inputs
  y   : inverter + AND2               2 gates,  3 gate inputs
  -----------------------------------------------------------
  total                               4 gates,  7 gate inputs
```

Eleven gates and twenty-four gate inputs, against four gates and seven. Same machine,
same four states, same behaviour on every input it will ever see — and the only
difference is which two-bit pattern was written next to which circle. This is why
synthesis tools try several encodings and why the next reading spends its time on them.

## Worked example: the same detector as a Mealy machine

A **Mealy** machine puts the output on the arc rather than on the state: $y$ is a
function of the state *and* the input arriving now. Redo the detector that way and state
D disappears, because "a match has just completed" no longer needs to be remembered — it
can be announced as it happens:

```
  state  x=0                  x=1
  -----  -------------------  -------------------
   A     -> A,  y = 0         -> B,  y = 0
   B     -> A,  y = 0         -> C,  y = 0
   C     -> A,  y = 1   <--   -> C,  y = 0
```

Three states instead of four, which is the general rule: a length-$m$ pattern needs
$m+1$ Moore states and $m$ Mealy states. Here it saves no flip-flops — three states
still need two — but it changes *when* the output happens. Run both on `1 1 0 1 1 0`,
recording what is true during each tick:

```
  tick        0    1    2    3    4    5    6
  input       1    1    0    1    1    0    -
  Moore state A    B    C    D    B    C    D
  Moore y     0    0    0    1    0    0    1
  Mealy state A    B    C    A    B    C    A
  Mealy y     0    0    1    0    0    1    -
```

Both find two matches. The Mealy output goes true on tick 2 — the very tick the final
`0` is present — while the Moore output goes true on tick 3, after the edge that moved
the register into D. One clock period of difference, every time, and the second Moore
pulse falls on tick 6, one tick past the end of a six-bit input.

That is the entire trade. Mealy is a cycle earlier and its output is combinational logic
sitting on an input pin, so anything the input does mid-cycle — a glitch, a slow edge, a
bit of ringing — comes straight out. Moore is a cycle later and its output cannot see
the input at all, so nothing the input does between edges can reach it. Neither is
better. A Mealy output driving another machine's input is a common source of long
combinational paths between two state registers; a Moore output is the safe default and
you pay a cycle for it.

## The mistake people actually make

**Starting again after a match.** Row D of the table above. It is tempting because the
match really is finished, and because it is what you would do by hand. It costs you
every overlapping occurrence, and the bug is invisible on the test input everybody tries
first, which is a single clean copy of the pattern.

**Inventing a state per input value instead of per distinguishable past.** With two
input bits people draw four states, then eight when a third bit turns up, and the
diagram explodes while carrying almost no information. States are for what must be
remembered; inputs are read, not stored. A machine watching a 32-bit bus can perfectly
well have three states.

**Mixing Moore and Mealy in one diagram.** Writing an output inside a circle and another
one on an arc is not a machine that does both — it is two conventions in one picture,
and the arc output will be a cycle earlier than the circle output for reasons the
diagram does not show. Pick one, and if a design genuinely needs a fast output and a
clean one, take the Mealy signal and register it, which turns it back into a Moore
output a cycle later.

**Assuming a Moore output is glitch-free.** It is immune to what the *input* does
between edges, which is not the same thing. $y = Q_1\overline{Q_0}$ is combinational
logic on two flip-flop outputs, and when both change on one edge the gate can show a
transient before it settles, exactly as module 6's decoder does. An output driving
something edge-sensitive gets a flip-flop of its own.

## Where the state diagram stops being the right tool

**When the state count depends on data.** "Count 1000 clock cycles, then do the next
thing" is a thousand states, and nobody draws them. The answer is to split the design in
two: a **datapath** — a counter, a register, a comparator — holding the value, and a
small control machine of four or five states holding the *phase*, with the counter's
"= 999" comparison as one of the control machine's inputs. That split is what makes real
designs tractable, and it is why the state diagrams you meet in practice are almost
always small.

**When there is no bound on what must be remembered.** Detecting balanced brackets, or
matching a pattern whose length arrives at run time, needs storage that grows with the
input, and no fixed number of flip-flops can do it. What replaces the state machine
there is a machine with a stack, or with a memory — which is module 10, and is the
reason a processor is not just a very large FSM.

**When the machine has to be fast.** Everything here assumed the next-state logic
settles inside one clock period. That loop is the one path in a synchronous design you
cannot pipeline, because its output is its own input a cycle later: registering the
middle of it does not make it faster, it makes it a different machine. When the loop is
too slow the fixes are to encode the states so the logic is shallower, to precompute the
next-state function one cycle ahead for each possible input, or to change the machine.
The next reading starts there.
''',
                },
                {
                    "title": "Bit patterns, leftovers, and the wires that come in from outside",
                    "minutes": 16,
                    "body": r'''
The state diagram is a fiction. What exists on the silicon is a handful of flip-flops
holding a pattern of ones and zeros, and three decisions stand between the diagram and
that pattern: how many flip-flops, which pattern goes with which circle, and what
happens if the register ever holds a pattern you did not assign. The first reading
already showed that the second of those is worth a factor of three in gates. This one
takes all three seriously, and then looks at the two ways a machine that is correct on
paper dies in the field.

## How many flip-flops, and which pattern

$N$ states need enough patterns to name them all, so a **binary** encoding uses
$n = \lceil \log_2 N \rceil$ flip-flops. Twenty states need five, because $2^4 = 16$ is
too few and $2^5 = 32$ is enough. That is the smallest register that can possibly work,
and for a long time it was the only encoding anyone used, because flip-flops were the
expensive part.

The alternative goes the other way. **One-hot** gives every state a flip-flop of its
own, and the state is whichever one currently holds a 1. Twenty states, twenty
flip-flops, and $2^{20} - 20$ patterns that name nothing. The reason anyone would do
this is what it does to the logic. "Am I in state STOP?" in a binary encoding is a
five-input AND of the state bits with three of them inverted; in one-hot it is the wire
called `STOP`. And the next-state logic inverts in the same way: instead of five
functions each depending on all five state bits, you get one function per state, each an
OR over the arcs that arrive there.

Write the `110` detector both ways and the two costs are easy to compare. One-hot, with
one flip-flop per state and the arcs read straight off the table in the first reading:

$$D_A = \overline{x}\,(A + B + D), \quad D_B = x\,(A + D), \quad
  D_C = x\,(B + C), \quad D_D = \overline{x}\,C, \quad y = D$$

```
  inverter for x'                     1 gate,   1 gate input
  D_A : OR3 + AND2                    2 gates,  5 gate inputs
  D_B : OR2 + AND2                    2 gates,  4 gate inputs
  D_C : OR2 + AND2                    2 gates,  4 gate inputs
  D_D : AND2                          1 gate,   2 gate inputs
  y   : a wire                        0 gates,  0 gate inputs
  ------------------------------------------------------------
  total                               8 gates, 16 gate inputs   + 4 flip-flops
```

Against the Gray-encoded binary version's four gates, seven gate inputs and two
flip-flops. One-hot loses this one, and it loses it badly: a flip-flop costs about as
much silicon as six or eight two-input gates, so the two extra flip-flops alone outweigh
the whole logic saving that did not happen.

That is the honest shape of the trade, and it is worth stating plainly because one-hot
is often recommended as though it were free. It wins when $N$ is large enough that the
binary decode ANDs get wide and deep, when the arcs are sparse so each `OR` has two or
three terms rather than ten, when the outputs are mostly "am I in this state" so the
output logic vanishes, and — decisively — when the flip-flops are free. On an FPGA a
lookup table arrives with a flip-flop attached whether you use it or not, so a twenty-
state one-hot register costs nothing that was not already there, and the win is entirely
in logic depth and therefore in clock frequency. On a standard-cell ASIC where every
flip-flop is area you paid for, the crossover sits much higher.

There is a third choice worth knowing. If the machine's outputs are the point, assign
the patterns so that the **output bits are state bits**. Give a three-output controller
states whose codes contain the three output values, and the output logic becomes three
wires — no gates, and no glitch when the state changes, because the output bits come
straight off flip-flops. It costs a wider register and a next-state function that has
lost the freedom to be convenient, and it is the standard answer whenever an output
drives something that must never see a transient.

## The patterns nobody assigned

Twenty states in five flip-flops leaves twelve patterns that name no state. They are not
hypothetical. The register powers up holding whatever the silicon happens to settle
into; a particle of background radiation can flip a bit in a running machine; a supply
dip can leave the register somewhere between. Something will eventually put the machine
into one of the twelve, and the only question is what happens next.

The usual answer is worse than people expect, and the reason is that the unused rows
look like a gift. Take a three-state machine — A = 00, B = 01, C = 10, advancing on
$x=1$ and holding on $x=0$, with pattern 11 unused:

```
  Q1 Q0  x    Q1+ Q0+
   0  0  0     0   0        A holds
   0  0  1     0   1        A -> B
   0  1  0     0   1        B holds
   0  1  1     1   0        B -> C
   1  0  0     1   0        C holds
   1  0  1     0   0        C -> A
   1  1  0     ?   ?        never happens
   1  1  1     ?   ?        never happens
```

Mark the last two rows "don't care" — which is what they are, and what every textbook
says to do with them — and hand the maps to a minimiser. It will use them, because that
is what they are for:

$$Q_1^+ = Q_0 x + Q_1 \overline{x}, \qquad
  Q_0^+ = \overline{Q_1}\,\overline{Q_0}\,x + Q_0 \overline{x}$$

Now evaluate those two expressions at the pattern that never happens:

```
  Q1 Q0 = 1 1,  x = 0 :  Q1+ = 0 + 1 = 1     Q0+ = 0 + 1 = 1   ->  1 1
  Q1 Q0 = 1 1,  x = 1 :  Q1+ = 1 + 0 = 1     Q0+ = 0 + 0 = 0   ->  1 0  (state C)
```

The machine that lands in 11 with $x$ low **stays there for ever**. Not for a while —
for ever, because 11 with $x = 0$ maps to itself, and $x$ low is exactly the condition
"nothing is happening", which is what an idle system looks like at power-up. A board
that comes up dead one time in some unlucky fraction, and works perfectly on the bench,
is this bug.

The fix is to stop calling those rows don't-cares and force them to the reset state. The
functions get slightly bigger:

$$Q_1^+ = \overline{Q_1}Q_0 x + Q_1\overline{Q_0}\,\overline{x}, \qquad
  Q_0^+ = \overline{Q_1}\,\overline{Q_0}\,x + \overline{Q_1}Q_0\overline{x}$$

```
  with don't-cares : 16 gate inputs, and 11 is a trap
  forced to state A: 19 gate inputs, and 11 recovers on the next edge
```

Three gate inputs out of sixteen, about nineteen per cent more logic, to make the whole
class of failure impossible. That is the trade, and it is why "unused states go back to
the start" is a rule rather than a preference. In HDL it is the difference between
leaving the `default` branch off a case statement and writing `default: next = IDLE;`,
which is one line.

One-hot changes the shape of this problem rather than removing it. Twenty flip-flops
have a million unused patterns, so pointing each of them at the reset state is not
something you can write down — but you do not have to, because you can *detect* the
condition cheaply: exactly one bit should be set, and an XOR tree or a "no bits set"
check spots any pattern that is not one-hot in a few gates. Detect and reset is the
one-hot answer; enumerate and redirect is the binary one.

## Reset, and the fact that releasing it is the hard part

Every one of the above depends on there being a known starting pattern, which means a
reset. There are two kinds and the difference is not stylistic.

A **synchronous** reset is just another input to the next-state logic: when it is
asserted, the next state is the start state. It costs a little logic, it cannot glitch
the flip-flops, and it is useless in the one situation you most need it — a machine
whose clock is not yet running, because a clock generated by a PLL takes time to lock
and a crystal oscillator takes milliseconds to start. No edges, no reset.

An **asynchronous** reset goes to a dedicated pin on the flip-flop and forces it low
with no clock at all, which is exactly what power-up needs. Its problem is at the other
end. Releasing it is a change on an input to a flip-flop, and it has timing
requirements of its own: **recovery time**, the interval before a clock edge during
which the reset must already have gone away, which is setup time under another name, and
**removal time**, its hold-time counterpart. A reset released from an RC network — the
circuit this module's build exercise puts together — has no idea where the clock edges
are, so it will eventually be released inside somebody's recovery window. And "somebody"
is the point: with twenty flip-flops spread across a chip, the release edge arrives at
each of them at a slightly different time, so some can take the clock edge that is
arriving and some can miss it. The machine leaves reset in a pattern that is a mixture
of the start state and the state before it, which is very often not a state at all.

The standard answer is to **assert asynchronously and release synchronously**. Two
flip-flops with their D inputs tied high and their asynchronous clears driven by the raw
reset: while raw reset is low both are cleared instantly, no clock required, and when it
goes away the 1 walks through them on clock edges, so the reset seen by the design goes
away on a clean edge with the full period of margin. That is six transistors' worth of
circuit and it converts a real, intermittent, unreproducible failure into nothing.

## One wire from outside, two readers

Module 4 established what happens when a signal changes inside a flip-flop's setup
window: the flip-flop is left balanced between its two stable states, resolves after an
unbounded time, and the mean time between failures goes as

$$\text{MTBF} = \frac{e^{t_r/\tau}}{T_0\,f_c\,f_d}$$

with $t_r$ the time the metastable output is left alone before anything reads it. Two
flip-flops in series give the first one a whole extra clock period of $t_r$, and because
the exponential does all the work, that turns a failure every few minutes into a failure
every few centuries.

A state machine adds a failure that is *not* metastability and that a lot of people
never meet. Feed an unsynchronised input straight into the next-state logic and it is
read by several different paths, with different delays, on their way to different
flip-flops. If the input changes while the logic is settling, those paths need not agree
about what it was — and they do not have to go metastable for that, they merely have to
have different delays, which they always do.

Work it on the three-state machine above, the risky version, sitting in state B = 01:

$$Q_1^+ = Q_0 x + Q_1\overline{x} \;\big|_{01} = x, \qquad
  Q_0^+ = \overline{Q_1}\,\overline{Q_0}\,x + Q_0\overline{x} \;\big|_{01} = \overline{x}$$

```
  both paths see x = 1  ->  Q1+ Q0+ = 1 0  =  C      legal
  both paths see x = 0  ->  Q1+ Q0+ = 0 1  =  B      legal
  Q1+ sees 1, Q0+ sees 0 -> Q1+ Q0+ = 1 1  =  the trap
  Q1+ sees 0, Q0+ sees 1 -> Q1+ Q0+ = 0 0  =  A      legal, but wrong
```

One unsynchronised wire and one set of don't-cares, each survivable on its own, combine
into a machine that wedges permanently. Neither mistake is visible in simulation, where
every signal changes at a defined instant and every path is timed identically.

Two consequences follow from that, and both get broken regularly:

**Synchronise once, then fan out.** The synchroniser's job is to produce a signal that
changes only just after a clock edge, and every consumer must read that one signal. Two
separate two-flip-flop synchronisers on the same asynchronous wire are two independent
resolutions, and on the edge where the input changes they can land on different values —
which is the split above with more hardware.

**A synchroniser fixes one wire, not a bus.** Put a synchroniser on each of eight bits
and each bit independently resolves to the value it had at one instant or the next, so a
byte changing from `01111111` to `10000000` can arrive as any of the patterns in between,
including `11111111` and `00000000` — words that were never sent. The two standard cures
are to make only one bit change at a time, which is what a **Gray-coded** counter is for,
or to send a handshake: the data sits still, a single request wire is synchronised, and
only after it has been seen does the receiver read the data. A FIFO between two clock
domains does both, with Gray-coded pointers and no handshake per word, and it needs a
memory — module 10.

## Where all of this stops holding

**The MTBF number is a model, not a guarantee.** $\tau$ and $T_0$ are measured on
silicon, and they get worse as the supply drops and the temperature rises — enough that
a synchroniser characterised at 1.2 V and room temperature can be an order of magnitude
worse at 0.7 V and 85 °C, which is exactly where a low-power design wants to run. Where
the number matters, it is computed at the worst corner and a third flip-flop is cheap.

**A reset fixes power-up, not corruption.** Everything above treats an illegal pattern
as something that happens once, at the start. In a part that has to keep working — a
car, an aeroplane, anything in orbit — a single ionising particle can flip a state bit
at any moment, and reset only helps if something notices. What replaces "point the
unused states at the start" there is active detection: an illegal-state checker on a
one-hot register, or two copies of the machine compared every cycle, plus a watchdog
that resets the whole block when the comparison fails.

**A control machine that is too slow cannot be pipelined out of trouble.** The
state-register loop feeds itself, so inserting a register inside it changes the machine
rather than speeding it up. What is left is to shorten the logic — a different encoding,
or splitting one machine into two smaller ones that talk to each other — or to compute
both possible next states in parallel and let the input choose between them at the last
gate, which trades area for one level of depth. Beyond that the answer is a different
architecture, which is what the next module's lookup tables are for.
''',
                },
            ],
            "quiz": {
                "title": "States, encodings and the things that come in from outside",
                "minutes": 9,
                "questions": [
                    {
                        "q": "What distinguishes a Mealy machine from a Moore machine?",
                        "opts": [
                            "A Mealy machine needs no clock",
                            "A Mealy machine's outputs depend on the current inputs as well as the state, so they can change between clock edges",
                            "A Moore machine cannot have inputs at all",
                            "A Mealy machine always needs more states",
                        ],
                        "a": 1,
                        "why": (
                            "That is the whole difference, and everything else follows from it. A Mealy output "
                            "can respond in the same cycle the input arrives, which is often a cycle sooner; "
                            "the price is that it also responds to whatever the input does mid-cycle, "
                            "including glitches. Both kinds are clocked and both have inputs. A Mealy machine "
                            "usually needs *fewer* states, because a distinction that Moore has to record in "
                            "a state can be read straight off the input instead."
                        ),
                    },
                    {
                        "q": "A machine has six states. How many flip-flops does a binary encoding need, and how many patterns does that leave over?",
                        "opts": [
                            "3 flip-flops, 2 patterns left over",
                            "3 flip-flops, none left over",
                            "6 flip-flops, none left over",
                            "4 flip-flops, 10 patterns left over",
                        ],
                        "a": 0,
                        "why": (
                            "$2^2 = 4$ is too few and $2^3 = 8$ is enough, so three flip-flops, and $8 - 6 = 2$ "
                            "patterns name no state. Those two are not harmless: the register powers up in "
                            "whatever it powers up in, and if the next-state logic sends one of them nowhere "
                            "the machine is stuck. One-hot would use six flip-flops and leave 58 unused "
                            "patterns, which sounds far worse and is often the better design, because the "
                            "next-state logic collapses to almost nothing."
                        ),
                    },
                    {
                        "q": "Why does a state machine need a reset input, when its next-state logic already says what to do in every state?",
                        "opts": [
                            "Because the clock might stop",
                            "Because its outputs would otherwise be undefined",
                            "Because at power-up the flip-flops hold whatever they happen to hold, which may be a pattern that names no state and has no path back",
                            "Because the state register cannot otherwise be read",
                        ],
                        "a": 2,
                        "why": (
                            "\"Every state\" means every state you drew. The register can come up holding a "
                            "pattern that is not one of them, and the logic you designed says nothing useful "
                            "about it — quite possibly it maps that pattern to itself. Reset forces a known "
                            "starting pattern and makes the question go away. It is also the reason a careful "
                            "designer points every unused pattern back at the start state instead of writing "
                            "\"don't care\" and letting the synthesiser choose."
                        ),
                    },
                    {
                        "q": "A button, not synchronised to the clock, is wired straight into a state machine's input. What can go wrong that a faster clock will not fix?",
                        "opts": [
                            "The flip-flop can be caught mid-decision and sit between 0 and 1 for a while, and different gates reading it may disagree about what it was",
                            "The button voltage will be too low for the input to register",
                            "The machine will run out of states",
                            "The button will bounce, and bouncing cannot be filtered",
                        ],
                        "a": 0,
                        "why": (
                            "Metastability. If the input changes inside the setup window the flip-flop is "
                            "briefly balanced between its two stable states, and the time it takes to fall "
                            "one way has no guaranteed upper bound — a faster clock makes it *more* likely to "
                            "be seen, not less. The fix is a chain of two flip-flops, so the second one is "
                            "sampling a signal that has already had a full period to settle. Contact bounce "
                            "is a genuine problem too, and the filter in module 8 is the answer to that one; "
                            "it is a different problem with a different cure."
                        ),
                    },
                    {
                        "q": "A Moore machine asserts an output in state S. The input that causes the move into S arrives just before a clock edge. When does the output go true?",
                        "opts": [
                            "Immediately, before that edge",
                            "Just after that edge, once the state register has taken S",
                            "One further clock period after that edge",
                            "Only once the input goes away again",
                        ],
                        "a": 1,
                        "why": (
                            "The register loads S on the edge, and the output function — which sees only the "
                            "state — settles a clock-to-output delay later. So the output is true for the "
                            "cycle *after* the input arrived. A Mealy machine given the same job asserts its "
                            "output as soon as the input arrives, before the edge: one cycle earlier, and "
                            "exposed to whatever that input does in the meantime. Neither is better; they "
                            "trade latency against cleanliness."
                        ),
                    },
                ],
            },
            "build": {
                "title": "Making sure the machine starts where you meant it to",
                "minutes": 24,
                "brief": r'''
A state machine's flip-flops power up holding whatever they happen to hold. Until
something forces them to a known pattern, the machine is in a state nobody chose —
possibly one that is not in your diagram at all. The reset input exists for this, and
the oldest circuit that drives it is a resistor and a capacitor.

The reset pin here is **active low**: the machine is held in reset while the pin is
low, and runs once the pin has risen past the pin's threshold. Tie a capacitor from
the pin to ground and a resistor from the pin to the supply, and at switch-on the
capacitor starts at zero and pulls the pin down with it; the resistor then charges it,
and the pin crosses the threshold some time later.

Which threshold, though? Module 5's four voltages are *promises*: an input undertakes
to read anything above $V_{IH}$ as a 1 and anything below $V_{IL}$ as a 0, and
undertakes nothing at all about the band between. Module 4 got away with a single
2.5 V decision point because a CMOS gate does switch near half its supply — but that
is typical behaviour, not a guarantee, and here it would not be enough: an RC ramp
crawls through the undefined band for tens of milliseconds, so an ordinary input given
this waveform has no guaranteed release time at all. Reset pins are therefore built as
**Schmitt-trigger** inputs — an input with one specified trip voltage on the way up
and a lower one on the way down, so that even an arbitrarily slow edge still produces
one clean decision at a stated voltage. This chip's datasheet gives the rising trip
point as $V_{T+} = 2.5$ V, half the rail as it happens, and that, not $V_{IH}$, is the
voltage the release time is measured to.

The arithmetic is then the same $v(t) = 5\left(1 - e^{-t/RC}\right)$ and the same
$t = RC\ln 2$ as the propagation-delay circuit in module 4 — four orders of magnitude
slower, and doing a completely different job.

Two requirements, from the chip's datasheet:

* reset must be **held for at least 20 ms** after the supply comes up, and must be
  **released within 100 ms**, or the board looks dead. Both times are measured to the
  $V_{T+} = 2.5$ V crossing, because that is where the pin decides
* the reset pin leaks up to **1 µA** out of the node, and that current can only come
  down through the resistor. Once the capacitor has charged the pin therefore settles
  at $5 - I \times R$ rather than at the rail, and the datasheet asks for **at least
  1 V of margin above $V_{T+}$** — a settled level above 3.5 V — because a megohm node
  picks up noise readily, and that margin is what stops a dip on it reaching the
  falling trip point and re-asserting reset on a running machine. So the resistor must
  stay below **1.5 MΩ**

The editor's model has no leakage in it, so the probe will show the node settling at
the full 5 V either way. The 1 µA is a constraint on the resistor you pick, not
something the simulation will show you.

Build it, and get the delay from the capacitor rather than from a huge resistor.
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
                        {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 100000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3},
                        {"id": "p4", "kind": "C", "x": 9, "y": 5, "rot": 1, "value": 470e-9},
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
                    {"name": "a 5 V supply charging a capacitance through a resistance", "code": r'''
c.assert(c.count('V') === 1, 'One supply: the rail that comes up at t = 0 when the board is switched on.');
c.close(c.values('V')[0], 5.0, 0.001, 'the supply voltage');
c.assert(c.count('C') >= 1,
  'Without a capacitor the reset pin follows the supply straight up and the machine is never held at all.');
c.assert(c.count('R') >= 1, 'The capacitor has to charge through a resistance, or there is no delay to speak of.');
'''},
                    {"name": "the machine does eventually come out of reset", "code": r'''
var r = c.step(1);
c.close(r.v[r.v.length - 1], 5.0, 0.02,
  'the reset level one second after switch-on. Anything short of the full supply means a second ' +
  'resistor to ground is dividing it down, and a reset pin that never gets above the 2.5 V trip ' +
  'point holds the machine in reset for ever');
'''},
                    {"name": "reset is held for between 20 ms and 100 ms", "code": r'''
var r = c.step(0.2);
var t = null;
for (var i = 0; i < r.t.length; i++) { if (r.v[i] >= 2.5) { t = r.t[i]; break; } }
c.assert(t !== null, 'The pin never reaches the 2.5 V trip point within 200 ms — RC is far too large.');
c.assert(t >= 0.02 && t <= 0.1,
  'Reset is released after ' + c.fmt(t, 's') + ', outside the 20-100 ms window. The V_T+ = 2.5 V ' +
  'trip point is crossed at 0.69 RC, so aim for an RC product between about 29 ms and 144 ms.');
'''},
                    {"name": "no resistor of 1.5 megohm or more", "code": r'''
var rs = c.values('R');
var big = rs.filter(function (x) { return x >= 1.5e6; });
c.assert(big.length === 0,
  'A resistor of ' + c.fmt(big[0] || 0, 'Ω') + ' is too large. The reset pin leaks up to 1 µA ' +
  'out of the node, and that current comes down through the resistor, so the pin settles at ' +
  '5 V minus I × R rather than at the rail; from 1.5 MΩ up the settled level is below the 3.5 V ' +
  'the datasheet asks for, leaving under 1 V of margin over the 2.5 V trip point on a node that ' +
  'picks up noise readily. Take the delay from the capacitor instead.');
'''},
                ],
                "hints": [
                    "The 20-100 ms window on the delay means an RC product between 28.9 ms and 144 ms, because the $V_{T+} = 2.5$ V trip point is crossed at $RC\\ln 2 \\approx 0.69\\,RC$.",
                    "100 kΩ with 470 nF gives $RC = 47$ ms and a release at about 33 ms — comfortably inside the window, and comfortably under the 1.5 MΩ limit, which leaves the pin settling at 4.9 V.",
                    "Values in the editor take engineering suffixes: `100k` for the resistor, `470n` for the capacitor.",
                    "Do not add a second resistor from the pin to ground. The level would settle at a divided-down voltage, the pin would never get above the 2.5 V trip point, and the machine would sit in reset for ever — which the second check is looking for.",
                ],
            },
            "blanks": [
                {
                    "title": "A state table, filled in from what each state means",
                    "minutes": 9,
                    "brief": r'''
The only skill in drawing a state machine is deciding what each state is *for*, and
the trick is to make every state mean **the longest useful thing seen so far**. Once
the meanings are written down, the transitions are not choices — you read them off.

The machine below watches a serial input and raises `y` for one clock whenever the
last three bits were 1 0 1. Overlaps count, so `1 0 1 0 1` fires twice: the trailing
1 of one match is allowed to be the leading 1 of the next.

Fill each hole by asking one question: *after this bit, what is the longest tail that
is still the start of `1 0 1`?*
''',
                    "caption": "a Moore sequence detector for 1 0 1",
                    "lang": "text",
                    "listing": r'''
  state   meaning                  next on x=0   next on x=1    y
  -----   ----------------------   -----------   -----------   ---
  S0      nothing useful yet       S0            ___            0
  S1      last bit was 1           S2            S1             0
  S2      last two were 1 0        ___           S3             0
  S3      last three were 1 0 1    ___           ___            1

  A binary encoding of these four states needs ___ flip-flops.
''',
                    "blanks": [
                        {
                            "prompt": "In S0 nothing useful has been seen, and now a 1 arrives.",
                            "opts": ["S0", "S1", "S2", "S3"],
                            "a": 1,
                            "why": (
                                "The tail is now `1`, which is the first symbol of the pattern, so exactly one "
                                "useful thing has been seen: that is S1. Staying in S0 would throw the 1 away and "
                                "the machine would never detect anything at all."
                            ),
                        },
                        {
                            "prompt": "In S2 the last two bits were 1 0, and now another 0 arrives.",
                            "opts": ["S0", "S1", "S2", "S3"],
                            "a": 0,
                            "why": (
                                "The tail is now `0 0`. The pattern starts with a 1, so neither the last bit nor "
                                "the last two are the start of it, and nothing useful survives: back to S0. "
                                "Staying in S2 would claim a `1 0` that has been overwritten."
                            ),
                        },
                        {
                            "prompt": "A match has just completed, so the machine is in S3, and a 0 arrives.",
                            "opts": ["S0", "S1", "S2", "S3"],
                            "a": 2,
                            "why": (
                                "The tail is `1 0 1 0`, whose last two bits are `1 0` — the first two symbols of "
                                "the pattern. So S2, one step from firing again, which is exactly how overlapping "
                                "matches get counted. Dropping back to S0 here would need three fresh bits and "
                                "would miss the second match in `1 0 1 0 1`."
                            ),
                        },
                        {
                            "prompt": "Still in S3 after a match, and this time a 1 arrives.",
                            "opts": ["S0", "S1", "S2", "S3"],
                            "a": 1,
                            "why": (
                                "The tail is `1 0 1 1`. The last bit is a 1 and the last two are `1 1`, which is "
                                "not the start of the pattern, so only the single 1 is worth keeping: S1. "
                                "Staying in S3 would raise `y` a second time for a sequence that has not happened."
                            ),
                        },
                        {
                            "prompt": "How many flip-flops does a binary encoding of four states need?",
                            "opts": ["1", "2", "3", "4"],
                            "a": 1,
                            "why": (
                                "Two flip-flops hold $2^2 = 4$ patterns, which is exactly four states with none "
                                "left over — the rare case where there are no unused patterns to worry about. "
                                "Four flip-flops is what a one-hot encoding would use, and it is not a silly "
                                "answer: it costs two more flip-flops and makes the output function a single wire."
                            ),
                        },
                    ],
                },
                {
                    "title": "The same table, once the states have been given bit patterns",
                    "minutes": 10,
                    "brief": r'''
The previous drill settled what the four states of the `1 0 1` detector mean and where
each one goes. Nothing in it was electrical — it could have been done on paper by
somebody who had never heard of a flip-flop.

This is the step that turns it into a circuit, and it is entirely mechanical. Give each
state a bit pattern; rewrite the transitions as those patterns; and what you are left
with is two next-state truth tables of three variables — $Q_1$, $Q_0$ and $x$ — plus a
one-line output function, all of which module 3 already knows how to turn into gates.

The patterns here are the obvious ones — S0 to S3 numbered 0 to 3 in binary. Two of the
next-state codes have been left out, and so have the three equations that fall out of
the finished table.
''',
                    "caption": "the 1 0 1 detector, encoded S0 = 00, S1 = 01, S2 = 10, S3 = 11",
                    "lang": "text",
                    "listing": r'''
  state  meaning              code    x=0 -> next  code    x=1 -> next  code    y
  -----  -------------------  ----    -----------  ----    -----------  ----   ---
  S0     nothing useful yet    00         S0         00        S1         01     0
  S1     last bit was 1        01         S2        ___        S1         01     0
  S2     last two were 1 0     10         S0         00        S3        ___     0
  S3     last three were 101   11         S2         10        S1         01     1

  The output is 1 in S3 and nowhere else, so           y = ___

  Q1+ is 1 in the rows 010, 110 and 101. The first two differ only in Q1, so
  they merge into Q0.x' ; the third has no neighbour and keeps all three of
  its literals:                                      Q1+ = Q0.x' + ___

  Q0+ is 1 in the rows 001, 011, 101 and 111 -- every row with x = 1 and no
  others -- so the whole function collapses to       Q0+ = ___
''',
                    "blanks": [
                        {
                            "prompt": "S1 on a 0 goes to S2. What is S2's code?",
                            "opts": ["00", "01", "10", "11"],
                            "a": 2,
                            "why": (
                                "S2 was numbered 2, which is `10` in two bits. The column is asking for the "
                                "*destination's* pattern, not the source's — this row starts in S1 = `01` "
                                "and ends in S2 = `10`, so both bits change on this transition. Nothing "
                                "about the encoding was forced: S2 could have been given `11` instead, "
                                "and the equations further down would have come out differently for the "
                                "same machine."
                            ),
                        },
                        {
                            "prompt": "S2 on a 1 goes to S3. What is S3's code?",
                            "opts": ["00", "01", "10", "11"],
                            "a": 3,
                            "why": (
                                "S3 was numbered 3, which is `11`. This is the transition that completes a "
                                "match, so it is the row that has to leave the register holding the pattern "
                                "the output logic is watching for. Get this one wrong and the detector "
                                "never fires."
                            ),
                        },
                        {
                            "prompt": "The output is 1 in S3 = 11 and in no other state. Write it as a function of the state bits.",
                            "opts": ["Q1.Q0", "Q1 + Q0", "Q1.Q0'", "Q0"],
                            "a": 0,
                            "why": (
                                "A Moore output is a function of the state alone, and \"the state is 11\" is "
                                "$Q_1 \\cdot Q_0$ — both bits high at once. $Q_1 + Q_0$ is true in S1, S2 and "
                                "S3, so it would fire on three states out of four. $Q_0$ alone is true in "
                                "S1 as well as S3, which would announce a match after a single 1. "
                                "$Q_1\\overline{Q_0}$ is S2, one step too early."
                            ),
                        },
                        {
                            "prompt": "Row 101 is $Q_1 = 1$, $Q_0 = 0$, $x = 1$, and it has no neighbour to merge with. Write it as a product.",
                            "opts": ["Q1.Q0'.x", "Q1.Q0.x", "Q1'.Q0.x", "Q1.Q0'.x'"],
                            "a": 0,
                            "why": (
                                "A minterm is written by taking each variable as itself where the row has a "
                                "1 and complemented where the row has a 0, so `101` is "
                                "$Q_1\\overline{Q_0}x$ — module 3's rule, unchanged. It is the transition "
                                "S2 to S3, the one that completes a match, which is why it survives on its "
                                "own: nothing else in the table looks like it.\n\n"
                                "The finished pair is $Q_1^+ = Q_0\\overline{x} + Q_1\\overline{Q_0}x$ and "
                                "$Q_0^+ = x$. With $y = Q_1 Q_0$ that is three two-input gates, one "
                                "three-input gate and two inverters for the entire machine, output "
                                "logic included."
                            ),
                        },
                        {
                            "prompt": "Every row with $x = 1$ makes $Q_0^+$ true, and no other row does. Write $Q_0^+$.",
                            "opts": ["x", "Q0", "Q1.x", "x'"],
                            "a": 0,
                            "why": (
                                "$Q_0^+ = x$: the flip-flop holding $Q_0$ is wired straight to the input and "
                                "does nothing but delay it by one clock. That is not a fluke of arithmetic. "
                                "Look at which states have $Q_0 = 1$ — S1, whose meaning is \"the last bit "
                                "was a 1\", and S3, whose meaning ends in a 1 — so $Q_0$ *is* the previous "
                                "input bit, and the encoding happened to make that visible.\n\n"
                                "It is worth knowing that this is what a good encoding looks like from the "
                                "inside: a state bit that means something simple gives a next-state "
                                "function that is simple. Number the same four states in a different order "
                                "and neither the meaning nor the collapse survives."
                            ),
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "The patterns nobody assigned",
                    "minutes": 5,
                    "brief": r'''
The bottom rung: one rule, one arithmetic step, and the number that decides whether the
`default` branch of a case statement matters.

A state register is $n$ flip-flops, so it can hold $2^n$ patterns. A machine has $N$
states. Those two numbers are almost never equal, and the gap is the set of patterns the
register can hold that name nothing in your diagram.
''',
                    "prompt": "How many patterns can the state register hold that name no state?",
                    "note": "Use the smallest binary encoding — the fewest flip-flops that can name all the states.",
                    "figure": r'''
A controller that pushes one byte onto a two-wire serial bus. Its states, in the order
it walks through them:

```
  IDLE     waiting for a transfer to be asked for
  START    pulling the data line low while the clock line is still high
  ADDR6    \
  ADDR5     |
  ADDR4     |
  ADDR3     +-- the seven address bits, one per state
  ADDR2     |
  ADDR1     |
  ADDR0    /
  RW       the read/write bit
  ACK      releasing the data line and looking at what the far end does with it
  DATA7    \
  DATA6     |
  DATA5     |
  DATA4     +-- the eight data bits, one per state
  DATA3     |
  DATA2     |
  DATA1     |
  DATA0    /
  STOP     releasing the data line while the clock line is high
```
''',
                    "given": [
                        {"label": "States in the machine", "value": "20"},
                        {"label": "Encoding", "value": "binary, smallest that fits"},
                        {"label": "Rule", "value": "n flip-flops hold 2^n patterns"},
                    ],
                    "answer": 12,
                    "tol": 0.5,
                    "unit": "patterns",
                    "aside": "One-hot would use twenty flip-flops and leave $2^{20} - 20 = 1{,}048{,}556$ "
                             "unused patterns. That sounds far worse and is not, because the check "
                             "\"exactly one bit is set\" costs a few gates and catches every one of them, "
                             "where twelve scattered binary patterns have to be enumerated.",
                    "hint": "Find the smallest $n$ with $2^n \\ge 20$, then subtract the states from the patterns.",
                    "wrong": "0 assumes the count of states is a power of two, which it almost never is. "
                             "8 is $2^n$ for the wrong $n$: four flip-flops hold sixteen patterns and "
                             "cannot name twenty states.",
                    "why": (
                        "$2^4 = 16$ is too few and $2^5 = 32$ is enough, so the register is five "
                        "flip-flops wide and holds 32 patterns. Twenty of them name states, and "
                        "$32 - 20 = 12$ name nothing.\n\n"
                        "Those twelve are the whole reason a state machine needs a reset and a "
                        "`default` branch. The register comes up at power-on holding whatever the "
                        "silicon settles into, and there is better than a one-in-three chance that is one "
                        "of the twelve. If the next-state logic was minimised with those twelve rows "
                        "marked \"don't care\" — which is what a minimiser is entitled to do with "
                        "them — then what it does in one of them is whatever happened to make the "
                        "equations smaller, and quite often that is nothing at all: the pattern maps to "
                        "itself and the machine never moves again.\n\n"
                        "Note that the ratio gets worse before it gets better. A machine with 17 states "
                        "still needs five flip-flops and wastes 15 patterns; one with 32 wastes none. "
                        "Adding a state to a 16-state machine doubles the register's unused space, which "
                        "is a good reason to notice when a design is sitting just above a power of two."
                    ),
                },
                {
                    "title": "How fast the loop can be clocked",
                    "minutes": 8,
                    "brief": r'''
Every path in a synchronous design runs from a flip-flop, through some logic, to a
flip-flop. A state machine's longest one is special: it starts at the state register,
goes through the next-state logic, and ends **back at the state register**. That loop is
the one path you cannot pipeline, because inserting a flip-flop inside it does not make
the machine faster — it makes it a different machine, one that takes two cycles per
state.

So whatever the loop costs is what the clock period must be, and the arithmetic is
module 4's setup inequality with one twist: the launching flip-flop and the capturing
flip-flop are both in the same register, so the skew that matters is skew *across* the
state register rather than between two separate ones.

Module 4's form, with $t_{skew}$ counted positive when the capture edge arrives **late**:

$$T + t_{skew} \ge t_{cq} + t_{pd} + t_{su}$$
''',
                    "prompt": "What is the highest clock frequency this machine can be run at?",
                    "note": "Give the answer in megahertz. The capture edge arrives early, not late.",
                    "figure": r'''
```
        +-----------------------------------------+
        |                                         |
        |     +-------------------+               |
        +---->|  next-state logic |----> D  [ state register ] ---> Q
   x -------->|   worst path      |            ^
              +-------------------+            |
                                             clock
```

The worst path leaves one flip-flop of the state register, crosses the next-state logic,
and arrives at the D input of another flip-flop of the same register. The clock tree
delivers the edge to those two flip-flops 0.20 ns apart, and it is the **capturing** one
that gets it first.
''',
                    "given": [
                        {"label": "Clock to output, $t_{cq}$", "value": "0.42 ns"},
                        {"label": "Next-state logic, worst path $t_{pd}$", "value": "2.10 ns"},
                        {"label": "Setup time, $t_{su}$", "value": "0.28 ns"},
                        {"label": "Clock skew across the state register", "value": "0.20 ns, capture edge early"},
                        {"label": "Output logic delay", "value": "not on this path"},
                    ],
                    "answer": 333.33,
                    "tol": 2.0,
                    "unit": "MHz",
                    "aside": "The output logic is genuinely not in this budget. It runs from the state "
                             "register to whatever is downstream, so it belongs to that path's period, "
                             "not to the machine's own loop.",
                    "hint": "An early capture edge is a negative $t_{skew}$, so it moves to the other "
                            "side of the inequality and *adds* to what the period must cover. Sum the "
                            "four times, then invert.",
                    "wrong": "377 MHz is what you get by leaving the skew out — 2.65 ns of budget "
                             "rather than 3.00. 408 MHz subtracts the skew instead of adding it, which "
                             "is what it would do if the capture edge arrived late rather than early.",
                    "why": (
                        "The capture edge arriving 0.20 ns early is $t_{skew} = -0.20$ ns, so\n\n"
                        "$$T \\ge t_{cq} + t_{pd} + t_{su} - t_{skew} = 0.42 + 2.10 + 0.28 + 0.20$$\n\n"
                        "```\n"
                        " T >= 0.42 + 2.10 + 0.28 + 0.20 = 3.00 ns\n"
                        " f  = 1 / 3.00 ns               = 333.3 MHz\n"
                        "```\n\n"
                        "The sign of the skew is the whole question and it is worth being able to say "
                        "why it goes that way. The capturing flip-flop wants its D input still by the "
                        "time *its* edge arrives. Moving that edge earlier gives the data less time to "
                        "get there, so an early capture edge eats into the period exactly as a slower "
                        "gate would. Move it later instead and setup gets easier — and hold gets harder, "
                        "which is the trade module 4 laid out.\n\n"
                        "Two things follow for a state machine specifically. The 2.10 ns of next-state "
                        "logic is 70% of the budget, and it is the part the encoding controls: the first "
                        "reading turned eleven gates into four by renumbering the states, and on a deeper "
                        "machine that is levels of logic, not just gates. And there is nowhere else to "
                        "go once the encoding is spent — you cannot pipeline a loop that feeds itself, so "
                        "the remaining moves are to split the machine into two smaller ones or to "
                        "compute both candidate next states in parallel and select between them at the "
                        "last gate."
                    ),
                },
                {
                    "title": "How long a synchroniser buys you",
                    "minutes": 11,
                    "brief": r'''
Every state machine that talks to the outside world has at least one input that knows
nothing about its clock. Module 4 gave the model for what that costs: an input that
changes inside the setup window leaves the flip-flop balanced between its two states,
the imbalance grows like $e^{t/\tau}$, and the mean time between failures is

$$\text{MTBF} = \frac{e^{t_r/\tau}}{T_0\,f_c\,f_d}$$

where $t_r$ is how long the metastable output is left alone before anything reads it,
$\tau$ and $T_0$ characterise the flip-flop, $f_c$ is the clock and $f_d$ is the rate at
which the asynchronous input changes.

The state-machine part is the value of $t_r$. The last flip-flop of the synchroniser
does not hand its output to another flip-flop — it hands it to the **next-state logic**,
so the logic delay comes out of the resolving time as well as the setup time. Each
synchroniser flip-flop before the last one adds a whole clock period, exactly as module
4's second flip-flop did.

The design below has two flip-flops. That is the standard answer, and the point of the
question is to find out whether the standard answer is enough here.
''',
                    "prompt": "What is the mean time between synchroniser failures?",
                    "note": "Give the answer in days.",
                    "figure": r'''
```
             +--------+        +--------+
  req ------>|D      Q|------->|D      Q|-----> next-state logic -----> D of the
 (async)     |        |        |        |        (1.40 ns)              state register
             |  FF1   |        |  FF2   |
             +---^----+        +---^----+
                 |                 |
   clock --------+-----------------+

  t_r  =  one whole clock period for FF1,
          plus what is left of the next period after the logic and the setup time
```
''',
                    "given": [
                        {"label": "Clock frequency $f_c$", "value": "400 MHz"},
                        {"label": "Synchroniser flip-flops", "value": "2"},
                        {"label": "Next-state logic after the synchroniser", "value": "1.40 ns"},
                        {"label": "Setup time of the state register", "value": "0.15 ns"},
                        {"label": "Resolution time constant $\\tau$", "value": "0.12 ns"},
                        {"label": "Metastability window $T_0$", "value": "0.30 ns"},
                        {"label": "Rate the request changes, $f_d$", "value": "4 MHz"},
                    ],
                    "answer": 73.83,
                    "tol": 1.5,
                    "unit": "days",
                    "aside": "A third flip-flop costs one more cycle of latency and takes the same "
                             "circuit to about 226 million years. Every extra $\\tau$ of resolving time "
                             "multiplies the MTBF by $e$, and a whole clock period here is twenty of them.",
                    "hint": "$t_r = 2T - t_{pd} - t_{su}$ with $T = 2.5$ ns. Work out the exponent "
                            "before anything else, and keep the denominator in per-second units: "
                            "$T_0 f_c f_d$ has dimensions of one over time.",
                    "wrong": "5.7 milliseconds is the one-flip-flop answer — a real number for a real "
                             "circuit, and the reason nobody ships one. If you got something near "
                             "$10^{13}$, the exponential was evaluated but the denominator was left out.",
                    "why": (
                        "The clock period is $T = 1/400\\ \\text{MHz} = 2.5$ ns. FF1's output has a whole "
                        "period before FF2 looks at it, and FF2's output has what is left of the next "
                        "period after the next-state logic and the state register's setup time:\n\n"
                        "```\n"
                        " t_r = 2 x 2.50 - 1.40 - 0.15          = 3.45 ns\n"
                        " exponent      3.45 / 0.12             = 28.75\n"
                        " e^28.75                               = 3.062e12\n"
                        " T0 x fc x fd = 0.30e-9 x 4e8 x 4e6    = 4.80e5 per second\n"
                        " MTBF = 3.062e12 / 4.80e5              = 6.379e6 s\n"
                        " in days       6.379e6 / 86400         = 73.8 days\n"
                        "```\n\n"
                        "Seventy-four days is not a passing grade. A thousand units in the field see "
                        "one of these failures roughly every two hours between them, and each failure "
                        "is a machine that took a transition nothing in the diagram allows. The "
                        "two-flip-flop rule is a rule of thumb attached to clock rates around 100 MHz; "
                        "at 400 MHz a period is only twenty $\\tau$, and twenty $\\tau$ is only a factor "
                        "of $e^{20} = 4.9 \\times 10^8$.\n\n"
                        "Run the same numbers with a third flip-flop and $t_r$ becomes "
                        "$3 \\times 2.5 - 1.55 = 5.95$ ns, the exponent becomes 49.58, and the MTBF "
                        "becomes $7.1 \\times 10^{15}$ s — about 226 million years. One flip-flop, one "
                        "cycle of latency, and nine orders of magnitude.\n\n"
                        "Two things this calculation does not cover. It is a model fitted to measured "
                        "silicon, and $\\tau$ degrades as the supply falls and the temperature rises, so "
                        "the number to design against is the worst corner and not the typical one. And "
                        "it says nothing about a bus: eight of these synchronisers on eight wires each "
                        "resolve independently, so the byte that arrives can be a mixture of the old "
                        "value and the new one — a word that was never sent, at a rate that has nothing "
                        "to do with this MTBF. That needs a Gray code or a handshake, not more "
                        "flip-flops."
                    ),
                },
                {
                    "title": "What the encoding really costs in power",
                    "minutes": 12,
                    "brief": r'''
The top of the ladder, and the received wisdom it tests is "one-hot switches fewer bits,
so it saves power". Two things have to be counted before that can be believed: how many
bits actually change per clock in each encoding, and what the clock net costs when it has
to reach four times as many flip-flops.

Module 5 established that taking a node up to $V$ and back down again dissipates $CV^2$
joules. A single transition — up, or down, but not both — is half of that, $\tfrac12
CV^2$. So the switching power of a register is $\tfrac12 CV^2$ multiplied by the number
of bit transitions it makes per second, and that number depends on the encoding.

The machine is the twenty-state serial controller from the first question, running a
transfer: it advances one state per clock, walks all twenty in order, and returns to
IDLE from STOP. Number the states 0 to 19 in that order for the binary encoding.

Ignore the next-state logic and ignore leakage. This is the state register's outputs
plus the clock net that reaches them.
''',
                    "prompt": "What total dynamic power does the binary-encoded version dissipate?",
                    "note": "Give the answer in microwatts, to two decimal places.",
                    "figure": r'''
The register walks `00000, 00001, 00010, ... , 10011` and then back to `00000`. The
number of bits that change on each step is the Hamming distance between neighbouring
codes:

```
  0 -> 1   1 bit      8 -> 9    1 bit     16 -> 17   1 bit
  1 -> 2   2 bits     9 -> 10   2 bits    17 -> 18   2 bits
  2 -> 3   1 bit     10 -> 11   1 bit     18 -> 19   1 bit
  3 -> 4   3 bits    11 -> 12   3 bits    19 ->  0   ? bits
  4 -> 5   1 bit     12 -> 13   1 bit
  5 -> 6   2 bits    13 -> 14   2 bits
  6 -> 7   1 bit     14 -> 15   1 bit
  7 -> 8   4 bits    15 -> 16   5 bits
```

The wrap is the one left to work out: `10011` back to `00000`.

The clock net is one node that goes high and low once every clock period, so it
completes $f$ full cycles a second whatever the machine is doing.
''',
                    "given": [
                        {"label": "States, walked one per clock", "value": "20"},
                        {"label": "Clock frequency", "value": "100 MHz"},
                        {"label": "Supply", "value": "1.8 V"},
                        {"label": "Capacitance on each flip-flop output node", "value": "8 fF"},
                        {"label": "Clock net capacitance", "value": "30 fF of trunk plus 4.5 fF per flip-flop reached"},
                        {"label": "Energy of one transition of a node", "value": "½ C V²"},
                    ],
                    "answer": 19.47,
                    "tol": 0.15,
                    "unit": "µW",
                    "aside": "The one-hot version of the same machine comes to 41.47 µW — and its state "
                             "bits are the *more* expensive half of that comparison, not the less.",
                    "hint": "Add the Hamming distances to get the transitions per twenty clocks, then "
                            "divide by twenty for the average per clock. Work out the clock net's "
                            "capacitance from the number of flip-flops before computing its power.",
                    "wrong": "2.46 µW is the state bits on their own, with the clock left out, and it is "
                             "an eighth of the answer. 23.49 µW treats every one of the five bits as "
                             "changing on every clock; the average is 1.9 bits, not 5.",
                    "why": (
                        "**The state bits.** The wrap is `10011` to `00000`, which changes three bits, "
                        "so the distances sum to\n\n"
                        "```\n"
                        " 1+2+1+3+1+2+1+4  = 15   (states  0 -> 8)\n"
                        " 1+2+1+3+1+2+1+5  = 16   (states  8 -> 16)\n"
                        " 1+2+1            =  4   (states 16 -> 19)\n"
                        " 3                =  3   (the wrap, 19 -> 0)\n"
                        " total                     38 transitions per 20 clocks\n"
                        "```\n\n"
                        "an average of $38/20 = 1.9$ bit transitions per clock. Each costs\n"
                        "$\\tfrac12 CV^2 = \\tfrac12 \\times 8\\ \\text{fF} \\times 1.8^2 = "
                        "1.296 \\times 10^{-14}$ J, so\n\n"
                        "```\n"
                        " P_state = 1.9 x 1.296e-14 x 100e6 = 2.462e-6 W   (2.46 uW)\n"
                        "```\n\n"
                        "**The clock net.** Five flip-flops, so\n"
                        "$C_{clk} = 30 + 5 \\times 4.5 = 52.5$ fF, one full cycle per period:\n\n"
                        "```\n"
                        " P_clk = 52.5e-15 x 1.8^2 x 100e6  = 1.701e-5 W   (17.01 uW)\n"
                        "```\n\n"
                        "**Together:** $2.46 + 17.01 = 19.47\\ \\mu$W, and the counting is 12.6% of it.\n\n"
                        "Now the comparison the question exists for. One-hot changes exactly two bits on "
                        "every transition between distinct states — one flip-flop leaves, one arrives — "
                        "so its state bits burn $2 \\times 1.296\\times10^{-14} \\times 10^8 = 2.59\\ "
                        "\\mu$W, which is *more* than binary's 2.46 µW, not less. The claim that one-hot "
                        "saves switching power in the register is simply false for a machine that walks "
                        "its states in order: binary averages 1.9 transitions a clock and one-hot always "
                        "spends 2.\n\n"
                        "And the register is the small half anyway. Twenty flip-flops make the clock net "
                        "$30 + 20 \\times 4.5 = 120$ fF, which burns 38.88 µW, so the one-hot machine "
                        "totals 41.47 µW against 19.47 — a factor of 2.1, essentially all of it the "
                        "clock arriving at four times as many flip-flops.\n\n"
                        "None of which makes one-hot a bad choice; it makes the *reason* for choosing it "
                        "a different one. One-hot buys shallow next-state logic and free state "
                        "decoding, and on an FPGA it buys them with flip-flops that were sitting there "
                        "unused. It does not buy power. If power is the target the lever is the clock: "
                        "gate it at the root of the tree while the controller is idle, and 17 of these "
                        "19.47 µW go away."
                    ),
                },
            ],
            "derive": {
                "title": "The size of the memory that could replace the next-state logic",
                "minutes": 13,
                "brief": r'''
The state table in the first reading was a truth table — inputs on the left, outputs on
the right, one row per combination. Module 3 turned tables like that into gates, but
there has always been another option: **look the row up**. A memory addressed by the
present state and the inputs, whose contents are the next state and the outputs, is a
complete state machine with no logic design in it at all. That is what "microcoded"
means, and it is how control units were built for thirty years.

The question is how big the memory has to be, and the answer decides when the idea is
sensible. Write $n$ for the number of state bits, $k$ for the number of input bits, $p$
for the number of output bits, and $N$ for the number of states.
''',
                "vars": ["n", "k", "p", "N", "B"],
                "steps": [
                    {
                        "prompt": "The memory has to be addressed by everything the next-state function depends on. Write the number of address lines.",
                        "given": "The next-state function is a function of the present state and the inputs, and of nothing else.",
                        "answer": "n + k",
                        "placeholder": "a count plus a count",
                        "hint": "The present state is $n$ bits wide and the inputs are $k$ bits wide; every one of them has to reach the memory.",
                        "deconstruct": [
                            "The state register contributes $n$ address lines.",
                            "The inputs contribute $k$ more.",
                            "There is nothing else the function looks at.",
                        ],
                    },
                    {
                        "prompt": "Write the number of rows that memory has.",
                        "answer": "2^{n+k}",
                        "placeholder": "two to the power of something",
                        "hint": "An address of $a$ lines selects one of $2^a$ rows — the same doubling as every extra bit in module 1.",
                        "deconstruct": [
                            "Each address line doubles the number of distinguishable addresses.",
                            "With $n+k$ lines there are $2^{n+k}$ of them, and every one has to hold a row.",
                        ],
                    },
                    {
                        "prompt": "Each row has to supply everything the memory is replacing: the next state and the outputs. Write the width of one row in bits.",
                        "answer": "n + p",
                        "placeholder": "another sum of two counts",
                        "hint": "The next state is a pattern $n$ bits wide, and there are $p$ output bits to emit alongside it.",
                        "deconstruct": [
                            "The next state goes back to the state register, so it is $n$ bits.",
                            "The outputs are $p$ bits.",
                            "Both come out of the same row, so the row is $n + p$ wide.",
                        ],
                    },
                    {
                        "prompt": "Write the total number of bits $B$ the memory has to hold.",
                        "answer": "2^{n+k}(n+p)",
                        "placeholder": "rows times width",
                        "hint": "Every row is the same width, so the total is simply the count of rows multiplied by that width.",
                        "deconstruct": [
                            "There are $2^{n+k}$ rows.",
                            "Each is $n+p$ bits wide.",
                            "Multiply them.",
                        ],
                    },
                    {
                        "prompt": "Now encode the same machine one-hot, so the state register is $N$ bits wide instead of $n$. Write the total number of bits that memory would need.",
                        "given": "Nothing else about the machine changes: same $k$ inputs, same $p$ outputs, same behaviour.",
                        "answer": "2^{N+k}(N+p)",
                        "placeholder": "the same shape, with a different width",
                        "hint": "Substitute $N$ for $n$ everywhere the state width appeared — in the address and in the row.",
                        "deconstruct": [
                            "The state now occupies $N$ address lines, so there are $2^{N+k}$ rows.",
                            "Each row must supply an $N$-bit next state and $p$ outputs.",
                            "Multiply, exactly as before.",
                        ],
                    },
                ],
                "closing": r'''
$$B_{\text{binary}} = 2^{n+k}\left(n + p\right), \qquad
  B_{\text{one-hot}} = 2^{N+k}\left(N + p\right)$$

Put the twenty-state serial controller into both. Say it has $k = 2$ inputs (a "go"
request and the acknowledge bit read back off the bus) and $p = 4$ outputs. Binary needs
$n = 5$ state bits:

```
  binary   rows  2^(5+2) = 128    width 5+4 =  9    ->        1,152 bits
  one-hot  rows  2^(20+2) = 4,194,304   width 20+4 = 24 -> 100,663,296 bits
```

A thousand-odd bits is a small ROM — smaller than the gates it replaces, and it can be
changed after the chip is made, which is the entire attraction. A hundred megabits is
not a design, it is a joke: 12 megabytes of memory to run a machine that fits in eight
gates.

That gap is the point, and it inverts the advice from the reading. One-hot minimises
gates by making the state wide and sparse; a memory charges $2^{\text{width}}$ for
exactly that width, so the encoding that is cheapest in logic is catastrophic in a
lookup table. Two implementations of the same table, and the cost functions point in
opposite directions — which is a good reason to be suspicious of any rule about encoding
that does not say what the state is being built out of.

Two limits worth naming.

**The inputs are in the exponent too.** With $n = 5$ and $p = 4$ fixed, going from $k=2$
to $k=8$ inputs takes the ROM from 1,152 bits to $2^{13} \times 9 = 73{,}728$ bits, and
$k = 16$ takes it to 18.9 megabits. Real microcoded machines never put every input in
the address. They store a **next-address field** plus a few bits that name *which single
condition to test*, and a small multiplexer picks that one input out of the sixteen. The
memory then grows with the number of states rather than with $2^{\text{inputs}}$, at the
cost of only being able to branch on one thing at a time.

**A memory is not free of the timing loop either.** The access time of the ROM sits in
exactly the place the next-state logic sat in, so it is bounded by the same inequality
the second numeric question worked out, and a ROM is generally slower than four levels
of gates. Microcode's advantages were flexibility and design effort, never speed — which
is why it lost ground the moment logic synthesis got good, and why it survives where the
control is genuinely complicated. Module 10 picks up the same array and asks what else
can be built out of it.
''',
            },
            "lab": {
                "title": "The same detector as a Moore machine and as a Mealy machine",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
The state table from the drill, executed — and beside it the Mealy version of the
same machine, so the timing difference stops being a claim and becomes a printout.

**`next_state(state, x)`** — the transition table. States are the strings `"S0"` to
`"S3"`, and `x` is 0 or 1.

**`moore_output(state)`** — 1 in S3, 0 elsewhere. The output depends on the state and
nothing else.

**`mealy_output(state, x)`** — 1 when the machine is in S2 and the arriving bit is a
1, because that is the moment the third symbol of the pattern shows up. The state has
not moved yet.

**`run_moore(bits)`** and **`run_mealy(bits)`** — both return `(states, outputs)` with
one entry per input bit. Entry `i` is what is true **during** tick `i`: `states[i]` is
the state the machine is in as bit `i` arrives, and `outputs[i]` is the output visible
during that tick. Record first, then step.

Run `main.py` on `1 0 1 0 1 0`. Both machines report two matches, and every Mealy
1 sits exactly one tick to the left of the corresponding Moore 1.
''',
                "files": [{"name": "main.py", "content": r'''
STATES = ("S0", "S1", "S2", "S3")


def next_state(state, x):
    """Where the machine goes from `state` when the bit `x` arrives."""
    # TODO: S0 -> S1 on a 1; S1 -> S2 on a 0, S1 on a 1; S2 -> S0 on a 0, S3 on a 1;
    # S3 -> S2 on a 0, S1 on a 1.
    return "S0"


def moore_output(state):
    """The Moore output: a function of the state alone."""
    # TODO
    return 0


def mealy_output(state, x):
    """The Mealy output: a function of the state and the bit arriving now."""
    # TODO
    return 0


def run_moore(bits, start="S0"):
    """(states, outputs), one entry per bit, recorded before the state moves."""
    # TODO
    return [], []


def run_mealy(bits, start="S0"):
    """(states, outputs), one entry per bit, recorded before the state moves."""
    # TODO
    return [], []


def row(name, seq):
    return name + " " + "".join(str(v) for v in seq)


if __name__ == "__main__":
    BITS = [1, 0, 1, 0, 1, 0]
    print(row("in   ", BITS))
    print(row("moore", run_moore(BITS)[1]))
    print(row("mealy", run_mealy(BITS)[1]))
    print("states:", run_moore(BITS)[0])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
STATES = ("S0", "S1", "S2", "S3")

TABLE = {
    ("S0", 0): "S0", ("S0", 1): "S1",
    ("S1", 0): "S2", ("S1", 1): "S1",
    ("S2", 0): "S0", ("S2", 1): "S3",
    ("S3", 0): "S2", ("S3", 1): "S1",
}


def next_state(state, x):
    """Where the machine goes from `state` when the bit `x` arrives."""
    return TABLE[(state, x)]


def moore_output(state):
    """The Moore output: a function of the state alone."""
    return 1 if state == "S3" else 0


def mealy_output(state, x):
    """The Mealy output: a function of the state and the bit arriving now."""
    return 1 if state == "S2" and x == 1 else 0


def run_moore(bits, start="S0"):
    """(states, outputs), one entry per bit, recorded before the state moves."""
    q = start
    states, out = [], []
    for x in bits:
        states.append(q)
        out.append(moore_output(q))
        q = next_state(q, x)
    return states, out


def run_mealy(bits, start="S0"):
    """(states, outputs), one entry per bit, recorded before the state moves."""
    q = start
    states, out = [], []
    for x in bits:
        states.append(q)
        out.append(mealy_output(q, x))
        q = next_state(q, x)
    return states, out


def row(name, seq):
    return name + " " + "".join(str(v) for v in seq)


if __name__ == "__main__":
    BITS = [1, 0, 1, 0, 1, 0]
    print(row("in   ", BITS))
    print(row("moore", run_moore(BITS)[1]))
    print(row("mealy", run_mealy(BITS)[1]))
    print("states:", run_moore(BITS)[0])
'''}],
                "hints": [
                    "A dictionary keyed by `(state, x)` is the state table written out, and it makes `next_state` a single lookup.",
                    "`moore_output` never sees the input; if your version takes `x` as an argument you have written a Mealy machine by accident.",
                    "Both `run_` functions have the same shape: append the state, append the output, then advance. Doing it in that order is what makes entry `i` describe tick `i`.",
                    "The Mealy output looks at the state *before* the step, so compute it before overwriting `q`.",
                ],
                "tests": [
                    {"name": "the transition table matches the drill", "code": r'''
_want = {("S0", 0): "S0", ("S0", 1): "S1", ("S1", 0): "S2", ("S1", 1): "S1",
         ("S2", 0): "S0", ("S2", 1): "S3", ("S3", 0): "S2", ("S3", 1): "S1"}
for (_s, _x), _exp in _want.items():
    assert next_state(_s, _x) == _exp, f"next_state({_s!r}, {_x}) should be {_exp!r}, got {next_state(_s, _x)!r}"
'''},
                    {"name": "the two output functions look at different things", "code": r'''
assert [moore_output(_s) for _s in STATES] == [0, 0, 0, 1], \
    "the Moore output is 1 in S3 and nowhere else"
assert mealy_output("S2", 1) == 1, "S2 with a 1 arriving is the moment the pattern completes"
assert mealy_output("S2", 0) == 0 and mealy_output("S3", 1) == 0, \
    "the Mealy output depends on both the state and the bit"
'''},
                    {"name": "one detection, in both machines", "code": r'''
_states, _moore = run_moore([1, 0, 1, 0])
assert _states == ["S0", "S1", "S2", "S3"], f"got {_states}"
assert _moore == [0, 0, 0, 1], f"the Moore output rises the tick after the match completes; got {_moore}"
_, _mealy = run_mealy([1, 0, 1, 0])
assert _mealy == [0, 0, 1, 0], f"the Mealy output rises on the tick the match completes; got {_mealy}"
'''},
                    {"name": "overlapping matches are both counted", "code": r'''
_, _moore = run_moore([1, 0, 1, 0, 1, 0])
_, _mealy = run_mealy([1, 0, 1, 0, 1, 0])
assert sum(_moore) == 2 and sum(_mealy) == 2, \
    f"10101 contains two overlapping matches; got {sum(_moore)} and {sum(_mealy)}"
assert _moore == [0, 0, 0, 1, 0, 1], f"got {_moore}"
assert _mealy == [0, 0, 1, 0, 1, 0], f"got {_mealy}"
_, _none = run_moore([1, 1, 1, 0, 0])
assert sum(_none) == 0, "111 00 contains no 101"
'''},
                    {"name": "Mealy leads Moore by exactly one tick, on every input", "code": r'''
import itertools
for _n in range(1, 11):
    for _bits in itertools.product([0, 1], repeat=_n):
        _, _mo = run_moore(list(_bits))
        _, _me = run_mealy(list(_bits))
        for _i in range(_n - 1):
            assert _me[_i] == _mo[_i + 1], \
                f"on {_bits} at tick {_i}: mealy {_me[_i]} should equal moore {_mo[_i + 1]}"
'''},
                    {"name": "the Mealy output counts occurrences of 101 exactly", "code": r'''
import itertools
def _occurrences(bs):
    return sum(1 for _i in range(len(bs) - 2) if list(bs[_i:_i + 3]) == [1, 0, 1])
for _n in range(3, 12):
    for _bits in itertools.product([0, 1], repeat=_n):
        _, _me = run_mealy(list(_bits))
        assert sum(_me) == _occurrences(list(_bits)), \
            f"{_bits} contains {_occurrences(list(_bits))} matches, the machine found {sum(_me)}"
'''},
                ],
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "Memory, and logic you can change your mind about",
            "summary": "A truth table with $2^n$ rows is a memory with $2^n$ words. Once that lands, ROMs, FPGAs and lookup tables stop being three subjects.",
            "concepts": [
                "A **memory array** is a decoder and a grid. The $n$ address lines drive a decoder whose one active output selects a row, and the cells on that row put their contents onto the data lines. A part described as 4 K × 8 holds 4096 words of 8 bits: twelve address lines, eight data lines, 32768 bits of storage.",
                "An **SRAM** cell is two inverters in a loop — module 4's latch, in miniature — and holds its value for as long as it is powered, at a cost of six transistors. A **DRAM** cell is one transistor and one capacitor: far smaller, but the charge drains away in milliseconds, so every row must be read and written straight back, continuously, whether or not anyone is using the memory. Density traded against a refresh controller.",
                "Several devices sharing one set of wires need **tri-state** outputs: driven high, driven low, or disconnected altogether. Exactly one device is enabled at a time — by a decoder, naturally — and the rest let go of the bus. Two devices driving at once is not a wrong logic level; it is a low-resistance path from the supply to ground through both of their output transistors.",
                "A **ROM is a truth table you look up**. Address it with the inputs and the data lines are the outputs, so any function of $n$ inputs and $m$ outputs fits in a $2^n \\times m$ ROM with no logic design at all. The catch is in the exponent: every extra input doubles the part, which is why a ROM is the right answer for a small decoder and a ridiculous one for a 32-bit adder.",
                "An **FPGA** is that idea made small and repeated. A **lookup table** is a tiny RAM — typically six inputs and therefore 64 bits — holding one column of a truth table, with a flip-flop beside it and a programmable network joining thousands of them together. Nothing in the silicon knows what circuit it is; the contents of the tables do, and that is what \"programming\" the chip means.",
            ],
            "read": [
                {
                    "title": "Twelve wires, and four thousand places to put a byte",
                    "minutes": 13,
                    "body": r'''
Module 4 built a circuit that holds one bit, and module 8 put a great many of them
side by side without once asking what it costs to *reach* one of them. That is the
question a memory part exists to answer, and answering it is most of the design.
Holding a bit is not the hard part — there are two well-known ways to do it and this
reading covers both. Picking one bit out of thirty-two thousand, using twelve wires,
is the hard part.

## Twelve wires and four thousand places

Take a small memory: 4096 bytes. Build it the obvious way, as 4096 groups of eight
latches, and each group needs an enable line of its own. Bring those out to the edge
of the chip and the part has 4096 enable pins. Nobody has ever shipped that. The part
that actually exists has twelve address pins, eight data pins, and a handful of
control lines.

Twelve wires is not a shortage. Module 1 said that $n$ wires carry $2^n$ patterns,
and $2^{12} = 4096$ — exactly the number of bytes there are to choose between. The
information is all present on the pins. What is missing is a circuit that turns *one
pattern out of 4096* into *one wire out of 4096 being true*, and that circuit is a
**decoder**.

Everything else about a memory array follows from the decoder, including the shape of
the silicon.

## A decoder is a truth table with the OR taken off

Module 3 turned a truth table into a sum of products: one AND term per row whose
output is 1, all of them ORed together. A decoder is that same construction with the
final OR removed and every row brought out on a wire of its own. Output number $k$ is
the minterm of row $k$ — the AND of all twelve address bits, each taken as itself
where $k$ has a 1 in that place and complemented where $k$ has a 0.

$$\text{out}_0 = \overline{A_{11}}\,\overline{A_{10}}\cdots\overline{A_0},
\qquad
\text{out}_{4095} = A_{11}A_{10}\cdots A_0$$

Exactly one output is true for any address, for the same reason exactly one row of a
truth table matches any given input: the minterms are mutually exclusive by
construction. The word for a bundle of wires with exactly one of them true is
**one-hot**, which module 9 met as a way of encoding states. A decoder is a machine
for turning binary into one-hot, and that is the only trick in this entire module.

The wire it drives is called a **word line**, and switching it on is what *selecting*
means in hardware: it opens the access transistors of every cell on that row at once.

## Why nobody builds the array as a list

Wire that up literally and the chip is 4096 rows tall and eight cells wide. Two things
go wrong, and the gate count is not either of them.

The first is shape. A memory cell is roughly square, so a 4096 x 8 array is five
hundred times taller than it is wide. It does not fit on a die alongside anything
else, and the wiring needed to reach the far end of it is longer than the array.

The second is the vertical wires. Each of the eight **bit lines** runs the full height
of the array with 4096 cells hanging off it, and every one of those cells adds
capacitance to that line whether it is selected or not. Reading a memory means moving
that capacitance, and the next reading shows exactly how little signal a cell has to
spend on the job.

So the array is folded. Split the twelve address bits into two halves: the top six
pick one of 64 word lines, and the bottom six pick which slice of that row reaches the
data pins.

### Worked: a 4 K x 8 part, both ways

```
  as a list                             folded 64 x 64
  ---------------------------------     ---------------------------------
  address lines           12            address lines           12
  words                 4096              row address bits       6
  data lines               8              column address bits    6
  cells        4096 x 8 = 32768         word lines              64
  decoder outputs       4096            cells on a word line  64 x 8 = 512
  decoder gates         4096            row decoder      64 gates of 6 in
    each with 12 inputs                 column decoder   64 gates of 6 in
  gate inputs   4096 x 12 = 49152       gates in total         128
  array shape     4096 x 8 cells        gate inputs  128 x 6 = 768
  bit line load         4096 cells      array shape      64 x 512 cells
                                        cells      64 x 512 = 32768
                                        bit line load           64 cells
```

The same 32768 cells both times — nothing was saved on storage, and nothing could be.
What changed is everything around them: 128 gates instead of 4096, 768 gate inputs
instead of 49152, an array eight times wider than it is tall instead of five hundred
times taller than it is wide, and a bit line carrying 64 cells instead of 4096.

That last number is the one that matters most, and it is worth knowing why. The two
decoders together have $64 + 64 = 128$ outputs where the flat one had 4096, and in
general splitting an $n$-bit address into halves takes the decoder from $2^n$ gates to
$2 \times 2^{n/2}$. At $n = 12$ that is 32 times fewer. At $n = 20$ it is five hundred
times fewer.

There is a detail in that table worth pausing on. When a word line goes up, all 512
cells on it drive their bit lines — the whole row is read, and the column decoder then
throws away 504 of the 512 bits. Wasteful, until you notice that fetching a *second*
byte from the same row costs almost nothing, because the row is already open. That
observation is the origin of DRAM page mode, of the burst transfer, and ultimately of
why a cache line is 64 bytes rather than 1.

## Reading the number printed on the part

A part described as **4 K x 8** holds 4096 words of 8 bits. Here K means 1024, not
1000, and it is worth being clear about why: the reachable count is $2^n$ for a whole
number of address lines, so the round numbers in this subject are powers of two and
the prefixes were bent to match them.

Two mistakes are common enough to name.

The first is reading 4 K x 8 as "4096 bits". It is 4096 *words*, and the part holds
$4096 \times 8 = 32768$ bits. The temptation is real, because 4096 is the number you
just worked out from the address lines and it feels like the answer.

The second is letting the two numbers into each other's arithmetic. The 4 K sets the
address count and never appears in the data width; the 8 sets the data width and never
appears in the address count. A part twice as wide has the same twelve address lines
and twice the pins on the other side.

### Worked: a 1 M x 16 part, and why it has ten address pins

```
  words                1 M = 1048576 = 2^20
  address bits          20
  data lines            16
  cells        1048576 x 16 = 16777216 = 16 Mbit
  folded, per bit plane      1024 x 1024
  row address bits      10
  column address bits   10
  address PINS          10
```

The last line is not a typo. A DRAM sends the row address and the column address down
the same ten pins, one after the other, latched by two separate strobes — this is
what RAS and CAS are, and it is why a DRAM read has always taken two steps. Ten pins
saved per part is worth having when a module carries sixteen of them and a
motherboard carries four modules.

## What sits in each square

The grid is settled; now the cell. There are two answers in wide use and they trade
the same thing against each other.

An **SRAM** cell is module 4's latch, shrunk. Two inverters in a loop, four
transistors, each one holding the other's input where it is; plus two access
transistors that connect the loop to the bit lines when the word line goes up. Six
transistors, and it holds its value for as long as the supply is present, with no
help from anybody. Reading it is easy because the loop is actively driving.

A **DRAM** cell is one capacitor and one transistor. The capacitor is charged or it is
not; the transistor connects it to the bit line when the word line goes up. Nothing
holds it up. The charge sits on a capacitor with a reverse-biased junction under it,
and reverse-biased junctions leak.

### Worked: how long a DRAM cell keeps its bit

```
  cell capacitance          C_s = 25 fF
  supply                    V   = 1.2 V
  charge on a stored 1      Q   = 25e-15 F x 1.2 V = 30 fC
```

The next reading works out that a full cell gives the sense amplifier 66.7 mV of
signal, and that the amplifier needs about 50 mV to decide reliably. So the cell is
allowed to lose the difference before a read starts failing:

```
  fraction of the signal still needed   50 / 66.7      = 0.75
  voltage the cell may lose             0.25 x 1.2 V   = 0.30 V
  charge that is                        25 fF x 0.30 V = 7.5 fC
  worst-cell leakage current                           = 120 fA
  time to leak it away          7.5e-15 C / 120e-15 A  = 62.5 ms
```

Sixty-two and a half milliseconds, and every DRAM datasheet in the world specifies 64
ms. That is not a coincidence; the arithmetic above is the arithmetic the standard was
written from. Note which cell it is about: not the average cell, the *worst* cell on
the part, because the part fails when any one of eight billion of them does. And
leakage roughly doubles for every 10 degrees, which is why the same devices are
specified at 32 ms above 85 C.

## Refresh is a read you throw away

The consequence is that a DRAM has to be read continuously whether or not anyone is
using it. The controller walks the rows on a timer, opening each one and letting the
sense amplifiers push it back to full voltage, and it must get all the way round
inside the retention window.

It is worth seeing that this is not an extra mechanism bolted on. Opening a row *is* a
refresh of that row, because the sense amplifiers restore what they read — the next
reading explains why they have to. Refresh is simply the guarantee that every row gets
opened often enough, whether or not the processor happened to ask.

The cost of that guarantee is small and is worked out in one of this module's
questions. What it buys is density: one transistor per bit instead of six.

```
  feature size F = 20 nm
  SRAM cell   ~120 F^2 = 120 x 400 nm^2 = 48000 nm^2 = 0.048 um^2
  DRAM cell     ~6 F^2 =   6 x 400 nm^2 =  2400 nm^2 = 0.0024 um^2
  ratio                                              = 20 to 1
```

A gigabit of DRAM cells is $2^{30} \times 2400\ \text{nm}^2 = 2.58\ \text{mm}^2$. The
same gigabit in SRAM cells is 51.5 mm$^2$, which is most of a large die before a
single wire has been drawn. That is why main memory is DRAM on its own chip and cache
is SRAM on the processor, and the whole memory hierarchy is downstream of that one
ratio.

## Where this picture stops

**The decoder's exponential is only postponed, not beaten.** Splitting the address in
two turns $2^n$ into $2 \times 2^{n/2}$, which is a huge saving and still exponential.
A 16 Gbit part is not one enormous array with one enormous pair of decoders; it is
thousands of sub-arrays of a few hundred rows each, with their own decoders and sense
amplifiers, gathered by yet another decoder above them. Banks, ranks and channels are
that hierarchy seen from outside.

**Word lines and bit lines are wires, and wires have RC.** Past a few hundred cells,
the delay along a word line stops being a gate delay and starts being a distributed RC
delay that grows with the *square* of the length. That, rather than the decoder, is
what actually caps the size of a sub-array.

**The cell counts above are cells, not chips.** A 6 F$^2$ DRAM cell needs a capacitor
of around 25 fF standing in that footprint, which is only possible because the
capacitor is built vertically — a deep trench or a stacked cylinder — using process
steps that a logic process does not have. That is why DRAM has never been put on the
same die as a fast processor in any quantity, and why "embedded DRAM" has repeatedly
been announced and repeatedly not taken over.
''',
                },
                {
                    "title": "One wire, several talkers",
                    "minutes": 13,
                    "body": r'''
The last reading stopped at the moment of selection: a word line goes up, and a row of
cells is connected to the wires that will carry their contents out. This reading is
about those wires, because they are where the difficulty in a memory actually lives.

There are two of them, one inside the chip and one outside it, and they have the same
shape of problem. A **bit line** is one wire with hundreds of cells on it, of which
exactly one is allowed to say anything. A **data bus** is one wire with several chips
on it, of which exactly one is allowed to say anything. Both are long, both are
capacitive, and both fail in a specific way when two things talk at once. Get the bit
line and the bus is easy, so start there.

## The bit line, and the smallest signal in the machine

An SRAM cell reading onto a bit line is not very interesting: the cross-coupled pair
is actively driving, it will win eventually, and the only question is how long it
takes to move the line's capacitance.

A DRAM cell is interesting, because it has nothing to drive with. It is a 25 fF
capacitor. The bit line it is being asked to move is 200 fF — eight times as much,
because the line is long and every unselected cell on it contributes.

The trick is to precharge. Before the word line goes up, the bit line is driven to
exactly **half the supply** and then released, so it is floating at 0.6 V on a 1.2 V
part. Then the access transistor turns on and the two capacitances become one node.
No charge goes anywhere else, so the charge that was on the two of them separately is
now shared between them.

### Worked: what a stored 1 is worth

```
  cell capacitance        C_s = 25 fF     charged to V   = 1.2 V
  bit line capacitance    C_b = 200 fF    precharged to V/2 = 0.6 V

  charge on the cell       25e-15 x 1.2 =  30 fC
  charge on the bit line  200e-15 x 0.6 = 120 fC
  total                                  = 150 fC
  shared over             25 + 200       = 225 fF

  final voltage           150e-15 / 225e-15 = 0.6667 V
  movement from precharge 0.6667 - 0.6     = 0.0667 V = 66.7 mV
```

A stored 0 does the mirror image: the cell contributes nothing, the total is 120 fC,
the line lands at $120/225 = 0.5333$ V, and the movement is $-66.7$ mV. So the whole
question "what was in that cell" comes down to whether one wire moved 67 millivolts
up or 67 millivolts down.

The thing that reads that is a **sense amplifier**, and it is module 4's latch again —
two cross-coupled inverters, with the bit line on one of its nodes and a reference at
the precharge level on the other. Given any imbalance at all it drives itself to the
rails, which is what a latch does. Two consequences fall straight out and both matter:

* The amplifier ends up holding the bit line at a **full rail**, and the access
  transistor is still open, so the cell is written back to full voltage as a side
  effect of being read. Refresh is not a separate operation; it is this.
* Before the amplifier acts, the cell has been **destroyed**. It is sitting at 0.667 V,
  not 1.2 V. A read that is abandoned half-way through loses the data, which is why a
  DRAM has a precharge step you have to wait for and why you cannot simply stop
  talking to it in the middle of a row.

Rearrange the arithmetic and the general result is short:

$$S = \frac{V}{2}\cdot\frac{C_s}{C_s + C_b}$$

The signal is set by the *ratio* of the two capacitances, not by either one alone.
Make the bit line longer to get more cells per sense amplifier and $C_b$ goes up and
the signal goes down. That single inequality is why a DRAM array is chopped into
sub-arrays of a few hundred rows with sense amplifiers folded in between them, and it
is what this module's derivation works out properly.

## Outside the chip: one wire, several talkers

Now the same problem one level up. Eight data pins leave the chip and go to the
processor. Seven other chips are on the same eight wires. Exactly one of them may
drive at any moment, and the thing that decides which is — of course — a decoder. Some
of the processor's upper address lines go to a decoder whose outputs are the **chip
select** inputs of the memory parts, one per part, one-hot, exactly as inside the
array. The *memory map* is the truth table of that decoder.

Which leaves the electrical question: what does a chip that is not selected do with
its output pin?

Not "drive a 0". That is the mistake, and it is a natural one, because in every other
context in this course an output has been either high or low. Here it must be
**neither**, and that needs a look at what a CMOS output actually is: a p-channel
device from the pin to the supply and an n-channel device from the pin to ground. HIGH
means the p device is on. LOW means the n device is on. **Tri-state** is a third
arrangement that had no name until buses existed — *both devices off* — and it is
reached by an extra enable input that gates each of them separately. The pin is then
connected to nothing at all, which is what "high impedance" means.

### Worked: what happens when two chips are enabled at once

Give the driver devices realistic on-resistances. Chip A is driving HIGH, so its p
device is on at about 60 ohms. Chip B is driving LOW, so its n device is on at about
40 ohms. The rail is 3.3 V. Between the supply and ground there is now nothing but
those two resistances in series.

```
  total resistance         60 + 40                  = 100 ohms
  current                  3.3 V / 100 ohms         = 33 mA
  voltage on the line      3.3 x 40 / 100           = 1.32 V
  power in chip B          1.32 V x 33 mA           = 43.6 mW
  power in chip A          (3.3 - 1.32) V x 33 mA   = 65.3 mW
  total, on ONE line       3.3 V x 33 mA            = 108.9 mW
  eight lines like it                               = 871 mW
```

Two separate things are wrong there and it is worth keeping them apart. The line has
landed at 1.32 V, which on a 3.3 V part is between $V_{IL} = 0.99$ V and
$V_{IH} = 2.31$ V — the forbidden band of module 1 — so no receiver reads a valid
anything. That is the *logical* failure and it is the lesser one. The 33 mA is the
real problem: a 3.3 V I/O pin is commonly rated at 25 mA absolute maximum, and almost
a watt of it is being turned into heat in two small transistors that were never
designed to carry it. Bus contention is a thermal fault, not a logic fault, and a
board that does it briefly on every cycle can run for months and then fail.

This is why the chip-select decoder is not a convenience. One enable active at a time
is not a rule anybody has to remember; it is a property of a one-hot output, and the
decoder is there to make the fault impossible by construction.

## The wire nobody is driving

There is a state a bus spends most of its time in: everybody tri-stated. The line is
then floating, connected to nothing, holding whatever charge it happened to be left
with and drifting from there.

That is worse than it sounds. A CMOS input sitting near its switching threshold has
both of its own devices partly on, so it draws current from the supply straight to
ground and can oscillate while it does. A floating input is not a 0; it is an
unspecified analogue voltage feeding a very high-gain amplifier.

The fix is a **pull-up**: one resistor from the line to the supply, which defines the
idle level as HIGH. And then the sizing problem, which has two ends.

### Worked: what leakage does to the idle level

Every tri-stated output still leaks. Datasheets guarantee a limit, commonly 10 microamps
per pin over temperature, and eight tri-stated drivers on one line all leak at once.

```
  drivers on the line                 8
  leakage each, worst case           10 uA
  total pulled out of the line       80 uA
  pull-up                            10 kohm
  drop across it       10e3 x 80e-6 = 0.80 V
  idle level           3.3 - 0.80   = 2.50 V
  V_IH                 0.7 x 3.3    = 2.31 V
  margin left                        = 0.19 V
```

It works, and it works by 190 mV, which is not much to have between you and a warranty
claim. Halve the pull-up to 4.7 kohm and the drop falls to 376 mV, so the line idles
at 2.92 V and the margin is a comfortable 610 mV. The price is paid at the other end:
when a driver does hold the line low it must sink $3.3/4700 = 702\ \mu$A through that
pull-up, on every line, for as long as the line is low. That is the trade in one
sentence — **a large pull-up is cheap to pull down and weak against leakage; a small
one is strong against leakage and expensive to pull down.**

## And then there is time

The other cost of a pull-up is that it is the only thing charging the line, and a bus
is a capacitor. Eight packages at 5-8 pF each plus twenty centimetres of track puts
100 pF on a wire without trying.

```
  pull-up                 R = 2.2 kohm
  bus capacitance         C = 100 pF
  time constant           RC = 220 ns

  falling: driven by an n device of 40 ohms
           40 x 100e-12 = 4 ns

  rising:  driven by the pull-up alone, against 80 uA of leakage
           final level   3.3 - 2200 x 80e-6 = 3.124 V
           target        V_IH = 2.31 V
           t = RC ln( 3.124 / (3.124 - 2.31) ) = 220 ns x 1.345 = 296 ns
```

Four nanoseconds down, 296 nanoseconds up: a factor of seventy-four, and the whole
clock has to be sized around the slow edge. If the rise has to complete inside half a
period then the bus cannot be clocked above $1/(2 \times 296\ \text{ns}) = 1.7$ MHz,
which is a startling number to arrive at on a board full of parts specified in
hundreds of megahertz.

Notice also that the leakage did not only cost margin, it cost time. Without it the
line heads for 3.3 V and crosses 2.31 V in 265 ns, having covered 70% of its journey.
With it the line heads for 3.124 V, and the same 2.31 V is now 74% of the way there.
Four percentage points, on an approach that is exponential, cost 31 ns — 12% more rise
time bought with the same 176 mV of idle level the leakage had already taken off the
margin. Two effects of one 80 microamps, and the second is the one nobody predicts.

This is exactly why a fully driven bus is used wherever it can be: with a p device of
60 ohms doing the pulling up, the rising edge is 7 ns rather than 296 ns. The price of
that is the tri-state logic and the absolute prohibition on two drivers at once. An
open-drain bus like I2C accepts the 296 ns because it wants the wired-AND behaviour
and does not want to care how many devices are attached, and its clock rate — 100 kHz
in the original standard — is where that decision lands.

## Where this stops

**Capacitance adds, and it never comes off.** Every device on the bus makes every
transition slower for everybody. That is a hard ceiling: past a few tens of megahertz,
a shared parallel bus with a dozen loads is not a thing that can be made to work at
any price.

So it was abandoned. Modern systems use point-to-point serial links — one driver, one
receiver, a controlled impedance, often differential — and where several devices must
be reached, a switch sits in the middle and talks to each of them separately. PCIe,
SATA and USB are all this, and even DDR memory has moved its command and address
signals this way. The decoder did not disappear when the shared bus did; it moved
inside the switch and became a routing table.

**And the bit line has the same ceiling, for the same reason.** $C_b$ in the formula
above is capacitance per unit length times length, so the two halves of this reading
are one constraint written twice. A memory is a hierarchy of short wires because a long
wire is the one thing in a chip that does not get better when the transistors do.
''',
                },
                {
                    "title": "A truth table you look up",
                    "minutes": 11,
                    "body": r'''
Everything so far in this module has been about storing things you were given. This
reading is about the observation that turns a memory into something else entirely, and
it is one sentence long:

> A memory with $n$ address lines and $m$ data lines is a table with $2^n$ rows and
> $m$ columns. So is a truth table.

Module 2 established that a truth table is the *complete* specification of a
combinational function — nothing about the function exists outside it. Module 3 turned
tables into gates. This reading is about not bothering: put the inputs on the address
lines, and the data lines are the outputs. No minimisation, no K-map, no gate
selection. The design is the contents.

That single idea is what a ROM is, what a lookup table in an FPGA is, and — read
sideways — what "programmable logic" has meant for forty years.

## A ROM is a function you have written down

Take the seven-segment decoder from this course's capstone. Four inputs, the bits of a
counter; seven outputs, one per bar of the display. As gates it is seven separate
Boolean functions, each one pulled out of the font table, each one minimised on its own
K-map, and the result is a few dozen gates that took real work to get right.

As a memory it is this, and there is nothing else to do:

```
  address  Q3Q2Q1Q0    abcdefg      address  Q3Q2Q1Q0    abcdefg
  -------  --------    -------      -------  --------    -------
     0       0000      1111110         8       1000      1111111
     1       0001      0110000         9       1001      1111011
     2       0010      1101101        10       1010      1110111
     3       0011      1111001        11       1011      0011111
     4       0100      0110011        12       1100      1001110
     5       0101      1011011        13       1101      0111101
     6       0110      1011111        14       1110      1001111
     7       0111      1110000        15       1111      1000111

  rows      2^4  = 16
  width     7 bits
  total     16 x 7 = 112 bits
```

One hundred and twelve bits, and the design step was reading a font off a page. Change
the font and you change 112 bits; the circuit is untouched. That is worth stating
plainly, because it is the whole attraction: **a ROM moves the design out of the wiring
and into the contents**, and contents can be changed by somebody who is not a logic
designer, after the board is built.

Which is why ROMs turn up as character generators, as gamma and linearisation tables,
as instruction decoders, as the microcode store module 9's derivation sized, and as the
translation tables in every printer and terminal ever built.

## The catch is in the exponent

The rows double with every input. That is not a mild cost.

```
  inputs   outputs   rows        ROM bits
  ------   -------   ---------   --------------------
     4        7           16     112
    10        4         1024     4096
    16        8        65536     524288          (512 Kbit)
    20       16      1048576     16777216        (16 Mbit)
    65       33     3.69e19      1.22e21
```

The last line is a 32-bit adder: thirty-two bits of one operand, thirty-two of the
other and a carry in, giving 65 inputs; thirty-two sum bits and a carry out, giving 33
outputs. As a lookup table it is $1.22 \times 10^{21}$ bits, which is about $1.5 \times
10^{20}$ bytes, which at 20 terabytes a drive is roughly eight million hard disks. The
same function as gates is module 3's ripple-carry adder: thirty-two full adders, on the
order of 160 gates, and a first-year exercise.

The reason for the gap is worth naming precisely, because it is the rule for deciding
between the two. **A ROM charges the same price for a regular function as for a random
one.** Every row is stored whether or not it could have been predicted from the others.
Gates charge only for the irregularity: a ripple-carry adder is cheap because the same
one-bit circuit does for all thirty-two places, and a K-map is nothing but a search for
that kind of regularity.

So the rule is not "ROMs are for small functions", although that is true. It is:

* **A ROM wins when the function is irregular** — a font, a character map, a state
  table, an instruction decoder, an arbitrary curve. There is no structure for gates to
  exploit, so gates end up storing the table too, in a more expensive form.
* **A ROM loses when the function has structure** — arithmetic above all. And it loses
  by factors that have twenty zeros in them, not by factors of two.

## An FPGA is that idea, made small and repeated

Now shrink the ROM until it is almost nothing, and put a hundred thousand of them on a
chip.

A **lookup table** in a modern FPGA has six inputs. Six inputs means $2^6 = 64$ rows,
one bit each, so a 6-LUT is 64 bits of SRAM and a 64-to-1 multiplexer driven by the six
input signals. It computes *any* function of six variables — all $2^{64}$ of them,
which is a number worth pausing over — and which one it computes is decided entirely by
the 64 bits.

Beside each LUT sits a flip-flop, so a LUT can drive a register directly and the pair
is exactly the "combinational cloud plus state" of module 9. Around them runs a
programmable interconnect: a mesh of wires with switches at the crossings, and each
switch is another configuration bit.

Nothing in the silicon knows what circuit it is. There is no sense in which an FPGA
"contains" your adder. What it contains is a fabric, and a few million SRAM bits that
say which functions the LUTs compute and which wires join which. Loading those bits is
what programming an FPGA means, and because they are SRAM they are lost at power-off —
which is why almost every FPGA board has a small flash chip beside the FPGA whose only
job is to shift the bitstream in at power-up.

### Worked: any function of eight variables, in five LUTs

A LUT has six inputs and the function has eight, so it does not fit. The way out is
**Shannon expansion**, which is the same "split on a variable" move a K-map makes,
applied deliberately.

Pick two of the eight variables — call them $x_7$ and $x_8$ — and hold them fixed. What
is left is a function of the other six, and there are four of those, one for each value
of the pair:

```
  x7 x8 = 00  ->  f00(x1..x6)      one 6-LUT
  x7 x8 = 01  ->  f01(x1..x6)      one 6-LUT
  x7 x8 = 10  ->  f10(x1..x6)      one 6-LUT
  x7 x8 = 11  ->  f11(x1..x6)      one 6-LUT
```

Then choose between the four results according to $x_7$ and $x_8$. That chooser is a
4-to-1 multiplexer, which is a function of four data inputs plus two select inputs —
six inputs, so it is exactly one more LUT.

```
  cofactor LUTs      4
  selector LUT       1
  total              5
```

Five LUTs, 320 configuration bits, for *any* function of eight variables no matter how
irregular. Compare with the ROM: the same function as a single-output ROM is
$2^8 = 256$ bits, so the fabric costs about 25% more storage than the ideal table — and
in exchange, the six inputs of a LUT that only needs four are free, the flip-flops come
attached, and the same silicon does something completely different tomorrow.

Push it one variable further and the shape of the cost becomes clear. Nine variables
gives eight cofactors, and the chooser is now an 8-to-1 multiplexer with eleven inputs,
which does not fit either — so build it from two 4-to-1s and a 2-to-1:

```
  cofactor LUTs                        8
  two 4-to-1 selectors                 2
  one 2-to-1 selector over those       1
  total                               11
```

Doubling with each variable again, exactly as the ROM did, and for exactly the same
reason. Nothing about an FPGA repeals the exponent. What it does is make the unit of
exponential growth 64 bits instead of a whole chip.

### Worked: the seven-segment decoder in a fabric

The decoder above is seven functions of four variables. Each one fits in a single
6-LUT, using four of its six inputs and 16 of its 64 bits.

```
  LUTs                7
  configuration bits  7 x 64 = 448
  bits actually doing anything  7 x 16 = 112
  waste                        75%
```

Three quarters of the storage does nothing, and nobody cares, because the LUTs are
there whether or not they are used. That is the FPGA bargain in miniature: the fabric
is uniform and mostly wasted, and it is still the cheapest way to have a circuit
tomorrow that you have not designed today.

## The mistake

The one worth naming is thinking a LUT *stores a signal* — that configuration and data
are the same kind of thing. They are not. The 64 bits are loaded once at power-up and
then sit still while the design runs; the signals flowing through the multiplexer
change every nanosecond. A LUT is a ROM being read continuously at full speed, not a
register being written.

The second, subtler one is assuming bigger LUTs are always better. Every extra input
doubles the SRAM: a 4-LUT is 16 bits, a 6-LUT is 64, an 8-LUT is 256. Real designs are
full of two- and three-input functions, so most of a large LUT is wasted most of the
time, and the multiplexer through it gets slower. The industry sat on 4-input LUTs for
about twenty years and moved to 6 only when the routing between LUTs — not the LUTs —
became the thing worth economising. It is an empirical optimum, not a principle.

## Where this stops

**An FPGA is not free.** Published measurements of the same designs built both ways put
the FPGA at roughly thirty-five times the silicon area, three to four times the delay,
and something like ten times the dynamic power of a fixed-function chip. You pay that
to be able to change your mind, and for many products it is obviously worth it — but it
is the reason a phone does not contain one.

**Which is why modern parts are not only LUTs.** A multiplier built out of LUTs is a
tower of them, deep and slow, so FPGAs carry hard multipliers, hard block RAMs, hard
memory controllers and often hard processors, and the fabric is left to do the
irregular glue it is actually good at. The rule from the ROM section, applied to the
chip's own floor plan.

**And notice what a block RAM is.** It is a decoder and a grid — the first reading of
this module, unchanged. A LUT is the same thing with $n = 6$ and the contents thought
of as logic. A ROM is the same thing with the contents fixed at manufacture. The
summary at the top of this module claimed that once you see the array, ROMs, FPGAs and
lookup tables stop being three subjects. They are one object, addressed three ways.
''',
                },
            ],
            "quiz": {
                "title": "Arrays, buses and tables",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A memory is described as 4 K × 8. How many address lines does it need?",
                        "opts": ["8", "10", "12", "4096"],
                        "a": 2,
                        "why": (
                            "4 K here means 4096 words, and $4096 = 2^{12}$, so twelve address lines select "
                            "one of them. The 8 is the width of each word and sets the number of *data* "
                            "lines, not address lines. 4096 wires would be the decoder's outputs, deep inside "
                            "the part where nobody has to route them. The whole thing holds "
                            "$4096 \\times 8 = 32768$ bits."
                        ),
                    },
                    {
                        "q": "What must a DRAM controller do that an SRAM controller need not?",
                        "opts": [
                            "Read every row and immediately write it back, continuously, before the charge on the cells drains away",
                            "Hold the address lines stable at all times",
                            "Supply a second, higher voltage for writes",
                            "Nothing — the two are interchangeable",
                        ],
                        "a": 0,
                        "why": (
                            "A DRAM cell is a capacitor, and a capacitor leaks. Refresh is a read followed by "
                            "an immediate write-back, issued row by row by the controller on a timer, and it "
                            "happens whether or not the processor is asking for anything. An SRAM cell is a "
                            "pair of cross-coupled inverters actively holding each other up, so it needs "
                            "nothing but its supply — which is exactly what the extra four transistors per "
                            "cell were bought with."
                        ),
                    },
                    {
                        "q": "Two memory chips on the same data bus are enabled at the same moment, one driving a line high and the other driving it low. What happens?",
                        "opts": [
                            "The line settles halfway, at about 2.5 V, which both chips read as a valid 1",
                            "A low-resistance path is made from the supply to ground through both chips' output transistors, and something gets hot",
                            "The high wins, because a driven high is stronger than a driven low",
                            "The line goes to high impedance until one of them gives up",
                        ],
                        "a": 1,
                        "why": (
                            "One chip's pull-up network and the other's pull-down network are both fully on, "
                            "with nothing but their own on-resistances between the supply and ground. The "
                            "voltage does land somewhere in the middle, which is in the forbidden band and a "
                            "valid 1 for nobody, but the current is the real problem. The decoder driving "
                            "the chip-select lines exists precisely to make this impossible: one enable "
                            "active at a time, by construction."
                        ),
                    },
                    {
                        "q": "A function of 10 inputs and 4 outputs is to be implemented as a ROM. How many bits does the ROM hold?",
                        "opts": ["40", "1024", "4096", "10240"],
                        "a": 2,
                        "why": (
                            "$2^{10} = 1024$ addresses, each holding a 4-bit word: 4096 bits. 1024 counts the "
                            "rows and forgets that each one is four bits wide. The number worth remembering "
                            "is how it grows — an eleventh input makes it 8192, and a twentieth makes it four "
                            "million — which is why nobody builds arithmetic this way and everybody builds "
                            "small, wide decoders this way."
                        ),
                    },
                    {
                        "q": "A 6-input lookup table in an FPGA holds how many bits, and what decides which function it computes?",
                        "opts": [
                            "6 bits, one per input",
                            "12 bits, two per input",
                            "64 bits, and they are the gate types the table is to use",
                            "64 bits, and they are the output column of the function's truth table",
                        ],
                        "a": 3,
                        "why": (
                            "Six inputs give $2^6 = 64$ rows, so 64 bits of storage, and those bits are "
                            "simply the answer for each row. There are no gates to configure — loading the "
                            "table *is* the design, which is the same observation as module 2's, that a "
                            "truth table is the complete specification of a function, taken literally in "
                            "silicon."
                        ),
                    },
                ],
            },
            "blanks": [
                {
                    "title": "The number printed on the part",
                    "minutes": 8,
                    "brief": r'''
Two numbers describe a memory: how many words it holds and how wide each word is.
Everything else on the pin-out follows from them, and the arithmetic is worth being
able to do without stopping to think, because it is the arithmetic that decides
whether a part fits the socket.

The rules are short. The **word count** fixes the number of address lines: $n$ lines
reach $2^n$ words, so the address count is $\log_2$ of the depth. The **width** fixes
the number of data lines and does not touch the address at all. The **total** is the
two multiplied.

The first row is filled in as a worked example.
''',
                    "caption": "four parts, read off their descriptions",
                    "lang": "text",
                    "listing": r'''
  part          words       width   address lines   data lines   bits held
  -----------   ---------   -----   -------------   ----------   ---------
  2 K x 8            2048       8        11              8           16384
  4 K x 16           4096      16       ___             16           65536
  64 K x 8          65536       8        16             ___         ___
  1 M x 4         1048576       4       ___              4         4194304

  In every one of these the K means ___ rather than a thousand, because a
  reachable count is a power of two: an address line either exists or does not.
''',
                    "blanks": [
                        {
                            "prompt": "4 K x 16 holds 4096 words. How many address lines reach them?",
                            "opts": ["4", "12", "16", "4096"],
                            "a": 1,
                            "why": (
                                "$4096 = 2^{12}$, so twelve. The 16 in the part's name is the width and has "
                                "nothing to do with the address — the same 4096 words would need twelve "
                                "address lines if they were one bit wide or sixty-four. 4096 is the number "
                                "of *decoder outputs* inside the part, which is exactly what the twelve "
                                "lines are there to avoid having to route."
                            ),
                        },
                        {
                            "prompt": "64 K x 8: how many data lines?",
                            "opts": ["8", "16", "64", "65536"],
                            "a": 0,
                            "why": (
                                "The width is the second number, so eight data lines, one per bit of a word. "
                                "Read the description as \"65536 things, each of them 8 bits\" and the two "
                                "roles never get confused: the first number is how many, the second is how "
                                "big each one is."
                            ),
                        },
                        {
                            "prompt": "And how many bits does 64 K x 8 hold in total?",
                            "opts": ["8192", "65536", "524288", "4194304"],
                            "a": 2,
                            "why": (
                                "$65536 \\times 8 = 524288$ bits, or 512 Kbit — which is how such a part is "
                                "usually advertised, and a good reason to be able to move between the two "
                                "descriptions. 65536 is the word count and forgets that each word is eight "
                                "bits wide, which is the single most common slip in this arithmetic."
                            ),
                        },
                        {
                            "prompt": "1 M x 4 holds 1048576 words. How many address lines?",
                            "opts": ["4", "10", "20", "1048576"],
                            "a": 2,
                            "why": (
                                "$1048576 = 2^{20}$, so twenty. Ten is the answer for a *DRAM's pin count* "
                                "rather than its address width, because a DRAM sends the top half of the "
                                "address and then the bottom half down the same ten pins — but the address "
                                "itself is still twenty bits, and the part still reaches a million words."
                            ),
                        },
                        {
                            "prompt": "In these part numbers, K means what?",
                            "opts": ["1000", "1024", "2048", "8"],
                            "a": 1,
                            "why": (
                                "1024, which is $2^{10}$. The prefix was bent to fit the hardware rather than "
                                "the other way round: a part with ten address lines reaches 1024 words and "
                                "there is no way to build one that reaches 1000, so the round numbers in "
                                "this subject are powers of two. Note that the same is not true of a hard "
                                "disk or a network link, where a kilobyte really is 1000 bytes — the "
                                "ambiguity is old, deliberate on both sides, and still with us."
                            ),
                        },
                    ],
                },
                {
                    "title": "Filling in a lookup table",
                    "minutes": 9,
                    "brief": r'''
The carry-out of a full adder — module 3's, unchanged — is a function of three bits:
the two operand bits and the carry in. It is 1 whenever at least two of the three are
1, which is why it is sometimes called the majority function.

Here it is being put into a lookup table rather than built out of gates. The address
is the three inputs read as a binary number, and the single data bit at that address
is the answer. Nothing else happens: there is no logic to design, only a column to
write down.

Fill in the two missing rows, then read the whole column out as one word.
''',
                    "caption": "a full adder's carry-out, as the contents of a LUT",
                    "lang": "text",
                    "listing": r'''
  address   a  b  cin      carry out
  -------   ---------      ---------
     0      0  0   0           0
     1      0  0   1           0
     2      0  1   0          ___
     3      0  1   1           1
     4      1  0   0           0
     5      1  0   1          ___
     6      1  1   0           1
     7      1  1   1           1

  Written as one word, address 7 first down to address 0:   ___

  A 6-input lookup table holds ___ bits in all, of which this
  three-input function occupies ___ .

  To make the same LUT compute something else you change ___ .
''',
                    "blanks": [
                        {
                            "prompt": "Address 2 is a = 0, b = 1, cin = 0. What is the carry out?",
                            "opts": ["0", "1"],
                            "a": 0,
                            "why": (
                                "Only one of the three inputs is 1, and one bit cannot generate a carry — "
                                "$0 + 1 + 0 = 1$, which fits in the sum bit with nothing left over. The "
                                "carry needs at least two 1s among the three."
                            ),
                        },
                        {
                            "prompt": "Address 5 is a = 1, b = 0, cin = 1. What is the carry out?",
                            "opts": ["0", "1"],
                            "a": 1,
                            "why": (
                                "Two of the three are 1, so $1 + 0 + 1 = 2$, which is `10` in binary: sum 0, "
                                "carry 1. Note that it does not matter *which* two — the function is "
                                "symmetric in its three inputs, which is exactly the regularity that makes "
                                "the gate version cheap and that a lookup table pays no attention to."
                            ),
                        },
                        {
                            "prompt": "Reading the output column from address 7 down to address 0, what is the 8-bit word?",
                            "opts": ["11101000", "00010111", "10010110", "11100010"],
                            "a": 0,
                            "why": (
                                "Addresses 7, 6, 5 and 3 give 1 and the rest give 0, so reading downwards "
                                "from 7 the word is `11101000` — $E8$ in hexadecimal, and a number you will "
                                "meet again the first time you look at an FPGA's configuration file. "
                                "`00010111` is the same column read upwards from address 0, which is a real "
                                "hazard: a table is only meaningful together with a statement of which end "
                                "is which."
                            ),
                        },
                        {
                            "prompt": "How many bits does a 6-input lookup table hold?",
                            "opts": ["6", "12", "36", "64"],
                            "a": 3,
                            "why": (
                                "Six inputs give $2^6 = 64$ combinations, and the table needs an answer for "
                                "each of them: 64 bits. That is the whole of a 6-LUT — 64 SRAM cells and a "
                                "64-to-1 multiplexer driven by the six inputs — and it can compute any of "
                                "the $2^{64}$ functions of six variables, because every one of them is just "
                                "a different way of filling those 64 cells."
                            ),
                        },
                        {
                            "prompt": "How much of that does a three-input function occupy?",
                            "opts": ["3 bits", "8 bits", "32 bits", "all 64 bits"],
                            "a": 1,
                            "why": (
                                "Eight, one per row of the table above. The remaining 56 do nothing — or "
                                "rather, the unused inputs are tied off and the same 8-bit pattern is "
                                "repeated through the table, which comes to the same thing. Wasteful and "
                                "irrelevant: the LUT is on the die whether you fill it or not, so an unused "
                                "input costs nothing at all."
                            ),
                        },
                        {
                            "prompt": "What has to change for the LUT to compute a different function?",
                            "opts": [
                                "the 64 stored bits, and nothing else",
                                "which gates inside it are wired to which",
                                "the number of inputs it has",
                                "the multiplexer's select order",
                            ],
                            "a": 0,
                            "why": (
                                "Only the contents. There are no gates inside a LUT to rewire — there is a "
                                "memory and a multiplexer, both fixed at manufacture — so the entire "
                                "difference between an AND, an XOR and something with no name is which 64 "
                                "bits were loaded at power-up. This is the whole of what \"programmable "
                                "logic\" means, and it is the same observation as module 2's: a truth table "
                                "is the complete specification of a function, so storing the table is "
                                "storing the design."
                            ),
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Ten pins for a million words",
                    "minutes": 5,
                    "brief": r'''
An address of $n$ bits reaches $2^n$ words, so the number of address bits is fixed the
moment the depth is. The number of address *pins* is a separate question, and on a
DRAM it is smaller.

The array inside is square: the top half of the address picks a row and the bottom
half picks a column. A DRAM takes advantage of that by sending the two halves down the
same pins one after the other, latched by two separate strobes — which is what the RAS
and CAS signals on every DRAM datasheet are for.
''',
                    "prompt": "How many address pins does the part need?",
                    "note": "Give the answer as a whole number of pins.",
                    "figure": r'''
A DRAM organised as 1 M × 16: 1048576 words of 16 bits. The array is square, so the
address splits into equal row and column halves. The controller puts the row half on
the address pins and pulses RAS, then puts the column half on the same pins and pulses
CAS.
''',
                    "given": [
                        {"label": "Words in the part", "value": "1 M = 1048576"},
                        {"label": "Width of each word", "value": "16 bits"},
                        {"label": "Address halves", "value": "equal — the array is square"},
                        {"label": "Address pins carry", "value": "the row half, then the column half"},
                    ],
                    "aside": "Find the full address width first, then remember that only half of it is on the pins at any one moment.",
                    "answer": 10.0,
                    "tol": 0.5,
                    "unit": "pins",
                    "hint": "$2^n = 1048576$ gives the full address width. The pins carry half of it at a time.",
                    "wrong": "20 is the full address width, which is right as far as it goes — but both halves never appear at once, so the part does not need pins for both. 16 is the data width and takes no part in this arithmetic at all.",
                    "why": (
                        "$2^{20} = 1048576$, so the address is 20 bits wide. A square array splits it into "
                        "10 row bits and 10 column bits, and because the two halves arrive at different "
                        "moments the same ten pins carry both: **10 address pins**.\n\n"
                        "The 16 never enters it. Width sets the number of data pins and nothing else, which "
                        "is the distinction worth fixing early — a 1 M × 4 part in the same package would "
                        "have the same ten address pins and four data pins instead of sixteen.\n\n"
                        "Ten pins saved per chip sounds like housekeeping until you count the parts. A "
                        "memory module carries sixteen of them, a board carries four modules, and the "
                        "address bus is common to all of them: multiplexing takes 20 wires out of the "
                        "connector rather than 10 out of each chip. The price is that a read now takes two "
                        "steps instead of one, which is where DRAM's latency starts — and it is also what "
                        "makes a second access to an already-open row so much cheaper than the first."
                    ),
                },
                {
                    "title": "The bus when nobody is driving it",
                    "minutes": 8,
                    "brief": r'''
Eight memory chips share one data line. At this moment none of them is selected, so
every one of their output drivers is tri-stated and the line is being held up by its
pull-up resistor alone.

That does not mean no current flows. A tri-stated output is off, not absent: its
transistors leak, and the datasheet guarantees only a limit, commonly 10 µA per pin
across the temperature range. Eight of them leak at once, and all of that current has
to come down through the pull-up.

The leakage is drawn as the current sink it behaves like, between the line and ground.
''',
                    "prompt": "What voltage does the idle line sit at?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rpu", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "i0", "kind": "I", "x": 11, "y": 6, "rot": 1, "value": 80e-6},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [14, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "3.30 V"},
                        {"label": "Pull-up", "value": "10 kΩ"},
                        {"label": "Tri-stated drivers on the line", "value": "8"},
                        {"label": "Leakage each, worst case", "value": "10 µA"},
                        {"label": "Receiver reads HIGH above", "value": "$V_{IH} = 0.7 \\times 3.3 = 2.31$ V"},
                    ],
                    "aside": "One resistor with a known current in it. The rail is the starting point and the resistor takes something off it.",
                    "answer": 2.5,
                    "tol": 0.02,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "Eight drivers at 10 µA each is 80 µA, and all of it flows through the 10 kΩ. Work out the drop and take it off the rail.",
                    "wrong": "3.30 V is the answer with the leakage ignored, which is what a schematic without the current source would have suggested. 0.80 V is the drop across the pull-up rather than the level left on the line.",
                    "why": (
                        "The eight drivers pull $8 \\times 10 = 80\\ \\mu$A out of the line, and the only "
                        "path back to the rail is the pull-up, so all 80 µA flows through it. The drop is "
                        "$10\\,\\text{k}\\Omega \\times 80\\ \\mu\\text{A} = 0.80$ V and the line idles at "
                        "$3.30 - 0.80 = \\mathbf{2.50}$ V.\n\n"
                        "Set that against $V_{IH} = 2.31$ V and there are 190 mV of margin. It works, and "
                        "it works with less room than anyone would choose — and note where the number came "
                        "from: not from anything the designer did, but from eight *worst-case datasheet "
                        "limits* added up. Every one of those parts is probably leaking a hundredth of "
                        "that, and the design still has to survive the day one of them does not.\n\n"
                        "The fix is a smaller pull-up. At 4.7 kΩ the drop is 376 mV and the line idles at "
                        "2.92 V, which is a comfortable 610 mV of margin. What it costs is at the other "
                        "end of the problem: when a driver does hold this line low it must sink "
                        "$3.3/4700 = 702\\ \\mu$A through the pull-up, on every line, for as long as the "
                        "line stays low. A large pull-up is cheap to pull down and weak against leakage; a "
                        "small one is the reverse, and there is no third option."
                    ),
                },
                {
                    "title": "What refresh costs",
                    "minutes": 8,
                    "brief": r'''
Every DRAM cell is a capacitor with a leak, so the whole array has to be read and
rewritten continuously just to stand still. That work is not free, and the size of
the bill is worth knowing before deciding it does not matter.
''',
                    "prompt": "What fraction of the time is the array busy refreshing rather than available to the processor?",
                    "note": "Give the answer as a percentage.",
                    "figure": r'''
One DRAM array: 8192 rows of cells, each cell one transistor and one capacitor. A
refresh reads a whole row into the sense amplifiers and immediately writes it back,
restoring the charge on every cell in that row. The controller issues them itself, on
a timer, in the gaps between whatever the processor happens to be asking for.
''',
                    "given": [
                        {"label": "Rows in the array", "value": "8192"},
                        {"label": "Every row refreshed within", "value": "64 ms"},
                        {"label": "Time to refresh one row", "value": "100 ns"},
                        {"label": "Row width", "value": "irrelevant"},
                    ],
                    "answer": 1.28,
                    "tol": 0.05,
                    "unit": "%",
                    "aside": "Nothing in this depends on how wide the rows are. A part with the same 8192 rows and four times the width stores four times as much and refreshes in the same time, which is one reason arrays grow sideways.",
                    "hint": "Work out how much refreshing has to fit inside one 64 ms window, then ask what fraction of 64 ms that is.",
                    "wrong": "0.0128 is the fraction — multiply by 100 for a percentage. If you got 12.8, check a factor of ten somewhere: 8192 × 100 ns is 819.2 µs, which is 0.8192 ms and not 8.192 ms.",
                    "why": (
                        "Every one of the 8192 rows must be refreshed once inside each 64 ms window, and each "
                        "refresh takes 100 ns, so the window contains "
                        "$8192 \\times 100\\ \\text{ns} = 819.2\\ \\mu\\text{s}$ of refreshing. As a fraction of "
                        "64 ms that is $819.2/64000 = 0.0128$, or **1.28%**.\n\n"
                        "Small, and not zero, and the shape of the number explains most of DRAM's character. "
                        "The cost is paid whether or not anything is reading the memory. It needs a controller "
                        "with a timer in it, which SRAM does not. And it gets worse when the part is hot, "
                        "because leakage does — the usual response is to halve the interval to 32 ms, which "
                        "doubles the overhead to 2.56%."
                    ),
                },
                {
                    "title": "How long the released line takes to come back up",
                    "minutes": 12,
                    "brief": r'''
The same bus as before, with two things added: a smaller pull-up, and the capacitance
that was always there. Eight packages at 5 to 8 pF each, plus twenty centimetres of
track, comes to about 100 pF — and 100 pF is drawn here as the single capacitor it
behaves like.

A driver has just let go of the line after holding it low, so the line starts at 0 V
and the pull-up has to charge that capacitance on its own. The receiver does not
notice anything until the line crosses $V_{IH}$, and $V_{IH}$ for a 3.3 V part is 70%
of the rail.

Watch what the leakage does here. It is only 80 µA and it barely dented the DC level
in the last question, but it also moves the voltage the line is heading *towards*, and
the threshold is close to that.
''',
                    "prompt": "How long after the driver lets go does the line cross $V_{IH}$?",
                    "note": "Give the answer in nanoseconds.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 3.3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rpu", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2200},
                            {"id": "i0", "kind": "I", "x": 11, "y": 6, "rot": 1, "value": 80e-6},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "cb", "kind": "C", "x": 14, "y": 6, "rot": 1, "value": 100e-12},
                            {"id": "g2", "kind": "GND", "x": 14, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 17, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [17, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [14, 3], "b": [14, 5]},
                            {"a": [14, 7], "b": [14, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "3.30 V"},
                        {"label": "Pull-up", "value": "2.2 kΩ"},
                        {"label": "Bus capacitance", "value": "100 pF"},
                        {"label": "Total leakage off the line", "value": "80 µA"},
                        {"label": "Line starts at", "value": "0 V, the driver having just let go"},
                        {"label": "Receiver reads HIGH above", "value": "$V_{IH} = 0.7 \\times$ rail"},
                    ],
                    "aside": "An exponential approach needs two things before the time constant is any use: where it starts and where it is going. The leakage changes the second one.",
                    "answer": 296.0,
                    "tol": 4.0,
                    "unit": "ns",
                    "check": r'''
const rail = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0].value;
const vih = 0.7 * rail;
const s = c.step(1.2e-6);
for (let i = 1; i < s.t.length; i++) {
  if (s.v[i] >= vih) {
    const f = (vih - s.v[i - 1]) / (s.v[i] - s.v[i - 1]);
    return (s.t[i - 1] + f * (s.t[i] - s.t[i - 1])) * 1e9;
  }
}
throw new Error('the line never reaches V_IH');
''',
                    "hint": "The line is not heading for 3.3 V — do the previous question's arithmetic again with this pull-up to find where it *is* heading. Then $v(t) = V_\\infty(1 - e^{-t/RC})$, solved for the $t$ at which $v = 2.31$ V.",
                    "wrong": "265 ns is the answer with the leakage left out — the line then heads for 3.3 V and $V_{IH}$ is 70% of the way, giving $RC \\ln(1/0.3)$. 220 ns is one time constant, which is where the line reaches 63% of its final value and not where it crosses the threshold.",
                    "why": (
                        "Three steps. **Where it is going:** the leakage takes "
                        "$2.2\\,\\text{k}\\Omega \\times 80\\ \\mu\\text{A} = 0.176$ V off the rail, so the "
                        "line is heading for 3.124 V, not 3.3 V. **How fast:** "
                        "$RC = 2.2\\,\\text{k}\\Omega \\times 100\\ \\text{pF} = 220$ ns, and the leakage "
                        "does not change that — a constant current shifts where the exponential ends up "
                        "without touching how quickly it gets there. **When it crosses:** with "
                        "$V_{IH} = 2.31$ V,\n\n"
                        "$$t = RC\\,\\ln\\!\\left(\\frac{3.124}{3.124 - 2.31}\\right) = 220\\ \\text{ns} "
                        "\\times 1.345 = \\mathbf{296\\ ns}$$\n\n"
                        "Now compare the two ends of the same edge. Falling, the line was driven by an n "
                        "device of about 40 Ω, so it took $40 \\times 100\\,\\text{pF} = 4$ ns. Rising, it "
                        "takes 296 ns. A factor of seventy-four between the two edges of one signal, and "
                        "the clock has to be sized around the slow one: if the rise must finish inside "
                        "half a period, this bus cannot run above 1.7 MHz.\n\n"
                        "The leakage's second effect is the one worth taking away. Without it the line "
                        "would head for 3.3 V and cross 2.31 V in 265 ns, 70% of the way to its target. "
                        "With it the target moves down to 3.124 V and the same 2.31 V is 74% of the way — "
                        "four percentage points, on an approach that is exponential, worth 31 ns. That is "
                        "why 80 µA of leakage is worth taking seriously twice: once for the margin it eats "
                        "and once for the time.\n\n"
                        "It is also the argument for driving a bus rather than pulling it up. Put a 60 Ω p "
                        "device on this line instead of the 2.2 kΩ and the rising edge is about 7 ns. What "
                        "you buy the 296 ns with is the wired-AND behaviour and not having to care how many "
                        "devices are attached, which is exactly the bargain I²C makes — and why its "
                        "original clock rate was 100 kHz."
                    ),
                },
                {
                    "title": "Two chips enabled at once",
                    "minutes": 14,
                    "brief": r'''
The failure the chip-select decoder exists to prevent, drawn out and measured.

An address decode has gone wrong and two parts are enabled on the same data line at
the same moment. Chip A is driving it HIGH, so its p-channel device is on, and a real
one has an on-resistance of around 60 Ω. Chip B is driving the same line LOW, so its
n-channel device is on at around 40 Ω. Between the supply and ground there is now
nothing but those two.

The line's own 2.2 kΩ pull-up is still there, and the six other parts on the line are
tri-stated and leaking their usual 10 µA each. Both of those are small next to what is
about to happen, and both are in the drawing because "small" is a conclusion rather
than an assumption.

The question is not what the line does — no receiver is going to read anything useful
off it either way. The question is what is happening inside chip B, whose pull-down
transistor is carrying the whole of this.
''',
                    "prompt": "How much power is being dissipated in chip B's pull-down device?",
                    "note": "Give the answer in milliwatts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v0", "kind": "V", "x": 3, "y": 10, "rot": 1, "value": 3.3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 14},
                            {"id": "rp", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 60},
                            {"id": "rpu", "kind": "R", "x": 6, "y": 6, "rot": 0, "value": 2200},
                            {"id": "i0", "kind": "I", "x": 13, "y": 6, "rot": 1, "value": 60e-6},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 10},
                            {"id": "rn", "kind": "R", "x": 16, "y": 6, "rot": 1, "value": 40},
                            {"id": "g1", "kind": "GND", "x": 16, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 19, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 11], "b": [3, 14]},
                            {"a": [3, 9], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [3, 6], "b": [5, 6]},
                            {"a": [7, 6], "b": [11, 6]},
                            {"a": [11, 6], "b": [11, 3]},
                            {"a": [7, 3], "b": [19, 3]},
                            {"a": [13, 3], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 10]},
                            {"a": [16, 3], "b": [16, 5]},
                            {"a": [16, 7], "b": [16, 10]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "3.30 V"},
                        {"label": "Chip A, driving HIGH", "value": "p device on at 60 Ω"},
                        {"label": "Chip B, driving LOW", "value": "n device on at 40 Ω"},
                        {"label": "Line pull-up", "value": "2.2 kΩ"},
                        {"label": "Six tri-stated parts, leaking", "value": "60 µA in total"},
                        {"label": "Absolute maximum per I/O pin", "value": "25 mA"},
                    ],
                    "aside": "Find the line's voltage first — three branches meet there, two of them heading for the rail. Then chip B's device is one resistor with a known voltage across it, and power follows.",
                    "answer": 44.9,
                    "tol": 0.5,
                    "unit": "mW",
                    "check": r'''
const n = c.outNode();
const d = c.dc();
const rn = c.net.parts.filter(function (p) {
  return p.kind === 'R' && ((p.n1 === n && p.n2 === 0) || (p.n2 === n && p.n1 === 0));
})[0];
const v = Math.abs(d.v[rn.n1] - d.v[rn.n2]);
return v * v / rn.value * 1000;
''',
                    "hint": "In siemens: 60 Ω is 16.67 mS towards the rail and 2.2 kΩ is 0.4545 mS towards the rail, against 25 mS towards ground, with 60 µA leaving the node. Once the line's voltage is known, $P = V^2/R$ across the 40 Ω.",
                    "wrong": "43.6 mW is the answer with the pull-up and the leakage dropped at the start — worth comparing with the real one, because it is only 3% out and that is the justification for dropping them. In that same simplification 108.9 mW is the power in *both* devices, and 65.3 mW is chip A's share; the question asks about chip B alone, which is the smaller of the two because it has the smaller on-resistance and so the smaller voltage across it.",
                    "why": (
                        "**The line first.** Three paths meet on it: 60 Ω to the rail, 2.2 kΩ to the rail, "
                        "40 Ω to ground, with 60 µA of leakage leaving. In conductances that is "
                        "$16.667 + 0.455 = 17.121$ mS towards 3.3 V and 25 mS towards 0 V, so\n\n"
                        "$$V = \\frac{3.3 \\times 17.121\\ \\text{mS} - 0.060\\ \\text{mA}}"
                        "{17.121 + 25\\ \\text{mS}} = \\frac{56.44}{42.12} = 1.340\\ \\text{V}$$\n\n"
                        "**Then chip B.** Its 40 Ω has 1.340 V across it, so it is carrying "
                        "$1.340/40 = 33.5$ mA and dissipating $1.340 \\times 33.5\\,\\text{mA} = "
                        "\\mathbf{44.9\\ mW}$.\n\n"
                        "Three things about that number. The 33.5 mA is past the 25 mA the pin is rated "
                        "for, and it is not a transient — it lasts as long as both parts are enabled. "
                        "Chip A is dissipating more still: it carries $(3.30 - 1.34)/60 = 32.7$ mA, and "
                        "$1.96\\,\\text{V} \\times 32.7\\,\\text{mA} = 64.0$ mW, the larger share because "
                        "the larger on-resistance takes the larger voltage. The rail is supplying 111 mW "
                        "in total, and eight data lines doing this at once is 0.89 W in two packages that "
                        "were expecting milliwatts.\n\n"
                        "And notice what the line itself is doing: sitting at 1.34 V, which is above "
                        "$V_{IL} = 0.99$ V and below $V_{IH} = 2.31$ V — squarely in module 1's forbidden "
                        "band, valid for nobody. That is the failure everyone expects, and it is the "
                        "harmless one. The damage is thermal, it is cumulative, and a board that does this "
                        "briefly on every cycle will run for months before it stops.\n\n"
                        "Worth checking the two parts that were almost ignored. Drop the pull-up and the "
                        "leakage entirely and the line sits at $3.3 \\times 40/100 = 1.32$ V with 33 mA in "
                        "it, giving 43.6 mW — 3% under. So the instinct was right, and the way to be "
                        "entitled to it is to work it out once with them in.\n\n"
                        "This is what the chip-select decoder is buying. One-hot outputs make two "
                        "simultaneous enables not unlikely but *impossible*, which is the only standard "
                        "worth holding a bus to."
                    ),
                },
            ],
            "tune": {
                "title": "Getting a 5 V data line into a 3.3 V input",
                "minutes": 10,
                "brief": r'''
An older memory part runs from 5 V and drives its data lines to the full rail. The
controller reading it runs from 3.3 V, and its inputs must not be taken above their
own supply — do that and current flows into the pin's protection diode, which is a
slow way of destroying it. But the line still has to read as a **1**, and this part's
$V_{IH}$ is 70% of 3.3 V, or 2.31 V.

So the divider has to land in a window: comfortably above 2.31 V, and at or below
3.3 V. That is one requirement. The other is current, and it matters here because
there are eight data lines and each one burns this current the whole time it is high.

Two knobs, and the ratio and the current are set by different things: the ratio by
where the two resistors sit relative to each other, the current by how large they are
together.
''',
                "prompt": "Land the divided line between 2.40 V and 3.30 V, and draw no more than 0.20 mA per line.",
                "note": "Both constraints at once. A divider is the cheapest level shifter there is and also the slowest — its resistance and the input's capacitance make exactly the low-pass filter module 4's build measured, so this trick is for slow lines only.",
                "model": "divider",
                "initial": {"r1": 1000, "r2": 4700},
                "constants": {"vin": 5},
                "plotKey": "vout",
                "constraints": [
                    {"k": "vout", "label": "2.40 V ≤ Vout ≤ 3.30 V", "min": 2.4, "max": 3.3},
                    {"k": "i", "label": "I ≤ 0.20 mA per line", "max": 0.2},
                ],
            },
            "derive": {
                "title": "How much signal a DRAM cell has to work with",
                "minutes": 14,
                "brief": r'''
A DRAM cell has no way of driving anything. It is a capacitor of about 25 fF, and the
bit line it has to make an impression on is several times that. The read works by
charge sharing: the bit line is precharged to half the supply and released, the access
transistor turns on, and whatever charge was on the two capacitances redistributes
itself over both.

The sense amplifier then has to decide which way the line moved. So the question that
decides how a DRAM array is laid out is: **how far does it move?**

Write $C_s$ for the cell capacitance, $C_b$ for the bit line's, and $V$ for the supply.
The cell is holding a 1, so it starts at the full $V$; the bit line starts at $V/2$.
''',
                "vars": ["C_s", "C_b", "V", "Q", "V_f", "S", "r"],
                "steps": [
                    {
                        "prompt": "Write the charge stored on the cell capacitor before the access transistor turns on.",
                        "given": "The cell is a capacitance $C_s$ charged to the full supply $V$.",
                        "answer": "C_s V",
                        "placeholder": "a capacitance times a voltage",
                        "hint": "$Q = CV$, with the cell's own capacitance and the voltage it is sitting at.",
                        "deconstruct": [
                            "The defining relation for a capacitor is $Q = CV$.",
                            "The capacitance here is $C_s$.",
                            "The voltage is the full supply, because the cell is holding a 1.",
                        ],
                    },
                    {
                        "prompt": "Write the charge on the bit line just before the same moment.",
                        "given": "The bit line is a capacitance $C_b$, precharged to half the supply and then left floating.",
                        "answer": "C_b V/2",
                        "placeholder": "the same relation, with the other capacitance",
                        "hint": "Same $Q = CV$, with $C_b$ and a voltage of $V/2$.",
                        "deconstruct": [
                            "The bit line's capacitance is $C_b$.",
                            "Precharging put it at $V/2$ and nothing has changed it since.",
                            "So its charge is that capacitance times that voltage.",
                        ],
                    },
                    {
                        "prompt": "The transistor turns on and the two capacitances become one node. Nothing conducts anywhere else, so the total charge is unchanged and both end at a common voltage. Write that voltage $V_f$.",
                        "given": "Total charge before equals total charge after; the two capacitances are now in parallel.",
                        "answer": "(C_s V + C_b V/2)/(C_s + C_b)",
                        "placeholder": "the total charge over the total capacitance",
                        "hint": "Add the two charges from the previous steps, then divide by the capacitance they are now spread over, which is $C_s + C_b$.",
                        "deconstruct": [
                            "The charge is conserved, so the total afterwards is the sum of the two before.",
                            "The two capacitors are now across the same node pair, so they add: $C_s + C_b$.",
                            "A single capacitance holding a known charge sits at $V = Q/C$.",
                        ],
                    },
                    {
                        "prompt": "The sense amplifier does not measure $V_f$. It measures how far the bit line has moved from where the precharge left it. Write that signal $S = V_f - V/2$, simplified.",
                        "given": "Subtract the precharge level from the answer to the previous step and cancel what cancels.",
                        "answer": "C_s V/(2(C_s + C_b))",
                        "placeholder": "a fraction with the two capacitances in it",
                        "hint": "Put $V/2$ over the same denominator $C_s + C_b$ and subtract. The $C_b$ terms in the numerator cancel exactly.",
                        "deconstruct": [
                            "Write $V/2$ as $\\tfrac{V}{2}(C_s + C_b)/(C_s + C_b)$ so both terms share a denominator.",
                            "The numerator becomes $C_s V + C_b V/2 - C_s V/2 - C_b V/2$.",
                            "The two $C_b V/2$ terms cancel and what is left is $C_s V/2$.",
                        ],
                    },
                    {
                        "prompt": "The absolute capacitances are a fabrication detail; what a designer controls is their ratio. Write $S$ again in terms of $V$ and $r = C_b/C_s$ only.",
                        "given": "Divide the top and the bottom of the previous answer by $C_s$.",
                        "answer": "V/(2(1 + r))",
                        "placeholder": "the supply over something in $r$",
                        "hint": "Dividing numerator and denominator by $C_s$ turns $C_s/(C_s + C_b)$ into $1/(1 + r)$.",
                        "deconstruct": [
                            "Divide the numerator $C_s V$ by $C_s$ to get $V$.",
                            "Divide the denominator $2(C_s + C_b)$ by $C_s$ to get $2(1 + r)$.",
                            "Nothing else in the expression contains a capacitance.",
                        ],
                    },
                ],
                "closing": r'''
$$S = \frac{V}{2}\cdot\frac{C_s}{C_s + C_b} = \frac{V}{2(1 + r)},
\qquad r = \frac{C_b}{C_s}$$

Put numbers through it. A 1.2 V part with a 25 fF cell:

```
  r = 4    (C_b = 100 fF)    S = 1.2 / (2 x 5)  = 120 mV
  r = 8    (C_b = 200 fF)    S = 1.2 / (2 x 9)  = 66.7 mV
  r = 16   (C_b = 400 fF)    S = 1.2 / (2 x 17) = 35.3 mV
```

A sense amplifier can resolve something like 50 mV once its own offset and the noise
coupled in from the neighbouring bit lines are accounted for. So the middle row works,
the top row works comfortably, and the bottom row does not work at all — and $r$ is
essentially the length of the bit line, because $C_b$ is capacitance per cell times the
number of cells hanging on it.

That is the constraint that decides the floor plan of every DRAM ever made. You cannot
put four thousand cells on one bit line, however much you would like to amortise the
sense amplifier over more of them, because the signal falls as $1/(1+r)$ and runs out.
Arrays are therefore chopped into sub-arrays of a few hundred rows with a bank of sense
amplifiers folded in between them, and the ROM-like picture of "a decoder and one big
grid" is, at the scale of a real part, a hierarchy of small grids.

Three things this leaves out, and each of them is a real limit.

**Charge sharing is destructive.** After the read the cell is at $V_f$, which for
$r = 8$ is 0.667 V rather than 1.2 V. The bit is not gone but it is badly weakened, and
what saves it is that the sense amplifier is a latch: once it has decided, it drives
the bit line all the way to a rail, and the access transistor is still open, so the
cell is written back to full voltage. Every read restores the row it touched. That is
why refresh is not an extra mechanism but a read whose result is thrown away, and it is
also why a DRAM cannot be interrupted half way through one.

**The amplifier's own offset is in the budget.** Two nominally identical inverters are
not identical — threshold voltages vary from transistor to transistor — so the
amplifier has a built-in preference of its own, commonly 10 to 20 mV. That is a
straight subtraction from $S$, and at $r = 16$ it is half the signal. Modern parts
spend real circuitry on cancelling it.

**None of this applies to SRAM.** An SRAM cell is not a capacitor being shared; it is a
pair of inverters actively driving. Its signal does not shrink as the bit line gets
longer, it just takes longer to develop, because the cell has to move a bigger
capacitance with a fixed current. Same wire, same capacitance, a completely different
constraint — which is worth holding on to, because "long wires are the problem" is true
in both cases for different reasons, and the fixes are not the same.
''',
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
