"""VLSI520 — Memory Hierarchy and Coherence.

Second course of the VLSI track. VLSI510 built a pipeline that assumed memory
answered in one cycle; this one removes that assumption and makes the learner
build the thing that replaces it.

Authoring rules, unchanged from the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

A note on the `cache` sandbox, because the briefs depend on it being read
correctly. Its trace is a strided sweep over a working set defined as *four times
the cache*, repeated three times, under LRU. Two consequences follow, and both
are visible on the plot: the working set grows with the cache, so capacity never
catches up; and a cyclic sweep is the worst case for LRU, so associativity never
helps either. The only reuse in that trace is spatial, inside a 64-byte line, so
for any stride that divides 64 the curve is a horizontal line at exactly
stride/64. Every `notice` below was checked against a Python transcription of
the draw function rather than against what the plot ought to show.
"""

COURSE = {
    "id": "VLSI520",
    "title": "Memory Hierarchy and Coherence",
    "band": 6,
    "level": "Expert",
    "prereqs": ["VLSI510"],
    "stack": ["Python", "Verilog"],
    "credits": 12,
    "hours": 150,
    "icon": "▣",
    "summary": (
        "A processor is only as fast as the memory it is waiting for. This course "
        "builds the cache from the address decomposition upward: placement and "
        "replacement, the three-C decomposition of a measured miss rate, average "
        "memory access time and the write policies that move bytes, and finally MESI "
        "coherence between two caches that both believe they own the same line. Every "
        "model is written by the learner and checked by execution."
    ),
    "outcomes": [
        "Split an address into tag, index and offset for any geometry, and implement a set-associative cache with true LRU replacement.",
        "Decompose a measured miss rate into compulsory, capacity and conflict components by simulation, and say what each one can and cannot be fixed by.",
        "Compute average memory access time for a multi-level hierarchy, and account for the bytes a write-back and a write-through cache each move.",
        "Implement MESI across two snooping caches, and explain the transactions a shared line costs — including the ones false sharing invents.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that runs a two-core coherent hierarchy and reports its miss decomposition and its AMAT.",
    "reading": [
        "*Computer Architecture: A Quantitative Approach*, Hennessy & Patterson — appendix B and chapter 5.",
        "Hill & Smith, *Evaluating Associativity in CPU Caches*, IEEE ToC 1989 — the source of the three-C method used in module 2.",
        "*A Primer on Memory Consistency and Cache Coherence*, Sorin, Hill & Wood — chapters 6 to 8.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Placement, tags and replacement",
            "summary": "An address is three fields. Which field you widen decides where a block may live and what it evicts.",
            "concepts": [
                "Offset, index, tag: the block offset selects a byte, the index selects a set, the tag is everything left over.",
                "Geometry: with capacity `C`, block size `B` and `W` ways, the cache has `C/B` blocks arranged in `C/(BW)` sets.",
                "Direct-mapped is one-way; fully associative is one set. Both are corners of the same design, not separate species.",
                "True LRU is a per-set ordering, not a per-block counter: a hit has to move its block to the recent end of that ordering. A policy that leaves the order alone on a hit is FIFO, and it will evict a block the program is still using.",
                "Widening the set costs `W` tag comparators and a `W`-to-1 multiplexer in the hit path, which is why real L1 caches stop at four or eight ways.",
            ],
            "read": [
                {
                    "title": "Twelve blocks, sixteen frames, no hits",
                    "minutes": 16,
                    "body": r'''
Three arrays, four 64-byte blocks each, at addresses 0, 1024 and 2048. A loop walks
them round-robin — one element from each, then the next element from each — four
times over. Written out, the address stream starts like this:

```text
0  1024  2048   64  1088  2112   128  1152  2176   192  1216  2240   ... (four passes)
```

Forty-eight accesses over twelve distinct blocks. The cache is 1 KB with 64-byte
blocks, so it holds sixteen block frames, and the working set needs twelve of them.
It fits, with four frames to spare. Run it.

```python
class Cache:
    def __init__(self, capacity, block, ways):
        self.block, self.ways = block, ways
        self.sets = capacity // (block * ways)
        self.tags = [[] for _ in range(self.sets)]
        self.hits = self.misses = self.evictions = 0

    def access(self, addr):
        b = addr // self.block
        s, t = self.tags[b % self.sets], b // self.sets
        if t in s:                      # hit: move to the recent end
            s.remove(t)
            s.append(t)
            self.hits += 1
            return True
        s.append(t)                     # miss: install, evict the front
        if len(s) > self.ways:
            s.pop(0)
            self.evictions += 1
        self.misses += 1
        return False


trace = []
for _ in range(4):
    for i in range(4):
        for base in (0, 1024, 2048):
            trace.append(base + i * 64)

print("accesses:", len(trace))
for ways in (1, 2, 4, 8):
    c = Cache(1024, 64, ways)
    for a in trace:
        c.access(a)
    print("%2d-way: %2d sets, %2d hits, %2d misses, miss rate %.2f, evictions %d"
          % (ways, c.sets, c.hits, c.misses, c.misses / len(trace), c.evictions))
```

Direct-mapped: zero hits out of forty-eight, and forty-four evictions. Two ways:
still zero. Four ways: thirty-six hits and a miss rate of 0.25. Nothing about
capacity explains any of that — the data fitted in every one of those four caches.
The whole of the difference is in *which* frame a block is allowed to occupy, and
that is decided by three fields of its address.

## Where the address gets cut, and why there

The block is 64 bytes, so the low 6 bits of an address select a byte inside it and
cannot help choose a frame: every byte of a block lives or dies together. That
leaves the block number, $\lfloor a/B \rfloor$, and sixteen frames to distribute it
over, which needs 4 bits. The question is which 4.

Take them from immediately above the offset and consecutive blocks land in
consecutive sets, so a contiguous array spreads itself across the whole cache. Take
them from the top of the address instead and every block of a 1 KB region shares one
index, so an array would evict itself while fifteen sixteenths of the cache sat
empty. The index is the low block bits because contiguous access is what programs
do. Whatever is left above the index is the tag, and it is the only part that has to
be stored and compared.

```python
BLOCK = 64
for sets in (16, 8):
    print("%d sets:" % sets)
    for addr in (0, 1024, 2048, 1088):
        b = addr // BLOCK
        print("   addr %5d -> block %3d -> set %2d, tag %d"
              % (addr, b, b % sets, b // sets))
```

The three array bases land in set 0 together. That is the whole defect, and it is a
consequence of an arithmetic the addresses make unavoidable: two blocks collide when
their block numbers are congruent modulo the set count $S$, so their addresses
differ by a multiple of $S \cdot B$. With $S = C/(BW)$ from the derivation, that
spacing is

$$S \cdot B = \frac{C}{W}$$

For this cache, 1024 bytes — and the three arrays were placed exactly 1024 bytes
apart. That spacing is not contrived: an allocator handing out power-of-two buffers
produces it constantly, which is why the pathology shows up in real code as an array
dimension that is a power of two.

## The set is the only unit of competition

Follow the twelve live blocks — 0 to 3, 16 to 19, 32 to 35 — into each geometry.
Block 0, block 16 and block 32 are congruent modulo 16, modulo 8 and modulo 4 alike,
so they share a set at every associativity here; likewise blocks 1, 17 and 33, and so
on. Four sets carry three live tags each, and every other set stays empty however the
cache is arranged:

```text
ways  sets  frames per set  live tags per set  sets used
  1    16          1                3             4 of 16
  2     8          2                3             4 of 8
  4     4          4                3             4 of 4
```

So the comparison that decides the outcome is three live tags against $W$ frames, and
the capacity never enters it. At one and two ways the set is over-subscribed, and LRU
turns over-subscription into total failure rather than partial: with three tags
cycling through two frames, the block LRU evicts is always the one wanted next. Not
a reduced hit rate — no hits at all. At four ways the three tags fit, and the twelve
remaining misses are the first touch of each block: $12/48 = 0.25$, which is the
figure the run printed.

The derivation *The geometry of a set-associative cache* takes the same argument in
symbols and ends with $W$ cancelling out: under a mapping that spreads blocks
uniformly, the region that fits is the capacity $C$ and associativity buys nothing.
This trace is the other case. Its mapping piles three blocks onto a quarter of the
sets and leaves the rest untouched, and it is exactly there that the comparators earn
their area.

## What moves when the ways double

Look at block 17 in the run above. At sixteen sets it is index 1, tag 1; at eight
sets it is index 1, tag 2. The bit the index gave up has reappeared at the bottom of
the tag, and the total number of address bits accounted for has not changed. Halving
the sets does not shrink the cache; it makes each set responsible for twice as much
of the address space and gives it twice as many frames to do that with. The lab check
named *widening the set moves bits from index to tag* is that observation, asserted
on this address.

The cost is in the hit path. Every one of the $W$ ways needs its own tag comparator,
their outputs drive a $W$-to-1 multiplexer on the data, and that multiplexer sits
between the data array and the register file on the load-use path — the path a
scheduler has already speculated on. Doubling the ways adds a level to that
multiplexer and a comparator per way to the tag array, which is why L1 caches stop at
four or eight ways while an L3, whose latency nobody is speculating on, goes to
sixteen.

## The mistake: a replacement policy that never runs on a hit

The tempting implementation keeps one list per set in *insertion* order and evicts
the front. Its hit path does nothing at all, which is attractive precisely because
the hit path is the critical path — and the reasoning that supports it sounds solid:
a hit changes nothing about which blocks are resident, so there is nothing to update.
That is FIFO, and here is the difference:

```python
def run(trace, ways, reorder_on_hit):
    """One set, `ways` frames. reorder_on_hit=True is LRU, False is FIFO."""
    resident = []
    out = []
    for b in trace:
        if b in resident:
            if reorder_on_hit:
                resident.remove(b)
                resident.append(b)
            out.append("hit")
        else:
            resident.append(b)
            if len(resident) > ways:
                resident.pop(0)
            out.append("miss")
    return out


blocks = [0, 1, 0, 2, 1]        # addresses 0, 64, 0, 128, 64 in 64-byte blocks
print("LRU :", run(blocks, 2, True))
print("FIFO:", run(blocks, 2, False))
```

A 128-byte two-way cache is a single set of two frames. The re-touch of block 0 is
the whole experiment: under LRU it makes block 1 the least recent, so block 1 is
evicted and the final access to it misses. Under FIFO block 0 was installed first and
leaves first regardless of having been used a moment ago, so block 1 survives and the
final access hits.

Read that result carefully, because it is the reason the bug survives review: on this
trace **FIFO scores better**. A policy that ignores use is not uniformly worse, and no
aggregate miss rate will reliably tell you which one you implemented. What separates
them is the guarantee — LRU never evicts the most recently used block, FIFO evicts it
whenever it happens to be the oldest — and a guarantee is checked by a case, not by an
average. The lab check named *replacement is LRU and not FIFO* is this five-access
trace, and it expects `[False, False, True, False, False]` with one hit and four
misses.

## True LRU stops being buildable at about four ways

The model the lab asks for is exact recency, which means a set keeps an ordering of
its $W$ frames.

```python
import math

for ways in (2, 4, 8, 16):
    orders = math.factorial(ways)
    print("%2d ways: %d orderings, %d bits per set if packed perfectly"
          % (ways, orders, math.ceil(math.log2(orders))))
```

Forty-five bits per set at sixteen ways if the permutation were packed optimally,
and no hardware packs permutations — the usual construction spends an age counter per
way, 64 bits per set, all of them read, compared and rewritten on every hit. So
shipped caches approximate. Tree pseudo-LRU spends $W-1$ bits, fifteen for sixteen
ways, and gets the recency order approximately right; some designs give up and choose
at random. Write true LRU anyway, as the lab does: it is the policy whose behaviour is
defined, and an approximation is only meaningful as a departure from something.

## Where this picture stops holding

LRU is not the best policy, only a defensible one. A cyclic sweep over $W+1$ blocks
in a $W$-way set scores zero hits under LRU, because the victim is invariably the
block wanted next; a policy allowed to look ahead misses once per pass after the
first and hits on everything else — five blocks through four frames, four passes, is
zero hits under LRU against twelve of twenty under Belady's optimal. The sandbox *What capacity and associativity do not buy you* is
built on that worst case on purpose, and it is why the curve there stays pinned at
100 per cent across sizes that look more than large enough.

The sandbox also shows something the tags-against-ways story above does not predict.
Its trace is a fixed 32 KB walk, three passes, and the same simulation reproduces it:

```python
WORKING_SET, LINE = 32 * 1024, 64


def miss_rate(kb, ways, stride=64, passes=3):
    lines = (kb * 1024) // LINE
    sets = max(1, lines // ways)
    tags = [[] for _ in range(sets)]
    hits = total = 0
    for _ in range(passes):
        for addr in range(0, WORKING_SET, stride):
            line = addr // LINE
            s, t = tags[line % sets], line // sets
            total += 1
            if t in s:
                s.remove(t)
                s.append(t)
                hits += 1
            else:
                s.append(t)
                if len(s) > ways:
                    s.pop(0)
    return (total - hits) / total


for kb in (8, 16, 24, 32, 64):
    row = ["%5.1f%%" % (100 * miss_rate(kb, w)) for w in (1, 4, 16)]
    print("%2d KB  direct %s   4-way %s   16-way %s" % (kb, *row))
```

At 24 KB the direct-mapped cache misses 66.7 per cent of the time and the associative
ones miss on every access. More associativity, worse result — and it is not an
artefact. The walk touches 512 lines. A 24 KB direct-mapped cache has 384 sets, so
128 of them are asked to hold two lines and 256 are asked to hold one; the 256
singletons survive and hit on the second and third passes, which is $512/1536 = 33.3$
per cent hits. Group those same 384 frames four to a set and there are 96 sets, each
responsible for five or six lines with four frames — over-subscribed everywhere, and
under a cyclic sweep that means nothing at all survives. Associativity redistributes
frames between sets; it never adds any, and redistribution can take a set that was
coping and break it.

Finally, the modulo arithmetic itself is a model. It assumes a power-of-two set count
and an address the cache is allowed to see. Skewed-associative caches hash a
different function into each way so that two blocks colliding in one way rarely
collide in another. And a virtually-indexed, physically-tagged L1 has to finish
indexing before translation completes, which caps $S \cdot B$ at the page size: with
4 KB pages and 64-byte blocks that is 64 sets, so capacity beyond 4 KB can be bought
only in ways. A 32 KB 8-way L1 is not a preference. It is $64 \times 64 \times 8$,
and the constraint that produced it is in the MMU rather than in the cache.

## What you are about to build

The lab *A set-associative cache with true LRU* asks for `block_of`, `index_of`,
`tag_of`, `access` and `miss_rate` — the five functions every trace above was made
of. Its checks are the numbers already on this page: 44 evictions on the colliding
trace, a miss rate of exactly 1.0 at one and two ways and 0.25 at four, one access in
sixteen missing on a sequential byte walk, and the five-access trace that separates
LRU from FIFO. Keep `self.tags[i]` in least-recently-used-first order and all five
fall out of it.
''',
                },
            ],
            "sandbox": {
                "title": "What capacity and associativity do not buy you",
                "visualiser": "cache",
                "minutes": 9,
                "initial": {"kb": 8, "ways": 1, "stride": 64},
                "brief": r'''
The plot sweeps cache size along the x axis and reports the miss rate of an LRU
cache on a strided walk. The accented curve is the associativity you have selected;
the faint ones are the three fixed references — direct, 4-way and 16-way — less
whichever of them you are currently sitting on.

Read the fine print of the experiment before you read the plot. The trace is a
cyclic sweep over a working set defined as **four times the cache**, so the working
set grows every time you drag the size slider. That is a deliberate worst case, and
it is worth meeting before you meet the friendly cases.
''',
                "notice": [
                    "With the stride at 64 B, drag the cache size from 1 KB up. The curve is a flat line at 100 per cent all the way to 16 KB, and then it falls off a cliff: 66.7 per cent at 24 KB, 33.3 at 32 KB, and dead flat from there to 64 KB. The walk is a fixed 32 KB, and the cliff is the moment it fits. Everything left after the cliff is the first touch of each line.",
                    "Still at 64 B, raise associativity from direct to 16-way. Below 16 KB the accented curve stays at 100 and the faint comparison curves sit exactly underneath it: a cyclic sweep is the worst case for LRU at *every* associativity, because the line LRU chooses to evict is precisely the one wanted next. Watch 24 KB, though — direct-mapped reads 66.7 per cent there and 4-way and 16-way both read 100. More associativity is *worse*, because 384 sets let some of the sweep miss each other and 96 sets do not.",
                    "Drop the stride to 32 B. Below the cliff the whole family falls to exactly 50 per cent; at 16 B it is 25, at 8 B it is 12.5. Every hit there is a spatial hit inside one 64-byte line, so the miss rate is exactly stride divided by block size — and past the cliff each of those numbers divides by three, because a third of the passes still pay for a first touch and the other two are free.",
                ],
            },
            "derive": {
                "title": "The geometry of a set-associative cache",
                "minutes": 13,
                "vars": ["C", "B", "W", "S", "M"],
                "brief": r'''
A cache of capacity $C$ bytes is built from blocks of $B$ bytes, arranged $W$ ways
to a set. Work out how many sets there are, then how much of a program a single set
is asked to hold.
''',
                "steps": [
                    {
                        "prompt": "How many blocks does the cache hold in total? Write it in terms of $C$ and $B$.",
                        "answer": "\\frac{C}{B}",
                        "hint": "The data array is $C$ bytes and every block occupies $B$ of them.",
                        "deconstruct": [
                            "Capacity here means data bytes; the tag store is extra and is not counted in $C$.",
                            "So the block count is simply the capacity divided by the block size.",
                        ],
                    },
                    {
                        "prompt": "Those blocks are grouped $W$ to a set. Write the number of sets $S$ in terms of $C$, $B$ and $W$.",
                        "answer": "\\frac{C}{B \\cdot W}",
                        "hint": "Take the block count you just wrote and divide it among sets of $W$ blocks each.",
                        "deconstruct": [
                            "There are $C/B$ blocks and each set holds $W$ of them.",
                            "So $S = (C/B)/W$.",
                        ],
                    },
                    {
                        "prompt": "A program touches a contiguous region of $M$ bytes. Assuming the index spreads blocks evenly, how many distinct memory blocks from that region map to one particular set?",
                        "given": "The region holds $M/B$ blocks, and they are shared out among the $S$ sets you just derived.",
                        "answer": "\\frac{M \\cdot W}{C}",
                        "hint": "Divide the region's block count by the number of sets, then substitute your expression for $S$.",
                        "deconstruct": [
                            "Blocks in the region: $M/B$. Sets available: $S = C/(BW)$.",
                            "Blocks per set is $(M/B) \\div (C/(BW))$, and the $B$ cancels.",
                        ],
                    },
                    {
                        "prompt": "A set holds $W$ blocks. Set your last expression equal to $W$ and solve for $M$: how large may the region be before a set is over-subscribed?",
                        "answer": "C",
                        "hint": "Write $MW/C = W$ and cancel.",
                        "deconstruct": [
                            "$\\frac{M W}{C} = W$ gives $M = C$ once $W$ cancels from both sides.",
                            "Associativity has vanished from the answer entirely.",
                        ],
                    },
                ],
                "closing": r'''
The $W$ cancelled. Under a uniform mapping, the working set that fits is the
capacity, and associativity buys nothing at all. Associativity earns its comparators
only where the mapping is *not* uniform — where a stride or a set of hot addresses
piles several live blocks onto one index while other sets sit empty. Module 2 gives
that surplus a name: the conflict miss.
''',
            },
            "quiz": {
                "title": "An address is three fields",
                "minutes": 7,
                "questions": [
                    {
                        "q": "How does a cache split an address?",
                        "opts": [
                            "Tag, index, block offset",
                            "Tag, way, offset",
                            "Index, way, offset",
                            "Tag, set, byte",
                        ],
                        "a": 0,
                        "why": r"""
The offset picks a byte inside the block, the index picks the *set*, and the tag is
everything left over — checked against the stored tags of that set to see whether the
block is one of the ones present. Note what is absent: the way is not part of the
address. Which way a block lands in is decided by the replacement policy at fill time,
not by the address, and that is exactly the freedom associativity buys.
""",
                    },
                    {
                        "q": "A 32 KiB cache has 64-byte blocks and is 4-way set associative. How many sets?",
                        "opts": ["128", "512", "64", "256"],
                        "a": 0,
                        "why": r"""
$32768/64 = 512$ blocks, and $512/4 = 128$ sets — so 7 index bits and 6 offset bits, with
the tag taking the rest. 512 is the block count, which is the number you get by
forgetting to divide by the associativity, and it is the single most common slip in this
arithmetic. A quick check: sets $\times$ ways $\times$ block size must equal capacity.
""",
                    },
                    {
                        "q": "Direct-mapped and fully associative are the two corners of the same geometry. Which is which?",
                        "opts": [
                            "Direct-mapped is one way; fully associative is one set",
                            "Direct-mapped is one set; fully associative is one way",
                            "Both have one set",
                            "Neither fits the set-associative model",
                        ],
                        "a": 0,
                        "why": r"""
One way means every block has exactly one place it may live, so the index is as wide as
it can be and there is no choice to make. One set means the index disappears entirely and
any block may live anywhere, which needs a comparator per block. Seeing them as endpoints
of one parameter rather than three separate designs is what makes the miss taxonomy in
the next module work.
""",
                    },
                    {
                        "q": "You keep capacity and block size fixed and halve the associativity. What happens?",
                        "opts": [
                            "More sets, a wider index, and more conflict misses",
                            "Fewer sets and fewer conflict misses",
                            "Nothing — capacity is what matters",
                            "The tag gets wider",
                        ],
                        "a": 0,
                        "why": r"""
Halving the ways doubles the sets, which takes one bit from the tag and gives it to the
index. The cache holds the same number of bytes and has become fussier about *where*
they go, so blocks that map to the same set now evict each other sooner. That is a
conflict miss, and it is the one kind of miss that depends on the shape rather than the
size — which is precisely what the next module measures.
""",
                    },
                    {
                        "q": "What does widening the block buy, and what does it cost?",
                        "opts": [
                            "Better spatial locality, at the cost of more traffic per miss and fewer blocks",
                            "Fewer compulsory misses with no cost",
                            "More associativity",
                            "A narrower tag with no other effect",
                        ],
                        "a": 0,
                        "why": r"""
A wider block prefetches its neighbours for free, which helps whenever the program walks
through memory in order. It also means each miss drags more bytes across the bus, and the
same capacity now holds fewer blocks, so unrelated data gets evicted sooner. The miss
rate falls with block size and then rises again — and the turning point depends on the
program, which is why block size is measured rather than reasoned about.
""",
                    },
                ],
            },
            "lab": {
                "title": "A set-associative cache with true LRU",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Build the cache. `traces.py` is read-only and generates the address walks; the
placement, the tag store and the replacement policy are yours.

Fill in, in `main.py`:

- `block_of(addr)` — the block number containing `addr`.
- `index_of(addr)` — which set that block maps to.
- `tag_of(addr)` — everything above the index.
- `access(addr)` — look the block up, keep `self.hits`, `self.misses` and
  `self.evictions` current, maintain the LRU order, and return `True` on a hit.
- `miss_rate(...)` — build a cache, run the trace through it, return the fraction
  that missed.

`self.tags[i]` is a list of the tags resident in set `i`. Keep it in **LRU order,
least recently used first**, so that a hit moves a tag to the end and an insertion
into a full set removes the one at the front. A cache that never reorders on a hit
is FIFO, not LRU, and one of the checks below tells the two apart.
''',
                "files": [
                    {"name": "traces.py", "ro": True, "content": r'''
"""Deterministic address traces. Read only: the checks assume these exact walks."""


def walk(start, stride, count, passes=1):
    """`passes` sweeps over `count` addresses spaced `stride` bytes apart."""
    out = []
    for _ in range(passes):
        for i in range(count):
            out.append(start + i * stride)
    return out


def interleave(*traces):
    """Round-robin several traces into one, stopping at the shortest."""
    n = min(len(t) for t in traces) if traces else 0
    out = []
    for i in range(n):
        for t in traces:
            out.append(t[i])
    return out
'''},
                    {"name": "main.py", "content": r'''
import numpy as np
from traces import walk, interleave


class Cache:
    """A set-associative cache with true LRU replacement."""

    def __init__(self, capacity_bytes, block_bytes, ways):
        self.block_bytes = block_bytes
        self.ways = ways
        self.sets = capacity_bytes // (block_bytes * ways)
        # one list of resident tags per set, least recently used first
        self.tags = [[] for _ in range(self.sets)]
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def block_of(self, addr):
        """The block number containing `addr`."""
        # TODO: the offset field is the low bits; discard it.
        return 0

    def index_of(self, addr):
        """The set this address maps to."""
        # TODO: the index is the block number modulo the number of sets.
        return 0

    def tag_of(self, addr):
        """Everything above the index field."""
        # TODO
        return 0

    def access(self, addr):
        """Look `addr` up, update the LRU order, and return True on a hit."""
        # TODO: on a hit, move the tag to the most-recently-used end.
        #       on a miss, insert it, and if the set is now over full remove the
        #       least recent tag and count an eviction.
        return False

    def run(self, trace):
        """Feed a whole trace through and return (hits, misses)."""
        for a in trace:
            self.access(a)
        return self.hits, self.misses


def miss_rate(capacity_bytes, block_bytes, ways, trace):
    """The fraction of `trace` that misses in a cache of that geometry."""
    # TODO: build a Cache, run the trace, divide.
    return 0.0


if __name__ == "__main__":
    hot = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
    rates = [miss_rate(1024, 64, w, hot) for w in (1, 2, 4, 8)]
    print("three arrays 1 KB apart, 1 KB cache")
    print("miss rate by associativity:", np.round(rates, 4).tolist())
    print("sequential byte walk:", round(miss_rate(1024, 64, 1, walk(0, 4, 256)), 4))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np
from traces import walk, interleave


class Cache:
    """A set-associative cache with true LRU replacement."""

    def __init__(self, capacity_bytes, block_bytes, ways):
        self.block_bytes = block_bytes
        self.ways = ways
        self.sets = capacity_bytes // (block_bytes * ways)
        self.tags = [[] for _ in range(self.sets)]
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def block_of(self, addr):
        """The block number containing `addr`."""
        return addr // self.block_bytes

    def index_of(self, addr):
        """The set this address maps to."""
        return self.block_of(addr) % self.sets

    def tag_of(self, addr):
        """Everything above the index field."""
        return self.block_of(addr) // self.sets

    def access(self, addr):
        """Look `addr` up, update the LRU order, and return True on a hit."""
        s = self.tags[self.index_of(addr)]
        t = self.tag_of(addr)
        if t in s:
            s.remove(t)
            s.append(t)
            self.hits += 1
            return True
        s.append(t)
        if len(s) > self.ways:
            s.pop(0)
            self.evictions += 1
        self.misses += 1
        return False

    def run(self, trace):
        """Feed a whole trace through and return (hits, misses)."""
        for a in trace:
            self.access(a)
        return self.hits, self.misses


def miss_rate(capacity_bytes, block_bytes, ways, trace):
    """The fraction of `trace` that misses in a cache of that geometry."""
    c = Cache(capacity_bytes, block_bytes, ways)
    c.run(trace)
    n = c.hits + c.misses
    return c.misses / n if n else 0.0


if __name__ == "__main__":
    hot = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
    rates = [miss_rate(1024, 64, w, hot) for w in (1, 2, 4, 8)]
    print("three arrays 1 KB apart, 1 KB cache")
    print("miss rate by associativity:", np.round(rates, 4).tolist())
    print("sequential byte walk:", round(miss_rate(1024, 64, 1, walk(0, 4, 256)), 4))
'''}],
                "hints": [
                    "`block_of` is `addr // self.block_bytes`; the index is that number modulo `self.sets`, and the tag is that number divided by `self.sets`.",
                    "A Python list makes true LRU short: `s.remove(t); s.append(t)` on a hit, and `s.pop(0)` when an insertion overflows the set.",
                    "Count the miss *and* the eviction separately — the first access to a cold set misses without evicting anything.",
                ],
                "tests": [
                    {"name": "the address splits into offset, index and tag", "code": r'''
_c = Cache(1024, 64, 1)
assert _c.sets == 16, f"1 KB of 64 B blocks, one way, is 16 sets; got {_c.sets}"
assert _c.block_of(130) == 2, f"byte 130 lies in block 2, got {_c.block_of(130)}"
assert _c.index_of(1088) == 1, \
    f"block 17 in a 16-set cache indexes set 1, got {_c.index_of(1088)}"
assert _c.tag_of(1088) == 1, \
    f"block 17 in a 16-set cache carries tag 1, got {_c.tag_of(1088)}"
'''},
                    {"name": "widening the set moves bits from index to tag", "code": r'''
_d = Cache(1024, 64, 2)
assert _d.sets == 8, f"two ways halves the set count to 8, got {_d.sets}"
assert _d.index_of(1088) == 1, f"block 17 mod 8 is 1, got {_d.index_of(1088)}"
assert _d.tag_of(1088) == 2, \
    f"the bit the index gave up reappears in the tag: expected 2, got {_d.tag_of(1088)}"
'''},
                    {"name": "replacement is LRU and not FIFO", "code": r'''
_c = Cache(128, 64, 2)
assert _c.sets == 1, f"128 B of 64 B blocks, two ways, is a single set; got {_c.sets}"
_r = [_c.access(a) for a in (0, 64, 0, 128, 64)]
assert _r == [False, False, True, False, False], \
    ("re-touching block 0 must make it the most recent, so block 1 is the victim "
     f"and the last access misses; FIFO would hit there. Got {_r}")
assert (_c.hits, _c.misses) == (1, 4), f"expected 1 hit and 4 misses, got {_c.hits}, {_c.misses}"
'''},
                    {"name": "a byte walk hits inside the block it just fetched", "code": r'''
import numpy as np
_t = walk(0, 4, 256)
_m = miss_rate(1024, 64, 1, _t)
assert np.isclose(_m, 1.0 / 16.0), \
    (f"16 accesses fall in each 64 B block, so exactly one in 16 should miss; got {_m}")
'''},
                    {"name": "three hot arrays thrash a direct-mapped cache", "code": r'''
import numpy as np
_hot = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
assert len(_hot) == 48
_m = miss_rate(1024, 64, 1, _hot)
assert np.isclose(_m, 1.0), \
    ("all three arrays are 1 KB apart, so they collide on the same index and a "
     f"direct-mapped cache holds one of them at a time. Expected 1.0, got {_m}")
'''},
                    {"name": "associativity rescues exactly this case", "code": r'''
import numpy as np
_hot = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
_m4 = miss_rate(1024, 64, 4, _hot)
assert np.isclose(_m4, 0.25), \
    (f"four ways hold all three tags, leaving only the 12 first touches: expected 0.25, got {_m4}")
_m2 = miss_rate(1024, 64, 2, _hot)
assert np.isclose(_m2, 1.0), \
    (f"two ways still cannot hold three live tags under LRU: expected 1.0, got {_m2}")
'''},
                    {"name": "every access is accounted for", "code": r'''
_hot = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
_c = Cache(1024, 64, 1)
_h, _m = _c.run(_hot)
assert _h + _m == len(_hot), \
    f"48 accesses must produce 48 outcomes, got {_h} hits and {_m} misses"
assert _c.evictions == 44, \
    (f"only four sets are ever used, so exactly four misses land in an empty set "
     f"and evict nothing; the other 44 each throw a block out. Got {_c.evictions}")
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Where the misses actually come from",
            "summary": "Compulsory, capacity, conflict. The taxonomy is a decomposition of measurements, and you get it by running three caches at once.",
            "concepts": [
                "Compulsory: the first reference to a block. No cache of any size or shape avoids it.",
                "Capacity: the block was here, and the program's own volume pushed it out. A fully associative cache of the same size misses too.",
                "Conflict: the block was here, and the *index* pushed it out. A fully associative cache of the same size would have hit.",
                "The method: run the real cache, a fully associative cache of equal capacity, and an infinite cache over the same trace, and label each miss by which of them also missed.",
                "The taxonomy classifies a measurement, not a cause — the same program under a different block size produces a different split.",
            ],
            "read": [
                {
                    "title": "Two traces, one miss rate, opposite fixes",
                    "minutes": 16,
                    "body": r'''
Here are two address traces. The first is the one from module 1: three arrays of
four blocks each, at 0, 1024 and 2048, walked round-robin four times. The second is
a cyclic sweep over 2 KB — thirty-two consecutive blocks, four passes. Put both
through a 1 KB cache with 64-byte blocks and vary nothing but the associativity.

```python
def miss_rate(trace, ways, frames=16, block=64):
    sets = frames // ways
    tags = [[] for _ in range(sets)]
    misses = 0
    for addr in trace:
        b = addr // block
        s, t = tags[b % sets], b // sets
        if t in s:
            s.remove(t)
            s.append(t)
        else:
            s.append(t)
            if len(s) > ways:
                s.pop(0)
            misses += 1
    return misses / len(trace)


colliding = []
for _ in range(4):
    for i in range(4):
        for base in (0, 1024, 2048):
            colliding.append(base + i * 64)

sweep = [i * 64 for _ in range(4) for i in range(32)]

print("accesses: colliding %d, sweep %d" % (len(colliding), len(sweep)))
for name, trace in (("three arrays 1 KB apart", colliding),
                    ("2 KB cyclic sweep", sweep)):
    rates = " ".join("%5.2f" % miss_rate(trace, w) for w in (1, 2, 4, 16))
    print("%-24s miss rate at 1/2/4/16 ways: %s" % (name, rates))
```

Direct-mapped, both traces miss on every single access. A profiler reporting a miss
rate would print 100 per cent for each and stop there, and the two situations could
not be less alike: four ways takes the first trace to 0.25 and does nothing whatever
to the second, which stays at 1.00 even fully associative. The number was the same
and the correct response to it was opposite.

## Ask what a different cache would have done

There is no way to look at a miss and see its cause, so stop trying to. Ask a
counterfactual instead: *which other cache would have avoided this miss?* Three
caches answer between them, and each one is chosen to differ from the real cache in
exactly one respect.

An infinite cache never evicts anything, so the only misses it can take are
references to blocks that have never been referenced before. Every cache in existence
takes those, whatever its size or shape. Whatever the infinite cache misses on is
therefore the floor, and the name for it is a **compulsory** miss.

A fully associative cache of the *same capacity* evicts, but never because of where a
block's address falls — any block may occupy any frame. So a miss it takes beyond the
compulsory ones happened because the program asked for more live data than the cache
holds. That surplus is a **capacity** miss.

The real cache has the same capacity and a restricted placement. What it misses on
beyond what the fully associative cache missed on is attributable to the index and to
nothing else: a **conflict** miss.

Three measurements, two subtractions, and the definitions are complete — which is the
derivation *Splitting a measured miss rate three ways* in one paragraph:

$$m_{\text{compulsory}} = m_{inf}, \qquad
  m_{\text{capacity}} = m_{fa} - m_{inf}, \qquad
  m_{\text{conflict}} = m_{dm} - m_{fa}$$

Note what has been defined and what has not. Nothing here says why the program
touched what it touched. The three names are labels for *what a change of cache would
have done*, which is exactly the question an architect is asking, and it is why the
taxonomy is worth its arithmetic.

## Running it on both traces

Feed one trace to all three models at once and label each access by which of them
also missed.

```python
class LRU:
    """A set-associative tag store. One set makes it fully associative."""

    def __init__(self, sets, ways):
        self.sets, self.ways = sets, ways
        self.tags = [[] for _ in range(sets)]

    def access(self, block):
        s, t = self.tags[block % self.sets], block // self.sets
        if t in s:
            s.remove(t)
            s.append(t)
            return True
        s.append(t)
        if len(s) > self.ways:
            s.pop(0)
        return False


def classify(trace, ways, frames=16, block=64):
    real, full, seen = LRU(frames // ways, ways), LRU(1, frames), set()
    counts = {"hit": 0, "compulsory": 0, "capacity": 0, "conflict": 0}
    for addr in trace:
        b = addr // block
        first = b not in seen
        seen.add(b)
        fa_hit = full.access(b)          # every access, hit or miss
        if real.access(b):
            counts["hit"] += 1
        elif first:
            counts["compulsory"] += 1
        elif not fa_hit:
            counts["capacity"] += 1
        else:
            counts["conflict"] += 1
    return counts


colliding = []
for _ in range(4):
    for i in range(4):
        for base in (0, 1024, 2048):
            colliding.append(base + i * 64)

sweep = [i * 64 for _ in range(4) for i in range(32)]

for name, trace in (("three arrays", colliding), ("cyclic sweep", sweep)):
    for w in (1, 4):
        print("%-13s %2d-way %s" % (name, w, classify(trace, w)))
```

The infinite cache never appears in that code, because it does not need to: a set of
blocks ever referenced is the same model with none of the bookkeeping.

Take the colliding trace at one way: 12 compulsory, 36 conflict, 0 capacity, and not
one hit. Every number is checkable by hand. Twelve distinct blocks are touched, so
twelve first references, and the derivation's compulsory rate $M/(BN)$ gives
$768/(64 \times 48) = 0.25$, which is what 12 out of 48 is. Twelve live blocks in a
sixteen-frame cache fit with room over, so a fully associative cache of that capacity
never evicts anything it will want again and the capacity count is zero. What is left
— 36 accesses, three quarters of the trace — is placement, and nothing else.

Now read the second line of the same output. Four ways: the 36 conflict misses have
become 36 hits, and the 12 compulsory misses are exactly where they were. That is the
decomposition making a prediction and the prediction coming true: associativity
removes conflict misses, all of them if you give it enough ways, and it cannot touch
either of the other two columns.

The sweep says the opposite thing, and says it before you have built anything. Thirty
-two compulsory and 96 capacity at one way, and the identical split at four ways —
zero conflict misses at either. A trace that has no conflict misses to remove has
nothing to gain from associativity, and no amount of measuring after the fact will
change that. The lab's `least_associativity` is this observation turned into a
function: on the colliding trace it returns 4, and on the sweep it returns 1, where
the 1 does not mean direct-mapped is a good idea but that associativity has no work to
do here.

Each C also comes with the change that moves it. Compulsory misses are one per
distinct block, so the only levers are a larger block, which fetches neighbours you
have not asked for yet, and prefetching, which does the same thing under a different
name. Capacity misses need either a larger cache or a program that revisits its data
sooner — the tiling of a matrix multiply is exactly that change. Conflict misses need
associativity, or the data moved: padding an array's leading dimension by one block
breaks the congruence that piled its rows onto one set. And the block-size lever cuts
both ways, since doubling $B$ halves the compulsory count and halves the number of
frames at the same time, which is why the sandbox *A curve with no conflict misses in
it* has you read the height against $\text{stride}/B$ rather than against the capacity.

## The mistake: consulting the reference model only when the real cache misses

The reference cache exists to explain misses, so it seems natural — and it reads
better — to ask it only when there is a miss to explain. The bookkeeping looks
identical and the model is doing less work.

```python
class LRU:
    def __init__(self, sets, ways):
        self.sets, self.ways = sets, ways
        self.tags = [[] for _ in range(sets)]

    def access(self, block):
        s, t = self.tags[block % self.sets], block // self.sets
        if t in s:
            s.remove(t)
            s.append(t)
            return True
        s.append(t)
        if len(s) > self.ways:
            s.pop(0)
        return False


def classify(trace, ask_reference_on_hits, frames=4, ways=2, block=64):
    real, full, seen = LRU(frames // ways, ways), LRU(1, frames), set()
    counts = {"hit": 0, "compulsory": 0, "capacity": 0, "conflict": 0}
    for addr in trace:
        b = addr // block
        first = b not in seen
        seen.add(b)
        if ask_reference_on_hits:
            fa_hit = full.access(b)
            hit = real.access(b)
        else:
            hit = real.access(b)
            fa_hit = False if hit else full.access(b)
        if hit:
            counts["hit"] += 1
        elif first:
            counts["compulsory"] += 1
        elif not fa_hit:
            counts["capacity"] += 1
        else:
            counts["conflict"] += 1
    return counts


trace = [0, 128, 64, 192, 0, 256, 128]
print("every access:", classify(trace, True))
print("misses only :", classify(trace, False))
```

Seven accesses through a 256-byte cache, two ways against a four-frame reference, and
the two versions disagree: one capacity miss becomes one conflict miss. The re-touch
of block 0 in the middle of the trace is a hit in the real cache, so the starved
reference never sees it, so its recency order still has block 0 as the oldest thing it
holds. When block 4 arrives the starved reference evicts block 0 while the honest one
evicts block 2 — and the last access, to block 2, is then reported as a hit that the
real cache spoiled. A conflict miss invented out of nothing.

The direction of the error is what makes it expensive. It moves misses from the
capacity column into the conflict column, and those two columns recommend different
hardware. Acting on the corrupted numbers buys ways, which cost comparators and hit
time and would have changed nothing, when the measurement that was actually there
said buy capacity. A reference model has to see every reference; the clue is in the
name.

## Where the taxonomy stops holding

It classifies one measurement, not a program. All three counts belong to a
(trace, geometry) pair, and changing the geometry moves all of them at once —
doubling the block size lowers the compulsory count and raises the other two, so
comparing a compulsory count taken at 32-byte blocks with a conflict count taken at
64 is comparing two different experiments.

The conflict term can also come out negative, which a set of three non-negative
categories should not be able to do.

```python
def miss_rate(blocks, sets, ways):
    tags = [[] for _ in range(sets)]
    misses = 0
    for b in blocks:
        s, t = tags[b % sets], b // sets
        if t in s:
            s.remove(t)
            s.append(t)
        else:
            s.append(t)
            if len(s) > ways:
                s.pop(0)
            misses += 1
    return misses / len(blocks)


sweep = [b for _ in range(4) for b in range(5)]   # five blocks, four passes
dm = miss_rate(sweep, sets=4, ways=1)             # four frames, one way
fa = miss_rate(sweep, sets=1, ways=4)             # four frames, fully associative
print("direct-mapped     m_dm = %.2f" % dm)
print("fully associative m_fa = %.2f" % fa)
print("conflict rate m_dm - m_fa = %+.2f" % (dm - fa))
```

Five blocks cycling through four frames. The fully associative cache under LRU misses
on every access, because the victim is always the block wanted next. The
direct-mapped cache misses 55 per cent of the time: blocks 1, 2 and 3 own a set each
and survive all four passes, while blocks 0 and 4 fight over set 0. Restricting
placement did not only take choices away — it took away LRU's ability to make the
worst one, on three quarters of the data. The conflict rate is $-0.45$.

The subtraction leaks in a second, quieter way. The reference cache runs LRU, so
everything a smarter replacement policy could have saved is charged to capacity. That
column is not "misses caused by the size" but "misses caused by the size, under LRU",
and the gap between the two is real: on the twenty accesses above, LRU takes no hits
at all, the direct-mapped cache takes nine, and Belady's optimal takes twelve.

And there is a fourth C that no uniprocessor measurement can produce at all. Put a
second cache on the bus and a block can be taken away from you by another core's
write, with your own cache neither evicting it nor running out of room. The sandbox
*The floor a single cache cannot get below* ends on exactly that point, and module 4
gives it a state machine.

## What you are about to build

The lab *Classify every miss in a trace* is the Hill–Smith method as it appears
above: `classify` running three models over one trace and labelling every access, and
`least_associativity` searching for the smallest candidate that leaves the conflict
column at zero. Its checks are the numbers this page has already computed — 12
compulsory and 36 conflict on the colliding trace at one way, all 36 becoming hits at
four ways, 96 capacity misses on the sweep at every associativity — plus one that
matters more than it looks: the labels must partition the trace, so the four counts
have to sum to its length. The blanks unit *Three Cs, measured rather than argued*
walks the same three subtractions in four lines, and the derivation
*Splitting a measured miss rate three ways* writes them in symbols and ends on the
one lever that moves the compulsory floor.
''',
                },
            ],
            "quiz": {
                "title": "Which C is it, and what would fix it",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Two traces each miss on every access in the same 1 KB direct-mapped cache. Four ways takes one of them to a 0.25 miss rate and leaves the other at 1.00. What measurement tells the two apart before you build anything?",
                        "opts": [
                            "Whether a fully associative cache of the same capacity misses on them too",
                            "Whether the trace touches more distinct bytes altogether than the cache can hold",
                            "Whether the addresses in the trace are spaced by a power of two",
                            "Whether the first pass of the trace misses more often than later passes",
                        ],
                        "a": 0,
                        "whys": [
                            r"Same capacity, no placement restriction: whatever it still misses on is volume, and whatever it rescues was the index's doing. That single comparison is the whole of the conflict-capacity distinction.",
                            r"This is the right instinct pointed at the wrong quantity. Both of these traces have a working set that would fit — twelve blocks and thirty-two, in sixteen frames — so a byte count says 'fits' for one and 'does not' for the other without ever explaining why the first one missed anyway.",
                            r"Power-of-two spacing is a good predictor of conflict misses and a poor definition of one. It is a property of the addresses rather than of the cache, and a trace with no such spacing can still pile several live blocks onto one index.",
                            r"That comparison finds the compulsory misses, which both traces have and neither is limited by. It says nothing at all about whether the misses after the first pass came from volume or from placement.",
                        ],
                        "why": r"""
A miss carries no label, so the classification is a counterfactual: which other cache
would have avoided it? An equally sized fully associative cache differs from the real
one in placement alone, so a miss it also takes is about volume and a miss it rescues
is about the index. On the colliding trace it rescues 36 of 48; on the cyclic sweep it
rescues none. That measurement is available from a simulation before any silicon
exists, which is exactly why the method is worth its three models.
""",
                    },
                    {
                        "q": "A direct-mapped run over 48 accesses classifies as 12 compulsory, 36 conflict, 0 capacity, 0 hits. You rerun it four-way. What should the four numbers become?",
                        "opts": [
                            "12 compulsory and 36 hits, with both other columns still zero",
                            "12 compulsory, 36 capacity, and no hits, because the misses move columns",
                            "3 compulsory and 9 conflict, each column divided by four",
                            "12 compulsory and 36 conflict again, since the trace has not changed",
                        ],
                        "a": 0,
                        "whys": [
                            r"Conflict is defined as what full associativity would have rescued, so giving the cache enough ways converts precisely that column into hits and leaves the other two alone.",
                            r"Misses do not migrate between columns when the geometry changes: capacity is what the fully associative reference missed on, and it missed on nothing here, so that column cannot fill up no matter what the real cache does.",
                            r"Associativity is not a divisor. Four ways either holds the live tags of a set or it does not, and here three tags in four frames means the conflict column empties completely rather than shrinking by a factor.",
                            r"The trace is unchanged but the cache is not, and conflict is a statement about the cache. A count that is invariant to associativity is the definition of a capacity or compulsory miss.",
                        ],
                        "why": r"""
The measured decomposition is a prediction, and this is the prediction: the conflict
column is exactly the set of misses full associativity would have rescued, so
supplying enough ways turns all 36 into hits while the 12 first references stay
untouched. Running it and getting that answer is what validates the method — and
getting a different one means the reference model was consulted wrongly, which is the
usual defect in a three-cache simulator.
""",
                    },
                    {
                        "q": "A classifier feeds the fully associative reference model only the accesses on which the real cache missed. Which way do its numbers go wrong?",
                        "opts": [
                            "It reports conflict misses that were really capacity misses",
                            "It reports capacity misses that were really conflict misses",
                            "It reports compulsory misses as capacity misses, since first references are skipped",
                            "It reports fewer misses overall, because the reference model sees fewer accesses",
                        ],
                        "a": 0,
                        "whys": [
                            r"Hits are references, and a starved reference model keeps a stale recency order that makes it evict blocks the honest one would have kept — so it 'hits' where it should have missed, and the classifier blames the index for a shortage of room.",
                            r"The inversion of what happens. A starved reference model holds on to blocks it should have evicted, so it hits more often than it deserves to, and each of those spurious hits is scored as a conflict rather than as a capacity miss.",
                            r"First references are found from a set of blocks ever seen, which is checked before either cache is consulted, so the compulsory column survives this bug intact.",
                            r"The counts come from the real cache, which sees every access either way. The total number of misses is unaffected; the only casualty is which column each one lands in.",
                        ],
                        "why": r"""
The reference model's recency order is only right if it sees the same reference stream
the real cache sees, and a hit is a reference. Starve it and it evicts blocks that
were recently used, which leaves other blocks resident longer, which makes it hit
where an honest model would have missed — and a reference-model hit on a real-cache
miss is scored as conflict. The error therefore moves work out of the capacity column
into the conflict column, and those two columns recommend different hardware: ways
that would change nothing, instead of the capacity the run was actually asking for.
""",
                    },
                    {
                        "q": "The compulsory miss rate over $N$ accesses to $M$ bytes with $B$-byte blocks is $M/(BN)$. What does doubling $B$ do to a real cache of fixed capacity?",
                        "opts": [
                            "Halves that rate, and halves the number of frames the cache has",
                            "Halves that rate, leaving the other two categories where they were",
                            "Leaves that rate alone, since $M$ itself has not changed",
                            "Halves that rate and halves the traffic each miss puts on the bus",
                        ],
                        "a": 0,
                        "whys": [
                            r"One first reference per distinct block, and doubling the block halves the number of blocks — but capacity is fixed, so the frame count halves with it and the blocks competing for each set change too.",
                            r"True as far as it goes, and it is the half of the trade that gets quoted. Capacity is bytes, so a doubled block means half as many frames, and unrelated data that used to sit in its own frame now shares one or is evicted sooner.",
                            r"$M$ is unchanged but the rate counts blocks, not bytes: $M/B$ distinct blocks at twice the size is half as many first references, so the rate does move.",
                            r"The rate does halve, but a miss now fetches twice as many bytes: half as many misses each costing double is the same traffic, not less, which is the trade rather than a saving.",
                        ],
                        "why": r"""
Compulsory misses are one per distinct block, so $M/B$ of them, and doubling $B$
halves the count. Capacity is bytes and does not change, so the same cache now holds
half as many frames, and each miss drags twice the data across the bus. The miss rate
against block size therefore falls and then rises, with the turning point depending on
the program — which is the reason block size is measured on real traces rather than
argued from a formula.
""",
                    },
                    {
                        "q": "On a cyclic sweep over five blocks in a four-frame cache, LRU makes a fully associative cache miss on every access while a direct-mapped one hits 45 per cent of the time. What does that do to the three-C subtraction?",
                        "opts": [
                            "The conflict term goes negative, because restricting placement helped here",
                            "The conflict term is zero, because the two caches hold identical numbers of blocks",
                            "The capacity term goes negative, because the working set exceeds the cache",
                            "Nothing: the subtraction is defined so that all three terms stay non-negative",
                        ],
                        "a": 0,
                        "whys": [
                            r"Conflict is $m_{dm} - m_{fa}$, and here the direct-mapped cache is the better of the two, so the difference comes out below zero — an honest report that placement was an advantage on this trace.",
                            r"Equal capacity is what makes the comparison fair, not what makes it come out zero. The two caches evict different blocks with those same frames, and on a cyclic sweep that difference is the entire result.",
                            r"Capacity is $m_{fa} - m_{inf}$, and the fully associative cache can never miss less often than an infinite one, so that term cannot go below zero however the working set is sized.",
                            r"Nothing in the arithmetic enforces it. The three terms are defined as differences between measurements, and a measurement that comes out the wrong way round produces a negative term rather than being clipped to zero.",
                        ],
                        "why": r"""
Restricting placement takes choices away from the replacement policy, and on a cyclic
sweep LRU's choices are the worst available: the fully associative cache evicts
exactly the block wanted next, every time. The direct-mapped cache cannot make that
mistake for the three blocks that own a set to themselves, so it outlives its own
reference model and $m_{dm} - m_{fa}$ comes out at $-0.45$. The taxonomy is a
subtraction between two measurements, not a partition guaranteed by construction, and
this is where the difference shows.
""",
                    },
                    {
                        "q": "A profile of your L1 comes back 5 per cent compulsory, 90 per cent capacity, 5 per cent conflict. Which change is worth making?",
                        "opts": [
                            "Restructure the program to revisit its data sooner, or build a larger cache",
                            "Raise the associativity, since that is the standard remedy for a bad miss rate",
                            "Shrink the block size so that the cache holds more separate blocks",
                            "Nothing helps: capacity misses are as unavoidable as compulsory ones",
                        ],
                        "a": 0,
                        "whys": [
                            r"Capacity misses come from live data exceeding the frames available, so the two levers are more frames or a working set that fits between reuses — which is what tiling a loop nest does.",
                            r"The reflex answer, and the profile has already priced it: conflict is 5 per cent, so even perfect associativity buys 5 per cent while costing comparators and hit time. Measuring first is what stops that trade from being made blind.",
                            r"More frames of less use each. Smaller blocks raise the compulsory count and discard spatial locality, and neither of those is the column that this profile says is doing the damage.",
                            r"Compulsory misses are unavoidable in a cache of any size; capacity misses are by definition the ones a bigger cache removes, and a program that reuses its data sooner removes them without any hardware at all.",
                        ],
                        "why": r"""
The whole value of the decomposition is that it prices the options before they are
paid for. Ninety per cent capacity means the live data does not fit between reuses, so
the fixes are more frames or a program that comes back to its data sooner — blocking a
matrix multiply is the second one, and it costs no silicon. Associativity is capped at
the 5 per cent in the conflict column however many ways are added, and that is the
number to weigh against the hit time those ways would cost.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "A curve with no conflict misses in it",
                "visualiser": "cache",
                "minutes": 8,
                "initial": {"kb": 4, "ways": 4, "stride": 16},
                "brief": r'''
The same experiment as module 1, read with the three Cs in hand. Remember what the
trace is: a cyclic sweep over a working set of four times the cache, so the only
reuse available to it is spatial reuse inside a block.
''',
                "notice": [
                    "Read the height at a stride of 16 B: exactly 25 per cent, which is 16/64. Halve the stride to 8 B and it halves to 12.5. These are compulsory-and-capacity misses in a fixed ratio — the block size, not the cache, sets them.",
                    "Now sweep associativity from 1 to 16 at that stride. The marker does not move by a pixel, and the readout underneath splits it for you: 8.33 per cent compulsory, the rest capacity, **zero conflict**. That is the definition — a fully associative cache of this size does no better than a direct-mapped one here, so there is nothing for associativity to buy.",
                    "The one place the faint curves separate is 24 KB, where direct-mapped reads 16.7 per cent and the associative ones read 25. Zero conflict misses does not mean associativity is harmless at every capacity; it means it is not the lever at *this* one.",
                    "Set the stride to 64 B or 128 B. The curve pins to 100 per cent from 1 KB to 16 KB — one access per block, so no spatial reuse is left to collect — and then drops to 33.3 per cent at 32 KB, where the 32 KB walk finally fits and temporal reuse arrives all at once. Below the cliff no associativity helps; above it none is needed.",
                ],
            },
            "derive": {
                "title": "Splitting a measured miss rate three ways",
                "minutes": 14,
                "vars": ["m_dm", "m_fa", "m_inf", "M", "B", "N"],
                "brief": r'''
You run the same trace through three caches and measure three miss rates:

- $m_{dm}$ — the real cache, with its real index;
- $m_{fa}$ — fully associative, same capacity, LRU;
- $m_{inf}$ — infinite, so it never evicts anything.

Every miss in the real cache belongs to exactly one of three classes. Write each
class's rate in terms of those three measurements.
''',
                "steps": [
                    {
                        "prompt": "The compulsory rate. Which of the three measurements is it, unchanged?",
                        "answer": "m_{inf}",
                        "hint": "An infinite cache evicts nothing, so the only misses left in it are first references.",
                        "deconstruct": [
                            "$m_{inf}$ counts a miss only when the block has never been referenced before.",
                            "That is precisely the definition of a compulsory miss.",
                        ],
                    },
                    {
                        "prompt": "The capacity rate: misses the fully associative cache suffers that the infinite one does not. Write it.",
                        "answer": "m_{fa} - m_{inf}",
                        "hint": "The fully associative cache has no index at all, so anything it misses beyond a first reference it missed on volume.",
                        "deconstruct": [
                            "$m_{fa}$ contains the compulsory misses plus whatever LRU had to throw out.",
                            "Subtract the compulsory part to leave the volume-driven part.",
                        ],
                    },
                    {
                        "prompt": "The conflict rate: what the real index costs you over a fully associative cache of the same size. Write it.",
                        "answer": "m_{dm} - m_{fa}",
                        "hint": "Two caches, same capacity, same replacement policy, different placement. The difference is placement alone.",
                        "deconstruct": [
                            "$m_{dm}$ contains everything: compulsory, capacity and conflict.",
                            "$m_{fa}$ contains compulsory and capacity, so the difference is what is left.",
                        ],
                    },
                    {
                        "prompt": "What fraction of the real cache's misses could full associativity remove? Write it in terms of $m_{dm}$ and $m_{fa}$.",
                        "answer": "\\frac{m_{dm} - m_{fa}}{m_{dm}}",
                        "hint": "Take the conflict rate you just wrote and express it as a share of the total miss rate.",
                        "deconstruct": [
                            "Conflict misses per access: $m_{dm} - m_{fa}$.",
                            "All misses per access: $m_{dm}$. Divide.",
                        ],
                    },
                    {
                        "prompt": "A program makes $N$ accesses over a region of $M$ bytes with blocks of $B$ bytes. Every block is touched at least once. Write the compulsory miss rate.",
                        "answer": "\\frac{M}{B \\cdot N}",
                        "hint": "Count the compulsory misses first — one per distinct block — then divide by the number of accesses.",
                        "deconstruct": [
                            "The region contains $M/B$ distinct blocks, and each costs exactly one first reference.",
                            "A rate is misses per access, so divide that count by $N$.",
                        ],
                    },
                ],
                "closing": r'''
Notice the last one: the only lever on the compulsory rate is $B$. Doubling the
block size halves it — and simultaneously halves the number of blocks the cache
holds, which pushes capacity and conflict misses up. That trade is the reason block
size is a measured choice rather than a derived one.
''',
            },
            "blanks": {
                "title": "Three Cs, measured rather than argued",
                "minutes": 8,
                "caption": "three_cs.py — a decomposition you get by running three caches",
                "lang": "python",
                "brief": r"""
The taxonomy is often taught as three definitions to memorise. It is better understood as
a *subtraction*: run the same trace through three caches and difference the results. Fill
in which three.
""",
                "listing": """# Same trace, three caches, three miss counts.

compulsory = misses_of( ___ )

capacity   = misses_of( ___ ) - compulsory

conflict   = misses_of(the real cache) - ___

# Which means: doubling the associativity can only remove
# ___ misses, and none of the others.
""",
                "blanks": [
                    {
                        "prompt": "Which cache still misses on a block it has never seen?",
                        "hole": "?",
                        "opts": [
                            "an infinite fully-associative cache",
                            "the real cache",
                            "a direct-mapped cache of the same size",
                            "a cache holding one block",
                        ],
                        "a": 0,
                        "why": "An infinite cache never evicts anything, so every miss it takes is a first reference — and no cache of any size or shape can avoid those. That is the floor: the only ways to reduce compulsory misses are prefetching and larger blocks, both of which fetch data before it is asked for.",
                        "whys": [
                            "An infinite cache never evicts anything, so every miss it takes is a first reference — and no cache of any size or shape can avoid those. That is the floor: the only ways to reduce compulsory misses are prefetching and larger blocks, both of which fetch data before it is asked for.",
                            "The real cache's misses are all three categories mixed together — which is the thing being decomposed.",
                            "A direct-mapped cache adds the maximum number of conflict misses, which is the opposite of isolating the compulsory ones.",
                            "A one-block cache misses on almost everything and separates nothing.",
                        ],
                    },
                    {
                        "prompt": "Which cache has the right size but no conflicts?",
                        "hole": "?",
                        "opts": [
                            "a fully-associative cache of the same capacity",
                            "an infinite cache",
                            "a direct-mapped cache of the same capacity",
                            "the real cache with a bigger block",
                        ],
                        "a": 0,
                        "why": "Fully associative removes conflict misses by construction — any block may live anywhere, so nothing is evicted because of where its address happened to land. What is left over the compulsory count is caused purely by the program's own working set exceeding the capacity.",
                        "whys": [
                            "Fully associative removes conflict misses by construction — any block may live anywhere, so nothing is evicted because of where its address happened to land. What is left over the compulsory count is caused purely by the program's own working set exceeding the capacity.",
                            "Already used, for compulsory. An infinite cache has no capacity misses either, so it cannot measure them.",
                            "Direct-mapped is maximally conflict-prone, so its extra misses are precisely the ones this step is trying to exclude.",
                            "Changing the block size changes the compulsory count too, so the three measurements would no longer be comparable.",
                        ],
                    },
                    {
                        "prompt": "Subtract what has already been accounted for.",
                        "hole": "?",
                        "opts": ["compulsory + capacity", "compulsory", "capacity", "zero"],
                        "a": 0,
                        "why": "Whatever the real cache misses on beyond what an equally-sized fully-associative cache would is, by definition, the cost of its restricted placement. The three numbers are defined to sum to the total, which is what makes it a decomposition rather than three independent measurements.",
                        "whys": [
                            "Whatever the real cache misses on beyond what an equally-sized fully-associative cache would is, by definition, the cost of its restricted placement. The three numbers are defined to sum to the total, which is what makes it a decomposition rather than three independent measurements.",
                            "Subtracting only the compulsory count leaves capacity misses miscounted as conflicts, which would blame the shape for a problem caused by the size.",
                            "Subtracting only capacity leaves the first references in, inflating conflict by the compulsory count.",
                            "Would make conflict equal to the total misses, which is true only for a cache with no capacity pressure at all.",
                        ],
                    },
                    {
                        "prompt": "So what does more associativity actually fix?",
                        "hole": "?",
                        "opts": ["conflict", "capacity", "compulsory", "all three"],
                        "a": 0,
                        "why": "Only conflict, and that is the practical value of the decomposition: measure first, and if the misses are mostly capacity then adding ways is spending area and hit time on nothing. A bigger cache, or a program that touches less data, is the fix for capacity.",
                        "whys": [
                            "Only conflict, and that is the practical value of the decomposition: measure first, and if the misses are mostly capacity then adding ways is spending area and hit time on nothing. A bigger cache, or a program that touches less data, is the fix for capacity.",
                            "Capacity misses come from the working set exceeding the size; rearranging where blocks may sit inside the same number of bytes does not create room.",
                            "A first reference misses in any cache. Associativity cannot help with data that has never been fetched.",
                            "If associativity fixed everything, every cache would be fully associative — and the reason they are not is hit time and comparator cost.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Classify every miss in a trace",
                "runtime": "python",
                "minutes": 42,
                "brief": r'''
Implement the Hill–Smith method directly: run three caches over one trace and label
each access.

`classify(trace, block_bytes, capacity_bytes, ways)` returns a dict with the four
keys in `KINDS`. For each address, in this order:

1. note whether this block has ever been referenced before;
2. feed it to a fully associative LRU cache holding `capacity_bytes // block_bytes`
   blocks, and remember whether that hit;
3. feed it to the real cache of the requested geometry.

Then label the access: a hit in the real cache is `"hit"`; otherwise it is
`"compulsory"` if this was the first reference, `"capacity"` if the fully
associative cache missed too, and `"conflict"` if it did not.

All three caches must see **every** access, whatever the label — a reference model
that only sees the misses is not a model of anything.

`least_associativity(trace, block_bytes, capacity_bytes, candidates)` returns the
smallest candidate that leaves zero conflict misses, or `None` if none does. Skip
any candidate that does not divide the block count evenly.

The `_LRU` helper is yours to write too: one list of tags per set, LRU order, exactly
as in module 1. A fully associative cache is that class with one set.
''',
                "files": [
                    {"name": "traces.py", "ro": True, "content": r'''
"""Deterministic address traces. Read only: the checks assume these exact walks."""


def walk(start, stride, count, passes=1):
    """`passes` sweeps over `count` addresses spaced `stride` bytes apart."""
    out = []
    for _ in range(passes):
        for i in range(count):
            out.append(start + i * stride)
    return out


def interleave(*traces):
    """Round-robin several traces into one, stopping at the shortest."""
    n = min(len(t) for t in traces) if traces else 0
    out = []
    for i in range(n):
        for t in traces:
            out.append(t[i])
    return out
'''},
                    {"name": "main.py", "content": r'''
import numpy as np
from traces import walk, interleave

KINDS = ("hit", "compulsory", "capacity", "conflict")


class _LRU:
    """A set-associative tag store. One set makes it fully associative."""

    def __init__(self, sets, ways):
        self.sets = sets
        self.ways = ways
        self.tags = [[] for _ in range(sets)]

    def access(self, block):
        """Return True on a hit; insert and evict LRU on a miss."""
        # TODO
        return False


def classify(trace, block_bytes, capacity_bytes, ways):
    """Label every access in `trace` as hit, compulsory, capacity or conflict."""
    counts = {k: 0 for k in KINDS}
    # TODO: build the real cache, the fully associative reference of equal
    #       capacity, and a set of blocks ever seen; feed all three every access.
    return counts


def least_associativity(trace, block_bytes, capacity_bytes, candidates):
    """Smallest candidate associativity with no conflict misses left, or None."""
    # TODO
    return None


if __name__ == "__main__":
    hot = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
    for w in (1, 2, 4):
        print(w, "way:", classify(hot, 64, 1024, w))
    print("least associativity that clears it:",
          least_associativity(hot, 64, 1024, [1, 2, 4, 8, 16]))
    sweep = walk(0, 64, 32, 4)
    print("2 KB working set in a 1 KB cache:", classify(sweep, 64, 1024, 4))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np
from traces import walk, interleave

KINDS = ("hit", "compulsory", "capacity", "conflict")


class _LRU:
    """A set-associative tag store. One set makes it fully associative."""

    def __init__(self, sets, ways):
        self.sets = sets
        self.ways = ways
        self.tags = [[] for _ in range(sets)]

    def access(self, block):
        """Return True on a hit; insert and evict LRU on a miss."""
        s = self.tags[block % self.sets]
        t = block // self.sets
        if t in s:
            s.remove(t)
            s.append(t)
            return True
        s.append(t)
        if len(s) > self.ways:
            s.pop(0)
        return False


def classify(trace, block_bytes, capacity_bytes, ways):
    """Label every access in `trace` as hit, compulsory, capacity or conflict."""
    n_blocks = capacity_bytes // block_bytes
    real = _LRU(n_blocks // ways, ways)
    full = _LRU(1, n_blocks)
    seen = set()
    counts = {k: 0 for k in KINDS}
    for addr in trace:
        b = addr // block_bytes
        first = b not in seen
        seen.add(b)
        fa_hit = full.access(b)
        hit = real.access(b)
        if hit:
            counts["hit"] += 1
        elif first:
            counts["compulsory"] += 1
        elif not fa_hit:
            counts["capacity"] += 1
        else:
            counts["conflict"] += 1
    return counts


def least_associativity(trace, block_bytes, capacity_bytes, candidates):
    """Smallest candidate associativity with no conflict misses left, or None."""
    n_blocks = capacity_bytes // block_bytes
    for w in sorted(candidates):
        if w > n_blocks or n_blocks % w:
            continue
        if classify(trace, block_bytes, capacity_bytes, w)["conflict"] == 0:
            return w
    return None


if __name__ == "__main__":
    hot = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
    for w in (1, 2, 4):
        print(w, "way:", classify(hot, 64, 1024, w))
    print("least associativity that clears it:",
          least_associativity(hot, 64, 1024, [1, 2, 4, 8, 16]))
    sweep = walk(0, 64, 32, 4)
    print("2 KB working set in a 1 KB cache:", classify(sweep, 64, 1024, 4))
'''}],
                "hints": [
                    "`_LRU.access` is the body you wrote in module 1, with the block number handed to it instead of the address.",
                    "A fully associative cache of the same capacity is `_LRU(1, capacity_bytes // block_bytes)` — one set, every block a way.",
                    "Query the fully associative model on every access, hit or miss, before you consult the real cache; if you only ask it about misses its LRU order drifts and the classification goes wrong.",
                ],
                "tests": [
                    {"name": "a sequential walk is compulsory misses and nothing else", "code": r'''
_c = classify(walk(0, 4, 256), 64, 1024, 1)
assert _c["compulsory"] == 16, \
    f"1 KB of data in 64 B blocks is 16 first references; got {_c['compulsory']}"
assert _c["hit"] == 240, f"the other 240 accesses hit inside a fetched block; got {_c['hit']}"
assert _c["capacity"] == 0 and _c["conflict"] == 0, \
    f"nothing is evicted here, so neither class can be non-zero: {_c}"
'''},
                    {"name": "the labels partition the trace", "code": r'''
_t = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
_c = classify(_t, 64, 1024, 1)
assert sum(_c.values()) == len(_t), \
    (f"every one of the {len(_t)} accesses gets exactly one label, so the counts "
     f"must sum to that; got {sum(_c.values())} from {_c}")
assert _c["hit"] == 0, f"a direct-mapped cache hits nothing on this trace; got {_c['hit']}"
'''},
                    {"name": "colliding arrays produce conflict misses, not capacity misses", "code": r'''
_t = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
_c = classify(_t, 64, 1024, 1)
assert _c["conflict"] == 36, \
    (f"12 blocks of live data in a 16-block cache fits easily, so 36 of the 48 "
     f"accesses are the index's fault alone; got {_c['conflict']}")
assert _c["capacity"] == 0, \
    f"the working set is three quarters of the cache, so nothing is a capacity miss: {_c}"
'''},
                    {"name": "an oversized working set produces capacity misses at every associativity", "code": r'''
_sweep = walk(0, 64, 32, 4)
for _w in (1, 2, 4, 16):
    _c = classify(_sweep, 64, 1024, _w)
    assert _c["capacity"] == 96, \
        (f"a 2 KB cyclic sweep through a 1 KB cache re-misses every block after the "
         f"first pass, whatever the associativity; at {_w} ways got {_c}")
    assert _c["conflict"] == 0, \
        f"full associativity misses just as often here, so nothing is a conflict: {_c}"
'''},
                    {"name": "associativity is chosen by measurement", "code": r'''
_t = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
_w = least_associativity(_t, 64, 1024, [1, 2, 4, 8, 16])
assert _w == 4, \
    f"three live tags per set need three ways, and 4 is the next candidate up; got {_w}"
_cap = least_associativity(walk(0, 64, 32, 4), 64, 1024, [1, 2, 4, 8, 16])
assert _cap == 1, \
    (f"on a cyclic sweep even a direct-mapped cache has no conflict misses, so the "
     f"answer is 1 and it means associativity has nothing here to fix; got {_cap}")
assert least_associativity(_t, 64, 1024, [1, 2]) is None, \
    "neither candidate holds three live tags, so none of them qualifies"
'''},
                    {"name": "raising associativity converts conflict misses into hits", "code": r'''
_t = interleave(walk(0, 64, 4, 4), walk(1024, 64, 4, 4), walk(2048, 64, 4, 4))
_one = classify(_t, 64, 1024, 1)
_four = classify(_t, 64, 1024, 4)
assert _four["compulsory"] == _one["compulsory"] == 12, \
    f"first references are untouched by associativity: {_one} vs {_four}"
assert _four["hit"] == _one["hit"] + _one["conflict"], \
    (f"every conflict miss should have become a hit: {_one['hit']} + "
     f"{_one['conflict']} != {_four['hit']}")
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Access time and the traffic a write costs",
            "summary": "AMAT turns a miss rate into cycles. The write policy turns it into bytes on the bus.",
            "concepts": [
                "$\\text{AMAT} = t_{hit} + m \\cdot t_{penalty}$ — one hit time always, and the penalty only sometimes.",
                "Two levels compose: the L2 access time and its own miss rate become the L1 penalty.",
                "Local miss rate is measured against accesses that reach the level; global miss rate is measured against all accesses, and is the product.",
                "Write-back with write-allocate moves a whole block on a miss and another on a dirty eviction; write-through with no-write-allocate sends one word per write, and still fetches a whole block whenever a *read* misses.",
                "Which wins is arithmetic, not doctrine: it turns on how many times a block is written before it leaves.",
            ],
            "read": [
                {
                    "title": "Where 512 accesses go, in bytes and then in cycles",
                    "minutes": 17,
                    "body": r'''
A loop walks a 1 KB array twice, four bytes at a time, storing to every fourth
element and loading the rest: 512 accesses, 128 of them writes, over sixteen
64-byte blocks. The cache is 1 KB, two-way, 64-byte blocks — the array fits in it
with nothing to spare and nothing to evict. Count the bytes that cross the memory
interface under each write policy.

```text
write-back, write-allocate         2048 bytes moved
write-through, no-write-allocate   1536 bytes moved
```

That is the wrong way round according to the usual summary, which has write-back as
the policy that saves traffic and write-through as the one that floods the bus. Here
write-back moves a third more. Nothing is broken; the summary left out the quantity
the comparison actually turns on.

```python
class Cache:
    """policy is "wb" (write-back, write-allocate) or "wt" (write-through, no-allocate)."""

    def __init__(self, frames, block, ways, policy, word=4):
        self.block, self.ways, self.policy, self.word = block, ways, policy, word
        self.sets = frames // ways
        self.tags = [[] for _ in range(self.sets)]
        self.dirty = [set() for _ in range(self.sets)]
        self.hits = self.misses = self.bytes_in = self.bytes_out = 0

    def access(self, op, addr):
        b = addr // self.block
        i, t = b % self.sets, b // self.sets
        s, d = self.tags[i], self.dirty[i]
        if op == "w" and self.policy == "wt":
            self.bytes_out += self.word            # every write goes onward
        if t in s:
            s.remove(t)
            s.append(t)
            if op == "w" and self.policy == "wb":
                d.add(t)
            self.hits += 1
            return
        self.misses += 1
        if op == "w" and self.policy == "wt":      # no-write-allocate: nothing fetched
            return
        self.bytes_in += self.block                # allocate
        s.append(t)
        if op == "w":
            d.add(t)
        if len(s) > self.ways:
            v = s.pop(0)
            if v in d:
                d.discard(v)
                self.bytes_out += self.block       # a dirty victim goes back

    def flush(self):
        moved = sum(self.block * len(d) for d in self.dirty)
        for d in self.dirty:
            d.clear()
        self.bytes_out += moved
        return moved


def rw_walk(count, passes, write_every, stride=4):
    out, k = [], 0
    for _ in range(passes):
        for i in range(count):
            out.append(("w" if k % write_every == 0 else "r", i * stride))
            k += 1
    return out


def run(trace, policy):
    c = Cache(16, 64, 2, policy)
    for op, addr in trace:
        c.access(op, addr)
    c.flush()
    return c


trace = rw_walk(256, passes=2, write_every=4)
print("512 accesses, %d of them writes, over 16 blocks"
      % sum(1 for op, _ in trace if op == "w"))
for policy in ("wb", "wt"):
    c = run(trace, policy)
    print("  %s: %3d hits %3d misses, %4d bytes in, %4d out, %4d moved in total"
          % (policy, c.hits, c.misses, c.bytes_in, c.bytes_out,
             c.bytes_in + c.bytes_out))

print("writes per block   write-back   write-through")
for every in (16, 8, 4, 2):
    t = rw_walk(256, passes=2, write_every=every)
    k = sum(1 for op, _ in t if op == "w") // 16
    print("%16d   %6d       %6d"
          % (k, run(t, "wb").bytes_in + run(t, "wb").bytes_out,
             run(t, "wt").bytes_in + run(t, "wt").bytes_out))
```

## Price one block, and the whole trace follows

Take a single block and ask what each policy spends on it over its lifetime in the
cache. Let the block be $B$ bytes, a word $V$ bytes, and let $k$ be the number of
times the program writes to that block before it is evicted.

Write-back with write-allocate fetches the block on the first miss, read or write —
$B$ bytes in. Every subsequent store lands in the cache and sets a dirty bit, and
none of them reaches memory. When the block finally leaves, if it was written at all,
it goes back whole: $B$ bytes out. The total is $2B$ **whatever $k$ is**. Sixteen
blocks at 128 bytes each is 2048, which is the number in the first table, and the
2048 column in the second one that never moves.

Write-through with no-write-allocate never allocates on a store, so a block is only
ever resident because a *read* missed and fetched it: $B$ in. Each of the $k$ writes
sends its word onward: $kV$ out. The total is $B + kV$, and it grows with $k$.

Set the two equal and the crossover is immediate:

$$B + kV = 2B \quad \Longrightarrow \quad k = \frac{B}{V}$$

With 64-byte blocks and 4-byte words, sixteen writes per block. The second table in
the run above sweeps $k$ over 2, 4, 8 and 16 writes per block and the write-through
column climbs 1152, 1280, 1536, 2048 while write-back sits at 2048 throughout —
meeting it exactly at sixteen, which is $B/V$ measured rather than asserted. The
opening trace has eight writes per block, comfortably under the crossover, and that
single number is what the doctrine left out.

The derivation *AMAT, global miss rates and bytes moved* does this per access rather
than per block: $m B (1 + d)$ for write-back, where $d$ is the fraction of victims
found dirty, against $(1-w) m B + w V$ for write-through. Same content, expressed
against a different denominator, and the per-block form is the one to reach for when
you want the crossover.

## A miss is not a unit of cost

Look again at the miss counts in the first table: 16 for write-back, 32 for
write-through. The write-through cache missed twice as often on identical work, and
moved fewer bytes.

The reason is the no-write-allocate rule. In the first pass each block is met by a
store, which misses and allocates nothing, and then by a load, which misses again and
fetches. Two misses per block, and the first of them moved zero bytes and stalled
nothing worth mentioning — the store went into a write buffer and the pipeline carried
on. A raw miss count silently assumes every miss costs the same thing, and across a
policy change that assumption fails badly enough to reverse the ranking. Compare
bytes, or compare cycles, and say which.

## From a rate to cycles

Every access pays the hit time. The tag check has to happen before anyone knows
whether it was a hit, so $t_{hit}$ is not conditional; the penalty is what a miss adds
on top. That is the whole of

$$\text{AMAT} = t_{hit} + m \cdot t_{penalty}$$

and it composes downwards without any new idea, because what an L1 miss costs *is* the
L2's average access time.

```python
def amat(t_hit, miss_rate, t_penalty):
    return t_hit + miss_rate * t_penalty


t1, m1, t2, m2_local, tm = 1.0, 0.05, 12.0, 0.20, 200.0
m2_global = m1 * m2_local

penalty = amat(t2, m2_local, tm)
print("L1 miss penalty = the L2's own AMAT = %.1f cycles" % penalty)
print("AMAT            = %.2f cycles" % amat(t1, m1, penalty))
print("using the global rate inside = %.2f cycles"
      % amat(t1, m1, amat(t2, m2_global, tm)))
print("global L2 miss rate = %.2f%% of all accesses" % (100 * m2_global))
print("cycles spent waiting on memory = %.2f of %.2f"
      % (m2_global * tm, amat(t1, m1, penalty)))
```

An L1 that hits in a cycle and misses 5 per cent of the time, an L2 that answers in
12 and misses on a fifth of what reaches it, and a memory at 200 cycles: 3.60 cycles
per access. Then read the last line. Two of those 3.60 cycles — more than half the
total — are spent in the one per cent of accesses that reach memory. That is the
shape of every hierarchy calculation, and it is why the memory system is worth a
course: the term that dominates the average is the one that almost never happens.

## The mistake: putting the global rate inside the parentheses

The middle line of that run is the wrong answer, 1.70 cycles against 3.60, and the
reasoning that produces it is careful rather than careless. The L2's local rate of 20
per cent looks like an exaggeration — the L2 is not failing on a fifth of the
program's accesses, it is failing on a fifth of the few that got past the L1, and the
honest share of all accesses is $0.05 \times 0.20 = 1\%$. Both of those statements are
true. Substituting the second into the composed formula is still wrong, because the
$m_1$ already sitting in front of the bracket is what accounts for reaching the L2 at
all; using the global rate inside counts that filtering twice and halves the answer.

The rule that prevents it is a question about the denominator: **every miss rate is
measured against the accesses that arrive at its own level.** Inside the bracket you
are already at the L2, so the L2's own local rate belongs there. The global rate is
for a different purpose entirely — comparing levels, or costing memory bandwidth,
where what you want is the share of *all* accesses.

## Reading a plot as an input to arithmetic

The sandbox *Turning a miss rate into cycles* is the module 1 curve again, now to be
converted rather than admired. The same simulation reproduces it, so the conversion
can be checked rather than eyeballed:

```python
WORKING_SET, LINE = 32 * 1024, 64


def miss_rate(kb, ways, stride, passes=3):
    lines = (kb * 1024) // LINE
    sets = max(1, lines // ways)
    tags = [[] for _ in range(sets)]
    hits = total = 0
    for _ in range(passes):
        for addr in range(0, WORKING_SET, stride):
            line = addr // LINE
            s, t = tags[line % sets], line // sets
            total += 1
            if t in s:
                s.remove(t)
                s.append(t)
                hits += 1
            else:
                s.append(t)
                if len(s) > ways:
                    s.pop(0)
    return (total - hits) / total


for kb in (8, 16, 32, 64):
    for stride in (8, 4):
        m = miss_rate(kb, 2, stride)
        print("%2d KB, %d B stride: miss rate %5.2f%%, AMAT %5.2f cycles"
              % (kb, stride, 100 * m, 1 + m * 100))
print("compulsory floor at a 4 B stride: %.2f%%" % (100 * 512 / (8192 * 3)))
```

With a 1-cycle hit and a 100-cycle penalty, a 12.5 per cent miss rate is 13.5 cycles
per access — thirteen and a half times what the same access costs when it hits. Going
from 8 KB to 16 KB changes nothing at all, and then 32 KB takes the same walk to 4.17
per cent and 5.17 cycles, a saving of 8.33 cycles on every access in the program.
Doubling again to 64 KB saves nothing further, because 2.08 per cent at the 4-byte
stride is the compulsory floor: one miss per 64-byte line, spread over three passes,
$512/(8192 \times 3)$. A cache with no capacity misses left cannot be improved by
being made larger, and the arithmetic says so before the silicon is spent.

## Where this stops holding

AMAT prices a stall as though the processor waits for one miss at a time. An
out-of-order core with a non-blocking cache does not: it keeps issuing, and a second
miss to an independent address overlaps the first. If two misses are in flight
together on average, the 6.0-cycle AMAT of a single-level cache with a 5 per cent miss
rate and a 100-cycle penalty corresponds to about $1 + 0.05 \times 50 = 3.5$ cycles of
actual stall. AMAT overstates in that direction, and it is the direction most modern
machines lean, which is why a design decision that AMAT says is worth 8 cycles per
access may be worth four in a real pipeline.

It understates in the other direction whenever the penalty stops being a constant.
Two hundred cycles is a lightly loaded number; a DRAM row miss costs more, a bank
conflict more again, and a queue at the memory controller adds delay that rises with
how much traffic the rest of the machine is generating. That is where the two halves
of this reading meet: the bytes counted in the first half are what fills that queue.
Write-through's extra traffic is invisible in latency while the write buffer absorbs
it and the bus has headroom, and it stops being invisible the moment either runs out —
at which point a policy that was cheaper in bytes on this trace becomes the one
holding up the reads.

Two smaller edges. AMAT is per access, and performance is per instruction: converting
one to the other needs the accesses per instruction, which is where a machine with a
higher miss rate and fewer memory instructions can still win. And write-allocate's
fetch is pure waste when the program is about to overwrite the entire block, which is
common enough — `memset`, a buffer being filled, the initialisation of an array — that
instruction sets provide non-temporal stores to skip it.

## What you are about to build

The lab *Write policy, byte for byte* is one `Cache` class with both policies and four
counters — `hits`, `misses`, `bytes_in`, `bytes_out` — plus a `flush` that writes back
what is still dirty when the trace ends, and `amat` and `amat2` taken straight from the
derivation. Its checks are the numbers above and two more worth previewing: a
write-only trace where no read ever allocates, so a write-through cache holds nothing,
hits nothing and moves 4096 bytes against write-back's 2048; and a thrashing sweep
where 40 of the 80 evictions are dirty, which is 2560 bytes out during the run and 512
more at the flush. Get the dirty bookkeeping right and both fall out; get it wrong and
only the second one tells you.
''',
                },
            ],
            "sandbox": {
                "title": "Turning a miss rate into cycles",
                "visualiser": "cache",
                "minutes": 8,
                "initial": {"kb": 16, "ways": 2, "stride": 8},
                "brief": r'''
Same plot, now read as an input to an arithmetic problem rather than as a result.
Take a 1-cycle hit and a 100-cycle miss penalty, and convert each height you see
into an average access time.
''',
                "notice": [
                    "At a stride of 8 B the curve sits at 12.5 per cent, and it opens at 16 KB. That is $1 + 0.125 \\times 100 = 13.5$ cycles per access: thirteen and a half times what the same access would cost if it hit.",
                    "Halve the stride to 4 B and the curve halves to 6.25, giving $1 + 0.0625 \\times 100 = 7.25$ cycles. Halving the miss rate nearly halved the access time, because at these numbers the penalty term is almost the whole of it.",
                    "Now drag the size slider from 1 KB to 16 KB at either stride. The curve does not move, so neither does the AMAT: on that stretch no amount of capacity buys a single cycle. Then keep going. At 32 KB the 8 B curve drops to 4.17 per cent — $1 + 0.0417 \\times 100 = 5.17$ cycles, saving 8.3 cycles per access — and the 4 B curve drops to 2.08, giving 3.08. The 32 KB walk has just fitted, and every capacity beyond that is wasted silicon.",
                    "Both of those cliffs land on the same figure the compulsory floor predicts: one miss per 64-byte line, spread over three passes. At a 4 B stride that is $512 / (8192 \\times 3) = 2.08$ per cent. AMAT is only ever as honest as the miss rate you feed it, and the miss rate is only as honest as the size you measured it at — quoting either without the other is how a cache that helps enormously and one that helps not at all come to look identical on a slide.",
                ],
            },
            "derive": {
                "title": "AMAT, global miss rates and bytes moved",
                "minutes": 15,
                "vars": ["t_1", "t_2", "t_m", "m_1", "m_2", "m", "B", "V", "w", "d"],
                "brief": r'''
An L1 with hit time $t_1$ and miss rate $m_1$ sits in front of an L2 with access
time $t_2$ and its own local miss rate $m_2$; memory answers in $t_m$. Blocks are
$B$ bytes and a word is $V$ bytes.
''',
                "steps": [
                    {
                        "prompt": "With no L2 at all, write the average memory access time in terms of $t_1$, $m_1$ and $t_m$.",
                        "answer": "t_1 + m_1 \\cdot t_m",
                        "hint": "You pay the hit time on every access, and the memory time on the fraction that miss.",
                        "deconstruct": [
                            "Every access costs $t_1$ whether it hits or not — the tag check happens regardless.",
                            "A fraction $m_1$ then also waits $t_m$.",
                        ],
                    },
                    {
                        "prompt": "Now insert the L2. Write the average access time in terms of $t_1$, $m_1$, $t_2$, $m_2$ and $t_m$.",
                        "answer": "t_1 + m_1 \\cdot \\left( t_2 + m_2 \\cdot t_m \\right)",
                        "hint": "The L1 miss penalty is no longer $t_m$; it is the L2's own average access time.",
                        "deconstruct": [
                            "Replace $t_m$ in the previous answer by whatever an L1 miss actually costs.",
                            "An L1 miss reaches the L2, which costs $t_2$, and misses in turn with probability $m_2$.",
                        ],
                    },
                    {
                        "prompt": "Write the L2 global miss rate — the fraction of *all* processor accesses that reach memory — in terms of $m_1$ and $m_2$.",
                        "answer": "m_1 \\cdot m_2",
                        "hint": "$m_2$ is measured against accesses that got past the L1, not against all of them.",
                        "deconstruct": [
                            "A fraction $m_1$ of accesses reach the L2 at all.",
                            "Of those, a fraction $m_2$ go further, so the product is the share of all accesses.",
                        ],
                    },
                    {
                        "prompt": "A write-back, write-allocate cache misses at rate $m$, and a fraction $d$ of the blocks it evicts are dirty. Write the bytes moved to and from memory per access.",
                        "answer": "m \\cdot B \\cdot \\left( 1 + d \\right)",
                        "hint": "A miss always fetches a block; it additionally writes a block out when the victim was dirty.",
                        "deconstruct": [
                            "Per miss: $B$ bytes in, always, because the policy allocates on writes as well as reads.",
                            "Plus $B$ bytes out with probability $d$, so $B(1+d)$ per miss and $mB(1+d)$ per access.",
                        ],
                    },
                    {
                        "prompt": "Now a write-through, no-write-allocate cache. A fraction $w$ of accesses are writes and each sends $V$ bytes straight to memory; reads miss at rate $m$ and fetch a block. Write the bytes per access.",
                        "answer": "\\left( 1 - w \\right) \\cdot m \\cdot B + w \\cdot V",
                        "hint": "Two independent contributions: the reads that miss, and every single write.",
                        "deconstruct": [
                            "A fraction $1-w$ of accesses are reads; of those, $m$ fetch $B$ bytes.",
                            "Every write, hit or miss, sends $V$ bytes onward, and a write miss allocates nothing.",
                        ],
                    },
                ],
                "closing": r'''
The break-even between the two is a statement about reuse, and it comes out cleanest
one block at a time. Write-back brings a block in and, if it was written at all, puts
it back: $2B$ bytes. Write-through brings it in on the read that first touches it and
then sends $V$ bytes for each of $k$ writes: $B + kV$. So write-back is the cheaper of
the two exactly once $k$ exceeds $B/V$ — with 64-byte blocks and 8-byte words, eight
writes per block. Easy for a stack or an array being filled, impossible for a scatter.
''',
            },
            "quiz": {
                "title": "From a miss rate to cycles, and to bytes",
                "minutes": 7,
                "questions": [
                    {
                        "q": "L1 hits in 1 cycle with a 5% miss rate. L2 takes 12 cycles and misses 20% of the time it is reached. Memory costs 200 cycles. What is the AMAT?",
                        "opts": ["3.6 cycles", "2.6 cycles", "11.6 cycles", "1.6 cycles"],
                        "a": 0,
                        "why": r"""
Compose the levels: the L1 penalty is the whole L2 experience,
$12 + 0.20 \times 200 = 52$ cycles. Then
$\text{AMAT} = 1 + 0.05 \times 52 = 3.6$. Note how heavily the memory term dominates
despite being reached on only 1% of accesses — 40 of those 52 cycles are memory. That is
the shape of every memory hierarchy calculation: rare events with enormous penalties.
""",
                    },
                    {
                        "q": "With those numbers, what is L2's *global* miss rate?",
                        "opts": ["1%", "20%", "25%", "5%"],
                        "a": 0,
                        "why": r"""
$0.05 \times 0.20 = 0.01$. The local rate, 20%, is measured against the accesses that
reach L2; the global rate is measured against all accesses the processor makes. Local
rates always look alarming at the lower levels because L1 has already filtered out
everything easy — quoting one without saying which is the most common way to make a
memory system sound worse or better than it is.
""",
                    },
                    {
                        "q": "What distinguishes write-back from write-through in bus traffic?",
                        "opts": [
                            "Write-back moves a block only when a dirty one is evicted",
                            "Write-back never writes to memory",
                            "Write-through generates less traffic",
                            "They generate identical traffic",
                        ],
                        "a": 0,
                        "why": r"""
Write-through sends every store to the next level; write-back absorbs repeated stores to
the same block and pays once, at eviction, for the whole block. For code that writes the
same cache line several times — which is most code — that is a large reduction. The price
is complexity: a dirty bit per block, a writeback buffer, and a coherence protocol that
has to know some other cache may hold the only current copy.
""",
                    },
                    {
                        "q": "What does write-allocate do on a write miss?",
                        "opts": [
                            "Fetches the block into the cache first, then writes into it",
                            "Writes straight to memory and leaves the cache alone",
                            "Allocates a block without fetching it",
                            "Stalls until the block is evicted",
                        ],
                        "a": 0,
                        "why": r"""
Fetch first, then write — which pairs naturally with write-back, since the block has to
be present for later stores to be absorbed. It looks wasteful when the program is about
to overwrite the entire block, and that case is real enough that architectures provide
non-temporal stores to bypass it. No-write-allocate pairs with write-through instead, and
the two pairings are what you almost always see.
""",
                    },
                    {
                        "q": "Which single change to a two-level hierarchy usually helps AMAT most?",
                        "opts": [
                            "Reducing the L1 miss rate, because it multiplies the entire lower hierarchy",
                            "Reducing the L2 hit time",
                            "Reducing the L1 hit time",
                            "Increasing the block size everywhere",
                        ],
                        "a": 0,
                        "why": r"""
The L1 miss rate multiplies everything below it — in the numbers above, halving it from
5% to 2.5% takes the AMAT from 3.6 to 2.3 cycles, which nothing else on the list comes
close to. The L1 hit time is paid on every access and so it matters too, but it is
already one cycle and there is nowhere for it to go. Being able to see which term
dominates, rather than optimising the one that is easiest to change, is what the formula
is for.
""",
                    },
                ],
            },
            "lab": {
                "title": "Write policy, byte for byte",
                "runtime": "python",
                "minutes": 44,
                "brief": r'''
One cache class, two policies, and an exact byte count for each.

`Cache(capacity_bytes, block_bytes, ways, policy, word_bytes=4)` where `policy` is
either `"wb"` or `"wt"`.

**`"wb"` — write-back, write-allocate.** A read miss fetches a block. A write miss
fetches a block too, then marks it dirty. A write hit marks the resident block
dirty. Evicting a dirty block writes `block_bytes` out.

**`"wt"` — write-through, no-write-allocate.** Reads behave the same. Every write,
hit or miss, sends `word_bytes` to memory immediately. A write miss allocates
nothing and fetches nothing, so a block only ever arrives because of a read. No
block is ever dirty.

Keep four counters: `hits`, `misses`, `bytes_in` (fetched from memory) and
`bytes_out` (sent to memory). `flush()` writes back everything still dirty, adds it
to `bytes_out`, and returns the number of bytes it moved.

Also write `amat(t_hit, miss_rate, t_penalty)` and
`amat2(t_1, m_1, t_2, m_2, t_m)`, straight from the derivation.
''',
                "files": [
                    {"name": "traces.py", "ro": True, "content": r'''
"""Deterministic read/write traces. Read only.

Every trace is a list of `(op, addr)` pairs, `op` being either "r" or "w".
"""


def rw_walk(start, stride, count, passes=1, write_every=0):
    """Sweep `count` addresses `passes` times, writing every `write_every`-th access.

    `write_every=0` means a read-only trace; `write_every=1` means every access is
    a write.
    """
    out = []
    k = 0
    for _ in range(passes):
        for i in range(count):
            op = "w" if write_every and (k % write_every == 0) else "r"
            out.append((op, start + i * stride))
            k += 1
    return out
'''},
                    {"name": "main.py", "content": r'''
import numpy as np
from traces import rw_walk


class Cache:
    """Write-back write-allocate ("wb") or write-through no-write-allocate ("wt")."""

    def __init__(self, capacity_bytes, block_bytes, ways, policy, word_bytes=4):
        self.block_bytes = block_bytes
        self.ways = ways
        self.policy = policy
        self.word_bytes = word_bytes
        self.sets = capacity_bytes // (block_bytes * ways)
        self.tags = [[] for _ in range(self.sets)]
        self.dirty = [set() for _ in range(self.sets)]
        self.hits = 0
        self.misses = 0
        self.bytes_in = 0
        self.bytes_out = 0

    def _index(self, addr):
        return (addr // self.block_bytes) % self.sets

    def _tag(self, addr):
        return (addr // self.block_bytes) // self.sets

    def _install(self, addr, dirty):
        """Fetch a block into its set, evicting LRU and writing it back if dirty."""
        # TODO: bytes_in grows by one block; a dirty victim grows bytes_out.
        pass

    def read(self, addr):
        """Return True on a hit. A read miss always allocates."""
        # TODO
        return False

    def write(self, addr):
        """Return True on a hit. Behaviour depends on self.policy."""
        # TODO
        return False

    def run(self, trace):
        for op, addr in trace:
            if op == "w":
                self.write(addr)
            else:
                self.read(addr)
        return self.hits, self.misses

    def flush(self):
        """Write every dirty block back. Return the bytes moved."""
        # TODO
        return 0


def amat(t_hit, miss_rate, t_penalty):
    """One level."""
    # TODO
    return 0.0


def amat2(t_1, m_1, t_2, m_2, t_m):
    """Two levels, with m_2 local to the L2."""
    # TODO
    return 0.0


if __name__ == "__main__":
    trace = rw_walk(0, 4, 256, passes=2, write_every=4)
    for policy in ("wb", "wt"):
        c = Cache(1024, 64, 2, policy)
        c.run(trace)
        left = c.flush()
        print(policy, "hits", c.hits, "misses", c.misses,
              "in", c.bytes_in, "out", c.bytes_out, "(flush moved", left, ")")
    print("amat:", np.round([amat(1.0, 0.05, 100.0),
                             amat2(1.0, 0.05, 12.0, 0.4, 200.0)], 4).tolist())
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np
from traces import rw_walk


class Cache:
    """Write-back write-allocate ("wb") or write-through no-write-allocate ("wt")."""

    def __init__(self, capacity_bytes, block_bytes, ways, policy, word_bytes=4):
        self.block_bytes = block_bytes
        self.ways = ways
        self.policy = policy
        self.word_bytes = word_bytes
        self.sets = capacity_bytes // (block_bytes * ways)
        self.tags = [[] for _ in range(self.sets)]
        self.dirty = [set() for _ in range(self.sets)]
        self.hits = 0
        self.misses = 0
        self.bytes_in = 0
        self.bytes_out = 0

    def _index(self, addr):
        return (addr // self.block_bytes) % self.sets

    def _tag(self, addr):
        return (addr // self.block_bytes) // self.sets

    def _install(self, addr, dirty):
        """Fetch a block into its set, evicting LRU and writing it back if dirty."""
        i, t = self._index(addr), self._tag(addr)
        s, d = self.tags[i], self.dirty[i]
        self.bytes_in += self.block_bytes
        s.append(t)
        if dirty:
            d.add(t)
        if len(s) > self.ways:
            victim = s.pop(0)
            if victim in d:
                d.discard(victim)
                self.bytes_out += self.block_bytes

    def read(self, addr):
        """Return True on a hit. A read miss always allocates."""
        i, t = self._index(addr), self._tag(addr)
        s = self.tags[i]
        if t in s:
            s.remove(t)
            s.append(t)
            self.hits += 1
            return True
        self.misses += 1
        self._install(addr, False)
        return False

    def write(self, addr):
        """Return True on a hit. Behaviour depends on self.policy."""
        i, t = self._index(addr), self._tag(addr)
        s, d = self.tags[i], self.dirty[i]
        if self.policy == "wt":
            self.bytes_out += self.word_bytes
            if t in s:
                s.remove(t)
                s.append(t)
                self.hits += 1
                return True
            self.misses += 1
            return False
        if t in s:
            s.remove(t)
            s.append(t)
            d.add(t)
            self.hits += 1
            return True
        self.misses += 1
        self._install(addr, True)
        return False

    def run(self, trace):
        for op, addr in trace:
            if op == "w":
                self.write(addr)
            else:
                self.read(addr)
        return self.hits, self.misses

    def flush(self):
        """Write every dirty block back. Return the bytes moved."""
        moved = 0
        for i in range(self.sets):
            moved += self.block_bytes * len(self.dirty[i])
            self.dirty[i].clear()
        self.bytes_out += moved
        return moved


def amat(t_hit, miss_rate, t_penalty):
    """One level."""
    return t_hit + miss_rate * t_penalty


def amat2(t_1, m_1, t_2, m_2, t_m):
    """Two levels, with m_2 local to the L2."""
    return t_1 + m_1 * (t_2 + m_2 * t_m)


if __name__ == "__main__":
    trace = rw_walk(0, 4, 256, passes=2, write_every=4)
    for policy in ("wb", "wt"):
        c = Cache(1024, 64, 2, policy)
        c.run(trace)
        left = c.flush()
        print(policy, "hits", c.hits, "misses", c.misses,
              "in", c.bytes_in, "out", c.bytes_out, "(flush moved", left, ")")
    print("amat:", np.round([amat(1.0, 0.05, 100.0),
                             amat2(1.0, 0.05, 12.0, 0.4, 200.0)], 4).tolist())
'''}],
                "hints": [
                    "Keep the dirty set per set index and keyed by tag, so an eviction can ask `victim in d` in one step.",
                    "In `\"wt\"`, add `word_bytes` to `bytes_out` before you decide whether the access hit — the write goes to memory either way.",
                    "A write miss under `\"wt\"` must not call `_install`: no fetch, no allocation, and `bytes_in` untouched.",
                ],
                "tests": [
                    {"name": "on a read-only trace the two policies are identical", "code": r'''
_t = rw_walk(0, 4, 256, passes=2)
_a = Cache(1024, 64, 2, "wb")
_a.run(_t)
_b = Cache(1024, 64, 2, "wt")
_b.run(_t)
assert (_a.hits, _a.misses) == (496, 16), \
    f"16 blocks fetched once, 496 hits after that; got {_a.hits}, {_a.misses}"
assert (_b.hits, _b.misses) == (496, 16), \
    f"with no writes the policy cannot matter; got {_b.hits}, {_b.misses}"
assert _a.bytes_in == _b.bytes_in == 1024, \
    f"16 blocks of 64 B is 1024 bytes in; got {_a.bytes_in} and {_b.bytes_in}"
assert _a.bytes_out == 0 and _b.bytes_out == 0, \
    f"nothing was written, so nothing goes back; got {_a.bytes_out} and {_b.bytes_out}"
'''},
                    {"name": "write-back defers its traffic to the eviction", "code": r'''
_t = rw_walk(0, 4, 256, passes=2, write_every=4)
_c = Cache(1024, 64, 2, "wb")
_c.run(_t)
assert (_c.hits, _c.misses) == (496, 16), \
    f"write-allocate means a write miss brings the block in, as a read would; got {_c.hits}, {_c.misses}"
assert _c.bytes_in == 1024, f"still 16 blocks fetched; got {_c.bytes_in}"
assert _c.bytes_out == 0, \
    f"the working set fits, so nothing was evicted and nothing left the cache yet; got {_c.bytes_out}"
assert _c.flush() == 1024, "all 16 blocks were written to, so all 16 are dirty at the end"
assert _c.bytes_out == 1024, f"flush must add its bytes to the counter; got {_c.bytes_out}"
'''},
                    {"name": "write-through pays per write and allocates nothing", "code": r'''
_t = rw_walk(0, 4, 256, passes=2, write_every=4)
_c = Cache(1024, 64, 2, "wt")
_c.run(_t)
assert _c.misses == 32, \
    (f"each block misses twice in the first pass — once on the write that does not "
     f"allocate, once on the read that does; got {_c.misses}")
assert _c.hits == 480, f"expected 480 hits, got {_c.hits}"
assert _c.bytes_out == 512, \
    f"128 writes of 4 bytes each go straight out; got {_c.bytes_out}"
assert _c.flush() == 0, "a write-through cache never holds a dirty block"
'''},
                    {"name": "a write-only trace makes a write-through cache useless", "code": r'''
_t = rw_walk(0, 4, 256, passes=4, write_every=1)
_wt = Cache(1024, 64, 2, "wt")
_wt.run(_t)
assert (_wt.hits, _wt.misses) == (0, 1024), \
    (f"no read ever allocates, so no block is ever resident and every one of the "
     f"1024 writes misses; got {_wt.hits}, {_wt.misses}")
assert _wt.bytes_in == 0 and _wt.bytes_out == 4096, \
    f"nothing fetched, 1024 words of 4 bytes out; got {_wt.bytes_in}, {_wt.bytes_out}"
_wb = Cache(1024, 64, 2, "wb")
_wb.run(_t)
assert (_wb.hits, _wb.misses) == (1008, 16), f"got {_wb.hits}, {_wb.misses}"
assert _wb.bytes_in + _wb.bytes_out + _wb.flush() == 2048, \
    "write-back moves each block in once and out once: 2048 bytes against 4096"
'''},
                    {"name": "a thrashing write-back cache writes back during the run", "code": r'''
_t = rw_walk(0, 64, 32, passes=3, write_every=2)
_c = Cache(1024, 64, 2, "wb")
_c.run(_t)
assert (_c.hits, _c.misses) == (0, 96), \
    f"a 2 KB cyclic sweep through a 1 KB cache hits nothing; got {_c.hits}, {_c.misses}"
assert _c.bytes_in == 6144, f"96 misses fetch 96 blocks; got {_c.bytes_in}"
assert _c.bytes_out == 2560, \
    (f"of the 80 blocks evicted during the run, 40 had been written to and had to "
     f"go back: 40 * 64 = 2560. Got {_c.bytes_out}")
_left = _c.flush()
assert _left == 512, \
    f"8 dirty blocks are still resident when the trace ends; got a flush of {_left}"
'''},
                    {"name": "AMAT composes across levels", "code": r'''
import numpy as np
assert np.isclose(amat(1.0, 0.05, 100.0), 6.0), \
    f"1 + 0.05*100 = 6.0, got {amat(1.0, 0.05, 100.0)}"
assert np.isclose(amat2(1.0, 0.05, 12.0, 0.4, 200.0), 5.6), \
    (f"1 + 0.05*(12 + 0.4*200) = 5.6; got {amat2(1.0, 0.05, 12.0, 0.4, 200.0)}")
assert np.isclose(amat2(1.0, 0.05, 12.0, 0.4, 200.0),
                  amat(1.0, 0.05, amat(12.0, 0.4, 200.0))), \
    "the L1 penalty is exactly the L2's own average access time — the two must agree"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "MESI across two caches",
            "summary": "Two private caches, one address. The protocol decides who may write, and every decision costs a bus transaction.",
            "concepts": [
                "The four states: Modified (mine and dirty), Exclusive (mine and clean), Shared (readable, possibly elsewhere), Invalid.",
                "Three requests on the bus: BusRd for a read miss, BusRdX for a write miss, BusUpgr for a write to a block already held Shared.",
                "E exists to save exactly one transaction: the first write to a block nobody else has costs nothing on the bus.",
                "A snooping cache holding Modified data must supply it and downgrade itself, so a remote read turns into a flush plus a state change.",
                "False sharing: two cores writing different words of one block invalidate each other every time, and the protocol cannot tell the difference.",
            ],
            "read": [
                {
                    "title": "Two counters, four bytes apart",
                    "minutes": 17,
                    "body": r'''
Two cores, one counter each, incremented alternately. In the first version the
counters are neighbouring words of a struct, at addresses 0 and 4. In the second
someone has moved them a cache block apart, to 0 and 64. Neither core ever touches
the other's counter; there is no lock, no shared variable, and nothing in the source
of either version that a reviewer would call communication. Run eight increments of
each version through two private caches on a snooping bus.

```python
BLOCK = 64


class Mesi:
    """Two private caches, one snooping bus. Nothing is evicted here."""

    def __init__(self):
        self.state = [{}, {}]
        self.bus = {"BusRd": 0, "BusRdX": 0, "BusUpgr": 0, "Flush": 0}
        self.hits = self.misses = 0

    def st(self, core, addr):
        return self.state[core].get(addr // BLOCK, "I")

    def read(self, core, addr):
        b, other = addr // BLOCK, 1 - core
        if self.st(core, addr) != "I":
            self.hits += 1
            return "hit"
        self.misses += 1
        self.bus["BusRd"] += 1
        remote = self.state[other].get(b, "I")
        if remote == "I":
            self.state[core][b] = "E"
            return "BusRd -> E"
        if remote == "M":
            self.bus["Flush"] += 1
        self.state[other][b] = "S"
        self.state[core][b] = "S"
        return "BusRd -> S"

    def write(self, core, addr):
        b, other = addr // BLOCK, 1 - core
        here = self.st(core, addr)
        if here in ("M", "E"):
            self.hits += 1
            self.state[core][b] = "M"
            return "silent" if here == "E" else "hit"
        if here == "S":
            self.hits += 1
            self.bus["BusUpgr"] += 1
            self.state[other].pop(b, None)
            self.state[core][b] = "M"
            return "BusUpgr"
        self.misses += 1
        self.bus["BusRdX"] += 1
        if self.state[other].get(b, "I") == "M":
            self.bus["Flush"] += 1
        self.state[other].pop(b, None)
        self.state[core][b] = "M"
        return "BusRdX"


def run(work):
    s = Mesi()
    for core, op, addr in work:
        (s.write if op == "w" else s.read)(core, addr)
    return s


false_sharing = [(c, "w", c * 4) for _ in range(4) for c in (0, 1)]
padded = [(c, "w", c * 64) for _ in range(4) for c in (0, 1)]
disjoint = [(c, "w", (c * 2 + i) * 64) for _ in range(4) for c in (0, 1) for i in (0, 1)]

for name, work in (("false sharing", false_sharing), ("padded", padded),
                   ("disjoint", disjoint)):
    s = run(work)
    print("%-14s %2d accesses, %2d hits, %2d misses, %s"
          % (name, len(work), s.hits, s.misses,
             {k: v for k, v in s.bus.items() if v}))
```

Four bytes apart: not one hit in eight accesses, eight bus transactions carrying data,
and seven flushes of dirty data from one cache to the other. Sixty-four bytes apart:
six hits, two cold misses, and the bus goes quiet after the first two accesses. The
program is identical. The difference is which block each address falls in.

## The unit of ownership is the block

Coherence hardware tracks state per block, because a tag is per block and there is
nowhere else to put the state. The derivation *What a shared line costs* opens on the
count that follows: a 64-byte block at 4 bytes to the word covers $B/V = 16$
independently addressable words, and one coherence decision covers all sixteen. When
core 1 takes the block for writing, the protocol is not asked, and cannot answer,
which word it wants. Core 0's copy goes Invalid whether or not it held anything core 1
intends to touch.

That is why the phenomenon is called *false* sharing: it is not sharing, it is a
block-granularity approximation to sharing, and the approximation is conservative in
the only direction it can safely be.

## Four states, and why exactly four

Rather than take the state names on trust, work out what a cache has to know about a
block it holds. Three independent questions:

- May I read it? Failing that, the block is not usable at all.
- May I write it without telling anyone? That is allowed only if no other cache can
  possibly hold a copy.
- Do I owe memory a copy? That is, has it been written since it was fetched?

Not present at all is one state: **Invalid**. Present, possibly held elsewhere, so
readable but not silently writable, and necessarily clean because a dirty block cannot
be shared under this design: **Shared**. Present, held by nobody else, clean:
**Exclusive**. Present, held by nobody else, dirty: **Modified**. The fourth
combination — present, shared, and dirty — is the one the design rules out, and that
is a decision rather than a law. MOESI puts it back and calls it Owned, precisely to
avoid the write-back that a shared dirty block would otherwise force.

Three requests carry the transitions, and each exists because the others would be
wasteful. BusRd asks for a readable copy. BusRdX asks for data *and* exclusivity, for
a write to a block that is not present. BusUpgr asks for exclusivity *only*, for a
write to a block already held Shared, where the data is in hand and only the
permission is missing.

## The ping-pong, one access at a time

Two cores taking turns to read and then write the same word is the worst case that is
still a legitimate program — a shared counter, a work-stealing index, a spin lock.
Watch every access.

```text
   1  core 0 r  BusRd -> E   core0=E core1=I
   2  core 0 w  silent       core0=M core1=I
   3  core 1 r  BusRd -> S   core0=S core1=S
   4  core 1 w  BusUpgr      core0=I core1=M
   5  core 0 r  BusRd -> S   core0=S core1=S
   6  core 0 w  BusUpgr      core0=M core1=I
   7  core 1 r  BusRd -> S   core0=S core1=S
   8  core 1 w  BusUpgr      core0=I core1=M
   ...
  totals: 8 hits 8 misses {'BusRd': 8, 'BusUpgr': 7, 'Flush': 7}
```

Step 1 is a read miss with no responder on the bus, so the block arrives Exclusive —
the cache has learned from *silence* that it is the only holder. Step 2 is the payoff:
a write to an Exclusive block changes E to M in the tag array and puts nothing on the
bus at all. Step 3 is core 1's read; core 0 is holding modified data, so it must supply
it and demote itself, which is the Flush, and both ends settle in Shared. Step 4 is
core 1's write from Shared: the data is already there, so it sends a BusUpgr, core 0
goes Invalid, and the cycle repeats from step 5.

Steady state is three bus transactions for every two accesses, and eight hits out of
sixteen — where the "hits" are the writes, each of which hit in the tag array while
serialising the two cores against each other. Note the totals: seven BusUpgr for eight
writes. The missing eighth is step 2, and it is the entire contribution of the E state.

## What Exclusive is worth

One transaction on this trace. That sounds like a rounding error until you run a
pattern that is not pathological.

```python
BLOCK = 64


def bus_traffic(work, with_E):
    """Count bus transactions. with_E=False is MSI: a clean read miss lands in S."""
    state = [{}, {}]
    bus = 0
    for core, op, addr in work:
        b, other = addr // BLOCK, 1 - core
        here = state[core].get(b, "I")
        remote = state[other].get(b, "I")
        if op == "r":
            if here != "I":
                continue                       # read hit, nothing on the bus
            bus += 1                           # BusRd
            if remote == "I":
                state[core][b] = "E" if with_E else "S"
            else:
                if remote == "M":
                    bus += 1                   # Flush
                state[other][b] = "S"
                state[core][b] = "S"
        else:
            if here in ("M", "E"):
                state[core][b] = "M"           # silent, and only E can be silent
                continue
            bus += 1                           # BusUpgr from S, BusRdX from I
            if here == "I" and remote == "M":
                bus += 1                       # Flush
            state[other].pop(b, None)
            state[core][b] = "M"
    return bus


ping_pong = [(c, o, 0) for _ in range(4) for c in (0, 1) for o in ("r", "w")]
private = [(c, o, (c * 2 + i) * BLOCK)
           for _ in range(3) for c in (0, 1) for i in (0, 1) for o in ("r", "w")]

for name, work in (("ping-pong", ping_pong), ("private read-then-write", private)):
    mesi, msi = bus_traffic(work, True), bus_traffic(work, False)
    print("%-24s %2d accesses: MESI %2d transactions, MSI %2d"
          % (name, len(work), mesi, msi))
```

On the contended word, MESI saves one transaction of twenty-three. On a private
read-then-write — each core loading and updating its own data, which is what most code
spends most of its time doing — MESI needs four transactions and MSI needs eight.
Half the bus traffic, from one state whose only job is to remember that nobody
answered.

## The mistake: sending BusRdX from Shared

A write needs exclusivity; BusRdX is how a write asks for exclusivity; a write to a
Shared block therefore sends BusRdX. Every step of that is defensible, and it
collapses the two write-miss paths into one branch, which makes the state machine
shorter and is the form the code wants to take.

It is also correct, in the sense that the protocol still never lets two caches write
the same block. What it costs is a block of data crossing the bus for no reason at all,
because the cache issuing the request already has that data — it is holding it in
Shared. On the ping-pong trace that is seven redundant block transfers, 448 bytes on
top of the 448 the flushes already move: the traffic on the most contended resource in
the machine, doubled, to save a branch. BusUpgr exists for that single case and does
nothing else.

There is a second error waiting immediately behind it, and the capstone brief flags it
because it is worth flagging: a BusUpgr is a **hit**. The data was present and the
access was satisfied from the cache; only the permission had to be acquired. Score it
as a miss and the miss rate starts to depend on the coherence protocol rather than on
the cache, and every false-sharing and producer-consumer measurement you take
afterwards is wrong in a way that looks plausible.

## Where the model stops holding

MESI guarantees **coherence**: every read of a given address returns the value of the
last write to that address, in a single agreed order. It says nothing whatever about
the order of operations on *different* addresses, and that is a separate property
called consistency. A core with a store buffer can retire its own store locally and
let a later load of a different address complete before the invalidation for the store
has been acknowledged — no coherence rule is broken, and two cores can still both
observe the other's variable as unwritten. That gap is exactly why fences and atomic
operations exist, and why a program that is correct under coherence alone can still
fail.

Snooping stops working before the core count gets interesting. Every transaction is a
broadcast, every cache must check every one against its tags, and the bus is the
serialisation point for the whole machine — which is fine for the two caches in this
module's lab and hopeless at sixteen. Directory protocols replace the broadcast with a
per-block list of sharers so a transaction reaches only the caches that hold the block,
and pay for it with an extra hop and a directory to keep somewhere.

The four states are a minimum rather than an optimum. Step 3 of the ping-pong trace
wrote a modified block back to memory to hand a copy to the other core; memory did not
want it and the block is modified again three accesses later. MOESI's Owned state lets
the supplying cache keep the dirty copy and serve it directly, and MESIF designates one
sharer as the forwarder so that several caches holding S do not all answer at once —
an arbitration question that two caches cannot pose.

And the protocol's knowledge of who holds what is deliberately conservative. A cache
that evicts a clean block in S or E does so silently, telling nobody, so a later
BusUpgr may invalidate copies that no longer exist. The bookkeeping is allowed to
overestimate sharing; it is never allowed to underestimate it.

Finally, none of this appears on any uniprocessor measurement. The sandbox *The floor
a single cache cannot get below* ends by asking you to imagine the missing axis: a
block that this cache has not evicted, at an address that has not moved, which misses
because another core wrote it. The three-C decomposition of module 2 cannot produce
that number, because all three of its reference caches are single caches. It is a
fourth C, and the only way to measure it is to model the second cache.

## What you are about to build

The lab *MESI between two snooping caches* asks for the state machine above with
replacement added: `state_of`, `read`, `write`, and an LRU order per core in which
evicting a Modified block costs a Flush. The checks are the transitions this page has
traced — a clean read miss landing in E rather than S, a first write to E costing a
single BusRd in total with no BusUpgr behind it, a second reader forcing a flush and
demoting the owner, a write from S issuing BusUpgr and never BusRdX — and then the
three workloads: ping-pong at 8 BusRd, 7 BusUpgr and 7 Flush, false sharing at 8
BusRdX and 7 Flush with no hits at all, and disjoint at 12 hits and no flushes.

`coherence_amat` comes from the derivation *What a shared line costs*, and its closing
numbers are the reason the whole module exists: at a 1-cycle hit, a 2 per cent local
miss rate, a 200-cycle memory and a 40-cycle snoop, padding the data takes the average
access from 9 cycles to 5. An 80 per cent slowdown, bought by a struct layout, with the
algorithm, the cache size and the local miss rate all unchanged.
''',
                },
            ],
            "quiz": {
                "title": "What a block costs when two caches want it",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Two cores write different words that happen to share one 64-byte block, and each write invalidates the other core's copy. Why can the protocol not let both proceed?",
                        "opts": [
                            "Because a cache tracks state per block, so ownership cannot name a word",
                            "Because writes to any address must be serialised across the whole machine",
                            "Because the two words are in the same set, so one evicts the other",
                            "Because the bus carries whole blocks and cannot transfer a single word",
                        ],
                        "a": 0,
                        "whys": [
                            r"State lives beside the tag, and a tag names a block. The protocol is never told which word a write touched, so it has to invalidate everything the block covers.",
                            r"Coherence serialises writes to *one* address, not to all of them. Two cores writing genuinely separate blocks proceed in parallel with no transaction between them, which is what the padded version of this workload demonstrates.",
                            r"A conflict miss and a coherence miss are different failures. These two words are in the same block, not merely the same set, and the block is resident in both caches until a write takes it away — no eviction happens anywhere.",
                            r"A bus that moved single words would change what a transfer costs and nothing about who is allowed to write. The permission is what is being contested here, and permission is granted per block.",
                        ],
                        "why": r"""
Coherence state is stored with the tag, and a tag identifies a block, so the finest
distinction the protocol can draw is block-sized. A write is a request for the block,
and the request carries no information about which of its sixteen words was wanted.
Everything follows from that: the invalidation is conservative because it must be, the
two cores serialise on data neither of them shares, and the only available fix is to
change the addresses so that the two counters land in different blocks.
""",
                    },
                    {
                        "q": "A read miss goes onto the bus and no other cache responds. The block is installed Exclusive rather than Shared. What is bought by the distinction?",
                        "opts": [
                            "The block can be supplied from this cache without going to memory",
                            "The block is known clean, so evicting it later needs no writeback",
                            "The next write to this block needs no bus transaction at all",
                            "The block will not be invalidated by another core's read",
                        ],
                        "a": 2,
                        "whys": [
                            r"Supplying data to a requester is something a cache in Shared or Modified does too — the state that matters for that is having a copy, not having the only one.",
                            r"True of Exclusive and true of Shared alike, since both are clean, so it cannot be what separates them. The dirty bit is what a writeback turns on, and that is the M in the protocol.",
                            r"Nobody else can hold the block, so there is nobody to invalidate, and the cache moves E to M in its own tag array without asking anyone.",
                            r"Another core's read never invalidates anything — it demotes the holder to Shared and takes a copy. Invalidation comes from a write, and E is no protection against one.",
                        ],
                        "why": r"""
Silence on the bus is information: it proves no other cache holds the block, and
Exclusive is where that proof is stored. The next write can then go ahead with nothing
on the bus, because there is provably nobody to invalidate. MSI, which has no E, has to
issue an upgrade for that same write, and the pattern it pays for — read a private
variable, then update it — is one of the most common in any program. On a private
read-then-write workload MESI needs half the transactions MSI does, all of it from
this one state.
""",
                    },
                    {
                        "q": "A core writes to a block it already holds in Shared. What does issuing BusRdX instead of BusUpgr cost, and does it break anything?",
                        "opts": [
                            "It transfers a block that is already resident; correctness is unaffected",
                            "It leaves the other copies valid, so two caches could then write",
                            "It forces a writeback of memory's copy; correctness is unaffected",
                            "It costs nothing at all, since both requests carry exactly the same message",
                        ],
                        "a": 0,
                        "whys": [
                            r"BusRdX asks for data and exclusivity; the exclusivity is needed and the data is already in hand, so the transfer is redundant traffic on the most contended resource in the machine.",
                            r"BusRdX invalidates other copies exactly as BusUpgr does — that is the X in its name. The protocol stays correct, which is precisely why this mistake survives testing.",
                            r"Memory's copy is not touched by either request. A writeback happens when a cache holding Modified data has to give it up, and no cache here holds this block modified.",
                            r"They differ in one respect that matters on a bus: BusUpgr asks for permission alone and moves no data, while BusRdX moves a whole block. On the ping-pong trace that is 448 redundant bytes.",
                        ],
                        "why": r"""
Both requests invalidate the other copies, so a protocol built entirely on BusRdX is
correct, which is what makes the shortcut tempting — it collapses two write paths into
one branch and no test fails. What it spends is bandwidth: the requester already holds
the data, so the block that comes back is a copy of what is in its own array. On the
ping-pong trace, seven upgrades become seven block transfers, 448 bytes on top of the
448 the flushes already move. BusUpgr exists for this single case.
""",
                    },
                    {
                        "q": "In a run over two cores, should a write that hits a Shared block and issues a BusUpgr be counted as a hit or a miss?",
                        "opts": [
                            "A miss, because issuing a bus transaction is what a miss is defined by",
                            "A hit, because the data was resident and only permission was missing",
                            "A miss, because the block was invalidated in the other cache",
                            "Neither, since an upgrade is a coherence event and not an access",
                        ],
                        "a": 1,
                        "whys": [
                            r"Bus traffic and hit-or-miss are separate questions. A miss is an access the cache could not satisfy from its own array, and this one it could — tying the label to the bus makes the miss rate a property of the protocol rather than of the cache.",
                            r"The block was in the array and the word was read out of it; what had to be acquired was the right to modify it, which is a permission and not data.",
                            r"What happened in the *other* cache classifies that cache's next access, not this one. The remote copy going Invalid is what makes the remote core's following access a coherence miss.",
                            r"Every access the core makes is either satisfied by the cache or not, and this one was, so leaving it out of both counts loses accesses and makes the rates not add up.",
                        ],
                        "why": r"""
A hit, and the capstone brief warns about it because the wrong answer is stable and
plausible. The data was present, the access was served from the array, and the bus
transaction bought permission rather than bytes. Counting it as a miss makes the miss
rate depend on which protocol the machine runs — the same code on MSI and MESI would
report different miss rates for identical cache behaviour — and it corrupts the
false-sharing and producer-consumer measurements in a direction that looks reasonable
until you compare them with the bus counts.
""",
                    },
                    {
                        "q": "A run has a 1-cycle hit, a 2 per cent local miss rate to a 200-cycle memory, and 10 per cent of accesses served by the other cache at 40 cycles. Padding the data to remove the sharing gives what?",
                        "opts": [
                            "9 cycles falling to 5, since the snoop term goes to zero",
                            "9 cycles falling to 1, since both miss terms go to zero",
                            "5 cycles rising to 9, since padding costs extra capacity misses",
                            "9 cycles unchanged, since the same data is fetched either way",
                        ],
                        "a": 0,
                        "whys": [
                            r"$1 + 0.02 \times 200 + 0.10 \times 40 = 9$, and removing the sharing removes the third term alone: the local miss rate is untouched by where the data sits.",
                            r"Padding does not remove the local misses — the data still has to be fetched the first time and re-fetched when it is evicted. Only the misses caused by another core's writes disappear.",
                            r"Backwards on the direction, though the concern is real: padding does waste space and can raise the local miss rate. Here it is the shared version that costs 9 cycles and the padded one that costs 5.",
                            r"The same bytes are fetched, but not the same number of times. A block taken away by a remote write has to be fetched again, and that refetch is the entire third term of the expression.",
                        ],
                        "why": r"""
The access time is $t_1 + m\,t_m + f\,t_s$, so $1 + 0.02 \times 200 + 0.10 \times 40 = 9$
cycles. Padding drives $f$ to zero and leaves $m$ where it was, giving 5. That is an 80
per cent slowdown attributable to a data layout, at an unchanged algorithm, cache size
and local miss rate — which is why a profiler that reports only the local miss rate can
show two versions of a program as identical while one of them runs at half the speed.
""",
                    },
                    {
                        "q": "MESI is running correctly on every cache in a machine. Which guarantee does that still not provide?",
                        "opts": [
                            "That two caches never hold the same block in Modified at once",
                            "That a read returns the value of the last write to that address",
                            "That a write to a block held Shared invalidates every other copy of it",
                            "That one core's two writes to different addresses are seen in order",
                        ],
                        "a": 3,
                        "whys": [
                            r"That is coherence's central invariant and the protocol enforces it: a transition into Modified invalidates every other copy first, so a second writer cannot exist.",
                            r"This is what coherence means for a single address, and MESI delivers it — writes to one block are serialised by the bus into a single order that every cache observes.",
                            r"BusUpgr and BusRdX both invalidate the remote copies before the write proceeds, which is the mechanism by which the guarantee above is kept.",
                            r"Coherence orders the accesses to each address separately and says nothing about how two addresses interleave. A store buffer can retire one write locally while the other is still in flight, and no coherence rule is broken.",
                        ],
                        "why": r"""
Coherence is a per-address property: every read of an address sees the last write to
that address, in one order all caches agree on. Consistency is the property that
relates *different* addresses, and MESI does not address it at all. A core with a store
buffer can complete a later operation before an earlier store has been made visible,
so two cores can each observe the other's flag as unset — with every cache perfectly
coherent throughout. Fences and atomic instructions exist to constrain that ordering,
and no amount of correctness in the coherence protocol removes the need for them.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "The floor a single cache cannot get below",
                "visualiser": "cache",
                "minutes": 8,
                "initial": {"kb": 2, "ways": 2, "stride": 4},
                "brief": r'''
One last look at the uniprocessor plot, this time to establish what it *cannot*
show. Everything on this axis is one cache in isolation; the misses this module is
about do not appear on it at all.
''',
                "notice": [
                    "At a stride of 4 B the curve sits at 6.25 per cent — one miss per sixteen accesses, which is the stride over the 64-byte block. The readout splits it: 2.08 compulsory, 4.17 capacity, zero conflict, so exactly a third of these misses are the unavoidable first touch. That is module 2's reckoning, measured rather than asserted.",
                    "Nothing on this plot goes below 6.25 per cent *at this size* — but drag the size up and at 32 KB it drops to 2.08, which is the compulsory third on its own. The floor is the compulsory term, not the number the curve happens to be sitting on, and the difference between the two is the entire capacity component.",
                    "Push the stride to 64 B and the curve jumps to 100 per cent, then drag associativity through its whole range. The marker does not move: at 2 KB every miss you can create here is a placement or a volume miss, and neither is what associativity fixes. The faint curves do separate at 24 KB, where direct-mapped reads 66.7 and the associative ones read 100 — worth a look, because it is the one place on this plot where more associativity costs you.",
                    "Now imagine the missing axis. A second cache writing one of these lines would invalidate this one, and the very next access to an address that has not moved, in a cache that has not evicted it, would miss anyway. That is the coherence miss, and it is the fourth C this plot has no room for.",
                ],
            },
            "derive": {
                "title": "What a shared line costs",
                "minutes": 14,
                "vars": ["B", "V", "w", "e", "t_1", "t_m", "t_s", "m", "f"],
                "brief": r'''
Two cores, private caches, MESI on a shared bus. Blocks are $B$ bytes, a word is
$V$ bytes. An L1 hit costs $t_1$, a miss served by memory costs $t_m$ on top, and a
miss served by the other cache costs $t_s$ on top.
''',
                "steps": [
                    {
                        "prompt": "Coherence is tracked per block, not per word. How many distinct words does one block cover?",
                        "answer": "\\frac{B}{V}",
                        "hint": "This is the number of independent variables that a single invalidation takes down with it.",
                        "deconstruct": [
                            "A block spans $B$ bytes and a word occupies $V$ of them.",
                            "So one coherence decision covers $B/V$ separately-addressable words.",
                        ],
                    },
                    {
                        "prompt": "A fraction $w$ of accesses are writes. Of those writes, a fraction $e$ find the block already in state Modified or Exclusive and need no bus transaction. Write the rate, per access, at which a write has to put something on the bus.",
                        "answer": "w \\cdot \\left( 1 - e \\right)",
                        "hint": "Only the writes that do not already hold the block in M or E reach the bus at all; whether each one becomes a BusUpgr or a BusRdX does not change how many there are.",
                        "deconstruct": [
                            "Writes happen at rate $w$ per access.",
                            "A fraction $e$ of them are silent, so $1-e$ of them must go to the bus — as a BusUpgr from Shared, as a BusRdX from Invalid.",
                        ],
                    },
                    {
                        "prompt": "A fraction $m$ of accesses miss and are served by memory; a further fraction $f$ miss and are served by the other cache. Write the average access time.",
                        "answer": "t_1 + m \\cdot t_m + f \\cdot t_s",
                        "hint": "Same shape as the AMAT you derived in module 3, with one more term for the misses the other cache answers.",
                        "deconstruct": [
                            "Every access costs $t_1$.",
                            "Two disjoint fractions of them then wait: $m$ for memory, $f$ for the snoop.",
                        ],
                    },
                    {
                        "prompt": "Padding the data so the two cores never share a block drives $f$ to zero and leaves $m$ unchanged. Write the ratio of the shared access time to the padded one.",
                        "answer": "\\frac{t_1 + m \\cdot t_m + f \\cdot t_s}{t_1 + m \\cdot t_m}",
                        "hint": "Divide your last answer by the same expression with $f$ set to zero.",
                        "deconstruct": [
                            "Shared: $t_1 + m t_m + f t_s$.",
                            "Padded: the same with $f = 0$, so the third term disappears.",
                        ],
                    },
                ],
                "closing": r'''
Put numbers in: $t_1 = 1$, $m = 0.02$, $t_m = 200$, $t_s = 40$. Padded, that is 5
cycles. Let false sharing push $f$ to 0.1 and it becomes 9 — an eighty per cent
slowdown bought by a data layout, with no change to the algorithm, the cache size or
the miss rate the uniprocessor tools would report.
''',
            },
            "blanks": {
                "title": "MESI, one transaction at a time",
                "minutes": 8,
                "caption": "mesi.py — four states, and what each transition costs the bus",
                "lang": "python",
                "brief": r"""
Every state in MESI exists to save a bus transaction, and the E state exists to save
exactly one. Fill in the four decisions and the protocol's whole economy is visible.
""",
                "listing": """# Two private caches, one address.

# A read miss brings the block in as ___
#   if no other cache has it,
# and as ___
#   if another cache responds.

# The first write to a block held in E costs ___ .

# A write to a block held in S must first put ___ on the bus.
""",
                "blanks": [
                    {
                        "prompt": "Nobody else has it. What state?",
                        "hole": "?",
                        "opts": ["E", "S", "M", "I"],
                        "a": 0,
                        "why": "Exclusive: mine, clean, and nobody else's. The cache learns this from the absence of a response on the bus, and remembering it is what lets the next write be free.",
                        "whys": [
                            "Exclusive: mine, clean, and nobody else's. The cache learns this from the absence of a response on the bus, and remembering it is what lets the next write be free.",
                            "Shared is the safe answer and the wasteful one — it forgets that nobody else has the block, so the next write has to ask permission it did not need. A protocol that does exactly this is MSI, and E is the entire difference.",
                            "Modified means dirty, and nothing has been written yet.",
                            "Invalid means not present, which is the state it just left.",
                        ],
                    },
                    {
                        "prompt": "Somebody else answered. What state?",
                        "hole": "?",
                        "opts": ["S", "E", "M", "I"],
                        "a": 0,
                        "why": "Shared: readable, clean, and known to exist elsewhere. Both caches end in S — the responder demotes from E or M to S as it supplies the data, which is why a read by one core can slow the next write by another.",
                        "whys": [
                            "Shared: readable, clean, and known to exist elsewhere. Both caches end in S — the responder demotes from E or M to S as it supplies the data, which is why a read by one core can slow the next write by another.",
                            "Exclusive would be a lie: another cache has just proved it holds the block, and acting on that lie would let two caches write without either noticing.",
                            "Modified requires being the only copy and having written it.",
                            "Invalid would discard the block that was just fetched.",
                        ],
                    },
                    {
                        "prompt": "You already know you are the only holder.",
                        "hole": "?",
                        "opts": ["no bus transaction at all", "a BusRdX", "a BusUpgr", "a writeback"],
                        "a": 0,
                        "why": "Nothing. The cache silently changes E to M and writes. This is the entire reason E exists, and it is worth a lot: a read followed by a write to the same line is one of the most common patterns in real code, and MSI pays a bus transaction for it every time.",
                        "whys": [
                            "Nothing. The cache silently changes E to M and writes. This is the entire reason E exists, and it is worth a lot: a read followed by a write to the same line is one of the most common patterns in real code, and MSI pays a bus transaction for it every time.",
                            "BusRdX asks for the data *and* for exclusivity. The data is already here and the exclusivity is already known, so it would fetch a copy of what the cache is holding.",
                            "BusUpgr asks other caches to invalidate — but E already means there are none to ask.",
                            "A writeback moves a dirty block out. Nothing is dirty yet, and the block is not being evicted.",
                        ],
                    },
                    {
                        "prompt": "Others may hold it. What must you send?",
                        "hole": "?",
                        "opts": ["BusUpgr", "BusRd", "nothing", "a writeback"],
                        "a": 0,
                        "why": "BusUpgr invalidates the other copies without transferring any data — the cache already has the block, it just needs permission to be the only one with it. Using BusRdX here would work and would drag a redundant copy across the bus, which is precisely the waste BusUpgr exists to avoid.",
                        "whys": [
                            "BusUpgr invalidates the other copies without transferring any data — the cache already has the block, it just needs permission to be the only one with it. Using BusRdX here would work and would drag a redundant copy across the bus, which is precisely the waste BusUpgr exists to avoid.",
                            "BusRd is a read request; it does not invalidate anything, so the other copies would survive and two caches would disagree.",
                            "Writing silently from S is the bug the whole protocol exists to prevent: another cache would keep serving a stale value with no way to know.",
                            "A writeback pushes dirty data out and says nothing to the other caches about their copies.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "MESI between two snooping caches",
                "runtime": "python",
                "minutes": 46,
                "brief": r'''
Implement the protocol. `workload.py` is read-only and supplies the two-core access
patterns; the state machine and the bus accounting are yours.

`Mesi(block_bytes=64, blocks_per_cache=4)` keeps, per core, a `dict` from block
number to state and a list giving LRU order. `state_of(core, addr)` returns one of
`"M"`, `"E"`, `"S"`, `"I"`.

`read(core, addr)` — returns `True` on a hit.

- resident in any of M, E, S: a hit, no bus traffic, refresh the LRU order.
- Invalid: a miss and a `BusRd`. If the other cache holds the block, it supplies it:
  count a `Flush` if the other copy was M, set the other copy to S, and take S
  yourself. If the other cache does not hold it, take **E**.

`write(core, addr)` — returns `True` when the data was already present.

- M: a hit, nothing on the bus.
- E: a hit; move silently to M. This is the transaction that E exists to save.
- S: a hit, but a `BusUpgr` first; the other copy goes Invalid, yours goes M.
- Invalid: a miss and a `BusRdX`; count a `Flush` if the other copy was M, invalidate
  it, and take M.

Replacement: `blocks_per_cache` blocks per core, LRU. Evicting a block in state M
costs a `Flush`.

Finally `coherence_amat(t_hit, m_local, t_mem, f_coh, t_snoop)`, straight from the
derivation.
''',
                "files": [
                    {"name": "workload.py", "ro": True, "content": r'''
"""Two-core access patterns. Read only: the expected counts depend on them exactly.

Every workload is a list of `(core, op, addr)` triples, `op` in {"r", "w"}.
"""


def ping_pong(rounds, addr=0):
    """The cores take turns reading and then writing the same word."""
    out = []
    for _ in range(rounds):
        for core in (0, 1):
            out.append((core, "r", addr))
            out.append((core, "w", addr))
    return out


def false_sharing(rounds, base=0, word_bytes=4):
    """Each core writes only its own word, but both words are in one block."""
    out = []
    for _ in range(rounds):
        for core in (0, 1):
            out.append((core, "w", base + core * word_bytes))
    return out


def disjoint(rounds, block_bytes=64, count=2):
    """Each core writes blocks no other core ever touches."""
    out = []
    for _ in range(rounds):
        for core in (0, 1):
            for i in range(count):
                out.append((core, "w", (core * count + i) * block_bytes))
    return out
'''},
                    {"name": "main.py", "content": r'''
import numpy as np
from workload import ping_pong, false_sharing, disjoint

TRANSACTIONS = ("BusRd", "BusRdX", "BusUpgr", "Flush")


class Mesi:
    """Two private caches on one snooping bus."""

    def __init__(self, block_bytes=64, blocks_per_cache=4):
        self.block_bytes = block_bytes
        self.blocks_per_cache = blocks_per_cache
        self.state = [{}, {}]
        self.order = [[], []]
        self.bus = {k: 0 for k in TRANSACTIONS}
        self.hits = 0
        self.misses = 0

    def block_of(self, addr):
        return addr // self.block_bytes

    def state_of(self, core, addr):
        """One of "M", "E", "S", "I"."""
        return self.state[core].get(self.block_of(addr), "I")

    def _touch(self, core, b):
        """Make `b` the most recent block in `core`, evicting LRU if over full."""
        # TODO: an evicted block in state M costs a Flush.
        pass

    def read(self, core, addr):
        """Return True on a hit."""
        # TODO
        return False

    def write(self, core, addr):
        """Return True when the data was already resident."""
        # TODO
        return False

    def run(self, work):
        for core, op, addr in work:
            if op == "w":
                self.write(core, addr)
            else:
                self.read(core, addr)
        return dict(self.bus)


def coherence_amat(t_hit, m_local, t_mem, f_coh, t_snoop):
    """Average access time when some misses are answered by the other cache."""
    # TODO
    return 0.0


if __name__ == "__main__":
    for name, work in (("ping-pong", ping_pong(4)),
                       ("false sharing", false_sharing(4)),
                       ("disjoint", disjoint(4))):
        s = Mesi()
        bus = s.run(work)
        print(f"{name:15} hits {s.hits:3d} misses {s.misses:3d} {bus}")
    print("amat:", np.round(coherence_amat(1.0, 0.02, 200.0, 0.10, 40.0), 4))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np
from workload import ping_pong, false_sharing, disjoint

TRANSACTIONS = ("BusRd", "BusRdX", "BusUpgr", "Flush")


class Mesi:
    """Two private caches on one snooping bus."""

    def __init__(self, block_bytes=64, blocks_per_cache=4):
        self.block_bytes = block_bytes
        self.blocks_per_cache = blocks_per_cache
        self.state = [{}, {}]
        self.order = [[], []]
        self.bus = {k: 0 for k in TRANSACTIONS}
        self.hits = 0
        self.misses = 0

    def block_of(self, addr):
        return addr // self.block_bytes

    def state_of(self, core, addr):
        """One of "M", "E", "S", "I"."""
        return self.state[core].get(self.block_of(addr), "I")

    def _touch(self, core, b):
        """Make `b` the most recent block in `core`, evicting LRU if over full."""
        o = self.order[core]
        if b in o:
            o.remove(b)
        o.append(b)
        while len(o) > self.blocks_per_cache:
            victim = o.pop(0)
            if self.state[core].get(victim) == "M":
                self.bus["Flush"] += 1
            self.state[core].pop(victim, None)

    def _invalidate(self, core, b):
        if b in self.order[core]:
            self.order[core].remove(b)
        self.state[core].pop(b, None)

    def read(self, core, addr):
        """Return True on a hit."""
        b = self.block_of(addr)
        other = 1 - core
        if self.state[core].get(b, "I") != "I":
            self.hits += 1
            self._touch(core, b)
            return True
        self.misses += 1
        self.bus["BusRd"] += 1
        ost = self.state[other].get(b, "I")
        if ost == "I":
            self.state[core][b] = "E"
        else:
            if ost == "M":
                self.bus["Flush"] += 1
            self.state[other][b] = "S"
            self.state[core][b] = "S"
        self._touch(core, b)
        return False

    def write(self, core, addr):
        """Return True when the data was already resident."""
        b = self.block_of(addr)
        other = 1 - core
        st = self.state[core].get(b, "I")
        if st == "M":
            self.hits += 1
            self._touch(core, b)
            return True
        if st == "E":
            self.hits += 1
            self.state[core][b] = "M"
            self._touch(core, b)
            return True
        if st == "S":
            self.hits += 1
            self.bus["BusUpgr"] += 1
            self._invalidate(other, b)
            self.state[core][b] = "M"
            self._touch(core, b)
            return True
        self.misses += 1
        self.bus["BusRdX"] += 1
        if self.state[other].get(b, "I") == "M":
            self.bus["Flush"] += 1
        self._invalidate(other, b)
        self.state[core][b] = "M"
        self._touch(core, b)
        return False

    def run(self, work):
        for core, op, addr in work:
            if op == "w":
                self.write(core, addr)
            else:
                self.read(core, addr)
        return dict(self.bus)


def coherence_amat(t_hit, m_local, t_mem, f_coh, t_snoop):
    """Average access time when some misses are answered by the other cache."""
    return t_hit + m_local * t_mem + f_coh * t_snoop


if __name__ == "__main__":
    for name, work in (("ping-pong", ping_pong(4)),
                       ("false sharing", false_sharing(4)),
                       ("disjoint", disjoint(4))):
        s = Mesi()
        bus = s.run(work)
        print(f"{name:15} hits {s.hits:3d} misses {s.misses:3d} {bus}")
    print("amat:", np.round(coherence_amat(1.0, 0.02, 200.0, 0.10, 40.0), 4))
'''}],
                "hints": [
                    "Read the local state before you read the remote one; the local state alone decides hit or miss, and only a miss or an upgrade needs to look across the bus.",
                    "Invalidating the other core means removing the block from *both* its state dict and its LRU list, or the next eviction there will trip over a block that is no longer resident.",
                    "The E case is two lines and no bus traffic. If your ping-pong run shows one more `BusUpgr` than expected, that is where it came from.",
                ],
                "tests": [
                    {"name": "a read nobody else holds lands in Exclusive", "code": r'''
_s = Mesi()
assert _s.read(0, 0) is False, "the first read of a block must be a miss"
assert _s.state_of(0, 0) == "E", \
    (f"no other cache has the block, so the snoop comes back clean and the state "
     f"is E, not S; got {_s.state_of(0, 0)!r}")
assert _s.bus["BusRd"] == 1 and _s.bus["BusRdX"] == 0, f"got {_s.bus}"
assert _s.state_of(1, 0) == "I", "the other core never touched it"
'''},
                    {"name": "the first write to an Exclusive block is free", "code": r'''
_s = Mesi()
_s.read(0, 0)
assert _s.write(0, 0) is True, "the block is resident, so the write hits"
assert _s.state_of(0, 0) == "M", f"E goes silently to M; got {_s.state_of(0, 0)!r}"
assert _s.bus["BusUpgr"] == 0, \
    (f"nobody else can hold a copy of an Exclusive block, so there is nothing to "
     f"invalidate and no transaction to issue; got {_s.bus['BusUpgr']}")
assert sum(_s.bus.values()) == 1, f"only the original BusRd should have happened: {_s.bus}"
'''},
                    {"name": "a second reader downgrades the owner", "code": r'''
_s = Mesi()
_s.read(0, 0)
_s.write(0, 0)
assert _s.state_of(0, 0) == "M"
_s.read(1, 0)
assert _s.state_of(0, 0) == "S" and _s.state_of(1, 0) == "S", \
    (f"the modified copy must be supplied and downgraded, leaving both in S; "
     f"got {_s.state_of(0, 0)!r} and {_s.state_of(1, 0)!r}")
assert _s.bus["Flush"] == 1, \
    f"the dirty data had to leave core 0 for this to be legal; got {_s.bus}"
'''},
                    {"name": "a write from Shared upgrades and invalidates", "code": r'''
_s = Mesi()
_s.read(0, 0)
_s.read(1, 0)
assert (_s.state_of(0, 0), _s.state_of(1, 0)) == ("S", "S")
assert _s.write(1, 0) is True, "the data is present, so this is a hit, not a miss"
assert _s.bus["BusUpgr"] == 1 and _s.bus["BusRdX"] == 0, \
    (f"the block is already resident, so it needs permission and not data: "
     f"BusUpgr, never BusRdX. Got {_s.bus}")
assert (_s.state_of(0, 0), _s.state_of(1, 0)) == ("I", "M"), \
    f"got {_s.state_of(0, 0)!r} and {_s.state_of(1, 0)!r}"
'''},
                    {"name": "ping-pong pays a full round trip every turn", "code": r'''
_s = Mesi()
_bus = _s.run(ping_pong(4))
assert (_s.hits, _s.misses) == (8, 8), \
    f"every read misses and every write then hits; got {_s.hits}, {_s.misses}"
assert _bus["BusRd"] == 8, f"one read miss per turn; got {_bus['BusRd']}"
assert _bus["BusUpgr"] == 7, \
    (f"the very first write finds the block in E and is free; the other seven find "
     f"it in S and must upgrade. Got {_bus['BusUpgr']}")
assert _bus["Flush"] == 7, \
    f"every turn after the first drags modified data across; got {_bus['Flush']}"
assert _bus["BusRdX"] == 0, "no write here ever starts from Invalid"
'''},
                    {"name": "false sharing costs everything that real sharing costs", "code": r'''
_f = Mesi()
_fbus = _f.run(false_sharing(4))
assert (_f.hits, _f.misses) == (0, 8), \
    (f"the cores write different words, but the block bounces, so not one of the 8 "
     f"writes hits; got {_f.hits}, {_f.misses}")
assert _fbus["BusRdX"] == 8 and _fbus["Flush"] == 7, f"got {_fbus}"
_d = Mesi()
_dbus = _d.run(disjoint(4))
assert (_d.hits, _d.misses) == (12, 4), \
    f"separate blocks: 4 cold misses and then hits; got {_d.hits}, {_d.misses}"
assert _dbus["Flush"] == 0, \
    f"nothing is ever snooped away, so nothing is flushed; got {_dbus}"
'''},
                    {"name": "evicting a modified block writes it back", "code": r'''
_s = Mesi(block_bytes=64, blocks_per_cache=2)
_s.write(0, 0)
_s.write(0, 64)
assert _s.bus["Flush"] == 0, "the cache is exactly full and nothing has left it"
_s.write(0, 128)
assert _s.bus["Flush"] == 1, \
    (f"block 0 is the least recently used and it is Modified, so evicting it must "
     f"push the data out; got {_s.bus['Flush']}")
assert _s.state_of(0, 0) == "I", f"the evicted block is gone; got {_s.state_of(0, 0)!r}"
assert _s.state_of(0, 64) == "M" and _s.state_of(0, 128) == "M"
'''},
                    {"name": "coherence misses enter the access time as their own term", "code": r'''
import numpy as np
_shared = coherence_amat(1.0, 0.02, 200.0, 0.10, 40.0)
_padded = coherence_amat(1.0, 0.02, 200.0, 0.0, 40.0)
assert np.isclose(_padded, 5.0), f"1 + 0.02*200 = 5.0; got {_padded}"
assert np.isclose(_shared, 9.0), f"5.0 + 0.10*40 = 9.0; got {_shared}"
assert np.isclose(_shared / _padded, 1.8), \
    "an 80 per cent slowdown from data layout alone, at an unchanged local miss rate"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A coherent two-core hierarchy, measured",
        "runtime": "python",
        "minutes": 130,
        "brief": r'''
Put the four modules together into one model and make it report on itself.

Two cores, each with a private set-associative write-back L1 kept coherent by MESI
over a snooping bus. Memory answers a miss when no other cache holds the block; the
other cache answers it when it does. Every miss is classified, and the whole run
condenses into an average access time.

`workloads.py` is read-only and supplies four two-core patterns. Everything else is
yours.

## What to build

`L1(capacity_bytes, block_bytes, ways)` is a tag store: `index_of`, `present`,
`touch`, `install` (returning the victim it displaced and that victim's state, or
`(None, "I")`) and `drop`.

`System(capacity_bytes=1024, block_bytes=64, ways=2)` owns two of them plus:

- `bus` — counts of `BusRd`, `BusRdX`, `BusUpgr`, `Flush`;
- `hits` and `miss`, the latter a dict over `MISS_KINDS`;
- `served_by_memory` and `served_by_cache`, counting where each miss got its data;
- `read(core, addr)` and `write(core, addr)` implementing MESI exactly as in module
  4, but now on top of a real set-associative cache that can evict;
- `state_of(core, addr)` and `accesses()`.

Classify every miss into one of three kinds, per core:

- `"cold"` — this core has never referenced this block before;
- `"coherence"` — this core held the block and another core's write took it away;
- `"replacement"` — anything else, i.e. this core evicted it itself.

Keep a set of blocks each core has ever referenced and a set of blocks each core has
had invalidated out from under it; clear a block from the second set when it is
reinstalled.

`report(system, t_hit, t_snoop, t_mem)` returns a dict with `accesses`, `hits`,
`misses`, `miss_rate` and `amat`, where

```text
amat = t_hit + (served_by_memory * t_mem + served_by_cache * t_snoop) / accesses
```

## Suggested order

Get `L1` and the single-core path working first — run `private_sweep`, whose two
cores never touch a block the other one has, so nothing coherent has to work yet, and
check that the cold and replacement counts behave the way module 2 taught you.
Then add the remote cache, then the classification, then the report. The checks are
ordered the same way.

A subtlety worth getting right early: a `BusUpgr` is a hit, not a miss. The data was
already there; only the permission was missing. Counting it as a miss makes the
false-sharing and producer-consumer numbers wrong in a way that is hard to find
later.
''',
        "deliverables": [
            "`L1`, a set-associative tag store with LRU replacement whose `install` reports the victim it displaced and the state that victim was in.",
            "`System.read` and `System.write` implementing the full MESI state machine over two `L1`s, with correct `bus` counts including a `Flush` on every eviction of a Modified block.",
            "A per-core miss classification into cold, replacement and coherence, maintained as the run proceeds rather than reconstructed afterwards.",
            "`report`, returning the access count, hit and miss counts, miss rate and AMAT, with the AMAT distinguishing misses answered by memory from misses answered by the other cache.",
            "A short comment at the top of `main.py` naming the geometry you would ship for these workloads and the number in the report that justifies it.",
        ],
        "constraints": [
            "NumPy and the standard library only.",
            "`workloads.py` is read-only; do not change a trace to make a number come out.",
            "A write to a block held Shared is a hit that issues a BusUpgr — it must not be counted as a miss.",
            "The classification must be maintained during the run. Re-deriving it from a second pass over the trace defeats the purpose and will not match the expected counts.",
            "No core may read another core's tag store except through the snoop that `read` and `write` already perform.",
        ],
        "rubric": [
            {"criterion": "Cache geometry and replacement", "weight": 20,
             "evidence": "L1 places blocks by index, keeps each set in LRU order, and reports the displaced victim and its state so the system can flush a Modified one."},
            {"criterion": "MESI state machine", "weight": 30,
             "evidence": "Every transition matches the module 4 table on both cores, including E on an uncontended read miss and a silent E to M upgrade, and the bus counts agree exactly on all four workloads."},
            {"criterion": "Miss classification", "weight": 25,
             "evidence": "Cold, replacement and coherence counts are correct on a private sweep that fits, on one that does not, and on a producer-consumer pattern where the consumer's copy is taken away by a remote write rather than evicted."},
            {"criterion": "AMAT reporting", "weight": 15,
             "evidence": "The report separates misses served by memory from misses served by the other cache and weights them by the right latency, matching hand computation to within 1e-9."},
            {"criterion": "False sharing demonstrated", "weight": 10,
             "evidence": "The false-sharing and padded workloads do identical work, and the report shows the first one missing on every access while the second misses twice."},
        ],
        "hints": [
            "`install` needs to return two things because the caller cannot see the victim's state once it has been removed. Pop it out of the state dict inside `install` and hand it back.",
            "Keep `ever` and `invalidated` as two lists of sets indexed by core. The classification is then three lines: not in `ever` is cold, in `invalidated` is coherence, everything else is replacement.",
            "Add the block to `ever` on every access including hits, and discard it from `invalidated` every time you install it — otherwise a block that is invalidated, refetched, and then evicted gets labelled coherence when it was replacement.",
            "A miss is served by the other cache exactly when that cache's state for the block is not Invalid at the moment of the miss. Read that state before you invalidate anything.",
        ],
        "files": [
            {"name": "workloads.py", "ro": True, "content": r'''
"""Two-core workloads. Read only: every expected number depends on these exactly.

A workload is a list of `(core, op, addr)` triples with `op` in {"r", "w"}.
"""


def private_sweep(rounds, blocks_per_core, block_bytes=64):
    """Each core writes its own contiguous run of blocks, `rounds` times over."""
    out = []
    for _ in range(rounds):
        for core in (0, 1):
            base = core * blocks_per_core * block_bytes
            for i in range(blocks_per_core):
                out.append((core, "w", base + i * block_bytes))
    return out


def producer_consumer(rounds, block_bytes=64, blocks=2):
    """Core 0 writes a small buffer, core 1 reads it, over and over."""
    out = []
    for _ in range(rounds):
        for i in range(blocks):
            out.append((0, "w", i * block_bytes))
        for i in range(blocks):
            out.append((1, "r", i * block_bytes))
    return out


def false_sharing(rounds, word_bytes=4, block_bytes=64):
    """Both cores write different words of the same block."""
    out = []
    for _ in range(rounds):
        out.append((0, "w", 0))
        out.append((1, "w", word_bytes))
    return out


def padded(rounds, block_bytes=64):
    """The same two counters, one block apart. Same work, no sharing."""
    out = []
    for _ in range(rounds):
        out.append((0, "w", 0))
        out.append((1, "w", block_bytes))
    return out
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from workloads import private_sweep, producer_consumer, false_sharing, padded

# Geometry I would ship for these workloads, and the number that says so:
#   TODO

MISS_KINDS = ("cold", "replacement", "coherence")


class L1:
    """A private set-associative tag store with LRU replacement."""

    def __init__(self, capacity_bytes, block_bytes, ways):
        self.block_bytes = block_bytes
        self.ways = ways
        self.sets = capacity_bytes // (block_bytes * ways)
        self.tags = [[] for _ in range(self.sets)]
        self.state = {}

    def index_of(self, block):
        """Which set this block lives in."""
        # TODO
        return 0

    def present(self, block):
        """The MESI state of `block` here, or "I"."""
        # TODO
        return "I"

    def touch(self, block):
        """Make a resident block the most recently used one in its set."""
        # TODO
        pass

    def install(self, block, state):
        """Place `block` in `state`. Return (victim, victim_state) or (None, "I")."""
        # TODO
        return None, "I"

    def drop(self, block):
        """Remove `block` entirely. Return the state it was in."""
        # TODO
        return "I"


class System:
    """Two private L1s on a snooping bus, speaking MESI."""

    def __init__(self, capacity_bytes=1024, block_bytes=64, ways=2):
        self.block_bytes = block_bytes
        self.l1 = [L1(capacity_bytes, block_bytes, ways) for _ in range(2)]
        self.bus = {"BusRd": 0, "BusRdX": 0, "BusUpgr": 0, "Flush": 0}
        self.hits = 0
        self.miss = {k: 0 for k in MISS_KINDS}
        self.served_by_memory = 0
        self.served_by_cache = 0
        self.ever = [set(), set()]
        self.invalidated = [set(), set()]

    def block_of(self, addr):
        return addr // self.block_bytes

    def state_of(self, core, addr):
        return self.l1[core].present(self.block_of(addr))

    def accesses(self):
        return self.hits + sum(self.miss.values())

    def read(self, core, addr):
        """MESI read. Return True on a hit."""
        # TODO
        return False

    def write(self, core, addr):
        """MESI write. Return True when the data was already resident."""
        # TODO
        return False

    def run(self, work):
        for core, op, addr in work:
            if op == "w":
                self.write(core, addr)
            else:
                self.read(core, addr)
        return self


def report(system, t_hit, t_snoop, t_mem):
    """Condense a finished run into access counts, a miss rate and an AMAT."""
    # TODO
    return {}


if __name__ == "__main__":
    for name, work in (("private sweep", private_sweep(3, 4)),
                       ("producer/consumer", producer_consumer(3)),
                       ("false sharing", false_sharing(4)),
                       ("padded", padded(4))):
        s = System(1024, 64, 2).run(work)
        r = report(s, 1.0, 20.0, 100.0)
        print(f"{name:18} {s.miss} bus {s.bus} amat {r.get('amat')}")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from workloads import private_sweep, producer_consumer, false_sharing, padded

# Geometry I would ship for these workloads, and the number that says so:
#   1 KB, 64 B blocks, 2 ways. On private_sweep(3, 8) the 256 B build reports an
#   AMAT of 101 cycles and 32 replacement misses; 512 B and above report 34.33 and
#   none at all, so the working set is the whole story and more capacity than that
#   buys nothing. Two ways rather than one because it costs nothing here and covers
#   the colliding-array case from module 2.

MISS_KINDS = ("cold", "replacement", "coherence")


class L1:
    """A private set-associative tag store with LRU replacement."""

    def __init__(self, capacity_bytes, block_bytes, ways):
        self.block_bytes = block_bytes
        self.ways = ways
        self.sets = capacity_bytes // (block_bytes * ways)
        self.tags = [[] for _ in range(self.sets)]
        self.state = {}

    def index_of(self, block):
        """Which set this block lives in."""
        return block % self.sets

    def present(self, block):
        """The MESI state of `block` here, or "I"."""
        return self.state.get(block, "I")

    def touch(self, block):
        """Make a resident block the most recently used one in its set."""
        s = self.tags[self.index_of(block)]
        if block in s:
            s.remove(block)
            s.append(block)

    def install(self, block, state):
        """Place `block` in `state`. Return (victim, victim_state) or (None, "I")."""
        s = self.tags[self.index_of(block)]
        if block in s:
            s.remove(block)
        s.append(block)
        self.state[block] = state
        if len(s) > self.ways:
            victim = s.pop(0)
            return victim, self.state.pop(victim, "I")
        return None, "I"

    def drop(self, block):
        """Remove `block` entirely. Return the state it was in."""
        s = self.tags[self.index_of(block)]
        if block in s:
            s.remove(block)
        return self.state.pop(block, "I")


class System:
    """Two private L1s on a snooping bus, speaking MESI."""

    def __init__(self, capacity_bytes=1024, block_bytes=64, ways=2):
        self.block_bytes = block_bytes
        self.l1 = [L1(capacity_bytes, block_bytes, ways) for _ in range(2)]
        self.bus = {"BusRd": 0, "BusRdX": 0, "BusUpgr": 0, "Flush": 0}
        self.hits = 0
        self.miss = {k: 0 for k in MISS_KINDS}
        self.served_by_memory = 0
        self.served_by_cache = 0
        self.ever = [set(), set()]
        self.invalidated = [set(), set()]

    def block_of(self, addr):
        return addr // self.block_bytes

    def state_of(self, core, addr):
        return self.l1[core].present(self.block_of(addr))

    def accesses(self):
        return self.hits + sum(self.miss.values())

    def _kind(self, core, b):
        if b not in self.ever[core]:
            return "cold"
        if b in self.invalidated[core]:
            return "coherence"
        return "replacement"

    def _evicted(self, victim, vstate):
        if victim is not None and vstate == "M":
            self.bus["Flush"] += 1

    def _snoop_invalidate(self, other, b):
        st = self.l1[other].present(b)
        if st != "I":
            if st == "M":
                self.bus["Flush"] += 1
            self.l1[other].drop(b)
            self.invalidated[other].add(b)

    def read(self, core, addr):
        """MESI read. Return True on a hit."""
        b = self.block_of(addr)
        other = 1 - core
        if self.l1[core].present(b) != "I":
            self.hits += 1
            self.l1[core].touch(b)
            self.ever[core].add(b)
            return True
        self.miss[self._kind(core, b)] += 1
        self.bus["BusRd"] += 1
        ost = self.l1[other].present(b)
        if ost == "I":
            self.served_by_memory += 1
            new = "E"
        else:
            self.served_by_cache += 1
            if ost == "M":
                self.bus["Flush"] += 1
            self.l1[other].state[b] = "S"
            new = "S"
        self._evicted(*self.l1[core].install(b, new))
        self.ever[core].add(b)
        self.invalidated[core].discard(b)
        return False

    def write(self, core, addr):
        """MESI write. Return True when the data was already resident."""
        b = self.block_of(addr)
        other = 1 - core
        st = self.l1[core].present(b)
        if st in ("M", "E"):
            self.hits += 1
            self.l1[core].state[b] = "M"
            self.l1[core].touch(b)
            self.ever[core].add(b)
            return True
        if st == "S":
            self.hits += 1
            self.bus["BusUpgr"] += 1
            self._snoop_invalidate(other, b)
            self.l1[core].state[b] = "M"
            self.l1[core].touch(b)
            self.ever[core].add(b)
            return True
        self.miss[self._kind(core, b)] += 1
        self.bus["BusRdX"] += 1
        if self.l1[other].present(b) == "I":
            self.served_by_memory += 1
        else:
            self.served_by_cache += 1
        self._snoop_invalidate(other, b)
        self._evicted(*self.l1[core].install(b, "M"))
        self.ever[core].add(b)
        self.invalidated[core].discard(b)
        return False

    def run(self, work):
        for core, op, addr in work:
            if op == "w":
                self.write(core, addr)
            else:
                self.read(core, addr)
        return self


def report(system, t_hit, t_snoop, t_mem):
    """Condense a finished run into access counts, a miss rate and an AMAT."""
    n = system.accesses()
    misses = sum(system.miss.values())
    cost = system.served_by_memory * t_mem + system.served_by_cache * t_snoop
    return {
        "accesses": n,
        "hits": system.hits,
        "misses": misses,
        "miss_rate": misses / n if n else 0.0,
        "amat": t_hit + (cost / n if n else 0.0),
    }


if __name__ == "__main__":
    for name, work in (("private sweep", private_sweep(3, 4)),
                       ("producer/consumer", producer_consumer(3)),
                       ("false sharing", false_sharing(4)),
                       ("padded", padded(4))):
        s = System(1024, 64, 2).run(work)
        r = report(s, 1.0, 20.0, 100.0)
        print(f"{name:18} {s.miss} bus {s.bus} amat {np.round(r['amat'], 4)}")
'''},
        ],
        "tests": [
            {"name": "the tag store places, reorders and evicts", "code": r'''
_c = L1(256, 64, 1)
assert _c.sets == 4, f"256 B of 64 B blocks, one way, is 4 sets; got {_c.sets}"
assert _c.index_of(5) == 1, f"block 5 in a 4-set cache indexes set 1; got {_c.index_of(5)}"
assert _c.present(0) == "I", "an empty cache holds nothing"
assert _c.install(0, "M") == (None, "I"), "the first block into an empty set evicts nothing"
assert _c.present(0) == "M", f"got {_c.present(0)!r}"
assert _c.install(4, "E") == (0, "M"), \
    "block 4 shares set 0 with block 0, so a one-way cache must throw block 0 out and say so"
assert _c.present(0) == "I" and _c.present(4) == "E"
_d = L1(256, 64, 2)
_d.install(0, "S")
_d.install(4, "S")
_d.touch(0)
assert _d.install(8, "M") == (4, "S"), \
    "touching block 0 made block 4 the least recent, so block 4 is the victim"
'''},
            {"name": "a private sweep that fits is cold misses and nothing else", "code": r'''
_s = System(1024, 64, 2).run(private_sweep(3, 4))
assert _s.accesses() == 24, f"3 rounds, 2 cores, 4 blocks each; got {_s.accesses()}"
assert _s.miss["cold"] == 8, \
    f"4 blocks per core, 2 cores, one first reference each; got {_s.miss}"
assert _s.miss["replacement"] == 0 and _s.miss["coherence"] == 0, \
    f"the working set fits and the cores share nothing; got {_s.miss}"
assert _s.hits == 16, f"every access after the first round hits; got {_s.hits}"
assert _s.bus["BusRdX"] == 8 and _s.bus["Flush"] == 0, \
    f"8 write misses, nothing snooped and nothing evicted; got {_s.bus}"
assert _s.served_by_memory == 8 and _s.served_by_cache == 0, \
    f"no block ever lives in both caches; got {_s.served_by_memory}, {_s.served_by_cache}"
'''},
            {"name": "an oversized sweep turns into replacement misses", "code": r'''
_small = System(256, 64, 1).run(private_sweep(3, 8))
assert _small.miss["cold"] == 16, f"8 blocks per core, 2 cores; got {_small.miss}"
assert _small.miss["replacement"] == 32, \
    (f"an 8-block working set cycling through a 4-block cache re-misses everything "
     f"after the first round; got {_small.miss}")
assert _small.miss["coherence"] == 0, f"the cores still share nothing; got {_small.miss}"
assert _small.hits == 0, f"LRU on a cyclic sweep hits nothing at all; got {_small.hits}"
assert _small.bus["Flush"] == 40, \
    (f"48 installs, 8 of which fill empty sets, leaves 40 evictions and every "
     f"victim is Modified; got {_small.bus}")
_big = System(512, 64, 1).run(private_sweep(3, 8))
assert _big.miss["replacement"] == 0 and _big.hits == 32, \
    f"doubling the capacity removes every one of them; got {_big.miss}, {_big.hits}"
'''},
            {"name": "producer-consumer produces coherence misses on both sides", "code": r'''
_s = System(1024, 64, 2).run(producer_consumer(3))
assert _s.accesses() == 12, f"3 rounds of 2 writes and 2 reads; got {_s.accesses()}"
assert _s.miss["cold"] == 4, \
    f"two blocks, first touched by each core once; got {_s.miss}"
assert _s.miss["coherence"] == 4, \
    (f"in rounds 2 and 3 the consumer's copy has been taken away by the producer's "
     f"upgrade, so its reads miss on blocks it still had; got {_s.miss}")
assert _s.miss["replacement"] == 0, f"two blocks in a 16-block cache; got {_s.miss}"
assert _s.bus["BusUpgr"] == 4, \
    (f"in rounds 2 and 3 the producer holds each block Shared and must upgrade "
     f"rather than refetch; got {_s.bus}")
assert _s.served_by_cache == 6 and _s.served_by_memory == 2, \
    f"only the two very first misses reach memory; got {_s.served_by_memory}, {_s.served_by_cache}"
'''},
            {"name": "a BusUpgr is a hit, not a miss", "code": r'''
_s = System(1024, 64, 2)
_s.read(0, 0)
_s.read(1, 0)
assert (_s.state_of(0, 0), _s.state_of(1, 0)) == ("S", "S"), \
    f"got {_s.state_of(0, 0)!r}, {_s.state_of(1, 0)!r}"
_before = sum(_s.miss.values())
assert _s.write(1, 0) is True, "the data is resident; only the permission was missing"
assert sum(_s.miss.values()) == _before, \
    f"an upgrade must not be counted as a miss; miss counts went {_before} -> {sum(_s.miss.values())}"
assert _s.bus["BusUpgr"] == 1 and _s.bus["BusRdX"] == 0, f"got {_s.bus}"
assert (_s.state_of(0, 0), _s.state_of(1, 0)) == ("I", "M"), \
    f"got {_s.state_of(0, 0)!r}, {_s.state_of(1, 0)!r}"
'''},
            {"name": "false sharing and padding do the same work at different prices", "code": r'''
import numpy as np
_f = System(1024, 64, 2).run(false_sharing(4))
_p = System(1024, 64, 2).run(padded(4))
assert _f.accesses() == _p.accesses() == 8, "identical amounts of work"
assert _f.hits == 0 and _f.miss["coherence"] == 6, \
    (f"different words, one block: every write after the first two is a coherence "
     f"miss; got {_f.hits} hits and {_f.miss}")
assert _p.hits == 6 and _p.miss["coherence"] == 0, \
    f"one block apart and the sharing disappears; got {_p.hits} hits and {_p.miss}"
_rf = report(_f, 1.0, 20.0, 100.0)
_rp = report(_p, 1.0, 20.0, 100.0)
assert np.isclose(_rf["miss_rate"], 1.0) and np.isclose(_rp["miss_rate"], 0.25), \
    f"got {_rf['miss_rate']} and {_rp['miss_rate']}"
assert np.isclose(_rf["amat"], 31.0), \
    f"1 + (1*100 + 7*20)/8 = 31.0; got {_rf['amat']}"
assert np.isclose(_rp["amat"], 26.0), f"1 + (2*100)/8 = 26.0; got {_rp['amat']}"
'''},
            {"name": "the report adds up", "code": r'''
import numpy as np
_s = System(1024, 64, 2).run(producer_consumer(3))
_r = report(_s, 1.0, 20.0, 100.0)
assert _r["accesses"] == 12 and _r["hits"] == 4 and _r["misses"] == 8, f"got {_r}"
assert _r["hits"] + _r["misses"] == _r["accesses"], \
    f"every access is one or the other; got {_r}"
assert np.isclose(_r["miss_rate"], 8.0 / 12.0), f"got {_r['miss_rate']}"
assert np.isclose(_r["amat"], 1.0 + (2 * 100.0 + 6 * 20.0) / 12.0), \
    (f"2 misses answered by memory at 100 and 6 by the other cache at 20, over 12 "
     f"accesses, on top of a 1-cycle hit; got {_r['amat']}")
'''},
        ],
    },
}
