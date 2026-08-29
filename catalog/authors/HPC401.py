"""HPC401 — High-Performance & Parallel Computing. Author module."""

COURSE = {
    "id": "HPC401",
    "title": "High-Performance & Parallel Computing",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["CE201", "CS301"],
    "stack": ["C/OpenMP (reference)", "Python"],
    "credits": 10,
    "hours": 150,
    "icon": "║",
    "summary": (
        "Performance engineering treated as a measurement discipline rather than a "
        "collection of tricks. You build a timing harness and a memory-traffic model, "
        "derive work and span for parallel primitives, enumerate every interleaving of "
        "a racy counter to prove the race exists, and count the messages a ring "
        "allreduce actually sends against its lower bound."
    ),
    "outcomes": [
        "Measure a kernel honestly: repeat, take the minimum, and report what varied",
        "Predict the memory traffic of a loop nest and explain the speedup blocking buys",
        "Derive work, span and parallelism for a task DAG and check them against an implementation",
        "Implement a work-efficient parallel scan and validate it against the sequential result",
        "Enumerate the interleavings of a small concurrent program and exhibit the race witness",
        "Cost a collective operation in messages and bytes against its theoretical bound",
        "Attribute a measured speedup to a serial fraction using Amdahl's law",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone optimisation study (60%).",
    "reading": [
        "Hennessy & Patterson, *Computer Architecture: A Quantitative Approach*, 6th ed. — chapters 1-2 and appendix B",
        "Williams, Waterman & Patterson, 'Roofline: An Insightful Visual Performance Model for Multicore Architectures', *CACM* 52(4), 2009",
        "Blelloch, 'Prefix Sums and Their Applications', CMU-CS-90-190, 1990",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Measurement and the memory hierarchy",
            "summary": "Time it before you touch it, then explain the number with a traffic model.",
            "concepts": [
                "Minimum-of-repeats beats the mean: the fastest run is the least perturbed one",
                "Timer resolution, warm-up effects, and why a single run tells you nothing",
                "The memory hierarchy: registers, L1/L2/L3, DRAM, and their bandwidth gap",
                "Loop nests have a working set; the ijk triple loop streams B once per row of A",
                "Cache blocking (tiling) trades a larger index space for a resident working set",
                "Arithmetic intensity = flops per byte moved; the roofline it implies",
                "Blocking changes the accumulation *order* of a sum, so verify equality deliberately",
            ],
            "lab": {
                "title": "Blocked matrix multiply and its traffic model",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Nothing in this course is allowed to be believed without a measurement and a
model that agrees with it. This lab builds both.

## The harness

**`time_best(fn, repeats=5)`** calls `fn()` `repeats` times and returns
`(last_result, best_seconds)` — the *minimum* elapsed time, using
`time.perf_counter()`. `repeats` below 1 raises `ValueError`.

## The kernels

Matrices are lists of rows of floats.

**`matmul_naive(a, b)`** — the textbook `i, j, k` triple loop. For each output
element accumulate `total += a[i][p] * b[p][j]` for `p` ascending, then store.
Mismatched inner dimensions raise `ValueError`; an empty `a` gives `[]`.

**`matmul_blocked(a, b, block)`** — the same product, computed over tiles.
Loop `ii`, `kk`, `jj` in steps of `block`, then the three inner loops inside the
tile, accumulating into `out[i][j]`. `block` below 1 raises `ValueError`; a
`block` that does not divide the matrix must still work (clamp the tile end with
`min`).

Because both versions accumulate over `p` in ascending order, they must agree
**exactly** — not approximately. If your results differ in the last bits you
have reordered the sum somewhere.

## The model

Count elements moved between DRAM and cache, assuming one row of `A` and one
tile stay resident.

```text
traffic_naive(n)          ->  elem_bytes * (n**3 + 2 * n**2)
traffic_blocked(n, block) ->  elem_bytes * (2 * n**3 // block + n**2)
```

`traffic_blocked` raises `ValueError` unless `block >= 1` and `block` divides
`n` — the model is only stated for the exact case.

**`arithmetic_intensity(n, block, elem_bytes=8)`** returns the blocked kernel's
flops per byte, counting `2 * n**3` flops (one multiply and one add per term).

```text
traffic_naive(64)            -> 2162688 bytes
traffic_blocked(64, 16)      ->  294912 bytes   (7.33x less)
arithmetic_intensity(64, 16) -> 1.7778 flop/byte
```
''',
                "files": [{"name": "main.py", "content": r'''
import random
import time


def time_best(fn, repeats=5):
    """Run fn repeats times; return (last result, best elapsed seconds)."""
    # your code here


def matmul_naive(a, b):
    """Textbook i, j, k triple loop."""
    # your code here


def matmul_blocked(a, b, block):
    """The same product, accumulated tile by tile."""
    # your code here


def traffic_naive(n, elem_bytes=8):
    """Modelled bytes moved by the naive n x n kernel."""
    # your code here


def traffic_blocked(n, block, elem_bytes=8):
    """Modelled bytes moved by the blocked n x n kernel."""
    # your code here


def arithmetic_intensity(n, block, elem_bytes=8):
    """Flops per byte for the blocked kernel."""
    # your code here


rng = random.Random(7)
N = 32
A = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]
B = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]

naive, t_naive = time_best(lambda: matmul_naive(A, B), 3)
blocked, t_blocked = time_best(lambda: matmul_blocked(A, B, 8), 3)
print("identical:", naive == blocked)
print(f"traffic ratio at n=64, b=16: {traffic_naive(64) / traffic_blocked(64, 16):.3f}")
print(f"arithmetic intensity: {arithmetic_intensity(64, 16):.4f} flop/byte")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import random
import time


def time_best(fn, repeats=5):
    """Run fn repeats times; return (last result, best elapsed seconds)."""
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    best = None
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        elapsed = time.perf_counter() - start
        if best is None or elapsed < best:
            best = elapsed
    return result, best


def matmul_naive(a, b):
    """Textbook i, j, k triple loop."""
    n = len(a)
    if n == 0:
        return []
    k = len(a[0])
    if len(b) != k:
        raise ValueError(f"inner dimensions disagree: {k} vs {len(b)}")
    m = len(b[0])
    out = [[0.0] * m for _ in range(n)]
    for i in range(n):
        row = a[i]
        out_i = out[i]
        for j in range(m):
            total = 0.0
            for p in range(k):
                total += row[p] * b[p][j]
            out_i[j] = total
    return out


def matmul_blocked(a, b, block):
    """The same product, accumulated tile by tile."""
    if block < 1:
        raise ValueError("block must be at least 1")
    n = len(a)
    if n == 0:
        return []
    k = len(a[0])
    if len(b) != k:
        raise ValueError(f"inner dimensions disagree: {k} vs {len(b)}")
    m = len(b[0])
    out = [[0.0] * m for _ in range(n)]
    for ii in range(0, n, block):
        i_end = min(ii + block, n)
        for kk in range(0, k, block):
            k_end = min(kk + block, k)
            for jj in range(0, m, block):
                j_end = min(jj + block, m)
                for i in range(ii, i_end):
                    row = a[i]
                    out_i = out[i]
                    for p in range(kk, k_end):
                        aip = row[p]
                        b_p = b[p]
                        for j in range(jj, j_end):
                            out_i[j] += aip * b_p[j]
    return out


def traffic_naive(n, elem_bytes=8):
    """Modelled bytes moved by the naive n x n kernel."""
    return elem_bytes * (n ** 3 + 2 * n * n)


def traffic_blocked(n, block, elem_bytes=8):
    """Modelled bytes moved by the blocked n x n kernel."""
    if block < 1:
        raise ValueError("block must be at least 1")
    if n % block:
        raise ValueError(f"block {block} does not divide n={n}")
    return elem_bytes * (2 * n ** 3 // block + n * n)


def arithmetic_intensity(n, block, elem_bytes=8):
    """Flops per byte for the blocked kernel."""
    return 2 * n ** 3 / traffic_blocked(n, block, elem_bytes)


rng = random.Random(7)
N = 32
A = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]
B = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]

naive, t_naive = time_best(lambda: matmul_naive(A, B), 3)
blocked, t_blocked = time_best(lambda: matmul_blocked(A, B, 8), 3)
print("identical:", naive == blocked)
print(f"traffic ratio at n=64, b=16: {traffic_naive(64) / traffic_blocked(64, 16):.3f}")
print(f"arithmetic intensity: {arithmetic_intensity(64, 16):.4f} flop/byte")
'''}],
                "hints": [
                    "`time_best` needs `start = time.perf_counter()` immediately before the call and the subtraction immediately after — nothing else between them.",
                    "The blocked loops are `for ii in range(0, n, block)` with `i_end = min(ii + block, n)`; the inner `for i in range(ii, i_end)` then never runs off the end.",
                    "Keep `kk` outside `jj`. That way `p` still ascends 0, 1, 2, ... across the whole reduction, so the floating-point sum matches the naive one bit for bit.",
                    "The traffic model is arithmetic, not a loop: `n**3 + 2*n**2` elements for the naive kernel, `2*n**3//block + n**2` for the blocked one.",
                ],
                "tests": [
                    {"name": "time_best repeats and reports the minimum", "code": r'''
_calls = []
def _work():
    _calls.append(1)
    return sum(range(1000))
_r, _s = time_best(_work, 4)
assert len(_calls) == 4, f"time_best called fn {len(_calls)} times, expected 4"
assert _r == 499500, f"time_best returned {_r!r}, expected the function result 499500"
assert isinstance(_s, float) and _s >= 0.0, f"elapsed was {_s!r}, expected a non-negative float"
try:
    time_best(_work, 0)
    assert False, "time_best(fn, 0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "matmul_naive computes the product", "code": r'''
_got = matmul_naive([[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]])
assert _got == [[19.0, 22.0], [43.0, 50.0]], f"2x2 product gave {_got!r}"
_got = matmul_naive([[1.0, 2.0, 3.0]], [[1.0], [2.0], [3.0]])
assert _got == [[14.0]], f"1x3 by 3x1 gave {_got!r}, expected [[14.0]]"
assert matmul_naive([], []) == [], "An empty left matrix gives []"
'''},
                    {"name": "matmul_blocked agrees exactly for every block size", "code": r'''
import random as _random
_rng = _random.Random(11)
_a = [[_rng.uniform(-1.0, 1.0) for _ in range(7)] for _ in range(7)]
_b = [[_rng.uniform(-1.0, 1.0) for _ in range(7)] for _ in range(7)]
_want = matmul_naive(_a, _b)
for _blk in (1, 2, 3, 7, 9):
    _got = matmul_blocked(_a, _b, _blk)
    assert _got == _want, f"matmul_blocked(a, b, {_blk}) differs from the naive product"
_a32 = [[_rng.uniform(-1.0, 1.0) for _ in range(32)] for _ in range(32)]
_b32 = [[_rng.uniform(-1.0, 1.0) for _ in range(32)] for _ in range(32)]
assert matmul_blocked(_a32, _b32, 8) == matmul_naive(_a32, _b32), \
    "At n=32 the blocked result must be bit-for-bit identical, not merely close"
'''},
                    {"name": "Both kernels reject bad shapes", "code": r'''
try:
    matmul_naive([[1.0, 2.0]], [[1.0, 2.0]])
    assert False, "matmul_naive should raise ValueError when the inner dimensions disagree"
except ValueError:
    pass
try:
    matmul_blocked([[1.0, 2.0]], [[1.0, 2.0]], 2)
    assert False, "matmul_blocked should raise ValueError when the inner dimensions disagree"
except ValueError:
    pass
for _bad in (0, -4):
    try:
        matmul_blocked([[1.0]], [[1.0]], _bad)
        assert False, f"matmul_blocked with block={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The traffic model matches the derivation", "code": r'''
assert traffic_naive(64) == 2162688, f"traffic_naive(64) gave {traffic_naive(64)!r}, expected 2162688"
assert traffic_naive(8) == 5120, f"traffic_naive(8) gave {traffic_naive(8)!r}, expected 5120"
assert traffic_naive(8, 4) == 2560, f"traffic_naive(8, 4) gave {traffic_naive(8, 4)!r}, expected 2560"
assert traffic_blocked(64, 16) == 294912, \
    f"traffic_blocked(64, 16) gave {traffic_blocked(64, 16)!r}, expected 294912"
assert traffic_blocked(8, 2) == 4608, \
    f"traffic_blocked(8, 2) gave {traffic_blocked(8, 2)!r}, expected 4608"
assert traffic_blocked(64, 1) == 4227072, \
    f"traffic_blocked(64, 1) gave {traffic_blocked(64, 1)!r}, expected 4227072 (a tile of one element moves more than no tiling at all)"
'''},
                    {"name": "traffic_blocked refuses a block that does not divide n", "code": r'''
for _bad in (0, -2):
    try:
        traffic_blocked(64, _bad)
        assert False, f"traffic_blocked(64, {_bad}) should raise ValueError"
    except ValueError:
        pass
try:
    traffic_blocked(64, 7)
    assert False, "traffic_blocked(64, 7) should raise ValueError — 7 does not divide 64"
except ValueError:
    pass
'''},
                    {"name": "Arithmetic intensity and the reported ratio", "code": r'''
_ai = arithmetic_intensity(64, 16)
assert abs(_ai - 16 / 9) < 1e-12, f"arithmetic_intensity(64, 16) gave {_ai!r}, expected 1.7777777777777777"
_ratio = traffic_naive(64) / traffic_blocked(64, 16)
assert abs(_ratio - 22 / 3) < 1e-12, f"traffic ratio was {_ratio!r}, expected 7.333333333333333"
assert "identical: True" in _out, "main.py should report that the two kernels agree exactly"
assert "1.7778 flop/byte" in _out, "main.py should print the arithmetic intensity to 4 decimals"
'''},
                    {"name": "matmul_blocked does its own loops", "code": r'''
_src = open("main.py").read()
_start = _src.index("def matmul_blocked")
_rest = _src[_start:]
_end = _rest.find(chr(10) + "def ", 1)
_body = _rest if _end == -1 else _rest[:_end]
assert "matmul_naive" not in _body, "matmul_blocked must run its own tiled loop nest, not delegate to matmul_naive"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Work, span and the parallel scan",
            "summary": "Cost a computation as a DAG, then build the work-efficient scan.",
            "concepts": [
                "A parallel computation is a DAG: work T1 = total nodes, span T-infinity = longest path",
                "Parallelism = T1 / T-infinity; it caps the speedup no matter how many workers you buy",
                "Brent's theorem: T_p <= T1/p + T-infinity, so p beyond the parallelism is wasted",
                "Tree reduction: n-1 operations in ceil(log2 n) depth, for any associative operator",
                "A naive scan is O(n log n) work; Blelloch's up-sweep/down-sweep is O(n), hence 'work-efficient'",
                "The identity element is what lets you pad to a power of two without changing the answer",
                "Associativity is required; commutativity is not — the reduction order must stay left to right",
            ],
            "lab": {
                "title": "Blelloch scan as a task DAG",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Everything here is executed sequentially. The point is not to run in parallel —
it is to *count* the DAG a parallel machine would execute, and to prove the
clever algorithm returns exactly what the obvious one does.

**`next_power_of_two(n)`** — the smallest power of two at least `n`; `1` for
`n <= 1`.

**`reduce_tree(values, op=operator.add, identity=0)`** — pairwise tree
reduction. Returns `(value, stats)` where `stats` is
`{"work": ..., "span": ...}`: `work` counts applications of `op`, `span` counts
levels. An odd element at the end of a level is carried to the next level
unchanged. Empty input returns `(identity, {"work": 0, "span": 0})`.

```text
reduce_tree(range(1, 101))                       -> (5050, {work: 99, span: 7})
reduce_tree(["a","b","c","d","e"], add, "")      -> ("abcde", {work: 4, span: 3})
```

**`sequential_scan(values, op, identity)`** — the reference **exclusive** scan:
element `i` is the fold of everything strictly before it.

```text
sequential_scan([1, 2, 3, 4])  ->  [0, 1, 3, 6]
```

**`blelloch_scan(values, op=operator.add, identity=0)`** — the work-efficient
exclusive scan, returning `(result, stats)`. Pad to `next_power_of_two(len)`
with `identity`, run the up-sweep (stride doubling, `buf[i] = op(buf[i-stride],
buf[i])`), overwrite the last slot with `identity`, then the down-sweep (stride
halving: the left child takes the parent's value, the parent takes
`op(old_left, parent)`). Count one unit of `work` per `op`, one unit of `span`
per stride level. Trim the padding before returning.

**`scan_cost(n)`** — the closed form for that DAG, `{"work": 2*(m-1),
"span": 2*log2(m)}` for `m = next_power_of_two(n)`. Your instrumented
`blelloch_scan` must reproduce it exactly.

**`parallelism(stats)`** — `work / span`, and `0.0` when `span` is 0.

**`brent_bound(stats, workers)`** — `work/workers + span`. Fewer than 1 worker
raises `ValueError`.

```text
n = 8   -> work 14, span 6, parallelism 2.3333, brent(4) = 9.5
n = 1000-> work 2046, span 20, parallelism 102.3
```
''',
                "files": [{"name": "main.py", "content": r'''
import operator
import random


def next_power_of_two(n):
    """Smallest power of two that is at least n."""
    # your code here


def reduce_tree(values, op=operator.add, identity=0):
    """(value, {"work": ..., "span": ...}) for a pairwise tree reduction."""
    # your code here


def sequential_scan(values, op=operator.add, identity=0):
    """The reference exclusive scan."""
    # your code here


def blelloch_scan(values, op=operator.add, identity=0):
    """(exclusive scan, {"work": ..., "span": ...}) via up-sweep and down-sweep."""
    # your code here


def scan_cost(n):
    """Closed-form {"work": ..., "span": ...} for the Blelloch DAG on n elements."""
    # your code here


def parallelism(stats):
    """work / span, or 0.0 when there is no work to do."""
    # your code here


def brent_bound(stats, workers):
    """Brent's bound on the time with this many workers."""
    # your code here


rng = random.Random(7)
data = [rng.randrange(0, 20) for _ in range(1000)]
total, red_stats = reduce_tree(data)
scan, scan_stats = blelloch_scan(data)
print("sum:", total, red_stats)
print("scan:", scan_stats, "parallelism:", round(parallelism(scan_stats), 3))
print("matches sequential:", scan == sequential_scan(data))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import operator
import random


def next_power_of_two(n):
    """Smallest power of two that is at least n."""
    if n <= 1:
        return 1
    size = 1
    while size < n:
        size *= 2
    return size


def reduce_tree(values, op=operator.add, identity=0):
    """(value, {"work": ..., "span": ...}) for a pairwise tree reduction."""
    level = list(values)
    if not level:
        return identity, {"work": 0, "span": 0}
    work = 0
    span = 0
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level) - 1, 2):
            nxt.append(op(level[i], level[i + 1]))
            work += 1
        if len(level) % 2:
            nxt.append(level[-1])
        level = nxt
        span += 1
    return level[0], {"work": work, "span": span}


def sequential_scan(values, op=operator.add, identity=0):
    """The reference exclusive scan."""
    out = []
    acc = identity
    for value in values:
        out.append(acc)
        acc = op(acc, value)
    return out


def blelloch_scan(values, op=operator.add, identity=0):
    """(exclusive scan, {"work": ..., "span": ...}) via up-sweep and down-sweep."""
    n = len(values)
    if n == 0:
        return [], {"work": 0, "span": 0}
    size = next_power_of_two(n)
    buf = list(values) + [identity] * (size - n)
    work = 0
    span = 0
    stride = 1
    while stride < size:
        for i in range(stride * 2 - 1, size, stride * 2):
            buf[i] = op(buf[i - stride], buf[i])
            work += 1
        span += 1
        stride *= 2
    buf[size - 1] = identity
    stride = size // 2
    while stride >= 1:
        for i in range(stride * 2 - 1, size, stride * 2):
            left = buf[i - stride]
            buf[i - stride] = buf[i]
            buf[i] = op(left, buf[i])
            work += 1
        span += 1
        stride //= 2
    return buf[:n], {"work": work, "span": span}


def scan_cost(n):
    """Closed-form {"work": ..., "span": ...} for the Blelloch DAG on n elements."""
    if n <= 0:
        return {"work": 0, "span": 0}
    size = next_power_of_two(n)
    return {"work": 2 * (size - 1), "span": 2 * size.bit_length() - 2}


def parallelism(stats):
    """work / span, or 0.0 when there is no work to do."""
    if stats["span"] == 0:
        return 0.0
    return stats["work"] / stats["span"]


def brent_bound(stats, workers):
    """Brent's bound on the time with this many workers."""
    if workers < 1:
        raise ValueError("workers must be at least 1")
    return stats["work"] / workers + stats["span"]


rng = random.Random(7)
data = [rng.randrange(0, 20) for _ in range(1000)]
total, red_stats = reduce_tree(data)
scan, scan_stats = blelloch_scan(data)
print("sum:", total, red_stats)
print("scan:", scan_stats, "parallelism:", round(parallelism(scan_stats), 3))
print("matches sequential:", scan == sequential_scan(data))
'''}],
                "hints": [
                    "In `reduce_tree`, build the next level with `range(0, len(level) - 1, 2)` and then append the odd survivor with `if len(level) % 2`.",
                    "The up-sweep index pattern is `for i in range(stride * 2 - 1, size, stride * 2)` with `stride` doubling from 1 while `stride < size`.",
                    "The down-sweep is the same index pattern with `stride` halving from `size // 2`. Save the left child first: `left = buf[i - stride]`, then `buf[i - stride] = buf[i]`, then `buf[i] = op(left, buf[i])`.",
                    "`size.bit_length()` gives log2(size) + 1 for an exact power of two, so the span is `2 * size.bit_length() - 2`.",
                ],
                "tests": [
                    {"name": "next_power_of_two", "code": r'''
_want = {0: 1, 1: 1, 2: 2, 3: 4, 5: 8, 8: 8, 9: 16, 1000: 1024}
for _n, _w in _want.items():
    _got = next_power_of_two(_n)
    assert _got == _w, f"next_power_of_two({_n}) gave {_got!r}, expected {_w}"
'''},
                    {"name": "reduce_tree counts its own DAG", "code": r'''
_v, _s = reduce_tree(range(1, 101))
assert _v == 5050, f"reduce_tree(range(1, 101)) summed to {_v!r}, expected 5050"
assert _s == {"work": 99, "span": 7}, f"stats were {_s!r}, expected work 99 and span 7"
_v, _s = reduce_tree([1, 2, 3, 4, 5])
assert (_v, _s) == (15, {"work": 4, "span": 3}), f"Got {(_v, _s)!r}, expected (15, work 4, span 3)"
assert reduce_tree([], operator.add, 0) == (0, {"work": 0, "span": 0}), "Empty input returns the identity"
assert reduce_tree([42]) == (42, {"work": 0, "span": 0}), "One element needs no operation at all"
'''},
                    {"name": "reduce_tree keeps the operands in order", "code": r'''
_v, _s = reduce_tree(["a", "b", "c", "d", "e"], operator.add, "")
assert _v == "abcde", f"String concatenation gave {_v!r} — the tree must not reorder operands"
assert _s == {"work": 4, "span": 3}, f"stats were {_s!r}, expected work 4 and span 3"
'''},
                    {"name": "sequential_scan is exclusive", "code": r'''
assert sequential_scan([1, 2, 3, 4]) == [0, 1, 3, 6], f"Got {sequential_scan([1, 2, 3, 4])!r}"
assert sequential_scan([]) == [], "Empty input scans to []"
assert sequential_scan([9]) == [0], "A single element scans to just the identity"
assert sequential_scan([3, 1, 4, 1, 5], max, 0) == [0, 3, 3, 4, 4], \
    f"Running maximum gave {sequential_scan([3, 1, 4, 1, 5], max, 0)!r}"
'''},
                    {"name": "blelloch_scan matches the sequential reference", "code": r'''
import random as _random
_rng = _random.Random(13)
for _ in range(60):
    _n = _rng.randrange(0, 40)
    _v = [_rng.randrange(-20, 20) for _ in range(_n)]
    _got, _stats = blelloch_scan(_v)
    assert _got == sequential_scan(_v), f"Length {_n}: got {_got!r}, expected {sequential_scan(_v)!r}"
assert blelloch_scan([]) == ([], {"work": 0, "span": 0}), "Empty input"
assert blelloch_scan([9])[0] == [0], "One element scans to [identity]"
assert blelloch_scan([3, 1, 4, 1, 5], max, 0)[0] == [0, 3, 3, 4, 4], \
    "The scan must work for any associative operator with an identity"
'''},
                    {"name": "The instrumented DAG matches the closed form", "code": r'''
for _n in (1, 2, 3, 5, 8, 16, 100, 1000):
    _stats = blelloch_scan(list(range(_n)))[1]
    _want = scan_cost(_n)
    assert _stats == _want, f"n={_n}: measured {_stats!r} but scan_cost says {_want!r}"
assert scan_cost(8) == {"work": 14, "span": 6}, f"scan_cost(8) gave {scan_cost(8)!r}"
assert scan_cost(1000) == {"work": 2046, "span": 20}, f"scan_cost(1000) gave {scan_cost(1000)!r}"
assert scan_cost(0) == {"work": 0, "span": 0}, "n=0 costs nothing"
'''},
                    {"name": "parallelism and Brent's bound", "code": r'''
assert abs(parallelism({"work": 14, "span": 6}) - 7 / 3) < 1e-12, \
    f"parallelism gave {parallelism({'work': 14, 'span': 6})!r}, expected 2.3333333333333335"
assert parallelism({"work": 30, "span": 8}) == 3.75, "n=16 has parallelism 3.75"
assert parallelism({"work": 0, "span": 0}) == 0.0, "No span means no parallelism to report"
assert brent_bound({"work": 14, "span": 6}, 4) == 9.5, \
    f"brent_bound gave {brent_bound({'work': 14, 'span': 6}, 4)!r}, expected 9.5"
try:
    brent_bound({"work": 14, "span": 6}, 0)
    assert False, "brent_bound with 0 workers should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The demo run agrees with the reference", "code": r'''
assert "matches sequential: True" in _out, \
    "main.py should confirm the Blelloch scan equals the sequential scan"
assert "'work': 2046" in _out or '"work": 2046' in _out, \
    "main.py should print the measured scan stats for the 1000-element run"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Coordination, races and interleaving",
            "summary": "Enumerate every schedule of a small program and exhibit the losing one.",
            "concepts": [
                "A data race is a property of the *program*, not of the run that happened to expose it",
                "Read-modify-write is three operations; only their atomic composition is safe",
                "Sequential consistency: an execution is some interleaving of each thread's program order",
                "The state space of p threads of k steps has (pk)! / (k!)^p interleavings",
                "Mutual exclusion removes schedules; a blocked thread simply has no enabled transition",
                "Systematic exploration (model checking) beats stress testing: it either finds the bug or proves its absence",
                "Deadlock is a reachable state with no enabled transition and unfinished threads",
            ],
            "lab": {
                "title": "A deterministic interleaving explorer",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A tiny abstract machine: one shared `counter`, one private register per thread,
and a single lock. A *program* is a tuple of operation names.

```text
NAIVE  = ("load", "inc", "store")
LOCKED = ("lock", "load", "inc", "store", "unlock")
```

A **state** is `(counter, pcs, regs, owner)` — the shared counter, one program
counter and one register per thread, and the lock owner (`FREE`, which is `-1`,
when nobody holds it). `initial_state` and `is_finished` are given.

**`step(programs, state, tid)`** returns the state after thread `tid` executes
its next operation, or `None` when that thread cannot proceed — it has finished,
or it is waiting on the lock. `"load"` copies the counter into the register,
`"inc"` adds one to the register, `"store"` copies the register back,
`"lock"` succeeds only when the lock is free or already this thread's,
`"unlock"` succeeds only for the owner. An unknown operation name raises
`ValueError`. States are immutable — build a new tuple.

**`schedules(programs, counter=0)`** — a generator yielding `(schedule, final)`
for every feasible complete interleaving, where `schedule` is a tuple of thread
ids. Explore thread ids in ascending order so the enumeration is deterministic.
Abandon any path that reaches a state with no enabled transition and unfinished
threads (that is a deadlock, not a result).

**`outcomes(programs, counter=0)`** — the sorted distinct final counters.

**`count_schedules(programs, counter=0)`** — how many complete interleavings there are.

**`run_schedule(programs, schedule, counter=0)`** — replay one schedule and
return the final counter. Raise `ValueError` if a step is not enabled, and again
if the schedule ends before every thread has finished.

**`find_race(programs, expected, counter=0)`** — the first schedule whose final
counter is not `expected`, or `None` when every schedule agrees.

```text
outcomes([NAIVE, NAIVE])          -> [1, 2]      count_schedules -> 20
outcomes([NAIVE, NAIVE, NAIVE])   -> [1, 2, 3]   count_schedules -> 1680
outcomes([LOCKED, LOCKED])        -> [2]         count_schedules -> 2
find_race([NAIVE, NAIVE], 2)      -> (0, 0, 1, 0, 1, 1)
```

The last line is the whole lesson: two threads, three instructions each, and a
schedule that loses an increment.
''',
                "files": [{"name": "main.py", "content": r'''
NAIVE = ("load", "inc", "store")
LOCKED = ("lock", "load", "inc", "store", "unlock")
FREE = -1


def initial_state(programs, counter=0):
    """Fresh state: given counter, every pc at 0, every register 0, lock free."""
    return (counter, (0,) * len(programs), (0,) * len(programs), FREE)


def is_finished(programs, state):
    """True when every thread has run off the end of its program."""
    return all(pc == len(p) for pc, p in zip(state[1], programs))


def step(programs, state, tid):
    """State after thread tid runs one operation, or None when it cannot."""
    # your code here


def schedules(programs, counter=0):
    """Yield (schedule, final counter) for every feasible complete interleaving."""
    # your code here


def outcomes(programs, counter=0):
    """Sorted distinct final counter values."""
    # your code here


def count_schedules(programs, counter=0):
    """How many complete interleavings exist."""
    # your code here


def run_schedule(programs, schedule, counter=0):
    """Replay one schedule; ValueError when it is not a complete feasible one."""
    # your code here


def find_race(programs, expected, counter=0):
    """First schedule whose result is not expected, or None."""
    # your code here


print("naive outcomes:", outcomes([NAIVE, NAIVE]), count_schedules([NAIVE, NAIVE]))
print("locked outcomes:", outcomes([LOCKED, LOCKED]), count_schedules([LOCKED, LOCKED]))
print("race witness:", find_race([NAIVE, NAIVE], 2))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
NAIVE = ("load", "inc", "store")
LOCKED = ("lock", "load", "inc", "store", "unlock")
FREE = -1


def initial_state(programs, counter=0):
    """Fresh state: given counter, every pc at 0, every register 0, lock free."""
    return (counter, (0,) * len(programs), (0,) * len(programs), FREE)


def is_finished(programs, state):
    """True when every thread has run off the end of its program."""
    return all(pc == len(p) for pc, p in zip(state[1], programs))


def step(programs, state, tid):
    """State after thread tid runs one operation, or None when it cannot."""
    counter, pcs, regs, owner = state
    pc = pcs[tid]
    if pc >= len(programs[tid]):
        return None
    op = programs[tid][pc]
    regs = list(regs)
    pcs = list(pcs)
    if op == "load":
        regs[tid] = counter
    elif op == "inc":
        regs[tid] = regs[tid] + 1
    elif op == "store":
        counter = regs[tid]
    elif op == "lock":
        if owner not in (FREE, tid):
            return None
        owner = tid
    elif op == "unlock":
        if owner != tid:
            return None
        owner = FREE
    else:
        raise ValueError(f"unknown operation {op!r}")
    pcs[tid] = pc + 1
    return (counter, tuple(pcs), tuple(regs), owner)


def schedules(programs, counter=0):
    """Yield (schedule, final counter) for every feasible complete interleaving."""
    prefix = []

    def walk(state):
        if is_finished(programs, state):
            yield (tuple(prefix), state[0])
            return
        for tid in range(len(programs)):
            nxt = step(programs, state, tid)
            if nxt is None:
                continue
            prefix.append(tid)
            yield from walk(nxt)
            prefix.pop()

    yield from walk(initial_state(programs, counter))


def outcomes(programs, counter=0):
    """Sorted distinct final counter values."""
    return sorted({final for _, final in schedules(programs, counter)})


def count_schedules(programs, counter=0):
    """How many complete interleavings exist."""
    return sum(1 for _ in schedules(programs, counter))


def run_schedule(programs, schedule, counter=0):
    """Replay one schedule; ValueError when it is not a complete feasible one."""
    state = initial_state(programs, counter)
    for tid in schedule:
        nxt = step(programs, state, tid)
        if nxt is None:
            raise ValueError(f"thread {tid} is not enabled at this point in the schedule")
        state = nxt
    if not is_finished(programs, state):
        raise ValueError("the schedule does not run every thread to completion")
    return state[0]


def find_race(programs, expected, counter=0):
    """First schedule whose result is not expected, or None."""
    for schedule, final in schedules(programs, counter):
        if final != expected:
            return schedule
    return None


print("naive outcomes:", outcomes([NAIVE, NAIVE]), count_schedules([NAIVE, NAIVE]))
print("locked outcomes:", outcomes([LOCKED, LOCKED]), count_schedules([LOCKED, LOCKED]))
print("race witness:", find_race([NAIVE, NAIVE], 2))
'''}],
                "hints": [
                    "`step` must not mutate the state it is handed: copy `pcs` and `regs` into lists, change one entry, and rebuild the tuples.",
                    "Waiting on a lock is not an error — it is simply an absence of a transition. Return `None` and let the caller try another thread.",
                    "Write `schedules` as a recursive generator over a shared `prefix` list: append the thread id, `yield from` the recursive call, then pop.",
                    "`find_race` needs no extra machinery — walk `schedules` in order and return the first schedule whose final counter differs from `expected`.",
                ],
                "tests": [
                    {"name": "step implements the three operations", "code": r'''
_p = [NAIVE]
_s = initial_state(_p, 5)
_s = step(_p, _s, 0)
assert _s[2][0] == 5, f"after load the register is {_s[2][0]!r}, expected the counter value 5"
_s = step(_p, _s, 0)
assert _s[2][0] == 6, f"after inc the register is {_s[2][0]!r}, expected 6"
_s = step(_p, _s, 0)
assert _s[0] == 6, f"after store the counter is {_s[0]!r}, expected 6"
assert is_finished(_p, _s), "the thread has run all three operations"
assert step(_p, _s, 0) is None, "a finished thread has no next step"
'''},
                    {"name": "step leaves the state it was given alone", "code": r'''
_p = [NAIVE, NAIVE]
_s0 = initial_state(_p)
_s1 = step(_p, _s0, 0)
assert _s0 == (0, (0, 0), (0, 0), FREE), f"step mutated the input state: it is now {_s0!r}"
assert _s1[1] == (1, 0), f"only thread 0 advanced; pcs are {_s1[1]!r}"
try:
    step([("frobnicate",)], initial_state([("frobnicate",)]), 0)
    assert False, "an unknown operation should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The lock blocks rather than fails", "code": r'''
_p = [LOCKED, LOCKED]
_s = step(_p, initial_state(_p), 0)
assert _s is not None and _s[3] == 0, f"thread 0 should own the lock, owner is {_s[3]!r}"
assert step(_p, _s, 1) is None, "thread 1 must have no enabled transition while the lock is held"
_s2 = _s
for _ in range(3):
    _s2 = step(_p, _s2, 0)
_s2 = step(_p, _s2, 0)
assert _s2[3] == FREE, f"after unlock the owner is {_s2[3]!r}, expected FREE"
assert step(_p, _s2, 1) is not None, "with the lock free thread 1 can proceed"
'''},
                    {"name": "The naive counter loses increments", "code": r'''
assert outcomes([NAIVE, NAIVE]) == [1, 2], f"Got {outcomes([NAIVE, NAIVE])!r}, expected [1, 2]"
assert count_schedules([NAIVE, NAIVE]) == 20, \
    f"Got {count_schedules([NAIVE, NAIVE])!r} interleavings, expected 20"
assert outcomes([NAIVE, NAIVE, NAIVE]) == [1, 2, 3], f"Got {outcomes([NAIVE] * 3)!r}"
assert count_schedules([NAIVE, NAIVE, NAIVE]) == 1680, \
    f"Got {count_schedules([NAIVE] * 3)!r} interleavings, expected 1680"
assert outcomes([NAIVE], 10) == [11], "One thread on its own always adds exactly one"
'''},
                    {"name": "The lock removes every losing schedule", "code": r'''
assert outcomes([LOCKED, LOCKED]) == [2], f"Got {outcomes([LOCKED, LOCKED])!r}, expected [2]"
assert count_schedules([LOCKED, LOCKED]) == 2, \
    f"Got {count_schedules([LOCKED, LOCKED])!r} interleavings, expected 2"
assert outcomes([LOCKED, LOCKED, LOCKED]) == [3], f"Got {outcomes([LOCKED] * 3)!r}, expected [3]"
assert count_schedules([LOCKED, LOCKED, LOCKED]) == 6, \
    f"Got {count_schedules([LOCKED] * 3)!r} interleavings, expected 6"
assert outcomes([NAIVE, LOCKED]) == [1, 2], "One unlocked thread is enough to reintroduce the race"
'''},
                    {"name": "find_race produces a replayable witness", "code": r'''
_w = find_race([NAIVE, NAIVE], 2)
assert _w == (0, 0, 1, 0, 1, 1), f"Got witness {_w!r}, expected (0, 0, 1, 0, 1, 1)"
assert run_schedule([NAIVE, NAIVE], _w) == 1, \
    f"replaying the witness gave {run_schedule([NAIVE, NAIVE], _w)!r}, expected 1"
assert find_race([LOCKED, LOCKED], 2) is None, "the locked version has no losing schedule"
assert find_race([NAIVE], 1) is None, "a single thread cannot race with itself"
'''},
                    {"name": "run_schedule rejects impossible schedules", "code": r'''
assert run_schedule([NAIVE, NAIVE], (0, 0, 0, 1, 1, 1)) == 2, "the serial schedule adds both increments"
try:
    run_schedule([NAIVE, NAIVE], (0, 0, 0, 0))
    assert False, "a schedule that steps a finished thread should raise ValueError"
except ValueError:
    pass
try:
    run_schedule([NAIVE, NAIVE], (0, 0, 0))
    assert False, "a schedule that stops early should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Message passing and collective cost",
            "summary": "Build ring allreduce and a binomial broadcast, then audit the wire.",
            "concepts": [
                "Distributed memory has no shared address space: every datum moves by an explicit message",
                "The alpha-beta model: time = latency + bytes / bandwidth, per message",
                "Ring allreduce = reduce-scatter then allgather, 2(p-1) rounds of n/p elements each",
                "Its bandwidth cost 2(p-1)n/p per rank is optimal and independent of p as p grows",
                "Binomial-tree broadcast: p-1 messages in ceil(log2 p) rounds",
                "Latency-bound versus bandwidth-bound collectives, and why small messages need a different algorithm",
                "Instrumenting a simulated world is how you audit an implementation against its bound",
            ],
            "lab": {
                "title": "A simulated MPI world",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A `World` is a message counter, not a network. Every algorithm you write must
declare each message it sends, and the tests compare the total against the
analytic bound.

## `World(size, elem_bytes=8)`

Attributes `size`, `elem_bytes`, `messages`, `elements`, `rounds`, and `log`
(a list of `(src, dst, count)`). A read-only property `bytes_moved` returns
`elements * elem_bytes`.

- `send(src, dst, count)` — record one message of `count` elements. Raise
  `ValueError` for a rank outside `range(size)`, for `src == dst`, or for a
  negative `count`.
- `barrier()` — bump `rounds` by one. Call it once per communication round.

`World(0)` and a non-positive `elem_bytes` raise `ValueError`.

## `ring_allreduce(world, vectors)`

`vectors` is one list per rank, all the same length `n`, with `n` divisible by
`world.size`. Return one summed vector per rank (all equal).

Split each vector into `p` chunks of `n // p`. Run `p - 1` **reduce-scatter**
rounds: in round `s`, rank `r` sends chunk `(r - s) % p` to rank `(r + 1) % p`
and adds the chunk it receives into its own copy. Then `p - 1` **allgather**
rounds: in round `s`, rank `r` sends chunk `(r + 1 - s) % p` onward and
overwrites the chunk it receives. Every rank sends in a round *before* any rank
applies what it received — snapshot the outgoing chunks first.

Wrong vector count, ragged lengths and an indivisible length all raise `ValueError`.

## `broadcast_tree(world, root, value)`

`value` is a list. Return a list of `world.size` copies. Work in ranks relative
to `root`: with `mask` doubling from 1 while `mask < p`, every relative rank
below `mask` sends to relative rank `rel + mask` when that is in range. One
`barrier()` per mask. An out-of-range `root` raises `ValueError`.

## The bounds

```text
allreduce_bytes_bound(p, n, elem_bytes=8)  ->  2 * (p - 1) * n * elem_bytes
broadcast_bytes_bound(p, n, elem_bytes=8)  ->  (p - 1) * n * elem_bytes
broadcast_rounds(p)                        ->  ceil(log2(p))
```

`p` below 1 raises `ValueError`. With `p = 4`, `n = 8` and 8-byte elements the
allreduce must send exactly 24 messages and 384 bytes — the bound, to the byte.
''',
                "files": [{"name": "main.py", "content": r'''
import random


class World:
    """A message counter standing in for an MPI communicator."""

    def __init__(self, size, elem_bytes=8):
        # your code here
        pass

    @property
    def bytes_moved(self):
        """elements * elem_bytes."""
        # your code here

    def send(self, src, dst, count):
        """Record one message of count elements from src to dst."""
        # your code here

    def barrier(self):
        """Mark the end of one communication round."""
        # your code here


def ring_allreduce(world, vectors):
    """Reduce-scatter then allgather; returns the summed vector for every rank."""
    # your code here


def broadcast_tree(world, root, value):
    """Binomial-tree broadcast; returns what every rank ends up holding."""
    # your code here


def allreduce_bytes_bound(p, n, elem_bytes=8):
    """Bytes a ring allreduce must move in total."""
    # your code here


def broadcast_bytes_bound(p, n, elem_bytes=8):
    """Bytes a broadcast must move in total."""
    # your code here


def broadcast_rounds(p):
    """ceil(log2(p)) rounds."""
    # your code here


rng = random.Random(7)
P, N = 4, 8
world = World(P)
vectors = [[rng.randrange(0, 10) for _ in range(N)] for _ in range(P)]
result = ring_allreduce(world, vectors)
print("all ranks agree:", all(r == result[0] for r in result))
print(f"messages: {world.messages}  bytes: {world.bytes_moved}  "
      f"bound: {allreduce_bytes_bound(P, N)}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import random


class World:
    """A message counter standing in for an MPI communicator."""

    def __init__(self, size, elem_bytes=8):
        if size < 1:
            raise ValueError("world size must be at least 1")
        if elem_bytes < 1:
            raise ValueError("elem_bytes must be at least 1")
        self.size = size
        self.elem_bytes = elem_bytes
        self.messages = 0
        self.elements = 0
        self.rounds = 0
        self.log = []

    @property
    def bytes_moved(self):
        """elements * elem_bytes."""
        return self.elements * self.elem_bytes

    def send(self, src, dst, count):
        """Record one message of count elements from src to dst."""
        if not 0 <= src < self.size or not 0 <= dst < self.size:
            raise ValueError(f"rank out of range: {src} -> {dst}")
        if src == dst:
            raise ValueError("a rank must not send to itself")
        if count < 0:
            raise ValueError("count must not be negative")
        self.messages += 1
        self.elements += count
        self.log.append((src, dst, count))

    def barrier(self):
        """Mark the end of one communication round."""
        self.rounds += 1


def ring_allreduce(world, vectors):
    """Reduce-scatter then allgather; returns the summed vector for every rank."""
    p = world.size
    if len(vectors) != p:
        raise ValueError(f"expected {p} vectors, got {len(vectors)}")
    n = len(vectors[0])
    if any(len(v) != n for v in vectors):
        raise ValueError("every rank must contribute the same length")
    if n % p:
        raise ValueError(f"vector length {n} is not divisible by world size {p}")
    bufs = [list(v) for v in vectors]
    chunk = n // p
    for stage in range(p - 1):
        outgoing = []
        for r in range(p):
            c = (r - stage) % p
            outgoing.append(bufs[r][c * chunk:(c + 1) * chunk])
            world.send(r, (r + 1) % p, chunk)
        for r in range(p):
            src = (r - 1) % p
            base = ((src - stage) % p) * chunk
            piece = outgoing[src]
            for i in range(chunk):
                bufs[r][base + i] += piece[i]
        world.barrier()
    for stage in range(p - 1):
        outgoing = []
        for r in range(p):
            c = (r + 1 - stage) % p
            outgoing.append(bufs[r][c * chunk:(c + 1) * chunk])
            world.send(r, (r + 1) % p, chunk)
        for r in range(p):
            src = (r - 1) % p
            c = (src + 1 - stage) % p
            bufs[r][c * chunk:(c + 1) * chunk] = outgoing[src]
        world.barrier()
    return bufs


def broadcast_tree(world, root, value):
    """Binomial-tree broadcast; returns what every rank ends up holding."""
    p = world.size
    if not 0 <= root < p:
        raise ValueError(f"root {root} is not a rank in this world")
    count = len(value)
    held = [None] * p
    held[root] = list(value)
    mask = 1
    while mask < p:
        for rel in range(mask):
            dst_rel = rel + mask
            if dst_rel < p:
                src = (rel + root) % p
                dst = (dst_rel + root) % p
                world.send(src, dst, count)
                held[dst] = list(held[src])
        world.barrier()
        mask *= 2
    return held


def allreduce_bytes_bound(p, n, elem_bytes=8):
    """Bytes a ring allreduce must move in total."""
    if p < 1:
        raise ValueError("p must be at least 1")
    return 2 * (p - 1) * n * elem_bytes


def broadcast_bytes_bound(p, n, elem_bytes=8):
    """Bytes a broadcast must move in total."""
    if p < 1:
        raise ValueError("p must be at least 1")
    return (p - 1) * n * elem_bytes


def broadcast_rounds(p):
    """ceil(log2(p)) rounds."""
    if p < 1:
        raise ValueError("p must be at least 1")
    return (p - 1).bit_length()


rng = random.Random(7)
P, N = 4, 8
world = World(P)
vectors = [[rng.randrange(0, 10) for _ in range(N)] for _ in range(P)]
result = ring_allreduce(world, vectors)
print("all ranks agree:", all(r == result[0] for r in result))
print(f"messages: {world.messages}  bytes: {world.bytes_moved}  "
      f"bound: {allreduce_bytes_bound(P, N)}")
'''}],
                "hints": [
                    "`bytes_moved` is a `@property`, so it recomputes from `elements` every time you read it — never store it.",
                    "Snapshot before you apply: build the whole `outgoing` list for the round first, then run a second loop that adds or overwrites. Applying inside the send loop lets a rank forward data it only just received.",
                    "In reduce-scatter round `s`, rank `r` receives from `(r - 1) % p` the chunk that rank sent, which is `((r - 1 - s) % p)`. Index it from the sender, not from the receiver.",
                    "`(p - 1).bit_length()` is exactly ceil(log2(p)) for p >= 1, and gives 0 for a world of one.",
                ],
                "tests": [
                    {"name": "World validates and accounts", "code": r'''
_w = World(4)
assert (_w.messages, _w.elements, _w.bytes_moved, _w.rounds) == (0, 0, 0, 0), "a fresh world is quiet"
_w.send(0, 1, 5)
_w.send(1, 2, 3)
assert _w.messages == 2 and _w.elements == 8, f"Got {_w.messages} messages, {_w.elements} elements"
assert _w.bytes_moved == 64, f"bytes_moved gave {_w.bytes_moved!r}, expected 64"
assert _w.log == [(0, 1, 5), (1, 2, 3)], f"log is {_w.log!r}"
_w.barrier()
assert _w.rounds == 1, f"rounds is {_w.rounds!r}, expected 1"
assert World(4, 4).bytes_moved == 0 and World(2).elem_bytes == 8, "elem_bytes defaults to 8"
'''},
                    {"name": "World rejects impossible sends", "code": r'''
for _bad in (0, -3):
    try:
        World(_bad)
        assert False, f"World({_bad}) should raise ValueError"
    except ValueError:
        pass
try:
    World(4, 0)
    assert False, "World(4, 0) should raise ValueError"
except ValueError:
    pass
_w = World(3)
for _args in [(1, 1, 4), (0, 3, 4), (-1, 2, 4), (0, 1, -2)]:
    try:
        _w.send(*_args)
        assert False, f"send{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "ring_allreduce sums every element", "code": r'''
import random as _random
for _p, _n in [(1, 4), (2, 4), (4, 8), (4, 4), (5, 10), (8, 16)]:
    _rng = _random.Random(3)
    _w = World(_p)
    _vecs = [[_rng.randrange(0, 10) for _ in range(_n)] for _ in range(_p)]
    _want = [sum(v[i] for v in _vecs) for i in range(_n)]
    _got = ring_allreduce(_w, _vecs)
    assert len(_got) == _p, f"p={_p}: got {len(_got)} results, expected {_p}"
    for _r, _res in enumerate(_got):
        assert _res == _want, f"p={_p} rank {_r} holds {_res!r}, expected {_want!r}"
'''},
                    {"name": "ring_allreduce hits the bandwidth bound exactly", "code": r'''
_w = World(4)
ring_allreduce(_w, [[1] * 8 for _ in range(4)])
assert _w.messages == 24, f"p=4 sent {_w.messages} messages, expected 2*p*(p-1) = 24"
assert _w.bytes_moved == 384, f"p=4 moved {_w.bytes_moved} bytes, expected 384"
assert _w.bytes_moved == allreduce_bytes_bound(4, 8), "the measurement must equal the bound"
assert _w.rounds == 6, f"p=4 used {_w.rounds} rounds, expected 2*(p-1) = 6"
_w1 = World(1)
assert ring_allreduce(_w1, [[1, 2, 3]]) == [[1, 2, 3]], "one rank needs no messages at all"
assert _w1.messages == 0 and allreduce_bytes_bound(1, 3) == 0, "and moves no bytes"
_w8 = World(8)
ring_allreduce(_w8, [[1] * 16 for _ in range(8)])
assert _w8.bytes_moved == allreduce_bytes_bound(8, 16) == 1792, \
    f"p=8 moved {_w8.bytes_moved} bytes, expected 1792"
'''},
                    {"name": "ring_allreduce rejects bad input", "code": r'''
try:
    ring_allreduce(World(4), [[1, 2, 3, 4]] * 3)
    assert False, "too few vectors should raise ValueError"
except ValueError:
    pass
try:
    ring_allreduce(World(2), [[1, 2], [1, 2, 3]])
    assert False, "ragged vectors should raise ValueError"
except ValueError:
    pass
try:
    ring_allreduce(World(4), [[1, 2, 3]] * 4)
    assert False, "a length not divisible by p should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "broadcast_tree reaches every rank once", "code": r'''
for _p in (1, 2, 3, 4, 5, 8):
    _w = World(_p)
    _held = broadcast_tree(_w, 0, [1.0, 2.0, 3.0])
    assert _held == [[1.0, 2.0, 3.0]] * _p, f"p={_p}: ranks hold {_held!r}"
    assert _w.messages == _p - 1, f"p={_p} sent {_w.messages} messages, expected {_p - 1}"
    assert _w.bytes_moved == broadcast_bytes_bound(_p, 3), \
        f"p={_p} moved {_w.bytes_moved} bytes, expected {broadcast_bytes_bound(_p, 3)}"
    assert _w.rounds == broadcast_rounds(_p), \
        f"p={_p} used {_w.rounds} rounds, expected {broadcast_rounds(_p)}"
_w = World(4)
_held = broadcast_tree(_w, 2, [7.0])
assert _held == [[7.0]] * 4, f"a non-zero root should still reach everyone: {_held!r}"
assert _w.messages == 3, f"root=2 sent {_w.messages} messages, expected 3"
try:
    broadcast_tree(World(4), 4, [1.0])
    assert False, "an out-of-range root should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The closed-form bounds", "code": r'''
assert broadcast_rounds(1) == 0, "one rank needs no rounds"
for _p, _want in [(2, 1), (3, 2), (4, 2), (5, 3), (8, 3), (9, 4), (16, 4)]:
    assert broadcast_rounds(_p) == _want, f"broadcast_rounds({_p}) gave {broadcast_rounds(_p)!r}, expected {_want}"
assert allreduce_bytes_bound(4, 8) == 384 and broadcast_bytes_bound(4, 8) == 192, \
    "the allreduce moves exactly twice the bytes of the broadcast"
assert allreduce_bytes_bound(4, 8, 4) == 192, "elem_bytes scales the bound linearly"
for _fn in (allreduce_bytes_bound, broadcast_bytes_bound, broadcast_rounds):
    try:
        _fn(0, 8) if _fn is not broadcast_rounds else _fn(0)
        assert False, f"{_fn.__name__} should raise ValueError for p=0"
    except ValueError:
        pass
assert "all ranks agree: True" in _out, "main.py should report that every rank ends with the same vector"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an optimisation study with an Amdahl account",
        "runtime": "python",
        "minutes": 240,
        "brief": r'''
You are handed a working but slow kernel and asked to make it fast *and* to say
exactly why each stage helped. `kernel.py` holds the logic and is what the
checks import; `main.py` is the study — it prints the speedup table and the
serial fraction the measurement implies.

## The kernel

A three-point weighted stencil applied `steps` times to a signal of `n` floats,
with the two end samples held fixed:

```text
y[0]   = x[0]
y[n-1] = x[n-1]
y[i]   = w0*x[i-1] + w1*x[i] + w2*x[i+1]      for 1 <= i <= n-2
```

`build_operator(n, weights)` and `stencil_v0` are **given**. `v0` rebuilds the
dense n x n operator matrix on every step and does a full matrix-vector product:
O(steps * n^2) time and O(steps * n^2) allocation.

## The stages

Each stage must return a result **bit-for-bit identical** to `stencil_v0`. That
is achievable, and it is the discipline the whole exercise rests on: keep the
three products in the order `w0*left + w1*centre + w2*right`, and adding the
exact zeros of the dense row changes nothing.

- **`stencil_v1`** — hoist the matrix build out of the step loop. Same
  arithmetic, one call to `build_operator` instead of `steps` calls.
- **`stencil_v2`** — drop the matrix. Touch only the three band entries, so the
  cost falls from O(n^2) to O(n) per step.
- **`stencil_v3`** — `v2` plus two allocated buffers swapped each step (no list
  is built inside the loop) and the three samples carried in local registers
  `a, b, c` so each element is read from the list once.

All four raise `ValueError` for `n < 2` or a negative `steps`, and return a copy
of the input for `steps == 0`.

## The analysis

- **`time_stages(x, weights, steps, repeats=1)`** — `{stage: best seconds}` for
  all four, minimum of `repeats` runs. `repeats < 1` raises `ValueError`.
- **`speedup_table(timings, baseline="v0")`** — a list of
  `{"stage", "seconds", "speedup"}` in `STAGES` order, `speedup = t_baseline / t_stage`.
  An unknown baseline raises `ValueError`.
- **`amdahl_speedup(serial_fraction, workers)`** — `1 / (s + (1-s)/w)`.
- **`serial_fraction_from_speedup(speedup, workers)`** — invert it:
  `(1/S - 1/w) / (1 - 1/w)`. `workers <= 1` cannot identify `s`, so raise
  `ValueError`; so does a non-positive speedup.
- **`max_speedup(serial_fraction)`** — `1/s`, and `inf` when `s` is 0.

A serial fraction outside `[0, 1]` or fewer than one worker raises `ValueError`.

## What the study should say

The interesting number is not the raw speedup. It is that once `v3` has removed
the O(n^2) term, whatever is left that does not shrink — the loop overhead, the
boundary handling, the buffer swap — is the serial fraction that caps everything
you do next.
''',
        "deliverables": [
            "`kernel.py` — `stencil_v1`, `v2`, `v3` returning results identical to `stencil_v0`",
            "`kernel.py` — the timing harness, the speedup table and the three Amdahl functions",
            "`main.py` — a study that prints a stage/seconds/speedup table for a real signal",
            "`main.py` — the serial fraction implied by the best measured speedup, and the ceiling it sets",
            "Input validation: `n < 2`, negative `steps`, bad baselines and impossible worker counts all raise `ValueError`",
            "Evidence that every stage is bit-for-bit equal to the supplied kernel, not merely close",
        ],
        "constraints": [
            "Standard library only; `time` and `random` are the only imports you need",
            "`kernel.py` must define names only — importing it must print nothing",
            "No stage may call another stage: each one is a self-contained implementation",
            "Only `stencil_v0` and `stencil_v1` may call `build_operator`; `v2` and `v3` must never build a matrix",
            "Timings come from `time.perf_counter` and report the minimum, never the mean",
        ],
        "rubric": [
            {"criterion": "Numerical fidelity", "weight": 30,
             "evidence": "Every stage returns exactly the same list as stencil_v0 for even, odd, minimal and zero-step cases."},
            {"criterion": "Optimisation quality", "weight": 25,
             "evidence": "v1 calls build_operator once; v2 and v3 never build a matrix and are measurably an order of magnitude faster than v0."},
            {"criterion": "Measurement method", "weight": 20,
             "evidence": "time_stages repeats and reports the minimum; the speedup table is derived from the baseline rather than hand-written."},
            {"criterion": "Amdahl analysis", "weight": 15,
             "evidence": "The forward and inverse laws round-trip, and main.py states the serial fraction and the ceiling it implies."},
            {"criterion": "Interface discipline", "weight": 10,
             "evidence": "kernel.py is import-clean, every documented ValueError is raised, and no stage delegates to another."},
        ],
        "hints": [
            "Start by copying `stencil_v0` into `stencil_v1` and moving the single `build_operator` line above the `for _ in range(steps)` loop. Nothing else changes.",
            "For `v2`, write the boundaries first (`nxt[0] = cur[0]`, `nxt[n-1] = cur[n-1]`) and then loop `for i in range(1, n - 1)`. Bind `w0, w1, w2 = weights` outside the step loop.",
            "For `v3`, allocate `cur` and `nxt` once, and end each step with `cur, nxt = nxt, cur`. Return `list(cur)` so the caller cannot see your scratch buffer.",
            "The register roll is `a = cur[0]; b = cur[1]`, then inside the loop `c = cur[i + 1]`, write the element, and finish with `a = b; b = c`.",
            "Invert Amdahl algebraically before you code it: from `S = 1/(s + (1-s)/w)` you get `1/S = s(1 - 1/w) + 1/w`, hence `s = (1/S - 1/w) / (1 - 1/w)`.",
        ],
        "files": [
            {"name": "kernel.py", "content": r'''
import random
import time

STAGES = ("v0", "v1", "v2", "v3")


def make_signal(n, seed=7):
    """A deterministic test signal of n samples in [-1, 1]."""
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def build_operator(n, weights):
    """The dense n x n stencil matrix, with identity rows at both ends."""
    w0, w1, w2 = weights
    m = [[0.0] * n for _ in range(n)]
    m[0][0] = 1.0
    m[n - 1][n - 1] = 1.0
    for i in range(1, n - 1):
        m[i][i - 1] = w0
        m[i][i] = w1
        m[i][i + 1] = w2
    return m


def stencil_v0(x, weights, steps):
    """Supplied baseline: rebuild the dense operator every step."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    cur = list(x)
    for _ in range(steps):
        m = build_operator(n, weights)
        nxt = [0.0] * n
        for i in range(n):
            row = m[i]
            total = 0.0
            for j in range(n):
                total += row[j] * cur[j]
            nxt[i] = total
        cur = nxt
    return cur


def stencil_v1(x, weights, steps):
    """Stage 1: build the operator once."""
    # your code here


def stencil_v2(x, weights, steps):
    """Stage 2: touch only the band."""
    # your code here


def stencil_v3(x, weights, steps):
    """Stage 3: ping-pong buffers and rolling registers."""
    # your code here


STAGE_FUNCTIONS = {"v0": stencil_v0, "v1": stencil_v1,
                   "v2": stencil_v2, "v3": stencil_v3}


def time_stages(x, weights, steps, repeats=1):
    """{stage: best elapsed seconds} for every stage."""
    # your code here


def speedup_table(timings, baseline="v0"):
    """Rows of {"stage", "seconds", "speedup"} in STAGES order."""
    # your code here


def amdahl_speedup(serial_fraction, workers):
    """Amdahl's law: the speedup this serial fraction allows."""
    # your code here


def serial_fraction_from_speedup(speedup, workers):
    """The serial fraction a measured speedup implies."""
    # your code here


def max_speedup(serial_fraction):
    """The ceiling as the worker count goes to infinity."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from kernel import (STAGES, make_signal, stencil_v0, stencil_v1, stencil_v2,
                    stencil_v3, time_stages, speedup_table, amdahl_speedup,
                    serial_fraction_from_speedup, max_speedup)

WEIGHTS = (0.25, 0.5, 0.25)
STEPS = 6
SIGNAL = make_signal(200)

# 1. confirm every stage is bit-for-bit equal to stencil_v0
# 2. time the stages and print a stage / seconds / speedup table
# 3. print the serial fraction the best speedup implies, and its ceiling
print("study not written yet")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "kernel.py", "content": r'''
import random
import time

STAGES = ("v0", "v1", "v2", "v3")


def make_signal(n, seed=7):
    """A deterministic test signal of n samples in [-1, 1]."""
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def build_operator(n, weights):
    """The dense n x n stencil matrix, with identity rows at both ends."""
    w0, w1, w2 = weights
    m = [[0.0] * n for _ in range(n)]
    m[0][0] = 1.0
    m[n - 1][n - 1] = 1.0
    for i in range(1, n - 1):
        m[i][i - 1] = w0
        m[i][i] = w1
        m[i][i + 1] = w2
    return m


def stencil_v0(x, weights, steps):
    """Supplied baseline: rebuild the dense operator every step."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    cur = list(x)
    for _ in range(steps):
        m = build_operator(n, weights)
        nxt = [0.0] * n
        for i in range(n):
            row = m[i]
            total = 0.0
            for j in range(n):
                total += row[j] * cur[j]
            nxt[i] = total
        cur = nxt
    return cur


def stencil_v1(x, weights, steps):
    """Stage 1: build the operator once."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    cur = list(x)
    if steps == 0:
        return cur
    m = build_operator(n, weights)
    for _ in range(steps):
        nxt = [0.0] * n
        for i in range(n):
            row = m[i]
            total = 0.0
            for j in range(n):
                total += row[j] * cur[j]
            nxt[i] = total
        cur = nxt
    return cur


def stencil_v2(x, weights, steps):
    """Stage 2: touch only the band."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    w0, w1, w2 = weights
    cur = list(x)
    for _ in range(steps):
        nxt = [0.0] * n
        nxt[0] = cur[0]
        nxt[n - 1] = cur[n - 1]
        for i in range(1, n - 1):
            nxt[i] = w0 * cur[i - 1] + w1 * cur[i] + w2 * cur[i + 1]
        cur = nxt
    return cur


def stencil_v3(x, weights, steps):
    """Stage 3: ping-pong buffers and rolling registers."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    w0, w1, w2 = weights
    cur = list(x)
    nxt = list(x)
    for _ in range(steps):
        a = cur[0]
        b = cur[1]
        nxt[0] = a
        for i in range(1, n - 1):
            c = cur[i + 1]
            nxt[i] = w0 * a + w1 * b + w2 * c
            a = b
            b = c
        nxt[n - 1] = cur[n - 1]
        cur, nxt = nxt, cur
    return list(cur)


STAGE_FUNCTIONS = {"v0": stencil_v0, "v1": stencil_v1,
                   "v2": stencil_v2, "v3": stencil_v3}


MIN_SAMPLE = 0.005   # seconds; must clear the platform timer's resolution


def time_stages(x, weights, steps, repeats=1):
    """{stage: best per-call seconds} for every stage.

    A single call to a fast stage can finish inside one tick of the clock, and
    browser timers are deliberately coarse. Measuring that gives 0.0 seconds and
    an infinite speedup. So auto-range like timeit does: keep multiplying the
    number of calls until the batch takes longer than MIN_SAMPLE, then divide.
    """
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    timings = {}
    for name in STAGES:
        fn = STAGE_FUNCTIONS[name]
        best = None
        for _ in range(repeats):
            calls = 1
            while True:
                start = time.perf_counter()
                for _ in range(calls):
                    fn(x, weights, steps)
                elapsed = time.perf_counter() - start
                if elapsed >= MIN_SAMPLE or calls >= 8192:
                    break
                calls *= 4
            per_call = elapsed / calls
            if best is None or per_call < best:
                best = per_call
        timings[name] = best
    return timings


def speedup_table(timings, baseline="v0"):
    """Rows of {"stage", "seconds", "speedup"} in STAGES order."""
    if baseline not in timings:
        raise ValueError(f"no timing for baseline stage {baseline!r}")
    base = timings[baseline]
    rows = []
    for name in STAGES:
        if name in timings:
            seconds = timings[name]
            rows.append({"stage": name, "seconds": seconds,
                         "speedup": base / seconds if seconds > 0 else float("inf")})
    return rows


def amdahl_speedup(serial_fraction, workers):
    """Amdahl's law: the speedup this serial fraction allows."""
    if not 0.0 <= serial_fraction <= 1.0:
        raise ValueError("serial_fraction must lie in [0, 1]")
    if workers < 1:
        raise ValueError("workers must be at least 1")
    return 1.0 / (serial_fraction + (1.0 - serial_fraction) / workers)


def serial_fraction_from_speedup(speedup, workers):
    """The serial fraction a measured speedup implies."""
    if workers <= 1:
        raise ValueError("workers must exceed 1 to identify a serial fraction")
    if speedup <= 0:
        raise ValueError("speedup must be positive")
    return (1.0 / speedup - 1.0 / workers) / (1.0 - 1.0 / workers)


def max_speedup(serial_fraction):
    """The ceiling as the worker count goes to infinity."""
    if not 0.0 <= serial_fraction <= 1.0:
        raise ValueError("serial_fraction must lie in [0, 1]")
    if serial_fraction == 0.0:
        return float("inf")
    return 1.0 / serial_fraction
'''},
            {"name": "main.py", "content": r'''
from kernel import (STAGES, make_signal, stencil_v0, stencil_v1, stencil_v2,
                    stencil_v3, time_stages, speedup_table, amdahl_speedup,
                    serial_fraction_from_speedup, max_speedup)

WEIGHTS = (0.25, 0.5, 0.25)
STEPS = 6
SIGNAL = make_signal(200)

reference = stencil_v0(SIGNAL, WEIGHTS, STEPS)
identical = all(fn(SIGNAL, WEIGHTS, STEPS) == reference
                for fn in (stencil_v1, stencil_v2, stencil_v3))
print("all stages bit-identical:", identical)

timings = time_stages(SIGNAL, WEIGHTS, STEPS, repeats=3)
print(f"{'stage':<8}{'seconds':>12}{'speedup':>12}")
for row in speedup_table(timings):
    print(f"{row['stage']:<8}{row['seconds']:>12.6f}{row['speedup']:>12.2f}")

best = max(speedup_table(timings), key=lambda row: row["speedup"])
workers = 4
serial = serial_fraction_from_speedup(min(best["speedup"], float(workers)), workers)
serial = max(serial, 0.0)
print(f"implied serial fraction at {workers} workers: {serial:.4f}")
print(f"ceiling from that fraction: {max_speedup(serial):.2f}x")
print(f"predicted speedup at 64 workers: {amdahl_speedup(serial, 64):.2f}x")
'''},
        ],
        "tests": [
            {"name": "Every stage is bit-for-bit equal to the baseline", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
for _n, _steps in [(2, 3), (3, 4), (5, 0), (5, 1), (9, 7), (40, 5), (61, 2)]:
    _x = _kernel.make_signal(_n)
    _want = _kernel.stencil_v0(_x, _w, _steps)
    for _name in ("v1", "v2", "v3"):
        _got = _kernel.STAGE_FUNCTIONS[_name](_x, _w, _steps)
        assert _got == _want, f"stencil_{_name} differs from stencil_v0 at n={_n}, steps={_steps}"
'''},
            {"name": "Stages leave the input alone and copy the output", "code": r'''
import kernel as _kernel
_w = (0.3, 0.4, 0.3)
_x = _kernel.make_signal(12)
_before = list(_x)
for _name in ("v1", "v2", "v3"):
    _out1 = _kernel.STAGE_FUNCTIONS[_name](_x, _w, 5)
    assert _x == _before, f"stencil_{_name} modified the input signal in place"
    _out1[0] = 999.0
    _out2 = _kernel.STAGE_FUNCTIONS[_name](_x, _w, 5)
    assert _out2[0] != 999.0, f"stencil_{_name} handed back a buffer it still owns"
assert _kernel.stencil_v3(_x, _w, 0) == list(_x), "zero steps returns a copy of the input"
'''},
            {"name": "Stages validate their arguments", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
for _name in ("v0", "v1", "v2", "v3"):
    _fn = _kernel.STAGE_FUNCTIONS[_name]
    try:
        _fn([1.0], _w, 3)
        assert False, f"stencil_{_name} should raise ValueError for a one-sample signal"
    except ValueError:
        pass
    try:
        _fn([1.0, 2.0, 3.0], _w, -1)
        assert False, f"stencil_{_name} should raise ValueError for negative steps"
    except ValueError:
        pass
try:
    _kernel.make_signal(1)
    assert False, "make_signal(1) should raise ValueError"
except ValueError:
    pass
assert _kernel.make_signal(6) == _kernel.make_signal(6), "make_signal must be deterministic"
'''},
            {"name": "v1 builds the operator once; v2 and v3 never build it", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
_x = _kernel.make_signal(20)
_real = _kernel.build_operator
_calls = []
def _spy(n, weights):
    _calls.append(n)
    return _real(n, weights)
_kernel.build_operator = _spy
try:
    _calls.clear()
    _kernel.stencil_v0(_x, _w, 5)
    _v0_calls = len(_calls)
    _calls.clear()
    _kernel.stencil_v1(_x, _w, 5)
    _v1_calls = len(_calls)
    _calls.clear()
    _kernel.stencil_v2(_x, _w, 5)
    _kernel.stencil_v3(_x, _w, 5)
    _band_calls = len(_calls)
finally:
    _kernel.build_operator = _real
assert _v0_calls == 5, f"the baseline should build the matrix 5 times, it built it {_v0_calls}"
assert _v1_calls == 1, f"stencil_v1 built the matrix {_v1_calls} times, expected exactly 1"
assert _band_calls == 0, f"v2 and v3 built a matrix {_band_calls} times; they must touch only the band"
'''},
            {"name": "No stage delegates to another", "code": r'''
import inspect as _inspect
import kernel as _kernel
for _name in ("v1", "v2", "v3"):
    _src = _inspect.getsource(_kernel.STAGE_FUNCTIONS[_name])
    for _other in ("stencil_v0", "stencil_v1", "stencil_v2", "stencil_v3"):
        if _other.endswith(_name):
            continue
        assert _other not in _src, f"stencil_{_name} calls {_other} — each stage stands alone"
'''},
            {"name": "time_stages measures all four stages", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
_x = _kernel.make_signal(200)
_timings = _kernel.time_stages(_x, _w, 6)
assert set(_timings) == set(_kernel.STAGES), f"time_stages returned keys {sorted(_timings)!r}"
for _k, _v in _timings.items():
    assert isinstance(_v, float) and _v > 0.0, f"timing for {_k} was {_v!r}, expected a positive float"
try:
    _kernel.time_stages(_x, _w, 6, 0)
    assert False, "time_stages with repeats=0 should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The band stages really are an order of magnitude faster", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
_x = _kernel.make_signal(200)
_timings = _kernel.time_stages(_x, _w, 6, repeats=2)
_rows = {_r["stage"]: _r["speedup"] for _r in _kernel.speedup_table(_timings)}
assert _rows["v2"] > 5.0, f"v2 was only {_rows['v2']:.2f}x faster than v0 — it is still O(n^2)"
assert _rows["v3"] > 5.0, f"v3 was only {_rows['v3']:.2f}x faster than v0"
'''},
            {"name": "speedup_table shape and baseline", "code": r'''
import kernel as _kernel
_fake = {"v0": 0.8, "v1": 0.4, "v2": 0.1, "v3": 0.05}
_rows = _kernel.speedup_table(_fake)
assert [_r["stage"] for _r in _rows] == list(_kernel.STAGES), f"rows came back as {_rows!r}"
assert _rows[0]["speedup"] == 1.0, "the baseline row must have speedup 1.0"
assert abs(_rows[2]["speedup"] - 8.0) < 1e-12, f"v2 speedup was {_rows[2]['speedup']!r}, expected 8.0"
_rows2 = _kernel.speedup_table(_fake, baseline="v2")
assert abs(_rows2[0]["speedup"] - 0.125) < 1e-12, f"with baseline v2, v0 should be 0.125x"
try:
    _kernel.speedup_table(_fake, baseline="v9")
    assert False, "an unknown baseline should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Amdahl, forward", "code": r'''
import kernel as _kernel
_got = _kernel.amdahl_speedup(0.1, 8)
assert abs(_got - 80 / 17) < 1e-12, f"amdahl_speedup(0.1, 8) gave {_got!r}, expected 4.705882352941176"
assert _kernel.amdahl_speedup(0.0, 8) == 8.0, "a perfectly parallel program scales linearly"
assert _kernel.amdahl_speedup(1.0, 8) == 1.0, "a wholly serial program does not scale at all"
assert _kernel.amdahl_speedup(0.25, 1) == 1.0, "one worker is never faster than one worker"
for _bad in [(-0.1, 8), (1.5, 8), (0.5, 0)]:
    try:
        _kernel.amdahl_speedup(*_bad)
        assert False, f"amdahl_speedup{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Amdahl, inverted", "code": r'''
import kernel as _kernel
_s = _kernel.serial_fraction_from_speedup(6.4, 16)
assert abs(_s - 0.1) < 1e-12, f"serial_fraction_from_speedup(6.4, 16) gave {_s!r}, expected 0.1"
for _sf, _wk in [(0.05, 8), (0.2, 32), (0.5, 4)]:
    _round = _kernel.serial_fraction_from_speedup(_kernel.amdahl_speedup(_sf, _wk), _wk)
    assert abs(_round - _sf) < 1e-9, f"round trip at s={_sf}, w={_wk} gave {_round!r}"
for _bad in [(4.0, 1), (4.0, 0), (0.0, 8), (-2.0, 8)]:
    try:
        _kernel.serial_fraction_from_speedup(*_bad)
        assert False, f"serial_fraction_from_speedup{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "max_speedup is the ceiling", "code": r'''
import kernel as _kernel
assert _kernel.max_speedup(0.05) == 20.0, f"max_speedup(0.05) gave {_kernel.max_speedup(0.05)!r}"
assert _kernel.max_speedup(1.0) == 1.0, "an entirely serial program has a ceiling of 1"
assert _kernel.max_speedup(0.0) == float("inf"), "no serial fraction means no ceiling"
try:
    _kernel.max_speedup(2.0)
    assert False, "max_speedup(2.0) should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The study reports its findings", "code": r'''
assert "all stages bit-identical: True" in _out, \
    "main.py should confirm every stage matches stencil_v0 exactly"
for _word in ("stage", "seconds", "speedup"):
    assert _word in _out, f"the printed table should have a {_word!r} column"
assert "implied serial fraction" in _out, "main.py should report the serial fraction it inferred"
assert "ceiling" in _out, "main.py should state the ceiling that fraction implies"
_src = open("kernel.py").read()
assert "print(" not in _src, "kernel.py holds the logic; the printing belongs in main.py"
'''},
        ],
    },
}
