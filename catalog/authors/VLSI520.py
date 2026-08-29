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
                "True LRU is a per-set ordering, not a per-block counter — and it is the only policy that turns a repeated access into a hit reliably.",
                "Widening the set costs `W` tag comparators and a `W`-to-1 multiplexer in the hit path, which is why real L1 caches stop at four or eight ways.",
            ],
            "sandbox": {
                "title": "What capacity and associativity do not buy you",
                "visualiser": "cache",
                "minutes": 9,
                "initial": {"kb": 8, "ways": 1, "stride": 64},
                "brief": r'''
The plot sweeps cache size along the x axis and reports the miss rate of an LRU
cache on a strided walk. The accented curve is the associativity you have selected;
the faint ones are the other two shown for comparison.

Read the fine print of the experiment before you read the plot. The trace is a
cyclic sweep over a working set defined as **four times the cache**, so the working
set grows every time you drag the size slider. That is a deliberate worst case, and
it is worth meeting before you meet the friendly cases.
''',
                "notice": [
                    "With the stride at 64 B, drag the cache size from 1 KB to 64 KB. The curve does not move: it is a horizontal line at 100 per cent. The working set is defined as four times the cache, so capacity can never catch up with it.",
                    "Still at 64 B, raise associativity from direct to 16-way. The accented curve stays at 100 and the faint comparison curves sit exactly underneath it. A cyclic sweep is the worst case for LRU at *every* associativity: the line LRU chooses to evict is precisely the one wanted next.",
                    "Drop the stride to 32 B. The whole family falls to exactly 50 per cent; at 16 B it is 25, at 8 B it is 12.5. Every hit in this trace is a spatial hit inside one 64-byte line, so the miss rate is exactly stride divided by block size.",
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
                        "placeholder": "\\frac{C}{B}",
                        "hint": "The data array is $C$ bytes and every block occupies $B$ of them.",
                        "deconstruct": [
                            "Capacity here means data bytes; the tag store is extra and is not counted in $C$.",
                            "So the block count is simply the capacity divided by the block size.",
                        ],
                    },
                    {
                        "prompt": "Those blocks are grouped $W$ to a set. Write the number of sets $S$ in terms of $C$, $B$ and $W$.",
                        "answer": "\\frac{C}{B \\cdot W}",
                        "placeholder": "\\frac{C}{B \\cdot W}",
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
                        "placeholder": "\\frac{M \\cdot W}{C}",
                        "hint": "Divide the region's block count by the number of sets, then substitute your expression for $S$.",
                        "deconstruct": [
                            "Blocks in the region: $M/B$. Sets available: $S = C/(BW)$.",
                            "Blocks per set is $(M/B) \\div (C/(BW))$, and the $B$ cancels.",
                        ],
                    },
                    {
                        "prompt": "A set holds $W$ blocks. Set your last expression equal to $W$ and solve for $M$: how large may the region be before a set is over-subscribed?",
                        "answer": "C",
                        "placeholder": "C",
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
    (f"the first 4 misses land in empty sets and evict nothing; the other 44 each "
     f"throw a block out. Got {_c.evictions}")
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
                    "Now sweep associativity from 1 to 16 at that stride. The curve does not move by a pixel, and the faint comparison curves lie on top of the accented one. Zero conflict misses: a fully associative cache of the same size does no better than a direct-mapped one here, which is the definition.",
                    "Set the stride to 64 B or 128 B. The curve pins to 100 per cent at every size and every associativity — one access per block, no spatial reuse left, and a working set that grows with the cache so temporal reuse never arrives either.",
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
                        "placeholder": "m_{inf}",
                        "hint": "An infinite cache evicts nothing, so the only misses left in it are first references.",
                        "deconstruct": [
                            "$m_{inf}$ counts a miss only when the block has never been referenced before.",
                            "That is precisely the definition of a compulsory miss.",
                        ],
                    },
                    {
                        "prompt": "The capacity rate: misses the fully associative cache suffers that the infinite one does not. Write it.",
                        "answer": "m_{fa} - m_{inf}",
                        "placeholder": "m_{fa} - m_{inf}",
                        "hint": "The fully associative cache has no index at all, so anything it misses beyond a first reference it missed on volume.",
                        "deconstruct": [
                            "$m_{fa}$ contains the compulsory misses plus whatever LRU had to throw out.",
                            "Subtract the compulsory part to leave the volume-driven part.",
                        ],
                    },
                    {
                        "prompt": "The conflict rate: what the real index costs you over a fully associative cache of the same size. Write it.",
                        "answer": "m_{dm} - m_{fa}",
                        "placeholder": "m_{dm} - m_{fa}",
                        "hint": "Two caches, same capacity, same replacement policy, different placement. The difference is placement alone.",
                        "deconstruct": [
                            "$m_{dm}$ contains everything: compulsory, capacity and conflict.",
                            "$m_{fa}$ contains compulsory and capacity, so the difference is what is left.",
                        ],
                    },
                    {
                        "prompt": "What fraction of the real cache's misses could full associativity remove? Write it in terms of $m_{dm}$ and $m_{fa}$.",
                        "answer": "\\frac{m_{dm} - m_{fa}}{m_{dm}}",
                        "placeholder": "\\frac{m_{dm} - m_{fa}}{m_{dm}}",
                        "hint": "Take the conflict rate you just wrote and express it as a share of the total miss rate.",
                        "deconstruct": [
                            "Conflict misses per access: $m_{dm} - m_{fa}$.",
                            "All misses per access: $m_{dm}$. Divide.",
                        ],
                    },
                    {
                        "prompt": "A program makes $N$ accesses over a region of $M$ bytes with blocks of $B$ bytes. Every block is touched at least once. Write the compulsory miss rate.",
                        "answer": "\\frac{M}{B \\cdot N}",
                        "placeholder": "\\frac{M}{B \\cdot N}",
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
                "Write-back with write-allocate moves a whole block on a miss and another on a dirty eviction; write-through with no-write-allocate moves one word per write and nothing else.",
                "Which wins is arithmetic, not doctrine: it turns on how many times a block is written before it leaves.",
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
                    "At a stride of 8 B the curve sits at 12.5 per cent, flat across the whole size axis. That is $1 + 0.125 \\times 100 = 13.5$ cycles per access against a 1-cycle hit: the hierarchy is running at about a thirteenth of its hit rate.",
                    "Halve the stride to 4 B and the curve halves to 6.25, giving $1 + 0.0625 \\times 100 = 7.25$ cycles. Halving the miss rate nearly halved the access time, because at these numbers the penalty term is almost the whole of it.",
                    "Now drag the size slider anywhere you like at either stride. The curve does not move, so neither does the AMAT. On this trace no amount of capacity buys a single cycle — a reminder that AMAT is only as honest as the miss rate you feed it.",
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
                        "placeholder": "t_1 + m_1 \\cdot t_m",
                        "hint": "You pay the hit time on every access, and the memory time on the fraction that miss.",
                        "deconstruct": [
                            "Every access costs $t_1$ whether it hits or not — the tag check happens regardless.",
                            "A fraction $m_1$ then also waits $t_m$.",
                        ],
                    },
                    {
                        "prompt": "Now insert the L2. Write the average access time in terms of $t_1$, $m_1$, $t_2$, $m_2$ and $t_m$.",
                        "answer": "t_1 + m_1 \\cdot \\left( t_2 + m_2 \\cdot t_m \\right)",
                        "placeholder": "t_1 + m_1 \\cdot \\left( t_2 + m_2 \\cdot t_m \\right)",
                        "hint": "The L1 miss penalty is no longer $t_m$; it is the L2's own average access time.",
                        "deconstruct": [
                            "Replace $t_m$ in the previous answer by whatever an L1 miss actually costs.",
                            "An L1 miss reaches the L2, which costs $t_2$, and misses in turn with probability $m_2$.",
                        ],
                    },
                    {
                        "prompt": "Write the L2 global miss rate — the fraction of *all* processor accesses that reach memory — in terms of $m_1$ and $m_2$.",
                        "answer": "m_1 \\cdot m_2",
                        "placeholder": "m_1 \\cdot m_2",
                        "hint": "$m_2$ is measured against accesses that got past the L1, not against all of them.",
                        "deconstruct": [
                            "A fraction $m_1$ of accesses reach the L2 at all.",
                            "Of those, a fraction $m_2$ go further, so the product is the share of all accesses.",
                        ],
                    },
                    {
                        "prompt": "A write-back, write-allocate cache misses at rate $m$, and a fraction $d$ of the blocks it evicts are dirty. Write the bytes moved to and from memory per access.",
                        "answer": "m \\cdot B \\cdot \\left( 1 + d \\right)",
                        "placeholder": "m \\cdot B \\cdot \\left( 1 + d \\right)",
                        "hint": "A miss always fetches a block; it additionally writes a block out when the victim was dirty.",
                        "deconstruct": [
                            "Per miss: $B$ bytes in, always, because the policy allocates on writes as well as reads.",
                            "Plus $B$ bytes out with probability $d$, so $B(1+d)$ per miss and $mB(1+d)$ per access.",
                        ],
                    },
                    {
                        "prompt": "Now a write-through, no-write-allocate cache. A fraction $w$ of accesses are writes and each sends $V$ bytes straight to memory; reads miss at rate $m$ and fetch a block. Write the bytes per access.",
                        "answer": "\\left( 1 - w \\right) \\cdot m \\cdot B + w \\cdot V",
                        "placeholder": "\\left( 1 - w \\right) \\cdot m \\cdot B + w \\cdot V",
                        "hint": "Two independent contributions: the reads that miss, and every single write.",
                        "deconstruct": [
                            "A fraction $1-w$ of accesses are reads; of those, $m$ fetch $B$ bytes.",
                            "Every write, hit or miss, sends $V$ bytes onward, and a write miss allocates nothing.",
                        ],
                    },
                ],
                "closing": r'''
Set the two expressions equal and the break-even is a statement about reuse: a block
must be written more than about $B(1+d)/V$ times before it leaves for write-back to
pay. With 64-byte blocks and 8-byte words that is roughly eight writes per block —
easy for a stack or an array being filled, impossible for a scatter.
''',
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
                    "At a stride of 4 B the curve sits at 6.25 per cent — one miss per sixteen accesses, the compulsory floor for a 64-byte block. Nothing on this plot goes below it, at any size or associativity.",
                    "Push the stride to 64 B and the curve jumps to 100 per cent, then drag associativity through its whole range. Neither the accented curve nor the faint ones move. Every miss you can create here is a placement or a volume miss.",
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
                        "placeholder": "\\frac{B}{V}",
                        "hint": "This is the number of independent variables that a single invalidation takes down with it.",
                        "deconstruct": [
                            "A block spans $B$ bytes and a word occupies $V$ of them.",
                            "So one coherence decision covers $B/V$ separately-addressable words.",
                        ],
                    },
                    {
                        "prompt": "A fraction $w$ of accesses are writes. Of those writes, a fraction $e$ find the block already in state Modified or Exclusive and need no bus transaction. Write the bus-upgrade rate per access.",
                        "answer": "w \\cdot \\left( 1 - e \\right)",
                        "placeholder": "w \\cdot \\left( 1 - e \\right)",
                        "hint": "Only writes can upgrade, and only the ones that do not already own the block exclusively.",
                        "deconstruct": [
                            "Writes happen at rate $w$ per access.",
                            "A fraction $e$ of them are silent, so $1-e$ of them must go to the bus.",
                        ],
                    },
                    {
                        "prompt": "A fraction $m$ of accesses miss and are served by memory; a further fraction $f$ miss and are served by the other cache. Write the average access time.",
                        "answer": "t_1 + m \\cdot t_m + f \\cdot t_s",
                        "placeholder": "t_1 + m \\cdot t_m + f \\cdot t_s",
                        "hint": "Same shape as the AMAT you derived in module 3, with one more term for the misses the other cache answers.",
                        "deconstruct": [
                            "Every access costs $t_1$.",
                            "Two disjoint fractions of them then wait: $m$ for memory, $f$ for the snoop.",
                        ],
                    },
                    {
                        "prompt": "Padding the data so the two cores never share a block drives $f$ to zero and leaves $m$ unchanged. Write the ratio of the shared access time to the padded one.",
                        "answer": "\\frac{t_1 + m \\cdot t_m + f \\cdot t_s}{t_1 + m \\cdot t_m}",
                        "placeholder": "\\frac{t_1 + m \\cdot t_m + f \\cdot t_s}{t_1 + m \\cdot t_m}",
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

Get `L1` and the single-core path working first — run `private_sweep` on one core
and check that the cold and replacement counts behave the way module 2 taught you.
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
             "evidence": "Cold, replacement and coherence counts are correct on a private sweep that fits, on one that does not, and on a producer-consumer pattern where all three kinds appear."},
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
