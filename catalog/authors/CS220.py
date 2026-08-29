"""CS220 — Database Management Systems. Author module."""

COURSE = {
    "id": "CS220",
    "title": "Database Management Systems",
    "year": 2,
    "level": "Intermediate",
    "prereqs": ["CS201"],
    "stack": ["SQL", "Python", "SQLite"],
    "credits": 10,
    "hours": 130,
    "icon": "⛃",
    "summary": (
        "A database is a data structure with a query language bolted on top, and this "
        "course takes both halves seriously. You write real SQL against a real engine, "
        "derive normal forms from functional dependencies, cost an index against a full "
        "scan, and decide whether an interleaved schedule is safe to run. The capstone "
        "is a small persistence layer with migrations, indexes and a query-cost report."
    ),
    "outcomes": [
        "Design a relational schema with primary keys, foreign keys and CHECK constraints that the engine actually enforces",
        "Write joins, aggregation, grouping and correlated subqueries, always with bound parameters",
        "Compute attribute closures, enumerate candidate keys, and decide whether a schema is in BCNF",
        "Decompose a violating relation into BCNF pieces and justify the result",
        "Estimate the I/O cost of an index lookup against a sequential scan and find the crossover selectivity",
        "Test a schedule for conflict serialisability by building and cycling its precedence graph",
        "Explain what two-phase locking guarantees, and what it costs when transactions deadlock",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Ramakrishnan & Gehrke, *Database Management Systems*, 3rd ed. — chapters 3-5, 15-19",
        "Silberschatz, Korth & Sudarshan, *Database System Concepts*, 7th ed. — chapters 7, 14, 17",
        "Codd, 'A Relational Model of Data for Large Shared Data Banks', *CACM* 13(6), 1970",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "The relational model and SQL",
            "summary": "Tables, keys and constraints, then the query language that reads them.",
            "concepts": [
                "A relation is a set of tuples over a named schema; order is not information",
                "Primary, candidate and foreign keys, and referential integrity as an enforced promise",
                "NOT NULL, UNIQUE and CHECK move validation from your code into the engine",
                "Inner versus left outer join, and which rows a left join is there to keep",
                "GROUP BY partitions; HAVING filters groups, WHERE filters rows",
                "Uncorrelated subqueries, `NOT IN` versus `NOT EXISTS`, and NULL's effect on both",
                "Bound parameters are not a style preference: string-built SQL is an injection hole",
            ],
            "lab": {
                "title": "A library schema, and questions asked of it",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Build a four-table library database in an in-memory SQLite instance, then answer
four questions about it. Every value that comes from outside the query text goes
in as a `?` parameter — no exceptions, no f-strings.

## `connect()`

Return a connection to `":memory:"` **with foreign key enforcement switched on**.
SQLite ignores foreign keys unless you ask: `PRAGMA foreign_keys = ON`, per
connection.

## `create_schema(conn)`

| table | columns |
| --- | --- |
| `author` | `id` PK, `name` NOT NULL UNIQUE, `country` NOT NULL |
| `book` | `id` PK, `title` NOT NULL, `author_id` NOT NULL → `author(id)`, `year` NOT NULL, `copies` NOT NULL CHECK > 0 |
| `member` | `id` PK, `name` NOT NULL |
| `loan` | `id` PK, `book_id` NOT NULL → `book(id)`, `member_id` NOT NULL → `member(id)`, `day` NOT NULL |

## `seed(conn)`

Insert `AUTHORS`, `BOOKS`, `MEMBERS` and `LOANS` — in that order, so no foreign
key is ever dangling — using `executemany` with placeholders.

## The queries

- **`titles_by_author(conn, name)`** → titles by that author, oldest first, ties
  alphabetical. A name nobody has gives `[]`.
- **`books_per_country(conn)`** → `(country, number of books)`, most books first,
  ties alphabetical by country.
- **`never_borrowed(conn)`** → titles with no `loan` row, alphabetical.
- **`top_borrowers(conn, limit)`** → `(member name, loans taken)` for the `limit`
  busiest members, most loans first, ties alphabetical. A member who has never
  borrowed anything does not appear.

```text
titles_by_author(conn, "Italo Calvino")  ->  ["Cosmicomics", "Invisible Cities"]
books_per_country(conn)                  ->  [("Italy", 3), ("United States", 3), ("Nigeria", 1)]
```
''',
                "files": [{"name": "main.py", "content": r'''
import sqlite3

AUTHORS = [
    (1, "Ursula K. Le Guin", "United States"),
    (2, "Italo Calvino", "Italy"),
    (3, "Chinua Achebe", "Nigeria"),
    (4, "Primo Levi", "Italy"),
]
BOOKS = [
    (1, "A Wizard of Earthsea", 1, 1968, 3),
    (2, "The Dispossessed", 1, 1974, 2),
    (3, "The Left Hand of Darkness", 1, 1969, 1),
    (4, "Invisible Cities", 2, 1972, 2),
    (5, "Cosmicomics", 2, 1965, 1),
    (6, "Things Fall Apart", 3, 1958, 4),
    (7, "The Periodic Table", 4, 1975, 1),
]
MEMBERS = [(1, "Ada"), (2, "Grace"), (3, "Linus"), (4, "Barbara")]
LOANS = [
    (1, 1, 1, "2026-03-01"), (2, 1, 2, "2026-03-02"), (3, 2, 1, "2026-03-03"),
    (4, 4, 3, "2026-03-04"), (5, 6, 1, "2026-03-05"), (6, 6, 2, "2026-03-06"),
    (7, 7, 2, "2026-03-07"), (8, 4, 1, "2026-03-08"),
]


def connect():
    """An in-memory connection with foreign keys enforced."""
    # your code here


def create_schema(conn):
    """Create author, book, member and loan with their keys and constraints."""
    # your code here


def seed(conn):
    """Insert the four constant tables, parents before children."""
    # your code here


def titles_by_author(conn, name):
    """Titles by one author, oldest first, ties alphabetical."""
    # your code here


def books_per_country(conn):
    """(country, book count), most books first, ties alphabetical."""
    # your code here


def never_borrowed(conn):
    """Titles that have never been loaned, alphabetical."""
    # your code here


def top_borrowers(conn, limit):
    """(member, loans) for the busiest members, most loans first."""
    # your code here


conn = connect()
create_schema(conn)
seed(conn)
print(titles_by_author(conn, "Italo Calvino"))
print(books_per_country(conn))
print(never_borrowed(conn))
print(top_borrowers(conn, 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import sqlite3

AUTHORS = [
    (1, "Ursula K. Le Guin", "United States"),
    (2, "Italo Calvino", "Italy"),
    (3, "Chinua Achebe", "Nigeria"),
    (4, "Primo Levi", "Italy"),
]
BOOKS = [
    (1, "A Wizard of Earthsea", 1, 1968, 3),
    (2, "The Dispossessed", 1, 1974, 2),
    (3, "The Left Hand of Darkness", 1, 1969, 1),
    (4, "Invisible Cities", 2, 1972, 2),
    (5, "Cosmicomics", 2, 1965, 1),
    (6, "Things Fall Apart", 3, 1958, 4),
    (7, "The Periodic Table", 4, 1975, 1),
]
MEMBERS = [(1, "Ada"), (2, "Grace"), (3, "Linus"), (4, "Barbara")]
LOANS = [
    (1, 1, 1, "2026-03-01"), (2, 1, 2, "2026-03-02"), (3, 2, 1, "2026-03-03"),
    (4, 4, 3, "2026-03-04"), (5, 6, 1, "2026-03-05"), (6, 6, 2, "2026-03-06"),
    (7, 7, 2, "2026-03-07"), (8, 4, 1, "2026-03-08"),
]

SCHEMA = """
CREATE TABLE author (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL
);
CREATE TABLE book (
    id        INTEGER PRIMARY KEY,
    title     TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES author(id),
    year      INTEGER NOT NULL,
    copies    INTEGER NOT NULL CHECK (copies > 0)
);
CREATE TABLE member (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE loan (
    id        INTEGER PRIMARY KEY,
    book_id   INTEGER NOT NULL REFERENCES book(id),
    member_id INTEGER NOT NULL REFERENCES member(id),
    day       TEXT NOT NULL
);
"""


def connect():
    """An in-memory connection with foreign keys enforced."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn):
    """Create author, book, member and loan with their keys and constraints."""
    conn.executescript(SCHEMA)
    conn.commit()


def seed(conn):
    """Insert the four constant tables, parents before children."""
    conn.executemany("INSERT INTO author (id, name, country) VALUES (?, ?, ?)", AUTHORS)
    conn.executemany(
        "INSERT INTO book (id, title, author_id, year, copies) VALUES (?, ?, ?, ?, ?)", BOOKS)
    conn.executemany("INSERT INTO member (id, name) VALUES (?, ?)", MEMBERS)
    conn.executemany(
        "INSERT INTO loan (id, book_id, member_id, day) VALUES (?, ?, ?, ?)", LOANS)
    conn.commit()


def titles_by_author(conn, name):
    """Titles by one author, oldest first, ties alphabetical."""
    rows = conn.execute("""
        SELECT book.title
          FROM book
          JOIN author ON author.id = book.author_id
         WHERE author.name = ?
         ORDER BY book.year, book.title
    """, (name,)).fetchall()
    return [row[0] for row in rows]


def books_per_country(conn):
    """(country, book count), most books first, ties alphabetical."""
    return conn.execute("""
        SELECT author.country, COUNT(*) AS books
          FROM book
          JOIN author ON author.id = book.author_id
         GROUP BY author.country
         ORDER BY books DESC, author.country
    """).fetchall()


def never_borrowed(conn):
    """Titles that have never been loaned, alphabetical."""
    rows = conn.execute("""
        SELECT title
          FROM book
         WHERE NOT EXISTS (SELECT 1 FROM loan WHERE loan.book_id = book.id)
         ORDER BY title
    """).fetchall()
    return [row[0] for row in rows]


def top_borrowers(conn, limit):
    """(member, loans) for the busiest members, most loans first."""
    return conn.execute("""
        SELECT member.name, COUNT(*) AS taken
          FROM loan
          JOIN member ON member.id = loan.member_id
         GROUP BY member.id, member.name
         ORDER BY taken DESC, member.name
         LIMIT ?
    """, (limit,)).fetchall()


conn = connect()
create_schema(conn)
seed(conn)
print(titles_by_author(conn, "Italo Calvino"))
print(books_per_country(conn))
print(never_borrowed(conn))
print(top_borrowers(conn, 3))
'''}],
                "hints": [
                    "`conn.executescript(...)` runs several DDL statements in one go; keep the whole schema in one string constant.",
                    "`REFERENCES author(id)` declares the foreign key, but nothing is enforced until the connection has run `PRAGMA foreign_keys = ON`.",
                    "`fetchall()` gives a list of tuples. When a query returns one column, unwrap it with `[row[0] for row in rows]`.",
                    "`NOT EXISTS (SELECT 1 FROM loan WHERE loan.book_id = book.id)` is the correlated form of 'no matching child row', and unlike `NOT IN` it behaves sensibly around NULL.",
                ],
                "tests": [
                    {"name": "The four tables exist", "code": r'''
_conn = connect()
create_schema(_conn)
_tables = {row[0] for row in _conn.execute(
    "SELECT name FROM sqlite_master WHERE type = 'table'")}
for _t in ("author", "book", "member", "loan"):
    assert _t in _tables, f"table {_t!r} is missing; found {sorted(_tables)!r}"
_cols = {row[1] for row in _conn.execute("PRAGMA table_info(book)")}
assert {"id", "title", "author_id", "year", "copies"} <= _cols, \
    f"book is missing columns; it has {sorted(_cols)!r}"
'''},
                    {"name": "Constraints are enforced by the engine", "code": r'''
import sqlite3 as _sqlite3
_conn = connect()
create_schema(_conn)
_conn.execute("INSERT INTO author (id, name, country) VALUES (?, ?, ?)", (1, "A", "Italy"))
for _sql, _args, _why in [
    ("INSERT INTO book (id, title, author_id, year, copies) VALUES (?, ?, ?, ?, ?)",
     (1, "T", 99, 1990, 1), "a book pointing at a missing author"),
    ("INSERT INTO book (id, title, author_id, year, copies) VALUES (?, ?, ?, ?, ?)",
     (2, None, 1, 1990, 1), "a book with no title"),
    ("INSERT INTO book (id, title, author_id, year, copies) VALUES (?, ?, ?, ?, ?)",
     (3, "T", 1, 1990, 0), "a book with zero copies"),
    ("INSERT INTO author (id, name, country) VALUES (?, ?, ?)",
     (2, "A", "Italy"), "a duplicate author name"),
]:
    try:
        _conn.execute(_sql, _args)
        assert False, f"{_why} should raise IntegrityError"
    except _sqlite3.IntegrityError:
        pass
'''},
                    {"name": "seed loads every row", "code": r'''
_conn = connect()
create_schema(_conn)
seed(_conn)
for _table, _want in [("author", 4), ("book", 7), ("member", 4), ("loan", 8)]:
    _got = _conn.execute(f"SELECT COUNT(*) FROM {_table}").fetchone()[0]
    assert _got == _want, f"{_table} holds {_got} rows, expected {_want}"
'''},
                    {"name": "titles_by_author joins and orders", "code": r'''
_got = titles_by_author(_conn, "Ursula K. Le Guin")
assert _got == ["A Wizard of Earthsea", "The Left Hand of Darkness", "The Dispossessed"], \
    f"got {_got!r}"
assert titles_by_author(_conn, "Italo Calvino") == ["Cosmicomics", "Invisible Cities"], \
    f"got {titles_by_author(_conn, 'Italo Calvino')!r}"
assert titles_by_author(_conn, "Nobody At All") == [], "an unknown author gives an empty list"
'''},
                    {"name": "books_per_country groups and ranks", "code": r'''
_got = [tuple(row) for row in books_per_country(_conn)]
assert _got == [("Italy", 3), ("United States", 3), ("Nigeria", 1)], f"got {_got!r}"
'''},
                    {"name": "never_borrowed and top_borrowers", "code": r'''
_got = never_borrowed(_conn)
assert _got == ["Cosmicomics", "The Left Hand of Darkness"], f"got {_got!r}"
_got = [tuple(row) for row in top_borrowers(_conn, 3)]
assert _got == [("Ada", 4), ("Grace", 3), ("Linus", 1)], f"got {_got!r}"
assert [tuple(r) for r in top_borrowers(_conn, 1)] == [("Ada", 4)], "limit is a bound parameter"
assert all(row[0] != "Barbara" for row in top_borrowers(_conn, 10)), \
    "a member with no loans should not appear in a join over loan"
'''},
                    {"name": "Quotes in an argument are data, not SQL", "code": r'''
_nasty = "x'; DROP TABLE book; --"
assert titles_by_author(_conn, _nasty) == [], "an unknown author gives an empty list"
assert _conn.execute("SELECT COUNT(*) FROM book").fetchone()[0] == 7, \
    "the book table should still be there — bind arguments, never format them into the SQL"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Design theory and normalisation",
            "summary": "Functional dependencies decide the schema; you only have to compute.",
            "concepts": [
                "A functional dependency X → Y is a constraint on every legal instance, not on one table",
                "Armstrong's axioms, and closure X+ as the decidable form of implication",
                "Superkey: X+ ⊇ R. Candidate key: a superkey with no proper subset that is one",
                "Update, insertion and deletion anomalies are the symptom; a bad dependency is the cause",
                "BCNF: for every non-trivial X → Y in R, X is a superkey of R",
                "3NF weakens BCNF to keep dependency preservation, which BCNF cannot always give you",
                "Projecting a dependency set onto a sub-relation is a closure computation over its subsets",
            ],
            "lab": {
                "title": "Closures, candidate keys and a BCNF decomposer",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Attributes are plain strings. A relation is a set of attribute names. A
functional dependency is a `(frozenset, frozenset)` pair.

**`parse_fds(text)`** — one dependency per line, `A B -> C D`, with `#` comments
and blank lines ignored. Returns a list of pairs. A line with no `->`, or with an
empty side, raises `ValueError`.

**`closure(attributes, fds)`** — the attribute closure `X+`, as a `frozenset`.
Apply every dependency whose left side is already contained, until nothing grows.

```text
closure({"A"}, parse_fds("A -> B\nB -> C"))  ->  {"A", "B", "C"}
closure(set(), fds)                          ->  set()
```

**`is_superkey(attributes, relation, fds)`** — does `X+` cover the whole relation?

**`candidate_keys(relation, fds)`** — every minimal superkey, as a list of
frozensets sorted by size then alphabetically. Try subsets smallest first and
skip any that already contain a key you have found.

**`project_fds(relation, fds)`** — the dependencies that hold on a sub-relation:
for each non-empty proper subset `X` of the sub-relation, `X → (X+ ∩ relation) − X`
when that right side is non-empty. Sorted by left-side size, then alphabetically.

**`bcnf_violations(relation, fds)`** — every `X → Y − X` where the dependency lies
inside the relation, `Y − X` is non-empty, and `X` is not a superkey. Sorted.

**`decompose(relation, fds)`** — apply the standard algorithm: project the
dependencies onto the relation, take the first violation `X → Y`, split into
`X ∪ Y` and `(R − Y) ∪ X`, and recurse on both halves against the *original*
dependency set. A relation with no violations returns `[relation]`. Results are
deduplicated and sorted by size then alphabetically.

```text
R = {"A", "B", "C"},  fds = "A B -> C" and "C -> B"
candidate_keys      -> [{"A","B"}, {"A","C"}]
bcnf_violations     -> [({"C"}, {"B"})]
decompose           -> [{"A","C"}, {"B","C"}]
```
''',
                "files": [{"name": "main.py", "content": r'''
import itertools


def parse_fds(text):
    """One 'A B -> C' per line into (frozenset lhs, frozenset rhs) pairs."""
    # your code here


def closure(attributes, fds):
    """The attribute closure of a set under the dependencies."""
    # your code here


def is_superkey(attributes, relation, fds):
    """True when the closure covers the whole relation."""
    # your code here


def candidate_keys(relation, fds):
    """Every minimal superkey, sorted by size then alphabetically."""
    # your code here


def project_fds(relation, fds):
    """The dependencies that hold on a sub-relation."""
    # your code here


def bcnf_violations(relation, fds):
    """Non-trivial dependencies whose left side is not a superkey."""
    # your code here


def decompose(relation, fds):
    """A BCNF decomposition of the relation."""
    # your code here


FDS = parse_fds("A B -> C\nC -> B")
R = {"A", "B", "C"}
print([sorted(k) for k in (candidate_keys(R, FDS) or [])])
print([sorted(part) for part in (decompose(R, FDS) or [])])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import itertools


def parse_fds(text):
    """One 'A B -> C' per line into (frozenset lhs, frozenset rhs) pairs."""
    fds = []
    for raw in text.split("\n"):
        line = raw.split("#")[0].strip()
        if not line:
            continue
        if "->" not in line:
            raise ValueError(f"no -> in dependency {raw!r}")
        left, _, right = line.partition("->")
        lhs = frozenset(left.replace(",", " ").split())
        rhs = frozenset(right.replace(",", " ").split())
        if not lhs or not rhs:
            raise ValueError(f"both sides must be non-empty in {raw!r}")
        fds.append((lhs, rhs))
    return fds


def closure(attributes, fds):
    """The attribute closure of a set under the dependencies."""
    result = set(attributes)
    growing = True
    while growing:
        growing = False
        for lhs, rhs in fds:
            if lhs <= result and not rhs <= result:
                result |= rhs
                growing = True
    return frozenset(result)


def is_superkey(attributes, relation, fds):
    """True when the closure covers the whole relation."""
    return set(relation) <= closure(attributes, fds)


def candidate_keys(relation, fds):
    """Every minimal superkey, sorted by size then alphabetically."""
    attributes = sorted(relation)
    keys = []
    for size in range(1, len(attributes) + 1):
        for combination in itertools.combinations(attributes, size):
            candidate = frozenset(combination)
            if any(key <= candidate for key in keys):
                continue
            if is_superkey(candidate, relation, fds):
                keys.append(candidate)
    return sorted(keys, key=lambda key: (len(key), sorted(key)))


def project_fds(relation, fds):
    """The dependencies that hold on a sub-relation."""
    relation = frozenset(relation)
    attributes = sorted(relation)
    projected = []
    for size in range(1, len(attributes)):
        for combination in itertools.combinations(attributes, size):
            lhs = frozenset(combination)
            rhs = (closure(lhs, fds) & relation) - lhs
            if rhs:
                projected.append((lhs, frozenset(rhs)))
    return sorted(projected, key=lambda fd: (len(fd[0]), sorted(fd[0]), sorted(fd[1])))


def bcnf_violations(relation, fds):
    """Non-trivial dependencies whose left side is not a superkey."""
    relation = frozenset(relation)
    found = []
    for lhs, rhs in fds:
        if not (lhs <= relation and rhs <= relation):
            continue
        extra = rhs - lhs
        if not extra:
            continue
        if is_superkey(lhs, relation, fds):
            continue
        found.append((frozenset(lhs), frozenset(extra)))
    return sorted(found, key=lambda fd: (sorted(fd[0]), sorted(fd[1])))


def decompose(relation, fds):
    """A BCNF decomposition of the relation."""
    relation = frozenset(relation)
    violations = bcnf_violations(relation, project_fds(relation, fds))
    if not violations:
        return [relation]
    lhs, rhs = violations[0]
    halves = [lhs | rhs, (relation - rhs) | lhs]
    pieces = []
    for half in halves:
        for piece in decompose(half, fds):
            if piece not in pieces:
                pieces.append(piece)
    return sorted(pieces, key=lambda part: (len(part), sorted(part)))


FDS = parse_fds("A B -> C\nC -> B")
R = {"A", "B", "C"}
print([sorted(k) for k in candidate_keys(R, FDS)])
print([sorted(part) for part in decompose(R, FDS)])
'''}],
                "hints": [
                    "`closure` is a fixed-point loop: keep sweeping the dependency list until a whole pass adds nothing.",
                    "`itertools.combinations(sorted(relation), size)` for size 1, 2, 3, … visits subsets smallest first, which is exactly the order minimality needs.",
                    "`project_fds` is where the real work is: for each proper subset X of the piece, the projected right side is `(closure(X, fds) & piece) - X`.",
                    "In `decompose`, recurse with the *original* dependency set and re-project inside each call — projecting a projection quietly loses dependencies.",
                ],
                "tests": [
                    {"name": "Parsing dependencies", "code": r'''
_fds = parse_fds("A B -> C\n# a comment\n\nC -> B\n")
assert len(_fds) == 2, f"expected 2 dependencies, got {len(_fds)}"
assert _fds[0] == (frozenset({"A", "B"}), frozenset({"C"})), f"got {_fds[0]!r}"
assert _fds[1] == (frozenset({"C"}), frozenset({"B"})), f"got {_fds[1]!r}"
for _bad in ["A B C", "-> C", "A ->", "A -> \n"]:
    try:
        parse_fds(_bad)
        assert False, f"parse_fds({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Attribute closure reaches a fixed point", "code": r'''
_chain = parse_fds("A -> B\nB -> C\nC -> D")
assert closure({"A"}, _chain) == frozenset({"A", "B", "C", "D"}), \
    f"got {sorted(closure({'A'}, _chain))!r}"
assert closure({"C"}, _chain) == frozenset({"C", "D"}), f"got {sorted(closure({'C'}, _chain))!r}"
assert closure(set(), _chain) == frozenset(), "an empty set implies nothing here"
assert closure({"D"}, []) == frozenset({"D"}), "with no dependencies, X+ is X"
_multi = parse_fds("A B -> C\nA -> D")
assert closure({"A"}, _multi) == frozenset({"A", "D"}), "A alone does not fire A B -> C"
assert closure({"A", "B"}, _multi) == frozenset({"A", "B", "C", "D"}), "both sides fire"
'''},
                    {"name": "Superkeys and candidate keys", "code": r'''
_r = {"A", "B", "C"}
_fds = parse_fds("A B -> C\nC -> B")
assert is_superkey({"A", "B"}, _r, _fds), "A B determines C, so it is a superkey"
assert not is_superkey({"C"}, _r, _fds), "C+ is {B, C}, which misses A"
_keys = [sorted(k) for k in candidate_keys(_r, _fds)]
assert _keys == [["A", "B"], ["A", "C"]], f"candidate keys came out as {_keys!r}"
_chain = parse_fds("A -> B\nB -> C\nC -> D")
assert [sorted(k) for k in candidate_keys({"A", "B", "C", "D"}, _chain)] == [["A"]], \
    "A alone determines everything in the chain"
assert [sorted(k) for k in candidate_keys({"A", "B"}, [])] == [["A", "B"]], \
    "with no dependencies the only key is the whole relation"
'''},
                    {"name": "Projecting dependencies onto a piece", "code": r'''
_chain = parse_fds("A -> B\nB -> C\nC -> D")
_p = [(sorted(l), sorted(r)) for l, r in project_fds({"A", "B", "D"}, _chain)]
assert (["A"], ["B", "D"]) in _p, f"A should determine B and D on that piece; got {_p!r}"
assert (["B"], ["D"]) in _p, f"B should determine D on that piece; got {_p!r}"
assert all(set(l) | set(r) <= {"A", "B", "D"} for l, r in _p), \
    "a projected dependency never mentions an attribute outside the piece"
assert project_fds({"A", "B"}, []) == [], "no dependencies project to no dependencies"
'''},
                    {"name": "BCNF violations", "code": r'''
_r = {"A", "B", "C"}
_fds = parse_fds("A B -> C\nC -> B")
_v = [(sorted(l), sorted(r)) for l, r in bcnf_violations(_r, _fds)]
assert _v == [(["C"], ["B"])], f"expected only C -> B to violate, got {_v!r}"
assert bcnf_violations({"A", "B"}, parse_fds("A -> B")) == [], \
    "A -> B on {A, B} is fine: A is a key"
assert bcnf_violations({"A", "B"}, parse_fds("A B -> A")) == [], \
    "a trivial dependency is never a violation"
_chain = parse_fds("A -> B\nB -> C\nC -> D")
_v = [(sorted(l), sorted(r)) for l, r in bcnf_violations({"A", "B", "C", "D"}, _chain)]
assert _v == [(["B"], ["C"]), (["C"], ["D"])], f"got {_v!r}"
'''},
                    {"name": "Decomposition of the classic example", "code": r'''
_fds = parse_fds("A B -> C\nC -> B")
_parts = [sorted(p) for p in decompose({"A", "B", "C"}, _fds)]
assert _parts == [["A", "C"], ["B", "C"]], f"got {_parts!r}"
assert decompose({"A", "B"}, parse_fds("A -> B")) == [frozenset({"A", "B"})], \
    "a relation already in BCNF comes back unchanged"
'''},
                    {"name": "Decomposition of the transitive chain", "code": r'''
_chain = parse_fds("A -> B\nB -> C\nC -> D")
_parts = decompose({"A", "B", "C", "D"}, _chain)
assert [sorted(p) for p in _parts] == [["A", "B"], ["B", "C"], ["C", "D"]], \
    f"got {[sorted(p) for p in _parts]!r}"
_union = set()
for _p in _parts:
    _union |= set(_p)
assert _union == {"A", "B", "C", "D"}, f"the pieces must cover the relation, they cover {_union!r}"
for _p in _parts:
    assert bcnf_violations(_p, project_fds(_p, _chain)) == [], \
        f"piece {sorted(_p)!r} is still not in BCNF"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Storage, indexing and access paths",
            "summary": "The optimiser's only real question: how many pages will this cost?",
            "concepts": [
                "Records live in pages; the page, not the row, is the unit of I/O",
                "A B+-tree keeps all data in the leaves and all leaves at the same depth",
                "Fan-out sets the height: height grows like log_f(n), which is why three levels is usually enough",
                "Clustered versus unclustered: whether the heap order matches the index order",
                "Selectivity, and why a matching index can still lose to a sequential scan",
                "An index lookup on an unclustered index costs about one page per matching row",
                "Covering indexes remove the heap fetch entirely, which changes the crossover point",
            ],
            "lab": {
                "title": "Index versus scan: a cost model that decides",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Rows are dicts with an `"id"`. A table of `n` rows at `rows_per_page` rows per
page costs `ceil(n / rows_per_page)` page reads to scan.

**`page_count(rows, rows_per_page)`** — the ceiling division, using integers only.
`ValueError` for a negative row count or a page size below 1.

**`full_scan(rows, rows_per_page, predicate)`** — `(matching rows, pages read)`.
A scan reads every page whatever the predicate says.

**`BPlusIndex(rows, key, fanout)`** — entries are `(key value, row id)` pairs kept
sorted. `fanout` below 2 raises `ValueError`.

- `entries` — the sorted pair list.
- `height` — number of levels including the leaf level. Leaves hold `fanout`
  entries each; each level above holds `fanout` children. An empty index has
  height 1.
- `search(key)` — row ids with exactly that key, in sorted key order.
- `range_search(low, high)` — row ids with `low <= key <= high`, inclusive.
  Use `bisect`, not a linear walk: the point of the structure is that you do not
  look at every entry.

**`index_cost(index, matches, rows_per_page, clustered=False)`**

```text
matches == 0            ->  height                       (descend, find nothing)
otherwise               ->  (height - 1)                 internal nodes
                          + page_count(matches, fanout)  leaf pages scanned
                          + matches                      one heap page per row, unclustered
                          or page_count(matches, rows_per_page) when clustered
```

**`choose_plan(row_count, rows_per_page, index, matches, clustered=False)`** —
`{"scan_cost", "index_cost", "plan"}` where `plan` is `"index"` only when it is
strictly cheaper; a tie goes to `"scan"`.

**`crossover(row_count, rows_per_page, index, clustered=False)`** — the smallest
number of matching rows for which the scan wins, or `row_count + 1` if it never
does.

For the 1000-row demo table (50 rows per page, fan-out 100) the unclustered index
loses from 18 matching rows onward — 1.8% selectivity — while the clustered one
holds on until 601.
''',
                "files": [{"name": "main.py", "content": r'''
from bisect import bisect_left, bisect_right

ROWS = [{"id": i, "year": 1900 + (i % 100), "title": f"row {i}"} for i in range(1000)]
ROWS_PER_PAGE = 50
FANOUT = 100


def page_count(rows, rows_per_page):
    """Pages needed to hold that many rows. ValueError on nonsense input."""
    # your code here


def full_scan(rows, rows_per_page, predicate):
    """(matching rows, pages read) for a sequential scan."""
    # your code here


class BPlusIndex:
    def __init__(self, rows, key, fanout):
        """Build the sorted (key, row id) entry list."""
        # your code here

    @property
    def height(self):
        """Levels in the tree, leaves included; 1 for an empty index."""
        # your code here

    def search(self, key):
        """Row ids whose key equals this one."""
        # your code here

    def range_search(self, low, high):
        """Row ids with low <= key <= high."""
        # your code here


def index_cost(index, matches, rows_per_page, clustered=False):
    """Page reads for an index lookup returning that many rows."""
    # your code here


def choose_plan(row_count, rows_per_page, index, matches, clustered=False):
    """{'scan_cost', 'index_cost', 'plan'} — ties go to the scan."""
    # your code here


def crossover(row_count, rows_per_page, index, clustered=False):
    """Smallest match count for which the scan wins."""
    # your code here


index = BPlusIndex(ROWS, "year", FANOUT)
print("height:", index.height, "matches for 1950:", len(index.search(1950)))
for flag in (False, True):
    print("clustered" if flag else "unclustered", "crossover:",
          crossover(len(ROWS), ROWS_PER_PAGE, index, flag))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
from bisect import bisect_left, bisect_right

ROWS = [{"id": i, "year": 1900 + (i % 100), "title": f"row {i}"} for i in range(1000)]
ROWS_PER_PAGE = 50
FANOUT = 100


def page_count(rows, rows_per_page):
    """Pages needed to hold that many rows. ValueError on nonsense input."""
    if rows < 0:
        raise ValueError(f"row count cannot be negative: {rows!r}")
    if rows_per_page < 1:
        raise ValueError(f"a page must hold at least one row: {rows_per_page!r}")
    return -(-rows // rows_per_page)


def full_scan(rows, rows_per_page, predicate):
    """(matching rows, pages read) for a sequential scan."""
    matches = [row for row in rows if predicate(row)]
    return matches, page_count(len(rows), rows_per_page)


class BPlusIndex:
    """A B+-tree modelled by its sorted leaf sequence and its fan-out."""

    def __init__(self, rows, key, fanout):
        """Build the sorted (key, row id) entry list."""
        if fanout < 2:
            raise ValueError(f"fan-out must be at least 2, got {fanout!r}")
        self.key = key
        self.fanout = fanout
        self.entries = sorted((row[key], row["id"]) for row in rows)
        self.keys = [entry[0] for entry in self.entries]

    @property
    def height(self):
        """Levels in the tree, leaves included; 1 for an empty index."""
        nodes = max(1, page_count(len(self.entries), self.fanout))
        levels = 1
        while nodes > 1:
            nodes = page_count(nodes, self.fanout)
            levels += 1
        return levels

    def search(self, key):
        """Row ids whose key equals this one."""
        low = bisect_left(self.keys, key)
        high = bisect_right(self.keys, key)
        return [row_id for _key, row_id in self.entries[low:high]]

    def range_search(self, low, high):
        """Row ids with low <= key <= high."""
        start = bisect_left(self.keys, low)
        stop = bisect_right(self.keys, high)
        return [row_id for _key, row_id in self.entries[start:stop]]


def index_cost(index, matches, rows_per_page, clustered=False):
    """Page reads for an index lookup returning that many rows."""
    if matches == 0:
        return index.height
    cost = index.height - 1 + page_count(matches, index.fanout)
    cost += page_count(matches, rows_per_page) if clustered else matches
    return cost


def choose_plan(row_count, rows_per_page, index, matches, clustered=False):
    """{'scan_cost', 'index_cost', 'plan'} — ties go to the scan."""
    scan = page_count(row_count, rows_per_page)
    lookup = index_cost(index, matches, rows_per_page, clustered)
    return {"scan_cost": scan, "index_cost": lookup,
            "plan": "index" if lookup < scan else "scan"}


def crossover(row_count, rows_per_page, index, clustered=False):
    """Smallest match count for which the scan wins."""
    for matches in range(row_count + 1):
        if choose_plan(row_count, rows_per_page, index, matches, clustered)["plan"] == "scan":
            return matches
    return row_count + 1


index = BPlusIndex(ROWS, "year", FANOUT)
print("height:", index.height, "matches for 1950:", len(index.search(1950)))
for flag in (False, True):
    print("clustered" if flag else "unclustered", "crossover:",
          crossover(len(ROWS), ROWS_PER_PAGE, index, flag))
'''}],
                "hints": [
                    "Ceiling division without floats: `-(-rows // rows_per_page)`.",
                    "For `height`, start from the number of leaf pages and keep dividing by the fan-out until one node is left, counting levels as you go.",
                    "Keep a parallel list of just the key values so `bisect_left` / `bisect_right` can work on it directly; the slice between them is every matching entry.",
                    "`crossover` needs no algebra — the cost is monotone in the match count, so walk upwards and return the first count at which `choose_plan` says 'scan'.",
                ],
                "tests": [
                    {"name": "page_count rounds up and refuses nonsense", "code": r'''
for _rows, _per, _want in [(0, 50, 0), (1, 50, 1), (50, 50, 1), (51, 50, 2), (1000, 50, 20)]:
    _got = page_count(_rows, _per)
    assert _got == _want, f"page_count({_rows}, {_per}) gave {_got!r}, expected {_want}"
for _args in [(-1, 50), (10, 0), (10, -5)]:
    try:
        page_count(*_args)
        assert False, f"page_count{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Tree height follows the fan-out", "code": r'''
_small = [{"id": i, "k": i} for i in range(10)]
assert BPlusIndex(_small, "k", 100).height == 1, "ten entries fit in one leaf"
assert BPlusIndex([], "k", 100).height == 1, "an empty index still has one level"
assert BPlusIndex(ROWS, "year", 100).height == 2, \
    f"1000 entries at fan-out 100 is 10 leaves under one root, got {BPlusIndex(ROWS, 'year', 100).height}"
_hundred = [{"id": i, "k": i} for i in range(100)]
assert BPlusIndex(_hundred, "k", 4).height == 4, \
    f"100 entries at fan-out 4 is 25 -> 7 -> 2 -> 1, got {BPlusIndex(_hundred, 'k', 4).height}"
try:
    BPlusIndex(ROWS, "year", 1)
    assert False, "a fan-out of 1 should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Equality and range search", "code": r'''
_idx = BPlusIndex(ROWS, "year", FANOUT)
assert len(_idx.entries) == 1000, f"the index holds {len(_idx.entries)} entries, expected 1000"
_got = _idx.search(1950)
assert _got == [50, 150, 250, 350, 450, 550, 650, 750, 850, 950], f"search(1950) gave {_got!r}"
assert _idx.search(1899) == [] and _idx.search(2000) == [], "a key nobody has gives []"
_range = _idx.range_search(1950, 1959)
assert len(_range) == 100, f"1950..1959 covers 100 rows, got {len(_range)}"
assert _idx.range_search(1950, 1950) == _got, "an inclusive range of one key equals a search"
assert _idx.range_search(2000, 2100) == [], "an empty range gives []"
'''},
                    {"name": "full_scan reads every page regardless", "code": r'''
_matches, _cost = full_scan(ROWS, ROWS_PER_PAGE, lambda row: row["year"] == 1950)
assert _cost == 20, f"a 1000-row table at 50 rows per page costs 20 pages, got {_cost}"
assert [row["id"] for row in _matches] == BPlusIndex(ROWS, "year", FANOUT).search(1950), \
    "the scan and the index must agree on which rows match"
_none, _cost = full_scan(ROWS, ROWS_PER_PAGE, lambda row: False)
assert _none == [] and _cost == 20, f"a scan that matches nothing still costs 20, got {_cost}"
'''},
                    {"name": "The cost model", "code": r'''
_idx = BPlusIndex(ROWS, "year", FANOUT)
for _matches, _clustered, _want in [(0, False, 2), (1, False, 3), (10, False, 12),
                                    (50, False, 52), (1, True, 3), (50, True, 3),
                                    (100, True, 4), (0, True, 2)]:
    _got = index_cost(_idx, _matches, ROWS_PER_PAGE, _clustered)
    assert _got == _want, \
        f"index_cost(matches={_matches}, clustered={_clustered}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "choose_plan picks the cheaper access path", "code": r'''
_idx = BPlusIndex(ROWS, "year", FANOUT)
_plan = choose_plan(1000, ROWS_PER_PAGE, _idx, 10)
assert _plan["scan_cost"] == 20 and _plan["index_cost"] == 12, f"got {_plan!r}"
assert _plan["plan"] == "index", f"12 pages beats 20, got {_plan!r}"
_plan = choose_plan(1000, ROWS_PER_PAGE, _idx, 100)
assert _plan["plan"] == "scan", f"102 pages loses to 20, got {_plan!r}"
_plan = choose_plan(1000, ROWS_PER_PAGE, _idx, 18)
assert _plan["index_cost"] == 20 and _plan["plan"] == "scan", \
    f"a tie should go to the scan, got {_plan!r}"
'''},
                    {"name": "Where the crossover sits", "code": r'''
_idx = BPlusIndex(ROWS, "year", FANOUT)
_un = crossover(1000, ROWS_PER_PAGE, _idx, False)
assert _un == 18, f"the unclustered crossover is 18 matching rows, got {_un}"
_cl = crossover(1000, ROWS_PER_PAGE, _idx, True)
assert _cl == 601, f"the clustered crossover is 601 matching rows, got {_cl}"
assert _cl > _un, "clustering must widen the range where the index wins"
assert "crossover" in _out, "the demo should print both crossover points"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Transactions and concurrency control",
            "summary": "Interleaving is what makes a database fast, and what makes it wrong.",
            "concepts": [
                "ACID: atomicity and durability come from logging, isolation from concurrency control",
                "Lost update, dirty read and unrepeatable read as concrete interleavings",
                "Two operations conflict when they touch the same item, differ in transaction, and one writes",
                "A schedule is conflict-serialisable exactly when its precedence graph is acyclic",
                "A topological order of that graph is an equivalent serial schedule",
                "Two-phase locking: a growing phase then a shrinking phase, which guarantees serialisability",
                "Strict 2PL holds every lock to commit, so cascading aborts cannot happen — at the price of deadlock",
            ],
            "lab": {
                "title": "Precedence graphs and a two-phase-locking scheduler",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A schedule is written as whitespace-separated operations: `r1(A)` is transaction
1 reading item `A`, `w2(B)` is transaction 2 writing `B`, and `c1` is transaction
1 committing.

**`parse_schedule(text)`** — a list of `{"op", "txn", "item"}` dicts, with `item`
`None` for a commit. Anything unparseable, a read or write with no item, or a
commit with one, raises `ValueError`.

**`format_op(op)`** — back to `"r1(A)"` or `"c1"`.

**`conflicts(ops)`** — every ordered pair `(earlier txn, later txn, item)` where
two operations of different transactions touch the same item and at least one of
them writes.

**`precedence_graph(ops)`** — `{txn: set of txns it must precede}`, with an entry
for every transaction that appears, even one with no outgoing edges.

**`has_cycle(graph)`** — depth-first search with a grey/black colouring.

**`is_conflict_serialisable(ops)`** — the graph is acyclic.

**`serial_order(ops)`** — an equivalent serial order as a list of transaction ids,
or `None` when the schedule is not serialisable. Break ties by taking the
smallest available transaction id, so the answer is deterministic.

**`two_phase_lock(ops)`** — a strict 2PL scheduler. Returns
`{"order", "aborted", "deadlocks"}` where `order` is the executed operations as
strings.

- A read needs a shared lock, a write an exclusive one. Shared locks coexist; an
  exclusive lock excludes everyone else. A transaction that already holds the
  only shared lock on an item may upgrade it.
- Take the first operation in the queue whose transaction is not blocked. If its
  lock is refused, mark that transaction blocked and move on.
- A commit releases every lock the transaction holds and unblocks everybody, so
  the queue is retried from the front in its original order.
- If every remaining transaction is blocked, that is a deadlock: abort the
  highest-numbered blocked transaction, release its locks, drop its remaining
  operations, and carry on. Count each deadlock.

```text
two_phase_lock(parse_schedule("r1(A) w2(A) w1(A) c1 c2"))["order"]
  ->  ["r1(A)", "w1(A)", "c1", "w2(A)", "c2"]
```
''',
                "files": [{"name": "main.py", "content": r'''
import re

OPERATION = re.compile(r"^([rwc])(\d+)(?:\(([A-Za-z_][A-Za-z_0-9]*)\))?$")

SERIALISABLE = "r1(A) w2(A) w1(B) r2(B) c1 c2"
CYCLIC = "r1(A) w2(A) w2(B) r1(B) c1 c2"
DEADLOCK = "r1(A) r2(B) w1(B) w2(A) c1 c2"


def parse_schedule(text):
    """Operation tokens into {'op', 'txn', 'item'} dicts."""
    # your code here


def format_op(op):
    """One operation dict back into 'r1(A)' or 'c1'."""
    # your code here


def conflicts(ops):
    """(earlier txn, later txn, item) for every conflicting ordered pair."""
    # your code here


def precedence_graph(ops):
    """txn -> set of transactions it must precede."""
    # your code here


def has_cycle(graph):
    """True when the directed graph contains a cycle."""
    # your code here


def is_conflict_serialisable(ops):
    """True when the precedence graph is acyclic."""
    # your code here


def serial_order(ops):
    """An equivalent serial order, smallest id first, or None."""
    # your code here


def two_phase_lock(ops):
    """{'order', 'aborted', 'deadlocks'} for a strict 2PL scheduler."""
    # your code here


for _name, _text in [("serialisable", SERIALISABLE), ("cyclic", CYCLIC), ("deadlock", DEADLOCK)]:
    _ops = parse_schedule(_text)
    print(_name, "->", is_conflict_serialisable(_ops), serial_order(_ops), two_phase_lock(_ops))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import re

OPERATION = re.compile(r"^([rwc])(\d+)(?:\(([A-Za-z_][A-Za-z_0-9]*)\))?$")

SERIALISABLE = "r1(A) w2(A) w1(B) r2(B) c1 c2"
CYCLIC = "r1(A) w2(A) w2(B) r1(B) c1 c2"
DEADLOCK = "r1(A) r2(B) w1(B) w2(A) c1 c2"


def parse_schedule(text):
    """Operation tokens into {'op', 'txn', 'item'} dicts."""
    ops = []
    for token in text.replace(",", " ").split():
        found = OPERATION.match(token)
        if not found:
            raise ValueError(f"cannot parse operation {token!r}")
        kind, txn, item = found.group(1), int(found.group(2)), found.group(3)
        if kind in ("r", "w") and item is None:
            raise ValueError(f"{token!r} needs a data item")
        if kind == "c" and item is not None:
            raise ValueError(f"a commit takes no data item: {token!r}")
        ops.append({"op": kind, "txn": txn, "item": item})
    return ops


def format_op(op):
    """One operation dict back into 'r1(A)' or 'c1'."""
    if op["item"] is None:
        return f"{op['op']}{op['txn']}"
    return f"{op['op']}{op['txn']}({op['item']})"


def conflicts(ops):
    """(earlier txn, later txn, item) for every conflicting ordered pair."""
    found = []
    for first in range(len(ops)):
        earlier = ops[first]
        if earlier["op"] == "c":
            continue
        for second in range(first + 1, len(ops)):
            later = ops[second]
            if later["op"] == "c":
                continue
            if earlier["txn"] == later["txn"] or earlier["item"] != later["item"]:
                continue
            if earlier["op"] == "r" and later["op"] == "r":
                continue
            found.append((earlier["txn"], later["txn"], earlier["item"]))
    return found


def precedence_graph(ops):
    """txn -> set of transactions it must precede."""
    graph = {op["txn"]: set() for op in ops}
    for earlier, later, _item in conflicts(ops):
        graph[earlier].add(later)
    return graph


def has_cycle(graph):
    """True when the directed graph contains a cycle."""
    colour = {node: "white" for node in graph}

    def visit(node):
        colour[node] = "grey"
        for neighbour in graph.get(node, ()):
            if colour.get(neighbour) == "grey":
                return True
            if colour.get(neighbour, "white") == "white" and visit(neighbour):
                return True
        colour[node] = "black"
        return False

    return any(visit(node) for node in sorted(graph) if colour[node] == "white")


def is_conflict_serialisable(ops):
    """True when the precedence graph is acyclic."""
    return not has_cycle(precedence_graph(ops))


def serial_order(ops):
    """An equivalent serial order, smallest id first, or None."""
    graph = precedence_graph(ops)
    incoming = {node: 0 for node in graph}
    for node, targets in graph.items():
        for target in targets:
            incoming[target] += 1
    ready = sorted(node for node in graph if incoming[node] == 0)
    order = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for target in sorted(graph[node]):
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
        ready.sort()
    return order if len(order) == len(graph) else None


def two_phase_lock(ops):
    """{'order', 'aborted', 'deadlocks'} for a strict 2PL scheduler."""
    queue = [dict(op) for op in ops]
    shared = {}
    exclusive = {}
    held = {}
    blocked = set()
    order = []
    aborted = []
    deadlocks = 0

    def release(txn):
        for item in list(held.get(txn, ())):
            shared.get(item, set()).discard(txn)
            if exclusive.get(item) == txn:
                del exclusive[item]
        held.pop(txn, None)

    def can_lock(txn, item, mode):
        holder = exclusive.get(item)
        if holder is not None and holder != txn:
            return False
        if mode == "w" and (shared.get(item, set()) - {txn}):
            return False
        return True

    def grant(txn, item, mode):
        held.setdefault(txn, set()).add(item)
        if mode == "w":
            exclusive[item] = txn
            shared.setdefault(item, set()).discard(txn)
        elif exclusive.get(item) != txn:
            shared.setdefault(item, set()).add(txn)

    while queue:
        position = None
        for index, op in enumerate(queue):
            if op["txn"] not in blocked:
                position = index
                break
        if position is None:
            deadlocks += 1
            victim = max(blocked)
            release(victim)
            aborted.append(victim)
            queue = [op for op in queue if op["txn"] != victim]
            blocked = set()
            continue
        op = queue[position]
        if op["op"] == "c":
            release(op["txn"])
            order.append(format_op(op))
            queue.pop(position)
            blocked = set()
        elif can_lock(op["txn"], op["item"], op["op"]):
            grant(op["txn"], op["item"], op["op"])
            order.append(format_op(op))
            queue.pop(position)
        else:
            blocked.add(op["txn"])
    return {"order": order, "aborted": aborted, "deadlocks": deadlocks}


for _name, _text in [("serialisable", SERIALISABLE), ("cyclic", CYCLIC), ("deadlock", DEADLOCK)]:
    _ops = parse_schedule(_text)
    print(_name, "->", is_conflict_serialisable(_ops), serial_order(_ops), two_phase_lock(_ops))
'''}],
                "hints": [
                    "`OPERATION.match(token)` is supplied: group 1 is the kind, group 2 the transaction number, group 3 the item or `None`.",
                    "Conflicts are a double loop over the operation list; skip commits, skip same-transaction pairs, skip read/read.",
                    "For `has_cycle`, colour a node grey on entry and black on exit — meeting a grey node means you have walked back into the path you are on.",
                    "In the scheduler, never pop an operation you could not grant: leave it in the queue, mark its transaction blocked, and let the commit that releases the lock clear every block at once.",
                ],
                "tests": [
                    {"name": "Parsing and formatting operations", "code": r'''
_ops = parse_schedule("r1(A) w2(B) c1")
assert _ops[0] == {"op": "r", "txn": 1, "item": "A"}, f"got {_ops[0]!r}"
assert _ops[1] == {"op": "w", "txn": 2, "item": "B"}, f"got {_ops[1]!r}"
assert _ops[2] == {"op": "c", "txn": 1, "item": None}, f"got {_ops[2]!r}"
assert [format_op(op) for op in _ops] == ["r1(A)", "w2(B)", "c1"], \
    f"got {[format_op(op) for op in _ops]!r}"
assert parse_schedule("") == [], "an empty schedule parses to an empty list"
for _bad in ["x1(A)", "r1", "c1(A)", "r(A)", "rr1(A)", "w1(A"]:
    try:
        parse_schedule(_bad)
        assert False, f"parse_schedule({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Conflicting pairs", "code": r'''
_c = conflicts(parse_schedule("r1(A) w2(A) w1(B) r2(B) c1 c2"))
assert (1, 2, "A") in _c and (1, 2, "B") in _c, f"got {_c!r}"
assert len(_c) == 2, f"expected exactly 2 conflicting pairs, got {_c!r}"
assert conflicts(parse_schedule("r1(A) r2(A) c1 c2")) == [], "two reads never conflict"
assert conflicts(parse_schedule("w1(A) w1(A) c1")) == [], \
    "a transaction never conflicts with itself"
assert conflicts(parse_schedule("w1(A) w2(B) c1 c2")) == [], "different items never conflict"
'''},
                    {"name": "The precedence graph, and cycles in it", "code": r'''
_g = precedence_graph(parse_schedule("r1(A) w2(A) w1(B) r2(B) c1 c2"))
assert _g == {1: {2}, 2: set()}, f"got {_g!r}"
assert has_cycle({1: {2}, 2: {3}, 3: {1}}), "1 -> 2 -> 3 -> 1 is a cycle"
assert not has_cycle({1: {2}, 2: {3}, 3: set()}), "a chain is not a cycle"
assert not has_cycle({}), "an empty graph has no cycle"
assert not has_cycle({1: {2}, 2: set(), 3: {2}}), "a diamond without a back edge is acyclic"
'''},
                    {"name": "Serialisability of three schedules", "code": r'''
assert is_conflict_serialisable(parse_schedule(SERIALISABLE)), \
    "r1(A) w2(A) w1(B) r2(B) only ever puts 1 before 2"
assert not is_conflict_serialisable(parse_schedule(CYCLIC)), \
    "r1(A) w2(A) w2(B) r1(B) forces 1 before 2 and 2 before 1"
assert is_conflict_serialisable(parse_schedule("r1(A) w1(A) c1 r2(A) w2(A) c2")), \
    "a serial schedule is serialisable"
assert is_conflict_serialisable(parse_schedule("r1(A) r2(A) c1 c2")), \
    "reads alone never conflict"
'''},
                    {"name": "An equivalent serial order", "code": r'''
assert serial_order(parse_schedule(SERIALISABLE)) == [1, 2], \
    f"got {serial_order(parse_schedule(SERIALISABLE))!r}"
assert serial_order(parse_schedule(CYCLIC)) is None, "a cyclic schedule has no serial order"
_order = serial_order(parse_schedule("r2(A) w1(A) c1 c2"))
assert _order == [2, 1], f"the conflict puts 2 before 1, got {_order!r}"
_independent = serial_order(parse_schedule("w3(A) w1(B) w2(C) c1 c2 c3"))
assert _independent == [1, 2, 3], f"with no conflicts, ties go smallest first; got {_independent!r}"
'''},
                    {"name": "The scheduler blocks, then resumes on commit", "code": r'''
_result = two_phase_lock(parse_schedule("r1(A) w2(A) w1(A) c1 c2"))
assert _result["order"] == ["r1(A)", "w1(A)", "c1", "w2(A)", "c2"], f"got {_result['order']!r}"
assert _result["aborted"] == [] and _result["deadlocks"] == 0, f"got {_result!r}"
_serial = two_phase_lock(parse_schedule("r1(A) w1(A) c1 r2(A) w2(A) c2"))
assert _serial["order"] == ["r1(A)", "w1(A)", "c1", "r2(A)", "w2(A)", "c2"], \
    f"a serial schedule should run unchanged, got {_serial['order']!r}"
_readers = two_phase_lock(parse_schedule("r1(A) r2(A) c1 c2"))
assert _readers["order"] == ["r1(A)", "r2(A)", "c1", "c2"], \
    f"shared locks coexist, got {_readers['order']!r}"
'''},
                    {"name": "Deadlock is detected and broken", "code": r'''
_result = two_phase_lock(parse_schedule(DEADLOCK))
assert _result["deadlocks"] == 1, f"expected one deadlock, got {_result!r}"
assert _result["aborted"] == [2], f"the highest-numbered blocked transaction is the victim; got {_result!r}"
assert _result["order"] == ["r1(A)", "r2(B)", "w1(B)", "c1"], f"got {_result['order']!r}"
assert all(op.endswith("2") or "2(" not in op for op in _result["order"][3:]), \
    "no operation of the aborted transaction may run after the abort"
assert "deadlock" in _out or "aborted" in _out, "the demo should report on the deadlock schedule"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a migrated, indexed record store",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Everything so far, wired into the layer an application would actually import.
`store.py` holds the schema, the migrations and the repository and is what the
checks import; `main.py` is a demo that migrates, seeds and prints a cost report.

## Migrations

`MIGRATIONS` is an ordered list of `(name, sql script)` pairs. Migration *n* is
the *n*-th entry, counting from 1.

- `connect(path=":memory:")` — a connection with `row_factory = sqlite3.Row` and
  `PRAGMA foreign_keys = ON`.
- `schema_version(conn)` — `PRAGMA user_version`, which is 0 on a fresh database.
- `migrate(conn)` — apply every migration above the current version, in order,
  bumping `user_version` after each, and return the names applied. Running it a
  second time applies nothing and returns `[]`.

The three migrations are `0001_core` (`artist`, `album`), `0002_plays` (`play`)
and `0003_indexes` (indexes on `album.artist_id`, `album.year`, `play.album_id`).

| table | columns |
| --- | --- |
| `artist` | `id` PK, `name` NOT NULL UNIQUE, `country` NOT NULL |
| `album` | `id` PK, `artist_id` NOT NULL → `artist(id)` ON DELETE CASCADE, `title` NOT NULL, `year` NOT NULL CHECK 1900-2100, `tracks` NOT NULL CHECK > 0, UNIQUE (`artist_id`, `title`) |
| `play` | `id` PK, `album_id` NOT NULL → `album(id)` ON DELETE CASCADE, `day` NOT NULL |

## `Repository(conn)`

Every method returns plain Python values — never a `sqlite3.Row` — and every
value that came from a caller is bound with `?`.

- `add_artist(name, country)` / `add_album(artist_id, title, year, tracks)` /
  `add_play(album_id, day)` — return the new id.
- `get_album(album_id)` — `{"id", "title", "year", "tracks", "artist"}`.
- `albums_by_artist(name)` — that artist's albums as dicts, oldest first.
- `albums_per_decade()` — `(decade, count)` ascending, decade being `year // 10 * 10`.
- `top_artists(limit)` — `{"name", "plays"}` for the most-played artists, ties
  alphabetical, **including artists with no plays at all**.
- `delete_artist(artist_id)` — returns how many albums went with them.

`ValidationError` for a blank name, a duplicate, a year outside the range or a
track count below 1. `NotFound` for an id that is not there. Both subclass
`StoreError`, so a caller can catch one thing.

## Cost report

- `query_plan(conn, sql, params=())` — the `EXPLAIN QUERY PLAN` detail strings.
- `uses_index(conn, sql, params=())` — does any plan line mention `USING INDEX`
  or `USING COVERING INDEX`?
- `cost_report(conn, queries=None)` — for each `(name, sql, params)` in
  `NAMED_QUERIES`, a dict `{"name", "uses_index", "plan", "rows"}`.

`seed(repo)` loads the demo dataset and returns `{"artists", "albums", "plays"}`.
''',
        "deliverables": [
            "`store.py` — schema, migrations, repository and cost report, importable with no side effects",
            "`main.py` — a demo that connects, migrates, seeds, prints a summary and prints the cost report",
            "A `MIGRATIONS` list driven by `PRAGMA user_version`, safe to run repeatedly against the same database",
            "A repository whose methods return dicts and tuples, never `sqlite3.Row` objects",
            "`StoreError`, `ValidationError` and `NotFound` used consistently instead of leaking `sqlite3` exceptions",
            "A cost report that shows which of the named queries reaches an index and which scans",
        ],
        "constraints": [
            "Standard library only; `sqlite3` is the whole dependency list",
            "`store.py` must not print anything — running it produces no output",
            "Every caller-supplied value is bound with `?`; no SQL is built by string formatting",
            "Foreign keys are enforced, and deleting an artist must cascade rather than orphan rows",
            "Two repositories over two connections must not share state",
        ],
        "rubric": [
            {"criterion": "Schema and constraints", "weight": 25,
             "evidence": "Keys, CHECKs, UNIQUEs and ON DELETE CASCADE are declared and demonstrably enforced by the engine."},
            {"criterion": "Migrations", "weight": 20,
             "evidence": "migrate applies each script once in order, tracks user_version, and is a no-op on a database already at the latest version."},
            {"criterion": "Repository correctness", "weight": 30,
             "evidence": "Joins, grouping and the left join in top_artists return the specified shapes and orderings, with bound parameters throughout."},
            {"criterion": "Error handling", "weight": 15,
             "evidence": "ValidationError and NotFound are raised at the right boundaries; sqlite3.IntegrityError never escapes the repository."},
            {"criterion": "Cost reporting", "weight": 10,
             "evidence": "query_plan and uses_index read EXPLAIN QUERY PLAN correctly and distinguish an indexed search from a table scan."},
        ],
        "hints": [
            "Write `migrate` first and test it twice in a row — a migration runner you cannot re-run is not a migration runner.",
            "`PRAGMA user_version` takes no bound parameter, so build that one statement from an `int()` you control, and keep `?` everywhere else.",
            "`dict(row)` turns a `sqlite3.Row` into a plain dict; do it at the repository boundary so nothing above it depends on sqlite3.",
            "`top_artists` needs `LEFT JOIN album ... LEFT JOIN play ...` with `COUNT(play.id)`, not `COUNT(*)` — `COUNT(*)` counts the artist's own row and every artist would score at least 1.",
        ],
        "files": [
            {"name": "store.py", "content": r'''
import sqlite3


class StoreError(Exception):
    """Base class for everything this module raises."""


class ValidationError(StoreError):
    """The caller supplied something the schema will not accept."""


class NotFound(StoreError):
    """No row with that identifier."""


MIGRATIONS = [
    ("0001_core", """
-- your CREATE TABLE statements for artist and album
"""),
    ("0002_plays", """
-- your CREATE TABLE statement for play
"""),
    ("0003_indexes", """
-- your CREATE INDEX statements
"""),
]

DEMO_ARTISTS = [
    ("Kraftwerk", "Germany"),
    ("Alice Coltrane", "United States"),
    ("Fela Kuti", "Nigeria"),
    ("Tom Ze", "Brazil"),
]
DEMO_ALBUMS = [
    ("Kraftwerk", "Autobahn", 1974, 5),
    ("Kraftwerk", "Trans-Europe Express", 1977, 7),
    ("Kraftwerk", "Computer World", 1981, 8),
    ("Alice Coltrane", "Journey in Satchidananda", 1971, 5),
    ("Alice Coltrane", "Ptah, the El Daoud", 1970, 5),
    ("Fela Kuti", "Zombie", 1976, 4),
]
DEMO_PLAYS = [
    ("Autobahn", 3),
    ("Computer World", 1),
    ("Journey in Satchidananda", 4),
    ("Zombie", 2),
]

NAMED_QUERIES = [
    ("albums of one artist", "SELECT title FROM album WHERE artist_id = ?", (1,)),
    ("albums of one year", "SELECT title FROM album WHERE year = ?", (1974,)),
    ("albums by track count", "SELECT title FROM album WHERE tracks = ?", (5,)),
]


def connect(path=":memory:"):
    """A connection with row access by name and foreign keys enforced."""
    # your code here


def schema_version(conn):
    """The migration number this database has reached."""
    # your code here


def migrate(conn):
    """Apply every outstanding migration; return the names applied."""
    # your code here


class Repository:
    def __init__(self, conn):
        self.conn = conn

    def add_artist(self, name, country):
        """Insert an artist and return its id."""
        # your code here

    def add_album(self, artist_id, title, year, tracks):
        """Insert an album and return its id."""
        # your code here

    def add_play(self, album_id, day):
        """Insert a play and return its id."""
        # your code here

    def get_album(self, album_id):
        """One album as a dict, with its artist's name."""
        # your code here

    def albums_by_artist(self, name):
        """That artist's albums as dicts, oldest first."""
        # your code here

    def albums_per_decade(self):
        """(decade, album count), ascending."""
        # your code here

    def top_artists(self, limit):
        """Most-played artists first, ties alphabetical, zero-play artists included."""
        # your code here

    def delete_artist(self, artist_id):
        """Remove an artist and return how many albums went with them."""
        # your code here


def seed(repo):
    """Load the demo dataset; return the counts inserted."""
    # your code here


def query_plan(conn, sql, params=()):
    """The EXPLAIN QUERY PLAN detail strings for a statement."""
    # your code here


def uses_index(conn, sql, params=()):
    """True when the plan reaches an index rather than scanning."""
    # your code here


def cost_report(conn, queries=None):
    """One {'name', 'uses_index', 'plan', 'rows'} dict per named query."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from store import Repository, connect, cost_report, migrate, seed

conn = connect()
print("applied:", migrate(conn))
repo = Repository(conn)
print("seeded:", seed(repo))

print("albums per decade:", repo.albums_per_decade())
print("top artists:", repo.top_artists(4))

for entry in cost_report(conn):
    print(f"{entry['name']:<24} index={entry['uses_index']} rows={entry['rows']}")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "store.py", "content": r'''
import sqlite3


class StoreError(Exception):
    """Base class for everything this module raises."""


class ValidationError(StoreError):
    """The caller supplied something the schema will not accept."""


class NotFound(StoreError):
    """No row with that identifier."""


MIGRATIONS = [
    ("0001_core", """
CREATE TABLE artist (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL
);
CREATE TABLE album (
    id        INTEGER PRIMARY KEY,
    artist_id INTEGER NOT NULL REFERENCES artist(id) ON DELETE CASCADE,
    title     TEXT NOT NULL,
    year      INTEGER NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    tracks    INTEGER NOT NULL CHECK (tracks > 0),
    UNIQUE (artist_id, title)
);
"""),
    ("0002_plays", """
CREATE TABLE play (
    id       INTEGER PRIMARY KEY,
    album_id INTEGER NOT NULL REFERENCES album(id) ON DELETE CASCADE,
    day      TEXT NOT NULL
);
"""),
    ("0003_indexes", """
CREATE INDEX idx_album_artist ON album(artist_id);
CREATE INDEX idx_album_year ON album(year);
CREATE INDEX idx_play_album ON play(album_id);
"""),
]

DEMO_ARTISTS = [
    ("Kraftwerk", "Germany"),
    ("Alice Coltrane", "United States"),
    ("Fela Kuti", "Nigeria"),
    ("Tom Ze", "Brazil"),
]
DEMO_ALBUMS = [
    ("Kraftwerk", "Autobahn", 1974, 5),
    ("Kraftwerk", "Trans-Europe Express", 1977, 7),
    ("Kraftwerk", "Computer World", 1981, 8),
    ("Alice Coltrane", "Journey in Satchidananda", 1971, 5),
    ("Alice Coltrane", "Ptah, the El Daoud", 1970, 5),
    ("Fela Kuti", "Zombie", 1976, 4),
]
DEMO_PLAYS = [
    ("Autobahn", 3),
    ("Computer World", 1),
    ("Journey in Satchidananda", 4),
    ("Zombie", 2),
]

NAMED_QUERIES = [
    ("albums of one artist", "SELECT title FROM album WHERE artist_id = ?", (1,)),
    ("albums of one year", "SELECT title FROM album WHERE year = ?", (1974,)),
    ("albums by track count", "SELECT title FROM album WHERE tracks = ?", (5,)),
]


def connect(path=":memory:"):
    """A connection with row access by name and foreign keys enforced."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def schema_version(conn):
    """The migration number this database has reached."""
    return conn.execute("PRAGMA user_version").fetchone()[0]


def migrate(conn):
    """Apply every outstanding migration; return the names applied."""
    applied = []
    version = schema_version(conn)
    for number, (name, script) in enumerate(MIGRATIONS, 1):
        if number <= version:
            continue
        conn.executescript(script)
        # PRAGMA does not take a bound parameter; the value is an int we control.
        conn.execute(f"PRAGMA user_version = {int(number)}")
        applied.append(name)
    conn.commit()
    return applied


def require_text(value, field):
    """A stripped non-empty string, or ValidationError."""
    text = (value or "").strip() if isinstance(value, str) else ""
    if not text:
        raise ValidationError(f"{field} is required")
    return text


class Repository:
    """The only place in the program that knows SQL."""

    def __init__(self, conn):
        self.conn = conn

    def add_artist(self, name, country):
        """Insert an artist and return its id."""
        name = require_text(name, "artist name")
        country = require_text(country, "country")
        try:
            cursor = self.conn.execute(
                "INSERT INTO artist (name, country) VALUES (?, ?)", (name, country))
        except sqlite3.IntegrityError as error:
            raise ValidationError(f"artist {name!r} already exists") from error
        self.conn.commit()
        return cursor.lastrowid

    def add_album(self, artist_id, title, year, tracks):
        """Insert an album and return its id."""
        title = require_text(title, "album title")
        if not isinstance(year, int) or not 1900 <= year <= 2100:
            raise ValidationError(f"year {year!r} is outside 1900-2100")
        if not isinstance(tracks, int) or tracks < 1:
            raise ValidationError(f"track count {tracks!r} must be at least 1")
        if self.conn.execute("SELECT 1 FROM artist WHERE id = ?", (artist_id,)).fetchone() is None:
            raise NotFound(f"no artist with id {artist_id!r}")
        try:
            cursor = self.conn.execute(
                "INSERT INTO album (artist_id, title, year, tracks) VALUES (?, ?, ?, ?)",
                (artist_id, title, year, tracks))
        except sqlite3.IntegrityError as error:
            raise ValidationError(f"that artist already has an album {title!r}") from error
        self.conn.commit()
        return cursor.lastrowid

    def add_play(self, album_id, day):
        """Insert a play and return its id."""
        day = require_text(day, "day")
        if self.conn.execute("SELECT 1 FROM album WHERE id = ?", (album_id,)).fetchone() is None:
            raise NotFound(f"no album with id {album_id!r}")
        cursor = self.conn.execute(
            "INSERT INTO play (album_id, day) VALUES (?, ?)", (album_id, day))
        self.conn.commit()
        return cursor.lastrowid

    def get_album(self, album_id):
        """One album as a dict, with its artist's name."""
        row = self.conn.execute("""
            SELECT album.id, album.title, album.year, album.tracks, artist.name AS artist
              FROM album
              JOIN artist ON artist.id = album.artist_id
             WHERE album.id = ?
        """, (album_id,)).fetchone()
        if row is None:
            raise NotFound(f"no album with id {album_id!r}")
        return dict(row)

    def albums_by_artist(self, name):
        """That artist's albums as dicts, oldest first."""
        rows = self.conn.execute("""
            SELECT album.id, album.title, album.year, album.tracks
              FROM album
              JOIN artist ON artist.id = album.artist_id
             WHERE artist.name = ?
             ORDER BY album.year, album.title
        """, (name,)).fetchall()
        return [dict(row) for row in rows]

    def albums_per_decade(self):
        """(decade, album count), ascending."""
        rows = self.conn.execute("""
            SELECT (year / 10) * 10 AS decade, COUNT(*) AS albums
              FROM album
             GROUP BY decade
             ORDER BY decade
        """).fetchall()
        return [(row["decade"], row["albums"]) for row in rows]

    def top_artists(self, limit):
        """Most-played artists first, ties alphabetical, zero-play artists included."""
        rows = self.conn.execute("""
            SELECT artist.name AS name, COUNT(play.id) AS plays
              FROM artist
              LEFT JOIN album ON album.artist_id = artist.id
              LEFT JOIN play ON play.album_id = album.id
             GROUP BY artist.id, artist.name
             ORDER BY plays DESC, artist.name
             LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

    def delete_artist(self, artist_id):
        """Remove an artist and return how many albums went with them."""
        if self.conn.execute("SELECT 1 FROM artist WHERE id = ?", (artist_id,)).fetchone() is None:
            raise NotFound(f"no artist with id {artist_id!r}")
        albums = self.conn.execute(
            "SELECT COUNT(*) FROM album WHERE artist_id = ?", (artist_id,)).fetchone()[0]
        self.conn.execute("DELETE FROM artist WHERE id = ?", (artist_id,))
        self.conn.commit()
        return albums


def seed(repo):
    """Load the demo dataset; return the counts inserted."""
    artists = {}
    for name, country in DEMO_ARTISTS:
        artists[name] = repo.add_artist(name, country)
    albums = {}
    for artist, title, year, tracks in DEMO_ALBUMS:
        albums[title] = repo.add_album(artists[artist], title, year, tracks)
    plays = 0
    for title, count in DEMO_PLAYS:
        for offset in range(count):
            repo.add_play(albums[title], f"2026-05-{offset + 1:02d}")
            plays += 1
    return {"artists": len(artists), "albums": len(albums), "plays": plays}


def query_plan(conn, sql, params=()):
    """The EXPLAIN QUERY PLAN detail strings for a statement."""
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return [str(tuple(row)[-1]) for row in rows]


def uses_index(conn, sql, params=()):
    """True when the plan reaches an index rather than scanning."""
    return any("USING INDEX" in line or "USING COVERING INDEX" in line
               for line in query_plan(conn, sql, params))


def cost_report(conn, queries=None):
    """One {'name', 'uses_index', 'plan', 'rows'} dict per named query."""
    report = []
    for name, sql, params in (NAMED_QUERIES if queries is None else queries):
        report.append({
            "name": name,
            "uses_index": uses_index(conn, sql, params),
            "plan": query_plan(conn, sql, params),
            "rows": len(conn.execute(sql, params).fetchall()),
        })
    return report
'''},
            {"name": "main.py", "content": r'''
from store import Repository, connect, cost_report, migrate, schema_version, seed

conn = connect()
print("applied:", migrate(conn))
print("applied again:", migrate(conn))
print("schema version:", schema_version(conn))

repo = Repository(conn)
print("seeded:", seed(repo))
print()

print("albums per decade:", repo.albums_per_decade())
print("top artists:", repo.top_artists(4))
print("Kraftwerk:", [album["title"] for album in repo.albums_by_artist("Kraftwerk")])
print()

for entry in cost_report(conn):
    print(f"{entry['name']:<24} index={entry['uses_index']} rows={entry['rows']}")
    for line in entry["plan"]:
        print("   ", line)
'''},
        ],
        "tests": [
            {"name": "Migrations run once, in order", "code": r'''
from store import connect, migrate, schema_version
_conn = connect()
assert schema_version(_conn) == 0, f"a fresh database is at version 0, got {schema_version(_conn)}"
_applied = migrate(_conn)
assert _applied == ["0001_core", "0002_plays", "0003_indexes"], f"applied {_applied!r}"
assert schema_version(_conn) == 3, f"version is {schema_version(_conn)}, expected 3"
assert migrate(_conn) == [], "a second run applies nothing"
_tables = {row[0] for row in _conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
for _t in ("artist", "album", "play"):
    assert _t in _tables, f"table {_t!r} is missing; found {sorted(_tables)!r}"
_indexes = {row[0] for row in _conn.execute(
    "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")}
assert {"idx_album_artist", "idx_album_year", "idx_play_album"} <= _indexes, \
    f"migration 0003 should create three indexes; found {sorted(_indexes)!r}"
'''},
            {"name": "The engine enforces the constraints", "code": r'''
import sqlite3 as _sqlite3
from store import connect, migrate
_conn = connect()
migrate(_conn)
_conn.execute("INSERT INTO artist (id, name, country) VALUES (1, 'A', 'Italy')")
for _sql, _args, _why in [
    ("INSERT INTO album (artist_id, title, year, tracks) VALUES (?, ?, ?, ?)",
     (99, "T", 1990, 5), "an album pointing at a missing artist"),
    ("INSERT INTO album (artist_id, title, year, tracks) VALUES (?, ?, ?, ?)",
     (1, "T", 1899, 5), "a year below 1900"),
    ("INSERT INTO album (artist_id, title, year, tracks) VALUES (?, ?, ?, ?)",
     (1, "T", 1990, 0), "an album with no tracks"),
    ("INSERT INTO artist (name, country) VALUES (?, ?)",
     ("A", "Italy"), "a duplicate artist name"),
]:
    try:
        _conn.execute(_sql, _args)
        assert False, f"{_why} should raise IntegrityError"
    except _sqlite3.IntegrityError:
        pass
'''},
            {"name": "seed loads the demo dataset", "code": r'''
from store import Repository, connect, migrate, seed


def _fresh():
    _c = connect()
    migrate(_c)
    _r = Repository(_c)
    seed(_r)
    return _c, _r


_c2 = connect()
migrate(_c2)
_counts = seed(Repository(_c2))
assert _counts == {"artists": 4, "albums": 6, "plays": 10}, f"seed reported {_counts!r}"
_conn, _repo = _fresh()
for _table, _want in [("artist", 4), ("album", 6), ("play", 10)]:
    _got = _conn.execute(f"SELECT COUNT(*) FROM {_table}").fetchone()[0]
    assert _got == _want, f"{_table} holds {_got} rows, expected {_want}"
'''},
            {"name": "add_artist validates and refuses duplicates", "code": r'''
from store import NotFound, Repository, StoreError, ValidationError, connect, migrate
_c = connect()
migrate(_c)
_r = Repository(_c)
_id = _r.add_artist("  Neu!  ", "Germany")
assert isinstance(_id, int) and _id > 0, f"add_artist returned {_id!r}"
assert _c.execute("SELECT name FROM artist WHERE id = ?", (_id,)).fetchone()[0] == "Neu!", \
    "the stored name should be stripped"
for _args in [("", "Germany"), ("   ", "Germany"), ("Cluster", ""), ("Neu!", "Germany")]:
    try:
        _r.add_artist(*_args)
        assert False, f"add_artist{_args!r} should raise ValidationError"
    except ValidationError:
        pass
assert issubclass(ValidationError, StoreError) and issubclass(NotFound, StoreError), \
    "both errors should share a base class a caller can catch"
'''},
            {"name": "add_album validates its arguments", "code": r'''
from store import NotFound, ValidationError
_conn, _repo = _fresh()
_artist = _conn.execute("SELECT id FROM artist WHERE name = ?", ("Fela Kuti",)).fetchone()[0]
for _args in [(_artist, "", 1976, 4), (_artist, "X", 1899, 4), (_artist, "X", 2101, 4),
              (_artist, "X", 1976, 0), (_artist, "X", 1976, -2), (_artist, "Zombie", 1976, 4)]:
    try:
        _repo.add_album(*_args)
        assert False, f"add_album{_args!r} should raise ValidationError"
    except ValidationError:
        pass
try:
    _repo.add_album(9999, "X", 1976, 4)
    assert False, "an unknown artist should raise NotFound"
except NotFound:
    pass
try:
    _repo.add_play(9999, "2026-05-01")
    assert False, "a play on an unknown album should raise NotFound"
except NotFound:
    pass
'''},
            {"name": "get_album joins in the artist", "code": r'''
from store import NotFound
_conn, _repo = _fresh()
_id = _conn.execute("SELECT id FROM album WHERE title = ?", ("Autobahn",)).fetchone()[0]
_album = _repo.get_album(_id)
assert isinstance(_album, dict), f"get_album returned a {type(_album).__name__}, expected a dict"
assert _album["title"] == "Autobahn" and _album["year"] == 1974, f"got {_album!r}"
assert _album["tracks"] == 5 and _album["artist"] == "Kraftwerk", f"got {_album!r}"
try:
    _repo.get_album(9999)
    assert False, "an unknown album id should raise NotFound"
except NotFound:
    pass
'''},
            {"name": "albums_by_artist orders by year", "code": r'''
_conn, _repo = _fresh()
_titles = [album["title"] for album in _repo.albums_by_artist("Kraftwerk")]
assert _titles == ["Autobahn", "Trans-Europe Express", "Computer World"], f"got {_titles!r}"
assert all(isinstance(album, dict) for album in _repo.albums_by_artist("Kraftwerk")), \
    "rows should be converted to plain dicts at the repository boundary"
assert _repo.albums_by_artist("Nobody At All") == [], "an unknown artist gives an empty list"
assert _repo.albums_by_artist("Tom Ze") == [], "an artist with no albums gives an empty list"
'''},
            {"name": "albums_per_decade groups by decade", "code": r'''
_conn, _repo = _fresh()
_got = [tuple(row) for row in _repo.albums_per_decade()]
assert _got == [(1970, 5), (1980, 1)], f"got {_got!r}"
'''},
            {"name": "top_artists keeps the silent ones", "code": r'''
_conn, _repo = _fresh()
_got = [(row["name"], row["plays"]) for row in _repo.top_artists(4)]
assert _got == [("Alice Coltrane", 4), ("Kraftwerk", 4), ("Fela Kuti", 2), ("Tom Ze", 0)], \
    f"got {_got!r}"
assert len(_repo.top_artists(2)) == 2, "limit is a bound parameter"
assert [row["name"] for row in _repo.top_artists(2)] == ["Alice Coltrane", "Kraftwerk"], \
    "equal play counts break alphabetically"
'''},
            {"name": "delete_artist cascades", "code": r'''
from store import NotFound
_conn, _repo = _fresh()
_id = _conn.execute("SELECT id FROM artist WHERE name = ?", ("Kraftwerk",)).fetchone()[0]
_removed = _repo.delete_artist(_id)
assert _removed == 3, f"Kraftwerk has 3 albums, delete_artist returned {_removed!r}"
assert _conn.execute("SELECT COUNT(*) FROM artist").fetchone()[0] == 3, "the artist is gone"
assert _conn.execute("SELECT COUNT(*) FROM album").fetchone()[0] == 3, "their albums went too"
assert _conn.execute("SELECT COUNT(*) FROM play").fetchone()[0] == 6, \
    "the four plays of their albums went with them, leaving 6"
try:
    _repo.delete_artist(9999)
    assert False, "deleting an unknown artist should raise NotFound"
except NotFound:
    pass
'''},
            {"name": "The cost report tells index from scan", "code": r'''
from store import cost_report, query_plan, uses_index
_conn, _repo = _fresh()
_plan = query_plan(_conn, "SELECT title FROM album WHERE year = ?", (1974,))
assert _plan and all(isinstance(line, str) for line in _plan), f"query_plan gave {_plan!r}"
assert uses_index(_conn, "SELECT title FROM album WHERE year = ?", (1974,)), \
    f"an equality test on the indexed year column should use an index; plan was {_plan!r}"
_scan = query_plan(_conn, "SELECT title FROM album WHERE tracks = ?", (5,))
assert not uses_index(_conn, "SELECT title FROM album WHERE tracks = ?", (5,)), \
    f"tracks has no index, so this must scan; plan was {_scan!r}"
_report = cost_report(_conn)
assert len(_report) == 3, f"expected one entry per named query, got {len(_report)}"
assert {entry["name"] for entry in _report} == {
    "albums of one artist", "albums of one year", "albums by track count"}, f"got {_report!r}"
_rows = {entry["name"]: entry["rows"] for entry in _report}
assert _rows["albums of one year"] == 1, f"1974 has one album, got {_rows['albums of one year']}"
assert _rows["albums by track count"] == 3, f"three albums have 5 tracks, got {_rows!r}"
'''},
            {"name": "store.py is a library, main.py is the demo", "code": r'''
_src = open("store.py").read()
assert "print(" not in _src, "store.py defines the layer; the printing belongs in main.py"
assert 'f"SELECT' not in _src and "f'SELECT" not in _src, \
    "no SELECT should be built by string formatting — bind values with ?"
assert "albums per decade" in _out, "main.py should print the seeded summary"
assert "index=" in _out, "main.py should print the cost report"
'''},
        ],
    },
}
