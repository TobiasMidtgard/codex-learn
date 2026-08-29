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
            "lab": {
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
            },
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
                "Random insertion gives height ~1.39 log2 n; sorted insertion gives a linked list",
            ],
            "lab": {
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
            },
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
