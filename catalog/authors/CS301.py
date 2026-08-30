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
            "quiz": {
                "title": "Reading a recurrence off an algorithm",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Merge sort satisfies `T(n) = 2T(n/2) + Theta(n)`. What does the `Theta(n)` term pay for?",
                        "opts": [
                            "The merge: one linear pass over the two sorted halves, once the recursive calls have returned",
                            "The two recursive calls, which the additive term prices separately from the rest",
                            "Finding the midpoint, which the divide step has to do before it can recurse",
                            "The base cases, since the recursion bottoms out once per element",
                        ],
                        "a": 0,
                        "why": r"""
The additive term is the work one call does itself, outside the recursion: split, then
merge. Splitting is a pair of slice indices and costs nothing worth naming; the merge
walks both halves once, and that is where the `n` comes from. The recursive calls are
already priced by `2T(n/2)`, and adding them again is the commonest way to write a
recurrence that says nothing. The base cases really do number `n`, but they are the
leaves of the tree this recurrence describes — the recursion adds them up for you, and
`T(1)` is what each of them costs.
""",
                    },
                    {
                        "q": "`T(n) = 3T(n/2) + Theta(n)` is Karatsuba's shape. Which bound does the master theorem give?",
                        "opts": [
                            "`Theta(n^(log_2 3))`, about `n^1.585` — the leaves dominate",
                            "`Theta(n log n)` — the levels each cost the same",
                            "`Theta(n)` — the combine at the root dominates",
                            "`Theta(n^(log_3 2))`, about `n^0.63` — the leaves dominate",
                        ],
                        "a": 0,
                        "why": r"""
Compare `d = 1` against `log_b a = log_2 3`, which is about 1.585. The combine is
cheaper than the recursion it feeds, so the cost per level grows on the way down and
the bottom level swallows the total: that is case 1, and the exponent is `log_b a`.
`n log n` is what you get when the two are equal, which is merge sort's `2T(n/2)`, not
this. `Theta(n)` would need the combine to dominate, which is case 3 and needs `d`
above 1.585. And `log_3 2` is the same two numbers the wrong way round: it is below 1,
which would claim that three subproblems of half the size cost less than a single pass
over the array.
""",
                    },
                    {
                        "q": "Both recursive calls have returned and `d` is the better of their two distances. Why is it enough to compare each point of the strip against only the next seven in y-order?",
                        "opts": [
                            "Two points closer than `d` must share a `2d`-by-`d` box straddling the split line, and each half already has its own points at least `d` apart, so at most eight points fit in that box",
                            "Because the strip itself never holds more than eight points",
                            "Because seven is what keeps the scan linear, so the constant was picked to make the bound come out",
                            "Because the points are sorted by y, so the distance to each later point is larger than to the one before",
                        ],
                        "a": 0,
                        "why": r"""
The box argument. A point that beats `d` lies within `d` of the split line in x and
within `d` in y, so both ends of the improving pair sit in a `2d`-by-`d` rectangle. The
recursion has already proved that no two points inside one half are closer than `d`, so
at most four fit in each `d`-by-`d` square and at most eight in the rectangle — seven
successors is the whole neighbourhood. The strip can hold every point in the input, so
bounding its size gets you nowhere. The constant falls out of the geometry rather than
being chosen to fit the bound. And it is the y-*difference* that grows monotonically
along the scan, not the distance, which is exactly what the early exit
`strip[j][1] - strip[i][1] >= d` tests.
""",
                    },
                    {
                        "q": "Which of these turns an `O(n log n)` closest pair into `O(n log^2 n)`?",
                        "opts": [
                            "Sorting the strip by y inside every recursive call instead of carrying one y-order down from the top",
                            "Using `math.hypot` rather than comparing squared distances",
                            "Recursing into both halves rather than into only the half that looks promising",
                            "Sorting the whole input by x once before the recursion starts",
                        ],
                        "a": 0,
                        "why": r"""
A sort inside the call makes the combine step `O(n log n)` instead of `O(n)`, so the
recurrence becomes `T(n) = 2T(n/2) + O(n log n)` and each of the `log n` levels costs
`n log n`. That is the defect the module names: the code still produces the right pair,
so only the clock catches it. `hypot` versus squared distances is a constant factor and
a readability question. Recursing into one half is not an optimisation but a wrong
answer, since the closest pair may lie entirely on either side. And the two sorts before
the recursion are the fix, not the fault — they are what the y-order is threaded down
from.
""",
                    },
                    {
                        "q": "Merging the halves `[2, 5]` and `[1, 3]` of `[2, 5, 1, 3]`, the merge emits `1` first. How many inversions does that one step account for?",
                        "opts": ["2", "1", "0", "3"],
                        "a": 0,
                        "why": r"""
`1` is smaller than every element still unconsumed in the left half — both `2` and `5` —
and in the original array all of them sit to its left, so one comparison settles two
inverted pairs at once. That is what `total += len(left) - i` is counting. Incrementing
by one per emission would be tallying merge steps rather than pairs. Zero would say the
right half never contributes anything, which is the whole point of the merge. Three is
the count for the entire array, `(2,1)`, `(5,1)` and `(5,3)` — and the last of those is
settled later, when `3` is emitted over the remaining `5`.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Counting inversions inside the merge",
                "minutes": 9,
                "caption": "inversions.py — four decisions removed",
                "lang": "python",
                "brief": r"""
The counting version of merge sort differs from the ordinary one by three lines, and
each of them is somewhere an off-by-one or a comparison can go in wrong without
changing the sorted output at all. Fill the holes, then read the last line as the price
of what you built.
""",
                "listing": """def _sort_and_count(xs):
    \"\"\"Return (sorted copy, inversion count) for xs.\"\"\"
    if len(xs) <= 1:
        return xs, 0
    mid = len(xs) // 2
    left, li = _sort_and_count(xs[:mid])
    right, ri = _sort_and_count(xs[mid:])

    merged, total = [], ___
    i = j = 0
    while i < len(left) and j < len(right):
        if ___:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
            total += ___
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, total

# two halves, one linear merge:  T(n) = ___ T(n/2) + Theta(n)  ->  Theta(n log n)
""",
                "blanks": [
                    {
                        "prompt": "Both halves have already been counted. What does this call's running total start from?",
                        "hole": "?",
                        "opts": ["li + ri", "0", "max(li, ri)", "li * ri"],
                        "a": 0,
                        "why": "Every inversion is either inside one half or crosses between them. The recursive calls have counted the first kind, and the merge below is about to add the second, so the two counts are carried forward and added to.",
                        "whys": [
                            "Every inversion is either inside one half or crosses between them. The recursive calls have counted the first kind, and the merge below is about to add the second, so the two counts are carried forward and added to.",
                            "Starting at zero throws away everything the recursion just computed, and the function returns only the pairs that cross the top-level split: `[5, 4, 3, 2, 1]` would come back as 6 instead of 10.",
                            "Keeping the larger of the two counts silently drops the other. The two halves are disjoint sets of pairs, so their counts add rather than compete.",
                            "A product corresponds to no set of pairs at all, and it collapses to zero the moment either half happens to be sorted.",
                        ],
                    },
                    {
                        "prompt": "Which comparison keeps equal values from being counted as an inversion?",
                        "hole": "?",
                        "opts": ["left[i] <= right[j]", "left[i] < right[j]", "left[i] >= right[j]", "i <= j"],
                        "a": 0,
                        "why": "Ties go to the left half. An equal pair is not an inversion, and taking the left element first means the counting branch never runs for it.",
                        "whys": [
                            "Ties go to the left half. An equal pair is not an inversion, and taking the left element first means the counting branch never runs for it.",
                            "Strict `<` sends ties down the else branch, where the total is incremented — so `[1, 1, 1]` would report inversions that do not exist, while the sorted output looks perfectly correct.",
                            "Reversed, this emits the larger element first: the list comes back descending, and the count becomes the number of pairs that are already in order.",
                            "Comparing positions rather than values interleaves the two halves by index. Nothing is sorted and nothing meaningful is counted.",
                        ],
                    },
                    {
                        "prompt": "The right-hand element has just jumped the queue. Over how many left-hand elements?",
                        "hole": "?",
                        "opts": ["len(left) - i", "1", "len(right) - j", "len(left)"],
                        "a": 0,
                        "why": "Everything from `left[i]` onwards is larger than the element just emitted and stood to its left in the original array, so a single comparison settles all of those pairs at once. That is precisely where the linear merge buys the whole `n log n`.",
                        "whys": [
                            "Everything from `left[i]` onwards is larger than the element just emitted and stood to its left in the original array, so a single comparison settles all of those pairs at once. That is precisely where the linear merge buys the whole `n log n`.",
                            "Adding one per emission counts merge steps rather than inverted pairs, and caps the answer at `n` per merge — nowhere near the `n(n-1)/2` a fully reversed array contains.",
                            "The right half is where the emitted element came from. Every pair being settled has its other end in the left half.",
                            "`len(left)` forgets that the first `i` left-hand elements are already emitted: they were smaller, so they are not inverted with this one. Every merge after the first then overcounts.",
                        ],
                    },
                    {
                        "prompt": "Two subproblems of half the size, plus a linear merge. What is the branching factor?",
                        "hole": "?",
                        "opts": ["2", "1", "n", "log n"],
                        "a": 0,
                        "why": "Two subproblems of half the size and a linear combine: `a = 2`, `b = 2`, `d = 1`, so `log_b a = d` and the master theorem's second case gives `n log n`.",
                        "whys": [
                            "Two subproblems of half the size and a linear combine: `a = 2`, `b = 2`, `d = 1`, so `log_b a = d` and the master theorem's second case gives `n log n`.",
                            "One subproblem of half the size is binary search, `T(n) = T(n/2) + Theta(1)`, which is logarithmic and never merges two halves because it only ever visits one.",
                            "`n` subproblems of half the size is not a recursion anyone can afford: the call count explodes faster than any polynomial in `n`.",
                            "`log n` is the depth of this recursion, not its branching factor. It belongs in the answer, not in the recurrence.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "From the recursion tree to the closed form",
                "minutes": 14,
                "vars": ["a", "b", "c", "d", "n", "k", "L", "T"],
                "brief": r"""
Every algorithm in this module produces the same shape:

$$T(n) = a\,T(n/b) + c\,n^{d}$$

Take $n$ to be a power of $b$, so the tree is exactly $L = \log_b n$ levels deep below
the root and the base cases sit at level $L$. The master theorem is not a rule to look
up; it is the sum of the level costs, and the three cases are the three things a
geometric series can do. Price one level, then add them up.
""",
                "steps": [
                    {
                        "prompt": "Level 0 is the original call. How many subproblems are there at level $k$?",
                        "answer": "a^{k}",
                        "hint": "Each call makes $a$ of them, and level $k$ is $k$ rounds of that.",
                        "deconstruct": [
                            "Level 0 holds one call.",
                            "Every level down multiplies the count by $a$, so after $k$ levels it has been multiplied $k$ times.",
                        ],
                    },
                    {
                        "prompt": "How big is each of those subproblems, in terms of $n$, $b$ and $k$?",
                        "answer": r"\frac{n}{b^{k}}",
                        "hint": "Every level divides the size by $b$.",
                        "deconstruct": [
                            "Level 1 holds subproblems of size $n/b$.",
                            "Level 2 divides again, giving $n/b^{2}$. Level $k$ has divided $k$ times.",
                        ],
                    },
                    {
                        "prompt": "Each of those calls pays $c$ times its own size to the power $d$ for its combine step. Write the cost of the whole of level $k$, using $c$, $n$, $d$, $a$, $b$ and $k$.",
                        "answer": r"c \cdot n^{d} \cdot \left(\frac{a}{b^{d}}\right)^{k}",
                        "hint": "Multiply the count by the cost of one call, then gather everything that carries a $k$ into a single $k$-th power.",
                        "deconstruct": [
                            r"The count is $a^{k}$ and one call costs $c\,(n/b^{k})^{d}$.",
                            r"That product is $c\,a^{k}\,n^{d}/b^{kd}$, and $a^{k}/b^{kd}$ is one factor raised to $k$.",
                        ],
                    },
                    {
                        "prompt": "That is a geometric series in $k$. What is the ratio between the cost of one level and the cost of the level above it?",
                        "answer": r"\frac{a}{b^{d}}",
                        "hint": "Divide the level-$(k+1)$ cost by the level-$k$ cost. Everything except the $k$-th power cancels.",
                        "deconstruct": [
                            "Only the factor carrying the exponent $k$ changes from one level to the next.",
                            "So the ratio is that factor itself — the same at every level, which is what makes the series geometric.",
                        ],
                    },
                    {
                        "prompt": "Merge sort has $a = b = 2$ and $d = 1$, so that ratio is exactly 1 and every level costs the same. Counting the $L + 1$ levels from the root down to the base cases, what is the total, in terms of $c$, $n$ and $L$?",
                        "answer": r"c \cdot n \cdot (L + 1)",
                        "hint": "Work out what one level costs when the ratio is 1, then count the levels.",
                        "deconstruct": [
                            r"Level $k$ costs $c\,n^{d}(a/b^{d})^{k} = c\,n \cdot 1^{k} = c\,n$.",
                            "Levels $0$ through $L$ inclusive is $L + 1$ of them.",
                        ],
                    },
                    {
                        "prompt": "Karatsuba has $a = 3$, $b = 2$, $d = 1$: the ratio is $3/2$, the series grows, and the bottom level dominates the sum. How many subproblems sit at that bottom level, in terms of $a$ and $L$?",
                        "answer": "a^{L}",
                        "hint": "It is the level count from the first step, read at $k = L$.",
                        "deconstruct": [
                            "Level $k$ holds $a^{k}$ calls.",
                            "The base cases are the level $k = L$.",
                        ],
                    },
                ],
                "closing": r"""
All three cases of the master theorem are that one sum, finishing differently. Ratio
exactly 1: $L + 1$ equal terms, and with $L = \log_2 n$ that is the $\Theta(n \log n)$
everyone quotes for merge sort. Ratio above 1: the sum is within a constant of its last
term, and $a^{L} = a^{\log_b n} = n^{\log_b a}$ — the exponent `master_case` returns in
case 1, and the reason Karatsuba beats the schoolbook method at all. Ratio below 1: the
series converges, the root term $c\,n^{d}$ carries the bound, and you are in case 3.
Nothing was memorised; the tree was just added up.
""",
            },
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
            "quiz": {
                "title": "The bill a greedy rule runs up",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Which rule schedules the largest number of compatible intervals?",
                        "opts": [
                            "Earliest finishing time",
                            "Earliest starting time",
                            "Shortest duration",
                            "Fewest conflicts with the intervals still available",
                        ],
                        "a": 0,
                        "why": r"""
Finishing earliest leaves the most room behind it, and the exchange argument makes that
precise: take any optimal schedule, swap its first interval for the one that finishes
earliest, and it is still compatible and still the same size. Earliest start dies on
`[(0, 10), (1, 2), (3, 4)]`, where one long interval swallows the day. Shortest duration
dies on `[(0, 3), (2, 4), (3, 6)]`, where the short middle interval blocks both of its
neighbours — the lab checks exactly that instance. Fewest conflicts is the one that
takes real effort to refute, and it is refuted: a counterexample is a standard figure in
Kleinberg & Tardos, where the least-conflicted interval still costs you the optimum.
""",
                    },
                    {
                        "q": "Huffman merges the two least frequent subtrees first. What does that guarantee about the two least frequent symbols?",
                        "opts": [
                            "They become siblings at the deepest level of the tree, so their codes are the same length and differ only in the last bit",
                            "They get the shortest codes, since they are dealt with first",
                            "Their codes have equal length only when their frequencies are equal",
                            "They never end up in the same subtree",
                        ],
                        "a": 0,
                        "why": r"""
Being merged first means being buried deepest: every later merge adds a bit to the front
of everything already in the subtree. Siblings hang off one parent, so their codewords
are the parent's prefix plus `0` and plus `1` — the same length whatever the two
frequencies are. Merged first therefore means longest, not shortest, which is the whole
economy of the code: rare symbols pay the long codewords so frequent ones can have short
ones. And far from being kept apart, they are the one pair the algorithm guarantees to
put together.
""",
                    },
                    {
                        "q": "A binary prefix-free code has codeword lengths 1, 2, 3, 3. What does the Kraft sum come to, and what does that tell you?",
                        "opts": [
                            "Exactly 1 — the tree is full, so no codeword could be shortened without breaking prefix-freeness",
                            "Exactly 1 — which is the arithmetic signature of a code that is not prefix-free",
                            "0.75 — there is a spare leaf, so one codeword could be made shorter",
                            "1.25 — which is why no such code exists",
                        ],
                        "a": 0,
                        "why": r"""
`1/2 + 1/4 + 1/8 + 1/8 = 1`, realised by `0`, `10`, `110`, `111`. Prefix-freeness forces
the sum to at most 1, because reserving a codeword of length `l` blocks a `2^-l` share
of the tree and the shares cannot overlap. Equality says every leaf is spoken for: the
tree is full, no internal node has an only child, and there is nothing left to shorten
into. A sum strictly below 1 is the interesting failure — it means a codeword could have
been shorter, so the code is not optimal, and it is why the lab asserts the Huffman
output hits 1 exactly rather than merely staying under it.
""",
                    },
                    {
                        "q": "With coins 1, 3 and 4, `greedy_failure` returns 6. Why is 6 the smallest counterexample and not something below it?",
                        "opts": [
                            "For every amount below 6 the largest coin that fits belongs to some optimal solution; at 6 the greedy 4 leaves 2, costing two more coins, where 3 + 3 costs one",
                            "Because 6 is the first amount larger than the largest coin",
                            "Because 6 is the first amount that is not itself a coin",
                            "Because 6 is a multiple of 3, and greedy never reaches for the 3",
                        ],
                        "a": 0,
                        "why": r"""
Walk it: 1, 3 and 4 are single coins; 2 is `1+1` either way; 5 is `4+1` and no better.
At 6 greedy commits to the 4 and is left with a 2 it can only pay in ones, three coins
against the optimum's `3+3`. Being past the largest coin is not the trigger — 5 is
already past it and greedy is fine there. Nor is being a non-coin: 2 and 5 are not coins
and neither breaks the rule. And greedy does use the 3, at 3 itself; its mistake is
taking the 4 at 6, which is a different thing from never taking the 3 at all.
""",
                    },
                    {
                        "q": "You suspect a proposed greedy rule is not optimal. What is enough to establish that?",
                        "opts": [
                            "One instance where it returns a strictly worse answer than the true optimum, exhibited and checked against that optimum",
                            "A proof that no exchange argument can be built for it",
                            "A family of instances on which its ratio grows without bound",
                            "An instance where it disagrees with a different greedy rule",
                        ],
                        "a": 0,
                        "why": r"""
Refutation is existential, which is why it is so much cheaper than justification: one
instance settles it forever, and `greedy_failure` finds it by searching upwards from 1
so the counterexample is also the smallest. It has to be measured against the true
optimum — that is why the lab makes you write the dynamic program alongside the greedy
rule. Showing that no exchange argument exists is far harder than the claim itself, and
would still leave open some other proof. An unbounded ratio is a much stronger result
than needed. And two heuristics disagreeing tells you at most one of them is wrong,
without saying which.
""",
                    },
                ],
            },
            "blanks": {
                "title": "A session with the three greedy rules",
                "minutes": 8,
                "caption": "python -i main.py — after the lab's functions are defined",
                "lang": "text",
                "brief": r"""
Four calls against the reference implementation. Nothing here needs a table or a proof;
each line is one greedy rule doing exactly what it says it does, and the interesting
part is which of them gets away with it.
""",
                "listing": """>>> schedule([(0, 3), (2, 4), (3, 6)])
___
>>> greedy_coin_count([1, 3, 4], 6)
___
>>> optimal_coin_count([1, 3, 4], 6)
___
>>> huffman_cost({"a": 5, "b": 2, "c": 1})
___
""",
                "blanks": [
                    {
                        "prompt": "Earliest finishing time, returned in finishing order.",
                        "hole": "?",
                        "opts": ["[(0, 3), (3, 6)]", "[(2, 4)]", "[(0, 3), (2, 4)]", "[(0, 3)]"],
                        "a": 0,
                        "why": "Sorted by finish, `(0, 3)` comes first and is taken. `(2, 4)` starts at 2, before the 3 already committed, so it is skipped; `(3, 6)` starts exactly at 3 and the intervals are half-open, so it fits.",
                        "whys": [
                            "Sorted by finish, `(0, 3)` comes first and is taken. `(2, 4)` starts at 2, before the 3 already committed, so it is skipped; `(3, 6)` starts exactly at 3 and the intervals are half-open, so it fits.",
                            "That is what shortest-duration returns — it takes the two-unit interval in the middle, which then blocks both of its neighbours and leaves a schedule of one. This is the instance that refutes the rule.",
                            "These two overlap on the half-open interval `[2, 3)`, so they are not a compatible set at all; `schedule` never returns two intervals that share a point.",
                            "Stopping after the first interval leaves `(3, 6)` on the table, and it is compatible with what was already chosen. The algorithm keeps scanning to the end of the sorted list.",
                        ],
                    },
                    {
                        "prompt": "Largest coin first, from 1, 3 and 4.",
                        "hole": "?",
                        "opts": ["3", "2", "6", "None"],
                        "a": 0,
                        "why": "The 4 fits, leaving 2, which the 3 cannot help with: two 1s finish the job. Three coins.",
                        "whys": [
                            "The 4 fits, leaving 2, which the 3 cannot help with: two 1s finish the job. Three coins.",
                            "Two coins is the optimum, not what this rule finds. Greedy has already spent the 4 before it could consider the pair of 3s.",
                            "Six is the amount, not the number of coins; the all-ones solution would indeed be six coins, but greedy takes the largest coin that fits, not the smallest.",
                            "`None` is reserved for a stranded remainder, which needs a coin system without a 1 — `[2, 5]` at 3 is the case that produces it.",
                        ],
                    },
                    {
                        "prompt": "The true minimum, from the table.",
                        "hole": "?",
                        "opts": ["2", "3", "1", "None"],
                        "a": 0,
                        "why": "`3 + 3`. The dynamic program considers every coin at every value, so it is never trapped by an early commitment the way the greedy rule is — and the gap between this line and the greedy count is what `greedy_failure` searches for.",
                        "whys": [
                            "`3 + 3`. The dynamic program considers every coin at every value, so it is never trapped by an early commitment the way the greedy rule is — and the gap between this line and the greedy count is what `greedy_failure` searches for.",
                            "Three is the greedy count. If the table returned the same number there would be no counterexample at 6 at all.",
                            "There is no single coin worth 6 in this system, so one coin cannot do it.",
                            "`None` means unreachable, and 6 is plainly reachable: any amount is, once the system contains a 1.",
                        ],
                    },
                    {
                        "prompt": "Total encoded length for a: 5, b: 2, c: 1.",
                        "hole": "?",
                        "opts": ["11", "8", "16", "9"],
                        "a": 0,
                        "why": "Merge the two lightest, `b` and `c`, into a subtree of weight 3, then merge that with `a` for a root of 8. Codes: `a` one bit, `b` and `c` two bits each, so `5*1 + 2*2 + 1*2 = 11`.",
                        "whys": [
                            "Merge the two lightest, `b` and `c`, into a subtree of weight 3, then merge that with `a` for a root of 8. Codes: `a` one bit, `b` and `c` two bits each, so `5*1 + 2*2 + 1*2 = 11`.",
                            "Eight is the total number of symbol occurrences, which is what the text would cost at one bit each — and one bit each is impossible for three symbols.",
                            "Sixteen is the fixed-length price: three symbols need two bits apiece, and 8 occurrences at 2 bits is 16. Huffman's saving is exactly the 5 bits between that and 11.",
                            "Nine would need the code lengths to be shorter than the tree allows; the only shape available for three symbols is one at depth 1 and two at depth 2.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "What the Huffman code costs",
                "minutes": 8,
                "brief": r"""
Huffman's rule is one line long — merge the two lightest subtrees, repeat — and the
number it produces is the thing the lab's `huffman_cost` returns. Build the tree by
hand here. Doing it once by hand is what makes the invariant obvious later: the total is
also the sum of the weights of every node the merging created.
""",
                "prompt": "How many bits does the encoded text take?",
                "note": "Whole bits. The text is 100 symbols long.",
                "figure": "A hundred symbols of text over a five-letter alphabet, with the counts listed. Build the Huffman code, then add up the length of each symbol's codeword times the number of times that symbol appears.",
                "given": [
                    {"label": "A", "value": "40 occurrences"},
                    {"label": "B", "value": "25 occurrences"},
                    {"label": "C", "value": "15 occurrences"},
                    {"label": "D", "value": "12 occurrences"},
                    {"label": "E", "value": "8 occurrences"},
                ],
                "aside": "Every merge buries one more subtree by one more bit, so the running total of the merged weights is the encoded length — which is usually quicker to add up than the codewords are to read off.",
                "answer": 215,
                "tol": 0.5,
                "unit": "bits",
                "hint": "Merge E and D first. Keep merging the two lightest of what is left, and write down the weight of each subtree you create.",
                "wrong": "300 is the fixed-length code: five symbols need three bits each, and 100 symbols at 3 bits is 300. The whole point of the exercise is the gap between that and what Huffman charges.",
                "why": r"""
The merges are `E+D = 20`, then `C+20 = 35`, then `B+35 = 60`, then `A+60 = 100`. Adding
the weights of those four created nodes gives `20 + 35 + 60 + 100 = 215`. Reading it off
the codewords instead: `A` sits at depth 1, `B` at 2, `C` at 3, `D` and `E` at 4, so
`40*1 + 25*2 + 15*3 + 12*4 + 8*4 = 40 + 50 + 45 + 48 + 32 = 215`. Against the 300 bits a
fixed-length code would spend that is a saving of 28%, bought entirely by giving the
40-occurrence symbol a single bit. Note also that no symbol more frequent than another
got a longer codeword — the invariant the lab asserts, and the reason the code cannot be
improved.
""",
            },
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
            "quiz": {
                "title": "Subproblems, tables and witnesses",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In the edit-distance table, what does cell `(i, j)` hold?",
                        "opts": [
                            "The distance between the first `i` characters of `a` and the first `j` characters of `b`",
                            "The distance between the single characters `a[i]` and `b[j]`",
                            "The cost of the cheapest operation available at position `(i, j)`",
                            "The number of operations still to come after `i` deletions and `j` insertions",
                        ],
                        "a": 0,
                        "why": r"""
Naming the subproblem is the whole design step, and here it is *prefixes*: cell
`(i, j)` is the answer to a smaller instance of the same question. That is what makes
the recurrence local — every way of finishing off `a[:i]` and `b[:j]` ends in exactly
one of three moves, each of which lands on a neighbouring cell. It also explains the
borders: `(i, 0)` is `a[:i]` against nothing, which costs `i` deletions. A cell about
two single characters would carry no history and nothing could be built on it; a cell
holding a per-position cost would be the recurrence's input rather than its output.
""",
                    },
                    {
                        "q": "Why do the checks replay your edit script instead of comparing it against a stored one?",
                        "opts": [
                            "Because ties are real: several scripts can achieve the same cost, so the check confirms yours turns `a` into `b` at the cost you claim",
                            "Because the value of the optimum is not unique either",
                            "Because the table can be filled in any order and the script depends on that order",
                            "Because a reconstructed script can come out cheaper than the table's value",
                        ],
                        "a": 0,
                        "why": r"""
The value of an optimum is unique — that is what makes it an optimum — but the witness
almost never is. `form` to `from` costs 2 whether you delete the `o` and re-insert it
after the `r` or substitute both letters where they stand, and a grader that demanded
one specific script would fail correct work. So the
check replays: consume `a`, apply each operation, and see whether `b` comes out and
whether the non-match operations number exactly the cost. The table's fill order is
fixed by the dependencies, and a script cheaper than the table's value would mean the
table was wrong, not that the reconstruction was clever.
""",
                    },
                    {
                        "q": "Items `(weight, value)` of `(6, 9)`, `(5, 7)`, `(5, 7)` with capacity 10. What does value-density greedy get, and what is the optimum?",
                        "opts": [
                            "9 against 14 — greedy takes the densest item, and then nothing else fits",
                            "14 against 14 — density greedy is optimal whenever every item fits individually",
                            "16 against 14 — greedy overfills the sack and has to be corrected",
                            "9 against 16 — the optimum takes all three items",
                        ],
                        "a": 0,
                        "why": r"""
Densities are `9/6 = 1.5` and `7/5 = 1.4`, so greedy takes the 6-weight item first and
is left with 4 units of capacity that nothing fits into: 9. The table takes both 5s for
14. What makes this the honest counterexample rather than a trick is that the greedy
rule *is* optimal on the fractional problem, where it would take the 6 and then
four-fifths of a 5 for `9 + 5.6 = 14.6`. Indivisibility is the entire difficulty, which
is why there is a table here and a one-line sort in the fractional version. All three
items weigh 16 together, so they never fit, and no correct algorithm ever exceeds the
capacity.
""",
                    },
                    {
                        "q": "You shrink the knapsack table to two rolling rows to save memory. What does that cost you?",
                        "opts": [
                            "The back-walk: you can report the best value but no longer which items achieved it",
                            "Nothing — the reconstruction only ever reads the final row",
                            "The optimal value, which now depends on the order the rows are visited in",
                            "The ability to handle zero-weight items",
                        ],
                        "a": 0,
                        "why": r"""
The reconstruction asks, for each `i` from the bottom up, whether `table[i][c]` differs
from `table[i-1][c]` — a question about a row that a rolling implementation has already
overwritten. The value survives intact, because each row only ever reads the one above
it, and that is exactly why the space reduction works at all. Recovering the witness in
small space is possible but not free: Hirschberg's divide-and-conquer does it for
sequence alignment at the price of running the fill twice. Zero-weight items are
unaffected either way, and they are worth testing precisely because `while weight <= c`
conditions like to get them wrong.
""",
                    },
                    {
                        "q": "How does the longest common subsequence relate to edit distance?",
                        "opts": [
                            "Forbid substitution and the cheapest script deletes and inserts everything outside a longest common subsequence, for a cost of `len(a) + len(b) - 2 * lcs`",
                            "They are equal whenever the two strings have the same length",
                            "`lcs` is always `max(len(a), len(b))` minus the unit-cost edit distance",
                            "There is no relation — one maximises and the other minimises",
                        ],
                        "a": 0,
                        "why": r"""
The two tables are nearly the same table, which is why the module puts them side by
side. A deletion-only-and-insertion-only script has to remove from `a` and add to `b`
everything not held in common, and the characters it can keep are exactly a common
subsequence — making the script cheapest means making that subsequence longest. For
`AGGTAB` and `GXTXAYB` the LCS is `GTAB`, so the deletion-and-insertion distance is
`6 + 7 - 8 = 5`. Unit-cost edit distance is a different quantity, because a substitution
buys a delete and an insert for the price of one, so the equality only holds under that
restriction — a same-length coincidence is not enough.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The edit-distance recurrence",
                "minutes": 8,
                "caption": "the recurrence, with its borders and two of its three moves removed",
                "lang": "text",
                "brief": r"""
Written out, the recurrence is four lines: two borders and a choice of three moves.
Everything else in `edit_distance` — the loops, the back-walk — is bookkeeping around
this. Note that the table is indexed by prefix *lengths*, so `D[i][j]` is about
`a[:i]` and `b[:j]`, while the characters being compared are `a[i-1]` and `b[j-1]`.
""",
                "listing": """D[i][0] = ___                      # a[:i] against the empty string
D[0][j] = ___                      # the empty string against b[:j]

if a[i-1] == b[j-1]:
    D[i][j] = D[i-1][j-1]          # free: the characters already agree
else:
    D[i][j] = 1 + min(D[i-1][j-1], # substitute a[i-1] for b[j-1]
                      ___,         # delete a[i-1], emitting nothing
                      ___)         # insert b[j-1], consuming nothing
""",
                "blanks": [
                    {
                        "prompt": "Turning a prefix of a into nothing.",
                        "hole": "?",
                        "opts": ["i", "0", "j", "1"],
                        "a": 0,
                        "why": "`a[:i]` is `i` characters and every one of them has to go, at one deletion each. This border is what stops the recurrence from falling off the edge of the table.",
                        "whys": [
                            "`a[:i]` is `i` characters and every one of them has to go, at one deletion each. This border is what stops the recurrence from falling off the edge of the table.",
                            "Zero would say any prefix can be turned into nothing for free, and the whole first column would then undercut every path that runs through it — `edit_distance('abc', '')` would come back as 0.",
                            "`j` is the length of the other prefix, and in this column there is no other prefix: the column is defined by `b[:0]`, which is empty.",
                            "One flat cost per row would price a hundred deletions the same as one. The cost model is unit cost per operation, not per cell.",
                        ],
                    },
                    {
                        "prompt": "Building a prefix of b out of nothing.",
                        "hole": "?",
                        "opts": ["j", "0", "i", "len(b)"],
                        "a": 0,
                        "why": "Symmetrical to the other border: `b[:j]` is `j` characters and each has to be inserted. Only the empty-against-empty corner is 0, and it is where the back-walk finishes.",
                        "whys": [
                            "Symmetrical to the other border: `b[:j]` is `j` characters and each has to be inserted. Only the empty-against-empty corner is 0, and it is where the back-walk finishes.",
                            "Zero along the whole top row would make `edit_distance('', 'abc')` free, when in fact it costs three insertions — the lab checks that case explicitly.",
                            "`i` indexes the wrong string here. In row 0 there is nothing of `a` left to be indexed by anything.",
                            "`len(b)` is a constant, so it would charge the same for one insertion as for all of them, and cell `(0, 0)` would stop being 0.",
                        ],
                    },
                    {
                        "prompt": "Delete: a character of `a` is consumed and nothing is emitted.",
                        "hole": "?",
                        "opts": ["D[i-1][j]", "D[i-1][j-1]", "D[i][j]", "D[i+1][j]"],
                        "a": 0,
                        "why": "Dropping `a[i-1]` shortens the `a` side by one and leaves the `b` side untouched, so the rest of the work is the subproblem one row up in the same column.",
                        "whys": [
                            "Dropping `a[i-1]` shortens the `a` side by one and leaves the `b` side untouched, so the rest of the work is the subproblem one row up in the same column.",
                            "Both indices moving is the substitute move, and it is already the first argument of the `min`. Listing it twice loses the delete option entirely, and strings that need a deletion come out too expensive.",
                            "A cell cannot be defined in terms of itself. That is not a recurrence, it is a loop the fill order can never satisfy.",
                            "Indices increase downwards through the table, so `i+1` is a cell that has not been computed yet — and reading it would mean recursing away from the base cases instead of towards them.",
                        ],
                    },
                    {
                        "prompt": "Insert: a character of `b` is emitted and nothing is consumed.",
                        "hole": "?",
                        "opts": ["D[i][j-1]", "D[j][i]", "D[i-1][j-1]", "D[i][j+1]"],
                        "a": 0,
                        "why": "Emitting `b[j-1]` accounts for one more character of `b` while `a` stands still, so the remaining work is the cell one column to the left.",
                        "whys": [
                            "Emitting `b[j-1]` accounts for one more character of `b` while `a` stands still, so the remaining work is the cell one column to the left.",
                            "Swapping the indices reads the table for the reversed pair of prefixes. It is not even in range once the two strings have different lengths.",
                            "That is the substitute move again, already accounted for. With both the delete and the insert replaced by it, the recurrence could only ever handle equal-length strings.",
                            "`j+1` is a column still to be filled. The dependencies of this table all point up and to the left, which is what lets the two loops run forwards.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Why the knapsack table is not a polynomial-time algorithm",
                "minutes": 12,
                "vars": ["n", "W", "b", "T", "c"],
                "brief": r"""
`knapsack` fills one row per item and one column per capacity. Two nested loops, no
recursion, no cleverness — it looks polynomial, and it is not. Count the cells, then
count the characters of input that produced them.
""",
                "steps": [
                    {
                        "prompt": "The table has a row for each of the $n$ items plus one for no items at all, and a column for every capacity from $0$ to $W$. How many cells is that?",
                        "answer": r"(n + 1) \cdot (W + 1)",
                        "hint": "Rows times columns, and mind both off-by-ones: capacity 0 gets a column to itself.",
                        "deconstruct": [
                            "Rows: $n + 1$, counting the empty row the back-walk finishes on.",
                            "Columns: $W + 1$, counting capacity $0$.",
                        ],
                    },
                    {
                        "prompt": "Each cell is one comparison between two entries already in the table, so the running time is proportional to the number of cells. Expand the product and keep only the term that grows fastest.",
                        "answer": r"n \cdot W",
                        "hint": "Multiply it out. Three of the four terms are dominated by the fourth once both $n$ and $W$ are large.",
                        "deconstruct": [
                            r"$(n+1)(W+1) = nW + n + W + 1$.",
                            "The product term outgrows the two linear terms and the constant.",
                        ],
                    },
                    {
                        "prompt": "Now measure the input rather than the table. The capacity arrives written as a binary number of $b$ bits. What is the largest $W$ those bits can express?",
                        "answer": "2^{b} - 1",
                        "hint": "$b$ bits, every one of them set.",
                        "deconstruct": [
                            "One bit reaches 1, two bits reach 3, three bits reach 7.",
                            "Each is one below the next power of two.",
                        ],
                    },
                    {
                        "prompt": "Substitute that into the leading term. Write the work in terms of $n$ and $b$.",
                        "answer": r"n \cdot (2^{b} - 1)",
                        "hint": "You have $nW$, and you have just written $W$ in terms of $b$.",
                        "deconstruct": [
                            "The leading term was $n\\,W$.",
                            "And the largest $W$ that $b$ bits can hold is $2^{b} - 1$.",
                        ],
                    },
                    {
                        "prompt": "The input grows by one character: $b$ becomes $b+1$ while $n$ stays put. Roughly what factor does the work grow by?",
                        "answer": "2",
                        "hint": "Compare $2^{b+1}$ with $2^{b}$. The $-1$ stops mattering almost immediately.",
                        "deconstruct": [
                            r"The ratio is exactly $(2^{b+1} - 1)/(2^{b} - 1)$.",
                            "The two $-1$s leave that a shade above 2 — 2.33 at $b = 2$, 2.001 at $b = 10$ — closing on 2 from above as $b$ grows, so it is indistinguishable from 2 for any $b$ worth worrying about.",
                        ],
                    },
                ],
                "closing": r"""
Nothing here is wrong with the algorithm. `knapsack` is the right way to solve the
problem and on the capacities in the lab it is instant. The point is what the word
*polynomial* measures: polynomial in the **length of the input**, and the capacity
contributes $b$ characters while costing $2^{b}$ work. Ten more items make the table ten
rows taller; ten more bits of capacity make it a thousand times wider. That asymmetry is
what *pseudo-polynomial* names, and it is why 0/1 knapsack is NP-hard in spite of a
table this simple — and why the same trick fails outright on a problem whose numbers are
not bounded, which is the subject of the last module.
""",
            },
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
            "quiz": {
                "title": "Which algorithm, and what it assumes",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why does Dijkstra insist on non-negative weights?",
                        "opts": [
                            "Its invariant is that a vertex's distance is final the moment it is extracted, and a negative edge elsewhere could lower it afterwards",
                            "Because a binary heap cannot order negative keys correctly",
                            "Because a negative weight only makes sense on a directed graph, and Dijkstra assumes an undirected one",
                            "It does not — Dijkstra is fine with negative edges as long as there is no negative cycle",
                        ],
                        "a": 0,
                        "why": r"""
The proof that the extracted vertex is settled runs: any other route to it leaves the
settled set at some point, and everything after that point costs at least 0, so the
route cannot be shorter. Remove the non-negativity and the argument evaporates. It is
not about cycles, either — take `a->b` at 2, `a->c` at 3 and `c->b` at -2. There is no
cycle at all, and Dijkstra still settles `b` at 2 while the true distance is 1. A heap
orders negative numbers perfectly well; it is the algorithm above the heap that breaks.
Tolerating negative edges without a negative cycle is exactly what Bellman-Ford is for.
""",
                    },
                    {
                        "q": "What is the guard `if d > dist[u]: continue` doing right after the pop?",
                        "opts": [
                            "Discarding a heap entry that a later improvement has superseded, which is what lets you skip decrease-key entirely",
                            "Detecting a negative weight before it can corrupt the distances",
                            "Stopping the search once the goal has been settled",
                            "Preventing the same vertex from being pushed onto the heap twice",
                        ],
                        "a": 0,
                        "why": r"""
Lazy deletion. When a vertex's distance improves, the old entry is still sitting in the
heap and there is no cheap way to reach in and rewrite it — a real decrease-key needs
handles into the heap and roughly doubles the amount of code. So the entry is left to
rot, and this line throws it away when it surfaces. Far from preventing duplicate
pushes, the guard is what makes them safe: there is at most one push per successful
relaxation, so the heap never holds more than `E + 1` entries and the `log` factor is
`log E`, which is `O(log V)` on a simple graph.
""",
                    },
                    {
                        "q": "Bellman-Ford relaxes every edge for `V - 1` rounds. Why that many?",
                        "opts": [
                            "A shortest path with no repeated vertex has at most `V - 1` edges, and after round `k` every shortest path of `k` edges or fewer is correct",
                            "Because the `V`-th round is reserved for the negative-cycle test, so one round has to be given up",
                            "Because a spanning tree has `V - 1` edges, and the shortest-path tree is a spanning tree",
                            "Because the distances converge geometrically and `V - 1` is a safe over-estimate",
                        ],
                        "a": 0,
                        "why": r"""
Induction on the number of edges in the path. After the first full pass, every vertex
one edge from the source is correct; after the second, every vertex two edges away; and
a simple path cannot use more than `V - 1` edges without revisiting a vertex, which a
shortest path has no reason to do when there is no negative cycle. The test round is a
consequence of that bound rather than its cause: since `V - 1` rounds suffice, any
further improvement proves the assumption of no negative cycle was wrong. The
shortest-path tree does have `V - 1` edges when everything is reachable, but that is a
coincidence of counting, not the argument.
""",
                    },
                    {
                        "q": "A negative cycle sits in a component the source cannot reach. Why must `bellman_ford` stay silent about it?",
                        "opts": [
                            "The distances it reports are distances from the source, and nothing that cycle does changes any of them",
                            "Because the `V - 1` rounds would have found it already if it mattered",
                            "Because a negative cycle in a disconnected component cannot exist in a directed graph",
                            "Because Bellman-Ford only ever inspects edges leaving a vertex it has already relaxed",
                        ],
                        "a": 0,
                        "why": r"""
The function answers one question — how far is everything from the source — and an
unreachable cycle leaves every one of those answers at `inf`. Raising would be a refusal
to answer a question that has a perfectly good answer, and the lab pins it down with a
graph containing both a reachable component and a separate negative loop. Keeping the
distinction alive is what the `dist[u] != inf` guard on each relaxation is for. Note
that Bellman-Ford scans the whole edge list every round, settled or not; that is exactly
why the unreachable cycle turns up under its nose and has to be deliberately ignored.
""",
                    },
                    {
                        "q": "Union-find with path compression and union by size costs what per operation, and what does that mean for Kruskal?",
                        "opts": [
                            "Near-constant amortised — inverse Ackermann in the number of elements, below 5 for any input that fits in memory — so Kruskal's cost is the sort",
                            "Exactly constant in the worst case, which is why Kruskal is linear once the edges are sorted",
                            "Logarithmic in the worst case per operation, and that is where Kruskal's `E log E` comes from",
                            "Logarithmic amortised, matching the heap operations in Dijkstra",
                        ],
                        "a": 0,
                        "why": r"""
The two optimisations together give an amortised bound of the inverse Ackermann
function, which is at most 4 or 5 for any number of elements that can physically exist.
So the union-find is not what Kruskal pays for: sorting `E` edges is `E log E`, and the
`E` union operations on top of it are near-linear. A single `find` can still walk a long
path in the worst case — the bound is amortised, not worst-case per operation, and the
compression that flattens the path is what pays for the next caller.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Dijkstra's inner loop",
                "minutes": 9,
                "caption": "dijkstra.py — the pop, the guard and the relaxation",
                "lang": "python",
                "brief": r"""
`dist` and `parent` are already initialised, `dist[source]` is 0 and the heap holds
`(0, source)`. What is left is the loop, and all four holes are places where a wrong
choice still produces plausible-looking numbers for most graphs.
""",
                "listing": """while heap:
    d, u = heapq.heappop(heap)
    if u in settled or ___:
        continue                      # a stale entry an improvement left behind
    settled.add(u)
    for v, w in graph.get(u, ()):
        nd = ___
        if nd < dist[v]:
            dist[v] = nd
            parent[v] = ___
            heapq.heappush(heap, (___, v))
""",
                "blanks": [
                    {
                        "prompt": "The lazy-deletion guard: which entries are safe to throw away?",
                        "hole": "?",
                        "opts": ["d > dist[u]", "d < dist[u]", "d == dist[u]", "u in graph"],
                        "a": 0,
                        "why": "A popped entry carrying a distance larger than the best one recorded is a leftover from before an improvement, and re-expanding from it would only waste time. Anything smaller than `dist[u]` is impossible, since `dist[u]` is only ever lowered to a value that was pushed.",
                        "whys": [
                            "A popped entry carrying a distance larger than the best one recorded is a leftover from before an improvement, and re-expanding from it would only waste time. Anything smaller than `dist[u]` is impossible, since `dist[u]` is only ever lowered to a value that was pushed.",
                            "This throws away the live entry and keeps the stale ones. Every vertex would be skipped on its real distance, and nothing past the source would ever be expanded.",
                            "Equality is the condition for the entry being current, so this skips exactly the entries worth processing.",
                            "Membership in the adjacency map has nothing to do with staleness, and note the polarity: this skips the vertices that *are* keys of `graph`. The source has outgoing edges, so it is a key, so it is discarded on the very first pop — `settled` stays empty, the relaxation loop never runs once, and every distance except the source's is still infinity at the end. The only vertices it would let through are the ones that appear solely as neighbours, which have nothing to relax anyway.",
                        ],
                    },
                    {
                        "prompt": "The tentative distance to `v` through `u`.",
                        "hole": "?",
                        "opts": ["d + w", "dist[v] + w", "w", "d + dist[v]"],
                        "a": 0,
                        "why": "`d` is the settled distance to `u` and `w` is the edge to `v`, so the route being offered costs `d + w`. Using `dist[u]` in place of `d` would be equally correct here, and that is exactly why the guard above is allowed to trust `d`.",
                        "whys": [
                            "`d` is the settled distance to `u` and `w` is the edge to `v`, so the route being offered costs `d + w`. Using `dist[u]` in place of `d` would be equally correct here, and that is exactly why the guard above is allowed to trust `d`.",
                            "Starting from `dist[v]` measures the new route from the destination's current estimate rather than from the source, so distances only ever grow and the comparison below can never fire.",
                            "The edge weight alone forgets how far away `u` was — every vertex adjacent to anything would end up one edge from the source.",
                            "Adding two distances-from-the-source together is not a route at all; it is also `inf` for every unvisited `v`, so nothing would ever improve.",
                        ],
                    },
                    {
                        "prompt": "Who is `v` reached through?",
                        "hole": "?",
                        "opts": ["u", "v", "None", "d"],
                        "a": 0,
                        "why": "The parent is the vertex the improving route came from, which is what makes the array walkable backwards from any target to the source. `shortest_path` is nothing but that walk, reversed.",
                        "whys": [
                            "The parent is the vertex the improving route came from, which is what makes the array walkable backwards from any target to the source. `shortest_path` is nothing but that walk, reversed.",
                            "A vertex as its own parent is a one-step cycle, and the reconstruction loop would never terminate.",
                            "`None` marks the source and the unreachable vertices, so writing it here erases the path while keeping the cost — the distance would be right and every path would come back as a single node.",
                            "`d` is a number, not a vertex. The walk would stop at the first thing it could not look up.",
                        ],
                    },
                    {
                        "prompt": "The key the heap orders by.",
                        "hole": "?",
                        "opts": ["nd", "d", "w", "nd + w"],
                        "a": 0,
                        "why": "The priority has to be the new distance from the source, which is the quantity the extraction invariant is about: pop the smallest and it is settled.",
                        "whys": [
                            "The priority has to be the new distance from the source, which is the quantity the extraction invariant is about: pop the smallest and it is settled.",
                            "Pushing `u`'s distance under `v`'s name makes the heap order by where you came from. Vertices would be extracted in an order that has nothing to do with how far away they are, and the guard above would then reject most of them.",
                            "Ordering by edge weight is a greedy walk along cheap edges — that is closer to Prim's rule for a spanning tree than to a shortest path, and it does not even give you Prim, since the visited set is wrong.",
                            "Charging the edge twice inflates every key, and the inflation differs per vertex, so the extraction order stops matching the distances that were actually recorded.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "What Bellman-Ford costs when the graph is dense",
                "minutes": 11,
                "vars": ["V", "E", "T"],
                "brief": r"""
Bellman-Ford does not look at the shape of the graph. It relaxes every edge, once per
round, and the number of rounds comes from the vertex count alone. Price it in
relaxation attempts, then compare it against what Dijkstra does on the same graph — the
comparison comes out as a single clean factor.
""",
                "steps": [
                    {
                        "prompt": "The implementation runs $V - 1$ relaxation rounds and then one further round as the negative-cycle test. How many passes over the edge list is that in the worst case?",
                        "answer": "V",
                        "hint": "$V-1$ rounds that relax, and one that only checks.",
                        "deconstruct": [
                            "$V - 1$ relaxation rounds, one per possible edge of a simple path.",
                            "Plus the single test round, which relaxes nothing but reads everything.",
                        ],
                    },
                    {
                        "prompt": "Each pass touches every edge exactly once. Write the total number of relaxation attempts $T$.",
                        "answer": r"V \cdot E",
                        "hint": "Passes times edges per pass.",
                        "deconstruct": [
                            "There are $V$ passes.",
                            "Each pass is $E$ attempts, whether or not any of them improves anything.",
                        ],
                    },
                    {
                        "prompt": "Now make the graph dense: a complete directed graph on $V$ vertices, one edge for every ordered pair of distinct vertices. How many edges is that?",
                        "answer": r"V \cdot (V - 1)",
                        "hint": "Every vertex points at every other vertex, and the two directions are separate edges.",
                        "deconstruct": [
                            "Each of the $V$ vertices has $V - 1$ others to point at.",
                            "No self-loops, and $(u, v)$ is a different edge from $(v, u)$.",
                        ],
                    },
                    {
                        "prompt": "Substitute that into $T$ and write the total in terms of $V$ alone.",
                        "answer": r"V^{2} \cdot (V - 1)",
                        "hint": "You have $T = V\\,E$, and you have just written $E$.",
                        "deconstruct": [
                            r"$T = V \cdot E$.",
                            r"$E = V(V-1)$, so $T = V \cdot V \cdot (V-1)$.",
                        ],
                    },
                    {
                        "prompt": "Dijkstra settles each vertex once and relaxes each edge once, so it makes $V + E$ relaxation attempts before the heap factor is counted. On this same complete graph, what does the ratio $T/(V+E)$ come to?",
                        "answer": "V - 1",
                        "hint": "Work out $V + E$ for the complete graph first. It collapses to a single power of $V$.",
                        "deconstruct": [
                            r"$V + E = V + V(V-1) = V + V^{2} - V$.",
                            r"That is $V^{2}$, and $T = V^{2}(V-1)$, so almost everything cancels.",
                        ],
                    },
                ],
                "closing": r"""
So on a dense graph the extra generality costs a factor of $V - 1$ in relaxations,
before either algorithm's constant factors are counted. That is the trade being made
every time you choose between them: Bellman-Ford survives a negative edge and reports a
negative cycle, Dijkstra does neither and touches each edge once. Two honest caveats.
Dijkstra's heap adds a $\log V$ factor that this ratio ignores, so the real gap on a
dense graph is nearer $V/\log V$. And the `bellman_ford` in the lab breaks out of the
round loop the moment a round changes nothing, which helps enormously on real graphs and
not at all on the worst case this bound describes.
""",
            },
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
            "quiz": {
                "title": "Guarantees, certificates and the wall",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why does the 2-approximation add **both** endpoints of the edge it picks?",
                        "opts": [
                            "It has no way to tell which endpoint an optimal cover would use, and taking both keeps the picked edges vertex-disjoint, which is what the certificate needs",
                            "Because a vertex cover has to contain both endpoints of every edge",
                            "Because taking one endpoint would leave the picked edge uncovered",
                            "Because the cover it builds has to be a maximal matching",
                        ],
                        "a": 0,
                        "why": r"""
One endpoint would cover that edge perfectly well — the difficulty is that you cannot
tell which one is the useful choice, and choosing badly is unbounded rather than merely
suboptimal: on a star, picking the leaf every time costs `n - 1` vertices where the
centre alone would have done. Taking both costs a factor of exactly 2 and buys the thing
that makes the factor provable, namely that the picked edges share no vertex. A cover is
not a matching, and it is definitionally false that a cover needs both endpoints of an
edge — that would make the only cover the whole vertex set.
""",
                    },
                    {
                        "q": "The algorithm returns a matching alongside the cover. What does that matching certify?",
                        "opts": [
                            "`OPT >= len(matching)`, because the matched edges share no vertex, so any cover has to spend a distinct vertex on each of them",
                            "`OPT <= len(matching)`, which is what bounds the cover from above",
                            "`OPT == 2 * len(matching)`, which is why the ratio is exactly 2",
                            "Nothing about `OPT` — it only records how the cover was built",
                        ],
                        "a": 0,
                        "why": r"""
The certificate is a **lower** bound, and that is the hard half: the cover's size is
right there in front of you, while `OPT` is the thing nobody can compute. The matching
supplies it for free. Because no two matched edges share a vertex, no single vertex can
cover two of them, so every cover — the optimal one included — is at least as large as
the matching. Put that beside `len(cover) == 2 * len(matching)` and the ratio of 2
follows without ever computing `OPT`. Claiming equality would be far too strong: on a
triangle the matching has one edge and `OPT` is 2.
""",
                    },
                    {
                        "q": "`ratio([(0, 1), (1, 2), (2, 3)])` is exactly 2.0. What makes that instance tight?",
                        "opts": [
                            "The edges it picks happen to form a perfect matching, so it takes all four vertices, while `{1, 2}` covers everything",
                            "Every path graph gives a ratio of 2, whatever order the edges arrive in",
                            "The optimum is 4 and the approximation found 8",
                            "Every connected graph gives a ratio of 2 — that is what a worst-case guarantee means",
                        ],
                        "a": 0,
                        "why": r"""
The algorithm picks `(0, 1)`, which leaves `(1, 2)` already covered, then picks
`(2, 3)`: two disjoint edges, four vertices, and the middle two would have sufficed. The
guarantee is achieved rather than approached, which is what stops anyone proving a
better constant for this algorithm. The order matters, though, and that is why the lab
fixes it: hand the same path in as `[(1, 2), (0, 1), (2, 3)]` and the algorithm picks
the middle edge, covers everything with two vertices and scores 1.0. A worst-case
guarantee is an upper bound on every instance, not a prediction about any of them — the
triangle scores 1.0 too.
""",
                    },
                    {
                        "q": "Vertex cover is NP-complete. Which reading of that is right?",
                        "opts": [
                            "The decision version — is there a cover of size at most `k`? — is in NP and every problem in NP reduces to it; the optimisation version is NP-hard",
                            "Every instance of it takes exponential time to solve",
                            "No approximation algorithm with a constant ratio can exist for it",
                            "It is a statement that the problem lies outside NP",
                        ],
                        "a": 0,
                        "why": r"""
NP-completeness is a statement about reductions and about membership, and both halves
matter: the decision version is in NP because a cover of size `k` is a certificate
anyone can check in linear time, and it is hard because every problem in NP reduces to
it. The optimisation version cannot be in NP at all — "this is the smallest" is not
something a witness settles — so it is called NP-hard instead. Nothing about that says
individual instances are hard: the lab's exhaustive search handles 18 nodes without
complaint, trees are easy, and bipartite graphs fall to matching. And the algorithm in
this very module is a constant-factor approximation, so the third reading is refuted by
the code you are about to write.
""",
                    },
                    {
                        "q": "Why is 'repeatedly take the highest-degree vertex' not a constant-factor approximation?",
                        "opts": [
                            "There are graph families on which its ratio grows like `log n`, so no constant bounds it",
                            "Because it can fail to produce a cover at all",
                            "Because it is slower than the matching algorithm",
                            "Because it produces no certificate, and without a certificate no ratio can exist",
                        ],
                        "a": 0,
                        "why": r"""
It is the more intelligent-looking rule, it beats the matching algorithm on most graphs
you would draw by hand, and it has no constant guarantee: bipartite families can be
built where it is dragged into taking about `log n` times the optimum. That is the
lesson worth carrying out of this module — a heuristic that usually wins and an
algorithm with a proof are different kinds of object. It does always produce a cover,
and it is not meaningfully slower. As for certificates: an algorithm's ratio is a fact
about the algorithm whether or not it hands you the evidence, and the matching is
valuable because it makes the bound checkable per instance rather than only provable in
general.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Reading the guarantee off four calls",
                "minutes": 8,
                "caption": "python -i main.py — the star, the triangle and three disjoint edges",
                "lang": "text",
                "brief": r"""
The guarantee says the cover is never more than twice the optimum. It says nothing
about any particular graph, and these four calls are the difference between those two
statements: two of them are as good as an exact algorithm, one of them is the worst the
bound allows.
""",
                "listing": """>>> cover, matching = vertex_cover_2approx([(0, 1), (0, 2), (0, 3)])
>>> sorted(cover), matching
([0, 1], ___)
>>> len(min_vertex_cover([(0, 1), (0, 2), (0, 3)]))
___
>>> ratio([(0, 1), (1, 2), (0, 2)])
___
>>> ratio([(0, 1), (2, 3), (4, 5)])
___
""",
                "blanks": [
                    {
                        "prompt": "Which edges did the algorithm pick on the star?",
                        "hole": "?",
                        "opts": ["[(0, 1)]", "[(0, 1), (0, 2), (0, 3)]", "[(0, 1), (0, 2)]", "[]"],
                        "a": 0,
                        "why": "The first edge is picked and both its endpoints go into the cover. Every remaining edge touches vertex 0, so all of them are already covered and none is picked. One edge in the matching, two vertices in the cover.",
                        "whys": [
                            "The first edge is picked and both its endpoints go into the cover. Every remaining edge touches vertex 0, so all of them are already covered and none is picked. One edge in the matching, two vertices in the cover.",
                            "All three edges share vertex 0, so they cannot all be in a matching — and the cover printed on that line has two vertices, not six.",
                            "Two edges sharing vertex 0 are not vertex-disjoint either. The moment 0 enters the cover, `(0, 2)` is skipped rather than picked.",
                            "An empty matching would mean no edge was ever picked, and then nothing would have put vertices 0 and 1 into the cover.",
                        ],
                    },
                    {
                        "prompt": "How large is the true optimum for that star?",
                        "hole": "?",
                        "opts": ["1", "2", "3", "4"],
                        "a": 0,
                        "why": "Every edge touches the centre, so `{0}` covers the whole graph. The approximation spent two vertices, giving a ratio of 2 on a graph a human solves at a glance — the price of never guessing which endpoint to keep.",
                        "whys": [
                            "Every edge touches the centre, so `{0}` covers the whole graph. The approximation spent two vertices, giving a ratio of 2 on a graph a human solves at a glance — the price of never guessing which endpoint to keep.",
                            "Two is what the approximation returned, not the optimum. The exhaustive search tries every single vertex before it tries any pair, and the centre works.",
                            "Three would be one vertex per leaf, which does cover the star, but it is three times larger than it needs to be.",
                            "Four is the whole vertex set. It is always a cover and is never the smallest one on a graph with any structure at all.",
                        ],
                    },
                    {
                        "prompt": "The ratio on a triangle.",
                        "hole": "?",
                        "opts": ["1.0", "2.0", "1.5", "0.5"],
                        "a": 0,
                        "why": "The algorithm picks `(0, 1)` and stops, since the other two edges are already covered: two vertices. A triangle genuinely needs two, so the approximation is exact here and the certificate is loose — one matched edge against an optimum of 2.",
                        "whys": [
                            "The algorithm picks `(0, 1)` and stops, since the other two edges are already covered: two vertices. A triangle genuinely needs two, so the approximation is exact here and the certificate is loose — one matched edge against an optimum of 2.",
                            "Two would need the cover to be four vertices, and the triangle only has three.",
                            "1.5 would need a cover of 3 against an optimum of 2, so all three vertices would have to be taken. The algorithm stops after one edge, because both remaining edges touch a vertex it has already added.",
                            "A ratio below 1 would mean beating the optimum, which is what the word optimum rules out.",
                        ],
                    },
                    {
                        "prompt": "The ratio on three disjoint edges.",
                        "hole": "?",
                        "opts": ["2.0", "1.0", "3.0", "1.5"],
                        "a": 0,
                        "why": "No edge shares a vertex with any other, so every edge is picked and all six vertices are taken. One endpoint per edge would have done, so the optimum is 3 and the ratio is exactly 2 — the same tight case as the path of four, for the same reason.",
                        "whys": [
                            "No edge shares a vertex with any other, so every edge is picked and all six vertices are taken. One endpoint per edge would have done, so the optimum is 3 and the ratio is exactly 2 — the same tight case as the path of four, for the same reason.",
                            "A ratio of 1 would need the algorithm to be exact, and here it takes both endpoints of three edges when three vertices would have sufficed.",
                            "Three is above the guarantee, which no input can produce: the cover is `2m` and the optimum is at least `m`.",
                            "The cover is 6 vertices, so 1.5 would need an optimum of 4. But `{0, 2, 4}` covers all three edges with three vertices, and nothing smaller can, since the three edges are disjoint.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How far exhaustive search actually reaches",
                "minutes": 8,
                "brief": r"""
`min_vertex_cover` refuses more than 18 nodes, and the refusal is not squeamishness.
Smallest-first search over subsets examines up to $2^{n}$ of them, and $2^{n}$ is the
one function in this course that beats every machine you could buy. Price the wall
before you walk into it.
""",
                "prompt": "How long does the full sweep take?",
                "note": "Answer in days, to two decimal places.",
                "figure": "A graph on 40 nodes. The search enumerates every subset of the node set, checks each one against the edge list, and the machine gets through 5 million subsets per second.",
                "given": [
                    {"label": "Nodes", "value": "40"},
                    {"label": "Subsets to test", "value": "`2^40` = 1 099 511 627 776"},
                    {"label": "Rate", "value": "5 000 000 subsets/second"},
                    {"label": "Seconds in a day", "value": "86 400"},
                ],
                "aside": "Every node added doubles this. The exponent is in the node count, so the graph that takes a week is only three nodes bigger than the one that takes a day.",
                "answer": 2.545,
                "tol": 0.05,
                "unit": "days",
                "hint": "Divide the subset count by the rate for a number of seconds, then divide by 86 400.",
                "wrong": "A number near 220 000 is the answer in seconds — it needs dividing by 86 400 once more.",
                "why": r"""
`2^40` is 1 099 511 627 776 subsets. At five million a second that is 219 902 seconds,
and `219902 / 86400 = 2.55` days. What matters is not the number but its slope: 42 nodes
is ten days, 50 nodes is a little over seven years, and 60 nodes outlives everyone
reading this. Meanwhile the 18-node cap in the lab is 262 144 subsets, which the same
machine clears in about a twentieth of a second — the whole exponential range from
instant to impossible fits inside a factor of three in `n`. That gap is the entire
argument for an approximation with a proved ratio, and for `min_vertex_cover` raising
`ValueError` rather than politely trying.
""",
            },
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
