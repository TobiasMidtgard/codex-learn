"""CS401 — Distributed Systems & Cloud Computing."""

COURSE = {
    "id": "CS401",
    "title": "Distributed Systems & Cloud Computing",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["CS320", "CS210"],
    "stack": ["Go (reference)", "Python", "Docker"],
    "credits": 15,
    "hours": 170,
    "icon": "☷",
    "summary": (
        "A distributed system is a set of machines that fail independently and cannot "
        "agree on what time it is. This course builds the four mechanisms that make such "
        "a set behave like one service: causal clocks, a Raft consensus core, tunable "
        "quorum replication, and consistent hashing. Every algorithm is implemented "
        "against a deterministic message simulator, so a partition is something you "
        "cause on purpose and can replay exactly."
    ),
    "outcomes": [
        "Order events with Lamport and vector clocks, and justify when each is sufficient",
        "Implement Raft leader election and log replication, including split votes and partition healing",
        "Reason about the R + W > N quorum condition and show precisely where it fails to hold",
        "Build a consistent-hashing ring with virtual nodes and measure key movement against modulo hashing",
        "Apply hinted handoff, read repair and anti-entropy to reconcile replicas after a fault",
        "Write deterministic fault-injection tests that reproduce a distributed failure exactly",
        "State the CAP and PACELC trade-offs a given design has actually made",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Kleppmann, *Designing Data-Intensive Applications*, O'Reilly 2017 — chapters 5, 8, 9",
        "Ongaro & Ousterhout, *In Search of an Understandable Consensus Algorithm (Raft)*, USENIX ATC 2014",
        "DeCandia et al., *Dynamo: Amazon's Highly Available Key-value Store*, SOSP 2007",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Time, causality and ordering",
            "summary": "Ordering events without a shared clock: Lamport counters and vector clocks.",
            "concepts": [
                "Physical clocks drift and skew; NTP bounds error but never removes it",
                "The happens-before relation: program order, plus send precedes its receive, plus transitivity",
                "Lamport clocks: a -> b implies L(a) < L(b), but the converse does not hold",
                "Vector clocks: one counter per process; the ordering they induce is exactly happens-before",
                "Two events are concurrent when neither vector dominates the other",
                "Vector clocks cost O(processes) per message — the reason Dynamo prunes them",
                "Total order by (Lamport, process id) is a tie-break, not a causal fact",
            ],
            "quiz": {
                "title": "What a clock can and cannot tell you",
                "minutes": 7,
                "questions": [
                    {
                        "q": "You are handed two Lamport stamps and told $L(a) < L(b)$. What follows?",
                        "opts": [
                            "$a$ happened before $b$",
                            "Nothing on its own — $a$ may have happened before $b$, or the two may be concurrent",
                            "$a$ and $b$ are concurrent",
                            "$a$ and $b$ ran on the same process",
                        ],
                        "a": 1,
                        "why": r"""
Lamport's rule runs one way only: if $a$ could have influenced $b$ then $L(a) < L(b)$.
Reading it backwards is the mistake, because a smaller stamp is produced both by a
genuine ancestor and by an event on some other machine nobody ever heard from. That is
what `lamport_blind_spots` in the lab is for — events 2 and 7 of the reference log are
concurrent and carry stamps 1 and 3, so a stamp comparison orders them anyway. Nor can
you read concurrency off the stamps: a causal chain also produces increasing numbers.
And two events on one process are indeed always ordered, but the stamps alone never say
they were on one process.
""",
                    },
                    {
                        "q": "Event $p$ carries the vector $\\{A:2, B:1, C:0\\}$ and event $q$ carries $\\{A:1, B:3, C:0\\}$. How are they related?",
                        "opts": [
                            "$p$ happened before $q$",
                            "$q$ happened before $p$",
                            "$p$ and $q$ are concurrent",
                            "$p$ and $q$ are the same event seen twice",
                        ],
                        "a": 2,
                        "why": r"""
Dominance has to hold in every entry at once. $p$ is ahead on $A$ (2 against 1) and $q$
is ahead on $B$ (3 against 1), so neither vector dominates and neither event can have
influenced the other — they are concurrent. This is the whole gain over a Lamport stamp:
the vector detects the disagreement, and a single integer cannot, because collapsing
three counters into one number throws away exactly the information you need. Two
identical vectors would mean the same event; here nothing matches.
""",
                    },
                    {
                        "q": "Process $B$ holds $\\{A:2, B:6\\}$ and receives a message carrying $\\{A:4, B:1\\}$. What does it hold immediately after the receive?",
                        "opts": [
                            "$\\{A:4, B:7\\}$",
                            "$\\{A:4, B:6\\}$",
                            "$\\{A:6, B:7\\}$",
                            "$\\{A:2, B:7\\}$",
                        ],
                        "a": 0,
                        "why": r"""
Merge, then increment. Element-wise maximum first — $A$ becomes $\max(2,4) = 4$ and $B$
stays at $\max(6,1) = 6$, because the sender's view of $B$ is older than $B$'s own — and
then the receive is itself an event on $B$, so $B$'s own entry goes to 7. Stopping after
the merge loses the receive. Adding the entries instead of taking the maximum inflates
$A$ to 6 and claims knowledge of four events that never happened. Skipping the merge
leaves $A$ at 2, which is the bug that makes a message appear to arrive before it was
sent.
""",
                    },
                    {
                        "q": "Replicas order operations by the pair (Lamport stamp, process id). What has that bought them?",
                        "opts": [
                            "A total order every replica agrees on, which says nothing about what caused what",
                            "A record of which operation caused which",
                            "The same ordering a vector clock would have produced",
                            "A guarantee that concurrent operations are never reordered",
                        ],
                        "a": 0,
                        "why": r"""
The tie-break is genuinely useful: it makes every replica apply the same operations in
the same sequence with no further communication, which is all a deterministic state
machine needs. What it is not is a fact about the world. It imposes an order on pairs
that had none, arbitrarily and by construction, so a consumer reading the sequence as
"this caused that" is wrong about every concurrent pair in it. A vector clock would have
left those pairs unordered, which is the honest answer and also a less convenient one.
""",
                    },
                    {
                        "q": "NTP holds every clock in the fleet within 10 ms of true time. A log line on machine X is stamped 4 ms earlier than one on machine Y. What may you conclude?",
                        "opts": [
                            "X's event happened first",
                            "The two events are concurrent",
                            "Nothing about their order — the gap is smaller than the error the clocks admit to",
                            "Y's clock has drifted and needs resynchronising",
                        ],
                        "a": 2,
                        "why": r"""
NTP gives you a bound, not the truth. With each clock inside 10 ms of real time, stamps
4 ms apart are consistent with either event having happened first. An ordering claim is
only safe once the gap exceeds the sum of the two error bounds — which is precisely what
Spanner's TrueTime does when it waits out its uncertainty interval before committing.
Concurrency is not available either: that is a statement about causality, and a clock
reading knows nothing about who sent what to whom. Both clocks here are behaving exactly
as specified.
""",
                    },
                ],
            },
            "blanks": {
                "title": "One event, stamped",
                "minutes": 8,
                "caption": "the receive path, four holes",
                "lang": "python",
                "brief": r"""
The whole of vector time is four lines: absorb what the sender knew, then count the one
thing that is genuinely new. Get the order of those two wrong, or forget that a message
carries a *copy*, and the clock still produces plausible-looking numbers — which is the
worst failure mode available, because nothing crashes.

Nothing is executed here. You are choosing the operation, not writing the loop.
""",
                "listing": """# One event on process P. `clock` is P's own vector; `carried` is the vector
# that arrived with the message. No physical clock appears anywhere.

if op == "recv":
    for q, v in carried.items():
        clock[q] = ___(clock[q], v)     # absorb everything the sender already knew

clock[P] += ___                         # this event is the one new thing to record

if op == "send":
    in_flight[msg] = ___(clock)         # what the message takes away with it

# and later, comparing the vectors of two events a and b
before = all(a[q] <= b[q] for q in a) and ___
""",
                "blanks": [
                    {
                        "prompt": "How does a receiver combine its own knowledge with the sender's?",
                        "hole": "?",
                        "opts": ["max", "min", "sum", "abs"],
                        "a": 0,
                        "why": "Element-wise maximum. Each entry is a count of events, and the receiver now knows about everything either side knew about, so the larger count is the true one.",
                        "whys": [
                            "Element-wise maximum. Each entry is a count of events, and the receiver now knows about everything either side knew about, so the larger count is the true one.",
                            "Taking the smaller count throws away knowledge on receipt — the receiver would forget events it had already seen, and its vector would go backwards, which is the one thing a clock must never do.",
                            "Adding double-counts everything both sides already knew. Two processes that have exchanged a few messages would report counters far above the number of events that ever happened.",
                            "`abs` takes one argument and these counters are never negative, so it is not even applicable — worth noticing because the merge really is this simple, and there is nothing clever hiding in it.",
                        ],
                    },
                    {
                        "prompt": "By how much does the process advance its own entry for this event?",
                        "hole": "?",
                        "opts": ["1", "0", "len(clock)", "v"],
                        "a": 0,
                        "why": "By one, because exactly one event just happened here. Local work, a send and a receive all count the same — the receive is not special, it merely does the merge first.",
                        "whys": [
                            "By one, because exactly one event just happened here. Local work, a send and a receive all count the same — the receive is not special, it merely does the merge first.",
                            "Not advancing at all means two distinct events on this process carry the same vector, so they compare as `equal` and the ordering the clock is supposed to induce quietly stops being a total order on one process's own timeline.",
                            "Jumping by the number of processes makes the counter grow with cluster size rather than with local activity, and comparisons against a process that has been quiet start returning `after` for no reason.",
                            "`v` is a counter that arrived from somewhere else. Using it here would let a chatty peer decide how fast this process's own time runs.",
                        ],
                    },
                    {
                        "prompt": "What does the message carry away?",
                        "hole": "?",
                        "opts": ["dict", "list", "sorted", "iter"],
                        "a": 0,
                        "why": "`dict(clock)` is a copy. Handing over the live vector means the next local event mutates a message already in flight, and the receiver merges a clock from the future — a bug that only shows up when the receive happens to be delivered late.",
                        "whys": [
                            "`dict(clock)` is a copy. Handing over the live vector means the next local event mutates a message already in flight, and the receiver merges a clock from the future — a bug that only shows up when the receive happens to be delivered late.",
                            "`list(clock)` keeps the process names and drops every counter, so the receiver has no numbers to take a maximum against.",
                            "`sorted(clock)` has the same problem and adds an ordering nobody asked for: the keys come back as a plain list, and the counts are gone.",
                            "`iter(clock)` hands over a one-shot view of a structure that is about to change underneath it. Reading it after the sender moves on gives either stale keys or a runtime error.",
                        ],
                    },
                    {
                        "prompt": "What has to hold as well, for `a` to be strictly before `b`?",
                        "hole": "?",
                        "opts": [
                            "any(a[q] < b[q] for q in a)",
                            "all(a[q] < b[q] for q in a)",
                            "any(a[q] > b[q] for q in a)",
                            "len(a) == len(b)",
                        ],
                        "a": 0,
                        "why": "At least one entry must be strictly smaller, or `a` and `b` are the same vector and the events are equal rather than ordered. Dominance is `<=` everywhere plus `<` somewhere.",
                        "whys": [
                            "At least one entry must be strictly smaller, or `a` and `b` are the same vector and the events are equal rather than ordered. Dominance is `<=` everywhere plus `<` somewhere.",
                            "Demanding every entry be strictly smaller is far too strong: a process that has been idle has the same count in both vectors, so an event genuinely in the past of another would be reported as concurrent.",
                            "Given that every entry already satisfies `<=`, no entry can be strictly greater — so this makes `before` permanently false, and every pair in the log comes back as concurrent.",
                            "Comparing lengths says the two vectors cover the same processes, which is true of every pair in a fixed cluster. It admits the equal case, so an event would be reported as strictly before itself.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How much clock rides on each message?",
                "minutes": 7,
                "brief": r"""
Vector clocks are the honest answer to ordering, and the bill arrives on every packet.
A vector is dense: one entry per process in the system, whether or not that process has
ever done anything, because a missing entry and a zero entry have to be told apart from
each other and from an entry you simply have not heard about yet.

This is the arithmetic that pushed Dynamo into truncating its clocks.
""",
                "prompt": "How many bytes of vector clock does each message carry?",
                "note": "Count the clock only, not the payload. A whole number of bytes.",
                "figure": "`[ payload 120 B ][ clock: (node id 16 B + counter 8 B) x one per process ]` — 200 processes, and every message carries the sender's entire vector.",
                "given": [
                    {"label": "Processes in the system", "value": "200"},
                    {"label": "Node id per entry", "value": "16 bytes"},
                    {"label": "Counter per entry", "value": "8 bytes"},
                    {"label": "Entries sent per message", "value": "all of them"},
                    {"label": "Application payload", "value": "120 bytes"},
                ],
                "aside": "Dynamo caps the clock at ten entries and drops the oldest, accepting that "
                         "two versions may then be reported as conflicting when one really did "
                         "precede the other. Bounded bytes, occasional false conflicts.",
                "answer": 4800,
                "tol": 0,
                "unit": "bytes",
                "hint": "One entry per process, and each entry is a node id next to a counter. "
                        "Nothing depends on how busy the processes have been.",
                "wrong": "The usual slip is to count only the processes that have a non-zero "
                         "counter. The vector is dense — a process that has never been heard "
                         "from still occupies an entry, because that is what distinguishes "
                         "'nothing yet' from 'not in the system'.",
                "why": "$200 \\times (16 + 8) = 4800$ bytes, against a 120-byte payload: the "
                       "bookkeeping is forty times the message. This is the cost that makes "
                       "vector clocks unusable at fleet scale and perfectly reasonable at the "
                       "scale of one key's replica set, which is why Dynamo keeps a clock per "
                       "*object* — three or five entries — rather than per cluster. Halving the "
                       "node id to 8 bytes only takes it to 3200; the term that hurts is the "
                       "process count, and it is linear.",
            },
            "lab": {
                "title": "Lamport and vector clocks over an event log",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
An **event log** is a list of `(process, op, arg)` triples in the order an
external observer saw them. `op` is one of:

- `"local"` — internal work, `arg` is `None`
- `"send"` — `arg` is the message id being sent
- `"recv"` — `arg` is the message id being received

The reference log used throughout:

```python
LOG = [
    ("A", "local", None),   # 0
    ("A", "send", "m1"),    # 1
    ("B", "local", None),   # 2
    ("B", "recv", "m1"),    # 3
    ("B", "send", "m2"),    # 4
    ("C", "local", None),   # 5
    ("C", "recv", "m2"),    # 6
    ("A", "local", None),   # 7
]
```

## What to write

**`processes(log)`** — the process ids in first-appearance order. Raise
`ValueError` for an unknown `op`.

**`lamport_clocks(log)`** — one integer stamp per event, same order as the log.
Each process holds a counter starting at 0. A `local` or `send` event increments
it. A `recv` event sets the counter to `max(own, stamp carried by the message) + 1`.
A `send` records the stamp it carries. Expected for `LOG`:

```text
[1, 2, 1, 3, 4, 1, 5, 3]
```

**`vector_clocks(log)`** — one dict per event, mapping every process id to a
counter. A `recv` takes the element-wise maximum with the vector the message
carried, then increments its own entry. Event 3 above ends at
`{"A": 2, "B": 2, "C": 0}`.

**`compare_vectors(a, b)`** — one of `"before"`, `"after"`, `"equal"`,
`"concurrent"`. `a` is *before* `b` when every entry of `a` is less than or
equal to the matching entry of `b` and at least one is strictly smaller.

**`concurrent_pairs(log)`** — sorted `(i, j)` index pairs with `i < j` whose
vectors are concurrent. `LOG` has twelve of them.

**`lamport_blind_spots(log)`** — the subset of those pairs where
`lamport[i] < lamport[j]`. These are the pairs a Lamport stamp alone would
order, wrongly: `[(2, 7), (5, 7)]`.

Both clock functions must raise `ValueError` when a `recv` names a message that
was never sent, and when the same message id is sent twice.
''',
                "files": [{"name": "main.py", "content": r'''
OPS = ("local", "send", "recv")

LOG = [
    ("A", "local", None),
    ("A", "send", "m1"),
    ("B", "local", None),
    ("B", "recv", "m1"),
    ("B", "send", "m2"),
    ("C", "local", None),
    ("C", "recv", "m2"),
    ("A", "local", None),
]


def processes(log):
    """Process ids in first-appearance order. ValueError on an unknown op."""
    # your code here


def lamport_clocks(log):
    """One Lamport stamp per event, in log order."""
    # your code here


def vector_clocks(log):
    """One {process: counter} dict per event, in log order."""
    # your code here


def compare_vectors(a, b):
    """One of before, after, equal, concurrent."""
    # your code here


def concurrent_pairs(log):
    """Sorted (i, j) index pairs, i < j, whose vector clocks are concurrent."""
    # your code here


def lamport_blind_spots(log):
    """Concurrent pairs that Lamport stamps would nonetheless order i before j."""
    # your code here


print("lamport:", lamport_clocks(LOG))
print("concurrent:", concurrent_pairs(LOG))
print("blind spots:", lamport_blind_spots(LOG))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
OPS = ("local", "send", "recv")

LOG = [
    ("A", "local", None),
    ("A", "send", "m1"),
    ("B", "local", None),
    ("B", "recv", "m1"),
    ("B", "send", "m2"),
    ("C", "local", None),
    ("C", "recv", "m2"),
    ("A", "local", None),
]


def processes(log):
    """Process ids in first-appearance order. ValueError on an unknown op."""
    seen = []
    for proc, op, _arg in log:
        if op not in OPS:
            raise ValueError("unknown operation " + repr(op))
        if proc not in seen:
            seen.append(proc)
    return seen


def lamport_clocks(log):
    """One Lamport stamp per event, in log order."""
    counters = {p: 0 for p in processes(log)}
    carried = {}
    stamps = []
    for i, (proc, op, arg) in enumerate(log):
        if op == "recv":
            if arg not in carried:
                raise ValueError("event %d receives unsent message %r" % (i, arg))
            # the receive must land strictly after the send it observed
            counters[proc] = max(counters[proc], carried[arg]) + 1
        else:
            counters[proc] += 1
        if op == "send":
            if arg in carried:
                raise ValueError("message %r sent twice" % (arg,))
            carried[arg] = counters[proc]
        stamps.append(counters[proc])
    return stamps


def vector_clocks(log):
    """One {process: counter} dict per event, in log order."""
    procs = processes(log)
    clocks = {p: {q: 0 for q in procs} for p in procs}
    carried = {}
    stamps = []
    for i, (proc, op, arg) in enumerate(log):
        vec = clocks[proc]
        if op == "recv":
            if arg not in carried:
                raise ValueError("event %d receives unsent message %r" % (i, arg))
            for q, v in carried[arg].items():
                if v > vec.get(q, 0):
                    vec[q] = v
        vec[proc] += 1
        if op == "send":
            if arg in carried:
                raise ValueError("message %r sent twice" % (arg,))
            carried[arg] = dict(vec)
        stamps.append(dict(vec))
    return stamps


def compare_vectors(a, b):
    """One of before, after, equal, concurrent."""
    keys = set(a) | set(b)
    less = any(a.get(k, 0) < b.get(k, 0) for k in keys)
    more = any(a.get(k, 0) > b.get(k, 0) for k in keys)
    if less and more:
        return "concurrent"
    if less:
        return "before"
    if more:
        return "after"
    return "equal"


def concurrent_pairs(log):
    """Sorted (i, j) index pairs, i < j, whose vector clocks are concurrent."""
    vecs = vector_clocks(log)
    pairs = []
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            if compare_vectors(vecs[i], vecs[j]) == "concurrent":
                pairs.append((i, j))
    return pairs


def lamport_blind_spots(log):
    """Concurrent pairs that Lamport stamps would nonetheless order i before j."""
    stamps = lamport_clocks(log)
    return [(i, j) for (i, j) in concurrent_pairs(log) if stamps[i] < stamps[j]]


print("lamport:", lamport_clocks(LOG))
print("concurrent:", concurrent_pairs(LOG))
print("blind spots:", lamport_blind_spots(LOG))
'''}],
                "hints": [
                    "Keep one dict of counters keyed by process, and a second dict mapping message id to the stamp (or vector) that message carried.",
                    "For a receive, merge first and increment second — `max` over the carried value, then `+ 1` for the receive event itself.",
                    "Store a *copy* of the vector when a message is sent (`dict(vec)`), or later increments will mutate the message in flight.",
                    "`compare_vectors` needs both a strictly-less and a strictly-greater flag: both true means concurrent, neither true means equal.",
                ],
                "tests": [
                    {"name": "processes and op validation", "code": r'''
assert processes(LOG) == ["A", "B", "C"], f"processes(LOG) gave {processes(LOG)!r}"
assert processes([]) == [], "An empty log has no processes"
try:
    processes([("A", "teleport", None)])
    assert False, "An unknown op should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Lamport stamps on the reference log", "code": r'''
_got = lamport_clocks(LOG)
assert _got == [1, 2, 1, 3, 4, 1, 5, 3], f"lamport_clocks(LOG) gave {_got!r}"
assert lamport_clocks([]) == [], "An empty log has no stamps"
_solo = lamport_clocks([("A", "local", None), ("A", "local", None)])
assert _solo == [1, 2], f"A single process should just count up, got {_solo!r}"
'''},
                    {"name": "Vector clocks on the reference log", "code": r'''
_v = vector_clocks(LOG)
assert _v[1] == {"A": 2, "B": 0, "C": 0}, f"event 1 vector is {_v[1]!r}"
assert _v[3] == {"A": 2, "B": 2, "C": 0}, f"event 3 vector is {_v[3]!r}"
assert _v[6] == {"A": 2, "B": 3, "C": 2}, f"event 6 vector is {_v[6]!r}"
assert _v[7] == {"A": 3, "B": 0, "C": 0}, f"event 7 vector is {_v[7]!r}"
assert _v[1] is not _v[7], "Each event needs its own dict, not a shared one"
'''},
                    {"name": "compare_vectors classifies the four cases", "code": r'''
_a = {"A": 1, "B": 0}
_b = {"A": 2, "B": 0}
_c = {"A": 0, "B": 1}
assert compare_vectors(_a, _b) == "before", f"got {compare_vectors(_a, _b)!r}"
assert compare_vectors(_b, _a) == "after", f"got {compare_vectors(_b, _a)!r}"
assert compare_vectors(_a, dict(_a)) == "equal", "Identical vectors are equal"
assert compare_vectors(_a, _c) == "concurrent", f"got {compare_vectors(_a, _c)!r}"
'''},
                    {"name": "concurrent_pairs finds all twelve", "code": r'''
_want = [(0, 2), (0, 5), (1, 2), (1, 5), (2, 5), (2, 7),
         (3, 5), (3, 7), (4, 5), (4, 7), (5, 7), (6, 7)]
_got = concurrent_pairs(LOG)
assert _got == _want, f"concurrent_pairs(LOG) gave {_got!r}"
assert concurrent_pairs([("A", "local", None)]) == [], "One event cannot be concurrent with itself"
'''},
                    {"name": "Lamport blind spots", "code": r'''
_got = lamport_blind_spots(LOG)
assert _got == [(2, 7), (5, 7)], f"lamport_blind_spots(LOG) gave {_got!r}"
_chain = [("A", "send", "x"), ("B", "recv", "x")]
assert lamport_blind_spots(_chain) == [], "A causal chain has no blind spots"
'''},
                    {"name": "Malformed logs are refused", "code": r'''
for _fn in (lamport_clocks, vector_clocks):
    try:
        _fn([("A", "recv", "ghost")])
        assert False, f"{_fn.__name__} should reject a receive with no matching send"
    except ValueError:
        pass
    try:
        _fn([("A", "send", "m"), ("A", "send", "m")])
        assert False, f"{_fn.__name__} should reject a duplicated message id"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Consensus: Raft",
            "summary": "Leader election and log replication on a deterministic message network.",
            "concepts": [
                "State machine replication: identical logs applied in order give identical state",
                "Terms as a logical clock — every message carries one, a larger term wins",
                "Election safety: one vote per server per term, so at most one leader per term",
                "The election restriction — a candidate needs a log at least as up to date as the voter's",
                "Log matching: identical (index, term) implies identical prefixes",
                "nextIndex backtracking is how a new leader repairs a divergent follower",
                "A leader may only commit an entry from its *own* term; earlier entries commit indirectly",
                "A split vote wastes a term; randomised timeouts, not cleverness, break the tie",
            ],
            "quiz": {
                "title": "Terms, votes, and what a leader may commit",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A follower at term 5 receives an `AppendEntries` carrying term 4. What does it do?",
                        "opts": [
                            "Adopts term 4 and appends the entries",
                            "Rejects it with `success=False` and stays at term 5",
                            "Starts an election at term 6",
                            "Appends the entries but refuses to advance its commit index",
                        ],
                        "a": 1,
                        "why": r"""
A message from a smaller term comes from a leader that has already been superseded and
does not know it yet. Rejecting it is the whole mechanism: the reply carries the
follower's own term, the stale leader sees a term larger than its own, and rule 1 makes
it step down. Adopting the smaller term would run history backwards. Appending the
entries — with or without committing them — would let a deposed leader keep writing to a
follower that has moved on, which is exactly the divergence the term is there to prevent.
Nothing here calls for an election: the follower has heard from a leader, just not a
current one.
""",
                    },
                    {
                        "q": "Why may a leader not commit an entry from an earlier term merely because a majority now stores it?",
                        "opts": [
                            "Because such an entry can still be overwritten by a future leader, even with a majority holding it",
                            "Because entries from earlier terms are always duplicates of entries it already has",
                            "Because it cannot tell which term an entry came from",
                            "Because `match_index` from a follower in an earlier term cannot be trusted",
                        ],
                        "a": 0,
                        "why": r"""
This is Figure 8 of the Raft paper, and it is the least obvious rule in the protocol. A
majority holding an old-term entry is not enough, because a server whose log lacks that
entry can still win a later election — the election restriction compares the last entry,
not the whole log — and will then force its own log onto everyone. Committing it would
mean an applied entry disappearing. The fix is the rule in the lab's `advance_commit`:
only count an entry of your *own* term, and everything before it commits with it through
log matching. A leader can always read the term off an entry, since it is stored beside
the command, and `match_index` is reported by the follower's own current term.
""",
                    },
                    {
                        "q": "Four servers, and the vote splits two-two. What is the state of the cluster at the end of that term?",
                        "opts": [
                            "The server with the lowest id takes office",
                            "Both candidates lead, each with its own half",
                            "No leader, nothing committed, nothing lost — a later term settles it",
                            "Deadlocked until an operator intervenes",
                        ],
                        "a": 2,
                        "why": r"""
A term that elects nobody is simply wasted: no entry can commit without a leader, and no
entry is damaged either. The retry is not cleverness, it is randomised timeouts — the two
candidates wake at different moments, one gets its requests out first, and the split does
not repeat. The lab reproduces this exactly, dropping all but two `RequestVote` messages
so both candidates stall on two votes out of four, then letting term 2 resolve it.
Lowest-id tie-breaking would make elections deterministic and is a real design, but it is
not Raft's, and two leaders in one term is precisely what one-vote-per-server-per-term
rules out.
""",
                    },
                    {
                        "q": "A voter refuses any candidate whose log is behind its own. What would break if it did not?",
                        "opts": [
                            "Two leaders could hold the same term at once",
                            "A leader could take office missing committed entries and would then delete them everywhere else",
                            "The leader's log would grow without bound",
                            "Followers would never learn the commit index",
                        ],
                        "a": 1,
                        "why": r"""
Two guarantees are easy to confuse here. One vote per server per term is what stops two
leaders in a term, and it holds with or without the log comparison. The election
restriction does something else: it keeps a server that is missing committed entries out
of office. Without it, such a server could win, and since a leader repairs followers by
overwriting them, it would erase entries that had already been acknowledged to a client.
The comparison is `last_log_term` first, then `last_log_index` — the term dominates,
because a longer log from an older term is the log that is stale.
""",
                    },
                    {
                        "q": "A leader is cut off into a minority partition holding two of five servers. What can it still do?",
                        "opts": [
                            "Nothing — it stops the moment the partition forms",
                            "Commit entries, since it is still the leader of the highest term it has seen",
                            "Elect a replacement leader on its own side of the partition",
                            "Accept client commands and replicate them, but never commit any of them",
                        ],
                        "a": 3,
                        "why": r"""
The leader has no way to detect the partition, so it keeps behaving normally: it appends
commands, sends `AppendEntries` to everyone, and gets replies from the one follower it
can still reach. What it cannot do is count to three. `advance_commit` needs a majority
including itself, and two is not a majority of five, so `commit_index` stops moving —
which is what the lab asserts after `isolate(["a", "b"])`. Meanwhile the other three
elect a leader at a higher term. When the link heals, the old leader sees that term,
steps down, and its uncommitted entries are overwritten. Availability was traded for
consistency, and this is the trade being made.
""",
                    },
                ],
            },
            "blanks": {
                "title": "One election and one entry, delivered by hand",
                "minutes": 9,
                "caption": "message trace — three servers, nothing in flight",
                "lang": "text",
                "brief": r"""
Below is what the deterministic network actually carries during the simplest useful
sequence: an election, a client command, and the two rounds it takes for everyone to
agree that the command is committed. The interesting holes are the boundary values — the
conventions for an empty log, and the one-round lag between the leader knowing something
and the follower being told.

Read it as a transcript, not as code. Every line is a message that moved because
`deliver()` was called.
""",
                "listing": """three servers, all at term 0 with empty logs. nothing moves until a message is
delivered. the empty heartbeat round that follows the election is left out; it changes
none of the values below.

n1         start_election()      -> term 1, votes for itself
n1 -> n2   RequestVote           term=1  last_log_index=-1  last_log_term=___
n2 -> n1   RequestVoteReply      term=1  granted=True
n1         2 votes of 3          -> leader of term 1

n1         client_append("set x 1")            -> index 0, entry (1, "set x 1")
n1 -> n2   AppendEntries         term=1  prev_log_index=___  prev_log_term=0
                                 entries=[(1, "set x 1")]  leader_commit=-1
n2 -> n1   AppendEntriesReply    term=1  success=True  match_index=___
n1         advance_commit()      -> commit_index=___    # n1 and n2 both hold index 0
n2         commit_index is still ___                    # nothing has told it otherwise

n1 -> n2   AppendEntries         term=1  prev_log_index=0  prev_log_term=1
                                 entries=[]  leader_commit=0
n2         commit_index=0
""",
                "blanks": [
                    {
                        "prompt": "What last-entry term does a candidate with an empty log advertise?",
                        "hole": "?",
                        "opts": ["0", "-1", "1", "None"],
                        "a": 0,
                        "why": "An empty log has last index -1 and last term 0. The two conventions differ on purpose: the index is a position and there is no position yet, while the term is compared with `>` and `>=`, so it has to be a number below every real term.",
                        "whys": [
                            "An empty log has last index -1 and last term 0. The two conventions differ on purpose: the index is a position and there is no position yet, while the term is compared with `>` and `>=`, so it has to be a number below every real term.",
                            "-1 is the index convention leaking into the term. It would still order correctly against real terms, but it disagrees with every other node's idea of 'no entries yet', and the comparison in the vote handler is between two nodes' answers.",
                            "Claiming term 1 asserts an entry the candidate does not have, and a voter that genuinely holds a term-1 entry would then find the candidate's log 'as up to date' as its own and vote for it.",
                            "`None` cannot be compared with an integer at all — the vote handler's `>` would raise before it decided anything.",
                        ],
                    },
                    {
                        "prompt": "The new leader has one entry at index 0. What does it put in `prev_log_index` for a follower it has not spoken to yet?",
                        "hole": "?",
                        "opts": ["0", "-1", "1", "None"],
                        "a": 1,
                        "why": "`become_leader` set `next_index` to `last_log_index() + 1`, which was 0 when the log was empty, so `prev` is -1: there is no entry before index 0, and the consistency check is vacuously satisfied.",
                        "whys": [
                            "That would claim the follower already holds index 0 and ask it to check the entry being sent against itself. The follower's log is empty, the check fails, and the leader backs off an index for no reason.",
                            "`become_leader` set `next_index` to `last_log_index() + 1`, which was 0 when the log was empty, so `prev` is -1: there is no entry before index 0, and the consistency check is vacuously satisfied.",
                            "Index 1 does not exist on either side. The follower would reject, the leader would decrement `next_index` twice, and the round trip is wasted — which is exactly the backtracking that exists for genuinely divergent logs, not for a fresh one.",
                            "The reply path arithmetic is `prev_log_index + len(entries)`, so a non-numeric sentinel breaks `match_index` before the follower ever answers.",
                        ],
                    },
                    {
                        "prompt": "The follower appended one entry onto an empty log. What `match_index` does it report?",
                        "hole": "?",
                        "opts": ["-1", "0", "1", "2"],
                        "a": 1,
                        "why": "`match_index = prev_log_index + len(entries)` = -1 + 1 = 0. It is the index of the highest entry the follower now holds, not a count of entries — which is why an empty log reports -1 rather than 0.",
                        "whys": [
                            "-1 is what a rejection reports, meaning 'nothing agreed'. Reporting it after a successful append would leave the leader convinced no follower has the entry, and the commit index would never move.",
                            "`match_index = prev_log_index + len(entries)` = -1 + 1 = 0. It is the index of the highest entry the follower now holds, not a count of entries — which is why an empty log reports -1 rather than 0.",
                            "1 is the *number* of entries the follower holds, and the off-by-one between a count and a 0-based index is the classic way to commit an entry nobody has.",
                            "2 is past the end of the follower's log entirely; the leader would set `next_index` to 3 and start sending from a position that does not exist.",
                        ],
                    },
                    {
                        "prompt": "The leader holds index 0 and knows n2 does too. How far can it commit?",
                        "hole": "?",
                        "opts": ["-1", "0", "1", "2"],
                        "a": 1,
                        "why": "Index 0 is an entry of the leader's own term, and two of three servers hold it — the leader counts itself. That is a majority, so `commit_index` becomes 0.",
                        "whys": [
                            "Leaving it at -1 is what happens if the leader forgets to count itself: it would then need both followers for a three-node cluster, which is a majority of the followers rather than a majority of the servers.",
                            "Index 0 is an entry of the leader's own term, and two of three servers hold it — the leader counts itself. That is a majority, so `commit_index` becomes 0.",
                            "There is no index 1 yet; only one command has been appended.",
                            "Nor an index 2. `advance_commit` scans down from `last_log_index()`, so it never considers a position past the end of the log.",
                        ],
                    },
                    {
                        "prompt": "At that same moment, what is n2's commit index?",
                        "hole": "?",
                        "opts": ["-1", "0", "1", "None"],
                        "a": 0,
                        "why": "Still -1. The follower stored the entry, but `leader_commit` on the message that carried it was -1, because the leader had not yet counted the majority. It learns the entry is committed on the next `AppendEntries`, one full round later.",
                        "whys": [
                            "Still -1. The follower stored the entry, but `leader_commit` on the message that carried it was -1, because the leader had not yet counted the majority. It learns the entry is committed on the next `AppendEntries`, one full round later.",
                            "0 is what the follower will hold after the next round. Assuming it here is the same mistake as assuming a client's write is durable everywhere the instant the leader answers — the commit point is a fact the leader discovers and then has to distribute.",
                            "1 is beyond anything either log contains.",
                            "`commit_index` starts at -1 and only ever moves up; it is never absent. The follower having no knowledge of a commit is represented by the number, not by a sentinel.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "When does the leader know it is committed?",
                "minutes": 8,
                "brief": r"""
Commit latency in Raft is not the time to reach every replica; it is the time to reach
*enough* of them. The leader already holds the entry the instant it is appended, so it
needs the round trip to the followers that turn its own copy into a majority — and every
follower slower than those is irrelevant to the answer the client is waiting for.

That is the property worth internalising before tuning anything: a chronically slow
replica costs the cluster nothing at all while enough faster ones are healthy — and it
becomes the machine every commit waits on only once so few of those faster ones are left
that the majority cannot be reached without it.
""",
                "prompt": "How long after the command reaches the leader does the leader know the entry is committed?",
                "note": "Delays are one way; a reply takes the same time back. Processing and disk time are zero.",
                "figure": "`n1 (leader) —8ms— n2 · —11ms— n3 · —40ms— n4 · —95ms— n5` — five servers, one-way delays from the leader.",
                "given": [
                    {"label": "Servers", "value": "5 (one leader, four followers)"},
                    {"label": "Leader to n2", "value": "8 ms one way"},
                    {"label": "Leader to n3", "value": "11 ms one way"},
                    {"label": "Leader to n4", "value": "40 ms one way"},
                    {"label": "Leader to n5", "value": "95 ms one way"},
                    {"label": "Processing and disk", "value": "0 ms"},
                ],
                "aside": "The same cluster with n4 and n5 removed commits faster, not slower: a "
                         "majority of three is two, the leader is one of them, so n2's reply at "
                         "16 ms is on its own enough. What the smaller cluster gives up is margin. "
                         "Lose n2 and every commit falls onto n3 at 22 ms, and the tail latency of "
                         "the cluster becomes the tail latency of that one machine.",
                "answer": 22,
                "tol": 0.5,
                "unit": "ms",
                "hint": "A majority of five is three, and the leader is one of them at zero cost. "
                        "Which follower's reply is the one that tips the count over?",
                "wrong": "Two traps sit here. Forgetting that the leader counts itself pushes you "
                         "to the third-fastest follower, and quoting a one-way delay forgets that "
                         "the leader learns nothing until the acknowledgement comes back.",
                "why": "A majority of five is three. The leader has the entry at $t = 0$, so two "
                       "follower acknowledgements are enough. `AppendEntries` reaches n2 at 8 ms "
                       "and n3 at 11 ms; their replies land at 16 ms and 22 ms. At 22 ms the "
                       "leader counts itself, n2 and n3 — a majority — and `advance_commit` moves. "
                       "n4 and n5 contribute nothing to the answer, and would not even if they "
                       "were down. The client's own latency is this plus the leader's reply to it; "
                       "the *follower's* view of the commit arrives a further round later, on the "
                       "next `AppendEntries`.",
            },
            "lab": {
                "title": "Raft election and log replication",
                "runtime": "python",
                "minutes": 90,
                "brief": r'''
`cluster.py` is given and read-only: a deterministic network with a FIFO queue,
cuttable links and a message dropper. Nothing moves unless you call
`deliver()`. You write `raft.py`.

## Message shapes

```text
RequestVote        term src dst last_log_index last_log_term
RequestVoteReply   term src dst granted
AppendEntries      term src dst prev_log_index prev_log_term entries leader_commit
AppendEntriesReply term src dst success match_index
```

A log entry is a `(term, command)` tuple. Indices are 0-based, so an empty log
has `last_log_index() == -1` and `last_log_term() == 0`. `commit_index` starts
at `-1`.

## `RaftNode(node_id, peers)`

Already initialised for you. Implement:

- `last_log_index()`, `last_log_term()`, `majority()` — majority is over the
  whole cluster, so `(len(peers) + 1) // 2 + 1`.
- `become_follower(term)` — state `"follower"`, adopt the term, clear
  `voted_for` and `votes`.
- `become_leader()` — state `"leader"`; every peer gets
  `next_index = last_log_index() + 1` and `match_index = -1`.
- `start_election()` — become a candidate, bump the term, vote for yourself,
  and return one `RequestVote` per peer. In a one-node cluster you are already
  the leader.
- `client_append(command)` — leader only; append `(self.term, command)` and
  return the new index. `ValueError` otherwise.
- `replicate()` — one `AppendEntries` per peer built from that peer's
  `next_index`. An empty `entries` list is a heartbeat. Non-leaders return `[]`.
- `handle(msg)` — dispatch. First: any message whose term exceeds yours makes
  you a follower at that term. An unknown `type` raises `ValueError`.

## The four handlers

**RequestVote** — grant when the terms match, you have not already voted for
someone else this term, and the candidate's log is at least as up to date
(higher `last_log_term`, or an equal term and an index that is not smaller).

**RequestVoteReply** — ignore unless you are still a candidate in that term and
the vote was granted. Add it; on reaching `majority()`, become leader and return
`replicate()`.

**AppendEntries** — reject with `success=False` when the term is stale, or when
`prev_log_index` is past the end of your log or holds a different term. Otherwise
step down to follower, overwrite from `prev_log_index + 1` where the terms differ,
append the rest, and set
`commit_index = min(leader_commit, prev_log_index + len(entries))` when the
leader is ahead. Reply with `match_index = prev_log_index + len(entries)`.

**AppendEntriesReply** — leaders only, current term only. On success record
`match_index` / `next_index` and try to advance the commit index; send more if
that peer is still behind. On failure decrement `next_index` (never below 0)
and resend.

The commit rule: the highest index `n` above the current `commit_index` such
that `log[n]` has *your* term and a majority of servers (you included) have
`match_index >= n`.

Note what the checks force you to notice — a follower learns an entry is
committed one round *after* the leader does.
''',
                "files": [
                    {"name": "cluster.py", "ro": True, "content": r'''
from collections import deque

from raft import RaftNode


class Cluster:
    """A deterministic message network. Nothing moves unless you tell it to."""

    def __init__(self, node_ids):
        self.node_ids = list(node_ids)
        self.nodes = {nid: RaftNode(nid, [p for p in self.node_ids if p != nid])
                      for nid in self.node_ids}
        self.queue = deque()
        self.down_links = set()
        self.dropped = 0

    def send(self, messages):
        """Queue every message in an outbound list (None is allowed)."""
        for msg in messages or []:
            self.queue.append(msg)
        return self

    def link_down(self, a, b):
        self.down_links.add(frozenset((a, b)))

    def isolate(self, group):
        """Cut every link between group and the rest of the cluster."""
        rest = [n for n in self.node_ids if n not in group]
        for a in group:
            for b in rest:
                self.link_down(a, b)

    def heal(self):
        self.down_links.clear()

    def reachable(self, a, b):
        return frozenset((a, b)) not in self.down_links

    def drop_matching(self, predicate):
        """Remove queued messages for which predicate(msg) is true."""
        kept = deque()
        removed = 0
        while self.queue:
            msg = self.queue.popleft()
            if predicate(msg):
                removed += 1
            else:
                kept.append(msg)
        self.queue = kept
        self.dropped += removed
        return removed

    def deliver(self, limit=10000):
        """FIFO delivery until the queue drains. Replies join the back."""
        moved = 0
        while self.queue and moved < limit:
            msg = self.queue.popleft()
            moved += 1
            if not self.reachable(msg["src"], msg["dst"]):
                self.dropped += 1
                continue
            self.send(self.nodes[msg["dst"]].handle(msg))
        return moved

    def leader(self):
        """The leader of the highest term, or None."""
        leaders = [n for n in self.nodes.values() if n.state == "leader"]
        return max(leaders, key=lambda n: n.term) if leaders else None

    def logs(self):
        return {nid: list(node.log) for nid, node in self.nodes.items()}
'''},
                    {"name": "raft.py", "content": r'''
class RaftNode:
    """One Raft server: follower, candidate or leader."""

    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = list(peers)
        self.state = "follower"
        self.term = 0
        self.voted_for = None
        self.log = []            # list of (term, command)
        self.commit_index = -1
        self.votes = set()
        self.next_index = {}     # peer -> next log index to send
        self.match_index = {}    # peer -> highest index known replicated

    # ---------------------------------------------------------- log helpers
    def last_log_index(self):
        """Index of the final entry, or -1 for an empty log."""
        # your code here

    def last_log_term(self):
        """Term of the final entry, or 0 for an empty log."""
        # your code here

    def majority(self):
        """How many servers of the whole cluster form a majority."""
        # your code here

    # ------------------------------------------------------ role transitions
    def become_follower(self, term):
        """Step down and adopt term."""
        # your code here

    def become_leader(self):
        """Take office and reset the per-peer replication indices."""
        # your code here

    # --------------------------------------------------------------- driving
    def start_election(self):
        """Become a candidate for the next term; return the RequestVote messages."""
        # your code here

    def client_append(self, command):
        """Leader only: append the command and return its index."""
        # your code here

    def replicate(self):
        """Leader only: one AppendEntries per peer, from that peer's next_index."""
        # your code here

    # -------------------------------------------------------------- handling
    def handle(self, msg):
        """Process one message and return the messages it produces."""
        # your code here

    def advance_commit(self):
        """Leader only: raise commit_index as far as the majority allows."""
        # your code here
'''},
                    {"name": "main.py", "content": r'''
from cluster import Cluster

cluster = Cluster(["n1", "n2", "n3"])
cluster.send(cluster.nodes["n1"].start_election())
cluster.deliver()

leader = cluster.leader()
if leader is None:
    print("no leader elected")
else:
    print("leader:", leader.node_id, "term", leader.term)
    leader.client_append("set x 1")
    leader.client_append("set y 2")
    cluster.send(leader.replicate())
    cluster.deliver()
    print("commit after one round:",
          {k: v.commit_index for k, v in cluster.nodes.items()})
    cluster.send(leader.replicate())
    cluster.deliver()
    print("commit after two rounds:",
          {k: v.commit_index for k, v in cluster.nodes.items()})
'''},
                ],
                "main": "main.py",
                "solution": [
                    {"name": "raft.py", "content": r'''
class RaftNode:
    """One Raft server: follower, candidate or leader."""

    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = list(peers)
        self.state = "follower"
        self.term = 0
        self.voted_for = None
        self.log = []            # list of (term, command)
        self.commit_index = -1
        self.votes = set()
        self.next_index = {}     # peer -> next log index to send
        self.match_index = {}    # peer -> highest index known replicated

    # ---------------------------------------------------------- log helpers
    def last_log_index(self):
        """Index of the final entry, or -1 for an empty log."""
        return len(self.log) - 1

    def last_log_term(self):
        """Term of the final entry, or 0 for an empty log."""
        return self.log[-1][0] if self.log else 0

    def majority(self):
        """How many servers of the whole cluster form a majority."""
        return (len(self.peers) + 1) // 2 + 1

    # ------------------------------------------------------ role transitions
    def become_follower(self, term):
        """Step down and adopt term."""
        self.state = "follower"
        self.term = term
        self.voted_for = None
        self.votes = set()

    def become_leader(self):
        """Take office and reset the per-peer replication indices."""
        self.state = "leader"
        nxt = self.last_log_index() + 1
        self.next_index = {p: nxt for p in self.peers}
        self.match_index = {p: -1 for p in self.peers}

    # --------------------------------------------------------------- driving
    def start_election(self):
        """Become a candidate for the next term; return the RequestVote messages."""
        self.state = "candidate"
        self.term += 1
        self.voted_for = self.node_id
        self.votes = {self.node_id}
        if len(self.votes) >= self.majority():
            # a single-server cluster elects itself immediately
            self.become_leader()
            return self.replicate()
        return [{"type": "RequestVote", "term": self.term, "src": self.node_id,
                 "dst": p, "last_log_index": self.last_log_index(),
                 "last_log_term": self.last_log_term()} for p in self.peers]

    def client_append(self, command):
        """Leader only: append the command and return its index."""
        if self.state != "leader":
            raise ValueError("only a leader accepts client commands")
        self.log.append((self.term, command))
        return self.last_log_index()

    def replicate(self):
        """Leader only: one AppendEntries per peer, from that peer's next_index."""
        if self.state != "leader":
            return []
        return [self._append_for(p) for p in self.peers]

    def _append_for(self, peer):
        nxt = self.next_index.get(peer, 0)
        prev = nxt - 1
        prev_term = self.log[prev][0] if prev >= 0 else 0
        return {"type": "AppendEntries", "term": self.term, "src": self.node_id,
                "dst": peer, "prev_log_index": prev, "prev_log_term": prev_term,
                "entries": list(self.log[nxt:]), "leader_commit": self.commit_index}

    # -------------------------------------------------------------- handling
    def handle(self, msg):
        """Process one message and return the messages it produces."""
        if msg["term"] > self.term:
            # rule 1 of the paper: a larger term always wins, whatever we were
            self.become_follower(msg["term"])
        kind = msg["type"]
        if kind == "RequestVote":
            return self._on_request_vote(msg)
        if kind == "RequestVoteReply":
            return self._on_vote_reply(msg)
        if kind == "AppendEntries":
            return self._on_append(msg)
        if kind == "AppendEntriesReply":
            return self._on_append_reply(msg)
        raise ValueError("unknown message type " + repr(kind))

    def _on_request_vote(self, msg):
        granted = False
        if msg["term"] == self.term and self.voted_for in (None, msg["src"]):
            # election restriction: never vote for a log behind our own
            up_to_date = (msg["last_log_term"] > self.last_log_term() or
                          (msg["last_log_term"] == self.last_log_term() and
                           msg["last_log_index"] >= self.last_log_index()))
            if up_to_date:
                granted = True
                self.voted_for = msg["src"]
        return [{"type": "RequestVoteReply", "term": self.term,
                 "src": self.node_id, "dst": msg["src"], "granted": granted}]

    def _on_vote_reply(self, msg):
        if self.state != "candidate" or msg["term"] != self.term or not msg["granted"]:
            return []
        self.votes.add(msg["src"])
        if len(self.votes) >= self.majority():
            self.become_leader()
            return self.replicate()
        return []

    def _on_append(self, msg):
        if msg["term"] < self.term:
            return [self._append_reply(msg["src"], False, -1)]
        self.state = "follower"
        self.term = msg["term"]
        self.votes = set()
        prev = msg["prev_log_index"]
        if prev >= 0 and (prev > self.last_log_index() or
                          self.log[prev][0] != msg["prev_log_term"]):
            return [self._append_reply(msg["src"], False, -1)]
        for offset, entry in enumerate(msg["entries"]):
            i = prev + 1 + offset
            if i < len(self.log):
                if self.log[i][0] != entry[0]:
                    # conflicting term: this entry and everything after it goes
                    del self.log[i:]
                    self.log.append(tuple(entry))
            else:
                self.log.append(tuple(entry))
        match = prev + len(msg["entries"])
        if msg["leader_commit"] > self.commit_index:
            self.commit_index = min(msg["leader_commit"], match)
        return [self._append_reply(msg["src"], True, match)]

    def _append_reply(self, dst, success, match):
        return {"type": "AppendEntriesReply", "term": self.term,
                "src": self.node_id, "dst": dst,
                "success": success, "match_index": match}

    def _on_append_reply(self, msg):
        if self.state != "leader" or msg["term"] != self.term:
            return []
        if msg["success"]:
            self.match_index[msg["src"]] = msg["match_index"]
            self.next_index[msg["src"]] = msg["match_index"] + 1
            self.advance_commit()
            if self.next_index[msg["src"]] <= self.last_log_index():
                return [self._append_for(msg["src"])]
            return []
        # log mismatch: walk back one index and try again
        self.next_index[msg["src"]] = max(0, self.next_index[msg["src"]] - 1)
        return [self._append_for(msg["src"])]

    def advance_commit(self):
        """Leader only: raise commit_index as far as the majority allows."""
        for n in range(self.last_log_index(), self.commit_index, -1):
            if self.log[n][0] != self.term:
                # never commit an old-term entry on its own count
                continue
            count = 1 + sum(1 for p in self.peers if self.match_index.get(p, -1) >= n)
            if count >= self.majority():
                self.commit_index = n
                return
'''},
                ],
                "hints": [
                    "Write `last_log_index`, `last_log_term`, `majority` and the two transitions first — every handler leans on them.",
                    "In `handle`, do the term check once at the top, before dispatching. Rule 1 of the paper applies to every message type.",
                    "`replicate` must build each message from that peer's own `next_index`, so an out-of-date follower gets its missing entries and an up-to-date one gets an empty `entries` list.",
                    "For the commit rule count yourself as a match: `1 + sum(...)`. Skipping that off-by-one is why a 3-node cluster appears to need all three followers.",
                ],
                "tests": [
                    {"name": "Log helpers and majority", "code": r'''
from raft import RaftNode
_n = RaftNode("a", ["b", "c"])
assert _n.last_log_index() == -1, f"an empty log has last index -1, got {_n.last_log_index()!r}"
assert _n.last_log_term() == 0, f"an empty log has last term 0, got {_n.last_log_term()!r}"
assert _n.majority() == 2, f"3 servers need 2 votes, got {_n.majority()!r}"
assert RaftNode("a", ["b", "c", "d", "e"]).majority() == 3, "5 servers need 3"
assert RaftNode("a", []).majority() == 1, "a lone server is its own majority"
_n.log = [(1, "x"), (2, "y")]
assert (_n.last_log_index(), _n.last_log_term()) == (1, 2), "helpers should read the tail"
'''},
                    {"name": "A quiet cluster elects one leader", "code": r'''
from cluster import Cluster
_c = Cluster(["n1", "n2", "n3"])
_c.send(_c.nodes["n1"].start_election())
_c.deliver()
_lead = _c.leader()
assert _lead is not None, "n1 should have won the election"
assert _lead.node_id == "n1", f"leader is {_lead.node_id!r}"
assert _lead.term == 1, f"leader term is {_lead.term!r}, expected 1"
assert [_c.nodes[n].state for n in ("n2", "n3")] == ["follower", "follower"], \
    "the other two must be followers"
assert all(_c.nodes[n].term == 1 for n in _c.node_ids), "every node adopts the new term"
'''},
                    {"name": "Only leaders take client commands", "code": r'''
from cluster import Cluster
_c = Cluster(["n1", "n2", "n3"])
_c.send(_c.nodes["n1"].start_election())
_c.deliver()
try:
    _c.nodes["n2"].client_append("set z 9")
    assert False, "a follower must refuse client_append with ValueError"
except ValueError:
    pass
_idx = _c.nodes["n1"].client_append("set z 9")
assert _idx == 0, f"the first entry sits at index 0, got {_idx!r}"
assert _c.nodes["n1"].log == [(1, "set z 9")], f"log is {_c.nodes['n1'].log!r}"
'''},
                    {"name": "Replication commits, and the commit index follows", "code": r'''
from cluster import Cluster
_c = Cluster(["n1", "n2", "n3"])
_c.send(_c.nodes["n1"].start_election())
_c.deliver()
_lead = _c.leader()
_lead.client_append("a")
_lead.client_append("b")
_c.send(_lead.replicate())
_c.deliver()
assert _lead.commit_index == 1, f"leader commit_index is {_lead.commit_index!r}, expected 1"
assert _c.nodes["n2"].commit_index == -1, \
    "a follower cannot know about the commit until the next AppendEntries"
_c.send(_lead.replicate())
_c.deliver()
assert all(_c.nodes[n].commit_index == 1 for n in _c.node_ids), \
    f"commit indices are {[_c.nodes[n].commit_index for n in _c.node_ids]!r}"
assert len({tuple(v) for v in _c.logs().values()}) == 1, "every log should be identical"
'''},
                    {"name": "A split vote elects nobody, the retry succeeds", "code": r'''
from cluster import Cluster
_s = Cluster(["a", "b", "c", "d"])
_s.send(_s.nodes["a"].start_election())
_s.send(_s.nodes["c"].start_election())
_s.drop_matching(lambda m: m["type"] == "RequestVote"
                 and (m["src"], m["dst"]) not in (("a", "b"), ("c", "d")))
_s.deliver()
assert _s.leader() is None, "two votes out of four is not a majority"
assert _s.nodes["a"].state == "candidate" and _s.nodes["c"].state == "candidate", \
    "both should still be candidates in term 1"
assert len(_s.nodes["a"].votes) == 2, f"a collected {len(_s.nodes['a'].votes)} votes"
_s.send(_s.nodes["a"].start_election())
_s.deliver()
_lead = _s.leader()
assert _lead is not None and _lead.node_id == "a", "the term-2 election should settle it"
assert _lead.term == 2, f"leader term is {_lead.term!r}"
'''},
                    {"name": "The minority side cannot commit", "code": r'''
from cluster import Cluster
_p = Cluster(["a", "b", "c", "d", "e"])
_p.send(_p.nodes["a"].start_election())
_p.deliver()
_old = _p.leader()
_old.client_append("w1")
_old.client_append("w2")
_p.send(_old.replicate())
_p.deliver()
_p.send(_old.replicate())
_p.deliver()
assert all(_p.nodes[n].commit_index == 1 for n in _p.node_ids), "w1 and w2 commit everywhere"
_p.isolate(["a", "b"])
for _i in range(3):
    _old.client_append("orphan%d" % _i)
_p.send(_old.replicate())
_p.deliver()
assert _old.commit_index == 1, \
    f"two of five is no majority, commit_index should stay 1, got {_old.commit_index!r}"
assert len(_p.nodes["b"].log) == 5, "b is still reachable from a, so it takes the entries"
assert len(_p.nodes["c"].log) == 2, "c is cut off and must not see them"
'''},
                    {"name": "A new term on the majority side wins", "code": r'''
_p.send(_p.nodes["c"].start_election())
_p.deliver()
_new = _p.leader()
assert _new is not None and _new.node_id == "c", f"expected c to win, got {_new and _new.node_id!r}"
assert _new.term == 2, f"new leader term is {_new.term!r}"
assert len(_new.votes) == 3, f"c should have three of five votes, got {len(_new.votes)}"
_new.client_append("z1")
_p.send(_new.replicate())
_p.deliver()
_p.send(_new.replicate())
_p.deliver()
assert _new.commit_index == 2, f"c should commit its own term-2 entry, got {_new.commit_index!r}"
'''},
                    {"name": "Healing the partition converges every log", "code": r'''
_p.heal()
for _round in range(3):
    _p.send(_p.nodes["c"].replicate())
    _p.deliver()
_logs = _p.logs()
assert len({tuple(v) for v in _logs.values()}) == 1, \
    "after the heal every log must match: " + repr(_logs)
assert _logs["a"] == [(1, "w1"), (1, "w2"), (2, "z1")], \
    f"the orphaned entries should be gone, a has {_logs['a']!r}"
assert _p.nodes["a"].state == "follower" and _p.nodes["a"].term == 2, \
    "the old leader steps down when it sees term 2"
assert all(_p.nodes[n].commit_index == 2 for n in _p.node_ids), \
    f"commit indices are {[_p.nodes[n].commit_index for n in _p.node_ids]!r}"
'''},
                    {"name": "Unknown message types are refused", "code": r'''
from raft import RaftNode
_n = RaftNode("a", ["b", "c"])
try:
    _n.handle({"type": "Gossip", "term": 0, "src": "b", "dst": "a"})
    assert False, "an unknown message type should raise ValueError"
except ValueError:
    pass
assert _n.replicate() == [], "a follower has nothing to replicate"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Replication and tunable consistency",
            "summary": "A quorum store with configurable N, R and W, plus read repair.",
            "concepts": [
                "Leaderless replication: the client's coordinator writes to W and reads from R",
                "R + W > N forces every read quorum to intersect every write quorum",
                "Intersection gives read-your-writes only if the newest version wins the merge",
                "W > N/2 is the separate condition that stops two concurrent writes both succeeding",
                "Last-writer-wins by version discards data; the alternative is sibling values",
                "Read repair is opportunistic anti-entropy carried on the read path",
                "Availability versus staleness is a dial, not a binary — this is PACELC's ELC half",
            ],
            "quiz": {
                "title": "Turning the dials",
                "minutes": 8,
                "questions": [
                    {
                        "q": "With $N = 5$, which setting guarantees a read sees the last completed write while keeping reads as cheap as possible?",
                        "opts": [
                            "$R = 5$, $W = 1$",
                            "$R = 3$, $W = 3$",
                            "$R = 1$, $W = 5$",
                            "$R = 2$, $W = 3$",
                        ],
                        "a": 2,
                        "why": r"""
The guarantee needs $R + W > N$. That rules out $R = 2, W = 3$ immediately, since $5$ is
not greater than $5$ — the read set and the write set can be disjoint, which is the case
the lab reproduces on purpose. Of the three that qualify, $R = 1$ is the cheapest read,
and the bill arrives on the other side: $W = 5$ means every replica must be up for any
write to succeed. $R = 3, W = 3$ is the balanced choice most stores default to, and
$R = 5, W = 1$ is the mirror image — writes that survive almost anything, reads that
need the entire cluster. The condition does not pick a point on the line; it only says
which points are on it.
""",
                    },
                    {
                        "q": "$R + W > N$ holds and a write has returned successfully. What is a later read guaranteed to do?",
                        "opts": [
                            "Contact at least one replica that acknowledged that write",
                            "Return that write's value, whatever the merge rule is",
                            "Contact every replica that acknowledged that write",
                            "Avoid contacting any replica that is behind",
                        ],
                        "a": 0,
                        "why": r"""
Intersection is all the arithmetic buys you: the two sets are too large to fit in $N$
replicas without sharing at least one. Turning that overlap into read-your-writes takes a
second ingredient — a version on every value and a merge that keeps the highest. Without
it the coordinator holds one fresh answer and some stale ones and no way to tell them
apart, which is the whole reason the store carries version numbers rather than bare
values. The read certainly does not reach every acknowledging replica; it stops the
moment it has $R$ responses. And it will often include a replica that is behind — read
repair exists precisely because it does.
""",
                    },
                    {
                        "q": "Why is $W > N/2$ a separate condition from $R + W > N$?",
                        "opts": [
                            "It is a stronger form of the same condition and implies it",
                            "It forces two concurrent writes to share a replica, so one of them can be seen as older",
                            "It guarantees the read quorum is also a majority",
                            "It only matters when read repair is switched off",
                        ],
                        "a": 1,
                        "why": r"""
The two conditions constrain different pairs of quorums. $R + W > N$ makes a read set
meet a write set. $W > N/2$ makes two *write* sets meet each other, so at least one
replica sees both writes and can order them by version — without it, two clients can
write disjoint quorums, both succeed, and no replica anywhere has grounds to call either
one older. It is not the stronger condition: $N = 5, W = 3, R = 1$ satisfies $W > N/2$
and fails $R + W > N$, so a read can still miss. It says nothing about $R$, and read
repair changes when replicas converge, not whether two writes were ever comparable.
""",
                    },
                    {
                        "q": "The coordinator merges $R$ answers by keeping the highest version. What does that quietly discard?",
                        "opts": [
                            "Nothing — the highest version is by definition the most recent write",
                            "The version numbers, which is why read repair has to run before the merge",
                            "A concurrent update that happened to draw a lower version",
                            "Every response that arrives after the first one",
                        ],
                        "a": 2,
                        "why": r"""
Versions are a total order; the writes that produced them were not. Two clients that both
read the old value and both write produce two values that are genuinely concurrent, and
last-writer-wins picks one and drops the other with no report to anyone. That is a real
choice, not a bug — it is cheap, it always converges, and for a "current temperature" it
is exactly right. For a shopping cart it is wrong, which is why Dynamo keeps both values
as siblings and hands the merge to the application, and why that cart is famous for
resurrecting a deleted item: union is a safe merge, and it never removes.
""",
                    },
                    {
                        "q": "A write with $W = 2$ raised a quorum error after one replica had already stored the value. What is now true?",
                        "opts": [
                            "The value sits on that one replica, and anti-entropy will spread it",
                            "The value is discarded, because the write never reached its quorum",
                            "The value sits on that one replica and is rolled back by the next read",
                            "The coordinator retries the write at a lower $W$",
                        ],
                        "a": 0,
                        "why": r"""
There is no rollback anywhere in this design — no undo log, no two-phase commit, nothing
that could take a value back off a replica that has already stored it. A failed write is
not an absent write; it is a write with an unknown outcome, and read repair or anti-entropy
will happily finish the job the coordinator gave up on. The lab asserts exactly this after
a `QuorumError`, and the client is left in the genuinely awkward position of having been
told "no" about something that may yet become true. Retrying at a lower $W$ would be a
policy decision, and a store that made it silently would be lying about its own
guarantees.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Sizing the quorums for a keyspace",
                "minutes": 8,
                "caption": "carts.yaml — four decisions, no code",
                "lang": "yaml",
                "brief": r"""
Every quorum store puts these dials in a config file and every one of them ships a
default that is wrong for somebody. Here the requirements are stated, so each dial has
exactly one defensible value — which is the point of the exercise: the settings are not
a matter of taste once you have written down what the service must survive.
""",
                "listing": """# keyspace: carts
#
# Five replicas per key. The service must keep taking writes while a whole rack
# (two of the five nodes) is down, and a read must never miss a write that was
# acknowledged to the client.

replicas: 5
write_quorum: ___                 # W, as large as the rack outage still allows
read_quorum: ___                  # R, the smallest that pairs with that W
merge: ___                        # how the coordinator turns R answers into one
misses_an_acknowledged_write: ___ # the consequence of the three settings above
""",
                "blanks": [
                    {
                        "prompt": "How large may W be if two of the five nodes are down?",
                        "hole": "?",
                        "opts": ["2", "3", "4", "5"],
                        "a": 1,
                        "why": "With two nodes down only three can acknowledge, so W = 3 is the largest value a write can still satisfy during the outage. Every larger W turns a rack failure into a total write outage.",
                        "whys": [
                            "W = 2 would work, but it gives up durability the outage did not force you to give up — and it drags R up to 4 to keep the pairing, making every read more expensive than it needs to be.",
                            "With two nodes down only three can acknowledge, so W = 3 is the largest value a write can still satisfy during the outage. Every larger W turns a rack failure into a total write outage.",
                            "W = 4 needs four live replicas. The moment the rack goes, every write raises a quorum error — the exact failure the requirement was written to avoid.",
                            "W = 5 demands the whole cluster for every write, so a single node reboot stops writes. This is the setting that makes availability numbers look inexplicable in a post-mortem.",
                        ],
                    },
                    {
                        "prompt": "Given that W, what is the smallest R that still meets the read requirement?",
                        "hole": "?",
                        "opts": ["1", "2", "3", "5"],
                        "a": 2,
                        "why": "R + W > N with N = 5 and W = 3 needs R > 2, so R = 3. At R = 3 the read set and any write set share at least one replica, which is exactly the guarantee that was asked for.",
                        "whys": [
                            "R = 1 gives R + W = 4, which is not greater than 5. A read aimed at the two replicas that were not in the write set misses the write entirely — the failure the lab reproduces deliberately.",
                            "R = 2 gives R + W = 5, and 5 is not greater than 5. This is the near miss worth remembering: the condition is strict, and equality is precisely the case where a read set and a write set can be disjoint.",
                            "R + W > N with N = 5 and W = 3 needs R > 2, so R = 3. At R = 3 the read set and any write set share at least one replica, which is exactly the guarantee that was asked for.",
                            "R = 5 satisfies the condition with room to spare and makes every read depend on every node, so a single failure stops reads — a much worse position than the writes were put in.",
                        ],
                    },
                    {
                        "prompt": "The coordinator has three answers in hand. Which one does it return?",
                        "hole": "?",
                        "opts": ["highest_version", "first_response", "majority_value", "lowest_version"],
                        "a": 0,
                        "why": "The overlap guarantees that one of the answers is at least as new as the last acknowledged write; taking the highest version is what turns that guarantee into the value the client gets back.",
                        "whys": [
                            "The overlap guarantees that one of the answers is at least as new as the last acknowledged write; taking the highest version is what turns that guarantee into the value the client gets back.",
                            "Returning whichever reply arrives first hands the answer to the network. The fastest replica is usually the nearest one, not the best informed, and the intersection argument is wasted.",
                            "Counting votes among replicas is worse than it looks: after a W = 3 write to five replicas, a read of three can easily see two stale copies and one fresh one, and the majority is wrong.",
                            "Keeping the lowest version returns the stalest answer available, and read repair would then push that stale value back over the fresh one.",
                        ],
                    },
                    {
                        "prompt": "With those three settings, how often can a read miss a write the client was told had succeeded?",
                        "hole": "?",
                        "opts": ["never", "sometimes", "only while a node is down", "only during a network partition"],
                        "a": 0,
                        "why": "Never, and that is arithmetic rather than luck: three read replicas and three write replicas cannot both fit inside five without sharing one, and the merge keeps the newest of what comes back.",
                        "whys": [
                            "Never, and that is arithmetic rather than luck: three read replicas and three write replicas cannot both fit inside five without sharing one, and the merge keeps the newest of what comes back.",
                            "'Sometimes' is the honest answer for R + W <= N, and the reason to state the requirement in the config rather than leave the dials to a default.",
                            "A node being down changes which replicas answer, not whether the sets overlap. It can stop the read from assembling R responses at all — that raises an error rather than returning a stale value.",
                            "A partition does not weaken the intersection either. It can leave a coordinator unable to reach R or W replicas, in which case the operation fails loudly; what it cannot do is let a successful read step over a successful write.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Where R + W > N comes from",
                "minutes": 12,
                "vars": ["N", "R", "W", "k"],
                "brief": r"""
A write is acknowledged by a set of $W$ replicas out of $N$. A later read collects
answers from a set of $R$ replicas out of the same $N$. Write $k$ for the number of
replicas that are in both sets.

Nothing below is about distributed systems. It is counting, and the famous condition
falls out of it in two lines.
""",
                "steps": [
                    {
                        "prompt": "Write the number of distinct replicas touched by the two operations together — the size of the union — in terms of $R$, $W$ and $k$.",
                        "answer": "R + W - k",
                        "hint": "Inclusion–exclusion. Adding the two sizes counts each shared replica twice.",
                        "deconstruct": [
                            "A replica in exactly one of the two sets is counted once by $R + W$.",
                            "A replica in both is counted twice, and there are $k$ of those, so subtract $k$.",
                        ],
                    },
                    {
                        "prompt": "Both sets are drawn from the same cluster, so that union cannot exceed $N$. Rearrange $R + W - k \\le N$ to get the smallest value $k$ can take.",
                        "answer": "R + W - N",
                        "hint": "Move $k$ to one side and $N$ to the other; the inequality flips to a lower bound on $k$.",
                        "deconstruct": [
                            "$R + W - k \\le N$ gives $R + W - N \\le k$.",
                            "That is a floor, not an estimate: no choice of the two sets can do worse.",
                        ],
                    },
                    {
                        "prompt": "The read is forced to touch the write when $k \\ge 1$ for every possible pair of sets. What is the largest $N$ for which that still holds, in terms of $R$ and $W$?",
                        "answer": "R + W - 1",
                        "hint": "Set the bound you just derived to at least 1 and solve for $N$.",
                        "deconstruct": [
                            "$R + W - N \\ge 1$ rearranges to $N \\le R + W - 1$.",
                            "Which is the same statement as $R + W > N$, written the other way round.",
                        ],
                    },
                    {
                        "prompt": "Now two *writes*, each acknowledged by $W$ replicas. By the same counting, what is the smallest number of replicas that must have seen both?",
                        "answer": "2 W - N",
                        "hint": "The bound was $R + W - N$ for any two sets of those sizes. Both sets now have size $W$.",
                        "deconstruct": [
                            "Nothing in the counting cared that one set was a read and the other a write.",
                            "Substitute $W$ for $R$ in $R + W - N$.",
                        ],
                    },
                    {
                        "prompt": "Require that overlap to be at least 1 and solve for $W$: two write quorums always share a replica when $W$ exceeds what?",
                        "answer": "\\frac{N}{2}",
                        "hint": "$2W - N \\ge 1$ is $W \\ge (N+1)/2$, and for a whole number of replicas that is the same as $W$ strictly greater than half of $N$.",
                        "deconstruct": [
                            "$2W - N \\ge 1$ gives $2W \\ge N + 1$.",
                            "Divide by two: $W \\ge (N+1)/2$, which for integer $W$ is exactly $W > N/2$.",
                        ],
                    },
                ],
                "closing": r"""
Two different conditions have come out of one piece of counting, and they are about
different things. $R + W > N$ is a read *seeing* a write. $W > N/2$ is two writes seeing
*each other*. A store can satisfy one and fail the other: $N = 5$, $W = 3$, $R = 1$ has
write quorums that always overlap and a read that can still miss both of them entirely.

Notice also what the bound $k \ge R + W - N$ does not promise. It says at least one
replica in the read set holds the write; it says nothing about that replica being the one
whose answer you keep. The version numbers do that half, and a store with quorums and no
versions has bought itself nothing.
""",
            },
            "lab": {
                "title": "A tunable quorum store",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
`store.py` holds the logic; `main.py` is a demo. The checks import from
`store.py`.

## `Replica(node_id)`

A single storage node. `store` maps `key -> (version, value)`; `up` is a
boolean you flip to simulate a crash.

- `get(key)` — the stored `(version, value)` tuple, or `None`. Raises
  `ReplicaDown` when `up` is false.
- `put(key, version, value)` — store it only when it is newer than what is
  held. Returns `True` when the write was taken, `False` when it was rejected
  as stale. Raises `ReplicaDown` when down.

## `QuorumStore(replicas, r, w)`

`N` is `len(replicas)`. Raise `ValueError` for an empty replica list, duplicate
node ids, or an `r` or `w` outside `1..N`.

- `order` — the node ids in the order they were supplied.
- `contact_order(prefer)` — `prefer` first (in the order given), then every
  remaining node in `order`. `None` means just `order`. Raise `ValueError` if
  `prefer` names an unknown node.
- `next_version()` — a monotonically increasing integer, starting at 1.
- `write(key, value, prefer=None)` — take one fresh version, walk
  `contact_order`, skip nodes that raise `ReplicaDown`, and **stop as soon as W
  nodes have acknowledged**. Fewer than W acks raises `QuorumError` — after the
  writes that did land have already landed. Record the ack list in
  `last_write_set` and return the version.
- `read(key, prefer=None, repair=False)` — walk `contact_order`, skip down
  nodes, stop at R responses. Fewer than R raises `QuorumError`. Return the
  highest-versioned `(version, value)` seen, or `None` when every responder was
  empty. Record `last_read_set`. With `repair=True`, push the winner to every
  responder that was behind and record their ids in `last_repaired`.

## `read_your_writes(n, r, w)`

Return whether `r + w > n`. The point of the `prefer` argument is to let you
see this fail: with `N=3, W=2, R=1`, write to `["a", "b"]` and read from
`["c"]` and the read misses. With `R=2` no choice of read set can miss.
''',
                "files": [
                    {"name": "store.py", "content": r'''
class ReplicaDown(Exception):
    """Raised when a coordinator touches a node that is not running."""


class QuorumError(Exception):
    """Raised when a request cannot assemble its R or W quorum."""


class Replica:
    """One storage node holding key -> (version, value)."""

    def __init__(self, node_id):
        self.node_id = node_id
        self.up = True
        self.store = {}

    def get(self, key):
        """The stored (version, value), or None. ReplicaDown when not running."""
        # your code here

    def put(self, key, version, value):
        """Store when strictly newer. True if taken, False if rejected as stale."""
        # your code here


class QuorumStore:
    """A leaderless coordinator with tunable read and write quorums."""

    def __init__(self, replicas, r, w):
        # your code here
        pass

    def contact_order(self, prefer=None):
        """prefer first, then the rest of self.order."""
        # your code here

    def next_version(self):
        """The next coordinator version number, starting at 1."""
        # your code here

    def write(self, key, value, prefer=None):
        """Write to W live replicas; QuorumError if fewer acknowledge."""
        # your code here

    def read(self, key, prefer=None, repair=False):
        """Read from R live replicas and return the newest answer."""
        # your code here


def read_your_writes(n, r, w):
    """True when every read quorum is forced to intersect every write quorum."""
    # your code here
'''},
                    {"name": "main.py", "content": r'''
from store import QuorumStore, Replica, read_your_writes

nodes = [Replica(name) for name in ("a", "b", "c")]
loose = QuorumStore(nodes, r=1, w=2)

version = loose.write("cart:7", "one item", prefer=["a", "b"])
print("wrote version", version, "to", loose.last_write_set)
print("R=1 reading from c:", loose.read("cart:7", prefer=["c"]))
print("read_your_writes(3, 1, 2):", read_your_writes(3, 1, 2))

strict = QuorumStore(nodes, r=2, w=2)
print("R=2 reading from c first:", strict.read("cart:7", prefer=["c"], repair=True))
print("repaired:", strict.last_repaired)
'''},
                ],
                "main": "main.py",
                "solution": [
                    {"name": "store.py", "content": r'''
class ReplicaDown(Exception):
    """Raised when a coordinator touches a node that is not running."""


class QuorumError(Exception):
    """Raised when a request cannot assemble its R or W quorum."""


class Replica:
    """One storage node holding key -> (version, value)."""

    def __init__(self, node_id):
        self.node_id = node_id
        self.up = True
        self.store = {}

    def get(self, key):
        """The stored (version, value), or None. ReplicaDown when not running."""
        if not self.up:
            raise ReplicaDown(self.node_id)
        return self.store.get(key)

    def put(self, key, version, value):
        """Store when strictly newer. True if taken, False if rejected as stale."""
        if not self.up:
            raise ReplicaDown(self.node_id)
        current = self.store.get(key)
        if current is not None and version <= current[0]:
            return False
        self.store[key] = (version, value)
        return True


class QuorumStore:
    """A leaderless coordinator with tunable read and write quorums."""

    def __init__(self, replicas, r, w):
        replicas = list(replicas)
        if not replicas:
            raise ValueError("a store needs at least one replica")
        self.order = [rep.node_id for rep in replicas]
        if len(set(self.order)) != len(self.order):
            raise ValueError("duplicate replica ids: " + repr(self.order))
        self.n = len(replicas)
        if not 1 <= r <= self.n:
            raise ValueError("r must lie in 1..%d, got %r" % (self.n, r))
        if not 1 <= w <= self.n:
            raise ValueError("w must lie in 1..%d, got %r" % (self.n, w))
        self.replicas = {rep.node_id: rep for rep in replicas}
        self.r = r
        self.w = w
        self._clock = 0
        self.last_write_set = []
        self.last_read_set = []
        self.last_repaired = []

    def contact_order(self, prefer=None):
        """prefer first, then the rest of self.order."""
        if prefer is None:
            return list(self.order)
        head = []
        for node_id in prefer:
            if node_id not in self.replicas:
                raise ValueError("unknown replica " + repr(node_id))
            if node_id not in head:
                head.append(node_id)
        return head + [n for n in self.order if n not in head]

    def next_version(self):
        """The next coordinator version number, starting at 1."""
        self._clock += 1
        return self._clock

    def write(self, key, value, prefer=None):
        """Write to W live replicas; QuorumError if fewer acknowledge."""
        version = self.next_version()
        acks = []
        for node_id in self.contact_order(prefer):
            try:
                self.replicas[node_id].put(key, version, value)
            except ReplicaDown:
                continue
            acks.append(node_id)
            if len(acks) == self.w:
                break
        self.last_write_set = acks
        if len(acks) < self.w:
            # note that the acks already collected are NOT rolled back
            raise QuorumError("only %d of %d replicas acknowledged" % (len(acks), self.w))
        return version

    def read(self, key, prefer=None, repair=False):
        """Read from R live replicas and return the newest answer."""
        responses = []
        for node_id in self.contact_order(prefer):
            try:
                got = self.replicas[node_id].get(key)
            except ReplicaDown:
                continue
            responses.append((node_id, got))
            if len(responses) == self.r:
                break
        self.last_read_set = [node_id for node_id, _ in responses]
        self.last_repaired = []
        if len(responses) < self.r:
            raise QuorumError("only %d of %d replicas answered" % (len(responses), self.r))
        best = None
        for _node_id, got in responses:
            if got is not None and (best is None or got[0] > best[0]):
                best = got
        if repair and best is not None:
            for node_id, got in responses:
                if got is None or got[0] < best[0]:
                    try:
                        self.replicas[node_id].put(key, best[0], best[1])
                        self.last_repaired.append(node_id)
                    except ReplicaDown:
                        pass
        return best


def read_your_writes(n, r, w):
    """True when every read quorum is forced to intersect every write quorum."""
    return r + w > n
'''},
                ],
                "hints": [
                    "`put` rejects anything with `version <= current[0]`; a fresh key has no current version, so it always takes the first write.",
                    "`write` and `read` both stop the moment the quorum is satisfied — that early exit is exactly what makes a non-overlapping read possible.",
                    "A failed write is not undone. Collect the acks, then raise, and say so in the exception message.",
                    "Read repair happens after the winner is chosen, and only touches the replicas that were actually in the read set.",
                ],
                "tests": [
                    {"name": "Replica stores newest-wins and reports down", "code": r'''
from store import Replica, ReplicaDown
_rep = Replica("a")
assert _rep.get("k") is None, "an unwritten key reads as None"
assert _rep.put("k", 5, "five") is True, "the first write is always taken"
assert _rep.get("k") == (5, "five"), f"get gave {_rep.get('k')!r}"
assert _rep.put("k", 3, "three") is False, "an older version must be rejected"
assert _rep.put("k", 5, "again") is False, "an equal version is not newer"
assert _rep.get("k") == (5, "five"), "a rejected write must not change the store"
_rep.up = False
for _call in (lambda: _rep.get("k"), lambda: _rep.put("k", 9, "x")):
    try:
        _call()
        assert False, "a down replica should raise ReplicaDown"
    except ReplicaDown:
        pass
'''},
                    {"name": "Constructor validation", "code": r'''
from store import QuorumStore, Replica
for _bad in [([], 1, 1), ([Replica("a"), Replica("a")], 1, 1),
             ([Replica("a"), Replica("b")], 0, 1), ([Replica("a"), Replica("b")], 1, 3),
             ([Replica("a"), Replica("b")], 3, 1)]:
    try:
        QuorumStore(*_bad)
        assert False, f"QuorumStore with r/w/replicas {_bad[1:]!r} should raise ValueError"
    except ValueError:
        pass
_ok = QuorumStore([Replica("a"), Replica("b"), Replica("c")], r=2, w=2)
assert _ok.n == 3 and _ok.order == ["a", "b", "c"], f"order is {_ok.order!r}"
'''},
                    {"name": "contact_order puts the preference first", "code": r'''
from store import QuorumStore, Replica
_s = QuorumStore([Replica(x) for x in "abcd"], r=2, w=2)
assert _s.contact_order() == ["a", "b", "c", "d"], f"got {_s.contact_order()!r}"
assert _s.contact_order(["c"]) == ["c", "a", "b", "d"], f"got {_s.contact_order(['c'])!r}"
assert _s.contact_order(["d", "b"]) == ["d", "b", "a", "c"], f"got {_s.contact_order(['d', 'b'])!r}"
try:
    _s.contact_order(["zz"])
    assert False, "an unknown replica id should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Writes stop at W and version numbers climb", "code": r'''
from store import QuorumStore, Replica
_reps = [Replica(x) for x in "abc"]
_s = QuorumStore(_reps, r=2, w=2)
_v1 = _s.write("k", "one")
assert _v1 == 1, f"the first version should be 1, got {_v1!r}"
assert _s.last_write_set == ["a", "b"], f"write set is {_s.last_write_set!r}"
assert _reps[2].get("k") is None, "W=2 means the third replica is left behind"
_v2 = _s.write("k", "two")
assert _v2 == 2, f"the second version should be 2, got {_v2!r}"
'''},
                    {"name": "R + W <= N can miss the write entirely", "code": r'''
from store import QuorumStore, Replica, read_your_writes
assert read_your_writes(3, 1, 2) is False, "1 + 2 is not greater than 3"
assert read_your_writes(3, 2, 2) is True, "2 + 2 is greater than 3"
assert read_your_writes(5, 3, 3) is True and read_your_writes(5, 2, 3) is False
_reps = [Replica(x) for x in "abc"]
_loose = QuorumStore(_reps, r=1, w=2)
_loose.write("cart", "one item", prefer=["a", "b"])
assert _loose.read("cart", prefer=["c"]) is None, \
    "R=1 aimed at c must miss a write that only reached a and b"
assert _loose.last_read_set == ["c"], f"read set is {_loose.last_read_set!r}"
'''},
                    {"name": "R + W > N always sees the write", "code": r'''
from store import QuorumStore, Replica
_reps = [Replica(x) for x in "abc"]
_strict = QuorumStore(_reps, r=2, w=2)
_v = _strict.write("cart", "one item", prefer=["a", "b"])
for _pref in (["c"], ["c", "b"], ["b", "c"], ["c", "a"], None):
    _got = _strict.read("cart", prefer=_pref)
    assert _got == (_v, "one item"), f"read with prefer={_pref!r} gave {_got!r}"
_reps2 = [Replica(x) for x in "abc"]
_s2 = QuorumStore(_reps2, r=2, w=2)
_s2.write("k", "old", prefer=["a", "b"])
_v2 = _s2.write("k", "new", prefer=["b", "c"])
assert _s2.read("k", prefer=["a", "c"]) == (_v2, "new"), \
    "the merge must take the highest version in the read set, not the first answer"
'''},
                    {"name": "Read repair heals the stale responder", "code": r'''
from store import QuorumStore, Replica
_reps = [Replica(x) for x in "abc"]
_s = QuorumStore(_reps, r=2, w=2)
_v = _s.write("k", "value", prefer=["a", "b"])
assert _reps[2].get("k") is None, "c starts out empty"
_got = _s.read("k", prefer=["c", "a"], repair=True)
assert _got == (_v, "value"), f"read gave {_got!r}"
assert _s.last_repaired == ["c"], f"last_repaired is {_s.last_repaired!r}"
assert _reps[2].get("k") == (_v, "value"), "c should now hold the winning version"
_s.read("k", prefer=["c", "a"], repair=True)
assert _s.last_repaired == [], "a second read has nothing left to repair"
'''},
                    {"name": "Too few live replicas raises QuorumError", "code": r'''
from store import QuorumStore, QuorumError, Replica
_reps = [Replica(x) for x in "abc"]
_s = QuorumStore(_reps, r=2, w=2)
_reps[0].up = False
_reps[1].up = False
try:
    _s.write("k", "v")
    assert False, "one live replica cannot satisfy W=2"
except QuorumError:
    pass
assert _reps[2].get("k") is not None, \
    "the ack that did land is not rolled back — a failed write can still be visible"
try:
    _s.read("k")
    assert False, "one live replica cannot satisfy R=2"
except QuorumError:
    pass
_reps[0].up = True
assert _s.read("k", prefer=["a", "c"]) is not None, "two live replicas are enough again"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Partitioning and placement",
            "summary": "Consistent hashing with virtual nodes, measured against modulo hashing.",
            "concepts": [
                "Modulo hashing remaps roughly (k-1)/k of all keys when the node count changes",
                "Consistent hashing places nodes and keys on one hash ring; a key belongs to the next node clockwise",
                "Adding a node to a ring of k moves about 1/(k+1) of the keys, and only from one neighbour",
                "Virtual nodes turn a few physical machines into many ring points, flattening the load",
                "A preference list is the first N distinct nodes clockwise — the basis of replica placement",
                "`hash()` on a str is salted per process; partitioning needs a stable digest such as MD5",
                "Hot keys are not solved by hashing — they need a separate splitting or caching strategy",
            ],
            "quiz": {
                "title": "Where a key lives",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A ring holds four nodes with 128 virtual points each. A fifth node joins. Which keys change owner?",
                        "opts": [
                            "About a fifth of them, and every one of them moves onto the new node",
                            "About a fifth of them, redistributed between all five nodes",
                            "About four fifths of them, as under modulo hashing",
                            "None, until a rebalance is triggered explicitly",
                        ],
                        "a": 0,
                        "why": r"""
A joining node only ever takes keys. Each of its 128 points claims the arc immediately
behind it from whoever held that arc before, and no point that was already on the ring
moves, so no two existing nodes ever swap keys with each other. The share taken comes out
near $1/5$, and every moved key has the same destination. That is the property the
structure exists for: modulo hashing moves a similar-sounding fraction of keys for a very
different reason — it renumbers everything — and the lab measures both. And nothing is
deferred: the new node owns those arcs from the instant its points are inserted, which is
why the data has to be streamed to it promptly.
""",
                    },
                    {
                        "q": "Why does the lab insist on MD5 rather than Python's builtin `hash()` for ring positions?",
                        "opts": [
                            "`hash()` collides far more often than a digest",
                            "`hash()` is too slow to call 128 times per node",
                            "`hash()` on a `str` is salted per process, so two nodes would build different rings",
                            "`hash()` returns a signed value and `bisect` requires unsigned positions",
                        ],
                        "a": 2,
                        "why": r"""
Python randomises string hashing per interpreter unless `PYTHONHASHSEED` is fixed. Two
processes would place the same key at different ring positions and disagree about who
owns it from the very first request — and the disagreement would survive restarts by
changing every time, which is about the worst debugging experience available. MD5 is not
chosen here for cryptographic strength; it is chosen because it is the same number
everywhere, for ever. It is true that `hash()` can come back negative and would need
fixing up, but that is a nuisance, not the reason. And `hash()` is the *faster* of the
two — speed is what you are giving up to get determinism.
""",
                    },
                    {
                        "q": "What do 128 virtual points per machine actually buy?",
                        "opts": [
                            "Fewer keys moving when a node joins or leaves",
                            "An even share of the ring per machine, because many small arcs vary far less than one large one",
                            "The ability to keep a key on more than one machine",
                            "A faster lookup, since the search has more points to bisect against",
                        ],
                        "a": 1,
                        "why": r"""
With one point per machine the arc lengths are wildly uneven — they are essentially
exponentially distributed — and the lab measures a max/min load ratio above 2 for four
nodes. Averaging 128 arcs per machine collapses that variance and brings the ratio under
1.5. The fraction that moves on a join is about $1/(k+1)$ either way, so that is not the
gain. Replication is the preference list's job, not the virtual nodes'. And more points
make the binary search marginally *longer*, not shorter — it is logarithmic, so 128 times
more points costs about seven extra comparisons, which is the price of the balance.
""",
                    },
                    {
                        "q": "A preference list walks the ring clockwise from the key. Why must it skip nodes it has already collected?",
                        "opts": [
                            "Because consecutive points often belong to the same machine, and three copies on one machine is one copy",
                            "Because two nodes can collide on the same ring position",
                            "Because the walk would otherwise never terminate",
                            "Because the first node is the coordinator and may not also hold a replica",
                        ],
                        "a": 0,
                        "why": r"""
With 128 points per machine scattered over the ring, the next point clockwise belongs to
the same machine roughly one time in $k$, and a list built from points rather than
machines would happily put all three replicas of a key on one box. Then one machine
failing takes the key with it, and the whole replication scheme is decoration. The walk
terminates either way, since it is bounded by the number of points. Collisions between
two nodes' positions are possible but astronomically rare with a 64-bit digest, and would
not be fixed by skipping repeats. And the coordinator is normally the first node in the
list — holding a replica is its job, not a conflict of interest.
""",
                    },
                    {
                        "q": "One key in the store takes 40% of all reads. What do more virtual nodes do for it?",
                        "opts": [
                            "Spread it over 128 points and so across many machines",
                            "Move it to the least loaded machine at the next rebalance",
                            "Nothing — one key hashes to one position, so it lands on one machine",
                            "Split its value between the replicas in its preference list",
                        ],
                        "a": 2,
                        "why": r"""
Hashing balances *keys*, not requests. A key has one hash, so it has one position, so it
has one owner however many points that owner has placed — and 40% of the traffic lands on
one machine no matter how the ring is dressed. Virtual nodes fix skew in how many keys a
machine owns, which is a different problem that happens to look similar in a load graph.
The fixes for a hot key are elsewhere: split it into sub-keys with a suffix, cache it in
front of the store, or serve reads from all $N$ replicas in its preference list rather
than from the first one. Rebalancing on load, meanwhile, would break the one property the
ring is for — that any client can compute the owner without asking anyone.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Placing a key on the ring",
                "minutes": 8,
                "caption": "ring.py — build, look up, walk",
                "lang": "python",
                "brief": r"""
Three operations, and each holds one decision that is easy to get subtly wrong: what a
ring point maps back to, which side of a tie the search lands on, and what happens past
the largest point. The wrap is the only special case in the whole structure — everything
else is a sorted list and a binary search.
""",
                "listing": """# `points` is kept sorted; `owner` maps a ring point back to a machine.
for node in nodes:
    for v in range(vnodes):
        point = ring_hash("%s#%d" % (node, v))
        bisect.insort(points, point)
        owner[point] = ___                    # 128 points, one machine

# the owner of a key is the first point strictly clockwise of it
i = bisect.___(points, ring_hash(key))
if i == len(points):
    i = ___                                   # the ring wraps here and nowhere else

# the preference list keeps walking, crediting each machine once
prefs = []
for step in range(len(points)):
    n = owner[points[(i + step) % len(points)]]
    if n ___ prefs:
        prefs.append(n)
""",
                "blanks": [
                    {
                        "prompt": "What does a ring point map back to?",
                        "hole": "?",
                        "opts": ["node", "v", "point", "vnodes"],
                        "a": 0,
                        "why": "The physical machine. Many points share one node id, and that many-to-one mapping is the entire mechanism of virtual nodes — the ring is full of positions, the cluster is made of machines.",
                        "whys": [
                            "The physical machine. Many points share one node id, and that many-to-one mapping is the entire mechanism of virtual nodes — the ring is full of positions, the cluster is made of machines.",
                            "`v` is the replica index within one machine's points, a number from 0 to 127. Storing it loses which machine placed the point, which is the only thing a lookup needs to know.",
                            "Mapping a point to itself says nothing. The dictionary exists to answer 'whose is this position?', and a position is not an answer to that.",
                            "`vnodes` is the same count for every machine, so every lookup would return 128.",
                        ],
                    },
                    {
                        "prompt": "Which search finds the first point clockwise of the key?",
                        "hole": "?",
                        "opts": ["bisect_right", "bisect_left", "insort", "insort_right"],
                        "a": 0,
                        "why": "`bisect_right` returns the index of the first point strictly greater than the key's hash, which is the definition the ring uses. It never mutates the list, which matters here: a lookup that changed the ring would change ownership as a side effect of reading.",
                        "whys": [
                            "`bisect_right` returns the index of the first point strictly greater than the key's hash, which is the definition the ring uses. It never mutates the list, which matters here: a lookup that changed the ring would change ownership as a side effect of reading.",
                            "`bisect_left` returns the first point greater *or equal*, so a key that hashes exactly onto a ring point is given to that point rather than to the next one clockwise. The ring still works, but it is not the rule the tests and the preference list are written against.",
                            "`insort` inserts. Every lookup would push the key's hash into `points` as if it were a machine's position, growing the ring on every read and silently handing arcs to a node id that does not exist.",
                            "`insort_right` is the same insertion with the tie-breaking side named explicitly — still a mutation, and still catastrophic on a read path.",
                        ],
                    },
                    {
                        "prompt": "The key hashed past the largest point on the ring. Where does the search go?",
                        "hole": "?",
                        "opts": ["0", "-1", "len(points) - 1", "None"],
                        "a": 0,
                        "why": "Back to the smallest point. The ring is a circle drawn on a sorted list, and this line is the only place that circularity appears — every other operation is ordinary array arithmetic.",
                        "whys": [
                            "Back to the smallest point. The ring is a circle drawn on a sorted list, and this line is the only place that circularity appears — every other operation is ordinary array arithmetic.",
                            "-1 indexes the last element in Python, which is the point the key just walked past. Keys above the largest position would be given to the machine behind them rather than the one in front, and the arc boundaries stop lining up with what the preference list computes.",
                            "The same last element, spelled out. It reads more deliberate and is wrong in exactly the same way.",
                            "`None` cannot index a list. The wrap is not an error case — it is the ordinary fate of every key hashing above the highest ring position, which is a real share of them.",
                        ],
                    },
                    {
                        "prompt": "What decides whether a machine joins the preference list?",
                        "hole": "?",
                        "opts": ["not in", "in", "is not", "!="],
                        "a": 0,
                        "why": "A machine is added the first time it is met and skipped afterwards, which is what makes the list N *distinct* nodes rather than N ring points.",
                        "whys": [
                            "A machine is added the first time it is met and skipped afterwards, which is what makes the list N *distinct* nodes rather than N ring points.",
                            "Inverted: nothing is ever appended, because a machine is only added once it is already there. The list stays empty for every key.",
                            "`n is not prefs` compares a string with a list by identity, so it is true on every iteration and every point clockwise gets appended — repeats included. Three replicas of a key can end up on one machine.",
                            "`n != prefs` has the same problem in a different disguise: a string never equals a list, so the guard is always true and never guards anything.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "What a modulo rehash really costs",
                "minutes": 12,
                "vars": ["k", "h"],
                "brief": r"""
The lab measures it; this is where the number comes from. A key hashes to $h$. Under
modulo hashing across $k$ machines it lands on machine $h \bmod k$; add one machine and
it lands on $h \bmod (k+1)$. A key keeps its home exactly when those two agree.

Treat $h$ as uniform over a large range — a digest gives you that — and the fraction is
pure number theory.
""",
                "steps": [
                    {
                        "prompt": "$k$ and $k+1$ never share a factor, so by the Chinese remainder theorem the pair $(h \\bmod k,\\ h \\bmod (k+1))$ is determined by $h$ modulo a single number. Write that number.",
                        "answer": "k(k + 1)",
                        "hint": "Coprime moduli combine into their product, and every pair of residues occurs exactly once across that range.",
                        "deconstruct": [
                            "Any common factor of $k$ and $k+1$ would have to divide their difference, which is 1 — so they are coprime for every $k$.",
                            "The theorem then says the two residues together carry exactly as much information as $h$ modulo the product.",
                        ],
                    },
                    {
                        "prompt": "A key stays put exactly when $h \\bmod k$ and $h \\bmod (k+1)$ are the same value; call it $r$. How many values can $r$ take?",
                        "answer": "k",
                        "hint": "$r$ has to be a legal residue for both moduli at once, so the smaller range wins.",
                        "deconstruct": [
                            "$h \\bmod k$ ranges over $0 \\ldots k-1$; $h \\bmod (k+1)$ ranges over $0 \\ldots k$.",
                            "They can only agree on a value both can produce, so $r$ lies in $0 \\ldots k-1$ — that is $k$ values.",
                        ],
                    },
                    {
                        "prompt": "Each of those values of $r$ pins $h$ to one residue modulo $k(k+1)$. Write the fraction of keys that keep their machine.",
                        "answer": "\\frac{1}{k + 1}",
                        "hint": "Good residues over total residues, then cancel the common factor.",
                        "deconstruct": [
                            "$k$ good values out of the $k(k+1)$ residues that $h$ can take.",
                            "$k / (k(k+1))$ cancels to $1/(k+1)$.",
                        ],
                    },
                    {
                        "prompt": "So write the fraction that has to move.",
                        "answer": "\\frac{k}{k + 1}",
                        "hint": "Everything that did not stay.",
                        "deconstruct": [
                            "The movers are $1 - 1/(k+1)$.",
                            "Over a common denominator that is $k/(k+1)$.",
                        ],
                    },
                ],
                "closing": r"""
Put $k = 3$ in and you get $3/4$: adding a fourth machine under modulo hashing moves
three quarters of the keys, and the lab measures 0.741 over 5000 MD5-hashed keys, which
is that fraction with the sampling noise you would expect.

The same lab measures 0.26 for the ring, and $1/(k+1) = 1/4$ turns up there too — but on
the other side of the ledger. On a ring that fraction is *everything* that moves, and all
of it moves onto the machine that just joined. Modulo hashing moves that quarter and then
moves the rest as well, to no purpose whatsoever: it is not placing keys badly, it is
renumbering every machine each time the count changes.
""",
            },
            "lab": {
                "title": "A consistent-hashing ring",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
`ring.py` holds the logic; `main.py` runs the measurement. The checks import
from `ring.py`.

## Given

```python
def ring_hash(text):
    return int.from_bytes(hashlib.md5(str(text).encode("utf-8")).digest()[:8], "big")
```

Every ring point for node `n` is `ring_hash("<n>#<v>")` for `v` in
`range(vnodes)`. Use exactly that format or your numbers will not match.

## `ConsistentHashRing(nodes=(), vnodes=128)`

Keep the ring points in a **sorted** list so lookups are a binary search
(`bisect`), not a linear scan.

- `nodes()` — the physical node ids, sorted.
- `add_node(node)` — insert its `vnodes` points. `ValueError` if already present.
- `remove_node(node)` — remove them. `KeyError` if absent.
- `get_node(key)` — the owner: the first ring point strictly greater than
  `ring_hash(key)`, wrapping to the first point when there is none. `KeyError`
  on an empty ring.
- `preference_list(key, count)` — the first `count` **distinct** node ids
  walking clockwise from that same position. `ValueError` when `count` exceeds
  the number of nodes.

## Measurement helpers

- `modulo_node(key, nodes)` — `sorted(nodes)[ring_hash(key) % len(nodes)]`.
- `movement(keys, before, after)` — the fraction of `keys` whose owner differs
  between the two `{key: node}` maps. `0.0` for an empty key list.
- `load(ring, keys)` — `{node: how many keys it owns}`, with a `0` entry for
  every node that owns none.

## What you should see

Adding a fourth node to a three-node ring with 128 virtual nodes each moves
about 26% of 5000 keys — close to the ideal 1/4. Modulo hashing over the same
keys moves about 74%. Report both from `main.py`.
''',
                "files": [
                    {"name": "ring.py", "content": r'''
import bisect
import hashlib


def ring_hash(text):
    """A stable 64-bit position on the ring. Do not use the builtin hash()."""
    return int.from_bytes(hashlib.md5(str(text).encode("utf-8")).digest()[:8], "big")


class ConsistentHashRing:
    """Nodes and keys share one hash ring; a key belongs to the next node clockwise."""

    def __init__(self, nodes=(), vnodes=128):
        self.vnodes = vnodes
        self.points = []      # sorted ring positions
        self.owner = {}       # position -> node id
        self._nodes = []
        for node in nodes:
            self.add_node(node)

    def nodes(self):
        """The physical node ids, sorted."""
        # your code here

    def add_node(self, node):
        """Insert this node's virtual points. ValueError when already present."""
        # your code here

    def remove_node(self, node):
        """Remove this node's virtual points. KeyError when absent."""
        # your code here

    def get_node(self, key):
        """The owning node id. KeyError on an empty ring."""
        # your code here

    def preference_list(self, key, count):
        """The first count distinct nodes clockwise from the key's position."""
        # your code here


def modulo_node(key, nodes):
    """The naive placement this lab exists to beat."""
    # your code here


def movement(keys, before, after):
    """Fraction of keys whose owner changed between two {key: node} maps."""
    # your code here


def load(ring, keys):
    """{node: key count}, with a zero entry for every node that owns none."""
    # your code here
'''},
                    {"name": "main.py", "content": r'''
from ring import ConsistentHashRing, load, modulo_node, movement

KEYS = ["key-%d" % i for i in range(5000)]

ring = ConsistentHashRing(["n1", "n2", "n3"], vnodes=128)
before = {k: ring.get_node(k) for k in KEYS}
ring.add_node("n4")
after = {k: ring.get_node(k) for k in KEYS}
print("consistent hashing moved: %.3f" % movement(KEYS, before, after))

mod_before = {k: modulo_node(k, ["n1", "n2", "n3"]) for k in KEYS}
mod_after = {k: modulo_node(k, ["n1", "n2", "n3", "n4"]) for k in KEYS}
print("modulo hashing moved:     %.3f" % movement(KEYS, mod_before, mod_after))

counts = load(ring, KEYS)
print("load:", counts)
print("max/min ratio: %.2f" % (max(counts.values()) / min(counts.values())))
print("preference list for key-0:", ring.preference_list("key-0", 3))
'''},
                ],
                "main": "main.py",
                "solution": [
                    {"name": "ring.py", "content": r'''
import bisect
import hashlib


def ring_hash(text):
    """A stable 64-bit position on the ring. Do not use the builtin hash()."""
    return int.from_bytes(hashlib.md5(str(text).encode("utf-8")).digest()[:8], "big")


class ConsistentHashRing:
    """Nodes and keys share one hash ring; a key belongs to the next node clockwise."""

    def __init__(self, nodes=(), vnodes=128):
        self.vnodes = vnodes
        self.points = []      # sorted ring positions
        self.owner = {}       # position -> node id
        self._nodes = []
        for node in nodes:
            self.add_node(node)

    def nodes(self):
        """The physical node ids, sorted."""
        return sorted(self._nodes)

    def add_node(self, node):
        """Insert this node's virtual points. ValueError when already present."""
        if node in self._nodes:
            raise ValueError("node %r is already on the ring" % (node,))
        self._nodes.append(node)
        for v in range(self.vnodes):
            point = ring_hash("%s#%d" % (node, v))
            index = bisect.bisect_left(self.points, point)
            self.points.insert(index, point)
            self.owner[point] = node

    def remove_node(self, node):
        """Remove this node's virtual points. KeyError when absent."""
        if node not in self._nodes:
            raise KeyError(node)
        self._nodes.remove(node)
        for v in range(self.vnodes):
            point = ring_hash("%s#%d" % (node, v))
            index = bisect.bisect_left(self.points, point)
            if index < len(self.points) and self.points[index] == point:
                self.points.pop(index)
            self.owner.pop(point, None)

    def get_node(self, key):
        """The owning node id. KeyError on an empty ring."""
        if not self.points:
            raise KeyError("the ring has no nodes")
        index = bisect.bisect_right(self.points, ring_hash(key))
        if index == len(self.points):
            index = 0                      # wrap past the largest point
        return self.owner[self.points[index]]

    def preference_list(self, key, count):
        """The first count distinct nodes clockwise from the key's position."""
        if count > len(self._nodes):
            raise ValueError("asked for %d nodes, ring has %d" % (count, len(self._nodes)))
        if not self.points:
            raise KeyError("the ring has no nodes")
        start = bisect.bisect_right(self.points, ring_hash(key))
        chosen = []
        for step in range(len(self.points)):
            node = self.owner[self.points[(start + step) % len(self.points)]]
            if node not in chosen:
                chosen.append(node)
                if len(chosen) == count:
                    break
        return chosen


def modulo_node(key, nodes):
    """The naive placement this lab exists to beat."""
    ordered = sorted(nodes)
    if not ordered:
        raise ValueError("no nodes to choose from")
    return ordered[ring_hash(key) % len(ordered)]


def movement(keys, before, after):
    """Fraction of keys whose owner changed between two {key: node} maps."""
    if not keys:
        return 0.0
    moved = sum(1 for k in keys if before.get(k) != after.get(k))
    return moved / len(keys)


def load(ring, keys):
    """{node: key count}, with a zero entry for every node that owns none."""
    counts = {node: 0 for node in ring.nodes()}
    for key in keys:
        counts[ring.get_node(key)] += 1
    return counts
'''},
                ],
                "hints": [
                    "`bisect.insort` (or `bisect_left` plus `list.insert`) keeps `points` sorted as nodes arrive; `bisect_right` then finds the successor of a key position.",
                    "The wrap-around is the whole trick: when `bisect_right` returns `len(points)` the key belongs to `points[0]`.",
                    "`preference_list` walks ring points, not nodes — several consecutive points can belong to the same machine, so skip duplicates.",
                    "Seed `load` with every node at zero before counting, otherwise a node that happens to own nothing vanishes from the report.",
                ],
                "tests": [
                    {"name": "Empty and single-node rings", "code": r'''
from ring import ConsistentHashRing
_empty = ConsistentHashRing([], vnodes=8)
assert _empty.nodes() == [], "a fresh ring has no nodes"
try:
    _empty.get_node("k")
    assert False, "get_node on an empty ring should raise KeyError"
except KeyError:
    pass
_one = ConsistentHashRing(["solo"], vnodes=8)
assert all(_one.get_node("key-%d" % i) == "solo" for i in range(50)), \
    "one node owns every key, including the wrap-around case"
assert len(_one.points) == 8, f"8 virtual nodes means 8 ring points, got {len(_one.points)}"
assert _one.points == sorted(_one.points), "points must stay sorted for bisect to work"
'''},
                    {"name": "add and remove maintain the ring", "code": r'''
from ring import ConsistentHashRing
_r = ConsistentHashRing(["a", "b"], vnodes=16)
assert _r.nodes() == ["a", "b"], f"nodes() gave {_r.nodes()!r}"
try:
    _r.add_node("a")
    assert False, "adding a node twice should raise ValueError"
except ValueError:
    pass
try:
    _r.remove_node("zz")
    assert False, "removing an absent node should raise KeyError"
except KeyError:
    pass
_r.remove_node("b")
assert _r.nodes() == ["a"] and len(_r.points) == 16, \
    f"after removal: {_r.nodes()!r} with {len(_r.points)} points"
assert all(_r.get_node("key-%d" % i) == "a" for i in range(40)), \
    "a removed node must never be returned again"
'''},
                    {"name": "preference_list is distinct and bounded", "code": r'''
from ring import ConsistentHashRing
_r = ConsistentHashRing(["a", "b", "c", "d"], vnodes=32)
_p = _r.preference_list("cart:7", 3)
assert len(_p) == 3 and len(set(_p)) == 3, f"preference list is {_p!r}"
assert _p[0] == _r.get_node("cart:7"), "the first entry is the owner"
assert set(_p) <= set(_r.nodes()), "every entry must be a real node"
assert _r.preference_list("cart:7", 4) == _p + [n for n in _r.nodes() if n not in _p][:1] \
    or len(_r.preference_list("cart:7", 4)) == 4, "asking for N gives every node once"
try:
    _r.preference_list("cart:7", 5)
    assert False, "asking for more nodes than exist should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "modulo_node and movement", "code": r'''
from ring import modulo_node, movement
assert modulo_node("k", ["b", "a"]) == modulo_node("k", ["a", "b"]), \
    "modulo_node must sort, so argument order cannot change the answer"
assert modulo_node("k", ["only"]) == "only"
assert movement([], {}, {}) == 0.0, "no keys means no movement"
_b = {"k1": "a", "k2": "a", "k3": "b", "k4": "b"}
_a = {"k1": "a", "k2": "c", "k3": "b", "k4": "c"}
assert movement(list(_b), _b, _a) == 0.5, f"got {movement(list(_b), _b, _a)!r}"
'''},
                    {"name": "load counts every node", "code": r'''
from ring import ConsistentHashRing, load
_r = ConsistentHashRing(["a", "b", "c"], vnodes=128)
_keys = ["key-%d" % i for i in range(2000)]
_counts = load(_r, _keys)
assert sorted(_counts) == ["a", "b", "c"], f"load keys are {sorted(_counts)!r}"
assert sum(_counts.values()) == 2000, f"counts sum to {sum(_counts.values())}"
assert max(_counts.values()) / min(_counts.values()) < 1.5, \
    f"128 virtual nodes should balance within 50%, got {_counts!r}"
assert load(ConsistentHashRing(["a"], vnodes=4), []) == {"a": 0}, \
    "a node owning nothing still needs a zero entry"
'''},
                    {"name": "Virtual nodes beat one point per node", "code": r'''
from ring import ConsistentHashRing, load
_keys = ["key-%d" % i for i in range(5000)]
_flat = load(ConsistentHashRing(["n1", "n2", "n3", "n4"], vnodes=1), _keys)
_fat = load(ConsistentHashRing(["n1", "n2", "n3", "n4"], vnodes=128), _keys)
_flat_ratio = max(_flat.values()) / min(_flat.values())
_fat_ratio = max(_fat.values()) / min(_fat.values())
assert _flat_ratio > 2.0, f"one point per node should be badly skewed, ratio was {_flat_ratio:.2f}"
assert _fat_ratio < 1.5, f"128 points per node should be even, ratio was {_fat_ratio:.2f}"
'''},
                    {"name": "Joining a ring moves far fewer keys than modulo", "code": r'''
from ring import ConsistentHashRing, modulo_node, movement
_keys = ["key-%d" % i for i in range(5000)]
_r = ConsistentHashRing(["n1", "n2", "n3"], vnodes=128)
_before = {k: _r.get_node(k) for k in _keys}
_r.add_node("n4")
_after = {k: _r.get_node(k) for k in _keys}
_ring_moved = movement(_keys, _before, _after)
assert 0.15 < _ring_moved < 0.35, \
    f"a fourth node should move about a quarter of the keys, got {_ring_moved:.3f}"
_mod_moved = movement(_keys,
                      {k: modulo_node(k, ["n1", "n2", "n3"]) for k in _keys},
                      {k: modulo_node(k, ["n1", "n2", "n3", "n4"]) for k in _keys})
assert _mod_moved > 0.6, f"modulo hashing should shuffle most keys, got {_mod_moved:.3f}"
assert _mod_moved > 2 * _ring_moved, "the whole point is that the ring is dramatically better"
'''},
                    {"name": "Leaving a ring is just as cheap", "code": r'''
from ring import ConsistentHashRing, movement
_keys = ["key-%d" % i for i in range(5000)]
_r = ConsistentHashRing(["n1", "n2", "n3", "n4"], vnodes=128)
_before = {k: _r.get_node(k) for k in _keys}
_r.remove_node("n2")
_after = {k: _r.get_node(k) for k in _keys}
_moved = movement(_keys, _before, _after)
assert 0.15 < _moved < 0.35, f"removing one of four should move about a quarter, got {_moved:.3f}"
assert all(_before[k] == _after[k] for k in _keys if _before[k] != "n2"), \
    "keys that did not belong to n2 must not move at all"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a fault-tolerant replicated key-value service",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
Put the four labs together into one Dynamo-shaped service. `kvstore.py` holds
the logic and is what the checks import; `main.py` is a demo that runs a seeded
fault workload and prints a convergence report.

## `Replica(node_id)`

- `up` (bool), `store` (`key -> (version, value)`), `hints` (a list).
- `get(key)` / `put(key, version, value)` behave exactly as in the quorum lab:
  newest version wins, `ReplicaDown` when the node is not running.
- `hold_hint(target, key, version, value)` — append
  `(target, key, version, value)` to `hints`. This node is standing in for
  `target`.
- `drain_hints()` — return the hint list and clear it.

## `KVService(node_ids, n=3, r=2, w=2, vnodes=64)`

`ValueError` for duplicate ids, `n` greater than the cluster size, or `r`/`w`
outside `1..n`. Build one `ConsistentHashRing`-style ring internally using the
given `ring_hash`.

- `preference_list(key)` — the first `n` distinct nodes clockwise.
- `put(key, value)` — take a fresh version, then walk the preference list.
  A live node stores it. A **down** node is covered by hinted handoff: the
  first healthy node that is neither in the preference list nor already used
  holds a hint for it, and that counts as an ack. Stop at `w` acks; fewer
  raises `QuorumError`. Returns the version.
- `get(key)` — read from the first `r` live nodes of the preference list,
  return the newest `(version, value)` or `None`, and read-repair every
  responder that was behind, recording them in `last_repaired`. Fewer than `r`
  live nodes raises `QuorumError`.
- `fail(node_id)` / `recover(node_id)` — flip a replica's `up` flag.
  `KeyError` for an unknown id.
- `handoff()` — every live node delivers the hints whose target is now live,
  and keeps the rest. Returns how many were delivered.
- `repair(key)` — anti-entropy: push the newest version held by any live
  preference-list replica to every live preference-list replica that is behind.
  Returns the sorted list of node ids it fixed.
- `replica_versions(key)` — `{node_id: version or None}` across the whole
  cluster, for inspection.

## The property that matters

After any sequence of failures and recoveries, once every node is back and you
have run `handoff()` and then `repair(key)`, every live replica in that key's
preference list must hold the identical `(version, value)`. `main.py` must
demonstrate this with a `random.Random(7)` workload, so the run is byte-for-byte
reproducible.

Be honest in the demo about the uncomfortable part: a `put` that raises
`QuorumError` may still have landed on some replicas, and anti-entropy will
happily spread it.
''',
        "deliverables": [
            "`kvstore.py` — `Replica`, `KVService`, `ReplicaDown` and `QuorumError`, importable with no side effects",
            "Consistent-hashing placement with virtual nodes and an N-node preference list per key",
            "Quorum `put`/`get` with configurable N, R and W, and newest-version-wins merging",
            "Hinted handoff on write, plus a `handoff()` that drains hints once a node returns",
            "Read repair on the read path and a `repair(key)` anti-entropy sweep",
            "`main.py` — a seeded fault-injection workload that ends with a convergence report",
        ],
        "constraints": [
            "Standard library only; `bisect`, `hashlib` and `random` are all you need",
            "`kvstore.py` must define classes and functions only — importing it prints nothing",
            "Every random choice goes through `random.Random(7)`, so two runs are identical",
            "No node may reach into another node's `store` directly; go through the service",
            "A failed quorum raises rather than silently returning a partial result",
        ],
        "rubric": [
            {"criterion": "Correctness of the quorum protocol", "weight": 35,
             "evidence": "All automated checks pass, including the QuorumError paths and the empty-key case."},
            {"criterion": "Fault tolerance", "weight": 25,
             "evidence": "Hinted handoff covers a down replica on write and drains cleanly on recovery; read repair and repair() both converge."},
            {"criterion": "Placement", "weight": 15,
             "evidence": "Preference lists are distinct, stable, and derived from the ring rather than from list position."},
            {"criterion": "Determinism of the fault harness", "weight": 15,
             "evidence": "Two runs of main.py produce identical output; every random draw comes from the seeded generator."},
            {"criterion": "Clarity", "weight": 10,
             "evidence": "Docstrings on every public method, no debug prints in the module, exceptions carry a useful message."},
        ],
        "hints": [
            "Build the ring first and get `preference_list` right — every other method starts by calling it.",
            "In `put`, track a `used` set of nodes that have already acknowledged, so a hint holder is never asked to ack twice.",
            "A hint belongs on a node *outside* the preference list. If every outsider is down, that ack is simply lost and W may not be met.",
            "`repair` is the only method allowed to look at more than R replicas; that is what makes it anti-entropy rather than a read.",
        ],
        "files": [
            {"name": "kvstore.py", "content": r'''
import bisect
import hashlib


class ReplicaDown(Exception):
    """Raised when a coordinator touches a node that is not running."""


class QuorumError(Exception):
    """Raised when a request cannot assemble its R or W quorum."""


def ring_hash(text):
    """A stable 64-bit ring position."""
    return int.from_bytes(hashlib.md5(str(text).encode("utf-8")).digest()[:8], "big")


class Replica:
    """One storage node, plus the hints it is holding for absent peers."""

    def __init__(self, node_id):
        self.node_id = node_id
        self.up = True
        self.store = {}
        self.hints = []

    def get(self, key):
        """The stored (version, value) or None. ReplicaDown when not running."""
        # your code here

    def put(self, key, version, value):
        """Store when strictly newer. True if taken, False if rejected as stale."""
        # your code here

    def hold_hint(self, target, key, version, value):
        """Stand in for target until it comes back."""
        # your code here

    def drain_hints(self):
        """Return the held hints and clear them."""
        # your code here


class KVService:
    """A quorum key-value service over a consistent-hashing ring."""

    def __init__(self, node_ids, n=3, r=2, w=2, vnodes=64):
        # your code here
        pass

    def preference_list(self, key):
        """The first n distinct nodes clockwise from the key's ring position."""
        # your code here

    def put(self, key, value):
        """Write to w replicas, using hinted handoff to cover the ones that are down."""
        # your code here

    def get(self, key):
        """Read from r live replicas, newest version wins, then read-repair."""
        # your code here

    def fail(self, node_id):
        """Stop a node. KeyError when it does not exist."""
        # your code here

    def recover(self, node_id):
        """Start a node again. KeyError when it does not exist."""
        # your code here

    def handoff(self):
        """Deliver every hint whose target is live again; return how many."""
        # your code here

    def repair(self, key):
        """Anti-entropy across the whole preference list. Returns the ids fixed."""
        # your code here

    def replica_versions(self, key):
        """{node_id: version or None} across the cluster, for inspection."""
        # your code here
'''},
            {"name": "main.py", "content": r'''
import random

from kvstore import KVService, QuorumError

KEYS = ["cart:%d" % i for i in range(6)]
service = KVService(["n1", "n2", "n3", "n4", "n5"], n=3, r=2, w=2)
rng = random.Random(7)

written = {}
failed = set()
for step in range(40):
    # your code here: fail or recover a node, then attempt a put
    pass

print("this demo is not finished yet")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "kvstore.py", "content": r'''
import bisect
import hashlib


class ReplicaDown(Exception):
    """Raised when a coordinator touches a node that is not running."""


class QuorumError(Exception):
    """Raised when a request cannot assemble its R or W quorum."""


def ring_hash(text):
    """A stable 64-bit ring position."""
    return int.from_bytes(hashlib.md5(str(text).encode("utf-8")).digest()[:8], "big")


class Replica:
    """One storage node, plus the hints it is holding for absent peers."""

    def __init__(self, node_id):
        self.node_id = node_id
        self.up = True
        self.store = {}
        self.hints = []

    def get(self, key):
        """The stored (version, value) or None. ReplicaDown when not running."""
        if not self.up:
            raise ReplicaDown(self.node_id)
        return self.store.get(key)

    def put(self, key, version, value):
        """Store when strictly newer. True if taken, False if rejected as stale."""
        if not self.up:
            raise ReplicaDown(self.node_id)
        current = self.store.get(key)
        if current is not None and version <= current[0]:
            return False
        self.store[key] = (version, value)
        return True

    def hold_hint(self, target, key, version, value):
        """Stand in for target until it comes back."""
        if not self.up:
            raise ReplicaDown(self.node_id)
        self.hints.append((target, key, version, value))
        return True

    def drain_hints(self):
        """Return the held hints and clear them."""
        held = self.hints
        self.hints = []
        return held


class KVService:
    """A quorum key-value service over a consistent-hashing ring."""

    def __init__(self, node_ids, n=3, r=2, w=2, vnodes=64):
        node_ids = list(node_ids)
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("duplicate node ids: " + repr(node_ids))
        if not 1 <= n <= len(node_ids):
            raise ValueError("n must lie in 1..%d, got %r" % (len(node_ids), n))
        if not 1 <= r <= n:
            raise ValueError("r must lie in 1..%d, got %r" % (n, r))
        if not 1 <= w <= n:
            raise ValueError("w must lie in 1..%d, got %r" % (n, w))
        self.order = node_ids
        self.replicas = {nid: Replica(nid) for nid in node_ids}
        self.n, self.r, self.w = n, r, w
        self.vnodes = vnodes
        self.points = []
        self.owner = {}
        for nid in node_ids:
            for v in range(vnodes):
                point = ring_hash("%s#%d" % (nid, v))
                index = bisect.bisect_left(self.points, point)
                self.points.insert(index, point)
                self.owner[point] = nid
        self._clock = 0
        self.last_repaired = []
        self.hints_written = 0

    # ------------------------------------------------------------- placement
    def preference_list(self, key):
        """The first n distinct nodes clockwise from the key's ring position."""
        start = bisect.bisect_right(self.points, ring_hash(key))
        chosen = []
        for step in range(len(self.points)):
            node = self.owner[self.points[(start + step) % len(self.points)]]
            if node not in chosen:
                chosen.append(node)
                if len(chosen) == self.n:
                    break
        return chosen

    def _next_version(self):
        self._clock += 1
        return self._clock

    # ------------------------------------------------------------ operations
    def put(self, key, value):
        """Write to w replicas, using hinted handoff to cover the ones that are down."""
        version = self._next_version()
        prefs = self.preference_list(key)
        used = set()
        acks = 0
        for node_id in prefs:
            replica = self.replicas[node_id]
            if replica.up:
                replica.put(key, version, value)
                used.add(node_id)
                acks += 1
            else:
                stand_in = self._stand_in(prefs, used)
                if stand_in is not None:
                    self.replicas[stand_in].hold_hint(node_id, key, version, value)
                    used.add(stand_in)
                    self.hints_written += 1
                    acks += 1
            if acks >= self.w:
                break
        if acks < self.w:
            raise QuorumError("only %d of %d replicas accepted %r" % (acks, self.w, key))
        return version

    def _stand_in(self, prefs, used):
        """The first healthy node outside the preference list that is still free."""
        for node_id in self.order:
            if node_id in prefs or node_id in used:
                continue
            if self.replicas[node_id].up:
                return node_id
        return None

    def get(self, key):
        """Read from r live replicas, newest version wins, then read-repair."""
        responses = []
        for node_id in self.preference_list(key):
            replica = self.replicas[node_id]
            if not replica.up:
                continue
            responses.append((node_id, replica.get(key)))
            if len(responses) == self.r:
                break
        self.last_repaired = []
        if len(responses) < self.r:
            raise QuorumError("only %d of %d replicas answered for %r"
                              % (len(responses), self.r, key))
        best = None
        for _node_id, got in responses:
            if got is not None and (best is None or got[0] > best[0]):
                best = got
        if best is not None:
            for node_id, got in responses:
                if got is None or got[0] < best[0]:
                    self.replicas[node_id].put(key, best[0], best[1])
                    self.last_repaired.append(node_id)
        return best

    # ----------------------------------------------------------------- faults
    def fail(self, node_id):
        """Stop a node. KeyError when it does not exist."""
        self.replicas[node_id].up = False

    def recover(self, node_id):
        """Start a node again. KeyError when it does not exist."""
        self.replicas[node_id].up = True

    def handoff(self):
        """Deliver every hint whose target is live again; return how many."""
        delivered = 0
        for replica in self.replicas.values():
            if not replica.up:
                continue
            still_waiting = []
            for target, key, version, value in replica.drain_hints():
                owner = self.replicas[target]
                if owner.up:
                    owner.put(key, version, value)
                    delivered += 1
                else:
                    still_waiting.append((target, key, version, value))
            replica.hints = still_waiting
        return delivered

    def repair(self, key):
        """Anti-entropy across the whole preference list. Returns the ids fixed."""
        live = [nid for nid in self.preference_list(key) if self.replicas[nid].up]
        best = None
        for node_id in live:
            got = self.replicas[node_id].get(key)
            if got is not None and (best is None or got[0] > best[0]):
                best = got
        if best is None:
            return []
        fixed = []
        for node_id in live:
            got = self.replicas[node_id].get(key)
            if got is None or got[0] < best[0]:
                self.replicas[node_id].put(key, best[0], best[1])
                fixed.append(node_id)
        return sorted(fixed)

    def replica_versions(self, key):
        """{node_id: version or None} across the cluster, for inspection."""
        out = {}
        for node_id in self.order:
            held = self.replicas[node_id].store.get(key)
            out[node_id] = None if held is None else held[0]
        return out
'''},
            {"name": "main.py", "content": r'''
import random

from kvstore import KVService, QuorumError

KEYS = ["cart:%d" % i for i in range(6)]
service = KVService(["n1", "n2", "n3", "n4", "n5"], n=3, r=2, w=2)
rng = random.Random(7)

written = {}
refused = 0
failed = set()

for step in range(40):
    # churn: at most two nodes down at once, so a W=2 quorum stays reachable
    if failed and rng.random() < 0.4:
        node = rng.choice(sorted(failed))
        service.recover(node)
        failed.discard(node)
    elif len(failed) < 2 and rng.random() < 0.35:
        node = rng.choice([n for n in service.order if n not in failed])
        service.fail(node)
        failed.add(node)

    key = rng.choice(KEYS)
    value = "v%d" % step
    try:
        written[key] = (service.put(key, value), value)
    except QuorumError:
        refused += 1

print("writes refused by the quorum:", refused)
print("hints written:", service.hints_written)

for node in sorted(failed):
    service.recover(node)
print("hints delivered on recovery:", service.handoff())

converged = 0
for key in KEYS:
    service.repair(key)
    versions = service.replica_versions(key)
    prefs = service.preference_list(key)
    seen = {versions[nid] for nid in prefs}
    if len(seen) == 1:
        converged += 1
    print(key, "prefs", prefs, "versions", [versions[nid] for nid in prefs])

print("keys converged: %d of %d" % (converged, len(KEYS)))
print("read back cart:0 ->", service.get("cart:0"))
'''},
        ],
        "tests": [
            {"name": "Replica semantics, hints included", "code": r'''
from kvstore import Replica, ReplicaDown
_rep = Replica("a")
assert _rep.get("k") is None, "an unwritten key reads as None"
assert _rep.put("k", 4, "four") is True and _rep.get("k") == (4, "four")
assert _rep.put("k", 4, "again") is False, "an equal version is not newer"
assert _rep.put("k", 2, "old") is False and _rep.get("k") == (4, "four"), \
    "a stale write must not overwrite"
_rep.hold_hint("b", "k", 9, "nine")
assert _rep.drain_hints() == [("b", "k", 9, "nine")], "drain_hints returns the held list"
assert _rep.hints == [], "drain_hints must clear the list"
_rep.up = False
try:
    _rep.get("k")
    assert False, "a down replica should raise ReplicaDown"
except ReplicaDown:
    pass
'''},
            {"name": "Service configuration is validated", "code": r'''
from kvstore import KVService
for _bad in [(["a", "a", "b"], 2, 1, 1), (["a", "b"], 3, 1, 1),
             (["a", "b", "c"], 3, 0, 2), (["a", "b", "c"], 3, 2, 4),
             (["a", "b", "c"], 0, 1, 1)]:
    try:
        KVService(_bad[0], n=_bad[1], r=_bad[2], w=_bad[3])
        assert False, f"KVService{_bad!r} should raise ValueError"
    except ValueError:
        pass
_svc = KVService(["a", "b", "c", "d"], n=3, r=2, w=2)
assert (_svc.n, _svc.r, _svc.w) == (3, 2, 2), "n, r and w should be stored as given"
try:
    _svc.fail("nope")
    assert False, "failing an unknown node should raise KeyError"
except KeyError:
    pass
'''},
            {"name": "Preference lists come from the ring", "code": r'''
from kvstore import KVService
_svc = KVService(["a", "b", "c", "d", "e"], n=3, r=2, w=2)
_p = _svc.preference_list("cart:7")
assert len(_p) == 3 and len(set(_p)) == 3, f"preference list is {_p!r}"
assert set(_p) <= set(_svc.order), "every entry must be a real node"
assert _svc.preference_list("cart:7") == _p, "placement must be stable across calls"
_lists = [_svc.preference_list("cart:%d" % i) for i in range(20)]
assert len({tuple(x) for x in _lists}) > 1, \
    "different keys should land on different preference lists, not one fixed order"
'''},
            {"name": "put and get on a healthy cluster", "code": r'''
from kvstore import KVService
_svc = KVService(["a", "b", "c", "d"], n=3, r=2, w=2)
assert _svc.get("missing") is None, "an unwritten key reads as None"
_v1 = _svc.put("cart:1", "one")
_v2 = _svc.put("cart:1", "two")
assert _v2 > _v1, f"versions must increase, got {_v1!r} then {_v2!r}"
assert _svc.get("cart:1") == (_v2, "two"), f"get gave {_svc.get('cart:1')!r}"
_versions = _svc.replica_versions("cart:1")
_prefs = _svc.preference_list("cart:1")
assert sum(1 for nid in _prefs if _versions[nid] == _v2) >= 2, \
    f"W=2 replicas should hold the newest version, versions are {_versions!r}"
'''},
            {"name": "W acks leave a replica behind, and the read repairs it", "code": r'''
from kvstore import KVService
_svc = KVService(["a", "b", "c", "d"], n=3, r=2, w=2)
_prefs = _svc.preference_list("cart:2")
_v = _svc.put("cart:2", "alpha")
assert _svc.replica_versions("cart:2")[_prefs[2]] is None, \
    "stopping at W=2 means the third preference replica never saw the write"
_svc.fail(_prefs[1])
assert _svc.get("cart:2") == (_v, "alpha"), "the read should still find the value"
assert _svc.last_repaired == [_prefs[2]], f"last_repaired is {_svc.last_repaired!r}"
assert _svc.replica_versions("cart:2")[_prefs[2]] == _v, \
    "read repair should have pushed the winner to the empty replica"
'''},
            {"name": "Hinted handoff covers a down replica", "code": r'''
from kvstore import KVService
_svc = KVService(["a", "b", "c", "d"], n=3, r=2, w=2)
_prefs = _svc.preference_list("cart:3")
_outsider = [n for n in _svc.order if n not in _prefs][0]
_svc.fail(_prefs[0])
_v = _svc.put("cart:3", "beta")
assert _svc.hints_written == 1, f"one hint should have been written, got {_svc.hints_written}"
_held = _svc.replicas[_outsider].hints
assert _held == [(_prefs[0], "cart:3", _v, "beta")], f"the outsider holds {_held!r}"
assert _svc.replica_versions("cart:3")[_prefs[0]] is None, \
    "the down node has no data yet — the hint is not its store"
'''},
            {"name": "Recovery drains the hints", "code": r'''
assert _svc.handoff() == 0, "nothing can be delivered while the target is still down"
_svc.recover(_prefs[0])
assert _svc.handoff() == 1, "the hint should be delivered once the target is back"
assert _svc.replica_versions("cart:3")[_prefs[0]] == _v, \
    f"versions after handoff: {_svc.replica_versions('cart:3')!r}"
assert _svc.replicas[_outsider].hints == [], "a delivered hint must be dropped"
assert _svc.handoff() == 0, "a second handoff has nothing left to do"
'''},
            {"name": "Too few live replicas raises QuorumError", "code": r'''
from kvstore import KVService, QuorumError
_svc = KVService(["a", "b", "c"], n=3, r=2, w=2)
_prefs = _svc.preference_list("cart:4")
_svc.fail(_prefs[0])
_svc.fail(_prefs[1])
try:
    _svc.put("cart:4", "gamma")
    assert False, "one live replica and no outsider cannot satisfy W=2"
except QuorumError:
    pass
try:
    _svc.get("cart:4")
    assert False, "one live replica cannot satisfy R=2"
except QuorumError:
    pass
_svc.recover(_prefs[0])
assert _svc.put("cart:4", "gamma") > 0, "two live replicas are enough again"
'''},
            {"name": "repair() sweeps the whole preference list", "code": r'''
from kvstore import KVService
_svc = KVService(["a", "b", "c", "d", "e"], n=3, r=2, w=2)
_prefs = _svc.preference_list("cart:5")
_v = _svc.put("cart:5", "delta")
_versions = _svc.replica_versions("cart:5")
_behind = [nid for nid in _prefs if _versions[nid] != _v]
assert _behind, "W=2 out of N=3 must leave exactly one replica behind"
assert _svc.repair("cart:5") == sorted(_behind), \
    f"repair should fix {sorted(_behind)!r}, it returned {_svc.repair('cart:5')!r}"
assert all(_svc.replica_versions("cart:5")[nid] == _v for nid in _prefs), \
    "every preference replica should now hold the newest version"
assert _svc.repair("cart:5") == [], "a converged key needs no repair"
assert _svc.repair("never-written") == [], "a key nobody wrote needs no repair"
'''},
            {"name": "A seeded fault workload converges", "code": r'''
import random as _random
from kvstore import KVService, QuorumError
_keys = ["cart:%d" % i for i in range(6)]
_svc = KVService(["n1", "n2", "n3", "n4", "n5"], n=3, r=2, w=2)
_rng = _random.Random(7)
_written = {}
_failed = set()
for _step in range(40):
    if _failed and _rng.random() < 0.4:
        _node = _rng.choice(sorted(_failed))
        _svc.recover(_node)
        _failed.discard(_node)
    elif len(_failed) < 2 and _rng.random() < 0.35:
        _node = _rng.choice([n for n in _svc.order if n not in _failed])
        _svc.fail(_node)
        _failed.add(_node)
    _key = _rng.choice(_keys)
    try:
        _written[_key] = _svc.put(_key, "v%d" % _step)
    except QuorumError:
        pass
assert _svc.hints_written > 0, "the workload should have exercised hinted handoff at least once"
for _node in sorted(_failed):
    _svc.recover(_node)
_svc.handoff()
for _key in _keys:
    _svc.repair(_key)
    _vs = _svc.replica_versions(_key)
    _seen = {_vs[nid] for nid in _svc.preference_list(_key)}
    assert len(_seen) == 1 and None not in _seen, \
        f"{_key} did not converge: {_vs!r}"
    assert max(_seen) >= _written[_key], \
        f"{_key} converged on {max(_seen)!r}, older than the last acknowledged write {_written[_key]!r}"
'''},
            {"name": "The workload is reproducible", "code": r'''
import random as _random
from kvstore import KVService, QuorumError


def _run():
    _svc = KVService(["n1", "n2", "n3", "n4", "n5"], n=3, r=2, w=2)
    _rng = _random.Random(7)
    _failed = set()
    _trace = []
    for _step in range(30):
        if _failed and _rng.random() < 0.4:
            _node = _rng.choice(sorted(_failed))
            _svc.recover(_node)
            _failed.discard(_node)
        elif len(_failed) < 2 and _rng.random() < 0.35:
            _node = _rng.choice([n for n in _svc.order if n not in _failed])
            _svc.fail(_node)
            _failed.add(_node)
        try:
            _trace.append(_svc.put("cart:%d" % (_step % 6), "v%d" % _step))
        except QuorumError:
            _trace.append(None)
    return _trace


assert _run() == _run(), "a seeded workload must replay identically"
'''},
            {"name": "kvstore.py is import-clean", "code": r'''
_src = open("kvstore.py").read()
assert "print(" not in _src, "kvstore.py is a library; the reporting belongs in main.py"
assert "hashlib" in _src, "placement needs a stable digest, not the builtin hash()"
'''},
        ],
    },
}
