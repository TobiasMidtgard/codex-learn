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
            "quiz": {
                "title": "What the scheduler is actually choosing",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A context switch moves the processor from one process to another. What does it cost?",
                        "opts": [
                            "Saving and restoring the register set and the page-table base, plus the cache and TLB misses the incoming process then takes",
                            "Only the handful of instructions that copy the registers into the process control block",
                            "Nothing measurable, on a processor with hardware task switching",
                            "Exactly one quantum, because the switch is charged to the outgoing process's slice",
                        ],
                        "a": 0,
                        "why": r"""
The visible part — spilling registers and reloading a page-table base — is tens to a
few hundred instructions, and if that were the whole bill a microsecond quantum would
be fine. The expensive part never appears in the switch routine: the incoming process
arrives to a cache full of someone else's lines and a TLB that has just been
invalidated, so its first thousands of instructions run at memory speed instead of
cache speed. None of that is charged to anybody's slice — it happens *between* slices,
which is precisely what makes it overhead rather than work.
""",
                    },
                    {
                        "q": "Non-preemptive shortest-job-first is optimal, in one specific sense. Which?",
                        "opts": [
                            "The smallest average waiting time achievable for a set of jobs that are all ready at the same instant",
                            "The smallest average waiting time whatever the arrival times",
                            "The smallest waiting time for the longest job in the set",
                            "The smallest spread of waiting times across the set",
                        ],
                        "a": 0,
                        "why": r"""
The proof is an exchange argument, and it is short. Take any schedule that runs a
longer job immediately before a shorter one and swap the pair: the shorter job's
completion moves earlier by more than the longer one's moves later, so the total
waiting drops. Repeat until nothing is out of shortest-first order. That argument
needs every job to be available at the swap, which is why the claim collapses once
arrivals are staggered — a preemptive scheduler that abandons a long job for a shorter
one that has just turned up beats non-preemptive SJF there. The longest job is the one
SJF treats worst, since it is the one left until last, and for the same reason the
spread of waiting times under SJF is wider than under round robin, not narrower.
""",
                    },
                    {
                        "q": "A process with a 100 ms burst reaches the head of an FCFS queue ahead of ten processes that each want 1 ms of CPU and then go back to their devices. What happens?",
                        "opts": [
                            "All ten wait out the full 100 ms, and their devices sit idle for the whole of it",
                            "FCFS notices the imbalance and lets the short jobs past",
                            "The ten are unaffected, because they spend most of their time blocked anyway",
                            "The long process is preempted as soon as a shorter one becomes ready",
                        ],
                        "a": 0,
                        "why": r"""
This is the convoy effect, and the damage is not the 100 ms of waiting — it is the
idle hardware. Those ten processes were the ones keeping the disks and the network
busy; while they queue, every device they own does nothing, and when they finally get
their millisecond each they immediately block again, leaving the CPU to the long job
once more. FCFS has no notion of burst length to notice anything with, and no
preemption to act on it if it did: the queue is the entire policy.
""",
                    },
                    {
                        "q": "Round robin is run with a quantum far larger than any process's burst. Which policy does it become?",
                        "opts": [
                            "FCFS",
                            "SJF",
                            "Strict priority",
                            "Nothing else — a preemptive policy cannot degenerate into a non-preemptive one",
                        ],
                        "a": 0,
                        "why": r"""
If the quantum outlasts every burst then no process is ever preempted: each is
dispatched once, runs to completion, and the order it runs in is the order the ready
queue holds, which is arrival order. That is FCFS with a timer that never fires. The
other end of the range fails in the mirror image — a quantum close to the switch cost
spends a large fraction of the processor on switching and delivers the rest in useless
slivers. The usable range sits between the two, which is where the rule of thumb that
80% of bursts should be shorter than the quantum comes from.
""",
                    },
                    {
                        "q": "A process arrives at tick 3, needs 6 ticks of CPU, and completes at tick 22. What is its waiting time?",
                        "opts": ["13", "19", "16", "6"],
                        "a": 0,
                        "why": r"""
Turnaround is completion minus arrival: $22 - 3 = 19$ ticks spent in the system. Six
of those it spent holding the processor, so the other 13 it spent in a queue —
waiting is turnaround minus burst. Both numbers are *derived*, which is the whole
reason the lab makes the schedulers return a timeline and nothing else: 19 is the
turnaround rather than the waiting, and $22 - 6 = 16$ is what you get from measuring
the turnaround from tick 0 instead of from the moment the process appeared.
""",
                    },
                    {
                        "q": "Strict priority scheduling can starve a low-priority process indefinitely. What does ageing do about it?",
                        "opts": [
                            "It raises a process's priority the longer it has been waiting, so every process eventually reaches the head",
                            "It kills processes that have waited beyond a threshold, clearing the queue",
                            "It lowers every process's priority at the same fixed rate, which keeps the queue moving",
                            "It caps the burst length, so no process can hold the processor long enough to starve another",
                        ],
                        "a": 0,
                        "why": r"""
Starvation happens because a static priority is a promise that never expires: if
higher-priority work keeps arriving, the low-priority process is passed over forever.
Ageing makes the priority a function of waiting time, so a process that has been
overlooked climbs until it wins on its own merits — the ordering is preserved for
processes that arrived together and inverted for one that has waited long enough.
Lowering everybody at the same rate changes no ordering at all and therefore fixes
nothing. Capping bursts is a different mechanism entirely: it bounds how long one
dispatch lasts, not how many dispatches you are skipped for.
""",
                    },
                ],
            },
            "blanks": {
                "title": "One dispatch, and the numbers that fall out of it",
                "minutes": 9,
                "caption": "round robin, one turn — then the metrics, read off the finished timeline",
                "lang": "python",
                "brief": r"""
Every scheduler in this module produces the same artefact: a list of
`(pid, start, end)` segments. Everything else — turnaround, waiting, the averages you
compare policies with — is arithmetic on that list afterwards. Fill the holes in one
dispatch and in the two lines that turn a timeline into numbers.

Nothing runs here. You are choosing between spellings, not writing code.
""",
                "listing": r'''
# One dispatch of round robin, then the metrics read back off the timeline.

pid       = queue.___                      # the process at the head goes next
slice_len = ___(quantum, remaining[pid])   # never run longer than what is left
timeline.append((pid, clock, clock + slice_len))
clock += slice_len
remaining[pid] -= slice_len
admit(clock)                               # arrivals at this tick queue ahead of it
if remaining[pid] > 0:
    queue.append(pid)

# afterwards, per process, from the timeline alone
completion = max(end for p, start, end in timeline if p == pid)
turnaround = completion - ___
waiting    = turnaround - ___
''',
                "blanks": [
                    {
                        "prompt": "Which end of the ready queue does the next process come from?",
                        "hole": "?",
                        "opts": ["pop(0)", "pop()", "append(pid)", "remove(pid)"],
                        "a": 0,
                        "why": "The ready queue is FIFO: `pop(0)` takes the process that has waited longest, and the requeue at the bottom of the block puts the preempted one at the back. That pairing is the entire fairness guarantee.",
                        "whys": [
                            "The ready queue is FIFO: `pop(0)` takes the process that has waited longest, and the requeue at the bottom of the block puts the preempted one at the back. That pairing is the entire fairness guarantee.",
                            "`pop()` takes the tail — which, given the `queue.append(pid)` three lines down, is the process that was just preempted. It would immediately redispatch itself and nothing else would ever run. That is a stack, and a stack starves.",
                            "`append` puts something onto the queue rather than taking something off, and it returns `None`. The next line would then look up `remaining[None]` and raise `KeyError`.",
                            "`remove(pid)` needs the pid you have not chosen yet, so it cannot be what chooses it — and it returns `None` too.",
                        ],
                    },
                    {
                        "prompt": "A slice is capped twice over: by the quantum, and by the work the process still owes.",
                        "hole": "?",
                        "opts": ["min", "max", "sum", "abs"],
                        "a": 0,
                        "why": "`min` takes whichever cap bites first. A process with 2 ticks left and a quantum of 3 runs for 2 and then exits — the quantum is a ceiling on the slice, never a floor.",
                        "whys": [
                            "`min` takes whichever cap bites first. A process with 2 ticks left and a quantum of 3 runs for 2 and then exits — the quantum is a ceiling on the slice, never a floor.",
                            "`max` charges the larger of the two, so it makes the quantum a floor instead of a ceiling. A process with 2 ticks left and a quantum of 3 is billed for 3 and `remaining` ends at -1; one with 5 left is billed for all 5 in a single slice and ends at 0. Either way `remaining[pid] > 0` is false, so nothing is ever requeued: round robin collapses into run-to-completion, and short processes are credited with more processor time than they asked for.",
                            "`sum` takes an iterable and a starting value, not two numbers, so `sum(3, 2)` raises `TypeError: 'int' object is not iterable` and no slice is computed at all. Read charitably as addition it would be wrong anyway: billing the quantum *and* the outstanding work in one slice claims more processor time than the workload ever asked for.",
                            "`abs` takes one argument, not two. Both of these numbers are already non-negative in any case, so there would be nothing for it to do.",
                        ],
                    },
                    {
                        "prompt": "Turnaround is measured from the moment the process appeared, not from the moment the clock started.",
                        "hole": "?",
                        "opts": ["arrival", "burst", "0", "clock"],
                        "a": 0,
                        "why": "Turnaround is completion minus arrival — the whole span the process spent in the system, running or queued. Subtracting anything else measures from the wrong end.",
                        "whys": [
                            "Turnaround is completion minus arrival — the whole span the process spent in the system, running or queued. Subtracting anything else measures from the wrong end.",
                            "Subtracting the burst here yields the waiting time directly and leaves the next line with nothing left to subtract. They are two different quantities and the code needs both.",
                            "Measuring from tick 0 bills a process that arrived at tick 3 for three ticks during which it did not exist. It only happens to be right for processes that arrived at 0.",
                            "`clock` is wherever the simulation has reached, which for a finished process is at or after its completion — so this would come out at zero or negative for every process.",
                        ],
                    },
                    {
                        "prompt": "Waiting is the part of the turnaround the process did not spend on the processor.",
                        "hole": "?",
                        "opts": ["burst", "arrival", "completion", "quantum"],
                        "a": 0,
                        "why": "Waiting is turnaround minus burst. The burst is the time the process actually held the CPU; subtract it and what remains is time spent queued or preempted, which is the only part a scheduler can improve.",
                        "whys": [
                            "Waiting is turnaround minus burst. The burst is the time the process actually held the CPU; subtract it and what remains is time spent queued or preempted, which is the only part a scheduler can improve.",
                            "The arrival was already taken out on the line above; taking it out twice subtracts it from a number it is no longer inside.",
                            "Turnaround minus completion is negative for anything that arrived after tick 0, and it is a duration minus an instant — the two are not even the same kind of quantity.",
                            "The quantum is a property of the policy, not of the process. Two processes with different bursts under the same quantum would come out with waiting times differing by the wrong amount.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "What a quantum costs",
                "minutes": 13,
                "vars": ["n", "q", "s"],
                "brief": r"""
Round robin is not free, and the price is paid in a currency the Gantt chart does not
show. Take $n$ runnable processes, all CPU-bound, none of them finishing during the
window we are watching. Each dispatch costs $s$ ticks of context switch and then
delivers $q$ ticks of useful work.

Two numbers fall out of that, and they pull in opposite directions.
""",
                "steps": [
                    {
                        "prompt": "One turn of the wheel gives every process exactly one slice. Counting the switch that precedes each slice, how long is a full cycle?",
                        "answer": "n(q + s)",
                        "hint": "Work out what one dispatch occupies from end to end, then count how many there are in a cycle.",
                        "deconstruct": [
                            "A dispatch is $s$ ticks of switching followed by $q$ ticks of work, so it occupies $q + s$ ticks.",
                            "A cycle contains one dispatch per process, and there are $n$ processes.",
                        ],
                    },
                    {
                        "prompt": "Of that cycle, how much was work the processes actually asked for? Write the fraction.",
                        "answer": "\\frac{q}{q + s}",
                        "hint": "Useful ticks per cycle over total ticks per cycle. Something cancels.",
                        "deconstruct": [
                            "A cycle lasts $n(q+s)$ and contains $nq$ ticks of user work.",
                            "$nq / (n(q+s))$ cancels to a ratio with no $n$ in it at all — the efficiency does not care how many processes there are.",
                        ],
                    },
                    {
                        "prompt": "Set the switch cost aside for a moment. A process has just used its whole slice and gone to the back of the queue. How long before it runs again?",
                        "answer": "(n - 1)q",
                        "hint": "Count who is ahead of it, and what each of them takes.",
                        "deconstruct": [
                            "There are $n - 1$ other processes in front of it in the queue.",
                            "Each of them uses a full quantum before the queue comes round again.",
                        ],
                    },
                    {
                        "prompt": "Now put the overhead back. What quantum makes exactly nine ticks in every ten useful? Write $q$ in terms of $s$.",
                        "answer": "9s",
                        "hint": "Set the efficiency you derived equal to $9/10$ and clear the denominator.",
                        "deconstruct": [
                            "$\\frac{q}{q+s} = \\frac{9}{10}$ multiplies out to $10q = 9q + 9s$.",
                            "One $q$ cancels from each side, and what is left is $q$ written in units of $s$.",
                        ],
                    },
                ],
                "closing": r"""
Those two results are the whole design problem, and they disagree. Efficiency wants a
large $q$ — at $q = 9s$ you are still spending a tenth of the machine on switching, and
getting that down to a hundredth costs $q = 99s$. Responsiveness wants a small one,
because $(n-1)q$ is how long an interactive process waits between slices, and it grows
with the load. A fixed quantum has to be wrong at one end or the other, which is why
modern schedulers stopped using one: they pick a target latency for the whole cycle
and divide it among however many processes are runnable, with a floor so that the
slice never shrinks to the point where $q$ is comparable to $s$.
""",
            },
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
            "quiz": {
                "title": "Faults, victims, and what a fault costs",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A running instruction touches a page that is not resident. What happens next?",
                        "opts": [
                            "The hardware traps to the kernel, the kernel fetches the page into a frame, and the faulting instruction is restarted from the beginning",
                            "The process is terminated: a reference to a non-resident page is a segmentation fault",
                            "The kernel supplies zeroes for the missing page so the instruction can finish, and fetches the real contents later",
                            "The instruction is skipped and execution continues while the page arrives in the background",
                        ],
                        "a": 0,
                        "why": r"""
A page fault is a trap, not an error — the same mechanism as a system call, raised by
the MMU instead of by an instruction. The kernel finds a frame, possibly evicting
something to get one, schedules the disk read, blocks the process, and when the page
lands it *restarts the faulting instruction*. Restarting rather than resuming is what
makes the whole scheme invisible to the program, and it is also the constraint that
shapes instruction sets: an instruction that has already modified memory or a register
before it faults cannot simply be re-run, which is why architectures with auto-increment
addressing need extra hardware to undo the increment. A segmentation fault is the
different case where the address is not in any valid mapping at all.
""",
                    },
                    {
                        "q": "Why can OPT not be used as a real replacement policy?",
                        "opts": [
                            "It needs the rest of the reference string, which only exists after the program has run",
                            "It needs more bookkeeping per frame than page-table hardware can supply",
                            "It is only correct for reference strings in which no page repeats",
                            "It can be implemented, but it faults more often than LRU",
                        ],
                        "a": 0,
                        "why": r"""
OPT evicts the resident page whose next use is furthest in the future, and the future
is exactly what a running kernel does not have. Its value is as a yardstick: run it
offline over a recorded trace and it gives the fewest faults any policy could possibly
have achieved on that trace, so the gap between LRU and OPT tells you how much is left
to win. LRU is the practical approximation, and it is the mirror image — the past
instead of the future — which works because references cluster in time. The bookkeeping
objection is real for LRU (exact LRU needs a timestamp or a stack update on *every*
reference, which is why hardware offers a reference bit and software approximates), but
it is not what rules OPT out.
""",
                    },
                    {
                        "q": "Giving a policy one more frame makes it fault more often. Which policy can do that?",
                        "opts": ["FIFO", "LRU", "OPT", "Any of the three, on the right reference string"],
                        "a": 0,
                        "why": r"""
This is Belady's anomaly, and the classic string in the lab shows it: FIFO faults nine
times with three frames and ten times with four. LRU and OPT cannot do it because they
are stack algorithms — the pages resident with $m$ frames are always a subset of those
resident with $m+1$, so a reference that hits with $m$ frames hits with $m+1$ too, and
the fault curve can only go down. FIFO breaks the subset property because its victim
choice ignores what is resident and looks only at load order, and load order changes
when the memory size changes.
""",
                    },
                    {
                        "q": "What makes a replacement policy a stack algorithm?",
                        "opts": [
                            "On any reference string, the pages resident with $m$ frames are always a subset of the pages resident with $m+1$ frames",
                            "It is implemented with a stack rather than a queue",
                            "It always evicts the most recently used page",
                            "Its fault count is the same for every memory size",
                        ],
                        "a": 0,
                        "why": r"""
The subset property is the definition, and everything else follows from it. If the
smaller memory's resident set is always contained in the larger one's, then every hit
in the small memory is a hit in the large one, so faults can never increase with
frames — the anomaly is ruled out by construction rather than by luck. It also means
one pass over the reference string can produce the fault count for every memory size at
once, which is how replacement policies are compared in practice. The name comes from
the fact that the resident set can be read off the top $m$ entries of a single ordered
list; it says nothing about the data structure anyone actually implements it with.
""",
                    },
                    {
                        "q": "A system is thrashing. Which observation actually says so?",
                        "opts": [
                            "The page-fault rate is high and climbing while the processes make almost no forward progress",
                            "CPU utilisation is low, so there is room to admit more processes",
                            "Every process's resident set is larger than its working set",
                            "The free-frame list is empty",
                        ],
                        "a": 0,
                        "why": r"""
Thrashing is the state where processes spend more time faulting than running, and the
fault rate is the direct measurement of it. Low CPU utilisation is the trap: a scheduler
that reads it as spare capacity and raises the degree of multiprogramming gives every
process fewer frames, pushes more of them below their working set, and drives the fault
rate higher still — utilisation collapses precisely because the processor is idle
waiting on the disk. A resident set larger than the working set is the healthy case, and
an empty free list is normal on any system that has been up for a while, since unused
memory is wasted memory.
""",
                    },
                    {
                        "q": "With 4 KiB pages, which part of a virtual address does the page table have nothing to do with?",
                        "opts": [
                            "The low 12 bits — the offset is copied to the physical address untouched",
                            "The low 10 bits",
                            "The high 20 bits",
                            "None of it: the whole address goes through the table",
                        ],
                        "a": 0,
                        "why": r"""
A 4 KiB page is $2^{12}$ bytes, so 12 bits are needed to name a byte within one, and
those 12 bits mean the same thing in both address spaces — byte 2748 of a page is byte
2748 of the frame that holds it. Only the bits above them, the page number, are looked
up and replaced by a frame number. That is also why page sizes are powers of two:
translation is then a shift and a concatenation rather than a division, and can be done
in hardware in the time it takes to read the table entry.
""",
                    },
                ],
            },
            "blanks": {
                "title": "One address, translated",
                "minutes": 8,
                "caption": "a 32-bit virtual address on a system with 4 KiB pages",
                "lang": "text",
                "brief": r"""
Paging is one shift and one table lookup, and almost every confusion about it comes
from losing track of which bits are which. Work this single address through and the
rest of the module is bookkeeping.

Every number here is hexadecimal unless it says otherwise, and each hex digit is four
bits.
""",
                "listing": r'''
page size        = 4 KiB = 2^12 bytes
virtual address  = 0x00003ABC

offset           = the low ___ bits of the address    ->  0xABC
virtual page no  = address >> 12                      ->  page ___
frame no         = page_table[page no]                ->  0x0025
physical address = (frame << 12) | offset             ->  0x0025___

one table entry per page, so a 32-bit address space
with 4 KiB pages needs 2^___ page-table entries
''',
                "blanks": [
                    {
                        "prompt": "How many bits does it take to name a byte inside one page?",
                        "hole": "?",
                        "opts": ["12", "10", "16", "20"],
                        "a": 0,
                        "why": "4 KiB is $2^{12}$ bytes, so 12 bits address every byte in a page — and `0xABC` is exactly three hex digits, which is twelve bits. Page size and offset width are the same fact said twice.",
                        "whys": [
                            "4 KiB is $2^{12}$ bytes, so 12 bits address every byte in a page — and `0xABC` is exactly three hex digits, which is twelve bits. Page size and offset width are the same fact said twice.",
                            "10 bits would be a 1 KiB page. It is the right number for a two-level table's index fields on a 32-bit machine, which is probably where the memory of it comes from, but it is not the offset here.",
                            "16 bits is a 64 KiB page, and it would leave `0xABC` short of the four hex digits it would then need.",
                            "20 is the width of the page *number* on a 32-bit machine with these pages — the bits above the offset, not the offset itself.",
                        ],
                    },
                    {
                        "prompt": "Shifting right by 12 throws the offset away. What is left?",
                        "hole": "?",
                        "opts": ["3", "4", "0x3ABC", "0xABC"],
                        "a": 0,
                        "why": "A shift of 12 bits is a shift of three hex digits, so `0x00003ABC >> 12` drops `ABC` and leaves `0x3`. The reference is to page 3, at byte 2748 within it.",
                        "whys": [
                            "A shift of 12 bits is a shift of three hex digits, so `0x00003ABC >> 12` drops `ABC` and leaves `0x3`. The reference is to page 3, at byte 2748 within it.",
                            "Rounding up. `0x3ABC` is 15036, and $15036 / 4096 = 3.67$ — the page containing it is page 3, not page 4. The fractional part is the offset, and dividing throws it away rather than rounding by it.",
                            "That is the address with only its leading zeroes removed; nothing has been shifted. Keeping the offset digits in the page number is the single commonest slip here.",
                            "`0xABC` is the offset — the part that was shifted out, not the part that survived.",
                        ],
                    },
                    {
                        "prompt": "The table has handed back frame 0x0025. What are the low three digits of the physical address?",
                        "hole": "?",
                        "opts": ["ABC", "3ABC", "0025", "0000"],
                        "a": 0,
                        "why": "The offset is carried across untouched, so the low three hex digits of the physical address are the low three of the virtual one. Only the page number was replaced.",
                        "whys": [
                            "The offset is carried across untouched, so the low three hex digits of the physical address are the low three of the virtual one. Only the page number was replaced.",
                            "That carries the virtual page digit across as well: the address becomes `0x00253ABC`, whose frame number now reads `0x253` instead of the `0x25` the table handed back. The reference lands 558 frames past the one it belongs in. The page number is precisely the part translation replaces, so it is the part that must not survive.",
                            "Repeating the frame number in the low digits translates the offset as well, and there is nothing in the table that could tell you what to translate it to.",
                            "Zeroing the offset points at the first byte of the frame, whatever byte was asked for. Every reference to a page would then return the same byte.",
                        ],
                    },
                    {
                        "prompt": "One entry per page. How many entries does a 32-bit address space need?",
                        "hole": "?",
                        "opts": ["20", "12", "32", "10"],
                        "a": 0,
                        "why": "32 bits of address minus 12 bits of offset leaves a 20-bit page number, so the table is indexed 0 to $2^{20}-1$: about a million entries, and at four bytes each that is 4 MiB of page table for every process. That number is the entire argument for multi-level tables.",
                        "whys": [
                            "32 bits of address minus 12 bits of offset leaves a 20-bit page number, so the table is indexed 0 to $2^{20}-1$: about a million entries, and at four bytes each that is 4 MiB of page table for every process. That number is the entire argument for multi-level tables.",
                            "$2^{12}$ is the page size in bytes, not the number of pages. It would be the answer for a 24-bit address space.",
                            "$2^{32}$ is one entry per *byte* of address space, which is a table four billion entries long describing four billion single-byte pages — the offset bits have not been taken out.",
                            "$2^{10}$ is the number of entries in one level of a classic two-level 32-bit table, where the 20-bit page number is split 10 and 10. It is a real number in this design, but it is not the total.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "What one fault in a thousand costs",
                "minutes": 8,
                "brief": r"""
A memory reference has two possible fates. Almost always the page is resident and the
reference costs one memory access. Occasionally it is not, and the cost is a disk read
— five orders of magnitude worse. The effective access time is the average over both,
weighted by how often each one happens:

$$\mathrm{EAT} = (1 - p)\,t_{mem} + p\,t_{fault}$$

Work it out for the numbers on the right. The two terms are quoted in different units,
which is where most of the wrong answers come from.
""",
                "prompt": "What is the effective access time?",
                "note": "Answer in nanoseconds, to one decimal place.",
                "figure": r"$\mathrm{EAT} = (1-p)\,t_{mem} + p\,t_{fault}$ — one reference, two fates, averaged by how often each one happens.",
                "given": [
                    {"label": "Memory access $t_{mem}$", "value": "100 ns"},
                    {"label": "Fault service $t_{fault}$", "value": "8 ms"},
                    {"label": "Fault rate $p$", "value": "0.001"},
                    {"label": "Wanted", "value": "EAT in ns"},
                ],
                "aside": "One reference in a thousand faults. That sounds like a rounding error and is not.",
                "answer": 8099.9,
                "tol": 0.05,
                "unit": "ns",
                "hint": "Convert the service time to nanoseconds before you weight anything: $8\\ \\mathrm{ms} = 8 \\times 10^{6}\\ \\mathrm{ns}$. Then 999 references in a thousand cost 100 ns each and one costs $8 \\times 10^{6}$.",
                "wrong": "Two slips account for nearly all of these: leaving the service time in milliseconds, so the second term comes out a million times too small, and dropping the $(1-p)$ weight on the first. Check both terms are in nanoseconds before adding them.",
                "why": r"""
$0.999 \times 100 + 0.001 \times 8000000 = 99.9 + 8000 = 8099.9$ ns. Memory that looks
like 100 ns behaves like 8.1 µs — a slowdown of 81 times — and notice how lopsided the
sum is: the resident term contributes 99.9 ns out of 8099.9, so the answer is almost
entirely the faults. Turn the arithmetic round and it tells you what fault rate you can
afford: holding the slowdown under 10% needs $p$ below about $1.25 \times 10^{-6}$, or
roughly one fault per million references. That gap, between one in a thousand and one
in a million, is the whole reason the working-set model exists.
""",
            },
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
            "quiz": {
                "title": "Interleavings, semaphores and safety",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is a race condition a property of?",
                        "opts": [
                            "The set of possible interleavings: at least one of them produces a wrong result",
                            "A particular run, and it is visible in that run's trace",
                            "Heavy load, which is when two threads finally collide",
                            "Multi-core hardware, where two threads genuinely execute at the same instant",
                        ],
                        "a": 0,
                        "why": r"""
This is why the lab makes you choose the interleaving by hand. A test that passes has
demonstrated that one schedule out of an enormous set behaves; it says nothing about
the others, and the others are where the bug lives. Load and core count change the
*probability* that a bad interleaving is chosen, which is why races surface in
production and not in testing, but they do not create or remove one — a race on a
single core with a preemptive kernel is exactly as real, it just needs the timer to
fire in the wrong microsecond.
""",
                    },
                    {
                        "q": "In a counting semaphore, which operation can block?",
                        "opts": [
                            "`wait` blocks when the counter is zero; `signal` never blocks",
                            "Both: `signal` blocks once the counter reaches its initial value",
                            "`signal` blocks while another thread is inside `wait`",
                            "Neither: a semaphore only counts, and the blocking is the scheduler's business",
                        ],
                        "a": 0,
                        "why": r"""
`wait` is the only operation that can fail to proceed, and the asymmetry is deliberate.
A `signal` that could block would be a resource in its own right and would need its own
semaphore to protect it, and that regress is the reason the primitive is defined this
way. In the simulator the asymmetry shows up as `try_step` returning `False` for a
`wait` on zero *without decrementing* — a blocked wait must consume nothing, or the
counter drifts below the number of resources that actually exist and the invariant the
whole structure rests on is gone.
""",
                    },
                    {
                        "q": "A producer takes the mutex and then waits on `empty`. The buffer is full. What follows?",
                        "opts": [
                            "The producer sleeps holding the mutex, so no consumer can get in to remove anything, so no slot is ever freed",
                            "Nothing: the mutex guards the buffer, and a consumer removing an item does not need it",
                            "The kernel spots the cycle and rolls one of the two back",
                            "It deadlocks only when the buffer has capacity 1",
                        ],
                        "a": 0,
                        "why": r"""
The consumer gets past `wait(full)` — there is plenty in the buffer — and then stops
dead at `wait(mutex)`, which the sleeping producer is holding. The producer is waiting
for a slot that only the consumer can free, and the consumer is waiting for a lock that
only the producer can release: hold-and-wait plus circular wait, in five lines. Capacity
makes no difference beyond delaying it, since the producer only has to run ahead by
more items than the buffer holds. And nothing rolls it back — a general-purpose kernel
does not track which lock is protecting what, so the two threads simply stay asleep.
""",
                    },
                    {
                        "q": "\"Request everything you will need in one go, or nothing at all.\" Which of Coffman's conditions does that remove?",
                        "opts": ["Hold and wait", "Mutual exclusion", "No preemption", "Circular wait"],
                        "a": 0,
                        "why": r"""
A process that never holds one resource while asking for another cannot be a link in a
waiting chain, so the chain cannot form. The cost is why nobody does it: you have to
declare everything up front and hold it for the whole run, so utilisation collapses and
a process that needs a rarely-contended resource for one second at the end holds it from
the start. The other three are attacked differently — mutual exclusion mostly cannot be
attacked at all (a printer is not shareable), no-preemption is attacked by taking
resources back by force and rolling the victim back, and circular wait is attacked by
numbering the resource types and requiring requests in increasing order, which is the
one that is actually cheap enough to use.
""",
                    },
                    {
                        "q": "The banker's algorithm reports that a state is safe. What has it established?",
                        "opts": [
                            "There is at least one order in which all the processes can be run to completion using only the resources on hand",
                            "No process will have to wait for a resource from here on",
                            "Every order in which the processes might run completes",
                            "The system is deadlocked but can still be recovered",
                        ],
                        "a": 0,
                        "why": r"""
Safety is an existence claim, and the safety check is a constructive proof of it: find
a process whose remaining need fits the free pool, pretend it runs and returns
everything, and repeat. Producing one such sequence is enough, because the operating
system controls the granting order and can therefore *impose* it if it has to.
Processes still wait; they just never wait forever. The mirror image is worth keeping
straight too — an unsafe state is not a deadlocked one. It only means the guarantee has
been lost, and a run through an unsafe state may well complete if the processes turn
out not to claim their declared maximums.
""",
                    },
                    {
                        "q": "Mutual exclusion, progress, bounded waiting. Which one fails if a process sitting outside its critical section can stop another from entering?",
                        "opts": ["Progress", "Mutual exclusion", "Bounded waiting", "None: that is what a lock is for"],
                        "a": 0,
                        "why": r"""
Progress says that the decision about who enters next is taken only among the processes
that actually want to enter, and that it cannot be postponed indefinitely. A process
that is not competing must not get a vote — the classic strict-alternation solution
fails exactly here, because it insists on turns and a process that never wants another
turn blocks its partner forever. Mutual exclusion is the different requirement that two
processes are never inside at once, and bounded waiting caps how many times others may
overtake you once you have declared an interest, which is what keeps a correct lock from
starving somebody.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The bounded buffer, semaphore by semaphore",
                "minutes": 9,
                "caption": "three semaphores, two programs, and only one order that works",
                "lang": "python",
                "brief": r"""
The bounded-buffer solution is short enough to memorise and easy enough to get subtly
wrong that it is worth reconstructing rather than recalling. Two of the three
semaphores count things — free slots and filled slots — and the third is a plain lock.
Fill the holes and read the two programs back as mirror images of each other.
""",
                "listing": r'''
sem = {"empty": ___, "full": 0, "mutex": 1}

# producer, once per item
wait(___)               # claim a free slot before touching the lock
wait("mutex")
buffer.append(item)
signal("mutex")
signal(___)             # a consumer may now take it

# consumer, once per item
wait("full")
wait("mutex")
item = buffer.pop(0)
signal("mutex")
signal(___)             # the slot is free again
''',
                "blanks": [
                    {
                        "prompt": "How many free slots does an empty buffer have?",
                        "hole": "?",
                        "opts": ["capacity", "0", "1", "len(buffer)"],
                        "a": 0,
                        "why": "`empty` counts free slots, and an empty buffer has every one of them free. That is also the invariant to hold on to: between operations, `empty` plus `full` is the capacity.",
                        "whys": [
                            "`empty` counts free slots, and an empty buffer has every one of them free. That is also the invariant to hold on to: between operations, `empty` plus `full` is the capacity.",
                            "Starting at zero says there is nowhere to put anything. The first producer blocks immediately and nothing ever runs — and since only a consumer raises `empty`, and consumers need something to consume, it never recovers.",
                            "One free slot regardless of the real capacity. Correct but crippled: the producer can never run more than one item ahead, so a buffer of any size behaves as a buffer of one and the two threads lock-step.",
                            "That is zero at this point, and worse, it is a snapshot. The semaphore is what tracks the count from here on; seeding it from the buffer length just spells zero the long way round.",
                        ],
                    },
                    {
                        "prompt": "Which semaphore does the producer wait on first?",
                        "hole": "?",
                        "opts": ['"empty"', '"full"', '"mutex"', '"capacity"'],
                        "a": 0,
                        "why": "Secure the resource, then take the lock. Waiting for a free slot first means that if the producer does sleep, it sleeps holding nothing, and a consumer can still get in and free one.",
                        "whys": [
                            "Secure the resource, then take the lock. Waiting for a free slot first means that if the producer does sleep, it sleeps holding nothing, and a consumer can still get in and free one.",
                            "`full` counts items waiting to be consumed. A producer waiting on it would block precisely when the buffer is empty, which is the moment it is most needed.",
                            "This is the deadlock the module is built around. There is nothing wrong with the line itself — it is wrong *here*, before the slot it is about to write into has been secured.",
                            "There is no semaphore by that name. Capacity is a constant fixed when the buffer is created; `empty` is the running count of how much of it is unused.",
                        ],
                    },
                    {
                        "prompt": "The item is in and the lock is back. What does the producer announce?",
                        "hole": "?",
                        "opts": ['"full"', '"empty"', '"mutex"', '"item"'],
                        "a": 0,
                        "why": "`full` counts items available to consume, so producing one raises it and releases a consumer blocked in `wait(\"full\")`. Every `wait(\"empty\")` on this side is paid for by a `signal(\"full\")`.",
                        "whys": [
                            "`full` counts items available to consume, so producing one raises it and releases a consumer blocked in `wait(\"full\")`. Every `wait(\"empty\")` on this side is paid for by a `signal(\"full\")`.",
                            "That claims a slot was freed by the act of filling it. `empty` would return to the capacity while the buffer fills, the producer would sail past the bound, and the simulator would raise the overflow this whole structure exists to prevent.",
                            "The mutex has already been signalled on the line above. Signalling it twice pushes the counter to 2 and the lock stops excluding anybody — two threads can then be inside the critical section at once.",
                            "There is no `item` semaphore. The item went into the buffer; what is being announced is that the *count* of available items went up.",
                        ],
                    },
                    {
                        "prompt": "And what does the consumer announce, having taken an item out?",
                        "hole": "?",
                        "opts": ['"empty"', '"full"', '"mutex"', '"done"'],
                        "a": 0,
                        "why": "Removing an item frees a slot, so `empty` goes up and a producer blocked on it is released. The two programs are mirror images: each waits on the counter it consumes and signals the counter it produces.",
                        "whys": [
                            "Removing an item frees a slot, so `empty` goes up and a producer blocked on it is released. The two programs are mirror images: each waits on the counter it consumes and signals the counter it produces.",
                            "The consumer already spent one `full` getting in. Signalling it again puts the item back as far as the counter is concerned, and the count of available items climbs forever while the buffer stays empty — until a consumer passes `wait(\"full\")` and finds nothing there.",
                            "Already released on the line above. A second signal breaks mutual exclusion.",
                            "Nothing waits on a `done` semaphore in this design, so signalling it releases nobody and the producer stays blocked with the buffer full.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "How many units make deadlock impossible",
                "minutes": 13,
                "vars": ["n", "m", "R"],
                "brief": r"""
The banker's algorithm decides one request at a time. This is the other approach: buy
enough hardware that the question never arises, and prove it by counting.

One resource type, $R$ identical units, $n$ processes. Each process needs at most $m$
units to finish, and asks for them one at a time, keeping whatever it has already been
given until it is done.
""",
                "steps": [
                    {
                        "prompt": "A process that has been given $m$ units has everything it will ever ask for and can run to completion. So what is the most a *blocked* process can be holding?",
                        "answer": "m - 1",
                        "hint": "One short of its maximum. If it held the last one it would not be blocked.",
                        "deconstruct": [
                            "A process is blocked only while it is still waiting for something it does not have.",
                            "Needing at least one more out of a maximum of $m$ leaves it holding at most $m - 1$.",
                        ],
                    },
                    {
                        "prompt": "A deadlock needs every one of the $n$ processes blocked at once. Add up what they are holding — how large can that total be?",
                        "answer": "n(m - 1)",
                        "hint": "Every process, each at its own worst case.",
                        "deconstruct": [
                            "Each of the $n$ processes is blocked, so each holds at most $m - 1$ units.",
                            "The worst case is all of them at that bound simultaneously.",
                        ],
                    },
                    {
                        "prompt": "In a deadlock nothing is left free — a spare unit would satisfy somebody's one-unit request. So all $R$ units are held. Write the smallest $R$ for which no deadlock can exist.",
                        "answer": "n(m - 1) + 1",
                        "hint": "A deadlock needs all $R$ units to fit inside the total you just bounded. Make $R$ one too large to fit.",
                        "deconstruct": [
                            "A deadlock requires $R \\le n(m-1)$: every unit held, and nobody holding as many as $m$.",
                            "One unit beyond that and the allocation cannot exist — by the pigeonhole principle somebody must hold $m$ units, and that process can finish and give them all back.",
                        ],
                    },
                    {
                        "prompt": "Five processes, each needing at most three units. How many units guarantee the system is deadlock-free?",
                        "answer": "11",
                        "hint": "Substitute $n = 5$ and $m = 3$ into what you just derived.",
                        "deconstruct": [
                            "$n(m-1) = 5 \\times 2 = 10$ units can be shared out as two each, with every process still wanting a third — that is a deadlock.",
                            "The eleventh unit has nowhere to hide: wherever it goes, somebody now holds three.",
                        ],
                    },
                ],
                "closing": r"""
Notice what that bought and what it did not. It is a static guarantee — check it once
when the machine is configured and no run-time test is ever needed again — but it is
crude, because it assumes every process might want its full $m$ at the same moment.
Ten processes that each might want ten units would need 91, and would spend almost all
of their time using a handful. The banker's algorithm trades the static guarantee for
utilisation: it will run you on fewer units than $n(m-1)+1$, and pays for it by testing
every single request against a safe sequence before granting it.
""",
            },
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
            "quiz": {
                "title": "Blocks, inodes, and the space between them",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A 100-byte file on a file system with 4 KiB blocks. What does it occupy, and what is the waste called?",
                        "opts": [
                            "One whole block; the 3996 unused bytes are internal fragmentation",
                            "100 bytes; the allocator hands out exactly what was asked for",
                            "One whole block; the unused bytes are external fragmentation",
                            "One whole block, and nothing is wasted, because the block is the unit of allocation",
                        ],
                        "a": 0,
                        "why": r"""
The block is the unit of allocation, which is exactly why the waste exists: nothing
smaller can be handed out, so a 100-byte file gets 4096 bytes and the remaining 3996
belong to it and can be used by nobody. That slack inside an allocated unit is internal
fragmentation. External fragmentation is the opposite arrangement — free space that
belongs to nobody but is scattered in pieces too small or too spread out to satisfy a
request. Averaged over many files it costs half a block each, which is the argument
against large blocks and the reason a file system full of small files can lose a
noticeable fraction of the disk.
""",
                    },
                    {
                        "q": "Contiguous allocation gives the fastest sequential read of the three schemes. What does it cost?",
                        "opts": [
                            "External fragmentation, and a file that cannot grow past the hole it was placed in",
                            "A pointer stored in every block, followed one at a time",
                            "An index block per file, read before any data can be",
                            "Nothing — it is strictly better, which is why extent-based file systems use it",
                        ],
                        "a": 0,
                        "why": r"""
Contiguous allocation is just first-fit or best-fit over the disk, and it inherits
every problem those have. Files are created and deleted, the free space breaks into
holes, and eventually there is plenty free but no single run big enough — which is
external fragmentation, curable only by compaction that has to move real data. Worse,
the size has to be known when the file is created, because growing means finding a
larger hole and copying. The per-block pointer is linked allocation's cost and the
index block is indexed allocation's; modern file systems keep the good part by
allocating *extents* — runs of contiguous blocks, several per file — which is a
compromise rather than a free lunch.
""",
                    },
                    {
                        "q": "Linked allocation stores the next block number inside each block. Which operation does that make expensive?",
                        "opts": [
                            "Reading byte 100000 of a file, because every earlier block has to be fetched to find out where the next one is",
                            "Appending, because every block has to be rewritten",
                            "Deleting, because the blocks are scattered",
                            "Growing, because the blocks must stay adjacent",
                        ],
                        "a": 0,
                        "why": r"""
Random access is what it destroys. The location of block $k$ is only discoverable by
reading blocks 0 through $k-1$, so a seek into the middle of a large file costs one
disk read per block skipped — and each of those reads is a genuine I/O, not a
calculation. Appending is cheap if the inode keeps a tail pointer, deletion is a walk
of the chain, and growing is trivially easy since the next block can be anywhere at
all. That is the whole trade: linked allocation solves the growth problem that
contiguous allocation has and gives up the thing contiguous allocation was best at.
""",
                    },
                    {
                        "q": "Free-space management: a bitmap of one bit per block, against a linked free list.",
                        "opts": [
                            "The bitmap makes finding a run of consecutive free blocks straightforward; the free list makes it hard",
                            "The free list occupies a fixed amount of space no matter how full the disk is",
                            "The bitmap has to be scanned linearly to free a block",
                            "Neither can answer \"is block 4712 free?\" without a scan",
                        ],
                        "a": 0,
                        "why": r"""
The bitmap's strength is that adjacency in the disk is adjacency in the structure: a
run of free blocks is a run of zero bits, and it can be found a machine word at a time.
Freeing block 4712 is clearing bit 4712, and asking whether it is free is reading bit
4712 — both constant time. Its cost is that it is proportional to the size of the disk
whether the disk is empty or full, which is the fixed-size structure here, not the free
list. The free list is the other way round: it shrinks as the disk fills, it hands out
a block in constant time, and it has no idea whether the block it just handed out is
next to anything.
""",
                    },
                    {
                        "q": "The lab's `append` checks the free list can cover the whole write before it writes a single byte. Why that order?",
                        "opts": [
                            "So a write that will not fit leaves the file and the free list exactly as they were, rather than half-written with blocks already taken",
                            "Because the free list cannot be modified while a file is open",
                            "Because counting the blocks is faster than allocating them",
                            "It makes no difference: the exception undoes the allocations on its way out",
                        ],
                        "a": 0,
                        "why": r"""
Raising an exception from the middle of a loop leaves everything the loop already did
still done — the blocks popped off the free list are gone, the inode lists them, and
the file contains a prefix of a write that officially failed. Nothing unwinds that for
you. Computing the requirement first and failing before the first mutation is the
cheapest form of atomicity there is, and it is the same discipline a real file system
applies with rather more machinery: reserve the space, then journal the intent, then
write.
""",
                    },
                    {
                        "q": "Two files are appended to alternately on a freshly formatted disk. What becomes of their blocks?",
                        "opts": [
                            "They interleave, so neither file is contiguous and a sequential read of either seeks back and forth",
                            "The allocator reserves a contiguous run for each file when it is created",
                            "The second file's blocks all follow the first file's, because the free list is kept sorted",
                            "Nothing worth measuring: block numbers do not affect the cost of a read",
                        ],
                        "a": 0,
                        "why": r"""
The free list is sorted and the allocator takes the lowest number, so alternating
writers get alternating blocks: one file ends up holding 0 and 2, the other 1 and 3.
Both files are correct and both are fragmented, and no single decision was wrong — the
fragmentation is an emergent property of the interleaving, which is why it cannot be
fixed by being cleverer about any one allocation. On rotating media that turns one
streaming read into alternating seeks, and it is the reason for delayed allocation and
for defragmentation. On flash the seek is nearly free, which is why the whole concern
quietened down rather than disappearing.
""",
                    },
                ],
            },
            "blanks": {
                "title": "append, before it writes anything",
                "minutes": 9,
                "caption": "the arithmetic that has to happen before a single byte moves",
                "lang": "python",
                "brief": r"""
`append` does its thinking first and its writing second, and that order is the whole
reason a full disk leaves no wreckage behind. Fill the holes in the cost calculation,
in the allocation policy, and in the one line of `delete` that keeps the policy
meaningful.
""",
                "listing": r'''
# FileSystem.append — settle the whole cost before touching a byte

slack    = len(inode["blocks"]) * self.block_size - inode[___]
overflow = max(0, len(data) - slack)
needed   = -(-overflow // ___)          # ceiling division, no import
if needed > len(self.free):
    raise OSError("no space left on device")

position = inode["size"]
for char in data:
    index = position // self.block_size
    if index >= len(inode["blocks"]):
        inode["blocks"].append(self.free.pop(___))
    self.blocks[inode["blocks"][index]] += char
    position += 1
inode["size"] = position

# and in delete, so the next allocation still finds the lowest number first
___
''',
                "blanks": [
                    {
                        "prompt": "The file already owns some blocks. How much of them is actually in use?",
                        "hole": "?",
                        "opts": ['"size"', '"blocks"', '"name"', '"nblocks"'],
                        "a": 0,
                        "why": "The blocks the file holds are worth `len(blocks) * block_size` bytes and `size` of them are occupied, so the difference is the slack in the last block. Both terms have to be in bytes for the subtraction to mean anything.",
                        "whys": [
                            "The blocks the file holds are worth `len(blocks) * block_size` bytes and `size` of them are occupied, so the difference is the slack in the last block. Both terms have to be in bytes for the subtraction to mean anything.",
                            "`inode[\"blocks\"]` is the list of block numbers. Subtracting a list from an integer is a `TypeError`, and even read charitably it sets a block count against a byte count.",
                            "The name is a string and says nothing about how full the last block is.",
                            "There is no such key on an inode. `nblocks` is a property of the whole disk, which is a different object with a different lifetime.",
                        ],
                    },
                    {
                        "prompt": "The overflow is in bytes and the answer wanted is in blocks.",
                        "hole": "?",
                        "opts": ["self.block_size", "self.nblocks", "len(data)", "slack"],
                        "a": 0,
                        "why": "Dividing bytes by the bytes-per-block gives blocks. `-(-x // b)` is `ceil(x / b)` spelled with floor division: negate, floor toward minus infinity, negate back — 9 bytes over 8-byte blocks comes out as 2 rather than 1.",
                        "whys": [
                            "Dividing bytes by the bytes-per-block gives blocks. `-(-x // b)` is `ceil(x / b)` spelled with floor division: negate, floor toward minus infinity, negate back — 9 bytes over 8-byte blocks comes out as 2 rather than 1.",
                            "That is how many blocks the disk has, not how many bytes one holds. The result would be a number in neither unit, and on a small disk it would demand absurdly many blocks.",
                            "The write size is already the numerator here, by way of the overflow. Dividing by it yields a fraction near one, never a block count.",
                            "Slack is routinely zero — a file whose size is an exact multiple of the block size has none at all — so this divides by zero on the commonest case in the tests.",
                        ],
                    },
                    {
                        "prompt": "The free list is kept sorted. Which end does a new block come from?",
                        "hole": "?",
                        "opts": ["0", "-1", "len(self.free)", "index"],
                        "a": 0,
                        "why": "`pop(0)` takes the head, which in a sorted list is the lowest-numbered free block. That is the policy the tests pin down: delete a file in the middle of the disk and the next allocation reuses its blocks before touching anything further out.",
                        "whys": [
                            "`pop(0)` takes the head, which in a sorted list is the lowest-numbered free block. That is the policy the tests pin down: delete a file in the middle of the disk and the next allocation reuses its blocks before touching anything further out.",
                            "`pop(-1)` takes the highest-numbered free block, so files march backwards from the end of the disk and a hole freed in the middle is the last thing ever reused.",
                            "That index is one past the end of the list, so `pop` raises `IndexError` every time — including on the very first allocation.",
                            "`index` is a position within the *file*, not within the free list. It goes out of range as soon as the file is longer than the free list is, and until then it picks essentially at random.",
                        ],
                    },
                    {
                        "prompt": "`delete` has a block number in hand and has to put it back.",
                        "hole": "?",
                        "opts": [
                            "bisect.insort(self.free, block)",
                            "self.free.append(block)",
                            "self.free.insert(0, block)",
                            "self.free.remove(block)",
                        ],
                        "a": 0,
                        "why": "`insort` finds the position by binary search and inserts there, so the list is still ascending afterwards — which is the precondition the `pop(0)` policy relies on. Sorted-ness is not decoration here; it is what makes \"lowest first\" true.",
                        "whys": [
                            "`insort` finds the position by binary search and inserts there, so the list is still ascending afterwards — which is the precondition the `pop(0)` policy relies on. Sorted-ness is not decoration here; it is what makes \"lowest first\" true.",
                            "Appending puts the freed block at the end whatever its number. The list stops being sorted, and from then on `pop(0)` returns whatever happens to be first rather than the lowest — the reuse policy quietly becomes something nobody designed.",
                            "Inserting at the front reuses the freed block next regardless of its number, and leaves the list unsorted for everything after it. It also turns the free list into a stack, which is a defensible policy but not this one.",
                            "`remove` takes a block *out* of the free list — the exact opposite of freeing it. The block is lost to the file system forever and the disk shrinks with every delete.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How much file one inode can address",
                "minutes": 8,
                "brief": r"""
The lab's inode keeps a flat list of every block the file owns, which is fine in memory
and impossible on disk: an inode has to be a fixed size, so it can hold only a fixed
number of pointers. Unix solved it by making most of the pointers indirect. A handful
point straight at data. One points at a block containing nothing but more pointers.
One points at a block of pointers to blocks of pointers.

A block holds $B/p$ pointers, where $B$ is the block size and $p$ is the size of a
pointer. Count the *data* blocks this inode can reach — the pointer blocks themselves
hold no file content.
""",
                "prompt": "How many data blocks in total can this inode address?",
                "note": "Answer in blocks, not bytes.",
                "figure": r"`12 direct -> data` · `1 single indirect -> pointers -> data` · `1 double indirect -> pointers -> pointers -> data`",
                "given": [
                    {"label": "Block size $B$", "value": "4 KiB"},
                    {"label": "Pointer size $p$", "value": "4 bytes"},
                    {"label": "Direct pointers", "value": "12"},
                    {"label": "Single indirect", "value": "1"},
                    {"label": "Double indirect", "value": "1"},
                ],
                "aside": "Twelve pointers cover the small files; two more cover everything else.",
                "answer": 1049612,
                "tol": 0.0,
                "unit": "blocks",
                "hint": "Pointers per block first: $4096 / 4$. The single indirect then reaches that many data blocks, and the double indirect reaches that many squared.",
                "wrong": "Almost every wrong answer here is one of two things: forgetting to square for the double indirect, or counting the pointer blocks as data. Only the 12 direct, the $k$ under the single indirect and the $k^2$ under the double indirect hold file content.",
                "why": r"""
$k = 4096/4 = 1024$ pointers per block, so the total is
$12 + 1024 + 1024^2 = 12 + 1024 + 1048576 = 1049612$ blocks — about 4.0 GiB at 4 KiB
each. What is worth noticing is how lopsided that is. The double indirect supplies
99.9% of the reach and costs one pointer in the inode; the twelve direct pointers cover
only 48 KiB between them. That asymmetry is deliberate and it is a statement about
files, not about disks: most files are small, and for a small file all twelve pointers
are in the inode you have already read, so the data is one disk access away with no
pointer block fetched at all. A byte near the end of a large file costs three.
""",
            },
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
