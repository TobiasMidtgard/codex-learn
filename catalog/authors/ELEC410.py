"""ELEC410 — AI Track: Reinforcement Learning & Search."""

COURSE = {
    "id": "ELEC410",
    "title": "AI Track — Reinforcement Learning & Search",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["ML401"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 140,
    "icon": "✦",
    "summary": (
        "Decision making when the answer is not a formula but a sequence of choices. "
        "You build the classical search engines first — uninformed, informed and "
        "adversarial — then move to Markov decision processes, learn the same "
        "policies from sampled experience instead of a known model, and measure the "
        "price of exploration in regret."
    ),
    "outcomes": [
        "Implement BFS, DFS, uniform-cost and A* against one successor interface and compare node counts",
        "Prove a heuristic admissible and consistent, and explain what each property buys",
        "Write alpha-beta pruning that returns exactly the minimax value at a fraction of the nodes",
        "Solve a Markov decision process by value iteration and by policy iteration, and certify the result",
        "Derive Q-learning and SARSA updates and predict how each behaves near a hazard",
        "Compare exploration rules by cumulative regret rather than by final score",
        "Report an ablation that isolates the effect of each algorithmic choice",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone build (60%).",
    "reading": [
        "Russell & Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. — chapters 3, 5, 16, 17",
        "Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed., MIT Press 2018 — chapters 2-6",
        "Lattimore & Szepesvári, *Bandit Algorithms*, Cambridge University Press 2020 — chapters 4-8",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "State-space search",
            "summary": "One successor interface, four frontier disciplines, four very different node counts.",
            "concepts": [
                "A search problem is a start state, a successor function and a goal test — nothing else",
                "Tree search revisits states; graph search keeps a closed set and pays memory for it",
                "BFS is optimal only when every step costs the same; uniform-cost search drops that condition",
                "Depth-first search trades optimality and completeness for a frontier that is linear in depth",
                "A* orders the frontier by f = g + h; it is optimal when h is admissible, and expands no reopened nodes when h is consistent",
                "Admissible: h(n) never exceeds the true cost to a goal. Consistent: h(n) <= c(n, n') + h(n')",
                "Manhattan distance on the 8-puzzle is admissible because each tile needs at least that many moves and each move shifts one tile by one",
            ],
            "read": [
                {
                    "title": "One interface, four frontiers",
                    "minutes": 12,
                    "body": r'''
Here is a maze three rows high and five wide. `S` is the top-left corner, `G` the
top-right, and there is one wall between them.

```text
S . # . G
. . . . .
. . . . .
```

You can see the answer: step down, walk along the middle row, step up. Six moves.
A program cannot see it. What a program has is a state — a `(row, col)` pair —
and a way of asking which states are one move away. Everything in this module is
built on that one question, asked over and over in a chosen order, and the order
is the whole difference between four algorithms that otherwise share every line.

## The search problem is three things

Before the four searches, pin down what they are searching. A search problem is a
start state, a *successor function* that maps a state to the
`(next_state, action, step_cost)` triples reachable in one move, and a *goal
test*. That is all. Nothing about mazes, tiles or geometry goes into the
algorithm; it all lives behind the successor function. This is why the lab in
this module, *Four searches, one interface*, can run the same `astar` over a maze
of characters and over the 8-puzzle without changing a line: the maze's successor
function returns open neighbours and the puzzle's returns the boards one slide
away, and the search cannot tell which it has been handed.

For the maze above, the successor function of `(1, 1)` returns four triples, in
the order north, east, south, west: `((0, 1), "N", 1)`, `((1, 2), "E", 1)`,
`((2, 1), "S", 1)`, `((1, 0), "W", 1)`. The successor function of `(0, 1)`
returns only two, because north is off the board and east is the wall. The order
is a convention, and it matters more than it looks: two searches that break ties
differently produce different paths of the same cost and different expansion
counts, so the lab fixes the order and the tie rule so that your numbers and its
numbers can be compared.

## The frontier, and what it means to expand

Every search keeps a collection of states it has discovered but not yet looked
inside. Call it the frontier. The loop is the same in every case: take a state
off the frontier, ask whether it is the goal, and if not, ask the successor
function for its neighbours and put the new ones on. Taking a state off and
generating its children is *expanding* it, and the number of expansions is the
cost you will measure, because it counts calls to the successor function — the
only expensive thing a search does.

Two decisions remain, and they are the entire design space. First: which state
comes off the frontier next? Second: what do you do about a state you have seen
before?

The second one first. A maze has cycles: `(1, 1)` leads to `(1, 2)` and `(1, 2)`
leads back. A search that does not remember what it has expanded will walk in
circles, and on the 8-puzzle, where every move can be undone, it will do so
forever. So graph search keeps a *closed set* of expanded states and refuses to
expand one twice. It pays memory for this, one entry per distinct state, and on
the 8-puzzle that is up to 181,440 entries — affordable. On the 15-puzzle the
state count is $16!/2 \approx 10^{13}$, and no closed set fits. That is where
graph search stops and other techniques begin; for this module, everything fits.

## Four ways to pick the next state

**Breadth-first** takes the state that has been waiting longest — a FIFO queue.
Because every state on the frontier was discovered by expanding a state one step
shallower, the frontier is always sorted by depth, and the first time the goal
comes off it, no shallower goal exists. That makes BFS optimal when every step
costs the same, and only then: if one step cost 100 and a detour of three steps
cost 3, BFS would return the 100-cost path first, because it counts steps rather
than cost.

**Uniform-cost search** repairs this by taking the state with the smallest path
cost so far, written $g(n)$. The frontier becomes a priority queue keyed on $g$.
Now the order is by cost, not depth, and when the goal is expanded no cheaper
path to it can exist, whatever the step costs — provided every step cost is
positive, so that a longer path is never cheaper than a shorter prefix of it.

**Depth-first** takes the state discovered most recently — a stack. It dives. On
a maze it can find a path with very few expansions if it happens to dive the
right way, and it uses memory proportional to the depth rather than to the width
of the tree. In exchange it gives up optimality: the first path it finds is
whatever its diving order stumbled on. In the lab it finds a path of cost more
than 18 on a maze whose optimum is 18, and it does so in fewer expansions than
BFS, which is the trade written down as a number.

**A\*** is uniform-cost search with foresight. Take the frontier ordered by $g$
and add an estimate of what is still to come: $f(n) = g(n) + h(n)$, where $h(n)$
is a *heuristic* guess at the cost from $n$ to the goal. If $h$ were the true
remaining cost, $f$ would be the true cost of the best path through $n$, and the
search would walk straight to the goal expanding only the states on that path.
Nobody has the true cost — that is what is being searched for — but a guess that
is never too high turns out to be enough.

## Watching A* work

Use the Manhattan distance to the goal as $h$: for the maze above,
$h(r, c) = |r - 0| + |c - 4|$. It ignores the wall, which is what makes it cheap
and also what makes it an underestimate.

Start at `(0, 0)`: $g = 0$, $h = 4$, $f = 4$. Expand it. East gives `(0, 1)` with
$g = 1$, $h = 3$, $f = 4$. South gives `(1, 0)` with $g = 1$, $h = 5$, $f = 6$.
The frontier holds two states and `(0, 1)` has the smaller $f$, so it goes next.
Its east neighbour is the wall; south is `(1, 1)` with $g = 2$, $h = 4$, $f = 6$.
Now the frontier is `(1, 0)` and `(1, 1)`, both at $f = 6$, and the tie goes to
whichever was inserted first: `(1, 0)`. Expanding it finds `(2, 0)` at
$f = 2 + 6 = 8$ and nothing better. Then `(1, 1)`, which finds `(1, 2)` at
$g = 3$, $h = 3$, $f = 6$, and `(2, 1)` at $f = 8$.

Notice what has happened: every state along the bottom row is sitting at
$f = 8$, and the search will not touch them while anything at $f = 6$ remains.
It expands `(1, 2)`, then `(1, 3)` at $f = 4 + 2 = 6$, then `(0, 3)` at
$f = 5 + 1$, then `(1, 4)` at $f = 5 + 1$, and then `(0, 4)` — the goal — at
$f = 6 + 0$. Nine expansions, cost 6. Uniform-cost search on the same maze,
which is A* with $h = 0$ everywhere, expands thirteen: every cell with $g \le 5$
and then the goal, including the whole bottom row that A* never looked at.

```python
import heapq

GRID = (
    "S.#.G",
    ".....",
    ".....",
)
MOVES = ((-1, 0), (0, 1), (1, 0), (0, -1))          # N, E, S, W


def successors(cell):
    r, c = cell
    out = []
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 5 and GRID[nr][nc] != "#":
            out.append(((nr, nc), 1))
    return out


def astar(start, goal, h):
    order = 0
    g = {start: 0}
    heap = [(h(start), order, start)]
    closed = set()
    expanded = []
    while heap:
        _f, _t, s = heapq.heappop(heap)
        if s in closed:
            continue
        closed.add(s)
        expanded.append(s)
        if s == goal:
            return g[s], expanded
        for nxt, step in successors(s):
            if nxt not in g or g[s] + step < g[nxt]:
                g[nxt] = g[s] + step
                order += 1
                heapq.heappush(heap, (g[nxt] + h(nxt), order, nxt))
    return None, expanded


GOAL = (0, 4)
manhattan = lambda s: abs(s[0] - GOAL[0]) + abs(s[1] - GOAL[1])
for name, h in (("ucs  ", lambda s: 0), ("astar", manhattan)):
    cost, expanded = astar((0, 0), GOAL, h)
    print(name, "cost", cost, "expanded", len(expanded), expanded)
```

The block prints `ucs   cost 6 expanded 13` followed by the thirteen cells in the
order they came off the queue, and then `astar cost 6 expanded 9` with the nine
traced above. The `order` counter in the heap entry is not decoration. When two
entries tie on $f$, `heapq` compares the next element of the tuple, and if that
were the state itself the queue would compare tuples of coordinates — harmless
here, and an exception the moment a state is something that cannot be ordered.
The counter sends ties to the earlier insertion and keeps the comparison from
ever reaching the state.

## Why an underestimate is enough

Suppose the search expands the goal via a path of cost $C$ while a cheaper path
of cost $C^* < C$ exists. Some state $n$ on that cheaper path is on the frontier
— the cheap path has to leave the closed set somewhere — with $g(n)$ equal to its
true cost along the cheap path, and $f(n) = g(n) + h(n)$. If $h$ never
overestimates, $h(n)$ is at most the true remaining cost, so $f(n) \le C^*$. But
the goal was chosen ahead of $n$, so $C \le f(n) \le C^* < C$, which is a
contradiction. A heuristic that never exceeds the true cost to the goal is called
*admissible*, and this is the whole of the proof that A* with an admissible
heuristic returns an optimal path.

Manhattan distance is admissible on the maze because a wall can only lengthen a
route, never shorten it. It is admissible on the 8-puzzle for a reason worth
stating precisely, since the lab asks you to implement it there: every tile has
to travel at least its row distance plus its column distance to reach its home
square, and every move slides exactly one tile exactly one square, so no solution
can use fewer moves than the sum over tiles. The blank is left out of the sum
because moving the blank *is* moving a tile; counting both would count each move
twice.

There is a stronger property. A heuristic is *consistent* if for every step from
$n$ to $n'$ with cost $c$, $h(n) \le c + h(n')$: the estimate never drops by more
than the step that was taken. Consistency implies admissibility (chain the
inequality along any path to the goal, where $h = 0$), and it buys something the
proof above does not: along any path $f$ never decreases, so the first time a
state is expanded is the cheapest time, and no closed state ever needs reopening.
Manhattan distance is consistent because one move changes one tile's distance by
exactly one. The lab's test walks four hundred random puzzle moves checking
$h(s) \le 1 + h(s')$ at every one of them.

## The mistake, and why it is tempting

The tempting shortcut is to test for the goal when a state is *generated* rather
than when it is expanded. It saves one expansion, and for BFS on a maze where
every step costs one it is harmless. For uniform-cost search and A* it is wrong,
and the reason is that a state's cost is only final when it comes off the queue.

```python
import heapq

EDGES = {"S": [("A", 1), ("G", 10)], "A": [("G", 1)], "G": []}


def search(test_on_generation):
    heap = [(0, "S")]
    g = {"S": 0}
    while heap:
        cost, s = heapq.heappop(heap)
        if s == "G":
            return cost
        for nxt, step in EDGES[s]:
            if test_on_generation and nxt == "G":
                return cost + step
            if nxt not in g or cost + step < g[nxt]:
                g[nxt] = cost + step
                heapq.heappush(heap, (g[nxt], nxt))


print("tested on generation:", search(True))
print("tested on expansion: ", search(False))
```

Expanding `S` generates `A` at cost 1 and `G` at cost 10. Testing on generation
returns 10 on the spot. Testing on expansion pushes both, pops `A` first because
1 is less than 10, generates `G` again at cost 2, relaxes its entry, and pops that
one next: the block prints `10` and then `2`. The lab insists on testing at
expansion in all four searches for a second reason as well — with every search
making the same decision at the same moment, the expansion counts mean the same
thing and can be compared.

The other frequent slip is in A*'s relaxation. When a cheaper route to a state
already on the frontier is found, the old heap entry cannot be removed from a
`heapq`, so the new one is pushed alongside it. The stale entry will surface
later with a worse priority, and the `if s in closed: continue` at the top of the
loop is what absorbs it. Leave that line out and the state is expanded twice, the
count is wrong, and — if the goal is the state in question — the path returned
can be the expensive one.

## Where it stops holding

Admissibility guarantees the cost of the path, not the cost of finding it. A*
with $h = 0$ is uniform-cost search, which is optimal and slow; A* with a
heuristic that is nearly the true cost expands almost nothing. In between, the
number of expansions grows exponentially in the heuristic's error, and on the
8-puzzle the difference between Manhattan distance and no heuristic is the
difference between hundreds of expansions and tens of thousands, which the last
test in the lab measures directly.

The guarantee also assumes positive step costs — a zero-cost cycle lets $g$ stop
increasing and the argument that the frontier eventually empties fails — and it
assumes the goal is reachable. When it is not, every graph search exhausts its
frontier and returns nothing, and that is an answer: the lab's walled-in start
expects `(None, None, expanded)` from all four, because an empty frontier is a
proof that no path exists. Finally, all of this is memory-bound. BFS, UCS and A*
hold the frontier and the closed set, and both grow with the number of distinct
states reached. Depth-first search does not, which is the one reason it survives
despite giving up optimality; for problems whose state space does not fit in
memory, iterative deepening and memory-bounded variants of A* pick up where this
module leaves off.
''',
                },
            ],
            "quiz": {
                "title": "Frontiers, heuristics and the moment a cost is final",
                "minutes": 8,
                "questions": [
                    {
                        "q": "On the lab's maze, breadth-first search returns a path of cost 18, the optimum. What is that optimality resting on?",
                        "opts": [
                            "Every step costs the same, so ordering the frontier by depth is ordering it by cost",
                            "A FIFO queue always releases the goal before any state that lies further from the start",
                            "The closed set guarantees that no state is ever reached again by a longer route",
                            "The goal test is applied on expansion rather than on generation, which fixes the order",
                        ],
                        "a": 0,
                        "whys": [
                            r"Depth and cost are the same number when every step costs one, and BFS orders by depth.",
                            r"The queue orders by *depth*, not by distance in cost. Give one edge a cost of 100 and the goal can come off the queue at depth 1 while a three-step path of cost 3 is still waiting behind it.",
                            r"The closed set stops states being expanded twice; it says nothing about which path reached them first. BFS reaches each state first by the shallowest path because of the queue, not because of the closed set.",
                            r"Testing on expansion is what makes the counts comparable across the four searches, and it is required for UCS and A*. BFS with unit costs would return the same path either way; it is not the source of the optimality.",
                        ],
                        "why": r"""
BFS knows nothing about cost. It expands states in order of how many steps they
are from the start, and the first goal it meets is the one with the fewest steps.
That coincides with the cheapest path only when fewest steps and least cost are
the same thing — every step costing one. Uniform-cost search exists precisely to
drop that condition: it orders by $g$ instead of depth, and pays for it with a
priority queue.
""",
                    },
                    {
                        "q": "Uniform-cost search on `S -> A -> G` (costs 1 and 1) with a direct edge `S -> G` of cost 10 returns 2, but only if the goal is tested when it is expanded. Why does testing at generation return 10?",
                        "opts": [
                            "Generation happens before relaxation, so the generated cost has not yet been compared with any alternative route",
                            "A state's path cost is final only when it leaves the queue, and `G` first appears with the cost 10 route",
                            "The goal can only be generated once, and the first generation is always along the first edge listed",
                            "Testing at generation skips the closed set, so the search never learns that `A` leads to `G` as well",
                        ],
                        "a": 1,
                        "whys": [
                            r"Relaxation is part of the story but it is the queue that settles it: `G` is relaxed to 2 when `A` is expanded, and that relaxed entry is the one that reaches the front. Comparing at generation would still see only the routes discovered so far.",
                            r"When `S` is expanded, `G` is generated at 10 and `A` at 1. Nothing has yet said that the cheapest way to `G` is known; that is only established when `G` comes off the queue ahead of everything cheaper.",
                            r"`G` is generated twice here — once from `S` at cost 10, once from `A` at cost 2 — and the second generation is the one that matters. Nothing limits a state to one generation; that is why the relaxation step exists.",
                            r"The closed set is about states already expanded; `A` is expanded either way. The problem is that the search stopped before expanding `A`, not that it forgot anything about it.",
                        ],
                        "why": r"""
A priority queue promises that the entry it releases is the cheapest one present.
That promise is about entries coming *off* the queue. At the moment `G` is
generated at cost 10, `A` is sitting on the queue at cost 1 with a cheaper route
to `G` behind it, and the search has not yet looked. Waiting for `G` to be
expanded lets `A` go first, relax `G` to 2, and put that entry ahead. The same
argument is why A* tests at expansion, and it is why the lab makes all four
searches test there — so the expansion counts count the same thing.
""",
                    },
                    {
                        "q": "Manhattan distance on the 8-puzzle is admissible. Which argument establishes that, and why is the blank left out of the sum?",
                        "opts": [
                            "Each move shifts one tile one square, so each tile needs at least its distance; the blank's motion is a tile's motion seen from the other side",
                            "Walls never shorten a route, so a straight-line count undercounts the true number of moves; the blank has no home square to measure a distance to",
                            "The sum of tile distances is the exact number of moves in the optimal solution; the blank's distance is always zero, so it adds nothing",
                            "The heuristic counts misplaced tiles, and the blank is not a tile, so including it would inflate the count by exactly one",
                        ],
                        "a": 0,
                        "whys": [
                            r"One move, one tile, one square: no solution can move all the tiles home in fewer moves than their distances sum to. The blank swaps places with that tile, so counting its distance too would count every move twice.",
                            r"That is the argument for the *maze*, where Manhattan ignores walls. The puzzle has no walls; its argument is about what a single move can achieve. And the blank does have a home square — position 8 — which is why leaving it out needs a reason.",
                            r"It is a lower bound, not the answer. A tile often has to move out of another's way and back, so the true solution length usually exceeds the sum; if it were exact there would be nothing left for A* to search.",
                            r"Misplaced-tile counting is a different, weaker heuristic. Manhattan measures how far each tile is, not whether it is displaced, and the blank's exclusion is about double counting moves, not about inflating a tally by one.",
                        ],
                        "why": r"""
Admissibility is a claim that no solution can be shorter than the estimate, so it
has to come from a statement about what one move can do. A slide moves exactly one
tile exactly one square, so a tile at distance $d$ from home needs at least $d$
moves, and the moves for different tiles do not overlap. Sum them and you have a
lower bound. The blank moves every time a tile moves — into the square the tile
left — so its distance is not extra information, it is the same moves again, and
adding it can push the estimate above the truth, breaking the bound.
""",
                    },
                    {
                        "q": "A heuristic is admissible but not consistent. What does A* lose compared with a consistent one?",
                        "opts": [
                            "The returned path may no longer be optimal, since only consistency guarantees the cost",
                            "The heuristic can overestimate along some edges, so the search may return a longer path",
                            "The search may expand more nodes than uniform-cost search does on the same problem",
                            "A state closed at one cost can be reached more cheaply later and would need reopening",
                        ],
                        "a": 3,
                        "whys": [
                            r"Admissibility alone is enough for the optimal cost — that is what the contradiction proof uses. Consistency buys efficiency, not correctness of the answer.",
                            r"An inconsistent heuristic can still be admissible, never overestimating the cost to the goal. What it can do is *drop* by more than a step's cost between neighbours, which is a different thing from overestimating.",
                            r"That can happen with any heuristic if the heuristic is poor, consistent or not. Consistency is not what separates A* from UCS in node count; the quality of $h$ is.",
                            r"With $f$ non-decreasing along every path, the first expansion of a state is the cheapest and the closed set can be trusted. Without it, a cheaper route to a closed state can turn up later.",
                        ],
                        "why": r"""
Consistency means $h$ never falls by more than the cost of the step, so
$f = g + h$ never decreases along a path. That is what lets the closed set be
final: once a state has been expanded at some $g$, no later route can be cheaper,
because a cheaper route would have had a smaller $f$ earlier and been expanded
first. Drop consistency and $f$ can dip, a state can be closed at a cost that is
not its best, and a correct implementation has to allow reopening it. The lab's
consistency test on Manhattan is what licenses the `if s in closed: continue`
line to discard a state for good.
""",
                    },
                    {
                        "q": "In the lab's `astar`, a state can sit in the heap twice after a cheaper route to it is found. What becomes of the stale entry?",
                        "opts": [
                            "`heapq` drops it as soon as the cheaper entry is pushed, because both entries carry the same state",
                            "It surfaces later with the worse priority and is skipped, because the state is already closed",
                            "It is expanded a second time, which is harmless because the closed set stops its children",
                            "It never reaches the top, because the insertion counter keeps it behind every newer entry",
                        ],
                        "a": 1,
                        "whys": [
                            r"`heapq` has no idea what a state is; it stores tuples and orders them. Nothing is removed when a second tuple with the same state arrives, which is why the search has to be ready for both to come out.",
                            r"The cheaper entry comes out first and closes the state; when the stale one comes out, the closed-set check discards it without counting an expansion.",
                            r"Expanding it again would count a second expansion for the same state, and the lab's counts would be wrong. Worse, if the state is the goal, the second expansion's `g` is the stale, higher one.",
                            r"The counter breaks ties on $f$ only. A stale entry has a *higher* $f$ than the fresh one, so it is behind on priority regardless of the counter — and it will still surface once everything cheaper is gone.",
                        ],
                        "why": r"""
A binary heap cannot delete an arbitrary entry cheaply, so A* implementations do
not try. They push the better entry and let the worse one rot. Because the better
entry has the smaller $f$, it is released first, the state goes into the closed
set, and when the stale entry finally comes out the `if s in closed: continue`
line throws it away before it can be counted or expanded. That one line is doing
the work a decrease-key operation would do in a fancier queue.
""",
                    },
                    {
                        "q": "Depth-first search on the lab's maze expands fewer nodes than breadth-first and finds a path costing more than 18. What has been traded for what?",
                        "opts": [
                            "Memory proportional to depth and a possibly early find, in exchange for any promise about the path's cost",
                            "Optimality on the maze in exchange for completeness, since a depth-first dive can miss a goal that BFS would reach",
                            "The closed set, which DFS does not keep, in exchange for a frontier that can hold the whole maze",
                            "Determinism in exchange for speed, since the diving order depends on the order successors are pushed",
                        ],
                        "a": 0,
                        "whys": [
                            r"A stack holds one branch at a time, and if the dive happens to head the right way the goal turns up early. What is given up is the guarantee that the first goal found is the cheapest one.",
                            r"DFS is complete on a finite graph with a closed set — the lab's test says so in its title. What it lacks is optimality, and the maze result shows it: a path is found, and it is not the best one.",
                            r"The lab's DFS does keep a closed set; without one it would circle forever. Its frontier is what stays small — one branch's worth, not the whole level of a tree.",
                            r"The lab's DFS is deterministic: successors are pushed in reverse so the first one pops first, every time. The order is fixed by convention; that is not what has been traded.",
                        ],
                        "why": r"""
DFS keeps only the current branch on its stack, so its memory is proportional to
the depth of the search rather than to the size of the frontier at some level,
and on a maze that dives the right way it can reach the goal after a handful of
expansions. The price is that the path it finds is the one its diving order
stumbled on. Nothing about a stack orders states by cost, so nothing about DFS
promises the path is cheap — and on the lab's maze it is not.
""",
                    },
                ],
            },
            "lab": {
                "title": "Four searches, one interface",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Everything here talks to the same interface. A *successor function* takes a
state and returns a list of `(next_state, action, step_cost)` triples. A *goal
test* takes a state and returns a bool. Nothing in a search algorithm may know
whether it is walking a maze or shuffling tiles.

Each search returns the triple `(path, cost, expanded)`:

- `path` — the list of states from start to goal inclusive, or `None`
- `cost` — the summed step costs of that path, or `None`
- `expanded` — how many nodes were *expanded*, always an int

A node counts as expanded when it comes off the frontier and is not a duplicate
that has already been closed. Apply the goal test **on expansion**, not on
generation, in all four searches, so that the counts are comparable.

## What to write

**`grid_successors(grid, cell)`** — the open neighbours of `cell`, each with
cost 1, in `N, E, S, W` order. `#` is a wall; the grid edge is a wall too.

**`bfs(start, goal_test, successors)`** — FIFO frontier, one visit per state.

**`dfs(start, goal_test, successors)`** — LIFO frontier. Push the successors in
reverse order so the first successor in `N, E, S, W` order is popped first.
Skip a state that has already been expanded.

**`ucs(start, goal_test, successors)`** — priority queue keyed on `g`.

**`astar(start, goal_test, successors, heuristic)`** — priority queue keyed on
`g + h`, with `g` relaxed when a cheaper route to a state appears.

Break priority ties with an increasing insertion counter so the queue is
deterministic and never has to compare two states.

**`manhattan(state, goal)`** — the 8-puzzle heuristic. A state is a 9-tuple read
row by row, with `0` for the blank. Sum the row and column distance of every
tile except the blank from its goal square.

**`puzzle_successors(state)`** — slide the blank `N, E, S, W`, cost 1 each.

```text
astar(START, goal_test, succ, manhattan_grid)  ->  cost 18, 36 expanded
ucs(START, goal_test, succ)                    ->  cost 18, 53 expanded
```

Unreachable goals return `(None, None, expanded)` — an exhausted frontier is an
answer, not a crash.
''',
                "files": [{"name": "main.py", "content": r'''
import heapq
from collections import deque

GRID = (
    "S..#......",
    ".#.#.####.",
    ".#........",
    ".#####.##.",
    "......#.#.",
    ".####.#.#.",
    ".#...##.#.",
    ".#.#....#.",
    "...#.##...",
    "####.....G",
)

MOVES = (("N", -1, 0), ("E", 0, 1), ("S", 1, 0), ("W", 0, -1))
GOAL8 = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def find_cell(grid, marker):
    """Row/column of the first cell holding marker. Provided."""
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == marker:
                return (r, c)
    raise ValueError("marker not found: " + marker)


def reconstruct(parent, state):
    """Walk the parent chain back to the root and return it forwards. Provided."""
    path = [state]
    while parent[state] is not None:
        state = parent[state]
        path.append(state)
    path.reverse()
    return path


def grid_successors(grid, cell):
    """[(neighbour, action, 1)] for open neighbours, in N, E, S, W order."""
    # your code here


def bfs(start, goal_test, successors):
    """Breadth-first graph search -> (path, cost, expanded)."""
    # your code here


def dfs(start, goal_test, successors):
    """Depth-first graph search -> (path, cost, expanded)."""
    # your code here


def ucs(start, goal_test, successors):
    """Uniform-cost search -> (path, cost, expanded)."""
    # your code here


def astar(start, goal_test, successors, heuristic):
    """A* search -> (path, cost, expanded)."""
    # your code here


def puzzle_successors(state):
    """[(state, action, 1)] for each legal slide of the blank."""
    # your code here


def manhattan(state, goal=GOAL8):
    """Summed row+column distance of every tile except the blank."""
    # your code here


START = find_cell(GRID, "S")
GOAL = find_cell(GRID, "G")
print(ucs(START, lambda s: s == GOAL, lambda s: grid_successors(GRID, s))[1:])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import heapq
from collections import deque

GRID = (
    "S..#......",
    ".#.#.####.",
    ".#........",
    ".#####.##.",
    "......#.#.",
    ".####.#.#.",
    ".#...##.#.",
    ".#.#....#.",
    "...#.##...",
    "####.....G",
)

MOVES = (("N", -1, 0), ("E", 0, 1), ("S", 1, 0), ("W", 0, -1))
GOAL8 = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def find_cell(grid, marker):
    """Row/column of the first cell holding marker. Provided."""
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == marker:
                return (r, c)
    raise ValueError("marker not found: " + marker)


def reconstruct(parent, state):
    """Walk the parent chain back to the root and return it forwards. Provided."""
    path = [state]
    while parent[state] is not None:
        state = parent[state]
        path.append(state)
    path.reverse()
    return path


def grid_successors(grid, cell):
    """[(neighbour, action, 1)] for open neighbours, in N, E, S, W order."""
    r, c = cell
    out = []
    for name, dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[nr]) and grid[nr][nc] != "#":
            out.append(((nr, nc), name, 1))
    return out


def bfs(start, goal_test, successors):
    """Breadth-first graph search -> (path, cost, expanded)."""
    parent = {start: None}
    cost = {start: 0}
    frontier = deque([start])
    expanded = 0
    while frontier:
        state = frontier.popleft()
        expanded += 1
        if goal_test(state):
            return reconstruct(parent, state), cost[state], expanded
        for nxt, _action, step in successors(state):
            # First discovery is the shallowest one, so never revisit.
            if nxt not in parent:
                parent[nxt] = state
                cost[nxt] = cost[state] + step
                frontier.append(nxt)
    return None, None, expanded


def dfs(start, goal_test, successors):
    """Depth-first graph search -> (path, cost, expanded)."""
    parent = {start: None}
    cost = {start: 0}
    stack = [start]
    closed = set()
    expanded = 0
    while stack:
        state = stack.pop()
        if state in closed:
            continue
        closed.add(state)
        expanded += 1
        if goal_test(state):
            return reconstruct(parent, state), cost[state], expanded
        # Reversed, so the first successor ends up on top of the stack.
        for nxt, _action, step in reversed(successors(state)):
            if nxt not in closed:
                parent[nxt] = state
                cost[nxt] = cost[state] + step
                stack.append(nxt)
    return None, None, expanded


def ucs(start, goal_test, successors):
    """Uniform-cost search -> (path, cost, expanded)."""
    return astar(start, goal_test, successors, lambda state: 0)


def astar(start, goal_test, successors, heuristic):
    """A* search -> (path, cost, expanded)."""
    order = 0
    g = {start: 0}
    parent = {start: None}
    heap = [(heuristic(start), 0, start)]
    closed = set()
    expanded = 0
    while heap:
        _f, _tie, state = heapq.heappop(heap)
        if state in closed:
            continue  # a stale entry left behind by a cheaper reopening
        closed.add(state)
        expanded += 1
        if goal_test(state):
            return reconstruct(parent, state), g[state], expanded
        for nxt, _action, step in successors(state):
            new_g = g[state] + step
            if nxt not in g or new_g < g[nxt]:
                g[nxt] = new_g
                parent[nxt] = state
                order += 1
                heapq.heappush(heap, (new_g + heuristic(nxt), order, nxt))
    return None, None, expanded


def puzzle_successors(state):
    """[(state, action, 1)] for each legal slide of the blank."""
    blank = state.index(0)
    r, c = divmod(blank, 3)
    out = []
    for name, dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            other = nr * 3 + nc
            tiles = list(state)
            tiles[blank], tiles[other] = tiles[other], tiles[blank]
            out.append((tuple(tiles), name, 1))
    return out


def manhattan(state, goal=GOAL8):
    """Summed row+column distance of every tile except the blank."""
    home = {tile: divmod(i, 3) for i, tile in enumerate(goal)}
    total = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        r, c = divmod(i, 3)
        gr, gc = home[tile]
        total += abs(r - gr) + abs(c - gc)
    return total


START = find_cell(GRID, "S")
GOAL = find_cell(GRID, "G")
print(ucs(START, lambda s: s == GOAL, lambda s: grid_successors(GRID, s))[1:])
'''}],
                "hints": [
                    "`ucs` is `astar` with a heuristic that always returns 0 — write it that way and you cannot get the two out of step.",
                    "Push `(g + h, order, state)` where `order` is a counter you increment on every push. Without it, heapq compares states when two priorities tie.",
                    "Skip a popped state that is already in the closed set; that is how you absorb the stale entries left behind when `g` is relaxed.",
                    "For `manhattan`, build a `tile -> (row, col)` map of the goal once, then walk the state. `divmod(i, 3)` turns a flat index into row and column.",
                ],
                "tests": [
                    {"name": "grid_successors respects walls and order", "code": r'''
_g = ("S.#", "...", "#.G")
assert grid_successors(_g, (1, 1)) == [((0, 1), "N", 1), ((1, 2), "E", 1),
                                       ((2, 1), "S", 1), ((1, 0), "W", 1)], \
    f"Got {grid_successors(_g, (1, 1))!r} — expected N, E, S, W order with cost 1"
assert grid_successors(_g, (0, 0)) == [((0, 1), "E", 1), ((1, 0), "S", 1)], \
    f"The top-left corner has no N or W neighbour, got {grid_successors(_g, (0, 0))!r}"
assert grid_successors(_g, (2, 2)) == [((1, 2), "N", 1), ((2, 1), "W", 1)], \
    f"The bottom-right corner has no S or E neighbour, got {grid_successors(_g, (2, 2))!r}"
assert grid_successors(_g, (0, 1)) == [((1, 1), "S", 1), ((0, 0), "W", 1)], \
    f"(0,2) is a wall, got {grid_successors(_g, (0, 1))!r}"
'''},
                    {"name": "BFS and UCS agree on the optimal maze cost", "code": r'''
_succ = lambda s: grid_successors(GRID, s)
_goal = lambda s: s == GOAL


def _valid(_path):
    assert _path[0] == START and _path[-1] == GOAL, f"path runs {_path[0]} -> {_path[-1]}"
    for _a, _b in zip(_path, _path[1:]):
        assert abs(_a[0] - _b[0]) + abs(_a[1] - _b[1]) == 1, f"{_a} and {_b} are not adjacent"
        assert GRID[_b[0]][_b[1]] != "#", f"{_b} is a wall"
    return len(_path) - 1


_pb, _cb, _eb = bfs(START, _goal, _succ)
_pu, _cu, _eu = ucs(START, _goal, _succ)
assert _cb == 18, f"bfs cost {_cb!r}, expected 18"
assert _cu == 18, f"ucs cost {_cu!r}, expected 18"
assert _valid(_pb) == 18 and _valid(_pu) == 18, "the returned paths must have 18 steps"
assert _eb > 0 and _eu > 0, "expanded counts should be positive ints"
'''},
                    {"name": "A* matches the cost with fewer expansions", "code": r'''
_succ = lambda s: grid_successors(GRID, s)
_goal = lambda s: s == GOAL
_h = lambda s: abs(s[0] - GOAL[0]) + abs(s[1] - GOAL[1])
_pa, _ca, _ea = astar(START, _goal, _succ, _h)
_pu, _cu, _eu = ucs(START, _goal, _succ)
assert _ca == 18, f"astar cost {_ca!r}, expected 18 — A* with an admissible h is optimal"
assert _ea < _eu, f"astar expanded {_ea}, ucs expanded {_eu} — the heuristic should help"
assert _ea <= 45, f"astar expanded {_ea}; a correct f = g + h ordering expands about 36 here"
'''},
                    {"name": "DFS is complete here but not optimal", "code": r'''
_succ = lambda s: grid_successors(GRID, s)
_goal = lambda s: s == GOAL
_pd, _cd, _ed = dfs(START, _goal, _succ)
assert _pd is not None, "dfs should still find the goal"
assert _pd[0] == START and _pd[-1] == GOAL, f"dfs path runs {_pd[0]} -> {_pd[-1]}"
for _a, _b in zip(_pd, _pd[1:]):
    assert abs(_a[0] - _b[0]) + abs(_a[1] - _b[1]) == 1, f"{_a} and {_b} are not adjacent"
    assert GRID[_b[0]][_b[1]] != "#", f"dfs walked through the wall at {_b}"
assert _cd == len(_pd) - 1, f"dfs cost {_cd!r} disagrees with its own path length"
assert _cd >= 18, "no path can beat the optimal 18"
assert _ed < bfs(START, _goal, _succ)[2], "on this maze DFS should expand fewer nodes than BFS"
'''},
                    {"name": "An unreachable goal exhausts the frontier", "code": r'''
_walled = ("S#", "#G")
_s = lambda s: grid_successors(_walled, s)
for _name, _fn in (("bfs", bfs), ("dfs", dfs), ("ucs", ucs)):
    _p, _c, _e = _fn((0, 0), lambda s: s == (1, 1), _s)
    assert _p is None and _c is None, f"{_name} claimed a path through solid wall: {_p!r}"
    assert isinstance(_e, int) and _e >= 1, f"{_name} should still report nodes expanded, got {_e!r}"
_p, _c, _e = astar((0, 0), lambda s: s == (1, 1), _s, lambda s: 0)
assert _p is None and _c is None, f"astar claimed a path through solid wall: {_p!r}"
'''},
                    {"name": "Manhattan is admissible and consistent", "code": r'''
import random as _random
_known = {
    (0, 2, 3, 1, 4, 6, 7, 5, 8): 4,
    (1, 2, 3, 4, 0, 6, 7, 5, 8): 2,
    (1, 2, 3, 7, 4, 8, 6, 5, 0): 10,
    (6, 4, 2, 7, 1, 3, 5, 8, 0): 14,
    (1, 6, 2, 7, 0, 8, 5, 3, 4): 14,
}
assert manhattan(GOAL8) == 0, "the goal is zero moves from the goal"
for _state, _opt in _known.items():
    _h = manhattan(_state)
    assert _h <= _opt, f"manhattan({_state}) = {_h} exceeds the true cost {_opt} — not admissible"
_rng = _random.Random(7)
_s = GOAL8
for _ in range(400):
    _kids = puzzle_successors(_s)
    assert len(_kids) in (2, 3, 4), f"{_s} has {len(_kids)} successors"
    for _nxt, _act, _cost in _kids:
        assert manhattan(_s) <= _cost + manhattan(_nxt), \
            f"h({_s}) = {manhattan(_s)} breaks consistency against {_nxt}"
    _s = _rng.choice(_kids)[0]
'''},
                    {"name": "A* solves the 8-puzzle optimally and cheaply", "code": r'''
_goal8 = lambda s: s == GOAL8
_known = {
    (0, 2, 3, 1, 4, 6, 7, 5, 8): 4,
    (1, 2, 3, 4, 0, 6, 7, 5, 8): 2,
    (1, 2, 3, 7, 4, 8, 6, 5, 0): 10,
    (6, 4, 2, 7, 1, 3, 5, 8, 0): 14,
}
for _state, _opt in _known.items():
    _p, _c, _e = astar(_state, _goal8, puzzle_successors, manhattan)
    assert _c == _opt, f"astar({_state}) cost {_c!r}, expected {_opt}"
    assert len(_p) == _opt + 1, f"a {_opt}-move solution visits {_opt + 1} states, got {len(_p)}"
    assert _p[0] == _state and _p[-1] == GOAL8, "the path must run from the state to the goal"
_hard = (6, 4, 2, 7, 1, 3, 5, 8, 0)
_ea = astar(_hard, _goal8, puzzle_successors, manhattan)[2]
_eu = ucs(_hard, _goal8, puzzle_successors)[2]
assert _eu > 20 * _ea, f"ucs expanded {_eu}, astar {_ea} — the heuristic should save orders of magnitude"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Adversarial search",
            "summary": "Minimax over a real game tree, and the pruning that makes it affordable.",
            "concepts": [
                "A zero-sum game tree alternates a maximiser and a minimiser over the same value scale",
                "Minimax is the value of the game under optimal play by both sides",
                "Depth limits force a heuristic evaluation at the horizon — and with it, horizon effects",
                "Alpha is the best value the maximiser can already guarantee, beta the best the minimiser can",
                "When alpha >= beta the remaining siblings cannot change the parent's value, so they are cut",
                "Pruning changes the node count, never the root value: it is an exact optimisation",
                "With perfect move ordering the effective branching factor falls from b to about sqrt(b)",
            ],
            "read": [
                {
                    "title": "The branch you never have to look at",
                    "minutes": 12,
                    "body": r'''
Two players take turns dropping pieces into a four-column board. You are `X` and
it is your move. In your head you try a column, imagine the best reply, imagine
your best answer to that, and somewhere three or four moves down you find a
position you can judge — a win, a loss, or a board that looks about level. Then
you carry the judgement back up to the move that started it, do the same for the
other three columns, and play the one whose worst case is best. That is minimax.
The reason it works is that both players are looking at the same number:
whatever is good for you is bad for your opponent by exactly the same amount. A
game with that property is *zero-sum*, and it is the only kind this module
handles.

## A tree with numbers on the leaves

Strip the game away and keep the shape. A root where it is the maximiser's turn;
three children where it is the minimiser's turn; three leaves under each child
holding the position's value, from the maximiser's point of view.

```text
                 MAX
        /         |         \
      MIN        MIN        MIN
    /  |  \    /  |  \    /  |  \
   3  12   8  2   4   6  14   5   2
```

The value of a leaf is what it says. The value of a MIN node is the smallest of
its children's values, because the minimiser will pick the move that hurts the
maximiser most: the left child is worth $\min(3, 12, 8) = 3$, the middle
$\min(2, 4, 6) = 2$, the right $\min(14, 5, 2) = 2$. The value of the root is
the largest of those, $\max(3, 2, 2) = 3$, and the move that achieves it is the
left branch. Nothing has been assumed except that each player chooses the best
available number for themselves, and that is the definition: the minimax value
of a position is its value under optimal play by both sides.

Written as a rule, for a non-terminal node $n$ with children $C(n)$:

$$
v(n) = \begin{cases} \max_{c \in C(n)} v(c) & \text{if the maximiser moves at } n \\ \min_{c \in C(n)} v(c) & \text{if the minimiser moves at } n \end{cases}
$$

and $v$ of a terminal node is its payoff. Counting one visit per node, the tree
above costs 13 visits: the root, three children, nine leaves.

## Where the leaves come from

In the tree above the leaves were given. In a real game they are not: Connect-3
on a 4 by 4 board runs for up to sixteen plies, and a full tree from the empty
board has tens of thousands of nodes even after gravity removes the illegal
moves. Chess has more positions than there are atoms available to store them. So
a search stops at a *depth limit* and, at a live position on that horizon,
substitutes a heuristic *evaluation* for the true value. The lab in this module,
*Alpha-beta on Connect-3*, hands you `evaluate`, which scores a position by
counting lines that one player could still complete, weighting a two-in-a-row
above a single piece. That function is a guess. Everything above the horizon is
exact arithmetic on guesses, which is why a deeper search is a better one: the
guesses are made further from the position that matters and their errors have
more chances to wash out.

There is a specific failure named for this. A position may look level at the
horizon while a forced loss sits one ply beyond it; the search cannot see it and
plays into it. That is the *horizon effect*, and the only cures are to search
deeper, to evaluate more carefully at leaves that are tactically unstable, or to
extend the search selectively in lines where something is about to happen. The
lab's depth-6 search from an empty board already sees enough to know the game is
drawn with best play, which is why both of its searches report value 0.

## Two bounds, and the cut

Go back to the tree and watch the search run left to right, but this time keep
two numbers with you. $\alpha$ is the best value the maximiser is already
guaranteed somewhere above the node being examined; $\beta$ is the best value
the minimiser is already guaranteed. At the root, before anything is known,
$\alpha = -\infty$ and $\beta = +\infty$.

Enter the left MIN node with that window. Its first leaf is 3, so its running
best is 3 and the minimiser can hold this node to at most 3: $\beta$ becomes 3.
Leaves 12 and 8 cannot lower that. The node returns 3, and the root now knows it
can guarantee 3 by playing left: $\alpha = 3$.

Enter the middle MIN node with $\alpha = 3$, $\beta = +\infty$. Its first leaf is
2. The minimiser can now hold this node to 2 or less. But the maximiser already
has 3 available at the root, and will never choose a branch worth at most 2.
Whatever the remaining leaves hold — 4 and 6, as it happens, or a thousand —
they cannot change the root's decision. The node returns 2 without looking at
them. In symbols: $\beta$ was set to 2, $\alpha \ge \beta$, and the loop over
children breaks.

Enter the right MIN node with $\alpha = 3$ again. Its first leaf is 14, so
$\beta = 14$; nothing to cut yet. The second is 5, $\beta = 5$; still above 3.
The third is 2, $\beta = 2$, now $\alpha \ge \beta$ — but there are no children
left to skip. It returns 2. The root's answer is unchanged, 3 on the left
branch, and the search visited eleven nodes instead of thirteen. Two leaves were
never generated, and the root value is exactly what full minimax gave.

```python
def minimax(node, maximising, stats):
    stats["nodes"] += 1
    if isinstance(node, int):
        return node
    values = [minimax(child, not maximising, stats) for child in node]
    return max(values) if maximising else min(values)


def alphabeta(node, maximising, alpha, beta, stats):
    stats["nodes"] += 1
    if isinstance(node, int):
        return node
    best = -10 ** 9 if maximising else 10 ** 9
    for child in node:
        value = alphabeta(child, not maximising, alpha, beta, stats)
        if maximising:
            best = max(best, value)
            alpha = max(alpha, best)
        else:
            best = min(best, value)
            beta = min(beta, best)
        if alpha >= beta:
            break
    return best


TREE = [[3, 12, 8], [2, 4, 6], [14, 5, 2]]
REORDERED = [[3, 12, 8], [2, 4, 6], [2, 5, 14]]
for name, tree in (("as drawn ", TREE), ("reordered", REORDERED)):
    full, pruned = {"nodes": 0}, {"nodes": 0}
    v1 = minimax(tree, True, full)
    v2 = alphabeta(tree, True, -10 ** 9, 10 ** 9, pruned)
    print(name, "minimax", v1, "in", full["nodes"], "nodes;",
          "alphabeta", v2, "in", pruned["nodes"])
```

The first line printed is `as drawn  minimax 3 in 13 nodes; alphabeta 3 in 11`.
The second tree is the same tree with the right node's leaves reversed, and it
prints `reordered minimax 3 in 13 nodes; alphabeta 3 in 9`: with the 2 examined
first, the right node is cut after a single leaf. Same tree, same answer, two
more nodes saved by looking at the children in a better order.

## Why the count changes and the value never does

A cut is taken only when a node's value is already known to be irrelevant: a MIN
node whose best is at or below $\alpha$ will not be chosen by the maximiser
above it, and a MAX node whose best is at or above $\beta$ will not be chosen by
the minimiser above it. The value returned from a cut node need not be its true
minimax value. The middle node above returned 2 and its true value happens to be
2; had its leaves been 2, 1, 1 it would still have returned 2 while its true
value was 1. That does not matter. What is returned is a *bound* tight enough to
settle the parent's choice, and the parent's choice is all that propagates. This
is why the lab's test compares your `minimax` and `alphabeta` at every depth
from 1 to 6 and demands the same root value and the same move: pruning is an
exact optimisation, and any disagreement between the two is a bug in the window
handling rather than a property of the game.

The ordering result is what makes the technique worth having. With children
examined in a random order, alpha-beta saves a constant fraction. With the best
child examined first at every node, the number of leaves visited falls from
$b^d$ to roughly $b^{d/2}$ — the effective branching factor drops from $b$ to
about $\sqrt{b}$, so the same time buys twice the depth. Nobody has perfect
ordering, because perfect ordering means already knowing the answer, but cheap
heuristics such as trying the move that was best at the previous iteration get
close enough that real engines see most of that gain. The lab uses ascending
column order and still cuts depth-6 Connect-3 from 4949 nodes to 964.

## The mistake, and why it is tempting

The window is passed *down* and never *up*. A child receives the parent's
current $\alpha$ and $\beta$, narrows its own copies as it examines its
children, and returns a single value. The parent then updates its own $\alpha$
or $\beta$ from that value. The tempting error is to let the child's narrowed
window leak back into the parent — through a shared mutable object, or by
returning the bounds alongside the value and reading them — and it is tempting
because it looks like more information. It is wrong because the child's $\beta$
is a fact about *its* subtree, a constraint the minimiser imposed there, and
applying it to the parent's remaining siblings cuts branches that were never
examined under that constraint. The symptom is a search that prunes more than it
should and returns a value that differs from minimax at some depth, and the
lab's depth sweep exists to catch it.

A quieter mistake lives in the comparison. Both searches must keep the *first*
move that achieves the best value, which means updating the running best only on
a strict improvement: `if value > best` for the maximiser, never `>=`. With
`>=`, a later column that ties overwrites the earlier one, and since alpha-beta
stops looking at some columns that minimax examines fully, the two searches can
end up reporting different moves for the same value. They will still agree on
the value, so the test that catches it is the one that compares moves.

A third: counting nodes in the wrong place. The lab counts a node on entry to
the call, before the terminal test, so that a leaf costs one visit exactly as an
interior node does. Count after the terminal test and the leaves vanish from the
total; count inside the loop over children and the root is never counted. The
numbers 4949 and 964 in the brief only come out if the count is where the brief
says.

## Where it stops holding

Everything above rests on zero-sum. If the two players' payoffs are not opposite
— a negotiation, a cooperative game, or a three-player game where two can gang
up on the third — there is no single number for both to argue over, minimax
does not apply, and alpha-beta's cut, which reasons from one player's bound to
the other's choice, has nothing to reason from. Chance also breaks the picture:
a dice roll between moves inserts nodes whose value is an *expectation* over
outcomes rather than a max or a min, and while the search still works — it is
called expectiminimax — the pruning argument weakens, because an average can be
moved by any of its terms, so a single bad outcome does not settle a chance node
the way a single bad leaf settles a MIN node.

Within zero-sum games, the limit is the evaluation function. Minimax is exact
above the horizon and only as good as the guess at it, and a search that goes
deeper with a bad evaluation can play worse than a shallower one with a good
evaluation, because it trusts more of its guesses. Depth is not a substitute for
knowing what a position is worth; it is a multiplier on it.
''',
                },
            ],
            "quiz": {
                "title": "Bounds, cuts and the value that does not move",
                "minutes": 8,
                "questions": [
                    {
                        "q": "In the traced tree the middle MIN node was abandoned after its first leaf, 2, without looking at 4 and 6. What made that safe?",
                        "opts": [
                            "The remaining leaves 4 and 6 were both larger than 2, so they could not have lowered the node's value any further",
                            "The maximiser already had 3 guaranteed on the left, so a branch worth at most 2 can never be chosen",
                            "A MIN node returns its first leaf whenever that leaf is below the running average of the tree",
                            "The minimiser's 2 was smaller than any value in the left subtree, so the node was already decided",
                        ],
                        "a": 1,
                        "whys": [
                            r"True, but the search did not know it — those leaves were never looked at. Had they been 1 and 0 the cut would have been made all the same, because it rests on what the maximiser already holds, not on what the remaining leaves contain.",
                            r"The node's value is at most 2 and the root has 3 in hand. Nothing below 2 or above 2 in this node changes the root's choice.",
                            r"No average is involved anywhere in minimax or alpha-beta. The cut compares a node's running best against a bound inherited from above; the rest of the tree's values are irrelevant to it.",
                            r"The comparison is not against the left subtree's values but against $\alpha$, the best the maximiser has already secured. The left subtree's *minimum* set $\alpha = 3$; its other leaves, 12 and 8, played no part.",
                        ],
                        "why": r"""
A MIN node's value can only go down as more leaves are seen. Once it is at or
below the best the maximiser already holds above it — the $\alpha$ passed in —
the maximiser will never choose it, so its exact value is irrelevant and the
remaining leaves are not worth generating. The cut is a statement about the
parent's choice, not about the leaves that were skipped, and it would be made
regardless of what they contain.
""",
                    },
                    {
                        "q": "A pruned MIN node can return a value above its true minimax value — leaves 2, 1, 1 return 2 after the cut, though the node is worth 1. Why does the root still come out right?",
                        "opts": [
                            "The parent only needed a bound tight enough to reject the branch, and 2 against an alpha of 3 is enough",
                            "The parent re-expands any branch that was cut, so the true value is always recovered before the root decides",
                            "A cut node's value never reaches the root, because the parent discards every branch that was pruned",
                            "The returned value is rounded towards the parent's alpha, so 2 and 1 are treated as the same answer",
                        ],
                        "a": 0,
                        "whys": [
                            r"The maximiser above had 3 and the node reported at most 2; whether the truth is 2 or 1 makes no difference to the choice, and only the choice propagates.",
                            r"Nothing is re-expanded. Re-examining cut branches would undo the saving that pruning exists for; the whole point is that the exact value of a rejected branch is never needed.",
                            r"The value does reach the parent — the parent computes `max(best, value)` with it. It loses the comparison to 3, which is the mechanism, but it is not discarded before being compared.",
                            r"There is no rounding. The node returns exactly the running best it had when the cut fired, which is a bound on its true value, and the parent uses that number as it is.",
                        ],
                        "why": r"""
Alpha-beta never promises that every node's returned value is its minimax
value. It promises that the *root's* value and move are unchanged, and it keeps
that promise because a cut fires only when the node's value has already been
shown to lose the parent's comparison. Reporting 2 for a node worth 1 is fine
when the parent holds 3: both lose. The lab's depth sweep checks the root, not
the interior, for exactly this reason.
""",
                    },
                    {
                        "q": "Reversing the right node's leaves to 2, 5, 14 cut the visit count from 11 to 9. What does good move ordering buy in general?",
                        "opts": [
                            "The root value becomes more accurate, because the strongest replies are examined before the horizon",
                            "The search finds the same value but returns a different, better move than the unordered search would",
                            "Every node except the leaves can be cut away, so the cost of the search becomes linear in the depth of the tree",
                            "The effective branching factor drops towards the square root of b, so a budget reaches about twice the depth",
                        ],
                        "a": 3,
                        "whys": [
                            r"Ordering changes how many nodes are visited, never the value returned. The root value is the minimax value under any ordering; the accuracy of the horizon evaluation is a separate matter that ordering cannot touch.",
                            r"The move is unchanged too — with the strict comparison the lab requires, both orderings report the same first-best column. Ordering is purely a cost saving.",
                            r"Even perfect ordering visits about $b^{d/2}$ leaves, which is still exponential in depth. Linear cost would mean examining one line only, which is not a search at all.",
                            r"From $b^d$ leaves to about $b^{d/2}$: the same node budget spent on a well-ordered tree reaches roughly twice as deep.",
                        ],
                        "why": r"""
With the best child examined first at every node, each MIN node is cut as soon
as its first leaf falls below $\alpha$, and each MAX node as soon as its first
leaf rises above $\beta$. The count of leaves visited becomes about $b^{d/2}$
rather than $b^d$ — the effective branching factor is $\sqrt{b}$ — and since the
cost of a search is dominated by the leaves, that doubles the depth the same
budget can afford. Nothing about the answer changes; only the bill.
""",
                    },
                    {
                        "q": "A student's `alphabeta` returns the child's narrowed `beta` alongside its value and the parent adopts it. What is the symptom?",
                        "opts": [
                            "Nothing changes: the child's bounds are tighter, and tighter bounds prune more without affecting the value",
                            "The search stops pruning altogether, because alpha and beta cross at the root and the loop breaks at once",
                            "Siblings are cut under a constraint that held only inside the child's subtree, so the value can differ from minimax",
                            "The root value is unchanged but the node count rises, because the parent must re-examine every child of the leaked node",
                        ],
                        "a": 2,
                        "whys": [
                            r"Tighter bounds are only safe when they are true bounds on the node they are applied to. The child's $\beta$ is what *its* minimiser could enforce in *its* subtree; the parent's other children were never subject to it, so cutting them with it is cutting on a false premise.",
                            r"The failure is over-pruning, not under-pruning. A leaked $\beta$ is smaller than the parent's, so more cuts fire, not fewer.",
                            r"The window is a fact about the path from the root to this node. A sibling's subtree has its own minimiser making its own choices, and a bound imported from next door cuts branches that might have been chosen.",
                            r"Adopting a narrower window never causes re-examination; alpha-beta visits each child at most once whatever the window. The count falls, wrongly, and the value can be wrong with it.",
                        ],
                        "why": r"""
The window is passed down and never up. A child narrows its own copies of
$\alpha$ and $\beta$ from what it finds in its own subtree, and those narrowed
values describe constraints the players can enforce *there*. The parent learns
one thing from the child — its value — and updates its own bound from that
alone. Import the child's window and the parent's remaining children are pruned
against constraints that do not apply to them, so branches that minimax would
choose are cut. The lab's depth-by-depth comparison is the test that catches it.
""",
                    },
                    {
                        "q": "Both searches update the running best with `>=` instead of `>`. Which of the lab's tests fails, and why?",
                        "opts": [
                            "The one comparing moves: values agree, but a tying later column overwrites the earlier one in only one of the searches",
                            "The one comparing root values at every depth: a non-strict comparison changes the minimax value itself at some depth",
                            "The one counting nodes: a non-strict comparison prevents any cut from firing, so alpha-beta visits as many nodes as minimax",
                            "The one on terminal boards: a non-strict comparison lets a finished position return a move instead of `None`",
                        ],
                        "a": 0,
                        "whys": [
                            r"Minimax sees every column and lets the last tie win; alpha-beta may have cut the later column and keeps the earlier one. Same value, different move, and the move test notices.",
                            r"The value is unaffected: `>=` and `>` produce the same maximum. What changes is *which* index is remembered alongside it.",
                            r"Cuts fire on `alpha >= beta`, which is a different comparison from the running-best update. Pruning proceeds as before; the node count is unchanged.",
                            r"Terminal boards return before any comparison is made — `terminal_value` short-circuits the call. The comparison operator never runs on them.",
                        ],
                        "why": r"""
The running-best update decides which column is *remembered*, not what value is
reported. With `>=`, every column that ties the best replaces it, so minimax —
which examines every column — reports the last tying column. Alpha-beta may
have cut some of those columns and so reports an earlier one. The values agree,
the moves do not, and the lab's requirement that both searches keep the *first*
move achieving the best value is there to make the two comparable at all.
""",
                    },
                    {
                        "q": "What is the horizon effect, in the terms of the lab's depth-limited search?",
                        "opts": [
                            "A forced loss one ply beyond the depth limit is invisible, so the evaluation at the limit calls the position level",
                            "The evaluation grows less accurate as the depth increases, because its errors compound on the way back up towards the root",
                            "Alpha-beta cuts the branch that contains the winning line because the first leaf it examined looked poor",
                            "The tree is far wider at the depth limit than at the root, so nearly all the search time is spent on leaves",
                        ],
                        "a": 0,
                        "whys": [
                            r"The search trusts `evaluate` at the horizon, and `evaluate` counts lines, not threats. A position with a forced win for the opponent next move scores like any other level board, and the search walks into it.",
                            r"Deeper search makes the result *more* reliable, not less: the guesses are made further from the decision and their errors have more chances to cancel. The horizon effect is about what lies beyond the limit, not about accumulation above it.",
                            r"Alpha-beta never cuts a branch that could change the root's value; it is exact. A poor first leaf can only cut a branch the parent would have rejected anyway.",
                            r"That is a fact about tree size — most nodes are leaves — and it is why search cost is measured in leaves. It is not the horizon effect, which is about the leaves being *misjudged*, not numerous.",
                        ],
                        "why": r"""
A depth limit replaces the true value of a live position with a guess, and the
guess is a static score that cannot see what happens next. If the next ply holds
a forced win for one side, the position is not level, whatever `evaluate` says,
and a search that stops there will play as if it were. Searching deeper pushes
the horizon back but never removes it; evaluating unstable positions more
carefully, or extending the search where a capture or a threat is pending, is
how engines cope with what remains.
""",
                    },
                ],
            },
            "lab": {
                "title": "Alpha-beta on Connect-3",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
The game is Connect-3 on a 4 by 4 board with gravity: a move names a column and
the piece falls to the lowest free cell. Three in a row in any direction wins.
`X` moves first and is the **maximiser** throughout; `O` is the minimiser.

The board is a 16-tuple of `"."`, `"X"` and `"O"`, index `row * 4 + col`, with
row 0 at the bottom. The engine below the line in `main.py` is given: `LINES`,
`legal_moves`, `play`, `winner`, `is_full` and `evaluate`. `evaluate` scores a
non-terminal position from X's point of view and is only ever called at the
depth limit.

## What to write

**`terminal_value(board)`** — `WIN` if X has three in a row, `-WIN` if O has,
`0` if the board is full, and `None` when the game is still alive.

**`minimax(board, player, depth, stats)`** — returns `(value, move)`.

- increment `stats["nodes"]` once on entry to every call, before anything else
- a terminal board returns `(terminal_value(board), None)`
- `depth == 0` on a live board returns `(evaluate(board), None)`
- otherwise X maximises and O minimises over `legal_moves(board)` in ascending
  column order, keeping the **first** move that achieves the best value

**`alphabeta(board, player, depth, alpha, beta, stats)`** — the same, plus a
window. After improving the running best, widen `alpha` (for X) or narrow
`beta` (for O), and break out of the loop as soon as `alpha >= beta`.

**`best_move(board, player, depth, prune=True)`** — returns
`(value, move, nodes)` by calling one of the two with a fresh `new_stats()`.

## What you should see

```text
depth 6 from an empty board
  minimax    value 0  move 1  nodes 4949
  alphabeta  value 0  move 1  nodes  964
```

Same value, same move, one fifth of the work. If your two searches disagree on
the root value, the bug is in the window handling, not in the game.
''',
                "files": [{"name": "main.py", "content": r'''
WIDTH = 4
HEIGHT = 4
CONNECT = 3
WIN = 1000
EMPTY = tuple("." * (WIDTH * HEIGHT))


def build_lines():
    """Every straight run of CONNECT cells on the board. Provided."""
    out = []
    for r in range(HEIGHT):
        for c in range(WIDTH):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cells = []
                for k in range(CONNECT):
                    rr, cc = r + dr * k, c + dc * k
                    if 0 <= rr < HEIGHT and 0 <= cc < WIDTH:
                        cells.append(rr * WIDTH + cc)
                if len(cells) == CONNECT:
                    out.append(tuple(cells))
    return tuple(out)


LINES = build_lines()


def legal_moves(board):
    """Columns that are not yet full, ascending. Provided."""
    return [c for c in range(WIDTH) if board[(HEIGHT - 1) * WIDTH + c] == "."]


def play(board, col, player):
    """Drop player into col and return the new board. Provided."""
    for r in range(HEIGHT):
        i = r * WIDTH + col
        if board[i] == ".":
            cells = list(board)
            cells[i] = player
            return tuple(cells)
    raise ValueError("column %d is full" % col)


def winner(board):
    """The player with CONNECT in a row, else None. Provided."""
    for line in LINES:
        a, b, c = (board[i] for i in line)
        if a != "." and a == b == c:
            return a
    return None


def is_full(board):
    """True when no column has room left. Provided."""
    return "." not in board


def evaluate(board):
    """Heuristic score from X's point of view. Provided."""
    score = 0
    for line in LINES:
        cells = [board[i] for i in line]
        x = cells.count("X")
        o = cells.count("O")
        if x and not o:
            score += 1 if x == 1 else 10
        elif o and not x:
            score -= 1 if o == 1 else 10
    return score


def new_stats():
    """A fresh node counter. Provided."""
    return {"nodes": 0}


def other(player):
    """The opponent of player. Provided."""
    return "O" if player == "X" else "X"


def show(board):
    """The board as four text rows, top row first. Provided."""
    return "\n".join("".join(board[r * WIDTH:(r + 1) * WIDTH])
                     for r in range(HEIGHT - 1, -1, -1))


def terminal_value(board):
    """WIN / -WIN / 0 for a finished game, None while it is still alive."""
    # your code here


def minimax(board, player, depth, stats):
    """Full-width minimax -> (value, move). X maximises, O minimises."""
    # your code here


def alphabeta(board, player, depth, alpha, beta, stats):
    """Minimax with an alpha-beta window -> (value, move)."""
    # your code here


def best_move(board, player, depth, prune=True):
    """(value, move, nodes) for one search of this position."""
    # your code here


for _depth in (4, 5, 6):
    print(_depth, best_move(EMPTY, "X", _depth, False), best_move(EMPTY, "X", _depth, True))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
WIDTH = 4
HEIGHT = 4
CONNECT = 3
WIN = 1000
EMPTY = tuple("." * (WIDTH * HEIGHT))


def build_lines():
    """Every straight run of CONNECT cells on the board. Provided."""
    out = []
    for r in range(HEIGHT):
        for c in range(WIDTH):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cells = []
                for k in range(CONNECT):
                    rr, cc = r + dr * k, c + dc * k
                    if 0 <= rr < HEIGHT and 0 <= cc < WIDTH:
                        cells.append(rr * WIDTH + cc)
                if len(cells) == CONNECT:
                    out.append(tuple(cells))
    return tuple(out)


LINES = build_lines()


def legal_moves(board):
    """Columns that are not yet full, ascending. Provided."""
    return [c for c in range(WIDTH) if board[(HEIGHT - 1) * WIDTH + c] == "."]


def play(board, col, player):
    """Drop player into col and return the new board. Provided."""
    for r in range(HEIGHT):
        i = r * WIDTH + col
        if board[i] == ".":
            cells = list(board)
            cells[i] = player
            return tuple(cells)
    raise ValueError("column %d is full" % col)


def winner(board):
    """The player with CONNECT in a row, else None. Provided."""
    for line in LINES:
        a, b, c = (board[i] for i in line)
        if a != "." and a == b == c:
            return a
    return None


def is_full(board):
    """True when no column has room left. Provided."""
    return "." not in board


def evaluate(board):
    """Heuristic score from X's point of view. Provided."""
    score = 0
    for line in LINES:
        cells = [board[i] for i in line]
        x = cells.count("X")
        o = cells.count("O")
        if x and not o:
            score += 1 if x == 1 else 10
        elif o and not x:
            score -= 1 if o == 1 else 10
    return score


def new_stats():
    """A fresh node counter. Provided."""
    return {"nodes": 0}


def other(player):
    """The opponent of player. Provided."""
    return "O" if player == "X" else "X"


def show(board):
    """The board as four text rows, top row first. Provided."""
    return "\n".join("".join(board[r * WIDTH:(r + 1) * WIDTH])
                     for r in range(HEIGHT - 1, -1, -1))


def terminal_value(board):
    """WIN / -WIN / 0 for a finished game, None while it is still alive."""
    won = winner(board)
    if won == "X":
        return WIN
    if won == "O":
        return -WIN
    if is_full(board):
        return 0
    return None


def minimax(board, player, depth, stats):
    """Full-width minimax -> (value, move). X maximises, O minimises."""
    stats["nodes"] += 1
    ended = terminal_value(board)
    if ended is not None:
        return ended, None
    if depth == 0:
        return evaluate(board), None
    best_col = None
    if player == "X":
        best = -10 ** 9
        for col in legal_moves(board):
            value, _ = minimax(play(board, col, player), "O", depth - 1, stats)
            if value > best:                 # strict, so ties keep the first column
                best, best_col = value, col
    else:
        best = 10 ** 9
        for col in legal_moves(board):
            value, _ = minimax(play(board, col, player), "X", depth - 1, stats)
            if value < best:
                best, best_col = value, col
    return best, best_col


def alphabeta(board, player, depth, alpha, beta, stats):
    """Minimax with an alpha-beta window -> (value, move)."""
    stats["nodes"] += 1
    ended = terminal_value(board)
    if ended is not None:
        return ended, None
    if depth == 0:
        return evaluate(board), None
    best_col = None
    if player == "X":
        best = -10 ** 9
        for col in legal_moves(board):
            value, _ = alphabeta(play(board, col, player), "O", depth - 1,
                                 alpha, beta, stats)
            if value > best:
                best, best_col = value, col
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break                        # O already has a cheaper option above
    else:
        best = 10 ** 9
        for col in legal_moves(board):
            value, _ = alphabeta(play(board, col, player), "X", depth - 1,
                                 alpha, beta, stats)
            if value < best:
                best, best_col = value, col
            if best < beta:
                beta = best
            if alpha >= beta:
                break                        # X already has a better option above
    return best, best_col


def best_move(board, player, depth, prune=True):
    """(value, move, nodes) for one search of this position."""
    stats = new_stats()
    if prune:
        value, move = alphabeta(board, player, depth, -10 ** 9, 10 ** 9, stats)
    else:
        value, move = minimax(board, player, depth, stats)
    return value, move, stats["nodes"]


for _depth in (4, 5, 6):
    print(_depth, best_move(EMPTY, "X", _depth, False), best_move(EMPTY, "X", _depth, True))
'''}],
                "hints": [
                    "Count the node before you test for a terminal board — every call is one visited node, including the leaves.",
                    "Use a strict comparison (`>` for X, `<` for O) when updating the running best. A non-strict one would let a later, equally good column overwrite the earlier one and your two searches would disagree on the move.",
                    "The window is passed down but never up: recurse with the current `alpha, beta` and only update your own copies afterwards.",
                    "Check the cut after updating the window, not before, and use `break` rather than `return` so the accumulated best value is the one you hand back.",
                ],
                "tests": [
                    {"name": "terminal_value reads finished games", "code": r'''
_won = play(play(play(EMPTY, 0, "X"), 0, "X"), 0, "X")
assert terminal_value(_won) == WIN, f"three X in column 0 should be {WIN}, got {terminal_value(_won)!r}"
_lost = play(play(play(EMPTY, 1, "O"), 1, "O"), 1, "O")
assert terminal_value(_lost) == -WIN, f"three O should be {-WIN}, got {terminal_value(_lost)!r}"
assert terminal_value(EMPTY) is None, "an empty board is not finished"
_full = tuple(("X", "O")[(i // WIDTH + i) % 2] for i in range(16))
if winner(_full) is None:
    assert terminal_value(_full) == 0, f"a full drawn board scores 0, got {terminal_value(_full)!r}"
'''},
                    {"name": "The horizon and the leaves", "code": r'''
_s = new_stats()
_v, _m = minimax(EMPTY, "X", 0, _s)
assert (_v, _m) == (evaluate(EMPTY), None), f"depth 0 should return evaluate(board), got {(_v, _m)!r}"
assert _s["nodes"] == 1, f"one call is one node, got {_s['nodes']}"
_won = play(play(play(EMPTY, 0, "X"), 0, "X"), 0, "X")
_s = new_stats()
assert minimax(_won, "O", 5, _s) == (WIN, None), "a finished game has a value and no move"
assert _s["nodes"] == 1, f"a terminal board must not be expanded, got {_s['nodes']} nodes"
'''},
                    {"name": "Minimax plays the tactics", "code": r'''
_b = EMPTY
for _col, _who in ((0, "X"), (1, "O"), (0, "X"), (1, "O")):
    _b = play(_b, _col, _who)
_v, _m = minimax(_b, "X", 1, new_stats())
assert (_v, _m) == (WIN, 0), f"X has two in column 0 and can win at once; got {(_v, _m)!r}"
_b2 = play(play(play(EMPTY, 0, "X"), 1, "O"), 0, "X")
_v2, _m2 = minimax(_b2, "O", 4, new_stats())
assert _m2 == 0, f"O must block column 0, played {_m2!r}"
assert _v2 < WIN, f"after the block X is not winning by force, value was {_v2!r}"
'''},
                    {"name": "Alpha-beta returns the minimax value", "code": r'''
for _depth in range(1, 7):
    _sm, _sa = new_stats(), new_stats()
    _vm, _mm = minimax(EMPTY, "X", _depth, _sm)
    _va, _ma = alphabeta(EMPTY, "X", _depth, -10 ** 9, 10 ** 9, _sa)
    assert _vm == _va, f"depth {_depth}: minimax {_vm}, alphabeta {_va} — pruning must be exact"
    assert _mm == _ma, f"depth {_depth}: minimax chose {_mm}, alphabeta chose {_ma}"
'''},
                    {"name": "Alpha-beta on a midgame position", "code": r'''
_b = play(play(play(EMPTY, 0, "X"), 1, "O"), 0, "X")
for _depth in (2, 3, 4):
    _vm, _mm = minimax(_b, "O", _depth, new_stats())
    _va, _ma = alphabeta(_b, "O", _depth, -10 ** 9, 10 ** 9, new_stats())
    assert (_vm, _mm) == (_va, _ma), \
        f"depth {_depth}: minimax {(_vm, _mm)!r} vs alphabeta {(_va, _ma)!r}"
'''},
                    {"name": "Pruning cuts the tree hard", "code": r'''
_sm, _sa = new_stats(), new_stats()
minimax(EMPTY, "X", 6, _sm)
alphabeta(EMPTY, "X", 6, -10 ** 9, 10 ** 9, _sa)
assert _sa["nodes"] < _sm["nodes"], \
    f"alphabeta visited {_sa['nodes']} nodes, minimax {_sm['nodes']} — no pruning happened"
assert _sa["nodes"] * 3 < _sm["nodes"], \
    f"expected roughly a fifth of {_sm['nodes']} nodes, got {_sa['nodes']}"
assert _sm["nodes"] > 4000, f"full-width depth 6 should visit thousands of nodes, got {_sm['nodes']}"
'''},
                    {"name": "best_move reports value, move and cost", "code": r'''
_vp, _mp, _np = best_move(EMPTY, "X", 5, True)
_vf, _mf, _nf = best_move(EMPTY, "X", 5, False)
assert (_vp, _mp) == (_vf, _mf), f"pruned {(_vp, _mp)!r} but full-width {(_vf, _mf)!r}"
assert _np < _nf, f"the pruned search reported {_np} nodes and the full one {_nf}"
assert _mp in legal_moves(EMPTY), f"move {_mp!r} is not a legal column"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Markov decision processes",
            "summary": "Known dynamics, stochastic outcomes: value iteration, policy iteration, and a certificate.",
            "concepts": [
                "An MDP is (S, A, P, R, gamma); the Markov property is what makes a state sufficient",
                "The Bellman optimality equation U(s) = R(s) + gamma max_a sum_s' P(s'|s,a) U(s')",
                "Value iteration is the Bellman backup applied as a fixed-point iteration; it is a contraction for gamma < 1",
                "Policy evaluation solves a linear system — iteratively here — for a fixed policy",
                "Policy iteration alternates evaluation and greedy improvement, and terminates because the policy space is finite",
                "The policy improvement theorem: acting greedily with respect to U^pi is never worse than pi",
                "The Bellman residual max_s |U(s) - backup(U)(s)| is a certificate you can check after the fact",
            ],
            "read": [
                {
                    "title": "An equation that grades its own answer",
                    "minutes": 12,
                    "body": r'''
A robot sits in the bottom-left corner of a room laid out as a grid four squares
wide and three high. The square at the top right pays +1 and ends the run; the
square directly beneath it pays −1 and ends the run too. One square in the
middle is a pillar. Every other square costs a little to stand on, −0.04, which
is the price of the electricity. The robot's wheels are not reliable: told to go
north, it goes north eight times out of ten, and one time in ten it slides west,
one time in ten east. Pushing into a wall or the pillar leaves it where it was.

```text
 row 3   .     .     .    +1
 row 2   .    ###    .    -1
 row 1   .     .     .     .
        col 1 col 2 col 3 col 4
```

The question is not "what is the shortest path". There is no path, because the
robot cannot follow one; every step is a gamble. The question is: from each
square, which direction should it push, and what is each square *worth* given
that it will push well from then on? That second question turns out to be the
one that answers the first.

## What a square is worth

Start with a definition that is nothing but bookkeeping. The worth of a square
is the total reward the robot can expect to collect from there until the run
ends, assuming it acts as well as it can. Call it $U(s)$. For the two terminal
squares there is nothing to decide: $U(4,3) = 1$ and $U(4,2) = -1$, because you
collect the payout and the run stops.

For any other square, split the total into the reward for being on this square
now and everything that comes after. The reward now is $R(s) = -0.04$. What
comes after depends on which way the robot pushes and where it actually lands.
If it pushes in direction $a$, it lands on $s'$ with probability
$P(s' \mid s, a)$, and from $s'$ it collects, by the same definition, $U(s')$.
So the expected total from pushing $a$ is
$R(s) + \sum_{s'} P(s' \mid s, a)\, U(s')$, and the robot pushes in whichever
direction makes that largest:

$$U(s) = R(s) + \gamma \max_a \sum_{s'} P(s' \mid s, a)\, U(s')$$

The $\gamma$ is a discount, a number in $(0, 1]$ that scales down rewards one
step further into the future. In this room $\gamma = 1$ and the run always
ends, so the discount does no work here, but it will matter below. This is the
Bellman optimality equation, and it was not announced: it fell out of writing
"the reward now, plus the expected worth of wherever you land" and letting the
robot choose. The pieces it needs — the states, the actions, the transition
probabilities $P$, the rewards $R$, and $\gamma$ — are the five things that
define a *Markov decision process*.

The word Markov is the assumption that the square the robot is on is all you
need to know: where it came from, how many steps it has taken, and what it was
told last time do not change what happens next. If they did, the square would
not be a state, and $U(s)$ would not be a single number. The lab in this module,
*The 4x3 world, solved twice*, is built so that the state really is the square,
and everything below depends on it.

## One backup, by hand

The equation defines $U$ in terms of itself, which is not a formula you can
evaluate. But you can check it at one square once you have the answer. Here is
the answer for this room, which the block further down computes:

```text
 0.812  0.868  0.918  +1.000
 0.762   ####  0.660  -1.000
 0.705  0.655  0.611   0.388
```

Take square (3, 3), the one to the left of the +1. Push east: with 0.8 you land
on the +1, worth 1.0; with 0.1 you slide north, hit the wall, and stay on
(3, 3), worth 0.918; with 0.1 you slide south to (3, 2), worth 0.660. The
expected worth of where you land is
$0.8 \times 1.0 + 0.1 \times 0.918 + 0.1 \times 0.660 = 0.9578$. Add the
$-0.04$ for standing here and you get $0.9178$, which is the 0.918 in the table.
Now push north instead: with 0.8 you bump the wall and stay, 0.918; with 0.1
you slide west to (2, 3), 0.868; with 0.1 you slide east onto the +1. That is
$0.7344 + 0.0868 + 0.1 = 0.9212$, minus 0.04 is 0.881, worse than east. So east
is the action, and the table's 0.918 agrees with itself.

The more interesting square is (3, 1), under the pillar's right-hand neighbour
and two steps from the −1. Pushing north gives
$0.8 \times 0.660 + 0.1 \times 0.655 + 0.1 \times 0.388 - 0.04 = 0.592$.
Pushing west, away from everything, gives
$0.8 \times 0.655 + 0.1 \times 0.660 + 0.1 \times 0.611 - 0.04 = 0.611$. West
wins, by 0.019, and that is the number in the table. The robot walks the long
way round the room rather than passing between the pillar and the −1, and
nobody told it to; the expected values of the two routes told it. The lab's
policy test checks exactly this square.

## Turning the equation into an algorithm

If you had $U$ you could check it. You do not have it. So guess — zero
everywhere, terminals at their payouts — and apply the right-hand side of the
equation to the guess to get a better guess. Repeat. This is *value iteration*,
and each pass over the states is a *sweep*; each sweep applies the *Bellman
backup* to every non-terminal square using the values from the previous sweep.

```python
WALL = (2, 2)
TERMINAL = {(4, 3): 1.0, (4, 2): -1.0}
STEP = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}
SLIPS = {"N": ("W", "E"), "E": ("N", "S"), "S": ("E", "W"), "W": ("S", "N")}
STATES = [(c, r) for c in range(1, 5) for r in range(1, 4) if (c, r) != WALL]


def move(s, a):
    nxt = (s[0] + STEP[a][0], s[1] + STEP[a][1])
    if nxt == WALL or not (1 <= nxt[0] <= 4 and 1 <= nxt[1] <= 3):
        return s
    return nxt


def expected(V, s, a):
    left, right = SLIPS[a]
    return 0.8 * V[move(s, a)] + 0.1 * V[move(s, left)] + 0.1 * V[move(s, right)]


V = {s: TERMINAL.get(s, 0.0) for s in STATES}
sweeps = 0
while True:
    sweeps += 1
    new = dict(V)
    for s in STATES:
        if s not in TERMINAL:
            new[s] = -0.04 + max(expected(V, s, a) for a in STEP)
    delta = max(abs(new[s] - V[s]) for s in STATES)
    V = new
    if delta < 1e-10:
        break

print("sweeps", sweeps)
for r in (3, 2, 1):
    print(" ".join("  ####" if (c, r) == WALL else f"{V[(c, r)]:6.3f}" for c in range(1, 5)))
print("one more backup at (3,3):", round(-0.04 + expected(V, (3, 3), "E"), 3))
```

It prints `sweeps 40`, then the three rows of the table above, then
`one more backup at (3,3): 0.918` — the hand calculation, done by the machine
on the converged values, gives back the value it started from. The loop stops
when the largest change in a sweep falls below $10^{-10}$, and it stops because
the backup is a *contraction*: for $\gamma < 1$ it shrinks the distance between
any two value functions by at least a factor $\gamma$ per sweep, so from any
starting guess the sweeps converge to the one fixed point, which is the solution
of the equation. With $\gamma = 1$ that argument needs a substitute — here, that
every run ends at a terminal with probability 1 — and it still converges, in
forty sweeps.

Notice the `new = dict(V)`. Each sweep reads the *old* values and writes a fresh
table, and the swap happens at the end. Updating in place, so that a square
backed up late in the sweep sees its neighbours' already-updated values, is also
correct — it is Gauss–Seidel iteration and it converges faster — but it does not
converge in the same number of sweeps, and the lab counts sweeps. Write it the
way the brief says and the counts will match.

## The same problem, solved the other way round

Value iteration hunts for values and reads a policy off them at the end: at each
square, the action that maximises the backup, which the lab calls
`greedy_policy`. *Policy iteration* turns this inside out. Fix a policy $\pi$ —
any policy; the lab starts with "push north everywhere". Evaluate it: the same
sweep as before, but with the $\max_a$ replaced by the one action $\pi(s)$
names, so it is a linear system rather than an optimisation, and it converges to
$U^\pi$, the worth of each square *under that policy*. Then improve it: at each
square, choose the action that is greedy with respect to $U^\pi$. Then evaluate
the new policy, and so on, until a round changes nothing.

Two facts make this work. Acting greedily with respect to $U^\pi$ produces a
policy that is at least as good as $\pi$ at every state — the *policy
improvement theorem*, whose proof is that switching to the greedy action at one
state can only raise the expected total, and switching everywhere is a sequence
of such steps. And there are finitely many policies — $4^9$ in this room — so a
strictly improving sequence has to stop, and when it stops the policy is greedy
with respect to its own values, which is the Bellman optimality equation, so the
values are $U^*$. The lab's test that the always-south policy is worth no more
than the optimum at any square, and that one greedy improvement step beats it,
is the improvement theorem made concrete.

Both algorithms land on the same policy. Policy iteration usually takes a
handful of rounds where value iteration takes tens of sweeps, and each of its
rounds is more expensive; which is faster depends on the problem, which is why
the lab has you write both.

## A certificate

The Bellman equation gives something unusual: a way to check an answer without
knowing the answer. For any proposed $U$, compute the backup at every
non-terminal square and take the largest gap:

$$\text{residual}(U) = \max_s \left| U(s) - \left( R(s) + \gamma \max_a \sum_{s'} P(s' \mid s, a)\, U(s') \right) \right|$$

For the true $U^*$ this is zero. For the output of a solve that stopped with
$\delta < 10^{-10}$ it is of that order. Corrupt one entry — set $U(1,1)$ to 0 —
and the residual at that square jumps to about 0.7, because the backup from its
neighbours still says 0.705. The lab's `bellman_residual` is this number, and
its test that a broken table produces a residual above 0.5 is the point of
writing it: a solver that returns a table and a residual can be trusted by
someone who never reads the solver.

## The mistake, and why it is tempting

The one that costs the most time is treating the terminal squares as ordinary.
They have a reward, and the equation has a reward term, so it seems natural to
back them up too: $U(4,3) = 1 + \max_a \ldots$. But the run *stops* there. There
is no next square, the sum over $s'$ is empty, and the value is the payout and
nothing more. Back a terminal up and it accumulates its own reward every sweep —
with $\gamma = 1$ it grows without bound, and every square that can reach it
follows. The lab's `transitions` returns `[]` for a terminal so that no backup
can be written for one, and `value_iteration` skips them by name as well.

A subtler one is the living reward. It is −0.04 in this room and it is what
makes the long way round from (3, 1) a real decision: each extra step costs
something, and the question is whether the 10% chance of sliding towards the −1
is worth more than a few steps of electricity. Set the living reward to 0 and
every square becomes worth reaching the +1 eventually, the robot dawdles, and
the policy goes indifferent in places where it should not. Set it to −2 and the
robot dives for the −1 to end its suffering. The reward function is not a
detail of the problem; it *is* the problem, and a policy that looks wrong is
often a reward that says something you did not mean.

## Where it stops holding

Everything here needed $P$ and $R$ in hand: the backup sums over next states
with known probabilities. In the next module the robot will have to find out
what its wheels do by driving, and the same equation will be estimated from
samples rather than computed from a table. The discount also needed care. With
$\gamma = 1$ and no guarantee of reaching a terminal — a room with a corner the
robot can never leave, or a task that never ends — the values are infinite and
the contraction argument has nothing to contract. Discounting fixes that at the
price of making the far future matter less, which the lab's last test shows: at
$\gamma = 0.5$ the +1 is worth far less from the far corner, and the values
shrink accordingly.

And the table is a table. Nine non-terminal squares fit; a robot whose state is
a continuous position and velocity has no rows to write in, and the backup over
$s'$ becomes an integral nobody can evaluate. That is where function
approximation enters, later in the track. For now the room is small, the model
is known, and the equation grades its own answer.
''',
                },
            ],
            "quiz": {
                "title": "Backups, fixed points and the residual",
                "minutes": 8,
                "questions": [
                    {
                        "q": "From (3, 1), pushing west is worth 0.611 and pushing north 0.592, so the robot goes the long way round. What is the 0.019 made of?",
                        "opts": [
                            "The chance of sliding towards the −1 on the north route outweighs the electricity spent on the extra steps west",
                            "The pillar blocks the north route from (3, 1), so the robot has to go west whatever the values say",
                            "Pushing north has a one-in-ten chance of landing on the −1 directly, and the west route has none",
                            "West keeps the robot near the start with probability 0.9, and standing still costs less than moving around the room",
                        ],
                        "a": 0,
                        "whys": [
                            r"North reaches (3, 2), a square from which slips can land on the −1; west reaches (2, 1), from which nothing can. Each extra step west costs 0.04, and the values say the risk is worth more than that.",
                            r"The pillar is at (2, 2), not above (3, 1). North from (3, 1) leads to (3, 2), an open square; the model does not forbid it, the values merely prefer the alternative.",
                            r"A north push from (3, 1) lands north, west or east — on (3, 2), (2, 1) or (4, 1). The −1 is at (4, 2), two moves away, not one; the danger is indirect, through (3, 2).",
                            r"Standing still still costs −0.04 per step, the same as moving, and from (3, 1) a west push lands on (2, 1) with probability 0.8, not on (3, 1). The value is about where the routes lead, not about staying put.",
                        ],
                        "why": r"""
The two routes to the +1 differ in what a slip can do. The route through
(3, 2) passes a square where a 10% slide lands on the −1 and ends the run;
the route round the left of the pillar never passes such a square, but it is
a few steps longer, and each step costs 0.04. The Bellman backup prices both
into a single number per action, and at (3, 1) the safer route comes out
0.019 ahead. Change the living reward and that verdict can flip, which is why
the reward function is the problem and not a detail of it.
""",
                    },
                    {
                        "q": "Why must the terminal squares be excluded from the backup, rather than treated like any other square with a reward?",
                        "opts": [
                            "A terminal's value is unknown until the sweep converges, so backing it up early biases the neighbours",
                            "A terminal has no next state, so its worth is its payout alone; backing it up adds the payout again on every sweep",
                            "Backing up a terminal is harmless when gamma is below one, and the lab skips them only to save time",
                            "The terminal's reward is already carried in the neighbours' living reward, so backing it up would count it twice over",
                        ],
                        "a": 1,
                        "whys": [
                            r"A terminal's value is known from the start: it is the payout, and it never changes. That is why the lab's `initial_values` writes it in before the first sweep.",
                            r"The run stops on the terminal. There is no landing square to sum over, so the equation for it collapses to $U = R$, and any backup written for it is adding a term that does not exist.",
                            r"With $\gamma < 1$ the value would settle at $R / (1 - \gamma)$ rather than diverge, which is still wrong — 20 for the +1 at $\gamma = 0.95$ — and every square that reaches it inherits the error.",
                            r"The living reward is the cost of standing on an ordinary square and has nothing to do with the terminal payout. The two are separate entries in $R$, and neither includes the other.",
                        ],
                        "why": r"""
The Bellman equation says: reward now, plus the expected worth of where you
land next. On a terminal there is no next. Its worth is its payout, full stop,
and the sum over successors is empty. Write a backup for it anyway and the
payout is added once per sweep on top of itself: with $\gamma = 1$ it grows
without limit, and with $\gamma < 1$ it settles at a wrong value, and either
way the neighbours that bootstrap from it are poisoned. The lab returns `[]`
from `transitions` for a terminal so that no such backup can be formed.
""",
                    },
                    {
                        "q": "With gamma below one, value iteration converges from any starting table. What is the argument?",
                        "opts": [
                            "Each sweep shrinks the gap between any two tables by a factor gamma, so every start closes in on one fixed point",
                            "The policy space is finite, so the sweeps must eventually repeat a greedy policy and the loop terminates at that point",
                            "Every sweep raises every value, and the values are bounded above by the largest reward available",
                            "The living reward is negative, so the values fall on every sweep until they reach the terminal payouts",
                        ],
                        "a": 0,
                        "whys": [
                            r"The backup is a contraction: apply it to two different tables and the largest gap between them shrinks by at least $\gamma$. Repeated contraction has one fixed point and reaches it from anywhere.",
                            r"That is the termination argument for *policy* iteration, where a policy is improved each round. Value iteration never fixes a policy; its sweeps update numbers, and the numbers converge because of the contraction, not because they cycle.",
                            r"Values can go up or down between sweeps depending on the starting guess; a table initialised too high comes *down*. Monotone growth is not the mechanism, and a bound above is not what makes a sequence converge.",
                            r"Values need not fall — in the lab they rise from zero towards the +1. The sign of the living reward shapes the answer, not the convergence.",
                        ],
                        "why": r"""
Take any two value tables and apply one Bellman backup to each. The largest
difference between the results is at most $\gamma$ times the largest difference
before, because the backup is an expectation (which cannot amplify a
difference) scaled by $\gamma$ (which shrinks it). A map that shrinks distances
by a fixed factor has exactly one fixed point and every starting point converges
to it. With $\gamma = 1$ the factor is 1 and the argument needs help — in the
lab's room, the guarantee that every run ends — but the lab still converges in
tens of sweeps.
""",
                    },
                    {
                        "q": "Policy iteration alternates evaluation and greedy improvement. Why is it guaranteed to stop, and at the optimum?",
                        "opts": [
                            "Evaluation returns the optimal values whatever the policy is, so a single round is always sufficient",
                            "Each round halves the Bellman residual of the values, so it drops below the stopping threshold after a predictable number of rounds",
                            "Greedy improvement never lowers any state's value and there are finitely many policies, so the improvement must end",
                            "The policy changes at exactly one state per round, so it stops after at most one round for each state",
                        ],
                        "a": 2,
                        "whys": [
                            r"Evaluation returns $U^\pi$, the worth of the room *under that policy* — the always-north policy evaluates to something much worse than the optimum. Improvement is what moves it.",
                            r"No halving is involved. Policy iteration stops when the policy stops changing, which is a discrete event, and the residual of the final values is near zero because the final policy is greedy with respect to them.",
                            r"The improvement theorem says the greedy policy is at least as good everywhere; if it differs, it is strictly better somewhere; and $4^9$ policies cannot strictly improve forever. When it stops, the policy is greedy for its own values, which is the optimality equation.",
                            r"Improvement can change any number of states in one round — the first round from all-north typically changes several. The bound on rounds comes from the finite number of policies, not from one state at a time.",
                        ],
                        "why": r"""
Two facts do all the work. Acting greedily with respect to a policy's own values
is never worse than that policy at any state, and is strictly better somewhere
unless the policy is already greedy for its values. And there are only finitely
many policies. A sequence that strictly improves through a finite set must
stop, and the only place it can stop is a policy that is greedy with respect to
its own values — which is exactly what the Bellman optimality equation says of
the optimal policy. The lab's always-south test is the first fact measured.
""",
                    },
                    {
                        "q": "What does `bellman_residual` tell you that the sweep loop's own stopping test does not?",
                        "opts": [
                            "It is the change between the last two sweeps of the solve, so it reports whether the loop exited on the threshold or on max_iter",
                            "It is the discount times the largest value, so it confirms that gamma was applied at every sweep",
                            "It counts the states whose greedy action changed in the final improvement step of the solve",
                            "It measures how far a table is from satisfying its own equation, so a corrupted entry shows without knowing the truth",
                        ],
                        "a": 3,
                        "whys": [
                            r"The stopping test compares consecutive sweeps and lives inside the solver. The residual is computed afterwards, on any table from anywhere, and the lab checks it on a table the solver never produced.",
                            r"There is no such identity. The residual is a gap between a value and its own backup, and for a correct table it is near zero whatever $\gamma$ is.",
                            r"That is a description of policy iteration's termination check, which counts policy changes. The residual is about values, and it is nonzero for a table that is wrong even if the greedy policy read off it happens to be right.",
                            r"Re-run one backup on the table and compare it with the table. The true solution reproduces itself; anything else does not, and the size of the mismatch is the certificate.",
                        ],
                        "why": r"""
The Bellman equation is a fixed-point condition: the true values, backed up
once, give the true values back. That makes it checkable by anyone holding a
table — compute one backup, subtract, take the largest gap. The solver's own
stopping test only says the solver stopped; the residual says whether what it
stopped on is a solution. Set one entry to zero and the residual jumps to 0.7
though the loop would have reported convergence a moment earlier. That is why
the lab has you return both.
""",
                    },
                    {
                        "q": "A student updates the value table in place during a sweep instead of building it from a snapshot. What happens?",
                        "opts": [
                            "It diverges, because a square can read a neighbour's value from the future and feed it straight back",
                            "It still converges, usually in fewer sweeps, but the sweep count differs, so the lab's expected counts no longer match",
                            "It converges to a different fixed point, since the order in which the squares are updated changes the equation being solved",
                            "It is the only correct form; the snapshot version counts the living reward twice per sweep",
                        ],
                        "a": 1,
                        "whys": [
                            r"In-place updating is Gauss–Seidel iteration, and for a contraction it converges too — faster, if anything, since later squares see fresher values. Nothing about it feeds back a wrong value; it feeds back a *newer* one.",
                            r"Both forms reach the same values; the difference is the path taken and the number of sweeps it takes to get there.",
                            r"The fixed point is a property of the equation, not of the update order. Any order that keeps applying the backup ends at the same $U^*$.",
                            r"The snapshot version adds the living reward once per backup, as it should. There is no double counting; the two forms differ only in which values a backup reads.",
                        ],
                        "why": r"""
Reading the old table and writing a fresh one is Jacobi iteration; reading
values that were updated earlier in the same sweep is Gauss–Seidel. Both are
applications of a contraction and both converge to the same fixed point. They
take different routes, and Gauss–Seidel usually arrives sooner. The lab asks
for the snapshot form because it counts sweeps and states a range for them;
the in-place form is not wrong, it is a different experiment.
""",
                    },
                ],
            },
            "lab": {
                "title": "The 4x3 world, solved twice",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
The textbook 4 by 3 gridworld. Columns run 1 to 4 left to right, rows 1 to 3
bottom to top. `(2, 2)` is a wall. `(4, 3)` pays `+1` and `(4, 2)` pays `-1`;
both end the episode. Every other state pays `-0.04` per visit.

Motion is unreliable: the intended direction happens with probability `0.8`,
and each perpendicular direction with probability `0.1`. A move into a wall or
off the board leaves the agent where it was.

The value of a non-terminal state is

```text
U(s) = R(s) + gamma * max over a of  sum over s' of  P(s' | s, a) * U(s')
```

and a terminal state is simply worth its own reward.

## What to write

**`transitions(state, action)`** — a **sorted list** of `(next_state, prob)`
pairs. Merge duplicates: from `(1, 1)` going `W`, the intended move and one of
the slips both leave you where you are, so `(1, 1)` appears once with `0.9`.
A terminal state has no transitions at all, so return `[]`.

**`q_value(V, state, action, gamma)`** — the expected `sum P * V(s')` for one
action. Note this is the sucessor term only; the reward is added by the caller.

**`value_iteration(gamma, theta, max_iter)`** — sweep until the largest change
in a sweep drops below `theta`. Returns `(V, sweeps)`. Terminal states hold
their reward and are never backed up.

**`greedy_policy(V, gamma)`** — `{state: action}` for the non-terminal states,
ties broken by the order in `ACTIONS`.

**`policy_evaluation(policy, gamma, theta, max_iter)`** — the same sweep with
`max` replaced by the action the policy names. Returns `V`.

**`policy_iteration(gamma)`** — start from the all-`"N"` policy, alternate
evaluation and greedy improvement, stop when the policy stops changing.
Returns `(policy, V, rounds)`.

**`bellman_residual(V, gamma)`** — the largest one-sided violation of the
equation above, over the non-terminal states. A correct solve gives something
near machine epsilon.

## Expected result at gamma = 1.0

```text
 0.812  0.868  0.918  +1.000
 0.762   ####  0.660  -1.000
 0.705  0.655  0.611   0.388
```

Both algorithms must land on the same policy, and it should send the agent the
long way round the `-1` square from `(3, 1)`.
''',
                "files": [{"name": "main.py", "content": r'''
WIDTH, HEIGHT = 4, 3
WALLS = {(2, 2)}
TERMINALS = {(4, 3): 1.0, (4, 2): -1.0}
LIVING_REWARD = -0.04
ACTIONS = ("N", "E", "S", "W")
STEP = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}
LEFT_OF = {"N": "W", "W": "S", "S": "E", "E": "N"}
RIGHT_OF = {"N": "E", "E": "S", "S": "W", "W": "N"}
INTENDED_P = 0.8
SIDE_P = 0.1


def states():
    """Every cell that is not a wall. Provided."""
    return [(c, r) for c in range(1, WIDTH + 1) for r in range(1, HEIGHT + 1)
            if (c, r) not in WALLS]


def is_terminal(state):
    """True for the two absorbing squares. Provided."""
    return state in TERMINALS


def reward(state):
    """R(s): the payout for being in this square. Provided."""
    return TERMINALS.get(state, LIVING_REWARD)


def move(state, action):
    """Where a deterministic step would land, walls and edges included. Provided."""
    dc, dr = STEP[action]
    nxt = (state[0] + dc, state[1] + dr)
    if not (1 <= nxt[0] <= WIDTH and 1 <= nxt[1] <= HEIGHT) or nxt in WALLS:
        return state
    return nxt


def initial_values():
    """Zero everywhere, except terminals which hold their reward. Provided."""
    V = {s: 0.0 for s in states()}
    for s in TERMINALS:
        V[s] = TERMINALS[s]
    return V


def transitions(state, action):
    """Sorted [(next_state, prob)] with duplicates merged; [] for a terminal."""
    # your code here


def q_value(V, state, action, gamma):
    """The expected successor value sum P(s'|s,a) * V(s')."""
    # your code here


def value_iteration(gamma=1.0, theta=1e-10, max_iter=1000):
    """(V, sweeps) from repeated Bellman optimality backups."""
    # your code here


def greedy_policy(V, gamma=1.0):
    """{state: action} greedy with respect to V, ties by ACTIONS order."""
    # your code here


def policy_evaluation(policy, gamma=1.0, theta=1e-12, max_iter=2000):
    """V for a fixed policy."""
    # your code here


def policy_iteration(gamma=1.0):
    """(policy, V, rounds) from evaluate-then-improve, starting from all N."""
    # your code here


def bellman_residual(V, gamma=1.0):
    """The largest violation of the Bellman optimality equation."""
    # your code here


V, sweeps = value_iteration()
print("sweeps", sweeps)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
WIDTH, HEIGHT = 4, 3
WALLS = {(2, 2)}
TERMINALS = {(4, 3): 1.0, (4, 2): -1.0}
LIVING_REWARD = -0.04
ACTIONS = ("N", "E", "S", "W")
STEP = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}
LEFT_OF = {"N": "W", "W": "S", "S": "E", "E": "N"}
RIGHT_OF = {"N": "E", "E": "S", "S": "W", "W": "N"}
INTENDED_P = 0.8
SIDE_P = 0.1


def states():
    """Every cell that is not a wall. Provided."""
    return [(c, r) for c in range(1, WIDTH + 1) for r in range(1, HEIGHT + 1)
            if (c, r) not in WALLS]


def is_terminal(state):
    """True for the two absorbing squares. Provided."""
    return state in TERMINALS


def reward(state):
    """R(s): the payout for being in this square. Provided."""
    return TERMINALS.get(state, LIVING_REWARD)


def move(state, action):
    """Where a deterministic step would land, walls and edges included. Provided."""
    dc, dr = STEP[action]
    nxt = (state[0] + dc, state[1] + dr)
    if not (1 <= nxt[0] <= WIDTH and 1 <= nxt[1] <= HEIGHT) or nxt in WALLS:
        return state
    return nxt


def initial_values():
    """Zero everywhere, except terminals which hold their reward. Provided."""
    V = {s: 0.0 for s in states()}
    for s in TERMINALS:
        V[s] = TERMINALS[s]
    return V


def transitions(state, action):
    """Sorted [(next_state, prob)] with duplicates merged; [] for a terminal."""
    if is_terminal(state):
        return []
    weights = {}
    for prob, act in ((INTENDED_P, action), (SIDE_P, LEFT_OF[action]),
                      (SIDE_P, RIGHT_OF[action])):
        nxt = move(state, act)
        weights[nxt] = weights.get(nxt, 0.0) + prob
    return sorted(weights.items())


def q_value(V, state, action, gamma):
    """The expected successor value sum P(s'|s,a) * V(s')."""
    return sum(prob * V[nxt] for nxt, prob in transitions(state, action))


def value_iteration(gamma=1.0, theta=1e-10, max_iter=1000):
    """(V, sweeps) from repeated Bellman optimality backups."""
    V = initial_values()
    for sweep in range(1, max_iter + 1):
        delta = 0.0
        updated = dict(V)
        for s in states():
            if is_terminal(s):
                continue
            best = max(q_value(V, s, a, gamma) for a in ACTIONS)
            updated[s] = reward(s) + gamma * best
            delta = max(delta, abs(updated[s] - V[s]))
        V = updated
        if delta < theta:
            return V, sweep
    return V, max_iter


def greedy_policy(V, gamma=1.0):
    """{state: action} greedy with respect to V, ties by ACTIONS order."""
    policy = {}
    for s in states():
        if is_terminal(s):
            continue
        best_a, best_q = None, None
        for a in ACTIONS:
            q = q_value(V, s, a, gamma)
            if best_q is None or q > best_q:   # strict: first action wins a tie
                best_a, best_q = a, q
        policy[s] = best_a
    return policy


def policy_evaluation(policy, gamma=1.0, theta=1e-12, max_iter=2000):
    """V for a fixed policy."""
    V = initial_values()
    for _ in range(max_iter):
        delta = 0.0
        updated = dict(V)
        for s in states():
            if is_terminal(s):
                continue
            updated[s] = reward(s) + gamma * q_value(V, s, policy[s], gamma)
            delta = max(delta, abs(updated[s] - V[s]))
        V = updated
        if delta < theta:
            break
    return V


def policy_iteration(gamma=1.0):
    """(policy, V, rounds) from evaluate-then-improve, starting from all N."""
    policy = {s: "N" for s in states() if not is_terminal(s)}
    V = initial_values()
    for rounds in range(1, 200):
        V = policy_evaluation(policy, gamma)
        improved = greedy_policy(V, gamma)
        if improved == policy:
            return policy, V, rounds
        policy = improved
    return policy, V, 200


def bellman_residual(V, gamma=1.0):
    """The largest violation of the Bellman optimality equation."""
    worst = 0.0
    for s in states():
        if is_terminal(s):
            continue
        best = max(q_value(V, s, a, gamma) for a in ACTIONS)
        worst = max(worst, abs(V[s] - (reward(s) + gamma * best)))
    return worst


V, sweeps = value_iteration()
print("sweeps", sweeps)
for row in range(HEIGHT, 0, -1):
    print(" ".join("  ####" if (col, row) in WALLS else f"{V[(col, row)]:6.3f}"
                   for col in range(1, WIDTH + 1)))
print("residual", bellman_residual(V))
'''}],
                "hints": [
                    "Accumulate the three outcomes into a dict keyed by next state, then `sorted(weights.items())` — that merges the duplicates and fixes the order in one step.",
                    "Back up from a snapshot: build the new value dict from the old one, and only swap it in at the end of the sweep. Updating in place gives Gauss-Seidel, which converges but not to the sweep counts the checks expect.",
                    "`policy_evaluation` is `value_iteration` with `max(... for a in ACTIONS)` replaced by the single action `policy[s]`. Write it that way and the two cannot drift apart.",
                    "`bellman_residual` re-runs one backup and compares it with what you already have — if it is not tiny, your sweep loop exited too early.",
                ],
                "tests": [
                    {"name": "transitions are merged, sorted and normalised", "code": r'''
assert transitions((4, 3), "N") == [], "a terminal square has no transitions"
assert transitions((4, 2), "W") == [], "a terminal square has no transitions"
for _s in states():
    if is_terminal(_s):
        continue
    for _a in ACTIONS:
        _t = transitions(_s, _a)
        _tot = sum(p for _n, p in _t)
        assert abs(_tot - 1.0) < 1e-9, f"transitions({_s}, {_a!r}) sum to {_tot}, not 1"
        _seen = [n for n, _p in _t]
        assert len(_seen) == len(set(_seen)), f"transitions({_s}, {_a!r}) repeats a state: {_t!r}"
        assert _seen == sorted(_seen), f"transitions({_s}, {_a!r}) is not sorted: {_t!r}"
assert transitions((1, 1), "W") == [((1, 1), 0.9), ((1, 2), 0.1)], \
    f"from (1,1) going W, got {transitions((1, 1), 'W')!r}"
assert transitions((1, 1), "N") == [((1, 1), 0.1), ((1, 2), 0.8), ((2, 1), 0.1)], \
    f"from (1,1) going N, got {transitions((1, 1), 'N')!r}"
'''},
                    {"name": "Value iteration reproduces the textbook values", "code": r'''
_V, _sweeps = value_iteration()
_want = {(1, 1): 0.705, (1, 2): 0.762, (1, 3): 0.812, (2, 1): 0.655, (2, 3): 0.868,
         (3, 1): 0.611, (3, 2): 0.660, (3, 3): 0.918, (4, 1): 0.388}
for _s, _u in _want.items():
    assert abs(_V[_s] - _u) < 5e-3, f"U{_s} = {_V[_s]:.4f}, expected about {_u}"
assert _V[(4, 3)] == 1.0 and _V[(4, 2)] == -1.0, "terminals keep their own reward"
assert isinstance(_sweeps, int) and 5 < _sweeps < 200, f"sweeps was {_sweeps!r}"
'''},
                    {"name": "The solution certifies itself", "code": r'''
_V, _ = value_iteration()
_res = bellman_residual(_V)
assert _res < 1e-6, f"Bellman residual {_res!r} — the values do not satisfy their own equation"
_broken = dict(_V)
_broken[(1, 1)] = 0.0
assert bellman_residual(_broken) > 0.5, "residual should expose a corrupted value"
'''},
                    {"name": "The greedy policy avoids the pit", "code": r'''
_V, _ = value_iteration()
_pi = greedy_policy(_V)
assert set(_pi) == {_s for _s in states() if not is_terminal(_s)}, \
    "the policy covers exactly the non-terminal states"
_want = {(1, 1): "N", (1, 2): "N", (1, 3): "E", (2, 1): "W", (2, 3): "E",
         (3, 1): "W", (3, 2): "N", (3, 3): "E", (4, 1): "W"}
for _s, _a in _want.items():
    assert _pi[_s] == _a, f"policy at {_s} is {_pi[_s]!r}, expected {_a!r}"
'''},
                    {"name": "Policy iteration lands in the same place", "code": r'''
_V, _ = value_iteration()
_pi = greedy_policy(_V)
_pi2, _V2, _rounds = policy_iteration()
assert _pi2 == _pi, f"policy iteration disagreed:\n{_pi2!r}\nvs\n{_pi!r}"
assert max(abs(_V[_s] - _V2[_s]) for _s in states()) < 1e-6, "the two value functions differ"
assert 1 < _rounds < 20, f"policy iteration took {_rounds!r} rounds — expected a handful"
'''},
                    {"name": "Policy improvement never hurts", "code": r'''
_V, _ = value_iteration()
_bad = {_s: "S" for _s in states() if not is_terminal(_s)}
_Vbad = policy_evaluation(_bad)
for _s in states():
    if is_terminal(_s):
        continue
    assert _Vbad[_s] <= _V[_s] + 1e-9, \
        f"the always-South policy claims {_Vbad[_s]:.4f} at {_s}, beating the optimal {_V[_s]:.4f}"
_Vgreedy = policy_evaluation(greedy_policy(_Vbad))
assert sum(_Vgreedy.values()) > sum(_Vbad.values()), \
    "one greedy improvement step should strictly beat the always-South policy"
'''},
                    {"name": "Discounting changes what is worth reaching", "code": r'''
_V1, _ = value_iteration(gamma=1.0)
_V5, _ = value_iteration(gamma=0.5)
assert _V5[(1, 1)] < _V1[(1, 1)], \
    f"heavy discounting should shrink the far-away prize: {_V5[(1, 1)]:.3f} vs {_V1[(1, 1)]:.3f}"
assert bellman_residual(_V5, 0.5) < 1e-6, "the discounted solve must satisfy its own equation too"
assert _V5[(3, 3)] > _V5[(1, 1)], "states nearer the +1 are worth more under any discount"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Learning from experience",
            "summary": "The same gridworld without a model: temporal-difference control, on-policy and off.",
            "concepts": [
                "Model-free control learns Q(s, a) from sampled transitions, never touching P",
                "The TD error r + gamma * (bootstrap) - Q(s, a) is the entire learning signal",
                "Q-learning bootstraps from max_a' Q(s', a') — off-policy: it evaluates greedy while behaving epsilon-greedy",
                "SARSA bootstraps from Q(s', a') for the action it will actually take — on-policy",
                "Near a hazard the two diverge: SARSA prices in its own exploration, Q-learning does not",
                "Online return during training is not the same measure as the quality of the greedy policy afterwards",
                "Convergence needs every state-action pair visited infinitely often and a decaying step size",
            ],
            "read": [
                {
                    "title": "The TD error is the whole signal",
                    "minutes": 12,
                    "body": r'''
Take the room from the previous module and remove the manual. The robot still
has wheels that slip, but now nobody tells it the probabilities. It cannot write
a backup, because the backup sums over next states with known weights and it
does not know the weights. What it can do is push, see where it lands, see what
that cost, and write down that one experience. The question of this module is
how a stream of those experiences turns into the same table of action values the
previous module computed from the model — and what changes when the thing being
learned is entangled with the way it is being explored.

The room for this module is nastier than the last one. Four rows, twelve
columns. The robot starts at the bottom left and the goal is the bottom right,
and the entire bottom row between them is a cliff: step onto it and you pay −100
and are dragged back to the start, with the episode still running. Every other
step costs −1. The shortest route is thirteen steps along the row directly above
the cliff, and it is also the route where one slip is most expensive.

## From the backup to a sample of it

Write the previous module's equation for the worth of an *action* rather than a
state, since a robot without a model needs to compare actions directly:

$$Q(s, a) = \sum_{s'} P(s' \mid s, a)\left[ r(s, a, s') + \gamma \max_{a'} Q(s', a') \right]$$

The robot cannot compute the sum. But it can *sample* it: push $a$ from $s$,
land on some $s'$, receive $r$. The bracket evaluated at that one landing,
$r + \gamma \max_{a'} Q(s', a')$, is a single draw from a distribution whose
mean is the right-hand side. Call that draw the *target*. If the current
estimate $Q(s, a)$ were correct, targets would scatter around it and average to
it. If it is too low, targets will tend to sit above it. So move the estimate a
fraction of the way towards each target as it arrives:

$$Q(s, a) \leftarrow Q(s, a) + \alpha\left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]$$

The bracket is the *temporal-difference error*: the difference between what one
step of experience suggested and what the table currently claims. It is the
entire learning signal. There is no gradient, no loss function, no model; one
number per step, and the table moves towards it at rate $\alpha$. This update
is *Q-learning*.

Trace the very first step. The table starts at zero everywhere, $\alpha = 0.5$,
$\gamma = 1$. Every action at the start looks equally good, and the tie rule
picks up. Suppose the exploration coin overrides that and the robot pushes right
— into the cliff. It receives $r = -100$ and lands back at the start, where the
best action is still worth 0, so the target is $-100 + 0 = -100$. The error is
$-100 - 0 = -100$, and half of it is applied:
$Q(\text{start}, \text{right}) = -50$. One experience, and the robot will not
choose right at the start again unless the other three actions fall below −50
or the coin overrides it. That is the whole mechanism; the rest is doing it a
hundred thousand times.

## Off-policy, and what the max is really saying

Look at the target once more: $\max_{a'} Q(s', a')$. It bootstraps from the
*best* action at the next state — not from the action the robot is about to
take, which, if it is exploring, may be something else entirely. Q-learning
learns the value of the greedy policy while behaving according to a different
one. That is what *off-policy* means, and it has a consequence that is easy to
state and hard to feel until you see it: Q-learning's table describes a robot
that never explores, even though the robot filling it in explores on every
step.

The alternative is to bootstrap from what will actually happen. Choose the next
action $a'$ first, by the same exploring rule, and use *its* value:

$$Q(s, a) \leftarrow Q(s, a) + \alpha\left[ r + \gamma\, Q(s', a') - Q(s, a) \right]$$

Five things go into the update — $s, a, r, s', a'$ — which is where the name
*SARSA* comes from. It is *on-policy*: the table describes the policy that is
generating the experience, exploration included. In the lab, *Cliff walking*,
the two learners differ in one line, and the brief prints both lines side by
side.

## Where the two disagree, in numbers

Put the robot on the row above the cliff, somewhere in the middle, with the
exploration rate $\varepsilon = 0.1$: nine times out of ten it acts greedily,
one time in ten it picks one of the four actions uniformly. Suppose its table at
that square currently says right is worth −5, up is −6, left is −7, and down —
into the cliff — is about −100.

Q-learning, backing up into this square from its left neighbour, uses
$\max_{a'} Q = -5$. The cliff-edge square is worth −5 as far as the table is
concerned, because the table describes a robot that would never press down.

SARSA uses the value of whichever action the exploring robot draws. On average
that is
$0.9 \times (-5) + 0.1 \times \frac{-5 - 6 - 7 - 100}{4} = -4.5 - 2.95 = -7.45$.
The square is worth about 2.45 less to SARSA than to Q-learning, and the 2.45
is almost entirely the one-in-forty chance of the random press being down.
Every cliff-edge square carries a penalty like it. Ten of them in a row add up
to more than the two extra steps a route one row higher would cost, and SARSA's
greedy policy moves up a row — or two. Q-learning's does not, because
Q-learning's table never priced the slips in.

```python
import random

ROWS, COLS = 3, 6
START, GOAL = (2, 0), (2, 5)
CLIFF = {(2, c) for c in range(1, 5)}
ACTIONS = ("U", "R", "D", "L")
DELTA = {"U": (-1, 0), "R": (0, 1), "D": (1, 0), "L": (0, -1)}


def step(s, a):
    r = min(ROWS - 1, max(0, s[0] + DELTA[a][0]))
    c = min(COLS - 1, max(0, s[1] + DELTA[a][1]))
    if (r, c) in CLIFF:
        return START, -100.0, False
    return (r, c), -1.0, (r, c) == GOAL


def greedy(Q, s):
    best = max(Q[s].values())
    return next(a for a in ACTIONS if Q[s][a] == best)


def choose(Q, s, eps, rng):
    if rng.random() < eps:
        return ACTIONS[rng.randrange(4)]
    return greedy(Q, s)


def learn(on_policy, episodes=400, alpha=0.5, eps=0.1, seed=3):
    rng = random.Random(seed)
    Q = {(r, c): {a: 0.0 for a in ACTIONS} for r in range(ROWS) for c in range(COLS)}
    total = 0.0
    for _ in range(episodes):
        s = START
        a = choose(Q, s, eps, rng)
        for _t in range(200):
            s2, reward, done = step(s, a)
            total += reward
            a2 = choose(Q, s2, eps, rng)
            if done:
                target = reward
            elif on_policy:
                target = reward + Q[s2][a2]
            else:
                target = reward + max(Q[s2].values())
            Q[s][a] += alpha * (target - Q[s][a])
            s, a = s2, a2
            if done:
                break
    return Q, total / episodes


def greedy_route(Q):
    s, route = START, [START]
    for _ in range(30):
        s, _r, done = step(s, greedy(Q, s))
        route.append(s)
        if done:
            break
    return route


for name, on_policy in (("q-learning", False), ("sarsa     ", True)):
    Q, mean_return = learn(on_policy)
    route = greedy_route(Q)
    print(name, "rows used", sorted({r for r, _c in route}),
          "steps", len(route) - 1, "mean training return", round(mean_return, 1))
```

This is a three-row, six-column miniature of the lab's world, with the same
rules and the same single-line difference between the two learners. It prints
`q-learning rows used [1, 2] steps 7 mean training return -24.9` and then
`sarsa      rows used [0, 1, 2] steps 9 mean training return -20.8`.
Q-learning's greedy route hugs row 1, the edge, and is the shortest possible at
seven steps. SARSA's climbs to row 0, takes nine, and — this is the part people
do not expect — collected a *better* average return while training, about four
points per episode, because it fell off the cliff less often while it was
learning.

The lab's version is bigger and the effect is bigger with it: the thirteen-step
edge route for Q-learning, a longer safe route for SARSA, and a training-return
gap the test requires to exceed ten points per episode.

## Two measures that are not the same measure

That last number is the one to sit with. Q-learning found the better *greedy*
policy: seven steps beats nine, and if you switched exploration off and let each
robot run its table, Q-learning's would win. SARSA got the better *online*
return: with exploration still on, which it was throughout training, SARSA lost
less. Neither measure is wrong. They answer different questions — how good is
the policy you end up with, and how much did it cost to get there — and a
report that gives only one of them is hiding the other. The lab's `returns`
list and its `greedy_path` are the two measures, and the tests check them
separately because they disagree.

Which one you want depends on whether the robot's training runs are real. A
simulator can afford a thousand falls off the cliff; a physical robot cannot,
and a policy that will keep exploring in deployment — because the world keeps
changing and it has to — should be judged under the exploring policy it will
actually follow.

## The mistake, and why it is tempting

The tempting mistake is to reason that Q-learning must be safer because it
learns the *optimal* policy. It does learn the optimal policy for a robot that
never slips. The word optimal is doing the misleading; the table is optimal
under an assumption about the behaviour that the behaviour violates, and on the
cliff the violation is expensive. SARSA's table is not optimal for anything in
that sense — it is the value of an $\varepsilon$-greedy policy — but it is the
truth about the robot that exists.

A mechanical mistake that costs hours: SARSA needs $a'$ *before* it can update,
so the next action is chosen inside the loop, right after the step, and then
carried into the next iteration as the current action. Q-learning chooses at
the top of the loop. Write SARSA by choosing the next action at the top of the
following iteration and using something else in the target — the greedy action,
say — and you have written Q-learning with extra steps. The lab's tests on the
two learners' routes will tell you at once, because the paths will coincide.

And one more, in the environment rather than the learner: the cliff is not
terminal. Falling costs −100 and *continues*, from the start. Make it terminal
and the −100 becomes a quick exit from a bad episode, which is a different
problem with different answers, and the test on `step` checks for `done` being
`False` after a fall.

## Where it stops holding

Both updates converge to the right table only if every state-action pair keeps
being tried — infinitely often, in the limit — and, when the targets are noisy,
if the step size $\alpha$ decays in the right way: its sum diverges, so the
table can move as far as it needs, and the sum of its squares converges, so the
noise eventually averages out. On the cliff the environment is deterministic,
so a Q-learning target is a fixed function of the table and a fixed
$\alpha = 0.5$ is fine; SARSA's targets are random through $a'$, so its table
keeps jittering around its answer by an amount that scales with $\alpha$. For a
route decision that is fine; for a precise value it is not, and in the
capstone's slippery maze, where the landing square is random for both learners,
the decay matters for both.

More seriously, Q-learning's convergence proof is for a table. Replace the table
with a function that generalises across states — a neural network, or even a
linear model — and combine it with bootstrapping and off-policy updates, and the
three together can diverge: the *deadly triad*. That is not a theoretical
curiosity; it is the reason the deep reinforcement learning of the next course
needs target networks, replay buffers and a good deal of care. SARSA, being
on-policy, is somewhat more forgiving in that setting, which is one more thing
the cliff is quietly teaching.
''',
                },
            ],
            "quiz": {
                "title": "Targets, bootstraps and the price of exploring",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is the temporal-difference error, in one sentence?",
                        "opts": [
                            "The difference between the reward received on a step and the reward the table had predicted for it",
                            "One sampled Bellman target minus the table's current claim, which averages to zero when the table is right",
                            "The change in a state's value between two consecutive sweeps of the whole value table",
                            "The gap between the best action's value at a state and the value of the action that the robot actually took there",
                        ],
                        "a": 1,
                        "whys": [
                            r"The table does not predict rewards; it predicts total return from a state-action pair. The error compares that prediction with reward-plus-bootstrap, not with the reward alone.",
                            r"$r + \gamma \max_{a'} Q(s', a')$ is one draw from the distribution whose mean is $Q(s, a)$; subtract the current estimate and you have the one number the update is driven by.",
                            r"There are no sweeps in model-free learning; the table is updated one entry at a time as experience arrives. That description belongs to value iteration in the previous module.",
                            r"That is the exploration cost at one step — how much the taken action is worse than the greedy one — and it is what SARSA prices in. It is not the learning signal; the TD error is.",
                        ],
                        "why": r"""
The Bellman equation says $Q(s, a)$ equals an expectation over landings of
reward plus discounted next value. A single step gives one landing, so
$r + \gamma \max_{a'} Q(s', a')$ is one sample of that expectation. If the
table were right the samples would scatter around $Q(s, a)$ and their average
would be zero; the error is that sample minus the table, and moving the table
a fraction $\alpha$ towards each sample is the whole of Q-learning.
""",
                    },
                    {
                        "q": "What makes Q-learning off-policy?",
                        "opts": [
                            "It updates the table only after the episode ends, from a policy frozen at the start of the episode",
                            "It learns from transitions that were generated by a separate random policy and stored in a replay buffer",
                            "Its target uses the best next action, so the table describes the greedy policy while the robot explores",
                            "It never explores, because the max in the target means the robot always takes the greedy action",
                        ],
                        "a": 2,
                        "whys": [
                            r"Q-learning updates after every step, not at episode end; that description is closer to Monte Carlo control. Off-policy is about *whose* value is being learned, not when.",
                            r"Replay buffers are one way to exploit off-policy learning, but they are not what makes it off-policy. The lab's Q-learning has no buffer and is off-policy all the same.",
                            r"The behaviour is $\varepsilon$-greedy; the target bootstraps from $\max_{a'}$, the greedy choice. Two policies are involved — one acting, one being evaluated — which is the definition.",
                            r"The max is in the *target*, not in the action selection. The robot still draws the exploration coin every step; the table it fills in is the one that pretends it does not.",
                        ],
                        "why": r"""
Two policies are in play. The behaviour policy chooses what the robot does,
and in the lab that is $\varepsilon$-greedy. The target policy is the one whose
value the table estimates, and because the bootstrap term is $\max_{a'} Q$, it
is the greedy policy. The two differ, so the learning is off-policy: the table
describes a robot that never explores, filled in by a robot that does. SARSA
closes the gap by bootstrapping from the action actually chosen next.
""",
                    },
                    {
                        "q": "On a cliff-edge square with values right −5, up −6, left −7, down −100, Q-learning bootstraps −5 and SARSA about −7.45. What is the 2.45 made of?",
                        "opts": [
                            "The living cost of the two extra steps a safer route would need, which SARSA charges in advance",
                            "The one-in-forty chance that the exploring robot's next press is the cliff, weighted by its −100",
                            "The spread between the up and left values, since SARSA averages the greedy action's neighbours",
                            "The learning rate times the reward, since SARSA applies alpha to the target rather than to the error",
                        ],
                        "a": 1,
                        "whys": [
                            r"SARSA knows nothing about routes; it knows what the next action will be. The safer route emerges because many squares each carry a small penalty, not because SARSA anticipates a detour.",
                            r"With probability 0.1 the next action is uniform over four, so down comes up one time in forty; $0.025 \times (-100)$ is −2.5, and the small remainder is the other explored actions being slightly worse than the greedy one.",
                            r"Up and left contribute, but only $0.025 \times (-6 - 7)$, a fraction of a point. The −100 dominates the average; the neighbours are not what SARSA is averaging over.",
                            r"Both learners apply $\alpha$ to the error in exactly the same line. The difference between them is entirely in how the target is built, before $\alpha$ is applied.",
                        ],
                        "why": r"""
SARSA's bootstrap is the value of the action it will actually take next, and
that action is drawn by the $\varepsilon$-greedy rule: 0.9 greedy, 0.1 uniform.
The expectation is $0.9 \times (-5) + 0.1 \times (-118/4) = -7.45$. Almost
the whole difference from the greedy −5 is the term $0.025 \times (-100)$, the
one press in forty that goes off the cliff. Q-learning's max skips that term,
which is why its table thinks the edge is safe and SARSA's does not.
""",
                    },
                    {
                        "q": "Q-learning found the shorter greedy path; SARSA collected the higher mean return while training. Which one has the better policy?",
                        "opts": [
                            "SARSA: training return is measured over hundreds of episodes and is the more reliable estimate",
                            "Q-learning: training return is contaminated by random actions and says nothing about the policy",
                            "Neither can be said until epsilon is set to zero for both, since exploration makes the two learners incomparable",
                            "Both, for different questions: the path measures the final policy, the return measures what learning cost",
                        ],
                        "a": 3,
                        "whys": [
                            r"The training return is an honest measure of something — the cost of learning under exploration — but not of the greedy policy, which is never run during training. More episodes do not turn one measure into the other.",
                            r"Random actions are exactly the point: the robot *did* take them, and paid for them. A deployed robot that keeps exploring will pay for them too, and the return is the number that says how much.",
                            r"They are comparable as they stand, on two axes. Setting $\varepsilon$ to zero would collapse both onto the greedy-path axis and throw away the second measure rather than settle it.",
                            r"Shortest route with exploration off; least lost with exploration on. A report needs both numbers, and the lab's tests check them separately.",
                        ],
                        "why": r"""
The greedy path is the policy you would deploy if exploration stopped. The
training return is what the robot actually collected while exploration was on.
Q-learning wins the first and SARSA the second, and the disagreement is not a
paradox: Q-learning's table ignores exploration and SARSA's prices it in.
Which matters depends on whether the training episodes are real — a simulator
can afford the falls, a physical robot cannot — and the lab measures both so
that the question can be asked.
""",
                    },
                    {
                        "q": "A student writes SARSA but, in the target, uses the greedy action at the next state instead of the action chosen for it. What have they written?",
                        "opts": [
                            "Q-learning under another name: the greedy action's value at the next state is the max, and the routes coincide",
                            "Monte Carlo control, since the target no longer bootstraps from the table at the next state",
                            "A learner that stops converging, because the action named in the target and the action actually taken next disagree",
                            "A safer learner than SARSA, because the greedy action is the one least likely to step off the cliff",
                        ],
                        "a": 0,
                        "whys": [
                            r"$Q(s', \text{greedy}(s'))$ is $\max_{a'} Q(s', a')$ by definition. The single line that separates the two learners has been rewritten as the other one, and the lab's route tests will show two identical paths.",
                            r"The target still bootstraps — it reads a value from the table at $s'$. Monte Carlo waits for the episode to end and uses the observed return; nothing here does that.",
                            r"Disagreement between the target's action and the action taken is exactly what off-policy learning is, and Q-learning converges in spite of it. The learner is fine; it is merely not SARSA.",
                            r"It is *less* safe, not more: bootstrapping from the greedy action is what makes Q-learning ignore the exploration risk and hug the cliff.",
                        ],
                        "why": r"""
The only difference between the two learners is which action's value sits in
the target. SARSA uses the action that will actually be taken; Q-learning uses
the best one, and the best one's value is the max. Substitute the greedy
action into SARSA's target and the max is back, along with everything that
follows from it: the edge-hugging route, the worse training return, the
off-policy character. The lab's tests on the two routes catch it because the
paths come out identical.
""",
                    },
                    {
                        "q": "On the cliff the environment is deterministic; in the capstone's maze the landing square is random. Why does a fixed step size matter more in the capstone?",
                        "opts": [
                            "Slips make the state non-Markov, so no fixed step size can converge on a slippery grid",
                            "With random landings the targets are noisy, and a step size that never shrinks keeps the table moving with the noise",
                            "A fixed alpha breaks the condition that the step sizes must sum to infinity, so the table can never travel far enough from its start",
                            "Slips add states to the maze, so a fixed alpha spreads the same amount of learning across more entries",
                        ],
                        "a": 1,
                        "whys": [
                            r"The slippery maze is still Markov: the next square depends only on the current square and the action, through a fixed probability. Randomness is not the same as history-dependence.",
                            r"Each target is one sample of an expectation; with $\alpha$ fixed the table follows each sample partway and never settles, jittering by an amount proportional to $\alpha$. A decaying $\alpha$ lets the samples average out.",
                            r"A fixed $\alpha$ satisfies the divergent-sum condition trivially — it is the *other* condition, that the squares sum to something finite, that it breaks, and that is the one that averages the noise away.",
                            r"The state set is the same set of squares whether the wheels slip or not. What slips change is the distribution over next squares, which is what makes the targets noisy.",
                        ],
                        "why": r"""
The convergence conditions on $\alpha$ exist to tame noise in the targets. On
a deterministic grid a Q-learning target is a fixed function of the current
table, so there is no noise to tame and a constant step works. When the
landing square is random, each target is a sample, and a table that moves a
fixed fraction towards every sample keeps moving; only a step size whose
squares sum to something finite lets the samples average out. SARSA has noisy
targets even on the cliff, through the random $a'$, which is why its table
jitters there already.
""",
                    },
                ],
            },
            "lab": {
                "title": "Cliff walking",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A 4 by 12 grid, rows numbered 0 at the top. The agent starts at `(3, 0)` and
the goal is `(3, 11)`. The whole strip `(3, 1)` to `(3, 10)` is a cliff.

- every step costs `-1`
- stepping into the cliff costs `-100` and teleports the agent back to the start
  without ending the episode
- reaching the goal costs `-1` and ends the episode
- a move into a wall leaves the agent in place, still paying `-1`

The optimal route is 13 steps long and runs along row 2, directly above the
cliff. Under an epsilon-greedy behaviour policy that route is also the most
dangerous one.

## What to write

**`step(state, action)`** — `(next_state, reward, done)` for one transition.
Actions are `"U"`, `"R"`, `"D"`, `"L"`.

**`greedy_action(Q, state)`** — the best action, ties broken by `ACTIONS` order.

**`epsilon_greedy(Q, state, epsilon, rng)`** — with probability `epsilon` draw
uniformly with `rng.randrange(len(ACTIONS))`, otherwise act greedily. Draw the
exploration coin with `rng.random()` **every** step, whatever epsilon is, so the
random stream stays aligned between the two algorithms.

**`q_learning(...)`** and **`sarsa(...)`** — both return `(Q, returns)` where
`returns` holds the undiscounted sum of rewards of each training episode. Same
defaults: `episodes=500, alpha=0.5, epsilon=0.1, gamma=1.0, seed=7,
max_steps=200`. Seed one `random.Random(seed)` at the top and use it for
everything.

The only difference between the two is the bootstrap:

```text
Q-learning   target = r + gamma * max over a' of Q[s2][a']
SARSA        target = r + gamma * Q[s2][a2]      a2 is the action about to be taken
```

and in both, a transition that ends the episode has `target = r`.

**`greedy_path(Q, max_steps)`** — the states visited by following
`greedy_action` from the start, the terminal state included.

## What you should see

Q-learning finds the 13-step cliff-edge route. SARSA, which bootstraps from the
action it will really take and therefore prices in the 10% chance of stepping
off, settles for a longer route along the top row — and collects a better
average return while training.
''',
                "files": [{"name": "main.py", "content": r'''
import random

ROWS, COLS = 4, 12
START = (3, 0)
GOAL = (3, 11)
CLIFF = frozenset((3, c) for c in range(1, 11))
ACTIONS = ("U", "R", "D", "L")
DELTA = {"U": (-1, 0), "R": (0, 1), "D": (1, 0), "L": (0, -1)}


def zero_q():
    """Q[state][action] = 0.0 for every cell of the grid. Provided."""
    return {(r, c): {a: 0.0 for a in ACTIONS}
            for r in range(ROWS) for c in range(COLS)}


def step(state, action):
    """One transition -> (next_state, reward, done)."""
    # your code here


def greedy_action(Q, state):
    """The highest-valued action, ties broken by ACTIONS order."""
    # your code here


def epsilon_greedy(Q, state, epsilon, rng):
    """Explore with probability epsilon, otherwise act greedily."""
    # your code here


def q_learning(episodes=500, alpha=0.5, epsilon=0.1, gamma=1.0, seed=7, max_steps=200):
    """Off-policy TD control -> (Q, returns)."""
    # your code here


def sarsa(episodes=500, alpha=0.5, epsilon=0.1, gamma=1.0, seed=7, max_steps=200):
    """On-policy TD control -> (Q, returns)."""
    # your code here


def greedy_path(Q, max_steps=100):
    """States visited by the greedy policy from START."""
    # your code here


Qq, Rq = q_learning()
Qs, Rs = sarsa()
print("q-learning path", greedy_path(Qq))
print("sarsa path     ", greedy_path(Qs))
print("mean return: q", sum(Rq) / len(Rq), "sarsa", sum(Rs) / len(Rs))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import random

ROWS, COLS = 4, 12
START = (3, 0)
GOAL = (3, 11)
CLIFF = frozenset((3, c) for c in range(1, 11))
ACTIONS = ("U", "R", "D", "L")
DELTA = {"U": (-1, 0), "R": (0, 1), "D": (1, 0), "L": (0, -1)}


def zero_q():
    """Q[state][action] = 0.0 for every cell of the grid. Provided."""
    return {(r, c): {a: 0.0 for a in ACTIONS}
            for r in range(ROWS) for c in range(COLS)}


def step(state, action):
    """One transition -> (next_state, reward, done)."""
    dr, dc = DELTA[action]
    row = min(ROWS - 1, max(0, state[0] + dr))
    col = min(COLS - 1, max(0, state[1] + dc))
    nxt = (row, col)
    if nxt in CLIFF:
        return START, -100.0, False      # dragged back, but the episode continues
    if nxt == GOAL:
        return nxt, -1.0, True
    return nxt, -1.0, False


def greedy_action(Q, state):
    """The highest-valued action, ties broken by ACTIONS order."""
    row = Q[state]
    best = max(row.values())
    for action in ACTIONS:
        if row[action] == best:
            return action


def epsilon_greedy(Q, state, epsilon, rng):
    """Explore with probability epsilon, otherwise act greedily."""
    if rng.random() < epsilon:
        return ACTIONS[rng.randrange(len(ACTIONS))]
    return greedy_action(Q, state)


def q_learning(episodes=500, alpha=0.5, epsilon=0.1, gamma=1.0, seed=7, max_steps=200):
    """Off-policy TD control -> (Q, returns)."""
    rng = random.Random(seed)
    Q = zero_q()
    returns = []
    for _ in range(episodes):
        state = START
        total = 0.0
        for _t in range(max_steps):
            action = epsilon_greedy(Q, state, epsilon, rng)
            nxt, r, done = step(state, action)
            total += r
            # Bootstrap from the best available action, not the one we will take.
            target = r if done else r + gamma * max(Q[nxt].values())
            Q[state][action] += alpha * (target - Q[state][action])
            state = nxt
            if done:
                break
        returns.append(total)
    return Q, returns


def sarsa(episodes=500, alpha=0.5, epsilon=0.1, gamma=1.0, seed=7, max_steps=200):
    """On-policy TD control -> (Q, returns)."""
    rng = random.Random(seed)
    Q = zero_q()
    returns = []
    for _ in range(episodes):
        state = START
        action = epsilon_greedy(Q, state, epsilon, rng)
        total = 0.0
        for _t in range(max_steps):
            nxt, r, done = step(state, action)
            total += r
            nxt_action = epsilon_greedy(Q, nxt, epsilon, rng)
            # Bootstrap from the action actually chosen: exploration is priced in.
            target = r if done else r + gamma * Q[nxt][nxt_action]
            Q[state][action] += alpha * (target - Q[state][action])
            state, action = nxt, nxt_action
            if done:
                break
        returns.append(total)
    return Q, returns


def greedy_path(Q, max_steps=100):
    """States visited by the greedy policy from START."""
    state = START
    path = [state]
    for _ in range(max_steps):
        state, _r, done = step(state, greedy_action(Q, state))
        path.append(state)
        if done:
            break
    return path


Qq, Rq = q_learning()
Qs, Rs = sarsa()
print("q-learning path", greedy_path(Qq))
print("sarsa path     ", greedy_path(Qs))
print("mean return: q", sum(Rq) / len(Rq), "sarsa", sum(Rs) / len(Rs))
'''}],
                "hints": [
                    "Clamp the row and column with `min`/`max` before you look at the result: a bump into the boundary is a legal step that costs -1 and changes nothing.",
                    "The cliff is not terminal. Return `START` as the next state with reward -100 and `done` False, and let the episode carry on.",
                    "SARSA has to choose the next action *before* it updates, because the update needs it. Q-learning chooses at the top of the loop instead.",
                    "Both updates end with `Q[state][action] += alpha * (target - Q[state][action])`. Only the way `target` is built differs.",
                ],
                "tests": [
                    {"name": "step encodes the cliff, the goal and the walls", "code": r'''
assert step((3, 0), "U") == ((2, 0), -1.0, False), f"Got {step((3, 0), 'U')!r}"
assert step((3, 0), "R") == (START, -100.0, False), \
    f"walking into the cliff should cost -100 and reset without ending, got {step((3, 0), 'R')!r}"
assert step((2, 11), "D") == (GOAL, -1.0, True), f"Got {step((2, 11), 'D')!r}"
assert step((0, 0), "U") == ((0, 0), -1.0, False), "a bump into the top wall still costs -1"
assert step((0, 11), "R") == ((0, 11), -1.0, False), "a bump into the right wall still costs -1"
assert step((2, 5), "D") == (START, -100.0, False), "row 3 between the ends is all cliff"
'''},
                    {"name": "Action selection is greedy, with a tie rule", "code": r'''
import random as _random
_Q = zero_q()
assert greedy_action(_Q, (0, 0)) == "U", "with everything tied, the first action in ACTIONS wins"
_Q[(0, 0)]["D"] = 5.0
assert greedy_action(_Q, (0, 0)) == "D", f"Got {greedy_action(_Q, (0, 0))!r}"
_Q[(0, 0)]["L"] = 5.0
assert greedy_action(_Q, (0, 0)) == "D", "on a tie keep the earlier action in ACTIONS order"
_rng = _random.Random(1)
assert all(epsilon_greedy(_Q, (0, 0), 0.0, _rng) == "D" for _ in range(50)), \
    "epsilon = 0 must never explore"
_rng = _random.Random(2)
_draws = [epsilon_greedy(_Q, (0, 0), 1.0, _rng) for _ in range(2000)]
for _a in ACTIONS:
    assert 350 < _draws.count(_a) < 650, \
        f"epsilon = 1 should be uniform over four actions; {_a!r} came up {_draws.count(_a)} times"
'''},
                    {"name": "Q-learning finds the cliff-edge route", "code": r'''
_Qq, _Rq = q_learning()
_path = greedy_path(_Qq)
assert _path[0] == START and _path[-1] == GOAL, f"greedy path runs {_path[0]} -> {_path[-1]}"
assert len(_path) == 14, f"the optimal route is 13 steps, got {len(_path) - 1}"
assert all(_s[0] == 2 for _s in _path[1:-1]), \
    f"Q-learning should hug row 2, the row above the cliff; got {_path!r}"
assert abs(max(_Qq[START].values()) + 13.0) < 1.0, \
    f"max Q at the start is {max(_Qq[START].values()):.2f}, expected about -13"
'''},
                    {"name": "SARSA keeps its distance", "code": r'''
_Qs, _Rs = sarsa()
_path = greedy_path(_Qs)
assert _path[-1] == GOAL, f"SARSA should still reach the goal, path ended at {_path[-1]}"
assert min(_s[0] for _s in _path) <= 1, \
    f"SARSA should climb away from the cliff, but stayed on rows {sorted({s[0] for s in _path})}"
assert len(_path) > 14, f"the safe route is longer than 13 steps, got {len(_path) - 1}"
'''},
                    {"name": "On-policy pays off while learning", "code": r'''
_Qq, _Rq = q_learning()
_Qs, _Rs = sarsa()
assert len(_Rq) == 500 and len(_Rs) == 500, "returns should hold one entry per episode"
_mq = sum(_Rq) / len(_Rq)
_ms = sum(_Rs) / len(_Rs)
assert _ms > _mq + 10, \
    f"SARSA averaged {_ms:.1f} and Q-learning {_mq:.1f}; the on-policy learner should fall in less"
assert _mq < -20, f"Q-learning falls off the cliff while exploring; mean return was {_mq:.1f}"
assert sum(_Rq[-100:]) / 100 > sum(_Rq[:100]) / 100, "the later episodes should be better than the first"
'''},
                    {"name": "Seeded runs are reproducible", "code": r'''
_a, _ra = q_learning(episodes=60)
_b, _rb = q_learning(episodes=60)
assert _ra == _rb and _a == _b, "the same seed must give the same run — seed one Random at the top"
_c, _rc = q_learning(episodes=60, seed=8)
assert _rc != _ra, "a different seed should give a different run"
'''},
                    {"name": "Short training is not enough", "code": r'''
_Q10, _R10 = q_learning(episodes=10)
_Q500, _R500 = q_learning(episodes=500)
assert sum(_R500[-50:]) / 50 > sum(_R10) / len(_R10), \
    "500 episodes should end better than 10 episodes managed on average"
_p10 = greedy_path(_Q10)
assert len(_p10) <= 101, "greedy_path must respect max_steps rather than loop forever"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Exploration and regret",
            "summary": "The one-state case, where the exploration question can be answered exactly.",
            "concepts": [
                "A stochastic bandit strips control down to the explore-exploit trade-off alone",
                "Pseudo-regret R(T) = T * mu* - sum of the means of the arms actually pulled",
                "Pure greedy has linear regret: one unlucky sample can hide the best arm forever",
                "Fixed-epsilon exploration also has linear regret, at rate epsilon times the mean gap",
                "UCB1 pulls the arm maximising mean + c * sqrt(ln t / n_a): optimism in the face of uncertainty",
                "The bonus term is a confidence radius from Hoeffding's inequality, and it shrinks as sqrt(1/n)",
                "UCB1's regret is O(sum over suboptimal arms of ln T / gap) — sublinear, so the average regret goes to zero",
            ],
            "read": [
                {
                    "title": "Paying for what you do not know",
                    "minutes": 12,
                    "body": r'''
Three coins on a table, each weighted, none labelled. You may flip one per turn
and you are paid a pound each time the one you flip comes up heads. You have
twenty thousand turns. Nobody tells you the biases — they happen to be 0.30,
0.60 and 0.50 — and the only way to learn one is to flip that coin and count.

Every decision problem in this course so far has been a chain of states. This
one has a single state, and that is the point: with the states stripped away,
what is left is the trade-off that was hiding inside every $\varepsilon$ of the
previous module. Flip the coin that looks best and you *exploit*; flip another
to find out more and you *explore*; and every flip spent exploring a coin that
turns out worse is a pound you did not win. This is the *stochastic bandit*, and
it is the one setting where the cost of exploration can be worked out exactly.

## What you lose, measured honestly

You want a number that says how badly a strategy did. The total winnings will
not do: they depend on luck, and a strategy that flipped the best coin every
time can still have a bad run. So measure against what the strategy *chose*,
not what it *got*. If the best coin has bias $\mu^* = 0.60$ and the strategy
flipped a coin with bias $\mu_a$, that turn cost it $\mu^* - \mu_a$ in
expectation, whatever the coin actually showed. Over $T$ turns:

$$R(T) = \sum_{t=1}^{T} \left(\mu^* - \mu_{a_t}\right) = T\mu^* - \sum_{t=1}^{T} \mu_{a_t}$$

This is *pseudo-regret*. Flip the 0.60 coin and you accrue nothing, even if it
came up tails. Flip the 0.30 coin and you accrue 0.30, even if it came up heads.
The lab in this module, *Epsilon-greedy against UCB1*, computes it from the true
biases and the list of choices, and its test that a lucky bad flip still counts
as regret is there because the temptation to use the rewards instead is real:
the rewards are what a real gambler sees. But the rewards measure luck plus
strategy, and the regret measures strategy alone.

A strategy is good if its regret grows *sublinearly*: if $R(T)/T \to 0$, the
fraction of turns wasted goes to zero. Whether a strategy manages that, and how
fast, is the whole question.

## Greedy: one bad flip and you are done

The obvious strategy keeps a running average for each coin, starting at zero,
and flips the one with the highest average. All three start tied and the tie
goes to the first coin, the 0.30 one. Flip it. If it comes up heads its average
is 1.0, well above the other two coins' zeros, so you flip it again; if it comes
up tails its average is 0.0, which ties the others, and the tie goes to it
again. Either way you flip the first coin forever. The block below shows it:
after twenty thousand turns the greedy strategy has pulled the coins
`[20000, 0, 0]` and its regret is $20000 \times 0.30 = 6000$, growing by
exactly 0.30 per turn with no end.

That is the extreme case, but the mechanism is general. Greedy stops sampling a
coin as soon as its estimate falls below another's, and an estimate from a
handful of flips can fall below by chance. Once it does, it is never corrected,
because the only way to correct it is to flip the coin again. Pure greedy has
*linear* regret, and the lab's test states it as a number: 2000 flips, regret
700, and exactly half of that after 1000, a straight line.

## Epsilon: better, and still a straight line

Explore with probability $\varepsilon$ — flip a coin chosen uniformly — and
exploit otherwise. Now every coin keeps being sampled, every estimate keeps
being corrected, and after a while the greedy choice is the right one. But the
exploration never stops. On every turn, with probability $\varepsilon$, a
uniformly random coin is flipped, and the expected cost of that flip is the
average gap $\bar\Delta = \frac{1}{k}\sum_a (\mu^* - \mu_a)$. Once the
estimates have settled, regret grows at

$$\frac{dR}{dt} \approx \varepsilon \bar\Delta$$

per turn, for ever. Here $\bar\Delta = (0.30 + 0 + 0.10)/3 = 0.1333$, so with
$\varepsilon = 0.1$ that is about 0.0133 per turn, or about 67 per five thousand
turns. The block prints the regret at each quarter of the run and the gaps
between the quarters are 60 to 65, a little under the estimate because the
exploiting turns are not yet perfect either. Epsilon-greedy has linear regret
too — a shallower line than greedy's, but a line. The lab measures the same
thing on its five arms, where the mean gap is 0.15 and $\varepsilon = 0.1$ gives
a tail rate near 0.015, and its last test checks that the rate lands in that
neighbourhood and that $\varepsilon = 0.3$ costs more.

Decaying $\varepsilon$ over time repairs this, if the decay is chosen well, and
choosing it well needs to know things about the gaps that you do not know. The
next idea makes the exploration decide for itself.

## Optimism, with a confidence interval attached

The trouble with greedy was that it trusted an estimate from three flips as much
as one from three thousand. An estimate should come with a margin: after $n$
flips the average $\hat\mu$ is within some radius of the truth with high
probability, and the radius shrinks as $n$ grows. Hoeffding's inequality gives
the radius for a coin: the chance that $\hat\mu$ underestimates $\mu$ by more
than $r$ is at most $e^{-2 n r^2}$. Ask for that chance to be small — one in
$t^4$ at turn $t$, say, so that the total chance of ever being fooled stays
bounded as $t$ grows — and solve: $e^{-2nr^2} = t^{-4}$ gives
$r = \sqrt{2\ln t / n}$.

Now be optimistic. Treat each coin as if it were as good as its interval allows,
and flip the one with the highest upper bound:

$$a_t = \arg\max_a \left[ \hat\mu_a + c\,\sqrt{\frac{\ln t}{n_a}} \right]$$

where $c$ absorbs the constant (the lab uses $c = 1$). Watch what the bonus
does. A coin flipped rarely has a large bonus, so its upper bound is high and it
gets flipped — exploration, aimed at the coins you know least about. A coin
flipped often has a small bonus, so it is flipped only if its average earns it —
exploitation. And a bad coin, once flipped enough for its interval to sit
entirely below the best coin's average, is never flipped again except when
$\ln t$ has grown enough to widen its interval back up, which happens more and
more slowly. This is *UCB1*, and it has no $\varepsilon$ and no randomness of
its own; the lab's implementation flips each coin once, in index order, and then
follows the rule.

Put numbers on it. After the warm-up, say the three coins showed tails, heads,
heads — averages 0, 1, 1, one flip each — and it is turn 4. The bonus is
$\sqrt{\ln 4 / 1} = 1.177$ for all three, so the upper bounds are 1.177, 2.177,
2.177, and the tie between the second and third goes to the lower index: flip
coin two. Suppose it shows tails; its average is now 0.5 from two flips, and at
turn 5 its bonus is $\sqrt{\ln 5 / 2} = 0.897$, upper bound 1.397. Coin three,
still one flip at average 1, has bonus $\sqrt{\ln 5} = 1.269$ and upper bound
2.269. Flip coin three. The rule is pulling towards whichever coin it has least
evidence about, and it will keep doing so until the evidence sorts them out.

```python
import math
import random

PROBS = (0.30, 0.60, 0.50)


def run(strategy, steps, epsilon=0.0, c=1.0, seed=11):
    rng = random.Random(seed)
    coins = random.Random(seed + 1)
    counts = [0, 0, 0]
    means = [0.0, 0.0, 0.0]
    regret = 0.0
    marks = []
    for t in range(1, steps + 1):
        if strategy == "ucb" and 0 in counts:
            arm = counts.index(0)
        elif strategy == "ucb":
            arm = max(range(3), key=lambda a: (means[a] + c * math.sqrt(math.log(t) / counts[a]), -a))
        elif rng.random() < epsilon:
            arm = rng.randrange(3)
        else:
            arm = max(range(3), key=lambda a: (means[a], -a))
        reward = 1.0 if coins.random() < PROBS[arm] else 0.0
        counts[arm] += 1
        means[arm] += (reward - means[arm]) / counts[arm]
        regret += max(PROBS) - PROBS[arm]
        if t % (steps // 4) == 0:
            marks.append(round(regret, 1))
    return marks, counts


for name, strat, kw in (("greedy   ", "eps", {}), ("eps 0.10 ", "eps", {"epsilon": 0.1}),
                        ("ucb1     ", "ucb", {})):
    marks, counts = run(strat, 20000, **kw)
    print(name, "regret at each quarter", marks, "pulls", counts)
```

Three lines come out. Greedy: `[1500.0, 3000.0, 4500.0, 6000.0]`, a ruler.
Epsilon 0.10: `[71.4, 131.8, 195.3, 259.9]`, with gaps of about 60, 64 and 65 —
a shallower ruler. UCB1: `[87.1, 101.5, 114.2, 125.6]`, with gaps of 14, 13 and
11: the curve is bending over. UCB1 was *behind* epsilon-greedy at the first
quarter — 87 to 71 — because it spent its early turns systematically checking
every coin, and it is well ahead by the end, because the checking tapered off.
The `(value, -a)` in the `max` keys is the tie rule, lowest index first, so that
the run is the same every time; the two seeded generators are so that the coins
and the exploration coin do not share a stream.

## Why the curve bends

Fix a bad coin with gap $\Delta_a = \mu^* - \mu_a$. For UCB1 to flip it at turn
$t$, its upper bound has to beat the best coin's, which — once both estimates
are close to their truths — needs the bonus to cover the gap:
$c\sqrt{\ln t / n_a} \gtrsim \Delta_a$, so $n_a \lesssim c^2 \ln t / \Delta_a^2$.
After that many flips the bad coin's interval sits below the best one's and it
stops being chosen. Each flip of it cost $\Delta_a$, so its total contribution
to the regret is about $\Delta_a \times \ln t / \Delta_a^2 = \ln t / \Delta_a$.
Sum over the bad coins:

$$R(T) = O\!\left( \sum_{a : \Delta_a > 0} \frac{\ln T}{\Delta_a} \right)$$

Logarithmic in $T$, so $R(T)/T \to 0$. Note the $1/\Delta_a$: a coin that is
only slightly worse than the best is *expensive* to rule out, because it takes
many flips to tell the two apart, even though each of those flips costs little.
That is why UCB1 here spent 836 flips on the 0.50 coin and only 140 on the 0.30
one. The lab's test on the five-arm bandit asks that the last quarter of the run
cost less than half of what the first quarter cost per step, and that the tail
is still positive — UCB1 never stops checking entirely, it checks
logarithmically often.

## The mistake, and why it is tempting

The mistake in measurement was covered above: regret is about choices, not
rewards, and the lab's test on `cumulative_regret` exists to catch an
implementation that subtracts what was won.

The mistake in reasoning is to read the UCB1 result as "its regret goes to
zero". It does not; the cumulative regret grows without bound, as $\ln T$ does.
What goes to zero is the regret *per turn*. A strategy with logarithmic regret
still wastes flips, forever, and if $T$ is small the $\ln T$ bound may be no
better than epsilon-greedy's line — the first quarter of the run above is
exactly that. Optimism pays over long horizons, and it is tempting to read a
short run as a verdict because a short run is what you have in front of you.

A third is the comparison itself. Comparing strategies by final score is
comparing samples of luck; the lab's insistence on regret curves, and on
comparing the *shape* of the curve rather than one number at the end, is the
discipline that carries into the capstone, where the same comparison is made
across training configurations rather than across coins.

## Where it stops holding

Hoeffding's bound needs rewards in a bounded range, which coins satisfy and
which a reward in pounds with occasional windfalls may not. The biases must be
fixed: if the coins are being swapped under the table while you play, an
estimate from a thousand old flips is worse than one from ten recent ones, and
UCB1's shrinking bonus is exactly the wrong instinct — non-stationary bandits
need sliding windows or discounting. If an adversary chooses the outcomes after
seeing your strategy, nothing based on averages works and the *adversarial*
bandit calls for randomised strategies with different guarantees. And if you
can see something before each turn — the weather, the customer — that changes
which coin is best, the problem is a *contextual* bandit and the estimate
becomes a model, which is the doorway back to function approximation and to the
next course.

Inside its assumptions, though, the bandit is the one part of reinforcement
learning with a complete answer. The chain of states in the earlier modules
made the exploration question hard; here it has been asked on its own, and
answered.
''',
                },
            ],
            "quiz": {
                "title": "Regret, optimism and the shape of the curve",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The best coin has bias 0.60. A strategy flips the 0.30 coin and it comes up heads. What does that turn add to the pseudo-regret?",
                        "opts": [
                            "Zero: the flip won a pound, so nothing was lost on that turn and there is nothing to charge against it",
                            "0.30: regret charges the gap between the best bias and the chosen bias, whatever the coin showed",
                            "0.60: the strategy could have flipped the best coin, so it forgoes that coin's whole bias",
                            "Minus 0.40: a heads on a 0.30 coin beat its expectation by 0.70, which more than covers the gap",
                        ],
                        "a": 1,
                        "whys": [
                            r"The pound was luck. Pseudo-regret is defined on what was chosen, and choosing a 0.30 coin over a 0.60 coin was a 0.30 mistake regardless of how the coin landed.",
                            r"$\mu^* - \mu_a = 0.60 - 0.30$, the expected pound lost by that choice. The lab's test that a heads on a bad arm still counts is this exact case.",
                            r"The strategy did not forgo everything; the 0.30 coin pays 0.30 on average. The charge is the *difference* between the two expected payouts, not the best coin's payout in full.",
                            r"Regret can never be negative, because no coin beats the best one in expectation. Mixing the observed reward into it is precisely the error that pseudo-regret is defined to avoid.",
                        ],
                        "why": r"""
Pseudo-regret asks one question of every turn: how much worse, in expectation,
was the coin you chose than the best coin? The answer depends on the biases
and the choice, and on nothing else. The coin's actual landing is noise, and
including it would mix luck into a measure that exists to exclude luck. That is
why the lab's `cumulative_regret` takes the true biases and the choice list,
and never sees the rewards.
""",
                    },
                    {
                        "q": "With estimates starting at zero and the tie going to the lowest index, pure greedy flipped the first coin twenty thousand times. Why did it never move?",
                        "opts": [
                            "The first coin happened to have the highest bias, so exploiting it was the correct decision throughout",
                            "Greedy flips coins in index order and only advances to the next one once the current coin has shown a tails",
                            "The other coins' estimates start at zero, and greedy treats an estimate of zero as unknown and skips it",
                            "Heads or tails, the first coin's estimate can never drop below the untouched zeros of the other two coins",
                        ],
                        "a": 3,
                        "whys": [
                            r"The first coin was the *worst*, at 0.30. Greedy stuck with it and paid 0.30 per turn for twenty thousand turns, which is the linear regret the lab's test measures.",
                            r"There is no index order in greedy beyond the tie rule. It flips whichever estimate is highest, and the first coin's estimate never stops being at least as high as the others'.",
                            r"Greedy has no notion of unknown; zero is a number like any other. The other coins are skipped because zero never *beats* the first coin's estimate, not because zero is treated specially.",
                            r"Heads gives it 1.0, above the zeros; tails gives it 0.0, tied with the zeros, and the tie rule picks it again. Its average can never drop below zero, so the others never get a turn.",
                        ],
                        "why": r"""
A coin's average is between 0 and 1, and the untouched coins sit at exactly 0.
So the first coin's estimate is always at least as high as theirs, and greedy —
which picks the highest, lowest index on a tie — never has a reason to leave
it. That is the general failure in its purest form: greedy stops sampling a coin
the moment it looks no better than another, and a coin it stops sampling can
never recover. The lab's test asks for exactly one distinct arm and a regret of
exactly 700 after 2000 pulls.
""",
                    },
                    {
                        "q": "On the lab's five arms, epsilon-greedy at 0.1 settles to about 0.015 regret per pull, which is epsilon times the mean gap. What does raising epsilon to 0.3 do to that rate?",
                        "opts": [
                            "Roughly triples it to 0.045: a random pull costs the mean gap, and it now happens three times as often",
                            "Lowers it, because the extra exploration identifies the best arm sooner and exploits it more of the time",
                            "Leaves it unchanged, since the mean gap is a property of the arms and does not depend on epsilon",
                            "Makes the regret sublinear, because at 0.3 the estimates converge and exploration is no longer needed",
                        ],
                        "a": 0,
                        "whys": [
                            r"The tail rate is $\varepsilon \bar\Delta$ once the greedy choice is right; the gap is fixed at 0.15 and $\varepsilon$ has tripled. The lab's last test checks that 0.3 regrets more than 0.1 for this reason.",
                            r"Identifying the best arm sooner saves a little early on, but the tail rate is set by the exploring pulls, which never stop and now happen on 30% of turns instead of 10%.",
                            r"The gap is a property of the arms; the *rate* is the gap times how often a random pull happens. Epsilon is that frequency, and the rate scales with it.",
                            r"Fixed epsilon is linear at any value. The estimates converging does not stop the coin being drawn on every turn; that is what makes it linear in the first place.",
                        ],
                        "why": r"""
Once the estimates are good, an exploiting turn costs nothing and an exploring
turn costs the average gap, $\bar\Delta = 0.15$ on the lab's arms. The regret
rate is therefore $\varepsilon \bar\Delta$, and it is a rate, not a total: it
never decays, because the coin that decides whether to explore is thrown on
every turn with the same $\varepsilon$. Triple $\varepsilon$ and you triple the
rate. Only a decaying $\varepsilon$, or a rule like UCB1 that lets the
evidence itself switch exploration off, escapes the straight line.
""",
                    },
                    {
                        "q": "UCB1's bonus is $c\\sqrt{\\ln t / n_a}$. What do the two parts do?",
                        "opts": [
                            "The logarithm counts the resizes of the running estimate and the square root averages the noise out",
                            "Fewer pulls widen the interval and a longer run slowly widens it again, so neglected arms keep being rechecked",
                            "The bonus is the coin's standard deviation, which is largest for a bias of one half and smallest for a bias near zero or one",
                            "The bonus is the estimated probability that the arm is best, so it grows with pulls that came up heads",
                        ],
                        "a": 1,
                        "whys": [
                            r"Nothing is resized; the average is updated in place. The logarithm comes from asking Hoeffding's bound to hold with probability $1 - t^{-4}$, and the square root from solving that bound for the radius.",
                            r"$1/n_a$ is the Hoeffding radius shrinking with evidence; $\ln t$ is the confidence tightening as the horizon grows. Together they say: trust an arm more the more you have pulled it, but never entirely.",
                            r"The bonus does not depend on the estimate at all — an arm at 0.5 and an arm at 0.9 with the same pull count get the same bonus. It is a confidence radius, not a variance.",
                            r"The bonus ignores the outcomes; only the count and the clock go into it. Heads raise the *average*, and it is the average plus the bonus that is compared.",
                        ],
                        "why": r"""
Hoeffding says an average of $n$ coin flips is within $r$ of the truth except
with probability $e^{-2nr^2}$. Demand that failure probability be $t^{-4}$ and
solve for $r$: $\sqrt{2 \ln t / n}$. The $1/n$ is the ordinary shrinking of a
confidence interval with more data; the $\ln t$ is the price of being confident
across a growing number of turns. An arm pulled rarely keeps a wide interval and
gets tried; an arm pulled often has a narrow one and must earn its pulls on its
average.
""",
                    },
                    {
                        "q": "Over 20000 turns UCB1 spent 836 pulls on the 0.50 coin and 140 on the 0.30 coin. Why the difference, when the 0.30 coin is worse?",
                        "opts": [
                            "The 0.50 coin's bonus is larger, because a bias near one half has the highest variance of any coin",
                            "UCB1 pulls arms in proportion to their bias, so a coin with a higher bias is pulled more often",
                            "The 0.30 coin was ruled out during the warm-up phase, because its very first flip happened to come up tails",
                            "A small gap takes about ln t over the gap squared pulls to resolve, so near-best arms are the costly ones",
                        ],
                        "a": 3,
                        "whys": [
                            r"The bonus depends on the count and the clock, not on the bias or its variance. Two arms with equal pull counts have equal bonuses whatever their averages are.",
                            r"UCB1 pulls the arm with the highest upper bound; proportional sampling is not a rule it follows. The best arm was pulled 19024 times, not 60% of the time.",
                            r"The warm-up pulls every arm once regardless of outcome, and one flip settles nothing — the bonus after one pull is enormous. The 0.30 coin was pulled 140 times in total, not once.",
                            r"$n_a \approx c^2 \ln t / \Delta_a^2$: with $\Delta$ of 0.1 that is nine times the pulls needed for $\Delta$ of 0.3, and each pull costs only 0.1, so the two coins end up costing similar total regret.",
                        ],
                        "why": r"""
An arm stops being pulled once its upper bound sits below the best arm's
average, and the bonus has to shrink to the size of the gap for that to happen:
$\sqrt{\ln t / n_a} \approx \Delta_a$, so $n_a \approx \ln t / \Delta_a^2$.
The gap enters squared. An arm 0.1 behind needs nine times the pulls of an arm
0.3 behind to be told apart from the best, and although each of those pulls
costs a third as much, the total regret per bad arm comes out as
$\ln t / \Delta_a$ — larger for the arm that was nearly good enough.
""",
                    },
                    {
                        "q": "UCB1 was behind epsilon-greedy at the first quarter and ahead at the end. Does UCB1's regret go to zero?",
                        "opts": [
                            "Yes, once the warm-up is over; the early lead of epsilon-greedy is an artefact of the chosen seed",
                            "The cumulative regret keeps growing like ln T; what goes to zero is the per-turn regret, and only over a long horizon",
                            "Neither strategy's regret goes to zero, so which one wins is entirely a matter of the horizon chosen",
                            "Epsilon-greedy's regret goes to zero eventually as well, once its running estimates have converged to the true biases",
                        ],
                        "a": 1,
                        "whys": [
                            r"The warm-up is three pulls; the first quarter is five thousand. UCB1 was behind because it kept rechecking the worse coins while its intervals were still wide, and that is the algorithm, not the seed.",
                            r"The quarter gaps were 14, 13, 11 — shrinking, never zero. Cumulative regret is a sum of positive terms that thins out but never stops; divide by $T$ and *that* goes to zero.",
                            r"Horizon matters, but the strategies are not symmetric: one's regret is linear and the other's logarithmic, so beyond some horizon UCB1 wins for good. The lab's 20000 turns is past that point.",
                            r"Fixed epsilon keeps throwing the exploration coin at the same rate no matter how good the estimates are. Its regret grows at $\varepsilon \bar\Delta$ per turn forever, which is a line, not a curve that flattens.",
                        ],
                        "why": r"""
Sublinear regret means the *fraction* of wasted turns goes to zero, not the
count. UCB1's cumulative regret grows like $\sum \ln T / \Delta_a$ — without
bound, but slowly enough that dividing by $T$ sends it to zero. Epsilon-greedy's
grows like $\varepsilon \bar\Delta \cdot T$, a line, and a line eventually
overtakes any logarithm — but only eventually, which is why the first quarter
can go the other way. The lab's test compares quarters of the curve for this
reason: the shape is the evidence, not the endpoint.
""",
                    },
                ],
            },
            "lab": {
                "title": "Epsilon-greedy against UCB1",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Five Bernoulli arms with means `(0.20, 0.55, 0.50, 0.45, 0.30)`. Arm 1 is best.
The learner never sees the means; it sees one 0/1 sample per pull.

## What to write

**`BernoulliBandit(probs, seed)`** — `pull(arm)` returns `1.0` when
`self.rng.random() < probs[arm]` and `0.0` otherwise, and counts the pull in
`self.pulls`. An arm index outside the range raises `IndexError`. `arms()`
returns how many there are.

**`argmax(values)`** — the index of the largest value, lowest index on a tie.

**`run_epsilon_greedy(bandit, steps, epsilon, seed)`** — keep a pull count and
an incremental sample mean per arm, both starting at zero. Each step: draw
`rng.random()`, explore with `rng.randrange(k)` if it is below `epsilon`,
otherwise take `argmax` of the means. Update with

```text
counts[a] += 1
means[a] += (reward - means[a]) / counts[a]
```

Returns `(choices, rewards)`.

**`run_ucb1(bandit, steps, c)`** — no randomness of its own. While some arm has
never been pulled, pull the lowest-indexed such arm. After that, at step `t`
counting from 1, pull the `argmax` of

```text
means[a] + c * sqrt(log(t) / counts[a])
```

Returns `(choices, rewards)`.

**`cumulative_regret(probs, choices)`** — the running total of
`max(probs) - probs[arm]`, one entry per choice. This is *pseudo*-regret: it
uses the true means, not the sampled rewards, so it is the clean measure of how
often the learner was on the wrong arm.

## What you should find at T = 20000

Pure greedy never recovers from its first sample and its regret is a straight
line. Epsilon-greedy at `0.1` bends the line but never flattens it: it keeps
paying `epsilon` times the mean gap forever. UCB1's regret curve visibly
flattens — the last quarter costs far less than the first.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random

PROBS = (0.20, 0.55, 0.50, 0.45, 0.30)


class BernoulliBandit:
    """Five coins of unknown bias; you may flip one per step."""

    def __init__(self, probs=PROBS, seed=7):
        self.probs = tuple(probs)
        self.rng = random.Random(seed)
        self.pulls = 0

    def arms(self):
        """How many arms this bandit has."""
        # your code here

    def pull(self, arm):
        """One 0/1 sample from arm; IndexError for an arm that does not exist."""
        # your code here


def argmax(values):
    """Index of the largest value; the lowest index on a tie."""
    # your code here


def run_epsilon_greedy(bandit, steps, epsilon, seed=99):
    """Epsilon-greedy with incremental sample means -> (choices, rewards)."""
    # your code here


def run_ucb1(bandit, steps, c=1.0):
    """UCB1 -> (choices, rewards). Each arm once first, then the optimism rule."""
    # your code here


def cumulative_regret(probs, choices):
    """Running pseudo-regret, one entry per choice."""
    # your code here


STEPS = 20000
for _name, _choices in (
    ("greedy   ", run_epsilon_greedy(BernoulliBandit(), STEPS, 0.0)[0]),
    ("eps 0.10 ", run_epsilon_greedy(BernoulliBandit(), STEPS, 0.1)[0]),
    ("ucb1     ", run_ucb1(BernoulliBandit(), STEPS)[0]),
):
    print(_name, round(cumulative_regret(PROBS, _choices)[-1], 1))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random

PROBS = (0.20, 0.55, 0.50, 0.45, 0.30)


class BernoulliBandit:
    """Five coins of unknown bias; you may flip one per step."""

    def __init__(self, probs=PROBS, seed=7):
        self.probs = tuple(probs)
        self.rng = random.Random(seed)
        self.pulls = 0

    def arms(self):
        """How many arms this bandit has."""
        return len(self.probs)

    def pull(self, arm):
        """One 0/1 sample from arm; IndexError for an arm that does not exist."""
        if not isinstance(arm, int) or not 0 <= arm < len(self.probs):
            raise IndexError("no such arm: %r" % (arm,))
        self.pulls += 1
        return 1.0 if self.rng.random() < self.probs[arm] else 0.0


def argmax(values):
    """Index of the largest value; the lowest index on a tie."""
    return values.index(max(values))


def run_epsilon_greedy(bandit, steps, epsilon, seed=99):
    """Epsilon-greedy with incremental sample means -> (choices, rewards)."""
    rng = random.Random(seed)
    k = bandit.arms()
    counts = [0] * k
    means = [0.0] * k
    choices, rewards = [], []
    for _t in range(steps):
        # Draw the coin every step so the stream does not depend on the estimates.
        explore = rng.random() < epsilon
        arm = rng.randrange(k) if explore else argmax(means)
        reward = bandit.pull(arm)
        counts[arm] += 1
        means[arm] += (reward - means[arm]) / counts[arm]
        choices.append(arm)
        rewards.append(reward)
    return choices, rewards


def run_ucb1(bandit, steps, c=1.0):
    """UCB1 -> (choices, rewards). Each arm once first, then the optimism rule."""
    k = bandit.arms()
    counts = [0] * k
    means = [0.0] * k
    choices, rewards = [], []
    for t in range(1, steps + 1):
        if 0 in counts:
            arm = counts.index(0)          # an unpulled arm has an infinite bonus
        else:
            bonus = [c * math.sqrt(math.log(t) / counts[a]) for a in range(k)]
            arm = argmax([means[a] + bonus[a] for a in range(k)])
        reward = bandit.pull(arm)
        counts[arm] += 1
        means[arm] += (reward - means[arm]) / counts[arm]
        choices.append(arm)
        rewards.append(reward)
    return choices, rewards


def cumulative_regret(probs, choices):
    """Running pseudo-regret, one entry per choice."""
    best = max(probs)
    running = 0.0
    out = []
    for arm in choices:
        running += best - probs[arm]
        out.append(running)
    return out


STEPS = 20000
for _name, _choices in (
    ("greedy   ", run_epsilon_greedy(BernoulliBandit(), STEPS, 0.0)[0]),
    ("eps 0.10 ", run_epsilon_greedy(BernoulliBandit(), STEPS, 0.1)[0]),
    ("ucb1     ", run_ucb1(BernoulliBandit(), STEPS)[0]),
):
    print(_name, round(cumulative_regret(PROBS, _choices)[-1], 1))
'''}],
                "hints": [
                    "The incremental mean `m += (x - m) / n` is exactly the running average, without keeping every sample.",
                    "Draw `rng.random()` unconditionally, then decide. If you short-circuit when epsilon is 0 the random stream shifts and the runs stop being comparable.",
                    "`0 in counts` is the cleanest test for the UCB warm-up phase, and `counts.index(0)` picks the lowest unpulled arm.",
                    "Pseudo-regret uses `probs`, not `rewards`. A lucky sample from a bad arm is still regret.",
                ],
                "tests": [
                    {"name": "The bandit is a well-behaved sampler", "code": r'''
_b = BernoulliBandit(PROBS, seed=7)
assert _b.arms() == 5, f"arms() gave {_b.arms()!r}"
_draws = [_b.pull(1) for _ in range(2000)]
assert set(_draws) <= {0.0, 1.0}, "a pull is 0.0 or 1.0"
assert 0.50 < sum(_draws) / 2000 < 0.60, f"arm 1 averaged {sum(_draws) / 2000:.3f}, expected about 0.55"
assert _b.pulls == 2000, f"pulls counted {_b.pulls}, expected 2000"
for _bad in (5, -1, 99):
    try:
        BernoulliBandit(PROBS, 1).pull(_bad)
        assert False, f"pull({_bad}) should raise IndexError"
    except IndexError:
        pass
assert [BernoulliBandit(PROBS, 3).pull(0) for _ in range(3)] == \
       [BernoulliBandit(PROBS, 3).pull(0) for _ in range(3)], "the same seed must replay"
'''},
                    {"name": "Pseudo-regret counts wrong arms, not bad luck", "code": r'''
assert argmax([1, 3, 3, 0]) == 1, f"argmax should take the first maximum, got {argmax([1, 3, 3, 0])!r}"
assert cumulative_regret(PROBS, [1, 1, 1]) == [0.0, 0.0, 0.0], "the best arm never regrets"
_r = cumulative_regret(PROBS, [0, 1, 2])
assert len(_r) == 3, f"one entry per choice, got {len(_r)}"
assert abs(_r[0] - 0.35) < 1e-9 and abs(_r[1] - 0.35) < 1e-9 and abs(_r[2] - 0.40) < 1e-9, \
    f"Got {_r!r}, expected [0.35, 0.35, 0.40]"
assert cumulative_regret(PROBS, []) == [], "no choices, no regret"
_long = cumulative_regret(PROBS, run_ucb1(BernoulliBandit(), 200)[0])
assert all(_b >= _a - 1e-12 for _a, _b in zip(_long, _long[1:])), "regret can never decrease"
'''},
                    {"name": "UCB1 tries everything before it trusts anything", "code": r'''
_c, _r = run_ucb1(BernoulliBandit(), 5)
assert _c == [0, 1, 2, 3, 4], f"the first five pulls should sweep the arms, got {_c!r}"
assert len(_r) == 5 and set(_r) <= {0.0, 1.0}, f"rewards look wrong: {_r!r}"
_c20, _ = run_ucb1(BernoulliBandit(), 20)
assert _c20[:5] == [0, 1, 2, 3, 4] and len(_c20) == 20, "the warm-up must come first, then the rule"
assert set(_c20) <= set(range(5)), f"chose an arm that does not exist: {_c20!r}"
'''},
                    {"name": "Pure greedy has exactly linear regret", "code": r'''
_choices, _ = run_epsilon_greedy(BernoulliBandit(), 2000, 0.0)
assert len(set(_choices)) == 1, \
    f"with epsilon 0 and equal initial estimates the learner never switches; it used {sorted(set(_choices))}"
_reg = cumulative_regret(PROBS, _choices)
assert abs(_reg[-1] - 700.0) < 1e-6, f"greedy regret after 2000 steps was {_reg[-1]:.1f}, expected 700"
assert abs(_reg[999] * 2 - _reg[-1]) < 1e-6, "a straight line: half the steps, half the regret"
'''},
                    {"name": "UCB1 beats fixed epsilon over a long horizon", "code": r'''
_T = 20000
_ucb = cumulative_regret(PROBS, run_ucb1(BernoulliBandit(), _T)[0])[-1]
_eps = cumulative_regret(PROBS, run_epsilon_greedy(BernoulliBandit(), _T, 0.1)[0])[-1]
_greedy = cumulative_regret(PROBS, run_epsilon_greedy(BernoulliBandit(), _T, 0.0)[0])[-1]
assert _ucb < _eps, f"after {_T} steps UCB1 regret {_ucb:.1f} should beat epsilon-greedy {_eps:.1f}"
assert _eps < _greedy, f"epsilon-greedy {_eps:.1f} should still beat pure greedy {_greedy:.1f}"
assert _ucb < 0.15 * _greedy, f"UCB1 regret {_ucb:.1f} against greedy {_greedy:.1f} looks far too high"
'''},
                    {"name": "UCB1 regret is sublinear", "code": r'''
_T = 20000
_curve = cumulative_regret(PROBS, run_ucb1(BernoulliBandit(), _T)[0])
_q = _T // 4
_head = _curve[_q - 1] / _q
_tail = (_curve[-1] - _curve[-_q - 1]) / _q
assert _tail < 0.5 * _head, \
    f"per-step regret should collapse: first quarter {_head:.4f}, last quarter {_tail:.4f}"
assert _tail > 0, "some regret always remains — UCB1 keeps checking the other arms"
'''},
                    {"name": "Fixed epsilon never stops paying", "code": r'''
_T = 20000
_curve = cumulative_regret(PROBS, run_epsilon_greedy(BernoulliBandit(), _T, 0.1)[0])
_q = _T // 4
_tail = (_curve[-1] - _curve[-_q - 1]) / _q
assert 0.008 < _tail < 0.030, \
    f"the tail rate was {_tail:.4f}; fixed epsilon 0.1 settles near epsilon times the mean gap, 0.015"
_curve2 = cumulative_regret(PROBS, run_epsilon_greedy(BernoulliBandit(), _T, 0.3)[0])
assert _curve2[-1] > _curve[-1], \
    f"epsilon 0.3 explores three times as hard and should regret more: {_curve2[-1]:.1f} vs {_curve[-1]:.1f}"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an agent, an ablation and a report",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
`world.py` is supplied and must not be edited. It holds a slippery 6 by 9 maze:
`S` at the top left, `G` at the bottom right, four pits along row 4, and walls.
Every step pays `-1`, a pit pays `-50` and ends the episode, the goal pays `+20`
and ends the episode. With probability `slip` the intended action is replaced by
one of the two perpendicular ones. Two routes of thirteen steps exist; one of
them skirts the pits.

```python
env = GridWorld(slip=0.1, seed=0)
env.states()        # every non-wall cell, as (row, col)
env.actions()       # ("U", "R", "D", "L")
env.reset(state)    # state=None starts at S; otherwise start where you say
env.step(action)    # -> (next_state, reward, done); raises after the episode ends
env.is_terminal(s)  # goal or pit
env.render(policy)  # the maze with an arrow in every state the policy names
```

Write `agent.py`. `main.py` imports it and prints the report.

## Learning

**`new_q(env, init)`** — `Q[state][action] = init` for every state.

**`greedy_action(Q, state)`** / **`epsilon_greedy(Q, state, epsilon, rng)`** — as
in the cliff lab, ties broken by the order in `ACTIONS`.

**`train(...)`** with defaults `algorithm="q", episodes=600, alpha=0.05,
epsilon=0.2, gamma=0.97, decay=0.999, slip=0.1, seed=0, max_steps=100,
exploring_starts=True, init=-30.0`, returning `(Q, returns)`.

- one `GridWorld(slip=slip, seed=seed)` and one `random.Random(seed + 1)`
- with `exploring_starts`, each episode begins at a uniformly drawn non-terminal
  state, taken as `starts[rng.randrange(len(starts))]` from `sorted` order;
  otherwise it begins at `S`
- `algorithm` is `"q"` or `"sarsa"`; anything else raises `ValueError`
- `epsilon` is multiplied by `decay` after every episode
- `returns` holds the undiscounted sum of rewards per episode

Why `init = -30.0`? Optimistic zeros make an untried action look better than any
route the agent has actually measured, so the greedy policy walks into a corner
and stays there. A pessimistic start makes every tried action look better than
an untried one, which still explores — each first attempt drops below the
floor — but never strands the greedy policy.

**`greedy_policy(Q, env)`** — `{state: action}` for the non-terminal states.

**`evaluate(Q, episodes, slip, seed, max_steps)`** — run the greedy policy from
`S` and return `{"mean_return", "success_rate", "mean_steps"}`. Defaults
`episodes=100, slip=0.1, seed=5000, max_steps=100`.

## Reporting

**`ablation(configs, ...)`** — `configs` is a list of `(label, kwargs)`. Train
and evaluate each and return a list of row dicts with keys `label`,
`mean_return`, `success_rate`, `mean_steps`, `train_mean`, where `train_mean` is
the mean of the last fifty training returns.

**`format_table(rows, columns)`** — `columns` is a list of `(key, heading)`.
Return a string: a heading line, a rule of `-` the same width, then one line per
row. Every line is the same length; floats print to two decimals; the first
column is left-aligned and the rest right-aligned; columns are separated by two
spaces.

**`moving_average(values, window)`** — the `len(values) - window + 1` means.
`ValueError` when `window` is below 1 or longer than `values`.

**`cumulative_regret(returns, reference)`** — the running total of
`reference - r`, one entry per episode.

**`sparkline(values, width, height)`** — a text plot as a list of exactly
`height` strings of exactly `width` characters, top row first. Column `i` takes
the mean of `values[lo:hi]` for `lo = i * n // width` and `hi = max((i + 1) * n
// width, lo + 1)`, both clamped inside the list. A column whose value is `v`
fills `1 + floor((v - lo_v) / (hi_v - lo_v) * (height - 1))` cells from the
bottom, using `"#"`; when every value is equal, every column fills one cell.
`ValueError` for empty values or a non-positive width or height.
''',
        "deliverables": [
            "`agent.py` — learning, evaluation and reporting, importable with no side effects",
            "A Q-learning agent that reaches the goal from S in at least 90 of 100 evaluation episodes",
            "An ablation over at least five configurations, each isolating one choice",
            "`format_table` output that lines up in a fixed-width terminal",
            "A `sparkline` learning curve and a cumulative-regret curve, both in text",
            "`main.py` — trains, prints the policy map, the ablation table and both curves",
        ],
        "constraints": [
            "Standard library only; `random` and `math` are all you need",
            "Do not edit `world.py` — the environment is the fixed part of the experiment",
            "Every result reproducible from its seed: no unseeded `random` calls anywhere",
            "`agent.py` must print nothing when imported",
            "One config differs from the baseline in exactly one setting, or the ablation proves nothing",
        ],
        "rubric": [
            {"criterion": "Agent quality", "weight": 35,
             "evidence": "The baseline configuration evaluates at 0.9 success or better with a positive mean return and about 14 steps."},
            {"criterion": "Experimental method", "weight": 25,
             "evidence": "Ablation rows change one factor at a time, all seeds are fixed, and the myopic and under-trained rows are visibly worse."},
            {"criterion": "Reporting", "weight": 20,
             "evidence": "The table aligns, the sparkline honours its width and height contract, and the regret curve is monotone."},
            {"criterion": "Robustness", "weight": 12,
             "evidence": "Bad arguments raise ValueError; evaluation of a useless Q returns zero success instead of looping forever."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public function, no dead code, and the reporting helpers do not re-train anything."},
        ],
        "hints": [
            "Write `train` once with a branch on `algorithm` for the bootstrap term only. Two near-identical functions will drift apart.",
            "`sorted(...)` the exploring-start list before you index into it: dict and set iteration order must never leak into a seeded experiment.",
            "For `format_table`, compute each column's width as `max(len(heading), max(len(cell)))` first, then format twice — once for the heading, once per row.",
            "In `sparkline`, guard the constant series before you divide by `hi_v - lo_v`.",
            "`evaluate` must stop at `max_steps`. A greedy policy that bumps a wall forever would otherwise hang the tab.",
        ],
        "files": [
            {"name": "world.py", "ro": True, "content": r'''
"""Supplied environment for the ELEC410 capstone. Do not edit this file."""

import random

LAYOUT = (
    "S........",
    ".####.##.",
    "......#..",
    ".####....",
    "....^^^^.",
    "........G",
)

ACTIONS = ("U", "R", "D", "L")
DELTA = {"U": (-1, 0), "R": (0, 1), "D": (1, 0), "L": (0, -1)}
PERPENDICULAR = {"U": ("L", "R"), "D": ("L", "R"), "L": ("U", "D"), "R": ("U", "D")}

STEP_REWARD = -1.0
PIT_REWARD = -50.0
GOAL_REWARD = 20.0


class GridWorld:
    """A slippery maze. Reaching G ends the episode; a pit ends it badly."""

    def __init__(self, slip=0.1, seed=0):
        self.rows = len(LAYOUT)
        self.cols = len(LAYOUT[0])
        self.slip = slip
        self.rng = random.Random(seed)
        self.start = self._find("S")
        self.goal = self._find("G")
        self.pits = frozenset((r, c) for r in range(self.rows)
                              for c in range(self.cols) if LAYOUT[r][c] == "^")
        self.walls = frozenset((r, c) for r in range(self.rows)
                               for c in range(self.cols) if LAYOUT[r][c] == "#")
        self.state = self.start

    def _find(self, marker):
        for r in range(self.rows):
            for c in range(self.cols):
                if LAYOUT[r][c] == marker:
                    return (r, c)
        raise ValueError("marker missing: " + marker)

    def states(self):
        """Every cell that is not a wall, row-major."""
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if (r, c) not in self.walls]

    def actions(self):
        """The four moves."""
        return ACTIONS

    def is_terminal(self, state):
        """True for the goal and for every pit."""
        return state == self.goal or state in self.pits

    def reset(self, state=None):
        """Start an episode at S, or at the state you name."""
        self.state = self.start if state is None else state
        return self.state

    def _slide(self, state, action):
        dr, dc = DELTA[action]
        nr, nc = state[0] + dr, state[1] + dc
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return state
        if (nr, nc) in self.walls:
            return state
        return (nr, nc)

    def step(self, action):
        """One transition -> (next_state, reward, done)."""
        if action not in DELTA:
            raise ValueError("unknown action: %r" % (action,))
        if self.is_terminal(self.state):
            raise RuntimeError("episode already finished; call reset()")
        if self.rng.random() < self.slip:
            action = self.rng.choice(PERPENDICULAR[action])
        self.state = self._slide(self.state, action)
        if self.state == self.goal:
            return self.state, GOAL_REWARD, True
        if self.state in self.pits:
            return self.state, PIT_REWARD, True
        return self.state, STEP_REWARD, False

    def render(self, policy=None):
        """The maze as text, with an arrow wherever the policy names an action."""
        arrows = {"U": "^", "R": ">", "D": "v", "L": "<"}
        out = []
        for r in range(self.rows):
            row = ""
            for c in range(self.cols):
                cell = LAYOUT[r][c]
                if cell in "#^SG":
                    row += cell
                elif policy and (r, c) in policy:
                    row += arrows[policy[(r, c)]]
                else:
                    row += "."
            out.append(row)
        return "\n".join(out)
'''},
            {"name": "agent.py", "content": r'''
import math
import random

from world import GridWorld, ACTIONS

BASELINE = {
    "algorithm": "q", "episodes": 600, "alpha": 0.05, "epsilon": 0.2,
    "gamma": 0.97, "decay": 0.999, "slip": 0.1, "seed": 0,
    "max_steps": 100, "exploring_starts": True, "init": -30.0,
}

ABLATIONS = [
    ("baseline", {}),
    ("sarsa", {"algorithm": "sarsa"}),
    ("myopic gamma=0.5", {"gamma": 0.5}),
    ("under-trained", {"episodes": 40}),
    ("coarse alpha=0.4", {"alpha": 0.4}),
    ("no exploring starts", {"exploring_starts": False}),
]


def new_q(env, init=-30.0):
    """Q[state][action] = init for every state of the world."""
    # your code here


def greedy_action(Q, state):
    """The highest-valued action, ties broken by ACTIONS order."""
    # your code here


def epsilon_greedy(Q, state, epsilon, rng):
    """Explore with probability epsilon, otherwise act greedily."""
    # your code here


def train(algorithm="q", episodes=600, alpha=0.05, epsilon=0.2, gamma=0.97,
          decay=0.999, slip=0.1, seed=0, max_steps=100, exploring_starts=True,
          init=-30.0):
    """Tabular TD control -> (Q, returns)."""
    # your code here


def greedy_policy(Q, env):
    """{state: action} over the non-terminal states."""
    # your code here


def evaluate(Q, episodes=100, slip=0.1, seed=5000, max_steps=100):
    """Run the greedy policy from S -> mean_return, success_rate, mean_steps."""
    # your code here


def ablation(configs=None, eval_episodes=100):
    """One row per configuration: training result plus evaluation metrics."""
    # your code here


def format_table(rows, columns):
    """A fixed-width table: heading, rule, one line per row."""
    # your code here


def moving_average(values, window):
    """The len(values) - window + 1 sliding means."""
    # your code here


def cumulative_regret(returns, reference):
    """Running total of reference - r, one entry per episode."""
    # your code here


def sparkline(values, width=40, height=6):
    """A text plot: exactly height strings of exactly width characters."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from world import GridWorld
from agent import (ABLATIONS, ablation, cumulative_regret, evaluate,
                   format_table, greedy_policy, moving_average, sparkline, train)

Q, returns = train()
env = GridWorld()

print("Learned policy")
print(env.render(greedy_policy(Q, env)))
print()

print("Ablation")
print(format_table(ablation(ABLATIONS[:4]), [
    ("label", "configuration"), ("mean_return", "return"),
    ("success_rate", "success"), ("mean_steps", "steps"), ("train_mean", "train"),
]))
print()

print("Learning curve (episode return, smoothed)")
for line in sparkline(moving_average(returns, 20), 48, 6):
    print(line)
print()

print("Cumulative regret against a perfect run")
for line in sparkline(cumulative_regret(returns, 7.0), 48, 6):
    print(line)
print()
print("Final evaluation:", evaluate(Q))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "agent.py", "content": r'''
import math
import random

from world import GridWorld, ACTIONS

BASELINE = {
    "algorithm": "q", "episodes": 600, "alpha": 0.05, "epsilon": 0.2,
    "gamma": 0.97, "decay": 0.999, "slip": 0.1, "seed": 0,
    "max_steps": 100, "exploring_starts": True, "init": -30.0,
}

ABLATIONS = [
    ("baseline", {}),
    ("sarsa", {"algorithm": "sarsa"}),
    ("myopic gamma=0.5", {"gamma": 0.5}),
    ("under-trained", {"episodes": 40}),
    ("coarse alpha=0.4", {"alpha": 0.4}),
    ("no exploring starts", {"exploring_starts": False}),
]


def new_q(env, init=-30.0):
    """Q[state][action] = init for every state of the world."""
    return {state: {action: float(init) for action in ACTIONS}
            for state in env.states()}


def greedy_action(Q, state):
    """The highest-valued action, ties broken by ACTIONS order."""
    row = Q[state]
    best = max(row.values())
    for action in ACTIONS:
        if row[action] == best:
            return action


def epsilon_greedy(Q, state, epsilon, rng):
    """Explore with probability epsilon, otherwise act greedily."""
    if rng.random() < epsilon:
        return ACTIONS[rng.randrange(len(ACTIONS))]
    return greedy_action(Q, state)


def train(algorithm="q", episodes=600, alpha=0.05, epsilon=0.2, gamma=0.97,
          decay=0.999, slip=0.1, seed=0, max_steps=100, exploring_starts=True,
          init=-30.0):
    """Tabular TD control -> (Q, returns)."""
    if algorithm not in ("q", "sarsa"):
        raise ValueError("algorithm must be 'q' or 'sarsa', not %r" % (algorithm,))
    if episodes < 0:
        raise ValueError("episodes must not be negative")
    env = GridWorld(slip=slip, seed=seed)
    rng = random.Random(seed + 1)
    starts = sorted(s for s in env.states() if not env.is_terminal(s))
    Q = new_q(env, init)
    returns = []
    eps = epsilon
    for _episode in range(episodes):
        state = env.reset(starts[rng.randrange(len(starts))]
                          if exploring_starts else None)
        action = epsilon_greedy(Q, state, eps, rng)
        total = 0.0
        for _t in range(max_steps):
            nxt, reward, done = env.step(action)
            total += reward
            nxt_action = None if done else epsilon_greedy(Q, nxt, eps, rng)
            if done:
                target = reward
            elif algorithm == "q":
                target = reward + gamma * max(Q[nxt].values())
            else:
                target = reward + gamma * Q[nxt][nxt_action]
            Q[state][action] += alpha * (target - Q[state][action])
            state, action = nxt, nxt_action
            if done:
                break
        returns.append(total)
        eps *= decay
    return Q, returns


def greedy_policy(Q, env):
    """{state: action} over the non-terminal states."""
    return {state: greedy_action(Q, state)
            for state in env.states() if not env.is_terminal(state)}


def evaluate(Q, episodes=100, slip=0.1, seed=5000, max_steps=100):
    """Run the greedy policy from S -> mean_return, success_rate, mean_steps."""
    if episodes < 1:
        raise ValueError("episodes must be at least 1")
    env = GridWorld(slip=slip, seed=seed)
    total = 0.0
    wins = 0
    steps = 0
    for _ in range(episodes):
        state = env.reset()
        for _t in range(max_steps):
            state, reward, done = env.step(greedy_action(Q, state))
            total += reward
            steps += 1
            if done:
                if state == env.goal:
                    wins += 1
                break
    return {"mean_return": total / episodes,
            "success_rate": wins / episodes,
            "mean_steps": steps / episodes}


def ablation(configs=None, eval_episodes=100):
    """One row per configuration: training result plus evaluation metrics."""
    rows = []
    for label, overrides in (ABLATIONS if configs is None else configs):
        settings = dict(BASELINE)
        settings.update(overrides)
        Q, returns = train(**settings)
        metrics = evaluate(Q, episodes=eval_episodes, slip=settings["slip"])
        tail = returns[-50:] or [0.0]
        rows.append({"label": label,
                     "mean_return": metrics["mean_return"],
                     "success_rate": metrics["success_rate"],
                     "mean_steps": metrics["mean_steps"],
                     "train_mean": sum(tail) / len(tail)})
    return rows


def _cell(value):
    """One table cell as text: two decimals for floats, str otherwise."""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def format_table(rows, columns):
    """A fixed-width table: heading, rule, one line per row."""
    if not columns:
        raise ValueError("a table needs at least one column")
    widths = []
    for key, heading in columns:
        cells = [_cell(row.get(key, "")) for row in rows]
        widths.append(max([len(heading)] + [len(c) for c in cells]))
    parts = []
    for (key, heading), width in zip(columns, widths):
        parts.append(heading.ljust(width) if key == columns[0][0]
                     else heading.rjust(width))
    head = "  ".join(parts)
    lines = [head, "-" * len(head)]
    for row in rows:
        cells = []
        for i, ((key, _heading), width) in enumerate(zip(columns, widths)):
            text = _cell(row.get(key, ""))
            cells.append(text.ljust(width) if i == 0 else text.rjust(width))
        lines.append("  ".join(cells))
    return "\n".join(lines)


def moving_average(values, window):
    """The len(values) - window + 1 sliding means."""
    if window < 1:
        raise ValueError("window must be at least 1")
    if window > len(values):
        raise ValueError("window %d is longer than the %d values" % (window, len(values)))
    out = []
    running = sum(values[:window])
    out.append(running / window)
    for i in range(window, len(values)):
        running += values[i] - values[i - window]
        out.append(running / window)
    return out


def cumulative_regret(returns, reference):
    """Running total of reference - r, one entry per episode."""
    running = 0.0
    out = []
    for value in returns:
        running += reference - value
        out.append(running)
    return out


def sparkline(values, width=40, height=6):
    """A text plot: exactly height strings of exactly width characters."""
    if not values:
        raise ValueError("nothing to plot")
    if width < 1 or height < 1:
        raise ValueError("width and height must be positive")
    n = len(values)
    columns = []
    for i in range(width):
        lo = min(i * n // width, n - 1)
        hi = max((i + 1) * n // width, lo + 1)
        chunk = values[lo:min(hi, n)]
        columns.append(sum(chunk) / len(chunk))
    low, high = min(columns), max(columns)
    span = high - low
    filled = []
    for value in columns:
        if span == 0:
            filled.append(1)
        else:
            filled.append(1 + int((value - low) / span * (height - 1)))
    rows = []
    for r in range(height):
        depth = height - r          # row 0 is the top, so it needs the tallest bars
        rows.append("".join("#" if f >= depth else " " for f in filled))
    return rows
'''},
            {"name": "main.py", "content": r'''
from world import GridWorld
from agent import (ABLATIONS, ablation, cumulative_regret, evaluate,
                   format_table, greedy_policy, moving_average, sparkline, train)

Q, returns = train()
env = GridWorld()

print("Learned policy")
print(env.render(greedy_policy(Q, env)))
print()

print("Ablation")
print(format_table(ablation(ABLATIONS[:4]), [
    ("label", "configuration"), ("mean_return", "return"),
    ("success_rate", "success"), ("mean_steps", "steps"), ("train_mean", "train"),
]))
print()

print("Learning curve (episode return, smoothed)")
for line in sparkline(moving_average(returns, 20), 48, 6):
    print(line)
print()

print("Cumulative regret against a perfect run")
for line in sparkline(cumulative_regret(returns, 7.0), 48, 6):
    print(line)
print()
print("Final evaluation:", evaluate(Q))
'''},
        ],
        "tests": [
            {"name": "train returns a full table and a return per episode", "code": r'''
from agent import train, new_q
from world import GridWorld
_env = GridWorld()
_Q, _R = train(episodes=30)
assert set(_Q) == set(_env.states()), "Q should cover every non-wall cell"
assert all(set(_Q[_s]) == set(_env.actions()) for _s in _Q), "every state needs all four actions"
assert len(_R) == 30, f"returns had {len(_R)} entries for 30 episodes"
assert all(isinstance(_x, float) for _x in _R), "an episode return is a float"
_blank = new_q(_env, -30.0)
assert _blank[_env.start]["U"] == -30.0, "new_q should honour init"
'''},
            {"name": "train validates and replays", "code": r'''
from agent import train
try:
    train(algorithm="montecarlo", episodes=5)
    assert False, "an unknown algorithm should raise ValueError"
except ValueError:
    pass
_a, _ra = train(episodes=40)
_b, _rb = train(episodes=40)
assert _ra == _rb and _a == _b, "the same seed must reproduce the run exactly"
_c, _rc = train(episodes=40, seed=3)
assert _rc != _ra, "a different seed should produce a different run"
'''},
            {"name": "The baseline agent solves the maze", "code": r'''
from agent import train, evaluate
_Q, _R = train()
_m = evaluate(_Q)
assert _m["success_rate"] >= 0.90, f"success rate {_m['success_rate']:.2f}, expected at least 0.90"
assert _m["mean_return"] > 0.0, f"mean return {_m['mean_return']:.2f}, expected a positive score"
assert _m["mean_steps"] < 25, f"mean steps {_m['mean_steps']:.1f}; the route is 13 steps long"
'''},
            {"name": "The greedy policy is legal and complete", "code": r'''
from agent import train, greedy_policy
from world import GridWorld
_env = GridWorld()
_Q, _ = train()
_pi = greedy_policy(_Q, _env)
assert set(_pi) == {_s for _s in _env.states() if not _env.is_terminal(_s)}, \
    "the policy covers exactly the non-terminal, non-wall states"
assert all(_a in _env.actions() for _a in _pi.values()), "every action must be legal"
_map = _env.render(_pi)
assert _map.count("\n") == 5 and "S" in _map and "G" in _map, f"render looks wrong:\n{_map}"
'''},
            {"name": "Discounting and training length both matter", "code": r'''
from agent import train, evaluate
_base = evaluate(train()[0])
_myopic = evaluate(train(gamma=0.5)[0])
_short = evaluate(train(episodes=40)[0])
assert _myopic["success_rate"] <= 0.5, \
    f"at gamma 0.5 the goal is worth almost nothing 13 steps away; success was {_myopic['success_rate']:.2f}"
assert _short["mean_return"] < _base["mean_return"], \
    f"40 episodes ({_short['mean_return']:.1f}) should not match 600 ({_base['mean_return']:.1f})"
'''},
            {"name": "evaluate survives a useless value table", "code": r'''
from agent import new_q, evaluate
from world import GridWorld
_env = GridWorld()
_flat = new_q(_env, 0.0)
_m = evaluate(_flat, episodes=5)
assert _m["success_rate"] == 0.0, "an all-U policy walks into the top wall and stays there"
assert _m["mean_steps"] == 100, f"evaluation must stop at max_steps, it ran {_m['mean_steps']}"
try:
    evaluate(_flat, episodes=0)
    assert False, "zero evaluation episodes should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "ablation reports one comparable row per configuration", "code": r'''
from agent import ablation
_rows = ablation([("baseline", {}), ("myopic", {"gamma": 0.5})], eval_episodes=30)
assert len(_rows) == 2, f"got {len(_rows)} rows"
for _row in _rows:
    assert set(_row) == {"label", "mean_return", "success_rate", "mean_steps", "train_mean"}, \
        f"row keys were {sorted(_row)}"
    assert 0.0 <= _row["success_rate"] <= 1.0, f"success_rate out of range: {_row['success_rate']!r}"
assert _rows[0]["label"] == "baseline" and _rows[1]["label"] == "myopic", "rows keep their order"
assert _rows[0]["mean_return"] > _rows[1]["mean_return"], \
    "the baseline should beat the myopic configuration on the same environment"
'''},
            {"name": "format_table lines up", "code": r'''
from agent import format_table
_rows = [{"label": "baseline", "mean_return": 4.4812, "success_rate": 0.97},
         {"label": "a much longer label", "mean_return": -100.0, "success_rate": 0.0}]
_cols = [("label", "configuration"), ("mean_return", "return"), ("success_rate", "success")]
_text = format_table(_rows, _cols)
_lines = _text.split("\n")
assert len(_lines) == 4, f"heading, rule and two rows expected, got {len(_lines)} lines"
assert len(set(len(_l) for _l in _lines)) == 1, f"lines have different widths:\n{_text}"
assert set(_lines[1]) == {"-"}, f"the second line should be a rule, got {_lines[1]!r}"
assert "configuration" in _lines[0] and "success" in _lines[0], f"heading was {_lines[0]!r}"
assert "4.48" in _lines[2], f"floats print to two decimals, row was {_lines[2]!r}"
assert _lines[2].startswith("baseline"), "the first column is left-aligned"
assert format_table([], _cols).count("\n") == 1, "an empty table is still a heading and a rule"
'''},
            {"name": "moving_average and cumulative_regret", "code": r'''
from agent import moving_average, cumulative_regret
assert moving_average([1.0, 2.0, 3.0, 4.0], 2) == [1.5, 2.5, 3.5], \
    f"Got {moving_average([1.0, 2.0, 3.0, 4.0], 2)!r}"
assert moving_average([5.0], 1) == [5.0], "a window of 1 is the identity"
for _bad in (0, -3, 5):
    try:
        moving_average([1.0, 2.0, 3.0, 4.0], _bad)
        assert False, f"window {_bad} should raise ValueError"
    except ValueError:
        pass
_reg = cumulative_regret([7.0, 5.0, 6.0], 7.0)
assert _reg == [0.0, 2.0, 3.0], f"Got {_reg!r}, expected [0.0, 2.0, 3.0]"
assert all(_b >= _a for _a, _b in zip(_reg, _reg[1:])), "regret against a perfect run never falls"
assert cumulative_regret([], 7.0) == [], "no episodes, no regret"
'''},
            {"name": "sparkline honours its contract", "code": r'''
from agent import sparkline
_plot = sparkline([float(i) for i in range(100)], 20, 5)
assert len(_plot) == 5, f"asked for 5 rows, got {len(_plot)}"
assert all(len(_row) == 20 for _row in _plot), f"row widths were {[len(r) for r in _plot]}"
assert set("".join(_plot)) <= {"#", " "}, "only '#' and spaces belong in the plot"
_heights = [sum(1 for _row in _plot if _row[i] == "#") for i in range(20)]
assert _heights == sorted(_heights), f"a rising series should give rising bars, got {_heights}"
assert _heights[0] == 1 and _heights[-1] == 5, f"first and last bars were {_heights[0]}, {_heights[-1]}"
_flat = sparkline([3.0] * 40, 10, 4)
assert all(_row.count("#") == (10 if _i == 3 else 0) for _i, _row in enumerate(_flat)), \
    f"a constant series should fill exactly the bottom row:\n{_flat!r}"
_short = sparkline([1.0, 2.0], 6, 3)
assert len(_short) == 3 and all(len(_r) == 6 for _r in _short), "fewer values than columns must still work"
for _args in (([], 10, 3), ([1.0], 0, 3), ([1.0], 10, 0)):
    try:
        sparkline(*_args)
        assert False, f"sparkline{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "agent.py is import-clean and the report prints", "code": r'''
_src = open("agent.py").read()
assert "print(" not in _src, "agent.py is a library; the printing belongs in main.py"
assert "Learned policy" in _out, "main.py should print the policy map"
assert "configuration" in _out and "success" in _out, "main.py should print the ablation table"
assert "Cumulative regret" in _out, "main.py should print the regret curve"
assert "#" in _out, "the text plots should actually draw something"
'''},
        ],
    },
}
