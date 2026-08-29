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
