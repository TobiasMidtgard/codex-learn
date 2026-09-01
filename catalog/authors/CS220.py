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
            "read": [
                {
                    "title": "Tables that keep promises",
                    "minutes": 12,
                    "body": r'''
Picture a library that runs on one spreadsheet. Every time someone borrows a book, a row
goes in: the member's name, the book's title, the author, the author's country, the day.
After a month it looks like this:

```text
member   title                   author              country        day
Ada      A Wizard of Earthsea    Ursula K. Le Guin   United States  2026-03-01
Grace    A Wizard of Earthsea    Ursula K. Le Guin   United States  2026-03-02
Ada      The Dispossessed        Ursula K. Le Guin   United States  2026-03-03
Linus    Invisible Cities        Italo Calvino       Italy          2026-03-04
```

It works until it does not. Le Guin's country is typed out on three rows, and one of them
will eventually be typed differently. Barbara joined last week and has borrowed nothing,
so there is no row for her and nowhere to write her name down. *Cosmicomics* has never
left the shelf, so the sheet has no idea it exists. And if someone deletes Linus's row
because the book came back, the library forgets that Calvino is Italian.

The relational model is a response to that sheet. It says: separate the things being
talked about — authors, books, members, loans — and give each its own table, so that
every fact is written down once. Then, and this is the part the sheet could never do,
tell the engine what must be true of those tables, so that a row that would break a rule
is refused rather than stored.

## A relation is a set

A table in this model is a *relation*: a set of tuples, every one shaped by the same
schema. Two words in that sentence carry weight. *Set* means there is no order. The rows
are not first, second and third; they are members of a collection, and a query that reads
them out without `ORDER BY` is allowed to hand them back in any order the engine finds
convenient, and in a different order tomorrow. It also means a row carries no position
you could select on: there is no "row 3", only rows with values. *Schema* means the
columns and their names are fixed and the same for every row, which is what makes it
possible to write a query about the column rather than about one row.

SQL departs from the model in one place: a SQL table is a *bag*, not a set, and will
store two identical rows unless you tell it otherwise. That is part of what `UNIQUE` and
`PRIMARY KEY` are for.

## Keys: how to point at a row

Take the book table. Two books can have the same title, so the title is not a way of
naming a book. Give every book a number instead:

```sql
CREATE TABLE book (
    id        INTEGER PRIMARY KEY,
    title     TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES author(id),
    year      INTEGER NOT NULL,
    copies    INTEGER NOT NULL CHECK (copies > 0)
);
```

`id` is the *primary key*: a column, or a set of columns, whose value identifies one row
and one only, and which the engine promises never to let repeat. In SQLite an
`INTEGER PRIMARY KEY` is the table's own row number, which makes it the cheapest possible
thing to look a row up by; that will matter in module three.

Now `author_id`. A book is by an author, and the way the book table says so is by holding
the author's key. That column is a *foreign key*: its value must be the primary key of
some row in `author`. `REFERENCES author(id)` is the promise, and it means two things at
once — a book cannot name an author who does not exist, and an author cannot be deleted
while a book still names them. With that promise kept, the spreadsheet's last problem goes
away: there is nothing to forget, because the author's country lives in one row of
`author` and the book points at it.

One trap is specific to SQLite. It parses `REFERENCES` and then, by default, ignores it. Foreign keys are enforced only on a
connection that has run `PRAGMA foreign_keys = ON`, and every new connection starts with
it off. A schema full of `REFERENCES` clauses that has never been switched on will accept
a book by author 99 without a murmur. The lab's `connect()` exists to make that pragma
impossible to forget.

## Constraints: validation that cannot be bypassed

The other clauses in that `CREATE TABLE` are the same idea applied to single columns.
`NOT NULL` says a book must have a title. `UNIQUE`, on `author.name`, says two authors
cannot share one. `CHECK (copies > 0)` says a book with no copies is not a book the
library holds.

You could check all of that in Python before the `INSERT`. The reason to put it in the
schema is that Python is not the only thing that will ever write to the database — there
will be a second script, a migration, a colleague at the `sqlite3` prompt — and a rule in
the schema holds for all of them. Here is the engine keeping three of them:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON")
conn.executescript("""
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
""")
conn.execute("INSERT INTO author VALUES (?, ?, ?)", (3, "Chinua Achebe", "Nigeria"))

attempts = [
    ("a book by author 99, who does not exist", (6, "Things Fall Apart", 99, 1958, 4)),
    ("a book with no title",                    (6, None, 3, 1958, 4)),
    ("a book with zero copies",                 (6, "Things Fall Apart", 3, 1958, 0)),
]
for what, row in attempts:
    try:
        conn.execute("INSERT INTO book VALUES (?, ?, ?, ?, ?)", row)
        print("accepted:", what)
    except sqlite3.IntegrityError as error:
        print("refused: ", what, "->", error)
print("books stored:", conn.execute("SELECT COUNT(*) FROM book").fetchone()[0])
```

Each attempt is refused with an `IntegrityError` that names the constraint, and the table
holds nothing afterwards. That is the property to want from validation: nothing
half-written, nothing to clean up.

## Joins: one row per matching pair

A query that needs facts from two tables has to put them back together, and the
operation that does it is the join. Start with what a join *produces*, on the smallest
real case: four members and eight loans, and one member — Barbara — who has never
borrowed anything.

`FROM member JOIN loan ON loan.member_id = member.id` considers every pair of a member
row and a loan row and keeps the pairs where the condition holds. Each loan names exactly
one member, so each loan survives in exactly one pair: eight rows out, one per loan.
Barbara is in no pair, so she is not in the result. That is an *inner* join, and losing
Barbara is not a bug in it; it is what "the pairs where the condition holds" means.

`LEFT JOIN` adds one rule: every row of the left table appears at least once. A left row
that matched nothing is emitted once anyway, with every column of the right table set to
NULL. Eight matched pairs plus one manufactured row for Barbara is nine. Run it:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.executescript("""
CREATE TABLE member (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE loan (id INTEGER PRIMARY KEY, member_id INTEGER NOT NULL, day TEXT NOT NULL);
""")
conn.executemany("INSERT INTO member VALUES (?, ?)",
                 [(1, "Ada"), (2, "Grace"), (3, "Linus"), (4, "Barbara")])
conn.executemany("INSERT INTO loan VALUES (?, ?, ?)", [
    (1, 1, "03-01"), (2, 2, "03-02"), (3, 1, "03-03"), (4, 3, "03-04"),
    (5, 1, "03-05"), (6, 2, "03-06"), (7, 2, "03-07"), (8, 1, "03-08"),
])

inner = conn.execute("""
    SELECT member.name, loan.id FROM member
    JOIN loan ON loan.member_id = member.id
    ORDER BY loan.id""").fetchall()
left = conn.execute("""
    SELECT member.name, loan.id FROM member
    LEFT JOIN loan ON loan.member_id = member.id
    ORDER BY member.id, loan.id""").fetchall()
print("inner join:", len(inner), "rows")
print("left join: ", len(left), "rows, the last of them", left[-1])

count_rows = conn.execute("""
    SELECT member.name, COUNT(*) FROM member
    LEFT JOIN loan ON loan.member_id = member.id
    GROUP BY member.id ORDER BY member.id""").fetchall()
count_loans = conn.execute("""
    SELECT member.name, COUNT(loan.id) FROM member
    LEFT JOIN loan ON loan.member_id = member.id
    GROUP BY member.id ORDER BY member.id""").fetchall()
print("COUNT(*):      ", count_rows)
print("COUNT(loan.id):", count_loans)
```

The second half of that output is the mistake this module is most concerned with.
`COUNT(*)` counts rows, and Barbara's padded row is a row, so she scores 1.
`COUNT(loan.id)` counts the non-NULL values in that column, and her padded row has a NULL
there, so she scores 0. Both queries run, both produce a tidy table, and one of them is
wrong by exactly one on exactly the rows nobody checks. It is tempting because `COUNT(*)`
is what everyone types first, and on an inner join it is correct. Only the outer join
manufactures a row with nothing in it — and the outer join is the one you reached for
precisely so that Barbara would appear.

## WHERE filters rows; HAVING filters groups

`GROUP BY` collapses rows that share a value into one row per value, and an aggregate —
`COUNT`, `SUM`, `MAX` — describes each group. The question of where a condition goes is
answered by *when it can be evaluated*. The engine works through the clauses in this
order: `FROM` and the joins first, then `WHERE` against each row, then `GROUP BY`, then
`HAVING` against each group, then `SELECT` to shape the output, and `ORDER BY` last of
all.

So a test on a column of a row — `year > 1960` — belongs in `WHERE`, because a single row
has a year. A test on an aggregate — `COUNT(*) > 2` — cannot be asked until the groups
exist, so it goes in `HAVING`. Putting `COUNT(*) > 2` in `WHERE` is an error in every
engine; the count does not exist yet. And because `WHERE` runs first, filtering there
means the groups are built from fewer rows, which is free.

`ORDER BY` runs last, which is why it can sort by an alias the `SELECT` made up —
`ORDER BY books DESC` in the lab's `books_per_country` — and why the count is worth
naming.

## NULL, and the subquery that returns nothing

Which books have never been borrowed? The natural first attempt is
`WHERE id NOT IN (SELECT book_id FROM loan)`, and on the lab's data it works. Then one
loan row acquires a NULL `book_id`, and the query returns nothing at all, with no error.

The reason is three-valued logic. A comparison with NULL is neither true nor false but
UNKNOWN, and `x NOT IN (2, NULL)` expands to `x <> 2 AND x <> NULL`. The second half is
UNKNOWN for every `x`, TRUE AND UNKNOWN is UNKNOWN, so no row's condition is ever TRUE —
and `WHERE` keeps only TRUE.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.executescript("""
CREATE TABLE book (id INTEGER PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE loan (id INTEGER PRIMARY KEY, book_id INTEGER);
INSERT INTO book VALUES (1, 'Cosmicomics'), (2, 'Invisible Cities'), (3, 'Zombie');
INSERT INTO loan VALUES (1, 2), (2, NULL);
""")
not_in = conn.execute("""
    SELECT title FROM book
     WHERE id NOT IN (SELECT book_id FROM loan)""").fetchall()
not_exists = conn.execute("""
    SELECT title FROM book
     WHERE NOT EXISTS (SELECT 1 FROM loan WHERE loan.book_id = book.id)""").fetchall()
print("NOT IN:    ", not_in)
print("NOT EXISTS:", not_exists)
print("1 <> NULL evaluates to", conn.execute("SELECT 1 <> NULL").fetchone()[0])
```

`NOT EXISTS` asks a different question — is there a loan row matching *this* book? — and
a loan row with a NULL `book_id` matches no book, so it is ignored, which is what you
meant. The last line shows the value at the root of it: `1 <> NULL` is not false, it is
nothing, and Python receives it as `None`. The lab's `never_borrowed` uses `NOT EXISTS`
for this reason, and it is worth making a habit.

## Bound parameters are not a style choice

Every query in the lab takes a value from outside — an author's name, a limit — and the
way it goes in matters more than anything else in this module. Compare:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.executescript("""
CREATE TABLE book (id INTEGER PRIMARY KEY, title TEXT NOT NULL);
INSERT INTO book VALUES (1, 'Cosmicomics'), (2, 'Invisible Cities');
""")
title = "' OR '1'='1"

pasted = "SELECT title FROM book WHERE title = '" + title + "'"
print(pasted)
print("pasted in:", conn.execute(pasted).fetchall())

bound = "SELECT title FROM book WHERE title = ?"
print("bound:    ", conn.execute(bound, (title,)).fetchall())
```

The first query was built by pasting the value into the SQL text, and the value contained
a quote. The quote ended the string the query was comparing against, and what followed it
was read as SQL: `WHERE title = '' OR '1'='1'` is true for every row, so the whole table
came back. Replace the tail with something more purposeful and you have SQL injection.

The bound version hands the engine a statement with a hole in it and the value
separately. The value is never parsed as SQL; it is compared as a string, no title
matches it, and the result is empty. Python's `sqlite3` refuses a second statement in
`execute()`, which happens to blunt the classic `'; DROP TABLE book; --`, but
`executescript()` does not refuse it and other drivers do not either. The rule does not
depend on any of that: a value goes in through `?`, always, and the lab's last test —
"Quotes in an argument are data, not SQL" — checks that you did.

## Where the model stops

Two things about SQLite are worth knowing before they surprise you. It does not enforce
column types: a string in an `INTEGER` column is stored as text, and a `CHECK` constrains
values rather than types. Inserting `'three'` into `copies` passes `CHECK (copies > 0)`,
because SQLite orders every text value above every number, and the row is stored with a
word where a count should be. If a column must hold an integer, the check has to say so:
`CHECK (typeof(copies) = 'integer' AND copies > 0)`. And the set-versus-bag point returns
in a form that bites: `ORDER BY books DESC` alone leaves two countries with the same
count in whatever order the engine likes, and a test that expects Italy before the United
States will pass on your machine and fail on another. Every `ORDER BY` in the lab ends
with a column that breaks ties, and so should yours.

This module's lab, **A library schema, and questions asked of it**, is the spreadsheet
above done properly: four tables, the constraints the engine enforces, and four
questions — a join, a grouping, a `NOT EXISTS`, and a ranked count with a bound limit —
each of which has a plausible wrong answer that runs.
''',
                },
            ],
            "quiz": {
                "title": "Relations, keys, and what a join keeps",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A relation is a *set* of tuples. Which consequence follows for SQL?",
                        "opts": [
                            "A query with no `ORDER BY` may return its rows in any order, and a different order on a later run is not a bug",
                            "The engine returns rows in insertion order unless you ask for something else",
                            "Adding an index can change which rows a query returns",
                            "Every row carries a position, counted from 1, that you can select on",
                        ],
                        "a": 0,
                        "why": (
                            "Order is not information. SQLite will often hand back rows in rowid order "
                            "today and in a completely different order tomorrow, once an index makes "
                            "another access path cheaper — the same rows, differently arranged, and "
                            "the engine considers itself to have answered correctly both times. That "
                            "is exactly why `ORDER BY` exists, and why a test that asserts an "
                            "unordered result is a test that will fail on someone else's machine. "
                            "Note that an index changes the *order* and the *cost*, never the set of "
                            "rows; and there is no row number to select on, because a set has no "
                            "positions to number."
                        ),
                    },
                    {
                        "q": "`SELECT title FROM book WHERE id NOT IN (SELECT book_id FROM loan)` — and one row of `loan` has a NULL `book_id`. What comes back?",
                        "opts": [
                            "Nothing at all, whatever is in `book`",
                            "Every book that has never been loaned, as intended",
                            "Every book, because a NULL matches nothing",
                            "An error: NULL is not comparable with `IN`",
                        ],
                        "a": 0,
                        "why": (
                            "`id NOT IN (1, 4, NULL)` expands to `id <> 1 AND id <> 4 AND id <> NULL`, "
                            "and that last comparison is UNKNOWN for every possible `id`. A conjunction "
                            "with an UNKNOWN in it can be FALSE, but it can never be TRUE — and "
                            "`WHERE` keeps only TRUE. So the result is empty, silently, with no error "
                            "and nothing in the log. `NOT EXISTS` asks a different question: does a "
                            "matching row exist? A row whose `book_id` is NULL simply fails to match "
                            "and is ignored, which is what you meant in the first place. This is the "
                            "single best reason to reach for `NOT EXISTS` by habit."
                        ),
                    },
                    {
                        "q": "You want the countries with more than two books, counting only books published after 1960. Where does each condition go?",
                        "opts": [
                            "`year > 1960` in `WHERE`, `COUNT(*) > 2` in `HAVING`",
                            "Both in `WHERE`",
                            "Both in `HAVING`",
                            "`year > 1960` in `HAVING`, `COUNT(*) > 2` in `WHERE`",
                        ],
                        "a": 0,
                        "why": (
                            "`WHERE` runs before the grouping and sees one row at a time; `HAVING` runs "
                            "after it and sees one group at a time. The year is a property of a book, so "
                            "it belongs in `WHERE` — and filtering there also means the groups are "
                            "built from fewer rows, which is free speed. The count is a property of a "
                            "group and does not exist until the grouping has happened, so an aggregate "
                            "in `WHERE` is rejected outright by every engine. Putting a plain column "
                            "test in `HAVING` is the mirror-image mistake: with no aggregate wrapped "
                            "around it there is no single value for the group, and standard SQL refuses "
                            "it too."
                        ),
                    },
                    {
                        "q": "`SELECT a.name, COUNT(*) FROM author a LEFT JOIN book b ON b.author_id = a.id GROUP BY a.id` — what does it report for an author with no books?",
                        "opts": ["1", "0", "NULL", "Nothing: that author is left out"],
                        "a": 0,
                        "why": (
                            "The left join manufactures one row for that author with every `book` column "
                            "set to NULL, and `COUNT(*)` counts *rows*, not values — so an author "
                            "with nothing scores 1. `COUNT(b.id)` counts the non-NULL values of that "
                            "column and reports the 0 you wanted. `COUNT(1)` is identical to `COUNT(*)`, "
                            "because the constant is never NULL either. This is quietly the most common "
                            "wrong number in a business report: it is off by exactly one, only on the "
                            "rows nobody checks, and it never raises anything."
                        ),
                    },
                    {
                        "q": "Why is `conn.execute(\"SELECT * FROM book WHERE title = ?\", (title,))` not merely a tidier spelling of an f-string?",
                        "opts": [
                            "The value never becomes part of the SQL text, so no quote inside it can end the string and start a statement",
                            "The driver escapes the quotes in the value before pasting it into the SQL",
                            "It is faster, because the driver caches the assembled string",
                            "It converts the value to the column's declared type, which an f-string cannot do",
                        ],
                        "a": 0,
                        "why": (
                            "The statement is parsed once with a hole in it, and the value is handed to "
                            "the engine down a separate channel. Nothing in it is ever read as SQL, so "
                            "`x'; DROP TABLE book; --` is a title that no book has, and that is the "
                            "whole of it. Escaping the quotes first is what a hand-rolled quoting helper "
                            "does, and such a helper is only ever a list of the tricks its author "
                            "happened to remember. Reusing a prepared statement is a real secondary "
                            "benefit, but speed is not the argument — and no driver quietly coerces "
                            "your value to the column's type; SQLite in particular stores whatever you "
                            "give it."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "One report, five decisions",
                "minutes": 9,
                "caption": "loans_by_author.sql — five holes, each one a different way to be wrong",
                "lang": "sql",
                "brief": r'''
This query is the shape of half the reports ever written: walk down from a parent
table, count something on a grandchild, keep the parents that have nothing.

Every hole below has a plausible-looking wrong filling that produces *numbers*
rather than an error. That is what makes reporting SQL dangerous — the query runs,
the report ships, and the figures come out plausible and wrong on precisely the rows
nobody looks at.
''',
                "listing": r'''-- Every author from one country, and how many loans their books have
-- attracted. An author whose books have never left the shelf -- or who
-- has no books on it at all -- must still appear, with a zero.

SELECT author.name,
       COUNT(___) AS loans
  FROM author
  ___ book ON book.author_id = author.id
  LEFT JOIN loan ON loan.___ = book.id
 WHERE author.country = ___
 GROUP BY author.id, author.name
 ORDER BY loans ___, author.name;
''',
                "blanks": [
                    {
                        "prompt": "An author with no loans must come out as 0, not as 1. What is counted?",
                        "hole": "?",
                        "opts": ["1", "loan.id", "*", "book.id"],
                        "a": 1,
                        "why": "`COUNT` over a column counts its non-NULL values. The outer join pads an author with no loans with a NULL `loan.id`, that NULL is not counted, and the author scores the 0 the brief asked for.",
                        "whys": [
                            "A constant is never NULL, so `COUNT(1)` is exactly `COUNT(*)` in every engine — including this one — and it inflates exactly the same authors by exactly the same amount.",
                            "`COUNT` over a column counts its non-NULL values. The outer join pads an author with no loans with a NULL `loan.id`, that NULL is not counted, and the author scores the 0 the brief asked for.",
                            "`COUNT(*)` counts rows, and the NULL-padded row an outer join invents is still a row. Because this is a two-level chain, an author with nothing borrowed keeps one padded row *per book*: three books and no loans reports 3, not 1. Only an author with a single book — or no books at all — happens to report 1. No error, no warning, just a report inflated by the size of each silent author's shelf.",
                            "This counts the surviving *book* rows, which the second join has already multiplied by the number of loans on each. An author with one much-borrowed book and one untouched one gets a number that is neither their book count nor their loan count.",
                        ],
                    },
                    {
                        "prompt": "How do we reach `book` without dropping an author who has none?",
                        "hole": "?",
                        "opts": ["JOIN", "RIGHT JOIN", "CROSS JOIN", "LEFT JOIN"],
                        "a": 3,
                        "why": "A left join keeps every row of `author` whether or not the `ON` clause finds it a partner, filling the missing side with NULLs. That is the only construct here that can produce a row for an author with an empty shelf.",
                        "whys": [
                            "A plain `JOIN` is an inner join: an author the `ON` clause cannot match simply vanishes from the result. The rows it deletes are precisely the rows the report was written to show.",
                            "A right join preserves `book` instead. Since `book.author_id` is `NOT NULL` and the foreign key is enforced, every book already has an author, so this collapses to the inner join and loses the same authors.",
                            "A cross join asks for every author paired with every book. The `ON` clause is not part of what a cross join means; engines that tolerate one anyway just treat the whole thing as an inner join, so it either multiplies the table or loses the empty authors.",
                            "A left join keeps every row of `author` whether or not the `ON` clause finds it a partner, filling the missing side with NULLs. That is the only construct here that can produce a row for an author with an empty shelf.",
                        ],
                    },
                    {
                        "prompt": "Which column of `loan` points at a book?",
                        "hole": "?",
                        "opts": ["book_id", "id", "member_id", "day"],
                        "a": 0,
                        "why": "`loan.book_id` is the declared foreign key into `book(id)`. It is the only column in `loan` whose values are book identifiers, and the join is only meaningful along a declared reference.",
                        "whys": [
                            "`loan.book_id` is the declared foreign key into `book(id)`. It is the only column in `loan` whose values are book identifiers, and the join is only meaningful along a declared reference.",
                            "`loan.id` is the loan's own surrogate key. Joining it to `book.id` pairs loan 1 with book 1 for no reason at all, and because both are dense integers it produces a full-looking result with entirely fictional numbers in it — the worst failure mode there is.",
                            "`member_id` identifies a borrower, not a book. The numbers still line up against `book.id`, so once again you get rows rather than an error, and the report attributes loans to whichever books happen to share an id with a member.",
                            "`day` is a date string. SQLite compares it against an integer id under the usual affinity rules, finds them never equal, and the outer join pads every author with NULLs — so the whole report comes out as zeros.",
                        ],
                    },
                    {
                        "prompt": "The country comes from outside the query. How does it get in?",
                        "hole": "?",
                        "opts": ["'Italy'", "{country}", "?", "%s"],
                        "a": 2,
                        "why": "`?` is the placeholder Python's `sqlite3` binds. The value travels beside the statement rather than inside it, so it is data to the engine no matter what characters it contains.",
                        "whys": [
                            "Hard-coding the country makes the statement answer exactly one question forever. Every new country means a new string, and the first person in a hurry builds that string by concatenation — which is how the hole gets opened.",
                            "That is a Python format hole, and filling it means the value becomes part of the SQL text. A country named `x' OR '1'='1` then returns the whole table, which is the injection this course keeps coming back to.",
                            "`?` is the placeholder Python's `sqlite3` binds. The value travels beside the statement rather than inside it, so it is data to the engine no matter what characters it contains.",
                            "`%s` is the placeholder that `psycopg2` and the MySQL drivers use. `sqlite3` has never heard of it, and bare `%` is SQLite's modulo operator, so the statement does not even parse: `sqlite3.OperationalError: near \"%\": syntax error`. That is the honest kind of failure. Quoting it as `'%s'` is the dangerous variant — that one parses, compares against the literal two-character string, and returns an empty report for every country.",
                        ],
                    },
                    {
                        "prompt": "Busiest author first.",
                        "hole": "?",
                        "opts": ["ASC", "DESCENDING", "-1", "DESC"],
                        "a": 3,
                        "why": "`DESC` sorts the count downwards, and `author.name` after it settles the ties, so the same data always produces the same report.",
                        "whys": [
                            "`ASC` is the default and sorts upwards, which puts every author nobody has borrowed at the top of a report about who is borrowed most.",
                            "SQL has no such keyword. SQLite stops with `near \"DESCENDING\": syntax error`, which is at least the honest kind of failure — you find out immediately.",
                            "This is not a sort direction at all: the parser reads `loans -1` as the expression `loans - 1` and sorts ascending on it. Every count shifted down by one sorts in exactly the same order as the counts themselves, so you get a silently ascending report.",
                            "`DESC` sorts the count downwards, and `author.name` after it settles the ties, so the same data always produces the same report.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How many rows does the left join produce?",
                "minutes": 6,
                "brief": r'''
The library data from the lab: four members, eight loans. Every loan names exactly
one member, and one member has never borrowed anything.

```sql
SELECT member.name, loan.id
  FROM member
  LEFT JOIN loan ON loan.member_id = member.id;
```

Count the rows this returns. Not the members, not the loans — the rows.
''',
                "prompt": "How many rows does that query return?",
                "note": "Whole rows, including any the join has padded with NULLs.",
                "figure": "`member` holds Ada, Grace, Linus and Barbara. The eight rows of `loan` carry `member_id` = 1, 2, 1, 3, 1, 2, 2, 1 — in that order, one row per borrowing.",
                "given": [
                    {"label": "Rows in `member`", "value": "4"},
                    {"label": "Rows in `loan`", "value": "8"},
                    {"label": "Join predicate", "value": "`loan.member_id = member.id`"},
                    {"label": "Members are ids 1-4", "value": "Ada 1, Grace 2, Linus 3, Barbara 4"},
                ],
                "aside": "A join is not a lookup. It emits one row per matching pair, and an outer "
                         "join then adds one more row for each left row that matched nothing.",
                "answer": 9,
                "tol": 0,
                "unit": "rows",
                "hint": "Count the matching pairs first — each loan matches exactly one member "
                        "— then ask what a LEFT JOIN does for a member that matched none.",
                "wrong": "Eight is the inner join: the eight loan rows, each paired with its one "
                         "member. The word LEFT is there to add something to that.",
                "why": (
                    "Each of the eight loans matches exactly one member, so the join emits those "
                    "eight pairs: four for Ada, three for Grace, one for Linus. Barbara matches "
                    "nothing, and keeping her is the entire reason the join is a LEFT one — "
                    "she comes back once, with every `loan` column NULL. Eight plus one is nine.\n\n"
                    "That ninth row is worth remembering, because it is the row that makes "
                    "`COUNT(*)` on this join report 1 for Barbara instead of 0. The NULL-padded "
                    "row is still a row; only `COUNT(loan.id)` looks at the values and gives her "
                    "the zero she has earned."
                ),
            },
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
            "read": [
                {
                    "title": "The dependency decides the table",
                    "minutes": 12,
                    "body": r'''
Return to the spreadsheet from the first module, keeping only the columns that concern
the borrowing itself:

```text
member   phone      title                 author            country
Ada      555-0101   Invisible Cities      Italo Calvino     Italy
Grace    555-0102   Cosmicomics           Italo Calvino     Italy
Ada      555-0101   Things Fall Apart     Chinua Achebe     Nigeria
Linus    555-0103   Things Fall Apart     Chinua Achebe     Nigeria
```

Three things go wrong with it, and it pays to name each. Ada changes her phone number,
and two rows have to change; miss one and the table disagrees with itself. That is an
*update anomaly*. Barbara joins and has a phone number, but she has borrowed nothing, so
there is no row to keep it in. That is an *insertion anomaly*. Grace returns
*Cosmicomics* and her row is deleted — and with it the only record that Calvino wrote it.
That is a *deletion anomaly*.

All three have one cause. The table is about loans, but some of its columns are facts
about something else. A member's phone is a fact about the member; an author's country is
a fact about the author. Those facts are repeated once per loan because the table has
nowhere else to put them. Normalisation is the discipline of finding those facts and
giving each its own table, and its whole apparatus follows from writing the facts down
precisely.

## A functional dependency is a promise about every instance

"A member has one phone number" can be stated as a rule about the table: any two rows
that agree on `member` agree on `phone`. Written $\text{member} \to \text{phone}$ and
read "member determines phone", it is a *functional dependency*. The sheet has three:

```text
member -> phone
title  -> author
author -> country
```

with the understanding that a loan is identified by who borrowed what and when, so the
key is $\{\text{member}, \text{title}, \text{day}\}$.

Two things about a dependency are easy to get backwards. First, it is a constraint on
the *schema* — a promise about every instance the table will ever hold — not an
observation about the rows in it now. You cannot read one off the data: a table with one
row satisfies every dependency you could write, and a table that happens to obey
$\text{title} \to \text{author}$ today says nothing about tomorrow. Dependencies come from
knowing the domain (one title, one author) and are declared, not discovered. Second, a
dependency says that the right side is *determined*, never how. There is no formula from
a member to a phone number; there is only the promise that the number is a function of
the member.

## Closure: what a set of dependencies implies

If $\text{title} \to \text{author}$ and $\text{author} \to \text{country}$, then two rows
agreeing on title agree on author, and therefore agree on country:
$\text{title} \to \text{country}$ holds too, though nobody wrote it down. A set of
dependencies implies others, and to reason about keys you need all of them. Enumerating
every implied dependency is hopeless. What is tractable is a narrower question: given a
set of attributes $X$, which attributes does $X$ determine? That set is the *closure*
$X^+$, and it is computed by a loop that needs no cleverness at all.

Start with $X$ itself, because a set trivially determines its own attributes. Then look
through the dependencies. If a dependency's *whole* left side is already in the set you
have reached, its right side is determined too, so add it. Keep sweeping until a full
pass adds nothing. Because the set only ever grows and there are finitely many
attributes, the loop terminates; because nothing is added without a dependency to justify
it, everything in the result is genuinely determined.

Here it is with the sheet's dependencies as single letters — $M$ember, $P$hone, $T$itle,
$A$uthor, $C$ountry, $D$ay — and each firing printed as it happens:

```python
def closure(attributes, fds):
    """X+ under fds, printing each dependency as it fires."""
    reached = set(attributes)
    grew = True
    while grew:
        grew = False
        for lhs, rhs in fds:
            if lhs <= reached and not rhs <= reached:
                left, right = " ".join(sorted(lhs)), " ".join(sorted(rhs))
                print(f"  {left} -> {right} fires, adding {' '.join(sorted(rhs - reached))}")
                reached |= rhs
                grew = True
    return frozenset(reached)


FDS = [
    ({"M"}, {"P"}),          # a member has one phone number
    ({"T"}, {"A"}),          # a title has one author
    ({"A"}, {"C"}),          # an author has one country
]
print("{T}+")
print("  =", sorted(closure({"T"}, FDS)))
print("{M, T, D}+")
print("  =", sorted(closure({"M", "T", "D"}, FDS)))
```

$\{T\}^+$ is $\{T, A, C\}$: a title fixes its author, and through the author its
country, and nothing else. $\{M, T, D\}^+$ is everything. That second fact is the
definition of a key.

## Superkeys and candidate keys

A set of attributes $X$ is a *superkey* of a relation $R$ when $X^+ \supseteq R$: fix the
values of $X$ and every other column is fixed. A *candidate key* is a superkey with no
proper subset that is also one — a superkey with nothing spare. The lab asks you to
enumerate them, and the enumeration has a shape worth knowing. Try subsets smallest
first, singles then pairs then triples; a set that contains a key already found is a
superkey and cannot be minimal, so skip it. And before trying anything, look at which
attributes appear on no right-hand side at all: nothing can ever produce them, so every
key must contain them. In the sheet those are $M$, $T$ and $D$, and $\{M, T, D\}^+$
covers everything, so $\{M, T, D\}$ is the one candidate key and no smaller set need be
tested.

## The test: is the left side a superkey?

Now look at the anomalies again with the dependencies in hand. Ada's phone was repeated
because $M \to P$ holds and $M$ recurs: Ada appears in two rows, and each carries her
phone. Calvino's country was repeated because $A \to C$ holds and $A$ recurs. The
dependencies that cause trouble are exactly the ones whose left side can appear in more
than one row — and a left side can appear in more than one row exactly when it is *not a
superkey*, because a superkey's values identify one row.

That is Boyce-Codd normal form, derived rather than announced: a relation is in BCNF when
for every non-trivial dependency $X \to Y$ that holds on it, $X$ is a superkey.
*Non-trivial* excludes dependencies like $M\,T \to M$, whose right side is already inside
the left; those hold in every relation and say nothing about its design. The test itself
is one closure per dependency: compute $X^+$ and ask whether it covers $R$.

On the sheet, $M \to P$ fails ($\{M\}^+ = \{M, P\}$), $T \to A$ fails, $A \to C$ fails.
Three violations, three facts that belong in tables of their own. On the lab's classic
relation the same test reads:

```python
def closure(attributes, fds):
    reached = set(attributes)
    grew = True
    while grew:
        grew = False
        for lhs, rhs in fds:
            if lhs <= reached and not rhs <= reached:
                reached |= rhs
                grew = True
    return frozenset(reached)


R = {"A", "B", "C"}
FDS = [({"A", "B"}, {"C"}), ({"C"}, {"B"})]
for lhs, rhs in FDS:
    plus = closure(lhs, FDS)
    verdict = "superkey, fine" if R <= plus else "not a superkey: violation"
    print(f"{' '.join(sorted(lhs))} -> {' '.join(sorted(rhs))}:  closure {sorted(plus)}  {verdict}")
```

## Decomposition, and why it must split on the dependency

Fix a violation $X \to Y$ by splitting the relation in two: one piece holding $X \cup Y$,
the fact itself in its own table, and one holding everything else plus $X$, so that the
second piece can still point at the first. Splitting the sheet on $T \to A$ gives
$\{T, A\}$ and $\{M, P, T, C, D\}$; then recurse on both pieces, because the second one
still has $M \to P$ in it and, less visibly, $T \to C$.

The rule is not arbitrary. The pieces are only useful if joining them back yields the
original rows and nothing more, and that is guaranteed when the attributes the pieces
share form a key of one of them. In the split above the shared attribute is $T$, and $T$
is a key of $\{T, A\}$: each title matches one row on that side, so joining back cannot
multiply anything. Split so that the shared column is *not* a key and the join invents
rows:

```python
rows = [
    ("Ada",   "Invisible Cities", "Calvino"),
    ("Grace", "Cosmicomics",      "Calvino"),
]
M, T, A = 0, 1, 2


def project(rows, columns):
    """The distinct rows over those columns, in that order."""
    return sorted({tuple(row[c] for c in columns) for row in rows})


def join_on(left, right, at):
    """Join two projections on the column at position at[0] in left and at[1] in right."""
    out = []
    for l in left:
        for r in right:
            if l[at[0]] == r[at[1]]:
                out.append(l + tuple(v for i, v in enumerate(r) if i != at[1]))
    return sorted(out)


good = join_on(project(rows, (M, T)), project(rows, (T, A)), (1, 0))
bad = join_on(project(rows, (M, A)), project(rows, (T, A)), (1, 1))
print("shared column T, a key of {T, A}:", len(good), "rows come back")
print("shared column A, a key of neither:", len(bad), "rows come back")
for row in bad:
    print("  ", row)
```

Sharing $A$ instead of $T$ pairs every member who borrowed a Calvino with every Calvino
title, and Ada is now recorded as having borrowed *Cosmicomics*, which she never did.
Every one of the four rows is plausible. That is what makes a lossy decomposition
dangerous: it does not fail, it lies.

## Projecting dependencies onto a piece

The recursion has a subtlety that the lab's `project_fds` exists for. After a split,
which dependencies hold on a piece? Not only those in the original list whose attributes
all lie inside it. $T \to C$ holds on $\{M, P, T, C, D\}$, but it is in nobody's list —
it is implied through $A$, and $A$ is not in the piece. The only reliable way to find the
dependencies of a piece is to compute, for every subset $X$ of it, what $X$ determines
*within* the piece: $X \to (X^+ \cap \text{piece}) - X$, dropping the ones whose right
side comes out empty. That is a closure per subset, against the original dependency set,
every time. Projecting a projection loses dependencies, which is why `decompose` recurses
with the original set and re-projects inside each call.

## Where BCNF costs something: 3NF

Take the classic relation from the block above, $R(A, B, C)$ with $A\,B \to C$ and
$C \to B$. The candidate keys are $\{A, B\}$ and $\{A, C\}$. $C \to B$ has a left side
that is no superkey, so BCNF says split: $\{B, C\}$ and $\{A, C\}$. Both pieces are fine.
But $A\,B \to C$ now has $A$ in one table and $B$ in another, and no single table can
check it. The engine can no longer enforce a rule that was true of the data; the only way
to check it is a join on every insert.

Third normal form is BCNF with one exemption: a dependency $X \to Y$ is tolerated when
every attribute of $Y$ belongs to some candidate key. $B$ is in $\{A, B\}$, so $C \to B$
is forgiven and $R$ stays whole. 3NF trades a little redundancy for the guarantee that a
lossless *and* dependency-preserving decomposition always exists; BCNF removes every
redundancy a functional dependency can cause, and can lose enforceability doing it. Which
to choose is a design decision, and it is worth knowing that the choice is there.

## The mistake, and where the theory ends

The most common wrong closure fires a dependency when *some* of its left side is known
rather than all of it — `A B -> C` firing on `A` alone. It is tempting because the loop
reads as "for each dependency, if it applies, add", and `lhs & reached` looks like a
test for "applies". It is not: the subset test `lhs <= reached` is the whole of what
applying means. A closure computed the other way is too large, non-keys are declared
keys, and violations vanish. The lab's test "A alone does not fire A B -> C" is there for
that reason.

The theory itself stops in two places. It handles *functional* dependencies only. A
table listing each member's phone numbers alongside each member's email addresses — two
independent multi-valued facts — is in BCNF and still repeats every phone once per email;
that is a multivalued dependency and fourth normal form, which this course leaves aside.
And it says nothing about speed. A fully normalised schema answers every report with
joins, and a real system sometimes keeps a deliberately redundant column for a query that
runs a million times a day. That is a defensible choice when it is a choice: the
redundancy is known, the dependency that makes it redundant is written down, and
something keeps the copies in step.

This module's lab, **Closures, candidate keys and a BCNF decomposer**, builds the whole
chain — `parse_fds`, `closure`, `candidate_keys`, `project_fds`, `bcnf_violations` and
`decompose` — and checks it on the transitive chain $A \to B \to C \to D$ and on the
classic relation above.
''',
                },
            ],
            "quiz": {
                "title": "Dependencies, keys and the BCNF test",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What does the dependency `A → B` actually assert?",
                        "opts": [
                            "In every legal instance of the relation, two rows agreeing on A agree on B",
                            "In the rows stored right now, no two rows agree on A and disagree on B",
                            "B can be computed from A by some formula",
                            "A is a key of the relation",
                        ],
                        "a": 0,
                        "why": (
                            "A functional dependency is a constraint on the *schema* — a promise about "
                            "every instance the table will ever hold. That is why you cannot read one "
                            "off the data: a table that happens to satisfy `A → B` today proves "
                            "nothing about tomorrow, and a table of one row satisfies every dependency "
                            "you can write. It is also not a computation; it says B is *determined* by "
                            "A, never how. And it makes A a key only in the special case where A "
                            "determines every other attribute too."
                        ),
                    },
                    {
                        "q": "R(A, B, C, D) with `A → B`, `B → C`, `C → D`. What is {B}+?",
                        "opts": ["{B, C, D}", "{B, C}", "{A, B, C, D}", "{B}"],
                        "a": 0,
                        "why": (
                            "Start with B itself, since closure is reflexive. `B → C` adds C; now `C → D` "
                            "fires and adds D; nothing else has a left side inside {B, C, D}, so the "
                            "loop stops. Nothing ever reaches A, because A appears on no right-hand "
                            "side — and an attribute that no dependency can produce has to be supplied, "
                            "so it sits in every candidate key. Since {B}+ falls short of R, B is not "
                            "even a superkey here, let alone a key."
                        ),
                    },
                    {
                        "q": "R(A, B, C) with `A B → C` and `C → B`. Which statement is true?",
                        "opts": [
                            "`C → B` violates BCNF, because {C}+ is {B, C} and that is not the whole of R",
                            "`A B → C` violates BCNF, because C belongs to no candidate key",
                            "R is in BCNF: both dependencies have a candidate key on the left",
                            "R is in BCNF, because both dependencies are non-trivial",
                        ],
                        "a": 0,
                        "why": (
                            "BCNF asks exactly one question of every non-trivial dependency: is the left "
                            "side a superkey? {A, B}+ is all of R, so `A B → C` passes. {C}+ is only "
                            "{B, C}, so `C → B` is the violation. This is the textbook relation for a "
                            "reason: C *is* part of the candidate key {A, C}, which is what makes R "
                            "third normal form and not Boyce-Codd — 3NF forgives a dependency whose "
                            "right side is prime, and BCNF does not. Being non-trivial is the "
                            "precondition for asking the question at all, never an answer to it."
                        ),
                    },
                    {
                        "q": "BCNF is strictly stronger than 3NF. So why does anyone still use 3NF?",
                        "opts": [
                            "A BCNF decomposition sometimes cannot preserve every dependency; a 3NF one always can",
                            "A BCNF decomposition can lose rows when the pieces are joined back",
                            "3NF is cheaper to check, and the check is the expensive part",
                            "BCNF applies only to relations with a single candidate key",
                        ],
                        "a": 0,
                        "why": (
                            "Both give you a lossless join — that is guaranteed by splitting on X → Y so "
                            "that the shared attributes X form a key of one piece, so losing rows is not "
                            "the trade. What BCNF can cost is dependency preservation. Decompose "
                            "R(A, B, C) with `A B → C` and `C → B` and A and B end up in different "
                            "pieces, so `A B → C` can no longer be checked without a join, and the "
                            "engine cannot enforce it locally any more. 3NF is defined so that a "
                            "lossless *and* dependency-preserving decomposition always exists; it pays "
                            "for that by tolerating exactly the dependency BCNF rejects."
                        ),
                    },
                    {
                        "q": "Decomposing R(A, B, C) on the violation `C → B` gives which two pieces?",
                        "opts": [
                            "{B, C} and {A, C}",
                            "{B, C} and {A, B}",
                            "{A, B} and {A, C}",
                            "{A, B, C} and {B, C}",
                        ],
                        "a": 0,
                        "why": (
                            "The rule is: split R into X ∪ Y and (R − Y) ∪ X. Here X is {C} and Y is "
                            "{B}, so one piece is {B, C} and the other is {A, C}. The shared attribute "
                            "is C, and C is a key of {B, C} — which is precisely the condition that "
                            "makes the join of the two pieces lossless. Leaving R itself as one of the "
                            "pieces would decompose nothing, and a split into {A, B} and {A, C} shares "
                            "only A, which determines neither piece, so joining those back would "
                            "invent rows that were never there."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "Closure and the BCNF test, in eleven lines",
                "minutes": 9,
                "caption": "normalise.py — the fixed point, then the one question BCNF asks",
                "lang": "python",
                "brief": r'''
Everything in this module reduces to two routines. The first is a fixed-point loop:
keep applying dependencies until a whole pass adds nothing. The second is a single
question asked of one dependency at a time.

They are short enough that the wrong version of either still runs, still returns a
set, and still looks like an answer.
''',
                "listing": r'''def closure(attrs, fds):
    """X+ : everything the dependencies force, starting from attrs."""
    reached = set(attrs)
    while True:
        grew = False
        for lhs, rhs in fds:
            if ___ and not rhs <= reached:
                reached ___ rhs
                grew = True
        if not ___:
            break
    return frozenset(reached)


def violates_bcnf(lhs, rhs, R, fds):
    """Does lhs -> rhs break BCNF on the relation R?"""
    if ___:
        return False          # trivial: the right side adds nothing
    return not ___ <= closure(lhs, fds)
''',
                "blanks": [
                    {
                        "prompt": "When may a dependency fire?",
                        "hole": "?",
                        "opts": [
                            "lhs & reached",
                            "rhs <= reached",
                            "lhs <= reached",
                            "reached <= lhs",
                        ],
                        "a": 2,
                        "why": "A dependency fires when its whole left side is already known — that is what `lhs <= reached` says, subset on the correct side. Every attribute of the left side, not merely one of them.",
                        "whys": [
                            "An intersection is truthy as soon as *one* attribute of the left side is known, so `A B → C` would fire on A alone. That is the single most common way to compute a closure that is far too large and to declare non-keys keys.",
                            "Testing the right side inverts the whole loop: combined with the `not rhs <= reached` that follows, the condition can never be true, and the closure returns exactly what it was given.",
                            "A dependency fires when its whole left side is already known — that is what `lhs <= reached` says, subset on the correct side. Every attribute of the left side, not merely one of them.",
                            "The subset is the wrong way round: this fires only while what you know is contained in the left side, which is true at the very start and false ever after. The closure stops one step in and returns nearly its input.",
                        ],
                    },
                    {
                        "prompt": "How does the newly implied attribute set get added?",
                        "hole": "?",
                        "opts": ["|=", "&=", "-=", "=="],
                        "a": 0,
                        "why": "Closure only ever grows, so the right side is unioned in. `reached |= rhs` is `reached = reached | rhs`, and it is what makes the loop monotone and therefore guaranteed to terminate.",
                        "whys": [
                            "Closure only ever grows, so the right side is unioned in. `reached |= rhs` is `reached = reached | rhs`, and it is what makes the loop monotone and therefore guaranteed to terminate.",
                            "Intersection shrinks the set to whatever the two have in common, so the first dependency to fire would throw away almost everything you had already established.",
                            "Difference removes the implied attributes instead of adding them — and since the guard above only fires when they are *not* yet present, this line would usually change nothing at all while `grew` still claims it did. That is an infinite loop.",
                            "`==` is a comparison, not an assignment. The line becomes an expression whose value is discarded, `reached` never changes, and the loop spins forever because `grew` is set on every pass.",
                        ],
                    },
                    {
                        "prompt": "What decides that the fixed point has been reached?",
                        "hole": "?",
                        "opts": ["reached", "fds", "rhs", "grew"],
                        "a": 3,
                        "why": "A full sweep that added nothing means no further sweep can add anything either, because the dependency list has not changed. `grew` is the flag that records whether this sweep did any work.",
                        "whys": [
                            "`reached` is non-empty whenever `attrs` is, so `not reached` is false and the loop never ends. Worse, for an empty starting set it ends immediately and returns the empty closure regardless of the dependencies.",
                            "The dependency list is a loop invariant — it is the same list on every pass — so testing it either never stops or never starts, depending only on whether there were any dependencies at all.",
                            "`rhs` is left over from the `for` loop above and holds whichever right side happened to come last. Stopping on it makes the answer depend on the order the dependencies were written in.",
                            "A full sweep that added nothing means no further sweep can add anything either, because the dependency list has not changed. `grew` is the flag that records whether this sweep did any work.",
                        ],
                    },
                    {
                        "prompt": "Which dependencies are exempt from the test?",
                        "hole": "?",
                        "opts": ["lhs == rhs", "rhs <= lhs", "lhs <= rhs", "not rhs"],
                        "a": 1,
                        "why": "A dependency is trivial when its right side is already inside its left: `A B → A` says nothing and holds in every relation, so it cannot be evidence of a design fault. BCNF only ever constrains the non-trivial ones.",
                        "whys": [
                            "Equality catches only `A → A` and misses `A B → A`, which is trivial too. Every partial overlap is then tested as though it were meaningful, and a relation in BCNF is reported as violating.",
                            "A dependency is trivial when its right side is already inside its left: `A B → A` says nothing and holds in every relation, so it cannot be evidence of a design fault. BCNF only ever constrains the non-trivial ones.",
                            "The subset is inverted. This exempts `C → A B C` — a dependency that genuinely constrains the relation — while still testing `A B → A`, which constrains nothing. The exemptions land on exactly the wrong dependencies.",
                            "An empty right side is not what trivial means, and a parser that rejects empty sides makes this test dead code. Every genuinely trivial dependency then goes on to be reported as a violation.",
                        ],
                    },
                    {
                        "prompt": "The left side must be a superkey. Of what?",
                        "hole": "?",
                        "opts": ["lhs", "fds", "R", "rhs"],
                        "a": 2,
                        "why": "X is a superkey of R exactly when X+ covers all of R, so the test is `R <= closure(lhs, fds)` and the violation is its negation. Note that superkey is relative to the relation you are testing — the same dependency can be fine on one piece and a violation on another.",
                        "whys": [
                            "A set is always inside its own closure, so this is true unconditionally and `violates_bcnf` becomes a function that returns False. A schema in any state at all would be pronounced in BCNF.",
                            "`fds` is a list of pairs, not a set of attributes, and Python refuses the comparison rather than guessing at it: `TypeError: '<=' not supported between instances of 'list' and 'frozenset'`. `violates_bcnf` does not return a wrong answer, it stops dead on its first call.",
                            "X is a superkey of R exactly when X+ covers all of R, so the test is `R <= closure(lhs, fds)` and the violation is its negation. Note that superkey is relative to the relation you are testing — the same dependency can be fine on one piece and a violation on another.",
                            "Checking only that the left side determines its own right side is checking that the dependency holds, which was assumed. It is true for every dependency in the set, so nothing is ever reported as a violation.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How many candidate keys?",
                "minutes": 8,
                "brief": r'''
Five attributes, four dependencies. Nothing here needs a decomposition — only
closures, computed in the right order.

```text
R(A, B, C, D, E)

    A  -> B C
    C D -> E
    B  -> D
    E  -> A
```

A superkey is any set whose closure covers R. A **candidate key** is a superkey
with no proper subset that is also one. Count the candidate keys.
''',
                "prompt": "How many candidate keys does R have?",
                "note": "Candidate keys, not superkeys — the minimal ones only.",
                "figure": "`R(A, B, C, D, E)` under `A → B C`, `C D → E`, `B → D`, `E → A`. Four dependencies, five attributes, and no attribute that is missing from all of them.",
                "given": [
                    {"label": "Relation", "value": "`R(A, B, C, D, E)`"},
                    {"label": "Dependencies", "value": "`A → B C`, `C D → E`, `B → D`, `E → A`"},
                    {"label": "Superkey", "value": "X with X+ ⊇ R"},
                    {"label": "Candidate key", "value": "a superkey with no proper subset that is one"},
                ],
                "aside": "Work upwards by size. Once a set is known to be a key, every larger set "
                         "containing it is a superkey and can never be minimal, so it need not be "
                         "tested at all.",
                "answer": 4,
                "tol": 0,
                "unit": "candidate keys",
                "hint": "Close each single attribute first. Then, among the pairs, only those "
                        "containing none of the single-attribute keys can still be minimal.",
                "wrong": "Superkeys are plentiful — every set containing a key is one, so there are "
                         "far more than a handful. Count only the minimal ones, and discard any "
                         "pair that already has a key inside it.",
                "why": (
                    "Singles first. {A}+ : `A → B C` gives B and C, then `B → D` gives D, then "
                    "`C D → E` gives E — all of R, so A is a key by itself. {E}+ : `E → A`, and A "
                    "then drags in the rest, so E is a key too. The others fall short: {B}+ is "
                    "{B, D}, {C}+ is {C}, {D}+ is {D}.\n\n"
                    "Any pair containing A or E already has a key inside it, so only pairs drawn "
                    "from {B, C, D} can still be minimal. {B, C}+ : `B → D` gives D, then "
                    "`C D → E` gives E, then `E → A` gives A — all of R. {C, D}+ : `C D → E` "
                    "gives E, `E → A` gives A, `A → B C` gives B — all of R. {B, D}+ is just "
                    "{B, D}, since nothing there produces C.\n\n"
                    "So the candidate keys are {A}, {E}, {B, C} and {C, D} — four of them, and "
                    "every larger set is a superkey that contains one. Worth noticing: all five "
                    "attributes appear in some candidate key, so all five are prime. That is "
                    "exactly the situation in which 3NF stops agreeing with BCNF."
                ),
            },
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
            "read": [
                {
                    "title": "What a lookup costs, counted in pages",
                    "minutes": 12,
                    "body": r'''
A thousand books, in a table on disk. Disk — spinning or solid state, it does not matter
for this — hands data over in fixed blocks of four or eight kilobytes, and the database's
buffer pool is built from blocks of the same size. Call one of them a *page*. If a book
row is around eighty bytes, fifty rows fit on a page, and the thousand rows occupy twenty
pages.

Now ask for one row: the book with `id = 42`. The engine cannot read eighty bytes; it
reads the page the row sits on, all fifty rows of it, and hands you the one you wanted.
The other forty-nine came along for free, and that is the fact the whole module rests on.
The cost of a query is the number of pages it touches, not the number of rows it returns,
and every model here counts pages.

## The scan

`SELECT * FROM book WHERE year = 1950` with no index has one strategy available: read
every page, test every row. Twenty pages at fifty rows each. Notice what the predicate
did to that cost — nothing. A scan that matches ten rows and a scan that matches none
read the same twenty pages. The cost is a property of the table, $\lceil N / p \rceil$
for $N$ rows at $p$ per page, and the query does not enter into it.

That sounds like a weakness and is also a strength. A scan reads pages in order, its cost
is known before it starts, and it never does worse than its estimate. Everything an index
buys has to be measured against that flat line.

## The tree

An index on `year` is a second structure holding, for every row, the pair
`(year, rowid)`, kept sorted by `year`. The pairs are small — a handful of bytes — so a
hundred of them fit on a page, and a thousand pairs occupy ten *leaf* pages. To find the
leaf holding 1950 without reading all ten, put a page above them holding ten pairs of
`(first year on that leaf, which leaf)`. One page, ten entries, and it directs you to the
right leaf. That page is the root, and the structure is a B+-tree of height 2: one
internal level, one leaf level, and all the data in the leaves.

Now scale it. A million entries at a hundred per leaf is ten thousand leaves; the level
above holds a hundred entries per page, so a hundred pages; the level above that, one.
Height 3. The number of entries a page can point at is the *fan-out* $f$, and each level
multiplies reach by $f$, so height grows like $\log_f N$ — and with $f$ in the hundreds
it barely grows at all. A hundred million rows is height 4. That is why "an index lookup
costs a few page reads" is true regardless of the table's size, and why three levels is
usually enough.

## The cost of a lookup, one term at a time

Find every book with `year = 1950` using the index. First, descend: from the root to the
correct leaf is $h - 1$ page reads, one per internal level. Second, walk the leaf entries
for 1950. They are contiguous, because the leaves are sorted, and there are $m$ of them
at $f$ per page, so $\lceil m / f \rceil$ leaf pages. Third — and this is the term that
decides everything — fetch the rows. Each leaf entry holds a rowid, and the row itself
lives in the table, on whatever page the table happened to put it.

If the table's rows are in no particular order with respect to `year`, the ten books from
1950 are on ten different pages, and fetching them costs ten reads. In general, $m$
reads: one page per matching row. That is an *unclustered* index, and its cost is

$$h - 1 + \left\lceil \frac{m}{f} \right\rceil + m.$$

If instead the table is stored in `year` order — *clustered* on the index — the ten rows
from 1950 sit next to each other, on one page or two, and the fetch costs
$\lceil m / p \rceil$:

$$h - 1 + \left\lceil \frac{m}{f} \right\rceil + \left\lceil \frac{m}{p} \right\rceil.$$

Same tree, same descent, same leaves. The only thing clustering changes is whether the
matching rows arrive one per page or fifty per page, and that is the difference between
a term that grows with $m$ and one that grows with $m / 50$.

## Where the scan catches up

Put the numbers in. $N = 1000$, $p = 50$, $f = 100$, so the scan is 20 pages and the tree
has height 2.

```python
def pages(rows, per_page):
    """Ceiling division: the pages that hold this many rows."""
    return -(-rows // per_page)


N, P, F = 1000, 50, 100          # rows, rows per page, index entries per leaf page
leaves = pages(N, F)
height, nodes = 1, leaves
while nodes > 1:
    nodes = pages(nodes, F)
    height += 1
scan = pages(N, P)
print(f"{leaves} leaf pages, height {height}, scan costs {scan} pages")
print(f"{'m':>4} {'unclustered':>12} {'clustered':>10}")
for m in (1, 10, 17, 18, 100, 600, 601):
    unclustered = height - 1 + pages(m, F) + m
    clustered = height - 1 + pages(m, F) + pages(m, P)
    print(f"{m:>4} {unclustered:>12} {clustered:>10}")
```

Read the unclustered column downwards. Ten matches cost 12 pages and beat the scan's 20.
Seventeen cost 19 and still win. Eighteen cost 20 — a tie, and a tie goes to the scan,
because the scan's estimate is exact and the index's is a hope about where the rows
landed. So the unclustered index wins only while fewer than eighteen rows match: under
two percent of the table. That number surprises everyone the first time, and it is the
most useful number in the module. An unclustered index is a tool for finding a few rows,
and "a few" is smaller than intuition says.

The clustered column tells the other story. Six hundred matches cost 19 and still beat
the scan; the index loses only at 601, sixty percent of the table. Clustering moved the
crossover by a factor of about $p$, because the term that grows with the result stopped
being per-row and became per-page. The derivation unit *Where the index stops paying*
reaches the same two numbers from algebra with the ceilings dropped; the lab reaches
them by search.

The fraction of the table a predicate matches is its *selectivity*, and it is the
quantity an optimiser most needs and least reliably has. An index on `year` with ten rows
per year is worth using; an index on a column with two values is a scan in disguise, and
the engine will read the table anyway unless the index can cover the query.

## Covering: deleting the expensive term

The $m$ term is one page per matching row, spent fetching columns the index does not
hold. If the index held every column the query needs, there would be nothing to fetch.
`SELECT book_id, COUNT(*) FROM loan WHERE day = ? GROUP BY book_id` touches two columns;
an index on `(day, book_id)` holds both, and the table is never opened. The cost falls to
$h - 1 + \lceil m / f \rceil$, which loses to the scan only when the index is nearly as
big as the table. SQLite says so in the plan:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE loan (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, day TEXT NOT NULL)")
conn.executemany("INSERT INTO loan VALUES (?, ?, ?)",
                 [(i, i % 7, f"2026-03-{i % 28 + 1:02d}") for i in range(1, 2001)])
conn.commit()


def plan(sql, params=()):
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return [row[-1] for row in rows]


query = "SELECT book_id, COUNT(*) FROM loan WHERE day = ? GROUP BY book_id"
print("no index:      ", plan(query, ("2026-03-04",)))
conn.execute("CREATE INDEX loan_day ON loan (day)")
print("index on day:  ", plan(query, ("2026-03-04",)))
conn.execute("CREATE INDEX loan_day_book ON loan (day, book_id)")
print("covering index:", plan(query, ("2026-03-04",)))
print("by book alone: ", plan("SELECT * FROM loan WHERE book_id = ?", (3,)))
```

`SCAN` means the whole table was read; `SEARCH ... USING INDEX` means the index narrowed
the rows first; `COVERING` means the table was never touched. Two other things moved in
that output. The `USE TEMP B-TREE FOR GROUP BY` line vanished with the covering index,
because within one day the entries are already in `book_id` order and the grouping can
read them as they come. And the last line is the composite-index rule. An index on
`(day, book_id)` is one sorted sequence, ordered by `day` and, within a single day, by
`book_id` — the way a phone book is ordered by surname and then first name. Every entry
for one day is contiguous, so `day = ?` is a search. The entries for one `book_id` are
scattered, one run per day, so nothing can be skipped, and a query on `book_id` alone
gets a scan. An index serves any *prefix* of its columns and nothing else, and the order
you declare them in is a design decision.

## The mistake

The one people make is believing an index is free speed, and adding one to every column
that appears in a `WHERE`. It is tempting because the index that helped last time helped
enormously, and because nothing visible goes wrong: the planner ignores an index that
does not pay, so the query is no slower. What goes wrong is elsewhere. Every `INSERT`,
`UPDATE` and `DELETE` on the table now maintains one more tree, which is one more page
write per row per index, and the index occupies pages of its own in the buffer pool,
evicting table pages that were doing work. An index earns its place by narrowing a query
to a few rows or by covering it entirely, and a column with low selectivity, or one that
is never a prefix of the query's predicate, does neither.

## Where the model stops holding

The model counts page reads and charges each one the same. Three things a real engine
knows are missing from it. A page already in the buffer pool costs nothing to read, so
the second run of a query, and every query on a table that fits in memory, is far cheaper
than the count says; the model describes a cold cache. On solid-state storage a random
read is closer in cost to a sequential one than it was on a spinning disk, which shrinks
the unclustered penalty without removing it. And the planner in front of you does not use
these formulas: SQLite estimates selectivity from statistics that `ANALYZE` gathers,
applies cost constants of its own, and will sometimes read an index end to end because it
is narrower than the table — a scan of the index rather than a search, which the plan
reports as `SCAN ... USING COVERING INDEX`. The model's job is not to predict SQLite's
choice to the page. It is to make the shape of the decision visible: a flat line for the
scan, a rising one for the index, and a crossover whose position depends on clustering
and selectivity and almost nothing else.

This module's lab, **Index versus scan: a cost model that decides**, builds exactly that:
`page_count`, a `BPlusIndex` whose height follows from the fan-out and whose searches use
`bisect` rather than a walk, the cost function above, and `crossover`, which should
report 18 and 601 for the demo table.
''',
                },
            ],
            "quiz": {
                "title": "Pages, trees, and the cost of a lookup",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why is the page, and not the row, the unit of cost?",
                        "opts": [
                            "Storage delivers a whole block at a time, so reading one row fetches its page whether or not the rest is wanted",
                            "Rows are variable length and pages are not",
                            "The buffer pool has no room to hold individual rows",
                            "SQL provides no way to address a single row",
                        ],
                        "a": 0,
                        "why": (
                            "Storage — spinning or solid state — has a minimum transfer unit, and the "
                            "file system and the buffer pool are both built on top of it. Asking for "
                            "one 200-byte row moves a 4 or 8 KB page into memory, so that row costs one "
                            "page read and the other forty rows sitting on the page are free. Every "
                            "cost model in this module is a consequence of that single fact. "
                            "Variable-length rows are real but beside the point; the buffer pool is "
                            "measured in pages *because* the page is the transfer unit, not the other "
                            "way round; and SQL addresses individual rows perfectly well — it is the "
                            "hardware underneath that cannot."
                        ),
                    },
                    {
                        "q": "A B+-tree over 1 000 000 entries with a fan-out of 100. How many levels, counting the leaves?",
                        "opts": ["3", "4", "5", "10 000"],
                        "a": 0,
                        "why": (
                            "1 000 000 entries at 100 per leaf is 10 000 leaf pages; 10 000 entries at "
                            "the level above pack into 100 nodes; those 100 fit under one root. Leaves, "
                            "one internal level, root — three. 10 000 is the leaf count, not the "
                            "height. Height grows like log_f(n), and with a fan-out in the hundreds it "
                            "barely grows at all: take the table to a hundred million rows and you add "
                            "a single level. That is the whole reason an index lookup costs a fixed "
                            "handful of page reads instead of something that scales with the table."
                        ),
                    },
                    {
                        "q": "The same index over the same query, once clustered and once not. What is different?",
                        "opts": [
                            "The heap fetch: clustered costs about one page per *page* of matching rows, unclustered about one page per matching *row*",
                            "The height of the tree",
                            "The number of entries in the leaves",
                            "Whether the index can serve a range query at all",
                        ],
                        "a": 0,
                        "why": (
                            "Clustering is a statement about the heap, not about the tree. If the rows "
                            "are stored in roughly index order then consecutive matches land on the "
                            "same page, and the buffer pool serves the second and the fortieth of them "
                            "for nothing. The tree itself is untouched — same entries, same fan-out, "
                            "same height — and both forms answer ranges perfectly well. What moves is "
                            "the crossover: on the lab's thousand-row table it sits at 18 matching rows "
                            "unclustered and 601 clustered, which is the difference between an index "
                            "that is almost never worth using and one that almost always is."
                        ),
                    },
                    {
                        "q": "Why does making an index *covering* change the arithmetic?",
                        "opts": [
                            "Every column the query needs is already in the index, so the heap is never visited and the per-row fetch term vanishes",
                            "It makes the tree shorter",
                            "It stores the table's rows in index order",
                            "It lets the planner skip evaluating the WHERE clause",
                        ],
                        "a": 0,
                        "why": (
                            "The expensive term in an unclustered lookup is one heap page per matching "
                            "row, and it is the only term that grows with the size of the result. If "
                            "the leaf entry already carries every column the query asks for, that term "
                            "is zero and the cost falls to the descent plus a few leaf pages. SQLite "
                            "says so out loud — the plan reads `SEARCH loan USING COVERING INDEX ...`. "
                            "Note the tree does not get shorter: an extra column makes each entry "
                            "wider, so the fan-out drops slightly and the index grows. Storing rows in "
                            "index order is clustering, a different mechanism entirely, and the `WHERE` "
                            "clause is still very much evaluated — narrowing on it is what the search is."
                        ),
                    },
                    {
                        "q": "There is an index on `(day, book_id)`. Which query can use it to *narrow* the rows it reads?",
                        "opts": [
                            "`WHERE day = ?`, because `day` is a prefix of the index key",
                            "`WHERE book_id = ?`, because `book_id` is in the index",
                            "Neither: a two-column index serves only a query that names both columns",
                            "Both equally, because the index contains both columns",
                        ],
                        "a": 0,
                        "why": (
                            "The index is one sorted sequence, ordered by `day` first and by `book_id` "
                            "only within a single day. Every entry for one `day` is therefore "
                            "contiguous, and the engine can descend straight to the start of that run "
                            "— a search. The entries for one `book_id` are scattered right through the "
                            "sequence, one per day, so nothing can be skipped; SQLite may still read "
                            "the whole index because it is narrower than the table, but that is a scan "
                            "of the index rather than a search. Naming both columns works as well, "
                            "which is why demanding both is too strong: any *prefix* of the key is "
                            "enough, and the one-column prefix is by far the commonest case."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "Reading a query plan out loud",
                "minutes": 9,
                "caption": "a sqlite3 session against a 200 000-row loan table",
                "lang": "text",
                "brief": r'''
`EXPLAIN QUERY PLAN` is the shortest feedback loop in this whole subject: you change
one thing, you ask again, and the engine tells you in half a line what it intends to
do. The vocabulary is tiny — `SCAN`, `SEARCH`, `USING COVERING INDEX`,
`USE TEMP B-TREE` — and knowing it is most of what separates guessing at performance
from measuring it.

The session below is real output from SQLite 3.50. Fill in what the engine said, and
what was asked of it.
''',
                "listing": r'''sqlite> -- 200 000 loans. The only index so far is the primary key.
sqlite> EXPLAIN QUERY PLAN
   ...> SELECT book_id, COUNT(*) FROM loan WHERE day >= ? GROUP BY book_id;
___ loan
USE TEMP B-TREE FOR GROUP BY

sqlite> CREATE INDEX loan_day ON loan (day);
sqlite> EXPLAIN QUERY PLAN
   ...> SELECT book_id, COUNT(*) FROM loan WHERE day >= ? GROUP BY book_id;
SEARCH loan USING INDEX loan_day (___)
USE TEMP B-TREE FOR GROUP BY

sqlite> CREATE INDEX loan_day_book ON loan (day, ___);
sqlite> EXPLAIN QUERY PLAN
   ...> SELECT book_id, COUNT(*) FROM loan WHERE day >= ? GROUP BY book_id;
SEARCH loan USING ___ INDEX loan_day_book (day>?)
USE TEMP B-TREE FOR GROUP BY

sqlite> EXPLAIN QUERY PLAN SELECT * FROM loan WHERE id = 42;
SEARCH loan USING ___ (rowid=?)
''',
                "blanks": [
                    {
                        "prompt": "No index on `day` yet. What is the engine doing?",
                        "hole": "?",
                        "opts": ["SEARCH", "SEEK", "FULL SCAN", "SCAN"],
                        "a": 3,
                        "why": "SQLite writes `SCAN` when it reads the whole table and `SEARCH` when an index narrows the rows first. With nothing indexed on `day`, all 200 000 rows must be read and tested. Older releases printed `SCAN TABLE loan`; the word that matters has not changed, and it is the word to look for in a slow report.",
                        "whys": [
                            "`SEARCH` is what appears once an index can restrict which rows are visited. No such index exists at this point in the session, so there is nothing to search — that is the whole reason the next two statements are there.",
                            "Not a word SQLite's planner uses. Reading plans is partly vocabulary, and the vocabulary is genuinely small: `SCAN`, `SEARCH`, `USING COVERING INDEX`, `USE TEMP B-TREE`.",
                            "Other engines say `Seq Scan` or `type: ALL`; SQLite prints a bare `SCAN`. The distinction that matters is never the adjective, only whether an index restricted the rows before they were read.",
                            "SQLite writes `SCAN` when it reads the whole table and `SEARCH` when an index narrows the rows first. With nothing indexed on `day`, all 200 000 rows must be read and tested. Older releases printed `SCAN TABLE loan`; the word that matters has not changed, and it is the word to look for in a slow report.",
                        ],
                    },
                    {
                        "prompt": "Which constraint is the index being used to satisfy?",
                        "hole": "?",
                        "opts": ["day<?", "day>?", "day=?", "book_id>?"],
                        "a": 1,
                        "why": "The bracket names the constraint the index resolved. The query says `day >= ?` and SQLite prints the bound as `day>?` — the planner records that this is a range on `day` and does not distinguish the open end from the closed one. What matters is that `day`, and nothing else, narrowed the search.",
                        "whys": [
                            "That is the opposite bound. The query wants days at or after the parameter, and SQLite would print `day<?` only if the comparison ran the other way.",
                            "The bracket names the constraint the index resolved. The query says `day >= ?` and SQLite prints the bound as `day>?` — the planner records that this is a range on `day` and does not distinguish the open end from the closed one. What matters is that `day`, and nothing else, narrowed the search.",
                            "An equality constraint prints as `day=?` and describes a different plan: one contiguous run of identical keys, rather than everything from a point onwards. The query here asks for a range.",
                            "`book_id` is not in `loan_day` and is not in the `WHERE` clause either — it appears only in the `GROUP BY`, which is exactly why the grouping still needs its own temporary B-tree.",
                        ],
                    },
                    {
                        "prompt": "Add the column that lets the index answer the whole query by itself.",
                        "hole": "?",
                        "opts": ["id", "COUNT(*)", "book_id", "member_id"],
                        "a": 2,
                        "why": "The query touches exactly two columns, `day` and `book_id`. Putting both into the index means every value it needs is in the leaves, and the table never has to be opened. The order matters too: `day` first, because that is the column being ranged over.",
                        "whys": [
                            "`id` is the rowid, and SQLite already stores the rowid beside every index entry, so appending it adds nothing the index did not have. `book_id` would still be missing, and the plan would still say `INDEX` rather than `COVERING INDEX`.",
                            "An aggregate is computed from rows; it is not a column and there is nothing to store. What can be indexed is the column being grouped by, which is what makes the aggregate cheap to compute.",
                            "The query touches exactly two columns, `day` and `book_id`. Putting both into the index means every value it needs is in the leaves, and the table never has to be opened. The order matters too: `day` first, because that is the column being ranged over.",
                            "`member_id` is not one of the columns this query mentions, so the engine would still have to visit the table to fetch `book_id` for every matching row — the per-row heap fetch stays, and nothing is covered.",
                        ],
                    },
                    {
                        "prompt": "The plan changed one word. Which one?",
                        "hole": "?",
                        "opts": ["COVERING", "CLUSTERED", "PARTIAL", "UNIQUE"],
                        "a": 0,
                        "why": "SQLite says `COVERING` when every column the query needs lives in the index, so the table is never touched. That deletes the per-row heap fetch from the cost — the one term that grows with the number of matching rows — which is how an extra column in an index turns a losing plan into a winning one without the query changing at all.",
                        "whys": [
                            "SQLite says `COVERING` when every column the query needs lives in the index, so the table is never touched. That deletes the per-row heap fetch from the cost — the one term that grows with the number of matching rows — which is how an extra column in an index turns a losing plan into a winning one without the query changing at all.",
                            "Clustering describes the order the *table* is stored in. SQLite has no clustered secondary indexes to report; the nearest thing it has is the rowid ordering of the table itself. Both tricks remove work, but by different means and with different words.",
                            "A partial index is one created with a `WHERE` clause of its own, so that it holds only some of the rows. This one was created without any such clause — and a partial index would still need the table for the columns it lacks.",
                            "Uniqueness is a constraint, not an access strategy. `loan_day_book` was created without `UNIQUE`, and two loans of the same book on the same day are perfectly legal, so it could not have been.",
                        ],
                    },
                    {
                        "prompt": "A lookup by primary key uses neither of the two indexes. What does it use?",
                        "hole": "?",
                        "opts": [
                            "TEMP B-TREE",
                            "INTEGER PRIMARY KEY",
                            "INDEX loan_day",
                            "COVERING INDEX loan_day_book",
                        ],
                        "a": 1,
                        "why": "In SQLite an `INTEGER PRIMARY KEY` *is* the rowid: the table is itself a B-tree keyed on it. A lookup by id is a descent through the table, with no separate index to consult and no second fetch afterwards — the cheapest access path the engine has, and why a surrogate integer key is so hard to beat.",
                        "whys": [
                            "A temporary B-tree is something the engine builds *during* a query in order to sort or group — you can see one doing exactly that above. It is never the structure a search is performed against.",
                            "In SQLite an `INTEGER PRIMARY KEY` *is* the rowid: the table is itself a B-tree keyed on it. A lookup by id is a descent through the table, with no separate index to consult and no second fetch afterwards — the cheapest access path the engine has, and why a surrogate integer key is so hard to beat.",
                            "That index is keyed on `day`, which this query never mentions. An index only helps when the query constrains a prefix of its key, and `id` is not a prefix of `(day)`.",
                            "`SELECT *` asks for every column, and that index holds only `day` and `book_id`, so it cannot cover this query. Even reading it end to end would leave every other column still to fetch.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Where the index stops paying",
                "minutes": 13,
                "vars": ["N", "p", "h", "f", "m"],
                "brief": r'''
The optimiser's entire question, in one inequality.

A heap of $N$ rows at $p$ rows per page. A B+-tree of height $h$ — leaf level
included — holding $f$ entries per leaf page. A query that matches $m$ rows.

Drop the ceilings. They are worth a page or two and they hide the shape; you can put
them back once you know what you are looking at. What is left is the crossover: the
number of matching rows at which the sequential scan catches the index up.
''',
                "steps": [
                    {
                        "prompt": r"A sequential scan reads the whole heap, whatever the predicate says. Write its cost in pages, in terms of $N$ and $p$.",
                        "answer": r"\frac{N}{p}",
                        "hint": r"$N$ rows packed $p$ to a page. Nothing about the query enters this — a scan that matches nothing costs exactly the same as one that matches everything.",
                        "deconstruct": [
                            r"Each page holds $p$ rows.",
                            r"So $N$ rows occupy $N/p$ pages, and every one of them is read.",
                        ],
                    },
                    {
                        "prompt": r"Now the unclustered lookup. It descends $h-1$ internal levels, walks the leaf entries for the $m$ matches at $f$ entries per leaf page, then fetches one heap page per matching row. Write the total.",
                        "given": r"Height $h$ counts the leaf level, so there are $h-1$ levels above it.",
                        "answer": r"h - 1 + \frac{m}{f} + m",
                        "hint": r"Three terms added together: the descent, the leaf pages the matches span, and the heap fetches. Only the last one is per-row.",
                        "deconstruct": [
                            r"Descending from the root to the leaf level touches $h-1$ internal nodes.",
                            r"The $m$ matching entries are contiguous in the leaves, so they span $m/f$ leaf pages.",
                            r"Unclustered means the rows themselves are scattered: one page read each, $m$ in total.",
                        ],
                    },
                    {
                        "prompt": r"Set the two costs equal and solve for $m$. This is the crossover — the match count at which the scan catches up.",
                        "given": r"$\frac{N}{p} = h - 1 + \frac{m}{f} + m$",
                        "answer": r"\frac{f \cdot (\frac{N}{p} - h + 1)}{f + 1}",
                        "hint": r"Move the constant terms to the left, then collect the two $m$ terms: $\frac{m}{f} + m = m\frac{1+f}{f}$.",
                        "deconstruct": [
                            r"$\frac{N}{p} - h + 1 = \frac{m}{f} + m$.",
                            r"The right side is $m \cdot \frac{1 + f}{f}$.",
                            r"Divide through: $m = \frac{f}{f+1}\left(\frac{N}{p} - h + 1\right)$.",
                        ],
                    },
                    {
                        "prompt": r"Cluster the index. The rows now sit in roughly index order, so the heap fetch becomes $\frac{m}{p}$ instead of $m$. Write the clustered lookup cost.",
                        "answer": r"h - 1 + \frac{m}{f} + \frac{m}{p}",
                        "hint": r"Only the last term changes. Matching rows are adjacent in the heap now, so they arrive $p$ at a time like any other page of rows.",
                        "deconstruct": [
                            r"The descent and the leaf walk are properties of the tree and do not care how the heap is ordered.",
                            r"The heap fetch becomes $m$ rows at $p$ rows per page.",
                        ],
                    },
                    {
                        "prompt": r"Solve that one for $m$ as well, to get the clustered crossover.",
                        "given": r"$\frac{N}{p} = h - 1 + \frac{m}{f} + \frac{m}{p}$",
                        "answer": r"\frac{f \cdot p \cdot (\frac{N}{p} - h + 1)}{p + f}",
                        "hint": r"Same move as before, but the two $m$ terms now share a denominator of $fp$: $\frac{m}{f} + \frac{m}{p} = m\frac{p+f}{fp}$.",
                        "deconstruct": [
                            r"$\frac{N}{p} - h + 1 = m\left(\frac{1}{f} + \frac{1}{p}\right)$.",
                            r"$\frac{1}{f} + \frac{1}{p} = \frac{p + f}{fp}$.",
                            r"So $m = \frac{fp}{p+f}\left(\frac{N}{p} - h + 1\right)$.",
                        ],
                    },
                ],
                "closing": r'''
Put the lab's numbers in. $N = 1000$, $p = 50$, $h = 2$, $f = 100$: a scan costs 20
pages and $\frac{N}{p} - h + 1 = 19$. The unclustered crossover is
$100 \times 19 / 101 \approx 18.8$ rows — under two percent of the table. The
clustered one is $100 \times 50 \times 19 / 150 \approx 633$, nearly two thirds of it.
Clustering buys roughly a factor of $p$, because the term that grows with the result
stops being per-row and becomes per-page.

The lab's exhaustive search reports 18 and 601, not 18.8 and 633. The gap is the
ceilings you dropped: $\lceil m/f \rceil$ is a whole page rather than 0.18 of one at
eighteen matches, and the two ceilings together cost the clustered plan up to two
extra pages — which, on a curve this flat, moves the crossing by about thirty rows.
The algebra gives you the shape and the order of magnitude. The exact integer is a
search, and that is the right division of labour.
''',
            },
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
            "read": [
                {
                    "title": "Interleavings, and which ones are safe",
                    "minutes": 13,
                    "body": r'''
Two librarians, two terminals, one book. *Things Fall Apart* has four copies on the
shelf. At the first terminal a copy is being returned, so the transaction there reads
`copies`, adds one and writes it back. At the second a copy is being lent, so that
transaction reads `copies`, subtracts one and writes it back. Run one after the other, in
either order, and the shelf ends at four, which is correct. Now let the engine interleave
them — which it will, because a transaction waiting on the disk is a transaction whose
turn can be given to someone else:

```python
def run(schedule, copies=4):
    """Two transactions on one shared value: T1 records a return, T2 a loan."""
    seen = {}
    delta = {1: +1, 2: -1}
    for op in schedule.split():
        kind, txn = op[0], int(op[1])
        if kind == "r":
            seen[txn] = copies
        else:
            copies = seen[txn] + delta[txn]
        print(f"  {op}: shelf holds {copies}; T1 saw {seen.get(1)}, T2 saw {seen.get(2)}")
    return copies


print("serial, T1 then T2:")
print("  final", run("r1 w1 r2 w2"))
print("interleaved:")
print("  final", run("r1 r2 w1 w2"))
```

Both transactions read four. The first wrote five; the second, still holding the four it
read, wrote three, and the return has vanished. Nothing raised, nothing logged, and one
copy of the book is now missing from the catalogue. This is the *lost update*, and it is
the reason the module exists: interleaving is what makes a database fast, and without a
rule for which interleavings are allowed, it is also what makes it wrong.

## What a transaction is promised

A transaction is a group of operations the application wants treated as one. The promise
the engine makes about it has four parts, and two of them belong to a different module.
*Atomicity* — all of it or none of it — and *durability* — once committed, it survives a
crash — are delivered by the log, which records what a transaction did so that it can be
undone or redone. *Consistency* is the application's constraints holding at every commit.
*Isolation* is the one here: each transaction should see the database as though it were
running alone. The lost update is an isolation failure, and concurrency control is the
machinery that prevents it.

## Which operations can be swapped

The serial runs were correct, so "correct" can be defined as "has the same effect as
some serial run". The question becomes which interleavings have that property, and the
way in is to ask when two operations can be swapped without anyone noticing.

Two reads of the same item can be swapped: neither changes anything, so each sees the
same value either way. Two operations on different items can be swapped whatever they
are, because neither can see the other's effect. Two operations of the same transaction
cannot be swapped, but they do not need to be — they are already in the order their
transaction gave them. What is left is a pair from *different* transactions, on the
*same* item, where at least *one writes*. Swap a read past a write and the read sees a
different value; swap two writes and a different one lands last. Those pairs *conflict*,
and they are the only pairs that carry information about which transaction came first.

So a schedule's meaning, for this purpose, is the set of orderings its conflicts impose.
For every conflicting pair, the transaction whose operation came earlier must come
earlier in any equivalent serial schedule. Draw one node per transaction and an arrow for
each such constraint, and you have the *precedence graph*.

## The graph, and the cycle

```python
import re

OPERATION = re.compile(r"([rw])(\d+)\((\w+)\)")


def edges(schedule):
    """One arrow per ordered pair of transactions forced by a conflict."""
    ops = [(kind, int(txn), item) for kind, txn, item in OPERATION.findall(schedule)]
    found = set()
    for i, (kind1, txn1, item1) in enumerate(ops):
        for kind2, txn2, item2 in ops[i + 1:]:
            if txn1 != txn2 and item1 == item2 and "w" in (kind1, kind2):
                found.add((txn1, txn2))
    return sorted(found)


for name, schedule in [("serialisable", "r1(A) w2(A) w1(B) r2(B)"),
                       ("cyclic",       "r1(A) w2(A) w2(B) r1(B)")]:
    print(f"{name:<13} {schedule}  ->  edges {edges(schedule)}")
```

The first schedule imposes $T_1 \to T_2$ twice — once on $A$, once on $B$ — and one arrow
is drawn for it. Every constraint says the same thing, so the serial schedule $T_1, T_2$
satisfies all of them: run $T_1$ entirely, then $T_2$, and every conflicting pair is in
the order it was in. The schedule is *conflict-serialisable*.

The second imposes $T_1 \to T_2$ on $A$ and $T_2 \to T_1$ on $B$. No serial order can put
$T_1$ first and also put $T_2$ first. There is no serial schedule with the same conflicts,
and the interleaving may have left the database somewhere no serial run could reach. The
rule that falls out of this is the whole of the theory: a schedule is
conflict-serialisable exactly when its precedence graph has no cycle. The lab's
`has_cycle` is a depth-first search that colours a node grey on entry and black on exit
and reports a cycle when it walks into a grey one. When there is no cycle, any
topological order of the graph — the lab takes the smallest available id first, so the
answer is reproducible — is an equivalent serial schedule.

Two things that order is not. It is not the order the transactions committed in: a
transaction can commit last and still belong first, if everything it read was read before
anyone overwrote it. And it is not the only order the schedule *could* have run in; there
are usually several, and every one of them is equally correct.

## Locks, and why one phase is not enough

The graph tells you afterwards whether a schedule was safe. A scheduler needs to refuse
an unsafe one as it happens, without knowing the future, and the tool is the lock. Before
reading an item a transaction takes a *shared* lock on it; before writing, an *exclusive*
one. Shared locks coexist, since reads do not conflict. An exclusive lock excludes
everyone else. A request that cannot be granted waits.

Locks alone are not enough, and the cyclic schedule shows why. Let $T_1$ lock $A$, read
it, and release the lock, since it is finished with $A$. $T_2$ now locks $A$, writes it,
locks $B$, writes it, and releases both. $T_1$ locks $B$ and reads it. Every operation
held the right lock at the right moment, and the schedule that ran is
`r1(A) w2(A) w2(B) r1(B)` — the cyclic one. The hole is that $T_1$ let go of $A$ and
*then* reached for $B$, which gave $T_2$ room to get between the two.

Close the hole with one rule: once a transaction has released any lock, it may not
acquire another. Every transaction then has a *growing phase* and a *shrinking phase*,
and a moment between them — its *lock point* — at which it holds everything it will ever
hold. That is two-phase locking, and it guarantees serialisability by an argument short
enough to carry around. Suppose the graph has an edge $T_1 \to T_2$: some item was
touched by $T_1$ and then, conflictingly, by $T_2$. $T_2$ needed a lock on that item which
$T_1$ held, so $T_1$ released it before $T_2$ acquired it — and $T_1$ releases nothing
before its lock point, while $T_2$ acquires nothing after its own. So $T_1$'s lock point
came first. Follow that along a cycle $T_1 \to T_2 \to \dots \to T_1$ and $T_1$'s lock
point precedes itself, which cannot be. Every schedule a two-phase scheduler emits is
acyclic. Notice what the rule does not forbid: holding many locks at once is the normal
case and the entire point, and upgrading a shared lock to an exclusive one is allowed,
provided no release has happened yet.

## Strict 2PL, cascades and deadlock

Plain 2PL lets a transaction release locks after its lock point and before it commits.
Suppose $T_1$ writes $A$, passes its lock point, releases $A$, and $T_2$ reads $A$. Then
$T_1$ aborts. The value $T_2$ read never existed, so $T_2$ must abort too, and so must
anything that read from $T_2$ in the meantime. That is a *cascading abort*, and *strict*
2PL rules it out by holding every exclusive lock until commit: nobody can read a value
until the transaction that wrote it is permanent. It is the discipline the lab's
scheduler implements, and the one real engines use.

Its price is the schedule the lab calls `DEADLOCK`:

```text
 step  operation   lock wanted     verdict
  1    r1(A)       S(A) for T1     granted
  2    r2(B)       S(B) for T2     granted
  3    w1(B)       X(B) for T1     refused: T2 holds S(B) until it commits
  4    w2(A)       X(A) for T2     refused: T1 holds S(A) until it commits
```

Both transactions are waiting, each for a lock the other will release only after
committing, and each can commit only after getting the lock. Neither did anything wrong;
the two-phase rule forbids the release that would unblock things. Waiting longer changes
nothing. The scheduler has to notice — every live transaction blocked is the condition
the lab detects, and a cycle in a waits-for graph is the general one — and break the
cycle by aborting a victim. One victim suffices, because removing one edge breaks a
cycle; the lab picks the highest-numbered blocked transaction so the answer is
reproducible. Its locks go, its remaining operations are dropped, and the survivor takes
the lock it was waiting for and runs to commit.

## The mistake, and where the theory stops

The mistake is to test for this by running the program. A non-serialisable interleaving
produces a wrong result only on the data and timing that happen to expose it; on the
lab's data the cyclic schedule may leave every value as a serial run would have. The bug
is in the schedule, not in the outcome, which is why the analysis works on the sequence
of operations and never looks at a value. It is a tempting mistake because every other
bug you have met showed up when you ran the code. A second, smaller one is to believe
that 2PL prevents deadlock. It prevents non-serialisable schedules and creates deadlocks
in the process; deadlock is handled afterwards, by detection and a victim, or by a
timeout.

Where it stops: conflict serialisability is sufficient for correctness and not necessary.
Two transactions that both write $A$ without reading it can be interleaved in a way that
cycles the graph and still ends exactly as a serial run would; that is *view*
serialisability, and it is too expensive to test for in practice, so engines settle for
the conflict version. Locks on rows cannot lock rows that do not exist yet, so a
transaction that counts the books from 1950 twice can see two different counts if someone
inserts one in between — the *phantom*, which needs locks on predicates or index ranges.
And most engines you will meet do not use 2PL for readers at all: PostgreSQL and its
relatives keep old versions of rows and let readers see a snapshot while writers proceed,
which removes most blocking and admits an anomaly of its own, write skew, that 2PL never
had. SQLite, the engine under this course, allows one writer at a time for the whole
file, so the row-level locking here is happening at a granularity SQLite never sees. The
theory is what those systems are approximating, and its vocabulary — conflict, cycle,
lock point, cascade — is how their documentation explains what they do instead.

This module's lab, **Precedence graphs and a two-phase-locking scheduler**, builds the
analysis and then the scheduler: `conflicts`, `precedence_graph`, `has_cycle` and
`serial_order` for the first half, and `two_phase_lock`, a strict scheduler that blocks,
resumes on commit, and detects and breaks the deadlock above, for the second.
''',
                },
            ],
            "quiz": {
                "title": "Conflicts, graphs and locks",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Two operations conflict when they...",
                        "opts": [
                            "belong to different transactions, touch the same item, and at least one of them writes",
                            "belong to different transactions and touch the same item",
                            "sit next to each other in the schedule",
                            "belong to different transactions and at least one of them writes",
                        ],
                        "a": 0,
                        "why": (
                            "All three conditions do work. Two reads of the same item commute — swap "
                            "them and nothing anywhere changes — so a read/read pair carries no "
                            "ordering information. Two operations of the same transaction are already "
                            "ordered by that transaction and are not free to be swapped in the first "
                            "place. And operations on different items commute whatever they do, "
                            "because neither can see the other's effect. What is left is exactly the "
                            "pair whose swap can change the outcome, which is why it is the atom the "
                            "whole theory is built from. Adjacency has nothing to do with it: a "
                            "conflict holds between operations a thousand steps apart."
                        ),
                    },
                    {
                        "q": "A schedule's precedence graph contains a cycle. What follows?",
                        "opts": [
                            "No serial schedule is conflict-equivalent to it",
                            "It is certain to deadlock",
                            "It has definitely produced a wrong answer",
                            "It contains at least one write/write pair",
                        ],
                        "a": 0,
                        "why": (
                            "A cycle says the transactions must be ordered T1 before T2 before … before "
                            "T1, and no serial order can satisfy that. It is a statement about "
                            "equivalence, not about damage: a non-serialisable schedule *may* leave the "
                            "database somewhere no serial run could reach, but on particular data it "
                            "can come out fine, which is what makes the bug so hard to find by testing. "
                            "Deadlock is a different phenomenon entirely — it belongs to locking, and a "
                            "schedule that never blocks anybody can still be cyclic. And every edge "
                            "needs only *one* write, so `r1(A) w2(A) r2(B) w1(B)` cycles with no "
                            "write/write pair in it at all."
                        ),
                    },
                    {
                        "q": "The graph turns out to be acyclic. What is a topological order of it?",
                        "opts": [
                            "A serial schedule that is conflict-equivalent to the one you ran",
                            "The order the transactions committed in",
                            "The only order in which the schedule could have been run",
                            "The order the locks were granted in",
                        ],
                        "a": 0,
                        "why": (
                            "Acyclic means every ordering constraint can be met at once, and any "
                            "topological order is a serial schedule reaching the same final state as "
                            "the interleaved one. There is usually more than one; the lab takes the "
                            "smallest available transaction id at each step purely so that the answer "
                            "is reproducible. It need not resemble the commit order at all — a "
                            "transaction can commit last and still have to be ordered first, if "
                            "everything it read was read before anyone overwrote it."
                        ),
                    },
                    {
                        "q": "What does the two-phase rule actually forbid?",
                        "opts": [
                            "Acquiring any lock after releasing any lock",
                            "Holding two locks at the same time",
                            "Releasing a lock before the transaction commits",
                            "Upgrading a shared lock to an exclusive one",
                        ],
                        "a": 0,
                        "why": (
                            "One growing phase, then one shrinking phase, and the moment between them "
                            "is the transaction's lock point. That single restriction is what "
                            "guarantees conflict-serialisability: order the transactions by their lock "
                            "points and you have the equivalent serial schedule. Holding many locks at "
                            "once is the normal case and the entire purpose. Releasing early is allowed "
                            "by plain 2PL — it is *strict* 2PL that holds everything to commit, and it "
                            "does so to rule out cascading aborts, not to keep the schedule "
                            "serialisable. Upgrading is permitted too, though it is one of the "
                            "commonest routes into a deadlock."
                        ),
                    },
                    {
                        "q": "Strict 2PL holds every exclusive lock until commit. What does that buy, and what does it cost?",
                        "opts": [
                            "It rules out cascading aborts; it makes deadlock likelier, because locks are held longer",
                            "It rules out deadlock, at the cost of throughput",
                            "It rules out non-serialisable schedules, which plain 2PL does not",
                            "It rules out lost updates, which plain 2PL does not",
                        ],
                        "a": 0,
                        "why": (
                            "Nobody can read or overwrite an uncommitted value, so no transaction ever "
                            "has to be rolled back merely because another one was. That is the "
                            "cascadeless property, and it is also what makes recovery simple: undoing "
                            "one transaction never drags a second one down with it. The price is that "
                            "every lock is held to the very end, which widens the window in which two "
                            "transactions can end up waiting on each other. Plain 2PL already "
                            "guarantees serialisability and already rules out lost updates; deadlock is "
                            "prevented by neither, and is dealt with after the fact — by a timeout, or "
                            "by finding a cycle in the waits-for graph and aborting somebody."
                        ),
                    },
                ],
            },
            "blanks": {
                "title": "A deadlock, one step at a time",
                "minutes": 9,
                "caption": "the scheduler's own trace of r1(A) r2(B) w1(B) w2(A) c1 c2",
                "lang": "text",
                "brief": r'''
This is the schedule the lab calls `DEADLOCK`, and it is worth walking by hand before
you make a machine do it. Two transactions each read one item and then reach for the
other. Neither has done anything wrong. Neither can proceed.

Read the *lock wanted* column as a request and the *verdict* column as the lock
manager's reply.
''',
                "listing": r'''Strict 2PL running   r1(A)  r2(B)  w1(B)  w2(A)  c1  c2

S(x) = shared lock on x, X(x) = exclusive lock on x.
Shared locks coexist; an exclusive lock excludes everyone else.

 step  operation   lock wanted    verdict
 ----  ----------  -------------  ------------------------------------------
  1    r1(A)       S(A) for T1    granted -- nobody holds A
  2    r2(B)       ___ for T2     granted -- nobody holds B
  3    w1(B)       X(B) for T1    ___
  4    w2(A)       ___ for T2     refused -- T1 holds S(A) and has not committed
  5    --          --             ___
  6    abort T2    --             T2's locks go; T1 ___
''',
                "blanks": [
                    {
                        "prompt": "T2 is reading B. What does it need?",
                        "hole": "?",
                        "opts": ["S(B)", "X(B)", "S(A)", "X(B) for T1"],
                        "a": 0,
                        "why": "A read needs a shared lock on the item being read, so `r2(B)` asks for `S(B)`. Nobody holds B, and shared locks coexist anyway, so it is granted immediately.",
                        "whys": [
                            "A read needs a shared lock on the item being read, so `r2(B)` asks for `S(B)`. Nobody holds B, and shared locks coexist anyway, so it is granted immediately.",
                            "An exclusive lock is what a *write* needs. Taking one to read would be correct but needlessly strict — it would block every other reader of B, and the deadlock two steps later would arrive one step sooner.",
                            "Wrong item. T2 is reading B here; A is what it reaches for at step 4, and that is where its trouble starts.",
                            "Wrong transaction as well as wrong mode. It is T2 that is executing this step, and T1 has no interest in B until step 3.",
                        ],
                    },
                    {
                        "prompt": "T1 wants to write B, which it has not locked at all.",
                        "hole": "?",
                        "opts": [
                            "granted -- a writer takes priority over a reader",
                            "refused -- T1 already holds S(A)",
                            "refused -- T2 holds S(B)",
                            "granted -- T1 may upgrade its own lock",
                        ],
                        "a": 2,
                        "why": "An exclusive lock excludes everyone else, and T2 is holding `S(B)` from step 2. Under strict 2PL T2 will not let go until it commits, so T1 waits — it is not aborted, it is simply blocked, and the scheduler moves on to somebody else's operation.",
                        "whys": [
                            "No such rule exists in plain two-phase locking. Priority schemes are how some systems *prevent* deadlock — wound-wait and wait-die both work by letting one transaction shove another aside — but they are an addition to 2PL, not part of it.",
                            "Holding `S(A)` is entirely legitimate and is not a reason to refuse anything. The two-phase rule constrains when locks may be acquired relative to releases, never how many may be held at once.",
                            "An exclusive lock excludes everyone else, and T2 is holding `S(B)` from step 2. Under strict 2PL T2 will not let go until it commits, so T1 waits — it is not aborted, it is simply blocked, and the scheduler moves on to somebody else's operation.",
                            "An upgrade is a shared lock of your own becoming exclusive, and it is allowed only when yours is the *only* shared lock on the item. T1 holds no lock on B at all, so there is nothing here to upgrade.",
                        ],
                    },
                    {
                        "prompt": "T2 wants to write A. What does it ask for?",
                        "hole": "?",
                        "opts": ["S(A)", "X(B)", "an upgrade of S(A)", "X(A)"],
                        "a": 3,
                        "why": "A write needs an exclusive lock on the item written, so `w2(A)` asks for `X(A)`. T1 holds `S(A)` and will not release it before committing, so this is refused and T2 blocks too.",
                        "whys": [
                            "A shared lock permits reading only. It would in fact be granted here, since shared locks coexist — and the write would then proceed with no protection at all, which is the precise hole the lock modes exist to close.",
                            "Wrong item: B is the one T2 already holds. It is the reach for A that closes the circle.",
                            "T2 holds no lock on A to upgrade — and even if it did, an upgrade needs to be the only shared lock on the item, which it would not be while T1 holds `S(A)`.",
                            "A write needs an exclusive lock on the item written, so `w2(A)` asks for `X(A)`. T1 holds `S(A)` and will not release it before committing, so this is refused and T2 blocks too.",
                        ],
                    },
                    {
                        "prompt": "Both transactions are now waiting. What has the scheduler detected?",
                        "hole": "?",
                        "opts": [
                            "a lock conflict, to be retried from the front of the queue",
                            "a deadlock: every live transaction is blocked, so nothing can release anything",
                            "starvation: T2 will get its lock eventually",
                            "a non-serialisable schedule",
                        ],
                        "a": 1,
                        "why": "A lock is released by a commit, and a commit is reached by executing operations. With every live transaction blocked, no operation can run, so no lock can ever be released. Waiting longer changes nothing, which is exactly the condition worth naming.",
                        "whys": [
                            "Retrying is what the scheduler does after every commit, and it is the right response to an ordinary conflict. Here there is no commit coming, so a retry produces the identical refusals for ever.",
                            "A lock is released by a commit, and a commit is reached by executing operations. With every live transaction blocked, no operation can run, so no lock can ever be released. Waiting longer changes nothing, which is exactly the condition worth naming.",
                            "Starvation is a transaction that *could* proceed but keeps being passed over. Here T2 cannot proceed under any scheduling at all, because the lock it waits for is held by a transaction that is itself waiting on T2.",
                            "The schedule that 2PL has actually produced so far is serialisable — that is what the protocol guarantees, and it never emits a cyclic one. Deadlock is the price paid for that guarantee, not a failure of it.",
                        ],
                    },
                    {
                        "prompt": "T2 is aborted and its locks released. What becomes of T1?",
                        "hole": "?",
                        "opts": [
                            "must restart from r1(A) as well",
                            "must release S(A) before it can continue",
                            "is aborted too, since both were blocked",
                            "may now take X(B) and run to commit",
                        ],
                        "a": 3,
                        "why": "Releasing T2's `S(B)` leaves B unheld, so T1's pending `X(B)` is granted the moment the scheduler retries the queue, and T1 goes on to commit. Breaking the cycle takes exactly one victim; the survivors lose nothing.",
                        "whys": [
                            "T1 has done nothing that needs undoing, and nothing it wrote was read by T2 — strict 2PL guarantees that. Restarting it would throw away correct work for no reason, which is what a *cascading* abort does and what strict 2PL exists to prevent.",
                            "Releasing `S(A)` is precisely what T1 must not do: acquiring `X(B)` after a release would break the two-phase rule and forfeit the serialisability guarantee. Locks come off at commit, all together.",
                            "Aborting everybody would resolve the deadlock and also lose every transaction involved. One victim is enough, because removing one edge is enough to break a cycle — the lab picks the highest-numbered blocked transaction only so the choice is deterministic.",
                            "Releasing T2's `S(B)` leaves B unheld, so T1's pending `X(B)` is granted the moment the scheduler retries the queue, and T1 goes on to commit. Breaking the cycle takes exactly one victim; the survivors lose nothing.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How many edges in the precedence graph?",
                "minutes": 8,
                "brief": r'''
Two operations **conflict** when they belong to different transactions, touch the
same item, and at least one of them writes. Each conflicting pair forces an ordering:
the earlier transaction must come before the later one in any equivalent serial
schedule, and that is drawn as one arrow.

```text
S:   r1(A)  r2(A)  w3(A)  r2(B)  w1(B)  r3(B)  w2(A)  c1  c2  c3
```

Build the precedence graph of S and count its **edges** — the distinct arrows, not
the conflicts that justify them.
''',
                "prompt": "How many distinct edges does the precedence graph of S contain?",
                "note": "An edge is an ordered pair of transactions. Two conflicts between the same pair, in the same direction, draw one arrow.",
                "figure": "`S = r1(A) r2(A) w3(A) r2(B) w1(B) r3(B) w2(A) c1 c2 c3` — three transactions, two data items, seven operations before the commits.",
                "given": [
                    {"label": "Transactions", "value": "T1, T2, T3"},
                    {"label": "Items", "value": "A and B"},
                    {"label": "Conflict", "value": "different transactions, same item, at least one write"},
                    {"label": "Count", "value": "edges, not conflicting pairs"},
                ],
                "aside": "Commits are not operations on data, so they never conflict with anything "
                         "and never contribute an edge.",
                "answer": 5,
                "tol": 0,
                "unit": "edges",
                "hint": "Take one item at a time. Write out that item's operations in schedule "
                        "order, then test every earlier/later pair among them.",
                "wrong": "Count arrows, not conflicts. The same ordered pair of transactions can be "
                         "forced twice — even on two different items — and it is still one arrow.",
                "why": (
                    "On A, in schedule order: r1, r2, w3, w2. The two reads commute, so they are "
                    "no constraint. r1 before w3 gives T1 → T3. r1 before w2 gives T1 → T2. r2 "
                    "before w3 gives T2 → T3. r2 and w2 are the same transaction, so nothing. w3 "
                    "before w2 gives T3 → T2.\n\n"
                    "On B, in schedule order: r2, w1, r3. r2 before w1 gives T2 → T1. r2 and r3 "
                    "are both reads. w1 before r3 gives T1 → T3.\n\n"
                    "Six conflicting pairs — but T1 → T3 was forced twice, once on A and once on "
                    "B, and one arrow is drawn for it. So the edges are T1 → T2, T1 → T3, "
                    "T2 → T1, T2 → T3 and T3 → T2: five.\n\n"
                    "Now look at what you have drawn. T1 → T2 and T2 → T1 are both there, so the "
                    "graph is cyclic and S is not conflict-serialisable. Which also means no "
                    "two-phase-locking scheduler could ever have produced it — 2PL emits only "
                    "acyclic schedules, and this is the kind of interleaving it exists to refuse."
                ),
            },
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
