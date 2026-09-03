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
            "read": [
                {
                    "title": "Two floats and no identity: what makes a value a value",
                    "minutes": 14,
                    "body": r'''
Draw a displacement on a squared map: three squares east, four squares north. Hand the
map to a friend and ask them to draw the same displacement on a map of their own. There
are now two drawings, and there is still one displacement. Nobody would call the friend's
arrow a *different* arrow because it sits on a different sheet: it points the same way
and runs the same length, and that is everything an arrow is.

A bank account is the other kind of thing. Two accounts holding exactly a hundred euros
each are two accounts, and a deposit into one leaves the other where it was. They are
told apart by *which one they are*, not by what they hold.

Python's default is the bank-account kind. Every object is given an identity when it is
made, and until you say otherwise `==` compares identities and nothing else:

```python
class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)


a = Vector2D(3, 4)
b = Vector2D(3, 4)
print(a == b)        # False
print(a is b)        # False
print(len({a, b}))   # 2
```

Two arrows drawn identically, and Python holds that they are different. That is right for
an account and wrong for an arrow, and this module is about telling Python which of the
two you are building. The lab, *An immutable Vector2D*, builds the arrow: a value with no
identity of its own, that compares by its components, works as a dictionary key, does
arithmetic with the ordinary operators, and cannot be changed once it exists.

## What `Vector2D(3, 4)` actually does

Two things happen at construction, and only the second is yours. `Vector2D(3, 4)` first
calls `Vector2D.__new__`, which allocates a blank object. Then it calls `__init__` with
that blank object as its first argument, and `__init__` fills the blanks in. The blank
object is what `self` is: the receiver of the call, passed explicitly because Python
hides nothing — Java hides the same binding as `this`. `a.dot(b)` and
`Vector2D.dot(a, b)` are one call written two ways:

```python
class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y


a = Vector2D(3, 4)
b = Vector2D(-1, 2)
print(a.dot(b))              # -3.0 + 8.0 = 5.0
print(Vector2D.dot(a, b))    # the same call, spelled out
```

Because `__init__` is an initialiser and not a constructor, it must return `None`. The
object already exists by the time it runs, and there is nothing for it to hand back.
Python enforces this rather than trusting you:

```python
# raises TypeError
class Broken:
    def __init__(self, x):
        self.x = x
        return self


Broken(1)
```

The message is `__init__() should return None, not 'Broken'`, and it is the language
stating the division of labour: `__new__` makes, `__init__` fills.

## Equality by value

To make two identical arrows equal, define `__eq__`. The first version anyone writes
compares the components and stops there, `self.x == other.x and self.y == other.y`, and
for two vectors it is right. Now ask a question that does not involve another vector.
`Vector2D(3, 4) == (3, 4)` reaches that body with `other` bound to a tuple, a tuple has
no `.x`, and the comparison raises `AttributeError`. That looks like an edge case until you notice where `==` gets
called without your knowledge: `v in [1, 2, 3]` compares `v` with `1`, and `list.index`
and `list.remove` do the same. An equality that crashes on the wrong type breaks
containers you never intended to put the vector in.

The fix is not `return False`. It is `return NotImplemented`, and the reason is the
protocol behind `==`. Python asks the left operand first: `Vector2D.__eq__(v, (3, 4))`.
If that returns `NotImplemented` — which means *I have no opinion* — Python turns round
and asks the right operand, `tuple.__eq__((3, 4), v)`. When that declines too, Python
falls back to comparing identity, which gives `False`, and `!=` is derived from the same
answer for free. Returning `False` directly gives the same result today and takes away
the other operand's turn: a class that *does* know how to compare itself with a vector
never gets asked.

```python
class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y


v = Vector2D(3, 4)
print(v == (3, 4))            # False, and no exception
print(v != "nope")            # True
print(v in [1, "two", v])     # True: the == against 1 and "two" declined politely
```

## The hash has to agree, and Python will not let you forget

Put the new class in a set and something unexpected happens:

```python
# raises TypeError
class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y


print(Vector2D.__hash__)      # None
{Vector2D(3, 4)}
```

Define `__eq__` and leave `__hash__` alone, and Python sets `__hash__` to `None` for you:
the instances stop being hashable. That looks officious until you see what a set does
with a hash. A set does not compare a new member against every existing one; that would
make membership linear. It calls `hash()` on the candidate, uses
the result to choose a bucket, and only compares with `==` against what is already in
that bucket. So two objects that `==` calls equal but that hash differently land in
different buckets, never meet, and the set keeps both. The inherited hash is built from
identity, so leaving it in place beside a value-based `__eq__` would produce exactly
that: a set holding two equal vectors. Rather than let it rot quietly, the language
breaks loudly.

The rule follows from the mechanism: **equal objects must hash equally**. The converse is
not required — unequal objects may share a hash and merely share a bucket — but the
forward direction is the whole contract. The way to honour it is to hash the fields
`__eq__` compares, and a tuple does the work:

```python
class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


bag = {Vector2D(1, 2), Vector2D(1, 2), Vector2D(0, 0)}
print(len(bag))                                     # 2
lookup = {Vector2D(1, 2): "here"}
print(lookup[Vector2D(1, 2)])                       # here
print(hash(Vector2D(1, 2)) == hash((1.0, 2.0)))     # True
```

A tuple's hash is computed from its members' hashes, so two tuples with equal members
hash equally, so two vectors with equal components hash equally. The contract is met by
construction. The module's numeric exercise is this trap made concrete: a `Card` whose
`__eq__` and `__hash__` mention `rank` alone, so six cards in three ranks make a set of
three. The set never looks at your attributes; it calls the two methods you wrote and
believes them.

## Arithmetic, and how a refusal travels

`a + b` is not a special form. Python evaluates it as `type(a).__add__(a, b)`, and if
that returns `NotImplemented` it tries the reflected method on the other side,
`type(b).__radd__(b, a)`. If both decline, Python raises `TypeError: unsupported operand
type(s) for +: 'Vector2D' and 'int'`, naming both types.

The reflected method is what makes `2 * v` work. Trace it: the left operand is an `int`,
so Python asks `int.__mul__(2, v)` first. `int` has never heard of a vector and returns
`NotImplemented`. Only then does Python ask `Vector2D.__rmul__(v, 2)`, and notice the
argument order: the vector arrives as `self` and the `2` as the argument, swapped
relative to how the expression was written. Instrument both hooks and watch:

```python
class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Vector2D({self.x!r}, {self.y!r})"

    def __mul__(self, scalar):
        print("  __mul__ asked with", scalar)
        if isinstance(scalar, bool) or not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        print("  __rmul__ asked with", scalar)
        return self.__mul__(scalar)


v = Vector2D(3, 4)
print("v * 2")
print(v * 2)
print("2 * v")
print(2 * v)
```

`v * 2` calls `__mul__` once. `2 * v` prints `__rmul__` first, because `int` had already
declined, and then `__mul__`, because `__rmul__` delegates. For a scalar the delegation
is right: scaling commutes, so the swapped operands make no difference. For matrix
multiplication the same delegation would be a bug, which is worth remembering the day
you overload `@`.

The mistake people make here is `raise NotImplementedError`. It is tempting because the
two names differ by a suffix and both seem to say *not supported*. They do not.
`NotImplemented` is a value, returned, meaning *ask someone else*; `NotImplementedError`
is an exception, raised, meaning *a subclass was supposed to fill this in*. Raising it
aborts the reflected lookup, so `2 * v` never reaches `__rmul__`, and it reports the
wrong problem. `return False` is worse in a quieter way: `v + 5` then evaluates to
`False`, and nothing tells you.

One guard in that block deserves a sentence. `isinstance(True, int)` is `True`, because
`bool` is a subclass of `int`. Without the explicit `bool` check, `True * v` would scale
the vector by one and `False * v` would collapse it to zero, silently.

## A repr that reads back

Print the vector above and you get `Vector2D(3.0, 4.0)`, because the block defined
`__repr__`. Leave it out and you get `<__main__.Vector2D object at 0x...>`, which names
the type and the identity — the two facts a value type is trying not to have. The
convention for `__repr__` is that it should look like the expression that would rebuild
the object, so that `eval(repr(v)) == v`:

```python
class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Vector2D({self.x!r}, {self.y!r})"

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


v = Vector2D(3, 4)
print(repr(v))                 # Vector2D(3.0, 4.0)
print(eval(repr(v)) == v)      # True
print([v, Vector2D(0, 1)])     # a list shows the reprs of its members
```

The `!r` inside the f-string asks each component for *its* repr, which is why `3` comes
back as `3.0`: the stored value is a float, and the repr says so. `__str__` is the
human-facing form, and with none defined, `print(v)` falls back to `__repr__`. The
reverse does not hold — define only `__str__` and a list of vectors prints as angle
brackets, because a container shows the reprs of its members and never their strs.
Write `__repr__` first; add `__str__` when a genuinely different display is wanted.

## Making it stay put

Everything so far assumed the components do not change. That assumption is
load-bearing. Hash a mutable object by its fields, put it in a set, and change a field:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))


p = Point(1, 2)
bag = {p}
p.x = 5
print(p in bag)      # False
print(len(bag))      # 1
```

The point is in the set — `len` says so — and the set cannot find it, because it was
filed under the hash of `(1, 2)` and now hashes to something else. Nothing raised. This is
why every hashable built-in is immutable, and why the lab insists a `Vector2D` never
changes after construction.

Python offers three strengths of immutability. The weakest is a naming convention: call
the attribute `_x`, and readers understand they are not to write to it. Nothing enforces
it. Next, `__slots__ = ("x", "y")` replaces the per-instance dictionary with two fixed
descriptors, so `v.z = 1` raises `AttributeError` — a typo caught, and memory saved. What
slots do *not* do is stop `v.x = 9`, which is an ordinary write to a slot that exists.
Real immutability needs the third step: override `__setattr__` and `__delattr__` to
refuse.

That creates a problem inside `__init__`. The line `self.x = float(x)` is not a bare
store; Python evaluates it as `type(self).__setattr__(self, "x", float(x))`, and by the
time `__init__` runs, your refusing guard is already installed:

```python
# raises AttributeError
class Vector2D:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = float(x)      # goes through the guard below
        self.y = float(y)

    def __setattr__(self, name, value):
        raise AttributeError("Vector2D is immutable")


Vector2D(3, 4)
```

The guard refuses its own constructor. The way past is to name the machinery the guard
stands in front of: `object.__setattr__(self, "x", float(x))` performs the plain store
without consulting your override. That is the one line in the class entitled to step
around the rule, and `__init__` is the only place it should appear:

```python
class Vector2D:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        object.__setattr__(self, "x", float(x))
        object.__setattr__(self, "y", float(y))

    def __setattr__(self, name, value):
        raise AttributeError("Vector2D is immutable")

    def __delattr__(self, name):
        raise AttributeError("Vector2D is immutable")


v = Vector2D(3, 4)
print(v.x, v.y)      # 3.0 4.0
try:
    v.x = 9
except AttributeError as e:
    print("refused:", e)
try:
    del v.y
except AttributeError as e:
    print("refused:", e)
print(v.x, v.y)      # 3.0 4.0, untouched
```

`AttributeError` is the right exception, because it is what Python itself raises for a
write it cannot perform — a property with no setter, an attribute on a tuple. Matching it
means `except AttributeError` around a write behaves the same whether an object defends
itself by hand or with `@property`.

## Where value semantics stops holding

A value type inherits its components' idea of equality, warts included. The components
here are floats, and float arithmetic rounds:

```python
class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __eq__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)


total = Vector2D(0.1, 0) + Vector2D(0.2, 0)
print(total == Vector2D(0.3, 0))     # False
print(total.x)                       # 0.30000000000000004
```

Two vectors a physicist would call equal are not equal to `==`, and no `__eq__` you write
can fix that without breaking the hash contract, because a tolerance is not transitive:
if $a$ is within $\varepsilon$ of $b$ and $b$ within $\varepsilon$ of $c$, nothing puts
$a$ within $\varepsilon$ of $c$, so "equal" objects would no longer be guaranteed the
same hash. This is why the lab's tests compare `magnitude()` with `abs(got - 5.0) <
1e-12` and use exact `==` only where the arithmetic is exact. A value type gives you *the
components' equality*, not a geometric one.

The other boundary is the one this reading opened with. Anything whose history matters —
an account, a player, a connection — should keep identity equality; give it a value-based
`__eq__` and two different accounts with the same balance become interchangeable to
every container in the program. Ask which kind of thing it is before writing a single
dunder. If you can hand it to a friend and get the same
thing back on a different sheet of paper, it is a value; build it the way the lab builds
`Vector2D`.
''',
                },
                {
                    "title": "When things go wrong: exceptions",
                    "minutes": 13,
                    "body": r'''
Four readings come off a sensor log and the job is to total them. It is not a hard job
until one of the four is the word `twelve`:

```python
# raises ValueError
readings = ["12", "7", "twelve", "3"]
total = 0
for text in readings:
    total += int(text)
print(total)
```

The last line never runs. `int("twelve")` cannot produce a number, and rather than
inventing one it **raises** an exception: it abandons the expression it was in the
middle of, abandons the loop around it, and abandons every function that called it,
climbing outwards until something catches it or it reaches the top of the program. When
nothing catches it, Python prints the traceback — the list of frames it climbed through —
and exits with `ValueError: invalid literal for int() with base 10: 'twelve'`.

Two facts are worth taking from that. The first is that an exception is not a return
value; `total` is never assigned, because the addition never happened. The second is that
the traceback is a *feature*: it names the exception type, the message, and the exact line
in each frame, which is more than any error code you would have designed yourself.

## Catching one thing

`try` marks the code that might fail; `except` names the failure you are prepared for.

```python
readings = ["12", "7", "twelve", "3"]
total = 0
for text in readings:
    try:
        total += int(text)
    except ValueError:
        print("skipping", repr(text))
print("total:", total)
```

The exception now stops climbing at the `except`, the loop carries on, and the total is
22 over the three readings that were numbers. Notice how small the `try` block is: one
statement, the one that can fail. Wrapping the whole loop instead would catch the same
error and then leave the loop, so the last reading would be lost as well.

Name the exception you expect. `except ValueError` catches that class and its subclasses
and lets everything else past, which is what you want, because the errors you did not
predict are the ones you need to see.

## The full shape: `else` and `finally`

A `try` statement has four parts, and the two less-used ones are about *what ran* rather
than *what failed*:

```python
def parse(text):
    try:
        value = int(text)
    except ValueError:
        print("  except:  not a number")
        return None
    else:
        print("  else:    parsed", value)
        return value
    finally:
        print("  finally: done with", repr(text))


print("parse('7')")
print("  ->", parse("7"))
print("parse('seven')")
print("  ->", parse("seven"))
```

`else` runs when the `try` body finished without raising, and it exists so that the `try`
can hold nothing but the risky line. Code that belongs after a successful parse would, if
you put it inside the `try`, have its *own* `ValueError` caught by a handler written for
the conversion — a real way to be told the wrong thing about where a bug is.

`finally` runs whichever way the statement leaves. Read the output: the `finally` line
prints after the `else` line and before the `-> 7`, so it runs even though `else` had
already said `return`. That is what makes it the place for cleanup — closing a file,
releasing a lock, putting a cursor back — and it is the machinery `with` is built on. One
warning about it: a `return` inside a `finally` discards whatever the block was doing,
including an exception on its way out, which turns a crash into a wrong answer.

## Refusing loudly beats returning nonsense

Here is a withdrawal that reports failure the way C reports it, with a value nobody can
mistake for a balance — until they do:

```python
def withdraw(balance, amount):
    """Return the new balance, or -1 if the withdrawal is refused."""
    if amount <= 0 or amount > balance:
        return -1
    return balance - amount


accounts = {"ada": 500, "bo": 40}
for name in list(accounts):
    accounts[name] = withdraw(accounts[name], 100)

print(accounts)
print("the bank now believes it holds", sum(accounts.values()), "kr")
```

Bo had 40 kr and asked for 100, so `withdraw` refuses — and the caller stores the refusal
as a balance. The dictionary reads `{'ada': 400, 'bo': -1}` and the bank's books are out
by 41 kr, with nothing on the screen to say so. The caller is not careless; it is doing
what the signature invites, because `-1` has the same type as a balance and arrives
through the same channel.

Raise instead, and the refusal cannot be mistaken for an answer:

```python
def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if amount > balance:
        raise ValueError(f"Insufficient funds: {balance} available, {amount} asked for")
    return balance - amount


accounts = {"ada": 500, "bo": 40}
for name in list(accounts):
    try:
        accounts[name] = withdraw(accounts[name], 100)
    except ValueError as err:
        print(f"{name}: refused - {err}")

print(accounts)
print("the bank holds", sum(accounts.values()), "kr")
```

The assignment on the left of the `=` never happens for `bo`, because the right-hand side
never produced a value. Bo keeps 40 kr, the books balance at 440, and the caller was told
which account and why. Two rules come out of this, and the lab *A bank account that says
no* is built on both: **validate before you change state**, so a refused call cannot have
half-happened; and **put the reason in the message**, because `err` is the only thing the
handler will have to work with.

## The exceptions you will actually meet

| Exception | Typical cause |
|---|---|
| `NameError` | a name that is not defined — usually a typo, or a use before the assignment |
| `TypeError` | wrong type: `"a" + 1`, calling something that is not a function, a missing argument |
| `ValueError` | right type, unusable value: `int("abc")`, `math.sqrt(-1)` |
| `KeyError` | a dictionary key that is not there |
| `IndexError` | a list index past the end |
| `AttributeError` | `thing.method()` where `thing` has no such attribute — including a misspelt one |
| `ZeroDivisionError` | dividing by zero |
| `FileNotFoundError` | opening a path that does not exist |

`KeyError` and `IndexError` share a base, `LookupError`; `FileNotFoundError` is one of
several `OSError`s. Catching the base catches all of its children, which is how
`except OSError` covers a missing file, a permission refusal and a full disk at once.

## Your own exception types

When the caller needs to tell *your* failure from every other failure, give it a class.
Subclass `Exception` — never `BaseException`, which is also the ancestor of
`KeyboardInterrupt` and `SystemExit` and would make your error catchable by handlers that
were written to let those two through:

```python
class OutOfStock(Exception):
    """No more of this part in the warehouse."""


def reserve(stock, part, count):
    if stock.get(part, 0) < count:
        raise OutOfStock(f"{part}: {stock.get(part, 0)} left, {count} wanted")
    stock[part] -= count


warehouse = {"wiper blades": 2}
try:
    reserve(warehouse, "wiper blades", 5)
except OutOfStock as err:
    print("back-order:", err)
except ValueError:
    print("this handler never runs: OutOfStock is not a ValueError")

print(isinstance(OutOfStock("x"), Exception))
print(warehouse)
```

Handlers are tried in order and the first matching one wins, so the narrow class has to
come before any base it inherits from. The empty body is not laziness: an exception class
carries its meaning in its *name*, and `OutOfStock` already says everything a handler
needs to dispatch on.

## Catching too much

The tempting shortcut is a handler wide enough that nothing can get past it. Watch what
it costs:

```python
def total_price(items):
    return sum(item["prcie"] for item in items)      # a typo, three months old


basket = [{"price": 10}, {"price": 5}]
try:
    print(total_price(basket))
except Exception:
    print("could not total the basket")

try:
    print(total_price(basket))
except KeyError as err:
    print("no such field:", err)
```

The same defect is reported twice. The wide handler says the basket could not be totalled,
which sends you looking at the basket; the narrow one prints `no such field: 'prcie'` and
the misspelling is on the screen. A bare `except:` is wider still — it catches
`BaseException`, so `KeyboardInterrupt` lands in it too and the program stops answering
Ctrl-C. The rule that follows: catch the class you know how to handle, and let the rest
climb.

## Ask forgiveness, not permission

Two ways to increment a counter that may not exist yet:

```python
def bump_lbyl(counts, name):
    if name in counts:          # look before you leap
        counts[name] += 1
    else:
        counts[name] = 1


def bump_eafp(counts, name):
    try:                        # ask forgiveness, not permission
        counts[name] += 1
    except KeyError:
        counts[name] = 1


counts = {"ada": 3}
bump_lbyl(counts, "ada")
bump_eafp(counts, "bo")
print(counts)
```

Both give `{'ada': 4, 'bo': 1}`, and for a dictionary either is defensible — the `try`
version does one lookup instead of two when the key is present, which is the common case.
The preference stops being a matter of taste when the thing you are checking can change
between the check and the use. `if os.path.exists(path)` followed by `open(path)` is two
questions about a filesystem other programs are also writing to, and the file can vanish
in the gap; `try: open(path) except FileNotFoundError:` asks once, and the answer it gets
is the answer it acts on.

## Where this stops

An exception you cannot do anything about should not be caught. The lab's
`safe_withdraw` turns a `ValueError` into `True` or `False`, and that is right *there*,
at the edge of the program where a caller wants a yes-or-no and has no use for a message.
Three layers down it would be wrong: the reason would be discarded at the one place that
still knew it, and the caller would be left holding a `False` with no idea whether the
amount was negative or the account was empty.

When you catch something in order to add context and still cannot fix it, re-raise. A bare
`raise` inside a handler sends on the exception that is already travelling, traceback
intact:

```python
# raises ValueError
def load_timeout(text):
    try:
        return int(text)
    except ValueError:
        print("log: timeout setting was", repr(text))
        raise


print(load_timeout("30"))
load_timeout("half a minute")
```

The note is logged and the failure still reaches whoever is entitled to decide what to do
about it — which is the whole argument of this reading, one function further out.
''',
                },
                {
                    "title": "Classes, modules and files",
                    "minutes": 13,
                    "body": r'''
A program that defines everything and runs everything in one file is fine at eighty lines
and unusable at eight hundred. This reading is about the three splits that keep it
readable: state and behaviour into a **class**, code into **modules** across several
files, and data out of the process altogether into a **file** — usually as JSON, which is
how the inventory lab at the end of the course, and the capstone after it, keep anything
between runs.

## Classes: data and behaviour in one place

A class is a blueprint. Each object built from it carries its own data — **attributes** —
and shares the same **methods**:

```python
class Car:
    wheels = 4                           # a class attribute: one copy, shared

    def __init__(self, plate, km=0):     # runs when a Car is created
        self.plate = plate               # instance attributes: this car's own data
        self.km = km

    def drive(self, distance):
        self.km += distance
        return self.km

    def __str__(self):                   # what print() shows
        return f"{self.plate} ({self.km} km)"


golf = Car("AB 12345")
polo = Car("CD 67890", km = 91000)
golf.drive(120)
print(golf)
print(polo)
print(golf.wheels, polo.wheels, Car.wheels)
print(Car.drive(golf, 30), golf.km)
```

`wheels` is written once in the class body and read through every instance, because a
lookup that fails on the object falls through to the class. `plate` and `km` are written
per object inside `__init__`, so the two cars disagree about them and agree about
`wheels`. Module 3 takes that lookup rule apart properly, including what happens the
moment somebody assigns to `golf.wheels`.

The last line is the one to sit with. `golf.drive(120)` and `Car.drive(golf, 30)` are the
same call written two ways: the method is a plain function on the class, and the dot
supplies the object in front of it as the first argument. That is all `self` is — the
receiver, named explicitly, exactly as the first reading of this module described it for
`Vector2D.dot`.

`__str__` is the human-facing display and is what `print` and `str()` reach for. It is the
sibling of the `__repr__` you wrote for `Vector2D`: define `__repr__` first, because a
list of cars shows the reprs of its members, and add `__str__` when the display a person
should read differs from the one a programmer should.

## Modules: one file is one module

Every `.py` file is a module, named after the file. Importing one gives you its contents:

```python
import math
from random import randint

print(math.sqrt(16))
print(round(math.pi, 4))
print(1 <= randint(1, 6) <= 6)
```

`import math` binds one name, `math`, and everything inside it is reached through the dot.
`from random import randint` binds the function itself, which is shorter to read and
costs you the label saying where it came from. Both forms run the module the first time
and cache it; neither copies anything.

## What `import` actually does

The mechanism is worth seeing rather than believing. Here a module is written to a scratch
folder, that folder is put on the import path, and the module is imported twice:

```python
import os
import sys
import tempfile

source = """
print("greet.py is running, and __name__ is", __name__)

MESSAGE = "hello from greet"


def main():
    print(MESSAGE)


if __name__ == "__main__":
    main()
"""

folder = tempfile.mkdtemp()                    # a scratch directory to write into
with open(os.path.join(folder, "greet.py"), "w") as f:
    f.write(source)

sys.path.insert(0, folder)                     # where import looks
print("this file's __name__ is", __name__)
import greet                                   # runs greet.py, top to bottom, once
import greet                                   # nothing at all: already imported
print(greet.MESSAGE)
greet.main()
```

Three things show up in that output. `greet.py is running` appears **once**, though the
import is written twice: the first import executes the file and files the result under
`sys.modules["greet"]`, and every import after that is a dictionary lookup. Anything with
a side effect at the top level of a module therefore happens once per program, at a
moment decided by whoever imports first.

Second, `__name__` inside `greet` is `"greet"`, while `__name__` in the file you are
running is `"__main__"`. That is the whole trick behind the guard:

```text
if __name__ == "__main__":
    main()
```

The body runs when the file is the one being executed and is skipped when the file is
being imported. Without it, importing a module would run its demo, its prompts and its
test data as a side effect of asking for one function out of it. With it, a file can be
both a library and a program.

Third, `hello from greet` prints twice — once through the module's `MESSAGE` and once
through `greet.main()` — while the guarded call inside `greet.py` printed nothing at all,
because on import `__name__` was not `"__main__"`.

The habit that falls out: keep the code that *defines* things — classes, functions — in
modules, and the code that *runs* things behind the guard in a `main.py`. The inventory
lab is built exactly that way, with `inventory.py` for the classes and `main.py` for the
demo, and its checks import from `inventory.py` directly.

## Files

`open` gives you a file object; the mode says what you may do with it.

```python
import os
import tempfile

path = os.path.join(tempfile.mkdtemp(), "notes.txt")

with open(path, "w") as f:        # "w" write (truncates!), "a" append, "r" read
    f.write("first line\n")       # write adds no newline of its own
    f.write("second line\n")

with open(path) as f:             # "r" is the default
    for line in f:
        print(repr(line))

with open(path) as f:
    print(f.read().splitlines())
```

Two details bite people. `"w"` truncates an existing file the instant it is opened, before
a single byte is written, so a mistyped mode destroys the thing you meant to append to.
And iterating a file yields lines *with* their newline still attached, which is why the
first loop prints `'first line\n'` and why `line.strip()` appears in so much
line-processing code.

Reading a path that is not there raises, and the exception says which path:

```python
# raises FileNotFoundError
with open("no-such-config-91827.json") as f:
    print(f.read())
```

## What `with` is for

`with` is the reason none of the blocks above call `close()`. It closes the file on the
way out of the block whichever way the block ends — including on an exception, which is
the case that matters, because data sitting in an unflushed buffer is lost when the
process dies:

```python
import os
import tempfile

path = os.path.join(tempfile.mkdtemp(), "half-written.txt")

try:
    with open(path, "w") as f:
        f.write("this much got written\n")
        raise ValueError("something went wrong in the middle")
except ValueError as err:
    print("caught:", err)

print("the file object is closed:", f.closed)
with open(path) as check:
    print(repr(check.read()))
```

The exception travelled, and the line still reached the disk. This is the `finally`
guarantee from the previous reading, packaged: `with` calls the object's `__exit__` on the
way out, and for a file `__exit__` flushes and closes.

## JSON

A dictionary of numbers and strings survives a program's death as text, and JSON is the
format everything else can read too. Four function names, and the `s` is the whole
distinction — `dumps` and `loads` work on **s**trings, `dump` and `load` on open files:

```python
import json

data = {"ada": 90, "linus": 75, "passed": True, "notes": None}
text = json.dumps(data, indent=2)      # object -> string
print(text)
print(type(text).__name__)

back = json.loads(text)                # string -> object
print(back == data)
```

`True` and `None` come back as themselves, having spent the trip as JSON's `true` and
`null`. Straight to a file it is the pair without the `s`, and the file object is the
second argument:

```python
import json
import os
import tempfile

path = os.path.join(tempfile.mkdtemp(), "scores.json")
scores = {"ada": 90, "linus": 75}

with open(path, "w") as f:
    json.dump(scores, f)               # object -> file

with open(path) as f:
    print(json.load(f))                # file -> object
```

## What JSON cannot hold

JSON knows six things: strings, numbers, `true`, `false`, `null`, arrays and objects whose
keys are strings. Everything Python has beyond that is converted on the way out and does
not come back:

```python
import json

original = {"tags": ("new", "boxed"), 1: "first", "when": {"year": 2026}}
back = json.loads(json.dumps(original))
print(back)
print(type(original["tags"]).__name__, "->", type(back["tags"]).__name__)
print(list(original), "->", list(back))
```

The tuple returns as a list and the integer key returns as the string `"1"`, because JSON
has neither. Nothing raised, and `original == back` is false. A round trip through JSON is
lossy, and knowing exactly what it loses is the difference between a save file that
reloads and one that reloads *almost*.

Your own classes do not get that far — they raise instead of being guessed at:

```python
# raises TypeError
import json


class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price


json.dumps(Item("Torch", 249.0))
```

So the conversion is yours to write, in both directions: a method that turns the object
into a dict of JSON-legal values, and a constructor that rebuilds it from one.

```python
import json


class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def to_dict(self):
        return {"name": self.name, "price": self.price}

    @classmethod
    def from_dict(cls, row):
        return cls(row["name"], row["price"])


text = json.dumps([Item("Torch", 249.0).to_dict(), Item("Jack", 899.0).to_dict()])
print(text)
again = [Item.from_dict(row) for row in json.loads(text)]
print(type(again[0]).__name__, again[0].name, again[0].price)
```

`from_dict` is a `@classmethod`: it receives the class rather than an instance, which is
what lets it build one, and what makes `cls(...)` build the *subclass* when a subclass
inherits it. That is the shape of `Inventory.load(path)` in this course's inventory lab
and of `Catalogue.load(path)` in the capstone — an alternative constructor, reading a file
and handing back a finished object. Module 3 comes back to `@classmethod` in its own
right.

## Where this stops

The formats have edges worth knowing before you meet them. JSON has no date type, so a
timestamp goes across as a string in a format you choose and parse back yourself. Its
numbers are doubles, so a large integer id can lose its last digits in a system that reads
it as one. And `json.load` on a file that is corrupt, truncated or empty raises
`JSONDecodeError` — a `ValueError` — which is a different failure from the file being
missing and deserves a different answer, as the *Save and load with JSON* lab insists.

One note about this page. In the browser the files above live in a virtual folder that is
thrown away when you reload, so nothing you write here can touch your machine. Everything
else — modes, buffering, the exceptions, what JSON keeps and drops — behaves exactly as it
does on your own disk.
''',
                },
            ],
            "quiz": [{
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
            }, {
                "title": "Errors, classes and files",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A `try` statement's `else` branch ends with `return value`. What runs before the function actually returns?",
                        "opts": [
                            "Nothing further: a `return` hands back at once and abandons the statement",
                            "The `finally` block, which runs on every way out, `return` included",
                            "The `except` block, which is entered on the way out of any `try`",
                            "Only the caller's next line; the `try` statement is over",
                        ],
                        "a": 1,
                        "why": r"""
`finally` always runs — that is what it is for. Trace the `parse()` example from the
reading and the `finally:` line prints *after* the `else:` line and *before* the returned
value reaches the caller: the return value is computed, the statement is unwound, the
`finally` body runs, and only then does the function hand anything back. That is what
makes it the place for cleanup, and it is exactly the guarantee `with` is built on. The
tempting answer is that a `return` ends everything — it ends the *function's* work, but
not the `try` statement's obligations. `except` is the answer for a different question: it
runs only when an exception was raised and matched, so on the successful path it never
runs at all.
""",
                    },
                    {
                        "q": "Why catch `except ValueError` rather than writing a bare `except:`?",
                        "opts": [
                            "A bare `except:` is a syntax error unless a class is named",
                            "Naming the class is faster: Python can skip the handlers that do not match",
                            "A bare `except:` also swallows the failures you did not predict, `KeyboardInterrupt` among them",
                            "There is no difference in what gets caught — the bare form is a shorthand for `except Exception`",
                        ],
                        "a": 2,
                        "why": r"""
Catch what you can handle, and let everything else surface so you can fix it. A bare
`except:` matches `BaseException`, so a misspelt attribute, a `NameError` in a branch
nobody exercised and the Ctrl-C the user pressed all land in a handler written for a bad
number, and each of them is reported as whatever that handler says. The reading's basket
shows the cost: `except Exception` says the basket could not be totalled, while
`except KeyError` prints `'prcie'` and puts the typo on the screen. The near-miss worth
knowing is that a bare `except:` is *not* the same as `except Exception:` — it is wider,
and the two extra classes it catches are the ones asking the program to stop.
""",
                    },
                    {
                        "q": "`golf.drive(120)` is called on a `Car`. What is `self` bound to inside `drive`?",
                        "opts": [
                            "`Car`, the class in whose body the method was written",
                            "The module the method was defined in",
                            "`golf`, because the dot passes the receiver as the first argument",
                            "Nothing yet — `self` is a convention, bound by the first assignment",
                        ],
                        "a": 2,
                        "why": r"""
`golf.drive(120)` becomes `Car.drive(golf, 120)`, and both spellings run in the reading's
first example with the same result. A method is an ordinary function stored on the class;
the dot is what supplies the object in front of it as the first argument. So `self` is one
particular car, and `self.km += distance` moves that car's odometer and no other's. The
tempting answer is the class, because that is where the `def` is written and where
`wheels = 4` lives — but a class attribute is reached *through* `self` by falling back to
the class when the instance has no such name, which is a lookup rule rather than a
binding, and module 3 takes it apart.
""",
                    },
                    {
                        "q": "A `with open(path, \"w\")` block writes one line and then raises. What has become of that line?",
                        "opts": [
                            "It was flushed and the file closed on the way out, so it reached the disk",
                            "It is lost: the block did not finish, so the buffer was never written",
                            "It is rolled back: a block that raises undoes the writes it had already made",
                            "It reaches the disk only if the exception is caught outside the block",
                        ],
                        "a": 0,
                        "why": r"""
`with` guarantees cleanup — the same guarantee, and the same reason, as `finally`. On the
way out of the block, for any reason at all, Python calls the file's `__exit__`, which
flushes the buffer and closes the handle; the exception then carries on travelling. The
reading's example proves both halves: the `ValueError` is caught outside, `f.closed` is
`True`, and reopening the path shows the line. The tempting answer is a rollback, because
a failed database transaction does undo its writes — a file has no such notion, and a
half-written file is a perfectly ordinary outcome. Nor does anything depend on whether the
exception is caught later: `__exit__` has already run by the time any outer handler sees
it.
""",
                    },
                    {
                        "q": "What does `json.dumps(data)` do?",
                        "opts": [
                            "Writes `data` to a file, taking the name from the object",
                            "Returns `data` as a JSON string, leaving files to `json.dump`",
                            "Parses a JSON string and returns the object inside it",
                            "Prints `data` to the console, indented so that a human can read it",
                        ],
                        "a": 1,
                        "why": r"""
`dumps` is dump-to-string; `json.dump`, without the `s`, takes an open file as its second
argument and writes to it. The mirror pair is `loads` for a string and `load` for a file,
so the `s` is the only thing separating four names that otherwise look interchangeable.
The parsing answer is the tempting one, because `dumps` and `loads` are used a line apart
in most round-trip code and the direction is easy to invert — remember it as *dump out,
load in*. And `indent=2` only shapes the string that comes back: it is still a `str`, and
nothing has been printed or saved until you do it.
""",
                    },
                    {
                        "q": "When is `raise ValueError(\"too big\")` the right move?",
                        "opts": [
                            "When a function is handed input it cannot turn into a sensible answer",
                            "When you want a warning recorded without interrupting anything",
                            "When you need to leave a loop early from inside a helper",
                            "When the error should be reported to whoever happens to be watching the console",
                        ],
                        "a": 0,
                        "why": r"""
Refusing loudly beats returning nonsense — the caller can catch it and decide, and cannot
mistake the refusal for an answer. The reading's `withdraw` that returns `-1` makes the
alternative concrete: the caller stores the refusal as a balance and the books go out by
41 kr with nothing on screen to say so. Printing is the tempting answer, and it is the
same mistake in a friendlier coat: the function has still returned something, still
returned it to code that cannot tell refusal from success, and has now also decided that
this program has a console worth printing to. Raising leaves both decisions where they
belong — with the caller.
""",
                    },
                ],
            }],
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
            "lab": [{
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
            }, {
                "title": "A bank account that says no",
                "runtime": "python",
                "minutes": 16,
                "brief": r'''
`Vector2D` refused a *write*. This one refuses a *request*: an account that would
rather raise than hand back a number nobody can act on.

## `BankAccount(owner, balance=0)`

Stores `owner` and `balance` as attributes. `balance` defaults to `0`.

- `deposit(amount)` adds to the balance, and raises `ValueError` if `amount` is
  zero or negative.
- `withdraw(amount)` subtracts from the balance, and raises `ValueError` if
  `amount` is zero or negative, **or** larger than the balance.
- A refused call must leave the balance exactly where it was. Validate first,
  then change state — never the other way round.
- `str(account)` gives the owner, a colon, the balance to two decimals, and ` kr`:

```text
str(BankAccount("Ada", 120))  ->  "Ada: 120.00 kr"
```

## `safe_withdraw(account, amount)`

The boundary function: it tries the withdrawal and answers `True` or `False`
rather than letting the exception escape.

```text
safe_withdraw(acc, 40)    ->  True,  and the balance moves
safe_withdraw(acc, 5000)  ->  False, and the balance does not
```

Catch `ValueError` specifically. A bare `except:` would also swallow the
`AttributeError` you get from a typo in `account.withdrwa`, and you would spend
an afternoon looking for a bug the computer had already found.
''',
                "files": [{"name": "main.py", "content": r'''
class BankAccount:
    def __init__(self, owner, balance=0):
        pass

    def deposit(self, amount):
        pass

    def withdraw(self, amount):
        pass

    def __str__(self):
        pass


def safe_withdraw(account, amount):
    """Return True if the withdrawal succeeded, False if it was refused."""
    pass


acc = BankAccount("Ada", 100)
acc.deposit(50)
print(acc)
print(safe_withdraw(acc, 500))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

    def __str__(self):
        return f"{self.owner}: {self.balance:.2f} kr"


def safe_withdraw(account, amount):
    """Return True if the withdrawal succeeded, False if it was refused."""
    try:
        account.withdraw(amount)
        return True
    except ValueError:
        return False


acc = BankAccount("Ada", 100)
acc.deposit(50)
print(acc)
print(safe_withdraw(acc, 500))
'''}],
                "hints": [
                    "`__init__` only stores what it was given: `self.owner = owner` and `self.balance = balance`.",
                    "Validate before you mutate. `if amount <= 0: raise ValueError(\"...\")` comes first, so a refused call cannot have moved the balance already.",
                    "`__str__` *returns* the string, it does not print it: `return f\"{self.owner}: {self.balance:.2f} kr\"`. The `:.2f` is what turns 120 into `120.00`.",
                    "`safe_withdraw` wraps the call in `try` / `except ValueError` and returns `True` from the try body, `False` from the handler.",
                ],
                "tests": [
                    {"name": "Stores owner and balance (with default)", "code": r'''
_a = BankAccount("Ada", 100)
assert _a.owner == "Ada" and _a.balance == 100, "Store owner and balance in __init__"
assert BankAccount("Bo").balance == 0, "balance should default to 0"
'''},
                    {"name": "Deposits add up", "code": r'''
_a = BankAccount("Ada", 100)
_a.deposit(50)
assert _a.balance == 150, f"After depositing 50 the balance is {_a.balance!r}"
'''},
                    {"name": "Refuses bad deposits", "code": r'''
_a = BankAccount("Ada", 100)
for _bad in (0, -5):
    try:
        _a.deposit(_bad)
        assert False, f"deposit({_bad}) should raise ValueError"
    except ValueError:
        pass
assert _a.balance == 100, "A refused deposit must not change the balance"
'''},
                    {"name": "Refuses overdrafts and bad withdrawals", "code": r'''
_a = BankAccount("Ada", 100)
for _bad in (500, 0, -1):
    try:
        _a.withdraw(_bad)
        assert False, f"withdraw({_bad}) should raise ValueError"
    except ValueError:
        pass
assert _a.balance == 100, "A refused withdrawal must not change the balance"
'''},
                    {"name": "str() formats the account", "code": r'''
_s = str(BankAccount("Ada", 120))
assert _s == "Ada: 120.00 kr", f"Got {_s!r}, expected: Ada: 120.00 kr"
'''},
                    {"name": "safe_withdraw returns True/False", "code": r'''
_a = BankAccount("Ada", 100)
assert safe_withdraw(_a, 40) is True and _a.balance == 60, "A valid withdrawal returns True"
assert safe_withdraw(_a, 500) is False and _a.balance == 60, \
    "A refused withdrawal returns False and changes nothing"
'''},
                ],
            }],
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
            "read": [
                {
                    "title": "The call that never asks which: abstract bases and dispatch",
                    "minutes": 15,
                    "body": r'''
A drawing arrives as a list of shapes — a circle here, a rectangle there, a triangle in
one corner — and the job is to total their areas. The first version anyone writes asks
each shape what it is before doing anything:

```python
import math


def total_area(shapes):
    total = 0.0
    for kind, dims in shapes:
        if kind == "circle":
            total += math.pi * dims[0] ** 2
        elif kind == "rectangle":
            total += dims[0] * dims[1]
        elif kind == "triangle":
            a, b, c = dims
            s = (a + b + c) / 2
            total += math.sqrt(s * (s - a) * (s - b) * (s - c))
    return total


drawing = [("circle", (1,)), ("rectangle", (3, 4)), ("triangle", (3, 4, 5))]
print(round(total_area(drawing), 4))     # 21.1416
```

It works, and it is already in trouble. A `total_perimeter` needs the same chain of
`elif`s over again. So does anything that prints a description. Add a square and there
are three chains to extend; add a hexagon to two of them and forget the third, and the
failure is not an error but a total that is quietly short, because an unrecognised kind
falls off the end of the chain and contributes nothing. The chain is a decision being
made in the wrong place. The *caller* is deciding how a circle's area is computed, when
the circle is the one that knows.

Move the decision onto the object. Give each kind of shape an `area()` method of its
own, and the loop stops asking:

```python
import math


class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2


class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


def total_area(shapes):
    return sum(shape.area() for shape in shapes)


print(round(total_area([Circle(1), Rectangle(3, 4)]), 4))   # 15.1416
```

`total_area` no longer mentions a circle. It names the *operation*, and each object
supplies the *code*: `shape.area()` is looked up on the object in front of it at the
moment of the call, and whichever class that object belongs to answers. That is what
polymorphic dispatch means. A hexagon is now a new class with an `area`, and `total_area`
does not change — it never knew about the other shapes either. This is the lab, *An
abstract Shape hierarchy*: a geometry kernel whose helpers touch nothing but `.area()`
and never ask which shape they are holding.

## Writing the promise down

The version above has a hole. Nothing says a shape *must* have an `area`. Write a `Blob`
with a `perimeter` and no `area`, put it in the list, and the failure arrives inside
`total_area` as an `AttributeError`, at a point in the program far from the class that
forgot. The promise *every shape can be asked for its area* exists only in the author's
head.

`abc` is how the promise gets written down and checked. Inherit from `ABC`, mark the
methods every subclass must supply with `@abstractmethod`, and the check runs at the one
moment it can help — when somebody tries to build an object:

```python
# raises TypeError
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self):
        """Enclosed area."""

    @abstractmethod
    def perimeter(self):
        """Length of the boundary."""


class Blob(Shape):
    def area(self):
        return 1.0


print(sorted(Shape.__abstractmethods__))    # ['area', 'perimeter']
print(sorted(Blob.__abstractmethods__))     # ['perimeter']
Blob()
```

The timing is the point. When the `class` statement runs, `ABCMeta` collects the names
still marked abstract into `__abstractmethods__`; defining `Blob` is legal, and has to
be, because that is how one abstract class extends another. Instantiation is what gets
refused, with a `TypeError` naming the class and the method still missing. The abstract
body never runs at all — nothing calls it unless a subclass does so deliberately with
`super()` — which is why leaving it as a docstring and nothing else is the honest way to
write one. People expect a `pass` body to run and return `None` when a subclass forgets;
it never gets the chance.

## The template method: written once, dispatched later

Once the base can rely on `area()` and `perimeter()` existing, it can build things out of
them. `describe()` is one line in `Shape`, and every subclass gets it for free:

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    def __init__(self):
        self.name = type(self).__name__

    @abstractmethod
    def area(self):
        """Enclosed area."""

    @abstractmethod
    def perimeter(self):
        """Length of the boundary."""

    def describe(self):
        return f"{self.name}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Rectangle(Shape):
    def __init__(self, width, height):
        super().__init__()
        self.width = float(width)
        self.height = float(height)

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)


print(Square(2).describe())                     # Square: area=4.00, perimeter=8.00
print([c.__name__ for c in Square.__mro__])     # ['Square', 'Rectangle', 'Shape', 'ABC', 'object']
```

Trace `Square(2).describe()`. `describe` is found on `Shape`, but the `self` it receives
is a `Square`, and `self.area` is looked up on *that object*, not in the file where
`describe` was written. The search walks the method resolution order printed on the last
line: `Square` has no `area`, `Rectangle` does, and the walk stops there — the abstract
`Shape.area` is never reached. Nothing is copied onto `Square` when the class is made;
there is one `Rectangle.area`, found by walking a list. This late binding is the whole
mechanism of the template method: the base fixes the shape of the algorithm, and each
subclass supplies the steps.

The same trace explains `self.name`. `Shape.__init__` runs with a `Square` as `self`, so
`type(self)` is `Square` and `type(self).__name__` is `'Square'`, even though every line
involved lives in `Shape`. Hard-code `"Shape"` there instead and every subclass claims to
be a `Shape` — a wrong `repr` that no test thinks to check. `Shape.__name__` is the same
mistake spelled differently: it is the constant string `'Shape'`, evaluated identically
for every subclass.

## `super()` is not a synonym for "my parent"

`Square.__init__` above says `super().__init__(side, side)`. It could have said
`Rectangle.__init__(self, side, side)`, and with one base the two lines call the
identical function. The difference is what `super()` *means*: not *my parent*, but *the
class after me in the MRO of the object being built*. With one base those coincide. Give
a class two bases and they stop coinciding:

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
print([c.__name__ for c in Both.__mro__])    # ['Both', 'Left', 'Right', 'Base', 'object']
print(trace)                                 # ['Both', 'Left', 'Right', 'Base']
```

`Left`'s `super()` goes *sideways* to `Right`, because `Right` is what follows `Left` in
`Both`'s MRO, and `Base` runs exactly once however many arrows point at it in the
diagram. Change `Left` to call `Base.__init__(self)` by name and `Right` is skipped
entirely: the trace comes out three entries long, and nothing raises. That is the
mistake, and it is tempting because naming the parent is explicit and works on the day
it is written. It stops working the day somebody inherits from your class and one other,
which is a day you do not get to choose. The module's numeric exercise asks for that
count; the mechanism above is where the number comes from.

One more thing the lab's `__init__` methods do: validate *before* calling
`super().__init__()`, so a rejected shape is never half-built. A `Circle(-1)` should
raise `ValueError` before any state exists.

## Is-a is about promises, not vocabulary

Inheritance makes a promise: anywhere the base is expected, the subclass will do. That is
Liskov's substitution principle, and it is a statement about behaviour, not about the
English. The dictionary says a square is a rectangle. Whether the *type* `Square` can be
a subtype of the *type* `Rectangle` depends on what `Rectangle` promises:

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)

    def __setattr__(self, name, value):
        # a square stays square: setting either side sets both
        object.__setattr__(self, "width", value)
        object.__setattr__(self, "height", value)


def widen(rect, extra):
    """Make it wider. The height must not move."""
    before = rect.height
    rect.width += extra
    return rect.height == before


print(widen(Rectangle(3, 4), 2))    # True
print(widen(Square(3), 2))          # False
```

`widen` was written against `Rectangle`, never mentions `Square`, and breaks the moment
it is handed one. This `Rectangle` promises two dimensions that move independently, and
a `Square` that stays square cannot keep that promise. The lab sidesteps the problem
rather than solving it: its dimensions are fixed at construction, so the promise is never
made, and `Square(Rectangle)` is honest — a square answers `area`, `perimeter` and
`describe` exactly as a rectangle would. The other way out is to drop the inheritance and
let a `Square` *hold* a `Rectangle`, which is the subject of the next module.

The same test sorts is-a from has-a. A `Car` and its `Engine`: can a function that asked
for an engine be handed a car and keep working? No — so the car *has* an engine. A
`Circle` and `Shape`: can `total_area` be handed a circle? Yes, and that is the entire
content of the relationship. Shared code is not the test; the ability to stand in is.

## Two questions, two tools

`isinstance(s, Shape)` asks a type question and is true for every subclass — the right
guard for an input. `type(self).__name__` asks for the dynamic class and is the right
thing for display. Reaching for `type(s) == Circle` excludes subclasses, and reaching for
`isinstance` inside `total_area` rebuilds the `elif` chain this reading started by
removing. The lab's helpers are meant to contain neither.

## Heron's formula, and where it stops

The lab's `Triangle` computes its perimeter as $a + b + c$ and its area with Heron's
formula. With $s = (a + b + c) / 2$,

$$A = \sqrt{s(s-a)(s-b)(s-c)}.$$

Check it on the 3-4-5 triangle before trusting it: $s = 6$, so
$A = \sqrt{6 \cdot 3 \cdot 2 \cdot 1} = \sqrt{36} = 6$, and the right-angle formula
$\frac{1}{2} \cdot 3 \cdot 4$ gives 6 as well. Now feed it sides that make no triangle.
With $1, 2, 3$: $s = 3$ and $s - c = 0$, so the radicand is zero and the area is 0.0 — a
"triangle" that is a line segment, and no error at all. With $1, 2, 10$: $s = 6.5$,
$s - c = -3.5$, the radicand is negative, and `math.sqrt` raises `ValueError: math domain
error` — the right exception with the wrong message, and only when `area()` is called,
not when the bad triangle was built.

So the check belongs in `__init__`, and it is the triangle inequality: every two sides
must together exceed the third. That reads as three comparisons. Sort the sides and one
is enough, because if the two *shortest* sides together exceed the longest, then either
other pairing includes the longest side, which on its own is at least as long as
whichever side it is being compared against. The lab's solution does exactly this:

```python
def check_triangle(a, b, c):
    sides = sorted([float(a), float(b), float(c)])
    if sides[0] + sides[1] <= sides[2]:
        raise ValueError("sides violate the triangle inequality")
    return sides


print(check_triangle(3, 4, 5))       # [3.0, 4.0, 5.0]
for bad in [(1, 2, 3), (1, 2, 10), (10, 1, 2)]:
    try:
        check_triangle(*bad)
    except ValueError as e:
        print(bad, "->", e)
```

The `<=` rather than `<` is what refuses the degenerate `1, 2, 3` as well as the
impossible `1, 2, 10`, and sorting is what makes `10, 1, 2` fail the same way regardless
of the order the sides were given in.

Where even this stops holding is the floats underneath it. `0.1 + 0.2 <= 0.3` is `False`
in Python, because the left side rounds to `0.30000000000000004`, so a triangle with
sides 0.1, 0.2 and 0.3 passes the check and reports a tiny positive area rather than
being refused. The check is exact for integers and for floats that happen to be exact;
for measured data a tolerance belongs in it. Hold that in mind, and then build the
hierarchy: an abstract `Shape`, four concrete subclasses, and three helpers that never
ask which one they hold.
''',
                },
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
            "read": [
                {
                    "title": "The balance nobody can reach: properties, and where an attribute lives",
                    "minutes": 14,
                    "body": r'''
Here is an account written the way a first draft is written, with a plain attribute for
the balance:

```python
class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount


ada = Account("Ada", 100)
ada.balance -= 250          # some line, in some other file, months later
print(ada.balance)          # -150
```

`withdraw` checks. The line that broke the account did not go through `withdraw`.
Nothing raised, nothing looked wrong at the moment it happened, and the negative number
surfaces on a statement weeks later, three files away from the write that caused it. The
fact *a balance is never negative* is an **invariant** — something that must be true of
every valid account at every moment — and with a plain attribute an invariant is only as
safe as every line in the program that assigns to it.

The Java reflex is to hide the attribute and write `get_balance()` and `set_balance()`,
and then every caller in the program changes from `ada.balance` to `ada.get_balance()`.
Python's answer keeps the caller's syntax and changes what happens underneath: a
property. The lab, *A bank account that defends itself*, builds an `Account` whose
balance can be read by anyone and written by nobody, whose owner is validated on every
assignment, and whose class-level state stays where it was put.

## What a property is

Start from how `ada.balance` is resolved. Before Python looks in the instance's own
dictionary, it looks on the *class* for something called `balance` that is a data
descriptor — an object with `__get__` and `__set__` methods. A `property` is exactly
that. If one is found, its getter runs and the result is the value of the expression;
the instance dictionary is never consulted:

```python
class Account:
    def __init__(self, owner, balance):
        self._owner = owner
        self._balance = float(balance)

    @property
    def balance(self):
        return self._balance


ada = Account("Ada", 100)
print(ada.balance)                       # 100.0
print(type(Account.balance).__name__)    # property
print(ada.__dict__)                      # {'_owner': 'Ada', '_balance': 100.0}
```

The caller writes `ada.balance` as before, and a method runs. Look at the dictionary:
there is `_balance` and there is no `balance`. There is only one thing called `balance`
anywhere, and it is the property on the class. The leading underscore is not a note to
the reader; it is what makes the storage a *different name* from the property, and that
difference is load-bearing.

Get it wrong and the failure is immediate. A getter written `return self.balance` reads
the property it is the getter for, which calls the getter, which reads the property:

```python
# raises RecursionError
class Account:
    def __init__(self, balance):
        self._balance = float(balance)

    @property
    def balance(self):
        return self.balance      # the property, calling itself


Account(100).balance
```

It is a tempting line to write because `balance` is the name you are thinking about, and
because in the plain-attribute version it was correct. The setter version of the same
mistake, `self.owner = value` inside `@owner.setter`, recurses the same way.

## Read-only, for free

Now assign to the property. The descriptor is found on the class on writes as well as
reads, so the assignment reaches the property, and a property with no setter refuses:

```python
# raises AttributeError
class Account:
    def __init__(self, balance):
        self._balance = float(balance)

    @property
    def balance(self):
        return self._balance


ada = Account(100)
ada.balance = 1_000_000
```

No code of your own, and the balance is read-only. The same wall is why
`self.balance = 100` inside `__init__` would fail too: it is the same assignment, hitting
the same property with no setter. The real number has to live under `_balance`, and
methods such as `deposit` and `withdraw` write to `_balance` directly, after checking.
This is what encapsulation buys: the invariant is checked in the two or three methods
that are allowed to change the number, and nowhere else can.

## A setter that validates every write

`owner` is a property that *can* be written, with a rule: a non-empty string, stored
stripped. `@property` produced an object holding the getter; `@owner.setter` takes a
second function and returns a *new* property carrying the same getter plus that function
as the write path, and rebinding the name `owner` to it is why both functions must share
the name:

```python
class Account:
    def __init__(self, owner, balance=0.0):
        self.owner = owner            # goes through the setter below
        if balance < 0:
            raise ValueError("opening balance cannot be negative")
        self._balance = float(balance)

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("owner must be a non-empty string")
        self._owner = value.strip()


ada = Account("  Ada  ", 100)
print(repr(ada.owner))               # 'Ada'
ada.owner = " Grace "
print(repr(ada.owner))               # 'Grace'
for bad in ["", "   ", None, 42]:
    try:
        ada.owner = bad
    except ValueError as e:
        print(repr(bad), "->", e)
print(repr(ada.owner))               # still 'Grace'
try:
    Account("", 10)
except ValueError as e:
    print("Account('', 10) ->", e)
```

Two things to notice. `self.owner = owner` in `__init__` is an ordinary assignment, so it
goes through the setter: the validation is written once and runs at construction *and*
on every later write. And every rejected write left the old value in place, because the
check comes before the store. A setter that assigns first and validates after has
already broken the invariant by the time it raises.

## Where an attribute lives

Properties aside, attribute lookup follows one rule, and a great deal of confusion about
classes comes from not holding it steadily. `obj.attr` looks in the instance's dictionary
first, then in the class's dictionary, then in each base along the MRO, and raises
`AttributeError` if nobody has it. Assignment through `obj.attr = value` *always* writes
the instance's dictionary. Watch both halves:

```python
class Account:
    interest_rate = 0.02          # shared default, on the class

    def __init__(self, owner):
        self.owner = owner


ada = Account("Ada")
bo = Account("Bo")
print(ada.interest_rate, "interest_rate" in ada.__dict__)    # 0.02 False
ada.interest_rate = 0.10
print(ada.__dict__)                                          # {'owner': 'Ada', 'interest_rate': 0.1}
print(ada.interest_rate, bo.interest_rate)                   # 0.1 0.02
Account.interest_rate = 0.05
print(ada.interest_rate, bo.interest_rate)                   # 0.1 0.05
del ada.interest_rate
print(ada.interest_rate)                                     # 0.05
```

The first read finds nothing on `ada` and falls through to the class. The assignment
creates an `interest_rate` in `ada`'s own dictionary, which from then on *shadows* the
class value for her alone; `bo` still falls through. Changing the class value changes
what `bo` sees and not what `ada` sees. Deleting the shadow makes the class value visible
again — which is the proof that nothing was ever overwritten. There were two attributes
with one name in two dictionaries, and the lookup rule chose between them. The module's
numeric exercise turns this into a question about two bonuses; the answer comes from
running the rule once per account.

## The counter that never moves

Now the trap. A class wants to count how many accounts have been made, so it keeps
`count = 0` on the class and increments it in `__init__`:

```python
class Account:
    count = 0

    def __init__(self, owner):
        self.owner = owner
        self.count += 1          # the bug


for name in ("Ada", "Bo", "Cy"):
    acct = Account(name)
print(Account.count)             # 0
print(acct.__dict__)             # {'owner': 'Cy', 'count': 1}
```

`self.count += 1` is `self.count = self.count + 1`, and the two halves go to different
places. The read finds nothing on the instance and falls through to the class, getting
`0`. The write, like every write through `self`, lands on the instance. So each account
ends up with a private `count` of `1`, the class tally never moves, nothing raises, and a
test that checks `acct.count` passes. It is tempting because it reads as *increment my
count*, and because for a number that belonged to the instance it would be right. The fix
names the class: `Account.count += 1`, or `type(self).count += 1`.

The mirror-image trap is a mutable value on the class. Put `history = []` in the class
body and let `__init__` leave it alone. `self.history.append(...)` is not an assignment
— no name is rebound — so nothing is shadowed, every instance falls through to the same
list, and two accounts share one history. Per-instance state has to be *created* per
instance, which is the whole job of `self.history = []` in `__init__`. The rule that
sorts the two cases: `+=` on a number is an assignment and writes the instance; `append`
on a list is a mutation and writes nothing.

## `cls`, and nothing at all

Two more kinds of method live on a class. A `@classmethod` receives the class it was
called *through* as `cls`, which makes it the right shape for an alternative constructor
and for writing shared state; a `@staticmethod` receives nothing and is a plain function
kept in the class because that is where it belongs:

```python
class Account:
    interest_rate = 0.02

    def __init__(self, owner, balance=0.0):
        self.owner = owner
        self._balance = float(balance)

    @classmethod
    def from_row(cls, row):
        owner, balance = row.split(",")
        return cls(owner.strip(), float(balance))

    @classmethod
    def set_interest_rate(cls, rate):
        if rate < 0:
            raise ValueError("rate cannot be negative")
        cls.interest_rate = rate

    @staticmethod
    def is_valid_amount(amount):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            return False
        return amount > 0


class Savings(Account):
    pass


s = Savings.from_row("Ada, 250")
print(type(s).__name__, s.owner, s._balance)          # Savings Ada 250.0
Account.set_interest_rate(0.05)
print(Account.interest_rate, s.interest_rate)           # 0.05 0.05
print(Account.is_valid_amount(5), Account.is_valid_amount(True), Account.is_valid_amount("5"))
```

`cls` is not pinned to the class where the method was written. Called as
`Savings.from_row(...)`, `cls` is `Savings`, so `return cls(...)` builds a `Savings` with
no `if` and no extra code — a subclass inherits a working constructor.
`set_interest_rate` writes `cls.interest_rate`, which is the class's dictionary, so the
write is a real change to the shared default rather than a shadow on one instance. Both
kinds can be called without an instance, so that is not the distinction between them;
what a `classmethod` has that a `staticmethod` lacks is the class.

The last line prints `True False False`, and the middle one matters: `isinstance(True,
int)` is `True` because `bool` is a subclass of `int`, so a predicate that forgets to
rule it out accepts `deposit(True)` as a deposit of one unit. The lab's tests include
exactly that argument.

## Where encapsulation stops

Python has no private. `ada._balance = -5` works, and the underscore is a request to the
reader rather than a lock; a double underscore mangles the name to `_Account__balance`,
which guards against accidental collision in subclasses and against nothing else. A
property guards writes *to the name*. It does not guard what the caller does with a
mutable value it returns: `ada.history` in the lab is a plain list, and
`ada.history.clear()` goes through no setter, because nothing was assigned. If a history
must be tamper-proof, the getter returns a copy or a tuple, and the class pays for that
on every read.

That cost is the other boundary. A property runs code on every access, and readers
assume attribute access is cheap; a property that opens a file or scans a list each time
it is read is a surprise waiting inside a loop. Keep properties for reads that cost what
an attribute costs, and for writes that need checking. Then build the account: two
properties, one of them read-only, a class counter that moves, and a history that
belongs to one account alone.
''',
                },
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
            "read": [
                {
                    "title": "It has a list; it is not one: a playlist Python already understands",
                    "minutes": 14,
                    "body": r'''
A playlist ought to work with the words Python already has. `len(jazz)` should count its
tracks, `for track in jazz` should walk them, `"So What" in jazz` should say whether a
title is there, `jazz[0:2]` should be the first two, and `jazz + blues` should be both.
The fastest way to get all of that is to inherit it:

```python
class Track:
    def __init__(self, title, seconds):
        self.title = title
        self.seconds = seconds


class Playlist(list):
    def add(self, track):
        if not isinstance(track, Track):
            raise TypeError("only Track objects can be added")
        self.append(track)
        return self


jazz = Playlist()
jazz.add(Track("So What", 545))
jazz.extend([1, 2, 3])          # nothing stops this
jazz[0] = "not a track"         # nor this
print(len(jazz), jazz)          # 4 ['not a track', 1, 2, 3]
```

Every method a list has, the playlist has, including the ones `add` was written to
prevent. Inheriting from `list` is a promise that a `Playlist` can be used anywhere a
list can — `extend`, `insert`, `sort`, slice assignment, `pop` — and a container that
wants to enforce a rule about its contents cannot keep that promise. Trying to intercept
the leaks one by one does not work either, because the built-in's own methods do not
call your overrides:

```python
class Guarded(list):
    def append(self, item):
        raise TypeError("use add()")


g = Guarded()
g.extend([1, 2])
g += [3]
print(g)          # [1, 2, 3]: three items, and append was never consulted
```

So the lab, *A Playlist that behaves like a sequence*, forbids the shortcut: neither
class may subclass `list`. A `Playlist` *has* a list, kept in a private attribute, and it
forwards to that list exactly the operations it means to support. That is composition,
and the forwarding is delegation. The rest of this reading is about how each piece of
Python's vocabulary reaches a method you wrote, because once you can see that, the
container writes itself.

## `len(p)`, and what truth falls back to

`len(p)` is not magic. Python evaluates it as `type(p).__len__(p)` and insists on a
non-negative integer coming back. One line of delegation buys it:

```python
class Track:
    def __init__(self, title, seconds):
        self.title = title
        self.seconds = seconds


class Playlist:
    def __init__(self, name):
        self.name = name
        self._tracks = []

    def add(self, track):
        if not isinstance(track, Track):
            raise TypeError("only Track objects can be added")
        self._tracks.append(track)
        return self

    def __len__(self):
        return len(self._tracks)


jazz = Playlist("Jazz")
print(len(jazz), bool(jazz))                 # 0 False
jazz.add(Track("So What", 545)).add(Track("Take Five", 324))
print(len(jazz), bool(jazz))                 # 2 True
```

The second column is something you did not write. `bool(p)` asks for `__bool__` first,
then for `__len__`, and only when neither exists assumes `True`. So the moment a
container defines `__len__`, an empty one becomes falsy and `if playlist:` means what a
reader expects. The corner to know about: a class where zero length is a perfectly
ordinary state — a queue that happens to be empty right now — goes falsy whether or not
you meant it to, and that is the moment to write `__bool__` and say so explicitly.

`add` returning `self` is what lets the calls chain on the second-to-last line. It costs
nothing, and the lab's tests rely on it.

## `for t in p`, and the difference between iterable and iterator

A `for` loop begins by calling `iter(p)`, which calls `type(p).__iter__(p)`, and then it
calls `next()` on whatever came back until `StopIteration`. That splits the world into
two jobs. An *iterable* is something you can ask for an iterator; an *iterator* is the
thing that produces the items, one per `__next__`. A list is iterable — it has
`__iter__` — and it is not an iterator, because it has no `__next__`. `iter()` checks:

```python
# raises TypeError
class Playlist:
    def __init__(self):
        self._tracks = ["So What", "Take Five"]

    def __iter__(self):
        return self._tracks        # a list: iterable, not an iterator


for title in Playlist():
    print(title)
```

The message is `iter() returned non-iterator of type 'list'`, and this is the mistake
people make here, because the reasoning behind it is nearly right: a list is iterable, so
surely handing one back is enough. It is not, because the loop does not want something it
*could* iterate; it wants the thing that has `__next__`. Ask the list for its iterator
and return that:

```python
class Playlist:
    def __init__(self):
        self._tracks = ["So What", "Take Five", "Blue Train"]

    def __iter__(self):
        return iter(self._tracks)


p = Playlist()
it = iter(p)
print(type(it).__name__)             # list_iterator
print(next(it), next(it))            # So What Take Five
for a in p:
    for b in p:
        if a < b:
            print(a, "<", b)
```

`iter(self._tracks)` produces a fresh `list_iterator` every time it is called, and that
is why the nested loop at the end works: each `for` asked for its own iterator, and the
inner one does not disturb the outer one's position. An `__iter__` that handed out one
shared iterator would let the inner loop exhaust it and the outer loop stop after a
single pass. A generator — `yield from self._tracks` — is the other correct spelling,
and it returns a fresh iterator for the same reason.

## `p[key]`, and the one argument it always gets

Subscription passes exactly one object to `__getitem__`, whatever was written between the
brackets. For `p[1]` that object is `1`. For `p[0:2]` it is not two arguments and not a
tuple; it is a `slice`:

```python
class Show:
    def __getitem__(self, key):
        return key


s = Show()
print(s[1])            # 1
print(s[-1])           # -1
print(s[0:2])          # slice(0, 2, None)
print(s[::2])          # slice(None, None, 2)
```

The colon syntax is packaged into a `slice` carrying `start`, `stop` and `step`, with
`None` for whatever was left out. That is why `__getitem__` branches on
`isinstance(key, slice)`, and why the branch is short: a list already knows what to do
with either kind of key, so `self._tracks[key]` handles the integer case — negative
indices included, and an `IndexError` for an index off the end, both for free.

What the slice branch must *not* do is fall through to the list. `self._tracks[0:2]` is
a plain list: no `name`, no `by_artist`, no `total_duration`. Nothing raises, and the
caller has quietly been handed something less capable than what they sliced. Build a new
`Playlist` instead, and the type stays closed under its own operations —
`jazz[0:2].total_seconds()` reads naturally, and a function that takes a playlist can be
handed a slice of one:

```python
class Track:
    def __init__(self, title, seconds):
        self.title = title
        self.seconds = seconds

    def __repr__(self):
        return f"Track({self.title!r}, {self.seconds})"


class Playlist:
    def __init__(self, name):
        self.name = name
        self._tracks = []

    def add(self, track):
        self._tracks.append(track)
        return self

    def __len__(self):
        return len(self._tracks)

    def __getitem__(self, key):
        if isinstance(key, slice):
            sliced = Playlist(self.name)
            for track in self._tracks[key]:
                sliced.add(track)
            return sliced
        return self._tracks[key]

    def total_seconds(self):
        return sum(t.seconds for t in self._tracks)


jazz = Playlist("Jazz")
jazz.add(Track("Blue Train", 617)).add(Track("So What", 545)).add(Track("Take Five", 324))
half = jazz[0:2]
print(type(half).__name__, half.name, len(half), half.total_seconds())   # Playlist Jazz 2 1162
print(jazz[-1])                        # Track('Take Five', 324)
print(half[0] is jazz[0])              # True
print(len(jazz))                       # 3
```

The last two lines say something about what a slice costs. `half[0] is jazz[0]` is
`True`: no `Track` was copied, both playlists refer to the same objects, and the slice is
a new *container* rather than new *contents*. And `jazz` still has three tracks, because
building a new container is what leaves the original alone. The module's numeric
exercise adds a concatenation on top of a slice and asks for the total; the answer
depends on seeing that the same track counted twice is the same object referenced twice.

## `x in p`, and the fallback that never complains

Python asks `__contains__` if it exists. If it does not, `in` falls back to iterating and
comparing each item with `==` until one matches or the items run out. The fallback means
`in` works the moment a class is iterable, and it also means the wrong thing works
silently:

```python
class Track:
    def __init__(self, title):
        self.title = title


class Playlist:
    def __init__(self):
        self._tracks = [Track("So What"), Track("Take Five")]

    def __iter__(self):
        return iter(self._tracks)


p = Playlist()
print("So What" in p)                        # False
print(any(t.title == "So What" for t in p))  # True
```

A title string compared against a `Track` with `==` is never equal, so the membership
test answers `False` and nobody is told. Writing `__contains__` is how a playlist comes
to accept a `Track` *or* a title, case-insensitively — and how it answers `False`, rather
than raising, for `42 in playlist`, because the lab asks for a container that is never
surprised by its operand.

## `p + q` produces a value

`__add__` follows the rule from the first module: it builds a new playlist named
`"A + B"` from both operands, leaves each operand untouched, and returns `NotImplemented`
for anything that is not a `Playlist`. The tempting mistake is
`self._tracks.extend(other._tracks)` followed by `return self`, which makes
`jazz + blues` an expression that *mutates* `jazz` and evaluates to the same object. An
expression that rewrites its own operands is the one thing `+` must never be, and the
lab checks both operands' lengths afterwards.

## Where delegation stops holding

Composition means the surface is exactly what you wrote and nothing more.
`sorted(playlist)` works, because it iterates; `playlist.sort()` does not exist, and that
is the point. But two things come through the protocols that you may not have meant.

The first is the old sequence protocol. A class with `__getitem__` and *no* `__iter__` is
still iterable: Python calls `__getitem__(0)`, `__getitem__(1)`, and so on until an
`IndexError`, and `in` falls back to the same walk. So forgetting `__iter__` on a
sequence-like class appears to work — right up to the day the class is given a
`__getitem__` that takes keys rather than positions, when every loop over it starts
raising `KeyError` at zero. Write `__iter__` and mean it.

The second is that delegation shares; it does not copy. `by_artist`, a slice, a
concatenation — every one of them holds references to the same `Track` objects as the
original, so a change to a track through one playlist is visible through all of them.
For the lab this is what you want; a track is one recording however many lists it sits
in. For a container of mutable things it is a decision to make on purpose.

The standard library has a middle path for the day the surface needs to be wider:
inherit from `collections.abc.Sequence`, supply `__len__` and `__getitem__`, and
`__iter__`, `__contains__`, `__reversed__`, `index` and `count` arrive as mixins written
in terms of the two you wrote. That is inheritance from an *interface* rather than from
a container — no storage comes with it, so the has-a relationship to the list underneath
is untouched. The lab keeps to the bare protocols so that you write each one once and see
what it does. `Track` first: a value, with the equality and hash rules from the first
module and a `duration` property that pads seconds to two digits. Then the container,
one dunder at a time.
''',
                },
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
            "lab": [{
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
            }, {
                "title": "Save and load with JSON",
                "runtime": "python",
                "minutes": 12,
                "brief": r'''
A `Playlist` that vanishes when the program ends is a demonstration, not a
program. Persistence is the last piece, and for a dictionary of plain values it
is two functions.

## What to write

**`save_scores(path, scores)`** writes the dictionary to the file at `path` as
JSON.

**`load_scores(path)`** reads that file and returns the dictionary. If the file
does not exist, it returns an empty dictionary rather than crashing.

```text
save_scores("scores.json", {"ada": 90})
load_scores("scores.json")     ->  {"ada": 90}
load_scores("nope.json")       ->  {}
```

## The two decisions

Use `json.dump` / `json.load` — the pair without the `s`, which take a *file
object* — inside a `with` block, so the file is closed whether the write
finishes or raises halfway through.

The missing file is the interesting half. Asking `os.path.exists(path)` first is
the wrong shape: the answer can be stale by the line after you get it, and it
does not help when the path exists but cannot be opened. Try the open and handle
the failure — `except FileNotFoundError`, not a bare `except:`, so a permission
error or a corrupt file still reaches you instead of being reported as "no
scores yet".
''',
                "files": [{"name": "main.py", "content": r'''
import json


def save_scores(path, scores):
    """Write the scores dict to path as JSON."""
    pass


def load_scores(path):
    """Read scores from path. Missing file -> {}."""
    pass


save_scores("scores.json", {"ada": 90, "linus": 75})
print(load_scores("scores.json"))
print(load_scores("does-not-exist.json"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import json


def save_scores(path, scores):
    """Write the scores dict to path as JSON."""
    with open(path, "w") as f:
        json.dump(scores, f)


def load_scores(path):
    """Read scores from path. Missing file -> {}."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


save_scores("scores.json", {"ada": 90, "linus": 75})
print(load_scores("scores.json"))
print(load_scores("does-not-exist.json"))
'''}],
                "hints": [
                    "Writing is one line inside a `with`: `with open(path, \"w\") as f: json.dump(scores, f)`. The `\"w\"` mode creates the file, or truncates it if it is already there.",
                    "`json.dump` takes the object *and* the file; `json.dumps` takes only the object and hands back a string. Passing the file to `dumps` is a `TypeError`.",
                    "Reading is `json.load(f)` — and the whole `with` goes inside `try` / `except FileNotFoundError`, whose handler returns `{}`.",
                ],
                "tests": [
                    {"name": "Round-trips a dict", "code": r'''
save_scores("t1.json", {"ada": 90, "linus": 75})
assert load_scores("t1.json") == {"ada": 90, "linus": 75}, \
    "load_scores should return exactly what save_scores wrote"
'''},
                    {"name": "Writes real JSON", "code": r'''
import json as _json
save_scores("t2.json", {"x": 1})
with open("t2.json") as _f:
    assert _json.load(_f) == {"x": 1}, "The file should contain plain JSON"
'''},
                    {"name": "Missing file gives {}", "code": r'''
assert load_scores("definitely-missing-42.json") == {}, \
    "A missing file should give {} — catch FileNotFoundError"
'''},
                    {"name": "Numbers stay numbers", "code": r'''
save_scores("t3.json", {"a": 1})
_v = load_scores("t3.json")["a"]
assert _v == 1 and isinstance(_v, int), "JSON keeps ints as ints — no str() conversions needed"
'''},
                    {"name": "A real error still gets through", "code": r'''
with open("t4.json", "w") as _f:
    _f.write("{not json at all")
try:
    load_scores("t4.json")
    assert False, "A corrupt file is not a missing file — it must not be swallowed"
except FileNotFoundError:
    assert False, "A corrupt file raises JSONDecodeError, not FileNotFoundError"
except ValueError:
    pass
'''},
                ],
            }, {
                "title": "Project: inventory manager",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Everything in the course so far, in one program: a small inventory system split
across two files. `inventory.py` holds the logic; `main.py` is a demo script that
uses it. The checks import from `inventory.py`, so that is where the classes go.

## `Item(name, price, quantity)`

A class with those three attributes and nothing else. It is a value the
`Inventory` holds — composition, not inheritance.

## `Inventory()`

The container. It keeps its items in `self.items`, a dict from name to `Item`,
and every method below is a few lines once that shape is in place.

- `add(item)` — adds the item. If an item of that name is already there,
  increase its quantity instead of storing a duplicate.
- `remove(name, quantity)` — reduces that item's quantity. Raise `KeyError` for
  an unknown name and `ValueError` when there is not enough stock; a refused
  call must change nothing. When the quantity reaches 0, drop the item entirely.
- `find(query)` — case-insensitive substring search on the name, returning a
  list of items sorted by name.
- `total_value()` — the sum of `price * quantity` over every item.
- `low_stock(threshold=5)` — the items with `quantity < threshold`, sorted by
  name.
- `save(path)` — writes every item to a JSON file.
- `Inventory.load(path)` — a **`@classmethod`** returning a new `Inventory` read
  from that file. `cls()` rather than `Inventory()`, so a subclass loads as
  itself.
- `report()` — a multi-line string, one line per item sorted by name, and a last
  line containing `Total:` and the total value.

## Suggested order

Get `Item`, `add` and `find` working first, then `remove`, then the two
calculations, then `save` / `load`, then `report`. The checks are ordered the
same way, so run them after every step and read the first failure.

Two things worth noticing as you go. An `Item` is not JSON, so `save` has to
turn each one into a plain dict and `load` has to turn it back — the same
`to_dict` / `from_dict` pair the capstone needs. And `add` already merges by
name, which means `load` gets the merging for free by calling `add` per row
rather than writing to `self.items` itself.
''',
                "files": [
                    {"name": "inventory.py", "content": r'''
import json


class Item:
    def __init__(self, name, price, quantity):
        pass


class Inventory:
    def __init__(self):
        self.items = {}   # name -> Item

    def add(self, item):
        pass

    def remove(self, name, quantity):
        pass

    def find(self, query):
        pass

    def total_value(self):
        pass

    def low_stock(self, threshold=5):
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
from inventory import Inventory, Item

inv = Inventory()
inv.add(Item("Wiper blades", 120.0, 8))
inv.add(Item("Jack", 899.0, 2))
inv.add(Item("Torch", 249.0, 4))

print(inv.report())
'''},
                ],
                "main": "main.py",
                "solution": [
                    {"name": "inventory.py", "content": r'''
import json


class Item:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity


class Inventory:
    def __init__(self):
        self.items = {}   # name -> Item

    def add(self, item):
        existing = self.items.get(item.name)
        if existing:
            existing.quantity += item.quantity
        else:
            self.items[item.name] = item

    def remove(self, name, quantity):
        if name not in self.items:
            raise KeyError(name)
        item = self.items[name]
        if quantity > item.quantity:
            raise ValueError(f"Only {item.quantity} {name} in stock")
        item.quantity -= quantity
        if item.quantity == 0:
            del self.items[name]

    def find(self, query):
        q = query.lower()
        hits = [item for item in self.items.values() if q in item.name.lower()]
        return sorted(hits, key=lambda item: item.name)

    def total_value(self):
        return sum(item.price * item.quantity for item in self.items.values())

    def low_stock(self, threshold=5):
        hits = [item for item in self.items.values() if item.quantity < threshold]
        return sorted(hits, key=lambda item: item.name)

    def save(self, path):
        data = [
            {"name": i.name, "price": i.price, "quantity": i.quantity}
            for i in self.items.values()
        ]
        with open(path, "w") as f:
            json.dump(data, f)

    @classmethod
    def load(cls, path):
        inv = cls()
        with open(path) as f:
            for row in json.load(f):
                inv.add(Item(row["name"], row["price"], row["quantity"]))
        return inv

    def report(self):
        lines = [f"{'Item':<20}{'Qty':>5}{'Price':>10}"]
        for item in sorted(self.items.values(), key=lambda i: i.name):
            lines.append(f"{item.name:<20}{item.quantity:>5}{item.price:>10.2f}")
        lines.append(f"Total: {self.total_value():.2f}")
        return "\n".join(lines)
'''},
                    {"name": "main.py", "content": r'''
from inventory import Inventory, Item

inv = Inventory()
inv.add(Item("Wiper blades", 120.0, 8))
inv.add(Item("Jack", 899.0, 2))
inv.add(Item("Torch", 249.0, 4))

print(inv.report())
inv.save("stock.json")
again = Inventory.load("stock.json")
print("Reloaded value:", again.total_value())
'''},
                ],
                "hints": [
                    "Keep `self.items` as a dict keyed by name. `add`, the duplicate merge and `remove` all become two or three lines once lookup by name is free.",
                    "`find`: `q = query.lower()`, then a comprehension over `self.items.values()` keeping the items where `q in item.name.lower()`, then `sorted(..., key=lambda i: i.name)`.",
                    "`remove` must validate both failures *before* subtracting, or a refused call will already have moved the stock: `raise KeyError(name)` for the unknown name, `raise ValueError(...)` when the quantity asked for is larger than the stock.",
                    "`save` builds a list of plain dicts and `json.dump`s it. `load` starts from `cls()` and calls `add()` on each row — the merging then comes free.",
                    "`report`: build a list of lines and join them with a newline. `f\"{item.name:<20}\"` pads left-aligned to 20 characters, `{item.price:>10.2f}` right-aligns to 10 with two decimals.",
                ],
                "tests": [
                    {"name": "Item stores its three attributes", "code": r'''
from inventory import Item
_i = Item("Torch", 249.0, 4)
assert _i.name == "Torch" and _i.price == 249.0 and _i.quantity == 4, \
    "Item should keep name, price and quantity"
'''},
                    {"name": "add() merges duplicates by name", "code": r'''
from inventory import Inventory, Item
_inv = Inventory()
_inv.add(Item("Torch", 249.0, 2))
_inv.add(Item("Torch", 249.0, 3))
_found = _inv.find("torch")
assert len(_found) == 1 and _found[0].quantity == 5, \
    "Adding the same name twice should merge quantities"
'''},
                    {"name": "find() is case-insensitive and sorted", "code": r'''
from inventory import Inventory, Item
_inv = Inventory()
_inv.add(Item("Wiper blades", 120.0, 8))
_inv.add(Item("Wheel jack", 899.0, 2))
_inv.add(Item("Torch", 249.0, 4))
_names = [i.name for i in _inv.find("w")]
assert _names == ["Wheel jack", "Wiper blades"], f"find('w') gave {_names!r}"
assert [i.name for i in _inv.find("TORCH")] == ["Torch"], "The search should ignore case"
'''},
                    {"name": "remove() reduces, drops at zero", "code": r'''
from inventory import Inventory, Item
_inv = Inventory()
_inv.add(Item("Torch", 249.0, 4))
_inv.remove("Torch", 3)
assert _inv.find("Torch")[0].quantity == 1, "remove should subtract the quantity"
_inv.remove("Torch", 1)
assert _inv.find("Torch") == [], "Quantity 0 should remove the item entirely"
'''},
                    {"name": "remove() raises the right errors", "code": r'''
from inventory import Inventory, Item
_inv = Inventory()
_inv.add(Item("Torch", 249.0, 2))
try:
    _inv.remove("Ghost", 1)
    assert False, "Unknown name should raise KeyError"
except KeyError:
    pass
try:
    _inv.remove("Torch", 5)
    assert False, "Removing more than the stock should raise ValueError"
except ValueError:
    pass
assert _inv.find("Torch")[0].quantity == 2, "A refused remove must change nothing"
'''},
                    {"name": "total_value() and low_stock()", "code": r'''
from inventory import Inventory, Item
_inv = Inventory()
_inv.add(Item("Wiper blades", 120.0, 8))
_inv.add(Item("Jack", 899.0, 2))
_inv.add(Item("Torch", 249.0, 4))
assert abs(_inv.total_value() - 3754.0) < 1e-6, \
    f"total_value gave {_inv.total_value()!r}, expected 3754.0"
assert [i.name for i in _inv.low_stock()] == ["Jack", "Torch"], "Default threshold 5, sorted by name"
assert [i.name for i in _inv.low_stock(3)] == ["Jack"], "The threshold parameter should be respected"
'''},
                    {"name": "save() / Inventory.load() round-trip", "code": r'''
from inventory import Inventory, Item
_inv = Inventory()
_inv.add(Item("Torch", 249.0, 4))
_inv.add(Item("Jack", 899.0, 2))
_inv.save("inv-test.json")
_loaded = Inventory.load("inv-test.json")
assert abs(_loaded.total_value() - _inv.total_value()) < 1e-6, \
    "The loaded inventory should match what was saved"
assert [i.name for i in _loaded.find("")] == ["Jack", "Torch"], \
    "load is a classmethod returning a new Inventory"
'''},
                    {"name": "report() lists items and the total", "code": r'''
from inventory import Inventory, Item
_inv = Inventory()
_inv.add(Item("Torch", 249.0, 4))
_inv.add(Item("Jack", 899.0, 2))
_rep = _inv.report()
assert isinstance(_rep, str) and "Torch" in _rep and "Jack" in _rep and "Total" in _rep, \
    "report() returns a string with every item and a Total line"
assert _rep.index("Jack") < _rep.index("Torch"), "Items should appear sorted by name"
'''},
                ],
            }],
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
