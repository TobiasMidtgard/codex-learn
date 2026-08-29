"""CS210 — Operating Systems. Author module."""

COURSE = {
    "id": "CS210",
    "title": "Operating Systems",
    "year": 2,
    "level": "Intermediate",
    "prereqs": ["CE201", "CS201"],
    "stack": ["C (reference)", "Python"],
    "credits": 15,
    "hours": 150,
    "icon": "◱",
    "summary": (
        "An operating system is the policy layer between hardware and programs: who "
        "gets the processor, which pages stay in memory, which thread may enter a "
        "critical section, and where bytes land on disk. You build simulators for each "
        "of those four decisions and measure them, rather than reading about them."
    ),
    "outcomes": [
        "Simulate FCFS, SJF, priority and round-robin scheduling and derive waiting and turnaround times",
        "Implement FIFO, LRU and OPT page replacement and explain why only some are stack algorithms",
        "Demonstrate Belady's anomaly experimentally rather than quoting it",
        "Reason about interleavings by executing them explicitly, and detect a deadlock from the trace",
        "Apply the banker's algorithm to decide whether a resource request may safely be granted",
        "Build an inode-and-free-list allocator and quantify the fragmentation it produces",
        "Assemble scheduling, paging and syscalls into one kernel simulator with an auditable trace",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Silberschatz, Galvin & Gagne, *Operating System Concepts*, 10th ed. — chapters 5, 6, 8, 10, 13",
        "Arpaci-Dusseau & Arpaci-Dusseau, *Operating Systems: Three Easy Pieces* — virtualisation and concurrency parts",
        "Tanenbaum & Bos, *Modern Operating Systems*, 4th ed. — chapters 2 and 3",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Processes and CPU scheduling",
            "summary": "Deciding which runnable process owns the processor, and what that decision costs.",
            "concepts": [
                "The process control block, and the ready / running / blocked states",
                "A context switch is pure overhead: saved registers, a new page-table base, a cold cache",
                "Non-preemptive policies (FCFS, SJF, priority) versus preemptive round robin",
                "Turnaround = completion − arrival; waiting = turnaround − burst; both are derived, never measured twice",
                "The convoy effect: one long burst at the head of an FCFS queue delays everything behind it",
                "Starvation under strict priority, and ageing as the usual remedy",
                "Quantum choice: too large degenerates to FCFS, too small drowns in switch overhead",
            ],
            "lab": {
                "title": "Four schedulers over one workload",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
A workload is a list of process dicts:

```python
{"pid": "A", "arrival": 0, "burst": 5, "priority": 2}
```

Every scheduler returns the same shape — a **Gantt timeline**, a list of
`(pid, start, end)` segments in the order the CPU actually ran them. Metrics are
derived from that timeline afterwards, never computed inside a scheduler.

**`fcfs(procs)`** — run in arrival order, ties broken by `pid`. When the CPU
would be idle, jump the clock forward to the next arrival; emit no segment for
the idle gap.

**`sjf(procs)`** — non-preemptive shortest-job-first. At each dispatch point,
choose the shortest burst among the processes that have already arrived; ties
break on arrival, then on `pid`.

**`priority_schedule(procs)`** — the same, but the key is `priority`, where a
**smaller number means more urgent**.

**`round_robin(procs, quantum)`** — preemptive, one slice of at most `quantum`
ticks per dispatch. A process that arrives at exactly the tick another process
is preempted joins the ready queue **before** the preempted one. Emit one
segment per dispatch — do not merge adjacent slices of the same process. Raise
`ValueError` when `quantum` is not positive.

**`metrics(procs, timeline)`** — `{pid: {"completion", "turnaround", "waiting"}}`,
where completion is the end of that process's **last** segment. Raise
`ValueError` if the timeline names a process that is not in `procs`, or if some
process never ran.

**`averages(stats)`** — `{"waiting": float, "turnaround": float}`; both `0.0`
for an empty workload.

For the table in `main.py` the round-robin timeline with `quantum = 3` begins:

```text
A 0-3, B 3-6, C 6-9, D 9-12, A 12-14, ...
```
''',
                "files": [{"name": "main.py", "content": r'''
WORKLOAD = [
    {"pid": "A", "arrival": 0, "burst": 5, "priority": 2},
    {"pid": "B", "arrival": 1, "burst": 3, "priority": 3},
    {"pid": "C", "arrival": 2, "burst": 8, "priority": 1},
    {"pid": "D", "arrival": 3, "burst": 6, "priority": 1},
]


def fcfs(procs):
    """Arrival order, ties on pid. Returns [(pid, start, end), ...]."""
    # your code here


def sjf(procs):
    """Non-preemptive shortest job first among the arrived processes."""
    # your code here


def priority_schedule(procs):
    """Non-preemptive, smallest priority number wins."""
    # your code here


def round_robin(procs, quantum):
    """Preemptive round robin, one segment per dispatch."""
    # your code here


def metrics(procs, timeline):
    """pid -> {completion, turnaround, waiting}, derived from the timeline."""
    # your code here


def averages(stats):
    """Mean waiting and turnaround over every process."""
    # your code here


for name, timeline in [("FCFS", fcfs(WORKLOAD)),
                       ("RR/3", round_robin(WORKLOAD, 3))]:
    print(name, timeline)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
WORKLOAD = [
    {"pid": "A", "arrival": 0, "burst": 5, "priority": 2},
    {"pid": "B", "arrival": 1, "burst": 3, "priority": 3},
    {"pid": "C", "arrival": 2, "burst": 8, "priority": 1},
    {"pid": "D", "arrival": 3, "burst": 6, "priority": 1},
]


def fcfs(procs):
    """Arrival order, ties on pid. Returns [(pid, start, end), ...]."""
    timeline = []
    clock = 0
    for p in sorted(procs, key=lambda p: (p["arrival"], p["pid"])):
        start = max(clock, p["arrival"])
        timeline.append((p["pid"], start, start + p["burst"]))
        clock = start + p["burst"]
    return timeline


def _non_preemptive(procs, key):
    """Shared engine: repeatedly dispatch the best arrived process to completion."""
    pending = list(range(len(procs)))
    timeline = []
    clock = 0
    while pending:
        ready = [i for i in pending if procs[i]["arrival"] <= clock]
        if not ready:
            # CPU idle: fast-forward to the next arrival rather than busy-wait
            clock = min(procs[i]["arrival"] for i in pending)
            continue
        chosen = min(ready, key=lambda i: key(procs[i]))
        p = procs[chosen]
        start = max(clock, p["arrival"])
        timeline.append((p["pid"], start, start + p["burst"]))
        clock = start + p["burst"]
        pending.remove(chosen)
    return timeline


def sjf(procs):
    """Non-preemptive shortest job first among the arrived processes."""
    return _non_preemptive(procs, lambda p: (p["burst"], p["arrival"], p["pid"]))


def priority_schedule(procs):
    """Non-preemptive, smallest priority number wins."""
    return _non_preemptive(procs, lambda p: (p["priority"], p["arrival"], p["pid"]))


def round_robin(procs, quantum):
    """Preemptive round robin, one segment per dispatch."""
    if quantum <= 0:
        raise ValueError("quantum must be positive")
    arrivals = sorted(procs, key=lambda p: (p["arrival"], p["pid"]))
    remaining = {p["pid"]: p["burst"] for p in procs}
    queue = []
    timeline = []
    clock = 0
    nxt = 0

    def admit(now):
        nonlocal nxt
        while nxt < len(arrivals) and arrivals[nxt]["arrival"] <= now:
            queue.append(arrivals[nxt]["pid"])
            nxt += 1

    while nxt < len(arrivals) or queue:
        if not queue:
            clock = max(clock, arrivals[nxt]["arrival"])
        admit(clock)
        pid = queue.pop(0)
        slice_len = min(quantum, remaining[pid])
        timeline.append((pid, clock, clock + slice_len))
        clock += slice_len
        remaining[pid] -= slice_len
        # arrivals during the slice are admitted before the preempted process
        admit(clock)
        if remaining[pid] > 0:
            queue.append(pid)
    return timeline


def metrics(procs, timeline):
    """pid -> {completion, turnaround, waiting}, derived from the timeline."""
    by_pid = {p["pid"]: p for p in procs}
    completion = {}
    for pid, start, end in timeline:
        if pid not in by_pid:
            raise ValueError(f"timeline names unknown process {pid!r}")
        completion[pid] = max(completion.get(pid, end), end)
    stats = {}
    for pid, p in by_pid.items():
        if pid not in completion:
            raise ValueError(f"process {pid!r} never ran")
        turnaround = completion[pid] - p["arrival"]
        stats[pid] = {"completion": completion[pid],
                      "turnaround": turnaround,
                      "waiting": turnaround - p["burst"]}
    return stats


def averages(stats):
    """Mean waiting and turnaround over every process."""
    if not stats:
        return {"waiting": 0.0, "turnaround": 0.0}
    n = len(stats)
    return {"waiting": sum(s["waiting"] for s in stats.values()) / n,
            "turnaround": sum(s["turnaround"] for s in stats.values()) / n}


for name, timeline in [("FCFS", fcfs(WORKLOAD)),
                       ("RR/3", round_robin(WORKLOAD, 3))]:
    print(name, timeline)
'''}],
                "hints": [
                    "Write `fcfs` first and keep the idle rule in one place: `start = max(clock, arrival)`.",
                    "SJF and priority differ only in the sort key — factor the dispatch loop out and pass the key in.",
                    "Round robin needs two admission points: before the dispatch, and again at the end of the slice, so a process arriving at the preemption tick queues ahead of the preempted one.",
                    "`metrics` must never look at bursts to find completion times — take the maximum `end` over each pid's segments.",
                ],
                "tests": [
                    {"name": "FCFS runs in arrival order", "code": r'''
_got = fcfs(WORKLOAD)
_want = [("A", 0, 5), ("B", 5, 8), ("C", 8, 16), ("D", 16, 22)]
assert _got == _want, f"fcfs gave {_got!r}, expected {_want}"
assert fcfs([]) == [], "An empty workload has an empty timeline"
'''},
                    {"name": "FCFS leaves the CPU idle until the first arrival", "code": r'''
_late = [{"pid": "X", "arrival": 5, "burst": 2, "priority": 1}]
assert fcfs(_late) == [("X", 5, 7)], f"fcfs gave {fcfs(_late)!r}, expected [('X', 5, 7)]"
_st = metrics(_late, fcfs(_late))
assert _st["X"]["waiting"] == 0, f"X waited {_st['X']['waiting']}, it arrived to an idle CPU"
'''},
                    {"name": "SJF prefers the shortest arrived burst", "code": r'''
_got = sjf(WORKLOAD)
_want = [("A", 0, 5), ("B", 5, 8), ("D", 8, 14), ("C", 14, 22)]
assert _got == _want, f"sjf gave {_got!r}, expected {_want}"
'''},
                    {"name": "Priority uses the priority field, not the burst", "code": r'''
_got = priority_schedule(WORKLOAD)
_want = [("A", 0, 5), ("C", 5, 13), ("D", 13, 19), ("B", 19, 22)]
assert _got == _want, f"priority_schedule gave {_got!r}, expected {_want}"
'''},
                    {"name": "Round robin slices and requeues", "code": r'''
_got = round_robin(WORKLOAD, 3)
_want = [("A", 0, 3), ("B", 3, 6), ("C", 6, 9), ("D", 9, 12), ("A", 12, 14),
         ("C", 14, 17), ("D", 17, 20), ("C", 20, 22)]
assert _got == _want, f"round_robin(WORKLOAD, 3) gave {_got!r}, expected {_want}"
_solo = [{"pid": "X", "arrival": 0, "burst": 5, "priority": 1}]
assert round_robin(_solo, 3) == [("X", 0, 3), ("X", 3, 5)], \
    "One segment per dispatch, even when the same process is redispatched"
for _bad in (0, -1):
    try:
        round_robin(WORKLOAD, _bad)
        assert False, f"round_robin(..., {_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "metrics derives waiting and turnaround", "code": r'''
_st = metrics(WORKLOAD, fcfs(WORKLOAD))
assert _st["A"] == {"completion": 5, "turnaround": 5, "waiting": 0}, f"A: {_st['A']!r}"
assert _st["D"] == {"completion": 22, "turnaround": 19, "waiting": 13}, f"D: {_st['D']!r}"
_rr = metrics(WORKLOAD, round_robin(WORKLOAD, 3))
assert _rr["C"]["completion"] == 22 and _rr["C"]["waiting"] == 12, f"C under RR: {_rr['C']!r}"
assert metrics([], []) == {}, "No processes, no statistics"
'''},
                    {"name": "metrics rejects an inconsistent timeline", "code": r'''
try:
    metrics(WORKLOAD, [("Z", 0, 1)])
    assert False, "A timeline naming an unknown pid should raise ValueError"
except ValueError:
    pass
try:
    metrics(WORKLOAD, [("A", 0, 5)])
    assert False, "A process that never ran should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "averages compare the policies", "code": r'''
assert averages({}) == {"waiting": 0.0, "turnaround": 0.0}, "Empty workload averages 0.0"
_a = averages(metrics(WORKLOAD, sjf(WORKLOAD)))
assert abs(_a["waiting"] - 5.25) < 1e-9, f"SJF mean waiting is {_a['waiting']!r}, expected 5.25"
_f = averages(metrics(WORKLOAD, fcfs(WORKLOAD)))
assert abs(_f["waiting"] - 5.75) < 1e-9, f"FCFS mean waiting is {_f['waiting']!r}, expected 5.75"
assert _a["waiting"] < _f["waiting"], "SJF is optimal for mean waiting time — it must beat FCFS here"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Virtual memory and page replacement",
            "summary": "Which resident page to evict, and how badly the wrong answer hurts.",
            "concepts": [
                "Paging: a virtual address splits into page number and offset; the page table maps the former",
                "A page fault is a trap, not an error — the handler fetches the page and restarts the instruction",
                "FIFO, LRU and OPT: implementable, approximable, and unimplementable respectively",
                "OPT is the offline lower bound used to judge the other two",
                "Stack algorithms: the resident set with m frames is a subset of the set with m+1 frames",
                "Belady's anomaly — FIFO is not a stack algorithm, so more frames can mean more faults",
                "Thrashing, the working-set model, and why fault rate not utilisation is the signal to watch",
            ],
            "lab": {
                "title": "Page replacement and Belady's anomaly",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Model physical memory as a fixed list of `nframes` slots, each holding a page
number or `None`. Every policy has the same signature and returns
`(faults, frames)`:

- `faults` — a list of booleans, one per reference, `True` where that reference
  faulted
- `frames` — the frame list as it stands after the last reference

Choosing a victim is the only thing that differs. In every policy, a **free
frame is always preferred**, lowest index first; only a full memory evicts.

**`fifo(refs, nframes)`** — evict the frame whose page was loaded longest ago.
Note that re-referencing a page does *not* refresh it.

**`lru(refs, nframes)`** — evict the frame whose page was referenced longest ago.

**`opt(refs, nframes)`** — evict the resident page whose next use lies furthest
in the future; a page never used again is evicted first. Ties break on the
lowest frame index.

All three raise `ValueError` when `nframes < 1`.

**`fault_curve(policy, refs, max_frames)`** — `[faults with 1 frame, ..., faults
with max_frames frames]`.

**`belady_pairs(policy, refs, max_frames)`** — every `(m, m + 1)` where giving
the policy one more frame produced *more* faults.

The classic string is in `main.py`. Under FIFO it faults 9 times with three
frames and 10 times with four; under LRU the curve never rises.
''',
                "files": [{"name": "main.py", "content": r'''
CLASSIC = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def fifo(refs, nframes):
    """Evict the page loaded longest ago. Returns (faults, frames)."""
    # your code here


def lru(refs, nframes):
    """Evict the page referenced longest ago. Returns (faults, frames)."""
    # your code here


def opt(refs, nframes):
    """Evict the page whose next use is furthest away. Returns (faults, frames)."""
    # your code here


def fault_curve(policy, refs, max_frames):
    """Fault counts for 1..max_frames frames."""
    # your code here


def belady_pairs(policy, refs, max_frames):
    """(m, m+1) pairs where an extra frame made things worse."""
    # your code here


print("FIFO", fault_curve(fifo, CLASSIC, 5))
print("LRU ", fault_curve(lru, CLASSIC, 5))
print("anomaly", belady_pairs(fifo, CLASSIC, 5))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
CLASSIC = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def _free_slot(frames):
    """Lowest-numbered empty frame, or None when memory is full."""
    for i, page in enumerate(frames):
        if page is None:
            return i
    return None


def _check(nframes):
    if nframes < 1:
        raise ValueError("need at least one frame")


def fifo(refs, nframes):
    """Evict the page loaded longest ago. Returns (faults, frames)."""
    _check(nframes)
    frames = [None] * nframes
    loaded_at = [0] * nframes          # tick at which each frame was filled
    faults = []
    for tick, page in enumerate(refs):
        if page in frames:
            faults.append(False)
            continue
        slot = _free_slot(frames)
        if slot is None:
            slot = min(range(nframes), key=lambda i: (loaded_at[i], i))
        frames[slot] = page
        loaded_at[slot] = tick
        faults.append(True)
    return faults, frames


def lru(refs, nframes):
    """Evict the page referenced longest ago. Returns (faults, frames)."""
    _check(nframes)
    frames = [None] * nframes
    used_at = [0] * nframes
    faults = []
    for tick, page in enumerate(refs):
        if page in frames:
            used_at[frames.index(page)] = tick   # a hit refreshes recency
            faults.append(False)
            continue
        slot = _free_slot(frames)
        if slot is None:
            slot = min(range(nframes), key=lambda i: (used_at[i], i))
        frames[slot] = page
        used_at[slot] = tick
        faults.append(True)
    return faults, frames


def _next_use(refs, page, after):
    """Index of the next reference to page strictly after `after`, or infinity."""
    for j in range(after + 1, len(refs)):
        if refs[j] == page:
            return j
    return float("inf")


def opt(refs, nframes):
    """Evict the page whose next use is furthest away. Returns (faults, frames)."""
    _check(nframes)
    frames = [None] * nframes
    faults = []
    for tick, page in enumerate(refs):
        if page in frames:
            faults.append(False)
            continue
        slot = _free_slot(frames)
        if slot is None:
            # negate nothing: max on (next use, -index) would break ties high,
            # so sort ascending on (-next_use, index) instead
            slot = min(range(nframes),
                       key=lambda i: (-_next_use(refs, frames[i], tick), i))
        frames[slot] = page
        faults.append(True)
    return faults, frames


def fault_curve(policy, refs, max_frames):
    """Fault counts for 1..max_frames frames."""
    return [sum(policy(refs, n)[0]) for n in range(1, max_frames + 1)]


def belady_pairs(policy, refs, max_frames):
    """(m, m+1) pairs where an extra frame made things worse."""
    curve = fault_curve(policy, refs, max_frames)
    return [(m + 1, m + 2) for m in range(len(curve) - 1)
            if curve[m + 1] > curve[m]]


print("FIFO", fault_curve(fifo, CLASSIC, 5))
print("LRU ", fault_curve(lru, CLASSIC, 5))
print("anomaly", belady_pairs(fifo, CLASSIC, 5))
'''}],
                "hints": [
                    "Keep two parallel lists: the frame contents and one integer per frame (load time for FIFO, last-use time for LRU). `min(range(n), key=...)` then picks the victim.",
                    "The only difference between FIFO and LRU is whether a hit updates that integer.",
                    "For OPT, a helper returning the next index at which a page is referenced — `float('inf')` when there is none — turns the victim choice into another `min` with a negated key.",
                    "`sum(list_of_bools)` counts the True values, which is exactly the fault count.",
                ],
                "tests": [
                    {"name": "FIFO on the classic string", "code": r'''
_f, _fr = fifo(CLASSIC, 3)
assert sum(_f) == 9, f"FIFO with 3 frames faulted {sum(_f)} times, expected 9"
assert _f[:4] == [True, True, True, True], "The first touch of each page must fault"
assert _f[7] is False and _f[8] is False, "Pages 1 and 2 are still resident at references 8 and 9"
assert sorted(_fr) == [3, 4, 5], f"Frames ended as {_fr!r}, expected pages 3, 4 and 5 resident"
'''},
                    {"name": "LRU refreshes on a hit, FIFO does not", "code": r'''
_l, _ = lru(CLASSIC, 3)
assert sum(_l) == 10, f"LRU with 3 frames faulted {sum(_l)} times, expected 10"
_refs = [1, 2, 3, 1, 4, 1]
assert sum(fifo(_refs, 3)[0]) == 5, \
    "FIFO ignores the hit on page 1 and evicts it for page 4, so the last reference faults"
assert sum(lru(_refs, 3)[0]) == 4, "LRU keeps the freshly used page 1 and evicts page 2 instead"
assert fifo(_refs, 3)[1] != lru(_refs, 3)[1], \
    "The two policies must end with different resident sets on this string"
'''},
                    {"name": "OPT is the lower bound", "code": r'''
_o, _ = opt(CLASSIC, 3)
assert sum(_o) == 7, f"OPT with 3 frames faulted {sum(_o)} times, expected 7"
for _n in (1, 2, 3, 4, 5):
    _best = sum(opt(CLASSIC, _n)[0])
    for _policy in (fifo, lru):
        assert _best <= sum(_policy(CLASSIC, _n)[0]), \
            f"OPT faulted more than {_policy.__name__} with {_n} frames — check the victim rule"
'''},
                    {"name": "Free frames are filled before anything is evicted", "code": r'''
for _policy in (fifo, lru, opt):
    _faults, _frames = _policy([7, 7, 7], 3)
    assert _faults == [True, False, False], f"{_policy.__name__} on [7,7,7]: {_faults!r}"
    assert _frames == [7, None, None], \
        f"{_policy.__name__} left {_frames!r}; fill frame 0 first and leave the rest free"
    assert _policy([], 2) == ([], [None, None]), "No references means no faults"
'''},
                    {"name": "Every policy rejects a memory with no frames", "code": r'''
for _policy in (fifo, lru, opt):
    for _bad in (0, -3):
        try:
            _policy([1, 2], _bad)
            assert False, f"{_policy.__name__}(refs, {_bad}) should raise ValueError"
        except ValueError:
            pass
'''},
                    {"name": "fault_curve measures the whole memory range", "code": r'''
assert fault_curve(fifo, CLASSIC, 5) == [12, 12, 9, 10, 5], \
    f"FIFO curve is {fault_curve(fifo, CLASSIC, 5)!r}, expected [12, 12, 9, 10, 5]"
assert fault_curve(lru, CLASSIC, 5) == [12, 12, 10, 8, 5], \
    f"LRU curve is {fault_curve(lru, CLASSIC, 5)!r}, expected [12, 12, 10, 8, 5]"
'''},
                    {"name": "Belady's anomaly, demonstrated", "code": r'''
assert belady_pairs(fifo, CLASSIC, 5) == [(3, 4)], \
    f"FIFO anomaly pairs are {belady_pairs(fifo, CLASSIC, 5)!r}, expected [(3, 4)]"
assert belady_pairs(lru, CLASSIC, 5) == [], "LRU is a stack algorithm — it cannot show the anomaly"
assert belady_pairs(opt, CLASSIC, 5) == [], "OPT is also a stack algorithm"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Concurrency, synchronisation and deadlock",
            "summary": "Interleavings made explicit, semaphores that block, and a safety check for resource requests.",
            "concepts": [
                "A race condition is a property of the *set* of interleavings, not of any one run",
                "Critical sections and the three requirements: mutual exclusion, progress, bounded waiting",
                "Counting semaphores: wait blocks on zero, signal is always non-blocking",
                "The bounded-buffer solution needs three semaphores — empty, full and a mutex",
                "Coffman's four conditions: mutual exclusion, hold-and-wait, no preemption, circular wait",
                "Acquiring the mutex before the counting semaphore breaks the third and deadlocks the pair",
                "Deadlock avoidance: the banker's algorithm grants only requests that leave a safe state",
            ],
            "lab": {
                "title": "Interleaving simulator and the banker's algorithm",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
No threads. Each "thread" is a list of atomic operations, and *you* choose the
interleaving — which makes every run reproducible.

## Part 1 — the bounded buffer

An operation is a tuple: `("wait", name)`, `("signal", name)`,
`("insert", item)` or `("remove", None)`.

**`new_state(capacity)`** — `{"capacity", "buffer": [], "consumed": [],
"sem": {"empty": capacity, "full": 0, "mutex": 1}}`. `ValueError` when capacity
is below 1.

**`try_step(state, op)`** — perform one atomic operation. Returns `True` when it
completed, `False` when a `wait` found its semaphore at zero (the semaphore is
**not** decremented in that case). `insert` past the capacity raises
`RuntimeError`, as does `remove` from an empty buffer — those are the invariant
violations the simulator exists to catch. An unknown kind raises `ValueError`.

**`producer(items)` / `consumer(count)`** — build the standard programs:

```text
producer, per item:  wait empty, wait mutex, insert, signal mutex, signal full
consumer, per item:  wait full,  wait mutex, remove, signal mutex, signal empty
```

**`bad_producer(items)`** — the same, with `wait mutex` moved in front of
`wait empty`.

**`run(state, programs, schedule, pcs=None)`** — execute the given interleaving.
`programs` maps a thread name to its operation list, `schedule` is a list of
thread names. Returns `(trace, pcs)`, where the trace holds
`(tid, index, "ran" | "blocked" | "done")` per scheduled turn and `pcs` maps each
thread to its next instruction. A blocked thread does not advance. An unknown
thread name raises `ValueError`.

**`round_robin(state, programs, max_rounds=1000)`** — cycle over the threads in
sorted name order. Returns `("done", trace)` when every program finishes,
`("deadlock", trace)` when a whole cycle passes with nothing advancing, and
`("timeout", trace)` if `max_rounds` runs out.

## Part 2 — the banker's algorithm

Matrices are lists of rows, one row per process.

**`need(maximum, allocation)`** — the remaining-claim matrix.

**`is_safe(available, maximum, allocation)`** — `(safe, order)`. Scan from
process 0, take the first process whose need fits the work vector, release its
allocation into the work vector, and **restart the scan from 0**. `order` is the
safe sequence found; it is partial when `safe` is `False`.

**`request(available, maximum, allocation, pid, req)`** — `(granted, reason)`.
A request above the declared claim, or a negative amount, raises `ValueError`.
A request above what is available returns `(False, "resources unavailable")`.
Otherwise grant it tentatively and test safety; deny with
`"would leave an unsafe state"` if the pretend state is unsafe.
''',
                "files": [{"name": "main.py", "content": r'''
def new_state(capacity):
    """Fresh bounded buffer with its three semaphores."""
    # your code here


def try_step(state, op):
    """One atomic operation. True if it ran, False if a wait blocked."""
    # your code here


def producer(items):
    """wait empty, wait mutex, insert, signal mutex, signal full — per item."""
    # your code here


def consumer(count):
    """wait full, wait mutex, remove, signal mutex, signal empty — per item."""
    # your code here


def bad_producer(items):
    """The producer with the two waits in the wrong order."""
    # your code here


def run(state, programs, schedule, pcs=None):
    """Execute one interleaving. Returns (trace, pcs)."""
    # your code here


def round_robin(state, programs, max_rounds=1000):
    """Cycle the threads in sorted order. Returns (outcome, trace)."""
    # your code here


def need(maximum, allocation):
    """maximum - allocation, elementwise."""
    # your code here


def is_safe(available, maximum, allocation):
    """(safe, order) from the banker's safety check."""
    # your code here


def request(available, maximum, allocation, pid, req):
    """(granted, reason) for one resource request."""
    # your code here


AVAILABLE = [3, 3, 2]
MAXIMUM = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
ALLOCATION = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]

print(round_robin(new_state(2), {"P": producer(["a", "b"]), "C": consumer(2)})[0])
print(is_safe(AVAILABLE, MAXIMUM, ALLOCATION))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def new_state(capacity):
    """Fresh bounded buffer with its three semaphores."""
    if capacity < 1:
        raise ValueError("capacity must be at least 1")
    return {"capacity": capacity, "buffer": [], "consumed": [],
            "sem": {"empty": capacity, "full": 0, "mutex": 1}}


def try_step(state, op):
    """One atomic operation. True if it ran, False if a wait blocked."""
    kind = op[0]
    if kind == "wait":
        if state["sem"][op[1]] > 0:
            state["sem"][op[1]] -= 1
            return True
        return False                      # blocked: nothing is consumed
    if kind == "signal":
        state["sem"][op[1]] += 1
        return True
    if kind == "insert":
        if len(state["buffer"]) >= state["capacity"]:
            raise RuntimeError("buffer overflow — a producer wrote past the capacity")
        state["buffer"].append(op[1])
        return True
    if kind == "remove":
        if not state["buffer"]:
            raise RuntimeError("buffer underflow — a consumer read an empty buffer")
        state["consumed"].append(state["buffer"].pop(0))
        return True
    raise ValueError(f"unknown operation {kind!r}")


def producer(items):
    """wait empty, wait mutex, insert, signal mutex, signal full — per item."""
    ops = []
    for item in items:
        ops += [("wait", "empty"), ("wait", "mutex"), ("insert", item),
                ("signal", "mutex"), ("signal", "full")]
    return ops


def consumer(count):
    """wait full, wait mutex, remove, signal mutex, signal empty — per item."""
    ops = []
    for _ in range(count):
        ops += [("wait", "full"), ("wait", "mutex"), ("remove", None),
                ("signal", "mutex"), ("signal", "empty")]
    return ops


def bad_producer(items):
    """The producer with the two waits in the wrong order."""
    ops = []
    for item in items:
        ops += [("wait", "mutex"), ("wait", "empty"), ("insert", item),
                ("signal", "mutex"), ("signal", "full")]
    return ops


def run(state, programs, schedule, pcs=None):
    """Execute one interleaving. Returns (trace, pcs)."""
    pcs = {tid: 0 for tid in programs} if pcs is None else dict(pcs)
    trace = []
    for tid in schedule:
        if tid not in programs:
            raise ValueError(f"schedule names unknown thread {tid!r}")
        pc = pcs[tid]
        if pc >= len(programs[tid]):
            trace.append((tid, pc, "done"))
            continue
        if try_step(state, programs[tid][pc]):
            trace.append((tid, pc, "ran"))
            pcs[tid] = pc + 1
        else:
            trace.append((tid, pc, "blocked"))
    return trace, pcs


def round_robin(state, programs, max_rounds=1000):
    """Cycle the threads in sorted order. Returns (outcome, trace)."""
    order = sorted(programs)
    pcs = {tid: 0 for tid in programs}
    trace = []
    for _ in range(max_rounds):
        if all(pcs[tid] >= len(programs[tid]) for tid in order):
            return "done", trace
        cycle, new_pcs = run(state, programs, order, pcs)
        trace.extend(cycle)
        if new_pcs == pcs:                # a whole cycle with no progress
            return "deadlock", trace
        pcs = new_pcs
    return "timeout", trace


def need(maximum, allocation):
    """maximum - allocation, elementwise."""
    return [[maximum[i][j] - allocation[i][j] for j in range(len(maximum[i]))]
            for i in range(len(maximum))]


def is_safe(available, maximum, allocation):
    """(safe, order) from the banker's safety check."""
    remaining = need(maximum, allocation)
    work = list(available)
    finished = [False] * len(maximum)
    order = []
    progress = True
    while progress:
        progress = False
        for i in range(len(maximum)):
            if finished[i]:
                continue
            if all(remaining[i][j] <= work[j] for j in range(len(work))):
                for j in range(len(work)):
                    work[j] += allocation[i][j]
                finished[i] = True
                order.append(i)
                progress = True
                break                     # restart the scan from process 0
    return all(finished), order


def request(available, maximum, allocation, pid, req):
    """(granted, reason) for one resource request."""
    remaining = need(maximum, allocation)
    if any(r < 0 for r in req):
        raise ValueError("a request cannot be negative")
    if any(req[j] > remaining[pid][j] for j in range(len(req))):
        raise ValueError(f"process {pid} asked for more than its declared maximum")
    if any(req[j] > available[j] for j in range(len(req))):
        return False, "resources unavailable"
    pretend_available = [available[j] - req[j] for j in range(len(req))]
    pretend_allocation = [list(row) for row in allocation]
    for j in range(len(req)):
        pretend_allocation[pid][j] += req[j]
    safe, _ = is_safe(pretend_available, maximum, pretend_allocation)
    return (True, "granted") if safe else (False, "would leave an unsafe state")


AVAILABLE = [3, 3, 2]
MAXIMUM = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
ALLOCATION = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]

print(round_robin(new_state(2), {"P": producer(["a", "b"]), "C": consumer(2)})[0])
print(is_safe(AVAILABLE, MAXIMUM, ALLOCATION))
'''}],
                "hints": [
                    "`try_step` is the whole synchronisation model: a `wait` that finds zero must return False *without* touching the counter, otherwise the semaphore leaks.",
                    "`run` should never advance the program counter of a blocked thread — that is precisely what makes the deadlock visible.",
                    "`round_robin` detects deadlock by comparing the program counters before and after a full cycle: identical means nothing can move.",
                    "In `is_safe`, `break` out of the scan after each success so the next scan starts at process 0 again; that is what makes the safe sequence deterministic.",
                ],
                "tests": [
                    {"name": "Semaphores block instead of going negative", "code": r'''
_s = new_state(2)
assert _s["sem"] == {"empty": 2, "full": 0, "mutex": 1}, f"Initial semaphores: {_s['sem']!r}"
assert try_step(_s, ("wait", "full")) is False, "wait on a zero semaphore must return False"
assert _s["sem"]["full"] == 0, "A blocked wait must leave the counter alone, not go negative"
assert try_step(_s, ("wait", "empty")) is True and _s["sem"]["empty"] == 1
try:
    new_state(0)
    assert False, "new_state(0) should raise ValueError"
except ValueError:
    pass
try:
    try_step(_s, ("frobnicate", "empty"))
    assert False, "An unknown operation should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The buffer invariants are enforced", "code": r'''
_s = new_state(1)
try_step(_s, ("insert", "a"))
try:
    try_step(_s, ("insert", "b"))
    assert False, "Inserting past the capacity should raise RuntimeError"
except RuntimeError:
    pass
try_step(_s, ("remove", None))
assert _s["consumed"] == ["a"], f"consumed is {_s['consumed']!r}, expected ['a']"
try:
    try_step(_s, ("remove", None))
    assert False, "Removing from an empty buffer should raise RuntimeError"
except RuntimeError:
    pass
'''},
                    {"name": "A hand-picked interleaving runs and blocks", "code": r'''
_s = new_state(1)
_progs = {"P": producer(["a"]), "C": consumer(1)}
_trace, _pcs = run(_s, _progs, ["C", "P", "P", "P"])
assert _trace[0] == ("C", 0, "blocked"), f"First turn was {_trace[0]!r}; C must block on full=0"
assert _pcs["C"] == 0, "A blocked thread does not advance its program counter"
assert _pcs["P"] == 3 and _s["buffer"] == ["a"], f"P reached {_pcs['P']}, buffer {_s['buffer']!r}"
_trace2, _pcs2 = run(_s, _progs, ["P", "P", "C"], _pcs)
assert _trace2[-1] == ("C", 0, "blocked") or _pcs2["C"] == 1, "C may proceed once full is signalled"
try:
    run(_s, _progs, ["Q"])
    assert False, "An unknown thread name should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The correct programs always terminate", "code": r'''
for _cap in (1, 2, 5):
    _s = new_state(_cap)
    _outcome, _trace = round_robin(_s, {"P": producer(["a", "b", "c"]), "C": consumer(3)})
    assert _outcome == "done", f"capacity {_cap}: round_robin returned {_outcome!r}"
    assert _s["consumed"] == ["a", "b", "c"], f"capacity {_cap}: consumed {_s['consumed']!r}"
    assert _s["buffer"] == [], "Everything produced was consumed, so the buffer ends empty"
    assert _s["sem"] == {"empty": _cap, "full": 0, "mutex": 1}, \
        f"capacity {_cap}: semaphores ended at {_s['sem']!r}, they should be back where they started"
'''},
                    {"name": "The wrong wait order deadlocks", "code": r'''
_s = new_state(1)
_outcome, _trace = round_robin(_s, {"P": bad_producer(["a", "b"]), "C": consumer(2)})
assert _outcome == "deadlock", f"round_robin returned {_outcome!r}, expected 'deadlock'"
assert _s["sem"]["mutex"] == 0, "The producer is holding the mutex while it waits for a free slot"
assert _s["buffer"] == ["a"], f"The buffer is full at one item: {_s['buffer']!r}"
assert _trace[-1][2] == "blocked" and _trace[-2][2] == "blocked", \
    "The final cycle should show every thread blocked"
'''},
                    {"name": "The safety check finds the safe sequence", "code": r'''
_safe, _order = is_safe(AVAILABLE, MAXIMUM, ALLOCATION)
assert _safe is True, "The textbook state is safe"
assert _order == [1, 3, 0, 2, 4], f"Safe sequence was {_order!r}, expected [1, 3, 0, 2, 4]"
assert need(MAXIMUM, ALLOCATION)[0] == [7, 4, 3], \
    f"need row 0 is {need(MAXIMUM, ALLOCATION)[0]!r}, expected [7, 4, 3]"
_unsafe, _partial = is_safe([0, 0, 0], [[2, 2, 2], [2, 2, 2]], [[1, 0, 0], [0, 1, 0]])
assert _unsafe is False, "Nothing available and both processes still needing resources is unsafe"
assert _partial == [], f"No process could finish, so the order is empty, got {_partial!r}"
'''},
                    {"name": "Requests are granted only when the state stays safe", "code": r'''
assert request(AVAILABLE, MAXIMUM, ALLOCATION, 1, [1, 0, 2]) == (True, "granted"), \
    f"P1 asking for [1,0,2] should be granted, got {request(AVAILABLE, MAXIMUM, ALLOCATION, 1, [1, 0, 2])!r}"
_g, _why = request(AVAILABLE, MAXIMUM, ALLOCATION, 4, [3, 3, 0])
assert _g is False and _why == "would leave an unsafe state", f"P4 request gave {(_g, _why)!r}"
assert request(AVAILABLE, MAXIMUM, ALLOCATION, 0, [7, 4, 3]) == (False, "resources unavailable"), \
    "A request larger than what is on hand must wait, not be refused outright"
try:
    request(AVAILABLE, MAXIMUM, ALLOCATION, 1, [9, 0, 0])
    assert False, "Asking above the declared maximum should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "File systems and storage allocation",
            "summary": "An inode, a free list, and the fragmentation that block allocation leaves behind.",
            "concepts": [
                "The inode holds metadata and block pointers; the directory maps a name to an inode",
                "Contiguous, linked and indexed allocation, and the trade-off each one makes",
                "Free-space management: bitmap versus free list, and the cost of each operation",
                "Internal fragmentation is the slack in the last block; external fragmentation is scattered free space",
                "A file's blocks become non-contiguous when writers interleave — the seek cost of that on rotating media",
                "Deletion returns blocks to the free list; only that makes reuse possible",
                "Failing an allocation atomically: check the space first, so a full disk leaves no half-written file",
            ],
            "lab": {
                "title": "An inode allocator with a free list",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Build a block-structured file system in memory. The disk is `nblocks` blocks of
`block_size` bytes; content is plain text, one character per byte.

`FileSystem(nblocks, block_size=8)` starts with every block free and no files.
`ValueError` if either argument is below 1.

- `create(name)` — a fresh inode `{"name", "size": 0, "blocks": []}`, returned.
  `FileExistsError` if the name is taken.
- `append(name, data)` — write `data` at the end of the file. Fill the slack in
  the current last block first, then take new blocks from the free list,
  **lowest block number first**. `FileNotFoundError` for an unknown name.
  If the free list cannot cover the write, raise `OSError` and change **nothing** —
  no partial write, no leaked block.
- `read(name)` — the file's whole content as one string.
- `delete(name)` — return every block to the free list (kept sorted) and drop the
  inode. `FileNotFoundError` for an unknown name.
- `stats()` — a dict:

```python
{"blocks_total", "blocks_used", "blocks_free", "files",
 "internal_fragmentation",   # bytes of slack in the last block of every file
 "fragmented_files"}         # files whose block numbers are not consecutive
```

A 20-byte file on 8-byte blocks occupies three blocks and wastes four bytes.
Two files appended in turn interleave their blocks, and `fragmented_files`
counts the result.
''',
                "files": [{"name": "main.py", "content": r'''
import bisect


class FileSystem:
    """A block-structured file system with inodes and a sorted free list."""

    def __init__(self, nblocks, block_size=8):
        if nblocks < 1 or block_size < 1:
            raise ValueError("nblocks and block_size must both be positive")
        self.nblocks = nblocks
        self.block_size = block_size
        self.blocks = [""] * nblocks       # the platter
        self.free = list(range(nblocks))   # sorted free list
        self.inodes = {}                   # name -> inode dict

    def create(self, name):
        """A new empty inode. FileExistsError when the name is taken."""
        # your code here

    def append(self, name, data):
        """Write data at the end of the file, or raise OSError and change nothing."""
        # your code here

    def read(self, name):
        """The whole file as one string."""
        # your code here

    def delete(self, name):
        """Free every block and drop the inode."""
        # your code here

    def stats(self):
        """Usage and fragmentation counters."""
        # your code here


fs = FileSystem(16, block_size=8)
fs.create("notes")
fs.append("notes", "x" * 20)
print(fs.read("notes"))
print(fs.stats())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import bisect


class FileSystem:
    """A block-structured file system with inodes and a sorted free list."""

    def __init__(self, nblocks, block_size=8):
        if nblocks < 1 or block_size < 1:
            raise ValueError("nblocks and block_size must both be positive")
        self.nblocks = nblocks
        self.block_size = block_size
        self.blocks = [""] * nblocks       # the platter
        self.free = list(range(nblocks))   # sorted free list
        self.inodes = {}                   # name -> inode dict

    def _inode(self, name):
        if name not in self.inodes:
            raise FileNotFoundError(f"no such file: {name}")
        return self.inodes[name]

    def create(self, name):
        """A new empty inode. FileExistsError when the name is taken."""
        if name in self.inodes:
            raise FileExistsError(f"file already exists: {name}")
        self.inodes[name] = {"name": name, "size": 0, "blocks": []}
        return self.inodes[name]

    def append(self, name, data):
        """Write data at the end of the file, or raise OSError and change nothing."""
        inode = self._inode(name)
        slack = len(inode["blocks"]) * self.block_size - inode["size"]
        overflow = max(0, len(data) - slack)
        # ceiling division without importing math
        needed = -(-overflow // self.block_size)
        if needed > len(self.free):
            raise OSError("no space left on device")
        position = inode["size"]
        for char in data:
            index = position // self.block_size
            if index >= len(inode["blocks"]):
                inode["blocks"].append(self.free.pop(0))
            self.blocks[inode["blocks"][index]] += char
            position += 1
        inode["size"] = position
        return len(data)

    def read(self, name):
        """The whole file as one string."""
        inode = self._inode(name)
        return "".join(self.blocks[b] for b in inode["blocks"])

    def delete(self, name):
        """Free every block and drop the inode."""
        inode = self._inode(name)
        for block in inode["blocks"]:
            self.blocks[block] = ""
            bisect.insort(self.free, block)   # the free list stays sorted
        del self.inodes[name]

    @staticmethod
    def _contiguous(blocks):
        return all(blocks[i + 1] == blocks[i] + 1 for i in range(len(blocks) - 1))

    def stats(self):
        """Usage and fragmentation counters."""
        used = sum(len(i["blocks"]) for i in self.inodes.values())
        internal = sum(len(i["blocks"]) * self.block_size - i["size"]
                       for i in self.inodes.values())
        fragmented = sum(1 for i in self.inodes.values()
                         if not self._contiguous(i["blocks"]))
        return {"blocks_total": self.nblocks, "blocks_used": used,
                "blocks_free": len(self.free), "files": len(self.inodes),
                "internal_fragmentation": internal, "fragmented_files": fragmented}


fs = FileSystem(16, block_size=8)
fs.create("notes")
fs.append("notes", "x" * 20)
print(fs.read("notes"))
print(fs.stats())
'''}],
                "hints": [
                    "The slack in the last block is `len(blocks) * block_size - size`; only the bytes beyond that need new blocks.",
                    "`-(-overflow // self.block_size)` is ceiling division with no import.",
                    "Check `needed > len(self.free)` *before* writing a single character — that is what makes a failed append atomic.",
                    "`bisect.insort(self.free, block)` puts a freed block back in order, so the next allocation still takes the lowest number.",
                ],
                "tests": [
                    {"name": "Create, append, read back", "code": r'''
_fs = FileSystem(16, block_size=8)
_fs.create("a")
assert _fs.read("a") == "", "A fresh file is empty"
_fs.append("a", "hello world")
assert _fs.read("a") == "hello world", f"read gave {_fs.read('a')!r}"
_fs.append("a", "!!")
assert _fs.read("a") == "hello world!!", f"read gave {_fs.read('a')!r} after the second append"
assert _fs.inodes["a"]["size"] == 13, f"size is {_fs.inodes['a']['size']!r}, expected 13"
'''},
                    {"name": "Blocks are allocated lowest first, and slack is reused", "code": r'''
_fs = FileSystem(8, block_size=4)
_fs.create("a")
_fs.append("a", "ab")
assert _fs.inodes["a"]["blocks"] == [0], f"blocks are {_fs.inodes['a']['blocks']!r}, expected [0]"
_fs.append("a", "cd")
assert _fs.inodes["a"]["blocks"] == [0], "Two spare bytes remained in block 0 — fill them first"
_fs.append("a", "e")
assert _fs.inodes["a"]["blocks"] == [0, 1], f"blocks are {_fs.inodes['a']['blocks']!r}"
assert _fs.read("a") == "abcde", f"read gave {_fs.read('a')!r}"
'''},
                    {"name": "Errors on unknown and duplicate names", "code": r'''
_fs = FileSystem(8, block_size=4)
_fs.create("a")
try:
    _fs.create("a")
    assert False, "Creating an existing name should raise FileExistsError"
except FileExistsError:
    pass
for _call in (lambda: _fs.read("ghost"), lambda: _fs.append("ghost", "x"),
              lambda: _fs.delete("ghost")):
    try:
        _call()
        assert False, "Operating on a missing file should raise FileNotFoundError"
    except FileNotFoundError:
        pass
for _bad in ((0, 4), (4, 0), (-1, 4)):
    try:
        FileSystem(*_bad)
        assert False, f"FileSystem{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Deleting returns blocks to the free list in order", "code": r'''
_fs = FileSystem(8, block_size=4)
_fs.create("a"); _fs.append("a", "aaaa")
_fs.create("b"); _fs.append("b", "bbbb")
_fs.create("c"); _fs.append("c", "cccc")
assert _fs.free == [3, 4, 5, 6, 7], f"free list is {_fs.free!r}"
_fs.delete("b")
assert _fs.free == [1, 3, 4, 5, 6, 7], f"free list after deleting b is {_fs.free!r} — keep it sorted"
assert "b" not in _fs.inodes, "The inode goes too"
_fs.create("d"); _fs.append("d", "dddd")
assert _fs.inodes["d"]["blocks"] == [1], "The freed block is the lowest, so it is reused first"
assert _fs.read("a") == "aaaa" and _fs.read("c") == "cccc", "The other files are untouched"
'''},
                    {"name": "A full disk fails atomically", "code": r'''
_fs = FileSystem(2, block_size=4)
_fs.create("a")
_fs.append("a", "xxxxxxxx")
assert _fs.free == [], "Both blocks are taken"
try:
    _fs.append("a", "y")
    assert False, "Appending to a full disk should raise OSError"
except OSError:
    pass
assert _fs.read("a") == "xxxxxxxx", f"The failed append changed the file: {_fs.read('a')!r}"
assert _fs.inodes["a"]["size"] == 8 and _fs.inodes["a"]["blocks"] == [0, 1], \
    "A failed append must leave the inode exactly as it was"
'''},
                    {"name": "Internal fragmentation is the slack in the last block", "code": r'''
_fs = FileSystem(16, block_size=8)
_fs.create("notes")
_fs.append("notes", "x" * 20)
_s = _fs.stats()
assert _s["blocks_used"] == 3, f"20 bytes over 8-byte blocks needs 3 blocks, got {_s['blocks_used']}"
assert _s["internal_fragmentation"] == 4, \
    f"internal_fragmentation is {_s['internal_fragmentation']}, expected 4"
assert _s["blocks_free"] == 13 and _s["blocks_total"] == 16, f"stats: {_s!r}"
assert FileSystem(4, block_size=4).stats()["internal_fragmentation"] == 0, \
    "An empty file system wastes nothing"
'''},
                    {"name": "Interleaved writers fragment their files", "code": r'''
_fs = FileSystem(16, block_size=4)
for _name in ("a", "b"):
    _fs.create(_name)
for _round in range(2):
    _fs.append("a", "aaaa")
    _fs.append("b", "bbbb")
assert _fs.inodes["a"]["blocks"] == [0, 2], f"a holds {_fs.inodes['a']['blocks']!r}"
assert _fs.inodes["b"]["blocks"] == [1, 3], f"b holds {_fs.inodes['b']['blocks']!r}"
assert _fs.stats()["fragmented_files"] == 2, \
    f"fragmented_files is {_fs.stats()['fragmented_files']}, expected 2"
_fs.create("c")
_fs.append("c", "cccccccc")
assert _fs.stats()["fragmented_files"] == 2, "c got blocks 4 and 5, which are consecutive"
assert _fs.read("a") == "aaaaaaaa" and _fs.read("b") == "bbbbbbbb", "Content survives fragmentation"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a miniature kernel simulator",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
The four labs become one kernel. `kernel.py` holds the machinery and is what the
checks import; `main.py` boots a small workload and prints the trace.

A process is a list of operations, executed in order:

```python
("compute", n)          # n ticks of user-mode work
("mem", page)           # one reference to virtual page `page`
("write", name, data)   # a syscall appending to a file
("read", name)          # a syscall reading a file
```

## `MemoryManager(frames)`

A single global frame table shared by every process, so a frame holds the pair
`(pid, page)`. `ValueError` when `frames < 1`.

`access(pid, page)` returns `(fault, frame_index)`. A hit refreshes recency. A
miss takes the lowest free frame if there is one, otherwise evicts the least
recently used frame, ties going to the lowest index. It counts faults in
`self.faults`.

## `FileStore()`

`write(name, data)` appends and returns the byte count. `read(name)` returns the
content or raises `FileNotFoundError`.

## `Kernel(frames=3, quantum=2)`

`ValueError` when the quantum is below 1. `spawn(pid, program)` registers a
process in arrival order and raises `ValueError` on a duplicate pid.

`run()` is round robin over a ready queue seeded with the spawn order. On each
dispatch the process gets at most `quantum` ticks:

- `compute` burns ticks; a burst longer than the remaining quantum is **split**,
  and the rest resumes on the next dispatch. `n < 1` raises `ValueError`.
- `mem` costs one tick. A **page fault yields the CPU immediately** — the process
  goes to the back of the queue as though it had blocked on the disk.
- `write` and `read` each cost one tick and also yield. A read of a missing file
  is logged and the process carries on; the kernel does not crash on a bad
  syscall.
- An unknown operation raises `ValueError`.

A process whose program is exhausted logs `EXIT`; otherwise it logs `PREEMPT`
and rejoins the queue.

Every event appends one line to `self.trace`, formatted
`f"{tick:>4} {pid} {event}"`, with events `DISPATCH`, `COMPUTE n`,
`MEMHIT page p in frame f`, `PAGEFAULT page p -> frame f`,
`SYSCALL write name`, `SYSCALL read name (n bytes)`,
`SYSCALL read name ENOENT`, `PREEMPT`, `EXIT`.

`run()` returns the report:

```python
{"ticks", "switches", "completed": {pid: tick}, "faults": {pid: count},
 "page_faults", "trace": [...]}
```

## Suggested order

`MemoryManager` and `FileStore` first — both are testable on their own. Then the
dispatch loop with `compute` only, then `mem`, then the two syscalls, and the
trace formatting last.
''',
        "deliverables": [
            "`kernel.py` — `MemoryManager`, `FileStore` and `Kernel`, importable with no side effects",
            "A global LRU frame table keyed by `(pid, page)`, with its own fault counter",
            "A round-robin dispatcher that splits an over-long compute burst across dispatches",
            "Page faults and syscalls that yield the CPU, so the trace shows real interleaving",
            "A tick-stamped trace log that accounts for every tick the kernel charged",
            "`main.py` — a demo workload, the printed trace, and the summary report",
        ],
        "constraints": [
            "Standard library only; `collections.deque` is the one import you need",
            "`kernel.py` defines classes only — importing it must print nothing",
            "No global mutable state: two `Kernel` objects must not share memory, files or traces",
            "A failed syscall is logged and survived, never raised out of `run()`",
            "The tick counter only ever advances by the cost of work actually performed",
        ],
        "rubric": [
            {"criterion": "Correctness of the simulation", "weight": 40,
             "evidence": "Every automated check passes, including the exact tick, switch and fault counts for the reference workload."},
            {"criterion": "Replacement policy", "weight": 20,
             "evidence": "MemoryManager reproduces textbook LRU fault counts standalone, prefers free frames, and breaks ties on the lowest index."},
            {"criterion": "Scheduling and preemption", "weight": 20,
             "evidence": "Long bursts split across dispatches, faults and syscalls yield, and the ready queue preserves round-robin order."},
            {"criterion": "Trace and reporting", "weight": 12,
             "evidence": "Trace lines carry the tick, pid and event in the stated format, and the report totals agree with the trace."},
            {"criterion": "Robustness", "weight": 8,
             "evidence": "Bad quanta, duplicate pids, unknown operations and missing files are handled exactly as specified."},
        ],
        "hints": [
            "Keep one dict per process: program, pc, and `left` — the ticks still owed by a half-finished compute burst. `left is None` means the next burst has not started.",
            "The dispatch loop has two exits: the quantum ran out (PREEMPT) or the program ran out (EXIT). Decide by looking at the pc after the loop, not inside it.",
            "A yielding operation (fault, read, write) should `break` out of the inner loop with the pc already advanced, so the process resumes at the next operation.",
            "`min(range(self.nframes), key=lambda i: (self.used_at[i], i))` gives the LRU victim with the lowest-index tie-break in one line.",
        ],
        "files": [
            {"name": "kernel.py", "content": r'''
from collections import deque


class MemoryManager:
    """A global LRU frame table. A frame holds the pair (pid, page)."""

    def __init__(self, frames):
        if frames < 1:
            raise ValueError("need at least one frame")
        self.nframes = frames
        self.frames = [None] * frames
        self.used_at = [-1] * frames
        self.clock = 0
        self.faults = 0

    def access(self, pid, page):
        """Reference one page. Returns (fault, frame_index)."""
        # your code here


class FileStore:
    """A flat namespace of append-only text files."""

    def __init__(self):
        self.files = {}

    def write(self, name, data):
        """Append data, returning how many bytes were written."""
        # your code here

    def read(self, name):
        """The file content, or FileNotFoundError."""
        # your code here


class Kernel:
    """Round-robin dispatcher over paged processes that make syscalls."""

    def __init__(self, frames=3, quantum=2):
        if quantum < 1:
            raise ValueError("quantum must be at least one tick")
        self.memory = MemoryManager(frames)
        self.files = FileStore()
        self.quantum = quantum
        self.procs = {}
        self.order = []
        self.trace = []
        self.tick = 0
        self.switches = 0

    def log(self, pid, event):
        """Append one tick-stamped trace line."""
        self.trace.append(f"{self.tick:>4} {pid} {event}")

    def spawn(self, pid, program):
        """Register a process. ValueError on a duplicate pid."""
        # your code here

    def run(self):
        """Dispatch until every process has exited. Returns the report."""
        # your code here

    def report(self):
        """Totals for the whole run."""
        # your code here
'''},
            {"name": "main.py", "content": r'''
from kernel import Kernel

k = Kernel(frames=2, quantum=2)
k.spawn("P1", [("compute", 3), ("mem", 0), ("write", "log", "started")])
k.spawn("P2", [("mem", 0), ("mem", 1), ("read", "log")])

result = k.run()
for line in result["trace"]:
    print(line)
print(result["ticks"], "ticks,", result["switches"], "dispatches,",
      result["page_faults"], "page faults")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "kernel.py", "content": r'''
from collections import deque


class MemoryManager:
    """A global LRU frame table. A frame holds the pair (pid, page)."""

    def __init__(self, frames):
        if frames < 1:
            raise ValueError("need at least one frame")
        self.nframes = frames
        self.frames = [None] * frames
        self.used_at = [-1] * frames
        self.clock = 0
        self.faults = 0

    def access(self, pid, page):
        """Reference one page. Returns (fault, frame_index)."""
        self.clock += 1
        key = (pid, page)
        for i, held in enumerate(self.frames):
            if held == key:
                self.used_at[i] = self.clock       # a hit refreshes recency
                return False, i
        victim = None
        for i, held in enumerate(self.frames):     # free frames first
            if held is None:
                victim = i
                break
        if victim is None:                         # otherwise the LRU frame
            victim = min(range(self.nframes), key=lambda i: (self.used_at[i], i))
        self.frames[victim] = key
        self.used_at[victim] = self.clock
        self.faults += 1
        return True, victim


class FileStore:
    """A flat namespace of append-only text files."""

    def __init__(self):
        self.files = {}

    def write(self, name, data):
        """Append data, returning how many bytes were written."""
        self.files[name] = self.files.get(name, "") + data
        return len(data)

    def read(self, name):
        """The file content, or FileNotFoundError."""
        if name not in self.files:
            raise FileNotFoundError(f"no such file: {name}")
        return self.files[name]


class Kernel:
    """Round-robin dispatcher over paged processes that make syscalls."""

    def __init__(self, frames=3, quantum=2):
        if quantum < 1:
            raise ValueError("quantum must be at least one tick")
        self.memory = MemoryManager(frames)
        self.files = FileStore()
        self.quantum = quantum
        self.procs = {}
        self.order = []
        self.trace = []
        self.tick = 0
        self.switches = 0

    def log(self, pid, event):
        """Append one tick-stamped trace line."""
        self.trace.append(f"{self.tick:>4} {pid} {event}")

    def spawn(self, pid, program):
        """Register a process. ValueError on a duplicate pid."""
        if pid in self.procs:
            raise ValueError(f"pid {pid!r} already exists")
        self.procs[pid] = {"pid": pid, "program": list(program), "pc": 0,
                           "left": None, "faults": 0, "finished": None}
        self.order.append(pid)
        return self.procs[pid]

    def _step(self, proc, budget):
        """Run one operation. Returns (ticks_spent, yielded)."""
        pid = proc["pid"]
        op = proc["program"][proc["pc"]]
        kind = op[0]

        if kind == "compute":
            if proc["left"] is None:
                if op[1] < 1:
                    raise ValueError("compute needs a positive tick count")
                proc["left"] = op[1]
            spent = min(budget, proc["left"])
            self.tick += spent
            proc["left"] -= spent
            self.log(pid, f"COMPUTE {spent}")
            if proc["left"] == 0:               # burst finished, move on
                proc["left"] = None
                proc["pc"] += 1
            return spent, False

        if kind == "mem":
            fault, frame = self.memory.access(pid, op[1])
            self.tick += 1
            proc["pc"] += 1
            if fault:
                proc["faults"] += 1
                self.log(pid, f"PAGEFAULT page {op[1]} -> frame {frame}")
                return 1, True                  # a fault blocks on the disk
            self.log(pid, f"MEMHIT page {op[1]} in frame {frame}")
            return 1, False

        if kind == "write":
            self.files.write(op[1], op[2])
            self.tick += 1
            proc["pc"] += 1
            self.log(pid, f"SYSCALL write {op[1]}")
            return 1, True

        if kind == "read":
            self.tick += 1
            proc["pc"] += 1
            try:
                data = self.files.read(op[1])
            except FileNotFoundError:
                self.log(pid, f"SYSCALL read {op[1]} ENOENT")
            else:
                self.log(pid, f"SYSCALL read {op[1]} ({len(data)} bytes)")
            return 1, True

        raise ValueError(f"unknown operation {kind!r}")

    def run(self):
        """Dispatch until every process has exited. Returns the report."""
        ready = deque(self.order)
        while ready:
            pid = ready.popleft()
            proc = self.procs[pid]
            self.switches += 1
            self.log(pid, "DISPATCH")
            budget = self.quantum
            while budget > 0 and proc["pc"] < len(proc["program"]):
                spent, yielded = self._step(proc, budget)
                budget -= spent
                if yielded:
                    break
            if proc["pc"] >= len(proc["program"]):
                proc["finished"] = self.tick
                self.log(pid, "EXIT")
            else:
                self.log(pid, "PREEMPT")
                ready.append(pid)
        return self.report()

    def report(self):
        """Totals for the whole run."""
        return {"ticks": self.tick,
                "switches": self.switches,
                "completed": {pid: self.procs[pid]["finished"] for pid in self.order},
                "faults": {pid: self.procs[pid]["faults"] for pid in self.order},
                "page_faults": self.memory.faults,
                "trace": list(self.trace)}
'''},
            {"name": "main.py", "content": r'''
from kernel import Kernel

k = Kernel(frames=2, quantum=2)
k.spawn("P1", [("compute", 3), ("mem", 0), ("write", "log", "started")])
k.spawn("P2", [("mem", 0), ("mem", 1), ("read", "log")])

result = k.run()
for line in result["trace"]:
    print(line)
print(result["ticks"], "ticks,", result["switches"], "dispatches,",
      result["page_faults"], "page faults")
print("completed:", result["completed"])
'''},
        ],
        "tests": [
            {"name": "MemoryManager fills free frames before evicting", "code": r'''
from kernel import MemoryManager
_m = MemoryManager(3)
assert _m.access("P", 7) == (True, 0), f"First access gave {_m.access('P', 7)!r}"
_m2 = MemoryManager(3)
assert _m2.access("P", 7) == (True, 0)
assert _m2.access("P", 8) == (True, 1), "The second page takes the next free frame"
assert _m2.access("P", 7) == (False, 0), "Page 7 is still resident, so this is a hit"
assert _m2.faults == 2, f"faults is {_m2.faults}, expected 2"
try:
    MemoryManager(0)
    assert False, "MemoryManager(0) should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "MemoryManager reproduces textbook LRU", "code": r'''
from kernel import MemoryManager
_m = MemoryManager(3)
for _page in [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]:
    _m.access("P", _page)
assert _m.faults == 10, f"LRU with 3 frames faulted {_m.faults} times, expected 10"
_m4 = MemoryManager(4)
for _page in [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]:
    _m4.access("P", _page)
assert _m4.faults == 8, f"LRU with 4 frames faulted {_m4.faults} times, expected 8"
'''},
            {"name": "Frames are keyed by process as well as page", "code": r'''
from kernel import MemoryManager
_m = MemoryManager(2)
assert _m.access("P1", 0)[0] is True
assert _m.access("P2", 0)[0] is True, "Page 0 of another process is a different frame"
assert _m.access("P1", 0) == (False, 0), "P1's page 0 is still in frame 0"
'''},
            {"name": "FileStore appends and reports missing files", "code": r'''
from kernel import FileStore
_f = FileStore()
assert _f.write("log", "abc") == 3, "write returns the byte count"
_f.write("log", "de")
assert _f.read("log") == "abcde", f"read gave {_f.read('log')!r}"
try:
    _f.read("ghost")
    assert False, "Reading a missing file should raise FileNotFoundError"
except FileNotFoundError:
    pass
'''},
            {"name": "The kernel rejects bad configuration", "code": r'''
from kernel import Kernel
for _bad in (0, -2):
    try:
        Kernel(frames=2, quantum=_bad)
        assert False, f"Kernel(quantum={_bad}) should raise ValueError"
    except ValueError:
        pass
_k = Kernel(frames=2, quantum=2)
_k.spawn("A", [("compute", 1)])
try:
    _k.spawn("A", [("compute", 1)])
    assert False, "A duplicate pid should raise ValueError"
except ValueError:
    pass
assert Kernel(frames=1, quantum=1).run()["ticks"] == 0, "No processes means no ticks"
'''},
            {"name": "A long burst is split across dispatches", "code": r'''
from kernel import Kernel
_k = Kernel(frames=2, quantum=2)
_k.spawn("A", [("compute", 5)])
_r = _k.run()
assert _r["ticks"] == 5, f"ticks is {_r['ticks']}, expected 5"
assert _r["switches"] == 3, f"A 5-tick burst at quantum 2 needs 3 dispatches, got {_r['switches']}"
assert _r["completed"] == {"A": 5}, f"completed is {_r['completed']!r}"
assert [l for l in _r["trace"] if "COMPUTE" in l] == \
    ["   2 A COMPUTE 2", "   4 A COMPUTE 2", "   5 A COMPUTE 1"], \
    f"COMPUTE lines were {[l for l in _r['trace'] if 'COMPUTE' in l]!r}"
'''},
            {"name": "Faults and syscalls yield the CPU", "code": r'''
from kernel import Kernel
_k = Kernel(frames=2, quantum=2)
_k.spawn("P1", [("compute", 3), ("mem", 0)])
_k.spawn("P2", [("mem", 0), ("compute", 1)])
_r = _k.run()
assert _r["ticks"] == 6, f"ticks is {_r['ticks']}, expected 6"
assert _r["switches"] == 4, f"switches is {_r['switches']}, expected 4"
assert _r["completed"] == {"P1": 5, "P2": 6}, f"completed is {_r['completed']!r}"
assert _r["faults"] == {"P1": 1, "P2": 1}, f"faults is {_r['faults']!r}"
assert _r["page_faults"] == 2, f"page_faults is {_r['page_faults']}"
'''},
            {"name": "Trace lines are tick-stamped and complete", "code": r'''
from kernel import Kernel
_k = Kernel(frames=2, quantum=2)
_k.spawn("P1", [("compute", 3), ("mem", 0)])
_k.spawn("P2", [("mem", 0), ("compute", 1)])
_r = _k.run()
assert _r["trace"][0] == "   0 P1 DISPATCH", f"First line is {_r['trace'][0]!r}"
assert sum(1 for l in _r["trace"] if l.endswith("DISPATCH")) == _r["switches"], \
    "There is exactly one DISPATCH line per dispatch"
assert sum(1 for l in _r["trace"] if l.endswith("EXIT")) == 2, "Both processes must log EXIT"
assert any("PAGEFAULT page 0 -> frame 0" in l for l in _r["trace"]), \
    f"Expected a PAGEFAULT line, trace was {_r['trace']!r}"
assert any(l.endswith("PREEMPT") for l in _r["trace"]), "P1 is preempted by the quantum"
'''},
            {"name": "Syscalls reach the file store", "code": r'''
from kernel import Kernel
_k = Kernel(frames=2, quantum=3)
_k.spawn("W", [("write", "log", "hello"), ("write", "log", "!")])
_k.spawn("R", [("read", "log"), ("read", "ghost")])
_r = _k.run()
assert _k.files.read("log") == "hello!", f"The file holds {_k.files.read('log')!r}"
assert any("SYSCALL read log" in l for l in _r["trace"]), "The read syscall should be logged"
assert any("ENOENT" in l for l in _r["trace"]), \
    "Reading a missing file is logged as ENOENT, not raised"
assert _r["completed"]["R"] is not None, "A failed syscall must not stop the process"
'''},
            {"name": "An unknown operation is refused", "code": r'''
from kernel import Kernel
_k = Kernel(frames=2, quantum=2)
_k.spawn("A", [("teleport", 3)])
try:
    _k.run()
    assert False, "An unknown operation should raise ValueError"
except ValueError:
    pass
_k2 = Kernel(frames=2, quantum=2)
_k2.spawn("A", [("compute", 0)])
try:
    _k2.run()
    assert False, "A compute burst of 0 ticks should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Kernels are independent and import-clean", "code": r'''
from kernel import Kernel
_a = Kernel(frames=2, quantum=2)
_a.spawn("X", [("mem", 0)])
_a.run()
_b = Kernel(frames=2, quantum=2)
assert _b.trace == [] and _b.tick == 0, "A second Kernel starts empty"
assert _b.memory.faults == 0, "Two kernels must not share a frame table"
assert _b.files.files == {}, "Two kernels must not share a file store"
_src = open("kernel.py").read()
assert "print(" not in _src, "kernel.py defines classes; the printing belongs in main.py"
'''},
            {"name": "The demo in main.py runs and reports", "code": r'''
assert "ticks" in _out and "dispatches" in _out, \
    f"main.py should print the summary line; stdout was {_out!r}"
assert "DISPATCH" in _out, "main.py should print the trace"
'''},
        ],
    },
}
