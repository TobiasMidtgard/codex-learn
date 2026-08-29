"""CS310 — Theory of Computation & Automata. Author module."""

COURSE = {
    "id": "CS310",
    "title": "Theory of Computation & Automata",
    "year": 3,
    "level": "Advanced",
    "prereqs": ["MA101", "CS201"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 130,
    "icon": "λ",
    "summary": (
        "The Chomsky hierarchy built as running code. You implement deterministic and "
        "nondeterministic finite automata, the subset construction that connects them, "
        "Thompson's translation from regular expressions, a CYK parser for context-free "
        "grammars, and a Turing machine with a step budget. Every construction is "
        "checked against the language it is supposed to denote, not against a diagram."
    ),
    "outcomes": [
        "Represent a finite automaton as data and simulate it over an input word",
        "Minimise a DFA by partition refinement and justify the resulting state count",
        "Decide equivalence of two regular languages by product construction",
        "Convert an NFA with epsilon moves into a DFA and verify the two agree",
        "Compile a regular expression into an automaton by Thompson's construction",
        "Parse a word against a Chomsky-normal-form grammar with CYK and count its derivations",
        "Simulate a Turing machine under a step budget and explain what that budget cannot decide",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone build (60%).",
    "reading": [
        "Sipser, *Introduction to the Theory of Computation*, 3rd ed. — chapters 1-3",
        "Hopcroft, Motwani & Ullman, *Introduction to Automata Theory, Languages, and Computation*, 3rd ed. — chapters 2-4, 7",
        "Thompson, 'Programming Techniques: Regular Expression Search Algorithm', CACM 11(6), 1968",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Deterministic finite automata and minimisation",
            "summary": "A DFA as data, its language as behaviour, and the unique smallest machine for it.",
            "concepts": [
                "The five-tuple (Q, Sigma, delta, q0, F), and totality of delta as the defining property of determinism",
                "Acceptance as a single walk of length |w| — regular languages need constant space",
                "Reachability pruning: a state the start cannot reach contributes nothing",
                "The Myhill-Nerode theorem: states of the minimal DFA are equivalence classes of the right-congruence",
                "Moore's partition refinement, splitting blocks by the signature of their outgoing transitions",
                "Canonical renaming by breadth-first order makes the minimal DFA literally unique",
                "Equivalence by product construction: walk both machines in lock-step and look for disagreement",
            ],
            "lab": {
                "title": "Simulate, minimise, compare",
                "runtime": "python",
                "minutes": 70,
                "brief": r'''
A `DFA` is constructed as `DFA(states, alphabet, delta, start, accepting)`,
where `delta` is a dict from `(state, symbol)` to a state. The constructor
stores the fields for you and then calls `self._validate()`, which you write.

**`_validate()`** raises `ValueError` when

- `start` is not in `states`,
- some accepting state is not in `states`,
- `delta` is missing an entry for some `(state, symbol)` pair — a DFA's
  transition function is **total**,
- some transition leads to a state outside `states`.

**`accepts(word)`** — walk from `start` and report membership. A symbol outside
the alphabet raises `ValueError`; it is not simply a rejection.

**`reachable()`** — the set of states reachable from `start`.

**`minimise()`** — a new `DFA` with the fewest possible states, whose states are
`0, 1, ..., k-1`, whose start is `0`, and whose numbering follows a
breadth-first walk from the start block over the alphabet in sorted order.
Drop unreachable states first, then refine the partition `{accepting,
non-accepting}` by transition signature until it stops splitting.

Because the numbering is canonical, two DFAs recognise the same language
**exactly when** their minimised forms are identical. The checks rely on that.

**`equivalent(a, b)`** — decide language equality by the product construction:
explore pairs of states reachable in lock-step from the two start states and
return `False` at the first pair whose acceptance disagrees. Raise `ValueError`
if the alphabets differ.

```text
EVEN_ZEROS.accepts("1010")      -> True     two zeros, and two is even
EVEN_ZEROS.accepts("0001")      -> False    three zeros is odd
len(REDUNDANT.minimise().states) -> 2
equivalent(EVEN_ZEROS, REDUNDANT) -> True
```
''',
                "files": [{"name": "main.py", "content": r'''
from collections import deque


class DFA:
    """A deterministic finite automaton over a finite alphabet."""

    def __init__(self, states, alphabet, delta, start, accepting):
        self.states = set(states)
        self.alphabet = tuple(sorted(alphabet))
        self.delta = dict(delta)
        self.start = start
        self.accepting = set(accepting)
        self._validate()

    def _validate(self):
        """Raise ValueError unless this really is a total, well-formed DFA."""
        # your code here

    def accepts(self, word):
        """True when the automaton ends in an accepting state. ValueError on a stray symbol."""
        # your code here

    def reachable(self):
        """The set of states reachable from the start state."""
        # your code here

    def minimise(self):
        """An equivalent DFA with states 0..k-1, numbered breadth-first from 0."""
        # your code here


def equivalent(a, b):
    """True when two DFAs over the same alphabet accept the same language."""
    # your code here


EVEN_ZEROS = DFA(
    states={"E", "O"},
    alphabet="01",
    delta={("E", "0"): "O", ("E", "1"): "E", ("O", "0"): "E", ("O", "1"): "O"},
    start="E",
    accepting={"E"},
)

REDUNDANT = DFA(
    states={0, 1, 2, 3},
    alphabet="01",
    delta={(0, "0"): 2, (0, "1"): 1, (1, "0"): 3, (1, "1"): 0,
           (2, "0"): 0, (2, "1"): 3, (3, "0"): 1, (3, "1"): 2},
    start=0,
    accepting={0, 1},
)

print(EVEN_ZEROS.accepts("0110"))
print(equivalent(EVEN_ZEROS, REDUNDANT))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
from collections import deque


class DFA:
    """A deterministic finite automaton over a finite alphabet."""

    def __init__(self, states, alphabet, delta, start, accepting):
        self.states = set(states)
        self.alphabet = tuple(sorted(alphabet))
        self.delta = dict(delta)
        self.start = start
        self.accepting = set(accepting)
        self._validate()

    def _validate(self):
        """Raise ValueError unless this really is a total, well-formed DFA."""
        if self.start not in self.states:
            raise ValueError(f"start state {self.start!r} is not in the state set")
        stray = self.accepting - self.states
        if stray:
            raise ValueError(f"accepting states outside the state set: {sorted(map(repr, stray))}")
        for q in self.states:
            for a in self.alphabet:
                if (q, a) not in self.delta:
                    raise ValueError(f"delta is not total: no entry for {(q, a)!r}")
                if self.delta[(q, a)] not in self.states:
                    raise ValueError(f"transition {(q, a)!r} leaves the state set")

    def accepts(self, word):
        """True when the automaton ends in an accepting state. ValueError on a stray symbol."""
        q = self.start
        for ch in word:
            if ch not in self.alphabet:
                raise ValueError(f"symbol {ch!r} is not in the alphabet {self.alphabet!r}")
            q = self.delta[(q, ch)]
        return q in self.accepting

    def reachable(self):
        """The set of states reachable from the start state."""
        seen = {self.start}
        queue = deque([self.start])
        while queue:
            q = queue.popleft()
            for a in self.alphabet:
                nxt = self.delta[(q, a)]
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return seen

    def minimise(self):
        """An equivalent DFA with states 0..k-1, numbered breadth-first from 0."""
        live = self.reachable()
        # Moore refinement: start from accepting versus not, split on signature.
        block = {q: (0 if q in self.accepting else 1) for q in live}
        while True:
            sig = {q: (block[q], tuple(block[self.delta[(q, a)]] for a in self.alphabet))
                   for q in live}
            groups = {}
            for q in live:
                groups.setdefault(sig[q], []).append(q)
            if len(groups) == len(set(block.values())):
                break
            block = {q: i for i, key in enumerate(sorted(groups))
                     for q in groups[key]}

        rep = {}
        for q in live:
            rep.setdefault(block[q], q)

        # Canonical numbering: breadth-first from the start block, alphabet in order.
        index = {block[self.start]: 0}
        order = [block[self.start]]
        queue = deque(order)
        while queue:
            b = queue.popleft()
            for a in self.alphabet:
                nb = block[self.delta[(rep[b], a)]]
                if nb not in index:
                    index[nb] = len(order)
                    order.append(nb)
                    queue.append(nb)

        delta = {}
        for b in order:
            for a in self.alphabet:
                delta[(index[b], a)] = index[block[self.delta[(rep[b], a)]]]
        accepting = {index[b] for b in order if rep[b] in self.accepting}
        return DFA(set(range(len(order))), self.alphabet, delta, 0, accepting)


def equivalent(a, b):
    """True when two DFAs over the same alphabet accept the same language."""
    if set(a.alphabet) != set(b.alphabet):
        raise ValueError(f"alphabets differ: {a.alphabet!r} versus {b.alphabet!r}")
    seen = {(a.start, b.start)}
    stack = [(a.start, b.start)]
    while stack:
        p, q = stack.pop()
        if (p in a.accepting) != (q in b.accepting):
            return False  # this pair is reached by a word only one machine accepts
        for ch in a.alphabet:
            nxt = (a.delta[(p, ch)], b.delta[(q, ch)])
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return True


EVEN_ZEROS = DFA(
    states={"E", "O"},
    alphabet="01",
    delta={("E", "0"): "O", ("E", "1"): "E", ("O", "0"): "E", ("O", "1"): "O"},
    start="E",
    accepting={"E"},
)

REDUNDANT = DFA(
    states={0, 1, 2, 3},
    alphabet="01",
    delta={(0, "0"): 2, (0, "1"): 1, (1, "0"): 3, (1, "1"): 0,
           (2, "0"): 0, (2, "1"): 3, (3, "0"): 1, (3, "1"): 2},
    start=0,
    accepting={0, 1},
)

print(EVEN_ZEROS.accepts("0110"))
print(equivalent(EVEN_ZEROS, REDUNDANT))
'''}],
                "hints": [
                    "`_validate` must loop over the full cross product of states and alphabet — a DFA missing one entry is not a DFA at all.",
                    "Refinement stops when a round produces no new blocks. Compare the number of signature groups against the number of distinct block ids you already had.",
                    "Pick one representative per block before you rebuild delta; every state in a block has the same outgoing block pattern by construction.",
                    "Number the new states by a breadth-first walk from the start block, taking symbols in sorted order. Without that, two machines for the same language minimise to different-looking answers.",
                ],
                "tests": [
                    {"name": "accepts walks the machine", "code": r'''
assert EVEN_ZEROS.accepts("") is True, "zero zeros is an even number of zeros"
for _w, _want in [("0", False), ("00", True), ("1010", True), ("0110", True),
                  ("111", True), ("010", True), ("0001", False)]:
    _got = EVEN_ZEROS.accepts(_w)
    assert _got == _want, f"EVEN_ZEROS.accepts({_w!r}) gave {_got!r}, expected {_want}"
for _w in ["0", "1", "0110", "111", ""]:
    assert REDUNDANT.accepts(_w) == EVEN_ZEROS.accepts(_w), (
        f"the two machines disagree on {_w!r}")
'''},
                    {"name": "a symbol outside the alphabet is an error", "code": r'''
for _bad in ["2", "01x", "abc"]:
    try:
        EVEN_ZEROS.accepts(_bad)
        assert False, f"accepts({_bad!r}) should raise ValueError, not return a verdict"
    except ValueError:
        pass
'''},
                    {"name": "_validate rejects malformed machines", "code": r'''
_ok = {("p", "a"): "p", ("p", "b"): "p"}
try:
    DFA({"p"}, "ab", {("p", "a"): "p"}, "p", set())
    assert False, "a missing (state, symbol) entry means delta is not total"
except ValueError:
    pass
try:
    DFA({"p"}, "ab", _ok, "q", set())
    assert False, "a start state outside the state set must raise ValueError"
except ValueError:
    pass
try:
    DFA({"p"}, "ab", _ok, "p", {"q"})
    assert False, "an accepting state outside the state set must raise ValueError"
except ValueError:
    pass
try:
    DFA({"p"}, "ab", {("p", "a"): "p", ("p", "b"): "zz"}, "p", set())
    assert False, "a transition leaving the state set must raise ValueError"
except ValueError:
    pass
_fine = DFA({"p"}, "ab", _ok, "p", {"p"})
assert _fine.accepts("abba") is True, "a one-state accepting sink accepts everything"
'''},
                    {"name": "reachable prunes what the start cannot see", "code": r'''
_d = DFA(
    states={"s", "t", "u"},
    alphabet="a",
    delta={("s", "a"): "t", ("t", "a"): "s", ("u", "a"): "u"},
    start="s",
    accepting={"t", "u"},
)
assert _d.reachable() == {"s", "t"}, f"got {_d.reachable()!r}, u is unreachable"
assert EVEN_ZEROS.reachable() == {"E", "O"}, f"got {EVEN_ZEROS.reachable()!r}"
assert len(_d.minimise().states) == 2, (
    f"got {len(_d.minimise().states)} states — the unreachable state must be dropped first")
'''},
                    {"name": "minimise on the textbook six-state machine", "code": r'''
_big = DFA(
    states=set("abcdef"),
    alphabet="01",
    delta={("a", "0"): "b", ("a", "1"): "c",
           ("b", "0"): "a", ("b", "1"): "d",
           ("c", "0"): "e", ("c", "1"): "f",
           ("d", "0"): "e", ("d", "1"): "f",
           ("e", "0"): "e", ("e", "1"): "f",
           ("f", "0"): "f", ("f", "1"): "f"},
    start="a",
    accepting={"c", "d", "e"},
)
_m = _big.minimise()
assert len(_m.states) == 3, f"the minimal machine has 3 states, you produced {len(_m.states)}"
assert _m.states == {0, 1, 2}, f"states should be 0..k-1, got {sorted(_m.states)!r}"
assert _m.start == 0, f"the start state should be 0, got {_m.start!r}"
for _w in ["", "0", "1", "01", "10", "0101", "111", "0011", "1101", "00000"]:
    assert _m.accepts(_w) == _big.accepts(_w), f"minimisation changed the verdict on {_w!r}"
'''},
                    {"name": "minimise is canonical and idempotent", "code": r'''
def _sig(d):
    return (sorted(d.states), d.start, sorted(d.accepting), sorted(d.delta.items()))


_a = EVEN_ZEROS.minimise()
_b = REDUNDANT.minimise()
assert len(_a.states) == 2 and len(_b.states) == 2, (
    f"both machines minimise to 2 states, got {len(_a.states)} and {len(_b.states)}")
assert _sig(_a) == _sig(_b), (
    "two DFAs for the same language must minimise to the identical canonical machine, "
    f"got {_sig(_a)!r} and {_sig(_b)!r}")
assert _sig(_a.minimise()) == _sig(_a), "minimising a minimal DFA must change nothing"
'''},
                    {"name": "minimise handles the degenerate languages", "code": r'''
_none = DFA({0, 1}, "ab",
            {(0, "a"): 1, (0, "b"): 1, (1, "a"): 0, (1, "b"): 0}, 0, set())
_m = _none.minimise()
assert len(_m.states) == 1 and _m.accepting == set(), (
    f"the empty language minimises to one rejecting state, got {len(_m.states)} states")
_all = DFA({0, 1}, "ab",
           {(0, "a"): 1, (0, "b"): 1, (1, "a"): 0, (1, "b"): 0}, 0, {0, 1})
_m2 = _all.minimise()
assert len(_m2.states) == 1 and _m2.accepting == {0}, (
    f"Sigma* minimises to one accepting state, got {len(_m2.states)} states")
'''},
                    {"name": "equivalent decides language equality", "code": r'''
assert equivalent(EVEN_ZEROS, REDUNDANT) is True, "these two recognise the same language"
assert equivalent(EVEN_ZEROS, EVEN_ZEROS.minimise()) is True
_odd = DFA({"E", "O"}, "01",
           {("E", "0"): "O", ("E", "1"): "E", ("O", "0"): "E", ("O", "1"): "O"},
           "E", {"O"})
assert equivalent(EVEN_ZEROS, _odd) is False, "even and odd counts are complementary"
try:
    equivalent(EVEN_ZEROS, DFA({"p"}, "ab", {("p", "a"): "p", ("p", "b"): "p"}, "p", {"p"}))
    assert False, "different alphabets must raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "equivalent agrees with exhaustive word comparison", "code": r'''
import itertools as _it
import random as _random

_rng = _random.Random(7)


def _random_dfa(n):
    _delta = {}
    for _q in range(n):
        for _s in "ab":
            _delta[(_q, _s)] = _rng.randrange(n)
    return DFA(set(range(n)), "ab", _delta, 0,
               {_q for _q in range(n) if _rng.random() < 0.4})


def _same_up_to(d1, d2, k):
    for _n in range(k + 1):
        for _tup in _it.product("ab", repeat=_n):
            _w = "".join(_tup)
            if d1.accepts(_w) != d2.accepts(_w):
                return False
    return True


for _trial in range(40):
    _d1 = _random_dfa(_rng.randrange(1, 5))
    _d2 = _random_dfa(_rng.randrange(1, 5))
    _got = equivalent(_d1, _d2)
    _want = _same_up_to(_d1, _d2, 8)
    assert _got == _want, (
        f"equivalent said {_got!r} but exhaustive comparison up to length 8 said {_want!r}")
    if _got:
        def _sig2(d):
            return (sorted(d.states), d.start, sorted(d.accepting), sorted(d.delta.items()))
        assert _sig2(_d1.minimise()) == _sig2(_d2.minimise()), (
            "equivalent machines must have identical canonical minimal forms")
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Nondeterminism and the subset construction",
            "summary": "Epsilon moves, sets of states as a single state, and the exponential that rarely bites.",
            "concepts": [
                "An NFA transition returns a set; acceptance asks whether *some* run accepts",
                "Epsilon moves and closure under them: the closure is a least fixed point",
                "Simulating an NFA directly costs O(|w| * |Q|^2) time and O(|Q|) space",
                "The subset construction: states of the DFA are epsilon-closed subsets of Q",
                "The empty subset is the dead state and must be present for delta to be total",
                "The 2^|Q| bound is tight in the worst case but almost never reached in practice",
                "Two machines agree on a language exactly when they agree on every word — which is why a bounded exhaustive check is a real test",
            ],
            "lab": {
                "title": "Epsilon closure and determinisation",
                "runtime": "python",
                "minutes": 65,
                "brief": r'''
`NFA(states, alphabet, delta, start, accepting)` where `delta` maps
`(state, symbol)` to a **set** of states, and the symbol `""` denotes an
epsilon move. A missing key means no transition at all. The `DFA` class at the
bottom of the file is given to you complete — you do not modify it.

**`epsilon_closure(states)`** — the least set containing `states` and closed
under epsilon moves. Returns a `frozenset`. The closure of a set always
contains that set.

**`step(states, symbol)`** — read one real symbol from a set of current states
and epsilon-close the result. Returns a `frozenset`. Raise `ValueError` if the
symbol is not in the alphabet.

**`accepts(word)`** — start from `epsilon_closure({start})` and fold `step`
across the word.

**`subset_construction(nfa)`** — returns an equivalent `DFA` whose states are
`frozenset`s of NFA states, whose start is `epsilon_closure({nfa.start})`, and
whose accepting states are the subsets meeting `nfa.accepting`. Explore only
the subsets you actually reach, but make sure `delta` is total: if a subset has
no successor on some symbol, the successor is `frozenset()`, and that empty
subset is itself a state with self-loops on every symbol.

```text
ABB.accepts("abb")     -> True     the classic (a|b)*abb machine
ABB.accepts("abba")    -> False
len(subset_construction(ABB).states) -> 4
```

The checks compare `nfa.accepts(w)` against `subset_construction(nfa).accepts(w)`
for every word up to length 6, over hand-written and randomly generated NFAs.
''',
                "files": [{"name": "main.py", "content": r'''
from collections import deque

EPSILON = ""


class NFA:
    """A nondeterministic finite automaton, with epsilon moves under the key ""."""

    def __init__(self, states, alphabet, delta, start, accepting):
        self.states = set(states)
        self.alphabet = tuple(sorted(alphabet))
        self.delta = {k: frozenset(v) for k, v in delta.items()}
        self.start = start
        self.accepting = set(accepting)

    def moves(self, state, symbol):
        """The set of successors of one state on one symbol (or on epsilon)."""
        return self.delta.get((state, symbol), frozenset())

    def epsilon_closure(self, states):
        """The least epsilon-closed superset of states, as a frozenset."""
        # your code here

    def step(self, states, symbol):
        """Read one real symbol, then epsilon-close. ValueError on a stray symbol."""
        # your code here

    def accepts(self, word):
        """True when some run of the machine ends in an accepting state."""
        # your code here


def subset_construction(nfa):
    """An equivalent DFA whose states are frozensets of NFA states."""
    # your code here


class DFA:
    """Given, complete. A total deterministic automaton."""

    def __init__(self, states, alphabet, delta, start, accepting):
        self.states = set(states)
        self.alphabet = tuple(sorted(alphabet))
        self.delta = dict(delta)
        self.start = start
        self.accepting = set(accepting)
        for q in self.states:
            for a in self.alphabet:
                if (q, a) not in self.delta:
                    raise ValueError(f"delta is not total: no entry for {(q, a)!r}")

    def accepts(self, word):
        q = self.start
        for ch in word:
            if ch not in self.alphabet:
                raise ValueError(f"symbol {ch!r} is not in the alphabet")
            q = self.delta[(q, ch)]
        return q in self.accepting


# (a|b)* a b b — nondeterministic, because state 0 guesses when the suffix begins.
ABB = NFA(
    states={0, 1, 2, 3},
    alphabet="ab",
    delta={(0, "a"): {0, 1}, (0, "b"): {0}, (1, "b"): {2}, (2, "b"): {3}},
    start=0,
    accepting={3},
)

# An epsilon chain: 0 -eps-> 1 -eps-> 2, and 2 loops on "a".
CHAIN = NFA(
    states={0, 1, 2},
    alphabet="a",
    delta={(0, ""): {1}, (1, ""): {2}, (2, "a"): {2}},
    start=0,
    accepting={2},
)

print(ABB.accepts("abb"))
print(sorted(CHAIN.epsilon_closure({0})) if CHAIN.epsilon_closure({0}) else None)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
from collections import deque

EPSILON = ""


class NFA:
    """A nondeterministic finite automaton, with epsilon moves under the key ""."""

    def __init__(self, states, alphabet, delta, start, accepting):
        self.states = set(states)
        self.alphabet = tuple(sorted(alphabet))
        self.delta = {k: frozenset(v) for k, v in delta.items()}
        self.start = start
        self.accepting = set(accepting)

    def moves(self, state, symbol):
        """The set of successors of one state on one symbol (or on epsilon)."""
        return self.delta.get((state, symbol), frozenset())

    def epsilon_closure(self, states):
        """The least epsilon-closed superset of states, as a frozenset."""
        seen = set(states)
        stack = list(seen)
        while stack:
            q = stack.pop()
            for nxt in self.moves(q, EPSILON):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return frozenset(seen)

    def step(self, states, symbol):
        """Read one real symbol, then epsilon-close. ValueError on a stray symbol."""
        if symbol not in self.alphabet:
            raise ValueError(f"symbol {symbol!r} is not in the alphabet {self.alphabet!r}")
        landed = set()
        for q in states:
            landed |= self.moves(q, symbol)
        return self.epsilon_closure(landed)

    def accepts(self, word):
        """True when some run of the machine ends in an accepting state."""
        current = self.epsilon_closure({self.start})
        for ch in word:
            current = self.step(current, ch)
        return bool(current & self.accepting)


def subset_construction(nfa):
    """An equivalent DFA whose states are frozensets of NFA states."""
    start = nfa.epsilon_closure({nfa.start})
    states = {start}
    delta = {}
    queue = deque([start])
    while queue:
        subset = queue.popleft()
        for ch in nfa.alphabet:
            # An empty successor is the dead state, and it is a state like any other.
            nxt = nfa.step(subset, ch) if subset else frozenset()
            delta[(subset, ch)] = nxt
            if nxt not in states:
                states.add(nxt)
                queue.append(nxt)
    accepting = {s for s in states if s & nfa.accepting}
    return DFA(states, nfa.alphabet, delta, start, accepting)


class DFA:
    """Given, complete. A total deterministic automaton."""

    def __init__(self, states, alphabet, delta, start, accepting):
        self.states = set(states)
        self.alphabet = tuple(sorted(alphabet))
        self.delta = dict(delta)
        self.start = start
        self.accepting = set(accepting)
        for q in self.states:
            for a in self.alphabet:
                if (q, a) not in self.delta:
                    raise ValueError(f"delta is not total: no entry for {(q, a)!r}")

    def accepts(self, word):
        q = self.start
        for ch in word:
            if ch not in self.alphabet:
                raise ValueError(f"symbol {ch!r} is not in the alphabet")
            q = self.delta[(q, ch)]
        return q in self.accepting


# (a|b)* a b b — nondeterministic, because state 0 guesses when the suffix begins.
ABB = NFA(
    states={0, 1, 2, 3},
    alphabet="ab",
    delta={(0, "a"): {0, 1}, (0, "b"): {0}, (1, "b"): {2}, (2, "b"): {3}},
    start=0,
    accepting={3},
)

# An epsilon chain: 0 -eps-> 1 -eps-> 2, and 2 loops on "a".
CHAIN = NFA(
    states={0, 1, 2},
    alphabet="a",
    delta={(0, ""): {1}, (1, ""): {2}, (2, "a"): {2}},
    start=0,
    accepting={2},
)

print(ABB.accepts("abb"))
print(sorted(CHAIN.epsilon_closure({0})) if CHAIN.epsilon_closure({0}) else None)
'''}],
                "hints": [
                    "The closure is a worklist loop: seed the set with the given states, pop, and push every epsilon successor you have not already seen.",
                    "`step` moves first and closes second. Closing before the move would let epsilon transitions be taken after the symbol was consumed.",
                    "In `subset_construction`, generate transitions for every reached subset including `frozenset()` — the dead state loops to itself, which keeps the DFA total.",
                    "A subset is accepting when it *intersects* the NFA's accepting set, not when it is contained in it.",
                ],
                "tests": [
                    {"name": "epsilon_closure reaches a fixed point", "code": r'''
assert CHAIN.epsilon_closure({0}) == frozenset({0, 1, 2}), \
    f"got {sorted(CHAIN.epsilon_closure({0}))!r}"
assert CHAIN.epsilon_closure({2}) == frozenset({2}), "state 2 has no epsilon moves"
assert CHAIN.epsilon_closure(set()) == frozenset(), "the closure of nothing is nothing"
assert isinstance(CHAIN.epsilon_closure({0}), frozenset), "return a frozenset, it is used as a dict key"
_loop = NFA({0, 1}, "a", {(0, ""): {1}, (1, ""): {0}}, 0, {1})
assert _loop.epsilon_closure({0}) == frozenset({0, 1}), "an epsilon cycle must terminate, not spin"
assert ABB.epsilon_closure({0, 3}) == frozenset({0, 3}), "no epsilon moves means the set is its own closure"
'''},
                    {"name": "step reads one symbol and closes", "code": r'''
assert ABB.step(frozenset({0}), "a") == frozenset({0, 1}), f"got {sorted(ABB.step(frozenset({0}), 'a'))!r}"
assert ABB.step(frozenset({0}), "b") == frozenset({0}), f"got {sorted(ABB.step(frozenset({0}), 'b'))!r}"
assert ABB.step(frozenset({1}), "a") == frozenset(), "state 1 has no a-transition"
assert ABB.step(frozenset(), "a") == frozenset(), "nowhere leads nowhere"
assert CHAIN.step(frozenset({0, 1, 2}), "a") == frozenset({2}), \
    f"got {sorted(CHAIN.step(frozenset({0, 1, 2}), 'a'))!r}"
try:
    ABB.step(frozenset({0}), "z")
    assert False, "a symbol outside the alphabet must raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "accepts on the two given machines", "code": r'''
for _w, _want in [("abb", True), ("aabb", True), ("babb", True), ("abba", False),
                  ("", False), ("ab", False), ("bb", False), ("abbabb", True)]:
    _got = ABB.accepts(_w)
    assert _got == _want, f"ABB.accepts({_w!r}) gave {_got!r}, expected {_want}"
assert CHAIN.accepts("") is True, "the epsilon chain reaches the accepting state on the empty word"
assert CHAIN.accepts("aaa") is True
'''},
                    {"name": "subset_construction gives a total DFA with the right shape", "code": r'''
_d = subset_construction(ABB)
assert _d.start == frozenset({0}), f"the start subset is {sorted(_d.start)!r}, expected {{0}}"
assert all(isinstance(_s, frozenset) for _s in _d.states), "states are frozensets of NFA states"
assert len(_d.states) == 4, f"got {len(_d.states)} subsets, the reachable ones number 4"
for _s in _d.states:
    for _c in "ab":
        assert (_s, _c) in _d.delta, f"delta is missing {(sorted(_s), _c)!r}"
assert _d.accepting == {_s for _s in _d.states if 3 in _s}, "a subset accepts when it holds state 3"
_dc = subset_construction(CHAIN)
assert _dc.start == frozenset({0, 1, 2}), f"got {sorted(_dc.start)!r}"
'''},
                    {"name": "the dead subset exists and loops", "code": r'''
_dead_nfa = NFA({0, 1}, "ab", {(0, "a"): {1}}, 0, {1})
_d = subset_construction(_dead_nfa)
assert frozenset() in _d.states, "a machine that can get stuck needs the empty subset as a state"
for _c in "ab":
    assert _d.delta[(frozenset(), _c)] == frozenset(), "the dead state loops to itself"
assert frozenset() not in _d.accepting, "the dead state never accepts"
assert _d.accepts("a") is True and _d.accepts("ab") is False and _d.accepts("b") is False
'''},
                    {"name": "the DFA agrees with the NFA on every short word", "code": r'''
import itertools as _it


def _agree(nfa, k):
    _d = subset_construction(nfa)
    for _n in range(k + 1):
        for _tup in _it.product(nfa.alphabet, repeat=_n):
            _w = "".join(_tup)
            assert nfa.accepts(_w) == _d.accepts(_w), (
                f"on {_w!r} the NFA said {nfa.accepts(_w)!r} but the DFA said {_d.accepts(_w)!r}")


_agree(ABB, 6)
_agree(CHAIN, 5)
_agree(NFA({0}, "ab", {}, 0, set()), 5)
_agree(NFA({0}, "ab", {(0, "a"): {0}, (0, "b"): {0}}, 0, {0}), 5)
'''},
                    {"name": "and on randomly generated machines too", "code": r'''
import itertools as _it
import random as _random

_rng = _random.Random(7)
for _trial in range(12):
    _n = _rng.randrange(1, 5)
    _delta = {}
    for _q in range(_n):
        for _sym in ["a", "b", ""]:
            _targets = {_t for _t in range(_n) if _rng.random() < 0.35}
            if _sym == "" and _q in _targets:
                _targets.discard(_q)  # a self epsilon loop adds nothing
            if _targets:
                _delta[(_q, _sym)] = _targets
    _nfa = NFA(set(range(_n)), "ab", _delta, 0,
               {_q for _q in range(_n) if _rng.random() < 0.4})
    _d = subset_construction(_nfa)
    for _k in range(7):
        for _tup in _it.product("ab", repeat=_k):
            _w = "".join(_tup)
            assert _nfa.accepts(_w) == _d.accepts(_w), (
                f"machine {_delta!r} accepting {_nfa.accepting!r} disagrees with its "
                f"subset DFA on {_w!r}")
'''},
                    {"name": "the exponential worst case really is reached", "code": r'''
# (a|b)* a (a|b)^(k-1): the (k+1)-state NFA needs 2^k DFA states.
_k = 4
_states = set(range(_k + 1))
_delta = {(0, "a"): {0, 1}, (0, "b"): {0}}
for _i in range(1, _k):
    _delta[(_i, "a")] = {_i + 1}
    _delta[(_i, "b")] = {_i + 1}
_nfa = NFA(_states, "ab", _delta, 0, {_k})
_d = subset_construction(_nfa)
assert len(_d.states) == 2 ** _k, (
    f"got {len(_d.states)} subsets, the tight bound for k={_k} is {2 ** _k}")
assert _nfa.accepts("abaa") is True and _nfa.accepts("bbaab") is False
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Regular expressions and Thompson's construction",
            "summary": "Parse the notation, compile it to an automaton, and run the automaton.",
            "concepts": [
                "The three regular operations — union, concatenation, Kleene star — and their precedence",
                "Recursive descent over the grammar alt := concat ('|' concat)*, concat := repeat*, repeat := atom postfix*",
                "Thompson fragments: one entry, one exit, glued by epsilon moves",
                "Linear size: each operator adds at most two states, so |Q| <= 2m + 2 for a pattern of length m",
                "Simulating the fragment with epsilon closures gives O(m * n) matching without backtracking",
                "Catastrophic backtracking is a property of the algorithm, not of the notation",
                "Kleene's theorem in one direction: every regular expression denotes a language some finite automaton accepts",
            ],
            "lab": {
                "title": "From pattern to automaton",
                "runtime": "python",
                "minutes": 75,
                "brief": r'''
The notation: literals, `|` for union, juxtaposition for concatenation, the
postfix operators `*`, `+` and `?`, parentheses for grouping, and `\` to escape
any of `( ) | * + ? \`. The empty pattern denotes the empty word.

**`parse(pattern)`** — a syntax tree built from these tuples:

```text
("eps",)            the empty word
("char", c)         one literal character
("cat", left, right)
("alt", left, right)
("star", inner)  ("plus", inner)  ("opt", inner)
```

Concatenation binds tighter than `|` and looser than the postfix operators, and
it folds to the left: `abc` parses as `("cat", ("cat", a, b), c)`. Raise
`ValueError` for an unclosed `(`, a stray `)`, a postfix operator with nothing
to its left, or a trailing `\`.

**`thompson(tree)`** — returns an `NFA` with integer states, one `start`, one
`accept`, and `trans` mapping `(state, symbol)` to a set of states, where the
symbol `""` is an epsilon move. Follow the standard fragments so that the state
count stays linear: the checks assert `nfa.n <= 2 * len(pattern) + 2`.

**`NFA.fullmatch(word)`** — simulate by epsilon closure, one symbol at a time.
No backtracking.

**`Regex(pattern)`** — compiles once in `__init__` and exposes `fullmatch(s)`.

```text
Regex("(a|b)*abb").fullmatch("babb")  -> True
Regex("a*b+c?").fullmatch("aabbc")    -> True
Regex("").fullmatch("")               -> True
Regex("a|").fullmatch("")             -> True
```

The checks compare your matcher against `re.fullmatch` over a battery of
patterns and words. Your notation is a strict subset of Python's, so on these
inputs the two must agree exactly.
''',
                "files": [{"name": "main.py", "content": r'''
META = "()|*+?\\"


class NFA:
    """A Thompson fragment promoted to a whole machine."""

    def __init__(self, n, start, accept, trans):
        self.n = n
        self.start = start
        self.accept = accept
        self.trans = trans  # {(state, symbol): set(states)}, "" is epsilon

    def closure(self, states):
        """The epsilon closure of a set of states, as a frozenset."""
        # your code here

    def fullmatch(self, word):
        """True when the whole word is accepted."""
        # your code here


def parse(pattern):
    """The syntax tree for a pattern. ValueError on malformed input."""
    # your code here


def thompson(tree):
    """Compile a syntax tree into an NFA by Thompson's construction."""
    # your code here


class Regex:
    """A compiled pattern."""

    def __init__(self, pattern):
        self.pattern = pattern
        # your code here

    def fullmatch(self, word):
        """True when the whole word matches the pattern."""
        # your code here


print(parse("ab"))
print(Regex("(a|b)*abb").fullmatch("babb"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
META = "()|*+?\\"


class NFA:
    """A Thompson fragment promoted to a whole machine."""

    def __init__(self, n, start, accept, trans):
        self.n = n
        self.start = start
        self.accept = accept
        self.trans = trans  # {(state, symbol): set(states)}, "" is epsilon

    def closure(self, states):
        """The epsilon closure of a set of states, as a frozenset."""
        seen = set(states)
        stack = list(seen)
        while stack:
            q = stack.pop()
            for nxt in self.trans.get((q, ""), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return frozenset(seen)

    def fullmatch(self, word):
        """True when the whole word is accepted."""
        current = self.closure({self.start})
        for ch in word:
            landed = set()
            for q in current:
                landed |= self.trans.get((q, ch), set())
            current = self.closure(landed)
            if not current:
                return False
        return self.accept in current


def parse(pattern):
    """The syntax tree for a pattern. ValueError on malformed input."""
    pos = [0]

    def peek():
        return pattern[pos[0]] if pos[0] < len(pattern) else None

    def parse_alt():
        node = parse_cat()
        while peek() == "|":
            pos[0] += 1
            node = ("alt", node, parse_cat())
        return node

    def parse_cat():
        node = None
        while True:
            ch = peek()
            if ch is None or ch in "|)":
                break
            piece = parse_repeat()
            node = piece if node is None else ("cat", node, piece)
        return node if node is not None else ("eps",)

    def parse_repeat():
        node = parse_atom()
        while peek() in ("*", "+", "?"):
            node = {"*": "star", "+": "plus", "?": "opt"}[pattern[pos[0]]], node
            pos[0] += 1
        return node

    def parse_atom():
        ch = peek()
        if ch is None:
            raise ValueError("pattern ends where an atom was expected")
        if ch == "(":
            pos[0] += 1
            inner = parse_alt()
            if peek() != ")":
                raise ValueError("unclosed ( in the pattern")
            pos[0] += 1
            return inner
        if ch == ")":
            raise ValueError("unmatched ) in the pattern")
        if ch in "*+?":
            raise ValueError(f"postfix {ch!r} has nothing to repeat")
        if ch == "\\":
            pos[0] += 1
            if peek() is None:
                raise ValueError("pattern ends in a trailing backslash")
            lit = pattern[pos[0]]
            pos[0] += 1
            return ("char", lit)
        pos[0] += 1
        return ("char", ch)

    tree = parse_alt()
    if pos[0] != len(pattern):
        raise ValueError(f"unexpected {pattern[pos[0]]!r} at position {pos[0]}")
    return tree


def thompson(tree):
    """Compile a syntax tree into an NFA by Thompson's construction."""
    trans = {}
    counter = [0]

    def fresh():
        counter[0] += 1
        return counter[0] - 1

    def link(a, symbol, b):
        trans.setdefault((a, symbol), set()).add(b)

    def build(node):
        kind = node[0]
        if kind == "eps":
            s, t = fresh(), fresh()
            link(s, "", t)
            return s, t
        if kind == "char":
            s, t = fresh(), fresh()
            link(s, node[1], t)
            return s, t
        if kind == "cat":
            s1, t1 = build(node[1])
            s2, t2 = build(node[2])
            link(t1, "", s2)  # the join costs no states at all
            return s1, t2
        if kind == "alt":
            s, t = fresh(), fresh()
            s1, t1 = build(node[1])
            s2, t2 = build(node[2])
            link(s, "", s1)
            link(s, "", s2)
            link(t1, "", t)
            link(t2, "", t)
            return s, t
        if kind in ("star", "plus", "opt"):
            s, t = fresh(), fresh()
            s1, t1 = build(node[1])
            link(s, "", s1)
            link(t1, "", t)
            if kind != "plus":
                link(s, "", t)      # skip the body entirely
            if kind != "opt":
                link(t1, "", s1)    # go round again
            return s, t
        raise ValueError(f"unknown node {node!r}")

    start, accept = build(tree)
    return NFA(counter[0], start, accept, trans)


class Regex:
    """A compiled pattern."""

    def __init__(self, pattern):
        self.pattern = pattern
        self.tree = parse(pattern)
        self.nfa = thompson(self.tree)

    def fullmatch(self, word):
        """True when the whole word matches the pattern."""
        return self.nfa.fullmatch(word)


print(parse("ab"))
print(Regex("(a|b)*abb").fullmatch("babb"))
'''}],
                "hints": [
                    "Carry the cursor in a one-element list so the nested helper functions can advance it without a `nonlocal` declaration in every one.",
                    "`parse_cat` stops on `|`, on `)` and at the end of the pattern. Stopping anywhere else, or not stopping at all, is what produces the confusing error messages.",
                    "A concatenation fragment adds no states: link the left fragment's accept to the right fragment's start with an epsilon move and reuse the outer endpoints.",
                    "Star, plus and opt share one shape. Star has both the skip edge and the loop edge, plus has only the loop, opt has only the skip.",
                ],
                "tests": [
                    {"name": "parse builds the right shapes", "code": r'''
assert parse("a") == ("char", "a"), f"got {parse('a')!r}"
assert parse("") == ("eps",), f"the empty pattern is epsilon, got {parse('')!r}"
assert parse("ab") == ("cat", ("char", "a"), ("char", "b")), f"got {parse('ab')!r}"
assert parse("abc") == ("cat", ("cat", ("char", "a"), ("char", "b")), ("char", "c")), \
    f"concatenation folds to the left, got {parse('abc')!r}"
assert parse("a|b") == ("alt", ("char", "a"), ("char", "b")), f"got {parse('a|b')!r}"
assert parse("ab|c") == ("alt", ("cat", ("char", "a"), ("char", "b")), ("char", "c")), \
    f"concatenation binds tighter than |, got {parse('ab|c')!r}"
assert parse("ab*") == ("cat", ("char", "a"), ("star", ("char", "b"))), \
    f"a postfix binds tighter than concatenation, got {parse('ab*')!r}"
assert parse("(ab)*") == ("star", ("cat", ("char", "a"), ("char", "b"))), f"got {parse('(ab)*')!r}"
assert parse("a+") == ("plus", ("char", "a")) and parse("a?") == ("opt", ("char", "a"))
assert parse("a|") == ("alt", ("char", "a"), ("eps",)), f"got {parse('a|')!r}"
'''},
                    {"name": "parse rejects malformed patterns", "code": r'''
for _bad in ["(a", "a)", "*a", "+", "?x", "a\\", "((a)", "(|"]:
    try:
        parse(_bad)
        assert False, f"parse({_bad!r}) should raise ValueError"
    except ValueError:
        pass
assert parse("\\*") == ("char", "*"), f"an escaped star is a literal, got {parse('\\*')!r}"
assert parse("\\\\") == ("char", "\\"), "an escaped backslash is a literal backslash"
'''},
                    {"name": "thompson keeps the machine linear in the pattern", "code": r'''
for _p in ["", "a", "ab", "abc", "(a|b)*abb", "a*b+c?", "((ab)|c)*", "a|b|c|d",
           "(a?b?)*", "\\*\\+"]:
    _nfa = thompson(parse(_p))
    assert _nfa.n <= 2 * len(_p) + 2, (
        f"pattern {_p!r} of length {len(_p)} built {_nfa.n} states, "
        f"Thompson's construction allows at most {2 * len(_p) + 2}")
    assert _nfa.start != _nfa.accept or _nfa.n == 1, "a fragment has a distinct entry and exit"
    assert 0 <= _nfa.start < _nfa.n and 0 <= _nfa.accept < _nfa.n, "states are 0..n-1"
'''},
                    {"name": "the matcher on hand-picked words", "code": r'''
_r = Regex("(a|b)*abb")
for _w, _want in [("abb", True), ("babb", True), ("aabb", True), ("abba", False),
                  ("", False), ("ab", False), ("abbabb", True), ("c", False)]:
    _got = _r.fullmatch(_w)
    assert _got == _want, f"(a|b)*abb on {_w!r} gave {_got!r}, expected {_want}"
assert Regex("").fullmatch("") is True and Regex("").fullmatch("a") is False
assert Regex("a|").fullmatch("") is True, "the right branch of a| is epsilon"
assert Regex("a*").fullmatch("") is True and Regex("a+").fullmatch("") is False
assert Regex("a?").fullmatch("") is True and Regex("a?").fullmatch("aa") is False
'''},
                    {"name": "the matcher agrees with Python re", "code": r'''
import itertools as _it
import re as _re

_patterns = ["", "a", "ab", "a|b", "ab|c", "(a|b)*abb", "a*b+c?", "((ab)|c)*",
             "a|b|c", "(a?b?)*", "(ab)+", "a(b|c)*d", "(a*)*b", "abc|ab|a"]
for _p in _patterns:
    _mine = Regex(_p)
    for _k in range(6):
        for _tup in _it.product("abcd", repeat=_k):
            _w = "".join(_tup)
            _want = _re.fullmatch(_p, _w) is not None
            _got = _mine.fullmatch(_w)
            assert _got == _want, (
                f"pattern {_p!r} on {_w!r}: you said {_got!r}, re says {_want!r}")
'''},
                    {"name": "escapes match literal metacharacters", "code": r'''
import re as _re

for _p, _w in [("\\*", "*"), ("a\\|b", "a|b"), ("\\(\\)", "()"), ("\\+", "+"),
               ("\\?", "?"), ("\\\\", "\\")]:
    assert Regex(_p).fullmatch(_w) is True, f"{_p!r} should match {_w!r}"
    assert _re.fullmatch(_p, _w) is not None, "sanity: re agrees"
assert Regex("\\*").fullmatch("a") is False, "an escaped star matches only a star"
assert Regex("a\\*").fullmatch("aaa") is False, "a\\* is the literal two-character word a*"
assert Regex("a\\*").fullmatch("a*") is True
'''},
                    {"name": "no catastrophic backtracking", "code": r'''
import time as _time

# A backtracking matcher needs exponential time on this shape; an NFA
# simulation with epsilon closures does not.
_r = Regex("(a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?a?)aaaaaaaaaaaaaaaaaaaa")
_t0 = _time.perf_counter()
assert _r.fullmatch("a" * 20) is True, "twenty as should match"
assert _r.fullmatch("a" * 19 + "b") is False, "a trailing b cannot match"
_elapsed = _time.perf_counter() - _t0
assert _elapsed < 4.0, (
    f"took {_elapsed:.2f}s — simulate the set of current states, do not backtrack")
'''},
                    {"name": "closure and fullmatch on a hand-built fragment", "code": r'''
_nfa = NFA(3, 0, 2, {(0, ""): {1}, (1, "a"): {2}})
assert _nfa.closure({0}) == frozenset({0, 1}), f"got {sorted(_nfa.closure({0}))!r}"
assert _nfa.closure({2}) == frozenset({2})
assert _nfa.closure(set()) == frozenset(), "the closure of nothing is nothing"
assert _nfa.fullmatch("a") is True and _nfa.fullmatch("") is False
assert _nfa.fullmatch("aa") is False, "there is nowhere to go after the first a"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Context-free grammars and CYK parsing",
            "summary": "Beyond regular: a cubic-time membership test that also counts derivations.",
            "concepts": [
                "Chomsky normal form: every rule is A -> B C or A -> a, with no unit and no epsilon rules",
                "The pumping lemma for regular languages, and why a^n b^n escapes it",
                "CYK as dynamic programming over spans: the table cell for a span holds every nonterminal deriving it",
                "The cubic bound O(n^3 |G|), and where the split point loop contributes the third factor",
                "Counting derivations instead of merely recording them turns the parser into an ambiguity detector",
                "Ambiguity is a property of the grammar, not of the language; inherent ambiguity is a property of the language",
                "Searching words in length order gives the shortest ambiguous witness, if one exists within the bound",
            ],
            "lab": {
                "title": "A CYK parser that counts",
                "runtime": "python",
                "minutes": 70,
                "brief": r'''
`Grammar(rules, start)` where `rules` is a list of `(lhs, rhs)` pairs and `rhs`
is a tuple. The nonterminals are exactly the left-hand sides.

**Validation in `__init__`** — raise `ValueError` unless the grammar is in
Chomsky normal form:

- `start` must be a nonterminal,
- every `rhs` must have length 1 or 2,
- a one-symbol `rhs` must be a terminal, that is a single character that is not
  a nonterminal (so unit rules `A -> B` and epsilon rules are both rejected),
- a two-symbol `rhs` must consist of two nonterminals.

Expose `self.nonterminals`, `self.terminals` and `self.by_lhs`, a dict from a
nonterminal to the list of its right-hand sides.

**`cyk(grammar, word)`** — the parse table as a dict from `(i, length)` to
`{nonterminal: number of parse trees}`, holding only the non-empty cells.
`word[i:i+length]` is the span. The empty word gives `{}`.

**`accepts(grammar, word)`** — whether the start symbol derives the whole word.

**`count_parses(grammar, word)`** — the number of distinct parse trees, `0`
when the word is not in the language.

**`shortest_ambiguous(grammar, max_len)`** — the shortest word of length 1 to
`max_len` over the grammar's terminals with more than one parse tree, taking
words in length order and, within a length, in sorted-terminal order. `None`
when there is none in range.

```text
count_parses(DOUBLE, "aaa")   -> 2       S -> S S | a
count_parses(DOUBLE, "aaaa")  -> 5       the Catalan numbers
shortest_ambiguous(DOUBLE, 5) -> "aaa"
shortest_ambiguous(ANBN, 6)   -> None
accepts(ANBN, "aabb")         -> True
accepts(ANBN, "")             -> False   CNF cannot derive the empty word
```
''',
                "files": [{"name": "main.py", "content": r'''
import itertools


class Grammar:
    """A context-free grammar restricted to Chomsky normal form."""

    def __init__(self, rules, start):
        self.rules = [(lhs, tuple(rhs)) for lhs, rhs in rules]
        self.start = start
        self.nonterminals = {lhs for lhs, _ in self.rules}
        self.terminals = set()
        self.by_lhs = {}
        self._validate()

    def _validate(self):
        """Raise ValueError unless every rule is in Chomsky normal form."""
        # your code here


def cyk(grammar, word):
    """{(i, length): {nonterminal: parse tree count}} for every non-empty cell."""
    # your code here


def accepts(grammar, word):
    """True when the start symbol derives the whole word."""
    # your code here


def count_parses(grammar, word):
    """The number of distinct parse trees for word, or 0."""
    # your code here


def shortest_ambiguous(grammar, max_len):
    """The shortest word up to max_len with more than one parse, or None."""
    # your code here


# S -> S S | a  — the textbook ambiguous grammar.
DOUBLE = Grammar([("S", ("S", "S")), ("S", ("a",))], "S")

# { a^n b^n : n >= 1 }, unambiguous, and not regular.
ANBN = Grammar([
    ("S", ("A", "B")),
    ("S", ("A", "C")),
    ("C", ("S", "B")),
    ("A", ("a",)),
    ("B", ("b",)),
], "S")

print(accepts(ANBN, "aabb"))
print(count_parses(DOUBLE, "aaa"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import itertools


class Grammar:
    """A context-free grammar restricted to Chomsky normal form."""

    def __init__(self, rules, start):
        self.rules = [(lhs, tuple(rhs)) for lhs, rhs in rules]
        self.start = start
        self.nonterminals = {lhs for lhs, _ in self.rules}
        self.terminals = set()
        self.by_lhs = {}
        self._validate()

    def _validate(self):
        """Raise ValueError unless every rule is in Chomsky normal form."""
        if self.start not in self.nonterminals:
            raise ValueError(f"start symbol {self.start!r} has no rules")
        for lhs, rhs in self.rules:
            if len(rhs) == 1:
                sym = rhs[0]
                if sym in self.nonterminals:
                    raise ValueError(f"unit rule {lhs!r} -> {sym!r} is not in CNF")
                if not isinstance(sym, str) or len(sym) != 1:
                    raise ValueError(f"terminal {sym!r} must be a single character")
                self.terminals.add(sym)
            elif len(rhs) == 2:
                for sym in rhs:
                    if sym not in self.nonterminals:
                        raise ValueError(
                            f"{sym!r} on the right of {lhs!r} is not a nonterminal")
            else:
                raise ValueError(
                    f"rule {lhs!r} -> {rhs!r} has {len(rhs)} symbols; CNF allows 1 or 2")
            self.by_lhs.setdefault(lhs, []).append(rhs)


def cyk(grammar, word):
    """{(i, length): {nonterminal: parse tree count}} for every non-empty cell."""
    n = len(word)
    table = {}
    if n == 0:
        return table  # CNF has no epsilon rules, so nothing derives the empty word
    for i, ch in enumerate(word):
        cell = {}
        for lhs, rhs in grammar.rules:
            if len(rhs) == 1 and rhs[0] == ch:
                cell[lhs] = cell.get(lhs, 0) + 1
        if cell:
            table[(i, 1)] = cell
    for length in range(2, n + 1):
        for i in range(0, n - length + 1):
            cell = {}
            for split in range(1, length):
                left = table.get((i, split))
                right = table.get((i + split, length - split))
                if not left or not right:
                    continue
                for lhs, rhs in grammar.rules:
                    if len(rhs) != 2:
                        continue
                    a, b = rhs
                    if a in left and b in right:
                        # Trees on the left times trees on the right, summed
                        # over every split point: that is the derivation count.
                        cell[lhs] = cell.get(lhs, 0) + left[a] * right[b]
            if cell:
                table[(i, length)] = cell
    return table


def accepts(grammar, word):
    """True when the start symbol derives the whole word."""
    return count_parses(grammar, word) > 0


def count_parses(grammar, word):
    """The number of distinct parse trees for word, or 0."""
    if not word:
        return 0
    table = cyk(grammar, word)
    return table.get((0, len(word)), {}).get(grammar.start, 0)


def shortest_ambiguous(grammar, max_len):
    """The shortest word up to max_len with more than one parse, or None."""
    letters = sorted(grammar.terminals)
    for length in range(1, max_len + 1):
        for combo in itertools.product(letters, repeat=length):
            word = "".join(combo)
            if count_parses(grammar, word) > 1:
                return word
    return None


# S -> S S | a  — the textbook ambiguous grammar.
DOUBLE = Grammar([("S", ("S", "S")), ("S", ("a",))], "S")

# { a^n b^n : n >= 1 }, unambiguous, and not regular.
ANBN = Grammar([
    ("S", ("A", "B")),
    ("S", ("A", "C")),
    ("C", ("S", "B")),
    ("A", ("a",)),
    ("B", ("b",)),
], "S")

print(accepts(ANBN, "aabb"))
print(count_parses(DOUBLE, "aaa"))
'''}],
                "hints": [
                    "Build `by_lhs` and `terminals` while you validate, not in a second pass — the validation already visits every rule.",
                    "Fill the table by increasing span length. A cell of length L needs cells of length 1..L-1, all of which are already present.",
                    "The count for `A -> B C` over one split is `left[B] * right[C]`; sum that over every split point, and never overwrite what an earlier split contributed.",
                    "`itertools.product(sorted(terminals), repeat=length)` enumerates words in the order the specification asks for.",
                ],
                "tests": [
                    {"name": "the grammar validator enforces CNF", "code": r'''
assert DOUBLE.nonterminals == {"S"}, f"got {DOUBLE.nonterminals!r}"
assert DOUBLE.terminals == {"a"}, f"got {DOUBLE.terminals!r}"
assert ANBN.terminals == {"a", "b"}, f"got {ANBN.terminals!r}"
assert sorted(ANBN.by_lhs["S"]) == [("A", "B"), ("A", "C")], f"got {ANBN.by_lhs['S']!r}"
_cases = [
    ([("S", ("T",)), ("T", ("a",))], "S"),          # unit rule
    ([("S", ())], "S"),                              # epsilon rule
    ([("S", ("a", "b", "c"))], "S"),                 # three symbols
    ([("S", ("A", "B")), ("A", ("a",))], "S"),       # B has no rules
    ([("S", ("a",))], "T"),                          # start has no rules
    ([("S", ("ab",))], "S"),                         # terminal is two characters
]
for _rules, _start in _cases:
    try:
        Grammar(_rules, _start)
        assert False, f"Grammar({_rules!r}, {_start!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "membership for a^n b^n", "code": r'''
for _w in ["ab", "aabb", "aaabbb", "aaaabbbb"]:
    assert accepts(ANBN, _w) is True, f"{_w!r} should be accepted"
for _w in ["", "a", "b", "ba", "abb", "aab", "abab", "aabbb", "bbaa"]:
    assert accepts(ANBN, _w) is False, f"{_w!r} should be rejected"
assert count_parses(ANBN, "") == 0, "CNF cannot derive the empty word"
assert cyk(ANBN, "") == {}, f"the empty word gives an empty table, got {cyk(ANBN, '')!r}"
'''},
                    {"name": "the table cells hold the right nonterminals", "code": r'''
_t = cyk(ANBN, "aabb")
assert _t[(0, 1)] == {"A": 1}, f"span a at 0 gave {_t[(0, 1)]!r}"
assert _t[(2, 1)] == {"B": 1}, f"span b at 2 gave {_t[(2, 1)]!r}"
assert _t[(1, 2)] == {"S": 1}, f"the inner ab should be an S, got {_t.get((1, 2))!r}"
assert _t[(0, 4)] == {"S": 1}, f"the whole word gave {_t[(0, 4)]!r}"
assert (0, 2) not in _t, f"the span aa derives nothing, got {_t.get((0, 2))!r}"
assert all(_v for _v in _t.values()), "empty cells must be omitted, not stored as {}"
'''},
                    {"name": "counting derivations gives the Catalan numbers", "code": r'''
for _n, _want in [(1, 1), (2, 1), (3, 2), (4, 5), (5, 14), (6, 42), (7, 132)]:
    _got = count_parses(DOUBLE, "a" * _n)
    assert _got == _want, f"{_n} as have {_want} parse trees, you counted {_got}"
assert count_parses(DOUBLE, "b") == 0, "b is not in the language"
assert count_parses(DOUBLE, "") == 0
'''},
                    {"name": "unambiguous grammars count exactly one", "code": r'''
for _w in ["ab", "aabb", "aaabbb", "aaaabbbb", "aaaaabbbbb"]:
    _got = count_parses(ANBN, _w)
    assert _got == 1, f"a^n b^n is unambiguous but {_w!r} counted {_got} parses"
'''},
                    {"name": "counts agree with an independent top-down counter", "code": r'''
import itertools as _it
import random as _random
from functools import lru_cache as _lru


def _ref_count(grammar, word):
    _rules = {}
    for _lhs, _rhs in grammar.rules:
        _rules.setdefault(_lhs, []).append(_rhs)

    @_lru(maxsize=None)
    def _go(sym, i, j):
        _total = 0
        for _rhs in _rules.get(sym, []):
            if len(_rhs) == 1:
                if j - i == 1 and word[i] == _rhs[0]:
                    _total += 1
            else:
                for _k in range(i + 1, j):
                    _l = _go(_rhs[0], i, _k)
                    if _l:
                        _total += _l * _go(_rhs[1], _k, j)
        return _total

    if not word:
        return 0
    return _go(grammar.start, 0, len(word))


_rng = _random.Random(7)
_grammars = [DOUBLE, ANBN,
             Grammar([("S", ("S", "T")), ("S", ("T", "S")), ("S", ("a",)),
                      ("T", ("b",)), ("T", ("T", "T"))], "S")]
for _g in _grammars:
    _letters = sorted(_g.terminals)
    for _k in range(1, 6):
        for _tup in _it.product(_letters, repeat=_k):
            _w = "".join(_tup)
            _got, _want = count_parses(_g, _w), _ref_count(_g, _w)
            assert _got == _want, (
                f"on {_w!r} your parser counted {_got} trees, the reference counted {_want}")
'''},
                    {"name": "shortest_ambiguous finds the smallest witness", "code": r'''
assert shortest_ambiguous(DOUBLE, 5) == "aaa", f"got {shortest_ambiguous(DOUBLE, 5)!r}"
assert shortest_ambiguous(DOUBLE, 2) is None, "no ambiguity shows up before length 3"
assert shortest_ambiguous(ANBN, 6) is None, "a^n b^n is unambiguous"
_amb = Grammar([("S", ("A", "B")), ("S", ("C", "D")),
                ("A", ("a",)), ("B", ("b",)), ("C", ("a",)), ("D", ("b",))], "S")
assert shortest_ambiguous(_amb, 4) == "ab", (
    f"got {shortest_ambiguous(_amb, 4)!r} — two rule paths derive the same two letters")
assert count_parses(_amb, "ab") == 2
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Turing machines, budgets and undecidability",
            "summary": "The last model on the ladder, and the first question no program can answer.",
            "concepts": [
                "A configuration is state, head position and tape contents; a computation is a sequence of them",
                "The transition function is partial: a missing entry halts the machine",
                "The Church-Turing thesis, and why a one-tape machine is enough",
                "A step budget turns a possibly non-terminating simulation into a total function that answers a different question",
                "Configuration repetition proves divergence — a sound but incomplete halting test",
                "Why no sound *and* complete test exists: the diagonal argument on a supposed decider for HALT",
                "The busy beaver function grows faster than any computable function, so no budget is ever enough",
            ],
            "lab": {
                "title": "A Turing machine you can watch",
                "runtime": "python",
                "minutes": 65,
                "brief": r'''
`TuringMachine(transitions, start, accept, blank="_")` where `transitions` maps
`(state, symbol)` to `(new_state, write_symbol, direction)` and direction is
`"L"`, `"R"` or `"S"`. A missing entry means the machine halts where it stands.

A **configuration** is `(state, head, cells)` where `cells` is a tuple of
`(index, symbol)` pairs, sorted by index, listing only the non-blank cells. It
is a tuple so that configurations are hashable, which is the whole point of the
last function.

**Validation in `__init__`** — raise `ValueError` for a direction outside
`"LRS"`, or a `blank` that is not a single character.

**`config(tape)`** — the initial configuration: `start` state, head at 0, the
non-blank cells of `tape` at indices `0, 1, ...`.

**`step(cfg)`** — the next configuration, or `None` when the machine has
halted (it is in the accept state, or no transition applies).

**`tape_string(cells)`** — the cells from the lowest to the highest non-blank
index, as a string; `""` when nothing is written.

**`run(tape, max_steps=1000)`** — a dict with keys `halted`, `accepted`,
`steps`, `state`, `head` and `tape`. The budget is checked *before* each step,
so `steps` never exceeds `max_steps` and `halted` is honest.

**`detect_loop(machine, tape, max_steps=1000)`** — the step number at which a
configuration first repeats one already seen, or `None` if the machine halts or
the budget runs out first. A repeat proves the machine never halts on that
input. It is sound; it is not complete, and `RIGHTWARD` shows why.

```text
INCREMENT.run("1011")["tape"]   -> "1100"
INCREMENT.run("111")["tape"]    -> "1000"     the tape grew leftwards
ANBN.run("aabb")["accepted"]    -> True
LOOPER.run("", 50)              -> halted False, steps 50
detect_loop(LOOPER, "")         -> 1
detect_loop(RIGHTWARD, "")      -> None       it diverges without repeating
```
''',
                "files": [{"name": "main.py", "content": r'''
class TuringMachine:
    """A single-tape deterministic Turing machine over a two-way infinite tape."""

    def __init__(self, transitions, start, accept, blank="_"):
        self.transitions = dict(transitions)
        self.start = start
        self.accept = accept
        self.blank = blank
        self._validate()

    def _validate(self):
        """ValueError on a bad direction or a blank that is not one character."""
        # your code here

    def config(self, tape):
        """The initial configuration (state, head, cells)."""
        # your code here

    def tape_string(self, cells):
        """The written span of the tape, lowest index to highest."""
        # your code here

    def step(self, cfg):
        """The next configuration, or None when the machine has halted."""
        # your code here

    def run(self, tape, max_steps=1000):
        """{halted, accepted, steps, state, head, tape} after at most max_steps steps."""
        # your code here


def detect_loop(machine, tape, max_steps=1000):
    """The step at which a configuration first repeats, or None."""
    # your code here


# Add one to a binary number written most significant digit first.
INCREMENT = TuringMachine(
    transitions={
        ("right", "0"): ("right", "0", "R"),
        ("right", "1"): ("right", "1", "R"),
        ("right", "_"): ("carry", "_", "L"),
        ("carry", "1"): ("carry", "0", "L"),
        ("carry", "0"): ("done", "1", "S"),
        ("carry", "_"): ("done", "1", "S"),
    },
    start="right",
    accept="done",
)

# Recognise { a^n b^n : n >= 1 } by crossing off one a and one b per sweep.
ANBN = TuringMachine(
    transitions={
        ("q0", "a"): ("q1", "X", "R"),
        ("q0", "Y"): ("q3", "Y", "R"),
        ("q1", "a"): ("q1", "a", "R"),
        ("q1", "Y"): ("q1", "Y", "R"),
        ("q1", "b"): ("q2", "Y", "L"),
        ("q2", "a"): ("q2", "a", "L"),
        ("q2", "Y"): ("q2", "Y", "L"),
        ("q2", "X"): ("q0", "X", "R"),
        ("q3", "Y"): ("q3", "Y", "R"),
        ("q3", "_"): ("qacc", "_", "S"),
    },
    start="q0",
    accept="qacc",
)

LOOPER = TuringMachine({("q", "_"): ("q", "_", "S")}, "q", "halt")
RIGHTWARD = TuringMachine({("q", "_"): ("q", "_", "R")}, "q", "halt")

print(INCREMENT.run("1011")["tape"])
print(ANBN.run("aabb")["accepted"])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class TuringMachine:
    """A single-tape deterministic Turing machine over a two-way infinite tape."""

    def __init__(self, transitions, start, accept, blank="_"):
        self.transitions = dict(transitions)
        self.start = start
        self.accept = accept
        self.blank = blank
        self._validate()

    def _validate(self):
        """ValueError on a bad direction or a blank that is not one character."""
        if not isinstance(self.blank, str) or len(self.blank) != 1:
            raise ValueError(f"blank {self.blank!r} must be a single character")
        for key, action in self.transitions.items():
            if len(action) != 3:
                raise ValueError(f"transition {key!r} -> {action!r} needs three parts")
            _state, _write, move = action
            if move not in ("L", "R", "S"):
                raise ValueError(f"direction {move!r} in {key!r} must be L, R or S")

    def config(self, tape):
        """The initial configuration (state, head, cells)."""
        cells = tuple((i, ch) for i, ch in enumerate(tape) if ch != self.blank)
        return (self.start, 0, cells)

    def tape_string(self, cells):
        """The written span of the tape, lowest index to highest."""
        if not cells:
            return ""
        mapping = dict(cells)
        lo, hi = min(mapping), max(mapping)
        return "".join(mapping.get(i, self.blank) for i in range(lo, hi + 1))

    def step(self, cfg):
        """The next configuration, or None when the machine has halted."""
        state, head, cells = cfg
        if state == self.accept:
            return None
        mapping = dict(cells)
        symbol = mapping.get(head, self.blank)
        action = self.transitions.get((state, symbol))
        if action is None:
            return None  # a partial transition function: no entry means halt
        new_state, write, move = action
        if write == self.blank:
            mapping.pop(head, None)
        else:
            mapping[head] = write
        if move == "L":
            head -= 1
        elif move == "R":
            head += 1
        return (new_state, head, tuple(sorted(mapping.items())))

    def run(self, tape, max_steps=1000):
        """{halted, accepted, steps, state, head, tape} after at most max_steps steps."""
        cfg = self.config(tape)
        steps = 0
        halted = False
        while True:
            nxt = self.step(cfg)
            if nxt is None:
                halted = True
                break
            if steps >= max_steps:
                break  # the budget is checked before the step is taken
            cfg = nxt
            steps += 1
        state, head, cells = cfg
        return {
            "halted": halted,
            "accepted": halted and state == self.accept,
            "steps": steps,
            "state": state,
            "head": head,
            "tape": self.tape_string(cells),
        }


def detect_loop(machine, tape, max_steps=1000):
    """The step at which a configuration first repeats, or None."""
    cfg = machine.config(tape)
    seen = {cfg}
    for step in range(1, max_steps + 1):
        cfg = machine.step(cfg)
        if cfg is None:
            return None  # it halted, so there is no loop to report
        if cfg in seen:
            return step
        seen.add(cfg)
    return None


# Add one to a binary number written most significant digit first.
INCREMENT = TuringMachine(
    transitions={
        ("right", "0"): ("right", "0", "R"),
        ("right", "1"): ("right", "1", "R"),
        ("right", "_"): ("carry", "_", "L"),
        ("carry", "1"): ("carry", "0", "L"),
        ("carry", "0"): ("done", "1", "S"),
        ("carry", "_"): ("done", "1", "S"),
    },
    start="right",
    accept="done",
)

# Recognise { a^n b^n : n >= 1 } by crossing off one a and one b per sweep.
ANBN = TuringMachine(
    transitions={
        ("q0", "a"): ("q1", "X", "R"),
        ("q0", "Y"): ("q3", "Y", "R"),
        ("q1", "a"): ("q1", "a", "R"),
        ("q1", "Y"): ("q1", "Y", "R"),
        ("q1", "b"): ("q2", "Y", "L"),
        ("q2", "a"): ("q2", "a", "L"),
        ("q2", "Y"): ("q2", "Y", "L"),
        ("q2", "X"): ("q0", "X", "R"),
        ("q3", "Y"): ("q3", "Y", "R"),
        ("q3", "_"): ("qacc", "_", "S"),
    },
    start="q0",
    accept="qacc",
)

LOOPER = TuringMachine({("q", "_"): ("q", "_", "S")}, "q", "halt")
RIGHTWARD = TuringMachine({("q", "_"): ("q", "_", "R")}, "q", "halt")

print(INCREMENT.run("1011")["tape"])
print(ANBN.run("aabb")["accepted"])
'''}],
                "hints": [
                    "Keep the cells as a dict while you are editing them, and freeze back to `tuple(sorted(mapping.items()))` before you return the configuration.",
                    "Writing the blank symbol should delete the cell, not store it — otherwise two configurations that are really identical will not compare equal.",
                    "In `run`, ask `step` for the next configuration first. If it is `None` the machine halted; only then does the budget matter.",
                    "`detect_loop` needs the initial configuration in the seen set before the first step, or a machine that returns to its start on step one goes unnoticed.",
                ],
                "tests": [
                    {"name": "configurations and the tape rendering", "code": r'''
_cfg = INCREMENT.config("1011")
assert _cfg[0] == "right" and _cfg[1] == 0, f"got {_cfg[:2]!r}"
assert _cfg[2] == ((0, "1"), (1, "0"), (2, "1"), (3, "1")), f"got {_cfg[2]!r}"
assert INCREMENT.config("")[2] == (), "an empty tape has no written cells"
assert INCREMENT.config("__")[2] == (), "blanks are not written cells"
assert INCREMENT.tape_string(()) == "", "nothing written renders as the empty string"
assert INCREMENT.tape_string(((0, "1"), (2, "1"))) == "1_1", \
    f"a gap is filled with the blank, got {INCREMENT.tape_string(((0, '1'), (2, '1')))!r}"
assert INCREMENT.tape_string(((-1, "1"), (0, "0"))) == "10", "negative indices come first"
'''},
                    {"name": "_validate rejects a bad machine", "code": r'''
for _bad in [({("q", "_"): ("q", "_", "X")}, "q", "h", "_"),
             ({("q", "_"): ("q", "_", "R")}, "q", "h", "__"),
             ({("q", "_"): ("q", "_")}, "q", "h", "_")]:
    try:
        TuringMachine(*_bad)
        assert False, f"TuringMachine{_bad!r} should raise ValueError"
    except ValueError:
        pass
_ok = TuringMachine({("q", "_"): ("h", "1", "S")}, "q", "h")
assert _ok.run("")["tape"] == "1", "S means stay, and the write still happens"
'''},
                    {"name": "step advances one configuration at a time", "code": r'''
_c0 = INCREMENT.config("0")
_c1 = INCREMENT.step(_c0)
assert _c1 == ("right", 1, ((0, "0"),)), f"got {_c1!r}"
_c2 = INCREMENT.step(_c1)
assert _c2 == ("carry", 0, ((0, "0"),)), f"got {_c2!r}"
_c3 = INCREMENT.step(_c2)
assert _c3 == ("done", 0, ((0, "1"),)), f"got {_c3!r}"
assert INCREMENT.step(_c3) is None, "the accept state has no successor"
_stuck = TuringMachine({}, "q", "h")
assert _stuck.step(_stuck.config("a")) is None, "no applicable transition means halt"
'''},
                    {"name": "the increment machine computes", "code": r'''
for _tape, _want in [("0", "1"), ("1", "10"), ("1011", "1100"), ("111", "1000"),
                     ("1111", "10000"), ("10", "11"), ("0111", "1000")]:
    _r = INCREMENT.run(_tape)
    assert _r["halted"] is True, f"{_tape!r} did not halt: {_r!r}"
    assert _r["accepted"] is True, f"{_tape!r} halted outside the accept state: {_r!r}"
    assert _r["tape"] == _want, f"increment({_tape!r}) wrote {_r['tape']!r}, expected {_want!r}"
assert INCREMENT.run("1011")["steps"] == 8, f"got {INCREMENT.run('1011')['steps']!r} steps"
assert INCREMENT.run("111")["head"] == -1, "the carry ran off the left end of the input"
'''},
                    {"name": "the a^n b^n recogniser", "code": r'''
for _w in ["ab", "aabb", "aaabbb", "aaaabbbb"]:
    _r = ANBN.run(_w, 500)
    assert _r["halted"] is True and _r["accepted"] is True, f"{_w!r} should be accepted: {_r!r}"
for _w in ["", "a", "b", "ba", "aab", "abb", "abab", "aaabb"]:
    _r = ANBN.run(_w, 500)
    assert _r["halted"] is True, f"{_w!r} should halt: {_r!r}"
    assert _r["accepted"] is False, f"{_w!r} should be rejected: {_r!r}"
assert ANBN.run("aabb", 500)["state"] == "qacc", "an accepted run ends in the accept state"
'''},
                    {"name": "the budget is a budget", "code": r'''
_r = LOOPER.run("", 50)
assert _r["halted"] is False, f"LOOPER never halts, got {_r!r}"
assert _r["steps"] == 50, f"the budget was 50, you took {_r['steps']}"
assert _r["accepted"] is False, "an exhausted budget is not an acceptance"
_r2 = LOOPER.run("", 0)
assert _r2["steps"] == 0 and _r2["halted"] is False, f"got {_r2!r}"
_r3 = INCREMENT.run("1011", 3)
assert _r3["halted"] is False and _r3["steps"] == 3, (
    f"a budget below the true running time must report an unfinished run, got {_r3!r}")
_r4 = INCREMENT.run("1011", 8)
assert _r4["halted"] is True and _r4["steps"] == 8, f"got {_r4!r}"
'''},
                    {"name": "loop detection is sound but incomplete", "code": r'''
assert detect_loop(LOOPER, "") == 1, f"got {detect_loop(LOOPER, '')!r} — step 1 returns to step 0"
assert detect_loop(INCREMENT, "1011") is None, "a machine that halts has no loop to report"
assert detect_loop(ANBN, "aabb", 500) is None
assert detect_loop(RIGHTWARD, "", 200) is None, (
    "RIGHTWARD diverges without ever repeating a configuration — the head keeps moving, "
    "so configuration repetition cannot detect it")
_r = RIGHTWARD.run("", 200)
assert _r["halted"] is False and _r["head"] == 200, f"got {_r!r}"
_flip = TuringMachine({("p", "_"): ("q", "1", "R"),
                       ("q", "_"): ("r", "_", "L"),
                       ("r", "1"): ("p", "_", "S")}, "p", "h")
assert detect_loop(_flip, "", 10) == 3, (
    f"write, move right, come back and erase: that is a three-step cycle, got "
    f"{detect_loop(_flip, '', 10)!r}")
assert detect_loop(_flip, "", 2) is None, "a budget shorter than the cycle finds nothing"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a regular-language toolkit",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
Assemble the first three modules into one library, `regtool.py`, driven from
`main.py`. The toolkit takes regular expressions in and answers questions about
the *languages* they denote — membership, size of the minimal automaton,
emptiness, the shortest member, and equality of two languages — none of which
can be answered by looking at the patterns.

## Pipeline

`parse` -> `thompson` -> `to_dfa` -> `minimise`. Each stage is a public
function and is tested on its own.

- **`parse(pattern)`** — the same notation and the same tuple trees as module 3:
  `("eps",)`, `("char", c)`, `("cat", l, r)`, `("alt", l, r)`, `("star", x)`,
  `("plus", x)`, `("opt", x)`. `ValueError` on malformed input.
- **`literals(tree)`** — the set of characters the pattern can match.
- **`thompson(tree)`** — an `NFA` with integer states, fields `n`, `start`,
  `accept`, `trans`, and at most `2m + 2` states for a pattern of length `m`.
- **`to_dfa(nfa, alphabet)`** — subset construction, but with the resulting
  states renamed to `0..k-1` in breadth-first order over the sorted alphabet, so
  the output is a `DFA` with integer states and a total transition function.
  The dead subset is included when it is reachable.
- **`minimise(dfa)`** — partition refinement plus the same canonical
  breadth-first renaming. Two DFAs over the same alphabet accept the same
  language exactly when their minimised forms are identical.

## Decision procedures

- **`equivalent(d1, d2)`** — product construction. `ValueError` on differing
  alphabets.
- **`is_empty(dfa)`** — no accepting state is reachable.
- **`shortest_word(dfa)`** — the shortest accepted word, breaking ties by the
  sorted alphabet order; `None` for the empty language, `""` when the start
  state accepts.
- **`complement(dfa)`** — flip the accepting set. This only works because
  `to_dfa` returns a *total* machine.
- **`intersect(d1, d2)`** — product construction with integer state names in
  breadth-first order. `ValueError` on differing alphabets.

## The facade

`Language(pattern, alphabet=None)` compiles once and exposes `alphabet`,
`dfa` (already minimal), `matches(word)`, `size()`, `is_empty()`,
`shortest()` and `equivalent(other)`. The default alphabet is the pattern's own
literals. `matches` returns `False` for a word containing a symbol outside the
alphabet rather than raising — a word over the wrong alphabet is simply not in
the language. `equivalent(other)` recompiles both sides over the union of the
two alphabets, because `a*` and `a*` over `{a}` and over `{a, b}` are the same
language but not the same automaton.
''',
        "deliverables": [
            "`regtool.py` — `parse`, `literals`, `NFA`, `thompson`, `DFA`, `to_dfa`, `minimise`, `equivalent`, `is_empty`, `shortest_word`, `complement`, `intersect`, `Language`, importable with no side effects",
            "`main.py` — compiles a couple of patterns, prints minimal state counts, the shortest member, and an equivalence verdict",
            "A canonical `minimise` whose output depends only on the language, not on the pattern that produced it",
            "A total `to_dfa`, including the dead state, so `complement` is correct without further work",
            "`Language.equivalent` that reconciles the two alphabets before comparing",
            "`ValueError` on every malformed pattern and on every mismatched-alphabet operation",
        ],
        "constraints": [
            "Standard library only; do not import `re` — you are implementing it",
            "`regtool.py` must define things only: importing it must print nothing",
            "`to_dfa` and `minimise` must return DFAs with integer states `0..k-1` and start state `0`",
            "No global caches: two `Language` objects must not share compiled state",
            "Every automaton you return must have a total transition function",
        ],
        "rubric": [
            {"criterion": "Parser and Thompson construction", "weight": 25,
             "evidence": "Precedence, escapes and the four error paths are right; the NFA stays within 2m + 2 states and matches the same words as an independent oracle."},
            {"criterion": "Determinisation and minimisation", "weight": 30,
             "evidence": "to_dfa is total and agrees with the NFA on every short word; minimise is idempotent, canonical, and gives 4 states for (a|b)*abb."},
            {"criterion": "Decision procedures", "weight": 25,
             "evidence": "equivalent, is_empty, shortest_word, complement and intersect are correct on hand-checked and exhaustively compared cases."},
            {"criterion": "Alphabet discipline", "weight": 12,
             "evidence": "Mismatched alphabets raise; Language.equivalent recompiles over the union; matches rejects foreign symbols without raising."},
            {"criterion": "Structure and readability", "weight": 8,
             "evidence": "regtool.py is import-clean, each stage is separately callable, and the canonical-renaming step is commented where it is subtle."},
        ],
        "hints": [
            "Build `to_dfa` in two phases: explore subsets exactly as in module 2, then walk the subset graph breadth-first from the start subset to assign the integer names.",
            "Both `to_dfa` and `minimise` end with the same renaming step. Write it once as a helper that takes a start key, a successor function and the sorted alphabet.",
            "`minimise` must run reachability first. An unreachable accepting state would otherwise survive refinement and break the canonical form.",
            "`shortest_word` is a breadth-first search over states, keeping the first word that reaches each state — with the alphabet in sorted order that word is automatically the smallest.",
            "In `Language.equivalent`, recompile *both* sides over the union alphabet; comparing one recompiled machine against the other's original will raise on the alphabet check.",
        ],
        "files": [
            {"name": "regtool.py", "content": r'''
from collections import deque

META = "()|*+?\\"


# ------------------------------------------------------------------ syntax
def parse(pattern):
    """The syntax tree for a pattern. ValueError on malformed input."""
    # your code here


def literals(tree):
    """The set of characters the pattern can match."""
    # your code here


# ------------------------------------------------------------------ automata
class NFA:
    """A Thompson fragment: integer states, one entry, one exit."""

    def __init__(self, n, start, accept, trans):
        self.n = n
        self.start = start
        self.accept = accept
        self.trans = trans  # {(state, symbol): set(states)}, "" is epsilon

    def closure(self, states):
        """The epsilon closure of a set of states, as a frozenset."""
        # your code here

    def move(self, states, symbol):
        """Read one real symbol from a set of states, then close."""
        # your code here

    def fullmatch(self, word):
        """True when the whole word is accepted."""
        # your code here


def thompson(tree):
    """Compile a syntax tree into an NFA."""
    # your code here


class DFA:
    """A total deterministic automaton with integer states 0..n-1."""

    def __init__(self, n, alphabet, delta, start, accepting):
        self.n = n
        self.alphabet = tuple(sorted(alphabet))
        self.delta = dict(delta)
        self.start = start
        self.accepting = set(accepting)
        for q in range(n):
            for a in self.alphabet:
                if (q, a) not in self.delta:
                    raise ValueError(f"delta is not total: no entry for {(q, a)!r}")

    def accepts(self, word):
        """True when the automaton ends in an accepting state."""
        q = self.start
        for ch in word:
            if ch not in self.alphabet:
                raise ValueError(f"symbol {ch!r} is not in the alphabet {self.alphabet!r}")
            q = self.delta[(q, ch)]
        return q in self.accepting

    def signature(self):
        """A canonical value: equal signatures mean identical machines."""
        return (self.n, self.alphabet, self.start,
                tuple(sorted(self.accepting)), tuple(sorted(self.delta.items())))


def to_dfa(nfa, alphabet):
    """Subset construction, renamed breadth-first to integer states."""
    # your code here


def minimise(dfa):
    """The unique minimal DFA for the same language, canonically numbered."""
    # your code here


# ------------------------------------------------------------------ decisions
def equivalent(d1, d2):
    """True when two DFAs over the same alphabet accept the same language."""
    # your code here


def is_empty(dfa):
    """True when no accepting state is reachable from the start."""
    # your code here


def shortest_word(dfa):
    """The shortest accepted word, or None when the language is empty."""
    # your code here


def complement(dfa):
    """A DFA for the complement over the same alphabet."""
    # your code here


def intersect(d1, d2):
    """A DFA for the intersection. ValueError on differing alphabets."""
    # your code here


# ------------------------------------------------------------------ facade
class Language:
    """A regular language, held as its minimal DFA."""

    def __init__(self, pattern, alphabet=None):
        self.pattern = pattern
        # your code here

    def matches(self, word):
        """True when word is in the language. Foreign symbols mean False, not an error."""
        # your code here

    def size(self):
        """The number of states in the minimal DFA."""
        # your code here

    def is_empty(self):
        """True when the language contains no word at all."""
        # your code here

    def shortest(self):
        """The shortest member, or None."""
        # your code here

    def equivalent(self, other):
        """True when both denote the same language, over the union of the alphabets."""
        # your code here
'''},
            {"name": "main.py", "content": r'''
from regtool import Language

abb = Language("(a|b)*abb")
same = Language("(a|b)*abb|(a|b)*abb")
plus = Language("a+", "ab")

print("states  ", abb.size())
print("shortest", abb.shortest())
print("equal   ", abb.equivalent(same))
print("a+ vs a*", plus.equivalent(Language("a*", "ab")))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "regtool.py", "content": r'''
from collections import deque

META = "()|*+?\\"


# ------------------------------------------------------------------ syntax
def parse(pattern):
    """The syntax tree for a pattern. ValueError on malformed input."""
    pos = [0]

    def peek():
        return pattern[pos[0]] if pos[0] < len(pattern) else None

    def parse_alt():
        node = parse_cat()
        while peek() == "|":
            pos[0] += 1
            node = ("alt", node, parse_cat())
        return node

    def parse_cat():
        node = None
        while True:
            ch = peek()
            if ch is None or ch in "|)":
                break
            piece = parse_repeat()
            node = piece if node is None else ("cat", node, piece)
        return node if node is not None else ("eps",)

    def parse_repeat():
        node = parse_atom()
        while peek() in ("*", "+", "?"):
            node = ({"*": "star", "+": "plus", "?": "opt"}[pattern[pos[0]]], node)
            pos[0] += 1
        return node

    def parse_atom():
        ch = peek()
        if ch is None:
            raise ValueError("pattern ends where an atom was expected")
        if ch == "(":
            pos[0] += 1
            inner = parse_alt()
            if peek() != ")":
                raise ValueError("unclosed ( in the pattern")
            pos[0] += 1
            return inner
        if ch == ")":
            raise ValueError("unmatched ) in the pattern")
        if ch in "*+?":
            raise ValueError(f"postfix {ch!r} has nothing to repeat")
        if ch == "\\":
            pos[0] += 1
            if peek() is None:
                raise ValueError("pattern ends in a trailing backslash")
            lit = pattern[pos[0]]
            pos[0] += 1
            return ("char", lit)
        pos[0] += 1
        return ("char", ch)

    tree = parse_alt()
    if pos[0] != len(pattern):
        raise ValueError(f"unexpected {pattern[pos[0]]!r} at position {pos[0]}")
    return tree


def literals(tree):
    """The set of characters the pattern can match."""
    kind = tree[0]
    if kind == "char":
        return {tree[1]}
    if kind == "eps":
        return set()
    if kind in ("cat", "alt"):
        return literals(tree[1]) | literals(tree[2])
    return literals(tree[1])


# ------------------------------------------------------------------ automata
class NFA:
    """A Thompson fragment: integer states, one entry, one exit."""

    def __init__(self, n, start, accept, trans):
        self.n = n
        self.start = start
        self.accept = accept
        self.trans = trans  # {(state, symbol): set(states)}, "" is epsilon

    def closure(self, states):
        """The epsilon closure of a set of states, as a frozenset."""
        seen = set(states)
        stack = list(seen)
        while stack:
            q = stack.pop()
            for nxt in self.trans.get((q, ""), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return frozenset(seen)

    def move(self, states, symbol):
        """Read one real symbol from a set of states, then close."""
        landed = set()
        for q in states:
            landed |= self.trans.get((q, symbol), set())
        return self.closure(landed)

    def fullmatch(self, word):
        """True when the whole word is accepted."""
        current = self.closure({self.start})
        for ch in word:
            current = self.move(current, ch)
            if not current:
                return False
        return self.accept in current


def thompson(tree):
    """Compile a syntax tree into an NFA."""
    trans = {}
    counter = [0]

    def fresh():
        counter[0] += 1
        return counter[0] - 1

    def link(a, symbol, b):
        trans.setdefault((a, symbol), set()).add(b)

    def build(node):
        kind = node[0]
        if kind == "eps":
            s, t = fresh(), fresh()
            link(s, "", t)
            return s, t
        if kind == "char":
            s, t = fresh(), fresh()
            link(s, node[1], t)
            return s, t
        if kind == "cat":
            s1, t1 = build(node[1])
            s2, t2 = build(node[2])
            link(t1, "", s2)  # the join costs no states
            return s1, t2
        if kind == "alt":
            s, t = fresh(), fresh()
            s1, t1 = build(node[1])
            s2, t2 = build(node[2])
            link(s, "", s1)
            link(s, "", s2)
            link(t1, "", t)
            link(t2, "", t)
            return s, t
        if kind in ("star", "plus", "opt"):
            s, t = fresh(), fresh()
            s1, t1 = build(node[1])
            link(s, "", s1)
            link(t1, "", t)
            if kind != "plus":
                link(s, "", t)      # skip the body
            if kind != "opt":
                link(t1, "", s1)    # go round again
            return s, t
        raise ValueError(f"unknown node {node!r}")

    start, accept = build(tree)
    return NFA(counter[0], start, accept, trans)


class DFA:
    """A total deterministic automaton with integer states 0..n-1."""

    def __init__(self, n, alphabet, delta, start, accepting):
        self.n = n
        self.alphabet = tuple(sorted(alphabet))
        self.delta = dict(delta)
        self.start = start
        self.accepting = set(accepting)
        for q in range(n):
            for a in self.alphabet:
                if (q, a) not in self.delta:
                    raise ValueError(f"delta is not total: no entry for {(q, a)!r}")

    def accepts(self, word):
        """True when the automaton ends in an accepting state."""
        q = self.start
        for ch in word:
            if ch not in self.alphabet:
                raise ValueError(f"symbol {ch!r} is not in the alphabet {self.alphabet!r}")
            q = self.delta[(q, ch)]
        return q in self.accepting

    def signature(self):
        """A canonical value: equal signatures mean identical machines."""
        return (self.n, self.alphabet, self.start,
                tuple(sorted(self.accepting)), tuple(sorted(self.delta.items())))


def _rename(start_key, successor, alphabet, is_accepting):
    """Breadth-first renaming shared by to_dfa, minimise and intersect."""
    index = {start_key: 0}
    order = [start_key]
    queue = deque([start_key])
    while queue:
        key = queue.popleft()
        for ch in alphabet:
            nxt = successor(key, ch)
            if nxt not in index:
                index[nxt] = len(order)
                order.append(nxt)
                queue.append(nxt)
    delta = {}
    for key in order:
        for ch in alphabet:
            delta[(index[key], ch)] = index[successor(key, ch)]
    accepting = {index[key] for key in order if is_accepting(key)}
    return DFA(len(order), alphabet, delta, 0, accepting)


def to_dfa(nfa, alphabet):
    """Subset construction, renamed breadth-first to integer states."""
    alphabet = tuple(sorted(alphabet))
    cache = {}

    def successor(subset, ch):
        key = (subset, ch)
        if key not in cache:
            cache[key] = nfa.move(subset, ch)
        return cache[key]

    start = nfa.closure({nfa.start})
    return _rename(start, successor, alphabet, lambda s: nfa.accept in s)


def minimise(dfa):
    """The unique minimal DFA for the same language, canonically numbered."""
    # Reachability first: an unreachable state would survive refinement.
    live = {dfa.start}
    queue = deque([dfa.start])
    while queue:
        q = queue.popleft()
        for ch in dfa.alphabet:
            nxt = dfa.delta[(q, ch)]
            if nxt not in live:
                live.add(nxt)
                queue.append(nxt)

    block = {q: (0 if q in dfa.accepting else 1) for q in live}
    while True:
        sig = {q: (block[q], tuple(block[dfa.delta[(q, ch)]] for ch in dfa.alphabet))
               for q in live}
        groups = {}
        for q in live:
            groups.setdefault(sig[q], []).append(q)
        if len(groups) == len(set(block.values())):
            break
        block = {q: i for i, key in enumerate(sorted(groups)) for q in groups[key]}

    rep = {}
    for q in live:
        rep.setdefault(block[q], q)

    def successor(b, ch):
        return block[dfa.delta[(rep[b], ch)]]

    return _rename(block[dfa.start], successor, dfa.alphabet,
                   lambda b: rep[b] in dfa.accepting)


# ------------------------------------------------------------------ decisions
def equivalent(d1, d2):
    """True when two DFAs over the same alphabet accept the same language."""
    if d1.alphabet != d2.alphabet:
        raise ValueError(f"alphabets differ: {d1.alphabet!r} versus {d2.alphabet!r}")
    seen = {(d1.start, d2.start)}
    stack = [(d1.start, d2.start)]
    while stack:
        p, q = stack.pop()
        if (p in d1.accepting) != (q in d2.accepting):
            return False
        for ch in d1.alphabet:
            nxt = (d1.delta[(p, ch)], d2.delta[(q, ch)])
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return True


def is_empty(dfa):
    """True when no accepting state is reachable from the start."""
    return shortest_word(dfa) is None


def shortest_word(dfa):
    """The shortest accepted word, or None when the language is empty."""
    seen = {dfa.start}
    queue = deque([(dfa.start, "")])
    while queue:
        q, word = queue.popleft()
        if q in dfa.accepting:
            return word  # breadth-first over a sorted alphabet: this is the smallest
        for ch in dfa.alphabet:
            nxt = dfa.delta[(q, ch)]
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, word + ch))
    return None


def complement(dfa):
    """A DFA for the complement over the same alphabet."""
    # Correct only because to_dfa returns a total machine, dead state included.
    return DFA(dfa.n, dfa.alphabet, dfa.delta, dfa.start,
               set(range(dfa.n)) - dfa.accepting)


def intersect(d1, d2):
    """A DFA for the intersection. ValueError on differing alphabets."""
    if d1.alphabet != d2.alphabet:
        raise ValueError(f"alphabets differ: {d1.alphabet!r} versus {d2.alphabet!r}")

    def successor(pair, ch):
        return (d1.delta[(pair[0], ch)], d2.delta[(pair[1], ch)])

    return _rename((d1.start, d2.start), successor, d1.alphabet,
                   lambda pair: pair[0] in d1.accepting and pair[1] in d2.accepting)


# ------------------------------------------------------------------ facade
class Language:
    """A regular language, held as its minimal DFA."""

    def __init__(self, pattern, alphabet=None):
        self.pattern = pattern
        self.tree = parse(pattern)
        self.alphabet = tuple(sorted(literals(self.tree) if alphabet is None else alphabet))
        self.nfa = thompson(self.tree)
        self.dfa = minimise(to_dfa(self.nfa, self.alphabet))

    def matches(self, word):
        """True when word is in the language. Foreign symbols mean False, not an error."""
        if any(ch not in self.alphabet for ch in word):
            return False
        return self.dfa.accepts(word)

    def size(self):
        """The number of states in the minimal DFA."""
        return self.dfa.n

    def is_empty(self):
        """True when the language contains no word at all."""
        return is_empty(self.dfa)

    def shortest(self):
        """The shortest member, or None."""
        return shortest_word(self.dfa)

    def equivalent(self, other):
        """True when both denote the same language, over the union of the alphabets."""
        union = tuple(sorted(set(self.alphabet) | set(other.alphabet)))
        mine = minimise(to_dfa(thompson(self.tree), union))
        theirs = minimise(to_dfa(thompson(other.tree), union))
        return equivalent(mine, theirs)
'''},
            {"name": "main.py", "content": r'''
from regtool import Language

abb = Language("(a|b)*abb")
same = Language("(a|b)*abb|(a|b)*abb")
plus = Language("a+", "ab")

print("states  ", abb.size())
print("shortest", abb.shortest())
print("equal   ", abb.equivalent(same))
print("a+ vs a*", plus.equivalent(Language("a*", "ab")))
'''},
        ],
        "tests": [
            {"name": "the parser handles precedence, escapes and errors", "code": r'''
from regtool import parse, literals

assert parse("") == ("eps",), f"got {parse('')!r}"
assert parse("abc") == ("cat", ("cat", ("char", "a"), ("char", "b")), ("char", "c")), \
    f"concatenation folds left, got {parse('abc')!r}"
assert parse("ab|c") == ("alt", ("cat", ("char", "a"), ("char", "b")), ("char", "c")), \
    f"got {parse('ab|c')!r}"
assert parse("ab*") == ("cat", ("char", "a"), ("star", ("char", "b"))), f"got {parse('ab*')!r}"
assert parse("\\|") == ("char", "|"), f"got {parse('\\|')!r}"
assert literals(parse("(a|b)*abb")) == {"a", "b"}, f"got {literals(parse('(a|b)*abb'))!r}"
assert literals(parse("")) == set(), "epsilon matches no character"
for _bad in ["(a", "a)", "*a", "+", "a\\", "((a)"]:
    try:
        parse(_bad)
        assert False, f"parse({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Thompson stays linear and matches correctly", "code": r'''
import itertools as _it
from regtool import parse, thompson

for _p in ["", "a", "abc", "(a|b)*abb", "a*b+c?", "((ab)|c)*", "(a?b?)*"]:
    _nfa = thompson(parse(_p))
    assert _nfa.n <= 2 * len(_p) + 2, (
        f"{_p!r} built {_nfa.n} states, Thompson allows at most {2 * len(_p) + 2}")
_nfa = thompson(parse("(a|b)*abb"))
for _w, _want in [("abb", True), ("babb", True), ("abba", False), ("", False)]:
    assert _nfa.fullmatch(_w) == _want, f"(a|b)*abb on {_w!r} gave {_nfa.fullmatch(_w)!r}"
assert thompson(parse("")).fullmatch("") is True
assert thompson(parse("a+")).fullmatch("") is False
assert thompson(parse("a*")).fullmatch("") is True
'''},
            {"name": "to_dfa is total and agrees with the NFA", "code": r'''
import itertools as _it
from regtool import parse, thompson, to_dfa, literals

for _p in ["", "a", "(a|b)*abb", "a*b+c?", "((ab)|c)*", "a|b|c", "(a?b?)*", "(ab)+"]:
    _tree = parse(_p)
    _alpha = tuple(sorted(literals(_tree) | {"a", "b"}))
    _nfa = thompson(_tree)
    _d = to_dfa(_nfa, _alpha)
    assert _d.start == 0, f"the start state must be 0, got {_d.start!r}"
    assert set(range(_d.n)) == {_q for _q, _ in _d.delta} | {0}, "states must be 0..n-1"
    for _q in range(_d.n):
        for _c in _alpha:
            assert (_q, _c) in _d.delta, f"delta is missing {(_q, _c)!r} for {_p!r}"
    for _k in range(6):
        for _tup in _it.product(_alpha, repeat=_k):
            _w = "".join(_tup)
            assert _nfa.fullmatch(_w) == _d.accepts(_w), (
                f"pattern {_p!r} on {_w!r}: NFA says {_nfa.fullmatch(_w)!r}, "
                f"DFA says {_d.accepts(_w)!r}")
'''},
            {"name": "minimise is minimal, canonical and idempotent", "code": r'''
from regtool import Language, parse, thompson, to_dfa, minimise

_abb = Language("(a|b)*abb")
assert _abb.size() == 4, f"the minimal DFA for (a|b)*abb has 4 states, you built {_abb.size()}"
_same = Language("(a|b)*abb|(a|b)*abb")
assert _abb.dfa.signature() == _same.dfa.signature(), (
    "two patterns for the same language must minimise to the identical machine")
assert minimise(_abb.dfa).signature() == _abb.dfa.signature(), "minimise must be idempotent"
_d = minimise(to_dfa(thompson(parse("a*")), "a"))
assert _d.n == 1 and _d.accepting == {0}, f"a* over {{a}} is one accepting state, got {_d.n}"
_d2 = minimise(to_dfa(thompson(parse("a+")), "a"))
assert _d2.n == 2, f"a+ over {{a}} needs two states, got {_d2.n}"
_d3 = minimise(to_dfa(thompson(parse("")), "ab"))
assert _d3.n == 2 and _d3.accepting == {0}, (
    f"the language {{epsilon}} over {{a,b}} is an accepting start plus a dead state, got {_d3.n}")
'''},
            {"name": "matching agrees with an independent oracle", "code": r'''
import itertools as _it
import re as _re
from regtool import Language

_patterns = ["", "a", "ab", "a|b", "ab|c", "(a|b)*abb", "a*b+c?", "((ab)|c)*",
             "a|b|c", "(a?b?)*", "(ab)+", "a(b|c)*d", "(a*)*b", "abc|ab|a"]
for _p in _patterns:
    _lang = Language(_p, "abcd")
    for _k in range(6):
        for _tup in _it.product("abcd", repeat=_k):
            _w = "".join(_tup)
            _want = _re.fullmatch(_p, _w) is not None
            _got = _lang.matches(_w)
            assert _got == _want, (
                f"pattern {_p!r} on {_w!r}: you said {_got!r}, re says {_want!r}")
'''},
            {"name": "equivalence over one alphabet", "code": r'''
from regtool import Language, parse, thompson, to_dfa, minimise, equivalent

_pairs = [("(a|b)*", "(a*b*)*", True),
          ("(a|b)*abb", "(a|b)*abb|(a|b)*abb", True),
          ("a*", "a+", False),
          ("a|b", "b|a", True),
          ("(ab)*", "a(ba)*b|", True),
          ("abc", "ab", False)]
for _p, _q, _want in _pairs:
    _d1 = minimise(to_dfa(thompson(parse(_p)), "ab" + "c" * ("c" in _p + _q)))
    _d2 = minimise(to_dfa(thompson(parse(_q)), "ab" + "c" * ("c" in _p + _q)))
    _got = equivalent(_d1, _d2)
    assert _got == _want, f"{_p!r} versus {_q!r}: you said {_got!r}, expected {_want}"
try:
    equivalent(minimise(to_dfa(thompson(parse("a")), "a")),
               minimise(to_dfa(thompson(parse("a")), "ab")))
    assert False, "differing alphabets must raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Language.equivalent reconciles the alphabets", "code": r'''
from regtool import Language

assert Language("a*").equivalent(Language("a*", "ab")) is True, (
    "the same language written over a larger alphabet is still the same language")
assert Language("a*", "ab").equivalent(Language("a*", "abc")) is True
assert Language("a").equivalent(Language("b")) is False, "different alphabets, different languages"
assert Language("(a|b)*").equivalent(Language("(a*b*)*")) is True
assert Language("a+").equivalent(Language("a*")) is False
assert Language("").equivalent(Language("a*")) is False, "{epsilon} is a proper subset of a*"
'''},
            {"name": "emptiness and the shortest member", "code": r'''
from regtool import Language, intersect, is_empty, shortest_word

_abb = Language("(a|b)*abb")
assert _abb.shortest() == "abb", f"got {_abb.shortest()!r}"
assert _abb.is_empty() is False
assert Language("").shortest() == "", "the language {epsilon} has the empty word as its member"
assert Language("a*", "ab").shortest() == ""
assert Language("b(a|b)*", "ab").shortest() == "b", f"got {Language('b(a|b)*', 'ab').shortest()!r}"
_only_a = Language("a+", "ab")
_only_b = Language("b+", "ab")
_both = intersect(_only_a.dfa, _only_b.dfa)
assert is_empty(_both) is True, "a+ and b+ share no word at all"
assert shortest_word(_both) is None, "an empty language has no shortest member"
_mixed = intersect(Language("(a|b)*a", "ab").dfa, Language("a(a|b)*", "ab").dfa)
assert shortest_word(_mixed) == "a", f"got {shortest_word(_mixed)!r}"
'''},
            {"name": "complement flips exactly the right words", "code": r'''
import itertools as _it
from regtool import Language, complement

for _p in ["(a|b)*abb", "a*", "a+b*", "(ab)*"]:
    _lang = Language(_p, "ab")
    _c = complement(_lang.dfa)
    for _k in range(6):
        for _tup in _it.product("ab", repeat=_k):
            _w = "".join(_tup)
            assert _c.accepts(_w) == (not _lang.dfa.accepts(_w)), (
                f"complement of {_p!r} disagrees on {_w!r}")
assert complement(complement(Language("a*", "ab").dfa)).accepts("aa") is True, \
    "complementing twice returns the original language"
'''},
            {"name": "intersect is the product, and its alphabet must match", "code": r'''
import itertools as _it
from regtool import Language, intersect

_a = Language("(a|b)*a", "ab")
_b = Language("a(a|b)*", "ab")
_p = intersect(_a.dfa, _b.dfa)
assert _p.start == 0, f"the product must be renumbered from 0, got {_p.start!r}"
for _k in range(6):
    for _tup in _it.product("ab", repeat=_k):
        _w = "".join(_tup)
        assert _p.accepts(_w) == (_a.dfa.accepts(_w) and _b.dfa.accepts(_w)), (
            f"the product disagrees on {_w!r}")
try:
    intersect(Language("a").dfa, Language("b").dfa)
    assert False, "differing alphabets must raise ValueError"
except ValueError:
    pass
'''},
            {"name": "matches, size and foreign symbols", "code": r'''
from regtool import Language

_l = Language("a*")
assert _l.alphabet == ("a",), f"the default alphabet is the pattern's literals, got {_l.alphabet!r}"
assert _l.matches("aaa") is True
assert _l.matches("b") is False, "a foreign symbol means the word is not in the language"
assert _l.matches("aab") is False
_wide = Language("a*", "ab")
assert _wide.matches("b") is False and _wide.size() == 2, (
    f"over {{a,b}} the machine needs a dead state, got {_wide.size()} states")
_one = Language("a*")
_two = Language("a*")
assert _one.dfa is not _two.dfa, "two Language objects must not share a compiled machine"
'''},
            {"name": "regtool.py is import-clean and main.py reports", "code": r'''
_src = open("regtool.py").read()
assert "print(" not in _src, "regtool.py is a library; the printing belongs in main.py"
assert "import re" not in _src, "you are implementing regular expressions, not importing them"
assert "states" in _out and "shortest" in _out, (
    f"main.py should print the toolkit's findings; stdout was {_out!r}")
'''},
        ],
    },
}
