"""ELEC420 — Security Track: Offensive & Defensive Security."""

COURSE = {
    "id": "ELEC420",
    "title": "Security Track — Offensive & Defensive Security",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["SEC301"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 140,
    "icon": "⛨",
    "summary": (
        "Attack and defence are the same body of knowledge read in two directions. "
        "You build deliberately broken components — a concatenated SQL query, an "
        "unchecked stack frame, an unthrottled login endpoint — defeat each one with a "
        "payload you construct yourself, then rebuild it so the same payload fails. "
        "Everything runs offline in the browser: simulated memory, synthetic logs, no "
        "network and no working malware."
    ),
    "outcomes": [
        "Construct an injection payload that defeats a string-concatenated query, and rewrite the query so it cannot",
        "Encode untrusted text so that a stored cross-site scripting payload renders as inert characters",
        "Model a stack frame as bytes and explain how an over-long copy reaches the saved return address",
        "Detect frame corruption with a canary and prevent it with a bounds-checked copy",
        "Quantify offline cracking cost from a password policy and a work factor, and justify a policy from it",
        "Implement HOTP/TOTP verification with a drift window, and exponential backoff against online guessing",
        "Measure a detector against labelled data with precision and recall rather than intuition",
    ],
    "assessment": "4 lab checkpoints (10% each) + defensive toolkit capstone (60%).",
    "reading": [
        "Anderson, *Security Engineering*, 3rd ed. (Wiley, 2020) — chapters 3, 6 and 21",
        "Stuttard & Pinto, *The Web Application Hacker's Handbook*, 2nd ed. (Wiley, 2011) — chapters 9 and 12",
        "Shostack, *Threat Modeling: Designing for Security* (Wiley, 2014) — the STRIDE chapters",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "read": [
                {
                    "title": "One quote that turns data into a command",
                    "minutes": 12,
                    "body": r'''
A login form has two boxes. Someone types `alice` into the first and a password
into the second, and the server, wanting to know whether that name exists, builds
a database query by pasting the name into a sentence:

```python
username = "alice"
sql = "SELECT name, role FROM users WHERE name = '" + username + "'"
print(sql)
```

That prints `SELECT name, role FROM users WHERE name = 'alice'`. The two single
quotes the server wrote are the fence: everything between them is a *string
literal*, a piece of data the database compares against, and the word `alice`
lives safely inside that fence. Now the same server, the same line, and a
visitor who types `' OR '1'='1` into the name box:

```python
username = "' OR '1'='1"
sql = "SELECT name, role FROM users WHERE name = '" + username + "'"
print(sql)
```

The result is `SELECT name, role FROM users WHERE name = '' OR '1'='1'`. Read it
as the database reads it. The opening quote the server wrote is closed
immediately by the quote the visitor typed, making an empty string. Then comes
`OR '1'='1'`, which the database parses not as data but as *more query* — a
condition that is true for every row in the table. The fence did not hold,
because the visitor supplied their own closing quote and everything after it
crossed from the data side into the command side.

That crossing is the whole of injection. There is a channel meant for data and a
channel meant for control — the keywords, operators and structure that say what
the query *does* — and a bug that lets bytes from the first channel be read as
the second. It is the same defect whether the target is SQL, an HTML page, a
shell command, or an LDAP filter. Learn to see the fence and to see what closes
it, and you have seen every variant at once.

## Watching the payload work, and then fail

Set up a real table and run both the broken query and its fix against the
identical payload.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT, role TEXT)")
conn.executemany("INSERT INTO users VALUES (?, ?)",
                 [("alice", "admin"), ("bob", "user"), ("carol", "user"), ("o'brien", "user")])

payload = "' OR '1'='1"
unsafe = "SELECT name FROM users WHERE name = '" + payload + "'"
print([row[0] for row in conn.execute(unsafe)])
print([row[0] for row in conn.execute("SELECT name FROM users WHERE name = ?", (payload,))])
print([row[0] for row in conn.execute("SELECT name FROM users WHERE name = ?", ("o'brien",))])
```

The three printed lines are the entire lesson. The first is
`['alice', 'bob', 'carol', "o'brien"]` — the whole table leaked, because the
always-true condition matched every row. The second is `[]` — the *same bytes*,
passed as a parameter with a `?` placeholder, matched nobody, because they were
never parsed as query text. The third is `["o'brien"]` — a real customer whose
name genuinely contains an apostrophe, found without trouble.

The `?` is the fix, and it is worth being precise about why. With a placeholder,
the database receives the query text and the value over two separate channels: it
compiles `SELECT name FROM users WHERE name = ?` first, deciding the shape of the
query while the value is still absent, and only then binds `' OR '1'='1` into the
already-compiled statement as data. There is no step at which those bytes can
become structure, because structure was fixed before they arrived. This is not
escaping the quote — the database is not searching the string for dangerous
characters. The value simply never visits the parser.

That third line matters as much as the attack. Watch what the concatenated query
does with the honest apostrophe:

```python
# raises sqlite3.OperationalError
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT, role TEXT)")
conn.execute("INSERT INTO users VALUES ('o''brien', 'user')")
sql = "SELECT name FROM users WHERE name = '" + "o'brien" + "'"
print(sql)
conn.execute(sql)
```

The printed query is `SELECT name FROM users WHERE name = 'o'brien'`, and it
raises a syntax error, because the apostrophe in `o'brien` closes the literal in
exactly the way the attacker's quote did. The point is that the string-building
approach is not "safe until someone attacks it." It is already broken for
ordinary data. Every legitimate O'Brien and D'Angelo has been demonstrating the
vulnerability, by accident, for as long as the code has run.

## The same bug on a page

Now the query is safe and the row is fetched. The application shows a comment the
user wrote. If it pastes that comment straight into the page's HTML, the fence is
back, and this time the control channel is the browser's HTML parser:

```python
ESCAPES = [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"), ("'", "&#x27;")]


def escape_html(text):
    out = str(text)
    for raw, entity in ESCAPES:
        out = out.replace(raw, entity)
    return out


def escape_ampersand_last(text):
    out = str(text)
    for raw, entity in reversed(ESCAPES):
        out = out.replace(raw, entity)
    return out


print(escape_html('<script>alert("xss")</script>'))
print(escape_html("Tom & Jerry"))
print(escape_ampersand_last("<b>"))
```

The first line prints
`&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;`. Those `&lt;` and `&gt;`
sequences are HTML *entities*: the browser renders them as the literal characters
`<` and `>` on the page and never as the start of a tag. The script the attacker
stored can no longer open an element, so it displays as text instead of running.
This is stored cross-site scripting neutralised — stored because the payload
lives in the database and fires for every later visitor, as against reflected
XSS, which bounces a payload straight back off a single crafted request.

The third printed line is the mistake, isolated. `escape_ampersand_last` runs the
same five replacements in the wrong order, and on the input `<b>` it prints
`&amp;lt;b&amp;gt;`. Encoding `<` produced `&lt;`, and then the later pass over
`&` reached into that entity and turned its ampersand into `&amp;`, so the page
now shows the literal text `&lt;b&gt;` instead of a bold marker. The rule that
falls out of this is not arbitrary: because every entity you produce begins with
`&`, the ampersand must be encoded *first*, before any pass that might create
one. Encode it last and you double-encode everything you just made. This is the
single mistake people reliably make with output encoding, and it is tempting
precisely because processing the list top to bottom feels natural and the bug is
invisible until a `<` and an `&` appear together.

## Where the fence picture stops

Two boundaries are worth marking. First, output encoding is context-specific.
The five-character HTML-body encoding above is correct for text between tags, but
text going into a URL, a JavaScript string, or a CSS value each has its own
control characters and its own escaping, and using HTML entities in those places
protects nothing. The rule is to encode for the sink the data lands in, not once
at the source for all sinks at once. Second, parameters cannot carry *identifiers*
— a table or column name cannot be a `?`, because the database must know the
query's shape before binding values. When a name genuinely must be chosen at
runtime, a placeholder has nothing to bind, and the only safe move is an
allow-list: compare the requested name against a fixed set of permitted ones and
refuse anything else. Escaping an identifier by hand is where the next injection
lives.

The lab, **Breaking and fixing a login lookup**, is this reading made executable.
You will write the concatenating `build_lookup_sql` and watch `' OR '1'='1`
return every row through it; write the parameterised `lookup_safe` and watch the
same payload return nothing while `o'brien` works; and write `escape_html` and
`render_comment` so a stored `<script>` tag arrives on the page as inert text and
a stray quote in an author's name cannot pry open an HTML attribute.
'''
                }
            ],
            "quiz": {
                "title": "Channels, fences, and what actually closes them",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A login query is built as `\"... WHERE name = '\" + username + \"'\"` and someone submits `' OR '1'='1` as the username, returning every row. What did the payload actually exploit?",
                        "opts": [
                            "The visitor's quote closed the literal early, so the text after it was parsed as query structure rather than data",
                            "The `OR` keyword binds more tightly than the surrounding `WHERE` clause, so it overrode the name comparison the query had originally intended",
                            "The database compared the password channel to the name channel and let a blank password through",
                            "SQLite treats `'1'='1'` as a stored procedure call that returns the full table on demand",
                        ],
                        "a": 0,
                        "whys": [
                            r"Right: the server wrote an opening quote, the visitor supplied the closing one, and everything past it — `OR '1'='1'` — crossed from the data channel into the control channel and was parsed as a condition.",
                            r"Precedence decides how a parsed expression groups, but it explains nothing about why the attacker's text was parsed as an expression at all. The bug happened one step earlier, when a closing quote let data become structure.",
                            r"There is one query and one channel here, for the name; the password is nowhere in this statement. The leak is not a comparison between fields, it is data reinterpreted as query text.",
                            r"`'1'='1'` is an ordinary always-true comparison, not a procedure. Nothing is being called; a condition that every row satisfies is simply being appended to the WHERE clause.",
                        ],
                        "why": r'''
The server's SQL string carries an opening quote that the attacker's leading
quote closes. From that point the remaining bytes — `OR '1'='1'` — sit outside
any literal, so the database reads them as query structure: a condition true for
every row. Injection is exactly this crossing from the data channel to the
control channel, and precedence, procedures and the password field are all beside
the point.
''',
                    },
                    {
                        "q": "Rewriting the query with a `?` placeholder and passing the username as a parameter stops the attack. Why does the identical payload now match nothing?",
                        "opts": [
                            "The database strips quotes and other dangerous characters out of any value bound to a parameter",
                            "The query's structure is compiled before the value is bound, so the value can never be parsed as query text",
                            "Parameters are automatically HTML-entity-encoded, which neutralises the injected quote",
                            "The placeholder limits the bound value to the column's declared maximum length, truncating the payload just before it reaches its `OR`",
                        ],
                        "a": 1,
                        "whys": [
                            r"A tempting picture, but the database is not searching the value for anything. Nothing is stripped or altered — `o'brien` binds intact and matches. The value simply never reaches the parser.",
                            r"Right: the statement is compiled with the value still absent, fixing the query's shape, and only then is the payload bound as data. There is no later step at which those bytes could become structure.",
                            r"HTML entities belong to the page's HTML parser, a different sink entirely. A parameter binds raw bytes to a compiled statement; entity encoding never enters the database path.",
                            r"Binding does no truncation; the whole value is compared as-is. The payload fails to match because it was never parsed as a condition, not because it was cut short.",
                        ],
                        "why": r'''
With a placeholder the database compiles `... WHERE name = ?` while the value is
absent, so the query's shape is decided before the payload exists to influence
it. The value is then bound as pure data. It is not escaped, filtered or
truncated — `o'brien` binds unharmed and matches — it simply never visits the
parser, so `' OR '1'='1` is compared as a name and matches nobody.
''',
                    },
                    {
                        "q": "The safe query is written; a customer genuinely named `o'brien` logs in. What does this reveal about the concatenating version that was replaced?",
                        "opts": [
                            "The parameterised query will now reject `o'brien` too, because the apostrophe is a reserved character the placeholder is obliged to strip out",
                            "The concatenating query was fine for real names and only failed on deliberately hostile input",
                            "The concatenating query was already broken for ordinary data, crashing on any name containing an apostrophe",
                            "Apostrophes in names must be stripped at signup so both query styles behave the same",
                        ],
                        "a": 2,
                        "whys": [
                            r"The parameterised query binds `o'brien` as data and finds the row without trouble — that is the whole point of the placeholder. The apostrophe is only dangerous when pasted into query text.",
                            r"This is the comforting story that keeps string-building alive, and it is false. The honest apostrophe closes the literal exactly as the attacker's quote did; the query was broken all along.",
                            r"Right: `... name = 'o'brien'` has an unbalanced quote and raises a syntax error, so every real O'Brien was demonstrating the vulnerability by accident long before any attacker arrived.",
                            r"Mangling real names to fit a broken query is fixing the wrong thing. The apostrophe is legitimate data; the defect is a query that cannot hold data, and the parameter already handles it.",
                        ],
                        "why": r'''
`SELECT name FROM users WHERE name = 'o'brien'` has three single quotes, so the
literal closes at the second and `brien'` is left as a syntax error. The
apostrophe a real customer types does precisely what the attacker's quote did.
The concatenating query was never "safe until attacked" — it was already broken
for ordinary data, and the placeholder that stops the attack is the same thing
that lets O'Brien log in.
''',
                    },
                    {
                        "q": "An HTML-body encoder replaces `&<>\"'` with entities. Running the replacements with `&` handled last turns `<b>` into `&amp;lt;b&amp;gt;`. What went wrong?",
                        "opts": [
                            "The `<` and `>` characters must be encoded before `&` or the browser closes the tag early",
                            "The pass over `&` reached into the `&lt;` already produced and re-encoded its ampersand",
                            "Five characters is too few; without encoding the space the entities run together",
                            "Entities must be uppercase, so `&lt;` should have been written `&LT;`",
                        ],
                        "a": 1,
                        "whys": [
                            r"Order does matter, but the other way: `&` must come first, not last. Encoding `<` early is harmless; the damage is a later `&` pass mangling the entity that early pass created.",
                            r"Right: encoding `<` yields `&lt;`, and because `&` is processed afterwards it finds that new ampersand and turns it into `&amp;`, so the page shows the literal text `&lt;` instead of a `<`.",
                            r"Spacing has nothing to do with it; `&amp;lt;` is a correctly-formed but doubly-encoded entity. The defect is re-encoding, not entities colliding for want of a separator.",
                            r"HTML entity names are case-sensitive and lowercase — `&lt;` is correct and `&LT;` would not render. Case is not what produced the doubled `&amp;`.",
                        ],
                        "why": r'''
Every entity this encoder produces begins with `&`. Encode `<` first and you have
`&lt;`; let a later pass over `&` run and it rewrites that ampersand to `&amp;`,
double-encoding what you just made. The fix is to encode `&` before any pass that
can create one, which is exactly why the ampersand goes first in the list.
''',
                    },
                    {
                        "q": "The five-character HTML-body encoding is applied to a value, but that value is then placed inside a `href` URL and, elsewhere, inside a `<script>` string. What is the flaw in encoding once at the source?",
                        "opts": [
                            "Encoding at the source is correct; the same entities are safe in every location a value can appear",
                            "Each sink — HTML body, URL, JavaScript string — has its own control characters, so encoding must match the context the value lands in",
                            "Source encoding at the point of storage is fine as long as the same value is also parameterised in every database query that later touches it",
                            "The value should be encoded twice at the source so it survives being decoded once in transit",
                        ],
                        "a": 1,
                        "whys": [
                            r"HTML entities protect an HTML body and nothing else. Dropped into a URL or a script string they neither escape the characters that matter there nor render correctly, so a single source pass is not universally safe.",
                            r"Right: a URL, a JavaScript string and an HTML body each have distinct dangerous characters and distinct escaping, so the encoding has to be chosen for the sink the data reaches, not applied once for all of them.",
                            r"Parameterisation defends the database channel; it says nothing about a value later written into a page's URL or script. The two are separate sinks needing separate handling.",
                            r"Double-encoding at the source produces visibly wrong output and still uses the wrong scheme for a URL or a script. The answer is context-matched encoding, not more of the same encoding.",
                        ],
                        "why": r'''
Output encoding is context-specific. The five-character scheme is right for text
between tags, but a URL, a CSS value and a JavaScript string each have their own
control characters and their own escaping. Encode for the sink the data lands in,
at the moment it lands there — a single source-side pass protects the HTML body
and leaves every other context exposed.
''',
                    },
                ],
            },
            "title": "Injection and output encoding",
            "summary": "Why concatenating data into a query or a page is the same bug twice.",
            "concepts": [
                "Injection is a confusion of channels: data crossing into the control channel",
                "String concatenation into SQL hands the parser attacker-controlled syntax",
                "Parameterised statements send code and data over separate channels",
                "Escaping the *sink* beats sanitising the *source*: encode on output, per context",
                "Stored XSS persists the payload; reflected XSS bounces it back off one request",
                "HTML entity encoding neutralises `& < > \" '` before the parser sees them",
                "Allow-lists constrain identifiers (table and column names) that cannot be parameterised",
            ],
            "lab": {
                "title": "Breaking and fixing a login lookup",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
`main.py` opens an in-memory SQLite database holding four users, in this order:

```text
alice    admin
bob      user
carol    user
o'brien  user
```

Write four functions.

**`build_lookup_sql(username)`** — the deliberately broken query builder. It
concatenates the username straight into the SQL text and returns the string:

```text
build_lookup_sql("alice")
->  SELECT name, role FROM users WHERE name = 'alice'
```

**`lookup_unsafe(conn, username)`** — run that string and return the list of
matching names, in row order. This is the vulnerable code path, and you will
show that it is: the payload `' OR '1'='1` closes the literal and appends a
condition that is always true, so every row comes back.

**`lookup_safe(conn, username)`** — the same lookup written with a `?`
placeholder and a parameter tuple. The payload must now match nothing, and the
legitimate name `o'brien` — which crashes the unsafe version with a syntax
error — must work.

**`escape_html(text)`** — HTML entity encoding for the five dangerous
characters. Encode `&` first, or you will double-encode the entities you just
produced.

```text
&  ->  &amp;      <  ->  &lt;      >  ->  &gt;
"  ->  &quot;     '  ->  &#x27;
```

**`render_comment(author, body)`** — build one comment element, encoding both
untrusted fields:

```text
<li class="comment"><b>AUTHOR</b>: BODY</li>
```

A `<script>` tag in `body` must come out as `&lt;script&gt;`, and a stray `"`
in `author` must not be able to open an HTML attribute.
''',
                "files": [{"name": "main.py", "content": r'''
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT, role TEXT)")
conn.executemany("INSERT INTO users VALUES (?, ?)", [
    ("alice", "admin"),
    ("bob", "user"),
    ("carol", "user"),
    ("o'brien", "user"),
])
conn.commit()

ESCAPES = [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"), ("'", "&#x27;")]


def build_lookup_sql(username):
    """The vulnerable builder: username concatenated into the SQL text."""
    # your code here


def lookup_unsafe(conn, username):
    """Run build_lookup_sql and return the matching names, in row order."""
    # your code here


def lookup_safe(conn, username):
    """The same lookup, parameterised with a ? placeholder."""
    # your code here


def escape_html(text):
    """HTML entity encoding. Encode & before anything else."""
    # your code here


def render_comment(author, body):
    """One <li> element with both untrusted fields encoded."""
    # your code here


print(build_lookup_sql("alice"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT, role TEXT)")
conn.executemany("INSERT INTO users VALUES (?, ?)", [
    ("alice", "admin"),
    ("bob", "user"),
    ("carol", "user"),
    ("o'brien", "user"),
])
conn.commit()

ESCAPES = [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"), ("'", "&#x27;")]


def build_lookup_sql(username):
    """The vulnerable builder: username concatenated into the SQL text."""
    return "SELECT name, role FROM users WHERE name = '" + str(username) + "'"


def lookup_unsafe(conn, username):
    """Run build_lookup_sql and return the matching names, in row order."""
    cursor = conn.execute(build_lookup_sql(username))
    return [row[0] for row in cursor.fetchall()]


def lookup_safe(conn, username):
    """The same lookup, parameterised with a ? placeholder."""
    cursor = conn.execute("SELECT name, role FROM users WHERE name = ?", (username,))
    return [row[0] for row in cursor.fetchall()]


def escape_html(text):
    """HTML entity encoding. Encode & before anything else."""
    out = str(text)
    for raw, entity in ESCAPES:
        out = out.replace(raw, entity)
    return out


def render_comment(author, body):
    """One <li> element with both untrusted fields encoded."""
    return ('<li class="comment"><b>' + escape_html(author) + "</b>: "
            + escape_html(body) + "</li>")


print(build_lookup_sql("alice"))
print(lookup_unsafe(conn, "' OR '1'='1"))
print(lookup_safe(conn, "' OR '1'='1"))
print(render_comment("mallory", "<script>alert(1)</script>"))
'''}],
                "hints": [
                    "The unsafe builder is one concatenation: an opening quote, the username, a closing quote.",
                    "`conn.execute(sql)` returns a cursor; `[row[0] for row in cursor.fetchall()]` pulls the names out.",
                    "The safe version passes a *tuple*: `conn.execute(sql_with_qmark, (username,))` — the trailing comma matters.",
                    "`ESCAPES` is already in the order you need. Loop over it and `.replace` each pair in turn.",
                ],
                "tests": [
                    {"name": "The vulnerable builder concatenates", "code": r'''
_got = build_lookup_sql("alice")
_want = "SELECT name, role FROM users WHERE name = 'alice'"
assert _got == _want, f"build_lookup_sql('alice') gave {_got!r}, expected {_want!r}"
assert "?" not in _got, "This builder is meant to be broken — no placeholder here"
'''},
                    {"name": "An always-true payload defeats it", "code": r'''
_leak = lookup_unsafe(conn, "' OR '1'='1")
assert _leak == ["alice", "bob", "carol", "o'brien"], \
    f"The payload should return every row, got {_leak!r}"
assert lookup_unsafe(conn, "alice") == ["alice"], "Ordinary lookups must still work"
assert lookup_unsafe(conn, "nobody") == [], "An unknown name matches nothing"
'''},
                    {"name": "The parameterised version refuses it", "code": r'''
_blocked = lookup_safe(conn, "' OR '1'='1")
assert _blocked == [], f"The payload is data, not syntax — expected [], got {_blocked!r}"
assert lookup_safe(conn, "alice") == ["alice"], "Ordinary lookups must still work"
'''},
                    {"name": "A quote in a real name breaks only the unsafe path", "code": r'''
try:
    lookup_unsafe(conn, "o'brien")
    assert False, "The unsafe query should be a syntax error for o'brien"
except sqlite3.OperationalError:
    pass
_ok = lookup_safe(conn, "o'brien")
assert _ok == ["o'brien"], f"lookup_safe should find o'brien, got {_ok!r}"
'''},
                    {"name": "escape_html encodes all five characters", "code": r'''
for _raw, _want in [("a & b", "a &amp; b"), ("<b>", "&lt;b&gt;"),
                    ('"x"', "&quot;x&quot;"), ("it's", "it&#x27;s"), ("", "")]:
    _got = escape_html(_raw)
    assert _got == _want, f"escape_html({_raw!r}) gave {_got!r}, expected {_want!r}"
assert escape_html("&lt;") == "&amp;lt;", "Encode & first, or entities get double-encoded"
'''},
                    {"name": "render_comment neutralises a stored payload", "code": r'''
_html = render_comment("mallory", '<script>alert("xss")</script>')
assert _html.startswith('<li class="comment">'), f"Wrong wrapper: {_html!r}"
assert "<script>" not in _html, f"The payload is still live markup: {_html!r}"
assert "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;" in _html, f"Got {_html!r}"
assert _html.endswith("</li>"), f"Wrong wrapper: {_html!r}"
'''},
                    {"name": "The author field cannot open an attribute", "code": r'''
_html = render_comment('mallory" onmouseover="steal()', "hi")
assert 'onmouseover="' not in _html, f"A quote escaped the attribute: {_html!r}"
assert "&quot;" in _html, "The quote should survive as an entity, not vanish"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "read": [
                {
                    "title": "Writing past the end of a buffer, byte by byte",
                    "minutes": 13,
                    "body": r'''
A function in a C program has a local variable — say a 16-byte array to hold a
name someone typed. When the program calls that function, it sets aside a small
region of the stack for it, and the layout of that region is not arbitrary. The
16 bytes for the array come first, at the lower addresses. Just above them sits
the saved frame pointer, and just above *that* sits the saved return address:
the location the CPU will jump back to when this function finishes. That return
address is the interesting byte. If you can change it, you change where the
program goes next.

Nothing here needs real memory to understand. Model the frame as a `bytearray`,
lowest address first, and put a known return address in the top four bytes.

```python
def to_word(value):
    return bytes((value >> (8 * i)) & 0xFF for i in range(4))


def from_word(raw):
    return sum(raw[i] << (8 * i) for i in range(4))


print(to_word(0xCAFEBABE).hex(" "))
print(hex(from_word(bytes.fromhex("be ba fe ca"))))
```

The first line prints `be ba fe ca`, and the second prints `0xcafebabe`. That
reversal is not a mistake. A 32-bit value on a little-endian machine is stored
lowest byte first, so `0xCAFEBABE` — whose lowest byte is `0xBE` — lands in
memory as `be ba fe ca`. This is why exploit write-ups show target addresses
"backwards": they are showing the bytes in memory order, and `to_word` /
`from_word` are the two directions of that convention. Get this pairing right and
the rest follows; get it wrong and every address you write lands scrambled.

## The copy that does not count

Now the vulnerability. A copy routine like C's `strcpy` copies bytes from a
source into the buffer until it hits a terminator. It never consults how big the
destination is. If the source is longer than 16 bytes, the extra bytes do not
stop at the edge of the buffer — they keep writing upward, into the saved frame
pointer, and then into the saved return address. Here is that copy, and an input
built to reach exactly the return-address slot.

```python
WORD = 4


def to_word(value):
    return bytes((value >> (8 * i)) & 0xFF for i in range(WORD))


def from_word(raw):
    return sum(raw[i] << (8 * i) for i in range(WORD))


buffer_size = 16
frame = bytearray(buffer_size + 2 * WORD)
frame[20:24] = to_word(0x08048400)
print(len(frame), "bytes; return address at offset", len(frame) - WORD)
print("before:", hex(from_word(frame[20:24])))

name = b"A" * 20 + to_word(0xCAFEBABE)
for i, byte in enumerate(name):
    frame[i] = byte
print("after: ", hex(from_word(frame[20:24])))
```

It prints `24 bytes; return address at offset 20`, then `before: 0x8048400`, then
`after:  0xcafebabe`. Trace the arithmetic, because every number in it is
load-bearing. The frame is `16 + 8 = 24` bytes: sixteen for the buffer, four for
the saved frame pointer, four for the return address. The return address
therefore begins at offset 20 (`24 - 4`). The malicious input is 20 filler bytes
— enough to fill the buffer *and* the saved frame pointer — followed by the
four-byte little-endian encoding of the address you want. The copy walks from
offset 0 with no check, so byte 20 of the input lands at offset 20 of the frame,
directly on top of the saved return address, and the program will now "return" to
`0xCAFEBABE`. That is a control-flow hijack, built out of nothing but a copy that
forgot to count.

The natural first version of that copy is the mistake this module is about: to
copy the whole input and only afterwards notice you have run off the end. If the
input is longer than the whole frame, the write at offset 24 is already out of
bounds:

```python
# raises IndexError
frame = bytearray(24)
data = b"A" * 25
for i, byte in enumerate(data):
    frame[i] = byte
```

It raises `IndexError`. The tempting bug in the lab's `unsafe_strcpy` is to
assign first and check second — to write `frame[i] = byte` and let the bytearray
raise on its own. That works, but it raises only *after* the illegal write has
been attempted, and it raises the interpreter's message rather than yours. The
routine is supposed to model "no bounds check at all, until the process
segfaults," so the check `if i >= len(frame): raise IndexError(...)` has to come
*before* the write, so that every byte up to the very last legal one is stored
and the fault is reported at the exact boundary. People reach for the
after-the-fact version because it is shorter, and it hides where the frame
actually ends.

## Catching it two ways

Defences split into detection and prevention, and it is worth being clear which
is which. A stack canary is detection. Place a known four-byte value between the
buffer and the saved registers; before the function returns, check it is still
that value. A contiguous overflow that reaches the return address must have
written through the canary slot to get there, so a corrupted canary is proof the
frame was smashed — after the fact, but before the poisoned return address is
used.

```python
WORD = 4
CANARY = 0x5A6B7C8D


def to_word(value):
    return bytes((value >> (8 * i)) & 0xFF for i in range(WORD))


def from_word(raw):
    return sum(raw[i] << (8 * i) for i in range(WORD))


frame = bytearray(16 + WORD + 2 * WORD)
frame[16:20] = to_word(CANARY)
frame[24:28] = to_word(0x08048400)

payload = b"A" * 24 + to_word(0xCAFEBABE)
frame[0:len(payload)] = payload
print("return address:", hex(from_word(frame[24:28])))
print("canary intact:", from_word(frame[16:20]) == CANARY)
```

It prints `return address: 0xcafebabe` and `canary intact: False`. The hijack
still succeeded — the canary does not prevent the overwrite — but the corrupted
canary means the program can detect the smash and abort before it ever executes
the attacker's return address. Note that adding the canary changed the layout: the
frame is now 28 bytes and the return address moved to offset 24, so the filler is
24 bytes, not 20. The offset is not a constant to memorise; it is
`len(frame) - WORD`, computed from whatever layout the frame actually has.

Prevention is a copy that refuses to overrun in the first place. There are two
honest versions, and they differ in what they do with data that will not fit.

```python
def safe_strncpy(frame, data, buffer_size):
    n = min(len(data), buffer_size)
    frame[0:n] = data[0:n]
    return n


def checked_copy(frame, data, buffer_size):
    if len(data) > buffer_size:
        raise BufferError(f"{len(data)} bytes into a {buffer_size}-byte buffer")
    frame[0:len(data)] = data
    return len(data)


frame = bytearray(24)
print(safe_strncpy(frame, b"A" * 40, 16), "bytes kept of 40")
try:
    checked_copy(frame, b"A" * 40, 16)
except BufferError as err:
    print("refused:", err)
```

It prints `16 bytes kept of 40` and `refused: 40 bytes into a 16-byte buffer`.
`safe_strncpy` truncates: it keeps the first 16 bytes and silently drops the
rest, which stops the overflow but loses data, and a truncated name or path can
be its own bug. `checked_copy` refuses: it raises rather than store a partial
value. Neither ever touches the return address, which is the whole point.

## Where the model is only a model

This is a faithful picture of a classic stack overflow and a deliberately small
one. Real systems layer on defences this simulation does not draw: non-executable
stacks (NX) mean a return address pointing into your input runs nothing, so modern
exploits chain together existing code fragments instead; address-space layout
randomisation (ASLR) means you do not know the address to jump to without first
leaking it. And real canaries are random per run, so they cannot be guessed and
written back — the fixed `CANARY` here is a constant only so the arithmetic stays
legible. The mechanism you are modelling is real and still worth understanding;
the ease of it here is a teaching convenience, not the state of the art.

That mechanism is exactly what the lab, **Smashing a simulated stack frame**,
asks you to build: `to_word` and `from_word`, a `StackFrame` whose
`return_offset` is computed from its own layout, an `unsafe_strcpy` that faults at
the boundary rather than after it, the two disciplined copies, and an
`exploit_payload` that rewrites the saved return address on a plain frame and
trips the canary on a protected one.
'''
                }
            ],
            "quiz": {
                "title": "Frames, offsets, and the copy that forgot to count",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A frame is `bytearray(buffer_size + 2 * WORD)` with `WORD = 4` and `buffer_size = 16`, and the saved return address is the top word. At what byte offset does that return address begin?",
                        "opts": [
                            "16 — it sits directly above the buffer, at the first byte past it",
                            "20 — the frame is 24 bytes, and the last word starts at 24 minus 4",
                            "24 — the return address occupies the four bytes ending the frame, so it starts there",
                            "8 — the two saved words are 8 bytes, and the offset counts down from the top",
                        ],
                        "a": 1,
                        "whys": [
                            r"Offset 16 is where the saved frame pointer begins, not the return address. The return address is the *second* saved word, another four bytes higher up.",
                            r"Right: the frame is `16 + 8 = 24` bytes and the last four hold the return address, so it begins at `24 - 4 = 20` — which is exactly `len(frame) - WORD`.",
                            r"Offset 24 is the length of the frame, one past its final byte. Start writing there and you are already out of bounds; the four-byte return word *ends* at 24 and starts at 20.",
                            r"There is no counting down; a bytearray is indexed from 0 upward. The saved frame pointer is at 16 and the return address at 20, both measured from the low end.",
                        ],
                        "why": r'''
The frame is `16 + 2 * 4 = 24` bytes: sixteen of buffer, then the saved frame
pointer, then the saved return address. The return address is the last word, so
it begins at `len(frame) - WORD = 24 - 4 = 20`. Offset 16 is the frame pointer;
offset 24 is one past the end. Computing the offset from the length is what keeps
it correct when a canary later changes the layout.
''',
                    },
                    {
                        "q": "To make `unsafe_strcpy` raise exactly when a write would run off the end of the frame, where must the bounds check go?",
                        "opts": [
                            "After the assignment, catching the bytearray's own IndexError and re-raising it with a clearer message",
                            "Before the assignment, so the byte at the boundary is never written and the fault names the exact edge",
                            "Once at the start, comparing the whole input length against the frame before copying anything",
                            "Nowhere — a bounds check would make it a safe copy, defeating the point of the routine",
                        ],
                        "a": 1,
                        "whys": [
                            r"Assigning first lets the illegal write be attempted before anything stops it, and it reports the interpreter's message rather than the frame's real edge. The routine models 'no check until the fault', which means the check precedes the write.",
                            r"Right: checking `i >= len(frame)` before writing stores every legal byte up to the last one and faults precisely at the boundary, which is how a real overrun behaves — bytes land until the illegal address is reached.",
                            r"A single up-front length check would refuse a partial copy, but the routine is meant to write as far as it legally can and only then fault — that is what makes it a model of an unchecked copy, not a guarded one.",
                            r"The routine still needs to stop at the frame's physical end, or the simulation would let a Python bytearray raise on its own at an unpredictable spot. The check models the segfault boundary, not a safe-copy guard.",
                        ],
                        "why": r'''
`unsafe_strcpy` models a copy with no destination-size check that nonetheless
faults when the process runs off its memory. Checking `i >= len(frame)` before
each write stores every legal byte and reports the fault at the exact boundary,
with the routine's own message. Assigning first and catching the bytearray's
IndexError attempts the illegal write before stopping it and hides where the frame
truly ends.
''',
                    },
                    {
                        "q": "On a plain 24-byte frame the exploit payload is 20 filler bytes plus the target address. On an otherwise identical frame with a canary added, what changes?",
                        "opts": [
                            "Nothing changes — the filler is always exactly 20 bytes, because the buffer size itself did not change when the canary was added",
                            "The filler grows to 24 bytes, because the canary word sits between the buffer and the saved return address",
                            "The filler shrinks, because the canary occupies space the payload would otherwise need to fill",
                            "The target address must be written twice, once before and once after the canary slot",
                        ],
                        "a": 1,
                        "whys": [
                            r"The buffer is still 16 bytes, but the payload fills everything up to the return address, and the canary added four bytes between them. Treating 20 as fixed writes the address into the frame pointer instead.",
                            r"Right: the canary is a whole extra word below the saved registers, so the frame is 28 bytes and the return address moves to offset 24 — the filler is now `len(frame) - WORD = 24` bytes.",
                            r"Adding a word makes the frame larger, not the payload smaller. The filler must cover the buffer, the canary and the saved frame pointer before the address, so it grows.",
                            r"The address is written once, at the return-address slot. The canary is passed through as filler like everything below the target; it is not a value the attacker writes twice.",
                        ],
                        "why": r'''
The filler is always `return_offset` bytes — `len(frame) - WORD` — not a
memorised 20. Adding a canary inserts a four-byte word between the buffer and the
saved registers, so the frame becomes 28 bytes and the return address moves to
offset 24. The payload is then 24 filler bytes plus the target address, and those
24 include the bytes that run through the canary slot.
''',
                    },
                    {
                        "q": "The canary-protected frame is overflowed by the exploit payload. `read_return_address()` returns the attacker's address and `canary_intact()` returns False. What does that pair of results mean the canary provides?",
                        "opts": [
                            "It prevented the overwrite, so the returned address is stale and the program is safe",
                            "It detected the overwrite after the fact, so the program can abort before using the poisoned return address",
                            "It corrected the overwrite, quietly restoring the frame's original saved return address the moment the corruption was first found",
                            "It slowed the copy enough that the overflow stopped short of the return address",
                        ],
                        "a": 1,
                        "whys": [
                            r"The return address was overwritten — that is what `read_return_address()` returning the attacker's value shows. A canary never blocks the write; it is a tripwire, not a wall.",
                            r"Right: a contiguous overflow reaching the return address must pass through the canary slot, so a changed canary is proof of a smash. The overwrite happened, but it can be caught before the bad address is ever executed.",
                            r"Nothing restores the old address; `read_return_address()` still returns the attacker's. The canary reports corruption, it does not repair it.",
                            r"Copy speed is irrelevant to a simulation, and the overflow plainly did reach the return address. The canary detects the reach; it does not shorten it.",
                        ],
                        "why": r'''
A stack canary is detection, not prevention. The overwrite succeeds — the return
address holds the attacker's value — but a contiguous overflow that reached it had
to write through the canary slot, so a corrupted canary proves the frame was
smashed. The program can check the canary before returning and abort, which stops
the poisoned address from ever being used.
''',
                    },
                    {
                        "q": "Given 40 bytes of input and a 16-byte buffer, `safe_strncpy` keeps 16 and returns 16, while `checked_copy` raises BufferError. When is the truncating version the more dangerous choice?",
                        "opts": [
                            "Never — truncation always fails safe, so silently keeping just the first 16 bytes of the input is strictly better than ever raising",
                            "When the dropped bytes carried meaning, so a silently shortened name or path becomes a different, wrong value",
                            "When the buffer is larger than the input, because then truncation corrupts the trailing bytes",
                            "When a canary is present, because truncation writes through the canary slot on its way",
                        ],
                        "a": 1,
                        "whys": [
                            r"Both stop the overflow, so both fail safe against memory corruption — but truncation trades that for a data bug. Silently keeping a prefix is not strictly better; it can produce a valid-looking wrong value.",
                            r"Right: truncation stops the overrun but discards whatever did not fit, so a path or identifier can be silently shortened into a different, still-usable value — a correctness bug the raising version turns into a loud failure instead.",
                            r"When the input is shorter than the buffer, nothing is truncated at all — `min(len(data), buffer_size)` copies the whole input and leaves the rest untouched. Truncation only bites when the input is longer.",
                            r"Neither copy exceeds the buffer, so neither reaches the canary slot; that is exactly what makes them safe. Truncation's risk is lost data, not a tripped canary.",
                        ],
                        "why": r'''
Both copies stop the overflow, so both are safe against memory corruption. The
difference is what happens to the excess. `safe_strncpy` drops it silently, which
can turn a long path or identifier into a shorter, valid-looking, wrong value — a
correctness bug that surfaces far from the copy. `checked_copy` refuses instead,
turning the same condition into an immediate, visible failure.
''',
                    },
                ],
            },
            "title": "Memory safety, simulated",
            "summary": "A stack frame as a bytearray, and what an unchecked copy does to it.",
            "concepts": [
                "Frame layout: local buffer, then saved frame pointer, then saved return address",
                "`strcpy` copies until a terminator; the destination size is never consulted",
                "Little-endian word encoding, and why payload addresses look byte-reversed",
                "Control-flow hijack: the corrupted saved return address is loaded by `ret`",
                "Stack canaries detect corruption between the buffer and the saved registers",
                "Detection (canary, ASLR, NX) versus prevention (bounds-checked copies)",
                "Truncating (`strncpy`) silently loses data; refusing (`BufferError`) does not",
            ],
            "lab": {
                "title": "Smashing a simulated stack frame",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
No real memory is harmed. A frame is a `bytearray` laid out low address first:

```text
without a canary            with a canary
[ buffer  N bytes ]         [ buffer  N bytes ]
[ saved fp  4     ]         [ canary    4     ]
[ return addr 4   ]         [ saved fp  4     ]
                            [ return addr 4   ]
```

Implement `to_word` / `from_word` (32-bit **little-endian**) and the
`StackFrame` class.

- `StackFrame(buffer_size=16, return_address=DEFAULT_RETURN, canary=False)`
  allocates the memory, writes `CANARY` into the canary slot when asked, and
  writes `return_address` into the final word.
- `return_offset` — the byte index where the saved return address begins.
- `read_return_address()` — decode that word.
- `canary_intact()` — `True` when the canary slot still holds `CANARY`
  (and always `True` for a frame that has no canary).
- `unsafe_strcpy(data)` — copy byte by byte from offset 0 with **no** length
  check, and raise `IndexError` on the first write past the end of the whole
  frame. Returns the number of bytes requested.
- `safe_strncpy(data)` — copy at most `buffer_size` bytes; returns how many.
- `checked_copy(data)` — raise `BufferError` when `len(data) > buffer_size`,
  otherwise copy. Returns how many.

Then write `exploit_payload(frame, new_return)`: filler bytes (`b"A"`) up to
`return_offset`, followed by `new_return` as a little-endian word. Feeding it
to `unsafe_strcpy` must make `read_return_address()` return `new_return` —
and, on a canary frame, must leave `canary_intact()` `False`.
''',
                "files": [{"name": "main.py", "content": r'''
WORD = 4
CANARY = 0x5A6B7C8D
DEFAULT_RETURN = 0x08048400


def to_word(value):
    """32-bit little-endian bytes."""
    # your code here


def from_word(raw):
    """Four little-endian bytes back to an int."""
    # your code here


class StackFrame:
    """A simulated frame: buffer, optional canary, saved fp, saved return address."""

    def __init__(self, buffer_size=16, return_address=DEFAULT_RETURN, canary=False):
        self.buffer_size = buffer_size
        self.has_canary = canary
        self.memory = bytearray(buffer_size + (WORD if canary else 0) + 2 * WORD)
        # write the canary (when present) and the saved return address

    @property
    def return_offset(self):
        """Index of the first byte of the saved return address."""
        # your code here

    def read_return_address(self):
        # your code here

    def canary_intact(self):
        # your code here

    def unsafe_strcpy(self, data):
        """Copy with no bounds check. IndexError past the end of the frame."""
        # your code here

    def safe_strncpy(self, data):
        """Copy at most buffer_size bytes; return how many were copied."""
        # your code here

    def checked_copy(self, data):
        """Refuse over-long data with BufferError, otherwise copy."""
        # your code here


def exploit_payload(frame, new_return):
    """Filler up to the saved return address, then new_return little-endian."""
    # your code here


frame = StackFrame(16)
print(frame.memory)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
WORD = 4
CANARY = 0x5A6B7C8D
DEFAULT_RETURN = 0x08048400


def to_word(value):
    """32-bit little-endian bytes."""
    return bytes((value >> (8 * i)) & 0xFF for i in range(WORD))


def from_word(raw):
    """Four little-endian bytes back to an int."""
    return sum(raw[i] << (8 * i) for i in range(WORD))


class StackFrame:
    """A simulated frame: buffer, optional canary, saved fp, saved return address."""

    def __init__(self, buffer_size=16, return_address=DEFAULT_RETURN, canary=False):
        self.buffer_size = buffer_size
        self.has_canary = canary
        self.memory = bytearray(buffer_size + (WORD if canary else 0) + 2 * WORD)
        if canary:
            self.memory[buffer_size:buffer_size + WORD] = to_word(CANARY)
        self.memory[len(self.memory) - WORD:] = to_word(return_address)

    @property
    def return_offset(self):
        """Index of the first byte of the saved return address."""
        return len(self.memory) - WORD

    def read_return_address(self):
        return from_word(self.memory[self.return_offset:self.return_offset + WORD])

    def canary_intact(self):
        if not self.has_canary:
            return True
        start = self.buffer_size
        return from_word(self.memory[start:start + WORD]) == CANARY

    def unsafe_strcpy(self, data):
        """Copy with no bounds check. IndexError past the end of the frame."""
        for i, byte in enumerate(data):
            if i >= len(self.memory):
                raise IndexError("write past the end of the frame")
            self.memory[i] = byte
        return len(data)

    def safe_strncpy(self, data):
        """Copy at most buffer_size bytes; return how many were copied."""
        n = min(len(data), self.buffer_size)
        self.memory[0:n] = bytes(data[0:n])
        return n

    def checked_copy(self, data):
        """Refuse over-long data with BufferError, otherwise copy."""
        if len(data) > self.buffer_size:
            raise BufferError(
                f"{len(data)} bytes into a {self.buffer_size}-byte buffer")
        self.memory[0:len(data)] = bytes(data)
        return len(data)


def exploit_payload(frame, new_return):
    """Filler up to the saved return address, then new_return little-endian."""
    return b"A" * frame.return_offset + to_word(new_return)


frame = StackFrame(16)
print(frame.memory)
print(hex(frame.read_return_address()))
frame.unsafe_strcpy(exploit_payload(frame, 0xCAFEBABE))
print(hex(frame.read_return_address()))
'''}],
                "hints": [
                    "Little-endian means the lowest byte comes first: `(value >> 0) & 0xFF`, then `>> 8`, then `>> 16`, then `>> 24`.",
                    "The frame length is `buffer_size + (4 if canary else 0) + 8`; the return address is the last four bytes, so `return_offset` is `len(self.memory) - WORD`.",
                    "In `unsafe_strcpy`, check `i >= len(self.memory)` *before* the write — a bytearray would happily raise on assignment, but you want your own message.",
                    "`exploit_payload` is exactly `return_offset` filler bytes plus one word, so its length always equals `len(frame.memory)`.",
                ],
                "tests": [
                    {"name": "Word encoding is little-endian", "code": r'''
assert to_word(0xCAFEBABE) == b"\xbe\xba\xfe\xca", f"to_word(0xCAFEBABE) gave {to_word(0xCAFEBABE)!r}"
assert to_word(0) == b"\x00\x00\x00\x00", f"to_word(0) gave {to_word(0)!r}"
assert from_word(b"\x01\x00\x00\x00") == 1, f"from_word gave {from_word(b'\x01\x00\x00\x00')!r}"
for _v in (0, 1, 0x08048400, 0xCAFEBABE, 0xFFFFFFFF):
    assert from_word(to_word(_v)) == _v, f"round trip failed for {_v:#x}"
'''},
                    {"name": "Frame layout and initial contents", "code": r'''
_f = StackFrame(16)
assert len(_f.memory) == 24, f"A 16-byte buffer with no canary needs 24 bytes, got {len(_f.memory)}"
assert _f.return_offset == 20, f"return_offset is {_f.return_offset}, expected 20"
assert _f.read_return_address() == DEFAULT_RETURN, \
    f"read_return_address gave {_f.read_return_address():#x}, expected {DEFAULT_RETURN:#x}"
assert _f.canary_intact() is True, "A frame without a canary reports intact"
_c = StackFrame(16, canary=True)
assert len(_c.memory) == 28, f"With a canary the frame is 28 bytes, got {len(_c.memory)}"
assert _c.return_offset == 24, f"return_offset is {_c.return_offset}, expected 24"
assert _c.canary_intact() is True, "A fresh canary should read back as CANARY"
'''},
                    {"name": "A copy that fits changes nothing above the buffer", "code": r'''
_f = StackFrame(16, canary=True)
assert _f.checked_copy(b"hello") == 5, "checked_copy returns the byte count"
assert _f.read_return_address() == DEFAULT_RETURN, "A short copy must not reach the return address"
assert _f.canary_intact(), "A short copy must not touch the canary"
assert _f.memory[0:5] == b"hello", f"Buffer holds {bytes(_f.memory[0:5])!r}"
assert _f.checked_copy(b"") == 0, "An empty copy is legal and writes nothing"
assert _f.checked_copy(b"A" * 16) == 16, "Exactly buffer_size bytes still fits"
assert _f.canary_intact(), "Filling the buffer exactly must not disturb the canary"
'''},
                    {"name": "The payload rewrites the saved return address", "code": r'''
_f = StackFrame(16)
_p = exploit_payload(_f, 0xCAFEBABE)
assert len(_p) == 24, f"Payload for a 24-byte frame should be 24 bytes, got {len(_p)}"
assert _p[:20] == b"A" * 20, f"Filler is wrong: {_p[:20]!r}"
assert _f.unsafe_strcpy(_p) == 24, "unsafe_strcpy returns how many bytes were asked for"
assert _f.read_return_address() == 0xCAFEBABE, \
    f"return address is {_f.read_return_address():#x}, expected 0xcafebabe"
'''},
                    {"name": "Running off the end of the frame raises", "code": r'''
_f = StackFrame(16)
try:
    _f.unsafe_strcpy(b"A" * 25)
    assert False, "25 bytes into a 24-byte frame should raise IndexError"
except IndexError:
    pass
assert _f.memory[23] == 0x41, "The bytes before the fault were still written"
assert _f.unsafe_strcpy(b"") == 0, "An empty copy writes nothing and must not raise"
'''},
                    {"name": "The two defensive copies behave differently", "code": r'''
_f = StackFrame(16)
try:
    _f.checked_copy(b"A" * 17)
    assert False, "17 bytes into a 16-byte buffer should raise BufferError"
except BufferError:
    pass
assert _f.read_return_address() == DEFAULT_RETURN, "A refused copy must leave the frame alone"
_g = StackFrame(16)
assert _g.safe_strncpy(b"A" * 40) == 16, "safe_strncpy truncates to buffer_size"
assert _g.read_return_address() == DEFAULT_RETURN, "Truncation must not reach the return address"
assert bytes(_g.memory[0:16]) == b"A" * 16, "The buffer should be full"
'''},
                    {"name": "The canary catches what the copy did not", "code": r'''
_c = StackFrame(16, return_address=DEFAULT_RETURN, canary=True)
_p = exploit_payload(_c, 0xCAFEBABE)
assert len(_p) == 28, f"Canary frames need a 28-byte payload, got {len(_p)}"
_c.unsafe_strcpy(_p)
assert _c.read_return_address() == 0xCAFEBABE, "The hijack still succeeds..."
assert _c.canary_intact() is False, "...but the canary must now report corruption"
_clean = StackFrame(16, canary=True)
_clean.safe_strncpy(b"B" * 99)
assert _clean.canary_intact() is True, "A bounds-respecting copy leaves the canary alone"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "read": [
                {
                    "title": "What a password is worth, in seconds",
                    "minutes": 13,
                    "body": r'''
Someone has stolen your database. Not the passwords — you hashed those — but the
hashes, and now they are working offline on their own hardware, with no login
screen to slow them down and no one watching. The only question that matters is
how long your policy makes them wait. That question has a number, and the number
is smaller than intuition suggests.

Start with the size of the problem. A password policy that allows lowercase
letters and digits, six characters long, draws each character from an alphabet of
`26 + 10 = 36` symbols. The number of distinct passwords is the alphabet size
raised to the length: every one of the six positions independently chooses from 36
options, so the count multiplies out as `36 * 36 * 36 * 36 * 36 * 36`, which is
`36 ** 6`. That product is the *keyspace*, and its size is where all the security
lives.

```python
import math

alphabet = 26 + 10
length = 6
keyspace = alphabet ** length
print(keyspace)
print(round(length * math.log2(alphabet), 2), "bits")
rate = 1e9
print(keyspace / 2 / rate, "seconds on average")
print(keyspace / 2 / (rate / 2 ** 12), "seconds with a work factor of 12")
```

It prints `2176782336`, then `31.02 bits`, then `1.088391168 seconds on average`,
then `4458.050224128 seconds with a work factor of 12`. Walk through where each
number comes from, because the whole cost model is in these four lines.

## Entropy is the log of the keyspace

The keyspace, 2,176,782,336, is about 2.2 billion. That is a large number written
one way and an unremarkable one written another. The second way is *entropy in
bits*: `length * log2(alphabet)`, which is `6 * log2(36) ≈ 31.02`. A password from
this policy is worth about 31 bits, meaning the keyspace is roughly `2 ** 31`.
Bits are the useful unit because they add: doubling the length adds another 31
bits rather than multiplying a huge number, and comparing two policies is
comparing two small numbers. Widen the alphabet and each character is worth more
bits; lengthen the password and you get more characters at that rate. The reason
length usually wins is that it is the exponent — every extra character multiplies
the whole keyspace, while a bigger alphabet only raises the base.

## Half the keyspace, and the rate

Now the attacker. They try candidates one at a time. On average — over many
different stolen passwords — they find each one after searching half the
keyspace, not all of it, because the target is equally likely to be anywhere in
the list and the expected position is the middle. So the work is
`keyspace / 2` guesses. Divide by how many guesses per second their hardware
manages, and you have seconds. At a billion guesses a second, that is
`2176782336 / 2 / 1e9 ≈ 1.09` seconds. Roughly one second to crack a
six-character lowercase-and-digits password. That is the number people find hard
to believe, and it is why this policy is not a policy.

The defence that changes it is the *work factor*, and it is the reason a password
hash is not a plain SHA-256. A password hashing function like bcrypt or scrypt is
deliberately slow, tunable by a work factor: raising it by one doubles the time to
compute a single hash. If the attacker's raw hardware does a billion plain hashes
a second, a work factor of 12 divides that by `2 ** 12 = 4096`, down to about
244,000 password-guesses a second. The same crack now takes
`2176782336 / 2 / (1e9 / 4096) ≈ 4458` seconds — from one second to about
seventy-four minutes, from one line of the policy that costs the defender nothing
to type. That is the lever the lab's `average_crack_seconds` exposes: the work
factor is subtracted from the attacker's rate, `hashes_per_second / 2 ** work_factor`,
and everything downstream scales with it.

## The mistake: reading the average as a guarantee

Here is the trap. "Seventy-four minutes on average" is not "safe for seventy-four
minutes." The average is over a population of passwords; any single one can fall
in the first second of searching if the attacker happens to try it early, and
attackers do not search randomly — they try the common passwords first. The
number is an order-of-magnitude estimate for planning, not a promise for any one
account. It is tempting to quote it as a floor because it is a concrete figure and
concrete figures feel like guarantees, but the honest reading is "this is roughly
the scale of effort, halved and averaged." Treat a comfortable-looking average as
protection for a specific user and you will be wrong about the user whose password
was guessed third.

## Online guessing is a different problem

Everything above assumes an offline attack: the attacker has the hashes and their
own hardware. An *online* attacker has neither — they must submit each guess
through your login endpoint, which means you control the rate. Here entropy almost
stops mattering. A million-to-one password is fine against ten guesses; a
thousand-to-one password is fine too. What you need is to make the eleventh guess
expensive, and the tool is exponential backoff.

```python
def delay_for(failures, base_delay=1.0, max_delay=300.0, threshold=3):
    if failures < threshold:
        return 0.0
    return min(base_delay * 2 ** (failures - threshold), max_delay)


print([delay_for(n) for n in range(1, 13)])
print(sum(delay_for(n) for n in range(1, 101)) / 3600, "hours for 100 guesses")
```

It prints
`[0.0, 0.0, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0, 300.0]` and then
about `7.56 hours for 100 guesses`. The first two failures are free, so a user who
fat-fingers their password twice notices nothing. From the third failure the delay
doubles each time — 1, 2, 4, 8 seconds — until it hits the cap of 300 seconds, so
it grows without ever locking the account forever. A hundred guesses that would
take a fraction of a second offline now take over seven hours, and a real attacker
guessing thousands of accounts finds each one individually throttled. The cap
matters: without it the delay would grow unbounded and a mistyped password could
lock someone out for a day. And a success must reset the counter to zero, or the
backoff from an attacker's failures would punish the legitimate user when they
finally log in.

## The second factor, RFC by RFC

A password is one factor. A time-based one-time password (TOTP) — the six digits
an authenticator app shows — is a second, and it is a small, exact construction
rather than magic. HOTP (RFC 4226) turns a shared secret and a counter into a
code: take HMAC-SHA1 of the counter, read one byte to pick an offset, extract four
bytes there, mask off the top bit, and reduce modulo `10 ** digits`.

```python
import hashlib
import hmac

secret = b"12345678901234567890"
counter = 0
digest = hmac.new(secret, counter.to_bytes(8, "big"), hashlib.sha1).digest()
print(digest.hex())
offset = digest[19] & 0x0F
print("offset", offset)
chunk = int.from_bytes(digest[offset:offset + 4], "big") & 0x7FFFFFFF
print(chunk)
print(str(chunk % 10 ** 6).zfill(6))
```

For the RFC's own test secret and counter 0 this prints the digest, then
`offset 0`, then `1284755224`, then `755224` — the first vector in the standard,
reproduced exactly. The `& 0x7FFFFFFF` masks the top bit so the four-byte value is
never negative regardless of platform; the `.zfill(6)` restores leading zeros that
the modulo throws away, which is the mistake the code is written to avoid — a code
of `081804` is not the integer `81804`, and dropping the zero fails verification
for one code in ten.

TOTP (RFC 6238) is HOTP with the counter set to the clock: `timestamp // step`,
where the step is usually 30 seconds. Because the client's clock and yours drift,
verification checks a small window of counters either side of now.

```python
import hashlib
import hmac


def hotp(secret, counter, digits=6):
    digest = hmac.new(secret, counter.to_bytes(8, "big"), hashlib.sha1).digest()
    offset = digest[19] & 0x0F
    truncated = int.from_bytes(digest[offset:offset + 4], "big") & 0x7FFFFFFF
    return str(truncated % 10 ** digits).zfill(digits)


def verify_totp(secret, code, timestamp, step=30, digits=6, window=1):
    counter = timestamp // step
    for drift in range(-window, window + 1):
        if counter + drift < 0:
            continue
        if hmac.compare_digest(hotp(secret, counter + drift, digits), str(code)):
            return True
    return False


secret = b"12345678901234567890"
print(59 // 30, hotp(secret, 59 // 30, 8))
code = hotp(secret, 1111111109 // 30, 8)
print(1111111109 // 30, code)
for late in (0, 30, 60):
    print(late, "seconds late:", verify_totp(secret, code, 1111111109 + late, digits=8))
```

It prints `1 94287082`, then `37037036 07081804`, then that the code verifies at 0
and 30 seconds late but not at 60. With `window=1` a code from the previous or next
30-second step still passes, absorbing about a minute of clock skew; two steps out,
it fails. The comparison uses `hmac.compare_digest`, not `==`, so that a
network attacker cannot learn the correct code digit by digit from how long the
comparison takes — a timing side channel that string equality would leak.

## Where this stops

The window is the honest limit. Widen it and you tolerate more clock drift but you
also give an attacker more valid codes to guess at once — a window of ten is ten
times easier to brute-force. And none of this survives a stolen secret: TOTP
proves possession of the shared key, so a phished code entered by the attacker
within the window, or a secret leaked from your own store, defeats it entirely.
The second factor raises the cost of impersonation; it does not make it
impossible.

The lab, **Cracking cost, backoff and TOTP**, is these three defences made
measurable: `keyspace`, `entropy_bits` and `average_crack_seconds` for the cost
model, `LoginThrottle` for the backoff, and `hotp` / `totp` / `verify_totp`
checked against the RFC 4226 and RFC 6238 test vectors printed above.
'''
                }
            ],
            "quiz": {
                "title": "Cost, backoff, and one-time codes",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A policy allows lowercase and digits, six characters. Its keyspace is `36 ** 6`. Why does `average_crack_seconds` divide that by two before dividing by the guess rate?",
                        "opts": [
                            "Half the passwords the policy could generate are rejected afterwards as too weak, so in practice only half of the whole keyspace is ever reachable",
                            "The attacker finds a given password after searching half the space on average, since it is equally likely to sit anywhere",
                            "Two guesses can be checked per hash, so the effective work is half the keyspace",
                            "The factor of two accounts for the birthday bound, where collisions halve the search",
                        ],
                        "a": 1,
                        "whys": [
                            r"The policy defines the whole keyspace; every one of the `36 ** 6` strings it allows is a valid password. Nothing is pre-rejected, so the halving is not about reachability.",
                            r"Right: the target is equally likely to be anywhere in the enumerated list, so its expected position is the middle — half the keyspace of guesses before a hit, on average.",
                            r"One hash checks one candidate; there is no two-for-one. The factor of two comes from the *average* search position, not from the cost of a single guess.",
                            r"Birthday collisions are about finding any two inputs that hash alike, which is not this attack. Here the attacker enumerates candidates for one known target, and the average hit is at the midpoint.",
                        ],
                        "why": r'''
The attacker enumerates candidates against one known hash. Averaged over many
targets, the sought password is equally likely to sit at any position in the list,
so its expected position is the middle — half the keyspace of guesses. That is why
the model uses `keyspace / 2`. It is a statement about the average search depth,
not about the policy rejecting anything or a hash checking two candidates.
''',
                    },
                    {
                        "q": "The six-character lowercase-and-digits policy cracks in about a second at a billion hashes a second. Adding a bcrypt work factor of 12 raises that to about 74 minutes. Where in the model does the work factor act?",
                        "opts": [
                            "It multiplies the keyspace by 4096, so there are far more candidates to try",
                            "It divides the attacker's guess rate by 4096, because each hash now costs 2**12 times as much to compute",
                            "It adds a further 12 bits of entropy to every password the policy allows, which lengthens the effective offline search the attacker has to run",
                            "It caps the attacker at 4096 guesses before the account locks",
                        ],
                        "a": 1,
                        "whys": [
                            r"The keyspace depends only on the alphabet and length, both unchanged. The work factor does not add candidates; it makes each candidate slower to test.",
                            r"Right: a work factor of 12 makes one hash cost `2 ** 12 = 4096` times as much, so the effective rate is `hashes_per_second / 4096` and the same search takes 4096 times longer.",
                            r"Entropy is a property of the policy — alphabet and length — and the work factor changes neither. It slows the attacker per guess rather than enlarging the space.",
                            r"Account lockout is online-guessing backoff, a different defence entirely. An offline attacker has the hashes and no login screen; the work factor slows their hashing, it does not lock anything.",
                        ],
                        "why": r'''
The work factor makes the password hash deliberately slow: raising it by one
doubles the cost of computing a single hash, so a factor of 12 divides the
attacker's effective rate by `2 ** 12 = 4096`. The keyspace and the password's
entropy are untouched — the same number of candidates, each now 4096 times slower
to test — which turns a one-second crack into about 74 minutes.
''',
                    },
                    {
                        "q": "With `base_delay=1`, `threshold=3`, `max_delay=300`, the delays for failures 1..12 are `[0, 0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 300]`. Why is the cap of 300 seconds a deliberate design choice rather than a limitation?",
                        "opts": [
                            "Without a cap the delay would keep doubling, so a mistyped password could lock a real user out for hours or days",
                            "The cap is simply where the doubling sequence naturally stops on its own, since 300 is the largest power of two that still fits under an hour",
                            "Beyond 300 seconds the exponential overflows the float, so the cap prevents a crash",
                            "The cap resets the failure counter to zero, giving the user a fresh start",
                        ],
                        "a": 0,
                        "whys": [
                            r"Right: uncapped, the delay doubles without bound, so a legitimate user who kept failing — or an attacker's failures charged to their account — could face a lockout of hours. The cap keeps the throttle punishing but never permanent.",
                            r"300 is not a power of two at all — the doubling passes through 256 and would reach 512 next. The cap is a chosen ceiling, not where the sequence naturally halts.",
                            r"A float handles far larger exponentials than this without overflowing; `2 ** 40` is nothing to it. The cap is about human lockout time, not numeric limits.",
                            r"The cap only bounds the delay's size; it does not touch the counter. Resetting the counter is what a *success* does, which is a separate mechanism.",
                        ],
                        "why": r'''
The delay doubles from the threshold on, and without a ceiling it would grow
unbounded — the twentieth failure would demand hours. Capping it at 300 seconds
keeps every further attempt expensive for an attacker while ensuring a legitimate
user who mistypes repeatedly is never locked out for longer than five minutes. The
cap bounds the delay; a success, separately, resets the counter.
''',
                    },
                    {
                        "q": "`hotp` computes an integer, reduces it modulo `10 ** digits`, and then calls `.zfill(digits)` before returning a string. What breaks if the `.zfill` is omitted and the code is returned as the raw integer?",
                        "opts": [
                            "Nothing — a numeric code and its zero-padded string compare equal after conversion",
                            "Codes that happen to begin with a zero lose it, so about one code in ten fails to match the authenticator's six digits",
                            "The modulo would overflow without a string to hold the extra digit",
                            "The HMAC digest would have to be recomputed from scratch, since returning the integer form rather than a string changes the dynamic-truncation offset byte",
                        ],
                        "a": 1,
                        "whys": [
                            r"They do not compare equal as strings: `081804` and `81804` differ in length and leading character. The authenticator shows six characters, and a five-character integer will not match it.",
                            r"Right: the modulo discards a leading zero — `081804` becomes the integer `81804` — so roughly one code in ten arrives a digit short and fails verification against the app's six-digit display.",
                            r"The modulo `10 ** digits` guarantees the value fits in `digits` places; nothing overflows. The problem is presentation — a dropped leading zero — not size.",
                            r"The offset byte comes from the digest and is fixed before truncation; the final formatting cannot reach back and change it. Only the displayed code is affected.",
                        ],
                        "why": r'''
Reducing modulo `10 ** digits` yields a number that may have fewer than `digits`
places when it starts with a zero — `081804` as an integer is `81804`. The
authenticator app always shows the full width, so returning the bare integer makes
roughly one code in ten a digit short and it fails to verify. `.zfill(digits)`
restores the leading zeros, which is why HOTP values are strings.
''',
                    },
                    {
                        "q": "`verify_totp` accepts a code from the step before or after the current one, and compares with `hmac.compare_digest` instead of `==`. What does using `compare_digest` defend against?",
                        "opts": [
                            "A client clock that has drifted more than a single step out of sync, which the verification window would otherwise reject outright",
                            "A timing side channel, where how long `==` takes to fail reveals the correct code one character at a time",
                            "A replay of a previously used code within the same 30-second step",
                            "An attacker submitting a code for a future counter beyond the window",
                        ],
                        "a": 1,
                        "whys": [
                            r"Clock drift is handled by the window of counters, not by the comparison function. `compare_digest` addresses how the two strings are compared, not which counters are tried.",
                            r"Right: `==` on strings can return as soon as two characters differ, so its timing leaks how many leading characters matched. `compare_digest` takes constant time, denying an attacker that digit-by-digit oracle.",
                            r"Replay within a step is a separate concern needing a used-code record; the comparison function does nothing about it. `compare_digest` is purely about not leaking timing.",
                            r"Codes beyond the window are rejected by the range of counters checked, regardless of comparison. The constant-time compare defends the matching step against timing analysis.",
                        ],
                        "why": r'''
String `==` can short-circuit on the first differing character, so the time it
takes to fail depends on how many leading characters matched — an attacker who can
measure that learns the correct code one character at a time. `hmac.compare_digest`
runs in constant time regardless of where the strings differ, closing that side
channel. The drift window and code reuse are handled elsewhere.
''',
                    },
                ],
            },
            "title": "Credentials: cost models and second factors",
            "summary": "What a password policy is worth, and what backoff and TOTP add to it.",
            "concepts": [
                "Keyspace and entropy: `alphabet ** length`, and `length * log2(alphabet)` bits",
                "Offline attack cost scales with hash rate; a work factor divides that rate",
                "Average search is half the keyspace — the useful number is an order of magnitude",
                "Online guessing is bounded by rate limiting, not by entropy",
                "Exponential backoff with a cap, and why lockout resets on success",
                "HOTP (RFC 4226): HMAC-SHA1, dynamic truncation, modulo 10^digits",
                "TOTP (RFC 6238) is HOTP over `time // step`, verified across a drift window",
            ],
            "lab": {
                "title": "Cracking cost, backoff and TOTP",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Three defences, measured rather than asserted.

## 1 — Policy cost model

A policy is a dict: `{"length": 6, "lower": True, "upper": False,
"digits": True, "symbols": False}`. The class sizes are in `CLASSES`
(symbols is `len(string.punctuation)`, i.e. 32).

- `alphabet_size(policy)` — the classes summed. `ValueError` when no class is
  enabled, because there is then nothing to draw from.
- `keyspace(policy)` — `alphabet_size ** length`. `ValueError` when
  `length < 1`.
- `entropy_bits(policy)` — `length * log2(alphabet_size)`.
- `average_crack_seconds(policy, hashes_per_second, work_factor=0)` — an
  offline attacker tries half the keyspace on average, at
  `hashes_per_second / 2 ** work_factor` guesses per second. `ValueError` for
  a non-positive rate.

## 2 — `LoginThrottle(base_delay=1.0, max_delay=300.0, threshold=3)`

- `delay_for(failures)` — `0.0` below `threshold`, otherwise
  `base_delay * 2 ** (failures - threshold)`, capped at `max_delay`.
- `record_failure(user, now)` — count it, block the user until
  `now + delay_for(count)`, and return that delay.
- `record_success(user)` — forget the user entirely.
- `allowed(user, now)` — `True` when `now` has reached the block expiry.
  An unseen user is always allowed.

## 3 — One-time passwords

- `hotp(secret, counter, digits=6)` — HMAC-SHA1 of the counter as an 8-byte
  big-endian value; take `offset = digest[19] & 0x0F`, read the four bytes at
  `offset` big-endian, mask off the top bit, take modulo `10 ** digits`, and
  zero-pad to `digits`. `ValueError` for a negative counter.
- `totp(secret, timestamp, step=30, digits=6)` — `hotp` over `timestamp // step`.
- `verify_totp(secret, code, timestamp, step=30, digits=6, window=1)` — `True`
  when `code` matches any counter within `window` steps either side. Compare
  with `hmac.compare_digest`, not `==`.

The RFC 4226 and RFC 6238 test vectors are in the checks.
''',
                "files": [{"name": "main.py", "content": r'''
import hashlib
import hmac
import math
import string

CLASSES = {"lower": 26, "upper": 26, "digits": 10, "symbols": len(string.punctuation)}

DEMO_POLICY = {"length": 6, "lower": True, "upper": False, "digits": True, "symbols": False}


def alphabet_size(policy):
    """Sum of the enabled class sizes. ValueError when none is enabled."""
    # your code here


def keyspace(policy):
    """alphabet_size ** length. ValueError when length < 1."""
    # your code here


def entropy_bits(policy):
    """length * log2(alphabet_size)."""
    # your code here


def average_crack_seconds(policy, hashes_per_second, work_factor=0):
    """Half the keyspace at hashes_per_second / 2 ** work_factor guesses a second."""
    # your code here


class LoginThrottle:
    """Exponential backoff for online guessing."""

    def __init__(self, base_delay=1.0, max_delay=300.0, threshold=3):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.threshold = threshold
        self.failures = {}
        self.blocked_until = {}

    def delay_for(self, failures):
        # your code here
        pass

    def record_failure(self, user, now):
        # your code here
        pass

    def record_success(self, user):
        # your code here
        pass

    def allowed(self, user, now):
        # your code here
        pass


def hotp(secret, counter, digits=6):
    """RFC 4226 HOTP over HMAC-SHA1, as a zero-padded string."""
    # your code here


def totp(secret, timestamp, step=30, digits=6):
    """RFC 6238 TOTP: hotp over timestamp // step."""
    # your code here


def verify_totp(secret, code, timestamp, step=30, digits=6, window=1):
    """True when code matches any counter within window steps either side."""
    # your code here


print(keyspace(DEMO_POLICY))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import hashlib
import hmac
import math
import string

CLASSES = {"lower": 26, "upper": 26, "digits": 10, "symbols": len(string.punctuation)}

DEMO_POLICY = {"length": 6, "lower": True, "upper": False, "digits": True, "symbols": False}


def alphabet_size(policy):
    """Sum of the enabled class sizes. ValueError when none is enabled."""
    size = sum(count for name, count in CLASSES.items() if policy.get(name))
    if size == 0:
        raise ValueError("a policy must enable at least one character class")
    return size


def keyspace(policy):
    """alphabet_size ** length. ValueError when length < 1."""
    length = policy.get("length", 0)
    if length < 1:
        raise ValueError("length must be at least 1")
    return alphabet_size(policy) ** length


def entropy_bits(policy):
    """length * log2(alphabet_size)."""
    return policy["length"] * math.log2(alphabet_size(policy))


def average_crack_seconds(policy, hashes_per_second, work_factor=0):
    """Half the keyspace at hashes_per_second / 2 ** work_factor guesses a second."""
    if hashes_per_second <= 0:
        raise ValueError("hash rate must be positive")
    rate = hashes_per_second / (2 ** work_factor)
    return keyspace(policy) / 2 / rate


class LoginThrottle:
    """Exponential backoff for online guessing."""

    def __init__(self, base_delay=1.0, max_delay=300.0, threshold=3):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.threshold = threshold
        self.failures = {}
        self.blocked_until = {}

    def delay_for(self, failures):
        if failures < self.threshold:
            return 0.0
        return min(self.base_delay * 2 ** (failures - self.threshold), self.max_delay)

    def record_failure(self, user, now):
        count = self.failures.get(user, 0) + 1
        self.failures[user] = count
        delay = self.delay_for(count)
        self.blocked_until[user] = now + delay
        return delay

    def record_success(self, user):
        self.failures.pop(user, None)
        self.blocked_until.pop(user, None)

    def allowed(self, user, now):
        return now >= self.blocked_until.get(user, 0.0)


def hotp(secret, counter, digits=6):
    """RFC 4226 HOTP over HMAC-SHA1, as a zero-padded string."""
    if counter < 0:
        raise ValueError("counter must not be negative")
    digest = hmac.new(secret, counter.to_bytes(8, "big"), hashlib.sha1).digest()
    offset = digest[19] & 0x0F
    truncated = int.from_bytes(digest[offset:offset + 4], "big") & 0x7FFFFFFF
    return str(truncated % (10 ** digits)).zfill(digits)


def totp(secret, timestamp, step=30, digits=6):
    """RFC 6238 TOTP: hotp over timestamp // step."""
    return hotp(secret, timestamp // step, digits)


def verify_totp(secret, code, timestamp, step=30, digits=6, window=1):
    """True when code matches any counter within window steps either side."""
    counter = timestamp // step
    for drift in range(-window, window + 1):
        if counter + drift < 0:
            continue
        if hmac.compare_digest(hotp(secret, counter + drift, digits), str(code)):
            return True
    return False


print(keyspace(DEMO_POLICY))
print(round(entropy_bits(DEMO_POLICY), 2), "bits")
print(average_crack_seconds(DEMO_POLICY, 1e9), "seconds at 1e9 h/s")
print(average_crack_seconds(DEMO_POLICY, 1e9, work_factor=12), "seconds at cost 12")
print(totp(b"12345678901234567890", 59, digits=8))
'''}],
                "hints": [
                    "`sum(count for name, count in CLASSES.items() if policy.get(name))` collapses the whole policy in one line — then raise if it is zero.",
                    "`delay_for` is `min(base * 2 ** (failures - threshold), max_delay)`, guarded by an early `return 0.0` below the threshold.",
                    "`counter.to_bytes(8, \"big\")` gives the RFC's 8-byte counter; `int.from_bytes(digest[offset:offset+4], \"big\") & 0x7FFFFFFF` is the dynamic truncation.",
                    "`str(value).zfill(digits)` restores the leading zeros that `% 10 ** digits` throws away — a TOTP of 081804 is not 81804.",
                ],
                "tests": [
                    {"name": "Alphabet and keyspace", "code": r'''
_p = {"length": 6, "lower": True, "digits": True}
assert alphabet_size(_p) == 36, f"lower+digits is 36 characters, got {alphabet_size(_p)}"
assert keyspace(_p) == 2176782336, f"36 ** 6 is 2176782336, got {keyspace(_p)}"
_full = {"length": 12, "lower": True, "upper": True, "digits": True, "symbols": True}
assert alphabet_size(_full) == 94, f"the full printable set is 94 characters, got {alphabet_size(_full)}"
assert keyspace(_full) == 94 ** 12, "keyspace should be alphabet ** length"
assert keyspace({"length": 1, "digits": True}) == 10, "A single digit has a keyspace of 10"
'''},
                    {"name": "Empty policies are refused", "code": r'''
for _bad in [{"length": 8}, {"length": 8, "lower": False, "digits": False}]:
    try:
        alphabet_size(_bad)
        assert False, f"alphabet_size({_bad!r}) should raise ValueError"
    except ValueError:
        pass
for _bad in [{"length": 0, "lower": True}, {"lower": True}, {"length": -3, "lower": True}]:
    try:
        keyspace(_bad)
        assert False, f"keyspace({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Entropy in bits", "code": r'''
_p = {"length": 6, "lower": True, "digits": True}
_got = entropy_bits(_p)
assert abs(_got - 31.019550008653873) < 1e-9, f"entropy_bits gave {_got!r}, expected 31.019550008653873"
_bin = {"length": 128, "digits": False, "lower": False, "upper": False, "symbols": True}
assert entropy_bits({"length": 4, "digits": True, "upper": True, "lower": True, "symbols": True}) > \
    entropy_bits({"length": 4, "digits": True}), "A wider alphabet is worth more bits"
'''},
                    {"name": "Offline cracking cost, and what a work factor buys", "code": r'''
_p = {"length": 6, "lower": True, "digits": True}
_fast = average_crack_seconds(_p, 1e9)
assert abs(_fast - 1.088391168) < 1e-9, f"At 1e9 h/s expected 1.088391168 s, got {_fast!r}"
_slow = average_crack_seconds(_p, 1e9, work_factor=10)
assert abs(_slow / _fast - 1024.0) < 1e-6, \
    f"A work factor of 10 should cost 1024x more, ratio was {_slow / _fast!r}"
try:
    average_crack_seconds(_p, 0)
    assert False, "A zero hash rate should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Backoff grows and caps", "code": r'''
_t = LoginThrottle()
_want = [0.0, 0.0, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0, 300.0]
for _n, _w in enumerate(_want, 1):
    _got = _t.delay_for(_n)
    assert abs(_got - _w) < 1e-9, f"delay_for({_n}) gave {_got!r}, expected {_w}"
assert _t.delay_for(40) == 300.0, "The delay is capped at max_delay"
'''},
                    {"name": "Blocking, expiry and reset", "code": r'''
_t = LoginThrottle()
assert _t.allowed("ghost", 0.0) is True, "An unseen user is not blocked"
assert _t.record_failure("mallory", 0.0) == 0.0, "The first failure costs nothing"
_t.record_failure("mallory", 0.0)
assert abs(_t.record_failure("mallory", 100.0) - 1.0) < 1e-9, "The third failure costs 1 s"
assert _t.allowed("mallory", 100.5) is False, "Still inside the block window"
assert _t.allowed("mallory", 101.0) is True, "The block has expired"
_t.record_failure("mallory", 101.0)
assert _t.allowed("mallory", 101.0) is False, "The fourth failure blocks for 2 s"
_t.record_success("mallory")
assert _t.allowed("mallory", 101.0) is True, "A success clears the block"
assert _t.delay_for(1) == 0.0 and _t.failures.get("mallory", 0) == 0, "and clears the counter"
'''},
                    {"name": "RFC 4226 HOTP vectors", "code": r'''
_secret = b"12345678901234567890"
_want = ["755224", "287082", "359152", "969429", "338314",
         "254676", "287922", "162583", "399871", "520489"]
for _c, _w in enumerate(_want):
    _got = hotp(_secret, _c)
    assert _got == _w, f"hotp(secret, {_c}) gave {_got!r}, expected {_w!r}"
assert isinstance(_got, str), "HOTP values are strings so leading zeros survive"
try:
    hotp(_secret, -1)
    assert False, "A negative counter should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "RFC 6238 TOTP vectors and the drift window", "code": r'''
_secret = b"12345678901234567890"
for _t, _w in [(59, "94287082"), (1111111109, "07081804"), (1111111111, "14050471"),
               (1234567890, "89005924"), (2000000000, "69279037")]:
    _got = totp(_secret, _t, digits=8)
    assert _got == _w, f"totp(secret, {_t}, digits=8) gave {_got!r}, expected {_w!r}"
_code = totp(_secret, 1111111109, digits=8)
assert verify_totp(_secret, _code, 1111111109, digits=8) is True, "The current step must verify"
assert verify_totp(_secret, _code, 1111111109 + 30, digits=8) is True, "One step late is inside the window"
assert verify_totp(_secret, _code, 1111111109 - 30, digits=8) is True, "One step early is inside the window"
assert verify_totp(_secret, _code, 1111111109 + 120, digits=8) is False, "Four steps late is outside it"
assert verify_totp(_secret, "00000000", 1111111109, digits=8) is False, "A wrong code must not verify"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "read": [
                {
                    "title": "From a wall of log lines to a number you can defend",
                    "minutes": 13,
                    "body": r'''
A day of authentication events is sitting in a file. Somewhere in it are a
brute-force attempt, an account logging in from two countries an hour apart, and a
compromised host quietly phoning home on a timer. Everything else is people doing
their jobs. Your task is not to read the file — no one reads the file — but to
write detectors that pull those three signals out and then to say, with a number,
how good your detectors are. That last part is what separates detection
engineering from pattern-matching by vibe.

A well-formed line looks like this:

```text
2026-05-04T08:00:00Z user=alice ip=10.0.0.10 country=NO action=login result=success bytes=512
```

A timestamp, then `key=value` fields. The first thing that goes wrong is the
timestamp, and it goes wrong silently.

## The timezone bug that does not raise

Parse that stamp naively and Python hands you a `datetime` with no timezone
attached, then quietly interprets it in whatever zone the machine running the code
happens to be in.

```python
from datetime import datetime, timezone

text = "2026-05-04T08:00:00Z"
naive = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
aware = naive.replace(tzinfo=timezone.utc)
print(naive.tzinfo, aware.tzinfo)
print(int(aware.timestamp()))
```

It prints `None UTC` and then `1777881600`. The `Z` in the log means Zulu —
UTC — but `strptime` discards it: `naive.tzinfo` is `None`. Call `.timestamp()` on
that naive value and the answer shifts by your machine's offset from UTC, so the
same log parsed in Oslo and in New York produces epoch seconds six hours apart, and
every time-window detector downstream inherits the error without a single
exception being raised. Attaching `timezone.utc` with `.replace` before taking the
timestamp is the fix, and `parse_ts` in the lab exists to make that one line
impossible to skip. A bug that raises is a bug you find; this one just makes your
detectors quietly wrong.

## Parse defensively or lose the pipeline

The second thing that goes wrong is a malformed line, and the rule is firm: a bad
line is dropped, never allowed to crash the run. A logging pipeline that dies on
line 40,000 of 50,000 has thrown away the 10,000 lines it had not reached yet,
including possibly the attack. So `parse_event` returns `None` for anything it
cannot trust — a blank line, a token with no `=`, an empty key or value, or a line
missing a required field — and `load_events` simply skips the `None`s.

```python
REQUIRED = ("user", "ip", "country", "action", "result")


def parse_event(line):
    parts = line.split()
    if not parts:
        return None
    event = {"ts": parts[0]}
    for token in parts[1:]:
        key, sep, value = token.partition("=")
        if not sep or not key or not value:
            return None
        event[key] = value
    for field in REQUIRED:
        if field not in event:
            return None
    return event


print(parse_event("2026-05-04T08:00:00Z user=alice ip=10.0.0.10 country=NO action=login result=success"))
print(parse_event("2026-05-04T08:00:00Z user=alice"))
print(parse_event("2026-05-04T08:00:00Z user= ip=10.0.0.1 country=NO action=login result=ok"))
print(parse_event(""))
```

The first line returns a full dict; the other three return `None` — one for
missing fields, one for an empty value (`user=`), one for a blank line. The device
that makes the empty-value case clean is `partition("=")`: it always returns three
pieces, and an empty separator or empty key or value is a single rejection, no
special-casing.

## Three detectors, three shapes of signal

Each attack has a shape, and the detector is that shape written down. **Brute
force** is many failures in a short time. Sort each user's failure timestamps and
slide a window of `threshold` failures across them: if the span from the first to
the `threshold`-th is within `window` seconds, fire.

```python
stamps = [1000, 1008, 1016, 1024, 1032, 1040]
threshold, window = 5, 60
for i in range(len(stamps) - threshold + 1):
    span = stamps[i + threshold - 1] - stamps[i]
    print("start", i, "->", stamps[i], "to", stamps[i + threshold - 1], "spans", span, "s:", span <= window)
```

It prints two lines, each ending `spans 32 s: True`: six failures eight seconds
apart contain five within any 32-second span, comfortably inside a 60-second
window. The index arithmetic is the part people get wrong. To look at `threshold`
consecutive failures starting at `i`, the last of them is at `i + threshold - 1`,
so `i` runs to `len(stamps) - threshold` inclusive — hence
`range(len(stamps) - threshold + 1)`. Off by one here and the last possible window
is never checked, so an attack that finishes at the very end of the log is missed.

**Impossible travel** is the same user succeeding from two different countries too
close together to have travelled. Sort each user's successful logins and compare
each consecutive pair: different country, gap under the minimum, fire.

**Beaconing** is the subtle one, because its signal is not volume but *regularity*.
Malware calling home every five minutes produces connections whose gaps are almost
identical; a human produces ragged gaps. So the test is on the variance of the
inter-arrival times, not their count.

```python
regular = [3000 + k * 300 for k in range(6)]
noisy = [3000 + g for g in (0, 300, 1200, 1320, 1920, 1965)]
for ip, stamps in (("10.0.0.99", regular), ("10.0.0.44", noisy)):
    gaps = [b - a for a, b in zip(stamps, stamps[1:])]
    print(ip, gaps, "range", max(gaps) - min(gaps))
```

It prints `10.0.0.99 [300, 300, 300, 300, 300] range 0` and
`10.0.0.44 [300, 900, 120, 600, 45] range 855`. Both hosts made six connections;
counting connections cannot tell them apart. The gap `range` — `max - min` — can:
zero for the metronome, 855 for the human. The mistake here is to build the
detector around how *much* traffic a host sends, when the tell of automation is how
*evenly* it sends it.

## The number that makes it honest

A detector is a classifier, and a classifier makes two kinds of error. It can flag
something innocent — a false positive — and it can miss something real — a false
negative. One number hides both, so you report two.

```python
def precision_recall(flagged, actual):
    flagged, actual = set(flagged), set(actual)
    hits = len(flagged & actual)
    precision = hits / len(flagged) if flagged else 0.0
    recall = hits / len(actual) if actual else 0.0
    return precision, recall


print(precision_recall(["mallory", "eve", "bob"], {"mallory", "eve", "svc"}))
print(precision_recall([], {"mallory"}))
print(precision_recall(["alice", "bob", "carol", "mallory", "eve"], {"mallory", "eve"}))
```

It prints `(0.666..., 0.666...)`, then `(0.0, 0.0)`, then `(0.4, 1.0)`.
*Precision* is the fraction of your flags that were right — of `mallory, eve, bob`,
two were real, so `2/3`. *Recall* is the fraction of the real attacks you caught —
of `mallory, eve, svc`, you named two, so `2/3` again. The two move in opposite
directions as you tune. The last line is the extreme: flag everyone and recall is a
perfect `1.0`, because you caught both real attacks — but precision collapses to
`0.4`, because three of your five flags were innocent. A detector that flags
everything catches every attack and is useless, and the recall number alone would
call it perfect. That is exactly why both are reported, and why the empty cases
return `0.0` rather than dividing by zero: flagging nothing, or having no ground
truth, must score zero, not crash the report.

## Where these detectors stop working

Every one of these is a heuristic tuned to a threshold, and the threshold is an
admission of where it breaks. Brute force at five-in-sixty misses an attacker who
guesses four times a minute — *slow* brute force walks under it deliberately.
Impossible travel assumes an IP maps to a country and that people do not use VPNs,
so a legitimate traveller on a corporate VPN can trip it while a real attacker
behind a local proxy does not. Beaconing on low gap-variance catches a naive timer
and misses malware that jitters its callbacks on purpose — which is why modern
implants do exactly that. These detectors raise the cost of the obvious attack;
they do not close the door, and the precision/recall number is honest precisely
because it measures that gap rather than hiding it.

The lab, **Three detectors and their score**, builds this pipeline end to end:
`parse_ts` with its timezone fix, `parse_event` and `load_events` with defensive
dropping, `brute_force`, `impossible_travel` and `beaconing` over a synthetic day
of events, and `precision_recall` scored against the labelled accounts — the same
`(1.0, 1.0)` the account detectors reach on this particular log, and the number you
would watch move as you tuned them on a real one.
'''
                }
            ],
            "quiz": {
                "title": "Parsing, windows, and scoring a detector",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`parse_ts` uses `datetime.strptime(text, \"%Y-%m-%dT%H:%M:%SZ\")` and then `.replace(tzinfo=timezone.utc)` before `.timestamp()`. What goes wrong if the `.replace` is left out?",
                        "opts": [
                            "`strptime` raises on the trailing `Z`, so the whole pipeline stops on the first line",
                            "The datetime is treated as local time, so the epoch seconds shift by the machine's UTC offset with no error raised",
                            "The timestamp is silently returned as a float instead of an int, which breaks the integer window comparisons every downstream detector relies on",
                            "The `Z` is parsed as a literal, adding a spurious character that corrupts later fields",
                        ],
                        "a": 1,
                        "whys": [
                            r"`strptime` matches the `Z` as a literal in the format string and parses cleanly — it just throws the zone information away. The failure is silent, not an exception.",
                            r"Right: without a tzinfo the datetime is naive, and `.timestamp()` assumes local time, so the same `Z`-stamped log yields different epoch seconds in different zones — wrong, and with nothing raised to warn you.",
                            r"Casting to `int` handles the float; the timezone bug is about *which instant* the value denotes, not its type. The shift happens whether or not you convert to int.",
                            r"The `Z` is consumed by the format's literal `Z` and produces no extra character. The bug is the discarded zone, invisible until the numbers are compared across machines.",
                        ],
                        "why": r'''
`strptime` matches the `Z` as a literal and returns a naive datetime — `tzinfo`
is `None`. Calling `.timestamp()` on a naive value makes Python assume local time,
so the epoch seconds shift by the machine's offset from UTC and the same log parsed
in two zones disagrees. Nothing raises; the detectors just inherit a silent error.
Attaching `timezone.utc` first fixes the instant the value denotes.
''',
                    },
                    {
                        "q": "`parse_event` returns `None` for a malformed line and `load_events` skips it, rather than raising. Why is dropping the right choice for a log pipeline?",
                        "opts": [
                            "Raising on a bad line stops the run, discarding every later line — including, possibly, the attack",
                            "Malformed lines are always benign, so there is never anything worth reporting in them",
                            "Returning None is measurably faster than raising an exception, and raw parsing speed is the priority when working through very large logs",
                            "A dropped line is automatically re-queued for parsing once the run finishes",
                        ],
                        "a": 0,
                        "whys": [
                            r"Right: a pipeline that raises on line 40,000 never reaches line 50,000, throwing away the events it had not parsed yet. Dropping the one bad line preserves every good one, which is what a detector needs.",
                            r"They are not always benign — a truncated or oddly-formatted line could itself be the interesting event — but that is an argument for logging drops, not for crashing. The reason to drop rather than raise is to keep the run alive.",
                            r"Performance is real but beside the point; even if raising were free, stopping the run would still lose the unparsed remainder. Robustness, not speed, is why dropping wins.",
                            r"Nothing re-queues a dropped line; it is skipped and gone. The value is that the surrounding good lines still get processed, not that the bad one comes back.",
                        ],
                        "why": r'''
A logging pipeline that raises on a malformed line dies partway through and
discards everything it had not yet parsed — potentially the attack itself.
Returning `None` and skipping it keeps every well-formed event flowing. Malformed
lines are not guaranteed benign, which is an argument for recording that a drop
happened, not for letting one bad line take down the whole run.
''',
                    },
                    {
                        "q": "Brute force slides a window over a user's sorted failure times: `for i in range(len(stamps) - threshold + 1)`. Why the `+ 1`?",
                        "opts": [
                            "It reserves one extra iteration as a guard against an off-by-one in the timestamps",
                            "The last valid start index is `len(stamps) - threshold`, and `range` is exclusive of its stop, so it needs the `+ 1` to include it",
                            "It accounts for the window boundary itself counting as one additional failure",
                            "Without it the loop would double-count the very first window against the second, so the trailing `+ 1` is there precisely to cancel that overlap out",
                        ],
                        "a": 1,
                        "whys": [
                            r"There is no guard iteration; every index the loop visits is a real candidate window. The `+ 1` is arithmetic about `range`'s exclusive stop, not slack.",
                            r"Right: a window of `threshold` failures starting at `i` ends at `i + threshold - 1`, so the largest legal `i` is `len(stamps) - threshold`, and because `range` stops one short you add one to include it.",
                            r"The window boundary is a timestamp comparison, not an extra element in the list. The `+ 1` is about which start indices exist, not about counting an extra failure.",
                            r"The loop visits each start index once; there is no double-counting to cancel. The `+ 1` exists so the final window, ending at the last failure, is actually examined.",
                        ],
                        "why": r'''
A window of `threshold` consecutive failures starting at index `i` ends at
`i + threshold - 1`, so the last start that fits is `len(stamps) - threshold`.
`range(stop)` never yields `stop`, so without the `+ 1` that final window — the one
ending on the last failure — is never checked, and an attack finishing at the end
of the log is missed.
''',
                    },
                    {
                        "q": "Two hosts each made six `connect` events. One's gaps are `[300, 300, 300, 300, 300]`, the other's are `[300, 900, 120, 600, 45]`. Why does the beaconing detector test `max(gaps) - min(gaps)` rather than the number of connections?",
                        "opts": [
                            "Connection count is hard to compute, whereas the gap range is a single subtraction",
                            "The tell of an automated beacon is regular timing, not volume, and both hosts sent the same number of connections",
                            "The gap range is larger for the beacon, which is what flags it as suspicious",
                            "Counting connections alone would also wrongly flag the busiest legitimate servers as beacons, so the raw volume is deliberately capped instead",
                        ],
                        "a": 1,
                        "whys": [
                            r"Counting is trivial either way; difficulty is not the issue. The reason to measure the gap range is that it captures the *regularity* that distinguishes a beacon, which a count cannot.",
                            r"Right: both hosts made six connections, so volume cannot separate them — but a beacon's near-constant gaps give a range near zero, while the human's ragged gaps give a large one. Regularity is the signal.",
                            r"It is the other way around: the beacon has the *small* range (0 here), the human the large one (855). The detector fires on low variance, so a small range is the suspicious case.",
                            r"Volume is not the axis at all here; the beacon and the human sent identical counts. The detector keys on how evenly the connections are spaced, not on capping how many there are.",
                        ],
                        "why": r'''
Both hosts sent six connections, so a count cannot tell them apart. Automation
reveals itself in *regularity*: the beacon's gaps are all 300, giving a range of 0,
while the human's gaps swing from 45 to 900, a range of 855. Testing
`max(gaps) - min(gaps)` against a small jitter fires on the metronome and leaves the
ragged human alone; volume never enters into it.
''',
                    },
                    {
                        "q": "A detector flags all five users; the two real attackers are among them. `precision_recall` returns `(0.4, 1.0)`. Why report both numbers instead of the recall alone?",
                        "opts": [
                            "Recall alone is enough; a recall of 1.0 means the detector is working perfectly",
                            "Recall alone rewards flagging everything, which catches every attack while burying analysts in false positives — precision exposes that",
                            "Precision and recall always rise and fall together in lockstep, so reporting both of them is really just a redundant consistency check on the arithmetic",
                            "Precision measures speed and recall measures accuracy, so the two describe different runs",
                        ],
                        "a": 1,
                        "whys": [
                            r"A recall of 1.0 here comes from flagging literally everyone, which is useless. Recall cannot see the three false positives dragging precision to 0.4, so it alone calls a worthless detector perfect.",
                            r"Right: flag everything and recall is a perfect 1.0 because no attack is missed, but precision falls to 0.4 as three of five flags are innocent. Only precision reveals the cost of that strategy, so both are reported.",
                            r"They move in *opposite* directions under tuning — widen the net and recall rises while precision falls. That trade-off is the whole reason one number cannot stand in for the other.",
                            r"Both measure the same run's classification quality, not speed. Precision is the fraction of flags that were right; recall is the fraction of attacks caught. Neither is a timing measurement.",
                        ],
                        "why": r'''
Flag every user and recall is a perfect `1.0` — no attack escapes — but precision
is only `0.4`, because three of the five flags were innocent. Recall alone would
crown that useless detector; precision is what exposes the flood of false
positives. The two trade against each other as thresholds move, so reporting both
is the only honest summary.
''',
                    },
                ],
            },
            "title": "Detection engineering",
            "summary": "Turning a log into baselines, detectors and a precision/recall number.",
            "concepts": [
                "Structured logging: one event per line, `key=value` fields, UTC timestamps",
                "Parse defensively — a malformed line is dropped, never allowed to crash the pipeline",
                "Sliding-window counting for brute force: `stamps[i + k - 1] - stamps[i] <= window`",
                "Impossible travel compares consecutive successful logins by geography and gap",
                "Beaconing shows as low variance in inter-arrival times, not in volume",
                "Every detector is a classifier: true/false positives and negatives",
                "Precision and recall trade against each other as thresholds move",
            ],
            "lab": {
                "title": "Three detectors and their score",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
`main.py` already generates `LOG_LINES`, a synthetic day of authentication and
network events. Each valid line looks like:

```text
2026-05-04T08:00:00Z user=alice ip=10.0.0.10 country=NO action=login result=success bytes=512
```

Write the pipeline.

**`parse_ts(text)`** — the ISO-8601 UTC stamp as integer epoch seconds. Use
`datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")` and attach `timezone.utc`
before calling `.timestamp()`, or you will silently inherit the local zone.

**`parse_event(line)`** — a dict with an integer `ts` plus every `key=value`
field. Return `None` for anything malformed: a blank line, an unparseable
stamp, a token with no `=`, an empty key or value, or a line missing any of
`user`, `ip`, `country`, `action`, `result`.

**`load_events(lines)`** — every valid event, in file order.

**`brute_force(events, threshold=5, window=60)`** — sorted usernames with
`threshold` failed logins inside any `window`-second span.

**`impossible_travel(events, min_seconds=3600)`** — sorted usernames with two
*consecutive successful* logins from different countries less than
`min_seconds` apart.

**`beaconing(events, min_events=5, jitter=2)`** — sorted source IPs with at
least `min_events` `connect` events whose inter-arrival gaps vary by no more
than `jitter` seconds (`max(gaps) - min(gaps) <= jitter`).

**`precision_recall(flagged, actual)`** — `(precision, recall)` as floats.
Each is `0.0` when its denominator is zero; do not divide by zero.
''',
                "files": [{"name": "main.py", "content": r'''
from datetime import datetime, timedelta, timezone

BASE = datetime(2026, 5, 4, 8, 0, 0, tzinfo=timezone.utc)


def at(seconds):
    """Timestamp text for BASE + seconds. Used only to build the sample log."""
    return (BASE + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


LOG_LINES = []
for _i, _user in enumerate(["alice", "bob", "carol"]):
    LOG_LINES.append(f"{at(_i * 120)} user={_user} ip=10.0.0.1{_i} country=NO action=login result=success bytes=512")
    LOG_LINES.append(f"{at(_i * 120 + 7200)} user={_user} ip=10.0.0.1{_i} country=NO action=login result=success bytes=512")
for _k in range(6):
    LOG_LINES.append(f"{at(1000 + _k * 8)} user=mallory ip=203.0.113.7 country=NO action=login result=fail bytes=0")
LOG_LINES.append(f"{at(2000)} user=eve ip=10.0.0.20 country=NO action=login result=success bytes=100")
LOG_LINES.append(f"{at(2600)} user=eve ip=198.51.100.9 country=JP action=login result=success bytes=100")
for _k in range(6):
    LOG_LINES.append(f"{at(3000 + _k * 300)} user=svc ip=10.0.0.99 country=NO action=connect result=success bytes=64")
for _gap in [0, 300, 1200, 1320, 1920, 1965]:
    LOG_LINES.append(f"{at(3000 + _gap)} user=svc ip=10.0.0.44 country=NO action=connect result=success bytes=64")
LOG_LINES.append("not a log line at all")
LOG_LINES.append("2026-05-04T08:00:00Z user=alice")
LOG_LINES.append("")

LABELLED_ACCOUNTS = {"mallory", "eve"}

REQUIRED_FIELDS = ("user", "ip", "country", "action", "result")


def parse_ts(text):
    """ISO-8601 UTC stamp -> integer epoch seconds."""
    # your code here


def parse_event(line):
    """One log line -> event dict, or None when it is malformed."""
    # your code here


def load_events(lines):
    """Every valid event, in file order."""
    # your code here


def brute_force(events, threshold=5, window=60):
    """Sorted users with `threshold` failed logins inside any `window` seconds."""
    # your code here


def impossible_travel(events, min_seconds=3600):
    """Sorted users seen succeeding from two countries less than min_seconds apart."""
    # your code here


def beaconing(events, min_events=5, jitter=2):
    """Sorted IPs whose connect gaps vary by at most `jitter` seconds."""
    # your code here


def precision_recall(flagged, actual):
    """(precision, recall); 0.0 wherever the denominator would be zero."""
    # your code here


EVENTS = load_events(LOG_LINES)
print(len(LOG_LINES), "lines")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
from datetime import datetime, timedelta, timezone

BASE = datetime(2026, 5, 4, 8, 0, 0, tzinfo=timezone.utc)


def at(seconds):
    """Timestamp text for BASE + seconds. Used only to build the sample log."""
    return (BASE + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


LOG_LINES = []
for _i, _user in enumerate(["alice", "bob", "carol"]):
    LOG_LINES.append(f"{at(_i * 120)} user={_user} ip=10.0.0.1{_i} country=NO action=login result=success bytes=512")
    LOG_LINES.append(f"{at(_i * 120 + 7200)} user={_user} ip=10.0.0.1{_i} country=NO action=login result=success bytes=512")
for _k in range(6):
    LOG_LINES.append(f"{at(1000 + _k * 8)} user=mallory ip=203.0.113.7 country=NO action=login result=fail bytes=0")
LOG_LINES.append(f"{at(2000)} user=eve ip=10.0.0.20 country=NO action=login result=success bytes=100")
LOG_LINES.append(f"{at(2600)} user=eve ip=198.51.100.9 country=JP action=login result=success bytes=100")
for _k in range(6):
    LOG_LINES.append(f"{at(3000 + _k * 300)} user=svc ip=10.0.0.99 country=NO action=connect result=success bytes=64")
for _gap in [0, 300, 1200, 1320, 1920, 1965]:
    LOG_LINES.append(f"{at(3000 + _gap)} user=svc ip=10.0.0.44 country=NO action=connect result=success bytes=64")
LOG_LINES.append("not a log line at all")
LOG_LINES.append("2026-05-04T08:00:00Z user=alice")
LOG_LINES.append("")

LABELLED_ACCOUNTS = {"mallory", "eve"}

REQUIRED_FIELDS = ("user", "ip", "country", "action", "result")


def parse_ts(text):
    """ISO-8601 UTC stamp -> integer epoch seconds."""
    moment = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return int(moment.timestamp())


def parse_event(line):
    """One log line -> event dict, or None when it is malformed."""
    parts = line.split()
    if not parts:
        return None
    try:
        event = {"ts": parse_ts(parts[0])}
    except ValueError:
        return None
    for token in parts[1:]:
        key, sep, value = token.partition("=")
        if not sep or not key or not value:
            return None
        event[key] = value
    for field in REQUIRED_FIELDS:
        if field not in event:
            return None
    return event


def load_events(lines):
    """Every valid event, in file order."""
    events = []
    for line in lines:
        event = parse_event(line)
        if event is not None:
            events.append(event)
    return events


def brute_force(events, threshold=5, window=60):
    """Sorted users with `threshold` failed logins inside any `window` seconds."""
    by_user = {}
    for event in events:
        if event["action"] == "login" and event["result"] == "fail":
            by_user.setdefault(event["user"], []).append(event["ts"])
    flagged = []
    for user, stamps in by_user.items():
        stamps.sort()
        for i in range(len(stamps) - threshold + 1):
            if stamps[i + threshold - 1] - stamps[i] <= window:
                flagged.append(user)
                break
    return sorted(flagged)


def impossible_travel(events, min_seconds=3600):
    """Sorted users seen succeeding from two countries less than min_seconds apart."""
    by_user = {}
    for event in events:
        if event["action"] == "login" and event["result"] == "success":
            by_user.setdefault(event["user"], []).append((event["ts"], event["country"]))
    flagged = []
    for user, seen in by_user.items():
        seen.sort()
        for (t1, c1), (t2, c2) in zip(seen, seen[1:]):
            if c1 != c2 and t2 - t1 < min_seconds:
                flagged.append(user)
                break
    return sorted(flagged)


def beaconing(events, min_events=5, jitter=2):
    """Sorted IPs whose connect gaps vary by at most `jitter` seconds."""
    by_ip = {}
    for event in events:
        if event["action"] == "connect":
            by_ip.setdefault(event["ip"], []).append(event["ts"])
    flagged = []
    for ip, stamps in by_ip.items():
        if len(stamps) < min_events:
            continue
        stamps.sort()
        gaps = [b - a for a, b in zip(stamps, stamps[1:])]
        if gaps and max(gaps) - min(gaps) <= jitter:
            flagged.append(ip)
    return sorted(flagged)


def precision_recall(flagged, actual):
    """(precision, recall); 0.0 wherever the denominator would be zero."""
    flagged = set(flagged)
    actual = set(actual)
    hits = len(flagged & actual)
    precision = hits / len(flagged) if flagged else 0.0
    recall = hits / len(actual) if actual else 0.0
    return (precision, recall)


EVENTS = load_events(LOG_LINES)
print(len(LOG_LINES), "lines ->", len(EVENTS), "events")
print("brute force:", brute_force(EVENTS))
print("impossible travel:", impossible_travel(EVENTS))
print("beaconing:", beaconing(EVENTS))
print("score:", precision_recall(brute_force(EVENTS) + impossible_travel(EVENTS),
                                 LABELLED_ACCOUNTS))
'''}],
                "hints": [
                    "`datetime.strptime(text, \"%Y-%m-%dT%H:%M:%SZ\").replace(tzinfo=timezone.utc)` — the `.replace` is what makes the result UTC rather than local.",
                    "`key, sep, value = token.partition(\"=\")` gives you the empty-`sep` case to reject in one step.",
                    "For brute force, sort each user's failure times and slide: `stamps[i + threshold - 1] - stamps[i] <= window`.",
                    "Beaconing is about *variance*, not volume: build the gap list with `zip(stamps, stamps[1:])`, then compare `max(gaps) - min(gaps)` against the jitter.",
                ],
                "tests": [
                    {"name": "Timestamps parse as UTC epoch seconds", "code": r'''
_want = int(datetime(2026, 5, 4, 8, 0, 0, tzinfo=timezone.utc).timestamp())
_got = parse_ts("2026-05-04T08:00:00Z")
assert _got == _want, f"parse_ts gave {_got!r}, expected {_want}"
assert isinstance(_got, int), f"parse_ts should return an int, got {type(_got).__name__}"
assert parse_ts("2026-05-04T08:00:30Z") - _got == 30, "Thirty seconds apart is thirty seconds"
'''},
                    {"name": "A good line becomes a full event", "code": r'''
_e = parse_event("2026-05-04T08:00:00Z user=alice ip=10.0.0.10 country=NO action=login result=success bytes=512")
assert _e is not None, "That line is well formed"
assert _e["user"] == "alice" and _e["country"] == "NO", f"Got {_e!r}"
assert _e["action"] == "login" and _e["result"] == "success", f"Got {_e!r}"
assert _e["ts"] == parse_ts("2026-05-04T08:00:00Z"), f"ts is {_e['ts']!r}"
assert _e["bytes"] == "512", "Extra fields are kept as text"
'''},
                    {"name": "Malformed lines are dropped, not raised", "code": r'''
_bad = [
    "",
    "   ",
    "not a log line at all",
    "2026-05-04T08:00:00Z user=alice",
    "2026-05-04T08:00:00Z user=alice ip=10.0.0.1 country=NO action=login",
    "2026-05-04T08:00:00Z user=alice ip=10.0.0.1 country=NO action=login result=ok bare",
    "2026-05-04T08:00:00Z user= ip=10.0.0.1 country=NO action=login result=ok",
    "2026-05-04T99:99:99Z user=a ip=b country=c action=d result=e",
]
for _line in _bad:
    assert parse_event(_line) is None, f"parse_event({_line!r}) should be None"
'''},
                    {"name": "The sample log loads cleanly", "code": r'''
assert len(EVENTS) == 26, f"Expected 26 valid events out of {len(LOG_LINES)} lines, got {len(EVENTS)}"
assert all(isinstance(_e["ts"], int) for _e in EVENTS), "Every ts should be an int"
assert [_e["user"] for _e in EVENTS][:2] == ["alice", "alice"], "File order should be preserved"
assert load_events([]) == [], "No lines means no events"
'''},
                    {"name": "Brute force fires on mallory only", "code": r'''
_got = brute_force(EVENTS)
assert _got == ["mallory"], f"brute_force gave {_got!r}, expected ['mallory']"
assert brute_force(EVENTS, threshold=7) == [], "Only six failures exist — seven cannot be found"
assert brute_force(EVENTS, window=10) == [], \
    "Five failures span 32 s, so a 10 s window should find nothing"
assert brute_force([]) == [], "An empty log flags nobody"
'''},
                    {"name": "Impossible travel fires on eve only", "code": r'''
_got = impossible_travel(EVENTS)
assert _got == ["eve"], f"impossible_travel gave {_got!r}, expected ['eve']"
assert impossible_travel(EVENTS, min_seconds=300) == [], \
    "The two logins are 600 s apart, which a 300 s threshold allows"
assert impossible_travel(EVENTS, min_seconds=100000) == ["eve"], "A wider threshold still flags eve"
'''},
                    {"name": "Beaconing fires on the regular host only", "code": r'''
_got = beaconing(EVENTS)
assert _got == ["10.0.0.99"], f"beaconing gave {_got!r}, expected ['10.0.0.99']"
assert beaconing(EVENTS, min_events=7) == [], "Neither host has seven connects"
assert beaconing(EVENTS, jitter=900) == ["10.0.0.44", "10.0.0.99"], \
    "A 900 s tolerance is loose enough to swallow the noisy host too"
'''},
                    {"name": "Precision and recall, including the empty cases", "code": r'''
_p, _r = precision_recall(["a", "b", "c"], {"b", "c", "d"})
assert abs(_p - 2 / 3) < 1e-9 and abs(_r - 2 / 3) < 1e-9, f"Got {(_p, _r)!r}, expected (0.667, 0.667)"
assert precision_recall([], {"a"}) == (0.0, 0.0), "Flagging nothing scores zero, it does not crash"
assert precision_recall(["a"], []) == (0.0, 0.0), "No ground truth scores zero too"
assert precision_recall(["a"], {"a"}) == (1.0, 1.0), "A perfect detector scores one"
_score = precision_recall(brute_force(EVENTS) + impossible_travel(EVENTS), LABELLED_ACCOUNTS)
assert _score == (1.0, 1.0), f"The two account detectors should be perfect here, got {_score!r}"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — defensive audit toolkit",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
One toolkit that ingests an application configuration and an application log
and produces a STRIDE-mapped findings report. `toolkit.py` holds the logic and
is what the checks import; `main.py` is the demo run.

## Vocabulary

`STRIDE` maps one-letter codes to names, `SEVERITY_RANK` orders
`critical < high < medium < low`, and a `Finding` is a dataclass with
`id`, `title`, `stride`, `severity`, `evidence`.

## Parsing

- `parse_config(text)` — `key = value` lines. Skip blanks and `#` comments.
  `true`/`false` (any case) become booleans, an optionally-signed run of digits
  becomes an `int`, everything else stays a string. A line with no `=` raises
  `ValueError`.
- `parse_event(line)` / `load_events(lines)` — as in module 4, but the
  required fields are only `user`, `action`, `result`.

## Configuration audit — `audit_config(config)`

Eight rules. **A missing key counts as its insecure value**, so an empty
configuration produces all eight findings.

```text
id       key                        insecure when   stride  severity
TLS-001  tls_enabled                is False        I       critical
PWD-001  admin_default_password     is True         S       critical
PWD-002  password_min_length        < 12            S       high
LOG-001  audit_logging              is False        R       high
RTL-001  max_login_attempts         <= 0            D       high
DBG-001  debug_mode                 is True         I       medium
SES-001  session_timeout_minutes    > 60            E       medium
INT-001  config_signature_required  is False        T       medium
```

Evidence for each is `f"{key} = {value!r}"` using the effective value.

## Log detectors

- `detect_brute_force(events, threshold=5, window=300)` — id `BRF-<user>`,
  stride `S`, severity `high`.
- `detect_privilege_escalation(events, admins)` — a successful
  `action=role_change` by a user not in `admins`. Id `PRV-<user>`, stride `E`,
  severity `critical`.
- `detect_exfiltration(events, byte_threshold=10000000)` — a user whose
  `action=download` `bytes` sum **exceeds** the threshold. Id `EXF-<user>`,
  stride `I`, severity `high`.

## Assembly

- `scan(config, events)` — every finding above, with `admins` read from the
  comma-separated `admins` config value, sorted by
  `(SEVERITY_RANK[severity], id)`.
- `stride_summary(findings)` — a dict with **all six** letters as keys and the
  counts as values, zeros included.
- `render_report(findings)` — a string beginning
  `SECURITY FINDINGS (n)`, then a rule, then two lines per finding (the
  headline `[SEVERITY] id name title`, then the indented evidence), then a
  rule, then a line beginning `STRIDE  S=..  T=..` in `STRIDE` order.
''',
        "deliverables": [
            "`toolkit.py` — parsing, the eight configuration rules, three log detectors, assembly and rendering; importable with no output",
            "`main.py` — a demo that scans the bundled configuration and log and prints the report",
            "A `Finding` record carrying id, title, STRIDE letter, severity and the evidence that produced it",
            "Deterministic ordering: severity first, then finding id, so two runs of the same input give the same report",
            "Defensive parsing: a malformed log line is dropped, a malformed configuration line raises `ValueError`",
            "A regression check per detector proving it fires on a positive case and stays quiet on a negative one",
        ],
        "constraints": [
            "Standard library only; `dataclasses` and `datetime` are the only imports you need",
            "`toolkit.py` must define names only — importing it must print nothing and read no files",
            "Absent configuration keys are treated as insecure defaults, never as passes",
            "No detector may mutate the event list it is given",
            "Severities are exactly `critical`, `high`, `medium`, `low` — no ad-hoc levels",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "Every automated check passes, including the empty-configuration and boundary cases."},
            {"criterion": "Threat coverage", "weight": 20,
             "evidence": "All six STRIDE categories are reachable, and each detector fires on its positive case only."},
            {"criterion": "Robustness", "weight": 15,
             "evidence": "Malformed log lines are dropped, malformed configuration lines raise, and missing keys default insecure."},
            {"criterion": "Determinism & ordering", "weight": 15,
             "evidence": "Findings sort by severity then id; repeated scans of the same input are byte-identical."},
            {"criterion": "Readability", "weight": 10,
             "evidence": "Rules are data, not a wall of if-statements; docstrings on every public function; no debug output."},
        ],
        "hints": [
            "Keep the eight configuration rules in a list of tuples `(id, key, insecure_default, predicate, title, stride, severity)` and loop over it — one rule per row beats eight if-statements.",
            "`config.get(key, insecure_default)` in that loop is what makes a missing key report rather than pass.",
            "`sorted(findings, key=lambda f: (SEVERITY_RANK[f.severity], f.id))` is the whole ordering requirement.",
            "`stride_summary` should start from `{letter: 0 for letter in \"STRIDE\"}` so the zero categories still appear in the report.",
        ],
        "files": [
            {"name": "toolkit.py", "content": r'''
from dataclasses import dataclass
from datetime import datetime, timezone

STRIDE = {
    "S": "Spoofing",
    "T": "Tampering",
    "R": "Repudiation",
    "I": "Information disclosure",
    "D": "Denial of service",
    "E": "Elevation of privilege",
}

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

REQUIRED_FIELDS = ("user", "action", "result")


@dataclass
class Finding:
    id: str
    title: str
    stride: str
    severity: str
    evidence: str


def parse_config(text):
    """key = value lines -> dict with bool / int / str values."""
    # your code here


def parse_ts(text):
    """ISO-8601 UTC stamp -> integer epoch seconds."""
    # your code here


def parse_event(line):
    """One log line -> event dict, or None when it is malformed."""
    # your code here


def load_events(lines):
    """Every valid event, in file order."""
    # your code here


def audit_config(config):
    """The eight configuration rules, as Findings."""
    # your code here


def detect_brute_force(events, threshold=5, window=300):
    """BRF-<user> for repeated failed logins inside one window."""
    # your code here


def detect_privilege_escalation(events, admins):
    """PRV-<user> for a successful role_change by a non-admin."""
    # your code here


def detect_exfiltration(events, byte_threshold=10000000):
    """EXF-<user> for download volume above the threshold."""
    # your code here


def scan(config, events):
    """Every finding, sorted by severity then id."""
    # your code here


def stride_summary(findings):
    """All six STRIDE letters mapped to their counts."""
    # your code here


def render_report(findings):
    """The whole report as one string."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from datetime import datetime, timedelta, timezone

from toolkit import load_events, parse_config, render_report, scan, stride_summary

BASE = datetime(2026, 5, 4, 8, 0, 0, tzinfo=timezone.utc)


def at(seconds):
    return (BASE + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


CONFIG_TEXT = """
# production.conf
tls_enabled = false
admin_default_password = false
password_min_length = 8
audit_logging = true
max_login_attempts = 5
debug_mode = true
session_timeout_minutes = 240
config_signature_required = true
admins = root,alice
"""

LOG_LINES = []
for _k in range(6):
    LOG_LINES.append(f"{at(_k * 30)} user=mallory ip=203.0.113.7 action=login result=fail bytes=0")
LOG_LINES.append(f"{at(400)} user=bob ip=10.0.0.11 action=role_change result=success bytes=0")
LOG_LINES.append(f"{at(500)} user=alice ip=10.0.0.10 action=role_change result=success bytes=0")
for _k in range(3):
    LOG_LINES.append(f"{at(600 + _k * 60)} user=carol ip=10.0.0.12 action=download result=success bytes=4000000")
LOG_LINES.append(f"{at(900)} user=alice ip=10.0.0.10 action=login result=success bytes=128")
LOG_LINES.append("### corrupt line ###")

CONFIG = parse_config(CONFIG_TEXT)
EVENTS = load_events(LOG_LINES)
FINDINGS = scan(CONFIG, EVENTS)

print(render_report(FINDINGS))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "toolkit.py", "content": r'''
from dataclasses import dataclass
from datetime import datetime, timezone

STRIDE = {
    "S": "Spoofing",
    "T": "Tampering",
    "R": "Repudiation",
    "I": "Information disclosure",
    "D": "Denial of service",
    "E": "Elevation of privilege",
}

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

REQUIRED_FIELDS = ("user", "action", "result")


@dataclass
class Finding:
    id: str
    title: str
    stride: str
    severity: str
    evidence: str


CONFIG_RULES = [
    ("TLS-001", "tls_enabled", False, lambda v: v is not True,
     "Transport encryption disabled", "I", "critical"),
    ("PWD-001", "admin_default_password", True, lambda v: v is True,
     "Default administrator password still accepted", "S", "critical"),
    ("PWD-002", "password_min_length", 0, lambda v: v < 12,
     "Password minimum length below 12", "S", "high"),
    ("LOG-001", "audit_logging", False, lambda v: v is not True,
     "Audit logging disabled", "R", "high"),
    ("RTL-001", "max_login_attempts", 0, lambda v: v <= 0,
     "No login rate limit configured", "D", "high"),
    ("DBG-001", "debug_mode", True, lambda v: v is True,
     "Debug mode enabled in production", "I", "medium"),
    ("SES-001", "session_timeout_minutes", 1440, lambda v: v > 60,
     "Session timeout longer than 60 minutes", "E", "medium"),
    ("INT-001", "config_signature_required", False, lambda v: v is not True,
     "Configuration integrity checks disabled", "T", "medium"),
]


def parse_config(text):
    """key = value lines -> dict with bool / int / str values."""
    config = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"bad configuration line: {raw!r}")
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"bad configuration line: {raw!r}")
        if value.lower() == "true":
            config[key] = True
        elif value.lower() == "false":
            config[key] = False
        elif value.lstrip("-").isdigit():
            config[key] = int(value)
        else:
            config[key] = value
    return config


def parse_ts(text):
    """ISO-8601 UTC stamp -> integer epoch seconds."""
    moment = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return int(moment.timestamp())


def parse_event(line):
    """One log line -> event dict, or None when it is malformed."""
    parts = line.split()
    if not parts:
        return None
    try:
        event = {"ts": parse_ts(parts[0])}
    except ValueError:
        return None
    for token in parts[1:]:
        key, sep, value = token.partition("=")
        if not sep or not key or not value:
            return None
        event[key] = value
    for field in REQUIRED_FIELDS:
        if field not in event:
            return None
    return event


def load_events(lines):
    """Every valid event, in file order."""
    events = []
    for line in lines:
        event = parse_event(line)
        if event is not None:
            events.append(event)
    return events


def audit_config(config):
    """The eight configuration rules, as Findings."""
    findings = []
    for ident, key, insecure_default, is_bad, title, stride, severity in CONFIG_RULES:
        value = config.get(key, insecure_default)
        try:
            bad = is_bad(value)
        except TypeError:
            bad = True
        if bad:
            findings.append(Finding(ident, title, stride, severity,
                                    f"{key} = {value!r}"))
    return findings


def detect_brute_force(events, threshold=5, window=300):
    """BRF-<user> for repeated failed logins inside one window."""
    by_user = {}
    for event in events:
        if event.get("action") == "login" and event.get("result") == "fail":
            by_user.setdefault(event["user"], []).append(event["ts"])
    findings = []
    for user in sorted(by_user):
        stamps = sorted(by_user[user])
        for i in range(len(stamps) - threshold + 1):
            if stamps[i + threshold - 1] - stamps[i] <= window:
                findings.append(Finding(
                    f"BRF-{user}", f"Credential guessing against {user}", "S", "high",
                    f"{len(stamps)} failed logins, {threshold} inside {window}s"))
                break
    return findings


def detect_privilege_escalation(events, admins):
    """PRV-<user> for a successful role_change by a non-admin."""
    admins = set(admins)
    seen = []
    for event in events:
        if event.get("action") != "role_change" or event.get("result") != "success":
            continue
        user = event["user"]
        if user in admins or user in seen:
            continue
        seen.append(user)
    return [Finding(f"PRV-{user}", f"Role change performed by non-admin {user}",
                    "E", "critical", f"action=role_change by {user}")
            for user in sorted(seen)]


def detect_exfiltration(events, byte_threshold=10000000):
    """EXF-<user> for download volume above the threshold."""
    totals = {}
    for event in events:
        if event.get("action") != "download":
            continue
        try:
            size = int(event.get("bytes", 0))
        except ValueError:
            size = 0
        totals[event["user"]] = totals.get(event["user"], 0) + size
    return [Finding(f"EXF-{user}", f"Large download volume for {user}", "I", "high",
                    f"{totals[user]} bytes downloaded")
            for user in sorted(totals) if totals[user] > byte_threshold]


def scan(config, events):
    """Every finding, sorted by severity then id."""
    raw_admins = config.get("admins", "")
    admins = {name.strip() for name in str(raw_admins).split(",") if name.strip()}
    findings = (audit_config(config)
                + detect_brute_force(events)
                + detect_privilege_escalation(events, admins)
                + detect_exfiltration(events))
    return sorted(findings, key=lambda f: (SEVERITY_RANK[f.severity], f.id))


def stride_summary(findings):
    """All six STRIDE letters mapped to their counts."""
    counts = {letter: 0 for letter in "STRIDE"}
    for finding in findings:
        counts[finding.stride] += 1
    return counts


def render_report(findings):
    """The whole report as one string."""
    rule = "-" * 72
    lines = [f"SECURITY FINDINGS ({len(findings)})", rule]
    for finding in findings:
        lines.append(f"[{finding.severity.upper():<8}] {finding.id:<16} "
                     f"{STRIDE[finding.stride]:<24} {finding.title}")
        lines.append(f"{'':<11}{finding.evidence}")
    lines.append(rule)
    counts = stride_summary(findings)
    lines.append("STRIDE  " + "  ".join(f"{k}={counts[k]}" for k in "STRIDE"))
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from datetime import datetime, timedelta, timezone

from toolkit import load_events, parse_config, render_report, scan, stride_summary

BASE = datetime(2026, 5, 4, 8, 0, 0, tzinfo=timezone.utc)


def at(seconds):
    return (BASE + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


CONFIG_TEXT = """
# production.conf
tls_enabled = false
admin_default_password = false
password_min_length = 8
audit_logging = true
max_login_attempts = 5
debug_mode = true
session_timeout_minutes = 240
config_signature_required = true
admins = root,alice
"""

LOG_LINES = []
for _k in range(6):
    LOG_LINES.append(f"{at(_k * 30)} user=mallory ip=203.0.113.7 action=login result=fail bytes=0")
LOG_LINES.append(f"{at(400)} user=bob ip=10.0.0.11 action=role_change result=success bytes=0")
LOG_LINES.append(f"{at(500)} user=alice ip=10.0.0.10 action=role_change result=success bytes=0")
for _k in range(3):
    LOG_LINES.append(f"{at(600 + _k * 60)} user=carol ip=10.0.0.12 action=download result=success bytes=4000000")
LOG_LINES.append(f"{at(900)} user=alice ip=10.0.0.10 action=login result=success bytes=128")
LOG_LINES.append("### corrupt line ###")

CONFIG = parse_config(CONFIG_TEXT)
EVENTS = load_events(LOG_LINES)
FINDINGS = scan(CONFIG, EVENTS)

print(render_report(FINDINGS))
print()
print("by category:", stride_summary(FINDINGS))
'''},
        ],
        "tests": [
            {"name": "parse_config types, comments and bad lines", "code": r'''
from toolkit import parse_config
_c = parse_config("# note\n\ntls_enabled = TRUE\ndebug_mode = false\nport = 8443\nlow = -3\nname = prod-01\n")
assert _c["tls_enabled"] is True, f"tls_enabled parsed as {_c['tls_enabled']!r}"
assert _c["debug_mode"] is False, f"debug_mode parsed as {_c['debug_mode']!r}"
assert _c["port"] == 8443 and isinstance(_c["port"], int), f"port parsed as {_c['port']!r}"
assert _c["low"] == -3, f"low parsed as {_c['low']!r}"
assert _c["name"] == "prod-01", f"name parsed as {_c['name']!r}"
assert "# note" not in _c and len(_c) == 5, f"Comments and blanks should vanish: {_c!r}"
try:
    parse_config("this line has no equals sign")
    assert False, "A line with no = should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "An empty configuration is eight findings", "code": r'''
from toolkit import audit_config
_f = audit_config({})
assert len(_f) == 8, f"Every missing key defaults insecure — expected 8 findings, got {len(_f)}"
assert sorted(x.id for x in _f) == ["DBG-001", "INT-001", "LOG-001", "PWD-001",
                                    "PWD-002", "RTL-001", "SES-001", "TLS-001"], \
    f"Got ids {sorted(x.id for x in _f)!r}"
assert all(x.stride in "STRIDE" for x in _f), "Every finding needs a STRIDE letter"
assert all(x.severity in ("critical", "high", "medium", "low") for x in _f), \
    "Severities are limited to the four named levels"
'''},
            {"name": "A hardened configuration is silent", "code": r'''
from toolkit import audit_config
_good = {"tls_enabled": True, "admin_default_password": False, "password_min_length": 12,
         "audit_logging": True, "max_login_attempts": 5, "debug_mode": False,
         "session_timeout_minutes": 60, "config_signature_required": True}
assert audit_config(_good) == [], f"A hardened config should be clean, got {audit_config(_good)!r}"
_edge = dict(_good, password_min_length=11)
assert [x.id for x in audit_config(_edge)] == ["PWD-002"], "11 is below the minimum, 12 is not"
_edge = dict(_good, session_timeout_minutes=61)
assert [x.id for x in audit_config(_edge)] == ["SES-001"], "60 passes, 61 does not"
_edge = dict(_good, max_login_attempts=0)
assert [x.id for x in audit_config(_edge)] == ["RTL-001"], "Zero attempts means no rate limit"
'''},
            {"name": "Findings carry their evidence", "code": r'''
from toolkit import audit_config
_f = audit_config({"tls_enabled": False, "admin_default_password": True,
                   "password_min_length": 12, "audit_logging": True,
                   "max_login_attempts": 3, "debug_mode": False,
                   "session_timeout_minutes": 30, "config_signature_required": True})
_by_id = {x.id: x for x in _f}
assert set(_by_id) == {"TLS-001", "PWD-001"}, f"Got {sorted(_by_id)!r}"
assert _by_id["TLS-001"].evidence == "tls_enabled = False", \
    f"Evidence was {_by_id['TLS-001'].evidence!r}"
assert _by_id["TLS-001"].stride == "I" and _by_id["TLS-001"].severity == "critical"
assert _by_id["PWD-001"].stride == "S" and _by_id["PWD-001"].severity == "critical"
'''},
            {"name": "Brute-force detector fires and stays quiet", "code": r'''
from toolkit import detect_brute_force, load_events
_hot = load_events([f"2026-05-04T08:0{_k}:00Z user=mallory ip=1.1.1.1 action=login result=fail"
                    for _k in range(5)])
assert len(_hot) == 5, f"Five lines should parse, got {len(_hot)}"
_f = detect_brute_force(_hot, threshold=5, window=300)
assert [x.id for x in _f] == ["BRF-mallory"], f"Got {[x.id for x in _f]!r}"
assert _f[0].stride == "S" and _f[0].severity == "high", f"Got {_f[0]!r}"
assert detect_brute_force(_hot, threshold=6) == [], "Six failures were never recorded"
assert detect_brute_force(_hot, window=60) == [], "Five failures span 240 s, not 60"
assert detect_brute_force([]) == [], "An empty log flags nobody"
'''},
            {"name": "Privilege escalation ignores real admins", "code": r'''
from toolkit import detect_privilege_escalation, load_events
_ev = load_events([
    "2026-05-04T08:00:00Z user=bob ip=1.1.1.1 action=role_change result=success",
    "2026-05-04T08:01:00Z user=alice ip=1.1.1.2 action=role_change result=success",
    "2026-05-04T08:02:00Z user=dan ip=1.1.1.3 action=role_change result=fail",
    "2026-05-04T08:03:00Z user=bob ip=1.1.1.1 action=role_change result=success",
])
_f = detect_privilege_escalation(_ev, {"alice"})
assert [x.id for x in _f] == ["PRV-bob"], f"Got {[x.id for x in _f]!r} — one finding per user, admins exempt"
assert _f[0].stride == "E" and _f[0].severity == "critical", f"Got {_f[0]!r}"
assert detect_privilege_escalation(_ev, {"alice", "bob"}) == [], "Both actors are admins here"
'''},
            {"name": "Exfiltration threshold is strict", "code": r'''
from toolkit import detect_exfiltration, load_events
_ev = load_events([
    "2026-05-04T08:00:00Z user=carol ip=1.1.1.1 action=download result=success bytes=6000000",
    "2026-05-04T08:01:00Z user=carol ip=1.1.1.1 action=download result=success bytes=4000000",
    "2026-05-04T08:02:00Z user=dan ip=1.1.1.2 action=login result=success bytes=99999999",
])
assert detect_exfiltration(_ev, byte_threshold=10000000) == [], \
    "Exactly at the threshold is not above it"
_f = detect_exfiltration(_ev, byte_threshold=9999999)
assert [x.id for x in _f] == ["EXF-carol"], f"Got {[x.id for x in _f]!r}"
assert _f[0].stride == "I" and _f[0].severity == "high", f"Got {_f[0]!r}"
assert "10000000" in _f[0].evidence, f"Evidence should carry the volume: {_f[0].evidence!r}"
'''},
            {"name": "scan orders by severity then id", "code": r'''
from toolkit import SEVERITY_RANK
assert isinstance(FINDINGS, list) and FINDINGS, "main.py should leave FINDINGS populated"
_ids = [f.id for f in FINDINGS]
assert _ids == ["PRV-bob", "TLS-001", "BRF-mallory", "EXF-carol", "PWD-002",
                "DBG-001", "SES-001"], f"Got {_ids!r}"
_keys = [(SEVERITY_RANK[f.severity], f.id) for f in FINDINGS]
assert _keys == sorted(_keys), f"Findings are not sorted: {_keys!r}"
assert scan(CONFIG, EVENTS) == FINDINGS, "Two scans of the same input must agree"
'''},
            {"name": "The demo log parses and the admin is exempt", "code": r'''
assert len(EVENTS) == 12, f"Twelve good lines and one corrupt one — expected 12 events, got {len(EVENTS)}"
assert not any(f.id == "PRV-alice" for f in FINDINGS), "alice is listed in admins"
assert any(f.id == "PRV-bob" for f in FINDINGS), "bob is not an admin and changed a role"
assert not any(f.id in ("PWD-001", "LOG-001", "RTL-001", "INT-001") for f in FINDINGS), \
    "Those four settings are hardened in the demo configuration"
'''},
            {"name": "stride_summary covers all six categories", "code": r'''
from toolkit import stride_summary
_counts = stride_summary(FINDINGS)
assert set(_counts) == set("STRIDE"), f"All six letters must be keys, got {sorted(_counts)!r}"
assert _counts == {"S": 2, "T": 0, "R": 0, "I": 3, "D": 0, "E": 2}, f"Got {_counts!r}"
assert sum(_counts.values()) == len(FINDINGS), "The counts must account for every finding"
assert stride_summary([]) == {"S": 0, "T": 0, "R": 0, "I": 0, "D": 0, "E": 0}, \
    "An empty report still names all six categories"
'''},
            {"name": "render_report is readable and complete", "code": r'''
from toolkit import render_report
_rep = render_report(FINDINGS)
assert isinstance(_rep, str), "render_report returns a string, it does not print"
_lines = _rep.split("\n")
assert _lines[0] == "SECURITY FINDINGS (7)", f"First line was {_lines[0]!r}"
assert _lines[2].startswith("[CRITICAL]"), f"The first finding line was {_lines[2]!r}"
assert "PRV-bob" in _lines[2] and "Elevation of privilege" in _lines[2], f"Got {_lines[2]!r}"
assert _lines[-1].startswith("STRIDE  S=2  T=0  R=0  I=3  D=0  E=2"), f"Last line was {_lines[-1]!r}"
assert render_report([]).startswith("SECURITY FINDINGS (0)"), "An empty report still renders"
assert "SECURITY FINDINGS (7)" in _out, "main.py should print the report"
'''},
            {"name": "toolkit.py is import-clean", "code": r'''
_src = open("toolkit.py").read()
assert "print(" not in _src, "toolkit.py defines the logic; printing belongs in main.py"
assert "open(" not in _src, "toolkit.py should not read files at import time"
'''},
        ],
    },
}
