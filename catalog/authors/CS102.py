"""CS102 — Object-Oriented Programming."""

COURSE = {
    "id": "CS102",
    "title": "Object-Oriented Programming",
    "year": 1,
    "level": "Beginner",
    "prereqs": ["CS101"],
    "stack": ["Python", "Java (reference)"],
    "credits": 10,
    "hours": 120,
    "icon": "◈",
    "summary": (
        "Objects are the second way to organise a program: state and the operations "
        "on that state, bundled and named. You build immutable value types, an "
        "abstract hierarchy that dispatches polymorphically, classes that defend "
        "their own invariants through properties, and containers that plug into "
        "Python's own protocols — finishing with a persisted library-catalogue model."
    ),
    "outcomes": [
        "Design a class whose invariants cannot be violated from outside it",
        "Implement the dunder protocols for equality, ordering, arithmetic and display",
        "Distinguish an is-a relationship from a has-a one and model each correctly",
        "Define an abstract base class and dispatch polymorphically over its subtypes",
        "Encapsulate state behind properties that validate on every write",
        "Explain class-attribute versus instance-attribute lookup and the shadowing rule",
        "Persist an object graph to JSON and reconstruct it without losing type",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Ramalho, *Fluent Python*, 2nd ed. — chapters 1, 11-14",
        "Gamma, Helm, Johnson & Vlissides, *Design Patterns* — chapter 1",
        "Python Data Model, docs.python.org/3/reference/datamodel.html — section 3.3",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Objects, state and the data model",
            "summary": "Classes as value types, and the dunder methods that make them feel built-in.",
            "concepts": [
                "A class describes state plus behaviour; an instance holds one set of that state",
                "`__init__` initialises an already-created object; it is not a constructor",
                "`self` is the receiver, passed explicitly — the same binding Java hides",
                "Value semantics: `__eq__` and `__hash__` must agree, or containers misbehave",
                "Operator overloading via `__add__`/`__mul__`, and `NotImplemented` as the polite refusal",
                "`__repr__` is for the programmer and should round-trip through `eval` where it can",
                "Immutability by convention (`_name`), by `__slots__`, and by overriding `__setattr__`",
            ],
            "quiz": {
                "title": "Value semantics and the data model",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`Vector2D(3, 4)` is evaluated. What is `__init__`'s part in it?",
                        "opts": [
                            "It creates the object and returns it to the caller",
                            "It is handed an object that already exists, fills in its state, and returns `None`",
                            "It runs only when the class defines no `__new__`",
                            "It reserves the memory, and Python fills in the attributes afterwards",
                        ],
                        "a": 1,
                        "why": r"""
Two things happen and only the second one is `__init__`. `Vector2D.__new__` allocates
the object; `__init__` is then handed that object as `self` and initialises it. It must
return `None` — returning anything else is a `TypeError`, which is the language saying
plainly that this is an initialiser and not a constructor. The distinction is invisible
until it is not: `__new__` is the hook you need for a class that interns its instances,
or that subclasses an immutable built-in like `tuple`, because by the time `__init__`
runs the value is already fixed.
""",
                    },
                    {
                        "q": "A class defines `__eq__` and leaves `__hash__` alone. What does `hash(obj)` do?",
                        "opts": [
                            "Falls back to the identity hash inherited from `object`",
                            "Returns `0` — legal, but it turns every dict into a linked list",
                            "Raises `TypeError`: defining `__eq__` sets `__hash__` to `None`",
                            "Raises `AttributeError`, because the method is missing",
                        ],
                        "a": 2,
                        "why": r"""
Python puts `__hash__ = None` in the class for you when `__eq__` is defined and
`__hash__` is not, and instances become unhashable — no sets, no dict keys. That looks
officious until you see the alternative: the inherited hash is based on identity, so two
objects your new `__eq__` calls equal would land in different buckets, and a dict would
cheerfully hold both. Rather than let that rot quietly, the language breaks loudly. Write
`__hash__` alongside `__eq__` over the same fields, or accept that the type is not
hashable — which is the right answer for anything mutable.
""",
                    },
                    {
                        "q": "`Vector2D.__add__` is handed an `int`. What should it return?",
                        "opts": [
                            "`NotImplemented`, so Python can ask the other operand and then raise `TypeError` itself",
                            "`False`, since the addition did not happen",
                            "`None`, which Python reads as a refusal",
                            "It should `raise NotImplementedError`",
                        ],
                        "a": 0,
                        "why": r"""
`NotImplemented` is a singleton meaning *I decline — ask someone else*. Python then tries
`int.__radd__`, and when that declines too it raises `TypeError: unsupported operand
type(s)`, a message naming both types and far better than anything you would have
written. The refusals that are not refusals: `False` makes `v + 5` evaluate to `False`,
`None` makes it `None`, and `NotImplementedError` is a real exception meant for an
abstract method a subclass forgot — raising it aborts the reflected-operand machinery and
reports the wrong problem entirely.
""",
                    },
                    {
                        "q": "A class defines `__repr__` and no `__str__`. What does `print(obj)` show?",
                        "opts": [
                            "`<Vector2D object at 0x7f...>`",
                            "An empty line",
                            "`TypeError`",
                            "Whatever `__repr__` returns — `__str__` falls back to it",
                        ],
                        "a": 3,
                        "why": r"""
`object.__str__` calls `__repr__`, so one good repr covers printing as well. The reverse
does not hold: define only `__str__` and `repr(v)` stays the angle-bracket default —
which is what you will see *inside a list*, because a container displays the reprs of its
elements and never their strs. That asymmetry is the reason for the usual advice: write
`__repr__` first, and add `__str__` only when a human-facing form genuinely differs from
the programmer-facing one.
""",
                    },
                    {
                        "q": "`2 * v`, where `v` is a `Vector2D`. How does Python reach your code?",
                        "opts": [
                            "It rewrites the expression as `v * 2` and calls `__mul__`",
                            "It asks `int.__mul__(2, v)` first, is told `NotImplemented`, then calls `Vector2D.__rmul__(v, 2)`",
                            "It calls `Vector2D.__mul__(v, 2)` directly, because the operands are different types",
                            "It raises `TypeError` — the left operand decides, and `int` cannot multiply a vector",
                        ],
                        "a": 1,
                        "why": r"""
The left operand is asked first. `int` has no idea what a vector is, returns
`NotImplemented`, and only then does the right operand get its reflected hook. There is
one documented exception, and it is not this case: when the right operand's type is a
*proper subclass* of the left's and overrides the reflected method, Python tries the
subclass's `__rmul__` before the base's `__mul__`, so a subclass can always override an
operator it inherited. `int` and `Vector2D` are unrelated types, so the ordinary order
holds here. Nothing is rewritten either: `__rmul__` is a separate method, and it
receives the vector as `self` and the
`2` as the argument, so the operands arrive swapped. Delegating it straight to `__mul__`
is right for a scalar, where the product commutes — for matrix multiplication that same
delegation would be a bug, and that is the case worth remembering.
""",
                    },
                    {
                        "q": "`__slots__ = ('x', 'y')` is added to a class. What does it actually do?",
                        "opts": [
                            "Makes the instances immutable",
                            "Makes `x` and `y` read-only",
                            "Replaces the per-instance `__dict__` with two fixed descriptors, so any other attribute raises `AttributeError`",
                            "Stops the class being subclassed",
                        ],
                        "a": 2,
                        "why": r"""
Slots trade flexibility for memory and for catching typos: there is no instance
dictionary, so `v.z = 1` fails where it would silently have worked. What slots do *not*
do is stop `v.x = 9` — that is an ordinary write to a slot descriptor, which is exactly
why the lab has to refuse it in `__setattr__` as well. And a subclass that does not
declare `__slots__` of its own quietly gets a `__dict__` back, taking the saving with it.
""",
                    },
                ],
            },
            "blanks": {
                "title": "A value type, hole by hole",
                "minutes": 9,
                "caption": "money.py — five decisions that make a value behave like one",
                "lang": "python",
                "brief": r'''
`Money` is the same shape as the `Vector2D` you are about to build: two components, no
identity of its own, and no way to change it once it exists. Every hole below is a place
where a value type is usually got wrong.

Nothing runs here — you are choosing symbols, not writing code.
''',
                "listing": '''class Money:
    """A fixed amount in one currency: a value, not a container."""

    __slots__ = ("amount", "currency")

    def __init__(self, amount, currency):
        # __setattr__ below refuses every write, so reach past it exactly here
        ___(self, "amount", round(float(amount), 2))
        object.__setattr__(self, "currency", currency.upper())

    def __setattr__(self, name, value):
        raise ___("Money is immutable")

    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"

    def __eq__(self, other):
        if not isinstance(other, Money):
            return ___
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self):
        return hash(___)

    def __mul__(self, factor):
        if isinstance(factor, bool) or not isinstance(factor, (int, float)):
            return NotImplemented
        return Money(self.amount * factor, self.currency)

    # scaling commutes, so the reflected hook is the very same function
    __rmul__ = ___
''',
                "blanks": [
                    {
                        "prompt": "`__init__` has to write two attributes through a guard that refuses every write.",
                        "hole": "?",
                        "opts": [
                            "setattr",
                            "object.__setattr__",
                            "Money.__setattr__",
                            "self.__setattr__",
                        ],
                        "a": 1,
                        "why": "`object.__setattr__` is the plain machinery your guard is standing in front of. Calling it by name is how you step around your own refusal exactly once, in the one place that is entitled to.",
                        "whys": [
                            "`setattr(self, name, value)` is spelled differently but is identical to `self.name = value`: it looks the method up on the type and lands straight back in the guard, so construction fails with the message meant for outsiders.",
                            "`object.__setattr__` is the plain machinery your guard is standing in front of. Calling it by name is how you step around your own refusal exactly once, in the one place that is entitled to.",
                            "The arity is right, but this is the guard itself, named explicitly. It raises for `__init__` as readily as for anyone else — the write has to go *above* `Money`, not to it.",
                            "Two problems at once: it is the same refusing method, and the instance is already bound as `self`, so passing it again hands the call one argument too many.",
                        ],
                    },
                    {
                        "prompt": "A refused attribute write should look like every other refused attribute write in Python.",
                        "hole": "?",
                        "opts": [
                            "NotImplementedError",
                            "TypeError",
                            "ValueError",
                            "AttributeError",
                        ],
                        "a": 3,
                        "why": "`AttributeError` is what Python itself raises for a write it cannot perform: a slot that does not exist, a property with no setter, an attribute on a `tuple`. Matching it means `except AttributeError` around a write keeps working whether an object defends itself by hand or with `@property`.",
                        "whys": [
                            "`NotImplementedError` announces a method a subclass was supposed to override. Nothing here is unfinished — this refusal is the finished behaviour.",
                            "`TypeError` is about the *kind* of thing that was passed — a string where a number was wanted. The type here is fine; it is the operation that is refused.",
                            "`ValueError` says the value was the wrong one, which invites the caller to try a different value. No value is acceptable: the attribute cannot be written at all.",
                            "`AttributeError` is what Python itself raises for a write it cannot perform: a slot that does not exist, a property with no setter, an attribute on a `tuple`. Matching it means `except AttributeError` around a write keeps working whether an object defends itself by hand or with `@property`.",
                        ],
                    },
                    {
                        "prompt": "`Money(3.5, 'EUR') == 3.5` should be `False`, not an exception.",
                        "hole": "?",
                        "opts": [
                            "NotImplemented",
                            "False",
                            "None",
                            "NotImplementedError",
                        ],
                        "a": 0,
                        "why": "Returning `NotImplemented` lets Python ask the other operand, and when `float.__eq__` declines as well, fall back to comparing identity — which gives `False`, and gives `!=` the opposite for free.",
                        "whys": [
                            "Returning `NotImplemented` lets Python ask the other operand, and when `float.__eq__` declines as well, fall back to comparing identity — which gives `False`, and gives `!=` the opposite for free.",
                            "`False` is the right result reached the wrong way: it takes the decision away from the other operand, so a class that *does* know how to compare itself with money never gets asked, and never can.",
                            "`None` is falsy, so this even appears to work — until a container relies on `==` and gets a non-boolean back, or someone writes `assert a == b` and reads a confusing failure.",
                            "That is an exception class, and returning one rather than raising it hands the caller a class object, which is truthy. `Money(1, 'EUR') == 3.5` would come out true.",
                        ],
                    },
                    {
                        "prompt": "Equal objects must hash equally, or a `dict` will lose them.",
                        "hole": "?",
                        "opts": [
                            "id(self)",
                            "[self.amount, self.currency]",
                            "(self.amount, self.currency)",
                            "self",
                        ],
                        "a": 2,
                        "why": "Hash the same fields `__eq__` compares, packed into a tuple — a tuple of hashables is hashable, so the work is already done for you. Equal amounts in the same currency then land in the same bucket, which is the one condition a `dict` needs in order to find them again.",
                        "whys": [
                            "The identity of the object breaks the contract in the quietest possible way: two equal `Money` objects hash differently, so a lookup by an equal key misses the entry, and a `set` keeps both.",
                            "A list is mutable and therefore unhashable, so `hash()` raises `TypeError` and every dictionary insertion fails. Swapping the brackets for parentheses is the whole fix.",
                            "Hash the same fields `__eq__` compares, packed into a tuple — a tuple of hashables is hashable, so the work is already done for you. Equal amounts in the same currency then land in the same bucket, which is the one condition a `dict` needs in order to find them again.",
                            "`hash(self)` calls this very method, so the first hash of the first object recurses until the stack runs out.",
                        ],
                    },
                    {
                        "prompt": "`3 * m` and `m * 3` are the same money, so the reflected hook can be the same function.",
                        "hole": "?",
                        "opts": [
                            "__mul__()",
                            "__mul__",
                            "Money.__mul__",
                            "self.__mul__",
                        ],
                        "a": 1,
                        "why": "Inside the class body `__mul__` is simply a name bound to the function defined a few lines above, so binding a second name to it is enough. The reflected call arrives with the operands swapped, and for a scalar that makes no difference at all.",
                        "whys": [
                            "The parentheses call the function while the class body is still executing, with no arguments at all, so the class never finishes being defined.",
                            "Inside the class body `__mul__` is simply a name bound to the function defined a few lines above, so binding a second name to it is enough. The reflected call arrives with the operands swapped, and for a scalar that makes no difference at all.",
                            "The class does not exist yet — its own body is what is running — so the name `Money` is unbound and the module fails to import.",
                            "`self` is a parameter of the methods, not a name in the class body. At class-definition time there is no instance for it to refer to.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How many cards does the set keep?",
                "minutes": 7,
                "brief": r'''
`Card` was written for a game that cares about rank and not about suit, so two cards
count as the same card when their ranks match. `__hash__` agrees with `__eq__`, as it
must — hash the fields you compare, compare the fields you hash.

```python
class Card:
    """Two cards count as the same card when their ranks match."""

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank

    def __hash__(self):
        return hash(self.rank)


hand = [Card("A", "spades"), Card("K", "hearts"), Card("A", "hearts"),
        Card("Q", "clubs"), Card("K", "spades"), Card("A", "diamonds")]

print(len(set(hand)))
```
''',
                "prompt": "How many members does `set(hand)` have?",
                "note": "A whole number. Nothing here is random, and nothing depends on the order.",
                "figure": "Six `Card` objects go into the set: the aces of spades, hearts and diamonds, the kings of hearts and spades, and the queen of clubs. `Card.__eq__` compares `rank` and nothing else, and `Card.__hash__` hashes the same single field.",
                "given": [
                    {"label": "Cards in `hand`", "value": "6"},
                    {"label": "Distinct suits", "value": "4"},
                    {"label": "`__eq__` compares", "value": "`self.rank == other.rank`"},
                    {"label": "`__hash__` returns", "value": "`hash(self.rank)`"},
                ],
                "aside": "The set never looks at your attributes. It calls `__hash__` to choose a bucket and `__eq__` to settle what shares one.",
                "answer": 3,
                "tol": 0,
                "unit": "members",
                "hint": "Sort the six cards into piles that `__eq__` cannot tell apart, then count the piles.",
                "wrong": "Count the piles `__eq__` makes — not the cards, and not the suits. `Card` was written to compare ranks alone, and the set has no other opinion available to it.",
                "why": r"""
Three: one ace, one king, one queen. The set asks `__hash__` for a bucket and `__eq__` to
settle ties, and this `__eq__` looks at `rank` alone — so the three aces collapse into one
member, the two kings into another, and the queen makes the third. The suit is real data,
sitting on every one of the six objects, and completely invisible to the container,
because nothing the container calls ever mentions it. That is the lesson worth carrying
out of this module: a set, a dict key, `list.remove`, `in` — every one of them is only as
good as the two methods you wrote. Compare rank *and* suit and the same six cards give
six members.
""",
            },
            "lab": {
                "title": "An immutable Vector2D",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Build `Vector2D` — a *value* type. Two vectors with the same components are
interchangeable, and no vector ever changes after construction.

## Construction and display

`Vector2D(x, y)` stores both components **as floats** in `self.x` and `self.y`.

```text
repr(Vector2D(3, 4))  ->  "Vector2D(3.0, 4.0)"
```

The repr must round-trip: `eval(repr(v)) == v`.

## Value semantics

- `__eq__` — equal when both components are equal. Comparing with anything that
  is not a `Vector2D` returns `NotImplemented`, so `Vector2D(1, 2) == (1, 2)`
  is simply `False`.
- `__hash__` — hash the `(x, y)` pair, so vectors work as set members and dict
  keys. Defining `__eq__` without `__hash__` makes the class unhashable.

## Arithmetic

- `__add__`, `__sub__` — vector plus/minus vector.
- `__mul__` and `__rmul__` — vector times a real scalar, on either side.
- `__neg__` — `-v`.
- Anything else returns `NotImplemented`, which Python turns into a `TypeError`.
  So `v + 5` and `v * w` both raise `TypeError`.

## Geometry

- `dot(other)` — the scalar product.
- `magnitude()` — the Euclidean length. `Vector2D(3, 4).magnitude()` is `5.0`.

## Immutability

Assigning to an attribute must raise `AttributeError`, and so must deleting one:

```text
v = Vector2D(1, 2)
v.x = 9        ->  AttributeError
del v.y        ->  AttributeError
```

Override `__setattr__` and `__delattr__` to refuse — which means `__init__`
cannot use `self.x = ...` either. Reach past your own guard with
`object.__setattr__(self, "x", float(x))`.
''',
                "files": [{"name": "main.py", "content": r'''
import math


class Vector2D:
    """An immutable 2-D vector with value semantics."""

    __slots__ = ("x", "y")

    def __init__(self, x, y):
        # store both components as floats WITHOUT using self.x = ...
        pass

    def __setattr__(self, name, value):
        # refuse every attribute write
        pass

    def __delattr__(self, name):
        # refuse every attribute deletion
        pass

    def __repr__(self):
        pass

    def __eq__(self, other):
        pass

    def __hash__(self):
        pass

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, scalar):
        pass

    def __rmul__(self, scalar):
        pass

    def __neg__(self):
        pass

    def dot(self, other):
        """The scalar product of two vectors."""
        pass

    def magnitude(self):
        """Euclidean length."""
        pass


a = Vector2D(3, 4)
b = Vector2D(-1, 2)
print("a         =", repr(a))
print("a + b     =", a + b)
print("2 * a     =", 2 * a)
print("a . b     =", a.dot(b))
print("|a|       =", a.magnitude())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


class Vector2D:
    """An immutable 2-D vector with value semantics."""

    __slots__ = ("x", "y")

    def __init__(self, x, y):
        object.__setattr__(self, "x", float(x))
        object.__setattr__(self, "y", float(y))

    def __setattr__(self, name, value):
        raise AttributeError("Vector2D is immutable")

    def __delattr__(self, name):
        raise AttributeError("Vector2D is immutable")

    def __repr__(self):
        return f"Vector2D({self.x!r}, {self.y!r})"

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        if isinstance(scalar, bool) or not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def dot(self, other):
        """The scalar product of two vectors."""
        return self.x * other.x + self.y * other.y

    def magnitude(self):
        """Euclidean length."""
        return math.hypot(self.x, self.y)


a = Vector2D(3, 4)
b = Vector2D(-1, 2)
print("a         =", repr(a))
print("a + b     =", a + b)
print("2 * a     =", 2 * a)
print("a . b     =", a.dot(b))
print("|a|       =", a.magnitude())
'''}],
                "hints": [
                    "`__init__` runs *after* your `__setattr__` guard is installed, so `self.x = x` inside it hits the guard. Use `object.__setattr__(self, \"x\", float(x))`.",
                    "`__repr__` should print the components with `!r`: `f\"Vector2D({self.x!r}, {self.y!r})\"`. Because they are floats, `3` comes back as `3.0`.",
                    "In `__eq__` and `__add__`, `return NotImplemented` (the singleton) for a wrong operand type — do not `raise NotImplementedError`, and do not return `False`.",
                    "`__rmul__` handles `2 * v`. It can simply delegate: `return self.__mul__(scalar)`.",
                ],
                "tests": [
                    {"name": "Construction, float coercion and repr", "code": r'''
_v = Vector2D(3, 4)
assert isinstance(_v.x, float) and isinstance(_v.y, float), \
    f"components are {type(_v.x).__name__}/{type(_v.y).__name__}, expected float/float"
assert (_v.x, _v.y) == (3.0, 4.0), f"components are {(_v.x, _v.y)!r}, expected (3.0, 4.0)"
_r = repr(_v)
assert _r == "Vector2D(3.0, 4.0)", f"repr gave {_r!r}, expected 'Vector2D(3.0, 4.0)'"
assert eval(_r) == _v, "repr should round-trip through eval"
'''},
                    {"name": "Equality is by value, not identity", "code": r'''
assert Vector2D(1, 2) == Vector2D(1.0, 2.0), "Equal components mean equal vectors"
assert Vector2D(1, 2) != Vector2D(1, 3), "Different components mean different vectors"
assert not (Vector2D(1, 2) == (1, 2)), "A tuple is not a Vector2D — comparison is False, not a crash"
assert Vector2D(1, 2) != "nope", "Comparison against unrelated types must not raise"
'''},
                    {"name": "Hashing agrees with equality", "code": r'''
_s = {Vector2D(1, 2), Vector2D(1, 2), Vector2D(0, 0)}
assert len(_s) == 2, f"set of three vectors (two equal) has {len(_s)} members, expected 2"
_d = {Vector2D(1, 2): "here"}
assert _d[Vector2D(1, 2)] == "here", "An equal vector should find the same dict entry"
assert hash(Vector2D(1, 2)) == hash(Vector2D(1, 2)), "Equal vectors must hash equally"
'''},
                    {"name": "Addition, subtraction and negation", "code": r'''
_got = Vector2D(3, 4) + Vector2D(-1, 2)
assert _got == Vector2D(2, 6), f"(3,4)+(-1,2) gave {_got!r}, expected Vector2D(2.0, 6.0)"
_got = Vector2D(3, 4) - Vector2D(-1, 2)
assert _got == Vector2D(4, 2), f"(3,4)-(-1,2) gave {_got!r}, expected Vector2D(4.0, 2.0)"
assert -Vector2D(3, -4) == Vector2D(-3, 4), f"-(3,-4) gave {(-Vector2D(3, -4))!r}"
_zero = Vector2D(0, 0)
assert _zero + _zero == _zero, "The zero vector is its own identity"
'''},
                    {"name": "Scalar multiplication on both sides", "code": r'''
assert Vector2D(3, 4) * 2 == Vector2D(6, 8), f"v*2 gave {(Vector2D(3, 4) * 2)!r}"
assert 2 * Vector2D(3, 4) == Vector2D(6, 8), "2*v needs __rmul__"
assert Vector2D(3, 4) * 0.5 == Vector2D(1.5, 2.0), "Float scalars work too"
assert Vector2D(3, 4) * 0 == Vector2D(0, 0), "Scaling by zero collapses the vector"
'''},
                    {"name": "Unsupported operands raise TypeError", "code": r'''
for _expr in ["Vector2D(1, 2) + 5", "Vector2D(1, 2) - 'x'", "Vector2D(1, 2) * Vector2D(1, 2)"]:
    try:
        eval(_expr)
        assert False, f"{_expr} should raise TypeError — return NotImplemented for bad operands"
    except TypeError:
        pass
'''},
                    {"name": "dot and magnitude", "code": r'''
_got = Vector2D(3, 4).dot(Vector2D(1, 2))
assert abs(_got - 11.0) < 1e-12, f"(3,4).dot((1,2)) gave {_got!r}, expected 11.0"
_got = Vector2D(3, 4).magnitude()
assert abs(_got - 5.0) < 1e-12, f"|(3,4)| gave {_got!r}, expected 5.0"
assert Vector2D(0, 0).magnitude() == 0.0, "The zero vector has zero length"
assert abs(Vector2D(1, 1).magnitude() - 2 ** 0.5) < 1e-12, "|(1,1)| is sqrt(2)"
'''},
                    {"name": "Instances are immutable", "code": r'''
_v = Vector2D(1, 2)
try:
    _v.x = 9
    assert False, "Assigning to v.x should raise AttributeError"
except AttributeError:
    pass
try:
    del _v.y
    assert False, "Deleting v.y should raise AttributeError"
except AttributeError:
    pass
assert (_v.x, _v.y) == (1.0, 2.0), f"The vector changed anyway: {_v!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Inheritance, abstraction and polymorphism",
            "summary": "One interface, several implementations, and code that never asks which.",
            "concepts": [
                "Inheritance models is-a; a `Circle` is a `Shape`, a wheel is not a car",
                "`super().__init__(...)` cooperates with the MRO instead of naming a parent",
                "`abc.ABC` + `@abstractmethod`: an incomplete subclass fails at instantiation",
                "Polymorphic dispatch: the call site names the operation, the object picks the code",
                "Template method — a concrete base method built out of abstract ones",
                "Liskov substitution: a subtype must be usable wherever the supertype is",
                "`isinstance` for type questions, `type(self).__name__` for the dynamic class",
            ],
            "quiz": {
                "title": "One interface, several implementations",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A subclass of an abstract `Shape` implements `area()` and forgets `perimeter()`. When does that go wrong?",
                        "opts": [
                            "When `perimeter()` is first called",
                            "At import, when the class statement runs",
                            "At the first attempt to instantiate it — `TypeError`, naming the method still missing",
                            "Never: the abstract method's empty body runs and returns `None`",
                        ],
                        "a": 2,
                        "why": r"""
`ABCMeta` collects the names still marked abstract when the class object is created, and
instantiation is refused while that set is non-empty — so the failure arrives at `Blob()`
with the missing names printed in the message. Defining the class has to stay legal,
because that is exactly how you write an abstract class that extends another abstract
class. And the abstract body never runs at all, which is why leaving it as nothing but a
docstring is the honest way to write one.
""",
                    },
                    {
                        "q": "Which of these should be inheritance rather than composition?",
                        "opts": [
                            "A `Playlist` and the `Track`s it holds",
                            "A `Circle` and the abstract `Shape` it implements",
                            "An `Account` and its transaction `history`",
                            "A `Car` and its `Engine`",
                        ],
                        "a": 1,
                        "why": r"""
Inheritance is a promise about substitutability: anywhere a `Shape` is expected, a
`Circle` must do — and it can, because `Shape` promises only that you can ask for an
area and a perimeter, and a circle answers both without ever contradicting the base. The
other three are ownership — a playlist has tracks, an account has a history, a car has an
engine — and not one of them can stand in for what it holds. The question that sorts them
is never *do these share code*, and it is not whether the English sounds like is-a
either; it is *can I hand this to a function that asked for the base and expect that
function to keep working*. Hold that test in mind for the `Square` two questions along,
where the vocabulary says yes and the behaviour says no.
""",
                    },
                    {
                        "q": "`Square.__init__` could say `Rectangle.__init__(self, side, side)`. Why `super().__init__(side, side)` instead?",
                        "opts": [
                            "`super()` is faster, because it caches the parent",
                            "`super()` skips the parent and calls the grandparent",
                            "Naming a base class from inside a subclass is a syntax error",
                            "`super()` follows the MRO of the object being built, so a later subclass inheriting from two places still gets every base initialised exactly once",
                        ],
                        "a": 3,
                        "why": r"""
With one base and no diamond the two lines call the identical function and the difference
is invisible. It shows up the day somebody writes `class Tile(Square, Drawable)`.
`super()` asks what comes *after the current class* in the MRO of `type(self)` — which is
not always the parent you can see in the file — while a hard-coded name pins the chain,
and lets a shared base run twice or a sibling not run at all. It also means renaming a
base is a one-line change rather than a search.
""",
                    },
                    {
                        "q": "A `Square` inherits from a `Rectangle` whose `width` and `height` can be set independently. What has been broken?",
                        "opts": [
                            "Any code holding what it was told is a `Rectangle`, setting the two sides separately, and expecting both to stick",
                            "Nothing — a square really is a rectangle",
                            "`area()`, which can no longer be inherited",
                            "`isinstance(sq, Rectangle)`, which starts returning `False`",
                        ],
                        "a": 0,
                        "why": r"""
The textbook case against reading is-a off the dictionary. Geometry says a square is a
rectangle; the *type* `Rectangle` promises rather more than geometry does, and one of its
promises is two dimensions that move independently. A `Square` that stays square has to
break that promise, and the code that notices is code that never mentioned `Square` at
all. Liskov's rule is about behaviour, not vocabulary. Two ways out: fix the dimensions
at construction so the promise is never made, or drop the inheritance and let a `Square`
hold a `Rectangle`.
""",
                    },
                    {
                        "q": "`Shape.describe()` calls `self.area()`. Which `area` runs for `Square(2).describe()`, given that `Square` defines none?",
                        "opts": [
                            "`Shape.area`, since that is where `describe` was written",
                            "None — it raises `TypeError`, because `Shape.area` is abstract",
                            "`Rectangle.area`, found by searching from `Square` up the MRO",
                            "A copy of `Rectangle.area` that Python puts on `Square` when the class is created",
                        ],
                        "a": 2,
                        "why": r"""
`self.area` is looked up on the *object*, not in the file where `describe` happens to
live, so the search starts at `Square`, finds nothing, moves to `Rectangle` and stops
there — the abstract `Shape.area` is never reached. That late binding is the whole
mechanism of the template method: the base fixes the shape of the algorithm and each
subclass supplies the steps. Nothing is copied anywhere; there is one function, found by
walking a list.
""",
                    },
                    {
                        "q": "`Shape.__init__` sets `self.name = type(self).__name__`. What is `Square(2).name`?",
                        "opts": [
                            "`'Square'`",
                            "`'Shape'`, because that is the class whose code is running",
                            "`'Rectangle'`, because `Square` delegates its construction there",
                            "`'type'`",
                        ],
                        "a": 0,
                        "why": r"""
`type(self)` is the class of the object in front of you, never the class of the method
doing the asking — `self.__class__` is the same thing spelled differently. That one line
is why no subclass needs a `name` of its own, and why a `Square` reports `'Square'` even
though every line of code involved was written in `Shape`. Hard-code the string in the
base instead and every subclass claims to be a `Shape`: a `repr` built that way is exactly
the sort of quiet wrongness that no test thinks to check.
""",
                    },
                ],
            },
            "blanks": {
                "title": "An abstract base class, hole by hole",
                "minutes": 9,
                "caption": "payroll.py — five decisions, and where the abstraction is actually enforced",
                "lang": "python",
                "brief": r'''
The same hierarchy as the lab, in a domain where the money makes the stakes obvious.
`Employee` is a promise: everyone on the payroll can be asked what they are owed this
month, and nobody has to ask what *kind* of employee they are holding.

Nothing runs here — you are choosing symbols, not writing code.
''',
                "listing": '''from abc import ABC, abstractmethod


class Employee(___):
    """Everyone on the payroll. Nobody is ever *just* an Employee."""

    def __init__(self, name):
        self.name = name
        self.role = ___.__name__

    @___
    def monthly_pay(self):
        """What this employee is owed for one month."""

    def payslip(self):
        return f"{self.name} ({self.role}): {___:.2f}"


class Salaried(Employee):
    """Paid a twelfth of the annual figure, whatever the month holds."""

    def __init__(self, name, annual):
        ___.__init__(name)
        self.annual = annual

    def monthly_pay(self):
        return self.annual / 12
''',
                "blanks": [
                    {
                        "prompt": "What makes the promise enforceable rather than merely documented?",
                        "hole": "?",
                        "opts": [
                            "ABCMeta",
                            "object",
                            "ABC",
                            "abstractmethod",
                        ],
                        "a": 2,
                        "why": "`ABC` is a plain class that carries `ABCMeta` as its metaclass, and inheriting from it is what arms the check refusing to instantiate anything with an abstract method left over. It is the one-line way in; `class Employee(metaclass=ABCMeta)` says the same thing at greater length.",
                        "whys": [
                            "`ABCMeta` is the *metaclass* — the class of which `ABC` is an instance. Inheriting from it would make `Employee` a maker of classes rather than a maker of employees, which is not what any of the code below goes on to do with it.",
                            "Every class inherits from `object` already, so this changes nothing. `@abstractmethod` still marks the method, but with no `ABCMeta` behind the class nothing ever reads the mark: `Employee('Ada')` succeeds, and a subclass that forgot `monthly_pay` fails much later and much less clearly, inside `payslip`.",
                            "`ABC` is a plain class that carries `ABCMeta` as its metaclass, and inheriting from it is what arms the check refusing to instantiate anything with an abstract method left over. It is the one-line way in; `class Employee(metaclass=ABCMeta)` says the same thing at greater length.",
                            "`abstractmethod` is a decorator you apply to a method: a function, not a base class. Putting it in the bases fails while the class statement is still being executed.",
                        ],
                    },
                    {
                        "prompt": "Every payslip names a role, and no subclass writes a line to make that happen.",
                        "hole": "?",
                        "opts": [
                            "type(self)",
                            "Employee",
                            "type(Employee)",
                            "self.role",
                        ],
                        "a": 0,
                        "why": "`type(self)` is the class of the object actually being built, so a `Salaried` records `'Salaried'` even though the line lives in `Employee`. It is the same trick the `Shape` hierarchy uses for its `name`, and it is why the subclasses stay empty of bookkeeping.",
                        "whys": [
                            "`type(self)` is the class of the object actually being built, so a `Salaried` records `'Salaried'` even though the line lives in `Employee`. It is the same trick the `Shape` hierarchy uses for its `name`, and it is why the subclasses stay empty of bookkeeping.",
                            "`Employee.__name__` is the constant string `'Employee'`, evaluated identically for every subclass. Every payslip would claim the same role, and nothing would fail loudly enough for anybody to notice.",
                            "`type(Employee)` is the metaclass, so this records `'ABCMeta'` — a true fact about the class machinery, and a useless one on a payslip.",
                            "`self.role` is what this very line is creating: it does not exist yet, and a string would have no `__name__` even if it did.",
                        ],
                    },
                    {
                        "prompt": "One mark, and a subclass that forgets is stopped at the door.",
                        "hole": "?",
                        "opts": [
                            "staticmethod",
                            "abstractmethod",
                            "property",
                            "classmethod",
                        ],
                        "a": 1,
                        "why": "With the mark in place, a subclass that does not define `monthly_pay` cannot be instantiated at all, and the error names the method — so the mistake surfaces where the object is created rather than in the middle of a payroll run.",
                        "whys": [
                            "`@staticmethod` strips `self` from the call, so the body could not reach a single field of the employee — and it would make the method entirely concrete, which is the opposite of the intent.",
                            "With the mark in place, a subclass that does not define `monthly_pay` cannot be instantiated at all, and the error names the method — so the mistake surfaces where the object is created rather than in the middle of a payroll run.",
                            "`@property` turns it into an attribute read, so the `.2f` line below would call the *result* rather than the method. Pay as a computed attribute is a defensible design, but it is a different one, and it obliges a subclass to supply nothing.",
                            "`@classmethod` binds the class instead of the instance — useful for an alternative constructor, and silent about who has implemented what.",
                        ],
                    },
                    {
                        "prompt": "`payslip` is written once, in the base, and must never learn which subclass it is holding.",
                        "hole": "?",
                        "opts": [
                            "self.monthly_pay",
                            "Employee.monthly_pay(self)",
                            "monthly_pay(self)",
                            "self.monthly_pay()",
                        ],
                        "a": 3,
                        "why": "The call goes through the object, so it finds whichever implementation that object actually has. That is the template method: one line in the base, and the subclasses supply the number.",
                        "whys": [
                            "Without the parentheses this formats the bound method object rather than the number it would have returned, and `:.2f` on a method raises `TypeError`.",
                            "Naming the base explicitly calls the *abstract* body, which is nothing but a docstring and returns `None`; formatting `None` with `:.2f` then raises `TypeError`. Every subclass's work is bypassed.",
                            "There is no module-level function by that name — it is an attribute of the class — so this raises `NameError`.",
                            "The call goes through the object, so it finds whichever implementation that object actually has. That is the template method: one line in the base, and the subclasses supply the number.",
                        ],
                    },
                    {
                        "prompt": "The subclass has its own work to do, and the shared setup still has to happen.",
                        "hole": "?",
                        "opts": [
                            "super()",
                            "Employee",
                            "self",
                            "Employee(self)",
                        ],
                        "a": 0,
                        "why": "`super().__init__(name)` passes the receiver along implicitly and lets the MRO decide what runs next, so the shared setup happens exactly once however the hierarchy is extended later.",
                        "whys": [
                            "`super().__init__(name)` passes the receiver along implicitly and lets the MRO decide what runs next, so the shared setup happens exactly once however the hierarchy is extended later.",
                            "`Employee.__init__(name)` hands the string in as `self` and then has nothing left for the `name` parameter, so it fails on the spot with a `TypeError` about a missing argument.",
                            "`self.__init__(name)` is `Salaried.__init__` again — the method calling itself with the same argument — and it recurses until the stack runs out.",
                            "That tries to build an instance of the abstract base, which is precisely what `ABC` refuses; it raises `TypeError` before any initialisation happens.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How many names end up in the trace?",
                "minutes": 8,
                "brief": r'''
The diamond: `Both` inherits from `Left` and `Right`, and each of those inherits from
`Base`. Every `__init__` records that it ran and then hands over with `super()`, except
`Base`, which records and stops.

```python
trace = []


class Base:
    def __init__(self):
        trace.append("Base")


class Left(Base):
    def __init__(self):
        trace.append("Left")
        super().__init__()


class Right(Base):
    def __init__(self):
        trace.append("Right")
        super().__init__()


class Both(Left, Right):
    def __init__(self):
        trace.append("Both")
        super().__init__()


Both()
print(len(trace))
```
''',
                "prompt": "How many entries does `trace` hold after `Both()` returns?",
                "note": "A whole number. `Both()` is called once, and `trace` starts empty.",
                "figure": "`Both` inherits from `Left` and then `Right`; both of those inherit from `Base`, so `Base` sits at the end of two arrows. Every `__init__` appends its own class name and then calls `super().__init__()` — except `Base`, which appends and returns.",
                "given": [
                    {"label": "Classes in the diamond", "value": "`Both`, `Left`, `Right`, `Base`"},
                    {"label": "Bases of `Both`", "value": "`Left`, then `Right`"},
                    {"label": "Each `__init__`", "value": "appends exactly once"},
                    {"label": "`Base.__init__`", "value": "appends, and calls no `super()`"},
                ],
                "aside": "`super()` is not a synonym for *my parent*. It means *whatever follows me in this object's MRO*.",
                "answer": 4,
                "tol": 0,
                "unit": "entries",
                "hint": "Write out `Both.__mro__` first. Every `super().__init__()` hands over to the next name on that one list, not to a parent on the diagram.",
                "wrong": "Five is the answer the diagram suggests, because `Base` sits at the end of two arrows. Follow the MRO instead: it is a single ordered list, and every class appears on it once.",
                "why": r"""
Four — `Both`, `Left`, `Right`, `Base`. The MRO of `Both` is `Both, Left, Right, Base,
object`, and each `super().__init__()` hands over to the next name on that list rather
than to a parent in the picture. So `Left`'s `super()` goes sideways to `Right`, not up to
`Base`, and `Base` runs once however many arrows point at it.

Cooperative `super()` is what makes that work, and it only works if everyone plays.
Change `Left` to call `Base.__init__(self)` directly and the trace comes out at three
entries with `Right` missing entirely, because `Left` has jumped over its sibling. That
is the bug the MRO exists to prevent, and it stays invisible until the day somebody
inherits from two classes at once.
""",
            },
            "lab": {
                "title": "An abstract Shape hierarchy",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
A geometry kernel that never asks *which* shape it is holding.

## `Shape(ABC)`

- `__init__` sets `self.name` to the **dynamic** class name, so a `Square`
  reports `"Square"` even though the code lives in `Shape`.
- Abstract: `area()` and `perimeter()`. Instantiating `Shape()` directly, or a
  subclass that leaves either one abstract, must raise `TypeError`.
- Concrete `describe()` — a template method written once, in terms of the
  abstract pair:

```text
Rectangle(3, 4).describe()  ->  "Rectangle: area=12.00, perimeter=14.00"
```

- Concrete `__repr__` -> `"<Square area=4.00>"`.

## Subclasses

| class | constructor | area | perimeter |
|---|---|---|---|
| `Circle` | `(radius)` | pi r^2 | 2 pi r |
| `Rectangle` | `(width, height)` | w h | 2(w + h) |
| `Square` | `(side)` | inherits `Rectangle` | inherits |
| `Triangle` | `(a, b, c)` | Heron | a + b + c |

`Square` must subclass `Rectangle` and delegate with `super().__init__(side, side)`.
Heron's formula: with `s = (a + b + c) / 2`, the area is `sqrt(s(s-a)(s-b)(s-c))`.

Every dimension must be strictly positive, else `ValueError`. A triangle whose
sides break the triangle inequality (`a + b <= c` for any ordering, e.g.
`1, 2, 3`) is also a `ValueError`.

## Polymorphic helpers

Write these as free functions that touch nothing but `.area()`:

- `total_area(shapes)` — the sum; `0.0` for an empty list.
- `sorted_by_area(shapes)` — a **new** list, smallest first.
- `largest(shapes)` — the biggest shape, or `None` when the list is empty.
''',
                "files": [{"name": "main.py", "content": r'''
import math
from abc import ABC, abstractmethod


class Shape(ABC):
    """The common interface of every plane figure."""

    def __init__(self):
        # set self.name from the dynamic class
        pass

    @abstractmethod
    def area(self):
        """Enclosed area."""

    @abstractmethod
    def perimeter(self):
        """Length of the boundary."""

    def describe(self):
        """A one-line summary, built from the abstract pair."""
        pass

    def __repr__(self):
        pass


class Circle(Shape):
    def __init__(self, radius):
        pass

    def area(self):
        pass

    def perimeter(self):
        pass


class Rectangle(Shape):
    def __init__(self, width, height):
        pass

    def area(self):
        pass

    def perimeter(self):
        pass


class Square(Rectangle):
    def __init__(self, side):
        pass


class Triangle(Shape):
    def __init__(self, a, b, c):
        pass

    def area(self):
        pass

    def perimeter(self):
        pass


def total_area(shapes):
    """Sum of the areas."""
    pass


def sorted_by_area(shapes):
    """A new list, smallest area first."""
    pass


def largest(shapes):
    """The biggest shape, or None."""
    pass


gallery = [Circle(1), Rectangle(3, 4), Square(2), Triangle(3, 4, 5)]
for shape in sorted_by_area(gallery):
    print(shape.describe())
print("total area:", total_area(gallery))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
from abc import ABC, abstractmethod


class Shape(ABC):
    """The common interface of every plane figure."""

    def __init__(self):
        self.name = type(self).__name__

    @abstractmethod
    def area(self):
        """Enclosed area."""

    @abstractmethod
    def perimeter(self):
        """Length of the boundary."""

    def describe(self):
        """A one-line summary, built from the abstract pair."""
        return f"{self.name}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"

    def __repr__(self):
        return f"<{self.name} area={self.area():.2f}>"


class Circle(Shape):
    """A disc of the given radius."""

    def __init__(self, radius):
        if radius <= 0:
            raise ValueError("radius must be positive")
        super().__init__()
        self.radius = float(radius)

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    """An axis-aligned rectangle."""

    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        super().__init__()
        self.width = float(width)
        self.height = float(height)

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Square(Rectangle):
    """A rectangle whose sides are equal."""

    def __init__(self, side):
        super().__init__(side, side)
        self.side = float(side)


class Triangle(Shape):
    """A triangle given by its three side lengths."""

    def __init__(self, a, b, c):
        if a <= 0 or b <= 0 or c <= 0:
            raise ValueError("every side must be positive")
        sides = sorted([float(a), float(b), float(c)])
        if sides[0] + sides[1] <= sides[2]:
            raise ValueError("sides violate the triangle inequality")
        super().__init__()
        self.a, self.b, self.c = float(a), float(b), float(c)

    def area(self):
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self):
        return self.a + self.b + self.c


def total_area(shapes):
    """Sum of the areas."""
    return sum(shape.area() for shape in shapes)


def sorted_by_area(shapes):
    """A new list, smallest area first."""
    return sorted(shapes, key=lambda shape: shape.area())


def largest(shapes):
    """The biggest shape, or None."""
    if not shapes:
        return None
    return max(shapes, key=lambda shape: shape.area())


gallery = [Circle(1), Rectangle(3, 4), Square(2), Triangle(3, 4, 5)]
for shape in sorted_by_area(gallery):
    print(shape.describe())
print("total area:", total_area(gallery))
'''}],
                "hints": [
                    "`self.name = type(self).__name__` inside `Shape.__init__` — `self.__class__` is the *actual* class, so subclasses need no code of their own.",
                    "Validate before you call `super().__init__()`, so a rejected shape never half-exists. `Square.__init__` should just be `super().__init__(side, side)` plus storing `self.side`.",
                    "Sort the three sides and test only `shortest + middle <= longest`; that single comparison covers all three orderings of the triangle inequality.",
                    "`total_area` is `sum(s.area() for s in shapes)` — it must not mention `Circle`, `Rectangle` or `isinstance` anywhere. That is the point of polymorphism.",
                ],
                "tests": [
                    {"name": "Shape is abstract and cannot be instantiated", "code": r'''
try:
    Shape()
    assert False, "Shape() should raise TypeError — it has abstract methods"
except TypeError:
    pass


class _Blob(Shape):
    def area(self):
        return 1.0


try:
    _Blob()
    assert False, "_Blob leaves perimeter() abstract, so _Blob() should raise TypeError"
except TypeError:
    pass
'''},
                    {"name": "Circle measurements", "code": r'''
import math as _math
_c = Circle(1)
assert abs(_c.area() - _math.pi) < 1e-12, f"Circle(1).area() gave {_c.area()!r}, expected pi"
assert abs(_c.perimeter() - 2 * _math.pi) < 1e-12, f"Circle(1).perimeter() gave {_c.perimeter()!r}"
_c2 = Circle(2.5)
assert abs(_c2.area() - _math.pi * 6.25) < 1e-12, f"Circle(2.5).area() gave {_c2.area()!r}"
'''},
                    {"name": "Rectangle, Square and the is-a relationship", "code": r'''
_r = Rectangle(3, 4)
assert _r.area() == 12.0, f"Rectangle(3,4).area() gave {_r.area()!r}, expected 12.0"
assert _r.perimeter() == 14.0, f"Rectangle(3,4).perimeter() gave {_r.perimeter()!r}, expected 14.0"
_s = Square(5)
assert isinstance(_s, Rectangle) and isinstance(_s, Shape), "Square must subclass Rectangle"
assert _s.area() == 25.0, f"Square(5).area() gave {_s.area()!r}, expected 25.0"
assert _s.perimeter() == 20.0, f"Square(5).perimeter() gave {_s.perimeter()!r}, expected 20.0"
assert _s.name == "Square", f"Square(5).name is {_s.name!r}, expected 'Square' — use type(self).__name__"
'''},
                    {"name": "Triangle uses Heron and checks the inequality", "code": r'''
_t = Triangle(3, 4, 5)
assert abs(_t.area() - 6.0) < 1e-12, f"Triangle(3,4,5).area() gave {_t.area()!r}, expected 6.0"
assert abs(_t.perimeter() - 12.0) < 1e-12, f"perimeter gave {_t.perimeter()!r}, expected 12.0"
_eq = Triangle(2, 2, 2)
assert abs(_eq.area() - 3 ** 0.5) < 1e-12, f"Triangle(2,2,2).area() gave {_eq.area()!r}, expected sqrt(3)"
for _bad in [(1, 2, 3), (1, 2, 10), (10, 1, 2)]:
    try:
        Triangle(*_bad)
        assert False, f"Triangle{_bad!r} breaks the triangle inequality and should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Dimensions must be positive", "code": r'''
for _make in [lambda: Circle(0), lambda: Circle(-1), lambda: Rectangle(0, 4),
              lambda: Rectangle(3, -4), lambda: Square(0), lambda: Triangle(0, 4, 5)]:
    try:
        _make()
        assert False, "A non-positive dimension should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "describe and repr are inherited templates", "code": r'''
_got = Rectangle(3, 4).describe()
assert _got == "Rectangle: area=12.00, perimeter=14.00", f"describe() gave {_got!r}"
_got = Triangle(3, 4, 5).describe()
assert _got == "Triangle: area=6.00, perimeter=12.00", f"describe() gave {_got!r}"
_got = Circle(1).describe()
assert _got == "Circle: area=3.14, perimeter=6.28", f"describe() gave {_got!r}"
_got = repr(Square(2))
assert _got == "<Square area=4.00>", f"repr(Square(2)) gave {_got!r}, expected '<Square area=4.00>'"
'''},
                    {"name": "Helpers dispatch polymorphically", "code": r'''
import math as _math
_shapes = [Circle(1), Rectangle(3, 4), Square(2)]
_want = _math.pi + 12.0 + 4.0
assert abs(total_area(_shapes) - _want) < 1e-12, f"total_area gave {total_area(_shapes)!r}, expected {_want}"
_order = [s.name for s in sorted_by_area(_shapes)]
assert _order == ["Circle", "Square", "Rectangle"], f"sorted_by_area gave {_order!r}"
assert [s.name for s in _shapes] == ["Circle", "Rectangle", "Square"], \
    "sorted_by_area must return a new list, not reorder the caller's"
assert largest(_shapes).name == "Rectangle", f"largest gave {largest(_shapes)!r}"
'''},
                    {"name": "Empty collections are handled", "code": r'''
assert total_area([]) == 0, f"total_area([]) gave {total_area([])!r}, expected 0"
assert sorted_by_area([]) == [], f"sorted_by_area([]) gave {sorted_by_area([])!r}"
assert largest([]) is None, f"largest([]) gave {largest([])!r}, expected None"
_one = [Square(3)]
assert largest(_one) is _one[0], "largest of a single-element list is that element"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Encapsulation, properties and class state",
            "summary": "Invariants that hold on every write, and the difference between the class and its instances.",
            "concepts": [
                "An invariant is a fact that must be true of every valid instance, always",
                "`@property` turns an attribute read into a method call — no caller changes",
                "A setter validates *every* write, including the one inside `__init__`",
                "A property with no setter is read-only: assignment raises `AttributeError`",
                "Attribute lookup: instance `__dict__` first, then the class, then its bases",
                "Assigning to `self.attr` always creates an instance attribute that shadows the class one",
                "`@classmethod` receives the class (alternative constructors); `@staticmethod` receives nothing",
            ],
            "quiz": {
                "title": "Invariants, properties and where state lives",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The getter for `owner` is written `return self.owner`. What happens on the first read?",
                        "opts": [
                            "It returns the stored value — a property knows to skip itself",
                            "`RecursionError`: the getter reads the property, which calls the getter",
                            "`AttributeError`, because `owner` is not in the instance dictionary",
                            "It returns the class attribute of the same name",
                        ],
                        "a": 1,
                        "why": r"""
There is only one attribute called `owner` and it *is* the property, so reading it from
inside its own getter starts again at the top. The standard shape is a property named
`owner` in front of storage named `_owner`, and that leading underscore is doing real
work: it is what makes the two names different, not merely a note to the reader. The same
trap catches the setter, where `self.owner = value` inside `@owner.setter` recurses just
as happily.
""",
                    },
                    {
                        "q": "`balance` is a `@property` with a getter and no setter. What does `account.balance = 500` do?",
                        "opts": [
                            "Creates an instance attribute that shadows the property from then on",
                            "Calls the getter and throws the result away",
                            "Raises `AttributeError`",
                            "Raises `TypeError`",
                        ],
                        "a": 2,
                        "why": r"""
A property is a *data* descriptor, and data descriptors found on the class win over the
instance dictionary on writes as well as reads. So the assignment reaches the property,
finds no setter, and raises — read-only for free, with no code of your own. It is also why
a property cannot be shadowed the way a plain class attribute can: `self.balance = 0`
inside `__init__` hits exactly the same wall, which is why the real number has to live
under `_balance`.
""",
                    },
                    {
                        "q": "`__init__` says `self.count += 1` instead of `Account.count += 1`. After three accounts, what is `Account.count`?",
                        "opts": [
                            "`0` — the class attribute never moved",
                            "`3`",
                            "`1`",
                            "`AttributeError` on the first account",
                        ],
                        "a": 0,
                        "why": r"""
`self.count += 1` is a read followed by a write, and the two do not go to the same place.
The read finds nothing on the instance and falls through to the class, getting `0`; the
write always lands on the instance. So each account ends up with a private `count` of `1`
shadowing the class attribute, and the shared tally sits at `0` forever. Nothing raises,
nothing looks wrong from inside the object, and a test that only ever checks
`account.count` passes.
""",
                    },
                    {
                        "q": "What does `@classmethod` give a method that `@staticmethod` does not?",
                        "opts": [
                            "Access to the instance's private attributes",
                            "The class it was called through, so an alternative constructor builds the right subclass",
                            "The right to be called without an instance",
                            "Automatic validation of its arguments",
                        ],
                        "a": 1,
                        "why": r"""
`cls` is not pinned to the class where the method was written: called as
`Savings.from_row(...)`, `cls` is `Savings`, so `return cls(...)` builds a `Savings` with
no extra code and no `if`. A `@staticmethod` receives nothing at all — it is a plain
function kept in the class's namespace because that is where it belongs, which is exactly
what `is_valid_amount` is. Both can be called without an instance, so that is not the
distinction.
""",
                    },
                    {
                        "q": "A class body says `history = []`, and `__init__` never mentions it. Two instances each call `self.history.append(...)`. What does the second one see?",
                        "opts": [
                            "Only its own entry",
                            "Nothing — appending to a class attribute is refused",
                            "Its own entry, plus a copy of the other made at construction",
                            "Both entries: there is one list, and it lives on the class",
                        ],
                        "a": 3,
                        "why": r"""
The list is built once, when the class body runs. `self.history` finds no instance
attribute and falls through to the class, and `append` mutates that one object in place —
no assignment happens anywhere, so nothing is ever shadowed and every instance goes on
sharing. Per-instance state has to be *created* per instance, which is the whole job of
`self.history = []` in `__init__`. Immutable defaults get away with it — `interest_rate =
0.02` on the class is fine — precisely because `+=` on a number is an assignment, and an
assignment writes to the instance.
""",
                    },
                    {
                        "q": "For a plain attribute — no property involved — where does `account.interest_rate` look, and in what order?",
                        "opts": [
                            "The class, then the instance",
                            "The instance only; a class attribute needs `Account.interest_rate`",
                            "The instance dictionary, then the class, then its bases along the MRO",
                            "The bases, then the class, then the instance",
                        ],
                        "a": 2,
                        "why": r"""
Instance first, then the class, then each base in MRO order, and `AttributeError` if
nobody has it. That single rule explains both the useful behaviour — a shared default any
one instance may override for itself — and the trap in `self.count += 1`, since only the
*read* half ever consults the class. The exception worth carrying with it: a data
descriptor such as a property is found on the class and takes priority over the instance
dictionary, which is what makes a read-only property genuinely read-only.
""",
                    },
                ],
            },
            "blanks": {
                "title": "A property that cannot be talked out of it",
                "minutes": 9,
                "caption": "thermostat.py — validation, a class-level tally, and an alternative constructor",
                "lang": "python",
                "brief": r'''
A setpoint with a safe range, and one rule: there is no way to get an unsafe value into
the object. Not through `__init__`, not through an assignment later, not through the
alternative constructor. Every hole is a place where that guarantee is either kept or
quietly given away.

Nothing runs here — you are choosing symbols, not writing code.
''',
                "listing": '''class Thermostat:
    """A setpoint that can never leave the safe range, whoever writes to it."""

    unit = "C"
    made = 0

    def __init__(self, room, setpoint=20.0):
        self.room = room
        self.setpoint = setpoint          # goes through the setter below
        self.log = []
        ___ += 1

    @property
    def setpoint(self):
        return self.___

    @setpoint.___
    def setpoint(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("setpoint must be a number")
        if not 5 <= value <= 30:
            raise ValueError("setpoint must lie between 5 and 30")
        self._setpoint = float(value)

    @property
    def fahrenheit(self):
        return self._setpoint * 9 / 5 + 32

    @___
    def from_fahrenheit(cls, room, degrees_f):
        """Build one from a setpoint quoted in Fahrenheit."""
        return cls(room, (degrees_f - 32) * 5 / 9)
''',
                "blanks": [
                    {
                        "prompt": "One tally, shared by every thermostat ever made.",
                        "hole": "?",
                        "opts": [
                            "cls.made",
                            "self.made",
                            "made",
                            "Thermostat.made",
                        ],
                        "a": 3,
                        "why": "Naming the class is what makes the write land on the class. It is the only place a shared counter can live if every instance is to see the same number.",
                        "whys": [
                            "`cls` exists only inside a `@classmethod`. In an ordinary method the name is simply undefined, and this raises `NameError`.",
                            "This reads the class value, adds one, and stores the result on the instance — so every thermostat privately believes exactly one has been made, and `Thermostat.made` stays at zero forever.",
                            "Names from the class body are not in scope inside its methods. The bare name is treated as a local, and reading it before it is assigned raises `UnboundLocalError`.",
                            "Naming the class is what makes the write land on the class. It is the only place a shared counter can live if every instance is to see the same number.",
                        ],
                    },
                    {
                        "prompt": "The property is the public name. The value has to live somewhere else.",
                        "hole": "?",
                        "opts": [
                            "setpoint",
                            "_setpoint",
                            "__setpoint",
                        ],
                        "a": 1,
                        "why": "One leading underscore is the convention for *this is the storage, do not touch it from outside*, and it is the one attribute the getter and the setter share. The property and its storage must be two different names, or there is nothing to store.",
                        "whys": [
                            "That is the getter reading the property it is the getter for: it calls itself until the stack runs out.",
                            "One leading underscore is the convention for *this is the storage, do not touch it from outside*, and it is the one attribute the getter and the setter share. The property and its storage must be two different names, or there is nothing to store.",
                            "Nothing ever writes that name — the setter stores `_setpoint` — and two leading underscores also mangle it to `_Thermostat__setpoint`, so the read fails with an `AttributeError` naming an attribute nobody typed.",
                        ],
                    },
                    {
                        "prompt": "The validation is written once. What connects it to the plain assignment `t.setpoint = 25`?",
                        "hole": "?",
                        "opts": [
                            "deleter",
                            "getter",
                            "setter",
                            "property",
                        ],
                        "a": 2,
                        "why": "`@property` produced an object holding the read path; `.setter` returns a *new* property carrying that same getter plus this function as the write path. Rebinding the name `setpoint` to the result is why the decorated function has to keep the name it already has.",
                        "whys": [
                            "`.deleter` supplies the `del t.setpoint` path. Assignment would still be refused, so construction fails at the first write, and the validation never runs.",
                            "`.getter` replaces the read path with this two-argument function and leaves the property with no way to be written at all, so `self.setpoint = setpoint` in `__init__` raises `AttributeError` on the first thermostat.",
                            "`@property` produced an object holding the read path; `.setter` returns a *new* property carrying that same getter plus this function as the write path. Rebinding the name `setpoint` to the result is why the decorated function has to keep the name it already has.",
                            "A property object has `getter`, `setter` and `deleter` and nothing named `property`, so asking for one raises `AttributeError` while the class body is still executing.",
                        ],
                    },
                    {
                        "prompt": "An alternative constructor: same object, different starting units.",
                        "hole": "?",
                        "opts": [
                            "classmethod",
                            "staticmethod",
                            "property",
                            "abstractmethod",
                        ],
                        "a": 0,
                        "why": "The method needs the class in order to build one, and it needs the class it was *called through*, so a subclass calling `from_fahrenheit` gets a subclass back. That is what makes this an alternative constructor rather than a factory wired to one type — and note it returns through `__init__`, so the setter validates the converted value like any other.",
                        "whys": [
                            "The method needs the class in order to build one, and it needs the class it was *called through*, so a subclass calling `from_fahrenheit` gets a subclass back. That is what makes this an alternative constructor rather than a factory wired to one type — and note it returns through `__init__`, so the setter validates the converted value like any other.",
                            "`@staticmethod` passes nothing automatically, so `cls` would receive the room name and the call arrives one argument short: a `TypeError` about `degrees_f`.",
                            "A property is evaluated on attribute access, with no arguments at all. `Thermostat.from_fahrenheit` would hand back the property object itself, which is not callable.",
                            "`@abstractmethod` only marks a method as one a subclass must supply, and outside an `ABC` nothing even reads the mark. It leaves an ordinary method here, with the instance arriving where `cls` was expected.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "Where does the rate come from?",
                "minutes": 8,
                "brief": r'''
`award_bonus` reads `self.bonus_rate`. Between the two accounts being opened and the
bonus being awarded, that name is written twice — once on an instance and once on the
class.

```python
class Loyalty:
    """A points balance that earns a bonus at the house rate."""

    bonus_rate = 0.02

    def __init__(self, owner, points):
        self.owner = owner
        self._points = float(points)

    @property
    def points(self):
        return self._points

    def award_bonus(self):
        """Credit the bonus and return the points added."""
        bonus = self._points * self.bonus_rate
        self._points += bonus
        return bonus


ada = Loyalty("Ada", 200)
bo = Loyalty("Bo", 200)

ada.bonus_rate = 0.05        # written on the instance
Loyalty.bonus_rate = 0.10    # written on the class

ada.award_bonus()
bo.award_bonus()
print(ada.points + bo.points)
```
''',
                "prompt": "What does the last line print?",
                "note": "Two decimal places is more than enough.",
                "figure": "Both accounts open with 200 points, and the class default is 0.02. Then `0.05` is written on `ada` herself, `0.10` is written on the class, and each account awards its bonus exactly once.",
                "given": [
                    {"label": "Opening points", "value": "200 each"},
                    {"label": "Class default", "value": "`bonus_rate = 0.02`"},
                    {"label": "Written on `ada`", "value": "`ada.bonus_rate = 0.05`"},
                    {"label": "Written on `Loyalty`", "value": "`Loyalty.bonus_rate = 0.10`"},
                ],
                "aside": "`award_bonus` reads `self.bonus_rate`, and that lookup starts at the instance every single time.",
                "answer": 430,
                "tol": 0.01,
                "unit": "points",
                "hint": "Take the two accounts separately. For each one, ask where the lookup of `self.bonus_rate` stops.",
                "wrong": "The order of the two writes is a red herring. `Loyalty.bonus_rate = 0.10` never reaches into `ada`'s own dictionary, and it would not have mattered if it had come first.",
                "why": r"""
430.0. `ada.bonus_rate = 0.05` created an attribute on `ada` herself, and `self.bonus_rate`
finds it before ever consulting the class, so she earns 10 and finishes on 210. `bo` has
nothing of his own, so his lookup falls through to the class, finds the 0.10 written there,
and he earns 20 to finish on 220.

The instance attribute is not a stale copy of the class one. It is a different attribute
in a different dictionary, and while it exists the class value is invisible to that
object: `del ada.bonus_rate` removes the shadow and 0.10 becomes visible again, which is
the proof that nothing was ever overwritten. Had `award_bonus` read `Loyalty.bonus_rate`
instead of `self.bonus_rate`, both accounts would have earned 20 and the per-instance
override would be dead code.
""",
            },
            "lab": {
                "title": "A bank account that defends itself",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
`Account` keeps a balance that can never be corrupted from outside.

## Class attributes

```text
Account.interest_rate = 0.02     shared default for every account
Account.count         = 0        how many accounts have been created
```

`__init__` increments the counter **on the class** (`Account.count += 1`), not
on `self` — `self.count += 1` would silently create an instance attribute and
the shared tally would never move.

## Instance state

`Account(owner, balance=0.0)` stores the owner through its property setter,
rejects a negative opening balance with `ValueError`, and gives every account
its **own** empty `history` list.

## Properties

- `owner` — readable and writable, but a non-string or a blank string raises
  `ValueError`. The value is stored stripped.
- `balance` — read-only. `account.balance = 1_000_000` must raise
  `AttributeError`. The real number lives in `_balance`.

## Behaviour

- `deposit(amount)` — positive only, else `ValueError`. Appends
  `("deposit", amount)` to `history` and returns the new balance.
- `withdraw(amount)` — positive only, and never more than the balance
  (`ValueError("insufficient funds")`). Appends `("withdraw", amount)`.
- `apply_interest()` — adds `self.interest_rate` of the balance, appends
  `("interest", amount)` and **returns the interest added**. Read the rate off
  `self`, so an instance override is honoured.
- `set_interest_rate(rate)` — a `@classmethod` writing `cls.interest_rate`;
  a negative rate is a `ValueError`.
- `is_valid_amount(amount)` — a `@staticmethod` returning `True` only for a
  positive `int`/`float` (and `False` for `bool`, `None` and strings).
- `__repr__` -> `"Account('Ada', 100.00)"`.

A rejected operation must leave the balance and the history untouched.
''',
                "files": [{"name": "main.py", "content": r'''
class Account:
    """A bank account whose balance is only reachable through its own methods."""

    interest_rate = 0.02
    count = 0

    def __init__(self, owner, balance=0.0):
        # assign the owner through the property, validate the opening balance,
        # give this account its own history list, and bump the class counter
        pass

    @property
    def owner(self):
        pass

    @owner.setter
    def owner(self, value):
        pass

    @property
    def balance(self):
        pass

    def deposit(self, amount):
        """Add money. Returns the new balance."""
        pass

    def withdraw(self, amount):
        """Take money out, never past zero. Returns the new balance."""
        pass

    def apply_interest(self):
        """Credit interest at self.interest_rate. Returns the interest added."""
        pass

    @classmethod
    def set_interest_rate(cls, rate):
        """Change the rate for every account that has not overridden it."""
        pass

    @staticmethod
    def is_valid_amount(amount):
        """True for a positive int or float."""
        pass

    def __repr__(self):
        pass


ada = Account("Ada", 100)
ada.deposit(50)
ada.withdraw(20)
print(ada, ada.balance, ada.history)
print("interest:", ada.apply_interest())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class Account:
    """A bank account whose balance is only reachable through its own methods."""

    interest_rate = 0.02
    count = 0

    def __init__(self, owner, balance=0.0):
        self.owner = owner
        if balance < 0:
            raise ValueError("opening balance cannot be negative")
        self._balance = float(balance)
        self.history = []
        Account.count += 1

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("owner must be a non-empty string")
        self._owner = value.strip()

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        """Add money. Returns the new balance."""
        if not self.is_valid_amount(amount):
            raise ValueError("deposit must be a positive number")
        self._balance += float(amount)
        self.history.append(("deposit", float(amount)))
        return self._balance

    def withdraw(self, amount):
        """Take money out, never past zero. Returns the new balance."""
        if not self.is_valid_amount(amount):
            raise ValueError("withdrawal must be a positive number")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= float(amount)
        self.history.append(("withdraw", float(amount)))
        return self._balance

    def apply_interest(self):
        """Credit interest at self.interest_rate. Returns the interest added."""
        interest = self._balance * self.interest_rate
        self._balance += interest
        self.history.append(("interest", interest))
        return interest

    @classmethod
    def set_interest_rate(cls, rate):
        """Change the rate for every account that has not overridden it."""
        if rate < 0:
            raise ValueError("rate cannot be negative")
        cls.interest_rate = rate

    @staticmethod
    def is_valid_amount(amount):
        """True for a positive int or float."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            return False
        return amount > 0

    def __repr__(self):
        return f"Account({self._owner!r}, {self._balance:.2f})"


ada = Account("Ada", 100)
ada.deposit(50)
ada.withdraw(20)
print(ada, ada.balance, ada.history)
print("interest:", ada.apply_interest())
'''}],
                "hints": [
                    "Name the storage `_owner` and `_balance`. A property called `owner` that reads `self.owner` recurses until the stack blows.",
                    "`self.owner = owner` in `__init__` goes through the setter, so validation happens exactly once, in one place.",
                    "For read-only `balance`, write the getter and simply do not write a setter — Python raises `AttributeError` on assignment for you.",
                    "`Account.count += 1` names the class explicitly. `self.count += 1` reads the class value, adds one, and stores the result as a *new instance attribute* — the class tally never moves.",
                ],
                "tests": [
                    {"name": "Construction and the owner property", "code": r'''
_a = Account("  Ada  ", 100)
assert _a.owner == "Ada", f"owner is {_a.owner!r}, expected 'Ada' (stripped)"
assert _a.balance == 100.0, f"balance is {_a.balance!r}, expected 100.0"
assert Account("Bo").balance == 0.0, "balance defaults to 0.0"
_a.owner = " Grace "
assert _a.owner == "Grace", f"after reassignment owner is {_a.owner!r}"
assert repr(_a) == "Account('Grace', 100.00)", f"repr gave {repr(_a)!r}"
'''},
                    {"name": "The owner setter rejects rubbish", "code": r'''
_a = Account("Ada", 10)
for _bad in ["", "   ", None, 42, ["Ada"]]:
    try:
        _a.owner = _bad
        assert False, f"owner = {_bad!r} should raise ValueError"
    except ValueError:
        pass
assert _a.owner == "Ada", f"a rejected write changed the owner to {_a.owner!r}"
try:
    Account("", 10)
    assert False, "Account('', 10) should raise ValueError — __init__ goes through the setter"
except ValueError:
    pass
try:
    Account("Ada", -1)
    assert False, "A negative opening balance should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "balance is read-only", "code": r'''
_a = Account("Ada", 100)
try:
    _a.balance = 1000000
    assert False, "Assigning to balance should raise AttributeError — give it no setter"
except AttributeError:
    pass
assert _a.balance == 100.0, f"balance is now {_a.balance!r}, expected 100.0"
'''},
                    {"name": "deposit and withdraw keep the invariant", "code": r'''
_a = Account("Ada", 100)
_got = _a.deposit(50)
assert _got == 150.0, f"deposit(50) returned {_got!r}, expected the new balance 150.0"
assert _a.withdraw(20) == 130.0, f"balance after withdraw(20) is {_a.balance!r}, expected 130.0"
for _bad in [0, -5, "10", None, True]:
    try:
        _a.deposit(_bad)
        assert False, f"deposit({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    _a.withdraw(1000)
    assert False, "Overdrawing should raise ValueError"
except ValueError:
    pass
assert _a.balance == 130.0, f"a refused operation changed the balance to {_a.balance!r}"
assert _a.history == [("deposit", 50.0), ("withdraw", 20.0)], f"history is {_a.history!r}"
'''},
                    {"name": "Each account owns its history", "code": r'''
_a = Account("Ada", 100)
_b = Account("Bo", 100)
_a.deposit(10)
assert _b.history == [], f"Bo's history is {_b.history!r} — history must be created per instance"
assert len(_a.history) == 1, f"Ada's history is {_a.history!r}"
'''},
                    {"name": "is_valid_amount is a static predicate", "code": r'''
assert Account.is_valid_amount(5) is True, "5 is a valid amount"
assert Account.is_valid_amount(0.01) is True, "0.01 is a valid amount"
for _bad in [0, -1, True, False, None, "5", [1]]:
    assert Account.is_valid_amount(_bad) is False, f"is_valid_amount({_bad!r}) should be False"
'''},
                    {"name": "Class attribute lookup, shadowing and the classmethod", "code": r'''
_prev = Account.count
_a = Account("Ada", 100)
_b = Account("Bo", 100)
assert Account.count == _prev + 2, f"Account.count moved to {Account.count}, expected {_prev + 2}"
assert "count" not in _a.__dict__, "count must live on the class — use Account.count += 1"
assert _a.interest_rate == 0.02 and Account.interest_rate == 0.02, "the shared default is 0.02"
_a.interest_rate = 0.10
assert _b.interest_rate == 0.02, "an instance attribute must shadow only that instance"
assert abs(_a.apply_interest() - 10.0) < 1e-9, f"Ada's interest was {_a.history[-1]!r}, expected 10.0"
assert abs(_b.apply_interest() - 2.0) < 1e-9, f"Bo's interest was {_b.history[-1]!r}, expected 2.0"
Account.set_interest_rate(0.05)
assert Account.interest_rate == 0.05 and _b.interest_rate == 0.05, "the classmethod writes cls.interest_rate"
assert _a.interest_rate == 0.10, "Ada's own override still shadows the class value"
try:
    Account.set_interest_rate(-0.01)
    assert False, "A negative rate should raise ValueError"
except ValueError:
    pass
Account.set_interest_rate(0.02)
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Composition and Python's container protocols",
            "summary": "Building objects out of other objects, and making yours behave like a list.",
            "concepts": [
                "Composition (has-a) is the default; inheritance is the special case",
                "Delegation: a container forwards work to the objects it holds",
                "`__len__` powers `len()` and the truthiness of your object",
                "`__iter__` must return an *iterator*; `iter(self._items)` is usually enough",
                "`__getitem__` should accept both an index and a `slice`",
                "`__contains__` makes `in` explicit — without it Python falls back to iteration",
                "Returning a new container from a slice or `__add__` keeps the type closed",
            ],
            "quiz": {
                "title": "Containers that behave like containers",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A `Playlist` defines `__len__` and no `__bool__`. What is `bool(empty_playlist)`?",
                        "opts": [
                            "`True` — an object is truthy unless it says otherwise",
                            "`False` — with no `__bool__`, truth falls back to `len(obj) != 0`",
                            "`TypeError`",
                            "`None`",
                        ],
                        "a": 1,
                        "why": r"""
Python asks `__bool__` first, then `__len__`, and only then assumes true. So an empty
container becomes falsy the moment you write `__len__`, and `if playlist:` means what a
reader expects it to mean. The corner worth knowing about: a class for which zero length
is a perfectly ordinary state becomes falsy at zero whether you wanted that or not, and
that is the moment to write `__bool__` explicitly.
""",
                    },
                    {
                        "q": "`__iter__` is written `return self._tracks`, handing back the underlying list. What happens at `for t in playlist:`?",
                        "opts": [
                            "Nothing — a list is perfectly iterable",
                            "The loop runs once and stops",
                            "`TypeError: iter() returned non-iterator of type 'list'`",
                            "The list is consumed, so a second loop over the same playlist sees nothing",
                        ],
                        "a": 2,
                        "why": r"""
Iterable and iterator are two different jobs. A list is iterable — it has `__iter__` — but
it is not an iterator, because it has no `__next__`, and `iter()` insists on being handed
something that has one. `return iter(self._tracks)` produces a fresh `list_iterator` on
every call, which is also why two nested loops over the same playlist do not tread on each
other: each `for` asks for its own.
""",
                    },
                    {
                        "q": "`playlist[0:2]`. What does `__getitem__` actually receive?",
                        "opts": [
                            "One argument: `slice(0, 2, None)`",
                            "Two arguments, `0` and `2`",
                            "The tuple `(0, 2)`",
                            "A `range` object",
                        ],
                        "a": 0,
                        "why": r"""
Subscription always passes exactly one object, so the colon syntax is packaged into a
`slice` carrying `start`, `stop` and `step` — `step` being `None` when it is not written.
That is why the method has to branch on `isinstance(key, slice)`, and why passing the key
straight through to the underlying list works for both cases: a list already knows what to
do with either. It also means `playlist[0:2]` and `playlist[slice(0, 2)]` are the same
call.
""",
                    },
                    {
                        "q": "A class defines `__iter__` and no `__contains__`. What does `x in obj` do?",
                        "opts": [
                            "Raises `TypeError`",
                            "Returns `False` always",
                            "Compares identity only, as if with `is`",
                            "Iterates, comparing each item with `==`, until it matches or runs out",
                        ],
                        "a": 3,
                        "why": r"""
Membership falls back to iteration, so `in` works the moment an object is iterable. What
you give up is speed and control: the scan is linear, and it compares with `==`, which
decides for you what counts as a match. Writing `__contains__` is how a playlist comes to
accept a title string as well as a `Track` — the fallback would compare a string against a
`Track`, find nothing, and never complain.
""",
                    },
                    {
                        "q": "Why does `Playlist` hold a list rather than subclass one?",
                        "opts": [
                            "Because `list` cannot be subclassed in Python",
                            "Because inheriting hands out every list method — `pop`, `sort`, `extend`, slice assignment — and not one of them will respect the rules `add` enforces",
                            "Because a subclass of `list` cannot define `__len__`",
                            "Because it would make the playlist mutable",
                        ],
                        "a": 1,
                        "why": r"""
Subclassing is a promise that your object can be used anywhere a list can, which means
accepting `p.extend([1, 2, 3])` — three integers now living in a playlist, having never
passed the `isinstance(track, Track)` check in `add`. Composition keeps the surface
exactly as wide as you meant it: the methods you wrote, and nothing else. The related fact
worth carrying: the built-in's own methods do not call your overrides, so even the ones you
try to intercept leak.
""",
                    },
                    {
                        "q": "`playlist[0:2]` returns a new `Playlist` rather than a plain list. What does that buy?",
                        "opts": [
                            "It stops the original being mutated by the slice",
                            "It is required — `__getitem__` must return the same type it was called on",
                            "The result supports everything the original did, so slices chain and can be handed to the same code",
                            "It makes the slice cheaper, because no tracks are copied",
                        ],
                        "a": 2,
                        "why": r"""
Keeping the type closed under its own operations is what lets `jazz[0:2].by_artist('Miles
Davis')` read naturally, and what lets a function that takes a playlist be handed a slice
of one. Returning a bare list would work, but then every caller has to remember which
operations quietly demote a playlist into something less capable. Note the two things that
happen either way: slicing never mutates the original, because a new container is built,
and no `Track` is copied, because both playlists hold references to the very same objects.
""",
                    },
                ],
            },
            "blanks": {
                "title": "A container, hole by hole",
                "minutes": 9,
                "caption": "deck.py — five protocol methods, and the ways each one goes wrong",
                "lang": "python",
                "brief": r'''
A `Deck` *has* a list of cards; it is not one. Everything below is delegation — five
methods that forward work to the list inside, and in doing so make the deck behave like
something Python already understands.

Nothing runs here — you are choosing symbols, not writing code.
''',
                "listing": '''class Deck:
    """An ordered hand of cards. It *has* a list; it is not one."""

    def __init__(self, name, cards=None):
        self.name = name
        self._cards = list(cards) if cards else []

    def __len__(self):
        return ___

    def __iter__(self):
        return ___(self._cards)

    def __getitem__(self, key):
        if isinstance(key, ___):
            return Deck(self.name, self._cards[key])
        return self._cards[key]

    def __contains__(self, item):
        if isinstance(item, str):
            return any(card.name == item for card in self._cards)
        return ___

    def __add__(self, other):
        if not isinstance(other, Deck):
            return NotImplemented
        return ___
''',
                "blanks": [
                    {
                        "prompt": "The deck's length is the length of what it holds.",
                        "hole": "?",
                        "opts": [
                            "self._cards",
                            "len(self._cards)",
                            "len(self)",
                            "self._cards.count()",
                        ],
                        "a": 1,
                        "why": "Pure delegation, and one line of it buys `len(deck)`, `if deck:` and every loop that wants a count. Ask the list; it already knows.",
                        "whys": [
                            "`__len__` must return a non-negative integer. Handing back the list itself raises `TypeError: 'list' object cannot be interpreted as an integer` the first time anybody calls `len`.",
                            "Pure delegation, and one line of it buys `len(deck)`, `if deck:` and every loop that wants a count. Ask the list; it already knows.",
                            "`len(self)` calls `__len__` again — the method asking itself how long it is — and recurses until the stack runs out.",
                            "`list.count` needs the value to count, so with no argument it raises `TypeError`; even with one it would be answering a different question.",
                        ],
                    },
                    {
                        "prompt": "`__iter__` has to hand back an iterator, not merely something iterable.",
                        "hole": "?",
                        "opts": [
                            "next",
                            "list",
                            "iter",
                            "tuple",
                        ],
                        "a": 2,
                        "why": "`iter` turns the list into a genuine iterator — an object with `__next__` — which is what a `for` statement demands of whatever `__iter__` returns. A fresh one is made on every call, so two loops over the same deck stay independent.",
                        "whys": [
                            "`next` expects an iterator and is being handed a list, so it raises `TypeError: 'list' object is not an iterator` — and even if it worked it would produce one card rather than something to iterate over.",
                            "A copy of the list is still a list: iterable, but not an iterator, so the loop fails with `iter() returned non-iterator of type 'list'` before the first card comes out.",
                            "`iter` turns the list into a genuine iterator — an object with `__next__` — which is what a `for` statement demands of whatever `__iter__` returns. A fresh one is made on every call, so two loops over the same deck stay independent.",
                            "A tuple has exactly the problem a list has: it owns an `__iter__` and no `__next__`, so it is iterable and is not an iterator.",
                        ],
                    },
                    {
                        "prompt": "One subscript syntax, two kinds of key.",
                        "hole": "?",
                        "opts": [
                            "range",
                            "list",
                            "int",
                            "slice",
                        ],
                        "a": 3,
                        "why": "The colon syntax arrives as a single `slice` object, so this is the test that tells `deck[1]` from `deck[1:3]`. Passing the key straight to the underlying list then handles both, because a list understands each of them.",
                        "whys": [
                            "A `range` is something you might build *from* a slice, not what arrives at the door — `isinstance(slice(0, 2), range)` is `False`, so the branch never fires.",
                            "`key` is never a list, so this branch never runs: every slice falls through to the line below and quietly returns a plain list. Nothing raises, and the type has stopped being closed without anybody noticing.",
                            "This inverts the test. `deck[0]` would take the wrapping branch and try to build a `Deck` out of a single card, while a slice falls through and comes back as a bare list.",
                            "The colon syntax arrives as a single `slice` object, so this is the test that tells `deck[1]` from `deck[1:3]`. Passing the key straight to the underlying list then handles both, because a list understands each of them.",
                        ],
                    },
                    {
                        "prompt": "A string was handled above. What should `in` mean for an actual card?",
                        "hole": "?",
                        "opts": [
                            "item in self._cards",
                            "item in self",
                            "self._cards.index(item)",
                            "any(card is item for card in self._cards)",
                        ],
                        "a": 0,
                        "why": "Delegating to the list gives `in` its ordinary meaning: a scan comparing with `==`, so any card equal to the one being asked about counts. The string branch above is the extra this deck adds; this line is the part it should not reinvent.",
                        "whys": [
                            "Delegating to the list gives `in` its ordinary meaning: a scan comparing with `==`, so any card equal to the one being asked about counts. The string branch above is the extra this deck adds; this line is the part it should not reinvent.",
                            "This re-enters `__contains__` with the same argument — the method calling itself — and recurses until the stack runs out.",
                            "`list.index` returns a position, and the position of the front card is `0`, which is falsy: the first card in the deck would report as absent. A card that really is missing raises `ValueError` rather than answering `False`.",
                            "Identity, not equality: a card equal to one in the deck but built separately reports `False`. That is precisely the case `__eq__` was written for, and this line declines to use it.",
                        ],
                    },
                    {
                        "prompt": "`a + b` is an expression. It produces a value; it does not rearrange its operands.",
                        "hole": "?",
                        "opts": [
                            "self._cards.extend(other._cards)",
                            "self._cards + other._cards",
                            'Deck(f"{self.name} + {other.name}", list(self) + list(other))',
                            "Deck(self.name, self._cards)",
                        ],
                        "a": 2,
                        "why": "A new deck, built out of both and leaving each of them exactly as it was. Returning a `Deck` rather than something less capable is what keeps the result usable by everything that accepts one.",
                        "whys": [
                            "`extend` mutates the left operand in place and returns `None`, so `a + b` evaluates to `None` and `a` has silently grown. An expression that rewrites its own operands is the one thing `+` must never be.",
                            "This returns a bare list. The addition works and every card is present, but the result has lost its name and every method the deck defines.",
                            "A new deck, built out of both and leaving each of them exactly as it was. Returning a `Deck` rather than something less capable is what keeps the result usable by everything that accepts one.",
                            "The right operand is dropped and the result is a copy of the left one. Nothing raises, but very little hides either: the length is short by however many cards `other` held, so one non-empty operand on the right is enough to catch it, and the name is wrong in every case — the correct result is called `A + B` and this one comes back called `A`, which even two empty decks would expose.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How long does the joined playlist run?",
                "minutes": 8,
                "brief": r'''
Three tracks, a slice and a concatenation. Both `__getitem__` and `__add__` build a new
playlist rather than changing an existing one; here are the three methods that matter.

```python
    def __getitem__(self, key):
        if isinstance(key, slice):
            sliced = Playlist(self.name)
            for track in self._tracks[key]:
                sliced.add(track)
            return sliced
        return self._tracks[key]

    def __add__(self, other):
        joined = Playlist(f"{self.name} + {other.name}")
        for track in list(self) + list(other):
            joined.add(track)
        return joined

    def total_seconds(self):
        return sum(track.seconds for track in self._tracks)
```

And the script:

```python
jazz = Playlist("Jazz")
jazz.add(Track("Blue Train", "John Coltrane", 617))
jazz.add(Track("So What", "Miles Davis", 545))
jazz.add(Track("Take Five", "Dave Brubeck", 324))

half = jazz[0:2]
both = jazz + half

print(both.total_seconds())
```
''',
                "prompt": "What does `both.total_seconds()` return?",
                "note": "A whole number of seconds.",
                "figure": "`jazz` holds Blue Train (617 s), So What (545 s) and Take Five (324 s), in that order. `half` is `jazz[0:2]`, a new playlist built by the slice branch of `__getitem__`, and `both` is `jazz + half`.",
                "given": [
                    {"label": "Blue Train", "value": "617 s"},
                    {"label": "So What", "value": "545 s"},
                    {"label": "Take Five", "value": "324 s"},
                    {"label": "`half`", "value": "`jazz[0:2]`"},
                    {"label": "`both`", "value": "`jazz + half`"},
                ],
                "aside": "Neither the slice nor the concatenation copies a single `Track`. All three playlists point at the same three objects.",
                "answer": 2648,
                "tol": 0,
                "unit": "s",
                "hint": "Total `jazz`, total the slice, then add the two. Nothing is de-duplicated along the way.",
                "wrong": "Two things to check: `0:2` takes indices 0 and 1 and stops before 2, and concatenation keeps duplicates — a track appearing in both operands is counted twice.",
                "why": r"""
2648. `jazz` runs 617 + 545 + 324 = 1486. The slice `jazz[0:2]` is a *new* `Playlist`
holding the first two tracks, 617 + 545 = 1162 — stopping before index 2 is what leaves
Take Five out of it. Concatenation then builds a third playlist out of both, so `both`
holds five entries and totals 1486 + 1162 = 2648, with Blue Train and So What counted
twice because the same objects appear twice in the list.

Note what was *not* copied. `half` and `both` hold references to the very same three
`Track` objects, so three tracks exist in memory throughout, and `jazz` still runs 1486 —
neither operation touched it. Returning new containers is what makes that safe to say.
""",
            },
            "lab": {
                "title": "A Playlist that behaves like a sequence",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Two classes. `Track` is a value; `Playlist` **contains** tracks — it does not
inherit from `list`.

## `Track(title, artist, seconds)`

- `title` and `artist` must be non-empty strings (stored stripped);
  `seconds` must be a positive `int`. Anything else is a `ValueError`.
- `duration` is a **property** formatting the length as `minutes:seconds`
  with the seconds zero-padded to two digits:

```text
Track("Blue Train", "John Coltrane", 617).duration  ->  "10:17"
Track("Short", "Someone", 59).duration              ->  "0:59"
```

- `__eq__` compares title and artist case-insensitively; `__hash__` agrees.
- `__repr__` -> `"Track('Blue Train', 'John Coltrane', 617)"`.

## `Playlist(name)`

Holds tracks in insertion order in a private list.

- `add(track)` — appends and returns the playlist, so calls chain.
- `remove(title)` — drops the first track with that title (case-insensitive);
  `ValueError` when nothing matches.
- `__len__`, and `__iter__` yielding tracks in order.
- `__getitem__` — an `int` gives a `Track` (negative indices included, and an
  out-of-range index raises `IndexError`); a **slice gives a new `Playlist`**
  with the same name.
- `__contains__` — accepts a `Track` *or* a title string (case-insensitive).
  Anything else is simply `False`, never an exception.
- `__add__` — concatenation into a new playlist named `"A + B"`.
- `__repr__` -> `"Playlist('Jazz', 3 tracks)"`.
- `total_seconds()`, and `total_duration()` in the same `m:ss` format.
- `by_artist(artist)` — a new `Playlist` named `artist`, case-insensitive.

Neither class may subclass `list`.
''',
                "files": [{"name": "main.py", "content": r'''
class Track:
    """One recording: what it is, who made it, how long it runs."""

    def __init__(self, title, artist, seconds):
        pass

    @property
    def duration(self):
        """Length as m:ss."""
        pass

    def __eq__(self, other):
        pass

    def __hash__(self):
        pass

    def __repr__(self):
        pass


class Playlist:
    """An ordered collection of tracks. It *has* tracks; it is not a list."""

    def __init__(self, name):
        self.name = name
        self._tracks = []

    def add(self, track):
        """Append a track and return self."""
        pass

    def remove(self, title):
        """Drop the first track with this title, or raise ValueError."""
        pass

    def __len__(self):
        pass

    def __iter__(self):
        pass

    def __getitem__(self, key):
        pass

    def __contains__(self, item):
        pass

    def __add__(self, other):
        pass

    def __repr__(self):
        pass

    def total_seconds(self):
        pass

    def total_duration(self):
        """The whole playlist as m:ss."""
        pass

    def by_artist(self, artist):
        """A new Playlist of this artist's tracks."""
        pass


jazz = Playlist("Jazz")
jazz.add(Track("Blue Train", "John Coltrane", 617))
jazz.add(Track("So What", "Miles Davis", 545))
jazz.add(Track("Take Five", "Dave Brubeck", 324))

print(jazz, "runs", jazz.total_duration())
for track in jazz:
    print(" ", track.title, track.duration)
print("Miles in the list?", "So What" in jazz)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class Track:
    """One recording: what it is, who made it, how long it runs."""

    def __init__(self, title, artist, seconds):
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string")
        if not isinstance(artist, str) or not artist.strip():
            raise ValueError("artist must be a non-empty string")
        if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds <= 0:
            raise ValueError("seconds must be a positive integer")
        self.title = title.strip()
        self.artist = artist.strip()
        self.seconds = seconds

    @property
    def duration(self):
        """Length as m:ss."""
        return f"{self.seconds // 60}:{self.seconds % 60:02d}"

    def __eq__(self, other):
        if not isinstance(other, Track):
            return NotImplemented
        return (self.title.lower(), self.artist.lower()) == (other.title.lower(), other.artist.lower())

    def __hash__(self):
        return hash((self.title.lower(), self.artist.lower()))

    def __repr__(self):
        return f"Track({self.title!r}, {self.artist!r}, {self.seconds})"


class Playlist:
    """An ordered collection of tracks. It *has* tracks; it is not a list."""

    def __init__(self, name):
        self.name = name
        self._tracks = []

    def add(self, track):
        """Append a track and return self."""
        if not isinstance(track, Track):
            raise TypeError("only Track objects can be added")
        self._tracks.append(track)
        return self

    def remove(self, title):
        """Drop the first track with this title, or raise ValueError."""
        wanted = str(title).strip().lower()
        for index, track in enumerate(self._tracks):
            if track.title.lower() == wanted:
                return self._tracks.pop(index)
        raise ValueError(f"no track titled {title!r}")

    def __len__(self):
        return len(self._tracks)

    def __iter__(self):
        return iter(self._tracks)

    def __getitem__(self, key):
        if isinstance(key, slice):
            sliced = Playlist(self.name)
            for track in self._tracks[key]:
                sliced.add(track)
            return sliced
        return self._tracks[key]

    def __contains__(self, item):
        if isinstance(item, Track):
            return any(track == item for track in self._tracks)
        if isinstance(item, str):
            wanted = item.strip().lower()
            return any(track.title.lower() == wanted for track in self._tracks)
        return False

    def __add__(self, other):
        if not isinstance(other, Playlist):
            return NotImplemented
        joined = Playlist(f"{self.name} + {other.name}")
        for track in list(self) + list(other):
            joined.add(track)
        return joined

    def __repr__(self):
        return f"Playlist({self.name!r}, {len(self)} tracks)"

    def total_seconds(self):
        return sum(track.seconds for track in self._tracks)

    def total_duration(self):
        """The whole playlist as m:ss."""
        total = self.total_seconds()
        return f"{total // 60}:{total % 60:02d}"

    def by_artist(self, artist):
        """A new Playlist of this artist's tracks."""
        wanted = str(artist).strip().lower()
        found = Playlist(artist)
        for track in self._tracks:
            if track.artist.lower() == wanted:
                found.add(track)
        return found


jazz = Playlist("Jazz")
jazz.add(Track("Blue Train", "John Coltrane", 617))
jazz.add(Track("So What", "Miles Davis", 545))
jazz.add(Track("Take Five", "Dave Brubeck", 324))

print(jazz, "runs", jazz.total_duration())
for track in jazz:
    print(" ", track.title, track.duration)
print("Miles in the list?", "So What" in jazz)
'''}],
                "hints": [
                    "`duration` formats with two pieces: `f\"{self.seconds // 60}:{self.seconds % 60:02d}\"`. The `02d` is what turns 5 into `05`.",
                    "`__iter__` needs an iterator, not a list: `return iter(self._tracks)`. Returning the list itself makes `iter(playlist)` fail.",
                    "In `__getitem__`, test `isinstance(key, slice)` first. `self._tracks[key]` already handles negative indices and raises `IndexError` for you.",
                    "`__contains__` gets whatever the user wrote after `in`. Branch on `isinstance(item, Track)` and `isinstance(item, str)`, and return `False` for everything else rather than raising.",
                ],
                "tests": [
                    {"name": "Track validation and duration", "code": r'''
_t = Track("  Blue Train ", " John Coltrane ", 617)
assert _t.title == "Blue Train", f"title is {_t.title!r}, expected 'Blue Train'"
assert _t.artist == "John Coltrane", f"artist is {_t.artist!r}"
assert _t.duration == "10:17", f"duration is {_t.duration!r}, expected '10:17'"
assert Track("Short", "Someone", 59).duration == "0:59", "seconds are padded to two digits"
assert Track("Long", "Someone", 3600).duration == "60:00", "minutes are not wrapped at 60"
assert repr(_t) == "Track('Blue Train', 'John Coltrane', 617)", f"repr gave {repr(_t)!r}"
'''},
                    {"name": "Track rejects bad input", "code": r'''
for _bad in [("", "A", 10), ("  ", "A", 10), ("T", "", 10), ("T", "A", 0),
             ("T", "A", -5), ("T", "A", 10.5), ("T", "A", "10"), (None, "A", 10)]:
    try:
        Track(*_bad)
        assert False, f"Track{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Track equality is by title and artist", "code": r'''
assert Track("So What", "Miles Davis", 545) == Track("so what", "MILES DAVIS", 999), \
    "equality is case-insensitive on title and artist, and ignores length"
assert Track("So What", "Miles Davis", 545) != Track("So What", "Bill Evans", 545), \
    "a different artist is a different track"
assert not (Track("A", "B", 10) == "A"), "comparison with a string must be False, not a crash"
assert len({Track("A", "B", 10), Track("a", "b", 20)}) == 1, "equal tracks must hash equally"
'''},
                    {"name": "len, iteration and indexing", "code": r'''
_p = Playlist("Jazz")
assert len(_p) == 0, f"a new playlist has len {len(_p)}, expected 0"
assert not _p, "an empty playlist should be falsy — that comes free with __len__"
_t1 = Track("Blue Train", "John Coltrane", 617)
_t2 = Track("So What", "Miles Davis", 545)
_t3 = Track("Take Five", "Dave Brubeck", 324)
assert _p.add(_t1) is _p, "add should return the playlist so calls chain"
_p.add(_t2).add(_t3)
assert len(_p) == 3, f"len is {len(_p)}, expected 3"
assert [t.title for t in _p] == ["Blue Train", "So What", "Take Five"], \
    f"iteration gave {[t.title for t in _p]!r}"
assert _p[0] is _t1 and _p[-1] is _t3, "int indexing should reach the underlying tracks"
try:
    _p[99]
    assert False, "an out-of-range index should raise IndexError"
except IndexError:
    pass
'''},
                    {"name": "Slicing returns a Playlist", "code": r'''
_s = _p[0:2]
assert isinstance(_s, Playlist), f"a slice gave {type(_s).__name__}, expected Playlist"
assert len(_s) == 2 and _s.name == "Jazz", f"the slice is {_s!r}"
assert [t.title for t in _s] == ["Blue Train", "So What"], f"slice holds {[t.title for t in _s]!r}"
assert len(_p) == 3, "slicing must not disturb the original"
assert len(_p[10:20]) == 0, "an empty slice gives an empty playlist, not an error"
'''},
                    {"name": "Membership accepts a Track or a title", "code": r'''
assert "blue train" in _p, "a title string should be found, case-insensitively"
assert Track("So What", "Miles Davis", 1) in _p, "an equal Track should be found"
assert "Nothing Here" not in _p, "an unknown title is not a member"
assert 42 not in _p, "a nonsense operand should be False, not an exception"
assert Track("Ghost", "Nobody", 10) not in _p, "an unrelated track is not a member"
'''},
                    {"name": "Totals, filtering and concatenation", "code": r'''
assert _p.total_seconds() == 1486, f"total_seconds gave {_p.total_seconds()!r}, expected 1486"
assert _p.total_duration() == "24:46", f"total_duration gave {_p.total_duration()!r}, expected '24:46'"
assert Playlist("Empty").total_duration() == "0:00", "an empty playlist runs 0:00"
_miles = _p.by_artist("miles davis")
assert isinstance(_miles, Playlist) and len(_miles) == 1, f"by_artist gave {_miles!r}"
assert _miles[0].title == "So What", f"by_artist picked {_miles[0]!r}"
assert len(_p.by_artist("Nobody")) == 0, "an unknown artist gives an empty playlist"
_other = Playlist("Blues").add(Track("Stormy Monday", "T-Bone Walker", 400))
_both = _p + _other
assert len(_both) == 4 and _both.name == "Jazz + Blues", f"concatenation gave {_both!r}"
assert len(_p) == 3 and len(_other) == 1, "__add__ must not mutate its operands"
'''},
                    {"name": "remove, and composition over inheritance", "code": r'''
_q = Playlist("Copy")
for _t in _p:
    _q.add(_t)
_gone = _q.remove("SO WHAT")
assert _gone.title == "So What", f"remove returned {_gone!r}"
assert len(_q) == 2 and "So What" not in _q, f"after removal the playlist is {list(_q)!r}"
try:
    _q.remove("Not There")
    assert False, "removing an absent title should raise ValueError"
except ValueError:
    pass
assert not issubclass(Playlist, list), "Playlist must contain a list, not inherit from one"
assert repr(_q) == "Playlist('Copy', 2 tracks)", f"repr gave {repr(_q)!r}"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a library catalogue domain model",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Every idea in the course in one domain model, split across two files.
`library.py` holds the classes and is what the checks import; `main.py` is a
demo script that uses it.

## `Item(ABC)` — the shared base

`Item(item_id, title, year)` stores a stripped, non-empty `item_id` and sets up
the loan state. It is **abstract**: `Item("X", "T", 2000)` must raise `TypeError`.

Properties:

- `title` — read/write, validated: a non-empty string, stored stripped.
- `year` — read/write, validated: an `int` between 1400 and 2100 inclusive.
  A `bool` or a string is a `ValueError`.
- `borrower` — read-only; `None` when the item is on the shelf.
- `available` — read-only; `True` exactly when `borrower is None`.
- `kind` — read-only; the lowercased dynamic class name (`"book"`, `"dvd"`,
  `"magazine"`).

Abstract methods every subclass must supply: `loan_days()`, `details()` and
`extra_fields()`.

Concrete behaviour on the base:

- `checkout(borrower)` — refuses a blank borrower and refuses an item already
  on loan (`ValueError` both times). Returns the item.
- `return_item()` — `ValueError` if it was not on loan. Returns the item.
- `describe()` — a template method:

```text
[B1] Dune (1965) - Frank Herbert, 412 pages
```

  i.e. `f"[{item_id}] {title} ({year}) - {details()}"`.
- `__repr__` -> `"Book('B1', 'Dune', 1965)"`.
- `to_dict()` — `kind`, `item_id`, `title`, `year`, `borrower`, plus whatever
  `extra_fields()` adds.
- `from_dict(data)` — a `@staticmethod` that rebuilds the right subclass from
  the `"kind"` field, restoring the borrower. An unknown kind is a `ValueError`.

## The three subclasses

| class | extra constructor arguments | `loan_days()` | `details()` |
|---|---|---|---|
| `Book` | `author`, `pages` (positive int) | 21 | `"Frank Herbert, 412 pages"` |
| `DVD` | `director`, `minutes` (positive int) | 7 | `"dir. Denis Villeneuve, 116 min"` |
| `Magazine` | `issue` (positive int) | 3 | `"issue 7"` |

Blank `author`/`director`, or a non-positive `pages`/`minutes`/`issue`, is a
`ValueError`.

## `Catalogue(name="Library")` — the container

Composition: it holds items in a private dict keyed by `item_id`.

- `add(item)` — `ValueError` on a duplicate id; returns the item.
- `remove(item_id)` — `KeyError` when absent; returns the removed item.
- `__len__`, `__iter__` (over items, insertion order), `__getitem__` by id
  (`KeyError` when absent), `__contains__` accepting an id string or an `Item`.
- `__repr__` -> `"Catalogue('City Library', 3 items)"`.
- `find_by_title(fragment)` — case-insensitive substring match, sorted by title.
- `by_kind(kind)` — every item of that kind, sorted by id.
- `available_items()` / `on_loan()` — sorted by id.
- `checkout(item_id, borrower)` / `return_item(item_id)` — delegate to the item.
- `save(path)` and the `@classmethod` `load(path)` — JSON round-trip preserving
  name, types and loans. A missing file gives an empty catalogue, not a crash.
- `report()` — a header line `"<name> - <n> items"` then one line per item,
  sorted by id, each `describe()` followed by ` [available]` or
  ` [on loan to Ada]`.

## Suggested order

`Item` and its properties, then the three subclasses, then `Catalogue` as a
plain container, then loans, then persistence, then `report()`. The checks are
ordered the same way.
''',
        "deliverables": [
            "`library.py` — `Item`, `Book`, `DVD`, `Magazine` and `Catalogue`, importable with no side effects",
            "An abstract base class whose subclasses cannot forget `loan_days`, `details` or `extra_fields`",
            "Properties that validate `title` and `year` on every write, and expose `available`/`borrower` read-only",
            "Container protocols on `Catalogue`: `__len__`, `__iter__`, `__getitem__`, `__contains__`, `__repr__`",
            "JSON persistence that reconstructs the correct subclass and the loan state",
            "`main.py` — a demo that stocks a catalogue, lends an item, prints the report and reloads from disk",
        ],
        "constraints": [
            "Standard library only — `json` and `abc` are the only imports you need",
            "`library.py` must define classes only; importing it must print nothing",
            "`Catalogue` composes its items; it must not subclass `dict` or `list`",
            "No item may be borrowed twice, and no refused operation may change state",
            "`describe()` and `to_dict()` live on `Item` only — no per-subclass copies",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the empty-catalogue, duplicate-id and missing-file edge cases."},
            {"criterion": "Abstraction & polymorphism", "weight": 25,
             "evidence": "Item is genuinely abstract; describe/to_dict are written once and dispatch to subclass hooks."},
            {"criterion": "Encapsulation", "weight": 20,
             "evidence": "title/year validate on every write; borrower and available are read-only; state is only reachable through methods."},
            {"criterion": "Readability", "weight": 15,
             "evidence": "Docstrings on every public method, no duplicated validation, no debug prints left behind."},
        ],
        "hints": [
            "Assign through the properties inside `Item.__init__` (`self.title = title`), so the validation you wrote once runs at construction too.",
            "`kind` is `type(self).__name__.lower()` — that is what makes `DVD` serialise as `\"dvd\"` and `from_dict` able to find the class again.",
            "`to_dict` should be `{\"kind\": ..., ...shared fields..., **self.extra_fields()}`. The subclasses only supply their own extras.",
            "`from_dict` is a plain `@staticmethod` with one `if/elif` chain over `data[\"kind\"]`; rebuild the object, then re-apply the loan with `item.checkout(data[\"borrower\"])` when there is one.",
        ],
        "files": [
            {"name": "library.py", "content": r'''
import json
from abc import ABC, abstractmethod


class Item(ABC):
    """Anything the library can lend."""

    def __init__(self, item_id, title, year):
        pass

    @property
    def title(self):
        pass

    @title.setter
    def title(self, value):
        pass

    @property
    def year(self):
        pass

    @year.setter
    def year(self, value):
        pass

    @property
    def borrower(self):
        pass

    @property
    def available(self):
        pass

    @property
    def kind(self):
        pass

    @abstractmethod
    def loan_days(self):
        """How long this kind of item may be borrowed for."""

    @abstractmethod
    def details(self):
        """The kind-specific half of describe()."""

    @abstractmethod
    def extra_fields(self):
        """The kind-specific half of to_dict()."""

    def checkout(self, borrower):
        pass

    def return_item(self):
        pass

    def describe(self):
        pass

    def __repr__(self):
        pass

    def to_dict(self):
        pass

    @staticmethod
    def from_dict(data):
        pass


class Book(Item):
    def __init__(self, item_id, title, year, author, pages):
        pass

    def loan_days(self):
        pass

    def details(self):
        pass

    def extra_fields(self):
        pass


class DVD(Item):
    def __init__(self, item_id, title, year, director, minutes):
        pass

    def loan_days(self):
        pass

    def details(self):
        pass

    def extra_fields(self):
        pass


class Magazine(Item):
    def __init__(self, item_id, title, year, issue):
        pass

    def loan_days(self):
        pass

    def details(self):
        pass

    def extra_fields(self):
        pass


class Catalogue:
    """A named collection of items, keyed by id."""

    def __init__(self, name="Library"):
        self.name = name
        self._items = {}

    def add(self, item):
        pass

    def remove(self, item_id):
        pass

    def __len__(self):
        pass

    def __iter__(self):
        pass

    def __getitem__(self, item_id):
        pass

    def __contains__(self, key):
        pass

    def __repr__(self):
        pass

    def find_by_title(self, fragment):
        pass

    def by_kind(self, kind):
        pass

    def available_items(self):
        pass

    def on_loan(self):
        pass

    def checkout(self, item_id, borrower):
        pass

    def return_item(self, item_id):
        pass

    def save(self, path):
        pass

    @classmethod
    def load(cls, path):
        pass

    def report(self):
        pass
'''},
            {"name": "main.py", "content": r'''
from library import Book, DVD, Magazine, Catalogue

shelf = Catalogue("City Library")
shelf.add(Book("B1", "Dune", 1965, "Frank Herbert", 412))
shelf.add(DVD("D1", "Arrival", 2016, "Denis Villeneuve", 116))
shelf.add(Magazine("M1", "Nature", 2024, 7))

shelf.checkout("B1", "Ada")
print(shelf.report())
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "library.py", "content": r'''
import json
from abc import ABC, abstractmethod


class Item(ABC):
    """Anything the library can lend."""

    def __init__(self, item_id, title, year):
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError("item_id must be a non-empty string")
        self.item_id = item_id.strip()
        self.title = title
        self.year = year
        self._borrower = None

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("title must be a non-empty string")
        self._title = value.strip()

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("year must be an integer")
        if not 1400 <= value <= 2100:
            raise ValueError("year must lie between 1400 and 2100")
        self._year = value

    @property
    def borrower(self):
        return self._borrower

    @property
    def available(self):
        return self._borrower is None

    @property
    def kind(self):
        return type(self).__name__.lower()

    @abstractmethod
    def loan_days(self):
        """How long this kind of item may be borrowed for."""

    @abstractmethod
    def details(self):
        """The kind-specific half of describe()."""

    @abstractmethod
    def extra_fields(self):
        """The kind-specific half of to_dict()."""

    def checkout(self, borrower):
        """Lend the item out. Returns the item."""
        if not isinstance(borrower, str) or not borrower.strip():
            raise ValueError("borrower must be a non-empty string")
        if not self.available:
            raise ValueError(f"{self.item_id} is already on loan")
        self._borrower = borrower.strip()
        return self

    def return_item(self):
        """Take the item back. Returns the item."""
        if self.available:
            raise ValueError(f"{self.item_id} is not on loan")
        self._borrower = None
        return self

    def describe(self):
        """One human-readable line, built from the subclass details."""
        return f"[{self.item_id}] {self.title} ({self.year}) - {self.details()}"

    def __repr__(self):
        return f"{type(self).__name__}({self.item_id!r}, {self.title!r}, {self.year})"

    def to_dict(self):
        """A JSON-safe record of this item, including its loan state."""
        record = {
            "kind": self.kind,
            "item_id": self.item_id,
            "title": self.title,
            "year": self.year,
            "borrower": self._borrower,
        }
        record.update(self.extra_fields())
        return record

    @staticmethod
    def from_dict(data):
        """Rebuild the right subclass from a to_dict() record."""
        kind = data.get("kind")
        if kind == "book":
            item = Book(data["item_id"], data["title"], data["year"],
                        data["author"], data["pages"])
        elif kind == "dvd":
            item = DVD(data["item_id"], data["title"], data["year"],
                       data["director"], data["minutes"])
        elif kind == "magazine":
            item = Magazine(data["item_id"], data["title"], data["year"], data["issue"])
        else:
            raise ValueError(f"unknown kind {kind!r}")
        if data.get("borrower"):
            item.checkout(data["borrower"])
        return item


class Book(Item):
    """A printed book."""

    def __init__(self, item_id, title, year, author, pages):
        if not isinstance(author, str) or not author.strip():
            raise ValueError("author must be a non-empty string")
        if isinstance(pages, bool) or not isinstance(pages, int) or pages <= 0:
            raise ValueError("pages must be a positive integer")
        super().__init__(item_id, title, year)
        self.author = author.strip()
        self.pages = pages

    def loan_days(self):
        return 21

    def details(self):
        return f"{self.author}, {self.pages} pages"

    def extra_fields(self):
        return {"author": self.author, "pages": self.pages}


class DVD(Item):
    """A film on disc."""

    def __init__(self, item_id, title, year, director, minutes):
        if not isinstance(director, str) or not director.strip():
            raise ValueError("director must be a non-empty string")
        if isinstance(minutes, bool) or not isinstance(minutes, int) or minutes <= 0:
            raise ValueError("minutes must be a positive integer")
        super().__init__(item_id, title, year)
        self.director = director.strip()
        self.minutes = minutes

    def loan_days(self):
        return 7

    def details(self):
        return f"dir. {self.director}, {self.minutes} min"

    def extra_fields(self):
        return {"director": self.director, "minutes": self.minutes}


class Magazine(Item):
    """A single numbered issue."""

    def __init__(self, item_id, title, year, issue):
        if isinstance(issue, bool) or not isinstance(issue, int) or issue <= 0:
            raise ValueError("issue must be a positive integer")
        super().__init__(item_id, title, year)
        self.issue = issue

    def loan_days(self):
        return 3

    def details(self):
        return f"issue {self.issue}"

    def extra_fields(self):
        return {"issue": self.issue}


class Catalogue:
    """A named collection of items, keyed by id."""

    def __init__(self, name="Library"):
        self.name = name
        self._items = {}

    def add(self, item):
        """Stock one item. Returns it."""
        if not isinstance(item, Item):
            raise TypeError("only Item objects can be catalogued")
        if item.item_id in self._items:
            raise ValueError(f"duplicate item_id {item.item_id!r}")
        self._items[item.item_id] = item
        return item

    def remove(self, item_id):
        """Withdraw one item. Returns it, or raises KeyError."""
        if item_id not in self._items:
            raise KeyError(item_id)
        return self._items.pop(item_id)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items.values())

    def __getitem__(self, item_id):
        if item_id not in self._items:
            raise KeyError(item_id)
        return self._items[item_id]

    def __contains__(self, key):
        if isinstance(key, Item):
            return self._items.get(key.item_id) is key
        return key in self._items

    def __repr__(self):
        return f"Catalogue({self.name!r}, {len(self)} items)"

    def find_by_title(self, fragment):
        """Every item whose title contains the fragment, sorted by title."""
        wanted = str(fragment).strip().lower()
        return sorted((i for i in self if wanted in i.title.lower()),
                      key=lambda i: i.title)

    def by_kind(self, kind):
        """Every item of one kind, sorted by id."""
        wanted = str(kind).strip().lower()
        return sorted((i for i in self if i.kind == wanted), key=lambda i: i.item_id)

    def available_items(self):
        """Everything still on the shelf, sorted by id."""
        return sorted((i for i in self if i.available), key=lambda i: i.item_id)

    def on_loan(self):
        """Everything currently borrowed, sorted by id."""
        return sorted((i for i in self if not i.available), key=lambda i: i.item_id)

    def checkout(self, item_id, borrower):
        """Lend one item out by id."""
        return self[item_id].checkout(borrower)

    def return_item(self, item_id):
        """Take one item back by id."""
        return self[item_id].return_item()

    def save(self, path):
        """Write the whole catalogue to path as JSON."""
        payload = {"name": self.name, "items": [item.to_dict() for item in self]}
        with open(path, "w") as handle:
            json.dump(payload, handle)

    @classmethod
    def load(cls, path):
        """Read a catalogue back. A missing file gives an empty one."""
        try:
            with open(path) as handle:
                payload = json.load(handle)
        except FileNotFoundError:
            return cls()
        catalogue = cls(payload.get("name", "Library"))
        for record in payload.get("items", []):
            catalogue.add(Item.from_dict(record))
        return catalogue

    def report(self):
        """A header line, then one line per item sorted by id."""
        lines = [f"{self.name} - {len(self)} items"]
        for item in sorted(self, key=lambda i: i.item_id):
            status = "available" if item.available else f"on loan to {item.borrower}"
            lines.append(f"{item.describe()} [{status}]")
        return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from library import Book, DVD, Magazine, Catalogue

shelf = Catalogue("City Library")
shelf.add(Book("B1", "Dune", 1965, "Frank Herbert", 412))
shelf.add(DVD("D1", "Arrival", 2016, "Denis Villeneuve", 116))
shelf.add(Magazine("M1", "Nature", 2024, 7))

shelf.checkout("B1", "Ada")
print(shelf.report())
print()
print("on loan:", [i.item_id for i in shelf.on_loan()])
print("books:", shelf.by_kind("book"))
print("search 'a':", [i.title for i in shelf.find_by_title("a")])

shelf.save("catalogue.json")
again = Catalogue.load("catalogue.json")
print("reloaded:", again, "still lent:", [i.item_id for i in again.on_loan()])
'''},
        ],
        "tests": [
            {"name": "Item is abstract", "code": r'''
from library import Item, Book
try:
    Item("X", "Title", 2000)
    assert False, "Item(...) should raise TypeError — it has abstract methods"
except TypeError:
    pass


class _Pamphlet(Item):
    def loan_days(self):
        return 1


try:
    _Pamphlet("P1", "Leaflet", 2020)
    assert False, "_Pamphlet leaves details/extra_fields abstract, so it should raise TypeError"
except TypeError:
    pass
assert issubclass(Book, Item), "Book must subclass Item"
'''},
            {"name": "Properties validate title and year", "code": r'''
from library import Book
_b = Book("  B1 ", "  Dune  ", 1965, "  Frank Herbert ", 412)
assert _b.item_id == "B1", f"item_id is {_b.item_id!r}, expected 'B1'"
assert _b.title == "Dune", f"title is {_b.title!r}, expected 'Dune'"
assert _b.year == 1965 and _b.author == "Frank Herbert", f"got {_b!r} / {_b.author!r}"
for _bad in ["", "   ", None, 7]:
    try:
        _b.title = _bad
        assert False, f"title = {_bad!r} should raise ValueError"
    except ValueError:
        pass
for _bad in [1399, 2101, "1965", True, 19.65]:
    try:
        _b.year = _bad
        assert False, f"year = {_bad!r} should raise ValueError"
    except ValueError:
        pass
assert (_b.title, _b.year) == ("Dune", 1965), f"a refused write changed the item to {_b!r}"
'''},
            {"name": "Constructors reject bad subclass fields", "code": r'''
from library import Book, DVD, Magazine
for _make in [lambda: Book("", "T", 2000, "A", 1), lambda: Book("B", "", 2000, "A", 1),
              lambda: Book("B", "T", 2000, "  ", 1), lambda: Book("B", "T", 2000, "A", 0),
              lambda: DVD("D", "T", 2000, "", 90), lambda: DVD("D", "T", 2000, "A", -3),
              lambda: Magazine("M", "T", 2000, 0), lambda: Magazine("M", "T", 3000, 1)]:
    try:
        _make()
        assert False, "invalid construction arguments should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "kind, loan_days and details dispatch", "code": r'''
from library import Book, DVD, Magazine
_b = Book("B1", "Dune", 1965, "Frank Herbert", 412)
_d = DVD("D1", "Arrival", 2016, "Denis Villeneuve", 116)
_m = Magazine("M1", "Nature", 2024, 7)
assert (_b.kind, _d.kind, _m.kind) == ("book", "dvd", "magazine"), \
    f"kinds are {(_b.kind, _d.kind, _m.kind)!r}"
assert (_b.loan_days(), _d.loan_days(), _m.loan_days()) == (21, 7, 3), \
    f"loan periods are {(_b.loan_days(), _d.loan_days(), _m.loan_days())!r}"
assert _b.details() == "Frank Herbert, 412 pages", f"Book.details gave {_b.details()!r}"
assert _d.details() == "dir. Denis Villeneuve, 116 min", f"DVD.details gave {_d.details()!r}"
assert _m.details() == "issue 7", f"Magazine.details gave {_m.details()!r}"
'''},
            {"name": "describe and repr are written once on Item", "code": r'''
from library import Book, DVD, Item
_b = Book("B1", "Dune", 1965, "Frank Herbert", 412)
_d = DVD("D1", "Arrival", 2016, "Denis Villeneuve", 116)
assert _b.describe() == "[B1] Dune (1965) - Frank Herbert, 412 pages", \
    f"describe gave {_b.describe()!r}"
assert _d.describe() == "[D1] Arrival (2016) - dir. Denis Villeneuve, 116 min", \
    f"describe gave {_d.describe()!r}"
assert repr(_b) == "Book('B1', 'Dune', 1965)", f"repr gave {repr(_b)!r}"
assert "describe" not in Book.__dict__ and "describe" not in DVD.__dict__, \
    "describe() belongs on Item alone — the subclasses supply details() instead"
assert "describe" in Item.__dict__, "Item should define describe()"
'''},
            {"name": "Loan state is encapsulated", "code": r'''
from library import Book
_b = Book("B1", "Dune", 1965, "Frank Herbert", 412)
assert _b.available is True and _b.borrower is None, "a fresh item is on the shelf"
try:
    _b.available = False
    assert False, "available is read-only and should raise AttributeError"
except AttributeError:
    pass
assert _b.checkout(" Ada ") is _b, "checkout should return the item"
assert _b.borrower == "Ada" and _b.available is False, f"after checkout: {_b.borrower!r}"
try:
    _b.checkout("Bo")
    assert False, "borrowing an item already on loan should raise ValueError"
except ValueError:
    pass
assert _b.borrower == "Ada", f"a refused checkout changed the borrower to {_b.borrower!r}"
_b.return_item()
assert _b.available is True, "after return_item the item is back on the shelf"
try:
    _b.return_item()
    assert False, "returning a shelved item should raise ValueError"
except ValueError:
    pass
try:
    _b.checkout("  ")
    assert False, "a blank borrower should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Catalogue is a container", "code": r'''
from library import Book, DVD, Magazine, Catalogue
_c = Catalogue("City Library")
assert len(_c) == 0 and not _c, "a new catalogue is empty and falsy"
_b = Book("B1", "Dune", 1965, "Frank Herbert", 412)
_d = DVD("D1", "Arrival", 2016, "Denis Villeneuve", 116)
_m = Magazine("M1", "Nature", 2024, 7)
for _i in (_b, _d, _m):
    _c.add(_i)
assert len(_c) == 3, f"len is {len(_c)}, expected 3"
assert [i.item_id for i in _c] == ["B1", "D1", "M1"], f"iteration gave {[i.item_id for i in _c]!r}"
assert _c["D1"] is _d, "indexing by id should give the item back"
assert "B1" in _c and _b in _c, "membership works for an id string and for an Item"
assert "ZZ" not in _c and Book("ZZ", "Other", 2000, "A", 1) not in _c, "unknown items are not members"
assert repr(_c) == "Catalogue('City Library', 3 items)", f"repr gave {repr(_c)!r}"
assert not issubclass(Catalogue, dict) and not issubclass(Catalogue, list), \
    "Catalogue should compose a dict, not inherit from one"
'''},
            {"name": "Duplicate and missing ids are errors", "code": r'''
from library import Book, Catalogue
try:
    _c.add(Book("B1", "Another", 2000, "Someone", 10))
    assert False, "adding a duplicate item_id should raise ValueError"
except ValueError:
    pass
assert len(_c) == 3, f"the refused add changed the catalogue to {len(_c)} items"
for _call in [lambda: _c["nope"], lambda: _c.remove("nope"), lambda: _c.checkout("nope", "Ada")]:
    try:
        _call()
        assert False, "an unknown item_id should raise KeyError"
    except KeyError:
        pass
'''},
            {"name": "Queries and lending through the catalogue", "code": r'''
assert [i.item_id for i in _c.by_kind("book")] == ["B1"], f"by_kind gave {_c.by_kind('book')!r}"
assert [i.title for i in _c.find_by_title("a")] == ["Arrival", "Nature"], \
    f"find_by_title('a') gave {[i.title for i in _c.find_by_title('a')]!r}"
assert [i.title for i in _c.find_by_title("DUNE")] == ["Dune"], "the search is case-insensitive"
assert _c.find_by_title("zzz") == [], "no match gives an empty list"
_c.checkout("B1", "Ada")
assert [i.item_id for i in _c.on_loan()] == ["B1"], f"on_loan gave {_c.on_loan()!r}"
assert [i.item_id for i in _c.available_items()] == ["D1", "M1"], f"available gave {_c.available_items()!r}"
_c.return_item("B1")
assert _c.on_loan() == [] and len(_c.available_items()) == 3, "returning puts it back on the shelf"
'''},
            {"name": "save and load round-trip types and loans", "code": r'''
from library import Book, DVD, Magazine, Catalogue
_c.checkout("D1", "Grace")
_c.save("cap_catalogue.json")
_back = Catalogue.load("cap_catalogue.json")
assert isinstance(_back, Catalogue), "load should return a Catalogue"
assert _back.name == "City Library", f"the name came back as {_back.name!r}"
assert len(_back) == 3, f"reloaded catalogue has {len(_back)} items, expected 3"
assert isinstance(_back["B1"], Book) and isinstance(_back["D1"], DVD) \
    and isinstance(_back["M1"], Magazine), "each item must come back as its own subclass"
assert _back["B1"].pages == 412 and _back["D1"].minutes == 116 and _back["M1"].issue == 7, \
    "the subclass-specific fields must survive"
assert _back["D1"].borrower == "Grace", f"the loan was lost: {_back['D1'].borrower!r}"
assert _back["B1"].available is True, "an item that was on the shelf must come back available"
assert len(Catalogue.load("no-such-catalogue-8812.json")) == 0, \
    "a missing file should give an empty catalogue, not an exception"
'''},
            {"name": "from_dict rejects an unknown kind", "code": r'''
from library import Item
try:
    Item.from_dict({"kind": "hologram", "item_id": "H1", "title": "X", "year": 2000})
    assert False, "an unknown kind should raise ValueError"
except ValueError:
    pass
_rec = Item.from_dict({"kind": "magazine", "item_id": "M9", "title": "Zine",
                       "year": 2001, "borrower": None, "issue": 3})
assert _rec.kind == "magazine" and _rec.issue == 3 and _rec.available, f"got {_rec!r}"
'''},
            {"name": "report reads cleanly, and library.py is import-clean", "code": r'''
_c.return_item("D1")
_c.checkout("B1", "Ada")
_lines = _c.report().split("\n")
assert _lines[0] == "City Library - 3 items", f"the header line is {_lines[0]!r}"
assert len(_lines) == 4, f"expected a header and 3 item lines, got {_lines!r}"
assert _lines[1] == "[B1] Dune (1965) - Frank Herbert, 412 pages [on loan to Ada]", \
    f"first item line is {_lines[1]!r}"
assert _lines[2].startswith("[D1]") and _lines[2].endswith("[available]"), \
    f"second item line is {_lines[2]!r}"
assert _lines[3].startswith("[M1]"), "items are listed in id order"
_src = open("library.py").read()
assert "print(" not in _src, "library.py defines classes; the printing belongs in main.py"
'''},
        ],
    },
}
