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
                            "The merge: one linear pass over the two sorted halves, once the recursive calls return",
                            "The two recursive calls, which the additive term prices alongside `2T(n/2)` itself",
                            "The `n` base cases, one per element, which is where a linear term in the total comes from",
                            "The whole level of the recursion tree, since every level of merge sort costs `Theta(n)`",
                        ],
                        "a": 0,
                        "why": r"""
A recurrence prices exactly one node of the recursion tree. `2T(n/2)` is the two
children; the additive term is everything that node does with its own hands, which here
is split and merge. Splitting is a pair of slice indices and costs nothing worth naming,
so the `n` is the merge: walk both sorted halves once, emitting the smaller head. What
the recurrence then does for you is add that cost up over the whole tree — which is why
the total, `n log n`, is not the same shape as the term you wrote down.
                        """,
                        "whys": [
                            r"""
Right, and the reason it is the merge rather than the split is worth keeping: the divide
step of merge sort is two slice indices, `O(1)`, while the combine walks every element of
both halves exactly once. Merge sort is the divide-and-conquer algorithm whose work is
almost all in the combine, which is what makes `T(n) = 2T(n/2) + Theta(n)` its signature
rather than quicksort's — quicksort partitions in `Theta(n)` and combines for free, and
lands on the same recurrence from the opposite end.
                            """,
                            r"""
`2T(n/2)` already is the two recursive calls — that is what the notation says. Charging
them again in the additive term counts the same work twice, and the arithmetic punishes
it immediately: `T(n) = 2T(n/2) + 2T(n/2)` is `T(n) = 4T(n/2)`, whose solution is
`Theta(n^2)`. That is not a slightly pessimistic estimate of merge sort, it is the cost
of an algorithm with four children per node. The additive term is defined as the work
outside the recursive calls, and if it were not, the recurrence could not be solved at
all — every appearance of `T` on the right has to be a strictly smaller instance.
                            """,
                            r"""
The base cases really do number `n`, and `n` times `T(1)` really is a `Theta(n)`
contribution to the answer. But that contribution is the bottom row of the tree, and the
recursion is what puts it there: unroll `2T(n/2)` all the way down and you arrive at `n`
leaves without ever writing them into the additive term. Writing them in as well would
count them twice. The distinction is the one the whole module turns on — the term
describes one call's own work, and the solution describes the sum over every call.
                            """,
                            r"""
Every level really does cost `Theta(n)`, and that fact is why merge sort is `n log n`
rather than something worse. But it is a property of the solved recurrence, not of the
term: `T(n) = 2T(n/2) + f(n)` prices one node, the root, and the levels below it are
what `2T(n/2)` unrolls into. Level `k` holds `2^k` calls on inputs of size `n/2^k`, so
its cost is `2^k * Theta(n/2^k) = Theta(n)` — the levels come out equal because the
additive term is linear, which is exactly the equality case of the master theorem. Read
the fact back into the term and you have used the answer as its own input.
                            """,
                        ],
                    },
                    {
                        "q": "`T(n) = 3T(n/2) + Theta(n)` is Karatsuba's shape. Which bound does the master theorem give?",
                        "opts": [
                            "`Theta(n^(log_3 2))`, about `n^0.63` — three subproblems at half the size",
                            "`Theta(n^(log_2 3))`, roughly `n^1.585` — the leaf count dominates",
                            "`Theta(n log n)`, since every level of the tree costs the same",
                            "`Theta(n)`, since the combine at the root dominates the rest",
                        ],
                        "a": 1,
                        "why": r"""
The master theorem is one comparison: `n^d`, the combine, against `n^(log_b a)`, the
leaves. Here `d = 1` and `log_b a = log_2 3 = 1.585`, so the leaves win and the answer
is their count. The three cases are the three ways that comparison can come out, and
naming which one you are in is the whole of the work — the exponent then reads straight
off. `a` is the branching factor and `b` is the shrink factor, and `log_b a` keeps them
in that order.
                        """,
                        "whys": [
                            r"""
`log_3 2` is 0.63 — the right two numbers in the wrong positions. The base of the
logarithm is `b`, the factor the input shrinks by, and the argument is `a`, the number of
calls: `log_b a`, not `log_a b`. The tell that it is inverted is that 0.63 is below 1,
so the claim is that Karatsuba runs in sublinear time — on an algorithm that has to read
both of its inputs before it can do anything, and whose additive term alone is
`Theta(n)`. A bound below the additive term is impossible for any recurrence of this
shape, whatever `a` and `b` are.
                            """,
                            r"""
Right, and the level-by-level picture is worth carrying: the root costs `n`, its three
children cost `3(n/2) = 1.5n` between them, the nine grandchildren `2.25n`, and the cost
grows by a factor of `3/2` every level down. A geometric series that grows is dominated
by its last term, so the bottom row — the leaves, `3^(log_2 n) = n^(log_2 3)` of them —
swallows the total. That 1.585 against schoolbook multiplication's 2 is the entire
saving Karatsuba buys, and it comes from turning four half-size multiplications into
three.
                            """,
                            r"""
`n log n` is the equality case, `d = log_b a`, where every level costs the same and there
are `log n` of them. That is merge sort: `2T(n/2) + Theta(n)`, where two calls at half
the size reproduce exactly the work of the one above. Karatsuba makes three calls at half
the size, so each level costs `3/2` as much as the one above rather than the same, and a
growing geometric series is not `log n` equal terms. The difference between 2 and 3 in
that position is the difference between `n log n` and `n^1.585`.
                            """,
                            r"""
`Theta(n)` is case 3, and it needs the combine to dominate the leaves — `d > log_b a`,
so `d` above 1.585. A linear combine has `d = 1`, well below it. Read the claim back as
a statement about the algorithm and it says that three multiplications of half-length
numbers, plus a linear pass of additions, cost no more than the linear pass alone. The
recursive calls have to appear in the answer somewhere, and case 3 is the case where they
do not, which is why it also carries a regularity condition rather than just the exponent
comparison.
                            """,
                        ],
                    },
                    {
                        "q": "Both recursive calls have returned and `d` is the better of their two distances. Why is it enough to compare each point of the strip against only the next seven in y-order?",
                        "opts": [
                            "Seven is the constant that keeps the scan linear, so it was chosen rather than derived",
                            "The points are y-sorted, so distances grow along the scan and the eighth is already too far",
                            "A pair beating `d` must fit in one `2d`-by-`d` box, and each half is already `d`-separated",
                            "The strip is what the recursion has narrowed the search to, and it holds at most eight points",
                        ],
                        "a": 2,
                        "why": r"""
The bound is geometry, not bookkeeping. A pair that improves on `d` has both ends within
`d` of the split line in x and within `d` of each other in y, so both sit in a
`2d`-by-`d` rectangle straddling the line. The recursion has already proved that no two
points inside one half are closer than `d`, so each `d`-by-`d` square of that rectangle
holds at most four points — corners only — and the rectangle at most eight. Fix one of
them and there are seven others: that is the seven, and it is a constant because the
recursion's own guarantee is what limits the crowd.
                        """,
                        "whys": [
                            r"""
It is a fair suspicion in general — constants do sometimes get reverse-engineered to make
a bound come out — but here the derivation runs the other way and lands on eight points
in the rectangle before anyone asks what it buys. You can even see the constant is not
tuned by noticing that it is loose: the true maximum in the rectangle is six rather than
eight once you rule out coincident points, and nobody bothers to tighten it, because any
constant at all is what makes the scan linear. A constant chosen to fit would have been
chosen smaller.
                            """,
                            r"""
What grows monotonically along the scan is the y-*difference*, not the distance — the two
are different because x still varies freely inside the strip. Point 8 can sit further
down and directly above you, and point 3 can sit further up and a full `d` across. That
is why the loop's early exit tests `strip[j][1] - strip[i][1] >= d`, a comparison on the
y-coordinates alone: it is the y-gap that is sorted, and once it reaches `d` no later
point can help however its x falls. Sorting by y buys the stopping rule; the box argument
buys the seven.
                            """,
                            r"""
Right, and the load-bearing clause is the one about the halves: the seven is a constant
only because the recursive calls have already established `d`-separation inside each
side. Before they return there is no such bound and the strip could be arbitrarily
crowded. That is why the scan comes after the recursion rather than instead of it, and
why the argument is about a `2d`-by-`d` box rather than the strip as a whole — `2d` wide
because the strip is `d` either side of the line, `d` tall because a taller pair is
already worse than `d`.
                            """,
                            r"""
The strip can hold every point in the input — put all `n` points on the split line and it
does. Bounding the strip is what you would need if the scan compared every pair inside
it, and that is exactly the `O(n^2)` the seven-neighbour argument exists to avoid. What
is bounded is not the strip but any `2d`-by-`d` window of it, and the scan works because
it only ever looks through such a window: sorted by y, the next seven points are the
only ones that can still be within `d` vertically.
                            """,
                        ],
                    },
                    {
                        "q": "Which of these turns an `O(n log n)` closest pair into `O(n log^2 n)`?",
                        "opts": [
                            "Sorting the whole input by x and by y once, before the recursion starts, instead of inside it",
                            "Recursing into both halves every time, rather than only into the half the split line favours",
                            "Calling `math.hypot` on every candidate pair instead of comparing squared distances",
                            "Sorting the strip by y inside each recursive call, rather than threading one y-order down",
                        ],
                        "a": 3,
                        "why": r"""
Put the change into the recurrence and read the answer off. A sort inside the call makes
the combine `O(n log n)` rather than `O(n)`, so `T(n) = 2T(n/2) + O(n log n)`, and with
`log n` levels each costing `n log n` the total is `n log^2 n`. The module calls this a
defect rather than a variant for a specific reason: the code still returns the correct
pair, every test still passes, and only the clock ever finds out. It is the shape of bug
that a correctness suite is structurally unable to catch.
                        """,
                        "whys": [
                            r"""
Those two sorts are the fix, not the fault. They happen once, before the recursion, so
they contribute a single `O(n log n)` term to the whole run rather than one per level —
and it is precisely because the y-order exists up front that a call can hand its children
their share of it without sorting anything. The instinct behind the wrong answer is
right in general, that a sort is the expensive thing here; the question is only whether
it is paid once or `log n` times.
                            """,
                            r"""
Recursing into both halves is not an optimisation anyone gave up: it is required, because
the closest pair can lie wholly on either side of the split and a search that commits to
one half can miss it outright. Note that the alternative would be *faster*, not slower —
`T(n) = T(n/2) + O(n)` solves to `O(n)` — so it fails the question on correctness rather
than on cost. Some divide-and-conquer algorithms really can discard a half, binary search
being the obvious one; they can do it because a comparison at the split proves the answer
is not there, and no such proof exists here.
                            """,
                            r"""
`hypot` is a constant factor: one square root per candidate pair, and the number of
candidate pairs is unchanged. Constants cannot move an exponent or add a logarithm, so
whatever this costs it is still `O(n log n)`. It is a real optimisation for two other
reasons — squared distances keep the arithmetic exact on integer inputs, and the square
root is monotone so comparing squares compares distances — but the module's point is that
a change worth making and a change that alters the bound are different claims, and only
the second one shows up in the recurrence.
                            """,
                            r"""
Right — and the fix is the one the lab makes you build: sort by x and by y once at the
top, then have each call hand its children the sub-orders they need, so the combine
stays a linear pass. Threading the order down is fiddlier than re-sorting, which is
exactly why the slow version gets written, and it is why the checks time the
implementation instead of only marking its output. A defect that changes no answer needs
a gate that measures something other than the answer.
                            """,
                        ],
                    },
                    {
                        "q": "Merging the halves `[2, 5]` and `[1, 3]` of `[2, 5, 1, 3]`, the merge emits `1` first. How many inversions does that one step account for?",
                        "opts": ["2", "1", "0", "3"],
                        "a": 0,
                        "why": r"""
An inversion is a pair standing in the wrong order in the original array. When the merge
takes an element from the right half, every element still unconsumed in the left half is
larger than it and stood to its left — so all of them are inverted with it, and one
comparison settles the lot. That is what `total += len(left) - i` says, and it is the
whole reason the count rides inside the merge instead of being computed separately: the
merge is already discovering these pairs, in batches, for free.
                        """,
                        "whys": [
                            r"""
Right. `1` is smaller than both `2` and `5`, which are still unconsumed on the left and
both stood to its left in `[2, 5, 1, 3]`, so this single emission settles the pairs
`(2, 1)` and `(5, 1)`. With `i = 0` and `len(left) = 2`, `total += len(left) - i` adds
exactly 2. The batching is the point: an `n log n` count is only possible because one
comparison can be worth many pairs.
                            """,
                            r"""
Adding one per emission counts merge steps rather than inverted pairs, and it undercounts
whenever the right half wins over more than one remaining left element — here it would
report 1 for a step worth 2. Over the whole array it would return the number of times the
right half emitted, which is a statistic about the merge and not about the input: run it
on `[3, 4, 1, 2]` and it reports 2, where the true count is 4. The increment has to
depend on how much of the left half is still standing, which is what `len(left) - i`
measures.
                            """,
                            r"""
Zero is what you would add if `1` had been emitted after the left half was exhausted —
then nothing remains to its left and it crosses nobody. Here `2` and `5` are both still
waiting, and both are inversions with `1`. A merge that charged nothing for a right-hand
emission would return 0 on every input, including a fully reversed one, so the count would
be reporting that no array is ever out of order.
                            """,
                            r"""
3 is the inversion count of the whole array — `(2, 1)`, `(5, 1)` and `(5, 3)` — and it is
tempting because it is the number the function eventually returns. This step accounts for
the first two of them. The third is settled later in the same merge, when `3` is emitted
while `5` is still unconsumed and `len(left) - i` is 1. The question asks what one step
contributes; adding the total at every step would count each pair as many times as there
are emissions.
                            """,
                        ],
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
                            "Fewest conflicts with the intervals still available",
                            "Earliest finishing time",
                            "Earliest starting time",
                            "Shortest duration",
                        ],
                        "a": 1,
                        "why": r"""
All four rules are plausible, three of them are wrong, and the difference between a rule
that works and a rule that looks like it works is a proof rather than a run of examples.
The proof here is the exchange argument: take any optimal schedule, and swap its first
interval for the one that finishes earliest. The result is still compatible, because the
new interval ends no later than the one it replaced, and it is still the same size. Repeat
and the greedy schedule is reached without ever shrinking. That argument is available for
finishing time and for none of the others: two of the three die on an instance of three
intervals, and the third needs a larger figure but dies all the same.
                        """,
                        "whys": [
                            r"""
This is the one that takes real work to refute, and it is here because it deserves to be
taken seriously — it is a better rule than the other two, it looks at the structure of
the instance rather than at one interval in isolation, and on most inputs you would draw
by hand it wins. It is still not optimal: Kleinberg and Tardos give a standard figure in
which the least-conflicted interval is precisely the one whose selection costs the
optimum. Being locally least obstructive is not the same as leaving the most room, and
only the finishing time measures the latter directly.
                            """,
                            r"""
Right, and the reason is the one the exchange argument turns on: of all the intervals you
could commit to, the one that finishes earliest leaves the most of the timeline free
behind it. Nothing else about an interval matters to what comes after — not when it
started, not how long it ran, not what it overlapped — because the only constraint the
future sees is the time you are next free.
                            """,
                            r"""
Starting early says nothing about finishing early, and it is finishing that decides what
is still available. `[(0, 10), (1, 2), (3, 4)]` settles it: the earliest start is the
interval that runs all day, so the rule returns 1 where `(1, 2)` and `(3, 4)` give 2. The
instinct is not silly — starting early feels like wasting no time — but the resource being
spent is the rest of the timeline, and a long early interval spends all of it.
                            """,
                            r"""
This is the most plausible of the three wrong rules, because a short interval genuinely
does consume less of the timeline. What it can also do is consume the wrong part of it.
`[(0, 3), (2, 4), (3, 6)]` is the instance the lab asserts on: the shortest interval is
`(2, 4)`, two units long, and it overlaps both of its neighbours, so taking it returns 1
where `(0, 3)` and `(3, 6)` give 2. Duration measures how much room an interval uses;
finishing time measures where the room it leaves behind begins.
                            """,
                        ],
                    },
                    {
                        "q": "Huffman merges the two least frequent subtrees first. What does that guarantee about the two least frequent symbols?",
                        "opts": [
                            "Their codewords are the same length only if their two frequencies happen to be equal",
                            "Their codewords are the longest in the code, but a later merge can still separate them",
                            "They become siblings, so their codewords are equally long and differ only in the final bit",
                            "They get the shortest codewords, since being handled first puts them nearest the root of the tree",
                        ],
                        "a": 2,
                        "why": r"""
A merge creates a new parent above two existing roots and never reaches inside either of
them. So the pair merged first is buried deepest, and it is buried together: every
subsequent merge prepends one bit to everything in the subtree, to both members equally.
Being siblings is what forces the equal length — the two codewords are their shared
parent's prefix plus `0` and plus `1` — and being merged first is what makes that length
the largest in the code. The economy of the whole scheme is in that sentence: the rare
symbols take the long codewords so the frequent ones can have short ones.
                        """,
                        "whys": [
                            r"""
Equal frequencies are not needed and were never used. The two codewords are the parent's
prefix plus one bit each, so they have the same length by construction, whatever the
counts. What the frequencies decide is which pair gets merged, not how the pair is
shaped once it has been. In the lab's instance `E` is 8 and `D` is 12, plainly unequal,
and both come out at depth 4 with codewords differing in the last bit.
                            """,
                            r"""
The first half is right and worth keeping: merged first does mean buried deepest, so
these two codewords are the longest in the code. The second half is the thing the
algorithm structurally cannot do. A merge only ever creates a new parent above two
existing roots; it never reopens a subtree that has already been formed, so nothing later
can put a node between two symbols that are already siblings. Every subsequent merge adds
one bit to the front of both of them at once, which is exactly why they stay the same
length as each other while both get longer.
                            """,
                            r"""
Right, and the equal length is forced by the sibling relation rather than by the
frequencies. Whatever the two counts are — 1 and 999 — once they hang off one parent
their codewords are that parent's prefix followed by `0` and by `1`. This is also the
step where the correctness proof starts: an optimal tree can always be rearranged so
that the two rarest symbols are siblings at maximum depth, and that is what licenses
merging them and treating the pair as a single symbol of the combined weight.
                            """,
                            r"""
Merged first means buried deepest, which is the opposite of nearest the root. The order
runs backwards to the intuition because the merges build the tree from the leaves upward:
the first merge is the one that ends up furthest from the root, and the last merge is the
root itself. If the rarest symbols did get the shortest codewords the code would be worse
than a fixed-length one — you would be spending your cheap bits on the symbols that
hardly ever appear.
                            """,
                        ],
                    },
                    {
                        "q": "A binary prefix-free code has codeword lengths 1, 2, 3, 3. What does the Kraft sum come to, and what does that tell you?",
                        "opts": [
                            "Exactly 1 — but every prefix-free code sums to 1, so the value tells you nothing extra",
                            "0.875 — one leaf is going spare at depth 3, so a codeword could have been shorter",
                            "1.25 — the sum runs over 1, which is why no prefix-free code has these lengths",
                            "Exactly 1 — the tree is full, so no codeword could be shortened and stay prefix-free",
                        ],
                        "a": 3,
                        "why": r"""
`1/2 + 1/4 + 1/8 + 1/8 = 1`, realised by `0`, `10`, `110`, `111`. The inequality behind
the sum is the useful part: reserving a codeword of length `l` blocks a `2^-l` share of
the tree below it, and prefix-freeness says those shares cannot overlap, so the total is
at most 1. Equality then means every share is claimed — the tree is full, no internal
node has an only child, and there is no unused branch left to shorten a codeword into.
A sum strictly below 1 is the interesting failure, because it certifies that some
codeword could have been shorter and the code is therefore not optimal.
                        """,
                        "whys": [
                            r"""
The arithmetic is right and the conclusion drawn from it is the common slip: the Kraft
inequality is `at most 1`, not `equal to 1`, and the gap between those is where the whole
diagnostic power sits. Lengths 1, 2, 3 sum to `1/2 + 1/4 + 1/8 = 0.875` and describe a
perfectly good prefix-free code with a wasted branch — the depth-3 codeword could have
been depth 2. So the sum does say something extra here: it says nothing has been wasted,
which is the part a Huffman code guarantees and an arbitrary prefix-free code does not.
                            """,
                            r"""
0.875 is `1/2 + 1/4 + 1/8`, which is the sum over the three *distinct* lengths — the
second codeword of length 3 has been counted once instead of twice. The sum runs over
codewords, not over the set of lengths that appear. Where 0.875 would be the right answer
is for lengths 1, 2, 3, and the reading attached to it would then be correct too: a spare
leaf at depth 3, so the depth-3 codeword could be pulled up to depth 2.
                            """,
                            r"""
1.25 comes out if the two depth-3 codewords are charged at `2^-2` each, so that the sum
reads `1/2 + 1/4 + 1/4 + 1/4` — an off-by-one in the depth, not in the method. The
conclusion drawn from it is in fact the right conclusion
for a sum above 1 — such a code really cannot exist, because the reserved shares would
have to overlap and one codeword would be a prefix of another — so the reasoning is
sound and only the arithmetic slipped. Recompute with `l = 3`, worth `1/8` each, and the
total lands on 1.
                            """,
                            r"""
Right, and the sharpest way to hold on to it is the geometric one: each codeword claims
an interval of length `2^-l`, prefix-freeness makes the intervals disjoint, and they all
live inside a unit interval. Summing to 1 means they tile it with nothing left over.
That is the condition the lab asserts on the Huffman output, and it is a stronger check
than merely confirming the code is decodable, because it also rules out a code that is
decodable and wasteful.
                            """,
                        ],
                    },
                    {
                        "q": "With coins 1, 3 and 4, `greedy_failure` returns 6. Why is 6 the smallest counterexample and not something below it?",
                        "opts": [
                            "Every amount below 6 comes out optimal; at 6 greedy takes the 4 and needs two 1s, where 3 + 3 needs one fewer",
                            "6 is the first amount past the largest coin, so the first greedy must make from more than one coin",
                            "6 is the first amount that is not itself a coin, so the first where greedy has a decision to make",
                            "6 is the first multiple of 3 that greedy cannot reach with 3s, because it commits to the 4 before it sees them",
                        ],
                        "a": 0,
                        "why": r"""
Walk it and there is nothing to argue about. 1, 3 and 4 are single coins. 2 is `1 + 1`
either way. 5 is `4 + 1` for greedy, and two coins is optimal. At 6, greedy commits to
the 4, is left with a 2 it can only pay in ones, and finishes on three coins where
`3 + 3` finishes on two. `greedy_failure` searches upward from 1 for exactly this reason:
the first amount at which the two disagree is by construction the smallest counterexample,
and having the smallest one makes the failure inspectable by hand.
                        """,
                        "whys": [
                            r"""
Right, and the clause about everything below 6 is what makes it the *smallest* rather
than merely *a* counterexample. Greedy is not lucky below 6, it is correct: at each of
1 through 5 the largest coin that fits belongs to some optimal solution, so committing to
it costs nothing. 6 is the first amount where that stops being true, and the reason is
that 4 leaves a remainder of 2 which this coin system cannot pay efficiently — 4 and 1
mesh badly with a 3 sitting between them.
                            """,
                            r"""
5 is already past the largest coin and greedy handles it perfectly: `4 + 1`, two coins,
optimal. So being past the largest coin is not the trigger, and it cannot be — a system
like 1, 2, 4 is greedy-optimal at every amount, well past its largest coin. The property
that matters is not how many coins are needed but whether the largest coin that fits is
ever the wrong first commitment, and that is a fact about how the denominations mesh
rather than about their size.
                            """,
                            r"""
2 and 5 are not coins either, and greedy is right about both. Nor is the number of
decisions the issue: greedy makes a decision at 2 and gets it right. What the search is
looking for is not the first amount with a choice but the first amount where the choice
greedy makes is worse than another — and it takes until 6 for that to happen, because
below it the largest coin that fits always belongs to some optimal solution.
                            """,
                            r"""
Greedy does use the 3, at 3 itself, so it is not blind to it. And 6 is the second
multiple of 3, not the first — 3 is reachable and optimal. The half of this that is right
is the mechanism: greedy really does commit to the 4 at 6 and thereby lock itself out of
`3 + 3`. What it is not is a rule about multiples of 3, and you can see that by checking
9: greedy takes `4 + 4 + 1` for three coins, and `3 + 3 + 3` is also three, so the rule
would predict a failure that does not happen.
                            """,
                        ],
                    },
                    {
                        "q": "You suspect a proposed greedy rule is not optimal. What is enough to establish that?",
                        "opts": [
                            "An instance where it disagrees with some other greedy rule that has been proposed for the problem",
                            "One instance where it returns a strictly worse answer than the true optimum, checked against that optimum",
                            "A proof that no exchange argument can be constructed for the rule, since that is how optimality gets established",
                            "A family of instances on which the ratio between the rule and the optimum grows without bound",
                        ],
                        "a": 1,
                        "why": r"""
Refutation is existential and justification is universal, which is why they cost such
different amounts. To claim a greedy rule is optimal you have to say something about
every instance there will ever be; to deny it you need one. That asymmetry is why
`greedy_failure` is a short search and the exchange argument is a proof, and it is why
the lab makes you write the dynamic program alongside the greedy rule — the
counterexample only counts once it has been measured against something known to be
optimal.
                        """,
                        "whys": [
                            r"""
Two heuristics disagreeing establishes that at most one of them is right, without saying
which — and it is entirely possible that the rule under suspicion is the one that is
correct. Neither heuristic is a benchmark for the other; the benchmark has to be
something known to compute the optimum, which for coin change is the dynamic program.
The instinct is sound, that a disagreement is where to look, and turning it into evidence
means computing the optimum at the amount where they diverge.
                            """,
                            r"""
Right, and the clause about checking against the true optimum is doing real work. An
instance where greedy looks bad is not a counterexample until something proves a better
answer exists, and eyeballing does not prove it. That is why `greedy_failure` calls
`optimal_coin_count` rather than a second heuristic: the dynamic program is the benchmark,
and without one the search would be comparing two guesses.
                            """,
                            r"""
This would settle it, and it is far harder than the claim it is being used to establish —
you would have to quantify over all possible exchange arguments, which is not a
mathematical object anyone has defined. It also proves the wrong thing even if you
managed it: the absence of one proof technique is not the absence of the property, and a
rule could be optimal for a reason that no exchange argument captures. One instance and
one dynamic program settle the same question in an afternoon.
                            """,
                            r"""
An unbounded ratio is a much stronger result, and it is a good thing to want — it is
exactly what separates a bad heuristic from a bad-but-bounded one, and it is what the
approximation module measures. It is not what was asked. Non-optimality only needs the
rule to be wrong somewhere; a rule that is off by one coin on one instance and perfect
everywhere else is already not optimal, and no family of instances is needed to say so.
                            """,
                        ],
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
                            "The cost of the cheapest operation available at `(i, j)`, which the fill then accumulates",
                            "How many operations remain after `i` deletions and `j` insertions",
                            "The distance between the first `i` characters of `a` and the first `j` characters of `b`",
                            "The distance between the single characters `a[i]` and `b[j]`, which the recurrence adds up",
                        ],
                        "a": 2,
                        "why": r"""
Naming the subproblem is the design step, and everything else follows from it. Here the
subproblem is a pair of prefixes: `(i, j)` is the answer to a smaller instance of exactly
the same question. That is what makes the recurrence local — any way of finishing off
`a[:i]` against `b[:j]` ends in one of three moves, and each move lands on a neighbouring
cell — and it is what makes the borders obvious, since `(i, 0)` is `a[:i]` against nothing
and costs `i` deletions. A cell that held anything else would have nothing for the next
cell to build on.
                        """,
                        "whys": [
                            r"""
This is the recurrence's input mistaken for its output. `min` of three candidates is
computed while filling `(i, j)`, and the cheapest of them is what gets stored — but what
gets stored is the whole distance for that prefix pair, not the price of the last step.
The difference shows up at the borders: under this reading `(3, 0)` would hold 1, the
cost of one deletion, where the table needs 3, the cost of deleting all three characters.
Accumulating afterwards is not possible either, because you would have to know which path
through the table to accumulate along, and finding that path is the problem.
                            """,
                            r"""
This reads the table backwards — as work remaining rather than work done — and although a
cost-to-go formulation can be made to work in general, it is not this one, and the
indices give it away. `i` and `j` are positions in the two strings, not counts of
operations already performed: `i` deletions would have consumed `i` characters of `a`
while advancing nowhere in `b`, so the pair `(i, j)` would not describe a state this table
has. The border check settles it too — `(0, 0)` holds 0, the cost of matching nothing
against nothing, where a work-remaining table would hold the full distance there.
                            """,
                            r"""
Right, and the test for whether a subproblem has been named properly is whether the cell
is self-contained: `(i, j)` is an answer, complete in itself, that never has to be
revisited once written. That is what lets the fill go in one sweep with no back-tracking,
and it is why the same table serves the reconstruction afterwards — every cell is a
finished claim about a real instance, so the back-walk can interrogate it.
                            """,
                            r"""
A cell about two single characters carries no history, and nothing can be built on it.
You can see the problem by asking what the recurrence would be: to combine
`distance(a[i], b[j])` values into a total you would need to know which characters got
paired with which, and that pairing is the alignment — the very thing the table exists to
find. The substitution cost `a[i] != b[j]` does appear in the recurrence, but as an
increment applied to the diagonal neighbour, not as the value of the cell.
                            """,
                        ],
                    },
                    {
                        "q": "Why do the checks replay your edit script instead of comparing it against a stored one?",
                        "opts": [
                            "The value of the optimum is not unique either, so no stored answer could be compared against",
                            "The fill order is not fixed, so the script a correct solution produces depends on how the table was swept",
                            "A correctly reconstructed script can come out cheaper than the value in the table, and the replay catches that",
                            "Ties are real — many scripts hit the same cost, so the check replays yours and compares the result",
                        ],
                        "a": 3,
                        "why": r"""
The value of an optimum is unique — that is what makes it *the* optimum — but the witness
that achieves it almost never is. `form` to `from` costs 2 whether you delete the `o` and
re-insert it after the `r`, or substitute both letters where they stand, and a grader
holding one specific script would fail the other. So the check does the only thing that
is fair: consume `a`, apply the operations in order, and require that `b` comes out and
that the operations which are not matches number exactly the cost claimed. That tests the
property the script is supposed to have, rather than testing whether it is the particular
script the author happened to write.
                        """,
                        "whys": [
                            r"""
The optimum's value is unique, and that uniqueness is exactly what the check leans on:
`edit_distance` is compared against a stored number without ceremony, because there is
only one right answer. If the value were ambiguous the whole table would be ill-defined,
since every cell is a `min` over its neighbours. The ambiguity is one level down, in
which sequence of moves achieves that value, and it is the script rather than the number
that needs replaying.
                            """,
                            r"""
The fill order is not free — it is fixed by the dependencies, since `(i, j)` reads
`(i-1, j)`, `(i, j-1)` and `(i-1, j-1)`, so those three have to be written first. Row by
row and column by column both satisfy that, and both produce the same table, because each
cell is a `min` over values that are already final. What can vary is the tie-breaking
inside the back-walk, which is a choice in the reconstruction rather than a consequence
of the sweep — and it is a real source of differing scripts, which is why the check
replays.
                            """,
                            r"""
A script cheaper than the table's value would mean the table is wrong, not that the
reconstruction was clever — the table's value is by definition the cheapest achievable,
so nothing correct can beat it. The replay is not looking for that. It exists for the
opposite direction: a reconstruction that is *valid but not minimal*, or one that claims
a cost its operations do not actually incur, and both of those are ordinary bugs in a
back-walk that reads the wrong neighbour.
                            """,
                            r"""
Right, and the general lesson is worth more than the instance: when a problem has many
optimal witnesses, a grader must check the defining property rather than the artefact.
Replaying does that in two parts — that the script transforms `a` into `b` at all, and
that its cost is the one claimed — and either half alone would be gameable. A script that
reaches `b` by rewriting every character is valid and expensive; a script that claims cost
2 and does not reach `b` is cheap and wrong.
                            """,
                        ],
                    },
                    {
                        "q": "Items `(weight, value)` of `(6, 9)`, `(5, 7)`, `(5, 7)` with capacity 10. What does value-density greedy get, and what is the optimum?",
                        "opts": [
                            "9 against 14 — greedy takes the densest item and then nothing else fits",
                            "14 against 14 — density greedy is optimal here, since every item fits on its own",
                            "9 against 23 — the optimum takes all three items, worth 23 between them",
                            "9 against 14.6 — the optimum is what the densities are pointing at",
                        ],
                        "a": 0,
                        "why": r"""
Densities are `9/6 = 1.5` and `7/5 = 1.4`, so greedy commits to the 6-weight item and is
left with 4 units of capacity that nothing fits into: 9. The table takes both 5s for 14.
What makes this an honest counterexample rather than a trick is that the greedy rule *is*
optimal on the fractional problem, where it would take the 6 and then four-fifths of a 5
for `9 + 5.6 = 14.6`. Indivisibility is the entire difficulty, and it is the reason there
is a table here and a one-line sort in the fractional version.
                        """,
                        "whys": [
                            r"""
Right, and the shape of the failure is worth naming: greedy is not defeated by a bad
density estimate, it is defeated by the remainder. Committing to the 6 leaves 4 units of
capacity that no item can use, and that stranded capacity is worth more than the 0.1 of
density the choice bought. Every counterexample to density greedy has this form, which is
also why the fractional version is immune — there, leftover capacity is always usable.
                            """,
                            r"""
Every item does fit on its own, and greedy is still not optimal, which is precisely why
this instance was chosen. The condition that would rescue the rule is not that items fit
individually but that they can be split, and the whole difference between the two
problems lives in that word. Run the density rule here and it takes the 6-weight item
first, at which point 4 units of capacity remain and both 5s are excluded: 9, not 14.
                            """,
                            r"""
The three items weigh `6 + 5 + 5 = 16` between them, and the sack holds 10, so they never
fit together — 23 is the value of a bundle that is not a candidate. This is the commonest
slip in the whole module, and it is worth noticing where it comes from: the optimum is
the best *feasible* set, and it is easy to compute the best set and forget to check the
constraint. No correct algorithm ever exceeds the capacity, so no answer above 14 is
available on this instance.
                            """,
                            r"""
14.6 is a real quantity and it is the answer to the neighbouring question: it is the
*fractional* optimum, `9` for the 6-weight item plus four-fifths of a 5 for `5.6`. On the
fractional problem the density rule is provably optimal, and that is exactly why the
relaxation is worth knowing — it is an upper bound on the integral optimum, and branch
and bound is built out of it. What it is not is achievable here, because you cannot take
four-fifths of an item. The integral optimum is 14, and the 0.6 between them is the price
of indivisibility.
                            """,
                        ],
                    },
                    {
                        "q": "You shrink the knapsack table to two rolling rows to save memory. What does that cost you?",
                        "opts": [
                            "The handling of zero-weight items, whose row now overwrites the one they read",
                            "The back-walk — you can report the best value but not which items achieved it",
                            "Nothing, because the reconstruction only ever reads the final row of the table",
                            "The optimal value, which starts depending on the order the rows are visited in",
                        ],
                        "a": 1,
                        "why": r"""
The reconstruction asks, for each item `i` from the bottom upward, whether `table[i][c]`
differs from `table[i-1][c]` — and that is a question about a row a rolling
implementation has already overwritten. The value survives untouched, because each row
only ever reads the one directly above it, and that is exactly why the space reduction
works at all. Recovering the witness in small space is possible but not free:
Hirschberg's divide-and-conquer does it for sequence alignment at the price of running
the fill twice.
                        """,
                        "whys": [
                            r"""
Zero-weight items are unaffected by the space reduction, because a row still reads only
the row above it whatever the weights are. They are worth testing for a different reason,
which is that `while weight <= c` and `for c in range(...)` conditions like to get them
wrong at the boundary, and a zero-weight item with positive value should always be taken.
That is a fencepost bug in the recurrence, and it is there in the full table too.
                            """,
                            r"""
Right, and the asymmetry is the thing to carry away: the value needs one row of history
and the witness needs all of them. That is a general property of dynamic programming
rather than a quirk of knapsack — the recurrence looks back a bounded distance, so the
fill can forget, while the reconstruction walks the whole chain of decisions and cannot.
Whenever you see a space optimisation applied to a table, the first question is whether
anything downstream still wants to read what was discarded.
                            """,
                            r"""
The reconstruction reads far more than the final row — that is the whole of its
difficulty. It starts at `table[n][capacity]` and walks upward, and at each step it
compares against `table[i-1][c]` to decide whether item `i` was taken. Only the final
row is needed to report the *value*, which is what makes the confusion natural: if the
answer were just a number, this would be correct and there would be no cost at all.
                            """,
                            r"""
The value is exactly what survives, and the reason is worth being precise about: each
row depends only on the row above it, so overwriting anything older destroys no
information the fill still needs. The order is not free either — rows have to be visited
top to bottom, and within the classic one-array version the capacity loop has to run
backwards to stop an item being taken twice — but getting that wrong produces a
different bug, an item used more than once, rather than an order-dependent answer.
                            """,
                        ],
                    },
                    {
                        "q": "How does the longest common subsequence relate to edit distance?",
                        "opts": [
                            "`lcs` is `max(len(a), len(b))` minus the unit-cost edit distance",
                            "There is no relation — one is a maximisation and the other a minimisation",
                            "Ban substitution and the cheapest script costs `len(a) + len(b) - 2 * lcs`",
                            "They are equal whenever the two strings are the same length, since nothing needs inserting",
                        ],
                        "a": 2,
                        "why": r"""
The two tables are nearly the same table, which is why the module puts them side by side.
If the only moves are deletion and insertion, a script has to remove from `a` and add to
`b` everything the two do not hold in common, and the characters it can leave alone are
exactly a common subsequence — so making the script cheapest is making that subsequence
longest. For `AGGTAB` and `GXTXAYB` the LCS is `GTAB`, and the deletion-and-insertion
distance is `6 + 7 - 2*4 = 5`. The restriction matters: allow substitution and a
mismatched pair costs 1 instead of 2, so the identity stops holding.
                        """,
                        "whys": [
                            r"""
This is the closest of the wrong answers and it holds on a surprising number of examples,
which is what makes it worth refuting concretely. Take `AB` and `BA`: the LCS is 1, the
unit-cost distance is 2, and `max(2, 2) - 2 = 0`, not 1. The identity that does hold is
the one with substitution banned, and it uses `len(a) + len(b)` rather than
`max(len(a), len(b))`. Substitution is what breaks it — it buys a delete and an insert
for the price of one, so it shortens the distance without lengthening the subsequence.
                            """,
                            r"""
The direction of the two problems really is opposite, and it is a good instinct that
maximising and minimising are different activities. What makes them the same problem here
is that the quantities are complementary rather than independent: every character is
either kept or paid for, so the total length is fixed and maximising what is kept is
minimising what is paid. That is a common enough pattern to look for — a matching and a
vertex cover stand in a related arrangement in the last module of this course.
                            """,
                            r"""
Right, and the counting argument is short enough to reconstruct rather than remember.
Every character of `a` is either kept or deleted, every character of `b` is either kept
or inserted, and the kept characters are the same subsequence read from both sides. So
the cost is `(len(a) - lcs) + (len(b) - lcs)`, which is where the `2 *` comes from. The
`ban substitution` clause is load-bearing: it is what forces a mismatch to cost two moves
rather than one.
                            """,
                            r"""
Equal lengths change nothing. `AB` and `BA` are both length 2, their LCS is 1, the
deletion-and-insertion distance is `2 + 2 - 2 = 2`, and the unit-cost edit distance is
also 2 — but `ABC` and `CBA` are both length 3 with LCS 1, giving `3 + 3 - 2 = 4` against
a unit-cost distance of 2, and the two have parted company. What matters is not the
lengths but whether substitution is available, because that is the move whose price
changes between the two problems.
                            """,
                        ],
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
                            "A binary heap cannot keep negative keys in the right order once they mix with positive ones",
                            "Negative weights only make sense on a directed graph, and Dijkstra assumes an undirected one",
                            "Only a negative cycle actually breaks it; a single negative edge is caught by the guard after the pop",
                            "Its invariant is that an extracted vertex is final, and a negative edge could lower it afterwards",
                        ],
                        "a": 3,
                        "why": r"""
The proof that an extracted vertex is settled runs like this: any other route to it must
leave the settled set at some point, that departure edge already costs at least as much
as the route we have, and everything after it costs at least 0 — so the alternative cannot
be shorter. Delete the non-negativity and the last clause evaporates, and with it the
whole argument, and the failure needs no cycle at all. Take `s->a` at 2, `s->b` at 3,
`b->a` at -2 and `a->t` at 1. `a` is extracted at 2 and its edge to `t` is relaxed to 3;
only afterwards does `b` reveal that `a` is really 1 away, and by then `a` is settled and
its outgoing edge is never looked at again. `t` comes out at 3 where the true distance is
2. That is why the lab's `dijkstra` raises `ValueError` on a negative weight rather than
running and returning something plausible.
                        """,
                        "whys": [
                            r"""
Heaps order negative numbers perfectly well; `-2` compares below `1` the way it should,
and no comparison-based priority queue cares about the sign of its keys. The thing that
breaks is a layer above the heap: the algorithm's claim that the minimum key on the heap
is a *final* distance. That claim is about the graph, not the data structure, and
swapping in a Fibonacci heap or a sorted list changes nothing about it.
                            """,
                            r"""
Dijkstra is fine on directed graphs and on undirected ones, and it is run on both
routinely. Negative weights are the awkward case in the other direction: an undirected
negative edge is a negative cycle immediately, since you can traverse it back and forth
forever, which is why negative weights are usually discussed on directed graphs. That is
a fact about where negative edges can meaningfully live, not about what Dijkstra assumes.
                            """,
                            r"""
The counterexample needs no cycle at all — four edges, `s->a`, `s->b`, `b->a`,
`a->t`, and no way back to anything — and `t` still comes out at 3 against a true distance
of 2. So a single negative edge is enough. The guard after the pop is lazy deletion of
superseded heap entries and nothing more: it discards a stale entry, and it has no way to
re-expand a vertex that has already been settled and left the queue. Note where the damage
lands, too — `a`'s own distance is eventually corrected to 1, and it is `t`, downstream of
the edge `a` had already relaxed, that keeps the stale number. Tolerating negative edges
as long as no negative cycle exists is precisely what Bellman-Ford is for, and it is why
the module ships both.
                            """,
                            r"""
Right, and the sharpest way to hold it is that Dijkstra never reconsiders. Extraction is
a commitment, the commitment is justified by `everything from here on costs at least 0`,
and a negative edge is the counterexample to that clause. Bellman-Ford makes no such
commitment — it relaxes every edge every round and lets a distance fall as late as it
likes — which is exactly the trade it makes for its worse bound.
                            """,
                        ],
                    },
                    {
                        "q": "What is the guard `if d > dist[u]: continue` doing right after the pop?",
                        "opts": [
                            "Discarding a heap entry that a later improvement superseded, which is what replaces decrease-key",
                            "Catching a negative weight before it can corrupt distances the algorithm has already settled",
                            "Stopping the search once the goal vertex has been settled, so the loop can exit early",
                            "Stopping the same vertex from being pushed onto the heap twice, which would break the `E log V` bound",
                        ],
                        "a": 0,
                        "why": r"""
Lazy deletion. When a vertex's distance improves, the entry already sitting in the heap
becomes stale, and there is no cheap way to reach in and rewrite it — a real decrease-key
needs handles from each vertex into its heap node and roughly doubles the amount of code.
So the stale entry is left to rot and this line throws it away when it surfaces. Far from
preventing duplicate pushes, the guard is what makes them safe: there is at most one push
per successful relaxation, so the heap never holds more than `E + 1` entries, and `log E`
is `O(log V)` on a simple graph.
                        """,
                        "whys": [
                            r"""
Right, and the trade is worth stating explicitly because it is the reason almost every
real implementation looks like this one. Decrease-key gives a heap of at most `V` entries
and an `E + V log V` bound with a Fibonacci heap; lazy deletion gives a heap of up to `E`
entries and `E log V` with a binary heap, in about a third of the lines and with no
handles to keep in step. On a sparse graph the two are within a constant factor, and the
simpler one wins.
                            """,
                            r"""
Nothing here inspects a weight, so nothing here could detect a negative one — the guard
compares a popped distance against the current best for the same vertex, and both of
those are non-negative sums under the algorithm's assumption. Dijkstra has no negative
weight detection anywhere, deliberately: it is a precondition, not a runtime check. What
does detect a negative structure is Bellman-Ford's extra round, and that is a separate
algorithm in a separate function.
                            """,
                            r"""
An early exit on the goal is a real and correct optimisation — once the target is
extracted its distance is final, so `shortest_path` may stop there — but it is a
different line in a different place, testing `u == target` rather than comparing
distances. This guard fires on stale entries for every vertex, including ones nowhere
near the goal, and it fires many times per run. Removing it would not affect termination;
it would affect how much stale work gets done, and on some graphs the correctness of the
distances it would then overwrite.
                            """,
                            r"""
Duplicate pushes are not prevented, they are the design. Every successful relaxation
pushes, so a vertex can appear on the heap once per incoming edge that improved it, and
the heap holds up to `E + 1` entries. That is exactly what makes the guard necessary
rather than optional. The bound survives because `log E` is `O(log V)` on a simple graph,
where `E` is at most `V^2` — so `E log E` and `E log V` are the same thing up to a
constant, and nothing is lost by letting the duplicates in.
                            """,
                        ],
                    },
                    {
                        "q": "Bellman-Ford relaxes every edge for `V - 1` rounds. Why that many?",
                        "opts": [
                            "The distances converge geometrically, and `V - 1` rounds is the safe over-estimate that follows",
                            "A simple shortest path has at most `V - 1` edges, and round `k` settles every path of `k` edges",
                            "The `V`-th round is reserved for the negative-cycle test, so one round has to be surrendered",
                            "A shortest-path tree is a spanning tree, and a spanning tree on `V` vertices has `V - 1` edges",
                        ],
                        "a": 1,
                        "why": r"""
Induction on the number of edges in the path. After one full pass, every vertex one edge
from the source is correct; after two, every vertex two edges away; and so on, because a
pass relaxes every edge and so in particular relaxes the last edge of every such path. A
simple path cannot use more than `V - 1` edges without revisiting a vertex, and when there
is no negative cycle a shortest path never has any reason to revisit one. So `V - 1`
rounds cover every path that could be shortest, and the bound is on the number of *edges*
in a path rather than on anything about the weights.
                        """,
                        "whys": [
                            r"""
Nothing converges geometrically here, and the word is a clue that the wrong kind of
algorithm is in mind — iterative numerical methods converge, and their stopping rules
depend on the magnitudes involved. Bellman-Ford is exact and combinatorial: after round
`k` a specific finite set of distances is exactly right, not approximately right, and
`V - 1` is a tight bound rather than a safety margin. It is tight because a path graph
really does need all `V - 1` rounds when the edges are scanned in the unlucky order.
                            """,
                            r"""
Right, and the clause about round `k` is what makes it a proof rather than a plausible
count. Each pass extends the guarantee by one edge, regardless of the order the edges are
scanned in — a lucky order finishes sooner, which is why the early exit on a round with no
change is sound, but the worst case needs all `V - 1`. The bound is on path length in
edges, so it holds however large or small the weights are.
                            """,
                            r"""
The test round is a consequence of the bound, not its cause. Because `V - 1` rounds
already suffice for every shortest path, any further improvement in round `V` proves that
some path used `V` edges or more — which means it repeated a vertex, which means it went
round a cycle, and it only helped if that cycle was negative. Read the reasoning in this
order and the test round is free. Read it the other way and you are left explaining why
`V` rounds were needed in the first place.
                            """,
                            r"""
The shortest-path tree does have `V - 1` edges when every vertex is reachable, so the
number is right and the coincidence is genuinely tempting. But it counts the wrong thing:
the tree's edge count is a global fact about the output, while what the rounds need is a
bound on the length of a single root-to-vertex path. Those differ, and you can see it on
a star, where the tree has `V - 1` edges and no path is longer than 1 — one round would
do, and the algorithm still runs `V - 1` because it cannot know that in advance.
                            """,
                        ],
                    },
                    {
                        "q": "A negative cycle sits in a component the source cannot reach. Why must `bellman_ford` stay silent about it?",
                        "opts": [
                            "A negative cycle in a component the source cannot reach cannot exist in a directed graph",
                            "Bellman-Ford only inspects edges leaving a vertex it has already relaxed, so it never sees it",
                            "The distances it reports are distances from the source, and that cycle changes none of them",
                            "The `V - 1` rounds would already have surfaced it if it were going to matter to anyone",
                        ],
                        "a": 2,
                        "why": r"""
The function answers one question — how far is everything from the source — and an
unreachable cycle leaves every one of those answers at `inf`, however negative it is.
Raising would be a refusal to answer a question that has a perfectly good answer, and the
lab pins it down with a graph holding both a reachable component and a separate negative
loop. The `dist[u] != inf` guard on each relaxation is what keeps the distinction alive:
without it, `inf + (-5)` would be an improvement on `inf` and the unreachable cycle would
start manufacturing finite distances out of nothing.
                        """,
                        "whys": [
                            r"""
Nothing forbids it. Take `x->y` at 1, `y->x` at -3 with the source somewhere else
entirely: two vertices, two edges, a cycle of weight -2, and no path from the source to
either of them. Directedness has nothing to do with reachability — a directed graph can
have any number of components the source cannot enter, and that is precisely the case the
lab constructs.
                            """,
                            r"""
Bellman-Ford does the opposite: it scans the entire edge list every round, settled or
unsettled, reachable or not, and that indiscriminate sweep is the whole difference between
it and Dijkstra. It has no frontier and no notion of which vertices it has reached. So the
unreachable cycle's edges are inspected every round; what stops them mattering is the
`dist[u] != inf` guard, which refuses to relax out of a vertex that has no finite distance
yet.
                            """,
                            r"""
Right, and the general shape is worth carrying: an error should be raised when the caller
cannot be given a correct answer, not whenever something unusual is noticed. Here every
reported distance is correct and no amount of negativity in an unreachable component can
change one of them, so there is nothing to warn about. If the caller wants to know about
cycles anywhere in the graph, that is a different query, and it is answered by running the
detection from a virtual source with a zero-weight edge to every vertex.
                            """,
                            r"""
The rounds do surface it, and that is exactly the difficulty rather than the resolution.
Bellman-Ford scans the whole edge list on every round, so the unreachable cycle's edges
are examined `V - 1` times and turn up under the algorithm's nose. The `dist[u] != inf`
guard is what stops them doing anything: relaxing from a vertex at infinite distance is
refused, so the cycle never improves anything and never trips the detection round. It has
to be deliberately ignored, not accidentally missed.
                            """,
                        ],
                    },
                    {
                        "q": "Union-find with path compression and union by size costs what per operation, and what does that mean for Kruskal?",
                        "opts": [
                            "Constant in the worst case, which is why Kruskal is linear once its edges have been sorted",
                            "Logarithmic in the worst case per operation, which is exactly where Kruskal's `E log E` comes from",
                            "Logarithmic amortised, matching the heap operations that Dijkstra's `E log V` is built from",
                            "Near-constant amortised — inverse Ackermann, under 5 for any real input — so the sort dominates",
                        ],
                        "a": 3,
                        "why": r"""
The two optimisations together give an amortised bound of the inverse Ackermann function
in the number of elements, which is at most 4 or 5 for any input that can physically
exist. So the union-find is not what Kruskal pays for: sorting `E` edges costs
`E log E`, and the `E` find-and-union operations on top of that are near-linear. The
practical reading is that Kruskal is a sort with a cheap filter after it, which is also
why it is the algorithm of choice when the edges arrive already sorted.
                        """,
                        "whys": [
                            r"""
The bound is not constant in the worst case, and it cannot be — there is a proved lower
bound showing that no union-find structure achieves constant worst-case time per
operation in this model. What is true is that inverse Ackermann is so slow-growing that
the difference is invisible in practice, and the conclusion drawn here is nearly right for
the wrong reason: Kruskal is not linear after the sort, it is `E` times a factor that is
under 5, which is a distinction only a proof cares about.
                            """,
                            r"""
`E log E` is Kruskal's bound and this is the wrong account of where it comes from. It
comes from sorting the edges, which happens once, before any union-find operation is
performed. Union by size alone would give a logarithmic bound on `find`; adding path
compression takes it to inverse Ackermann, and the two together are why the data structure
disappears from the analysis. Hand Kruskal a pre-sorted edge list and the `log` goes with
the sort, leaving a near-linear run.
                            """,
                            r"""
The two logarithms belong to different structures. Dijkstra's comes from the heap, where
`log V` really is the cost of an operation and really does appear in the final bound.
Union-find is not a heap and has no comparison tree to descend — after path compression
most roots are one hop away — and its bound is inverse Ackermann rather than logarithmic.
Matching the two up is tempting because both algorithms end up with a `log` in their
totals, but Kruskal's comes from the sort.
                            """,
                            r"""
Right, and the word `amortised` is carrying real weight. A single `find` can still walk a
long path — the bound is over a sequence of operations, not over each one — and the
compression that flattens the path is what pays for the next caller. That is the same
accounting the vector's doubling used two courses ago: an expensive operation is allowed
provided it buys cheapness for the ones after it.
                            """,
                        ],
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
                            "Nothing says which endpoint an optimal cover uses, and taking both keeps the picked edges disjoint",
                            "A vertex cover has to contain both endpoints of every edge it covers, so there is no choice to make",
                            "Taking only one endpoint would leave the edge that was just picked uncovered by the cover",
                            "The higher-degree endpoint is the better pick, but taking both keeps the analysis simple",
                        ],
                        "a": 0,
                        "why": r"""
One endpoint would cover that edge perfectly well. The difficulty is that you cannot tell
which one is useful, and choosing badly is unbounded rather than merely suboptimal: on a
star, picking the leaf every time costs `n - 1` vertices where the centre alone would have
done. Taking both costs a factor of exactly 2 and buys the property that makes the factor
provable — the picked edges share no vertex, so they form a matching, and that matching is
the lower-bound certificate. This is the shape of most approximation arguments: give up a
little to gain something you can prove.
                        """,
                        "whys": [
                            r"""
Right, and the second clause is the one doing the work. Covering the edge is easy;
producing a *certificate* is not, and taking both endpoints is what forces the picked
edges to be vertex-disjoint. That disjointness is what lets you say `OPT` is at least the
number of picked edges, and without it the algorithm would still return a cover with no
way to bound how bad it was.
                            """,
                            r"""
This is definitionally false and it is worth seeing why it matters: a vertex cover is a
set of vertices touching every edge, so one endpoint per edge is enough. If a cover
really did need both endpoints of every edge, then the only cover would be the entire
vertex set of any graph with no isolated vertices, the optimisation problem would be
trivial, and there would be nothing for anyone to approximate. The algorithm takes both
endpoints by choice, not by obligation.
                            """,
                            r"""
The picked edge would be covered by either endpoint on its own — that is what covering an
edge means. The edge is not the problem. The problem is every *other* edge that touches
the endpoint you did not take, and the risk that the one you did take was the useless one.
On a star with the centre `c` and leaves `l1 ... lk`, picking a leaf covers the edge you
picked and leaves `k - 1` edges still uncovered, each of which will cost you another leaf.
                            """,
                            r"""
The higher-degree endpoint is the more intelligent-looking pick, it wins on most graphs
you would draw by hand, and it has no constant-factor guarantee at all — there are
families where repeatedly taking the highest-degree vertex is dragged to about `log n`
times the optimum. So this is not a simplification of a better rule; it is a different
rule with a worse worst case. The half that is right is that the choice was made for the
analysis, and the reason is that the analysis is the deliverable: a cover with a proof
beats a cover without one.
                            """,
                        ],
                    },
                    {
                        "q": "The algorithm returns a matching alongside the cover. What does that matching certify?",
                        "opts": [
                            "Nothing about `OPT` — it is a record of how the cover was built, not evidence about the optimum",
                            "`OPT >= len(matching)` — matched edges share no vertex, so each needs its own cover vertex",
                            "`OPT <= len(matching)`, which is the bound that pins the cover from above",
                            "`OPT == 2 * len(matching)`, which is where the ratio of exactly 2 comes from",
                        ],
                        "a": 1,
                        "why": r"""
The certificate is a **lower** bound, and that is the hard half. The cover's size is
sitting in front of you; `OPT` is the thing nobody can compute. The matching supplies a
bound on it for free: no two matched edges share a vertex, so no single vertex can cover
two of them, and therefore every cover — the optimal one included — is at least as large
as the matching. Put that beside `len(cover) == 2 * len(matching)` and the ratio of 2
follows without `OPT` ever being computed. That is what an approximation guarantee is made
of, and it is why the lab returns the matching rather than discarding it.
                        """,
                        "whys": [
                            r"""
It is a record of how the cover was built, and that record is precisely what makes it
evidence. The construction guarantees the picked edges are pairwise vertex-disjoint —
each was picked while still uncovered — and vertex-disjointness is a property of the
graph, not of the algorithm. Anyone can check it in linear time without trusting the run
that produced it, which is what turns a trace into a certificate. That is the difference
the module is drawing: a heuristic's ratio is a fact about the algorithm, while a
certificate makes the bound checkable on the instance in front of you.
                            """,
                            r"""
Right, and the reason it has to be a lower bound is worth being explicit about. You
already know an upper bound on `OPT` — the cover you just built is one — so an upper bound
adds nothing. What blocks the ratio argument is the other side: `len(cover) / OPT` cannot
be bounded until `OPT` is bounded from below, and the matching is what supplies that
without solving the problem.
                            """,
                            r"""
`OPT <= len(matching)` is false as well as useless. It is false because a triangle has a
matching of size 1 and an optimum of 2, so the optimum can exceed the matching. And it
would be useless even if true, because the cover already gives an upper bound on `OPT`
for nothing — every cover is at least as large as the smallest one. The bound the
argument is missing is always the lower one.
                            """,
                            r"""
Equality is far too strong, and the triangle refutes it immediately: the matching has one
edge and `OPT` is 2, so `2 != 2 * 1` fails by a factor. Where the 2 does appear is in
`len(cover) == 2 * len(matching)`, which is a fact about what the algorithm returned and
holds exactly, by construction — every picked edge contributes both of its endpoints.
Combining that identity with the inequality is what produces the ratio; asserting the
identity of `OPT` itself would mean having solved the problem.
                            """,
                        ],
                    },
                    {
                        "q": "`ratio([(0, 1), (1, 2), (2, 3)])` is exactly 2.0. What makes that instance tight?",
                        "opts": [
                            "It is not special — the guarantee is 2, so every instance comes out at 2 by definition",
                            "The vertex count is even, so the edges the algorithm picks match up all of them exactly",
                            "The edges it picks form a matching of size 2, so it takes all 4 vertices where 2 would do",
                            "Every path graph comes out at 2.0, whatever order its edges are handed to the algorithm in",
                        ],
                        "a": 2,
                        "why": r"""
The algorithm picks `(0, 1)` and takes both endpoints; `(1, 2)` is now covered and is
skipped; then it picks `(2, 3)` and takes both. Two disjoint edges, four vertices, where
`{1, 2}` covers all three edges. The guarantee is achieved rather than approached, and
that is what stops anyone proving a better constant for this algorithm — a proof of 1.9
would have to be false on this four-vertex graph. Note that the order matters and the lab
fixes it deliberately: hand the same path in as `[(1, 2), (0, 1), (2, 3)]` and the
algorithm picks the middle edge, covers everything with two vertices and scores 1.0.
                        """,
                        "whys": [
                            r"""
A worst-case guarantee is a ceiling on every instance, not a prediction about any of them,
and most instances come in well under it. The triangle scores 1.0 — the algorithm picks
one edge, takes two vertices, and two is the optimum. The same path graph scores 1.0
under a different edge order. If every instance really did land on the bound the
algorithm would be useless in practice as well as in theory, and there would be no point
measuring a ratio at all.
                            """,
                            r"""
The matching being perfect is a real observation and it is true here — both picked edges
together use all four vertices. What it is not is the mechanism, and the parity is a
coincidence. What makes the ratio 2 is that the optimal cover is exactly the size of the
matching, 2, while the algorithm spends `2 * 2 = 4`; tightness needs `OPT` to be *equal*
to the matching rather than larger. Extend the path to five vertices,
`[(0, 1), (1, 2), (2, 3), (3, 4)]`, and the count is odd and the matching covers four of
the five rather than all of them — and the ratio is still exactly 2.0, four vertices
against the optimal `{1, 3}`.
                            """,
                            r"""
Right, and the tightness is what the instance is for. An approximation guarantee is only
interesting alongside evidence that it cannot be improved, and a single instance achieving
the bound is that evidence. It also shows where the factor of 2 physically goes: both
picked edges contributed a vertex that the optimal cover did not want, and on this graph
that is every vertex the algorithm took.
                            """,
                            r"""
The same path graph scores 1.0 under a different edge order — hand it in as
`[(1, 2), (0, 1), (2, 3)]` and the algorithm picks the middle edge first, covers all
three edges with `{1, 2}` and matches the optimum exactly. So order is the whole story on
this instance, which is why the lab fixes the order rather than leaving it to the caller.
A worst-case guarantee describes the worst order, not every order.
                            """,
                        ],
                    },
                    {
                        "q": "Vertex cover is NP-complete. Which reading of that is right?",
                        "opts": [
                            "Every instance of it needs exponential time, which is what the completeness is asserting",
                            "No approximation algorithm with a constant ratio can exist for it, or the classes would collapse",
                            "The problem sits outside NP, since no polynomial algorithm for it has ever been found",
                            "The decision version is in NP and all of NP reduces to it — the optimisation version is NP-hard",
                        ],
                        "a": 3,
                        "why": r"""
NP-completeness is two claims joined by an `and`: membership and hardness. Membership is
about the decision version — `is there a cover of size at most k` — which is in NP because
a cover of size `k` is a certificate anyone can check in linear time. Hardness is that
every problem in NP reduces to it. The optimisation version cannot be in NP at all, since
`this is the smallest` is not something a witness settles, so it is called NP-hard rather
than NP-complete. Keeping the two versions apart is most of what it takes to read the
statement correctly.
                        """,
                        "whys": [
                            r"""
Completeness says nothing about individual instances, only about the worst case over all
of them, and plenty of instances are easy. The lab's exhaustive search clears 18 nodes
without complaint; trees fall to a linear-time dynamic program; bipartite graphs fall to
matching by König's theorem. A problem can be NP-complete and still have large, useful
families that are solved in polynomial time, and most real work on hard problems consists
of finding those families.
                            """,
                            r"""
This module contains a constant-factor approximation for it, so the claim is refuted by
the code the lab is about to make you write — the ratio is 2, and it is proved rather than
observed. NP-hardness bounds what can be computed *exactly* in polynomial time; it says
nothing on its own about approximation. There are inapproximability results for vertex
cover, and they are much more delicate than this: no ratio below 1.36 unless P equals NP,
and none below 2 under the unique games conjecture. Note that they rule out doing better
than 2, not doing 2.
                            """,
                            r"""
This gets the containment backwards. Being in NP means a proposed answer can be *checked*
quickly, not that one can be *found* quickly, and vertex cover is in NP for the easy
reason that a candidate cover is checked by walking the edge list once. Whether a
polynomial algorithm exists is the P versus NP question, and it is open — nobody has ruled
one out either. NP is a class of problems with short verifiable certificates, and almost
everything anyone works on lives comfortably inside it.
                            """,
                            r"""
Right, and the reason the distinction is drawn so carefully is that both halves are load
bearing. Membership without hardness would make it an ordinary NP problem; hardness
without membership makes it NP-hard, which is what the optimisation version is. The
certificate is what supplies membership, and it is the same object the approximation
algorithm hands back — a set of vertices you can check by walking the edge list once.
                            """,
                        ],
                    },
                    {
                        "q": "Why is 'repeatedly take the highest-degree vertex' not a constant-factor approximation?",
                        "opts": [
                            "There are graph families where its ratio grows like `log n`, so no constant can bound it",
                            "It can fail to produce a cover at all on graphs where several degrees tie",
                            "It is slower than the matching algorithm, and a ratio is only claimed for linear-time rules",
                            "It hands back no certificate, and a ratio cannot be claimed without evidence about `OPT`",
                        ],
                        "a": 0,
                        "why": r"""
It is the more intelligent-looking rule, it beats the matching algorithm on most graphs
you would draw by hand, and it has no constant guarantee: bipartite families can be
constructed on which it is dragged into taking about `log n` times the optimum. That is
the lesson worth carrying out of the module — a heuristic that usually wins and an
algorithm with a proof are different kinds of object, and which one you want depends on
whether you need a good answer or a bounded one.
                        """,
                        "whys": [
                            r"""
Right, and the construction is worth knowing in outline: a bipartite graph with one side
of `n` vertices and the other split into groups of sizes `n/2, n/3, ... , n/n`, wired so
that the greedy rule is tempted into the large side group by group. The optimum is the
side of size `n`, and the greedy total is the sizes of those groups added up:
`n/2 + n/3 + ... + n/n`, which is `n(H_n - 1)` and grows like `n log n`. Divide one by the
other and the ratio is `H_n - 1` itself — 6.5 at a thousand vertices, 13.4 at a million,
climbing without ever settling. Nothing is malformed about the instance; it is a graph, and that is what
makes the absence of a constant a fact about the rule rather than about the input.
                            """,
                            r"""
It always produces a cover, and ties change nothing: whichever vertex is taken, its edges
are removed, and the loop runs until no edge is left. That termination condition is what
guarantees a cover — an edge can only survive by having neither endpoint taken, and the
loop does not stop while such an edge exists. The rule's failure is one of quality, not of
validity, which is exactly what makes it dangerous. An algorithm that broke visibly would
never have been proposed.
                            """,
                            r"""
It is not meaningfully slower — both rules are near-linear with the right bookkeeping,
and the degree-based one is what most people would reach for first. Speed is not the axis
this fails on, and no approximation guarantee has ever been conditional on running time:
the ratio and the complexity are separate claims about an algorithm, and a slow algorithm
with a proved ratio is still an approximation algorithm.
                            """,
                            r"""
An algorithm's ratio is a fact about the algorithm, true or false whether or not the
implementation hands you the evidence. The matching is valuable for a different reason:
it makes the bound checkable on the instance in front of you rather than only provable in
general, so you can look at one run and know it. The greedy degree rule's problem is not
that its certificate is missing but that no constant bound exists to certify — supplying
a certificate would require a bound to certify, and there is not one.
                            """,
                        ],
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
