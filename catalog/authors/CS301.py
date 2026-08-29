"""CS301 — Design & Analysis of Algorithms. Author module."""

COURSE = {
    "id": "CS301",
    "title": "Design & Analysis of Algorithms",
    "year": 3,
    "level": "Advanced",
    "prereqs": ["CS201", "MA101"],
    "stack": ["Python"],
    "credits": 15,
    "hours": 160,
    "icon": "⌘",
    "summary": (
        "A design course, not a catalogue. Each module takes one paradigm — divide "
        "and conquer, greedy, dynamic programming, graph search, approximation — and "
        "asks for a working implementation together with the argument that it is "
        "correct and the recurrence that gives its running time. Every lab is checked "
        "against a brute-force reference and, where it matters, against the clock."
    ),
    "outcomes": [
        "Derive the running time of a divide-and-conquer algorithm from its recurrence",
        "State and discharge the exchange argument that justifies a greedy choice",
        "Design a dynamic program by naming its subproblem, and recover the witness from the table",
        "Implement Dijkstra, Bellman-Ford and Kruskal with the data structures their bounds assume",
        "Detect negative cycles and unreachable vertices instead of returning nonsense",
        "Bound an approximation algorithm by exhibiting a lower-bound certificate",
        "Measure an optimisation empirically rather than asserting that it helped",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone build (60%).",
    "reading": [
        "Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms*, 4th ed. — chapters 4, 15, 16, 22-24, 35",
        "Kleinberg & Tardos, *Algorithm Design*, 1st ed. — chapters 4-6, 11",
        "Dasgupta, Papadimitriou & Vazirani, *Algorithms*, 1st ed. — chapters 2 and 9",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Divide and conquer, and the recurrences it produces",
            "summary": "Split, recurse, and pay for the combine step — then price the whole thing.",
            "concepts": [
                "The three-line template: divide into a subproblems of size n/b, recurse, combine in Theta(n^d)",
                "The master theorem as a comparison between n^d and n^(log_b a)",
                "Counting inversions: the merge step already knows how many pairs are out of order",
                "The closest-pair sweep: after the recursive calls, only a strip of width 2d can hold an improvement",
                "The seven-neighbour argument that makes the strip scan linear, not quadratic",
                "Maintaining a y-sorted order across the recursion instead of re-sorting at every level",
                "Why an O(n log^2 n) implementation is a defect and not a variant",
            ],
            "lab": {
                "title": "Inversions and the closest pair",
                "runtime": "python",
                "minutes": 70,
                "brief": r'''
Three functions. Two of them are algorithms; the third prices them.

**`count_inversions(xs)`** — the number of index pairs `i < j` with
`xs[i] > xs[j]`. The quadratic version is one line and is not acceptable here:
the checks feed it twelve thousand values and time it. Piggy-back the count on
a merge sort — when the right-hand element wins the merge comparison, it jumps
over everything still left in the left half.

```text
count_inversions([])              -> 0
count_inversions([1, 2, 3])       -> 0
count_inversions([5, 4, 3, 2, 1]) -> 10
count_inversions([2, 4, 1, 3, 5]) -> 3
```

Equal values are not an inversion.

**`closest_pair(points)`** — the two closest points in the plane, returned as
`(distance, (p, q))` with the pair in sorted order so the answer is unique.
Raise `ValueError` for fewer than two points. Duplicated points are legal and
give a distance of 0.

```text
closest_pair([(0, 0), (3, 4), (1, 1)]) -> (1.4142135623730951, ((0, 0), (1, 1)))
```

Sort by x once, sort by y once, then recurse: solve both halves, take the
better distance `d`, and only compare points inside the vertical strip of
half-width `d` around the split line, in y-order, against the next seven
points. Six thousand points are timed.

**`master_case(a, b, d)`** — for `T(n) = a T(n/b) + Theta(n^d)`, return
`(case, exponent)`:

- case 1 when `d < log_b a`, exponent `log_b a` (the leaves dominate)
- case 2 when `d == log_b a`, exponent `d` (every level costs the same; a
  `log n` factor joins the bound)
- case 3 when `d > log_b a`, exponent `d` (the root dominates)

Round the exponent to 6 decimal places and compare with a tolerance of `1e-9`.
Raise `ValueError` unless `a >= 1`, `b > 1` and `d >= 0`.

```text
master_case(2, 2, 1) -> (2, 1.0)         merge sort
master_case(3, 2, 1) -> (1, 1.584963)    Karatsuba
master_case(2, 2, 2) -> (3, 2.0)         a linear-work split with a quadratic combine
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def count_inversions(xs):
    """Pairs i < j with xs[i] > xs[j], in O(n log n) via merge sort."""
    # your code here


def closest_pair(points):
    """(distance, (p, q)) for the closest pair. ValueError when len(points) < 2."""
    # your code here


def master_case(a, b, d):
    """T(n) = a T(n/b) + Theta(n^d)  ->  (case, exponent)."""
    # your code here


print(count_inversions([2, 4, 1, 3, 5]))
print(closest_pair([(0, 0), (3, 4), (1, 1)]))
print(master_case(2, 2, 1))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def count_inversions(xs):
    """Pairs i < j with xs[i] > xs[j], in O(n log n) via merge sort."""
    _, total = _sort_and_count(list(xs))
    return total


def _sort_and_count(xs):
    """Return (sorted copy, inversion count) for xs."""
    if len(xs) <= 1:
        return xs, 0
    mid = len(xs) // 2
    left, li = _sort_and_count(xs[:mid])
    right, ri = _sort_and_count(xs[mid:])
    merged = []
    total = li + ri
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            # right[j] is smaller than every remaining element of the left half,
            # so it is on the wrong side of all len(left) - i of them at once.
            merged.append(right[j])
            j += 1
            total += len(left) - i
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, total


def _dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def _brute(pts):
    """Quadratic closest pair over tagged points; used at the recursion base."""
    best = (float("inf"), None, None)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = _dist(pts[i], pts[j])
            if d < best[0]:
                best = (d, pts[i], pts[j])
    return best


def _closest(px, py):
    """px sorted by x, py the same tagged points sorted by y."""
    n = len(px)
    if n <= 3:
        return _brute(px)
    mid = n // 2
    left_ids = {t[2] for t in px[:mid]}
    lpy = [t for t in py if t[2] in left_ids]
    rpy = [t for t in py if t[2] not in left_ids]
    best = min(_closest(px[:mid], lpy), _closest(px[mid:], rpy), key=lambda r: r[0])
    split_x = px[mid][0]
    # Only points within best[0] of the split line can beat the recursive answer.
    strip = [t for t in py if abs(t[0] - split_x) < best[0]]
    for i in range(len(strip)):
        # Geometry bounds the number of strip points within best[0] in y by 8.
        for j in range(i + 1, min(i + 8, len(strip))):
            if strip[j][1] - strip[i][1] >= best[0]:
                break
            d = _dist(strip[i], strip[j])
            if d < best[0]:
                best = (d, strip[i], strip[j])
    return best


def closest_pair(points):
    """(distance, (p, q)) for the closest pair. ValueError when len(points) < 2."""
    if len(points) < 2:
        raise ValueError("closest_pair needs at least two points")
    # Tag with the original index so duplicate coordinates still split cleanly.
    tagged = [(p[0], p[1], i) for i, p in enumerate(points)]
    px = sorted(tagged)
    py = sorted(tagged, key=lambda t: (t[1], t[0], t[2]))
    d, a, b = _closest(px, py)
    pair = tuple(sorted(((a[0], a[1]), (b[0], b[1]))))
    return d, pair


def master_case(a, b, d):
    """T(n) = a T(n/b) + Theta(n^d)  ->  (case, exponent)."""
    if a < 1 or b <= 1 or d < 0:
        raise ValueError("need a >= 1, b > 1, d >= 0")
    crit = math.log(a) / math.log(b)
    if d < crit - 1e-9:
        return 1, round(crit, 6)
    if d > crit + 1e-9:
        return 3, round(float(d), 6)
    return 2, round(float(d), 6)


print(count_inversions([2, 4, 1, 3, 5]))
print(closest_pair([(0, 0), (3, 4), (1, 1)]))
print(master_case(2, 2, 1))
'''}],
                "hints": [
                    "Write a helper that returns both the sorted list and the count; `count_inversions` is then a one-line wrapper around it.",
                    "In the merge, the whole increment happens on the branch where the right element is emitted: add `len(left) - i`.",
                    "Tag each point with its original index before sorting. Without a tag you cannot split a y-sorted list containing duplicate coordinates.",
                    "`log_b a` is `math.log(a) / math.log(b)`; compare against `d` with a tolerance, never with `==` on floats.",
                ],
                "tests": [
                    {"name": "count_inversions on the small cases", "code": r'''
for _xs, _want in [([], 0), ([7], 0), ([1, 2, 3], 0), ([5, 4, 3, 2, 1], 10),
                   ([2, 4, 1, 3, 5], 3), ([1, 1, 1], 0), ([2, 1], 1)]:
    _got = count_inversions(_xs)
    assert _got == _want, f"count_inversions({_xs!r}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "count_inversions agrees with the quadratic reference", "code": r'''
import random as _random


def _ref_inv(xs):
    return sum(1 for _i in range(len(xs)) for _j in range(_i + 1, len(xs)) if xs[_i] > xs[_j])


_rng = _random.Random(7)
for _trial in range(25):
    _xs = [_rng.randrange(12) for _ in range(_rng.randrange(0, 60))]
    _got, _want = count_inversions(_xs), _ref_inv(_xs)
    assert _got == _want, f"count_inversions({_xs!r}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "count_inversions is O(n log n), not O(n^2)", "code": r'''
import random as _random
import time as _time

_rng = _random.Random(11)
_big = [_rng.randrange(10 ** 6) for _ in range(12000)]
_t0 = _time.perf_counter()
_got = count_inversions(_big)
_elapsed = _time.perf_counter() - _t0
assert isinstance(_got, int), f"count_inversions returned {_got!r}, expected an int"
assert _elapsed < 5.0, (
    f"12000 values took {_elapsed:.2f}s — that is a quadratic double loop, "
    "count the inversions inside a merge sort instead")
'''},
                    {"name": "closest_pair on hand-checkable inputs", "code": r'''
_d, _p = closest_pair([(0, 0), (3, 4), (1, 1)])
assert abs(_d - 1.4142135623730951) < 1e-9, f"distance {_d!r}, expected sqrt(2)"
assert _p == ((0, 0), (1, 1)), f"pair {_p!r}, expected ((0, 0), (1, 1))"
_d2, _p2 = closest_pair([(2, 2), (2, 2), (9, 9)])
assert _d2 == 0.0, f"duplicated points are distance 0, got {_d2!r}"
assert _p2 == ((2, 2), (2, 2)), f"pair {_p2!r}"
_d3, _p3 = closest_pair([(0, 0), (10, 0)])
assert abs(_d3 - 10.0) < 1e-9 and _p3 == ((0, 0), (10, 0)), f"got {(_d3, _p3)!r}"
'''},
                    {"name": "closest_pair refuses fewer than two points", "code": r'''
for _bad in ([], [(1, 1)]):
    try:
        closest_pair(_bad)
        assert False, f"closest_pair({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "closest_pair agrees with the quadratic reference", "code": r'''
import math as _math
import random as _random


def _ref_closest(pts):
    _best = (float("inf"), None)
    for _i in range(len(pts)):
        for _j in range(_i + 1, len(pts)):
            _dd = _math.hypot(pts[_i][0] - pts[_j][0], pts[_i][1] - pts[_j][1])
            if _dd < _best[0]:
                _best = (_dd, tuple(sorted((pts[_i], pts[_j]))))
    return _best


_rng = _random.Random(7)
for _trial in range(12):
    _pts = [(_rng.randrange(40), _rng.randrange(40)) for _ in range(_rng.randrange(2, 90))]
    _got = closest_pair(_pts)
    _want = _ref_closest(_pts)
    assert abs(_got[0] - _want[0]) < 1e-9, (
        f"closest_pair over {len(_pts)} points gave distance {_got[0]!r}, expected {_want[0]!r}")
    _a, _b = _got[1]
    assert abs(_math.hypot(_a[0] - _b[0], _a[1] - _b[1]) - _got[0]) < 1e-9, (
        f"the returned pair {_got[1]!r} is not {_got[0]!r} apart")
'''},
                    {"name": "closest_pair is O(n log n)", "code": r'''
import random as _random
import time as _time

_rng = _random.Random(13)
_pts = [(_rng.random() * 1000.0, _rng.random() * 1000.0) for _ in range(6000)]
_t0 = _time.perf_counter()
_d, _pair = closest_pair(_pts)
_elapsed = _time.perf_counter() - _t0
assert _d > 0.0, f"distinct random points should not coincide, got {_d!r}"
assert _elapsed < 6.0, (
    f"6000 points took {_elapsed:.2f}s — recurse on the two halves and scan only "
    "the strip, do not compare every pair")
'''},
                    {"name": "master_case classifies the standard recurrences", "code": r'''
for _args, _want in [((2, 2, 1), (2, 1.0)), ((1, 2, 0), (2, 0.0)),
                     ((3, 2, 1), (1, 1.584963)), ((7, 2, 2), (1, 2.807355)),
                     ((2, 2, 2), (3, 2.0)), ((4, 2, 3), (3, 3.0)),
                     ((9, 3, 2), (2, 2.0)), ((1, 2, 1), (3, 1.0))]:
    _got = master_case(*_args)
    assert _got[0] == _want[0], f"master_case{_args!r} gave case {_got[0]!r}, expected {_want[0]}"
    assert abs(_got[1] - _want[1]) < 1e-6, (
        f"master_case{_args!r} gave exponent {_got[1]!r}, expected {_want[1]}")
for _bad in [(0, 2, 1), (2, 1, 1), (2, 0, 1), (2, 2, -1)]:
    try:
        master_case(*_bad)
        assert False, f"master_case{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Greedy algorithms and their proof obligation",
            "summary": "A greedy rule is a claim; the exchange argument is the payment.",
            "concepts": [
                "Greedy-stays-ahead and the exchange argument as the two standard proof shapes",
                "Interval scheduling: earliest finishing time is optimal, earliest start and shortest duration are not",
                "Huffman coding as repeated merging of the two least frequent symbols",
                "Optimality invariant: a symbol with higher frequency never gets a longer codeword",
                "The Kraft equality as a structural check on a prefix-free code",
                "Canonical versus non-canonical coin systems, and why greedy change-making is system-specific",
                "Searching for the smallest counterexample is a legitimate way to refute a proposed greedy rule",
            ],
            "lab": {
                "title": "Scheduling, Huffman, and where greedy breaks",
                "runtime": "python",
                "minutes": 65,
                "brief": r'''
**`schedule(intervals)`** — the largest set of pairwise non-overlapping
intervals `(start, end)`, returned in finishing order. Intervals are half-open,
so `(0, 2)` and `(2, 3)` are compatible. Raise `ValueError` if any interval has
`start >= end`.

```text
schedule([(0, 10), (1, 2), (3, 4)]) -> [(1, 2), (3, 4)]
schedule([(0, 3), (2, 4), (3, 6)])  -> [(0, 3), (3, 6)]
```

The second example is the one that refutes "always take the shortest".

**`huffman_codes(freqs)`** — a prefix-free binary code for a `symbol -> count`
mapping. Repeatedly merge the two least frequent subtrees, label the lighter
branch `0` and the heavier `1`, and read the codes off the leaves. A single
symbol gets `"0"`; an empty mapping gives `{}`. Raise `ValueError` for a
frequency that is not positive.

**`huffman_cost(freqs)`** — the total encoded length, `sum(count * len(code))`.
For the CLRS frequencies `a:45 b:13 c:12 d:16 e:9 f:5` this is `224`.

**`greedy_coin_count(coins, amount)`** — take the largest coin that still fits,
repeatedly. Return the number of coins, or `None` when this rule strands a
non-zero remainder. `amount = 0` gives `0`.

**`optimal_coin_count(coins, amount)`** — the true minimum by dynamic
programming, or `None` when the amount cannot be made at all.

**`greedy_failure(coins, limit)`** — the smallest amount in `1..limit` where
the greedy rule is strictly worse than the optimum, counting "greedy strands a
remainder but the amount is makeable" as worse. Return `None` when greedy is
optimal throughout the range.

```text
greedy_failure([1, 3, 4], 20)     -> 6      greedy 4+1+1, optimal 3+3
greedy_failure([1, 5, 10, 25], 99) -> None  a canonical system
greedy_failure([2, 5], 20)        -> 6      greedy takes 5 and strands 1
```
''',
                "files": [{"name": "main.py", "content": r'''
import heapq
import itertools


def schedule(intervals):
    """Largest pairwise-compatible set of half-open intervals, in finishing order."""
    # your code here


def huffman_codes(freqs):
    """symbol -> prefix-free bit string. {} for no symbols, "0" for one."""
    # your code here


def huffman_cost(freqs):
    """Total encoded length under huffman_codes(freqs)."""
    # your code here


def greedy_coin_count(coins, amount):
    """Largest-coin-first count, or None when that rule strands a remainder."""
    # your code here


def optimal_coin_count(coins, amount):
    """True minimum number of coins, or None when the amount is unreachable."""
    # your code here


def greedy_failure(coins, limit):
    """Smallest amount in 1..limit where greedy loses to the optimum, else None."""
    # your code here


print(schedule([(0, 10), (1, 2), (3, 4)]))
print(huffman_cost({"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}))
print(greedy_failure([1, 3, 4], 20))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import heapq
import itertools


def schedule(intervals):
    """Largest pairwise-compatible set of half-open intervals, in finishing order."""
    for start, end in intervals:
        if start >= end:
            raise ValueError(f"interval {(start, end)!r} has start >= end")
    chosen = []
    last_end = None
    # Earliest finishing time first: the exchange argument says any optimal
    # solution can be rewritten to start with this interval without shrinking.
    for start, end in sorted(intervals, key=lambda iv: (iv[1], iv[0])):
        if last_end is None or start >= last_end:
            chosen.append((start, end))
            last_end = end
    return chosen


def huffman_codes(freqs):
    """symbol -> prefix-free bit string. {} for no symbols, "0" for one."""
    for symbol, count in freqs.items():
        if count <= 0:
            raise ValueError(f"frequency for {symbol!r} must be positive")
    if not freqs:
        return {}
    if len(freqs) == 1:
        return {next(iter(freqs)): "0"}
    tick = itertools.count()
    # The counter keeps the heap total-ordered without ever comparing subtrees.
    heap = [(freqs[s], next(tick), ("leaf", s)) for s in sorted(freqs)]
    heapq.heapify(heap)
    while len(heap) > 1:
        w1, _, n1 = heapq.heappop(heap)
        w2, _, n2 = heapq.heappop(heap)
        heapq.heappush(heap, (w1 + w2, next(tick), ("node", n1, n2)))
    codes = {}
    stack = [(heap[0][2], "")]
    while stack:
        node, prefix = stack.pop()
        if node[0] == "leaf":
            codes[node[1]] = prefix
        else:
            stack.append((node[1], prefix + "0"))
            stack.append((node[2], prefix + "1"))
    return codes


def huffman_cost(freqs):
    """Total encoded length under huffman_codes(freqs)."""
    codes = huffman_codes(freqs)
    return sum(freqs[s] * len(codes[s]) for s in codes)


def greedy_coin_count(coins, amount):
    """Largest-coin-first count, or None when that rule strands a remainder."""
    if amount < 0:
        raise ValueError("amount must not be negative")
    used = 0
    left = amount
    for coin in sorted(coins, reverse=True):
        if coin <= 0:
            raise ValueError("coins must be positive")
        take = left // coin
        used += take
        left -= take * coin
    return used if left == 0 else None


def optimal_coin_count(coins, amount):
    """True minimum number of coins, or None when the amount is unreachable."""
    if amount < 0:
        raise ValueError("amount must not be negative")
    best = [0] + [None] * amount
    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and best[value - coin] is not None:
                candidate = best[value - coin] + 1
                if best[value] is None or candidate < best[value]:
                    best[value] = candidate
    return best[amount]


def greedy_failure(coins, limit):
    """Smallest amount in 1..limit where greedy loses to the optimum, else None."""
    for amount in range(1, limit + 1):
        best = optimal_coin_count(coins, amount)
        if best is None:
            continue  # not makeable at all — greedy is not at fault
        got = greedy_coin_count(coins, amount)
        if got is None or got > best:
            return amount
    return None


print(schedule([(0, 10), (1, 2), (3, 4)]))
print(huffman_cost({"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}))
print(greedy_failure([1, 3, 4], 20))
'''}],
                "hints": [
                    "Sort by finishing time and keep a single `last_end`; an interval joins the answer when `start >= last_end`.",
                    "Push `(weight, counter, node)` triples onto the heap. Without the counter Python will try to compare two subtrees when weights tie.",
                    "`optimal_coin_count` is a one-dimensional table over `0..amount`; `None` marks an unreachable value so it never contributes.",
                    "In `greedy_failure`, an amount that neither rule can make is not a counterexample — skip it before comparing.",
                ],
                "tests": [
                    {"name": "schedule picks by finishing time", "code": r'''
assert schedule([]) == [], "no intervals, no schedule"
assert schedule([(3, 9)]) == [(3, 9)], f"got {schedule([(3, 9)])!r}"
_got = schedule([(0, 10), (1, 2), (3, 4)])
assert _got == [(1, 2), (3, 4)], f"got {_got!r} — earliest start would pick only (0, 10)"
_got = schedule([(0, 3), (2, 4), (3, 6)])
assert _got == [(0, 3), (3, 6)], f"got {_got!r} — shortest duration would pick only (2, 4)"
_got = schedule([(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)])
assert len(_got) == 4, f"got {_got!r}, the optimum has 4 intervals"
'''},
                    {"name": "schedule respects half-open touching and rejects bad input", "code": r'''
assert schedule([(0, 2), (2, 3)]) == [(0, 2), (2, 3)], "touching endpoints are compatible"
assert schedule([(0, 5), (1, 4), (2, 3)]) == [(2, 3)], "nested intervals: the innermost finishes first"
for _bad in [[(3, 3)], [(5, 1)], [(0, 2), (4, 4)]]:
    try:
        schedule(_bad)
        assert False, f"schedule({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "schedule is verified as a compatible set", "code": r'''
import random as _random

_rng = _random.Random(7)
for _trial in range(20):
    _ivs = []
    for _ in range(_rng.randrange(0, 14)):
        _s = _rng.randrange(0, 20)
        _ivs.append((_s, _s + _rng.randrange(1, 6)))
    _got = schedule(_ivs)
    for _iv in _got:
        assert _iv in _ivs, f"{_iv!r} is not one of the supplied intervals"
    for _i in range(len(_got) - 1):
        assert _got[_i][1] <= _got[_i + 1][0], f"{_got!r} contains an overlap"
'''},
                    {"name": "huffman_codes is prefix-free and satisfies Kraft equality", "code": r'''
_f = {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}
_codes = huffman_codes(_f)
assert set(_codes) == set(_f), f"every symbol needs a code, got {sorted(_codes)}"
assert all(set(_c) <= {"0", "1"} and _c for _c in _codes.values()), f"got {_codes!r}"
_vals = sorted(_codes.values())
for _i, _x in enumerate(_vals):
    for _y in _vals[_i + 1:]:
        assert not _y.startswith(_x), f"{_y!r} has {_x!r} as a prefix — the code is not prefix-free"
_kraft = sum(2.0 ** -len(_c) for _c in _codes.values())
assert abs(_kraft - 1.0) < 1e-9, f"Kraft sum is {_kraft!r}, a full Huffman tree gives exactly 1"
'''},
                    {"name": "huffman_cost hits the optimum, and the frequency invariant holds", "code": r'''
_f = {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}
_got = huffman_cost(_f)
assert _got == 224, f"huffman_cost of the CLRS example gave {_got!r}, the optimum is 224"
_codes = huffman_codes(_f)
for _s in _codes:
    for _t in _codes:
        if _f[_s] > _f[_t]:
            assert len(_codes[_s]) <= len(_codes[_t]), (
                f"{_s!r} is more frequent than {_t!r} but got the longer code — not optimal")
assert huffman_cost({"z": 4}) == 4, "one symbol still needs one bit per occurrence"
'''},
                    {"name": "huffman edge cases and validation", "code": r'''
assert huffman_codes({}) == {}, "no symbols, no codes"
assert huffman_cost({}) == 0, "an empty alphabet encodes to nothing"
assert huffman_codes({"q": 3}) == {"q": "0"}, f"got {huffman_codes({'q': 3})!r}"
assert huffman_codes({"a": 1, "b": 1}) in ({"a": "0", "b": "1"}, {"a": "1", "b": "0"}), \
    f"two equal symbols need one bit each, got {huffman_codes({'a': 1, 'b': 1})!r}"
for _bad in [{"a": 0}, {"a": 2, "b": -1}]:
    try:
        huffman_codes(_bad)
        assert False, f"huffman_codes({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the two coin counters", "code": r'''
assert greedy_coin_count([1, 5, 10, 25], 0) == 0, "zero costs no coins"
assert greedy_coin_count([1, 5, 10, 25], 30) == 2, f"got {greedy_coin_count([1, 5, 10, 25], 30)!r}"
assert greedy_coin_count([1, 3, 4], 6) == 3, "greedy takes 4 then 1 then 1"
assert greedy_coin_count([2, 5], 3) is None, "greedy takes 2 and strands 1"
assert optimal_coin_count([1, 3, 4], 6) == 2, f"got {optimal_coin_count([1, 3, 4], 6)!r} — 3 + 3"
assert optimal_coin_count([2, 5], 3) is None, "3 cannot be made from 2s and 5s"
assert optimal_coin_count([2, 5], 0) == 0, "zero is always reachable"
assert optimal_coin_count([7], 21) == 3, f"got {optimal_coin_count([7], 21)!r}"
'''},
                    {"name": "greedy_failure finds the smallest counterexample", "code": r'''
assert greedy_failure([1, 3, 4], 20) == 6, f"got {greedy_failure([1, 3, 4], 20)!r}, expected 6"
assert greedy_failure([1, 5, 10, 25], 99) is None, "US-style coins are canonical for greedy"
assert greedy_failure([1, 2, 5, 10, 20, 50], 200) is None, "so is the euro system"
assert greedy_failure([2, 5], 20) == 6, f"got {greedy_failure([2, 5], 20)!r}, expected 6"
assert greedy_failure([1, 7, 10], 20) == 14, f"got {greedy_failure([1, 7, 10], 20)!r} — 10+1+1+1+1 versus 7+7"
assert greedy_failure([1, 3, 4], 5) is None, "no counterexample below 6"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Dynamic programming and witness reconstruction",
            "summary": "Name the subproblem, fill the table, then walk it backwards for the answer itself.",
            "concepts": [
                "Optimal substructure and overlapping subproblems as the two preconditions",
                "Edit distance: three predecessors per cell, and unit costs for insert, delete and substitute",
                "Longest common subsequence, and its relation to the deletion-only edit distance",
                "0/1 knapsack over a weight axis, and why fractional greedy fails on it",
                "Reconstruction by back-pointer walk versus recomputation from the table",
                "The value of an optimum is unique; the witness rarely is, so verify the witness rather than compare it",
                "Space-for-time: rolling rows give the value but destroy the reconstruction",
            ],
            "lab": {
                "title": "Three tables, three witnesses",
                "runtime": "python",
                "minutes": 75,
                "brief": r'''
Each function returns the optimal value **and** the object that achieves it.
The checks never compare your witness against one fixed answer — ties are real
— they replay it and confirm that it does what you claim.

**`edit_distance(a, b)`** — returns `(cost, script)` for unit-cost Levenshtein
distance. The script is a list of operations applied left to right:

```text
("match", ch)          consume ch from a, emit it        cost 0
("sub", ch_a, ch_b)    consume ch_a from a, emit ch_b    cost 1
("del", ch_a)          consume ch_a from a, emit nothing cost 1
("ins", ch_b)          consume nothing, emit ch_b        cost 1
```

Replaying the script on `a` must produce exactly `b`, and the number of
non-`match` operations must equal `cost`.

```text
edit_distance("kitten", "sitting") -> (3, [...])
edit_distance("", "abc")           -> (3, [("ins", "a"), ("ins", "b"), ("ins", "c")])
edit_distance("abc", "abc")        -> (0, [("match", "a"), ("match", "b"), ("match", "c")])
```

**`lcs(a, b)`** — returns the longest common subsequence as a string. Any
longest one is accepted; the checks confirm it is a subsequence of both and
that its length matches an independent table.

**`knapsack(items, capacity)`** — `items` is a list of `(weight, value)` pairs
with non-negative integer weights. Returns `(best_value, indices)` where
`indices` is a sorted list of chosen positions. Raise `ValueError` for a
negative capacity or a negative weight.

```text
knapsack([(2, 3), (3, 4), (4, 5), (5, 6)], 5) -> (7, [0, 1])
knapsack([], 10)                              -> (0, [])
knapsack([(11, 99)], 10)                      -> (0, [])
```
''',
                "files": [{"name": "main.py", "content": r'''
def edit_distance(a, b):
    """(cost, script) for unit-cost Levenshtein distance from a to b."""
    # your code here


def lcs(a, b):
    """A longest common subsequence of a and b, as a string."""
    # your code here


def knapsack(items, capacity):
    """(best_value, chosen indices) for 0/1 knapsack over (weight, value) items."""
    # your code here


print(edit_distance("kitten", "sitting")[0])
print(lcs("AGGTAB", "GXTXAYB"))
print(knapsack([(2, 3), (3, 4), (4, 5), (5, 6)], 5))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def edit_distance(a, b):
    """(cost, script) for unit-cost Levenshtein distance from a to b."""
    n, m = len(a), len(b)
    # table[i][j] = distance between a[:i] and b[:j]
    table = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        table[i][0] = i
    for j in range(1, m + 1):
        table[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1]
            else:
                table[i][j] = 1 + min(table[i - 1][j - 1], table[i - 1][j], table[i][j - 1])

    # Walk back from the corner, preferring match, then substitute, then delete.
    script = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and table[i][j] == table[i - 1][j - 1]:
            script.append(("match", a[i - 1]))
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + 1:
            script.append(("sub", a[i - 1], b[j - 1]))
            i -= 1
            j -= 1
        elif i > 0 and table[i][j] == table[i - 1][j] + 1:
            script.append(("del", a[i - 1]))
            i -= 1
        else:
            script.append(("ins", b[j - 1]))
            j -= 1
    script.reverse()
    return table[n][m], script


def lcs(a, b):
    """A longest common subsequence of a and b, as a string."""
    n, m = len(a), len(b)
    table = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    out = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif table[i - 1][j] >= table[i][j - 1]:
            i -= 1
        else:
            j -= 1
    out.reverse()
    return "".join(out)


def knapsack(items, capacity):
    """(best_value, chosen indices) for 0/1 knapsack over (weight, value) items."""
    if capacity < 0:
        raise ValueError("capacity must not be negative")
    for weight, _value in items:
        if weight < 0:
            raise ValueError("weights must not be negative")
    n = len(items)
    # table[i][c] = best value using the first i items under capacity c
    table = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        weight, value = items[i - 1]
        row, prev = table[i], table[i - 1]
        for c in range(capacity + 1):
            row[c] = prev[c]
            if weight <= c:
                candidate = prev[c - weight] + value
                if candidate > row[c]:
                    row[c] = candidate
    chosen = []
    c = capacity
    for i in range(n, 0, -1):
        if table[i][c] != table[i - 1][c]:
            chosen.append(i - 1)
            c -= items[i - 1][0]
    chosen.reverse()
    return table[n][capacity], chosen


print(edit_distance("kitten", "sitting")[0])
print(lcs("AGGTAB", "GXTXAYB"))
print(knapsack([(2, 3), (3, 4), (4, 5), (5, 6)], 5))
'''}],
                "hints": [
                    "Allocate the table with `(len(a) + 1)` rows and `(len(b) + 1)` columns, and fill row 0 and column 0 with the pure-insert and pure-delete costs.",
                    "Reconstruct by walking from `(n, m)` back to `(0, 0)`, appending operations and reversing at the end. The loop condition is `i > 0 or j > 0`, not `and`.",
                    "For the knapsack back-walk: item `i-1` was taken exactly when `table[i][c] != table[i-1][c]`; subtract its weight from `c` and carry on.",
                    "A zero-weight item with positive value is always worth taking — make sure your table does not silently exclude it.",
                ],
                "tests": [
                    {"name": "edit_distance values", "code": r'''
for _a, _b, _want in [("kitten", "sitting", 3), ("", "", 0), ("", "abc", 3),
                      ("abc", "", 3), ("abc", "abc", 0), ("flaw", "lawn", 2),
                      ("a", "b", 1), ("intention", "execution", 5)]:
    _got = edit_distance(_a, _b)[0]
    assert _got == _want, f"edit_distance({_a!r}, {_b!r}) cost {_got!r}, expected {_want}"
'''},
                    {"name": "the edit script actually transforms a into b", "code": r'''
import random as _random


def _replay(a, script):
    _i = 0
    _out = []
    for _op in script:
        if _op[0] == "match":
            assert _i < len(a) and a[_i] == _op[1], f"match {_op[1]!r} does not line up in {a!r}"
            _out.append(a[_i])
            _i += 1
        elif _op[0] == "sub":
            assert _i < len(a) and a[_i] == _op[1], f"sub {_op!r} does not line up in {a!r}"
            _out.append(_op[2])
            _i += 1
        elif _op[0] == "del":
            assert _i < len(a) and a[_i] == _op[1], f"del {_op!r} does not line up in {a!r}"
            _i += 1
        elif _op[0] == "ins":
            _out.append(_op[1])
        else:
            assert False, f"unknown operation {_op!r}"
    assert _i == len(a), f"the script consumed {_i} of {len(a)} characters of {a!r}"
    return "".join(_out)


_rng = _random.Random(7)
_words = ["kitten", "sitting", "", "a", "abc", "flaw", "lawn", "banana", "ananas",
          "algorithm", "logarithm", "aaaa", "abab"]
for _a in _words:
    for _b in _words:
        _cost, _script = edit_distance(_a, _b)
        assert _replay(_a, _script) == _b, (
            f"replaying the script for ({_a!r} -> {_b!r}) did not give {_b!r}")
        _paid = sum(1 for _op in _script if _op[0] != "match")
        assert _paid == _cost, (
            f"({_a!r} -> {_b!r}) claims cost {_cost} but the script pays {_paid}")
'''},
                    {"name": "edit_distance matches an independent recurrence", "code": r'''
import random as _random
from functools import lru_cache as _lru


def _ref_ed(a, b):
    @_lru(maxsize=None)
    def _go(i, j):
        if i == 0:
            return j
        if j == 0:
            return i
        if a[i - 1] == b[j - 1]:
            return _go(i - 1, j - 1)
        return 1 + min(_go(i - 1, j - 1), _go(i - 1, j), _go(i, j - 1))
    return _go(len(a), len(b))


_rng = _random.Random(7)
for _trial in range(30):
    _a = "".join(_rng.choice("abc") for _ in range(_rng.randrange(0, 9)))
    _b = "".join(_rng.choice("abc") for _ in range(_rng.randrange(0, 9)))
    _got, _want = edit_distance(_a, _b)[0], _ref_ed(_a, _b)
    assert _got == _want, f"edit_distance({_a!r}, {_b!r}) gave {_got}, expected {_want}"
'''},
                    {"name": "lcs returns a genuine common subsequence of the right length", "code": r'''
import random as _random


def _is_sub(s, t):
    _it = iter(t)
    return all(_ch in _it for _ch in s)


def _ref_len(a, b):
    _tab = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for _i in range(1, len(a) + 1):
        for _j in range(1, len(b) + 1):
            if a[_i - 1] == b[_j - 1]:
                _tab[_i][_j] = _tab[_i - 1][_j - 1] + 1
            else:
                _tab[_i][_j] = max(_tab[_i - 1][_j], _tab[_i][_j - 1])
    return _tab[len(a)][len(b)]


assert lcs("", "abc") == "", f"got {lcs('', 'abc')!r}"
assert lcs("abc", "") == "", f"got {lcs('abc', '')!r}"
assert lcs("abc", "xyz") == "", f"got {lcs('abc', 'xyz')!r}"
assert lcs("AGGTAB", "GXTXAYB") == "GTAB", f"got {lcs('AGGTAB', 'GXTXAYB')!r}"
_rng = _random.Random(7)
for _trial in range(30):
    _a = "".join(_rng.choice("abcd") for _ in range(_rng.randrange(0, 12)))
    _b = "".join(_rng.choice("abcd") for _ in range(_rng.randrange(0, 12)))
    _got = lcs(_a, _b)
    assert _is_sub(_got, _a) and _is_sub(_got, _b), (
        f"lcs({_a!r}, {_b!r}) gave {_got!r}, which is not a subsequence of both")
    assert len(_got) == _ref_len(_a, _b), (
        f"lcs({_a!r}, {_b!r}) gave {_got!r} of length {len(_got)}, expected {_ref_len(_a, _b)}")
'''},
                    {"name": "knapsack values and edge cases", "code": r'''
_v, _idx = knapsack([(2, 3), (3, 4), (4, 5), (5, 6)], 5)
assert _v == 7, f"best value {_v!r}, expected 7"
assert sorted(_idx) == _idx, f"indices {_idx!r} should come back sorted"
assert knapsack([], 10) == (0, []), f"got {knapsack([], 10)!r}"
assert knapsack([(11, 99)], 10) == (0, []), "an item that does not fit is not taken"
assert knapsack([(2, 3)], 0) == (0, []), "zero capacity carries nothing"
_v0, _i0 = knapsack([(0, 5), (3, 1)], 2)
assert _v0 == 5 and _i0 == [0], f"a zero-weight item is free value, got {(_v0, _i0)!r}"
for _bad in [([(1, 1)], -1), ([(-1, 1)], 5)]:
    try:
        knapsack(*_bad)
        assert False, f"knapsack{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the chosen indices fit and are worth what is claimed", "code": r'''
import itertools as _it
import random as _random

_rng = _random.Random(7)
for _trial in range(25):
    _items = [(_rng.randrange(0, 9), _rng.randrange(1, 15)) for _ in range(_rng.randrange(0, 11))]
    _cap = _rng.randrange(0, 20)
    _best, _idx = knapsack(_items, _cap)
    assert len(set(_idx)) == len(_idx), f"indices {_idx!r} repeat an item"
    assert all(0 <= _i < len(_items) for _i in _idx), f"indices {_idx!r} out of range"
    _w = sum(_items[_i][0] for _i in _idx)
    _val = sum(_items[_i][1] for _i in _idx)
    assert _w <= _cap, f"chosen weight {_w} exceeds capacity {_cap}"
    assert _val == _best, f"claimed value {_best} but the indices are worth {_val}"
    _opt = 0
    for _r in range(len(_items) + 1):
        for _combo in _it.combinations(range(len(_items)), _r):
            if sum(_items[_i][0] for _i in _combo) <= _cap:
                _opt = max(_opt, sum(_items[_i][1] for _i in _combo))
    assert _best == _opt, f"knapsack({_items!r}, {_cap}) gave {_best}, the optimum is {_opt}"
'''},
                    {"name": "knapsack beats the value-density greedy where greedy fails", "code": r'''
# Density greedy takes item 0 (1.5 per unit) and then nothing else fits.
_items = [(6, 9), (5, 7), (5, 7)]
_best, _idx = knapsack(_items, 10)
assert _best == 14, f"got {_best!r}; the optimum takes both size-5 items"
assert sorted(_idx) == [1, 2], f"got indices {_idx!r}, expected [1, 2]"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Shortest paths and spanning trees",
            "summary": "Three graph algorithms, each with the data structure its bound depends on.",
            "concepts": [
                "Dijkstra's invariant: once a vertex is extracted, its distance is final — and why that needs non-negative weights",
                "Lazy deletion in a binary heap gives O((V + E) log V) without a decrease-key operation",
                "Bellman-Ford as V-1 rounds of relaxation, with the V-th round as the negative-cycle test",
                "A negative cycle unreachable from the source is not an error",
                "The cut property, and Kruskal as its repeated application in weight order",
                "Union-find with path compression and union by size: near-constant amortised cost",
                "Parent arrays as a compressed representation of a whole shortest-path tree",
            ],
            "lab": {
                "title": "Dijkstra, Bellman-Ford, Kruskal",
                "runtime": "python",
                "minutes": 80,
                "brief": r'''
Graphs are adjacency maps: `{node: [(neighbour, weight), ...]}`. A node that
appears only as a neighbour is still a node of the graph.

**`dijkstra(graph, source)`** — returns `(dist, parent)`. Unreachable nodes get
`math.inf` and a parent of `None`; the source gets `0` and `None`. Raise
`ValueError` on a negative weight — Dijkstra's extraction invariant does not
survive one. Use `heapq` with lazy deletion: push a new entry on improvement
and discard an entry whose recorded distance is stale. The checks build a
100 x 100 grid and time you.

**`shortest_path(graph, source, target)`** — `(cost, path)` built from
`dijkstra`. An unreachable target gives `(math.inf, [])`; `source == target`
gives `(0, [source])`.

**`bellman_ford(graph, source)`** — returns the same `dist` dict but tolerates
negative edges. Raise `ValueError` when a negative cycle is **reachable from
the source**. A negative cycle sitting in a component the source cannot reach
must not raise.

**`DisjointSet(n)`** — `find(x)` with path compression, `union(a, b)` returning
`True` when two distinct sets were merged and `False` when they were already
one, and `components` as the current number of sets.

**`kruskal(n, edges)`** — nodes are `0..n-1` and `edges` is a list of
`(u, v, w)`. Returns `(total_weight, tree_edges)`, where each tree edge is
normalised to `(min(u, v), max(u, v), w)` and the list is sorted by
`(w, u, v)`. A disconnected graph yields a spanning forest, so check
`len(tree_edges) == n - components` rather than assuming `n - 1`.
''',
                "files": [{"name": "main.py", "content": r'''
import heapq
import math


def dijkstra(graph, source):
    """(dist, parent) over a non-negative weighted graph. ValueError on a negative weight."""
    # your code here


def shortest_path(graph, source, target):
    """(cost, path) from source to target; (math.inf, []) when unreachable."""
    # your code here


def bellman_ford(graph, source):
    """dist dict allowing negative weights. ValueError on a reachable negative cycle."""
    # your code here


class DisjointSet:
    """Union-find over 0..n-1 with path compression and union by size."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n

    def find(self, x):
        # your code here
        pass

    def union(self, a, b):
        # your code here
        pass


def kruskal(n, edges):
    """(total_weight, tree_edges) for a minimum spanning forest."""
    # your code here


GRAPH = {
    "a": [("b", 7), ("c", 9), ("f", 14)],
    "b": [("a", 7), ("c", 10), ("d", 15)],
    "c": [("a", 9), ("b", 10), ("d", 11), ("f", 2)],
    "d": [("b", 15), ("c", 11), ("e", 6)],
    "e": [("d", 6), ("f", 9)],
    "f": [("a", 14), ("c", 2), ("e", 9)],
}

print(dijkstra(GRAPH, "a"))
print(shortest_path(GRAPH, "a", "e"))
print(kruskal(4, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4)]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import heapq
import math


def _all_nodes(graph):
    """Every node, including ones that only appear as a neighbour."""
    nodes = set(graph)
    for edges in graph.values():
        for v, _w in edges:
            nodes.add(v)
    return nodes


def dijkstra(graph, source):
    """(dist, parent) over a non-negative weighted graph. ValueError on a negative weight."""
    for u, edges in graph.items():
        for v, w in edges:
            if w < 0:
                raise ValueError(f"negative weight {w} on edge {u!r} -> {v!r}")
    nodes = _all_nodes(graph)
    if source not in nodes:
        raise ValueError(f"source {source!r} is not a node of the graph")
    dist = {n: math.inf for n in nodes}
    parent = {n: None for n in nodes}
    dist[source] = 0
    heap = [(0, source)]
    settled = set()
    while heap:
        d, u = heapq.heappop(heap)
        # Lazy deletion: an entry left behind by an improvement is simply skipped.
        if u in settled or d > dist[u]:
            continue
        settled.add(u)
        for v, w in graph.get(u, ()):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, parent


def shortest_path(graph, source, target):
    """(cost, path) from source to target; (math.inf, []) when unreachable."""
    dist, parent = dijkstra(graph, source)
    if target not in dist or dist[target] == math.inf:
        return math.inf, []
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return dist[target], path


def bellman_ford(graph, source):
    """dist dict allowing negative weights. ValueError on a reachable negative cycle."""
    nodes = _all_nodes(graph)
    if source not in nodes:
        raise ValueError(f"source {source!r} is not a node of the graph")
    edges = [(u, v, w) for u, out in graph.items() for v, w in out]
    dist = {n: math.inf for n in nodes}
    dist[source] = 0
    for _round in range(len(nodes) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    # One more round: any further improvement means a reachable negative cycle.
    for u, v, w in edges:
        if dist[u] != math.inf and dist[u] + w < dist[v]:
            raise ValueError("negative cycle reachable from the source")
    return dist


class DisjointSet:
    """Union-find over 0..n-1 with path compression and union by size."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # second pass flattens the path
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.components -= 1
        return True


def kruskal(n, edges):
    """(total_weight, tree_edges) for a minimum spanning forest."""
    dsu = DisjointSet(n)
    chosen = []
    total = 0
    for u, v, w in sorted(edges, key=lambda e: (e[2], min(e[0], e[1]), max(e[0], e[1]))):
        if dsu.union(u, v):
            chosen.append((min(u, v), max(u, v), w))
            total += w
    chosen.sort(key=lambda e: (e[2], e[0], e[1]))
    return total, chosen


GRAPH = {
    "a": [("b", 7), ("c", 9), ("f", 14)],
    "b": [("a", 7), ("c", 10), ("d", 15)],
    "c": [("a", 9), ("b", 10), ("d", 11), ("f", 2)],
    "d": [("b", 15), ("c", 11), ("e", 6)],
    "e": [("d", 6), ("f", 9)],
    "f": [("a", 14), ("c", 2), ("e", 9)],
}

print(dijkstra(GRAPH, "a"))
print(shortest_path(GRAPH, "a", "e"))
print(kruskal(4, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4)]))
'''}],
                "hints": [
                    "Collect the node set from both the keys and the neighbour lists before you initialise `dist`, or an unreachable sink will be missing from the answer.",
                    "The lazy-deletion guard is `if d > dist[u]: continue` right after the pop — that is what lets you skip a decrease-key operation.",
                    "Bellman-Ford relaxes over a flat edge list `V - 1` times; the `V`-th pass is a test, not a relaxation. Guard every relaxation with `dist[u] != math.inf` so an unreachable negative cycle stays silent.",
                    "`find` twice: walk up to the root, then walk the same path again reassigning parents to the root.",
                ],
                "tests": [
                    {"name": "dijkstra on the standard six-node graph", "code": r'''
import math as _math

_dist, _parent = dijkstra(GRAPH, "a")
assert _dist == {"a": 0, "b": 7, "c": 9, "d": 20, "e": 20, "f": 11}, f"got {_dist!r}"
assert _parent["a"] is None, f"the source has no parent, got {_parent['a']!r}"
assert _parent["f"] == "c", f"parent of f is {_parent['f']!r}, expected c"
'''},
                    {"name": "dijkstra handles unreachable nodes and rejects negative weights", "code": r'''
import math as _math

_g = {"a": [("b", 1)], "b": [], "z": [("y", 1)], "y": []}
_d, _p = dijkstra(_g, "a")
assert _d["z"] == _math.inf and _d["y"] == _math.inf, f"unreachable nodes need inf, got {_d!r}"
assert _p["z"] is None, f"unreachable parent should be None, got {_p['z']!r}"
_solo = dijkstra({"a": []}, "a")[0]
assert _solo == {"a": 0}, f"got {_solo!r}"
try:
    dijkstra({"a": [("b", -1)], "b": []}, "a")
    assert False, "a negative weight must raise ValueError in dijkstra"
except ValueError:
    pass
'''},
                    {"name": "shortest_path returns a walkable path", "code": r'''
import math as _math

_cost, _path = shortest_path(GRAPH, "a", "e")
assert _cost == 20, f"cost {_cost!r}, expected 20"
assert _path[0] == "a" and _path[-1] == "e", f"path {_path!r} does not run from a to e"
_walk = 0
for _i in range(len(_path) - 1):
    _step = [_w for _v, _w in GRAPH[_path[_i]] if _v == _path[_i + 1]]
    assert _step, f"{_path[_i]!r} -> {_path[_i + 1]!r} is not an edge"
    _walk += _step[0]
assert _walk == _cost, f"the path costs {_walk} but you reported {_cost}"
assert shortest_path(GRAPH, "a", "a") == (0, ["a"]), f"got {shortest_path(GRAPH, 'a', 'a')!r}"
_g = {"a": [], "b": []}
assert shortest_path(_g, "a", "b") == (_math.inf, []), f"got {shortest_path(_g, 'a', 'b')!r}"
'''},
                    {"name": "dijkstra scales to a 100 x 100 grid", "code": r'''
import random as _random
import time as _time

_rng = _random.Random(7)
_N = 100
_grid = {}
for _r in range(_N):
    for _c in range(_N):
        _out = []
        if _r + 1 < _N:
            _out.append(((_r + 1, _c), _rng.randrange(1, 10)))
        if _c + 1 < _N:
            _out.append(((_r, _c + 1), _rng.randrange(1, 10)))
        _grid[(_r, _c)] = _out
_t0 = _time.perf_counter()
_d, _p = dijkstra(_grid, (0, 0))
_elapsed = _time.perf_counter() - _t0
assert len(_d) == _N * _N, f"got {len(_d)} distances for {_N * _N} nodes"
assert _d[(_N - 1, _N - 1)] > 0
assert _elapsed < 8.0, (
    f"10000 nodes took {_elapsed:.2f}s — use a heap, not a linear scan for the minimum")
'''},
                    {"name": "bellman_ford handles negative edges", "code": r'''
import math as _math

_g = {"s": [("a", 4), ("b", 5)], "a": [("c", -3)], "b": [("c", 2)], "c": []}
_d = bellman_ford(_g, "s")
assert _d == {"s": 0, "a": 4, "b": 5, "c": 1}, f"got {_d!r}"
_d2 = bellman_ford({"a": [("b", 1)], "b": [], "z": []}, "a")
assert _d2["z"] == _math.inf, f"unreachable node should be inf, got {_d2!r}"
assert bellman_ford({"a": []}, "a") == {"a": 0}, "a lone source is 0 away from itself"
'''},
                    {"name": "bellman_ford detects only reachable negative cycles", "code": r'''
_bad = {"s": [("a", 1)], "a": [("b", 1)], "b": [("a", -3)]}
try:
    bellman_ford(_bad, "s")
    assert False, "a negative cycle reachable from s must raise ValueError"
except ValueError:
    pass
_far = {"s": [("t", 1)], "t": [], "x": [("y", 1)], "y": [("x", -3)]}
_d = bellman_ford(_far, "s")
assert _d["t"] == 1, f"got {_d!r}"
assert _d["x"] == float("inf"), "an unreachable negative cycle is not an error and stays at inf"
'''},
                    {"name": "bellman_ford agrees with dijkstra when weights are non-negative", "code": r'''
import random as _random

_rng = _random.Random(7)
for _trial in range(15):
    _n = _rng.randrange(2, 9)
    _g = {_i: [] for _i in range(_n)}
    for _u in range(_n):
        for _v in range(_n):
            if _u != _v and _rng.random() < 0.4:
                _g[_u].append((_v, _rng.randrange(0, 12)))
    _a = dijkstra(_g, 0)[0]
    _b = bellman_ford(_g, 0)
    assert _a == _b, f"on {_g!r} dijkstra gave {_a!r} but bellman_ford gave {_b!r}"
'''},
                    {"name": "DisjointSet merges and reports components", "code": r'''
_ds = DisjointSet(5)
assert _ds.components == 5, f"got {_ds.components!r}"
assert _ds.find(3) == 3, "every element starts as its own root"
assert _ds.union(0, 1) is True, "union of two distinct sets returns True"
assert _ds.union(1, 0) is False, "a repeated union returns False"
assert _ds.union(1, 2) is True
assert _ds.find(0) == _ds.find(2), "0 and 2 are now in one set"
assert _ds.find(0) != _ds.find(4), "4 was never merged"
assert _ds.components == 3, f"got {_ds.components!r}, expected 3"
_big = DisjointSet(2000)
for _i in range(1999):
    _big.union(_i, _i + 1)
assert _big.components == 1 and _big.find(0) == _big.find(1999), "a long chain must collapse"
'''},
                    {"name": "kruskal builds a minimum spanning forest", "code": r'''
_total, _tree = kruskal(4, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4)])
assert _total == 7, f"total {_total!r}, expected 7"
assert _tree == [(0, 1, 1), (1, 2, 2), (2, 3, 4)], f"got {_tree!r}"
assert kruskal(3, []) == (0, []), "no edges, no tree"
assert kruskal(1, []) == (0, []), "a single node needs no edges"
_t2, _e2 = kruskal(4, [(0, 1, 5), (2, 3, 1)])
assert _t2 == 6 and len(_e2) == 2, f"a forest over two components, got {(_t2, _e2)!r}"
_t3, _e3 = kruskal(2, [(1, 0, 9)])
assert _e3 == [(0, 1, 9)], f"tree edges are normalised to (min, max, w), got {_e3!r}"
'''},
                    {"name": "kruskal matches an exhaustive minimum over random graphs", "code": r'''
import itertools as _it
import random as _random

_rng = _random.Random(7)
for _trial in range(15):
    _n = _rng.randrange(2, 7)
    _pool = list(_it.combinations(range(_n), 2))
    _rng.shuffle(_pool)
    _edges = [(_u, _v, _rng.randrange(1, 20)) for _u, _v in _pool[:_rng.randrange(1, len(_pool) + 1)]]
    _total, _tree = kruskal(_n, _edges)
    _ds = DisjointSet(_n)
    for _u, _v, _w in _edges:
        _ds.union(_u, _v)
    _want_size = _n - _ds.components
    assert len(_tree) == _want_size, f"forest of {len(_tree)} edges, expected {_want_size}"
    assert sum(_w for _, _, _w in _tree) == _total, "the reported total must match the chosen edges"
    _best = None
    for _combo in _it.combinations(range(len(_edges)), _want_size):
        _d2 = DisjointSet(_n)
        if all(_d2.union(_edges[_i][0], _edges[_i][1]) for _i in _combo):
            _cost = sum(_edges[_i][2] for _i in _combo)
            _best = _cost if _best is None else min(_best, _cost)
    assert _total == _best, f"kruskal gave {_total}, the true minimum is {_best}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Intractability and approximation",
            "summary": "When the exact answer is out of reach, bound the inexact one and prove the bound.",
            "concepts": [
                "NP-completeness as a statement about reductions, not about difficulty in the informal sense",
                "Vertex cover: the decision problem is NP-complete, the optimisation problem is NP-hard",
                "The maximal-matching 2-approximation, and why taking both endpoints is not wasteful",
                "Lower-bound certificates: any vertex cover must contain a distinct vertex per matching edge",
                "Approximation ratio as a worst-case guarantee, measured against a certificate rather than against OPT",
                "Exhaustive search as a testing oracle for small instances only, and the 2^n wall behind it",
                "Why the greedy highest-degree heuristic has no constant ratio at all",
            ],
            "lab": {
                "title": "A vertex cover you can vouch for",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
An undirected graph is a list of edges `(u, v)` with `u != v`; nodes are
whatever appears in it.

**`is_vertex_cover(edges, cover)`** — `True` when every edge has at least one
endpoint in `cover`.

**`vertex_cover_2approx(edges)`** — the classical algorithm: repeatedly pick
any still-uncovered edge, add **both** its endpoints, and discard every edge
they cover. Process edges in the order given so the result is deterministic.
Return `(cover, matching)` where `cover` is a `set` and `matching` is the list
of edges you picked, each normalised to `(min(u, v), max(u, v))`.

The matching is the proof. Its edges share no vertex, so any vertex cover
contains at least one endpoint of each: `OPT >= len(matching)`. Your cover has
exactly `2 * len(matching)` vertices, hence `|C| <= 2 * OPT`.

**`min_vertex_cover(edges)`** — the exact optimum by exhaustive search over
subsets, smallest first. Only ever called on small graphs. Return a `set`. Any
cover of minimum size is accepted; the checks verify size and validity, never
identity. Raise `ValueError` when the graph has more than 18 distinct nodes.

**`ratio(edges)`** — `len(approx cover) / len(optimum)` as a float, and `1.0`
for a graph with no edges.

```text
vertex_cover_2approx([(0, 1), (1, 2), (2, 3)]) -> ({0, 1, 2, 3}, [(0, 1), (2, 3)])
len(min_vertex_cover([(0, 1), (1, 2), (2, 3)])) -> 2
ratio([(0, 1), (1, 2), (2, 3)])                -> 2.0
```

That last graph is the tight case: the guarantee of 2 is achieved, not merely
approached.
''',
                "files": [{"name": "main.py", "content": r'''
import itertools


def is_vertex_cover(edges, cover):
    """True when every edge has an endpoint in cover."""
    # your code here


def vertex_cover_2approx(edges):
    """(cover set, matching list) from the maximal-matching algorithm."""
    # your code here


def min_vertex_cover(edges):
    """The exact smallest vertex cover, as a set. ValueError above 18 nodes."""
    # your code here


def ratio(edges):
    """Size of the approximation over the size of the optimum; 1.0 with no edges."""
    # your code here


print(vertex_cover_2approx([(0, 1), (1, 2), (2, 3)]))
print(min_vertex_cover([(0, 1), (1, 2), (2, 3)]))
print(ratio([(0, 1), (1, 2), (2, 3)]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import itertools


def _nodes(edges):
    seen = []
    for u, v in edges:
        for x in (u, v):
            if x not in seen:
                seen.append(x)
    return seen


def is_vertex_cover(edges, cover):
    """True when every edge has an endpoint in cover."""
    return all(u in cover or v in cover for u, v in edges)


def vertex_cover_2approx(edges):
    """(cover set, matching list) from the maximal-matching algorithm."""
    cover = set()
    matching = []
    for u, v in edges:
        if u in cover or v in cover:
            continue  # already covered by an earlier pick
        matching.append((min(u, v), max(u, v)))
        cover.add(u)
        cover.add(v)
    return cover, matching


def min_vertex_cover(edges):
    """The exact smallest vertex cover, as a set. ValueError above 18 nodes."""
    nodes = _nodes(edges)
    if len(nodes) > 18:
        raise ValueError(f"exhaustive search refuses {len(nodes)} nodes")
    if not edges:
        return set()
    # Smallest first, so the first cover found is optimal.
    for size in range(1, len(nodes) + 1):
        for combo in itertools.combinations(nodes, size):
            if is_vertex_cover(edges, set(combo)):
                return set(combo)
    return set(nodes)


def ratio(edges):
    """Size of the approximation over the size of the optimum; 1.0 with no edges."""
    if not edges:
        return 1.0
    cover, _matching = vertex_cover_2approx(edges)
    return len(cover) / len(min_vertex_cover(edges))


print(vertex_cover_2approx([(0, 1), (1, 2), (2, 3)]))
print(min_vertex_cover([(0, 1), (1, 2), (2, 3)]))
print(ratio([(0, 1), (1, 2), (2, 3)]))
'''}],
                "hints": [
                    "The approximation is a single pass: skip an edge whose endpoints are already covered, otherwise record it in the matching and add both endpoints.",
                    "`itertools.combinations(nodes, size)` inside a loop over increasing `size` gives you smallest-first exhaustive search for free.",
                    "Collect the node list in first-appearance order rather than through a set, so exhaustive search is reproducible.",
                    "A graph with no edges has an empty optimum — return 1.0 from `ratio` before you divide by zero.",
                ],
                "tests": [
                    {"name": "is_vertex_cover checks every edge", "code": r'''
assert is_vertex_cover([], set()) is True, "an empty graph is covered by nothing"
assert is_vertex_cover([(0, 1), (1, 2)], {1}) is True, f"got {is_vertex_cover([(0, 1), (1, 2)], {1})!r}"
assert is_vertex_cover([(0, 1), (2, 3)], {1}) is False, "edge (2, 3) is uncovered"
assert is_vertex_cover([(0, 1)], {0, 1}) is True
'''},
                    {"name": "the 2-approximation on the path of four nodes", "code": r'''
_cover, _match = vertex_cover_2approx([(0, 1), (1, 2), (2, 3)])
assert _cover == {0, 1, 2, 3}, f"got {_cover!r}"
assert _match == [(0, 1), (2, 3)], f"got {_match!r}"
assert vertex_cover_2approx([]) == (set(), []), f"got {vertex_cover_2approx([])!r}"
_c1, _m1 = vertex_cover_2approx([(5, 9)])
assert _c1 == {5, 9} and _m1 == [(5, 9)], f"got {(_c1, _m1)!r}"
'''},
                    {"name": "the returned matching really is a matching", "code": r'''
import random as _random

_rng = _random.Random(7)
for _trial in range(30):
    _n = _rng.randrange(2, 9)
    _edges = sorted({(min(_a, _b), max(_a, _b))
                     for _a, _b in ((_rng.randrange(_n), _rng.randrange(_n))
                                    for _ in range(_rng.randrange(0, 14))) if _a != _b})
    _cover, _match = vertex_cover_2approx(_edges)
    _seen = set()
    for _u, _v in _match:
        assert _u not in _seen and _v not in _seen, f"matching {_match!r} reuses a vertex"
        _seen.add(_u)
        _seen.add(_v)
    assert len(_cover) == 2 * len(_match), (
        f"cover {_cover!r} should hold both endpoints of each of {len(_match)} matched edges")
    assert is_vertex_cover(_edges, _cover), f"{_cover!r} does not cover {_edges!r}"
'''},
                    {"name": "min_vertex_cover is exact on small graphs", "code": r'''
assert min_vertex_cover([]) == set(), f"got {min_vertex_cover([])!r}"
_path4 = [(0, 1), (1, 2), (2, 3)]
_opt4 = min_vertex_cover(_path4)
assert len(_opt4) == 2, f"the path on four nodes needs two vertices, got {_opt4!r}"
assert is_vertex_cover(_path4, _opt4), f"{_opt4!r} does not cover {_path4!r}"
_star = [(0, 1), (0, 2), (0, 3), (0, 4)]
assert min_vertex_cover(_star) == {0}, f"a star is covered by its centre, got {min_vertex_cover(_star)!r}"
_tri = [(0, 1), (1, 2), (0, 2)]
assert len(min_vertex_cover(_tri)) == 2, f"a triangle needs two vertices, got {min_vertex_cover(_tri)!r}"
assert is_vertex_cover(_tri, min_vertex_cover(_tri))
try:
    min_vertex_cover([(_i, _i + 1) for _i in range(0, 40, 2)])
    assert False, "20 nodes should be refused by the exhaustive search"
except ValueError:
    pass
'''},
                    {"name": "the ratio never exceeds 2 and the certificate bounds OPT", "code": r'''
import random as _random

_rng = _random.Random(7)
_worst = 0.0
for _trial in range(40):
    _n = _rng.randrange(2, 8)
    _edges = sorted({(min(_a, _b), max(_a, _b))
                     for _a, _b in ((_rng.randrange(_n), _rng.randrange(_n))
                                    for _ in range(_rng.randrange(1, 12))) if _a != _b})
    if not _edges:
        continue
    _cover, _match = vertex_cover_2approx(_edges)
    _opt = min_vertex_cover(_edges)
    assert len(_match) <= len(_opt), (
        f"the matching has {len(_match)} disjoint edges, so OPT cannot be {len(_opt)}")
    _r = ratio(_edges)
    assert abs(_r - len(_cover) / len(_opt)) < 1e-12, f"ratio gave {_r!r} for {_edges!r}"
    assert _r <= 2.0 + 1e-12, f"ratio {_r!r} on {_edges!r} breaks the guarantee of 2"
    _worst = max(_worst, _r)
assert _worst > 1.0, "over 40 random graphs the approximation should be suboptimal at least once"
'''},
                    {"name": "the bound is tight, and the empty graph is handled", "code": r'''
assert ratio([]) == 1.0, f"got {ratio([])!r}"
assert ratio([(0, 1)]) == 2.0, f"one edge: the approximation takes both ends, got {ratio([(0, 1)])!r}"
assert ratio([(0, 1), (1, 2), (2, 3)]) == 2.0, (
    f"got {ratio([(0, 1), (1, 2), (2, 3)])!r}; a perfect matching is the tight case")
_disjoint = [(0, 1), (2, 3), (4, 5)]
assert ratio(_disjoint) == 2.0, f"got {ratio(_disjoint)!r}"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a route planner with a preprocessed heuristic",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
Build a road-network route planner in `router.py` and drive it from `main.py`.
The point is not that A* finds the shortest path — Dijkstra already does — but
that a **preprocessed, admissible** heuristic makes it settle far fewer
vertices while returning provably the same cost.

## `Graph`

- `add_node(name, x, y)` — a named vertex at a point in the plane.
- `add_edge(u, v, weight=None)` — undirected. A weight of `None` means the
  straight-line distance between the two endpoints. Raise `ValueError` for an
  unknown endpoint, or for a weight strictly below the straight-line distance:
  the heuristics below are only admissible on a graph where no road is shorter
  than the crow flies.
- `nodes()` — the node names, in insertion order.
- `neighbours(u)` — a list of `(v, weight)`.
- `straight_line(u, v)` — Euclidean distance between two nodes.

## Search

- `dijkstra(graph, source, goal=None)` — returns `(dist, parent, expanded)`,
  where `expanded` counts vertices settled (popped and accepted). With a
  `goal`, stop as soon as it is settled.
- `reconstruct(parent, source, goal)` — the node list, or `[]` when there is no
  parent chain back to the source.
- `astar(graph, source, goal, heuristic)` — returns `(cost, path, expanded)`.
  `heuristic` is a callable from node name to a lower bound on the remaining
  distance. Unreachable goal gives `(math.inf, [], expanded)`.
- `zero_heuristic(graph, goal)` and `euclidean_heuristic(graph, goal)` — both
  return callables. The zero one turns A* back into Dijkstra, which is the
  cheapest possible correctness check you can run on your own search.

## Preprocessing: ALT landmarks

`Landmarks(graph, k=4)` runs one Dijkstra from each of `k` landmark nodes and
stores the resulting distance tables. Choose landmarks by farthest-point
selection starting from the first node, so the choice is deterministic. Then

```text
h(u) = max over landmarks L of abs(dist[L][goal] - dist[L][u])
```

is admissible by the triangle inequality on an undirected graph, and is
consistent. Skip any landmark whose table has no finite entry for `u` or the
goal. `Landmarks.heuristic(goal)` returns the callable.

## Measurement

`compare(graph, source, goal)` returns a dict with keys `cost`, `dijkstra`,
`euclidean` and `landmark`, the last three being expansion counts. The costs
must agree; the counts are the result you are actually reporting.

`grid_graph(width, height, seed=7)` builds the test network: a grid whose edge
weights are the straight-line distance times a random factor in `[1.0, 1.6]`,
so straight-line distance stays a valid lower bound.
''',
        "deliverables": [
            "`router.py` — `Graph`, `dijkstra`, `astar`, `reconstruct`, the three heuristics, `Landmarks`, `compare` and `grid_graph`, importable with no side effects",
            "`main.py` — builds a grid, routes a corner-to-corner journey and prints the three expansion counts side by side",
            "A binary heap search with lazy deletion in both `dijkstra` and `astar`, and an expansion counter that counts settled vertices only",
            "An `add_edge` that refuses a weight below the straight-line distance, with the admissibility argument in its docstring",
            "Landmark preprocessing whose cost is paid once and reused across queries",
            "A measured comparison: identical costs, strictly fewer expansions for the landmark heuristic on a grid",
        ],
        "constraints": [
            "Standard library only — `heapq`, `math` and `random` are all you need",
            "`router.py` must define things only; importing it must print nothing and build no graph",
            "Every heuristic must be admissible on the graphs the module builds; do not scale one to win the measurement",
            "A* must stop when the goal is settled, not when the queue empties",
            "No global caches — two `Landmarks` objects over different graphs must not interfere",
        ],
        "rubric": [
            {"criterion": "Correctness of the searches", "weight": 35,
             "evidence": "Dijkstra, A* with each heuristic and the reconstructed paths all agree on cost over randomised source/goal pairs, including unreachable and self-routes."},
            {"criterion": "Admissibility and consistency", "weight": 25,
             "evidence": "Both heuristics are checked exhaustively against true distances on a small grid; add_edge rejects a sub-Euclidean weight."},
            {"criterion": "Preprocessing quality", "weight": 20,
             "evidence": "Landmark selection is deterministic, tables are built once, and the landmark heuristic expands strictly fewer vertices than plain Dijkstra."},
            {"criterion": "Measurement discipline", "weight": 12,
             "evidence": "compare() reports one cost and three expansion counts drawn from real runs, not from re-derived estimates."},
            {"criterion": "Structure and readability", "weight": 8,
             "evidence": "router.py is import-clean, every public function has a docstring, and the heap invariants are commented where they are subtle."},
        ],
        "hints": [
            "Keep one search loop shape for both algorithms: push `(priority, node)`, pop, skip when the recorded distance is stale, then count the expansion.",
            "In A* the heap key is `g + h`, but the value you relax and store is `g`. Mixing the two is the classic bug and shows up as a wrong cost.",
            "Farthest-point selection: start from `nodes()[0]`, run Dijkstra, take the finite-distance node that is farthest, and repeat using the minimum distance to the landmarks chosen so far.",
            "`abs(dist[L][goal] - dist[L][u])` is a lower bound because `d(u, goal) >= abs(d(L, goal) - d(L, u))` — that is the reverse triangle inequality, and it needs the graph to be undirected.",
            "If A* ever expands more vertices than Dijkstra, your heuristic is not consistent — check that `h(goal)` is exactly 0.",
        ],
        "files": [
            {"name": "router.py", "content": r'''
import heapq
import math
import random


class Graph:
    """An undirected road network whose nodes sit at points in the plane."""

    def __init__(self):
        self.pos = {}
        self.adj = {}
        self.order = []

    def add_node(self, name, x, y):
        """Place a node. Re-adding a name moves it."""
        # your code here

    def straight_line(self, u, v):
        """Euclidean distance between two nodes."""
        # your code here

    def add_edge(self, u, v, weight=None):
        """Undirected edge. None means the straight-line distance."""
        # your code here

    def nodes(self):
        """Node names in insertion order."""
        # your code here

    def neighbours(self, u):
        """[(neighbour, weight), ...] for u."""
        # your code here


def dijkstra(graph, source, goal=None):
    """(dist, parent, expanded) — settles vertices until the queue or the goal runs out."""
    # your code here


def reconstruct(parent, source, goal):
    """The path source..goal as a list of node names, or [] when there is none."""
    # your code here


def zero_heuristic(graph, goal):
    """A heuristic that is always 0, turning A* into Dijkstra."""
    # your code here


def euclidean_heuristic(graph, goal):
    """Straight-line distance to the goal."""
    # your code here


def astar(graph, source, goal, heuristic):
    """(cost, path, expanded) with the given admissible heuristic."""
    # your code here


class Landmarks:
    """ALT preprocessing: one Dijkstra per landmark, reused by every query."""

    def __init__(self, graph, k=4):
        self.graph = graph
        self.chosen = []
        self.tables = {}
        # your code here

    def heuristic(self, goal):
        """A callable node -> lower bound on the distance from that node to goal."""
        # your code here


def compare(graph, source, goal):
    """{cost, dijkstra, euclidean, landmark} — one cost, three expansion counts."""
    # your code here


def grid_graph(width, height, seed=7):
    """A width x height lattice with weights >= the straight-line distance."""
    rng = random.Random(seed)
    g = Graph()
    for r in range(height):
        for c in range(width):
            g.add_node((r, c), float(c), float(r))
    for r in range(height):
        for c in range(width):
            if c + 1 < width:
                g.add_edge((r, c), (r, c + 1), 1.0 + rng.random() * 0.6)
            if r + 1 < height:
                g.add_edge((r, c), (r + 1, c), 1.0 + rng.random() * 0.6)
    return g
'''},
            {"name": "main.py", "content": r'''
from router import grid_graph, compare

net = grid_graph(20, 20)
result = compare(net, (0, 0), (19, 19))

print("cost      ", round(result["cost"], 4))
print("dijkstra  ", result["dijkstra"])
print("euclidean ", result["euclidean"])
print("landmark  ", result["landmark"])
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "router.py", "content": r'''
import heapq
import math
import random


class Graph:
    """An undirected road network whose nodes sit at points in the plane."""

    def __init__(self):
        self.pos = {}
        self.adj = {}
        self.order = []

    def add_node(self, name, x, y):
        """Place a node. Re-adding a name moves it."""
        if name not in self.pos:
            self.order.append(name)
            self.adj[name] = []
        self.pos[name] = (float(x), float(y))

    def straight_line(self, u, v):
        """Euclidean distance between two nodes."""
        if u not in self.pos or v not in self.pos:
            raise ValueError(f"unknown node in ({u!r}, {v!r})")
        ux, uy = self.pos[u]
        vx, vy = self.pos[v]
        return math.hypot(ux - vx, uy - vy)

    def add_edge(self, u, v, weight=None):
        """Undirected edge. None means the straight-line distance.

        A weight below the straight-line distance would break admissibility:
        euclidean_heuristic could then over-estimate and A* could return a
        path that is not shortest. Such an edge is refused outright.
        """
        if u not in self.pos or v not in self.pos:
            raise ValueError(f"unknown node in ({u!r}, {v!r})")
        if u == v:
            raise ValueError("self loops are not roads")
        line = self.straight_line(u, v)
        if weight is None:
            weight = line
        weight = float(weight)
        if weight < line - 1e-9:
            raise ValueError(
                f"weight {weight} is below the straight-line distance {line}")
        self.adj[u].append((v, weight))
        self.adj[v].append((u, weight))

    def nodes(self):
        """Node names in insertion order."""
        return list(self.order)

    def neighbours(self, u):
        """[(neighbour, weight), ...] for u."""
        if u not in self.adj:
            raise ValueError(f"unknown node {u!r}")
        return list(self.adj[u])


def dijkstra(graph, source, goal=None):
    """(dist, parent, expanded) — settles vertices until the queue or the goal runs out."""
    if source not in graph.pos:
        raise ValueError(f"unknown source {source!r}")
    if goal is not None and goal not in graph.pos:
        raise ValueError(f"unknown goal {goal!r}")
    dist = {n: math.inf for n in graph.nodes()}
    parent = {n: None for n in graph.nodes()}
    dist[source] = 0.0
    heap = [(0.0, source)]
    settled = set()
    expanded = 0
    while heap:
        d, u = heapq.heappop(heap)
        # Lazy deletion: an improvement left an older, larger entry behind.
        if u in settled or d > dist[u]:
            continue
        settled.add(u)
        expanded += 1
        if goal is not None and u == goal:
            break
        for v, w in graph.adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, parent, expanded


def reconstruct(parent, source, goal):
    """The path source..goal as a list of node names, or [] when there is none."""
    if goal not in parent:
        return []
    if goal == source:
        return [source]
    path = []
    node = goal
    while node is not None:
        path.append(node)
        if node == source:
            path.reverse()
            return path
        node = parent.get(node)
    return []


def zero_heuristic(graph, goal):
    """A heuristic that is always 0, turning A* into Dijkstra."""
    def h(_node):
        return 0.0
    return h


def euclidean_heuristic(graph, goal):
    """Straight-line distance to the goal."""
    def h(node):
        return graph.straight_line(node, goal)
    return h


def astar(graph, source, goal, heuristic):
    """(cost, path, expanded) with the given admissible heuristic."""
    if source not in graph.pos:
        raise ValueError(f"unknown source {source!r}")
    if goal not in graph.pos:
        raise ValueError(f"unknown goal {goal!r}")
    g_score = {n: math.inf for n in graph.nodes()}
    parent = {n: None for n in graph.nodes()}
    g_score[source] = 0.0
    heap = [(heuristic(source), 0.0, source)]
    settled = set()
    expanded = 0
    while heap:
        _f, g, u = heapq.heappop(heap)
        # The key is g + h, but the value relaxed and stored is always g.
        if u in settled or g > g_score[u]:
            continue
        settled.add(u)
        expanded += 1
        if u == goal:
            return g, reconstruct(parent, source, goal), expanded
        for v, w in graph.adj[u]:
            ng = g + w
            if ng < g_score[v]:
                g_score[v] = ng
                parent[v] = u
                heapq.heappush(heap, (ng + heuristic(v), ng, v))
    return math.inf, [], expanded


class Landmarks:
    """ALT preprocessing: one Dijkstra per landmark, reused by every query."""

    def __init__(self, graph, k=4):
        self.graph = graph
        self.chosen = []
        self.tables = {}
        names = graph.nodes()
        if not names or k <= 0:
            return
        current = names[0]
        for _ in range(min(k, len(names))):
            table = dijkstra(graph, current)[0]
            self.chosen.append(current)
            self.tables[current] = table
            # Farthest-point selection: the next landmark is the node whose
            # smallest distance to the chosen set is largest.
            best, best_d = None, -1.0
            for n in names:
                if n in self.tables:
                    continue
                spread = min(self.tables[L][n] for L in self.chosen)
                if spread != math.inf and spread > best_d:
                    best, best_d = n, spread
            if best is None:
                break
            current = best

    def heuristic(self, goal):
        """A callable node -> lower bound on the distance from that node to goal."""
        tables = self.tables
        chosen = self.chosen

        def h(node):
            best = 0.0
            for L in chosen:
                table = tables[L]
                du = table.get(node, math.inf)
                dg = table.get(goal, math.inf)
                if du == math.inf or dg == math.inf:
                    continue
                # Reverse triangle inequality on an undirected graph.
                bound = abs(dg - du)
                if bound > best:
                    best = bound
            return best

        return h


def compare(graph, source, goal):
    """{cost, dijkstra, euclidean, landmark} — one cost, three expansion counts."""
    dist, parent, dij_expanded = dijkstra(graph, source, goal)
    cost = dist[goal]
    e_cost, _e_path, e_expanded = astar(
        graph, source, goal, euclidean_heuristic(graph, goal))
    marks = Landmarks(graph)
    l_cost, _l_path, l_expanded = astar(
        graph, source, goal, marks.heuristic(goal))
    if not (math.isinf(cost) and math.isinf(e_cost)):
        assert abs(e_cost - cost) < 1e-9, "euclidean A* disagreed with Dijkstra"
    if not (math.isinf(cost) and math.isinf(l_cost)):
        assert abs(l_cost - cost) < 1e-9, "landmark A* disagreed with Dijkstra"
    return {
        "cost": cost,
        "dijkstra": dij_expanded,
        "euclidean": e_expanded,
        "landmark": l_expanded,
    }


def grid_graph(width, height, seed=7):
    """A width x height lattice with weights >= the straight-line distance."""
    rng = random.Random(seed)
    g = Graph()
    for r in range(height):
        for c in range(width):
            g.add_node((r, c), float(c), float(r))
    for r in range(height):
        for c in range(width):
            if c + 1 < width:
                g.add_edge((r, c), (r, c + 1), 1.0 + rng.random() * 0.6)
            if r + 1 < height:
                g.add_edge((r, c), (r + 1, c), 1.0 + rng.random() * 0.6)
    return g
'''},
            {"name": "main.py", "content": r'''
from router import grid_graph, compare

net = grid_graph(20, 20)
result = compare(net, (0, 0), (19, 19))

print("cost      ", round(result["cost"], 4))
print("dijkstra  ", result["dijkstra"])
print("euclidean ", result["euclidean"])
print("landmark  ", result["landmark"])
'''},
        ],
        "tests": [
            {"name": "Graph stores nodes, edges and distances", "code": r'''
from router import Graph

_g = Graph()
_g.add_node("a", 0, 0)
_g.add_node("b", 3, 4)
_g.add_node("c", 3, 0)
assert _g.nodes() == ["a", "b", "c"], f"nodes() gave {_g.nodes()!r}, expected insertion order"
assert abs(_g.straight_line("a", "b") - 5.0) < 1e-9, f"got {_g.straight_line('a', 'b')!r}"
_g.add_edge("a", "b")
assert abs(_g.neighbours("a")[0][1] - 5.0) < 1e-9, "a weight of None means the straight line"
assert ("a", 5.0) in [(_n, round(_w, 9)) for _n, _w in _g.neighbours("b")], \
    f"edges are undirected, b sees {_g.neighbours('b')!r}"
_g.add_edge("a", "c", 7.5)
assert ("c", 7.5) in _g.neighbours("a"), f"got {_g.neighbours('a')!r}"
'''},
            {"name": "add_edge refuses what would break admissibility", "code": r'''
from router import Graph

_g = Graph()
_g.add_node("a", 0, 0)
_g.add_node("b", 3, 4)
for _bad in [("a", "b", 4.9), ("a", "zz", 1.0), ("a", "a", 1.0)]:
    try:
        _g.add_edge(*_bad)
        assert False, f"add_edge{_bad!r} should raise ValueError"
    except ValueError:
        pass
_g.add_edge("a", "b", 5.0)
assert len(_g.neighbours("a")) == 1, "a weight equal to the straight line is legal"
'''},
            {"name": "dijkstra and reconstruct on a hand-checkable network", "code": r'''
import math as _math
from router import Graph, dijkstra, reconstruct

_g = Graph()
for _n, _x, _y in [("a", 0, 0), ("b", 1, 0), ("c", 2, 0), ("d", 3, 0), ("z", 9, 9)]:
    _g.add_node(_n, _x, _y)
_g.add_edge("a", "b", 1.0)
_g.add_edge("b", "c", 1.0)
_g.add_edge("c", "d", 1.0)
_g.add_edge("a", "d", 10.0)
_dist, _parent, _exp = dijkstra(_g, "a")
assert abs(_dist["d"] - 3.0) < 1e-9, f"dist to d is {_dist['d']!r}, expected 3.0"
assert _dist["z"] == _math.inf, f"z is unreachable, got {_dist['z']!r}"
assert _exp == 4, f"four reachable vertices should be settled, got {_exp!r}"
assert reconstruct(_parent, "a", "d") == ["a", "b", "c", "d"], \
    f"got {reconstruct(_parent, 'a', 'd')!r}"
assert reconstruct(_parent, "a", "a") == ["a"], "the source is its own path"
assert reconstruct(_parent, "a", "z") == [], "no path means an empty list"
'''},
            {"name": "A* returns Dijkstra's cost with every heuristic", "code": r'''
import random as _random
from router import grid_graph, dijkstra, astar, zero_heuristic, euclidean_heuristic, Landmarks

_net = grid_graph(12, 12)
_marks = Landmarks(_net)
_names = _net.nodes()
_rng = _random.Random(7)
for _trial in range(25):
    _s = _rng.choice(_names)
    _t = _rng.choice(_names)
    _want = dijkstra(_net, _s, _t)[0][_t]
    for _label, _h in [("zero", zero_heuristic(_net, _t)),
                       ("euclidean", euclidean_heuristic(_net, _t)),
                       ("landmark", _marks.heuristic(_t))]:
        _cost, _path, _exp = astar(_net, _s, _t, _h)
        assert abs(_cost - _want) < 1e-9, (
            f"{_label} A* from {_s!r} to {_t!r} gave {_cost!r}, Dijkstra says {_want!r}")
        assert _path[0] == _s and _path[-1] == _t, f"{_label} path {_path!r} is wrong at the ends"
'''},
            {"name": "the returned path is walkable and costs what is claimed", "code": r'''
import random as _random
from router import grid_graph, astar, euclidean_heuristic

_net = grid_graph(10, 10)
_names = _net.nodes()
_rng = _random.Random(11)
for _trial in range(15):
    _s, _t = _rng.choice(_names), _rng.choice(_names)
    _cost, _path, _exp = astar(_net, _s, _t, euclidean_heuristic(_net, _t))
    _walk = 0.0
    for _i in range(len(_path) - 1):
        _step = [_w for _v, _w in _net.neighbours(_path[_i]) if _v == _path[_i + 1]]
        assert _step, f"{_path[_i]!r} -> {_path[_i + 1]!r} is not an edge"
        _walk += min(_step)
    assert abs(_walk - _cost) < 1e-9, f"path {_path!r} walks {_walk!r} but you reported {_cost!r}"
'''},
            {"name": "both heuristics are admissible, checked exhaustively", "code": r'''
from router import grid_graph, dijkstra, euclidean_heuristic, Landmarks

_net = grid_graph(7, 7)
_marks = Landmarks(_net)
for _goal in [(0, 0), (3, 4), (6, 6)]:
    _true = dijkstra(_net, _goal)[0]
    _he = euclidean_heuristic(_net, _goal)
    _hl = _marks.heuristic(_goal)
    assert abs(_he(_goal)) < 1e-12, f"h(goal) must be 0, euclidean gave {_he(_goal)!r}"
    assert abs(_hl(_goal)) < 1e-12, f"h(goal) must be 0, landmark gave {_hl(_goal)!r}"
    for _n in _net.nodes():
        assert _he(_n) <= _true[_n] + 1e-9, (
            f"euclidean h({_n!r}) = {_he(_n)!r} over-estimates the true {_true[_n]!r}")
        assert _hl(_n) <= _true[_n] + 1e-9, (
            f"landmark h({_n!r}) = {_hl(_n)!r} over-estimates the true {_true[_n]!r}")
'''},
            {"name": "landmark preprocessing is deterministic and reusable", "code": r'''
from router import grid_graph, Landmarks

_net = grid_graph(8, 8)
_a = Landmarks(_net, 4)
_b = Landmarks(_net, 4)
assert _a.chosen == _b.chosen, f"landmark choice must be deterministic: {_a.chosen!r} vs {_b.chosen!r}"
assert len(_a.chosen) == 4, f"asked for 4 landmarks, got {_a.chosen!r}"
assert len(set(_a.chosen)) == 4, f"landmarks repeat: {_a.chosen!r}"
assert all(len(_t) == 64 for _t in _a.tables.values()), "each table covers every node"
_small = Landmarks(grid_graph(2, 2), 10)
assert len(_small.chosen) <= 4, f"cannot choose more landmarks than nodes: {_small.chosen!r}"
_other = Landmarks(grid_graph(5, 5), 2)
assert _a.chosen != _other.chosen or len(_other.chosen) == 2, "two Landmarks must not share state"
assert len(_a.chosen) == 4, "building a second Landmarks must not disturb the first"
'''},
            {"name": "a heuristic pays for itself in expansions", "code": r'''
import random as _random
from router import grid_graph, dijkstra, astar, euclidean_heuristic, Landmarks

_net = grid_graph(16, 16)
_marks = Landmarks(_net)
_names = _net.nodes()
_rng = _random.Random(7)
_wins = 0
_pairs = 0
for _trial in range(12):
    _s, _t = _rng.choice(_names), _rng.choice(_names)
    if _s == _t:
        continue
    _pairs += 1
    _dij = dijkstra(_net, _s, _t)[2]
    _euc = astar(_net, _s, _t, euclidean_heuristic(_net, _t))[2]
    _lan = astar(_net, _s, _t, _marks.heuristic(_t))[2]
    assert _euc <= _dij, f"euclidean A* expanded {_euc} against Dijkstra's {_dij}"
    assert _lan <= _dij, f"landmark A* expanded {_lan} against Dijkstra's {_dij}"
    if _lan < _dij:
        _wins += 1
assert _pairs > 0
assert _wins >= _pairs - 1, (
    f"the landmark heuristic beat Dijkstra on only {_wins} of {_pairs} routes — "
    "check that the bound is the max over landmarks, not the first one")
'''},
            {"name": "degenerate routes", "code": r'''
import math as _math
from router import Graph, astar, euclidean_heuristic, zero_heuristic, grid_graph, compare

_net = grid_graph(5, 5)
_cost, _path, _exp = astar(_net, (2, 2), (2, 2), euclidean_heuristic(_net, (2, 2)))
assert _cost == 0.0 and _path == [(2, 2)], f"routing to yourself gave {(_cost, _path)!r}"
_split = Graph()
_split.add_node("a", 0, 0)
_split.add_node("b", 1, 0)
_split.add_node("x", 50, 50)
_split.add_edge("a", "b")
_c, _p, _e = astar(_split, "a", "x", euclidean_heuristic(_split, "x"))
assert _c == _math.inf and _p == [], f"an unreachable goal gives (inf, []), got {(_c, _p)!r}"
for _bad in [("a", "nope"), ("nope", "a")]:
    try:
        astar(_split, _bad[0], _bad[1], zero_heuristic(_split, _bad[1]))
        assert False, f"astar with unknown node {_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "compare reports one cost and three real counts", "code": r'''
import math as _math
from router import grid_graph, dijkstra, compare

_net = grid_graph(14, 14)
_r = compare(_net, (0, 0), (13, 13))
assert set(_r) == {"cost", "dijkstra", "euclidean", "landmark"}, f"keys were {sorted(_r)}"
_want = dijkstra(_net, (0, 0), (13, 13))[0][(13, 13)]
assert abs(_r["cost"] - _want) < 1e-9, f"cost {_r['cost']!r}, expected {_want!r}"
for _k in ("dijkstra", "euclidean", "landmark"):
    assert isinstance(_r[_k], int) and _r[_k] > 0, f"{_k} count was {_r[_k]!r}"
assert _r["euclidean"] <= _r["dijkstra"], f"got {_r!r}"
assert _r["landmark"] < _r["dijkstra"], (
    f"the whole point is fewer expansions: {_r!r}")
'''},
            {"name": "grid_graph weights never undercut the straight line", "code": r'''
from router import grid_graph

_net = grid_graph(6, 6)
assert len(_net.nodes()) == 36, f"got {len(_net.nodes())} nodes"
for _u in _net.nodes():
    for _v, _w in _net.neighbours(_u):
        assert _w >= _net.straight_line(_u, _v) - 1e-9, (
            f"edge {_u!r}-{_v!r} weighs {_w!r}, below the straight line "
            f"{_net.straight_line(_u, _v)!r}")
assert len(_net.neighbours((0, 0))) == 2, f"a corner has two roads, got {_net.neighbours((0, 0))!r}"
assert len(_net.neighbours((3, 3))) == 4, "an interior node has four"
'''},
            {"name": "router.py is import-clean", "code": r'''
_src = open("router.py").read()
assert "print(" not in _src, "router.py defines the library; the printing belongs in main.py"
assert "cost" in _out and "landmark" in _out, (
    f"main.py should print the comparison; stdout was {_out!r}")
'''},
        ],
    },
}
