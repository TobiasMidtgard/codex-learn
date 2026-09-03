"""CS201 — Data Structures & Algorithms. Author module."""

COURSE = {
    "id": "CS201",
    "title": "Data Structures & Algorithms",
    "year": 2,
    "level": "Intermediate",
    "prereqs": ["CS102", "MA101"],
    "stack": ["Python", "C (reference)"],
    "credits": 15,
    "hours": 160,
    "icon": "≡",
    "summary": (
        "Python hands you a list and a dict and asks no questions. This course opens "
        "both of them up: you build the growable array, the linked list, the stack, "
        "the queue, the search tree, the hash table and the heap from nothing but "
        "fixed slots and references, instrument each one so its cost is visible, and "
        "then compare implementations on measured operation counts rather than folklore."
    ),
    "outcomes": [
        "Implement a growable array and argue its amortised cost from a counted resize schedule",
        "Choose between contiguous and linked storage from the operation mix a workload demands",
        "Apply stacks, queues and monotonic deques to parsing and windowing problems",
        "Implement binary search tree insertion, deletion in all three cases, traversal and height",
        "Build hash tables with both separate chaining and open addressing, including tombstones",
        "Implement a binary heap and the three classic O(n log n) sorts, and test sorting stability",
        "Compare two implementations of one ADT using deterministic operation counts",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone ordered-map build (60%).",
    "reading": [
        "Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms*, 4th ed. — chapters 2, 6, 10-12",
        "Sedgewick & Wayne, *Algorithms*, 4th ed. — sections 1.3-1.4, 2.1-2.3, 3.1-3.4",
        "Skiena, *The Algorithm Design Manual*, 3rd ed. — chapters 3-4",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Sequences: contiguous versus linked",
            "summary": "A growable array and a linked list, both instrumented so the cost shows.",
            "concepts": [
                "Random access needs contiguous slots; O(1) splicing needs references",
                "A dynamic array wraps a fixed backing store, a length and a capacity",
                "Doubling on overflow makes append O(1) amortised; growing by a constant does not",
                "The aggregate argument: n appends cost fewer than 3n slot writes in total",
                "Shrinking at a quarter full, not a half, avoids thrashing on push/pop cycles",
                "A tail pointer is what makes appending to a singly linked list O(1)",
                "Big-O hides constants: cache locality is why arrays usually still win",
            ],
            "read": [
                {
                    "title": "Lockers, treasure hunts, and where an append's cost goes",
                    "minutes": 14,
                    "body": r'''
A row of parcel lockers runs along the wall of a sorting office, numbered from 0. A
courier holding a slip that says *locker 4017* does not walk the row reading labels:
she knows where locker 0 is and how wide each locker is, multiplies, and goes straight
there. That is an **array**. The slots are contiguous, so an index turns into an
address by one multiplication and one addition, and slot 4017 costs exactly what slot
0 costs.

Now picture a treasure hunt instead. Each clue is hidden somewhere in a park, and every
clue says where the next one is. There is no arithmetic that gets you to the 4017th
clue: the only route is through the 4016 before it. That is a **linked list**. Each
cell holds a value and a reference to the next cell, and the cells can be anywhere at
all — which is the whole of its weakness and, as it turns out, the whole of its
strength.

Python hands you `list` and asks no questions. This module opens it up, because the two
questions that decide which container to reach for — what happens when the lockers run
out, and what it costs to get to the end of the hunt — both have exact answers, and
both are worth deriving rather than memorising.

## When the lockers run out

An array is a fixed block of slots. That is what makes indexing cheap, and it is also a
problem the moment a 17th value arrives at a block of 16. The slots after the block
belong to something else, so the only option is to get a bigger block, copy everything
across, and let the old one go.

So a growable array is three things: a **backing store** of some fixed capacity, a
**length** saying how much of it is live, and a rule for what to do when the two meet.
The copy is the expensive part, and the only decision that matters is *how much bigger*
the new store should be. Here is the rule everybody uses, with a counter on every slot
write so the cost is visible rather than assumed:

```python
class DynamicArray:
    """A growable array over a fixed backing store, with every write counted."""

    def __init__(self, capacity=1):
        self.capacity = capacity
        self._store = [None] * capacity
        self._size = 0
        self.writes = 0
        self.resizes = 0

    def _resize(self, capacity):
        store = [None] * capacity
        for i in range(self._size):
            store[i] = self._store[i]
            self.writes += 1
        print(f"resize {self.capacity:>2} -> {capacity:>2}, copied {self._size:>2}")
        self._store = store
        self.capacity = capacity
        self.resizes += 1

    def append(self, value):
        if self._size == self.capacity:
            self._resize(self.capacity * 2)
        self._store[self._size] = value
        self.writes += 1
        self._size += 1


array = DynamicArray()
for value in range(16):
    array.append(value)
print("capacity", array.capacity, "resizes", array.resizes, "writes", array.writes)
```

Sixteen appends from capacity 1 cost 4 resizes and 31 writes: the 16 stores, plus
copies of 1, 2, 4 and 8. Those copies are a geometric series, and that is the entire
argument in one line.

## Counting the copies

Take $n = 2^{k}$ appends, so the store doubles exactly $k$ times and ends up exactly
full. Each doubling copies the live prefix, which at that moment is the old capacity, so
the copies are $1, 2, 4, \dots, 2^{k-1}$. Add them:

$$1 + 2 + 4 + \dots + 2^{k-1} = 2^{k} - 1 = n - 1.$$

The trick that proves it is one you will use again in the heap module: call the sum $S$,
double it to get $2 + 4 + \dots + 2^{k}$, subtract, and everything cancels except the
two ends. So the copies alone come to one fewer than the number of appends, and the
total writes are the $n$ stores plus $n - 1$ copies:

$$W = 2n - 1, \qquad \frac{W}{n} = 2 - \frac{1}{n}.$$

Under two writes per append, and falling. When $n$ is not a power of two the last
doubling happens before the final append, so the copies stop at the largest power of two
below $n$ and still total less than $2n$ — sixteen appends copy 15, seventeen copy 31,
and both stay under $3n$ all told. That is what **$O(1)$ amortised** means: not that any
particular append is cheap, but that the sum over all of them is proportional to their
number.

Now replace doubling with the rule that looks thriftier: grow by a fixed 100 slots
whenever the store fills. The copies are now $c, 2c, 3c, \dots$ up to about $n$, an
arithmetic series of about $n/c$ terms averaging $n/2$, so they total roughly

$$\frac{n}{c} \cdot \frac{n}{2} = \frac{n^{2}}{2c}.$$

The $n^{2}$ is not a constant factor to tune away later. Run both policies for ten
thousand appends and the gap is already a factor of nineteen:

```python
def total_writes(n, grow):
    """Slot writes for n appends under a growth rule, starting from capacity 1."""
    capacity, size, writes = 1, 0, 0
    for _ in range(n):
        if size == capacity:
            writes += size            # the copy
            capacity = grow(capacity)
        writes += 1                   # the store
        size += 1
    return writes


n = 10_000
print("doubling:      ", total_writes(n, lambda c: c * 2))
print("plus a hundred:", total_writes(n, lambda c: c + 100))
```

Doubling: 26,383 writes. Growing by a hundred: 505,100. Push $n$ to a million and the
first is about two million while the second is about five *billion*. The thing people
get backwards here is which policy wastes memory. Doubling is the wasteful one — a
freshly doubled store sits half empty, and that idle half is exactly what pays for the
cheap appends. The fixed increment never holds more than 100 spare slots, and pays for
the thrift in copying.

## Shrinking, and the trap at a half

If the array can grow it should be able to shrink, or a container that once held a
million values and now holds ten keeps a million slots forever. The rule that suggests
itself is the mirror of doubling: when the array falls to half full, halve the capacity.
It is wrong, and it is wrong in a way that no test about *values* will ever catch.

Picture an array of capacity 16 holding 9 values, and a workload that pushes and pops
alternately. A pop takes it to 8, which is half full, so it halves to 8 — copying 8
values — and comes out of the shrink *completely full*. The very next push finds no
room and doubles straight back to 16, copying 8 again. Then a pop halves it. Every
single operation copies the whole array, and the amortised bound has gone entirely.

```python
def alternate(shrink_at, operations=1000):
    """Push and pop on the boundary; count the slot writes each policy makes."""
    capacity, size, writes = 16, 9, 0
    for step in range(operations):
        if step % 2 == 0:                       # pop
            size -= 1
            if capacity > 1 and size * shrink_at <= capacity:
                writes += size                  # the shrink copies what is live
                capacity //= 2
        else:                                   # push
            if size == capacity:
                writes += size                  # the growth copies it all again
                capacity *= 2
            writes += 1
            size += 1
    return writes


print("shrink at a half:   ", alternate(2))
print("shrink at a quarter:", alternate(4))
```

Waiting until a **quarter** full before halving leaves the array half full after the
shrink, with room to move in both directions; a linear number of operations is needed
before either trigger can fire again, and that is what spreads the next copy's cost
out. A thousand alternating operations cost 8500 writes under the half rule and 500
under the quarter rule — the 500 stores, and not one copy. The gap between the two
triggers *is* the amortisation. Close the gap to nothing and you close the amortisation
with it.

## The treasure hunt

A linked list is a chain of cells, each holding a value and a reference to the next.
Nothing is contiguous, nothing can be reached by arithmetic, and the honest cost of
getting to cell $i$ is $i$ steps. That makes `find` a walk that pays one step per cell
examined — and it makes the end of the list a very long way from the start.

Which is why a singly linked list keeps a **tail pointer**. Without one, appending means
walking to the last cell first: $O(n)$ per append and $O(n^{2})$ for building a list of
$n$. With one, an append is three constant-time moves: make the cell, hang it off
`tail.next`, move `tail` along.

```python
class ListNode:
    """One cell: a value and a reference to the next cell."""

    def __init__(self, value, next=None):
        self.value = value
        self.next = next


class SinglyLinkedList:
    """Head, tail, and a counter for every node a traversal visits."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.steps = 0

    def push_back(self, value):
        node = ListNode(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node

    def find(self, value):
        node, index = self.head, 0
        while node is not None:
            self.steps += 1
            if node.value == value:
                return index
            node = node.next
            index += 1
        return -1


lst = SinglyLinkedList()
for value in range(1000):
    lst.push_back(value)
print("steps after 1000 push_backs:", lst.steps)
print("find(999) ->", lst.find(999), "in", lst.steps, "steps")
```

A thousand appends and not one node visited. The step counter is there so the
difference shows: `find(999)` has to touch all thousand cells, and it does. Note what
kind of claim the tail pointer makes. It is not amortised — it is not a statement about a
total — it is a true constant on every single call, and the two are worth keeping
apart, because only one of them promises anything about the call you are making right
now.

## What a reference buys back

Everything so far has gone the array's way. Here is what the list is for. Suppose you
are standing on a cell — you hold a reference to it, because you are iterating, or
because a cache handed it to you — and you want the cell after it gone. Two reads and
one write, and nothing else in the chain is touched:

```python
class ListNode:
    """One cell: a value and a reference to the next cell."""

    def __init__(self, value, next=None):
        self.value = value
        self.next = next


head = ListNode("a", ListNode("b", ListNode("c", ListNode("d"))))
cursor = head.next                  # standing on "b"
cursor.next = cursor.next.next      # unhook "c": nothing after it moves
values = []
node = head
while node is not None:
    values.append(node.value)
    node = node.next
print(values)
```

The chain now reads `['a', 'b', 'd']`, and the cells holding `d` and anything after it
never heard about the change. In an array, deleting from the middle slides every later
element down one slot, which is $O(n)$ per deletion and $O(n^{2})$ for a loop that walks
a sequence deleting as it goes. That loop is precisely the workload a linked list exists
for.

But read the premise again: *standing on the cell*. The splice is $O(1)$ because the
node is already in hand. The moment the request is "delete the element at index
400,000", the list has to walk there first, and the walk costs what the array's shifting
would have cost. So the rule is not that lists are good at deleting. It is that a list
is good at deleting from a position you already hold — which is what an iterator, a
cursor, or the node handle in an LRU chain gives you. It is also why Python's
`list.remove(x)` is $O(n)$ and always will be: the search, not the removal, is the cost.

## Where the accounting stops being the whole story

Both containers traverse in $O(n)$, and on real hardware the array is several times
faster. Big-O throws away the constant, and on a modern machine the constant is memory.
Reading one array element brings a 64-byte cache line into the core — sixteen 32-bit
integers for the price of one miss, with the next line prefetched before it is asked
for. Each list cell was allocated at a different moment and can sit anywhere, so
`node.next` can be a fresh miss of a hundred-odd cycles, and worse, a miss that cannot
even be *started* until the previous one has returned, because the address is not known
until then.

This is why `list` in Python and `std::vector` in C++ are the default containers, and
why linked lists survive mostly where $O(1)$ splicing of a node you already hold is the
point. The asymptotic argument tells you which container to reach for when the operation
mix is lopsided; the cache tells you which to reach for when it is not.

## What you are about to build

The lab in this module is *A growable array and a linked list, counted*, and it is the
two structures above with their counters exposed. `DynamicArray` keeps `writes` and
`resizes`, counting one write for every value put into a slot of the backing store —
copies included, cleared slots excluded — and the checks are the numbers derived here:
sixteen appends from capacity 1 must cost exactly 4 resizes and 31 writes, a thousand
must cost 2023, and popping back down must halve at a quarter full and land at capacity
1 when the array empties. `SinglyLinkedList` keeps `steps`, one per node visited by a
traversal, and the check that matters is that 1000 calls to `push_back` leave it at
zero. If yours does not, the tail pointer is not being kept — usually because
`push_front` on an empty list or `pop_front` on a one-element list forgot to update it.
The fill-in-the-blanks unit walks the growth and shrink rules line by line, and the
derivation unit does the geometric series with symbols instead of a trace; between them,
the whole amortised argument fits in four numbers.
''',
                },
                {
                    "title": "Counting the work, not the seconds",
                    "minutes": 11,
                    "body": r'''
Two people ship the same feature. One version answers in nine milliseconds on the test
fixture and in forty minutes on the production table; the other answers in nine
milliseconds on both. Neither is wrong, and the machine is the same machine. What
differs is how the work each one does **grows** as its input grows, and that growth is a
property of the code you can read off the page before running anything.

**Big O** notation is how that growth gets written down. Saying a function is $O(n)$
says the work rises in proportion to the input, whatever the constant of proportionality
happens to be on this machine, in this language, this afternoon. Throwing the constant
away looks careless until you notice it is the part that does not survive: a faster
laptop, a newer interpreter, the same loop rewritten in C, each divides the constant and
leaves the shape untouched. Double the input instead and an $O(n)$ program does twice
the work while an $O(n^{2})$ one does four times — on every machine that will ever run
either of them.

## The shapes, at a size you will meet

| Growth | Name | Steps at a million items |
|---|---|---|
| $O(1)$ | constant | one, whatever $n$ is |
| $O(\log n)$ | logarithmic | about 20 |
| $O(n)$ | linear | a million, so hundredths of a second |
| $O(n \log n)$ | linearithmic | about 20 million, so a second or two |
| $O(n^{2})$ | quadratic | a million million: minutes to hours |
| $O(2^{n})$ | exponential | hopeless past $n = 40$ |

The two rows to hold on to are the last two, because they are the ones that turn a
program that worked in testing into a program that does not work at all. Everything
above $O(n \log n)$ scales; $O(n^{2})$ scales until the input does not fit in an
afternoon.

## Reading a loop for its shape

A loop over the input is $O(n)$. A loop *inside* a loop over the same input is
$O(n^{2})$, and the useful version of that statement is the count. Ask whether a list
holds a repeat by comparing every pair: the outer index $i$ runs over $n$ positions and
the inner one covers the $n - 1 - i$ positions after it, so the comparisons are
$n-1, n-2, \dots, 1$, which is the triangular sum

$$\frac{n(n-1)}{2}.$$

That is the same sum the constant-growth policy produced in the reading before this one,
and it is the same reason both are unusable: the leading term is $n^{2}/2$. Against it,
put the version
that remembers what it has already seen in a set, where a membership test is one hash
rather than a scan. Count both:

```python
def has_duplicate(items):
    """Compare every pair, counting the comparisons."""
    comparisons = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            comparisons += 1
            if items[i] == items[j]:
                return True, comparisons
    return False, comparisons


def has_duplicate_hashed(items):
    """One pass, with a set doing the remembering."""
    seen = set()
    lookups = 0
    for item in items:
        lookups += 1
        if item in seen:
            return True, lookups
        seen.add(item)
    return False, lookups


values = list(range(2000))     # no repeats, which is the worst case for both
print("every pair:", has_duplicate(values)[1], "comparisons")
print("with a set:", has_duplicate_hashed(values)[1], "lookups")
```

1,999,000 against 2,000: a factor of a thousand at two thousand items, and a factor of
ten thousand at twenty thousand, because the ratio between them is itself proportional
to $n$. The two functions are the same length and the same shape on the page. Only the
count separates them.

$O(\log n)$ is what halving looks like. Each step throws away half of what is left, so
the question is how many halvings a million survives:

```python
n, halvings = 1000000, 0
while n > 1:
    n //= 2
    halvings += 1
print(halvings, "halvings take a million down to one")
```

Nineteen. Binary search over a sorted array, the second lab in this module, is that loop
with a comparison attached to each halving — which is why it reads seventeen elements of
a hundred thousand where a scan reads fifty thousand before it finds the average one.

## The costs worth carrying in your head

| Operation | Cost | Why |
|---|---|---|
| `values[i]`, `values.append(x)` | $O(1)$ | an index is arithmetic; an append usually has room |
| `x in values`, `values.remove(x)` | $O(n)$ | nothing about a list says where `x` is |
| `x in seen`, `table[key]` | $O(1)$ | the hash computes the slot |
| `values.insert(0, x)`, `values.pop(0)` | $O(n)$ | every later element shifts one slot |
| `sorted(values)` | $O(n \log n)$ | a comparison sort cannot do better |

The mistake this table exists to prevent is a membership test against a **list** inside a
loop. It is tempting because the code is honest and reads well, the container is already
to hand, and on the twenty rows of test data it is instant. It is $O(n^{2})$, and the
repair is one word — build a `set` from the list before the loop and test against that.

## What it costs, and where it stops holding

`seen = set()` buys its speed with $O(n)$ extra memory. Most optimisations are that
trade, and the discipline is to name it when you make it rather than to notice it later
in a memory graph.

Two limits are worth stating plainly. First, Big O is a statement about growth, not about
time: it hides the constant, and at small $n$ the constant is the whole answer. CPython's
own `sorted` builds its initial runs with a binary insertion sort, which is $O(n^{2})$
and beats merging below about sixty-four elements — a deliberate choice, in the standard
library, to run the faster-growing algorithm exactly where its smaller constant wins.
Second, it hides *which* operations, and on real hardware they are not interchangeable —
walking a linked list and walking an array are both $O(n)$, and the array is several
times quicker for the cache reasons the previous reading gave.

So the analysis is a tool for a specific question: what happens when this input gets
large? Reach for it at that moment. For $n = 10$, reach for the version that is easier
to read.
''',
                },
            ],
            "quiz": {
                "title": "Where the cost of a growable array actually goes",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Starting from capacity 1, a dynamic array doubles whenever the backing store fills. Over $n$ appends, how many slot writes happen in total?",
                        "opts": [
                            "About $n\\log_2 n$: there are $\\log_2 n$ resizes and each one copies the whole store",
                            "Exactly $2n$: each element is written once on arrival and copied once, later on",
                            "Fewer than $3n$: the $n$ stores, plus copies forming a geometric series under $2n$",
                            "About $n^2/2$: every resize copies all that is already stored, and resizes are frequent",
                        ],
                        "a": 2,
                        "whys": [
                            r"There really are about $\log_2 n$ resizes, but they are nothing like equal — the last one alone copies more than every earlier one put together. Charging all of them the final size overstates the work by a factor of $\log n$.",
                            r"The closest of the wrong answers, and the reasoning is nearly right. But an element that arrives early is copied *repeatedly*: the very first element is copied at every single resize, all $\log_2 n$ of them. The copies total just under $2n$ on their own, before the $n$ stores are added.",
                            r"The copies are 1, 2, 4, 8 …, and they stop at the last doubling before the $n$th append.",
                            r"Quadratic is what growing by a *fixed* number of slots costs. Doubling makes resizes exponentially rarer as the array grows — about $\log_2 n$ of them over $n$ appends, not one every few.",
                        ],
                        "why": r"""
The copies are 1, 2, 4, 8 and so on, and the series stops at the last doubling
before the $n$th append, so it adds to $2^{\lceil\log_2 n\rceil} - 1$ — one less
than the first power of two at or above $n$, and therefore under $2n$. It comes to
exactly $n - 1$ only when $n$ is itself a power of two: sixteen appends copy 15, but
seventeen copy 31. Add the $n$ stores and the total is under $3n$, so the amortised
cost per append is a small constant.
""",
                    },
                    {
                        "q": "Why double the capacity rather than grow by a fixed 100 slots?",
                        "opts": [
                            "A fixed increment cannot be implemented unless the final length is known in advance",
                            "Doubling holds less memory at every moment, because it grows the store far less often",
                            "Doubling makes the copies a geometric series; a fixed increment makes them arithmetic",
                            "With doubling an element already in the store is never copied again, so nothing accumulates",
                        ],
                        "a": 2,
                        "whys": [
                            r"It is perfectly easy to implement — `capacity + 100` needs to know nothing about the future, and neither does `capacity * 2`. A fixed increment is not impossible, it is merely slow.",
                            r"Backwards, and instructively so. Doubling is the policy that wastes memory: a doubled store can sit half empty, and that idle half is precisely the price paid for cheap appends. A fixed increment never holds more than 100 spare slots — it just pays for that thrift in copying.",
                            r"$1+2+4+\dots < 2n$ against $c+2c+3c+\dots \approx n^2/(2c)$: geometric against arithmetic is the whole of it.",
                            r"Every growth copies every live element, however the new store was obtained — the first element is copied at all $\log_2 n$ resizes. What doubling changes is how *often* that happens, never whether it happens.",
                        ],
                        "why": r"""
With a fixed increment $c$ there are $n/c$ growths, copying $c$, then $2c$, then
$3c$ — an arithmetic series summing to roughly $n^2/(2c)$. Growing by 100 turns a
million appends into about five billion slot writes; doubling turns them into about
two million. What is bought with copying is paid for in memory, and the trade runs
the way most people first guess it does not: the fast policy is the wasteful one.
""",
                    },
                    {
                        "q": "The array halves its capacity when it falls to a quarter full rather than to a half. What does waiting until a quarter buy?",
                        "opts": [
                            "Shrinking at a half would drop the elements that no longer fit in the smaller store",
                            "At a half, alternating push and pop at the boundary resizes on every operation",
                            "A quarter is the largest fraction at which the geometric series still converges",
                            "It keeps `pop` at $O(1)$ worst case rather than $O(n)$ worst case, on every call",
                        ],
                        "a": 1,
                        "whys": [
                            r"Nothing is ever dropped. The shrink copies the live prefix, and at the moment it fires that prefix fills a quarter of the old store — so it fits in the halved one twice over. That is what the trigger guarantees.",
                            r"Come out of a shrink exactly full, and the very next append doubles straight back.",
                            r"Nothing here is converging or failing to. The copy series converges for any growth factor above one, and the shrink trigger is a different number altogether: the quarter is chosen to leave *slack* after the shrink, not to make a sum finite.",
                            r"No trigger makes `pop` $O(1)$ in the worst case — a shrink that does fire copies everything it keeps, under either rule. What the quarter buys is the *amortised* bound, and that is exactly what the half rule loses: alternating push and pop defeats it entirely. Worst case unchanged, average case rescued.",
                        ],
                        "why": r"""
Shrink at exactly half and the array comes out of the shrink completely full, so the
very next append doubles it straight back. Alternate a push and a pop on that
boundary and every single operation copies the whole array — $O(n)$ per operation,
with no amortisation left at all. Waiting until a quarter leaves the array half full
after the shrink, so a linear number of operations is needed to reach either trigger
again, and the cost of the next resize is spread over all of them. The gap between
the two triggers is the amortisation; closing it to nothing closes the amortisation
to nothing with it.
""",
                    },
                    {
                        "q": "`push_back` on the singly linked list is $O(1)$. What makes it so?",
                        "opts": [
                            "The list caches its length, so the position of the end is known without walking",
                            "Nodes are allocated from one contiguous block, so the end is a fixed offset away",
                            "The list keeps a reference to its last node, so nothing has to be walked",
                            "It is $O(1)$ amortised: the walk to the end happens, but only once in a while",
                        ],
                        "a": 2,
                        "whys": [
                            r"A length is a number, not an address. Knowing there are exactly 1000 nodes still leaves you following 1000 `next` links to reach the last one.",
                            r"Nodes are emphatically not contiguous — each is allocated separately, at whatever moment it was appended. That is the defining difference from the array, and it is why no arithmetic can reach the end.",
                            r"Allocate a node, hang it off `self.tail.next`, move `self.tail` on. Three constant-time steps, no walk.",
                            r"Nothing is amortised here: `push_back` costs the same three steps on the first call and on the millionth. The lab's assertion is `steps == 0` after 1000 calls — not a bound on the average, but zero, every time.",
                        ],
                        "why": r"""
The tail pointer is the whole trick. Without it, the only route to the end of a
singly linked list is a walk from the head, which is $O(n)$ — and the lab's step
counter exists to catch exactly that, since 1000 `push_back` calls must cost 0 steps.
Note what kind of claim this is: a true constant, not an amortised one. The dynamic
array's cheap append is a claim about a total; this is a claim about every individual
call, and the two are worth keeping apart, because only one of them can promise
anything about the call you are making right now.
""",
                    },
                    {
                        "q": "Both containers hold a million integers, and traversing either is $O(n)$. On real hardware the array is several times faster. Why?",
                        "opts": [
                            "Following a pointer is really $O(\\log n)$ once the chase through memory is counted",
                            "The array is walked by index arithmetic, while the list pays a pointer comparison and a branch at every node",
                            "One cache line brings in several neighbouring array elements; each list hop is its own trip",
                            "A list node carries a `next` field as well as its value, so the list moves more bytes",
                        ],
                        "a": 2,
                        "whys": [
                            r"Following a pointer is one step per node, exactly as advancing an index is. Both traversals are honestly $O(n)$; every bit of the gap lives in the constant that $O$ throws away.",
                            r"The instruction counts are within a small factor of each other, and a modern core retires several instructions per cycle. What it cannot do is issue a load whose *address* is not known until the previous load has returned — and a `next` chain is exactly that dependency, one link at a time.",
                            r"A cache line is 64 bytes: sixteen 32-bit integers arrive for the price of one miss.",
                            r"True, and it does cost — a node is typically three times the size of the value it holds. But bandwidth is not what binds here. A sequential scan of three times the bytes still beats a scattered scan of a third of them, because the sequential one is prefetched before it is asked for and the scattered one cannot be.",
                        ],
                        "why": r"""
Big-O throws away constants, and on modern hardware that constant is dominated by
memory locality. Reading one array element pulls in a whole cache line, which is the
next several elements for free; the nodes of a linked list were allocated at
different moments and can sit anywhere, so each `node.next` can be a fresh miss
costing a hundred-odd cycles — and, worse, a miss that cannot be started until the
previous one finished. This gap is why `list` in Python and `std::vector` in C++ are
the default containers, and why linked lists survive mostly where $O(1)$ splicing of
a node you already hold is the point.
""",
                    },
                    {
                        "q": "A program holds a long sequence, and repeatedly deletes the element it is currently looking at before moving on to the next. Which container does that favour?",
                        "opts": [
                            "The array, because removing at a known index is a single write",
                            "The linked list, because unhooking a node you already hold is $O(1)$",
                            "The linked list, because it can be indexed as cheaply as the array can",
                            "The array, because its removals amortise in the same way its appends do",
                        ],
                        "a": 1,
                        "whys": [
                            r"Removing from the middle of an array is not one write: everything after the hole slides down a slot. That is $O(n)$ per removal and $O(n^2)$ over the sequence, which is the cost this workload is built to expose.",
                            r"Two reference assignments, and not one element moves.",
                            r"It cannot be indexed cheaply — reaching index $i$ means following $i$ links. The premise is that you are *already holding* the node, which is what makes the splice free, and it is why an index would have spoiled it.",
                            r"Amortisation covers the resizing, not the shifting. A removal from the middle moves every later element whatever the growth policy is, and no capacity rule touches that.",
                        ],
                        "why": r"""
This is the workload the linked list exists for, and it is narrower than it first
looks. The splice is $O(1)$ only because the node is already in hand: `prev.next =
node.next` and the node is gone, with nothing after it disturbed. The moment the
question becomes "delete the element at index 400,000" the list loses, because
reaching that node costs the walk the array would have spent shifting.

So the rule is not "lists are good at deleting". It is that a list is good at
deleting *from a position you are already standing on* — which is what an iterator,
a cursor, or an LRU chain's node handle gives you. That is also why `list.remove(x)`
in Python is $O(n)$ and always will be: the search, not the removal, is the cost.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The growth and shrink rules, line by line",
                "minutes": 9,
                "lang": "python",
                "caption": "dynamic_array.py — five holes, and a counter that has to come out at 31",
                "brief": r"""
The whole amortised argument lives in four numbers: when to grow, by how much, when
to shrink, and by how much. Get any of them wrong and the container still *works* —
every test about values passes — while the write counter quietly goes quadratic.

Nothing runs here. Filled in correctly, sixteen appends from capacity 1 leave
`resizes` at 4 and `writes` at 31.
""",
                "listing": r'''
class DynamicArray:
    """capacity is the size of the backing store; _size is how much of it is live."""

    def append(self, value):
        if self._size == ___:
            self._resize(___)
        self._store[self._size] = value
        self.writes += 1
        self._size += 1

    def pop(self):
        if self._size == 0:
            raise IndexError("pop from an empty array")
        value = self._store[self._size - 1]
        self._store[self._size - 1] = None
        self._size -= 1
        if self.capacity > 1 and self._size * ___ <= self.capacity:
            self._resize(max(1, self.capacity // ___))
        return value

    def _resize(self, capacity):
        store = [None] * capacity
        for i in range(___):
            store[i] = self._store[i]
            self.writes += 1
        self._store = store
        self.capacity = capacity
        self.resizes += 1
''',
                "blanks": [
                    {
                        "prompt": "When has the backing store run out of room?",
                        "hole": "?",
                        "opts": ["self.writes", "len(self.to_list())", "self.capacity", "self.capacity - 1"],
                        "a": 2,
                        "why": "`_size` counts live elements and `capacity` counts slots, so the store is full exactly when the two meet — and not a moment before. This is the one comparison the whole doubling schedule hangs off.",
                        "whys": [
                            "`writes` is a diagnostic counter that only ever goes up, and it outruns `_size` as soon as a resize copies anything. Comparing the length against it fires on the first two appends, taking the capacity to 4, and then never again — so the fifth append writes off the end of the store and raises `IndexError`.",
                            "`to_list()` returns the live prefix, so its length *is* `_size`; the test becomes `_size == _size`, always true, and every single append resizes.",
                            "`_size` counts live elements and `capacity` counts slots, so the store is full exactly when the two meet — and not a moment before. This is the one comparison the whole doubling schedule hangs off.",
                            "This grows one append early and leaves the last slot of every store permanently unused. Sixteen appends would then cost 5 resizes rather than 4, and the `capacity == 16` check fails.",
                        ],
                    },
                    {
                        "prompt": "The new capacity to grow into.",
                        "hole": "?",
                        "opts": ["self.capacity * 2", "self.capacity + 1", "self.capacity + 100", "self._size"],
                        "a": 0,
                        "why": "Doubling is what makes the copies a geometric series: 1 + 2 + 4 + … stays below the number of appends that paid for it, so the amortised cost per append is a constant.",
                        "whys": [
                            "Doubling is what makes the copies a geometric series: 1 + 2 + 4 + … stays below the number of appends that paid for it, so the amortised cost per append is a constant.",
                            "One extra slot per growth means every append resizes and copies everything: $n$ appends cost about $n^2/2$ writes. A thousand appends would cost half a million.",
                            "A fixed increment of any size is still arithmetic growth, and still quadratic — 100 only moves the constant. A million appends would cost around five billion writes instead of two million.",
                            "At this point `_size` equals `capacity`, so this resizes the store to exactly the size it already was. The append then writes off the end of it.",
                        ],
                    },
                    {
                        "prompt": "The shrink trigger: this multiplier makes the test read *at most a quarter full*.",
                        "hole": "?",
                        "opts": ["2", "8", "0.25", "4"],
                        "a": 3,
                        "why": "A quarter full means `_size <= capacity / 4`, and multiplying out to `_size * 4 <= capacity` keeps it in integers. After the halving the array sits half full, with room to move in both directions.",
                        "whys": [
                            "This shrinks at half full, which leaves the array completely full straight afterwards. A push and a pop repeated on that boundary then resize on every operation — the thrashing the quarter rule exists to prevent.",
                            "This waits until an eighth. The amortised cost survives, but it lets the store grow to eight times the live size rather than four before releasing anything — twice the capacity held, and seven idle slots per live element instead of three — and the lab's check that an emptied array is back to capacity 1 fails outright: `_size * 8 <= capacity` stops firing at capacity 4 with one element left, so the final pop halves that to 2 and the array is stranded there.",
                            "Multiplying by a float makes the comparison true almost always — a full array of 8 gives `8 * 0.25 = 2.0 <= 8` — so the store halves after nearly every pop and the capacity collapses under the live data.",
                            "A quarter full means `_size <= capacity / 4`, and multiplying out to `_size * 4 <= capacity` keeps it in integers. After the halving the array sits half full, with room to move in both directions.",
                        ],
                    },
                    {
                        "prompt": "And the store shrinks by this divisor.",
                        "hole": "?",
                        "opts": ["1", "2", "4"],
                        "a": 1,
                        "why": "Halving mirrors the doubling, so the two triggers sit a factor of two apart and the array leaves a shrink half full rather than exactly full.",
                        "whys": [
                            "Integer division by 1 returns the same capacity, so the shrink condition stays true and every subsequent pop pays for a full copy that changes nothing.",
                            "Halving mirrors the doubling, so the two triggers sit a factor of two apart and the array leaves a shrink half full rather than exactly full.",
                            "Quartering lands the array exactly full at the moment it shrinks, so the next append doubles it back and the push/pop thrash returns by a different route.",
                        ],
                    },
                    {
                        "prompt": "How much of the old store is worth copying across?",
                        "hole": "?",
                        "opts": ["capacity", "len(self._store)", "self._size", "self.capacity"],
                        "a": 2,
                        "why": "Only the live prefix means anything; everything from `_size` onwards is rubbish left behind by earlier pops. Copying exactly `_size` values is also what makes the write count come out at 31 for sixteen appends.",
                        "whys": [
                            "`capacity` here is the parameter, the *new* size. When growing, that reads past the end of the old store; the values it copies do not exist.",
                            "This is the old capacity spelled a longer way, with the same failure: fine while growing, an `IndexError` the first time the array shrinks.",
                            "Only the live prefix means anything; everything from `_size` onwards is rubbish left behind by earlier pops. Copying exactly `_size` values is also what makes the write count come out at 31 for sixteen appends.",
                            "The old capacity is right when growing, because the store is full at that moment — but on a shrink it is twice the new store's length, and the copy raises `IndexError` on the first slot past the end.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Why doubling makes an append cost a constant",
                "minutes": 12,
                "vars": ["n", "k", "c", "W"],
                "brief": r"""
The array starts with one slot and doubles whenever it fills. Each doubling copies
every live element into the new store, which looks expensive — and on the append
that triggers it, it is. The claim is that it is cheap *on average*, and that claim
is a sum rather than an opinion. So count.

A **write** is one value put into a slot of the backing store: the $n$ appends
themselves, plus every copy made during a resize.
""",
                "steps": [
                    {
                        "prompt": "The store starts at capacity 1 and doubles on overflow. What is the capacity after $k$ doublings?",
                        "answer": "2^{k}",
                        "hint": "Each doubling multiplies by 2, and you started at 1.",
                        "deconstruct": [
                            "Capacity 1 becomes 2, then 4, then 8.",
                            "After $k$ of those, it is 2 multiplied by itself $k$ times.",
                        ],
                    },
                    {
                        "prompt": "A doubling copies the whole live prefix, which is exactly the old capacity: 1 element on the first doubling, 2 on the second, 4 on the third. Add up the copies made by all $k$ of them.",
                        "given": "$1 + 2 + 4 + \\dots + 2^{k-1}$",
                        "answer": "2^{k} - 1",
                        "hint": "A geometric series with ratio 2. In binary it is $k$ ones in a row, which is one less than a 1 followed by $k$ zeros.",
                        "deconstruct": [
                            "Write $S = 1 + 2 + \\dots + 2^{k-1}$ and double it: $2S = 2 + 4 + \\dots + 2^{k}$.",
                            "Subtract: $2S - S$ cancels everything but the ends, leaving $2^{k} - 1$.",
                        ],
                    },
                    {
                        "prompt": "Those $k$ doublings take the store to precisely the capacity you found, so $n = 2^{k}$ appends fill it exactly. Rewrite the copy total in terms of $n$.",
                        "answer": "n - 1",
                        "hint": "You have $2^{k} - 1$, and $n$ is another name for $2^{k}$.",
                        "deconstruct": [
                            "$n = 2^{k}$ by the substitution the prompt just made.",
                            "So $2^{k} - 1$ is $n - 1$: the copies alone cost slightly less than one per append.",
                        ],
                    },
                    {
                        "prompt": "Now add the appends themselves, one write each. What is the total write count $W$?",
                        "answer": "2n - 1",
                        "hint": "Copies plus stores: $(n - 1) + n$.",
                        "deconstruct": [
                            "The copies came to $n - 1$.",
                            "The stores are one per append, so $n$ more.",
                        ],
                    },
                    {
                        "prompt": "Divide by $n$ to get the amortised cost of a single append.",
                        "answer": "2 - \\frac{1}{n}",
                        "hint": "Divide both terms of $2n - 1$ by $n$ separately.",
                        "deconstruct": [
                            "$\\frac{2n}{n} = 2$.",
                            "$\\frac{1}{n}$ is what comes off it, and it shrinks as the array grows.",
                        ],
                    },
                    {
                        "prompt": "Now suppose the array grew by a fixed $c$ slots instead, starting at capacity $c$. There are $n/c - 1$ growths, copying $c$, then $2c$, and so on up to $n - c$. What is the total copy count?",
                        "given": "$c + 2c + 3c + \\dots + (n - c)$",
                        "answer": "\\frac{n(n-c)}{2c}",
                        "hint": "An arithmetic series is the number of terms times the average of the first and last. There are $n/c - 1$ terms, and the first and last average to $n/2$.",
                        "deconstruct": [
                            "The terms run $c, 2c, \\dots, (n-c)$, so there are $n/c - 1$ of them.",
                            "First plus last over two is $(c + n - c)/2 = n/2$.",
                            "Multiply the count by the average.",
                        ],
                    },
                ],
                "closing": r"""
$2 - 1/n$ writes per append: under 2, and falling towards it. That is what "$O(1)$
amortised" means here — not that no append is ever expensive, because one in every
$n$ of them copies the entire array, but that the expensive ones are rare in exactly
the proportion that pays for them.

Set the two totals side by side for a million appends. Doubling: about two million
writes. Growing by $c = 100$: $n(n-c)/(2c)$ is about five *billion*. The difference
is not a constant factor you can optimise away later; it is the difference between a
container that scales and one that does not, and it comes down entirely to whether
the growth is multiplicative or additive.
""",
            },
            "lab": [{
                "title": "A growable array and a linked list, counted",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Two containers, each keeping a public counter so the checks can see how much
work you actually did.

## `DynamicArray(capacity=1)`

A fixed Python list is the *backing store* — treat it as raw memory. Keep
`self.capacity`, the private size, `self.writes` and `self.resizes`.

Count **one write for every value you put into a slot of the backing store**,
including the copies made while resizing. Clearing a vacated slot does not
count.

- `__len__`, `to_list()`
- `__getitem__` / `__setitem__` — negative indices count from the end, and
  anything out of range raises `IndexError`
- `append(value)` — when the store is full, resize to twice the capacity first
- `pop()` — remove and return the last value; `IndexError` when empty. After
  removing, if the capacity is above 1 and the array is at most a quarter full,
  resize down to half the capacity
- `insert(index, value)` — shift the tail up by one; an index equal to the
  length is allowed (that is an append)

`ValueError` for a capacity below 1.

Starting from capacity 1, sixteen appends must cost exactly **4 resizes and 31
writes** — sixteen values plus the 1 + 2 + 4 + 8 copies.

## `SinglyLinkedList(values=None)`

Nodes are `ListNode(value, next)`. Keep `self.head`, `self.tail` and
`self.steps`, where a step is one node visited by a traversal.

- `__len__`, `__iter__` (yields values), `to_list()`
- `push_front(value)`, `push_back(value)` — **both O(1)**, so neither may walk
  the list; that is what the tail pointer is for
- `pop_front()` — return the removed value; `IndexError` when empty
- `find(value)` — the index of the first match or `-1`, adding one step per
  node examined
- `reverse()` — in place, one step per node, leaving `head` and `tail` correct

```text
lst = SinglyLinkedList(range(100))
lst.steps = 0
lst.find(99)   -> 99, having taken exactly 100 steps
```
''',
                "files": [{"name": "main.py", "content": r'''
class DynamicArray:
    """A growable array over a fixed backing store."""

    def __init__(self, capacity=1):
        # your code here
        pass

    def __len__(self):
        # your code here
        return 0

    def __getitem__(self, index):
        # your code here
        pass

    def __setitem__(self, index, value):
        # your code here
        pass

    def append(self, value):
        """Add to the end, doubling the capacity when the store is full."""
        # your code here

    def pop(self):
        """Remove and return the last value; halve the capacity at a quarter full."""
        # your code here

    def insert(self, index, value):
        """Shift the tail up and drop value in at index."""
        # your code here

    def to_list(self):
        """The live elements as a plain list."""
        # your code here


class ListNode:
    """One cell of a singly linked list."""

    def __init__(self, value, next=None):
        self.value = value
        self.next = next


class SinglyLinkedList:
    """A singly linked list with a tail pointer and a traversal counter."""

    def __init__(self, values=None):
        # your code here
        pass

    def __len__(self):
        # your code here
        return 0

    def __iter__(self):
        # your code here
        return iter(())

    def push_front(self, value):
        """O(1) insertion at the head."""
        # your code here

    def push_back(self, value):
        """O(1) insertion at the tail — no walking."""
        # your code here

    def pop_front(self):
        """Remove and return the head value."""
        # your code here

    def find(self, value):
        """Index of the first match, or -1. One step per node examined."""
        # your code here

    def reverse(self):
        """Reverse in place, fixing head and tail."""
        # your code here

    def to_list(self):
        """The values as a plain list."""
        # your code here


array = DynamicArray()
for value in range(16):
    array.append(value)
print(array.capacity, array.resizes, array.writes)
print(SinglyLinkedList([1, 2, 3]).to_list())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class DynamicArray:
    """A growable array over a fixed backing store."""

    def __init__(self, capacity=1):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self.writes = 0
        self.resizes = 0
        self._size = 0
        self._store = [None] * capacity

    def __len__(self):
        return self._size

    def _slot(self, index):
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")
        return index

    def __getitem__(self, index):
        return self._store[self._slot(index)]

    def __setitem__(self, index, value):
        self._store[self._slot(index)] = value
        self.writes += 1

    def _resize(self, capacity):
        store = [None] * capacity
        for i in range(self._size):
            store[i] = self._store[i]
            self.writes += 1
        self._store = store
        self.capacity = capacity
        self.resizes += 1

    def append(self, value):
        """Add to the end, doubling the capacity when the store is full."""
        if self._size == self.capacity:
            self._resize(self.capacity * 2)
        self._store[self._size] = value
        self.writes += 1
        self._size += 1

    def pop(self):
        """Remove and return the last value; halve the capacity at a quarter full."""
        if self._size == 0:
            raise IndexError("pop from an empty array")
        value = self._store[self._size - 1]
        self._store[self._size - 1] = None
        self._size -= 1
        if self.capacity > 1 and self._size * 4 <= self.capacity:
            self._resize(max(1, self.capacity // 2))
        return value

    def insert(self, index, value):
        """Shift the tail up and drop value in at index."""
        if index < 0:
            index += self._size
        if index < 0 or index > self._size:
            raise IndexError("index out of range")
        if self._size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self._size, index, -1):
            self._store[i] = self._store[i - 1]
            self.writes += 1
        self._store[index] = value
        self.writes += 1
        self._size += 1

    def to_list(self):
        """The live elements as a plain list."""
        return [self._store[i] for i in range(self._size)]


class ListNode:
    """One cell of a singly linked list."""

    def __init__(self, value, next=None):
        self.value = value
        self.next = next


class SinglyLinkedList:
    """A singly linked list with a tail pointer and a traversal counter."""

    def __init__(self, values=None):
        self.head = None
        self.tail = None
        self.steps = 0
        self._size = 0
        for value in values or []:
            self.push_back(value)

    def __len__(self):
        return self._size

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def push_front(self, value):
        """O(1) insertion at the head."""
        self.head = ListNode(value, self.head)
        if self.tail is None:
            self.tail = self.head
        self._size += 1

    def push_back(self, value):
        """O(1) insertion at the tail — no walking."""
        node = ListNode(value)
        if self.tail is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def pop_front(self):
        """Remove and return the head value."""
        if self.head is None:
            raise IndexError("pop from an empty list")
        node = self.head
        self.head = node.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return node.value

    def find(self, value):
        """Index of the first match, or -1. One step per node examined."""
        node = self.head
        index = 0
        while node is not None:
            self.steps += 1
            if node.value == value:
                return index
            node = node.next
            index += 1
        return -1

    def reverse(self):
        """Reverse in place, fixing head and tail."""
        previous = None
        node = self.head
        self.tail = self.head
        while node is not None:
            self.steps += 1
            following = node.next
            node.next = previous
            previous = node
            node = following
        self.head = previous

    def to_list(self):
        """The values as a plain list."""
        return list(self)


array = DynamicArray()
for value in range(16):
    array.append(value)
print(array.capacity, array.resizes, array.writes)
print(SinglyLinkedList([1, 2, 3]).to_list())
'''}],
                "hints": [
                    "Keep the backing store and the length apart: `self._store` may be far longer than `len(self)`, and everything outside the live prefix is rubbish.",
                    "Put the resize logic in one private `_resize(new_capacity)` that copies the live prefix and bumps both counters — `append`, `pop` and `insert` should all call it rather than reimplementing it.",
                    "`insert` shifts from the far end backwards: `for i in range(self._size, index, -1): store[i] = store[i - 1]`. Going forwards would smear one value over the tail.",
                    "`push_back` is only O(1) if `self.tail` is always right — remember to set it when pushing to the front of an empty list, and when `pop_front` empties the list.",
                ],
                "tests": [
                    {"name": "Indexing, including from the end", "code": r'''
_a = DynamicArray()
assert len(_a) == 0, f"a fresh array has length 0, got {len(_a)}"
for _v in [10, 20, 30]:
    _a.append(_v)
assert _a.to_list() == [10, 20, 30], f"to_list gave {_a.to_list()!r}"
assert _a[0] == 10 and _a[2] == 30, "forward indexing"
assert _a[-1] == 30 and _a[-3] == 10, f"negative indexing gave {_a[-1]!r} for [-1]"
_a[1] = 99
assert _a.to_list() == [10, 99, 30], f"__setitem__ gave {_a.to_list()!r}"
for _bad in (3, -4, 100):
    try:
        _a[_bad]
        assert False, f"index {_bad} should raise IndexError"
    except IndexError:
        pass
try:
    DynamicArray(0)
    assert False, "capacity 0 should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The doubling schedule is exactly right", "code": r'''
_a = DynamicArray()
assert _a.capacity == 1, f"the default capacity is 1, got {_a.capacity!r}"
for _v in range(16):
    _a.append(_v)
assert _a.capacity == 16, f"after 16 appends the capacity is 16, got {_a.capacity!r}"
assert _a.resizes == 4, f"16 appends need 4 resizes (1->2->4->8->16), got {_a.resizes!r}"
assert _a.writes == 31, f"16 appends cost 16 stores + 15 copies = 31 writes, got {_a.writes!r}"
assert _a.to_list() == list(range(16)), "the values must survive every resize"
'''},
                    {"name": "Appending is O(1) amortised", "code": r'''
_a = DynamicArray()
for _v in range(1000):
    _a.append(_v)
assert _a.writes == 2023, f"1000 appends cost 1000 + 1023 copies = 2023 writes, got {_a.writes!r}"
assert _a.writes < 3 * 1000, "the whole point of doubling is that total work stays below 3n"
assert _a.capacity == 1024 and len(_a) == 1000, \
    f"expected capacity 1024 and length 1000, got {_a.capacity!r} and {len(_a)}"
'''},
                    {"name": "pop shrinks at a quarter full", "code": r'''
_a = DynamicArray()
for _v in range(16):
    _a.append(_v)
assert _a.pop() == 15, "pop returns the last value"
for _ in range(11):
    _a.pop()
assert len(_a) == 4, f"expected 4 left, got {len(_a)}"
assert _a.capacity == 8, f"at a quarter full the capacity halves to 8, got {_a.capacity!r}"
while len(_a):
    _a.pop()
assert _a.capacity == 1, f"emptied out, the capacity should be back to 1, got {_a.capacity!r}"
assert _a.to_list() == [], "an emptied array holds nothing"
try:
    _a.pop()
    assert False, "popping an empty array should raise IndexError"
except IndexError:
    pass
'''},
                    {"name": "insert shifts the tail", "code": r'''
_a = DynamicArray()
for _v in [1, 2, 3]:
    _a.append(_v)
_a.insert(0, 0)
assert _a.to_list() == [0, 1, 2, 3], f"insert at the front gave {_a.to_list()!r}"
_a.insert(len(_a), 4)
assert _a.to_list() == [0, 1, 2, 3, 4], f"insert at the end gave {_a.to_list()!r}"
_a.insert(2, 99)
assert _a.to_list() == [0, 1, 99, 2, 3, 4], f"insert in the middle gave {_a.to_list()!r}"
try:
    _a.insert(99, 0)
    assert False, "insert beyond the end should raise IndexError"
except IndexError:
    pass
_b = DynamicArray()
_b.insert(0, "only")
assert _b.to_list() == ["only"], "inserting into an empty array must work"
'''},
                    {"name": "Linked list basics", "code": r'''
_l = SinglyLinkedList()
assert len(_l) == 0 and _l.to_list() == [], "a fresh list is empty"
try:
    _l.pop_front()
    assert False, "pop_front on an empty list should raise IndexError"
except IndexError:
    pass
_l.push_back(2)
_l.push_back(3)
_l.push_front(1)
assert _l.to_list() == [1, 2, 3], f"to_list gave {_l.to_list()!r}"
assert list(_l) == [1, 2, 3], "__iter__ should yield the values"
assert len(_l) == 3, f"length is {len(_l)}, expected 3"
assert _l.pop_front() == 1, "pop_front returns the head value"
assert _l.to_list() == [2, 3] and len(_l) == 2, f"after pop_front: {_l.to_list()!r}"
_l.pop_front()
_l.pop_front()
_l.push_back("again")
assert _l.to_list() == ["again"], "the tail pointer must survive the list emptying"
assert SinglyLinkedList(range(4)).to_list() == [0, 1, 2, 3], "the constructor takes an iterable"
'''},
                    {"name": "push_back never walks the list", "code": r'''
_l = SinglyLinkedList()
for _v in range(1000):
    _l.push_back(_v)
assert _l.steps == 0, \
    f"1000 push_backs took {_l.steps} steps — keep a tail pointer instead of walking"
for _v in range(1000):
    _l.push_front(_v)
assert _l.steps == 0, f"push_front took {_l.steps} steps and should take none"
'''},
                    {"name": "find pays for every node it passes", "code": r'''
_l = SinglyLinkedList(range(100))
_l.steps = 0
assert _l.find(99) == 99, f"find(99) gave {_l.find(99)!r}"
assert _l.steps == 100, f"finding the last of 100 nodes costs 100 steps, got {_l.steps}"
_l.steps = 0
assert _l.find(0) == 0, "the head is found immediately"
assert _l.steps == 1, f"finding the head costs 1 step, got {_l.steps}"
_l.steps = 0
assert _l.find("absent") == -1, "a missing value gives -1"
assert _l.steps == 100, f"a failed search still walks the whole list, got {_l.steps}"
'''},
                    {"name": "reverse fixes both ends", "code": r'''
_l = SinglyLinkedList([1, 2, 3, 4])
_l.steps = 0
_l.reverse()
assert _l.to_list() == [4, 3, 2, 1], f"reverse gave {_l.to_list()!r}"
assert _l.steps == 4, f"reversing 4 nodes costs 4 steps, got {_l.steps}"
assert _l.head.value == 4 and _l.tail.value == 1, \
    f"head/tail are {_l.head.value!r}/{_l.tail.value!r}, expected 4/1"
_l.push_back(0)
assert _l.to_list() == [4, 3, 2, 1, 0], "pushing after a reverse must still use the tail"
_e = SinglyLinkedList()
_e.reverse()
assert _e.to_list() == [] and _e.head is None and _e.tail is None, \
    "reversing an empty list must not break it"
_one = SinglyLinkedList([7])
_one.reverse()
assert _one.to_list() == [7] and _one.head is _one.tail, "a single node is its own head and tail"
'''},
                ],
            }, {
                "title": "Binary search, with its reads counted",
                "runtime": "python",
                "minutes": 16,
                "brief": r'''
The counterpart to the traversal you counted in the lab above. `find` on the
linked list took 100 steps to reach the 100th node, because a reference is the
only way forward. A sorted array in contiguous slots can be read at any index for
the same price as any other, and that one property turns a search of a hundred
thousand values into seventeen reads.

## `binary_search(items, target)`

Return the index of `target` in the **sorted** list `items`, or `-1` when it is
absent.

Keep two indices, `low` and `high`, bounding the window still worth searching, and
read only the element in the middle of it:

- equal to `target` — return that index
- smaller than `target` — every index from `low` to `mid` is too small, so
  `low = mid + 1`
- larger than `target` — `high = mid - 1`

The loop runs while `low <= high`. When they cross, the window is empty and the
value is not there.

```text
binary_search([1, 3, 5, 7, 9, 11], 7)   ->  3
binary_search([1, 3, 5, 7, 9, 11], 4)   ->  -1
binary_search([], 7)                    ->  -1
```

Write it as a loop; no recursion is needed here.

One check hands the function an object holding a hundred thousand values that
counts every element read and refuses any index that is not an integer. A scan
reads tens of thousands; halving reads 17, and the check allows 25. Anything that
walks the sequence — `in`, `.index()`, a `for` over `items`, or a slice — fails
it.
''',
                "files": [{"name": "main.py", "content": r'''
def binary_search(items, target):
    """Return the index of target in the sorted list, or -1."""
    low = 0
    high = len(items) - 1
    # your code here
    return -1


print(binary_search([1, 3, 5, 7, 9, 11], 7))    # 3
print(binary_search([1, 3, 5, 7, 9, 11], 4))    # -1
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def binary_search(items, target):
    """Return the index of target in the sorted list, or -1."""
    low = 0
    high = len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        value = items[mid]
        if value == target:
            return mid
        if value < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


print(binary_search([1, 3, 5, 7, 9, 11], 7))    # 3
print(binary_search([1, 3, 5, 7, 9, 11], 4))    # -1
'''}],
                "hints": [
                    "The loop condition is `while low <= high`, and the middle is "
                    "`mid = (low + high) // 2`.",
                    "`items[mid] < target` means the answer is to the right of mid, so "
                    "`low = mid + 1`; too large means `high = mid - 1`. Moving past mid "
                    "rather than to it is what makes the window shrink every time.",
                    "Read `items[mid]` and nothing else — `in`, `.index()`, a loop over "
                    "`items` or a slice all read the whole sequence and fail the count.",
                ],
                "tests": [
                    {"name": "Finds every present value", "code": r'''
_xs = [1, 3, 5, 7, 9, 11]
assert [binary_search(_xs, v) for v in _xs] == [0, 1, 2, 3, 4, 5], \
    f"each value should map to its own index, got {[binary_search(_xs, v) for v in _xs]!r}"
'''},
                    {"name": "Absent values give -1", "code": r'''
assert binary_search([1, 3, 5], 4) == -1, "4 is not in the list"
assert binary_search([], 7) == -1, "the empty list has nothing in it"
assert binary_search([5], 4) == -1 and binary_search([5], 5) == 0, \
    "a single-element list is still a window"
'''},
                    {"name": "Handles the ends of a big list", "code": r'''
_big = list(range(0, 200000, 2))
assert binary_search(_big, 0) == 0, "the first element"
assert binary_search(_big, 199998) == 99999, "the last element"
assert binary_search(_big, 3) == -1, "the odd numbers are absent"
'''},
                    {"name": "Reads a logarithmic number of elements", "code": r'''
class _Probe:
    """A sorted sequence of 0, 2, 4, ... that counts what is read from it."""

    def __init__(self, n):
        self.n = n
        self.reads = 0

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        if not isinstance(i, int):
            raise TypeError("index must be an int — slicing reads the whole window")
        if i < 0 or i >= self.n:
            raise IndexError(i)
        self.reads += 1
        return i * 2


_p = _Probe(100000)
assert binary_search(_p, 135790) == 67895, \
    "the probe holds 0, 2, 4, ... so 135790 sits at index 67895"
assert _p.reads <= 25, \
    f"read {_p.reads} elements of 100000 — halve the window each time round, which is about 17"
'''},
                ],
            }],
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Stacks, queues and monotonic windows",
            "summary": "LIFO for parsing, FIFO from two stacks, and a deque that keeps a window's maximum.",
            "concepts": [
                "A stack is the natural memory for anything nested — expressions, calls, brackets",
                "Reverse Polish notation removes the need for precedence and parentheses",
                "Dijkstra's shunting-yard algorithm converts infix to RPN in one pass",
                "Associativity decides whether an equal-precedence operator pops before pushing",
                "A FIFO queue from two stacks is O(1) amortised — the same aggregate argument as doubling",
                "A monotonic deque holds only the candidates that can still become the answer",
                "Each index enters and leaves the deque once, so a sliding-window maximum is O(n), not O(nk)",
            ],
            "read": [
                {
                    "title": "Nesting, order, and the window that never looks back",
                    "minutes": 14,
                    "body": r'''
Open a source file in any editor and type an unmatched bracket: the editor notices at
once, and it notices with almost no memory. It does not remember the whole file. It
remembers the brackets that are still open, and the rule that the next closing bracket
must match the *most recently opened* one — `( [ ) ]` is wrong not because the counts
are off but because the `)` arrived while `[` was still the newest thing waiting.

That memory — the newest thing waiting comes out first — is a **stack**. Push on the way
in, pop on the way out, and the order reverses itself without anyone arranging it.
Bracket matching is the smallest program that needs one:

```python
PAIRS = {")": "(", "]": "[", "}": "{"}


def balanced(text):
    """True when every closing bracket matches the most recently opened one."""
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack


for text in ["(a + b) * [c]", "([)]", "((", "f(x[1])"]:
    print(f"{text:<14} {balanced(text)}")
```

Everything nested is a stack in disguise: brackets, function calls, the parts of an
arithmetic expression you have to set aside while you deal with something that binds
tighter. This module builds three things on that idea, then one thing on the opposite
idea — a queue, where the *oldest* thing waiting comes out first — and ends with a
structure that is both at once.

## Reverse Polish, and why a calculator wants it

Read `3 + 4 * 2` aloud. You cannot apply the `+` when you meet it, because its right
operand has not arrived, and when `4` arrives you still cannot, because a `*` is waiting
behind it that binds tighter. Infix notation forces the reader to hold operators in
suspense and to consult a table of precedences before releasing them. Hewlett-Packard
built calculators that refused to do any of that: you typed `3 4 2 * +`, operands first
and operator afterwards, and the machine needed neither brackets nor a precedence table.
That is **reverse Polish notation**, and an evaluator for it is a stack and a loop:

```python
OPERATORS = {"+", "-", "*", "/"}


def evaluate_rpn(tokens):
    """Evaluate postfix tokens, printing the stack after each one."""
    stack = []
    for token in tokens:
        if token in OPERATORS:
            right = stack.pop()
            left = stack.pop()
            if token == "+":
                stack.append(left + right)
            elif token == "-":
                stack.append(left - right)
            elif token == "*":
                stack.append(left * right)
            else:
                quotient = abs(left) // abs(right)
                stack.append(-quotient if (left < 0) != (right < 0) else quotient)
        else:
            stack.append(int(token))
        print(f"{token:>3}  {stack}")
    return stack[0]


print(evaluate_rpn("3 4 + 2 *".split()))
print(evaluate_rpn("-7 2 /".split()))
```

Every operand is pushed. Every operator pops two values, combines them, and pushes the
result. An expression is well formed when exactly one value is left at the end, and the
first trace ends on 14 with the stack holding nothing else.

The trace shows where the one real mistake lives. When `-` arrives on `[3, 4]`, the
first pop returns `4` and the second returns `3`: the stack hands the operands back in
the *reverse* of the order they were written, so the value popped first is the **right**
operand. Get this backwards and `+` and `*` pass every test while `-`, `/` and `^` are
silently reversed — a test suite made only of commutative operators would sign it off,
which is why the lab checks `3 4 -` and `-7 2 /` by name.

The second trace shows a smaller trap. C, Java and most calculators truncate integer
division *towards zero*, so $-7 / 2$ is $-3$. Python's `//` rounds *down*, so `-7 // 2`
is `-4`. To get the C answer, divide the absolute values and put the sign back
afterwards: the result is negative exactly when one operand is negative and the other is
not, which is what the `!=` between the two sign tests computes.

## Spending the parentheses

If RPN is so much easier to evaluate, the work has to have gone somewhere: into the
conversion from infix. Dijkstra's **shunting-yard** algorithm does it in one pass with
one stack, and the picture he had in mind was a railway siding. Operands go straight
through to the output track. Operators are shunted onto a siding, and the only question
is when an operator on the siding is allowed back out.

Derive the rule from what postfix means. In the output, an operator must come *after*
both of its operands. When a new operator arrives — say `*` in `3 + 4 * 2` — the `+` on
the siding already has its left operand out (`3`) and would take `4` as its right operand
if it came out now. Should it? Only if it binds at least as tightly as the newcomer. It
does not, so it waits, and the `4` ends up belonging to `*`. When the input is
exhausted, whatever is on the siding comes out in stack order.

That leaves one case the precedence table cannot settle: two operators of *equal*
precedence, like the two `-` in `3 - 4 - 5`. Left-associative operators group from the
left, $(3 - 4) - 5$, so the first `-` must come out before the second goes on. `^` is
right-associative, $2^{(3^{2})}$, so the first `^` must *stay* on the siding when the
second arrives. So the pop condition reads: pop while the operator on top binds strictly
tighter, *or* binds equally tightly and the incoming operator is left-associative.

```python
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
RIGHT_ASSOCIATIVE = {"^"}


def shunting_yard(tokens):
    """Infix tokens to postfix tokens, the parentheses spent along the way."""
    output, operators = [], []
    for token in tokens:
        if token in PRECEDENCE:
            while operators and operators[-1] != "(":
                top = operators[-1]
                tighter = PRECEDENCE[top] > PRECEDENCE[token]
                equal_and_left = (PRECEDENCE[top] == PRECEDENCE[token]
                                  and token not in RIGHT_ASSOCIATIVE)
                if tighter or equal_and_left:
                    output.append(operators.pop())
                else:
                    break
            operators.append(token)
        elif token == "(":
            operators.append(token)
        elif token == ")":
            while operators[-1] != "(":
                output.append(operators.pop())
            operators.pop()
        else:
            output.append(token)
    while operators:
        output.append(operators.pop())
    return output


for expression in ["3 + 4 * 2", "( 3 + 4 ) * 2", "3 - 4 - 5", "2 ^ 3 ^ 2"]:
    print(f"{expression:<14} -> {' '.join(shunting_yard(expression.split()))}")
```

Notice what happened to the parentheses in `( 3 + 4 ) * 2`: they are gone, and the
meaning survived, because an operator in postfix takes the two values immediately before
it and there is only one way to read that. The brackets were not discarded; they were
spent, converting a notation whose meaning depends on a table into one whose meaning
depends on nothing but order.

## A queue from two stacks

Now the opposite discipline: first in, first out. A queue over a plain Python list is
easy to write and quietly $O(n)$ per dequeue, because `pop(0)` shifts every remaining
element down a slot. There is a cleaner way, and it is the amortised argument from the
sequences module in new clothes.

Keep two stacks, an **inbox** and an **outbox**. Enqueue pushes onto the inbox. Dequeue
pops from the outbox — and when the outbox is empty, tip the whole inbox into it first,
one pop and one push at a time. The tip reverses the order exactly once, which is what
turns two last-in-first-out piles into one first-in-first-out line.

```python
class CountingQueue:
    """A FIFO from two stacks, counting every push and pop on either."""

    def __init__(self):
        self.inbox, self.outbox = [], []
        self.operations = 0

    def enqueue(self, value):
        self.inbox.append(value)
        self.operations += 1

    def dequeue(self):
        if not self.outbox:                    # only onto an EMPTY outbox
            while self.inbox:
                self.outbox.append(self.inbox.pop())
                self.operations += 2
        self.operations += 1
        return self.outbox.pop()


queue = CountingQueue()
for value in range(1000):
    queue.enqueue(value)
first = queue.dequeue()
after_first = queue.operations
rest = [queue.dequeue() for _ in range(999)]
print("first out:", first, "| operations by then:", after_first)
print("the rest in order:", rest == list(range(1, 1000)),
      "| total operations:", queue.operations)
```

The first dequeue is spectacular: 3001 operations by the time it returns, because it
moved a thousand elements in one call. But look at the total. Each value is pushed onto
the inbox, popped off it during the one tip, pushed onto the outbox, and popped off
that — four operations in its whole life and never a fifth, because nothing is ever
tipped back. So $n$ enqueues and $n$ dequeues cost $4n$ operations however they are
interleaved, which is 2 per call: $O(1)$ amortised, with one call in the run being
$O(n)$.

The bug people write here is tipping the inbox whenever it has something in it, rather
than only when the outbox is *empty*. It looks more eager and it breaks the queue: newer
values land on top of older ones still waiting in the outbox, and come out first. The
tip is safe precisely because it only ever happens onto an empty outbox.

## The window that never looks back

Here is a problem where the right structure is neither a stack nor a queue but both at
once. A weather station reports, every day, the highest temperature over the last seven
days. With $n$ readings and a window of $k$, the loop that recomputes each window from
scratch is $O(nk)$ — fine for a week, ruinous when someone asks for the last hundred
thousand samples of a sensor.

Think about what a window's maximum can *be*. Suppose the readings so far include a 3
followed later by a 5. The 3 can never again be the answer to anything: every future
window that contains the 3 also contains the 5, which is both larger and younger, and
the 5 will still be there after the 3 has aged out. So the 3 is dead the moment the 5
arrives. Apply that to every reading and what survives is a list of candidates that is
*decreasing* from oldest to youngest — each one larger than everything that came after
it, or it would have been killed.

That list needs both ends. New candidates enter at the back, after killing every smaller
candidate ahead of them; the front is the current maximum, and it leaves from the front
when it ages out of the window. Two ends, so a **deque**, and it holds *indices* rather
than values because ageing out is a question about position, not size:

```python
from collections import deque


def sliding_window_max(values, k):
    """The maximum of every width-k window, with the deque shown at each step."""
    window, out = deque(), []
    for index, value in enumerate(values):
        while window and values[window[-1]] <= value:
            window.pop()                        # beaten by a younger, larger value
        window.append(index)
        if window[0] <= index - k:
            window.popleft()                    # the front has aged out
        if index >= k - 1:
            out.append(values[window[0]])
        held = [values[i] for i in window]
        print(f"see {value:>2}: deque holds {held}, reported {out[-1] if out else '-'}")
    return out


print(sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
```

Two eviction rules, and it is worth seeing that they do different jobs. The loop at the
back drops candidates the newcomer has beaten — note the `<=`, so an equal value also
dies, since the younger twin outlives it and reports the same maximum. The check at the
front drops an index that has fallen outside the window: the window ending at `index`
covers `index - k + 1` through `index`, so anything at `index - k` or earlier has left.
Between them, the front is always the largest value still inside the window, and the
answer for the example is `[3, 3, 5, 5, 6, 7]`.

And now the cost. A single step can pop many indices — a long falling run followed by
one big value empties the deque in one go — so no step is $O(1)$ in the worst case. But
an index has to be appended before it can be popped, and it is appended exactly once. So
over the whole run there are at most $n$ appends and $n$ pops, whatever $k$ is: the
total is $O(n)$, and $k$ has vanished from it. That is the aggregate argument for the
third time in one module.

## Where it stops holding

The deque trick works because the window only moves forward and the question is
monotone — a maximum, or a minimum by flipping the comparison, but not a median or an
average, for which nothing is ever safely dead. It also assumes $1 \le k \le n$; a window
wider than the sequence has no full windows at all, and the lab treats that as an error
rather than an empty answer. Shunting-yard as written handles binary operators only:
unary minus, function calls with several arguments and operators of mixed arity all need
extra token kinds, and the one-pass simplicity gets more expensive with each. The
two-stack queue's amortised bound holds for any interleaving, but it is a bound on the
total; a system with a latency budget for a single call cannot use it, and would reach
for a ring buffer instead.

## What you are about to build

The lab is *An expression evaluator and a sliding-window maximum*, and it is the four
pieces above in order. `Stack` is the plain list wrapper; `Queue` is the two-stack
version, and its test enqueues after a dequeue to catch a tip made at the wrong moment.
`evaluate_rpn` is checked on `3 4 -` and `-7 2 /`, which is where the operand order and
the truncating division show, and it must raise `ValueError` for an unknown token, too
few operands, or more than one value left at the end. `shunting_yard` is checked on the
two pairs that isolate associativity — `2 ^ 3 ^ 2` and `3 - 4 - 5` — and on unbalanced
parentheses. And `sliding_window_max` is compared against the brute-force loop on sixty
random cases and then run on 60,000 values with $k = 500$, where an $O(nk)$ solution
makes thirty million comparisons and the deque makes on the order of a hundred thousand.
The numeric unit counts the queue's 4000 operations out exactly, and the
fill-in-the-blanks unit walks the deque's five holes; the trace above is the same code
with a print in it.
''',
                },
            ],
            "quiz": {
                "title": "Nesting, order, and why the window is linear",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why does a monotonic deque bring the sliding-window maximum down to $O(n)$ when the obvious nested loop is $O(nk)$?",
                        "opts": [
                            "The deque keeps the window sorted, which costs $O(k\\log k)$ but only once at the start",
                            "Every index is appended once and removed at most once, so deque work is under $2n$",
                            "`deque` indexes in $O(1)$, so the maximum can be read without scanning the window",
                            "Each step does $O(1)$ work, because the evictions per step are bounded by a constant",
                        ],
                        "a": 1,
                        "whys": [
                            r"Nothing is ever sorted. The deque is *kept* decreasing by refusing to admit anything that would break the order, which costs nothing beyond the comparison already being made — and a sort done once at the start would have to be redone as soon as the window moved.",
                            r"An index has to be appended before it can be popped, and it is appended exactly once.",
                            r"It does index in $O(1)$ — and so does the brute-force loop, which is still $O(nk)$. The saving is not in *reading* the maximum; it is in never re-examining an element that a later, larger one has already beaten.",
                            r"No such bound exists. On a strictly decreasing prefix followed by one large value, a single step pops the entire deque — $k-1$ indices at once. That is exactly why the argument has to be aggregate: no individual step is $O(1)$, and the bound survives anyway.",
                        ],
                        "why": r"""
This is the aggregate argument again, in a new costume. A single step can pop many
indices, so no step is $O(1)$ in the worst case — but an index has to be appended
before it can be popped, and it is appended exactly once, so across the whole run
there are at most $n$ appends and $n$ removals, whatever $k$ is. That total is what
$O(n)$ is a statement about. An algorithm whose cost genuinely depends on $k$ is what
falls over on the day someone passes $k = 100{,}000$; this one does not notice.
""",
                    },
                    {
                        "q": "An index is dropped from the back of the deque when its value is not greater than the incoming value. Why is that safe?",
                        "opts": [
                            "Duplicate values cannot survive in one window, so the dropped index was redundant",
                            "The dropped index has already aged out of the window at the front",
                            "The newcomer is both larger and younger, so it outlives the dropped index",
                            "The dropped index can still be a maximum, but only of windows already reported",
                        ],
                        "a": 2,
                        "whys": [
                            r"Duplicates are perfectly possible, and they are precisely why the comparison is written `<=` rather than `<`. Two equal values inside one window is an ordinary case, not an impossible one.",
                            r"Ageing out is a separate check, made at the *front* of the deque against `index - k`. This eviction happens at the back, and the index being dropped is still comfortably inside the window.",
                            r"Two conditions, and both hold: at least as large, and arriving later.",
                            r"Half right, and it is the half that carries no weight. Windows already reported are indeed settled — but the dropped index is still *inside* the current window, so the claim being made is about the future. What licenses it is the newcomer's youth, not the report's age.",
                        ],
                        "why": r"""
Two conditions have to hold together, and both do: the newcomer is at least as large,
so it beats the older element on value; and it arrived later, so it stays inside the
window for at least as long. Any future window containing the older index also
contains the newer one, and the newer one wins — so the older index can never be the
answer to anything again, and is discarded without a second thought. Note that only
one of the two conditions is about the values. Drop the youth half and the argument
collapses, which is why the eviction is written at the back, where the newcomer's
arrival order is what is being used.
""",
                    },
                    {
                        "q": "A FIFO queue built from two stacks. What does a single `dequeue` cost?",
                        "opts": [
                            "$O(1)$ worst case: a dequeue moves at most one element between the stacks",
                            "$O(n)$ always: the inbox has to be tipped across on every single dequeue",
                            "$O(1)$ amortised: many can move at once, but each element crosses once",
                            "$O(\\log n)$: the tip-over halves the work left for the dequeues that follow",
                        ],
                        "a": 2,
                        "whys": [
                            r"A dequeue that arrives with 1000 elements in the inbox genuinely moves all 1000, so no worst-case constant exists. That is what makes this an amortised claim rather than a worst-case one — and the distinction matters to anyone with a latency budget for a single call.",
                            r"The tip fires only when the outbox is *empty*. After one tip of 1000 elements, the next 999 dequeues pop one element each and never touch the inbox at all.",
                            r"Pushed to the inbox, popped from it, pushed to the outbox, popped from it: four operations in an element's whole life.",
                            r"Nothing here is halved, and nothing is ordered by comparison, so there is no logarithm available. The tip moves the *whole* inbox, not half of it — and having moved it, moves nothing again.",
                        ],
                        "why": r"""
The tip-over is the expensive event and it is genuinely $O(n)$ when it happens: a
dequeue that arrives with 1000 elements in the inbox moves all 1000. What rescues the
bound is that those elements are now in the outbox and never go back — each element
crosses from inbox to outbox exactly once in its whole life, so $n$ dequeues cost
$O(n)$ in total. That is the identical argument to the doubling array, on completely
different machinery, and the numeric unit in this module counts it out exactly rather
than bounding it.
""",
                    },
                    {
                        "q": "Shunting-yard turns `2 ^ 3 ^ 2` into `2 3 2 ^ ^`, but `3 - 4 - 5` into `3 4 - 5 -`. What accounts for the difference?",
                        "opts": [
                            "`^` outranks `-`, so two equal-precedence operators never meet on the stack",
                            "`^` is right associative, so an equal `^` is left on the stack; `-` is left associative",
                            "Unary minus is folded in first, which reorders the subtractions but not the powers",
                            "The stack pops only on strictly greater precedence, and `^` is the only operator above `-`",
                        ],
                        "a": 1,
                        "whys": [
                            r"Precedence is real and `^` does outrank `-`. But in both of these expressions the two operators being compared are *equal* to each other, so precedence cannot separate the cases — something else has to.",
                            r"Pop while the top binds strictly tighter, *or* binds equally tightly and the incoming operator is left associative.",
                            r"There is no unary minus in `3 - 4 - 5`: all three operands are positive and both signs are binary. Unary minus is a genuine complication in shunting-yard, but it is not the one on this page.",
                            r"This is the pop rule with its second clause missing — and that clause is the whole answer. Drop it and `3 - 4 - 5` converts to `3 4 5 - -`, which evaluates to $3-(4-5) = 4$ instead of $-6$.",
                        ],
                        "why": r"""
The pop condition is the only place associativity shows up: pop while the operator on
top binds *strictly tighter*, or binds equally tightly *and the incoming operator is
left associative*. Two `^` tokens are equally tight and `^` is right associative, so
nothing is popped, both sit on the stack, and they come off in reverse — giving
$2^{(3^2)} = 512$ rather than $(2^3)^2 = 64$. Two `-` tokens are equally tight and
`-` is left associative, so the first is popped before the second is pushed, giving
$(3-4)-5 = -6$. The two expressions are structurally identical and differ in one
property of one operator, which is what makes the pair worth staring at.
""",
                    },
                    {
                        "q": "`evaluate_rpn(\"3 4 -\".split())` must give $-1$. Which popped value is the left operand?",
                        "opts": [
                            "The one popped first, since it is nearest the operator in the token stream",
                            "Either one: `-` is applied to the pair, and the evaluator normalises the order",
                            "The one popped second, since a stack returns operands in reverse of push order",
                            "Neither: the evaluator must track the order separately, as a stack does not keep it",
                        ],
                        "a": 2,
                        "whys": [
                            r"Nearest the operator in the *stream* is nearest the *top* of the stack — and the top is the right operand. The two orderings are exact opposites, which is why this is the slip that silently reverses every non-commutative operator while leaving `+` and `*` looking perfect.",
                            r"There is nothing to normalise: `left - right` and `right - left` differ by a sign, and no evaluator can pick between them without already knowing which is which. `+` and `*` would survive this; `-`, `/` and `^` would not.",
                            r"`3` is pushed, then `4`. The top is `4`, the right operand; underneath it is `3`, the left.",
                            r"A stack keeps the order perfectly — last in, first out, with no ambiguity anywhere. That single order is exactly the information needed, which is why RPN evaluation wants one stack and nothing else.",
                        ],
                        "why": r"""
`3` is pushed, then `4`. The top of the stack is therefore `4`, which is the *right*
operand, and the value underneath it is `3`, the left. So the pops come out
right-then-left and the operator has to be applied as `left - right`. Get it the
wrong way round and `+` and `*` still pass every test while `-`, `/` and `^` are all
silently reversed — which is why the lab checks `3 4 -` and `-7 2 /` specifically.
A test suite made only of commutative operators would have signed this off.
""",
                    },
                    {
                        "q": "`shunting_yard` emits no parentheses at all, whatever the input contained. How can the RPN still mean the same thing?",
                        "opts": [
                            "Parentheses only ever affect readability, so dropping them cannot change a value",
                            "The order of the operators alone already fixes which operands each one takes",
                            "They are re-inserted by `evaluate_rpn` when it meets an ambiguous precedence",
                            "The algorithm rejects any input whose meaning depends on its parentheses",
                        ],
                        "whys": [
                            r"They affect values constantly: `(2 + 3) * 4` is 20 and `2 + 3 * 4` is 14. What is true is that once the grouping has been *resolved*, there is nothing left for a bracket to say.",
                            r"An operator in RPN takes the two values immediately before it, and there is only one way to read that.",
                            r"`evaluate_rpn` never looks at precedence at all — a stack and a loop is the whole of it, which is exactly the appeal. All the precedence work happened once, in `shunting_yard`.",
                            r"It rejects nothing. `(2 + 3) * 4` and `2 + 3 * 4` are both perfectly good input; they convert to `2 3 + 4 *` and `2 3 4 * +`, which is precisely how the difference in meaning survives the loss of the brackets.",
                        ],
                        "a": 1,
                        "why": r"""
Infix needs parentheses because the same string of tokens can be grouped more than
one way, and precedence rules are a convention for choosing between the readings.
RPN has no such ambiguity to resolve: an operator takes the two values immediately
before it, full stop, so the grouping is carried by position rather than by
punctuation.

That is what shunting-yard is *for*. It is not discarding the parentheses, it is
spending them — converting a representation whose meaning depends on a table of
precedences into one whose meaning depends on nothing but order. Which is why
`evaluate_rpn` is thirty lines and needs no table at all, and why compilers and
calculators have been doing this since 1961.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The monotonic deque, hole by hole",
                "minutes": 9,
                "lang": "python",
                "caption": "sliding_window.py — five holes between $O(n)$ and wrong answers",
                "brief": r"""
The deque holds **indices**, not values, front to back in decreasing order of the
value each index points at. Every line below is doing one of four jobs: evict what
can never win again, admit the newcomer, evict what has aged out, and read the
answer. Filling it in wrongly mostly does not crash — it quietly returns the wrong
maximum for some windows and the right one for others.

Nothing runs here. Correctly filled, `sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)`
returns `[3, 3, 5, 5, 6, 7]`.
""",
                "listing": r'''
from collections import deque


def sliding_window_max(values, k):
    """Maximum of every width-k window, in O(n) total."""
    window = deque()          # indices, front to back in decreasing value order
    out = []
    for index, value in enumerate(values):
        while window and values[___] <= value:
            window.___()                      # evict from the back
        window.append(index)
        if window[0] <= index ___:            # the front has aged out
            window.popleft()
        if index >= ___:                      # the first full window exists
            out.append(values[window[___]])
    return out
''',
                "blanks": [
                    {
                        "prompt": "Which index is compared against the newcomer?",
                        "hole": "?",
                        "opts": ["index", "window[-1]", "window[0]", "index - 1"],
                        "a": 1,
                        "why": "The back of the deque holds the smallest surviving candidate, and it is the one the newcomer can knock out. Working from the back is what keeps the deque decreasing.",
                        "whys": [
                            "This compares the incoming value with itself, which is never strictly greater, so the loop never runs and the deque grows without bound — every index stays in it and the front never changes after the first element.",
                            "The back of the deque holds the smallest surviving candidate, and it is the one the newcomer can knock out. Working from the back is what keeps the deque decreasing.",
                            "The front holds the current maximum. Comparing against it and popping from the back would evict candidates on the strength of an element that is not being evicted, and the deque stops being ordered.",
                            "The previous index may well have been evicted already, so reading `values` at it says nothing about what is still in the deque. It also ignores the whole run of smaller candidates behind it.",
                        ],
                    },
                    {
                        "prompt": "…and it comes off which end?",
                        "hole": "?",
                        "opts": ["popleft", "clear", "appendleft", "pop"],
                        "a": 3,
                        "why": "`pop` takes from the back, which is where the beaten candidate is. Each index is appended once and popped at most once, and that pairing is the whole $O(n)$ argument.",
                        "whys": [
                            "`popleft` throws away the front — the current maximum — while the loop condition keeps looking at the back, so the loop can spin discarding the answer and leave the deque unordered.",
                            "Clearing drops every surviving candidate, including ones still inside the window that are larger than the newcomer. The result is the maximum of a suffix, not of the window.",
                            "This adds instead of removing, so the loop condition never stops being true and the deque grows until memory runs out.",
                            "`pop` takes from the back, which is where the beaten candidate is. Each index is appended once and popped at most once, and that pairing is the whole $O(n)$ argument.",
                        ],
                    },
                    {
                        "prompt": "The front index is stale when it is this far behind.",
                        "hole": "?",
                        "opts": ["- k", "- k + 1", "- 1", "+ k"],
                        "a": 0,
                        "why": "The window ending at `index` covers `index - k + 1` up to `index`, so the oldest index still inside it is `index - k + 1`. Anything at `index - k` or earlier has left, which is exactly the test written here.",
                        "whys": [
                            "The window ending at `index` covers `index - k + 1` up to `index`, so the oldest index still inside it is `index - k + 1`. Anything at `index - k` or earlier has left, which is exactly the test written here.",
                            "This evicts the oldest index that is still legitimately inside the window. The answer is then the maximum of a window of width $k-1$, which is right whenever the true maximum is not the oldest element and wrong when it is.",
                            "This throws away the front on every step where it is not the newest index, so the deque never holds more than one candidate and the result is just `values` shifted along.",
                            "The front index is never ahead of the current one, so `window[0] <= index + k` is true on every single step and the front is thrown away every time — the opposite of aging out. The newcomer appended a line earlier is often the only index there, so the deque is left empty and `values[window[0]]` raises `IndexError` on the first full window.",
                        ],
                    },
                    {
                        "prompt": "The first full window is complete when `index` reaches…",
                        "hole": "?",
                        "opts": ["k + 1", "0", "k - 1", "k"],
                        "a": 2,
                        "why": "Indices are counted from 0, so the window of width $k$ starting at 0 ends at $k-1$. That is the first step at which there is anything to report, and it gives exactly $n - k + 1$ outputs.",
                        "whys": [
                            "Two short at the start, for the same reason, and the lab's length check on 60000 elements fails immediately.",
                            "This reports from the very first element, so the early outputs are maxima of partial windows of width 1, 2, 3 and so on rather than of width $k$.",
                            "Indices are counted from 0, so the window of width $k$ starting at 0 ends at $k-1$. That is the first step at which there is anything to report, and it gives exactly $n - k + 1$ outputs.",
                            "An off-by-one that skips the very first window: the output is one short, and `sliding_window_max([4, 2, 9], 3)` returns `[]` rather than `[9]`.",
                        ],
                    },
                    {
                        "prompt": "Where the answer for this window is read from.",
                        "hole": "?",
                        "opts": ["1", "0", "-1"],
                        "a": 1,
                        "why": "The deque is kept decreasing, so the front is the largest value still in the window — and the eviction step above has already made sure the front is inside it.",
                        "whys": [
                            "The second-largest candidate, when there is one — and an `IndexError` the moment the deque holds a single index, which happens on any strictly increasing stretch of the input, where each newcomer evicts every survivor behind it.",
                            "The deque is kept decreasing, so the front is the largest value still in the window — and the eviction step above has already made sure the front is inside it.",
                            "The back is the *smallest* surviving candidate, usually the newest element. This returns something close to `values` itself and only agrees with the answer when the window happens to end on its maximum.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "The bill for a thousand in and a thousand out",
                "minutes": 7,
                "brief": r"""
The two-stack queue is the cleanest amortised argument in the course, because you can
count it exactly rather than bound it. One dequeue in this run is spectacularly
expensive; the total is not.
""",
                "prompt": "How many `push` and `pop` calls happen on the two inner stacks in total?",
                "note": "Count only `push` and `pop`, on either stack. `is_empty` and `__len__` are free.",
                "figure": r"""
`enqueue` pushes onto the **inbox**. `dequeue` pops from the **outbox** — and when
the outbox is empty it is refilled first, by tipping the inbox across one element at
a time: one `pop` from the inbox and one `push` onto the outbox for each. That single
tip reverses the order exactly once, which is what turns two LIFOs into a FIFO.
""",
                "given": [
                    {"label": "Enqueues", "value": "1000"},
                    {"label": "Dequeues", "value": "1000"},
                    {"label": "Order", "value": "all 1000 enqueues, then all 1000 dequeues"},
                    {"label": "Counted", "value": "`push` and `pop` on the inbox and the outbox"},
                ],
                "answer": 4000,
                "tol": 0.5,
                "unit": "operations",
                "aside": "One of those dequeues moves a thousand elements by itself. An amortised bound is a claim about the total, never about the worst single call.",
                "hint": "Follow one value from the instant it is enqueued to the instant it is returned, and count every stack operation it takes part in. Then multiply.",
                "wrong": "2000 counts one push and one pop per value, as though there were a single stack. Each value passes through two of them.",
                "why": r"""
Each value is pushed onto the inbox, popped off the inbox during the one tip-over,
pushed onto the outbox, and finally popped off the outbox: four operations, and never
a fifth, because nothing is ever tipped back. $1000 \times 4 = 4000$.

Spread over the 2000 calls the caller made, that is 2 stack operations per call —
constant, which is the entire claim. And it does not depend on the ordering: however
the enqueues and dequeues are interleaved, each value still crosses each stack exactly
once, so the total is $4n$ for any interleaving at all.
""",
            },
            "lab": {
                "title": "An expression evaluator and a sliding-window maximum",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
## `Stack`

`push(value)`, `pop()`, `peek()`, `is_empty()`, `__len__`. `pop` and `peek` on
an empty stack raise `IndexError`.

## `Queue`

FIFO built from **two stacks**, nothing else — an inbox that takes pushes and
an outbox that serves pops. When the outbox runs dry, tip the whole inbox into
it, which reverses the order exactly once. `enqueue`, `dequeue`, `peek`,
`is_empty`, `__len__`; `IndexError` on an empty dequeue or peek.

## `evaluate_rpn(tokens)`

`tokens` is a list of strings in postfix order. Operands are integers, possibly
negative. Operators are `+ - * / ^`.

- `/` truncates **towards zero**, so `-7 / 2` is `-3`, not `-4`
- `/` by zero raises `ZeroDivisionError`
- `^` is integer exponentiation; a negative exponent is a `ValueError`
- an unknown token, too few operands, or more than one value left at the end
  are all `ValueError`

```text
evaluate_rpn("3 4 + 2 *".split())            -> 14
evaluate_rpn("5 1 2 + 4 * + 3 -".split())    -> 14
evaluate_rpn("-7 2 /".split())               -> -3
```

## `shunting_yard(tokens)`

Infix tokens (already split, with `(` and `)` as their own tokens) to a postfix
token list. Precedence: `^` above `* /` above `+ -`. `^` is **right**
associative, everything else is left associative. Unbalanced parentheses and
unknown tokens raise `ValueError`.

```text
shunting_yard("3 + 4 * 2".split())      ->  ["3", "4", "2", "*", "+"]
shunting_yard("( 1 + 2 ) * 3".split())  ->  ["1", "2", "+", "3", "*"]
shunting_yard("2 ^ 3 ^ 2".split())      ->  ["2", "3", "2", "^", "^"]
shunting_yard("3 - 4 - 5".split())      ->  ["3", "4", "-", "5", "-"]
```

## `sliding_window_max(values, k)`

The maximum of every window of width `k`, left to right, in **O(n) total** —
the obvious nested loop is O(nk) and will not do.

Hold *indices* in a deque, front to back in decreasing value order. For each new
element, drop every index at the back whose value cannot beat it (they are now
younger and smaller, so they are dead), push the new index, drop the front if it
has fallen out of the window, and once the first full window exists read the
answer off the front.

`ValueError` when `k < 1` or `k` is wider than the sequence.

```text
sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)  ->  [3, 3, 5, 5, 6, 7]
```
''',
                "files": [{"name": "main.py", "content": r'''
from collections import deque

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
RIGHT_ASSOCIATIVE = {"^"}


class Stack:
    """LIFO over a Python list."""

    def __init__(self):
        # your code here
        pass

    def __len__(self):
        # your code here
        return 0

    def is_empty(self):
        # your code here
        pass

    def push(self, value):
        # your code here
        pass

    def pop(self):
        """Remove and return the top; IndexError when empty."""
        # your code here

    def peek(self):
        """The top, left in place; IndexError when empty."""
        # your code here


class Queue:
    """FIFO built from two stacks."""

    def __init__(self):
        # your code here
        pass

    def __len__(self):
        # your code here
        return 0

    def is_empty(self):
        # your code here
        pass

    def enqueue(self, value):
        # your code here
        pass

    def dequeue(self):
        """Remove and return the oldest value; IndexError when empty."""
        # your code here

    def peek(self):
        """The oldest value, left in place; IndexError when empty."""
        # your code here


def evaluate_rpn(tokens):
    """Evaluate a postfix token list."""
    # your code here


def shunting_yard(tokens):
    """Infix tokens to postfix tokens."""
    # your code here


def sliding_window_max(values, k):
    """The maximum of every width-k window, in O(n)."""
    # your code here


print(evaluate_rpn("3 4 + 2 *".split()))
print(shunting_yard("3 + 4 * 2".split()))
print(sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
from collections import deque

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
RIGHT_ASSOCIATIVE = {"^"}


class Stack:
    """LIFO over a Python list."""

    def __init__(self):
        self._items = []

    def __len__(self):
        return len(self._items)

    def is_empty(self):
        return not self._items

    def push(self, value):
        self._items.append(value)

    def pop(self):
        """Remove and return the top; IndexError when empty."""
        if not self._items:
            raise IndexError("pop from an empty stack")
        return self._items.pop()

    def peek(self):
        """The top, left in place; IndexError when empty."""
        if not self._items:
            raise IndexError("peek at an empty stack")
        return self._items[-1]


class Queue:
    """FIFO built from two stacks."""

    def __init__(self):
        self._inbox = Stack()
        self._outbox = Stack()

    def __len__(self):
        return len(self._inbox) + len(self._outbox)

    def is_empty(self):
        return len(self) == 0

    def enqueue(self, value):
        self._inbox.push(value)

    def _shift(self):
        if self._outbox.is_empty():
            if self._inbox.is_empty():
                raise IndexError("the queue is empty")
            while not self._inbox.is_empty():
                self._outbox.push(self._inbox.pop())

    def dequeue(self):
        """Remove and return the oldest value; IndexError when empty."""
        self._shift()
        return self._outbox.pop()

    def peek(self):
        """The oldest value, left in place; IndexError when empty."""
        self._shift()
        return self._outbox.peek()


def _as_number(token):
    """The integer a token denotes, or ValueError if it denotes nothing."""
    try:
        return int(token)
    except (TypeError, ValueError):
        raise ValueError(f"unknown token {token!r}")


def _apply(operator, left, right):
    """One binary operation with C-style truncating division."""
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        quotient = abs(left) // abs(right)
        return -quotient if (left < 0) != (right < 0) else quotient
    if right < 0:
        raise ValueError("negative exponents are not integers")
    return left ** right


def evaluate_rpn(tokens):
    """Evaluate a postfix token list."""
    stack = Stack()
    for token in tokens:
        if token in PRECEDENCE:
            if len(stack) < 2:
                raise ValueError(f"not enough operands for {token!r}")
            right = stack.pop()
            left = stack.pop()
            stack.push(_apply(token, left, right))
        else:
            stack.push(_as_number(token))
    if len(stack) != 1:
        raise ValueError(f"expected one value at the end, {len(stack)} left")
    return stack.pop()


def shunting_yard(tokens):
    """Infix tokens to postfix tokens."""
    output = []
    operators = Stack()
    for token in tokens:
        if token in PRECEDENCE:
            while not operators.is_empty() and operators.peek() != "(":
                top = operators.peek()
                if (PRECEDENCE[top] > PRECEDENCE[token]
                        or (PRECEDENCE[top] == PRECEDENCE[token]
                            and token not in RIGHT_ASSOCIATIVE)):
                    output.append(operators.pop())
                else:
                    break
            operators.push(token)
        elif token == "(":
            operators.push(token)
        elif token == ")":
            while not operators.is_empty() and operators.peek() != "(":
                output.append(operators.pop())
            if operators.is_empty():
                raise ValueError("unbalanced parentheses")
            operators.pop()
        else:
            _as_number(token)
            output.append(token)
    while not operators.is_empty():
        top = operators.pop()
        if top == "(":
            raise ValueError("unbalanced parentheses")
        output.append(top)
    return output


def sliding_window_max(values, k):
    """The maximum of every width-k window, in O(n)."""
    if k < 1:
        raise ValueError("the window must hold at least one element")
    if k > len(values):
        raise ValueError("the window is wider than the sequence")
    window = deque()
    out = []
    for index, value in enumerate(values):
        while window and values[window[-1]] <= value:
            window.pop()
        window.append(index)
        if window[0] <= index - k:
            window.popleft()
        if index >= k - 1:
            out.append(values[window[0]])
    return out


print(evaluate_rpn("3 4 + 2 *".split()))
print(shunting_yard("3 + 4 * 2".split()))
print(sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
'''}],
                "hints": [
                    "In `evaluate_rpn` the *second* value you pop is the left operand — `3 4 -` is 3 minus 4, not 4 minus 3.",
                    "Truncating division: compute `abs(left) // abs(right)` and negate it when exactly one operand is negative.",
                    "The shunting-yard pop condition is 'the operator on top binds at least as tightly' — strictly tighter, or equally tight when the incoming operator is left associative.",
                    "In the sliding window, store indices rather than values; that is the only way to know when the front has aged out of the window.",
                ],
                "tests": [
                    {"name": "Stack, including the empty cases", "code": r'''
_s = Stack()
assert len(_s) == 0 and _s.is_empty(), "a fresh stack is empty"
for _m in ("pop", "peek"):
    try:
        getattr(_s, _m)()
        assert False, f"{_m} on an empty stack should raise IndexError"
    except IndexError:
        pass
_s.push(1)
_s.push(2)
assert len(_s) == 2 and not _s.is_empty(), f"length is {len(_s)}, expected 2"
assert _s.peek() == 2 and len(_s) == 2, "peek must leave the top in place"
assert _s.pop() == 2 and _s.pop() == 1, "a stack serves last in, first out"
assert _s.is_empty(), "both values were popped"
'''},
                    {"name": "Queue from two stacks keeps FIFO order", "code": r'''
_q = Queue()
assert _q.is_empty() and len(_q) == 0, "a fresh queue is empty"
for _m in ("dequeue", "peek"):
    try:
        getattr(_q, _m)()
        assert False, f"{_m} on an empty queue should raise IndexError"
    except IndexError:
        pass
for _v in [1, 2, 3]:
    _q.enqueue(_v)
assert _q.peek() == 1, f"peek gave {_q.peek()!r}, expected the oldest value 1"
assert _q.dequeue() == 1, "first in, first out"
_q.enqueue(4)
assert [_q.dequeue() for _ in range(3)] == [2, 3, 4], \
    "values enqueued after a dequeue must still come out last"
assert _q.is_empty() and len(_q) == 0, "the queue is drained"
_q.enqueue(5)
assert _q.dequeue() == 5, "the queue must be reusable after emptying"
'''},
                    {"name": "RPN evaluation", "code": r'''
for _expr, _want in [("3 4 + 2 *", 14), ("5 1 2 + 4 * + 3 -", 14), ("42", 42),
                     ("-7 2 /", -3), ("7 -2 /", -3), ("7 2 /", 3), ("-8 2 /", -4),
                     ("2 3 ^", 8), ("2 3 ^ 2 ^", 64), ("3 4 -", -1)]:
    _got = evaluate_rpn(_expr.split())
    assert _got == _want, f"evaluate_rpn({_expr!r}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "RPN rejects malformed input", "code": r'''
for _expr in ["3 +", "+", "3 4", "", "3 4 &", "3 x +"]:
    try:
        evaluate_rpn(_expr.split())
        assert False, f"evaluate_rpn({_expr!r}) should raise ValueError"
    except ValueError:
        pass
try:
    evaluate_rpn("1 0 /".split())
    assert False, "dividing by zero should raise ZeroDivisionError"
except ZeroDivisionError:
    pass
try:
    evaluate_rpn("2 -1 ^".split())
    assert False, "a negative exponent should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Shunting-yard precedence and associativity", "code": r'''
for _expr, _want in [
        ("3 + 4 * 2", ["3", "4", "2", "*", "+"]),
        ("( 1 + 2 ) * 3", ["1", "2", "+", "3", "*"]),
        ("2 ^ 3 ^ 2", ["2", "3", "2", "^", "^"]),
        ("3 - 4 - 5", ["3", "4", "-", "5", "-"]),
        ("3 + 4 * 2 / ( 1 - 5 )", ["3", "4", "2", "*", "1", "5", "-", "/", "+"]),
        ("7", ["7"])]:
    _got = shunting_yard(_expr.split())
    assert _got == _want, f"shunting_yard({_expr!r}) gave {_got!r}, expected {_want!r}"
for _bad in ["( 1 + 2", "1 + 2 )", "( )3"]:
    try:
        shunting_yard(_bad.split())
        assert False, f"shunting_yard({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Infix through RPN gives the right number", "code": r'''
for _expr, _want in [("3 + 4 * 2", 11), ("( 3 + 4 ) * 2", 14), ("2 ^ 3 ^ 2", 512),
                     ("100 / 3", 33), ("10 - 2 - 3", 5), ("( 8 - 20 ) / 5", -2)]:
    _got = evaluate_rpn(shunting_yard(_expr.split()))
    assert _got == _want, f"{_expr} evaluated to {_got!r}, expected {_want}"
'''},
                    {"name": "Sliding-window maximum", "code": r'''
_got = sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)
assert _got == [3, 3, 5, 5, 6, 7], f"Got {_got!r}, expected [3, 3, 5, 5, 6, 7]"
assert sliding_window_max([4, 2, 9], 1) == [4, 2, 9], "a width-1 window is the sequence itself"
assert sliding_window_max([4, 2, 9], 3) == [9], "one window as wide as the sequence"
assert sliding_window_max([5, 5, 5, 5], 2) == [5, 5, 5], "equal values must not confuse the deque"
assert sliding_window_max([-3, -1, -7], 2) == [-1, -1], "negatives work the same way"
for _bad in [([1, 2, 3], 0), ([1, 2, 3], 4), ([], 1), ([1], -1)]:
    try:
        sliding_window_max(*_bad)
        assert False, f"sliding_window_max{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "It agrees with brute force, and stays linear", "code": r'''
import random as _random
_rng = _random.Random(7)
for _trial in range(60):
    _n = _rng.randint(1, 30)
    _values = [_rng.randint(-20, 20) for _ in range(_n)]
    _k = _rng.randint(1, _n)
    _want = [max(_values[_i:_i + _k]) for _i in range(_n - _k + 1)]
    _got = sliding_window_max(_values, _k)
    assert _got == _want, f"values={_values!r} k={_k} gave {_got!r}, expected {_want!r}"
_big = [_rng.randint(0, 10 ** 6) for _ in range(60000)]
_out = sliding_window_max(_big, 500)
assert len(_out) == len(_big) - 499, f"expected {len(_big) - 499} windows, got {len(_out)}"
assert _out[0] == max(_big[:500]), "the first window is still wrong"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Binary search trees",
            "summary": "Ordered storage with insert, all three deletion cases, traversal and height.",
            "concepts": [
                "The BST invariant: everything left is smaller, everything right is larger",
                "Search, insert and delete all cost O(h), so the height is the whole story",
                "In-order traversal of a BST yields the keys in sorted order — for free",
                "Pre-order records the shape; post-order is the order you may safely free nodes in",
                "Deletion splits into three cases: leaf, one child, and two children",
                "The two-child case promotes the in-order successor, the leftmost node of the right subtree",
                "Random insertion gives height ~3 log2 n and average depth ~1.39 log2 n; sorted insertion gives a linked list",
            ],
            "read": [
                {
                    "title": "The invariant, the descent, and what deletion has to put back",
                    "minutes": 14,
                    "body": r'''
Somebody thinks of a number between 1 and 1000, and you find it in ten guesses. Each
guess is the middle of the range still possible, and each answer — higher or lower —
throws away half of what is left. Ten halvings of a thousand reach one. That is binary
search, and a sorted array supports it perfectly, right up to the moment somebody wants
to *insert* a value: everything after the insertion point has to slide one slot along,
which is $O(n)$, and a sequence that is searched a million times and updated a million
times has lost the argument.

A **binary search tree** is the guessing game with its decisions frozen into
references. Each node holds a key. Everything smaller hangs somewhere off its left
reference, everything larger somewhere off its right, and a search descends from the
root making one comparison per level, turning left or right, and stops when it finds
the key or runs out of tree. Insertion is the same descent, ending by hanging a new node
in the empty slot the search fell out of. No sliding, no shifting; the cost of both is
the number of levels walked.

## The invariant, stated the way that catches bugs

Here is the tree the lab uses as its worked example, built by inserting 50, 30, 70, 20,
40, 60, 80 in that order:

```text
            50
        30      70
      20  40  60  80
```

The rule that makes it a search tree is easy to state wrongly. It is *not* "each node
is larger than its left child and smaller than its right child". It is: every key in
the **whole left subtree** is smaller than the node, and every key in the **whole right
subtree** is larger. The difference only shows two levels down, which is exactly where
it hides:

```text
        20
       /  \
     10    30
       \
        25
```

Every parent–child pair here is correctly ordered, and the tree is broken. A search for
25 compares with 20, goes right, compares with 30, goes left, and falls off the tree:
the key is in there and unreachable. A checker that compares neighbours signs this tree
off. The checker that catches it carries an interval down the recursion — everything
under the left reference of 20 must be below 20, everything under the right reference
of 10 must be between 10 and the 20 above it — and narrows the interval at every step:

```python
class TreeNode:
    """One node: a key and two references."""

    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right


def locally_ordered(node):
    """Every parent against its own two children — the check that is not enough."""
    if node is None:
        return True
    if node.left is not None and not node.left.key < node.key:
        return False
    if node.right is not None and not node.right.key > node.key:
        return False
    return locally_ordered(node.left) and locally_ordered(node.right)


def is_bst(node, low=None, high=None):
    """Every key against the interval its ancestors confine it to."""
    if node is None:
        return True
    if low is not None and node.key <= low:
        return False
    if high is not None and node.key >= high:
        return False
    return is_bst(node.left, low, node.key) and is_bst(node.right, node.key, high)


def contains(node, key):
    while node is not None:
        if key == node.key:
            return True
        node = node.left if key < node.key else node.right
    return False


suspect = TreeNode(20, TreeNode(10, right=TreeNode(25)), TreeNode(30))
print("locally ordered:", locally_ordered(suspect))
print("really a BST:   ", is_bst(suspect))
print("contains(25):   ", contains(suspect, 25))
```

Locally ordered, not a search tree, and 25 is lost. The lab's final test runs that
interval check after 250 random deletions, because a deletion that leaves the tree
locally ordered and globally wrong is the failure this structure actually has.

## Insert, and the three traversals

Insertion walks the same path a search would and stops at the first empty reference.
The lab asks you to write it **iteratively**, and there is a reason that is not taste:
the deepest trees come from sorted input, and a recursive insert on sorted input uses
one stack frame per level.

```python
class TreeNode:
    """One node: a key and two references."""

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def insert(root, key):
    """Descend until the slot the key belongs in is empty; return the root."""
    if root is None:
        return TreeNode(key)
    node = root
    while True:
        if key == node.key:
            return root                       # already present: nothing to do
        if key < node.key:
            if node.left is None:
                node.left = TreeNode(key)
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = TreeNode(key)
                return root
            node = node.right


def walk(node, order, out):
    """Collect keys in pre-, in- or post-order."""
    if node is None:
        return out
    if order == "pre":
        out.append(node.key)
    walk(node.left, order, out)
    if order == "in":
        out.append(node.key)
    walk(node.right, order, out)
    if order == "post":
        out.append(node.key)
    return out


root = None
for key in [50, 30, 70, 20, 40, 60, 80]:
    root = insert(root, key)
for order in ("pre", "in", "post"):
    print(f"{order:>4}-order: {walk(root, order, [])}")
```

Three traversals, and each is the same three lines in a different order. The middle one
is the important one: in-order traversal of a binary search tree produces the keys
*sorted*, `[20, 30, 40, 50, 60, 70, 80]`. That is not something the traversal computes.
It is the invariant read out loud — left subtree, then this node, then right subtree is
*smaller keys, this key, larger keys*, applied recursively all the way down — and it is
the strongest test there is for whether a tree is still a search tree after you have
been modifying it. Pre-order visits each node before its subtrees, which records the
*shape*: feed `[50, 30, 20, 40, 70, 60, 80]` back through `insert` and you rebuild the
identical tree, which is why the lab checks shape with it. Post-order visits a node only
after both subtrees are finished, which is the one safe order in which to free nodes in
a language where you free them yourself — every other order reads a pointer out of a
node it has already released.

## Height is the whole story

Search, insert and delete all cost one comparison per level, so all three are $O(h)$
where $h$ is the height, the number of edges on the longest root-to-leaf path. That
looks like a reassurance and is a warning, because $h$ is not a function of $n$. It is a
function of the order the keys arrived in.

```python
import random


class TreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def insert(root, key):
    if root is None:
        return TreeNode(key)
    node = root
    while True:
        if key < node.key:
            if node.left is None:
                node.left = TreeNode(key)
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = TreeNode(key)
                return root
            node = node.right


def height(root):
    """Edges on the longest downward path, measured without recursion."""
    best, stack = -1, ([(root, 0)] if root is not None else [])
    while stack:
        node, depth = stack.pop()
        best = max(best, depth)
        for child in (node.left, node.right):
            if child is not None:
                stack.append((child, depth + 1))
    return best


def build(keys):
    root = None
    for key in keys:
        root = insert(root, key)
    return root


keys = list(range(1000))
print("sorted insertion, height:  ", height(build(keys)))
random.Random(7).shuffle(keys)
print("shuffled insertion, height:", height(build(keys)))
```

The same thousand keys. Sorted, each key is larger than everything present, so every
insert walks the entire right spine and hangs off the bottom: a linked list wearing
tree-shaped types, height 999, and `contains(999)` costs a thousand comparisons.
Shuffled, the height is 24. Some forty times shallower, settled by nothing but arrival
order — and sorted arrival is not exotic. It is what happens when the keys come from a
file or a database that returned them sorted.

The lower end is pure counting. A perfect tree of height $h$ has $1$ node at depth 0,
$2$ at depth 1, $4$ at depth 2, and $2^{h}$ at the bottom, so it holds

$$n = 1 + 2 + 4 + \dots + 2^{h} = 2^{h+1} - 1$$

nodes, which rearranges to $h = \log_2(n + 1) - 1$: a million keys need at least 19
levels, and 999,999 is what sorted insertion gives them. Random insertion sits much
closer to the good end than the bad — the average node lands at depth about
$1.39 \log_2 n$ and the height at roughly $3 \log_2 n$ — but nothing in an unbalanced
tree *enforces* that. Which is the whole reason balanced trees exist, and the reason the
lab shuffles before building.

The recursion-depth point, made concrete:

```python
# raises RecursionError
class TreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def insert_recursively(node, key):
    """The textbook version: one stack frame per level of the descent."""
    if node is None:
        return TreeNode(key)
    if key < node.key:
        node.left = insert_recursively(node.left, key)
    else:
        node.right = insert_recursively(node.right, key)
    return node


root = None
for key in range(3000):          # sorted input: a chain 3000 deep
    root = insert_recursively(root, key)
```

Three thousand sorted keys, three thousand frames deep, and Python gives up around the
thousandth. The iterative version walks the same 3000 nodes and uses one frame.

## Deletion, in three cases

Insertion never disturbs an existing node. Deletion has to remove one and leave the
invariant standing, and how hard that is depends on how many children the node has.

A **leaf** is unhooked: the parent's reference to it becomes `None`. A node with **one
child** is spliced out: the parent's reference is pointed at the child instead, and
because everything in that child's subtree was already on the correct side of the
parent, nothing else needs checking.

Two children is the case that needs a thought. The node cannot be unhooked, because two
subtrees would be left dangling. What can be done is to replace its *key* with one that
keeps the invariant — a key larger than everything on the left and smaller than
everything remaining on the right — and then remove the node that key came from. The
smallest key in the right subtree is exactly that: larger than the node, because it is
in the right subtree, and smaller than every other key there. It is the **in-order
successor**, and it is found by stepping right once and then left until you cannot.
Because the walk stopped when there was no left child, the successor has at most one
child — so deleting *it* lands in the leaf case or the one-child case, never back in the
two-child case, and the recursion bottoms out at once instead of cascading.

The convention that removes most of the difficulty is that `delete` returns *the new
root of the subtree it was given*, and the caller stores that back. No parent pointers,
no special case for the root, no case for "the node I want to unhook is a left child":

```python
class TreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def insert(root, key):
    if root is None:
        return TreeNode(key)
    node = root
    while True:
        if key < node.key:
            if node.left is None:
                node.left = TreeNode(key)
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = TreeNode(key)
                return root
            node = node.right


def delete(node, key):
    """Remove key from this subtree and return the subtree's new root."""
    if node is None:
        return None
    if key < node.key:
        node.left = delete(node.left, key)
    elif key > node.key:
        node.right = delete(node.right, key)
    else:
        if node.left is None:
            return node.right          # a leaf, or a right child only
        if node.right is None:
            return node.left           # a left child only
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.key = successor.key
        node.right = delete(node.right, successor.key)
    return node


def pre_order(node, out):
    if node is not None:
        out.append(node.key)
        pre_order(node.left, out)
        pre_order(node.right, out)
    return out


def build(keys):
    root = None
    for key in keys:
        root = insert(root, key)
    return root


root = build([50, 30, 70, 20, 40, 60, 80])
root = delete(root, 20)
print("after deleting the leaf 20:       ", pre_order(root, []))
root = delete(root, 30)
print("after deleting one-child 30:      ", pre_order(root, []))
root = build([50, 30, 70, 20, 40, 60, 80])
root = delete(root, 50)
print("after deleting two-child root 50: ", pre_order(root, []))
```

Deleting 20 leaves `[50, 30, 40, 70, 60, 80]`; deleting 30, which now has only its
right child, splices 40 into its place. Deleting 50 from the fresh tree promotes 60,
not 40, giving `[60, 30, 20, 40, 70, 80]`. The predecessor would also keep the
invariant — it is the mirror choice — but the lab's checks are written for the
successor, and the pre-order is how they can tell.

The bug that lives here is forgetting the reassignment. Write `delete(node.left, key)`
without the `node.left =` in front and the recursion finds the node, computes the right
replacement, returns it — and the parent goes on pointing at the old child. The size
counter drops, `contains` still finds the key, and the tree and the count disagree from
then on. Every test about traversal order catches it; nothing about the code looks
wrong.

## Where it stops holding

Everything above assumes the keys are unique, comparable and *never change*. A repeated
key has nowhere consistent to go — the lab refuses it — and a key that is mutated after
insertion silently breaks the invariant, which is why map keys are immutable wherever
maps exist. The costs assume $h$ is small, and nothing
here keeps it small: an unbalanced tree fed sorted or nearly sorted keys is a linked
list with extra steps, and fixing that takes rotations — AVL and red–black trees — which
belong to a later course. And the in-order-gives-sorted property belongs to binary
*search* trees specifically; a heap is also a binary tree with an ordering invariant,
and its in-order traversal is not sorted at all.

## What you are about to build

The lab is *A binary search tree that can also delete*. `BST` takes an iterable of keys,
inserts them iteratively, exposes `root` so the checks can look at the shape, and offers
`contains`, the three traversals, `height` (edges, with $-1$ for an empty tree and $0$
for a single node), `min_key` and `max_key`, and `delete` with all three cases. The
worked example above is the lab's own: inserting 50, 30, 70, 20, 40, 60, 80 must give
the pre-order `[50, 30, 20, 40, 70, 60, 80]` and height 2, and deleting 50 must leave
`[60, 30, 20, 40, 70, 80]`. The last test shuffles 500 keys, deletes 250, and runs the
interval checker over what is left. The fill-in-the-blanks unit is `_delete` with five holes,
and the derivation unit does the height bounds with symbols.
''',
                },
                {
                    "title": "Base case, progress, and the price of recomputing",
                    "minutes": 12,
                    "body": r'''
Most of the code in this module describes itself the same way. `contains` is a
comparison and then *the same search, on a smaller tree*. The three traversals are the
node and then the same traversal of each subtree. `_delete` is a comparison and then the
same deletion, one level down. None of that is a stylistic preference: a subtree of a
binary search tree **is** a binary search tree, so a function written for one already
works on the other, and writing it any other way means writing out by hand what the
structure already says. (Insertion has the same shape, and the lab still asks for it as
a loop — which is a statement about what a call costs, and the point this reading is
here to make.)

A function that calls itself is **recursive**, and it needs exactly two things to be
correct. There must be a **base case** — an input it answers outright, without calling
itself — and every call it makes must move the input **towards** that case. Both, or
neither works: a base case that nothing reaches never fires, and progress towards
nothing runs forever.

```python
def countdown(n):
    """Print n down to 1, then stop."""
    if n == 0:               # the base case: answered without another call
        print("lift off")
        return
    print(n)
    countdown(n - 1)         # the same problem, one step smaller


countdown(3)
```

`n - 1` is the progress and `n == 0` is the base. Change the call to `countdown(n)` and
both rules survive on the page while neither survives in practice, which is why the
error you get is `RecursionError` rather than anything that names the real fault.

## What a call costs while it is waiting

`countdown(3)` does not finish before `countdown(2)` starts. It stops in the middle,
and the interpreter has to remember where: the value of `n`, the line to return to, the
half-finished expression. That record is a **stack frame**, and every call that has not
yet returned is holding one. Frames come back only as calls return, so what the machine
has to hold at once is not the number of calls — it is the **depth**, the longest chain
of calls waiting on each other.

For a tree, the depth of a recursive descent is the height of the tree. That is why the
previous reading's three thousand sorted keys ended in `RecursionError` at around the
thousandth: CPython caps the frame stack deliberately, because a runaway recursion is
far commoner than a legitimately deep one. A balanced tree of a million keys descends
about 20 levels and is in no danger; a degenerate one of three thousand is.

Depth is also why recursion suits data that is nested rather than long. A list of a
million numbers is one frame if you loop over it and a million if you recurse down it;
a folder tree, a parsed expression, or JSON of unknown shape is a handful of frames
either way, and the recursive version is the one that fits on the screen:

```python
def deep_sum(values):
    """Add up numbers nested in lists to any depth."""
    total = 0
    for item in values:
        if isinstance(item, list):
            total += deep_sum(item)     # same problem, one layer in
        else:
            total += item
    return total


print(deep_sum([1, [2, [3, [4, [5]]]], 6]))
```

## The price of recomputing

Recursion has one failure that correctness testing never catches, because the answers
are right. Take the definition of the Fibonacci numbers literally — each is the sum of
the two before it — and count the calls:

```python
CALLS = 0


def fib(n):
    """The definition, taken at its word."""
    global CALLS
    CALLS += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


print("fib(25) =", fib(25), "after", CALLS, "calls")
```

242,785 calls to produce 75,025. The reason is visible if you draw two levels of the
call tree: `fib(25)` asks for `fib(24)` and `fib(23)`, and `fib(24)` asks for `fib(23)`
again. The two branches share almost all of their work and neither knows the other
exists, so the same subproblems are solved over and over, and the total multiplies by
about 1.618 for every 1 added to `n`. Exponential — the growth class the first module
warned was hopeless past forty.

The repair is to write the answer down the first time it is computed. That is
**memoisation**: a dictionary from arguments to result, consulted before any work:

```python
MEMO = {}
CALLS = 0


def fib(n):
    """The same definition, with each answer computed once."""
    global CALLS
    CALLS += 1
    if n < 2:
        return n
    if n not in MEMO:
        MEMO[n] = fib(n - 1) + fib(n - 2)
    return MEMO[n]


print("fib(25) =", fib(25), "after", CALLS, "calls")
```

Forty-nine calls against 242,785, for identical arithmetic and the same answer. Each
value from 2 to 25 is computed once and read thereafter, so the work is proportional to
$n$ rather than to $\varphi^{n}$. The standard library will do the bookkeeping for you:

```python
from functools import lru_cache


@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(90))
```

## Where it stops holding

A cache is only sound when the function is **pure** — the same arguments always give
the same answer — and it needs the arguments to be hashable, which is the same
requirement a dictionary key has and for the same reason. It is also memory:
`lru_cache(maxsize=None)` never evicts anything, so a function called with millions of
distinct arguments trades a time problem for a space one.

And memoisation removes the repeated work, not the frames. `fib(2000)` under
`lru_cache` still descends two thousand calls deep on the first call and still ends in
`RecursionError`. Recursion whose depth grows with $n$ wants either a bound you can
argue for — a balanced tree's height — or a rewrite as a loop, which is what both labs
in this module ask for: the descent written iteratively, and Fibonacci carried in two
variables with no frames at all.
''',
                },
            ],
            "quiz": [{
                "title": "The invariant, and what it costs to break it",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In-order traversal of a BST comes out sorted. Why?",
                        "opts": [
                            "`insert` places each key in sorted position as it descends, so the order is built in",
                            "Left subtree, node, right subtree is smaller, this, larger — read out recursively",
                            "The tree is balanced, so the levels are visited in increasing order of key",
                            "Each node's key is greater than its parent's, so a depth-first walk is increasing",
                        ],
                        "a": 1,
                        "whys": [
                            r"`insert` maintains a *local* property at each node — smaller left, larger right — and never compares two keys that are not on the same root-to-node path. No sorted sequence is maintained anywhere. The global ordering is not built; it falls out.",
                            r"The invariant read out loud, applied recursively all the way down.",
                            r"Balance has nothing to do with it: a degenerate chain of a thousand nodes traverses in sorted order too, just slowly. And a *level*-order walk of a balanced tree is not sorted at all — the root, the median key, comes out first.",
                            r"That is a heap's invariant, not a BST's, and it describes a different structure with a different guarantee. In a BST the ordering constraint is left-versus-right, not parent-versus-child — and a heap's in-order traversal is not sorted.",
                        ],
                        "why": r"""
Left subtree, node, right subtree — and by the invariant that is exactly *smaller
keys, this key, larger keys*, applied recursively all the way down. The sortedness is
not something the traversal computes; it is the invariant read out loud. That is also
the strongest test there is for whether a tree really is a BST, and it is what the
lab's random-work check asserts after 250 deletions: a tree whose in-order traversal
is not sorted has stopped being a search tree, whatever its shape looks like.
""",
                    },
                    {
                        "q": "Deleting a node with two children promotes its in-order successor. Why is that successor always easy to remove?",
                        "opts": [
                            "It is always a leaf, so unhooking it from its parent is the entire job",
                            "It is the leftmost node of the right subtree, so it has no left child",
                            "It is the root of the right subtree, reachable in a single step from the node",
                            "Its key is copied rather than moved, so the node it came from can be left alone",
                        ],
                        "a": 1,
                        "whys": [
                            r"It may well have a right child. Delete 50 from the lab's tree and the successor 60 happens to be a leaf — but insert 65 first and it is not, and the code still has to work.",
                            r"Walk right once, then left until you cannot. Stopping means there is no left child.",
                            r"Only when that root has no left child. In the lab's tree the right subtree of 50 is rooted at 70, and the successor is 60 — one step further left, and the walk is what finds it.",
                            r"The key is copied, but the node it was copied from is still there, so the key now appears twice and the in-order traversal reports it twice. The recursive `_delete` on the right subtree is what removes the lower copy — and it terminates at once, because that node has at most one child.",
                        ],
                        "why": r"""
Walk right once, then left until you cannot. Stopping means there is no left child,
which is what makes the follow-up deletion land in the leaf case or the one-child
case — never back in the two-child case. So the recursion bottoms out immediately
instead of unwinding down the tree, and the whole two-child case costs one extra
descent rather than an unbounded cascade of promotions. That termination is the
reason the successor is chosen rather than, say, the largest key in the tree.
""",
                    },
                    {
                        "q": "The keys 1, 2, 3, …, 1000 are inserted in that order into an unbalanced BST. What is the height, counting edges?",
                        "opts": [
                            "10 — a BST of 1000 keys splits the range in half at each level, whatever the order",
                            "1000 — the root-to-leaf path passes through every one of the thousand nodes",
                            "999 — every key is larger than everything present, so every insert goes right",
                            "0 — a chain has no branching, and height measures how much a tree branches",
                        ],
                        "a": 2,
                        "whys": [
                            r"Halving the range at each level is what a *balanced* tree does, and nothing here enforces it — the BST invariant constrains where a key may go, not what shape results. About 10 is the height this tree would have had if the keys had arrived shuffled.",
                            r"One out. The path does pass through all 1000 nodes, but height counts *edges*, and 1000 nodes on a path are joined by 999 of them. The question says edges for exactly this reason.",
                            r"Sorted input is the worst input: each key walks the whole right spine and hangs off the bottom.",
                            r"Height is the length of the longest root-to-leaf *path*, not a measure of branching — and a chain is nothing but one long path. A 1000-node chain has the largest height a 1000-node tree can have, not the smallest.",
                        ],
                        "why": r"""
Sorted input is the worst input. Each key walks the entire right spine and hangs off
the bottom, so the tree is a linked list wearing tree-shaped types: 1000 nodes,
999 edges from the root to the deepest leaf, and `contains(1000)` costing 1000
comparisons. About 10 is the height a *balanced* thousand-node tree would have, and
the gap between 10 and 999 — a hundredfold, on identical keys — is the entire
justification for red-black and AVL trees.
""",
                    },
                    {
                        "q": "Which traversal is the safe order in which to free every node, in a language where you must free them yourself?",
                        "opts": [
                            "Pre-order, so each node is released before anything can reach it again",
                            "In-order, because the keys come out in order and nothing is skipped",
                            "Post-order — both children are released before the node that points at them",
                            "Any order works, because freeing a node does not disturb the pointers other nodes hold",
                        ],
                        "a": 2,
                        "whys": [
                            r"Free the parent first and the very next thing the traversal does is read `node.left` out of memory that has just been handed back. That is a use-after-free, and it usually appears to work, which is what makes it dangerous.",
                            r"In-order frees the node *between* its two subtrees, so the right subtree is reached through a pointer read out of a node that no longer exists. The key order is beside the point here; this is the one traversal question that is not about keys at all.",
                            r"A node is visited only once both subtrees are finished, so nothing below it is still needed when it goes.",
                            r"The pointers that matter are the ones *inside* the node being freed. `node.left` and `node.right` live in that node's own memory, and once it is freed that memory belongs to the allocator, not to you.",
                        ],
                        "why": r"""
Post-order visits a node only after both of its subtrees are finished, so when the
node is freed nothing below it is still needed — and crucially, the pointers needed
to *reach* the children were read before the parent went away. Every other order
dereferences at least one field of a node it has already released. This is the one
traversal whose reason for existing has nothing to do with the keys, which is why it
is easy to forget it exists until a `free` walk corrupts a heap.
""",
                    },
                    {
                        "q": "Search, insert and delete on a BST are all $O(h)$. Why is that a warning rather than a reassurance?",
                        "opts": [
                            "$h$ is close to $n$ in practice, so the bound is far too optimistic to rely on",
                            "$h$ cannot be measured without walking the tree, so the bound cannot be checked",
                            "$h$ runs from $\\log_2 n$ to $n-1$, and the insertion order alone decides which",
                            "$O(h)$ hides a comparison at every node on the path, so it is really $O(h\\log n)$",
                        ],
                        "a": 2,
                        "whys": [
                            r"Too pessimistic rather than too optimistic — and it depends entirely on the input. Random insertion keeps $h$ near $3\log_2 n$; it is *sorted* insertion that drives it to $n-1$, and knowing which one you have is the whole question.",
                            r"Height is cheap to measure — one post-order walk — and the lab measures it. But a measured $h$ is a fact about the tree you have, not a promise about the tree the next thousand inserts will leave you with.",
                            r"Two orders of magnitude for the same thousand keys, settled by nothing but arrival order.",
                            r"One comparison per level, and a level is one node — which is exactly what $O(h)$ counts. Nothing is hidden: the point of the invariant is that a single comparison decides which way to go.",
                        ],
                        "why": r"""
$O(h)$ is an honest bound that says nothing at all until you know $h$, and $h$ spans
two orders of magnitude for the same thousand keys depending on nothing but the order
they arrived in. Feed a tree its keys sorted — which is what happens when you load a
table from a database that helpfully returned it ordered — and every operation
degrades from ten steps to a thousand with no error and no warning. Random insertion
keeps $h$ down to about $3\log_2 n$ — the *average* node sits at depth
$1.39\log_2 n$, but the height is the deepest path, not the typical one — which is
why the lab shuffles before building.
""",
                    },
                    {
                        "q": "A tree holds 20 at the root, 10 on its left, 30 on its right, and 25 as the right child of 10. Every parent is larger than its left child and smaller than its right child. Is it a BST?",
                        "opts": [
                            "Yes — every parent and child pair satisfies the invariant, which is all it asks",
                            "No — 25 lies in the left subtree of 20 and is larger than it",
                            "Yes, but only until some key between 20 and 25 is inserted somewhere",
                            "No — 10 has a right child and no left child, which the invariant forbids",
                        ],
                        "a": 1,
                        "whys": [
                            r"Parent-and-child pairs are what a *local* check tests, and this tree passes every one of them. The invariant is about subtrees: everything in the left subtree of 20 must be below 20, and 25 is not.",
                            r"`contains(25)` goes right at 20 and never looks left, so the key is in the tree and unreachable.",
                            r"It is already broken, and inserting nothing at all will not fix it — `contains(25)` fails today, on this tree. This is exactly why a checker has to carry a low and a high bound down the recursion instead of comparing neighbours.",
                            r"A node with one child is perfectly ordinary — it is the one-child deletion case, and several nodes in the lab's tree look like it. The invariant says nothing whatever about how many children a node has.",
                        ],
                        "why": r"""
The invariant is not "larger than the left child and smaller than the right child".
It is "larger than **everything** in the left subtree and smaller than **everything**
in the right subtree", and the difference only shows up two levels down — which is
precisely where it is easy to miss:

```
        20
       /  \
     10    30
       \
        25
```

Every parent–child pair here is correctly ordered. The tree is still not a BST,
because a search for 25 turns right at the root and never comes back. That is why the
lab's checker is `_check(node, lo, hi)` and not a comparison between neighbours: it
carries the interval each subtree is confined to down the recursion, narrowing it at
every step, so a key that escapes its ancestor's bound is caught however deep it sits.
A local check would have signed this tree off.
""",
                    },
                ],
            }, {
                "title": "Growth, halving, and what a call leaves behind",
                "minutes": 6,
                "questions": [
                    {
                        "q": "A loop over `n` items, with a second loop inside it that also runs over those `n` items, does work that grows as…",
                        "opts": [
                            r"$O(2n)$ — two loops, so twice the work of one pass over the data",
                            r"$O(n^2)$ — the inner loop runs its full length once for every outer step",
                            r"$O(n\log n)$ — each level of nesting multiplies the cost by a logarithmic factor",
                            r"$O(n)$ — both loops walk the same list, so the list is walked once",
                        ],
                        "a": 1,
                        "whys": [
                            r"Two loops one after the other would be $2n$, and the constant would be dropped anyway. These are nested, so the inner one restarts from the top on every step of the outer one.",
                            r"$n$ steps outside, and the inner loop's full length inside each of them.",
                            r"$n\log n$ is what halving buys — a divide-and-conquer sort, say. Nothing here halves anything, and the depth of the nesting is a constant 2, not a function of $n$.",
                            r"The list is walked $n$ times, once per step of the outer loop. Walking it once is a single loop, and that is the $O(n)$ version of this code.",
                        ],
                        "why": r"The comparisons come to $n + n + \dots$, one full inner pass per outer step, and the leading term is $n^2$. Counting a nested loop as $2n$ is the commonest slip here: sequential loops add, nested loops multiply.",
                    },
                    {
                        "q": "How do `x in my_set` and `x in my_list` compare?",
                        "opts": [
                            r"Both are $O(n)$: `in` compares against the elements held, either way",
                            r"The set is $O(1)$, the list $O(n)$: a hash names the slot, a list is scanned",
                            r"The list is $O(1)$, the set $O(n)$: a set must hash every element it holds first",
                            r"Both are $O(1)$: the interpreter indexes either container for membership",
                        ],
                        "a": 1,
                        "whys": [
                            r"True of the list, and it is what the set avoids. Hashing the key computes the slot it would be in, so a set answers without comparing against anything but that slot's contents.",
                            r"One hash against a scan — and rewriting a list membership test inside a loop as a set is the commonest real speedup there is.",
                            r"Inverted. Hashing happens on the way *in*, once per element; a lookup hashes the key it was given and nothing else.",
                            r"A list has no index from value to position — that is exactly what a hash table adds, and what `in` on a list has to do without.",
                        ],
                        "why": r"A set hashes the key and reads one slot, which is $O(1)$. A list has nothing that says where a value might be, so `in` compares against the elements until it finds one or runs out: $O(n)$. Inside a loop, that difference is $O(n)$ against $O(n^2)$.",
                    },
                    {
                        "q": "Binary search needs its input to be…",
                        "opts": [
                            "free of duplicates, or the halving may return the wrong equal key",
                            "sorted, because only order says which half of the window to throw away",
                            "numeric, since the midpoint of the window is found by averaging the two ends",
                            "short enough to fit in memory, which is what makes an arbitrary index cheap",
                        ],
                        "a": 1,
                        "whys": [
                            "Duplicates are allowed. The search may return any one of the equal keys, which is a question of *which* index comes back rather than whether the search works.",
                            "Order is the whole mechanism: one comparison rules out half the window because everything on that side is on the wrong side of the value.",
                            "The midpoint is an average of the two *indices*, not of the values, so the elements need only be comparable — strings and dates binary-search perfectly well.",
                            "Size is not the requirement; a sorted file on disk is binary-searched the same way. What the algorithm needs is an index that costs the same wherever it points, plus order.",
                        ],
                        "why": "Comparing against the middle element is only informative when order tells you which side the target must be on. Take the sortedness away and a comparison rules out one element rather than half the window, and the search degrades into a scan that also skips things.",
                    },
                    {
                        "q": "An editor's undo needs the actions to come back in a particular order. Which structure gives it?",
                        "opts": [
                            "A queue: the oldest action waiting is the first one taken, in arrival order",
                            "A stack: undo takes the most recent action first, which is last in, first out",
                            "A set: every distinct action is held once, and undoing removes it from the set",
                            "A binary search tree keyed on the timestamp, so the latest sits at the far right",
                        ],
                        "a": 1,
                        "whys": [
                            "That is redo-from-the-beginning, not undo: it would reverse the very first edit of the session first.",
                            "Push each action as it happens, pop to undo — the order reverses itself with no bookkeeping.",
                            "Actions repeat, and a set holds each thing once, so typing the same character twice would leave one action to undo.",
                            "It would work and it is $O(\\log n)$ per operation for something a stack does in $O(1)$ — the extra structure buys ordering by key, which nothing here needs.",
                        ],
                        "why": "Undo asks for the most recently added item, which is what last in, first out means, and pushing and popping the end of a list is $O(1)$. Anything ordered the other way undoes the wrong edit; anything ordered by key pays for a search nobody needs.",
                    },
                    {
                        "q": "What must every recursive function have?",
                        "opts": [
                            "A loop inside it, because the repetition has to come from somewhere",
                            "A base case it answers without recursing, and calls that move towards it",
                            "Exactly one call to itself, or the same subproblem is solved twice over",
                            "Shared state outside the function, so each call can see what the last one left",
                        ],
                        "a": 1,
                        "whys": [
                            "The repetition comes from the calls themselves. The three traversals in this module recurse into each subtree and contain no loop of their own.",
                            "Both halves are needed: a base case nothing reaches never fires, and progress towards nothing runs until the frames are gone.",
                            "Two calls are fine — the traversals make two, one per subtree. Repeated subproblems are a cost to fix with a cache, not a rule of correctness.",
                            "Each call gets its own frame with its own arguments, which is what lets the same function work on a subtree without disturbing the call above it.",
                        ],
                        "why": "A base case is where the recursion stops, and progress is what reaches it. Miss either and the frames pile up until Python raises `RecursionError`, which is the stack's way of reporting an infinite loop.",
                    },
                    {
                        "q": "Memoisation makes a recursive function faster by…",
                        "opts": [
                            "compiling the hot function down to machine code the second time it is called",
                            "storing each subproblem's answer the first time, so it is computed once",
                            "running the two recursive branches in parallel on separate threads",
                            "reaching the base case sooner, which cuts the depth of the call chain",
                        ],
                        "a": 1,
                        "whys": [
                            "That is a compiler's job, and it would change the constant rather than the growth. Memoisation leaves the code exactly as it is and removes the repeats.",
                            "`fib(25)` falls from 242,785 calls to 49, doing the same arithmetic once each.",
                            "Nothing runs in parallel, and it would not help much: the branches overlap almost entirely, so the same work would be done twice at once.",
                            "The depth is untouched — `fib(n)` still descends to `fib(1)` on the first call, which is why a memoised recursion can still exhaust the stack. What goes is the *width* of the call tree.",
                        ],
                        "why": "The naive recursion recomputes the same subproblems exponentially often. A cache consulted before the work turns each distinct subproblem into one computation and a lookup thereafter, which is the difference between $O(\\varphi^{n})$ and $O(n)$ — the same arithmetic, none of the repeats.",
                    },
                ],
            }],
            "blanks": {
                "title": "Deletion, all three cases",
                "minutes": 9,
                "lang": "python",
                "caption": "bst.py — the recursion that reattaches what it returns",
                "brief": r"""
Insertion is the easy half. Deletion is where a BST implementation is usually wrong,
and the trick that removes most of the difficulty is the convention below: `_delete`
returns *the new root of the subtree it was given*, and the caller stores that back.
No parent pointers, no special case for the root, no case for "the node I want to
unhook is a left child".

Nothing runs here. Correctly filled, deleting 50 from the tree built by inserting
50, 30, 70, 20, 40, 60, 80 leaves a pre-order of `[60, 30, 20, 40, 70, 80]`.
""",
                "listing": r'''
def _delete(self, node, key):
    """Remove key from this subtree and return the subtree's new root."""
    if node is None:
        return None
    if key < node.key:
        node.left = self._delete(___, key)
    elif key > node.key:
        node.right = self._delete(node.right, key)
    else:
        if node.left is None:          # leaf, or a right child only
            return ___
        if node.right is None:         # a left child only
            return node.left
        successor = node.___           # the in-order successor lives in here
        while successor.___ is not None:
            successor = successor.left
        node.key = successor.key
        node.right = self._delete(node.right, ___)
    return node
''',
                "blanks": [
                    {
                        "prompt": "The key is smaller than this node, so the search continues where?",
                        "hole": "?",
                        "opts": ["node.right", "node", "self.root", "node.left"],
                        "a": 3,
                        "why": "Smaller keys live to the left — the same descent as `contains`, with the difference that the result is stored back into `node.left`, which is how a deletion three levels down gets reattached on the way out.",
                        "whys": [
                            "Descending right when the key is smaller searches the half of the tree the invariant guarantees it is not in. The call returns the right subtree unchanged, which is then assigned to `node.left`, and the tree loses everything on the left.",
                            "Passing the same node back is unbounded recursion: the guard `key < node.key` is still true, so it recurses until the stack runs out.",
                            "Restarting from the root each time is unbounded recursion by a longer route, and it also discards the descent already made.",
                            "Smaller keys live to the left — the same descent as `contains`, with the difference that the result is stored back into `node.left`, which is how a deletion three levels down gets reattached on the way out.",
                        ],
                    },
                    {
                        "prompt": "There is no left child. What takes this node's place?",
                        "hole": "?",
                        "opts": ["node", "node.right", "node.left", "None"],
                        "a": 1,
                        "why": "Whatever is on the right is spliced into the gap — and when there is nothing on the right either, that expression is `None`, which is exactly the leaf case. One line covers both.",
                        "whys": [
                            "Returning the node itself deletes nothing — the size counter drops, the key stays reachable, and the map and the tree disagree from then on.",
                            "Whatever is on the right is spliced into the gap — and when there is nothing on the right either, that expression is `None`, which is exactly the leaf case. One line covers both.",
                            "The left child is `None` here by the test immediately above, so this always returns `None` and silently discards the entire right subtree along with the node.",
                            "Returning nothing handles a leaf correctly and throws away a whole right subtree whenever there is one. The lab catches it: after deleting 30 from the sample tree, 40 must survive.",
                        ],
                    },
                    {
                        "prompt": "The in-order successor is the smallest key still above this node. Which subtree holds it?",
                        "hole": "?",
                        "opts": ["left", "key", "right"],
                        "a": 2,
                        "why": "Everything larger than the node sits in its right subtree, so the next key in sorted order is the smallest one in there. Starting anywhere else and there is nothing to be smallest of.",
                        "whys": [
                            "Going left and then further left finds the smallest key in the *left* subtree — the minimum of everything below the node, not its successor. Promoting it puts a small key above a whole subtree of larger ones and breaks the invariant on the spot.",
                            "That is a key, not a node, and the walk below immediately asks it for a `.left` it does not have.",
                            "Everything larger than the node sits in its right subtree, so the next key in sorted order is the smallest one in there. Starting anywhere else and there is nothing to be smallest of.",
                        ],
                    },
                    {
                        "prompt": "…and the walk down to it goes which way?",
                        "hole": "?",
                        "opts": ["left", "right", "key"],
                        "a": 0,
                        "why": "Left as far as it goes. The node where the walk stops has no left child, and that is what guarantees the follow-up deletion cannot land in the two-child case again.",
                        "whys": [
                            "Left as far as it goes. The node where the walk stops has no left child, and that is what guarantees the follow-up deletion cannot land in the two-child case again.",
                            "Walking right finds the *largest* key in the right subtree instead of the smallest. Promoting it puts a key above the rest of that subtree that is larger than all of them, and in-order traversal stops being sorted.",
                            "The loop body assigns `successor = successor.left`, so a key here mixes types and the comparison against `None` never means what it looks like.",
                        ],
                    },
                    {
                        "prompt": "The successor's key has been copied up. Now remove the node it came from.",
                        "hole": "?",
                        "opts": ["key", "successor", "node.left.key", "successor.key"],
                        "a": 3,
                        "why": "The key now appears twice in the tree — once where it was promoted to and once where it came from. This call removes the lower copy, and because that node has at most one child the recursion stops there rather than descending further.",
                        "whys": [
                            "`key` is the key that was just overwritten, and it was smaller than everything in the right subtree — so the search runs off the left edge, removes nothing, and leaves the successor's node in place while the size counter says one fewer. The duplicate is then reachable from two places.",
                            "That is the node object rather than its key, so every comparison in the recursive call raises `TypeError` on the first `<` against an integer.",
                            "The left child of the node being deleted has nothing to do with the right subtree being searched. The call removes some unrelated key if it happens to collide, and nothing at all otherwise.",
                            "The key now appears twice in the tree — once where it was promoted to and once where it came from. This call removes the lower copy, and because that node has at most one child the recursion stops there rather than descending further.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "How shallow a tree of n keys is allowed to be",
                "minutes": 12,
                "vars": ["n", "h", "d"],
                "brief": r"""
Every BST operation costs $O(h)$, so the only question worth asking about a tree is
how big $h$ can be and how small it can get. The lower end is pure counting: a tree
of height $h$ has room for only so many nodes, and $n$ keys therefore need a certain
depth no matter how cleverly they are arranged.

Height is counted in **edges**: a single node has height 0.
""",
                "steps": [
                    {
                        "prompt": "In a perfect binary tree, the root sits alone at depth 0 and every node has two children. How many nodes are at depth $d$?",
                        "answer": "2^{d}",
                        "hint": "Each level has twice as many nodes as the one above it, starting from 1.",
                        "deconstruct": [
                            "Depth 0 holds 1 node, depth 1 holds 2, depth 2 holds 4.",
                            "Each step down doubles the count, $d$ times over.",
                        ],
                    },
                    {
                        "prompt": "Add up every level from depth 0 to depth $h$. How many nodes $n$ does a perfect tree of height $h$ hold?",
                        "given": "$1 + 2 + 4 + \\dots + 2^{h}$",
                        "answer": "2^{h+1} - 1",
                        "hint": "The same geometric series as the doubling array, run one step further: it goes up to $2^{h}$ rather than stopping at $2^{h-1}$.",
                        "deconstruct": [
                            "There are $h+1$ levels, holding $2^0$ up to $2^{h}$.",
                            "A geometric series with ratio 2 summing to $2^{h}$ comes to one less than the next power: $2^{h+1} - 1$.",
                        ],
                    },
                    {
                        "prompt": "Now count only the levels above the deepest one — that is a perfect tree of height $h - 1$. How many nodes sit strictly above depth $h$?",
                        "answer": "2^{h} - 1",
                        "hint": "Use the formula you just derived with $h - 1$ in place of $h$.",
                        "deconstruct": [
                            "A perfect tree of height $h-1$ holds $2^{(h-1)+1} - 1$ nodes.",
                            "The exponent simplifies to $h$.",
                        ],
                    },
                    {
                        "prompt": "A perfect tree with $n$ nodes therefore satisfies $n = 2^{h+1} - 1$. Rearrange it to give $2^{h+1}$ in terms of $n$.",
                        "answer": "n + 1",
                        "hint": "One term to move across.",
                        "deconstruct": [
                            "Add 1 to both sides of $n = 2^{h+1} - 1$.",
                        ],
                    },
                    {
                        "prompt": "Now the other end. Insert $n$ keys in sorted order, so every node gets exactly one child. What is the height?",
                        "answer": "n - 1",
                        "hint": "The tree is a single path. Count the edges on it, not the nodes.",
                        "deconstruct": [
                            "$n$ nodes in a chain from root to leaf.",
                            "A path through $n$ nodes has $n-1$ edges, and height counts edges.",
                        ],
                    },
                ],
                "closing": r"""
Take base-2 logarithms of $2^{h+1} = n + 1$ and the best case is
$h = \log_2(n+1) - 1$. Against the worst case of $n - 1$, for a million keys: 19
versus 999,999. Same keys, same code, same invariant — the only difference is the
order they arrived in.

Step 3 is worth a second look, because it is the reason nobody bothers optimising the
upper levels of a tree. A perfect tree has $2^{h}$ nodes on its bottom level and
$2^{h} - 1$ everywhere else combined: more than half of all the nodes are leaves, and
the population halves again with every level you climb — $2^{h-1}$ one step above
the leaves, $2^{h-2}$ above that, down to a single root. That fact is what makes
bottom-up heapify linear, and you will meet it again in the heap module.
""",
            },
            "lab": [{
                "title": "A binary search tree that can also delete",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Keys are comparable and unique; a repeated `insert` is ignored.

## `TreeNode(key)`

`key`, `left`, `right`. The tree exposes its `root` so the checks can look at
the shape you built.

## `BST`

- `insert(key)` — `True` if the key was new, `False` if it was already there.
  Write this **iteratively**: a recursive insert overflows the stack on sorted
  input, which is exactly the input that produces the deepest trees.
- `contains(key)`, `__len__`
- `in_order()`, `pre_order()`, `post_order()` — lists of keys
- `height()` — edges on the longest root-to-leaf path. An empty tree is `-1`,
  a single node is `0`
- `min_key()` / `max_key()` — `ValueError` on an empty tree
- `delete(key)` — `True` when something was removed, `False` when the key was
  absent. Three cases:
  - **leaf** — unhook it
  - **one child** — splice the child into its place
  - **two children** — copy the in-order successor's key into this node, then
    delete that successor from the right subtree (it has at most one child, so
    that recursion terminates immediately)

## Worked example

Inserting `50, 30, 70, 20, 40, 60, 80` gives

```text
            50
        30      70
      20  40  60  80
```

```text
in_order()    -> [20, 30, 40, 50, 60, 70, 80]
pre_order()   -> [50, 30, 20, 40, 70, 60, 80]
post_order()  -> [20, 40, 30, 60, 80, 70, 50]
height()      -> 2
```

Deleting `50` from that tree must promote `60`, the in-order successor, not
`40`, the in-order predecessor:

```text
pre_order()   -> [60, 30, 20, 40, 70, 80]
```
''',
                "files": [{"name": "main.py", "content": r'''
class TreeNode:
    """One node of a binary search tree."""

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BST:
    """An unbalanced binary search tree over unique, comparable keys."""

    def __init__(self, keys=None):
        self.root = None
        self._size = 0
        for key in keys or []:
            self.insert(key)

    def __len__(self):
        # your code here
        return 0

    def insert(self, key):
        """Add a key. True when it was new, False when it was already present."""
        # your code here

    def contains(self, key):
        """Is the key in the tree?"""
        # your code here

    def in_order(self):
        """Keys in sorted order."""
        # your code here

    def pre_order(self):
        """Node, then left subtree, then right subtree."""
        # your code here

    def post_order(self):
        """Both subtrees, then the node."""
        # your code here

    def height(self):
        """Edges on the longest root-to-leaf path; -1 for an empty tree."""
        # your code here

    def min_key(self):
        """The smallest key; ValueError when empty."""
        # your code here

    def max_key(self):
        """The largest key; ValueError when empty."""
        # your code here

    def delete(self, key):
        """Remove a key. True when something went, False when it was absent."""
        # your code here


tree = BST([50, 30, 70, 20, 40, 60, 80])
print(tree.in_order())
print(tree.pre_order(), tree.height())
tree.delete(50)
print(tree.pre_order())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class TreeNode:
    """One node of a binary search tree."""

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BST:
    """An unbalanced binary search tree over unique, comparable keys."""

    def __init__(self, keys=None):
        self.root = None
        self._size = 0
        for key in keys or []:
            self.insert(key)

    def __len__(self):
        return self._size

    def insert(self, key):
        """Add a key. True when it was new, False when it was already present."""
        if self.root is None:
            self.root = TreeNode(key)
            self._size += 1
            return True
        node = self.root
        while True:
            if key == node.key:
                return False
            if key < node.key:
                if node.left is None:
                    node.left = TreeNode(key)
                    self._size += 1
                    return True
                node = node.left
            else:
                if node.right is None:
                    node.right = TreeNode(key)
                    self._size += 1
                    return True
                node = node.right

    def contains(self, key):
        """Is the key in the tree?"""
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def in_order(self):
        """Keys in sorted order."""
        keys = []

        def walk(node):
            if node is None:
                return
            walk(node.left)
            keys.append(node.key)
            walk(node.right)

        walk(self.root)
        return keys

    def pre_order(self):
        """Node, then left subtree, then right subtree."""
        keys = []

        def walk(node):
            if node is None:
                return
            keys.append(node.key)
            walk(node.left)
            walk(node.right)

        walk(self.root)
        return keys

    def post_order(self):
        """Both subtrees, then the node."""
        keys = []

        def walk(node):
            if node is None:
                return
            walk(node.left)
            walk(node.right)
            keys.append(node.key)

        walk(self.root)
        return keys

    def height(self):
        """Edges on the longest root-to-leaf path; -1 for an empty tree."""

        def measure(node):
            if node is None:
                return -1
            return 1 + max(measure(node.left), measure(node.right))

        return measure(self.root)

    def min_key(self):
        """The smallest key; ValueError when empty."""
        if self.root is None:
            raise ValueError("an empty tree has no smallest key")
        node = self.root
        while node.left is not None:
            node = node.left
        return node.key

    def max_key(self):
        """The largest key; ValueError when empty."""
        if self.root is None:
            raise ValueError("an empty tree has no largest key")
        node = self.root
        while node.right is not None:
            node = node.right
        return node.key

    def delete(self, key):
        """Remove a key. True when something went, False when it was absent."""
        if not self.contains(key):
            return False
        self.root = self._delete(self.root, key)
        self._size -= 1
        return True

    def _delete(self, node, key):
        """Remove key from this subtree and return the subtree's new root."""
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)
        return node


tree = BST([50, 30, 70, 20, 40, 60, 80])
print(tree.in_order())
print(tree.pre_order(), tree.height())
tree.delete(50)
print(tree.pre_order())
'''}],
                "hints": [
                    "Iterative insert: walk down keeping the current node, and stop when the child you want to descend into is `None` — that empty slot is where the new node goes.",
                    "All three traversals are the same three lines in different orders; write one recursive `walk` that appends to a list from the enclosing scope.",
                    "`_delete(node, key)` should *return the new subtree root* and let the caller reattach it: `node.left = self._delete(node.left, key)`. That single convention removes every parent-pointer special case.",
                    "For the two-child case, find the leftmost node of the right subtree, copy its key up, and then delete *that key* from the right subtree — it is guaranteed to be a leaf or a one-child node, so the recursion stops there.",
                ],
                "tests": [
                    {"name": "Insert, contains and length", "code": r'''
_t = BST()
assert len(_t) == 0 and _t.root is None, "a fresh tree is empty"
assert _t.contains(1) is False, "nothing is in an empty tree"
assert _t.insert(50) is True, "the first insert is new"
assert _t.insert(50) is False, "a repeated key must be refused"
assert len(_t) == 1, f"length is {len(_t)}, expected 1 after a duplicate insert"
for _k in [30, 70, 20, 40, 60, 80]:
    _t.insert(_k)
assert len(_t) == 7, f"length is {len(_t)}, expected 7"
for _k in [20, 30, 40, 50, 60, 70, 80]:
    assert _t.contains(_k), f"{_k} was inserted but contains() says no"
for _k in [0, 45, 99]:
    assert not _t.contains(_k), f"{_k} was never inserted but contains() says yes"
'''},
                    {"name": "The three traversals", "code": r'''
_t = BST([50, 30, 70, 20, 40, 60, 80])
assert _t.in_order() == [20, 30, 40, 50, 60, 70, 80], f"in_order gave {_t.in_order()!r}"
assert _t.pre_order() == [50, 30, 20, 40, 70, 60, 80], f"pre_order gave {_t.pre_order()!r}"
assert _t.post_order() == [20, 40, 30, 60, 80, 70, 50], f"post_order gave {_t.post_order()!r}"
assert BST().in_order() == [] and BST().pre_order() == [] and BST().post_order() == [], \
    "an empty tree traverses to an empty list"
assert BST([7]).in_order() == [7] and BST([7]).post_order() == [7], "one node, one key"
'''},
                    {"name": "Height, minimum and maximum", "code": r'''
assert BST().height() == -1, f"an empty tree has height -1, got {BST().height()!r}"
assert BST([1]).height() == 0, f"a single node has height 0, got {BST([1]).height()!r}"
assert BST([50, 30, 70, 20, 40, 60, 80]).height() == 2, "a full tree of 7 nodes has height 2"
assert BST([1, 2, 3, 4, 5]).height() == 4, \
    f"sorted input degenerates to a chain, got height {BST([1, 2, 3, 4, 5]).height()!r}"
assert BST([5, 4, 3, 2, 1]).height() == 4, "reverse-sorted input degenerates the other way"
_t = BST([50, 30, 70, 20, 80])
assert (_t.min_key(), _t.max_key()) == (20, 80), f"Got {(_t.min_key(), _t.max_key())!r}"
for _m in ("min_key", "max_key"):
    try:
        getattr(BST(), _m)()
        assert False, f"{_m} on an empty tree should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Deleting a leaf and a one-child node", "code": r'''
_t = BST([50, 30, 70, 20, 40, 60, 80])
assert _t.delete(20) is True, "deleting a leaf returns True"
assert _t.in_order() == [30, 40, 50, 60, 70, 80], f"after deleting 20: {_t.in_order()!r}"
assert _t.pre_order() == [50, 30, 40, 70, 60, 80], f"shape after deleting a leaf: {_t.pre_order()!r}"
assert len(_t) == 6, f"length is {len(_t)}, expected 6"
assert _t.delete(30) is True, "30 now has a single child"
assert _t.pre_order() == [50, 40, 70, 60, 80], \
    f"the surviving child must be spliced in; got {_t.pre_order()!r}"
assert _t.delete(99) is False, "deleting an absent key returns False"
assert len(_t) == 5, f"a failed delete must not change the size; got {len(_t)}"
'''},
                    {"name": "Deleting a two-child node promotes the successor", "code": r'''
_t = BST([50, 30, 70, 20, 40, 60, 80])
assert _t.delete(50) is True, "the root has two children"
assert _t.pre_order() == [60, 30, 20, 40, 70, 80], \
    f"60 is the in-order successor and must be promoted; got {_t.pre_order()!r}"
assert _t.in_order() == [20, 30, 40, 60, 70, 80], f"in_order gave {_t.in_order()!r}"
assert len(_t) == 6 and _t.root.key == 60, f"root is {_t.root.key!r}, expected 60"
_u = BST([50, 30, 70, 20, 40, 60, 80])
assert _u.delete(30) is True, "30 has two children too"
assert _u.pre_order() == [50, 40, 20, 70, 60, 80], \
    f"40 should be promoted into 30's place; got {_u.pre_order()!r}"
'''},
                    {"name": "Deleting down to nothing", "code": r'''
_t = BST([2, 1, 3])
assert _t.delete(2) and _t.delete(3) and _t.delete(1), "every delete should succeed"
assert len(_t) == 0 and _t.root is None and _t.in_order() == [], \
    f"the tree should be empty, got root {_t.root!r} and {_t.in_order()!r}"
assert _t.height() == -1, "an emptied tree is back to height -1"
assert _t.insert(9) is True and _t.in_order() == [9], "the tree must be reusable"
_single = BST([5])
assert _single.delete(5) is True and _single.root is None, "deleting the only node clears the root"
'''},
                    {"name": "The invariant survives random work", "code": r'''
import random as _random
_rng = _random.Random(7)
_keys = list(range(500))
_rng.shuffle(_keys)
_t = BST(_keys)
_alive = set(_keys)
assert _t.in_order() == sorted(_alive), "in-order traversal must be sorted"
for _k in _rng.sample(_keys, 250):
    assert _t.delete(_k) is True, f"deleting {_k} should have succeeded"
    _alive.discard(_k)
assert len(_t) == len(_alive), f"length is {len(_t)}, expected {len(_alive)}"
assert _t.in_order() == sorted(_alive), "after 250 deletions the traversal is still not sorted"
def _check(_node, _lo, _hi):
    if _node is None:
        return
    assert (_lo is None or _node.key > _lo) and (_hi is None or _node.key < _hi), \
        f"key {_node.key!r} sits outside its allowed range ({_lo!r}, {_hi!r})"
    _check(_node.left, _lo, _node.key)
    _check(_node.right, _node.key, _hi)
_check(_t.root, None, None)
for _k in sorted(_alive)[:20]:
    assert _t.contains(_k), f"{_k} should still be present"
for _k in _keys:
    if _k not in _alive:
        assert not _t.contains(_k), f"{_k} was deleted but is still found"
'''},
                ],
            }, {
                "title": "Fibonacci, fast and slow",
                "runtime": "python",
                "minutes": 16,
                "brief": r'''
The same function twice, so the gap between the two is something you have measured
rather than something you have been told. (`fib(0)` is 0, `fib(1)` is 1, and every
number after those is the sum of the two before it.)

## `fib_naive(n)`

The definition taken at its word: the base cases, and otherwise
`fib_naive(n - 1) + fib_naive(n - 2)`. It must genuinely call itself twice, with no
cache of any kind — one check wraps the function in a counter and requires the call
count to be exponential, because the point of this half is to feel what
recomputation costs.

## `fib(n)`

The same numbers, cheaply. Either hold the last two values in variables and loop, or
keep the recursion and memoise it — a dictionary consulted before the work, or
`@lru_cache(maxsize=None)` from `functools`.

It must return `fib(90) = 2880067194370816120` exactly, and a check times that call
and fails anything slower than half a second. Python integers are arbitrary
precision, so the 19 digits are not a problem; recomputation is.

```text
[fib(n) for n in range(10)]  ->  [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
fib(90)                      ->  2880067194370816120
```

The starter times both on `n = 25` so the gap is on the screen. Raise the naive one
to 32 and watch it crawl; going much past that in a browser tab is a long wait for a
number you already have.
''',
                "files": [{"name": "main.py", "content": r'''
import time


def fib_naive(n):
    """The recursive definition, with no caching. Exponential."""
    # your code here


def fib(n):
    """The same numbers in O(n): iterate, or memoise."""
    # your code here


start = time.time()
print("fib_naive(25) =", fib_naive(25))
print(f"  took {time.time() - start:.3f}s")

start = time.time()
print("fib(90) =", fib(90))
print(f"  took {time.time() - start:.4f}s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import time


def fib_naive(n):
    """The recursive definition, with no caching. Exponential."""
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib(n):
    """The same numbers in O(n): two variables, one pass."""
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


start = time.time()
print("fib_naive(25) =", fib_naive(25))
print(f"  took {time.time() - start:.3f}s")

start = time.time()
print("fib(90) =", fib(90))
print(f"  took {time.time() - start:.4f}s")
'''}],
                "hints": [
                    "`fib_naive`: `if n < 2: return n`, then "
                    "`return fib_naive(n - 1) + fib_naive(n - 2)`. Both base cases are "
                    "covered by that one line, because fib(0) is 0 and fib(1) is 1.",
                    "Iterative `fib`: start `previous, current = 0, 1`, then n times "
                    "`previous, current = current, previous + current`, and return "
                    "`previous`. Assigning both on one line matters — computing `current` "
                    "first would feed the new value back into `previous`.",
                    "Memoised instead: decorate the recursion with "
                    "`@lru_cache(maxsize=None)` from `functools`, or check a module-level "
                    "dict before recursing and store the result before returning it.",
                ],
                "tests": [
                    {"name": "Both agree on the sequence", "code": r'''
_want = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
assert [fib(n) for n in range(10)] == _want, f"fib gave {[fib(n) for n in range(10)]!r}"
assert [fib_naive(n) for n in range(10)] == _want, \
    f"fib_naive gave {[fib_naive(n) for n in range(10)]!r}"
'''},
                    {"name": "fib_naive really is the plain double recursion", "code": r'''
_original = fib_naive
_calls = 0


def _counted(n):
    """Stand in for fib_naive so the recursion is counted as it goes."""
    global _calls
    _calls += 1
    return _original(n)


fib_naive = _counted
try:
    _value = _counted(16)
finally:
    fib_naive = _original
assert _value == 987, f"fib_naive(16) gave {_value!r}, expected 987"
assert _calls > 1000, (
    f"fib_naive(16) made {_calls} calls. The plain recursion makes 3193 of them; "
    "a cache or a loop here removes the cost this half of the lab exists to show")
'''},
                    {"name": "fib(90) is exact, and instant", "code": r'''
import time as _time
_start = _time.time()
_value = fib(90)
_elapsed = _time.time() - _start
assert _value == 2880067194370816120, f"fib(90) gave {_value!r}"
assert _elapsed < 0.5, \
    f"fib(90) took {_elapsed:.2f}s — iterate or memoise instead of recomputing"
'''},
                    {"name": "The fast version holds up well past 90", "code": r'''
assert fib(1) == 1 and fib(2) == 1, "the first two values after the base cases"
assert fib(50) == 12586269025, f"fib(50) gave {fib(50)!r}"
assert fib(300) % 1000000007 == 644264086, \
    "fib(300) is a 63-digit integer, and a float somewhere in the loop will not match it"
'''},
                ],
            }],
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Hash tables",
            "summary": "Separate chaining with resize, and open addressing with tombstones.",
            "concepts": [
                "A hash function must be deterministic, fast and spread keys evenly",
                "FNV-1a: one XOR and one multiply per byte, folded into 32 bits",
                "Collisions are certain — the birthday bound bites long before the table is full",
                "Separate chaining: each bucket is a list; the cost is 1 + load factor on average",
                "Growing at a load factor threshold keeps the expected chain short",
                "Open addressing has no chains, so a deletion must leave a tombstone or break probe chains",
                "Tombstones are cleared only by rehashing, so they count towards the resize trigger",
            ],
            "read": [
                {
                    "title": "From key to slot: what a hash buys and what a collision costs",
                    "minutes": 13,
                    "body": r'''
A library shelves its books by the last two digits of the ISBN. A hundred shelves, and
a request for a book goes straight to one of them: no catalogue, no search, one
arithmetic step from the number on the request slip to the shelf it lives on. That is a
**hash table**. The function from key to shelf is the *hash*, the shelves are an array
of slots, and a lookup costs one evaluation of the function plus whatever it takes to
find the book on a shelf that may hold more than one.

That last clause is the whole subject. Two books with ISBNs ending in 47 land on the
same shelf — a **collision** — and every design decision in a hash table is a decision
about what to do when that happens. The comfortable belief is that collisions are rare
if the table is big and the function is good. It is false, it is false by a margin that
surprises everyone the first time, and the number that says so is derived below.

## A hash function you can compute by hand

A hash function has to be deterministic — the same key must go to the same shelf
tomorrow — fast, and able to *spread* keys so that similar inputs do not pile onto
neighbouring slots. The one this course uses is FNV-1a, because it is three lines long
and has published test vectors you can check against. Start from a fixed offset. For
each byte of the key, XOR the byte into the accumulator and multiply by a fixed prime.
Keep the accumulator to 32 bits.

```python
FNV_OFFSET = 2166136261
FNV_PRIME = 16777619
MASK32 = 0xFFFFFFFF


def fnv1a(text, mask=True):
    """32-bit FNV-1a: one XOR and one multiply per byte."""
    value = FNV_OFFSET
    for byte in text.encode("utf-8"):
        value ^= byte
        value *= FNV_PRIME
        if mask:
            value &= MASK32
    return value


for text in ["", "a", "foobar"]:
    print(f"fnv1a({text!r:>8}) = {fnv1a(text)}")
print("bits in the accumulator without the mask:", fnv1a("foobar", mask=False).bit_length())
print("slot for 'foobar' in a table of 8:", fnv1a("foobar") % 8)
```

The empty string hashes to the offset itself, `"a"` to 3826002220, `"foobar"` to
3214735720, and those are the numbers in the FNV specification; reduced modulo 8,
`foobar` lands in slot 0. The mask is the line
worth staring at. In C the accumulator is a `uint32_t` and the multiplication wraps
around for free — that overflow is not an accident the algorithm tolerates, it is part
of the mixing. Python integers do not overflow; they grow. Leave the mask out and after
six bytes the accumulator is 176 bits long, every test vector fails, and what you have
computed is not FNV-1a at all. `& 0xFFFFFFFF` is how you say *this is a 32-bit
register* in a language that has none.

To turn a hash into a slot, reduce it modulo the capacity. The lab hashes `repr(key)`
rather than `str(key)`, and the reason is small but real: under `str`, the integer 1 and
the string `"1"` are the same text and always share a slot; under `repr` they are `1`
and `'1'`. The table would still be *correct* either way, because slots compare keys
with `==` before believing a match — but a hash that manufactures collisions the keys
did not have is a worse hash.

## Collisions are not a corner case

How many keys can go into $m$ slots before two share one? The instinct says "about
$m$, when the slots run out", or perhaps "about $m/2$". Count pairs instead. With $k$
keys there are $\binom{k}{2} \approx k^{2}/2$ pairs, and under a hash that spreads
evenly, each pair collides with probability $1/m$. The expected number of collisions is

$$\frac{k^{2}}{2m},$$

and that reaches 1 when $k \approx \sqrt{2m}$. Not $m$, not $m/2$: the *square root*.
For 365 slots — the birthday version of the problem — that is about 27, and the exact
calculation puts even odds at 23. Here it is measured rather than trusted:

```python
import random

rng = random.Random(7)
slots, keys, trials = 365, 23, 10_000
collided = 0
for _ in range(trials):
    seen = set()
    for _ in range(keys):
        slot = rng.randrange(slots)
        if slot in seen:
            collided += 1
            break
        seen.add(slot)
print(f"{keys} keys into {slots} slots: a collision in {collided / trials:.1%} of trials")
```

Twenty-three keys, three hundred and sixty-five slots, and a collision in about half of
all trials. Ten thousand slots reach even odds at about 118 keys. So a table holding a
few hundred keys in a few hundred buckets is full of collisions long before it is full
of keys, and an implementation that only handles the empty-slot case passes every small
test and loses data the first week it is deployed. Collision handling is not an
optimisation to add later; it is the data structure.

## Separate chaining, and the load factor

The first answer to a collision is the library's: let a shelf hold more than one book.
Each slot is a list — a **chain** — of `(key, value)` pairs, and a lookup hashes to the
slot and walks the chain comparing keys.

What does that cost? Call the **load factor** $\alpha = n/m$, keys per slot. With an
even spread the average chain has $\alpha$ pairs, so a lookup that *misses* pays one
hash-and-index plus a walk down the whole chain: $1 + \alpha$. A hit stops when it finds
its key, about half way, so it is cheaper — the miss is the dear case, which is the
opposite of most people's guess. Either way the cost is a constant as long as $\alpha$
is, and keeping $\alpha$ bounded is what the resize is for: whenever $n/m$ crosses a
threshold, double $m$ and rehash every pair into the new slots.

```python
FNV_OFFSET = 2166136261
FNV_PRIME = 16777619
MASK32 = 0xFFFFFFFF


def fnv1a(text):
    value = FNV_OFFSET
    for byte in text.encode("utf-8"):
        value = ((value ^ byte) * FNV_PRIME) & MASK32
    return value


class ChainedHashMap:
    """Buckets are lists of (key, value) pairs; doubles past the load factor."""

    def __init__(self, capacity=8, load_factor=0.75):
        self.capacity = capacity
        self.load_factor = load_factor
        self.size = 0
        self.buckets = [[] for _ in range(capacity)]

    def _index(self, key):
        return fnv1a(repr(key)) % self.capacity

    def put(self, key, value):
        bucket = self.buckets[self._index(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1
        if self.size / self.capacity > self.load_factor:
            self._resize(self.capacity * 2)

    def _resize(self, capacity):
        pairs = [pair for bucket in self.buckets for pair in bucket]
        print(f"key #{self.size:>3} pushed the load past {self.load_factor}: "
              f"{self.capacity:>3} -> {capacity:>3} slots, {len(pairs):>3} pairs rehashed")
        self.capacity = capacity
        self.buckets = [[] for _ in range(capacity)]
        for key, value in pairs:
            self.buckets[self._index(key)].append((key, value))

    def get(self, key, default=None):
        for k, value in self.buckets[self._index(key)]:
            if k == key:
                return value
        return default


table = ChainedHashMap()
for i in range(100):
    table.put(i, i * i)
longest = max(len(bucket) for bucket in table.buckets)
print("capacity", table.capacity, "| longest chain", longest, "| get(7) =", table.get(7))
```

From 8 slots with a threshold of 0.75, the seventh key takes the load to $7/8$ and
triggers the first doubling; the thirteenth, twenty-fifth, forty-ninth and
ninety-seventh trigger the rest, and a hundred keys end at 256 slots after exactly five
resizes — the number the lab checks. Rehashing is $O(n)$ when it happens, and it happens
after a number of inserts proportional to $n$, so it amortises the same way the doubling
array did. Note that the check is `>` and not `>=`: six keys in eight slots is *exactly*
0.75 and does not resize, and an off-by-one here gives six resizes rather than five.

## Open addressing, and why deletion is the hard part

The second answer keeps no chains at all. One flat array; when a key's home slot is
taken, try the next slot, and the next, wrapping round — **linear probing**. A lookup
starts at the home slot and walks forward until it finds the key or meets a slot that
has *never been used*, at which point it can stop: if the key existed, the insert that
placed it would have stopped here or earlier.

That stopping rule is what makes deletion dangerous. Suppose three keys hash to slot 3
and probe into 3, 4 and 5. Delete the first one by writing `None` into slot 3, and a
lookup for the second key starts at 3, meets the `None`, and stops — reporting a miss on
a key sitting one slot further on. Nothing is corrupted. The pairs are still there,
visible by eye, and the algorithm can no longer reach them.

```python
FNV_OFFSET = 2166136261
FNV_PRIME = 16777619
MASK32 = 0xFFFFFFFF
TOMBSTONE = object()


def fnv1a(text):
    value = FNV_OFFSET
    for byte in text.encode("utf-8"):
        value = ((value ^ byte) * FNV_PRIME) & MASK32
    return value


def hash_index(key, capacity):
    return fnv1a(repr(key)) % capacity


class ProbingHashMap:
    """Linear probing over one flat list; deletion leaves a tombstone."""

    def __init__(self, capacity=8):
        self.capacity = capacity
        self.slots = [None] * capacity

    def put(self, key, value):
        index = hash_index(key, self.capacity)
        first_tombstone = None
        while self.slots[index] is not None:
            slot = self.slots[index]
            if slot is TOMBSTONE:
                if first_tombstone is None:
                    first_tombstone = index
            elif slot[0] == key:
                self.slots[index] = (key, value)
                return
            index = (index + 1) % self.capacity
        target = index if first_tombstone is None else first_tombstone
        self.slots[target] = (key, value)

    def get(self, key, default=None):
        index = hash_index(key, self.capacity)
        while self.slots[index] is not None:        # stop only at never-used
            slot = self.slots[index]
            if slot is not TOMBSTONE and slot[0] == key:
                return slot[1]
            index = (index + 1) % self.capacity
        return default

    def delete(self, key, marker=TOMBSTONE):
        index = hash_index(key, self.capacity)
        while self.slots[index] is not None:
            slot = self.slots[index]
            if slot is not TOMBSTONE and slot[0] == key:
                self.slots[index] = marker
                return True
            index = (index + 1) % self.capacity
        return False


colliding = [k for k in range(2000) if hash_index(k, 8) == 3][:3]
print("three keys that all want slot 3:", colliding)
for marker, name in ((TOMBSTONE, "tombstone"), (None, "None")):
    table = ProbingHashMap()
    for key in colliding:
        table.put(key, key * 10)
    table.delete(colliding[0], marker)
    found = [table.get(key, "lost") for key in colliding[1:]]
    print(f"delete by writing a {name:<9}: the other two come back as {found}")
```

The fix is a third kind of slot. `None` means *never used*; a **tombstone** means *used
once, then emptied*, and a lookup walks straight through it. Insertion remembers the
first tombstone it passes and, if it reaches a never-used slot without finding the key,
drops the new pair into that tombstone rather than extending the run. The sentinel is a
private `object()` compared with `is`, because a real pair could compare `==` to almost
anything.

Tombstones have a cost of their own, and it is time rather than space. A lookup cannot
stop at one, so every tombstone in a probe run is a slot the lookup has to step over.
Insert a million keys and delete all but ten, and a table that counts only live pairs
looks empty while every lookup still walks a million slots. So the resize trigger counts
tombstones alongside live keys, and a rehash — the only thing that clears them —
rebuilds every probe run from scratch.

## Where it stops holding

Chaining degrades gently: at $\alpha = 2$ the chains average two pairs and nothing much
has changed. Open addressing does not. Occupied slots merge into runs, runs merge into
longer runs, and a miss has to walk to the end of whichever run it lands in. Knuth's
estimates for linear probing say an unsuccessful search costs about

$$\frac{1}{2}\left(1 + \frac{1}{(1 - \alpha)^{2}}\right)$$

probes, and the square in the denominator is the part to remember:

```python
def probes_for_miss(alpha):
    """Knuth's estimate for linear probing: an unsuccessful search."""
    return 0.5 * (1 + 1 / (1 - alpha) ** 2)


def probes_for_hit(alpha):
    """And a successful one, which can stop as soon as it finds its key."""
    return 0.5 * (1 + 1 / (1 - alpha))


for alpha in (0.5, 0.75, 0.875, 0.95):
    print(f"load {alpha:<6} miss {probes_for_miss(alpha):>6.1f}   hit {probes_for_hit(alpha):>5.1f}")
```

At three-quarters full a miss costs 8.5 probes; at seven-eighths, 32.5. Halving the
free space nearly quadrupled the cost, and that is why open-addressed tables give up and
grow at 0.75 while chained ones can run past 1. Two other limits. The hash must be
deterministic *between runs*, and Python's own `hash()` of a string is salted per
process on purpose — a table that persisted slot numbers computed with it would not read
back tomorrow, which is why the lab uses FNV-1a. And a hash table knows nothing about
order: asking for the smallest key, or every key between two bounds, means visiting all
of them, which is the trade the capstone measures against the search tree.

## What you are about to build

The lab is *Chaining, probing and the tombstone problem*. `fnv1a` is checked against
the published vectors, including the 32-bit mask; `hash_index` is
`fnv1a(repr(key)) % capacity`. `ChainedHashMap` must resize on `len / capacity >
load_factor` after a *new* key is added — a hundred keys from capacity 8 is five resizes
ending at 256 — and `ProbingHashMap` must keep one flat `slots` list, leave `TOMBSTONE`
behind on delete, count tombstones towards the resize trigger, and reuse the first
tombstone on an insert. The test that matters is the one traced above: three keys that
collide on slot 3, delete the first, and the other two must still be found. Both maps
are then driven with 4000 random operations against a plain `dict`, mixing integer and
string keys so that `repr` earns its keep. The fill-in-the-blanks unit is a transcript of
that same collision, and the numeric unit is the 8.5 probes.
''',
                },
            ],
            "quiz": {
                "title": "Collisions, tombstones and the load factor",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A linear-probing map deletes a key by writing `None` into its slot instead of a tombstone. What breaks?",
                        "opts": [
                            "Nothing breaks: the table wastes one slot until the next resize clears it",
                            "Inserts start overwriting live pairs, because the free slot is claimed twice",
                            "Keys that probed past that slot become unreachable — lookups stop at a `None`",
                            "Only keys whose home slot *is* that slot are lost; the rest of the chain is fine",
                        ],
                        "a": 2,
                        "whys": [
                            r"It is not a wasted slot, it is silent data loss: pairs that are still physically in the table become unreachable to `get`, which reports a miss for a key sitting three slots away.",
                            r"Inserts are fine — a `None` slot is genuinely free and writing into it is correct. The damage is done to *lookups*, which stop at the first `None` and never see what lies beyond it.",
                            r"A `None` means *nothing was ever placed here*, and a lookup is entitled to stop there.",
                            r"Exactly backwards, which is what makes it worth thinking about. The key whose home slot it was has indeed gone — deliberately. What is lost *as well* are the other keys, the ones that collided and probed past it, and those are the ones that look perfectly healthy in the slot array.",
                        ],
                        "why": r"""
A lookup walks forward from the home slot and stops at the first `None`, because a
`None` means *nothing was ever placed here*, and if the key existed the probe would
have put it here or earlier. Deleting by writing `None` forges that signal. Three keys
land on slot 3 and spill into 4 and 5; delete the one in slot 3 and the other two are
still sitting there, still findable by eye, and completely unreachable by the
algorithm — `get` stops at slot 3 and reports a miss. That is why the lab makes
exactly that arrangement and then asks for the other two.
""",
                    },
                    {
                        "q": "Why do tombstones count towards the resize trigger rather than being ignored?",
                        "opts": [
                            "They occupy memory that the allocator cannot otherwise reclaim",
                            "The load factor is capacity over size, and a tombstone changes the capacity",
                            "Every lookup probes through them, so a sparse table can be as slow as a full one",
                            "Otherwise a resize would never trigger once deletions began to outnumber inserts",
                        ],
                        "a": 2,
                        "whys": [
                            r"The slot exists either way — the slot array was allocated at its full capacity and no tombstone adds a byte to it. What a tombstone costs is time, not space.",
                            r"The load factor is size over capacity, the other way round — and a tombstone changes neither the capacity nor the live count. What it changes is the *probe length*, which is why it has to be counted separately and then added in.",
                            r"Insert a million keys, delete all but ten: the table looks empty and every lookup still walks a million slots.",
                            r"A resize would still trigger on inserts, as usual. The failure is the opposite one: a table being steadily emptied never crosses the trigger at all, so it never rehashes — and a rehash is the only thing that removes a tombstone.",
                        ],
                        "why": r"""
A tombstone is transparent to correctness and completely opaque to cost: `get` may
not stop at one, so it has to keep walking. Insert a million keys and delete all but
ten, and without counting tombstones the table looks 0.00001 full while every lookup
still walks a million slots. Counting them means the table eventually rehashes, and a
rehash is the only thing that clears them, since it rebuilds every probe chain from
scratch. So the count is not bookkeeping about *occupancy* — it is bookkeeping about
*probe length*, which is the quantity the load factor was standing in for all along.
""",
                    },
                    {
                        "q": "A chained table holds $n$ keys in $m$ buckets, with a hash that spreads keys evenly. What is the average cost of an *unsuccessful* lookup?",
                        "opts": [
                            "$n/m$ — the walk down the chain, which is all the work there is",
                            "$1 + n/m$ — one bucket index, plus a chain of average length $n/m$",
                            "$\\log_2(n/m)$ — the chain is kept in key order, so it is binary searched",
                            "$1 + n/(2m)$ — a failed lookup stops half way down the chain on average",
                        ],
                        "a": 1,
                        "whys": [
                            r"The $1$ is not decoration. At a load factor of 0.75 the chain walk averages three-quarters of a comparison, so the hash and the array index *are* most of the cost — and dropping the $1$ makes a lookup in an empty table come out free.",
                            r"One hash and one index, then a walk down a chain of expected length $n/m$.",
                            r"The chains here are unordered lists, so there is nothing to binary search. At an average length below one, ordering them would buy nothing anyway.",
                            r"Half way down is the *successful* case: a hit stops at the key it found, which is on average half the chain. A miss has no early exit — it has to reach the end of the chain to be sure the key is absent, which is why the two costs differ by that factor of two.",
                        ],
                        "why": r"""
The $1$ is the hash and the index into the bucket array, which happens whether the
bucket is empty or not; the $n/m$ is the expected chain length, and a failed lookup
walks all of it. That constant matters more than it looks: when the load factor is
0.75 the walk averages three quarters of a comparison, so the $1$ *is* the cost, and
the whole structure is $O(1)$ only because a resize keeps $n/m$ bounded. Note that
the miss is the more expensive case here, which is the opposite of the intuition most
people bring — a miss cannot stop early, and a hit usually can.
""",
                    },
                    {
                        "q": "`fnv1a` masks the accumulator back to 32 bits after every multiply. Why does that matter in Python particularly?",
                        "opts": [
                            "Python's multiplication slows down on large integers, so the mask is an optimisation",
                            "Without it the accumulator could go negative, and a negative index is legal but wrong",
                            "Python integers grow without bound, so nothing wraps and the published vectors fail",
                            "The mask is what makes the hash deterministic between runs of the interpreter",
                        ],
                        "a": 2,
                        "whys": [
                            r"They do slow down, and that is a consequence rather than the reason — a hash that is fast and wrong is no use to anyone. Without the mask the accumulator is thousands of bits long after a few dozen bytes, and what it computes is not FNV-1a at all.",
                            r"XOR and multiplication of non-negative values never produce a negative, so there is nothing here to guard against. In C the danger runs the other way: a *signed* accumulator would overflow into negative territory, which is why the reference uses `uint32_t`.",
                            r"`& 0xFFFFFFFF` is how you say *this is a 32-bit register* in a language that has none.",
                            r"Determinism comes from the algorithm being a pure function of the input bytes; the mask neither adds it nor could. It is Python's own built-in `hash()` that varies between runs, which is exactly why the lab does not use it.",
                        ],
                        "why": r"""
In C the accumulator is a `uint32_t` and the wrap-around is free — it is what the
hardware does, and the algorithm was designed around it. Python has arbitrary-precision
integers, so the same code without the mask produces a number thousands of bits long
after a few dozen bytes, and every published test vector fails. The overflow is not an
accident FNV-1a tolerates; it is part of the mixing, and a language that refuses to
overflow has to be told to.
""",
                    },
                    {
                        "q": "`hash_index` hashes `repr(key)` rather than `str(key)`. What does that buy?",
                        "opts": [
                            "`repr` is faster, since it does not have to format the value for a human reader",
                            "`str` is not defined for tuples, so `repr` is the only option for compound keys",
                            "`repr(1)` is `1` and `repr(\"1\")` is `'1'`, so the two do not collide by default",
                            "`repr` is injective, so two different keys can never be given the same slot",
                        ],
                        "a": 2,
                        "whys": [
                            r"`repr` usually does slightly more work, not less — it has quoting and escaping to attend to. Neither is on the hot path in any case; the hash then walks every byte of whatever came back.",
                            r"""`str` is perfectly well defined for tuples: `str((1, 2))` is `'(1, 2)'`. Both calls return `str` objects, which is why `fnv1a` calls `.encode("utf-8")` on the result of either one.""",
                            r'Under `str` the integer 1 and the string "1" are the same text, so they always land in the same slot.',
                            r"Distinct text does not mean distinct slot. A 32-bit hash of unbounded input *must* collide — that is what the buckets are for. What `repr` buys is only that it does not manufacture collisions that were not there in the keys.",
                        ],
                        "why": r"""
Neither choice is *incorrect* — the buckets compare keys with `==`, so a collision
between the integer 1 and the string "1" is resolved correctly either way. It is a
quality-of-hash question: `str` maps genuinely different keys onto identical text and
manufactures collisions the table then has to work through, so a mixed-type key space
degrades measurably for no reason at all. That is the distinction worth carrying:
correctness comes from the comparison, and performance comes from the hash, and they
are two separate obligations that it is easy to conflate.
""",
                    },
                    {
                        "q": "A table of 365 slots is filled with keys hashed uniformly at random. Roughly how many keys go in before a collision is more likely than not?",
                        "opts": [
                            "About 183 — half the slots, which is when they begin to run out",
                            "About 23 — roughly the square root of the number of slots",
                            "About 365 — a collision is certain only once every slot has been claimed",
                            "About 100 — collisions become likely at roughly a quarter of the slots",
                        ],
                        "a": 1,
                        "whys": [
                            r"Half full is where a *particular* slot becomes likely to be occupied. A collision needs only *some pair* of keys to agree, and 23 keys already make 253 pairs — which is why the threshold is quadratically smaller than the intuition.",
                            r"$\binom{23}{2} = 253$ pairs, each colliding with probability $1/365$.",
                            r"Certain, yes — but long past likely. By the time 365 keys are in, a uniform hash has produced hundreds of collisions. The pigeonhole bound is the last thing to bite, never the first.",
                            r"The threshold does not scale with the table at all; it scales with the table's *square root*. Ten thousand slots reach even odds at about 118 keys, not 2500 — the fraction gets smaller as the table gets bigger.",
                        ],
                        "why": r"""
The count of *pairs* is what matters, and it grows quadratically: $k$ keys make
$\binom{k}{2}$ pairs, each of which collides with probability $1/m$. Even odds arrive
when that product reaches about 1, which is at $k \approx 1.18\sqrt{m}$ — 23 keys in
365 slots, 118 keys in ten thousand, 77000 in a 32-bit space.

This is why collision handling is not an optimisation to add later. A chained table
holding a few hundred keys in a few hundred buckets is already full of collisions
before it is anywhere near full of keys, and an implementation that only handles the
empty-bucket case will pass every small test and lose data in production. The load
factor governs how *long* the chains get; the birthday bound governs the fact that
there are chains at all.
""",
                    },
                ],
            },
            "blanks": {
                "title": "A session with three keys that all want slot 3",
                "minutes": 9,
                "lang": "text",
                "caption": "a REPL transcript — the outputs are the holes",
                "brief": r"""
Three three-letter words that all hash to the same slot of an eight-slot table, so
the probe chain is forced and nothing is left to chance. The transcript below is
real: fill in what the interpreter printed.

`slots` is the flat list of slots. A slot is `None` when it has never been used,
`TOMBSTONE` when a key was deleted from it, and a `(key, value)` pair otherwise.
""",
                "listing": r'''
>>> table = ProbingHashMap(capacity=8)
>>> [hash_index(key, 8) for key in ("ada", "gnu", "ink")]
[3, 3, 3]
>>> for value, key in enumerate(("ada", "gnu", "ink"), 1):
...     table.put(key, value)
...
>>> [i for i, slot in enumerate(table.slots) if slot is not None]
___
>>> table.delete("ada")
True
>>> table.slots[3] is TOMBSTONE
___
>>> table.get("ink", "gone")
___
>>> table.get("ada", "gone")
___
>>> len(table), table.tombstones
___
>>> table.put("ada", 99)
>>> table.slots[3]
___
''',
                "blanks": [
                    {
                        "prompt": "Where did the three pairs end up?",
                        "hole": "?",
                        "opts": ["[3, 4, 5]", "[0, 1, 2]", "[3, 4]", "[3]"],
                        "a": 0,
                        "why": "`ada` takes its home slot 3; `gnu` finds it occupied and probes one along to 4; `ink` probes past both to 5. Linear probing means the chain occupies a contiguous run starting at the home slot.",
                        "whys": [
                            "`ada` takes its home slot 3; `gnu` finds it occupied and probes one along to 4; `ink` probes past both to 5. Linear probing means the chain occupies a contiguous run starting at the home slot.",
                            "Slots are chosen by the hash, not by insertion order, and all three keys hash to 3. A table that filled from the front would be a list with extra steps.",
                            "Two slots would mean one of the three keys was dropped or replaced. All three keys are distinct, so all three are stored.",
                            "Only one slot would be filled if later keys overwrote earlier ones — which is what a table with no probing at all would do, and it would lose two of the three pairs.",
                        ],
                    },
                    {
                        "prompt": "What did the deletion leave behind?",
                        "hole": "?",
                        "opts": ["False", "True"],
                        "a": 1,
                        "why": "Slot 3 now holds the tombstone sentinel rather than `None`. That distinction is the entire mechanism: `None` means never used, and a lookup is allowed to stop there.",
                        "whys": [
                            "A `False` here would mean the slot held `None` or a live pair. It holds neither: an open-addressed table cannot write `None` on a delete without cutting the probe chain behind it.",
                            "Slot 3 now holds the tombstone sentinel rather than `None`. That distinction is the entire mechanism: `None` means never used, and a lookup is allowed to stop there.",
                        ],
                    },
                    {
                        "prompt": "`ink` was reached by probing past `ada`. Is it still reachable?",
                        "hole": "?",
                        "opts": ["None", "'gone'", "3", "1"],
                        "a": 2,
                        "why": "`ink` was stored with the value 3. The lookup starts at slot 3, meets the tombstone and keeps walking, passes `gnu` in slot 4 and finds `ink` in slot 5 — which is precisely what the tombstone was left there to permit.",
                        "whys": [
                            "`get` returns its default on a miss, and the default supplied here is a string. `None` would come back only from a call that left the default out.",
                            "This is what the same session would print if the delete had written `None` into slot 3: the lookup would stop dead at the first never-used slot and report a miss on a key that is sitting two slots further on.",
                            "`ink` was stored with the value 3. The lookup starts at slot 3, meets the tombstone and keeps walking, passes `gnu` in slot 4 and finds `ink` in slot 5 — which is precisely what the tombstone was left there to permit.",
                            "1 was `ada`'s value, and `ada` is the key that was deleted. The values were assigned in order, so `gnu` is 2 and `ink` is 3.",
                        ],
                    },
                    {
                        "prompt": "And the key that was deleted?",
                        "hole": "?",
                        "opts": ["None", "KeyError", "1", "'gone'"],
                        "a": 3,
                        "why": "The lookup walks the chain, skips the tombstone rather than stopping at it, reaches slot 6 which has never been used, and returns the default. A tombstone keeps other keys reachable without making the deleted one come back.",
                        "whys": [
                            "The default was given as a string, so a miss returns that string. `None` is what a bare `get(key)` would return.",
                            "`get` never raises on a miss; that is what distinguishes it from `__getitem__`, and it is why the default parameter exists.",
                            "The value 1 is still physically in the table's memory only in the sense that nothing overwrote it — the slot holds the sentinel now, and a lookup that returned the old value would make `delete` meaningless.",
                            "The lookup walks the chain, skips the tombstone rather than stopping at it, reaches slot 6 which has never been used, and returns the default. A tombstone keeps other keys reachable without making the deleted one come back.",
                        ],
                    },
                    {
                        "prompt": "Live keys, and tombstones.",
                        "hole": "?",
                        "opts": ["(3, 0)", "(2, 1)", "(2, 0)", "(3, 1)"],
                        "a": 1,
                        "why": "Two live pairs are left and one tombstone stands in for the third. They are counted separately because they mean different things — but the resize trigger adds them together, since a lookup pays for both.",
                        "whys": [
                            "Three live keys would mean the delete had not taken effect. It returned `True`, so a pair was genuinely removed.",
                            "Two live pairs are left and one tombstone stands in for the third. They are counted separately because they mean different things — but the resize trigger adds them together, since a lookup pays for both.",
                            "The length is right and the tombstone count is not: deleting from an open-addressed table always leaves one behind, and only a rehash clears it.",
                            "This has the deleted key both still counted and marked as removed, which no single delete can produce.",
                        ],
                    },
                    {
                        "prompt": "Reinserting the deleted key — where does it land?",
                        "hole": "?",
                        "opts": ["('ada', 1)", "('gnu', 2)", "('ada', 99)", "None"],
                        "a": 2,
                        "why": "`put` remembers the first tombstone it passes and, on reaching a never-used slot without finding the key, drops the pair into that remembered slot rather than the empty one. The chain gets shorter instead of longer, and the tombstone count goes back to 0.",
                        "whys": [
                            "The old value does not come back — the pair was removed, and this is a fresh insertion with a new value.",
                            "`gnu` is in slot 4 and nothing moves it. Slots are never shuffled by an insertion; only a rehash relocates anything.",
                            "`put` remembers the first tombstone it passes and, on reaching a never-used slot without finding the key, drops the pair into that remembered slot rather than the empty one. The chain gets shorter instead of longer, and the tombstone count goes back to 0.",
                            "The slot would still hold the sentinel if `put` had ignored the tombstone and used slot 6 instead. That version is correct but leaks: tombstones then only ever accumulate, and the table rehashes far sooner than it needs to.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "What a load factor of 0.75 actually costs",
                "minutes": 7,
                "brief": r"""
Chaining degrades gently as a table fills: the average chain is $\alpha$ long and
that is that. Open addressing does not, because occupied slots merge into runs and
runs merge into longer runs — primary clustering. Knuth's estimates for linear
probing put a number on it, and the number is the reason 0.75 is where almost every
open-addressed table gives up and grows.
""",
                "prompt": "How many slots does an **unsuccessful** lookup probe on average when the table is three-quarters full?",
                "note": "Use the estimate quoted in the table below. Two decimal places is plenty.",
                "figure": r"""
A linear-probing table of `capacity` slots holding `n` live pairs, with load factor
$\alpha = n/\text{capacity}$. A lookup starts at the key's home slot and walks
forward until it meets a slot that has never been used — so the cost of a miss is the
length of whatever run of occupied slots it happens to land in.
""",
                "given": [
                    {"label": "Load factor $\\alpha$", "value": "0.75"},
                    {"label": "Unsuccessful search", "value": "$\\frac{1}{2}\\left(1 + \\frac{1}{(1-\\alpha)^2}\\right)$"},
                    {"label": "Successful search", "value": "$\\frac{1}{2}\\left(1 + \\frac{1}{1-\\alpha}\\right)$"},
                    {"label": "Probing", "value": "linear, step 1"},
                ],
                "answer": 8.5,
                "tol": 0.05,
                "unit": "probes",
                "aside": "At $\\alpha = 0.875$ the same formula gives 32.5. Halving the free space nearly quadruples the cost of a miss.",
                "hint": "$1 - \\alpha$ is 0.25, and it is squared before it goes underneath the 1.",
                "wrong": "2.5 is the figure for a successful search. A miss is far dearer, because a hit can stop as soon as it finds its key while a miss has to walk the run to its end.",
                "why": r"""
$1 - \alpha = 0.25$; squared that is $0.0625$; and $1/0.0625 = 16$. So the estimate is
$\frac{1}{2}(1 + 16) = 8.5$ probes for a miss, against $\frac{1}{2}(1 + 4) = 2.5$ for
a hit.

The square is the part worth remembering. Cost does not rise in proportion to how
full the table is; it rises with the *square* of the reciprocal of the free space,
because a slot filling in between two runs does not extend a run by one — it joins
two runs into one long one. That is primary clustering, and it is why a chained table
can be run at a load factor above 1 quite happily while an open-addressed one cannot.
""",
            },
            "lab": {
                "title": "Chaining, probing and the tombstone problem",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
Two maps with the same behaviour and completely different failure modes.

## `fnv1a(text)`

The 32-bit FNV-1a hash. Start from `2166136261`; for each **byte** of
`text.encode("utf-8")`, XOR it into the accumulator and then multiply by
`16777619`, masking back to 32 bits every time.

```text
fnv1a("")       -> 2166136261
fnv1a("a")      -> 3826002220
fnv1a("foobar") -> 3214735720
```

## `hash_index(key, capacity)`

`fnv1a(repr(key)) % capacity`. Using `repr` keeps `1` and `"1"` apart.

## `ChainedHashMap(capacity=8, load_factor=0.75)`

Buckets are plain lists of `(key, value)` pairs. `ValueError` for a capacity
below 1 or a load factor outside `0 < f <= 1`.

- `put(key, value)` — replaces the value if the key is already there
- `get(key, default=None)`, `__getitem__` (raises `KeyError`), `__contains__`,
  `__len__`
- `delete(key)` — `True` if something went, `False` otherwise
- `keys()`, `items()` — any order
- `self.capacity` and `self.resizes`

After inserting a **new** key, resize to twice the capacity whenever
`len(self) / capacity > load_factor`, rehashing everything. From the default
capacity of 8, inserting 100 distinct keys must trigger exactly **5 resizes**
and end at capacity **256**.

## `ProbingHashMap(capacity=8, load_factor=0.75)`

One flat `self.slots` list. A slot is `None` when it has never been used, the
sentinel `TOMBSTONE` when a key was deleted from it, or a `(key, value)` pair.
Probing is linear: try `hash_index(key, capacity)`, then the next slot, wrapping
round.

- `put` — walk the probe chain. Remember the **first** tombstone you pass; if
  you reach a never-used slot without finding the key, store the pair in that
  remembered tombstone if there was one, otherwise in the empty slot.
- `get` — walk the chain, skipping tombstones, and stop at the first never-used
  slot. Stopping at a tombstone instead would lose keys.
- `delete` — replace the pair with `TOMBSTONE` and count it in
  `self.tombstones`.
- Resize (doubling, and dropping every tombstone) when
  `(len(self) + self.tombstones) / capacity > load_factor`.

The check that matters: put three keys that hash to the same slot, delete the
first, and the other two must still be found.
''',
                "files": [{"name": "main.py", "content": r'''
FNV_OFFSET = 2166136261
FNV_PRIME = 16777619
MASK32 = 0xFFFFFFFF

TOMBSTONE = object()


def fnv1a(text):
    """The 32-bit FNV-1a hash of a string."""
    # your code here


def hash_index(key, capacity):
    """Which slot a key belongs in."""
    # your code here


class ChainedHashMap:
    """A hash map whose buckets are lists of (key, value) pairs."""

    def __init__(self, capacity=8, load_factor=0.75):
        # your code here
        pass

    def __len__(self):
        # your code here
        return 0

    def __contains__(self, key):
        # your code here
        return False

    def __getitem__(self, key):
        """The value, or KeyError."""
        # your code here

    def get(self, key, default=None):
        """The value, or default."""
        # your code here

    def put(self, key, value):
        """Insert or replace, resizing when the load factor is exceeded."""
        # your code here

    def delete(self, key):
        """True when a pair was removed."""
        # your code here

    def keys(self):
        """Every key, in any order."""
        # your code here

    def items(self):
        """Every (key, value) pair, in any order."""
        # your code here


class ProbingHashMap:
    """An open-addressed hash map using linear probing and tombstones."""

    def __init__(self, capacity=8, load_factor=0.75):
        # your code here
        pass

    def __len__(self):
        # your code here
        return 0

    def __contains__(self, key):
        # your code here
        return False

    def __getitem__(self, key):
        """The value, or KeyError."""
        # your code here

    def get(self, key, default=None):
        """The value, or default."""
        # your code here

    def put(self, key, value):
        """Insert or replace, reusing the first tombstone on the probe chain."""
        # your code here

    def delete(self, key):
        """Leave a tombstone behind so the probe chain survives."""
        # your code here

    def keys(self):
        """Every key, in any order."""
        # your code here

    def items(self):
        """Every (key, value) pair, in any order."""
        # your code here


table = ChainedHashMap()
for i in range(100):
    table.put(i, i * i)
print(len(table), table.capacity, table.resizes)
print(table.get(7), table.get("missing", "-"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
FNV_OFFSET = 2166136261
FNV_PRIME = 16777619
MASK32 = 0xFFFFFFFF

TOMBSTONE = object()


def fnv1a(text):
    """The 32-bit FNV-1a hash of a string."""
    value = FNV_OFFSET
    for byte in text.encode("utf-8"):
        value ^= byte
        value = (value * FNV_PRIME) & MASK32
    return value


def hash_index(key, capacity):
    """Which slot a key belongs in."""
    return fnv1a(repr(key)) % capacity


class ChainedHashMap:
    """A hash map whose buckets are lists of (key, value) pairs."""

    def __init__(self, capacity=8, load_factor=0.75):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if not 0 < load_factor <= 1:
            raise ValueError("the load factor must be in (0, 1]")
        self.capacity = capacity
        self.load_factor = load_factor
        self.resizes = 0
        self._size = 0
        self._buckets = [[] for _ in range(capacity)]

    def __len__(self):
        return self._size

    def _bucket(self, key):
        return self._buckets[hash_index(key, self.capacity)]

    def __contains__(self, key):
        return any(k == key for k, _ in self._bucket(key))

    def __getitem__(self, key):
        """The value, or KeyError."""
        for k, value in self._bucket(key):
            if k == key:
                return value
        raise KeyError(key)

    def get(self, key, default=None):
        """The value, or default."""
        for k, value in self._bucket(key):
            if k == key:
                return value
        return default

    def put(self, key, value):
        """Insert or replace, resizing when the load factor is exceeded."""
        bucket = self._bucket(key)
        for position, (k, _) in enumerate(bucket):
            if k == key:
                bucket[position] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self._size / self.capacity > self.load_factor:
            self._resize(self.capacity * 2)

    def _resize(self, capacity):
        pairs = self.items()
        self.capacity = capacity
        self._buckets = [[] for _ in range(capacity)]
        for key, value in pairs:
            self._buckets[hash_index(key, capacity)].append((key, value))
        self.resizes += 1

    def delete(self, key):
        """True when a pair was removed."""
        bucket = self._bucket(key)
        for position, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(position)
                self._size -= 1
                return True
        return False

    def keys(self):
        """Every key, in any order."""
        return [key for bucket in self._buckets for key, _ in bucket]

    def items(self):
        """Every (key, value) pair, in any order."""
        return [pair for bucket in self._buckets for pair in bucket]


class ProbingHashMap:
    """An open-addressed hash map using linear probing and tombstones."""

    def __init__(self, capacity=8, load_factor=0.75):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if not 0 < load_factor <= 1:
            raise ValueError("the load factor must be in (0, 1]")
        self.capacity = capacity
        self.load_factor = load_factor
        self.resizes = 0
        self.tombstones = 0
        self._size = 0
        self.slots = [None] * capacity

    def __len__(self):
        return self._size

    def _find(self, key):
        """The slot holding key, or None once a never-used slot is reached."""
        index = hash_index(key, self.capacity)
        for _ in range(self.capacity):
            slot = self.slots[index]
            if slot is None:
                return None
            if slot is not TOMBSTONE and slot[0] == key:
                return index
            index = (index + 1) % self.capacity
        return None

    def __contains__(self, key):
        return self._find(key) is not None

    def __getitem__(self, key):
        """The value, or KeyError."""
        index = self._find(key)
        if index is None:
            raise KeyError(key)
        return self.slots[index][1]

    def get(self, key, default=None):
        """The value, or default."""
        index = self._find(key)
        return default if index is None else self.slots[index][1]

    def put(self, key, value):
        """Insert or replace, reusing the first tombstone on the probe chain."""
        index = hash_index(key, self.capacity)
        first_tombstone = None
        for _ in range(self.capacity):
            slot = self.slots[index]
            if slot is None:
                break
            if slot is TOMBSTONE:
                if first_tombstone is None:
                    first_tombstone = index
            elif slot[0] == key:
                self.slots[index] = (key, value)
                return
            index = (index + 1) % self.capacity
        if first_tombstone is not None:
            self.slots[first_tombstone] = (key, value)
            self.tombstones -= 1
        else:
            self.slots[index] = (key, value)
        self._size += 1
        if (self._size + self.tombstones) / self.capacity > self.load_factor:
            self._resize(self.capacity * 2)

    def _resize(self, capacity):
        pairs = self.items()
        self.capacity = capacity
        self.slots = [None] * capacity
        self.tombstones = 0
        for key, value in pairs:
            index = hash_index(key, capacity)
            while self.slots[index] is not None:
                index = (index + 1) % capacity
            self.slots[index] = (key, value)
        self.resizes += 1

    def delete(self, key):
        """Leave a tombstone behind so the probe chain survives."""
        index = self._find(key)
        if index is None:
            return False
        self.slots[index] = TOMBSTONE
        self.tombstones += 1
        self._size -= 1
        return True

    def keys(self):
        """Every key, in any order."""
        return [slot[0] for slot in self.slots
                if slot is not None and slot is not TOMBSTONE]

    def items(self):
        """Every (key, value) pair, in any order."""
        return [slot for slot in self.slots
                if slot is not None and slot is not TOMBSTONE]


table = ChainedHashMap()
for i in range(100):
    table.put(i, i * i)
print(len(table), table.capacity, table.resizes)
print(table.get(7), table.get("missing", "-"))
'''}],
                "hints": [
                    "`text.encode(\"utf-8\")` gives you an iterable of integers, so the FNV loop is `value ^= byte` then `value = (value * FNV_PRIME) & MASK32`.",
                    "Write `_resize` as: take a snapshot of the pairs, replace the storage with a bigger empty one, and re-`put` every pair. Never rehash in place.",
                    "In the probing map, compare tombstones with `is`, not `==` — `slot is TOMBSTONE` — because a real pair could compare equal to almost anything.",
                    "`get` on a probing map must stop only at a `None` slot. If it stopped at a tombstone, every key that had probed past a since-deleted slot would vanish.",
                ],
                "tests": [
                    {"name": "FNV-1a matches the published vectors", "code": r'''
for _text, _want in [("", 2166136261), ("a", 3826002220), ("b", 3876335077),
                     ("foobar", 3214735720), ("hello", 1335831723)]:
    _got = fnv1a(_text)
    assert _got == _want, f"fnv1a({_text!r}) gave {_got!r}, expected {_want}"
assert fnv1a("abc") == fnv1a("abc"), "a hash function must be deterministic"
assert 0 <= fnv1a("anything") <= 0xFFFFFFFF, "the result must stay inside 32 bits"
for _cap in (1, 8, 97):
    for _key in (0, 5, "x", (1, 2)):
        assert 0 <= hash_index(_key, _cap) < _cap, f"hash_index({_key!r}, {_cap}) out of range"
assert repr(1) != repr("1"), "hashing repr(key) is what keeps 1 and '1' apart"
'''},
                    {"name": "Chained map: put, get, replace, delete", "code": r'''
_m = ChainedHashMap()
assert len(_m) == 0 and _m.get("nope") is None, "a fresh map is empty"
assert _m.get("nope", "fallback") == "fallback", "get takes a default"
try:
    _m["nope"]
    assert False, "__getitem__ on a missing key should raise KeyError"
except KeyError:
    pass
_m.put("a", 1)
_m.put("b", 2)
assert len(_m) == 2 and _m["a"] == 1 and _m["b"] == 2, f"items are {_m.items()!r}"
_m.put("a", 99)
assert _m["a"] == 99, "put must replace the value for an existing key"
assert len(_m) == 2, f"replacing must not grow the map; length is {len(_m)}"
assert ("a" in _m) and ("zz" not in _m), "__contains__ is wrong"
assert _m.delete("a") is True and _m.delete("a") is False, "the second delete finds nothing"
assert len(_m) == 1 and sorted(_m.keys()) == ["b"], f"keys are {_m.keys()!r}"
for _bad in [(0, 0.75), (8, 0), (8, 1.5), (-1, 0.5)]:
    try:
        ChainedHashMap(*_bad)
        assert False, f"ChainedHashMap{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Chained map resizes on the load factor", "code": r'''
_m = ChainedHashMap()
assert _m.capacity == 8 and _m.resizes == 0, "the default capacity is 8"
for _i in range(6):
    _m.put(_i, _i * _i)
assert _m.capacity == 8, f"6/8 is exactly the load factor, so no resize yet; got {_m.capacity}"
_m.put(6, 36)
assert _m.capacity == 16 and _m.resizes == 1, \
    f"the 7th key takes the load past 0.75; got capacity {_m.capacity}, {_m.resizes} resizes"
for _i in range(7, 100):
    _m.put(_i, _i * _i)
assert len(_m) == 100, f"length is {len(_m)}, expected 100"
assert _m.capacity == 256, f"100 keys from capacity 8 ends at 256, got {_m.capacity}"
assert _m.resizes == 5, f"that is 5 doublings, got {_m.resizes}"
for _i in range(100):
    assert _m[_i] == _i * _i, f"key {_i} was lost or corrupted by a resize"
assert sorted(_m.keys()) == list(range(100)), "every key must survive rehashing"
'''},
                    {"name": "Probing map: the same contract", "code": r'''
_p = ProbingHashMap()
assert len(_p) == 0 and _p.get(1) is None, "a fresh map is empty"
try:
    _p[1]
    assert False, "__getitem__ on a missing key should raise KeyError"
except KeyError:
    pass
for _i in range(5):
    _p.put(_i, _i * 10)
assert len(_p) == 5 and _p[3] == 30, f"items are {sorted(_p.items())!r}"
_p.put(3, 999)
assert _p[3] == 999 and len(_p) == 5, "put must replace rather than duplicate"
assert (3 in _p) and (77 not in _p), "__contains__ is wrong"
assert _p.delete(3) is True and _p.delete(3) is False, "the second delete finds nothing"
assert len(_p) == 4 and _p.get(3, "gone") == "gone", "the deleted key must be unreachable"
assert sorted(_p.keys()) == [0, 1, 2, 4], f"keys are {sorted(_p.keys())!r}"
assert _p.tombstones == 1, f"one deletion leaves one tombstone, got {_p.tombstones}"
'''},
                    {"name": "Tombstones keep the probe chain alive", "code": r'''
_p = ProbingHashMap(capacity=8)
_target = 3
_colliding = [_k for _k in range(2000) if hash_index(_k, 8) == _target][:3]
assert len(_colliding) == 3, "expected to find three colliding keys to test with"
_first, _second, _third = _colliding
for _k in _colliding:
    _p.put(_k, _k)
assert _p.slots[_target][0] == _first, "the first key belongs in its home slot"
assert _p.slots[(_target + 1) % 8][0] == _second, "the second probes one along"
assert _p.slots[(_target + 2) % 8][0] == _third, "the third probes two along"
assert _p.delete(_first) is True, "deleting the head of the chain"
assert _p.slots[_target] is TOMBSTONE, "the vacated slot must hold the tombstone sentinel"
assert _p[_second] == _second, "the second key must still be reachable past the tombstone"
assert _p[_third] == _third, "and so must the third — this is what tombstones are for"
_p.put(_first, 42)
assert _p.slots[_target] == (_first, 42), \
    f"reinserting should reuse the tombstone at {_target}, got {_p.slots[_target]!r}"
assert _p.tombstones == 0 and len(_p) == 3, \
    f"the tombstone is spent; got {_p.tombstones} tombstones and length {len(_p)}"
'''},
                    {"name": "Probing map resizes and clears its tombstones", "code": r'''
_p = ProbingHashMap()
for _i in range(100):
    _p.put(_i, _i * _i)
assert len(_p) == 100 and _p.capacity == 256, \
    f"expected 100 keys at capacity 256, got {len(_p)} at {_p.capacity}"
assert _p.tombstones == 0, "no deletions yet, so no tombstones"
for _i in range(0, 100, 2):
    assert _p.delete(_i) is True, f"deleting {_i} should have worked"
assert len(_p) == 50 and _p.tombstones == 50, \
    f"got {len(_p)} live keys and {_p.tombstones} tombstones, expected 50 and 50"
for _i in range(1, 100, 2):
    assert _p[_i] == _i * _i, f"odd key {_i} was lost behind a tombstone"
_resizes_before = _p.resizes
for _i in range(100, 400):
    _p.put(_i, _i * _i)
assert _p.resizes > _resizes_before, "adding another 300 keys must have grown the table"
assert _p.tombstones == 0, f"a rehash discards tombstones, got {_p.tombstones}"
for _i in range(1, 100, 2):
    assert _p[_i] == _i * _i, f"odd key {_i} did not survive the rehash"
for _i in range(0, 100, 2):
    assert _i not in _p, f"deleted key {_i} came back from the dead"
'''},
                    {"name": "Both maps agree with a dict under random traffic", "code": r'''
import random as _random
for _cls in (ChainedHashMap, ProbingHashMap):
    _rng = _random.Random(7)
    _m = _cls()
    _ref = {}
    for _step in range(4000):
        _key = _rng.choice([_rng.randint(0, 200), str(_rng.randint(0, 200))])
        _action = _rng.random()
        if _action < 0.6:
            _value = _rng.randint(0, 10 ** 6)
            _m.put(_key, _value)
            _ref[_key] = _value
        elif _action < 0.8:
            assert _m.delete(_key) == (_key in _ref), \
                f"{_cls.__name__}.delete({_key!r}) disagreed with the reference dict"
            _ref.pop(_key, None)
        else:
            assert _m.get(_key, "MISS") == _ref.get(_key, "MISS"), \
                f"{_cls.__name__}.get({_key!r}) gave {_m.get(_key, 'MISS')!r}"
    assert len(_m) == len(_ref), f"{_cls.__name__} holds {len(_m)} keys, the dict holds {len(_ref)}"
    assert sorted(_m.items(), key=repr) == sorted(_ref.items(), key=repr), \
        f"{_cls.__name__} and the reference dict hold different pairs"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Heaps and comparison sorting",
            "summary": "A binary heap in an array, then merge, quick and heap sort with a stability test.",
            "concepts": [
                "A complete binary tree fits in an array: children of i are 2i+1 and 2i+2",
                "The heap property is local, so push and pop are O(log n) sift operations",
                "Bottom-up heapify is O(n), not O(n log n) — most nodes are near the leaves",
                "Merge sort is stable and O(n log n) always, at the cost of O(n) extra space",
                "Quicksort is in-place and fast in practice; pivot choice is what saves it",
                "Three-way partitioning makes runs of equal keys cheap instead of quadratic",
                "Stability is a property of the algorithm, not the data — heap and quick sorts lose it",
            ],
            "read": [
                {
                    "title": "A tree in an array, and what each sort pays for its speed",
                    "minutes": 14,
                    "body": r'''
An emergency department does not see patients in the order they arrive. Every arrival
is given a priority, and the next patient seen is the most urgent one waiting, whoever
came through the door first. The structure behind that desk needs two operations, and
they pull in opposite directions: *add a patient* with any priority, and *take the most
urgent*. A sorted list makes the take one step and every arrival an $O(n)$ shuffle; an
unsorted one makes arrivals one step and every take a full scan. A **binary heap** does both in $O(\log n)$, and it
manages that by refusing to keep the whole order. It keeps only what is needed to know
who is next.

The rule is local and it is the whole structure: in a min-heap, every node's key is no
larger than its children's. Nothing is said about siblings, nothing about cousins, and
so the array is very far from sorted — but the smallest key has no parent it could be
larger than, so it must be at the root, and that is the one fact the desk needs.

## A tree that lives in an array

A heap is a **complete** binary tree — every level full except the last, which fills
from the left — and a complete tree can be stored in a flat array with no references at
all. Number the nodes level by level, left to right, from 0: the root is 0, its children
are 1 and 2, their children are 3 to 6. The pattern that falls out is that the children of index
$i$ are $2i + 1$ and $2i + 2$, and the parent of $i$ is $\lfloor (i - 1) / 2 \rfloor$,
where the floor is what sends both children back to the same parent. Check it at the
root before believing it:

```python
heap = [1, 3, 2, 7, 4, 9, 5, 8]
for i in range(4):
    kids = [heap[j] for j in (2 * i + 1, 2 * i + 2) if j < len(heap)]
    print(f"index {i} holds {heap[i]}, its children hold {kids}")
print("parent of index 7 is index", (7 - 1) // 2, "holding", heap[(7 - 1) // 2])
```

That is the entire data structure: a list and arithmetic on indices, in one contiguous
block of memory — which after the sequences module you know is worth a great deal.

## Sift up, sift down

Adding an item: append it at the end, which keeps the tree complete, and then repair the
one place the heap rule might now be broken — between the new item and its parent. If
the new item is smaller, swap them and look at the new parent. This **sift up** climbs
at most one path from leaf to root, and a complete tree of $n$ nodes has
$\lfloor \log_2 n \rfloor$ levels below the root, so it is $O(\log n)$.

Taking the smallest: the root is the answer, but removing it leaves a hole at the top.
Fill the hole with the *last* item of the array — which again keeps the tree complete —
and repair downward: compare the item with its two children, swap with the smaller if
that child is smaller, and continue from where it landed. **Sift down** descends one
path, and it is the same $O(\log n)$.

```python
class MinHeap:
    """A binary min-heap in a flat list, root at index 0."""

    def __init__(self, items=None):
        self.data = list(items or [])
        for index in reversed(range(len(self.data) // 2)):
            self._sift_down(index)

    def _sift_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self.data[index] < self.data[parent]:
                self.data[index], self.data[parent] = self.data[parent], self.data[index]
                index = parent
            else:
                return

    def _sift_down(self, index):
        size = len(self.data)
        while True:
            left, right, smallest = 2 * index + 1, 2 * index + 2, index
            if left < size and self.data[left] < self.data[smallest]:
                smallest = left
            if right < size and self.data[right] < self.data[smallest]:
                smallest = right
            if smallest == index:
                return
            self.data[index], self.data[smallest] = self.data[smallest], self.data[index]
            index = smallest

    def push(self, item):
        self.data.append(item)
        self._sift_up(len(self.data) - 1)

    def pop(self):
        smallest = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0)
        return smallest


heap = MinHeap()
for value in [5, 9, 3, 7, 1, 8]:
    heap.push(value)
    print(f"push {value}: {heap.data}")
print("pop ->", heap.pop(), "leaving", heap.data)
```

Follow the trace and notice that the array is never sorted: after six pushes it reads
`[1, 3, 5, 9, 7, 8]`, with 9 sitting before 7. Every parent is smaller than its children
and nothing more is true, and nothing more needs to be. The mistake to name here is in
`pop`: the item moved into the root must be the *last* one, not the smaller child.
Promoting a child leaves a hole further down that has to be filled in turn, and the
completeness that the index arithmetic depends on is gone.

## Building a heap in linear time

Given $n$ items at once, pushing them one at a time costs $n$ sift-ups of up to
$\log_2 n$ each — $O(n \log n)$. There is a better way, and its reason returns in every
tree argument you will ever make.

Leave the leaves alone; a leaf is already a heap of one. Then take each internal node,
from the last one backwards to the root, and sift it *down*. When node $i$ is
processed, both of its subtrees are already heaps, so one sift-down makes the subtree
rooted at $i$ a heap too. The cost of sifting a node down is at most its **height above
the leaves**, $h$. And here is the fact: in a complete binary tree, half the nodes are
leaves ($h = 0$), a quarter are one level up ($h = 1$), an eighth two up, and in general
about $n / 2^{h+1}$ nodes sit at height $h$. So the total work is

$$\sum_{h \ge 0} \frac{n}{2^{h+1}} \cdot h = \frac{n}{2} \sum_{h \ge 0} \frac{h}{2^{h}}
= \frac{n}{2} \cdot 2 = n,$$

using $\sum_{h \ge 0} h x^{h} = x/(1-x)^{2}$ at $x = 1/2$. The population is
concentrated at the bottom, sift-down charges by distance from the bottom, so the cheap
operation is applied to the many nodes and the dear one to the few. Sift-*up* inverts
that: it charges by distance from the root, and the half of the nodes that are leaves
each pay the full height.

```python
def sift_up(data, index):
    """Climb towards the root; return the number of swaps made."""
    swaps = 0
    while index > 0 and data[index] < data[(index - 1) // 2]:
        data[index], data[(index - 1) // 2] = data[(index - 1) // 2], data[index]
        index = (index - 1) // 2
        swaps += 1
    return swaps


def sift_down(data, index):
    """Sink towards the leaves; return the number of swaps made."""
    swaps, size = 0, len(data)
    while True:
        left, right, smallest = 2 * index + 1, 2 * index + 2, index
        if left < size and data[left] < data[smallest]:
            smallest = left
        if right < size and data[right] < data[smallest]:
            smallest = right
        if smallest == index:
            return swaps
        data[index], data[smallest] = data[smallest], data[index]
        index = smallest
        swaps += 1


n = 2 ** 16 - 1                      # a perfect tree of height 15
worst = list(range(n, 0, -1))        # descending: every element wants to rise
pushed, by_pushes = [], 0
for value in worst:
    pushed.append(value)
    by_pushes += sift_up(pushed, len(pushed) - 1)
heapified = list(worst)
by_heapify = sum(sift_down(heapified, i) for i in reversed(range(n // 2)))
print(f"n = {n}, root of each: {pushed[0]} and {heapified[0]}")
print(f"{n} pushes:      {by_pushes:>7} swaps")
print(f"bottom-up heapify: {by_heapify:>7} swaps")
```

Same input, a valid heap either way with 1 at the root, and a factor of fourteen between
them, purely from which direction the work flows: 917,506 swaps against 65,519, which is
under $n$. This does *not* make heap sort $O(n)$: the $n$ pops that follow each sift
down from the root, and those really are $\log n$ apiece.

## Three sorts, and what each gives up

With a heap in hand, sorting is one line: build the heap in $O(n)$, pop it dry in
$O(n \log n)$. That is **heap sort** — in place, with no bad input to fear, and not
stable, for a reason that comes at the end.

**Merge sort** halves the list, sorts each half, and merges: walk both sorted halves
with a finger on each, appending the smaller front element, and when one half runs out,
append the rest of the other. Every level of the recursion does $O(n)$ merging and there
are $\log_2 n$ levels: $O(n \log n)$ on any input, because halving does not consult the
data. The price is $O(n)$ extra memory and a copy of every element at every level. What
it buys, apart from the guarantee, is
**stability**: records with equal keys come out in the order they went in, and it costs
one character. On a tie, take from the *left* half, because the left half holds what
came first:

```python
def heap_sort(items, key):
    """Bottom-up heapify, then take the root n times, refilling it from the end."""
    data = list(items)

    def sift_down(index, size):
        while True:
            left, right, smallest = 2 * index + 1, 2 * index + 2, index
            if left < size and key(data[left]) < key(data[smallest]):
                smallest = left
            if right < size and key(data[right]) < key(data[smallest]):
                smallest = right
            if smallest == index:
                return
            data[index], data[smallest] = data[smallest], data[index]
            index = smallest

    for index in reversed(range(len(data) // 2)):
        sift_down(index, len(data))
    out = []
    for size in range(len(data), 0, -1):
        out.append(data[0])
        data[0] = data[size - 1]              # the LAST item moves to the root
        sift_down(0, size - 1)
    return out


def merge_sort(items, key):
    data = list(items)
    if len(data) <= 1:
        return data
    middle = len(data) // 2
    left = merge_sort(data[:middle], key)
    right = merge_sort(data[middle:], key)
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(right[j]) < key(left[i]):      # strictly smaller: a tie takes the left
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


records = [("b", 1), ("a", 2), ("b", 3), ("a", 4)]
first = lambda record: record[0]
print("merge_sort:", merge_sort(records, first))
print("heap_sort: ", heap_sort(records, first))
```

Merge sort keeps the tags in arrival order within each key. Heap sort has reversed the two `b` records,
and it was always going to: each take moves the *last* element of the array into the
root, from arbitrarily far away, and nothing in the array records which of two equal
keys came first. Long-range exchange is what makes heap sort and quicksort cheap, and it
is what costs them stability — the same property seen from two sides. Stability can be
bought back by sorting on `(key, original_index)`, at the cost that implies.

**Quicksort** picks a pivot, partitions the list in place into what is smaller and what
is larger, and recurses on both sides. Its constant factor is the best of the three,
because partitioning is two pointers walking through one array with the working set
shrinking into cache — but it has a worst case, and it takes three separate defences to
keep it away. A pivot that is the minimum or maximum splits off one element and leaves
$n - 1$, which is $O(n^{2})$; on already-sorted input, taking the first element as pivot
does this every time. **Median-of-three** — the middle of the first, middle and last
keys — makes that input harmless. A run of *equal* keys defeats median-of-three, because
with a two-way partition every equal key goes to one side and the sort degenerates
again:

```python
def quick_sort_two_way(data):
    """Lomuto partition: everything not below the pivot goes to the right."""
    passes = 0

    def sort(low, high):
        nonlocal passes
        while low < high:
            passes += 1
            middle = (low + high) // 2
            data[middle], data[high] = data[high], data[middle]
            pivot = data[high]
            store = low
            for i in range(low, high):
                if data[i] < pivot:
                    data[store], data[i] = data[i], data[store]
                    store += 1
            data[store], data[high] = data[high], data[store]
            sort(low, store - 1)
            low = store + 1

    sort(0, len(data) - 1)
    return passes


def quick_sort_three_way(data):
    """Dutch-flag partition: an equal block that is never recursed into."""
    passes = 0

    def sort(low, high):
        nonlocal passes
        while low < high:
            passes += 1
            pivot = data[(low + high) // 2]
            less, index, greater = low, low, high
            while index <= greater:
                if data[index] < pivot:
                    data[less], data[index] = data[index], data[less]
                    less += 1
                    index += 1
                elif data[index] > pivot:
                    data[index], data[greater] = data[greater], data[index]
                    greater -= 1
                else:
                    index += 1
            sort(low, less - 1)
            low = greater + 1

    sort(0, len(data) - 1)
    return passes


same = [7] * 2000
print("two-way partition passes on 2000 equal keys:  ", quick_sort_two_way(list(same)))
print("three-way partition passes on 2000 equal keys:", quick_sort_three_way(list(same)))
```

**Three-way partitioning** carves the list into less-than, equal-to and greater-than in
one pass and recurses only on the outer two. Two thousand identical keys are finished in
a single pass rather than 1999 of them, each one scanning everything that is left. The
third defence is against the stack rather than the clock: recurse into the *smaller*
side and loop on the larger, so the depth is bounded by $\log_2 n$ even when the splits
are bad. Each defence closes exactly one failure and none of the others, which is why all
three appear in the lab's reference solution.

## Where it stops holding

Every sort here decides by comparing two keys, and no comparison sort can beat
$n \log n$: there are $n!$ possible orderings of the input, each comparison has two
outcomes, so telling the orderings apart needs at least $\log_2(n!) \approx n \log_2 n$
comparisons in the worst case. Counting sort and radix sort escape the bound by looking
at digits rather than comparing, and are the right tool for small integer keys. The
heap's $O(n)$ build is a fact about *building*, not about *searching*: a heap answers
"what is the smallest" in $O(1)$ and "is 42 present" in nothing better than $O(n)$.

## What you are about to build

The lab is *A binary heap and three sorts*, and it forbids `heapq`, `sorted` and
`list.sort` because they are what you are building. `MinHeap(items, key)` keeps `data`
with the root at 0, builds by bottom-up heapify, and offers `push`, `pop`, `peek` and
`__len__`, with `IndexError` on an empty pop or peek. `merge_sort`, `quick_sort` and
`heap_sort` each take `(items, key=None)`, return a new list, and leave their input
alone; all three are run on the awkward inputs — empty, one element, all equal, sorted,
reverse-sorted — and `quick_sort` on 3000 sorted values. Only `merge_sort` is held to the stability check, and it is the tie line above
that passes it. The fill-in-the-blanks unit is that merge, hole by hole, and the
derivation unit is the heapify sum with symbols.
''',
                },
            ],
            "quiz": {
                "title": "Array-shaped trees, and what each sort gives up",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In a heap stored in a flat array with the root at index 0, the children of index $i$ are at:",
                        "opts": [
                            "$2i$ and $2i+1$",
                            "$i+1$ and $i+2$",
                            "$2i+1$ and $2i+2$",
                            "$(i-1)/2$ and $(i+1)/2$",
                        ],
                        "a": 2,
                        "whys": [
                            r"The *one-based* layout, where the root sits at index 1 and index 0 is left empty. Still common, and a rich source of off-by-one bugs when it is mixed with the zero-based form — check it at the root and it makes index 0 its own left child.",
                            r"Consecutive indices are siblings and cousins, not children. Indices 1 and 2 are the two children of the root, so index 2 cannot also be a child of index 1.",
                            r"Check it at the root: index 0's children must be 1 and 2, which $2i+1$ and $2i+2$ give.",
                            r"Halving goes upwards. The parent of $i$ is $(i-1)//2$, and the integer division is what makes both children map back to the same parent — but that is the inverse of what was asked for.",
                        ],
                        "why": r"""
Check it against index 0: its children must be 1 and 2, which $2i+1$ and $2i+2$ give
and nothing else does. The parent is the inverse, $(i-1)//2$, and the integer
division is what makes both children map back to the same parent. This one line is
what lets a complete binary tree live in a flat array with no pointers at all — the
structure is implied by arithmetic on the indices, which is why a heap costs exactly
one array and nothing else.
""",
                    },
                    {
                        "q": "Bottom-up heapify is $O(n)$, while building the same heap with $n$ separate pushes is $O(n\\log n)$. Where does the difference come from?",
                        "opts": [
                            "Bottom-up heapify skips most nodes, so it does less work simply by doing less",
                            "`push` is $O(n)$ in the worst case, because the backing array has to be grown",
                            "Sift-down charges distance to the leaves, and half the nodes are already there",
                            "Heapify compares each node against its parent once, so it is $n$ comparisons flat",
                        ],
                        "a": 2,
                        "whys": [
                            r"It does skip the leaves, but only because a leaf is already a heap of one — and it visits every internal node, which is half of them. Skipping half the nodes saves a factor of two, not a factor of $\log n$.",
                            r"Amortised growth makes `push` $O(\log n)$, not $O(n)$ — and if a push really were $O(n)$ the loop would be *worse* than $n\log n$, not better. The extra factor comes from the sift, not from the store.",
                            r"The cheap operation is applied to the many nodes and the dear one to the few.",
                            r"Heapify does not compare upwards at all, and one pass of parent comparisons would not produce a heap: fixing a node can break the one below it, which is exactly why `sift_down` recurses. The comparisons do total about $2n$, but not one per node.",
                        ],
                        "why": r"""
It is a question of where the nodes are. In any binary tree half the nodes are
leaves, a quarter are one level up, an eighth two levels up: the population is
concentrated at the bottom, and sift-down charges each node by its distance from the
bottom. So the cheap operation is applied to the many nodes and the dear one to the
few, and the weighted sum converges to $n$. Sifting up inverts that — it charges by
distance from the *root*, so the half of the nodes that are leaves each pay the full
height. Same tree, same heap at the end, and a factor of $\log n$ between them purely
because of which end the work is measured from.
""",
                    },
                    {
                        "q": "Merge sort's merge takes from the left half when the two keys compare equal. What does that one line buy?",
                        "opts": [
                            "Stability — records with equal keys come out in the order they went in",
                            "The $O(n\\log n)$ bound, which fails if ties are broken the other way",
                            "A speed-up of about a factor of two on input that is already sorted",
                            "Correctness: taking from the right on a tie leaves the output unsorted",
                        ],
                        "a": 0,
                        "whys": [
                            r"The left half holds what came first, so taking it on a tie preserves the original order.",
                            r"Both branches do one comparison and one append, so the cost is identical whichever side a tie goes to. The bound comes from halving the input, and nothing about a tie changes that.",
                            r"There is no such short cut in this merge — it compares and appends $n$ elements per level whatever the input looks like. (Timsort does exploit runs that are already sorted, but by detecting them beforehand, not by breaking ties.)",
                            r"The output is still perfectly sorted: the two candidates are *equal*, so emitting either one keeps the sequence non-decreasing. What is lost is not correctness but the promise — which is precisely the point of the question.",
                        ],
                        "why": r"""
Both halves are already sorted and the left half holds the elements that came first,
so on a tie the left one is the earlier record and taking it preserves the original
order. Take from the right instead and the sort is still perfectly correct — the
output is still in non-decreasing order — but equal records come out reversed, which
is exactly what a stable sort promises not to do. That promise is what lets you sort
by one field and then by another and keep the first as a tiebreak, which is how every
multi-column sort in every spreadsheet is actually implemented.
""",
                    },
                    {
                        "q": "Why is heap sort not stable?",
                        "opts": [
                            "A heap cannot hold duplicate keys, so equal records never arise in the first place",
                            "It sorts in place, and an in-place sort cannot be stable",
                            "Building and popping exchange elements that started far apart",
                            "It is implemented recursively, and recursion does not preserve the original order",
                        ],
                        "a": 2,
                        "whys": [
                            r"Heaps hold duplicates perfectly happily — the lab sorts `[5, 5, 5]`. The heap property is $\le$ between parent and child, not $<$.",
                            r"Insertion sort is in place and stable, so no such rule exists. What costs heap sort its stability is the *distance* of its exchanges, not the absence of a scratch array — merge sort would still be stable if you found a way to merge in place.",
                            r"`pop` moves the *last* element of the array into the root, from arbitrarily far away.",
                            r"Merge sort is recursive and stable, and the heap here sifts iteratively, so recursion is doing no work in this explanation from either direction.",
                        ],
                        "why": r"""
Long-range exchange is exactly what makes heap sort and quicksort cheap, and exactly
what destroys stability — the two properties are the same property seen from
different sides. `pop` takes the root and moves the *last* element of the array into
its place, and that element may have started thousands of positions away from an
equal key it now sits before. Nothing in the array records which of two equal keys
came first, so nothing can restore it. Stability can always be bought back by
appending the original index to the key, at the cost of the memory and comparisons
that implies — which is the honest way to state the trade.
""",
                    },
                    {
                        "q": "Three-way partitioning splits into less-than, equal-to and greater-than. What does carving out the equal region prevent?",
                        "opts": [
                            "A badly chosen pivot degrading the sort on input that is already sorted",
                            "The $O(n)$ of scratch space a two-way partition needs for the equal keys",
                            "A run of identical keys degenerating to quadratic time",
                            "Stack overflow, by replacing one of the two recursive calls with a loop",
                        ],
                        "a": 2,
                        "whys": [
                            r"That is what median-of-three is for, and it is a separate defence. Three-way partitioning does not help choose a pivot, and a bad pivot still hurts on keys that are all distinct.",
                            r"A two-way partition is already in place and needs no scratch space at all — and neither does the three-way one. Nothing here is allocated.",
                            r"The equal block is finished in one pass, and never recursed into.",
                            r"Recursing into the smaller side and looping on the larger is what bounds the depth to $\log n$ — also present in the reference solution, and also a separate defence.",
                        ],
                        "why": r"""
With a two-way partition, a million equal keys put every element on one side of the
pivot, the recursion shortens the range by one each time, and the sort is $O(n^2)$ on
input that is arguably already sorted. Three-way partitioning puts them all in the
middle block, and that block is done: the two recursive calls are on what is strictly
smaller and strictly larger, so an array of identical keys is finished in a single
pass. Note how narrow each of quicksort's three defences is — pivot choice, the equal
block, and the tail loop each close exactly one failure and none of the others.
""",
                    },
                    {
                        "q": "Both merge sort and quicksort are $O(n\\log n)$, yet quicksort usually wins on real data. The usual reason is:",
                        "opts": [
                            "Quicksort makes strictly fewer comparisons, so it does less work per level",
                            "Merge sort is $O(n\\log n)$ only on average; its worst case is quadratic",
                            "Quicksort partitions in place and scans sequentially; merge sort copies each level",
                            "Merge sort recurses more deeply, so a larger share of its time goes into call overhead",
                        ],
                        "a": 2,
                        "whys": [
                            r"Comparison counts actually favour merge sort slightly, which makes it the better choice whenever a comparison is expensive — long strings, or records reached through a costly key function.",
                            r"Merge sort is $O(n\log n)$ in the worst case as well as on average: it halves unconditionally, and no input can persuade it otherwise. It is *quicksort* whose worst case is quadratic, which is the risk it accepts in exchange for the constant.",
                            r"Two pointers walking towards each other through one array, with nothing allocated.",
                            r"Both recurse to depth $\log_2 n$ — merge sort exactly, quicksort on any decent pivot — and both make about the same number of calls, so call overhead cannot separate them.",
                        ],
                        "why": r"""
The constant hidden by $O(n\log n)$ is mostly memory traffic, and quicksort's is
about as good as it gets: two pointers walking towards each other through one array,
with the working set staying in cache as the ranges shrink. Merge sort allocates and
copies $n$ elements per level, so it moves several times the data and asks the
allocator for it each time. Which is why the choice between them is not really about
complexity at all: pick quicksort when moving memory is the cost, and merge sort when
*comparing* is the cost or when stability is required.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The merge, and the line that makes it stable",
                "minutes": 9,
                "lang": "python",
                "caption": "merge_sort.py — five holes, one of which changes nothing except stability",
                "brief": r"""
Merge sort is three decisions: where to stop recursing, where to split, and which
side to take from on a tie. The third is the interesting one, because getting it
wrong leaves a sort that passes every test about order and fails the only test about
*which* equal element came out first.

Nothing runs here. Correctly filled, sorting
`[("b", 1), ("a", 2), ("b", 3), ("a", 4)]` by its first element returns
`[("a", 2), ("a", 4), ("b", 1), ("b", 3)]` — the tags still in the order they arrived.
""",
                "listing": r'''
def merge_sort(items, key=None):
    """A stable O(n log n) sort returning a new list."""
    keyof = key if key is not None else (lambda item: item)
    data = list(items)
    if len(data) <= ___:
        return data
    middle = ___
    left = merge_sort(data[:middle], key)
    right = merge_sort(data[middle:], key)

    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if keyof(right[j]) ___ keyof(left[i]):
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[___:])
    merged.extend(right[___:])
    return merged
''',
                "blanks": [
                    {
                        "prompt": "The base case: a list this long or shorter is already sorted.",
                        "hole": "?",
                        "opts": ["2", "1", "0"],
                        "a": 1,
                        "why": "A list of one element, or of none, is sorted by definition and needs no work. It is also the only base case that guarantees both halves are strictly shorter than the whole, which is what makes the recursion terminate.",
                        "whys": [
                            "This returns any two-element list untouched, so `[2, 1]` comes back as `[2, 1]` and the error propagates up through every merge above it.",
                            "A list of one element, or of none, is sorted by definition and needs no work. It is also the only base case that guarantees both halves are strictly shorter than the whole, which is what makes the recursion terminate.",
                            "A single-element list falls through: `middle` becomes 0, the right half is the whole list again, and the function calls itself on identical input until the stack runs out.",
                        ],
                    },
                    {
                        "prompt": "Where the split goes, if each half is to be half the size.",
                        "hole": "?",
                        "opts": ["len(data)", "1", "len(data) // 2", "len(data) // 2 + 1"],
                        "a": 2,
                        "why": "Halving is what gives $\\log_2 n$ levels of recursion, each doing $O(n)$ work. Floor division sends the odd element to the right half, which costs nothing and keeps the arithmetic on integers.",
                        "whys": [
                            "The right half is always empty, so every call recurses on the entire input and the function never terminates.",
                            "This sorts correctly, and it does it in $O(n^2)$: peeling one element off at a time turns merge sort into insertion sort with a much larger constant.",
                            "Halving is what gives $\\log_2 n$ levels of recursion, each doing $O(n)$ work. Floor division sends the odd element to the right half, which costs nothing and keeps the arithmetic on integers.",
                            "On a two-element list this makes `middle` equal to 2, so the right half is empty and the left half is the whole input — the recursion never shrinks and never returns.",
                        ],
                    },
                    {
                        "prompt": "The comparison. On a tie, which half should give up its element?",
                        "hole": "?",
                        "opts": ["<=", ">", ">=", "<"],
                        "a": 3,
                        "why": "The right element is taken only when it is *strictly* smaller, so a tie falls through to the left — and the left half holds whatever came first in the input. That is the entire implementation of stability.",
                        "whys": [
                            "Correct order, lost stability: on every tie the right element goes first, so equal records come out reversed. The lab's tag check catches it and nothing else will.",
                            "This takes from the right whenever the right element is larger, which merges the two halves into descending nonsense — and the leftover `extend` calls then append an ascending tail onto it.",
                            "The same inversion, and ties go the wrong way as well.",
                            "The right element is taken only when it is *strictly* smaller, so a tie falls through to the left — and the left half holds whatever came first in the input. That is the entire implementation of stability.",
                        ],
                    },
                    {
                        "prompt": "One half ran out. Append what is left of the left half, starting from…",
                        "hole": "?",
                        "opts": ["i", "0", "j", "i + 1"],
                        "a": 0,
                        "why": "`i` is how far the left half has been consumed, so `left[i:]` is exactly the part that has not been merged yet — and it is empty, harmlessly, when the left half is the one that ran out.",
                        "whys": [
                            "`i` is how far the left half has been consumed, so `left[i:]` is exactly the part that has not been merged yet — and it is empty, harmlessly, when the left half is the one that ran out.",
                            "Starting from 0 re-appends the entire left half, so every element already merged appears twice and the output is longer than the input.",
                            "`j` indexes the right half. Using it here takes a slice of the left half at an unrelated position — sometimes too much, sometimes too little, and always silently.",
                            "This skips one element: the value at `left[i]` was compared but never appended, and it vanishes from the output.",
                        ],
                    },
                    {
                        "prompt": "…and the right half, starting from…",
                        "hole": "?",
                        "opts": ["i", "j + 1", "j", "0"],
                        "a": 2,
                        "why": "`j` is the matching marker for the right half. Exactly one of these two slices is non-empty, because the loop stopped when one of the halves was exhausted, and both are written out because you do not know which.",
                        "whys": [
                            "`i` belongs to the left half, so this slices the right half at the wrong offset and drops or duplicates elements depending on how the two halves happened to interleave.",
                            "One element short: `right[j]` was examined but never appended.",
                            "`j` is the matching marker for the right half. Exactly one of these two slices is non-empty, because the loop stopped when one of the halves was exhausted, and both are written out because you do not know which.",
                            "The whole right half again, duplicating everything already merged from it.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Why building a heap costs n, not n log n",
                "minutes": 12,
                "vars": ["n", "h", "x", "S", "T"],
                "brief": r"""
Sifting one node down costs its distance from the leaves, and there are $n$ nodes, so
heapify obviously costs $n\log n$ — that is the reasoning, and it is wrong. It is
wrong because it charges every node the height of the whole tree, and almost no node
is that far from the bottom.

Count by level instead. Take $n$ as a power of two so the tree is full, and let $h$
be **height above the leaves**: leaves are at $h = 0$, their parents at $h = 1$.
""",
                "steps": [
                    {
                        "prompt": "Half the nodes are leaves, a quarter are one level above them, an eighth two levels above. How many nodes sit at height $h$?",
                        "answer": "\\frac{n}{2^{h+1}}",
                        "hint": "At $h = 0$ it should give $n/2$, at $h = 1$ it should give $n/4$.",
                        "deconstruct": [
                            "The leaves are $n/2$ of the nodes, so the formula must give $n/2$ when $h = 0$.",
                            "Each level up halves the population again, which is one more factor of 2 in the denominator.",
                        ],
                    },
                    {
                        "prompt": "Sifting a node at height $h$ down costs at most $h$ swaps, because that is how far it can fall. What is the total work contributed by all the nodes at height $h$?",
                        "answer": "\\frac{h n}{2^{h+1}}",
                        "hint": "Number of nodes at that height, times the cost of each.",
                        "deconstruct": [
                            "There are $n/2^{h+1}$ of them.",
                            "Each costs at most $h$, so multiply.",
                        ],
                    },
                    {
                        "prompt": "Add that over every height. Pull the constant $n/2$ out of the sum and call what remains $S = \\sum_{h \\ge 0} h/2^{h}$. Write the total work $T$ in terms of $n$ and $S$.",
                        "given": "$T = \\sum_{h \\ge 0} \\frac{h n}{2^{h+1}}$",
                        "answer": "\\frac{n S}{2}",
                        "hint": "$\\frac{hn}{2^{h+1}}$ is $\\frac{n}{2} \\cdot \\frac{h}{2^{h}}$, and only the second factor depends on $h$.",
                        "deconstruct": [
                            "Split the denominator: $2^{h+1} = 2 \\cdot 2^{h}$.",
                            "The $n/2$ is the same in every term, so it comes outside the sum.",
                            "What is left inside is the definition of $S$.",
                        ],
                    },
                    {
                        "prompt": "Now evaluate $S$, using the standard result $\\sum_{h \\ge 0} h x^{h} = \\frac{x}{(1-x)^{2}}$ for $|x| < 1$.",
                        "given": "$S = \\sum_{h \\ge 0} h/2^{h}$, so take $x = 1/2$.",
                        "answer": "2",
                        "hint": "With $x = 1/2$ the denominator is $(1/2)^2 = 1/4$.",
                        "deconstruct": [
                            "$h/2^{h}$ is $h x^{h}$ with $x = 1/2$.",
                            "So $S = \\frac{1/2}{(1/2)^{2}} = \\frac{1/2}{1/4}$.",
                        ],
                    },
                    {
                        "prompt": "Put that value into your expression for $T$.",
                        "answer": "n",
                        "hint": "Substitute $S = 2$ into $nS/2$.",
                        "deconstruct": [
                            "$T = nS/2$ and $S = 2$.",
                            "The twos cancel.",
                        ],
                    },
                ],
                "closing": r"""
$T \le n$: bottom-up heapify does at most one swap per element in the whole array,
and the $\log$ never appears. The series is what does it — $S$ converges, so the deep
nodes contribute a vanishing share of the total no matter how tall the tree gets.

The contrast with building by $n$ pushes is worth holding on to. Sift-*up* charges
each node its distance from the root, and the same population argument now works
against you: the $n/2$ leaves each pay the full height, giving $\Theta(n\log n)$. Same
tree, same swaps, same code almost — and a whole factor of $\log n$ turning on which
direction the work flows. It is also why `heap_sort` cannot inherit the $O(n)$: the
build is linear, but the $n$ pops that follow each sift down from the root, and those
really do cost $\log n$ apiece.
""",
            },
            "lab": {
                "title": "A binary heap and three sorts",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
No `heapq`, no `sorted`, no `list.sort` — those are what you are building.

## `MinHeap(items=None, key=None)`

- `self.data` — the array holding the heap, root at index 0
- `self.key` — always a callable; the identity function when `key` is `None`
- constructing from `items` uses **bottom-up heapify**: sift down from the last
  internal node backwards, which is O(n), not n separate pushes
- `push(item)`, `pop()` (smallest), `peek()`, `__len__`
- `pop` and `peek` raise `IndexError` when empty

The invariant, for every index `i` above 0: `key(data[i])` is not smaller than
`key(data[(i - 1) // 2])`.

## The three sorts

All three take `(items, key=None)`, **return a new list**, and leave the input
untouched.

**`merge_sort`** — split in half, sort each half, merge. When two keys are
equal, take from the left half; that one line is what makes it stable.

**`quick_sort`** — pick the median of the first, middle and last keys as the
pivot, then partition into three regions (less than, equal to, greater than) in
one pass, and recurse on the outer two only. The equal region means a list of
identical values sorts in a single pass instead of degenerating.

**`heap_sort`** — build a `MinHeap` and pop it dry.

```text
merge_sort([3, 1, 2])                     -> [1, 2, 3]
quick_sort(["bbb", "a", "cc"], key=len)   -> ["a", "cc", "bbb"]
heap_sort([5, 5, 5])                      -> [5, 5, 5]
```

## Stability

Sort `[("b", 1), ("a", 2), ("b", 3), ("a", 4)]` by its first element. A stable
sort must give `[("a", 2), ("a", 4), ("b", 1), ("b", 3)]` — the tags stay in
their original relative order. Merge sort must pass that check. Quick sort and
heap sort are not required to, and generally will not: swapping distant
elements is exactly what makes them cheap.
''',
                "files": [{"name": "main.py", "content": r'''
class MinHeap:
    """A binary min-heap in a flat array."""

    def __init__(self, items=None, key=None):
        self.key = key if key is not None else (lambda item: item)
        self.data = list(items or [])
        # your code here: heapify bottom-up

    def __len__(self):
        # your code here
        return 0

    def _sift_up(self, index):
        """Move the item at index towards the root until the heap holds."""
        # your code here

    def _sift_down(self, index):
        """Move the item at index towards the leaves until the heap holds."""
        # your code here

    def push(self, item):
        """Add an item in O(log n)."""
        # your code here

    def pop(self):
        """Remove and return the smallest item; IndexError when empty."""
        # your code here

    def peek(self):
        """The smallest item, left in place; IndexError when empty."""
        # your code here


def merge_sort(items, key=None):
    """A stable O(n log n) sort returning a new list."""
    # your code here


def quick_sort(items, key=None):
    """Median-of-three quicksort with three-way partitioning."""
    # your code here


def heap_sort(items, key=None):
    """Sort by draining a MinHeap."""
    # your code here


print(merge_sort([3, 1, 2]))
print(quick_sort([5, 3, 5, 1]))
print(heap_sort(["bbb", "a", "cc"], key=len))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class MinHeap:
    """A binary min-heap in a flat array."""

    def __init__(self, items=None, key=None):
        self.key = key if key is not None else (lambda item: item)
        self.data = list(items or [])
        for index in reversed(range(len(self.data) // 2)):
            self._sift_down(index)

    def __len__(self):
        return len(self.data)

    def _sift_up(self, index):
        """Move the item at index towards the root until the heap holds."""
        while index > 0:
            parent = (index - 1) // 2
            if self.key(self.data[index]) < self.key(self.data[parent]):
                self.data[index], self.data[parent] = self.data[parent], self.data[index]
                index = parent
            else:
                return

    def _sift_down(self, index):
        """Move the item at index towards the leaves until the heap holds."""
        size = len(self.data)
        while True:
            left = 2 * index + 1
            right = left + 1
            smallest = index
            if left < size and self.key(self.data[left]) < self.key(self.data[smallest]):
                smallest = left
            if right < size and self.key(self.data[right]) < self.key(self.data[smallest]):
                smallest = right
            if smallest == index:
                return
            self.data[index], self.data[smallest] = self.data[smallest], self.data[index]
            index = smallest

    def push(self, item):
        """Add an item in O(log n)."""
        self.data.append(item)
        self._sift_up(len(self.data) - 1)

    def pop(self):
        """Remove and return the smallest item; IndexError when empty."""
        if not self.data:
            raise IndexError("pop from an empty heap")
        smallest = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0)
        return smallest

    def peek(self):
        """The smallest item, left in place; IndexError when empty."""
        if not self.data:
            raise IndexError("peek at an empty heap")
        return self.data[0]


def merge_sort(items, key=None):
    """A stable O(n log n) sort returning a new list."""
    keyof = key if key is not None else (lambda item: item)
    data = list(items)
    if len(data) <= 1:
        return data
    middle = len(data) // 2
    left = merge_sort(data[:middle], key)
    right = merge_sort(data[middle:], key)
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if keyof(right[j]) < keyof(left[i]):
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def _median_of_three(a, b, c):
    """The middle one of three keys."""
    if a <= b <= c or c <= b <= a:
        return b
    if b <= a <= c or c <= a <= b:
        return a
    return c


def quick_sort(items, key=None):
    """Median-of-three quicksort with three-way partitioning."""
    keyof = key if key is not None else (lambda item: item)
    data = list(items)

    def sort(low, high):
        while low < high:
            middle = (low + high) // 2
            pivot = _median_of_three(keyof(data[low]), keyof(data[middle]),
                                     keyof(data[high]))
            less, index, greater = low, low, high
            while index <= greater:
                current = keyof(data[index])
                if current < pivot:
                    data[less], data[index] = data[index], data[less]
                    less += 1
                    index += 1
                elif current > pivot:
                    data[index], data[greater] = data[greater], data[index]
                    greater -= 1
                else:
                    index += 1
            if less - low < high - greater:
                sort(low, less - 1)
                low = greater + 1
            else:
                sort(greater + 1, high)
                high = less - 1

    sort(0, len(data) - 1)
    return data


def heap_sort(items, key=None):
    """Sort by draining a MinHeap."""
    heap = MinHeap(items, key)
    return [heap.pop() for _ in range(len(heap))]


print(merge_sort([3, 1, 2]))
print(quick_sort([5, 3, 5, 1]))
print(heap_sort(["bbb", "a", "cc"], key=len))
'''}],
                "hints": [
                    "The parent of index `i` is `(i - 1) // 2` and its children are `2i + 1` and `2i + 2`; check a child index against the length before you touch it.",
                    "`pop` takes the root as the answer, moves the *last* item into index 0 and sifts it down — that keeps the array a complete tree with no holes.",
                    "Bottom-up heapify only sifts down the internal nodes: `for index in reversed(range(len(self.data) // 2)): self._sift_down(index)`. The leaves are already heaps of one.",
                    "The three-way partition keeps three markers: everything below `less` is smaller than the pivot, everything above `greater` is larger, and `index` scans the unknown middle. Only two of the three moves advance `index`.",
                ],
                "tests": [
                    {"name": "Heap invariant and ordered draining", "code": r'''
import random as _random
def _check_heap(_h, _note=""):
    for _i in range(1, len(_h.data)):
        _parent = (_i - 1) // 2
        assert not (_h.key(_h.data[_i]) < _h.key(_h.data[_parent])), \
            f"heap property broken at index {_i} {_note}: {_h.data!r}"
_rng = _random.Random(7)
_values = [_rng.randint(0, 999) for _ in range(200)]
_h = MinHeap()
for _v in _values:
    _h.push(_v)
    _check_heap(_h, "after a push")
assert len(_h) == 200, f"length is {len(_h)}, expected 200"
_drained = [_h.pop() for _ in range(200)]
assert _drained == sorted(_values), "draining a min-heap must give ascending order"
assert len(_h) == 0, "the heap should be empty now"
'''},
                    {"name": "Bottom-up heapify", "code": r'''
import random as _random
_rng = _random.Random(11)
_values = [_rng.randint(-500, 500) for _ in range(300)]
_h = MinHeap(_values)
assert len(_h) == 300, f"heapify should keep every item, got {len(_h)}"
for _i in range(1, len(_h.data)):
    _parent = (_i - 1) // 2
    assert not (_h.data[_i] < _h.data[_parent]), f"heapify left index {_i} out of order"
assert [_h.pop() for _ in range(300)] == sorted(_values), "a heapified array must drain sorted"
assert MinHeap(list(range(1000, 0, -1))).peek() == 1, "the smallest of 1..1000 is 1"
assert len(MinHeap()) == 0, "MinHeap() with no items is empty"
'''},
                    {"name": "peek, and the empty cases", "code": r'''
_h = MinHeap()
for _m in ("pop", "peek"):
    try:
        getattr(_h, _m)()
        assert False, f"{_m} on an empty heap should raise IndexError"
    except IndexError:
        pass
_h.push(5)
_h.push(3)
assert _h.peek() == 3 and len(_h) == 2, "peek must leave the item in the heap"
assert _h.pop() == 3 and _h.pop() == 5, "and then pop them in order"
'''},
                    {"name": "A key function turns the heap into anything", "code": r'''
_h = MinHeap(["bbb", "a", "cc", "dddd"], key=len)
assert [_h.pop() for _ in range(4)] == ["a", "cc", "bbb", "dddd"], "shortest first"
_max = MinHeap([3, 9, 1, 7], key=lambda x: -x)
assert [_max.pop() for _ in range(4)] == [9, 7, 3, 1], "negating the key gives a max-heap"
_records = MinHeap(key=lambda r: r["priority"])
for _r in [{"priority": 5, "id": "e"}, {"priority": 1, "id": "a"}, {"priority": 3, "id": "c"}]:
    _records.push(_r)
assert [_records.pop()["id"] for _ in range(3)] == ["a", "c", "e"], "priority queue order"
'''},
                    {"name": "All three sorts handle the awkward inputs", "code": r'''
_cases = [[], [1], [2, 1], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [7, 7, 7, 7],
          [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], [-2, 0, -5, 3, -5],
          [0] * 50, list(range(60)), list(range(60, 0, -1))]
for _sort in (merge_sort, quick_sort, heap_sort):
    for _case in _cases:
        _original = list(_case)
        _got = _sort(_case)
        assert _got == sorted(_original), \
            f"{_sort.__name__}({_original!r}) gave {_got!r}, expected {sorted(_original)!r}"
        assert _case == _original, f"{_sort.__name__} mutated its input: {_case!r}"
        assert _got is not _case, f"{_sort.__name__} must return a new list"
'''},
                    {"name": "The key parameter works everywhere", "code": r'''
_words = ["bbb", "a", "dddd", "cc"]
for _sort in (merge_sort, quick_sort, heap_sort):
    _got = _sort(_words, key=len)
    assert _got == ["a", "cc", "bbb", "dddd"], f"{_sort.__name__} by length gave {_got!r}"
    _got = _sort([3, 9, 1, 7], key=lambda x: -x)
    assert _got == [9, 7, 3, 1], f"{_sort.__name__} with a negating key gave {_got!r}"
'''},
                    {"name": "merge_sort is stable", "code": r'''
_pairs = [("b", 1), ("a", 2), ("b", 3), ("a", 4), ("c", 5), ("a", 6)]
_got = merge_sort(_pairs, key=lambda p: p[0])
_want = [("a", 2), ("a", 4), ("a", 6), ("b", 1), ("b", 3), ("c", 5)]
assert _got == _want, f"merge_sort is not stable: gave {_got!r}, expected {_want!r}"
import random as _random
_rng = _random.Random(7)
_many = [(_rng.randint(0, 5), _i) for _i in range(400)]
_got = merge_sort(_many, key=lambda p: p[0])
assert _got == sorted(_many, key=lambda p: p[0]), "merge_sort disagrees with a stable reference"
for _group in range(6):
    _tags = [_t for _k, _t in _got if _k == _group]
    assert _tags == sorted(_tags), f"equal keys were reordered within group {_group}"
'''},
                    {"name": "All three agree with the reference on big random data", "code": r'''
import random as _random
_rng = _random.Random(7)
_big = [_rng.randint(0, 10 ** 6) for _ in range(2000)]
_want = sorted(_big)
for _sort in (merge_sort, quick_sort, heap_sort):
    _got = _sort(_big)
    assert _got == _want, f"{_sort.__name__} got 2000 random values wrong"
_dupes = [_rng.randint(0, 9) for _ in range(3000)]
for _sort in (merge_sort, quick_sort, heap_sort):
    assert _sort(_dupes) == sorted(_dupes), \
        f"{_sort.__name__} struggles with 3000 values drawn from 10 distinct keys"
_sorted_input = list(range(3000))
assert quick_sort(_sorted_input) == _sorted_input, \
    "already-sorted input must not degenerate — that is what median-of-three is for"
assert quick_sort(list(range(3000, 0, -1))) == list(range(1, 3001)), \
    "nor must reverse-sorted input"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an ordered map over two backends",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
One abstract data type, two implementations, and a measurement that settles the
argument between them. `ordered_map.py` holds everything the checks import;
`main.py` prints the comparison.

## The ADT

`OrderedMap(backend="bst")` — a key-value map that can also answer *ordered*
questions. `ValueError` for a backend other than `"bst"` or `"hash"`. Both
backends must satisfy exactly the same contract:

- `put(key, value)`, `get(key, default=None)`, `__setitem__`, `__getitem__`
  (raising `KeyError`), `__contains__`, `__len__`
- `delete(key)` — `True` when a pair was removed
- `keys()` / `items()` — **always in ascending key order**, whichever backend
  is underneath
- `min_key()` / `max_key()` — `None` on an empty map
- `range_keys(low, high)` — every key with `low <= key <= high`, ascending;
  an empty list when `low > high`
- `floor_key(key)` — the largest key that is `<= key`, or `None`
- `ceiling_key(key)` — the smallest key that is `>= key`, or `None`

## The two backends

**`BSTMap`** — the tree from module 3, carrying a value on each node. `items()`
is an in-order walk, so ordering is free; `range_keys` should prune subtrees it
cannot need rather than walking everything.

**`HashMap`** — chained hashing from module 4, with FNV-1a. Ordering is *not*
free here: `keys()` has to sort, and `floor_key` has to scan.

## The measurement

Every backend keeps `self.comparisons`, incremented **once per key comparison
performed while locating a key** — one per node visited on a BST descent, one
per entry examined in a hash bucket. Resizes and rehashing do not count.

`benchmark(backend, n=2000, seed=7)` returns a dict:

```text
{"backend": ..., "n": ..., "put_comparisons": ..., "get_comparisons": ...,
 "hits": ..., "ordered_first": ...}
```

Build a map of `n` distinct pseudo-random integer keys drawn with
`random.Random(seed)`, recording the comparisons the insertions cost; reset the
counter; look every key up once, counting the hits; then record `keys()[0]`.
Both backends must report the same `n`, `hits` and `ordered_first` — the whole
point is that only the *cost* differs.

Expect the hash backend to spend roughly one comparison per lookup and the tree
to spend on the order of `log2 n`. That gap, not a stopwatch, is the result you
report.
''',
        "deliverables": [
            "`ordered_map.py` — `BSTMap`, `HashMap`, `OrderedMap` and `benchmark`, importable with no side effects",
            "One ADT surface that behaves identically on both backends, including the ordered queries",
            "A BST backend with insert, delete in all three cases, in-order iteration and pruned range queries",
            "A chained hash backend with FNV-1a hashing and doubling on the load factor",
            "Deterministic instrumentation: a `comparisons` counter on each backend and a seeded `benchmark`",
            "`main.py` — a printed table comparing the two backends at a couple of sizes",
        ],
        "constraints": [
            "Standard library only; `random` is the only import you should need",
            "No `dict`, `set` or `sorted` may stand in for the map itself — sorting the *output* of `keys()` is fine",
            "`ordered_map.py` must define classes and functions only; running it prints nothing",
            "`benchmark` must be reproducible: the same seed gives byte-identical numbers",
            "No wall-clock timing in the checked code — operation counts only",
        ],
        "rubric": [
            {"criterion": "ADT correctness", "weight": 30,
             "evidence": "Both backends pass the same contract checks, including empty maps, missing keys and replaced values."},
            {"criterion": "Ordered queries", "weight": 25,
             "evidence": "keys(), range_keys, floor_key and ceiling_key are right at the boundaries and outside the key range, on both backends."},
            {"criterion": "Backend implementations", "weight": 20,
             "evidence": "The BST handles all three deletion cases and prunes its range walk; the hash map resizes on load factor and survives rehashing."},
            {"criterion": "Instrumentation and benchmark", "weight": 15,
             "evidence": "comparisons counts real key comparisons, benchmark is seeded and reproducible, and the two backends agree on every result but cost."},
            {"criterion": "Design and readability", "weight": 10,
             "evidence": "OrderedMap delegates rather than duplicating logic, names are precise, and every public method carries a docstring."},
        ],
        "hints": [
            "Write `BSTMap` first and get `items()` right; `keys()`, `min_key` and `range_keys` can all lean on an in-order walk while you are still building.",
            "`range_keys` prunes by never descending left when the node's key is already at or below `low`, and never descending right when it is at or above `high`.",
            "`floor_key` on a tree is a descent that remembers the last node it passed on the way right; on a hash map it is one pass over `keys()`. Both are correct — the difference in cost is the point of the exercise.",
            "Count a comparison in exactly one place per backend — inside the BST descent loop and inside the bucket scan — so the numbers stay meaningful and you cannot double count.",
            "`OrderedMap` should hold a backend object and forward every call to it. If you find yourself writing an `if self.backend == ...` inside a method, the polymorphism has gone in the wrong place.",
        ],
        "files": [
            {"name": "ordered_map.py", "content": r'''
import random

FNV_OFFSET = 2166136261
FNV_PRIME = 16777619
MASK32 = 0xFFFFFFFF


def fnv1a(text):
    """The 32-bit FNV-1a hash of a string."""
    # your code here


class MapNode:
    """One node of the search-tree backend."""

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BSTMap:
    """An ordered map backed by an unbalanced binary search tree."""

    def __init__(self):
        self.root = None
        self.comparisons = 0
        self._size = 0

    def __len__(self):
        return self._size

    def put(self, key, value):
        """Insert or replace, counting one comparison per node visited."""
        # your code here

    def get(self, key, default=None):
        """The value, or default, counting one comparison per node visited."""
        # your code here

    def delete(self, key):
        """Remove a key; True when something went."""
        # your code here

    def items(self):
        """Every (key, value) pair in ascending key order."""
        # your code here

    def range_keys(self, low, high):
        """Keys with low <= key <= high, ascending, pruning subtrees."""
        # your code here

    def floor_key(self, key):
        """The largest key <= key, or None."""
        # your code here

    def ceiling_key(self, key):
        """The smallest key >= key, or None."""
        # your code here


class HashMap:
    """An ordered map backed by a chained hash table."""

    def __init__(self, capacity=8, load_factor=0.75):
        self.capacity = capacity
        self.load_factor = load_factor
        self.comparisons = 0
        self.resizes = 0
        self._size = 0
        self._buckets = [[] for _ in range(capacity)]

    def __len__(self):
        return self._size

    def _index(self, key):
        """Which bucket a key belongs in."""
        # your code here

    def put(self, key, value):
        """Insert or replace, resizing past the load factor."""
        # your code here

    def get(self, key, default=None):
        """The value, or default, counting one comparison per entry examined."""
        # your code here

    def delete(self, key):
        """Remove a key; True when something went."""
        # your code here

    def items(self):
        """Every (key, value) pair in ascending key order."""
        # your code here

    def range_keys(self, low, high):
        """Keys with low <= key <= high, ascending."""
        # your code here

    def floor_key(self, key):
        """The largest key <= key, or None."""
        # your code here

    def ceiling_key(self, key):
        """The smallest key >= key, or None."""
        # your code here


class OrderedMap:
    """The ADT: one surface, two interchangeable backends."""

    BACKENDS = {"bst": BSTMap, "hash": HashMap}

    def __init__(self, backend="bst"):
        # your code here
        pass

    def __len__(self):
        # your code here
        return 0

    def __contains__(self, key):
        # your code here
        return False

    def __getitem__(self, key):
        """The value, or KeyError."""
        # your code here

    def __setitem__(self, key, value):
        # your code here
        pass

    def put(self, key, value):
        # your code here
        pass

    def get(self, key, default=None):
        # your code here
        pass

    def delete(self, key):
        # your code here
        pass

    def items(self):
        """Pairs in ascending key order."""
        # your code here

    def keys(self):
        """Keys in ascending order."""
        # your code here

    def min_key(self):
        """The smallest key, or None."""
        # your code here

    def max_key(self):
        """The largest key, or None."""
        # your code here

    def range_keys(self, low, high):
        # your code here
        pass

    def floor_key(self, key):
        # your code here
        pass

    def ceiling_key(self, key):
        # your code here
        pass


def benchmark(backend, n=2000, seed=7):
    """Build a map of n random keys, look them all up, and report the cost."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from ordered_map import benchmark

print(f"{'backend':<8}{'n':>7}{'put cmp':>10}{'get cmp':>10}{'per get':>10}")
for n in (500, 2000):
    for backend in ("bst", "hash"):
        report = benchmark(backend, n)
        print(f"{report['backend']:<8}{report['n']:>7}{report['put_comparisons']:>10}"
              f"{report['get_comparisons']:>10}{report['get_comparisons'] / n:>10.2f}")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "ordered_map.py", "content": r'''
import random

FNV_OFFSET = 2166136261
FNV_PRIME = 16777619
MASK32 = 0xFFFFFFFF


def fnv1a(text):
    """The 32-bit FNV-1a hash of a string."""
    value = FNV_OFFSET
    for byte in text.encode("utf-8"):
        value ^= byte
        value = (value * FNV_PRIME) & MASK32
    return value


class MapNode:
    """One node of the search-tree backend."""

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BSTMap:
    """An ordered map backed by an unbalanced binary search tree."""

    def __init__(self):
        self.root = None
        self.comparisons = 0
        self._size = 0

    def __len__(self):
        return self._size

    def put(self, key, value):
        """Insert or replace, counting one comparison per node visited."""
        if self.root is None:
            self.root = MapNode(key, value)
            self._size += 1
            return
        node = self.root
        while True:
            self.comparisons += 1
            if key == node.key:
                node.value = value
                return
            if key < node.key:
                if node.left is None:
                    node.left = MapNode(key, value)
                    self._size += 1
                    return
                node = node.left
            else:
                if node.right is None:
                    node.right = MapNode(key, value)
                    self._size += 1
                    return
                node = node.right

    def _find(self, key):
        """The node holding key, or None."""
        node = self.root
        while node is not None:
            self.comparisons += 1
            if key == node.key:
                return node
            node = node.left if key < node.key else node.right
        return None

    def get(self, key, default=None):
        """The value, or default, counting one comparison per node visited."""
        node = self._find(key)
        return default if node is None else node.value

    def delete(self, key):
        """Remove a key; True when something went."""
        if self._find(key) is None:
            return False
        self.root = self._delete(self.root, key)
        self._size -= 1
        return True

    def _delete(self, node, key):
        """Remove key from this subtree and return its new root."""
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.key = successor.key
            node.value = successor.value
            node.right = self._delete(node.right, successor.key)
        return node

    def items(self):
        """Every (key, value) pair in ascending key order."""
        pairs = []

        def walk(node):
            if node is None:
                return
            walk(node.left)
            pairs.append((node.key, node.value))
            walk(node.right)

        walk(self.root)
        return pairs

    def range_keys(self, low, high):
        """Keys with low <= key <= high, ascending, pruning subtrees."""
        keys = []
        if low > high:
            return keys

        def walk(node):
            if node is None:
                return
            if node.key > low:
                walk(node.left)
            if low <= node.key <= high:
                keys.append(node.key)
            if node.key < high:
                walk(node.right)

        walk(self.root)
        return keys

    def floor_key(self, key):
        """The largest key <= key, or None."""
        best = None
        node = self.root
        while node is not None:
            if node.key == key:
                return node.key
            if node.key < key:
                best = node.key
                node = node.right
            else:
                node = node.left
        return best

    def ceiling_key(self, key):
        """The smallest key >= key, or None."""
        best = None
        node = self.root
        while node is not None:
            if node.key == key:
                return node.key
            if node.key > key:
                best = node.key
                node = node.left
            else:
                node = node.right
        return best


class HashMap:
    """An ordered map backed by a chained hash table."""

    def __init__(self, capacity=8, load_factor=0.75):
        self.capacity = capacity
        self.load_factor = load_factor
        self.comparisons = 0
        self.resizes = 0
        self._size = 0
        self._buckets = [[] for _ in range(capacity)]

    def __len__(self):
        return self._size

    def _index(self, key):
        """Which bucket a key belongs in."""
        return fnv1a(repr(key)) % self.capacity

    def put(self, key, value):
        """Insert or replace, resizing past the load factor."""
        bucket = self._buckets[self._index(key)]
        for position, (existing, _) in enumerate(bucket):
            self.comparisons += 1
            if existing == key:
                bucket[position] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self._size / self.capacity > self.load_factor:
            self._resize(self.capacity * 2)

    def _resize(self, capacity):
        """Double the table and rehash, without counting comparisons."""
        pairs = [pair for bucket in self._buckets for pair in bucket]
        self.capacity = capacity
        self._buckets = [[] for _ in range(capacity)]
        for key, value in pairs:
            self._buckets[self._index(key)].append((key, value))
        self.resizes += 1

    def get(self, key, default=None):
        """The value, or default, counting one comparison per entry examined."""
        for existing, value in self._buckets[self._index(key)]:
            self.comparisons += 1
            if existing == key:
                return value
        return default

    def delete(self, key):
        """Remove a key; True when something went."""
        bucket = self._buckets[self._index(key)]
        for position, (existing, _) in enumerate(bucket):
            self.comparisons += 1
            if existing == key:
                bucket.pop(position)
                self._size -= 1
                return True
        return False

    def items(self):
        """Every (key, value) pair in ascending key order."""
        pairs = [pair for bucket in self._buckets for pair in bucket]
        pairs.sort(key=lambda pair: pair[0])
        return pairs

    def range_keys(self, low, high):
        """Keys with low <= key <= high, ascending."""
        if low > high:
            return []
        return [key for key, _ in self.items() if low <= key <= high]

    def floor_key(self, key):
        """The largest key <= key, or None."""
        best = None
        for existing, _ in self.items():
            if existing <= key:
                best = existing
            else:
                break
        return best

    def ceiling_key(self, key):
        """The smallest key >= key, or None."""
        for existing, _ in self.items():
            if existing >= key:
                return existing
        return None


class OrderedMap:
    """The ADT: one surface, two interchangeable backends."""

    BACKENDS = {"bst": BSTMap, "hash": HashMap}

    def __init__(self, backend="bst"):
        if backend not in self.BACKENDS:
            raise ValueError(f"unknown backend {backend!r}")
        self.backend = backend
        self.store = self.BACKENDS[backend]()

    def __len__(self):
        return len(self.store)

    def __contains__(self, key):
        return self.store.get(key, _MISSING) is not _MISSING

    def __getitem__(self, key):
        """The value, or KeyError."""
        value = self.store.get(key, _MISSING)
        if value is _MISSING:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.store.put(key, value)

    def put(self, key, value):
        """Insert or replace one pair."""
        self.store.put(key, value)

    def get(self, key, default=None):
        """The value, or default."""
        return self.store.get(key, default)

    def delete(self, key):
        """Remove a key; True when something went."""
        return self.store.delete(key)

    def items(self):
        """Pairs in ascending key order."""
        return self.store.items()

    def keys(self):
        """Keys in ascending order."""
        return [key for key, _ in self.store.items()]

    def min_key(self):
        """The smallest key, or None."""
        keys = self.keys()
        return keys[0] if keys else None

    def max_key(self):
        """The largest key, or None."""
        keys = self.keys()
        return keys[-1] if keys else None

    def range_keys(self, low, high):
        """Keys with low <= key <= high, ascending."""
        return self.store.range_keys(low, high)

    def floor_key(self, key):
        """The largest key <= key, or None."""
        return self.store.floor_key(key)

    def ceiling_key(self, key):
        """The smallest key >= key, or None."""
        return self.store.ceiling_key(key)


_MISSING = object()


def benchmark(backend, n=2000, seed=7):
    """Build a map of n random keys, look them all up, and report the cost."""
    rng = random.Random(seed)
    keys = rng.sample(range(n * 10), n)
    mapping = OrderedMap(backend)
    for key in keys:
        mapping.put(key, key * 2)
    put_comparisons = mapping.store.comparisons
    mapping.store.comparisons = 0
    hits = 0
    for key in keys:
        if mapping.get(key) == key * 2:
            hits += 1
    return {
        "backend": backend,
        "n": n,
        "put_comparisons": put_comparisons,
        "get_comparisons": mapping.store.comparisons,
        "hits": hits,
        "ordered_first": mapping.keys()[0],
    }
'''},
            {"name": "main.py", "content": r'''
from ordered_map import benchmark

print(f"{'backend':<8}{'n':>7}{'put cmp':>10}{'get cmp':>10}{'per get':>10}")
for n in (500, 2000):
    for backend in ("bst", "hash"):
        report = benchmark(backend, n)
        print(f"{report['backend']:<8}{report['n']:>7}{report['put_comparisons']:>10}"
              f"{report['get_comparisons']:>10}{report['get_comparisons'] / n:>10.2f}")
'''},
        ],
        "tests": [
            {"name": "Both backends satisfy the same basic contract", "code": r'''
from ordered_map import OrderedMap
for _backend in ("bst", "hash"):
    _m = OrderedMap(_backend)
    assert len(_m) == 0, f"{_backend}: a fresh map has length 0, got {len(_m)}"
    assert _m.get("nope") is None and _m.get("nope", -1) == -1, f"{_backend}: get default"
    _m.put(5, "five")
    _m[3] = "three"
    _m.put(9, "nine")
    assert len(_m) == 3, f"{_backend}: length is {len(_m)}, expected 3"
    assert _m[5] == "five" and _m.get(3) == "three", f"{_backend}: lookups are wrong"
    _m.put(5, "FIVE")
    assert _m[5] == "FIVE" and len(_m) == 3, f"{_backend}: put must replace, not duplicate"
    assert (3 in _m) and (4 not in _m), f"{_backend}: __contains__ is wrong"
    try:
        _m[4]
        assert False, f"{_backend}: __getitem__ on a missing key should raise KeyError"
    except KeyError:
        pass
try:
    OrderedMap("btree")
    assert False, "an unknown backend should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Deletion, including all three tree cases", "code": r'''
from ordered_map import OrderedMap
for _backend in ("bst", "hash"):
    _m = OrderedMap(_backend)
    for _k in [50, 30, 70, 20, 40, 60, 80]:
        _m.put(_k, _k * 10)
    assert _m.delete(20) is True, f"{_backend}: deleting a leaf"
    assert _m.delete(30) is True, f"{_backend}: deleting a one-child node"
    assert _m.delete(70) is True, f"{_backend}: deleting a two-child node"
    assert _m.delete(70) is False, f"{_backend}: deleting an absent key returns False"
    assert len(_m) == 4, f"{_backend}: length is {len(_m)}, expected 4"
    assert _m.keys() == [40, 50, 60, 80], f"{_backend}: keys are {_m.keys()!r}"
    assert _m[40] == 400 and _m[80] == 800, f"{_backend}: values were corrupted by deletion"
    assert _m.delete(50) is True and _m.keys() == [40, 60, 80], \
        f"{_backend}: deleting the root left {_m.keys()!r}"
'''},
            {"name": "keys() and items() come back ordered on both backends", "code": r'''
from ordered_map import OrderedMap
import random as _random
_rng = _random.Random(7)
_keys = _rng.sample(range(10000), 400)
for _backend in ("bst", "hash"):
    _m = OrderedMap(_backend)
    for _k in _keys:
        _m.put(_k, -_k)
    assert _m.keys() == sorted(_keys), f"{_backend}: keys() must be ascending"
    assert _m.items() == [(_k, -_k) for _k in sorted(_keys)], f"{_backend}: items() is wrong"
    assert OrderedMap(_backend).keys() == [], f"{_backend}: an empty map has no keys"
    assert OrderedMap(_backend).items() == [], f"{_backend}: an empty map has no items"
'''},
            {"name": "min_key and max_key", "code": r'''
from ordered_map import OrderedMap
for _backend in ("bst", "hash"):
    _empty = OrderedMap(_backend)
    assert _empty.min_key() is None and _empty.max_key() is None, \
        f"{_backend}: an empty map has no smallest or largest key"
    _m = OrderedMap(_backend)
    for _k in [40, 10, 90, 25]:
        _m.put(_k, _k)
    assert (_m.min_key(), _m.max_key()) == (10, 90), \
        f"{_backend}: got {(_m.min_key(), _m.max_key())!r}, expected (10, 90)"
    _m.delete(10)
    _m.delete(90)
    assert (_m.min_key(), _m.max_key()) == (25, 40), \
        f"{_backend}: after deleting both ends, got {(_m.min_key(), _m.max_key())!r}"
'''},
            {"name": "range_keys is inclusive at both ends", "code": r'''
from ordered_map import OrderedMap
for _backend in ("bst", "hash"):
    _m = OrderedMap(_backend)
    for _k in [10, 20, 30, 40, 50, 60, 70]:
        _m.put(_k, _k)
    assert _m.range_keys(20, 50) == [20, 30, 40, 50], \
        f"{_backend}: range_keys(20, 50) gave {_m.range_keys(20, 50)!r}"
    assert _m.range_keys(25, 45) == [30, 40], f"{_backend}: got {_m.range_keys(25, 45)!r}"
    assert _m.range_keys(0, 100) == [10, 20, 30, 40, 50, 60, 70], f"{_backend}: whole range"
    assert _m.range_keys(31, 39) == [], f"{_backend}: a gap holds no keys"
    assert _m.range_keys(50, 20) == [], f"{_backend}: an inverted range is empty"
    assert _m.range_keys(70, 70) == [70], f"{_backend}: a single-key range"
    assert _m.range_keys(80, 90) == [], f"{_backend}: above every key"
    assert OrderedMap(_backend).range_keys(0, 10) == [], f"{_backend}: an empty map"
'''},
            {"name": "floor_key and ceiling_key", "code": r'''
from ordered_map import OrderedMap
for _backend in ("bst", "hash"):
    _empty = OrderedMap(_backend)
    assert _empty.floor_key(5) is None and _empty.ceiling_key(5) is None, \
        f"{_backend}: an empty map has neither"
    _m = OrderedMap(_backend)
    for _k in [10, 20, 30, 40, 50]:
        _m.put(_k, _k)
    for _probe, _want in [(30, 30), (35, 30), (10, 10), (9, None), (99, 50), (50, 50)]:
        _got = _m.floor_key(_probe)
        assert _got == _want, f"{_backend}: floor_key({_probe}) gave {_got!r}, expected {_want!r}"
    for _probe, _want in [(30, 30), (35, 40), (50, 50), (51, None), (0, 10), (10, 10)]:
        _got = _m.ceiling_key(_probe)
        assert _got == _want, f"{_backend}: ceiling_key({_probe}) gave {_got!r}, expected {_want!r}"
'''},
            {"name": "Both backends match a reference dict under random traffic", "code": r'''
from ordered_map import OrderedMap
import random as _random
for _backend in ("bst", "hash"):
    _rng = _random.Random(11)
    _m = OrderedMap(_backend)
    _ref = {}
    for _step in range(4000):
        _key = _rng.randint(0, 500)
        _roll = _rng.random()
        if _roll < 0.6:
            _value = _rng.randint(0, 10 ** 6)
            _m.put(_key, _value)
            _ref[_key] = _value
        elif _roll < 0.8:
            assert _m.delete(_key) == (_key in _ref), \
                f"{_backend}: delete({_key}) disagreed with the reference"
            _ref.pop(_key, None)
        else:
            assert _m.get(_key, "MISS") == _ref.get(_key, "MISS"), \
                f"{_backend}: get({_key}) gave {_m.get(_key, 'MISS')!r}"
    assert len(_m) == len(_ref), f"{_backend}: holds {len(_m)} keys, the dict holds {len(_ref)}"
    assert _m.items() == sorted(_ref.items()), f"{_backend}: the contents diverged"
'''},
            {"name": "The hash backend really does hash and resize", "code": r'''
from ordered_map import OrderedMap, HashMap, fnv1a
assert fnv1a("") == 2166136261, f"fnv1a('') gave {fnv1a('')!r}"
assert fnv1a("a") == 3826002220, f"fnv1a('a') gave {fnv1a('a')!r}"
assert fnv1a("foobar") == 3214735720, f"fnv1a('foobar') gave {fnv1a('foobar')!r}"
_m = OrderedMap("hash")
assert _m.store.capacity == 8, f"the table starts at capacity 8, got {_m.store.capacity!r}"
for _i in range(100):
    _m.put(_i, _i)
assert _m.store.capacity == 256, f"100 keys should end at capacity 256, got {_m.store.capacity!r}"
assert _m.store.resizes == 5, f"that is 5 doublings, got {_m.store.resizes!r}"
assert _m.keys() == list(range(100)), "every key must survive rehashing"
_bucket_sizes = [len(_b) for _b in _m.store._buckets]
assert max(_bucket_sizes) <= 5, \
    f"the longest chain is {max(_bucket_sizes)} — FNV-1a should spread 100 keys over 256 buckets"
'''},
            {"name": "benchmark is reproducible and backend-agnostic", "code": r'''
from ordered_map import benchmark
_bst = benchmark("bst", 2000)
_hash = benchmark("hash", 2000)
for _report, _name in [(_bst, "bst"), (_hash, "hash")]:
    for _field in ("backend", "n", "put_comparisons", "get_comparisons", "hits", "ordered_first"):
        assert _field in _report, f"{_name}: the report is missing {_field!r}"
    assert _report["n"] == 2000 and _report["hits"] == 2000, \
        f"{_name}: every key was inserted, so every lookup must hit; got {_report!r}"
assert _bst["ordered_first"] == _hash["ordered_first"], \
    f"the two backends disagree on the smallest key: {_bst['ordered_first']!r} vs {_hash['ordered_first']!r}"
assert benchmark("bst", 500) == benchmark("bst", 500), "the same seed must give the same numbers"
assert benchmark("hash", 500, seed=1) != benchmark("hash", 500, seed=2), \
    "different seeds should draw different keys"
'''},
            {"name": "The measurement shows the cost gap it is meant to show", "code": r'''
from ordered_map import benchmark
_n = 2000
_bst = benchmark("bst", _n)
_hash = benchmark("hash", _n)
assert _bst["get_comparisons"] > 5 * _n, \
    f"a tree of {_n} random keys should cost about log2(n) comparisons per lookup, got {_bst['get_comparisons']}"
assert _bst["get_comparisons"] < 40 * _n, \
    f"{_bst['get_comparisons']} comparisons is far more than a random BST should need — check the descent"
assert _hash["get_comparisons"] < 4 * _n, \
    f"a hash lookup should cost about one comparison, got {_hash['get_comparisons'] / _n:.2f} per lookup"
assert _hash["get_comparisons"] * 3 < _bst["get_comparisons"], \
    f"the hash backend should be far cheaper per lookup: {_hash['get_comparisons']} vs {_bst['get_comparisons']}"
assert _bst["put_comparisons"] > 0 and _hash["put_comparisons"] >= 0, \
    "insertions must be counted too"
'''},
            {"name": "ordered_map.py is import-clean", "code": r'''
_src = open("ordered_map.py").read()
assert "print(" not in _src, "ordered_map.py is a library; the printing belongs in main.py"
assert "import time" not in _src and "time.time" not in _src, \
    "the benchmark reports operation counts, not wall-clock seconds"
'''},
        ],
    },
}
