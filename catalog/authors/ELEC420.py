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
