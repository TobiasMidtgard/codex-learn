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
            "quiz": {
                "title": "Determinism, classes, and the smallest machine",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What makes a finite automaton *deterministic*?",
                        "opts": [
                            "No state is visited twice during a run",
                            "Every state is reachable from the start state",
                            "`delta` is a total function: exactly one arrow leaves every state on every symbol",
                            "Exactly one state is accepting",
                        ],
                        "a": 2,
                        "why": """
Determinism is a property of `delta` and nothing else: one arrow out of every state
for every letter, never two and never none. That is why `_validate` walks the whole
cross product of states and alphabet — a machine missing a single entry has a word it
cannot even finish reading. Revisiting a state is entirely ordinary, and in fact
unavoidable: a loop is how a DFA counts modulo something. Reachability is a tidiness
property that minimisation cleans up and that never changes the language. And the
accepting set may be any size at all, including empty, which is the machine for the
language containing no word.
""",
                    },
                    {
                        "q": "Myhill-Nerode: two words `u` and `v` reach the same state of the minimal DFA exactly when...",
                        "opts": [
                            "`u` and `v` are the same length",
                            "for every word `z`, `uz` is in the language exactly when `vz` is",
                            "`u` and `v` are both in the language, or both outside it",
                            "one of `u` and `v` is a suffix of the other",
                        ],
                        "a": 1,
                        "why": """
The state a word reaches is a summary of everything about that word that still
matters, and what still matters is exactly which continuations lead to acceptance.
Agreeing on membership alone is the special case `z = ""`, and it is not enough: take
the language of words ending in `01`. Neither `0` nor `1` is in it, yet appending `1`
puts `01` in the language and leaves `11` outside, so they belong to different
classes. Length is irrelevant — a DFA cannot count without spending a state per count
— and the suffix relation is not even an equivalence.
""",
                    },
                    {
                        "q": "Moore's refinement starts from the partition `{accepting, non-accepting}`. When does a block split?",
                        "opts": [
                            "When it holds more than one state",
                            "When it holds the start state and something else",
                            "When two states in it have different numbers of incoming arrows",
                            "When two states in it send some symbol into different blocks",
                        ],
                        "a": 3,
                        "why": """
A block is a claim that its members are indistinguishable so far. The claim breaks the
moment two members disagree about where they *go*: if `p` and `q` both read `a` and
land in blocks already known to be different, then some word separates them, and one
more letter separates `p` from `q`. That is the whole algorithm — compute each state's
signature `(current block, blocks it moves to)` and regroup. Blocks are never merged,
only cut, which is why the process stops: there are at most `|Q|` blocks to reach.
Incoming arrows never enter into it; the future is what distinguishes states, not the
past.
""",
                    },
                    {
                        "q": "Why must unreachable states be dropped *before* refinement rather than after?",
                        "opts": [
                            "Refinement fails to terminate while unreachable states are present",
                            "An unreachable state can be distinguishable from every reachable one, so refinement keeps it as its own block and the result is not minimal",
                            "An unreachable state makes `delta` partial, so the machine is not a DFA",
                            "It is purely a speed optimisation — the state count comes out the same either way",
                        ],
                        "a": 1,
                        "why": """
Refinement asks whether two states behave the same, and an unreachable state behaves
perfectly well; it simply never happens. The machine in the checks makes this concrete:
`s <-> t` over `a` with `u` an accepting self-loop nobody can reach. Refine without
pruning and `t` and `u` split apart on the first round, leaving three states for a
language that needs two. Termination is never at risk — each round only cuts — and
`delta` stays total whether or not a state is reachable. The count really does differ,
which is why the pruning is a step of the algorithm and not an optimisation.
""",
                    },
                    {
                        "q": "`equivalent` walks two DFAs in lock-step and stops at the first pair whose acceptance disagrees. Why is that decision procedure correct *and* terminating?",
                        "opts": [
                            "It examines every word up to the length of the larger machine, which is enough",
                            "It relies on both machines having been minimised first",
                            "A pair of states is reached exactly by the words that drive both machines there, and there are only finitely many pairs to reach",
                            "It works only when the two machines have the same number of states",
                        ],
                        "a": 2,
                        "why": """
The product machine has at most `|Q1| * |Q2|` states, so the search runs out of new
pairs and halts. Correctness is the other half: reaching a pair where one machine
accepts and the other does not means there is a word accepted by exactly one of them,
which is a counterexample; and if no such pair is reachable, no word distinguishes
them. Nothing needs minimising first — comparing canonical minimal forms is a
different, equally valid method — and the two machines may be any sizes, since the
walk is over pairs rather than over some correspondence between states.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Refinement, one round at a time",
                "minutes": 9,
                "caption": "the inner loop of minimise() — four holes",
                "lang": "python",
                "brief": """
Partition refinement is six lines that are hard to write and easy to read once they
are right. The shape is: give every state a block id, compute a *signature* saying
where that state goes, regroup by signature, and stop when a round produces no new
blocks.

`live` is the set of reachable states, already pruned. Nothing runs here — you are
choosing expressions, not writing code.
""",
                "listing": r'''
# Moore's refinement, over the reachable states only.
# block[q] is the id of the block state q currently sits in.

block = {q: (0 if q in ___ else 1) for q in live}

while True:
    sig = {q: (block[q], tuple(___ for a in alphabet)) for q in live}
    groups = {}
    for q in live:
        groups.setdefault(___, []).append(q)
    if len(groups) == ___:
        break                    # a round that split nothing is the fixed point
    block = {q: i for i, key in enumerate(sorted(groups)) for q in groups[key]}
''',
                "blanks": [
                    {
                        "prompt": "What is the one distinction you get for free, before any refining?",
                        "hole": "?",
                        "opts": ["live", "accepting", "delta", "alphabet"],
                        "a": 1,
                        "why": "Acceptance is the only behaviour the machine hands you directly: the empty word already separates an accepting state from a rejecting one. Every later split is a refinement of that first cut.",
                        "whys": [
                            "`live` is the set being partitioned, not a property that distinguishes its members. Seeding every state into the same block would leave nothing for the first round to split on, and refinement would stop immediately with one block.",
                            "Acceptance is the only behaviour the machine hands you directly: the empty word already separates an accepting state from a rejecting one. Every later split is a refinement of that first cut.",
                            "`delta` is where the states *go*, which is what the signature uses one line further down. Starting from it would prejudge the very thing refinement is meant to discover.",
                            "The alphabet says which symbols exist, not which states behave alike. A state is not distinguished by the letters available to it — every state has all of them.",
                        ],
                    },
                    {
                        "prompt": "The signature has to say where `q` goes on each symbol — but at what resolution?",
                        "hole": "?",
                        "opts": ["delta[(q, a)]", "block[delta[(q, a)]]", "block[q]", "a"],
                        "a": 1,
                        "why": "The destination *block*, not the destination state. Two states are still indistinguishable if they move to different states that nothing has yet told apart; comparing raw destinations would split every pair immediately and return the machine you started with.",
                        "whys": [
                            "The raw destination state is too fine. Two equivalent states almost never move to the *same* state — they move to states that are themselves equivalent — so this splits every block on the first round and the machine never shrinks.",
                            "The destination *block*, not the destination state. Two states are still indistinguishable if they move to different states that nothing has yet told apart; comparing raw destinations would split every pair immediately and return the machine you started with.",
                            "That is `q`'s own block, which is already the first component of the signature. Repeating it says nothing about where the symbol takes you, and the tuple would be the same for every state in a block forever.",
                            "The symbol itself is the same for every state, so the tuple would be identical everywhere and no block would ever split. The loop variable is what you index *with*, not what you record.",
                        ],
                    },
                    {
                        "prompt": "States are regrouped by what?",
                        "hole": "?",
                        "opts": ["sig[q]", "block[q]", "q", "len(groups)"],
                        "a": 0,
                        "why": "By the signature just computed. Two states land in the same new block exactly when they agree on their current block and on the block each symbol takes them to — which is the definition of surviving this round together.",
                        "whys": [
                            "By the signature just computed. Two states land in the same new block exactly when they agree on their current block and on the block each symbol takes them to — which is the definition of surviving this round together.",
                            "Grouping by the current block reproduces the partition unchanged, so the loop would compare the same numbers forever and break on the first round with the split into accepting and non-accepting.",
                            "Grouping by the state itself gives one group per state — the discrete partition. That is the largest machine, not the smallest, and it is exactly what minimisation is meant to avoid.",
                            "That is a count, and it changes as the dictionary is filled. Using it as a key would scatter states into groups by the accident of iteration order.",
                        ],
                    },
                    {
                        "prompt": "The loop stops when a round changes nothing. What does `len(groups)` have to be compared against?",
                        "hole": "?",
                        "opts": ["len(live)", "len(set(block.values()))", "len(alphabet)", "1"],
                        "a": 1,
                        "why": "The number of blocks you already had. If regrouping produced no more groups than there were blocks, no block was cut, the partition is stable, and the classes you are holding are the Myhill-Nerode classes.",
                        "whys": [
                            "The number of states. That test asks whether every state has ended up alone, which happens only for a machine that was already minimal *and* had no two equivalent states — so most machines would loop until they hit it, which they never do.",
                            "The number of blocks you already had. If regrouping produced no more groups than there were blocks, no block was cut, the partition is stable, and the classes you are holding are the Myhill-Nerode classes.",
                            "The alphabet size has nothing to do with how many blocks the partition has settled into; a two-letter machine can have any number of classes.",
                            "Stopping at a single block would mean stopping only when every state is equivalent to every other — true only for the machines accepting everything or nothing.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How small does *contains 0101* get?",
                "minutes": 8,
                "brief": """
There is an obvious automaton for this language: remember the last four symbols you
read, and accept once that window has ever been `0101`. Sixteen windows, so sixteen
states plus a little bookkeeping at the start.

Myhill-Nerode says the minimal machine has one state per *class of futures* — and two
different windows can have exactly the same future. `1111` and `1011` are different
windows, but from either of them the words that finish the job are the same, so they
cannot be distinguished by any continuation and the minimal machine cannot afford to
keep them apart.

Work out the classes, not the windows.
""",
                "prompt": "How many states does the minimal DFA for this language have?",
                "note": "Count the states of the smallest machine, not of the first one that comes to mind.",
                "figure": "**L** = every word over `{0, 1}` that contains `0101` somewhere inside it. "
                          "So `0101`, `110100`, `001011` are in **L**; `0011`, `0110`, `1010` are not. "
                          "The automaton reads left to right, one pass, no lookahead.",
                "given": [
                    {"label": "Alphabet", "value": "`{0, 1}`"},
                    {"label": "Pattern to find", "value": "`0101`, as a substring"},
                    {"label": "Naive machine", "value": "remember the last 4 symbols: 16 windows"},
                    {"label": "Wanted", "value": "states of the *minimal* DFA"},
                ],
                "aside": "Once the pattern has been seen the machine can stop paying attention: "
                         "acceptance is permanent, so that class is a sink.",
                "answer": 5,
                "tol": 0.5,
                "unit": "states",
                "hint": "The only thing worth remembering is how much of `0101` the word currently "
                        "ends with. List the possible answers to that question, including *none of it* "
                        "and *the whole thing, already*.",
                "wrong": "If you counted 16 you counted windows. Two words with different last-four "
                         "symbols can still have identical futures, and Myhill-Nerode merges those. "
                         "If you counted 4 you forgot that *nothing matched yet* is itself a state.",
                "why": """
Five. The classes are indexed by the longest suffix of what you have read that is also
a prefix of `0101`: the empty match, `0`, `01`, `010`, and `0101` — the last of which is
a sink, because the pattern cannot be un-seen. They are pairwise distinguishable
because each needs a different shortest completion: 4, 3, 2, 1 and 0 more symbols
respectively, and two states that need different numbers of symbols to reach acceptance
cannot be the same class. They are all reachable, by the words `""`, `0`, `01`, `010`,
`0101`. So the machine is exactly five states — and this generalises: searching for a
pattern of length `p` costs `p + 1` states, not `2^p`. That collapse from 16 to 5 is
the same fact the Knuth-Morris-Pratt failure function exploits.
""",
            },
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
            "quiz": {
                "title": "Guessing, closing, and the price of removing the guess",
                "minutes": 7,
                "questions": [
                    {
                        "q": "An NFA accepts a word when...",
                        "opts": [
                            "every run over that word ends in an accepting state",
                            "the shortest run over that word ends in an accepting state",
                            "the machine has no choices left to make when the word runs out",
                            "some run over that word ends in an accepting state",
                        ],
                        "a": 3,
                        "why": """
Acceptance is existential — one successful run is enough, and the other runs may dead-end,
reject, or wander. That single word, *some*, is what the subset simulation encodes: carry
the whole set of states any run could be in, and ask at the end whether the set meets the
accepting set. Requiring *every* run to accept defines a different and genuinely different
machine (a co-NFA), and the shortest run is not even well defined when epsilon moves let
runs have different lengths on the same word.
""",
                    },
                    {
                        "q": "Why is the epsilon closure of a set always a superset of that set?",
                        "opts": [
                            "Because every state has an epsilon self-loop",
                            "Because epsilon moves always come in pairs, one each way",
                            "It is defined as the least set that both contains those states and is closed under epsilon moves",
                            "It is not — closing drops any state with no epsilon moves",
                        ],
                        "a": 2,
                        "why": """
Being a superset is half the definition, not a theorem: the closure is the least fixed
point of *add every epsilon successor*, seeded with the states you started from. The
worklist implementation makes that literal — `seen` begins as the input set and only ever
grows. A state with no epsilon moves is its own closure, which is why the checks assert
`ABB.epsilon_closure({0, 3}) == {0, 3}`. Epsilon edges are directed like any other, so no
symmetry is on offer, and no machine is required to carry self-loops on them.
""",
                    },
                    {
                        "q": "In the subset construction, when is a subset an accepting state of the DFA?",
                        "opts": [
                            "When every state in it is accepting",
                            "When it shares at least one state with the NFA's accepting set",
                            "When it is the epsilon closure of some accepting state",
                            "When it contains both the start state and an accepting state",
                        ],
                        "a": 1,
                        "why": """
The subset is the set of states some run could be in. If any one of them accepts, then
some run accepts, and the word is in the language — so the test is intersection, written
`s & nfa.accepting`. Demanding that all of them accept is the containment test `s <=
accepting`, and it rejects words the NFA plainly accepts: for the `(a|b)*abb` machine the
subset after `abb` is `{0, 3}`, which is accepting even though `0` is not. The start state
has no special role here; it turns up in many subsets simply because it has a self-loop.
""",
                    },
                    {
                        "q": "The empty subset shows up as a state of the constructed DFA. What is it doing there?",
                        "opts": [
                            "It marks the end of the input word",
                            "It is the closure of the start state when the start has no epsilon moves",
                            "It is accepting, because there is nothing left to reject",
                            "It is the dead state — `delta` must be total, so a subset with nowhere to go still needs a destination",
                        ],
                        "a": 3,
                        "why": """
A DFA has to have an answer for every state and symbol, and *the run died* is an answer:
it is the empty set of possible states, and it loops to itself forever because nothing can
revive a dead run. It is never accepting — the empty set meets nothing, least of all the
accepting set. Machines that can never get stuck simply never reach it, which is why
determinising `(a|b)*abb` gives four subsets and none of them empty.
""",
                    },
                    {
                        "q": "An NFA has `n` states. What is true of the DFA the subset construction produces?",
                        "opts": [
                            "Exactly `2^n` states, always",
                            "At most `2^n` states, and for some machines the count really does grow exponentially in `n`",
                            "At most `n^2` states",
                            "At most `2^n` in theory, but no machine has ever been found needing more than `n`",
                        ],
                        "a": 1,
                        "why": """
`2^n` is an upper bound because there are that many subsets, and the construction builds
only the ones it can reach — for most machines a handful. But the bound is not idle. The
`(k+1)`-state NFA for *the k-th symbol from the end is an a* determinises to `2^k` subsets,
every one reachable, and minimisation removes none of them because every one is its own
Myhill-Nerode class. So the blow-up is a property of the language, not of a clumsy
construction, and no cleverer algorithm avoids it.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Closure and determinisation, hole by hole",
                "minutes": 9,
                "caption": "the two functions that turn a guess into a table",
                "lang": "python",
                "brief": """
Two worklist loops with different jobs. The first one chases epsilon edges until nothing
new turns up; the second one chases *subsets* until nothing new turns up. They look alike
on purpose — both are computing a least fixed point — and both are one wrong expression
away from a machine that quietly disagrees with the one it came from.

Nothing runs here. Pick the expression each hole wants.
""",
                "listing": r'''
EPSILON = ""


# lifted out of the NFA class, so `self` is the machine being closed over
def epsilon_closure(self, states):
    seen = set(states)
    stack = list(seen)
    while stack:
        q = stack.pop()
        for nxt in self.moves(q, ___):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return frozenset(seen)


def subset_construction(nfa):
    start = nfa.epsilon_closure({___})
    states, delta, queue = {start}, {}, deque([start])
    while queue:
        subset = queue.popleft()
        for ch in nfa.alphabet:
            nxt = ___
            delta[(subset, ch)] = nxt
            if nxt not in states:
                states.add(nxt)
                queue.append(nxt)
    accepting = {s for s in states if ___}
    return DFA(states, nfa.alphabet, delta, start, accepting)
''',
                "blanks": [
                    {
                        "prompt": "The closure follows one kind of edge and only that kind.",
                        "hole": "?",
                        "opts": ["q", "EPSILON", "self.alphabet", "nxt"],
                        "a": 1,
                        "why": "Epsilon edges are the free moves — the ones a run may take without consuming input — and the closure exists precisely to take all of them at once. Reading a real symbol here would consume input inside a function whose contract is that it consumes none.",
                        "whys": [
                            "`q` is the state being expanded, not the symbol being followed. Passing it as the symbol asks for transitions labelled with a state name, which no machine has, so the closure would return its input unchanged.",
                            "Epsilon edges are the free moves — the ones a run may take without consuming input — and the closure exists precisely to take all of them at once. Reading a real symbol here would consume input inside a function whose contract is that it consumes none.",
                            "The alphabet is a tuple of symbols, not one symbol. `moves` looks up a single key, and a tuple is not one, so every lookup would miss and the closure would be the identity.",
                            "`nxt` is the loop variable being bound by this very line — it does not exist yet when the call is made.",
                        ],
                    },
                    {
                        "prompt": "Where does the determinised machine begin?",
                        "hole": "?",
                        "opts": ["nfa.start", "nfa.states", "nfa.accepting", "0"],
                        "a": 0,
                        "why": "At the closure of the start state alone. Before a single symbol is read the machine has already taken every free move available to it, which is why `CHAIN` determinises to a start subset of `{0, 1, 2}`.",
                        "whys": [
                            "At the closure of the start state alone. Before a single symbol is read the machine has already taken every free move available to it, which is why `CHAIN` determinises to a start subset of `{0, 1, 2}`.",
                            "The whole state set is the subset a machine is in when *every* state is possible, which is not where a run begins. Starting there accepts far too much: any word reaching acceptance from anywhere would be accepted.",
                            "The accepting set is where runs are meant to end. Beginning there builds a machine for a different language entirely — roughly, the words that can be read starting from an accepting state.",
                            "State `0` happens to be the start of the two example machines, but the function takes any NFA and the field is there to be read. Hard-coding it breaks on the first machine whose states are named anything else.",
                        ],
                    },
                    {
                        "prompt": "One symbol takes one subset to the next. Which call does the move *and* the closing?",
                        "hole": "?",
                        "opts": ["nfa.moves(subset, ch)", "nfa.epsilon_closure(subset)", "nfa.step(subset, ch)", "subset | {ch}"],
                        "a": 2,
                        "why": "`step` is the composite: gather every successor on `ch`, then epsilon-close the result. Doing it in that order matters — closing first and moving afterwards would leave the free moves *after* the symbol untaken, so a word ending in an epsilon hop to acceptance would be rejected.",
                        "whys": [
                            "`moves` handles one state, not a set, and it does no closing. Every run that finishes with a free move would be lost, and the DFA would reject words the NFA accepts.",
                            "Closing without moving never consumes the symbol, so the machine would sit in the same subset forever and accept on the strength of the empty word alone.",
                            "`step` is the composite: gather every successor on `ch`, then epsilon-close the result. Doing it in that order matters — closing first and moving afterwards would leave the free moves *after* the symbol untaken, so a word ending in an epsilon hop to acceptance would be rejected.",
                            "That mixes a set of states with a symbol. The subsets are sets of NFA states; putting a letter in one makes a key nothing else will ever match.",
                        ],
                    },
                    {
                        "prompt": "Which subsets accept?",
                        "hole": "?",
                        "opts": ["s & nfa.accepting", "s <= nfa.accepting", "nfa.accepting <= s", "s == nfa.accepting"],
                        "a": 0,
                        "why": "A non-empty intersection: one accepting state in the subset means one accepting run, and one accepting run is acceptance. The other tests all ask for more than the NFA does.",
                        "whys": [
                            "A non-empty intersection: one accepting state in the subset means one accepting run, and one accepting run is acceptance. The other tests all ask for more than the NFA does.",
                            "Containment demands that every possible run be accepting. The subset after `abb` on the `(a|b)*abb` machine is `{0, 3}`, which fails that test even though the word is plainly in the language.",
                            "This asks the subset to contain *all* accepting states at once. A machine with two accepting states would then accept only words that can reach both simultaneously.",
                            "Equality is stricter still, and it makes acceptance depend on which other states happen to be possible — so adding an unrelated accepting state to the machine would silently change which words are accepted.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Why determinising can cost exponentially",
                "minutes": 12,
                "vars": ["k", "n"],
                "brief": r'''
Fix $k \ge 1$ and let $N_k$ be this NFA over $\{a, b\}$, with states $0, 1, \dots, k$:

- state $0$ loops to itself on both letters, and on $a$ it *also* guesses forward to $1$;
- states $1$ through $k-1$ advance to the next state on either letter;
- state $k$ is accepting and has no outgoing transitions.

$N_k$ accepts exactly the words whose $k$-th symbol from the right-hand end is an $a$.
It has $k + 1$ states and the guess is doing all the work. The question is what
removing the guess costs.
''',
                "steps": [
                    {
                        "prompt": "Before worrying about which subsets are reachable: how many subsets does the state set of $N_k$ have? Write it in terms of $k$.",
                        "answer": "2^{k+1}",
                        "hint": "Each state is either in a given subset or out of it, and there are $k+1$ of them.",
                        "deconstruct": [
                            "A set with $j$ elements has $2^j$ subsets, counting the empty one.",
                            "$N_k$ has states $0$ through $k$, so $j = k + 1$.",
                        ],
                    },
                    {
                        "prompt": "State $0$ is the start and loops to itself on every letter, so it is in the current set after every word. The reachable subsets are therefore $\\{0\\}$ together with an arbitrary subset of $\\{1, \\dots, k\\}$. How many is that?",
                        "answer": "2^{k}",
                        "placeholder": "2^{?}",
                        "hint": "Membership of state $0$ is decided for you, so it contributes no choice. Count only the choices left.",
                        "deconstruct": [
                            "One of the $k+1$ binary choices has been fixed to *in*.",
                            "The remaining $k$ states are still free, giving $2^k$ subsets.",
                        ],
                    },
                    {
                        "prompt": "Now write that same count in terms of $n$, the number of states of the NFA, where $n = k + 1$.",
                        "answer": "2^{n-1}",
                        "hint": "Substitute $k = n - 1$ into what you just wrote.",
                        "deconstruct": [
                            "$n = k + 1$ rearranges to $k = n - 1$.",
                            "So the count $2^k$ becomes $2^{n-1}$.",
                        ],
                    },
                    {
                        "prompt": "Every one of those subsets is also a distinct Myhill-Nerode class, so minimisation removes none of them. Write the ratio of DFA states to NFA states as a function of $n$.",
                        "answer": "\\frac{2^{n-1}}{n}",
                        "hint": "Divide the DFA's state count by the NFA's.",
                        "deconstruct": [
                            "The DFA has $2^{n-1}$ states and the NFA has $n$.",
                            "The ratio is one over the other; it is not a difference, because the interesting thing is the factor.",
                        ],
                    },
                ],
                "closing": r'''
Put $k = 6$ in and the numbers stop being abstract: a seven-state NFA becomes a
sixty-four-state DFA, and $64/7 \approx 9$. Push $k$ to $20$ and the ratio is about
$50\,000$.

Two things are worth taking from this. The blow-up is *not* an artefact of the
construction — the last step is what closes that door, because a language needing
$2^{n-1}$ Myhill-Nerode classes needs $2^{n-1}$ DFA states no matter who builds the
machine. And the bound is an upper bound on every machine but a lower bound on almost
none: determinising a typical regular expression produces a DFA a little larger than the
NFA, not exponentially larger. Both facts are true at once, and knowing only the first
one is what makes people afraid of a construction they should be using.
''',
            },
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
            "quiz": {
                "title": "Precedence, fragments, and why backtracking is optional",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In this notation, how does `ab|c*` parse?",
                        "opts": [
                            "`a (b|c)*`",
                            "`(ab|c)*`",
                            "`(ab) | (c*)`",
                            "`a (b | c*)`",
                        ],
                        "a": 2,
                        "why": """
Three levels of precedence, tightest first: the postfix operators, then concatenation,
then union. So `c*` is formed before anything is concatenated to it, `ab` is formed
before anything is unioned with it, and `|` splits the pattern at the top. That is
exactly the shape of the grammar the parser walks — `alt` calls `concat` calls `repeat`
calls `atom` — and the descent order *is* the precedence. Anyone who wants the other
readings has to write the parentheses.
""",
                    },
                    {
                        "q": "Thompson's construction glues fragments together with epsilon moves. Why does concatenation allocate no new states?",
                        "opts": [
                            "Because concatenation is not one of the three regular operations",
                            "Because the two fragments are guaranteed to share a state already",
                            "Because the right fragment is copied into the left one instead of being linked",
                            "The left fragment's exit is joined to the right fragment's entry by an epsilon edge, and the pair already has one entry and one exit",
                        ],
                        "a": 3,
                        "why": """
Every fragment is built to the same contract: one entry, one exit, and no edges into the
entry or out of the exit from elsewhere. Concatenation needs a fragment with the same
contract, and `(entry of the left, exit of the right)` already satisfies it once you add
the epsilon edge from the left's exit to the right's entry. Union and the postfix
operators are different: they need a new entry to branch from and a new exit to merge
into, which is where the two states per operator come from.
""",
                    },
                    {
                        "q": "Why does simulating the NFA never suffer catastrophic backtracking?",
                        "opts": [
                            "Because the patterns this notation supports are too simple to be slow",
                            "It carries the whole set of currently possible states forward, so each input symbol is processed exactly once",
                            "Because it determinises the machine before matching",
                            "Because the epsilon moves are eliminated before matching starts",
                        ],
                        "a": 1,
                        "why": """
A backtracking matcher explores one run at a time and may try exponentially many before
finding the accepting one, which is why `(a?){20}a{20}` is a denial-of-service in some
engines. The set simulation explores all runs at once: one pass over the word, and at
each symbol a set of at most `|Q|` states is mapped to another. Nothing is determinised
in advance — the subsets are computed on the fly and thrown away — and the epsilon moves
are still there, taken by the closure at every step.
""",
                    },
                    {
                        "q": "Thompson's construction proves one direction of Kleene's theorem. Which one?",
                        "opts": [
                            "Every language a finite automaton accepts has a regular expression",
                            "Every context-free language has a regular expression",
                            "Every regular expression denotes a language that some finite automaton accepts",
                            "Regular expressions and Turing machines recognise the same languages",
                        ],
                        "a": 2,
                        "why": """
The construction takes a pattern and hands back a machine, so it establishes
*expressions are no more powerful than automata*. The converse — turning any automaton
back into an expression — is a separate construction (state elimination, or Kleene's own
recursion on paths), and together the two halves say the notations are interchangeable.
The other two claims are false, and interestingly so: `a^n b^n` is context-free with no
regular expression at all, and no finite automaton comes close to a Turing machine.
""",
                    },
                    {
                        "q": "In this notation `a|` is a legal pattern and it matches both `a` and the empty word. Why?",
                        "opts": [
                            "Because a trailing `|` is ignored by the parser",
                            "Because `|` is treated as optional when it ends a pattern",
                            "Because the parser inserts a `*` wherever a branch is missing",
                            "The right branch of the union is an empty concatenation, and an empty concatenation is the empty word",
                        ],
                        "a": 3,
                        "why": """
`parse_cat` stops at `|`, at `)` and at the end of the pattern. When it stops having
consumed nothing it returns `("eps",)`, and that is a real node with a real
two-state fragment, not an absence. So `a|` is `("alt", ("char", "a"), ("eps",))` and
denotes `{"a", ""}`. Python's `re` agrees, which is what makes the comparison against
`re.fullmatch` a fair test. It looks like a typo and it is a well-defined pattern —
worth knowing before you write a parser that rejects it.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The fragments, wired up",
                "minutes": 9,
                "caption": "thompson.build() — five holes across three node kinds",
                "lang": "python",
                "brief": """
`fresh()` hands out a new state id; `link(a, symbol, b)` adds `a --symbol--> b` and `""`
is the epsilon move. Every branch has to return `(entry, exit)` for a fragment that obeys
the contract: nothing else points into the entry, nothing else leads out of the exit.

Star, plus and opt share a shape and differ by exactly two edges — which is the neatest
thing in the whole construction and the easiest to get backwards.
""",
                "listing": r'''
def build(node):
    kind = node[0]

    if kind == "char":
        s, t = fresh(), fresh()
        link(s, ___, t)
        return s, t

    if kind == "cat":
        s1, t1 = build(node[1])
        s2, t2 = build(node[2])
        link(___, "", ___)
        return s1, t2

    if kind in ("star", "plus", "opt"):
        s, t = fresh(), fresh()
        s1, t1 = build(node[1])
        link(s, "", s1)
        link(t1, "", t)
        if kind != ___:
            link(s, "", t)      # skip the body entirely
        if kind != ___:
            link(t1, "", s1)    # go round again
        return s, t
''',
                "blanks": [
                    {
                        "prompt": "The two-state fragment for one literal. What labels its only edge?",
                        "hole": "?",
                        "opts": ["kind", "node[1]", '""', "node[0]"],
                        "a": 1,
                        "why": "The character itself, which the parser stored as the second element of the `('char', c)` tuple. This is the only place in the whole construction where a non-epsilon edge is created — every other edge is a free move.",
                        "whys": [
                            "`kind` is the string `\"char\"`, the node's tag. Labelling the edge with it would build a machine that matches the four-letter word `char` instead of the literal the pattern asked for.",
                            "The character itself, which the parser stored as the second element of the `('char', c)` tuple. This is the only place in the whole construction where a non-epsilon edge is created — every other edge is a free move.",
                            "An epsilon edge consumes nothing, so the fragment would match the empty word and never the character. Every pattern would then denote a language of one word: the empty one.",
                            "`node[0]` is `kind` under another name — the tag, not the payload.",
                        ],
                    },
                    {
                        "prompt": "Concatenation: which end of the left fragment gets the joining edge?",
                        "hole": "?",
                        "opts": ["t1", "s1", "t2", "s2"],
                        "a": 0,
                        "why": "The left fragment's *exit*. Reading the left part finishes there, and the joining edge is what says *and now begin the right part* without consuming anything in between.",
                        "whys": [
                            "The left fragment's *exit*. Reading the left part finishes there, and the joining edge is what says *and now begin the right part* without consuming anything in between.",
                            "That is the left fragment's entry, and the returned fragment already uses it as its own entry. An edge out of it would let the machine skip the left part altogether, so `ab` would match `b`.",
                            "The right fragment's exit is the exit of the whole thing. An edge leaving it would break the contract that nothing leads out of a fragment's exit, and the enclosing operator would then be building on a fragment that is not one.",
                            "The right fragment's entry is where the edge should *arrive*, not where it should leave.",
                        ],
                    },
                    {
                        "prompt": "And which end of the right fragment does it arrive at?",
                        "hole": "?",
                        "opts": ["t1", "s1", "t2", "s2"],
                        "a": 3,
                        "why": "The right fragment's entry. The whole join is one epsilon edge from the left's exit to the right's entry — no new states, which is why concatenation is free and why a long literal pattern costs two states per character and not four.",
                        "whys": [
                            "The left fragment's exit is where the edge starts; making it the destination too would be a self-loop on epsilon, which changes nothing and joins nothing.",
                            "The left fragment's entry is already serving as the entry of the whole concatenation. An edge back into it would create a loop the pattern never asked for.",
                            "The right fragment's exit is the exit of the concatenation. Arriving straight at it would skip the right part entirely, so `ab` would match `a`.",
                            "The right fragment's entry. The whole join is one epsilon edge from the left's exit to the right's entry — no new states, which is why concatenation is free and why a long literal pattern costs two states per character and not four.",
                        ],
                    },
                    {
                        "prompt": "The skip edge lets the body be bypassed. Which operator must *not* have it?",
                        "hole": "?",
                        "opts": ['"star"', '"opt"', '"plus"', '"cat"'],
                        "a": 2,
                        "why": "`+` means one or more, so the body has to be entered at least once and there must be no way round it. Star and opt both allow zero copies and both keep the skip edge.",
                        "whys": [
                            "Star allows zero copies, so it needs the skip edge. Withholding it would make `a*` behave like `a+` and reject the empty word.",
                            "Opt is *zero or one*; the skip edge is the zero. Without it `a?` would be indistinguishable from a bare `a`.",
                            "`+` means one or more, so the body has to be entered at least once and there must be no way round it. Star and opt both allow zero copies and both keep the skip edge.",
                            "Concatenation never reaches this branch — it is handled above and has no body to skip.",
                        ],
                    },
                    {
                        "prompt": "The loop edge sends the exit of the body back to its entry. Which operator must *not* have it?",
                        "hole": "?",
                        "opts": ['"opt"', '"star"', '"plus"', '"char"'],
                        "a": 0,
                        "why": "`?` is at most one copy, so nothing may go round a second time. Star and plus are the two that repeat, and they share this edge exactly.",
                        "whys": [
                            "`?` is at most one copy, so nothing may go round a second time. Star and plus are the two that repeat, and they share this edge exactly.",
                            "Star is *zero or more*; without the loop edge the *more* disappears and `a*` collapses to `a?`.",
                            "Plus is *one or more*, and the loop is where the *more* lives. Removing it would leave a fragment matching exactly one copy.",
                            "A literal has no body to repeat, and this branch never sees one.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "How big can Thompson's machine get?",
                "minutes": 12,
                "vars": ["c", "u", "p", "m"],
                "brief": r'''
Count the states the construction allocates. Reading `build` from the bottom up:

- a literal atom allocates two states and links them with the character;
- concatenation allocates none — it links two existing fragments;
- a union allocates two, one to branch from and one to merge into;
- each postfix operator (`*`, `+`, `?`) allocates two, for the same reason.

Take a pattern of length $m$ containing $c$ literal atoms, $u$ union operators and $p$
postfix operators, and assume no branch of a union is empty — so the parser produces no
`("eps",)` nodes. What is the largest machine that pattern can compile to?
''',
                "steps": [
                    {
                        "prompt": "Start with the literals alone. How many states do the $c$ atoms account for?",
                        "answer": "2 c",
                        "hint": "Every literal builds its own private two-state fragment; they never share.",
                        "deconstruct": [
                            "One `char` node allocates a fresh entry and a fresh exit.",
                            "There are $c$ of them and no state is ever reused, so the total is $2c$.",
                        ],
                    },
                    {
                        "prompt": "Now add the operators. Concatenation allocates nothing; each union and each postfix allocates a fresh entry and a fresh exit. Write the total state count of the machine in terms of $c$, $u$ and $p$.",
                        "answer": "2 c + 2 u + 2 p",
                        "hint": "Add two states for each of the $u$ unions and two for each of the $p$ postfixes, on top of what the literals already cost.",
                        "deconstruct": [
                            "The literals contributed $2c$.",
                            "Each of the $u$ unions adds $2$, and each of the $p$ postfixes adds $2$.",
                            "Concatenation adds nothing at all, so it never appears in the count.",
                        ],
                    },
                    {
                        "prompt": "Every literal occupies at least one character of the pattern, every union occupies its own `|`, and every postfix its own operator character — and no two of them occupy the same position. What is the largest $c + u + p$ can be, for a pattern of length $m$?",
                        "answer": "m",
                        "hint": "You are counting distinct positions in a string of length $m$, so the count cannot exceed the string.",
                        "deconstruct": [
                            "Map each atom to the pattern character it begins at, each union to its `|`, each postfix to its operator symbol.",
                            "That map is injective — no character does two of those jobs.",
                            "An injection into a set of size $m$ means at most $m$ things, so $c + u + p \\le m$.",
                        ],
                    },
                    {
                        "prompt": "Put the two together. What is the largest number of states Thompson's construction can build for a pattern of length $m$?",
                        "answer": "2 m",
                        "hint": "Substitute the bound from the previous step into the state count you wrote before it.",
                        "deconstruct": [
                            "The count was $2c + 2u + 2p = 2(c + u + p)$.",
                            "And $c + u + p$ is at most $m$.",
                        ],
                    },
                ],
                "closing": r'''
So the machine is linear in the pattern, with the constant $2$, and the bound is tight:
`aaaa` has $c = 4$ and compiles to exactly $8$ states, and `a|b|c|d` has $c = 4$, $u = 3$
and compiles to exactly $14 = 2 \times 7$. Parentheses are what make most patterns come in
under the bound — they cost characters and allocate nothing.

The checks in the lab allow $2m + 2$ rather than $2m$, and the extra two are for the
assumption dropped along the way: the empty pattern, and any empty branch such as the
right-hand side of `a|`, produce an `("eps",)` node, which allocates two states while
occupying no characters at all. Note what that allowance buys — exactly one such node.
A pattern holding $k$ of them compiles to $2m + 2k$ states in the worst case, so the
slack runs out as soon as there are two: `|` alone parses to `("alt", ("eps",), ("eps",))`
and compiles to six states from a single character, against the $4$ the check allows.
Every pattern in the tested battery has at most one empty branch, which is why $2m + 2$
holds there.

Linear size is the whole reason the simulation is $O(mn)$ rather than exponential. A
construction that could blow up in the pattern would put the cost back where
backtracking had it, just earlier.
''',
            },
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
            "quiz": {
                "title": "What a stack buys, and what a table costs",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why is `{ a^n b^n : n >= 1 }` not regular?",
                        "opts": [
                            "Because no regular expression is allowed to use exponents",
                            "A finite automaton has nowhere to keep an unbounded count, and the pumping lemma turns that intuition into a proof",
                            "Because the language is infinite",
                            "Because a DFA is allowed only one accepting state",
                        ],
                        "a": 1,
                        "why": """
Suppose some DFA with `p` states accepted it. Reading `a^p b^p`, the machine must revisit
a state within the first `p` letters, so there is a loop over a block of `a`s. Go round
that loop one extra time and the machine still accepts, but the word now has more `a`s
than `b`s and is not in the language. The contradiction is the proof. Being infinite is
no obstacle at all — `a*` is regular and infinite — and a DFA may have as many accepting
states as it likes.
""",
                    },
                    {
                        "q": "Which rule is allowed in Chomsky normal form?",
                        "opts": [
                            "`A -> B`",
                            "`A -> a B`",
                            "`A -> ε`",
                            "`A -> B C`",
                        ],
                        "a": 3,
                        "why": """
CNF permits exactly two shapes: one nonterminal going to two nonterminals, or one
nonterminal going to one terminal. `A -> B` is a unit rule and `A -> ε` an epsilon rule,
and both are banned because they break CYK's central invariant — that a rule application
always splits a span into two strictly shorter ones, so the table can be filled by
increasing length. `A -> a B` mixes a terminal with a nonterminal, which is legal in a
general grammar and in Greibach normal form, but not here. Every context-free language
without the empty word has a CNF grammar, so nothing is lost.
""",
                    },
                    {
                        "q": "The CYK table cell for a span holds what?",
                        "opts": [
                            "The one nonterminal that derives it, or nothing",
                            "The terminals appearing in that span",
                            "Every nonterminal that derives exactly that span",
                            "The rules used anywhere inside that span",
                        ],
                        "a": 2,
                        "why": """
All of them, which is the reason the algorithm is polynomial rather than exponential:
a span is analysed once and the answer serves every larger span that contains it.
Insisting on one nonterminal per cell would be wrong even for unambiguous grammars,
since different nonterminals can legitimately derive the same span in different
contexts. The terminals are already visible in the word, and the rules are what you
apply to the cells, not what you store in them.
""",
                    },
                    {
                        "q": "Counting parse trees instead of merely recording which nonterminals fit turns the parser into...",
                        "opts": [
                            "a faster parser, since counts are cheaper than sets",
                            "an ambiguity detector: more than one tree for some word means the grammar is ambiguous",
                            "a proof that the language itself is inherently ambiguous",
                            "a test for whether a language is context-free at all",
                        ],
                        "a": 1,
                        "why": """
A count above one is a witness, and `shortest_ambiguous` goes looking for the smallest.
But note what it witnesses: ambiguity is a property of the *grammar*. The same language
usually has an unambiguous grammar too, and finding a witness says nothing about whether
one exists. Inherent ambiguity — no unambiguous grammar exists at all — is a property of
the language, and it is undecidable, so no search of this kind could ever establish it.
The counting costs the same as the set version; the multiplications replace the unions.
""",
                    },
                    {
                        "q": "Where does CYK's third factor of `n` come from?",
                        "opts": [
                            "The grammar is scanned once for every cell of the table",
                            "The table has `n^3` cells",
                            "Each cell stores `n` separate counts",
                            "A span of length `L` can be cut in `L - 1` places, and `L` grows with `n`",
                        ],
                        "a": 3,
                        "why": """
The table has about `n^2 / 2` cells, which accounts for two factors. The third is the
split loop: a cell of length `L` tries every way of cutting its span into a non-empty
left part and a non-empty right part, and there are `L - 1` of those. Summing `L - 1`
over all the cells is where the cube appears. A cell holds at most one count per
nonterminal, and the grammar is scanned once per split rather than once per cell — a
cell of span length `L` scans it `L - 1` times, so one scan per cell would leave you at
`n^2 |G|` and no third factor at all.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Filling the table by increasing span",
                "minutes": 9,
                "caption": "cyk() — the base row and the split loop",
                "lang": "python",
                "brief": """
The table is keyed by `(i, length)`, meaning the span `word[i:i+length]`, and each cell
maps a nonterminal to the number of trees it has over that span. The base row is the
single characters; every longer span is assembled from two shorter ones that are already
in the table.

Four holes, and three of them are indices. Getting an index wrong here does not crash —
it quietly parses a different word.
""",
                "listing": r'''
n = len(word)
table = {}

for i, ch in enumerate(word):
    cell = {}
    for lhs, rhs in grammar.rules:
        if len(rhs) == 1 and rhs[0] == ___:
            cell[lhs] = cell.get(lhs, 0) + 1
    if cell:
        table[(i, 1)] = cell

for length in range(2, n + 1):
    for i in range(0, n - length + 1):
        cell = {}
        for split in range(1, length):
            left = table.get((i, ___))
            right = table.get((___, length - split))
            if not left or not right:
                continue
            for lhs, rhs in grammar.rules:
                if len(rhs) == 2 and rhs[0] in left and rhs[1] in right:
                    cell[lhs] = cell.get(lhs, 0) + ___
        if cell:
            table[(i, length)] = cell
''',
                "blanks": [
                    {
                        "prompt": "The base row: a one-symbol rule fires when its terminal is what?",
                        "hole": "?",
                        "opts": ["lhs", "ch", "rhs", "i"],
                        "a": 1,
                        "why": "The character sitting at position `i`, which the enumerate has already unpacked. A CNF terminal rule covers exactly one symbol, so this comparison is the entire base case.",
                        "whys": [
                            "`lhs` is the nonterminal on the left of the rule. Comparing a terminal against it would fire a rule whenever a nonterminal happened to be spelled the same way as a letter — which is exactly the confusion CNF validation exists to prevent.",
                            "The character sitting at position `i`, which the enumerate has already unpacked. A CNF terminal rule covers exactly one symbol, so this comparison is the entire base case.",
                            "`rhs` is the whole right-hand side tuple, and `rhs[0]` has already been taken out of it on the same line. A tuple never equals a character, so no rule would ever fire and every word would be rejected.",
                            "`i` is the position, not the symbol at it. Comparing a terminal against an integer index is always false.",
                        ],
                    },
                    {
                        "prompt": "The left half of the span starts at `i`. How long is it?",
                        "hole": "?",
                        "opts": ["length", "split", "i", "length - split"],
                        "a": 1,
                        "why": "`split` is the length of the left half — the loop runs it from `1` to `length - 1`, so both halves are non-empty. That is what makes the recursion well founded: every lookup is into a strictly shorter span, already computed.",
                        "whys": [
                            "The full length is the span being built, and it is not in the table yet. Looking it up would read the cell currently being written, or more likely find nothing at all.",
                            "`split` is the length of the left half — the loop runs it from `1` to `length - 1`, so both halves are non-empty. That is what makes the recursion well founded: every lookup is into a strictly shorter span, already computed.",
                            "`i` is where the span starts, not how long it is. Using it as a length makes the two halves depend on the position of the span rather than on the cut.",
                            "That is the length of the *right* half — and putting it here does not swap the halves, because the right half still starts at `i + split`. The left half would run from `i` for `length - split` symbols, so the two overlap whenever `split` is under half the span and leave a gap whenever it is over. Symmetric rules are no protection: with this fill, `count_parses(DOUBLE, 'aaaa')` comes out as `6` instead of `5`, and `'aaaaa'` as `42` instead of `14`.",
                        ],
                    },
                    {
                        "prompt": "And where does the right half begin?",
                        "hole": "?",
                        "opts": ["i + split", "split", "i", "i + length"],
                        "a": 0,
                        "why": "Immediately after the left half ends: the left half occupies `split` symbols starting at `i`, so the right half starts at `i + split` and runs for the remaining `length - split`. The two halves have to meet exactly, with no gap and no overlap.",
                        "whys": [
                            "Immediately after the left half ends: the left half occupies `split` symbols starting at `i`, so the right half starts at `i + split` and runs for the remaining `length - split`. The two halves have to meet exactly, with no gap and no overlap.",
                            "That forgets where the span itself begins, so for every span not starting at position `0` the right half is read from the wrong part of the word.",
                            "Starting the right half where the left half starts overlaps them completely. The parser would then accept words on the strength of reading the same symbols twice.",
                            "That is one symbol past the end of the whole span, so the right half would begin outside it and the two halves would never join up.",
                        ],
                    },
                    {
                        "prompt": "A rule `A -> B C` fires over this split. How many trees does that contribute?",
                        "hole": "?",
                        "opts": ["left[rhs[0]] * right[rhs[1]]", "left[rhs[0]] + right[rhs[1]]", "1", "max(left[rhs[0]], right[rhs[1]])"],
                        "a": 0,
                        "why": "Every tree for the left half can be paired with every tree for the right half, so the split contributes the product. Summing that product over all the splits is what makes `count_parses(DOUBLE, 'a' * n)` come out as the Catalan numbers.",
                        "whys": [
                            "Every tree for the left half can be paired with every tree for the right half, so the split contributes the product. Summing that product over all the splits is what makes `count_parses(DOUBLE, 'a' * n)` come out as the Catalan numbers.",
                            "A sum counts each half once instead of pairing them. Two trees on the left and three on the right make six whole trees, not five.",
                            "Adding one per split records only *that* the rule fits, which is the membership test. It gives the right answer to `accepts` and the wrong answer to every count above one.",
                            "A maximum discards one half of the pairing entirely, so a word with two independent choices would be reported as having one.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Where the third factor of n comes from",
                "minutes": 13,
                "vars": ["n", "L", "g"],
                "brief": r'''
CYK is quoted as $O(n^3 |G|)$ and the cube is worth earning rather than accepting. The
work the parser does is one *rule test* per triple: a span, a way of cutting that span in
two, and a rule to try across the cut.

Count the triples exactly, for a word of length $n$. Spans of length $1$ are the base row
and are handled separately, so only spans of length $2$ and above matter here.
''',
                "steps": [
                    {
                        "prompt": "How many spans of length $2$ or more does a word of length $n$ have? Write it in terms of $n$.",
                        "answer": "\\frac{n(n-1)}{2}",
                        "hint": "A span of length $L$ can start in $n - L + 1$ places. Sum that over $L = 2, 3, \\dots, n$ and you are adding $n-1$ down to $1$.",
                        "deconstruct": [
                            "For a fixed $L$ the starting index runs from $0$ to $n - L$, which is $n - L + 1$ spans.",
                            "Summing over $L$ from $2$ to $n$ gives $(n-1) + (n-2) + \\dots + 1$.",
                            "That is the sum of the first $n-1$ integers.",
                        ],
                    },
                    {
                        "prompt": "A span of length $L$ is cut into two non-empty halves in how many places?",
                        "answer": "L - 1",
                        "hint": "The cut may fall after the first symbol, after the second, and so on — but not at either end, because CNF gives no rule for an empty half.",
                        "deconstruct": [
                            "There are $L + 1$ positions in the span if you count the two ends.",
                            "Both ends are excluded, because a half of length zero has no nonterminal deriving it.",
                        ],
                    },
                    {
                        "prompt": "Now count the (span, split) pairs: sum $(n - L + 1)(L - 1)$ over $L = 2 \\dots n$. Write the closed form in terms of $n$.",
                        "answer": "\\frac{n^3 - n}{6}",
                        "placeholder": "\\frac{?}{6}",
                        "hint": "Substitute $j = L - 1$ so the summand becomes $j(n - j)$ with $j$ running from $1$ to $n-1$, then use the two standard sums.",
                        "deconstruct": [
                            "With $j = L - 1$ the sum is $\\sum_{j=1}^{n-1} j(n-j) = n\\sum j - \\sum j^2$.",
                            "$\\sum_{j=1}^{n-1} j = \\frac{(n-1)n}{2}$ and $\\sum_{j=1}^{n-1} j^2 = \\frac{(n-1)n(2n-1)}{6}$.",
                            "Factor out $\\frac{(n-1)n}{6}$: the bracket is $3n - (2n-1) = n+1$, so the sum is $\\frac{(n-1)n(n+1)}{6}$.",
                        ],
                    },
                    {
                        "prompt": "Each of those pairs is tried against every one of the $g$ binary rules of the grammar. Write the total number of rule tests.",
                        "answer": "\\frac{g (n^3 - n)}{6}",
                        "hint": "Multiply the pair count by the number of rules being tried at each one.",
                        "deconstruct": [
                            "The inner loop over rules runs once per (span, split) pair.",
                            "So the total is the pair count times $g$.",
                        ],
                    },
                ],
                "closing": r'''
$\frac{n^3 - n}{6}$ factors as $\frac{(n-1)n(n+1)}{6}$, which is $\binom{n+1}{3}$ — the
triples are literally a choice of three cut positions out of $n+1$, once you see it that
way.

The numbers are smaller than the cube suggests at the sizes anyone actually parses. At
$n = 10$ there are $165$ (span, split) pairs, not $1000$; the $\frac{1}{6}$ is doing real
work. It stops helping around $n = 100$, where the count is $166\,650$, and by $n = 1000$
it is over $1.6 \times 10^8$ — which is why nobody runs CYK over a whole document and why
every practical parser trades generality for a linear-time algorithm that only handles
some grammars.

Note also which factor $|G|$ is. It multiplies, it does not exponentiate: converting a
grammar to CNF can enlarge it, and the parse cost follows that growth linearly.
''',
            },
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
            "quiz": {
                "title": "Halting, budgets, and the question with no program",
                "minutes": 7,
                "questions": [
                    {
                        "q": "The transition function is partial. What does a missing entry mean?",
                        "opts": [
                            "The machine rejects and rewinds the tape",
                            "The machine halts where it stands",
                            "The machine loops on that cell forever",
                            "The machine is malformed and should have been rejected by validation",
                        ],
                        "a": 1,
                        "why": """
Nothing applies, so nothing happens: `step` returns `None` and the run is over. That is
one of the two ways to stop — the other is arriving in the accept state, which also has
no successor. Both are *halting*; only one of them is *accepting*, which is why `run`
reports the two separately. Nothing rewinds, because there is no notion of rejection
beyond stopping somewhere that is not the accept state, and a partial transition
function is entirely well formed. It is the DFA that must be total, not this.
""",
                    },
                    {
                        "q": "Why does `run` report `halted` separately from `steps`?",
                        "opts": [
                            "Because `steps` counts tape cells rather than transitions",
                            "Because a machine that has halted always has `steps` equal to zero",
                            "Because `halted` refers only to reaching the accept state",
                            "Running out of budget is not halting: the simulation stopped, but the machine had not",
                        ],
                        "a": 3,
                        "why": """
`halted` False with `steps` equal to `max_steps` is the honest report of an unfinished
experiment: the machine had somewhere to go and we stopped watching. Nothing follows from
it — the machine might halt on the very next step or never. That is why the budget is
checked before the step is taken rather than after: it keeps `steps` from ever exceeding
`max_steps` and keeps `halted` from ever claiming more than was observed. `accepted` is
the narrower flag, true only when the machine halted *and* did so in the accept state.
""",
                    },
                    {
                        "q": "`detect_loop` reports the step at which a configuration repeats. What does that prove?",
                        "opts": [
                            "The machine halts, but only after a long time",
                            "The machine's language is undecidable",
                            "The machine never halts on that input, because a deterministic machine in a configuration it has been in before must repeat everything it did after it",
                            "Nothing — a configuration can repeat and the machine still halt later",
                        ],
                        "a": 2,
                        "why": """
A configuration is the entire state of the computation: control state, head position and
tape. The successor is a function of it alone, so returning to one you have seen means
entering a cycle that will run forever. That makes the test *sound* — when it says the
machine diverges, it is right. Note what it does not give you: nothing about the
language, and no upper bound on runtime for the machines it says nothing about.
""",
                    },
                    {
                        "q": "`detect_loop` is sound but not complete. What does incompleteness mean here?",
                        "opts": [
                            "It sometimes reports a loop where there is none",
                            "Some machines run forever without ever repeating a configuration, and the test returns `None` for them",
                            "It only works for machines with a single tape",
                            "It needs a budget at least as large as the number of states",
                        ],
                        "a": 1,
                        "why": """
`RIGHTWARD` is the counterexample and it is three symbols long: it walks right forever
over blank tape. The head position is part of the configuration, so every configuration
it visits is new and no repeat ever occurs — yet it plainly never halts. Reporting a loop
that is not there would be *unsoundness*, and determinism rules that out. The gap between
the two is the whole subject: sound and complete together is exactly what the halting
problem says you cannot have.
""",
                    },
                    {
                        "q": "Why is there no program that decides, for every machine and input, whether the machine halts?",
                        "opts": [
                            "Because the tape is infinite and no program can inspect an infinite object",
                            "Because the busy beaver function grows too fast to compute",
                            "Assume one exists, then build a machine that asks it about itself and does the opposite of the answer; its own behaviour contradicts whatever the decider said",
                            "Because no program is able to read its own description",
                        ],
                        "a": 2,
                        "why": """
The diagonal argument, and it needs nothing more than the assumption it destroys. Feed
the contrary machine its own description: if the decider says it halts, it loops; if it
says it loops, it halts. Both branches are contradictions, so the decider cannot exist.
The infinite tape is a red herring — the *description* being reasoned about is finite,
and finiteness is what makes the self-application legal. Busy beaver's uncomputability is
a consequence of this result rather than a cause of it. And a program certainly can read
its own description; the recursion theorem is what guarantees the construction above is
allowed.
""",
                    },
                ],
            },
            "blanks": {
                "title": "One step of the machine",
                "minutes": 9,
                "caption": "TuringMachine.step() — four holes",
                "lang": "python",
                "brief": """
A configuration is `(state, head, cells)`, and `cells` is a sorted tuple of
`(index, symbol)` pairs holding only the cells that are not blank. It is a tuple because
it has to be hashable: `detect_loop` puts configurations in a set, and a set is the whole
mechanism of the divergence test.

That constraint drives two of the holes below. The other two are about how a machine
stops.
""",
                "listing": r'''
def step(self, cfg):
    state, head, cells = cfg
    if state == ___:
        return None
    mapping = dict(cells)
    symbol = mapping.get(head, ___)
    action = self.transitions.get((state, symbol))
    if action is None:
        return ___
    new_state, write, move = action
    if write == self.blank:
        mapping.pop(head, None)      # a blank is an absent cell, not a stored one
    else:
        mapping[head] = write
    if move == "L":
        head -= 1
    elif move == "R":
        head += 1
    return (new_state, head, ___)
''',
                "blanks": [
                    {
                        "prompt": "One of the two ways to stop is checked before anything else.",
                        "hole": "?",
                        "opts": ["self.start", "self.blank", "self.accept", "None"],
                        "a": 2,
                        "why": "The accept state has no successor by construction, whatever the transition table happens to say. Checking it first is what makes `accepted` mean *halted in the accept state* rather than *ran out of transitions somewhere*.",
                        "whys": [
                            "The start state is where a run begins, and a machine may return to it any number of times. Halting there would stop most machines before they had done anything.",
                            "The blank is a tape symbol, and the control state is never one. The comparison is always false, so the accept state would lose its special meaning and the machine would run on past it.",
                            "The accept state has no successor by construction, whatever the transition table happens to say. Checking it first is what makes `accepted` mean *halted in the accept state* rather than *ran out of transitions somewhere*.",
                            "Comparing the state against `None` tests for a state no machine has. Nothing would ever match, and the accept state would behave like any other.",
                        ],
                    },
                    {
                        "prompt": "The cell under the head might not be in `mapping`. What is read instead?",
                        "hole": "?",
                        "opts": ["self.blank", "self.accept", '""', "0"],
                        "a": 0,
                        "why": "The tape is infinite and mostly blank, so `cells` stores only what has been written. An absent index is a blank cell, and that is exactly the convention `config` and `tape_string` use at the other two ends of the same representation.",
                        "whys": [
                            "The tape is infinite and mostly blank, so `cells` stores only what has been written. An absent index is a blank cell, and that is exactly the convention `config` and `tape_string` use at the other two ends of the same representation.",
                            "That is a control state, not a tape symbol. Reading it would look up a transition keyed by a state name where a symbol belongs, and `INCREMENT`'s `(\"right\", \"_\")` rule would never fire.",
                            "An empty string is not the blank symbol — the blank is a real one-character symbol, `\"_\"` by default, and `_validate` insists on that. The two are different keys and the lookup would miss.",
                            "Zero is a perfectly good tape symbol in its own right; `INCREMENT` writes `\"0\"` deliberately. Treating unwritten cells as zeros would make an untouched tape read as a string of zeros.",
                        ],
                    },
                    {
                        "prompt": "No transition applies. What comes back?",
                        "hole": "?",
                        "opts": ["cfg", "None", "(state, head, cells)", "self.accept"],
                        "a": 1,
                        "why": "`None` is the caller's signal that the machine has halted; `run` reads it as *stop, and record that it stopped on its own*. Anything else would be reported as a successor configuration.",
                        "whys": [
                            "Returning the configuration unchanged says *the machine took a step and nothing happened*, so `run` would keep going until the budget ran out and then report a halting machine as still running.",
                            "`None` is the caller's signal that the machine has halted; `run` reads it as *stop, and record that it stopped on its own*. Anything else would be reported as a successor configuration.",
                            "That rebuilds the same configuration by hand — the same problem in more characters, and `detect_loop` would report a repeat on the very next step for every machine that halts this way.",
                            "The accept state is not a configuration, and reaching the end of the transition table is not the same as accepting. Returning it would mark every stuck machine as having succeeded.",
                        ],
                    },
                    {
                        "prompt": "The cells go back into the configuration. In what form?",
                        "hole": "?",
                        "opts": ["mapping", "tuple(mapping.items())", "tuple(sorted(mapping.items()))", "sorted(mapping.items())"],
                        "a": 2,
                        "why": "Sorted, and a tuple. Sorted because two configurations that describe the same tape must compare equal, and dict order records the history of writes rather than the contents; a tuple because `detect_loop` stores configurations in a set and a list is not hashable.",
                        "whys": [
                            "A dict is neither hashable nor order-independent, so the configuration could not go into a set at all — and `detect_loop` is nothing but a set.",
                            "A tuple is hashable, but unsorted it preserves insertion order. Two machines holding the identical tape, written in a different order, would produce different tuples and a genuine loop would go unnoticed.",
                            "Sorted, and a tuple. Sorted because two configurations that describe the same tape must compare equal, and dict order records the history of writes rather than the contents; a tuple because `detect_loop` stores configurations in a set and a list is not hashable.",
                            "Sorting fixes the ordering problem and leaves the hashing one: a list cannot be a member of a set, so the first `seen.add` would raise.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How long before a configuration must repeat?",
                "minutes": 8,
                "brief": """
`detect_loop` is only as good as the budget you give it, and the honest way to choose a
budget is to count how many configurations there are. Beyond that count a repeat is not
merely likely, it is forced — there is nowhere else for the machine to be.

Confine the head to a window of cells and everything becomes finite and countable: a
configuration is a control state, a head position, and the contents of the window.
""",
                "prompt": "How many distinct configurations can this machine be in?",
                "note": "An exact integer. The head never leaves the window, and the cells outside it stay blank throughout.",
                "figure": "A single-tape machine with **5** control states over the tape alphabet "
                          "`{0, 1, _}`. On the input in question its head visits only **8** cells and "
                          "never leaves them, so every cell outside that window is blank for the whole "
                          "run. A configuration is `(state, head position, tape contents)`.",
                "given": [
                    {"label": "Control states", "value": "5"},
                    {"label": "Tape alphabet", "value": "`{0, 1, _}` — 3 symbols"},
                    {"label": "Cells the head visits", "value": "8"},
                    {"label": "Outside the window", "value": "always blank"},
                ],
                "aside": "The head has to be somewhere, and an all-blank window is one of the "
                         "possible window contents like any other — neither is a special case to "
                         "subtract.",
                "answer": 262440,
                "tol": 0.5,
                "unit": "configurations",
                "hint": "Three independent choices: which state, which of the 8 positions, and what "
                        "the 8 cells hold. Count each one and combine them the way independent "
                        "choices combine.",
                "wrong": "Adding the three counts gives a few thousand and is the usual slip. The "
                         "machine is in one state *and* at one position *and* holding one tape, so "
                         "the three counts multiply.",
                "why": """
`5 * 8 * 3^8 = 5 * 8 * 6561 = 262440`. Run this machine for 262441 steps inside that
window and some configuration has come round a second time, which — determinism again —
proves it never halts. So `detect_loop` with a budget of 262441 is a *complete*
divergence test for machines that stay in the window.

The number is the point, though. Eight cells and three symbols already cost a quarter of
a million; widen the window to twenty cells and the same formula gives about
`3.5 * 10^11`. And the window itself was an assumption — a machine that keeps wandering
right has no window at all, which is `RIGHTWARD` and is why the test is incomplete in
general. Every route to a budget that always works runs into the same wall, and the wall
has a name: the busy beaver function, which outgrows every computable bound and so
outgrows every budget you could compute.
""",
            },
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
